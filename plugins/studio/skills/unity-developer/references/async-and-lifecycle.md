# Lifecycle, async (coroutines / Awaitable / UniTask), threading, Enter Play Mode

## Event function order (per frame, simplified)
```
Instantiate / scene load:  Awake → OnEnable → (sceneLoaded callback) ... Start (before first Update)
Physics (0..n per frame):  FixedUpdate → internal physics → OnTrigger*/OnCollision* → yield WaitForFixedUpdate
Input events processed
Game logic:                Update → coroutines (yield null / WaitForSeconds / Awaitable.NextFrameAsync) → Animation → LateUpdate
Rendering:                 culling → render (URP: RenderPipelineManager.begin/endCameraRendering) → OnGUI
End of frame:              yield WaitForEndOfFrame / Awaitable.EndOfFrameAsync
Pause/quit:                OnApplicationPause / OnApplicationFocus; OnApplicationQuit → OnDisable → OnDestroy
Teardown:                  OnDisable → OnDestroy
```
- `Awake`: runs once when the GameObject first becomes active, even if the component is
  disabled. Init self only (cache components, create state). Don't touch other objects' state.
- `OnEnable`: every enable; subscribe to events here, unsubscribe in `OnDisable` (symmetry).
- `Start`: once, before the first `Update`, only if enabled; safe to read other objects (their `Awake` ran).
- `Instantiate` runs `Awake` + `OnEnable` synchronously inside the call; `Start` runs later
  (next frame, before that object's first Update). Inactive prefab instances defer `Awake`.
- Order between different objects' `Awake`/`Update` is undefined. Need order? Explicit init
  from a composition root, or `[DefaultExecutionOrder(-100)]` as last resort (document it).
- `FixedUpdate`: physics forces/velocity; `Time.deltaTime` inside returns `fixedDeltaTime`.
  Transform moves of rigidbodies → `Rigidbody.MovePosition` + Interpolate for smooth visuals.
- `LateUpdate`: cameras, follow/IK after animation.
- Mobile: save in `OnApplicationPause(true)`; iOS/Android may kill the app without `OnApplicationQuit`.
- `OnDestroy` is not called for objects never activated; `OnDisable`/`OnDestroy` also run on
  scene unload and play-mode exit - guard against touching already-destroyed singletons.

## Choosing async style
| | Coroutine | `Awaitable` (Unity 6 built-in) | UniTask (Cysharp) | `Task` |
|---|---|---|---|---|
| Alloc | iterator + yield objects | pooled, near-zero | zero-alloc struct | allocates per op |
| Return values | no (callbacks) | `Awaitable<T>` | `UniTask<T>` | `Task<T>` |
| Lifetime | stops when GameObject disabled/destroyed | runs until done/cancelled - pass a token | same as Awaitable; `.AttachExternalCancellation` | runs on, even after Play Mode exit |
| WhenAll/WhenAny | manual | no built-in (wrap in Task or loop) | yes, zero-alloc | yes |
| Threads | main only | `BackgroundThreadAsync`/`MainThreadAsync` switch | `SwitchToThreadPool`/`SwitchToMainThread` | `Task.Run` thread pool |
| Await twice | n/a | NEVER (pooled → undefined behavior) | NEVER for UniTask (use `.Preserve()`) | ok |
| Use when | simple sequenced visuals, legacy code | default for new Unity 6 code without UniTask | project already uses it or needs heavy combinators/PlayerLoop timing | pure .NET libs shared with backend |
- Rule: one style per project layer; don't mix UniTask and Awaitable in the same API surface.
- Coroutines belong to the MonoBehaviour that started them: deactivating the GameObject or
  destroying it kills them; `enabled = false` on the component does NOT stop them.

## Awaitable essentials
```csharp
public sealed class LootPopup : MonoBehaviour {
    async Awaitable ShowAsync(LootData data) {
        var ct = destroyCancellationToken;                  // cancels when this object is destroyed
        try {
            var icon = await LoadIconAsync(data.IconKey, ct); // Awaitable<Sprite>
            await Awaitable.WaitForSecondsAsync(0.25f, ct);
            await Awaitable.BackgroundThreadAsync();          // CPU work off main thread
            var text = BuildDescription(data);                 // plain C# only here!
            await Awaitable.MainThreadAsync();                 // back before touching Unity API
            Render(icon, text);
        } catch (OperationCanceledException) { /* destroyed: expected */ }
    }
}
```
- API: `NextFrameAsync`, `WaitForSecondsAsync`, `FixedUpdateAsync`, `EndOfFrameAsync`,
  `BackgroundThreadAsync`, `MainThreadAsync`, `FromAsyncOperation`; any `AsyncOperation`
  (scene load, `UnityWebRequest` op, `ResourceRequest`) is awaitable; `AwaitableCompletionSource` for callbacks.
- Continuations run synchronously when completion triggers (same frame) - no extra frame latency.
- Can `yield return` a non-generic `Awaitable` from a coroutine (not `Awaitable<T>`).
- Need WhenAll: wrap each in a `Task` (`async Task AsTask(Awaitable a) => await a;`) - allocates; or await sequentially.
- Fire-and-forget only at top level (UI event handlers): `_ = ShowAsync(d);` inside a method that
  catches and logs; never `async void` except Unity event handlers, and then wrap in try/catch.
- Many concurrent awaitable loops (hundreds) lose the perf edge - use a manager `Update` instead.

## Cancellation
- `MonoBehaviour.destroyCancellationToken` - per object; `Application.exitCancellationToken` - app/play-mode exit.
- Per-operation cancel (e.g. new search replaces old): `CancellationTokenSource.CreateLinkedTokenSource(destroyCancellationToken)`;
  cancel + dispose the previous CTS before starting the next.
- Disable-scoped work: own a CTS created in `OnEnable`, cancelled in `OnDisable`.
- Always pass the token down to every awaited call; check `ct.ThrowIfCancellationRequested()` after
  awaits that don't take tokens (e.g. Addressables handles, Tasks from SDKs).
- After an await, the object may be destroyed: re-check `this == null` (Unity null) before touching it
  if no token was used.

## Threading rules
- `UnityEngine.Object` APIs, `transform`, `GameObject`, `Component`, `Physics` queries, most
  `Application`/`Time` members: main thread only (exceptions or silent corruption otherwise).
- Off-thread OK: pure C#, `Mathf`/`Vector3`/`Quaternion` math structs, `Debug.Log`, file IO
  (not on Web), `JsonUtility.FromJson` (documented as background-thread safe; check each other API's page).
- Bulk parallel work: Jobs + Burst (see performance.md) beats hand-rolled threads (scheduler,
  safety system, no main-thread stalls).
- `Task.Run` work keeps running after exiting Play Mode in the Editor - always pass a token.
- Web platform: managed C# threads unsupported (no multithreaded GC in WebAssembly) -
  `BackgroundThreadAsync`/`Task.Run` don't parallelize; only native engine code and Burst jobs
  use threads. Design async code to degrade.
- `SynchronizationContext` in Unity = main-thread `UnitySynchronizationContext`; `ConfigureAwait(false)`
  on a Task drops you on a thread pool thread - don't touch Unity API after it.

## Domain reload & Enter Play Mode Options
- Fast Enter Play Mode (default "Reload Scene only" = no domain reload) is the default from Unity 6.6
  and optional before (Project Settings → Editor → Enter Play Mode Settings). Consequences:
  - Static fields, static events, singletons keep values between play sessions.
  - Static event subscribers from the last session still attached → double handlers, NREs.
```csharp
static int s_Score; static event Action s_OnWin;
[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
static void ResetStatics() { s_Score = 0; s_OnWin = null; }
```
  - Editor-side statics: `[InitializeOnEnterPlayMode]`; Unity 6.5+ adds Editor lifecycle
    attributes (e.g. `[OnCodeInitializing]`, each with an unloading counterpart, per the March 2026
    CoreCLR update) designed to survive the CoreCLR move (verify: exact names in 6.5+ Script Reference).
- Scene Reload disabled: scene objects are not recreated - non-serialized/runtime state may
  persist; test both settings if the project toggles them.
- CoreCLR (6.7 experimental player, Unity 7.0 editor — formerly announced as 6.8) replaces domain reload with finer-grained code
  reload - code that resets statics explicitly is future-proof.
- Third-party packages relying on statics: test with domain reload off before enabling project-wide.

## Scene loading lifecycle
- `SceneManager.LoadSceneAsync(name, LoadSceneMode.Additive)`; with `allowSceneActivation = false`
  progress stops at 0.9 until you allow it; `Awake`/`OnEnable` of new objects run on activation (spike there).
- Prefer a persistent Bootstrap scene + additive content scenes; unload with `UnloadSceneAsync`,
  then `Resources.UnloadUnusedAssets()` at loading screens if needed.
- `SceneManager.sceneLoaded` fires after `Awake`/`OnEnable` of that scene's objects, before `Start`.

## Bug patterns → fix
| Bug | Cause | Fix |
|---|---|---|
| NRE in `Awake` referencing other component | other `Awake` not run yet | move cross-object reads to `Start` or explicit init |
| Handler fires twice after replay | static event + domain reload off | reset statics (SubsystemRegistration) |
| "MissingReferenceException" after await | object destroyed during await | `destroyCancellationToken`, null check |
| Coroutine silently stops | GameObject deactivated | run on a persistent runner or use Awaitable + token |
| Jittery movement | physics in `Update` / transform set in `FixedUpdate` | forces in FixedUpdate, Rigidbody interpolation, camera in LateUpdate |
| Background thread exception "can only be called from the main thread" | Unity API off-thread | `await Awaitable.MainThreadAsync()` before Unity calls |
| Await hangs/throws randomly | awaited the same Awaitable twice | await once; wrap in Task for multiple consumers |

## Sources
- Unity Manual: Order of execution for event functions https://docs.unity3d.com/Manual/execution-order.html
- Unity Manual 6.3: Introduction to Awaitable https://docs.unity.com/en-us/engine/6000.3/manual/scripting/programming-distribute-work-threads/async-await-support/async-awaitable-introduction
- Unity Manual: Awaitable code example reference https://docs.unity3d.com/6000.5/Documentation/Manual/async-awaitable-examples.html
- Scripting API: MonoBehaviour.destroyCancellationToken https://docs.unity3d.com/ScriptReference/MonoBehaviour-destroyCancellationToken.html
- Unity Manual 6.6: Configurable Enter Play Mode (default Reload Scene only) https://docs.unity.com/en-us/engine/current/manual/programming-environment/code-reload-serialization/code-reload/code-reloading-editor/configurable-enter-play-mode
- Scripting API 6.3: Awaitable (pooled, await once, implements IEnumerator) https://docs.unity.com/en-us/engine/6000.3/script-reference/unityengine/awaitable
- Unity Manual: Web technical overview (no managed threads) https://docs.unity.com/en-us/engine/current/manual/platform-specific/webgl/intro/technical-overview
- Scripting API: JsonUtility.FromJson (background threads) https://docs.unity.com/en-us/engine/current/script-reference/unityengine/jsonutility/fromjson
- Unity forum: CoreCLR, Scripting and ECS status update (March 2026) https://discussions.unity.com/t/coreclr-scripting-and-ecs-status-update-march-2026/1711852
- UniTask (Cysharp) https://github.com/Cysharp/UniTask
