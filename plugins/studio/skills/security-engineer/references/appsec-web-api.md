# AppSec for .NET web/API services (practitioner reference)

## OWASP Top 10:2025 → .NET checks
| ID | Category | What to check in ASP.NET Core |
|---|---|---|
| A01 | Broken Access Control (now includes SSRF) | fallback auth policy; resource-based authz on every object ID; CORS allowlist; SSRF allowlist |
| A02 | Security Misconfiguration | no DeveloperExceptionPage in prod; HSTS; headers; Swagger off/auth'd in prod; default creds |
| A03 | Software Supply Chain Failures (new) | lock files, NuGet audit, signed packages, pinned CI actions, SBOM (secure-sdlc.md) |
| A04 | Cryptographic Failures | TLS 1.2+; no MD5/SHA1 for security; AES-GCM; Data Protection API; password hashing |
| A05 | Injection | EF Core parameterization; no string-built SQL/LDAP/shell; output encoding in Razor |
| A06 | Insecure Design | threat model exists; business-logic abuse cases (bonus, refunds, race conditions) |
| A07 | Authentication Failures | JWT validation params; MFA for admins; lockout/rate-limit; breached-password check |
| A08 | Software or Data Integrity Failures | unsafe deserialization; unsigned updates/webhooks; CI artifact integrity |
| A09 | Security Logging & Alerting Failures | auth failures, authz denials, admin actions logged + alerted; no secrets/PII in logs |
| A10 | Mishandling of Exceptional Conditions (new) | fail closed; global exception handler (ProblemDetails, no stack traces); no partial state on error |
(Top 10:2025 released as 8th edition; final published early 2026 per secondary sources — verify at top10.owasp.org)

## OWASP API Security Top 10 (2023 — still current edition; verify for newer)
| ID | Risk | .NET mitigation |
|---|---|---|
| API1 | Broken Object Level Authorization (BOLA/IDOR) | load resource, then `IAuthorizationService.AuthorizeAsync(User, resource, "Owner")`; scope queries by `playerId` from token, never from body |
| API2 | Broken Authentication | standard JWT bearer/OIDC; short-lived access + rotating refresh; no custom token formats |
| API3 | Broken Object Property Level Authorization | separate request/response DTOs; no binding to entities (mass assignment); no over-returning fields |
| API4 | Unrestricted Resource Consumption | `AddRateLimiter` per user/IP; max page size; request body limits; timeouts |
| API5 | Broken Function Level Authorization | admin endpoints in separate group/host with policy; deny by default |
| API6 | Unrestricted Access to Sensitive Business Flows | bot protection on signup/bonus/claim; per-account velocity limits |
| API7 | Server-Side Request Forgery | URL allowlist, block private/link-local ranges after DNS resolve, no redirects |
| API8 | Security Misconfiguration | see A02 |
| API9 | Improper Inventory Management | OpenAPI for every version; retire old versions; no forgotten staging hosts |
| API10 | Unsafe Consumption of APIs | validate third-party responses (PSP, store APIs) as untrusted input; TLS + timeouts |

## ASVS 5.0 (May 2025): levels and chapters
- Levels are cumulative: L1 baseline (all internet-facing apps), L2 standard (apps handling PII/
  accounts — default for this studio's backends), L3 high assurance (wallet, payments, RNG/payout,
  admin/back-office of real-money platforms).
- ~350 requirements in 17 chapters: V1 Encoding & Sanitization, V2 Validation & Business Logic,
  V3 Web Frontend, V4 API & Web Service, V5 File Handling, V6 Authentication, V7 Session Mgmt,
  V8 Authorization, V9 Self-contained Tokens, V10 OAuth & OIDC, V11 Cryptography, V12 Secure
  Communication, V13 Configuration, V14 Data Protection, V15 Secure Coding & Architecture,
  V16 Security Logging & Error Handling, V17 WebRTC.
- Use: pick level per component in the threat model, turn the relevant chapters into story
  acceptance criteria; cite requirement IDs as `v5.0.0-<chapter>.<section>.<req>`.

## Authentication & authorization (ASP.NET Core)
```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o => {
        o.Authority = cfg["Auth:Authority"];           // OIDC discovery → signing keys rotate automatically
        o.Audience = "game-api";
        o.TokenValidationParameters = new() {
            ValidateIssuer = true, ValidateAudience = true, ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30),       // default is 5 min; tighten
            ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 } };   // block alg confusion
    });
builder.Services.AddAuthorizationBuilder()
    .SetFallbackPolicy(new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build()) // deny by default
    .AddPolicy("Admin", p => p.RequireRole("admin").RequireClaim("amr", "mfa"));
builder.Services.AddSingleton<IAuthorizationHandler, PlayerOwnsResourceHandler>();     // BOLA check
```
- Endpoints opt out explicitly with `[AllowAnonymous]` — Grep for it in review.
- Passwords (if self-hosted identity): ASP.NET Core Identity `PasswordHasher` (PBKDF2) or Argon2id;
  prefer an IdP (Entra ID, Auth0, Keycloak, PlayFab/UGS auth for players).
- Player auth on mobile: platform sign-in (Game Center / Play Games / Apple / Google) exchanged
  server-side for our tokens; device-ID-only "guest" accounts get limited privileges and link flows.
