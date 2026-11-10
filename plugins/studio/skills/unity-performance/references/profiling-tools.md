# Profiling tools (Unity 6): which tool answers which question
Step-by-step bound-thread diagnosis (Timeline wait markers) and the GC fix table live in
`studio:unity-developer` (performance); GPU counters and platform GPU tools live in
`studio:technical-artist` (rendering-performance). This file = tool choice, setup, gotchas.

## Tool picker
| Question | Tool | Notes |
|---|---|---|
| Over budget? CPU- or GPU-bound? | Profiler **Highlights** module (Unity 6) | off by default; set target frame time; red = CPU over, yellow = GPU over |
| Which thread / marker costs the time | CPU Usage module: Timeline, then Hierarchy (Self ms, GC Alloc) | Timeline for waits/threads, Hierarchy for totals |
| Did my change help, over many frames | **Profile Analyzer** package | Compare view, median + upper quartile; same frame range both sides |
| What holds memory, what leaked | **Memory Profiler** package 1.1.x | snapshot compare; Summary/Unity Objects/All Of Memory |
| Static issues: allocating APIs, settings, assets, build size | **Project Auditor** | package 1.0 on 6.1, 1.1 up to 6.3, built into the Editor from 6.4 |
| Why a batch broke, pass order | Frame Debugger | → technical-artist |
| Numbers in players, tests, HUD, CI | `ProfilerRecorder`, `FrameTimingManager` | below |
| Burst codegen / vectorization | Burst Inspector | references/burst-jobs-collections.md |
| OS-level memory, thermals, CPU frequency | Xcode Instruments, Android Studio profiler, `adb shell dumpsys meminfo <pkg>`, Perfetto | resident memory as the OS sees it |

## Profiler setup and gotchas
- Target: Development Build + Autoconnect Profiler (or attach by IP / USB). Editor play mode
  numbers include Editor overhead: use them only for relative checks, and prefer the
  Standalone Profiler process when profiling the Editor itself.
- Deep Profiling instruments every C# call: use it only to find callers, never for timings.
  For allocations, enable Call Stacks for `GC.Alloc` samples instead (dev build).
