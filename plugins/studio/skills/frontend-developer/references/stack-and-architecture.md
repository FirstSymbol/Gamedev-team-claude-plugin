# Admin frontend stack and architecture

## Default stack (2026-11; verify exact versions in `package.json`)
| Concern | Default | Alternatives / notes |
|---|---|---|
| Build | Vite 8 (Rolldown bundler, stable 2026-03) | keep existing Vite 6/7 projects until a reason to bump |
| UI runtime | React 19.x (npm latest 19.3) + TypeScript `strict` (latest majors 6.0 Mar 2026, 7.0 Jul 2026) | React Compiler 1.0 optional (auto-memo) |
| Server state | TanStack Query v5 | SWR (simpler), RTK Query (if Redux already) |
| Routing | TanStack Router (type-safe search params, loaders) | React Router 7/8 (8.0 Jun 2026; data/framework mode) |
| Forms | React Hook Form + `@hookform/resolvers/zod`, or TanStack Form v1 (Standard Schema) | — |
| Validation | Zod 4 | Valibot (smaller) |
| Tables | TanStack Table (headless; v9 since Aug 2026, v8 still common) | AG Grid (Community MIT; Enterprise paid) for heavy grids, pivot, Excel export |
| Components | shadcn/ui (Radix primitives, copied into repo) + Tailwind CSS 4 | MUI, Mantine, Ant Design (fast admin CRUD) |
| Charts | Recharts / ECharts | Grafana embeds for ops metrics |
| Client state | React state/context; Zustand for cross-page UI state | no Redux for server data |
| API client | `openapi-typescript` + `openapi-fetch`, or Orval (generates TanStack Query hooks) | never hand-written DTOs |
| Lint/format | ESLint 9/10 flat config (10.0 Feb 2026) + typescript-eslint, Prettier or Biome | — |
- No SSR needed for internal admin tools: SPA served by the BFF or static hosting behind auth.
  Next.js/TanStack Start only if public pages need SSR/SEO. React Server Components had a critical
  RCE (CVE-2025-55182, CVSS 10, 2025-12-03; `react-server-dom-*` 19.0/19.1.0/19.1.1/19.2.0, fixed 19.0.1/19.1.2/19.2.1,
  plus follow-up DoS/source-exposure CVEs) — if RSC frameworks are used, stay on the latest patched versions.

## React vs Blazor decision
| Choose React + TS | Choose Blazor (.NET 10) |
|---|---|
| dedicated frontend skills, rich UI ecosystem, complex grids/charts | team is C#-only, CRUD-heavy back-office, shared DTOs/validation with backend |
| independent deploy from backend | tight integration with ASP.NET Core auth (cookie, Identity passkeys) |
| need many third-party UI libs | acceptable: Blazor Server (SignalR circuit per user, low-latency network) or WebAssembly (bigger download) |
- Blazor .NET 10 notes: `[PersistentState]` declarative state, circuit state persistence, QuickGrid
  for simple grids, `AddValidation()` for nested model validation; Interactive Server render mode
  suits internal tools on a reliable network. Commercial grids: MudBlazor (MIT), Radzen (free core), Telerik/Syncfusion (paid).
- Don't mix both in one admin app; ADR via tech-lead-architect.

## Project layout (feature-first)
```
src/
  app/            router setup, providers (QueryClient, auth, theme), layout shell
  features/
    players/      routes.tsx  PlayerSearchPage.tsx  PlayerDetailPage.tsx  api.ts (queries/mutations)  schemas.ts  components/
    wallets/      AdjustBalanceDialog.tsx  api.ts ...
    audit/
  shared/
    api/          generated/ (OpenAPI types/client)  http.ts (fetch wrapper, ProblemDetails parsing)
    ui/           design-system components (shadcn)  DataTable.tsx  ConfirmDialog.tsx
    auth/         usePermissions.ts  <Can permission="..."/>
    lib/          formatting (money, dates), query-keys.ts
tests/e2e/        Playwright specs
```
- Features don't import each other's internals; shared code moves to `shared/` when 2+ features need it.
- Path aliases (`@/shared/...`) in `tsconfig` + Vite; enforce boundaries with ESLint `import/no-restricted-paths` or `eslint-plugin-boundaries`.

