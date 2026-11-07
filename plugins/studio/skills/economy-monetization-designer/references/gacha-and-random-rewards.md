# Gacha and random rewards (practitioner reference)
Legal content here is informational — every paid random mechanic goes to compliance-advisor;
market go/no-go "needs human legal review".

## Loot table structure
- Two-stage roll: rarity tier (weights) → item within tier (weights, often uniform). Publish both
  stages or the resulting per-item rate.
- Featured/rate-up: featured share f of the top tier (e.g. 50%) with a guarantee after a miss.
- Multi-pull guarantees: "10-pull ≥ 1 SR+" — changes effective rates; disclose consolidated rates.
- Duplicate handling: convert dupes to shards/currency (fixed rate) so no pull is worthless;
  or exclude owned items (changes odds dynamically — disclose rule).
- Weights live in server config with version + effective dates; rolls happen on the server with a
  CSPRNG; client only animates the result.

## Probability toolkit
| Question | Formula | p = 1% example |
|---|---|---|
| P(at least one in n pulls) | 1 - (1-p)^n | n=100 → 63.4% |
| Pulls for confidence t | n = ln(1-t) / ln(1-p) | 50%: 69, 90%: 230, 99%: 459 |
| Expected pulls (no pity) | 1/p | 100 |
| Collect all m equal items | m·H_m (H_m = Σ 1/k) | m=10 → 29.3 rolls of the tier |
| Expected cost | E[pulls] × price per pull | report mean, p90, p99 |
- Players feel the p90/p99 tail, not the mean: a 1% item leaves 1 in 10 players at 230+ pulls
  without pity. Design pity from the tail.

## Pity systems
| Type | Mechanic | Effect |
|---|---|---|
| Hard pity | guaranteed top item at pull N | caps worst case at N × price |
| Soft pity | rate ramps after pull K (e.g. +6%/pull) | most hits cluster before N; raises consolidated rate |
| 50/50 + guarantee | top item is featured with prob f; if not, next top is featured | E[tops per featured] = 2 - f (with f = 0.5 → 1.5) |
| Spark / exchange | each pull gives points; X points buy any featured item | deterministic cap; easy to explain and disclose |
| Carry-over | pity counter persists across banners | fairness; must be disclosed either way |
| Bad-luck protection (drops) | rate increases per failed kill/open | earned loot, PvE drop tables |
- Disclose base rate, consolidated rate (incl. pity), pity thresholds and carry-over rules.

## Runnable example: exact pity distribution and expected cost
```python
# Pity gacha: exact distribution of pulls-to-top-rarity + expected cost. Stdlib only.
def rate(k, base=0.006, soft=74, step=0.06, hard=90):   # P(top) on pull k since last top
    return 1.0 if k >= hard else min(1.0, base + max(0, k - soft + 1) * step)
def pulls_distribution(**kw):
    surv, dist, k = 1.0, [], 0
    while surv > 1e-12:
        k += 1; p = rate(k, **kw); dist.append(surv * p); surv *= 1 - p
    return dist                                    # dist[k-1] = P(first top on pull k)
def percentile(dist, t):
    acc = 0.0
    for i, q in enumerate(dist):
        acc += q
        if acc >= t: return i + 1
def summary(dist, price_per_pull, featured_share=0.5, guarantee=True):
    e = sum((i + 1) * q for i, q in enumerate(dist))
    # 50/50 with guarantee after a loss: expected tops per featured = 0.5*1 + 0.5*2 = 1.5
    tops = (2 - featured_share) if guarantee else 1 / featured_share
    return {"E_pulls_top": round(e, 1), "consolidated_rate": f"{1/e:.2%}",
            "p50/p90/p99": [percentile(dist, t) for t in (0.5, 0.9, 0.99)],
            "E_pulls_featured": round(e * tops, 1), "E_cost_featured": round(e * tops * price_per_pull, 2)}
if __name__ == "__main__":
    print(summary(pulls_distribution(), price_per_pull=2.0))             # soft pity 74+, hard 90
    print(summary(pulls_distribution(soft=10**9), price_per_pull=2.0))   # hard pity only
```
- Output: base 0.6% + soft pity from 74 + hard 90 → E = 62.3 pulls, consolidated 1.61%,
  p50/p90/p99 = 76/80/83, featured E = 93.4 pulls ≈ USD 187 at USD 2/pull. Hard pity only →
  E = 69.7, p50 = 90 (most players hit the cap). Shows why soft pity "feels" generous.
- Validate the live implementation: sample ≥ 10^6 server rolls in a test environment and run a
  chi-square goodness-of-fit per tier against configured weights (qa-engineer).

## Expected cost rules of thumb
- Publish the expected cost to obtain a specific featured item internally for every banner;
  compare with the JOGA (Japan) guideline: estimated amount for any rare item ≤ JPY 50,000, or
  ≤ 100x the price of one pull — otherwise display the estimate on the gacha page.
- Report p99 cost; if p99 > a sane monthly cap for your audience, add pity/spark.
- Paid-currency gacha priced in premium currency: also show real-money equivalent per pull
  (EU CPC 2025 principles; see monetization-models.md).

