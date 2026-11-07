# Engineering standards
Write the project's chosen rules into `.team/specs/architecture/standards.md` (≤ 1 page) and
enforce them with tooling. Existing project conventions win over this file.

## C# coding standards (Microsoft conventions)
| Element | Rule |
|---|---|
| Types, methods, properties, events, public fields, constants | PascalCase |
| Interfaces | `I` + PascalCase (`IWalletService`) |
| Parameters, locals | camelCase |
| Private/internal instance fields | `_camelCase`; static private `s_camelCase` (runtime style) — pick one and enforce |
| Async methods | `Async` suffix; return `Task`/`ValueTask`; accept `CancellationToken` last |
| Namespaces | file-scoped; match folder path; one public type per file |
| `var` | when the type is obvious from the right side |
| Nullability | `<Nullable>enable</Nullable>`; no `!` suppression without comment |
| Exceptions | no empty catch; catch specific types; use ProblemDetails at API edges |
| Collections | expose `IReadOnlyList<T>`/`IReadOnlyCollection<T>`; no public mutable lists |
- Unity scripts: Unity's C# style guide (e-book) is compatible; `[SerializeField] private` fields
  use camelCase (Inspector shows "Nice Name"); avoid `_` prefix on serialized fields if the team
  prefers clean Inspector labels — decide once in standards.md.

## .editorconfig + analyzers (enforced in build)
```ini
root = true
[*.cs]
indent_style = space
indent_size = 4
csharp_style_namespace_declarations = file_scoped:warning
csharp_style_var_when_type_is_apparent = true:suggestion
dotnet_style_qualification_for_field = false:warning
dotnet_naming_rule.private_fields_underscore.symbols = private_fields
dotnet_naming_rule.private_fields_underscore.style = underscore_camel
dotnet_naming_rule.private_fields_underscore.severity = warning
dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private
dotnet_naming_style.underscore_camel.required_prefix = _
dotnet_naming_style.underscore_camel.capitalization = camel_case
dotnet_diagnostic.CA2007.severity = none      # ConfigureAwait not needed in ASP.NET Core apps
dotnet_diagnostic.CA1848.severity = warning   # LoggerMessage / high-perf logging
```
```xml
<!-- Directory.Build.props (server) -->
<PropertyGroup>
  <Nullable>enable</Nullable>
  <AnalysisLevel>latest-recommended</AnalysisLevel>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  <TreatWarningsAsErrors Condition="'$(CI)' == 'true'">true</TreatWarningsAsErrors>
</PropertyGroup>
```
- Analyzer packs: built-in NetAnalyzers (CA rules) + IDE code-style rules; optional Roslynator,
  Meziantou.Analyzer, SonarAnalyzer.CSharp (pick ≤ 2 extra; tune noise in .editorconfig).
- Unity: `Microsoft.Unity.Analyzers` (UNT rules, suppresses wrong IDE suggestions for Unity
  messages); custom Roslyn analyzers as DLLs labeled `RoslynAnalyzer` in the Editor; Unity reads
  `.editorconfig` for diagnostic severities (verify: target Unity version docs).
- Format gate in CI: `dotnet format --verify-no-changes` for server solutions.
- Architecture tests (NetArchTest / ArchUnitNET) for module boundaries; asmdef references for Unity.

## Unity project conventions (link, don't repeat)
- Folder/asmdef layout, DI, patterns → `studio:unity-developer` (architecture-patterns).
- Meta/GUID, serialization, Force Text, never-commit folders, LFS → `studio:stack-unity`.
- Standards.md must state: Unity version (ProjectVersion.txt), render pipeline, DI container,
  async library (Awaitable vs UniTask), UI stack, Addressables policy, naming for assets
  (e.g., `T_` textures, `M_` materials, `PF_` prefabs — or none, but consistent), scene ownership.
- One owner per scene/prefab at a time (or prefab variants/nested prefabs) to avoid merge conflicts.

## Branching strategy
| Model | Use when | Rules |
|---|---|---|
| Trunk-based (default) | CI/CD services, small-medium teams, live games | branches < 1-2 days; feature flags for incomplete work; main always releasable; release branches cut from trunk for store builds, fixes cherry-picked from main |
| GitHub flow | web/admin apps, continuous deploy | PR to main, deploy on merge |
| GitFlow | multiple supported versions in parallel (SDKs, on-prem, console patches with long cert) | develop + release + hotfix branches; heavier merges; avoid otherwise |
- Games: trunk + `release/<version>` per submission; tag every build sent to a store; console
  cert builds frozen on release branch; hotfixes land on main first.
