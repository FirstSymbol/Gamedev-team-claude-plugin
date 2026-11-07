# Localization-ready writing

## String IDs
- Format: `<area>.<screen|feature>.<element>[.<state|variant>]`, lowercase, dot-separated:
  `shop.offer.button.buy`, `quest.q_main_03.obj1`, `tutorial.match3.swipe_hint`.
- Semantic, not derived from English text (`btn_ok` → breaks when text changes). Never reuse
  an ID for a different meaning; meaning change → new ID, old one retired.
- Dialogue: tool-generated line IDs (Yarn `#line:`, ink `#id:` tags, articy technical names).

## String table columns (CSV/Sheets → Unity Localization or custom)
`id, source_en, context, speaker, max_length, placeholders, plural(y/n), gender(y/n),
screenshot, status(draft|final|locked), notes_for_translators`
- Context answers: where it appears, who speaks to whom, what the placeholders contain,
  tone, whether it's a verb or noun ("Play" button vs "a play").
- Do-not-translate list: brand/product names, some character names (decide per locale).

## Text expansion (IBM figures via W3C; English → European languages)
| EN source length (chars) | Translated length vs source |
|---|---|
| ≤ 10 | 200–300% |
| 11–20 | 180–200% |
| 21–30 | 160–180% |
| 31–50 | 140–160% |
| 51–70 | 151–170% |
| > 70 | ~130% |
- Short labels are the danger zone; German/Finnish/Russian often run longest among common
  targets. Budget: UI elements fit +30–40% on long text and ~2× on very short labels, or use
  auto-size/wrap with min font size (agree with ux-ui-designer).
- CJK: fewer characters but taller glyphs and more line spacing; Thai/Arabic/Devanagari
  need extra vertical space. Thai has no spaces between words (line-breaking rules).

## Never concatenate
- Bad: `"You found " + count + " " + itemName + "!"` — word order, plural and case differ.
- Good: one full string with named placeholders: `You found {count} {itemName}!` →
  better: avoid inserting nouns into sentences in inflected languages:
  `Found: {itemName} ×{count}`.
- Placeholders: named (`{playerName}`), never positional-only in source; document type and
  example values; translators may reorder them.
- Don't build sentences from fragments in UI layout (label + value split across widgets
  that must read as one sentence).

## Plurals (CLDR categories)
| Language | Categories used |
|---|---|
| English, German, Spanish, Italian | one, other |
| French | one (0 and 1), many (large numbers, verify), other |
| Russian, Ukrainian | one, few, many, other (21 → one; 5, 11–14 → many) |
| Polish | one, few, many, other |
| Arabic | zero, one, two, few, many, other |
| Japanese, Chinese, Korean, Thai | other only |
- Always write the `other` form; translators add forms their language needs. Check per-locale
  rules in the CLDR Language Plural Rules table.

## Gender & grammatical agreement
- Player gender/pronouns: ask once (or offer form of address), store as a variable; many
  languages inflect verbs/adjectives by the speaker's or addressee's gender (Russian past
  tense, French/Spanish adjectives, Arabic 2nd person).
- Prefer neutral source phrasing where natural; otherwise use select variants.
- Inserted nouns may need grammatical case/gender (Slavic, German) → avoid insertion, or keep
  per-noun variants (article/case forms) in the item table.

## ICU MessageFormat vs Unity Smart Strings
| | ICU MessageFormat | Unity Localization Smart Strings (SmartFormat-based) |
|---|---|---|
| Plural | `{count, plural, one {# life left} other {# lives left}}` | `{count:plural:{} life left\|{} lives left}` — forms in the locale's CLDR order (verify order per locale) |
| Gender/select | `{gender, select, female {She} male {He} other {They}} joined.` | `{gender:choose(female\|male):She\|He\|They} joined.` (verify syntax for installed version) |
| Where | web/backend, many TMS tools, .NET/JS libs | Unity Localization package (String Tables, Smart toggle per entry) |
- Pick one syntax per pipeline; if strings are shared with backend/web, standardise on ICU
  and convert for Unity, or keep server texts separate. Note the choice in an ADR with
  unity-developer. Smart Strings are SmartFormat syntax, not ICU — they don't interoperate.
- Mark entries that use Smart formatting (the "Smart" flag) — unmarked entries print braces literally.

## Unity Localization package notes
- String Tables (per locale) + Asset Tables (localized sprites/audio); `LocalizedString`
  references in UI; CSV and Google Sheets import/export extensions; XLIFF export (verify
  per version). Pseudo-Locale for testing expansion and missing strings.
- Fonts: TextMeshPro font asset per script with fallback chains; dynamic atlases for CJK;
  Arabic/Hebrew need RTL + shaping support — verify TMP/UI Toolkit support on the project's
  Unity version (technical-artist/unity-developer).

## Formatting & culture
- Numbers, dates, times, currencies: format via locale APIs (`CultureInfo`), never in text.
  Store prices come localised from the store SDK — don't hard-code currency symbols.
- Avoid culture-bound idioms, gestures, holidays in functional text; flag culturally
  sensitive content (religion, symbols, maps/borders) for review per market.
- Legal/regulatory strings (odds, age, privacy, gambling disclaimers) are per region →
  compliance-advisor owns the source.

## Loc kit (handoff to translators)
- String tables with context + max lengths, glossary (term, definition, DNT flag, per-locale
  approved translation), tone bible excerpt, character sheet (age, voice, how they address
  others), screenshots per screen, placeholder list, plural/gender notes, schedule & freeze.
- Process: string freeze per milestone → export → translation → import → LQA in build
  (qa-engineer) → fixes. Late changes after freeze go through a change list with IDs.

## Pseudo-localization checklist (request before first loc pass)
- [ ] Expansion (+30–50%) and accented characters render in every screen.
- [ ] No hard-coded strings (untranslated text = bug).
- [ ] No truncation/overlap at longest strings; wrap/auto-size works.
- [ ] Placeholders and plural forms resolve correctly; RTL mirror check if RTL planned.

## Sources
- W3C Internationalization, "Text size in translation" (IBM expansion table) https://www.w3.org/International/articles/article-text-size/index.en
- Unicode CLDR, Plural Rules https://cldr.unicode.org/index/cldr-spec/plural-rules
- Unity Localization 1.4 manual, Smart Strings https://docs.unity3d.com/Packages/com.unity.localization@1.4/manual/Smart/SmartStrings.html
- Unity Localization 1.4 manual, Plural Formatter https://docs.unity3d.com/Packages/com.unity.localization@1.4/manual/Smart/Plural-Formatter.html
- Unicode ICU User Guide, Formatting Messages https://unicode-org.github.io/icu/userguide/format_parse/messages/
- Yarn Spinner docs, Line Provider https://docs.yarnspinner.dev/components/line-provider
