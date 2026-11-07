# Agile delivery (Scrum, Kanban, agent-team cadence)

## Scrum Guide 2020 essentials
| Element | Rule |
|---|---|
| Pillars / values | Transparency, inspection, adaptation; commitment, focus, openness, respect, courage |
| Accountabilities | Product Owner (backlog value, Product Goal), Scrum Master (effectiveness, impediments), Developers (Sprint Backlog, DoD quality). One team, no sub-teams, typically ≤ 10 people |
| Sprint | ≤ 1 month, fixed length, new Sprint starts immediately; cancel only if Sprint Goal obsolete (PO decides) |
| Sprint Planning | ≤ 8 h for 1-month Sprint. Topics: Why valuable (Sprint Goal)? What can be Done? How? |
| Daily Scrum | 15 min, Developers, progress toward Sprint Goal, adapt plan |
| Sprint Review | ≤ 4 h; inspect Increment with stakeholders, adapt Product Backlog; not a gate/demo-only |
| Retrospective | ≤ 3 h; improve quality/effectiveness; pick improvements, may add to next Sprint Backlog |
| Artifacts → commitment | Product Backlog → Product Goal; Sprint Backlog → Sprint Goal; Increment → Definition of Done |
- Shorter sprints scale timeboxes down proportionally (2-week sprint: planning ≤ 4 h, review ≤ 2 h, retro ≤ 1.5 h).
- Refinement is ongoing (not an event); keep ~10% of capacity for it.
- Game teams (Keith): 2-3-week sprints; "releases" of 2-4 sprints toward a milestone; a playable
  build every sprint; reviews are playtests, not slide decks.

## Kanban Guide (2025.5) essentials
- Three practices: define and visualize the workflow; actively manage items in the workflow; improve the workflow.
- Definition of Workflow (DoW) must state: work item type, start/finish points, states between,
  how WIP is controlled, explicit policies per state, Service Level Expectation (SLE).
- Four mandatory flow measures:
| Measure | Definition | Use |
|---|---|---|
| WIP | Items started, not finished | Limit it; the main control lever |
| Throughput | Items finished per unit time | Forecasting (Monte Carlo) |
| Work Item Age | Start → now, for unfinished items | Daily: act on items approaching SLE |
| Cycle Time | Start → finish | Set SLE (e.g. 85% of items done in ≤ 8 days) |
- Little's Law (averages, stable system): avg Cycle Time = avg WIP / avg Throughput. Halving WIP
  at constant throughput halves cycle time.
- WIP limit starting point: ~team size per column or (people × 1.0-1.5) for the board; lower
  until it hurts slightly, then hold. Blocked items count toward WIP.
- Pull, don't push: finish before starting ("stop starting, start finishing").
- Choose Kanban over Scrum for: live-ops/support, content production pipelines (art, levels),
  bug fixing during beta, and agent teams where work arrives continuously.

## Ceremonies adapted for an AI-agent team
| Ceremony | Agent-team form | Owner | Artifact |
|---|---|---|---|
| Planning | Producer reads backlog + capacity; drafts Sprint Goal + selected items; product-manager confirms value; human approves goal | producer | `.team/specs/plan/sprint-NN.md` |
| Daily | Run `team_status.py`; check aging items, blocked rows, WIP vs limits; re-dispatch or escalate | producer/orchestrator | `.team/status.md` rows |
| Refinement | BA/game-designer split epics into stories meeting DoR; tech-lead sizes; ≤ 2 sprints of ready backlog | product-manager | `.team/specs/backlog/` |
| Review | Demo = artifacts + build/test evidence vs Sprint Goal; human inspects; backlog updated | producer | review section in sprint file |
| Retro | Read handoffs/blocked returns; list 3 keep / 3 change; turn ≤ 2 into concrete rules (skill notes, DoR tweaks) | producer | `.team/reports/retro-NN.md` |
- Agent "sprint" = an increment of work the human can inspect (often 1 session to a few days).
  Keep the Sprint Goal; drop the calendar ritual.
