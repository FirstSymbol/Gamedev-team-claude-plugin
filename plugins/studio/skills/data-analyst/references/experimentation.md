# Experimentation (A/B tests in games and products)

## Pre-registration checklist (write before launch)
- Hypothesis: "Changing X for population P will move metric M by ≥ δ because …".
- Randomization unit: player ID (default). Session/device only for pure-UI stateless tests.
  Social/multiplayer/economy-trading features → cluster randomization (guild, region, match pool).
- Population + trigger: who is eligible; exposure logged at first divergent experience
  (analyze triggered users only, or dilute effect accordingly).
- Primary metric (one), secondary metrics, guardrails (crash-free rate, latency, refunds, CS
  tickets, revenue for non-monetization tests, RG flags in iGaming).
- α (0.05 two-sided), power (0.8), MDE, sample size, duration (whole weeks), stopping rule,
  analysis method (t-test / delta method / CUPED / sequential), pre-declared segments.
- Assignment: deterministic hash `bucket = hash(salt + exp_id + player_id) mod 10000`; server-side
  (Remote Config/feature flag) so it is stable across devices and reinstalls; log assignment.

## Sample size & MDE
- Per-arm n for a mean difference δ, variance σ², α = 0.05 two-sided, power 0.8:
  `n ≈ 16·σ² / δ²` (Lehr's rule; (1.96 + 0.84)² × 2 ≈ 15.7).
- General: `n = (z_{1−α/2} + z_{1−β})² · (σ_A² + σ_B²) / δ²`; proportions: σ² = p(1 − p).
- MDE for given n: `δ = (z_{1−α/2} + z_{1−β}) · sqrt(2σ²/n)` ≈ `2.8 · sqrt(2σ²/n)`.
| Metric | Baseline | MDE (abs) | n per arm (≈) |
|---|---|---|---|
| D1 retention | 35% | +1 pp | 16·0.2275/0.0001 ≈ 36,400 |
| D7 retention | 10% | +1 pp | 16·0.09/0.0001 ≈ 14,400 |
| Payer conversion | 2% | +0.2 pp (10% rel.) | 16·0.0196/0.000004 ≈ 78,400 |
| ARPDAU (mean $0.10, sd $1.50) | $0.10 | +$0.005 (5% rel.) | 16·2.25/0.000025 ≈ 1.44 M |
- Revenue metrics are heavy-tailed: winsorize/cap at p99.9 (pre-declared), use CUPED, or test
  conversion and ARPPU separately; consider longer runs or larger allocations.
- Duration = total n / eligible users per day; minimum 7 days, prefer 14 (weekly seasonality,
  novelty); retention metrics need the last cohort matured (D7 test → +7 days after enrollment stops).
```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
es = proportion_effectsize(0.36, 0.35)                      # Cohen's h
n = NormalIndPower().solve_power(effect_size=es, alpha=0.05, power=0.8, ratio=1.0)
```

## Analysis methods
| Metric type | Method |
|---|---|
| Binary per user (converted, retained) | two-proportion z-test; CI for difference |
| Continuous per user (revenue, playtime) | Welch t-test (CLT ok at large n); bootstrap by user for small/skewed |
| Ratio with unit ≠ randomization unit (ARPDAU, revenue per session, CTR) | delta method or bootstrap clustered by user — naive t-test underestimates variance |
| Counts | Poisson/negative binomial or per-user mean + t-test |
- Report: absolute + relative effect, 95% CI, p-value, n per arm, exposure dates.
- Practical significance: compare CI to the smallest effect worth shipping, not just to zero.

## CUPED (variance reduction, Deng et al. 2013)
- `Y_cuped = Y − θ·(X − mean(X))`, `θ = cov(X, Y) / var(X)` pooled across arms; X = pre-experiment
  covariate unaffected by treatment (same metric in the 2–4 weeks before exposure).
- Variance multiplied by `(1 − ρ²)`; ρ = corr(X, Y). ρ = 0.5 → 25% less variance → ~25% fewer users.
- New users have no pre-period → use acquisition covariates (country, platform, channel) via
  regression adjustment (CUPAC/ML predictions) or skip.
```python
theta = np.cov(df.x, df.y)[0, 1] / np.var(df.x, ddof=1)
df["y_adj"] = df.y - theta * (df.x - df.x.mean())
```

## Sample Ratio Mismatch (SRM) — check first, always
- Chi-square goodness-of-fit of assignment counts vs planned split.
```python
from scipy.stats import chisquare
stat, p = chisquare([n_a, n_b], f_exp=[(n_a + n_b) * 0.5] * 2)
```
- Alarm threshold: p < 0.0005 (Microsoft ExP practice) to p < 0.001; on SRM, do NOT read results.
- Causes: assignment after a filter that treatment affects, crashes/redirect loss in one arm,
  bot filtering, logging differences, delayed SDK init, caching, client version differences.
- Example: 50.2% / 49.8% split with ~1.4 M users → χ² ≈ 22.8, p ≈ 2×10⁻⁶ → SRM; investigate.

## Peeking & sequential testing
- Repeated significance checks on a fixed-horizon test inflate false positives: ~14% at 5 looks,
  ~19% at 10, ~25% at 20 (nominal α = 0.05; Armitage, McPherson & Rowe 1969).
- Options: (1) fixed horizon — look once at the planned n; (2) group sequential with α-spending
  (O'Brien-Fleming: very strict early, near-nominal at the end; Pocock: constant); (3) always-valid
  inference (mSPRT, Optimizely/Eppo/Statsig sequential modes); (4) Evan Miller's simple
  sequential test for conversion.
- Dashboards may show live data for safety (guardrails), not for shipping decisions.

## Multiple comparisons
- One primary metric decides; secondaries are explanatory.
- k variants vs control: Bonferroni α/k (conservative) or Dunnett; many metrics: Holm or
  Benjamini–Hochberg FDR (q = 0.05–0.10). Segment hunting after the fact = hypothesis generation only.
- Expect 1 in 20 A/A metric differences "significant" at α = 0.05; run A/A tests to validate the pipeline.

## Threats specific to games
- Novelty/primacy: plot effect by days since exposure; decide on stabilized period; long-term
  holdout (1–5% of users) for cumulative features.
- Interference: shared economy, gifting, PvP matchmaking, leaderboards, guild events → cluster
  randomization or switchback by region/time.
- Monetization tests: store prices can't be split per user on one SKU → separate SKUs per variant;
  check platform rules and consumer-protection rules for personalized pricing (compliance-advisor).
- Client version gating: treatment code only in new builds → randomize among users on the new
  build only, or the comparison is confounded by update behavior.
- Seasonality and live events: avoid launching across major events or ensure both arms see them.
- Twyman's law: a surprising large lift is most likely a bug — re-verify tracking and SRM.

## Bayesian alternative (conversion)
- Beta-Binomial: posterior `Beta(α₀ + conversions, β₀ + non-conversions)`; prior Beta(1,1) or
  informed from history. Report P(B > A) and expected loss; ship when expected loss < threshold.
```python
rng = np.random.default_rng(7)
a = rng.beta(1 + conv_a, 1 + n_a - conv_a, 200_000)
b = rng.beta(1 + conv_b, 1 + n_b - conv_b, 200_000)
p_b_better = (b > a).mean(); expected_loss_b = np.maximum(a - b, 0).mean()
```
- Pros: intuitive statements, decision-theoretic stopping. Cons: prior choice must be
  pre-registered; optional stopping is not "free" for error control; revenue needs other models.

## Readout structure
1. Decision + one-line why. 2. Validity: SRM p, exposure counts, dates, A/A history, data issues.
3. Primary metric: effect, 95% CI, p (or posterior). 4. Guardrails. 5. Secondary + pre-declared
segments. 6. Caveats (novelty, seasonality, power). 7. Recommendation + follow-ups.

## Sources
- Kohavi, Tang & Xu, "Trustworthy Online Controlled Experiments", Cambridge University Press, 2020
- Evan Miller, "How Not To Run an A/B Test" https://www.evanmiller.org/how-not-to-run-an-ab-test.html
- Evan Miller, Sample size calculator https://www.evanmiller.org/ab-testing/sample-size.html
- Deng, Xu, Kohavi & Walker, "Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data" (CUPED), WSDM 2013
- Fabijan et al., "Diagnosing Sample Ratio Mismatch in Online Controlled Experiments", KDD 2019 https://dl.acm.org/doi/10.1145/3292500.3330722
- Lukas Vermeer, SRM checker FAQ https://lukasvermeer.nl/srm/docs/faq/
- Armitage, McPherson & Rowe, "Repeated significance tests on accumulating data", JRSS A, 1969
