---
name: retro
description: Run a studio retro - curate the lessons log of agent mistakes and update agent playbooks so errors are not repeated.
disable-model-invocation: true
argument-hint: "[role or focus, optional]"
---
# /studio:retro - learn from mistakes
Focus: $ARGUMENTS

Follow `studio:team-protocol`. Reply in the user's language.

1. **Snapshot (main thread)**: `python "${CLAUDE_PLUGIN_ROOT}/skills/team-protocol/scripts/lessons.py" stats <root>`.
   No lessons anywhere → tell the user and stop (nothing to learn from yet).
2. **Coach** → `team-coach`: curate project + global lessons (focus role if given), embed
   recurring/S1 rules into playbooks by scope, write `.team/reports/retro-<date>.md`
   (+ `.team/reports/pack-improvements.md` when studio roles need pack changes).
3. **Gap** → if the coach reports a missing specialty, offer `team-recruiter` to the user;
   don't spawn it without a concrete need.
4. **Report** (≤ 10 lines): lessons before → after, rules embedded (role: rule), promoted to
   global, top recurring themes, pack proposals path. If the project is the pack source repo,
   remind the user to review the diff and commit; otherwise suggest sending
   `pack-improvements.md` to the pack maintainer.
