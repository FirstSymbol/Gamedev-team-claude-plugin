# Event calendar planning

## Planning horizons
| Horizon | Artifact | Locked when | Content |
|---|---|---|---|
| Quarter | `calendar-<YYYY-Qn>.md` | 6-8 wk before quarter | seasons/passes, holiday beats, major updates, collabs |
| Month | month section | 4 wk before | event instances, offers, tournaments, featuring requests |
| Week | week rows | 1 wk before (configs on staging) | exact UTC start/end, segments, CR ids |
- Rolling: review weekly; never let the locked horizon drop below 4 weeks.

## Cadence beats (mobile casual/midcore baseline - adapt per genre)
| Beat | Example | Notes |
|---|---|---|
| Daily | login reward, daily quests, store rotation, hourly bonus (social casino) | reset at a fixed UTC hour; announce it in UI |
| Weekly Mon-Thu | points LTE or collection push; mid-week offer | weekly quests reset Monday |
| Weekend Fri-Sun | tournament / boost / weekend sale | weekend days carry ~16% of weekly playtime each vs 13-14% weekdays (GameAnalytics 2026) |
| Monthly / 28-35 d | season or battle pass; monthly sale | align pass end with next pass start; 1-3 d gap at most |
| 6-8 weeks | collection album season, league season | album end = big reward + reset |
| Quarterly | content update, new meta layer, major holiday mega-event | needs client release + store review buffer |
- Social casino: weekly new slot/machine release + themed event; daily bonus cadence is core
  retention (studio:domain-igaming for math/compliance).
- PC/console live service: seasons 8-12 weeks typical, mid-season update; Steam seasonal sales
  and platform events set extra beats (dates from Steamworks/platform partner portals).

## Overlap rules
- One headline competitive event (tournament/leaderboard/league finale) per audience at a time.
- Cap concurrent progression events per segment (e.g. 2-3 casual; midcore top games run > 20
  concurrent events (GameRefinery 2025) - don't copy without the UI and runway to support it).
- Shared point sources: if 2+ events reward the same action, cap the combined multiplier and
  include all in one injection budget.
- Pass + events: events feed pass XP deliberately; document the XP share.
- Monetization peaks (mega sale, gacha banner, chain offer) need a low-pressure breather beat
  between them; no back-to-back high-pressure weeks for the same segment.
- New client version week: no new event type on release day; gate with `minClientVersion` and
  start after ~70-80% of DAU have updated (measure adoption; verify per title).
- End times: fixed UTC hour that is daytime in the main market; never end during local night
  for the top geo; avoid ending exactly at daily reset.
- Holidays: support and on-call coverage planned before booking an event over a holiday.
- Store featuring windows (Apple In-App Events, Google Play promotional content) align with
  the beat they promote.

## Holiday and seasonal beats (verify exact dates yearly)
| Month | Global / Western | Regional | Notes |
|---|---|---|---|
| Jan | New Year | Lunar New Year (Jan/Feb; 2027-02-06) | LNY huge in CN/TW/SEA/KR |
| Feb | Valentine's | Ramadan starts ~early Feb 2027 (verify) | Ramadan: evening play peaks in MENA/ID/MY |
| Mar | St Patrick's, Easter 2027-03-28 | Eid al-Fitr ~Mar 2027 (verify) | spring season start |
| Apr-May | spring | JP Golden Week (late Apr-early May), KR Children's Day 05-05 | JP/KR high-spend windows |
| Jun-Aug | summer break | | longer sessions; casual peaks |
| Sep | back to school | Chuseok (KR, Sep/Oct) | dip in students' play |
| Oct | Halloween | Diwali (Oct/Nov, verify) | strong themed-event month |
| Nov | Black Friday / Cyber Monday (2026-11-27 / 11-30) | Singles' Day 11-11 | biggest sale beat in the West |
| Dec | Christmas, year-end | | advent calendars; high installs from new devices |
- Islamic and lunar holidays shift ~11 days earlier each Gregorian year (Islamic) or vary
  (lunisolar) - recompute every year.
- Sensitive dates: avoid celebratory events on national mourning days; localize themes
  (no Halloween push in markets where it is unpopular/culturally sensitive).

## Content pipeline lead times (practitioner defaults; replace with measured values)
| Item | Lead time before start | Breakdown |
|---|---|---|
| Reskin of existing event template | 2-4 wk | art 1-2 wk, config 2-3 d, loc 5-7 d, QA 3-5 d |
| New event mechanic (client + server) | 8-12 wk | design 2 wk, build 4-6 wk, QA 1-2 wk, geo test |
| Season / battle pass content | 6-10 wk | reward list → art → config → QA |
| IP collaboration | 3-9 months | licensing + licensor approvals dominate |
| Localization batch | 5-10 working days | + linguistic QA in build |
| Client-dependent event | + store review + adoption | ship client 2-3 wk ahead, dark-launched |
| Apple In-App Event | submit >= 2 wk ahead | promote up to 14 d before start; <= 31 d long; <= 10 published at once; name 30 / short 50 / long 120 chars; no prices in metadata |
| Google Play promotional content | draft ~30 d ahead for priority events (practitioner) | Google: featuring + promo content can give > 2x explore acquisitions (Google analysis 2023-24) |
| Apple featuring nomination | ideally ~3 months for major beats (verify current guidance) | via App Store Connect featuring nominations |
- Apple In-App Events are ineligible for repetitive daily tasks or pure price promotions.

## Event templates (goal → metric → threshold → guardrails)
| Template | Goal KPI | Success example (set per game) | Guardrails |
|---|---|---|---|
| Weekly points LTE | sessions/DAU, D7 of recent installs | participation >= 40% of eligible DAU; +x% sessions vs holdout | currency injection <= weekly budget |
| Weekend tournament | session length, payer conversion | +x% weekend playtime vs holdout | bracket fairness; cheat reports |
| Monthly pass | payer conversion, ARPDAU | premium pass conversion >= y% of MAU | completion feasible for non-whales; refund rate |
| Collection season | D30 retention, engagement | album completion curve on target | duplicate pain; last-card frustration |
| Holiday mega-event | revenue, reactivation | revenue vs prior-year beat + holdout | spend-velocity alerts; support load |
| Comeback campaign | reactivation of lapsed | reactivated % vs holdout; D7 of reactivated | abuse by deliberate lapsing |
- Store each template as a reusable event-engine config; new instance = data + art + copy.

## Calendar file format
```
| Week (Mon UTC) | Event id | Type | Segment | Start-End (UTC) | Goal KPI | Brief | CR | State |
|---|---|---|---|---|---|---|---|---|
| 2027-03-15 | spring_points_2027_03 | points LTE | level>=10, excl holdout | 03-20 10:00 - 03-23 10:00 | sessions/DAU | events/spring_points_2027_03.md | CR-041 | staged |
```
- Track "weeks of approved runway" and "concurrent events per segment" at the top of the file.

## Sources
- GameAnalytics Mobile & PC Benchmarks 2026 (weekday playtime split): https://gamedevreports.substack.com/p/gameanalytics-mobile-and-pc-game
- Apple In-App Events: https://developer.apple.com/app-store/in-app-events/
- Apple Getting featured: https://developer.apple.com/app-store/getting-featured/
- Google Play promotional content: https://play.google.com/console/about/programs/liveopsbeta/
- GameRefinery Live Events Tracker: https://gamerefinery.com/how-to-build-better-live-events-with-the-gamerefinery-live-events-tracker
- Sensor Tower LiveOps for the Holiday Season (2025): https://investgame.net/wp-content/uploads/2025/12/2025-12-16-LiveOpsfortheHolidaySeason.pdf
