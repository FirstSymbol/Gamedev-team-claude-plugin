# Systems, progression, difficulty

## Systems doc essentials (`10-systems/<system>.md`)
- Purpose (aesthetic + pillar), inputs/outputs (resources in/out), player decisions, rules,
  states, parameters (table), interactions with other systems, failure modes, telemetry.
- Interaction matrix across systems (rows affect columns): mark `+` amplifies, `-` dampens,
  `$` touches economy (→ economy-monetization-designer). Review any cell with feedback loops.
- Feedback loops: positive (rich get richer → snowball; add catch-up, caps, decay) vs
  negative (stabilising → rubber-banding; keep skill expression).

## Progression curve formulas
Design **time first, XP second**: target play time per level `T(L)`, expected XP rate
`R(L)` (XP/min at that level) → `XPnext(L) = T(L) · R(L)`. Keeps pacing stable when rewards change.

| Shape | XP to next level | Total to reach L | Feel / use |
|---|---|---|---|
| Linear | `a + b(L-1)` | `aL' + bL'(L'-1)/2`, L'=L-1 | casual, short games, battle-pass tiers (often flat) |
| Power | `a · L^k` (k≈1.5–2.5) | `≈ a·L^(k+1)/(k+1)` | most RPGs; steady slowdown |
| Exponential | `a · r^(L-1)` (r≈1.05–1.2) | `a(r^(L-1)-1)/(r-1)` | long-tail MMO/idle; needs content scaling |
| Logistic (S) | for power/unlocks: `Pmin+(Pmax-Pmin)/(1+e^(-k(L-L0)))` | — | slow start, fast middle, plateau (soft cap) |
- Ranges for k and r are practitioner heuristics; always plot cumulative time-to-level.
- Worked: `T(L) = 3 · 1.15^(L-1)` min → finishing L10 ≈ 61 min cumulative, L20 ≈ 5.1 h.
- RuneScape: `XP(L) = floor(¼ · Σ_{l=1}^{L-1} floor(l + 300·2^(l/7)))`; doubles every 7
  levels (r = 2^(1/7) ≈ 1.104); L92 ≈ half of L99 (13,034,431 XP).
- Pokémon growth groups (total XP at level n): Fast `0.8n³` (800k at 100), Medium Fast `n³`
  (1M), Medium Slow `1.2n³ − 15n² + 100n − 140` (1,059,860), Slow `1.25n³` (1.25M).
  Shows that one family (cubic) can yield distinct pacing per content tier.

```python
# gen_xp_table.py — write the curve, not the rows. Output CSV → Unity importer → SO.
import csv, math
def minutes(L): return 3 * 1.15 ** (L - 1)          # target time on level L
def xp_rate(L): return 60 * (1 + 0.08 * (L - 1))      # XP/min at level L (from reward tables)
with open("xp_table.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["level", "xp_to_next", "cum_minutes"]); cum = 0
    for L in range(1, 51):
        cum += minutes(L)
        w.writerow([L, round(minutes(L) * xp_rate(L), -1), round(cum, 1)])
```
- Round displayed numbers (to 10/50/100) for readability; keep the formula as source of truth.

## Unlock pacing
- Map each unlock (feature, mode, item tier, area) to cumulative play time and session #.
  Heuristics (tune per genre, verify with telemetry):
  - First session: core loop only + 1 meta tease; one new concept at a time.
  - Sessions 2–5: one new system per session; each introduced with a guaranteed win.
  - After week 1: unlock cadence slows; live content/events carry novelty (liveops-manager).
- Unlock table columns: `unlock | gate (level/quest/time) | target cum. minutes | session # |
  teaches | pillar`. Check no two major systems unlock in the same session early.
- Gating types: level gate, content gate (beat boss), skill gate (ability), time gate
  (cooldown — F2P; coordinate with economy), social gate (team) — avoid stacking two hard gates.
- Pre-announce locked content (visible locks + "unlocks at level 8") to create goals.

## Difficulty curves
- Track two curves: player power `P(L)` (from progression/gear) and content power `E(L)`.
  Perceived difficulty `D = E/P` (or required skill × E/P). Plot both; the gap is the design.
- Shape: waves/sawtooth, not a straight ramp — intro (easy, teach) → develop → test (spike)
  → relief (breather/reward). Bosses/chapter ends as spikes, next level noticeably easier.
- Heuristic bands (verify by telemetry): normal content D ≈ 0.8–1.1, spikes 1.2–1.5, never
  a spike right after a new mechanic is introduced.
- Measure: attempts per success, fail reasons, quit-after-fail rate, time-to-complete
  distribution (not just mean). For puzzle levels see level-designer's casual reference.

## Dynamic difficulty adjustment (DDA)
| Approach | Example | Pros | Cons / rules |
|---|---|---|---|
| Player-chosen difficulty | Easy/Normal/Hard | transparent | wrong first pick; allow change any time |
| Assist options | Celeste Assist Mode (game speed, invincibility) | respectful, accessible | can undercut challenge pillar; frame neutrally |
| Supply-side adjustment | Hamlet (Hunicke, Half-Life): tweak health/ammo supply when failure predicted | invisible | bound it; log it |
| Pacing director | Left 4 Dead AI Director: build-up → peak → relax by player "intensity" (Booth, 2009) | dynamic pacing | complex; tune extensively |
| Rubber-banding | kart racers: better items for trailing players | keeps races close | feels unfair if visible; limit in competitive |
| Matchmaking (MMR) | PvP skill-based matching | fair competition | not DDA inside a match; never handicap in ranked |
- Rules: adjust slowly and within bounds (e.g. ±10–20% of a parameter, heuristic); never
  change mid-action visibly; never in ranked PvP; log DDA state in telemetry; don't tune
  DDA to raise spend (ethics + regulator scrutiny — compliance-advisor if spend-linked).
- Fail-forward alternatives: checkpoints, hints after N fails, optional assist after N fails.

## Long-term structures
- Soft caps (diminishing returns: `effective = cap · (1 − e^(−x/cap))`), hard caps (level cap
  + horizontal progression), prestige/rebirth (reset for permanent multiplier — idle games),
  catch-up (XP boosts below median level), seasonal resets (battle pass tiers usually linear XP).
- Power creep control: new content matches the curve, not the best existing item
  (balancing.md cost curves).

## Sources
- Schreiber & Romero, "Game Balance" (CRC Press, 2021) — progression and curves chapters
- Old School RuneScape Wiki, "Experience" https://oldschool.runescape.wiki/w/Experience
- Bulbapedia, "Experience" (growth rates) https://bulbapedia.bulbagarden.net/wiki/Experience
- Hunicke & Chapman, "AI for Dynamic Difficulty Adjustment in Games" (Hamlet) https://users.cs.northwestern.edu/~hunicke/pubs/Hamlet.pdf
- Booth, "The AI Systems of Left 4 Dead", AIIDE 2009 keynote (Valve) (verify: slides on valvesoftware.com publications)
- Chen, "Flow in Games (and Everything Else)", CACM 2007
