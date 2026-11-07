# Editor tooling (inspectors, drawers, windows, importers, validators)

## Ground rules
- All editor code in an Editor-only asmdef (`includePlatforms: ["Editor"]`, e.g. `Game.Editor` →
  references runtime asmdefs). Runtime code may use `#if UNITY_EDITOR` only for small hooks
  (`OnValidate` helpers, `[Conditional("UNITY_EDITOR")]` methods).
- UI Toolkit for new editor UI (`CreateInspectorGUI` / `CreatePropertyGUI` / `CreateGUI`);
  IMGUI only when extending legacy IMGUI tools. Default inspectors are UI Toolkit-based since 2022.2.
- Edit data through `SerializedObject`/`SerializedProperty` → free Undo, multi-object edit, prefab overrides.
  Direct field edits need `Undo.RecordObject(obj, "Label")` + `EditorUtility.SetDirty(obj)`
  (+ `PrefabUtility.RecordPrefabInstancePropertyModifications` for prefab instances).
- Type discovery: `TypeCache.GetTypesDerivedFrom<T>()` / `GetMethodsWithAttribute<T>()` (cached), never AppDomain scans.
- Long operations: `EditorUtility.DisplayCancelableProgressBar` (+ `ClearProgressBar` in finally) or `Progress` API.

