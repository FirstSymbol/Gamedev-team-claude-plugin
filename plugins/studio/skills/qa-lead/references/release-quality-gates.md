# Release quality gates, triage, go/no-go

## Severity (impact, set by QA) - studio scale
| Sev | Definition | Game/casino examples |
|---|---|---|
| S1 Blocker | Crash/hang on common path, data/save loss, money/wallet wrong, security/PII exposure, cert/store-policy fail, legal non-compliance | crash on launch on a top-10 device; double credit of a win; purchase charged but not granted; RTP config wrong; age gate bypass |
| S2 Critical | Major feature broken, no reasonable workaround; progression blocker for a segment | daily bonus not granted after midnight UTC; matchmaking fails for one region; IAP restore broken |
| S3 Major | Feature degraded, workaround exists; noticeable perf drop | wrong reward animation; 10% FPS drop on mid tier; localisation overflow in shop |
| S4 Minor | Cosmetic, low-visibility text, polish | z-fighting in menu; typo in settings |
Severity is objective impact; do not inflate to get attention, do not deflate to ship.

## Priority (urgency, set at triage by producer/PM with QA)
| | P1 fix now (hotfix/this build) | P2 this release | P3 next release | P4 backlog |
|---|---|---|---|---|
| S1 | default | only if feature is dark/flagged off | never | never |
| S2 | if in FTUE/revenue/high-reach | default | with explicit waiver | - |
| S3 | rare (visible in store screenshots/marketing) | if cheap | default | - |
| S4 | - | polish window | default | default |
Reach multiplier: % of DAU affected (segment/device share) raises priority one step if > 10%.

## Triage process
- Cadence: daily during stabilization/release, 2-3x/week otherwise; 15 min, fixed agenda.
- Participants: qa-lead (chair), producer, tech lead or owning engineer; PM/design for UX issues.
- Inputs: new bugs since last triage, reopened, S1/S2 aging list, crash cluster top-10.
- Per bug: valid/dup/as-designed? → severity check → priority → owner → target build → needs info?
- SLAs (typical): S1 ack < 2 h, fix or mitigation (flag off / rollback) < 24 h; S2 < 3 working days.
- Bug bar: published per milestone (e.g. Alpha: no S1 in core loop; Beta: 0 S1, S2 <= 10; RC: 0 S1, 0 S2 unwaived).
- Crash clusters from Crashlytics/Backtrace/Sentry are triaged like bugs: one ticket per signature,
  severity by users affected + platform threshold proximity.
- "Won't fix" needs a reason (risk accepted by whom); "as designed" goes to design to confirm.

## Go/no-go gate (release candidate)
| # | Criterion | Typical threshold | Evidence |
|---|---|---|---|
| 1 | Open defects | 0 S1; 0 S2 unless waived by named approver | tracker query link/export |
| 2 | Planned tests executed | 100% of high-risk; >= 95% overall; pass >= 98% | test run report |
| 3 | Regression | full regression for impacted areas + smoke all platforms green | CI + manual run IDs |
| 4 | Stability | crash-free sessions >= target on beta/staged cohort (below) | crash dashboard snapshot |
| 5 | Performance | within budgets on lowest supported tier (below) | profiler/benchmark capture |
| 6 | Platform compliance | store/cert checklist done (release-platform-manager) | platform report |
| 7 | Compliance | odds disclosure, age gate, privacy labels/consent verified (compliance-advisor) | compliance report |
| 8 | Backend readiness | migrations rehearsed, rollback tested, load test at 2x expected peak | ops report, k6/NBomber run |
| 9 | Monitoring | crash, error rate, economy anomaly alerts live; kill switches tested | alert list |
| 10 | Rollout plan | staged % schedule + halt criteria agreed | release plan |
Verdict wording: **GO**, **GO with risks** (list risk IDs + owner + follow-up date), **NO-GO** (blocking items + owner + ETA).
Any NO-GO area → overall NO-GO (matches `/studio:release`). Final publish decision belongs to the human.

