# Bug reporting

## Anatomy of a good report (template: templates/bug-report.md)
- **Title** = where + what + when: "Shop: coin pack purchase charges but grants 0 coins after app resume (Android)".
  Not: "Shop broken", "Bug!!!", "Purchase issue".
- **Build/env**: version + build number + commit/CI run, platform, device model, OS, backend env, account ID (test).
- **Preconditions**: account state (VIP 3, balance 5,000, streak day 6), feature flags, A/B bucket, locale.
- **Steps**: numbered, one action per step, exact values; start from a known state (fresh install / login).
- **Expected** (cite AC/spec ID) vs **Actual** (observable facts, not interpretation).
- **Frequency**: x/y attempts (e.g. 3/10); "always" only if 5/5+.
- **Severity proposal** + reach (devices/segments affected); qa-lead/triage sets priority.
- **Evidence**: video (with timestamp of failure), screenshot, logs, request IDs/trace IDs, save file.
- **Notes**: workaround, first bad build (bisect), related bugs, suspected area - mark as hypothesis.

## Repro minimization
1. Reproduce twice from a clean state; record exact build and account.
2. Remove steps one at a time; keep only those needed for the failure.
3. Reduce data: smallest account state, single device, default settings, one locale.
4. Vary one factor at a time: device/GPU family, OS, network, time (server vs device clock), account.
5. Bisect builds (last good / first bad) using CI artifacts; note the commit range.
6. For backend issues capture the failing request (curl/HTTP file) with correlation ID - often the best repro.
7. Intermittent: increase attempts (10-20), log frequency, attach every occurrence's logs; check for
   race (fast taps), timing (slow network via throttling), memory (low-RAM device).
If not reproducible: file anyway with all evidence, label `cannot-reproduce`, frequency 1/N.

## Severity guide (studio scale; full matrix in studio:qa-lead gates reference)
| Sev | Rule of thumb |
|---|---|
| S1 | crash/hang on common path, data/save/progress loss, money/currency/items wrong, security/PII, store/cert/legal fail |
| S2 | major feature or progression blocked, no workaround, or affects a key segment/device tier |
| S3 | degraded feature with workaround, noticeable perf drop, wrong but non-blocking behavior |
| S4 | cosmetic, typo, minor polish |
Bump one level when > 10% of players/devices are affected or the issue is in FTUE/purchase flow.

## Log collection
### Unity Player / Editor log paths
| Platform | Player.log |
|---|---|
| Windows | `%USERPROFILE%\AppData\LocalLow\<CompanyName>\<ProductName>\Player.log` (previous run: `Player-prev.log`) |
| macOS | `~/Library/Logs/<CompanyName>/<ProductName>/Player.log` |
| Linux / Steam Deck (native) | `~/.config/unity3d/<CompanyName>/<ProductName>/Player.log` |
| Steam Deck via Proton | inside the Proton prefix: `steamapps/compatdata/<appid>/pfx/drive_c/users/steamuser/AppData/LocalLow/<Company>/<Product>/` (verify) |
| Android | no file - logcat (below) |
| iOS | Xcode console / device log (below) |
| Editor (Windows) | `%LOCALAPPDATA%\Unity\Editor\Editor.log` |
| Editor (macOS) | `~/Library/Logs/Unity/Editor.log` |
Development builds add full stack traces; set Player Settings → Stack Trace per log type for release builds.

### Android (adb)
```bash
adb devices                                      # confirm device
adb logcat -c                                    # clear before repro
adb logcat -v threadtime Unity:V CRASH:V AndroidRuntime:E ActivityManager:I DEBUG:V *:S > repro.log
adb logcat --pid=$(adb shell pidof -s com.studio.game) -v threadtime > app.log    # only the game process
adb bugreport bugreport.zip                      # ANR traces, tombstones, system state
adb shell dumpsys meminfo com.studio.game        # memory (PSS) snapshot
adb exec-out screencap -p > screen.png; adb shell screenrecord /sdcard/repro.mp4   # evidence (max 3 min)
```
- Native crashes: tombstones (in bugreport); symbolicate with the build's symbols zip
  (Unity "Create symbols.zip" / Public symbols) - Crashlytics/Backtrace do this if symbols are uploaded.
- ANR: traces in bugreport (`/data/anr/` needs root otherwise); Play Console → Android vitals shows ANR clusters.

### iOS
- Live log: Xcode → Devices and Simulators → Open Console, or macOS Console.app (select device, filter by process);
  CLI: `idevicesyslog` (libimobiledevice).
- Crash logs: on device Settings → Privacy & Security → Analytics & Improvements → Analytics Data;
  Xcode → Window → Organizer → Crashes (TestFlight/App Store, symbolicated with dSYMs).
- Upload dSYMs to the crash reporter for every build (Unity iOS builds produce them in Xcode archive).

### Backend / web
- Correlation: include `traceId`/`X-Request-Id` from the response or client log; QA can find server logs by it.
- Web: browser DevTools console + HAR export of network; Playwright trace zip for automated failures.

### Crash reporters (live and beta)
- Firebase Crashlytics (Unity SDK), Backtrace (Unity SDK: exceptions, native crashes, OOM, hangs),
  Sentry (Unity SDK). Attach the crash issue link + affected users/devices to the bug.

## Evidence rules
- Video for anything timing/visual/flow related; trim to < 60 s, note timestamp.
- Screenshot with debug overlay (build ID, player ID, server env) when the game has one - recommend adding it.
- Never attach real player PII or payment data; use test accounts; redact tokens from logs/HAR.
- Save/progress bugs: attach the save file and server profile snapshot (JSON) for the test account.
- Economy bugs: ledger entries (transaction IDs, before/after balances).

## Bug lifecycle (default)
`New → Triaged (sev/prio/owner) → In progress → Fixed (build X) → Verified (QA, build Y) → Closed`;
`Reopened` if verification fails (comment with new evidence); `Won't fix` / `As designed` need a reason + approver.
Verification: rerun original steps on the fix build + regression of the area; add an automated regression
test for S1/S2 (link test name in the bug).

## Sources
- Unity Manual, Log files https://docs.unity3d.com/Manual/LogFiles.html
- Android Developers, Logcat command-line tool https://developer.android.com/tools/logcat
- Android Developers, Capture and read bug reports https://developer.android.com/studio/debug/bug-report
- Apple Developer, Diagnosing issues using crash reports and device logs https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs
- ISTQB CTFL Syllabus v4.0, 5.5 Defect management https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
- Backtrace Unity integration https://github.com/backtrace-labs/backtrace-unity
