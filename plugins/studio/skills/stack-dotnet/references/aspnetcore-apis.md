# ASP.NET Core 10 HTTP APIs

## Minimal APIs vs controllers
| Choose | When |
|---|---|
| Minimal APIs (default for new services) | new HTTP/JSON services, vertical slices, Native AOT, lowest overhead |
| Controllers (`[ApiController]`) | existing MVC codebase, heavy use of MVC filters/model binders, conventional routing, Razor views |
| Mixed | allowed in one app; don't mix styles inside one feature |
- Microsoft's .NET 11 investment focus is minimal APIs, SignalR, Blazor (aspnetcore roadmap 2026).
- Organize with route groups; one static `Map<Feature>Endpoints` per slice, not one giant `Program.cs`.

```csharp
var wallets = app.MapGroup("/api/v1/wallets")
    .RequireAuthorization()
    .RequireRateLimiting("per-player")
    .WithTags("Wallets");

wallets.MapPost("/{walletId:guid}/debits", async Task<Results<Ok<DebitResult>, NotFound, ProblemHttpResult>> (
        Guid walletId, DebitRequest req, [FromHeader(Name = "Idempotency-Key")] string idemKey,
        DebitHandler handler, CancellationToken ct) =>
    {
        var r = await handler.Handle(walletId, req, idemKey, ct);
        return r.Match<Results<Ok<DebitResult>, NotFound, ProblemHttpResult>>(
            ok => TypedResults.Ok(ok),
            notFound => TypedResults.NotFound(),
            err => TypedResults.Problem(err.Detail, statusCode: err.Status, title: err.Code));
    })
    .WithName("DebitWallet");
```
- Use `TypedResults` + `Results<...>` unions: compile-time checked and auto-documented in OpenAPI.
- Endpoint filters (`AddEndpointFilter`) = cross-cutting per group (tenant checks, audit), not business logic.
- Bind complex inputs with `[AsParameters]` records; keep handlers in injectable classes for unit tests.

## Validation
| Option | Notes |
|---|---|
| Built-in (.NET 10) `builder.Services.AddValidation()` | DataAnnotations + `IValidatableObject` on query/header/body; 400 with problem details; source-generated; discovers types only in the assembly where called; opt out `.DisableValidation()`; namespace `Microsoft.Extensions.Validation` |
| FluentValidation (Apache-2.0) | complex/conditional rules, async rules; run via endpoint filter; don't use the deprecated auto-validation package |
| Domain invariants | always also in the domain/handler; request validation is not a security boundary for business rules |
- Validate: sizes (max string/collection lengths), ranges, enums defined (`Enum.IsDefined`), formats.
- Limit body size: `KestrelServerOptions.Limits.MaxRequestBodySize` (default ~28.6 MB) or `[RequestSizeLimit]`.

## Errors: ProblemDetails (RFC 9457, obsoletes 7807)
```csharp
builder.Services.AddProblemDetails(o => o.CustomizeProblemDetails = ctx =>
    ctx.ProblemDetails.Extensions["traceId"] = Activity.Current?.Id ?? ctx.HttpContext.TraceIdentifier);
builder.Services.AddExceptionHandler<DomainExceptionHandler>(); // IExceptionHandler, ordered
app.UseExceptionHandler();
app.UseStatusCodePages();
```
- Return expected failures as values (Result type) → `TypedResults.Problem`; reserve exceptions for bugs/infra.
- Stable machine-readable `type`/`code` per error (e.g. `wallet.insufficient_funds`); clients branch on code, not text.
- Never leak stack traces/SQL in production; `DeveloperExceptionPage` only in Development.
- .NET 10 breaking: exceptions handled by an `IExceptionHandler` returning `true` are no longer logged
  by the middleware; log them yourself or set `SuppressDiagnosticsCallback = _ => false`.

## Versioning
- Package `Asp.Versioning.Http` (minimal) / `Asp.Versioning.Mvc` (controllers); report versions via
  `ReportApiVersions = true`; deprecate with `api-deprecated-versions` + `Sunset` header.
- Scheme: URL segment `/api/v1/` for public/game-client APIs (cache/CDN/log friendly); header for internal.
- Game clients can't all update at once: support N and N-1 (often N-2) concurrently; add a
  `/client-config` endpoint returning `minSupportedVersion` + force-update flag.
- Breaking = removing/renaming fields, changing types/semantics, new required input, new error codes
  that old clients can't handle. Additive optional fields are non-breaking.

## Authentication and authorization
```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o => {
        o.Authority = cfg["Auth:Authority"];     // OIDC discovery + key rotation
        o.Audience = "game-api";
        o.MapInboundClaims = false;              // keep "sub", "role" as issued
        o.TokenValidationParameters.ClockSkew = TimeSpan.FromSeconds(30); // default 5 min
    });
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("ops.balance.adjust", p => p.RequireClaim("perm", "balance:adjust"));
```
| Identity provider | Use |
|---|---|
| Keycloak / OpenIddict (OSS) | self-hosted OIDC for players + staff |
| Entra ID / Entra External ID | staff SSO (admin panel), enterprise |
| Duende IdentityServer | full-featured; free Community Edition only if < $1M annual revenue (and < $3M capital), self-hosted, applied for before prod; otherwise paid license |
| `MapIdentityApi<TUser>()` | simple first-party apps only; opaque proprietary tokens, no federation |
- Game client flow: guest/device ID or platform auth (Google Play Games, Game Center, Steam ticket)
  verified server-side → issue own access JWT (5–15 min) + rotating refresh token (stored hashed, reuse detection).
