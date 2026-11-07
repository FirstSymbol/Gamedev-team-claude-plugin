# ASO and store pages (App Store, Google Play, Steam)

## Apple App Store metadata
| Field | Limit | Indexed for search | Notes |
|---|---|---|---|
| App name | 30 chars | yes (highest weight) | brand + 1-2 keywords; no prices, no "#1/best" |
| Subtitle | 30 chars | yes | benefit + keywords; don't repeat name words |
| Keyword field | 100 chars | yes | comma-separated, no spaces, singular forms, no competitor trademarks, no repeats of name/subtitle words |
| Promotional text | 170 chars | no | editable without review - use for events/sales |
| Description | 4,000 chars | no | first 3 lines visible; conversion copy only |
| Screenshots | up to 10 per device size | n/a | first 3 carry search-result conversion |
| App previews | up to 3, 15-30 s | n/a | autoplay muted - message must work without sound |
| In-App Events | name 30 / short 50 / long 120 chars | event cards appear in search/Today | <= 10 published, <= 31 days, promote <= 14 days ahead |
(verify field limits in App Store Connect Help before each submission.)

### Custom product pages (CPP) and product page optimization (PPO)
- CPP: up to 70 additional pages per app (since 2025-10); customize screenshots, app previews,
  promotional text per localization; assign keywords so a CPP appears in organic search for
  them (since 2025-07; each keyword combination unique to one page); deep links per CPP
  (iOS/iPadOS 18+); reviewed separately from app updates; use in Apple Ads and as `ppid` URLs
  in other channels to match ad message → page.
- PPO: up to 3 treatments vs original; runs up to 90 days; test icon (alternate icons must be
  in the binary), screenshots, app previews; treatments need App Review; localizable.
- Map one CPP per audience/creative concept (e.g. "puzzle lovers", "decor fans", "competitive");
  measure CVR per CPP in App Store Connect analytics.

## Google Play metadata
| Field | Limit | Indexed | Notes |
|---|---|---|---|
| App title | 30 chars | yes | no emojis, ALL CAPS, or ranking/price claims (Play metadata policy) |
| Short description | 80 chars | yes | benefit-first |
| Full description | 4,000 chars | yes | natural keyword use; no keyword stuffing; no testimonials |
| Icon | 512 x 512 | n/a | no ranking/price badges |
| Feature graphic | 1024 x 500 | n/a | used in features/promos |
| Screenshots | 2-8 per device type | n/a | landscape games: landscape shots |
| Video | YouTube URL | n/a | ads disabled, embeddable |
(verify limits in Play Console Help.)
- Custom store listings: up to 50 (most developers), targeted by country, pre-registration,
  inactive users, or URL/ad campaign; own name, icon, descriptions, graphics.
- Store listing experiments: up to 2 variants vs current listing; 1 default-graphics experiment
  or up to 5 localized experiments at a time; graphics (icon, feature graphic, screenshots) and,
  in localized experiments, descriptions; target metric install/open/pre-registration clicks;
  configurable confidence level and minimum detectable effect; auto-stop after 6 months.
  Test one asset at a time.
- Promotional content (LiveOps cards) + featuring requests: Google reports > 2x explore
  acquisitions during featuring windows for apps submitting promo content (2023-24 analysis).

## Creative rules for store assets
- First 2-3 screenshots = core promise + core loop + payoff; large captions (<= 5-7 words);
  readable at thumbnail size; localized text and culturally adapted visuals for top geos.
- Video: real gameplay within the first 3 s; end with the payoff/progression; muted-safe.
- Icon: one focal element, strong silhouette, test 2-3 variants via PPO/experiments.
- Keep store assets consistent with ad creatives (message match lifts CVR); CPPs/custom
  listings for each major ad concept.
- Seasonal refresh: event-themed screenshots/icons for big beats (re-test conversion; themed
  icons can lower brand recognition).

## Ratings and reviews
- iOS: `AppStore.requestReview` / `SKStoreReviewController` - system shows the prompt at most
  3 times per 365 days; you can't know if it displayed; no custom pre-prompt that filters
  unhappy users (review gating).
