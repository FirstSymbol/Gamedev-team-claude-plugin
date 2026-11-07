---
name: risk-review
description: Run a cross-discipline risk review of the project or a plan and update .team/risks.md.
disable-model-invocation: true
argument-hint: "[scope: whole project | milestone | feature path]"
---
# /studio:risk-review
Scope: $ARGUMENTS (default: whole project)

1. Main thread: `team_status.py` summary; read `.team/brief.md` and the scope's specs list.
2. Spawn `producer` (lead) with the scope. The producer gathers risks per discipline,
   spawning only where the scope applies, in waves of ≤ 3 (spawned leads must not spawn further):
   `tech-lead-architect` (technical/architecture/perf), `security-engineer` (security/fraud),
   `compliance-advisor` (legal/regulatory/platform policy), `qa-lead` (quality/test debt),
   `economy-monetization-designer` (economy exploits/inflation), `devops-sre-engineer`
   (ops/availability), `marketing-manager` (market/launch).
3. Each risk: ID, description (cause → event → impact), probability 1–5, impact 1–5,
   owner role, mitigation, trigger/early-warning signal, state. Merge duplicates.
4. Producer updates `.team/risks.md` (keeps existing IDs) and returns the top 10 by P×I.
5. Report to user (their language, ≤ 15 lines): top risks with mitigations, risks needing a
   human decision, what changed since last review.
