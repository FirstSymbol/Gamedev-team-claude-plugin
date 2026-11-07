# Shaders in URP (Shader Graph, HLSL, variants, mobile cost)

## Shader Graph vs hand-written HLSL
| Use Shader Graph when | Write HLSL when |
|---|---|
| artist-iterated surface looks, most props/characters/environment | tight mobile budgets needing exact instruction control |
| standard Lit/Unlit/Sprite/UI/Terrain targets (6.3 adds UI + terrain material types, templates, custom lighting) | custom lighting models beyond Shader Graph custom lighting, multi-pass, stencil tricks |
| team lacks shader programmers | compute shaders, full-screen Render Graph passes, procedural draws (`RenderMeshIndirect`) |
| reuse via Sub Graphs + Custom Function nodes (HLSL file) | shared shader libraries, strict variant control |
- Default: Shader Graph + Custom Function nodes for the few hand-tuned bits. Keep graphs small,
  shared logic in Sub Graphs, and versioned with clear names (`SG_Env_Rock`, `SubG_Triplanar`).
- Never edit generated code from "View Generated Shader" - it is overwritten on reimport.

## Minimal URP HLSL (SRP Batcher compatible)
```hlsl
Shader "Game/UnlitTint" {
  Properties { _BaseMap("Base", 2D) = "white" {} _BaseColor("Tint", Color) = (1,1,1,1) }
  SubShader {
    Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry" }
    Pass {
      Name "ForwardUnlit" Tags { "LightMode"="UniversalForward" }
      HLSLPROGRAM
      #pragma vertex vert
      #pragma fragment frag
      #pragma multi_compile_instancing
      #pragma multi_compile_fog
      #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
      TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
      CBUFFER_START(UnityPerMaterial)          // ALL material props here → SRP Batcher compatible
        float4 _BaseMap_ST; half4 _BaseColor;
      CBUFFER_END
      struct Attributes { float4 positionOS : POSITION; float2 uv : TEXCOORD0; UNITY_VERTEX_INPUT_INSTANCE_ID };
      struct Varyings   { float4 positionCS : SV_POSITION; float2 uv : TEXCOORD0; half fog : TEXCOORD1; };
      Varyings vert(Attributes i) {
        Varyings o; UNITY_SETUP_INSTANCE_ID(i);
        o.positionCS = TransformObjectToHClip(i.positionOS.xyz);
        o.uv = TRANSFORM_TEX(i.uv, _BaseMap);
        o.fog = ComputeFogFactor(o.positionCS.z);
        return o;
      }
      half4 frag(Varyings i) : SV_Target {
        half4 c = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv) * _BaseColor;
        c.rgb = MixFog(c.rgb, i.fog);
        return c;
      }
      ENDHLSL
    }
    // Add ShadowCaster / DepthOnly / DepthNormals passes (UsePass or copy from URP Lit) if the
    // object must cast shadows or appear in depth-based effects (SSAO, soft particles, decals).
  }
}
```
- URP uses HLSL + Core.hlsl macros; no `UnityCG.cginc`, no Surface Shaders (BiRP only).
- SRP Batcher check: select shader → Inspector "SRP Batcher: compatible". Properties outside
  `UnityPerMaterial` or a `MaterialPropertyBlock` on the renderer break compatibility.
- GPU Resident Drawer needs DOTS instancing: Shader Graph and URP shaders support it; custom HLSL
  needs `#pragma target 4.5`, `#pragma multi_compile _ DOTS_INSTANCING_ON`, instanced props in
  `UNITY_DOTS_INSTANCING_START/END` blocks; no `MaterialPropertyBlock` on those renderers.

## Keywords & variants
| Declaration | Variants built | Use |
|---|---|---|
| `shader_feature_local` | only those used by materials in the build | per-material toggles (most cases) |
| `multi_compile_local` | all combinations always | runtime-toggled keywords (quality settings) - expensive |
| `dynamic_branch` (`#pragma dynamic_branch`) | none (runtime `if` on uniform) | cheap toggles on modern GPUs; mobile cost is a uniform branch |
- `_local` keywords avoid the global keyword limit; prefer them for material-level features.
- Variant count = product of keyword sets per pass → watch build logs ("compiled N variants")
  and Editor.log shader compilation stats; aim for hundreds per shader, not tens of thousands.
