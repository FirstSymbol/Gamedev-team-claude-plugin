# VFX: Particle System (Shuriken) vs VFX Graph, budgets, optimization

## Decision
| Criterion | Particle System (built-in, CPU) | VFX Graph (`com.unity.visualeffectgraph`, GPU) |
|---|---|---|
| Scale | hundreds-thousands of particles | up to millions |
| Platforms | everything incl. GLES, low-end mobile, Web | needs compute + SSBO; no OpenGL ES; mobile and URP "not out of preview" per package docs (still so in 17.3 / Unity 6.3) |
| Physics | collides with Unity physics, triggers, `OnParticleCollision` | depth-buffer collision, SDFs, signed-distance/vector fields; no physics callbacks |
| CPU access | per-particle read/write from C# (`GetParticles`/`SetParticles`) | exposed properties + events (`SendEvent`, `VFXEventAttribute`); GPU readback costly |
| Authoring | Inspector modules | node graph, Shader Graph outputs, subgraphs |
| Pipelines | BiRP, URP, HDRP | URP, HDRP (URP: no gamma color space) |
| Culling / bounds | automatic bounds | must set bounds (manual or recorded) - wrong bounds = popping or no culling |
- Rule: mobile/Web/low-end or gameplay-coupled effects (hits that need callbacks) → Particle System.
  PC/console/high-end, massive ambient effects (rain, swarms, magic storms) → VFX Graph.
- Mixed projects fine; one effect = one system. Check `SystemInfo.supportsComputeShaders` and provide
  a Particle System fallback when shipping VFX Graph on mixed-capability platforms.

## Budgets (set per tier in the tech-art budget; heuristics, verify on device)
| Tier | Live CPU particles on screen | Overdraw layers in hot spots | Notes |
|---|---|---|---|
| Low mobile | ≤ ~300-500 total | ≤ 2-3 | unlit, small sprites, no soft particles |
| Mid mobile | ≤ ~1000-2000 | ≤ 4 | limited lit particles |
| PC/console | 10k+ CPU, 100k-1M+ GPU (VFX Graph) | measure | lit, soft, distortion OK within budget |
- Fill-rate (overdraw) usually limits mobile VFX before particle count does: large transparent quads
  near the camera are the classic killer.

## Particle System optimization
- Max Particles cap per system; Ring Buffer mode for persistent decals/trails.
- Culling: offscreen systems pause only in procedural mode. Procedural mode is lost with World
  simulation space, Collision, Sub Emitters, Trails, External Forces, complex curves, or values
  changed from script at runtime - Inspector icon tooltip lists the reasons
  (`ParticleSystem.proceduralSimulationSupported`). Keep ambient looping effects procedural.
- Prefer Simulation Space Local for attached effects; scaling mode explicit.
- Collision module: Planes or low-quality World collision with collides-with layer mask; it's CPU-expensive.
- Mesh particles: low-poly meshes, GPU instancing on the renderer (`Enable GPU Instancing` in Renderer module).
- Sorting: one material per effect where possible (shared atlas texture) to keep batching;
  sort mode only when needed.
- Trails/Ribbons: cap vertices (lifetime, min vertex distance).
- Pool effect instances (`ObjectPool` / pre-instantiated), `Play/Stop` not `Instantiate/Destroy`; stop
  emission with `StopEmitting` so live particles finish.
- Sub-emitters multiply counts - budget them explicitly.

## VFX Graph optimization
- Capacity per system = memory reserved upfront; set realistic capacity, not 1M by default.
- Bounds: use "Recorded" bounds or explicit; enable culling flags; set Culling State to pause when invisible.
- Update/Output contexts cost per particle; strip unused attributes; use `Particle Strip` carefully.
- Shader Graph outputs: keep shader cheap; lit outputs and soft particles cost depth texture reads.
- Instancing (VFX Graph 17 / Unity 6): on by default; many identical VFX instances batch. Assets using
  Output Mesh or Output Event Handlers can't be instanced (17.3 manual).
- Events from gameplay via `VisualEffect.SendEvent(id, attr)`; cache `Shader.PropertyToID`/`VisualEffect` IDs.
- Scalability: expose spawn-rate/capacity multipliers per quality level.

## Content techniques (cheap looks)
- Flipbooks (texture sheet animation) instead of high counts; motion vectors flipbook blending for smoothness.
- Pack masks in RGBA (alpha + emission + distortion mask).
- Cut out transparent waste: use tight meshes (Sprite mesh type Tight / custom quad shapes)
  instead of full quads for large sprites - reduces overdraw significantly.
- Fake lighting in texture/vertex colors; HDR color + bloom for glow rather than many additive layers.
- Distortion/refraction requires opaque texture copy (URP) - one effect class per tier.
- Shaders for VFX: unlit, `half`, 1-2 samples; additive/premultiplied blend; avoid alpha test on big quads.

## Debug & measure
- Scene view Overdraw / URP Rendering Debugger (Overdraw mode) to see hot spots.
- Particle System: Profiler `ParticleSystem.Update`/`ScheduleGeometryJobs`; VFX Graph: VFX
  Control panel + GPU timings in Frame Debugger / platform tools.
- Test worst case: max simultaneous effects in a real combat scene on the lowest device; record
  GPU ms with and without VFX.

## Checklist
- [ ] System choice matches platform tier; VFX Graph has fallback if any target lacks compute.
- [ ] Max particles/capacity, bounds and culling configured; effects pooled.
- [ ] Overdraw in worst-case scene within tier limit (screenshot of overdraw view attached).
- [ ] Materials shared/atlased; shaders unlit/half on mobile.
- [ ] Scalability multipliers wired to quality levels.

## Sources
- Unity Manual: Choosing your particle system solution https://docs.unity3d.com/Manual/ChoosingYourParticleSystem.html
- VFX Graph 17.3: System requirements https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.3/manual/System-Requirements.html
- VFX Graph 17.3: Instancing https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.3/manual/Instancing.html
- Unity e-book: The definitive guide to advanced visual effects (Unity 6 ed.) https://unity.com/resources/creating-advanced-vfx-unity6
- Unity how-to: Mobile optimization part 2 (transparency, overdraw) https://unity.com/how-to/mobile-game-optimization-tips-part-2
- Unity blog: #UnityTips ParticleSystem performance - culling https://unity.com/blog/engine-platform/particlesystem-performance-culling-tips
- Scripting API: ParticleSystemCullingMode https://docs.unity3d.com/ScriptReference/ParticleSystemCullingMode.html
