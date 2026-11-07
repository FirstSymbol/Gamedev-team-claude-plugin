# Observability and operations for .NET services

## OpenTelemetry baseline (traces + metrics + logs)
```csharp
builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("wallet-api", serviceVersion: AppVersion.Value))
    .WithTracing(t => t.AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()       // or Npgsql: .AddNpgsql()
        .AddSource("Game.Wallet"))                     // custom ActivitySource
    .WithMetrics(m => m.AddAspNetCoreInstrumentation().AddHttpClientInstrumentation()
        .AddRuntimeInstrumentation().AddMeter("Game.Wallet"))
    .WithLogging()
    .UseOtlpExporter();                                // OTEL_EXPORTER_OTLP_ENDPOINT env var
```
- Packages: `OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore/Http/Runtime`,
  `OpenTelemetry.Exporter.OpenTelemetryProtocol`. `OpenTelemetry.Instrumentation.EntityFrameworkCore` is still prerelease (1.x-beta, Nov 2026).
- Aspire `ServiceDefaults` project wires all of this plus health checks and resilience; reuse it.
- Backends: Grafana stack (Tempo/Loki/Mimir/Prometheus), Jaeger, Seq, Elastic, Azure Monitor, Datadog — via OTLP, no vendor SDK in code.
- Sampling: parent-based + ratio (e.g. 10%) in prod; always keep error traces (tail sampling in the OTel Collector).
- Propagate `traceparent` (W3C) from Unity/admin clients where possible; return `traceId` in ProblemDetails.

## Custom spans and metrics
```csharp
public sealed class WalletTelemetry(IMeterFactory meters) {
    public static readonly ActivitySource Source = new("Game.Wallet");
    private readonly Counter<long> _debits = meters.Create("Game.Wallet").CreateCounter<long>("wallet.debits", unit: "{debit}");
    private readonly Histogram<double> _amount = meters.Create("Game.Wallet").CreateHistogram<double>("wallet.debit.amount", unit: "{coin}");
    public void Debited(string currency, long amount) {
        _debits.Add(1, new KeyValuePair<string, object?>("currency", currency));
        _amount.Record(amount, new KeyValuePair<string, object?>("currency", currency));
    }
}
using var act = WalletTelemetry.Source.StartActivity("wallet.debit");
act?.SetTag("wallet.id", walletId);
```
- Tags = low cardinality only (currency, result, endpoint). Never player IDs/emails as metric tags (cardinality explosion + PII); IDs go on spans/logs.
- Built-in meters (.NET 8+): `Microsoft.AspNetCore.Hosting`, `...Server.Kestrel`, `...RateLimiting`,
  `System.Net.Http`, `System.Runtime`; .NET 10 adds auth/authorization/Identity metrics.
- RED per endpoint (rate, errors, duration p50/p95/p99) + business metrics (purchases/min, bets/min,
  wallet errors by code, queue lag). SLO example: p95 < 200 ms, 5xx < 0.1% for wallet endpoints.
- Local live view: `dotnet-counters monitor -n wallet-api --counters Microsoft.AspNetCore.Hosting,System.Runtime`.

## Logging
- `ILogger<T>` everywhere in code; choose sink at host level: OTel logs exporter, or Serilog
  (`Serilog.AspNetCore`, `UseSerilog`, `UseSerilogRequestLogging()`) when you need its sinks/enrichers.
- High-volume paths: `[LoggerMessage]` source-generated methods (no boxing/allocation when level is off).
```csharp
static partial class Log {
    [LoggerMessage(EventId = 1001, Level = LogLevel.Warning, Message = "Debit rejected {WalletId} {Reason}")]
    public static partial void DebitRejected(ILogger logger, Guid walletId, string reason);
}
```
- Levels: Information = business events (one per request max), Warning = handled anomaly,
  Error = needs a human; Debug off in prod. Override noisy categories (`Microsoft.EntityFrameworkCore.Database.Command: Warning`).
- Redact: tokens, passwords, card data, emails/phones (PII), receipts. `Microsoft.Extensions.Compliance.Redaction` for classified data.
- Correlate: logs carry TraceId/SpanId automatically with OTel; add `PlayerId` via `BeginScope` on spans/logs (not metrics).

## Aspire (13.x) for local orchestration
```csharp
// AppHost/Program.cs
var builder = DistributedApplication.CreateBuilder(args);
var pg = builder.AddPostgres("pg").WithDataVolume().AddDatabase("game");
var redis = builder.AddRedis("redis");
var api = builder.AddProject<Projects.Wallet_Api>("wallet-api").WithReference(pg).WithReference(redis).WaitFor(pg);
builder.AddProject<Projects.Admin_Bff>("admin-bff").WithReference(api);
builder.Build().Run();
```
- Gives: one-command local env, connection strings via config, dashboard with traces/logs/metrics.
- Standalone dashboard for any OTLP app: `docker run --rm -it -p 18888:18888 -p 4317:18889 -p 4318:18890 -d --name aspire-dashboard mcr.microsoft.com/aspire/dashboard:<tag>`
  (new repo; legacy `mcr.microsoft.com/dotnet/aspire-dashboard` gets Aspire 13 servicing only). Pin a version tag/digest, not `latest`.
