# Latency compensation (implementation reference)

## Technique map
| Technique | Applies to | Hides | Cost |
|---|---|---|---|
| Client-side prediction | locally controlled entity | own input latency (RTT) | must run same movement code on client and server |
| Server reconciliation | predicted entity | prediction errors | input history buffer + resimulation |
| Entity interpolation | remote entities | jitter, low send rate | remote entities shown ~interp delay in the past |
| Extrapolation / dead reckoning | remote vehicles, slow-turning objects | delay when no new data | overshoot/corrections; cap at ~1–2 send intervals |
| Lag compensation (server rewind) | hit detection | shooter's view vs server time | history of hitboxes; "shot behind cover" |
| Rollback (predict-rollback) | whole sim (fighting, Quantum) | all remote input latency | determinism; resim N frames per late input |
| Input delay | lockstep/rollback | reduces rollback depth | adds constant latency (1–3 frames typical) |

## Fixed tick and time
- Simulation runs at fixed tick `dt` (e.g. 1/60 s) on server and clients; rendering interpolates
  between ticks. Never simulate gameplay in `Update` with variable `deltaTime`.
- Client runs AHEAD of the server for its own inputs: client tick ≈ server tick + RTT/2 + jitter
  buffer, so inputs for tick T arrive at the server just before it simulates T.
- Server adjusts client pace: if inputs arrive late (buffer empty) → tell client to speed up
  slightly; if buffer grows → slow down (Overwatch "time dilation" of the command frame rate,
  GDC 2017). NGO/N4E/Fusion do equivalent tick sync internally.
- Clock offset estimate: NTP-style `offset = ((t1 - t0) + (t2 - t3)) / 2`, smoothed (EMA or
  median of last N); never jump time backwards on the client — slew.

## Prediction + reconciliation (Gambetta model)
```csharp
public struct InputCmd { public uint Tick; public Vector2 Move; public bool Jump; }
public struct MoveState { public uint Tick; public Vector3 Pos; public Vector3 Vel; }

public sealed class PredictedMover {
    const int Size = 256;                                 // ring buffer, power of 2 (> max RTT in ticks)
    readonly InputCmd[] inputs = new InputCmd[Size];
    readonly MoveState[] states = new MoveState[Size];
    MoveState current;

    public void ClientTick(uint tick, InputCmd cmd, float dt) {
        cmd.Tick = tick;
        inputs[tick & (Size - 1)] = cmd;
        current = MovementSim.Step(current, cmd, dt);     // SAME pure function the server runs
        current.Tick = tick;
        states[tick & (Size - 1)] = current;
        Net.SendUnreliable(cmd);                          // in practice: send last 3–5 inputs redundantly
    }

    public void OnServerState(MoveState auth, uint latestLocalTick, float dt) {
        var predicted = states[auth.Tick & (Size - 1)];
        if (predicted.Tick == auth.Tick && (predicted.Pos - auth.Pos).sqrMagnitude < 0.0004f) return; // 2 cm tolerance
        current = auth;                                   // rewind to authoritative state
        for (uint t = auth.Tick + 1; t <= latestLocalTick; t++) {   // replay unacknowledged inputs
            current = MovementSim.Step(current, inputs[t & (Size - 1)], dt);
            current.Tick = t;
            states[t & (Size - 1)] = current;
        }
        // visual smoothing: keep render offset = oldRenderPos - current.Pos, decay it over ~100 ms
    }
}
```
- `MovementSim.Step` must be a pure, shared function (same assembly on client and server); any
  hidden state (physics scene, random) breaks reconciliation.
- Send redundant inputs (last 3–5 per packet) over unreliable channel: cheap loss tolerance.
- Server: buffer inputs per client by tick; if an input is missing at sim time, repeat the last
  input (and tell the client); never wait.
- Smooth corrections visually (render offset decay); snap only when error > threshold (e.g. > 1 m).
- Physics-based characters: prediction requires stepping the physics scene for one body
  (`Physics.Simulate` on a separate `PhysicsScene`) or a kinematic controller — prefer kinematic
  character controllers for predicted movement.

## Entity interpolation (remote entities)
```csharp
// Render remote entity at renderTime = serverTimeEstimate - interpDelay
// interpDelay ≈ 2–3 × send interval (e.g. 100 ms at 20–30 Hz; ~ 2 snapshots of cushion against loss)
bool TrySample(SnapshotBuffer buf, double renderTime, out Vector3 pos, out Quaternion rot) {
    if (!buf.TryFindBracket(renderTime, out var a, out var b)) { pos = default; rot = default; return false; }
    float t = (float)((renderTime - a.Time) / (b.Time - a.Time));
    pos = Vector3.Lerp(a.Pos, b.Pos, t);              // Hermite with velocity for fast movers
    rot = Quaternion.Slerp(a.Rot, b.Rot, t);
    return true;
}
```
- Buffer empty (loss burst) → extrapolate ≤ 1 send interval, then hold; adapt `interpDelay` to
  measured jitter (raise quickly, lower slowly).
- Gambetta's demo uses 100 ms; Source engine default `cl_interp` 0.1 s with `cl_interp_ratio` 2.
  Competitive shooters push it down with higher send rates (Valorant: ~1 buffered frame at 128 Hz).

## Lag compensation (server-side rewind)
- Server keeps per-entity hitbox history (ring buffer per tick, ≥ max rewind window).
- On a fire command, rewind target hitboxes to the time the shooter saw:
  `rewindTime = commandTime - shooterInterpDelay` (Valve: server time − packet latency − client view interp).
- Clamp rewind (e.g. ≤ 200–250 ms) — design decision (see `studio:domain-multiplayer` designing-for-latency.md).
- Only rewind entities potentially hit (broadphase against current + swept bounds) for CPU.
- Unity: N4E `PhysicsWorldHistorySingleton` (`LagCompensationConfig`, server history size power
  of 2); Fusion lag-compensated hitboxes (`HitboxManager`/`Runner.LagCompensation.Raycast`);
  FishNet Pro lag compensation; NGO: custom history buffer; Mirror: `LagCompensator` component (collider history, `RaycastCheck` from a `[Command]`).
```csharp
public sealed class HitboxHistory {
    readonly (uint tick, Bounds box)[] ring = new (uint, Bounds)[64];   // 64 ticks ≈ 1 s at 60 Hz
    public void Record(uint tick, Bounds b) => ring[tick & 63] = (tick, b);
    public bool TryGet(uint tick, out Bounds b) { var e = ring[tick & 63]; b = e.box; return e.tick == tick; }
}
```

## Rollback (predict-rollback, GGPO model)
1. Each frame: use confirmed remote inputs if present, else predict (repeat last input).
2. Save state snapshot per frame (fast copy: structs/arrays, no allocations).
3. When a remote input arrives for frame F that differs from the prediction: load state F,
   resimulate F..now with corrected inputs, within the same render frame.
4. Cap rollback window (e.g. 7–8 frames); beyond it, stall or add input delay.
- Requirements: deterministic sim (fixed-point or deterministic float discipline, deterministic
  iteration order, seeded RNG in state), state save/load in < 1 ms, sim step << frame budget
  (rollback 8 frames = 9 sims per frame).
- Unity: Photon Quantum (built-in), or custom sim outside GameObjects (pure C# structs) — Unity
  physics/animation are not rollback-friendly.
- Desync detection: per-frame state checksum exchanged every N frames; log and dump on mismatch.

## Choosing per entity (cheat sheet)
| Entity | Approach |
|---|---|
| Local player movement | predict + reconcile |
| Local player shots/abilities | predict cosmetics; server confirms damage with lag comp |
| Remote players | interpolate (snapshot buffer) |
| Projectiles | server-spawned, client predicted spawn for shooter, interpolate for others |
| Vehicles (fast, momentum) | interpolate + short extrapolation; or predict all (Rocket League style) at high tick |
| Doors/pickups/state | replicated state, no prediction (or predicted with rollback of UI) |

## Sources
- Gabriel Gambetta, "Client-Side Prediction and Server Reconciliation", "Entity Interpolation", "Lag Compensation" https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html
- Valve Developer Community, "Source Multiplayer Networking" https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking
- Glenn Fiedler, "Snapshot Interpolation" https://gafferongames.com/post/snapshot_interpolation/
- Timothy Ford, "Overwatch Gameplay Architecture and Netcode" (GDC 2017) https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and
- Riot Games, "Peeking into VALORANT's Netcode" (2020) https://www.riotgames.com/en/news/peeking-valorants-netcode
- GGPO SDK https://github.com/pond3r/ggpo
- Unity: Netcode for Entities LagCompensationConfig API https://docs.unity3d.com/Packages/com.unity.netcode@1.11/api/Unity.NetCode.LagCompensationConfig.html
- Mirror docs: Lag Compensation https://mirror-networking.gitbook.io/docs/manual/general/lag-compensation.md
