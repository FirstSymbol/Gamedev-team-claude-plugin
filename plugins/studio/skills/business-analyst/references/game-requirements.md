# BA in gamedev: GDD boundary, live-ops, back-office, payments

## GDD vs requirements — who writes what
| Content | Owner | BA contribution |
|---|---|---|
| Core loop, mechanics, feel, balance numbers | game-designer / economy-monetization-designer | none — reference GDD section |
| Player-facing rules that touch money, data, accounts | GD defines intent | BA formalizes as BR-n + Gherkin edge cases |
| Back-office, CS, finance, compliance, reporting | BA | full ownership of requirements |
| Live-ops tooling (events, offers, config) | liveops-manager states needs | BA turns needs into stories + NFRs |
| Platform/store/cert constraints | release-platform-manager | BA records as constraints C-n |
| Tracking/KPIs | data-analyst / product-manager | BA links AC to events |
- Rule: GDD is a living design doc (vision, fun); requirements are contractual and testable.
  Never rewrite a GDD into stories wholesale — extract only what engineering must build and
  what can fail (server rules, persistence, purchases, rewards).
- Feature spec for engineering = GDD section link + BRs + stories + AC + NFRs + open questions.
- Expect iteration: prototype-first features get requirements AFTER the fun is validated;
  write lightweight stories for prototypes, full AC for production/live features.

## Game NFRs that BAs forget
- Device tiers (min/rec spec, RAM), target FPS (30/60), cold start time, download size
  (store cellular/OTA limits: verify current Apple/Google thresholds), offline behavior.
- Server authority: which values are client-trusted (none for currency, rewards, RNG outcomes).
- Time: server time source, reset times (UTC vs local), daylight saving, clock-tamper defense.
- Localization: text expansion (+30% for DE/RU), RTL, fonts for CJK, store listing locales.
- Age rating / audience (COPPA, GDPR-K, age gates), platform cert rules (studio:domain-pc-console).
- Live updates: what can change via remote config vs requires a client release vs store review.

## Live-ops requirements checklist
- Event lifecycle: draft → scheduled → live → ended → archived; start/end in UTC; preview
  on staging; per-segment targeting; overlap rules; kill switch.
- Content delivery without client release: remote config, Addressables/CDN bundles, server
  catalogs; version compatibility (min client version per content).
- Offers/store: SKU catalog, price tiers per platform/region, personalization rules,
  frequency caps, cooldowns, limited stock, A/B variants, start/end, eligibility by segment.
- Rewards: idempotent grant, expiry, inbox/claim, compensation grants (mass gift after outage).
- Segmentation: by spend tier, level, cohort, country, platform, last active, A/B bucket.
- Ops safety: approval workflow for prod changes (4-eyes for economy), audit log, rollback,
  dry-run "who would receive this" counts.
- Analytics hooks: each event/offer has an ID logged in impressions, purchases, claims.
- Domain detail → skill `studio:domain-f2p-liveops`.

## Admin panel / back-office requirements
| Capability | Must-have requirement details |
|---|---|
| Player lookup | by ID, email, device ID, store txn ID, nickname; PII masked by role |
| Player profile | balances, inventory, purchases, sessions, bans, consents, RG limits |
| Grants/corrections | currency/item grant with reason code, ticket ID, limit per role, audit |
| Refund/chargeback handling | link to purchase, auto-debit or flag negative balance policy |
| Bans/sanctions | type (chat, play, payments), duration, reason, appeal path |
| Config/content | edit with validation, diff view, schedule, approval, rollback |
| Reports/exports | CSV with filters; heavy queries async; export logged |
| RBAC | roles: viewer, CS L1, CS L2, live-ops, finance, admin; least privilege |
| Audit trail | who, what, when, before/after, reason; immutable; retention period stated |
- NFRs: SSO/2FA for staff, IP allowlist/VPN, session timeout, every write audited,
  bulk actions capped + confirmed, rate limits, separate prod/staging access.
- Typical CS macros/flows (missing purchase, lost account, ban appeal) → write a use case each.

## CRM / player messaging requirements
- Channels: push, in-game inbox, pop-ups, email; consent per channel and region (opt-in where required).
- Campaign: segment, trigger (event/time/inactivity), content per locale, A/B, frequency cap
  (e.g. ≤ 1 push/day, quiet hours local time), expiry, deep link target, attribution of uplift.
- Lifecycle journeys: FTUE nudges, D1/D3/D7 reactivation, lapsed payer win-back, VIP host flows.
- iGaming: responsible-gambling exclusions (self-excluded/limit-reached players must be
  suppressed from marketing) → route to compliance-advisor.

## Payment flows — requirement checklist
### Mobile IAP (App Store / Google Play)
- Product types: consumable, non-consumable, auto-renewable subscription; SKU naming/versioning.
- Server-side receipt/purchase validation before grant; grant idempotent on store txn ID.
- Google Play: acknowledge/consume purchases; unacknowledged purchases are refunded after
  3 days (Play Billing docs). Handle PENDING state (cash/slow payment methods).
- Apple StoreKit 2: verify signed transactions (JWS); `finish()` only after grant persisted.
- Refunds/revocations: App Store Server Notifications V2 (REFUND), Google RTDN + Voided
  Purchases API (30-day lookback) → debit currency or flag; policy for negative balances.
- Restore purchases (non-consumables/subscriptions), family sharing, cross-device sync.
- Loot boxes/random paid items: disclose odds before purchase (App Store Review Guideline
  3.1.1; Google Play policy) — also regional rules (verify per market with compliance-advisor).
- Web shop / external payments: allowed scope varies by platform and region and changes often
  (verify current Apple/Google policy and court rulings); requires account linking + same ledger.
### Real-money / social casino specifics
- Social casino: virtual currency never redeemable for cash; gifting rules; sweepstakes dual
  currency models carry legal risk per US state → compliance-advisor.
- Real-money: deposit → KYC/AML checks → wallet → bet/win → withdrawal with approval
  thresholds, RG limits (deposit/loss/session), self-exclusion, reality checks; domain detail →
  skill `studio:domain-igaming`.
### Failure scenarios to always specify (Gherkin)
- Payment succeeds at store but app crashes before grant → grant on next login (pending queue).
- Duplicate callbacks/receipts → single grant. Network timeout → client retries same key.
- Price changed between display and purchase → charge store price, show updated price.
- Refund after currency spent → negative balance / restriction policy (BR-n).
- Fraud signals (jailbreak, receipt reuse, velocity) → hold grant, flag for review.

## Requirements by project type
| Project | BA focus |
|---|---|
| Mobile F2P | live-ops tooling, store/offers, CRM, payment edge cases, privacy/ATT consent |
| Social casino | virtual economy rules, gifting, VIP program, CS tooling, platform policy |
| Real-money iGaming | KYC/AML, RG, jurisdiction rules, game certification, audit, reporting to regulator |
| Multiplayer | matchmaking rules, party/lobby flows, reconnect, reports/moderation, anti-cheat ops |
| PC/console | platform entitlements, cert requirements, cross-progression, DLC catalog |

## Sources
- Google Play Billing — process purchases / acknowledge https://developer.android.com/google/play/billing/integrate
- Apple App Store Server Notifications https://developer.apple.com/documentation/appstoreservernotifications
- Apple App Store Review Guidelines (3.1.1 loot box odds) https://developer.apple.com/app-store/review/guidelines/
- Google Play Voided Purchases API https://developers.google.com/android-publisher/voided-purchases
- Unity Remote Config docs https://docs.unity.com/ugs/en-us/manual/remote-config/manual/WhatsRemoteConfig
