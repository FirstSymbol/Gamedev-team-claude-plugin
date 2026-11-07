# Render pipelines, batching, Render Graph, lighting basics
Deep shader/VFX/import work belongs to technical-artist (studio:technical-artist references).

## Pipeline choice (Unity 6.x, 2026)
| Pipeline | Status | Choose when |
|---|---|---|
| URP (Universal) | primary, all new features | default for every new project: mobile, Web, XR, Switch-class, PC/console |
| HDRP | maintenance since 6.5 (no new features) | existing HDRP projects; new high-end PC/console only with an ADR acknowledging the risk |
| Built-in (BiRP) | deprecated in 6.5, supported through 6.7 LTS lifecycle | legacy only - plan migration (Render Pipeline Converter, command-line converter) |
- Pipeline switch mid-project = re-authoring all shaders/materials/lighting; decide at kickoff (ADR).
- Asset Store packs: check URP support before buying; BiRP-only shaders render pink in URP.

## URP rendering paths
| Path | Lights | Notes |
|---|---|---|
| Forward | per-object light limit (mobile ~4-8 additional) | simplest; MSAA friendly |
| Forward+ | clustered, no per-object limit | required for GPU Resident Drawer; good default for PC/console and modern mobile |
| Deferred | many lights, no MSAA | SM 4.5+, no OpenGL/GLES; G-buffer bandwidth heavy on mobile |
| Deferred+ (6.1+) | clustered deferred | supports GPU Resident Drawer + GPU occlusion; "optimized for tile-based mobile" per 6.1 docs; measure per device |

## Draw-call reduction (what to use, in order)
1. **GPU Resident Drawer** (BatchRendererGroup, Unity 6): automatic instanced drawing of
   MeshRenderers. Setup: Graphics → BRG Variants = Keep All; URP asset SRP Batcher on, GPU
   Resident Drawer = Instanced Drawing; renderer path Forward+ (or Deferred+). Needs compute
   shaders; not OpenGL ES. Only MeshRenderer objects; anything else (skinned meshes, particles,
   terrain) falls back to normal non-instanced drawing.
   Pair with GPU Occlusion Culling for dense scenes. Biggest wins: many static/repeated meshes.
2. **SRP Batcher**: batches by shader variant, caches per-material data on GPU; reduces
   CPU setup cost per draw, not draw count. Shader must keep all material props in
   `CBUFFER_START(UnityPerMaterial)`; a `MaterialPropertyBlock` makes that renderer incompatible.
3. **Static batching**: static non-moving meshes sharing a material; costs memory (combined copies).
4. **GPU instancing**: many identical mesh+material objects; opt out of SRP Batcher for them;
   or `Graphics.RenderMeshInstanced` / `RenderMeshIndirect` for procedural crowds/grass.
5. Dynamic batching: deprecated in 6.5 - don't rely on it.
- Per-object variation without breaking batching: separate materials, texture arrays + index,
  `Renderer.SetShaderUserValue` (6.3, 32-bit per renderer), not `MaterialPropertyBlock` in SRP.
- `renderer.material` instantiates a material copy (breaks batching, leaks) - use `sharedMaterial`.
- Verify with Frame Debugger ("why this draw call can't be batched" reason) and Rendering Profiler counters.

## Render Graph (URP 17+)
- Unity 6 URP builds frames through Render Graph; Compatibility Mode (non-RG) removed in 6.4
  for custom passes; URP and HDRP share one Render Graph API/compiler (6.3).
- Custom effect = `ScriptableRendererFeature` + `ScriptableRenderPass.RecordRenderGraph(RenderGraph, ContextContainer)`;
  declare texture reads/writes so the graph can cull passes and merge native render passes
  (vital for tile-based mobile GPUs).
- Old `Execute(ScriptableRenderContext, ref RenderingData)` passes from 2022 LTS must be ported.
- Debug: Render Graph Viewer (can attach to device builds, 6.3).
- Blitting: `Blitter`/`RenderGraphUtils.AddBlitPass`, never `cmd.Blit` to camera target in RG.