- Sessions for web back-office: cookies `HttpOnly; Secure; SameSite=Lax|Strict`, antiforgery tokens.

## Input validation and injection
- Validate at the edge: DTO + FluentValidation/DataAnnotations; allowlist ranges (bet amount
  `> 0 && <= tableMax`, decimal scale), enum checks, string length limits.
- EF Core: LINQ and `FromSql($"... {x}")` / `FromSqlInterpolated` are parameterized;
  `FromSqlRaw("..." + x)` is injectable. Dapper: always parameters object.
- Never pass user input to `Process.Start`, file paths (`Path.GetFullPath` + base-dir check), or
  regex without timeout (`new Regex(p, opts, TimeSpan.FromMilliseconds(100))` — ReDoS).
- File uploads: size limit, content sniffing, random server-side names, store outside web root/S3.

## Deserialization
- `BinaryFormatter` is removed from .NET 9+ (throws); never reintroduce via compatibility package.
- Newtonsoft.Json: `TypeNameHandling.None` (default) — `Auto`/`All` with untrusted input = RCE.
- System.Text.Json: safe by default; polymorphism only via `[JsonDerivedType]` allowlist.
- MessagePack-CSharp: use `MessagePackSecurity.UntrustedData` for client/network input.
- Unity client↔server DTOs: same rule both directions — server never deserializes client-chosen types.

## SSRF (A01:2025)
```csharp
static async Task<bool> IsSafeAsync(Uri u) {
    if (u.Scheme != Uri.UriSchemeHttps || !AllowedHosts.Contains(u.Host)) return false;
    foreach (var ip in await Dns.GetHostAddressesAsync(u.Host))
        if (IPAddress.IsLoopback(ip) || ip.IsIPv6LinkLocal || IsPrivateOrLinkLocal(ip)) return false; // 10/8,172.16/12,192.168/16,169.254/16
    return true;
}
```
- Disable auto-redirects (`HttpClientHandler.AllowAutoRedirect = false`) for user-influenced URLs;
  DNS rebinding: connect to the resolved IP (`SocketsHttpHandler.ConnectCallback`) not re-resolve.
- Cloud metadata (169.254.169.254) must be unreachable from app pods (IMDSv2 / network policy).

## Secrets management
| Stage | Use |
|---|---|
| Local dev | `dotnet user-secrets` (outside repo); `.env` gitignored for compose |
| CI | platform secret store + OIDC to cloud; masked; environment-scoped |
| Runtime | Azure Key Vault / AWS Secrets Manager / HashiCorp Vault via config provider; managed identity |
| Keys for crypto | KMS/Key Vault keys (non-exportable); Data Protection keys persisted + protected with KMS |
- Rotate on exposure immediately; rotation runbook per secret; assume any secret seen in a log is burned.
- Unity client contains no secrets: API keys in a build are public. Use per-user tokens.

## Hardening defaults
- `app.UseHsts()`, `UseHttpsRedirection()`; headers: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, `frame-ancestors` (CSP) for web/back-office.
- `app.UseExceptionHandler()` + `AddProblemDetails()`; never return stack traces.
- Rate limiting (`Microsoft.AspNetCore.RateLimiting`): fixed/sliding/token-bucket per user; stricter on
  login, purchase, bonus-claim endpoints. Kestrel limits: `MaxRequestBodySize`, header timeouts.
- CORS: explicit origins; never `AllowAnyOrigin` with credentials.
- Logging: redact `Authorization`, cookies, receipts, card fields; `[LogProperties]` redaction via
  `Microsoft.Extensions.Compliance.Redaction`.

## Dependency scanning (summary; pipeline detail in secure-sdlc.md)
- `dotnet list package --vulnerable --include-transitive`; NuGet audit at restore; Dependabot/Renovate.
- Unity side: UPM packages and Asset Store DLLs have no audit feed — inventory them manually,
  prefer maintained packages, check plugin native libs (Android .so/.aar) with SCA (Trivy/OSV) where possible.

## Review grep list (fast triage)
`AllowAnonymous`, `FromSqlRaw`, `ExecuteSqlRaw`, `TypeNameHandling`, `BinaryFormatter`,
`new HttpClient(`, `HttpClient.GetAsync(` with variables, `Process.Start`, `MD5`, `SHA1`,
`new Random(` (in security/RNG contexts), `DangerousAcceptAnyServerCertificateValidator`,
`ServerCertificateCustomValidationCallback`, `AllowAnyOrigin`, `password`, `secret`, `apikey`.

## Sources
- OWASP Top 10:2025 https://top10.owasp.org/2025/0x00_2025-Introduction
- OWASP API Security Top 10 2023 https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- OWASP ASVS 5.0 (GitHub) https://github.com/OWASP/ASVS/tree/master/5.0/en
- Microsoft Learn: ASP.NET Core security overview https://learn.microsoft.com/aspnet/core/security/
- Microsoft Learn: BinaryFormatter migration guide https://learn.microsoft.com/dotnet/standard/serialization/binaryformatter-migration-guide/
- OWASP Cheat Sheets: SSRF Prevention, Deserialization, .NET Security https://cheatsheetseries.owasp.org/cheatsheets/DotNet_Security_Cheat_Sheet.html
- Microsoft Learn: Rate limiting middleware https://learn.microsoft.com/aspnet/core/performance/rate-limit
