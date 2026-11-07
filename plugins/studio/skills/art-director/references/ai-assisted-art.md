# AI-assisted art and audio (responsible use)

Not legal advice. Any ship decision involving AI output → compliance-advisor; mark
"needs human legal review" where law/platform terms are unclear.

## Risk ladder (pick the lowest rung that solves the problem)
| Rung | Use | Risk | Default policy |
|---|---|---|---|
| 1 | mood boards, ideation thumbnails (internal only) | low | allowed with approved tools |
| 2 | concept exploration → human repaints final | low-med | allowed; log prompts |
| 3 | texture/material bases, upscaling, cleanup of own art | med | allowed; human edit + log |
| 4 | in-game final assets largely AI-generated | high | needs AD + legal approval, disclosure |
| 5 | live generation at runtime (images/text/voice) | highest | needs ADR, guardrails, platform review |
| - | logo, key characters, brand identity | IP-critical | human-authored only |

## Prompt structure for concept exploration
```
[subject + action] , [composition/camera: shot, angle, focal length] ,
[style descriptors from OUR style guide: shape language, rendering, edge, detail density] ,
[palette + lighting mood: key light, temperature, value key] ,
[medium: painterly / cel-shaded / clay render] , [output: aspect ratio, background] ,
negative: [what to avoid: text, watermarks, extra limbs, photoreal skin]
```
- Describe style in craft terms; never use living artists' names, studio names, or franchise
  titles in prompts. Use only our own art as image/style references.
- Generate wide (many thumbnails, low detail), select, then iterate narrow. Keep seeds.
- Prompt library: `.team/specs/art/prompts.md` with versioned prompts that produced approved
  directions, linked to style-guide sections.

## Style consistency techniques
- Fixed seeds + fixed style block; reference-image conditioning from approved in-house art.
- Custom fine-tunes/LoRA only on data you own or licensed for training; record dataset source.
- Post-process into the project palette (gradient map/palette lock) and paint over edges,
  silhouettes, hands, text, and UI-critical details by hand.
- Character consistency: human-made turnaround sheet is the canonical source; AI only for
  variations, then reviewed against the sheet.

## Licensing, ownership, platform policy (verify before ship)
| Topic | Current position | Action |
|---|---|---|
| Tool terms | commercial use, output ownership, indemnity differ per tool and tier | record tool, plan, ToS version/date per asset |
| Training data | some vendors claim licensed-only training and offer IP indemnity (enterprise tiers) | prefer such tools for rungs 3-4 (verify current terms) |
| US copyright | USCO Part 2 report (2025-01-29): prompts alone insufficient for authorship; human selection/arrangement/modification can be protected | keep human-authored layers; document edits |
| EU AI Act Art. 50 | transparency duties apply from 2026-08-02 (machine-readable marking by providers; deepfake disclosure by deployers; grace to 2026-12-02 for marking on systems placed earlier, reported) | live-gen features and realistic depictions → legal review |
| Steam | Content Survey: disclose pre-generated AI content (ships in game) and live-generated (runtime); live-gen needs described guardrails; players can report via overlay; dev-efficiency tools not the focus (form updated ~2026-01, verify) | fill survey truthfully; keep provenance log as evidence |
| Mobile stores | gen-AI apps need user reporting/flagging of offensive output (Google Play AI-Generated Content policy; verify Apple guidelines) | only relevant for live generation |
| Voice | cloning real voices requires explicit consent; union agreements (SAG-AFTRA interactive) regulate AI replicas | written consent + contract clause |
| Music | AI music services have faced label litigation and licensing deals (2024-2025; verify current status) | avoid shipped AI music unless license explicitly covers games |
- Content credentials: consider C2PA metadata on marketing images; strip nothing that tools
  embed for provenance.

## What NOT to ship
- Anything resembling existing IP: characters, logos, trademarks, trade dress, signature styles.
- Real people's likeness or voice without written consent (incl. celebrities in slots themes).
- Unreviewed AI text in images (gibberish glyphs), anatomy/perspective errors, inconsistent
  lighting vs style guide.
- Store screenshots/trailers misrepresenting the game (store policy) - must be real captures.
- Assets from tools whose terms forbid commercial use or claim output rights.
- Content generated from confidential or third-party material uploaded to cloud tools without
  permission (NDA/data leak).

## Human review gate (all rungs ≥ 3)
- [ ] Logged in `ai-usage-log.md`: asset ID, tool + version, plan/ToS date, prompt(s), seed,
      input references (owned?), human edits description, reviewer, date.
- [ ] Reverse image search / similarity check on finals; no recognizable IP.
- [ ] Paint-over done on silhouettes, faces, hands, text, UI-critical areas.
- [ ] Matches style guide (critique passes 1-3 in visual-direction.md).
- [ ] Disclosure impact recorded (Steam survey, store text, credits) → compliance-advisor.
- [ ] Technical spec met (naming, size, format) like any other asset.

## ai-usage-log.md row
`AssetID | Rung | Tool/version | Plan & ToS date | Prompt ref | Seed | Inputs (owned?) | Human edits | Reviewer | Disclosure needed? | Date`

## Sources
- Steam Content Survey (Steamworks docs) https://partner.steamgames.com/doc/gettingstarted/contentsurvey
- PC Gamer, "Steam updates AI disclosure form..." https://www.pcgamer.com/software/ai/steam-updates-ai-disclosure-form-to-specify-that-its-focused-on-ai-generated-content-that-is-consumed-by-players-not-efficiency-tools-used-behind-the-scenes/
- U.S. Copyright Office, Copyright and Artificial Intelligence (Part 2: Copyrightability, 2025) https://www.copyright.gov/ai/
- Copyright Alliance, summary of USCO Part 2 https://copyrightalliance.org/ai-report-part-2-copyrightability/
- Cooley, "EU AI Act: Transparency Obligations Take Effect 2 August 2026" https://www.cooley.com/news/insight/2026/2026-08-03-eu-ai-act-transparency-obligations-take-effect-2-august-2026
- C2PA (Coalition for Content Provenance and Authenticity) https://c2pa.org/
