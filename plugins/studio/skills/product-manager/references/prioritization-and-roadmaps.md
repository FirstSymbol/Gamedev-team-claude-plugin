# Prioritization and roadmaps

## Choosing a model
| Model | Use when | Inputs | Weakness |
|---|---|---|---|
| RICE | Default for comparing many backlog ideas | reach, impact, confidence, effort | reach/impact guessed → fake precision |
| ICE | Fast triage of growth experiments | impact, confidence, ease (1-10) | very subjective; use for ordering tests only |
| WSJF / Cost of Delay | Deadlines, regulatory dates, events, dependencies | value, time criticality, risk reduction, size | relative scoring drift; needs calibration |
| Kano | Deciding feature mix for a release (basics vs delighters) | user survey (functional/dysfunctional) | needs users; categories decay over time |
| MoSCoW | Scoping a fixed-time release / milestone | must/should/could/won't | everything becomes "must" without a rule |
| Value vs effort 2×2 | Workshop with stakeholders | rough value, rough effort | coarse |
| Opportunity scoring (ODI) | Which need to address | importance, satisfaction | survey cost |
- Always record: model, scores, data sources, confidence, date. Re-score each quarter or when
  data changes. Use scores to start a discussion, not end it.

## RICE (Intercom)
- Score = (Reach × Impact × Confidence) / Effort.
- Reach: users/events per period (e.g., players per quarter who hit the flow), from analytics.
- Impact per user: 3 massive, 2 high, 1 medium, 0.5 low, 0.25 minimal.
- Confidence: 100% high (data), 80% medium, 50% low; < 50% = moonshot → run discovery first.
- Effort: person-months across product, design, engineering (round; 0.5 minimum).
- Example: FTUE fix reach 60k/qtr × impact 2 × 80% / 2 pm = 48,000; offer wall reach 15k × 3 × 50% / 3 = 7,500.
## ICE
- Impact × Confidence × Ease, each 1-10. Good for an experiment backlog (growth team); re-rank weekly.

## Cost of Delay and WSJF
- Cost of Delay (CoD) = value lost per unit time by not having it (e.g., $/week, retention pts/week).
- CD3 = CoD / duration — maximizes value delivered over time (Reinertsen).
- SAFe WSJF = (user-business value + time criticality + risk reduction/opportunity enablement) / job size;
  score each column relatively (modified Fibonacci 1, 2, 3, 5, 8, 13, 20) with the smallest item = 1 per column.
- Urgency profiles: standard (linear), fixed date (holiday event, platform deadline, regulation
  in force date), expedite (outage, store compliance), intangible (tech debt that will bite).
- Games: seasonal events and platform SDK deadlines are fixed-date CoD; schedule backward from them.

## Kano
| Category | Present | Absent | Game example |
|---|---|---|---|
| Must-be (basic) | taken for granted | strong dissatisfaction | save works, fair odds disclosure, no crashes |
| Performance (one-dimensional) | more is better | less is worse | load time, reward amount, matchmaking speed |
| Attractive (delighter) | delight | not missed | surprise reward, emotes, photo mode |
| Indifferent | no effect | no effect | rarely used settings |
| Reverse | some dislike | some like | forced social sharing |
- Survey pair: "How do you feel if the product has X?" / "…does not have X?" (like / expect /
  neutral / tolerate / dislike); classify with the Kano table; ≥ 20-30 respondents per segment.
- Release rule: all must-bes first, enough performance to compete, 1-2 delighters for differentiation.
- Delighters become basics over time (genre conventions) — re-survey yearly.

## MoSCoW (with rules that keep it honest)
- Must: release fails without it (legal, pillar, core job). Must ≤ 60% of capacity.
- Should: important, workaround exists. Could: nice, first to cut. Won't (this time): explicit.
- Link to producer's cut list: Should + Could ranked = cut list.

## Roadmaps
- Now-Next-Later (Janna Bastow): columns of problems/outcomes, not dated features.
| Column | Certainty | Granularity | Dates |
|---|---|---|---|
| Now | committed, in delivery | specific initiatives with metrics | yes (producer forecast) |
| Next | validated problems, discovery underway | opportunity + candidate solutions | quarter at most |
| Later | strategic bets, unvalidated | themes/outcomes | none |
- Each item: outcome/metric, target segment, evidence level, owner. Link to OST and OKR.
- Game roadmaps add a live calendar (seasons, events) owned by liveops-manager and a milestone
  plan owned by producer; the PM roadmap shows why, the producer plan shows when.
- Publish external roadmaps (community) only with "Next/Later" stripped of dates; get marketing review.

## OKRs
- Objective: qualitative, inspiring, time-boxed (quarter). Key Results: 2-4 measurable outcomes
  (not tasks) with baseline → target. Initiatives (features) are separate, below KRs.
- Good KR: "Raise D7 retention of new players from 14% to 17%". Bad KR: "Ship daily streak".
- Committed vs aspirational OKRs (Doerr): committed = 100% expected; aspirational ≈ 70% is success.
- Max 3 objectives per team per quarter; weekly check-in with confidence (1-10); end-of-quarter
  scoring 0.0-1.0 and retro.
- Tie to North Star input metrics: each KR should move an input metric.

## North Star metric and input tree
- North Star = the single metric that best captures value delivered to users and predicts
  long-term business results. Criteria: expresses customer value, leading indicator of revenue,
  measurable, actionable by teams, understandable.
- Examples: social casino — weekly active spinners with ≥ 3 sessions; mobile F2P — D7-retained
  new players per week or weekly engaged players; multiplayer PC — weekly matches completed per
  active player; B2B SaaS — weekly active teams completing core workflow. (Choose with data-analyst.)
- Input metrics (Amplitude): 3-6 drivers across breadth (how many users do the value action),
  depth (how much), frequency (how often), efficiency (how fast to value).
```
North Star: Weekly engaged players (≥ 3 sessions/week)
 ├─ Breadth: new players activated (FTUE complete + first win) / week
 ├─ Frequency: sessions per player per week (notifications, daily rewards, events)
 ├─ Depth: % players using 2+ core features (social, collections, tournaments)
 └─ Efficiency: time to first meaningful reward (minutes)
Guardrails: crash-free sessions, refund/chargeback rate, complaint rate, payer share of revenue
```
- Revenue is a result, not a North Star (except for marketplaces where GMV ≈ value).
- Each team owns 1-2 input metrics; every roadmap item names which input it moves.

## Prioritization review checklist
- [ ] Top 10 items have model scores, data sources, and confidence.
- [ ] Fixed-date items flagged with CoD profile and backward plan.
- [ ] Must-bes (Kano/MoSCoW) covered before delighters.
- [ ] Every Now item maps to a KR and an input metric.
- [ ] Tech debt and compliance items compete with explicit CoD (not starved).

## Sources
- Sean McBride, "RICE: Simple prioritization for product managers", Intercom https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- Donald Reinertsen, "The Principles of Product Development Flow", 2009 (Cost of Delay, CD3).
- Scaled Agile, "WSJF" (archived) https://webarchive.library.unt.edu/web/20161225031923mp_/http://www.scaledagileframework.com/wsjf
- Noriaki Kano et al., "Attractive Quality and Must-Be Quality", 1984; Kano survey method.
- Amplitude, "North Star Playbook" https://amplitude.com/books/north-star/about-north-star-framework
- John Doerr, "Measure What Matters", 2018; Christina Wodtke, "Radical Focus", 2nd ed., 2021.
- Janna Bastow on Now-Next-Later, Lenny's Podcast https://www.lennysnewsletter.com/p/building-better-roadmaps-janna-bastow
