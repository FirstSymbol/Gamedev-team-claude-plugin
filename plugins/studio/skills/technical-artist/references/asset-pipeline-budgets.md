# Asset import pipeline & budgets (textures, meshes, atlases, audio, animation)

## Texture formats (GPU memory per pixel)
| Format | bpp | Platform | Use |
|---|---|---|---|
| RGBA32 (uncompressed) | 32 | all | avoid; only tiny lookup textures/pixel-art needing exact colors |
| BC1 (DXT1) | 4 | desktop/console | opaque color |
| BC3 (DXT5) | 8 | desktop | color + alpha (fast compress) |
| BC7 | 8 | desktop DX11+ | high-quality color/alpha (slow compress) |
| BC4 / BC5 | 4 / 8 | desktop | single-channel masks / normal maps (RG) |
| BC6H | 8 | desktop | HDR (skyboxes, lightmaps) |
| ASTC 4x4 / 5x5 / 6x6 / 8x8 / 10x10 / 12x12 | 8 / 5.12 / 3.56 / 2 / 1.28 / 0.89 | Android (GLES 3.1+/Vulkan), iOS A8+ | default mobile; block size = quality knob |
| ETC2 RGB / RGBA | 4 / 8 | Android GLES 3.0 | fallback for old Android / Crunch |
| ASTC HDR | as ASTC | Vulkan / ext | mobile HDR; unsupported → decompressed to RGB9e5 / RGBA Half |
- Android default compression = ASTC (Player Settings; Build Profile override wins). Devices
  lacking the format decompress to RGBA32 at runtime (4-8x memory + CPU cost). PVRTC deprecated.
- Memory = width × height × bpp / 8 × 1.33 (mips). Examples (with mips, MiB): 2048² RGBA32 ≈ 21.3;
  2048² ASTC 4x4 ≈ 5.3; 2048² ASTC 6x6 ≈ 2.4; 1024² BC7 ≈ 1.3.
- ASTC block choice (practitioner defaults, verify visually on device):
| Content | ASTC block |
|---|---|
| UI, fonts-as-texture, hero character face | 4x4 |
| Characters, weapons, normal maps | 5x5-6x6 |
| Environment albedo/masks | 6x6 |
| Large terrain/sky/background, distant | 8x8+ |
- Crunch reduces download/disk size, not GPU memory; costs quality and load-time CPU.

## Texture import rules
- Max Size per platform override (mobile typically half of PC); never import 8K sources at 8K.
- sRGB on for color (albedo, UI); off for data (normal, masks, flow, LUT-as-data).
- Read/Write Enabled OFF (on = second CPU copy, doubles memory) unless CPU sampling is required.
- Mipmaps: ON for 3D world textures; OFF for UI/sprites in screen space. Mipmap Streaming
  (Quality settings budget) for large open scenes on mobile/console.
- Dimensions: multiples of 4 required for block formats; POT preferred (mips, older GPUs).
- Normal maps: Texture Type = Normal map (correct encoding); BC5 desktop, ASTC 5x5-6x6 mobile.
- Channel packing: one RGBA mask (R=metal, G=AO, B=detail, A=smoothness) instead of 3-4 textures.
- Filter: Bilinear default; Trilinear for surfaces at grazing angles; Aniso 2-4 only on floors/roads.
- Texture arrays / atlases for many small materials (fewer materials → batching).

## Sprite atlases (Sprite Atlas V2)
- Group by usage (screen/level/character), not by type; one atlas per screen avoids loading unused sprites.
- Max atlas 2048 on mobile (4096 only if device tier allows); padding 2-4 px; Tight packing for world sprites.
- Late binding + Addressables for optional atlases; "Include in Build" off for atlases loaded on demand.
- Unity 6.4+: `SpriteAtlasManager.CreateSpriteAtlas` builds atlases at runtime (UGC/dynamic avatars).
- Sprite Mesh Type = Tight for large irregular sprites (less overdraw), Full Rect for UI 9-slice.

## Mesh / model import
- Read/Write OFF; Import Cameras/Lights OFF; Animation import OFF and Rig = None for static props.
- Index Format Auto (16-bit when < 65k verts); Optimize Mesh ON; Blend shapes OFF unless used.
- Mesh Compression (importer) reduces build size, not runtime memory; Player Settings Vertex
  Compression reduces runtime vertex precision/memory (check artifacts on large meshes).
