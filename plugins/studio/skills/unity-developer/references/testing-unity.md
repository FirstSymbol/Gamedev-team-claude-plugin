# Unity testing (Test Framework, NUnit, perf tests, coverage, CI)

## Unity Test Framework (UTF) status
| Version | Notes |
|---|---|
| 1.4.x | Unity 2022 LTS / 6.0 era; `-retry`/`-repeat` CLI options exist since 1.3.5 |
| 1.5.x | 1.5.1 (2025-02-26) moved into Unity source as an embedded package - version follows the editor |
| 1.6.x | Unity 6.2+; user guide lives in the Unity Manual |
| 2.0.x-exp | experimental line, reportedly dropped; forum: 6.0.44 resolves to 1.5 even with 2.0.1 pinned - don't target 2.0 |
- Don't pin UTF in `manifest.json` on Unity 6 unless a package demands it; use the editor's version.
- NUnit is a Unity-customized NUnit 3.5 (`com.unity.ext.nunit` 2.0) - newer NUnit features (e.g. some constraint APIs) may be missing.
- UI Toolkit interaction tests: UI Test Framework package (Unity 6.3).

## EditMode vs PlayMode
| | EditMode | PlayMode |
|---|---|---|
| Runs | in Editor, no play loop (`[UnityTest]` yields = editor updates) | in Play Mode (Editor) or in a built player (`-testPlatform <BuildTarget>`) |
| Speed | ms per test | seconds (enter play mode, scene setup) |
| Use for | domain logic, services with fakes, ScriptableObject validation, editor tools, asset/import rules | MonoBehaviour lifecycle, physics, coroutines/Awaitable timing, scene/prefab integration, input simulation |
| Target | 70-80% of tests | the rest; keep each test isolated (own scene or cleanup) |
- Player-target PlayMode runs catch IL2CPP/stripping/platform bugs that Editor runs can't.

## asmdef setup
```jsonc
// Tests/EditMode/Game.Tests.EditMode.asmdef  (comments illustrative - real asmdef JSON has none)
{ "name": "Game.Tests.EditMode",
  "references": ["Game.Core", "UnityEngine.TestRunner", "UnityEditor.TestRunner"],
  "includePlatforms": ["Editor"],
  "overrideReferences": true, "precompiledReferences": ["nunit.framework.dll"],
  "autoReferenced": false, "defineConstraints": ["UNITY_INCLUDE_TESTS"] }
// Tests/PlayMode/Game.Tests.PlayMode.asmdef: same, but "includePlatforms": [] (all) and
// reference UnityEngine.TestRunner only (UnityEditor.TestRunner breaks player builds).
```
- Production asmdefs never reference test asmdefs. Internal access: `[assembly: InternalsVisibleTo("Game.Tests.EditMode")]`.
- Testing a package: add it to `testables` in `Packages/manifest.json`.

## NUnit + UTF essentials
```csharp
public class DailyRewardServiceTests {
    FakeClock _clock; DailyRewardService _sut;
    [SetUp] public void SetUp() { _clock = new FakeClock(new DateTime(2026, 1, 1)); _sut = new DailyRewardService(_clock, TestConfigs.Rewards()); }

    [Test] public void Claim_SameDayTwice_SecondIsRejected() {
        Assert.That(_sut.TryClaim(out _), Is.True);
        Assert.That(_sut.TryClaim(out _), Is.False);
    }
    [TestCase(0, 100)] [TestCase(6, 700)]
    public void Reward_ScalesWithStreak(int streak, int expected) => Assert.That(_sut.RewardFor(streak), Is.EqualTo(expected));
}

public class PlayerMovementPlayTests {
    GameObject _go;
    [UnityTest] public IEnumerator Jump_LeavesGround() {
        _go = Object.Instantiate(TestAssets.LoadPrefab("Player"));        // see "assets in tests"
        var mover = _go.GetComponent<PlayerMover>();
        mover.Jump();
        yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
        Assert.That(_go.transform.position.y, Is.GreaterThan(0f));
    }
    [TearDown] public void TearDown() { if (_go) Object.Destroy(_go); }
}
```
- `[UnityTest]` returns `IEnumerator` (yield frames); `[UnitySetUp]`/`[UnityTearDown]` for multi-frame setup.
- `async Task` tests: `[Test] public async Task X()` supported since UTF 1.3 (incl. SetUp/TearDown); `Awaitable`
  as a test return type is not documented - return `Task` and await Awaitables inside.
- Logs: an unexpected `Debug.LogError`/exception fails the test; expect with
  `LogAssert.Expect(LogType.Error, new Regex("not found"))`; `LogAssert.ignoreFailingMessages` only temporarily.
- `[Category("Slow")]`, `[Timeout(ms)]`, `[Retry(n)]` sparingly; `[Ignore("reason + ticket")]` never without ticket.
- `[UnityPlatform(RuntimePlatform.Android)]`, `[RequiresPlayMode]`, `[PrebuildSetup(typeof(T))]`
  (`IPrebuildSetup` builds test data before run, e.g. generated scenes).
- Name tests `Method_Condition_Expected`; one behavior per test; arrange-act-assert.

## Test doubles & testable design
- Put logic in plain C# behind interfaces (`IClock`, `IRandom`, `ISaveStore`, `IAnalytics`);
  MonoBehaviour is a humble view → logic is EditMode-testable (see architecture-patterns.md).
- Prefer handwritten fakes. NSubstitute/Moq work in Editor (Mono) but rely on runtime proxy
  generation (Reflection.Emit) → fail in IL2CPP player test runs.
