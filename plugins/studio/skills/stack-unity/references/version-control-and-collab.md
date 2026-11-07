# Version control & collaboration for Unity

## Project settings (once, verify in every repo)
- Project Settings → Editor → Asset Serialization Mode = **Force Text**; Version Control →
  Mode = **Visible Meta Files**. Binary serialization makes merges and code review impossible.
- Project Settings → Version Control → Smart merge = Premerge or Ask (default Ask).
- Commit: `Assets/`, `Packages/manifest.json`, `Packages/packages-lock.json`, `ProjectSettings/`,
  every `.meta`. Never: `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/`, `Build*/`,
  `MemoryCaptures/`, IDE files (`*.csproj`, `*.sln`, `.vs/`, `.idea/`).
- Empty folders: Unity creates a `.meta` per folder; Git drops empty dirs → orphan meta warnings.
  Delete empty folders or keep a `.gitkeep` + its meta.

## .gitignore (core lines)
```
/[Ll]ibrary/
/[Tt]emp/
/[Oo]bj/
/[Bb]uild/
/[Bb]uilds/
/[Ll]ogs/
/[Uu]ser[Ss]ettings/
/[Mm]emoryCaptures/
/[Rr]ecordings/
*.csproj
*.sln
*.pidb.meta
*.pdb.meta
*.mdb.meta
.vs/
.idea/
.DS_Store
crashlytics-buildid.txt
sysinfo.txt
*.apk
*.aab
*.unitypackage
```
Use GitHub's `Unity.gitignore` as the base; keep root-anchored paths (`/`) so nested
`Assets/**/Library` folders in packages are not ignored.

## .gitattributes (LFS + merge)
```
* text=auto
*.cs      text diff=csharp
*.unity   merge=unityyamlmerge eol=lf
*.prefab  merge=unityyamlmerge eol=lf
*.asset   merge=unityyamlmerge eol=lf
*.mat     merge=unityyamlmerge eol=lf
*.anim    merge=unityyamlmerge eol=lf
*.controller merge=unityyamlmerge eol=lf
*.meta    merge=unityyamlmerge eol=lf
# binaries -> LFS (+ lockable for exclusive checkout)
*.psd  filter=lfs diff=lfs merge=lfs -text lockable
*.png  filter=lfs diff=lfs merge=lfs -text
*.jpg  filter=lfs diff=lfs merge=lfs -text
*.tga  filter=lfs diff=lfs merge=lfs -text
*.exr  filter=lfs diff=lfs merge=lfs -text
*.fbx  filter=lfs diff=lfs merge=lfs -text lockable
*.blend filter=lfs diff=lfs merge=lfs -text lockable
*.wav  filter=lfs diff=lfs merge=lfs -text
*.mp3  filter=lfs diff=lfs merge=lfs -text
*.ogg  filter=lfs diff=lfs merge=lfs -text
*.mp4  filter=lfs diff=lfs merge=lfs -text
*.ttf  filter=lfs diff=lfs merge=lfs -text
*.otf  filter=lfs diff=lfs merge=lfs -text
*.dll  filter=lfs diff=lfs merge=lfs -text
*.so   filter=lfs diff=lfs merge=lfs -text
*.a    filter=lfs diff=lfs merge=lfs -text
*.aar  filter=lfs diff=lfs merge=lfs -text
*.unitypackage filter=lfs diff=lfs merge=lfs -text
LightingData.asset filter=lfs diff=lfs merge=lfs -text
```
- Large generated YAML (`LightingData.asset`, terrain data, NavMesh data) is effectively binary:
  LFS it and never merge - regenerate (rebake) instead.
- Add LFS rules BEFORE first commit of binaries; migrating later: `git lfs migrate import --include="*.psd,..." --everything`
  (rewrites history - human approval, coordinate force-push).
- LFS hosting quotas (GitHub bandwidth/storage) bite fast on art-heavy repos - estimate early.
- File locking: `git lfs lock Assets/Art/Hero.psd`; `lockable` makes unlocked files read-only.

## Smart merge (UnityYAMLMerge)
- Binary location: Windows `C:\Program Files\Unity\Hub\Editor\<ver>\Editor\Data\Tools\UnityYAMLMerge.exe`;
  macOS `/Applications/Unity/Hub/Editor/<ver>/Unity.app/Contents/Helpers/UnityYAMLMerge`;
  Linux `~/Unity/Hub/Editor/<ver>/Editor/Data/Tools/UnityYAMLMerge`.
