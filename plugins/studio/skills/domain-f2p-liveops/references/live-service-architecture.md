# Live-service architecture for F2P games

## Building blocks
| Block | Purpose | Rule |
|---|---|---|
| Remote config | tunable values (prices, rewards, timers, toggles) | client defaults compiled in; fetch at boot + on resume; last-known-good cache |
| Feature flags | ship dark, ramp %, kill switch | flag per risky feature; owner + expiry date; remove after full rollout |
| Server-driven content | event definitions, offers, store layout, quests as data | schema-versioned JSON; validated at publish, not at runtime |
| Remote assets | event art/UI without app update | Addressables remote catalog + CDN (UGS Cloud Content Delivery or own CDN) |
| Segmentation/targeting | who sees which config/offer | evaluated server-side; deterministic; logged on exposure |
| Economy service | wallets, inventory, purchases, grants | server-authoritative, idempotent, append-only ledger |
| Event engine | schedules, progress, leaderboards, rewards | server UTC windows; reward claims idempotent |
| Telemetry | exposure + outcome events | every config/flag/segment version stamped on events |

## Compatibility and safety rules
- Clients in the wild run N-2..N versions: never remove or retype a config key a live client
  reads; add new keys, deprecate after the min supported version passes.
- `min_supported_version` + `recommended_version` in config drive a forced/soft update gate.
- Target config by app version (Game Overrides JEXL `app.version` / PlayFab segments) when
  shape changes; content must declare the min client version it needs.
- Config changes apply on next fetch: design UI for mid-session changes (event ends while a
  screen is open → server rejects claim with a clear "event ended" state, never silent loss).
- Apple App Review 2.5.2: no downloading executable code that changes features; data and
  assets are fine. Lua/JS gameplay scripts downloaded at runtime = review risk (verify with
  release-platform-manager before relying on it).
- Validate every config publish against a JSON Schema + business rules (no negative price,
  reward cap, start < end, segment exists) in CI or the admin tool; reject, don't warn.

