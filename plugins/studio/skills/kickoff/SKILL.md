---
name: kickoff
description: Kick off a new product/game or major initiative with the studio team (vision → plan → architecture → backlog).
disable-model-invocation: true
argument-hint: <idea, pitch or path to brief>
---
# /studio:kickoff — project kickoff
Input: $ARGUMENTS

Follow `studio:orchestrator` and `studio:team-protocol`. Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/team-protocol/scripts/`. Reply in the user's language.

Existing project already in progress → use `/studio:onboard` instead (keeps AS-IS decisions).

## 0. Intake (main thread)
- `team_status.py <root> --init`. If an existing codebase is present, run the scanners and
  save to `.team/reports/`.
- Ask the human ONE batched list (only what is unknown): target platforms, audience/market,
  business model (premium / F2P / social casino / real-money / B2B), team & timeline,
  budget constraints, must-use tech, regulatory regions. Write answers to `.team/brief.md`.

## 1. Vision (parallel)
- Game → `lead-game-designer`: one-pager + pillars `.team/specs/gdd/01-vision.md`.
- Product/IT → `product-manager`: vision + PRD-lite + success metrics `.team/specs/vision/prd.md`
  (+ opportunity tree `.team/specs/vision/ost.md` if the problem is unclear).
- Market check → `marketing-manager`: audience, competitors, positioning `.team/specs/marketing/positioning.md`.
- Regulated (gambling, kids, health, finance) → `compliance-advisor`: constraints list
  `.team/specs/compliance/market-matrix.md`.

## 2. Architecture & feasibility
- `tech-lead-architect`: architecture overview (C4 context/container), stack choices as
  ADRs, NFRs, top technical risks → `.team/specs/architecture/overview.md`, `nfr.md` + ADRs.
- Multiplayer / live service → include `studio:domain-multiplayer` / `studio:domain-f2p-liveops`.

## 3. Plan
- `producer`: milestones (prototype → vertical slice → alpha → beta → launch or MVP
  phases), roadmap, staffing assumptions, risk register seeded → `.team/specs/plan/roadmap.md`,
  `.team/specs/plan/raid.md`, `.team/risks.md`.
- `business-analyst` or `game-designer`: first backlog slice (epics → stories for the
  first milestone) → `.team/specs/backlog/`.

## 4. Review with the human
- Present ≤ 15 lines: vision, pillars/value prop, architecture choice, milestone plan,
  top 5 risks, decisions they must make. Do not start building until the human confirms.
