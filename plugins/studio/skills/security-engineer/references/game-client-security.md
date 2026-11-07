# Game client security and anti-cheat (practitioner reference)

## Axiom: the client is hostile
Anything shipped to the device (code, assets, memory, packets, local saves, PlayerPrefs) is
readable and modifiable by a motivated player. Client-side checks raise cost; only the server
decides outcomes. Design question for every feature: "what if the client lies here?"

## What attackers do, and the real defense
| Vector | Tools (examples) | Effect | Primary defense (server) | Secondary (client, raises cost) |
|---|---|---|---|---|
| Decompile managed code | ILSpy, dnSpy on `Assembly-CSharp.dll` (Mono builds) | full source logic, endpoints, keys | no secrets/logic of value in client | ship IL2CPP; obfuscator |
| IL2CPP metadata recovery | Il2CppDumper, Cpp2IL on `global-metadata.dat` + `libil2cpp.so`/`GameAssembly.dll` | type/method names, hook points | same | metadata encryption (commercial), symbol stripping |
| Memory editing | Cheat Engine (PC), GameGuardian (Android) | change HP, currency, cooldowns | server owns values; client values are display caches | value obfuscation (XOR/split + checksum) |
| Speed hack | time-function hooks (Cheat Engine speedhack, GameGuardian) | faster movement/timers | server clock for timers; max movement per tick validated | compare client delta vs server tick |
| Packet tampering/replay | proxies (mitmproxy, Charles) + cert pinning bypass (Frida) | modified requests, replayed rewards | server validation; idempotency keys; nonces; per-session sequence numbers | TLS pinning (raises cost only) |
| Modded client / repack | APKTool + resign, Frida/Xposed/Magisk hooks | everything above, distributed to others | attestation (Play Integrity / App Attest) checked server-side; server authority | tamper checks, root/jailbreak signals |
| Aimbot/wallhack/ESP (realtime PvP) | memory readers, overlays | perfect aim, see through walls | interest management (don't send hidden enemies); server-side hit validation; stats anomaly detection | kernel/user anti-cheat (PC) |
| Bots/automation | macros, emulator farms | farming, economy inflation | rate limits, behavioral analytics, CAPTCHA at economic choke points | input entropy heuristics |
| Save-file edits | text/binary editors | unlocks, currency | cloud save validated server-side; client save = cache only | signed saves (HMAC key is extractable — weak) |

## Mono vs IL2CPP (Unity)
| | Mono | IL2CPP |
|---|---|---|
| What ships | managed DLLs (IL) | native binary + `global-metadata.dat` |
| Effort to read logic | minutes (ILSpy shows near-original C#) | hours: names recovered via Il2CppDumper/Cpp2IL, logic as native code (Ghidra/IDA) |
| Hooking | Harmony/BepInEx trivial | Frida/native hooks, still routine for cheat makers |
| Verdict | never for competitive/real-money builds | required (iOS mandatory), but treat as obfuscation, not protection |
- Strip: `Managed Stripping Level` High, no development builds in production, no `Debug.Log` of
  tokens, remove debug menus with `#if` (not runtime flags).
- Obfuscators (e.g. Obfuscator for Unity assets, Beebyte, commercial packers): rename symbols,
  encrypt strings/metadata. Cost: build complexity, crash-symbolication pain (keep mapping files).

## Server authority patterns (what the backend must do)
- Commands not results: client sends `UseItem(itemId)`, `Fire(aimDir, tick)`, `PlaceBet(amount)`;
  server computes outcomes. Never accept `AddCoins(500)` or `MatchWon=true`.
- Validate ranges, rates and causality: movement speed ≤ max × tick + tolerance; cooldowns by
  server clock; resources owned before spend; actions only in valid state.
- Idempotency: every reward/purchase/claim request carries a client-generated UUID; server stores
  processed IDs; replay returns the original result.
- Sequence numbers per session on realtime channels; drop out-of-window or duplicated packets.
- RNG on the server (`RandomNumberGenerator`) for loot, gacha, casino outcomes; client gets results.
  Casino RNG must be certified (e.g. GLI-19 for interactive gaming) — see `studio:domain-igaming`.
- Hidden information (cards, fog of war, enemy positions out of view) never sent to clients that
  must not see it — the fix for wallhacks/ESP is not sending the data.
- Telemetry for detection: per-player stats percentiles (accuracy, headshot %, currency/hour,
  win rate); flag > 3–4 σ outliers for review; ban waves delayed to hide detection signals.

## Anti-cheat products (PC/console realtime)
| Product | Notes |
|---|---|
| Easy Anti-Cheat (Epic Online Services) | free via EOS; user/kernel modes; Unity: "EOS Plugin for Unity" (github.com/EOS-Contrib/eos_plugin_for_unity, ex-PlayEveryWare; v6.2.0 Sep 2026) lists Anti-Cheat as supported |
| BattlEye | commercial, kernel-level, widely used in shooters |
| Valve Anti-Cheat (VAC) | Steam games via Steamworks |
- Kernel anti-cheat has privacy, stability and platform (Linux/Steam Deck) costs; choose with
  producer + compliance-advisor; it never replaces server authority.

## Mobile: OWASP MASVS v2 control groups
| Group | Studio requirement |
|---|---|
| MASVS-STORAGE | tokens in Android Keystore / iOS Keychain, not PlayerPrefs; no PII in logs/backups |
| MASVS-CRYPTO | platform crypto; no hard-coded keys |
| MASVS-AUTH | server-side session validation; biometric only as local unlock of a server session |
| MASVS-NETWORK | TLS everywhere (ATS on iOS, `cleartextTrafficPermitted=false`); pinning for payment/auth hosts optional with rotation plan |
| MASVS-PLATFORM | deep links validated; WebViews with JS bridges locked down; no exported components unintentionally |
| MASVS-CODE | up-to-date SDKs; input from server validated too; min OS version policy |
| MASVS-RESILIENCE | attestation, tamper/root/debugger detection — only for high-value apps (real-money, competitive) |
| MASVS-PRIVACY | data minimization, ATT/consent flows, SDK data-collection inventory |
- Test with OWASP MASTG; tooling: MobSF for static scans of APK/IPA.

## Device attestation (server-verified)
| Platform | API | Notes |
|---|---|---|
| Android | Play Integrity API | replaces SafetyNet Attestation (turned down; verify: exact date on developer.android.com SafetyNet deprecation timeline); verify the token on the server via Google, check `requestDetails` (`requestHash`/`nonce`), `appIntegrity` (`PLAY_RECOGNIZED`), `accountDetails` (`LICENSED`), then tier on `deviceIntegrity` labels; prefer Standard requests; default 10,000 requests/day |
| iOS | App Attest (DeviceCheck framework) | attest key once, then assert per sensitive request; server validates with Apple |
- Use attestation as a risk signal at economic choke points (login, purchase, reward claim,
  ranked match), not as a hard gate for all users (false negatives on custom ROMs, emulators).

## IAP receipt validation (server-side, mandatory)
| Store | Validate | Then |
|---|---|---|
| Apple (StoreKit 2) | verify JWS signed transaction (Apple App Store Server Library: certificate chain to Apple root) or query App Store Server API by `transactionId` | subscribe to App Store Server Notifications V2 for refunds/revocations |
| Apple (legacy) | App Store Receipts and the `verifyReceipt` endpoint are marked deprecated in Apple docs (no turndown date stated as of 2026-11) — migrate to App Store Server API / JWS | — |
| Google Play | Play Developer API `purchases.products.get` / `purchases.subscriptionsv2.get` with purchase token; check `purchaseState`, `acknowledgementState`, `obfuscatedExternalAccountId` matches player | acknowledge within 3 days or it is refunded; Real-time developer notifications (Pub/Sub) for refunds; Voided Purchases API |
| Unity IAP v5 | `CrossPlatformValidator` = local only, Google Play only (Apple receipt validation deprecated; StoreKit 2 validates on device); Unity offers no remote validation service | in `OnPurchasePending(PendingOrder)` send `order.Info.Receipt` (Google) or `order.Info.Apple.jwsRepresentation` (Apple) to server; `ConfirmPurchase(order)` only after server grant |
- Flow: client purchase → send receipt/token + player ID → server validates with store → checks
  bundle ID/product ID/environment (sandbox vs prod) → dedupes by transaction/order ID → grants
  entitlement in one DB transaction → returns new state. Client never self-grants.
- Refund handling: revoke entitlement or claw back currency; flag repeat refunders (fraud signal).
- Bind purchases to account (`appAccountToken` on iOS, `obfuscatedAccountId` on Play) to block
  receipt sharing between accounts.

## Replay and packet tampering (realtime + REST)
- TLS for REST/WebSocket; for UDP game traffic use DTLS (Unity Transport supports DTLS/secure WebSockets)
  or per-session keys from the matchmaker (connect token pattern: netcode.io style — server-signed,
  expiring token with session key).
- Every message: session ID, monotonically increasing sequence, server rejects duplicates/old.
- Rewards granted only from server-side match results, never from a client "match end" packet.

## Review checklist (client-facing feature)
- [ ] List every client→server message; for each: validation rule, rate limit, idempotency.
- [ ] No outcome decided on the client; no hidden info sent to the client.
- [ ] IL2CPP, stripping, no dev build, no debug menus in release; obfuscation decision documented.
- [ ] Tokens in secure storage; TLS enforced; no secrets in the build (`strings` the binary to check).
- [ ] IAP validated server-side with refund handling; attestation at choke points if high value.
- [ ] Detection telemetry defined (stats, anomalies) with review/ban process owner.

## Sources
- OWASP MASVS https://mas.owasp.org/MASVS/
- OWASP MASTG https://mas.owasp.org/MASTG/
- Android: About the SafetyNet Attestation API deprecation https://developer.android.com/training/safetynet/attestation
- Android: Play Integrity API https://developer.android.com/google/play/integrity
- Apple: Establishing your app's integrity (App Attest) https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity
- Apple: App Store Server API https://developer.apple.com/documentation/appstoreserverapi
- Google Play: Fight fraud and abuse / verify purchases https://developer.android.com/google/play/billing/security
- Unity Manual: IL2CPP overview https://docs.unity3d.com/Manual/IL2CPP.html
- Unity IAP: Receipt validation https://docs.unity.com/en-us/iap/receipt-validation ; Upgrade to IAP v5 https://docs.unity.com/en-us/iap/upgrade-to-iap-v5
- Apple: App Store Receipts (deprecated) https://developer.apple.com/documentation/appstorereceipts
- EOS Plugin for Unity https://github.com/EOS-Contrib/eos_plugin_for_unity
