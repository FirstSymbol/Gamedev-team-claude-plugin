---
name: stack-unity
description: Shared Unity engine knowledge - Unity 6 versions, assets/Addressables, input/UI, serialization, IL2CPP/platforms, VCS, render pipelines, batch-mode/MCP verification.
---
# Unity stack (shared knowledge)
Mission: one source of engine truth for every role touching a Unity project; roles link here
instead of restating engine facts.

## Version baseline (as of 2026-11)
| Line | Type | Support | Use |
|---|---|---|---|
| 6.0 (6000.0) | LTS | ended Oct 2026 | upgrade to 6.3 LTS; no new projects |
| 6.3 (6000.3) | LTS | to Dec 2027 (+1y Enterprise) | default for production / shipping |
| 6.4-6.6 | Update ("Supported") | until next release | opt-in for needed features |
| 6.7 | next LTS, late 2026; still Beta in docs selector as of 2026-11-07 | (verify: GA date + LTS end on unity.com/releases) | last Mono release; experimental CoreCLR Desktop Player + IL2CPP iOS player |
| 7.0 | alpha since 2026-10-05, no release date | - | CoreCLR Editor, Mono removed (was announced as 6.8); alphas still C# 9 / .NET Std 2.1, .NET 10/C# 14 undated |
- Always respect `ProjectSettings/ProjectVersion.txt`; never bump the editor version without an ADR
  (tech-lead-architect). Check docs for the exact `6000.x` line: `docs.unity3d.com/6000.3/...`.
- Scripting today: Mono/IL2CPP, C# 9, API compatibility .NET Standard 2.1 or .NET Framework.
### Changed vs 2022 LTS (what old habits break)
- Async: `Awaitable` (pooled, main-thread) + `destroyCancellationToken`; see async refs in unity-developer.
- URP: Render Graph is the only path for custom passes (Compatibility Mode removed in 6.4);
  Forward+, GPU Resident Drawer, GPU occlusion culling, APV, STP upscaler.
- Deprecations: Built-in RP deprecated in 6.5 (supported through 6.7 LTS); dynamic batching
  deprecated 6.5; HDRP in maintenance (no new features); legacy Input Manager deprecated.
- API renames: `Rigidbody.velocity`→`linearVelocity`, `drag`→`linearDamping`;
  `FindObjectsOfType`→`FindObjectsByType`; `InstanceID`→`EntityId` (obsolete errors from 6.5).
- Workflow: Build Profiles replace Build Settings; Fast Enter Play Mode (no domain reload)
  default from 6.6 - statics must be reset explicitly.
- UI Toolkit: runtime data binding (6.0), world-space UI (6.2), USS filters (6.3).
- Android min API 25 (6.3); Web defaults to WebAssembly 2023 (6.5); Unity AI replaced Muse (6.2).

## Rules that always apply
- **Meta/GUID**: every asset has a `.meta` with its GUID; references are by GUID. Commit
  `.meta` with its asset; move/rename inside the Editor (or move the `.meta` too); never
  delete/regenerate metas; duplicate GUIDs = silent broken refs.
- **Never commit/read**: `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/`, `Build*/`,
  `*.csproj`, `*.sln`. `Library/` is a cache - deleting it forces a full reimport (slow, safe).
- **Asset Serialization = Force Text** and Visible Meta Files (VCS-friendly; see vcs ref).
- **Serialization basics**: fields that are `public` or `[SerializeField]`, non-static,
  non-readonly; no properties (use `[field: SerializeField]`), no `Dictionary` before 6.6, no
  polymorphism without `[SerializeReference]`; renames need `[FormerlySerializedAs]`.
- **Main thread**: all `UnityEngine.Object` APIs on the main thread only. Background work =
  plain C#, Jobs/Burst on NativeContainers, or `Awaitable.BackgroundThreadAsync()` then back.
- **Unity null**: destroyed objects `== null` but are not C# null; never `?.`/`??`/`is null`
  on `UnityEngine.Object`.
- **Editor-only code**: `UnityEditor` APIs only in Editor asmdefs or `#if UNITY_EDITOR`;
  otherwise the player build fails.
- **Scene/prefab YAML**: do not hand-edit beyond trivial scalar fields; use editor scripts
  (`-executeMethod`) or give exact Editor steps.
- **Verification without GUI**: compile + tests via batch mode; read `Editor.log`
  (references/ai-tooling.md). Never claim "works" without a log or test result.
- **Discovery**: run team-protocol `scan_unity_project.py` before reading project files.

## References (read on demand)
- references/addressables-and-assets.md — loading/unloading content, Addressables groups,
  bundles, Resources removal, memory leaks from assets, remote content updates.
- references/input-and-ui.md — Input System setup, rebinding, UI Toolkit vs uGUI choice,
  TextMeshPro/text, safe areas, localization (writing loc-ready strings: `studio:narrative-designer`).
- references/serialization-and-platforms.md — serialization edge cases, SerializeReference,
  JSON, IL2CPP/AOT/stripping, platform defines, Android/iOS/Web/console specifics, build size.
- references/version-control-and-collab.md — Git LFS, .gitattributes, smart merge, prefab
  workflow to avoid conflicts, Unity Version Control.
- references/rendering-and-pipelines.md — choosing BiRP/URP/HDRP, SRP Batcher, GPU Resident
  Drawer, Render Graph, lighting/baking basics (deep shader work: studio:technical-artist).
- references/ai-tooling.md — Unity AI, Unity MCP servers, batch-mode CLI, logs, how an agent
  verifies Unity work without the GUI.

## Sources
- Unity forum: CoreCLR, Scripting and .NET update, October 2026 https://discussions.unity.com/t/coreclr-scripting-and-net-update-october-2026/1738338
- Unity forum: CoreCLR, Scripting and ECS status update (March 2026) https://discussions.unity.com/t/coreclr-scripting-and-ecs-status-update-march-2026/1711852
- Unity releases: Unity 6 releases (LTS support windows) https://unity.com/releases/unity-6-releases
- Unity Manual 6.2: What's new https://docs.unity3d.com/6000.2/Documentation/Manual/WhatsNewUnity62.html
