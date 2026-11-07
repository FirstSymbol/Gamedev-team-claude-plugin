# .NET backend and web test automation (QA view)
Baseline rules (xUnit v3 on Microsoft.Testing.Platform, no EF InMemory, CPM): studio:stack-dotnet
`testing-dotnet.md`. This file: API scenario suites, contracts, admin web E2E, load.

## Suite layout
```
tests/
  Game.Api.Tests.Integration/   WebApplicationFactory + Testcontainers (Postgres, Redis)
  Game.Api.Tests.Contract/      Pact provider verification / OpenAPI schema checks
  Game.Client.Contract/         Pact consumer tests for the Unity client's shared DTO lib (netstandard2.1)
  admin-web/e2e/                Playwright (TS runner, or Microsoft.Playwright.Xunit.v3 for .NET)
  load/                         k6 scripts (JS) or NBomber (C#)
```

## xUnit v3 integration tests with WebApplicationFactory + Testcontainers
```csharp
public sealed class ApiFactory : WebApplicationFactory<Program>, IAsyncLifetime {
    readonly PostgreSqlContainer _pg = new PostgreSqlBuilder("postgres:17-alpine").Build();
    readonly RedisContainer _redis = new RedisBuilder("redis:7-alpine").Build();
    public FakeTimeProvider Time { get; } = new(new DateTimeOffset(2026, 3, 1, 23, 59, 0, TimeSpan.Zero));

    protected override void ConfigureWebHost(IWebHostBuilder b) {
        b.UseSetting("ConnectionStrings:Db", _pg.GetConnectionString());
        b.UseSetting("ConnectionStrings:Redis", _redis.GetConnectionString());
        b.ConfigureTestServices(s => s.AddSingleton<TimeProvider>(Time));   // control "server UTC day"
    }
    public async ValueTask InitializeAsync() {
        await Task.WhenAll(_pg.StartAsync(), _redis.StartAsync());
        using var scope = Services.CreateScope();
        await scope.ServiceProvider.GetRequiredService<GameDb>().Database.MigrateAsync();
    }
    public override async ValueTask DisposeAsync() { await _pg.DisposeAsync(); await _redis.DisposeAsync(); await base.DisposeAsync(); }
}

public sealed class DailyBonusApiTests(ApiFactory f) : IClassFixture<ApiFactory> {
    [Fact]
    public async Task Claim_twice_same_day_is_rejected_and_balance_credited_once() {
        var ct = TestContext.Current.CancellationToken;
        var client = f.CreateClient();
        var player = await TestData.NewPlayerAsync(client, ct);              // unique per test
        var first = await client.PostAsync($"/v1/players/{player.Id}/daily-bonus/claim", null, ct);
        var second = await client.PostAsync($"/v1/players/{player.Id}/daily-bonus/claim", null, ct);
        Assert.Equal(HttpStatusCode.OK, first.StatusCode);
        Assert.Equal(HttpStatusCode.Conflict, second.StatusCode);
        Assert.Equal(100, (await TestData.BalanceAsync(client, player.Id, ct)));
    }
}
```
- Testcontainers 4.10+: image (with tag) goes in the builder constructor; parameterless builder ctors are `[Obsolete]`.
- Packages: `Testcontainers.PostgreSql`, `Testcontainers.Redis`, `Microsoft.AspNetCore.Mvc.Testing`,
  `Microsoft.Extensions.TimeProvider.Testing` (`FakeTimeProvider`). Docker required on CI agents.
- One container per test class/collection (or assembly fixture `[assembly: AssemblyFixture(typeof(...))]`,
  xUnit v3); isolate by unique player IDs, not by recreating DBs. Respawn library to reset tables if needed.
- Advance time with `f.Time.Advance(TimeSpan.FromMinutes(1))` to cross UTC midnight deterministically.
- Auth: replace JWT handler in `ConfigureTestServices` with a test scheme issuing known claims; also keep
  one suite against the real auth config (token expiry, wrong audience).

## Must-have API scenarios for money/rewards
| Scenario | Assert |
|---|---|
| Idempotency: same `Idempotency-Key` replayed | same response body, ledger has 1 entry |
| Concurrency: 20 parallel spend requests, balance for 3 | exactly 3 succeed; balance >= 0; no deadlock 500s |
| Validation: EP/BVA values (0, -1, max+1, overflow) | 400 ProblemDetails, no ledger rows |
| Authorization: player A acts on player B | 403/404, no data leak in body |
| Receipt validation: forged/replayed store receipt | rejected, logged, no grant |
| Time: claim at 23:59:59 and 00:00:00 UTC, DST irrelevant server-side | correct streak |
| Failure: DB down mid-request (stop container) | 5xx with no partial write; retry succeeds |
```csharp
var tasks = Enumerable.Range(0, 20).Select(_ => client.PostAsJsonAsync(url, new { amount = 1 }, ct));
var codes = (await Task.WhenAll(tasks)).Select(r => r.StatusCode).ToList();
Assert.Equal(3, codes.Count(c => c == HttpStatusCode.OK));
```

