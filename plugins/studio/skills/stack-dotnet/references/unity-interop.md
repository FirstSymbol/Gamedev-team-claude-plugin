# Sharing code and contracts between .NET backend and Unity

## Unity runtime facts (2026-11)
| Unity | Scripting runtime | API surface | C# | Notes |
|---|---|---|---|---|
| 2022.3 LTS / Unity 6.0–6.6 | Mono (Editor, JIT) + IL2CPP (AOT players) | .NET Standard 2.1 (+ .NET Framework profile) | 9 | no `System.Text.Json` built in |
| 6.7 LTS | last Mono-based; experimental CoreCLR desktop player | .NET Standard 2.1 | 9 | experimental builds not for production |
| 7.0 (alpha since 2026-10-05, 7000.0.0a7; no release date) | CoreCLR, Mono removed | .NET 10 (experimental builds: .NET Std 2.1) | 14 (experimental: 9) | upgrade guide "Path to CoreCLR" |
- Plan for netstandard2.1 + C# 9 until the project actually moves to Unity 7.
- IL2CPP = AOT: no `System.Reflection.Emit`, no runtime codegen; managed stripping removes "unused"
  types used only via reflection → `link.xml` / `[Preserve]`. Generic virtual methods over value types may need hints.
- C# 9 in Unity: `record`/`init` need a polyfill `namespace System.Runtime.CompilerServices { internal static class IsExternalInit {} }`.
  Not available: file-scoped types and later features (C# 10+), `required`, generic math, `field`, extensions blocks.
- `BinaryFormatter`: removed in .NET 9 and being removed by Unity; never use for saves or network.

## Shared library layout
```
shared/Game.Contracts/Game.Contracts.csproj    DTOs, enums, error codes, message keys, pure rules
  <TargetFrameworks>netstandard2.1;net10.0</TargetFrameworks>
  <LangVersion>9.0</LangVersion>               keep Unity-compatible syntax
  <Nullable>enable</Nullable>                  annotations only; Unity side may ignore
```
- Contents: request/response DTOs, enums, error code constants, validation of pure rules
  (e.g. reward schedule math) — NO EF Core, ASP.NET Core, logging frameworks, `HttpClient` wiring.
- Server-only logic (RNG outcome, wallet mutation, payouts) never goes in the shared lib: the client must not be able to compute or forge it.
- Multi-target lets the server use the net10.0 build; `#if NETSTANDARD2_1` only for polyfills.
- Delivery to Unity (pick one, document in ADR):
| Method | Pros | Cons |
|---|---|---|
| UPM local package (`package.json` + `.asmdef`, source files) referenced via `file:` or git URL | source visible, debuggable, asmdef-managed | needs Unity-safe syntax in every file |
| Prebuilt DLL in `Assets/Plugins/` (CI builds netstandard2.1) | simple, compiler-version independent | binary drift; update discipline; `.meta` per DLL |
| NuGetForUnity package from private feed | versioned, dependency resolution | extra tool; watch transitive deps |
- Dependencies in shared libs must also exist for Unity (netstandard2.0/2.1, IL2CPP-safe). Check before adding.
- CI: build the shared lib for both TFMs and compile a minimal Unity test project (or run Unity batch mode) on contract changes.

## Serialization compatibility
| Format | Server | Unity | Use when | Watch |
|---|---|---|---|---|
| JSON STJ ↔ Newtonsoft | `System.Text.Json` (ASP.NET Core default) | `com.unity.nuget.newtonsoft-json` | REST, config, debugging | naming, enums, dates, polymorphism (below) |
| JSON ↔ `JsonUtility` | STJ | built-in | tiny flat DTOs only | no dictionaries, properties, polymorphism, nullable; fields only |
| MessagePack (MessagePack-CSharp v3) | `MessagePack` | NuGetForUnity `MessagePack` + `MessagePack.Unity` git package; Unity ≥ 2022.3.12f1 | compact binary REST/SignalR/MagicOnion | source generator required for IL2CPP; `[Key(n)]` never reused |
| MemoryPack | `MemoryPack` | NuGetForUnity + `MemoryPack.Unity`; Unity ≥ 2022.3.12f1 | C#-only, max speed (saves, internal RPC) | default mode: no member deletion/reorder; use `VersionTolerant` + `[MemoryPackOrder]` for network contracts; avoid `DateTimeOffset`/`ValueTuple` across .NET↔Unity |
| Protobuf | `Grpc.AspNetCore` / `Google.Protobuf` | `Google.Protobuf` + `Grpc.Net.Client` | gRPC, cross-language | field numbers forever |

### JSON parity rules (STJ server ↔ Newtonsoft client)
- Naming: ASP.NET Core web defaults = camelCase + case-insensitive reads. Configure Newtonsoft with
  `CamelCasePropertyNamesContractResolver` or annotate both sides (`[JsonPropertyName]` + `[JsonProperty]`).
- Enums: serialize as strings on both sides (`JsonStringEnumConverter` / `StringEnumConverter`); unknown
  enum values from newer servers must not crash old clients → add an `Unknown = 0` member and a tolerant converter.
- Dates: UTC ISO 8601 (`DateTimeOffset` or `DateTime` Kind Utc); Newtonsoft `DateParseHandling` can turn
  date-like strings into `DateTime` — set `DateParseHandling.None` when strings must stay strings.
- Numbers: money as `long` minor units or string-encoded decimal; JS/admin clients lose precision > 2^53.
- Polymorphism: STJ `[JsonPolymorphic]` + `[JsonDerivedType(typeof(X), "x")]` (`$type` discriminator).
  Never Newtonsoft `TypeNameHandling.All/Auto` on untrusted input (remote code execution class of bugs).
- Missing/extra members: both ignore unknown by default — keep it (forward compatibility); `required` validation on server only.
- Contract test: snapshot (Verify) the JSON of every DTO on the server, deserialize the same fixtures in a Unity EditMode test.

## Calling the backend from Unity
| Transport | Platforms | Notes |
|---|---|---|
| `UnityWebRequest` | all incl. WebGL | main thread; wrap in `Awaitable`/UniTask; set `timeout`; dispose; certificate handler for pinning |
| `System.Net.Http.HttpClient` | not WebGL | works on Mono/IL2CPP; reuse one instance; mobile proxies/certs differ from UnityWebRequest |
| gRPC: `Grpc.Net.Client` + Cysharp YetAnotherHttpHandler | desktop/mobile, not WebGL/consoles | C-core gRPC for Unity discontinued; MagicOnion builds C#-interface RPC on top |
| gRPC-Web | WebGL | server `UseGrpcWeb()`; unary + server streaming only |
| SignalR .NET client (`Microsoft.AspNetCore.SignalR.Client`) | not WebGL | IL2CPP strips it: preserve assemblies in `link.xml`; test Android + iOS builds early |
| SignalR JS client via `.jslib` bridge | WebGL | marshal JSON strings only |
- Always: timeouts, retry with backoff + jitter on idempotent calls only, `Idempotency-Key` on purchases/claims,
  `X-Client-Version` + platform headers, server-driven `minSupportedVersion` gate.
- Auth tokens on device: platform secure storage (Keychain/Keystore plugins), not `PlayerPrefs` plain text.
- Clock: client time is untrusted; server returns `serverTime` for countdowns (daily bonus timers).

## Versioning shared contracts
- SemVer the contracts package; server supports every client version still allowed to connect (N, N-1, …).
- Allowed without version bump: add optional field, add endpoint, add enum value (clients tolerate unknown).
- Breaking (new API version + ADR): remove/rename field, change type/unit, reuse MessagePack key/proto
  number, change semantics of an existing field, make optional input required.
- Deprecation path: mark `[Obsolete]` in contracts → stop writing in new clients → remove after the
  oldest supported client no longer reads it (track via client version metrics).
- Keep an `errors` catalog (stable codes) in the contracts lib so Unity maps codes to localized UI text.

## Sources
- Unity Manual: .NET profile support https://docs.unity3d.com/Manual/dotnet-profile-support.html
- Unity Manual: Managed code stripping https://docs.unity3d.com/Manual/ManagedCodeStripping.html
- Unity forum: CoreCLR, Scripting, and Serialization Update (June 2026) https://discussions.unity.com/t/coreclr-scripting-and-serialization-update-june-2026/1723299
- Unity Manual: CoreCLR scripting back end (6000.7) https://docs.unity.com/en-us/engine/6000.7/manual/programming-environment/scripting-backends/coreclr.md
- MessagePack-CSharp https://github.com/MessagePack-CSharp/MessagePack-CSharp
- MemoryPack https://github.com/Cysharp/MemoryPack
- YetAnotherHttpHandler https://github.com/Cysharp/YetAnotherHttpHandler
- SignalR client IL2CPP issue https://github.com/dotnet/aspnetcore/issues/12102
