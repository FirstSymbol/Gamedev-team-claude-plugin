# Test strategy and test planning (ISTQB CTFL 4.0 based)

## Core vocabulary (CTFL 4.0, 2023)
| Term | Meaning | Use in practice |
|---|---|---|
| Test basis | Specs the tests derive from (PRD, GDD, story AC, API contract) | Every test case traces to a basis item |
| Test objective | Why we test: find defects, build confidence, reduce risk, verify compliance | State per level in the plan |
| Test level | Component, component integration, system, system integration, acceptance | Each has its own owner, env, entry/exit |
| Test type | Functional, non-functional (ISO 25010), black-box, white-box | Choose per risk, not per habit |
| Confirmation vs regression | Re-test the fix vs re-check unchanged areas | Both after every fix; regression scope by impact analysis |
| Shift-left | Static testing (reviews of specs/AC/code) + early test design | QA reviews AC before sprint start |
| Test approach | Levels, types, techniques, deliverables, entry/exit criteria, independence, metrics, data, env | The heart of the plan |

Seven principles worth enforcing: testing shows presence not absence of defects; exhaustive
testing is impossible (prioritise by risk); early testing saves cost; defects cluster
(Pareto - focus where bugs were found); tests wear out (pesticide paradox - refresh cases);
testing is context dependent; absence-of-defects fallacy (built wrong thing = still failure).

## Test levels mapped to Unity + .NET stack
| Level | Unity client | .NET backend | Admin web | Owner |
|---|---|---|---|---|
| Component | EditMode NUnit on plain C# (rules, economy calc, state machines) | xUnit v3 unit tests on domain | Vitest/Jest on components | engineers |
| Component integration | PlayMode tests: prefab + services, scene load, Addressables | `WebApplicationFactory` + Testcontainers (Postgres/Redis) | component + mocked API | engineers + qa-engineer |
| System | Device E2E (AltTester/GameDriver), manual functional on builds | API suites (contract + scenario) | Playwright E2E | qa-engineer |
| System integration | Client ↔ backend ↔ store/IAP sandbox, ads, analytics, push, platform services | 3rd-party providers (payments, KYC, game providers) | SSO, reporting | qa-engineer |
| Acceptance | UAT by PM/design, playtests, beta (TestFlight/closed track/Steam Playtest), cert pre-checks | Ops acceptance (backup/restore, failover) | Back-office UAT | PM/design/ops + QA |

## Pyramid vs trophy - pick per layer
| Shape | Origin | Where it fits | Target mix (tests count) |
|---|---|---|---|
| Test pyramid | Cohn 2009; Fowler/Vocke "Practical Test Pyramid" 2018 | Unity client: logic is cheap to unit-test, device E2E is slow/flaky | ~70% EditMode, ~20% PlayMode/integration, ~10% device E2E + manual exploratory |
| Testing trophy | Kent C. Dodds 2018 (static, unit, integration, E2E) | .NET APIs and admin web: most value at integration with real DB | static analysis (analyzers, TS strict) + thin unit + **thick integration** + few E2E |
| Ice-cream cone (anti) | - | Teams with UI-only automation | Refactor: push each UI check down to the lowest level that can catch it |
Rules:
- One behavior, one level: if an EditMode test covers reward math, E2E checks only that the reward UI shows.
- Integration tests use real engines (Postgres, Redis) via Testcontainers; no EF InMemory for behavior.
- Manual testing goes to exploratory charters, usability, feel, visual, device-specific checks - not to
  regression scripts a machine can run.
- Contract tests replace many E2E checks between Unity client and backend (see `studio:qa-engineer` (automation-dotnet-web)).

## Risk-based testing
Risk level = likelihood x impact (1-5 each; score 1-25).
| Likelihood drivers | Impact drivers |
|---|---|
| New/complex code, new tech, many integrations, past defect cluster, time pressure, team inexperience, high churn | Money/wallet loss, RNG/fairness, data loss/save corruption, PII leak, store/cert rejection, crash on launch, legal/regulatory, reputational (streamers), revenue funnel (FTUE, shop) |
| Score | Treatment |
|---|---|
| 20-25 | Multiple levels + techniques, automation in CI, exploratory sessions, independent review, exit gate item |
| 12-19 | Systematic black-box design (EP/BVA/decision table), automated regression |
| 6-11 | Happy path + key negatives, sampled regression |
| 1-5 | Smoke only or explicitly out of scope (log as accepted risk) |
- Re-score each milestone; escaped defects raise likelihood of that area for the next 2 releases.
- Product risks go to the plan; project risks (env late, devices unavailable) go to `.team/risks.md`.

