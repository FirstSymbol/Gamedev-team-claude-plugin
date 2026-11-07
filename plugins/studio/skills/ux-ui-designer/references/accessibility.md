# Accessibility (games + web admin)

## Which standard applies
| Product | Baseline | Notes |
|---|---|---|
| Unity game, any platform | Game Accessibility Guidelines (GAG) Basic, then Intermediate | design guidance, not law |
| Xbox / PC Game Pass / Windows | Xbox Accessibility Guidelines (XAG) v3.2 (2023) | best practice; not cert requirements |
| Web admin / back-office / player web portal | WCAG 2.2 AA | legal baseline in many jurisdictions |
| Text/voice chat in games (US) | CVAA advanced communications (since 2019) | route to compliance-advisor |
| EU consumer e-commerce flows | European Accessibility Act (EAA) | see EAA note below |
Rule: never claim "compliant/certified"; write "designed against <guideline> <level>, gaps: …".

## GAG tiers (gameaccessibilityguidelines.com)
- **Basic** (easy, wide reach - do all): remappable controls; simple controls or alternative;
  UI reachable with gameplay input; adjustable sensitivity; haptics toggle; large well-spaced
  touch controls; game speed option; no flicker/repetitive patterns; self-paced text prompts;
  interactive tutorials; clear language; start game without menu chains; readable default font;
  high contrast text/UI; no info by color alone; subtitles for important speech, clear and
  readable; no info by sound alone; separate volume for SFX/speech/music; speech input never
  required; wide difficulty choice; settings saved; a11y features described in-game and on
  store page; solicit a11y feedback.
- **Intermediate** (more effort): e.g. subtitle customization (size, background), captions for
  key sounds, colorblind-friendly cues, hold-to-toggle options, adjustable timing, practice modes.
- **Advanced** (complex/niche): e.g. screen-reader support for menus, sign language, full
  audio description, one-switch play. (verify full lists on site per category)
- Categories: motor, cognitive, vision, hearing, speech, general.

## XAG numbers to design against (Microsoft Learn, verified 2026-11)
| XAG | Topic | Concrete requirement |
|---|---|---|
| 101 | Text display | min body height (descender→ascender): console 26 px @1080p (52 @4K); PC/VR 18 px @1080p (36 @4K); mobile 18 px @100 DPI, 72 px @400 DPI |
| 101 | Text scaling | up to 200% of minimum without loss; scroll in one direction only; glyph text also ≥ min |
| 101 | Spacing | ≤ 80 chars/line (40 CJK); line spacing ≥ 1.5; paragraph ≥ 2x line; letter ≥ 0.12x; word ≥ 0.16x font size; sentence case option; ≥ 1 sans-serif font |
| 102 | Contrast | text/UI vs background contrast; offer high-contrast option (verify ratios on page) |
| 104 | Subtitles/captions | speaker name on change; on by default or set before first audio; ≤ 40 chars/line, ≤ 2 lines; mixed case; background 0-100% opacity configurable; size ≥ XAG 101 min, scalable 200%; preview in settings |
| 112 | UI navigation | a11y settings reachable at first launch; full digital (d-pad/keyboard) navigation; consistent prompts (A select, B back); linear menus wrap; focus order follows visual layout; always a way back |
Other XAG topics (numbering: verify): additional visual/audio cue channels, audio
accessibility, screen narration, input/remapping, difficulty options, haptics, time limits,
photosensitivity, communication (chat), a11y settings menu.

## Vision
- Contrast: text ≥ 4.5:1, large text (≥ 18 pt or 14 pt bold) ≥ 3:1, UI components and
  meaningful graphics ≥ 3:1 (WCAG 1.4.3/1.4.11). Game text over 3D scenes: outline/shadow or
  plate behind text; test on brightest and darkest scene.
- Color vision deficiency: ~8% of men, ~0.5% of women (Northern European ancestry). Deuter-
  anomaly most common. Always pair color with shape/icon/pattern/text.
- Colorblind-safe categorical palette (Okabe-Ito): `#E69F00 #56B4E9 #009E73 #F0E442 #0072B2
  #D55E00 #CC79A7 #000000`. Avoid red/green-only win/lose or rarity tiers; rarity = color + gem
  shape + label.
- Colorblind "filters" (full-screen daltonization) are a weak substitute; prefer selectable cue
  colors for key gameplay signals (enemy outline, team color).
- Simulate: Unity has no built-in CVD sim in all versions (verify); use Color Oracle, Chrome
  DevTools "Emulate vision deficiencies", or Figma plugins on screenshots.

## Hearing
- Subtitles for all speech, captions for gameplay-relevant sounds with direction (`< footsteps`).
- Separate volume sliders: master, music, SFX, voice, UI (+ mono audio toggle).
- Slots/casino: win tiers must be visible without sound (big-win banner, not only fanfare).

## Motor
- Full remapping (keyboard, gamepad), including UI confirm/back; hold ↔ toggle option;
  adjustable QTE/timing or skip; no simultaneous multi-button chords required.
- Unity Input System supports runtime rebinding (`PerformInteractiveRebinding`) and saving
  overrides as JSON (`SaveBindingOverridesAsJson`). See studio:stack-unity input-and-ui.
