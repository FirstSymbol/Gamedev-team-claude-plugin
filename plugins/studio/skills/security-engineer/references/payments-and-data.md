# Payments, wallets and data security (practitioner reference)

## PCI DSS v4.0.1: scope reduction first
- v4.0.1 (June 2024) is current; future-dated requirements became mandatory 31 Mar 2025
  (incl. 6.4.3 payment-page script inventory/authorization and 11.6.1 change/tamper detection).
- Scope = every system that stores, processes or transmits cardholder data (CHD) + anything
  connected to them. Smallest scope = card data never touches our systems.
| Integration | Card data path | Typical SAQ (merchant) | Our burden |
|---|---|---|---|
| Hosted payment page / redirect (PSP domain) | never on our servers or page | SAQ A | low; protect redirect integrity; script-attack eligibility statement |
| PSP iframe / hosted fields (Stripe Elements, Adyen Components) | in PSP iframe on our page | SAQ A (with eligibility criteria on script protection) | protect the parent page scripts (6.4.3/11.6.1 or PSP confirmation) — verify current SAQ A text |
| Direct post / JS that sends card data from our page | through our page | SAQ A-EP | much larger: web server hardening, scans, 6.4.3/11.6.1 |
| Card data via our API/servers | our servers | SAQ D / ROC | full PCI program — avoid |
| In-app store purchases (Apple/Google) | store handles payment | out of PCI scope for us | receipt validation (game-client-security.md) |
- Never store PAN unencrypted, never store CVV/full track data at all (even encrypted) after authorization.
- Tokenization: PSP returns a token/payment-method ID; we store only token + last4 + brand + expiry.
- PSP webhooks: verify HMAC signature, check timestamp, process idempotently by event ID, then
  query the PSP API for authoritative status before crediting.
- Final PCI scoping/SAQ choice is confirmed by compliance-advisor / QSA — never self-certify silently.

## Wallet / ledger integrity (real-money and premium currency)
Principles:
- Double-entry, append-only ledger: every movement = balanced entries (debit one account, credit
  another); balance = SUM(entries) (cache it, but the sum is the truth).
- Never UPDATE or DELETE ledger rows; corrections are compensating entries with reason + actor.
- Amounts in integer minor units (`long` cents) or `decimal` with fixed scale; never `float/double`.
- Every operation carries an idempotency key (client request ID or PSP event ID) with a unique index.
```sql
CREATE TABLE ledger_entry (
  id            bigserial PRIMARY KEY,
  txn_id        uuid        NOT NULL,          -- groups balanced entries
  account_id    bigint      NOT NULL,
  amount_minor  bigint      NOT NULL,          -- +credit / -debit
  currency      char(3)     NOT NULL,
  kind          text        NOT NULL,          -- bet, win, deposit, withdrawal, bonus, reversal
  idem_key      text        NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (idem_key, account_id)
);
-- invariant per txn_id: SUM(amount_minor) = 0 (checked in the txn and by nightly job)
```
```csharp
// Debit with concurrency safety (EF Core + Postgres)
await using var tx = await db.Database.BeginTransactionAsync(IsolationLevel.Serializable, ct);
var wallet = await db.Wallets.FromSql($"SELECT * FROM wallet WHERE account_id = {id} FOR UPDATE").SingleAsync(ct);
if (wallet.BalanceMinor < stake) return Result.InsufficientFunds;
db.Entries.AddRange(Entry.Debit(id, stake, txnId, idemKey), Entry.Credit(HouseAccount, stake, txnId, idemKey));
wallet.BalanceMinor -= stake;                                  // cached balance, verified by reconciliation
await db.SaveChangesAsync(ct); await tx.CommitAsync(ct);       // retry on serialization failure (40001)
```
- Concurrency: row lock (`FOR UPDATE`) or optimistic concurrency (`xmin`/rowversion) + retry;
  test with parallel requests (race = double spend).
- Reconciliation: hourly cached-balance vs SUM(entries); daily vs PSP settlement reports and store
  payouts; mismatch = SEV1 (freeze affected accounts, notify compliance-advisor).
- Separation of duties: back-office manual adjustments require two-person approval + reason + audit log.
- Outbox pattern for events (ledger write + outbox row in one transaction) → no lost/duplicate
  notifications to game servers or analytics.

