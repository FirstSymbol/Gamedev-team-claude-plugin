# Casual / puzzle / match-3 level design

## Level parameters (match-3 example; adapt for other puzzle types)
| Parameter | Typical lever | Effect on difficulty |
|---|---|---|
| Colours (tile types) | 4–6 | more colours → fewer matches/cascades → much harder (usually strongest lever) |
| Move limit / timer | per objective | −1 move ≈ −2 pp completion on average; removing moves hurts more than adding helps (Tactile data) |
| Objective | score, collect N, clear layer, drop items, free cells | clear/drop objectives with far targets are harder |
| Blockers | layers, spreading, fixed vs falling, need special/booster | multi-layer & spreading blockers raise variance |
| Board shape | size, holes, isolated pockets, portals | pockets/bottlenecks cut cascade potential |
| Spawn/drop rules | colour weights, spawners, pre-placed specials | weights tune luck; pre-placed specials ease starts |
| Seed | fixed vs random start | fixed seeds make difficulty consistent but solvable by guides |
- Store each level as data (JSON/SO), versioned, with stable `levelId` — never rename.
```json
{ "levelId": "L0123", "version": 3, "board": {"w": 9, "h": 9, "mask": "<...>"},
  "colors": 5, "moves": 24, "objectives": [{"type": "collect", "item": "acorn", "count": 4}],
  "blockers": [{"type": "ice", "layers": 2, "cells": "<...>"}],
  "spawn": {"weights": [1,1,1,1,1]}, "difficultyTarget": {"aps": 3.0, "band": "hard"} }
```

## Difficulty metrics
| Metric | Definition | Use |
|---|---|---|
| Pass rate (win rate per attempt) | successes / attempts | primary difficulty signal |
| APS (attempts per success) | attempts / successes | intuitive per-level cost; ≈ 1/pass rate |
| First-attempt win rate | wins on 1st try / players | early-game and tutorial levels |
| Churn at level | players whose last session ended stuck on L / players reaching L | finds churn walls |
| Moves-left distribution | moves remaining at win; progress at loss | "near-miss" vs "hopeless" losses |
| Time to pass / time to abandon | wall-clock per level | King uses these to score "fun" |
| Booster/extra-moves use | per attempt | monetisation pressure (economy-monetization-designer) |
- King (GDC coverage): fun and difficulty are measured separately; harder levels should
  be shorter; they repeatedly identify the ~100 least fun levels and fix them. Level 65 was
  highest-converting and highest-churn: making it easier retained players longer.
- Tactile (Lily's Garden, 4,000 levels): the distribution of moves used to win is well
  modelled by a negative binomial; fitted CDF at the move limit ≈ completion rate; lets you
  predict the effect of changing the move limit before release.

## Difficulty sequencing
- Waves, not ramps: a hard level is usually followed by an easier one (King). Illustrative
  10-level cycle (tune per title): E E M E M H E M H SH, where SH is a labelled
  "super hard" level.
- Illustrative target bands (heuristics, verify with your data):

| Band | APS target | First-attempt win | Where |
|---|---|---|---|
| Tutorial/easy | 1.0–1.3 | ≥ 80% | levels 1–20, after hard levels |
| Medium | 1.5–2.5 | 40–70% | bulk of the sequence |
| Hard | 3–6 | 15–35% | ~1 per 5–10 levels |
| Super hard | 6–15 | < 15% | episode ends; labelled; shorter |
- Early-game: near-guaranteed wins while teaching; first real fail typically after the
  core is learned (verify timing via FTUE funnel; lead-game-designer owns FTUE targets).
- Complexity staircase (King): newer players meet simpler blockers; new blockers are added
  only when the existing set can't support a desired level type; new levels mix recent and
  older blockers; late-game difficulty comes from objectives, tight constraints and layouts
  more than blocker count.
- New element intro: level N teaches (forced/hinted move, easy) → N+1..N+3 develop (easy/medium)
  → combine with known elements → first hard use ≥ 3 levels after intro.

## Estimating difficulty before release
- Bots: run N ≥ 1,000 simulated attempts per level with a heuristic/greedy or MCTS agent →
  predicted pass rate. Calibrate bot→human with a regression on live levels (bot pass rate
  vs human pass rate), then predict new levels. Bots spot outliers but not feel; still
  playtest (King, Tactile).
- Request from unity-developer: headless level runner (EditMode/batch), seeded RNG,
  CSV output `levelId, attempt, win, movesUsed, objectiveProgress`.
- Designer gate: predicted APS within ±25% of target band (heuristic) before shipping a batch.

## Live tuning loop
1. Ship level batch with targets → 2. after enough attempts (data-analyst sets threshold)
   compare APS/churn vs target → 3. adjust moves/colours/blockers (one lever per level per
   pass) → 4. remote-config the new version (bump `version`) → 5. track churn and
   monetisation guardrails together.
- Fix churn walls first (high churn + APS far above band), then "unfun" levels (high
  time-to-abandon or long durations), then outliers in easy bands.

## Ethics & compliance
- Every level must be beatable without paid boosters within reasonable attempts; publish
  "hard" labels instead of hidden spikes. No per-player hidden difficulty raises tied to
  spend likelihood. Extra-move offers and near-miss presentation → economy-monetization-
  designer + compliance-advisor (near-miss design is a gambling-regulation concern).

## Other casual formats (quick rules)
- Merge: board space is the pressure; difficulty = order requirements vs spawn supply;
  watch for unwinnable boards (always provide a sink: sell/storage).
- Block/tile puzzles: guarantee solvability (generator + solver); difficulty = branching
  factor and dead-end depth.
- Word/trivia: difficulty = word frequency/obscurity; use frequency lists; localize per language.
- Hyper-casual runners: chunk-based level generation; difficulty = speed + obstacle density
  + pattern novelty; first 30 s must be winnable by anyone.

## Sources
- mobilegamer.biz, "How King defines a 'good' Candy Crush Saga level – and constantly prunes the bad ones" https://mobilegamer.biz/how-king-defines-a-good-candy-crush-saga-level-and-why-it-constantly-prunes-the-bad-ones/
- PocketGamer.biz, "Crafting Candy Crush's difficulty: Blockers, level design, AI and the complexity staircase" https://www.pocketgamer.biz/crafting-candy-crushs-difficulty-blockers-level-design-ai-and-the-complexity-staircase/
- Kristensen, Valdivia, Burelli (ITU Copenhagen / Tactile Games), "Statistical Modelling of Level Difficulty in Puzzle Games" (2021) https://arxiv.org/abs/2107.03305
- GDC news, King's method for balancing match-3 difficulty https://gdconf.com/news/come-gdc-summer-and-learn-kings-new-method-balancing-match-3-game-difficulty
