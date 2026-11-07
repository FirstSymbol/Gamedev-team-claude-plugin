# AI tooling & GUI-less verification of Unity work

## Unity's own AI (status 2026-11, fast-moving - verify before relying)
| Product | Status | Notes |
|---|---|---|
| Unity Muse (Chat, Sprite, Texture, Animate) | retired 2025-10-01 | replaced by Unity AI; don't add Muse packages |
| Unity AI (Unity 6.2+) | beta; Assistant uses credits - included with Pro/Enterprise/Industry subscriptions, Personal = trial then $10/month (unity.com/products/ai, 2026-11) | in-Editor Assistant (agentic: scene/asset/code actions), Generators (sprites, textures, materials, sound, animation) |
| AI Gateway | connect a verified third-party agent you already subscribe to | bypasses Unity's agent + credit system (no Unity credits consumed); Assistant also offers per-task model choice |
| Inference Engine (formerly Sentis) | runtime package | run ONNX models in player builds (on-device ML), not an authoring tool |
| Unity MCP server (`com.unity.ai.assistant`) | beta, Unity 6.0+, free (no credits, no concurrency limits) | lets external agents (Claude Code, Cursor) drive the Editor |
- Generated assets: track provenance (store/legal policies on AI content) → compliance-advisor;
  record generator + prompt in asset metadata or an art log.

## Unity MCP servers (agent drives a running Editor)
| Server | Install | Requirements | Notes |
|---|---|---|---|
| Official Unity MCP (AI Assistant package) | Package Manager `com.unity.ai.assistant`; Project Settings → AI → Unity MCP Server = Running | Unity 6.0+; MCP server free, no credits needed | relay binary `%USERPROFILE%\.unity\relay\relay_win.exe` (macOS `~/.unity/relay/relay_mac_arm64.app/...` or `relay_mac_x64.app/...`, Linux `~/.unity/relay/relay_linux`) run with `--mcp`; first connection must be approved in Editor (Pending Connections) |
| MCP for Unity (CoplayDev/unity-mcp, MIT) | git URL `https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#main` (pin a tag) or OpenUPM `com.coplaydev.unity-mcp`; Window → MCP for Unity → Configure All Detected Clients | Unity 2021.3 LTS - 6.x, Python 3.10+ via `uv` | ~50 tools: scenes, GameObjects, scripts, assets, materials, tests, profiling, builds, console (catalog: coplaydev.github.io/unity-mcp/reference/tools/; v10.3.0 as of Oct 2026) |
| Other community servers (e.g. IvanMurzak/Unity-MCP) | per README | varies | evaluate maintenance + license before adopting |
```bash
# Claude Code, official relay (Windows example; use absolute path, clients may not expand ~)
claude mcp add unity -- "C:\Users\<you>\.unity\relay\relay_win.exe" --mcp
# target a specific project/editor when several are open
claude mcp add unity -- <relay> --mcp --project-path "D:\Game"   # or --instance-id <pid> / UNITY_PROJECT_PATH env
```
- Official tool names seen in docs: `Unity.ManageScene`, `Unity.ManageGameObject`, `Unity_ReadConsole`
  (names differ across package versions 2.4 → 2.17 - list tools after connecting).
- Rules for agents using MCP:
  - Commit (or stash) before a session of MCP edits - scene changes are hard to diff/undo.
  - Prefer creating/editing C# + running tests over many tiny scene mutations.
  - After each mutation batch: read console (errors/warnings), save scenes explicitly.
  - Security: MCP = arbitrary Editor code execution. Approve only known clients; never on
    machines holding signing keys/store credentials without human consent.
- MCP needs an open Editor; batch mode needs the project NOT open (project lock). Pick one.

## Batch-mode CLI (no GUI)
- Editor binary (Hub default): Windows `C:\Program Files\Unity\Hub\Editor\<ver>\Editor\Unity.exe`;
  macOS `/Applications/Unity/Hub/Editor/<ver>/Unity.app/Contents/MacOS/Unity`;
  Linux `~/Unity/Hub/Editor/<ver>/Editor/Unity`. `<ver>` from `ProjectSettings/ProjectVersion.txt`.
- Requires an activated license on the machine (Hub login; CI: serial/license server).
```bash
U="/c/Program Files/Unity/Hub/Editor/6000.3.<x>f1/Editor/Unity.exe"; P="$(pwd)"
# 1) Compile/import check (exits non-zero on script compile errors)
"$U" -batchmode -nographics -quit -projectPath "$P" -logFile build/compile.log
grep -E "error CS[0-9]+|Scripts have compiler errors" build/compile.log
# 2) EditMode tests (do NOT pass -quit with -runTests)
"$U" -batchmode -nographics -projectPath "$P" -runTests -testPlatform EditMode \
     -testResults build/editmode.xml -logFile build/editmode.log
# 3) PlayMode tests (drop -nographics if tests render/need GPU)
"$U" -batchmode -projectPath "$P" -runTests -testPlatform PlayMode \
     -testResults build/playmode.xml -logFile build/playmode.log
# 4) Custom editor step (asset validation, data import, build)
"$U" -batchmode -nographics -quit -projectPath "$P" -executeMethod Game.Editor.CI.ValidateAll -logFile build/validate.log
# 5) Player build from a Unity 6 Build Profile asset
"$U" -batchmode -quit -projectPath "$P" -activeBuildProfile "Assets/Settings/Build Profiles/Android.asset" -build "build/Game.aab" -logFile build/android.log
```
- Useful test args: `-testFilter "Namespace.Class.Method;Other"` (regex ok), `-testCategory "fast;!slow"`,
  `-assemblyNames Game.Tests.EditMode`, `-retry 2` (flaky), `-repeat N`, `-runSynchronously` (EditMode, single frame only).
