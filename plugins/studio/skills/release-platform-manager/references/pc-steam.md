# PC release: Steam (Steamworks) + Epic/GOG notes
Porting/tech specifics (input, settings, anti-cheat, Deck tuning): studio:domain-pc-console.

## Steamworks onboarding and fees
- Steam Direct fee: USD 100 per app, non-refundable, recouped after the product earns USD 1,000 adjusted
  gross revenue. Onboarding: digital paperwork (company, bank, tax, identity).
- First few titles: 21-day wait between paying the app fee and release, plus a public Coming Soon page
  for >= 2 weeks (Steamworks onboarding docs; not 30 days).
- Permissions needed to release: "Publish app changes to Steam" + "Manage pricing and discounts".

## Store page
| Asset (required) | Size |
|---|---|
| Header capsule | 920 x 430 |
| Small capsule | 462 x 174 |
| Main capsule | 1232 x 706 |
| Vertical capsule | 748 x 896 |
| Screenshots | >= 5, >= 1920 x 1080, 16:9 |
| Page background (optional) | 1438 x 810 |
| Library capsule / header / hero / logo | 600 x 900 / 920 x 430 / 3840 x 1240 (safe area 860 x 380) / 1280 wide and/or 720 tall |
Review rules: capsules show readable title/logo; screenshots "must only contain gameplay" (no concept art,
award badges or marketing text); description detailed, no external links; only features available at launch;
Early Access questions answered. Content Survey covers mature content and AI-generated content disclosure and
feeds Valve's own age rating (mandatory for Germany since 2024-11-15 and for Indonesia - age-ratings.md).
- Coming Soon page must be live >= 2 weeks before release; submit store page >= 7 business days before you want it live.
- Wishlists accrue from the Coming Soon page - publish early (6-12 months before launch is common practice).

## Review process
| Item | Typical time | Notes |
|---|---|---|
| Store page review | 3-5 business days | submit before the build |
| Build review | 3-5 business days, plan >= 7 business days | build must launch on every OS listed; every listed feature implemented |
| Adult content | longer than usual | both page and build |
| Later updates | no re-review of builds/store edits after first approval (policy content still applies) | |
- Build check failures seen most: game does not launch on a listed OS, listed features (controller support,
  achievements, cloud) missing, in-game purchases not through Steam (must use Steam Wallet/microtransactions).
- Release is manual: "Release App" button after approval; nothing auto-launches.
- Not allowed (Steamworks onboarding, "What you shouldn't publish"): blockchain apps that issue or allow exchange of
  cryptocurrencies or NFTs (since 2021); apps with advertising-based business models (no ad-funded F2P).

## Builds: depots, branches, SteamPipe
- **Depot** = set of files (per OS, per language, per DLC, shared content). **Package** = what the user owns.
  **Branch** = which build each user gets (`default` = public; beta branches, optionally password-protected).
- Upload with `steamcmd +login <builder> +run_app_build <path>/app_build_<appid>.vdf +quit` from the
  ContentBuilder; keep `config/config.vdf` on CI to avoid Steam Guard prompts; dedicated builder account
  with minimal permissions.
```vdf
"AppBuild" {
  "AppID" "<appid>"  "Desc" "v1.4.0 build 1234 (git abc123)"
  "ContentRoot" "..\content\"  "BuildOutput" "..\output\"
  "SetLive" "qa"                               // beta branch only; "default" cannot be set live automatically
  "Depots" { "<depotid>" { "FileMapping" { "LocalPath" "*" "DepotPath" "." "Recursive" "1" }
                           "FileExclusion" "*.pdb" } }
}
```
- `"Preview" "1"` validates mappings without uploading. Read `output/*.log` for errors.
- Setting a build live on the default branch of a released app requires Steam Guard mobile/phone
  confirmation (security changes impose a 3-day wait).
- Branch strategy: `qa` (internal, password), `beta` (opt-in players), `default` (release), `previous`
  (last good build for instant rollback by setting it live again).
- Keep debug symbols out of depots; upload them to the crash reporter (Backtrace/Sentry) per BuildID.
- Update size: Steam diffs in 1 MB chunks; keep asset bundles/Addressables deterministic and avoid
  repacking unchanged content.

