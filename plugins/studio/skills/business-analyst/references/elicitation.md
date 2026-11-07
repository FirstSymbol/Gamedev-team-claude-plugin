# Elicitation & stakeholder analysis

## BABOK v3 frame (what elicitation sits inside)
- 6 knowledge areas, 30 tasks, 50 techniques. Core concept model (BACCM): Change, Need,
  Solution, Stakeholder, Value, Context — check every requirement set touches all six.
- Elicitation & Collaboration tasks: Prepare → Conduct → Confirm results → Communicate →
  Manage stakeholder collaboration. "Confirm" = play back to the source before using it.
- Requirement types: business (why), stakeholder (who needs what), solution (functional +
  non-functional), transition (data migration, training, cutover — temporary).

## Stakeholder analysis
### Checklist of stakeholder classes (IT + gamedev)
| Class | Typical roles | Usually forgotten needs |
|---|---|---|
| End users | players (new, payer, whale, churn-risk), B2B clients | accessibility, locales, offline |
| Sponsor/owner | PO, publisher, product-manager | success metric, deadline driver |
| Operations | live-ops, community, CS/support agents | admin tools, bulk actions, audit trail |
| Finance | finance, payments, BI | reconciliation, refunds, tax, reports |
| Compliance | legal, DPO, RG officer (iGaming) | consent, KYC/AML, age gates, retention |
| Delivery | devs, QA, DevOps, art | testability, environments, config without deploy |
| External | platform holders, PSPs, ad networks, regulators | certification rules, SLAs |

### Power/interest grid (Mendelow)
| | Low interest | High interest |
|---|---|---|
| High power | Keep satisfied (summary at milestones) | Manage closely (workshops, sign-off) |
| Low power | Monitor (changelog) | Keep informed (demos, Q&A) |

### RACI per deliverable
- R does, A owns (exactly one A), C consulted before, I informed after.
- Rules: one A per row; no row without R; a person with many A's is a bottleneck → flag.
```
| Deliverable        | PM | BA | SA | GD | Compliance | QA |
| BRD sign-off       | A  | R  | C  | C  | C          | I  |
| Payment flow rules | A  | R  | C  | I  | C          | I  |
| API contract       | I  | C  | A/R| I  | I          | C  |
```

## Technique selection (BABOK techniques, condensed)
| Situation | Technique | Output |
|---|---|---|
| Existing system/docs/code | Document analysis, interface analysis | as-is rules, data fields, gaps |
| Expert knows the domain | Structured interview (30–45 min) | confirmed notes, BR list |
| Many stakeholders disagree | Facilitated workshop (≤ 8 people, 90 min) | agreed scope, priorities |
| Tacit/manual work (ops, CS) | Observation (passive or "think aloud") | real steps, workarounds |
| Large user base | Survey/questionnaire (≤ 10 questions) | quantified preference |
| Unclear UX/rules | Prototyping (paper/wireframe/clickable) | validated flow |
| Edge rules/decisions | Decision tables, business rules analysis | complete rule matrix |
| Improve idea pool | Brainstorming, benchmarking competitors | option list |
| Existing product data | Data mining with data-analyst | evidence for need |

## Interview question bank
### Opening / context
- What problem are we solving, for whom, and how do you know it is a problem (data, complaints)?
- What happens today (walk me through the last time you did it)? Where does it hurt most?
- What does success look like in 3 months? Which number moves, and by how much?
### Scope & constraints
- What is explicitly out of scope? What must not change?
- Deadlines and why (event, store feature, regulatory date, marketing beat)?
- Budget/team constraints; platforms, regions, languages, age ratings?
### Rules & data
- What are the rules/exceptions? Who decides when rules conflict?
- What data is created/read/changed? Who owns it? How long is it kept?
- What limits exist (per user/day, amounts, cooldowns)? What happens at the limit?
### Unhappy paths
- What if it fails halfway (network loss, payment declined, server timeout, app killed)?
- What if a user does it twice / concurrently / from two devices?
- How do we undo it (refund, rollback, manual correction)? Who is allowed to?
### Operations & reporting
- Who supports this after launch? What do they need to see/change without a deploy?
- What reports or alerts are needed, how often, for whom?
### Closing
- Who else should I talk to? Which document/system is the source of truth?
- What did I not ask that I should have?
Probing: "Why?" (5 whys, stop at a business goal), "Can you give an example?",
"What would happen if we did nothing?", "How often / how many?" (get numbers).