## Odds disclosure requirements (informational, checked 2026-11; recheck before launch)
| Market/platform | Rule | Status |
|---|---|---|
| Apple App Store | 3.1.1: disclose odds of each item type before purchase | in force (guidelines updated 2026-10-16) |
| Google Play | Payments policy: apps offering randomized virtual items ("loot boxes") "must clearly disclose the odds of receiving those items in advance of" purchase, close in time to it | in force (checked 2026-11) |
| China | odds + draw results disclosure (Ministry of Culture notice, 2016, eff. 2017-05-01); minors spend caps (NPPA 2019); 2023-12 NPPA draft (login rewards, spending limits) withdrawn | in force (verify: nppa.gov.cn for newer measures, as of 2026-11) |
| South Korea | mandatory probability disclosure in game, site and ads (Game Industry Promotion Act, eff. 2024-03-22); up to 3x punitive damages, burden on company (eff. 2025-08-01); KFTC fined Nexon KRW 11.6bn (2024-01) for MapleStory odds | in force (verify: status of the reported revenue-based fines bill on the National Assembly bill site, as of 2026-11) |
| Japan | kompu gacha (complete-a-set gacha) banned under Premiums and Representations Act (CAA, 2012-07); JOGA self-regulation: rates display, cost guideline | in force |
| Belgium | paid loot boxes treated as illegal gambling (Gaming Commission, 2018) | in force, enforcement weak (Xiao 2023 study) |
| Austria | Supreme Court OGH 6 Ob 228/24h (2025-12): FIFA Ultimate Team packs not gambling (skill predominates in the overall game); narrow ruling | other designs may still qualify |
| Netherlands | Council of State (2022-03-09) overturned Ksa fine vs EA (FIFA packs not a separate game of chance) | no ban; government backs an EU-level ban via the Digital Fairness Act; no national bill found (verify: tweedekamer.nl, as of 2026-11) |
| UK | no gambling classification; industry principles (Ukie, 2023): age controls, odds disclosure | voluntary (DCMS response 2022-07: no legislation) |
| Brazil | ECA Digital (Law 15.211/2025, in force 2026-03-17): loot boxes banned in games aimed at or likely accessed by minors; Decree 12.880/2026: age verification, or a loot-box-free version for minors; ANPD enforces | administrative sanctions from 2026-11, formal inspections from 2027-01 |
| Australia | paid chance-based items → minimum M; interactive simulated gambling → R18+ (from 2024-09-22) | in force for new classifications |
| EU (PEGI) | paid random items → PEGI 16 or 18 (new submissions from June 2026; details `studio:release-platform-manager` (age-ratings)) | in force; not retroactive, even for major updates of existing titles |
| Spain | organic bill on minors in digital environments (Congress 121/000052) bars under-18s from random reward mechanisms | pending (verify: congreso.es stage, as of 2026-11) |
| USA (FTC) | HoYoverse/Genshin (2025): USD 20M; no loot box sales to under-16 without parental consent; disclose odds and exchange rates | consent order |
| ESRB | "In-Game Purchases (Includes Random Items)" label | in force |

## Design rules (safe defaults)
- Show odds in-flow at the point of purchase (one tap max), in the player's language, per item
  or per tier + per item within tier; include pity rules. Studies found most Chinese titles used
  less prominent formats (Xiao 2024) — prominence matters to regulators.
- Offer a direct-purchase path for featured content where markets require/encourage it.
- Age-gate paid random rewards (16+/18+ per market); disable for declared minors where required.
- Never alter odds per player silently (no "dynamic odds" based on spend); any segmentation of
  rates must be disclosed and legally reviewed.
- Neutral reveal animations; no near-miss teasing; allow skip.
- Log every paid roll server-side: player, banner/version, pity counter, RNG draw, result, price
  — retain for audits and disputes (Korea/China enforcement relies on records).
- Changing rates mid-banner = disclosed patch note + compensation policy.

## Sources
- Apple App Review Guidelines 3.1.1 https://developer.apple.com/app-store/review/guidelines/
- Google Play Payments policy https://support.google.com/googleplay/android-developer/answer/9858738
- JOGA declaration 2024 (paid gacha guideline, JPY 50,000 / 100x) https://japanonlinegame.org/wp-content/uploads/2024/06/JOGA_declaration_2024.pdf
- Leon Y. Xiao et al., "Gaming the system: suboptimal compliance with loot box probability disclosure regulations in China" (Behavioural Public Policy, 2024) https://durham-repository.worktribe.com/output/1238986/gaming-the-system-suboptimal-compliance-with-loot-box-probability-disclosure-regulations-in-china
- Korea punitive damages for probability items (Yoon & Yang, 2025) https://www.legal500.com/developments/thought-leadership/punitive-damages-and-other-special-legal-provisions-for-litigation-concerning-probability-based-game-items/
- Brazil ECA Digital in force 2026-03-17 (Demarest) https://www.demarest.com.br/en/eca-digital-entrada-em-vigor-em-17-de-marco-de-2026/
- Mayer Brown, enforcement of Brazil's ECA Digital (2026-04) https://www.mayerbrown.com/pt/insights/publications/2026/04/enforcement-of-brazils-eca-digital-introduces-new-obligations-for-companies
- DLA Piper, OGH 6 Ob 228/24h (2026-01) https://www.dlapiper.com/insights/publications/2026/01/supreme-court-shifts-the-playing-field-lootboxes-fall-outside-the-austrian-gambling-act
- Osborne Clarke (ES), Spain's minors in digital environments bill https://www.osborneclarke.com/es/insights/espana-busca-proteger-los-menores-en-el-entorno-digital-claves-del-proyecto-de-ley
- Australian Classification: mandatory minimum classifications (2024) https://www.classification.gov.au/about-us/media-and-news/news/new-mandatory-minimum-classifications-for-gambling-games-content
- FTC business blog, HoYoverse settlement (2025-01) https://ftc.gov/business-guidance/blog/2025/01/level-tips-businesses-ftcs-settlement-genshin-impact-developer-hoyoverse
- Osborne Clarke, PEGI 2026 criteria https://www.osborneclarke.com/insights/games-loot-boxes-get-16-plus-age-rating-europe-under-pegi-overhaul
