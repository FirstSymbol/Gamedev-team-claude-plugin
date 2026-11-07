# Realtime services in .NET (implementation reference)

## Which .NET option
| Need | Use | Not for |
|---|---|---|
| Turn-based, card/casino tables, lobbies, chat, presence, live leaderboards | ASP.NET Core SignalR (WebSockets) | > ~10 Hz movement sync |
| Many stateful rooms/tables/sessions with single-writer semantics | Orleans grains (+ SignalR for client push) | per-frame physics |
| Realtime action server without Unity headless | custom UDP: LiteNetLib (or ENet/Kcp2k/Riptide) + shared sim library | teams without netcode experience |
| Request/response game APIs | minimal APIs / gRPC (server-to-server) | push |

## Shared simulation library
- `netstandard2.1` class library (DTOs, message codecs, rules, sim step) referenced by the .NET server
  and consumed by Unity (local package or DLL). No `UnityEngine` references; use `System.Numerics`
  or own fixed-point types.
- Same code = same results only if deterministic: avoid `Dictionary` iteration order in sim logic,
  use seeded RNG in state, consider fixed-point for lockstep/rollback.
- See `studio:stack-dotnet` for project layout/hosting and `studio:stack-unity` for consuming DLLs.

## SignalR for tables and lobbies
```csharp
public interface ITableClient { Task State(TableStateDto s); Task Error(string code); }

[Authorize]
public sealed class TableHub(IGrainFactory grains) : Hub<ITableClient> {
    public async Task Join(string tableId) {
        var snapshot = await grains.GetGrain<ITableGrain>(tableId).Join(PlayerId);
        await Groups.AddToGroupAsync(Context.ConnectionId, tableId);
        await Clients.Caller.State(snapshot);                       // full snapshot on (re)join
    }
    public Task<BetResult> PlaceBet(string tableId, PlaceBetCmd cmd) =>  // cmd carries idempotency key
        grains.GetGrain<ITableGrain>(tableId).PlaceBet(PlayerId, cmd);
    string PlayerId => Context.UserIdentifier!;                     // from JWT sub, never from client args
}
// Program.cs
builder.Services.AddSignalR(o => o.MaximumReceiveMessageSize = 32 * 1024)   // 32 KB is the default; keep small
       .AddMessagePackProtocol();                                           // smaller/faster than JSON
app.MapHub<TableHub>("/hubs/table", o => o.AllowStatefulReconnects = true); // .NET 8+ stateful reconnect
```
- Auth over WebSockets: JWT arrives as `access_token` query param — read it in
  `JwtBearerEvents.OnMessageReceived` for the hub path only; keep tokens short-lived.
- Server push from outside the hub: inject `IHubContext<TableHub, ITableClient>`; Orleans grain
  → stream/observer → SignalR group broadcast.
- Every state message carries `tableId`, monotonically increasing `seq`, server timestamp; client
  drops stale `seq`, requests snapshot on gap.
- Reconnect: client `WithAutomaticReconnect()` (+ `WithStatefulReconnect()` on .NET client); on
  reconnect, re-join groups (groups are per connection) and fetch snapshot.
- Scale-out: Redis backplane (`AddStackExchangeRedis`) or Azure SignalR Service; without Azure
  SignalR, sticky sessions are required unless clients use WebSockets with `SkipNegotiation`.
- Rate-limit hub methods (per user) and validate every argument; hubs are public API surface.
- Unity client: `Microsoft.AspNetCore.SignalR.Client` DLLs (via NuGetForUnity) work on standalone/
  mobile with IL2CPP given `link.xml` preservation; WebGL needs a JS-side client or a WebSocket
  library with JS interop (commercial: Best HTTP) (verify: WebGL support of the chosen wrapper/version
  on its own docs — Microsoft does not ship a Unity WebGL SignalR client).

## Orleans for rooms/tables/sessions
```csharp
public interface ITableGrain : IGrainWithStringKey {
    Task<TableStateDto> Join(string playerId);
    Task<BetResult> PlaceBet(string playerId, PlaceBetCmd cmd);
}
public sealed class TableGrain(
    [PersistentState("table", "tables")] IPersistentState<TableState> state,
    IWalletClient wallet, IRng rng) : Grain, ITableGrain {
    public async Task<BetResult> PlaceBet(string playerId, PlaceBetCmd cmd) {
        if (state.State.Phase != Phase.Betting) return BetResult.Rejected("phase");
        if (state.State.Processed.Contains(cmd.IdemKey)) return state.State.Results[cmd.IdemKey];
        var debit = await wallet.Debit(playerId, cmd.AmountMinor, cmd.IdemKey);   // ledger is source of truth
        if (!debit.Ok) return BetResult.Rejected("funds");
        state.State.AddBet(playerId, cmd); await state.WriteStateAsync();
        return BetResult.Accepted(state.State.Seq);
    }
}
[GenerateSerializer] public sealed record PlaceBetCmd([property: Id(0)] string IdemKey, [property: Id(1)] long AmountMinor);
```
- Grains are single-threaded per activation (turn-based concurrency): no locks needed inside; avoid
  long awaits that block the table — use timeouts on external calls.
