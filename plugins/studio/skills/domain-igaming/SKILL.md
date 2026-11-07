---
name: domain-igaming
description: Shared iGaming knowledge - RMG vs social/sweepstakes casino, RNG/GLI certification, jurisdictions, responsible gambling, wallets/ledgers, RGS rounds.
---
# iGaming domain (shared knowledge)
Mission: one source of casino-domain truth for designers, engineers, QA, compliance and producer.
Everything legal here is informational, dated, and "needs human legal review" before any decision.

## Model first: which business are we?
| Model | Real money in | Real value out | Law that applies | Store path |
|---|---|---|---|---|
| Real-money (RMG) | yes | yes (cash) | gambling licence per market | Apple 5.3.4 / Play gambling programme, free app, no IAP |
| Social casino | yes (IAP coins) | no (no cash-out, no transfer) | consumer, loot-box/ratings, some US case law | normal IAP; PEGI 18 (from 2026-06), AU R18+ |
| Sweepstakes (dual currency) | yes (gold coins) | yes (redeemable sweeps coins) | sweepstakes/promotion law; banned in a growing list of US states | high legal risk (verify per state) |
| Skill/real-money tournaments | entry fee | prizes | skill-gaming laws per state/country | Play/Apple restricted programmes |
- Prize + chance + consideration = gambling in most legal systems; removing one element (no
  prize value, free entry route, predominance of skill) is the legal theory each model relies on.
- Classify the product before writing any spec; record it in an ADR and in `.team/brief.md`.

## Rules that always apply
- **Server decides, client displays**: outcomes, balances, jackpots and bonus state are generated
  and stored server-side (GLI-19 §2.6.5(g)); the Unity client never contains outcome logic,
  reel strips with weights, or RNG seeds. Applies to social casino too (anti-cheat, fairness).
- **Certified RNG**: cryptographically strong, unpredictable, unbiased scaling, never seeded from
  time alone (GLI-19 §3.3). One RNG service; games request draws, never roll their own.
- **Math is versioned and certified**: every RTP variant has a PAR sheet and lab certificate per
  jurisdiction; any math/RNG/evaluator change = change control and possible re-certification.
- **Money is a ledger**: double-entry, append-only, idempotent transaction IDs, integer minor
  units (`long`) or `decimal` — never `float/double` (studio:stack-dotnet).
- **Every round is reconstructable**: bet, RNG draws, outcome, wins, balance before/after, versions,
  timestamps (UTC, NTP-synced) — game recall and dispute replay depend on it.
- **Interrupted rounds resolve, never vanish**: hold the wager, let the player complete or settle
  automatically; no new round of the same game until resolved (GLI-19 §4.16).
- **Responsible gambling is a feature set**, not a page: limits, reality checks, self-exclusion,
  age/KYC, time and net-position display where required — design them in from sprint 1.
- **Geo and age gates are hard gates** (RMG/sweeps): KYC/age before play, geolocation before
  every session in US states; block, don't warn.
- **Regulated UX rules differ per market** (UK: no autoplay, no turbo, ≥ 2.5 s slot spin, no
  celebrating losses-as-wins): implement as per-jurisdiction config flags, not forks.
- **Compliance-advisor reviews** every feature touching money, odds, bonuses, minors, ads, data.
- Prefer a licensed partner (RGS/aggregator/PAM/white label) over building regulated components
  yourself unless the business plan funds licences and certification.

## Who uses what
| Role | Start with |
|---|---|
| economy-monetization-designer | rng-and-game-certification.md (math rules), casino math in its own skill |
| dotnet-backend-developer, system-analyst | wallet-and-rgs-integration.md, rng-and-game-certification.md |
| unity-developer | rules above + wallet-and-rgs-integration.md (client contract, replays) |
| qa-engineer | rng-and-game-certification.md (test evidence), wallet-and-rgs-integration.md (rollback cases) |
| compliance-advisor, producer | business-models-and-platforms.md, jurisdictions.md, responsible-gambling-and-aml.md |
| security-engineer | wallet-and-rgs-integration.md (fraud, bonus abuse), RNG strength |

## References (read on demand)
- references/business-models-and-platforms.md — choosing/validating RMG vs social vs sweepstakes,
  sweepstakes US legal pressure, Apple/Google gambling rules, geo-restriction, ratings.
- references/jurisdictions.md — target-market questions: UKGC, MGA, Curacao, Gibraltar, IoM,
  Ontario, US states, Sweden, Germany; licence types and technical rules.
- references/rng-and-game-certification.md — RNG design/testing, GLI-11/GLI-19, test labs, game
  certification workflow, change control, game rules, recall, interrupted games.
- references/responsible-gambling-and-aml.md — limits, reality checks, self-exclusion (GAMSTOP etc.),
  KYC/age verification, AML basics, UK stake/bonus rules, marketing restrictions.
- references/wallet-and-rgs-integration.md — wallet/ledger design, idempotency, reconciliation,
  RGS/aggregator APIs, bet→outcome→settle→rollback lifecycle, logs/replays, bonus abuse and fraud.
- Slot/table math, PAR sheets, social coin economy → `studio:economy-monetization-designer`
  (casino-math). Legal analysis workflow → `studio:compliance-advisor`.
- Social casino ad-network policies (Meta, Google Ads certification, geo lists) →
  `studio:marketing-manager` (ua-performance). Ratings → `studio:release-platform-manager` (age-ratings).
