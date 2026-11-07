# Quality metrics and test reporting

## Rules for any metric
- Each metric answers a decision question; if no decision changes, drop it.
- Report trend (last 3-5 builds/releases), not a single number; show the threshold.
- Never use defect counts to rate people (Goodhart: counts get gamed, reporting drops).
- Normalize: per feature, per KLOC, per 1k sessions, per test run - raw counts mislead.

## Core metrics
| Metric | Formula | Good signal / threshold (default) | Limits |
|---|---|---|---|
| Defect density | defects found / size (KLOC, story points, or feature) | compare areas: top 20% dense areas get more test + review | size units vary; use within one codebase only |
| Defect detection percentage (DDP) | pre-release defects / (pre-release + escaped in N days) | >= 90% for S1-S2 | needs a fixed window (e.g. 30 days post release) |
| Escape rate | escaped defects / total defects (= 1 - DDP) | <= 10%; any escaped S1 → root-cause review | depends on live telemetry quality |
| Open S1/S2 aging | count + days open | 0 S1 > 24 h; S2 median < 3 days | |
| Reopen rate | reopened / resolved | < 5% | high = weak fix verification or unclear repro |
| Test pass rate | passed / executed (per cycle) | RC >= 98% | pass rate of a weak suite is meaningless |
| Execution progress | executed / planned, by risk class | 100% of 20+ risk cases before gate | |
| Flaky test rate | tests with both pass and fail on same commit (window 7-14 days) / total tests | < 1% of tests; quarantine on detection | Google (2016): ~1.5% of runs flaky, ~16% of tests some flakiness, 84% of pass→fail transitions involved a flaky test |
| Automation share | automated regression cases / total regression cases | trend up for stable areas | automating unstable UI raises cost |
| CI feedback time | PR pipeline duration p50/p90 | PR < 15 min; nightly < 2 h | |
| MTTR (failed deployment recovery time, DORA) | mean time from production failure detection to restore | hours, not days; track p50 and max | measure restore (rollback/flag off), not root-cause fix |
| Change failure rate (DORA) | releases causing incident/hotfix / releases | < 15% | |
| Crash-free sessions/users | 1 - sessions with crash / sessions | see release-quality-gates.md | compare at equal exposure |
| Bug find/fix trend | new vs closed per day | converging before RC | flat "new" may mean testing stopped |

## Test coverage: meaning and limits
- Code coverage (line/branch) tells what code ran during tests, not that behavior was checked.
- Google guidance (2020): ~60% acceptable, 75% commendable, 90% exemplary; focus on coverage of changed
  lines in review (diff coverage) over global targets.
- Studio defaults: diff coverage >= 80% on domain logic (economy, rewards, wallet, rules); no global gate on
  view/MonoBehaviour code; 0% is a review flag, 100% is not a goal.
- Mutation testing measures assertion strength: Stryker.NET for .NET domain libraries; run nightly on core
  modules, track mutation score trend (>= 60-70% on money/RNG code).
- Requirements coverage (AC with >= 1 passing test) and risk coverage (high risks with planned + executed tests)
  matter more for go/no-go than code coverage.
- Tools: .NET `coverlet`/`Microsoft.Testing.Extensions.CodeCoverage` + ReportGenerator; Unity Code Coverage package
  (`com.unity.testtools.codecoverage`, `-enableCodeCoverage -coverageResultsPath`).

## Data sources
| Metric | Source |
|---|---|
| Defects | tracker export (Jira/YouTrack/GitHub) or `.team/reports/bug-*.md` |
| Tests | NUnit XML (Unity), TRX/JUnit XML (.NET, Playwright), CI history |
| Flakiness | CI test history: same commit, different results; reruns marked |
| Stability | Firebase Crashlytics, Backtrace, Sentry, Play Console vitals, App Store Connect / Xcode Organizer |
| Perf | Unity Profiler captures, Android GPU Inspector/Perfetto, backend APM (OpenTelemetry) |

## Test summary / release QA report template (`.team/reports/release-<v>-qa.md`)
```
# QA report - <product> <version> (<build id>) - <YYYY-MM-DD>
Verdict: GO | GO with risks | NO-GO     Decided by: qa-lead (final publish: human)
## Scope
Tested: <features/areas, platforms, device tiers>   Not tested: <items + accepted risk>
## Gate criteria
| # | Criterion | Threshold | Actual | Status | Evidence |
|---|---|---|---|---|---|
| 1 | Open S1/S2 | 0 / 0 unwaived | <n>/<n> | PASS/FAIL | <link/path> |
| 2 | High-risk tests executed | 100% | <x%> | | |
| 3 | Pass rate | >= 98% | | | |
| 4 | Crash-free sessions (beta) | >= <t>% | | | |
| 5 | Perf budgets (low tier) | <budget> | | | |
| 6 | Platform/compliance checks | done | | | |
## Defects
New <n> | Fixed <n> | Open by severity S1 <n> S2 <n> S3 <n> S4 <n> | Escapes from last release <n>
Top open issues: <ID - title - sev - owner - ETA> (max 5)
## Risks and waivers
| Risk ID | Description | Mitigation | Owner | Follow-up date | Approved by |
## Trends (last 3 builds)
Pass rate <a→b→c> | Open S2 <..> | Crash-free <..> | Flaky rate <..>
## Recommendations
<= 5 bullets: what to fix before release / what to watch during rollout
```
Keep it ≤ 1 page; link evidence instead of pasting logs.

## Weekly quality dashboard (minimum set)
1. Open S1/S2 with aging. 2. Find/fix trend. 3. Pass rate + flaky rate per suite. 4. Crash-free
sessions per platform/version. 5. Escapes in last release by area (feeds risk re-scoring).

## Sources
- Google Testing Blog, "Flaky Tests at Google and How We Mitigate Them" (2016) https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
- Google Testing Blog, "Code Coverage Best Practices" (2020) https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- DORA, software delivery performance metrics https://dora.dev/guides/dora-metrics-four-keys/
- ISTQB CTFL Syllabus v4.0 (test monitoring, control, completion) https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
- Stryker.NET mutation testing https://stryker-mutator.io/docs/stryker-net/introduction/
- Unity Code Coverage package https://docs.unity3d.com/Packages/com.unity.testtools.codecoverage@1.2/manual/index.html
