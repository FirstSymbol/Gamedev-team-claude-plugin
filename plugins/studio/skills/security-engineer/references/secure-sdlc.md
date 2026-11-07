# Secure SDLC: CI gates, pen-tests, triage (practitioner reference)

## Gate matrix (security-engineer defines, devops-sre-engineer wires)
| Gate | Tool options | When | Blocks merge on |
|---|---|---|---|
| Secret scanning | gitleaks (pre-commit + CI), GitHub Secret Protection push protection, TruffleHog | every push/PR | any verified secret |
| SAST | CodeQL (C#, JS/TS), Semgrep (C#, YAML/Docker rules), Roslyn analyzers, SonarAnalyzer.CSharp | every PR | new High/Critical (baseline existing) |
| SCA (deps) | NuGet audit, `dotnet list package --vulnerable --include-transitive`, Dependabot/Renovate, OSV-Scanner | every PR + daily | Critical/High with fix available |
| Container/IaC | Trivy / Grype (images), Checkov / tfsec(Trivy) / kubeconform (IaC, Helm) | image build, IaC PR | Critical with fix; misconfig High |
| DAST | OWASP ZAP baseline (passive) on stage per deploy; API scan with OpenAPI nightly; full scan weekly | post-deploy stage | High alerts not triaged |
| SBOM + provenance | CycloneDX / Syft, `actions/attest-build-provenance` | release | missing SBOM |
| License | ORT, `dotnet-project-licenses`, FOSSA/Snyk | release | copyleft in shipped client (legal → compliance-advisor) |
Rule: new findings block; legacy findings go to a dated baseline with owners. A gate nobody
triages is turned off by the team within a month — set an owner per gate.

## Roslyn analyzers (cheapest SAST, runs in every build)
```xml
<!-- Directory.Build.props -->
<PropertyGroup>
  <AnalysisLevel>latest-recommended</AnalysisLevel>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
</PropertyGroup>
```
- Security-relevant rules to keep as errors: CA2100 (SQL injection review), CA3001–CA3012
  (taint: SQL, XSS, path, command, LDAP, regex), CA5350/CA5351 (weak crypto), CA5359/CA5386
  (cert validation / TLS protocol hard-coding), CA2300–CA2330 (insecure deserializers), CA5394 (insecure randomness).
  Note: CA3001+ taint rules are disabled by default ("Enabled by default in .NET 10: No") — enable explicitly
  in `.editorconfig` (`dotnet_diagnostic.CA3001.severity = error`).
- Unity: analyzer `.dll`s run in Unity when given the asset label `RoslynAnalyzer` (exact, case-sensitive) with
  Any Platform/Editor/Standalone unticked in the Plugin Inspector (Unity 6.3 Manual); scope per asmdef.
  At minimum run them on shared netstandard libraries.

## CodeQL (GitHub)
```yaml
- uses: github/codeql-action/init@<sha>
  with: { languages: csharp, build-mode: none, queries: security-extended }
- uses: github/codeql-action/analyze@<sha>
```
- `build-mode: none` analyzes C# without compiling (faster, slightly less precise); use `autobuild`/manual
  for best accuracy on critical services. Private repos need GitHub Code Security license
  (GHAS split into Secret Protection $19 + Code Security $30 per active committer/month from 2025-04-01,
  also available on Team plans; re-check current pricing).
- Semgrep alternative/add-on: `semgrep scan --config p/csharp --config p/secrets --error`.

## Secret scanning
```bash
gitleaks git --redact --exit-code 1          # history of current branch; `git`/`dir` since v8.19 (detect/protect deprecated)
gitleaks dir --redact .                      # working tree (e.g. Unity StreamingAssets, configs)
```
- Pre-commit hook (`pre-commit` framework, `gitleaks` hook) on dev machines (Windows: works in Git Bash).
- gitleaks-action needs a (free) license key for organization repos; or run the binary directly.
- Leak response: revoke/rotate first, then purge history (`git filter-repo`) if needed — purging
  without rotating is useless (forks, caches, clones).
- Unity-specific places secrets hide: `ProjectSettings/*.asset` (service IDs are fine; API secrets are
  not), `StreamingAssets/*.json`, `Resources/*.txt`, Firebase `google-services.json` (public-ish but
  lock down with rules), keystore passwords in `ProjectSettings` — Android keystore passwords must
  come from CI secrets, not committed settings.

## DAST with ZAP
```yaml
- uses: zaproxy/action-baseline@<sha>       # passive, safe for stage
  with: { target: https://stage.example.com, rules_file_name: .zap/rules.tsv, fail_action: true }
- uses: zaproxy/action-api-scan@<sha>       # active against OpenAPI; stage only, never prod
  with: { target: https://stage.example.com/openapi/v1.json, format: openapi }
```
- Authenticated scans: script login or inject a stage-only test token via header replacer.
- `.zap/rules.tsv` to IGNORE accepted alerts with justification comment; review quarterly.
- WebSocket/SignalR/UDP game traffic isn't covered by ZAP — test via custom harness/fuzzing.

## Pen-test scoping
| Item | Define |
|---|---|
| Objective | e.g. "can a player gain currency/withdraw funds without paying/winning?" |
| In scope | hosts, APIs (OpenAPI), game client builds (APK/IPA/PC), admin back-office, test accounts per role |
| Out of scope | third-party PSP/store/IdP infrastructure, DoS/load, social engineering (unless agreed) |
| Environment | stage with prod-like config + seeded data; prod only with written approval + window |
| Type | black/grey/white box (grey default: accounts + API docs); client reversing included for games |
| Rules | test windows, contacts, stop conditions, data handling, reporting format (CVSS + PoC) |
| Retest | included, within 30–60 days of fixes |
- Real-money/gambling: regulators often require periodic independent pen-tests and RNG/platform
  audits by accredited labs (verify per jurisdiction with compliance-advisor).
- Authorization letter signed by the asset owner before any testing. Agents never scan third
  parties or production on their own.

## Vulnerability triage and SLAs
1. Validate (reproduce / reachability: is the vulnerable code path used? is the package in the shipped artifact?).
2. Score: CVSS v4.0 base → adjust with exploitability (CISA KEV listed? EPSS high?) and business impact.
3. Assign owner + due date by severity; track in the issue tracker with label `security`.
| Severity | Remediation SLA (internet-facing) | Reference points |
|---|---|---|
| Critical (or KEV-listed) | 7 days (KEV: ≤ 14 days max) | CISA BOD 22-01: KEV CVEs ≤ 2 weeks for federal agencies |
| High | 30 days | FedRAMP ConMon: High 30 days |
| Medium | 90 days | FedRAMP: Moderate 90 days |
| Low | 180 days or accept | FedRAMP: Low 180 days |
- Exceptions: documented risk acceptance with compensating control, approver (tech-lead-architect
  + producer for business risk), expiry date.
- Metrics: open vulns by severity, mean time to remediate, SLA breach count — reported per release.
- Client builds: a fix in the game client ships only with a store release — plan server-side
  mitigations (block old versions via min-version gate) for Critical client issues.

## Secure SDLC touchpoints (lightweight, per feature)
| Phase | Activity | Owner |
|---|---|---|
| Spec | abuse cases + ASVS-level requirements in acceptance criteria | security-engineer + system-analyst |
| Design | threat model for new trust boundaries/money/PII | security-engineer |
| Code | analyzers, secure defaults, review checklist (appsec-web-api.md grep list) | developers + code-reviewer |
| Test | security test cases (authz matrix, replay, race) | qa-engineer |
| Release | gates green, SBOM, pen-test for major changes | devops-sre-engineer, security-engineer |
| Operate | monitoring, incident runbook, vuln intake (`security.txt`, bug bounty) | devops-sre-engineer |
- Maturity references: OWASP SAMM for program assessment; NIST SSDF (SP 800-218) for practice list.

## Sources
- GitHub Docs: CodeQL code scanning https://docs.github.com/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql
- Microsoft Learn: Code analysis security rules (CA2100, CA3001…, CA5350…) https://learn.microsoft.com/dotnet/fundamentals/code-analysis/quality-rules/security-warnings
- gitleaks https://github.com/gitleaks/gitleaks
- Microsoft Learn: CA3001 https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3001
- Unity 6.3 Manual: Install an existing analyzer https://docs.unity.com/en-us/engine/6000.3/manual/programming-environment/script-compilation/roslyn-analyzers/install-existing-analyzer
- GitHub changelog: Secret Protection and Code Security (2025-03-04) https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/
- ZAP GitHub Actions https://www.zaproxy.org/docs/automate/github-actions/
- CISA BOD 22-01 and KEV catalog https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- FedRAMP Continuous Monitoring Performance Management Guide https://www.fedramp.gov/
- NIST SP 800-218 SSDF https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP SAMM https://owaspsamm.org/
