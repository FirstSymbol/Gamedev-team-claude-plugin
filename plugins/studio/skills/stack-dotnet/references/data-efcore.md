# Data access: EF Core 10, PostgreSQL, Dapper, Redis

## Baseline
- EF Core 10 (LTS, supported to 2028-11-10) requires .NET 10. EF Core 11 ships with .NET 11
  (STS); read its breaking changes first (SQL Server compat level 160 default, `Migrate()` throws
  with zero migrations, `DbQueryConcurrencyException` from split queries, Microsoft.Data.SqlClient 7).
- PostgreSQL provider: `Npgsql.EntityFrameworkCore.PostgreSQL` — major version tracks EF Core.

## DbContext lifetime and registration
```csharp
builder.Services.AddDbContextPool<GameDb>(o => o
    .UseNpgsql(dataSource, npg => npg.EnableRetryOnFailure())
    .UseSnakeCaseNamingConvention());            // EFCore.NamingConventions
```
- Scoped per request; not thread-safe: never share one DbContext across parallel tasks
  (`Task.WhenAll` over the same context = exception). Background work: `IServiceScopeFactory` per unit of work.
- Pooling: no per-request state in the context constructor (pooled instances are reset, not rebuilt).
- Use `NpgsqlDataSource` (`NpgsqlDataSourceBuilder`) as the single connection factory; map enums
  and plugins (NodaTime, JSON) there.

## Migrations workflow
1. `dotnet ef migrations add <Name>` → review the C# AND the SQL (`dotnet ef migrations script <from> <to>`).
2. Never edit a migration that has run anywhere shared; add a new one.
3. Deploy: idempotent script (`migrations script --idempotent`) or a migration bundle
   (`dotnet ef migrations bundle`) run as a separate deploy step/job — not `Database.Migrate()` at
   startup of N replicas (races, long locks, app crash loops).
4. Zero-downtime = expand/contract: add nullable column → deploy code writing both → backfill in
   batches → switch reads → drop old in a later release. Renames are drop+add for old app versions.
5. Large tables: create indexes `CONCURRENTLY` (raw SQL in migration, outside transaction on PostgreSQL); set `lock_timeout`.
6. CI check: `dotnet ef migrations has-pending-model-changes` (EF 8+) fails the build on forgotten migrations.

