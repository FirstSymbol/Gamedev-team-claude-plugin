# Monetization models (practitioner reference)

## Core formulas
| Metric | Formula | Note |
|---|---|---|
| Conversion | payers / active users (period) | segment by install cohort, not calendar |
| ARPDAU | revenue (IAP net + ads) / DAU | ads and IAP tracked separately |
| ARPPU | IAP revenue / payers | heavy-tailed: report median and p90 too |
| LTV(d) | Σ_{t=0..d} ARPDAU(t) × retention(t) | cohort-based; cap horizon (D180/D365) |
| Net revenue | gross × (1 - store fee) - VAT/GST | store fees differ by program/region (below) |
- Genre benchmarks (conversion, ARPDAU, D1/D7/D30) → studio:domain-f2p-liveops; cite source + year.
- Store commission (checked 2026-11): Apple 30% standard, 15% Small Business Program (< USD 1M
  proceeds) and subscriptions after year 1. Google Play: new structure in EEA/UK/US from
  2026-06-30 and AU/JP from 2026-09-30 - IAP 20% (new installs) / 25% (existing installs) + 5%
  Play Billing fee, subscriptions 10% + 5%, lower with Play Games Level Up; other markets keep
  15% on first USD 1M/yr, 30% above, 15% subscriptions. US/EU/JP/KR alternative billing and
  link-out terms differ again (compliance-advisor) - model net revenue per storefront.

## IAP store design
- Sections: currency packs, bundles (currency + items), featured/limited offers, pass/subscription,
  cosmetics. Max ~6 currency packs; one "best value", one "most popular" badge (truthful).
- Show real-money price from the store SDK (localized `StoreKit`/`Play Billing` price string),
  never hardcoded; show item prices in currency AND real-money equivalent where feasible
  (EU CPC 2025 principle 1; see compliance-advisor).
- Currency pack sizes must let players buy what they need: avoid a 950-gem item with only
  500/1,200-gem packs (CPC principle 3 "do not force unwanted purchases").
- Receipts validated server-side before granting; handle refunds/revocations (claw back or
  flag; see compliance-advisor references/loot-boxes-and-monetization-law.md).

## Price points per platform
- Apple (2023 system): 800 price points by default, 100 higher ones (up to USD 10,000) on request;
  175 storefronts, 43 currencies; auto-equalized from a chosen base storefront (Apple updates
  non-base prices for tax/FX); setting a storefront price manually stops auto-adjustment there.
- Google Play: per-country local prices with auto conversion templates; min/max price per currency
  are in the tables of Play Console Help "Supported locations for distribution to Google Play users".
- Steam: developer sets the price per currency (37 currencies; Valve reviews prices); optional
  conversion from USD tiers by exchange rate, purchasing power or multi-variable method.
  Consoles: platform-holder price tiers per region (check each partner portal).
- Typical ladder (USD): 0.99 / 1.99 / 4.99 / 9.99 / 19.99 / 49.99 / 99.99. Bonus currency grows
  with tier (e.g. +0/+10/+20/+30/+40/+60%) — practitioner pattern, tune by test.
- Price per hard-currency unit must decrease monotonically up the ladder; test with a spreadsheet
  check (`gems/USD` strictly increasing).
- Regional pricing: use platform equalization + purchasing-power adjustments for emerging markets;
  watch arbitrage via VPN/gifting (security-engineer).

## Starter packs and first purchase
- Goal: convert non-payers; one-time, high value (often 3-10x the currency-pack value),
  low price (0.99-4.99), shown after the player understands the value (after tutorial/D1),
  with a real (non-resetting) expiry window.
- Follow-up ladder: starter → "second purchase" pack at ~2x price → regular store.
- Never show a "limited" timer that restarts on next login (fake urgency = deceptive practice).

## Battle pass / season pass math
- Inputs: tiers T, XP per tier x, season length S days, daily XP available per player archetype
  d_a (dailies + weeklies + play), premium price P, premium-currency rebate R.
- Completion days for archetype a: D_a = T·x / d_a. Design so the target archetype (regular,
  ~5 sessions/week) completes at ~70-85% of S; casual reaches ~50-60% of T (practitioner targets).
- Value: premium track perceived value ≥ ~5-10x P; place the strongest reward at tier 1 (instant
  value) and the final tier (completion goal); cosmetics over power.
- Rebate: if R (currency returned along premium track) ≥ next season price, completers renew for
  free — strong retention, lower net revenue per completer; model both.
  (Example often cited: Fortnite pass 950 V-Bucks returning up to 1,500; verify: Epic's current
  Battle Pass help page - not rechecked 2026-11.)
- Tier skips: price per tier ≈ P / (0.3-0.5·T) so buying the whole pass via skips is expensive;
  cap skips or disclose total cost. Bundle "pass + 25 tiers" at ~2.5x P.
- Rules: no paid random items as the only path to pass rewards; time-limited passes now push
  PEGI ratings to ≥ 12 for new submissions from June 2026 (compliance-advisor).
```text
Example: T=50, x=1,000 XP, S=56 days -> 50,000 XP. Regular player 1,000 XP/day -> 50 days (89% of S):
too tight; add 300 XP weekly-challenge average/day -> 38 days (69%) OK; casual 450 XP/day x 56 days -> 25 tiers (50% of T).
```

