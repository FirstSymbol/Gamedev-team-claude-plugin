# Audio direction

## Audio style guide (sections)
1. **Pillars**: 3 adjectives tied to game pillars (e.g. "Bright, tactile, celebratory").
2. **Palette**: instrumentation/genre for music; material vocabulary for SFX (wood, coin, glass,
   synth); what is forbidden (e.g. no realistic gunfire in a cozy game).
3. **Feedback language**: UI sound family (one synth/foley family), positive vs negative
   contours (rising = gain, falling = loss/cancel), loudness hierarchy.
4. **Music**: themes per area/mode, emotional arc, adaptive rules, loop lengths, stingers.
5. **Voice**: casting notes, tone, processing (radio, creature), VO vs barks vs walla.
6. **Mix**: bus structure, priority/ducking rules, loudness targets, platform variants.
7. **Tech**: formats, sample rates, voice limits, middleware, naming (`SFX_`, `MUS_`, `VO_`).
8. **References**: tracks/games described with what to take (tempo, timbre, density).

## SFX list per feature (template columns)
`ID | Event (code hook) | Description | Variations | Loop? | Priority | Bus | Length | Notes`
- One row per game/UI event that needs sound; event names match code/analytics hooks
  (`ui_button_tap`, `reel_stop_1`). Variations: 3-5 for frequent sounds to avoid repetition.
- Every UI state with visual feedback gets an audio decision (sound or explicit "silent").
- Mark sounds that carry gameplay info → they need a visual/caption equivalent (accessibility).

### Slot / casino SFX baseline
| Event | Direction |
|---|---|
| Spin start | short, punchy, same every time (habituation fine) |
| Reel loop | low-intensity texture under 1-2 s spin; ends with stops |
| Reel stop 1..5 | short thud/click, slight pitch rise per reel |
| Anticipation (e.g. 2 scatters landed) | rising tension on remaining reels; only on genuine outcomes |
| Line win small | short chime proportional to value |
| Rollup | loop with pitch/intensity steps per tier; ends on value lock |
| Big/Mega/Epic win | tier stings + music swell; skippable with visuals |
| Bonus trigger / free spins | distinct motif reused across feature |
| UI tap / error / insufficient funds | soft, non-punishing |
- UKGC RTS 14F: no celebratory audio for returns ≤ stake (real-money); default to same in
  social casino. Sound must never be the only win indicator (many mobile players play muted).

## Adaptive music techniques
| Technique | How | Use |
|---|---|---|
| Horizontal re-sequencing | switch segments at bar/beat transition points | area/mode changes, combat states |
| Vertical layering (stems) | fade stems in/out by parameter (intensity 0-1) | tension, progress, streaks |
| Stingers | short one-shots synced to beat over music | wins, level-up, discovery |
| Transitions | dedicated bridge segments / tails | avoid hard cuts |
- Define parameters: `intensity`, `state` (menu/explore/combat/bonus), `streak`. Document in
  the style guide with values that trigger each change.
- Loops: musical loop points on bar lines; deliver with tails; 1.5-3 min menu loops to delay fatigue
  (heuristic). Slots: base-game loop short and unobtrusive; bonus music distinct.

## Mixing and loudness
| Target | Value | Source |
|---|---|---|
| Console/PC integrated loudness | -24 LUFS (±2 LU) | Sony recommendation (as reported by Audiokinetic, 2024); original ASWG-R001 (2013): -23 LUFS |
| Mobile/portable integrated | -18 LUFS (±2 LU); some guides -16 | Sony / IESD reference levels (verify current docs) |
| True peak max | -1 dBTP | same |
| Loudness range (LRA) | ≤ 20 LU console (narrower on mobile) | same |
- Measure ITU-R BS.1770 integrated loudness over ≥ 30 min of representative gameplay
  (not menus alone). Tools: Wwise Loudness Meter, FMOD Loudness Meter, Youlean, iZotope Insight.
- Dialogue is the anchor; music ducks ~6-10 dB under VO (sidechain/duck), SFX priority by
  gameplay importance.
