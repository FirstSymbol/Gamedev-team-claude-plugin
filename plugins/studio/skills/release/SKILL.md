---
name: release
description: Run the studio release-readiness gate (quality, platform, compliance, ops, marketing) for a build or version.
disable-model-invocation: true
argument-hint: <version/build and target platforms/stores>
---
# /studio:release — release readiness
Release: $ARGUMENTS

Follow `studio:team-protocol`. Reply in the user's language. Never submit, publish, deploy
to production, or change store listings without explicit human confirmation.

Spawn in ONE parallel wave (only relevant ones):
- `qa-lead` → quality gate: open S1/S2 bugs, regression results, test coverage of new
  features, perf/memory on target devices, crash-free rate target → `.team/reports/release-<v>-qa.md`.
- `release-platform-manager` → platform checklist per store/console (metadata, ratings,
  privacy labels, SDK/target API levels, cert requirements, build signing) → `…-platform.md`.
  Console or Steam release → tell it to load `studio:domain-pc-console`.
- `devops-sre-engineer` → deploy plan, migrations (expand/contract), rollback, monitoring
  and alerts, feature flags → `…-ops.md` (only if backend/live service involved).
- `compliance-advisor` → privacy/consent, age rating, loot box/odds disclosure, gambling
  licensing per region → `…-compliance.md` (only if monetization, PII, minors, or gambling).
- `marketing-manager` → store copy/ASO/launch comms readiness → `…-marketing.md`
  (only for public releases).
- `security-engineer` → if new auth/payment/network surface since last release → `…-security.md`.

Then (main thread): compile `.team/reports/release-<v>.md` with a table
`Area | Status (GO / GO with risks / NO-GO) | Blocking items | Owner`. Overall decision =
NO-GO if any area is NO-GO. `technical-writer` drafts the changelog/release notes.
Report the table and the decisions the human must make.