- Spawning is capacity: plan waves of ≤ 3-4 parallel agents; each item has one owner role.
- Human time is the bottleneck: batch decisions; one review checkpoint per goal.

## Definition of Ready (story/task)
- [ ] Value stated (who, why) and linked to goal/PRD; acceptance criteria testable.
- [ ] Dependencies identified and available (API contract, art, design numbers).
- [ ] Sized ≤ half a sprint (or ≤ SLE in Kanban); spikes for unknowns done.
- [ ] UX/design inputs attached if user-facing; analytics events listed if measurable.
- [ ] Owner role assigned; no open blocking questions.
## Definition of Done (increment) — extend team-protocol DoD
- [ ] AC met and verified by someone other than the author (qa-engineer or tests).
- [ ] Code reviewed, builds on CI, tests green, no new analyzer warnings.
- [ ] Runs on target min-spec / platforms; perf budget not regressed.
- [ ] Telemetry events firing; loc strings externalized; docs/release notes updated.
- [ ] Integrated in the main branch build; playable/usable in the sprint build.
- Game-specific: DoD differs per stage. Prototype DoD = "playable, learn something"; production
  DoD = shippable quality. Write the stage on the DoD.

## Backlog hygiene
- Ordered (not just prioritized); top 1-2 sprints ready (DoR), next 1-2 roughly sized, rest coarse.
- Size cap: nothing larger than half a sprint enters a sprint; XL → split by workflow step,
  rule, data variation, platform, or happy/unhappy path.
- Prune: items untouched > 90 days → delete or archive (they come back if they matter).
- Bugs: triage within 1 working day; severity (S1 crash/data loss, S2 major, S3 minor, S4 cosmetic)
  × frequency → priority; S1 interrupts the sprint.
- Tech debt items carry a cost-of-delay note; reserve 10-20% capacity (agreed with tech-lead-architect).
- Track "unplanned work %" per sprint; > 25% → fix intake/triage before adding capacity.

## Scaled coordination (multiple teams/streams)
- Scrum of Scrums: one rep per team, daily/2-3×/week, 15 min: dependencies, impediments, integration risk.
- Shared cadence: same sprint boundaries; joint review/playtest of an integrated build.
- Big-room / PI planning (SAFe-style) for 8-12 week horizons: teams plan, expose dependencies on a
  board, confidence vote (fist of five); producer owns the dependency board.
- Feature teams (vertical, own a player-facing feature) over component teams; component/shared
  teams (engine, backend platform, tools) serve via SLAs and explicit intake.
- Strike teams for short goals (e.g., FTUE overhaul) with a clear exit date.
- Agent mapping: each lead = a "team"; orchestrator = scrum of scrums; dependencies live in
  `.team/specs/plan/raid.md`.

## Health metrics (watch, don't target)
| Metric | Healthy signal | Act when |
|---|---|---|
| Sprint Goal hit rate | ≥ 80% of sprints | < 60% → over-commit or unstable inputs |
| Cycle time P85 | stable or falling | rising 3 periods → WIP too high/blocked |
| Work item age | < SLE | item > SLE → swarm or split today |
| Carry-over | < 20% of committed | > 30% → slice smaller |
| Escaped defects | trending down | spike → DoD gap |
| DORA (if shipping software) | deploy freq, lead time, change fail rate, recovery time, rework rate | see tech-lead-architect |

## Sources
- Ken Schwaber & Jeff Sutherland, "The Scrum Guide", Nov 2020 https://scrumguides.org/scrum-guide.html
- Daniel Vacanti & John Coleman, "The Kanban Guide", May 2025 https://kanbanguides.org/the-kanban-guide/
- ProKanban, "The Kanban Pocket Guide, Ch. 6: Basic Metrics of Flow" https://prokanban.org/blog/the-kanban-pocket-guide-chapter-6-the-basic-metrics-of-flow
- Clinton Keith, "Agile Game Development: Build, Play, Repeat", 2nd ed., 2020.
- Mike Cohn, "Agile Estimating and Planning", 2005 (story splitting, velocity ranges).
- DORA metrics guide https://dora.dev/guides/dora-metrics/
