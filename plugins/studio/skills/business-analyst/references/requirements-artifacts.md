# Requirements artifacts

## Artifact selection
| Need | Artifact | Size rule |
|---|---|---|
| Align on why/what/scope | Vision / BRD-lite (templates/brd-lite.md) | ≤ 2 pages |
| Whole user journey, release slicing | Story map | 1 board, 5–15 activities |
| Backlog item | User story + Gherkin AC (templates/user-story.md) | fits one sprint, ≤ ~3 days dev |
| Complex multi-step interaction, many alternates | Use case (Cockburn fully dressed) | 1 per user goal |
| Rule-heavy logic (bonus eligibility, pricing) | Decision table | all combinations covered |
| Quality constraints | NFR catalogue (ISO 25010) | each NFR measurable |
| Coverage/impact | Traceability matrix | every row has goal + test |

## Vision / BRD-lite contents
Problem, objectives (SMART, linked to KPI), stakeholders, scope in/out, capabilities (high
level), business rules BR-n, assumptions A-n, constraints C-n, dependencies, risks, success
metrics + measurement, release slices, open questions. Detail goes to stories, not the BRD.

## User stories
- Format: `As a <role/persona>, I want <capability>, so that <benefit tied to goal>.`
- Card–Conversation–Confirmation (Ron Jeffries): the card is a token; AC are the confirmation.
- INVEST (Bill Wake, 2003): Independent, Negotiable, Valuable, Estimable, Small, Testable.
| Letter | Check | Fix if failing |
|---|---|---|
| I | can ship in any order vs siblings | merge coupled stories or extract shared enabler |
| N | states need, not UI/implementation | rewrite "so that"; move design to UX/SA |
| V | user or business sees value | combine technical slices into vertical slice |
| E | team can size it | spike (timeboxed) first |
| S | ≤ 1 sprint, ideally 1–3 days | split (SPIDR below) |
| T | AC binary pass/fail | add numbers, examples |
- Splitting — SPIDR (Mike Cohn): Spike, Paths (happy vs alternate), Interfaces (platform,
  device, UI variants), Data (subsets, types), Rules (relax a business rule first, add later).
  Also: CRUD operations, workflow steps, simple→complex, defer performance.
- Enablers/tech stories allowed but state the business outcome they unblock.

## Acceptance criteria (Gherkin)
```gherkin
Feature: Daily login bonus
  Rule: BR-12 bonus can be claimed once per UTC day
  Background:
    Given player "p1" is logged in
  Scenario: Claim available bonus
    Given "p1" has not claimed today and the streak is 2
    When "p1" claims the daily bonus
    Then the wallet is credited 300 coins
    And the streak becomes 3
  Scenario: Second claim the same day is rejected
    Given "p1" already claimed today
    When "p1" claims the daily bonus
    Then no coins are credited
    And the response says "already claimed" with the next reset time
  Scenario Outline: Streak rewards
    Given the streak before claim is <before>
    When "p1" claims
    Then the reward is <coins>
    Examples:
      | before | coins |
      | 0      | 100   |
      | 6      | 1000  |
      | 7      | 100   |
```
- One behavior per scenario; Given = state, When = one action, Then = observable outcome.
- Declarative, not imperative ("claims the bonus", not "clicks button #claim").
- Cover: happy, alternate, error/negative, boundary (0, max, max+1), concurrency/idempotency,
  offline/timeout, permissions. Concrete example values beat abstract wording.
- AC ≠ Definition of Done: DoD is global (tests, review); AC are story-specific.

## Use case (fully dressed, Cockburn)
`ID, name (verb-goal), primary actor, stakeholders & interests, preconditions, trigger,
main success scenario (numbered 3–9 steps), extensions (2a, 3a… with condition → steps),
postconditions (success guarantee / minimal guarantee), business rules, NFRs, open issues.`
- Use for: payment checkout, account recovery, KYC, tournament registration.

