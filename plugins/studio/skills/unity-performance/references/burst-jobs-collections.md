# Burst, Jobs and Collections beyond the basics
Basics (IJobParallelFor example, allocator lifetimes, when Burst is worth it): `studio:unity-developer`
(performance). Threshold switch + main-thread fallback and generation counters for stale results
are unity-developer playbook Risks. Packages in Unity 6 projects: Burst 1.8.x, Collections 2.x,
Mathematics 1.3.x (verify the versions the project pins in `Packages/manifest.json`).

## BurstCompile options
| Option | Values | Use |
|---|---|---|
| `FloatMode` | Default (= Strict), Strict, Fast, Deterministic | Fast for math kernels that tolerate reordering/FMA; Deterministic (64-bit only) for lockstep/replays |
| `FloatPrecision` | Standard (= Medium, 3.5 ulp), High (1 ulp), Low (350 ulp for sin/cos/exp/log/pow) | Low only for visuals |
| `OptimizeFor` | Default, Performance, Size, FastCompilation, Balanced (verify list) | Size for cold code on mobile |
| `CompileSynchronously` | true/false (JIT in Editor only) | benchmarks/tests in Editor; otherwise first frames run managed code |
| `DisableSafetyChecks` | true/false | never in debugging sessions |
- `[BurstCompile]` works on job structs, on static methods (inside a class/struct marked
  `[BurstCompile]`), and on assemblies; a Burst entry point also compiles the methods it calls.
- Burst static methods can be called directly from managed code; keep parameters blittable,
  pass structs by `ref`/`in`/pointer and return results via `out` (verify signature limits per Burst version).
- Editor gotcha: Burst compiles asynchronously; until it finishes, jobs run as Mono. Editor
  timings of the first seconds measure Mono. Players use AOT Burst code from frame 1.

## Codegen inspection and hints
- Burst Inspector (Jobs → Burst → Open Inspector): look for packed SIMD instructions in hot
  loops; a scalar loop usually means aliasing, a branch, a managed call or a non-contiguous access.
- Job structs carry implicit `[NoAlias]` (Burst 1.8); explicit `[NoAlias]` is rarely needed and
  Burst advises against it in user code.
- `Unity.Burst.CompilerServices.Hint.Likely/Unlikely/Assume` for hot branches;
  `Loop.ExpectVectorized()` turns a missed vectorization into a compile error (may need an
  experimental define; verify per version).
- Prefer `Unity.Mathematics` types (`float4`, `math.*`) and SoA layouts (`NativeArray<float>`
  per component) for vectorization; avoid `NativeArray<SomeClassLikeStruct>` with many fields
  when the loop touches two.

## Collections 2.x picker
| Need | Container | Note |
|---|---|---|
| Fixed-size data passed to jobs | `NativeArray<T>` | `NativeArrayOptions.UninitializedMemory` when you overwrite every element |
| Growable list | `NativeList<T>` | `AsParallelWriter()` needs capacity reserved up front |
| Hash map, single writer | `NativeHashMap<K,V>` | Collections 2.x fast map |
| Hash map, parallel writers | `NativeParallelHashMap<K,V>` / `NativeParallelMultiHashMap` | `ParallelWriter`; capacity reserved up front |
| Queue / per-thread streams | `NativeQueue<T>`, `NativeStream` | stream for variable output per index |
| Small inline buffers, no allocation | `FixedList32Bytes<T>`..`FixedList4096Bytes<T>`, `FixedString*Bytes` | live inside structs/stack |
| Nested containers, no safety handle | `UnsafeList<T>`, `UnsafeHashMap` | you own lifetime and bounds |
- Allocators: `Temp` - allocate and free inside one frame or inside a job, never pass a
  main-thread Temp container into a job; `TempJob` - pass to jobs, dispose within 4 frames;
  `Persistent` - long-lived, dispose explicitly. Custom allocators via `AllocatorManager`.
- Containers allocated with `Temp` on one thread share one safety handle: odd safety errors in
  Temp hash maps are expected; move to `TempJob` if they block you.

