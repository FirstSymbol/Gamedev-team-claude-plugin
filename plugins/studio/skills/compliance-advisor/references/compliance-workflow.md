# Compliance workflow (how this advisor works)

## When reviews happen
| Gate | Trigger | Output |
|---|---|---|
| G0 concept | new product/market, business model (RMG/social/sweeps/F2P) | market matrix + model classification questions for counsel |
| G1 spec | PRD/GDD/economy spec touching any trigger below | CR report on the spec (cheapest time to change) |
| G2 pre-build | SDK selection, data flows, payment/ads vendors | SDK/DPA inventory, consent design |
| G3 pre-release | release candidate, store listing, ratings | release checklist sign-off request to counsel |
| G4 live | live events, new offers, law changes | delta review; watch-list update |

## Trigger → checklist
| Trigger | Must check (load reference) |
|---|---|
| Personal data (any analytics, login, ads, chat) | lawful basis per purpose, consent/CMP, notices, SDK DPAs, transfers, retention, DSR flow, localization (privacy.md) |
| Children / mixed audience | age assurance, COPPA VPC, AADC defaults, no profiling ads, purchase controls, ratings (privacy.md, platform-and-consumer-rules.md) |
| Virtual currency / IAP | real-money price display, bundle sizes, refunds/withdrawal, expiry, parental controls (loot-boxes-and-monetization-law.md) |
| Paid random items | odds disclosure per market, bans (BE, BR minors), ratings (PEGI 16, AU M), pity disclosure (loot-boxes-and-monetization-law.md) |
| Prize + chance + consideration | gambling classification per market → studio:domain-igaming; counsel mandatory |
| Ads / influencers / UA | disclosure, child-directed limits, gambling ad rules, claims substantiation (platform-and-consumer-rules.md) |
| Subscriptions / auto-renew | pre-purchase terms, renewal notices, easy cancel (platform-and-consumer-rules.md) |
| UGC / chat / social | moderation, reporting/blocking, DSA (EU) duties, ratings impact (verify) |
| Accessibility | EAA scope for e-commerce/communication features (platform-and-consumer-rules.md) |
| Time-limited offers, login streaks | dark patterns, PEGI 2026 criteria, EU CPC principles |

## Risk rating
- Likelihood (L1 rare … L3 likely: enforcement history, regulator focus, complaint-prone feature)
  × Impact (I1 minor … I3 severe: fines, store removal, criminal exposure, refunds, reputation).
| Score | Rating | Rule |
|---|---|---|
| 6-9 | High | blocker until mitigated or counsel accepts in writing |
| 3-4 | Medium | mitigation planned before release; counsel informed |
| 1-2 | Low | log and monitor |
- Automatic High: gambling classification uncertainty, children's data without VPC, paid loot
  boxes in a banning market, missing odds disclosure on a store requiring it, data transfers to a
  restricted jurisdiction without a mechanism.

## Escalate to a human lawyer (always)
- Any go/no-go: market launch, business-model choice, new monetization mechanic in a regulated
  market, sweepstakes/RMG anything.
- Drafting or changing ToS, privacy policy, EULA, official sweepstakes rules, refund policy.
- Regulator, platform or law-enforcement contact; data breach; player dispute with legal threat.
- Conflicting sources or no primary source found; High risks.
- Counsel pack format (≤ 1 page): facts (what the feature does, markets, audience), the specific
  questions, options with trade-offs, sources consulted (dated), deadline.

## Research recipe
1. Primary sources first: statute/regulation text (EUR-Lex, legislation.gov.uk, state legislature,
   pravo.gov.ru), regulator guidance (EDPB, ICO, FTC, UKGC, CPPA), store policy pages.
2. Then case law/decisions, then law-firm briefings (date them), press last (leads only).
3. Record: claim → source URL → publication/effective date → retrieval date.
4. If sources conflict or are older than 12 months for a fast-moving topic → `(verify: …)` + escalate.
5. Never fabricate citations; "not found" is a valid finding.

## Documentation trail
- CR report per feature/version (`.team/reports/compliance/CR-NNN-<slug>.md`), immutable once
  issued; changes = new CR referencing the previous one.
- Risks in `.team/risks.md` with owner and state; decisions by humans recorded as ADRs
  (`.team/decisions/ADR-NNN-*.md`) with counsel's name/role and date (no legal text pasted).
- Market matrix (`.team/specs/compliance/market-matrix.md`): market × trigger → status, CR link,
  last verified date.
- Watch list: laws pending (e.g. EU Digital Fairness Act proposal, Spain loot-box bill, Korea
  revenue-based fines, US state sweepstakes bills) with next check date.

## Regulatory watch list (as of 2026-11; verify)
| Item | Status | Relevance |
|---|---|---|
| EU Digital Fairness Act | proposal expected late 2026 | virtual currencies, loot boxes, dark patterns, minors |
| Spain minors digital protection bill | in parliament; loot box ban for under-18s | Spain launches |
| Korea revenue-based fines for probability items | bill pending | KR gacha |
| Brazil ECA Digital enforcement | sanctions from 2026-11, enforcement 2027 | BR loot boxes, age verification |
| US state sweepstakes bans | spreading (CA 2026, NY, more) | sweeps model |
| UK gambling reforms | stake caps, bonus caps done; levy/duty changes | RMG UK |
| PEGI criteria (June 2026) | in force for new submissions | ratings of new titles |

## Sources
- EDPB guidelines index https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en
- ICO Age appropriate design code https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/
- FTC business guidance https://www.ftc.gov/business-guidance
- EU Digital Fairness Act consultation summary (Lewis Silkin, 2026-01) https://www.lewissilkin.com/insights/2026/01/14/european-commission-issues-responses-to-digital-fairness-consultation-102m1s7
- Yoon & Yang on Korea probability-item rules (2025) https://www.legal500.com/developments/thought-leadership/punitive-damages-and-other-special-legal-provisions-for-litigation-concerning-probability-based-game-items/
