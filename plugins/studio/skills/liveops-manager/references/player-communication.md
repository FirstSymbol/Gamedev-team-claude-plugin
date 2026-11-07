# Player communication

## Channels
| Channel | Reaches | Best for | Notes |
|---|---|---|---|
| In-game inbox / mailbox | active players | rewards, compensation, announcements, personal messages | attach rewards with expiry (7-14 d); keep < 10 unread |
| News / popups / MOTD | active players at session start | event start, new features, offers | priority queue; caps below |
| Push (remote) | installed, opted-in, incl. lapsed | event start/end, reactivation, social triggers | opt-in gated (iOS; Android 13+) |
| Push (local) | installed, opted-in | timers: energy full, chest ready | cancel if no longer relevant |
| Email | players with account + consent | lapsed winback, account/security, receipts | consent + unsubscribe required |
| Store surfaces | browsers + installed | Apple In-App Events, Google Play promotional content | review rules: see `event-calendar.md` |
| Community (Discord, Reddit, X, TikTok, YouTube) | engaged fans, press | patch notes, roadmaps, incidents, feedback | community managed with marketing-manager |
| Status page / status account | all, during incidents | outage and incident updates | pinned, timestamped |

## Frequency caps (practitioner defaults - tune by A/B against opt-out and uninstall)
| Channel | Cap |
|---|---|
| Remote push, marketing/event | <= 1/day, <= 3-5/week for actives; lapsed: decaying schedule (D3, D7, D14, D30) then stop |
| Local push, transactional | <= 2/day; never duplicate a remote push on the same topic |
| Popups at session start | <= 2 per session; <= 1 offer popup per session; none during FTUE |
| Email marketing | <= 1-2/week; lapsed sequence max 4-5 then sunset the address |
| Inbox | no hard cap; group rewards; no spam-like daily offers |
- Quiet hours 22:00-08:00 player-local; some countries regulate night-time advertising push
  (e.g. South Korea requires separate consent for ad push 21:00-08:00 - verify current law).
- Monitor per send: open/tap rate, push-disable rate, uninstall within 24 h, unsubscribes.
  Stop a campaign whose disable/uninstall rate exceeds 2x baseline.

## Content rules
- Specific and true: what, when (with time zone or countdown), what the player gets; deep
  link to the exact screen; localized (narrative-designer owns copy, loc pipeline applies).
- No fake urgency, no "free" for paid items, prices shown honestly; no shaming copy.
- Apple App Review 4.5.4: push must not be required for the app to work, and must not be used
  for promotions or direct marketing unless the user explicitly opted in to receive them.
- Marketing email: GDPR/ePrivacy consent (EU/UK), CAN-SPAM (US: identification, physical
  address, working unsubscribe honored within 10 business days).
- Minors/unknown age: no spend-oriented push or email; compliance-advisor sets rules.
- Personalization in copy (name, progress) only from server-validated data.

## Event communication schedule (template)
| When | Channel | Audience | Message |
|---|---|---|---|
| T-3 d | news, community post, Apple In-App Event live | all eligible | teaser + date |
| T0 | push + popup | engaged eligible | event live, main reward, deep link |
| T+1 d | inbox | eligible non-joiners | reminder + small starter reward |
| T-24 h | push | participants with progress | ends soon, progress to next milestone |
| End +1 h | inbox | participants | results, rewards claimed/delivered |
| End +1-3 d | community | all | recap, winners, next event teaser |

## Patch notes and dev comms cadence
- Patch notes with every client release and every significant server-side balance change;
  same time in store "What's New", in-game news and community.
- Structure: headline features → events → balance changes (exact numbers, before → after) →
  fixes → known issues. Competitive games: preview balance changes 24-72 h ahead.
- Cadence: weekly community post (events this week), monthly dev update, quarterly roadmap;
  never promise dates you don't control (store review, licensor approval).
- Feedback loop: tag community/support feedback weekly; top 5 issues → product-manager with
  volumes, not anecdotes.

## Incident communication templates
- Acknowledge (<= 1 h SEV1): "We're aware that <symptom> since <time UTC>. We're working on it;
  next update by <time>. Your <progress/purchases> are safe / being checked."
- Update: what changed, what players should (not) do, next update time.
- Resolve: cause in plain words, what was fixed, compensation (what, who, how to claim,
  expiry), apology once - no blame on platforms or players.
- Never: speculate on cause, promise compensation before it's approved, delete criticism.

## Sources
- Apple App Review Guidelines (4.5.4 push notifications): https://developer.apple.com/app-store/review/guidelines/
- Android notification runtime permission: https://developer.android.com/develop/ui/views/notifications/notification-permission
- FTC CAN-SPAM Act compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Apple In-App Events: https://developer.apple.com/app-store/in-app-events/
- Pushwoosh push notification benchmarks: https://www.pushwoosh.com/blog/push-notification-benchmarks/
