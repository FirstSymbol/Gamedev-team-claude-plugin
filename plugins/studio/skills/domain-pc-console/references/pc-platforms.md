# PC platform specifics (Steam, Epic, GOG, Steam Deck)
Store submission mechanics: studio:release-platform-manager `pc-steam.md`.

## Store/SDK feature mapping
| Feature | Steam (Steamworks) | Epic (EOS / EGS) | GOG (Galaxy SDK) |
|---|---|---|---|
| Accounts/identity | Steam ID, auth session tickets (server-validate) | Epic Account Services / EOS Connect (also cross-platform IDs) | GOG Galaxy user |
| Achievements | Stats & Achievements API | EOS Achievements | Galaxy achievements |
| Cloud saves | Auto-Cloud (paths) or Remote Storage API | EOS Player Data Storage / EGS cloud saves (verify) | Galaxy cloud saves |
| Matchmaking/lobbies | Steam Matchmaking, Steam Networking Sockets/Datagram Relay | EOS Lobbies/Sessions, P2P | Galaxy matchmaking (limited) |
| Overlay/invites | Steam Overlay, rich presence | EOS Social Overlay | Galaxy overlay |
| IAP | Steam microtransactions (Steam Wallet) | EGS offers/ecom | GOG store |
| Anti-cheat | none built in (use EAC/BattlEye/server-side) | Easy Anti-Cheat via EOS (no fee, verify) | none built in |
- Unity wrappers: Steamworks.NET, Facepunch.Steamworks (check maintenance/Unity 6 compatibility); EOS Plugin for
  Unity (PlayEveryWare, verify current owner); GOG Galaxy SDK (C++ - wrapper needed).
- Abstract platform services behind interfaces (`IAchievements`, `ICloudSave`, `IPlatformUser`) so one build
  pipeline produces Steam/Epic/GOG variants via defines; never let store SDK types leak into game logic.
- Validate ownership/auth tickets on your backend (Steam `ISteamUser::GetAuthTicketForWebApi` →
  Web API `AuthenticateUserTicket`); never trust a client-provided Steam ID.

## Anti-cheat
| Option | Model | Notes |
|---|---|---|
| Server authority + validation | design | first line: validate movement, cooldowns, economy server-side (domain-multiplayer) |
| Easy Anti-Cheat (EOS) | client kernel/user-mode + backend | free via EOS; Linux/Proton support must be enabled by the developer (verify current EOS steps) |
| BattlEye | client kernel driver + service | commercial; Proton support opt-in per title (since 2021) |
| Other (e.g. Denuvo Anti-Cheat, custom) | varies | commercial; evaluate false positives, perf, privacy |
- Steam Deck/Linux: kernel anti-cheat without Proton enablement = "Unsupported" on Deck; decide early.
- Disclose kernel-level anti-cheat on the store page where required (Steam shows anti-cheat info, verify) and in privacy policy.
- Anti-cheat breaks modding and some accessibility tools - define offline/single-player exemptions.
- Threat modelling and server checks → security-engineer.

## Graphics settings (PC expectations)
- [ ] Presets (Low/Medium/High/Ultra) + individual options; auto-detect on first launch (GPU tier heuristic).
- [ ] Display: resolution, window mode (exclusive fullscreen / borderless / windowed), monitor select, refresh
      rate, VSync, frame cap (incl. unlimited), render scale / dynamic resolution.
- [ ] Upscalers: Unity STP, AMD FSR, NVIDIA DLSS, Intel XeSS via plugins/HDRP-URP integrations (verify per pipeline).
- [ ] FOV slider (first-person), motion blur/film grain/chromatic aberration toggles, brightness/gamma, HDR toggle.
- [ ] Apply without restart where possible; settings persisted per machine (don't sync display settings to cloud).
- [ ] Min-spec and recommended-spec machines in the test lab; publish specs only from measured results.

## Ultrawide, multi-monitor, high refresh
- Camera: Hor+ FOV scaling for 21:9 / 32:9; cap or pillarbox cutscenes authored for 16:9.
- UI: anchor to safe 16:9 center region option; HUD scale slider; test 16:10 (Deck, laptops) and 4:3 edge cases.
- Physics/gameplay must not depend on frame rate (fixed timestep; test at 30, 60, 144, 240+ fps).
- Mouse: raw input, sensitivity independent of FPS, no acceleration by default, full key rebinding.
- Controller on PC: hot-swap glyphs between keyboard/mouse, Xbox, PlayStation, Steam Input; avoid double input
  (Steam Input + native); support Steam Input API or ensure sane defaults.

## Shader compilation stutter (DX12/Vulkan)
- Symptom: first-time hitches when new materials/effects appear (PSO creation).
- Unity: ShaderVariantCollection warm-up, PSO tracing and warming with GraphicsStateCollection (Unity 6, verify
  per graphics API), Shader stripping to reduce variants; warm during loading screens.
- Test with a cleared shader cache (driver cache + Unity cache) on a mid-tier GPU; first-run experience matters
  for reviews and refunds (Steam refund window: 2 h playtime).

## Steam Deck tuning
- Native resolution 1280x800 (16:10); support it explicitly in UI layout; text >= 9 px (12 px recommended).
- Default settings must give >= 30 fps (Verified); offer a Deck preset (30/40/60 fps caps, FSR/STP).
- Target Vulkan for performance/battery (Valve recommendation); prefer VP9/AV1 video over vendor codecs (WMF) for Proton.
- Detect Deck via `ISteamUtils::IsSteamRunningOnSteamDeck()` to choose defaults; don't lock settings by hardware.
- Suspend/resume: device sleeps often - handle like console suspend (network reconnect, time jumps).
- On-screen keyboard for text entry (`ShowFloatingGamepadTextInput`/`ShowGamepadTextInput`); avoid launchers;
  if a launcher is mandatory, use `SetGameLauncherMode` for controller navigation.
- Cloud saves via Steam Cloud; all single-player content playable offline.

## PC build and distribution hygiene
- Windows: x64 build; IL2CPP recommended for release (perf, harder to decompile) vs Mono (moddability); sign the
  executable (code signing reduces SmartScreen warnings).
- Redistributables via Steam install scripts (VC++), not bundled installers; no admin rights required.
- Save/config paths: `Application.persistentDataPath` (Windows: `%USERPROFILE%\AppData\LocalLow\<Company>\<Product>`);
  keep Steam Cloud paths in sync with it.
- Crash reporting with symbols per build (Backtrace, Sentry, Unity Cloud Diagnostics); collect GPU driver versions.
- Linux native vs Proton: native builds need their own QA pass; Proton-only is acceptable if Deck verified.
- macOS: notarization with `notarytool`, Apple silicon native (verify Unity target support), Metal-only rendering.

## Sources
- Steamworks, Steam Deck compatibility review https://partner.steamgames.com/doc/steamdeck/compat
- Steamworks, Steam Deck recommendations https://partner.steamgames.com/doc/steamdeck/recommendations
- Steamworks, ISteamUtils API https://partner.steamgames.com/doc/api/ISteamUtils
- Steamworks, Steam Cloud https://partner.steamgames.com/doc/features/cloud
- Epic Online Services, Anti-Cheat https://dev.epicgames.com/docs/game-services/anti-cheat
- BattlEye https://www.battleye.com/
- Unity Manual, Prewarm shaders / PSO tracing https://docs.unity3d.com/Manual/shader-prewarm.html
- GOG for developers https://www.gog.com/indie
