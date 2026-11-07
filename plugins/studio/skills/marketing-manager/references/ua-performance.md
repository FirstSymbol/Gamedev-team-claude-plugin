# User acquisition and performance marketing

## Channels (status 2026-11; product names/features change - recheck each network's docs before planning)
| Channel | Buying model / product | Strength | Watch |
|---|---|---|---|
| Meta (Facebook/Instagram/Audience Network) | Advantage+ app campaigns; optimize install → event → value | scale, broad audiences, strong creative feedback | learning phase; iOS via SKAN/AEM |
| Google App campaigns (ex-UAC) | tCPI / tCPA / tROAS across Search, Play, YouTube, AdMob | Android scale, Play intent | low control; asset-group based |
| TikTok | app campaigns (incl. automated Smart+ variants) | young audiences, creative-led | fast creative fatigue |
| Apple Ads (renamed from Apple Search Ads, 2025-04) | App Store search, Today tab, "You Might Also Like" | high-intent iOS; deterministic attribution in Apple's own reports | brand + competitor keyword costs |
| AppLovin (AppDiscovery / AXON) | in-game inventory, ROAS bidding | very strong for games | creative = playables/video; payer quality varies by genre |
| Unity Ads | in-game video/playables | games inventory | ironSource Ads (iAds) direct demand sunset 2026-04-30 (Unity Ads, LevelPlay mediation and ironSource Exchange programmatic demand continue) |
| Moloco, Mintegral, Liftoff, others | DSPs / networks | incremental scale | fraud checks, incrementality |
| PC/Steam | YouTube, Reddit, TikTok, Meta, influencers; Steam features are organic | wishlists | measure with Steam UTM links; ad-driven wishlists convert worse |
- Start with 1-2 channels in soft launch; add channels only when the first is profitable at scale.

## Unit economics (write the math into `ua-plan.md`)
- `ROAS_Dn = net cohort revenue to Dn / spend` (net of store fee, ad-network share, VAT; Google Play
  switched EEA/UK/US to a 10-25% service fee + 5% Play Billing fee from 2026-06-30, AU/JP from
  2026-09-30; legacy 15%/30% elsewhere; Apple 15%/30%).
- `max CPI = predicted net LTV(payback window) / target ROAS multiple` (e.g. 1.0 = break-even
  at window end; 1.2-1.5 if overhead must be covered).
- Required early ROAS from your curve: `ROAS_D7 target = ROAS_target(Dwindow) / (LTV_window / LTV_D7)`.
  Example: LTV365/LTV7 = 5 → 100% at D365 needs 20% D7 ROAS; ratio 20 → 5% (Liftoff 2026: a ~5%
  D7 ROAS "might be right on track" for a mid-core game recouping in six months).
- Organic uplift: `effective CPI = spend / (paid installs + incremental organic)`; measure the
  uplift with geo or spend-pulse tests, don't assume a k-factor.
- Payback cash: plot cumulative spend vs cumulative net revenue per cohort; finance must fund
  the gap (6-12 month payback is common for successful hybrid-casual, 2025 industry reports).
- Observed D7 ROAS (Segwise 2025 data via Liftoff, 2026-04 - reference points, not targets; derive
  your own from the LTV curve): mid-core IAP-led ~4.3% iOS / 6.1% Android; hyper-casual ~7.6% iOS /
  7.8% Android; casual D30 ~47% iOS / 15% Android. Ad-led games usually aim to pay back in ~30 days.
- Benchmarks for CPI/IPM/CPM/ATT: `studio:domain-f2p-liveops` (lifecycle-and-kpis).

## Creative testing framework
- Unit = concept (fantasy/theme) x hook (first 3 s) x format (9:16 / 1:1 / 16:9 video,
  playable, static) x end card/CTA. Name files by this schema for analysis.
- Budget split (practitioner): ~70% proven winners, ~20% iterations of winners, ~10% new concepts.
- Test in a dedicated test campaign/ad set with equal budgets; graduate winners into scaling
  campaigns; change one variable per iteration.
- Read after a minimum sample (practitioner: >= 10k impressions and >= 50 installs per creative
  for IPM; ROAS reads need far more). Kill if IPM < 50% of control after the sample.
- Metrics funnel: hook rate (3-s views / impressions) → CTR → store CVR → IPM → CPI → D7
  ROAS by creative (MMP creative reporting).
- Fatigue: IPM down > 30% from peak or frequency > ~3-4/week → refresh; keep a 4-6 week
  pipeline of new concepts.
- Representative ads: UK ASA has upheld complaints against mobile game ads that didn't show
  actual gameplay (check asa.org.uk rulings search for recent cases before a campaign) - if a "fake" mechanic is advertised, it must exist
  and be reachable early in the game.
- AI-generated creatives: check platform labeling rules and IP rights; never use real people's
  likeness without release.

## Attribution and measurement
| Layer | Tool | Use |
|---|---|---|
| MMP | AppsFlyer, Adjust, Singular (also Branch, Kochava) | channel/campaign/creative attribution, deep links, fraud protection, cost aggregation |
| iOS privacy | SKAdNetwork 4 / AdAttributionKit | aggregated, delayed postbacks; conversion value schema |
| Incrementality | geo holdouts, platform conversion-lift tests | true causal lift per channel |
| MMM | Meta Robyn, Google Meridian (open source) | budget allocation across channels, incl. non-trackable |
- MMP setup requirements for engineering (unity-developer): SDK init after consent, revenue
  events from server-validated purchases (S2S), impression-level ad revenue from mediation,
  SKAN/AAK conversion value updates, deep links, uninstall measurement.
