# <Feature> | owner: <role> | status: draft | updated: <YYYY-MM-DD> | milestone: <...>
Pillars served: <P#>  GDD section: <path>  Depends on: <paths>  ADRs: <paths>

## Intent
<Player experience goal in 1–2 sentences. Which problem/opportunity, which player motivation.>

## Player-facing behaviour
1. <Player does X> → <game responds Y> (feedback: visual / audio / haptic)
2. <...>

## Rules
| ID | Trigger | Effect | Duration | Exceptions / stacking |
|---|---|---|---|---|
| R1 | <...> | <...> | <...> | <...> |

## States
<state list or Mermaid stateDiagram; every state has entry/exit conditions; no dead ends>

## Parameters (tunables → ScriptableObject/remote config)
| Name | Type | Default | Range | Unit | Live-tunable | Notes |
|---|---|---|---|---|---|---|
| <dashDistance> | float | <4.0> | <2–8> | m | no | <...> |
Data table: <.team/specs/gdd/data/<file>.csv>

## Edge cases
- <zero/max values, interrupts, disconnect, background/resume, save mid-action, spam input>

## UI / UX & text
- Screens/HUD: <link to ux spec>  Strings: <IDs, owner narrative-designer>

## Economy impact
- Sources/sinks added: <none | list → economy-monetization-designer>

## Telemetry
| Event | Params | Answers |
|---|---|---|
| <feature_used> | <...> | <success metric + target> |

## Acceptance criteria
- [ ] Given <context>, when <action>, then <observable result>.
- [ ] <...>

## Out of scope
- <explicit non-goals for this milestone>

## Open questions
- <question> → <owner>, due <YYYY-MM-DD>
