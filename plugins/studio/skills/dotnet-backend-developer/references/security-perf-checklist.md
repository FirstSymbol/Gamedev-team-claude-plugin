# Service security and performance checklist

Run before handing off any endpoint/worker. Each item is checkable in code or config.

## Authentication and authorization (OWASP API Top 10 2023: API1, API2, API5)
- [ ] Every endpoint has explicit auth: group-level `RequireAuthorization()`; anonymous endpoints marked `AllowAnonymous` deliberately and listed in impl report.
- [ ] Object-level authorization (BOLA, API1): resource loaded by ID is checked against caller (`wallet.PlayerId == user.sub`) or a permission; integration test proves 403/404.
- [ ] Function-level (API5): admin/internal endpoints on separate group with policy; not reachable with player tokens; ideally separate host/network.
- [ ] JWT validation: issuer, audience, lifetime, signing key via OIDC metadata; `ClockSkew` ≤ 1 min; no `alg: none`; HTTPS metadata required.
- [ ] Refresh tokens: rotating, stored hashed, reuse → revoke family; access token TTL 5–15 min.
- [ ] Admin actions require fresh auth/MFA for dangerous ops (balance adjust, ban, payout) — `auth_time`/`amr` claim check.
- [ ] Mass assignment (API3): bind to request DTOs, never entities; server sets owner IDs, status, balances.

## Input and output
- [ ] Request DTO validated (lengths, ranges, enums, collection sizes); body size limits set for upload endpoints.
- [ ] No string-built SQL (`FromSqlRaw` + concatenation, Dapper string concat); interpolated APIs only.
- [ ] No `TypeNameHandling` (Newtonsoft) / `BinaryFormatter` / MessagePack Typeless on untrusted input; `MessagePackSecurity.UntrustedData` set.
- [ ] Outbound URLs from user input (avatars, webhooks) are allow-listed (SSRF, API7); no internal IP ranges.
- [ ] File uploads: size cap, content sniffing, random storage names, served from separate domain/CDN.
- [ ] Responses expose only DTO fields needed (API3 excessive data exposure); no internal flags, other players' PII.
- [ ] Errors are ProblemDetails without stack traces; `UseDeveloperExceptionPage` only in Development.

## Abuse and resource limits (API4, API6)
- [ ] Rate limits on auth, OTP, purchase, claim, search, chat (token bucket per player + per IP).
- [ ] Pagination caps (`limit` ≤ 100–200), date range caps, export jobs async.
- [ ] Business-flow abuse (API6): bonus/referral/promo endpoints have per-account + per-device + per-IP caps and velocity checks; flagged to security-engineer.
- [ ] Timeouts on every outbound call (resilience handler default total 30 s — tighten for game paths, e.g. 2–5 s).
- [ ] SignalR: message size limit, per-connection rate limit, auth required on hub.

## Secrets and data protection
- [ ] No secrets in code, appsettings, logs, exceptions, or test fixtures committed; user-secrets locally.
- [ ] PII minimized and classified; encrypted at rest (DB/disk) and in transit (TLS 1.2+); hashed passwords only via Identity (PBKDF2) or IdP.
- [ ] Data Protection keys persisted to shared store (Redis/DB/blob) when running > 1 instance (cookies/antiforgery break otherwise).
- [ ] Logs: no tokens, passwords, payment data, full receipts, emails/phones; request logging excludes `Authorization` and `access_token` query.

## Transport and headers
- [ ] HTTPS only (HSTS on public hosts); TLS terminated at proxy → `UseForwardedHeaders` with known proxies.
- [ ] CORS: explicit admin origins; credentials only with explicit origins.
- [ ] Security headers on HTML/admin BFF responses (CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`); APIs return `application/json` / `application/problem+json`.
- [ ] Webhooks: signature verified over raw body, timestamp window, event ID dedupe.

## Dependencies and config (API8, API9, API10)
- [ ] `dotnet list package --vulnerable --include-transitive` clean; NuGetAudit warnings not suppressed.
- [ ] New packages: license checked (commercial traps), maintained, from nuget.org/verified feed.
- [ ] Inventory: new endpoints appear in OpenAPI; old versions have sunset dates (API9).
- [ ] Third-party API responses validated, not trusted blindly (API10): platform receipt fields, payment callbacks.

## Performance checklist
| Check | Target / tool |
|---|---|
| No sync-over-async (`.Result`, `.Wait()`, `GetAwaiter().GetResult()`) | Grep; analyzers (VSTHRD002 in Microsoft.VisualStudio.Threading.Analyzers) |
| Queries: projection + `AsNoTracking`, no N+1, index for each filter/sort | EF logs in Development, `EXPLAIN ANALYZE` |
| Query count per request | ≤ 3–5 for hot endpoints (rule of thumb) |
| Allocation in hot paths | BenchmarkDotNet `[MemoryDiagnoser]`; avoid LINQ in tight loops, `string.Format` in logs |
| HttpClient | `IHttpClientFactory`; never `new HttpClient()` per call (socket exhaustion) |
| JSON | STJ source-gen context for hot DTOs; stream large responses (`IAsyncEnumerable<T>`) |
| Caching | HybridCache for read-mostly config/catalog; output cache for public GETs |
| Payloads | gzip/brotli `AddResponseCompression` only if proxy doesn't compress; don't compress already-compressed or secret-bearing responses over TLS (BREACH) |
| Connection pools | DB pool × replicas ≤ DB max connections; Redis multiplexer singleton |
| Background work | out of request path (queue/outbox); request ≤ p95 200 ms for wallet ops |
| Load test | k6/NBomber at 2× expected peak (e.g. event start, jackpot); watch p99, errors, DB CPU, pool waits |

- Thread-pool starvation symptoms: latency climbs, CPU low → `dotnet-counters` `threadpool.queue.length`; fix blocking calls.
- Memory growth: `dotnet-gcdump` diff; usual suspects: static caches without bounds, event handler leaks, large `MemoryCache` without `SizeLimit`.
- Measure before optimizing; record numbers (before/after) in the impl report.

## Sources
- OWASP API Security Top 10 2023 https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- OWASP ASVS 5.0 https://owasp.org/www-project-application-security-verification-standard/
- OWASP .NET Security Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/DotNet_Security_Cheat_Sheet.html
- ASP.NET Core security overview https://learn.microsoft.com/en-us/aspnet/core/security/
- ASP.NET Core performance best practices https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices
- Data Protection key storage https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/implementation/key-storage-providers
