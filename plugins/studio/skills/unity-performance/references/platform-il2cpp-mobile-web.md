# Platform perf: IL2CPP, mobile thermals and pacing, Web, render submission, uploads
IL2CPP/AOT correctness, stripping and the build-size playbook: `studio:stack-unity`
(serialization-and-platforms). Pipeline setup (SRP Batcher, GPU Resident Drawer): `studio:stack-unity`
(rendering-and-pipelines). GPU levers: `studio:technical-artist` (rendering-performance).

## IL2CPP performance settings
| Setting | Options | Guidance |
|---|---|---|
| C++ Compiler Configuration | Debug / Release / Master | Master enables all optimizations (link-time codegen on MSVC); much longer builds; Unity recommends it for shipping when build time allows. Time verdicts on the configuration you ship |
| LTO mode (6.5+ Android, 6.6 dropdown) | Thin / Full | Thin: faster builds, fewer optimizations; Unity reported -5.7% time-to-full-display with heavy generics at +30-35% build time (Android, 6.5 forum post) - measure your project |
| IL2CPP Code Generation | runtime speed vs code size/build time (names differ by version) | size option uses full generic sharing: smaller code, faster builds, slower shared-generic calls (one forum case ~12x on `GetHashCode`) |
| Script Debugging, Development Build | on/off | both change codegen: never time them |
- `[Il2CppSetOption(Option.NullChecks / ArrayBoundsChecks, false)]` on a proven-hot, fully
  tested method or type removes checks (most local scope wins); a bug becomes memory
  corruption instead of an exception. Divide-by-zero checks are off by default. The attribute
  source ships with the Editor's il2cpp data and must be copied into the project (verify path).
- Devirtualization: IL2CPP is conservative; calls on `sealed` classes/methods become direct
  calls. Seal hot classes and avoid interface dispatch in inner loops (generics with struct
  constraints or concrete types). Gains are small per call - worth it only in measured hot code.
- Each generic instantiation over a value type is separate C++ code: keep heavy packages
  (Mathematics, Collections) out of a runtime core that does not need them and share one
  generic container type instead of many `List<StructX>` variants.
- First use is expensive (type/metadata init, static constructors, generic dictionaries):
  warm up behind a loading screen (unity-developer playbook Risks); measure cold rows separately.
- Small work items gain nothing from threads under IL2CPP: thread only above a measured size.
- Native plugins: link with hidden visibility, an exported-symbol version script and dead-code
  GC (`-fvisibility=hidden`, version script, `--gc-sections`) - devops-sre-engineer owns the toolchain.

## Mobile: thermals, sustained performance, pacing
- Work at ~65% of the frame budget and soak-test 20-30 min on the lowest device per tier;
  record fps, CPU/GPU ms and thermal level over time, not the first-minute number.
- Adaptive Performance (core package `com.unity.adaptiveperformance` 5.1 on Unity 6; settings in
  Project Settings → Adaptive Performance; installing a provider adds it there):
  - Providers: Android (`com.unity.adaptiveperformance.google.android`, Android thermal headroom
    via ADPF; polls headroom every 12 s, 1 s on Android 15, since 5.1.5; disabled on devices
    reporting bad headroom), Basic provider (any platform, from FrameTimingManager); vendor
    providers per docs (verify current list).
  - Read `ThermalStatus.ThermalMetrics` (warning level, temperature level/trend) and
    `PerformanceStatus` (bottleneck: CPU/GPU/target fps); start with built-in scalers
    (resolution, LOD, shadows, frame rate) and tune per game; simulate in Device Simulator.
- iOS: read `ProcessInfo.thermalState` through a small native plugin if Adaptive Performance has
  no iOS provider in your version (verify); drop quality at `serious`, not only at `critical`.
- Frame pacing: Android Optimized Frame Pacing (Swappy) clamps the target rate down to a divisor
  of the display refresh rate - set `targetFrameRate` to 30/60/90/120 to match; check 90/120 Hz
  devices separately. Uneven pacing reads as stutter even at a good average fps.
- Menus/idle screens: lower `targetFrameRate` or use `OnDemandRendering.renderFrameInterval`
  (render every Nth frame while scripts and input still tick) to save battery and heat.
- Resolution: URP render scale / dynamic resolution / STP upscaler per tier (technical-artist).

