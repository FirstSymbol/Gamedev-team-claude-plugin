# Balancing (methodology, formulas, simulation)

## Spreadsheet structure (Google Sheets/Excel → CSV → Unity SO import)
| Sheet | Contents | Rule |
|---|---|---|
| `Globals` | named constants (base HP, crit mult, tick rate) | every formula references names, no literals |
| `Entities` | one row per unit/item/card; raw stats | stable string `id` column (never row index) |
| `Derived` | DPS, EHP, TTK, value score per row | formulas only; locked |
| `Curve` | target value per tier/cost/level | formula from cost curve |
| `Deviation` | `(value − target)/target` | conditional format: > ±10% red (heuristic) |
| `Sim` | pasted/imported sim outputs | date + build + seed noted |
| `Changelog` | date, change, reason, expected effect | one line per tuning pass |
- Export `Entities` as CSV (UTF-8, `.` decimal) to `.team/specs/gdd/data/`; unity-developer
  imports into ScriptableObjects via editor tool (see unity-developer architecture refs).

## Core combat formulas
- `DPS = dmgPerHit × hitsPerSec × hitChance × (1 + critChance × (critMult − 1))`
- Flat armor (League of Legends style): damage taken × `100 / (100 + armor)` →
  `EHP = HP × (1 + armor/100)`; linear EHP per armor point = no runaway, diminishing % reduction.
- Percentage reduction: `EHP = HP / (1 − DR)`; stack multiplicatively: `1 − Π(1 − DR_i)`.
  Cap DR (e.g. ≤ 75–80%) or EHP explodes as DR → 1.
- Shots to kill `STK = ceil(EHP / dmgPerHit)`; `TTK = (STK − 1) / fireRate` (first shot at
  t=0) `+ reloads × reloadTime`. Example: 100 HP, 25 dmg, 600 RPM (10/s) → STK 4 →
  TTK 0.3 s. Headshots: recompute STK with multiplier; publish body/head TTK pairs.
- Duel outcome: A wins if `TTK(A→B) < TTK(B→A)` (deterministic); with spread/accuracy use sim.
- Healing/regen in duels: effective DPS = `DPS_attacker − HPS_defender`; if ≤ 0, unkillable — flag.

## Cost curves (Schreiber, Game Balance Concepts)
1. Express every cost and benefit in one central resource (mana, gold, power points).
2. Choose curve shape: increasing (big items disproportionately expensive), decreasing
   (rewards saving — then a 2× cost item must be > 2× as good), or stepped at thresholds.
3. Cost the simplest single-effect objects first; derive per-stat/per-keyword values.
4. Solve unknowns algebraically from objects with one unknown; estimate conditional effects
   as `benefit × P(condition)`.
5. Score all objects; classify above/on/below curve; fix by cost or by benefit.
- Worked (Magic 2011 analysis): 1 per power/toughness, first coloured mana costs 2, +1
  threshold at 5+ mana; a blue 4/3 (benefit 1 + 4 + 3 = 8) → balanced cost 5 mana (1 coloured).
- Linear value model: `value = Σ w_i · stat_i`; fit weights by least squares on content you
  trust as balanced; outliers = candidates. Re-fit after each major patch.

## Intransitive balance (counters)
- Payoff matrix (row player, zero-sum). Solve for the mixed-strategy equilibrium: opponent
  mix makes all your options' expected values equal.
- Worked: R beats S for +2, P beats R +1, S beats P +1:
  `EV(R) = −p + 2s`, `EV(P) = r − s`, `EV(S) = −2r + p` → equal ⇒ `r = 0.25, p = 0.5, s = 0.25`.
  Buffing Rock's win makes **Paper** (its counter) the most played — expect this in meta shifts.
- Use for unit/class/card-type triangles; target equilibrium shares near equal unless a type
  is meant to be niche. Check with sim or telemetry pick rates.