## Subscriptions and VIP
| Model | Mechanic | Watch-outs |
|---|---|---|
| Monthly card | pay once, daily currency drip for 30 days (must log in) | value must be clear; drip is a retention tool |
| Auto-renew subscription | perks (ad-free, daily rewards, pass) | Apple 3.1.2: ≥ 7-day period, ongoing value, clear terms; easy cancel laws (compliance-advisor) |
| VIP tiers (spend-based) | cumulative spend unlocks permanent perks | can incentivize harmful spend; add spend-limit tools; casino VIP = regulated in real-money |
| Ad-free purchase | one-time removal of interstitials | keep rewarded ads available (opt-in) |
- Trial: show price after trial, renewal date, cancel path before purchase; send renewal reminders
  where required by market auto-renewal law (compliance-advisor platform-and-consumer-rules.md).

## Ads
| Format | Rule of thumb | Policy anchor |
|---|---|---|
| Rewarded video | opt-in, clear reward before watch, cap per day (e.g. 5-10), cooldowns | exempt from Play interstitial limits when explicitly opted in |
| Interstitial | natural breaks only; none in first session/tutorial; min gap 60-180 s and N levels; skip for payers | Google Play: no unexpected full-screen, none at start of a level, none before splash, closable ≤ 15 s |
| Banner | menus only, never over controls; avoid in core gameplay | accidental-click ads violate policies |
| Offerwall | high-value non-payers; fraud-prone | validate server-to-server callbacks |
- Mediation: AdMob / AppLovin MAX / ironSource LevelPlay (Unity); frequency caps in mediation
  plus in-game logic (both). Children/mixed-audience apps: certified family ad networks only,
  no personalized ads (COPPA/GDPR; compliance-advisor). Consent first (Google UMP/TCF) in EEA/UK.
- Hybrid model: IAP + ads; stop interstitials after first purchase (protects payer experience).

## Offer segmentation and personalization
- Segments: spend tier (never/low/mid/high), last purchase price ("anchor"), days since last
  purchase, progression blocker, currency balance, engagement trend, platform/country.
- Next-offer rule: price ≈ last purchase price (step up at most ~1 tier); balance-low triggers;
  churn-risk → value offers, not pressure.
- Store/offer logic server-side (remote config + rules); log every impression and purchase for
  A/B; avoid price discrimination on protected traits; EU: disclose personalized pricing based
  on automated decision-making (Consumer Rights Directive art. 6(1)(ea), from Omnibus 2019/2161).
- "Discount" claims need a genuine prior price. EU: the Omnibus 30-day prior-price rule (art. 6a
  Price Indication Directive) covers goods only, not digital content/services - fake or inflated
  "was" prices for virtual items are judged under the UCPD instead (Commission guidance on art. 6a, 2021-12);
  UK: CMA/DMCC Act pricing rules (compliance-advisor).

## Anchoring and decoy
- Anchor: show a high-value pack first (or "was" price only if genuinely charged before).
- Decoy: a pack slightly worse than the target (e.g. 4.99/500 vs 9.99/1,200) makes the target the
  rational choice; keep every pack honest in gems-per-USD.
- Charm pricing (.99) and bundle framing are fine; misleading quantity/price claims are not.

## Ethical lines and dark patterns to avoid
| Pattern | Why it is a problem | Instead |
|---|---|---|
| Fake/resetting countdowns, fake scarcity | deceptive (EU UCPD, FTC Act §5) | real end dates |
| Obscured prices (multi-step currency conversion) | CPC 2025 principles 1-2 | show real-money equivalent |
| Confirmshaming, nagging pop-ups after "no" | manipulative design | one decline = cooldown |
| Accidental purchases (one-tap, button placement swaps) | Epic/FTC 2022: USD 245M refunds | confirm step, undo window |
| Hidden or hard cancellation | auto-renew laws, FTC enforcement | in-app cancel path |
| Pay-to-skip frustration you engineered | trust loss, regulator focus on "pay to progress" | tune friction for non-payers first |
| Paid random items for minors | FTC/HoYoverse 2025 (under-16 consent), Brazil 2026 ban | gate by age, direct purchase alternative |
| Escalating offers to high spenders with no limits | harm to vulnerable consumers (CPC principle 7) | spend limits, cool-offs, cap offers |
| Near-miss visuals in random rewards | gambling-like cue | neutral reveal |
| Disguised ads, fake close buttons | Google Play ads policy | standard close, labelled ads |
- Rule: if a mechanic only works because the player misunderstands cost or odds, redesign it.
- Every monetization spec gets a compliance-advisor review before build ("needs human legal review"
  for market-specific go/no-go).

## Sources
- Apple App Review Guidelines (3.1.1, 3.1.2; updated 2026-10-16) https://developer.apple.com/app-store/review/guidelines/
- Apple App Store Connect Help: set a price for an in-app purchase https://developer.apple.com/help/app-store-connect/manage-in-app-purchases/set-a-price-for-an-in-app-purchase
- Google Play Console Help, service fees https://support.google.com/googleplay/android-developer/answer/112622
- Apple App Store Small Business Program https://developer.apple.com/app-store/small-business-program/
- Steamworks, Pricing https://partner.steamgames.com/doc/store/pricing
- Commission guidance on art. 6a Directive 98/6/EC (2021) https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021XC1229(06)
- Google Play policy: Ads (interstitials, 15-second rule) https://support.google.com/googleplay/android-developer/answer/9857753
- FTC, Epic Games settlements (2022) https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations
- FTC business blog on HoYoverse/Genshin settlement (2025-01) https://ftc.gov/business-guidance/blog/2025/01/level-tips-businesses-ftcs-settlement-genshin-impact-developer-hoyoverse
- CPC Network key principles on in-game virtual currencies (2025), summary https://www.zwillgen.com/gaming/cpcn-announces-virtual-currency-consumer-protection-guidelines/
- Deconstructor of Fun https://www.deconstructoroffun.com/ ; GameRefinery (feature/monetization trends) https://www.gamerefinery.com/
