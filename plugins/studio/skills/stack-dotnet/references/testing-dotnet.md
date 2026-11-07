# Testing .NET services

## Test mix for a game backend
| Layer | Share | Tooling | Targets |
|---|---|---|---|
| Unit (domain rules: wallet math, reward schedules, RNG mapping) | ~60% | xUnit v3 + fakes | ms each, no I/O |
| Integration (endpoint → DB) | ~30% | WebApplicationFactory + Testcontainers | real PostgreSQL/Redis, per-feature happy + failure paths |
| Contract (Unity/admin clients) | few | Verify snapshots of OpenAPI/DTO JSON; Pact optional | breaking-change detection |
| E2E / load | few | k6, NBomber; Playwright for admin UI | pre-release |
- Every bug fix ships a test that fails before the fix. Money/economy logic: aim ≥ 90% branch coverage + mutation testing.

## Frameworks
| Framework | State (2026) | Notes |
|---|---|---|
| xUnit v3 (`xunit.v3`) | default | test project is an executable; runs on Microsoft.Testing.Platform (MTP) or VSTest |
| NUnit 4 | fine if already used | `Assert.That` constraint model; parallelism opt-in |
| MSTest 4 (4.5.x, Oct 2026) | fine; MTP-native | Microsoft-maintained |
| TUnit | newer, source-generated, MTP-only | consider for greenfield only after team agreement |
- Don't mix frameworks in one solution without reason.
- .NET 10 SDK: `dotnet test` runs MTP natively; select runner in `global.json`
  (`"test": { "runner": "Microsoft.Testing.Platform" }`); .NET 11 SDK also reads `DOTNET_TEST_RUNNER`. MTP v2 dropped VSTest-mode support under the .NET 10 SDK.
- Under MTP: VSTest `--filter` syntax and `--logger` don't apply; use xUnit filters (`--filter-class`, `--filter-trait`) and `--report-trx` (Microsoft.Testing.Extensions.TrxReport).

### xUnit v3 essentials
- `TestContext.Current.CancellationToken` → pass to every async call (cancels on timeout/abort).
- Fixtures: class (`IClassFixture<T>`), collection (`[Collection]`), assembly (`[assembly: AssemblyFixture(typeof(PgFixture))]`) — use assembly fixture for one Postgres container per run.
- `IAsyncLifetime` for async setup/teardown: v3 is `ValueTask InitializeAsync()` + `IAsyncDisposable.DisposeAsync()` (v2 used `Task`).
- Dynamic skip `Assert.Skip(...)`, `Assert.SkipWhen(cond, reason)`; `[Fact(Explicit = true)]` for slow/manual tests.
- `MatrixTheoryData<T1,T2>` for combinatorial cases; `TheoryDataRow` for per-row skip/traits.
- Migration v2→v3: package rename (`xunit` → `xunit.v3`), `<OutputType>Exe</OutputType>`, removed
  `Xunit.Abstractions` (`ITestOutputHelper` moves to `Xunit` namespace).

## Integration tests: WebApplicationFactory + Testcontainers
```csharp
public sealed class ApiFactory : WebApplicationFactory<Program>, IAsyncLifetime {
    private readonly PostgreSqlContainer _pg = new PostgreSqlBuilder("postgres:17-alpine").Build();
    protected override void ConfigureWebHost(IWebHostBuilder b) {
        b.UseEnvironment("Testing");
        b.UseSetting("ConnectionStrings:game", _pg.GetConnectionString());
        b.ConfigureTestServices(s => {
            s.AddAuthentication("Test").AddScheme<AuthenticationSchemeOptions, TestAuthHandler>("Test", _ => { });
            s.AddSingleton<TimeProvider>(new FakeTimeProvider(DateTimeOffset.Parse("2026-01-01T00:00:00Z")));
            s.Replace(ServiceDescriptor.Singleton<IPaymentGateway, FakePaymentGateway>());
        });
    }
    public async ValueTask InitializeAsync() { await _pg.StartAsync(); /* apply migrations */ }
    public override async ValueTask DisposeAsync() { await _pg.DisposeAsync(); await base.DisposeAsync(); }
}
```
- Top-level `Program` must be visible: .NET 10 source-generates `public partial class Program`; an analyzer
  flags the explicit declaration as removable (needed only on .NET 9 and earlier).
- Apply real migrations in the fixture (catches migration bugs); reset data between tests with
  Respawn (`Respawner.CreateAsync(conn, new() { DbAdapter = DbAdapter.Postgres })`) or per-test transactions.