- Profiler attached = extra CPU, memory and network; confirm final timings with no profiler
  connected (ProfilerRecorder or the harness's own clock).
- Headless capture (players): `-profiler-enable -profiler-log-file <path>.raw
  -profiler-capture-frame-count <N>`; profiler memory defaults 16 MB player / 256 MB Editor,
  raise with `-profiler-maxusedmemory <bytes>`. Load the `.raw` in the Profiler window.
- Keep captures (`.data`/`.raw`, snapshots) outside the repo; cite file name, device and build
  hash in the report.
- Highlights: CPU Active Time = longest of main/render thread minus waits; GPU Time = first
  command to completion. Both must stay below target (CPU and GPU run in parallel).

## Markers in code
```csharp
using Unity.Profiling;
static readonly ProfilerMarker s_Layout = new(ProfilerCategory.Scripts, "Text.Layout");
static readonly ProfilerMarker<int> s_Build = new("Mesh.Build", "Vertices"); // metadata; com.unity.profiling.core
void Rebuild(int n) {
    using (s_Layout.Auto()) { /* layout */ }
    s_Build.Begin(n); /* build */ s_Build.End();
}
```
- One marker per meaningful stage (layout, mesh build, upload), named `Area.Stage`; markers are
  the rows that Profile Analyzer, Performance Testing (`Measure.ProfilerMarkers`) and
  ProfilerRecorder read - name them once and keep names stable (renaming breaks baselines).
- `ProfilerCounter`/`ProfilerCounterValue` (com.unity.profiling.core) show custom values in the
  Profiler; they are compiled out of non-development builds.

## ProfilerRecorder (players, tests, runtime HUD)
```csharp
// List what this build exposes (run once in a dev and a release player)
var handles = new List<ProfilerRecorderHandle>();
ProfilerRecorderHandle.GetAvailable(handles);
foreach (var h in handles) {
    var d = ProfilerRecorderHandle.GetDescription(h);
    Debug.Log($"{d.Category.Name}/{d.Name} {d.UnitType}");
}
// Average of the last N samples
static double Avg(ProfilerRecorder r) {
    int n = r.Count; if (n == 0) return 0;
    Span<ProfilerRecorderSample> s = stackalloc ProfilerRecorderSample[n];
    r.CopyTo(s); double sum = 0; foreach (var x in s) sum += x.Value; return sum / n;
}
```
- Works in release players, but not every counter does: the Profiler counters reference has an
  "available in release players" column; check with `GetAvailable` on the actual build.
- Render counters (draw calls, batches, SetPass) → read from a dev build; timing → release build.
- `LastValue` = value at the end of the previous frame; `CurrentValue` = now. Dispose every
  recorder (`OnDisable`/test teardown) - it holds native memory.
- Allocation reading: "GC Allocated In Frame" (Memory category); always prove the probe works
  with a control allocation first (qa-engineer playbook, Risks).
- Useful memory counters: "System Used Memory", "Total Used Memory", "GC Reserved Memory",
  "GC Used Memory", "Texture Memory", "Mesh Memory" (verify names per version via `GetAvailable`).

## FrameTimingManager
- Always on in development players; in release enable Player Settings → Other Settings →
  Rendering → Frame Timing Stats (OpenGL also needs its Profiler GPU setting; verify name per version).
  Attaching a ProfilerRecorder to its counters enables it automatically.
- Per frame: `FrameTimingManager.CaptureFrameTimings()`, then `GetLatestTimings(n, array)`;
  fields include CPU frame, main/render thread, present wait and GPU frame times
  (verify exact field names per version).
- No GPU time on WebGL and on Linux with OpenGL; GPU timing has overhead on some APIs (why it
  is off by default in release). The Adaptive Performance Basic provider builds on it.

## Profile Analyzer
- Pull frames from the Profiler window or load `.data`; select the same steady-state range on
  both sides (skip loading and warm-up frames); filter by thread (Main, Render, Job workers).
- Compare view: sort by absolute median delta; read the distribution, not only the mean;
  a marker whose count changed is a behavior change, not a speed-up.
- Export CSV into the perf report appendix; at least 300 frames per side.

## Memory Profiler
- Snapshot at fixed states: main menu (baseline) → level loaded → level unloaded + GC → menu.
  Compare snapshots; growth after unload = leak (static refs, events, un-released handles).
- Summary splits Allocated vs Resident; categories Managed, Native, Graphics, Untracked.
  Untracked = allocations Unity cannot attribute (native plugins, OS); confirm with platform tools.
- Unity Objects view, group by type: duplicates of the same texture/mesh name+size = asset
  duplicated in bundles or Read/Write copies (`studio:stack-unity` addressables-and-assets).
- Capturing allocates and stalls: never time anything during a snapshot.

## Project Auditor
- Code analysis flags allocating calls, boxing, LINQ and costly APIs, and marks issues in
  hot paths (`Update`-family callers); Settings flags Mono backend, incremental GC off, etc.;
  Assets flags Read/Write textures, uncompressed audio, shader variants; Build Report view for size.
- Use as a review checklist and a non-blocking CI report; triage its list, don't bulk-"fix" it.

## Sources
- Unity Manual 6.3: Highlights Profiler module https://docs.unity.com/en-us/engine/6000.3/manual/analysis/profiler/visualizing-data/highlights
- Unity Manual 6.3: Profiler command-line arguments https://docs.unity3d.com/Manual/profiler-command-line-arguments.html
- Unity Manual: Profiler counters reference https://docs.unity3d.com/Manual/profiler-counters-reference.html
- Scripting API: ProfilerRecorder https://docs.unity.com/en-us/engine/current/script-reference/unity/profiling/profilerrecorder
- Unity Manual: Enable FrameTimingManager https://docs.unity3d.com/Manual/frame-timing-manager-enable.html
- Scripting API 6.3: FrameTimingManager https://docs.unity.com/en-us/engine/6000.3/script-reference/unityengine/frametimingmanager.md
- Profiling Core: ProfilerCounter guide https://docs.unity.cn/Packages/com.unity.profiling.core@1.0/manual/profilercounter-guide.html
- Project Auditor 1.1 introduction https://docs.unity3d.com/Packages/com.unity.project-auditor@1.1/manual/project-auditor-introduction.html
- Memory Profiler 1.1 manual https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/index.html
- Unity blog: Use all of Unity 6's profiling tools https://unity.com/blog/use-unity-6-profiling-tools-smart-efficient
