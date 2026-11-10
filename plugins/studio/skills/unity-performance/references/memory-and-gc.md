# Memory and GC: managed heap, incremental GC, native memory, low memory
Per-frame allocation fixes (LINQ, closures, boxing, pools): `studio:unity-developer`
(performance). Asset loading/unloading and Addressables release: `studio:stack-unity`
(addressables-and-assets). Snapshot workflow: references/profiling-tools.md.

## Managed heap model (Mono and IL2CPP)
- Boehm-Demers-Weiser collector: mark-and-sweep, non-generational, non-compacting. Freed gaps
  can only take objects of equal or smaller size → fragmentation; a large allocation may grow
  the heap even when total free space is enough.
- Allocation that does not fit → GC runs → still no contiguous block → heap expands (on most
  platforms each expansion doubles the previous one; oversized requests get an out-of-cycle
  expansion).
- Unity keeps the expanded heap. Empty full pages (4 KB desktop, often 16 KB mobile) are
  returned to the OS "eventually" at an unreliable interval: never plan memory on it.
- Cost of a collection grows with live managed objects and references (mark phase), not with
  garbage amount: big long-lived object graphs make every GC slower.
- 1 KB/frame at 60 fps = 3.6 MB/min of garbage → periodic GC spikes. Target 0 B per gameplay
  frame after warm-up.
- The GC does not free native memory (textures, meshes, NativeContainers, AssetBundles).

## Incremental GC
- Default on (Player Settings → Other Settings → Configuration → Use Incremental GC). It
  splits the mark phase into slices across frames; it does not reduce total work.
- Slice: `GarbageCollector.incrementalTimeSliceNanoseconds`, default 3 ms; a guideline, not a
  hard cap (timer may have 1 ms resolution). Keep it well below the frame budget.
- Write barriers on reference writes cost CPU: up to ~1 ms/frame in CPU-bound projects (Unity
  docs). Profile critical sections with incremental on and off; compare in Profile Analyzer.
- Measurement side effect: a collection can land inside any benchmark row → scatter and
  misleading bisects (references/measurement-methodology.md, settle rows with a collection).
- `GarbageCollector.CollectIncremental(ns)` runs slices within a total budget, e.g. in a frame
  with spare time (`WaitForTargetFPS` idle) or at a loading screen.

## GC modes (`GarbageCollector.GCMode`)
| Mode | Behavior | Use |
|---|---|---|
| Enabled | automatic (incremental if enabled) | default |
| Manual | no automatic collections; `GC.Collect()` (full, blocking) and `CollectIncremental` still work | collect at safe points (loading, menus, between rounds) |
| Disabled | no collections at all; `GC.Collect()` has no effect; heap only grows | short critical sections with all memory pre-allocated and 0 B/frame proven |
- Manual/Disabled with any steady allocation = unbounded heap → OS kills the app. Gate it with
  an allocation test and a memory counter alarm (`GC Reserved Memory`).

## Native and graphics memory
| Source | Trap | Rule |
|---|---|---|
| Texture/Mesh Read/Write Enabled | CPU copy kept in addition to the GPU copy (2x) | off unless scripts read pixels/vertices (technical-artist audit) |
| Same asset in several bundles / Resources + Addressables | duplicate copies loaded | Addressables analyze; Memory Profiler Unity Objects duplicates |
| Large data held as managed array + native copy | 2x resident | never hold large assets twice; let native code open them by path or read in place |
| `NativeArray`/`UnsafeList` Persistent | leaks are invisible to GC | dispose in `OnDestroy`/`Dispose`; leak detection on in Editor |
| AssetBundles / Addressables handles | not released → assets stay | release per load call; verify with snapshot after unload |
| Atlases/caches that only grow | thrash or OOM when full | cap + LRU or second page; never reset-all on full (every client rebuilds) |
| Fonts/glyph atlases, audio decompressed on load | big hidden native blocks | streaming/compressed-in-memory audio; dynamic atlases with caps |
- `Resources.UnloadUnusedAssets()` and `GC.Collect()` are CPU-heavy (seconds in big projects):
  only at loading screens.

## Object layout and buffers
- Keep hot per-object classes under ~2 KB: larger objects took a slower large-object path
  under IL2CPP in a measured project (verify per Unity version). Move rare fields to an
  on-demand side object, create lists lazily, guard size with a test (sum field sizes via
  reflection in EditMode as a lower bound).
- Shared scratch buffers: create lazily, size to the visible window plus margin, grow with
  fixed headroom; release after a quiet period and on low memory; test the first draw/edit
  right after a release (re-creation path bugs).
- Structs for hot data (no per-instance header, no GC tracing); arrays of structs over
  lists of small classes for 1000+ items; `NativeArray` for data consumed by jobs.

## Low memory and platform limits
- `Application.lowMemory` (iOS, Android): drop caches, scratch buffers, pooled spares, then
  `Resources.UnloadUnusedAssets()` if safe. Subscribe in play mode only; it fires late -
  stay under budget rather than relying on it.
- iOS: no published per-app limit; query `os_proc_available_memory()` on device; jetsam kills
  without a managed exception. Android: low-memory killer by priority; test on the 2-3 GB tier.
  Tier numbers: `studio:unity-developer` (performance).
- Web: wasm heap (Maximum Memory Size, growth settings) and browser tab limits - mobile Safari
  is the tightest; GC runs only between frames on Web (see `studio:stack-unity`
  serialization-and-platforms for Web build settings) (verify current GC/Web behavior in docs).
- uGUI: keep each Graphic's mesh below 65,000 vertices (unity-developer hard rule; above it
  canvas batching exhausted system memory).

## Memory checks per release
- [ ] Snapshot diff menu → level → menu shows no growth beyond tolerance (Memory Profiler).
- [ ] Peak resident memory on the lowest device of each tier ≤ perf-budget.md.
- [ ] No Read/Write textures/meshes except listed exceptions (Project Auditor / TA audit).
- [ ] `GC Reserved Memory` stable over a 20-30 min soak (no stair-step growth).
- [ ] Low-memory path exercised in a test (simulate the event, then render/edit).

## Sources
- Unity Manual: Managed memory introduction https://docs.unity.com/en-us/engine/6000.6/manual/analysis/performance-memory/managed-memory/introduction
- Unity Manual: Garbage collector overview https://docs.unity.com/en-us/engine/current/manual/analysis/performance-memory/managed-memory/garbage-collector
- Unity Manual: Configuring garbage collection (GC modes) https://docs.unity.com/en-us/engine/6000.6/manual/analysis/performance-memory/managed-memory/disabling-garbage-collection
- Scripting API: GarbageCollector.incrementalTimeSliceNanoseconds https://docs.unity3d.com/ScriptReference/Scripting.GarbageCollector-incrementalTimeSliceNanoseconds.html
- Scripting API: GarbageCollector https://docs.unity3d.com/ScriptReference/Scripting.GarbageCollector.html
- Memory Profiler 1.1 manual https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/index.html
- Unity e-book tips: Optimize your mobile game performance (profiling, memory) https://unity.com/blog/games/optimize-your-mobile-game-performance-tips-on-profiling-memory-and-code-architecture-from
