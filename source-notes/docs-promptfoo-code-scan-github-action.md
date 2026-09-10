---
source_url: https://www.promptfoo.dev/docs/code-scanning/github-action/
source_type: docs
title: "Promptfoo Code Scanning — GitHub Action"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-10
date_extracted: 2026-09-10
last_checked: 2026-09-10
status: current
confidence_overall: emerging
issue: "#1265"
---

# Promptfoo Code Scanning — GitHub Action

> The GitHub Action CI wiring for Promptfoo's LLM-security code scanner. The
> primary contribution is concrete supply-chain hardening: a cross-step
> intra-job environment-state-persistence attack vector (and its isolation
> mitigation), provenance-verified dependency pinning with build attestations,
> and fork-PR default-deny — all documented with actionable configuration.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Code Scan GitHub Action page)
- **Author credibility**: Promptfoo, the commercial LLM-security scanner vendor
  (now part of OpenAI per the site banner). The content is first-party product
  documentation describing the GitHub Action's configuration, trust model, and
  supply-chain security features. It is authoritative about the product's own
  feature set but is vendor-positioned; scanner behavior claims are not independently
  validated. The supply-chain hardening section (post-v0.1.8 provenance attestation,
  intra-job persistence mitigation) describes independently checkable mechanisms
  (`gh attestation verify`, workflow structure) rather than opaque product behavior.
