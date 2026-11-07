# Release management

## Versioning
- Marketing version = SemVer `MAJOR.MINOR.PATCH` (patch = hotfix, minor = feature release/train,
  major = big content/season or breaking save/protocol change). Pre-release: `1.4.0-rc.2`.
- Build number = monotonically increasing integer from CI (never reused, never reset per version).
| Platform | Field | Rule |
|---|---|---|
| Android | `versionName` (string) / `versionCode` (int) | versionCode must increase on every upload; max 2,100,000,000 |
| iOS | `CFBundleShortVersionString` / `CFBundleVersion` | build must be unique and increasing within a version |
| Steam | BuildID assigned by SteamPipe | put version + git SHA in build `Desc` |
| Consoles | platform-specific version/patch fields | per platform submission rules (domain-pc-console) |
| Backend | SemVer or date-based + git SHA | API version separate from service build version |
Unity (set from CI, never by hand):
```csharp
PlayerSettings.bundleVersion = version;                    // "1.4.0"
PlayerSettings.Android.bundleVersionCode = buildNumber;    // int
PlayerSettings.iOS.buildNumber = buildNumber.ToString();
```
- Expose version + build + git SHA + backend env in a debug overlay and in every crash report/analytics event.
- Content/config versions (Addressables catalog, remote config, economy tables) versioned separately and
  logged with each session.

## Release train
| Phase (2-week mobile train example) | Activity |
|---|---|
| Day 1-7 | features merged behind flags to `main`; nightly builds to internal track |
| Day 8 (branch cut) | create `release/1.4`; feature freeze; only fixes via PR to main + cherry-pick |
| Day 8-11 | regression on RC builds; qa-lead triage daily |
| Day 11 | go/no-go (qa-lead gate + platform + compliance) → human approval → submit |
| Day 12-18 | review + staged rollout; next train already in development |
- Missing the train = feature waits for the next one (flags make this cheap). No "one more feature".
- Console/PC: longer trains with cert windows; mobile live-ops content ships via config/Addressables between trains.

## Branching and tags
- Trunk-based: short-lived feature branches → `main`; `release/<major.minor>` cut per train;
  tag every submitted build `v1.4.0+1234` (annotated, signed if possible).
- Build store submissions only from tags; CI stores artifacts + symbols per tag.
- Fixes land in `main` first, then cherry-pick to `release/*` (avoid forgetting the fix in the next train).
- Backend deploys independent of client trains; contracts additive (expand/contract) so old clients keep working.

## Release checklist (generic)
- [ ] Scope frozen, release notes drafted (technical-writer), known issues listed.
- [ ] qa-lead gate verdict GO / GO with risks (report path).
- [ ] Platform checklist done (mobile-stores.md / pc-steam.md / console cert).
- [ ] Compliance sign-off where monetization, data, minors or gambling are involved.
- [ ] Backend: migrations rehearsed on staging copy, deploy + rollback plan, feature flags default states.
- [ ] Min supported client version decided; server supports N and N-1 (or the agreed window).
- [ ] Monitoring and alerts: crash-free, ANR, error rate, purchase success, economy anomalies.
- [ ] Rollout schedule with halt criteria; on-call named; comms (status page, community post).
- [ ] Human approval recorded before submission/publication.

## Hotfix process
1. Trigger: S1 in production (crash spike, money bug, exploit, legal) - qa-lead/producer declare.
2. Mitigate first: kill switch / flag off / server-side config / halt staged rollout / server rollback.
3. Branch `hotfix/1.4.1` from tag `v1.4.0+1234`; minimal fix + regression test; no unrelated changes.
4. QA: confirmation + smoke + impacted-area regression (qa-lead regression scope rules).
5. Submit with expedited review request (Apple) if critical; Play: new versionCode, resume staged rollout.
6. Tag `v1.4.1+1240`; merge/cherry-pick fix to `main`; post-mortem within 5 working days.
- Server-only fixes preferred when possible (no store review); design features so rules/config live server-side.

## Force update / minimum supported client
- Server config: `minSupportedVersion` (hard: block), `recommendedVersion` (soft: prompt), per platform,
  checked at boot before login and on API errors (`426 Upgrade Required` or custom error code).
- Android: Play In-App Updates API (immediate = blocking full-screen; flexible = background download).
  iOS: no system API - custom modal with App Store link (`itms-apps://` / product page).
- Steam/PC: launcher/store updates automatically; still enforce protocol version for online play.
- Rules: never force-update before the new version is 100% available in all regions (staged rollout,
  review delays); keep a support window (e.g. N-1 for 30 days) unless security/money requires hard block.
- Protocol/contract version in every request header; backend rejects unknown-too-old with a clear upgrade error.

## Phased rollouts
| Channel | Mechanism | Control |
|---|---|---|
| Google Play | staged rollout %, per country | increase or halt anytime; halted → ship new versionCode |
| App Store | phased release (7-day automatic ramp 1→100%) | pause up to 30 days total; release to all anytime |
| Steam | beta branch → default; previous build branch | rollback = set previous build live |
| Backend | canary/blue-green, % traffic (devops-sre-engineer) | automated rollback on SLO burn |
| Features | remote flags with % / segment targeting | instant off without client release |
Suggested mobile ramp: 1% (24 h) → 5% (24 h) → 20% (48 h) → 50% → 100%, advancing only if halt criteria are clear
(crash-free, ANR, purchase success, error rate - qa-lead gates reference).

## Kill switches
- Every risky feature (shop offers, new payment flow, event, ads placement, multiplayer mode) has a server-side
  flag checked by the server (authoritative) and the client (UI hidden).
- Kill switch list in `.team/specs/release/release-process.md`: flag name, owner, effect, tested date.
- Test kill switches in staging each release (flag off → feature gone, no errors, economy consistent).
- Defaults safe on config fetch failure (feature off for new risky features).
- Remote config tools: Unity Remote Config / Unity Gaming Services, Firebase Remote Config, LaunchDarkly,
  in-house config service (verify current product names and pricing).

## Sources
- Semantic Versioning 2.0.0 https://semver.org/
- Android Developers, Version your app https://developer.android.com/studio/publish/versioning
- Android Developers, In-app updates https://developer.android.com/guide/playcore/in-app-updates
- App Store Connect Help, Release a version update in phases https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases
- Steamworks, Uploading to Steam (branches, SetLive) https://partner.steamgames.com/doc/sdk/uploading
- Martin Fowler, Feature Toggles (Pete Hodgson) https://martinfowler.com/articles/feature-toggles.html
- trunkbaseddevelopment.com, Branch for release https://trunkbaseddevelopment.com/branch-for-release/