- Deployment publishers exist (Docker Compose, K8s, Azure) — treat as a starting point; devops-sre-engineer owns prod manifests.

## Configuration and options
```csharp
builder.Services.AddOptions<PaymentOptions>().BindConfiguration("Payments")
    .ValidateDataAnnotations().ValidateOnStart();
```
- `IOptions<T>` (singleton, fixed), `IOptionsSnapshot<T>` (scoped, per request reload), `IOptionsMonitor<T>` (singleton + change callbacks).
- Source-generated validation: `[OptionsValidator] partial class PaymentOptionsValidator : IValidateOptions<PaymentOptions>` (AOT-safe).
- Precedence (default host): appsettings.json < appsettings.{Env}.json < user-secrets (Development) < env vars < command line.
- Env var nesting `Payments__ApiKey`. Feature flags: `Microsoft.FeatureManagement` or a remote config service.

## Secrets
- Local: `dotnet user-secrets`; never commit `.env`/secrets; add secret scanning (gitleaks) in CI.
- Prod: Key Vault / AWS Secrets Manager / Vault / K8s Secrets via CSI driver; managed identity over static keys.
- Rotate signing keys (JWT) with overlap (publish JWKS with old + new keys).

## Container images
| Image | Use |
|---|---|
| `mcr.microsoft.com/dotnet/aspnet:10.0` | default (Ubuntu 24.04 "noble"; no Debian images for .NET 10) |
| `aspnet:10.0-noble-chiseled` | distroless: no shell/package manager, non-root by default; smaller attack surface |
| `-chiseled-extra` | adds ICU + tzdata (needed when `InvariantGlobalization=false` or time zones used) |
| `runtime-deps:10.0-noble-chiseled` | self-contained / Native AOT apps |
| `-resolute` tags (Ubuntu 26.04, 2026-04) | newer base OS option |
- SDK container publish without Dockerfile: `dotnet publish -t:PublishContainer` (`ContainerBaseImage`, `ContainerFamily=noble-chiseled`).
- Multi-stage Dockerfile: restore with only `*.csproj` + `Directory.*.props` copied first for layer cache.
- Run as non-root (`USER $APP_UID`), port 8080 default since .NET 8, read-only root FS where possible.
- Chiseled has no shell: debug with `kubectl debug` ephemeral containers or `dotnet-monitor` sidecar.
- Set memory limits; .NET respects cgroup limits; `DOTNET_GCHeapHardLimitPercent` if needed.

## Native AOT and trimming tradeoffs
| Aspect | JIT (default) | Native AOT (`<PublishAot>true</PublishAot>`) |
|---|---|---|
| Startup | ~100s ms | ~10s ms; good for scale-to-zero, CLIs, functions |
| Image size | larger | small single binary |
| Peak throughput | best (tiered PGO) | no dynamic PGO; MS docs only claim size/memory/startup gains — benchmark your workload |
| Supported | everything | minimal APIs (RDG source gen), gRPC, worker services; SignalR partial; not MVC controllers, Razor, Session; EF Core partial (precompiled queries, experimental); reflection-heavy libs break |
- Requires source-gen JSON (`JsonSerializerContext`), no runtime codegen; treat all AOT/trim warnings (IL2xxx/IL3xxx) as errors.
- Default for long-running game APIs: JIT + ReadyToRun optional. Use AOT for sidecars/tunnel agents/CLIs where startup and size matter.

## Runtime and diagnostics
- Server GC is default for ASP.NET Core; DATAS (dynamic heap count) on by default since .NET 9 — lowers memory in containers; disable (`DOTNET_GCDynamicAdaptationMode=0`) only with measurements.
- Tools: `dotnet-counters`, `dotnet-trace` (CPU/alloc), `dotnet-dump` (hangs, leaks), `dotnet-gcdump`; `dotnet-monitor` in K8s.
- Thread-pool starvation signature: rising latency, low CPU, growing `threadpool.queue.length` → find sync-over-async.
- Graceful shutdown: `HostOptions.ShutdownTimeout`, readiness flips to unhealthy first, K8s preStop sleep 5–10 s.

## Sources
- .NET observability with OpenTelemetry https://learn.microsoft.com/en-us/dotnet/core/diagnostics/observability-with-otel
- Creating metrics (IMeterFactory) https://learn.microsoft.com/en-us/dotnet/core/diagnostics/metrics-instrumentation
- Compile-time logging source generation https://learn.microsoft.com/en-us/dotnet/core/extensions/logger-message-generator
- Options pattern https://learn.microsoft.com/en-us/dotnet/core/extensions/options
- Aspire docs https://aspire.dev/
- Aspire standalone dashboard (image repo) https://aspire.dev/dashboard/standalone/
- OTel EF Core instrumentation (prerelease) https://www.nuget.org/packages/OpenTelemetry.Instrumentation.EntityFrameworkCore
- .NET aspnet image tags (noble default, resolute, no Debian for 10) https://github.com/dotnet/dotnet-docker/blob/main/README.aspnet.md
- .NET container images https://learn.microsoft.com/en-us/dotnet/core/docker/container-images
- Native AOT for ASP.NET Core https://learn.microsoft.com/en-us/aspnet/core/fundamentals/native-aot
