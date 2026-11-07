# Layout & flow

## Process
1. Experience goals for the level (what the player should feel/learn) → 2. parti (core
   organising idea; sketch 5–10 thumbnails, one label each) → 3. bubble diagram (≥ 3
   variants: spaces + connections) → 4. top-down layout with critical path → 5. greybox →
   6. playtest → iterate. A layout can't prove a level works; only blockout + playtest can.
- Draw boxy: ~90% of corners at 90° on grid (Level Design Book); use line weights for wall
  types; perspective sketches for height changes.

## Critical path & structure
| Typology | Shape | Use |
|---|---|---|
| Linear / corridor | A→B | tutorials, story beats, mobile runners |
| Beaded necklace | arenas strung on corridors | action games: fight → traverse → fight |
| Hub & spoke | central hub, branches | open levels, missions, metroidvania zones |
| Loop / figure-8 | path returns to start area | exploration without backtracking pain |
| Branch & merge | optional side routes rejoin | choice + secrets with bounded content cost |
| Open / sandbox | many routes, systemic | immersive sims, open world |
| Lanes (MP) | 3 lanes + connectors | MOBA/arena/shooter maps |
- Mark the critical path (ideal route) on every single-player layout; budget its time
  (e.g. "teaching level ≤ 5 min critical path"). Optional content ≤ 1 step off path, or
  rewarded proportionally to the detour.
- Shortcuts unlocked from the far side (loop back) reduce backtracking and reward progress.

## Orientation: landmarks, sightlines, weenies
- Lynch's city elements (used by Totten for levels): paths, edges, districts, nodes,
  landmarks. Give each district a distinct silhouette/colour/material.
- Landmark = unique, tall/bright, visible from multiple decision points; global landmarks
  orient across the level, local ones mark rooms/junctions.
- "Weenie" (Disney): a visible goal drawing the player forward; reveal it early, reach it late.
- Sightlines: frame the next objective at each doorway/turn; use leading lines (edges,
  cables, light gradients), contrast and motion to pull attention.
- Prospect–refuge (Totten, from Appleton): players feel safe in refuge (cover, enclosure) with
  prospect (view over space); use for arena entrances and sniper spots.
- Signposting order: composition/light → landmarks → affordance language (consistent
  climbable/breakable colour) → UI markers last. Keep affordance colours consistent game-wide.

## Gating
| Gate | Example | Rule |
|---|---|---|
| Lock & key | key card, lever, boss key | key visible before or near the lock, or the lock shown first as a goal |
| Ability | double jump opens area (metroidvania) | show the blocked path before the ability (creates a goal) |
| Skill | hard platforming section | follows teach section; checkpoint before |
| Narrative/event | door opens after dialogue | don't trap player in long non-interactive waits |
| Soft gate | strong enemies, environmental hazard | allowed sequence breaks; balance rewards |
| Valve (one-way) | drop-down, closing door | prevents backtracking soft-locks; signal it's one-way |
- Soft-lock check: from every reachable state, the critical path must remain completable.

## Metrics (parameters, not eyeballing)
- Define them with game-designer from actual character controller values; store in a
  `LevelMetrics` ScriptableObject + metrics gym scene. Design to *comfortable* values, not
  maximum (players don't hit perfect inputs).

| Metric | Unity reference start (Level Design Book) | Rule |
|---|---|---|
| Player capsule | 1.0 × 1.8–2.0 m, eye height 1.5–1.7 m | collision > visual model |
| Min corridor width | 2.0 m | ≥ 2× player width; wider for combat/co-op |
| Door | 1.25 × 2.5 m | narrower than hall to read as a door |
| Interior wall height | 3.0 m | |
| Stair step | 0.1–0.15 m rise; 30–35° slope; landing every 12–16 steps | match controller step offset |
- Derive per game: max jump height `h = v₀²/(2g)`, max gap `d = vₓ · 2v₀/g` (flat ground);
  comfortable gap ≈ 70–80% of max (heuristic); safe drop height (no damage); cover heights
  (low cover ≈ crouch eye height − 0.1 m, high cover > standing eye height); climb/mantle heights.
- Combat ranges (TF2 example, Hammer units): close ≤ 256, medium ≤ 1024, long/sniper ~2048.
  Convert to your weapons' effective ranges; sightline length per area = intended weapon range.
- Consistency > realism: "big" spaces can be much smaller than real equivalents; lock
  camera height/FOV early — it changes perceived scale.

## Multiplayer maps (also see `domain-multiplayer` skill)
- Symmetry (fair, readable) vs asymmetry (attack/defend; balance spawn times/routes).
- Spawn safety: no direct sightline from enemy areas; multiple exits.
- Timing: equal travel time from spawns to first contact point (measure with bots/run tests).
- Callouts: name every area for team communication; distinct visuals per area.
- Rotations: 2–3 routes between objectives; flank routes longer than direct route.
- Molecule/node-graph design (Totten): nodes = key spaces, edges = routes; balance node degree.

## Layout review checklist
- [ ] Purpose + experience goals stated; parti identifiable in the layout.
- [ ] Critical path marked and timed; optional content cost/benefit acceptable.
- [ ] Landmark visible from each major decision point; no indistinguishable junctions.
- [ ] Every gate has a visible reason and a solution reachable; soft-lock check done.
- [ ] Sizes come from metrics; jumps tested at comfortable values.
- [ ] MP: spawn safety, timing parity, callouts, ≥ 2 routes per objective.

## Sources
- The Level Design Book (Robert Yang et al.), "Layout" https://book.leveldesignbook.com/process/layout
- The Level Design Book, "Metrics" https://book.leveldesignbook.com/process/blockout/metrics
- Totten, "An Architectural Approach to Level Design", 2nd ed. (CRC Press, 2019)
- Lynch, "The Image of the City" (MIT Press, 1960)
- Smith & Worch, "What Happened Here? Environmental Storytelling", GDC 2010 https://gdcvault.com/play/1012647/What-Happened-Here-Environmental