- Round timers: grain timers (`this.RegisterGrainTimer(cb, state, new GrainTimerCreationOptions { DueTime, Period })`,
  Orleans 8.2+; `RegisterTimer` obsolete; callbacks don't interleave by default) for in-memory phases;
  reminders (`RegisterOrUpdateReminder` + `IRemindable`) for durable schedules (minutes+). Docs cover Orleans 8–10.
- Money stays in the wallet/ledger service with DB transactions and idempotency (security-engineer
  payments-and-data.md); grain state holds table state, not balances.
- RNG via certified RNG service for real-money games (`studio:domain-igaming`).
- Co-host Orleans silo + SignalR in one ASP.NET Core app for small scale; split later.
- Clustering: Azure Table/ADO.NET/Redis/Kubernetes membership providers; grain placement handles
  table distribution and failover (state reloads from storage on reactivation).

## Custom UDP server with LiteNetLib
```csharp
var listener = new EventBasedNetListener();
var net = new NetManager(listener) { AutoRecycle = true, DisconnectTimeout = 10_000 };
net.Start(port);
listener.ConnectionRequestEvent += req => {
    if (ConnectToken.TryValidate(req.Data.GetString(), out var claims)) req.Accept();  // signed, expiring token
    else req.Reject();
};
listener.NetworkReceiveEvent += (peer, reader, channel, method) => inbox.Enqueue(peer.Id, reader.GetRemainingBytes());

var sw = Stopwatch.StartNew(); double acc = 0, last = 0, dt = 1.0 / 30;
while (!ct.IsCancellationRequested) {
    net.PollEvents();
    double now = sw.Elapsed.TotalSeconds; acc += now - last; last = now;
    while (acc >= dt) { sim.Tick(inbox.Drain()); BroadcastSnapshots(); acc -= dt; }
    Thread.Sleep(1);                                    // see timer note below
}
```
- `DeliveryMethod`: `Unreliable`/`Sequenced` for state/input, `ReliableOrdered` for rare events; use channels.
- Timer precision: Windows default timer resolution ~15.6 ms — `Task.Delay`/`PeriodicTimer` jitter
  ruins 60 Hz loops; use a Stopwatch accumulator as above. Linux containers are better but still
  measure tick jitter.
- Run the loop on a dedicated thread (`new Thread(Loop) { IsBackground = true }`), not the thread pool.
- Zero-alloc hot path: pooled `NetDataWriter`, structs, `ArrayPool<byte>`; Server GC + `TieredPGO`; measure GC pauses.
- ENet-CSharp, Kcp2k, Riptide are alternatives (none archived on GitHub as of 2026-11); check last
  release date and open issues before adopting.

## Connect tokens (dedicated servers)
- Matchmaker/backend issues token: `{playerId, sessionId, serverAddr, expiresAt (≤ 30–60 s), nonce}`
  signed with Ed25519/HMAC key shared only with game servers (netcode.io connect-token pattern).
- Server validates signature, expiry, sessionId match, single use (nonce cache) → binds peer to playerId.
- Session key in token enables packet encryption/MAC for custom UDP; UTP/DTLS covers it for Unity Transport.

## Server → backend reporting
- Game server authenticates as a service (OAuth client credentials or mTLS), never with a player token.
- `POST /matches/{matchId}/result` idempotent by matchId; backend validates participants vs
  allocation record; rewards computed by backend from result, not sent by the server as amounts.

## Observability for realtime services
- Metrics: connections, messages/s in/out, broadcast latency, tick duration p99, rooms/grains
  active, reconnects/min, rejected commands by reason (cheat signal).
- Traces: per command (bet, join) through hub → grain → wallet; `seq` and `tableId` as attributes, not metric labels.

## Sources
- Microsoft Learn: ASP.NET Core SignalR (scale-out, auth, MessagePack, stateful reconnect) https://learn.microsoft.com/aspnet/core/signalr/introduction
- Microsoft Learn: SignalR scale-out and sticky sessions https://learn.microsoft.com/aspnet/core/signalr/scale
- Microsoft Learn: Orleans overview https://learn.microsoft.com/dotnet/orleans/overview
- Microsoft Learn: Orleans timers and reminders https://learn.microsoft.com/dotnet/orleans/grains/timers-and-reminders
- LiteNetLib https://github.com/RevenantX/LiteNetLib
- netcode.io standard (connect tokens) https://github.com/mas-bandwidth/netcode/blob/main/STANDARD.md
- Glenn Fiedler, "Fix Your Timestep!" https://gafferongames.com/post/fix_your_timestep/
