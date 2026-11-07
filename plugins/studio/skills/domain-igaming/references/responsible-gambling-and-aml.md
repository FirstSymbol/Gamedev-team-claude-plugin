# Responsible gambling, KYC and AML (informational — needs human legal review)

## RG feature set (build for the strictest target market, configure down)
| Feature | Behaviour | Market anchors (verify current text) |
|---|---|---|
| Deposit limits | daily/weekly/monthly; decreases immediate, increases after cooling-off (often 24 h+) | UK LCCP; SE mandatory to set; DE LUGAS EUR 1,000/month cross-operator |
| Loss / wager / stake limits | per period; slot max stake per spin | UK slots GBP 5 (GBP 2 age 18-24) from 2025; DE EUR 1 |
| Session time limits | hard stop or warning at limit | ES, UK (voluntary tools), others |
| Reality check | pop-up at chosen interval with elapsed time + net position, links to history/limits | UK RTS 13; time and net position permanently shown in UK casino since 2025-01-17 (RTS 13C, 2E) |
| Time-out / cool-off | 24 h to 6 weeks, no marketing during | UK, MGA |
| Self-exclusion (operator) | ≥ 6 months, irrevocable for term, closes account, refunds balance | UK, MGA, Ontario, US states |
| National self-exclusion | check at registration/login | GAMSTOP (GB, mandatory for online since 2020-03-31), Spelpaus (SE), OASIS (DE), CRUKS (NL), RGIAJ (ES), ROFUS (DK), state lists (US) |
| Panic button | immediate 24 h block | DE (GlüStV 2021) |
| Activity statements | deposits, wagers, wins, net over periods | most licences |
| Safer-gambling messaging | links to help (e.g. GambleAware, 1-800-GAMBLER), age 18+/21+ | all |
- Server-side enforcement before the wallet debit; client only displays. Every limit change and
  exclusion event goes to the audit log with actor and timestamp.
- Self-excluded players: block login/registration (fuzzy matching on name/DOB/email/phone/
  address/payment), suppress all marketing, stop bonuses, handle open rounds and balance payout.

## Harm detection and customer interaction
- Markers (UKGC customer interaction guidance, 2022): time played, spend vs affordability,
  deposit frequency, chasing losses, late-night play, failed deposits, cancelled withdrawals,
  limit increases, multiple payment methods, contact with customer service about losses.
- Pipeline: event stream → risk score per player → tiered actions (message → limit prompt →
  human interaction → restriction) → outcomes logged. Data scientists own models; compliance
  owns thresholds (data-analyst + compliance-advisor).
- UK financial vulnerability checks: light-touch checks from GBP 500 net deposits in rolling
  30 days (2024-08-30), lowered to GBP 150 (2025-02-27); repeat at most once per 12 months.
  Enhanced financial risk assessments: pilot via 3 credit reference agencies (CRAs); UKGC
  confirmed a staged rollout 2026-07-07 (first stage: largest operators, highest spenders; reported
  trigger GBP 5,000 net deposits in 24 h, falling to GBP 1,000 when fully live; no enforcement in
  early stages) (verify: stage dates/thresholds in LCCP on the UKGC site, as of 2026-11).

## Age verification and KYC
- RMG: verify identity and age before deposit/play (UK: before any gambling incl. free demos since
  2019-05-07); US states: 21+ for casino; most other markets 18+.
- Methods: electronic ID checks (credit/identity bureaus), document + liveness (e.g. Onfido,
  Jumio, Veriff — vendor choice by market), bank ID (BankID SE/NO), eID (EU, ES DNIe).
- CDD: name, DOB, address, nationality; PEP and sanctions screening at onboarding and ongoing;
  EDD (source of funds/wealth) on risk triggers or spend thresholds set in the AML risk assessment.
- Social casino: no legal KYC, but age gate 18+ and no targeting of minors (platform + rating rules).
- Sweepstakes: KYC before redemption (prize payout), state eligibility checks.