## Query performance checklist
| Problem | Fix |
|---|---|
| Tracking overhead on reads | `AsNoTracking()` (or `UseQueryTrackingBehavior(NoTracking)` for read-heavy contexts) |
| Over-fetching | project to DTO with `Select(...)`; never return entities from APIs |
| N+1 | no lazy loading (don't install Proxies); `Include` or projection; watch logs for repeated queries |
| Cartesian explosion (2+ collection Includes) | `AsSplitQuery()` (needs stable ordering; EF 11 throws on concurrent modification) |
| Hot repeated query | `EF.CompileAsyncQuery(...)` static field; compiled model for big models (startup) |
| Bulk changes | `ExecuteUpdateAsync`/`ExecuteDeleteAsync` (bypass change tracker + interceptors + concurrency tokens) |
| Deep paging | keyset pagination `WHERE (created_at, id) < (@c, @id) ORDER BY created_at DESC, id DESC LIMIT n` |
| `Contains` on lists | EF 10 default = padded scalar parameters; override `EF.Constant`/`EF.Parameter` or `UseParameterizedCollectionMode` per case |
| Slow unknown query | `TagWith("feature:x")`, log SQL in Development, `EXPLAIN (ANALYZE, BUFFERS)` on PostgreSQL |
- Client evaluation of untranslatable LINQ throws (since EF 3); don't "fix" with `AsEnumerable()` on large sets.
- `FindAsync` hits the change tracker first; good for key lookups in write paths.
- Soft delete / multi-tenant: EF 10 named query filters `HasQueryFilter("Tenant", ...)`, disable selectively
  `IgnoreQueryFilters(["SoftDelete"])`. Tenant filter must never be ignorable from user input.
- Complex types (EF 10) replace owned types for value objects and JSON columns: `ComplexProperty(x => x.Address)` (columns) or `ComplexProperty(x => x.Address, b => b.ToJson())`.

## Concurrency tokens (optimistic)
```csharp
public sealed class Wallet {
    public Guid Id { get; set; }
    public long BalanceMinor { get; set; }
    [Timestamp] public uint Version { get; set; } // Npgsql maps uint [Timestamp] to system column xmin
}
// SQL Server: [Timestamp] public byte[] RowVersion { get; set; } = [];
```
- On conflict EF throws `DbUpdateConcurrencyException` → reload + retry (bounded, 3x) or return 409.
- `ExecuteUpdate` ignores tokens: add the version/balance predicate in `Where` yourself, check affected rows.
- Atomic conditional update for counters/balances (no read-modify-write race):
  `await db.Wallets.Where(w => w.Id == id && w.BalanceMinor >= amt).ExecuteUpdateAsync(s => s.SetProperty(w => w.BalanceMinor, w => w.BalanceMinor - amt), ct)` → 0 rows = insufficient funds/conflict.

## Transactions
- One `SaveChangesAsync` is atomic already; use explicit transactions only to span multiple saves/raw SQL.
- With `EnableRetryOnFailure`, wrap explicit transactions in the execution strategy:
```csharp
var strategy = db.Database.CreateExecutionStrategy();
await strategy.ExecuteAsync(async () => {
    await using var tx = await db.Database.BeginTransactionAsync(IsolationLevel.ReadCommitted, ct);
    // ... changes + outbox rows ...
    await db.SaveChangesAsync(ct);
    await tx.CommitAsync(ct);
}); // whole block re-runs on transient failure: keep it idempotent
```
- PostgreSQL default is READ COMMITTED. Pessimistic row lock: `FromSql($"SELECT * FROM wallets WHERE id = {id} FOR UPDATE")`
  inside the transaction; lock rows in a consistent order (by id) to avoid deadlocks.
- SERIALIZABLE on PostgreSQL may abort with SQLSTATE 40001 → must retry the whole transaction.
- Never hold a transaction across external HTTP calls (payment provider, platform receipt check).
- `TransactionScope` across connections → distributed transactions; avoid. Use outbox (realtime-and-messaging).

## Dapper vs EF Core
| Use Dapper (or raw `NpgsqlCommand`) | Stay with EF Core |
|---|---|
| reporting/analytics SQL, CTEs, window functions | CRUD, aggregates with invariants |
| hot read path proven by profiling | anything needing change tracking/concurrency tokens |
| bulk import (`NpgsqlBinaryImporter` COPY) | migrations-owned schema |
- Both can share the connection/transaction: `db.Database.GetDbConnection()` + `GetDbTransaction()`.
- EF also has `SqlQuery<T>($"...")` for unmapped DTOs (interpolated = parameterized). `FromSqlRaw` +
  string concatenation is SQL injection (EF 10 analyzer warns).

## PostgreSQL / Npgsql specifics
- `timestamp with time zone` requires `DateTime.Kind == Utc` (Npgsql 6+ strict); prefer `DateTimeOffset`/UTC everywhere.
- Enums: `dataSourceBuilder.MapEnum<Rarity>()` + `npg.MapEnum<Rarity>()` or store as string (simpler migrations).
- `jsonb` for flexible blobs (player settings); index with GIN only when queried.
- Pooling: Npgsql pool per connection string (default Max Pool Size 100); total = replicas × pool ≤ `max_connections`.
  With PgBouncer transaction mode: avoid session state, set `No Reset On Close=true`, protocol-level prepared statements need PgBouncer ≥ 1.21 with `max_prepared_statements` > 0.
- Use `citext` or `lower()` index for case-insensitive unique usernames/emails.
- Sequences/identity for internal PKs; UUIDv7 (`Guid.CreateVersion7()`) for public IDs if insert locality matters.

## Redis and caching
- `StackExchange.Redis` `IConnectionMultiplexer` = singleton; never per request.
- `HybridCache` (Microsoft.Extensions.Caching.Hybrid, GA 2025): L1 in-memory + L2 `IDistributedCache`,
  stampede protection, tags.
```csharp
builder.Services.AddStackExchangeRedisCache(o => o.Configuration = redisConn);
builder.Services.AddHybridCache(o => o.DefaultEntryOptions = new() {
    Expiration = TimeSpan.FromMinutes(5), LocalCacheExpiration = TimeSpan.FromMinutes(1) });
var cfg = await cache.GetOrCreateAsync($"liveops:config:{region}",
    async ct => await LoadConfig(region, ct), tags: ["liveops"], cancellationToken: ct);
```
- Cache-aside with TTL + jitter; key schema `<service>:<entity>:<id>:v<schemaVersion>`.
- Invalidate on write (tag eviction or key delete after commit); tolerate stale reads only where the spec allows.
- Never treat cache as source of truth for balances, inventory, entitlements.
- Other Redis uses: leaderboards (sorted sets `ZADD/ZREVRANGE`), presence, SignalR backplane,
  short-lived locks (`SET key val NX PX`), idempotency key store with TTL. Redlock is not a correctness
  guarantee: still enforce invariants in the DB (unique constraints, conditional updates).

## Sources
- What's new in EF Core 10 https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew
- Breaking changes in EF Core 11 https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-11.0/breaking-changes
- EF Core efficient querying https://learn.microsoft.com/en-us/ef/core/performance/efficient-querying
- EF Core handling concurrency conflicts https://learn.microsoft.com/en-us/ef/core/saving/concurrency
- EF Core connection resiliency https://learn.microsoft.com/en-us/ef/core/miscellaneous/connection-resiliency
- Npgsql EF Core concurrency tokens https://www.npgsql.org/efcore/modeling/concurrency.html
- HybridCache library https://learn.microsoft.com/en-us/aspnet/core/performance/caching/hybrid
- PgBouncer changelog (1.21 prepared statements) https://www.pgbouncer.org/changelog.html
