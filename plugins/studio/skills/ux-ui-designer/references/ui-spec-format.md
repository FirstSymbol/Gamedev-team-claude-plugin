# UI spec format (team standard)

## File and ID conventions
- One file per screen/modal: `.team/specs/<area>/ux/SCR-<AREA>-<NNN>-<slug>.md` from
  templates/screen-spec.md. AREA = 2-6 uppercase letters (`LOBBY`, `SHOP`, `HUD`, `ADM`).
- Component IDs inside a screen: `<SCR-ID>/<kebab-name>` (e.g. `SCR-SHOP-001/pack-card`).
- Shared components live in `.team/specs/ui-kit/ux/CMP-<name>.md`; screens reference them.
- Version line at top: `v<n> <YYYY-MM-DD> <status: draft|review|approved>`; changelog at bottom.

## Required sections (in order)
1. **Header**: ID, title, platforms, orientation, input methods, owner, linked stories/AC.
2. **Purpose**: user goal + business goal in one line each; success metric.
3. **Entry/exit**: from which screens/triggers; back behavior; modal or full-screen.
4. **Layout**: grid, safe area, ASCII wireframe, responsive rules (aspect ratios/breakpoints).
5. **Components**: table with states, bindings, actions.
6. **Copy**: loc keys, source text, max length, tone note.
7. **Data bindings**: field → source (API/DTO/config) → format → fallback.
8. **Interaction & motion**: per action: trigger, feedback, duration, easing, reduced-motion.
9. **Focus/navigation**: default focus, order, gamepad/keyboard mapping, narration labels.
10. **Analytics**: event name, trigger, properties.
11. **Edge cases**: offline, slow, empty, error, long text, huge numbers, RTL, small screens.
12. **Accessibility**: checklist results + known gaps.
13. **Implementation notes**: Unity or web specifics.
14. **Open questions**: question → owner.

## Layout grid
- Spacing scale on 4/8 base: 4, 8, 12, 16, 24, 32, 48, 64. Name them (`space-2` = 8).
- Mobile portrait reference 1080×1920 (9:16); test 9:19.5 (modern phones) and 3:4 (iPad).
  Landscape reference 1920×1080; test 4:3 to 21:9 (verify target device list with producer).
- Margins: ≥ 16 dp/pt mobile; content inside safe area; backgrounds full-bleed.
- ASCII wireframe rules: box per region, label with component ID, `[Button]`, `(icon)`,
  `{binding}`, `<loc.key>`, `~~~` = scroll region, `*` = primary CTA, `▼` = focus start.
```
+------------------------------------------+  SCR-SHOP-001 (portrait, safe area inside)
| (back)      <shop.title>     {coins} (+) |  top bar 56 dp, sticky
|------------------------------------------|
| [Tab: Coins*] [Tab: Gems] [Tab: Offers]  |  tabs, LB/RB cycle
|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
| +--------------+  +--------------+       |  pack-card grid 2 cols, gap 12
| | (coin art)   |  | (coin art)   |       |
| | {amount}     |  | {amount}     |       |
| | <tag.best>   |  |              |       |
| | [{price}]*▼  |  | [{price}]    |       |
| +--------------+  +--------------+       |
|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
| <shop.legal_footer>   [Restore]          |
+------------------------------------------+
```

## Component table
| ID | Type | States | Binding | Action | Notes |
|---|---|---|---|---|---|
| pack-card/buy | Button primary | default, pressed, disabled(owned), loading(purchasing), error | `{price}` ← IAP localized price | `Purchase(sku)` | debounce 1 s; min 48 dp high |
State definitions (spec only those that apply, but consider all):
| State | Must specify |
|---|---|
| default | visual priority, label |
| hover | PC/web only; never the only affordance |
| pressed | ≤ 100 ms response; scale/darken |
| focused | gamepad/keyboard outline ≥ 3:1 contrast, ≥ 2 px |
| disabled | reason visible (tooltip/inline), still focusable if reason matters |
| loading | skeleton or spinner after 300-500 ms; blocks re-submit |
| empty | explanation + next action ("No missions yet - come back at 00:00 UTC") |
| error | plain message + retry/back; error code small for support |
| success | confirmation; auto-dismiss ≥ 3 s for toasts or tap to dismiss |
| offline | cached view + banner; queue or block actions explicitly |

## Copy and localization keys
- Key format: `<area>.<screen>.<element>[.<variant>]` (`shop.pack.buy_cta`). Never reuse a key
  for a different meaning; plural forms via ICU (`{count, plural, one {# coin} other {# coins}}`).
- Columns: key | source (en) | max chars | context for translators | placeholders.
- Expansion budget: +30-40% for EN→DE/FR/RU; short strings can grow 100%+; CJK may need
  larger font size for legibility. Use auto-size with min font, or wrap; never clip.
- Numbers/currency/dates via locale formatting; compact notation for big numbers (`1.2M`) with
  full value on tap/tooltip (casino balances).
- Final wording → narrative-designer; legal strings → compliance-advisor.

