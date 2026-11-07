# Economy model: <game/feature> (v<n>, <YYYY-MM-DD>)
Owner: economy-monetization-designer. Status: draft | review | approved. Compliance review: <H-NNN path | pending>

## Goals and constraints
- Player goals / anchors: <power, collection, expression, social>
- Business targets: conversion <x%>, ARPDAU <$>, D30 retention <x%> (source: <PRD path>)
- Markets/platforms/age rating: <list>; server-authoritative: yes

## Currencies
| Currency | Type | Sources (rate) | Sinks (price) | Cap/expiry | Real-money value |
|---|---|---|---|---|---|
| <coins> | soft | <quest +120/session> | <upgrade 200*1.15^lvl> | <none> | <via gems: 10 coins = 1 gem> |

## Flow diagram
<mermaid flowchart per currency>

## Curves and tables (config keys)
| Key | Formula/table | Range allowed for liveops | Notes |
|---|---|---|---|

## Simulation results (script: `.team/specs/economy/sims/<name>.py`, seed <n>, N <players>)
| Archetype | D7 p50/p90 balance | D30 sink/source | Time-to-goal <milestone> | Spend D30 |
|---|---|---|---|---|

## Monetization hooks
- Store catalog / offers / pass / ads: <link monetization-plan.md>

## Random rewards (if any)
| Pool | Rates (per tier/item) | Pity | E[pulls], p90, p99 | E[cost] | Disclosure location |
|---|---|---|---|---|---|

## Telemetry
- Events: <currency_change fields>; dashboards/alerts: <bands>

## Risks and open questions
- <risk> → <mitigation> (risks.md ID); legal items: <list> — needs human legal review
