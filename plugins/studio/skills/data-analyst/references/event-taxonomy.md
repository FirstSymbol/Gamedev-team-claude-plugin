# Event taxonomy & tracking plan

## Design process
1. Start from decisions/KPIs: list questions ("where do new players drop in FTUE?") → metrics →
   minimal events/properties needed. No "track everything".
2. Map the player journey (install → FTUE → core loop → meta → store → social) to events.
3. Write tracking-plan rows BEFORE implementation; review with devs (system-analyst for server events).
4. Implement behind one analytics facade; QA validates in debug view; monitor volumes after release.
5. Version and deprecate deliberately; the plan is the contract for the data.

## Naming conventions
- `snake_case`, `object_action`, past-tense or Firebase-style present (pick one, never mix):
  `level_completed` / `level_end`. Object first groups related events alphabetically.
- ≤ 40 chars, `[a-z0-9_]`, start with a letter (Firebase limit); no dynamic values in names
  (`level_5_complete` ✗ → `level_completed {level: 5}` ✓).
- Properties `snake_case`; booleans `is_`/`has_`; units in name (`duration_ms`, `price_usd_micros`);
  enums lowercase strings with a closed list in the plan.
- Prefer platform-recommended names where they exist (GA4/Firebase: `level_start`, `level_end`,
  `tutorial_begin`, `tutorial_complete`, `earn_virtual_currency`, `spend_virtual_currency`,
  `purchase`, `unlock_achievement`, `post_score`) to get built-in reports.

## Envelope (required on every event)
| Property | Type | Source | Notes |
|---|---|---|---|
| event_id | UUID | client | dedupe key (retries, offline replays) |
| event_name / schema_version | string / int | client | version bumps on breaking change |
| client_ts / server_ts | timestamp ms UTC | client / ingest | keep both; analyze on client_ts with sanity bounds |
| player_id / install_id | string | server-issued / client | no email/name; pseudonymous IDs only |
| session_id, session_number | string, int | client | session rule documented |
| platform, os_version, device_model | string | client | |
| app_version, build_number, content_version | string | client | needed for schema drift + regressions |
| country | string | ingest (geo-IP), not client | |
| ab_assignments | map/array | client from server | `{exp_id: variant}` for every active experiment |
| consent_analytics, consent_ads | bool | client | pipeline drops/limits per consent |
| is_test_user | bool | server flag | exclude QA/devs from KPIs |

## Core game event set (starter)
| Event | Key properties | Emitted by |
|---|---|---|
| app_open / session_start | is_first, launch_source | client |
| tutorial_step | step_id, step_index, duration_ms | client |
| level_start / level_end | level_id, mode, result (win/lose/quit), duration_ms, moves, boosters_used | client |
| currency_earned / currency_spent | currency, amount, source/sink, balance_after, item_id | server (authoritative) |
| item_acquired | item_id, item_type, source, quantity | server |
| store_opened / offer_shown | placement, offer_id, price_tier | client |
| purchase_completed | sku, price_local, currency_local, price_usd_micros, store, transaction_id, is_first_purchase | server (validated receipt) |
| ad_impression / ad_reward_granted | ad_format, network, placement, revenue_usd_micros (ILRD) | client / server (S2S reward) |
| social_invite_sent / invite_accepted | channel, invite_id | client / server |
| error_shown | error_code, screen, http_status | client |
| feature_used | feature_id, context | client (sparingly) |
Social casino adds: spin (game_id, bet, win, balance_after — aggregate server-side, don't stream
every spin from client), bonus_claimed, gift_sent/received, vip_tier_changed. Real-money iGaming:
bets/wins come from the platform ledger, never client analytics (studio:domain-igaming).

## Tracking plan row format
```
| Event | Trigger (exact) | Properties (type, enum, required) | Source | KPI/question | Ver | Owner | Status |
| level_end | result screen shown | level_id str req; result enum[win,lose,quit] req; duration_ms int req | client | level funnel, difficulty | 2 | data-analyst | live |
```

## Versioning & governance
- Additive property = minor (no version bump); rename/type change/semantics change = new
  `schema_version` (or `_v2` event) + dual-fire during transition + deprecate old after N releases.
- JSON Schema per event in repo; validate at ingest; route invalid events to quarantine table + alert.
- Volume budget: ≤ ~100–300 events per session typical; never per-frame; batch on client
  (flush every 10–30 s, on pause/background, and at N events); sample high-volume debug events.
- Change log in the tracking plan; analytics QA checklist in every feature's test plan.

## Client vs server events
- Server is source of truth for money, currency, items, purchases, rewards, and experiment
  assignment. Client events cover UI/behavior and performance.
- Join client and server streams on player_id + event_id/transaction_id; reconcile revenue
  daily vs store/PSP reports (expect < 1–2% gap after refunds/timezones; investigate more).

## Privacy & consent
- Data minimization: no direct PII in events (email, name, phone, precise location, free text);
  pseudonymous IDs; IP truncated at ingest unless needed for fraud with a legal basis.
- EU/UK (GDPR/ePrivacy): analytics SDKs that access device storage generally need consent unless
  strictly necessary — legal basis decided by compliance-advisor; implement consent gate before init.
- iOS ATT: IDFA only after authorization; SKAdNetwork/AdAttributionKit for attribution otherwise.
- Google Consent Mode v2 (EEA/UK): set `ad_storage`, `analytics_storage`, `ad_user_data`,
  `ad_personalization` via `FirebaseAnalytics.SetConsent(IDictionary<ConsentType, ConsentStatus>)`
  (`ConsentStatus.Granted/Denied`) before logging (verify: `ConsentType` member names in Firebase Unity reference).
