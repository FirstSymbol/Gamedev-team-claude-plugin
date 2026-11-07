# SQL patterns & tooling

## Modeling for queries
- Build a `player_day` aggregate (player_id, date, sessions, playtime_s, revenue_usd, is_payer,
  install_date, platform, country, ab variants) daily; most KPIs become cheap scans.
- `installs` (player_id, install_date, source, platform, country) = cohort table; one row per player.
- Revenue in a separate validated `purchases` table from server receipts (net + gross columns).
- Always filter `is_test_user = false` and restrict date partitions explicitly.

## Classic retention D1/D7/D30 (PostgreSQL)
```sql
WITH cohort AS (
  SELECT player_id, install_date FROM installs
  WHERE install_date BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'
), activity AS (
  SELECT DISTINCT player_id, activity_date FROM player_day
  WHERE activity_date BETWEEN DATE '2026-09-01' AND DATE '2026-10-31'
)
SELECT c.install_date,
       COUNT(*)                                                         AS cohort_size,
       AVG((EXISTS (SELECT 1 FROM activity a WHERE a.player_id = c.player_id
                    AND a.activity_date = c.install_date + 1))::int)    AS d1,
       AVG((EXISTS (SELECT 1 FROM activity a WHERE a.player_id = c.player_id
                    AND a.activity_date = c.install_date + 7))::int)    AS d7,
       AVG((EXISTS (SELECT 1 FROM activity a WHERE a.player_id = c.player_id
                    AND a.activity_date = c.install_date + 30))::int)   AS d30
FROM cohort c
GROUP BY c.install_date ORDER BY c.install_date;
```
- Exclude immature cohorts (install_date + N > max data date) — otherwise Dn is biased down.
- Rolling retention: replace `= install_date + N` with `>= install_date + N`.

## Retention matrix (long form, any SQL)
```sql
SELECT c.install_date,
       a.activity_date - c.install_date AS day_n,
       COUNT(DISTINCT a.player_id)::numeric
         / MAX(cs.cohort_size)          AS retention
FROM installs c
JOIN player_day a ON a.player_id = c.player_id AND a.activity_date >= c.install_date
JOIN (SELECT install_date, COUNT(*) AS cohort_size FROM installs GROUP BY 1) cs
  ON cs.install_date = c.install_date
WHERE a.activity_date - c.install_date <= 30
GROUP BY 1, 2;
```

## ClickHouse specifics
```sql
-- retention(): array of flags; element k = 1 if cond1 and cond_k both true for the player
SELECT install_date,
       count() AS cohort,
       avg(r[2]) AS d1, avg(r[3]) AS d7, avg(r[4]) AS d30
FROM (
  SELECT player_id, install_date,
         retention(event_date = install_date,
                   event_date = install_date + 1,
                   event_date = install_date + 7,
                   event_date = install_date + 30) AS r
  FROM events_with_install            -- events joined to install_date
  WHERE event_date BETWEEN '2026-09-01' AND '2026-10-31'
  GROUP BY player_id, install_date
) GROUP BY install_date ORDER BY install_date;

-- windowFunnel(window_seconds)(ts, step1, step2, ...): deepest step reached in order within window
SELECT level, count() AS players
FROM (
  SELECT player_id,
         windowFunnel(86400)(toDateTime(event_ts),   -- window in timestamp units (DateTime → s)
           event_name = 'store_opened', event_name = 'offer_shown',
           event_name = 'purchase_started', event_name = 'purchase_completed') AS level
  FROM events WHERE event_date >= today() - 7 GROUP BY player_id
) GROUP BY level ORDER BY level;
```
- `uniqExact` for exact distinct counts, `uniq`/`uniqCombined` approximate and faster.
- Daily aggregates via materialized view into `AggregatingMergeTree` (`uniqState`, `sumState`).
- Dedup with ReplacingMergeTree requires `FINAL` (or `uniqExact(event_id)`) for exact numbers.

## BigQuery (incl. GA4/Firebase export)
```sql
-- GA4 export: one table per day analytics_<property_id>.events_YYYYMMDD
SELECT event_date,
       COUNT(DISTINCT user_pseudo_id) AS dau,
       COUNTIF(event_name = 'level_end'
               AND (SELECT value.string_value FROM UNNEST(event_params)
                    WHERE key = 'result') = 'win') AS level_wins
FROM `proj.analytics_123456.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20261001' AND '20261031'
GROUP BY event_date ORDER BY event_date;
```
- Cost = bytes scanned: select only needed columns, filter `_TABLE_SUFFIX`/partition, cluster
  by `event_name, user_id`; preview with dry run. `APPROX_COUNT_DISTINCT` for fast DAU.
- `DATE_DIFF(activity_date, install_date, DAY)` for day_n; `COUNTIF`, `SAFE_DIVIDE`.

## Window function patterns
```sql
-- Sessionization: new session after 30 min gap
SELECT *, SUM(is_new) OVER (PARTITION BY player_id ORDER BY event_ts) AS session_seq
FROM (
  SELECT player_id, event_ts,
         CASE WHEN event_ts - LAG(event_ts) OVER (PARTITION BY player_id ORDER BY event_ts)
                   > INTERVAL '30 minutes'
                OR LAG(event_ts) OVER (PARTITION BY player_id ORDER BY event_ts) IS NULL
              THEN 1 ELSE 0 END AS is_new
  FROM events) t;

