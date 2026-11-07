# Asset specs and pipeline

## Asset brief: must-have fields (templates/asset-brief.md)
| Field | Why |
|---|---|
| ID + name (final file name) | traceability, naming compliance |
| Purpose & gameplay role | what it must communicate (danger, reward, tier) |
| Context | where/how seen: camera distance, screen size, background, animation |
| Style refs | guide sections + 2-5 reference images with "take this / not that" |
| Technical spec | dimensions, texel density, poly/bone budget, format, atlas, pivot, frame count |
| Variants/states | skins, damage states, idle/win/blur, LODs, localization variants |
| Deliverables | source + export files, naming, folder |
| Rounds & milestones | sketch → color/blockout → final; dates; max rounds |
| Acceptance criteria | measurable checks (silhouette test, size, budget, naming) |
| Licensing | work-for-hire/assignment, fonts, stock, AI use allowed? |

## Naming conventions (default; adopt project's if one exists)
- Pattern: `<Prefix>_<Category>_<Name>_<Variant>_<Suffix>` - ASCII, PascalCase parts, no
  spaces, no Cyrillic, no dates/"final_v2" in names (VCS handles versions).
| Prefix | Type | Suffix examples |
|---|---|---|
| `T_` | texture | `_D` albedo, `_N` normal, `_M` mask (ORM/MRA packed), `_E` emissive |
| `SM_` / `SK_` | static / skinned mesh | `_LOD0..n` |
| `M_` / `MI_` | material / material variant | - |
| `SPR_` | sprite | `_0001` frame index |
| `UI_` | UI sprite/icon | `_Normal`, `_Pressed`, `_Disabled` |
| `FX_` | VFX prefab/texture | - |
| `ANIM_` | animation clip | `_Idle`, `_Win` |
| `SFX_` / `MUS_` / `VO_` | audio | `_01` variation, `_Loop` |
| `ATL_` | sprite atlas | - |
- Example: `SPR_Symbol_Pharaoh_Win_0012`, `T_Prop_Chest_Gold_D`, `SFX_UI_Button_Tap_03`.
- Mesh/texture pairs share `<Category>_<Name>`. Folder by feature, not by type, for
  Addressables grouping (`Assets/_Project/Art/Features/<Feature>/...`; confirm with unity-developer).

## Resolution and density targets (starting points - confirm with technical-artist)
| Context | Texel density (px/m) | Typical max texture |
|---|---|---|
| First-person PC/console, close props | ~1024 (10.24 px/cm) | 2K-4K |
| Third-person PC/console | ~512 | 2K |
| Mobile 3D | ~256-512 | 1K-2K |
| Top-down/isometric mobile | ~128-256 | 1K |
(industry heuristics, not standards; verify against target-device memory budgets)
- 2D/UI: author at the highest reference resolution (e.g. 2x of 1080p layout or 4K for
  TV/PC); export at runtime size; avoid runtime downscale > 2x (shimmer/blur).
- Power-of-two (POT) dimensions for 3D textures and anything mipmapped; UI sprites go in atlases
  (atlas page is POT; individual sprites need not be).
- Keep 2-4 px padding/extrusion around sprites in atlases to prevent bleeding.

## Sprite atlases (Unity)
- Sprite Atlas V2 is the default mode (Unity 2022.2+); atlases packed on Play/Build.
- Group by what is on screen together (per screen/feature), not by type; one atlas per
  draw-call group. Shared UI kit atlas separate from feature atlases.
- Page size: 2048×2048 safe mobile default; 4096 for modern devices/PC (verify device floor).
- Compression: ASTC for Android/iOS (block 4x4 high quality UI, 6x6/8x8 backgrounds) (verify
  default per Unity 6.x platform settings); BC7 (quality) / DXT5|BC3 for PC/console.
- Disable mipmaps for screen-space UI; enable for world-space sprites.
- Variant atlases (scale 0.5) for low-end tiers via Addressables labels if needed.

## 2D vs 3D pipeline choice
| Factor | 2D (sprites/Spine) | 3D (meshes/rig) |
|---|---|---|
| Many character variations/angles | costly (redraw per angle) | cheap (reuse rig/anims) |
| Painterly look, slots/casino symbols | strong | needs NPR shading |
| Memory | frames × resolution add up fast | textures + mesh, animation compressed |
| Animation tool | Spine, Unity 2D Animation (bones), frame-by-frame | Maya/Blender → FBX → Animator |
| Slots typical | symbols as Spine/2D skeletal + particle VFX | 3D only for premium/hero moments |
- Spine: runtime `spine-unity`, export `.skel` (binary) + atlas; lock Spine editor version to
  runtime version (verify compatibility table).
- 3D export: FBX, Y-up/Z-forward conversion consistent, scale 1 unit = 1 m, apply transforms,
  triangulate or let importer; tangents from MikkTSpace.

## File formats and handoff to technical-artist
| Asset | Source | Export to engine |
|---|---|---|
| 2D art | PSD/Krita/Procreate (layered) | PNG (8-bit sRGB; 16-bit for heightmaps), straight alpha |
| Vector UI | Figma/AI/SVG | PNG at target scale or SVG (UI Toolkit vector support) |
| 3D | .blend/.ma + Substance files | FBX (+ textures PNG/TGA) |
| Animation 2D | Spine project | .skel + .atlas + PNG |
| Fonts | licensed TTF/OTF | TMP SDF font asset generated in Unity |
| Audio | WAV 48 kHz/24-bit masters | WAV into engine; engine compresses (see audio-direction.md) |
- Handoff package: files named per convention + `README` line per asset (purpose, spec,
  pivot, frame rate, loop points) + license note. technical-artist owns import presets.

## Outsourcing management
- Before RFP: art bible, style target, asset list with complexity tiers (S/M/L) and counts,
  technical spec sheet, NDA, IP assignment terms (compliance-advisor/legal).
- Vendor trial: 1 paid test asset judged against brief; compare 2-3 vendors.
- Rounds: R1 sketch/blockout (direction), R2 color/high-poly (look), R3 final (craft). Feedback
  per round consolidated in ONE document, numbered, prioritized (P1-P3), within 2 business days.
- Change after approval of a round = change request (scope/cost), not a feedback note.
- Acceptance: technical checklist (naming, size, format, budget) + art checklist (readability,
  consistency) + in-engine check. Record accepted/rejected per asset in `asset-list-<feature>.md`.
- Track: asset | tier | vendor | round | status | due | blocker. Share weekly with producer.
- License hygiene: every font, texture pack, SFX library, and AI tool has a license entry
  (name, license type, URL, scope: commercial/seat/redistribution).

## Asset list (per feature) columns
`ID | Name | Type | Tier S/M/L | Spec | Owner/vendor | Round | Status | Due | Notes`

## Sources
- Unity Manual, Sprite Atlas V2 (Unity 6) https://docs.unity3d.com/Manual/sprite/atlas/v2/v2-landing.html
- Unity Manual, Texture compression formats https://docs.unity3d.com/Manual/texture-compression-formats.html
- Unity Manual, Importing models / FBX https://docs.unity3d.com/Manual/ImportingModelFiles.html
- Spine runtimes documentation (Esoteric Software) https://esotericsoftware.com/spine-unity
- Unity e-book "2D game art, animation, and lighting for artists" https://unity.com/resources/2d-game-art-animation-lighting-for-artists-ebook
