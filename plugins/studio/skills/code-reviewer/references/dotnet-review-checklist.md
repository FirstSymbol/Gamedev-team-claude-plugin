# C#/.NET review checklist

Apply to changed lines + their direct callers. Severity hints in brackets: [B]locker, [M]ajor, [m]inor.

## Correctness and language
- [M] Nullable warnings suppressed with `!` without justification; `#nullable disable` in new code.
- [M] `async void` (except event handlers); fire-and-forget `_ = DoAsync()` without error handling.
- [B] Sync-over-async: `.Result`, `.Wait()`, `GetAwaiter().GetResult()` in request/worker paths (deadlock/thread-pool starvation).
- [M] `CancellationToken` accepted but not passed to I/O calls; `HttpContext.RequestAborted` ignored in long ops.
- [M] Exceptions swallowed (`catch { }`, `catch (Exception) { return null; }`); `throw ex;` (loses stack) instead of `throw;`.
- [m] Catching `Exception` where a specific type is expected; `OperationCanceledException` logged as error.
- [M] Floating point for money/currency; integer overflow on balances without `checked`/`long`.
- [M] `DateTime.Now`/local time in server logic; `DateTime` Kind mixing; use `TimeProvider` + UTC/`DateTimeOffset`.
- [m] String comparison without `StringComparison` for identifiers; culture-sensitive parsing (`double.Parse` without `CultureInfo.InvariantCulture`).
- [m] LINQ multiple enumeration of `IEnumerable` from DB/expensive sources; `Count() > 0` instead of `Any()`.
- [m] Mutable public collections/`List<T>` exposed from domain types; prefer `IReadOnlyList<T>`.
- [m] `record` with mutable collection members (equality surprises); `struct` too large/mutable.
- C# 14/15 features fine on matching TFM; flag in shared `netstandard2.1` libs consumed by Unity (C# 9 max).

## Dependency injection and lifetimes
- [B] Scoped service (DbContext, per-request) captured in a singleton or BackgroundService field.
- [M] `new HttpClient()` per call; `HttpClient` without timeout/resilience; use `IHttpClientFactory`.
- [M] `BuildServiceProvider()` during registration; service locator (`IServiceProvider.GetService`) in business code.
- [m] Options read via `IConfiguration["..."]` in business code instead of typed, validated options.

## ASP.NET Core endpoints
- [B] Missing authorization on new endpoint, or object-level check missing (ID from route/body not verified against caller).
- [B] Binding request directly to EF entity (mass assignment: client can set `Balance`, `Role`, `OwnerId`).
- [M] Returning EF entities (over-exposure, lazy-load serialization cycles); return DTOs.
- [M] Errors not ProblemDetails / inconsistent codes; stack traces or exception messages returned to clients.
- [M] State-changing endpoint without idempotency (key or natural unique constraint) where retries/double taps are possible.
- [M] No input limits: unbounded `pageSize`, string lengths, collection sizes, file size.
- [m] Missing `TypedResults`/`Produces` metadata → OpenAPI drift; contract change without version/changelog.
- [M] Breaking contract change (rename/remove field, enum change, new required input) without new version + ADR.

## EF Core and data
- [B] `FromSqlRaw`/`ExecuteSqlRaw`/Dapper with string concatenation or interpolation into raw SQL text.
- [B] Read-modify-write on balances/counters without concurrency token, row lock or conditional update.
- [M] N+1: navigation access in loops, lazy loading, per-item queries; missing `Include`/projection.
- [M] Multiple collection `Include` without `AsSplitQuery` on large sets (cartesian explosion).
- [M] Tracking queries for read-only endpoints (`AsNoTracking` missing on hot paths).
- [M] `DbContext` used across parallel tasks (`Task.WhenAll` over same context).
- [M] Explicit transaction with retrying execution strategy not wrapped in `strategy.ExecuteAsync`.
- [M] External HTTP calls inside a DB transaction/lock.
- [M] Migration: destructive change (drop/rename column) in same release as code change; missing index for new filter; data backfill in one huge statement; edited already-applied migration.
- [m] `ToList()` before `Where` (client-side filtering); `Count()` for existence checks.
- [M] Event published before/without commit (no outbox) when consistency matters.

## Concurrency and background work
- [B] Shared mutable static state without synchronization; non-thread-safe collections in singletons (use `ConcurrentDictionary`, immutable snapshots).
- [M] `lock` around `await` (won't compile) replaced with ad-hoc flags; use `SemaphoreSlim`; .NET 9+ `System.Threading.Lock` for sync locks.
- [M] BackgroundService loop without try/catch (crash stops host) or ignoring stop token.
- [M] Work assumed single-instance (timers, schedulers) in a multi-replica deployment without lease/lock.
- [m] `Task.Run` in ASP.NET request path to "make it async".

## Logging and observability
- [B] Secrets/tokens/passwords/card data logged; [M] PII (email, phone, IP) logged without policy.
- [m] String interpolation in log calls (`LogInformation($"...")`) → message templates or `[LoggerMessage]`.
- [m] Missing logs/metrics for new business flow or error branch; log-and-throw duplicates.

## Tests
- [M] New behavior without tests; bug fix without regression test.
- [M] Integration tests using EF InMemory for behavior that depends on SQL/constraints/transactions.
- [M] Tests that can't fail (no assertions, asserting mocks only, catching exceptions).
- [m] Time/random dependence (`DateTime.UtcNow`, `Random`) without `FakeTimeProvider`/seed → flaky.
- [m] Over-mocking (mocking DbContext/HttpClient) instead of real DB container or handler stubs.
- [m] Test names don't state scenario + expectation.

## Packages and build
- [M] New package with commercial license (MediatR, AutoMapper, MassTransit v9+, FluentAssertions v8+, Duende) without ADR.
- [M] Package version outside `Directory.Packages.props` (when CPM used); vulnerable package (`dotnet list package --vulnerable`).
- [m] New analyzer warnings, `#pragma warning disable` without reason, `TreatWarningsAsErrors` disabled.
- [m] Target framework changes or `LangVersion` bumps not mentioned in impl report.

## Maintainability
- [m] Method > ~40 lines or > 3 nesting levels doing several things; extract with intention-revealing names.
- [m] Dead code, commented-out code, TODO without ticket.
- [m] New abstraction with a single implementation and no test seam need (YAGNI); generic repository over DbContext.
- [m] Duplicate of an existing helper/service (Grep before flagging).

## Sources
- .NET code analysis rules https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview
- ASP.NET Core best practices https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices
- David Fowler, ASP.NET Core diagnostic scenarios (async guidance) https://github.com/davidfowl/AspNetCoreDiagnosticScenarios/blob/master/AsyncGuidance.md
- EF Core performance https://learn.microsoft.com/en-us/ef/core/performance/
- OWASP API Security Top 10 2023 https://owasp.org/API-Security/editions/2023/en/0x11-t10/
