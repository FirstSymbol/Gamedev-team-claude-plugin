# Test design techniques (with worked examples)

Running example specs (replace with the real AC):
- **Daily bonus**: claim once per server UTC day; streak day 1-7 rewards `[100,150,200,300,400,600,1000]`
  coins; missing a full UTC day resets streak to 1; after day 7 the streak wraps to day 1; VIP level
  multiplier: VIP 0-2 x1, VIP 3-6 x1.5 (round down), VIP >= 7 x2; feature unlocks after FTUE.
- **Wallet bet**: integer coins; min bet 1, max bet 10,000; bet <= balance; balance stored as `long`.

## Choosing a technique
| Situation | Technique |
|---|---|
| Input field / numeric parameter / range | Equivalence partitioning + boundary value analysis |
| Several conditions combine into different outcomes | Decision table |
| Behavior depends on history / time / mode | State transition |
| Many independent config parameters (device, OS, locale, network) | Pairwise / combinatorial |
| Unclear spec, new feature, risk hunting | Exploratory (session-based) |
| Known failure patterns of this domain | Error guessing / checklist |
Black-box techniques give coverage you can measure (partitions, boundaries, rules, transitions
covered); report it as e.g. "decision table: 8/8 rules covered".

## Equivalence partitioning (EP)
Divide inputs into classes the system should treat the same; one test per class (valid classes can be
combined, invalid classes tested one at a time so a failure is attributable).
Wallet bet (balance = 5,000):
| Partition | Example | Expected |
|---|---|---|
| V1: 1 <= bet <= min(10,000, balance) | 250 | accepted, balance 4,750 |
| I1: bet < 1 | 0, -5 | rejected `BET_TOO_LOW`, balance unchanged |
| I2: bet > 10,000 | 12,000 | rejected `BET_TOO_HIGH` |
| I3: balance < bet <= 10,000 | 6,000 | rejected `INSUFFICIENT_FUNDS` |
| I4: non-integer / malformed | 1.5, "abc", null | 400 validation error (API), input blocked (UI) |
| I5: overflow | 9,223,372,036,854,775,807 | rejected; no wraparound |

## Boundary value analysis (BVA)
CTFL 4.0: 2-value BVA tests each boundary and its closest neighbor across; 3-value adds the neighbor
inside. Use 3-value for money/RNG/time.
| Boundary | 2-value | 3-value |
|---|---|---|
| min bet = 1 | 0, 1 | 0, 1, 2 |
| max bet = 10,000 | 10,000, 10,001 | 9,999, 10,000, 10,001 |
| bet = balance (5,000) | 5,000, 5,001 | 4,999, 5,000, 5,001 |
| VIP multiplier edges | 2/3, 6/7 | 2,3,4 and 6,7,8 |
Time boundaries for the daily bonus (server UTC): 23:59:59.999 vs 00:00:00.000; claim exactly at
reset; last claim 24 h ago vs 47:59:59 ago (still "yesterday"?) vs 48:00:00 (missed day) - clarify AC.

## Decision table - daily bonus claim
Conditions: C1 FTUE done; C2 already claimed today (UTC); C3 last claim was yesterday; C4 current streak = 7.
| Rule | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|
| C1 FTUE done | N | Y | Y | Y | Y |
| C2 claimed today | - | Y | N | N | N |
| C3 last claim yesterday | - | - | Y | Y | N |
| C4 streak = 7 | - | - | N | Y | - |
| Action | hidden/locked | reject `ALREADY_CLAIMED` | grant day streak+1 | grant day 1 (wrap) | grant day 1 (reset) |
`-` = don't care (collapsed). Add VIP as a second table (multiplier per VIP band) rather than
multiplying rules. Each column = one test; expected reward = table[day] x multiplier, rounded down
(day 5, VIP 4 → 400 x 1.5 = 600; day 2, VIP 3 → 150 x 1.5 = 225).

