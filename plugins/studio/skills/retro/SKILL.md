---
name: retro
description: Run a studio retro - curate the lessons log of agent mistakes and update agent playbooks so errors are not repeated.
disable-model-invocation: true
argument-hint: "[role] [from <project path> ...]"
---
# /studio:retro - learn from mistakes
Arguments: $ARGUMENTS (optional focus role; `from` + project paths to harvest)

Follow `studio:team-protocol`. Reply in the user's language.

1. **Snapshot (main thread)**: `python "${CLAUDE_PLUGIN_ROOT}/skills/team-protocol/scripts/lessons.py" stats <root>`.
   Pack scope = `<root>/plugins/studio/AUTHORING.md` exists (also check `<root>/lessons/`).
   No lessons anywhere and no source projects → tell the user and stop.
2. **Coach** → `team-coach`: curate project + global lessons (focus role if given) and the
   source projects, embed recurring/S1 rules into playbooks by scope, write
   `.team/reports/retro-<date>.md` (+ `pack-improvements.md` outside pack scope).
3. **Port roles** (pack scope): if the report lists custom roles from source projects, ask
   the user which to add to the pack; for each chosen one spawn `team-recruiter` in port
   mode with the source path. Missing specialty reported → offer `team-recruiter`.
4. **Report** (≤ 10 lines): lessons before → after, rules embedded (role: rule), promoted to
   global, top recurring themes, pack proposals path. Pack scope: remind the user to review
   `git diff` (playbooks + `lessons/`), bump `plugin.json` version, commit and push, then
   `claude plugin marketplace update studio-market`. Otherwise suggest running
   `/studio:retro from <this project>` in the pack repo.
