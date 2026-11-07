# Admin panel patterns (game / casino back-office)

## RBAC in the UI
- Source of truth = server. After login, fetch `GET /admin/v1/me` → `{ user, roles, permissions: ["players:read", "balance:adjust:small", ...], env }`.
- Check permissions (fine-grained verbs), not roles, in components: roles change, permissions are stable.
```tsx
export function Can({ permission, children, fallback = null }: { permission: Permission; children: ReactNode; fallback?: ReactNode }) {
  return usePermissions().has(permission) ? <>{children}</> : <>{fallback}</>;
}
<Can permission="balance:adjust"><AdjustBalanceButton playerId={id} /></Can>
```
- Hide what the user can never do; disable + tooltip ("Requires Finance approval") for what needs escalation.
- Route guards redirect to a 403 page; API 403 at runtime shows a non-crashing "no access" state.
- Typical roles for a casino/F2P back-office (confirm with security-engineer/compliance-advisor):
| Role | Typical permissions |
|---|---|
| Support L1 | player search/read, notes, resend email, small goodwill grants under cap |
| Support L2 | + ban/unban, session revoke, larger grants with reason |
| Finance/Payments | refunds, chargeback handling, payout approval, reports |
| LiveOps | events/offers/config edit + publish (with approval), segment preview |
| Compliance/RG | KYC review, self-exclusion/limits view & enforce, audit export |
| Admin | user/role management only (not automatically all business actions) |
- Separation of duties: the creator of a large adjustment/payout cannot approve it (4-eyes).
- Environment banner: color-coded header (PROD red, STAGE amber) + env name in tab title.

## Audit log (UI side)
- Every mutating admin action shows its result with audit ID; the server writes the audit record
  (who, when, what, before/after, reason, ticket, IP, user agent) — UI never writes audit itself.
- Player detail page has an "Activity / audit" tab (filterable by actor, action, date).
- Audit views are read-only, exportable with permission, and include actor display names + IDs.
- Required inputs for sensitive actions: `reason` (min length), optional ticket ID; validated client + server.

## Dangerous action confirmation
| Risk | UX pattern |
|---|---|
| Low (edit note) | inline save, undo toast |
| Medium (ban, revoke sessions, publish config) | modal summarizing effect + reason field + confirm button naming the action ("Ban player") |
| High (balance adjust above cap, refund, mass grant, delete) | modal + type-to-confirm (player ID or amount) + 4-eyes approval request; preview of affected count for bulk |
- Generate `Idempotency-Key` (`crypto.randomUUID()`) when the dialog opens; reuse it on retry; new key on reopen.
- Disable submit while pending; show server result (new balance, audit ID); never optimistic for money.
- Show before → after values ("Balance 1,200 → 700 COIN") computed from server preview where possible.
- Bulk ops: dry-run endpoint returning affected count + sample; execute as server job with progress.

## CRUD screen anatomy
- List page: search bar (debounced 300 ms, min 2–3 chars for free text), filter chips, sortable columns,
  server pagination, row click → detail, bulk select only where bulk endpoints exist.
- Detail page: header (entity ID with copy, status badges, key actions), tabs (overview, wallet/ledger, purchases, sessions, audit, notes).
- Create/edit: form page or drawer; unsaved-changes guard (`beforeunload` + router blocker); `If-Match`/ETag
  conflict → "Changed by someone else, reload" dialog.
- Status changes via explicit commands (Ban, Unban, Approve) rather than editable status dropdowns.

## Filtering, search, pagination
- URL is the state: `/players?q=john&status=active&sort=-createdAt&cursor=...`; parse/validate with Zod; defaults omitted from URL.
- Server pagination: cursor for big/append-only tables (ledger, audit, rounds), page/pageSize for small sets.
- Show total only if the API provides it cheaply; otherwise "Load more"/"Next".
- Date range pickers with presets (Today, 7d, 30d) and server cap (e.g. ≤ 31 days for heavy tables).
- Lookups by exact ID/email/transaction ID first (fast index path), fuzzy search second.

## Dashboards
- KPIs from backend aggregates (not computed client-side from raw rows): DAU, revenue, deposits/withdrawals, GGR, active rounds, error rates.
- Each tile: value, period, comparison, last updated time; auto-refresh 30–60 s via `refetchInterval` or SSE.
- Metric definitions owned by data-analyst; link tile → definition.

## Data display rules
- Money: integer minor units → `Intl.NumberFormat(locale, { style: 'currency' | 'decimal' })` with currency code; virtual currencies with fixed decimals = 0.
- Time: UTC in API; display local + UTC on hover; relative times ("5 min ago") only with absolute tooltip.
- PII masking by default (email `j***@mail.com`, phone last 4); "reveal" requires permission and is audited.
- Copy buttons for IDs; monospace for IDs/hashes.

## Error and empty states
- Parse ProblemDetails: show `code`-mapped message, `traceId` with copy button for bug reports.
- Distinguish: empty (no data), filtered empty (clear filters CTA), error (retry), forbidden (request access), offline.
- Global error boundary per route; never white screen.

## Accessibility (internal tools still need it)
- WCAG 2.2 AA basics: labels, focus visible, focus trap + return in dialogs (Radix handles), keyboard
  table navigation, contrast; status not by color alone (icon + text).

## Sources
- OWASP Authorization Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Logging Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- NN/g, Confirmation dialogs https://www.nngroup.com/articles/confirmation-dialog/
- TanStack Table docs (pagination, server-side) https://tanstack.com/table/latest/docs/guide/pagination
- WCAG 2.2 https://www.w3.org/TR/WCAG22/