- Touch: targets ≥ 44 pt / 48 dp; no precision drag-only actions; avoid long-press as sole path.

## Cognitive
- Plain language; consistent terms; one new concept at a time; objective reminder on demand;
  pause anywhere in single-player; replayable tutorials; text at own pace (no auto-advance only).
- Timers: let players extend/disable non-core timers; real-money/social casino: show session
  time and spend on request (responsible-gaming tools; see studio:domain-igaming).

## Motion and photosensitivity
- No content flashing > 3 times/s (WCAG 2.3.1, A). For console/broadcast-heavy titles run a
  Harding FPA or PEAT test on trailers/cutscenes (verify requirements per publisher).
- Provide "reduce motion": disable screen shake, camera bob, parallax, zoom bursts, flashing
  win effects; shorten transitions. Respect OS setting where available: iOS
  `UIAccessibility.isReduceMotionEnabled`, Android "Remove animations", web
  `@media (prefers-reduced-motion: reduce)`.
- Auto-moving content > 5 s needs pause/stop/hide (WCAG 2.2.2) - e.g. admin dashboard tickers.
- Camera: FOV slider (PC default 90 horizontal is common; verify per genre), motion-blur toggle.

## Screen readers / narration
- Unity: Accessibility module screen-reader API (`AccessibilityHierarchy`, `AccessibilityNode`,
  `AssistiveSupport`) for iOS VoiceOver / Android TalkBack since 2023.2; desktop support
  newer (verify per Unity 6.x release notes). Otherwise: menu narration via TTS plugin.
- Spec narration labels per component (role, name, value, hint) in the screen spec.

## WCAG 2.2 AA checklist for web admin panels
- [ ] All function by keyboard (2.1.1); no keyboard trap (2.1.2); visible focus (2.4.7).
- [ ] Focus not hidden by sticky headers/toasts (2.4.11 AA, new in 2.2).
- [ ] Targets ≥ 24×24 CSS px or spaced (2.5.8 AA, new); drag actions have click alternative (2.5.7 AA, new).
- [ ] Contrast 4.5:1 text, 3:1 large text and UI parts (1.4.3, 1.4.11); reflow at 320 CSS px (1.4.10).
- [ ] Text resize 200% without loss (1.4.4); text spacing override safe (1.4.12).
- [ ] Form labels + instructions (3.3.2); errors identified in text with suggestion (3.3.1, 3.3.3).
- [ ] Don't re-ask entered data in same process (3.3.7 A, new); login without cognitive test,
      allow paste/password managers (3.3.8 AA, new); help in consistent place (3.2.6 A, new).
- [ ] Data tables with `<th scope>`; status messages via `aria-live` (4.1.3); name/role/value (4.1.2).
- [ ] Session timeouts warn and allow extension (2.2.1).
- 4.1.1 Parsing was removed in 2.2. Test: axe DevTools/Lighthouse (catches ~30-40% of issues;
  verify) + manual keyboard + screen-reader pass (NVDA/VoiceOver).

## European Accessibility Act (EAA) note
- Directive (EU) 2019/882 applies since 2025-06-28. Video games are not a listed product, but
  in-scope services can touch games: e-commerce (buying in apps/web stores), consumer
  banking/payments, electronic communications (chat). Interpretation for in-game purchases is
  contested (verify with compliance-advisor; needs human legal review).
- Microenterprises providing services (< 10 staff and ≤ EUR 2M turnover/balance) are exempt;
  document the assessment.
- Practical target for web/admin/store checkout: EN 301 549 (≈ WCAG 2.1 AA; WCAG 2.2 alignment
  in progress, verify) - designing to WCAG 2.2 AA covers it.

## Accessibility settings menu (spec checklist)
- First-launch prompt (or defaults meeting guidelines); reachable from title and pause.
- Sections: Text (size, background, font), Subtitles/captions, Color (cue colors, contrast),
  Audio (mixer, mono, visual cues), Controls (remap, toggle/hold, sensitivity, aim assist),
  Motion (shake, blur, flashes, FOV), Difficulty/assist, Narration.
- Live preview for subtitle/text changes; all settings persisted and cloud-synced if accounts.

## Sources
- Game Accessibility Guidelines https://gameaccessibilityguidelines.com/
- Xbox Accessibility Guidelines (v3.2) https://learn.microsoft.com/en-us/gaming/accessibility/guidelines
- XAG 101 Text display https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/101
- XAG 104 Subtitles and captions https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/104
- XAG 112 UI navigation https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/112
- WCAG 2.2 (W3C Recommendation) https://www.w3.org/TR/WCAG22/
- M. Okabe & K. Ito, "Color Universal Design (CUD): How to make figures and presentations that are friendly to colorblind people" (2002, rev. 2008)
- IGDA GA-SIG, "Demystifying EAA & GPSR" https://igda-gasig.org/what-and-why/demystifying-eaa-gpsr/
- Taylor Wessing, "Accessibility in the gaming industry" (2025-03) https://www.taylorwessing.com/en/insights-and-events/insights/2025/03/accessibility-in-the-gaming-industry