## AML basics
- Programme: business-wide risk assessment, policies, MLRO/compliance officer, training, CDD/EDD,
  transaction monitoring, suspicious activity reporting (UK NCA SAR; US FinCEN SAR, CTR for
  cash > USD 10,000 at casinos; EU FIU per member state), record keeping ≥ 5 years.
- Typologies to detect: deposit → minimal play → withdrawal; chip dumping/collusion in P2P;
  third-party or many payment instruments; rapid deposit/withdraw cycles; structuring below
  thresholds; mismatched KYC vs payment owner; high-value low-volatility play (roulette both sides).
- Controls: closed-loop withdrawals (back to the deposit method), withdrawal requires KYC
  completion, turnover-before-withdrawal rules where legal, velocity limits, device/IP links.
- UK/EU: Money Laundering Regulations 2017 (UK); EU AMLR (Reg. 2024/1624) applies from 2027-07-10
  with gambling providers as obliged entities (CDD at EUR 2,000 transactions; member states may
  exempt only low-risk services such as lotteries, never casinos/online gambling/betting, recitals
  63-64); AMLA (Frankfurt) operating since 2025; national FIU reporting continues.

## Bonuses and marketing (constraints that shape product)
- UK: wagering requirement ≤ 10x and no mixed-product promotions (from 2026-01-19); clear T&Cs;
  no bonuses to self-excluded/at-risk players; marketing consent per channel.
- Sweden: bonus only at first occasion of play with a licensee (verify: 2025-26 amendments at
  spelinspektionen.se, as of 2026-11).
- Ontario: no public advertising of bonuses/inducements; athletes barred from gambling ads (2024-02-28).
- Spain: Royal Decree 958/2020 restricts advertising and welcome bonuses (verify: which articles
  the Tribunal Supremo annulled in its 2024 rulings — check BOE/ordenacionjuego.es, as of 2026-11).
- Germany: advertising restrictions, no bonus-funded autoplay; jackpots banned for virtual slots.
- Implement bonus rules as a rules engine with per-market config; QA tests each rule set.

## Product design checklist (RG by design)
- [ ] All limits and exclusions enforced server-side with audit log; tests per jurisdiction.
- [ ] Net position, elapsed time and reality checks per market profile.
- [ ] No autoplay/turbo/LDW celebrations where banned (UK RTS, see jurisdictions.md).
- [ ] Withdrawal flow cannot be reversed by player where banned (UK reverse-withdrawal ban, 2021 —
      verify: LCCP social responsibility code text, as of 2026-11); withdrawals not slower than deposits.
- [ ] Marketing suppression lists synced (self-excluded, cool-off, no consent).
- [ ] Help links and age notice on every gambling surface; customer service RG escalation path.

## Sources
- UKGC Remote gambling and software technical standards https://www.gamblingcommission.gov.uk/standards/remote-gambling-and-software-technical-standards
- Harris Hagan, RTS changes in force 2025-01-17 https://www.harrishagan.com/reminder-changes-to-remote-games-design-requirements-come-into-force-on-17-january-2025/
- CMS, UKGC response on financial risk and vulnerability checks https://cms.law/en/gbr/legal-updates/gambling-white-paper-consultations-the-commission-s-response-on-financial-risk-and-vulnerability-checks
- AffPapa, UKGC phased financial risk assessments (2026-07-08) https://affpapa.com/ukgc-set-to-roll-out-phased-financial-risk-assessments/
- EU AMLR, Regulation (EU) 2024/1624 https://eur-lex.europa.eu/eli/reg/2024/1624/oj
- OLBG, UKGC 10x wagering cap from 2026-01-19 https://www.olbg.com/news/gambling-commission-cap-wagering-requirements-10x
- GAMSTOP https://www.gamstop.co.uk/
- GLI-19 v3.0 (responsible gaming, accounts, complaints) https://gaminglabs.com/wp-content/uploads/2024/06/GLI-19-Interactive-Gaming-Systems-v3.0.pdf
- FinCEN, casinos and card clubs AML guidance https://www.fincen.gov/resources/statutes-regulations/guidance
