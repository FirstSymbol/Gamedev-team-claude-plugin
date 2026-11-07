# Design reviews, playtesting, FTUE

## Design review — when
| Gate | Reviews | Attendees (agents) |
|---|---|---|
| Concept → pre-production | one-pager, pillars, core loop prototype | lead, product-manager, producer, tech-lead |
| Spec → sprint (DoR) | feature spec | lead, owner designer, unity-developer, qa-engineer, ux if UI |
| Milestone (vertical slice, alpha, beta) | build vs GDD, playtest report | all leads |
| Live change | balance/economy/event change | lead, economy, liveops, data-analyst |

## Review checklist (score each: pass / issue(blocker|major|minor) / n.a.)
1. Pillar fit: which pillar(s); does it violate an anti-pillar?
2. Player goal: can the player state what to do and why within the first exposure?
3. Rules complete: triggers, effects, durations, stacking, interruptions, cancel rules.
4. States: idle/active/cooldown/disabled/fail/win; transitions drawn; no dead ends.
5. Edge cases: zero/max values, disconnect, app background, save/load mid-action, spam input.
6. Feedback: every player action has visual + audio + (mobile) haptic feedback in ≤ 100 ms.
7. Failure: failure is legible (player knows why), recoverable, and not punitive beyond intent.
8. Numbers: all tunables in a table with unit/range/default; owner named.
9. Economy impact: new sources/sinks flagged to economy-monetization-designer.
10. Content cost: assets, VO, loc strings, levels needed — confirmed with producer/art.
11. Tech feasibility & perf: unity-developer/tech-lead sign-off; network authority if MP.
12. Accessibility: remappable input, colour-blind-safe signals, subtitles, hold/toggle options.
13. Telemetry: events + success metric + target defined (data-analyst).
14. Compliance: loot boxes/odds, minors, gambling-like mechanics → compliance-advisor.
15. Acceptance criteria: testable Given/When/Then; QA can write cases from them.
- Output `.team/reports/design-review-<id>.md`: verdict (approve / approve with fixes /
  rework), findings table `# | severity | finding | owner | due`.

## Playtest program
| Stage | Method | Sample | Answers |
|---|---|---|---|
| Paper / greybox | think-aloud, observation | 3–5 per round, many rounds | is the core loop understood and repeated? |
| Vertical slice | moderated sessions + survey | 5–8 target players | fantasy, pillar moments, FTUE comprehension |
| Alpha (closed) | unmoderated + telemetry + survey | 30–200 | progression pace, difficulty spikes, session length |
| Beta / soft launch | telemetry, A/B, surveys | 1k–100k+ | retention, funnel, economy (with data-analyst, liveops) |
- 5 users find most usability problems in a formative test (Nielsen, 2000) — valid for
  comprehension/usability, not for preference, balance or retention claims.
- Recruit the target audience (motivation profile, platform); avoid devs and genre-experts
  unless testing expert content. Fresh testers for FTUE ("Kleenex testers").

### Playtest plan (write before the test)
```
Build: <version>  Date: <YYYY-MM-DD>  Method: <moderated|unmoderated|telemetry>
Research questions (≤ 5): RQ1 "Do players discover the dash-cancel without prompting?"
Hypotheses + pass bar: "≥ 4/6 players use dash-cancel by level 3"
Tasks/script: <what players are asked to do; what moderators never say>
Data: observation sheet, telemetry events <list>, survey <items>, interview prompts
Participants: n=<n>, profile <motivation/platform>, exclusions <devs, prior testers>
```
- Moderator rules: don't help, don't explain; ask "what are you thinking?" and "what do
  you expect to happen?"; log timestamps of confusion, delight, quits.

### Qualitative vs quantitative
| Telemetry (what) | Observation/interview (why) |
|---|---|
| funnel drop by step, level pass rate, attempts, deaths heatmap, session length, retention | confusion points, mental model, emotional reaction, stated reasons |
- Triangulate: never ship a fix from one source alone when the stakes are high. Telemetry
  spike + observed confusion = strong signal.
- Surveys: keep ≤ 10 items; mix 5/7-point scales with 1–2 open questions; ask after play,
  not during. Validated instruments: PENS (need satisfaction), GEQ (game experience,
  verify: licence/version). Self-reported "fun" ratings are weak; behaviour beats opinion.

### RITE (Rapid Iterative Testing and Evaluation)
- Origin: Medlock, Wixon et al., Microsoft Games Studios, 2002 (Age of Empires II tutorial).
- Loop: test one participant → team (designer + decision maker present) triages → fix
  obvious issues before the next participant → repeat; verify with participants until
  ~no new must-fix issues (AoE II: ~10 iterating sessions, then 6 with no changes needed).
- Prereqs: build can be changed within hours (data-driven tunables, scripted tutorial),
  decision maker in the room, agreed severity rule (fix if 1 participant hits a blocker that
  the team judges will recur).
- Pitfalls: changing too much at once, too many deciders, no verification phase.

### Synthesis (`.team/reports/playtest-<date>.md`)
- Issues table: `ID | observation (n/N players) | evidence (clip/time/event) | severity |
  hypothesis (cause) | proposed fix | owner`.
- Severity: blocker (can't progress / quits), major (wrong mental model, frequent
  frustration), minor (polish). Rank by severity × frequency.
- End with: pillar verdicts (proven / weak / not observed) and next test's questions.

## FTUE (first-time user experience)
- Goals: time-to-first-fun short (mobile: core action within the first ~30–60 s;
  heuristic, verify per genre); first win early; first meaningful choice in session 1;
  tease the meta loop; reason to return (session 2 hook).
- Principles (Hodent, "The Gamer's Brain", 2017): teach by doing in context, one concept at
  a time, reduce cognitive load, show-don't-tell, spaced reinforcement; allow skip for
  returning players; never block with long text.
- Instrument every step: `ftue_step_started/completed {step_id, t_since_install}`; read as a
  step funnel, not an average. Mark the "aha" step and its conversion.
- Retention benchmarks (D1/D7/D30 by percentile and genre): `studio:domain-f2p-liveops`
  (lifecycle-and-kpis) is canonical; don't restate. D1 problems usually start in FTUE.
- FTUE review: watch 5 fresh testers; every point where ≥ 2 hesitate > 5 s is an issue.

## Sources
- Medlock, Wixon, Terrano, Romero, Fulton, "Using the RITE method to improve products" (UPA 2002); summary: MeasuringU "Ten Things to Know about the RITE Method" https://measuringu.com/rite-method/
- Nielsen, "Why You Only Need to Test with 5 Users" (2000) https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/
- Hodent, "The Gamer's Brain: How Neuroscience and UX Can Impact Video Game Design" (CRC Press, 2017)
- GameAnalytics benchmarks summary (gamedevreports) https://gamedevreports.substack.com/p/gameanalytics-mobile-gaming-benchmarks
- devtodev, "Main Metrics. FTUE" https://www.devtodev.com/resources/articles/main-metrics-ftue
- Rigby & Ryan, "Glued to Games" (Praeger, 2011) — PENS
