# Security for admin panels

Admin panels are the highest-value target in a game/casino ecosystem: one stolen staff session can
mint currency, approve payouts or leak player PII. Treat as internet-hostile even if "internal".

## Session and token storage
| Option | Verdict |
|---|---|
| BFF (backend-for-frontend) + HttpOnly, Secure, SameSite cookie; tokens kept server-side | default |
| Tokens in memory only (SPA + OIDC code flow + PKCE, refresh via iframe/rotating refresh token) | acceptable when BFF impossible; XSS can still use the token while the page is open |
| Tokens in localStorage/sessionStorage | no: any XSS exfiltrates them |
- IETF "OAuth 2.0 for Browser-Based Applications" (RFC 10017 / BCP 212, Aug 2026) lists patterns in decreasing security with BFF first and "strongly recommended" for business/sensitive apps.
- .NET BFF options: ASP.NET Core with `AddOpenIdConnect` + cookie + YARP proxy to APIs, or Duende BFF (bundled with Duende IdentityServer licence tiers; frontend count limited per tier, e.g. Lite 2, Standard 10).
- Cookie: `__Host-` prefix, `Secure`, `HttpOnly`, `SameSite=Strict` (or `Lax` if IdP redirects need it), short idle timeout (15–30 min) + absolute lifetime (8–12 h).
- Staff IdP with MFA mandatory (phishing-resistant passkeys/WebAuthn preferred); step-up auth (`acr`/`max_age`) for high-risk actions.
- Logout: server-side session revoke + IdP end-session; "revoke all sessions" for compromised staff.

## CSRF
- Cookie-authenticated APIs are CSRF targets. Defenses (layer them):
  1. `SameSite=Strict/Lax` cookies.
  2. Require a custom header on every state-changing request (e.g. `X-CSRF: 1`); BFF rejects mutations without it (forces CORS preflight cross-origin).
  3. Or synchronizer token (ASP.NET Core antiforgery: `AddAntiforgery`, token via endpoint/cookie → header).
- Never mutate on GET. Check `Origin`/`Sec-Fetch-Site` on mutations as an extra layer.
- CORS: BFF serves the SPA same-origin → no CORS needed; if cross-origin, explicit origins only, never `*` with credentials.

## XSS
- React escapes text by default; risks: `dangerouslySetInnerHTML`, `href={userValue}` (`javascript:` URLs),
  `eval`/`new Function`, injecting into `<script>`/`style`, third-party widgets, markdown renderers.
- Player-controlled data shown to staff (nicknames, chat logs, support tickets, device names) = stored XSS against admins. Render as text; for rich text sanitize with DOMPurify and a strict allow-list.
- URL values: allow only `https:`/`mailto:` schemes; validate before rendering links.
- Enable Trusted Types via CSP (`require-trusted-types-for 'script'`; MDN: Baseline "newly available" since Feb 2026, so older staff browsers may lack it).

## Content Security Policy (served by BFF/host)
```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://cdn.example.com; connect-src 'self' https://otel.example.com;
  frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'; upgrade-insecure-requests
```
- Vite production builds need no `unsafe-eval`; avoid inline scripts (or use nonces/hashes).
- `style-src 'unsafe-inline'` often needed by CSS-in-JS/Radix; Tailwind builds can avoid it (verify: run the chosen UI libs under a Report-Only CSP without it).
- Roll out with `Content-Security-Policy-Report-Only` + `report-to` endpoint first, then enforce.
- Other headers: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`,
  `Permissions-Policy` (deny camera/mic/geolocation), HSTS; `frame-ancestors 'none'` prevents clickjacking.

## Authorization reality check
- Every permission enforced by the API; UI gating is UX only. Pen-test by calling the API with a low-privilege session.
- IDOR: changing `/players/123` to `/players/124` must be checked server-side (tenant/brand scoping too).
- Bulk/export endpoints are permissioned separately and rate-limited; exports are audited and watermarked with requester.

## Sensitive data in the browser
- Mask PII by default; reveal per field with permission + audit; never cache PII in localStorage/IndexedDB.
- TanStack Query cache is memory only — clear on logout (`queryClient.clear()`).
- No secrets in the bundle: anything in `import.meta.env.VITE_*` is public. Only public config (API base URL, OTel endpoint).
- Error tracking (Sentry etc.): scrub PII, disable session replay on admin or mask all inputs.

## Supply chain
- Lockfile committed; CI uses `npm ci`/`pnpm install --frozen-lockfile`.
- `npm audit`/`pnpm audit` + Dependabot/Renovate; review new deps (maintainers, downloads, install scripts).
- Disable lifecycle scripts for untrusted deps: pnpm 11+ blocks dependency build scripts by default (`strictDepBuilds: true`);
  allow-list via `allowBuilds` in `pnpm-workspace.yaml` (pnpm 10 `onlyBuiltDependencies` removed in v11).
- Pin GitHub Actions by SHA; Subresource Integrity for any CDN script (prefer bundling instead).
- 2025 npm worm "Shai-Hulud" (CISA alert 2025-09-23; 500+ packages) self-replicated via stolen npm creds and exfiltrated GitHub
  PATs + cloud keys — rotate npm/GitHub/cloud tokens after alerts, phishing-resistant MFA on npm/GitHub.

## Network exposure
- Admin hosted on separate domain/subdomain from player-facing sites (cookie isolation).
- Restrict by IdP + network (VPN/ZTNA/IP allow-list) for production back-office; WAF in front.
- Separate admin API from player API (different host/route group, different auth audience).

## Checklist before shipping an admin screen
- [ ] No token in Web Storage; session cookie flags correct.
- [ ] Mutations require CSRF header/token; no GET side effects.
- [ ] No `dangerouslySetInnerHTML` with unsanitized data; user URLs scheme-checked.
- [ ] CSP and security headers present (check with browser devtools / securityheaders).
- [ ] Low-privilege role E2E test proves API denies the action (not just hidden button).
- [ ] PII masked; reveal audited; cache cleared on logout.
- [ ] New dependencies reviewed; audit clean.

## Sources
- OWASP Cross-Site Request Forgery Prevention Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Cross Site Scripting Prevention Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- OWASP Content Security Policy Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
- OWASP Session Management Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- IETF OAuth 2.0 for Browser-Based Applications (RFC 10017) https://datatracker.ietf.org/doc/draft-ietf-oauth-browser-based-apps/
- CISA: Widespread supply chain compromise impacting npm ecosystem (2025-09-23) https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem
- MDN Trusted Types API https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API
- pnpm build settings (allowBuilds, strictDepBuilds) https://pnpm.io/settings/build
- Duende BFF https://duendesoftware.com/products/bff
- React docs: dangerouslySetInnerHTML https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html
- MDN Content Security Policy https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