- Same engine as prod: Testcontainers modules `Testcontainers.PostgreSql`, `.Redis`, `.RabbitMq`, `.Kafka`.
  EF InMemory/SQLite hide SQL translation, constraints, concurrency and transaction behavior.
- Test auth: a `TestAuthHandler` that builds claims from a header (`X-Test-User`) — test authorization
  rules (403 for other player's wallet) explicitly.
- Concurrency tests for economy endpoints: fire N parallel requests with the same/different
  `Idempotency-Key` via `Task.WhenAll` and assert balance invariants.
- CI needs Docker; on hosted runners pin image tags; reuse containers per assembly to keep suite < 5 min.

## Snapshot testing: Verify
- `Verify.XunitV3` (`await Verify(result)`), `Verify.Http` for `HttpResponseMessage`, `Verify.EntityFramework` for SQL.
- Commit `*.verified.*`; gitignore `*.received.*`. Scrub volatile values (`ScrubMember`, auto GUID/date scrubbing).
- Best uses: API response shapes (contract with Unity/admin), generated OpenAPI doc, complex DTO mapping, emails.
- Review snapshot diffs like code; blind accepting defeats the purpose.

## Test doubles
| Tool | Stance |
|---|---|
| Hand-written fakes | first choice for ports (`IPaymentGateway`, `IClock`); reusable, readable |
| NSubstitute (BSD) | default mocking library: `Substitute.For<IStore>()`, `Received(1)` |
| Moq | 4.20.0 (Aug 2023) shipped SponsorLink telemetry, removed in 4.20.2 — trust concern; keep pinned ≥ 4.20.2 or migrate to NSubstitute |
| FakeItEasy (MIT) | fine alternative |
- Built-ins: `FakeTimeProvider` (Microsoft.Extensions.TimeProvider.Testing), `FakeLogger<T>` /
  `FakeLogCollector` (Microsoft.Extensions.Diagnostics.Testing), `TestServer` handlers for outbound HTTP.
- Don't mock what you don't own (DbContext, HttpClient): use real DB in containers, `HttpMessageHandler` stubs or WireMock.Net.
- Assertions: FluentAssertions v8+ is commercial (Xceed); options: stay on v7.x (Apache-2.0), AwesomeAssertions (community fork), Shouldly, or plain `Assert`.

## Coverage
- VSTest mode: `coverlet.collector` → `dotnet test --collect:"XPlat Code Coverage"`.
- MTP mode: `Microsoft.Testing.Extensions.CodeCoverage` → `--coverage --coverage-output-format cobertura`.
- Merge/report: ReportGenerator (`reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage`).
- Gate on changed-lines coverage in PR (e.g. ≥ 80%), not a global vanity number; exclude generated code/migrations.

## Mutation testing: Stryker.NET
- `dotnet tool install -g dotnet-stryker`; run `dotnet stryker` in the test project; scope with
  `--mutate "src/Economy/**/*.cs"` and `--since:main` for PR-only runs.
- Thresholds in `stryker-config.json` (`high: 80, low: 60, break: 50` as a start); target domain/economy code, not controllers/DTOs.
- Surviving mutants = missing assertions; fix tests, don't chase 100%.

## Other useful tests
- Architecture rules: NetArchTest.Rules / ArchUnitNET (e.g. Domain must not reference EF Core).
- Benchmarks: BenchmarkDotNet (`[MemoryDiagnoser]`) for hot paths; never Stopwatch micro-benchmarks.
- Load: k6 (JS scripts, thresholds) or NBomber (C#); define p95 latency + error-rate SLO per endpoint.
- Determinism: inject `TimeProvider`, seedable RNG abstractions (except certified RNG — test distribution statistically).

## Sources
- xUnit.net v3 what's new https://xunit.net/docs/getting-started/v3/whats-new
- xUnit.net v3 and Microsoft Testing Platform https://xunit.net/docs/getting-started/v3/microsoft-testing-platform
- Migrating from VSTest to Microsoft.Testing.Platform https://learn.microsoft.com/en-us/dotnet/core/testing/migrating-vstest-microsoft-testing-platform
- Integration tests in ASP.NET Core https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests
- Testcontainers for .NET https://dotnet.testcontainers.org/
- Testcontainers 4.10: image required in builder ctor https://github.com/testcontainers/testcontainers-dotnet/discussions/1470
- Testing with dotnet test (VSTest vs MTP mode, global.json) https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-with-dotnet-test
- ASP.NET Core 10 release notes (Program source generator) https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0
- MSTest releases https://github.com/microsoft/testfx/releases
- Verify https://github.com/VerifyTests/Verify
- Stryker.NET https://stryker-mutator.io/docs/stryker-net/introduction/
