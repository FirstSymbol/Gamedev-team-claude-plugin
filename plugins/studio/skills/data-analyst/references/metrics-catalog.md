# Metrics catalog (product + game analytics)

## Definition rules (apply to every metric)
- Write: name, formula (numerator/denominator), unit of analysis, window, filters (exclude
  test/QA/bots/refunded), timezone (UTC default; state if local), dedupe key, source table, owner.
- "Active user" = ≥ 1 session_start (or any non-background event) in the window; state which.
- Install/first-open date defines cohorts; reinstalls/new devices for same account → dedupe by
  player ID when logins exist, else device ID (state it).

## KPI tree (example, F2P mobile)
```
North star: weekly net revenue (or D30 net LTV per install)
├─ Acquisition: installs, CPI, D7 ROAS            (marketing-manager)
├─ Retention: D1/D7/D30, stickiness, sessions/DAU
├─ Monetization: conversion, ARPPU, ARPDAU (IAP + ads)
└─ Guardrails: crash-free sessions, refund rate, CS tickets/1k DAU, RG flags (iGaming)
```

## Engagement
| Metric | Formula | Notes |
|---|---|---|
| DAU / WAU / MAU | distinct active users per day / 7d / 30d (or calendar month) | state rolling vs calendar |
| Stickiness | avg DAU / MAU (or DAU/WAU) | mobile games often cited 10–20% (verify); GameAnalytics PC 2025 median 4–5%, top 10% 13–15% |
| Sessions per DAU | sessions / DAU | session timeout rule must be defined (e.g. 30 s–5 min background) |
| Session length | Σ session duration / sessions | median preferred over mean (long tail) |
| Playtime per DAU | Σ duration / DAU | GameAnalytics 2024 mobile median ≈ 22 min/day |
| New vs returning DAU | share of DAU with install date = today | growth health |

## Retention
- Classic (exact-day, "Day N"): `R(N) = users from install cohort active on day N / cohort size`.
  Day 0 = install day; D1 = next calendar day (UTC) or 24–48 h after install (state which).
- Rolling (unbounded, "return on day N or later"): `users active on day ≥ N / cohort size` —
  always ≥ classic; MyTracker, some MMPs report this. Never compare across methods.
- Bracket/range retention: active anywhere in days [N, M] (e.g. week-2 retention) — smoother for small cohorts.
- Churn (games): no activity for X days (commonly 7, 14, or 30 — define per game cadence).
- Report D1, D7, D30 (GameAnalytics uses D28 in older reports, D30 from the 2026 edition) with cohort n.
- Lifetime estimate (days) = `Σ_{d=0..H} R(d)` over horizon H; fit `R(d) = a·d^b` (power law,
  b < 0) on D1–D30 to extrapolate; validate on older cohorts.

## Monetization
| Metric | Formula | Notes |
|---|---|---|
| Gross vs net revenue | net = gross − store fee − VAT/taxes − refunds | Apple/Google fee 15% (small business / first $1M on Google / subs after year 1) or 30% (verify current programs) |
| ARPU | revenue / active users (period) | name period: ARPMAU |
| ARPDAU | daily revenue / DAU | split IAP vs ads; average of daily values, not total/Σ |
| ARPPU | revenue / paying users (period) | sensitive to whales — report median too |
| Conversion (payer rate) | payers / active users (period) | daily vs monthly vs cumulative per cohort differ 10x+ |
| First-purchase conversion | new payers in cohort by day N / cohort | time-to-first-purchase distribution |
| Ad ARPDAU | (impressions / DAU) × eCPM / 1000 | eCPM by format/geo; rewarded > interstitial > banner |
| Revenue concentration | share of revenue from top 1%/10% payers | whale dependence risk |
| Refund/chargeback rate | refunded revenue / gross | spikes = fraud or UX issue |

## LTV models (pick by data maturity)
| Model | Formula / method | Use when |
|---|---|---|
| Empirical cohort LTV(d) | Σ net revenue of cohort up to day d / installs | always compute; ground truth |
| ARPDAU × lifetime | `LTV(H) ≈ ARPDAU × Σ_{d=0..H} R(d)` | quick estimate, stable ARPDAU |
| Multiplier | `LTV(180) ≈ k × LTV(7)`; k fitted from mature cohorts | UA decisions with D7 data |
| Curve fit | fit cumulative ARPU `c·d^b` or log curve; extrapolate with caps | ≥ 30 days of data |
| BG/NBD + Gamma-Gamma | probabilistic repeat purchase (Python `lifetimes`/`pymc-marketing`) | many payers, non-contractual |
| Subscription | `ARPU × gross margin / monthly churn` | subscription products |
| ML (GBM on early behavior) | predict pLTV per user from D0–D3 features | large volume, UA bidding |
- Always: net revenue, by acquisition source/geo/platform, confidence band, horizon stated.
- Payback day = first d where cumulative net LTV(d) ≥ CPI (or CAC).

