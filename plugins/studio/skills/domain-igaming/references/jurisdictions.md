# Jurisdictions overview (informational, as of 2026-11 — needs human legal review)
Regulation changes yearly; treat every row as a starting point and re-verify on the regulator's
site before a market decision. Dates ISO.

## Comparison
| Market | Regulator / law | Licence types | Technical/game anchors | Notable player-protection rules |
|---|---|---|---|---|
| Great Britain | Gambling Commission (UKGC); Gambling Act 2005, LCCP, RTS | operating (B2C, remote casino etc.), gambling software (B2B), personal licences | RTS (updated 2025-10-31), approved test houses, annual security audit (ISO/IEC 27001:2022 basis) | GAMSTOP, slot stake caps, 10x wagering cap, financial risk checks (responsible-gambling-and-aml.md) |
| Malta | Malta Gaming Authority (MGA); Gaming Act 2018 (Cap. 583) | B2C / B2B gaming service licences; critical gaming supply | system audit + game certification via approved labs | Player Protection Directive; Bill 55 (2023) art. 56A shields licensees from some foreign judgments (contested; verify: pending CJEU references and Austrian/German enforcement rulings on curia.europa.eu, as of 2026-11) |
| Curacao | Curacao Gaming Authority (CGA); National Ordinance on Games of Chance (LOK), in force 2024-12-24 | direct B2C licence (indefinite term) and B2B supplier licence for critical goods/services (required from 2026-12-24); old LBH master/sub-licence system ended | certified RNG/software, CGA audits, critical records on a Tier-IV data centre server in Curacao (art. 5.9) | some legacy-transition decisions reported delayed into 2025-26 (Legal 500): check each licensee on the CGA register |
| Gibraltar | Gambling Commissioner / GRA; Gambling Act (2005; replacement Act in progress — verify: status/commencement on gibraltarlaws.gov.gi, as of 2026-11) | B2C, B2B | GRA technical/RG codes | gives no EU/UK market access by itself (each market needs its own licence); mainly UK-facing groups (practitioner view) |
| Isle of Man | Gambling Supervision Commission; Online Gambling Regulation Act 2001 | full/sub/network licences | testing via approved labs | AML/CFT code strong focus |
| Ontario (CA) | AGCO regulates; iGaming Ontario conducts and manages; market open since 2022-04-04 | operator + gaming-related supplier registration | Registrar's Standards for Internet Gaming; independent testing | no public inducement/bonus advertising; athletes banned from gambling ads since 2024-02-28 (verify: Advertising standards in AGCO Registrar's Standards, page last updated 2026-05-14) |
| New Jersey (US) | Division of Gaming Enforcement (DGE); N.J.A.C. 13:69O | casino-partnered operators; vendor licences | servers in Atlantic City, geolocation, lab testing (GLI/BMM) | 21+, self-exclusion list, RG messaging |
| Other US iGaming | PA (PGCB), MI (MGCB), WV, DE (lottery), CT (tribal + lottery), RI (2024); Maine legalised (LD 1164, tribal operators, effective 2026-07-29; launch expected 2027 after rulemaking) | per-state supplier + operator | per-state technical standards, in-state servers/geofence | age 21+; state self-exclusion lists |
| Sweden | Spelinspektionen; Gambling Act (2018:1138), licensing since 2019-01-01 | online casino/betting licences (5-year max) | accredited testing, Swedish servers/log access for regulator | Spelpaus (national self-exclusion), mandatory deposit limits, bonus only on first occasion, BankID identification, credit gambling banned (verify: 2025-26 amendments under SGA "Rules and regulation" at spelinspektionen.se, as of 2026-11) |
| Germany | GGL; Glücksspielstaatsvertrag 2021 (from 2021-07-01) | virtual slot machine, poker, betting licences | slots: EUR 1 max stake, ≥ 5 s per spin, no autoplay, no jackpots; 5.3% tax on stakes for virtual slots/online poker (verify: RennwLottG text, as of 2026-11) | OASIS self-exclusion, LUGAS cross-operator EUR 1,000 monthly deposit limit (adjustable) |
| Other EU | NL (Ksa, KOA 2021), DK, ES (DGOJ), IT (ADM), FR (ANJ, no online casino) | national | national tech standards | national self-exclusion registers (CRUKS NL, RGIAJ ES, ROFUS DK) |

