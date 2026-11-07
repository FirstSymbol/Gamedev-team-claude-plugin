# Privacy and data protection for games (informational — needs human legal review)

## GDPR / UK GDPR essentials
- Scope: EU establishment, or offering games to / monitoring people in the EU (art. 3(2)); UK GDPR
  + DPA 2018 for UK, amended by the Data (Use and Access) Act 2025 (Royal Assent 2025-06-19; most
  UK GDPR changes commenced 2026-02-05; ICO replaced by the Information Commission 2026-09-30;
  verify: complaints-handling duty commencement on GOV.UK, unconfirmed as of 2026-11).
- Fines up to EUR 20M or 4% of global turnover; breach notification to the supervisory authority
  within 72 h (art. 33), to players without undue delay if high risk (art. 34).

### Lawful basis per purpose (typical game mapping; confirm per product)
| Purpose | Basis | Notes |
|---|---|---|
| Account, gameplay, cloud save, purchases | contract (6(1)(b)) | only what the service needs |
| Anti-cheat, fraud, security logs | legitimate interests (6(1)(f)) | written LIA; proportionate retention |
| Product analytics | legitimate interests or consent | device access for non-essential SDKs needs ePrivacy consent (art. 5(3)) |
| Personalized ads, attribution, cross-app tracking | consent (6(1)(a)) | via CMP; separate from ToS acceptance |
| Marketing push/email | consent (and ePrivacy rules) | per channel, withdrawable |
| Tax, invoicing, AML (RMG) | legal obligation (6(1)(c)) | retention per law |
| Age estimation (face/biometrics) | special-category rules if biometric ID (art. 9) | prefer non-biometric methods |
- ePrivacy art. 5(3): storing/reading anything on the device (IDs, SDK storage, fingerprinting)
  needs consent unless strictly necessary; EDPB Guidelines 2/2023 read this broadly (SDKs, pixels).
- Consent quality (EDPB Guidelines 05/2020): freely given (not bundled with play unless necessary),
  specific per purpose, informed, unambiguous, reject as easy as accept, withdrawable in settings,
  logged (who/when/what version).
- Children: information-society consent age 13-16 by member state (art. 8; e.g. 16 DE/IE/NL,
  15 FR, 14 ES/IT, 13 UK/BE/DK; verify: national acts as of 2026-11, ES minors-in-digital-
  environments bill would raise 14 → 16); below it, parental consent with reasonable verification.

### DPIA (art. 35)
- Do one when: children's data at scale, behavioural profiling for monetization/ads, large-scale
  tracking, voice/chat recording, biometric age checks, new tech. UK AADC requires a DPIA for
  services likely accessed by children. Keep it versioned in `.team/reports/compliance/`.

### Data subject rights
- Access, rectification, erasure, restriction, portability, objection; answer within 1 month
  (+2 if complex). Verify identity proportionately (in-game account auth is fine).
- In-app account deletion is also a store rule: Apple 5.1.1(v) (since 2022-06-30); Google Play
  requires an in-app deletion path AND a web link resource (works after uninstall), declared in
  the Data safety form; associated data must be deleted too (retention exceptions disclosed).
- Deletion must propagate to processors/SDK vendors (APIs: Firebase, Unity Analytics, AppsFlyer, etc.).

### Processors, SDKs, DPAs
- Inventory every SDK: purpose, data, role (processor vs independent controller), DPA/terms,
  transfer mechanism, retention, consent dependency. Ad networks/attribution are often
  independent controllers → disclose as recipients, need consent.
- Art. 28 DPA with processors (backend hosting, analytics, support tools, CRM).

### International transfers (chapter V)
- Adequacy (incl. EU-US Data Privacy Framework, adequacy decision 2023-07-10; annulment action
  dismissed by the EU General Court 2025-09-03, T-553/23 Latombe; verify: status of any appeal to
  the Court of Justice on curia.europa.eu as of 2026-11), else SCCs (2021/914) + transfer
  impact assessment; UK: IDTA or UK Addendum. Russia/China: see below + counsel.

## Consent management for games (EEA/UK/CH)
- Google requires a Google-certified CMP integrated with IAB TCF for ads served via AdMob/Ad
  Manager/AdSense in EEA and UK (since 2024-01-16) and Switzerland (since 2024-07-31). Options: Google UMP SDK (free,
  Unity plugin via Google Mobile Ads), or certified CMPs (Usercentrics, OneTrust, Didomi …).
- IAB TCF v2.2 (2023) dropped legitimate interest for ads personalization; TCF participants had to
  adopt v2.3 by 2026-02-28 (IAB Europe) — keep CMP SDKs current.
