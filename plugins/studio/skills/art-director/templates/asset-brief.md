# AB-<NNN> <Asset or family name>
Owner: art-director | Artist/vendor: <name> | Created: <YYYY-MM-DD> | Due: <YYYY-MM-DD> | Priority: <P0-P3>

## Purpose
- Gameplay/UI role: <what it must communicate: reward tier, danger, interactable...>
- Where seen: <screen/level, camera distance, on-screen size px/% on smallest device, background>

## Style
- Guide sections: <style-guide.md §...> | Pillars to hit: <...>
- References: <link/desc> → take: <...> / avoid: <...> (2-5 refs, inspiration only)
- Shape / palette / value: <dominant shape, hex swatches, value range>

## Technical spec (agreed with technical-artist)
- Type: <sprite/Spine/3D mesh/UI icon/VFX texture/SFX/music>
- Dimensions/density: <px, texel density, POT?> | Budget: <tris, bones, texture count, KB>
- Format: <PSD+PNG / FBX+PNG / .skel+atlas / WAV 48k/24> | Atlas: <ATL_...> | Pivot: <...>
- States/variants: <idle, win, blur, disabled, LODs, skins, loc variants>
- Animation: <frame rate, frames, loop points, duration>

## Deliverables
- Files: <exact names per naming.md> → folder: <path>
- Source files: <layered PSD/.blend/Spine project> | License/attribution notes: <...>
- AI use: <not allowed | rung N allowed per ai-assisted-art.md, log required>

## Rounds
| Round | Content | Due | Feedback by |
|---|---|---|---|
| R1 | <sketch/blockout> | <date> | <date> |
| R2 | <color/high-poly> | <date> | <date> |
| R3 | <final + in-engine check> | <date> | <date> |

## Acceptance criteria
- [ ] Reads at <size> on <device> and in grayscale; silhouette distinct from <list>
- [ ] Matches palette/value rules; light from <direction>
- [ ] Spec met: dimensions, budget, format, naming, pivot
- [ ] Verified in engine by technical-artist (import preset applied)
- [ ] License/provenance recorded

## Open questions
- <question> → <owner>