- Exit codes: commonly observed 0 = pass, 2 = test failures, 1 = other error, but UTF docs state "no common
  definition for exit codes" - never rely on the code alone; always parse `-testResults` XML: `<test-run ... total= passed= failed=>`
  and `<test-case result="Failed">` → `<message>`, `<stack-trace>`.
- `-executeMethod` target: `static` method in an Editor assembly; end with
  `EditorApplication.Exit(ok ? 0 : 1)` so CI sees failure; log with `Debug.Log` (goes to `-logFile`).
- `-logFile -` streams to stdout (on Windows only when launched with a configured stdout, e.g. from CI).
- One target per invocation; pass `-buildTarget` or `-activeBuildProfile` up front (switching
  target inside a batch run reloads assemblies and is unreliable).
- Batch mode fails fast if the project is open in another Editor ("another Unity instance is
  running") - ask the human to close it or use MCP instead.
- First run on a clean clone imports everything (`Library/` rebuild): minutes to hours; cache
  `Library/` in CI keyed on `Packages/packages-lock.json` + editor version.

## Logs
| Log | Location |
|---|---|
| Editor (default) | Win `%LOCALAPPDATA%\Unity\Editor\Editor.log`; macOS `~/Library/Logs/Unity/Editor.log`; Linux `~/.config/unity3d/Editor.log` |
| Editor (batch runs) | wherever `-logFile` points - always set it per step |
| Player | Win `%USERPROFILE%\AppData\LocalLow\<Company>\<Product>\Player.log`; macOS `~/Library/Logs/<Company>/<Product>/Player.log`; Linux `~/.config/unity3d/<Company>/<Product>/Player.log` |
| Android / iOS / Web | `adb logcat -s Unity` / Xcode device console / browser JS console |
| Package Manager | `upm.log` next to Editor.log |
| Crashes | Editor `%TMP%\Unity\Editor\Crashes` (override `-crash-report-folder`) |
- In code: `Application.consoleLogPath`. Grep, don't read whole logs: `error CS`, `Exception`,
  `NullReferenceException`, `Build completed with a result of`, `Missing Prefab`, `The referenced script`.

## Verification ladder for agents (report which rung was reached)
| Rung | How | Proves |
|---|---|---|
| 0 Static | Grep/Glob, Roslyn analyzers (`Microsoft.Unity.Analyzers`) in IDE/CI | conventions, obvious API misuse |
| 1 Compile | batch `-quit` import, grep `error CS` | code + asmdef refs compile for the active target |
| 2 EditMode tests | `-runTests -testPlatform EditMode` | pure logic |
| 3 PlayMode tests | `-runTests -testPlatform PlayMode` | lifecycle, scenes, prefabs |
| 4 Validation | `-executeMethod` validators (missing refs, import rules, Addressables analyze) | content integrity |
| 5 Player build | `-activeBuildProfile ... -build` | IL2CPP/stripping, platform code |
| 6 Device smoke | human or device farm | real perf, input, platform services |
- No Unity installed / no license → state "unverified: rungs 1+ need the human", list exact commands.
- Never claim a rung you did not run; attach log/XML paths in the impl report.

## Sources
- Unity AI product page (beta, credits, AI Gateway, free MCP) https://unity.com/products/ai
- Unity AI Assistant: Unity MCP get started https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.17/manual/integration/unity-mcp-get-started.html
- Unity blog: Unity's AI tools in beta - how to get started with MCP https://unity.com/en/blog/unity-ai-mcp-how-to-get-started
- CoplayDev/unity-mcp (MCP for Unity) https://github.com/CoplayDev/unity-mcp
- Unity Muse retirement notice (Muse docs) https://docs.unity3d.com/Packages/com.unity.muse.chat@1.1/manual/index.html
- Test Framework: Running tests from the command line https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-command-line.html
- Unity Manual 6.3: Log files https://docs.unity.com/en-us/engine/6000.3/manual/get-started/project-configuration/log-files
- Unity Manual: Build from the command line https://docs.unity.com/en-us/engine/current/manual/building-and-publishing/build-command-line
- Unity Manual: Editor command line arguments https://docs.unity3d.com/Manual/EditorCommandLineArguments.html