- Android: Play In-App Review API - quota-limited, may not show; don't trigger from a button
  or ask a qualifying question first (Google guidance).
- Trigger after a positive moment (win, level-up, reward claim), never after a loss, crash,
  failed purchase or in the first session; cap internal attempts too.
- Respond to reviews (both stores) within ~48 h for negative ones on recent versions; tag themes
  for product; Apple allows resetting the summary rating on a new version (use after a fix release).

## Steam store page
| Asset | Size (px) | Notes |
|---|---|---|
| Header capsule | 920 x 430 | most-seen; logo legible at small size |
| Small capsule | 462 x 174 | 120x45 and 184x69 auto-derived - logo must read |
| Main capsule | 1232 x 706 | front-page features |
| Vertical capsule | 748 x 896 | sales/events pages |
| Library capsule | 600 x 900 | Steam library |
| Library hero / logo | 3840 x 1240 / 1280 x 720 (verify) | library page |
(Sizes changed 2024-08; old dimensions rejected - verify on Steamworks store assets page.)
- Capsules: game art + logo only (Valve rules restrict extra marketing text such as review
  scores/awards on capsules - verify current guidelines).
- Short description: genre + hook + what you do, in plain words; first 4-5 screenshots show
  gameplay variety; trailer starts with gameplay (no studio logos first).
- Tags: up to 20; order by relevance; match the genre players search; check comparables' tags.
- Coming Soon page: must be live >= 2 weeks before release; submit for review >= 7 business
  days before you want it live; wishlists and Community Hub open when public; Steam emails
  wishlisters at release. Valve: early wishlisters are about as likely to buy as late ones -
  publish once art direction and core features are settled.

### Wishlists and conversion (verify each year)
- GameDiscoverCo (launches Sep 2024 - Sep 2025): median week-1 sales ~0.15x launch wishlists
  for games with > 25k wishlists (0.14x excluding adult games); ~0.10x for games priced > $10;
  2024 developer poll (> 10k wishlists) median 0.17x, spread ~0.1x-10x of median.
- Older howtomarketagame tiers (~15-25% first-week conversion by wishlist band) come from a
  ~2020 sample - don't plan with them.
- Ad-driven wishlists convert worse than organic/festival wishlists (developer postmortems) -
  track wishlist sources via Steamworks UTM analytics.
- December (Winter Sale) launches convert worst (GameDiscoverCo).

### Steam Next Fest
- Three per year (2026: Feb 23-Mar 2, Jun 15-22, Oct 19-26; Feb 2027 planned Feb 22-Mar 1 -
  verify on Steamworks). Game must be unreleased; one Next Fest per game total; needs a
  public store page and a playable demo; demo builds reviewed beforehand (~4 weeks before for
  press preview, ~2 weeks before for public start - third-party guides, verify deadlines).
- Plan: page live months before → demo ready for the fest → livestream daily during the fest →
  release within the following months while wishlist momentum is warm.
- Other beats: genre fests (Valve-curated themed events), seasonal sales, Steam Playtest for
  pre-release testing.

## Sources
- Apple Custom product pages: https://developer.apple.com/app-store/custom-product-pages/
- Apple Product page optimization: https://developer.apple.com/app-store/product-page-optimization/
- Apple In-App Events: https://developer.apple.com/app-store/in-app-events/
- Google Play store listing experiments: https://support.google.com/googleplay/android-developer/answer/6227309
- AppTweak - Google Play custom store listings: https://www.apptweak.com/en/aso-blog/custom-store-listings
- Steamworks store graphical assets: https://partner.steamgames.com/doc/store/assets
- Steamworks Coming Soon: https://partner.steamgames.com/doc/store/coming_soon
- GameDiscoverCo - state of Steam wishlist conversions: https://newsletter.gamediscover.co/p/the-state-of-steam-wishlist-conversions
- Steamworks Next Fest (Oct 2026): https://partner.steamgames.com/doc/marketing/upcoming_events/nextfest/2026october