## Workshop recipe (90 min, ≤ 8 people)
1. Pre-read sent 24 h before: goal, draft scope, 3–5 decisions needed.
2. 10 min — goal + agenda + rules (timebox, parking lot).
3. 25 min — process walk-through (as-is) on shared board; capture pain points.
4. 25 min — to-be options; dot-vote or MoSCoW on capabilities.
5. 20 min — rules + edge cases for top items (decision table).
6. 10 min — decisions, owners, open questions with due dates.
- Output within 24 h: decisions list + updated artifacts; silence = consent only if stated upfront.

## Observation & document analysis
- Observation: record steps, time per step, tools switched, workarounds (spreadsheets,
  copy-paste), error recovery. Workarounds = hidden requirements.
- Document analysis sources: existing specs, tickets, CS macros/FAQ, logs, DB schema, admin
  UI, app store reviews, competitor apps, regulations (quote clause numbers).
- Code as source (agent advantage): Grep enums, validation rules, config keys, error codes —
  they are de-facto business rules. Cite file paths in notes.

## Agent ↔ human elicitation protocol (token- and attention-efficient)
- Exhaust passive sources first (brief, repo, docs, scans) — never ask what files already answer.
- One batched round per phase; ≤ 7 questions; numbered so the human can answer "1a, 2: yes, 3 skip".
- Each question: context in ≤ 1 line + options (a/b/c) + your default assumption.
- Separate BLOCKING (cannot proceed) from DEFAULTABLE (will assume X unless told).
- Prefer closed/multiple-choice for decisions, open questions only for goals and pain.
- Proceed on defaults for non-blocking items; record them in "Assumptions" with ID A-n.
- Confirm results: play back a ≤ 10-line summary ("I understood… correct?") before the BRD.
- Never ask the human to choose technical implementation; ask for intent and constraints.

Batched question template:
```
To draft <artifact> I need 4 answers (defaults apply if you skip):
1. [BLOCKING] Target platforms? a) iOS+Android b) +WebGL c) PC  — default: a
2. Daily bonus resets at: a) 00:00 UTC b) player local midnight c) 24 h rolling — default: a
3. Can CS agents grant currency manually? yes/no; if yes, max per grant? — default: yes, 10,000, audited
4. Any regulatory market (UK/EU gambling, US sweepstakes)? — default: none, social casino only
```

## Confirming & recording
- Elicitation notes file: source, date, participants, statements (quote critical rules),
  derived requirement IDs, open questions (owner, due), conflicts.
- Conflicting statements → do not pick a side; record both, escalate to the A in RACI.
- Requirement quality checks before use: atomic, unambiguous, testable, feasible, necessary,
  traceable to source (stakeholder or document).

## Sources
- IIBA, BABOK Guide v3 — knowledge areas and tasks overview https://www.iiba.org/knowledgehub/business-analysis-standard/4-tasks-and-knowledge-areas/introducing-business-analysis-tasks/
- Modern Requirements, "BABOK knowledge areas explained" https://www.modernrequirements.com/blogs/babok-knowledge-areas-explained/
- BA Times, "BABOK Version 3 vs. Version 2" https://www.batimes.com/?p=6133
- Mendelow, A. (1991) power/interest matrix — summarized in BABOK v3 Stakeholder List, Map, or Personas technique
- Karl Wiegers & Joy Beatty, "Software Requirements", 3rd ed., Microsoft Press, 2013
