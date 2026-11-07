# Quality attributes, trade-offs, capacity

## ISO/IEC 25010:2023 product quality (9 characteristics) — NFR checklist
| Characteristic | Sub-characteristics (main) | Typical game/backend NFR |
|---|---|---|
| Functional suitability | completeness, correctness, appropriateness | payout = paytable for 100% of spins (math tests) |
| Performance efficiency | time behaviour, resource utilization, capacity | API p95 < 200 ms, p99 < 500 ms at peak; client 60 fps on min-spec, < 1.5 GB RAM mobile |
| Compatibility | co-existence, interoperability | N-2 client versions served; OS/device matrix |
| Interaction capability (ex-usability) | recognizability, learnability, operability, user error protection, engagement, inclusivity, user assistance, self-descriptiveness | FTUE ≤ 3 min; colorblind-safe; subtitles; remappable input |
| Reliability | faultlessness, availability, fault tolerance, recoverability | 99.9% monthly API availability; RPO ≤ 5 min, RTO ≤ 1 h; crash-free sessions ≥ 99.5% |
| Security | confidentiality, integrity, non-repudiation, accountability, authenticity, resistance | all currency ops audited; OWASP ASVS L2; tokens ≤ 15 min |
| Maintainability | modularity, reusability, analysability, modifiability, testability | module boundaries enforced by tests; CI < 15 min; coverage on domain ≥ 80% |
| Flexibility (ex-portability) | adaptability, scalability, installability, replaceability | scale 10× via config; new platform port < N weeks; vendor SDKs behind interfaces |
| Safety (new 2023) | operational constraint, risk identification, fail safe, hazard warning, safe integration | photosensitivity warnings; spend limits; fail closed on wallet errors |
- Write each NFR as a quality attribute scenario: source → stimulus → artifact → environment →
  response → response measure. Example: "At 3× normal peak (environment), 5k RPS of spin requests
  (stimulus) to the Game API (artifact) complete with p99 < 400 ms and 0 lost transactions (measure)."
- Every NFR: number, measurement method (load test, APM, crash reporter), owner, priority.

## ATAM-lite trade-off analysis (half-day equivalent; for agents one structured pass)
1. Business drivers: goals, constraints, top quality attributes (from PRD/brief).
2. Utility tree: quality attribute → refinement → scenarios, each rated (importance H/M/L,
   difficulty H/M/L). Focus on (H,H) scenarios.
3. For each (H,H) scenario walk the architecture: which decisions support it?
4. Record sensitivity points (one parameter strongly affects one attribute, e.g., cache TTL →
   staleness), trade-off points (one decision affects several attributes, e.g., sync replication
   ↑ durability ↓ latency), risks and non-risks.
5. Output `.team/reports/arch-review-<topic>.md`: utility tree, findings, risk themes →
   `.team/risks.md`, and ADRs to write/revise.
- Common trade-offs: consistency vs availability/latency (CAP/PACELC), server authority vs
  responsiveness (prediction), cost vs headroom, flexibility (config-driven) vs testability,
  microservices autonomy vs operability.

## Availability tactics
| Tactic | Implementation (.NET/infra) |
|---|---|
| Redundancy | ≥ 2 instances per service across AZs; managed DB with standby/failover |
| Health checks | `/health/live` (process) vs `/health/ready` (dependencies); LB uses ready |
| Timeouts everywhere | per-call timeouts < caller timeout; no infinite waits |
| Retries with backoff + jitter | only idempotent ops; cap attempts (2-3); `AddStandardResilienceHandler()` |
| Circuit breaker / bulkhead | isolate flaky dependencies (ad network, analytics, store validation) |
| Graceful degradation | serve cached config/catalog; queue non-critical writes; disable features via flags |
| Kill switches | remote flags to disable store, events, specific games/slots without a client release |
| Idempotency | idempotency keys on purchases, rewards, spins; safe client retries |
| Backups + restore drills | PITR enabled; restore tested each quarter (RPO/RTO proven, not assumed) |
| Staged rollout | canary 1-5% → 25% → 100%; automated rollback on SLO burn |
- Availability math: serial dependencies multiply (3 × 99.9% = 99.7%); parallel redundancy
  1 − (1 − a)^n (two 99% replicas ≈ 99.99%, if failures independent).
