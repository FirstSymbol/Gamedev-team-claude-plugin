---
name: team-protocol
description: Studio team operating rules - .team/ blackboard, handoffs, return format, DoR/DoD, escalation. Preloaded into every studio agent.
---
# Studio team protocol
Mission: many agents, one team, minimal tokens. Every studio agent follows this.

## Language
- Talk to the human in the human's language (Russian if they write Russian). Artifacts in
  `.team/` follow the project's existing doc language; default English. Code/identifiers: English.

## Blackboard: `.team/` in the target project root (create if missing)
```
.team/brief.md            goal, scope, constraints, non-goals (orchestrator/producer)
.team/status.md           board table: ID | task | owner | state | artifact
.team/risks.md            risk register: ID | risk | P | I | owner | mitigation | state
.team/decisions/ADR-NNN-<slug>.md   decisions (templates/adr.md)
.team/specs/<area>/...    by area: vision/ (prd, ost, product roadmap) plan/ (roadmap, raid)
                          architecture/ (overview, nfr, perf-budget.md) gdd/ (00-index.md:
                          section|owner|status, 01-vision.md) <feature>/ (design.md, stories/,
                          system-spec.md + api/, ux/) api/ (CHANGELOG.md for contract changes)
                          analytics/ (tracking-plan.md, metrics.md) art/ (style, tech-art-budget.md)
                          economy/ liveops/ marketing/ qa/ release/ ops/ security/ netcode/ compliance/
.team/handoffs/H-NNN-<from>-to-<to>.md
.team/reports/...         test reports, reviews, analyses, playtest notes
.team/lessons/<role>.md   mistakes turned into rules (scripts/lessons.py; common.md = all roles)
.team/context/            project cache from /studio:onboard: project-map.md, meta.md (commit)
```
- Write artifacts to files; pass PATHS, not contents, between agents.
- Before working, read only what you need: `brief.md`, your handoff, files it names.
- Never rewrite another role's artifact wholesale; append a `## <role> notes` section or
  open a handoff. Status board: update only your own rows.
- IDs: next free number in the folder (glob first). Dates ISO `YYYY-MM-DD`.

## Handoff file (templates/handoff.md) — ≤ 25 lines
`Goal / Context (paths) / Done so far / Deliverable expected / Acceptance criteria /
Constraints / Open questions / Deadline-priority`.

## Return to caller (MANDATORY, ≤ 15 lines, no preamble)
```
STATUS: done | partial | blocked
ARTIFACTS: <paths written/changed>
SUMMARY: <≤ 5 bullets, facts only>
DECISIONS: <made or needed, with ADR path>
RISKS: <new/raised, with risks.md IDs>
LESSONS: <IDs added/bumped, or "none">
NEXT: <recommended next role + task>
```
Do not paste file contents back. Do not restate the task.

## Lessons (do not repeat mistakes)
Script: `python "<scripts dir>/lessons.py" <cmd> <project root> --role <your role>` (see Token discipline).
- **Before work**: `list --role <you> [--tags <area>]` (project + global, ≤ 25 lines). Treat
  each listed rule as a hard rule for this task; S1 rules override your playbook defaults.
- **After work, record a lesson** (`add --sev --tags --rule --evidence`) when: your build/test
  failed and you fixed it; a reviewer/QA/human found a defect in your work; a wrong assumption
  blocked you; a fix took > 1 attempt; an agent you called returned unusable output.
- code-reviewer, qa-engineer, security-engineer: for each blocker/major found, add the lesson
  under the AUTHOR's role. Orchestrator/leads: routing or handoff mistakes under own role.
- Rule = one generic, actionable sentence: "Do X when Y" / "Never X; instead Y" (≤ 220 chars).
  Not a bug diary: no secrets, personal data or one-off facts. Duplicates are auto-bumped
  (Hits) - recurring = most important. Sev: S1 money/data/security/crash, S2 rework, S3 minor.
- Never edit lesson files by hand; use `lessons.py`. `team-coach` curates them (`/studio:retro`).

## Definition of Ready (before starting)
- Goal and acceptance criteria are explicit; inputs exist at stated paths; owner of each
  open question known. If not ready → STATUS: blocked with the precise missing item.

## Definition of Done (generic; roles add their own)
- Deliverable at stated path; acceptance criteria checked one by one; assumptions listed;
  risks logged; lessons recorded; status row updated; next handoff named.
- Code: builds, tests pass, no new warnings from analyzers, reviewed by code-reviewer for
  non-trivial changes.

## Escalation & conflict
- Scope/priority conflict → producer. Product value/KPI → product-manager. Technical
  disagreement → tech-lead-architect (ADR). Design vision → lead-game-designer.
  Quality/release go-no-go → qa-lead. Legal/regulatory doubt → compliance-advisor
  (never guess on law; mark "needs human legal review").
- Irreversible or external actions (publishing, payments, store submission, deleting data,
  git push/force-push, prod deploy) → stop and ask the human.

## Token discipline
- Existing `.team/context/project-map.md` → read it BEFORE any Glob/Grep of code; trust it for
  layout, commands, conventions; Grep only to confirm specifics. Wrong or missing facts →
  note them in your return (NEXT: `/studio:onboard --refresh`); never rewrite it yourself.
- Use scripts for discovery instead of browsing trees. Scripts dir:
  `${CLAUDE_PLUGIN_ROOT}/skills/team-protocol/scripts/` — `scan_unity_project.py <dir>`,
  `scan_dotnet_solution.py <dir>`, `team_status.py <dir> [--init]`, `lessons.py <cmd> <dir> ...`
  (run: `python "<scripts dir>/<script>" <project dir>`).
  Read their summary, not the file tree.
- Grep/Glob before Read; read file ranges, not whole large files. Never read `Library/`,
  `Temp/`, `obj/`, `bin/`, `node_modules/`, `.meta` files in bulk, or binary assets.
- Load a reference file only when its trigger condition in your skill applies.
- Spawn the minimum roles needed; prefer one specialist over a committee.
- Terse output: no greetings, no summaries of what you are about to do, no repetition.
- No scratch/helper files in the project or `.team/`; put throwaway scripts in the OS temp dir
  and remove them before returning.
