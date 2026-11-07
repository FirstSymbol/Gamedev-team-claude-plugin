# Platform and consumer rules (informational — needs human legal review)
Gambling-specific store rules (Apple 5.3, Google Play gambling programme): studio:domain-igaming
(references/business-models-and-platforms.md).

## Store policies affecting monetization
| Topic | Apple (Guidelines updated 2026-10-16) | Google Play |
|---|---|---|
| Digital goods payment | IAP required (3.1.1); no own unlock mechanisms (keys, QR, crypto) | Play Billing required for digital goods (Payments policy) |
| External links / alt billing | US storefront: buttons/external links/calls to action to other purchase methods allowed (3.1.1(a), 3.1.3; post Epic v. Apple injunction, 2025); EU DMA, JP, KR alternative terms | alternative billing (Payments §8) and external-offer links (§9) only in eligible countries via enrolled programmes (verify: eligible-country list and US terms after Epic v. Google remedies, Play Console Help as of 2026-11) |
| Loot boxes | disclose odds of each item type before purchase (3.1.1) | "clearly disclose the odds of receiving those items in advance of, and in close and timely proximity to, that purchase" (Payments policy §7) |
| Currency | purchased credits/currencies may not expire; restore for restorable IAP | consumables vs non-consumables correctly typed |
| Subscriptions | 3.1.2: ≥ 7-day period, ongoing value, cross-device, clear description before subscribing | Subscriptions policy: clear offer terms, trial terms, easy cancellation info |
| Kids | Kids category (1.3): no third-party analytics/ads without strict limits, parental gate for purchases/links | Families policy: Families-certified ad SDKs only, no personalized ads to children, teacher/family program rules |
| Account deletion | in-app deletion required if accounts can be created (5.1.1(v)) | in-app path + web link resource (usable after uninstall), declared in Data safety; associated data deleted |
| Ratings | Apple questionnaire, tiers 4+/9+/13+/16+/18+: loot boxes 9+ (AU 16+, BR A18), simulated gambling infrequent 13+ / frequent 18+, real gambling 18+ | IARC questionnaire (PEGI/ESRB/USK/ClassInd/etc.) |
- Pricing/refunds are store-controlled; never promise refunds you cannot execute; link store support.
- Keep a per-release store compliance checklist with release-platform-manager.

## Subscriptions and auto-renew
- Pre-purchase disclosure: price per period, renewal, trial length and price after trial, how to
  cancel, what is included. Show before the store sheet, not only in ToS.
- US: ROSCA (federal) requires clear disclosure, express informed consent, simple cancellation;
  FTC click-to-cancel rule vacated (8th Cir., 2025-07) but enforcement under ROSCA/§5 continues;
  state auto-renewal laws (California ARL as amended by AB 2863, for contracts made/extended from
  2025-07-01: separate express affirmative consent, online "click to cancel", annual reminder,
  notice of material changes, consent records kept ≥ 3 years or 1 year after termination), NY, others.
- UK: Digital Markets, Competition and Consumers Act 2024 subscription contract regime (pre-contract
  info, reminders, easy exit, cooling-off) — repeatedly delayed (autumn 2026 → spring 2027);
  government confirmed 2026-08-09 it starts January 2027 (verify: commencement regulations on
  legislation.gov.uk for the exact day).
- EU: CRD pre-contract info + withdrawal; some member states require cancel buttons
  (DE "Kündigungsbutton", § 312k BGB, since 2022-07-01); check other markets' national law.
- Store-managed subscriptions: platform handles cancel UI, but your in-game messaging must still be
  accurate; send renewal reminders where laws require (annual plans).

## Advertising to children and in-game ads
- EU UCPD Annex I no. 28: no direct exhortation to children to buy or to persuade parents.
- UK CAP Code + ASA/CAP guidance on advertising in-game purchases (2021): show real-money prices,
  no pressure on children, clear "ad" labelling of in-game promotions; ads for gambling-like
  content must not appeal strongly to under-18s.
