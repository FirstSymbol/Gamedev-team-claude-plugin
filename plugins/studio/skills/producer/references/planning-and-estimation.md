# Planning and estimation

## Game milestones (exit criteria = binary, each answers one risk question)
| Milestone | Risk question | Exit criteria (all must hold) | Typical share of schedule |
|---|---|---|---|
| Concept | Worth making? | One-pager, pillars, target audience, comps, business model, rough budget/team, top 10 risks | 3-5% |
| Prototype | Is the core fun/valuable? | Core loop playable (greybox), 5+ external playtests, fun/clarity signal vs pillars, kill/continue decision | 5-10% |
| Vertical slice | Can we make it at quality, at cost? | One slice of final quality (art, audio, UX, perf on min-spec), production pipeline proven, measured cost per content unit, production estimate | 10-15% |
| Alpha (feature complete) | Is everything in? | All features implemented (placeholder content ok), all systems testable end to end, no unknown tech left | 30-40% (production) |
| Beta (content complete) | Is it shippable? | All content final, zero A/B (crash/blocker) bugs open > SLA, perf/memory budgets met, localization in, cert pre-check passed | 15-20% |
| Gold / release candidate | Will platform accept it? | Cert/store requirements passed, RC build signed off by qa-lead, day-one patch plan | 5% |
| Soft launch (F2P) | Does it retain and monetize? | Tech KPIs (crash-free ≥ 99.5% sessions, load time) then D1/D7/D30 + ARPDAU vs genre target in 1-3 test markets | 2-6 months |
| Live / global | Can we operate it profitably? | LTV > CPI at scale, live-ops cadence running, on-call + incident process | ongoing |
- Pre-production (concept → slice) is where cheap pivots happen; budget 20-30% of time there.
- Non-game IT products: Discovery → MVP (walking skeleton + core job) → Beta (design partners) →
  GA → Growth. Same rule: each phase retires a named risk.
- Casino/social casino: add "math certified / RTP verified" and "wallet reconciliation passes"
  as beta exit criteria (see `studio:domain-igaming`).
- Soft-launch KPI gates vary by genre; set targets with data-analyst from current benchmarks
  (GameAnalytics publishes yearly; top-quartile D1 ~30% across mobile in 2025 data) (verify: latest report).

## WBS rules
- Decompose by deliverable (noun), not activity; 100% rule: children sum to parent, nothing outside.
- Leaf = work package: one owner role, ≤ 2 weeks (≤ 10 ideal days), clear done check.
- Game WBS branches: Design / Code (client, server, tools) / Art (2D, 3D, VFX, UI) / Audio /
  Narrative+Loc / QA / Release+Platform / Live-ops / Marketing assets / Production overhead.
- Content = count × unit cost: e.g., 40 levels × measured 6 days (from vertical slice) = 240 days.
  Never estimate content before the slice measured the unit cost.
- Include "invisible" work: integration, bug fixing (15-25% of dev time in production), cert,
  localization, store assets, analytics events, admin panel, tooling, onboarding.

## Estimation techniques
| Technique | Use when | How | Watch out |
|---|---|---|---|
| 3-point / PERT | Leaf tasks, critical path | E = (O + 4M + P) / 6; SD = (P − O) / 6 | People anchor O; ask P first ("what if it goes badly?") |
| T-shirt (XS-XL) | Early roadmap, epics | Map to ranges: S 1-3d, M 3-8d, L 2-4w, XL > 4w = split | XL means unknown; spike it |
| Planning poker | Team-level stories | Fibonacci points, simultaneous reveal, discuss outliers | Points are relative; don't convert to hours across teams |
| Reference class | Whole project / milestone | Find 3-10 similar past projects, take their actual overrun distribution, apply to your base estimate | Most powerful debias tool (Flyvbjerg); needs honest history |
| Analogy / unit cost | Content production | Measured cost per asset/level × count + 10-20% iteration | Unit cost from slice, not from guess |
| #NoEstimates (count) | Stable flow, similar-sized items | Forecast from item count × throughput | Requires right-sizing items (all ≤ SLE) |
- Aggregation: sum of Es; project SD = sqrt(sum of SD²) (assumes independence; real tasks
  correlate, so treat as optimistic). P85 ≈ E + 1.04 SD; P95 ≈ E + 1.65 SD.