## Contract tests (Unity client ↔ backend)
| Approach | Use when | Tooling |
|---|---|---|
| Consumer-driven contracts (Pact) | separate client/backend teams, many API consumers (Unity, admin web, partners) | PactNet (consumer tests + provider verification), Pact Broker / PactFlow, `can-i-deploy` |
| Schema checks (OpenAPI) | provider-led API, single consumer | ASP.NET Core OpenAPI doc snapshot + `oasdiff breaking` in CI; JSON Schema validation of responses |
| Snapshot of DTO serialization | shared netstandard2.1 DTO lib | Verify (`Verify.XunitV3`) snapshots of JSON for each DTO version |
- Unity client cannot run PactNet inside the player; write consumer tests in a .NET test project referencing
  the shared DTO library and the client's API wrapper (plain C#).
- Version compatibility: provider must verify contracts of every supported client version (min supported
  client, see release-platform-manager force-update policy).
- Breaking change = removed field, type change, new required field, enum value the old client can't parse.

## Playwright for admin panels / back office
- Prefer the TS test runner (`@playwright/test`) when the admin app is JS/TS; for .NET teams use
  `Microsoft.Playwright.Xunit.v3` (`PageTest` base class: fresh page per test).
```ts
test('support agent grants compensation coins', async ({ page }) => {
  await page.goto('/players/p-123');
  await page.getByRole('button', { name: 'Grant coins' }).click();
  await page.getByLabel('Amount').fill('500');
  await page.getByLabel('Reason').selectOption('compensation');
  await page.getByRole('button', { name: 'Confirm' }).click();
  await expect(page.getByTestId('balance')).toHaveText('5,500');
  await expect(page.getByRole('row', { name: /compensation/ })).toBeVisible();  // audit log entry
});
```
- Locators by role/label/test-id; web-first assertions (auto-wait), no `waitForTimeout`.
- Auth once via `storageState` setup project; test roles (support, finance, admin) - check RBAC denials too.
- Trace on first retry (`trace: 'on-first-retry'`) for debugging flakes; run sharded in CI.
- Back-office risks: privilege escalation, mass actions without confirmation, missing audit log, PII export.
- Accessibility smoke: `@axe-core/playwright` on key pages (WCAG 2.2 AA).

## Load testing
| Tool | Language | Pick when |
|---|---|---|
| k6 (Grafana) | JS scripts, Go engine | HTTP/WebSocket/gRPC APIs, CI thresholds, cloud or local |
| NBomber | C# / F# | reuse .NET client code, SignalR, custom protocols; free for personal/academic use, organizations need a paid (per-org) license |
| Custom headless Unity bots | C# | netcode/game-server realism (domain-multiplayer) |
k6 with thresholds as pass/fail gate:
```js
import http from 'k6/http'; import { check } from 'k6';
export const options = {
  scenarios: { claim: { executor: 'ramping-arrival-rate', startRate: 50, timeUnit: '1s',
    preAllocatedVUs: 200, stages: [{ target: 500, duration: '5m' }, { target: 500, duration: '20m' }] } },
  thresholds: { http_req_failed: ['rate<0.001'], 'http_req_duration{name:claim}': ['p(95)<250', 'p(99)<600'] },
};
export default function () {
  const r = http.post(`${__ENV.BASE}/v1/players/${__VU}-${__ITER}/daily-bonus/claim`, null,
    { tags: { name: 'claim' } });
  check(r, { 'ok or conflict': (x) => x.status === 200 || x.status === 409 });
}
```
NBomber equivalent: `Scenario.Create("claim", async ctx => { ...; return Response.Ok(); })
.WithLoadSimulations(Simulation.Inject(rate: 500, interval: TimeSpan.FromSeconds(1), during: TimeSpan.FromMinutes(20)))`
then `NBomberRunner.RegisterScenarios(s).Run()`.
- Use arrival-rate (open model) for public APIs; closed model (VUs) only for fixed-client systems.
- Load profile from analytics: peak req/s per endpoint at event start/push send, x2 for headroom.
- Seed realistic data volume (millions of ledger rows) before the run; empty DBs lie.
- Watch server metrics during the run (CPU, GC pauses, DB connections, Redis latency) via OpenTelemetry.

## Sources
- xUnit.net v3 getting started https://xunit.net/docs/getting-started/v3/getting-started
- ASP.NET Core integration tests (WebApplicationFactory) https://learn.microsoft.com/aspnet/core/test/integration-tests
- Testcontainers for .NET https://dotnet.testcontainers.org/
- Pact docs https://docs.pact.io/
- Playwright .NET test runners https://playwright.dev/dotnet/docs/test-runners
- Grafana k6 thresholds https://grafana.com/docs/k6/latest/using-k6/thresholds/
- NBomber overview https://nbomber.com/docs/getting-started/overview/
- NBomber license https://nbomber.com/docs/getting-started/license/
- Testcontainers .NET: parameterless builder ctors obsolete (4.10) https://github.com/testcontainers/testcontainers-dotnet/discussions/1470
- oasdiff (OpenAPI breaking change detection) https://github.com/oasdiff/oasdiff
