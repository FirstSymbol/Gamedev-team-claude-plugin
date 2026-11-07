# Test cases - <feature> (<spec path>)
Owner: qa-engineer  Date: <YYYY-MM-DD>  Build: <tested build>  Coverage: AC <x/y>, rules <x/y>, boundaries <x/y>

Legend: Level = U (EditMode/unit) | I (PlayMode/integration/API) | S (system/device) | E (exploratory);
Auto = Y (automated, test name) | P (planned) | N (manual); Risk = register ID; Result = Pass/Fail/Blocked/Not run.

| ID | AC/Risk | Title | Technique | Preconditions | Steps | Test data | Expected | Level | Auto | Result | Bug |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-<feat>-001 | AC-1 / R1 | <claim on day 1 grants 100> | EP | <FTUE done, never claimed> | 1. Open lobby 2. Tap Claim | VIP 0 | +100 coins; streak = 1; button disabled | I | Y `DailyBonusApiTests.Claim_day1` | | |
| TC-<feat>-002 | AC-2 / R1 | <second claim same UTC day rejected> | Decision table R2 | <claimed today> | 1. Call claim | - | 409 `ALREADY_CLAIMED`; balance unchanged | I | P | | |
| TC-<feat>-003 | AC-3 | <boundary 23:59:59 → 00:00:00 UTC> | BVA | <claimed at 23:59:59> | 1. Advance server time 1 s 2. Claim | - | granted, streak 2 | U | Y | | |

## Exploratory charters
| ID | Charter (Explore … with … to discover …) | Timebox | Tester | Notes/bugs path |
|---|---|---|---|---|
| EX-<feat>-01 | <Explore claim with clock/timezone changes and airplane mode to discover double-grant> | 60 min | | |

## Gaps / not covered
- <condition - reason - risk accepted by>
