# CI/CD for .NET services (practitioner reference)

## Pipeline stages (default order; each blocks the next)
| Stage | Command / tool | Gate |
|---|---|---|
| Restore | `dotnet restore --locked-mode` | lock file (`packages.lock.json`, `RestorePackagesWithLockFile=true`) unchanged |
| Build | `dotnet build -c Release --no-restore -warnaserror` | zero warnings (analyzers on via `AnalysisLevel=latest-recommended`) |
| Unit tests | `dotnet test --no-build -c Release` | 100% pass; flaky tests quarantined with an issue, not retried silently |
| Coverage | coverlet / Microsoft.Testing.Extensions.CodeCoverage + ReportGenerator | line coverage on changed code ≥ 80% (team-set; never a vanity global %) |
| Integration | Testcontainers (Postgres/Redis/Kafka) or compose services | API contract tests green |
| Security | SAST, SCA, secret scan, container scan (owned by security-engineer, see `studio:security-engineer`) | no new Critical/High |
| Package | `dotnet publish` → OCI image; SBOM; provenance attestation | image signed/attested, digest recorded |
| Deploy stage | Helm/Bicep/Terraform apply with the digest | smoke tests + synthetic check pass |
| Deploy prod | same artifact (by digest), environment approval | SLO burn normal for 30 min post-deploy |
Rule: build once, promote the same digest through environments; config differs, binary never does.

## Reproducibility
- `global.json` pins SDK (`"rollForward": "latestFeature"` or `latestPatch`); `actions/setup-dotnet`
  reads it via `global-json-file: global.json`.
- Central Package Management (`Directory.Packages.props`) + lock files; `Directory.Build.props` for
  `TreatWarningsAsErrors`, `Nullable`, `AnalysisLevel`, `Deterministic`, `ContinuousIntegrationBuild=true`.
- Cache `~/.nuget/packages` keyed on `**/packages.lock.json`.
- NuGet audit runs at restore (SDK 8+); `NuGetAuditMode=all` covers transitive deps (default `all` only
  for projects targeting net10.0+ (NuGet 7 / .NET 10 SDK), else `direct` — set it explicitly); fail with `WarningsAsErrors=NU1903;NU1904` (high/critical).

## GitHub Actions skeleton
```yaml
name: api-ci
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }               # least privilege by default
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<sha>          # pin by SHA
      - uses: actions/setup-dotnet@<sha>
        with: { global-json-file: global.json, cache: true, cache-dependency-path: '**/packages.lock.json' }
      - run: dotnet restore --locked-mode
      - run: dotnet build -c Release --no-restore -warnaserror
      - run: dotnet test -c Release --no-build --collect "XPlat Code Coverage" --results-directory cov
      - run: |
          dotnet tool install -g dotnet-reportgenerator-globaltool
          reportgenerator -reports:"cov/**/coverage.cobertura.xml" -targetdir:cov/report -reporttypes:"Cobertura;MarkdownSummaryGithub"
          cat cov/report/SummaryGithub.md >> $GITHUB_STEP_SUMMARY
  image:
    needs: build-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write, id-token: write, attestations: write }
    outputs: { digest: ${{ steps.push.outputs.digest }} }
    steps:
      - uses: actions/checkout@<sha>
      - uses: docker/login-action@<sha>
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - id: push
        uses: docker/build-push-action@<sha>
        with: { push: true, tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}, sbom: true, provenance: mode=max }
      - uses: actions/attest-build-provenance@<sha>
        with: { subject-name: ghcr.io/${{ github.repository }}/api, subject-digest: ${{ steps.push.outputs.digest }}, push-to-registry: true }
  deploy-prod:
    needs: image
    runs-on: ubuntu-latest
    environment: production                    # required reviewers + wait timer set in repo settings
    permissions: { id-token: write, contents: read }
    steps:
      - uses: azure/login@<sha>                # or aws-actions/configure-aws-credentials: OIDC, no stored keys
        with: { client-id: ${{ vars.AZURE_CLIENT_ID }}, tenant-id: ${{ vars.AZURE_TENANT_ID }}, subscription-id: ${{ vars.AZURE_SUB_ID }} }
      - run: helm upgrade --install api deploy/charts/api --set image.digest=${{ needs.image.outputs.digest }} --atomic --timeout 10m
```
- `--collect "XPlat Code Coverage"` is VSTest mode; if `global.json` selects MTP, use `--coverage --coverage-output-format cobertura` (see stack-dotnet testing-dotnet).
- `--atomic` rolls back the Helm release automatically if the rollout fails.
- Coverage gate: fail if below threshold, e.g. `coverlet.msbuild` `/p:Threshold=80 /p:ThresholdType=line`,
  or a diff-coverage tool on changed lines (preferred for legacy code).