```
# .git/config or ~/.gitconfig (mergetool, per Unity manual)
[merge]
    tool = unityyamlmerge
[mergetool "unityyamlmerge"]
    trustExitCode = false
    cmd = '<path>/UnityYAMLMerge' merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"
# optional merge driver so `git merge` uses it automatically (pairs with .gitattributes merge=unityyamlmerge)
[merge "unityyamlmerge"]
    name = Unity SmartMerge
    driver = '<path>/UnityYAMLMerge' merge -h -p --force %O %B %A %A
    recursive = binary
```
- `-p` premerges and opens the fallback tool only for remaining conflicts; fallback tools in
  `mergespecfile.txt` (same Tools folder); `--fallback none` disables.
- By default `.asset`, `.mat`, `.controller` go to the fallback tool; `--force` merges them as YAML.
- After any scene/prefab merge: open it in Unity, check Console for "missing prefab"/"broken
  PPtr" errors, and run the team's missing-reference validator before pushing.
- Never "resolve" a YAML conflict by picking hunks blindly in a text editor: fileIDs and
  `m_Modifications` lists must stay consistent.

## Reduce conflicts structurally
- Scenes: small and many. Additive scene composition (Bootstrap, Environment, Lighting,
  Gameplay, UI) so different people own different files.
- Prefabs: everything placed in scenes is a prefab instance; scene files hold only placement
  and overrides. Edit prefabs in Prefab Mode, not in scene instances, then apply.
- Nested prefabs: compose (Character = Body + Weapon socket + UI) so people edit separate files.
- Prefab Variants: per-variant overrides (EnemyBase → EnemyFast); keep overrides minimal; when
  overrides pile up, promote changes to the base. Audit with "Overrides" dropdown.
- Data in ScriptableObjects (one asset per item/level), not giant monolithic config assets
  or huge serialized lists in one prefab.
- Names: no spaces in paths/asset names (Unity CLI tools mishandle them - Unity e-book).
- Ownership: CODEOWNERS / team rule "one owner per scene at a time"; announce scene edits or
  use LFS locks/Unity VCS locks for scenes and key prefabs.
- Avoid noisy diffs: don't commit re-saved assets you didn't intend to change (Unity re-serializes
  on version upgrades - do upgrade re-saves in one dedicated commit).
- `ProjectSettings/` changes reviewed like code; `packages-lock.json` changes only with manifest changes.

## Branching & review
- Trunk-based with short-lived feature branches; long-lived branches + scenes = merge hell.
- PR checklist for Unity: only intended `.meta` changes (no GUID churn), no `Library/` files,
  no binary added outside LFS (`git lfs ls-files`), scenes/prefabs touched listed in PR text.
- CI: compile + EditMode tests on every PR (GameCI or self-hosted, see unity-developer testing ref).
- GUID collision check: duplicated folders copied outside Unity produce duplicate GUIDs →
  Unity reassigns one on import and silently breaks references. Copy assets inside the Editor.

## Unity Version Control (formerly Plastic SCM)
| Aspect | Git + LFS | Unity Version Control |
|---|---|---|
| Large binaries | LFS, quotas, slower clones | native, handles TB-scale repos |
| Locking | LFS locks (opt-in, server support needed) | built-in exclusive checkout (artists) |
| Artist UX | needs GUI client (Fork, GitHub Desktop) | Gluon client: file-based, no branches needed |
| Ecosystem/CI | universal (GitHub/GitLab, Actions, GameCI) | Unity Cloud/DevOps; Git sync possible |
| Cost | hosting/LFS bandwidth | seat/storage pricing (verify: current tiers on unity.com/products pricing page) |
- Pick Git+LFS for code-heavy teams already on GitHub/GitLab; Unity VCS for art-heavy teams
  needing locks and huge assets. Perforce P4 (formerly Helix Core) is the AAA/console norm.
- Decision is an ADR (tech-lead-architect + devops-sre-engineer).

## Sources
- Unity Manual 6.3: Smart merge https://docs.unity.com/en-us/engine/6000.3/manual/get-started/project-configuration/version-control/smart-merge
- Unity blog: Ultimate guide to version control & DevOps in Unity 6 https://unity.com/blog/complete-guide-version-control-devops-unity-6
- GitHub gitignore template Unity.gitignore https://github.com/github/gitignore/blob/main/Unity.gitignore
- Git LFS documentation https://git-lfs.com/
- Unity e-book "Version control and project organization best practices" https://unity.com/resources/version-control-project-organization-best-practices-ebook
- Unity DevOps product page (Version Control) https://unity.com/products/unity-devops
- Perforce P4 (Helix Core) product page https://www.perforce.com/products/helix-core