-- First purchase per player and day-to-convert
SELECT player_id, purchased_at, purchased_at::date - install_date AS days_to_first_purchase
FROM (SELECT p.*, i.install_date,
             ROW_NUMBER() OVER (PARTITION BY p.player_id ORDER BY purchased_at) AS rn
      FROM purchases p JOIN installs i USING (player_id)) x
WHERE rn = 1;

-- Cumulative ARPU (LTV curve) per cohort
SELECT install_date, day_n,
       SUM(rev) OVER (PARTITION BY install_date ORDER BY day_n) / MAX(cohort_size)
         OVER (PARTITION BY install_date) AS ltv
FROM cohort_revenue_by_day;

-- Payer concentration: revenue share of top 1% payers
SELECT SUM(rev) FILTER (WHERE pct = 1) / SUM(rev) AS top1_share
FROM (SELECT player_id, SUM(net_usd) AS rev,
             NTILE(100) OVER (ORDER BY SUM(net_usd) DESC) AS pct
      FROM purchases GROUP BY player_id) t;

-- Rolling 30-day MAU per day (needs player_day)
SELECT d.day, COUNT(DISTINCT pd.player_id) AS mau
FROM generate_series(DATE '2026-10-01', DATE '2026-10-31', INTERVAL '1 day') AS d(day)
JOIN player_day pd ON pd.activity_date > d.day - 30 AND pd.activity_date <= d.day
GROUP BY d.day;
```

## Ordered funnel (PostgreSQL)
```sql
WITH s AS (
  SELECT player_id,
         MIN(event_ts) FILTER (WHERE event_name = 'tutorial_begin')    AS t1,
         MIN(event_ts) FILTER (WHERE event_name = 'tutorial_complete') AS t2,
         MIN(event_ts) FILTER (WHERE event_name = 'level_end')         AS t3
  FROM events WHERE event_date >= DATE '2026-10-01' GROUP BY player_id)
SELECT COUNT(t1) AS step1,
       COUNT(*) FILTER (WHERE t2 > t1 AND t2 <= t1 + INTERVAL '1 day') AS step2,
       COUNT(*) FILTER (WHERE t3 > t2 AND t3 <= t1 + INTERVAL '1 day') AS step3
FROM s;
```

## Python (pandas) snippets
```python
import pandas as pd, numpy as np
df = pd.read_parquet("player_day.parquet")            # player_id, install_date, activity_date
df["day_n"] = (df.activity_date - df.install_date).dt.days
size = df.groupby("install_date").player_id.nunique()
mat = (df[df.day_n.between(0, 30)]
       .groupby(["install_date", "day_n"]).player_id.nunique()
       .unstack().div(size, axis=0))                   # retention matrix
curve = mat[[1, 7, 30]].mean()                         # simple avg; weight by size for pooled

# Bootstrap CI for ARPU difference (by user)
def boot_diff(a, b, n=5000, seed=1):
    rng = np.random.default_rng(seed)
    d = [rng.choice(b, b.size).mean() - rng.choice(a, a.size).mean() for _ in range(n)]
    return np.percentile(d, [2.5, 97.5])
```
- Run via Bash: `python -I analysis/<script>.py --from 2026-10-01 --to 2026-10-31`; write CSV/PNG
  outputs to `.team/reports/assets/`; never print raw PII.
- Charts: matplotlib/plotly; label units, n, date range.

## Dashboards
| Tool | Best for | Notes |
|---|---|---|
| Metabase | self-serve business dashboards, quick SQL questions | easy setup; models + segments; ClickHouse driver available (verify version) |
| Apache Superset | open-source BI at scale, SQL Lab, many DBs | more setup; RBAC; caching layer |
| Grafana | ops/real-time time series (CCU, errors, live-event health) | ClickHouse/Postgres plugins; alerting |
| Looker Studio | GA4/BigQuery free dashboards | slow on large data; use extracts/aggregates |
| UGS / GameAnalytics / Firebase consoles | out-of-box game KPIs | limited joins; export to warehouse for depth |
Dashboard rules: one question per dashboard; KPI tiles with comparison period; definitions linked
to metrics.md; date range + timezone shown; cohort charts show n; alerts on guardrails
(revenue drop > X% vs same weekday, crash spike, event volume anomaly).

## Data quality checks (run before analysis)
- Volume per event/day vs 7-day median (±30% alert); null/empty rate for required properties.
- Duplicates by event_id; client_ts far in future/past (> 24 h skew); unknown enum values.
- Revenue reconciliation vs store/PSP; DAU vs backend login counts (expect close match).

## Sources
- ClickHouse docs, retention function https://clickhouse.com/docs/sql-reference/aggregate-functions/parametric-functions#retention
- ClickHouse docs, windowFunnel https://clickhouse.com/docs/sql-reference/aggregate-functions/parametric-functions#windowfunnel
- GA4 BigQuery export schema https://support.google.com/analytics/answer/7029846
- PostgreSQL docs, Window functions https://www.postgresql.org/docs/current/tutorial-window.html
- BigQuery docs, Query best practices (cost) https://cloud.google.com/bigquery/docs/best-practices-costs
- Metabase docs https://www.metabase.com/docs/latest/
- Apache Superset docs https://superset.apache.org/docs/intro
