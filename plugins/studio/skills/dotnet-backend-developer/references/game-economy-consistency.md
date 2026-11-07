# Consistency for game economies: wallets, purchases, rewards, bets

## Non-negotiables
- Server authoritative: client sends intent (`claim daily bonus`, `bet 100 on round X`), server computes
  outcome, price, reward. Client-sent amounts are checked against server-side catalog/rules.
- Integers only: `long` minor units per currency (coins, gems, cents). No `double`; `decimal` only for fiat conversions.
- Append-only ledger is the source of truth; `wallets.balance` is a projection updated in the SAME transaction.
- Every mutation has an idempotency identity (client key or natural key) protected by a DB unique constraint.
- Corrections are compensating entries (reversal + new entry), never UPDATE/DELETE of ledger rows.
- Reconcile automatically: ledger sum = balance for every wallet; alert on any drift.

## Schema (PostgreSQL)
```sql
CREATE TABLE wallets (
  id uuid PRIMARY KEY, player_id uuid NOT NULL, currency text NOT NULL,
  balance bigint NOT NULL CHECK (balance >= 0),           -- DB-level last line of defense
  UNIQUE (player_id, currency));
CREATE TABLE wallet_transactions (
  id uuid PRIMARY KEY, wallet_id uuid NOT NULL REFERENCES wallets(id),
  kind text NOT NULL,                  -- purchase_grant, bet, win, refund, bonus, admin_adjust, reversal
  amount bigint NOT NULL CHECK (amount <> 0),   -- signed: debit < 0, credit > 0
  balance_after bigint NOT NULL,
  idempotency_scope text NOT NULL, idempotency_key text NOT NULL,
  request_hash text NOT NULL, reference text NULL,         -- round id, store transaction id, admin ticket
  created_at timestamptz NOT NULL DEFAULT now(), created_by text NOT NULL,
  UNIQUE (idempotency_scope, idempotency_key));
CREATE UNIQUE INDEX ux_store_tx ON wallet_transactions (reference) WHERE kind = 'purchase_grant';
```
- Double-entry variant (recommended once there are system accounts: house, bonus pool, IAP revenue,
  jackpot): each transaction = ≥ 2 entries summing to zero per currency. Enables "where did coins come from" audits.
- `balance_after` per entry gives cheap audit trails and drift detection.

## Debit/credit algorithm (one transaction)
```csharp
public async Task<Result<TxDto>> Apply(WalletCommand cmd, CancellationToken ct) {
    var strategy = db.Database.CreateExecutionStrategy();
    return await strategy.ExecuteAsync(async () => {
        await using var tx = await db.Database.BeginTransactionAsync(ct);
        // 1. Replay check (fast path); unique constraint is the real guard
        var prior = await db.WalletTransactions.AsNoTracking()
            .FirstOrDefaultAsync(t => t.IdempotencyScope == cmd.Scope && t.IdempotencyKey == cmd.Key, ct);
        if (prior is not null)
            return prior.RequestHash == cmd.Hash ? Result.Ok(prior.ToDto(replayed: true))
                                                 : Errors.IdempotencyKeyReused;
        // 2. Atomic conditional balance change: no read-modify-write race
        var rows = await db.Database.SqlQuery<long>($"""
            UPDATE wallets SET balance = balance + {cmd.Amount}
            WHERE id = {cmd.WalletId} AND player_id = {cmd.PlayerId} AND balance + {cmd.Amount} >= 0
            RETURNING balance AS "Value"
            """).ToListAsync(ct);   // no further LINQ on it: EF would wrap UPDATE in a subquery
        if (rows.Count == 0) return Errors.InsufficientFundsOrNotFound;
        // 3. Ledger row + outbox event in the same transaction
        var entry = WalletTransaction.Create(cmd, balanceAfter: rows[0], clock.GetUtcNow());
        db.WalletTransactions.Add(entry);
        db.Outbox.Add(OutboxMessage.From(new WalletChanged(entry.Id, cmd.WalletId, cmd.Amount, rows[0])));
        try { await db.SaveChangesAsync(ct); }
        catch (DbUpdateException e) when (e.IsUniqueViolation()) {   // concurrent duplicate won
            await tx.RollbackAsync(ct); return Errors.RequestInProgressOrDuplicate;  // client retries → replay path
        }
        await tx.CommitAsync(ct);
        return Result.Ok(entry.ToDto(replayed: false));
    });
}
```
- `IsUniqueViolation()` = `PostgresException { SqlState: "23505" }` (Npgsql `PostgresErrorCodes.UniqueViolation`).
- Alternatives: `SELECT ... FOR UPDATE` on the wallet row then domain method (clearer for multi-step rules;
  lock order by wallet id when touching 2 wallets, e.g. transfers/gifts); optimistic `xmin` token + retry (fine at low contention).
- Hot wallets (house/jackpot) contend on one row: shard into N sub-accounts or aggregate asynchronously.
- Never call external services (store validation, payment, provider) while holding the transaction/lock.

