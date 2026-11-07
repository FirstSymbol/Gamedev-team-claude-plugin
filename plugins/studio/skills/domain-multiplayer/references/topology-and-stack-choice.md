# Topology, authority and stack choice (decision reference)

## Topologies
| Topology | Who simulates truth | Cheat resistance | Server cost | Latency | Fits |
|---|---|---|---|---|---|
| Dedicated server (authoritative) | headless server we host | high | highest (per-session compute) | 1 hop to server, fair for all | competitive PvP, shooters, ranked, real money |
| Listen server / client host | one player's device | low (host can cheat, host advantage) | low (relay only if NAT) | host has 0 ms; others via host | casual co-op, small friend sessions |
| Distributed authority (NGO DA, Fusion Shared) | each client owns some objects; session owner for global state | low | low (cloud service for routing) | owner sees own objects instantly | casual co-op/social, physics-light; not esports (Unity docs) |
| P2P mesh via relay | every peer | low | relay bandwidth only | peer-to-peer RTT | 2–8 players, fighting games (with rollback), co-op |
| Deterministic lockstep | all peers run same sim from inputs | medium (state hack desyncs; map-hack still possible) | low | input delay = slowest peer | RTS, large unit counts |
| Deterministic predict/rollback (GGPO, Photon Quantum) | all peers, resimulate on late inputs | medium-high (server-validated input in Quantum) | low-medium | local input instant | fighting, platform fighters, sports, competitive mobile |
| Request/response + push (REST + WebSocket/SignalR) | backend services | high | low per player | 50–300 ms fine | turn-based, card/casino tables, async PvP, lobbies, chat |
| Async (store-and-forward) | backend | high | lowest | n/a | ghost races, async PvP raids, leaderboards |

## Authority model per object (mix freely within a game)
| Object | Typical authority |
|---|---|
| Player avatar movement | client-predicted, server-authoritative (reconciled) |
| Projectiles/hits | server (with lag compensation) or predicted visuals + server confirm |
| Physics props | server; DA/owner only in casual co-op |
| Inventory, currency, progression, loot | backend services only — never game-client or listen host |
| Casino outcome (cards, reels, RNG) | backend with certified RNG; table server only orchestrates |
| Cosmetic/local-only (camera, VFX) | client, not networked |

## Sync model
| Model | Sends | Strengths | Weaknesses |
|---|---|---|---|
| Snapshot/state sync | entity state (deltas) | late join easy, robust to loss, server authority | bandwidth grows with entities × players |
| Event/RPC-driven | discrete events | cheap for rare actions | lost/late events desync without state backup |
| Input sync (lockstep/rollback) | player inputs only | tiny bandwidth, huge unit counts | requires bit-exact determinism (float, physics, iteration order); hard late join |
Rule: persistent state → replicated state; one-shot cosmetic events → unreliable RPC;
gameplay-critical one-shots → reliable RPC or state.

## Choosing by genre (default; ADR overrides)
| Genre | Topology | Tick (server) | Notes |
|---|---|---|---|
| Competitive FPS/TPS | dedicated, prediction + lag comp | 60–128 Hz | Valorant 128 Hz (Riot tech blog 2020); budget anti-cheat |
| Battle royale (50–100 players) | dedicated, heavy interest mgmt | 20–30 Hz | Apex ~20 Hz, Fortnite ~30 Hz (verify: Respawn 2019 netcode deep-dive post; Epic 2018 Fortnite dev update) |
| MOBA / top-down action | dedicated, prediction | 30 Hz | lockstep historically (e.g. older RTS-derived MOBAs) |
| Fighting / 1v1 precise | P2P + rollback | 60 fps input frames | GGPO model; 1–3 frame input delay + rollback |
| Physics sports/vehicles | dedicated, predict everything | 60–120 Hz | Rocket League: 120 Hz physics, predicts all objects (GDC 2018 "It IS Rocket Science!", Jared Cone; verify figures in GDC Vault) |
| Co-op PvE (2–4) | listen/DA/relay | 20–30 Hz | accept host advantage; cheat only harms the group |
| RTS | lockstep | 10–20 Hz turns | determinism is the main cost |
| Social hub / party | DA or dedicated lightweight | 10–20 Hz | interest mgmt for crowds |
| Turn-based / card / casino table | REST + SignalR/WebSocket push | event-driven | server-authoritative state machine; see `studio:domain-igaming` for real-money rules |
| Async PvP | backend only | n/a | snapshot of defender, server-sim or validated result |