## Data bindings
| Field | Source | Format | Fallback | Refresh |
|---|---|---|---|---|
| `{coins}` | `WalletDto.coins` (GET /wallet) | compact ≥ 1e6 | last cached + stale icon | on purchase, on resume |

## Analytics events
- Name `snake_case` `<object>_<action>`: `shop_opened`, `pack_purchase_started`,
  `pack_purchase_completed`, `pack_purchase_failed`. Properties: `screen_id`, `sku`,
  `price_usd_est`, `placement`, `source`, `error_code`. Final schema owner: data-analyst.
- One event per funnel step; include `screen_view` with `screen_id` for every screen.

## Edge-case checklist
- [ ] Offline at open / mid-action; server 5xx; timeout; duplicate tap; app backgrounded mid-flow.
- [ ] Empty list, 1 item, 1,000 items (pagination/virtualization).
- [ ] Longest locale string; RTL mirroring (icons with direction flip, numbers don't).
- [ ] Values: 0, negative (refund), max int, 12+ digit balances.
- [ ] Smallest supported device; largest tablet; split-screen/foldable if supported.
- [ ] Accessibility text at 200%; reduced motion; colorblind.
- [ ] Interrupted by system popup (purchase sheet, permission, call).

## Design tokens
- Tiers: primitive (`color.gold.500`) → semantic (`color.action.primary`) → component
  (`button.primary.bg`). Specs reference semantic/component tokens only.
- Format: W3C Design Tokens Community Group (DTCG) Format Module 2025.10 (first stable,
  2025-10-28); tools: Style Dictionary, Tokens Studio, Terrazzo.
```json
{
  "color": {
    "action": { "primary": { "$type": "color", "$value": "{color.gold.500}" } }
  },
  "space": { "2": { "$type": "dimension", "$value": { "value": 8, "unit": "px" } } },
  "motion": { "fast": { "$type": "duration", "$value": { "value": 150, "unit": "ms" } } }
}
```
(verify exact `$value` object shape against the 2025.10 spec before tooling)
- Unity mapping: UI Toolkit USS custom properties (`--color-action-primary`) in a theme
  `.tss`; uGUI: ScriptableObject theme + binder component. Web: CSS variables.

## Unity implementation notes (spec must state)
| Topic | Decide and write |
|---|---|
| UI system | uGUI (default runtime per Unity 6.3 docs; needed for Animator/Timeline keyframed UI, in-scene authoring) vs UI Toolkit (multi-resolution menus/HUDs, data binding, USS styling, world-space in recent 6.x) |
| Scaling | uGUI Canvas Scaler "Scale With Screen Size", reference resolution, Match 0-1 (0.5 typical; portrait games favor width=0) ; UI Toolkit PanelSettings Scale Mode equivalent |
| Anchors | per element: anchor preset + pivot; stretch for bars, corner anchors for HUD widgets |
| Safe area | `Screen.safeArea` applied to a root `RectTransform`/VisualElement, re-applied on orientation change |
| Text | TextMeshPro (in `com.unity.ugui` 2.0+ since 2023.2) or UI Toolkit TextCore; SDF font assets; fallback chain for CJK/Cyrillic/emoji; avoid Auto Size in lists (perf); RTL needs plugin for uGUI TMP (verify) |
| Batching | static vs dynamic canvases split; avoid layout groups on frequently changing elements |
| Input | EventSystem + Input System UI Input Module; navigation mode per screen |
Deep engine facts → `studio:stack-unity` (input-and-ui).

## Web admin implementation notes
- Breakpoints: ≥ 1280 primary for admin; support 1024; mobile read-only unless required.
- Component library (e.g. MUI, Ant Design, shadcn/ui, Fluent) - state which; reuse its a11y.
- Tables: sticky header, sortable columns announce sort (`aria-sort`), server pagination,
  bulk select with count, CSV export.
- Forms: inline validation on blur; submit-level error summary linked to fields.

## Figma handoff notes (when the team uses Figma)
- Agents cannot see Figma unless an MCP/export is provided; reference frames by name/link
  and keep the text spec as the source of truth for behavior.
- Name Figma components = spec component IDs; variants = states; variables = tokens.
- Dev Mode: mark frames "Ready for dev"; annotate measurements only where not tokenized.
- Code Connect maps Figma components to code snippets when configured (frontend/Unity UI).

## Sources
- Design Tokens Format Module 2025.10 https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/
- Unity Manual (6000.3), Comparison of UI systems https://docs.unity.com/en-us/engine/6000.3/manual/uitoolkits/ui-system-compare
- Unity uGUI 2.0 changelog (TMP merge) https://docs.unity3d.com/Packages/com.unity.ugui@2.0/changelog/CHANGELOG.html
- Unity Scripting API, Screen.safeArea https://docs.unity3d.com/ScriptReference/Screen-safeArea.html
- Unicode CLDR / ICU MessageFormat plural rules https://unicode-org.github.io/icu/userguide/format_parse/messages/
- Figma Dev Mode https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode
