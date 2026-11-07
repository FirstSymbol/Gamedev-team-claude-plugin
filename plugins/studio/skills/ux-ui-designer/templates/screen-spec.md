# SCR-<AREA>-<NNN> <Screen title>
v<n> <YYYY-MM-DD> <draft|review|approved> | owner: ux-ui-designer | stories: <US-NNN, ...>
Platforms: <iOS/Android/PC/console/web> | Orientation: <portrait/landscape> | Input: <touch/mouse/gamepad/keyboard>

## Purpose
- User goal: <one line> | Business goal: <one line> | Success metric: <metric + target>

## Entry / exit
- Entry: <screen/trigger> | Exit: <targets> | Back: <behavior> | Type: <full-screen/modal/overlay>

## Layout
Grid: <reference resolution, margins, columns, spacing tokens> | Safe area: <rule>
```
<ASCII wireframe: label regions with component IDs, {bindings}, <loc.keys>, * primary, ▼ focus start>
```
Responsive: <aspect ratios / breakpoints and what changes>

## Components
| ID | Type | States | Binding | Action | Notes |
|---|---|---|---|---|---|
| <id> | <type> | <default, pressed, focused, disabled, loading, empty, error> | <{field}> | <action> | <size/token> |

## Copy
| Key | Source (en) | Max chars | Context | Placeholders |
|---|---|---|---|---|
| <area.screen.element> | <text> | <n> | <where/tone> | <{name}> |

## Data bindings
| Field | Source | Format | Fallback | Refresh |
|---|---|---|---|---|

## Interaction & motion
| Trigger | Feedback | Duration/easing | Reduced-motion |
|---|---|---|---|

## Focus & navigation
- Default focus: <id> | Order: <id → id → ...> | Wrap: <yes/no>
- Gamepad: <A/Cross: ..., B/Circle: ..., LB/RB: ...> | Keyboard: <Tab/Enter/Esc>
- Narration labels: <id: role, name, value>

## Analytics
| Event | Trigger | Properties |
|---|---|---|

## Edge cases
- <offline / timeout / empty / long text / huge numbers / RTL / interrupted>

## Accessibility
- [ ] Contrast ≥ 4.5:1 text, 3:1 UI | [ ] Targets ≥ 44pt/48dp | [ ] No color-only info
- [ ] Text scales 200% | [ ] Reduced motion variant | [ ] Full gamepad/keyboard path
- Gaps: <list or none>

## Implementation notes
- Unity: <uGUI|UI Toolkit>, scaler <ref res, match>, anchors <...>, safe area <...>, TMP <fonts/fallbacks>
- Web: <component lib, breakpoints, ARIA notes>

## Open questions
- <question> → <owner>

## Changelog
- v<n> <YYYY-MM-DD>: <change>
