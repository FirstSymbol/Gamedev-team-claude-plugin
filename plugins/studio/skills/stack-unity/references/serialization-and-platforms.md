# Serialization, IL2CPP/AOT, stripping, platforms, build size

## What Unity serializes (fields on MonoBehaviour / ScriptableObject / [Serializable] class)
| Serialized | Not serialized |
|---|---|
| `public` or `[SerializeField]` non-static, non-const, non-readonly fields | properties (use `[field: SerializeField] public int Hp { get; private set; }`) |
| primitives, enums, string, Vector*/Color/Rect/AnimationCurve/Gradient/LayerMask | `Dictionary` before 6.6, `HashSet`, multi-dim/jagged arrays, nested `List<List<T>>` |
| `T[]`, `List<T>` of serializable T | interfaces/abstract types (without `[SerializeReference]`) |
| `UnityEngine.Object` refs (by GUID/fileID) | delegates, `System.Object`, `[NonSerialized]` fields |
| `[Serializable]` plain classes/structs (by value) | static/readonly fields |
- By-value classes: no polymorphism, no null (a null field is re-created as a default instance),
  no shared references, nesting depth limit 10 (cycles → warnings).
- Dictionaries: Unity 6.6+ serializes `[SerializeField] Dictionary<K,V>` natively (opt-in,
  exact type only; public without attribute → analyzer UAC1015). On 6.3 LTS and older: two lists
  via `ISerializationCallbackReceiver`, or a pair list + runtime dictionary built in `Awake`.
  Migrating: mark the old backing field `[NonSerialized]` to avoid storing data twice.
- Renames: `[FormerlySerializedAs("oldName")]` on fields (keep until all assets re-saved);
  for `[SerializeReference]` types: `[MovedFrom(true, "Old.Namespace", "OldAssembly", "OldClass")]`.
- `OnValidate` runs in Editor on load/change - keep it cheap and side-effect free (no `Instantiate`).
- Mutating ScriptableObject assets at runtime: persists in Editor, not in builds - never use as save data.

## [SerializeReference]
- Serializes managed references: polymorphism (`List<IEffect>`), real null, shared refs
  inside the same host object. Not for `UnityEngine.Object` types.
- Generic concrete types (e.g. `Effect<int>`) reportedly supported since 2023.1 (verify: not stated
  in the 6.6 SerializeReference/serialization-rules pages - test in your editor). No native inspector
  type picker: write a small `PropertyDrawer` with a type dropdown (see unity-developer editor-tooling).
- Missing type after rename/delete → data kept as "missing type" (`SerializationUtility.HasManagedReferencesWithMissingTypes`)
  - fix with `[MovedFrom]`, never by re-saving the asset blindly.
- Costlier than by-value (IDs, type names in YAML); avoid for big arrays of tiny structs.

## JSON / save formats
| Library | Pros | Cons / IL2CPP notes |
|---|---|---|
| `JsonUtility` | built-in, fast, low alloc, same rules as Unity serializer | no dictionaries, no top-level arrays, no properties, no polymorphism (except SerializeReference) |
| Newtonsoft (`com.unity.nuget.newtonsoft-json` 3.2.x) | full-featured, dictionaries, converters | reflection: needs `link.xml`/`[Preserve]`; `AotHelper.EnsureList<T>()` for generics; allocations |
| MessagePack-CSharp / MemoryPack | fast binary, source generators (AOT-safe) | schema/versioning discipline; extra package |
| Protobuf / FlatBuffers | cross-language contracts with backend | codegen step; see dotnet-backend contracts |
| `System.Text.Json` | shared with .NET backend | not shipped in Unity (bring NuGet DLLs); prefer source-gen (AOT-safe) under IL2CPP - test reflection mode on a device build |
- Save data: versioned DTOs (`int version` + migrations), never serialize MonoBehaviours;
  write temp + atomic replace in `Application.persistentDataPath`.
- `BinaryFormatter`: banned (security, obsolete in .NET).

## IL2CPP / AOT rules
- No `Reflection.Emit`, no `dynamic`, no runtime code generation; `System.Linq.Expressions`
  falls back to interpretation (slow). Prefer source generators.
- Generic virtual methods over value types can fail at runtime if never instantiated in AOT
  code; full generic sharing (2022.1+) reduces this - still test on device builds.
- Reflection-only use (serializers, DI scanning, `Type.GetType(string)`) → type is stripped → preserve it.
- Native interop: `[MonoPInvokeCallback]` on static callbacks passed to native code.
- IL2CPP Code Generation: "Faster runtime" (default) vs "Faster (smaller) builds";
  C++ Compiler Configuration: Release for QA/prod, Master for final (longer builds, best perf), Debug only to debug.
- Always test the IL2CPP player build before release - Editor runs Mono and hides AOT/stripping bugs.

## Managed code stripping
| Level | Notes |
|---|---|
| Disabled | Mono only |
| Minimal | IL2CPP default; strips only UnityEngine + .NET class libs |
| Low | marked for deprecation (6.1 docs) - don't use |
| Medium / High | strips user assemblies too; requires `link.xml`/`[Preserve]` hygiene; real size win |
```xml
<!-- Assets/link.xml (packages cannot ship their own link.xml; reference their assemblies here) -->
<linker>
  <assembly fullname="Game.Save" preserve="all"/>
  <assembly fullname="Newtonsoft.Json"><type fullname="Newtonsoft.Json.Converters.StringEnumConverter" preserve="all"/></assembly>
  <assembly fullname="Game.Core"><type fullname="Game.Core.Dto.*" preserve="fields"/></assembly>
</linker>
```
- `[Preserve]` (UnityEngine.Scripting) keeps type + default ctor; `[assembly: AlwaysLinkAssembly]` keeps an asmdef processed.
- Symptoms in device logs (logcat / Xcode): `MissingMethodException`, missing-type errors from
  serializers, `ExecutionEngineException: ... no ahead of time (AOT) code was generated`.