- Software overruns are right-skewed: median 1.2-1.5×, tail 2-3× for novel tech (verify per org).
- Agent-team note: specialists' token/time cost is not human effort. Estimate human-review time,
  external dependencies (store review, cert, legal) and playtest calendar separately.

## Velocity and forecasting
- Velocity = points Done per sprint (DoD met). Use the last 3-6 sprints; report a range (min-max or P15-P85).
- Never compare velocities across teams; never set velocity targets (Goodhart).
- Prefer throughput (items finished per week) for forecasting: no estimation overhead.
- Monte Carlo "When will N items be done?":
  1. Collect daily/weekly throughput samples (≥ 5-10 periods, recent, same team/process).
  2. Simulate: repeatedly sample a random period's throughput until the backlog (N, plus
     expected growth 10-30% for discovered work) is exhausted; record periods needed.
  3. Run ≥ 1,000 trials (10,000 common); read percentiles.
  4. Commit at P85 externally; plan internally to P50. ASOS found P85 forecasts right ~90% of the time.
- "How many by date D?" = same simulation, count items done by D; commit at P85 (i.e. the count
  reached in 85% of runs).
```python
import random
def when(backlog, samples, trials=10000):
    res = []
    for _ in range(trials):
        left, weeks = backlog, 0
        while left > 0:
            left -= random.choice(samples); weeks += 1
        res.append(weeks)
    res.sort(); return {p: res[int(trials*p/100)-1] for p in (50, 85, 95)}
```
- Re-forecast every sprint/week; show the forecast trend (dates sliding = early warning).

## Critical path and dependencies
- Critical path = longest chain of dependent work; zero float. Shorten by: parallelizing
  (fast-tracking), adding capacity to non-learning work (crashing), or cutting scope on it.
- Gamedev usual critical-path items: core tech/netcode, content pipeline, platform cert, external
  vendors (outsourced art, audio, localization), store/legal approvals, backend scale tests.
- Dependency log entry: from → to, deliverable, need-by date, owner, state, fallback.
- Schedule risk first: unknown tech, external dependencies and fun-validation early; polish late.
- Merge bias: a milestone waiting on 3 parallel 85%-likely tracks is only ~61% likely on time.

## Buffers
- Critical Chain style: strip padding from tasks (use ~P50), add one project buffer ≈ 50% of
  the removed padding, or 15-25% of critical-path duration; feeding buffers where side chains join.
- Fever chart: % buffer consumed vs % critical chain complete. Green if consumed < complete,
  yellow up to +15 pts, red beyond → trigger recovery (cut list, add help, re-plan).
- Fixed-date launches (holiday, event, platform showcase): buffer = scope, not time. Keep a
  ranked cut list worth 20-30% of remaining effort.
- Certification/store review buffer: plan 2+ submission cycles for console, 1-2 weeks for
  first iOS/Android review (verify: `studio:domain-pc-console`, current store review times).

## Planning checklist
- [ ] Fixed vs flexible constraint declared (scope/time/cost/quality).
- [ ] Milestones with exit criteria and owners; slice before production.
- [ ] WBS 100% rule; leaves ≤ 2 weeks; invisible work included.
- [ ] Estimates are ranges by doers; reference-class correction applied.
- [ ] Forecast P50/P85; buffer visible; critical path and dependencies listed.
- [ ] Top risks feed plan order (risky first).

## Sources
- Clinton Keith, "Agile Game Development: Build, Play, Repeat", 2nd ed., Addison-Wesley, 2020.
- PMI, "PMBOK Guide" 8th ed., 2025 (principles; schedule, scope, finance, risk domains) https://www.pmi.org/standards/pmbok
- Daniel Vacanti, "When Will It Be Done?", 2020; ActionableAgile Monte Carlo docs https://55degrees.atlassian.net/wiki/spaces/ActionableAgile/pages/2407399482/Monte+Carlo+How+Many
- ASOS Tech, "The Full Monte" (forecast accuracy by percentile) https://medium.com/asos-techblog/the-full-monte-901d721b8532
- Bent Flyvbjerg & Dan Gardner, "How Big Things Get Done", 2023 (reference class forecasting).
- Eliyahu Goldratt, "Critical Chain", 1997 (buffers, fever chart).
- GameAnalytics benchmarks summary 2026 https://gamedevreports.substack.com/p/gameanalytics-mobile-and-pc-game
