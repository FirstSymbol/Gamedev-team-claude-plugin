# Casino math (practitioner reference)
Regulated real-money math must be certified by an accredited lab — see studio:domain-igaming
(references/rng-and-game-certification.md). This file is the designer's math toolkit.

## Definitions
| Term | Definition |
|---|---|
| RTP | long-run return to player = E[win] / bet (per bet configuration) |
| House edge (HE) | 1 - RTP |
| Hit frequency | P(win > 0) per spin |
| Win frequency | P(win > bet) — excludes "losses disguised as wins" (LDW: 0 < win ≤ bet) |
| Volatility (SD) | σ of win per unit bet; drives session swings |
| Volatility index | VI = z·σ (z = 1.645 at 90%, 1.96 at 95%); player return after n spins ≈ RTP ± VI/√n |
| Cycle | all reel-stop combinations = Π W_r (W_r = weighted stops on reel r) |
| PAR sheet | Probability Accounting Report: strips, paytable, combos, RTP split, hit freq, SD (templates/par-sheet.md) |
| Max win | largest single-game payout (x bet); exposure = max win × max bet |

## Core formulas
- Symbol probability on reel r: `p_r(s) = w_r(s) / W_r` (virtual-reel weights or physical strip counts).
- Line combination probability (independent reels): `P = Π_r p_r(s_r)`; count = `Π_r w_r(s_r)`.
- RTP = Σ_o P(o)·x_o, with x_o the pay in multiples of total bet (convert line pays: x = line pay × lines bet / total bet).
- Variance: `σ² = Σ_o P(o)·x_o² - RTP²`; SD = √σ². Report SD per bet configuration.
- Ways games (243/1024 ways): for each visible window, ways for symbol s paying k-of-a-kind =
  Π_{r=1..k} n_r(s), n_r = matching symbols (incl. wilds) visible on reel r, and n_{k+1} = 0.
  Enumerate windows (strip positions) in code; never hand-derive for certification.
- Feature split: `RTP = RTP_base + P(trigger) · E[feature win | trigger]` (all in x bet). Report each part.
- Free spins with retrigger: initial n spins, each spin retriggers +n with probability q:
  `E[spins] = n / (1 - n·q)` (valid if n·q < 1); `E[FS win] = E[spins] · RTP_fs_spin · multiplier`.
- Max-win cap: if raw outcomes exceed cap C, RTP_capped = RTP - Σ_{x_o>C} P(o)(x_o - C);
  document P(reaching cap) (e.g. "1 in 20M spins") and the capped RTP.
- Gamble/double-up: fair 50/50 gamble keeps RTP (EV 1.0 on the gambled amount) but raises SD;
  certify it separately.

## Progressive jackpots
- Contribution rate c (% of each bet to the meter, often 0.5-3%; verify per product).
  Seed S paid by operator (or from a reserve funded by part of c).
- Hit probability per spin p (fixed odds) or must-hit-by (mystery) value uniform in [S, cap].
- Mean jackpot when won: `E[J] ≈ S + c·b / p` (b = average bet; meter grows c·b per spin, mean 1/p spins).
- Jackpot RTP per spin: `RTP_jp = p·E[J]/b = c + p·S/b`. Total RTP = RTP_base + RTP_jp.
- Certification usually requires the minimum RTP to hold with the meter at seed (excluding external
  jackpots; GLI-19 §4.7.1); show base-only RTP and with-jackpot RTP.
- Wide-area/networked jackpots: contributions are liabilities → ledger accounts, reconciliation
  per period, disclose contribution rate and odds in game rules.

## Required numbers per game (all bet configurations)
- RTP (total, base, each feature, jackpot), hit frequency, win frequency, SD/VI, max win (x bet),
  P(max win), feature trigger rates (1 in N), average feature win, RTP at min/max bet and every
  line/ways setting (each must meet regulatory minimum; GLI-19: ≥ 75% unless regulator says otherwise).
- Jurisdiction floors/ceilings differ (verify per target: e.g. many EU regulators approve ~85-98%
  ranges; UK has no fixed minimum, RTP must be disclosed accurately).

