# Input System, UI Toolkit vs uGUI, text, safe areas, localization

## Input System (`com.unity.inputsystem` 1.x)
- Player Settings → Active Input Handling = "Input System Package (New)". "Both" only during
  migration (legacy Input Manager is deprecated in Unity 6 and will be removed).
- Unity 6 default: project-wide actions asset `InputSystem_Actions` (Project Settings → Input
  System Package), preloaded and auto-enabled; access via `InputSystem.actions`.
- Wiring options:
| Option | Use when | Notes |
|---|---|---|
| Project-wide actions + `FindAction` cached in `Awake` | most single-player games | no asset refs to pass around |
| Generated C# class ("Generate C# Class") | type safety, many actions | regenerate on asset change; own the instance |
| `PlayerInput` component | local multiplayer, quick prototypes | reflection/SendMessage modes are slow and string-based; use C# events mode |
| `InputActionReference` fields | designer-wired per prefab | must `Enable()` non-project-wide actions |
```csharp
InputAction _move, _jump;
void Awake() { _move = InputSystem.actions.FindAction("Player/Move", throwIfNotFound: true);
               _jump = InputSystem.actions.FindAction("Player/Jump", true); }
void Update() {
    Vector2 m = _move.ReadValue<Vector2>();          // polling: no alloc, frame-coherent
    if (_jump.WasPressedThisFrame()) Jump();
}
```
- Action maps per context (`Player`, `UI`, `Vehicle`); switch with `map.Disable()/Enable()`,
  never by `if (inMenu) return;` sprinkled in handlers.
