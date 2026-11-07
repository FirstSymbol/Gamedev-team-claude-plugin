# Loot boxes, virtual currencies and monetization law (informational — needs human legal review)
Design-side odds/pity math: `studio:economy-monetization-designer` (gacha-and-random-rewards).

## Loot box legal status by market (as of 2026-11; verify before launch)
| Market | Position | Key facts |
|---|---|---|
| Belgium | paid loot boxes = game of chance (illegal without licence) | Gaming Commission report 2018 under the 1999 Gaming Act; publishers removed paid boxes (e.g. FIFA points packs) or skipped launches; research shows weak enforcement and non-compliance (Xiao 2023) |
| Netherlands | not gambling per highest court | Ksa fined EA (2019, upheld 2020); Council of State overturned 2022-03-09 (FIFA packs part of a larger game of skill); government/parliament push an EU-level ban via the Digital Fairness Act; no national bill found (verify: tweedekamer.nl, as of 2026-11) |
| UK | outside gambling law | DCMS response 2022-07: no legislation, industry-led; Ukie principles 2023-07 (age controls, odds disclosure, spending controls); CAP/ASA guidance on in-game purchase ads |
| Austria | not gambling (FUT form) per Supreme Court | lower courts held FIFA packs gambling with refunds (BG Hermagor 2023); OGH 6 Ob 228/24h (2025-12) held FIFA Ultimate Team packs not a game of chance: assessed within the overall game, skill predominates; narrow — other loot box designs may still qualify |
| Germany | youth protection angle | JuSchG 2021 lets USK weigh in-game purchases/loot boxes in ratings + descriptors |
| Spain | pending | organic bill on protection of minors in digital environments (Congress 121/000052; totality amendment rejected 2025-09) bars under-18s from random reward mechanisms; government expected approval autumn 2026 (verify: congreso.es stage as of 2026-11) |
| Brazil | banned for minors | ECA Digital (Law 15.211/2025) in force 2026-03-17: loot boxes prohibited in games aimed at or likely accessed by children/adolescents; Decree 12.880/2026: age verification for games with loot boxes or a loot-box-free version for minors; ANPD enforces; fines up to 10% of the group's BR revenue (alternative per-user fine capped at BRL 50M; verify: art. 35 text), suspension or ban; administrative sanctions from 2026-11, formal inspections from 2027-01 |
| Australia | classification | from 2024-09-22: paid chance items → minimum M; interactive simulated gambling → R18+ |
| China | disclosure + minors | probability and result disclosure duty (since 2017); minors' spending caps; 2023-12 NPPA draft (login rewards, spending limits) withdrawn (verify: NPPA site for any newer measures, as of 2026-11) |
| South Korea | disclosure statute | mandatory probability disclosure (2024-03-22); 3x punitive damages, burden on company (2025-08-01); KFTC fines (Nexon KRW 11.6bn, 2024) |
| Japan | kompu gacha banned | Consumer Affairs Agency, Premiums and Representations Act (2012); JOGA guidelines |
| USA | no federal statute | FTC Act §5: HoYoverse USD 20M (2025, no loot boxes to under-16s without parental consent, odds/exchange-rate disclosure); state bills stalled; most consumer class actions dismissed or sent to arbitration (verify: 2025-26 docket status before relying) |
| EU-wide | soft law + pending law | CPC key principles on in-game virtual currencies (2025-03-21); DSA art. 28 minors guidelines (2025-07-14) target exploitative virtual currencies/loot boxes; Digital Fairness Act proposal expected late 2026 (verify: Commission work programme); PEGI 16 for paid random items (new submissions from June 2026) |

## EU consumer law applied to monetization
- Unfair Commercial Practices Directive 2005/29: misleading/aggressive practices; Annex I no. 28
  bans direct exhortation to children to buy ("Buy the gems now!" to a child audience = per se unfair).
- Consumer Rights Directive 2011/83: pre-contract information (price, trader identity, features);
  14-day withdrawal right — for digital content the right is lost only with the consumer's express
  prior consent + acknowledgement (art. 16(m)) before supply starts; capture both in the purchase flow.
- Omnibus Directive 2019/2161: disclose personalized pricing from automated decision-making;
  penalties up to ≥ 4% annual turnover for widespread infringements.
- Digital Content Directive 2019/770: conformity of purchased digital content; unilateral changes
  to purchased items need justification and notice.
- CPC key principles (2025), 7 points: (1) show prices in real money alongside virtual currency;
  (2) avoid obscuring cost (multi-currency, multi-step conversion); (3) don't force unwanted
  purchases (bundle sizes matching item prices); (4) pre-contractual transparency; (5) respect
  the 14-day withdrawal right incl. for unused currency; (6) fair, plain-language terms (no
  unilateral changes, ban appeals); (7) protect vulnerable consumers — children and high spenders;
  parental controls disable spending by default unless adult-only; age gates alone insufficient.
- CPC coordinated action against Star Stable Entertainment (launched 2025-03-21, led by SE and NO
  authorities; one month to propose commitments) applied these principles; CPC later opened
  actions against other publishers (King, Supercell, Mojang reported). No published outcome found
  (verify: Commission coordinated-actions page, as of 2026-11).

## US consumer law
- FTC Act §5 (unfair/deceptive): Epic 2022 — USD 245M refunds for dark patterns (single-button
  purchases, charges without consent, locking accounts after chargebacks); HoYoverse 2025 —
  misrepresented odds/costs of loot boxes; children's purchases.
