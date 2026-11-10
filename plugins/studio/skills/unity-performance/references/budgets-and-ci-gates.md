# Perf budgets, perf tests and CI regression gates
Device-tier numbers (frame, draws, tris, memory): `studio:unity-developer` (performance).
Art budgets: `studio:technical-artist` (asset-pipeline-budgets). Basic UTF batch runs and a
`Measure.Frames` example: `studio:qa-engineer` (automation-unity). CI wiring: devops-sre-engineer.

## perf-budget.md (`.team/specs/architecture/`, owner tech-lead-architect)
```
| Platform/tier (lowest device) | Target fps | CPU main ms | Render thread ms | GPU ms |
| GC alloc/frame (gameplay) | Peak resident MB | Cold start s | Scene load s |
| Sustained fps after 20 min | Download/install size MB | Draws/SetPass (from TA budget) |
Per-feature rows: <feature> | <row/marker> | <budget> | <test that guards it>
Measurement rules: build type, device, scene, how measured (link a perf test or harness row).
```
- Every budget row names the test or harness row that guards it; a row with no guard is a wish.
- Accepted misses → `.team/specs/plan/perf-backlog.md`: ID | what | measured | target | suspected
  cause | owner. Relaxing a budget = tech-lead-architect decision (ADR if it changes a promise).
- Docs/marketing claims ("zero GC", "N ms") must point to a guarding test.

## Performance Testing package (com.unity.test-framework.performance, 3.x)
```csharp
using NUnit.Framework; using Unity.PerformanceTesting; using UnityEngine.TestTools;

[Test, Performance]                       // EditMode or PlayMode, synchronous code
public void Layout_1000Glyphs() {
    Measure.Method(() => _layout.Run(_text))
        .WarmupCount(5).MeasurementCount(20).IterationsPerMeasurement(10)
        .SampleGroup(new SampleGroup("Layout", SampleUnit.Microsecond))
        .Run();
}

[UnityTest, Performance]                  // PlayMode, frames + named markers
public IEnumerator Scroll_Frames() {
    yield return LoadBenchScene();
    yield return Measure.Frames().WarmupCount(30).MeasurementCount(300)
        .ProfilerMarkers(new SampleGroup("Text.Layout"), new SampleGroup("Mesh.Build"))
        .Run();
}

[Test, Performance]
public void Parse_Scope() {
    using (Measure.Scope("Parse")) { _parser.Parse(_doc); }   // one sample per scope
}
```
- `Measure.Custom(sampleGroup, value)` records any number (bytes, counts, ms from FrameTimingManager).
- Results JSON: `-perfTestResults <path>.json` on the batch command line (package 3.2+);
  without it the file goes to `Application.persistentDataPath`.
- Marker names must match `ProfilerMarker` names exactly; keep them stable (baselines key on them).
- Known issue: `Measure.ProfilerMarkers` reported 0 for some C# job markers (issue BUTFP-24,
  3.0.3) - for jobs, time the schedule-to-complete span with a main-thread marker (verify fixed in your version).
- Editor PlayMode timings are smoke signals only; timing gates run in IL2CPP players on a fixed
  device (`-testPlatform <BuildTarget>` player tests; see qa-engineer automation-unity).

## Allocation tests (deterministic, run on every PR)
```csharp
using Is = UnityEngine.TestTools.Constraints.Is;   // Unity overlay over NUnit Is

[Test] public void Rebuild_DoesNotAllocate() {
    _shape.Rebuild();                                  // warm-up: first call may init statics/caches
    Assert.That(() => { _shape.MarkDirty(); _shape.Rebuild(); }, Is.Not.AllocatingGCMemory());
}

static object s_Sink;                                  // keeps the control allocation alive
[UnityTest] public IEnumerator Frame_AllocatesNothing_AfterWarmUp() {
    using var rec = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame");
    s_Sink = new byte[4096]; yield return null;        // control: prove the probe sees allocations
    Assert.That(rec.LastValue, NUnit.Framework.Is.GreaterThanOrEqualTo(4096), "probe blind: test invalid");
    yield return null;                                 // warm-up frame
    long quietest = long.MaxValue;
    for (int i = 0; i < 5; i++) { _view.Tick(); yield return null; quietest = Math.Min(quietest, rec.LastValue); }
    Assert.That(quietest, NUnit.Framework.Is.EqualTo(0));   // quietest window: Editor noise excluded
}
```
- `Is.Not.AllocatingGCMemory()` checks the main-thread delegate only; frame-level tests catch
  allocations from callbacks, coroutines and Unity internals.
