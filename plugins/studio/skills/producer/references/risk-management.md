# Risk management

## Risk register method (`.team/risks.md`)
- Statement format: "Because <cause>, <event> may occur, leading to <impact on goal>." One risk
  per row; an issue (already happened) goes to the RAID issues list instead.
- Columns: ID | risk | P | I | score | owner | response | mitigation | trigger | due | state.
- Probability (P) 1-5: 1 < 10%, 2 10-30%, 3 30-50%, 4 50-70%, 5 > 70%.
- Impact (I) 1-5 — take the worst axis:
| I | Schedule | Cost | Scope/quality | Player/business |
|---|---|---|---|---|
| 1 | < 1 week | < 2% | cosmetic | none visible |
| 2 | 1-2 weeks | 2-5% | minor feature cut | minor KPI dip |
| 3 | 2-4 weeks / milestone slip | 5-10% | feature cut, quality noticeable | rating/KPI hit, PR noise |
| 4 | > 1 month / launch window at risk | 10-20% | pillar compromised | store rejection, revenue loss |
| 5 | launch missed / project kill | > 20% | product unviable | legal action, data breach, license loss |
- Score = P × I. 15-25 red (owner acts now, reported weekly to human), 8-14 amber (mitigation
  planned with date), 1-7 green (watch). Any I = 5 is reviewed regardless of P.
- Every red/amber risk has a trigger (early-warning signal with threshold) and a due date.
- Review cadence: top 10 each sprint/status report; full register each milestone; closed risks kept.

## Response strategies (threats / opportunities)
| Strategy | Threat example | Opportunity counterpart |
|---|---|---|
| Avoid | Drop unproven netcode feature from v1 | Exploit: lock in a platform featuring slot |
| Mitigate (reduce P or I) | Spike + perf test early; second vendor | Enhance: extra polish on a viral feature |
| Transfer | Outsource porting with fixed price; insurance; partner liability | Share: co-marketing with platform |
| Accept (active: contingency reserve / passive) | Minor art delay, buffer absorbs | Accept |
| Escalate | Outside team authority (budget, legal, platform policy) → human | Escalate |
- Contingency plan = what we do if it fires (pre-agreed cut, fallback tech, delay comms).
- Residual risk after mitigation is re-scored; secondary risks created by a response are logged.

## Gamedev risk catalog (seed for every project)
| Category | Typical risks | Early-warning signal | Default mitigation |
|---|---|---|---|
| Scope creep | Feature additions, "one more system", content bloat | Backlog grows > 10%/sprint; unplanned work > 25% | Change control, cut list, pillar test for every add |
| Fun / design | Core loop not fun; FTUE confusing | Playtest scores flat; D1 low in tests | Prototype gate, weekly external playtests, kill criteria |
| Crunch / people | Overtime, burnout, key-person dependency | Hours > 45/week 2+ weeks; one owner per system | Scope cuts over overtime; pair/document; bus factor ≥ 2 |
| Technology | New engine version, netcode, perf on min-spec, backend scale | Frame time > budget at slice; load test fails | Spikes first, perf budgets per milestone, ADRs |
| Pipeline / content | Tools not ready, asset rework, outsourcing quality | Unit cost > slice estimate by 20% | Prove pipeline in slice; vendor test task; style guide |
| Platform / cert | TRC/XR/Lotcheck failure, store policy rejection, SDK deadlines | Pre-cert checklist red items | Early cert pre-check, platform contacts, 2 submission cycles buffer |
| Market | Competitor launch, genre saturation, UA cost too high | CPI tests > LTV target; wishlist velocity low | Soft launch / CPI test early, positioning review |
| Monetization / economy | Inflation, exploits, pay-to-win backlash | Currency sinks < sources; refund rate up | Economy sim, telemetry, server authority, kill switches |
| Legal / compliance | Loot box laws, gambling licensing, COPPA/GDPR, IP/music licenses | New regulation in target market; no license chain | compliance-advisor review per market; "needs human legal review" |
| Security / fraud | Cheating, payment fraud, account takeover, wallet double-spend | Anomalous currency gain; chargeback rate > 1% | Server-authoritative economy, receipt validation, idempotent wallet |
| Operations | Outages at launch, no on-call, live-ops overload | No load test; no runbook | Load test 3-5× expected peak, runbooks, staged rollout |
| Dependencies / vendors | SDK (ads, analytics) changes, middleware license, publisher approvals | Vendor misses 1st date | Contract dates + fallback; abstraction layer for SDKs |
| Financial | Burn > plan, funding milestone missed | Burn rate > plan 2 months | Milestone-based budget, re-scope early |
- Casino/real-money: add RNG certification lead time, jurisdiction licensing, responsible gaming
  requirements, payment-provider approval (see `studio:domain-igaming`).

