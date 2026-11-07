# RNG and game certification

## Standards map
| Standard | Scope | Use |
|---|---|---|
| GLI-11 v3.0 (2016) | land-based gaming devices (EGMs) | cabinet/slot hardware+software, RNG, payout rules |
| GLI-19 v3.0 (2020-07-17) | interactive gaming systems (online) | platform, RNG, games, accounts, logs, security |
| GLI-16 / GLI-33 etc. | cashless / event wagering | as required by market (verify) |
| UKGC RTS | remote gambling GB | RNG + game design + security; test house approval |
| National tech specs | MGA, Ontario, NJ, SE, DE, ES, IT | often reference or mirror GLI-19 |
- Accredited/approved test labs (check each regulator's list): GLI, BMM Testlabs, iTech Labs,
  eCOGRA, Gaming Associates, Trisigma, SIQ (verify current approvals per market).

## RNG requirements (GLI-19 v3.0 chapter 3, condensed)
- Lab reviews source of all randomness, scaling, shuffling and mapping code (§3.2.1).
- Statistical tests on final outcome output at 99% confidence collectively: chi-square/total
  distribution, overlaps, coupon collector, runs, interplay correlation, serial correlation,
  duplicates (§3.2.2).
- Distribution: each selection equally likely or matching the intended non-uniform design;
  scaling/mapping unbiased — discarding values (rejection sampling) is allowed to remove bias (§3.2.3).
- Independence: no information about future draws from past draws; no discarding based on
  previous selections unless the design says so (e.g. without replacement) (§3.2.4).
- Period large enough that all outcomes are available on every draw (§3.2.5).
- Cryptographically strong for outcome determination: resistant to direct cryptanalytic,
  known-input (not seeded from time alone; no shared initial seeds) and state-compromise attacks
  (periodic reseed from external entropy) (§3.3.1-3.3.2).
- Hardware RNGs: dynamic output monitoring (§3.3.3).
- Client: no logic used to generate any game result; all critical functions on the platform
  (§2.6.5(g)).

## Implementation pattern (.NET server)
```csharp
public interface IGameRng { int NextInt(int maxExclusive); }          // one service, injectable
public sealed class CryptoGameRng : IGameRng {
    // OS CSPRNG; GetInt32 uses rejection sampling, so no modulo bias.
    public int NextInt(int maxExclusive) => RandomNumberGenerator.GetInt32(maxExclusive);
}
public static class Reels {
    // Weighted virtual reel: cumulative weights, one draw per reel, uniform over total weight.
    public static int PickStop(IGameRng rng, ReadOnlySpan<int> cumWeights) {
        int r = rng.NextInt(cumWeights[^1]);
        int i = 0; while (cumWeights[i] <= r) i++; return i;            // or binary search
    }
}
```
- Draw count per game cycle is fixed by design; log every draw (value, purpose) with the round.
- Never: `System.Random`/`UnityEngine.Random` for outcomes, `% n` on raw bytes, seeding from
  `DateTime.Now`, client-side rolls, re-rolling an outcome to hit a target RTP/jackpot.
- QA "forced outcome"/cheat tools: only behind a build flag absent from certified builds; labs
  and code reviewers check for it (code-reviewer, security-engineer).
- Deterministic test RNG (seeded) implements `IGameRng` for unit tests and simulations only.

## Game requirements commonly tested (GLI-19 chapter 4; national variations apply)
- Theoretical RTP ≥ 75% for every wagering configuration unless the regulator sets otherwise;
  external progressives/incentives excluded (§4.7.1).
- Chance events constant probability for a paid game unless artwork says otherwise.
- Game rules and paytable available in-game; values in currency; malfunction voids pays/plays.
- Game cycle = wager to wager; complete when wagered funds lost or final award credited (§4.3.3).
- Game recall: last play info (time, bet, outcome display, balance, wins incl. jackpots, player
  choices, feature phases) and at least the last 50 events of bonus/feature games (§4.14).
- Game disable: players may finish the current game; jackpot disable rules (§4.15).
- Interrupted games: wagers held, mechanism to complete, resolve before another instance of the
  same game (§4.16); procedures for games that cannot be completed (appendix A.6.4).
- Records (§2.8): system-clock timestamps, exportable data; per-game play info mirrors recall fields;
  complaint records 5 years, some system/chat logs 90 days, or as the regulator specifies.

## Certification workflow
1. Design math → PAR sheet per RTP variant (economy-monetization-designer, templates/par-sheet.md).
2. Implement evaluator once (server C#), share with simulation tool; unit + statistical tests.
3. Internal pre-cert: exact RTP vs simulation (≥ 10^8-10^9 spins), RTP per bet config, max win
   cap, interrupted-game and recall tests, jurisdiction profile checks (qa-engineer).
4. Submission package: source code (game + RNG integration), build artifacts with hashes
   (SHA-256), PAR sheets, game rules/help screens per language, RNG certificate reference,
   jurisdiction config, test accounts/environment access, change log.
5. Lab tests: source review, math verification, RNG statistics, functional/UX rules per
   market (e.g. UK RTS 14), security where in scope → report + certificate per jurisdiction.
6. Regulator approval/registration where required (some markets accept lab certificate only).
7. Release: deploy exactly the certified hashes; automated hash verification at startup or via
   regulator tooling; record cert IDs in the release notes (release-platform-manager).
8. Live: monitor actual vs theoretical RTP per game (alert on statistically significant deviation,
   e.g. outside 99% CI given volume); investigate before regulators do.

## Change control
| Change | Typical impact |
|---|---|
| Math (strips, paytable, feature odds), RNG, evaluator, outcome mapping | full re-certification |
| Game rules text, paytable display, RTP display | re-test of affected items |
| Art/sound only, no logic | lab notification or minor review (market-dependent; verify) |
| Platform/wallet changes affecting rounds or balances | platform re-test |
- Keep a certified-component manifest: component → version → hash → certificate IDs → markets.

## Social casino note
- Not legally required, but keep RMG-grade RNG and math discipline: fairness complaints, app-store
  reviews and a future RMG port all depend on it; publish RTP/odds where platform rules require.

## Sources
- GLI-19 Standards for Interactive Gaming Systems v3.0 (2020) https://gaminglabs.com/wp-content/uploads/2024/06/GLI-19-Interactive-Gaming-Systems-v3.0.pdf
- GLI press release on GLI-19 v3.0 https://gaminglabs.com/press-releases/gaming-laboratories-international-gli-releases-revised-standard-gli-19-standards-for-interactive-gaming-systems-v3-0
- UKGC Remote gambling and software technical standards https://www.gamblingcommission.gov.uk/standards/remote-gambling-and-software-technical-standards
- .NET `RandomNumberGenerator.GetInt32` https://learn.microsoft.com/dotnet/api/system.security.cryptography.randomnumbergenerator.getint32
- Hannum & Cabot, "Practical Casino Math", 2nd ed. (2005)
