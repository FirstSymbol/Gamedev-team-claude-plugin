# Unity test automation (QA view)
Engineer-level unit test patterns: `studio:unity-developer` (testing-unity); batch mode and logs:
`studio:stack-unity` (ai-tooling). This file: QA scenarios, UI/input, device E2E, CI results.

## Where each check lives
| Check | Tool | Runs |
|---|---|---|
| Rules, reward math, economy calc, state machines | UTF EditMode (NUnit) on plain C# | every PR, seconds |
| Scene/prefab wiring, lifecycle, Addressables load, UI flow in one scene | UTF PlayMode in Editor | every PR / nightly |
| Same on real hardware (IL2CPP, GPU, memory) | UTF PlayMode player run `-testPlatform Android|iOS|StandaloneWindows64` | nightly |
| Full journeys on devices (FTUE, purchase sandbox, claim bonus) | AltTester / GameDriver / Airtest+Poco | nightly / RC |
| Frame time / allocations regression | Performance Testing package (`com.unity.test-framework.performance`) | nightly on reference device |

## Test assemblies
- Tests in asmdefs: `Game.Tests.EditMode` (`includePlatforms: [Editor]`) and `Game.Tests.PlayMode`
  (all platforms), both with `defineConstraints: ["UNITY_INCLUDE_TESTS"]`, references `UnityEngine.TestRunner`,
  `UnityEditor.TestRunner` (EditMode only), `nunit.framework.dll` (precompiled reference).
- Package: `com.unity.test-framework` (bundled with the editor - check the installed version in Package Manager;
  package docs list releases up to 1.9.0; for Unity 6.2+ the user guide lives in the Unity Manual).
- Categories drive selection: `[Category("Smoke")]`, `[Category("Slow")]`, `[Category("Device")]`.

## EditMode pattern: deterministic time and RNG
```csharp
public sealed class FakeClock : IClock { public DateTime UtcNow { get; set; } }

public class DailyBonusTests {
    [TestCase(1, 0, 100)] [TestCase(5, 4, 600)] [TestCase(2, 3, 225)] [TestCase(7, 7, 2000)]
    public void Reward_UsesStreakTableAndVipMultiplier(int day, int vip, long expected) =>
        Assert.That(DailyBonusRules.Reward(day, vip), Is.EqualTo(expected));

    [Test]
    public void Claim_AtUtcMidnightBoundary_StartsNewDay() {
        var clock = new FakeClock { UtcNow = new DateTime(2026, 3, 1, 23, 59, 59, DateTimeKind.Utc) };
        var svc = new DailyBonusService(clock, new InMemoryBonusStore());
        Assert.That(svc.Claim("p1").Granted, Is.True);
        Assert.That(svc.Claim("p1").Error, Is.EqualTo(ClaimError.AlreadyClaimed));
        clock.UtcNow = clock.UtcNow.AddSeconds(1);                 // 00:00:00 next day
        Assert.That(svc.Claim("p1").StreakDay, Is.EqualTo(2));
    }
}
```
- Seeded RNG: inject `IRandom`/`System.Random(seed)`; never `UnityEngine.Random` without `InitState(seed)`.

## PlayMode pattern: scene + condition waits
```csharp
public class LobbyFlowTests {
    [UnitySetUp] public IEnumerator Load() {
        yield return SceneManager.LoadSceneAsync("Lobby", LoadSceneMode.Single);
    }

    [UnityTest, Timeout(30000), Category("Smoke")]
    public IEnumerator ClaimButton_GrantsCoins() {
        var view = Object.FindAnyObjectByType<DailyBonusView>();
        var before = view.Balance;
        view.ClaimButton.onClick.Invoke();                         // logic path; input path below
        yield return WaitUntil(() => view.Balance > before, 5f);
        Assert.That(view.Balance - before, Is.EqualTo(100));
        LogAssert.NoUnexpectedReceived();                          // fail on unexpected errors
    }

    static IEnumerator WaitUntil(Func<bool> cond, float timeout) {
        var t = 0f;
        while (!cond()) { t += Time.unscaledDeltaTime; if (t > timeout) Assert.Fail("timeout"); yield return null; }
    }
}
```
- Never `WaitForSeconds` as synchronization; wait on state with a timeout.
- `LogAssert.Expect(LogType.Error, regex)` for expected errors; unhandled error logs fail the test by default.
- Use `[UnityTearDown]` to unload scenes/destroy spawned objects; reset statics (Fast Enter Play Mode).
- Server calls: point the client at a fake HTTP server or test backend via config; never prod.
- Async: UTF 1.3+ runs `[Test] public async Task X()` on the main thread; failing logs are evaluated only
  after the test ends; avoid `Assert.ThrowsAsync` (blocks the Editor) - try/catch instead. Else `[UnityTest]` + `IEnumerator`.

