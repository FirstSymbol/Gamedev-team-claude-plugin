# GDD structure, ownership, change control

## Pick the document type
| Doc | Size | Audience | Use when | Owner |
|---|---|---|---|---|
| One-pager / pitch | 1 page | stakeholders, whole team | concept, greenlight, onboarding | lead-game-designer |
| Living modular GDD | index + sections, each ≤ ~3 pages | team | pre-production → live ops | section owners |
| Feature spec | 1–4 pages | engineers, QA, art | anything entering a sprint | feature's designer |
| One-page diagrams (Librande) | 1 poster | team wall / review | systems overview, level maps, flows | any designer |
| Balance sheet / data table | spreadsheet / CSV | designers, devs | tunables, curves, content lists | game-designer / economy |
| ADR | ≤ 1 page | team | irreversible/pillar-level decisions | decider |
- Rules: a spec that doesn't fit its size limit is two specs. Link, never copy, between docs.
  Numbers live in data tables (single source), not prose.
- Librande (GDC 2010, "One-Page Designs"): documents are read when they're visual, short and
  posted where people work; favour maps, flowcharts, matrices over paragraphs.

## Modular GDD layout (`.team/specs/gdd/`)
```
00-index.md                 TOC: section | owner | status | updated | depends-on
01-vision.md                one-pager (templates/one-pager.md)
02-core-loop.md             loops (core/meta/session), verbs, fail/win states   game-designer
03-ftue.md                  first session beats, funnel targets                lead + ux-ui-designer
10-systems/<system>.md      one file per system (combat, crafting, social…)   game-designer
20-progression.md           XP/unlock curves, difficulty curve                 game-designer
30-levels/00-plan.md        level list, sequence, difficulty map              level-designer
30-levels/<level-id>.md     level docs                                        level-designer
40-narrative/               premise, world, characters, quests, tone bible     narrative-designer
50-economy.md               index → `.team/specs/economy/` (model, offers, odds) economy-monetization-designer
60-ux.md                    index → `.team/specs/<feature>/ux/` flows, HUD     ux-ui-designer
70-art-audio.md             links to art-director style guide                 art-director
80-liveops.md               index → `.team/specs/liveops/` events, seasons    liveops-manager
85-tech-constraints.md      platform limits, netcode model; budgets → `architecture/perf-budget.md` tech-lead-architect
90-open-questions.md        Q | owner | due | answer
(feature specs live in `.team/specs/<feature>/design.md`; list them in 00-index.md)
data/                       CSV/JSON tables referenced by specs (versioned)
```
- Drop sections the game doesn't need (no `50-economy.md` for a premium narrative game);
  never leave empty stubs > 1 milestone.
- Multiplayer games add `15-multiplayer.md` (modes, authority, matchmaking rules) co-owned
  with multiplayer-network-engineer. Casino games keep math (RTP, paytables, PAR sheets) in `.team/specs/economy/`
  owned by economy-monetization-designer + compliance-advisor review.

## Section header (every GDD file)
```
# <Section>  | owner: <role> | status: draft|review|approved|built|deprecated | updated: YYYY-MM-DD
Pillars served: <P1, P3>   Depends on: <paths>   Related ADRs: <paths>
## Changelog (last 5)  - YYYY-MM-DD <who>: <what changed, why>
```

## Ownership (RACI-lite)
| Section | R (writes) | A (approves) | C (consulted) |
|---|---|---|---|
| Vision/pillars | lead-game-designer | human / product-manager | all leads |
| Core loop, systems, progression | game-designer | lead-game-designer | economy, unity-developer |
| Levels | level-designer | lead-game-designer | game-designer, art-director |
| Narrative/text | narrative-designer | lead-game-designer | ux-ui-designer, localization |
| Economy/monetization | economy-monetization-designer | lead-game-designer + product-manager | compliance-advisor, data-analyst |
| UX flows | ux-ui-designer | lead-game-designer | narrative-designer |
| Tech constraints | tech-lead-architect | tech-lead-architect | unity-developer |

## Status lifecycle & change control
- draft → review (design review held) → approved (dev may build) → built (matches build;
  QA verified) → deprecated (kept, marked, linked to replacement).
- Changing an `approved`/`built` section: changelog line + notify dependants (handoff) +
  update status of affected feature specs back to `review` if rules changed.
- Pillar or genre-level change: ADR + full index review. Numbers-only tweak: data table
  commit + changelog line, no review needed unless it shifts economy.

## Writing rules (for all designers)
- Lead with intent (player experience goal), then rules, then numbers (link to table).
- Use player verbs and observable outcomes; ban "should feel fun".
- Every rule states: trigger, effect, duration, exceptions. Every number has unit + range.
- Mark unknowns `TBD(<owner>, <date>)`; mark assumptions `ASSUMPTION:`.
- Prefer tables, state diagrams (Mermaid allowed), annotated mockups over prose.
- Include telemetry: which events prove the feature works (hand to data-analyst).

## Feature spec vs GDD section
- GDD section = *what the system is* (stable reference). Feature spec = *what we build this
  milestone* (slice, acceptance criteria, out of scope). Feature specs link to GDD sections;
  after "built", fold durable rules back into the GDD section.

## Index example (`00-index.md`)
```
| Section | Owner | Status | Updated | Depends on |
|---|---|---|---|---|
| 01-vision | lead-game-designer | approved | 2026-03-02 | - |
| 02-core-loop | game-designer | review | 2026-03-10 | 01 |
| 50-economy/currencies | economy-monetization-designer | draft | 2026-03-11 | 02, 20 |
```

## Sources
- Librande, "One-Page Designs", GDC 2010 https://gdcvault.com/play/1012785/One-Page
- Game Developer, "Video: One-page designs" https://www.gamedeveloper.com/design/video-one-page-designs
- Schell, "The Art of Game Design: A Book of Lenses", 3rd ed. (CRC Press, 2019) — chapter on design documents
- Rogers, "Level Up! The Guide to Great Video Game Design", 2nd ed. (Wiley, 2014) — GDD and one-sheet/ten-pager formats
- Fullerton, "Game Design Workshop", 4th ed. (CRC Press, 2018) — design documentation chapter