## UA & virality
| Metric | Formula |
|---|---|
| CPI | spend / attributed installs |
| ROAS Dn | cohort net (or gross — state) revenue to day n / spend; e.g. D7 ROAS 10–20% common target band (verify per genre/network) |
| CAC | spend / new payers (or new customers) |
| K-factor | `K = i × c` (invites sent per user × conversion per invite); K > 1 = viral growth |
| Viral cycle time | median time invite → new user's first invite |
| Organic uplift | organic installs during campaign vs baseline (incrementality test preferred) |

## Funnels & conversion
- Ordered funnel: each step within a time window from step 1 (e.g. 24 h); strict order or not.
- Report step conversion and overall; median time between steps; drop-off by segment.
- FTUE funnel: first_open → tutorial_step_n → tutorial_complete → first_level_complete → D1.
- Purchase funnel: store_open → offer_view → purchase_start → store_sheet → purchase_success
  (server-validated) → grant.

## Cohort analysis
- Rows = cohort (install week/day), columns = day/week since install, cells = retention or cumulative ARPU.
- Compare cohorts only with same acquisition mix; annotate releases, events, UA changes.
- Minimum cohort size for daily rates: ~1,000 for ±3 pp at D1 (95% CI half-width
  `1.96·sqrt(p(1−p)/n)`); smaller → weekly cohorts.

## Economy metrics (F2P / social casino)
- Sources vs sinks per currency per DAU; net flow → inflation; balance distribution percentiles.
- Social casino: coins in/out per spin (RTP realized vs design), time-to-bust, bonus share of
  income, purchase triggers (balance at purchase). Real-money iGaming: GGR = stakes − wins,
  NGR = GGR − bonuses − taxes/levies (verify jurisdictional definition).

## Benchmarks (mobile games; use as orientation only)
Canonical F2P gate/benchmark table: `studio:domain-f2p-liveops` (lifecycle-and-kpis); keep this section in sync.
GameAnalytics 2025 report (2024 data; 11.6k games, classic retention):
| Metric | Bottom 25% | Median | Top 25% |
|---|---|---|---|
| D1 | 10–11.5% | — | 26.5–27.7% (iOS 31–33%, Android 25–27%) |
| D7 | ~1.5% | 3.4–3.9% | 7–8% |
| D28 | — | 75% of games < 3% | — |
| Session length | — | 5–6 min | 8–9 min |
GameAnalytics 2026 report (2025 data; mobile titles ≥ 1,000 MAU; different sample):
D1 top 25% just above 30%, top 10% ~40%; D7 median just under 4%, top 25% 6–7%, top 10%
11–12%; D30 median ~0.7–0.8%, top 25% 1.6–1.8%; sessions/day top 25% 5.3–5.7.
Genre ranking (GameAnalytics 2025, qualitative): arcade strong D1 but weak long-term; board,
card, puzzle, casino strongest mid/long-term retention.
AppsFlyer genre averages (Q3 2022 data, via Mistplay; method not stated — verify):
| Genre | D1 | D7 | D30 |
|---|---|---|---|
| Casino | 28.2% | 9.9% | 4.1% |
| Match | 32.7% | 14.0% | 7.2% |
| Puzzle | 31.9% | 12.2% | 5.4% |
| Tabletop | 31.3% | 11.9% | 5.5% |
| RPG | 30.5% | 9.9% | 3.5% |
| Strategy | 25.4% | 8.1% | 3.1% |
| Simulation | 30.1% | 8.7% | 3.0% |
| Action | 29.8% | 7.6% | 2.1% |
| Shooting | 28.5% | 6.5% | 1.8% |
| Hyper-casual | 29.3% | 5.9% | 1.4% |
Monetization orientation (older, verify before use): payer conversion for most F2P titles
≈ 1–3% of MAU; GameAnalytics (Jun 2018–May 2019 data) top-15% titles 0.8–1.2% conversion,
RPG/strategy leaders up to ~3%/2.5%; ARPPU top-15% ~$20, action/strategy/RPG $27–31. MyTracker 2021: avg D1 paying-user rate 0.67%,
D7 1.10%. Benchmarks drift yearly (ATT, UA costs) → always cite year, sample, and method.

## Sources
- GameAnalytics 2025 Mobile Gaming Benchmarks, summary (GameDev Reports, 2025) https://gamedevreports.substack.com/p/gameanalytics-mobile-gaming-benchmarks
- GameAnalytics Mobile and PC Game Benchmarks 2026, summary (GameDev Reports, 2026) https://gamedevreports.substack.com/p/gameanalytics-mobile-and-pc-game
- Mistplay, mobile game retention benchmarks (AppsFlyer 2022 data) https://business.mistplay.com/resources/mobile-game-retention-benchmarks
- MyTracker, paying user and rolling retention benchmarks across genres (2021) https://tracker.my.com/blog/paying-user-and-rolling-retention-rate-benchmarks-across-game-genres-a-study
- wnhub, GameAnalytics 2019 benchmark summary (conversion/ARPPU) https://wnhub.io/news/other/item-15810
- Fader, Hardie & Lee, "Counting Your Customers the Easy Way" (BG/NBD), Marketing Science, 2005