## Unity netcode options (2026 snapshot — verify versions before ADR)
| Option | Authority/topologies | Prediction / lag comp | Hosting | Strengths | Watch out |
|---|---|---|---|---|---|
| Netcode for GameObjects (NGO 2.x/3.x; 3.2.1 current, Unity 6.0+; 3.0 makes N4E a hard dependency) | client-server (dedicated/host), Distributed Authority | no built-in full prediction; client-anticipation APIs; build your own reconciliation | any (Unity Transport; Relay; DA needs UGS service) | first-party, GameObject workflow, MPPM integration | DA: casual only; small-mid player counts; roll your own prediction for action games |
| Netcode for Entities (standalone 1.x ≤ 1.12; core package 6.5+ on Unity 6.5; 7.x needs 6000.7, `NetCode`→`Netcode` renames) | dedicated / host, server-authoritative | full prediction, rollback/resim of predicted ghosts, lag-compensated physics queries, relevancy/importance | any | high entity counts, competitive action, Unity's "fast-paced" answer | requires DOTS/ECS skillset; Entities workflow |
| Mirror | client-server, host | experimental `PredictedRigidbody` (physics only); `LagCompensator` component | any (KCP/Telepathy/Steam transports) | mature, large community, many transports | prediction not core; perf at high CCU needs care |
| FishNet (v4) | client-server, host | built-in client prediction (v2) + lag comp (Pro) | any | free, feature-rich, active | single-maintainer project risk (bus factor) |
| Photon Fusion 2 | Shared, Host, Dedicated Server | tick-based prediction/resim, lag-compensated hitboxes | Photon Cloud (relay) / self-host server | strong prediction out of box, interest mgmt | per-CCU pricing; vendor lock-in |
| Photon Quantum 3 | deterministic predict/rollback | inherent (rollback) | Photon Cloud | frame-perfect, cheat-resistant, mobile/web friendly | must write deterministic Quantum ECS sim (own DSL/fixed-point) |
| Photon PUN 2 | room-based, master client | none | Photon Cloud | legacy simplicity | maintenance/LTS mode; not for new projects (Photon docs) |
| Normcore | room-based shared state, ownership | none (state sync) | Normal-hosted only | fastest to prototype, VR/social | hosted-only, less control over authority |
| Custom over .NET (LiteNetLib/ENet + shared sim lib) | anything, usually dedicated .NET server | you build it | containers anywhere | full control, server in plain .NET (no Unity headless), shared C# code | big engineering cost; only with experienced netcode engineers |
| SignalR / WebSockets (+ Orleans) | backend-authoritative | not needed (event-driven) | ASP.NET Core anywhere | ideal for turn/table/casino, chat, lobbies; same .NET stack as backend | not for 30+ Hz movement; scale-out needs backplane |

## Decision procedure
1. Is precise realtime required? No → REST + push (SignalR) or async. Stop.
2. Money/ranked/economy? Yes → server-authoritative (dedicated server or backend).
3. Determinism feasible and inputs small? (fighting/RTS/sports) → rollback/lockstep (Quantum, GGPO-style).
4. Entities > ~200 networked or competitive shooter → N4E or Fusion (or custom with experts).
5. Casual co-op ≤ 8, GameObject project → NGO (host or DA) / Mirror / FishNet.
6. Team skills and existing code beat feature tables; prototype the riskiest mechanic with
   simulated 150 ms RTT + 2% loss before committing.
7. Record: topology, framework, hosting, tick/send rate, player cap, reconnect policy → ADR.

## Sources
- Unity docs: Netcode for GameObjects — Distributed authority https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.6/manual/terms-concepts/distributed-authority.html
- Unity docs: Netcode for Entities manual + changelog (7.2.0, 2026-10-29) https://docs.unity3d.com/Packages/com.unity.netcode@7.2/changelog/CHANGELOG.html
- Unity docs: NGO changelog (3.2.1, 2026-11-05) https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@3.2/changelog/CHANGELOG.html
- Mirror docs: Client Side Prediction, Lag Compensation https://mirror-networking.gitbook.io/docs/manual/general/client-side-prediction.md , https://mirror-networking.gitbook.io/docs/manual/general/lag-compensation.md
- Photon: Photon products overview https://doc.photonengine.com/photon/current/photon-products
- Glenn Fiedler, "Deterministic Lockstep" / "State Synchronization" https://gafferongames.com/post/deterministic_lockstep/ , https://gafferongames.com/post/state_synchronization/
- Gabriel Gambetta, "Fast-Paced Multiplayer" series https://www.gabrielgambetta.com/client-server-game-architecture.html
- GGPO (rollback networking SDK) https://github.com/pond3r/ggpo
- Riot Games tech blog, "Peeking into VALORANT's Netcode" (2020) https://www.riotgames.com/en/news/peeking-valorants-netcode
- FishNet docs https://fish-networking.gitbook.io/docs
