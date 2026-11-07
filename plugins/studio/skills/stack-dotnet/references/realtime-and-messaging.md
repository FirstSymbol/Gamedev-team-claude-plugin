# Realtime, background work, messaging

## Pick the transport
| Need | Use | Avoid |
|---|---|---|
| Server → client push (balance update, jackpot ticker, notifications) | SignalR | polling < 5 s |
| One-way live feed to browser admin dashboards | SSE (`TypedResults.ServerSentEvents`, .NET 10) or SignalR | WebSocket hand-rolled |
| Service ↔ service RPC, streaming, strict contracts | gRPC (HTTP/2) | JSON over HTTP for chatty internal calls |
| Fast-paced game state sync (tick-based) | dedicated netcode/UDP (multiplayer-network-engineer) | SignalR for 30+ Hz state |
| Async workflows, fan-out, decoupling | message broker + outbox | in-memory events across services |

## SignalR
```csharp
public interface IPlayerClient { Task BalanceChanged(BalanceDto b); Task Kicked(string reason); }
[Authorize]
public sealed class PlayerHub : Hub<IPlayerClient> {
    public override async Task OnConnectedAsync() =>
        await Groups.AddToGroupAsync(Context.ConnectionId, $"player:{Context.UserIdentifier}");
}
// from any service: IHubContext<PlayerHub, IPlayerClient> hub
await hub.Clients.User(playerId).BalanceChanged(dto);
```
- Strongly typed hubs; hub methods thin (validate → call handler). Hub instances are transient: no state in fields.
- Auth: browsers/WebSockets can't set headers → token via `access_token` query string; read it in
  `JwtBearerEvents.OnMessageReceived` for the hub path only; exclude it from request logs.
- `Context.UserIdentifier` defaults to `NameIdentifier` claim; with `MapInboundClaims=false` set a custom `IUserIdProvider` (`sub`).
- Limits: `MaximumReceiveMessageSize` default 32 KB; keep messages small, send IDs/deltas not snapshots.
- Reliability: SignalR is at-most-once. Client must re-fetch state on reconnect (HTTP GET), messages carry
  version/sequence so clients drop stale ones. .NET 8+ stateful reconnect (`AllowStatefulReconnects`) buffers briefly; not a guarantee.
- MessagePack hub protocol (`AddMessagePackProtocol`) cuts payload size; JSON is easier to debug.
- Scale-out:
| Option | Notes |
|---|---|
| Redis backplane `AddStackExchangeRedis(conn, o => o.Configuration.ChannelPrefix = RedisChannel.Literal("game"))` | every message goes to every server; needs sticky sessions unless clients use WebSockets with `SkipNegotiation` |
| Azure SignalR Service | managed connections, no sticky sessions; Azure lock-in |
| Partition by game room/table | route clients of one room to one node; simplest for game tables |
- Sticky sessions required for negotiate + long polling/SSE fallback behind a load balancer.

## gRPC
- `Grpc.AspNetCore`; proto-first contracts in a shared `Contracts` project (`<Protobuf Include=... GrpcServices="Server|Client" />`).
- Always set deadlines client-side (`deadline: DateTime.UtcNow.AddSeconds(2)`) and propagate `CancellationToken`.
- Needs HTTP/2 end-to-end; L4 load balancers pin one connection → use L7 (Envoy/YARP) or client-side balancing.
- Browsers / Unity WebGL: gRPC-Web (`app.UseGrpcWeb()` + `.EnableGrpcWeb()`), unary + server streaming only.
- JSON transcoding (`AddJsonTranscoding`) exposes the same service as REST for admin tools.
- Proto evolution: never reuse/renumber field numbers; `reserved` removed ones; add fields only.
- Unity client: `Grpc.Net.Client` + Cysharp YetAnotherHttpHandler (C-core gRPC for Unity is discontinued); see unity-interop.

## Background services
```csharp
public sealed class SettlementWorker(IServiceScopeFactory scopes, ILogger<SettlementWorker> log) : BackgroundService {
    protected override async Task ExecuteAsync(CancellationToken stop) {
        using var timer = new PeriodicTimer(TimeSpan.FromSeconds(5));
        while (await timer.WaitForNextTickAsync(stop)) {
            try {
                await using var scope = scopes.CreateAsyncScope();
                await scope.ServiceProvider.GetRequiredService<SettlementJob>().RunBatch(stop);
            } catch (Exception ex) when (ex is not OperationCanceledException) {
                log.LogError(ex, "Settlement batch failed");   // keep the loop alive
            }
        }
    }
}
```
- Unhandled exception in `ExecuteAsync` stops the host by default (`BackgroundServiceExceptionBehavior.StopHost`, .NET 6+).
- Resolve scoped services (DbContext) per iteration via scope; never inject them into the singleton worker.
- Graceful shutdown: honor the token; `HostOptions.ShutdownTimeout` (default 30 s) must exceed your batch time; K8s `terminationGracePeriodSeconds` larger still.
- In-process queue: `System.Threading.Channels` bounded channel (`BoundedChannelFullMode.Wait`); lost on crash → only for best-effort work.
- Multiple replicas run every worker: use a DB lease/`SELECT ... FOR UPDATE SKIP LOCKED` batch claim, or move to a queue.
- Schedulers: Quartz.NET (Apache-2.0, clustered via DB), Hangfire (LGPL core, Pro paid; dashboard needs auth), TickerQ (young project, small community: spike before adopting).