## Platform defines & conditional code
- Common: `UNITY_EDITOR`, `UNITY_ANDROID`, `UNITY_IOS`, `UNITY_WEBGL`, `UNITY_STANDALONE_WIN/OSX/LINUX`,
  `UNITY_SERVER`, `DEVELOPMENT_BUILD`, `ENABLE_IL2CPP`, `ENABLE_MONO`, version `UNITY_6000_3_OR_NEWER`.
- Prefer asmdef Include/Exclude Platforms + Define Constraints over large `#if` blocks;
  asmdef Version Defines (`PACKAGE_X_PRESENT` when a package version exists) for optional deps.
- Platform services behind interfaces (`IStoreService`, `IHaptics`) with per-platform implementations
  in platform-constrained asmdefs; Editor gets a fake.
- Custom defines: Player Settings → Scripting Define Symbols per Build Profile; don't hardcode in code.

## Platform specifics (2026)
### Android
- Google Play: new apps/updates must target API 36 (Android 16) from 2026-08-31 (existing apps
  ≥ API 35 to stay visible). Unity 6.3 minimum API 25. Ship AAB; ARM64 required.
- 16 KB memory page size support required by Play for Android 15+ targets; Unity 6 engine is
  compatible - audit every native plugin `.so` (check Play Console / APK Analyzer alignment warnings per build).
- Vulkan is the default graphics API for new projects; keep GLES3 fallback or use the
  Vulkan Device Filtering Asset (6.3) for bad drivers.
- Gradle 9.1 / AGP 9.0 in 6.3; custom Gradle templates break on upgrades - diff them on every editor bump.
- Big content: Play Asset Delivery (install-time/fast-follow/on-demand packs) or Addressables remote.
- Frame pacing: enable Optimized Frame Pacing; set `Application.targetFrameRate` explicitly (default 30 on mobile).
### iOS
- App Store uploads require Xcode 26+ with iOS 26 SDK (since 2026-04-28). IL2CPP + Metal only.
- Privacy manifest (`PrivacyInfo.xcprivacy`) + required-reason APIs: Unity ships one for the
  engine; every third-party SDK must provide its own. ATT prompt before IDFA.
- No hard RAM cap; OS kills on memory pressure (jetsam) - budget per device tier (performance ref).
- Post-build Xcode changes via `PBXProject` in `[PostProcessBuild]`, never by hand in the exported project.
### Web
- WebAssembly 2023 is the default target (6.5); WebGL2 remains the default graphics API, WebGPU opt-in
  (6.6 manual gives no stability label - check per-version release notes before shipping on it).
- Single-threaded by default: `Task.Run`/threads don't run in parallel, `Awaitable.BackgroundThreadAsync`
  unusable; no raw sockets (WebSockets/WebRTC), `UnityWebRequest` = browser fetch (CORS applies).
- Serve Brotli/gzip with correct `Content-Encoding` headers or enable decompression fallback.
- Audio starts only after a user gesture; mobile browsers have tight memory - test Safari iOS.
- No LZMA AssetBundles; engine bundle caching limited (see addressables ref).
### Consoles / PC storefronts
- Platform SDKs/packages under NDA from platform holders; certification rules (TRC/XR/Lotcheck) →
  studio:domain-pc-console and release-platform-manager.

## Build size playbook
1. Build, then read the Build Report in `Editor.log` (sizes by category + largest assets) or
   the Build Report Inspector / Project Auditor.
2. Usual offenders: uncompressed or oversized textures, audio as PCM/uncompressed, unused
   fonts with full glyph atlases, shader variants, duplicated Addressables assets, `Resources/`.
3. Code: Managed Stripping Medium/High + IL2CPP "Faster (smaller) builds"; remove unused
   packages and built-in modules (Package Manager → Built-in).
4. Shaders: Shader Build Settings / `IPreprocessShaders` to strip variants; URP asset features
   you don't use disabled (see technical-artist rendering ref).
5. Move optional content to remote Addressables / Play Asset Delivery; Play limits (compressed): base
   module 500 MB, install-time total 4 GB, asset pack 1.5 GB; >200 MB shows a cellular-data dialog.

## Sources
- Unity Manual: Script serialization rules https://docs.unity3d.com/Manual/script-serialization-rules.html
- Unity Manual 6.6: Dictionary serialization https://docs.unity3d.com/Manual/script-serialization-dictionaries.html
- Scripting API: SerializeReference https://docs.unity3d.com/ScriptReference/SerializeReference.html
- Unity Manual: Configure managed code stripping https://docs.unity3d.com/Manual/managed-code-stripping-configure.html
- Unity Manual: Android requirements and compatibility https://docs.unity3d.com/Manual/android-requirements-and-compatibility.html
- Unity forum: Unity support for 16 KB page sizes https://discussions.unity.com/t/info-unity-engine-support-for-16-kb-memory-page-sizes-android-15/1589588
- Google Play target API requirements https://developer.android.com/google/play/requirements/target-sdk
- Apple: Upcoming SDK minimum requirements https://developer.apple.com/news/upcoming-requirements/
- Unity Manual: Vulkan https://docs.unity3d.com/Manual/vulkan.html
- Unity Manual 6.3: What's new https://docs.unity.com/en-us/engine/current/manual/whats-new/unity63
- Google Play Console Help: Maximum size limits https://support.google.com/googleplay/android-developer/answer/9859372
- Unity Manual 6.6: WebGPU https://docs.unity.com/en-us/engine/current/manual/platform-specific/webgl/develop/graphics/web-gpu
