# Tech-art tooling & automation (audits, import rules, DCC export, CI)

## Layers of enforcement (cheapest first)
| Layer | Tool | Runs where |
|---|---|---|
| Defaults | Presets + Preset Manager (folder filters) | Editor on first import |
| Rules | `AssetPostprocessor` (path-scoped, versioned) | every import, incl. CI/Accelerator |
| Audit without Unity | Python/Bash over files + `.meta` YAML | agent shell, pre-commit, CI |
| Audit in Unity | `-executeMethod` validators, Project Auditor, Addressables Build Report | batch mode / CI |
| Runtime check | dev-build overlay (`ProfilerRecorder` memory/draws), Memory Profiler snapshots | device |
- Code for postprocessors/validators/menus: unity-developer references/editor-tooling.md
  (TA defines the rules and budgets; unity-developer or TA implements).

## Reading import settings from .meta (no Editor needed)
- `.meta` files are YAML; importer settings live there. Parse them with a script - never
  Read them one by one (token cost). Field names below are the 2022-6.x YAML keys (confirm once on a sample `.meta` of
  the project):
| Importer | Field | Bad value |
|---|---|---|
| TextureImporter | `isReadable` | `1` without justification |
| TextureImporter | `enableMipMap` | `1` on UI/sprites, `0` on 3D world textures |
| TextureImporter | `sRGBTexture` | `1` on normal/mask textures |
| TextureImporter | `maxTextureSize` (default + per `buildTarget` in `platformSettings`) | above budget |
| TextureImporter | `platformSettings` → `buildTarget: Android/iPhone`, `overridden`, `textureFormat` | no override when budget needs one |
| ModelImporter | `isReadable`, `importAnimation`, `importBlendShapes`, `importCameras`, `importLights` | `1` on static props |
```python
# tools/audit_textures.py  - stdlib only; usage: python tools/audit_textures.py Assets 2048
import os, re, struct, sys
root, max_px = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2048
def png_size(p):
    with open(p, "rb") as f:
        h = f.read(24)
    return struct.unpack(">II", h[16:24]) if h[:8] == b"\x89PNG\r\n\x1a\n" else None
rows = []
for d, _, files in os.walk(root):
    for fn in files:
        if not fn.lower().endswith((".png", ".tga", ".psd", ".jpg", ".exr")): continue
        p = os.path.join(d, fn); meta = p + ".meta"
        m = open(meta, encoding="utf-8", errors="ignore").read() if os.path.exists(meta) else ""
        issues = []
        if re.search(r"^\s*isReadable: 1", m, re.M): issues.append("read/write on")
        sizes = [int(x) for x in re.findall(r"maxTextureSize: (\d+)", m)]
        if sizes and max(sizes) > max_px: issues.append(f"maxTextureSize {max(sizes)}")
        if fn.lower().endswith(".png"):
            wh = png_size(p)
            if wh and (wh[0] % 4 or wh[1] % 4): issues.append(f"not multiple of 4 {wh}")
        if issues: rows.append(f"{p}\t{'; '.join(issues)}")
print("\n".join(rows) or "OK"); sys.exit(1 if rows else 0)
```
- Output a summary table to `.team/reports/asset-audit-<date>.md` (counts by issue + top 20 offenders), not raw dumps.
- Extend similarly: models with `isReadable: 1`, audio with `loadType` mismatch, sprites outside atlases.

## In-Unity validators (batch mode)
- Budget validator per folder/label: texture max size and format per platform, mesh tris/verts
  (`Mesh.triangles.Length/3` via `AssetDatabase.LoadAssetAtPath<Mesh>`), material count per prefab,
  shader not in allowed list, missing LODs above N tris, particle max counts.
- Run: `Unity -batchmode -nographics -quit -projectPath . -executeMethod Game.Editor.ArtValidation.Run -logFile build/art.log`
  → exit code 1 on violations (CI gate). Flags/logs: `studio:stack-unity` (ai-tooling).
- Project Auditor (Unity 6 module) for settings/shader/texture diagnostics; Addressables Build Report for duplicates.
- Shader variants: build log "Compiled shader ... variants"; `IPreprocessShaders` logging to CSV to find explosions.

## Presets & Preset Manager
- Create presets from a correctly configured importer (Inspector → preset icon → Save current to...).
- Preset Manager → add default per importer type with filter (folder/glob) - e.g. UI textures, normal maps,
  environment albedo, characters, audio SFX/music. Presets apply on first import only; to re-apply
  to existing assets use Reset in the importer's context menu (Reimport does not apply them), Preset "Apply", or a postprocessor.
- Name presets `Preset_<Importer>_<Category>_<Tier>`; keep them in `Assets/_Project/Settings/Presets/`.

## DCC export pipeline
- Blender headless export: `blender -b source.blend -P tools/export_fbx.py -- --out Assets/_Project/Art/...`
  (script: apply transforms, `bpy.ops.export_scene.fbx(apply_scale_options='FBX_SCALE_UNITS',
  bake_space_transform=True, use_mesh_modifiers=True, add_leaf_bones=False)`); options confirmed in the Blender 5.2 API;
  `bake_space_transform` is experimental and "known to be broken with armatures/animations" - set False for rigs.
- Maya/Max: FBX presets checked into repo; 1 unit = 1 cm in Maya → set FBX/importer scale consistently.
- Naming conventions (enforced by validator):
| Asset | Pattern |
|---|---|
| Mesh / prefab | `SM_<Name>` static, `SK_<Name>` skinned, `PF_<Name>` prefab; LODs `_LOD0.._LODn` |
| Textures | `T_<Name>_<Suffix>`: `_D` albedo, `_N` normal, `_M` packed mask, `_E` emission |
| Materials / shaders | `M_<Name>`, `MI_<Name>` (variant), `SG_<Name>` Shader Graph, `SubG_<Name>` |
| VFX | `VFX_<Name>` (VFX Graph), `PS_<Name>` (Particle System prefab) |
- Source files (PSD/blend/spp) in LFS outside `Assets/` unless live import is wanted (keeps imports fast).

## CI integration
- Pre-commit (fast, no Unity): texture/meta audit script, LFS check (`git lfs ls-files` covers new binaries).
- PR CI: Unity batch validator + EditMode tests; publish audit report artifact.
- Nightly: full player build per platform + build size report diff (size per category vs last nightly);
  alert on > 5% growth (pick threshold with release-platform-manager).
- Pipeline setup itself → devops-sre-engineer; TA owns rules, thresholds and reports.

## Checklist
- [ ] Presets exist for every asset category in the budget; Preset Manager filters set.
- [ ] Audit script runs clean on main; violations ticketed with owner.
- [ ] Batch validator wired into CI and fails on budget violations.
- [ ] DCC export scripts/presets in repo; naming validated.
- [ ] Build size diff tracked per nightly.

## Sources
- Unity Manual: Presets https://docs.unity3d.com/Manual/Presets.html
- Scripting API: AssetPostprocessor https://docs.unity3d.com/ScriptReference/AssetPostprocessor.html
- Unity Manual: Project Auditor https://docs.unity3d.com/Manual/com.unity.project-auditor.html
- Unity Manual: Build from the command line https://docs.unity.com/en-us/engine/current/manual/building-and-publishing/build-command-line
- Blender Python API (5.2): export_scene.fbx https://docs.blender.org/api/current/bpy.ops.export_scene.html
- Unity Manual 6.6: Filter default preset assets https://docs.unity.com/en-us/engine/6000.6/manual/assets-and-media/presets/default
- Unity e-book: Version control and project organization best practices https://unity.com/resources/version-control-project-organization-best-practices-ebook
