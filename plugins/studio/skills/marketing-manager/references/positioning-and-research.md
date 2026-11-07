# Positioning, audience and market research

## Audience definition (write as a card in `positioning.md`)
| Field | Content | Example |
|---|---|---|
| Primary motivations | Quantic Foundry model: 12 motivations in 6 pairs (Action, Social, Mastery, Achievement, Immersion, Creativity) | Completion + Strategy |
| Platform + device | where they play, session context | Android mid-range, commute |
| Session pattern | length x frequency | 5-8 min, 4-6x/day |
| Spend profile | payer share, typical spend, price sensitivity | low ARPPU, high payer conv. |
| Genre literacy | what they already play (3-5 titles) | Royal Match, Toon Blast |
| Demographics | secondary, for targeting only | 25-45, F-skewed |
| Anti-audience | who we will not chase | competitive PvP players |
- Source motivations from surveys, playtests and comparables' reviews, not intuition.
- Mobile casual mass-market vs PC core audiences behave differently: never reuse a persona
  across platforms without data.

## Competitor analysis
1. Pick 5-10 comparables: 3 direct (same core loop + audience), 2-3 adjacent (same audience,
   different loop), 1-2 aspirational (category leader).
2. Per comparable capture: downloads/revenue estimate (tool + date), monetization model, store
   page (icon, first 3 screenshots, video hook), ad creatives (Meta Ad Library, Google Ads
   Transparency Center), top 3 praised + top 3 criticized themes from reviews, liveops cadence,
   community size (Discord, subreddit, followers).
3. Synthesize: positioning map on 2 axes the audience cares about; white space; table stakes
   we must match; differentiators we can own.
| Comparable | Est. downloads/rev (tool, date) | Model | Hook (store/ad) | Praise | Complaints | Gap for us |
|---|---|---|---|---|---|---|

## Market-data tools (status 2026-11; verify pricing/access before buying)
| Tool | Coverage | Notes |
|---|---|---|
| Sensor Tower | mobile downloads/revenue, ad intel, PC/console via Video Game Insights | acquired data.ai (2024) and Video Game Insights (2025-03); sales-led pricing |
| AppMagic | mobile downloads/revenue estimates, tags/genres | cheaper alternative; check methodology per market |
| Appfigures, AppTweak, MobileAction | ASO keywords, rankings, featuring | ASO workflows |
| Liftoff GameRefinery | mobile feature/liveops/event intelligence | event tracker now also PC/console |
| SteamDB | Steam metadata, followers, CCU, price/sale history, upcoming releases | free |
| Gamalytic | Steam sales/revenue estimates | free tier + paid (~$25-75/mo, 2026, verify) |
| Video Game Insights (Sensor Tower) | Steam + PS/Xbox estimates | free tools remain; paid inside Sensor Tower |
| GameDiscoverCo (newsletter + Plus) | Steam/console trend analysis, wishlist data | paid tier for data |
| Meta Ad Library, Google Ads Transparency Center | competitors' live ads | free; creative research |
- All third-party numbers are estimates: cross-check two sources; report ranges, not points.
- Steam sales from reviews: "reviews x multiplier" (Boxleiter-style) estimates vary widely by
  price, genre and year (verify the current multiplier from GameDiscoverCo/Gamalytic data).

## Positioning statement (Moore template)
`For <target audience> who <need/motivation>, <game> is a <category/genre> that <key benefit>.
Unlike <primary alternative>, it <primary differentiator>.`
- Dunford's components (Obviously Awesome): competitive alternatives → unique attributes →
  value → best-fit customers → market category. Pick the category that makes the value obvious.
- Test: could a competitor sign the same statement? Then it isn't positioning.

## Messaging hierarchy
| Level | Content | Where it shows |
|---|---|---|
| 1. Core promise | <= 8 words, the fantasy/benefit | tagline, capsule/icon, first screenshot, first 3 s of video |
| 2. Pillars (3) | each with proof points | screenshots 2-4, trailer beats, store description opening |
| 3. Features / reasons to believe | concrete systems, content counts, social proof | description body, press kit, FAQ |
- Every creative and store asset maps to one level and one pillar; log the mapping.

## Validation before production lock
- Concept tests: 3-5 concept videos/statics on Meta or TikTok to a store page or landing
  page; compare CTR, IPM (mobile) or click-to-wishlist (Steam) under equal budgets and audience.
- Mobile prototype CPI test: compare against your genre's CPI/IPM benchmark (domain
  lifecycle-and-kpis.md); low IPM = hook/positioning problem before it is a game problem.
- Steam: announce trailer + page; measure wishlists/visit and follower growth by source (UTM).
- Survey + playtest: motivation profile of people who love the prototype = real audience.

## Market sizing (TAM / SAM / SOM)
| Layer | Definition | Method |
|---|---|---|
| TAM | all spend in the category/platform | analyst totals (Newzoo, Sensor Tower) - cite edition |
| SAM | segment you can serve (genre x platforms x geos x languages) | sum comparables' revenue in segment |
| SOM | realistic share in 1-3 years | bottom-up: reachable players x install conversion x LTV |
- Bottom-up SOM example (mobile): UA budget $2M / blended CPI $2.50 = 800k paid installs +
  organic uplift 0.5x = 1.2M installs x LTV $3.10 = ~$3.7M gross over the LTV window.
- Steam: distribution is hit-driven (median game sells little) - size from the comparable
  percentile you can credibly reach, not the category average.
- B2B/SaaS: count ICP accounts x ACV for SAM; SOM from pipeline capacity x win rate.

## Sources
- Quantic Foundry Gamer Motivation Model: https://quanticfoundry.com/
- Sensor Tower - Video Game Insights acquisition: https://sensortower.com/blog/video-game-insights-acquisition
- GameDiscoverCo - The state of Steam wishlist conversions: https://newsletter.gamediscover.co/p/the-state-of-steam-wishlist-conversions
- Meta Ad Library: https://www.facebook.com/ads/library/
- Google Ads Transparency Center: https://adstransparency.google.com/
- SteamDB: https://steamdb.info/
- Geoffrey Moore - Crossing the Chasm (3rd ed., 2014); April Dunford - Obviously Awesome (2019)
