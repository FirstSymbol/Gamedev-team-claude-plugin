# Testing networked games (implementation reference)

## Test pyramid for netcode
| Level | What | Tooling | Runs |
|---|---|---|---|
| Unit | serialization round-trip, quantization error bounds, sim step purity, reconciliation replay | NUnit/xUnit on shared sim lib; Unity EditMode | every PR |
| Integration (in-process) | server + N clients in one process with fake/loopback transport | NGO `NetcodeIntegrationTest` (`Unity.Netcode.TestHelpers.Runtime`), N4E test worlds (client+server worlds), custom harness | every PR |
| Multi-instance local | editor + virtual players / clones under simulated network | Multiplayer Play Mode, ParrelSync | dev loop, manual QA |
| Headless bots | real builds, scripted clients, real network | thin clients (N4E), headless client builds, .NET bot clients | nightly |
| Load/soak | target CCU per server, hours long | bot fleet in cloud, server metrics | before launch, per major release |
| Playtest under latency | humans with conditioner profiles | simulator presets | per milestone |

## Network condition profiles (use the same names everywhere)
| Profile | RTT | Jitter | Loss | Notes |
|---|---|---|---|---|
| LAN | 1–5 ms | 0 | 0% | baseline only |
| Good broadband | 40 ms | 5 ms | 0.5% | |
| Typical | 100 ms | 20 ms | 1% | acceptance target for responsiveness |
| Bad | 200 ms | 40 ms | 3% | must remain fair/understandable |
| Mobile 4G spiky | 80–300 ms | 60 ms | 2% + 1 s outage bursts | tests reconnect + buffer adaptation |
| Packet duplication/reorder | 100 ms | 30 ms | 1% dup, 5% reorder | catches sequence bugs |
(Values are team conventions, not standards; tune to telemetry once live.)

## Simulators
| Tool | Platform | Use |
|---|---|---|
| Unity Multiplayer Tools Network Simulator (component/presets) | Editor/dev builds with Unity Transport | per-instance presets in MPPM, scripted scenarios (lag spikes, disconnects) |
| Unity Transport simulator pipeline (`SimulatorPipelineStage` + `SimulatorUtility.Parameters`: `PacketDelayMs`, `PacketJitterMs`, `PacketDropPercentage`, `PacketDuplicationPercentage`, `Mode`) | UTP (6.7 API) | low-level loss/delay/jitter/dup/fuzz for custom stacks |
| clumsy | Windows (WinDivert) | system-wide lag/drop/throttle/out-of-order on dev machine; filter by port, e.g. `udp and udp.DstPort == 7777` |
| `tc netem` | Linux (servers, CI containers) | `tc qdisc add dev eth0 root netem delay 100ms 20ms loss 1%` |
| Network Link Conditioner | macOS/iOS | device-level profiles for iOS testing |
| Android emulator network settings / developer options | Android | coarse latency profiles |
| LiteNetLib built-in `SimulateLatency`/`SimulatePacketLoss` | LiteNetLib | debug builds of custom .NET stack |
- Simulate on both directions; asymmetric loss (upload worse) is common on mobile.
- Never leave simulators enabled in release builds (compile out with `#if DEVELOPMENT_BUILD`).

## Multi-instance in the editor
- Multiplayer Play Mode (Unity 6+; MPPM 3.0 needs 6.3+): main editor + up to 3 virtual players (+ up to 4 local builds), tags
  per player (e.g. "Server", "Client") to drive role selection; integrates with NGO/N4E.
- ParrelSync: project clones (symlinked Assets) as separate editors — works on older Unity versions
  and for frameworks without MPPM support; clones must not edit assets (read-only discipline).
- Builds: for perf/timing truth, test player builds (Mono vs IL2CPP differences, real frame pacing).

## Automated multi-client tests (patterns)
```csharp
[UnityTest]
public IEnumerator LateJoiner_ReceivesDoorState() {
    yield return StartServerAndClients(clients: 1);
    ServerDoor.Open();                               // state change before second client joins
    yield return ConnectAdditionalClient(out var late);
    yield return WaitUntilReplicated(late, d => d.IsOpen, timeoutSeconds: 2);
    Assert.IsTrue(late.Door.IsOpen);
}
```
Must-have scenarios:
- [ ] Late join gets full state; reconnect within window restores the same player.
- [ ] Duplicate and out-of-order packets do not double-apply commands (idempotency/seq).
- [ ] Prediction: with 150 ms RTT, local movement has zero correction in steady state (same sim both sides).
- [ ] Reconciliation: forced server correction converges within N ticks without visible snap > threshold.
- [ ] Invalid commands (speed, range, cooldown, not owner) are rejected and counted.
- [ ] Host/session-owner leaves (listen/DA): defined behavior (migration or clean end).
- [ ] Protocol version mismatch → clean rejection message.
- [ ] Server tick p99 under max players with bots stays within budget.

## Desync detection (lockstep/rollback and shared-sim stacks)
- Hash critical state every N ticks (e.g. FNV-1a/xxHash over positions, HP, RNG state in fixed order);
  exchange/compare; on mismatch dump both states with tick and inputs for replay.
- Record input logs; deterministic replay test in CI: replay recorded match → final hash equals recorded hash.
- Cross-platform determinism test: same replay on Windows x64, Android ARM64, iOS — float drift shows up here.

## Bots and load testing
- Bot client = headless build (N4E thin clients, `-batchmode -nographics` client build) or a .NET
  console client using the shared protocol library (cheapest per bot; thousands per VM).
- Bot behaviors: idle, random walk, scripted combat, worst-case (everyone in one spot, max ability spam).
- Measure per server instance: tick time p50/p99, CPU %, memory, bytes/s in/out, GC pauses, players
  per vCPU at which p99 tick crosses budget → that's sessions per vCPU for hosting cost.
- SignalR/table services: load test with k6 (WebSocket) or a .NET client harness; measure broadcast
  latency p99 at N tables × M players; test Redis backplane failover.
- Soak: 4–24 h runs to find leaks (memory growth, handle leaks, unbounded dictionaries of disconnected peers).

## What to report (`.team/reports/net-<feature>.md`)
- Profiles tested, correction rate (corrections/min), max visible snap, bandwidth p50/p95 per client,
  egress per match, server tick p99, sessions per vCPU, open issues with repro profile.

## Sources
- Unity docs: Multiplayer Play Mode https://docs.unity3d.com/Packages/com.unity.multiplayer.playmode@latest
- Unity docs: Multiplayer Tools (Network Simulator) https://docs.unity3d.com/Packages/com.unity.multiplayer.tools@latest
- ParrelSync https://github.com/VeriorPies/ParrelSync
- clumsy https://jagt.github.io/clumsy/
- Linux tc-netem man page https://man7.org/linux/man-pages/man8/tc-netem.8.html
- Unity docs: Netcode for Entities (thin clients) https://docs.unity3d.com/Packages/com.unity.netcode@latest
- Grafana k6 WebSockets https://grafana.com/docs/k6/latest/using-k6/protocols/websockets/
- Unity Transport API: SimulatorUtility.Parameters https://docs.unity3d.com/Packages/com.unity.transport@6.7/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html
- NGO API: NetcodeIntegrationTest https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@3.2/api/Unity.Netcode.TestHelpers.Runtime.NetcodeIntegrationTest.html
- Unity docs: Multiplayer Play Mode 3.0 https://docs.unity3d.com/Packages/com.unity.multiplayer.playmode@3.0/manual/index.html