## Custom inspector (UI Toolkit)
```csharp
[CustomEditor(typeof(Spawner)), CanEditMultipleObjects]
public sealed class SpawnerEditor : Editor {
    public override VisualElement CreateInspectorGUI() {
        var root = new VisualElement();
        InspectorElement.FillDefaultInspector(root, serializedObject, this);   // keep default fields
        var count = new PropertyField(serializedObject.FindProperty("count"));
        count.RegisterValueChangeCallback(_ => Validate(root));
        root.Add(new Button(() => { foreach (Spawner s in targets) s.Preview(); }) { text = "Preview spawn" });
        return root;
    }
    static void Validate(VisualElement root) { /* add/remove HelpBox */ }
}
```
- Load UXML/USS with `AssetDatabase.LoadAssetAtPath<VisualTreeAsset>(path)` or `[SerializeField]`
  default references on the editor script (set in the script's import inspector).
- Bind by `bindingPath`/`PropertyField`; call `root.Bind(serializedObject)` for elements created outside `CreateInspectorGUI`.

## PropertyDrawers (attribute + type drawers)
```csharp
public sealed class MinMaxAttribute : PropertyAttribute { public readonly float Min, Max; public MinMaxAttribute(float a, float b) { Min = a; Max = b; } }

[CustomPropertyDrawer(typeof(MinMaxAttribute))]
public sealed class MinMaxDrawer : PropertyDrawer {
    public override VisualElement CreatePropertyGUI(SerializedProperty p) {
        var a = (MinMaxAttribute)attribute;
        var slider = new MinMaxSlider(p.displayName, p.vector2Value.x, p.vector2Value.y, a.Min, a.Max);
        slider.BindProperty(p);                // Vector2 property
        return slider;
    }
}
```
- `[SerializeReference]` type picker: dropdown of `TypeCache.GetTypesDerivedFrom<IEffect>()` (non-abstract,
  `[Serializable]`), set `property.managedReferenceValue = Activator.CreateInstance(t)`, then `ApplyModifiedProperties()`.
- Drawers used inside lists must be stateless (one drawer instance may serve many elements).
- Decorators (`[Header]`-like): `DecoratorDrawer`; tooltips via `[Tooltip]`, ranges `[Range]`, `[Min]` - built-ins first.

## EditorWindow
```csharp
public sealed class ItemBrowser : EditorWindow {
    [SerializeField] string _search;                              // survives domain reload
    [MenuItem("Tools/Game/Item Browser %#i")]                     // Ctrl/Cmd+Shift+I
    static void Open() => GetWindow<ItemBrowser>("Items");
    void CreateGUI() {
        var list = new ListView(LoadItems(), 20, () => new Label(), (e, i) => ((Label)e).text = _items[i].name);
        rootVisualElement.Add(new ToolbarSearchField());
        rootVisualElement.Add(list);
    }
    List<ItemConfig> _items;
    List<ItemConfig> LoadItems() => _items = AssetDatabase.FindAssets("t:ItemConfig")
        .Select(g => AssetDatabase.LoadAssetAtPath<ItemConfig>(AssetDatabase.GUIDToAssetPath(g))).ToList();
}
```
- Refresh on data change: `EditorApplication.projectChanged`, `Undo.undoRedoPerformed`; unsubscribe in `OnDisable`.
- Editor settings: `ScriptableSingleton<T>` + `[FilePath("UserSettings/Tool.asset", FilePathAttribute.Location.ProjectFolder)]`
  (per-user) or `ProjectSettings/` (shared); expose via `SettingsProvider` in Project Settings/Preferences.
- Scene-view tools: `EditorTool` / `[Overlay]` (Unity 6 overlays, dockable) instead of `OnSceneGUI` hacks;
  `Handles` for in-scene editing, `OnDrawGizmosSelected` for debug visuals.

## MenuItem & context actions
- `[MenuItem("Tools/Game/Rebuild Item Index", priority = 100)]`; validation method:
  `[MenuItem("Tools/Game/Rebuild Item Index", true)] static bool CanRebuild() => !EditorApplication.isPlaying;`
- Shortcuts: `%`=Ctrl/Cmd, `#`=Shift, `&`=Alt, `_g`=plain key; prefer `[Shortcut]` (ShortcutManager) for rebindable keys.
- Asset context: `"Assets/Game/Generate Variants"`; component context: `"CONTEXT/Rigidbody/Reset Mass"`;
  on own components `[ContextMenu("Bake")]` / `[ContextMenuItem]` on fields.
- `ScriptableWizard` (`DisplayWizard<T>("Create Enemy", "Create")` + `OnWizardCreate`, `OnWizardUpdate`
  for validation): quick creation dialogs; use EditorWindow for anything richer.

## Asset pipeline hooks
| Need | Tool |
|---|---|
| Default import settings by folder/type | Presets + Preset Manager (no code) - owned by technical-artist |
| Enforce/derive import settings in code | `AssetPostprocessor` (`OnPreprocessTexture`, `OnPreprocessModel`, `OnPostprocessPrefab`) |
| React to imports/moves/deletes | `OnPostprocessAllAssets(imported, deleted, moved, movedFrom, didDomainReload)` |
| New file type (.csv, .ldtk, .json → SO/prefab) | `[ScriptedImporter(version, "csv")]` + `ctx.AddObjectToAsset`/`SetMainObject` |
| Batch edits | `AssetDatabase.StartAssetEditing()` … `StopAssetEditing()` in try/finally, then `SaveAssets()` |
```csharp
sealed class UiTexturePostprocessor : AssetPostprocessor {
    public override uint GetVersion() => 2;                        // bump → reimport matching assets
    void OnPreprocessTexture() {
        if (!assetPath.StartsWith("Assets/_Project/Art/UI/")) return;
        var ti = (TextureImporter)assetImporter;
        ti.textureType = TextureImporterType.Sprite; ti.mipmapEnabled = false;
    }
}
```
- Postprocessors must be deterministic and fast (run on every import, also in CI/Accelerator).
- Never `AssetDatabase.Refresh()`/`ImportAsset` inside a postprocessor callback (reentrancy, loops).
- ScriptedImporter: declare dependencies (`ctx.DependsOnSourceAsset`, `DependsOnCustomDependency`) so reimports trigger.

## Validation tools (run in Editor and CI)
- Checks worth automating: missing scripts (`GameObjectUtility.GetMonoBehavioursWithMissingScriptCount`),
  broken refs (`objectReferenceValue == null && objectReferenceInstanceIDValue != 0` on 2022/6.0; the
  InstanceID member is absent from 6.3+ SerializedProperty docs after the EntityId migration -
  verify: replacement member in your version's SerializedProperty reference),
  naming/folder rules, texture size/format rules (technical-artist budget), duplicate IDs in SO data,
  Addressables duplicate dependencies, scenes in Build Profile exist.
- Pattern: pure validators returning `List<Issue>`; called from a menu item, an EditMode test
  (fails CI), and `IPreprocessBuildWithReport.OnPreprocessBuild` (throw `BuildFailedException` to stop bad builds).
- CI entry: `-executeMethod Game.Editor.CI.ValidateAll` → `EditorApplication.Exit(issues.Count == 0 ? 0 : 1)`.
- Use Unity Search (`SearchService.Request("t:Prefab ref:...")`) for complex asset queries; cache results.

## Third-party inspector frameworks
| Tool | Notes |
|---|---|
| Odin Inspector & Validator (Sirenix, commercial) | huge attribute library, validator; per-seat licensing for every Editor user incl. artists (Personal one-time fee < $200K revenue/funding, Enterprise yearly above; Validator included only in Enterprise); Odin Serializer adds AOT generation step for IL2CPP |
| NaughtyAttributes / Tri-Inspector / Alchemy (free, OSS) | lighter attribute sets; check maintenance status |
- Adding one is a project-wide dependency → ADR; never in code shipped as a reusable package to others.
- Don't mix two attribute frameworks; prefer Unity built-ins + small custom drawers for core code.

## Checklist
- [ ] Editor code compiles out of player builds (Editor asmdef); player build verified.
- [ ] All edits undoable (SerializedObject or Undo API); prefab overrides recorded.
- [ ] Tools have a menu path under `Tools/<Game>/`, tooltips, and no blocking work on the main thread > 1 s without progress UI.
- [ ] Postprocessors versioned (`GetVersion`) and path-scoped; validators runnable from CLI.
- [ ] No `AssetDatabase` calls per-frame in `OnInspectorGUI`/`CreateGUI` loops; results cached.

## Sources
- Unity Manual: Create a custom inspector (UI Toolkit) https://docs.unity3d.com/Manual/UIE-HowTo-CreateCustomInspector.html
- Unity Manual: Property drawers https://docs.unity3d.com/Manual/editor-PropertyDrawers.html
- Scripting API: AssetPostprocessor https://docs.unity3d.com/ScriptReference/AssetPostprocessor.html
- Unity Manual: Scripted Importers https://docs.unity3d.com/Manual/ScriptedImporters.html
- Scripting API: MenuItem https://docs.unity3d.com/ScriptReference/MenuItem.html
- Scripting API: TypeCache https://docs.unity3d.com/ScriptReference/TypeCache.html
- Unity Manual: Presets https://docs.unity3d.com/Manual/Presets.html
- Scripting API 6.3: SerializedProperty (entityIdValue; no InstanceID members listed) https://docs.unity.com/en-us/engine/6000.3/script-reference/unityeditor/serializedproperty
- Odin Inspector https://odininspector.com/
- Odin Inspector pricing/licensing https://odininspector.com/pricing
