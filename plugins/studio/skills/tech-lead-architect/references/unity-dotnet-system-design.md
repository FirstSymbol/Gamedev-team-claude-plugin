# Unity client + ASP.NET Core backend + admin: reference system design
Code-level interop (netstandard2.1 libs, IL2CPP limits, serializer compatibility, HTTP/gRPC/SignalR
from Unity) → `studio:stack-dotnet` (unity-interop). This file is the system view.

## Reference container view
| Container | Tech (default) | Responsibility |
|---|---|---|
| Game client | Unity 6.3 LTS, C# 9, `Game.Contracts` (netstandard2.1) | gameplay, UI, local cache/save, net client, telemetry batching |
| CDN / object storage | CloudFront / Azure Front Door / CCD | Addressables bundles + catalogs, config snapshots, store art |
| Edge | LB + WAF, rate limits, TLS | DDoS/bot filtering, routing by path/version |
| Game API | ASP.NET Core 10 modular monolith | bootstrap, auth, profile, wallet/ledger, store/IAP, config, social, leaderboards |
| Realtime | SignalR (Redis backplane) or dedicated servers | presence, chat, live events, multiplayer sessions (`studio:domain-multiplayer`) |
| Workers | `BackgroundService` + queue consumers | receipt webhooks, rewards fan-out, reconciliation, scheduled live-ops |
| Admin panel | SPA (frontend-developer) + Admin API | CS tools, grants, bans, config/live-ops editor, reports |
| Data | PostgreSQL (primary + replica), Redis, object storage | ledger, players; cache/leaderboards; archives |
| Observability | OpenTelemetry → APM; crash reporter | traces/metrics/logs; client crashes, ANRs |
| Analytics | event ingest → warehouse (or vendor SDK) | product analytics, A/B reads (data-analyst) |
| External | Apple/Google/Steam/console auth & stores, APNs/FCM, attribution, ad networks, payment providers | |

## Repo and contracts sharing
| Option | Pros | Cons | Use when |
|---|---|---|---|
| Shared `Game.Contracts` netstandard2.1 project → Unity local UPM package (`file:`) or DLL | one source of truth, compile-time safety | Unity C# 9 / API limits constrain server code style | same org, monorepo or package feed |
| OpenAPI-generated client (NSwag/Kiota/OpenAPI Generator) | language-agnostic, versioned spec | generator output may need IL2CPP tweaks; less type sharing | multiple clients (web admin, partners) |
| Protobuf/gRPC or MessagePack schemas | compact, schema evolution rules built in | tooling in Unity, gRPC-Web/HTTP2 constraints | bandwidth-sensitive or realtime |
- Contracts project rules: DTOs, enums, error codes, pure validation; no server deps, no Unity
  refs; nullable annotations; `[DataMember]`/serializer attributes only; changes reviewed as public API.
- Shared pure rules (e.g., reward formula preview) may live in a `Game.Rules` netstandard2.1 lib, but
  the server's result is authoritative; client copy is for prediction/display only.
- Wire conventions: camelCase JSON, enums as strings, timestamps ISO-8601 UTC, IDs as strings
  (GUID v7 or ULID), money/currency as `long` minor units, explicit `schemaVersion` on persisted blobs.

## Startup flow (every session)
```mermaid
sequenceDiagram
  participant C as Unity client
  participant CDN
  participant API as Game API
  C->>API: GET /v1/bootstrap (X-Client-Version, X-Platform)
  API-->>C: minSupported, recommended, maintenance, configVersion, cdnBase, featureFlags
  alt version < minSupported
    C->>C: blocking update screen (store link / Play in-app update)
  end
  C->>API: POST /v1/auth/{guest|apple|google|steam} (+ refresh token if any)
  API-->>C: accessToken (JWT 15 min), refreshToken (rotating)
  C->>CDN: GET config/{configVersion}.json (ETag) + Addressables catalog for this app version
  C->>API: GET /v1/players/me (profile, wallet, inventory snapshot)
  C->>C: enter game; telemetry session_start
```

