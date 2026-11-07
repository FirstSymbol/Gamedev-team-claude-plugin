# Addressables, asset bundles, Resources, memory

## Choose a loading mechanism
| Mechanism | Use when | Avoid when |
|---|---|---|
| Direct serialized reference | always-needed, small, same scene/prefab | big optional content (pulls everything into memory/build) |
| Addressables (`com.unity.addressables` 2.x on Unity 6) | optional/large content, DLC, remote/live content, memory control | tiny jam game (setup overhead) |
| Raw `AssetBundle` API | custom pipeline already exists, extreme control | new projects (Addressables wraps this with refcount + catalog) |
| `Resources/` | prototypes, a few bootstrap configs | production content: all of it ships, index built at startup, no unload granularity |
| `StreamingAssets/` | raw files (video, DB, JSON) read by path | Android: inside APK/AAB, needs `UnityWebRequest`, not `File.*` |
Rule: content needed at most in one mode at a time (levels, skins, locales) → Addressables.

## Core API (Addressables 2.x)
```csharp
[SerializeField] AssetReferenceGameObject enemyRef;   // typed, validated in inspector
AsyncOperationHandle<GameObject> _h;

async Awaitable SpawnAsync(CancellationToken ct) {
    _h = enemyRef.LoadAssetAsync();          // refcount +1 on asset & its bundles
    await _h.Task;                            // or: while (!_h.IsDone) await Awaitable.NextFrameAsync(ct);
    ct.ThrowIfCancellationRequested();
    if (_h.Status != AsyncOperationStatus.Succeeded) { Debug.LogException(_h.OperationException); return; }
    Instantiate(_h.Result, transform);
}
void OnDestroy() { if (_h.IsValid()) Addressables.Release(_h); }   // refcount -1
```
- `Addressables.InstantiateAsync` → release with `Addressables.ReleaseInstance(go)` (not `Destroy` only).
- Batch: `Addressables.LoadAssetsAsync<T>(keys, callback, MergeMode.Union)`; labels as keys.
- Scenes: `Addressables.LoadSceneAsync(key, LoadSceneMode.Additive)`; unload via `UnloadSceneAsync(handle)`.
- Pre-download: `GetDownloadSizeAsync(key)` → `DownloadDependenciesAsync(key)`; show size to user on cellular.
- Every `Load*` needs exactly one `Release`. Leaks = assets never unload; double release = errors/crash.
- Don't `await` a handle after its owner died; check `IsValid()` before release.
- `Addressables.InitializeAsync()` runs implicitly on first call; call it explicitly at boot to
  control timing and catch catalog errors.

## Group & packing strategy
| Content | Group setup |
|---|---|
| Boot/UI essentials | local, Pack Together, Prevent Updates (static) |
| Levels/chapters | one group per level or label, Pack Together By Label |
| Cosmetics/skins (growing) | remote, Pack Separately or By Label (small bundles) |
| Shared shaders/fonts/common materials | dedicated shared group (avoids duplication) |
| Locales | per-locale group (Localization package does this) |
- Bundle rule (Unity): assets loaded and unloaded together go in the same bundle; mixed
  lifetimes = memory held until the last asset in the bundle is released.
- Too many tiny bundles → larger catalog, per-bundle overhead, slower downloads; too few huge
  bundles → memory spikes. Mobile: favor many small-to-medium bundles (measure the size target per
  game with the Build Report; practitioners commonly aim ~1-10 MB on mobile).
- Duplicates: an asset referenced by two groups but not itself addressable is copied into both
  bundles (and loaded twice). Find via Addressables Build Report "potential duplicates" /
  Analyze "Check Duplicate Bundle Dependencies"; fix by making it addressable in a shared group.
- If any scene is addressable, make all non-bootstrap scenes addressable (avoids duplication
  between Build Profile scenes and bundles).
- Compression: LZ4 (128 KB chunks, partial decompress) for local bundles; LZMA (smallest,
  whole-bundle decompress) for remote download - disk cache recompresses to LZ4. Web: LZ4 only
  (no LZMA). CRC on LZ4 forces full decompress - "Excluding Cached" avoids repeat cost.