## Double-spend and duplication vectors
| Vector | Defense |
|---|---|
| Double tap / parallel requests | same `Idempotency-Key` per intent + unique constraint |
| Client retry after timeout (first request succeeded) | replay returns stored result, not a second debit |
| Two devices spending same balance concurrently | conditional `UPDATE ... balance + amt >= 0` or row lock; `CHECK (balance >= 0)` |
| Replayed IAP receipt / purchase token | unique `(store, purchaseToken/transactionId)`; validate with store server-side; check `obfuscatedAccountId` matches the player |
| Webhook delivered twice / out of order | dedupe by provider event ID; state machine transitions |
| Negative or huge amounts in request | server computes amounts from catalog; validate sign/range; `checked` arithmetic |
| Refund/chargeback after spending | store notifications → reversal entry; policy for negative balance (debt) defined with economy-monetization-designer |
| Reward claimed twice across days/timezones | unique `(player_id, reward_type, period_key)`; period from server time + defined reset timezone |
| Admin double-submit / insider abuse | idempotency key on admin commands, 4-eyes for large adjustments, audit trail |
| Race between bet settlement and cancel | round state machine `UPDATE rounds SET state='settled' WHERE id=@id AND state='open'` |

## IAP purchase flow (consumables)
1. Client completes store purchase → sends receipt/purchase token + `Idempotency-Key` to backend.
2. Backend validates with the store server API (Apple App Store Server API `Get Transaction Info` / JWS
   signed transactions; Google Play Developer API `purchases.products.get`) — never trust client-side validation.
3. Check product ID ↔ catalog, bundle/package name, environment (sandbox vs production), purchase state.
4. One transaction: insert grant with unique store ID (Google: `purchaseToken`, globally unique — never
   `orderId`, promo-code purchases have none; Apple: `transactionId`) → credit wallet → outbox `PurchaseGranted`.
5. After commit: Google `purchases.products.consume`/`acknowledge` from the backend (unacknowledged purchases
   auto-refund after 3 days); Apple: client finishes the transaction after server ack. Failed fraud/eligibility
   checks: don't grant, explicitly refund+revoke (`orders.refund` with `revoke=true`).
6. Subscribe to App Store Server Notifications V2 and Google RTDN + Voided Purchases API for refunds/chargebacks
   → reversal entries; if already spent, Google suggests negative balance + purchase restrictions (policy owned by economy-monetization-designer).
7. Pending/deferred purchases (parental approval, PENDING state): grant only on PURCHASED/final state.
- Reconcile daily: store reports vs `purchase_grant` entries.

## Bets and rounds (casino/slots)
```
round: Created → BetPlaced (debit, ref=roundId) → OutcomeDrawn (server RNG, stored) → Settled (credit win, ref=roundId)
                         ↘ Cancelled (refund, ref=roundId)  on failure/timeout before outcome
```
- Idempotency identity = `(round_id, operation)`: one bet debit, one settlement credit, one refund per round.
- Outcome is produced and persisted server-side before the client sees it; RNG certification and RTP
  math → `studio:domain-igaming` and economy-monetization-designer.
- Seamless-wallet integrations with external game providers: they call `debit`/`credit`/`rollback` with
  their transaction IDs — store them unique; `rollback` of unknown tx must be recorded (tombstone) so a late debit is rejected.
- Stale open rounds: sweeper job refunds or settles per rules after timeout; never leave money in limbo.
- Real-money contexts: responsible-gambling limits checked inside the same transaction as the debit (verify per jurisdiction with compliance-advisor).

## Rewards, bonuses, liveops grants
- Daily bonus: `period_key = date in reset timezone` (e.g. UTC 00:00) computed on server with `TimeProvider`;
  `nextClaimAt` returned to client for the timer.
- Batch grants (event rewards to 1M players): idempotent per `(campaign_id, player_id)`, processed in chunks
  via queue/outbox; re-running the job is safe.
- Expiring currencies/bonus wagering requirements: separate wallet/sub-balance with its own ledger kind.

## Verification and testing
- Invariant tests: for random sequences of ops, `sum(ledger) == balance`, balance never < 0 (property-based: FsCheck/CsCheck).
- Concurrency integration test (Testcontainers Postgres): 50 parallel debits on balance for 10 → exactly 10 succeed.
- Duplicate test: same idempotency key ×20 in parallel → one ledger row, all responses identical.
- Reconciliation job + alert: nightly (and on demand) `balance` vs ledger sum vs external (store, provider) reports.
- Mutation testing (Stryker.NET) on the wallet module; target ≥ 80% score.

## Sources
- Modern Treasury, Accounting for Developers https://www.moderntreasury.com/journal/accounting-for-developers-part-i
- Stripe idempotent requests https://docs.stripe.com/api/idempotent_requests
- PostgreSQL explicit locking https://www.postgresql.org/docs/current/explicit-locking.html
- Apple App Store Server API https://developer.apple.com/documentation/appstoreserverapi
- Google Play: Fight fraud and abuse / verify purchases https://developer.android.com/google/play/billing/security
- Google Play: Integrate the library (acknowledge within 3 days) https://developer.android.com/google/play/billing/integrate
- Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), ch. 7 Transactions
