# Design frameworks (applied)

## MDA (Hunicke, LeBlanc, Zubek, 2004)
- Mechanics (rules, data) → Dynamics (run-time behaviour from player + rules) → Aesthetics
  (player emotional response). Designer builds M→D→A; player experiences A→D→M.
- Design backwards: pick target aesthetics, hypothesise dynamics that produce them, then
  mechanics. Validate by observing dynamics in playtests (you can't ship aesthetics directly).

| Aesthetic | "Game as…" | Typical mechanics | Observable signal |
|---|---|---|---|
| Sensation | sense-pleasure | juice, audio, haptics, animation | replaying for feel, "satisfying" comments |
| Fantasy | make-believe | role, avatar, fiction-consistent verbs | role-play language, cosmetics use |
| Narrative | drama | quests, branching, characters | dialogue read rate, lore lookups |
| Challenge | obstacle course | skill tests, timers, ranks | retries, rank chasing |
| Fellowship | social framework | co-op, guilds, gifting | group play rate, chat |
| Discovery | uncharted territory | exploration, secrets, systemic combos | off-path time, wiki activity |
| Expression | self-discovery | building, customisation, playstyles | build diversity, sharing |
| Submission | pastime | low-stakes repetition, idle | long relaxed sessions |
- Use as the "why" line in every mechanic spec: "Aesthetic: Challenge + Expression".

## Loops
| Loop | Duration | Example (match-3) | Example (action RPG) |
|---|---|---|---|
| Core (moment-to-moment) | 1–30 s | swap → match → cascade → score | move → attack → dodge → loot |
| Session / level | 1–20 min | play level → win stars/coins | clear dungeon → boss → chest |
| Meta | days–weeks | spend coins → restore area → unlock episode | gear upgrades → skill tree → harder zones |
| Social/live | weeks–seasons | team events, leaderboards | guild raids, seasons |
- Loop spec: verbs, inputs (resources/energy/skill), outputs (rewards), sinks, fail state,
  loop duration, which loop it feeds. A loop with no sink inflates; with no reward stalls.
- Telfer (Mobile Free to Play): the core loop is what the player does repeatedly for the
  entire game — test it in isolation, before meta, with placeholder art.
- Koster ("A Theory of Fun"): fun = learning/mastering patterns; once mastered, boredom.
  Each loop needs a source of new patterns (content, combinations, opponents, variation).

### Compulsion loops — ethics check (mandatory for F2P/casino)
- Compulsion loop = anticipation → action → (variable) reward. Variable-ratio rewards are the
  strongest reinforcement schedule; they are also the core of loot-box/gambling concerns.
- Dark patterns (Zagal, Björk, Lewis, FDG 2013): temporal (grinding, playing by
  appointment), monetary (pay-to-skip, pre-delivered content, monetised rivalries), social
  (social pyramid schemes, impersonation).
- Rules: reward loops must sit on an intrinsically fun core; publish odds for paid random
  rewards; no punishment for missing a day beyond a lost bonus; no fake scarcity; spend
  caps/limits for minors; no pressure UX on players showing problem patterns.
  Loot boxes/odds/minors → compliance-advisor; social casino → `studio:domain-igaming`.

## Schell lenses — shortlist for reviews (The Art of Game Design, 3rd ed., 2019)
| Lens | Question to ask the spec |
|---|---|
| Essential Experience | What experience should the player have; what is essential to it? |
| Surprise | What surprises players? Do rules/story/art create surprises? |
| Curiosity | What questions does the game put in the player's mind? |
| Endogenous Value | What do players value inside the game, and why? |
| Problem Solving | What problems must players solve? Are there hidden ones? |
| Elemental Tetrad | Do mechanics, story, aesthetics, technology reinforce one theme? |
| Toy | Is it fun to play with even without goals? |
| Flow | Clear goals, no distractions, immediate feedback, challenge matching skill? |
| Meaningful Choices | Are choices real, informed, consequential? Any dominant strategy? |
| Triangularity | Is there a choice between a safe low reward and a risky high reward? |
| Skill vs. Chance | Is the skill/chance mix right for the audience? |
| Reward / Punishment | Are rewards proportional and varied? Is punishment fair and meaningful? |
| Visible Progress | Can players see their progress toward goals? |
| Fairness | Does every player feel they had a fair chance? |
| Elegance | Which elements do the most with the least? What can be removed? |
| Accessibility | Can players see how to begin without reading a manual? |
- Pick 4–6 lenses relevant to the mechanic; answer each in 1–2 lines in the review.

## Flow (Csikszentmihalyi, 1990; Chen, "Flow in Games", 2007)
- Conditions: clear goals, immediate feedback, challenge ≈ skill, sense of control, focus.
- Flow channel: challenge above skill → anxiety; below → boredom. Skill grows, so challenge
  must rise; use waves (tension then relief) rather than a straight line.
- Chen: give players choices that let them self-adjust (optional hard paths, assists)
  instead of only hidden DDA.

## Player agency & meaningful choice
- Checklist per decision: (1) player understands options and likely outcomes, (2) outcome
  differs in a way the player cares about, (3) no option dominates in all contexts,
  (4) consequence is visible soon enough to learn from, (5) choice expresses playstyle.
- Sid Meier's maxim "a game is a series of interesting decisions" (often quoted; GDC 2012
  "Interesting Decisions") — no-decision stretches need sensation/narrative to carry them.
