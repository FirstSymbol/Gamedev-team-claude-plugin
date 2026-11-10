# Measurement methodology: A/B runs, harness, bisect, reports
Goal: a perf verdict that another agent can reproduce on the same machine and get the same
answer. The short rule lives in the qa-engineer playbook (Quality bar: perf verdicts); this is
the full procedure. Which thread the frame waits on: `studio:unity-developer` (performance).

## What to measure in which build
| Measurement | Build | Why |
|---|---|---|
| Timing verdicts (ms, fps, load time) | IL2CPP, non-development, target device or fixed reference machine | Mono, dev builds and the Editor shift relative costs |
| Draw calls, batches, SetPass, GC alloc per frame | development build | many render counters are missing in release players |
| Allocation and budget tests in CI | Editor/dev player tests with `ProfilerRecorder` | deterministic counts, not timings |
| Resident memory | release player + OS tools | Editor and dev overhead inflate memory |
- A change can win on Mono and lose on IL2CPP (small threaded tasks, extra generic
  instantiations, type-init on first use): never ship a verdict measured on Mono only.
- Desktop harness: `QualitySettings.vSyncCount = 0` and `Application.targetFrameRate = -1`, or
  vsync hides every CPU change. Mobile: measure CPU/GPU ms (FrameTimingManager), not fps -
  `-1` means the platform default (30 fps on mobile).

## Know the machine before judging
- **Frame floor**: frame time of the harness with an empty row. Nothing measures below it.
- **Spread**: run an unchanged build 5+ times; record min/median/max per row. A delta inside
  that spread is a tie; a "win" must exceed it and repeat on a second alternated pass.
- **Machine state**: AC power, battery saver and game modes off, same thermal start (let
  phones cool to ambient; log `thermalState`/Adaptive Performance temperature level if
  available), no other heavy process. One timing run per machine at a time.
- **Agents sharing a machine**: serialize timing runs with an atomic lock directory.
```python
import os, time, socket, contextlib
@contextlib.contextmanager
def timing_lock(path, owner):              # path e.g. <tmp>/perf.lock
    while True:
        try: os.mkdir(path); break         # atomic: exactly one agent wins
        except FileExistsError: time.sleep(10)
    with open(os.path.join(path, "owner.txt"), "w") as f: f.write(f"{owner} {socket.gethostname()} {time.time()}")
    try: yield
    finally:
        os.remove(os.path.join(path, "owner.txt")); os.rmdir(path)
```
  Clear an orphan lock only after reading `owner.txt` and confirming that owner is gone.
- Builds and editors for other work run at Idle priority and never in parallel with a timing run.

## A/B protocol
1. Write the question: rows, expected direction, budget row it is judged against.
2. One detached worktree per side (`git worktree add --detach ../ab-A <commitA>`, same for B),
   each with its own clean project copy, so editing continues while the harness runs.
3. Delete old player and IL2CPP output folders before building each side; after the build,
   check the executable timestamp (flag or tag changes can silently reuse an old exe).
4. Build each side with the native-library version that belongs to that commit.
5. Run alternately A, B, A, B ... in one session, 5+ cold process starts per side; never
   compare against numbers from an earlier session, machine or build.
6. Settle each row before timing: `GC.Collect()` + ~10 idle frames, then warm-up frames, then
   the measured frames. Large scatter or non-monotonic results → suspect incremental GC
   landing inside rows; confirm with a diagnostic run with incremental GC off.
7. Per row report median of runs (each run = median of its frames), p95/max for spikes,
   min-max spread, and run count.
8. Verdict per row: win / loss / tie. Report every row, including rows the change did not
   target; a regressed row outside the batch is still a regression.
9. Surprise result? Before blaming the machine, rebuild an old known-green commit and
   re-measure; if a check counts work that the change moved elsewhere, update the check.

## Harness rules
- A row = fixed workload + fixed measurement. Never change what an existing row measures;
  add a new row and retire the old one with a note.
- Any harness change (idle frames, warm-up count, resolution, quality level) applies to every
  side and every engine compared, and is written into the report.
- Cold (first use) and warm (steady state) are separate rows; load/first-frame rows start a
  fresh process.
- Emit machine-readable results (CSV/JSON: build hash, backend, device, row, run, value, unit);
  the report is generated from them, never typed by hand.
- Timing source: harness clock (`Stopwatch`, `Time.realtimeSinceStartupAsDouble`) or
  `ProfilerRecorder` "Main Thread"/marker samples - keep the same source for both sides.

## Bisecting a perf regression
- Stabilize the measurement first; a bisect that jumps between unrelated commits is measuring
  noise (GC, thermals, stale builds), not code.
- `git bisect start <bad> <good>` + `git bisect run <script>`: the script builds fresh,
  runs the alternated protocol against a fixed reference build, exits 0 good / 1 bad /
  125 skip (unbuildable commit).
- After the culprit is found: profile it, name the cause, try fixes, then report with the
  fixes tried and their numbers. Never report "regressed, cause unknown" without a profile.

## Micro-optimizations
- Judge each one against all held benchmark rows; a local win that costs another row is a loss.
- Prefer small fixed headroom (capacity rounding, spare slots) over exact sizing that
  regrows on the next change.
- Burst vs managed results may differ in the last float bits; set tolerances in tests
  (references/burst-jobs-collections.md).

## Perf report (`.team/reports/perf-<area>.md`, ≤ 40 lines)
```
Question / budget row: <...>
Builds: A <hash>, B <hash>; backend IL2CPP release (counters: dev build <hash>)
Device/machine: <model, OS, power, thermal start>   Session: <date>, alternated, N=<runs>/side
Floor/spread: <ms> / <min-max per row>
| Row | A median | B median | delta % | p95 A/B | spread | verdict |
Profiled cause (losses): <marker/thread/counter + capture file name>
Fixes tried: <what, result>   Harness changes: <none | list, applied to all sides>
```

## Sources
- Unity how-to: Best practices for profiling game performance https://unity.com/how-to/best-practices-for-profiling-game-performance
- Profile Analyzer manual https://docs.unity3d.com/Packages/com.unity.performance.profile-analyzer@1.2/manual/index.html
- Unity Manual: Incremental garbage collection https://docs.unity3d.com/Manual/performance-incremental-garbage-collection.html
- Scripting API: GarbageCollector.incrementalTimeSliceNanoseconds https://docs.unity3d.com/ScriptReference/Scripting.GarbageCollector-incrementalTimeSliceNanoseconds.html
- Git: git-bisect https://git-scm.com/docs/git-bisect
- Git: git-worktree https://git-scm.com/docs/git-worktree
