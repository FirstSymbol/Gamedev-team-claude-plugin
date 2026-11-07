# Business models and platform rules (informational — needs human legal review)

## Legal elements test
| Element | RMG | Social casino | Sweepstakes | Skill tournament |
|---|---|---|---|---|
| Consideration | stake | coin purchase (optional) | gold-coin purchase; free AMOE route claimed to remove it | entry fee |
| Chance | yes | yes | yes | claimed: skill predominates |
| Prize of value | cash | none (if no cash-out/transfer) | sweeps coins redeemable for cash/prizes | cash/prizes |
| Typical legal basis | licence | "no prize" theory | "no purchase necessary" promotion law | skill-gaming exemption |
- Weak points regulators/courts attack: secondary markets for social coins (Washington: Kater v.
  Churchill Downs, 9th Cir. 2018, virtual chips = "thing of value"); AMOE that is impractical;
  "skill" games where chance dominates.

## Real-money gaming (RMG)
- Licence per market (B2C operator) + supplier/B2B licence for game studios/RGS where required
  (UK, MGA, Ontario, US states, Curacao LOK). Studios selling games to operators usually need the
  B2B licence or ship through a licensed aggregator.
- Products: casino (slots, RNG table, live dealer), sports betting, poker (P2P), bingo, lottery.
- Tech consequences: certified RNG + math per jurisdiction; PAM (player account management) with
  KYC/AML/RG; payment processing (PSPs, no credit cards in UK since 2020-04-14); geolocation;
  regulator reporting feeds; data residency (US states, some EU/LatAm markets).

## Social casino
- Coins: purchasable, never cash-out, no transfer between players (gifting only free/system coins,
  capped), no marketplace; ToS states no monetary value.
- Ratings: PEGI 18 for social casino in new submissions from June 2026; Australia R18+ for
  interactive simulated gambling (since 2024-09-22); IARC questionnaire answers must declare
  simulated gambling; Apple: infrequent simulated gambling 13+, frequent 18+, real gambling 18+,
  Australia overlay R18+ even for infrequent simulated gambling (App Store Connect age ratings).
- Must not link to, advertise or convert into real-money gambling inside the app (Google Play ads
  policy prohibits gambling ads in simulated-gambling apps); keep brand separation if the same
  group runs RMG.
- Risks: US class actions (Washington, others) over "illegal gambling" theory; loot-box style
  scrutiny of coin packs; minors (age gate 18+, no ads to children).

## Sweepstakes / dual-currency model (US)
- Mechanics: Gold Coins (GC, purchasable, play-only) + Sweeps Coins (SC, given free via AMOE —
  mail-in, daily login — and as a "bonus" with GC purchases; SC winnings redeemable after KYC
  and play-through).
- Legal pressure (as of 2026-11; verify each state before any decision): statutory bans in
  Montana, Connecticut, New Jersey, Nevada (2025), California (AB 831, signed 2025-10-11,
  effective 2026-01-01, extends liability to payment processors/affiliates), New York (S5935-A,
  ch. 605, signed 2025-12-05, effective immediately; USD 10k-100k per violation; also bars payment
  processors, geolocation/platform/content suppliers and media affiliates from supporting).
  2026 wave: Indiana (HB 1052, effective 2026-07-01, civil penalties up to USD 100k, no express
  supplier liability), Maine (LD 2007, ~2026-07), Louisiana (HB 883/Act 182 + HB 53, effective
  2026-08-01, up to USD 100k and 5 years, covers suppliers/affiliates), Tennessee (SB 2136, signed
  2026-05-22, AG enforcement), Oklahoma (SB 1589, veto overridden, effective 2026-11-01, felony);
  Iowa SF 2289 (2026) adds regulator enforcement powers. Earlier cease-and-desist actions (e.g.
  Michigan, Washington). Trackers disagree; check legislature/regulator sites, not affiliate maps.
- Operator exposure: state AG actions, class actions for recovering losses, payment-processor
  and app-store delisting, geofencing obligations per state.
- Studio rule: do not design a sweepstakes product or "redeemable" currency without a dated legal
  opinion per state (compliance-advisor → human counsel).