- Callbacks (`performed += …`): unsubscribe in `OnDisable`; `ctx.ReadValue<T>()` only inside callback.
- Physics-driven input: Input Settings → Update Mode = Process Events In Fixed Update, or
  sample in `Update` and consume in `FixedUpdate` (don't lose taps between fixed steps).
- Rebinding: `action.PerformInteractiveRebinding().WithCancelingThrough("<Keyboard>/escape")
  .OnComplete(op => op.Dispose()).Start()`; persist `actions.SaveBindingOverridesAsJson()`;
  restore with `LoadBindingOverridesFromJson` at boot. Disable the action during rebind.
- Touch: `EnhancedTouchSupport.Enable()` + `Touch.activeTouches`; on-screen controls
  (`OnScreenStick`, `OnScreenButton`) feed virtual gamepad bindings.
- UI: EventSystem needs `InputSystemUIInputModule` (not `StandaloneInputModule`).
- Device changes: `InputSystem.onDeviceChange`; show correct glyphs per active control scheme
  (`PlayerInput.currentControlScheme` or last used device).
- Consoles: user pairing (`InputUser`) and platform-specific packages; see studio:domain-pc-console.

## UI system decision (Unity 6.3 manual)
| Need | Pick |
|---|---|
| Editor tools, inspectors, property drawers | UI Toolkit (IMGUI only for quick/legacy) |
| Runtime screen-space menus, HUD, large data-driven UI, designer CSS-like workflow | UI Toolkit |
| Keyframed Animation/Timeline-driven UI, in-scene authoring, serialized UnityEvents | uGUI |
| Existing uGUI project / asset-store UI kits | uGUI (don't mix without reason) |
| World-space diegetic UI | uGUI (mature) or UI Toolkit world space (added 6.2; newer - prototype first) |
- Unity's own recommendation table (6.3): runtime → uGUI recommended, UI Toolkit alternative;
  editor → UI Toolkit recommended. UI Toolkit evolves fast; uGUI is mature/slow-moving.
- Mixing is allowed (UITK HUD + uGUI world-space), but one input/navigation owner per screen.

## uGUI performance rules
- Any change inside a Canvas rebuilds that Canvas' batches → split static vs dynamic
  elements into separate (nested) Canvases; HUD timers in their own Canvas.
- Turn off `Raycast Target` on non-interactive Graphics/TMP text; fewer GraphicRaycasters.
- Avoid nested Layout Groups/ContentSizeFitters on frequently changing content; lay out once,
  then disable the layout component, or position manually.
- Hide screens with `Canvas.enabled = false` / `CanvasGroup.alpha=0 + blocksRaycasts=false`
  instead of `SetActive` toggling on large hierarchies (avoids OnEnable/rebuild cost).
- Long lists: pooled/virtualized scroll views (recycle rows), never instantiate 1000 rows.
- Fullscreen transparent images and stacked panels = overdraw; disable cameras behind
  opaque fullscreen UI. Masks: `RectMask2D` cheaper than stencil `Mask` for rectangles.
- Set `Canvas.worldCamera` for Screen Space-Camera/World canvases (else `Camera.main` lookups).

## UI Toolkit rules
- Author UXML + USS in UI Builder; logic in plain C# controllers (query once: `root.Q<Button>("play")`).
- Data: runtime data binding (`dataSource`, `SetBinding`) for plain C# view models; in editor
  UI prefer `SerializedObject` binding. Property bags are reflection-generated on first access.
- Lists: `ListView`/`MultiColumnListView` with `makeItem`/`bindItem` (virtualized; fixed item height fastest).
- Styling: USS classes over inline styles; avoid deep descendant selectors and `:hover`
  on huge trees; toggle classes (`EnableInClassList`) rather than rewriting style values.
- Animated elements: `usageHints = UsageHints.DynamicTransform` and animate `style.translate/scale`,
  not layout properties (`left/width` trigger layout).
- PanelSettings: Scale Mode = Scale With Screen Size; reference resolution from UX spec.
- Testing: UI Test Framework package (6.3) for automated interaction tests.

## Text (TextMeshPro / TextCore)
- TMP lives in `com.unity.ugui` 2.x since 2023.2 (the standalone `com.unity.textmeshpro` is deprecated).
- SDF font assets: static atlas for known glyph sets (Latin UI), dynamic + fallback chain for
  user content/CJK; clear dynamic atlas data before committing (avoids huge diffs).
- CJK: separate fallback font assets per language, loaded with the locale (Addressables).
- No-alloc updates: `tmp.SetText("{0:0}", score)` instead of string concat/interpolation each frame.
- RTL/complex shaping (Arabic, Hindi): TMP has no HarfBuzz-based shaping - budget for a plugin,
  or use UI Toolkit Advanced Text Generator (HarfBuzz + ICU + FreeType; 6.3 manual).

## Safe areas and screens
- Read `Screen.safeArea` (pixels) and `Screen.cutouts`; re-apply on resolution/orientation change.
- uGUI: a `SafeArea` RectTransform under the Canvas, anchors = safeArea / screen size.
- UI Toolkit: convert with `RuntimePanelUtils.ScreenToPanel` and set root padding.
- Test in Device Simulator (notches, cutouts, aspect ratios) and on at least one real notched device.
- Aspect coverage: 4:3 tablet → 21:9 phone; foldables / Android 16 large screens (6.3 App Category).

## Localization (`com.unity.localization` 1.5.x; 1.5.14 latest as of 2026-11-05)
- String Tables (text) + Asset Tables (sprites, audio, fonts per locale); tables are Addressables.
- In code: `LocalizedString` field + `StringChanged` event or `GetLocalizedStringAsync()`;
  in UI: `LocalizeStringEvent` (uGUI) or UI Toolkit binding to `LocalizedString`.
- Smart Strings for plurals/gender/variables (`{count:plural:One item|{} items}`); never concat translated fragments.
- Keys: stable semantic IDs (`shop.buy_button`), not English text; add translator comments.
- Pipeline: CSV / Google Sheets / XLIFF extensions; pseudo-localization locale to catch
  truncation (+30-40% length) and hard-coded strings before translators start.
- Preload tables used on the first screen (`Preload` flag) to avoid flashes of keys.
- Formatting: numbers/dates/currency via locale `CultureInfo`; IL2CPP needs culture data
  (keep invariant globalization off if localizing formats).

## Checklist
- [ ] One input path (Input System), action maps per context, rebinding persisted.
- [ ] UI choice recorded (ADR if mixing systems); UX spec reference resolution in PanelSettings/CanvasScaler.
- [ ] No per-frame text allocations; dynamic canvases split; Raycast Target off on decor.
- [ ] Safe area applied and tested on notched + tablet aspect.
- [ ] All user-facing strings in String Tables; pseudo-loc pass done; CJK fallback fonts present.

## Sources
- Unity Manual 6.3: Comparison of UI systems https://docs.unity.com/en-us/engine/6000.3/manual/uitoolkits/ui-system-compare
- Input System: Project-wide actions https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/about-project-wide-actions.html
- Unity Manual: Input Manager (legacy, deprecated) https://docs.unity3d.com/6000.3/Documentation/Manual/InputLegacy.html
- Unity Manual: UI Toolkit runtime data binding https://docs.unity3d.com/Manual/UIE-runtime-binding.html
- Unity blog: Some of the best optimization tips for Unity UI https://unity.com/how-to/unity-ui-optimization-tips
- uGUI 2.0 changelog (TMP merge) https://docs.unity3d.com/Packages/com.unity.ugui@2.0/changelog/CHANGELOG.html
- Localization package manual https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/index.html
- Localization changelog (1.5.14) https://docs.unity3d.com/Packages/com.unity.localization@1.5/changelog/CHANGELOG.html
- Screen.safeArea API https://docs.unity3d.com/ScriptReference/Screen-safeArea.html
- Unity Manual 6.3: Advanced Text Generator https://docs.unity.com/en-us/engine/6000.3/manual/uitoolkits/uielements/uie-work-with-text/uie-advanced-text-generator
