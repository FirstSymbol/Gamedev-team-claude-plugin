# API documentation

## Principles
- Examples first: minimal working request/code before parameter tables.
- Reference is generated from the source of truth (code/OpenAPI); prose adds intent, constraints,
  errors, and examples. Never hand-maintain a parallel copy of signatures.
- Every operation documents: purpose, auth, inputs (type, required, constraints, example),
  outputs, errors (status + problem type + cause + fix), idempotency, rate limits, versioning.

## OpenAPI-driven docs (ASP.NET Core)
- .NET 9+: built-in `Microsoft.AspNetCore.OpenApi` (`builder.Services.AddOpenApi()`,
  `app.MapOpenApi()` → `/openapi/v1.json`); .NET 10 emits OpenAPI 3.1 by default (pin 3.0 via
  `OpenApiVersion` option if tooling needs it). UI is separate: Scalar (`MapScalarApiReference()`)
  or Swagger UI. Swashbuckle no longer in templates since .NET 9.
- XML comments flow into OpenAPI (.NET 10) via a compile-time source generator when
  `<GenerateDocumentationFile>true</GenerateDocumentationFile>` is set; supported tags:
  `summary`, `remarks`, `param`, `returns`, `response`, `example`, `deprecated`, `inheritdoc`.
- `<response code="404">` only adds a description; the status must already exist in metadata
  (`TypedResults`/`Results<Ok<T>, NotFound>`, `.Produces<T>()`, `[ProducesResponseType]`).
- `AddOpenApi(documentName)` with a non-literal name disables XML support (source generator limit).
- Minimal API metadata: `.WithName()`, `.WithSummary()`, `.WithDescription()`, `.WithTags()`.
- Build-time document: `Microsoft.Extensions.ApiDescription.Server` writes the spec on build →
  commit or publish it as an artifact; diff in CI.
- Lint/diff: Spectral or Redocly CLI (style rules: every operation has summary, operationId,
  4xx/5xx responses, examples); oasdiff for breaking-change detection in PRs.
- Errors: RFC 9457 Problem Details (`type`, `title`, `status`, `detail`, `instance`); document
  each `type` URI on an errors reference page.

```csharp
/// <summary>Spins the daily bonus wheel for the current player.</summary>
/// <remarks>One spin per UTC day. Idempotent per <c>Idempotency-Key</c> header.</remarks>
/// <param name="request">Client context for the spin.</param>
/// <returns>The granted reward and next available spin time.</returns>
/// <response code="200">Reward granted.</response>
/// <response code="409">Already spun today; see <c>nextSpinAt</c>.</response>
public static async Task<Results<Ok<SpinResult>, Conflict<ProblemDetails>>> Spin(
    SpinRequest request, IBonusService bonus, CancellationToken ct) { /* ... */ }
```

## C# XML doc comments (`///`)
| Tag | Rule |
|---|---|
| `<summary>` | one sentence, third person, starts with verb: "Gets…", "Creates…", "Returns…"; properties "Gets or sets…" |
| `<param name>` | what it is + constraints/units ("Bet in coins; must be > 0.") |
| `<returns>` | what and when null/empty |
| `<exception cref>` | each thrown exception + condition |
| `<remarks>` | threading, performance, side effects, Unity main-thread requirement |
| `<example>` + `<code>` | short usage |
| `<see cref>` / `<seealso>` | link types/members; `<see langword="null"/>` |
| `<inheritdoc/>` | overrides/interface impls instead of copy-paste |
- Enable `<GenerateDocumentationFile>true</GenerateDocumentationFile>`; CS1591 (missing XML
  comment) as warning for public API projects; suppress per-project for tests/internal apps.
- Document public/protected surface of libraries and packages; skip trivial privates.
- Unity: XML comments work in Unity C# (IDE tooltips); for package docs feed them to DocFX.