## Lighting & baking basics
| Mode | Cost | Use |
|---|---|---|
| Baked | runtime ~free, memory for lightmaps | static environment, mobile default |
| Mixed (Baked Indirect / Shadowmask / Subtractive) | medium | baked GI + realtime direct/shadows for dynamic objects; Subtractive cheapest (mobile) |
| Realtime | high (shadows!) | main directional light, few key lights |
- Dynamic objects get indirect light from Light Probes or **Adaptive Probe Volumes** (APV,
  URP+HDRP in Unity 6; per-pixel, no manual probe placement; supports lighting scenarios).
- Baking: GPU Lightmapper default (6.3), xAtlas packer default for new scenes; set texel density
  per scene; bake on a build machine for consistency; `LightingData.asset` → LFS, don't merge.
- Reflection probes: baked, low resolution on mobile (64-128), box projection indoors.
- Shadows: biggest realtime light cost. Mobile: 1 directional shadow, 1-2 cascades, short
  shadow distance; disable cast shadows on small props; blob shadows for crowds.
- Realtime light count is a design constraint - write it into the art spec per tier.

## Frame cost knobs (URP asset / camera)
- Render Scale + upscaler (STP in Unity 6: needs SM 5.0 compute, no OpenGL ES, forces TAA;
  FSR/DLSS where supported) - cheapest way to recover GPU time on fill-bound devices.
- HDR, MSAA (4x on tile-based mobile is relatively cheap; costly on desktop deferred),
  Depth Texture / Opaque Texture (each adds copies - enable only if a shader needs them).
- Post-processing: mobile-safe = tonemapping, color grading (LUT), light bloom (Kawase/Dual
  bloom 6.3); avoid DoF, motion blur, SSAO on low tier.
- Camera stacking: each overlay camera re-renders culling/setup; prefer one camera + UI overlay.
- Quality tiers: one URP Asset per quality level (Low/Med/High) + per-device mapping
  (Adaptive Performance is a built-in module in 6.3).

## Profiling tools
- Frame Debugger (draw order, batching break reasons), Render Graph Viewer, Rendering Profiler module.
- GPU: RenderDoc (desktop/Android), Xcode GPU frame capture (iOS/macOS), Android GPU Inspector,
  Arm Performance Studio / Snapdragon Profiler (mobile counters: overdraw, bandwidth).
- Decide CPU-bound vs GPU-bound first (Profiler: `Gfx.WaitForPresent`/`WaitForGPU` high = GPU-bound).

## Sources
- Unity Manual 6.3: GPU Resident Drawer https://docs.unity3d.com/6000.3/Documentation/Manual/urp/gpu-resident-drawer.html
- Unity Manual: SRP Batcher compatibility https://docs.unity3d.com/Manual/SRPBatcher-Incompatible.html
- Unity Manual 6.4: Upgrade guide (Compatibility Mode removal) https://docs.unity3d.com/Manual/UpgradeGuideUnity64.html
- Unity Manual 6.3: What's new https://docs.unity.com/en-us/engine/current/manual/whats-new/unity63
- Unity Manual 6.1: What's new in URP (Deferred+) https://docs.unity3d.com/6000.1/Documentation/Manual/urp/whats-new/urp-whats-new.html
- Unity e-book: Introduction to the Universal Render Pipeline for advanced creators (Unity 6 ed.) https://unity.com/resources/introduction-to-urp-advanced-creators-unity-6
- Unity how-to: Mobile optimization - lighting, batching https://unity.com/how-to/mobile-game-optimization-tips-part-2
- Ocean View Games: Unity 6.5 - should you upgrade (BiRP/HDRP/dynamic batching status) https://oceanviewgames.co.uk/blog/posts/unity-6-5-should-you-upgrade
- Unity Manual 6.0: Spatial-Temporal Post-processing (STP) requirements https://docs.unity.com/en-us/engine/6000.0/manual/cameras/urp/change-resolution-scale-urp/stp-upscaler
