# Game UI patterns

## HUD taxonomy (Fagerholt & Lorentzon, "Beyond the HUD", Chalmers 2009)
| Type | In game fiction? | In game space? | Example | Use when |
|---|---|---|---|---|
| Diegetic | yes | yes | ammo counter on gun, wristwatch map | immersion-first, info is glanceable |
| Non-diegetic | no | no | health bar overlay, coin counter | clarity-first; default for mobile/casino |
| Spatial | no | yes | nameplates, waypoint markers, outline | info tied to a world position |
| Meta | yes | no | blood splatter at screen edge, cracked visor | state felt rather than read |
- HUD rules: show only what drives the next decision; peripheral info in corners, critical
  center-near; fade non-critical elements in calm moments; let players scale/hide HUD (GAG).
- Priority stack: survival/fail-state > objective > resources > social > cosmetics.
- Every HUD number that changes: animate delta at source → fly to counter → tick (≤ 600 ms).

## Menus and navigation depth
- Hub-and-spoke for F2P/casino lobbies; tab bar ≤ 5 items mobile; PC/console top tabs with
  LB/RB (L1/R1) cycling.
- Depth: frequent actions ≤ 2 interactions from hub; never > 4 for any player task.
- Back is always available and predictable: hardware back (Android), B/Circle, Esc.
  Android back on root screen → confirm-exit dialog, not instant quit.
- Modals: only for blocking decisions; one at a time; queue the rest (popup manager with
  priority + cap per session, e.g. ≤ 3 unsolicited popups at launch).
- Start the game without menu chains (GAG basic): "Continue" is the default focus on title.

## Store / shop UX (F2P, social casino)
| Element | Rule |
|---|---|
| Price | platform-localized string (`Product.metadata.localizedPriceString` in Unity IAP); never hard-code "$" |
| Value | show amount, bonus % vs base pack, per-unit price only if accurate |
| Tags | "Best value"/"Most popular" must be true (consumer law); max 1-2 tags per screen |
| Layout | 3-6 packs visible; anchor high pack first or center the target pack |
| Confirm | platform sheet is the confirmation; add own confirm only for premium-currency spends above a threshold |
| States | idle / processing (block double-tap) / pending (deferred, Ask to Buy) / success (grant animation) / failed (reason + retry) / restored |
| Restore | non-consumables/subscriptions need "Restore Purchases" on iOS (verify: App Store Review Guidelines 3.1.1) |
| Odds | randomized paid items: disclose odds before purchase (Apple 3.1.1, Google Play policy; verify current text) |
| Timers | countdowns must be real; no reset-on-relaunch fake urgency |
| Insufficient funds | inline shortfall ("Need 1,200 more") + direct path to the right pack |
- Social casino: coins are not cashable - copy must never imply real-money value or winnings;
  see studio:domain-igaming and route copy to compliance-advisor.

## Reward and celebration screens
- Tiered intensity proportional to value; define tiers as data (e.g. small < 5x bet, big
  ≥ 10x, mega ≥ 25x, epic ≥ 50x - tune with economy-monetization-designer).
- Duration budget: small ≤ 1 s, big 2-4 s, top tier ≤ 8 s; first tap accelerates count-up,
  second tap skips to final value. Never block input > 1 s without skip.
- Sequence: anticipation → reveal → count-up → collect CTA → fly-to-counter → counter tick.
- Collect button appears after reveal; auto-collect on timeout for chained rewards.
- Real-money gambling (UKGC RTS 14F): no win celebration when return ≤ stake. Apply the same
  rule in social casino as good practice.
- Reduced-motion variant: no screen shake/flash, shorter count-up, static burst.

## Notification badges
| Badge | Meaning | Clear rule |
|---|---|---|
| Dot | something new, not quantified | clears on opening the destination |
| Count | N actionable items | decrements as items are handled; cap "99+" |
| "!" | requires action (claim, expired soon) | clears when actioned |
- Only actionable items badge; bubble up to parent tab; never badge ads/offers on every launch
  (badge blindness). Badge = color + shape (not color alone).