| SLO | Downtime / 30 days | Downtime / year |
|---|---|---|
| 99% | 7.2 h | 3.65 days |
| 99.5% | 3.6 h | 1.83 days |
| 99.9% | 43.2 min | 8.76 h |
| 99.95% | 21.6 min | 4.38 h |
| 99.99% | 4.3 min | 52.6 min |
- Error budget = 1 − SLO; spend it on releases; freeze risky changes when exhausted (Google SRE).

## Scalability tactics
- Stateless API nodes (session in JWT/Redis) → horizontal scale behind LB/K8s HPA.
- Cache: CDN for static/content bundles (Addressables, Remote Config snapshots); HybridCache/Redis
  for hot reads (catalog, config, leaderboards); cache-aside with TTL + stampede protection.
- Database: indexes + query budget first; read replicas for reporting/admin; partition large
  append-only tables (ledger, telemetry) by time; shard by player ID only when one primary can't keep up.
- Async: queue non-interactive work (emails, analytics fan-out, reward grants for events).
- Realtime: SignalR with backplane or dedicated servers; session affinity rules (see stack-dotnet, domain-multiplayer).
- Launch spikes: pre-scale before launch/events/featuring; load test at 3-5× forecast peak.

## Back-of-envelope capacity estimation
- Inputs: DAU, peak concurrency ratio, sessions/day, requests/session, payload sizes, write ratio, retention of data.
- Formulas:
  - avg RPS = DAU × sessions/day × requests/session / 86,400
  - peak RPS = avg RPS × peak factor (daily curve 2-3×; launch/event/featuring 5-10×)
  - concurrent in-flight = RPS × latency (Little's Law) → connection/thread pool sizing
  - storage/year = writes/day × bytes/record × 365 × (1 + index overhead ~0.5-1.0) × replicas
  - bandwidth = RPS × response bytes (+ CDN for assets: installs × bundle size)
- Worked example (social casino, 1M DAU):
  - 6 sessions × 40 requests = 240M req/day → avg ≈ 2,800 RPS → peak ×3 ≈ 8,300 RPS; design 3-5× headroom.
  - Spins: 150/day/DAU → 150M spins/day ≈ 1,740/s avg; ledger 2 entries × 120 B → 36 GB/day raw
    ≈ 13 TB/year → partition by day, aggregate history, archive cold data to object storage.
  - DB concurrency at peak: 5,200 writes/s × 4 ms ≈ 21 concurrent → pool of 50-100 is ample;
    the bottleneck is row-lock contention per hot account, not connections.
  - Telemetry: 100 events/DAU/day × 500 B = 50 GB/day → separate pipeline (batch, compress).
- Latency reference (order of magnitude): memory ref ~100 ns; SSD random read ~16-150 µs;
  same-datacenter round trip ~0.5 ms; cross-region ~70-150 ms; mobile network RTT 50-300 ms.
  Design client flows for 1 request per user action; batch where possible.
- Per-node throughput is workload-specific: measure with a load test (k6, NBomber, Azure Load
  Testing) on a realistic mix before trusting any rule of thumb (verify per stack).

## Performance budgets (client side; own with unity-developer/technical-artist)
- Frame time: 16.6 ms (60 fps) or 33.3 ms (30 fps) on min-spec, with ~20% headroom.
- Mobile: cold start to interactive ≤ 5-10 s; download size per store limits and cellular
  thresholds (verify: current App Store/Play limits); memory below OS kill thresholds on 3-4 GB devices.
- Network: payloads < 10-50 KB per call; compress; avoid chatty polling — push or long-interval polls.

## NFR document skeleton (`.team/specs/architecture/nfr.md`)
- Quality goals (top 5, ranked) → scenarios table: ID | attribute | scenario | measure | method | owner | priority.
- Capacity model: inputs, formulas, results, headroom, date.
- SLOs and error budgets per user journey (login, purchase, spin/match start).

## Sources
- ISO/IEC 25010:2023 overview (arc42 quality model) https://quality.arc42.org/standards/iso-25010
- Len Bass, Paul Clements, Rick Kazman, "Software Architecture in Practice", 4th ed., 2021 (scenarios, tactics).
- SEI, ATAM collection https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/
- Google SRE Book, "Embracing Risk" (error budgets) https://sre.google/sre-book/embracing-risk/
- AWS Builders' Library, "Timeouts, retries, and backoff with jitter" https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- Latency numbers every programmer should know https://gist.github.com/jboner/2841832
- Microsoft Azure Well-Architected Framework https://learn.microsoft.com/en-us/azure/well-architected/