- **Scope**: Covers the GitHub Action installation paths (GitHub App vs manual),
  action input configuration surface, fork-PR gating, SARIF publishing to
  GitHub Code Scanning, two-auth trust-model tradeoff, and the Supply Chain
  Security section. Does NOT cover the scanner's code-analysis methodology
  (call-graph tracing, far-tracing, CVE detection) — those are covered in
  `blog-promptfoo-building-security-scanner-llm-apps.md` (#292). The CLI
  surface is covered by sibling #1264 (`/docs/code-scanning/cli/`).
- **Vendor caveat**: Scans run against `https://api.promptfoo.app`; on-prem
  execution is Enterprise-only. Treat the hardening claims as vendor guidance
  to verify, not independently established practice. The CI-isolation and
  provenance-verification mechanisms are independently checkable and are the
  items worth citing in the guide.

## Extracted Claims

### Claim 1: Intra-job environment-state persistence allows a PR-controlled code step to compromise a later security scan step within the same CI job
- **Evidence**: The Supply Chain Security section explicitly describes the attack
  vector: the scanner's installer strips npm config and `NODE_OPTIONS` from its
  own environment and isolates its npm config files, but a step that runs
  pull-request-controlled code earlier in the same job (such as `npm ci` or a
  build) can persist state — `$GITHUB_PATH`, `$GITHUB_ENV`, or `$HOME` writes —
  that later steps inherit, and that step already runs with the job's GitHub token.
  The stated mitigation: keep the scan in a job that only checks out and scans
  the PR; run untrusted build steps in a separate job.
- **Confidence**: emerging (vendor-authored security guidance; the mechanism is
  a well-known CI/CD attack surface but the specific mitigation framing is
  Promptfoo's recommendation)
- **Quote**: "The scanner install strips npm config and `NODE_OPTIONS` from its
  environment and isolates its npm config files, but a step that runs
  pull-request-controlled code earlier in the same job (such as `npm ci` or a
  build) can persist state — `$GITHUB_PATH`, `$GITHUB_ENV`, or `$HOME` writes —
  that later steps inherit, and it already runs with the job's token."
- **Our assessment**: Buy it. The intra-job persistence vector is real and
  distinct from the inter-job blast-radius issue documented in the LiteLLM
  incident (`failure-litellm-supply-chain-incident-march-2026.md`, Claim 4/11):
  that incident focused on shared environments *across* pipeline stages; this
  is an attack *within* a single job where an earlier step poisons environment
  state for later steps. The scanner's own npm config stripping is a defense
  against the direct vector but not against this indirect persistence. The
  isolation recommendation (scan-only job, untrusted build in a separate job)
  is the correct generalization of the blast-radius principle to the intra-job
  level. High value for Ch06.

### Claim 2: The action installs an exact, release-pinned CLI version with `--ignore-scripts` and publishes a signed build-provenance attestation for the artifact bytes
- **Evidence**: The Supply Chain Security section documents three mechanisms:
  (a) the action installs an exact, release-pinned version of the `promptfoo`
  CLI with npm lifecycle scripts disabled (`--ignore-scripts`); (b) it does not
  resolve `promptfoo@latest` at runtime; (c) the `dist/` bundle and `action.yml`
  are built by the promptfoo monorepo release workflow, which publishes a signed
  build-provenance attestation for the exact artifact bytes. Verification command:
  `gh attestation verify dist/index.js --repo promptfoo/promptfoo` (and likewise
  for `action.yml`).
- **Confidence**: settled (independently checkable via `gh attestation verify`)
- **Quote**: "The `dist/` bundle and `action.yml` committed to
  [promptfoo/code-scan-action](https://github.com/promptfoo/code-scan-action)
  are built and exported by the promptfoo monorepo release workflow, which
  publishes a signed build-provenance attestation for the exact artifact bytes.
  Verify a checkout with `gh attestation verify dist/index.js --repo
  promptfoo/promptfoo` (and likewise for `action.yml`)."
- **Our assessment**: Buy it. This is the concrete "how" behind the guide's
  existing rule at `guide/06-security-and-trust.md:486` ("Pin every CI
  dependency to verified SHAs — including security scanners"). The `--ignore-scripts`
  flag prevents npm lifecycle hooks from executing during install, closing the
  hook-injection vector. The provenance attestation provides a cryptographic
  chain from source to artifact, which is strictly stronger than SHA pinning
  alone (a SHA pin tells you what you have; the attestation tells you who
  built it and how). The `gh attestation verify` command is the copyable
  verification step.

### Claim 3: The hardening boundary is post-v0.1.8 — releases before v0.1.8 resolved `promptfoo@latest` at runtime and predate the provenance attestation
- **Evidence**: The Supply Chain Security section header explicitly scopes the
  hardening to "code-scan-action releases after v0.1.8" and states earlier
  releases "resolve `promptfoo@latest` at runtime and predate the provenance
  attestation." The `promptfoo-version` input is documented as rejecting ranges
  and dist-tags.
- **Confidence**: settled (vendor-documented version boundary)
- **Quote**: "The hardening below applies to code-scan-action releases after
  v0.1.8; earlier releases resolve `promptfoo@latest` at runtime and predate
  the provenance attestation."
- **Our assessment**: Buy it. The version boundary is the actionable trust
  cutoff: teams using the action should ensure they are on a post-v0.1.8
  release. The `promptfoo-version` input's rejection of ranges/dist-tags
  (e.g., `0.121.0` not `latest`) reinforces this as a design-level constraint
  rather than documentation-only guidance. Worth calling out as a concrete
  "upgrade threshold" for the guide's supply-chain section.

### Claim 4: Fork-PR scanning is disabled by default — a maintainer override via `@promptfoo-scanner` comment or `enable-fork-prs: true` is required
- **Evidence**: The Fork Pull Requests section states scanning is disabled by
  default for fork PRs because any GitHub user can open a fork PR on public
  repositories. A maintainer with write permissions can trigger a scan via a
  `@promptfoo-scanner` comment, or opt in globally via `enable-fork-prs: true`.
  The page provides the YAML configuration snippet for the opt-in.
- **Confidence**: settled (concrete documented behavior)
- **Quote**: "By default, code scanning is disabled for fork PRs. This is
  because any GitHub user can open a fork PR on public repositories."
- **Our assessment**: Buy it. A clean default-deny pattern for an LLM-scanner
  CI gate: fork PRs (untrusted by definition) are not scanned unless a maintainer
  explicitly approves. The `@promptfoo-scanner` comment trigger is an interesting
  granularity — one-off override per PR without changing the workflow file. This
  is a generalizable CI-cost/abuse control pattern relevant to any CI-gated
  LLM security tool (Ch03/Ch06).

### Claim 5: SARIF output is only published when a scan actually completes — an intentionally skipped scan does not publish a clean Code Scanning result
- **Evidence**: The Write SARIF output section explicitly warns: "The action
  sets `sarif-path` only when a scan actually completes, so keep the upload step
  conditional." The conditional guard is `if: ${{ steps.promptfoo-code-scan.outputs.sarif-path != '' }}`. The text states: "Intentionally skipped scans do not
  publish a clean Code Scanning result."
- **Confidence**: settled (concrete documented operational gotcha)
- **Quote**: "The action sets `sarif-path` only when a scan actually completes,
  so keep the upload step conditional. Intentionally skipped scans do not publish
  a clean Code Scanning result."
- **Our assessment**: Buy it. This is a real operational footgun: if the upload
  step is unconditional (no `if` guard), a skipped scan would produce a
  zero-finding SARIF upload that shows up as "all clear" in the Security tab
  — a false clean. The conditional-guard pattern is simple and the failure mode
  is subtle enough to be a common wiring mistake. Extends the SARIF-output
  capability already covered by `blog-promptfoo-open-sourcing-modelaudit.md`
  Claim 12, which documents SARIF as a capability but not this publishing
  path or skip-vs-clean distinction.

### Claim 6: Two authentication paths with different trust properties — GitHub App (OIDC keyless) vs manual install (API key required)
- **Evidence**: Quick Start states the GitHub App path uses GitHub OIDC for
  automatic authentication with no API key, token, or Promptfoo Cloud account;
  just a valid email address. Manual Installation states a Promptfoo Cloud
  account is required, plus a `PROMPTFOO_API_KEY` secret, and PR comments come
  from `github-actions[bot]` rather than the official Promptfoo Scanner bot.
- **Confidence**: settled (concrete documented product behavior)
- **Quote**: "Authentication is handled automatically with GitHub OIDC. No API
  key, token, or other configuration is needed."
- **Quote**: "You'll need a [Promptfoo API token](https://www.promptfoo.app/api-tokens)
  for authentication."
- **Our assessment**: Buy it as a product documentation fact. The trust-model
  difference is significant: the GitHub App path avoids long-lived secrets
  entirely (OIDC tokens are ephemeral and scoped), while the manual path
  requires a persistent `PROMPTFOO_API_KEY` secret stored in GitHub. For teams
  using the manual path, this is a CI credential hygiene surface worth noting.
  The bot-identity difference (`promptfoo-scanner` bot vs `github-actions[bot]`)
  also affects audit-trail traceability. Treat both paths as vendor-positioned
  but document the concrete tradeoff.

### Claim 7: Severity threshold input with deprecated alias precedence rules, and exact-version-only enforcement for `promptfoo-version`
- **Evidence**: The Action Inputs table documents `min-severity` (default
  `medium`, values `low|medium|high|critical`) and its deprecated alias
  `minimum-severity` ("Takes effect only when `min-severity` is unset; if both
  are set, `min-severity` wins and a warning is emitted"). The `promptfoo-version`
  input is documented as accepting exact versions only ("Ranges and dist-tags
  are rejected"). The default is "Version pinned at release."
- **Confidence**: settled (concrete documented configuration behavior)
- **Quote**: "Ranges and dist-tags are rejected."
- **Our assessment**: The severity input is the merge-gating knob — teams set
  `min-severity: high` to fail CI on critical/high findings only. The alias
  precedence rule is a defensive design: both inputs can coexist in a shared
  workflow without conflict. The `promptfoo-version` exact-only constraint is
  a supply-chain control embedded in the input schema (ranges like `@latest`
  would reintroduce the runtime-resolution risk that post-v0.1.8 eliminates).
  Not novel individually, but the combination of a severity gate + an
  exact-version pin + provenance attestation in a single Action is the
  concrete supply-chain-hardening stack the guide should document.

### Claim 8: The documented workflow pins third-party actions to full commit SHAs and recommends pinning the scanner action itself via `gh api` resolution
- **Evidence**: The Manual Installation workflow example pins `actions/checkout`,
  `actions/setup-node`, and `github/codeql-action/upload-sarif` by full commit
  SHA with version comments. The page states: "Tags such as `v0` are convenient
  but mutable; a commit SHA is the only immutable reference." It recommends
  resolving `promptfoo/code-scan-action`'s release tag to its commit with
  `gh api repos/promptfoo/code-scan-action/commits/<tag> --jq .sha` and using
  `uses: promptfoo/code-scan-action@<full-commit-sha> # <tag>`. The action's
  bundled runtime is Node.js 24; older releases and direct CLI paths require
  Node.js `>=22.22.0`.
- **Confidence**: settled (concrete documented recommendation)
- **Quote**: "Tags such as `v0` are convenient but mutable; a commit SHA is the
  only immutable reference."
- **Our assessment**: Buy it. The pinned-SHA convention is already a best
  practice (and cited by the LiteLLM incident notes); the novel addition here
  is the specific `gh api` resolution command for pinning the scanner action
  itself, plus the acknowledgment that `v0` (a convenience tag) is mutable
  and therefore weaker than a commit SHA. This is the concrete implementation
  of the guide's existing rule at `guide/06-security-and-trust.md:486` ("Pin
  every CI dependency to verified SHAs — including security scanners").

## Concrete Artifacts

### Workflow skeleton (verbatim from Manual Installation section)

```yaml
name: Promptfoo Code Scan
on:
  pull_request:
    types: [opened, ready_for_review, synchronize]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      security-events: write
    steps:
      - name: Checkout code
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          fetch-depth: 0
      - name: Set up Node.js
        uses: actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6
        with:
          node-version: '24'
      - name: Run Promptfoo Code Scan
        id: promptfoo-code-scan
        uses: promptfoo/code-scan-action@v0
        env:
          PROMPTFOO_API_KEY: ${{ secrets.PROMPTFOO_API_KEY }}
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          min-severity: medium
          sarif-output-path: promptfoo-code-scan.sarif
      - name: Upload SARIF to GitHub Code Scanning
        if: ${{ steps.promptfoo-code-scan.outputs.sarif-path != '' }}
        uses: github/codeql-action/upload-sarif@54f647b7e1bb85c95cddabcd46b0c578ec92bc1a # v4.36.3
        with:
          sarif_file: ${{ steps.promptfoo-code-scan.outputs.sarif-path }}
          category: promptfoo-code-scan
```
Source: promptfoo docs, "Workflow Configuration" section. Note the conditional
upload guard and pinned third-party actions.

### Supply Chain Security section (verbatim)

```markdown
The hardening below applies to code-scan-action releases after v0.1.8;
earlier releases resolve `promptfoo@latest` at runtime and predate the
provenance attestation.

- The action installs an exact, release-pinned version of the `promptfoo`
  CLI with npm lifecycle scripts disabled (`--ignore-scripts`); it does not
  resolve `promptfoo@latest` at runtime. Use the `promptfoo-version` input
  to override the pin with another exact version.
- The `dist/` bundle and `action.yml` committed to
  [promptfoo/code-scan-action](https://github.com/promptfoo/code-scan-action)
  are built and exported by the promptfoo monorepo release workflow, which
  publishes a signed build-provenance attestation for the exact artifact
  bytes. Verify a checkout with `gh attestation verify dist/index.js
  --repo promptfoo/promptfoo` (and likewise for `action.yml`).
- The scanner install strips npm config and `NODE_OPTIONS` from its
  environment and isolates its npm config files, but a step that runs
  pull-request-controlled code earlier in the same job (such as `npm ci`
  or a build) can persist state — `$GITHUB_PATH`, `$GITHUB_ENV`, or
  `$HOME` writes — that later steps inherit, and it already runs with the
  job's token. Keep the scan in a job that only checks out and scans the
  PR; run untrusted build steps in a separate job.
```
Source: promptfoo docs, "Supply Chain Security" section. Verbatim.

### Action input defaults (summary table)

| Input | Default | Notes |
|-------|---------|-------|
| `api-host` | `https://api.promptfoo.app` | Vendor-hosted scanner backend |
| `min-severity` | `medium` | `low\|medium\|high\|critical`; wins over deprecated alias |
| `config-path` | Auto-detected | `.promptfoo-code-scan.yaml` |
| `enable-fork-prs` | `false` | Fork PR scanning disabled by default |
| `promptfoo-version` | Pinned at release | Exact versions only; ranges/dist-tags rejected |
| `sarif-output-path` | (none) | Conditional upload required for Code Scanning |

Source: promptfoo docs, "Action Inputs" table.

### Provenance verification command

```bash
gh attestation verify dist/index.js --repo promptfoo/promptfoo
```
Source: promptfoo docs, "Supply Chain Security" section. Verbatim.

## Cross-References

- **Corroborates**:
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 4** (shared
    CI environment increases blast radius: "all steps shared a common environment.
    That increased blast radius: if one component was compromised, it could
    potentially access credentials or context intended for other parts of the
    pipeline") — documents the *inter-job* blast-radius failure; this page's
    intra-job state-persistence vector (Claim 1) is a new, distinct mechanism
    for the same principle. Together they establish that CI isolation must cover
    both cross-job boundaries (LiteLLM's lesson) and intra-job step boundaries
    (this page's contribution).
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 14** ("Move
    to pinned, verified SHAs for packages and actions used in CI/CD, avoiding
    latest wherever possible") — this page's pinned CLI version, `--ignore-scripts`
    constraint, and pinned-SHA workflow skeleton are the concrete implementation
    of the same control for a scanning Action.
  - `failure-litellm-supply-chain-compromise-march-2026.md` **Lesson 4**
    (pinned-Docker installs were safe; unpinned pip installs were exposed —
    "You ran pip install litellm without pinning a version and received
    v1.82.7 or v1.82.8") — the real-world consequence of unpinning; this
    page's `--ignore-scripts` + release-pinned CLI + provenance attestation
    is the supply-chain-hardening answer.
  - `blog-promptfoo-building-security-scanner-llm-apps.md` — extends that
    note's Claims 5-6 (general scanners cannot detect LLM injection via
    sanitization shortcuts; far-tracing is the method) with the concrete CI
    deployment: this page is the GitHub Action that packages the same scanner
    for CI gate use. The two notes are complementary layers: methodology (blog,
    #292) vs CI wiring and supply-chain trust boundaries (this note, #1265).
  - `blog-promptfoo-open-sourcing-modelaudit.md` **Claim 12** (ModelAudit
    supports SARIF output) — extends that SARIF capability claim with the
    GitHub Code Scanning publishing path: this page documents how SARIF output
    actually surfaces in the Security tab, plus the conditional-upload /
    skip-vs-clean gotcha (Claim 5) that the capability claim does not cover.

- **Contradicts**: None identified. The guide's existing Ch06 CI-isolation rule
  (`guide/06-security-and-trust.md:485`, citing the LiteLLM incident) and this
  page's intra-job persistence vector are complementary mechanisms for the same
  blast-radius principle — not opposing claims. No existing note claims that CI
  isolation, artifact pinning, or SARIF publishing is unnecessary or harmful.

- **Extends**:
  - `blog-promptfoo-building-security-scanner-llm-apps.md` **Claim 10** (custom
    guidance as a config-level strictness tuning mechanism) — this page
    operationalizes the guidance-from-the-blog as a file-based config schema
    (`.promptfoo-code-scan.yaml`: `minSeverity`, `diffsOnly`, `guidance`),
    providing the concrete deployment artifact for the design pattern.
  - `blog-promptfoo-open-sourcing-modelaudit.md` **Claim 12** — extends the
    SARIF-output capability with the conditional-upload workflow and skip-vs-clean
    distinction specific to GitHub Code Scanning integration.
  - `failure-litellm-supply-chain-compromise-march-2026.md` — extends the
    supply-chain threat model by adding an intra-job persistence vector. The
    LiteLLM incident focused on PyPI publishing pipeline compromise; this
    page's CI attack vector (earlier job steps poisoning later scanner steps
    via environment state) is a different, more subtle attack surface.

- **Novel**: First source note in the corpus covering:
  1. **Intra-job environment state persistence** as a CI/scan attack vector —
     the `$GITHUB_PATH`/`$GITHUB_ENV`/`$HOME` persistence mechanism and the
     scan-only-job isolation mitigation are new to the corpus.
  2. **`gh attestation verify`** for Action-bundle provenance verification —
     the concrete tool for verifying signed build-provenance attestations on
     a GitHub Action's `dist/` bundle is new.
  3. **Version-boundary cutoff semantics** (≤ v0.1.8 = unpinned + no
     attestation) as an actionable trust boundary for a CI dependency.
  4. **Fork-PR default-deny + `@promptfoo-scanner` maintainer override** as a
     CI-cost/abuse control pattern.
  5. **Two-auth-model trust tradeoff** (OIDC keyless vs API-key manual) for a
     scanning bot — same vendor ecosystem, different credential surfaces.
  6. **SARIF conditional-upload skip-vs-clean distinction** — the operational
     gotcha that an intentionally skipped scan must not publish a clean Code
     Scanning result.

## Guide Impact

- **Chapter 06 (Security and Trust)**, section "Three CI/CD anti-patterns" /
  "Isolate CI/CD stages by blast radius" (`guide/06-security-and-trust.md:485`):
  The guide's existing rule cites `failure-litellm-supply-chain-incident-march-2026`
  Claim 11 at the *job* level. This page adds a *new* intra-job vector: steps
  within a single job can poison each other via environment-state persistence
  even when the job itself is correctly scoped. **Recommendation**: update the
  rule or add a callout that job-level isolation alone is insufficient — earlier
  steps that run untrusted code can persist `$GITHUB_PATH`/`$GITHUB_ENV`/`$HOME`
  writes that compromise later steps. Cite this source (Claim 1) as the
  concrete mechanism.
- **Chapter 06**, section "Pin every CI dependency to verified SHAs"
  (`guide/06-security-and-trust.md:486`): This page provides the concrete
  verification step — `gh attestation verify dist/index.js --repo promptfoo/promptfoo`
  — as a worked example of provenance verification for a specific Action.
  **Recommendation**: add this as a copyable verification example alongside the
  existing `cosign verify` release-image example. Also cite the pinned-SHA
  workflow convention (Claim 8) as the implementation of the "pin everything"
  rule for Actions specifically.
- **Chapter 03 (Runbooks & Agents)**, section "Red-teaming as a CI gate" or
  CI/CD gating: The fork-PR default-deny pattern (Claim 4) is a generalizable
  CI-cost and abuse-control pattern for any CI-gated LLM security tool. The
  SARIF conditional-upload gotcha (Claim 5) is an operational footgun relevant
  to any team wiring a scanner into GitHub Code Scanning.

## Extraction Notes

- Source read in full: https://www.promptfoo.dev/docs/code-scanning/github-action/
  (fetched via direct HTTP). Single self-contained docs page; no sub-pages
  required following. All quoted passages were copied character-for-character
  from the extracted HTML.
- The Prospector triage (three concurrent runs, all agreeing) explicitly
  recommended extracting only the net-new CI/supply-chain material and NOT
  re-extracting the scanner methodology already captured in
  `blog-promptfoo-building-security-scanner-llm-apps.md` (#292). This note
  follows that guidance: no call-graph tracing, far-tracing, or CVE methodology
  is extracted here; only the CI wiring, trust boundaries, and operational
  gotchas are new.
- Sibling #1264 (CLI page, `/docs/code-scanning/cli/`) is queued separately;
  the SARIF conditional-upload gotcha is shared between the two pages.
  Coordination note: this note carries the GitHub Code Scanning publishing path;
  the CLI note (when mined) should carry the CLI interface surface. Neither note
  should duplicate the other's SARIF coverage.
- Cross-reference candidates file (`miner-related-notes.md`) was read per
  MINER.md §4 before writing Cross-References. Of the 10 listed candidates,
  all but `blog-promptfoo-owasp-red-teaming.md` (which argues pre-deployment
  LLM security testing belongs in CI/CD) were dismissed as non-overlapping.
  The OWASP red-teaming note was evaluated for proximity but is about runtime
  attack-simulation (red teaming) rather than static code scanning; the
  thematic connection is too weak to cite evidentially. The supply-chain
  cross-references (`failure-litellm-supply-chain-*`, `blog-promptfoo-building-*`)
  were discovered by searching `source-notes/` per the Prospector's guidance.
  Each cited claim was re-read and verified per §4b before citation.
- This note explicitly does NOT contradict `blog-promptfoo-building-security-scanner-llm-apps.md`:
  that note covers scanner methodology and CVE case studies; this covers CI
  wiring and supply-chain trust boundaries — different layers of the same product.
- Vendor caveat: the page is Promptfoo's vendor documentation. All claims about
  scanner behavior are vendor-positioned. The supply-chain hardening items
  (Claims 1-3) describe independently checkable mechanisms; the action input
  defaults and behavioral claims (Claims 5-8) are vendor-reported product
  documentation.
