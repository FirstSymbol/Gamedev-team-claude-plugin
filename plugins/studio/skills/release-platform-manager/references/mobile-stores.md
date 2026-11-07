# Mobile stores: Apple App Store and Google Play (checked 2026-11)
Policy text changes several times a year - re-read the live guideline before each submission.

## Apple App Store Review Guidelines - sections games hit most
| Guideline | Rule (paraphrase/quote) | Game implication |
|---|---|---|
| 2.1(b) App Completeness | final build, working URLs, IAP "complete, up-to-date, visible to the reviewer and functional" | demo account, IAP products in "Ready to Submit", no placeholder art |
| 3.1.1 In-App Purchase | unlocking features/currency/levels "must use in-app purchase"; no license keys, QR, crypto unlocks | soft/hard currency, battle pass, ad removal = IAP |
| 3.1.1 loot boxes | randomized paid items "must disclose the odds of receiving each type of item to customers prior to purchase" | odds screen reachable from the purchase point |
| 3.1.1(a) / 3.1.3 / US storefront | outside the US, no buttons/links/calls to action to non-IAP purchasing; the US storefront is exempt (buttons, external links allowed; guidelines 2026-10-16) | web shop links: US yes; elsewhere only via entitlements (EU, JP, KR...); US link-out commission post-appeal (verify: Apple developer news, at submission) |
| 4.3 Spam | no multiple bundle IDs of the same app; no clones | reskinned slot apps at risk |
| 4.7 Mini apps/games | HTML5 mini games allowed, developer responsible for content | in-app mini-game hubs |
| 5.1.1 Data collection | privacy policy link in metadata and in-app; consent; **account deletion in-app if account creation exists** | guest + linked accounts need delete flow |
| 5.1.2 Data use / ATT | tracking requires App Tracking Transparency permission; can't gate features/rewards on enabling tracking or push | no "allow tracking for 100 coins" |
| 5.3.1-5.3.2 Contests | sweepstakes sponsored by developer; official rules in app, Apple not a sponsor | tournaments with prizes |
| 5.3.3 | IAP may not buy credit/currency "for use in conjunction with real money gaming" | |
| 5.3.4 Real money gaming | licensing in every location, geo-restricted, free on the store; lotteries need consideration, chance, prize | RMG casino: license per jurisdiction, geofence |
| 5.6 Code of conduct | no manipulative practices, fake reviews; use the system review prompt API | no custom rating gates |
- Social casino (no cash-out) is allowed but rated for frequent simulated gambling (18+ in Apple's 2025 age
  system; Australia R18+ regional rating). Some markets require extra review time for 5.3 content.
- Kids Category (1.3): "should not include third-party analytics or third-party advertising" - narrow exceptions (analytics with no IDFA/child data; contextual ads with human creative review); purchases/links behind a parental gate.
- Brazil: fixed-odds betting apps need SPA license details in App Review Information.

### Apple platform requirements (from developer.apple.com/news/upcoming-requirements)
| Since | Requirement |
|---|---|
| 2024-05-01 | privacy manifest: approved reasons for required-reason APIs, incl. third-party SDKs (Unity, ads, analytics SDKs ship their own manifests - keep SDKs current) |
| 2026-01-31 | new age rating questionnaire answered for every app (tiers 4+, 9+, 13+, 16+, 18+) |
| 2026-04-28 | uploads built with Xcode 26 / iOS 26 SDK or later |
| 2026-09-09 | iOS/iPadOS uploads must target iOS 13 or later |
| EU | DSA trader status required to distribute/update in the EU |
| Game Center | entitlement + configuration in App Store Connect before submission if used |
Unity: set Xcode version on build agents per year; set Player Settings > Target minimum iOS Version >= 13.0 (Apple upload rule since 2026-09-09) and check the editor line's own minimum.

### App Privacy ("nutrition labels") and ATT
- Declare every data type collected by the app **and its SDKs** (ads, attribution, analytics, crash),
  purpose, linked to identity or not, used for tracking or not. Keep an SDK data inventory per release.
- ATT: show the system prompt (`ATTrackingManager.requestTrackingAuthorization`) before accessing IDFA;
  pre-prompt screen allowed but no incentives; `NSUserTrackingUsageDescription` in Info.plist.
- SKAdNetwork / AdAttributionKit for attribution without IDFA (ads/UA team).

### TestFlight and release
| Item | Fact |
|---|---|
| Internal testers | up to 100 App Store Connect users, no beta review |
| External testers | up to 10,000; first build of a version needs Beta App Review; public link optional |
| Build expiry | 90 days after upload |
| Review time | Apple: "at least 50% of submissions in less than 24 hours and 90% in less than 48 hours" (developer.apple.com/distribute/app-review, checked 2026-11) |
| Phased release | automatic updates over 7 days: 1%, 2%, 5%, 10%, 20%, 50%, 100%; pause up to 30 days total; manual downloads always possible |
| Expedited review | request for critical fixes; use sparingly |
| Holiday freeze | App Store Connect submissions slowed/paused late December (check yearly notice) |

