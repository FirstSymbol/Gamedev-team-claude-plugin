# F2P lifecycle, KPIs and soft-launch gates

## KPI definitions (use these exact formulas in specs and dashboards)
| KPI | Formula | Notes |
|---|---|---|
| Dn retention (classic) | users active on day n / installs of cohort (day 0 = install day) | default; "rolling" (active on day >= n) is inflated - never mix |
| DAU/MAU | avg DAU / MAU | stickiness; PC SDK games median 4-5%, top 10% 13-15% (GameAnalytics 2026); mobile casual 10-20% is a practitioner rule (verify: no mobile DAU/MAU in GameAnalytics 2025/2026 summaries) |
| ARPDAU | (net IAP + ad revenue) / DAU | state gross vs net (store fee) explicitly |
| Payer conversion | unique payers / active users in period | or cumulative: % of install cohort that paid by Dn - say which |
| ARPPU | revenue / unique payers (period) | heavy-tailed; report median + p90 too |
| Cumulative ARPU (LTVn) | cohort revenue to day n / cohort installs | the LTV curve; fit to project D180/D365 |
| Predicted LTV | ~ ARPDAU x sum of retention(d) over lifetime days | sanity check vs curve-fit (power law on cumulative ARPU) |
| CPI / CPA | spend / installs (or / target action) | blended CPI hides channel mix |
| ROAS Dn | cohort revenue to Dn / cohort spend | net of store fee and ad-network share |
| Payback day | first day ROAS >= 100% | business sets target window (e.g. 180-365 d) |
| Crash-free sessions | 1 - crashed sessions / sessions | Firebase Crashlytics / Unity Cloud Diagnostics; gate > 99.5% |
- Store fee (checked 2026-11): Apple 30% standard, 15% Small Business Program (< USD 1M proceeds)
  and subscriptions after year 1. Google Play legacy markets: 15% on first USD 1M/yr, 30% above,
  15% subscriptions; EEA/UK/US (from 2026-06-30) and AU/JP (from 2026-09-30): 20% (new installs)
  or 25% (existing installs) + 5% Play Billing fee on IAP, subscriptions 10% + 5% (lower tiers in
  Play Games Level Up). Model net revenue per storefront.
- Day boundaries: compute in UTC or player-local consistently; document which.

## Benchmarks (cite with year; refresh every report cycle)
### Retention, all genres, mobile
| Source (data year) | D1 | D7 | D30 |
|---|---|---|---|
| GameAnalytics 2025 report (2024), median | ~22% (cited by the soft-launch guide below; not in the report summary, whose bottom 25% is 10-11.5%) | 3.4-3.9% | 75% of games < 3% at D28 |
| GameAnalytics 2025 report (2024), top 25% | 26.5-27.7% (iOS 31-33%, Android 25-27%) | 7-8% | n/a |
| GameAnalytics 2026 report (2025), median | n/a | just under 4% | 0.69-0.79% |
| GameAnalytics 2026 report (2025), top 25% / top 10% | ~30% / ~40% | 6-7% / 11-12% | 1.6-1.8% / n/a |
| GameAnalytics 2026 report (2025), top 1% | 64-68% | > 25% | 13-15% |
| Adjust Gaming App Insights 2026 (2025, top 5,000 apps) | 27% | n/a | n/a |
- GameAnalytics samples all SDK games (min 1,000 MAU) incl. unmarketed - commercial gates sit
  near or above its top 10%. Retention declined YoY in both reports.
- Genre direction (GameAnalytics 2025): arcade leads D1 but decays; board, card, puzzle and
  casino lead mid/long-term retention.
- PC (GameAnalytics 2026, 2025 data): top 25% D1 15-16%, top 10% D30 ~2.5%; median session 18 min.

