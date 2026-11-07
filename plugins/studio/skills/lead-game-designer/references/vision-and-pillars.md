# Vision, pillars, audience, USP

## High concept (one sentence, then one paragraph)
- Formula A: "In <title>, you <core verb(s)> to <goal> in <world/fantasy>, unlike <comparable>
  because <hook>."
- Formula B (pitch shorthand): "<Known game> meets <known game/theme>" — internal only; never
  the whole vision (it imports the comparables' scope too).
- Test: a stranger can name the core action, the goal and the platform after hearing it once.
- Add: genre, platform(s), session length, business model (premium / F2P / social casino /
  live service), camera, single/multiplayer.

## Player fantasy & experience goals
- Fantasy = who the player gets to be/do ("a heist crew mastermind", "a cozy island mayor").
- Experience goals = target emotions per phase (first 5 min, first session, day 7, endgame).
  Map them to MDA aesthetics (game-designer: frameworks.md) — Challenge, Fantasy, Narrative,
  Fellowship, Discovery, Expression, Submission, Sensation (Hunicke et al., 2004).
- Write each as an observable player behaviour: "players replay a level voluntarily to
  improve rank" beats "the game feels rewarding".

## Design pillars
| Property | Rule |
|---|---|
| Count | 3–5 (more = no prioritisation) |
| Form | Player-centric verb phrase: "Every run tells a story", "Outsmart, don't outgun" |
| Test | "A feature fits if it …" — answerable yes/no in a review |
| Anti-pillar | "We don't …" — the tempting thing you refuse (e.g. "no PvP", "no energy timers") |
| Priority | Rank them; tie-break conflicts by rank |
| Evidence | Each pillar has a prototype/playtest question that proves it works |
- Pillar audit per feature: score 0–2 per pillar; total 0 → cut candidate; any feature scoring
  only on a lower-ranked pillar is first to cut in scope talks.
- Keep pillars stable after pre-production; changing one is an ADR + full GDD review.

## Target audience
Describe: platform + device tier, session pattern (e.g. 3–5 × 4 min/day mobile vs 2 h PC
evenings), age band (affects rating/compliance), motivation profile, comparable games they
play, spend profile (hand to economy-monetization-designer).

### Bartle player types (1996) — use as vocabulary, not segmentation
| Type | Suit | Wants | Design hooks |
|---|---|---|---|
| Achiever | Diamonds | points, levels, completion | goals, ranks, collections |
| Explorer | Spades | discovery, how things work | secrets, systemic depth, lore |
| Socialiser | Hearts | interaction with players | guilds, chat, co-op, gifting |
| Killer | Clubs | impose on others | PvP, leaderboards, raids |
- Caveat: derived from MUD players; players shift types by mood; not validated as a
  psychometric model. Don't size markets with it.

### Quantic Foundry Gamer Motivation Model (Yee; empirically derived from survey data)
| Cluster | Pairs (motivations) |
|---|---|
| Action–Social | Action (Destruction, Excitement), Social (Competition, Community) |
| Mastery–Achievement | Mastery (Challenge, Strategy), Achievement (Completion, Power) |
| Immersion–Creativity | Immersion (Fantasy, Story), Creativity (Design, Discovery) |
- 12 motivations / 6 pairs / 3 clusters; Discovery and Power act as bridges between clusters.
- Use: pick 2–3 primary motivations for the core audience and 1–2 secondary; every pillar
  should serve a primary one. QF publishes genre-level motivation profiles
  (verify: current data on quanticfoundry.com; sample sizes grew from ~30k to 500k+ gamers).
- Caveat (QF's own): the map shows relationships of motivations, not boxes for people.

### Self-Determination Theory (PENS: Rigby & Ryan, "Glued to Games", 2011)
- Competence (mastery, clear feedback), Autonomy (meaningful choice), Relatedness
  (connection). Use as a review lens: which need does this feature satisfy, which does it
  frustrate (e.g. forced social = autonomy hit)?

## USP (unique selling proposition)
- 1–2 features that are (a) visible in a 30 s trailer/store screenshot, (b) absent or weak in
  top comparables, (c) tied to a pillar, (d) feasible for the team. Verify with
  marketing-manager (store/ASO hook) and tech-lead-architect (cost).
- Red flags: USP is a technology ("uses procedural generation"), a quantity ("100 levels"),
  or invisible in the first session.

## Competitive analysis (deconstruction)
Pick 3–5 comparables: 1–2 market leaders, 1–2 closest in fantasy, 1 adjacent-genre innovator.
| Dimension | Capture |
|---|---|
| Core loop | verbs, loop length (seconds/minutes), win/fail states |
| Meta loop | progression layers, collection, social, live events |
| FTUE | time to first fun, tutorial steps, first choice, first reward |
| Economy | currencies, sinks/sources, energy/timers, IAP/ads placement (economy designer) |
| Retention hooks | dailies, streaks, events, social obligations (note dark patterns) |
| Market | genre rank, downloads/revenue estimates (verify: AppMagic/Sensor Tower data), reviews |
| Player complaints | top 1–3-star review themes = opportunity space |
| Steal / avoid | what we adopt, what we explicitly reject (link to anti-pillars) |
- Mobile F2P: Deconstructor of Fun and Mobile Free to Play publish deconstructions; for
  market data load `studio:domain-f2p-liveops`. Social casino: `studio:domain-igaming`.
- Output: `.team/specs/gdd/01-vision.md` appendix table + "positioning sentence".

## Vision validation (pre-production exit)
- [ ] Core loop prototype played by ≥ 5 target players; ≥ 3 can explain the goal unprompted.
- [ ] Each pillar has a demonstrable moment in the prototype.
- [ ] Fantasy recognisable from a mock store page/key art (art-director, marketing-manager).
- [ ] Business model fit reviewed by economy-monetization-designer and product-manager.
- [ ] Top 5 risks (design, tech, market) logged in `.team/risks.md`.

## Sources
- Hunicke, LeBlanc, Zubek, "MDA: A Formal Approach to Game Design and Game Research" (2004) https://users.cs.northwestern.edu/~hunicke/MDA.pdf
- Bartle, "Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs" (1996) https://mud.co.uk/richard/hcds.htm
- Quantic Foundry, "How we developed the Gamer Motivation Profile v2" https://quanticfoundry.com/2015/07/20/how-we-developed-the-gamer-motivation-profile-v2/
- Game Developer, "Player segments based on gaming motivations" https://www.gamedeveloper.com/business/player-segments-based-on-gaming-motivations
- Rigby & Ryan, "Glued to Games: How Video Games Draw Us In and Hold Us Spellbound" (Praeger, 2011)
- Schell, "The Art of Game Design: A Book of Lenses", 3rd ed. (CRC Press, 2019)
- Mobile Free to Play, "The Free to Play Game Design Bible" https://mobilefreetoplay.com/bible/
