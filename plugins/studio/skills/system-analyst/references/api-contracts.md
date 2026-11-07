# API contracts (REST, events, gRPC, Unity client ↔ .NET server)

## REST resource design rules
- Resources are plural nouns: `/players/{playerId}/wallets/{currency}`; ≤ 2 levels of nesting;
  actions that don't fit CRUD → sub-resource or custom verb `POST /orders/{id}:cancel` (Google AIP-136).
- JSON field names camelCase; enums as strings (`"PENDING"`), never ints; IDs opaque strings.
- Times `date-time` UTC ISO 8601 (`2026-11-07T12:00:00Z`); durations ISO 8601 or `...Seconds` ints.
- Money: `{ "amountMinor": 1999, "currency": "USD" }` or decimal string; never float.
- Nullable vs absent: define once (absent = unchanged in PATCH; `null` = clear).
| Method | Safe | Idempotent | Typical success | Notes |
|---|---|---|---|---|
| GET | yes | yes | 200 | never mutates; cacheable (ETag) |
| POST | no | no* | 201 + `Location` / 200 / 202 | *make retry-safe with Idempotency-Key |
| PUT | no | yes | 200 / 204 | full replace; client-chosen ID |
| PATCH | no | no* | 200 | JSON Merge Patch (RFC 7396) preferred over JSON Patch |
| DELETE | no | yes | 204 | repeat → 204 or 404 (pick one, document) |
| Status | Use |
|---|---|
| 400 | malformed/validation (problem details with `errors[]`) |
| 401 / 403 | no/invalid credentials / authenticated but not allowed |
| 404 | not found or hidden for authz |
| 409 | state conflict (already claimed, concurrent idempotent request) |
| 412 / 428 | ETag mismatch / If-Match required (optimistic concurrency) |
| 422 | semantically invalid; idempotency key reused with different payload |
| 426 or custom 4xx problem type | client version too old → force update |
| 429 | rate limited + `Retry-After` |
| 500 / 502 / 503 / 504 | server / upstream / overloaded (+ `Retry-After`) / upstream timeout |

## OpenAPI contract-first
- Target OpenAPI 3.1 (full JSON Schema 2020-12: `type: [string, "null"]` replaces `nullable`,
  `examples` array, top-level `webhooks`). OpenAPI 3.2.0 (Sept 2025) adds QUERY method,
  hierarchical tags, streaming/sequential media (SSE), OAuth device flow — adopt only if
  tooling supports it (verify: codegen/lint support).
- Workflow: write YAML → lint (Spectral) → breaking-change diff in CI (oasdiff) → generate
  server stubs/clients (NSwag, Kiota, openapi-generator) → contract tests vs implementation.
- ASP.NET Core 9+ `Microsoft.AspNetCore.OpenApi` emits docs code-first; for contract-first
  diff the emitted doc against the reviewed spec in CI (verify: .NET 10 default OpenAPI 3.1 output).
```yaml
openapi: 3.1.0
info: { title: Rewards API, version: 1.4.0 }
servers: [{ url: https://api.example.com/v1 }]
security: [{ bearer: [] }]
paths:
  /players/me/daily-bonus:claim:
    post:
      operationId: claimDailyBonus
      parameters:
        - { name: Idempotency-Key, in: header, required: true, schema: { type: string, maxLength: 64 } }
      responses:
        '200':
          description: Claimed
          content:
            application/json:
              schema: { $ref: '#/components/schemas/ClaimResult' }
              examples: { ok: { value: { coins: 300, streak: 3, nextResetAt: '2026-11-08T00:00:00Z' } } }
        '409': { $ref: '#/components/responses/Problem' }
        '429': { $ref: '#/components/responses/Problem' }
components:
  securitySchemes: { bearer: { type: http, scheme: bearer, bearerFormat: JWT } }
  responses:
    Problem:
      description: Error
      content: { application/problem+json: { schema: { $ref: '#/components/schemas/Problem' } } }
  schemas:
    ClaimResult:
      type: object
      required: [coins, streak, nextResetAt]
      properties:
        coins: { type: integer, minimum: 0 }
        streak: { type: integer, minimum: 1 }
        nextResetAt: { type: string, format: date-time }
    Problem:
      type: object
      properties:
        type: { type: string, format: uri-reference }
        title: { type: string }
        status: { type: integer }
        detail: { type: string }
        instance: { type: string }
        code: { type: string }
```

## Error model — RFC 9457 (obsoletes RFC 7807)
- Media type `application/problem+json`. Members: `type` (URI, default `about:blank`),
  `title` (stable per type), `status` (must match HTTP status), `detail` (occurrence, not
  parsed by clients), `instance` (occurrence URI). Unknown extensions must be ignored by clients.
