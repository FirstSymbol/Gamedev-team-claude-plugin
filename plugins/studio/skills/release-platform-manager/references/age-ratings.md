# Age ratings (checked 2026-11)
Ratings are determined by content questionnaires; answer from the actual build and keep answers consistent
across systems. Legal effect per country (and loot box law) → compliance-advisor; casino math → studio:domain-igaming.

## Which system where
| Channel | System | Cost/process |
|---|---|---|
| IARC storefronts (globalratings.com, 2026-11): Google Play, Microsoft, Nintendo, Sony PlayStation, Epic Games, Meta Horizon, One Store, Pico, Luna, YouTube Playables, Facebook Gaming, Fortnite | IARC questionnaire → ratings for participating authorities (ESRB, PEGI, USK, ClassInd, ACB, GRAC, Taiwan DGSC, Saudi GAMR, Indonesia IGRS) + generic age elsewhere | free, minutes; ratings can be audited/changed post-launch |
| Apple App Store | Apple's own questionnaire (App Store Connect → App Information) → 4+, 9+, 13+, 16+, 18+; regional overlays (Australia, Brazil, Korea) | free; new questionnaire mandatory since 2026-01-31 |
| Physical/boxed console & PC retail | full certificates: ESRB (long form), PEGI, USK, CERO, ACB, etc. | fees, weeks; schedule it (verify: fee schedule and lead time on each board's site at booking) |
| Digital console (PS/Xbox/Switch) | Sony PlayStation, Microsoft, Nintendo are IARC storefronts; CERO (Japan) is not an IARC participant → Japan needs a CERO rating; confirm per platform holder's submission docs | |
| Steam | Content Survey (mature content, AI disclosure) drives Valve's own rating; ratings mandatory in Germany since 2024-11-15 (real USK rating or Valve rating; unrated titles hidden in DE) and required for Indonesia (IGRS or Valve); IARC ratings from other stores must not be entered as USK/IGRS | free |

## Rating scales
| Board | Region | Labels |
|---|---|---|
| ESRB | US/Canada | E, E10+, T, M (17+), AO (18+); descriptors incl. **Simulated Gambling**, **Real Gambling** (AO); interactive elements: In-Game Purchases, **In-Game Purchases (Includes Random Items)** (since 2020), Users Interact, Shares Location, Unrestricted Internet |
| PEGI | Europe (most countries), UK | 3, 7, 12, 16, 18; descriptors: violence, bad language, fear/horror, gambling, sex, drugs, discrimination, in-game purchases, paid random items |
| USK | Germany | 0, 6, 12, 16, 18; since 2023 also weighs online risks (purchases, loot boxes, chat) with additional notices |
| CERO | Japan | A (all), B (12+), C (15+), D (17+), Z (18+, legally restricted) |
| ACB / Classification Board | Australia | G, PG, M, MA15+, R18+, RC (refused) |
| ClassInd | Brazil | L, 10, 12, 14, 16, 18 (Apple shows AL, A6-A18 pictograms) |
| GRAC | Korea | All, 12, 15, 18 (self-rating via IARC/platforms for mobile) |
| Apple | global | 4+, 9+, 13+, 16+, 18+ (12+/17+ removed in 2025) |

## Simulated gambling (social casino, slots, poker without cash-out)
| System | Outcome |
|---|---|
| Apple | infrequent simulated gambling → 13+; frequent → 18+; real gambling → 18+; Australia: any simulated gambling → R18+ regional rating |
| PEGI | simulated casino-style games of chance → PEGI 18 (since 2020); games that prominently reference gambling → PEGI 12; social casino → PEGI 18 under the June 2026 criteria |
| Australia (Classification Board, from 2024-09-22) | simulated gambling → mandatory minimum R18+ (legally adults only); not retroactive for earlier classifications |
| ESRB | "Simulated Gambling" descriptor; rating set by overall content (social casino often T - verify: per-title result of your IARC/ESRB submission vs comparable titles on esrb.org); "Real Gambling" → AO |
| IARC/Google Play | questionnaire asks simulated gambling explicitly; results per region (expect 18 in PEGI/ACB regions) |
| Real-money gambling | outside game ratings: licenses per jurisdiction, store-specific approval (Google RMG program, Apple 5.3.4) |
Practical: a social casino title should plan for 18+ in EU/AU/Apple-frequent, age-gate at 18 in-app where
required, keep marketing assets consistent with 18+ (compliance-advisor confirms per market).

## Loot boxes / paid random items
| System | Label / effect |
|---|---|
| ESRB | Interactive Element "In-Game Purchases (Includes Random Items)" - does not change the age rating |
| PEGI (from June 2026, new submissions) | paid random items → PEGI 16 or 18 (18 for social casino); time-limited offers → PEGI 12 (7 if spending disabled until a parent enables it); pressure-to-play (dailies, streaks) → 7, → 12 if players lose rewards/status for not returning; NFT/blockchain → 18; unrestricted communication → 18 unless safeguards |
| PEGI (pre-June 2026) | "In-game Purchases (Includes Paid Random Items)" notice; not retroactive - existing titles need not be reclassified, even after substantial updates (Osborne Clarke 2026) |
| Australia (from 2024-09-22) | in-game purchases linked to chance (paid loot boxes) → minimum M |
| Apple | loot boxes → 9+ globally; Australia 16+; Brazil A18; odds disclosure mandatory (3.1.1) |
| Google Play | odds disclosure before purchase (Payments policy) |
| Country law (examples) | Belgium treats paid loot boxes as gambling (2018 regulator view); Japan bans "complete gacha"; China and South Korea (since 2024-03-22) mandate probability disclosure → compliance-advisor |
Design impact: the PEGI 2026 rules make F2P mechanics (gacha, streak penalties, FOMO timers, open chat) rating
inputs. Share this table with economy-monetization-designer and liveops-manager before features lock.

## Questionnaire workflow
1. Inventory content from the build + live-ops roadmap (events add content later): violence, language,
   sexual content, drugs, gambling frequency, purchases (random? time-limited?), chat/UGC, location sharing,
   unrestricted web, ads.
2. Answer once in a master sheet `.team/specs/release/ratings-<platform>.md` with rationale per answer.
3. Submit IARC (via the storefront's console), Apple questionnaire, Steam Content Survey from that sheet.
4. Re-run when content changes (new chat feature, gacha, casino mini-game) - ratings can be revised and
   storefronts may remove mis-rated apps.
5. Store results (certificate IDs, rating per region) for marketing assets and in-game legal screens.

## Sources
- App Store Connect Help, Age ratings reference https://developer.apple.com/help/app-store-connect/reference/age-ratings
- PEGI, What do the labels mean https://pegi.info/what-do-the-labels-mean
- Osborne Clarke, Games with loot boxes get 16+ age rating in Europe (2026) https://www.osborneclarke.com/insights/games-loot-boxes-get-16-plus-age-rating-europe-under-pegi-overhaul
- ESRB, In-Game Purchases (Includes Random Items) https://www.esrb.org/ratings-guide/in-game-purchases
- ESRB Ratings guide https://www.esrb.org/ratings-guide/
- IARC participants https://globalratings.com/participants/ ; storefronts https://globalratings.com/storefronts/
- Steamworks, Age ratings mandatory in Germany https://partner.steamgames.com/doc/gettingstarted/contentsurvey/germany ; Indonesia https://partner.steamgames.com/doc/gettingstarted/contentsurvey/indonesia
- Australian Classification, New mandatory minimum classifications for gambling-like content https://classification.gov.au/about-us/media-and-news/news/new-mandatory-minimum-classifications-for-gambling-games-content
- CERO rating system https://www.cero.gr.jp/en/publics/index/17/
- USK https://usk.de/en/
