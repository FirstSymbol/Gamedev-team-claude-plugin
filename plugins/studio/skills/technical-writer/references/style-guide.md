# Technical English style (team rules)

Defaults follow the Google developer documentation style guide and Microsoft Writing Style
Guide; project-specific rules in `.team/specs/docs/glossary.md` win.

## Core rules
| Rule | Do | Don't |
|---|---|---|
| Person | "you" for the reader | "the user should", "we will now" |
| Voice | active: "The service retries the call." | passive: "The call is retried." |
| Tense | present: "returns" | future: "will return" |
| Mood (steps) | imperative: "Run `dotnet test`." | "You might want to run…" |
| Front-load | goal/condition first: "To rotate the key, run…" | burying the action at the end |
| Brevity | one idea per sentence; ≤ ~25 words | stacked clauses, "in order to" |
| Headings | sentence case, no end period: "Configure the wallet service" | Title Case, "Configuration:" |
| Lists | numbered for sequences, bullets otherwise; parallel grammar | mixed fragments and sentences |
| Commas | serial comma: "Android, iOS, and Windows" | "Android, iOS and Windows" |
| Links | descriptive text: "see [Deploy to staging](…)" | "click here" |
| Dates/times | ISO `2026-11-07`, UTC stated: `00:00 UTC` | `11/07/26`, "midnight" |
| Numbers | numerals for counts/values with units: `5 s`, `512 MB` | "five seconds" in tech specs |
| Code | code font for code, paths, commands, keys: `appsettings.json` | quotes or bold for code |
| UI elements | bold: **Build Profiles** > **Add Build Profile** | quotes |
| Weak phrases | start with a verb; cut "you can", "there is/are" | "There is a setting that you can use…" |
- Avoid: "simply", "just", "easy", "obviously", "please", "etc.", "and/or", Latin abbreviations
  (e.g., i.e. → "for example", "that is"), "master/slave" (→ primary/replica), "whitelist"
  (→ allowlist), "sanity check" (→ quick check).
- Contractions OK in conceptual/player text (Microsoft style); avoid in reference tables.

## Procedures (how-to steps)
1. One action per step; result after the action if useful: "Run `docfx build`. The site is
   written to `_site/`."
2. Put the location before the action: "In **Project Settings** > **Player**, set …".
3. Show expected output for verification steps; state what to do if it differs.
4. ≤ 9 steps per procedure; split longer tasks into sub-procedures.
5. Prerequisites as a list before step 1, not discovered mid-procedure.

## Terminology list (glossary.md format)
| Term | Use | Avoid | Definition | Notes |
|---|---|---|---|---|
| coins | soft currency in social casino | chips, credits, money | non-cashable virtual currency | never "win money" |
| player | person playing the game | user (in player docs), customer | - | "user" OK for admin panel docs |
| sign in | verb | log in, login (verb) | - | "sign-in" as noun/adjective |
| Unity 6.3 LTS | engine version | Unity 2025, U6 | - | use exact `6000.3.x` in setup docs |
- Pick one term per concept and never alternate for variety (translation memory and search
  depend on it). Add every new domain term in the same PR as the doc using it.
- Capitalize product/feature names only if they are proper names (team decision, in glossary).

## Writing for localization (docs, patch notes, UI-adjacent text)
- Short, complete sentences; subject-verb-object; no idioms, sports metaphors, slang, or puns.
- No string concatenation or sentence fragments assembled in code; full sentences with named
  placeholders: `"{playerName} won {amount} coins"`; ICU plurals for counts.
- Avoid ambiguous `-ing` forms and noun stacks ("player wallet balance sync retry policy"
  → "the retry policy for syncing the player's wallet balance").
- Keep "that" for clarity ("Make sure that the key exists"). Avoid humor and cultural references.
- Expansion: allow 30-40% longer text (German/French/Russian), more for short strings; CJK
  needs no spaces-based wrapping assumptions.
- Dates, numbers, currencies: never hard-code formats in text; say "in the player's locale".
- Provide context for translators: where the text appears, max length, what placeholders contain.

## Player-facing vs developer-facing tone
| Aspect | Player text | Developer text |
|---|---|---|
| Goal | excitement + clarity | precision + reproducibility |
| Vocabulary | game terms from glossary | API/config terms in code font |
| Numbers | rounded, with units the player sees | exact values, units, ranges |
| Length | 1 line per item | as needed, but scannable |

## Accessibility of docs
- Alt text for every meaningful image (what it shows and why); decorative images empty alt.
- Don't rely on color or position ("the red button on the right") alone; name the element.
- Tables with header rows; no images of text or code.
- Diagrams: provide a text summary below Mermaid diagrams.

## Linting setup (docs-as-code)
- Vale with `Google` or `Microsoft` style packages + project vocabulary
  (`.vale/styles/config/vocabularies/<Project>/accept.txt`).
- markdownlint (MD013 line length relaxed for tables), lychee/markdown-link-check for links.
- Run in CI on `**/*.md`; warnings allowed initially, errors for broken links.

## Self-review checklist
- [ ] Title states the outcome; first paragraph says who it is for and what they get.
- [ ] Every sentence earns its place; removed "simply/just/please".
- [ ] Terms match glossary; acronyms expanded on first use.
- [ ] Commands, paths, and names verified against the repo.
- [ ] Read aloud once: no ambiguous pronouns ("it", "this") across sentences.

## Sources
- Google developer documentation style guide, Highlights https://developers.google.com/style/highlights
- Google developer documentation style guide, Word list https://developers.google.com/style/word-list
- Microsoft Writing Style Guide, Top 10 tips https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice
- Microsoft Writing Style Guide, Global communications https://learn.microsoft.com/en-us/style-guide/global-communications/
- Vale linter https://vale.sh/
- ICU MessageFormat https://unicode-org.github.io/icu/userguide/format_parse/messages/
