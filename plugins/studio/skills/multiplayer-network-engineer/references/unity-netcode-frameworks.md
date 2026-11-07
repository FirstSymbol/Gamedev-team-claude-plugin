# Unity netcode frameworks: implementation notes

Choice criteria live in `studio:domain-multiplayer` (topology-and-stack-choice.md). This file is
"how to build it right" once chosen. API names checked against docs where possible; versions move
fast — confirm against the installed package docs before coding (checked 2026-11: NGO 3.2.1,
N4E 7.2, UTP 6.7, MPPM 3.0).

## Common rules (all frameworks)
- One composition point owns the network runner/manager; gameplay code depends on an interface
  (`INetSession`) so tests can run without a network.
- Gameplay sim in plain C# (deterministic where needed) called from the framework's tick
  callback; MonoBehaviours only bridge to views.
- Authority checks at the top of every server-side handler: `if (!IsServer) return;` + ownership + validation.
- Spawn through the framework (registered prefabs/ghosts); never `Instantiate` networked objects directly.
- Scene management through the framework's networked scene loading.
- Strip server-only code from client builds (`#if UNITY_SERVER` / `#if !UNITY_SERVER`, separate asmdefs
  with define constraints) — keeps server logic and secrets out of the client.

## Netcode for GameObjects (NGO 2.x/3.x; 3.0 adds N4E as hard dependency, timing types → `Unity.Netcode.GameObjects.Timing`)
```csharp
public sealed class Health : NetworkBehaviour {
    readonly NetworkVariable<int> hp = new(100, NetworkVariableReadPermission.Everyone,
                                           NetworkVariableWritePermission.Server);
    public override void OnNetworkSpawn() => hp.OnValueChanged += OnHpChanged;
    public override void OnNetworkDespawn() => hp.OnValueChanged -= OnHpChanged;

    [Rpc(SendTo.Server)]                                   // method name must end with "Rpc"
    public void RequestFireRpc(Vector3 aimDir, int clientTick, RpcParams p = default) {
        var sender = p.Receive.SenderClientId;
        if (!FireRules.IsValid(sender, aimDir, clientTick)) return;       // server validation
        // lag-compensated hit test on server, then apply damage → hp.Value -= dmg on victim
    }
    void OnHpChanged(int oldV, int newV) => view.SetHp(newV);
}
```
- Topologies: `StartServer()` (dedicated), `StartHost()` (listen), Distributed Authority via
  Multiplayer Services session (UGS) — DA: owner writes, `HasAuthority` instead of `IsServer` checks.
- `NetworkTransform`: set authority (server vs owner) explicitly; owner-authoritative = trusts the client
  (casual only). Tune thresholds/interpolation; enable half-float/quaternion compression where offered.
- No full built-in prediction/reconciliation: use `AnticipatedNetworkVariable` /
  `AnticipatedNetworkTransform` (client anticipation) for simple cases; implement input-buffer
  reconciliation (latency-compensation.md) for action movement.
- Unity Transport (UTP): DTLS via Relay `"dtls"` connection type or `SetServerSecrets/SetClientSecrets`;
  WebGL → `UseWebSockets = true` (+ `"wss"` with Relay).
- Network simulation: Multiplayer Tools Network Simulator component / UTP debug simulator (testing-netcode.md).
- Testing: Multiplayer Play Mode (main editor + up to 3 virtual players, plus up to 4 local build
  instances; MPPM 3.0 needs Unity 6.3+) and NGO's `NetcodeIntegrationTest` (namespace
  `Unity.Netcode.TestHelpers.Runtime`; asmdef reference `Unity.Netcode.Runtime.Tests` since 2.4.1;
  override `NumberOfClients`, optional `m_EnableTimeTravel` mock transport).

## Netcode for Entities (1.x standalone; core package 6.5+; 7.x on 6000.7+)
7.0 renamed all `NetCode` casing to `Netcode` (namespace `Unity.NetCode` → `Unity.Netcode`, e.g.
`NetcodePhysicsConfig`); auto-updater handles most — names below use the 1.x/6.x spelling.
```csharp
public struct PlayerInput : IInputComponentData {          // auto-sent, buffered per tick
    public float2 Move; public InputEvent Jump;            // InputEvent for one-shot actions
}
[GhostComponent] public struct Health : IComponentData { [GhostField] public int Value; }
public struct Velocity : IComponentData { [GhostField(Quantization = 1000)] public float3 Value; }

[UpdateInGroup(typeof(PredictedSimulationSystemGroup))]
public partial struct MoveSystem : ISystem {
    public void OnUpdate(ref SystemState s) {
        var dt = SystemAPI.Time.DeltaTime;                  // fixed tick inside prediction group
        foreach (var (input, tr) in SystemAPI.Query<RefRO<PlayerInput>, RefRW<LocalTransform>>().WithAll<Simulate>())
            tr.ValueRW.Position += new float3(input.ValueRO.Move.x, 0, input.ValueRO.Move.y) * 5f * dt;
    }
}
```
- Ghost modes: Interpolated (remote), Predicted, OwnerPredicted (predicted for owner, interpolated for others).
- Prediction systems run in `PredictedSimulationSystemGroup` and are re-run for rollback; filter by
  `Simulate` tag; no side effects (VFX/audio) inside prediction — trigger from presentation systems
  when `NetworkTime.IsFirstTimeFullyPredictingTick`.