- Agency killers: fake choices that converge invisibly, info hidden until after commit,
  solved metas, forced optimal paths for monetisation.

## Game feel & juice
- Swink ("Game Feel", 2008): real-time control + simulated space + polish. Specify all three.
- Responsiveness: ~100 ms reads as immediate (perceptual cycle, Card/Moran/Newell as used
  by Swink); budget input→first visible response ≤ 1–2 frames of logic + render
  (verify per platform; mobile touch adds latency).
- Platformer forgiveness (heuristics, tune per game): coyote time 0.05–0.15 s, jump buffer
  0.1–0.15 s, variable jump height (release cuts velocity), corner correction a few pixels.
- Impact: hit-stop 2–6 frames @60 fps, screen shake with decay (trauma²), recoil, knockback,
  flash on hit, particles, layered SFX with pitch variance ±5–10%, haptics on mobile.
- Juice ("Juice It or Lose It", Jonasson & Purho, GDC Europe 2012): maximum output for minimum
  input — tweens/easing, squash & stretch, particles, sound, camera. Counterpoint ("Don't
  Juice It or Lose It", GDC 2014): juice must not obscure readability or the fiction.
- Spec feel numerically: curves (AnimationCurve keys), durations in s/frames, accel/decel
  in m/s², camera offsets; supply a tuning scene for unity-developer.
- Accessibility: options to reduce shake/flash; flashing content ≤ 3 flashes/s (WCAG 2.3.1).

## Sources
- Hunicke, LeBlanc, Zubek, "MDA" (2004) https://users.cs.northwestern.edu/~hunicke/MDA.pdf
- Schell, "The Art of Game Design: A Book of Lenses", 3rd ed. (CRC Press, 2019)
- Koster, "A Theory of Fun for Game Design", 2nd ed. (O'Reilly, 2013)
- Swink, "Game Feel" (Morgan Kaufmann, 2008)
- Zagal, Björk, Lewis, "Dark Patterns in the Design of Games", FDG 2013 https://research.chalmers.se/en/publication/177148
- Jonasson & Purho, "Juice It or Lose It", GDC Europe 2012 https://gdcvault.com/play/1016487/Juice-It-or-Lose
- Telfer, "Crafting a Strong Core Loop" https://mobilefreetoplay.com/bible/crafting-strong-core-loop/
- Chen, "Flow in Games (and Everything Else)", Communications of the ACM 50(4), 2007
- WCAG 2.2, 2.3.1 Three Flashes or Below Threshold https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
