---
name: domain-multiplayer
description: Multiplayer concepts for all roles - topology/authority choice, latency and fairness, netcode stack options, hosting, matchmaking, cheating trade-offs.
---
# Domain: Multiplayer games
Mission: shared vocabulary and decision rules so design, production and engineering pick the same multiplayer model early.

## Use when
- Scoping or designing any feature where two or more players share state (PvP, co-op, MMO-lite,
  async/turn-based, casino tables, social hubs, leaderboards with live updates).
- Choosing topology, netcode framework, hosting, or matchmaking; estimating server cost.
- Reviewing a design for latency tolerance, cheat exposure, reconnect behavior.

## Decide first (in this order; record as ADR via tech-lead-architect)
1. Interaction model: realtime (sub-second reactions) / near-realtime (co-op, ~200 ms tolerant) /
   turn-based or table-based (seconds) / async (minutes-days).
2. What is at stake: money or ranked fairness → server-authoritative is mandatory.
3. Player count per session and total CCU target → bandwidth and hosting cost class.
4. Topology: dedicated server / listen (host) server / distributed authority / P2P via relay /
   deterministic lockstep or rollback / plain request-response + push.
5. Stack: engine netcode (NGO, Netcode for Entities, Mirror, FishNet, Photon Fusion/Quantum,
   Normcore) or custom .NET (LiteNetLib/ENet, SignalR/WebSockets + Orleans).
6. Hosting + services: fleet provider, relay, lobby, matchmaking, regions.
7. Failure UX: disconnect, reconnect window, host migration, abandoned match rules.

## Rules of thumb
- Real money, ranked, economy-affecting → dedicated server or backend authority. Client-hosted
  topologies (listen, DA, P2P) only for casual co-op/social where cheating harms nobody else.
- Turn-based/casino tables are request-response + server push (WebSockets/SignalR), not netcode
  frameworks built for 60 Hz physics.
- Physics-heavy competitive play is the most expensive netcode there is; budget senior time.
- Fighting games (1v1, frame-precise) → rollback (GGPO-style / Photon Quantum).
- RTS with thousands of units → deterministic lockstep (send inputs, not state).
- Minimum RTT ≈ distance_km / 100 ms (light in fiber ~200 km/ms, round trip); regions matter more
  than code. Cross-Atlantic play is ~80–100 ms RTT at best.
- Typical feel thresholds (rules of thumb, genre-dependent): < 50 ms excellent; 50–100 ms good;
  100–150 ms playable for action with compensation; > 200 ms only turn-based/async feel fine.
- Server tick ≠ client frame rate: 20–30 Hz casual/BR, 60 Hz action, 128 Hz top competitive shooters.
- Every ms of compensation is a fairness trade: favoring the shooter means victims get hit
  "behind cover"; cap rewind (e.g. 200–250 ms) and tell designers.
- Hosting landscape moves fast: Unity Multiplay hosting ended 31 Mar 2026 (licensed to Rocket
  Science Group); Hathora shut down 5 May 2026. Prefer portable server builds (container + SDK
  adapter) over provider lock-in. (verify current status before committing)

## Glossary (short)
- Authority: who decides the truth for an object (server, owner client, session owner).
- Tick: one fixed simulation step; send rate: snapshots/s actually sent (≤ tick rate).
- Client-side prediction: client simulates its own inputs immediately; reconciliation corrects
  with server state. Interpolation: render remote entities slightly in the past between snapshots.
- Lag compensation: server rewinds hitboxes to what the shooter saw. Rollback: resimulate from a
  past frame when late inputs arrive.
- Interest management (AOI/relevancy): send each client only what it needs/may see.
- RPC: one-off event message; state sync: replicated variables converge over time.
- Relay: forwards packets between clients behind NATs (no game logic). Fleet: pool of game
  server processes; allocation: assigning a session to one.
- CCU: concurrent users; drives server count and egress cost.

## Role pointers
- game-designer / level-designer: designing-for-latency.md before locking combat/abilities.
- producer / product-manager: hosting-and-services.md for cost/vendor risk; topology table for scope.
- economy-monetization-designer / liveops-manager: server authority on all currency flows.
- multiplayer-network-engineer: implementation playbook in `studio:multiplayer-network-engineer`.
- security-engineer: client trust and anti-cheat in `studio:security-engineer`.

## References (read on demand)
- references/topology-and-stack-choice.md — picking topology, authority model, sync model, Unity netcode framework or custom .NET.
- references/hosting-and-services.md — game server hosting, relay, lobby, matchmaking, regions, cost model, vendor status.
- references/designing-for-latency.md — designing mechanics/UX that survive latency, fairness trade-offs, reconnect, cheat-aware design.