- Quantization per `GhostField`; relevancy + importance scaling for big worlds; snapshot sizes in Network Debugger.
- Lag compensation: enable in `NetCodePhysicsConfig`; query `PhysicsWorldHistorySingleton` on server
  with the command's interpolation tick.
- Thin clients (headless, no rendering) for load testing are built in — use them.

## Mirror
- Attributes: `[SyncVar(hook = nameof(OnHpChanged))]`, `SyncList<T>`, `[Command]` (client→server),
  `[ClientRpc]` (server→all), `[TargetRpc]` (server→one), `[Server]` guards.
- `[Command(requiresAuthority = true)]` default — keep it; commands on objects the client doesn't own are rejected.
- Transports: KCP (default, reliable UDP), Telepathy (TCP), SimpleWebTransport (WebGL), Steam/EOS transports.
- `NetworkTransformUnreliable` for high-rate movement; enable interest management component on NetworkManager.
- Prediction: only experimental `PredictedRigidbody` (Rigidbodies; docs: "don't recommend using this just yet");
  character/input prediction = your own input-buffer reconciliation. Lag comp: `LagCompensator` component.

## FishNet (v4)
- `SyncVar<T>` / `SyncList<T>` as generic fields (v4 style) with `OnChange` callbacks; `[ServerRpc]`,
  `[ObserversRpc]`, `[TargetRpc]`; `[ServerRpc(RequireOwnership = true)]` default.
- Built-in client-side prediction: `[Replicate]` method taking `IReplicateData` struct +
  `ReplicateState`, `[Reconcile]` method taking `IReconcileData`, override `CreateReconcile()`; run inputs
  on `TimeManager.OnTick`, send reconcile on `OnPostTick` for rigidbodies — follow the prediction guide exactly.
- Observers: add ObserverConditions (distance/grid/scene) — default is everyone sees everything.
- Lag compensation (`RollbackManager`, `ColliderRollback`) is a paid FishNet Pro feature (also Pro: code stripping, LOD).

## Photon Fusion 2
```csharp
public struct NetInput : INetworkInput { public Vector2 Move; public NetworkButtons Buttons; }
public sealed class PlayerMover : NetworkBehaviour {
    [Networked] public int Hp { get; set; }
    [Networked] TickTimer FireCooldown { get; set; }
    public override void FixedUpdateNetwork() {             // runs per tick, resimulated on correction
        if (!GetInput(out NetInput input)) return;
        transform.position += (Vector3)(input.Move * 5f * Runner.DeltaTime);
        if (HasStateAuthority && FireCooldown.ExpiredOrNotRunning(Runner)) { /* lag-comp raycast */ }
    }
    public override void Render() { /* visuals only; interpolated */ }
}
```
- Modes: Shared (client state authority — casual), Host, Server (dedicated); choose per ADR.
- Collect input in `INetworkRunnerCallbacks.OnInput`; never read `Input` inside `FixedUpdateNetwork`.
- Side effects only when `Runner.IsForward` (not during resimulation).
- Lag-compensated hits: Hitbox/HitboxRoot + `Runner.LagCompensation.Raycast` with `HitOptions`.
- Pricing per CCU on Photon Cloud; dedicated-server mode needs your own hosting (domain-multiplayer hosting-and-services.md).

## Photon Quantum 3 (deterministic)
- Sim written in Quantum ECS (fixed-point `FP`, Quantum DSL for components); Unity is the view.
- Only inputs sent; rollback built in; server-side input validation/ "custom plugin" for authority.
- Unity physics/animation are not used in sim; plan content pipeline around Quantum assets.

## Normcore
- Room-based shared datastore (`RealtimeModel`), ownership per model; hosted by Normal only.
- No prediction/server authority for gameplay logic — use for social/VR/co-op prototypes.

## Dedicated server builds (any framework)
- Build target Linux Dedicated Server (server subtarget); `-batchmode -nographics`; `Application.targetFrameRate = tickRate`.
- Read config from env/command line (port, session ID, provider); expose health/ready to the hosting SDK.
- Remove rendering, audio, UI assets via `#if UNITY_SERVER` and Addressables groups excluded from server profile.
- Memory/CPU per instance measured with bots at max players — hand numbers to devops-sre-engineer.

## Sources
- Unity docs: Netcode for GameObjects https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@latest/
- Unity docs: Netcode for Entities (prediction, ghosts, lag compensation) https://docs.unity3d.com/Packages/com.unity.netcode@latest
- Unity docs: Multiplayer Play Mode https://docs.unity3d.com/Packages/com.unity.multiplayer.playmode@latest
- Mirror docs https://mirror-networking.gitbook.io/docs
- FishNet docs https://fish-networking.gitbook.io/docs ; prediction code https://fish-networking.gitbook.io/docs/guides/features/prediction/creating-code/controlling-an-object.md
- NGO API: NetcodeIntegrationTest https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@3.2/api/Unity.Netcode.TestHelpers.Runtime.NetcodeIntegrationTest.html
- N4E changelog (6.5 core package, 7.0 casing rename) https://docs.unity3d.com/Packages/com.unity.netcode@7.2/changelog/CHANGELOG.html
- Mirror docs: Client Side Prediction https://mirror-networking.gitbook.io/docs/manual/general/client-side-prediction.md
- Photon Fusion 2 docs https://doc.photonengine.com/fusion/current/fusion-intro
- Photon Quantum 3 docs https://doc.photonengine.com/quantum/current/quantum-intro
- Normcore docs https://normcore.io/documentation
