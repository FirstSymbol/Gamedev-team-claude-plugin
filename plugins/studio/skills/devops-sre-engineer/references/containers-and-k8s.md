# Containers and Kubernetes for .NET services (practitioner reference)

## Dockerfile for ASP.NET Core (multi-stage, non-root)
```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY Directory.Packages.props Directory.Build.props global.json ./
COPY src/Api/Api.csproj src/Api/
RUN --mount=type=cache,target=/root/.nuget/packages dotnet restore src/Api/Api.csproj
COPY . .
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet publish src/Api/Api.csproj -c Release -o /app --no-restore /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled AS final
WORKDIR /app
COPY --from=build /app .
USER $APP_UID
EXPOSE 8080
ENTRYPOINT ["dotnet", "Api.dll"]
```
- Copy project files first, restore, then copy source → restore layer cached across code edits.
- .NET 8+ images: non-root `app` user (`$APP_UID`), default port 8080 (`ASPNETCORE_HTTP_PORTS`).
- Chiseled images (no shell, no package manager) cut size and CVE count; debug with
  `kubectl debug --image=busybox --target=<container>` instead of `exec sh`.
- Native AOT (`PublishAot=true`) + `runtime-deps:10.0-noble-chiseled` for minimal startup/memory;
  check library AOT compatibility first (reflection-heavy serializers, EF Core limits).
- Pin base images by digest in prod (`FROM ...@sha256:...`); Renovate/Dependabot bumps it.
- `.dockerignore`: `bin/ obj/ .git/ **/*.user tests/ Library/` — keeps context small and secrets out.
- Config: env vars (`ConnectionStrings__Db`), mounted secrets; never `appsettings.Production.json` with secrets.
- Server GC in containers respects cgroup limits; set `DOTNET_GCHeapHardLimitPercent` only if
  you've measured a reason. Set memory limits — the runtime sizes the heap from them.

## Unity dedicated server image
```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/* \
 && useradd -m -u 10001 game
WORKDIR /srv/game
COPY --chown=game:game build/StandaloneLinux64/ .
USER game
EXPOSE 7777/udp
ENTRYPOINT ["./Server.x86_64", "-batchmode", "-nographics", "-logFile", "-"]
```
- Log to stdout (`-logFile -`); expose game port as UDP; health via a small TCP/HTTP endpoint or the
  orchestrator SDK (Agones/GameLift/PlayFab). Fleet design → multiplayer-network-engineer.

## docker compose for local dev
```yaml
services:
  api:
    build: .
    ports: ["8080:8080"]
    environment:
      ConnectionStrings__Db: "Host=db;Database=game;Username=game;Password=dev"
      OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel:4317"
    depends_on: { db: { condition: service_healthy }, redis: { condition: service_started } }
  db:
    image: postgres:17
    environment: { POSTGRES_USER: game, POSTGRES_PASSWORD: dev, POSTGRES_DB: game }
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U game"], interval: 5s, retries: 10 }
    volumes: ["pgdata:/var/lib/postgresql/data"]
  redis: { image: redis:7 }
  otel: { image: grafana/otel-lgtm, ports: ["3000:3000", "4317:4317", "4318:4318"] }
volumes: { pgdata: {} }
```
- `grafana/otel-lgtm` = single-container Grafana + Loki + Tempo + Prometheus/Mimir for local OTel.
  Aspire (13.x, formerly ".NET Aspire") is an alternative local orchestrator with its own dashboard; pick one per repo via ADR.
- Windows dev machine: Docker Desktop with WSL2 backend; keep repo inside the WSL filesystem or
  accept slow bind mounts on NTFS. Line endings: `.gitattributes` `*.sh text eol=lf`.

## Kubernetes: minimal production Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 3
  strategy: { rollingUpdate: { maxUnavailable: 0, maxSurge: 1 } }
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      securityContext: { runAsNonRoot: true, seccompProfile: { type: RuntimeDefault } }
      topologySpreadConstraints:
        - { maxSkew: 1, topologyKey: topology.kubernetes.io/zone, whenUnsatisfiable: ScheduleAnyway, labelSelector: { matchLabels: { app: api } } }
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: ghcr.io/org/api@sha256:<digest>
          ports: [{ containerPort: 8080 }]
          resources: { requests: { cpu: 250m, memory: 256Mi }, limits: { memory: 512Mi } }
          securityContext: { allowPrivilegeEscalation: false, readOnlyRootFilesystem: true, capabilities: { drop: [ALL] } }
          envFrom: [{ secretRef: { name: api-secrets } }]
          startupProbe:   { httpGet: { path: /healthz/live,  port: 8080 }, periodSeconds: 5, failureThreshold: 30 }
          livenessProbe:  { httpGet: { path: /healthz/live,  port: 8080 }, periodSeconds: 10, failureThreshold: 3 }
          readinessProbe: { httpGet: { path: /healthz/ready, port: 8080 }, periodSeconds: 5 }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api }
spec: { minAvailable: 2, selector: { matchLabels: { app: api } } }
```
- Memory limit set, CPU limit usually not (CPU throttling hurts latency); CPU requests drive scheduling/HPA.
- `readOnlyRootFilesystem` → mount `emptyDir` at `/tmp` if the app writes temp files.

## Probes (k8s docs guidance)
| Probe | Checks | Failure effect | .NET mapping |
|---|---|---|---|
| startup | app finished booting | kill/restart; liveness/readiness paused until success | same as live, generous `failureThreshold` |
| liveness | process can make progress (no deadlock) | container restart | `MapHealthChecks("/healthz/live", new() { Predicate = _ => false })` — no dependency checks |
| readiness | can serve traffic now | removed from Service endpoints, not restarted | `/healthz/ready` with DB/cache checks tagged `ready` |
- Never put DB/downstream checks in liveness: a DB blip restarts every pod (cascading failure,
  explicitly warned in k8s docs). Defaults: `periodSeconds` 10, `timeoutSeconds` 1, `failureThreshold` 3.
- Graceful shutdown: on SIGTERM ASP.NET Core stops accepting, drains (`HostOptions.ShutdownTimeout`,
  default 30 s in .NET 8+ — verify); keep `terminationGracePeriodSeconds` ≥ drain time; a short
  `preStop` sleep (5 s) avoids traffic to terminating pods while endpoints update.

## Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 3
  maxReplicas: 30
  metrics: [{ type: Resource, resource: { name: cpu, target: { type: Utilization, averageUtilization: 65 } } }]
  behavior: { scaleDown: { stabilizationWindowSeconds: 300 } }
```
- Requires metrics-server and CPU requests. Queue/CCU-driven scaling → KEDA (Kafka lag, Redis list,
  Prometheus query). Live-ops events: pre-scale on schedule (KEDA cron) before the spike.
- Game servers (stateful UDP sessions) are NOT scaled by HPA: use Agones Fleet + FleetAutoscaler
  (buffer of Ready servers) — sessions must never be killed by scale-down.
- SignalR/WebSocket services: scale-out needs a backplane (Redis) or Azure SignalR Service plus
  sticky sessions; long connections make scale-down slow — set drain expectations.

## Secrets
| Option | Use when |
|---|---|
| External Secrets Operator ← Key Vault / AWS Secrets Manager / Vault | default for prod; rotation stays in the vault |
| Secrets Store CSI driver | mount as files, no k8s Secret object required |
| Sealed Secrets / SOPS | GitOps without cloud vault |
| Plain k8s `Secret` | dev only; base64 is not encryption — enable etcd encryption at rest anyway |
- Workload identity (Azure Workload Identity / EKS IRSA or Pod Identity / GKE WI) over static keys.
- RBAC: no wildcard verbs; app service accounts get nothing by default (`automountServiceAccountToken: false`).
- NetworkPolicies: default-deny ingress per namespace, allow explicit paths.

## Helm
- One chart per service (or a shared library chart); values per env (`values-stage.yaml`).
- `helm upgrade --install --atomic --timeout 10m` in CI; `helm rollback <rel> <rev>` is the rollback.
- Lint/validate in CI: `helm lint`, `helm template | kubeconform -strict`.
- GitOps alternative: Argo CD / Flux reconcile charts from git; CI only updates image digest in git.

## When NOT to use Kubernetes
| Situation | Prefer |
|---|---|
| ≤ 5 services, team without k8s ops experience | Azure Container Apps, AWS ECS Fargate, Google Cloud Run, App Service |
| Single region turn-based/casino backend, steady load | 2+ VMs/VMSS behind LB with compose or systemd; or PaaS |
| Dedicated game servers only | managed hosting (GameLift Servers, PlayFab, Edgegap) — see `studio:domain-multiplayer` |
| Need k8s for "portability" only | containers + IaC give portability; k8s adds a platform to run |
- Signals k8s is worth it: many services, multiple teams, need for bin-packing/cost, Agones, or an
  existing platform team. Managed control plane only (AKS/EKS/GKE); never self-run etcd.

## Sources
- Kubernetes docs: Liveness, Readiness, and Startup Probes https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
- Kubernetes docs: Horizontal Pod Autoscaling https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- Kubernetes docs: Good practices for Secrets https://kubernetes.io/docs/concepts/security/secrets-good-practices/
- Microsoft Learn: .NET container images https://learn.microsoft.com/dotnet/core/docker/container-images
- Microsoft Learn: Health checks in ASP.NET Core https://learn.microsoft.com/aspnet/core/host-and-deploy/health-checks
- Agones docs: Fleet autoscaling https://agones.dev/site/docs/reference/fleetautoscaler/
- Docker docs: Multi-stage builds https://docs.docker.com/build/building/multi-stage/
