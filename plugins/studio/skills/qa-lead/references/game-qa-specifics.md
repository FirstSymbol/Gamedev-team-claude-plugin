# Game QA specifics

## Playtesting vs QA
| | Playtesting | QA testing |
|---|---|---|
| Question | Is it fun, clear, balanced, sticky? | Does it work as specified, on every target? |
| Owner | lead-game-designer / game-designer (UX research) | qa-lead / qa-engineer |
| Participants | target players, not the team | trained testers |
| Output | observations, survey scores, funnel drop-off → design changes | defects, test results → fixes |
| Timing | from paper/greybox onward, repeated | from first playable build, continuous |
- Keep separate channels: playtest notes → `.team/reports/playtest-*.md`; real defects found in playtests
  are re-filed as bugs by qa-engineer with repro steps.
- Never use playtesters as the regression team; never treat "players dislike X" as a bug without a spec.

## Android device fragmentation - compatibility matrix
Build the matrix from data: Play Console → Device catalog + Android vitals by device, analytics
(top devices by DAU/revenue for the target markets), and Unity min API (Unity 6.3: API 25+).
| Axis | Cover |
|---|---|
| GPU family | Qualcomm Adreno, ARM Mali, Samsung Xclipse (RDNA), PowerVR/IMG (budget) - driver bugs differ per family |
| SoC tier | low (e.g. 3-4 GB RAM, Helio/Unisoc/Snapdragon 4xx), mid (Snapdragon 6/7, Dimensity 7xxx), high (flagship) |
| RAM class | 3, 4, 6, 8+ GB (low-memory kills, Addressables memory) |
| OS version | min supported API, the 2-3 most common, newest (target API behavior changes) |
| OEM skin | Samsung One UI, Xiaomi HyperOS/MIUI, Oppo/Realme ColorOS, Huawei (no GMS - only if targeted) |
| Screen | aspect 16:9 to 21:9+, notches/punch-holes (safe area), foldables, tablets |
| Graphics API | Vulkan vs OpenGL ES 3.x fallback (Unity Auto Graphics API) |
Tiering rule: P0 devices (top ~10 by DAU + min-spec reference) every RC; P1 (next ~20) every release
via cloud farm; P2 (long tail) sampled monthly. Cloud farms: Firebase Test Lab, AWS Device Farm,
BrowserStack App Automate, Sauce Labs (verify current device lists and Unity/AltTester support).
iOS: oldest supported iPhone + newest + iPad; check iOS min version vs Unity's supported minimum.

## Localization QA (LQA)
- Pseudo-localization early (Unity Localization package pseudo-locale: expansion ~30-40%, accents,
  brackets) catches truncation and hard-coded strings before translators start.
- Checklist: truncation/overflow, font fallback (CJK, Thai, Arabic/Hebrew RTL shaping in TextMeshPro),
  plurals/gender (ICU/Smart Strings), number/date/currency formats per locale, concatenated strings,
  text in images/textures, voice-subtitle sync, store metadata and screenshots per locale.
- Linguistic review by native speakers in context (screenshots/build), not spreadsheets only.
- Culturalisation: gambling imagery, symbols, colors, maps, flags (escalate to compliance-advisor).
- Bug fields for LQA: locale, string key, screenshot, expected text, category (linguistic/visual/functional).

## Compliance testing (verify the build, legality stays with compliance-advisor)
| Area | Checks |
|---|---|
| Store policy | IAP via store billing for digital goods; loot box odds shown before purchase; account deletion in-app (Apple 5.1.1); no real-money gambling without license/approval |
| Privacy | consent before tracking SDK init (GDPR/UMP CMP), ATT prompt before IDFA, data matches Privacy labels / Data safety, privacy policy link in-app |
| Age | age gate works and is neutral; under-age path disables chat/purchases/ads as specified; Families/kids policies if targeted |
| Social casino | no cash-out or prize of real value; "no real money gambling" disclaimer where required; age 18+ gating where required (verify per market) |
| Console cert | TRC/XR/Lotcheck pre-check list (studio:domain-pc-console) |
| Ratings | content matches the IARC/ESRB/PEGI questionnaire answers (release-platform-manager) |

