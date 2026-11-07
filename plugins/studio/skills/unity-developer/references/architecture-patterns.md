# Unity architecture patterns (practitioner reference)

## Layering for a feature
| Layer | Type | Unity-free? | Tested in |
|---|---|---|---|
| Config/data | ScriptableObject, JSON, Remote Config | data only | EditMode |
| Domain logic | plain C# classes/structs, interfaces | yes | EditMode (fast) |
| Services | plain C# + Unity API adapters (time, input, save, net) | adapters no | EditMode with fakes |
| View/presenter | MonoBehaviour, UI Toolkit controllers | no | PlayMode |
Rule: MonoBehaviours translate engine events into domain calls and render state. Keep them thin.

## Composition / DI options
| Option | Use when | Notes |
|---|---|---|
| VContainer | default for new projects | fast, IL2CPP-friendly, source-gen; `LifetimeScope` per scene |
| Extenject/Zenject | existing project uses it | heavier, reflection; keep, don't mix with another container |
| Manual composition root | small game/jam | one `Bootstrap` MonoBehaviour wires services in `Awake` |
| Service locator | legacy | allowed only behind an interface; never `static` grab-bag |
Avoid: `FindObjectOfType`/`FindAnyObjectByType` at runtime, `GameObject.Find`, static singletons with
state that survives domain reload off (Enter Play Mode Options) — reset statics with
`[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]`.

```csharp
public sealed class GameLifetimeScope : LifetimeScope {
    [SerializeField] RewardsConfig rewardsConfig;
    protected override void Configure(IContainerBuilder b) {
        b.RegisterInstance(rewardsConfig);
        b.Register<IClock, UnityClock>(Lifetime.Singleton);
        b.Register<DailyRewardService>(Lifetime.Singleton);
        b.RegisterComponentInHierarchy<DailyRewardView>();
        b.RegisterEntryPoint<DailyRewardPresenter>(); // IStartable/ITickable without MonoBehaviour
    }
}
```

## Communication patterns
| Pattern | Use | Pitfall |
|---|---|---|
| C# events / `Action` | 1:N inside a module | must unsubscribe; leaks keep destroyed objects alive |
| ScriptableObject event channels | designer-wired cross-scene signals | hard to trace; name channels clearly |
| Message bus (MessagePipe, custom) | decoupled modules, many publishers | overuse = invisible control flow |
| Reactive (R3/UniRx) | UI binding, streams | learning curve; dispose subscriptions (`AddTo(this)`) |
| Direct interface call | clear owner relationship | fine — prefer it when coupling is legitimate |

## State management
- Game flow: explicit state machine (`IState { Enter; Tick; Exit }`) owned by a plain class;
  avoid booleans like `isPaused && !isLoading && ...`.
- Character/AI: hierarchical FSM or behaviour tree; Animator state machine only for animation.
- UI screens: stack-based navigator (push/pop), each screen = presenter + view.

## Data with ScriptableObjects
- Static config (items, levels, balance tables) → SO assets; runtime state → plain C# objects.
- Never mutate SO assets at runtime in builds expecting persistence (edits persist in Editor only).
- Large tables: import from CSV/Sheets via editor tool into SOs; keep source of truth explicit.
- Use `[CreateAssetMenu]`, validation in `OnValidate`, and unique IDs (string/GUID) not list indices.

## Object lifetime & pooling
- `UnityEngine.Pool.ObjectPool<T>` for bullets/VFX/UI rows; reset state on `actionOnGet`.
- Scene loading: additive scenes for persistent systems (Bootstrap scene) + content scenes.
- `DontDestroyOnLoad` only for a single root object owned by the composition root.

## Save/load
- Versioned DTOs (`saveVersion` int + migrations), never serialize MonoBehaviours directly.
- Write to temp file then atomic replace; `Application.persistentDataPath`; handle corrupt files.
- Server-authoritative economies: client save is cache only (see `studio:domain-f2p-liveops`).

## Shared code with .NET backend
- Put DTOs/contracts/pure rules in a `netstandard2.1` library; consume in Unity as a
  local package (`file:` path in manifest) or prebuilt DLL in `Assets/Plugins`; no Unity refs in it.
- Avoid APIs Unity's Mono/IL2CPP lacks: Unity 6.x and 7.0 alphas expose only .NET Standard 2.1 /
  C# 9 (`System.Text.Json` is not shipped; prefer Newtonsoft `com.unity.nuget.newtonsoft-json` on the client).

## Folder/asmdef layout (typical)
```
Assets/_Project/
  Runtime/Core (Game.Core.asmdef)        domain + services, no UI
  Runtime/Features/<Feature>/ (Game.<Feature>.asmdef → Core)
  Runtime/UI (Game.UI.asmdef → Core, Features)
  Editor/ (Game.Editor.asmdef, includePlatforms: Editor)
  Tests/EditMode (Game.Tests.EditMode.asmdef, UNITY_INCLUDE_TESTS)
  Tests/PlayMode (Game.Tests.PlayMode.asmdef)
```
- Dependencies point inward (Features → Core, never Core → Features). Cycles = compile error.
- Split asmdefs to cut iteration time; don't over-split (< ~20 lines each is noise).

## Sources
- Unity e-book "Level up your code with design patterns and SOLID" (Unity, 2024 ed.) https://unity.com/resources/design-patterns-solid-ebook
- Unity e-book "Create modular game architecture with ScriptableObjects" https://unity.com/resources/create-modular-game-architecture-with-scriptable-objects-ebook
- VContainer docs https://vcontainer.hadashikick.jp/
- Unity Manual: Assembly definitions https://docs.unity3d.com/Manual/assembly-definition-files.html
- Unity Manual: Object pooling API https://docs.unity3d.com/ScriptReference/Pool.ObjectPool_1.html
- Unity Manual: Configurable Enter Play Mode https://docs.unity3d.com/Manual/configurable-enter-play-mode.html
- Unity forum: CoreCLR, Scripting and .NET update, October 2026 (7.0 alpha still .NET Std 2.1 / C# 9) https://discussions.unity.com/t/coreclr-scripting-and-net-update-october-2026/1738338
