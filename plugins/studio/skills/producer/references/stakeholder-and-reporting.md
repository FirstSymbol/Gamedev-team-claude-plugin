# Stakeholders and reporting

## Stakeholder map (producer view)
| Stakeholder | Cares about | Cadence | Channel |
|---|---|---|---|
| Human / exec / publisher | date, budget, go/no-go, top risks | weekly + milestone | status report, milestone review |
| Product-manager / lead-game-designer | scope, value, vision integrity | per sprint | review, change log |
| Leads (tech, QA) | capacity, quality gates, debt | per sprint | planning, RAID |
| Platform holders / stores | submission dates, compliance | per milestone | release-platform-manager |
| Vendors / outsourcing | specs, dates, acceptance | weekly | dependency log |
| Live players / community (post-launch) | issues, roadmap | per release | marketing-manager, liveops-manager |
- Power/interest grid: manage closely (high/high), keep satisfied (high power), keep informed (high interest), monitor.
- Agree up front: who decides scope, date, budget, and go/no-go (RACI line in `brief.md`).

## Status report rules (templates/status-report.md)
- ≤ 1 page; first line = overall RAG + one-sentence why; then decisions needed.
- Report against the baseline: planned vs forecast date, scope done vs total, budget burn.
- Facts with evidence paths (build, test report, burn-up), not adjectives.
- Same structure every period; show trend arrows (↑ ↓ →) vs last report.
- Bad news early and with options; never introduce a red item without a recovery proposal.

## RAG rules (derive, don't feel)
| Dimension | Green | Amber | Red |
|---|---|---|---|
| Schedule | P85 forecast ≤ milestone date | P50 ≤ date < P85 | P50 > date |
| Buffer (fever chart) | consumed % ≤ chain complete % | ≤ +15 pts | > +15 pts |
| Scope | change ≤ 5% of baseline, approved | 5-15% or pending decisions | > 15% or unapproved growth |
| Quality | open S1 = 0, S2 trend down, budgets met | S2 rising or 1 budget missed | any S1 > SLA, crash-free < target |
| Cost/capacity | burn ≤ plan +5% | +5-10% | > +10% |
| Risk | no red risk without active mitigation | ≥ 1 red with mitigation | red risk fired or unmitigated |
- Overall RAG = worst dimension, unless explicitly justified. Watermelon check: if all green but
  the team says "worried", investigate (age of items, untested assumptions).
- Red needs: cause, impact, recovery options (≥ 2), decision owner, decide-by date.

## Burn-up chart (prefer over burn-down)
- Two lines: total scope (points or items) and completed; x = sprints/weeks.
- Shows scope growth separately from progress (burn-down hides it).
- Add forecast cone: extend completed line at P15/P50/P85 throughput; where it crosses the scope
  line = date range. Mark milestone dates and scope-change events.
- Text form for `.team/` reports:
```
Week | Scope | Done | P50 ETA | P85 ETA
W10  | 180   | 92   | W19     | W22
W11  | 186   | 104  | W19     | W21
```

## Change control
1. Request logged in `.team/specs/plan/changes.md`: ID, requester, change, reason, date.
2. Impact analysis (producer + owners, ≤ 1 day): effort range, schedule (critical path?),
   cost, risk, quality, dependencies; compare with the milestone cut list.
3. Options: (a) accept + cut equal scope, (b) accept + move date, (c) defer to later milestone,
   (d) reject. Recommend one.
4. Decide: product-manager for scope within a milestone; human for date/budget/pillar changes.
5. Update baseline, roadmap, forecast, risks; announce in next status report.
- Threshold: changes < 1 day of effort and off the critical path can be approved by
  product-manager directly (log anyway). Batch small changes weekly.
- Freeze points: feature freeze at alpha, content freeze at beta, code freeze at RC (only
  release-blocker fixes, approved by qa-lead).

## Scope negotiation — iron triangle
- Scope / time / cost, with quality as the non-negotiable center. Pick which is fixed; at most two.
- Default stances:
| Context | Fixed | Flex |
|---|---|---|
| Fixed launch window (holiday, platform event, licensed IP) | time, quality | scope |
| Publisher milestone payments | scope per milestone, time | cost (via internal effort), polish |
| Live-ops season | time | scope (feature parity across platforms optional) |
| Regulated release (casino, kids) | quality/compliance | time |
- Adding people late to a late software project makes it later (Brooks); only add to
  separable, low-onboarding work (content, QA passes).
- Negotiation script: restate goal → show forecast vs date → present 2-3 options with
  consequences → recommend → ask for decision with deadline.

## Cut lists
- Per milestone, rank remaining scope by value (product-manager) vs cost (team) into:
  must (pillar/MVP), should, could, won't-this-release. Cut list = should + could, ranked.
- Size the cut list ≥ 20-30% of remaining effort so a red forecast can be fixed by cuts alone.
- Cut whole features, not quality across everything ("thin everywhere" = bad reviews).
- Typical game cut order: extra modes → content quantity (levels/items) → secondary
  systems → platform extras → polish on low-traffic areas. Never cut: FTUE quality, stability,
  core loop polish, legal/compliance, accessibility basics.
- Pre-agree cuts with product-manager/lead-game-designer at milestone start; execution is then fast.

## Milestone review agenda
1. Exit criteria check (binary, with evidence paths).
2. Playable/usable demo of the increment.
3. Forecast for next milestone (P50/P85), buffer state.
4. Top 5 risks and changes since last review.
5. Decisions: go / go with conditions / re-plan / stop. Record in `.team/decisions/` or `changes.md`.

## Sources
- PMI, "PMBOK Guide" 8th ed., 2025 (stakeholders, governance domains) https://www.pmi.org/standards/pmbok
- Mike Cohn, "Agile Estimating and Planning", 2005 (burn charts, release planning).
- Frederick P. Brooks, "The Mythical Man-Month", anniversary ed., 1995.
- Clinton Keith, "Agile Game Development", 2nd ed., 2020 (milestones with publishers, cut decisions).
- Eliyahu Goldratt, "Critical Chain", 1997 (buffer reporting).