## Steam features checklist (what the store page claims must work)
| Feature | API/notes |
|---|---|
| Achievements, stats | Steamworks Stats & Achievements; Unity wrappers: Steamworks.NET (SDK 1.65), Facepunch.Steamworks (both with commits in 2026-10) |
| Steam Cloud | Auto-Cloud (config only, file paths) or Remote Storage API; test conflict + offline cases |
| Controller support (full/partial) | Steam Input; glyphs match the active device |
| Steam Deck | compatibility review: Verified / Playable / Unsupported / Unknown |
| Overlay, rich presence, invites | test overlay with fullscreen/borderless; multiplayer join via invites |
| Trading cards, workshop | optional; separate reviews |
| Remote Play Together | needs local multiplayer |
Steam Deck Verified criteria: full controller support with default config, glyphs match Deck controls,
controller text entry (Steamworks API or built-in), no unsupported-hardware warnings, launchers controller-
navigable, default settings reach 30 fps at 800p, text legible at 12" (min 9 px at 1280x800, 12 px recommended),
works under Proton if no native Linux build (anti-cheat must enable Proton support).

## Playtest, demos, festivals
- Steam Playtest: separate free child app from your store page; users request access; you control waves and
  size; no review score impact. Good for closed/open betas and load tests.
- Demos: separate app with own store page/reviews; Steam Next Fest editions several times a year (register
  ahead; demo must pass review - verify: next edition dates and registration deadline in Steamworks before planning).
- Early Access: must be playable; answer the EA questionnaire; set expectations on price/roadmap.
- Refund policy (players): within 14 days of purchase and < 2 h playtime - short games and demos interplay.
  In-game items: refundable via Steam only in Valve games or where the developer opts in (48 h, not consumed).

## Other PC stores (brief)
| Store | Notes |
|---|---|
| Epic Games Store | self-publishing portal; 88/12 revenue split (verify: reported 2025 change keeping 100% of first USD 1M per app/year - Epic distribution terms); Epic Online Services (accounts, achievements, EAC free); IARC storefront |
| GOG | curated submission; DRM-free expectation; GOG Galaxy SDK for achievements/cloud |
| Microsoft Store / PC Game Pass | GDK for PC; Xbox requirements apply to PC titles (see studio:domain-pc-console) |

## Steam release checklist
- [ ] Store page approved, Coming Soon >= 2 weeks; price (regional) approved; launch discount set.
- [ ] Build approved; release build on `default` from release tag; previous build kept on a `previous` branch.
- [ ] All OS depots launch from a clean install (fresh Windows user, no dev redistributables).
- [ ] Redistributables (VC++/DirectX) via Steamworks install scripts if needed.
- [ ] Listed features verified: achievements unlock, cloud sync two machines, controller, Deck.
- [ ] Content Survey (mature, AI disclosure) accurate; EULA/privacy policy if collecting data.
- [ ] Crash reporting with symbols per BuildID; day-one patch plan; community/news post drafted (marketing).

## Sources
- Steamworks, Release process https://partner.steamgames.com/doc/store/releasing
- Steamworks, Review process https://partner.steamgames.com/doc/store/review_process
- Steamworks, Steam Direct fee https://partner.steamgames.com/doc/gettingstarted/appfee
- Steamworks, Graphical assets https://partner.steamgames.com/doc/store/assets/standard
- Steamworks, Uploading to Steam (SteamPipe) https://partner.steamgames.com/doc/sdk/uploading
- Steamworks, Steam Deck compatibility review https://partner.steamgames.com/doc/steamdeck/compat
- Steamworks, Playtest https://partner.steamgames.com/doc/features/playtest
- Steamworks, Onboarding (21-day wait, content rules) https://partner.steamgames.com/doc/gettingstarted/onboarding
- Steamworks, Library assets https://partner.steamgames.com/doc/store/assets/libraryassets
- Steam refunds https://store.steampowered.com/steam_refunds/
- IARC storefronts https://globalratings.com/storefronts/
