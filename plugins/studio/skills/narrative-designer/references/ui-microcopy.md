# UI text, onboarding, microcopy

## Principles
- Clarity over cleverness; voice from the tone bible, but never at the cost of comprehension.
- One term per concept (glossary): if it's "Gems" on the store, it's "Gems" everywhere.
- Front-load the key word; digits for numbers ("3 lives", "+250 coins"); avoid double negatives.
- Buttons: verb-first, say the outcome ("Collect", "Play level 12", "Spend 50 Gems") — not
  "OK"/"Yes". Cancel = the safe action, clearly labelled ("Keep playing").
- Case style fixed per tone bible (e.g. sentence case for body, Title Case for screen titles).
- Write for the 2nd language reader: short sentences, no idioms/puns in functional text
  (puns allowed in flavour text with a loc note explaining them).

## Length heuristics (EN source; plan for expansion — see localization-ready-writing.md)
| Element | Target | Notes |
|---|---|---|
| Button | 1–3 words | leave ≥ 40% spare width for translations |
| Screen title | ≤ 3–4 words | |
| Tooltip / tip | ≤ 2 short lines | one idea |
| Tutorial prompt | ≤ ~12 words, one instruction | action verb + target: "Swipe to match 3 gems" |
| Toast / feedback | ≤ 6 words | "Level up!", "Saved" |
| Push notification | title few words; body ≤ ~1–2 lines | truncation differs per OS/device (verify) |
| Dialogue bubble (mobile) | ≤ 2–3 lines per tap | split long speeches |
| Store: app name / subtitle / short desc | App Store 30 / 30; Google Play title 30, short desc 80 chars | marketing-manager owns (verify current limits) |
- Ask ux-ui-designer for the real limit per element (px width × font); record it as
  `maxLength` in the string table.

## Onboarding / tutorial text
- Teach by doing: gesture/hand animation + highlight first, text second, text optional.
- One instruction per prompt; prompt appears when needed (just-in-time), disappears on success.
- Don't narrate the obvious ("This is your inventory"); explain the why only when it affects decisions.
- Reinforce later with contextual tips after N failures or T seconds idle (hint ladder:
  subtle → explicit → show).
- Returning players: skippable; recap screen after long absence ("Previously…").
- Instrument: each tutorial string ID maps to an FTUE step event (lead-game-designer funnel).

## Feedback, errors, empty states
- Error = what happened + what to do: "Can't connect. Check your internet and tap Retry."
  No blame, no codes in the main text (code in small print for support).
- Fail screens: say why and how to improve ("Out of moves — clear the ice first next time"),
  then the retry action. Offers on fail screens → economy-monetization-designer; keep honest.
- Empty states: explain what goes here and how to fill it ("No friends yet. Invite friends
  to send lives.").
- Confirmation for destructive or paid actions: name the cost and the result; irreversible
  actions say so ("You can't undo this").

## Rewards, progression, notifications
- Specific and brief: "+250 Coins", "New area unlocked: Harbor". Celebrate with VFX/SFX more
  than with adjectives.
- Push notifications: value-first and specific ("Your harbor shipment arrived: 3 crates
  ready"), never guilt or fake urgency ("Your friends are leaving you!"). Promotional pushes
  need user opt-in on iOS (App Store Review Guideline 4.5.4, verify current wording);
  frequency/caps → liveops-manager.

## Ethics & compliance in copy
- No fake scarcity/urgency, confirm-shaming ("No thanks, I like losing"), or hidden costs.
- Paid random items: state odds/contents per platform rules → compliance-advisor.
- Social casino: make clear virtual coins have no cash value and can't be cashed out; never
  phrase as real-money gambling (`domain-igaming` skill, compliance-advisor).
- Age-sensitive audiences: plainer language, no pressure to purchase or share data.

## Accessibility
- Plain language; avoid relying on colour words alone ("tap the red button") — add
  shape/label. Support dynamic text size where UI allows.
- Subtitles: speaker names, ≤ 2 lines on screen, adjustable size/background, include
  important sound cues (Game Accessibility Guidelines; Xbox Accessibility Guidelines).

## Microcopy spec format (per screen, CSV or table)
| String ID | Screen/element | Text (EN) | Max chars | Context for translators | Variants/states |
|---|---|---|---|---|---|
| `shop.offer.button.buy` | Shop > offer card > CTA | Buy for {price} | 16 | price is localized store string | disabled: `shop.offer.button.owned` |

## Review checklist
- [ ] Every string from the UX flow has an ID, max length, context.
- [ ] Glossary terms consistent; tone bible voice applied.
- [ ] Buttons describe outcomes; destructive/paid actions confirmed with cost.
- [ ] Errors say what to do; fail screens explain why.
- [ ] No manipulative patterns; compliance-sensitive copy flagged.
- [ ] Tested in-game at longest pseudo-localised length.

## Sources
- Hodent, "The Gamer's Brain" (CRC Press, 2017) — onboarding and cognitive load
- Game Accessibility Guidelines https://gameaccessibilityguidelines.com/
- Microsoft, Xbox Accessibility Guidelines https://learn.microsoft.com/en-us/gaming/accessibility/guidelines
- Apple, App Store Review Guidelines (4.5.4 push notifications) https://developer.apple.com/app-store/review/guidelines/
- Nielsen Norman Group, "Error-Message Guidelines" https://www.nngroup.com/articles/error-message-guidelines/
- Podmajersky, "Strategic Writing for UX" (O'Reilly, 2019)