- Large binary art: Git LFS with file locking for unmergeable assets, or Unity Version Control /
  Perforce for art-heavy teams (see `studio:stack-unity` version control).
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`…) enable changelog automation;
  libraries/contracts use SemVer (breaking = major).
- Protected main: PR required, CI green, ≥ 1 approval (2 for wallet/auth/payments), no force-push.

## Code review policy
- Standard (Google): approve when the change improves overall code health, even if not perfect;
  don't block on personal preference; style is the linter's job.
- Size: aim < 400 changed lines; review effectiveness drops beyond 200-400 LOC per session
  (SmartBear/Cisco study); split refactors from behavior changes.
- Speed: first response within 1 working day; agent reviews (code-reviewer) immediately after impl.
- Checklist focus order: correctness → security/data → design/boundaries → tests → readability → perf.
- Comment labels: `blocking:`, `suggestion:`, `nit:`, `question:` (Conventional Comments).
- Required reviewers via CODEOWNERS: wallet/ledger, auth, payments, RNG → 2 reviewers incl.
  security-engineer; public contracts → system-analyst/tech-lead; shaders → technical-artist.
- Author duties: self-review, description (why, how tested, risk, screenshots/video for UI),
  link to story/ADR.

## Tech debt management
- Classify (Fowler quadrant): deliberate/inadvertent × prudent/reckless. Prudent-deliberate debt
  needs an ADR or debt ticket with payback trigger at creation time.
- Register `.team/specs/architecture/tech-debt.md`: ID | description | location | interest
  (cost per sprint: slowdowns, incidents, bugs) | principal (effort) | risk | owner | trigger | state.
- Prioritize by interest/principal ratio and cost of delay; high-interest items first.
- Capacity: reserve 10-20% per sprint (agree with producer/product-manager); boy-scout rule for small fixes.
- Signals: change failure rate, rework rate, cycle time in a module, hotspot analysis
  (churn × complexity), recurring incidents, onboarding time.
- Big rewrites → strangler fig: route a slice to the new implementation, migrate, delete old.

## Dependency policy
- .NET: Central Package Management (`Directory.Packages.props`), lock files
  (`RestorePackagesWithLockFile` + `--locked-mode` in CI), NuGet Audit warnings as errors for
  high/critical, Dependabot or Renovate weekly with grouped minor updates.
- Unity: pin UPM package versions in `Packages/manifest.json`; scoped registries (OpenUPM) listed
  in standards.md; Asset Store packages vendored in a dedicated folder with license noted.
- New dependency gate (record in PR or ADR if significant): license (allow MIT/Apache-2.0/BSD/
  MS-PL; review LGPL/MPL; reject GPL/AGPL for distributed clients; commercial needs budget and
  compliance OK), last release < 12 months, maintainers > 1, security history, size/IL2CPP/AOT
  support, transitive deps. See stack-dotnet for current commercial-license changes.
- Wrap vendor SDKs (ads, analytics, attribution, payments) behind interfaces; one adapter per vendor.
- Upgrade cadence: .NET LTS within 6 months of GA; Unity LTS minor updates monthly on a branch with
  smoke tests; major engine upgrades only via ADR + spike.

## Engineering health metrics (DORA)
- Throughput: deployment frequency, change lead time, failed deployment recovery time.
- Instability: change fail rate, deployment rework rate (added 2024).
- Track per service/client; use trends, never individual performance targets.

## Sources
- Microsoft, "C# coding conventions" https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions
- Microsoft, "Identifier names" https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names
- Microsoft, "Code analysis overview" and configuration files https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview
- Microsoft, "Central Package Management" https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management
- Trunk Based Development https://trunkbaseddevelopment.com/
- Google Engineering Practices, "Code Review" https://google.github.io/eng-practices/review/
- Conventional Commits 1.0.0 https://www.conventionalcommits.org/en/v1.0.0/
- Microsoft Azure Architecture Center, "Strangler Fig pattern" https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig
- DORA metrics guide https://dora.dev/guides/dora-metrics/
