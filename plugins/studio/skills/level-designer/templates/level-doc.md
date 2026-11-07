# <LevelId> — <Level name> | owner: level-designer | status: draft | updated: <YYYY-MM-DD>
Chapter/episode: <...>  Position in sequence: <n>  Purpose: <teach | develop | test | twist | breather | boss>
Pillars served: <P#>  Mechanics: <introduced / developed / tested>  Difficulty target: <band, APS or deaths/time>

## Experience goals
- Player should feel/learn: <...>
- Parti (core idea): <one phrase>

## Layout
- Map: <path to top-down sketch/screenshot>  Typology: <linear | hub | loop | lanes | ...>
- Critical path: <start → … → exit>, target time <mm:ss>; optional areas: <list + reward>
- Landmarks: <global / local, where visible from>
- Gates: <type, location, key/solution location>  Soft-lock check: <done/date>

## Metrics used (from LevelMetrics <asset path>)
| Metric | Value | Where it matters |
|---|---|---|
| <max comfortable jump gap> | <m> | <area> |

## Beats
| # | Beat | Type | Intensity 0–10 | Mechanic arc | Duration | Narrative/env. story |
|---|---|---|---|---|---|---|
| 1 | <...> | <...> | <...> | <...> | <...> | <...> |

## Encounters / puzzle parameters
- <encounter id: goal, arena, enemy roles × counts, waves/triggers, resources>
- Puzzle/match-3: <colours, moves, objectives, blockers, spawn weights, seed> → data: <path>

## Checkpoints & failure
- Checkpoints: <locations>; replay cost after fail: <s>; fail reasons expected: <...>

## Rewards
- <per-level rewards → TBD(economy-monetization-designer)>

## Tech & art notes
- Scenes: <Id>_Geo / <Id>_Gameplay / <Id>_Light  Perf budget: <draw calls/tris>  Kit: <...>
- Art handoff: moods per district <...>; do-not-change metrics <...>

## Telemetry
- Events: level_start, checkpoint_reached{id}, death{pos,cause}, level_complete{time,moves_left}, level_quit{pos}

## Playtest log
| Date | Build | n | Findings | Changes |
|---|---|---|---|---|
| <...> | <...> | <...> | <...> | <...> |

## Open questions
- <question> → <owner>, due <YYYY-MM-DD>