## NFR catalogue — ISO/IEC 25010:2023 product quality (9 characteristics)
(verify: subcharacteristic names vs the purchased standard; 2023 edition replaced 2011)
| Characteristic | Subcharacteristics | Example measurable NFR |
|---|---|---|
| Functional suitability | completeness, correctness, appropriateness | 100% of BR-n covered by AC |
| Performance efficiency | time behaviour, resource utilization, capacity | API p95 < 200 ms at 2k RPS; app cold start < 5 s on min-spec device; RAM < 1.2 GB |
| Compatibility | co-existence, interoperability | works with iOS 16+ / Android 8+ (API 26); OpenAPI contract |
| Interaction capability (ex-usability) | recognizability, learnability, operability, user error protection, engagement, inclusivity, assistance, self-descriptiveness | FTUE complete by ≥ 80% of new users; WCAG 2.2 AA for web/back-office |
| Reliability | faultlessness, availability, fault tolerance, recoverability | 99.9% monthly (≈ 43 min downtime); RPO 5 min, RTO 1 h |
| Security | confidentiality, integrity, non-repudiation, accountability, authenticity, resistance | all wallet ops audited with actor + reason; OWASP ASVS L2 |
| Maintainability | modularity, reusability, analysability, modifiability, testability | config change without client release; ≥ 70% domain unit coverage |
| Flexibility (ex-portability) | adaptability, scalability, installability, replaceability | scale to 3x peak CCU by adding nodes; install size < 200 MB |
| Safety (new) | operational constraint, risk identification, fail safe, hazard warning, safe integration | fail closed on RNG/payment errors; photosensitivity warning |
Also capture: localization (locales, RTL), legal/data residency, observability (logs/metrics/
traces), supportability (admin tools), cost (cloud budget/month), platform cert rules.
NFR phrasing: `<system/part> shall <quality> <metric> <threshold> under <condition>, measured by <method>.`

## Prioritization
| Method | Use for | Rule |
|---|---|---|
| MoSCoW (DSDM) | release scope | Must ≤ ~60% of effort, Should ~20%, Could ~20%; Won't = explicit this time |
| RICE (Intercom) | backlog ordering | (Reach × Impact × Confidence) / Effort; Impact 3/2/1/0.5/0.25; Confidence 100/80/50% |
| Kano | feature discovery/delight | Basic (must-be), Performance (linear), Attractive (delight), Indifferent, Reverse |
| WSJF (SAFe) | flow with delay cost | (Business value + Time criticality + Risk reduction) / Job size |
| Cost of delay | deadline-driven (events, store features) | quantify $/week of delay |
- Kano survey: functional + dysfunctional question pair per feature; classify via Kano table.
- Record the score inputs, not just the rank; revisit when Confidence < 50%.

## Story mapping (Jeff Patton, 2014)
- Backbone (left→right): user activities in narrative order → steps under each.
- Body (top→bottom): stories per step ordered by priority.
- Horizontal slices: walking skeleton (thinnest end-to-end), then release 1, 2… each tied to an outcome.
```
Activities: | Install & FTUE | Play round    | Buy coins       | Claim rewards |
Skeleton:   | guest login    | 1 slot, spin  | 1 SKU, IAP      | daily bonus   |
Release 1:  | social login   | 3 slots       | offers wall     | streaks       |
Release 2:  | account link   | tournaments   | personalized    | missions      |
```

## Jobs-to-be-done
- Job statement: `When <situation>, I want to <motivation>, so I can <expected outcome>.`
- Outcome statement (Ulwick ODI): `<direction: minimize> <metric: time/likelihood> <object> <context>`.
- Forces of progress: push of situation, pull of new solution vs anxiety + habit.
- Use JTBD in discovery/BRD; convert to stories only after the job is validated.

## Traceability matrix
```
| Goal | BR    | Story  | AC scenario         | Design/API         | Test ID   | Status |
| G1   | BR-12 | US-031 | claim once per day  | POST /bonus/claim  | TC-118    | passed |
```
- Forward trace (goal → test) proves coverage; backward trace (test → goal) finds gold-plating.
- Change request → find affected rows → impacted stories, APIs, tests → estimate → decide.
- Keep it in one markdown table per area; IDs are stable, never reused.

## Requirement quality smells
- Ambiguity words: fast, easy, flexible, robust, user-friendly, etc., and/or, support, handle.
- Passive voice hiding the actor ("data is validated" — by whom?). Missing negative cases.
- Compound "shall X and Y" → split. Design disguised as need ("use Redis") → constraint or move to SA.

## Sources
- Bill Wake, "INVEST in Good Stories, and SMART Tasks" (2003) https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
- Mike Cohn, "SPIDR: Five Simple but Powerful Ways to Split User Stories" https://www.mountaingoatsoftware.com/blog/five-simple-but-powerful-ways-to-split-user-stories
- Jeff Patton, "User Story Mapping", O'Reilly, 2014
- Cucumber, Gherkin reference https://cucumber.io/docs/gherkin/reference/
- ISO/IEC 25010:2023 product quality model https://www.iso.org/standard/78176.html
- Intercom, RICE prioritization https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- DSDM/Agile Business Consortium, MoSCoW prioritisation https://www.agilebusiness.org/?p=1907
- Alistair Cockburn, "Writing Effective Use Cases", Addison-Wesley, 2000