- Rock-paper-scissors-plus: add a soft modifier (terrain, cost, timing) so counters are not
  absolute (e.g. counter wins 65–75% not 100%; heuristic).

## Probability quick refs
- P(≥ 1 success in n tries) = `1 − (1 − p)^n`; p=5%, n=20 → 64%. Median tries =
  `ln 0.5 / ln(1 − p)` (p=5% → ~14). Expected tries = `1/p`.
- Bad-luck protection (pity counter, increasing p) caps variance; any paid random reward →
  economy-monetization-designer + compliance-advisor (odds disclosure).
- Use Monte Carlo for anything with > 2 interacting random variables.

## Simulation
- Prefer one source of truth: game rules in a plain C# class (no MonoBehaviour), run by both
  the game and an EditMode test/batch sim. Python for quick exploratory models.
```csharp
// EditMode sim: same CombatResolver the game uses (plain C#, seeded RNG).
[Test] public void Knight_vs_Archer_WinRate_InBand() {
    var rng = new System.Random(12345); int wins = 0; const int N = 10000;
    for (int i = 0; i < N; i++)
        if (CombatResolver.Duel(Units.Knight, Units.Archer, rng).Winner == Side.A) wins++;
    float wr = wins / (float)N;
    Assert.That(wr, Is.InRange(0.45f, 0.55f), $"Knight WR {wr:P1}");
}
```
```python
import random
def duel(a, b, rng):                      # a, b: dict(hp, dmg, rate, acc)
    ha, hb, t = a["hp"], b["hp"], 0.0; ta, tb = 0.0, 0.0
    while ha > 0 and hb > 0:
        if ta <= tb: hb -= a["dmg"] * (rng.random() < a["acc"]); ta += 1 / a["rate"]
        else:        ha -= b["dmg"] * (rng.random() < b["acc"]); tb += 1 / b["rate"]
    return hb <= 0
rng = random.Random(1); n = 10000
print(sum(duel(dict(hp=100,dmg=25,rate=2,acc=.8), dict(hp=80,dmg=15,rate=3,acc=.9), rng) for _ in range(n)) / n)
```
- Sim output → `Sim` sheet + `.team/reports/balance-<topic>.md`: setup, seed, N, results,
  deviations, proposed changes. N ≥ 10,000 for ±1% precision on a ~50% rate (95% CI ≈ ±1%).

## Telemetry-driven tuning
- Metrics: win rate, pick/ban rate, usage by skill bracket, TTK distribution, level pass
  rate/attempts, resource earn vs spend per day, time-to-milestone vs target.
- Competitive heuristic: per-character/faction win rate within ~45–55% at the relevant
  skill bracket; high pick + high win = overtuned; low pick + high win = niche/skill-heavy
  (verify thresholds with data-analyst for sample size).
- Process: hypothesis → one change per variable → remote-config/A/B where possible (Unity
  Remote Config or backend flags) → guardrail metrics (retention, revenue, session length)
  → read after a pre-agreed sample/time → keep/revert. data-analyst owns test design and stats.
- Segment before concluding (new vs veteran, platform, spender tier) — aggregates hide
  opposite effects (Simpson's paradox).
- Prefer buffing underused options over nerfing popular ones when both fix the gap (players
  react worse to nerfs; practitioner consensus).

## Sources
- Schreiber, "Game Balance Concepts" (2010), Level 3: Transitive Mechanics and Cost Curves https://gamebalanceconcepts.wordpress.com/2010/07/21/level-3-transitive-mechanics-and-cost-curves/
- Schreiber & Romero, "Game Balance" (CRC Press, 2021) — transitive/intransitive chapters, payoff matrices
- League of Legends Wiki, "Armor" (damage reduction formula) https://leagueoflegends.fandom.com/wiki/Armor
- Schreiber, "Math for Game Programmers: Balancing TCGs With Algebra, Not Magic", GDC https://gdcvault.com/play/1023564
