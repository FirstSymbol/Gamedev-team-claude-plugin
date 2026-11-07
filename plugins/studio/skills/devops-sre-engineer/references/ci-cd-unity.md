# CI/CD for Unity (practitioner reference)

## Options
| Option | Use when | Notes |
|---|---|---|
| GameCI on GitHub Actions | default for GitHub repos | Docker images per editor version/platform (Linux/Windows); macOS runs a local editor install |
| GameCI on GitLab CI | GitLab repos | same images; GameCI example project in the game-ci GitLab group (game.ci/docs/gitlab) |
| Unity Build Automation (ex-Cloud Build) | no CI expertise, need macOS/iOS without owning Macs | per-build-minute pricing (verify: current rates on unity.com/products pricing page); less control, slower queues |
| Self-hosted runner + Unity CLI | big projects (Library > 20 GB), console SDKs, IL2CPP Windows builds | warm Library on disk = fastest builds; you own patching and security |
| Jenkins/TeamCity + Unity CLI | existing studio farm | TeamCity has Unity plugin; keep build scripts in repo, not in the server UI |
Rule: build logic lives in a C# `BuildScript` in an Editor asmdef; CI only calls it. CI YAML stays thin.

## Unity command line (any CI)
```
Unity.exe -batchmode -nographics -quit -projectPath . -buildTarget Android ^
  -executeMethod Studio.Build.BuildScript.BuildAndroid -logFile - -customBuildVersion 1.4.0
```
```csharp
public static class BuildScript {
    public static void BuildAndroid() {
        var args = Environment.GetCommandLineArgs();
        PlayerSettings.bundleVersion = Arg(args, "-customBuildVersion") ?? "0.0.0";
        PlayerSettings.Android.bundleVersionCode = int.Parse(Env("BUILD_NUMBER", "1"));
        EditorUserBuildSettings.buildAppBundle = true;               // AAB for Play
        var opts = new BuildPlayerOptions {
            scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray(),
            locationPathName = "build/Android/game.aab", target = BuildTarget.Android };
        var report = BuildPipeline.BuildPlayer(opts);
        if (report.summary.result != BuildResult.Succeeded) EditorApplication.Exit(1); // fail CI
    }
}
```
- Exit code: always `EditorApplication.Exit(1)` on failure; check log for `Scripts have compiler errors`.
- Addressables: call `AddressableAssetSettings.BuildPlayerContent()` before `BuildPlayer` (or the
  build-with-player setting) and upload catalogs/bundles as a separate versioned artifact.
- Unity 6 Build Profiles: `-activeBuildProfile "Assets/Settings/Build Profiles/X.asset"` activates a profile;
  `-build <path>` builds the Player from it (6000.3 Manual). GameCI `unity-builder` has a `buildProfile` input.