- Extensions: stable machine `code`, `errors[]` for field validation, `traceId`, `retryAfterSeconds`.
- Multiple problems of different types → return the most relevant; same type → array extension.
```json
{ "type": "https://errors.example.com/bonus-already-claimed", "title": "Bonus already claimed",
  "status": 409, "detail": "Daily bonus was claimed at 2026-11-07T08:12:00Z.",
  "code": "BONUS_ALREADY_CLAIMED", "nextResetAt": "2026-11-08T00:00:00Z", "traceId": "00-4bf9…-01" }
```
- Error catalogue per API: `code | status | meaning | retryable? | client action (UX)`.
- ASP.NET Core: `AddProblemDetails()` + `IExceptionHandler`; `Results.Problem(...)`.

## Pagination, filtering, sorting
| Style | Use | Contract |
|---|---|---|
| Cursor/keyset (default) | feeds, history, ledgers, large tables | `?pageSize=50&pageToken=…` → `{ items, nextPageToken }` (empty = end) |
| Offset | small admin tables needing "page 7 of 20" | `?offset&limit` + `totalCount` (costly on big tables) |
- Google AIP-158: `page_size` optional, server may cap (coerce > max to max), `next_page_token`
  opaque; changing filters with the same token → 400. Microsoft guidelines: `nextLink` URL.
- Cursor encodes last sort key + ID (`(createdAt, id) > (…)`); stable unique ordering required.
- Filters: explicit params (`?status=PENDING&createdAfter=`) or AIP-160 filter string; document
  allowed fields; reject unknown params (400) rather than ignore silently.

## Idempotency
- Header `Idempotency-Key` (IETF httpapi draft; Stripe convention). Client generates UUIDv4 per
  logical operation and REUSES it on retries. Server stores `(key, client/user scope) →
  request hash, status, response` for a TTL (Stripe: ≥ 24 h).
| Case | Response (draft-ietf-httpapi-idempotency-key-header) |
|---|---|
| Key missing on required endpoint | 400 |
| Same key, same payload, completed | replay stored response |
| Same key, different payload | 422 |
| Same key, original still processing | 409 |
- Natural idempotency beats keys when available: store txn ID unique constraint, `PUT` with
  client ID, `(playerId, bonusDay)` unique index. Webhooks/events: dedupe by event ID.
(verify: draft status — it is an Internet-Draft, not an RFC)

## Concurrency & long-running operations
- Optimistic concurrency: `ETag` on GET, `If-Match` on PUT/PATCH → 412 on mismatch; map to
  row version (EF Core `[Timestamp]`/xmin).
- Long work (exports, payouts) → `202 Accepted` + `Location: /operations/{id}` →
  `{ status: RUNNING|SUCCEEDED|FAILED, result|error }`; or webhook on completion.

## Versioning & compatibility
- Major version in path (`/v1`) for public/mobile APIs (Google AIP-185); Microsoft uses
  `api-version` query (date-based). Pick one per product; never both.
- Non-breaking (additive): new optional field, new endpoint, new optional param, new enum value
  ONLY if clients are tolerant readers. Breaking: remove/rename field, type change, new required
  input, changed semantics/defaults, new error for existing success path, tighter validation.
- Deprecation: `Deprecation` header (RFC 9745) + `Sunset` header (RFC 8594) + changelog;
  keep old major ≥ the longest-lived client build in the wild (mobile: months).
- Mobile reality: old Unity builds stay installed; keep N-2 client versions working or force
  update via min-version check (`X-Client-Version` header → problem type `client-update-required`).

## Rate limits & payloads
- `429` + `Retry-After`; document limits per client/user/IP; optional `RateLimit` headers
  (IETF httpapi draft, verify). Payload caps (e.g. request ≤ 64 KB, list `pageSize` ≤ 100).
- Mobile budgets: ≤ 1–3 calls per screen open; gzip/brotli; avoid > 100 KB JSON per response.

## Events — AsyncAPI 3.0 + CloudEvents envelope
```yaml
asyncapi: 3.0.0
info: { title: Wallet events, version: 1.0.0 }
servers: { prod: { host: kafka.internal:9092, protocol: kafka } }
channels:
  walletCredited:
    address: wallet.credited.v1
    messages: { walletCredited: { $ref: '#/components/messages/WalletCredited' } }
operations:
  publishWalletCredited:
    action: send
    channel: { $ref: '#/channels/walletCredited' }
components:
  messages:
    WalletCredited:
      headers: { type: object, properties: { ce_id: { type: string }, ce_type: { type: string } } }
      payload:
        type: object
        required: [playerId, currency, amountMinor, ledgerEntryId, occurredAt]
        properties:
          playerId: { type: string }
          currency: { type: string }
          amountMinor: { type: integer }
          ledgerEntryId: { type: string }
          occurredAt: { type: string, format: date-time }
```
- 3.0 vs 2.x: operations moved out of channels; `action: send|receive`; channel `address`
  separate from ID; request/reply supported.