## Scheduling patterns
- One scheduled batch for all dirty items per frame, not one `.Run()`/`Complete()` per object:
  per-object synchronous jobs pay scheduling + sync cost N times and use one core.
- Schedule early (Update), `JobHandle.ScheduleBatchedJobs()` to start workers, complete as late
  as possible (LateUpdate/before render) and in exactly one place.
- `IJobFor.ScheduleParallel(count, innerloopBatchCount, dep)`: batch 32-128 for cheap items,
  1-8 for heavy ones; measure.
- Transforms: `IJobParallelForTransform` + `TransformAccessArray` instead of copying positions.
- Worker count: `JobsUtility.JobWorkerCount`; on 2 cores or fewer, Web without threads, and in
  edit mode, run the main-thread path (unity-developer threshold rule).
- Read Unity objects on the main thread into blittable snapshots before scheduling (stack-unity
  main-thread rule); jobs never touch `UnityEngine.Object`.
- Results from a job scheduled for an older state must be dropped (generation counter).

## Unsafe code on hot paths (review checklist)
- [ ] An ADR records why unsafe/Burst is needed and which tests guard it (alloc + budget tests).
- [ ] Every pointer has one owner and a documented lifetime; freed in `Dispose`, nulled after.
- [ ] Bounds checks in Editor/dev via `[Conditional("ENABLE_UNITY_COLLECTIONS_CHECKS")]` helpers;
  release players have no safety checks - out-of-range writes corrupt memory silently.
- [ ] `[NativeDisableUnsafePtrRestriction]` / `[NativeDisableParallelForRestriction]` only with a
  comment proving no two workers write the same index.
- [ ] `UnsafeUtility.MemCpy`/`MemClear` sizes computed from `UnsafeUtility.SizeOf<T>()`, never literals.
- [ ] Tests run with Burst safety checks on and leak detection Full Stack Traces in the Editor.
- Code review owner: code-reviewer (opus) for every unsafe diff.

## Web multithreading
- Only Burst-compiled jobs run on worker threads on Web; non-Burst C# jobs run on the main
  thread (GC limitation). All jobs are scheduled from the main thread.
- Requires Player Settings "Enable Native C/C++ Multithreading" (covers native and Burst),
  Unity 6.4+ and Burst 1.8.26+ (verify for your version); off → every job runs on the main thread.
- Threads need cross-origin isolation (COOP/COEP headers) for SharedArrayBuffer on the host page
  (verify hosting requirements in the Web multithreading docs); keep the single-thread,
  time-sliced fallback for hosts without it.

## Determinism and tests
- Burst vs Mono/IL2CPP float results may differ in the last bits (FMA, reordering): compare with
  a tolerance (ulps or epsilon), not exact equality; use Deterministic mode only where required.
- Compile Burst synchronously in perf tests (`CompileSynchronously = true` or
  Jobs → Burst → Synchronous Compilation) so the Editor does not measure Mono.

## Sources
- Burst 1.8 manual: BurstCompile attribute https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile.html
- Burst 1.8 API: FloatMode https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FloatMode.html
- Burst 1.8 changelog (implicit NoAlias on jobs) https://docs.unity3d.com/Packages/com.unity.burst@1.8/changelog/CHANGELOG.html
- Unity Manual 6.6: Burst optimization hints https://docs.unity3d.com/Manual/burst/optimization-hint.html
- Burst 1.6: Optimization guidelines (aliasing, Loop.ExpectVectorized) https://docs.unity3d.com/Packages/com.unity.burst@1.6/manual/docs/OptimizationGuidelines.html
- Collections 2.3: Allocator overview https://docs.unity3d.com/Packages/com.unity.collections@2.3/manual/allocator-overview.html
- Collections 2.2: Known issues (shared Temp safety handle) https://docs.unity3d.com/Packages/com.unity.collections@2.2/manual/issues.html
- Unity Manual 6.5: Multithreading with Burst in Unity Web https://docs.unity.com/en-us/engine/6000.5/manual/platform-specific/webgl/develop/web-multithreading/burst
