# Story structures, branching, quests, environmental storytelling

## Narrative role (agree with lead-game-designer first)
| Role | Example genres | Budget signal |
|---|---|---|
| Central | narrative adventure, RPG, visual novel | branching scripts, VO, cinematics |
| Supporting | action-adventure, live-service shooter | critical-path story + barks + lore |
| Meta/reward | renovation match-3, idle, casual | short dialogues between levels, characters as hosts |
| Flavour | puzzle, casino, hyper-casual | names, item text, UI voice only |

## Linear arcs (use for the spine)
- Three-act: setup (~25%) → confrontation (~50%, midpoint reversal) → resolution (~25%).
- Kishōtenketsu: introduction → development → twist → reconciliation; conflict optional
  (good for cozy games and level-mechanic arcs).
- Episodic/seasonal (live service): each season = self-contained arc + thread to the next;
  align with liveops calendar (liveops-manager).
- Hero's journey: vocabulary only; don't force 12 stages onto game pacing.

## Interactive structures
| Structure | Shape | Content cost | Use |
|---|---|---|---|
| Linear with flavour choices | one path, tone/dialogue choices | ~1× | most action games |
| Branching tree | every choice splits | `(b^(d+1)−1)/(b−1)` nodes; 2 choices × 10 depth ≈ 2,047 | short only (gamebooks, micro-scenes) |
| Branch & bottleneck | branches rejoin at key beats; state carried | ~1.5–3× | Telltale-style, most narrative games |
| Foldback / parallel paths | parallel routes converge | ~2× | chapters with choice of approach |
| Hub & spoke | missions from a hub, any order | per spoke | RPG towns, mission selects |
| Quality-based narrative (QBN) / storylets | storylets unlocked by state "qualities"; player picks among legal ones | linear in storylets | Failbetter games, sandbox stories, live games |
| Salience-based | system picks the most applicable content from a pool | per line | barks, companions (Valve dynamic dialog) |
| Waypoint | fixed waypoints, free paths between | moderate | open world with authored beats |
- Reflect choices cheaply: callbacks (later line references a choice), state-variant lines,
  epilogue slides — before adding true branches.
- State: name every variable/flag (`met_ramona`, `trust_kai: int -3..3`), owner, where set,
  where read. Keep a variables table in `40-narrative/state.md`.

## Choice design
- Types: expressive (tone/personality), tactical (approach), moral (values), plot (branch).
- A choice is meaningful if the player understands the options, outcomes differ in ways
  they care about, and the result is acknowledged (immediately or delayed).
- Avoid false binaries and "gotcha" outcomes that the options didn't signal.
- Timed choices: give ≥ ~5–8 s unless pressure is the point (heuristic); offer an
  accessibility option to disable timers.

## Quest design
- Structure: hook (why care) → objective(s) → complication/twist → climax → reward →
  consequence (world/character state changes).
- Verb wrapper: mechanics (kill, fetch, escort, defend, investigate, deliver, solve) need a
  motivation and a twist; avoid > 2 consecutive quests of the same verb.
- Quest doc (`40-narrative/quests/<id>.md`):

| Field | Content |
|---|---|
| ID / name / giver | `Q_MAIN_03` / "Ash and Iron" / smith Hilde |
| Prerequisites | flags/level/items |
| Objectives | trackable states with journal text IDs (`quest.q_main_03.obj1`) |
| Fail conditions | timer, NPC death, choice; can it be failed? retry? |
| Rewards | items/XP/currency → TBD(economy-monetization-designer / game-designer) |
| Dialogue | file/node names |
| World changes | flags set, NPC states, level changes (→ level-designer) |
| Markers & UI | map markers, notifications (→ ux-ui-designer) |
| Edge cases | out-of-order completion, sequence breaks, abandoned quest, save mid-quest |

## Environmental storytelling (Smith & Worch, GDC 2010)
- Stage spaces with props/lighting/composition so players infer "what happened here";
  players explore and interpret, which builds investment.
- Two forms: designer-authored (staged scenes) and systemic (world reacts to systems/player:
  bullet holes, corpses persisting, NPC routines changing).
- Techniques: before/after contrast, implied paths of events (trail of objects), personal
  items in context, notes/audio logs (sparingly), architecture that reveals social order.
- Brief for level-designer: location, story to imply (1–2 lines), props list, readability
  test ("3 of 5 testers can describe what happened").

## Barks & systemic dialogue
- Valve's dynamic dialog (Ruskin, GDC 2012): lines tagged with criteria (concept + world
  facts like health, location, who's nearby); query picks the rule with most matching
  criteria → context-specific variety cheaply. Yarn Spinner 3 storylets/saliency and line
  groups offer similar selection in-tool.
- Bark spec: trigger concept, criteria, priority, cooldown (global + per line), max repeats,
  interruptibility, subtitle display, VO length limit.

## Ludonarrative coherence
- Ludonarrative dissonance (Hocking, 2007): story and mechanics pull in opposite
  directions. Review each major beat: does the gameplay ask the player to do what the
  story says the character values? Fix with mechanics change, framing, or acknowledged irony.

## Platform/genre notes
- Mobile meta-narrative: story as reward between levels; dialogues 2–5 lines per beat,
  tap-to-advance, skippable, recap for returning players (heuristic).
- Live service: lore drip through events, collectibles, seasonal cinematics; maintain a
  canon timeline doc.
- Casino/social casino: theme narrative is flavour; never imply higher win chances through
  story or characters (→ compliance-advisor).

## Sources
- Smith & Worch, "What Happened Here? Environmental Storytelling", GDC 2010 https://gdcvault.com/play/1012647/What-Happened-Here-Environmental
- Nieman Storyboard, "Harvey Smith on environmental storytelling" (2011) https://niemanstoryboard.org/2011/01/14/harvey-smith-on-environmental-storytelling-and-embedding-narrative/
- Short, "Beyond Branching: Quality-Based, Salience-Based, and Waypoint Narrative Structures" (2016) https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/
- Yarn Spinner docs, "Storylets and saliency: a primer" https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/storylets-and-saliency-a-primer
- Ruskin, "AI-driven Dynamic Dialog through Fuzzy Pattern Matching", GDC 2012 (Valve) (verify: GDC Vault)
- Hocking, "Ludonarrative Dissonance in Bioshock" (Click Nothing blog, 2007)
- Yarn Spinner, "Yarn Spinner 3.0: What To Expect" https://www.yarnspinner.dev/blog/yarn-spinner-30-what-to-expect/