## Controller / gamepad navigation
- Every screen has: default focus element, focus order map, wrap rules, back action.
- Focus must be visible: outline/scale ≥ 3:1 contrast against both states (WCAG 2.4.13 analog).
- Platform confirm/back: Xbox A/B; PlayStation Cross/Circle (PS5 standard in all regions);
  Switch A (right)/B (bottom). Show glyphs for the active device; switch on last input.
- Grids: d-pad moves cell-to-cell; LB/RB switch tabs; LT/RT page; Y/Triangle secondary action.
- Unity uGUI: `Selectable.navigation` Explicit for non-grid layouts (Automatic breaks on
  irregular layouts); `EventSystem.SetSelectedGameObject` on screen open; restore last focus on back.
- Unity UI Toolkit: `focusable = true`, `tabIndex`, `element.Focus()`; handle
  `NavigationMoveEvent`/`NavigationSubmitEvent`/`NavigationCancelEvent`. (verify per Unity version)
- Mouse + gamepad on PC: hover moves focus; hide cursor on gamepad input.
- Text entry with gamepad: platform virtual keyboard; avoid required typing.

## Mobile touch layout
| Rule | Value / source |
|---|---|
| Min target iOS | 44 × 44 pt (Apple HIG) |
| Min target Android | 48 × 48 dp, ≥ 8 dp apart (Material / Android a11y) |
| Web admin min | 24 × 24 CSS px or spacing equivalent (WCAG 2.2 SC 2.5.8, AA) |
| Game virtual controls | larger than minimum; GAG basic: "large and well spaced" |
| One-handed use | ~49% of observed phone use is one-handed (Hoober 2013) |
- Thumb zone (portrait, one hand): bottom-center = easy; top corners = hard. Primary CTA
  (Spin, Play, Collect) bottom-center; destructive/rare actions top.
- Landscape two-thumb games: left = movement, right = actions; keep center clear for view.
- Safe area: all interactive and critical text inside `Screen.safeArea`; backgrounds bleed
  to full screen. Home indicator zone: no swipe-up gestures at bottom edge.
- Gestures always have a visible button alternative (WCAG 2.5.7 dragging; GAG simple controls).
- Hit area can exceed visual size (padding/invisible raycast target) - spec both.

## Feedback timing
| Event | Response |
|---|---|
| Tap/press | visual state change ≤ 100 ms (perceived instant); haptic optional, toggleable |
| Server action | spinner after 300-500 ms, not before (avoid flash); timeout + retry at ~10 s |
| Long load | progress bar + tip; > 10 s show cancel/back where possible |
| Number change | count-up 300-800 ms scaled by magnitude |
Thresholds follow NN/g response-time limits (0.1 s / 1 s / 10 s).

## Common screen archetypes (spec checklist)
- Lobby/hub, gameplay HUD, pause, settings (incl. accessibility tab), shop, offer popup, reward,
  inventory/collection, leaderboards, profile, daily login/mission list, event hub,
  error/maintenance, force-update, loading, legal/consent (GDPR/ATT pre-prompt).
- Admin web: list (filter/sort/paginate/export), detail, edit form (validation), audit log,
  bulk action with confirm, dashboard.

## Sources
- E. Fagerholt & M. Lorentzon, "Beyond the HUD: User Interfaces for Increased Player Immersion in FPS Games", MSc thesis, Chalmers 2009 (no URL verified)
- Apple Human Interface Guidelines, Accessibility https://developer.apple.com/design/human-interface-guidelines/accessibility
- Android accessibility, Touch target size https://support.google.com/accessibility/android/answer/7101858
- WCAG 2.2 https://www.w3.org/TR/WCAG22/
- Steven Hoober, "How Do Users Really Hold Mobile Devices?" UXmatters 2013 https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php
- NN/g, "Response Times: The 3 Important Limits" https://www.nngroup.com/articles/response-times-3-important-limits/
- Game Accessibility Guidelines https://gameaccessibilityguidelines.com/
