# PRDs and feature specs

## PRD structure (templates/prd.md) — 1-3 pages, link out for details
| Section | Content | Common failure |
|---|---|---|
| Header | owner, status (draft/review/approved/shipped), date, links (brief, OKR, OST) | no status → stale docs |
| Problem | segment, job, evidence (data, quotes), why now | solution restated as problem |
| Goals & metrics | 1 primary metric (baseline → target, by when), 1-3 guardrails | output goals ("ship X") |
| Non-goals | what we deliberately won't do this release, and why | missing → scope creep |
| Users & scenarios | personas/segments, top 3-5 scenarios (narrative) | everyone is the user |
| Scope / requirements | prioritized capability list (must/should/could), rules, edge cases at business level | UI pixel specs, implementation detail |
| UX | links to flows/prototypes (ux-ui-designer) | |
| Dependencies | teams, services, vendors, data, legal | discovered mid-build |
| Risks & assumptions | top risks with mitigation; assumptions with evidence level | |
| Launch criteria | binary checks to release (see below) | "when ready" |
| Rollout | flags, staged %, markets, experiment design, rollback | big bang |
| Open questions | owner + due date each | unowned questions |
| Evidence | discovery results that justify building | none |
- Length rule: if > 3 pages, split into a product PRD + feature briefs.
- PM writes what/why; business-analyst derives stories + AC; system-analyst contracts; ux designs.

## Success metrics
- Primary metric = the product outcome from discovery (behavioral, attributable, moves within
  weeks). Examples: FTUE completion %, D7 retention of new cohort, payer conversion in 7 days,
  task success rate, weekly active creators.
- Specify: definition (event-level, with data-analyst), baseline, target, minimum detectable
  effect, timeframe, segment, data source.
- Guardrails: metrics that must not degrade (crash-free sessions, D1, refund rate, support
  tickets/1k DAU, session length for "dark pattern" checks, latency p95).
- Counter-metric pairing: speed ↔ quality, monetization ↔ retention, engagement ↔ complaints.
- Leading vs lagging: pair a leading indicator (activation) with the lagging business result (LTV).

## Non-goals
- Write 3-7 explicit non-goals: adjacent features, segments, platforms, scale levels, integrations.
- Format: "Not in this release: <X> — because <reason>; revisit <when/trigger>."

## Launch criteria (binary checklist)
- [ ] Primary + guardrail metrics instrumented and validated in a test build (data-analyst sign-off).
- [ ] qa-lead go: no open S1, S2 within agreed threshold, perf budgets met.
- [ ] Feature flag / remote config kill switch tested; rollback plan written.
- [ ] Support/ops ready: FAQ, admin tooling, CS macros, on-call informed.
- [ ] Compliance cleared (privacy, age rating, store policy, gambling/loot box rules where relevant).
- [ ] Localization complete for launch markets; store/release notes ready.
- [ ] Experiment design approved (if A/B): hypothesis, MDE, sample size, duration, stop rule.
- [ ] Stakeholders informed; success review date booked (e.g., +14/+30 days).

## Game feature brief (for game teams; pairs with GDD)
- Ownership split: lead-game-designer/game-designer own mechanics and the GDD; PM owns the business
  case, metrics and launch. The brief is ≤ 1 page and links to GDD sections.
| Field | Example (daily login streak in social casino) |
|---|---|
| Player value (fantasy/feeling) | "I get rewarded for coming back; a streak feels like progress" |
| Player motivation / segment | returning casual players, D2-D14 |
| Pillar fit | pillar "generous & fair": rewards visible, no punishment for missing a day beyond reset |
| Business goal | D7 retention +2 pp in new cohort |
| Core loop touchpoint | session start → reward → spend in slots → return tomorrow |
| Economy impact | +X coins/day per active player; inflation check by economy-monetization-designer |
| Live-ops hooks | remote-configurable reward tables, event multipliers |
| Metrics | streak start rate, day-N continuation, D7, coins sink/source ratio |
| Risks | reward inflation, notification fatigue, compliance (no purchase-required streaks for minors) |
| Scope / non-goals | no paid streak-repair in v1 |
- Fun check: prototype/playtest before full build if the feature is gameplay; data-backed for meta/retention features.
- Monetized features: show value to non-payers too; avoid pay-to-win in competitive modes;
  disclose odds for random rewards where required (compliance-advisor).

## Specs beyond the PRD (who writes what)
| Artifact | Owner | Path |
|---|---|---|
| Stories + Gherkin AC, BRD | business-analyst | `.team/specs/<area>/stories/` |
| API / data contracts, sequence diagrams | system-analyst | `.team/specs/<area>/contracts/` |
| UX flows, wireframes | ux-ui-designer | `.team/specs/<area>/ux/` |
| GDD sections, balance tables | game-designer | `.team/specs/gdd/` |
| Tracking plan, experiment design | data-analyst | `.team/specs/<area>/analytics.md` |
| Architecture impact, ADR | tech-lead-architect | `.team/decisions/` |

## Review checklist (PM self-review before handoff)
- [ ] A new engineer can state the problem, user and metric after reading page 1.
- [ ] No implementation prescribed unless it is a real constraint (and labeled as such).
- [ ] Each must-have maps to the primary metric or a launch criterion.
- [ ] Edge cases at business level: offline, failure, refunds, abuse, minors, regions.
- [ ] Open questions have owners; approval list named (producer, tech-lead, design lead).

## Sources
- Marty Cagan, "Inspired", 2nd ed., 2017 (product spec as prototype + context; PRD critique).
- Lenny Rachitsky, "My favorite templates" / PRD guides, Lenny's Newsletter https://www.lennysnewsletter.com/p/my-favorite-templates-issue-37
- Atlassian, "Product requirements document" guide https://www.atlassian.com/agile/product-management/requirements
- Ron Kohavi, Diane Tang, Ya Xu, "Trustworthy Online Controlled Experiments", 2020 (guardrail metrics).
- Clinton Keith, "Agile Game Development", 2nd ed., 2020 (feature value for players, GDD vs backlog).
