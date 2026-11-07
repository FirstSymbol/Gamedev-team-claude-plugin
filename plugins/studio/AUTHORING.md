# Studio pack — authoring spec (MUST follow)

Goal: maximum professional depth at minimum token cost. Every token in a SKILL.md is paid on
every invocation; every token in a description is paid on EVERY turn of EVERY session.

## Language
- All skill/agent/reference content in English (cheaper tokens). Agents reply to the human in
  the human's language (team-protocol enforces this). No Cyrillic inside plugins/studio (the Russian user README lives at the repo root).

## Layout per role
```
plugins/studio/
  agents/<role>.md                 # thin wrapper: identity + preloaded skills
  skills/<role>/SKILL.md           # lean playbook (core, always loaded with the agent)
  skills/<role>/references/*.md    # deep knowledge, read on demand
  skills/<role>/templates/*.md     # artifact templates (optional)
```
Shared skills: `team-protocol`, `orchestrator`, `stack-unity`, `stack-dotnet`,
`domain-igaming`, `domain-f2p-liveops`, `domain-multiplayer`, `domain-pc-console`.
Do NOT duplicate shared knowledge in role skills — link to it by skill + topic name, never by
path: "see `studio:stack-unity` (addressables-and-assets)". Paths like `references/x.md` in a
SKILL.md always mean files of THAT skill (the validator checks them).
Shared knowledge skills (stack-*, domain-*) use sections: Mission / Version baseline (stack) or
Key concepts (domain) / Rules that always apply / References (read on demand).

## SKILL.md (role) — budget: ≤ 130 lines, ≤ 7,000 chars (validator limits; aim lower)
Frontmatter:
```yaml
---
name: <role>                 # kebab-case, equals folder name
description: <≤ 170 chars, trigger-first: WHAT domain + WHEN to use. No fluff words.>
---
```
Body sections, in this order (use exactly these headings; terse bullets, no prose padding):
1. `# <Role title>` + one-line **Mission**.
2. `## Owns` / `## Not mine` — responsibilities and explicit boundaries (who owns instead).
3. `## Inputs → Outputs` — what it needs, what artifacts it writes (paths under `.team/`).
4. `## Procedure` — numbered default workflow (5–12 steps), each step actionable.
5. `## Quality bar` — checklist of the definition of done for this role (5–12 items).
6. `## Risks & anti-patterns` — top 6–10 failure modes with a one-line mitigation each.
7. `## Handoffs` — `→ role: what` lines (only roles that exist in the roster).
8. `## References (read on demand)` — `- references/<file>.md — <when to read it>`.
   Every reference file MUST be listed here with a concrete trigger condition.

## references/*.md — budget: ≤ 350 lines each, one topic per file
- Dense: bullets, tables, checklists, formulas, decision rules, code snippets (C# for Unity/.NET).
- Practitioner-grade: concrete numbers (budgets, thresholds, benchmarks) with source + year.
- Mark uncertain or fast-moving facts with `(verify: <what/where>)`.
- Each file ends with `## Sources` — 3–10 URLs/books actually used (no fabricated links).
- No intro/outro fluff, no "In this document we will…". Start with content.
- Prefer 3–6 focused files per role over one giant file.

## templates/*.md
- Fill-in skeletons with `<placeholders>`; short; the agent copies into `.team/…` then fills.

## agents/<role>.md — thin wrapper (≤ 32 lines body)
```yaml
---
name: <role>
description: <≤ 210 chars. "<Role>: <scope>. Use for <triggers>." Shown to the orchestrator every turn.>
tools: <minimal whitelist, comma-separated>   # designers: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Skill (+ Bash only to run own sim/forecast scripts)
model: <opus|sonnet|haiku>                     # leads opus, specialists sonnet, routine haiku
effort: <low|medium|high>
skills: [team-protocol, <role>, <shared/domain skills it always needs>]
color: <red|blue|green|yellow|purple|orange|pink|cyan>
---
```
Body: identity (1–2 lines), "Your playbook is the preloaded `<role>` skill; if it is not in
context, invoke Skill `studio:<role>` first.", role-specific hard rules (≤ 6 bullets),
and the return contract reminder ("Return per team-protocol §Return").
Leads additionally list which specialists they may spawn (`Agent` tool) and when.
Tool whitelist guide: engineers `Read, Write, Edit, Glob, Grep, Bash, Skill` (+ WebSearch,
WebFetch if docs lookups needed); reviewers read-only `Read, Glob, Grep, Bash, Skill`;
leads add `Agent`.

## Style rules
- Imperative voice. Bullets ≤ 2 lines. Tables for comparisons. No emojis.
- Name concrete tools/APIs/versions (Unity 6.3 LTS, .NET 10 LTS, xUnit v3…), not generic advice.
- Each risk has a mitigation; each checklist item is verifiable.
- Unity/.NET specifics wherever the role touches implementation.
- Don't invent facts. If unsure, write `(verify: …)`.

## Roster (agent names — use only these in Handoffs)
Leads (opus): producer, product-manager, tech-lead-architect, lead-game-designer, qa-lead
Analysis: business-analyst, system-analyst, data-analyst
Game design: game-designer, level-designer, narrative-designer, economy-monetization-designer
Art/UX: ux-ui-designer, art-director, technical-artist
Engineering: unity-developer, dotnet-backend-developer, frontend-developer,
  multiplayer-network-engineer, devops-sre-engineer, security-engineer, code-reviewer
Quality/release: qa-engineer, release-platform-manager
Market/ops: marketing-manager, liveops-manager, compliance-advisor
Routine (haiku): technical-writer
Main thread: orchestrator (skill, not an agent)