- Apple 5.3.1-5.3.2: sweepstakes must be sponsored by the developer; official rules in-app,
  stating Apple is not a sponsor. 5.3.3 bars IAP for currency "for use in conjunction with real
  money gaming of any kind" - SC-linked GC sold via IAP is at risk; get written App Review guidance.

## Apple App Store (Guidelines updated 2026-10-16)
- 5.3.3: no IAP to buy credit/currency used for real-money gaming.
- 5.3.4: RMG and lotteries need licensing/permissions where used, must be geo-restricted to those
  locations, and the app must be free on the App Store; gambling aids (card counters) banned.
- 3.1.1: loot boxes disclose odds before purchase; purchased currencies may not expire.
- Expect longer review; keep licence documents, geo-restriction evidence and test accounts per
  market ready for App Review notes.

## Google Play (Real-Money Gambling, Games and Contests policy)
- Gambling apps only in supported countries via the application process; valid licence per
  country and product type; block under-age users and unlicensed locations; free to download; no
  Play Billing; rated AO / IARC equivalent; responsible-gambling info in app and store listing.
- Other real-money games/contests: forbidden unless under the gambling programme, a gamified
  loyalty program or a limited regional pilot (no real-money stakes for prizes).
- Gambling ads inside Play apps: not to under-18s, not in Designed for Families apps, not in
  simulated-gambling apps, no RMG support features or redirects to RMG, no deceptive placement.
- Daily fantasy sports: US-only (licence per state that requires one) or via the gambling
  programme outside the US, with state blocking.
- Loyalty programs in games: fixed-ratio rewards only (no chance-based rewards).

## Geo-restriction and licensing proofs
- RMG US: certified geolocation (e.g. GeoComply) at login and periodically; block VPN/proxy/
  emulators; state-line buffer logic; log every check for the regulator.
- EU/UK: IP + payment/KYC address consistency; block unlicensed markets at registration and login.
- Mobile: store-level territory availability is not enough — enforce server-side per request.
- Evidence pack per market: licence certificate, approved game list with cert IDs, RNG cert,
  geo-blocking test report, RG feature screenshots, ToS/privacy, contact for regulator.

## Choosing a path (decision rules)
- Need revenue in regulated markets fast → integrate licensed RGS/aggregator + white-label PAM;
  studio licenses as B2B supplier only when games are its product.
- Social casino first, RMG later → keep math and RNG at RMG grade from day one (re-use for
  certification), keep codebases/brands and wallets separate.
- Sweepstakes → only with written state-by-state counsel; plan exit paths for banning states.

## Sources
- Apple App Review Guidelines (5.3, 3.1.1; updated 2026-10-16) https://developer.apple.com/app-store/review/guidelines/
- Google Play Real-Money Gambling, Games, and Contests policy https://support.google.com/googleplay/android-developer/answer/9877032
- Kater v. Churchill Downs Inc. (9th Cir. 2018) https://law.justia.com/cases/federal/appellate-courts/ca9/16-35010/16-35010-2018-03-28.html
- SBC Americas, Newsom signs California sweepstakes ban (2025-10-14) https://sbcamericas.com/2025/10/14/newsom-signs-california-sweepstakes-ban/
- NY Senate, S5935 (signed ch. 605, 2025-12-05) https://www.nysenate.gov/legislation/bills/2025/S5935
- National Law Review, Indiana HB 1052 (2026-03) https://natlawreview.com/article/sweepstakes-gaming-banned-indiana
- InfoLawGroup, Sweepstakes casino laws in 2026 (2026-07-27) https://www.infolawgroup.com/insights/2026/7/27/sweepstakes-casino-laws-in-2026-new-bans-proposed-legislation-and-regulatory-trends
- App Store Connect Help, Age ratings https://developer.apple.com/help/app-store-connect/reference/age-ratings
- Australian Classification, mandatory minimum classifications (2024) https://www.classification.gov.au/about-us/media-and-news/news/new-mandatory-minimum-classifications-for-gambling-games-content
- Osborne Clarke on PEGI 2026 criteria https://www.osborneclarke.com/insights/games-loot-boxes-get-16-plus-age-rating-europe-under-pegi-overhaul