## UI testing
| UI tech | Approach |
|---|---|
| uGUI | Find by name/test ID component; simulate via `ExecuteEvents.Execute(go, new PointerEventData(EventSystem.current), ExecuteEvents.pointerClickHandler)` or real input (below); assert on presenter state, then on text (`TMP_Text.text`) |
| UI Toolkit | `uiDocument.rootVisualElement.Q<Button>("claim-button")`; prefer testing the presenter/view-model; for event path `using var e = NavigationSubmitEvent.GetPooled(); e.target = btn; btn.SendEvent(e);` or real pointer input via Input System |
| Both | Add stable IDs (`name`, `TestId` component) for automation; never locate by hierarchy index or localized text |

## Input simulation: Input System test fixture
- Manifest: add `"testables": ["com.unity.inputsystem"]`; test asmdef references `Unity.InputSystem`
  and `Unity.InputSystem.TestFramework`.
```csharp
public class PlayerInputTests : InputTestFixture {          // isolates devices per test
    [UnityTest]
    public IEnumerator SouthButton_Jumps() {
        var gamepad = InputSystem.AddDevice<Gamepad>();
        var player = Object.Instantiate(Resources.Load<PlayerController>("TestPlayer"));
        Press(gamepad.buttonSouth);
        yield return null;
        Release(gamepad.buttonSouth);
        yield return new WaitForFixedUpdate();
        Assert.That(player.IsAirborne, Is.True);
    }

    [UnityTest]
    public IEnumerator Tap_OnClaimButton() {
        var mouse = InputSystem.AddDevice<Mouse>();
        Set(mouse.position, ScreenPointOf("ClaimButton"));   // helper: RectTransformUtility.WorldToScreenPoint
        PressAndRelease(mouse.leftButton);
        yield return null;
        // assert presenter state
    }
}
```
- Touch: `InputSystem.AddDevice<Touchscreen>()` + `BeginTouch/EndTouch`; also test controller disconnect via
  `InputSystem.RemoveDevice(gamepad)` (console requirement: pause + reconnect prompt).

## Device E2E options
| Tool | Model | Strengths | Watch out |
|---|---|---|---|
| AltTester Unity SDK (2.x) | SDK instruments build; drivers in C#, Python, Java, Robot | object-level queries (name/path/component), Unity + Appium combo, free OSS SDK | never ship instrumented builds; SDK 2.4 "free, open source" but some UI Toolkit commands are marked Non-GPL (verify: package LICENSE + Desktop terms) |
| GameDriver | commercial agent + C# API (NUnit) | Unity and Unreal, XR, HierarchyPath queries | license cost |
| Airtest + Poco (NetEase) | image recognition + Poco SDK for Unity UI tree; Python | cross-engine, image fallback for non-UI | image tests brittle across resolutions |
| Appium (UiAutomator2/XCUITest) | OS-level automation | system dialogs (permissions, ATT, store purchase sheet) | cannot see Unity objects without AltTester/Poco |
Device farms: Firebase Test Lab, AWS Device Farm, BrowserStack (verify: farm allows the instrumented app to reach AltTester Server / port 13000).
AltTester C# sketch (instrumented app / AltTester Server reachable; default port 13000; `WaitForObject` timeout default 20 s):
```csharp
var alt = new AltDriver();                                    // 127.0.0.1:13000
alt.LoadScene("Lobby");
alt.WaitForObject(By.NAME, "ClaimButton", timeout: 10).Tap();
var balance = alt.WaitForObject(By.NAME, "BalanceLabel").GetText();
Assert.That(balance, Is.EqualTo("5,100"));                    // locale-aware formatting!
alt.Stop();
```
- Instrument only in a dedicated Build Profile / scripting define (e.g. `ALTTESTER`); CI check that release builds
  contain no AltTester assemblies.

