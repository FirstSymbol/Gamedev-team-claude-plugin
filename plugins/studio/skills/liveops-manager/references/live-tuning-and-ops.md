# Live tuning, event operations and incidents

## Change classes and approvals
| Class | Examples | Approvers | Rollout |
|---|---|---|---|
| C0 cosmetic | copy fix, art swap inside an existing event | liveops + loc review | after staging check |
| C1 tuning in guardrails | rewards +/-20%, duration, drop rates inside approved ranges | liveops + economy-monetization-designer | staged (10% → 50% → 100%) or per segment |
| C2 economy/monetization | new price, new currency source, odds change, new offer type | economy + product-manager (+ compliance-advisor if odds/price display/minors) | A/B or staged with holdout |
| C3 emergency | kill switch, disable event/offer/endpoint, exploit mitigation | on-call liveops + any lead; post-hoc review <= 24 h | immediate |
- Four-eyes rule for C1+: author != publisher.

## Change request (`.team/specs/liveops/changes/CR-NNN.md`)
`What/why | keys changed (before → after diff) | segments + client versions affected |
expected KPI impact | risk | staging evidence (screens/test ids) | schedule (UTC) |
rollback step | approvers | monitoring + alert owner`.

## Config as code
- Config lives in a git repo (JSON/YAML per domain); PR review = approval; CI validates JSON
  Schema + business rules; pipeline publishes to the config service (UGS CLI / Admin API,
  PlayFab Admin API, custom service) - no hand edits in dashboards for C1+ (verify the
  deployment tooling your backend supports).
- Every publish = immutable version; rollback = re-point to previous version, target < 15 min,
  rehearsed quarterly. Audit log: who, what, when, CR id.
- Publish windows: Tue-Thu daytime with on-call for 2 h after; freeze 48 h before major beats
  and holidays except C3.

## Event monitoring dashboard (build before the event starts)
| Panel | Alert example (tune per game) |
|---|---|
| Participation: % of eligible DAU joined | < 50% of forecast at T+6h |
| Milestone funnel (by segment) | stall at one milestone vs forecast curve |
| Currency injection per hour vs forecast, by source | > 150% of forecast for 1 h |
| Revenue per hour vs baseline/forecast, by SKU | < 60% or > 200% (pricing bug) |
| Purchase errors / server validation failures | > 2% of attempts for 15 min |
| Crash-free sessions, ANR (by platform/version) | < 99.5% crash-free |
| Event endpoints: 5xx rate, p95 latency | 5xx > 1% or p95 > 500 ms for 10 min |
| Leaderboard anomalies: score/min, score jumps | above p99.9 plausibility cap |
| Support tickets tagged with event | > 2x baseline |
| Community sentiment (Discord/Reddit keywords) | spike of "bug", "scam", "refund" |
| Refund rate by SKU | > 2x trailing average |
- Check schedule: T-1h (prod config == staged, diff empty) · T0 (verify on real devices per
  platform/segment) · T+15m · T+1h · T+24h · daily · T-end (claims close) · end+1h (rewards
  delivered, leaderboard payouts done).

## Incident playbook (broken event, economy exploit, pricing error)
| SEV | Definition | Player-facing update |
|---|---|---|
| SEV1 | purchases broken, mass currency mint, data loss, all players blocked | <= 1 h |
| SEV2 | event broken for a segment/platform, exploit spreading | <= 4 h |
| SEV3 | cosmetic/minor, workaround exists | next scheduled comms |
1. **Detect**: alert or report → open `incident-<date>-<slug>.md`, name incident lead.
2. **Triage**: who, how many, since when, value at stake; link ledger queries.
3. **Contain first**: kill switch, pause offer, disable endpoint, freeze leaderboard, extend
   event. Don't debate while an exploit runs.
4. **Communicate**: internal channel; status in-game/community per SEV table
   (template in `player-communication.md`). Infra-caused → devops-sre-engineer leads.
5. **Fix** via CR (C3 now, proper fix C1/C2 later); regression test by qa-engineer.
6. **Remediate**: compensation (policy below) and/or clawback.
7. **Postmortem** within 5 working days: blameless, timeline, root cause, action items with
   owners; update templates/alerts.

### Exploits
- Preserve evidence: snapshot ledger + logs before cleanup.
- Identify via ledger: earn rate > p99.9, abnormal `SourceId` patterns, same device/IP clusters.
- Response by intent: mass accidental benefit (bug paid everyone) → let modest gains stand or
  normalize silently; deliberate abuse → remove ill-gotten gains, temporary restrictions;
  bans only for repeat abuse or cheat tools, per ToS. Cheat tooling → security-engineer.
- Clawback can create negative balances: decide (and publish) whether spent gains are
  recovered; avoid punishing players who unknowingly received items.

### Broken event recovery
- Extend by downtime + 24 h; scale milestone thresholds down proportionally to time lost, or
  retro-grant milestones players were on pace to reach (from progress rate before failure).

## Compensation policy (publish internally; same for all platforms)
| Impact | Example | Compensation |
|---|---|---|
| Minor | < 1 h degraded, no loss | none, or token gift (~1 day of daily rewards) |
| Moderate | event broken 1-6 h, lost progress | restore progress + 1-2 days of rewards; extend event |
| Major | outage > 6 h or lost limited rewards | restore + compensation pack sized to lost value; extension |
| Undelivered purchase | paid, not granted | deliver exact item + small apology bonus (e.g. 10%); never ask to re-buy |
- Target affected cohort from logs; broad gift only for broad outages.
- Deliver via inbox with expiry (7-14 d); ledger source `comp:<incident-id>`.
- Cap value at loss + small apology; economy signs off on anything above "Moderate".

## Post-event analysis (`.team/reports/liveops/post-event-<event-id>.md`)
```
## Summary        goal KPI, threshold, result (hit/miss), one-line verdict
## KPIs           table: metric | treatment | holdout | forecast | delta | CI
## Funnel         eligible → joined → milestone 1..N → grand prize (by segment)
## Economy        injection vs budget per currency; sinks used; inflation note
## Revenue        by SKU/segment; new payers; ARPPU; refunds
## Engagement     sessions, playtime, retention of participants vs holdout
## Incidents      links; compensation cost
## Sentiment      support tickets, community themes
## Learnings      3 bullets max
## Decisions      repeat / tune (what) / retire; template changes; owner + date
```

## Sources
- Google SRE Book - Postmortem culture: https://sre.google/sre-book/postmortem-culture/
- Google SRE Workbook - Canarying releases: https://sre.google/workbook/canarying-releases/
- PagerDuty Incident Response guide: https://response.pagerduty.com/
- Unity Game Overrides (staged rollout, priorities): https://docs.unity.com/en-us/game-overrides/get-started
- Unity Economy config caching (config hash propagation): https://docs.unity.com/en-us/Economy/config-caching.md
