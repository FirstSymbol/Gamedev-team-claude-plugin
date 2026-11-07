# Security quick-scan (every review, ~5 minutes)

Goal: catch the high-impact, pattern-detectable issues. Anything deeper (threat model, crypto
design, payment flows, anti-cheat) → hand off to security-engineer.

## 1. Grep sweep on the diff
```bash
git diff <base>...HEAD -U0 | grep -nE \
 'FromSqlRaw|ExecuteSqlRaw|SqlQueryRaw|\+ *"(SELECT|UPDATE|DELETE|INSERT)|TypeNameHandling|BinaryFormatter|Typeless|AllowAnonymous|DisableAntiforgery|AllowAnyOrigin|dangerouslySetInnerHTML|innerHTML|eval\(|new Function|localStorage|sessionStorage|PlayerPrefs\.Set|ServerCertificateCustomValidationCallback|RequireHttpsMetadata *= *false|ValidateIssuer *= *false|ValidateAudience *= *false|ValidateLifetime *= *false|password|secret|apikey|api_key|token|BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|Random\(|System\.Random|MD5|SHA1'
```
- Each hit: confirm or dismiss with a reason. Secret-like strings: verify not committed real values (also check `appsettings*.json`, `.env`, Unity assets, test fixtures).
- Run `gitleaks detect --no-git -s <changed paths>` if available (verify tool presence).

## 2. Authentication and authorization (highest yield)
- [ ] New endpoints/hubs/gRPC methods: authorization applied (group policy or attribute); anonymous ones intended.
- [ ] Object-level check: every ID from route/query/body is checked against the caller (owner, tenant, brand) — BOLA/IDOR.
- [ ] Admin/internal functionality not reachable with player tokens; permission check server-side, not only hidden in UI.
- [ ] Token validation not weakened (issuer/audience/lifetime/signature, HTTPS metadata).
- [ ] No identity taken from client-supplied fields (`playerId` in body for "me" operations).

## 3. Injection and unsafe deserialization
- [ ] SQL built only with parameters (EF LINQ, `FromSql($"...")` interpolated API, Dapper parameters); no concatenation into raw SQL, ORDER BY whitelist for dynamic sorts.
- [ ] No Newtonsoft `TypeNameHandling` != None, `BinaryFormatter`, MessagePack Typeless, `XmlSerializer` on arbitrary types for untrusted input.
- [ ] No command execution with user input (`Process.Start` args), no path traversal (`Path.Combine(root, userInput)` without canonical check).
- [ ] Frontend: no `dangerouslySetInnerHTML`/`innerHTML` with untrusted data; URLs scheme-checked.
- [ ] SSRF: server fetches only allow-listed hosts.

## 4. Money, economy, game integrity
- [ ] State-changing ops idempotent + race-safe (unique constraint, conditional update/lock, single transaction).
- [ ] Amounts/prices/outcomes computed server-side from catalog/rules; client inputs validated (sign, range).
- [ ] RNG for outcomes: server-side, cryptographically secure or certified RNG (`RandomNumberGenerator`), never `System.Random`/`UnityEngine.Random` for money outcomes.
- [ ] Receipts/webhooks verified server-side (signature, store API), deduped by provider ID.
- [ ] Admin balance changes: permission, reason, audit, limits.

## 5. Secrets and sensitive data
- [ ] No secrets in code, config, Unity assets/ScriptableObjects, client bundles (`VITE_*` is public).
- [ ] Logs/exceptions/telemetry don't contain tokens, passwords, card data, full receipts, PII.
- [ ] Client storage: no tokens in `localStorage` (web) or plaintext `PlayerPrefs` (Unity).
- [ ] Crypto: no MD5/SHA1 for security purposes; passwords via Identity/IdP hashing; no custom crypto; TLS validation not disabled (`ServerCertificateCustomValidationCallback => true`).

## 6. Web/transport configuration
- [ ] CORS: no `AllowAnyOrigin` with credentials; explicit origins.
- [ ] CSRF protection for cookie-authenticated mutations; antiforgery not disabled without reason.
- [ ] Rate limiting on new auth/purchase/claim/search endpoints.
- [ ] Error responses don't leak internals; Developer exception page only in Development.

## 7. Dependencies
- [ ] New packages: known publisher, maintained, license OK; `dotnet list package --vulnerable --include-transitive` / `npm audit` clean.
- [ ] No packages from unknown feeds; lockfiles updated consistently.

## Escalate to security-engineer when
- Auth flows, token issuance, session handling or crypto change.
- Payments, payouts, KYC, RNG, wallet ledger design change.
- New internet-facing service/tunnel, file upload, or webhook receiver.
- Any confirmed blocker from this scan.

## Report line
Always include: `Security quick-scan: <done, N findings | no findings>; escalated: <yes/no + why>`.

## Sources
- OWASP Top 10 2021 https://owasp.org/Top10/
- OWASP API Security Top 10 2023 https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- OWASP Code Review Guide https://owasp.org/www-project-code-review-guide/
- OWASP Deserialization Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- OWASP .NET Security Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/DotNet_Security_Cheat_Sheet.html
- Microsoft: Secure coding guidelines for .NET https://learn.microsoft.com/en-us/dotnet/standard/security/secure-coding-guidelines