## Batch-mode CLI
```bash
Unity -batchmode -projectPath . -runTests -testPlatform EditMode \
  -testResults artifacts/editmode.xml -logFile artifacts/editmode.log
Unity -batchmode -projectPath . -runTests -testPlatform PlayMode \
  -testCategory "Smoke;!Slow" -testResults artifacts/playmode.xml -logFile artifacts/playmode.log
Unity -batchmode -projectPath . -runTests -testPlatform Android \
  -testResults artifacts/android.xml -logFile artifacts/android.log    # builds + runs player on device
```
- Do not add `-quit` with `-runTests` (not supported while tests run). `-testFilter`/`-testCategory` take
  `;`-lists or regex; `!` excludes; both given = intersection.
- `-retry 1` reruns failures: a test that passes on retry is **flaky** - report it, don't count it green.
- `-repeat N` to hunt flakiness; `-playerHeartbeatTimeout` (default 10 min) for slow device startup.
- `-nographics` fine for EditMode; PlayMode tests that render/need GPU run without it.
- Exit codes: UTF docs state "no common definition for exit codes" - always parse the XML; non-zero exit or missing
  XML = run error. Coverage: `-enableCodeCoverage -coverageResultsPath artifacts/coverage`.

## Parsing results (NUnit 3 XML)
Root `<test-run total= passed= failed= skipped= result=>`; leaves `<test-case fullname= result="Passed|Failed|Skipped" duration=>` with `<failure><message/><stack-trace/></failure>`.
```python
import sys, xml.etree.ElementTree as ET
r = ET.parse(sys.argv[1]).getroot()
print(f"total={r.get('total')} passed={r.get('passed')} failed={r.get('failed')} skipped={r.get('skipped')}")
for tc in r.iter("test-case"):
    if tc.get("result") == "Failed":
        msg = (tc.findtext("failure/message") or "").strip().splitlines()[:1]
        print(f"FAIL {tc.get('fullname')} :: {msg[0] if msg else ''}")
sys.exit(1 if int(r.get("failed", "0")) else 0)
```
- CI: publish XML to the CI test tab (most CI systems read NUnit/JUnit); keep `.log` as artifact.
- Compile errors produce no XML: grep the log for `error CS` and report as run failure, not test failure.

## Performance regression tests
```csharp
[UnityTest, Performance]
public IEnumerator Lobby_FrameTime() {
    yield return SceneManager.LoadSceneAsync("Lobby");
    yield return Measure.Frames().WarmupCount(30).MeasurementCount(300).Run();
}
```
Run on a fixed reference device; compare medians/p95 with previous baseline (±10% gate, see qa-lead gates).

## Sources
- Unity Test Framework manual, command-line reference https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-command-line.html
- Unity 6.3 Manual, Test Framework command-line reference https://docs.unity.com/en-us/engine/6000.3/manual/programming-environment/test-framework-introduction/reference-command-line
- UTF async tests https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-async-tests.html
- AltTester SDK commands (AltDriver defaults 127.0.0.1:13000, WaitForObject timeout 20 s) https://alttester.com/docs/sdk/latest/pages/commands.html
- Unity Input System manual, Input testing https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/manual/Testing.html
- AltTester Unity SDK docs https://alttester.com/docs/sdk/latest/
- Airtest / Poco (NetEase) https://airtest.netease.com/
- Unity Performance Testing package https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0/manual/index.html
- Unity Code Coverage package https://docs.unity3d.com/Packages/com.unity.testtools.codecoverage@1.2/manual/index.html
- GameDriver https://www.gamedriver.io/
