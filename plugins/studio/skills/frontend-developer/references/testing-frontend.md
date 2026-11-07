# Frontend testing: Vitest, Testing Library, MSW, Playwright

## Mix
| Level | Tool | What | Target |
|---|---|---|---|
| Unit | Vitest | pure functions: formatters, schema rules, permission helpers, query-key builders | ms each |
| Component/integration | Vitest + React Testing Library + MSW | a screen/form with real hooks, mocked network | most of the suite |
| E2E | Playwright | critical journeys on a real build against a test backend | 5–20 specs, < 10 min |
| Visual (optional) | Playwright `toHaveScreenshot` | design-system components, key pages | stable fonts/data |
| A11y | `@axe-core/playwright`, `vitest-axe` | each new screen | zero serious/critical violations |

## Vitest setup
```ts
// vite.config.ts (or vitest.config.ts)
test: { environment: 'jsdom', setupFiles: ['./src/test/setup.ts'], globals: false,
        coverage: { provider: 'v8', reporter: ['text', 'lcov'], include: ['src/**'] } }
// setup.ts
import '@testing-library/jest-dom/vitest';
import { server } from './msw-server';
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));   // MSW 2.x; MSW 3 renamed it `onUnhandledFrame`
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```
- Versions (npm, 2026-11): Vitest 5 (Sep 2026, Node 22+, Vite 6.4+), MSW 3 (Sep 2026, ESM-only, Node 22+, TS 5.9+).
- Vitest shares Vite config/transforms; since Vitest 4 (Oct 2025) Browser Mode is stable (real Chromium via `@vitest/browser-playwright`: `provider: playwright()`) for components that jsdom can't emulate.
- `happy-dom` is faster than jsdom; switch only if tests pass identically.
- Fake time with `vi.useFakeTimers()` for debounce/countdowns; restore after each test. MSW 3 no longer bypasses
  fake timers: advance them for `delay()`ed mocked responses.

## Testing Library rules
- Query by role/label/text the user sees: `getByRole('button', { name: /ban player/i })`; `getByTestId` last resort.
- Interact via `@testing-library/user-event` (`const user = userEvent.setup(); await user.click(...)`), not `fireEvent`.
- Await async UI with `findBy*` / `waitFor`; no arbitrary sleeps.
- Render with real providers via a helper: fresh `QueryClient({ defaultOptions: { queries: { retry: false } } })` per test, router, permission context.
- Assert behavior and visible output, not implementation (no state/props inspection, no snapshot of whole trees).

## MSW (Mock Service Worker v2) for network
```ts
export const handlers = [
  http.get('/admin/v1/players', ({ request }) => {
    const q = new URL(request.url).searchParams.get('q');
    return HttpResponse.json({ items: q ? [playerFixture] : [], nextCursor: null });
  }),
  http.post('/admin/v1/players/:id/balance-adjustments', async ({ request }) => {
    if (!request.headers.get('Idempotency-Key')) return HttpResponse.json(problem('request.missing_key'), { status: 400 });
    return HttpResponse.json({ balanceAfter: 700, auditId: 'a-1' });
  }),
];
```
- Same handlers in tests, Storybook and local dev (browser worker) → one fake backend.
- Fixtures typed from generated OpenAPI types; failing type-check = contract drift.
- Test error paths: 400 with field errors, 403, 409/412 conflict, 422 business error, 500 with traceId, network error.

## Must-have component tests for admin screens
- Permission gating: without `balance:adjust` the button is absent; with it, present.
- Dangerous action: confirm disabled until reason valid; submits once on double click; sends idempotency key; shows result + audit ID.
- Form ↔ server errors: ProblemDetails `errors` appear on the right fields.
- List: filters update URL search params and refetch; empty/filtered-empty/error states render.

## Playwright E2E
```ts
// playwright.config.ts essentials
use: { baseURL: process.env.E2E_BASE_URL, trace: 'on-first-retry', screenshot: 'only-on-failure' },
retries: process.env.CI ? 2 : 0,
projects: [{ name: 'setup', testMatch: /auth\.setup\.ts/ },
           { name: 'chromium', use: { storageState: 'playwright/.auth/support.json' }, dependencies: ['setup'] }],
```
- Auth once per role in a setup project; save `storageState` per role (support, finance, admin) — gitignore the files.
- Locators: `page.getByRole(...)`, `getByLabel`; web-first assertions `await expect(locator).toBeVisible()` (auto-wait/retry).
- No `waitForTimeout`; wait on UI state or `page.waitForResponse` for specific calls.
- Isolate data: each test creates its own player via API (`request` fixture) and cleans up; never depend on order.
- Target a seeded test environment (Aspire/docker-compose backend) — not production, ever.
- Critical journeys: login (+MFA stub), player search → detail, balance adjust with confirm, ban/unban,
  permission denial for a lower role, audit entry visible after action.
- CI: `npx playwright install --with-deps chromium`; shard (`--shard=1/4`) when > 10 min; upload trace/report artifacts.
- Debug: `npx playwright test --ui`, `--debug`, trace viewer (`npx playwright show-trace`).

## Coverage and gates
- Gate on changed-lines coverage for `features/` (e.g. ≥ 80%); exclude generated API client and `*.stories.tsx`.
- Required CI checks: `tsc --noEmit`, ESLint, Vitest, Playwright smoke on PR; full E2E nightly/pre-release.
- Flaky test = bug: quarantine with issue link, fix within the sprint.

## Sources
- Vitest docs https://vitest.dev/guide/
- Vitest 4.0 announcement https://vitest.dev/blog/vitest-4
- Vitest 5.0 release notes https://github.com/vitest-dev/vitest/releases/tag/v5.0.0
- MSW 3.0 release notes https://github.com/mswjs/msw/releases/tag/v3.0.0
- Testing Library guiding principles https://testing-library.com/docs/guiding-principles
- Testing Library query priority https://testing-library.com/docs/queries/about#priority
- MSW docs https://mswjs.io/docs/
- Playwright best practices https://playwright.dev/docs/best-practices
- Playwright authentication https://playwright.dev/docs/auth
- TanStack Query testing guide https://tanstack.com/query/latest/docs/framework/react/guides/testing