- Admin panel: OIDC authorization code + PKCE through a BFF (HttpOnly cookie); see frontend-developer.
- Authorize by policy/permission, not role strings scattered in code; resource checks (owner, tenant)
  in handlers via `IAuthorizationService` — IDs from the token, never from the request body.
- .NET 10: cookie auth returns 401/403 (no redirect) for endpoints with `IApiEndpointMetadata`.
- Identity passkeys (WebAuthn) available in .NET 10 Identity for staff sign-in.

## Rate limiting (`Microsoft.AspNetCore.RateLimiting`, built in)
```csharp
builder.Services.AddRateLimiter(o => {
    o.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    o.AddPolicy("per-player", ctx => RateLimitPartition.GetTokenBucketLimiter(
        ctx.User.FindFirst("sub")?.Value ?? ctx.Connection.RemoteIpAddress?.ToString() ?? "anon",
        _ => new TokenBucketRateLimiterOptions { TokenLimit = 20, TokensPerPeriod = 10,
             ReplenishmentPeriod = TimeSpan.FromSeconds(1), QueueLimit = 0 }));
});
app.UseRateLimiter(); // after UseRouting/UseAuthentication when partitioning by user
```
- Algorithms: fixed window, sliding window, token bucket (bursty clients), concurrency (expensive ops).
- State is per instance; multi-instance global limits need gateway (YARP/NGINX/cloud WAF) or Redis-backed limiter.
- Behind a proxy: `UseForwardedHeaders` with `KnownProxies`/`KnownNetworks` first, or IP partitions collapse to the proxy IP.
- Set `Retry-After` in `OnRejected`. Stricter limits on auth, purchase, OTP, search endpoints.

## Caching
| Layer | API | Rule |
|---|---|---|
| Output cache | `AddOutputCache()`, `.CacheOutput(p => p.Expire(...).Tag("catalog"))`, `EvictByTagAsync` | public, non-personalized GET (catalog, config); Redis store `AddStackExchangeRedisOutputCache` for multi-instance |
| Data cache | `HybridCache` (L1 memory + L2 distributed, stampede protection) | read-mostly data; see data-efcore |
| HTTP caching | `ETag`/`Cache-Control` | static config to CDN; version in URL |
- Default output-cache policy skips authenticated requests and responses with cookies; keep it that way
  for player data. Never cache balances or anything used for authorization decisions.

## Health checks
```csharp
builder.Services.AddHealthChecks()
    .AddNpgSql(connString, tags: ["ready"])           // AspNetCore.HealthChecks.NpgSql
    .AddRedis(redisConn, tags: ["ready"]);
app.MapHealthChecks("/health/live", new() { Predicate = _ => false }); // process up
app.MapHealthChecks("/health/ready", new() { Predicate = r => r.Tags.Contains("ready") });
```
- Liveness must not check dependencies (a DB outage would restart every pod). Readiness does.
- Don't expose detailed health JSON publicly; restrict by network/`RequireHost`/auth.

## OpenAPI (built-in `Microsoft.AspNetCore.OpenApi`)
- `builder.Services.AddOpenApi(); app.MapOpenApi();` → `/openapi/v1.json`; 3.1 default in .NET 10;
  YAML via `app.MapOpenApi("/openapi/{documentName}.yaml")`.
- Swashbuckle is no longer in templates (since .NET 9); UI via `Scalar.AspNetCore` or Swagger UI static, Development only.
- XML doc comments flow into the document with `<GenerateDocumentationFile>true</GenerateDocumentationFile>`.
- Build-time document: `Microsoft.Extensions.ApiDescription.Server` → commit/diff the spec in CI to catch breaking changes (e.g. `oasdiff`).
- Add security schemes with document transformers; .NET 10 uses Microsoft.OpenApi 2.x (`OpenApiAny` → `JsonNode`): old transformers need updates.
- Generate clients: TypeScript (`openapi-typescript`, Orval) for admin panel; Kiota/NSwag for .NET.

## Other pipeline essentials
- Order: ForwardedHeaders → ExceptionHandler → HSTS/HTTPS → Routing → CORS → Authentication →
  Authorization → RateLimiter → OutputCache → endpoints. Docs constraints: CORS before auth and caching;
  RateLimiter after Routing for endpoint policies (template puts it right after Routing; keep it after auth when partitioning by user).
- CORS: explicit origins for the admin panel; never `AllowAnyOrigin` with credentials.
- Timeouts: `AddRequestTimeouts()` + `.WithRequestTimeout(...)`; pass `HttpContext.RequestAborted` downstream.
- JSON: `ConfigureHttpJsonOptions` (web defaults: camelCase, case-insensitive read); enums as strings
  via `JsonStringEnumConverter` consistently across all clients; source-gen `JsonSerializerContext` for AOT.
- Antiforgery: `AddAntiforgery()`; minimal APIs validate it automatically for form-bound endpoints; cookie-auth JSON APIs need SameSite + CSRF token/custom header.
- SSE (.NET 10) `TypedResults.ServerSentEvents(IAsyncEnumerable<SseItem<T>>)` for one-way live feeds (admin dashboards).

## Sources
- What's new in ASP.NET Core 10 https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0
- Minimal APIs overview https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/overview
- Handle errors in ASP.NET Core APIs https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api
- Rate limiting middleware https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit
- Output caching middleware https://learn.microsoft.com/en-us/aspnet/core/performance/caching/output
- Health checks https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks
- ASP.NET API Versioning https://github.com/dotnet/aspnet-api-versioning
- RFC 9457 Problem Details for HTTP APIs https://www.rfc-editor.org/rfc/rfc9457
- ASP.NET Core middleware order https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/
- Duende Community Edition terms https://duendesoftware.com/products/communityedition