- US: COPPA (no behavioural ads to under-13s without VPC), CARU Advertising Guidelines (self-
  regulatory; children's ads, in-app purchases, influencer disclosures), FTC Act §5.
- Platform: Google Play Families ads policy (certified SDKs), Apple Kids category limits.
- Gambling/social casino ads: never target under-18s; UK CAP/BCAP "strong appeal" test for gambling
  ads (in force 2022-10-01); verify: whether ASA applies it to free-to-play social casino creative
  (CAP Code s.16 scope, ASA rulings as of 2026-11).
- UA creatives: no misleading gameplay ads (ASA has ruled against unrepresentative mobile game ads);
  keep creative-to-product evidence.

## Influencer and endorsement disclosure
- US FTC Endorsement Guides (revised 2023): clear and conspicuous disclosure of material
  connections (free items, payment, affiliate), in the content itself (not only bio); applies to
  streamers and virtual influencers; FTC rule banning fake reviews/testimonials (2024).
- UK: CMA and ASA influencer guidance ("#ad" upfront); EU: UCPD + national rules (FR influencer
  law 2023 incl. gambling promotion limits).
- Loot box/gacha streams with sponsored currency must disclose sponsorship and any boosted odds
  (deceptive if odds differ from players').
- Brief template for creators: disclosure wording, prohibited claims, age audience, gambling rules.

## Accessibility law
- European Accessibility Act (Directive 2019/882), applies from 2025-06-28: games are not a listed
  product, but e-commerce services (incl. in-app/store purchase flows), electronic communications
  features and consumer terminal software may bring parts of a game into scope (interpretations
  differ by member state — check the national transposition act per market); microenterprise exemption for services
  (< 10 staff and ≤ EUR 2M turnover/balance sheet).
- Technical reference: EN 301 549 (maps to WCAG 2.1 AA) for purchase/account UIs; accessibility
  statement for in-scope services.
- US: CVAA (since 2019 for games) — accessible advanced communications features (text/voice chat);
  ADA Title III claims against websites/web stores are common (circuit split on non-physical
  businesses; counsel to assess).
- Practical: make store, account, consent, purchase-confirmation and chat UIs accessible first
  (text scaling, screen reader labels in UI Toolkit/uGUI, contrast, captions) — ux-ui-designer.

## Age ratings
- Criteria tables (PEGI June 2026 monetization rules, ESRB, AU, USK, IARC/Apple questionnaires) live in
  `studio:release-platform-manager` (age-ratings); cite them, don't restate. Compliance adds the legal
  reading per market and flags mismatches between design and declared rating.
- Ratings answers must match the shipped build and live-ops plans (adding loot boxes later can
  trigger re-rating duties on some systems).

## Sources
- Apple App Review Guidelines https://developer.apple.com/app-store/review/guidelines/
- Google Play policy: Ads https://support.google.com/googleplay/android-developer/answer/9857753
- FTC Endorsement Guides https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- CAP, "Guidance on advertising in-game purchases" (ASA/CAP, 2021) — UK advertising codes https://www.asa.org.uk/
- Taylor Wessing, accessibility in the gaming industry (EAA, 2025-03) https://www.taylorwessing.com/en/insights-and-events/insights/2025/03/accessibility-in-the-gaming-industry
- Osborne Clarke, PEGI 2026 overhaul https://www.osborneclarke.com/insights/games-loot-boxes-get-16-plus-age-rating-europe-under-pegi-overhaul
- European Accessibility Act, Directive (EU) 2019/882 https://eur-lex.europa.eu/eli/dir/2019/882/oj
- Google Play Payments policy https://support.google.com/googleplay/android-developer/answer/9858738
- Google Play account deletion requirements https://support.google.com/googleplay/android-developer/answer/13327111
- App Store Connect Help, Age ratings https://developer.apple.com/help/app-store-connect/reference/age-ratings
- Barnes & Thornburg, California ARL amendments in effect (2025) https://btlaw.com/en/insights/alerts/2025/california-expands-automatic-renewal-law-new-requirements-now-in-effect
- Stephenson Harwood, UK subscription regime from January 2027 (2026-08-24) https://shlegal.com/insights/subscription-reforms-brought-forward-to-january-2027-is-your-business-ready/
