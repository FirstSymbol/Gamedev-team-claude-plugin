# Porting checklist: Unity game → console / handheld / PC
Use as a gap analysis at the start of a port and as a pre-cert checklist later. Exact platform values
(memory reservations, timing limits, requirement IDs) come from NDA docs - fill them in privately.

## 0. Feasibility (before committing)
- [ ] Partner approval + dev kits + Unity platform module for the target Unity 6.x line (see SKILL.md access table).
- [ ] Third-party plugins/SDKs available for the platform (native plugins need per-platform builds; check
      analytics, ads (usually removed), crash reporter, networking, voice, anti-cheat, middleware like Wwise/FMOD).
- [ ] IL2CPP-only on consoles: reflection/serialization stripping, AOT generics (`link.xml`, `[Preserve]`;
      studio:stack-unity serialization-and-platforms ref).
- [ ] Monetization model allowed on the platform (store IAP only; ads rarely acceptable; loot box disclosure).
- [ ] Online services: platform accounts/identity linking with your backend, cross-play/cross-progression policy.

## 1. Input and controllers
- [ ] Input System action maps; full controller navigation of every screen (no mouse-only UI); focus visible.
- [ ] Per-platform glyphs and official button names (no Xbox glyphs on PlayStation, no competitor references).
- [ ] Controller disconnect → pause + reconnect prompt; reassign controller to user; multiple controllers.
- [ ] Platform-specific: PS confirm/cancel button conventions by region (verify), Switch Joy-Con single/pair,
      handheld vs docked, touch screen (Switch/Deck) optional; DualSense haptics/adaptive triggers optional.
- [ ] System keyboard for text entry (platform software keyboard API).
- [ ] Remapping and accessibility options (hold/toggle, sensitivity, dead zones).

## 2. Application lifecycle (TCR-like)
- [ ] Suspend/resume (rest mode, quick resume, sleep) in every state: gameplay, menus, loading, online match, saving.
- [ ] On resume: re-validate user sign-in, network, entitlements, session; resync server time; reconnect sockets.
- [ ] Constrained/background modes: pause audio/gameplay when system UI overlays; handle focus loss.
- [ ] Startup: first interactive frame and loading screens within platform limits; animated loading indicator (no frozen frames).
- [ ] Graceful handling of platform service outages (clear message, retry, offline mode).

## 3. User accounts and privileges
- [ ] Primary user selection at start; sign-out / user switch mid-game returns to title safely.
- [ ] Progress, settings, achievements bound to the right user; no writes for signed-out users.
- [ ] Child accounts / parental controls: multiplayer, communication, UGC, purchases respect privileges and
      show system resolution UI where required.
- [ ] Block/mute lists honored for chat, voice, invites; text filtering for UGC/names.
- [ ] Backend account linking: platform user ID ↔ studio account; account deletion/privacy flows per platform.

## 4. Save data
- [ ] Platform save APIs (not raw file IO) on console; save size within quota; versioned save format + migrations.
- [ ] Atomic writes (temp + commit); corruption detection (checksum) and recovery path.
- [ ] "Saving, do not turn off" indicator when required; no save during suspend race.
- [ ] Storage full / quota exceeded handled with a platform-compliant message.
- [ ] Cloud saves (Xbox roaming, PS Plus cloud, Steam Cloud): conflict resolution, first-launch download, no silent overwrite.

## 5. Achievements / trophies / activities
- [ ] List designed with platform limits (counts, points/grades, hidden/spoiler rules; verify per platform).
- [ ] Unlock logic server/client consistent; unlock exactly at criteria; retroactive unlock for existing saves if needed.
- [ ] PS5 Activities / Game Help, Xbox rich presence, Switch play reports - per scope agreed with platform.
- [ ] Test every unlock on a retail-like build (debug unlock tools excluded from release).

## 6. Performance and memory
| Target | Public figures (verify against platform docs) |
|---|---|
| Xbox Series X | 16 GB GDDR6, ~13.5 GB available to games (Microsoft-stated at reveal, 2020; verify) |
| Xbox Series S | 10 GB, ~8 GB available to games; lower GPU - usually the hardest Xbox target |
| PS5 / PS5 Pro | 16 GB GDDR6 unified (game-available amount under NDA) |
| Nintendo Switch | 4 GB LPDDR4 shared with OS; 720p handheld / 1080p docked |
| Nintendo Switch 2 | 12 GB (reported, verify); 1080p LCD with VRR up to 120 Hz handheld; docked up to 4K60, 120 fps at 1080p/1440p (Nintendo tech specs) |
| Steam Deck | 16 GB LPDDR5 unified, 1280x800 16:10; Verified needs 30 fps at default settings |
- [ ] Budgets per platform (frame time, memory per category, streaming bandwidth, load times) agreed with tech-lead-architect.
- [ ] Memory: texture/audio compression per platform (ASTC/BCn), Addressables bundles per platform, no leaks in 4 h soak.
- [ ] CPU: Burst/Jobs where hot; avoid main-thread spikes on suspend/resume; GC allocation budget per frame ~0 in gameplay.
- [ ] GPU: dynamic resolution / upscaler (Unity STP, platform upscalers via plugins) to hold framerate.
- [ ] Load times measured from cold boot on retail-like hardware with store-installed package.

## 7. Resolution and display modes
- [ ] Performance vs quality modes where expected (60 fps vs 30/40 fps 4K); 120 Hz modes optional (VRR support).
- [ ] Switch handheld vs docked profiles (resolution, LOD, effects) switch at runtime without hitch.
- [ ] Safe area / title-safe margins (TV overscan settings), UI scale option, text legible at TV distance.
- [ ] HDR output where supported (tone mapping, paper-white setting, UI brightness).

## 8. Platform services and store
- [ ] Entitlements: base game, DLC, season pass, consumables via platform store API; offline cache; refunds.
- [ ] Platform invites/joinability, sessions, voice/chat platform APIs, cross-play toggles.
- [ ] Platform-specific legal: EULA, privacy notices, age rating display, region locks.

## 9. Localization and terminology
- [ ] Mandatory languages per region (verify); default to system language; fonts include all glyphs.
- [ ] Official terminology for each platform (system features, controller names); screenshot audit.
- [ ] Remove competitor references (logos, button prompts, store names) from text and images.

## 10. Build and pipeline
- [ ] Separate build profiles per platform (Unity 6 Build Profiles) with defines; CI agents with platform SDKs (private).
- [ ] Packaging tool + validator runs in CI (e.g. Xbox Submission Validator); symbols archived per build for crash analysis.
- [ ] Patch strategy: content layout to minimize patch size (asset bundles stable, no full repack).

## Sources
- Microsoft GDK, Top failing test cases https://learn.microsoft.com/gaming/gdk/docs/store/policies/console/console-topfailingtestcases
- Xbox XR-001 Title Stability https://devdocs.xbox.com/publishing/certification/xr/xr-001
- Nintendo, Nintendo Switch 2 tech specs https://www.nintendo.com/us/gaming-systems/switch-2/tech-specs/
- Steamworks, Steam Deck compatibility review https://partner.steamgames.com/doc/steamdeck/compat
- Unity Manual, Build Profiles https://docs.unity3d.com/Manual/build-profiles.html
