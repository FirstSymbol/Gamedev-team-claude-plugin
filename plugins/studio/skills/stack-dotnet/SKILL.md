---
name: stack-dotnet
description: Shared .NET 10/C# 14 baseline - ASP.NET Core, EF Core, SignalR/gRPC/queues, testing, observability, Unity code sharing. Load for any .NET work.
---
# .NET stack (shared knowledge)
Mission: one verified, current .NET baseline for every agent that writes, reviews or designs .NET code.

## Version baseline (checked 2026-11-07)
| Item | State | Rule |
|---|---|---|
| .NET 10 | LTS, GA 2025-11-11, support to 2028-11-14 | default target `net10.0` |
| .NET 11 | STS; RC3 as of 2026-11-07, launch at .NET Conf 2026-11-10; STS = 24 months (since .NET 9) | adopt only for a needed feature (verify: GA build on dotnet.microsoft.com after 2026-11-10) |
| .NET 8 LTS, .NET 9 STS | both end support 2026-11-10 | upgrade to 10; log a risk if still present |
| C# 14 (.NET 10) | `extension(T x) { }` blocks (props, static members, operators), `field` keyword, `a?.B = x`, implicit Span conversions, `nameof(List<>)`, partial ctors/events | use freely on net10.0 |
| C# 15 (.NET 11) | `union Pet(Cat, Dog)`, `closed` hierarchies (exhaustive switch), extension indexers, `[with(capacity: n), ..xs]`, labeled `break`/`continue` | only on net11.0 projects |
| ASP.NET Core 10 | `AddValidation()` for minimal APIs, OpenAPI 3.1 default (+YAML), SSE `TypedResults.ServerSentEvents`, Identity passkeys, cookie auth returns 401/403 on API endpoints | see aspnetcore-apis |
| EF Core 10 | LTS to 2028-11-10; complex types (optional, struct, `ToJson()`), named query filters, `LeftJoin`, `ExecuteUpdateAsync` with plain lambda | see data-efcore |
| EF Core 11 | SQL Server compat level default 160; `Migrate()` throws if no migrations; split-query concurrency now throws | read breaking changes before upgrade |
| Aspire | 13.x (renamed from ".NET Aspire", aspire.dev), needs .NET 10 SDK | local orchestration default |
| Tests | xUnit v3 on Microsoft.Testing.Platform; .NET 10 SDK runs MTP natively (runner in `global.json`) | see testing-dotnet |
| Containers | `mcr.microsoft.com/dotnet/aspnet:10.0` = Ubuntu 24.04; `-noble-chiseled` distroless; no Debian images for 10 | see observability-and-ops |
| Unity | Unity 6.x: Mono/IL2CPP, .NET Standard 2.1, C# 9. 6.7 LTS = last Mono; Unity 7 = CoreCLR + .NET 10/C# 14 (no release date); public experimental CoreCLR builds stay netstandard2.1/C# 9 (Unity, June 2026) | shared libs stay `netstandard2.1` |
| Licensing | MediatR + AutoMapper (2025), MassTransit v9 (Massient), FluentAssertions v8 (Xceed), NBomber (orgs), Duende (≥ $1M revenue): commercial | check license before adding; prefer OSS or pin last OSS major |

## Rules that always apply
- Read `global.json`, `Directory.Build.props`, `Directory.Packages.props` (Central Package
  Management) and `.team/reports/scan-dotnet.md` before changing anything; follow existing conventions.
- `<Nullable>enable</Nullable>`, analyzers on (`<AnalysisLevel>latest-recommended</AnalysisLevel>`),
  warnings as errors in CI. No new warnings.
- Async end to end: no `.Result`/`.Wait()`/`async void`; pass `CancellationToken` to every I/O call.
- DI lifetimes: never capture scoped (DbContext) in singletons; `ValidateScopes`/`ValidateOnBuild` on in Development.
- Time via `TimeProvider`; IDs via `Guid.CreateVersion7()` when sortable IDs help indexes.
- Money/currency: `decimal` or `long` minor units; never `double`/`float`.
- Outbound HTTP via `IHttpClientFactory` + `AddStandardResilienceHandler()` (Microsoft.Extensions.Http.Resilience).
- Config via Options pattern + `ValidateOnStart()`; secrets never in repo or `appsettings*.json`.
- Logs: message templates (`{PlayerId}`), no interpolation, no PII/tokens/card data.
- Integration tests run against the real engine (Testcontainers), never EF InMemory for behavior.
- Public contracts (HTTP, gRPC, messages, shared DTOs) change additively; breaking change → ADR.
- New package: license, maintenance (last release < 12 months), AOT/trim support, and
  `netstandard2.1` availability if Unity consumes it.

## References (read on demand)
- references/aspnetcore-apis.md — building/changing HTTP endpoints: minimal APIs vs controllers,
  validation, ProblemDetails, versioning, JWT/OIDC, rate limiting, output caching, health, OpenAPI.
- references/data-efcore.md — DbContext, migrations, query performance, concurrency, transactions,
  Dapper, PostgreSQL/Npgsql, Redis/HybridCache.
- references/realtime-and-messaging.md — SignalR (scale-out), gRPC, BackgroundService, queues
  (RabbitMQ/Kafka/MassTransit/Wolverine), outbox, idempotent consumers.
- references/testing-dotnet.md — writing or reviewing tests: xUnit v3, WebApplicationFactory,
  Testcontainers, Verify, mocking, coverage, mutation testing.
- references/observability-and-ops.md — OpenTelemetry, logging, metrics, Aspire, options/secrets,
  container images, Native AOT/trimming, GC and diagnostics.
- references/unity-interop.md — code or contracts shared with a Unity client: netstandard2.1 libs,
  IL2CPP limits, JSON/MessagePack/MemoryPack compatibility, HTTP/gRPC/SignalR from Unity, versioning.

## Sources
- .NET 8/9 end of support, STS = 24 months https://devblogs.microsoft.com/dotnet/dotnet-8-9-end-of-support/
- .NET Conf 2026 (.NET 11 launch, Nov 10-12) https://devblogs.microsoft.com/dotnet/dotnet-conf-2026/
