# Designing for latency, fairness and trust (for designers, producers, engineers)

## What latency does to a mechanic
| Mechanic | Latency effect | Design mitigation |
|---|---|---|
| Own movement | feels sluggish without prediction | always predicted locally (engineering default) |
| Hitscan shooting | target moved since shooter saw it | lag compensation (server rewind) → "shot behind cover" for victims; cap rewind |
| Projectiles | spawn delay, desync on fast projectiles | predicted spawn on shooter's client; slower, larger projectiles; generous hitboxes |
| Melee / parry / block | windows < RTT are unfair | wind-up ≥ ~200 ms, parry windows ≥ 150 ms (tune); resolve on server with rewind |
| Physics interactions between players | two predictions collide, corrections jitter | reduce player-player physics; server-owned props; "soft" pushes |
| Grabs/throws, trades of items | both parties act simultaneously | server-confirmed with request→animation→result; never predicted |
| Economy actions (buy, craft, open chest) | must be correct, not instant | optimistic UI with spinner + server confirm; rollback UI on reject |
| Casino bet/spin/deal | money | server-confirmed always; animation starts on confirm (pre-roll anticipation anim hides 100–300 ms) |
| Simultaneous-turn / race-to-click | lower-ping player wins | server timestamps with tolerance, or turn-based resolution |

## Hiding latency (proven patterns)
- Anticipation: start a wind-up animation/sound locally the instant input happens; server result
  lands during the wind-up (Overwatch-style ability wind-ups; card-flip anticipation).
- Predict cosmetic, confirm consequential: muzzle flash/hit sparks immediately; damage numbers and
  kills from server.
- Show "pending" states for anything the server must confirm (purchases, matchmaking, seat taken).
- Input buffering: accept inputs slightly early (e.g. 100–150 ms) for combos/jumps.
- Larger, slower, telegraphed attacks are more latency-tolerant than instant ones.

## Fairness trade-offs to decide explicitly (ADR)
| Question | Option A | Option B |
|---|---|---|
| Who is favored on hits? | shooter (lag comp, "favor the shooter") | victim (no rewind, lead your shots) |
| Max rewind | e.g. 200–250 ms; high-ping players must lead shots | unlimited (high-ping abuse) |
| High-ping players | allowed with handicap | restricted by region/ping limit in ranked |
| Host advantage (listen/DA) | accept (casual co-op) | dedicated server (competitive) |
| Peeker's advantage | accept as genre norm | reduce with higher tick + lower buffering (Valorant: ~141 ms baseline cut to ~71 ms via 128 Hz, regional servers, high client FPS — Riot 2020) |

## Player count, update rate and scope
- Bandwidth and CPU grow with players × visible entities × update rate. Doubling player count is
  not "just more players": it can 4x replication cost (everyone sees everyone).
- Design levers that reduce cost: smaller visible sets (walls, fog, zones), fewer simultaneous
  physics objects, lower update rate for distant/irrelevant actors, cosmetic-only crowds (not networked).
- Large lobbies/social hubs: shard into instances (e.g. 50 per instance) rather than one huge room.

## Disconnects, reconnects, quitting
| Decision | Typical defaults (tune per genre) |
|---|---|
| Reconnect window | 60–180 s for session games; slot held, character AI/idle |
| Mid-match join / backfill | allowed in casual; disallowed in ranked |
| Leaver penalty | ranked: loss + cooldown escalation; casual: none or mild |
| Host migration (listen/DA) | needs explicit support; else match ends for all when host leaves |
| Casino table disconnect | bet already placed is resolved server-side; result shown on reconnect; auto-fold/auto-stand rules defined per game (regulatory) |
| Mobile app backgrounding | treat as disconnect after grace (iOS suspends sockets quickly); resume via reconnect |
- Every networked feature spec includes a "what happens if a player disconnects mid-action" line.

## Trust: which features need server authority
| Feature | If client is trusted, a cheater can… | Requirement |
|---|---|---|
| Currency, inventory, loot, progression | grant anything | backend authority, always |
| Match result / ranked rating | report wins | server reports results |
| Movement | teleport, speed hack | server validation of speed/position; reconciled prediction |
| Hit detection | auto-hit everything | server decides hits (rewind), client only requests |
| Visibility (fog, hands, hidden traps) | see everything (ESP) | don't send hidden data (interest management) |
| Timers/cooldowns | skip waits | server clock |
| RNG (crits, drops, cards, reels) | choose outcomes | server RNG; certified for real money |
Designers: list your feature's client-sent messages in the spec; security-engineer reviews them.

## Testing design under latency (before content production)
- Playtest the core loop with simulated 100 ms and 200 ms RTT, 1–3% packet loss, 20 ms jitter;
  include a mobile 4G profile. Engineering provides presets (MPPM / network simulator / clumsy).
- Acceptance: core actions still feel responsive at 100 ms; game remains fair/understandable at 200 ms.
- Track in playtests: "felt unfair" moments with timestamps → check for latency causes.

## Casino and turn-based specifics
- Server state machine per table/round (Betting → Dealing → Resolving → Payout); clients render state.
- Timeouts per decision step (e.g. 15–30 s) with default actions; shown as countdown synced to server time.
- All randomness and outcomes server-side before reveal; the client animation never decides.
- Late-joining spectators get a snapshot of the current state, then deltas.
- Real-money rules (RTP disclosure, game-cycle completion on disconnect, auditing) → `studio:domain-igaming`.

## Sources
- Gabriel Gambetta, "Fast-Paced Multiplayer" (parts I–IV) https://www.gabrielgambetta.com/client-server-game-architecture.html
- Valve Developer Community, "Source Multiplayer Networking" https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking
- Valve Developer Community, "Lag Compensation" https://developer.valvesoftware.com/wiki/Lag_Compensation
- Timothy Ford, "Overwatch Gameplay Architecture and Netcode" (GDC 2017) https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and
- Riot Games tech blog, "Peeking into VALORANT's Netcode" (2020) https://www.riotgames.com/en/news/peeking-valorants-netcode
- Unity docs: Netcode for GameObjects manual https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@latest/
