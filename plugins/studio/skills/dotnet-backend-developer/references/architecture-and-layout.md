# Service architecture and project layout

## Pick the style
| Style | Use when | Cost |
|---|---|---|
| Vertical slices (feature folders, one handler per use case) | default for game/admin APIs; many small use cases | some duplication across slices (accept it) |
| Clean/Onion (Domain, Application, Infrastructure, Api projects) | rich domain with invariants shared by many use cases (wallet/ledger, tournament rules), long-lived core | more projects, mapping, indirection |
| Modular monolith (modules = bounded contexts, each sliced inside) | several domains (identity, wallet, catalog, liveops, admin) in one deployable | needs enforced module boundaries |
| Microservices | independent scaling/deploy/team ownership proven necessary | network, consistency, ops cost; ADR required |
- Default for a casino/F2P ecosystem: modular monolith with vertical slices; extract a service
  (e.g. tunnel/gateway, game-round engine) only with a scaling/isolation/compliance reason.
- Mix allowed: vertical slices for features + a small pure `Domain` for the ledger/rules.

## Layout: modular monolith with slices
```
src/
  Game.Api/                     host: Program.cs, auth, middleware, OpenAPI, module registration
  Modules/
    Wallet/
      Game.Wallet/              module (internal by default)
        Domain/                 Wallet, LedgerEntry, Money (no EF/ASP.NET refs)
        Features/
          Debit/ DebitEndpoint.cs DebitHandler.cs DebitRequest.cs DebitValidator.cs
          GetBalance/ ...
        Persistence/            WalletDbContext (own schema "wallet"), configurations, migrations
        WalletModule.cs         public: AddWalletModule(), MapWalletEndpoints(), public contracts
      Game.Wallet.Contracts/    integration events + public DTOs other modules may use
    LiveOps/ ...
  Shared/Game.Contracts/        netstandard2.1 DTOs shared with Unity (see stack-dotnet unity-interop)
  Game.ServiceDefaults/         Aspire defaults: OTel, health, resilience
  Game.AppHost/                 Aspire local orchestration
tests/
  Game.Wallet.Tests/            unit (domain + handlers with fakes)
  Game.Api.IntegrationTests/    WebApplicationFactory + Testcontainers
  Game.ArchitectureTests/       NetArchTest rules
Directory.Build.props  Directory.Packages.props  global.json  .editorconfig
```
- One DbContext per module (own schema); modules never query another module's tables — call its
  public API (in-process interface) or consume its integration events.
- Module internals `internal`; expose only `XxxModule` + Contracts. Enforce with architecture tests.
- Solution file: `.slnx` (new XML format, supported by .NET 9.0.200+ SDK / VS 2022 17.13+) is fine for new solutions (verify team tooling).

## Slice anatomy (no mediator library required)
```csharp
internal static class DebitEndpoint {
    public static void Map(RouteGroupBuilder g) => g.MapPost("/{walletId:guid}/debits", Handle);
    static async Task<IResult> Handle(Guid walletId, DebitRequest req,
        [FromHeader(Name = "Idempotency-Key")] Guid key, DebitHandler h, ClaimsPrincipal user, CancellationToken ct)
    {
        var result = await h.Handle(new(walletId, user.GetPlayerId(), req.Amount, req.Reason, key), ct);
        return result.IsSuccess ? TypedResults.Ok(result.Value) : result.Error.ToProblem();
    }
}
internal sealed class DebitHandler(WalletDbContext db, TimeProvider clock) { /* domain + persistence */ }
```
- Register handlers explicitly (`services.AddScoped<DebitHandler>()`) or by assembly scan (Scrutor).
- MediatR is commercial since 2025: don't add it to new projects; if present, keep the pinned OSS version or plan removal (ADR).
- Cross-cutting concerns: endpoint filters (validation, audit), decorators (Scrutor `Decorate`) or
  middleware — not pipeline behaviors from a paid library.
- Mapping: hand-written `ToDto()` extension methods or Mapperly (source generator, Apache-2.0);
  AutoMapper is commercial since 2025 and hides mapping bugs.

## Domain modeling rules
- Entities enforce invariants in methods (`wallet.Debit(amount)` returns Result), not public setters.
- Value objects as `readonly record struct` (`Money(long Minor, Currency Currency)`); EF 10 complex types map them.
- Strongly typed IDs (`readonly record struct PlayerId(Guid Value)`) for money-adjacent code; value converters in EF.
- Result pattern for expected failures; exceptions for programmer errors/infra.
- Domain events raised in entities, dispatched after `SaveChanges` (in-process) or written to outbox (cross-module/service).

## DI and composition
- Lifetimes: DbContext scoped; HttpClients typed via factory; stateless services singleton; no
  `BuildServiceProvider()` inside registration (duplicate singletons).
- Keyed services (`AddKeyedSingleton<IPaymentProvider, AppStoreProvider>("appstore")`) for strategy-by-key.
- `IHostedService` registration order = start order; use `IHostedLifecycleService` for start/stop hooks.
- Options per module (`Wallet:` section); validated on start.

## Project hygiene
- `Directory.Build.props`: `TargetFramework net10.0`, `Nullable enable`, `ImplicitUsings enable`,
  `TreatWarningsAsErrors true` (CI), `AnalysisLevel latest-recommended`, `InvariantGlobalization` per app needs.
- Central Package Management: `Directory.Packages.props` with `ManagePackageVersionsCentrally=true`;
  enable `CentralPackageTransitivePinningEnabled` for vulnerable transitive fixes.
- `dotnet list package --vulnerable --include-transitive` in CI; NuGet audit warnings on (`NuGetAudit` default on since .NET 8 SDK).
- `.editorconfig` committed; `dotnet format --verify-no-changes` in CI.

## Architecture tests (NetArchTest.Rules)
```csharp
Types.InAssembly(typeof(Wallet).Assembly).That().ResideInNamespace("Game.Wallet.Domain")
    .ShouldNot().HaveDependencyOnAny("Microsoft.EntityFrameworkCore", "Microsoft.AspNetCore")
    .GetResult().IsSuccessful.ShouldBeTrue();
```
- Rules worth having: Domain has no infra deps; modules don't reference other modules' internals;
  endpoints don't reference DbContext of another module; Contracts project has no dependencies.

## When to split a service out
- Different scaling profile (e.g. game-round engine at 10x request rate of admin).
- Different security/compliance zone (payment, RNG certification boundary, tunnel exposed to internet).
- Different release cadence/team. Otherwise keep in the monolith; extraction is easier from clean module boundaries.

## Sources
- Jimmy Bogard, Vertical Slice Architecture https://www.jimmybogard.com/vertical-slice-architecture/
- Milan Jovanovic, Vertical Slice Architecture https://www.milanjovanovic.tech/blog/vertical-slice-architecture
- Microsoft, Common web application architectures https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures
- Central Package Management https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management
- NetArchTest https://github.com/BenMorris/NetArchTest
- Mapperly https://mapperly.riok.app/
