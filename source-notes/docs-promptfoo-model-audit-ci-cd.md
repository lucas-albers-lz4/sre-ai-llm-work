---
source_url: https://www.promptfoo.dev/docs/model-audit/ci-cd
source_type: docs
title: "Promptfoo ModelAudit — CI/CD Integration: Tri-State Exit Codes, Multi-CI Model-File Gates, and the SARIF/Scheduled-Audit Wiring"
author: "Promptfoo (vendor documentation)"
date_published: null
date_extracted: 2026-11-03
last_checked: 2026-11-03
status: current
confidence_overall: emerging
issue: "#1949"
---

# Promptfoo ModelAudit — CI/CD Integration

> The concrete pipeline wiring for ML model-file scanning: the tri-state
> `0/1/2` exit contract, a changed-file PR workflow, SARIF upload to GitHub Code
> Scanning with a separate failure step, a weekly scheduled audit that opens an
> issue instead of blocking a PR, a path-scoped `--strict` production gate, and
> GitLab/Jenkins/CircleCI recipes that differ materially in whether they actually
> gate. The novel delta over `blog-promptfoo-open-sourcing-modelaudit.md` (#553)
> and the ModelAudit landing page note (#1948) is the per-CI wiring and its
> operational gaps, not the model-file threat model.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "Model Audit > CI/CD
  Integration" page; living docs, no publish date, footer "Last updated on
  **Nov 3, 2026** by **dependabot\[bot\]**").
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team/security
  vendor. First-party documentation of its own `promptfoo scan-model` wrapper and
  `modelaudit` package. Authoritative as a *specification* of workflow YAML, exit
  codes, and CLI flags, all of which are string-checkable against the page and
  the installed CLI. Not measurement: the page publishes no detection rate,
  false-positive rate, runtime benchmark, or field evidence for the gating
  recommendations. The CI recipes are illustrative vendor examples, not hardened
  distribution paths — several install the scanner unpinned.
- **Scope**: Covers exit-code semantics, four GitHub Actions workflows (changed
  model files, SARIF upload, scheduled audit, strict production gate), GitLab CI,
  Jenkins, CircleCI, best-practice scan strategy/performance/security/timeout/
  retry/notifications, and troubleshooting (`--verbose`, `--max-size`,
  `--dry-run`). Does **not** cover the pickle-RCE threat model, blocklist-vs-
  allowlist architecture, GHSA analysis, format coverage, scanner internals, or
  remote-source authentication — those are owned by
  `blog-promptfoo-open-sourcing-modelaudit.md` (#553),
  `docs-promptfoo-model-audit.md` (#1948), and the sibling `/docs/model-audit/
  scanners` page (#1950). The parent note explicitly defers the CI/CD workflow
  YAML and PR-vs-scheduled scanning to this child page.
- **Relationship to sibling pages**: this is the child page that
  `docs-promptfoo-model-audit.md` says it deliberately did **not** mine (#1949).
  It is the canonical home for the model-scan CI/CD wiring; it should be cited
  for that wiring, while #553 and #1948 remain the security-rationale and CLI-
  surface notes.

## Extracted Claims

### Claim 1: The CI gate contract is tri-state — `0` clean, `1` findings (warnings or critical), `2` operational/inconclusive — and the page states only exit 2 is an actual scan failure
- **Evidence**: The "Exit Codes" section defines all three values, and the
  paragraph immediately after states the CI interpretation. The same contract is
  already recorded in `blog-promptfoo-open-sourcing-modelaudit.md` (Concrete
  Artifacts) and `docs-promptfoo-model-audit.md` (Claims 8–9); this page is the
  child page the blog note linked for it.
- **Confidence**: settled (documented CLI contract, checkable against the
  installed command)
- **Quote**: "In CI/CD pipelines, exit code 1 indicates findings that should be reviewed. Only exit code 2 represents actual scan failures."
- **Our assessment**: Buy it as the documented contract, and use it as the model-
  artifact analogue of the code-scan completion-signal rule: exit 2 includes
  "no scanned files", so a gate that checks only `exit == 1` will treat a scan
  that never ran as success. The tri-state is the right primitive. But the
  page's own workflows do not consistently implement the stated policy: the PR
  workflow fails on critical/error findings, and both the scheduled and
  production workflows use `--strict` (warnings fatal). That is the same
  documented-vs-example tension already filed as contradiction **#1995** against
  the parent page; no new contradiction is filed here.

### Claim 2: The reference GitHub Actions PR workflow scans only model files changed in the pull request, diffing the base SHA against the PR SHA and filtering by an extension regex before running one `scan-model` per file
- **Evidence**: The "Scan Changed Model Files" workflow: `actions/checkout@v4`
  with `fetch-depth: 0`; `git diff --name-only --diff-filter=ACM` against
  `${{ github.event.pull_request.base.sha }}`; `grep -Ei "\.(${MODEL_EXTENSIONS})$"`;
  a per-file loop writing `scan_results/<sha256>.json`.
- **Confidence**: settled (directly readable workflow)
- **Quote**: "CHANGED=$(git diff --name-only --diff-filter=ACM"
- **Our assessment**: Buy the pattern: diff-scoped scanning gives fast PR
  feedback and avoids re-scanning an unchanged model corpus. Two operational
  caveats follow from the code. First, each `scan-model` invocation ends in
  `|| true`, so the per-file exit status is discarded; the only gate is the
  later `jq` check over the JSON. If the scanner writes malformed or partial
  JSON, or no JSON at all, the gate's behavior is whatever `jq` does with the
  glob — not what the exit-code contract says. Second, the loop is serial, so
  per-PR cost scales with the number of changed files; the page gives a separate
  `xargs -P 4` performance example (Claim 12) but does not combine it with the
  PR workflow. Neither caveat is fatal, but a team copying this should replace
  `|| true` with captured status and feed it into the aggregate gate.

### Claim 3: The changed-file extension filter is much broader than model weights — it includes config formats (`json`, `yaml`, `yml`, `xml`, `toml`, `config`, `jinja`, `j2`, `template`) and archives (`zip`, `tar`, `7z`), so a config-only PR can trigger model scans
- **Evidence**: The `MODEL_EXTENSIONS` regex in the GitHub, GitLab, and Jenkins
  examples includes those extensions alongside `pkl`, `pt`, `onnx`, `gguf`,
  `safetensors`, and the rest. The same list is reproduced in Concrete
  Artifacts.
- **Confidence**: settled (directly readable regex)
- **Quote**: "MODEL_EXTENSIONS='pkl|pickle|dill|pth|pt|ckpt|checkpoint|orbax-checkpoint|h5|hdf5|keras|onnx|pb|tflite|safetensors|gguf|ggml|ggmf|ggjt|ggla|ggsa|bin|engine|plan|msgpack|flax|orbax|jax|joblib|skops|npy|npz|pmml|zip|tar|7z|json|yaml|yml|xml|toml|config|jinja|j2|template|bst|model|ubj'"
- **Our assessment**: The broad filter is defensible for a *security* scan —
  ModelAudit scans config files and archives for embedded secrets, unsafe
  settings, and path traversal — but it makes the "changed model files" framing
  too narrow. A PR that only edits a YAML config or a JSON manifest still runs
  the scanner, which is a latency/cost surprise for the reviewer and a reason to
  keep the PR scan cheap (selected scanners, `--max-size`, timeout). It also
  means "no model files changed" is not the same as "no scan-worthy artifact
  changed." The guide should state the covered extensions explicitly rather than
  calling the gate "model scanning" without qualification.

### Claim 4: The PR workflow's gate is a `jq` predicate over all result JSON — fail on `has_errors`, any failed check, or critical/error findings — followed by a warning-count branch that exits 0
- **Evidence**: The "Check for critical issues" step runs
  `jq -es 'all(.[]; ... (.has_errors == false) and (.failed_checks == 0) and
  ([.checks[]? | select(.status == "failed")] | length == 0) and
  ([.issues[]? | select(.severity == "critical" or .severity == "error")] |
  length == 0))' scan_results/*.json`, then counts `severity == "warning"`
  findings and exits 0 if there are any.
- **Confidence**: emerging (the code is settled; the reachability of the
  warning branch depends on `failed_checks` semantics the page does not define)
- **Quote**: "WARNING_COUNT=$(jq -es '[.[] | .issues[]? | select(.severity == \"warning\")] | length' scan_results/*.json)"
- **Our assessment**: The *intent* is a warning-tolerant gate: critical/error
  findings and failed checks fail the job, warnings are reported but pass. The
  implementation has an unresolved sharp edge. The `jq -e` predicate also
  requires `.failed_checks == 0`; the page never says whether a warning
  increments `failed_checks`. If it does, the predicate is false for a
  warning-only result, and because GitHub runs `run:` steps with `bash -e`, the
  step aborts before the warning branch — so "exit 0 on warnings" would be
  unreachable. If warnings do not increment `failed_checks`, the branch works.
  Either way, the safer gate is to parse severity explicitly and decide the
  policy in the script, not to rely on an undocumented `failed_checks` counter.
  This is a concrete example of the #1995 gate-policy ambiguity at the workflow
  level.

### Claim 5: The SARIF workflow separates evidence production from failure — scan with `--format sarif --no-write` and `continue-on-error: true`, upload with `if: always()`, then fail in a separate step keyed on the scan step's outcome
- **Evidence**: The "Upload to GitHub Advanced Security" workflow:
  `permissions: security-events: write, contents: read`; `promptfoo scan-model
  models/ --no-write --format sarif --output modelaudit.sarif`; upload via
  `github/codeql-action/upload-sarif@v3` with `category: model-security`; final
  step `if: steps.scan.outcome == 'failure'` → `exit 1`.
- **Confidence**: settled (directly readable workflow)
- **Quote**: "Use SARIF format to integrate with GitHub Code Scanning:"
- **Our assessment**: Buy the shape — it is better than the PR workflow's
  warning branch because the upload runs even when the scan fails, and the
  failure decision is explicit rather than hidden in a `jq` exit. But it still
  does not distinguish findings from operational failure at the failure step:
  `steps.scan.outcome == 'failure'` is true for exit 1 (findings) **and** exit 2
  (operational error), so a warning-level finding fails the job. The distinction
  survives only in the SARIF content. Two further caveats: `if: always()` will
  try to upload even if the scan failed before writing `modelaudit.sarif`, which
  can produce a confusing upload-step error; and the third-party actions are
  floated on mutable tags (`upload-sarif@v3`), not pinned by SHA as the hardened
  code-scan action note requires (`docs-promptfoo-code-scan-github-action.md`,
  Claim 8). The `--no-write` flag is already documented on the parent page
  (`docs-promptfoo-model-audit.md`, Claim 4); cite it rather than treating it as
  new here.

### Claim 6: The scheduled workflow runs weekly (`0 2 * * 0`), uses `--strict --sbom`, tolerates a failing scan with `continue-on-error`, then opens a GitHub issue on non-clean results instead of failing a PR
- **Evidence**: The "Weekly Model Security Audit" workflow: `cron: '0 2 * * 0'
  # Sundays at 2 AM UTC` plus `workflow_dispatch`; scan step with
  `continue-on-error: true` and `--strict --sbom sbom.json`; a `check-issues`
  step that sets `critical=true` and exits 1 when the `jq` predicate fails; a
  `github-script` step gated on `if: failure() && steps.check-issues.outputs.
  critical == 'true'` that files an issue titled `🚨 Critical Model Security
  Issues Detected`.
- **Confidence**: settled for the workflow code; emerging for the operational
  outcome (the page gives no example of the issue it produces)
- **Quote**: "cron: '0 2 * * 0' # Sundays at 2 AM UTC"
- **Our assessment**: Buy the *pattern*: a scheduled scan should write findings
  to a durable, assignable surface (an issue) rather than block an unrelated PR.
  This is the model-artifact equivalent of the guide's runbook/audit cadence.
  The implementation has a naming/severity mismatch worth flagging: the issue
  title says "Critical" but the trigger is a **non-clean** result, and the scan
  runs `--strict`, so a warning-only result can open an issue that claims
  criticality. The body is more accurate ("Weekly security scan found non-clean
  results"). Operators should either separate warning and critical issues or
  retitle the issue. Also note the "Generate SBOM" step only echoes a message;
  the actual SBOM is produced by `--sbom sbom.json` in the scan step, so the
  step is cosmetic.

### Claim 7: The production gate triggers on pushes touching `models/production/**` and runs `--strict`, which fails on warnings or critical issues
- **Evidence**: The "Strict Mode for Production" workflow: `on: push: branches:
  [main]` with `paths: - 'models/production/**'`; `promptfoo scan-model
  models/production/ --strict --format json --output results.json`. The prose
  after it states the failure semantics.
- **Confidence**: settled (documented flag behavior and workflow trigger)
- **Quote**: "The scan step fails if strict mode finds warnings or critical issues."
- **Our assessment**: Buy the flag semantics; be precise about placement. This is
  a **post-merge** gate on `main`, not a pre-merge PR check. Unless branch
  protection requires the check (or a downstream deployment job depends on it),
  a bad model can merge and only then fail the production validation. The guide
  should present this as a promotion/deployment gate, not as the PR gate. It is
  also the strongest evidence for Side A of contradiction **#1995**:
  `--strict` makes warnings fatal, which is the opposite of the parent page's
  "findings ... don't necessarily block deployment" callout.

### Claim 8: GitLab CI aggregates per-file exit status by taking the maximum (`scan_status`), so an operational error on one file outranks findings on another, and retains results with `when: always` for 30 days
- **Evidence**: The `.gitlab-ci.yml` example: diff via
  `$CI_COMMIT_BEFORE_SHA..$CI_COMMIT_SHA`; per-file `file_status=$?`; max
  propagation `if [ "$file_status" -gt "$scan_status" ]; then
  scan_status=$file_status; fi`; `exit "$scan_status"`; `artifacts: paths:
  scan_results/`, `when: always`, `expire_in: 30 days`; `only: merge_requests`,
  `main`.
- **Confidence**: settled (directly readable configuration)
- **Quote**: "if [ \"$file_status\" -gt \"$scan_status\" ]; then scan_status=$file_status; fi"
- **Our assessment**: Buy the max-propagation — it is the correct aggregation
  for a tri-state contract: if one file has an operational error (2) and another
  has findings (1), the job exits 2 and preserves the "scan is broken" signal
  rather than downgrading it. `when: always` is also the right artifact policy;
  it avoids the CircleCI eval trap where a failing step skips the artifact
  upload (`docs-promptfoo-circleci-integration.md`, Claim 8). Two corrections to
  the Prospector brief: the page uses the legacy `only:` keyword, **not**
  `rules:`, and the install is unpinned (`apt-get install python3 python3-pip`,
  `npm install -g promptfoo`, `pip3 install modelaudit`). The job also scans the
  full diff on `main`, not just merge requests, because the diff range is the
  same in both cases.

### Claim 9: The Jenkins recipe is the only non-GitHub example with an explicit build failure — it captures the `jq` status with `returnStatus`, calls `error(...)` on critical/failed checks, and archives `scan_*.json` with `allowEmptyArchive`
- **Evidence**: The Jenkinsfile: changed-file diff against `HEAD~1 HEAD`; per-file
  `scan-model`; a `jq -es 'all(...)'` check run with `returnStatus: true`; `if
  (critical != 0) { error("Found model scan failures or critical security
  issues") }`; `post { always { archiveArtifacts artifacts: 'scan_*.json',
  allowEmptyArchive: true } }`.
- **Confidence**: settled (directly readable pipeline)
- **Quote**: "error(\"Found model scan failures or critical security issues\")"
- **Our assessment**: Buy the failure wiring — `returnStatus: true` plus
  `error()` is a clean separation of "inspect the result" from "fail the build,"
  and `allowEmptyArchive: true` keeps the job from failing again on a missing
  artifact. But the diff range is a real coverage gap: `HEAD~1 HEAD` only covers
  the last commit, so a multi-commit push can skip model files changed in earlier
  commits. It should diff the branch against its merge base, as the GitHub and
  GitLab examples do. The per-file scan status is also discarded; only the `jq`
  check gates. And the install is unpinned (`npm install -g promptfoo`,
  `pip install modelaudit`).

### Claim 10: The CircleCI recipe is artifact-only, not a gate — it scans changed models, appends JSON to `scan_results.json`, and stores artifacts, with no severity check or failure step
- **Evidence**: The `.circleci/config.yml` example: `cimg/node:lts`; install
  `npm install -g promptfoo` and `pip install modelaudit`; changed files from
  `git diff --name-only origin/main...HEAD`; per-file `promptfoo scan-model
  "$file" --format json >> scan_results.json`; `store_artifacts`; workflow
  filters `main` and `develop`. Nothing parses the JSON, counts findings, or
  exits non-zero.
- **Confidence**: settled (directly readable absence)
- **Quote**: "promptfoo scan-model \"$file\" --format json >> scan_results.json"
- **Our assessment**: Buy the absence, and treat it as the page's clearest
  inconsistency. The same page prescribes a fail-closed production gate with
  `--strict`, then ships a CircleCI recipe that cannot fail: a critical finding
  produces a green build and an artifact nobody may read. This is the "gate that
  cannot fail" failure class the guide already names (`guide/05-llm-ops-
  reliability.md:655`; `docs-promptfoo-github-action.md`, Claim 1;
  `docs-promptfoo-aws-codecommit-codebuild.md`, Claims 4–6). Two technical
  caveats: `>>` concatenates multiple JSON documents into one file, which is not
  a single valid JSON document and will break a naive `jq` consumer; and the
  recipe installs `modelaudit` with `pip` in a `cimg/node` image without the
  Python setup step the GitLab recipe includes, so the install may fail
  depending on the image. The guide should not present this as a model-security
  gate; it is a report-only example.

### Claim 11: Every example installs Promptfoo/ModelAudit unpinned (`npm install -g promptfoo`, `pip install modelaudit` or `[all]`) and floats third-party actions on mutable tags — the opposite of the hardened code-scan action
- **Evidence**: Across all workflows: `npm install -g promptfoo`; `pip install
  modelaudit` / `pip install modelaudit[all]`; `uses:` tags including
  `actions/checkout@v4`, `actions/setup-node@v4`, `actions/setup-python@v5`,
  `actions/upload-artifact@v4`, `actions/github-script@v7`,
  `github/codeql-action/upload-sarif@v3`, `actions/cache@v3`,
  `nick-fields/retry@v2`, and `slackapi/slack-github-action@v1`.
- **Confidence**: settled (directly readable configuration)
- **Quote**: "npm install -g promptfoo"
- **Quote**: "pip install modelaudit[all]"
- **Our assessment**: Buy it, and this is the highest-value supply-chain point in
  the note. The page's whole purpose is gating on security findings, yet its
  install path resolves `latest` with npm lifecycle scripts enabled, and its
  GitHub examples float actions on mutable tags. The hardened code-scan action
  does the opposite — exact release-pinned CLI, `--ignore-scripts`, build-
  provenance attestation, and full-SHA pins (`docs-promptfoo-code-scan-github-
  action.md`, Claims 2 and 8). The same unpinned pattern is already recorded in
  the eval-era non-Action recipes (`docs-promptfoo-aws-codecommit-codebuild.md`,
  Claim 13; `docs-promptfoo-jenkins-integration.md`, Claim 4;
  `docs-promptfoo-circleci-integration.md`, Claim 2). For the guide, the scanner
  is itself a CI dependency: if the unpinned `promptfoo`/`modelaudit` install or
  a mutable `upload-sarif` tag is compromised, the gate is compromised. Copy the
  workflow *shape*, not the install lines; pin the CLI and every action to a
  resolved SHA, and apply the guide's cooldown rule
  (`failure-litellm-supply-chain-incident-march-2026.md`, Claim 14).

### Claim 12: The best-practice scan strategy is tiered — changed files on PRs, comprehensive scans on merge, weekly/daily full audits, and a `--strict` production gate — with cache, parallel `xargs`, timeout, retry, and Slack notification patterns
- **Evidence**: The "Best Practices" section: four scan-strategy bullets; a
  cache example keyed on `package-lock.json`/`requirements.txt`; a parallel scan
  using `xargs -0 -P 4`; a security checklist (encrypted secrets, read-only
  tokens, rotation, access audit); `--timeout 1800 --verbose` for 8GB+ models; a
  `nick-fields/retry@v2` example with `max_attempts: 3`; and a Slack
  notification step on failure.
- **Confidence**: settled for the vendor guidance; emerging for its
  effectiveness (no runtime, false-positive, or field data on the page)
- **Quote**: "**Pull Requests**: Scan only changed files for fast feedback"
- **Quote**: "**Production Gate**: Use `--strict` mode to block deployments"
- **Our assessment**: Buy the tiering as a sound default shape: fast, diff-scoped
  PR feedback; comprehensive coverage on merge; scheduled full audits for drift
  and newly disclosed CVEs; and a strict promotion gate. The page gives no
  measured latency or detection data, so the guide should mark the tiering
  *emerging* and not present `--timeout 1800`, `xargs -P 4`, or cache keys as
  validated budgets. Two inconsistencies: the parallel example scans only
  `*.pkl` (`find models/ -name "*.pkl"`), which is narrower than the PR
  workflow's extension list; and its `--output {}.json` writes result files next
  to the models, which can pollute the checkout. The security checklist
  (encrypted secrets, read-only tokens, rotation, access audit) is generic
  hygiene, not model-scan-specific.

### Claim 13: The troubleshooting section exposes `--verbose`, `--max-size`, and `--dry-run` as first-line controls — and `--max-size` silently bounds coverage, so a "clean" capped scan is not a safety statement
- **Evidence**: The "Troubleshooting" section: `promptfoo scan-model models/
  --verbose`; `promptfoo scan-model models/ --max-size 1GB`; `promptfoo
  scan-model models/ --dry-run` ("Preview scan without processing").
- **Confidence**: settled (documented flags)
- **Quote**: "# Preview scan without processing"
- **Our assessment**: Buy the flags, but do not treat them as new CLI surface:
  they are already on the parent page's options table
  (`docs-promptfoo-model-audit.md`, Claim 4). The CI-specific value is
  operational: `--dry-run` lets a team validate the workflow's file selection
  before paying scan cost, and `--max-size` stops a pathological artifact from
  hanging the job. The caveat is the same one the parent note records for lean
  scanner images: a file above the cap is not scanned, so a clean result on a
  capped scan is a coverage statement, not evidence that the artifact is safe.
  Put the cap in the gate's written scope, not in a silent flag.

## Concrete Artifacts

### Exit-code contract (verbatim from "Exit Codes")

```
0: No security issues found ✅
1: Security issues detected (warnings or critical findings) 🟡
2: Operational errors or inconclusive scans (file access, installation, timeouts, or no scanned files) 🔴
```

> In CI/CD pipelines, exit code 1 indicates findings that should be reviewed.
> Only exit code 2 represents actual scan failures.

Source: docs page, "Exit Codes". The callout is the source of the #1995
tension; see Cross-References.

### Changed-file extension filter (verbatim from the GitHub/GitLab/Jenkins examples)

```
MODEL_EXTENSIONS='pkl|pickle|dill|pth|pt|ckpt|checkpoint|orbax-checkpoint|h5|hdf5|keras|onnx|pb|tflite|safetensors|gguf|ggml|ggmf|ggjt|ggla|ggsa|bin|engine|plan|msgpack|flax|orbax|jax|joblib|skops|npy|npz|pmml|zip|tar|7z|json|yaml|yml|xml|toml|config|jinja|j2|template|bst|model|ubj'
```

Source: docs page, "GitHub Actions → Scan Changed Model Files" (also GitLab and
Jenkins). The list is identical across the three recipes.

### GitHub Actions PR gate — key steps (condensed from "Scan Changed Model Files")

```yaml
name: Model Security Scan
on:
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  scan-models:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install Promptfoo and ModelAudit
        run: |
          npm install -g promptfoo
          pip install modelaudit
      - name: Get changed model files
        id: changed-files
        run: |
          CHANGED=$(git diff --name-only --diff-filter=ACM \
            ${{ github.event.pull_request.base.sha }} ${{ github.sha }} | \
            grep -Ei "\.(${MODEL_EXTENSIONS})$" || true)
          # writes has_changes / changed_files.txt
      - name: Scan changed models
        if: steps.changed-files.outputs.has_changes == 'true'
        run: |
          while IFS= read -r file; do
            if [ -f "$file" ]; then
              report_id=$(printf '%s' "$file" | sha256sum | cut -d ' ' -f1)
              promptfoo scan-model "$file" \
                --format json \
                --output "scan_results/${report_id}.json" || true
            fi
          done < changed_files.txt
      - name: Check for critical issues
        if: steps.changed-files.outputs.has_changes == 'true'
        run: |
          jq -es 'all(.[]; ... (.has_errors == false) and (.failed_checks == 0)
            and ([.checks[]? | select(.status == "failed")] | length == 0)
            and ([.issues[]? | select(.severity == "critical" or .severity == "error")] | length == 0))' \
            scan_results/*.json >/dev/null
          WARNING_COUNT=$(jq -es '[.[] | .issues[]? | select(.severity == "warning")] | length' scan_results/*.json)
          if [ "$WARNING_COUNT" -gt 0 ]; then
            echo "⚠️  Found warnings in $WARNING_COUNT file(s)"
            exit 0
          fi
```

Source: docs page, "GitHub Actions → Scan Changed Model Files". Condensed: the
artifact-upload step and the full `jq` predicate are elided; the `...` marks the
elision. The `|| true` on each scan and the warning-count branch are as
published.

### SARIF upload to GitHub Code Scanning (condensed from "Upload to GitHub Advanced Security")

```yaml
jobs:
  scan-models:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Scan models directory
        id: scan
        continue-on-error: true
        run: |
          promptfoo scan-model models/ \
            --no-write \
            --format sarif \
            --output modelaudit.sarif
      - name: Upload SARIF to GitHub
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: modelaudit.sarif
          category: model-security
      - name: Fail if scan found issues or errors
        if: steps.scan.outcome == 'failure'
        run: exit 1
```

Source: docs page, "GitHub Actions → Upload to GitHub Advanced Security".
Condensed: install/setup steps omitted.

### Scheduled audit that files an issue (condensed from "Scheduled Security Scans")

```yaml
name: Weekly Model Security Audit
on:
  schedule:
    - cron: '0 2 * * 0' # Sundays at 2 AM UTC
  workflow_dispatch:
jobs:
  comprehensive-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Comprehensive model scan
        continue-on-error: true
        run: |
          promptfoo scan-model models/ \
            --format json \
            --output scan_results.json \
            --strict \
            --sbom sbom.json
      - name: Check for critical issues
        id: check-issues
        run: |
          if ! jq -e '... (.has_errors == false) and (.failed_checks == 0)
            and ([.checks[]? | select(.status == "failed")] | length == 0)
            and ([.issues[]? | select(.severity == "critical" or .severity == "error")] | length == 0)' \
            scan_results.json >/dev/null; then
            echo "critical=true" >> $GITHUB_OUTPUT
            exit 1
          fi
      - name: Create issue if scan fails closed
        if: failure() && steps.check-issues.outputs.critical == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            // reads scan_results.json, filters critical/error,
            // creates an issue titled
            // '🚨 Critical Model Security Issues Detected'
```

Source: docs page, "GitHub Actions → Scheduled Security Scans". Condensed:
install/setup and the full `github-script` body omitted. Note the issue title
says "Critical" while the trigger is any non-clean result (see Claim 6).

### Production strict gate (condensed from "Strict Mode for Production")

```yaml
name: Production Model Validation
on:
  push:
    branches: [main]
    paths:
      - 'models/production/**'
jobs:
  strict-validation:
    runs-on: ubuntu-latest
    steps:
      - name: Strict security scan
        run: |
          promptfoo scan-model models/production/ \
            --strict \
            --format json \
            --output results.json
```

Source: docs page, "GitHub Actions → Strict Mode for Production". Condensed:
setup/install steps omitted. This is a post-merge gate on `main`.

### GitLab CI — exit-status aggregation and artifacts (key lines from "GitLab CI")

```yaml
model-security-scan:
  stage: test
  image: node:24
  before_script:
    - apt-get update && apt-get install -y python3 python3-pip
    - npm install -g promptfoo
    - pip3 install modelaudit
  script:
    - |
      CHANGED=$(git diff --name-only --diff-filter=ACM $CI_COMMIT_BEFORE_SHA $CI_COMMIT_SHA | \
        grep -Ei "\.(${MODEL_EXTENSIONS})$" || true)
      if [ -n "$CHANGED" ]; then
        scan_status=0
        while IFS= read -r file; do
          file_status=0
          promptfoo scan-model "$file" \
            --format json \
            --output "scan_results/${report_id}.json" || file_status=$?
          if [ "$file_status" -gt "$scan_status" ]; then scan_status=$file_status; fi
        done < changed_files.txt
        exit "$scan_status"
      fi
  artifacts:
    paths:
      - scan_results/
    when: always
    expire_in: 30 days
  only:
    - merge_requests
    - main
```

Source: docs page, "GitLab CI". Condensed: the file-list write and the
`report_id` line are elided. Note the legacy `only:` keyword and the unpinned
install.

### Jenkins — `returnStatus` + `error()` (key lines from "Jenkins")

```groovy
stage('Scan Models') {
    steps {
        script {
            def changed = sh(
                script: '''
                    MODEL_EXTENSIONS='...'
                    git diff --name-only HEAD~1 HEAD | \
                    grep -Ei "\\.(${MODEL_EXTENSIONS})$" || true
                ''',
                returnStdout: true
            ).trim()
            if (changed) {
                changed.split('\n').each { file ->
                    sh 'promptfoo scan-model "$MODEL_FILE" --format json --output "$REPORT_FILE"'
                }
                def critical = sh(
                    script: '''jq -es 'all(.[]; ...)' scan_*.json >/dev/null''',
                    returnStatus: true
                )
                if (critical != 0) {
                    error("Found model scan failures or critical security issues")
                }
            }
        }
    }
}
post {
    always {
        archiveArtifacts artifacts: 'scan_*.json', allowEmptyArchive: true
    }
}
```

Source: docs page, "Jenkins". Condensed: install stage, `withEnv` wrapper, and
the full `jq` predicate are elided; the failure call and artifact step are as
published.

### CircleCI — artifact-only recipe (key lines from "CircleCI")

```yaml
version: 2.1
jobs:
  model-scan:
    docker:
      - image: cimg/node:lts
    steps:
      - checkout
      - run:
          name: Install tools
          command: |
            npm install -g promptfoo
            pip install modelaudit
      - run:
          name: Scan changed models
          command: |
            CHANGED=$(git diff --name-only origin/main...HEAD | \
              grep -Ei "\.(${MODEL_EXTENSIONS})$" || true)
            if [ -n "$CHANGED" ]; then
              echo "$CHANGED" | while read -r file; do
                if [ -f "$file" ]; then
                  promptfoo scan-model "$file" --format json >> scan_results.json
                fi
              done
            fi
      - store_artifacts:
          path: scan_results.json
          destination: model-scan-results
workflows:
  security:
    jobs:
      - model-scan:
          filters:
            branches:
              only:
                - main
                - develop
```

Source: docs page, "CircleCI". Condensed: the `MODEL_EXTENSIONS` definition is
elided. There is no severity check, no `jq`, and no failure step — this recipe
stores an artifact and always passes (see Claim 10).

### Performance, timeout, and retry snippets (verbatim from "Best Practices")

```yaml
# Parallel scanning
- name: Parallel scan
  run: |
    find models/ -name "*.pkl" -print0 | \
      xargs -0 -P 4 -I {} promptfoo scan-model {} --format json --output {}.json
```

```yaml
- name: Scan large model
  run: |
    promptfoo scan-model large_model.bin \
      --timeout 1800 \
      --verbose \
      --format json \
      --output results.json
```

```yaml
- name: Scan with retry
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: promptfoo scan-model models/ --format json --output results.json
```

Source: docs page, "Best Practices → Performance / Timeout Configuration /
Retry Logic". Note the parallel example scans only `*.pkl`, narrower than the
PR workflow's extension list.

## Cross-References

### Candidate notes from `miner-related-notes.md` — cite or dismiss

1. `source-notes/docs-promptfoo-evaluate-coding-agents.md` — agent-eval
   workspace isolation and trajectory CI. No overlap with model-file scanning.
   **Dismiss**.
2. `source-notes/docs-promptfoo-enterprise-guardrails.md` — runtime guardrail
   enforcement (HTTP endpoint, placements, aggregate `action`). Different
   security layer from static model-artifact scanning. **Dismiss**.
3. `source-notes/docs-litellm-evals-api.md` — LiteLLM Evaluations API. No
   overlap. **Dismiss**.
4. `source-notes/docs-litellm-batches-api.md` — LiteLLM batch rate limiting.
   No overlap. **Dismiss**.
5. `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **Extends**:
   its Claim 4 documents SARIF as an export format with "no upload step, no CI
   job, and no build-blocking behavior"; this page supplies the concrete
   `upload-sarif` + failure-step wiring for model-scan findings. Different
   artifact type, same missing-bridge problem.
6. `source-notes/docs-promptfoo-model-audit.md` — **Extends**: the sibling
   landing-page note explicitly defers the CI/CD workflow YAML and PR-vs-
   scheduled scanning to this child page (its Source Context). Cite its Claim 4
   for the read-only flags (`--no-write`, `--timeout`, `--max-size`), Claim 8
   and contradiction **#1995** for the exit-1 gate-policy tension, Claim 9 for
   the "no scanned files = exit 2" gotcha, and Claim 10 for install variants and
   the mutable-`latest*`-tag pin rule.
7. `source-notes/blog-pagerduty-sre-agent-triage.md` — AI incident triage. No
   overlap. **Dismiss**.
8. `source-notes/docs-promptfoo-pi-scorer.md` — model-graded Pi scorer. No
   overlap. **Dismiss**.
9. `source-notes/docs-google-sre-reliable-product-launches.md` — launch
   coordination engineering. No overlap with model-file scanning. **Dismiss**.
10. `source-notes/docs-google-sre-team-lifecycles.md` — SRE team lifecycles.
    No overlap. **Dismiss**.

### Cross-references against existing notes

- **Corroborates**:
  - `docs-promptfoo-aws-codecommit-codebuild.md`, Claim 13 — the non-Action
    CI path installs the scanner unpinned, the opposite of the hardened GitHub
    Action. This page extends that observation from eval recipes to model-scan
    recipes: every recipe here uses `npm install -g promptfoo` and `pip install
    modelaudit` without a version.
  - `docs-promptfoo-circleci-integration.md`, Claim 2 — the CircleCI eval
    recipe floats `cimg/node:lts` and installs `promptfoo` globally and
    unpinned. This page's CircleCI model-scan recipe does the same.
  - `docs-promptfoo-jenkins-integration.md`, Claim 4 — the Jenkins eval recipe
    uses an unpinned global npm install. This page's Jenkins model-scan recipe
    does the same and adds an explicit `error()` gate.
- **Contradicts**:
  - **#1995** — the exit-1 gate-policy contradiction already filed against
    `docs-promptfoo-model-audit.md` (Claim 8) and
    `blog-promptfoo-open-sourcing-modelaudit.md` (Guide Impact: "Gate production
    deployments with `--strict` mode"). This page supplies both sides: the
    "only exit 2 represents actual scan failures" callout (Claim 1), and the
    `--strict` production gate plus the critical/error failure steps (Claims 4,
    5, 7). No new contradiction is filed; this note adds evidence for Side A
    (block on severe findings / `--strict`) and Side B (findings need not block)
    without asserting a verdict.
  - **Internal inconsistency, not filed**: the CircleCI recipe (Claim 10) is
    artifact-only while the rest of the page prescribes fail-closed gates. This
    is a gap in the vendor's recipe, not a claim-vs-claim contradiction with
    another source note.
- **Extends**:
  - `blog-promptfoo-open-sourcing-modelaudit.md`, Claim 12 and Concrete
    Artifacts — the blog note records SARIF/SBOM capability and the exit-code
    triad; this page supplies the actual CI YAML, the SARIF upload step, the
    scheduled audit, and the path-scoped production gate. Cite the blog note for
    the security rationale, not for the workflow detail.
  - `docs-promptfoo-code-scan-github-action.md`, Claim 5 — the code-scan Action
    sets `sarif-path` only when a scan completes, so an unguarded upload can
    publish a false clean. This page's model-scan SARIF workflow uses
    `if: always()` with `continue-on-error: true` and a separate failure step,
    which keeps the job from going green on failure but can still attempt an
    upload when no SARIF was written. Cite the code-scan note for the
    completion-signal rule and this note for the model-artifact variant.
  - `docs-promptfoo-code-scan-github-action.md`, Claims 2 and 8 — the hardened
    code-scan Action's pinned CLI, `--ignore-scripts`, provenance attestation,
    and full-SHA action pins are the contrast case for this page's unpinned
    installs and mutable action tags (Claim 11).
  - `docs-promptfoo-github-action.md`, Claims 1 and 11 — that page's eval
    integration is a report, not a gate; this page's CircleCI model-scan recipe
    is the model-artifact instance of the same "gate that cannot fail" pattern.
  - `docs-promptfoo-jenkins-integration.md`, Claim 6 — the Jenkins eval recipe
    has no SARIF/security-gate artifacts or exit-code threshold. This page's
    Jenkins recipe adds a `jq` + `error()` model-scan gate, but still no SARIF
    output or documented threshold; the scan target is different (model files
    vs evals).
  - `docs-promptfoo-circleci-integration.md`, Claim 8 — that note records the
    trap where `store_artifacts` after a failing eval step skips the artifact on
    exactly the red runs. This page's GitLab (`when: always`) and GitHub
    (`if: always()`) examples show the fix; its CircleCI model-scan recipe uses
    `store_artifacts` after the scan with no `when: always`, so the same trap
    remains possible if the recipe is extended with a failing gate.
  - `failure-litellm-supply-chain-incident-march-2026.md`, Claim 14 — pin
    verified SHAs and add an upgrade cooldown. This page's unpinned scanner
    installs and mutable action tags are exactly the exposure that rule targets;
    because the scanner is the gate, a compromised scanner compromises the
    security decision.
- **Novel**:
  - The multi-CI (GitLab/Jenkins/CircleCI) model-file scan wiring — no existing
    note carries it.
  - The SARIF-to-GitHub-Code-Scanning workflow for model artifacts, with
    `continue-on-error` on the scan and a separate outcome-keyed failure step.
  - The weekly scheduled audit that auto-files a GitHub issue on non-clean
    results instead of failing a PR.
  - The path-scoped `--strict` production gate on `models/production/**`.
  - GitLab's maximum-per-file-exit-status aggregation as a tri-state-preserving
    gate.
  - The changed-file extension list's inclusion of config and archive formats,
    which makes "changed model files" broader than model weights.
  - The CircleCI model-scan recipe that is artifact-only and cannot fail.

## Guide Impact

- **Chapter 06 §Gating on LLM security scans** (`guide/06-security-and-trust.md:768`):
  Add a **model-artifact gate** subsection parallel to the existing code-scan
  gate. Use Claim 1 for the tri-state contract and Claim 9 for the "no scanned
  files = exit 2" rule: a gate must fail on exit 2, not treat it as a clean
  result, and must not reduce the contract to `exit == 1`. Present the gate
  policy as severity-filtered (hard-fail exit 2; fail on CRITICAL/ERROR from the
  parsed JSON; decide WARNING separately) **pending the #1995 verdict**; do not
  copy either the parent page's "findings need not block" callout or the
  `--strict` production gate as the universal default. Use Claim 5's SARIF
  workflow as the concrete pattern for publishing findings to GitHub Code
  Scanning, and Claim 6's scheduled audit as the pattern for reporting drift to
  an issue rather than blocking unrelated PRs.
- **Chapter 06 §Supply-chain security for LLM infrastructure**
  (`guide/06-security-and-trust.md:634`): Add the rule that **the scanner is a
  CI dependency**. The page's model-scan recipes install `promptfoo` and
  `modelaudit` unpinned and float `upload-sarif`/`checkout`/`setup-*` on mutable
  tags (Claim 11); a compromised scanner or upload action invalidates the gate.
  Pair the model-scan stage with the existing pin-and-attest rules
  (`docs-promptfoo-code-scan-github-action.md`, Claims 2 and 8;
  `failure-litellm-supply-chain-incident-march-2026.md`, Claim 14), and pin the
  scanner image/CLI by digest or exact version rather than copying the vendor's
  `npm install -g` / `pip install` lines.
- **Chapter 05 §CI/CD supply-chain isolation**
  (`guide/05-llm-ops-reliability.md:1359`): Add model-artifact scanning as a
  pipeline stage. Use Claim 12's tiering (changed files on PRs; comprehensive
  scan on merge; weekly/daily audit; `--strict` promotion gate) and Claim 8's
  GitLab `when: always` artifact retention. Use Claim 10 as a cautionary example:
  a "scan" stage that only stores an artifact is not a gate. Prefer the
  GitLab/Jenkins fail-closed shapes over the CircleCI report-only shape, and
  keep the failure artifacts available on red runs.
- **Chapter 05 §A gate that cannot fail is not a gate**
  (`guide/05-llm-ops-reliability.md:655`): Add the CircleCI model-scan recipe as
  a worked example of the failure class — it scans, appends JSON, stores an
  artifact, and always passes (Claim 10). Pair it with the GitHub PR gate
  (Claims 2–4) and the GitLab max-status aggregation (Claim 8) as the
  fail-closed alternatives.
- **Chapter 03 (Runbooks & Agents)**: Add a scheduled-audit runbook pattern:
  weekly `--strict --sbom` scan, retained artifacts, an auto-filed issue on
  non-clean results, a Slack notification on critical findings, and `--timeout`
  / retry / `--max-size` controls for large models (Claims 6, 12, 13). Note the
  issue-title severity mismatch (Claim 6) so responders do not assume every
  filed issue is critical.

## Extraction Notes

- Source fetched 2026-11-03 from the live page. It is living vendor
  documentation with no publish date; `date_published` is `null` and workflow
  text is recorded as of the extraction date (footer: last updated 2026-11-03
  by dependabot[bot]). The page is a single self-contained docs page; no
  substantive sub-pages were followed — its "Next Steps" links to
  `/docs/model-audit/scanners` (#1950), `/docs/model-audit/usage`, and
  `/docs/model-audit/`, which are separate issues/notes.
- Per the Prospector brief, this is a **delta extraction**: I did not re-derive
  the pickle-RCE threat model, blocklist-vs-allowlist analysis, GHSAs, format
  coverage, or detection-rate comparisons (settled in
  `blog-promptfoo-open-sourcing-modelaudit.md`, #553). The exit-code triad is
  restated only because it is the contract the CI recipes consume; it is
  already in #553's Concrete Artifacts and #1948's Claims 8–9. The new material
  is the per-CI wiring and its gaps.
- **Correction to the Prospector brief**: the GitLab example uses the legacy
  `only:` keyword, not `rules:`. The brief also described "per-file exit status
  aggregation"; that is present, and I extracted the `scan_status` max-
  propagation specifically.
- **No new contradiction filed.** The gate-policy tension on this page is the
  same one already tracked in **#1995** (exit-1 findings vs. `--strict`/fail-on-
  critical). This page adds concrete workflow evidence for both sides but does
  not create a new claim conflict. The CircleCI artifact-only recipe vs. the
  page's own fail-closed advice is an internal inconsistency in a vendor recipe,
  not a cross-source contradiction; I recorded it under Claim 10 and did not
  file it.
- **Unverified operational inference (flagged, not asserted):** the PR
  workflow's warning-tolerant branch may be unreachable because `jq -e`'s
  predicate includes `.failed_checks == 0` and GitHub runs `run:` steps with
  `bash -e`; the page never defines `failed_checks`. I treat this as a caveat
  for implementers, not a vendor claim. The scheduled workflow's "Generate
  SBOM" step is cosmetic (the SBOM is produced by `--sbom`), and the issue
  title's "Critical" label overstates the non-clean trigger; both are noted in
  the relevant claims.
- Quotes were copied character-for-character from the rendered page. The fetch
  conversion collapsed the YAML/Groovy code blocks onto single lines, so code
  indentation and line breaks in Concrete Artifacts were reconstructed to be
  valid; command, flag, and expression text is unchanged. The extension regex
  and the short shell/Groovy quotes are verbatim.
- `confidence_overall` is **emerging**: the workflow shape, flags, and exit
  codes are documented and string-checkable (settled as a spec), but there is no
  independent validation of detection quality, runtime, or false positives; the
  page is drift-prone living docs; and its own recipes disagree on gate policy
  (report-only CircleCI vs. `--strict` production) and supply-chain posture
  (unpinned installs vs. the hardened code-scan action).
- Candidate file read before writing Cross-References; all 10 listed paths were
  either cited or explicitly dismissed. Every cited `Claim N` was re-read in the
  cited note per MINER.md §4b. No source-note PR includes `registry/*` changes;
  the derived indexes are left to the post-merge rebuild.