## Economy and exploit testing
Server-authoritative is the only safe default; test the server, not the UI.
| Exploit class | Test |
|---|---|
| Clock manipulation | change device time/timezone forward/back; daily bonus, timers, energy must use server time |
| Replay/duplication | resend same purchase receipt / reward claim; idempotency key must dedupe |
| Race conditions | fire N parallel claim/spend requests (k6 or script) - balance must stay consistent |
| Value tampering | MITM proxy (mitmproxy, Charles, Fiddler) edit amounts, prices, item IDs, negative or huge values |
| Client memory edit | GameGuardian/Cheat Engine on currency; server must reject/ignore client totals |
| Offline/desync | kill network mid-transaction; reconnect; double-grant or lost-grant check |
| Refund abuse | purchase → consume → refund (store sandbox); entitlement revoked/flagged |
| Integer edges | overflow at int32 max, decimal rounding of currency, minor-unit conversions |
| Event boundaries | start/end time in each timezone, DST change, leap day |
- Track an economy sanity dashboard during tests: currency sources/sinks per hour, top earners.
- Security-sensitive findings → security-engineer, flagged S1 if money or items with real value.

## Soak, stress, load
| Test | What | Pass criteria (defaults) |
|---|---|---|
| Client soak | 4-8 h autoplay/bot loop on low tier device | no crash; memory growth < 5% per hour after warm-up; no frame-time drift |
| Background/foreground cycles | 100x suspend/resume, incoming call, lock screen | no crash, state restored, audio resumes |
| Backend soak | 8-24 h at expected peak | no memory leak, stable p95, no connection pool exhaustion |
| Load | ramp to 1x, 2x expected peak (CCU, req/s) | SLO p95 met at 1x; graceful degradation at 2x |
| Spike | 10x in 1 min (event start, push notification) | queueing/rate limits hold; no data corruption |
| Multiplayer | headless bot clients join, play, leave, reconnect; matchmaking at target CCU | match start time, tick stability, packet loss tolerance per spec |
Tools: k6, NBomber (.NET), Locust; headless Unity clients (`-batchmode -nographics`) or protocol bots
for netcode; Unity Profiler/Memory Profiler captures at start and end of soak.

## Casino RNG / RTP verification testing
Math and certification rules: `studio:domain-igaming`. QA verifies the implementation:
- RNG: server-side CSPRNG (`System.Security.Cryptography.RandomNumberGenerator`), unbiased range
  mapping (`RandomNumberGenerator.GetInt32(min, max)`, no `% n` bias), no reseeding per request, no client RNG for outcomes.
- Statistical tests on raw output: chi-square uniformity per reel/symbol, runs test, serial correlation;
  batteries: NIST SP 800-22, Dieharder, TestU01 (labs run these for certification; QA runs a smoke subset).
- RTP simulation: run >= 10^7-10^9 spins headless through the production math engine (not a re-implementation).
  Required spins for RTP precision: `n = (z * sigma / e)^2`; sigma = per-spin std dev in bet units
  (volatile slots 5-15+). Example: sigma 10, e = 0.1% (0.001), z = 1.96 → n ≈ 3.8 x 10^8 spins.
- Compare measured RTP, hit frequency, feature trigger rate, max win to the PAR sheet within CI.
- Config tests: paytable/reel strips deployed = certified versions (hash compare), RTP variant per market.
- Real-money: certification by accredited lab (GLI-11/GLI-19, BMM, eCOGRA, iTech Labs); any math change
  = re-certification (compliance-advisor). Social casino: same rigor for fairness claims and odds disclosure.

## Accessibility checks
- Baselines: Game Accessibility Guidelines (basic/intermediate/advanced), Xbox Accessibility Guidelines (XAG),
  WCAG 2.2 AA for admin web and web-based UI. Apple/Google: VoiceOver/TalkBack for native UI only.
- Checklist: remappable controls, no essential info by color alone (test with color-blind simulation),
  subtitle size/background options, text >= platform minimum (Steam Deck: >= 9 px at 1280x800, 12 px recommended),
  hold vs toggle, difficulty/assist options, reduced motion/flash (photosensitivity: avoid > 3 flashes/s),
  audio cues have visual alternatives, touch targets >= 44 pt (iOS) / 48 dp (Android).
- Xbox titles: accessibility feature tags on store must match the build.

## Sources
- Unity Localization package manual (pseudo-localization) https://docs.unity3d.com/Packages/com.unity.localization@1.5/manual/Pseudo-Localization.html
- Android Developers, Android vitals for games https://developer.android.com/games/optimize/vitals
- Game Accessibility Guidelines https://gameaccessibilityguidelines.com/
- Xbox Accessibility Guidelines https://learn.microsoft.com/gaming/accessibility/guidelines
- NIST SP 800-22 Rev. 1a, statistical test suite for RNGs https://csrc.nist.gov/pubs/sp/800/22/r1/upd1/final
- GLI-11 Gaming Devices standard (Gaming Laboratories International) https://gaminglabs.com/gli-standards/
- Steamworks, Steam Deck compatibility review https://partner.steamgames.com/doc/steamdeck/compat
- .NET API, RandomNumberGenerator.GetInt32 https://learn.microsoft.com/dotnet/api/system.security.cryptography.randomnumbergenerator.getint32