Typical high-risk areas by product:
| Product | Score-20+ areas |
|---|---|
| Social/real-money casino | wallet ledger, bet/win settlement, RNG, RTP config, bonus wagering, jackpots, geo/age gating, purchase flow |
| Mobile F2P | IAP + receipt validation, FTUE, save/cloud sync, live event start/end time, ads SDK, offline mode, low-end Android |
| Multiplayer | reconnect, desync, matchmaking under load, server authority/cheats, session migration |
| PC/console | suspend/resume, user switching, controller disconnect, save integrity, achievements, cert requirements |

## Entry / exit criteria (measurable examples)
| Level/milestone | Entry | Exit |
|---|---|---|
| Component (CI) | builds; analyzers clean | 100% tests pass; no new warnings; coverage on changed core logic not lower than baseline |
| System test cycle | smoke pass on build; test env + data ready; release notes/changelog for build | all planned high-risk cases executed; 0 open S1; S2 <= agreed N with owners; pass rate >= 95% |
| Feature "done" | AC reviewed by QA; test cases designed | AC verified on target device tier; regression for impacted areas green; bugs triaged |
| Beta/soft launch | feature complete; crash-free >= 99.0% internal (release-quality-gates.md) | crash-free sessions >= target; KPIs instrumented and verified |
| Release candidate | code freeze; no open S1/S2; cert pre-check done | gate criteria in release-quality-gates.md met or waived by named approver |
- Exit can be unmet when stopping; then the residual risk must be visible and accepted (CTFL 4.0).

## Test plan content (CTFL 4.0 §5.1.1 structure)
1. Context: scope, test objectives, constraints, test basis, out of scope.
2. Assumptions and constraints (devices available, env access, freeze dates).
3. Stakeholders: roles, responsibilities, training needs.
4. Communication: cadence (daily triage, weekly report), channels, templates.
5. Risk register: product risks (with scores) and project risks.
6. Test approach: levels, types, techniques, deliverables, entry/exit criteria, independence,
   metrics, test data, environments (dev/stage/prod-like), device matrix, deviations.
7. Budget and schedule: effort per area, milestones, cert submission windows.
Template: qa-engineer `templates/test-plan.md`. Strategy (org-wide, long-lived) ≠ plan (per release).

## Test strategy document skeleton (long-lived, ≤ 2 pages)
- Quality goals and ISO 25010 priorities for the product.
- Level/type matrix and automation split (pyramid/trophy targets per layer).
- Environments: local, CI, dev, staging (prod-like data volume), device lab/cloud farm.
- Tooling: UTF + AltTester, xUnit v3 + Testcontainers, Playwright, k6/NBomber, crash reporter.
- CI gates: PR (unit + static), nightly (integration + PlayMode on device), pre-release (full regression, soak, load).
- Defect process: severity/priority definitions, triage SLA, bug template.
- Metrics and reporting cadence; who decides go/no-go and how waivers are approved.

## Independence and roles
- Engineers own component + integration tests; QA designs system/acceptance and reviews AC.
- Independent review for 20+ risks (QA tests what devs did not write tests for).
- Embed one QA per feature team for shift-left; keep a central lead for strategy and gates.

## Sources
- ISTQB CTFL Syllabus v4.0 (2023) https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
- Ham Vocke, "The Practical Test Pyramid" (martinfowler.com, 2018) https://martinfowler.com/articles/practical-test-pyramid.html
- Martin Fowler, "TestPyramid" bliki https://martinfowler.com/bliki/TestPyramid.html
- Kent C. Dodds, "The Testing Trophy and Testing Classifications" https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications
- ISO/IEC 25010:2023 product quality model https://www.iso.org/standard/78176.html
- Google Testing Blog, "Just Say No to More End-to-End Tests" (2015) https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
