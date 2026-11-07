# State sync, serialization and bandwidth (implementation reference)

## Rates
| Term | Meaning | Typical |
|---|---|---|
| Tick rate | server simulation steps/s | 20–30 Hz casual/BR, 60 Hz action, 128 Hz competitive FPS |
| Send (snapshot) rate | state packets/s to each client | = tick or tick/2; lower for far/irrelevant entities |
| Client input rate | input packets/s to server | = client tick (with redundancy) |
- Server tick budget: tick work p99 ≤ 70% of `1/tickRate` (60 Hz → ≤ 11.7 ms) at max players.

## Bandwidth budget (compute before building)
```
down_per_client (B/s) = sendRate × (packetOverhead + Σ_visible(entityBytes))
packetOverhead ≈ 28 B IPv4+UDP (48 B IPv6+UDP) + transport header (~4–16 B) + DTLS (~29 B) if used
server_egress (B/s)   = down_per_client × players          (per match)
```
Example: 30 Hz × (40 B + 20 visible × 12 B) = 30 × 280 = 8.4 KB/s per client; 64 players →
~538 KB/s egress per match ≈ 1.9 GB/h. Multiply by matches for hosting cost (domain-multiplayer
hosting-and-services.md).
| Target | Budget (rule of thumb — verify against your audience) |
|---|---|
| Mobile client down | ≤ 10–20 KB/s sustained; bursts on join |
| Mobile client up | ≤ 2–5 KB/s |
| PC/console client down | ≤ 30–60 KB/s; Fiedler's examples target 256 kbit/s (32 KB/s) |
| Packet size | ≤ ~1200 B payload to avoid IP fragmentation (QUIC requires 1200 B minimum datagram support; ENet default MTU ~1400 — verify) |

## RPC vs replicated state
| Use | Mechanism | Channel |
|---|---|---|
| Persistent object state (HP, team, door open) | replicated variable / ghost field | engine-managed (eventual, latest-wins) |
| High-rate transform | snapshot/delta with quantization | unreliable sequenced |
| Player input | input command stream | unreliable, redundant |
| One-shot gameplay event (ability cast, kill) | reliable RPC/event (or state + counter) | reliable ordered |
| One-shot cosmetic (sound, VFX hint) | unreliable RPC | unreliable |
| Chat, inventory, lobby | backend service (SignalR/REST), not the game channel | reliable |
- Late join test: anything set via RPC alone is missing for late joiners → move to state.
- Prefer "state + change counter" over reliable RPC for events that must survive loss/late join
  (e.g. `fireCount` incremented: clients play FX when counter changes).

## Serialization and compression
- Bit-pack, not JSON: write only needed bits; use engine writers (`FastBufferWriter` NGO,
  `NetworkWriter` Mirror, `Writer` FishNet, `DataStreamWriter` UTP, `NetDataWriter` LiteNetLib).
- Quantize:
| Value | Encoding | Size |
|---|---|---|
| Position (±512 m, 1 mm precision) | fixed-point per axis | 20 bits/axis |
| Position relative to cell/origin | delta to grid cell | 10–16 bits/axis |
| Rotation (quaternion) | smallest-three: drop largest, 2-bit index + 3 × 9–10 bits | ~29–32 bits |
| Yaw only (characters) | 0–360° in 8–12 bits | 1–1.5 B |
| Velocity | bounded fixed-point, or omit and derive | 8–16 bits/axis |
| HP/ammo | range-bounded int | ceil(log2(range)) bits |
| Booleans/flags | bitfield | 1 bit each |
- Fiedler's cube demo needed 4096 units/m position and 15-bit quaternion components to avoid
  visible pops under extrapolation — precision depends on the sim; measure, don't guess.
- Delta compression: send only changed fields relative to the last acked snapshot (baseline);
  requires per-client ack tracking; fall back to full state if baseline too old.
- Both sides must simulate from quantized values (quantize server state too) to avoid drift.
- Avoid per-packet allocations: pooled buffers, structs, `Span<byte>`; GC spikes = tick spikes.

## Priority and interest management
- Relevancy (AOI): send entity only if it can affect/see the client — distance/grid cells, line
  of sight (PvP hidden info), team, room/zone.
- Priority accumulator (Fiedler): each entity accumulates priority per tick (higher for near,
  fast, interacting); fill packet in priority order up to byte budget; reset sent entities.
- Update frequency by distance tier: near every tick, mid every 2–4 ticks, far every 8+ ticks.
| Framework | Interest API |
|---|---|
| NGO | `NetworkObject.CheckObjectVisibility`, `NetworkShow/NetworkHide`; scene-based; custom per-client visibility |
| Netcode for Entities | ghost relevancy (`GhostRelevancy` set/mode), importance scaling (`GhostDistanceImportance`) |
| Mirror | Interest Management components (Spatial Hashing, Distance, Scene, Match, Team) |
| FishNet | ObserverManager + ObserverConditions (Distance, Grid, Scene, Match, Owner) |
| Fusion | Area of Interest (AOI) + per-player object interest |

## Reliability and ordering
- Reliable ordered over UDP = head-of-line blocking on loss; keep it for low-rate critical messages.
- Unreliable sequenced (drop older than last received) for state and inputs.
- Separate channels so a lost reliable message does not stall state updates.
- WebSockets/TCP (WebGL, SignalR) are reliable-ordered only: fine for turn/table games; for
  realtime action on WebGL use WebRTC data channels or accept higher interp delay (UTP on Web =
  WebSockets, `UseWebSockets`; verify: WebRTC/WebTransport support in UTP 6.x release notes).

## Netcode protocol versioning
- `protocolVersion` handshake on connect; mismatch → reject with "update required".
- Additive changes only within a version (append fields with defaults); bump version on removal.
- Shared DTO/serialization code in one assembly used by client and server (Unity asmdef +
  `netstandard2.1` library for .NET servers).

## Measurement
- Engine tools: Unity Multiplayer Tools (Network Profiler, Runtime Network Stats Monitor) for NGO;
  N4E Network Debugger (snapshot sizes per ghost type); Fusion Network Statistics; Mirror/FishNet stats.
- Log per-tick bytes per entity type; alert in tests when a type exceeds its budget.
- Report in `.team/reports/net-<feature>.md`: bytes/s per client (p50/p95), egress per match, tick ms p99.

## Sources
- Glenn Fiedler, "State Synchronization", "Snapshot Compression", "Reading and Writing Packets" https://gafferongames.com/post/state_synchronization/ , https://gafferongames.com/post/snapshot_compression/
- Glenn Fiedler, "Packet Fragmentation and Reassembly" https://gafferongames.com/post/packet_fragmentation_and_reassembly/
- RFC 9000 (QUIC), §14 Datagram Size (1200-byte minimum) https://www.rfc-editor.org/rfc/rfc9000#section-14
- Unity docs: Netcode for Entities — ghost relevancy/importance https://docs.unity3d.com/Packages/com.unity.netcode@latest
- Mirror docs: Interest Management https://mirror-networking.gitbook.io/docs/manual/interest-management
- FishNet docs: Observers https://fish-networking.gitbook.io/docs
- Unity Multiplayer Tools docs https://docs.unity3d.com/Packages/com.unity.multiplayer.tools@latest