## Exact first, simulation second
- Fixed reels, no player choice, no state → exact enumeration of the full cycle (combinatorial).
- Cascades, sticky/persistent state, player choice, collection meters, bonus buys → simulation
  with stated N, seed policy and confidence interval; labs re-run independently.
- Simulation size for precision ε at confidence z: `N = (z·σ / ε)²`.
| σ (x bet) | ±0.1% at 95% | ±0.1% at 99% | ±0.5% at 95% |
|---|---|---|---|
| 3 (low vol) | 3.5e7 | 6.0e7 | 1.4e6 |
| 7 (medium) | 1.9e8 | 3.3e8 | 7.5e6 |
| 20 (high) | 1.5e9 | 2.7e9 | 6.1e7 |
- So 10^7 spins verifies a medium-volatility game to only ~±0.44% (95%) — fine for smoke tests,
  insufficient as RTP evidence for high-volatility titles; use 10^8-10^10 (numpy/C#/parallel).
- Pass rule for regression tests: |RTP_mc - RTP_exact| ≤ z_0.995·σ/√N (99%); fail = bug in
  reels, paytable, evaluator or RNG mapping.

## Runnable example (stdlib Python): exact RTP + Monte Carlo with CI
```python
# Slot math: exact full-cycle RTP + Monte Carlo verification with 95%/99% CI. Python 3.9+, stdlib only.
import itertools, math, random, sys
REELS = [{"7": 1, "BAR": 3, "BELL": 5, "CH": 7, "-": 16}] * 3   # weighted stops per reel (32 each)
PAY3 = {"7": 1000, "BAR": 100, "BELL": 40, "CH": 20}             # pays in x total bet, 1 line
def pay(a, b, c):
    if a == b == c and a in PAY3: return PAY3[a]
    if {a, b, c} <= {"7", "BAR", "BELL"}: return 7                 # any mixed "bar-class"
    if a == b == "CH": return 5
    return 1 if a == "CH" else 0                                   # 1x = stake back (not a "win")
def exact():
    n = math.prod(sum(r.values()) for r in REELS); m1 = m2 = hit = 0
    for combo in itertools.product(*(r.items() for r in REELS)):
        w = math.prod(c[1] for c in combo); x = pay(*(c[0] for c in combo))
        m1 += w * x; m2 += w * x * x; hit += w * (x > 0)
    rtp = m1 / n; return rtp, math.sqrt(m2 / n - rtp ** 2), hit / n, n
def simulate(spins, seed=None):
    rng = random.Random(seed)  # MC check only; production RNG = certified CSPRNG on the server
    strips = [[s for s, k in r.items() for _ in range(k)] for r in REELS]
    s1 = s2 = 0
    for _ in range(spins):
        x = pay(*(rng.choice(st) for st in strips)); s1 += x; s2 += x * x
    mean = s1 / spins; sd = math.sqrt(s2 / spins - mean ** 2)
    return mean, sd, sd / math.sqrt(spins)
if __name__ == "__main__":
    rtp, sd, hit, cycle = exact()
    print(f"exact: cycle={cycle} RTP={rtp:.4%} hit={hit:.2%} SD={sd:.3f} VI90={1.645*sd:.2f}")
    n = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**6
    m, s, se = simulate(n, seed=42)
    print(f"MC {n:.0e}: RTP={m:.4%} 95%CI +/-{1.96*se:.4%} 99%CI +/-{2.576*se:.4%} "
          f"z={(m-rtp)/se:+.2f} -> {'PASS' if abs(m-rtp) <= 2.576*se else 'FAIL'}")
```
- Measured output (Python 3.12): exact RTP 95.5719%, hit 24.10%, SD 7.078; `python slot.py 1e7`
  → MC 95.6339%, 95% CI ±0.4435%, z = +0.27, PASS (≈ 24 s pure Python).
- Note the 1x cherry pay: counts toward hit frequency but is an LDW — UKGC RTS 14F forbids
  celebrating it; report win frequency separately.
- Production: port the evaluator to C# shared with the server (one implementation for game and
  sim), run 10^9 spins in parallel jobs, store seed + version + results in the PAR sheet.