## Unity Gaming Services (UGS) - status 2026-11
| Service | Use | Notes |
|---|---|---|
| Remote Config | key/value + JSON settings per environment | `RemoteConfigService.Instance.FetchConfigsAsync(user, app)`; typed getters with defaults |
| Game Overrides | targeted/scheduled overrides of Remote Config/Economy | JEXL (stateless) or Audiences (stateful); % rollout by user id; multi-variant with weights; priority resolves key conflicts; start/end dates |
| Cloud Code | server logic (JS scripts or C# modules) | put grants, validation, event claims here, not in client |
| Economy | currencies, inventory, virtual + real-money purchases | config is cached per `configAssignmentHash`; Economy SDK >= 2.0 passes it automatically |
| Cloud Save, Leaderboards, Authentication, Analytics, CCD | player data, rankings, identity, telemetry, remote content | Game Overrides can target CCD badges |
- Multiplay Game Server Hosting ended 2026-03-31 (software licensed to Rocket Science
  Group) - dedicated servers: see `studio:domain-multiplayer`.
- Organizations based in Mainland China/Hong Kong/Macau lost most global UGS services on
  2026-06-30 (Remote Config, Analytics, Relay, Lobby, Vivox...) → Unity UOS equivalents.
- Pricing: per-service free tier then usage-based (verify current UGS pricing page).
- Lock-in: UGS IDs, Economy config and Cloud Code are proprietary; keep domain rules in a
  portable `netstandard2.1` library if migration is plausible.

```csharp
// Client: typed config facade with compiled defaults (UGS Remote Config; verify API per package version)
public sealed class LiveConfig {
    struct UserAttrs { public int level; public string segment; }
    struct AppAttrs { }
    RuntimeConfig cfg;
    public async Task InitAsync() {
        await UnityServices.InitializeAsync();
        if (!AuthenticationService.Instance.IsSignedIn)
            await AuthenticationService.Instance.SignInAnonymouslyAsync();
        try { cfg = await RemoteConfigService.Instance.FetchConfigsAsync(new UserAttrs(), new AppAttrs()); }
        catch (Exception e) { Debug.LogWarning($"Config fetch failed, using defaults: {e.Message}"); }
    }
    public int DailyRewardCoins => cfg?.GetInt("daily_reward_coins", 100) ?? 100;
    public bool PiggyBankEnabled => cfg?.GetBool("ff_piggy_bank", false) ?? false;
}
```

## PlayFab (Microsoft Azure)
- Title Data (global config), Player Data, Economy v2 (catalog, inventory, stores), CloudScript
  on Azure Functions, Segments + Scheduled Tasks, Experiments, PlayStream events.
- Fits cross-engine/multi-platform titles and Azure shops; cheapest paid tier ~$99/mo
  (third-party comparison, 2026-10 - verify on playfab.com pricing).

## Nakama / Satori (Heroic Labs)
- Nakama server core open source (Apache 2.0), Go; runtime modules in Go, TypeScript or Lua;
  built-in wallet + ledger, storage, leaderboards/tournaments, groups, chat, realtime.
- Satori (commercial): LiveOps event calendar, audiences, feature flags, experiments.
- Heroic Cloud managed hosting or self-host; good for realtime/social and cost control.
  (verify: licensing of add-ons such as Hiro metagame framework)

## Custom ASP.NET Core backend (see `studio:stack-dotnet`)
- Config: versioned JSON documents (DB or blob) published via admin tool → served through CDN
  with ETag; client sends `If-None-Match`; publish = new immutable version + pointer swap
  (instant rollback = pointer back).
- Flags: OpenFeature .NET SDK as the abstraction; provider = Microsoft.FeatureManagement,
  Unleash, Flagsmith, ConfigCat, LaunchDarkly or GrowthBook. Avoid vendor lock in call sites.
- Economy: append-only `LedgerEntry` + `Wallet` balance projection, optimistic concurrency
  (rowversion), unique index on `(PlayerId, SourceId)` for idempotency, outbox for analytics.
- Admin tool (studio:frontend-developer): role-based approvals, diff view, schedule, audit log.

```csharp
// Server-authoritative grant: client reports WHAT happened (sourceId), server decides HOW MUCH.
app.MapPost("/economy/claim", async (ClaimRequest req, ClaimsPrincipal user,
    EconomyDb db, IRewardRules rules, CancellationToken ct) =>
{
    var playerId = user.GetPlayerId();
    var prior = await db.Ledger.AsNoTracking()
        .SingleOrDefaultAsync(e => e.PlayerId == playerId && e.SourceId == req.SourceId, ct);
    if (prior is not null) return Results.Ok(prior.ToDto());           // idempotent replay
    var reward = await rules.ResolveAsync(playerId, req.SourceId, DateTime.UtcNow, ct);
    if (reward is null) return Results.Problem(statusCode: 409, title: "not_eligible");
    var wallet = await db.Wallets.SingleAsync(w => w.PlayerId == playerId && w.Currency == reward.Currency, ct);
    wallet.Balance += reward.Amount;                                   // rowversion-protected
    var entry = db.Ledger.Add(new LedgerEntry(playerId, req.SourceId, reward.Currency,
        reward.Amount, wallet.Balance, reward.ConfigVersion)).Entity;
    try { await db.SaveChangesAsync(ct); }
    catch (DbUpdateException ex) when (ex.IsUniqueViolation())         // concurrent duplicate
    { return Results.Ok((await db.Ledger.SingleAsync(e => e.PlayerId == playerId && e.SourceId == req.SourceId, ct)).ToDto()); }
    return Results.Ok(entry.ToDto());
});
```

## Server-authoritative economy checklist
- [ ] Client never sends amounts, prices or reward ids it chose; only intents + context.
- [ ] Every balance change = ledger entry with source, config version, before/after balance.
- [ ] Rate limits per player per endpoint; anomaly alerts (earn rate > p99.9 x N).
- [ ] Event progress validated server-side (plausibility: max points per minute, session time).
- [ ] Time-based rewards use server time; cooldowns stored server-side.
- [ ] Offline play (if any) reconciles via signed, bounded claims; caps on offline earnings.
- [ ] Inflation dashboard: sources vs sinks per currency per day, by segment.

## Anti-patterns
| Anti-pattern | Consequence | Fix |
|---|---|---|
| Hardcoded event dates/prices in the client | every change needs a store release | server-driven schedule + remote config |
| Client-side reward calculation | memory editors / proxies mint currency | server resolves rewards |
| One giant JSON config blob | merge conflicts, risky publishes | per-domain documents, schema per document |
| Flags never removed | combinatorial bugs, dead code | expiry date + cleanup ticket per flag |
| Targeting evaluated on the client only | players spoof segments for better offers | server evaluates; client gets the result |
| No config version on telemetry | can't attribute KPI changes | stamp config/segment/variant ids on events |
| Device clock for timers | time-travel exploits | server UTC; detect clock skew |

## Sources
- Unity Game Overrides - Get started: https://docs.unity.com/en-us/game-overrides/get-started
- Unity Economy config caching: https://docs.unity.com/en-us/Economy/config-caching.md
- Unity Cloud Code integration with other services: https://docs.unity.com/cloud-code/integration-with-other.html
- Unity status: Multiplay deprecation notice: https://status.unity.com/info_notices/362941
- Unity support (UGS LiveOps section): https://support.unity.com/hc/en-us/sections/49818013491604-Unity-Gaming-Services-LiveOps
- Heroic Labs Satori 2.0 announcement: https://heroiclabs.com/blog/announcing-satori-20/
- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- OpenFeature: https://openfeature.dev/