## DocFX (static API + conceptual site for .NET)
- .NET Foundation project, community-maintained; v2.78.x current line (2025-2026; verify latest
  on NuGet). Install: `dotnet tool install -g docfx`.
- `docfx init` → `docfx.json`; `docfx metadata` generates YAML from projects/assemblies;
  `docfx build` renders; `docfx docfx.json --serve` previews locally.
- Structure: `docs/` (conceptual Markdown, `toc.yml`), `api/` (generated), `index.md`.
- Cross-reference: `<xref:Namespace.Type.Member>` in Markdown; `@Namespace.Type` shorthand.
- Publish to GitHub Pages/Azure Static Web Apps from CI; build fails on broken xrefs
  (`--warningsAsErrors`).
- REST APIs: prefer rendering OpenAPI with Scalar/Redoc rather than DocFX's REST support (verify
  DocFX OpenAPI 3.x support before relying on it).

## Unity package documentation
- Package layout (Unity Manual): `package.json`, `README.md`, `CHANGELOG.md`, `LICENSE.md`,
  `Third Party Notices.md`, `Editor/`, `Runtime/`, `Tests/Editor|Runtime/`, `Samples~/`,
  `Documentation~/` (tilde hides from Project window; Create Package makes them without tilde).
- `Documentation~/`: `index.md` or `<package-name>.md` (overview, install, requirements,
  quickstart), feature pages, `TableOfContents.md` if multi-page (verify current convention).
- `package.json` doc fields: `displayName`, `description`, `documentationUrl`, `changelogUrl`,
  `licensesUrl`, `unity` (min version, e.g. `"6000.3"`), `samples` array (`displayName`,
  `description`, `path: "Samples~/<Name>"`).
- CHANGELOG.md in Keep a Changelog format (Unity recommends a standard format).
- Each sample: README with what it shows, required render pipeline/input system, and steps.
- Manual page skeleton: Overview → Installation → Requirements (Unity version, RP, platforms)
  → Quickstart → Concepts → How-tos → API reference link → Known limitations.

## Writing reference pages (examples-first pattern)
````markdown
## Spin bonus wheel
`POST /v1/bonus/wheel/spin` - grants one daily reward.

```http
POST /v1/bonus/wheel/spin
Authorization: Bearer <token>
Idempotency-Key: 6f1c...

200 OK
{ "reward": { "type": "coins", "amount": 7500 }, "nextSpinAt": "2026-11-08T00:00:00Z" }
```
| Field | Type | Required | Description |
|---|---|---|---|
| `Idempotency-Key` (header) | string (UUID) | yes | Retries with the same key return the first result. |

Errors: `409 bonus-already-claimed` - wait until `nextSpinAt`.
````

## Review checklist
- [ ] Generated reference builds without warnings; no "TODO" summaries on public API.
- [ ] Every endpoint has a runnable example and documented error cases.
- [ ] Auth, pagination, rate limits, idempotency, versioning/deprecation documented once and linked.
- [ ] Breaking changes detected by oasdiff are in CHANGELOG with migration.
- [ ] Samples compile against current version (copied from tests where possible).

## Sources
- Microsoft Learn, OpenAPI XML documentation comment support in ASP.NET Core (2026) https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/openapi-comments
- Microsoft Learn, Recommended XML tags for C# documentation comments https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/recommended-tags
- DocFX https://dotnet.github.io/docfx/
- NuGet, docfx package https://www.nuget.org/packages/docfx
- Unity Manual, Package layout https://docs.unity.com/en-us/engine/current/manual/packages-list/cus-pkg-lp/cus-pkg-development/cus-pkg-structure/cus-layout
- RFC 9457 Problem Details for HTTP APIs https://www.rfc-editor.org/rfc/rfc9457
- Scalar, "OpenAPI with ASP.NET Core in .NET 9 and 10" (2026-10) https://scalar.com/blog/posts/2026-10-06-openapi-aspnet-core-dotnet-9-10
