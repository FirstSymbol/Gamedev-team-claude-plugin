---
name: feature
description: Run the studio feature pipeline (spec → design → contracts → build → test → review → docs) for one feature.
disable-model-invocation: true
argument-hint: <feature description or path to spec>
---
# /studio:feature — feature pipeline
Feature: $ARGUMENTS

Follow the `studio:orchestrator` rules (load that skill now if it is not in context) and
`studio:team-protocol`. Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/team-protocol/scripts/`. Reply to the user in their language.

## 0. Prepare (main thread, cheap)
- `team_status.py <root> --init`; read `.team/brief.md` (create a 5-line brief if empty).
- Detect stack once: run `scan_unity_project.py` and/or `scan_dotnet_solution.py`; save to
  `.team/reports/scan-unity.md` / `scan-dotnet.md` if missing or older than the last change.
- Classify: game mechanic? (→ game design track) business/back-office? (→ BA track)
  touches API/data? UI? money/RNG/personal data? multiplayer? Note which domains apply.
- Create status rows `F-<n>.<step>` in `.team/status.md`.

## 1. Define (parallel where independent)
- Game mechanic → `game-designer` spec `.team/specs/<feature>/design.md`
  (+ `economy-monetization-designer` if currencies/prices/rewards/odds).
- Business/back-office → `business-analyst` stories + Gherkin AC `.team/specs/<feature>/stories/`;
  touches back-office data, payments or integrations → BA hands to `system-analyst` in step 2.
- Gate: acceptance criteria are explicit and testable. If questions remain, ask the human
  ONE batched question list, then continue.

## 2. Shape
- API/data/integration touched → `system-analyst` `.team/specs/<feature>/system-spec.md` +
  contract files in `.team/specs/<feature>/api/` (OpenAPI/AsyncAPI/proto, error model, sequences).
- UI touched → `ux-ui-designer` flow + screen specs `.team/specs/<feature>/ux/`.
- Money/RNG/personal data/gambling → `compliance-advisor` + `security-engineer` quick review
  (notes appended to the spec). Architecture-level change → `tech-lead-architect` ADR.
- New art/audio assets → `art-director` brief; shader/VFX/import budgets → `technical-artist`.
- Player-facing behavior worth measuring → `data-analyst` adds rows to
  `.team/specs/analytics/tracking-plan.md` BEFORE build, so engineers implement events.

## 3. Build (parallel per layer, same wave)
- Server → `dotnet-backend-developer`; client → `unity-developer`; admin web →
  `frontend-developer`; realtime → `multiplayer-network-engineer`; shaders/VFX →
  `technical-artist`. Each gets: spec paths, contract path, scan report, DoD.
- Each writes code + tests + `.team/reports/impl-<feature>-<layer>.md` (layer: client/server/web;
  netcode writes `net-<feature>.md`, tech art `techart-<feature>.md`).

## 4. Verify
- `qa-engineer`: test plan from AC, adds missing automated tests, runs `dotnet test` /
  Unity batch tests where possible → `.team/reports/test-run-<feature>.md` with pass/fail per AC.
- `code-reviewer` on the changed files → `.team/reports/review-<feature>.md`.
- Blocking findings → back to the owning engineer (max 2 loops, then escalate to tech-lead-architect).

## 5. Close
- `technical-writer` (haiku): changelog entry + docs touch-ups.
- Update status rows to done; final report to user (≤ 10 lines): what changed (paths),
  AC status, open risks, what the human must verify manually (e.g. Unity Editor play test).

## Skip rules (token economy)
- Tiny change (≤ 2 files, no API/UI/money): skip steps 1–2, one engineer + reviewer.
- No UI → skip UX. No API → skip system-analyst. No money/PII/RNG → skip compliance/security.
