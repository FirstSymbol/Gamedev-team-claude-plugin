# Architecture styles and game backend services

## Modular monolith vs microservices
| Criterion | Modular monolith (default) | Microservices |
|---|---|---|
| Team size | 1-3 teams (≤ ~25 engineers) | many teams needing independent release cadence |
| Domain clarity | boundaries still being learned | stable bounded contexts |
| Scaling profile | uniform load, scale whole app horizontally | parts with 10×+ different load/latency/availability needs |
| Ops maturity | basic CI/CD, one deploy unit | automated provisioning, observability, on-call per service (Fowler's prerequisites) |
| Data | one DB, schema per module | DB per service, eventual consistency accepted |
| Failure isolation | process-level | per-service blast radius (if designed for it) |
| Cost | lowest infra + cognitive cost | network, serialization, tracing, versioning overhead |
- Rule: start as a modular monolith (Fowler "MonolithFirst"); extract a service when a module has
  a concrete driver: independent scaling, different availability/SLO, different release cadence,
  separate team ownership, compliance isolation (e.g., payments/PCI, gambling certification scope).
- Enforce module boundaries in a monolith: one project per module (`Game.Wallet`, `Game.Players`),
  internal types `internal`, public contracts in `*.Contracts` projects, architecture tests
  (NetArchTest/ArchUnitNET) failing the build on forbidden references, schema per module.
- Distributed-monolith smells: synchronous call chains > 2 hops per request, shared DB tables,
  lock-step deploys, shared "common" library with domain logic.

## Event-driven architecture
| Pattern | Use | Watch |
|---|---|---|
| Event notification | decouple modules ("PlayerLeveledUp") | hidden flow; document event catalog |
| Event-carried state transfer | consumers keep local copies | eventual consistency, schema versioning |
| Event sourcing | audit-critical aggregates (ledger, match history) | complexity, replays, snapshots; not for everything |
| Outbox pattern | atomic DB write + publish | mandatory when publishing from a transaction (see stack-dotnet realtime-and-messaging) |
- Delivery is at-least-once: every consumer idempotent (dedupe by message ID / business key).
- Events are contracts: versioned schemas, additive changes, owner per event type.
- Analytics telemetry is a separate pipeline (high volume, lossy-tolerant) from domain events.

## CQRS — when and when not
- Use when: read and write models differ strongly (leaderboards, dashboards, admin search),
  read load ≫ write load, or with event sourcing. Can be as light as separate query handlers
  using Dapper/read replicas.
- Avoid when: CRUD with simple screens; small team; strong read-your-writes needs everywhere.
- Fowler: CQRS adds risky complexity; apply to specific bounded contexts, not the whole system.

## Hexagonal / ports and adapters (clean/onion family)
- Domain + application core with no framework references; ports = interfaces the core owns;
  adapters = EF Core, HTTP, queues, Unity APIs.
- Pays off for: rule-heavy domains (economy, wallet, matchmaking rules), code shared between Unity
  and server (pure C# core in `netstandard2.1`), testability with fakes.
- Don't over-layer CRUD: vertical slice architecture (feature folders, one handler per use case)
  is fine for simple endpoints; mix per module.

## Other styles (quick decision)
| Style | Choose when |
|---|---|
| Serverless functions | spiky, event-driven, low-steady-load tasks (receipt validation webhooks, cron jobs); avoid for latency-critical game loops |
| Actor model (Orleans) | many stateful entities with independent lifecycles (players, rooms, lobbies); Orleans is .NET-native |
| Dedicated game servers | realtime authoritative simulation (see `studio:domain-multiplayer`) |
| BFF (backend-for-frontend) | different clients (Unity, admin web, partners) need different shapes |
| Cell-based | very large scale or regional isolation; blast radius per cell |

## Game backend reference services
| Service | Responsibility | Key design rules |
|---|---|---|
| Auth/identity | device/guest, platform (Apple, Google Play Games, Steam, console), email/OIDC; account linking; JWT issuance | short-lived access JWT (5-15 min) + rotating refresh; server validates platform tokens; link/merge flows; ban/kick |
| Player profile | profile, inventory, progression, settings | owned by one module; optimistic concurrency (version/ETag); save conflict policy |
| Wallet / ledger | balances of soft/hard currency, chips; purchases, rewards, bets/wins | double-entry ledger, immutable entries, balance = derived/cached; idempotency key per operation; `long` minor units; serializable or row-lock per account; reconciliation jobs; audit trail |
| Store / IAP | catalog, offers, receipt validation (App Store Server API, Google Play Developer API, Steam microtransactions) | server-side receipt validation, grant via ledger with transaction ID dedupe; handle refunds/voids webhooks |
| Live-ops config | remote config, feature flags, A/B assignments, event schedules, catalogs | versioned config snapshots; schema-validated; staged rollout; client caches with TTL + defaults baked in |
| Matchmaking | queues, rating (Elo/Glicko/TrueSkill), party handling, region/latency | separate from game servers; tickets with timeouts and widening; see domain-multiplayer |
| Leaderboards | rankings, seasons, tournaments | Redis sorted sets for live; persisted snapshots; anti-cheat validation server-side |
| Social | friends, clubs/guilds, chat, gifts | rate limits, moderation hooks, blocking |
| Messaging / inbox | rewards inbox, notifications (APNs/FCM) | idempotent claims; expiry |
| Telemetry ingest | analytics events | batch, compress, async; separate from gameplay path |
| Admin / back-office | CS tools, player lookup, grants, bans, config editing, reports | RBAC + audit log for every write; four-eyes for currency grants above threshold |
- Casino/social casino: RNG and game math run server-side; spin = one atomic transaction
  (debit bet, compute outcome, credit win) with idempotency; RNG certification and jurisdiction
  rules → `studio:domain-igaming`.

## Wallet/ledger sketch (C#)
```csharp
public sealed record LedgerEntry(Guid Id, Guid TxId, Guid AccountId, string Currency,
    long AmountMinor, string Reason, string IdempotencyKey, DateTimeOffset At);
// Invariant: entries of one TxId sum to zero across accounts (double entry).
// Unique index (AccountId, IdempotencyKey) → retries return the original result.
// Balance check + insert in one transaction with row lock (SELECT ... FOR UPDATE on account row)
// or optimistic concurrency on an AccountBalance(version) row.
```

## Decision record minimum for style choices
- Drivers (quality attributes with numbers), team topology, ops maturity, options compared,
  migration path if wrong (e.g., "module X extracted when RPS > 2k or team > 2").

## Sources
- Martin Fowler, "MonolithFirst" https://martinfowler.com/bliki/MonolithFirst.html
- Martin Fowler, "Microservice Prerequisites" https://martinfowler.com/bliki/MicroservicePrerequisites.html
- Martin Fowler, "CQRS" https://martinfowler.com/bliki/CQRS.html
- Martin Fowler, "What do you mean by Event-Driven?" https://martinfowler.com/articles/201701-event-driven.html
- Microsoft Azure Architecture Center, "Architecture styles" https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/
- Alistair Cockburn, "Hexagonal Architecture", 2005 https://alistair.cockburn.us/hexagonal-architecture/
- AWS, "Guidance for Custom Game Backend Hosting on AWS" https://github.com/aws-solutions-library-samples/guidance-for-custom-game-backend-hosting-on-aws
- Microsoft Learn, "Solutions for the game development industry" https://learn.microsoft.com/en-us/azure/architecture/industries/game-development