- `GC.GetAllocatedBytesForCurrentThread` reads 0 on Unity Mono: never use it as the probe.
- Also guard object size for hot per-object classes (references/memory-and-gc.md, IL2CPP 2 KB).

## Timing budget tests (noisy - design for it)
- Prefer ratios inside one process (feature row / reference row measured in the same run) over
  absolute ms; absolute thresholds only on a dedicated, idle reference device.
- Threshold ≥ the measured spread of that device; qa-lead sets the % (default ±10% vs baseline,
  qa-engineer automation-unity). Fail = rerun once alternated with the baseline build; still
  red → bug with both result files.
- Load-sensitive tests never run on a shared agent machine with other jobs (mark them
  `[Category("PerfTiming")]` and filter them out of PR runs).

## CI gate ladder
| Gate | When | Blocks | Owner |
|---|---|---|---|
| Compile + allocation tests + object-size tests | every PR (batch mode) | merge | unity-developer writes, qa-engineer reviews |
| Project Auditor report diff | every PR | no (review input) | code-reviewer reads |
| Build size vs fixed lab project | PR or nightly | merge above agreed delta | devops-sre-engineer |
| Perf tests on reference device(s), IL2CPP release | nightly | release (opens bug, not PR block) | qa-engineer |
| Soak: 20-30 min on lowest tier, fps + temperature + memory | weekly / pre-release | release gate | qa-lead |
- Baselines per device x Unity version x backend x quality level; stored as committed JSON with a
  reason line; update a baseline only through a reviewed change, never automatically on red.
- Unity Performance Benchmark Reporter turns baseline + result files into an HTML regression
  report (XML input by default; JSON needs its format option - verify syntax).
- Keep raw results as CI artifacts for 30+ days so a later bisect has history.

## Build size gate
- Measure only shipped files: exclude `<Product>_BackUpThisFolder_ButDontShipItWithYourGame`
  (IL2CPP sources), `<Product>_BurstDebugInformation_DoNotShip`, `.pdb`/symbols.
- Compare against a fixed lab: same empty project already using the same base packages
  (e.g. uGUI), same settings, IL2CPP release; report the delta, not the total.
- Each player carries only its platform/CPU natives (devops-sre-engineer playbook); heavy
  packages and generic instantiations add IL2CPP code (references/platform-il2cpp-mobile-web.md).
- Size playbook (offenders, stripping, variants): `studio:stack-unity` (serialization-and-platforms).

## Sources
- Performance Testing package 3.1: command-line arguments https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.1/manual/cmd-line-args.html
- Performance Testing package 3.3: Measure.Frames https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.3/manual/measure-frames.html
- Performance Testing package 3.2: Measure.ProfilerMarkers https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.2/manual/measure-profile-markers.html
- Unity issue: ProfilerMarkers no timing for C# jobs https://issuetracker-mig.prd.it.unity3d.com/issues/cant-obtain-timing-data-of-c-number-job-using-profilermarkers-function
- Test Framework 2.0: AllocatingGCMemoryConstraint https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Constraints.AllocatingGCMemoryConstraint.html
- Unity Performance Benchmark Reporter wiki https://github.com/Unity-Technologies/PerformanceBenchmarkReporter/wiki/How-to-Use-the-Unity-Performance-Benchmark-Reporter