- Strip: URP asset - disable unused features (additional lights shadows, SSAO, decals, LOD cross-fade,
  HDR output); Graphics settings → Shader Stripping; Unity 6.3 Shader Build Settings restrict
  keyword types; code: `IPreprocessShaders.OnProcessShader` to remove known-unused variants.
- Runtime stutter = variant/PSO creation on first use. Unity 6: trace with
  `GraphicsStateCollection.BeginTrace` in a dev build, ship the `.graphicsstate`, `WarmUp/WarmUpProgressively`
  on loading screens (experimental API); verify via Profiler markers `Shader.CreateGPUProgram`,
  `CreateGraphicsGraphicsPipelineImpl`. Older path: `ShaderVariantCollection.WarmUp`.
- Enable "Strict shader variant matching" in dev builds (Player settings) to catch missing variants (pink errors).

## Mobile cost rules
- Precision: `half` for colors/UVs/normals in fragment code; `float` for positions/depth/time.
- Fragment cost dominates (more pixels than vertices): move math to vertex stage, bake gradients
  into textures/ramps, avoid `pow`/`sin` chains, dependent texture reads, and discard/alpha-clip
  on large surfaces (breaks early-Z / HSR on TBDR GPUs - use for foliage cards sparingly).
- Texture samples: ≤ 3-4 per fragment on low-tier mobile (practitioner heuristic, verify per device);
  pack masks into RGBA channels (metal/AO/detail/smoothness).
- Transparent shaders: no depth write → overdraw; keep shader cheap (unlit, 1-2 samples).
- Avoid grab/opaque texture effects (refraction, distortion) on low tier: they require an extra copy.
- Use URP Simple Lit / Unlit or Baked Lit for low tiers; Lit (PBR) for mid/high.
- Measure: Shader Graph has no cost counter - inspect compiled stats (Show compiled code / Mali
  Offline Compiler / Xcode shader profiler) and on-device GPU time.

## Shader Graph practices
- Material types per target: Lit, Unlit, Sprite Lit/Unlit, Fullscreen, Decal, UI (6.3), Terrain (6.3).
- Expose only what artists tune; group with Categories; use Keywords (Boolean/Enum) with
  `Shader Feature` + Local scope by default.
- Sub Graphs for shared nodes; Custom Function nodes reference `.hlsl` files (not inline strings) for review/diff.
- Keep `Precision` = Half on graph/node level for mobile unless a node needs Float.
- Per-renderer variation: `Renderer.SetShaderUserValue` (6.3, read `unity_RendererUserValue`) or vertex
  colors / texture arrays - not material copies.
- Material variants (Unity 2022+): base material + variants with overrides (like prefab variants) to reduce duplication.

## Review checklist
- [ ] SRP Batcher compatible (or documented exception: instancing-only).
- [ ] Shadow/Depth/DepthNormals passes present where the object needs them.
- [ ] Keywords: `shader_feature_local` by default; variant count checked in build log.
- [ ] Mobile tier: half precision, ≤ N samples, no clip on big surfaces, cheap transparent path.
- [ ] Warmup collection updated after adding shaders/materials used in gameplay.
- [ ] Fallback for unsupported platforms (e.g. no compute → simpler path).

## Sources
- Unity e-book: Create popular shaders and visual effects with URP (Unity 6) https://unity.com/resources/create-shaders-visual-effects-urp-unity-6
- Unity Manual: SRP Batcher compatibility https://docs.unity3d.com/Manual/SRPBatcher-Incompatible.html
- Unity Manual 6.3: PSO tracing and warming https://docs.unity3d.com/Manual/shader-pso-trace-warming.html
- Unity Manual 6.0: Prewarm shaders https://docs.unity3d.com/6/Documentation/Manual/shader-prewarm.html
- Unity Manual 6.3: What's new (Shader Build Settings, Shader Graph, SetShaderUserValue) https://docs.unity.com/en-us/engine/current/manual/whats-new/unity63
- Unity how-to: Mobile optimization part 2 (shaders) https://unity.com/how-to/mobile-game-optimization-tips-part-2
- Unity Manual 6.0: Writing custom shaders in URP https://docs.unity3d.com/6000.0/Documentation/Manual/urp/writing-custom-shaders-urp.html
- Unity Manual: Declare DOTS Instanced properties https://docs.unity3d.com/Manual/dots-instancing-shaders-declare.html