## Crash-free / stability targets
| Source | Figure | Note |
|---|---|---|
| Instabug Mobile App Stability Outlook 2025 | median crash-free sessions 99.95% (all apps); iOS 99.91%, Android 99.80% median | cross-industry, not games-only |
| Instabug 2023 | median 99.94%; p75 99.99%; "99.9% is no longer enough" | |
| Google Play Android vitals | bad-behavior thresholds: user-perceived crash rate 1.09% (overall), ANR 0.47%; per phone model 8% | exceeding → reduced visibility, store-listing warning (verify: developer.android.com/topic/performance/vitals) |
No public games-specific crash benchmark found (Backtrace/Crashlytics publish case studies, not medians).
Studio defaults (Unity games tend to run below app medians because of native/GPU crashes):
| Stage | Crash-free sessions | Crash-free users | ANR (Android) |
|---|---|---|---|
| Internal/QA builds | >= 99.0% | - | - |
| Beta / soft launch | >= 99.5% | >= 99.0% | < 0.47% user-perceived |
| Global launch gate | >= 99.8% (stretch 99.9%) | >= 99.5% | < 0.3% |
| Live, any staged step | no regression > 0.1 pp vs previous version at same rollout % | | halt if > vitals threshold |
- Compare at equal exposure (same rollout %, same days since release); new versions look better early.
- Track OOM separately (Unity iOS kills are not always "crashes" in dashboards) and per device model.

## Performance budget gate (fill per project; defaults for mobile F2P)
| Metric | Low tier (e.g. 3-4 GB RAM Android) | Mid/High | PC/console |
|---|---|---|---|
| Frame time | p95 <= 33.3 ms (30 fps) in core loop | p95 <= 16.7 ms (60 fps) | locked target per mode (verify: platform perf reqs) |
| Peak memory (PSS) | <= 60-70% of device RAM class budget, no OOM in 1 h soak | | per-platform title budget |
| Cold start to interactive | <= 10 s; Android vitals flags slow cold start >= 5 s | <= 5 s | (verify: XR-001 launch timings) |
| Download size | base AAB/IPA within store limits; rest via PAD/ODR/Addressables (verify current limits) | | |
| Battery/thermal | no throttling in 30 min session on reference device | | n/a |
| Backend | p95 latency <= agreed SLO at 2x peak load; error rate < 0.1% | | |
Gate rule: regression > 10% vs last release on any budget metric = S2 until explained.
Perf details: `studio:unity-developer` (performance), technical-artist for rendering.

## Regression scope selection
1. Start from the change set: diff of code/config/content since last release + touched asmdefs/services.
2. Impact analysis: map changed modules → features (keep a feature-to-module map in the strategy).
3. Always run: smoke (launch, login, FTUE, purchase sandbox, save/load, core loop, logout), money/RNG paths.
4. Add: high-risk areas per register, areas with escapes in last 2 releases, platform-specific paths
   if engine/SDK/OS changed (Unity version bump, Android target API, iOS SDK) → full device matrix.
5. Config-only/live-ops release: economy and event configs validated by schema + server tests + targeted
   manual check; no full client regression.
6. Hotfix: fix verification + smoke + regression of the touched area only; full suite runs after release.
| Change type | Regression scope |
|---|---|
| Engine/SDK/target API upgrade | full regression, full device matrix, perf + soak |
| New feature behind flag | feature tests + smoke with flag on and off |
| Backend contract change | contract tests + client compatibility matrix (N, N-1 min supported client) |
| Content/config only | schema validation + targeted checks |
| Hotfix | confirmation + smoke + impacted area |

## Staged rollout halt criteria (agree before release)
- Crash-free sessions below gate or > 0.1 pp worse than previous version at same exposure.
- New crash signature in top-3 within 24 h; ANR above vitals threshold on any top-10 device.
- Purchase success rate drops > 2 pp; economy anomaly alert (currency inflow > 3 sigma).
- Backend 5xx > 0.5% for 10 min. Action: halt rollout, flag off, hotfix or rollback server.

## Sources
- Instabug, Mobile App Stability Outlook 2025 https://www.instabug.com/mobile-app-stability-outlook-2025
- Instabug, Benchmarking crash-free sessions https://instabug.com/blog/benchmarking-crash-free-sessions-for-mobile-apps-whats-a-good-crash-free-rate
- Android Developers, Android vitals https://developer.android.com/games/optimize/vitals
- Android Developers Blog, Raising the bar on technical quality on Google Play (2022) https://android-developers.googleblog.com/2022/10/raising-bar-on-technical-quality-on-google-play.html
- Microsoft GDK, Top failing certification test cases https://learn.microsoft.com/gaming/gdk/docs/store/policies/console/console-topfailingtestcases
- ISTQB CTFL Syllabus v4.0 (defect management, test completion) https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