## Server state with TanStack Query v5
```ts
export const playerKeys = {
  all: ['players'] as const,
  list: (f: PlayerFilters) => [...playerKeys.all, 'list', f] as const,
  detail: (id: string) => [...playerKeys.all, 'detail', id] as const,
};
export const playerListQuery = (f: PlayerFilters) => queryOptions({
  queryKey: playerKeys.list(f),
  queryFn: ({ signal }) => api.GET('/admin/v1/players', { params: { query: f }, signal }).then(unwrap),
  placeholderData: keepPreviousData,     // no flicker while paging
  staleTime: 30_000,
});
export function useAdjustBalance(playerId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (v: AdjustInput) => api.POST('/admin/v1/players/{id}/balance-adjustments', {
      params: { path: { id: playerId } }, body: v,
      headers: { 'Idempotency-Key': v.idempotencyKey } }).then(unwrap),
    onSuccess: () => qc.invalidateQueries({ queryKey: playerKeys.detail(playerId) }),
  });
}
```
- `queryOptions` factories shared between route loaders (prefetch) and components.
- Defaults to tune: `staleTime` (0 by default → refetch on mount/focus), `retry` (3 by default; set 0–1 for 4xx), `refetchOnWindowFocus` (keep for ops dashboards).
- Mutations: no automatic retry for non-idempotent calls; invalidate precise keys; optimistic updates only for harmless toggles.
- Live data: polling via `refetchInterval` (10–30 s) or SSE/SignalR pushing `invalidateQueries`.

## Routing and URL state
- Filters/sort/page/selected tab live in search params, validated with Zod (TanStack Router `validateSearch`).
- Route-level code splitting (lazy routes) per feature; protected route wrapper checks session + permission.
- Deep links to entities (`/players/:id`) so support can paste links into tickets.

## Forms and validation
```ts
const adjustSchema = z.object({
  amountMinor: z.number().int().refine(v => v !== 0, 'Must not be 0').refine(v => Math.abs(v) <= 1_000_000, 'Over limit'),
  currency: z.enum(['COIN', 'GEM']),
  reason: z.string().trim().min(10).max(500),
  ticketId: z.string().regex(/^SUP-\d+$/).optional(),
});
```
- Client schema mirrors server rules for UX; server stays authoritative. Map ProblemDetails `errors`
  to fields (`setError(path, { message })`), unknown errors to a form-level alert with `traceId`.
- Money: integers in minor units in forms and API; format with `Intl.NumberFormat`; never floats.
- Dates: send ISO UTC; show user's zone + explicit label (UTC toggle for ops).

## Tables / data grids
- Server-side pagination/sort/filter for anything that can exceed ~1,000 rows (`manualPagination`, `manualSorting` in TanStack Table).
- Virtualize long lists (`@tanstack/react-virtual`) above ~200 rendered rows.
- Column config: stable IDs, persisted visibility/order per user (localStorage, non-sensitive).
- Bulk actions: explicit selection count, confirm, server batch endpoint (not N requests).
- Exports: server-generated async job (CSV) for large data; client export only for the visible page.

## Performance budgets (internal tool)
- Initial JS ≤ ~300 KB gzip for shell; route chunks lazy; check with `vite build` + `rollup-plugin-visualizer` (7.x peer-supports Rolldown 1.x).
- Interaction to Next Paint < 200 ms on grids; memoize row renderers or rely on React Compiler.
- Avoid importing whole icon/date libs; tree-shakeable imports (`lucide-react`, `date-fns`).

## Sources
- React docs https://react.dev/
- Vite 8 announcement https://vite.dev/blog/announcing-vite8
- React blog: Critical security vulnerability in RSC (2025-12-03) https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
- TanStack Query v5 docs https://tanstack.com/query/latest/docs/framework/react/overview
- TanStack Router docs https://tanstack.com/router/latest/docs/framework/react/overview
- TanStack Form v1 announcement https://tanstack.com/blog/announcing-tanstack-form-v1
- Zod docs https://zod.dev/
- What's new in ASP.NET Core 10 (Blazor section) https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0