### UA cost (mobile)
| Source (period) | Figure |
|---|---|
| Adjust 2026 (2025) | global gaming CPI $0.56 (+30% YoY); North America $1.68; Slots $4.47; Idle RPG $3.19; Strategy $1.03 |
| Adjust 2026 (2025) | IPM 8.62; CPM $4.34 avg, North America $15.98; casino/slots CPM ~ $12 |
| Liftoff + Singular Casual 2025 (Feb 2024-Feb 2025) | highest iOS CPI casino $21.03; Android leader RPG $4.29; iOS CPI up to 4x Android in some genres |
| Liftoff ROAS benchmarks 2026 (Liftoff data) | D30 ROAS casual iOS ~47%, Android ~15% |
| Adjust 2026 | ATT opt-in (gaming, shown prompt) 39% Q1 2026; sports 54%, action 50% |

### Monetization
- AppsFlyer State of Gaming 2024 (2023 data): ~5% of players convert to payers; ~70% of payers buy
  again; ~50% of lifetime payers make their first purchase within 3 days of install.
- AppsFlyer App Monetization 2026 (Jan 2025-Mar 2026): casino converts 4.95% of new installs to
  payers, 3.01% repeat buyers (verify: figures and conversion window not rechecked - open the
  AppsFlyer report itself, not a summary).
- Daily payer conversion > 1% of DAU is a practitioner rule of thumb, not a published benchmark
  (verify against your genre data / GameAnalytics genre tables).

## Soft-launch gates by genre (practitioner targets)
Compiled from vendor/practitioner guides 2025-2026 - not standards; the one practitioner guide
cited (Android casual/puzzle) uses D1 28-32% peer band (stop < 25%), D7 stop-scale < 8%, D30
stop-scale < 3%, and no payer-conversion floor. Set both a **kill/fix
threshold** (below = stop and fix) and a **scale target**; tie the final gate to LTV/CPI.
| Genre | D1 | D7 | D30 | Payer conv (cum. D30) | Primary revenue |
|---|---|---|---|---|---|
| Hyper-casual | 35%+ | 8-10% | n/a | n/a | ads; CPI < ~$0.30 in prototype tests |
| Hybrid-casual | 35-40% | 10-15% | 3-5% | 1-2% | ads + IAP |
| Casual puzzle / match-3 | 40%+ | 15-20% | 6-10% | 2-4% | IAP + rewarded ads |
| Midcore (RPG, strategy) | 35-45% | 15-20% | 8-12% | 3-6% | IAP |
| Social casino | 35-40% | 15-20% | 8-10% | 3-5% | IAP, high ARPPU |
(verify: rows other than casual/puzzle are unsourced practitioner targets - check GameAnalytics
genre tables / Sensor Tower or AppMagic comparables before adopting as a gate.)

### Decision rules
- Fix retention before monetization: no pricing work rescues D1 < ~30%.
- Scale gate: predicted LTV / CPI >= 1.3-1.5 at the target payback window, at the CPI you
  get with real spend (CPI rises with volume).
- Readouts need paid traffic from the intended channels; organic-only cohorts mislead.
- Sample: >= 1,000-2,000 paid installs per cohort/variant for D7 decisions; read >= 3 weekly
  cohorts before judging a trend; D30 needs real calendar time - plan for it.
- Change one major variable per cohort when diagnosing; log build + config version per cohort.
- Kill/pivot when 2-3 iteration cycles fail to move the kill-threshold metric.

## Soft-launch geos
| Purpose | Typical geos | Why / caveat |
|---|---|---|
| Tech + retention, cheap traffic | Philippines, Indonesia, Malaysia, Vietnam, Brazil, Mexico, Turkey | low CPI, English (PH); behaviour differs from tier-1 |
| Monetization proxy for US | Canada, Australia, New Zealand | English, similar spend; CPI near US |
| Proxy for Western Europe | Netherlands, Nordics, Poland (cheaper) | localization tests |
| Asia-specific | Taiwan, Singapore, Thailand | local tastes; not a US proxy |
- Social casino: Meta forbids social casino ads in 19 markets incl. PH, ID, MY, VN, SG, TW, TH,
  KR, IN (Meta policy 2026-05-18, unchanged as of 2026-11) - soft launch in CA/AU/NZ/UK-style
  markets (local gambling/ads law per market → compliance-advisor).
