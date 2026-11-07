# Test plan - <product> <release/milestone>
Owner: <qa-lead>  Date: <YYYY-MM-DD>  Status: draft | approved  Strategy: <path to test-strategy.md>

## 1. Context
- Scope (features/areas): <list with spec paths>
- Out of scope + accepted risk: <item - reason - risk ID>
- Test objectives: <find defects in X / confirm Y / verify compliance Z>
- Test basis: <PRD/GDD/story/API contract paths>

## 2. Assumptions and constraints
- <devices available, env ready by date, code freeze date, store sandbox access>

## 3. Stakeholders and roles
| Role | Who | Responsibility |
|---|---|---|
| QA lead | <name/agent> | plan, triage, gate |
| QA engineer(s) | | design, automation, execution |
| Dev owners | | fixes, unit/integration tests |

## 4. Communication
- Triage: <cadence>; status report: <cadence, path>; blocker escalation: <to whom>

## 5. Risk register (product risks)
| ID | Area | Risk | L | I | Score | Approach (level/type/technique) | Owner |
|---|---|---|---|---|---|---|---|
| R1 | <wallet> | <double credit on retry> | 4 | 5 | 20 | API concurrency + idempotency tests, exploratory | <qa> |

## 6. Test approach
- Levels and types: <component / integration / system / acceptance; functional, perf, compatibility, security, LQA, compliance>
- Automation: <what is automated where (EditMode, PlayMode, API, E2E, load)>
- Techniques: <EP/BVA, decision table, state transition, pairwise, exploratory charters>
- Environments: <dev/stage URLs, backend version, feature flags>
- Device/platform matrix: <P0 / P1 / P2 lists or link>
- Test data: <accounts, generators, store sandbox users>
- Entry criteria: <measurable>
- Exit criteria: <measurable, e.g. 0 S1, S2 <= N, 100% high-risk executed, pass >= 98%>
- Metrics collected: <pass rate, open S1/S2, flaky rate, crash-free>
- Deliverables: <test cases path, test-run reports, release QA report>

## 7. Schedule and effort
| Activity | Start | End | Effort | Notes |
|---|---|---|---|---|
| Test design | | | | |
| Execution cycle 1 | | | | |
| Regression / RC | | | | |
| Cert / store pre-check | | | | |
