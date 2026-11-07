# Pacing & encounter design

## Pacing tools
- **Intensity graph**: x = critical-path time (or level %), y = intensity 0–10. Plot planned
  beats; compare with playtest (deaths, heart-rate proxies: retries, damage taken, speed).
  Target shape: rising waves with valleys; biggest peak near the end; valley after each peak.
- **Beat chart** (per level or chapter):

| # | Beat | Type (combat/traverse/puzzle/story/reward/rest) | Intensity | Mechanic (intro/develop/test/twist) | Duration | Narrative note |
|---|---|---|---|---|---|---|
| 1 | Courtyard ambush | combat | 6 | test: dash-cancel | 2 min | first sight of tower (landmark) |

- **Variety rule**: avoid > 2 consecutive beats of the same type at the same intensity
  (heuristic); alternate challenge with breathers, exploration, reward.
- **Rest/safe spaces**: after peaks; save points, shops, story, vistas of the next goal.

## Introduce → develop → twist → conclude (kishōtenketsu-style)
- Nintendo's 3D Mario levels: introduce a gimmick safely, develop it with added risk,
  twist it (combine with another idea or invert it), conclude with a final test — then drop
  it (cf. Hayashida interview; GMTK analysis). Each mechanic gets a short, complete arc.
- Teach in a safe space (no fail or cheap fail) → test with stakes → combine with known
  mechanics → master test. Never introduce a mechanic inside a hard encounter.

## Director-style dynamic pacing (Left 4 Dead)
- AI Director tracks per-player "intensity" (damage, nearby deaths, incapacitation) and
  cycles Build Up → Sustain Peak → Peak Fade → Relax, spawning/withholding enemies
  accordingly (Booth, Valve, 2009). Use as a model for wave spawners and roguelike rooms:
  cap peak duration, guarantee relax windows.

## Combat encounter anatomy
| Element | Decide |
|---|---|
| Goal | kill all / survive N s / reach exit / protect / escape — vary across the level |
| Arena | size vs weapon ranges; cover (low/high), verticality, flanking routes, retreat space |
| Entry | player sees the arena before committing (prospect) where fairness matters; ambushes are deliberate, rare beats |
| Enemy composition | roles mix (below); first wave readable; elites later |
| Spawns | in front/peripheral vision; avoid behind-the-player spawns unless telegraphed; stagger waves by trigger/count/time |
| Resources | health/ammo placed to support intended pacing (more after peaks) |
| Exit/reward | clear end signal (music, door opens, loot); short breather |
| Difficulty knobs | enemy count, roles, aggression/accuracy, spawn rate, time limit, resource supply, arena hazards |

| Enemy role | Function | Example design note |
|---|---|---|
| Fodder | power fantasy, crowd | dies in 1–2 hits; groups |
| Soldier | baseline pressure | standard ranges, flanks occasionally |
| Ranged/sniper | forces movement/cover use | long sightline; reachable position |
| Tank/heavy | forces focus/weak points | slow, telegraphed attacks |
| Disruptor/flanker | breaks camping | approaches from side routes |
| Support | priority target | heals/buffs others; visually distinct |
| Elite/boss | test of mastery | phases, unique patterns |

- Readability: each attack has a telegraph (animation + audio + VFX) proportional to its
  damage; heavy hits telegraph longer. Limit simultaneous attackers on the player (token
  system: e.g. 1–3 melee attackers at once, heuristic) — request from unity-developer.
- Fairness: off-screen damage indicated; no unavoidable damage without a learnable cue.

## Boss design checklist
- [ ] Arena reinforces the fight (cover, hazards, phase changes alter the space).
- [ ] 2–4 phases; each adds/changes one pattern; phase transitions are breathers.
- [ ] Every pattern telegraphed and punishable (opening after the attack).
- [ ] Tests mechanics taught in the preceding levels — none new.
- [ ] Checkpoint right before; retry cost ≤ ~30 s to re-engage (heuristic).
- [ ] Fail telemetry: death cause by pattern/phase.

## Non-combat beats
- Traversal: rhythm via gap spacing and timing; escalate with hazards and moving parts;
  open/close camera framing to vary feel.
- Puzzles (in action games): goal visible, components visible, no pixel hunts; hint after N
  attempts or T seconds; solution uses mechanics in a new combination.
- Stealth: readable AI states (unaware/suspicious/alert), sightline cones, multiple routes,
  recoverable failure.
- Narrative beats: player keeps control where possible; short cutscenes at valleys, not peaks
  (→ narrative-designer).

## Session pacing by platform
- Mobile: levels/rounds 1–5 min; natural stop points every few minutes; progress saved at
  every stop; one peak per level.
- PC/console: 30–90 min sessions; chapters with save points every ~10–20 min of play
  (heuristic); bigger arcs per chapter.
- Multiplayer: match pacing via objective timers, respawn waves, map control shifts.

## Sources
- Booth, "The AI Systems of Left 4 Dead", AIIDE 2009 keynote (Valve) (verify: slides on valvesoftware.com)
- Totten, "An Architectural Approach to Level Design", 2nd ed. (CRC Press, 2019) — pacing, prospect/refuge
- The Level Design Book https://book.leveldesignbook.com/
- Game Maker's Toolkit (Mark Brown), "Super Mario 3D World's 4 Step Level Design" (YouTube, 2015) (verify title)
- Schell, "The Art of Game Design", 3rd ed. (CRC Press, 2019) — interest curves
