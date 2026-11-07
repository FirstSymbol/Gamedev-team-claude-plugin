---
name: domain-pc-console
description: Shared PC/console knowledge - console cert (TRC/XR/Lotcheck, public info), dev kit access, porting, Steam/Epic/GOG, anti-cheat, Steam Deck, cert schedule.
---
# PC & console domain (shared knowledge)
Mission: one source of truth for PC/console specifics so roles plan, build and test for
certification instead of discovering it at submission.

## NDA boundary (read first)
- Sony TRC, Nintendo guidelines/Lotcheck checklists and most console SDK docs are confidential
  (NDA). Use only public info here; for exact requirement IDs/values ask the human for the platform
  docs (PlayStation Partners, Nintendo Developer Portal). Never invent requirement numbers.
- Microsoft publishes Xbox Requirements (XR) and top cert failures publicly on Microsoft Learn - cite them.
- Don't commit NDA docs, SDKs or console-specific code to public repos; keep platform code in
  separate private packages/folders guarded by `#if UNITY_PS5` / `UNITY_GAMECORE` / `UNITY_SWITCH`.

## Platform access (gatekeeping)
| Platform | Access path | Unity |
|---|---|---|
| PlayStation 4/5 | apply as partner (PlayStation Partners); approval, NDA, dev/test kits purchased | PS platform modules + docs from Sony/Unity console forums after approval |
| Xbox Series X|S / One, PC Game Pass | ID@Xbox or managed partner; GDK (PC GDK public, console parts gated); dev kits via program | Unity GameCore (Xbox) module after approval |
| Nintendo Switch / Switch 2 | register on Nintendo Developer Portal, project approval (pitch); dev kits | Switch module via Nintendo/Unity after approval |
| Steam / Epic / GOG | self-serve onboarding (fees, tax, identity) | standard Windows/macOS/Linux build targets |
- Console builds typically require a paid Unity tier (Pro or higher) and per-platform approval (verify current Unity terms).
- Lead time: partner approval + dev kit delivery can take weeks to months - start in pre-production.
- Plan engine version with console SDK support: each platform module supports specific Unity 6.x lines and
  SDK versions; check before upgrading (ADR via tech-lead-architect).

## Rules that always apply
- Design for certification from day one: suspend/resume, user switching, controller loss, save integrity,
  network loss, privileges/parental controls, platform terminology - retrofitting is expensive.
- Server-authoritative online features; anti-cheat is defense-in-depth, not a substitute (domain-multiplayer).
- One input abstraction (Unity Input System actions) with per-platform glyph sets; never hard-code button names.
- Saves: atomic writes, versioned format, platform save APIs on console, cloud conflict handling on PC/Xbox.
- Per-platform performance and memory budgets set by tech-lead-architect; test on retail-equivalent kits, not dev PCs.
- Each patch/DLC goes through certification again (lighter, still scheduled).

## Certification planning (schedule)
| Milestone | Activity |
|---|---|
| Pre-production | partner/dev-kit applications; budget age ratings; pick Unity line with platform support |
| Alpha | platform features stubbed (accounts, saves, achievements/trophies); first internal cert pass |
| Beta | full internal pre-cert pass against TRC/XR/guidelines checklist; fix all would-fail items |
| Submission (master/RC) | ratings certificates ready; store product setup; submit per platform window |
| Cert result | pass → release scheduling; fail → fix + resubmit (each pass costs days to weeks) |
| Launch | day-one patch also certified; holiday submission cutoffs published by platform holders |
- Budget >= 2 submissions per platform; first-party QA turnaround is typically days to ~2 weeks per pass
  (verify with platform holder/publisher for your title and season).
- Physical release: add manufacturing lead time (weeks) after cert pass (verify with publisher).
- Sim-ship on several consoles: stagger submissions so one team is not fixing three fail reports at once.

## References (read on demand)
- references/console-certification.md — what cert checks (public XR data, common TRC-like areas), FMA
  severity, pre-cert self-check, submission artifacts.
- references/porting-checklist.md — porting a Unity game to console/handheld: input, lifecycle, saves,
  accounts, achievements, perf/memory, resolution modes, localization/terminology.
- references/pc-platforms.md — PC specifics: Steam/Epic/GOG features, anti-cheat, graphics settings,
  ultrawide/HDR, shader stutter, Steam Deck tuning, min-spec testing.
- Steam builds/branches/review: `studio:release-platform-manager`; Steam page copy/wishlists: `studio:marketing-manager`. Test strategy: `studio:qa-lead`.