- Remote groups: enable AssetBundle Cache; CRC "Enabled, Excluding Cached".

## Memory model
- Asset refcount → bundle refcount. A bundle unloads only when all its loaded assets reach 0.
- `Resources.UnloadUnusedAssets()` frees non-referenced assets loaded outside Addressables
  (expensive: full scan, call at load screens only).
- `AssetBundle.Unload(false)` keeps loaded objects (can duplicate on reload); `Unload(true)`
  destroys them (missing textures if still referenced). Prefer Addressables release.
- Catalogs cannot be unloaded once loaded (only updated) - keep catalog count small.
- Diagnose: Memory Profiler package (snapshot compare before/after level) + Addressables
  Profiler module (Unity 6) / Event Viewer (older). Look for assets alive after their scene unloaded.
- Common leaks: forgotten handle, static list holding loaded prefabs, event subscription on a
  pooled object keeping its scene alive, `Instantiate` of loaded prefab then releasing the
  prefab while instances still use its textures (they go pink/missing).

## Content updates (live games)
1. Full release build → keep `addressables_content_state.bin` per shipped version (commit or archive with build ID).
2. Static groups: "Prevent Updates" (a.k.a. Cannot Change Post Release); dynamic: allow updates.
3. Patch: Tools → Check for Content Update Restrictions (moves changed static assets to a new
   remote group) → Build → Update a Previous Build (uses the state file).
4. Runtime: `Addressables.CheckForCatalogUpdates()` → `UpdateCatalogs()` at a safe point
   (blocks other Addressables ops; release loaded content first or enable Unique Bundle IDs).
5. Host on CDN (Unity CCD or S3/CloudFront); version paths per build; never overwrite files in place.
- Never change group update-restriction settings between the full build and its patches.
- Code changes are NOT content: new scripts/`[SerializeReference]` types require a new player build.
- Unity/Addressables version upgrade = new player + full content rebuild (CRC changes).
- Platforms: WebGL/some consoles lack engine bundle caching by default - plan updates via
  app updates or custom caching. Android large content: Play Asset Delivery
  (`com.unity.addressables.android`, 1.1.0 released for 6000.3); iOS On-Demand Resources.

## Asset hygiene checklist
- [ ] No production content in `Resources/`; any `Resources.Load` call justified in code review.
- [ ] Addressables keys are stable (address strings or `AssetReference`), not file paths that move.
- [ ] Build Report reviewed: no duplicates of large textures/meshes/shaders across bundles.
- [ ] Every load has a matching release tied to an owner lifetime (scene, screen, pool).
- [ ] Memory snapshot after returning to menu ≈ snapshot before entering level (± small delta).
- [ ] Download size shown and consented before big remote fetches; retry + offline handling.
- [ ] Content state file archived per release; content-update dry run done in staging CDN.

## Sources
- Addressables: planning and best practices (Unity blog) https://unity.com/blog/engine-platform/addressables-planning-and-best-practices
- Addressables manual (2.x) https://docs.unity3d.com/Packages/com.unity.addressables@2.2/manual/index.html
- Managing catalogs at runtime (Addressables 2.2) https://docs.unity3d.com/Packages/com.unity.addressables@2.2/manual/LoadContentCatalogAsync.html
- Content update workflow (Addressables 1.20) https://docs.unity3d.com/Packages/com.unity.addressables@1.20/manual/ContentUpdateWorkflow.html
- Unity Learn: Best practices - The Resources folder https://learn.unity.com/tutorial/assets-resources-and-assetbundles
- Unity Manual: AssetBundle compression formats https://docs.unity3d.com/Manual/AssetBundles-Cache.html
- Unity Manual: Optimizing AssetBundle memory usage https://docs.unity3d.com/6000.5/Documentation/Manual/assetbundles-optimizing.html
- Unity Manual 6.3: Addressables for Android package (released 1.1.0) https://docs.unity.com/en-us/engine/6000.3/manual/packages-list/packages-all/pack-safe/com-unity-addressables-android