## Table games house edge (standard rules, optimal play)
| Game / bet | House edge |
|---|---|
| European roulette (single zero), any bet | 2.70% |
| American roulette (double zero), most bets | 5.26% (top line 0-00-1-2-3: 7.89%) |
| Baccarat banker (5% commission) / player / tie 8:1 | 1.06% / 1.24% / 14.36% |
| Craps pass/come | 1.41% |
| Blackjack, basic strategy | ~0.3-0.6%, rules-dependent (3:2 vs 6:5 blackjack adds ~1.4%) |
| Video poker 9/6 Jacks or Better, optimal | 0.46% (RTP 99.54%) |
- Compute with Wizard of Odds calculators or exact combinatorics; rule variations change edge
  materially — document the rule set in the PAR/rules sheet. Live/RNG table games still need
  certified shuffles (studio:domain-igaming).

## Social casino coin economy
- Coins have no cash value and cannot be cashed out, transferred or sold (enforce in ToS and code:
  no P2P transfer, no gifting of purchased coins). Legal risk: Washington — Kater v. Churchill Downs
  (9th Cir. 2018) held virtual chips a "thing of value"; settled for USD 155M (Big Fish, 2020-21).
  Sweepstakes (redeemable) models are gambling-law territory → compliance-advisor.
- The slot house edge is the main sink: coins burned per spin = bet × (1 - RTP). RTP is a design
  lever (no regulatory floor in social; verify app-store/rating rules): it sets "time on device".
- Drift approximation: expected spins to bust ≈ balance / (bet × HE); variance makes the real
  distribution wide — simulate busts per archetype (median and p10 session length).
- Faucets and cadence (tune together): timed bonus (e.g. every 1-4 h), daily wheel/login streak,
  level-up rewards, missions/quests, friend gifts (cap per day), rewarded ads, piggy bank
  (accumulates from play, unlocks for a price), mail/comeback bonuses.
- Level-up reward ≈ k × average bet at that level × expected spins per level, with k chosen so
  free income covers a target share (e.g. 30-60%) of burn for non-payers (heuristic; simulate).
- Bet inflation: higher levels unlock higher max bet → coin values inflate; coin packs and
  bonuses must scale with level (pack size indexed to max bet) or purchases feel worthless.
- Purchase moments: "out of coins" offer, big-bet unlocks, new machine unlocks, piggy bank,
  event/collection completion. Keep price per coin honest across packs; no fake "was" prices.
- Ratings/platforms: social casino is rated 18 in PEGI/AU (table: `studio:release-platform-manager`
  (age-ratings)); no links/ads to real-money gambling from a
  social app (Google Play ads policy); 18+ audience gating is standard practice.

## Sources
- Robert C. Hannum, Anthony N. Cabot, "Practical Casino Math", 2nd ed. (UNR Institute for the Study of Gambling, 2005).
- Edward O. Thorp, "The Mathematics of Gambling" (Lyle Stuart, 1984).
- Wizard of Odds — house edge tables and slot math articles https://wizardofodds.com/gambling/house-edge/
- GLI-19 Standards for Interactive Gaming Systems v3.0 (2020), §3 RNG, §4.7 payout https://gaminglabs.com/wp-content/uploads/2024/06/GLI-19-Interactive-Gaming-Systems-v3.0.pdf
- UKGC RTS changes effective 2025-01-17 (14E/14F/14G/8A), summary https://www.harrishagan.com/reminder-changes-to-remote-games-design-requirements-come-into-force-on-17-january-2025/
- Kater v. Churchill Downs Inc., No. 16-35010 (9th Cir. 2018) https://law.justia.com/cases/federal/appellate-courts/ca9/16-35010/16-35010-2018-03-28.html
- Osborne Clarke on PEGI 2026 criteria https://www.osborneclarke.com/insights/games-loot-boxes-get-16-plus-age-rating-europe-under-pegi-overhaul
