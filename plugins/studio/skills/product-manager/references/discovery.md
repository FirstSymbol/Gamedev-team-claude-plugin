# Product discovery

## Four product risks (Cagan) — discovery exists to retire them before build
| Risk | Question | Owner | Cheap test |
|---|---|---|---|
| Value | Will they choose/buy/use it? | product-manager | fake door, landing page, concierge, pre-order |
| Usability | Can they figure it out? | ux-ui-designer | clickable prototype, 5-user usability test |
| Feasibility | Can we build it with our time/tech/skills? | tech-lead-architect | spike, tech prototype |
| Viability | Does it work for the business (cost, legal, brand, channels)? | product-manager | stakeholder review, unit economics, compliance-advisor |
- Torres adds ethics (could it harm users/society?) as a fifth assumption type. Games: add
  "fun" (is the loop engaging?) — owned by game-designer, tested by playtest.

## Problem framing
- Problem statement: "<Segment> struggles to <job/progress> when <context>, because <cause>,
  evidenced by <data>. This matters now because <trigger>. Success = <outcome metric change>."
- 5 Whys on solution requests until a user need or business outcome appears.
- Separate: business outcome (revenue, retention) → product outcome (behavior the team can
  move: e.g., % new players completing FTUE) → output (feature). Teams own product outcomes.
- Size the problem: affected users × frequency × severity; check data before interviews.

## Jobs To Be Done
- Job statement: "When <situation>, I want to <motivation>, so I can <expected outcome>."
- Forces of progress (switch interview): push of current situation + pull of new solution vs
  anxiety of new + habit of present. Design to amplify push/pull, reduce anxiety/habit.
- Jobs are solution-agnostic and stable; competitors = anything hired for the same job (a
  casino app competes with mobile puzzle games for "5-minute break thrill").
- Game players' jobs: relax/kill time, mastery, social status, collection/completion,
  self-expression, competition, escapism — map to motivation models (Quantic Foundry) with game-designer.
- Outcome-driven expectations (Ulwick): "minimize the time it takes to <step>" statements,
  scored by importance vs satisfaction to find underserved needs.

## Opportunity Solution Tree (Teresa Torres)
```
Outcome (one product outcome metric)
 └─ Opportunities (needs, pains, desires — from interviews/data; parent→child = more specific)
     └─ Solutions (≥ 3 per target opportunity)
         └─ Assumption tests (riskiest assumptions per solution)
```
- One outcome per tree; split shared outcomes by segment or journey step.
- Opportunities are framed as customer needs, not solutions in disguise (test: can > 1
  solution address it?).
- Pick the target opportunity by: size, customer importance, market factors, company fit;
  don't discard by expected effort.
- Compare-and-contrast ≥ 3 solutions; test the riskiest assumptions across all three.
- Start with 3-4 story-based interviews; refresh the map every 3-4 interviews; interview weekly.
- Store as `.team/specs/vision/ost.md` (nested bullets; IDs O-n, S-n, A-n).

## Customer interviews
- Goal: collect specific past stories ("Tell me about the last time you…"), not opinions or
  predictions ("Would you use…?" is banned).
- Script: warm-up (2 min) → story prompt → dig (what happened next? why? what did you try?) →
  current workarounds → close (who else should we talk to?). 30 min; one interviewer + note taker.
- Recruit: 5-8 per segment surfaces most themes for a focused question; continuous weekly beats
  big batches. Players: Discord/community, in-game survey opt-in, playtest panels.
- Synthesis: interview snapshot per session (quote, story, opportunities, insights) →
  affinity clusters → update OST.
- Agent team: product-manager drafts the script and synthesis template; humans run interviews;
  agents synthesize transcripts provided in `.team/reports/interviews/`. Never fabricate users or quotes.

## Assumption mapping
1. Story-map the solution's steps; list assumptions per step and per risk type.
2. Plot on 2×2: importance (if wrong, does it fail?) × evidence (how much do we know?).
3. Test the high-importance / low-evidence quadrant first ("leap of faith").
4. Write each test: "We believe <assumption>. We'll run <test> with <n> <users>. We're right
   if <metric ≥ threshold> by <date>." Set the threshold BEFORE running.

## Test methods (cheapest first)
| Method | Tests | Effort | Signal |
|---|---|---|---|
| Data mining (existing analytics, reviews, tickets) | value, size | hours | behavior at scale |
| One-question survey (in-app) | value, segment | 1 day | stated preference (weak) |
| Fake door / painted door (button → "coming soon") | demand | 1-3 days | CTR vs threshold; disclose honestly |
| Landing page / store page test (CPI/CTR test) | value, positioning | days, ad budget | conversion; standard for game concepts |
| Clickable prototype (Figma) | usability, value | days | task success, comprehension |
| Wizard of Oz / concierge | value, workflow | days-weeks | real usage with manual backend |
| Paper/greybox game prototype | fun, comprehension | days | playtest metrics, retention proxy |
| Technical spike | feasibility | 1-5 days | works / perf numbers |
| A/B test in product | causal impact | weeks | metric delta with significance (data-analyst) |
- Fake doors in paid flows or for minors: check store policy and ethics; never take money
  for nonexistent items; route to compliance-advisor.
- Game concepts: art/theme CPI tests on ad networks before production are standard for mobile
  (compare CPI and CTR across 3-5 concepts) (verify: current costs with marketing-manager).

## Discovery cadence
- Dual-track: discovery runs one or two cycles ahead of delivery; same team.
- Weekly: ≥ 1 customer touchpoint, OST update, 1-3 assumption tests running.
- Exit to delivery when: value + usability evidence above thresholds, feasibility confirmed,
  viability reviewed. Document in PRD "Evidence" section.
- Kill criteria are set before the test; respect them (sunk cost is not evidence).

## Sources
- Teresa Torres, "Continuous Discovery Habits", 2021; Product Talk, "Opportunity Solution Trees" https://www.producttalk.org/opportunity-solution-trees/
- Marty Cagan, "Inspired", 2nd ed., 2017; SVPG, "The Four Big Risks" https://www.svpg.com/four-big-risks/
- Clayton Christensen et al., "Competing Against Luck", 2016 (JTBD); Bob Moesta, "Demand-Side Sales 101", 2020 (forces of progress).
- Tony Ulwick, "Jobs to be Done: Theory to Practice", 2016 (outcome-driven innovation).
- Rob Fitzpatrick, "The Mom Test", 2013 (interview questions about past behavior).
- David Bland & Alex Osterwalder, "Testing Business Ideas", 2019 (assumption mapping, experiment library).
