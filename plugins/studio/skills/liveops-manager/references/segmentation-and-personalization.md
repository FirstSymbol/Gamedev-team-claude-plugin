# Segmentation, personalization and holdouts

## Segment registry (`.team/specs/liveops/segments.md`)
Every segment: `id | definition (SQL or rule expression) | refresh (real-time/hourly/nightly) |
owner | used by (events/offers) | version | created`. Segments are evaluated server-side,
deterministically; membership is logged on every exposure.

## Lifecycle stages
| Stage | Definition (tune per game) | Goal | Levers |
|---|---|---|---|
| New | D0-D7 since install | habit, FTUE completion | beginner pass, login calendar, guided quests; no hard offers before value is shown |
| Early | D8-D30 | first purchase, social hook | starter pack, first-purchase bonus, join a team |
| Established | D31-D90 | depth, repeat spend | pass, collections, tournaments |
| Veteran | D90+ | prestige, content freshness | endgame events, leagues, cosmetics, creator/community roles |
| At-risk | activity < 50% of own trailing-14-day baseline, or progress stall | prevent churn | difficulty relief, help offers, re-engagement event |
| Lapsed | no session 14-30 d (choose and fix one) | reactivation | comeback rewards, push/email winback |
| Returned | session after lapse | re-onboard | returning-player pass, "what's new" recap, catch-up boosts |

## Spend tiers - neutral naming, ethical use
- Industry jargon "minnow/dolphin/whale" exists; in specs and anything external use neutral
  tiers: non-payer, first-time payer, low / mid / high spender.
- Define tiers by percentile of trailing 90-day net spend within the game (e.g. high = top
  1-2% of payers), not fixed dollar values; recompute monthly; document refunds handling.
- Revenue concentration is typically steep (a small share of payers drives most revenue -
  measure your own Lorenz curve; don't quote folklore numbers).
- Safeguards (mandatory for high tiers):
  - Spend-velocity monitor: e.g. 24 h spend > 3x player's own 90-day daily average or above
    an absolute threshold → pause targeted offers, flag for review, optional check-in message.
  - Honor self-set spend/time limits; no targeted offers to minors or unknown-age accounts.
  - Exclude recently refunded/charged-back accounts from offers.
  - EU: consumers must be told when a price is personalized by automated decision-making
    (Consumer Rights Directive as amended by Omnibus Directive 2019/2161) and EU consumer
    authorities (CPC Network, 2025) published principles on in-game virtual currency pricing
    (verify current text with compliance-advisor - needs human legal review).
- Prefer personalizing bundle composition, timing and relevance over charging different
  prices for identical goods - players compare offers publicly (Reddit/Discord).

## RFM for games
| Dimension | Metric | Score |
|---|---|---|
| Recency | days since last session (engagement RFM) or last purchase (monetary RFM) | quintile 1-5 |
| Frequency | sessions in last 7 d, or purchases in last 90 d | quintile 1-5 |
| Monetary | net spend last 90 d (payers only; non-payers = 0 cell) | quintile 1-5 |
| Cell | Read | Default action |
|---|---|---|
| R high, F high, M 0 | engaged non-payer | starter/value pack, rewarded ads, pass free track upsell |
| R high, F high, M high | core payer | content-first: pass, collections; no discount spam |
| R low, M high | lapsing payer | winback with new content + modest reward; personal support |
| R low, F low, M 0 | churned casual | low-cost push/email winback; accept loss |
| R high, F low | sporadic | session triggers: timers, streaks, weekend events |

## Churn-risk segmentation
- Start rule-based: session frequency drop vs personal baseline, stuck on a level >= N attempts,
  lost long streak, left team/clan, failed purchase, loss streak.
- Then model: P(no session in next 7 d) via logistic regression / gradient boosting on
  rolling features; evaluate precision@top-decile and calibration monthly.
- Prediction is not impact: test interventions with an uplift experiment (treat vs hold out
  within the at-risk segment); target players with the highest uplift, not highest risk.

## Targeting rules
- One targeted offer slot per player per period; explicit priority order resolves conflicts;
  cooldown after any targeted offer (e.g. 48-72 h).
- Mutually exclusive segments for offers; overlapping segments allowed for events.
- Data freshness stated: real-time attributes (level, balance) vs nightly batch (RFM, churn
  score). Never target on stale balance for "you're low on coins" offers.
- Guardrail exclusions applied last and always: minors/unknown age, self-limited, recently
  refunded, global holdout, legal geo restrictions.
- Staging preview: test account per segment sees the expected config before publish.

## Holdouts and experiments
- Global liveops holdout: 2-5% of players, persistent (rotate yearly), excluded from targeted
  liveops to measure total incremental value; they still get baseline content and any
  compensation. Per-event holdout 5-10% when the event's value is unproven.
- Randomize by hashed player id + per-experiment salt; stratify or check balance by platform,
  geo, spend tier.
- Sample size for a proportion (80% power, alpha 0.05 two-sided):
  `n per arm ~= 16 * p * (1 - p) / delta^2`. Example: payer conversion p = 3%, detect
  +0.3 pp absolute → n ~= 16 * 0.0291 / 0.000009 ~= 51,700 per arm.
- Revenue is heavy-tailed: winsorize at p99-p99.9 or use CUPED (pre-period covariate);
  report payer conversion and ARPPU separately from ARPDAU.
- Guardrails on every test: D1/D7 retention, refund rate, support tickets, uninstalls.
- Run >= 2 full weekly cycles (novelty + weekday effects); no peeking without sequential tests.
- Tools: UGS Game Overrides (multi-variant, % rollout), PlayFab Experiments, Satori Experiments,
  Firebase A/B Testing, or feature-flag service + warehouse. Analysis owner: data-analyst.

## Personalization maturity ladder
1. Rule-based lifecycle segments + global holdout.
2. RFM-driven offer targeting with cooldowns and guardrails.
3. Predictive churn / propensity-to-pay scores with uplift tests.
4. Contextual bandits for offer/content selection, with guardrails, exploration floor and an
   explainability log. Don't jump to 4 without 1-3 instrumented.

## Sources
- Unity Game Overrides - Get started (targeting, rollout, variants): https://docs.unity.com/en-us/game-overrides/get-started
- Heroic Labs Satori 2.0 (audiences, flags, experiments): https://heroiclabs.com/blog/announcing-satori-20/
- Omnibus Directive (EU) 2019/2161: https://eur-lex.europa.eu/eli/dir/2019/2161/oj
- Kohavi, Tang, Xu - Trustworthy Online Controlled Experiments (Cambridge Univ. Press, 2020)
- Deng et al. - Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data (CUPED), WSDM 2013
