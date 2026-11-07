# <Project name>
<One sentence: what it does and for whom.>

Status: <active | maintenance | deprecated> | Owner: <team/role> | Last verified: <YYYY-MM-DD>

## What it does
- <capability 1>
- <capability 2>
- Not in scope: <explicit non-goals>

## Quickstart
Prerequisites:
- <.NET SDK x.y (see global.json) | Unity 6000.x>
- <Docker x / tools>

<!-- .NET service -->
```bash
git clone <repo-url>
cd <repo>
docker compose up -d          # <dependencies: db, cache>
dotnet run --project src/<Project.Api>
curl http://localhost:<port>/health   # expected: Healthy
```
<!-- Unity package: Window > Package Manager > + > Add package from git URL -->
```
<https://host/org/repo.git?path=/Packages/com.org.package#v1.0.0>
```

## Configuration
| Key | Env var | Default | Required | Description |
|---|---|---|---|---|
| `<Section:Key>` | `<Section__Key>` | `<value>` | <yes/no> | <what it controls> |

## Usage
<1-3 most common tasks with a code sample each.>

## Development
| Task | Command |
|---|---|
| Build | `<dotnet build>` |
| Test | `<dotnet test>` / `<Unity -batchmode -runTests -testPlatform EditMode ...>` |
| Lint/format | `<dotnet format --verify-no-changes>` |
Project layout: `<src/…, tests/…, Runtime/, Editor/, Tests/>`

## Operations
- Runbooks: <docs/runbooks/...> | Dashboards: <name/link> | Alerts: <names>
- API reference: <OpenAPI URL /openapi/v1.json or docs site>

## Links
- Changelog: [CHANGELOG.md](CHANGELOG.md) | Architecture: <docs/architecture.md> | ADRs: <path>
- Contributing: <CONTRIBUTING.md> | License: <LICENSE.md>
