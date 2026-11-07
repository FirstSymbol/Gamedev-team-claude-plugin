# Visual direction

## Style guide (art bible) structure
1. **Pillars**: 3 adjectives + one-line meaning + do/don't image pair each
   (e.g. "Warm - saturated midtones, soft rim light; not neon, not desaturated grit").
2. **Shape language**: primary shape per category (heroes, enemies, props, UI, symbols).
3. **Proportion & scale**: character heads-tall, prop scale vs character, UI corner radii.
4. **Color**: master palette (hex), per-area/per-feature color scripts, accent rules, value ranges.
5. **Value**: foreground/midground/background value bands; focal point brightest/highest contrast.
6. **Lighting mood**: key light direction/color temperature, rim/fill ratios, time-of-day script.
7. **Materials & texture**: surface vocabulary (painted, PBR stylized), detail density, edge wear.
8. **Line & edge**: outlines yes/no, weight by distance, hard vs soft edge rules.
9. **UI art style**: frames, buttons, icon style (fill/outline, perspective, light direction), fonts.
10. **VFX style**: shape (sharp/soft), palette subset, timing feel - with technical-artist.
11. **Camera & composition**: FOV, framing rules, safe zones for UI.
12. **References**: boards described in words + source links; mark "inspiration only".
13. **Do/Don't gallery** and **review checklist**.
Keep it ≤ 20 pages; every rule testable on a screenshot.

## Shape language (conventional associations - validate per audience)
| Shape | Reads as | Use |
|---|---|---|
| Circle/soft curves | friendly, safe, playful | heroes in casual, collectibles, rewards |
| Square/blocky | stable, strong, trustworthy | tanks, structures, UI panels |
| Triangle/spikes | danger, speed, aggression | enemies, hazards, warnings |
- Mix with a dominant shape (≈ 60-70%) + secondary + accent; avoid equal mixes (no read).
- Silhouette test: fill black at gameplay size; each class must be identifiable.

## Color and value rules
- Value first: a scene must read in grayscale; check by desaturating screenshots.
- Limit hue families per screen (dominant + secondary + accent); accent reserved for
  interaction/reward.
- Saturation hierarchy: gameplay-critical > interactive > background. Backgrounds lower
  saturation and contrast to free the foreground.
- Color script: strip of thumbnails per level/feature/session state showing mood progression.
- Colorblind: test deuteranopia/protanopia/tritanopia sims; pair hue with shape/pattern (see
  ux-ui-designer references/accessibility.md for palette).
- UI over art: text plates or outlines; contrast 4.5:1 for text (WCAG-derived target).

## Lighting mood
- Define key/fill/rim per mood (e.g. "victory: warm key 3200 K-ish, high key, soft shadows").
- Lighting supports focal hierarchy; brightest value near gameplay focus, not at frame edges.
- Mobile: fake lighting in textures/vertex color when real-time budget is low (technical-artist).

## Critique / review framework (order matters)
| Pass | Question | Typical fixes |
|---|---|---|
| 1 Readability | Does it read at gameplay size, in motion, in grayscale? | silhouette, value contrast, simplify detail |
| 2 Function | Does it communicate its gameplay role (danger, reward, interactive)? | shape language, accent color |
| 3 Consistency | Does it match pillars, palette, light direction, detail density? | palette swap, edge style |
| 4 Craft | Anatomy, perspective, materials, topology/UV (tech-art) | paint-over, redline |
| 5 Polish | Micro-detail, secondary animation, FX accents | only after 1-4 pass |
- Note format: `#n [P1|P2|P3] <area>: <observation> → <requested change> (ref: <guide §>)`.
- P1 = blocks acceptance; P2 = must fix before final; P3 = nice to have. Max ~10 notes/round.
- Paint-over/redline described in words when you cannot draw: give coordinates/regions,
  value targets ("darken background to ~30% value"), and reference examples.
- Separate taste from rule: if it is not in the brief or guide, label it "suggestion".

## Casino / slot art specifics
### Symbol hierarchy (typical 5x3 video slot)
| Tier | Count (typical) | Visual treatment |
|---|---|---|
| Special: Wild, Scatter, Bonus | 2-3 | unique frame/shape, text label ("WILD"), strongest contrast, animated idle |
| High-pay | 4-5 | themed characters/objects, richest color + detail, largest silhouette |
| Low-pay | 4-6 | royals (A K Q J 10 9) or gems/suits; simpler, lower saturation, uniform style |
- Legibility test: render reel cell at smallest supported device size (often ~80-120 px cell
  height on phones; verify per layout); all symbols identifiable in < 0.5 s by testers.
- No two symbols share dominant hue + silhouette; distinguish by both.
- Winning-line highlight must not hide symbols; non-winning symbols dim (≈ 40-60% brightness).
- Symbol states: idle, blur (spin), land/bounce, win animation, dimmed, (sticky/expanded wild).
- Paytable art reuses symbol art at legible size; values shown in coins and/or bet multipliers.

### Win celebration tiers
- Tier thresholds are data (owned by economy-monetization-designer), e.g. Big ≥ 10x bet,
  Mega ≥ 25x, Epic ≥ 50x; art/audio intensity scales per tier (overlay size, coin shower
  density, music sting length).
- Escalation sequence: line win flash → rollup counter → tier banner upgrade (Big → Mega) as
  value crosses thresholds → collect.
- Durations: small wins ≤ 1-1.5 s; tier celebrations ≤ ~6-8 s; tap to fast-forward/skip.
- Regulatory: UKGC RTS 14F (from 2021-10-31) forbids celebrating returns ≤ stake in online
  slots; real-money products in other markets: check (studio:domain-igaming, compliance-advisor).
  Social casino: apply the same rule by default.
- Near-miss/anticipation effects (scatter landing slowdown) are sensitive in some markets
  (verify per jurisdiction); never fake near misses beyond actual math outcomes.

### Theme research
- Inventory 10-20 competitor titles in the theme: palette, symbol set, bonus visuals, what feels
  generic. Pick a differentiating angle (setting, art technique, character).
- Popular theme families (Egypt, fruits/classic, Asian luck, wild west, mythology, animals):
  originality comes from execution; avoid trade dress of famous slot brands.
- Cultural review for culture-based themes: symbols, colors (e.g. red/gold auspicious in
  Chinese markets; number 4 unlucky; avoid sacred/religious iconography as pay symbols).
- Age-rating/marketing: avoid child-appealing styles for gambling products (UK CAP/BCAP rules;
  verify per market with compliance-advisor).

## Consistency rules for production
- Master files: one palette swatch file, one light-direction rig, one icon template grid.
- Lock "golden" reference assets per category; new assets compared side by side in review.
- Any style change after lock → ADR-lite note in `style-guide.md` changelog with reason.

## Sources
- James Gurney, Color and Light: A Guide for the Realist Painter (Andrews McMeel, 2010)
- Marcos Mateu-Mestre, Framed Ink (Design Studio Press, 2010)
- GDC "Art Direction Bootcamp" sessions, GDC Vault https://gdcvault.com/
- UK Gambling Commission, online slots game design changes (announced 2021-02, in force 2021-10-31) https://www.gamblingcommission.gov.uk/
- SBC News, "UKGC bans online slots autoplay and quickspin features" (2021-02-02) https://sbcnews.co.uk/europe/uk/2021/02/02/ukgc-bans-online-slots-autoplay-and-quickspin-features/
- CMS, "Gambling White Paper Consultations: Remote Game Design" https://cms.law/en/gbr/legal-updates/gambling-white-paper-consultations-remote-game-design