## Auth flows
| Flow | Client | Server validation | Notes |
|---|---|---|---|
| Guest/device | random install ID in secure storage (iOS Keychain / Android Keystore-backed) | create account; bind install ID hash | prompt to link before first purchase or after N days |
| Sign in with Apple | identity token (JWT) | verify signature via Apple JWKS, `aud` = bundle ID, nonce | Guideline 4.8: apps using third-party/social login for the primary account must also offer an equivalent privacy-preserving login (name+email only, private email, no ad tracking); Sign in with Apple qualifies but is not named |
| Google Play Games Services v2 | `GamesSignInClient.requestServerSideAccess(webClientId, forceRefreshToken)` → server auth code | exchange at `https://oauth2.googleapis.com/token` (web OAuth client), then `Players.get('me')` for player ID | use the game-server (web) client ID, not the Android one |
| Steam | `GetAuthTicketForWebApi(identity)` → hex ticket | `ISteamUserAuth/AuthenticateUserTicket` with publisher key and same identity, server-side only | never `GetAuthSessionTicket` for Web API |
| Consoles | platform SDK token | platform server API (NDA docs) | see `studio:domain-pc-console` |
| Email/OIDC (IT products) | OIDC Authorization Code + PKCE (system browser) | standard OIDC | never embedded webview for credentials |
| Admin | OIDC (Entra ID / Keycloak / Auth0) + MFA | separate issuer/audience, RBAC policies | admin tokens never valid on player API |
- Tokens: access JWT 5-15 min (claims: sub, platform, roles, client version optional); refresh
  token opaque, 30-90 days, stored hashed, rotated on use, reuse detection revokes the family.
- Account linking: one player account ↔ many identities. Conflict (identity already linked
  elsewhere) → explicit choose-account UI; never silently merge wallets; log and support-tooling.
- Sensitive ops (purchases, wallet, rewards claims): device/app attestation (Play Integrity standard
  requests with `requestHash`, default 10,000 req/day per app, raise via Play Console; Apple App Attest
  `DCAppAttestService` attestKey/generateAssertion) as a risk signal, not sole gate. Threat model → security-engineer.

## Request conventions
- Headers: `Authorization: Bearer`, `X-Client-Version` (semver), `X-Platform`, `X-Build`,
  `traceparent` (W3C), `Idempotency-Key` on every mutation with value (purchases, claims, spins).
- Server middleware order: request ID/tracing → version gate → rate limit → authN → authZ →
  endpoint; errors as ProblemDetails with stable `code` (`client_outdated`, `insufficient_funds`).
- Client net layer: one `ApiClient` with timeouts (5-10 s), retries only for idempotent/keyed
  requests (exponential backoff + jitter, max 2-3), token refresh single-flight, offline queue for
  non-critical writes, main-thread marshaling for results (see stack-unity async rules).

## Remote config and live-ops config
| Option | Fit | Watch |
|---|---|---|
| UGS Remote Config + Game Overrides | Unity-native, targeting/A-B built in | vendor coupling; economy logic still server-side |
| Firebase Remote Config | mobile, free tier, A/B with Analytics | client-evaluated; not for secrets/economy authority |
| Custom config service (ASP.NET Core + admin editor) | casino/economy-heavy, compliance, full audit | build the editor, validation, rollout tooling |
- Custom design: author in admin → validate against JSON Schema + business rules (economy
  bounds) → immutable versioned snapshot → publish to CDN (content-hashed key) → bootstrap
  returns `configVersion`; client fetches with ETag, caches last good, falls back to baked defaults.
- Refresh on start, on resume after > 10-15 min, and on server push (`config_changed`).
- Targeting: evaluate economy-affecting segments server-side; UI-only toggles may be client-side.
- A/B assignment: deterministic `hash(playerId + experimentKey) % 100` buckets, persisted,
  logged as an exposure event when the variant is actually shown.
- Each flag/config entry: owner, default, `minClientVersion`, expiry date; kill switches for
  store, each live event, each slot/game mode. Two-person approval + audit for prod economy changes.

## Telemetry
- Operational: OpenTelemetry on server (traces, RED metrics, logs with trace IDs); client crash/ANR
  reporting (Unity Cloud Diagnostics, Sentry, Backtrace or Crashlytics — pick one); client perf
  samples (fps, load times, memory) sampled ~1-10% of sessions.
- Product analytics: event catalog (name, version, owner, properties) owned with data-analyst;
  client batches (every 30-60 s or 50 events, flush on pause/quit), gzip, retries with on-disk queue.
- Authoritative facts (purchase, currency grant/spend, match result) are emitted server-side —
  revenue and economy dashboards never trust client events.
- Common properties: `event_id` (dedupe), `player_id` (pseudonymous), `session_id`,
  `client_version`, `platform`, `country`, `ts_utc`, `config_version`, experiment variants.
- Consent first: no tracking/attribution SDK init before consent (GDPR/ATT); no PII in events → compliance-advisor.

## Versioning and backward compatibility
- Old clients live for months (store rollout, users not updating). Declare a support window,
  e.g., current + previous 2 minor versions or 90 days, enforced by `minSupported`.
- API rules: additive only — new optional fields, new endpoints, new enum values tolerated
  (client maps unknown → `Unknown`); never rename/retype/remove a field in place. Both Newtonsoft
  and System.Text.Json ignore unknown members by default; keep it so.
