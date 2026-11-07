# Observability, SLOs and incident response (practitioner reference)

## SLI / SLO / error budget (Google SRE)
- SLI = good events / valid events, measured as close to the user as possible (LB/gateway logs,
  client telemetry), not host CPU.
- SLO = target for an SLI over a rolling window (typically 28 or 30 days).
- Error budget = 1 − SLO. 99.9% over 30 d = 43.2 min of full outage, or 0.1% of requests.
| SLO | Budget / 30 d | Budget / week |
|---|---|---|
| 99% | 7.2 h | 1.68 h |
| 99.5% | 3.6 h | 50.4 min |
| 99.9% | 43.2 min | 10.1 min |
| 99.95% | 21.6 min | 5.04 min |
| 99.99% | 4.32 min | 1.01 min |
- Pick the SLO from user need and dependency ceilings: you cannot beat the product of your hard
  dependencies' availability. Start lower than you think, tighten with data.
- Error budget policy (written, agreed with product-manager): budget exhausted → freeze risky
  feature releases, spend capacity on reliability until back within SLO.

## Game/backend SLI catalogue (starting points — tune with data)
| Journey | SLI (good / valid) | Typical SLO |
|---|---|---|
| Login/auth | non-5xx and < 2 s / all login attempts | 99.9% |
| Store / IAP verify | receipt validated & entitlement granted < 5 s / valid receipts | 99.95% |
| Matchmaking | matched < target wait (e.g. 60 s p95) / tickets | 99% |
| Game session | sessions ended normally (not server crash/desync) / sessions started | 99.5% |
| Casino spin/bet | bet settled correctly < 1 s / bets placed | 99.95% (+ zero ledger mismatches, separate invariant) |
| API latency | requests < 300 ms / requests | 99% |
| Client stability | crash-free sessions (Crashlytics/Sentry) | ≥ 99.8% live, ≥ 99.5% beta (gate owner: `studio:qa-lead` (release-quality-gates)) |

## Alerting: multiwindow, multi-burn-rate (SRE Workbook ch. 5)
- Burn rate = observed error rate / (1 − SLO). Burn rate 1 spends exactly the budget over the window.
| Budget consumed | Long window | Short window | Burn rate | Action |
|---|---|---|---|---|
| 2% | 1 h | 5 min | 14.4 | page |
| 5% | 6 h | 30 min | 6 | page |
| 10% | 3 d | 6 h | 1 | ticket |
- Fire only when both windows exceed the threshold (short window makes it reset fast).
```yaml
# Prometheus rule (99.9% SLO), error ratio recorded as slo:errors:ratio_rate<window>
- alert: ApiErrorBudgetFastBurn
  expr: slo:errors:ratio_rate1h > (14.4 * 0.001) and slo:errors:ratio_rate5m > (14.4 * 0.001)
  labels: { severity: page }
  annotations: { runbook_url: "https://…/runbooks/api#fast-burn", summary: "API burning error budget 14x" }
```
- Every page: user-visible, urgent, actionable, has a runbook link. Otherwise → ticket or dashboard.
- Low-traffic services (< ~1 req/min): use synthetic probes or longer windows; burn-rate is noisy.
- Track pages per on-call shift; Google SRE targets ≤ 2 incidents per 12 h shift for sustainable on-call.

## Telemetry pipeline
```
.NET app (OpenTelemetry SDK) --OTLP--> OTel Collector (agent/gateway) --> Prometheus/Mimir (metrics)
Unity client (crash + analytics SDK) -----------------------------------> Loki (logs), Tempo/Jaeger (traces)
                                                                          Grafana (dashboards, alerting)
```
```csharp
builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("wallet-api", serviceVersion: BuildInfo.Version))
    .WithTracing(t => t.AddAspNetCoreInstrumentation().AddHttpClientInstrumentation()
                       .AddSource("Studio.Wallet"))                  // custom ActivitySource
    .WithMetrics(m => m.AddAspNetCoreInstrumentation().AddRuntimeInstrumentation()
                       .AddMeter("Studio.Wallet"))                   // custom Meter
    .UseOtlpExporter();                                              // OTEL_EXPORTER_OTLP_ENDPOINT
builder.Logging.AddOpenTelemetry(o => { o.IncludeScopes = true; o.IncludeFormattedMessage = true; });
```
```yaml
# otel-collector (gateway) essentials
receivers: { otlp: { protocols: { grpc: {}, http: {} } } }
processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 25 }
  batch: {}
  tail_sampling: { policies: [ { name: errors, type: status_code, status_code: { status_codes: [ERROR] } },
                               { name: slow, type: latency, latency: { threshold_ms: 500 } },
                               { name: base, type: probabilistic, probabilistic: { sampling_percentage: 10 } } ] }
exporters: { otlphttp/loki: { endpoint: http://loki:3100/otlp }, prometheusremotewrite: { endpoint: http://mimir/api/v1/push }, otlp/tempo: { endpoint: tempo:4317, tls: { insecure: true } } }
service:
  pipelines:
    traces:  { receivers: [otlp], processors: [memory_limiter, tail_sampling, batch], exporters: [otlp/tempo] }
    metrics: { receivers: [otlp], processors: [memory_limiter, batch], exporters: [prometheusremotewrite] }
    logs:    { receivers: [otlp], processors: [memory_limiter, batch], exporters: [otlphttp/loki] }
```
- `memory_limiter` first, `batch` last in each pipeline (collector docs recommendation).
- Metric cardinality: never label by user/session/bet ID; per-label-set cost explodes in Prometheus.
  IDs go in traces/logs. Budget: < ~10k active series per service unless justified.