- iOS: ATT opt-in ~39% of gaming users shown the prompt (Adjust, Q1 2026); design the
  conversion-value schema around D0-D2 signals (tutorial complete, first purchase, revenue
  buckets) because SKAN 4 postback windows are 0-2, 3-7 and 8-35 days with fine values only
  in the first. AdAttributionKit (iOS 17.4+) supports re-engagement and alternative marketplaces;
  Apple's SKAdNetwork page says to use AdAttributionKit for app ad campaigns, but the SKAdNetwork
  class itself is not deprecated (only `registerAppForAdNetworkAttribution()` and
  `updateConversionValue(_:)`; checked 2026-11) - ignore third-party "SKAN sunset" dates.
- Android: GAID still available; Google retired Privacy Sandbox technologies on Chrome and Android
  (incl. Attribution Reporting, Topics, Protected App Signals, SDK Runtime; announced 2025-10-17)
  - no migration needed; use Play Install Referrer via the MMP.
- Truth hierarchy: incrementality > MMM > MMP last-touch > ad-network self-reporting.

## Budget pacing
- Pick the optimization event that fires >= ~50 times per ad set per week (Meta learning-phase
  rule of thumb; verify: Meta Business Help "About the learning phase", not rechecked 2026-11);
  else optimize higher in the funnel.
- Raise budgets in steps of ~20-30% every 2-3 days (practitioner) to avoid learning resets;
  cut fast on cohort ROAS below kill threshold for 2+ cohorts.
- Weekly reallocation by cohort D7 ROAS vs target per channel/geo/OS; keep 10-20% for tests.
- Seasonality: Q4 (Black Friday to Christmas) CPMs spike; launch bursts then are expensive.
- Soft-launch UA: size budget so each weekly cohort per geo reaches >= 1,000-2,000 paid
  installs (domain soft-launch gates); same channels you will scale with.
- Geos: see domain lifecycle-and-kpis.md (CA/AU/NZ as US proxy; PH/ID/BR/MX/TR for cheap
  retention reads).

## Restricted category: social casino (always with compliance-advisor; load studio:domain-igaming)
- **Meta** (policy version 2026-05-18, unchanged in current text as of 2026-11): allowed without separate authorization only if there is
  no chance to win money or anything of monetary value; target 18+ only; barred in 19
  markets (Azerbaijan, Bangladesh, Cambodia, Egypt, Hong Kong, India, Indonesia, South Korea,
  Kyrgyzstan, Malaysia, Mongolia, Myanmar, Pakistan, Philippines, Saudi Arabia, Singapore,
  Taiwan, Thailand, Vietnam); "coins" may be mentioned only if they have no monetary value. If
  players can buy/sell virtual prizes for money → Online Gambling policy (prior written permission).
- **Google Ads**: social casino certification required; one account cannot hold both social
  casino and online gambling certification; choose one country group - Group 1 (incl. US, UK,
  CA, AU, NZ, DE, FR, JP, BR, MX, Nordics, ES...) or Group 2 (HK, IN, KR, MY, TW, TH, VN); game
  must carry a legal-gambling-age disclaimer, state no real-money gambling or real-world
  prizes, disclose IAP in ad or landing page; no real-money gambling brand marks; no targeting
  minors; sweepstakes casinos are not eligible (listed as not social casino; date of that change
  not shown on the policy page). Certification applications move into the Google Ads account from
  2026-09. Violations are "egregious":
  suspension without warning, no re-entry.
- TikTok, Snap, Apple Ads, ad networks and MMP-partner networks each have own gambling/
  simulated-gambling rules (not researched here: read each network's current gambling policy
  before spend).
- Soft-launch geo choice must respect these lists (e.g. no Meta social casino ads in PH/ID/MY/VN).
- Creative rules: no implied real-money winnings, cash imagery or "win big" money claims; show
  18+ / no-real-money disclaimers; age-gate landing pages.
- Store side (age ratings for simulated gambling, regional bans) → release-platform-manager.

## Sources
- Adjust Gaming App Insights 2026 (summary): https://gamedevreports.substack.com/p/adjust-gaming-app-insights-report
- Liftoff - What is a good ROAS? 2026 benchmarks: https://liftoff.ai/?p=35616
- Unity - Sunsetting ironSource Ads: https://unity.com/en/products/ironsource-ads-sunset
- Apple SKAdNetwork docs (AdAttributionKit note): https://developer.apple.com/documentation/storekit/skadnetwork
- Android Authority, Google kills Privacy Sandbox (2025-10): https://www.androidauthority.com/google-kills-privacy-sandbox-3608497
- Google Play Console Help, service fees: https://support.google.com/googleplay/android-developer/answer/112622
- AppleInsider - Apple rebrands Search Ads as Apple Ads (2025-04-14): https://appleinsider.com/articles/25/04/14/apple-rebrands-its-advertising-business-as-apple-ads
- Apple AdAttributionKit docs: https://developer.apple.com/documentation/adattributionkit
- Meta Social Casino Games policy: https://transparency.meta.com/policies/ad-standards/content-specific-restrictions/social-casino-games
- Google Ads social casino games policy: https://support.google.com/adspolicy/answer/15132179
- AppsFlyer 2025 Creative Report: https://www.appsflyer.com/company/newsroom/pr/ai-emotion-creative-trends/