- Order on first launch: age gate (if mixed audience) → CMP (EEA/UK) → iOS ATT prompt (only if
  tracking) → initialize ad/attribution SDKs with consent signals. Mediation SDKs must receive
  consent flags (AppLovin MAX, LevelPlay `setConsent`, etc.).
- iOS: App Tracking Transparency for IDFA/cross-app tracking (iOS 14.5+); privacy nutrition
  labels and privacy manifests (`PrivacyInfo.xcprivacy`, required-reason APIs) must match SDKs.
- Android: `AD_ID` permission declaration (Android 13+), Data safety form in Play Console.
- US: IAB Global Privacy Platform (GPP) strings for state opt-outs; honor Global Privacy Control.

## CCPA / CPRA (California) and US states
- Applies to businesses over thresholds (annual revenue > USD 26,625,000, CPI-adjusted from
  2025-01-01, next adjustment due 2027; or 100k+ consumers/households; or ≥ 50% revenue from
  selling/sharing PI).
- Duties: notice at collection, "Do Not Sell or Share" (cross-context behavioural ads = sharing),
  limit use of sensitive PI, DSR within 45 days, honor GPC, contracts with service providers.
- Minors: opt-in required to sell/share data of under-16s (13-15 themselves, under 13 a parent).
- CPPA regulations on risk assessments, ADMT and cybersecurity audits approved by OAL 2025-09-23,
  effective 2026-01-01: ADMT duties from 2027-01-01; pre-2026 processing assessed by 2027-12-31,
  risk-assessment submissions due 2028-04-01; cybersecurity audit certifications 2028-04-01
  (revenue > USD 100M), 2029-04-01 (USD 50-100M), 2030-04-01 (< USD 50M).
- ~20 other state comprehensive privacy laws (VA, CO, CT, TX, OR, …) plus kids' design/age laws;
  build one high-water-mark US flow (verify: per-state effective dates and minors' rules on the
  state AG/legislature sites before each launch).

## COPPA (US, under 13)
- Applies if directed to children (subject matter, visuals, characters, music, ads, audience
  evidence) or with actual knowledge of under-13 users. Mixed audience: neutral age screen,
  route under-13s to a no-PI or VPC path.
- Personal information includes persistent identifiers (device ID, cookies) used for ads/profiling;
  "support for internal operations" exception covers security, frequency capping limits, etc.
- Verifiable parental consent before collection; 2025 amendments (published 2025-04-22, effective
  2025-06-23, compliance by 2026-04-22): separate VPC for disclosing to third parties (e.g. ads),
  written information security program, written data retention policy published online,
  third-party recipients named in the privacy notice.
- FTC COPPA policy statement (2026-02-25): enforcement discretion for general/mixed-audience
  services collecting child data solely for age verification (use limited to that, prompt
  deletion, notice, security, reasonably accurate method); does not require age verification,
  does not bind state AGs; COPPA Rule review on age verification announced.
- Enforcement in games: Epic/Fortnite USD 275M civil penalty (2022); HoYoverse/Genshin USD 20M
  incl. COPPA claims (2025). Safe harbors: ESRB Privacy Certified, kidSAFE, PRIVO, CARU.
- Child-directed: no behavioural ads, certified family ad networks only (Google Play Families
  policy), no open chat without parental controls.

## UK Age Appropriate Design Code (Children's code, since 2021-09-02)
- Applies to online services likely to be accessed by under-18s in the UK (games included).
- 15 standards: best interests; DPIA; age-appropriate application; transparency; detrimental use
  of data; policies and community standards; default settings (high privacy); data minimisation;
  data sharing; geolocation (off by default); parental controls (child told when monitored);
  profiling (off by default); nudge techniques (no nudging to lower privacy or extend play);
  connected toys/devices; online tools (easy rights exercise).
- Games-specific: no nudges to spend/play longer for children, default-off chat with strangers,
  age assurance proportionate to risk. UK Online Safety Act 2023 adds duties for user-to-user
  features (chat, UGC): children's risk assessments, highly effective age assurance (children's
  safety duties in force 2025-07-25; verify against Ofcom's current codes).
- EU parallel: DSA art. 28 + Commission guidelines on protection of minors (2025-07-14) for online
  platforms accessible to minors (micro/small enterprises exempt): private-by-default accounts,
  streaks/push off by default, no exploitative virtual currencies/loot boxes, age verification
  for gambling-type content; voluntary benchmark the Commission uses to assess art. 28(1).