## State transition - daily bonus + wallet transaction
States: `Locked` → `Available` → `Claimed` → (UTC midnight) `Available`; missed day → streak reset.
| From \ Event | FTUE complete | claim | UTC midnight | 24 h+ no claim |
|---|---|---|---|---|
| Locked | Available | (invalid: reject) | Locked | Locked |
| Available | - | Claimed (streak+1) | Available | Available (streak reset to 1) |
| Claimed | - | (invalid: `ALREADY_CLAIMED`) | Available | - |
Wallet transaction: `Pending` → `Committed` | `Failed`; `Committed` → `Reversed` (refund/chargeback).
Invalid transitions to test: commit twice (same idempotency key → same result, no double credit),
reverse a `Failed`, commit after timeout already rolled back.
Coverage levels: all states; all valid transitions (0-switch); invalid transitions; transition pairs
(1-switch) for high risk (e.g. Claimed → midnight → claim → midnight → claim across DST).

## Pairwise / combinatorial
Most config defects are triggered by 1-2 parameter interactions (NIST research); pairwise covers all
pairs with far fewer tests than the full product.
Tools: **PICT** (Microsoft, CLI, constraints), **ACTS** (NIST, GUI/CLI, t-way up to 6), **allpairspy**
(Python), **Pairwise Online Tool** (pairwise.teremokgames.com, verify availability).
```text
# daily_bonus.pict  →  pict daily_bonus.pict > cases.tsv
Platform:  Android10, Android13, Android15, iOS17, iOS18
Network:   WiFi, Cellular, OfflineThenOnline
Locale:    en-US, de-DE, ja-JP, ar-SA
VIP:       0, 3, 7
TimeZone:  UTC-8, UTC, UTC+5:30, UTC+14
IF [Platform] IN {"iOS17","iOS18"} THEN [Network] <> "OfflineThenOnline";   # example constraint only
```
Full product = 5x3x4x3x4 = 720 cases; pairwise ≈ 20-25. Use 3-way for money/RNG configurations.

## Exploratory testing (session-based test management)
Charter (Hendrickson): **Explore** <target> **with** <resources/approach> **to discover** <information>.
- "Explore daily bonus claim with device clock/timezone changes and airplane mode to discover
  double-grant or lost-streak defects."
- "Explore wallet with parallel requests (k6 script, 2 devices same account) to discover race conditions."
Session: 60-90 min, one charter, timeboxed; notes: setup, what tested, bugs, issues/questions,
coverage %, % time on test/bug investigation/setup (TBS). Debrief 10 min with qa-lead.
Heuristics: SFDIPOT (Structure, Function, Data, Interfaces, Platform, Operations, Time) from Bach's
HTSM; tours (money tour, landmark tour, back-alley tour); CRUD on every entity; interrupt everything.

## Error guessing - game/backend checklist
- Time: UTC midnight, DST switch, timezone change mid-session, device clock rollback/forward, leap day.
- Lifecycle: kill app during claim/purchase/save; background during transaction; low memory kill.
- Network: timeout after server commit (client retries → duplicate?), offline queue replay, flaky 3G.
- Concurrency: double tap, two devices same account, parallel API calls, rapid scene transitions.
- Data: zero, negative, max `int`/`long`, empty strings, emoji/RTL in names, very long names.
- Economy: refund after consume, receipt replay, price changed between display and buy, currency rounding.
- Platform: permissions denied, notch/safe area, font scale 200%, dark mode, low storage, OS update.
- Config: missing remote config key, malformed JSON, event config start > end, A/B bucket switch.

## Traceability
Each test case ID → AC ID → risk ID. Report coverage as: AC covered x/y; partitions x/y; boundaries x/y;
decision rules x/y; transitions x/y. Gaps are explicit in the test-run report.

## Sources
- ISTQB CTFL Syllabus v4.0, ch. 4 Test analysis and design (2023) https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
- Microsoft PICT https://github.com/microsoft/pict
- NIST ACTS / combinatorial testing https://csrc.nist.gov/projects/automated-combinatorial-testing-for-software
- Elisabeth Hendrickson, "Explore It!" (Pragmatic Bookshelf, 2013) https://pragprog.com/titles/ehxta/explore-it/
- Jonathan Bach, "Session-Based Test Management" (2000) https://www.satisfice.com/download/session-based-test-management
- James Bach, Heuristic Test Strategy Model https://www.satisfice.com/download/heuristic-test-strategy-model
- allpairspy https://github.com/thombashi/allpairspy
