---
name: unity-performance
description: Shared Unity performance knowledge - profiling tools, A/B measurement, perf budgets and CI gates, GC/memory, Burst/Jobs, IL2CPP, mobile thermals, Web threads.
---
# Unity performance (shared knowledge)
Mission: one measurement-led method for every role that changes or judges Unity performance;
roles link here instead of restating profiling, statistics or engine perf facts.

## Key concepts
- **Frame budget**: CPU Active Time and GPU Time each must stay below the target frame time
  (they run in parallel). Mobile works at ~65% of it (thermals; tier table in
  `studio:unity-developer` (performance)).
- **Bottleneck class first**: main thread, render thread (draw submission), workers/sync points,
  GPU, memory/GC, load/first use. A fix for the wrong class measures as noise.
- **Evidence ladder**: Editor = relative hints only; dev player = counters, markers, allocations;
  IL2CPP release player on target device = timing verdicts.
- **Noise**: every machine has a frame floor and run-to-run spread; a delta inside the spread is
  a tie. Incremental GC, thermals, background load and stale builds are the usual noise sources.
- **Cold vs warm**: first use (IL2CPP type init, shader/PSO compile, asset load, pool growth) is
  a separate row from steady state; report both.
- **Who does what**
| Concern | Owner |
|---|---|
| `.team/specs/architecture/perf-budget.md` (per platform/tier) | tech-lead-architect (+ technical-artist) |
| CPU, GC, memory, Jobs/Burst fixes; perf markers in code | unity-developer |
| GPU, shaders, overdraw, asset/texture budgets | technical-artist |
| Perf tests, A/B verdicts, regression reports | qa-engineer |
| CI perf/size gates, device farm, build machines | devops-sre-engineer |
| Release go/no-go on perf exit criteria | qa-lead |

## Rules that always apply
- Profile before changing code: name the cause (marker, thread, counter) and what was tried
  before reporting a regression or proposing a fix; no "probably GC".
- Every perf claim cites device, build type (dev/release, Mono/IL2CPP), scene/row, median and
  spread, and the budget row it is judged against; otherwise mark it "unmeasured".
- A/B verdicts follow the qa-engineer perf-verdict rule (fresh IL2CPP release builds of both
  sides, alternated in one session, median of 5+); counters come from a dev build.
- Judge a change against every row of the benchmark set, not only its target row; report every
  regressed row, including rows outside the batch.
- Never change what an existing benchmark row measures; harness changes go to all sides and are
  written down. New behavior = new row.
- One timing run per machine at a time; agents serialize timing runs with a lock
  (references/measurement-methodology.md); a loaded machine invalidates the run.
- "Zero GC" or "N ms" claims in docs/specs need an automated test that would fail (allocation
  test with a control allocation, budget test); otherwise drop the claim. Count allocations with
  `ProfilerRecorder`/`Profiler` APIs: `GC.GetAllocatedBytesForCurrentThread` reads 0 on Unity Mono.
- Accepted misses go to a perf backlog (measured vs target, suspected cause); never silently
  relax a budget - budget changes need tech-lead-architect sign-off.
- Engine facts stay in their homes: GC alloc fix table and Jobs basics in
  `studio:unity-developer` (performance); GPU levers in `studio:technical-artist`
  (rendering-performance); SRP Batcher/GPU Resident Drawer setup and build-size playbook in
  `studio:stack-unity` (rendering-and-pipelines, serialization-and-platforms).

## References (read on demand)
- references/profiling-tools.md — choosing and driving Profiler/Highlights, Profile Analyzer,
  Memory Profiler, Project Auditor, Frame Debugger, ProfilerMarker/Recorder/Counter, FrameTimingManager.
- references/measurement-methodology.md — any A/B comparison, benchmark harness, bisecting a
  perf regression, noisy or contradictory numbers, writing a perf report.
- references/budgets-and-ci-gates.md — writing perf-budget.md, Performance Testing package
  tests, allocation/budget tests, CI regression gates, baselines, build-size gates.
- references/memory-and-gc.md — managed heap and incremental GC behavior, memory growth/leaks,
  native vs managed memory, low-memory handling, mobile memory limits.
- references/burst-jobs-collections.md — Burst options and inspection, Collections containers,
  scheduling patterns, unsafe code review, threading thresholds, Web multithreading.
- references/platform-il2cpp-mobile-web.md — IL2CPP perf settings and costs, mobile thermals
  and frame pacing, Adaptive Performance, Web constraints, CPU-side render submission, texture uploads.

## Sources
- Unity Manual 6.3: Highlights Profiler module https://docs.unity.com/en-us/engine/6000.3/manual/analysis/profiler/visualizing-data/highlights
- Unity blog: Use all of Unity 6's profiling tools https://unity.com/blog/use-unity-6-profiling-tools-smart-efficient
- Unity how-to: Best practices for profiling game performance https://unity.com/how-to/best-practices-for-profiling-game-performance