## Google Play
### Platform requirements
| Item | Requirement (verify each year: developer.android.com/google/play/requirements/target-sdk) |
|---|---|
| Target API level | from 2026-08-31: new apps and updates must target Android 16 (API 36); existing apps must target >= API 35 to stay visible to new users on newer OS; Wear OS/Automotive API 35, TV/XR API 34 |
| Extension | extension to 2026-11-01 could be requested via Play Console forms (now passed; next cycle expected same pattern) |
| App bundle | AAB required for new apps; large assets via Play Asset Delivery (Unity: Addressables + PAD) |
| Play Billing Library | 2-year cycle: since 2026-08-31 (extension ended 2026-11-01) new apps/updates need PBL 8+; v8 until 2027-08-31, v9 until 2028-08-31. Unity IAP 4.15.1 ships PBL 8.3.0, 5.0 → 8.0.0, 5.4 → 9.0.0 |
| 16 KB page size | apps targeting Android 15+ must support 16 KB pages on 64-bit devices; from 2027-02-01 non-compliant updates cannot be released (Unity: use a 16 KB-ready editor version, check native plugins/SDKs) |
| Account deletion | apps with account creation must offer in-app deletion and a web deletion link in Data safety |
| New personal developer accounts | created after 2023-11-13: closed test with >= 12 opted-in testers for 14 continuous days before production access |

### Policies games hit most (Play Policy Center)
| Policy | Key points |
|---|---|
| Payments | digital goods via Google Play Billing (regional alternative billing programs exist); loot boxes: "clearly disclose the odds of receiving those items in advance of purchase" |
| Real-Money Gambling, Games and Contests | allowed only in approved countries via application; licensed operator per country/state; geo + age controls; free to download; **no Play Billing**; rated AO/IARC equivalent; responsible gambling info |
| Simulated gambling / social casino | no real-money wagering or prizes of real-world value; not for children; apps with simulated gambling content may not show real-money gambling ads (RMG policy, ads section) |
| Families / Designed for Families | if children are in the target audience: Families Self-Certified Ads SDKs only, no "real or simulated gambling", ads must not show simulated gambling/contests; neutral age screen for mixed audiences |
| Data safety | form must match all collection/sharing by app + SDKs; inaccuracy = enforcement |
| User data / permissions | prominent disclosure + consent for sensitive data; no unnecessary permissions |
| Device and network abuse | no hidden downloading of executable code outside Play (dynamic code); Addressables content OK (assets, not code) |
| Ads | no deceptive/disruptive ads; interstitials not at app launch/unexpectedly (Better Ads) |

### Testing tracks and rollout
| Track | Use |
|---|---|
| Internal testing | up to 100 testers, available within minutes; smoke/QA builds |
| Closed testing | email lists / Google Groups; multiple tracks (alpha, QA, partners); pre-registration-like betas |
| Open testing | public opt-in from store listing; soft-launch style feedback |
| Production | staged rollout % (e.g. 1 → 5 → 20 → 50 → 100) with halt; can target countries |
- Pre-launch report: automated runs on Firebase Test Lab devices for each upload (crashes, ANRs, accessibility, security).
- Halt rollout stops new distribution; to fix, upload a higher versionCode and resume rollout.
- Managed publishing: approved releases go live only when you click publish - use for coordinated launches.
- Review time: usually hours to a few days; Play states some apps get extended review up to 7 days or longer.
- Android vitals bad-behaviour thresholds (crash 1.09%, ANR 0.47% overall; 8% per phone model; 28-day average) affect discoverability; memory/bitmap thresholds may affect visibility from 2027-02.

## Pre-submission checklist (mobile)
- [ ] Version/build numbers incremented; built from release tag; symbols (dSYM / native symbols) uploaded.
- [ ] Target API / Xcode SDK / privacy manifest requirements met (dated check).
- [ ] Privacy labels + Data safety updated for SDK changes; privacy policy URL live.
- [ ] Age rating questionnaire (Apple) and IARC (Play) answers match content (age-ratings.md).
- [ ] IAP products created, priced, approved; restore purchases works; receipt validation server-side.
- [ ] Odds disclosure for paid random items; ATT prompt flow; account deletion flow.
- [ ] Reviewer notes: demo account, how to reach gated content, geo/age gating explanation.
- [ ] Screenshots/video per required device size; localized metadata; no competitor platform references.
- [ ] Staged rollout plan + halt criteria + min supported client version set server-side.

## Sources
- Apple App Store Review Guidelines https://developer.apple.com/app-store/review/guidelines/
- Apple Upcoming requirements https://developer.apple.com/news/upcoming-requirements/
- App Store Connect Help, Age ratings https://developer.apple.com/help/app-store-connect/reference/age-ratings
- App Store Connect Help, Release a version update in phases https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases
- Android Developers, Target API level requirements https://developer.android.com/google/play/requirements/target-sdk
- Play Console Help, Real-Money Gambling, Games, and Contests https://support.google.com/googleplay/android-developer/answer/9877032
- Play Console Help, Testing requirements for new personal developer accounts https://support.google.com/googleplay/android-developer/answer/14151465
- Android Developers, Android vitals https://developer.android.com/games/optimize/vitals
- Android Developers, Play Billing Library deprecation FAQ https://developer.android.com/google/play/billing/deprecation-faq
- Android Developers, Support 16 KB page sizes https://developer.android.com/guide/practices/page-sizes
- Apple App Review (review times) https://developer.apple.com/distribute/app-review/
- Play Console Help, Families policy requirements https://support.google.com/googleplay/android-developer/answer/9893335
