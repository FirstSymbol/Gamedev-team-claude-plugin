# PAR sheet: <game name> v<math version> (<YYYY-MM-DD>)
Model: <real-money | social | sweepstakes>. Jurisdictions: <list>. Evaluator build: <commit/hash>.

## Configuration
- Grid <5x3>, paylines/ways <20 lines | 243 ways>, bet levels <list>, denominations <list>
- Max win cap <x bet>; RTP variants <96.1 / 94.0 / 92.0 ...> (each certified separately)

## Reel strips (per RTP variant, base and feature sets)
| Reel | Length | Symbol counts (or full strip ref: `<file>`) |
|---|---|---|

## Paytable (x total bet)
| Symbol | 3 | 4 | 5 | Notes (wild/scatter) |
|---|---|---|---|---|

## Results (per bet configuration)
| Metric | Value | Method (exact / MC N, seed) |
|---|---|---|
| RTP total | | |
| RTP base / free spins / bonus / jackpot | | |
| Hit frequency / win frequency (> bet) | | |
| SD, VI (90%) | | |
| Feature trigger (1 in N) / avg feature win | | |
| Max win, P(max win) | | |
| Min RTP across configurations | | must be ≥ regulatory floor |

## Verification
- MC: N <1e9>, RTP_mc <x>, 99% CI ±<y>, |diff| ≤ CI: <pass/fail>
- Lab: <GLI/BMM/iTech/eCOGRA>, certificate <id/pending>; RNG cert ref <id>

## Change log
| Version | Change | RTP impact | Re-cert needed |
|---|---|---|---|