- Logs: structured (JSON), correlation via `trace_id`; no PII, tokens or card data in logs.
- Dashboards per service: RED (Rate, Errors, Duration) for request services, USE (Utilization,
  Saturation, Errors) for resources; game: CCU, matches/min, tick time p99, server FPS.

## Incident response
| Severity | Definition (example) | Response |
|---|---|---|
| SEV1 | outage of core journey for many users, data/money integrity risk | page now, IC assigned, status page, exec + compliance notified |
| SEV2 | major degradation or one region/platform down | page, IC, status page |
| SEV3 | minor/partial, workaround exists | business hours ticket |
Roles (SRE book "Managing Incidents"): Incident Commander (decides, delegates, holds state),
Operations lead (only one making changes), Communications lead (status page, stakeholders,
cadence e.g. every 30 min), Scribe (timeline). Small team: IC + ops + comms minimum.
1. Declare early (cheap to downgrade); open channel `#inc-<date>-<slug>`; assign IC.
2. Mitigate before root-causing: rollback, flag off, failover, scale, shed load.
3. Communicate on a fixed cadence even with no news.
4. Declare resolved when SLIs recover; hand over explicitly if shift ends.
5. Postmortem for every SEV1/SEV2 (templates/postmortem.md) within 5 business days; blameless.
- Real-money incidents (wallet mismatch, RNG/payout error): freeze affected operations, preserve
  logs/DB snapshots, notify compliance-advisor immediately — regulators may require reporting
  within fixed windows (gaming-regulator windows differ per jurisdiction: confirm with compliance-advisor;
  GDPR Art. 33 personal-data breach = 72 h to the supervisory authority).

## Runbook format (`.team/specs/ops/runbook-<service>.md`)
```
## <Alert name>
Meaning: <what the user experiences>
Dashboards: <links>     Owner: <team>     Escalation: <who after 30 min>
Check: 1. <query/command> → expected <x>
Mitigate: 1. <rollback/flag/scale command>  2. <...>
Verify: SLI back above <threshold> for 15 min
```
- Each alert ↔ one runbook section; review runbooks after each incident; test commands on stage.

## DORA metrics (dora.dev, 2024+ model)
| Metric | Definition | Elite-ish signal |
|---|---|---|
| Deployment frequency | prod deploys per period | on demand / multiple per day |
| Change lead time | commit → running in prod | < 1 day |
| Change fail rate | deploys causing degradation needing remediation / deploys | low (benchmarks shift yearly — verify current report) |
| Failed deployment recovery time | time to recover from a failed deploy | < 1 h |
| Deployment rework rate (added 2024) | unplanned deploys due to prod incidents / deploys | low |
- Throughput = lead time, frequency, recovery time; instability = fail rate, rework rate.
- Compute from CI/CD + incident data automatically; never use them to rank individuals.
- Mobile/console clients: measure for the backend and for client release trains separately.

## Sources
- Google SRE Book, ch. 4 "Service Level Objectives", ch. 14 "Managing Incidents", ch. 15 "Postmortem Culture" https://sre.google/sre-book/table-of-contents/
- Google SRE Workbook, ch. 5 "Alerting on SLOs" https://sre.google/workbook/alerting-on-slos/
- Google SRE Workbook, "Error Budget Policy" example https://sre.google/workbook/error-budget-policy/
- OpenTelemetry .NET docs https://opentelemetry.io/docs/languages/dotnet/
- OpenTelemetry Collector configuration https://opentelemetry.io/docs/collector/configuration/
- DORA metrics guide and history https://dora.dev/guides/dora-metrics-four-keys/ , https://dora.dev/guides/dora-metrics/history/
- Grafana docs: Loki OTLP ingestion https://grafana.com/docs/loki/latest/send-data/otel/