- Normals: Import; Tangents: only when normal-mapped (Calculate Mikktspace).
- Characters: Optimize Game Objects (strips transform hierarchy, expose only needed bones);
  Skin Weights 2-4 bones per vertex on mobile (Quality setting).
- Scale: 1 unit = 1 m; export from DCC with applied transforms and "Bake Axis Conversion" to avoid
  rotated roots; pivot at logical base/hinge.
- LODs: name `<Mesh>_LOD0/_LOD1/...` in FBX → LOD Group auto-created. Unity 6.2+ Mesh LOD: auto-generated
  in importer (Generate Mesh LODs) stored in one index buffer; triangle meshes only; ignores skin weights/
  blend shapes; GPU instancing/Entities Graphics always use LOD0; don't combine with LOD Group.
- LOD Bias / Maximum LOD Level per quality tier; Fade mode cross-fade costs (dithering shader variant).
- Colliders: separate simplified meshes or primitives; never MeshCollider on the render mesh for dynamic objects.

## Audio import (shared with audio owner)
| Clip type | Load Type | Format |
|---|---|---|
| Short frequent SFX (< ~1 s) | Decompress On Load | ADPCM or PCM (tiny) |
| Medium SFX / VO | Compressed In Memory | Vorbis (quality 50-70%) |
| Music / ambience loops | Streaming | Vorbis/MP3 |
- Force To Mono for 3D-positioned sounds; sample rate override 22-32 kHz for SFX on mobile; Preload Audio Data off for rarely used clips.

## Animation import
- Compression: Optimal; tune rotation/position/scale error; remove unused curves (scale curves are common waste).
- Generic rig for non-humanoids and when retargeting isn't needed (Humanoid costs +30-50% CPU, Unity).
- Animator Culling Mode: Cull Update Transforms / Cull Completely for offscreen characters.

## Budget template values (heuristics per tier; replace with measured project numbers)
| Item | Low mobile | Mid mobile | PC/console |
|---|---|---|---|
| Texture memory resident | ≤ 150-250 MB | ≤ 300-500 MB | ≤ 1-3 GB |
| Hero character tris (LOD0) | 3-8k | 10-20k | 40-100k+ |
| Prop tris | 100-1.5k | 300-3k | 1-20k |
| Bones per character | ≤ 30-40 | ≤ 60 | ≤ 150+ |
| Texture size per hero material | 512-1024 | 1024 | 2048-4096 |
| Materials per character | 1 | 1-2 | 2-4 |
- Store the agreed budget in `.team/specs/art/tech-art-budget.md`; validators (tooling ref) enforce it.

## Import automation
- Presets + Preset Manager with folder filters (e.g. `glob:"Assets/_Project/Art/UI/**.png"`; `glob:` prefix,
  quoted, case-sensitive, applied top to bottom) for defaults; `AssetPostprocessor` for rules presets can't express
  (code: unity-developer references/editor-tooling.md).
- Folder conventions: `Art/<Category>/<Asset>/` with source files outside `Assets/` (PSD/blend in `ArtSource/` LFS repo
  or folder) unless the team wants live DCC import.
- Unity Accelerator (cache server) for teams > 3 to cut reimport time after branch switches.

## Sources
- Unity Manual 6.3: Recommended texture formats by platform https://docs.unity.com/en-us/engine/6000.3/manual/materials-and-shaders/textures/textures-getting-started/texture-compression-formats/texture-choose-format-by-platform
- Unity Manual 6.2: Introduction to Mesh LOD https://docs.unity3d.com/6000.2/Documentation/Manual/lod/mesh-lod-introduction.html
- Unity Manual 6.4: What's new (runtime sprite atlas) https://docs.unity3d.com/Manual/WhatsNewUnity64.html
- Unity how-to: Mobile optimization part 2 (animation rigs, batching) https://unity.com/how-to/mobile-game-optimization-tips-part-2
- Unity e-book: Optimize your mobile game performance (Unity 6 ed.) https://unity.com/blog/games/optimize-your-mobile-game-performance-tips-on-profiling-memory-and-code-architecture-from
- ARM: ASTC format overview https://github.com/ARM-software/astc-encoder/blob/main/Docs/FormatOverview.md
- Unity Manual 6.6: Filter default preset assets (glob syntax) https://docs.unity.com/en-us/engine/6000.6/manual/assets-and-media/presets/default
