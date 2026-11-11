---
name: onboard
description: Onboard the studio team onto an existing project - scan, analyze and cache project context in .team/ so normal commands work with full context.
disable-model-invocation: true
argument-hint: "[--refresh] [docs: <paths>] [lessons: <notes files>]"
---
# /studio:onboard - bring the team into an existing project
Arguments: $ARGUMENTS

Follow `studio:orchestrator` and `studio:team-protocol`. Scripts:
`${CLAUDE_PLUGIN_ROOT}/skills/team-protocol/scripts/`. Reply in the user's language.
Hard rule for every step: READ-ONLY on the product. No code, config, package or git changes;
no installs, migrations or deploys. Only `.team/` is written, one file per Write/Edit call
(never Bash heredocs: multi-file heredoc chains break on Windows Git Bash).

## 0. Mode (main thread)
- `team_status.py <root>`. If `.team/context/meta.md` exists and `--refresh` is not given →
  show the context line and ask: refresh or keep. Keep → stop.
- `--refresh` → do section R only. Otherwise continue with 1.

## 1. Intake (main thread, cheap)
- `team_status.py <root> --init`; run `scan_unity_project.py` / `scan_dotnet_solution.py` when
  Unity (`ProjectSettings/`) / .NET (`*.sln*`, `*.csproj`) exist → `.team/reports/scan-unity.md`,
  `scan-dotnet.md`. Other stacks: note `package.json`, `go.mod`, etc. by Glob (names only).
- Sources: `docs:` paths from arguments + Glob for README*, CLAUDE.md, docs/**/*.md, *GDD*,
  CHANGELOG* (names only; do not read them here).
- `git log --oneline -n 30` and `git rev-parse HEAD` (commit for the cache stamp).

## 2. Analysis wave (one message, parallel; each agent: no spawning, read-only product)
- `tech-lead-architect` → `.team/context/project-map.md` from `templates/project-map.md`
  (≤ 150 lines), `.team/specs/architecture/overview.md` (C4 context/container, AS-IS),
  retroactive ADRs for decisions evident in code (`Status: accepted (retroactive)`), tech
  debt + technical risks → `.team/risks.md`. Inputs: scan reports, docs list.
- `qa-engineer` → `.team/reports/baseline.md`: run existing build + test commands if the
  toolchain is present (pass/fail/skip counts, duration, failing test names), test layout,
  flaky/missing areas. Toolchain missing → list exact commands for the human. Do not fix.
- `producer` → `.team/status.md` rows (done / in progress / next) and
  `.team/specs/plan/roadmap.md` (AS-IS) from docs, git log, TODO/FIXME counts, issue exports
  given in `docs:`. Mark every inferred item `(inferred)`.
- Game with design docs or gameplay code → `lead-game-designer`: `.team/specs/gdd/00-index.md`
  + `01-vision.md` reconstructed AS-IS from existing docs; gaps as open questions.
  Product/IT without game → `product-manager`: AS-IS `.team/specs/vision/prd.md` instead.

## 3. Lessons (only if `lessons:` given)
- `team-coach` with those files as free-form sources (team-coach step 1b) → project lessons.

## 4. Cache stamp + brief (main thread)
- `.team/brief.md` (≤ 10 lines, AS-IS: goal, stack, platforms, stage, constraints).
- `.team/context/meta.md`:
  `Commit: <sha>` / `Date: <YYYY-MM-DD>` / `Sources: <docs read>` / `Agents: <roles run>`.

## 5. Report (≤ 15 lines)
Stack + stage, baseline (build/tests green?), top 5 risks/debt, what is in progress, open
questions for the human (one batched list). Then: "Context cached in `.team/` - use
`/studio:feature`, `/studio:bugfix`, etc. Refresh after big changes: `/studio:onboard --refresh`."

## R. Refresh (`--refresh`)
1. Read `Commit:` from `.team/context/meta.md`; `git diff --stat <sha>..HEAD` and
   `git log --oneline <sha>..HEAD`. No changes → report "context is current", stop.
2. Re-run the scanners whose stack has changed files.
3. `tech-lead-architect`: update only the changed areas of `project-map.md` /
   `overview.md` (input: diff stat + log), new retroactive ADRs if needed.
4. Many test/build file changes → `qa-engineer` re-baseline. Then update `meta.md` and
   report what changed in ≤ 8 lines.

## Templates
- templates/project-map.md - the cached project map every agent reads before exploring.