## Web
- Main thread only unless Web multithreading is configured (Burst jobs only;
  references/burst-jobs-collections.md); long work must be time-sliced (~2 ms/frame,
  unity-developer threshold rule).
- FrameTimingManager gives no GPU time on Web: use browser DevTools Performance panel / GPU
  timing extensions for GPU questions; Unity Profiler connects to Web dev builds (verify setup).
- Background tabs are throttled: benchmarks run in a focused foreground tab with a fixed window size.
- Memory: wasm heap settings and browser tab limits (references/memory-and-gc.md); mobile
  Safari is the tightest target.

## CPU-side render submission (routing table)
| Symptom (Profiler) | First lever | Owner / home |
|---|---|---|
| Render thread long in `Camera.Render`/`RenderLoop`, many SetPass | SRP Batcher compatibility, fewer shader variants per scene | technical-artist; `studio:stack-unity` rendering-and-pipelines |
| Many identical MeshRenderers | GPU Resident Drawer (Forward+/Deferred+, compute) or instancing | technical-artist + tech-lead-architect (pipeline ADR) |
| `Canvas.SendWillRenderCanvases`, UI rebuilds | split dynamic canvases, no layout groups on dynamic UI | unity-developer; `studio:stack-unity` input-and-ui |
| Culling cost high | layer cull distances, fewer cameras/render passes, occlusion | technical-artist |
| `Gfx.WaitForPresent` with idle render thread | GPU-bound: not a CPU problem | technical-artist |

## Uploading textures and meshes from code
- Update only changed regions: write the dirty rect into a small staging texture and
  `Graphics.CopyTexture` it into the atlas, instead of `SetPixelData` + `Apply` on the whole
  atlas (a 2048² RHalf atlas is 8 MiB per upload; desktop ~1-2 ms, far more on mobile/Web).
- `Apply(updateMipmaps: false)` when the texture has no mips; `makeNoLongerReadable: true` for
  data that never changes again (frees the CPU copy).
- Convert formats (float → half, color packing) in Burst jobs or once at import, not in
  managed per-texel loops on change.
- Meshes rebuilt often: `Mesh.MarkDynamic()`, `SetVertexBufferParams` once, then
  `SetVertexBufferData`/`SetIndexBufferData` with `MeshUpdateFlags` to skip bounds/index
  validation where safe; job-built meshes via `Mesh.AllocateWritableMeshData` +
  `ApplyAndDisposeWritableMeshData`. Re-upload only what changed (e.g. one paragraph on a keystroke).
- Atlas full → add a page or evict (LRU); never reset the atlas and force every client to rebuild.

## Sources
- Unity Manual: IL2CPP compiler options (Il2CppSetOption) https://docs.unity3d.com/ru/Manual/IL2CPP-CompilerOptions.html
- Scripting API 6.0: Il2CppCompilerConfiguration https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/il2cppcompilerconfiguration.md
- Unity forum: Boosting Android performance with LTO in Unity 6.5 https://discussions.unity.com/t/boosting-android-performance-with-lto-optimizations-in-unity-6-5/1720008
- Unity blog: IL2CPP optimizations - Devirtualization https://unity.com/blog/engine-platform/il2cpp-optimizations-devirtualization
- Unity blog: IL2CPP full generic sharing in Unity 2022.1 beta https://blog.unity.com/es/engine-platform/il2cpp-full-generic-sharing-in-unity-2022-1-beta
- Unity Manual 6.3: Adaptive Performance Android provider https://docs.unity3d.com/Manual/com.unity.adaptiveperformance.google.android.html
- Adaptive Performance Android provider changelog https://docs.unity3d.com/Packages/com.unity.adaptiveperformance.google.android@6.0/changelog/CHANGELOG.html
- Android Developers: ADPF with Unity https://developer.android.com/games/engines/unity/unity-adpf
- Unity issue: targetFrameRate with Optimized Frame Pacing https://issuetracker.unity3d.com/issues/android-application-dot-settargetframerate-different-results-when-optimized-frame-pacing-is-used
- Scripting API 6.3: FrameTimingManager (no GPU time on Web) https://docs.unity.com/en-us/engine/6000.3/script-reference/unityengine/frametimingmanager.md
