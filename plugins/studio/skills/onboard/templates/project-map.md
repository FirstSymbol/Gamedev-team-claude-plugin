# Project map (cache - read before exploring code)
Commit: <sha>  Date: <YYYY-MM-DD>  Owner: tech-lead-architect
Rule: facts with paths only; `(inferred)` where not verified; no secrets; ≤ 150 lines.

## Purpose & stage
<one line: what it is, for whom> | Stage: <prototype / vertical slice / alpha / live>

## Stack & versions
| Layer | Tech + version | Evidence |
|---|---|---|
| Client | <Unity 6000.x, URP, Input System> | ProjectSettings/ProjectVersion.txt |
| Server | <.NET 10, ASP.NET Core, EF Core 10, DB> | global.json, *.csproj |
| Web/admin | <React+TS / none> | package.json |
| CI/infra | <GitHub Actions / Docker / ...> | .github/workflows/ |

## Layout (where things live)
| Path | Purpose |
|---|---|
| <Assets/_Project/Runtime/Core> | <core domain, no UnityEngine refs> |

## Modules & dependencies
- <assembly/project> → <depends on> (<asmdef/csproj path>)

## Entry points
- <boot scene, Program.cs, routes/endpoint groups, workers, CLI tools>

## Key domain types
| Concept | Type | Path |
|---|---|---|
| <Wallet> | <Wallet class> | <path> |

## Conventions (follow these)
- <architecture pattern, DI, async style, naming, error handling, logging>
- Tests: <framework, location, naming, how fixtures are built>

## Commands
| Task | Command | Notes |
|---|---|---|
| Build | <dotnet build Casino.sln> | |
| Test | <dotnet test / Unity -runTests ...> | <needs Docker? editor?> |
| Run | <dotnet run --project ...> | |

## Config & environments
- <appsettings layering, env vars names, feature flags, remote config> (names only, never values)

## Integrations
- <payments, stores, analytics, ads, auth, backend services> → <where wired>

## Hotspots & fragile areas
- <most-changed files (git log), known debt, areas without tests> → risks.md IDs

## Where to look for...
| Question | Look at |
|---|---|
| <how a new endpoint is added> | <sibling feature path> |
