# Console certification (public information only)

## Names and owners
| Platform holder | Requirement set | Process name | Public? |
|---|---|---|---|
| Sony (PlayStation) | TRC - Technical Requirements Checklist | submission / "cert" via PlayStation Partners | NDA |
| Microsoft (Xbox, PC via Microsoft Store) | XR - Xbox Requirements (formerly TCR) + Microsoft Store policies | certification via Partner Center | XR list and test cases public on Microsoft Learn / devdocs.xbox.com |
| Nintendo | Guidelines / requirement checklist | Lotcheck | NDA |
Cert checks platform compliance and stability, not fun or bugs in general - but blocking bugs fail it.

## Xbox: what fails most (Microsoft Learn, v3.0 2026-08)
| XR / test case | Console | PC |
|---|---|---|
| XR-001 Title Stability (001-01) | 38% | 34% |
| XR-003 Title Integrity (003-02) | 14% | 4% |
| XR-045 Respect User Privileges (045-01) | 11% | 9% |
| XR-064 Joining a session from the same game (064-02) | 8% | 13% |
| XR-055 Achievements (055-01) | 7% | 18% |
| XR-064 In-game invitations (064-03) | 6% | - |
| XR-015 User communication (015-01) | 3% | 3% |
| XR-052 Cloud storage roaming (052-06) / correct user association (052-05) | 3% / 2% | 2% / 4% |
| XR-022 Official naming standards (022-01) | 2% | 5% |
| XR-001 Stability after suspend, sleep, hibernate (001-02) | 2% | - |
Lessons that generalize to every console:
- Stability: crashes/hangs at launch, during invites/matchmaking/joins, rapid menu enter/back, random input
  on every screen, suspend/resume in every mode. Test installs from the store, not side-loaded builds.
- Integrity: every mode completable, leaderboards populate, all input devices work, no soft-locks.
- Privileges: child and adult accounts; respect multiplayer/communication/UGC privileges and show the
  system resolution UI when blocked (Xbox: `XUserCheckPrivilege`, `XUserResolvePrivilegeWithUiAsync`).
- Joinability/invites routed through the platform shell, including password-protected sessions.
- Achievements/trophies unlock exactly when criteria are met.
- Saves follow the signed-in user; switching users mid-game must not leak or overwrite progress; cloud saves roam.
- Naming: no references to competing platforms in text or images (controller art, button callouts).
- PC (Xbox/Microsoft Store): tested at 1366x768, 1440x900, 1080p, 1440p, 4K, windowed and fullscreen, AMD/Intel/Nvidia GPUs.

## Xbox FMA (Failure Mode Analysis) - severity scoring
- Each issue scored on severity (-4 to 22), probability (share of users reaching it, -3 to 8),
  repeatability (-3 to 6, e.g. 9/10 repros → 5). Sum → classification:
  **CFR** (Condition for Resubmission - blocks), **SRI** (Standard Reporting Issue - reported, not blocking),
  **ION** (Issue of Note). Use the same three-axis thinking in internal pre-cert triage for every platform.

## TRC-like areas common to all consoles (public-level summary)
| Area | Typical expectation | Test |
|---|---|---|
| Lifecycle | suspend/resume, rest/sleep mode, quick resume, constrained mode; no crash/hang; network re-validated after resume | suspend in every screen/mode, online and offline |
| User accounts | correct primary user, sign-out/sign-in/user switch mid-game handled; guest users; account picker | switch users while suspended; sign out during save |
| Controllers | disconnect → pause + reconnect prompt; re-pairing to a user; multiple controllers | pull battery/USB in gameplay, menus, cutscenes |
| Save data | platform save API, user-bound, no corruption on power loss, save indicator, space-full handling | kill power during save; full storage |
| Network | loss of platform/partner services handled with clear message, no hang; offline modes work | unplug network in matchmaking/purchase |
| Privileges/parental | age/parental restrictions on multiplayer, chat, UGC, purchases | child account matrix |
| Communication/UGC | block/mute honored, text filtering, report flow | blocked user cannot chat/invite |
| Achievements/trophies | unlock rules, no unlock in debug/cheat only, list complete; PlayStation platinum rules (verify) | unlock every one on retail-like build |
| Store/entitlements | DLC/add-on ownership checks, offline entitlement cache, purchase via platform store only | buy/refund/restore flows |
| Terminology/branding | official platform names, button names/glyphs, logos per platform guidelines | screenshot audit of all UI |
| Localization | system-language default, mandatory languages per region (verify per platform) | switch console language |
| Performance | no unresponsive screens beyond limits; loading indicators; framerate target per platform | cold launch timing, long loads |
| Age rating | rating per region present and matching content | metadata check |
| Accessibility | platform-specific expectations (Xbox accessibility tags must match features) | feature checklist |

## Pre-cert self-check (internal "cert pass")
1. Obtain the current checklist version from the platform portal (requirements change by version/date).
2. Map each requirement → owner → test case (qa-engineer `templates/test-cases.md`), tag platform.
3. Run on retail-equivalent kits/test kits with store-like install (package, not dev deploy).
4. Run with child and adult accounts, multiple users, multiple controllers, network off/on.
5. Score findings with FMA-style severity x probability x repeatability; fix all would-be blockers.
6. Run the platform's packaging validator (Xbox: Submission Validator logs must accompany submission).
7. Repeat on the exact submission build; any code change after the pass = re-run affected areas.

## Submission package (typical items)
- Final package/master + validator logs; version/patch numbers per platform rules.
- Age rating certificates per region (IARC/ESRB/PEGI/CERO etc. - release-platform-manager).
- Store product setup: descriptions, assets, pricing, add-ons, achievements/trophy list and art.
- Test notes for platform QA: how to reach all modes, debug-free build, accounts, server environment,
  known waivers (if pre-agreed with platform account manager).
- Partner services (backend, matchmaking) live and configured for cert testing.

## Patches and live updates
- Every patch, DLC and often server-driven content that changes client behavior goes through cert/content
  update rules; check patch size and frequency limits (NDA, verify with platform).
- Plan live-ops content as data (Addressables/config) within platform rules about downloadable executable code.

## Sources
- Microsoft GDK, Top failing test cases (v3.0, 2026-08) https://learn.microsoft.com/gaming/gdk/docs/store/policies/console/console-topfailingtestcases
- Xbox Developer docs, Failure Mode Analysis https://devdocs.xbox.com/publishing/certification/xr-fma
- Microsoft GDK, Xbox Requirements supporting content https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/policies/xr/console-xr-supporting-docs
- Microsoft GDK, Submission Validator checks https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/packaging/subval/submissionvalidator-tests
- Xbox XR-001 Title Stability https://devdocs.xbox.com/publishing/certification/xr/xr-001
- PlayStation Partners (portal, NDA) https://partners.playstation.net/
- Nintendo Developer Portal (registration, NDA) https://developer.nintendo.com/