- Time: never `DateTime.Now`/`Time.time` inside logic; inject. Random: seeded `System.Random`/`Unity.Mathematics.Random`.
- ScriptableObject configs: `ScriptableObject.CreateInstance<T>()` in tests + set fields; destroy in TearDown.
- MonoBehaviours in EditMode: `new GameObject().AddComponent<T>()` (Awake runs; Update/Start don't) -
  `Object.DestroyImmediate` in TearDown.
- Assets in tests: Editor-only PlayMode runs can use `AssetDatabase.LoadAssetAtPath` inside
  `#if UNITY_EDITOR`; for player runs use Addressables/Resources test folders or `[PrebuildSetup]`.
- Scenes: `EditorSceneManager.LoadSceneInPlayMode(path, new LoadSceneParameters(LoadSceneMode.Additive))`
  in Editor; player runs need the scene in the test build list.
- Input simulation: Input System `InputTestFixture` (add `Unity.InputSystem.TestFramework` reference):
  `Press(keyboard.spaceKey)`, `Set(gamepad.leftStick, new Vector2(1,0))`.
- Determinism for physics tests: fixed timestep, no frame-rate dependence; assert ranges, not exact floats.

## Performance tests (`com.unity.test-framework.performance` 3.x)
```csharp
[Test, Performance] public void Pathfinding_64x64() =>
    Measure.Method(() => _grid.FindPath(a, b))
        .WarmupCount(5).MeasurementCount(20).IterationsPerMeasurement(10).GC().Run();

[UnityTest, Performance] public IEnumerator BattleScene_FrameTime() {
    yield return LoadBattleScene();
    yield return Measure.Frames().WarmupCount(30).MeasurementCount(300).Run();   // PlayMode only
}
```
- Results land in the test results XML/JSON; compare against a baseline per device; fail CI on
  regression threshold (e.g. median +10%) rather than absolute numbers on shared runners.
- `Measure.ProfilerMarkers(...)` to sample existing markers; `.GC()` counts allocations - assert 0 for hot paths.

## Code coverage (`com.unity.testtools.codecoverage` 1.2/1.3)
```bash
Unity -batchmode -projectPath . -runTests -testPlatform EditMode -enableCodeCoverage \
  -coverageResultsPath build/coverage \
  -coverageOptions "generateHtmlReport;generateAdditionalMetrics;assemblyFilters:+Game.*,-Game.Tests.*"
```
- Quote `-coverageOptions` (semicolons). Coverage target for domain/services asmdefs (e.g. ≥ 70%);
  don't chase coverage on views.

## Batch mode & CI
```bash
Unity -batchmode -nographics -projectPath . -runTests -testPlatform EditMode \
      -testResults build/editmode.xml -logFile build/editmode.log      # no -quit with -runTests
Unity -batchmode -projectPath . -runTests -testPlatform PlayMode -testCategory "!Slow" \
      -testResults build/playmode.xml -logFile build/playmode.log
```
- More flags (`-testFilter`, `-assemblyNames`, `-retry`, `-repeat`, `-runSynchronously`) and
  exit codes / log parsing: `studio:stack-unity` (ai-tooling).
- GameCI (GitHub Actions):
```yaml
- uses: actions/cache@v4
  with: { path: Library, key: Library-${{ hashFiles('Packages/packages-lock.json', 'ProjectSettings/ProjectVersion.txt') }} }
- uses: game-ci/unity-test-runner@v4
  env: { UNITY_LICENSE: "${{ secrets.UNITY_LICENSE }}", UNITY_EMAIL: "${{ secrets.UNITY_EMAIL }}", UNITY_PASSWORD: "${{ secrets.UNITY_PASSWORD }}" }
  with: { testMode: all, githubToken: "${{ secrets.GITHUB_TOKEN }}", coverageOptions: "generateAdditionalMetrics;assemblyFilters:+Game.*" }
- uses: actions/upload-artifact@v4
  if: always()
  with: { name: test-results, path: artifacts }
```
- Personal license: one-time manual activation → store license file as secret; Pro: serial or
  floating license server (`unityLicensingServer`). Pipeline ownership → devops-sre-engineer.
- PR gate: compile + EditMode on every PR (< 10 min); PlayMode + player tests nightly or on main.

## Checklist
- [ ] Test asmdefs with `UNITY_INCLUDE_TESTS`, EditMode = Editor-only, PlayMode without editor refs.
- [ ] New logic has EditMode tests; lifecycle/integration behaviors have PlayMode tests.
- [ ] No real time/random/network in tests; fakes injected; objects destroyed in TearDown.
- [ ] Tests pass in batch mode (XML attached); flaky tests fixed or quarantined with a ticket.
- [ ] Hot paths covered by a perf test with `.GC()` = 0 where required.

## Sources
- Test Framework 1.6 manual https://docs.unity3d.com/Packages/com.unity.test-framework@1.6/manual/index.html
- Test Framework 1.5 changelog https://docs.unity3d.com/Packages/com.unity.test-framework@1.5/changelog/CHANGELOG.html
- Test Framework: Running tests from the command line https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-command-line.html
- Performance Testing: Measure.Method https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0/manual/measure-method.html
- Performance Testing: Measure.Frames https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0/manual/measure-frames.html
- Code Coverage in batchmode https://docs.unity3d.com/Packages/com.unity.testtools.codecoverage@1.2/manual/CoverageBatchmode.html
- GameCI test runner docs https://game.ci/docs/github/test-runner
- Unity forum: Hard dependency on Test Framework 1.5? https://discussions.unity.com/t/hard-dependency-on-test-framework-1-5/1632378
- Custom NUnit package (based on NUnit 3.5) https://docs.unity3d.com/Packages/com.unity.ext.nunit@2.0/manual/index.html
