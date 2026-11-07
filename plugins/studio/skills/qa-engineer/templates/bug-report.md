# BUG-<id>: <Area>: <what fails> <when/condition> (<platform>)
Severity: S<1-4> (proposed)  Priority: <set at triage>  Status: New  Reporter: qa-engineer  Date: <YYYY-MM-DD>
Owner: <role>  Related: <AC/spec ID, test case ID, risk ID, crash issue link>

## Environment
- Build: <version (build number), commit/CI run>   Backend env: <dev/stage>, API version <x>
- Platform/device: <model, OS version, GPU family, RAM>   Locale/timezone: <xx-XX, UTC+N>
- Account: <test player ID>   Flags/A-B: <flags, bucket>

## Preconditions
- <account state, balance, streak, settings>

## Steps to reproduce
1. <one action per step, exact values>
2. <...>

## Expected
<per spec/AC ID>

## Actual
<observable facts>

## Frequency
<x/y attempts>; first bad build: <build or unknown>; last good: <build>

## Evidence
- Video/screenshot: <path, timestamp>
- Logs: <path to Player.log / logcat / device log excerpt>   Request/trace ID: <id>
- Data: <save file / ledger entries / HAR>

## Notes
- Workaround: <none / steps>   Reach: <devices/segments affected>
- Hypothesis (unconfirmed): <suspected cause/area>

## Resolution (filled by owner / QA)
Root cause: <1-2 lines>  Fix: <PR/paths>  Regression test: <test name>  Verified in: <build>