- Breaking change → new versioned route (`/v2/...`, Asp.Versioning) or new message type; old version
  kept until `minSupported` passes it; ADR required.
- Expand → migrate → contract (parallel change) for API, DB schema and events: deploy server
  that accepts both, ship clients, raise `minSupported`, then remove the old path.
- DB migrations backward-compatible with the previous server build during rolling deploys.
- Content: Addressables remote catalogs are built per player build (code + content must match);
  key remote content by app version; never push content that needs newer code to older clients.
- Config entries carry `minClientVersion`; server filters per caller version.
- Save/profile blobs: `schemaVersion` + forward migrations on server (unity-developer handles local saves).

## Forced and soft updates
- Bootstrap response: `minSupported`, `recommended`, `storeUrl` per platform, `maintenance`
  {active, eta, message, allowList}. Below min → blocking screen; below recommended → dismissible prompt.
- Defense in depth: version-gate middleware answers HTTP 426 + ProblemDetails `client_outdated` to
  any call from a too-old client (handles clients that skipped bootstrap).
- Android: Play In-App Updates (Unity plugin `AppUpdateManager`; immediate vs flexible; priority 0-5
  via Play Developer API). iOS: no in-app update API — open the App Store page. Steam: client
  auto-updates; still gate by build ID. Consoles: platform patch rules apply (verify: Sony TRC / Xbox XR / Nintendo Lotcheck under NDA).
- Never raise `minSupported` to a version not yet live at 100% on every store (Apple phased release
  spans 7 days; Play staged rollout %). Raise in steps and watch the blocked-session metric.
- Maintenance mode is server-driven; QA allow-list by player ID to verify before reopening.

## Admin panel / back-office
- Separate SPA + Admin API (same backend, separate auth scheme/policies, or separate service if
  compliance requires isolation). Roles: viewer, CS agent, live-ops, economy admin, super admin.
- Every write audited: who, when, what, before/after, reason/ticket; immutable audit table.
- Currency/item grants above threshold need four-eyes approval; bulk ops dry-run first.
- PII views masked by default and access-logged; heavy reports on read replica / warehouse.

## Hosting choice (record as ADR)
| Option | Choose when | Trade-off |
|---|---|---|
| Custom ASP.NET Core | casino/real-money, custom economy, compliance/audit, long-lived product | build and operate everything |
| Unity Gaming Services (Auth, Cloud Save, Economy, Remote Config, Cloud Code C# modules) | small team, Unity-only, fast start | vendor lock-in, pricing at scale, rate limits; Multiplay hosting ended Mar 2026 (verify: per-service quotas/pricing on docs.unity.com before ADR) |
| PlayFab / Nakama / AWS Game Backend Framework | standard F2P features, cross-engine | lock-in or self-hosting ops; extensibility limits |
- Hybrid is common: platform services for auth/matchmaking, custom service for wallet/ledger.

## Design review checklist
- [ ] Bootstrap + version gate + maintenance mode exist before first external build.
- [ ] Every value-bearing mutation is server-authoritative, idempotent and ledgered.
- [ ] Contracts additive-only policy and support window written in an ADR.
- [ ] Config has schema validation, versioned snapshots, defaults, kill switches.
- [ ] Telemetry: server-side authoritative economy events; consent gating; event catalog.
- [ ] Admin writes audited; admin and player auth fully separated.
- [ ] Load test at 3-5× forecast peak including login storm after maintenance.

## Sources
- Steamworks, "User Authentication and Ownership" https://partner.steamgames.com/doc/features/auth ; ISteamUserAuth https://partner.steamgames.com/doc/webapi/ISteamUserAuth
- Android Developers, "Support in-app updates (Unity)" https://developer.android.com/guide/playcore/in-app-updates/unity
- Apple, "App Store Server API" https://developer.apple.com/documentation/appstoreserverapi
- Apple, App Store Review Guidelines (4.8 Login Services) https://developer.apple.com/app-store/review/guidelines/
- Android Developers, "Enable server-side access to Play Games Services" https://developer.android.com/games/pgs/android/server-access
- Android Developers, Play Integrity API overview (quota, standard vs classic) https://developer.android.com/google/play/integrity/overview
- Unity, Remote Config docs https://docs.unity.com/en-us/remote-config ; Cloud Code C# modules https://docs.unity.com/en-us/cloud-code/modules/overview
- AWS, "Guidance for Custom Game Backend Hosting on AWS" https://github.com/aws-solutions-library-samples/guidance-for-custom-game-backend-hosting-on-aws
- OpenTelemetry .NET https://opentelemetry.io/docs/languages/dotnet/
- Martin Fowler, "Parallel Change" https://martinfowler.com/bliki/ParallelChange.html
