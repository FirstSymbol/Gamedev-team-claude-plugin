# Ads mediation and push notifications

## Mediation platforms (status 2026-11)
| Platform | Notes | Pick when |
|---|---|---|
| AppLovin MAX | bidding-first mediation; AppLovin demand strong in games | default for ad-heavy casual/hybrid-casual |
| Unity LevelPlay | ironSource-heritage mediation; ironSource Ads direct-demand network sunset 2026-04-30 (mediation, Unity Ads and other networks unaffected) | Unity-centric stack, existing LevelPlay setup |
| Google AdMob mediation | Google demand + Open Bidding; simplest with Firebase | Google demand dominates, small ad share |
- Re-check waterfall/bidding yield after network changes (Unity warned of yield adjustments for
  setups reliant on ironSource Ads demand). Keep latest adapters; run the mediation debugger
  / test suite before each release.
- Bidding (in-app header bidding) by default; waterfall instances only for non-bidding networks.
- Run one mediation at a time; A/B mediation platforms only via split by user (verify vendor
  support) and compare ad ARPDAU net of IAP cannibalization.

## Formats and placement rules
| Format | Use | Rules of thumb (A/B test them) |
|---|---|---|
| Rewarded video | opt-in value exchange: double reward, revive, extra move/spin, skip timer | the best F2P format; daily cap; reward must be meaningful but not replace IAP sinks |
| Interstitial | natural breaks (level end) | none in FTUE / first sessions; minimum interval; never mid-gameplay; remove for payers or via "No Ads" IAP |
| Rewarded interstitial | opt-out reward between levels | disclose reward and skip option before showing |
| Banner / MREC | menus, idle screens | respect safe area; low eCPM; hurts UX in premium-feel games |
| App open | cold start | not for games with short sessions; never before first gameplay |
- Ad ARPDAU = impressions/DAU x eCPM / 1000. Track impressions/DAU, eCPM by geo/format, show
  rate, fill, and retention impact (holdout with lower frequency).
- Hybrid monetization: measure rewarded ads' effect on IAP conversion (cannibalization vs
  "ad-to-payer" lift) with a randomized holdout before scaling frequency.
- Rewarded grants of premium currency → use server-to-server reward callbacks (MAX S2S, AdMob
  SSV, LevelPlay server-to-server callbacks) and grant on the server.
- Ad callbacks may arrive off the main thread depending on SDK/settings - marshal to the main
  thread before touching Unity objects (verify per plugin).

## Privacy and consent (ads)
- EEA/UK/Switzerland: Google requires a Google-certified CMP using IAB TCF v2.2 to serve
  personalized/any Google ads (since 2024-01; verify) - Google UMP SDK or certified CMP.
- iOS: ATT prompt before IDFA access; pre-prompt explaining value raises opt-in; gaming ATT
  opt-in ~39% of users shown the prompt (Adjust, Q1 2026). Add mediation's SKAdNetwork IDs to
  `Info.plist`; AdAttributionKit supersedes SKAN going forward (marketing-manager owns UA).
- Children / mixed audience: COPPA, Google Play Families Policy (only Families Self-Certified
  ad SDKs), child-directed / under-age-of-consent flags in every network; no personalized ads
  to minors. Age gate design → compliance-advisor.
- US state privacy (CCPA/CPRA "do not sell/share"): pass GPP/US privacy signals to mediation.

## Push notifications - plumbing
| Need | Tool |
|---|---|
| Local (timers: energy full, chest ready) | Unity Mobile Notifications package (`com.unity.mobile.notifications`) |
| Remote (campaigns, events) | Firebase Cloud Messaging (Android + iOS via APNs), or OneSignal / Airship / Braze / Pushwoosh |
| Server sends | backend → FCM HTTP v1 API / APNs token-based (.p8) auth |
- Permission: iOS asks once per install - show a soft pre-prompt after a value moment (first
  reward timer), not at launch; provisional authorization (quiet delivery) is an option.
  Android 13+ (API 33) requires runtime `POST_NOTIFICATIONS`; use notification channels.
- Opt-in benchmark (Airship 2021 medians, pre-Android 13): Android 81%, iOS 51% - Android is
  now permission-gated and lower (verify current Airship/Pushwoosh gaming benchmarks).
- Tokens: store per device with platform/app version/locale/timezone; refresh on change;
  delete on APNs 410 / FCM `UNREGISTERED`.
- Send in player-local time with quiet hours; deep link to the exact feature; localize.
- Cancel scheduled local notifications that became irrelevant (energy already refilled).
- Frequency caps and content policy: `studio:liveops-manager` (player-communication).

## Anti-patterns
- Interstitial right after a loss or purchase → churn and refund risk.
- Ads shown to payers at the same frequency as non-payers → reduces spend; segment frequency.
- Granting premium currency on client rewarded callbacks → spoofable; use S2S.
- Prompting for push and ATT back-to-back at first launch → low opt-in for both.
- No consent flow in EEA → Google demand stops serving; regulator exposure.

## Sources
- Unity: Sunsetting ironSource Ads: https://unity.com/en/products/ironsource-ads-sunset
- Adjust Gaming App Insights 2026 (summary): https://gamedevreports.substack.com/p/adjust-gaming-app-insights-report
- Adjust ATT opt-in rates 2025: https://www.adjust.com/blog/att-opt-in-rates-2025
- Airship push notification benchmarks: https://grow.urbanairship.com/rs/313-QPJ-195/images/Airship-2023-Push-Notification-Benchmarks-en.pdf
- Pushwoosh push notification benchmarks: https://www.pushwoosh.com/blog/push-notification-benchmarks/
- Unity Mobile Notifications package docs: https://docs.unity3d.com/Packages/com.unity.mobile.notifications@2.4/manual/index.html
