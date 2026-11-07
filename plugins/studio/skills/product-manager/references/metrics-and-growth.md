# Metrics and growth
PM sets goals and interprets; data-analyst owns definitions, tracking plan, SQL, dashboards and
experiment statistics (hand off via `.team/specs/<area>/analytics.md`).

## AARRR (McClure "pirate metrics") — with game/app definitions
| Stage | Question | App/SaaS metric | Game metric |
|---|---|---|---|
| Acquisition | Do they arrive? | visitors → signups, CAC by channel | installs, CPI, store page CVR, organic share |
| Activation | Do they get first value? | % reaching "aha" action in N days | FTUE completion, first win/level N, tutorial drop-off funnel |
| Retention | Do they come back? | W1/W4 retention, DAU/MAU | D1/D7/D30, sessions/day, DAU/MAU (stickiness) |
| Revenue | Do they pay? | conversion to paid, ARPA, MRR, churn | payer conversion, ARPDAU, ARPPU, ad ARPDAU, LTV |
| Referral | Do they bring others? | invites/user, K-factor | invites, shares, guild/club joins, viral K |
- Fix in order: activation and retention before acquisition spend. Paid UA on a leaky product burns money.
- Funnels are a view; growth loops (Reforge) explain compounding: new user → action → output
  (content, invite, ad revenue) → reinvested into acquisition. Name the product's main loop.

## Activation
- Define the activation event from data: the early action most correlated with long-term
  retention (e.g., "completed 3 slot spins + claimed bonus on day 0", "joined a team in week 1").
  Correlation ≠ cause; validate by experiment.
- Measure time-to-value; remove steps before the first reward (forced signups, long intros, permission prompts).
- FTUE funnel per step with drop-off %; the largest drop is the first target.

## Retention
- Cohort retention curves (by install week/channel/platform); the goal is a curve that flattens
  (a stable retained base), not just a higher D1.
- Unbounded (returned on day N or later) vs classic/bounded (active exactly on day N) —
  state which; games usually use classic DN.
- Mobile benchmarks: canonical table in `studio:domain-f2p-liveops` (lifecycle-and-kpis) - GameAnalytics
  2026 (2025 data): median D1 ~22%, D7 ~4%, D30 < 1%; top quartile D1 ~30% (declining YoY; verify by genre).
  Soft-launch targets often quoted: D1 35-40%+, D7 15%+, D30 5-10%+ for mid-core/casual (vendor
  guidance varies widely; set per genre with data-analyst).
- SaaS: watch logo churn and net revenue retention (NRR > 100% means expansion beats churn).
- Product-market fit signals: flattening retention curve; Sean Ellis test ≥ 40% "very disappointed"
  if they could no longer use the product.
- Resurrection/reactivation and churn prediction are live-ops topics (`studio:domain-f2p-liveops`).

## Monetization metrics
| Metric | Formula | Note |
|---|---|---|
| ARPDAU | revenue (IAP + ads) / DAU, per day | split IAP vs ads |
| Payer conversion | payers / active users (period) | F2P mobile often low single-digit % (verify by genre) |
| ARPPU | revenue / payers | heavy-tailed; report median too |
| LTV (simple) | ARPDAU × expected lifetime days (area under retention curve) | cap horizon (D180/D365); predict from early cohorts |
| ROAS DN | cohort revenue by day N / UA spend | UA targets usually set on D7/D30 ROAS (marketing-manager) |
| Payback | days until cumulative cohort revenue ≥ CAC | |
| LTV:CAC | LTV / CAC | SaaS rule of thumb ≥ 3:1 |
| Revenue concentration | % revenue from top 1%/10% payers | risk if extremely concentrated; social casino typical |
| Refund/chargeback rate | refunds / transactions | guardrail; fraud signal |
- Social casino specifics: coins sink/source balance, purchase frequency, VIP tiers, bonus
  economy — see `studio:domain-igaming`; economy design → economy-monetization-designer.
- Ethical guardrails: no pressure tactics against minors, transparent odds where required, spend
  limits for vulnerable users; review with compliance-advisor.

## Experimentation culture
- Hypothesis template: "Because <evidence>, we believe <change> for <segment> will <move metric
  by X>. We'll know when <primary metric> changes by ≥ MDE without guardrail harm."
- Decide before launch: primary metric, guardrails, MDE, sample size, duration (≥ 1-2 full weeks
  for weekly seasonality), stop rule. No peeking-based stops unless using sequential methods.
- Sample size rule of thumb (80% power, α = 0.05, two variants): n per variant ≈ 16 × σ² / δ².
  For a proportion p: σ² = p(1 − p). Example: D7 14% → detect +1 pp: 16 × 0.1204 / 0.0001 ≈ 19,300 per variant.
- Check sample ratio mismatch (SRM) before reading results; segment only pre-registered cuts.
- Novelty effect in games: rewards/visual changes spike early; read on later days or on new cohorts only.
- Monetization tests: watch long-term retention and LTV, not just day-0 revenue; holdout groups
  for cumulative features (live-ops calendars, notifications).
- When you can't A/B (small audience, platform limits, social features): staged rollout + pre/post
  with control markets, or diff-in-diff (data-analyst).
- Experiment log `.team/reports/experiments.md`: ID, hypothesis, result, decision, learning.
  Share losses — most experiments don't win (Kohavi reports ~2/3 or more fail to improve the target).

## Metric hygiene
- Every metric has an owner, definition (events, filters, timezone, dedupe), and dashboard link.
- Ratio metrics show numerator and denominator; watch mix shifts (channel, platform, country).
- Separate leading (activation, D1) from lagging (LTV, NRR) in reviews.
- Avoid vanity metrics: total installs, registered users, page views without behavior.
- Weekly metric review: North Star + inputs + guardrails, anomalies with hypotheses, actions.

## Handoff to data-analyst (what to send)
- PRD path, primary/guardrail metrics in plain words, segments, required events/properties
  draft, experiment hypothesis + MDE, decision deadline.

## Sources
- Dave McClure, "Startup Metrics for Pirates: AARRR!", 2007 (talk/slides, 500 Startups).
- Brian Balfour, Casey Winters, Kevin Kwok, Andrew Chen, "Growth Loops are the New Funnels", Reforge https://www.reforge.com/blog/growth-loops
- Ron Kohavi, Diane Tang, Ya Xu, "Trustworthy Online Controlled Experiments", 2020 (sample size rule, SRM, guardrails).
- GameAnalytics 2026 benchmarks summary (2025 data) https://gamedevreports.substack.com/p/gameanalytics-mobile-and-pc-game
- Sean Ellis & Morgan Brown, "Hacking Growth", 2017 (PMF 40% test, growth process).
- Amplitude, "North Star Playbook" https://amplitude.com/books/north-star/about-north-star-framework