## Great Britain detail (most demanding mainstream market)
- Age: verify age before any gambling including free-to-play demos (since 2019-05-07).
- Game design (RTS): slots ≥ 2.5 s game cycle (RTS 14 slot rules, 2021-10-31); from 2025-01-17:
  no spin-stop/turbo (14E), other casino ≥ 5 s cycle (14G), no autoplay for all gaming (8A),
  no celebrating returns ≤ stake (14F), no simultaneous play (14C), net position display (2E),
  elapsed time display (13C).
- Stakes: online slots max GBP 5 per spin (from 2025-04-09), GBP 2 for 18-24 year olds
  (from 2025-05-21) (verify: licence-condition text on gamblingcommission.gov.uk; not on the RTS page).
- Bonuses: wagering requirement cap 10x and ban on mixed-product promotions (from 2026-01-19).
- Credit cards banned for gambling (2020-04-14); GAMSTOP participation mandatory for online.
- Duty: remote gaming duty 21% → 40% from 2026-04-01; new 25% remote betting rate in General Betting
  Duty from 2027-04-01 (UK horse racing stays 15%); bingo duty abolished 2026-04-01 (Budget 2025-11-26).
  Statutory levy on operators also applies; re-check each Budget.

## US federal backdrop
- UIGEA (2006) targets payment processing for unlawful internet gambling; Wire Act scope
  (1st Cir. 2021: sports betting only) — states legalise intrastate; interstate pooling only for
  poker via MSIGA compacts (verify: current members/live states on state regulator sites, as of 2026-11).
- Sweepstakes: state-by-state bans spreading (business-models-and-platforms.md).

## What changes per jurisdiction in our code/config
| Area | Varies by | Implement as |
|---|---|---|
| RTP variants allowed | regulator floor/approval | certified math variant ID per market |
| Spin speed, autoplay, turbo, LDW celebration | UK, DE, NL, others | `JurisdictionProfile` flags in server config, delivered to client |
| Stake limits, deposit limits | UK, DE, SE, NL | server-enforced limits service |
| Session/time displays, reality check interval | UK, ES, others | client UI driven by server profile |
| Self-exclusion registry | GAMSTOP, Spelpaus, OASIS, CRUKS, state lists | adapter per registry, checked at login/registration |
| Data residency, regulator feeds | US states, SE, IT, ES | deployment per region; reporting jobs |
| Bonus rules | UK 10x, SE first-time only, Ontario ads | bonus engine rule sets per market |
- Never fork the game per market; one build + certified config per jurisdiction, hashed and listed
  on the certificate.

## Sources
- UKGC Remote gambling and software technical standards (last updated 2025-10-31) https://www.gamblingcommission.gov.uk/standards/remote-gambling-and-software-technical-standards
- Harris Hagan, RTS changes in force 2025-01-17 https://www.harrishagan.com/reminder-changes-to-remote-games-design-requirements-come-into-force-on-17-january-2025/
- OLBG, UKGC caps wagering requirements at 10x https://www.olbg.com/news/gambling-commission-cap-wagering-requirements-10x
- Mondaq, Curacao passes LOK https://www.mondaq.com/gaming/1572668/curaao-passes-lok-a-gamechanger-for-the-island39s-regulatory-framework
- Legal 500, Curacao gambling guide https://www.legal500.com/guides/chapter/curacao-gambling/
- Track360, US online casino legal states tracker 2026 https://track360.io/blog/us-online-casino-legal-states-tracker-2026
- GOV.UK, Changes to gambling duties (Budget 2025) https://www.gov.uk/government/publications/changes-to-gambling-duties
- Malta Gaming Authority https://www.mga.org.mt/ ; Spelinspektionen https://www.spelinspektionen.se/en/