## Brokers
| Broker | Strength | Ordering | Notes |
|---|---|---|---|
| RabbitMQ | work queues, routing, simple ops | per queue (single consumer) | `RabbitMQ.Client` 7.x is async-only API; quorum queues for durability |
| Kafka | high-throughput event streams, replay | per partition (key = playerId) | `Confluent.Kafka`; consumer groups; commit offsets after processing |
| Azure Service Bus / AWS SQS | managed, sessions/FIFO | sessions / FIFO groups | dead-letter built in |
| PostgreSQL as queue | low volume, no new infra | `SKIP LOCKED` | rule of thumb < ~100 msg/s; load-test before relying on it |

| Library | License (2026) | Use |
|---|---|---|
| MassTransit v8 | Apache-2.0; security patches through end of 2026 | existing projects; plan v9 license or exit |
| MassTransit v9 | commercial (Massient), released; support via subscription | if budget approved |
| Wolverine (JasperFx) | MIT | new OSS projects; built-in EF/Marten outbox, local + RabbitMQ/Kafka/ASB |
| Rebus | MIT (Pro add-ons paid) | lightweight bus |
| NServiceBus | commercial | enterprise sagas |
| Raw client | — | single queue, few message types |

## Delivery semantics
- Assume at-least-once everywhere. Exactly-once processing = at-least-once delivery + idempotent consumer.
- Retry: immediate 1–3x, then delayed with exponential backoff + jitter, then dead-letter queue with alert.
- Poison messages: DLQ after N attempts; tool to inspect/replay; never infinite requeue.
- Message contract: `messageId` (UUID), `correlationId`, `occurredAt` (UTC), `schemaVersion`, producer;
  events in past tense (`PurchaseCompleted`), commands imperative (`GrantReward`).

## Transactional outbox
Problem: `SaveChanges()` then `Publish()` — crash between them loses the event; reverse order publishes phantom events.
1. In the same DB transaction as the state change, insert an `outbox_messages` row (id, type, payload, created_at).
2. A relay (BackgroundService, Wolverine/MassTransit outbox, or Debezium CDC) publishes unsent rows,
   marks `sent_at`; publish is at-least-once.
3. Consumers keep an inbox/processed table: `INSERT (message_id) ... ON CONFLICT DO NOTHING` in the
   same transaction as their effect; 0 rows inserted = duplicate → ack and skip.
4. Clean up sent rows after retention (e.g. 7 days); index `sent_at IS NULL`.
- MassTransit: `AddEntityFrameworkOutbox<TDb>(o => o.UsePostgres().UseBusOutbox())`. Wolverine: `UseEntityFrameworkCoreTransactions()` + durable outbox.

## Idempotency patterns
| Level | Technique |
|---|---|
| HTTP command | `Idempotency-Key` header (client UUID per user action); store key + request hash + response; replay same response; 409/422 if same key different body |
| DB | unique constraint on natural key (`(provider, transaction_id)`, `(player_id, reward_day)`) — the final guard |
| Consumer | inbox table keyed by `messageId` |
| State machine | transition only from expected state: `UPDATE ... WHERE state = 'Pending'` |
| Commutative ops | "set to X" over "add X" where the domain allows |
- Keys expire (24 h–7 days typical; Stripe keeps 24 h) but DB uniqueness on business keys never expires.

## Sources
- SignalR scale-out https://learn.microsoft.com/en-us/aspnet/core/signalr/scale
- SignalR authentication https://learn.microsoft.com/en-us/aspnet/core/signalr/authn-and-authz
- gRPC on .NET https://learn.microsoft.com/en-us/aspnet/core/grpc/
- Background tasks with hosted services https://learn.microsoft.com/en-us/aspnet/core/fundamentals/host/hosted-services
- Transactional outbox pattern https://microservices.io/patterns/data/transactional-outbox.html
- Milan Jovanovic, MediatR and MassTransit going commercial https://dev.to/milanjovanovictech/mediatr-and-masstransit-going-commerical-what-this-means-for-you-2ppi
- MassTransit v9 commercial (Massient) https://masstransit.massient.com/introduction/v9-announcement
- Wolverine docs https://wolverinefx.net/
- Stripe idempotent requests https://docs.stripe.com/api/idempotent_requests