## Russia — Federal Law 152-FZ (as of 2026-11; confirm with Russian counsel)
- Localization (art. 18(5), since 2015): recording, systematization, accumulation, storage,
  updating and retrieval of Russian citizens' personal data must use databases in Russia.
  Amendment 23-FZ (2025-02-28, in force 2025-07-01) made it an express prohibition on using
  foreign databases for these actions, incl. initial collection (online too), and extended it to
  processors; after initial collection in Russia, transfer abroad stays possible under the
  cross-border rules (art. 6(1) cl. 2, 3, 4, 8 exceptions unchanged).
- Roskomnadzor: notify before processing (operator registry); cross-border transfers require prior
  notification and assessment of the recipient country (since 2023-03-01).
- Consent: specific, informed, conscious; from 2025-09-01 (156-FZ, art. 9(1)) consent must be
  obtained separately from any other document (not inside ToS/offer/contract; own checkbox in
  web forms); consent for distribution of PD made public is separate.
- Liability: 420-FZ (from 2025-05-30): first leak RUB 3-15M by scale (from 1k subjects / 10k IDs);
  repeat leak 1-3% of prior-year revenue, min RUB 20M (one review of the final text says 25M),
  max RUB 500M; localization breach up to RUB 6M / 18M repeat. Criminal art. 272.1 Criminal Code
  (421-FZ, from 2024-12-11) for illegal use/transfer of computer-held PD.
- Practical pattern: primary account/identity DB hosted in Russia; transfer abroad only after
  notification and legal basis; review each Western SDK (availability, transfers, sanctions);
  separate RU build/backend region if needed. Sanctions/export-control questions → counsel.

## Data minimization checklist for games
- [ ] Collect DOB/age band only if needed for age-appropriate flows; store age band, not DOB.
- [ ] Chat/voice: retention limits, moderation logs separate, no training use without basis.
- [ ] Precise location off by default; country from IP/store is usually enough.
- [ ] Analytics events contain pseudonymous IDs, no free-text PII; IP truncated in warehouse.
- [ ] Retention schedule per data category; deletion jobs tested.
- [ ] Privacy policy, store privacy labels and actual SDK behaviour match (diff before each release).

## Sources
- GDPR text (EUR-Lex) https://eur-lex.europa.eu/eli/reg/2016/679/oj
- EDPB guidelines (05/2020 consent; 2/2023 technical scope of art. 5(3) ePrivacy) https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en
- ICO Children's code guidance https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/
- FTC COPPA Rule and FAQs https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa
- FTC Epic Games settlements (2022-12-19) https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations
- Google: EU User Consent Policy / certified CMP requirement https://support.google.com/admob/answer/13554116
- California Privacy Protection Agency https://cppa.ca.gov/
- IAPP on 152-FZ amendments https://iapp.org/news/a/level-up-russia-enhances-the-protection-of-personal-data
- GOV.UK, DUAA 2025 plans for commencement https://www.gov.uk/guidance/data-use-and-access-act-2025-plans-for-commencement
- Google Play Help, account deletion requirements https://support.google.com/googleplay/android-developer/answer/13327111
- IAB Europe TCF (v2.3 deadline 2026-02-28) https://iabeurope.eu/transparency-consent-framework/
- EU General Court press release, T-553/23 (2025-09) https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf
- CPPA, 2025 CPI adjustment of thresholds https://cppa.ca.gov/announcements/2024/20241217.html
- Mondaq, CPPA finalizes ADMT/risk assessment/cyber audit rules https://www.mondaq.com/unitedstates/security/1666554/the-cppa-finalizes-rules-on-admt-risk-assessments-and-cybersecurity-audits
- National Law Review, COPPA amendments in effect https://natlawreview.com/article/amendments-ftc-coppa-rule-now-effect
- Hunton, FTC COPPA age-verification policy statement (2026-02) https://www.hunton.com/privacy-and-cybersecurity-law-blog/ftc-issues-coppa-policy-statement-encouraging-adoption-of-age-verification-technologies
- European Commission, DSA guidelines on protection of minors (2025-07-14) https://digital-strategy.ec.europa.eu/en/library/commission-publishes-guidelines-protection-minors
- Lidings, 23-FZ localization update https://www.lidings.com/media/legalupdates/localization_pd_update/
- Gorodissky, 156-FZ separate consent from 2025-09-01 https://www.gorodissky.com/publications/articles/russia-introduced-new-rules-on-data-processing-consent/
- Seamless Legal, 420-FZ turnover fines and criminal liability https://seamless.legal/insights/Turnover_fines_and_criminal_liability/
