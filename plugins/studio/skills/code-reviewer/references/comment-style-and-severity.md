# Review comments: severity, style, verdict

## Standard (Google engineering practices)
- Approve once the change definitely improves overall code health, even if not perfect; there is no "perfect" code, only better code.
- Technical facts and data overrule opinions and personal preferences; the style guide is the authority on style.
- Design and correctness first, then tests, then naming/comments/style.
- Speed matters: respond within one business day; small PRs reviewed faster and better.
- Evidence (SmartBear/Cisco study): defect detection drops above ~200–400 LOC per review and ~60–90 min
  per session; inspection rate < ~500 LOC/hour. Large diffs → review in passes and say so.

## Severity levels
| Level | Meaning | Examples | Merge? |
|---|---|---|---|
| **blocker** | will cause incident, data loss, security hole, money error, legal issue, or build break | missing authz, SQL injection, double-spend race, secret in code, dropped serialized data, migration drops column in use | no |
| **major** | likely bug or significant maintainability/perf problem; must fix or get explicit owner sign-off | N+1 on hot path, missing tests for new logic, swallowed exceptions, breaking contract without version, per-frame allocations | no (unless waived with reason) |
| **minor** | should fix; low risk | unclear naming, missing log on error branch, small duplication, missing `AsNoTracking` on cold path | yes; fix now or follow-up |
| **nit** | optional polish, taste | wording, ordering, tiny simplifications | yes; author decides |
| **question** | need info to judge | "Is this endpoint reachable by players?" | depends on answer |
| **praise** | good pattern worth repeating | clean idempotency handling | — |
- Severity is about impact × likelihood, not effort to fix. When unsure between two levels, pick the higher only if you can name the failure scenario.
- Cap nits at 5 per review; formatter/analyzer-enforceable style is never a comment (suggest the rule instead).

## Comment format (Conventional Comments style)
```
**<severity>** `<path>:<line>` — <problem in one sentence>.
Why: <impact / failure scenario>.
Fix: <concrete suggestion or code snippet>.
```
Examples:
```
**blocker** `src/Wallet/Features/Debit/DebitHandler.cs:42` — balance is read, decremented in memory and saved without a concurrency token.
Why: two parallel debits both pass the funds check → negative balance / double spend.
Fix: conditional update `UPDATE ... WHERE balance >= @amt` (check rows affected) or `[Timestamp] uint Version` + retry; add a parallel-requests integration test.

**nit** `Assets/_Project/Runtime/UI/ShopView.cs:88` — `itemsList` → `items` (type already says list). Optional.

**question** `src/Api/Admin/PlayersEndpoints.cs:15` — is this group behind the admin policy? I can't find `RequireAuthorization` on the parent group.
```
- Comment on code, not the person ("this method" not "you"). Explain why; link docs/checklist when helpful.
- Be specific: file:line, input that breaks it, expected vs actual. Offer a fix or ask a question.
- Distinguish facts ("this throws on null") from opinions ("I'd prefer..."). Opinions are nits.
- One issue per comment; group repeated occurrences ("same at lines 40, 77, 103").
- Acknowledge good work briefly (1–3 praise items), concretely.
- Don't request out-of-scope refactors as blockers; propose a follow-up ticket instead.

## Verdict rules
| Findings | Verdict |
|---|---|
| any blocker | **request changes** |
| majors without waiver | **request changes** |
| only minor/nit/question (non-blocking) | **approve with comments** |
| nothing material | **approve** |
- State what was NOT reviewed (generated code, assets, files outside scope, large PR passes skipped).
- Re-review: check only the fixes + their blast radius; close resolved findings explicitly.

## Report hygiene
- Order findings by severity, then file. Count per severity in the summary line.
- ≤ 80 lines; link to code locations instead of pasting large snippets.
- Summarize risk in 1–3 bullets for the orchestrator (what could go wrong if merged as-is).

## Sources
- Google Engineering Practices: The Standard of Code Review https://google.github.io/eng-practices/review/reviewer/standard.html
- Google Engineering Practices: How to write code review comments https://google.github.io/eng-practices/review/reviewer/comments.html
- Google Engineering Practices: Speed of code reviews https://google.github.io/eng-practices/review/reviewer/speed.html
- Conventional Comments https://conventionalcomments.org/
- SmartBear, Best practices for code review (Cisco study) https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/