- Google Play personal developer accounts created after 2023-11-13 must run a closed test with
  >= 12 testers opted in for 14 consecutive days before applying for production access.

## Content cadence
- Market pressure: events in top F2P games grew 35% (May 2023 → Jan 2025); midcore titles run
  > 20 concurrent events on average (verify: not on the cited GameRefinery tracker page, which
  is from 2024-08 - locate the GameRefinery/Sensor Tower report before quoting).
- Layering (Sensor Tower holiday LiveOps guide, 2025): long-term global events, mid-term
  complex events, short-term basic events running in parallel.
| Beat | Minimum at launch | Mature live game |
|---|---|---|
| Always-on | daily login, daily quests/missions | + streaks, piggy bank, store rotation |
| Weekly | 1 limited-time event + offer rotation | 2-4 overlapping events, weekend boosts |
| Monthly / 4-5 wk | season or pass | pass + collection album + tournament series |
| Quarterly | content/feature update | new meta layer, major holiday beat, IP collab |
- Content runway: >= 6-8 weeks of approved event content at global launch; production rate
  must exceed consumption rate (track "weeks of runway" on the board).
- Templates over one-offs: a reusable event engine (data-driven) + reskins keeps cost per
  event low; new mechanics a few times per year.

## Segmentation basics
- Axes: lifecycle stage (new D0-7, established, veteran, lapsed, returned), spend (non-payer,
  first-time, repeat; tiers by trailing 30/90-day spend), engagement, progression, geo/language,
  platform, acquisition source, churn-risk score.
- Evaluate segments server-side, deterministically, with a versioned definition; log segment
  membership on every offer/event exposure.
- Keep a persistent global holdout (e.g. 2-5%) excluded from targeted liveops to measure
  incremental value. Deep dive: `studio:liveops-manager` (segmentation-and-personalization).

## Sunset checklist
- Announce in-app + store + community >= 60-90 days ahead (practitioner norm; store and
  consumer-law notice rules per region → compliance-advisor); disable IAP first; keep servers through notice; refund policy decided with
  compliance-advisor; export/erase personal data per GDPR/CCPA.

## Sources
- GameAnalytics Mobile & PC Benchmarks 2026 (summary): https://gamedevreports.substack.com/p/gameanalytics-mobile-and-pc-game
- GameAnalytics Mobile Gaming Benchmarks 2025 (summary): https://gamedevreports.substack.com/p/gameanalytics-mobile-gaming-benchmarks
- Adjust Gaming App Insights Report 2026 (summary): https://gamedevreports.substack.com/p/adjust-gaming-app-insights-report
- Liftoff & Singular Casual Games 2025 (summary): https://gamedevreports.substack.com/p/liftoff-and-singular-casual-games
- Liftoff, What is a good ROAS? 2026 benchmarks: https://liftoff.ai/?p=35616
- Google Play Console Help, service fees: https://support.google.com/googleplay/android-developer/answer/112622
- Apple App Store Small Business Program: https://developer.apple.com/app-store/small-business-program/
- Play Console Help, testing requirements for new personal developer accounts: https://support.google.com/googleplay/android-developer/answer/14151465
- AppsFlyer State of Gaming App Marketing 2024: https://gamesbeat.com/appsflyer-state-of-gaming-report-user-acquisition/
- GameRefinery Live Events Tracker: https://gamerefinery.com/how-to-build-better-live-events-with-the-gamerefinery-live-events-tracker
- Meta Social Casino Games ad policy: https://transparency.meta.com/policies/ad-standards/content-specific-restrictions/social-casino-games
- Mobile soft launch guide (practitioner, 2025): https://gamegrowthadvisor.com/blog/2025-12-16-mobile-soft-launch-complete-guide/
