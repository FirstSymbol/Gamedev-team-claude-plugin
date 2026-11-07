# Threat model: <system/feature>   (<YYYY-MM-DD>, v<n>)
Owner: security-engineer   Reviewers: <roles>   ASVS target: L<1|2|3> per component below

## Scope and assets
| Asset | Why it matters | Impact if compromised (1–5) |
|---|---|---|
| <wallet balance / account / match fairness / PII> | <...> | <n> |
Attacker profiles: <cheater | fraudster | account thief | insider | bot farm>
Out of scope: <...>

## Data-flow diagram
```mermaid
flowchart LR
  <entities, processes, stores, flows with protocol + auth; subgraphs = trust boundaries>
```

## Threats (STRIDE per boundary-crossing flow/element)
| ID | Element/flow | STRIDE | Threat (attacker does X to get Y) | L | I | Risk | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| T1 | <client → API: PlaceBet> | T | <modifies amount after confirm> | <1–5> | <1–5> | <L×I> | <server recomputes; idempotency key> | <role> | open |

## Attack tree (top goal, optional)
```
GOAL: <...>
├─ OR <path> → <mitigation>
```

## Security requirements fed to specs
- <REQ-SEC-1: acceptance criterion, ASVS ref v5.0.0-x.y.z> → <spec path>

## Accepted risks
| ID | Rationale | Approver | Review date |
|---|---|---|---|

## Open questions
- <question> → <owner>