## GitLab CI equivalents
| GitHub | GitLab |
|---|---|
| `environment: production` + required reviewers | protected environment + deployment approvals (Premium+) |
| `needs:` | `needs:` (DAG) |
| `if:` on job | `rules: - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH` |
| OIDC `id-token: write` | `id_tokens:` keyword (JWT with `aud`) |
| Coverage summary | `coverage: '/Total.*?(\d+\.?\d*)%/'` + `artifacts:reports:coverage_report` (cobertura) |
| Dependabot | Dependency Scanning template / Renovate |
```yaml
test:
  image: mcr.microsoft.com/dotnet/sdk:10.0
  script: [dotnet test -c Release --collect "XPlat Code Coverage"]
  artifacts:
    reports: { coverage_report: { coverage_format: cobertura, path: "**/coverage.cobertura.xml" } }
deploy_prod:
  stage: deploy
  environment: { name: production, url: https://api.example.com }
  rules: [{ if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH', when: manual }]
  script: [helm upgrade --install api deploy/charts/api --atomic]
```

## Containers from CI
- Dockerfile route: multi-stage (see containers-and-k8s.md). SDK route (no Dockerfile):
  `dotnet publish -c Release --os linux --arch x64 /t:PublishContainer -p:ContainerRepository=api`
  (`ContainerFamily=noble-chiseled` for a minimal base). Pick one route per repo.
- Tag images with commit SHA (immutable) + optional SemVer; deploy by digest, never `:latest`.
- Scan images (Trivy/Grype) in CI and on a nightly schedule (new CVEs appear after build).

## SBOM and provenance
| Tool | Output | Notes |
|---|---|---|
| CycloneDX .NET (`dotnet-CycloneDX`) | CycloneDX JSON from NuGet graph | app-level dependencies |
| Microsoft sbom-tool | SPDX 2.2/3 | used for Microsoft's own builds |
| Syft / BuildKit `sbom: true` | SPDX/CycloneDX of the image | includes OS packages |
| `actions/attest-build-provenance` | SLSA provenance, Sigstore-signed | verify with `gh attestation verify` |
- Store SBOMs with the artifact; feed them to Dependency-Track or GitHub dependency graph for
  continuous CVE matching after release.

## Supply-chain hardening for the pipeline itself
- Pin third-party actions to full commit SHAs; the tj-actions/changed-files compromise
  (March 2025, CVE-2025-30066) leaked secrets from repos using mutable tags.
- `permissions:` minimal at workflow level; elevate per job. No `pull_request_target` with checkout
  of PR code. Fork PRs never get secrets.
- OIDC federation to Azure/AWS/GCP instead of long-lived cloud keys; scope trust to repo + branch/environment.
- Dependabot/Renovate for actions, NuGet and base images; auto-merge patch updates only when tests pass.
- Required status checks + branch protection/rulesets on `main`; CODEOWNERS for `.github/` and `deploy/`.

## Environments and approvals
| Env | Deploy trigger | Approval | Data |
|---|---|---|---|
| dev | every merge to main | none | synthetic |
| stage | auto after dev smoke | none (or QA) | anonymised prod-like |
| prod | promotion of the same digest | 1–2 required reviewers, change window for risky changes | real |
- Casino/real-money: prod deploys need an audit trail (who, what digest, when) — environment
  deployment history + change ticket; regulated jurisdictions may require certified build
  hashes (see `studio:domain-igaming`, confirm with compliance-advisor).

## Sources
- GitHub Docs: Using environments for deployment https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment
- GitHub Docs: Security hardening for GitHub Actions https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- GitHub Docs: Artifact attestations https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations
- Microsoft Learn: Containerize a .NET app with dotnet publish https://learn.microsoft.com/dotnet/core/containers/sdk-publish
- Microsoft Learn: Auditing package dependencies (NuGet audit) https://learn.microsoft.com/nuget/concepts/auditing-packages
- Microsoft Learn: Testing with dotnet test (VSTest vs MTP mode) https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-with-dotnet-test
- GitLab Docs: Deployment approvals https://docs.gitlab.com/ci/environments/deployment_approvals/
- CISA alert on tj-actions/changed-files (CVE-2025-30066) https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction
