# Release strategies, migrations, rollback and DR (practitioner reference)

## Choosing a rollout strategy
| Strategy | How | Rollback | Cost | Use when |
|---|---|---|---|---|
| Rolling | replace pods gradually (`maxUnavailable: 0`) | redeploy previous digest (minutes) | none extra | default for stateless APIs with backward-compatible changes |
| Blue/green | full parallel env, switch LB/DNS | switch back (seconds) | 2x capacity during release | big-bang changes, strict maintenance windows, casino backends needing instant revert |
| Canary | 1% → 5% → 25% → 100% with metric gates | shift weight to 0 | small | high-traffic services; automate with Argo Rollouts / Flagger / service mesh weights |
| Feature flag | code deployed dark, enabled per cohort | flip flag (seconds) | flag debt | risky features, live-ops events, A/B tests, client features |
| Staged store rollout | Play staged % / App Store phased release | halt rollout; no binary rollback | none | every mobile client release |
- Canary gate example: compare canary vs baseline over 15 min — 5xx ratio ≤ baseline + 0.1 pp,
  p99 latency ≤ baseline × 1.2, no new error fingerprints; otherwise auto-abort.
- Game servers: never replace a running match; new fleet version takes new sessions, old fleet
  drains naturally (Agones: new Fleet + allocate by label; GameLift: new fleet + alias switch).
- Apple phased release: 7 days at 1%, 2%, 5%, 10%, 20%, 50%, 100% of auto-update users; can pause
  up to 30 days total (unlimited pauses). Google Play: staged rollout by % with halt/resume.

## Mobile/client constraints
- Old clients live for months: server must accept N-1 and N-2 client protocol versions.
- `min_supported_version` from remote config → force-update screen; bump only after the new
  version reaches most users.
- Kill switches (server flags) for every new client feature that touches economy, payments or netcode.
- Addressables/content releases: versioned catalogs, roll forward by publishing previous content as
  a new version; never overwrite a published bundle path in place (CDN caches).

## Feature flags
| Tool | Notes |
|---|---|
| Microsoft.FeatureManagement | .NET native, config/Azure App Configuration backed, targeting filters |
| OpenFeature SDK (.NET) + provider | vendor-neutral API; swap flagd/LaunchDarkly/Unleash/Flagsmith providers |
| Unity Remote Config / Game Overrides | client flags with audience targeting (UGS) |
- Flag types: release (short-lived, delete within 2 sprints), ops kill switch (permanent, documented),
  experiment (owned by data-analyst), permission (entitlements).
- Default value = safe behavior when flag service is unreachable. Evaluate server-side for anything
  money-related; client flags are hints, not security.
- Track flags in a registry with owner + expiry; flag debt is real debt.

## Database migration safety: expand / contract (parallel change)
| Phase | Schema | App | Reversible? |
|---|---|---|---|
| 1 Expand | add new column/table (nullable or default), new index `CONCURRENTLY` | old app unaffected | yes (drop new) |
| 2 Migrate | backfill in batches (e.g. 1–10k rows/txn, throttled) | new app writes both, reads old | yes |
| 3 Switch | — | new app reads new, still writes both | yes (flag back) |
| 4 Contract | drop old column/constraint after ≥ 1 release + backup | old code gone | NO — separate, delayed release |
- Rule: each deploy must work with schema N and N+1 (rollback of the app must not need a schema rollback).
- Renames = add + copy + switch + drop, never `RENAME COLUMN` in one deploy.
- Postgres: `CREATE INDEX CONCURRENTLY` (no table lock; cannot run in a transaction); adding
  `NOT NULL` on big tables: add `CHECK (...) NOT VALID`, then `VALIDATE CONSTRAINT`.
- Set `lock_timeout` (e.g. 5 s) for DDL so a migration fails instead of blocking all traffic.
- SQL Server: online index ops need Enterprise/Azure SQL; check edition before planning.
- EF Core: generate SQL and review it — `dotnet ef migrations script --idempotent -o migrate.sql`,
  or `dotnet ef migrations bundle` as a pipeline artifact. Do not call `Database.Migrate()` at app
  startup in multi-replica prod (Microsoft guidance: race conditions, elevated permissions).
- Migrations run as a separate pipeline job with its own DB credentials (DDL rights) before the
  app deploy; app runtime credentials have DML only.
- Ledger/wallet tables: no destructive migrations; append-only; dual-run reconciliation before switch.

## Rollback playbook
1. Decide fast: if SLO burn alert fires within the bake window → roll back first, debug later.
2. App: redeploy previous digest (`helm rollback api <rev>` / previous task definition / swap slots).
3. Flags: turn off the feature flag if the change was flagged (fastest).
4. Data: forward-fix preferred; restore only for corruption, scoped (PITR to a side DB, copy rows back).
5. Client: halt staged rollout, server-side kill switch, hotfix build with increased build number.
6. Record in incident timeline; postmortem if user-visible.
- Practice: rollback exercised on stage every release train; measure time-to-rollback (DORA recovery time).

## Backups and disaster recovery
- RPO = max acceptable data loss (time); RTO = max acceptable downtime. Set per data class with
  product-manager; real-money wallets typically RPO ≈ 0 (synchronous replication) and RTO minutes.
| Tier | Example | RPO | RTO | Mechanism |
|---|---|---|---|---|
| 0 | wallet/ledger, purchases | ~0 | < 15 min | sync replica / zone-redundant DB + PITR |
| 1 | player profiles, inventory | ≤ 5 min | < 1 h | async replica + PITR (managed DB) |
| 2 | leaderboards, analytics | ≤ 24 h | < 1 day | daily snapshot, rebuildable |
| 3 | caches, matchmaking state | n/a | minutes | rebuild from source of truth |
- 3-2-1: 3 copies, 2 media/services, 1 off-site/off-account; plus immutable/WORM backup copy
  (ransomware) in a separate account/subscription with separate credentials.
- Managed DBs: enable PITR (Azure SQL/PostgreSQL Flexible Server, RDS) — know the retention (often
  7–35 days) and that PITR restores to a NEW server.
- Restore drill quarterly: restore to isolated env, run integrity checks (row counts, ledger balance
  = sum of entries), measure actual RTO. Untested backups are assumed broken.
- DR patterns: backup/restore (cheap, hours) → pilot light → warm standby → multi-region active/active
  (expensive, complex consistency). Choose the cheapest one that meets RTO/RPO.
- Secrets/keys are part of DR: KMS keys, signing keys, keystores (Android upload key!) backed up
  with access controls; losing the iOS/Android signing material blocks releases.
- Game servers & matchmaking are tier 3: rebuild from IaC; DR plan = redeploy fleet in another region.

## Release checklist (backend)
- [ ] Change is backward compatible with current clients and current schema.
- [ ] Migration reviewed (SQL), timed on prod-size data, `lock_timeout` set.
- [ ] Flag/kill switch for risky paths; default safe.
- [ ] Dashboards + canary gates ready; on-call aware; not before a weekend/live event unless urgent.
- [ ] Rollback command written in the PR/release notes and tested on stage.

## Sources
- Martin Fowler, "ParallelChange" (expand/contract) https://martinfowler.com/bliki/ParallelChange.html
- Martin Fowler, "BlueGreenDeployment" https://martinfowler.com/bliki/BlueGreenDeployment.html
- Microsoft Learn: Applying EF Core migrations https://learn.microsoft.com/ef/core/managing-schemas/migrations/applying
- Google SRE Workbook, ch. 16 "Canarying Releases" https://sre.google/workbook/canarying-releases/
- Apple: Release a version update in phases https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases
- Google Play: Release app updates with staged rollouts https://support.google.com/googleplay/android-developer/answer/6346149
- AWS Whitepaper: Disaster recovery options in the cloud https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html
- PostgreSQL docs: CREATE INDEX CONCURRENTLY https://www.postgresql.org/docs/current/sql-createindex.html
