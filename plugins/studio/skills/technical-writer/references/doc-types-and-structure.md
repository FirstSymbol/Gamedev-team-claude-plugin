# Doc types and structure

## Diátaxis (diataxis.fr) - one page, one type
| Type | Reader need | Axis | Form | Example |
|---|---|---|---|---|
| Tutorial | learn by doing (newcomer) | action + acquisition | guided lesson, guaranteed success, no choices | "Build your first slot feature with the SDK" |
| How-to guide | complete a task (competent user) | action + application | numbered steps to a goal, assumes knowledge | "Rotate the payment API key" |
| Reference | look up facts | cognition + application | dry, complete, structured like the code | API reference, config table, CLI flags |
| Explanation | understand why | cognition + acquisition | discussion, context, trade-offs | "Why the wallet is server-authoritative" |
- Smells: tutorial explaining theory → move to explanation; reference with steps → move to how-to.
- Docs folder layout: `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/`,
  `docs/adr/` (or link `.team/decisions/`), `docs/runbooks/`.

## README (repo/service/package front door)
Order (keep ≤ ~150 lines; link out for depth):
1. Name + one-line purpose; badges optional (build, version).
2. What it does / does not do (scope, owners, status).
3. Quickstart: prerequisites (exact versions) → install → run → verify (expected output).
4. Configuration table: key | env var | default | required | description.
5. Usage: 1-3 most common tasks with code.
6. Development: build, test, lint commands; project layout.
7. Deployment/operations: link runbooks, dashboards, alerts.
8. Links: API reference, architecture, changelog, contributing, license.
### .NET service specifics
- Prereqs: .NET SDK version from `global.json`; Docker for dependencies; `dotnet user-secrets`
  for local secrets (never commit secrets).
- Commands: `dotnet restore`, `dotnet build`, `dotnet test`, `dotnet run --project src/<Api>`;
  `docker compose up -d` for DB/cache. Health endpoint and OpenAPI URL (e.g. `/openapi/v1.json`).
- Config: list `appsettings.json` sections and env var overrides (`Section__Key`).
### Unity package specifics
- Install via Package Manager: git URL (`https://<host>/<repo>.git?path=/Packages/<name>#v1.2.0`),
  scoped registry, or local `file:` path; minimum Unity version (`"unity": "6000.3"` in package.json).
- Dependencies, supported platforms/render pipelines, samples (`Samples~`), known limitations.
- README is for contributors; user manual in `Documentation~` (see api-docs.md).

## Architecture documentation
| Format | Use |
|---|---|
| C4 model (context, container, component, code) | diagrams at the right zoom; Mermaid/PlantUML/Structurizr as code |
| arc42 (12 sections) | full architecture doc template for larger systems |
| ADRs (Nygard: context, decision, consequences) | one decision per file; immutable, superseded by new ADR |
- Minimal architecture doc: goals & constraints, context diagram, containers diagram, key
  flows (sequence), data ownership, cross-cutting (auth, logging, errors), deployment view,
  quality attributes with numbers, risks/tech debt, ADR index.
- Assemble from tech-lead-architect/system-analyst artifacts; do not invent decisions.

## Runbooks (templates/runbook.md)
- One runbook per alert or operational task; title = alert name or task.
- Structure: summary & impact → severity → preconditions/access → diagnosis steps (commands
  with expected output) → mitigation options (fastest safe first) → escalation (who, when) →
  verification → rollback → follow-up (postmortem link).
- Rules: commands copy-pasteable with placeholders; each step states expected result; no
  tribal knowledge ("restart the thing"); link dashboards by name/URL; "last tested" date.
- Validate by dry run with devops-sre-engineer; record gaps.

## Other common docs
| Doc | Must contain |
|---|---|
| CONTRIBUTING.md | branch/commit convention, PR checklist, code style, how to run tests |
| Onboarding guide | access requests, tools + versions, first build in < 1 day, who to ask |
| Migration guide | from → to versions, breaking changes table, step-by-step, rollback |
| Troubleshooting/FAQ | symptom → cause → fix, searchable error messages verbatim |
| Postmortem (blameless) | timeline, impact, root cause(s), what went well/poorly, action items with owners |

## Docs-as-code
- Markdown in repo, reviewed in PRs with the code change; owners via CODEOWNERS.
- Lint: markdownlint (format), Vale (style rules; Google/Microsoft packages available),
  link checker (lychee or markdown-link-check) in CI.
- Diagrams as code (Mermaid renders on GitHub/GitLab/Azure DevOps).
- "Last verified: YYYY-MM-DD" on runbooks and how-tos.

## Sources
- Diátaxis, Daniele Procida https://diataxis.fr/
- C4 model, Simon Brown https://c4model.com/
- arc42 template https://arc42.org/overview
- Michael Nygard, "Documenting Architecture Decisions" (2011) https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Google SRE Book, "Being On-Call" / playbooks https://sre.google/sre-book/being-on-call/
- Unity Manual, Package layout https://docs.unity.com/en-us/engine/current/manual/packages-list/cus-pkg-lp/cus-pkg-development/cus-pkg-structure/cus-layout
