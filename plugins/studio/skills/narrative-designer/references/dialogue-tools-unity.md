# Dialogue tools in Unity: choose, integrate, conventions

## Choose
| Tool | Authoring | Strengths | Weak spots | Licence/cost (verify) |
|---|---|---|---|---|
| Ink (inkle) | plain-text markup; Inky editor | writer-friendly prose, powerful flow (knots/stitches/diverts/weave), state + lists, mature C# runtime | no built-in localisation pipeline; visual overview weak | MIT; Unity package free (`ink-unity-integration`) |
| Yarn Spinner | screenplay-like text; VS Code extension | line IDs + built-in localisation, Unity Localization provider, commands as C# attributes, storylets/saliency & line groups (v3) | complex systemic state lives in C# | MIT core; Unity package via GitHub/OpenUPM or paid stores |
| articy:draft X | visual flow/database app | visual flows, entity database (characters/items), designer-friendly, Unity importer + flow player | separate commercial app; merge/diff of project files; licence per seat | commercial; importer free |
| Pixel Crushers Dialogue System | Unity editor + importers | full runtime (UI, quests, barks, save), imports articy/ink/others | asset-store dependency; large | commercial Asset Store |
| Custom (SO graph) | Unity editor | exact fit | you own tooling, loc, debug forever | dev time |
- Default picks: writer-led linear/branching story → Ink; dialogue-heavy game needing
  localisation + VO + barks → Yarn Spinner; large RPG with item/character database and
  non-technical writers → articy:draft X. Decide with unity-developer; record an ADR.

## Ink integration (Unity)
- Install `ink-unity-integration` via Package Manager (git URL/OpenUPM); `.ink` files
  auto-compile to JSON next to the source; Ink Player Window for testing in editor.
```csharp
using Ink.Runtime;
public sealed class InkDialogue {
    readonly Story _story;
    public InkDialogue(TextAsset compiledJson) {
        _story = new Story(compiledJson.text);
        _story.BindExternalFunction("play_sfx", (string id) => Audio.Play(id)); // ink: EXTERNAL play_sfx(id)
        _story.ObserveVariable("gold", (_, v) => Wallet.SyncFromStory((int)v));
    }
    public bool Next(out string line, out List<string> tags) {
        line = null; tags = null;
        if (!_story.canContinue) return false;
        line = _story.Continue().Trim(); tags = _story.currentTags; return true;
    }
    public IReadOnlyList<Choice> Choices => _story.currentChoices;
    public void Choose(int i) => _story.ChooseChoiceIndex(i);
    public string Save() => _story.state.ToJson();
    public void Load(string json) => _story.state.LoadJson(json);
}
```
- Ink conventions: `#speaker:kai`, `#id:<lineId>` tags on every line (for loc/VO), knots
  per scene (`=== harbor_intro ===`), globals in one `globals.ink`, `EXTERNAL` list documented
  as the writer↔dev contract. Localisation: map `#id` tags to string tables (custom tool) or
  ship per-language ink files (verify current community approach).

## Yarn Spinner integration (Unity)
- Components: Yarn Project asset (compiles `.yarn` files), `DialogueRunner`, dialogue
  presenters (Line Presenter, Options Presenter in v3; "Dialogue Views" in v2), Line
  Provider (built-in localised or Unity Localization provider), Variable Storage.
```yarn
title: Harbor_Intro
---
Kai: The ferry's late again. #line:harbor_intro_01
-> Ask why #line:harbor_intro_02
    Kai: Storm up north. <<set $knows_storm to true>> #line:harbor_intro_03
-> Leave #line:harbor_intro_04
<<play_sfx gull>>
===
```
```csharp
public sealed class DialogueAudio : MonoBehaviour {
    [YarnCommand("play_sfx")] public static void PlaySfx(string id) => Audio.Play(id); // static: no target object
}
// or: dialogueRunner.AddCommandHandler<string>("play_sfx", Audio.Play);
// start: dialogueRunner.StartDialogue("Harbor_Intro");
```
- Line IDs: "Add Line Tags to Scripts" on the Yarn Project generates `#line:` IDs; strings
  files cannot be generated until every line has an ID. Commands may be coroutines/async
  (dialogue waits).
- v3 content selection: node groups (same `title` + `when:` headers; `<<jump Alice>>`
  picks most salient), line groups (`=> ` lines with `<<if …>>` conditions); saliency
  strategies: Best, Best Least Recently Viewed, Random Best Least Recently Viewed
  (recommended default), Random.

## articy:draft X integration
- Export from articy with the Unity export → articy Importer for Unity (free) generates
  typed C# classes and an `ArticyDatabase`. `ArticyFlowPlayer` component traverses flows;
  implement `IArticyFlowPlayerCallbacks` (`OnFlowPlayerPaused`, `OnBranchesUpdated`) on the
  same GameObject; set "Pause On" to Dialogue Fragments. Query objects by id, technical name
  or type via `ArticyDatabase`.
- Use technical names (not display names) in code; lock the template/feature schema early
  — schema changes regenerate code.

## Writer ↔ developer contract (write `40-narrative/dialogue-conventions.md`)
| Item | Convention example |
|---|---|
| File layout | one file per scene/area: `Assets/_Project/Narrative/<area>/<scene>.yarn` |
| Node/knot names | `Area_Scene_Beat` (PascalCase_Underscore) |
| Line IDs | tool-generated, never edited or reused; deleted lines keep IDs retired |
| Speakers | fixed character keys from `characters.md` (`kai`, `hilde`) |
| Commands | list: name, params, effect, owner, sync/async (`<<camera_focus kai 0.5>>`) |
| Variables | `$snake_case`, typed, declared once; save-relevant ones flagged |
| Tags | `#vo:`, `#emotion:`, `#anim:` — enumerated list only |
| Markup | rich-text tags allowed list (TMP `<b>`, `<i>`, custom `[wave]`); no layout hacks |
| Max line length | dialogue box limit in chars per language (from ux-ui-designer) |

## Testing & CI
- In-editor playthrough tools (Ink Player Window, Yarn preview in VS Code, articy simulation).
- Lint before handoff: unreachable nodes, missing line IDs, undefined variables/commands,
  lines over max length. Ask unity-developer for a batch-mode compile/lint step in CI.
- Save/load: persist dialogue state (ink `state.ToJson()`, Yarn variable storage) in the
  game's versioned save DTO; test mid-conversation save if allowed.
- VO: lock script per scene before recording; VO file names = line IDs.

## Sources
- inkle, ink-unity-integration https://github.com/inkle/ink-unity-integration
- inkle, "Writing with ink" https://github.com/inkle/ink/blob/master/Documentation/WritingWithInk.md
- Yarn Spinner docs, Commands and Functions (Unity) https://docs.yarnspinner.dev/yarn-spinner-for-unity/creating-commands-functions
- Yarn Spinner docs, Line Provider https://docs.yarnspinner.dev/components/line-provider
- Yarn Spinner docs, Storylets and saliency https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/storylets-and-saliency-a-primer
- articy, Importer for Unity tutorial (lesson 2: flow player) https://www.articy.com/en/importer-for-unity-tutorial-l2/
- articy, Unity integration downloads https://www.articy.com/en/downloads/unity
