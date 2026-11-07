---
name: bugfix
description: Run the studio bug pipeline - reproduce, root-cause, fix with regression test, review.
disable-model-invocation: true
argument-hint: <bug description, log, or issue link>
---
# /studio:bugfix — bug pipeline
Bug: $ARGUMENTS

Follow `studio:team-protocol`. Reply in the user's language.

1. **Triage (main thread)**: severity (S1 crash/data loss/money → S4 cosmetic), area
   (Unity client / .NET server / admin web / build / infra), owner role. S1 involving money,
   wallet, RNG or personal data → also `security-engineer`; production incident →
   `devops-sre-engineer` first (mitigate, then fix).
2. **Reproduce** → `qa-engineer`: minimal repro steps, expected vs actual, environment,
   logs, frequency → `.team/reports/bug-<id>.md`. Skip if the user gave a clear stack trace
   pointing at code — go straight to step 3.
3. **Root cause + fix** → owning engineer (`unity-developer`, `dotnet-backend-developer`,
   `frontend-developer`, `multiplayer-network-engineer`, `devops-sre-engineer`):
   write a failing regression test first, fix the cause (not the symptom), note root cause
   and blast radius in the bug report.
4. **Review** → `code-reviewer` on the diff (skip for one-line non-risky fixes).
5. **Verify** → `qa-engineer` reruns repro + regression suite for the area.
6. **Close**: changelog line via `technical-writer` if user-facing; if the same class of bug
   can recur, add a risk or a lint/test rule (note in `.team/risks.md`).
Report: root cause (1–2 lines), fix (paths), test added, residual risk.
