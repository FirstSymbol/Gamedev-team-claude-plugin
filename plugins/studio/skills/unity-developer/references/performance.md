# Unity client performance (CPU, GC, memory, Jobs/Burst)
Rendering-side fixes (shaders, overdraw, textures) → technical-artist; pipeline/batching facts →
`studio:stack-unity` (rendering-and-pipelines). Tool deep-dives, A/B method, perf/alloc tests,
GC modes, Burst/Collections depth, IL2CPP and thermals → `studio:unity-performance`.

## Budgets
| Target | Frame budget | Mobile working budget (65%, Unity guidance) |
|---|---|---|
| 30 fps | 33.33 ms | ~21.7 ms |
| 60 fps | 16.67 ms | ~10.8 ms |
| 72 / 90 / 120 fps (XR, high-refresh) | 13.9 / 11.1 / 8.3 ms | profile thermals on device |
- Mobile keeps ~35% idle so the SoC cools; full-budget frames → thermal throttling within
  minutes. Profile 15-20+ minute sessions on real devices, not only the first minute.
- Set `Application.targetFrameRate` explicitly (mobile default is 30); `QualitySettings.vSyncCount = 0` on mobile.
- Device-tier heuristics (practitioner rules of thumb, verify per game on target devices):
| Tier (example) | Batches/draws | Visible tris | App memory (resident) |
|---|---|---|---|
| Low Android (2-3 GB RAM, Mali-G52 class) | ≤ 100-150 | ≤ 100-200k | ≤ ~500-700 MB |
| Mid (4-6 GB, 2021+ SoC) | ≤ 200-400 | ≤ 300-600k | ≤ ~1 GB |
| High / recent iPhone | ≤ 500-1000+ | ≤ 1M+ | ≤ ~1.5-2 GB (Apple publishes no jetsam limit; query `os_proc_available_memory()` on device) |
- Write chosen budgets into `.team/specs/architecture/perf-budget.md` (owner tech-lead-architect); test against the
  lowest device of each tier; higher tiers get quality toggles.

## Profiling workflow
1. Reproduce on a **Development Build** on target device (Autoconnect Profiler / attach by IP);
   Editor profiling only for relative comparisons (Editor overhead skews numbers).
2. CPU Usage module → Timeline: find the bound thread.
   - Main thread busy whole frame → CPU main-thread bound (scripts, physics, animation, UI).
   - Main in `Gfx.WaitForPresentOnGfxThread` + render thread busy in `Camera.Render` → render-thread bound (draw calls/setup).
   - Main in `WaitForJobGroupID` → job/worker bound or sync points.
   - Main in `Gfx.WaitForPresentOnGfxThread` and render thread in `Gfx.PresentFrame`/`WaitForLastPresent` → GPU-bound.
   - `WaitForTargetFPS` idle → within budget.
3. Hierarchy view sorted by Self ms and GC Alloc; add `ProfilerMarker`s to narrow down;
   Deep Profiling only in a second pass (it distorts relative costs).
4. **Profile Analyzer** (package): capture 300+ frames before/after a change, compare
   median/max per marker - report deltas, not single frames.
5. **Memory Profiler** (package 1.1+): snapshot at menu → level → back to menu; diff for leaked
   assets, duplicate textures, managed growth. Check "Untracked"/native vs managed split.
6. **Frame Debugger** / platform GPU tools for GPU-bound cases (hand to technical-artist).
7. **Project Auditor** (Unity 6 built-in module) for static code/settings issues (allocating APIs, settings).
8. Record result in `.team/reports/perf-<area>.md`: device, build, scene, before/after ms, memory.

```csharp
static readonly ProfilerMarker s_Tick = new("Enemies.Tick");
void Update() { using (s_Tick.Auto()) { /* work */ } }

// Runtime HUD / automated perf check without the Profiler window
ProfilerRecorder _gc, _main;
void OnEnable() {
    _gc   = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame");
    _main = ProfilerRecorder.StartNew(ProfilerCategory.Internal, "Main Thread", 15);
}
void OnDisable() { _gc.Dispose(); _main.Dispose(); }
```

## GC & allocation rules
- Incremental GC is on by default (Player Settings → Use incremental GC); it spreads work but
  doesn't remove cost - target **0 B GC Alloc per frame** in gameplay.
| Allocates (hot path) | Use instead |
|---|---|
| LINQ, `foreach` over interfaces (`IEnumerable<T>`) | `for` over arrays/`List<T>`; concrete-type `foreach` |
| Lambdas capturing locals/`this` per call | cached delegates, static lambdas, method groups cached once |
| string concat / interpolation / `ToString()` each frame | update text only on change; `TMP_Text.SetText("{0}", v)`; ZString/StringBuilder |
| `GetComponent`/`Find*`/`GetComponentsInChildren()` per frame | cache in `Awake`; `GetComponentsInChildren(list)` overload |
| `Physics.RaycastAll`/`OverlapSphere` | `Physics.RaycastNonAlloc`/`OverlapSphereNonAlloc` with pooled arrays |
| boxing: struct → interface/object, `params object[]`, enum in non-generic APIs | generic constraints, custom `IEqualityComparer` for enum keys |
| `new List<T>()` per call | `ListPool<T>.Get()`/`Release` (UnityEngine.Pool), reuse fields |
| `Instantiate`/`Destroy` churn | `ObjectPool<T>` |
| coroutine `new WaitForSeconds()` each loop | cache the yield instruction, or `Awaitable` |
| `Debug.Log` in release | wrap in `[Conditional("DEVELOPMENT_BUILD")]` logger; strip |
| `Mesh.vertices`/`material` property getters | `GetVertices(list)`, `sharedMaterial`, `MaterialPropertyBlock` (non-SRP) |
- `tag == "x"` allocates → `CompareTag("x")`. `Camera.main` is cached since 2020.2 (cheap now).
- Many `Update()` methods: each MonoBehaviour message has native→managed overhead; for 1000+
  entities use a manager ticking plain C# objects, or Jobs/ECS.