## Licensing in CI
| License | Secrets (GameCI) | Notes |
|---|---|---|
| Personal | `UNITY_LICENSE` (.ulf contents), `UNITY_EMAIL`, `UNITY_PASSWORD` | get .ulf via Unity Hub > Preferences > Licenses; manual .alf activation for Personal was removed by Unity in 2023 |
| Plus/Pro | `UNITY_SERIAL`, `UNITY_EMAIL`, `UNITY_PASSWORD` | seat consumed per concurrent activation; return license after job |
| Floating (Unity Licensing Server) | `unityLicensingServer: <url>` input | best for many parallel jobs; license acquired/returned per build |
- Use a dedicated CI Unity account, never a developer's personal one; 2FA on that account can
  break unattended activation (verify: GameCI docs don't cover 2FA as of 2026-11 - dry-run activation first).
- Concurrent matrix jobs × seats: Pro serials allow limited activations — throttle matrix with
  `max-parallel` or use floating licenses.

## GameCI GitHub Actions workflow (skeleton)
```yaml
name: unity-ci
on: { pull_request: {}, push: { branches: [main] } }
concurrency: { group: unity-${{ github.ref }}, cancel-in-progress: true }
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with: { lfs: true }
      - uses: actions/cache@v6
        with:
          path: Library
          key: Library-test-${{ hashFiles('Assets/**', 'Packages/**', 'ProjectSettings/**') }}
          restore-keys: Library-test-
      - uses: game-ci/unity-test-runner@v4
        env: { UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}, UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}, UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }} }
        with: { testMode: all, githubToken: ${{ secrets.GITHUB_TOKEN }}, coverageOptions: 'generateAdditionalMetrics;generateHtmlReport' }
  build:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix: { targetPlatform: [Android, WebGL, StandaloneLinux64, StandaloneWindows64] }
    steps:
      - uses: actions/checkout@v7
        with: { lfs: true, fetch-depth: 0 }     # full history for Semantic versioning
      - uses: actions/cache@v6
        with:
          path: Library
          key: Library-${{ matrix.targetPlatform }}-${{ hashFiles('Assets/**', 'Packages/**', 'ProjectSettings/**') }}
          restore-keys: Library-${{ matrix.targetPlatform }}-
      - uses: game-ci/unity-builder@v6
        env: { UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}, UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}, UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }} }
        with:
          targetPlatform: ${{ matrix.targetPlatform }}
          versioning: Semantic
          buildMethod: Studio.Build.BuildScript.BuildFromCI
          androidExportType: androidAppBundle
          androidKeystoreName: user.keystore
          androidKeystoreBase64: ${{ secrets.ANDROID_KEYSTORE_BASE64 }}
          androidKeystorePass: ${{ secrets.ANDROID_KEYSTORE_PASS }}
          androidKeyaliasName: ${{ secrets.ANDROID_KEYALIAS_NAME }}
          androidKeyaliasPass: ${{ secrets.ANDROID_KEYALIAS_PASS }}
      - uses: actions/upload-artifact@v7
        with: { name: build-${{ matrix.targetPlatform }}, path: build/${{ matrix.targetPlatform }} }
```
- Pin `game-ci/*` and `actions/*` to commit SHAs in production repos (supply-chain; see
  ci-cd-dotnet.md). Majors as of 2026-11: unity-builder v6 (thin wrapper over `game-ci/cli`, inputs
  same as v5; v4.8.x still patched), unity-test-runner v4.4 (v5 beta); checkout v7, cache v6,
  upload-artifact v7 (all Node 24). Unity 6.6+ needs builder ≥ v5.0.1/v4.8.2 (shared-memory fix).
- Free disk on `ubuntu-latest` before large Android builds (`jlumbroso/free-disk-space` or manual
  `rm -rf /usr/share/dotnet ...`); standard Linux runners list 14 GB SSD (GitHub runner reference).
- Git LFS bandwidth costs: cache `.git/lfs` keyed on `git lfs ls-files -l` hash.

## Build matrix by platform
| Target | Runner | Gotchas |
|---|---|---|
| Android (AAB) | ubuntu | keystore in secrets (base64); `bundleVersionCode` strictly increasing, max 2100000000; Play requires AAB; from 2026-08-31 new apps/updates must target API 36 (extension to 2026-11-01) |
| iOS | build Xcode project on ubuntu → archive on `macos-*` runner | signing via fastlane `match`; Xcode version pin; `CFBundleVersion` increasing per upload |
| WebGL | ubuntu | Brotli/gzip compression needs matching server `Content-Encoding` headers; memory size; no threads by default |
| StandaloneWindows64 (Mono) | ubuntu ok | IL2CPP Windows needs Windows runner + VS build tools |
| macOS standalone | macos | notarization (`notarytool`) for distribution outside Steam/App Store |
| Dedicated server | ubuntu | `StandaloneLinux64` + server subtarget: `-standaloneBuildSubtarget Server` (customParameters) or `BuildPlayerOptions.subtarget = (int)StandaloneBuildSubtarget.Server`; strips rendering; package into a container (containers-and-k8s.md) |
| Consoles | self-hosted (NDA SDKs) | never on public runners; devkit licences — see `studio:domain-pc-console` |

## Caching the Library folder
- Key = platform + hash(Assets, Packages, ProjectSettings); restore-keys = platform prefix. Never share
  a Library cache across platforms (reimport churn) or Unity versions (add editor version to key).
- GitHub cache: 10 GB/repo free, LRU eviction, 7-day retention default; larger limits paid since
  Nov 2025 (GitHub changelog 2025-11-20). Library > ~5 GB → self-hosted runner with persistent disk.
- Unity Accelerator (cache server) on LAN/self-hosted farm cuts import time for teams and CI.
- Measure: log cold vs warm build minutes in the infra report; target warm < 30% of cold.

## Store upload with fastlane
```ruby
# fastlane/Fastfile
lane :android_internal do
  upload_to_play_store(track: "internal", aab: "build/Android/game.aab",
                       json_key_data: ENV["PLAY_JSON_KEY"], release_status: "draft")
end
lane :ios_beta do
  app_store_connect_api_key(key_id: ENV["ASC_KEY_ID"], issuer_id: ENV["ASC_ISSUER_ID"],
                            key_content: ENV["ASC_KEY_P8"])
  match(type: "appstore", readonly: true)          # certs from encrypted git/S3 repo
  build_app(project: "build/iOS/Unity-iPhone.xcodeproj", scheme: "Unity-iPhone", export_method: "app-store")
  upload_to_testflight(skip_waiting_for_build_processing: true)
end
```
- App Store Connect API key (.p8) over Apple ID passwords (no 2FA prompts in CI).
- CI uploads to internal/TestFlight only. Production promotion = human action owned by
  release-platform-manager (team-protocol: external/irreversible actions need the human).
- Steam: `steamcmd +login <builder> +run_app_build app_build.vdf +quit` to a non-default branch;
  set live manually. Use a dedicated build account (Edit App Metadata + Publish permissions only); persist steamcmd's
  config (login token) between runs - a fresh password login triggers a new Steam Guard code.

## Versioning and build numbers
| Field | Rule |
|---|---|
| Marketing version (`bundleVersion`) | SemVer `MAJOR.MINOR.PATCH`; from git tag (GameCI `versioning: Semantic` = last tag's major.minor + commits since tag) |
| Android `versionCode` / iOS `CFBundleVersion` | integer, monotonically increasing across ALL branches; derive from CI run number + offset, never from SemVer math |
| Server/client compat | expose `protocolVersion` in both; server rejects incompatible clients with "update required" |
| Addressables content | content catalog version independent of binary; record binary→catalog compatibility |
- Stamp commit SHA + build number into a `BuildInfo` ScriptableObject or `Resources/buildinfo.json`
  so crash reports and logs show exactly what shipped.
- Tag releases in git from CI after a store upload succeeds; artifacts retained ≥ lifetime of the release
  (symbols: upload IL2CPP/`.dSYM`/Android symbols to the crash reporter — Crashlytics, Sentry, Backtrace).

## Pipeline checklist
- [ ] PR: compile + EditMode/PlayMode tests + (optional) one fast platform build.
- [ ] main: full matrix, signed artifacts, symbols uploaded, version stamped.
- [ ] Nightly: long tests, perf capture on device farm (Firebase Test Lab / AWS Device Farm), size report.
- [ ] Build size tracked per platform; alert on > 5% growth per release (budget owned by tech-lead-architect).
- [ ] Secrets only in CI secret store / environment secrets; keystores never committed.

## Sources
- GameCI docs: activation, builder, test runner https://game.ci/docs/github/activation , https://game.ci/docs/github/builder
- Unity Manual: Command line arguments https://docs.unity3d.com/Manual/EditorCommandLineArguments.html
- Unity Manual: Dedicated Server https://docs.unity3d.com/Manual/dedicated-server.html
- Unity forum: "Unity no longer supports manual activation of Personal licenses" (2023) https://discussions.unity.com/t/unity-no-longer-supports-manual-activation-of-personal-licenses/926760
- GitHub changelog: Actions cache can exceed 10 GB (2025-11-20) https://github.blog/changelog/2025-11-20-github-actions-cache-size-can-now-exceed-10-gb-per-repository/
- fastlane docs https://docs.fastlane.tools/
- GameCI releases https://github.com/game-ci/unity-builder/releases , https://github.com/game-ci/unity-test-runner/releases
- GitHub-hosted runners reference https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- Google Play target API requirement https://developer.android.com/google/play/requirements/target-sdk
- Steamworks: Uploading to Steam https://partner.steamgames.com/doc/sdk/uploading
- Google Play: versionCode https://developer.android.com/studio/publish/versioning
