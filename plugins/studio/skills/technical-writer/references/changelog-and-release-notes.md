# Changelog and release notes

## Three audiences, three artifacts
| Artifact | Reader | Source | Tone |
|---|---|---|---|
| `CHANGELOG.md` | developers/integrators | curated commits/PRs | precise, technical |
| Release notes (internal) | QA, ops, CS, LiveOps | changelog + tickets + known issues | operational |
| Player patch notes / store "What's new" | players | release notes filtered to player value | friendly, short, no jargon |

## Keep a Changelog 1.1.0
```markdown
# Changelog
All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-11-07
### Added
- Daily bonus wheel endpoint `POST /v1/bonus/wheel/spin`.
### Changed
- **Breaking:** `WalletDto.balance` is now `long` (was `int`). See migration below.
### Deprecated
- `GET /v1/bonus/daily` - use `/v1/bonus/wheel` (removal in 2.0.0).
### Removed
### Fixed
- Double-grant on purchase retry when the store callback arrives twice (#482).
### Security
- Bumped `System.Text.Json` to fix <advisory ID>.

[Unreleased]: https://<host>/<repo>/compare/v1.4.0...HEAD
[1.4.0]: https://<host>/<repo>/compare/v1.3.2...v1.4.0
```
- Rules: newest first; one section per version with ISO date; only the six types above;
  `[Unreleased]` at top collects upcoming changes; yanked versions marked `[YANKED]`.
- Write for humans: what changed + impact; link issue/PR; never paste raw git log.

## Semantic Versioning 2.0.0
| Bump | When | Example |
|---|---|---|
| MAJOR | incompatible public API change | 1.4.0 → 2.0.0 |
| MINOR | backward-compatible feature | 1.4.0 → 1.5.0 |
| PATCH | backward-compatible fix | 1.4.0 → 1.4.1 |
- Pre-release `1.5.0-beta.2` (lower precedence than `1.5.0`); build metadata `+build.417`
  (ignored for precedence). `0.y.z` = anything may change; `1.0.0` defines the public API.
- "Public API" must be declared: HTTP contracts, NuGet/UPM package API, save format, config keys.
- Games: player-facing version (`1.12.0`) is marketing; also track build numbers:
  Android `versionCode` (monotonic integer), iOS `CFBundleVersion`; Unity `PlayerSettings.bundleVersion`.

## Conventional Commits 1.0.0
```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]   e.g. BREAKING CHANGE: <what and migration>   Refs: #482
```
| Type | SemVer effect | Changelog section |
|---|---|---|
| `feat` | MINOR | Added |
| `fix` | PATCH | Fixed |
| `!` or `BREAKING CHANGE:` footer | MAJOR | Changed (Breaking) / Removed |
| `perf`, `refactor` | PATCH or none | Changed (if user-visible) |
| `docs`, `test`, `build`, `ci`, `chore`, `style`, `revert` | none | omit unless user-visible |
(types beyond feat/fix follow @commitlint/config-conventional)
- Tooling: release-please, semantic-release, git-cliff (changelog generation); .NET versioning
  from git: MinVer, GitVersion, Nerdbank.GitVersioning; commit linting: commitlint.
- Generated changelog = draft; the writer curates wording and groups.

## Internal release notes (per build to QA/ops/CS)
- Header: version, build number(s), platforms, date, environment, release owner.
- Sections: Highlights → Breaking/migrations → New → Changed → Fixed (ticket IDs) →
  Config/feature flags/remote-config changes → Known issues (with workarounds) →
  Rollback plan → Monitoring to watch.

## Player patch notes
- Lead with what players feel: new content, events, balance, fixes. Group: New / Improved /
  Balance (old → new numbers) / Fixed / Known issues.
- Plain language, second person, no ticket IDs, no internal names, no blame.
- Balance changes with concrete values: "Daily bonus: 5,000 → 7,500 coins".
- Never promise future features or dates; avoid odds/payout claims unless approved by
  compliance-advisor (social casino/gambling).
- Localize: provide loc keys or a translation sheet; keep sentences short for expansion.

## Store "What's new" limits
| Store | Field | Limit |
|---|---|---|
| Google Play | Release notes ("What's new") | 500 Unicode characters per language (Play Console Help, 2026) |
| Apple App Store | What's New in This Version | 4,000 characters (App Store Connect Help, 2026) |
| Steam | Event / announcement (patch notes) | no tight limit; use headline + summary + body (verify Steamworks event rules) |
| Consoles | per platform holder rules | verify with release-platform-manager |
- Write a 500-char version first (fits everywhere), then a long version for Steam/App Store.
- First line carries the key message (often the only line shown before "more").

## Example: player note (Google Play, ≤ 500 chars)
```
New: Pharaoh's Gold slot is here - spin for free spins with expanding wilds!
Improved: Faster lobby loading and smoother reel animations.
Balance: Daily bonus raised from 5,000 to 7,500 coins.
Fixed: Rare issue where purchased coins appeared after a restart only.
```

## Sources
- Keep a Changelog 1.1.0 https://keepachangelog.com/en/1.1.0/
- Semantic Versioning 2.0.0 https://semver.org/spec/v2.0.0.html
- Conventional Commits 1.0.0 https://www.conventionalcommits.org/en/v1.0.0/
- commitlint config-conventional https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional
- Google Play Console Help, prepare and roll out a release https://support.google.com/googleplay/android-developer/answer/9859348
- Apple App Store Connect, platform version information https://developer.apple.com/help/app-store-connect/reference/platform-version-information