## Fraud and abuse signals
| Signal | Example rule (tune with data-analyst) |
|---|---|
| Velocity | > N deposits/withdrawals or purchases per hour per account/card/device |
| Identity mismatch | billing country ≠ IP geo ≠ device locale; VPN/proxy/hosting ASN |
| Device/account graph | many accounts per device fingerprint / payment instrument / IP (multi-accounting, bonus abuse) |
| Chargeback/refund history | refund rate > threshold → block premium purchases |
| Behavioral | deposit → minimal play → withdraw (laundering pattern); bot-like timing |
| Collusion (tables/PvP) | same players repeatedly at the same tables, chip dumping, soft-play patterns |
| Account takeover | new device + password reset + withdrawal-method change within hours |
- Actions: score → step-up (MFA, KYC re-check) → hold withdrawal → manual review → block.
  Real-money AML/KYC thresholds are regulatory → compliance-advisor.
- Never reveal which rule fired to the user; log decisions for audit and appeals.

## Encryption
| Layer | Requirement |
|---|---|
| In transit (external) | TLS 1.2 minimum, 1.3 preferred; HSTS; modern ciphers only (Mozilla "intermediate" profile) |
| In transit (internal) | TLS/mTLS between services handling money/PII (service mesh or app-level) |
| At rest (platform) | managed DB/storage encryption (AES-256) with customer-managed keys for regulated data |
| At rest (field-level) | sensitive fields (IBAN, document numbers) encrypted in app with envelope encryption |
| Passwords | Argon2id / PBKDF2 (ASP.NET Identity) — never reversible encryption |
| Integrity | HMAC-SHA256 for webhooks/tokens; signatures (ECDSA/RSA-PSS) for server-signed data |
- .NET: `AesGcm` (12-byte nonce, unique per key — random nonces OK below ~2^32 messages per key),
  `RandomNumberGenerator.GetBytes`, `CryptographicOperations.FixedTimeEquals` for MAC comparison.
- ASP.NET Core Data Protection for cookies/tokens: persist key ring to shared storage
  (blob/Redis/DB) and protect it with Key Vault/KMS, or multi-instance apps break.

## Key management
- Envelope encryption: data key (DEK) encrypts data; KMS master key (KEK) encrypts DEKs; KEK never
  leaves KMS/HSM. Rotate KEK yearly (or per policy); re-wrap DEKs, don't re-encrypt all data.
- Separate keys per environment and per purpose (payments, PII, tokens); least-privilege IAM per key.
- RNG seeds/keys for certified casino RNG: HSM or KMS-backed, access audited (verify: GLI/regulator requirements).
- Signing keys (JWT, app signing, receipts): documented rotation with overlap period (publish
  old+new in JWKS).
- Key/secret inventory with owner, location, rotation date, blast radius.

## GDPR security aspects (technical; legal calls → compliance-advisor)
- Art. 32 security of processing: encryption, pseudonymization, resilience, regular testing.
- Art. 33: notify supervisory authority within 72 h of becoming aware of a personal-data breach
  (unless unlikely to result in risk); Art. 34: notify individuals if high risk.
- Art. 25 data protection by design/default: collect minimum, short retention, default private.
- Data subject rights need engineering: export (portability) and erasure across DB, logs,
  analytics, backups (document backup expiry instead of editing backups). Ledger records with
  legal retention duties are kept — legal basis decided by compliance-advisor.
- Pseudonymize analytics (player ID → salted hash/surrogate); PII stays in the identity store.
- Children's data (COPPA/age-appropriate design) and gambling age-gating → compliance-advisor.

## Checklist (payment/wallet feature)
- [ ] Card data path chosen to minimize PCI scope; SAQ type confirmed with compliance-advisor.
- [ ] Webhooks signed + idempotent + confirmed via PSP API.
- [ ] Ledger double-entry, append-only, integer minor units, idempotency keys, concurrency tested.
- [ ] Reconciliation jobs + alerts exist; manual adjustments dual-approved and audited.
- [ ] Fraud signals logged; velocity limits enforced server-side.
- [ ] Encryption in transit/at rest; keys in KMS; rotation documented; breach runbook (72 h) exists.

## Sources
- PCI SSC Document Library (PCI DSS v4.0.1, SAQ A, 6.4.3/11.6.1 guidance) https://www.pcisecuritystandards.org/document_library/
- PCI SSC blog/FAQ on SAQ A eligibility updates (2025) https://blog.pcisecuritystandards.org/
- GDPR text (Art. 25, 32–34) https://gdpr-info.eu/
- Martin Kleppmann, "Designing Data-Intensive Applications" (O'Reilly, 2017) — transactions, isolation
- Microsoft Learn: ASP.NET Core Data Protection key management https://learn.microsoft.com/aspnet/core/security/data-protection/configuration/overview
- Mozilla Server Side TLS guidelines https://wiki.mozilla.org/Security/Server_Side_TLS
- OWASP Cryptographic Storage Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
