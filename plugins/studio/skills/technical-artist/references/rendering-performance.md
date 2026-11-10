# GPU / rendering performance (art-side levers)
Pipeline mechanics (GPU Resident Drawer, SRP Batcher, Render Graph, lighting modes) live in
`studio:stack-unity` (rendering-and-pipelines). This file = diagnosing and fixing GPU cost.
Profiler/Highlights, FrameTimingManager, A/B method, texture/mesh upload costs → `studio:unity-performance`.

## Diagnose first
1. Confirm GPU-bound (Profiler Timeline: main thread in `Gfx.WaitForPresentOnGfxThread`, render
   thread in `Gfx.PresentFrame`/`WaitForLastPresent`; `FrameTimingManager` GPU ms). CPU-bound
   render thread (`Camera.Render` long) = draw call/SetPass problem, not pixels.
2. Resolution test: drop Render Scale to 0.5. GPU ms drops a lot → fragment/fill/bandwidth bound;
   barely changes → vertex/geometry or draw-submission bound.
3. Frame Debugger: walk passes; count SetPass calls and batches; read "batch break" reasons.
4. Platform GPU tool for counters: RenderDoc (desktop/Android), Xcode GPU frame capture + Metal
   counters (iOS), Android GPU Inspector, Arm Performance Studio (Mali: Streamline counters,
   Mali Offline Compiler for shader cycles), Snapdragon Profiler (Adreno), PIX (Windows/Xbox).
5. Record in `.team/reports/gpu-perf-<area>.md`: device, scene, resolution, GPU ms per pass before/after.

## Mobile GPU model (TBDR) - why rules differ
- Mali/Adreno/Apple GPUs are tile-based: framebuffer in on-chip tile memory; external memory
  bandwidth (load/store of render targets) is the expensive part and drains battery/heat.
- Costly on TBDR: extra render target switches, full-screen copies (Opaque/Depth texture, grab
  passes), MSAA resolve to memory, post-processing chains, reading back depth.
- Render Graph merges passes into native render passes where declared correctly - custom
  features must declare attachments properly (unity-developer/TA write them together).
- Alpha test/discard and depth write from fragment shaders defeat hidden-surface removal → more shading.

## Overdraw & fill rate
- Target overdraw: average ≤ 2-2.5x on low mobile, hot spots ≤ 3-4x (practitioner heuristic, verify per device).
- View: URP Rendering Debugger → Rendering → Overdraw; Scene view Overdraw (BiRP); GPU tool heatmaps.
- Fixes: opaque instead of transparent; tight sprite meshes; smaller/fewer particles near camera;
  fewer full-screen UI layers (disable 3D camera behind opaque menus); front-to-back opaque order
  (URP sorts opaque automatically); avoid stacked transparent water/fog/glass planes.
- Skybox/background: cheap shader; draw after opaques (default).

## Draw calls & SetPass (art-side)
- Fewer materials = fewer state changes: atlases, texture arrays, shared master materials with
  material variants; avoid unique material per prop.
- Keep shaders consistent across a scene (SRP Batcher batches by shader variant).
- Static environment: mark Static (batching/occlusion/lightmaps); large repeated sets → GPU
  Resident Drawer or instancing (no per-renderer MaterialPropertyBlocks).
- Occlusion: Occlusion Culling bake for indoor/dense scenes, or GPU Occlusion Culling (Unity 6, with GRD).
- Camera far plane and per-layer cull distances (`Camera.layerCullDistances`) for small props.
- LODs on everything with > ~1k tris visible at distance; impostors/billboards for far trees.
- Mobile batches/draw targets per tier: see `studio:unity-developer` (performance) budget table.

## Lighting & shadows cost
| Lever | Typical saving |
|---|---|
| Bake static lighting (lightmaps + APV/probes) instead of realtime additional lights | large on mobile |
| Shadow distance shorter, 1-2 cascades on mobile, lower shadow resolution | usually the biggest realtime-light saving; measure GPU ms per device (no published benchmark) |
| Disable Cast Shadows on small props, particles, grass | per-object shadow pass removed |
| Soft shadows off on low tier | fragment cost |
| Additional lights per object limit (Forward), per-pixel → per-vertex on low tier | fragment cost |
| Light cookies, realtime reflection probes, SSAO off on low tier | pass removal |
- Lightmap texel density consistent (e.g. 10-20 texels/m environment, lower for distant); lightmap
  atlas count small; compress lightmaps (check banding).
- Realtime reflection probes: avoid; baked probes at 64-128 px on mobile.

## Post-processing budget (URP Volume)
| Effect | Low mobile | Mid mobile | PC/console |
|---|---|---|---|
| Tonemapping + color grading (LUT) | yes | yes | yes |
| Bloom (Kawase/Dual in 6.3) | low quality or off | yes, half res | yes |
| Vignette, film grain | cheap - ok | ok | ok |
| SSAO | no | maybe, low | yes |
| Depth of Field, Motion Blur | no | cutscenes only | yes |
| Upscaling (STP/FSR) + render scale < 1 | render scale 0.7-0.85 | STP if compute available | DLSS/FSR/STP |
- One global Volume profile per quality tier; local volumes sparingly (blending cost minor, but
  each enabled effect is a pass).

## Resolution & frame pacing
- Render Scale and dynamic resolution are the biggest single GPU lever on high-DPI phones;
  render UI at native, 3D at reduced scale.
- Cap frame rate deliberately (30 for battery-heavy genres, 60 for action); thermal headroom 35%.
- HDR rendering off on low tier if not needed (bandwidth); MSAA 2-4x on TBDR is cheaper than FXAA chains on some GPUs (measure).

## Fix table
| Symptom | Likely cause | Fix |
|---|---|---|
| GPU ms scales with resolution | fill/fragment | render scale, cheaper shaders, overdraw cuts |
| Spikes when effects appear | shader/PSO compile | PSO trace + warmup (shaders-urp.md) |
| High bandwidth, device heats | many RT switches/copies, post chain | remove Opaque/Depth texture needs, fewer passes, lower HDR/MSAA |
| Many SetPass calls | material/shader variety | atlases, master materials, SRP Batcher compat |
| Shadows dominate | cascades/distance/casters | shadow settings per tier, disable small casters |
| Foliage heavy | alpha test + overdraw | fewer, opaque-core cards, LOD to billboards, density scaling |
| UI heavy | fullscreen transparent layers | opaque backgrounds, disable world camera behind menus |

## Sources
- Unity how-to: Best practices for profiling game performance https://unity.com/how-to/best-practices-for-profiling-game-performance
- Unity how-to: Mobile optimization part 2 (lighting, transparency, shaders) https://unity.com/how-to/mobile-game-optimization-tips-part-2
- Unity e-book: Introduction to URP for advanced creators (Unity 6) https://unity.com/resources/introduction-to-urp-advanced-creators-unity-6
- Arm: Mali GPU best practices developer guide https://developer.arm.com/documentation/101897/latest/
- Unity Manual 6.3: GPU Resident Drawer https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html
- Unity Manual 6.3: What's new (bloom filters, Render Graph viewer on device) https://docs.unity.com/en-us/engine/current/manual/whats-new/unity63