- Bus tree: Master → Music, SFX (UI, Gameplay, Ambience), VO, (Cinematics). Player sliders map
  to Music/SFX/VO/UI (GAG basic: separate volume controls).
- Phone speakers reproduce little low bass (roughly below ~300 Hz, device-dependent; verify):
  give important low sounds mid/high harmonics; check mono fold-down.
- Check on: phone speaker, earbuds, TV speakers, studio monitors.

## Middleware choice
| Option | Pros | Cons | Fit |
|---|---|---|---|
| Unity Audio (AudioMixer, snapshots, Audio Random Container 2023.2+) | built-in, no license, simple | limited adaptive music authoring, fewer profiling tools | casual mobile, slots, small teams |
| FMOD Studio | timeline + parameters, designer-friendly, Unity integration package, live update | license tiers (indie free/cheap under budget limits; verify fmod.com/licensing) | most mid-size games, adaptive music |
| Wwise | deepest feature set (RTPC, states, interactive music, spatial audio), profiler | steeper learning; license by budget (free under ~USD 250K budget; verify audiokinetic.com) | large/console projects, complex audio |
Decide early (ADR with tech-lead-architect); switching late is expensive.

## Unity Audio import defaults (starting points, confirm with technical-artist)
| Clip type | Load Type | Compression | Notes |
|---|---|---|---|
| Short frequent SFX (< ~1 s) | Decompress On Load | ADPCM | low CPU, small |
| Medium SFX | Compressed In Memory | Vorbis q ~50-70 | balance memory/CPU |
| Music / long ambience | Streaming | Vorbis | one stream per track; limit concurrent streams |
| VO | Compressed In Memory or Streaming | Vorbis | per-language Addressables groups |
- Force To Mono for non-spatial mobile SFX; sample-rate override (e.g. 22-32 kHz) where
  inaudible; masters stay 48 kHz/24-bit WAV.
- Voice limits: set real voice count per platform; prioritize via AudioSource priority.

## Voice-over and localization
- Script sheet: `LineID | Character | Context | Line | Direction | Max duration | Loc notes`;
  LineID = loc key = file name (`VO_<Char>_<LineID>_<lang>.wav`).
- Recording spec: 48 kHz/24-bit, dry, consistent mic distance; deliver edited, breaths
  attenuated, peaks ≤ -1 dBTP, loudness-normalized per spec.
- Localized VO: time-constrained lines (±10% of source for lip-sync/cutscenes) vs wild lines;
  FIGS + JA/KO/ZH typical sets; subtitles always available (accessibility).
- Union/talent contracts and AI voice clauses (SAG-AFTRA interactive agreement, 2025) → route to
  compliance-advisor; never clone a voice without explicit written consent.

## Audio review checklist
- [ ] Every event in SFX list implemented and audible in context.
- [ ] Integrated loudness and true peak within platform target.
- [ ] No info carried by sound alone; captions/visuals exist.
- [ ] No repetition fatigue in 10-min session (variations, randomization).
- [ ] Mute/volume settings persist; app respects device silent mode on mobile (verify platform behavior).
- [ ] Licenses on file for every library sound and music track.

## Sources
- Audiokinetic, "Mastering a Game with Wwise, Part 1" https://audiokinetic.com/en/mastering-a-game-with-wwise-part1
- Designing Sound, "Video games and loudness standards: interview with Sony's Garry Taylor" (2012) https://designingsound.org/2012/07/30/video-games-and-loudness-standards-interview-with-sonys-garry-taylor/
- IESD Mix Reference Levels v03.02 (Audio Gang) https://www.audiogang.org/wp-content/uploads/2015/04/IESD-Mix-Ref-Levels-v03.02.pdf
- ITU-R BS.1770 loudness measurement https://www.itu.int/rec/R-REC-BS.1770
- FMOD licensing https://www.fmod.com/licensing
- Audiokinetic, "Free Wwise Indie License" https://www.audiokinetic.com/en/blog/free-wwise-indie-license
- Unity Manual, Audio Clip import settings https://docs.unity3d.com/Manual/class-AudioClip.html
