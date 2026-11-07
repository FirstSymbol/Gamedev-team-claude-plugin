---
name: domain-f2p-liveops
description: Shared F2P/live-service knowledge - lifecycle, soft-launch KPI gates, live events, remote config/flags, UGS/PlayFab/Nakama, IAP validation, ads mediation, push.
---
# F2P & live-ops domain (shared knowledge)
Mission: one source of F2P/live-service truth for designers, PM, data, liveops, marketing and
engineers; roles link here instead of restating it.

## Rules that always apply
- **Server-authoritative economy**: server owns balances, inventory, prices, timers, event
  progress and reward grants. Client = cache + view; never grant on a client callback.
- **Idempotent grants**: every grant/purchase keyed by a unique id (store transaction id,
  `eventId:playerId:milestone`); replays return the original result, never double-grant.
- **Server time only**: event windows, cooldowns, daily resets from server UTC; device clock is
  attacker-controlled. Define the reset hour per game (often 00:00 UTC or local-midnight per region).
- **Everything tunable is data**: prices, rewards, schedules, odds, difficulty live in remote
  config / server content with a schema version; the client ships safe defaults and works offline
  or degrades gracefully when config fetch fails.
- **Every live change is reversible**: owner, approval, staged rollout, kill switch, rollback
  path rehearsed (`studio:liveops-manager` (live-tuning-and-ops)).
- **Measure by design**: each feature ships with telemetry; economy-affecting changes ship
  behind an A/B or holdout (studio:data-analyst).
- **Store rules**: digital goods via Apple/Google IAP (external-purchase exceptions are
  region-specific - verify current Apple/Google rules per storefront); no executable code
  downloads (App Review 2.5.2) - data and assets only; loot boxes must disclose odds
  (App Review 3.1.1; Google Play policy). Ad/IAP targeting minors → compliance-advisor.
- **Ethics**: no deceptive timers, fake scarcity, hidden prices or pressure on vulnerable
  players; spend-limit and cooling-off tools for high spenders. Social casino or anything with
  wagering semantics → load studio:domain-igaming and involve compliance-advisor.

## Lifecycle at a glance
| Phase | Goal | Typical length | Exit gate (detail: lifecycle-and-kpis.md) |
|---|---|---|---|
| Prototype / greybox | core loop fun | 1-3 mo | playtest fun + CPI/IPM smoke test on fake ads |
| Closed alpha/beta | stability, FTUE | 1-3 mo | crash-free > 99.5% sessions, FTUE funnel known |
| Soft launch 1: tech + retention | D1/D7, perf | 4-8 wk | retention vs genre gate |
| Soft launch 2: monetization | payer conv, ARPDAU, LTV curve | 6-12 wk | predicted LTV > CPI with margin |
| Soft launch 3: scale test | CPI at volume, liveops cadence | 4-8 wk | ROAS curve holds at spend; event cadence sustainable |
| Global launch → live | grow, retain | years | content cadence + UA payback within target |
| Sunset | wind down | 60-90 d notice | refunds/notice per store + law (verify per region) |

## KPI snapshot (all genres, mobile; GameAnalytics 2026 benchmarks, 2025 data)
| Metric | Median | Top 25% | Top 10% |
|---|---|---|---|
| D1 | ~22% (2024 data) | ~30% | ~40% |
| D7 | ~4% | 6-7% | 11-12% |
| D30 | 0.7-0.8% | 1.6-1.8% | n/a (top 1%: 13-15%) |
Medians include unmarketed apps; commercial gates are far higher (genre table in references).

## Platform choice (live-service backend)
| Option | Pick when |
|---|---|
| UGS (Remote Config, Game Overrides, Cloud Code, Economy, Cloud Save, CCD) | Unity client, small/mid team, fast start |
| PlayFab | cross-engine, Azure shop, mature economy/segments |
| Nakama (+ Satori for liveops) | open-source core, self-host option, realtime/social |
| Custom ASP.NET Core | scale/cost control, regulated (social casino), complex economy |
Details, caveats and C# patterns: references/live-service-architecture.md.

## References (read on demand)
- references/lifecycle-and-kpis.md — soft-launch planning, KPI definitions/gates by genre,
  geos, content cadence, segmentation basics, go/kill decisions.
- references/live-service-architecture.md — remote config, feature flags, server-driven
  content, UGS/PlayFab/Nakama/custom .NET, server-authoritative economy code.
- references/event-types.md — designing or choosing a live event, pass, collection, piggy
  bank, streak, tournament or offer; levers and pitfalls per type.
- references/iap-and-refunds.md — Unity IAP v5, Google Play Billing, StoreKit 2, server
  receipt validation, refunds/chargebacks, subscriptions.
- references/ads-and-push.md — ads mediation (MAX, LevelPlay, AdMob), placements, consent,
  push notification plumbing and permission flow.