- CloudEvents 1.0 required attributes: `id`, `source`, `specversion`, `type`; plus `time`,
  `subject`, `datacontenttype`. Dedupe key = `source` + `id`.
- Event naming: past tense facts `wallet.credited.v1`; payload carries IDs + changed state, not
  whole aggregates; schema version in type/topic; consumers ignore unknown fields.

## gRPC / Protobuf design
```proto
syntax = "proto3";
package studio.wallet.v1;
option csharp_namespace = "Studio.Wallet.V1";
service WalletService {
  rpc GetBalance(GetBalanceRequest) returns (GetBalanceResponse);
  rpc Credit(CreditRequest) returns (CreditResponse);   // idempotent via request_id
}
enum Currency { CURRENCY_UNSPECIFIED = 0; CURRENCY_COINS = 1; CURRENCY_GEMS = 2; }
message CreditRequest {
  string player_id = 1; Currency currency = 2; int64 amount_minor = 3;
  string request_id = 4; string reason_code = 5;
  reserved 6; reserved "legacy_note";
}
```
- Rules: version in package (`.v1`); never reuse/renumber fields — `reserved` removed ones;
  enum zero = `*_UNSPECIFIED`; `optional` for presence; snake_case fields; one request/response
  message per RPC (Google AIP / Buf style). Lint + breaking checks with `buf lint`/`buf breaking`.
- Errors: gRPC status codes (`INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`,
  `FAILED_PRECONDITION`, `ABORTED`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`) + `google.rpc.Status`
  details (ErrorInfo with reason code). Deadlines on every call.
- Unity: HTTP/2 gRPC is not native in UnityWebRequest; use gRPC-Web (`Grpc.Net.Client.Web`) or
  Cysharp YetAnotherHttpHandler; MagicOnion for C#-shared RPC/streaming (verify: target Unity
  version + platform support, incl. WebGL = gRPC-Web only).

## Unity client ↔ .NET server contract checklist
- Shared DTOs: `netstandard2.1` contracts library (no Unity refs) or codegen from OpenAPI/proto
  for both sides; JSON via Newtonsoft on client (studio:unity-developer architecture notes).
- Standard headers: `Authorization: Bearer`, `X-Client-Version`, `X-Platform`, `Accept-Language`,
  `traceparent` (W3C Trace Context), `Idempotency-Key` on mutations.
- Auth: platform sign-in (Game Center / Play Games / Steam / device) → server exchange → short
  access token (≈ 15 min) + refresh token; never trust client-provided player ID.
- Server-authoritative: client sends intents (`claim`, `spin`, `purchase receipt`), server
  returns resulting state + new balances; client never computes rewards/RNG.
- Tolerant reader: unknown fields ignored, unknown enum → `Unknown`; additive server changes
  must not crash old builds (contract test with oldest supported client DTOs).
- Network behavior per call: timeout (e.g. 10 s), retry policy (idempotent only, exponential
  backoff + jitter, max 3), offline queue for grants, error code → UX action map.
- Clock: server time in responses (`serverTime`) for timers; client offsets, never local clock.
- Snapshot endpoint at login (`GET /bootstrap`: profile, wallet, config version, feature flags)
  to minimize round trips; config versioned with ETag.

## Sources
- RFC 9457 Problem Details for HTTP APIs https://www.rfc-editor.org/rfc/rfc9457.html
- OpenAPI Specification v3.1.0 https://spec.openapis.org/oas/v3.1.0.html ; v3.2.0 https://spec.openapis.org/oas/v3.2.0.html
- AsyncAPI 3.0.0 specification https://www.asyncapi.com/docs/reference/specification/v3.0.0
- IETF draft Idempotency-Key header https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-04
- Stripe API, Idempotent requests https://docs.stripe.com/api/idempotent_requests
- Google AIP-158 Pagination https://google.aip.dev/158 ; AIP-185 Versioning https://google.aip.dev/185
- Microsoft REST API Guidelines https://github.com/microsoft/api-guidelines
- CloudEvents 1.0 spec https://github.com/cloudevents/spec
- Buf style guide https://buf.build/docs/best-practices/style-guide/