## Jobs & Burst basics
```csharp
[BurstCompile]
struct MoveJob : IJobParallelFor {
    public NativeArray<float3> Positions;
    [ReadOnly] public NativeArray<float3> Velocities;
    public float Dt;
    public void Execute(int i) => Positions[i] += Velocities[i] * Dt;
}
// Update: schedule early, complete as late as possible (e.g. LateUpdate)
_handle = new MoveJob { Positions = _pos, Velocities = _vel, Dt = Time.deltaTime }.Schedule(_pos.Length, 64);
// LateUpdate: _handle.Complete(); then apply to transforms (or use IJobParallelForTransform)
// OnDestroy: _handle.Complete(); _pos.Dispose(); _vel.Dispose();
```
- Burst = HPC# only: blittable structs, `NativeArray`/`NativeList` (Collections), `Unity.Mathematics`;
  no managed objects, no `UnityEngine.Object`, no exceptions in hot code.
- Allocators: `Temp` (same frame), `TempJob` (≤ 4 frames), `Persistent` (dispose manually); leak
  detection: Jobs → Leak Detection → Full Stack Traces in Editor.
- Batch size 32-128 for cheap per-item work; `.Complete()` immediately after `Schedule` = no parallelism.
- Burst Inspector to check vectorization; Safety Checks on in Editor, off in release automatically.
- Worth it for: 1000+ items math (boids, projectiles, grids, pathfinding cost fields, mesh gen).
  Not for: a dozen objects (scheduling overhead dominates).

## Common fixes
| Symptom | Likely cause | Fix |
|---|---|---|
| Periodic spikes 5-50 ms | GC collections | remove per-frame allocs; pool; check GC Alloc column |
| Spike on spawn/first use | `Instantiate`, shader compile/warmup, asset load | pre-warm pools; `ShaderVariantCollection`/`GraphicsStateCollection` warmup; async load at loading screen |
| Hitch on scene load | sync `LoadScene`, `Awake` heavy work | `LoadSceneAsync` + `allowSceneActivation`; spread init over frames |
| High `Physics.Simulate` | many colliders/contacts, small fixed step | layer collision matrix, primitive colliders, fixed step 0.02-0.033, disable Auto Sync Transforms |
| High `Animator.Update` | many animators offscreen | Culling Mode = Cull Update Transforms/Completely; Generic rigs (Humanoid +30-50% CPU, Unity) |
| High `Canvas.SendWillRenderCanvases`/layout | UI rebuilds | split canvases, no layout groups on dynamic UI (stack-unity input-and-ui ref) |
| Render thread bound | too many draws/SetPass | GPU Resident Drawer/SRP Batcher/static batching; fewer materials (technical-artist) |
| GPU bound on mobile | overdraw, fill-rate, post FX, shadows | render scale/upscaler, cut transparent layers, shadow distance (technical-artist) |
| Memory grows per level | leaked handles/static refs/events | Memory Profiler diff; Addressables release (stack-unity addressables ref) |
| Thermal drop after 10 min | budget too close to 100% | target 65%; lower targetFrameRate in menus; Adaptive Performance |

## Checklist
- [ ] Budgets per tier written; measured on lowest device of the tier (dev build, not Editor).
- [ ] 0 B GC alloc per gameplay frame (Profiler or `ProfilerRecorder` assertion in a perf test).
- [ ] Before/after numbers from Profile Analyzer attached; median and p95/max frame time.
- [ ] Memory snapshot diff shows no growth across level reloads.
- [ ] Jobs completed and NativeContainers disposed in `OnDestroy`; no leak warnings.

## Sources
- Unity how-to: Best practices for profiling game performance https://unity.com/how-to/best-practices-for-profiling-game-performance
- Unity blog: Use all of Unity 6's profiling tools https://unity.com/blog/use-unity-6-profiling-tools-smart-efficient
- Unity e-book: Optimize your mobile game performance (Unity 6 ed.) tips https://unity.com/blog/games/optimize-your-mobile-game-performance-tips-on-profiling-memory-and-code-architecture-from
- Unity how-to: Mobile optimization part 2 (animation, batching, cameras) https://unity.com/how-to/mobile-game-optimization-tips-part-2
- Unity Manual: Project Auditor https://docs.unity3d.com/Manual/com.unity.project-auditor.html
- Scripting API: ProfilerRecorder https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerRecorder.html
- Burst manual https://docs.unity3d.com/Packages/com.unity.burst@latest
