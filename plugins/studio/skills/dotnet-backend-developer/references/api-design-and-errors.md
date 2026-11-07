# API design and error handling (game client + admin APIs)

## Resource and route conventions
- Plural nouns, kebab-case paths, IDs in path: `GET /api/v1/players/{playerId}/wallets`.
- Commands that aren't CRUD → sub-resource nouns: `POST /wallets/{id}/debits`, `POST /bonuses/daily/claims`,
  `POST /rounds/{id}/settlement` — not `/doDebit`.
- "Me" alias for the caller: `GET /api/v1/me/inventory` (ID comes from the token).
- Separate route groups (and ideally hosts/ports) for player API, admin API (`/admin/v1`), internal (`/internal`), webhooks (`/webhooks/{provider}`).
- JSON camelCase, enums as strings, timestamps UTC ISO 8601 with `Z`, money as `{ "amountMinor": 1500, "currency": "COIN" }`.

## Status codes (use exactly these)
| Situation | Code |
|---|---|
| Read OK / command done with body | 200 |
| Created resource | 201 + `Location` |
| Accepted async job | 202 + status URL |
| Done, no body | 204 |
| Malformed input / validation | 400 (`ValidationProblem`, `errors` map) |
| Missing/invalid token | 401 |
| Authenticated but not allowed | 403 (use 404 if existence must be hidden) |
| Not found | 404 |
| Version/state conflict, duplicate key with different payload | 409 |
| Precondition failed (`If-Match` ETag mismatch) | 412 |
| Business rule rejected (insufficient funds, bonus already claimed today) | 422 (or 409 — pick one per API, document) |
| Rate limited | 429 + `Retry-After` |
| Client too old | 426 or 400 with code `client.update_required` (pick one, document) |
| Bug/unhandled | 500 (generic body + traceId) |
| Dependency down/maintenance | 503 + `Retry-After` |

## Error catalog (ProblemDetails, RFC 9457)
```json
{ "type": "https://errors.example.com/wallet/insufficient-funds",
  "title": "Insufficient funds", "status": 422,
  "code": "wallet.insufficient_funds", "detail": "Balance 120 < required 500",
  "traceId": "00-4bf9...-01", "errors": null }
```
- `code` = stable machine key `<area>.<snake_case>`; Unity/admin map codes to localized text. Never branch on `title`/`detail`.
- Keep the catalog in the shared contracts lib (constants) and in the API spec; adding a code a
  client can't handle is a breaking change for that client → fallback "generic error" UI required.
- `detail` safe for end users or omitted; never echo internal IDs, SQL, stack traces, other players' data.
- Validation: `errors: { "amount": ["must be > 0"] }` keyed by camelCase JSON path.
- Log once at the boundary with the same `traceId`; 4xx at Information/Warning, 5xx at Error.

```csharp
public sealed record Error(string Code, string Detail, int Status);
public static IResult ToProblem(this Error e) =>
    TypedResults.Problem(title: e.Code, detail: e.Detail, statusCode: e.Status,
        type: $"https://errors.example.com/{e.Code.Replace('.', '/')}",
        extensions: new Dictionary<string, object?> { ["code"] = e.Code });
public static class WalletErrors {
    public static Error InsufficientFunds(long have, long need) =>
        new("wallet.insufficient_funds", $"Balance {have} < required {need}", 422);
}
```

## Idempotency contract (all state-changing player/admin commands)
- Client sends `Idempotency-Key: <uuid>` generated once per user intent (button press), reused on retries.
- Server stores `(scope=playerId, key) → request hash, status, response` for ≥ 24 h.
  - Same key + same hash, completed → return stored response (same status/body), header `Idempotent-Replayed: true`.
  - Same key, still processing → 409 `request.in_progress` (client retries later).
  - Same key + different hash → 422 `request.idempotency_key_reused`.
- Store and business effect commit in one transaction (see game-economy-consistency).
- Spec: IETF draft "The Idempotency-Key HTTP Header Field" (verify current draft status).

## Pagination, filtering, sorting
- Player feeds/history: cursor (keyset) pagination: `?limit=50&cursor=<opaque>` → `{ items, nextCursor }`;
  cursor = base64 of last `(sortKey, id)`; stable under inserts.
- Admin grids: offset pagination acceptable for small/medium tables (`page`, `pageSize` ≤ 100, `total`
  optional — `COUNT(*)` on big tables is expensive; offer "has more" instead).
- Filters as explicit query params (`status=active&createdFrom=...`); whitelist sortable fields
  (`sort=-createdAt`); reject unknown fields with 400. Never pass raw sort/filter strings to SQL.
- Hard caps: `limit` max 100–200; date ranges max (e.g. 31 days) for admin exports; exports async (202 + job).

## Concurrency on updates (admin edits)
- Return `ETag` (row version) on GET; require `If-Match` on PUT/PATCH; 412 on mismatch → UI reloads.
- PATCH: JSON Merge Patch (`application/merge-patch+json`) for simple objects; prefer explicit command endpoints for state transitions.

## Game-client compatibility
- Old clients live for months on mobile: additive changes only within a version; `minSupportedVersion` gate.
- Unknown enum values/fields must be ignored by clients — make it a client requirement in the contract.
- Server time in responses that drive timers (`serverTime`, `nextClaimAt`), never trust device clock.
- Large catalogs/config: versioned, cacheable `GET /config?v=<hash>` + CDN; client sends known hash → 304.
- Batch endpoints for chatty startup (`GET /me/bootstrap` returns profile + wallet + config versions) to cut mobile round trips.

## Webhooks in (payments, platform notifications)
- Verify signature (HMAC/JWS per provider) on the raw body before parsing; reject old timestamps (replay window 5 min).
- Respond 2xx fast after durable enqueue; process async; dedupe by provider event ID (unique constraint).
- Provider retries out of order: process by state machine, not arrival order.

## API documentation deliverables
- OpenAPI generated from code (`MapOpenApi`) and diffed in CI; every endpoint has summary, auth
  requirement, all `ProducesProblem` codes, example payloads.
- Changelog entry for client teams (unity-developer, frontend-developer) with new codes and deprecations.

## Sources
- Microsoft REST API Guidelines https://github.com/microsoft/api-guidelines
- RFC 9457 Problem Details https://www.rfc-editor.org/rfc/rfc9457
- RFC 9110 HTTP Semantics (status codes, conditional requests) https://www.rfc-editor.org/rfc/rfc9110
- IETF draft Idempotency-Key header https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
- Stripe idempotent requests https://docs.stripe.com/api/idempotent_requests
- RFC 7396 JSON Merge Patch https://www.rfc-editor.org/rfc/rfc7396