## RAID log (`.team/specs/plan/raid.md`)
| Type | Fields | Rule |
|---|---|---|
| Risks | ID, statement, P, I, owner, response, trigger | Lives in `.team/risks.md`; RAID links IDs |
| Assumptions | ID, assumption, impact if false, owner, validate-by date, state | Unvalidated past date → becomes a risk |
| Issues | ID, issue, impact, owner, action, due, state | Happened now; resolve or escalate within 2 working days |
| Dependencies | ID, from → to, deliverable, need-by, owner, state, fallback | Late dependency → issue + critical-path check |
- Decisions go to `.team/decisions/ADR-NNN-*.md` (technical) or `changes.md` (scope); RAID links them.

## Pre-mortem (Gary Klein) — run at each milestone plan, 30-45 min equivalent
1. Frame: "It is <date after milestone>. The milestone failed badly. Why?"
2. Each relevant role (or spawned specialist, ≤ 3) lists failure reasons independently; no discussion first.
3. Merge and cluster; score P × I; add new risks to the register.
4. For top 5: one mitigation now + one trigger to watch; adjust the plan (order, buffer, cuts).
5. Record in `.team/reports/premortem-<milestone>.md` (≤ 30 lines).
- Prompt for agents: "Assume <milestone> slipped 6 weeks and shipped with poor reviews. List the
  5 most likely causes in your discipline, each with an observable early signal."

## Other techniques (pick when relevant)
- Assumption audit: list plan assumptions; each with "how we'd know it's false" and date.
- Monte Carlo schedule risk: run forecast with and without top risks firing (add their delay
  distribution) to size buffer.
- Expected Monetary Value: EMV = P × cost impact; sum EMV of accepted risks ≈ contingency reserve.
- Risk burndown: total score of open risks per sprint should trend down in pre-production;
  if flat, the plan isn't retiring risk.
- Tripwires: pre-agreed decision points ("if D7 < 10% by soft-launch week 6, pivot or kill").

## Anti-patterns
- Register written once, never reviewed → top 10 in every status report.
- Vague risks ("tech risk") → cause → event → impact sentence or reject.
- All mitigations "monitor" → each red risk needs an action that changes P or I.
- Owner = "team" → one named role owner.
- Ignoring opportunities → log upside risks too (platform featuring, viral mechanic).
- Hiding risks to keep status green → RAG derives from register (any red risk without plan = amber+).

## Sources
- PMI, "PMBOK Guide" 8th ed., 2025 (risk performance domain) https://www.pmi.org/standards/pmbok
- PMI, "The Standard for Risk Management in Portfolios, Programs, and Projects", 2019.
- Gary Klein, "Performing a Project Premortem", Harvard Business Review, Sept 2007 https://hbr.org/2007/09/performing-a-project-premortem
- Clinton Keith, "Agile Game Development", 2nd ed., 2020 (risk-first pre-production).
- Tom DeMarco & Timothy Lister, "Waltzing with Bears: Managing Risk on Software Projects", 2003.
