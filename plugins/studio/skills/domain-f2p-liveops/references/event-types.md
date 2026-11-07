# Live event & feature types (catalog)

Use: pick the type by the KPI you need to move, then copy its levers into the event brief
(liveops-manager `templates/event-brief.md`). Numbers are practitioner defaults - tune per game.

## Choose by goal
| KPI to move | Best-fit types |
|---|---|
| D1-D7 retention / habit | login calendar, streaks, daily/weekly quests, beginner pass |
| Session frequency | timed chests, energy refills, hourly bonus (social casino), streaks |
| Session length / depth | points (milestone) events, collections, tournaments |
| Payer conversion | starter pack, first-purchase bonus, piggy bank, pass premium track |
| ARPPU / repeat spend | chain/endless offers, tiered sales, gacha banners, high-tier pass |
| Reactivation | comeback rewards, returning-player pass, catch-up mechanics |
| Social / virality | team/clan events, co-op goals, gifting, partner events |

## Catalog
| Type | Mechanic | Duration | Key levers | Pitfalls |
|---|---|---|---|---|
| Login calendar | reward per login day (7/28-day) | rolling | day-7/28 jackpot, missed-day handling | pure entitlement, no gameplay; no inflation control |
| Streak | consecutive-day counter, escalating rewards | open-ended | streak freeze/repair (sink or IAP), milestone days | losing a long streak churns players - offer repair |
| Daily/weekly quests | task list → points → chest | 24 h / 7 d | task mix (play/spend/social), reroll | tasks forcing spend or ads feel coercive |
| Points / milestone LTE | earn points from core play → milestone track | 2-7 d | point sources, milestone curve, grand prize | curve tuned to whales only → most quit at 20% |
| Tournament / leaderboard | ranked score vs bracket | 1-7 d | bracket size (often 30-100), matchmaking by skill/spend, tiered prizes | unmatched brackets → payers crush everyone; bots/cheats |
| League / ladder | promote/relegate weekly | weekly | tier count, promote %, demotion protection | top tiers stagnate - reset seasonally |
| Season / battle pass | free + premium tracks of rewards via XP | ~28-60 d | price point, track length, premium-track value ratio, catch-up XP, pass skip tiers | unfinishable pass → refunds/anger; FOMO overload |
| Mini-pass / event pass | small pass bound to one event | 3-14 d | cheaper price, event-specific rewards | pass fatigue when stacked with main pass |
| Collections / albums | collect sets (cards/stickers) from play/chests | 4-8 wk season | rarity distribution, duplicates → currency/trading, set rewards | last card too rare = frustration; trading needs anti-abuse |
| Piggy bank | premium currency accrues while playing; pay to unlock | until full / timed | fill rate, cap, price, "full" reminder | must show exact contents and price; no deceptive "lost" claims |
| Offers: starter pack | one-time high-value pack | 24-72 h after trigger | trigger (level N, first loss), value ratio | showing in first session before value is understood |
| Offers: personalized | segment-targeted price/contents | 24-72 h | price anchor per segment, cooldown | perceived unfairness if players compare; regulator scrutiny |
| Offers: chain / endless | sequence: free → paid → free steps | event-long | free-step ratio, step pricing ladder | high spend pressure - cap visibility for spend-limited players |
| Gacha banner | limited pool with featured item | 1-3 wk | rates (disclosed), pity/spark, rate-up | undisclosed odds = store/legal violation; see compliance-advisor |
| Team / clan event | group goal or team vs team | 2-7 d | team size, contribution caps, MVP rewards | inactive teammates; free-riders - kick/merge tools |
| Partner / co-op event | pair with friend/random partner to fill goal | 2-5 d | partner matching, gifting | drop-off if partner inactive - auto-rematch |
| Mini-game / side mode | separate mechanic, own currency | 3-10 d | entry cost, reward table | dev cost high; reuse via event engine |
| Comeback / returning player | rewards + catch-up after N days absent | 7-14 d | absence threshold (e.g. 14-30 d), catch-up boosts | gaming by deliberate absence - cap frequency |
| Weekend boost / happy hour | 2x drops/XP | hours-days | multiplier, scope | economy inflation; schedule clashes |
| IP collab | licensed characters/cosmetics | 2-4 wk | exclusive items, pass, store | licensing lead time 3-9 months; approvals |
| Social casino specific | hourly/daily bonus, level-up bonus, jackpot/"high roller" rooms, slot tournaments, quests on spins | various | bonus size vs coin sink, room bet ranges | wagering semantics → studio:domain-igaming + compliance-advisor |

## Design rules
- Every event states: goal KPI, target segment, entry condition, economy sources/sinks added,
  expected currency injection, success threshold, holdout plan.
- Reward value budget: estimate currency/items injected per participant per segment; compare
  to weekly sink capacity (economy-monetization-designer signs off).
- Completion targets: define % of participants expected to hit each milestone (e.g. 60-70%
  reach first meaningful reward, 10-20% grand prize for non-payers - tune per game).
- Overlap: at most one "headline" competitive event at a time; stacking passes and milestone
  events must share point sources consciously (see `studio:liveops-manager` (event-calendar)).
- Fairness: matchmake tournaments by skill/progression; separate brackets for new players.
- Transparency: odds disclosed for randomized rewards (Apple App Review 3.1.1, Google Play
  policy); show exact price and contents on every offer; no fake countdowns.
- Server-authoritative progress and rewards (see `live-service-architecture.md`).
- Minors: avoid personalized spend pressure and chain offers for under-18 / unknown-age users;
  follow UK Age Appropriate Design Code / COPPA as applicable (compliance-advisor).

## Reusable event engine (data model sketch)
```json
{
  "eventId": "spring_points_2027_03",
  "type": "points_milestone",
  "startUtc": "2027-03-20T10:00:00Z", "endUtc": "2027-03-23T10:00:00Z",
  "minClientVersion": "1.42.0",
  "audience": { "segment": "level_gte_10", "excludeHoldout": true },
  "pointSources": [{ "action": "match_win", "points": 10 }, { "action": "booster_used", "points": 2 }],
  "milestones": [{ "points": 100, "reward": "chest_small" }, { "points": 2500, "reward": "skin_spring" }],
  "assets": { "addressablesLabel": "event_spring_2027" },
  "configVersion": 17
}
```
- Engine supports types as plugins; new event = new data + art, not new code.

## Sources
- GameRefinery - building better live events (event tracker): https://gamerefinery.com/how-to-build-better-live-events-with-the-gamerefinery-live-events-tracker
- Games Alchemy - evolution of battle pass / event pass systems: https://gamesalchemy.substack.com/p/29-the-evolution-of-battle-pass-event
- Apple App Review Guidelines (3.1.1 loot box odds): https://developer.apple.com/app-store/review/guidelines/
- Apple In-App Events (event badges, limits): https://developer.apple.com/app-store/in-app-events/
- Google Play promotional content (LiveOps): https://play.google.com/console/about/programs/liveopsbeta/
