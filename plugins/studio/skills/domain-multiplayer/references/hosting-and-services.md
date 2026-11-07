# Hosting, relay, lobby and matchmaking (decision reference)

## Vendor status (as of 2026-11; fast-moving — verify before any contract)
| Service | Status | Notes |
|---|---|---|
| Unity Multiplay Game Server Hosting | ended 31 Mar 2026 (no new allocations from 1 Apr 2026); software licensed to Rocket Science Group ("Multiplay by Rocket Science") | Unity Relay, Lobby, Matchmaker, Distributed Authority, NGO unaffected (Unity status notice) |
| Hathora | game hosting shut down 5 May 2026 (announced Mar 2026) after acquisition by Fireworks AI; customers handed over to GameFabric (Nitrado) | Edgegap docs + GamesBeat; Edgegap/Gameye also run migration offers |
| Amazon GameLift Servers (renamed from GameLift, 2025) | active | managed EC2 fleets, Anywhere (own hardware), containers fleets, FlexMatch matchmaking, FleetIQ on Spot |
| PlayFab Multiplayer Servers (Microsoft) | active | Azure-backed, Windows/Linux containers, standby pools; PlayFab Matchmaking + Lobby + Party |
| Edgegap | active | edge orchestration across many locations, deploy containers per match, Unity/Unreal plugins |
| Agones (open source; Google-founded, CNCF Sandbox since 2026, repo `agones-dev/agones`) | active (1.5x releases, 2026) | Kubernetes CRDs for game servers (Fleet, GameServer, FleetAutoscaler, Allocation); self-run on GKE/AKS/EKS |
| GameFabric (Nitrado), Gameye, i3D.net | active (2026) | managed fleets/bare metal; Hathora/Multiplay migration targets |
| Photon Cloud (Fusion 2/Quantum 3/PUN 2) | active; PUN 2 in maintenance/LTS mode (fixes only — new projects: Fusion or Quantum) | relay/room servers included; dedicated Fusion servers self-hosted |
| Steam Datagram Relay / EOS P2P | active | relay + NAT traversal for P2P/listen servers on Steam / Epic |
| Open Match 2 (Google) | public preview (repo README, no tagged releases) | matchmaking framework only; you write match functions |
Lesson from 2026: hosting vendors exit. Keep the server build a plain container, isolate the
provider SDK (allocate/ready/health/shutdown) behind one adapter, and have a second provider tested.

## Hosting options compared
| Option | Ops burden | Cost profile | Fit |
|---|---|---|---|
| Managed fleet (GameLift Servers, PlayFab MPS) | low-medium | per instance-hour + egress; reserved/spot discounts | mid-large PvP, need autoscaling + matchmaking integration |
| Edge orchestrator (Edgegap, Gameye) | low | per vCPU-minute of running sessions | spiky/global player base, low latency per match |
| Agones on managed k8s | high (k8s skills) | raw compute; cheapest at scale | studios with platform team; multi-cloud portability |
| Bare metal (i3D, others) | medium | fixed monthly, cheapest per core at steady load | high steady CCU, plus cloud burst |
| Relay only (Unity Relay, Photon, SDR, EOS) | very low | per CCU / bandwidth | listen server, DA, P2P, co-op |
| Plain ASP.NET Core service (SignalR) | low (same as backend) | standard web hosting | turn-based, casino tables, lobbies |

## Cost model (estimate before ADR)
- Sessions per vCPU = measured! Headless Unity server CPU per match varies 10x by genre. Measure
  with bots: server frame time p99 at target tick and player count.
- Servers needed ≈ peak concurrent matches / sessions per instance × (1 + buffer 10–30%).
- Peak CCU ≈ DAU × peak concurrency ratio (often 5–15% of DAU for session-based games — verify
  with your analytics/comparables).
- Egress: per-client downstream KB/s × CCU × seconds. Example: 10 KB/s × 10,000 CCU = 100 MB/s
  ≈ 360 GB/h. Cloud egress list prices are roughly $0.05–0.09/GB in major regions (verify: current
  AWS/GCP/Azure egress price pages; some game-hosting products bundle bandwidth).
- Turn-based/casino on SignalR: thousands of connections per instance; cost dominated by backend
  DB, not connections.