- Children/mixed audiences (COPPA, Google Play Families): restricted SDKs/identifiers; no ads
  personalization; check SDK certification lists.
- Deletion requests: support player-level deletion across SDKs and warehouse (UGS
  `RequestDataDeletion`, Firebase/GA user deletion API, own pipeline by player_id).
- Retention: define TTL per table (e.g. raw events 13–25 months, aggregates longer); the legal
  retention period is set with compliance-advisor and written in the privacy notice.

## SDK options for Unity
| Option | Strengths | Limits / notes |
|---|---|---|
| Unity Analytics (UGS) | native Unity, dashboards, funnels, SQL Data Explorer, Remote Config/A-B tie-in | SDK 6.x consent via `EndUserConsent.SetConsentState` (AnalyticsIntent); `StartDataCollection` deprecated in Unity 6.2+; custom events via `RecordEvent` with `CustomEvent`/`Event` subclasses (changelog 6.1–6.3, current 6.3.0) |
| Firebase Analytics (GA4) | free, BigQuery export, Crashlytics/Remote Config/A-B Testing | 500 distinct event names, 25 params/event, 40-char names, 100-char string values (standard), 25 user properties |
| GameAnalytics | free, game-specific types: business, resource (sources/sinks), progression (3-tier), design (hierarchical IDs), error, ad | opinionated schema; raw player-level Data Export (to AWS/GCS bucket) only in paid PipelineIQ plan (from $499/mo, 2026) |
| AppsFlyer / Adjust / Singular (MMP) | attribution, SKAN/AAK, ROAS, ad revenue (ILRD) aggregation, fraud protection | not a product analytics tool; send only key in-app events (purchase, tutorial_complete, level milestones) |
| Amplitude / Mixpanel | strong behavioral analysis UI, cohorts, experimentation add-ons | event-volume pricing; Mixpanel `mixpanel-unity` active (3.6.x, 2026; no Simplified ID Merge); Amplitude `unity-plugin` (verify: release cadence on GitHub) |
| Custom pipeline | full control, joins with server data, no sampling, cost-efficient at scale | you own ingestion, schema, privacy, uptime |
Typical stack: MMP (attribution) + one product analytics SDK or custom pipeline + server events → warehouse.

## Unity facade (one call site, many sinks)
```csharp
public interface IAnalyticsSink { void Track(string name, IReadOnlyDictionary<string, object> props); void Flush(); }
public sealed class Analytics {
    readonly IAnalyticsSink[] _sinks; readonly IConsentState _consent; readonly AnalyticsEnvelope _env;
    public Analytics(IAnalyticsSink[] sinks, IConsentState consent, AnalyticsEnvelope env)
        { _sinks = sinks; _consent = consent; _env = env; }
    public void Track(string name, Dictionary<string, object> props) {
        if (!_consent.AnalyticsGranted) return;            // gate before any SDK call
        props["event_id"] = Guid.NewGuid().ToString("N");
        _env.Fill(props);                                    // session, versions, ab_assignments
        foreach (var s in _sinks) s.Track(name, props);
    }
}
```
- Event names as `const string` in one static class generated from the tracking plan.
- Flush on `OnApplicationPause(true)`; persist unsent batch to disk for offline sessions.

## Custom pipeline (.NET + ClickHouse/BigQuery)
- Client batches JSON → `POST /v1/events:batch` (gzip, ≤ 500 events or 1 MB) → validate schema →
  Kafka/Redpanda/Pub/Sub → sink to ClickHouse (Kafka engine or ClickPipes) or BigQuery (Storage
  Write API / Dataflow).
```sql
CREATE TABLE events (
  event_date Date, event_ts DateTime64(3, 'UTC'), event_name LowCardinality(String),
  event_id UUID, player_id String, session_id String, platform LowCardinality(String),
  app_version LowCardinality(String), country LowCardinality(String),
  props String  -- JSON; promote hot props to typed columns
) ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_name, event_date, player_id, event_id)
TTL event_date + INTERVAL 25 MONTH;
```
- ReplacingMergeTree dedupes only at merge time → use `FINAL` or `uniqExact(event_id)` in exact
  queries. BigQuery: partition by `DATE(event_ts)`, cluster by `event_name, player_id`.

## Sources
- Firebase Analytics API reference (limits) https://firebase.google.com/docs/reference/swift/firebaseanalytics/api/reference/Classes/Analytics
- Unity Analytics SDK 6.1 migration guide (consent) https://docs.unity.com/ugs/en-us/manual/analytics/manual/sdk61-migration-guide
- Unity Analytics package changelog 6.3 https://docs.unity3d.com/Packages/com.unity.services.analytics@6.3/changelog/CHANGELOG.html
- Firebase Unity reference: FirebaseAnalytics.SetConsent https://firebase.google.com/docs/reference/unity/class/firebase/analytics/firebase-analytics
- GameAnalytics pricing (Data Export in PipelineIQ) https://www.gameanalytics.com/pricing
- Mixpanel Unity SDK https://github.com/mixpanel/mixpanel-unity
- GameAnalytics Unity SDK event tracking https://docs.gameanalytics.com/integrations/sdk/unity/event-tracking
- GA4 recommended events for games https://support.google.com/analytics/answer/9267735
- ClickHouse ReplacingMergeTree docs https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree
