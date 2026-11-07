# Unity C# review checklist

Severity hints: [B]locker, [M]ajor, [m]inor. Engine facts: `studio:stack-unity`; patterns: unity-developer skill.

## Lifecycle and null semantics
- [M] `?.` / `??` / `is null` on `UnityEngine.Object` (bypasses destroyed-object check) → `== null`, `TryGetComponent`, `if (obj)`.
- [M] Events/delegates subscribed in `OnEnable`/`Awake` without unsubscribe in `OnDisable`/`OnDestroy` (leaks, calls on destroyed objects).
- [M] Cross-object access in `Awake` assuming other objects initialized (use `Start` or explicit init order / composition root).
- [M] Static state not reset with Enter Play Mode Options (domain reload off; default in Unity 6.6+ Fast Enter Play Mode, verify) → reset in `[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]`.
- [m] Logic in `Update` that could be event-driven; empty `Update`/`FixedUpdate` methods (still cost a call).

## Async and threading
- [B] Unity API called from a background thread (`Task.Run`, thread-pool continuation) → main thread only.
- [M] `async void` methods (except Unity event handlers wired intentionally) — exceptions vanish.
- [M] Tasks/UniTask/Awaitable not cancelled on destroy → use `destroyCancellationToken`, `GetCancellationTokenOnDestroy()`.
- [M] Coroutines started on objects that get disabled (silently stop) or never stopped.
- [m] `Task.Delay` in WebGL builds (no threads) → `Awaitable.WaitForSecondsAsync` / UniTask.

## Performance and GC (hot paths: Update, physics callbacks, UI rebuild, per-frame)
- [M] Allocations per frame: LINQ, `foreach` over non-struct enumerators of interfaces, boxing, string concat/format, closures capturing locals, `new List` each frame.
- [M] `GetComponent`, `Find*`, `Camera.main` (cached since 2020.2 but still a lookup), `GameObject.Find` inside per-frame code.
- [M] `Instantiate`/`Destroy` churn for bullets/VFX/list rows → `ObjectPool<T>`.
- [m] `SendMessage`/`BroadcastMessage`; `tag == "x"` → `CompareTag`.
- [m] Physics: `Raycast` allocating variants in loops → `RaycastNonAlloc`/`Physics.RaycastAll` alternatives with buffers.
- [m] UI: layout groups rebuilt every frame by changing text/size; large canvases not split (static vs dynamic).
- [m] `Debug.Log` in hot paths shipped to release builds (strip via conditional wrapper).

## Serialization and assets
- [B] Renamed/moved serialized field without `[FormerlySerializedAs]` → data loss in scenes/prefabs/SOs.
- [B] Missing or regenerated `.meta` files, changed GUIDs, edits to `Library/`.
- [M] Public mutable fields for inspector wiring → `[SerializeField] private`.
- [M] Runtime mutation of ScriptableObject assets expecting persistence (editor-only persistence; shared state across scenes).
- [M] `Resources.Load` for new content → Addressables or direct references.
- [M] Hand-edited `.unity`/`.prefab` YAML beyond trivial values; large prefab/scene diffs unexplained.
- [m] Serialized interfaces/polymorphism without `[SerializeReference]` (data silently dropped).

## IL2CPP, platforms, builds
- [B] Reflection-based code (serializers, DI, SignalR client) without `link.xml`/`[Preserve]` → stripped in IL2CPP builds.
- [M] Platform-specific APIs without `#if UNITY_ANDROID`/`UNITY_IOS`/`UNITY_WEBGL` guards; threads/sockets on WebGL.
- [M] Editor-only code (`UnityEditor` namespace) in runtime assemblies without `#if UNITY_EDITOR` or Editor asmdef → build break.
- [M] New code outside asmdefs or asmdef reference cycles; test code in runtime assemblies.
- [m] `System.Text.Json`/C# 10+ syntax used in Unity code or shared libs (Unity 6.x: C# 9, .NET Standard 2.1).

## Networking, economy, security (client side)
- [B] Client computes authoritative outcomes (rewards, wins, prices, timers) or sends amounts the server trusts.
- [B] Secrets/API keys/signing keys in client code or assets (extractable).
- [M] Purchases/claims without idempotency key reused on retry; retries on non-idempotent calls.
- [M] Auth tokens in `PlayerPrefs` plaintext → platform secure storage.
- [M] Using device clock for cooldowns/daily rewards → server time.
- [m] `UnityWebRequest` without timeout/dispose; no handling of offline/5xx/429.
- [M] Shared contract DTO changed in a non-additive way (rename/remove/reorder MessagePack keys) without server coordination.

## Tests
- [M] New pure logic without EditMode tests; logic stuck inside MonoBehaviours making it untestable.
- [m] PlayMode tests depending on frame timing (`yield return null` counts) without deterministic waits.
- [m] Tests not in a test asmdef with `UNITY_INCLUDE_TESTS` constraint.

## Architecture
- [M] New singletons/static managers instead of the project's DI/composition approach.
- [m] MonoBehaviour > ~300 lines mixing input, logic, view → split presenter/logic/view.
- [m] Direct cross-feature references violating asmdef layering (Core → Features).

## Sources
- Unity Manual: Managed code stripping https://docs.unity3d.com/Manual/ManagedCodeStripping.html
- Unity Manual: Configurable Enter Play Mode https://docs.unity3d.com/Manual/configurable-enter-play-mode.html
- Unity Manual: Garbage collection best practices https://docs.unity3d.com/Manual/performance-garbage-collection-best-practices.html
- Unity Scripting API: FormerlySerializedAs https://docs.unity3d.com/ScriptReference/Serialization.FormerlySerializedAsAttribute.html
- Unity e-book: Optimize your game performance for mobile, XR, and the web https://unity.com/resources/mobile-xr-web-game-performance-optimization-unity-6