- ROSCA + state auto-renewal laws for subscriptions (platform-and-consumer-rules.md).
- FTC "Click-to-Cancel" negative option rule was vacated by the 8th Circuit (2025-07); state laws
  still apply (e.g. California ARL as amended by AB 2863, in force 2025-07-01).

## Virtual currency rules checklist
- [ ] Real-money equivalent visible for currency packs and for items priced in currency.
- [ ] One purchasable currency if possible; no exchange chains hiding price.
- [ ] Pack sizes allow buying exact item prices; leftover currency minimized.
- [ ] No expiry of purchased currency (Apple 3.1.1; EU fairness); event currency rules disclosed.
- [ ] Withdrawal-right waiver captured (EU/UK) before delivery; receipts by email/store.
- [ ] Parental controls respected; spending off by default for child-likely audiences (CPC 7).
- [ ] Terms: no unilateral confiscation without reason; account ban appeal path; refund policy.
- [ ] No sale or transfer of currency between players unless designed and legally reviewed
      (money transmission, gambling and AML risks).

## Refunds and chargebacks
| Channel | Mechanism | Game action |
|---|---|---|
| Apple App Store | Apple decides refunds; App Store Server Notifications v2 `REFUND`, `REFUND_REVERSED`, `CONSUMPTION_REQUEST` (any product type): send consumption data via Send Consumption Information within 12 h only if the customer gave valid, separate consent (not via ATT); else don't respond | revoke unspent consumables, revert entitlements; log |
| Google Play | Voided Purchases API + real-time developer notifications; user refunds via Play | same; poll Voided Purchases daily |
| Steam | games: 14 days / < 2 h playtime; in-game purchases refundable via Steam only in Valve games (48 h) unless the developer enables refunds | no refund callback: poll `ISteamMicroTxn/GetReport` (status Refunded/Chargedback), `QueryTxn` per order |
| Web/PSP | chargebacks via card schemes | dispute evidence, 3DS; fraud review |
- Clawback: deduct refunded currency; allow negative balance only with clear ToS; never lock
  access to unrelated paid content as punishment for disputes (Epic/FTC).
- Abuse: repeated refund-after-consumption → limit purchases, flag account, human review.
- Track refund rate per SKU/market (data-analyst); spikes signal UX confusion or fraud.

## When to escalate immediately
- Paid random items in BE/BR(minors)/any market with pending bans; odds disclosure gaps; selling
  currency or random items to likely-children; secondary markets/cash-out; sweepstakes features.

## Sources
- CPC key principles summary (ZwillGen, 2025) https://www.zwillgen.com/gaming/cpcn-announces-virtual-currency-consumer-protection-guidelines/
- Consumer Rights Directive 2011/83/EU https://eur-lex.europa.eu/eli/dir/2011/83/oj
- FTC Epic Games settlements (2022-12-19) https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations
- FTC business blog on HoYoverse/Genshin (2025-01) https://ftc.gov/business-guidance/blog/2025/01/level-tips-businesses-ftcs-settlement-genshin-impact-developer-hoyoverse
- Demarest, ECA Digital in force 2026-03-17 https://www.demarest.com.br/en/eca-digital-entrada-em-vigor-em-17-de-marco-de-2026/
- Australian Classification, mandatory minimum classifications https://www.classification.gov.au/about-us/media-and-news/news/new-mandatory-minimum-classifications-for-gambling-games-content
- Leon Y. Xiao, "Breaking Ban: Belgium's ineffective gambling law regulation of video game loot boxes", Collabra: Psychology (2023).
- Xiao, "Gaming the system" (China disclosure compliance, 2024) https://durham-repository.worktribe.com/output/1238986/gaming-the-system-suboptimal-compliance-with-loot-box-probability-disclosure-regulations-in-china
- DLA Piper, OGH 6 Ob 228/24h: loot boxes outside Austrian Gambling Act (2026-01) https://www.dlapiper.com/insights/publications/2026/01/supreme-court-shifts-the-playing-field-lootboxes-fall-outside-the-austrian-gambling-act
- Mayer Brown, enforcement of Brazil's ECA Digital (2026-04) https://www.mayerbrown.com/pt/insights/publications/2026/04/enforcement-of-brazils-eca-digital-introduces-new-obligations-for-companies
- Trench Rossi, Brazil regulates ECA Digital (Decree 12.880/2026) https://www.trenchrossi.com/en/legal-alerts/brazil-regulates-the-children-and-adolescents-online-safety-act-digital-eca
- Osborne Clarke (ES), Spain's minors in digital environments bill https://www.osborneclarke.com/es/insights/espana-busca-proteger-los-menores-en-el-entorno-digital-claves-del-proyecto-de-ley
- Spanish consumer authority, CPC action on Star Stable (2025) https://portal-cec.consumo.gob.es/en/comunicacion/noticias/2025/european-commission-and-national-authorities-act-protect-children
- Apple, Send Consumption Information (12 h, consent) https://developer.apple.com/documentation/appstoreserverapi/send-consumption-information
- Steam refunds policy https://store.steampowered.com/steam_refunds/ ; Steamworks ISteamMicroTxn https://partner.steamgames.com/doc/webapi/ISteamMicroTxn
- Lewis Silkin, Digital Fairness consultation responses (2026-01) https://www.lewissilkin.com/insights/2026/01/14/european-commission-issues-responses-to-digital-fairness-consultation-102m1s7