## Regions and latency
- Place servers where players are: start with 2–4 regions (e.g. us-east, eu-central, ap-southeast,
  sa-east). Measure client→region ping at login (ping beacons/QoS servers) and matchmake by it.
- RTT floor ≈ distance_km / 100 ms; real-world adds 20–50% routing overhead.
- Matchmaking trades: tight latency + skill = long queues in small populations. Widen windows over
  time (e.g. +25 ms allowed RTT every 15 s waiting).

## Relay and NAT
- Most home/mobile networks need relay or NAT punch-through for P2P/listen servers; carrier-grade
  NAT on mobile makes direct P2P unreliable → budget relay for 100% of mobile sessions.
- Relay adds a hop (+ latency) but hides player IPs (DDoS protection for P2P players).

## Lobbies and matchmaking
| Concept | What it is | Options |
|---|---|---|
| Lobby | pre-game room: members, ready state, settings, chat | Unity Lobby, PlayFab Lobby, EOS Lobbies, Steam Lobbies, custom (SignalR + Orleans) |
| Party | group that queues together | platform services or custom |
| Matchmaking ticket | request with attributes (skill, region pings, mode, party size) | Unity Matchmaker, GameLift FlexMatch, PlayFab Matchmaking, Open Match 2, custom |
| Rating | skill estimate | Elo (simple 1v1), Glicko-2 (uncertainty), TrueSkill 2 (Microsoft, teams; patented — verify licensing), OpenSkill (open TrueSkill-like) |
| Backfill | fill leavers' slots in running matches | needs server→matchmaker API |
- Match quality metrics: queue time p50/p95, skill spread per match, ping per match, first-match
  win rate for new players, abandon rate. Owners: game-designer (rules), data-analyst (metrics).
- Small populations: fewer modes/queues, bots to fill, cross-platform play — design decision early.
- Casino/table games: "matchmaking" = seat assignment by stake level, table limits, and
  regulatory constraints (jurisdiction, self-exclusion) — enforced server-side.

## Session lifecycle (dedicated server)
1. Players matched → matchmaker requests allocation in best region.
2. Provider starts/assigns a warm server (keep a ready buffer; cold start of a Unity server image can
   take tens of seconds).
3. Server receives session config (mode, map, expected player IDs), marks Ready/Allocated.
4. Clients get address + short-lived connect token; server validates token on connect.
5. Match runs; server reports results to backend (server-to-server auth), never via clients.
6. Server shuts down or recycles cleanly; logs/metrics shipped; replay/telemetry stored.

## Questions to answer in the hosting ADR
- Target CCU (launch, 6 months), regions, players/session, tick rate, measured sessions per vCPU.
- Topology + who hosts what (game server vs backend vs relay).
- Provider + exit plan (second provider proof-of-concept), SDK adapter boundary.
- Cost estimate (compute + egress) at launch and at 10x; budget owner (producer).
- DDoS protection approach; incident/on-call ownership (devops-sre-engineer).

## Sources
- Unity status notice: Multiplay deprecation https://status.unity.com/info_notices/362941
- Unity Discussions: Multiplay end of services https://discussions.unity.com/t/end-of-services/1698428
- Edgegap: Switch from Hathora (migration docs) https://docs.edgegap.com/docs/tools-and-integrations/switch-from-hathora
- AWS re:Post: Amazon GameLift is now Amazon GameLift Servers https://repost.aws/articles/ARK7UPPDp4QIuP5Rd4qdgKBQ/amazon-gamelift-is-now-amazon-gamelift-servers
- Microsoft Learn: PlayFab Multiplayer https://learn.microsoft.com/gaming/playfab/multiplayer/
- Agones docs https://agones.dev/site/docs/
- CNCF blog: Agones moves to the CNCF (2026-03-23) https://www.cncf.io/blog/2026/03/23/agones-moves-to-the-cncf-a-new-era-for-open-source-multiplayer-game-infrastructure/
- GamesBeat: Hathora acquired, hands customers to Nitrado https://gamesbeat.com/hathora-acquired-will-exit-game-infrastructure-biz-and-hand-over-customers-to-nitrado/
- Photon PUN 2 intro (maintenance/LTS notice) https://doc.photonengine.com/pun/current/getting-started/pun-intro
- Open Match 2 repository https://github.com/googleforgames/open-match2
- Glickman, "The Glicko-2 system" http://www.glicko.net/glicko/glicko2.pdf
