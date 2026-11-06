---
source_url: https://www.promptfoo.dev/docs/model-audit/usage
source_type: docs
title: "Promptfoo ModelAudit — Advanced Usage: The Env-Var Remote-Auth Contract, Finding Accounting, and the SARIF/SBOM Output Surface"
author: "Promptfoo (vendor documentation)"
date_published: null
date_extracted: 2026-11-06
last_checked: 2026-11-06
status: current
confidence_overall: emerging
issue: "#1960"
---

# Promptfoo ModelAudit — Advanced Usage

> The operator-facing companion to the ModelAudit docs section. Its novel deltas
> are the credential channel (remote auth is now environment-variables-only,
> with the old CLI flags removed), the JSON/SARIF output contracts a gate has to
> consume (`issues` vs `checks`, and `success`/`has_errors` as execution
> signals rather than finding verdicts), default-on cloud result sharing, and
> the programmatic/pre-commit/custom-scanner extension surfaces. The CI recipes
> overlap the dedicated `/docs/model-audit/ci-cd` page; this page supplies a
> distinct two-layer GitLab variant and a path-triggered GitHub example with
> operational gaps.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "Model Audit >
  Advanced Usage" page). Living docs; no publish date is shown. Footer: "Last
  updated on **Nov 6, 2026** by **Michael**".
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team/security
  vendor. First-party documentation of its own `promptfoo scan-model` wrapper and
  the `modelaudit` package. Authoritative as a *specification* of env-var names,
  flag removals, output formats, and example wiring — all string-checkable
  against the installed CLI and the linked JSON schema/example. Not measurement:
  the page publishes no detection rate, false-positive rate, runtime benchmark,
  or field evidence for its gating recommendations.
- **Scope**: Covers cloud/artifact-registry authentication, migration from
  removed credential flags, remote scanning (HF/cloud/registries/DVC),
  configuration flags and result sharing, CI/CD recipes (GitHub Actions, GitLab
  CI, pre-commit), programmatic Python usage, JSON output accounting, SARIF
  2.1.0 output and severity mapping, SBOM generation, troubleshooting, and
  custom-scanner extension. Does **not** re-derive the pickle-RCE threat model,
  blocklist-vs-allowlist architecture, GHSAs, format coverage, scanner internals,
  or detection-rate comparisons — those are settled in
  `blog-promptfoo-open-sourcing-modelaudit.md` (#553),
  `docs-promptfoo-model-audit.md` (#1948), and
  `docs-promptfoo-model-audit-scanners.md` (#1950).
- **Relationship to sibling pages**: the parent landing-page note explicitly
  defers remote-source *authentication* to this page, and the CI/CD child note
  owns the fuller per-CI workflow detail. This note is a delta extraction: the
  new material is the auth contract, the output/accounting contract, the sharing
  default, and the programmatic/extension surfaces.

## Extracted Claims

### Claim 1: Remote authentication is now environment-variables-only — every remote source has a documented env-var contract, including private-model access, and the page says this is the sole supported channel
- **Evidence**: The opening of "Authentication and Configuration" and the
  per-provider subsections: `HF_TOKEN` for private Hugging Face models;
  `JFROG_URL` plus `JFROG_API_TOKEN` or `JFROG_ACCESS_TOKEN`; `MLFLOW_TRACKING_URI`
  plus `MLFLOW_TRACKING_USERNAME` / `MLFLOW_TRACKING_PASSWORD`; standard
  `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_DEFAULT_REGION` for S3;
  `GOOGLE_APPLICATION_CREDENTIALS` for GCS; and the AWS credential plus
  `AWS_ENDPOINT_URL` pair for Cloudflare R2.
- **Confidence**: settled (documented env-var names; checkable against the
  installed CLI)
- **Quote**: "Authentication for all remote services is now handled exclusively via environment variables."
- **Our assessment**: Buy it as the contract the parent note deferred. The
  SRE-relevant point is that the scanner gate's credentials now live in the
  runner/secret store, not in the command line — and each remote fetches under a
  different provider's SDK credential chain (AWS for S3/R2, Google ADC for GCS,
  MLflow's own vars, JFrog's URL+token). The page does not describe credential
  scoping (read-only? path-scoped?) or precedence between the two JFrog token
  variables, so the guide should present this as "declare the env var" rather
  than "the scanner enforces least privilege."

### Claim 2: The old credential CLI flags were removed, not deprecated — using them errors — and the stated rationale is preventing exposure in shell history and process lists
- **Evidence**: "Migration from Deprecated Flags" lists `--jfrog-api-token` →
  `JFROG_API_TOKEN`, `--jfrog-access-token` → `JFROG_ACCESS_TOKEN`, and
  `--registry-uri` → `JFROG_URL` or `MLFLOW_TRACKING_URI`, and states use of the
  removed flags is an error.
- **Confidence**: settled (documented migration table and explicit error claim)
- **Quote**: "The following CLI flags have been removed and replaced by environment variables. Attempting to use them will result in an error."
- **Quote (rationale)**: "Using environment variables is more secure than passing secrets as CLI flags, as it prevents them from being exposed in shell history or process lists. This aligns with industry best practices for managing credentials."
- **Our assessment**: Buy it, and it is the concrete credential-channel instance
  for the guide's "declare, don't infer" section: `argv` is a public broadcast
  on most hosts (`ps aux`, shell history, CI logs), so a secret passed as a flag
  is leaked by default. Replacing the flag with an env var fixes the *channel*;
  it does not by itself make credential *selection* explicit, because the page
  still relies on ambient provider chains (`AWS_*`, ADC). That distinction is
  worth preserving in the guide.

### Claim 3: When Promptfoo Cloud is connected, model-audit results are shared automatically by default, with `--share` / `--no-share` and a global `PROMPTFOO_DISABLE_SHARING` switch
- **Evidence**: "Configuration Options → Sharing Results": results are shared
  automatically when cloud is enabled; `--share` explicitly enables, `--no-share`
  disables for one scan, and `PROMPTFOO_DISABLE_SHARING=true` disables globally.
- **Confidence**: settled (documented default and controls)
- **Quote**: "When connected to promptfoo Cloud, model audit results are automatically shared by default. This provides a web-based interface to view, analyze, and collaborate on scan results."
- **Our assessment**: Buy it, and treat it as a data-governance hazard rather
  than a convenience. Model-audit results carry file paths, content hashes,
  scanner findings, and arbitrary `details`/`file_metadata`; a CI runner holding
  private-model access may be shipping that metadata to a third party without an
  explicit opt-in. The default is the opposite of fail-closed. A gate for private
  artifacts should set `--no-share` or `PROMPTFOO_DISABLE_SHARING=true`
  deliberately, especially in regulated or air-gapped pipelines. This is new
  relative to the blog note's "runs entirely offline" focus, which is about the
  scan engine, not result egress.

### Claim 4: ModelAudit has no configuration-file support — scan policy lives in CLI flags, and `--blacklist` is a repeated *name* pattern, not a vulnerability policy
- **Evidence**: "Configuration Options" states config files are not currently
  supported; all examples are CLI flags. The blacklist example passes model-name
  patterns (`deepseek`, `qwen`, `unsafe_model`) and resource limits
  (`--max-size 1GB`, `--timeout 600`).
- **Confidence**: settled (documented absence plus examples)
- **Quote**: "While configuration files are not currently supported, you can achieve similar results using CLI flags:"
- **Our assessment**: Buy the absence. The operational consequence is that scan
  policy is not a versioned artifact: scanner selection, severity handling,
  blacklist, size, and timeout are re-declared in every CI job, so drift between
  jobs is invisible and review of "what we scan for" has to read YAML, not a
  config file. Also do not over-read `--blacklist`: blacklisting a vendor or
  product name is a governance/policy filter (e.g. "don't allow this model
  family"), not a detection control — it does not make the scanner find more
  vulnerabilities, and treating the name list as a security boundary would be a
  category error.

### Claim 5: The JSON output has a two-array finding contract — `issues` are findings, `checks` are performed checks and may repeat a finding as a failed check, so counting both double-counts
- **Evidence**: "JSON Output Format" states the result includes scan statistics,
  assets, file metadata, `issues`, and `checks`, and gives the accounting rule.
  It also tells consumers to tolerate omitted optional fields and new
  scanner-specific fields. The page links a JSON Schema and an example result.
- **Confidence**: settled (documented contract plus a linked schema/example)
- **Quote**: "Treat `issues` as findings. `checks` records performed checks and may include a failed check for the same finding, so do not count both arrays as separate findings."
- **Quote (schema drift)**: "Consumers should tolerate omitted optional fields and new scanner-specific fields, especially within `details` and `file_metadata`."
- **Our assessment**: Buy it. This is a metric-definition hazard: a dashboard
  that sums `len(issues) + len(checks where status == failed)` doubles the count,
  and an error-budget or trend line built that way is wrong from day one. It also
  means the two arrays answer different questions — `issues` is "what is wrong,"
  `checks` is "what was verified" — so coverage (`checks`) and findings
  (`issues`) should be reported separately, never collapsed. The schema-drift
  instruction is a warning against exhaustive parsing: a gate must select the
  fields it needs, not reject unknown ones.

### Claim 6: The result's top-level `success` / `has_errors` are execution-status signals, not finding verdicts — the vendor's own example carries a `critical` issue while both are clean, so a gate keyed on `success` would pass a critical finding
- **Evidence**: The linked example result
  (`modelaudit-scan-result.example-...json`, fetched 2026-11-06) contains one
  issue with `"severity": "critical"` while reporting `"has_errors": false`,
  `"success": true`, and `"failed_checks": 1`; the one failed check in the
  `checks` array is the same finding. The page does not define
  `success`/`has_errors`; it only says `issues` are the findings and `checks` may
  repeat them.
- **Confidence**: emerging (the example demonstrates the behavior; the page
  never states the semantics explicitly)
- **Quote**: (no direct quote; see the linked example artifact reproduced in
  Concrete Artifacts)
- **Our assessment**: Buy the observed behavior and treat it as a gate-design
  warning. If `success` can be `true` on a critical issue while `failed_checks`
  is nonzero, then `success` means "the scan completed," not "the artifact is
  clean." A JSON-driven gate must key on `issues[].severity` (and/or the process
  exit code), never on `success`. This also confirms the finding-accounting rule
  in Claim 5: the `failed_checks` counter moves with a finding, so it is not an
  independent finding count either.

### Claim 7: The JSON schema fixes the severity vocabulary to lowercase `debug | info | warning | critical`, defaulting to `warning`, and allows extra fields on issues and checks
- **Evidence**: The linked JSON Schema's `IssueSeverity` enum and the `Issue`
  `severity` default, plus `additionalProperties: true` on `Issue` and `Check`.
- **Confidence**: settled (published schema)
- **Quote**: `"enum": ["debug", "info", "warning", "critical"]`
- **Our assessment**: Buy it. This matters for gate predicates: the values are
  lowercase, and there is no `error` severity in the JSON enum (SARIF's `error`
  level is a *mapping output*, not a JSON issue severity). A `jq` filter written
  against `"CRITICAL"` or `"error"` silently matches nothing. The default
  `warning` also means a finding emitted without an explicit severity is not
  automatically fatal.

### Claim 8: SARIF output is 2.1.0 with a documented severity mapping — CRITICAL→error, WARNING→warning, INFO→note, DEBUG→none — and rules/results/artifacts/tool/invocation sections
- **Evidence**: "SARIF Output Format" states 2.1.0 support and lists the sections;
  "SARIF Structure" enumerates Rules, Results, Artifacts, Tool Information, and
  Invocation Details; "Severity Mapping" gives the four mappings.
- **Confidence**: settled (documented format and mapping)
- **Quote**: "ModelAudit supports SARIF (Static Analysis Results Interchange Format) 2.1.0 output for seamless integration with security tools and CI/CD pipelines:"
- **Quote (mapping)**: "`CRITICAL` → `error`"
- **Our assessment**: Buy it as the machine-consumable bridge. The mapping is the
  important contract: it projects the scanner's four-level severity onto SARIF's
  three practical levels (`error`/`warning`/`note`) and drops `DEBUG` to `none`.
  That means a SARIF consumer sees a coarser signal than the JSON consumer — a
  `critical` and (if it existed) an `error` both arrive as SARIF `error`, while
  `info` becomes `note`. The guide should state which artifact is authoritative
  for gating; the page implies SARIF is for publishing to code-scanning
  dashboards, not for the severity decision.

### Claim 9: SARIF is positioned as the interop layer for GitHub Advanced Security, Azure DevOps, VS Code, SonarQube/SonarCloud, Fortify, Checkmarx, CodeQL, and Snyk
- **Evidence**: "Integration with Security Tools" names GitHub Advanced
  Security, Azure DevOps, and the VS Code SARIF Viewer; "Static Analysis
  Platforms" lists the rest and says the output is compatible with them.
- **Confidence**: settled (documented integration list; actual importer behavior
  not tested here)
- **Quote**: "SARIF output is compatible with:"
- **Our assessment**: Buy the list as declared interoperability. The useful
  operational fact is that model-file findings can ride the same SARIF ingestion
  path as application-code findings, so an organisation does not need a separate
  model-security dashboard. The page does not document how each platform maps
  ModelAudit rule IDs or whether any importer deduplicates across runs, so treat
  "compatible" as format-level, not as a tested end-to-end integration.

### Claim 10: The GitHub Actions example is a path-triggered push scan that uploads SARIF with `if: always()` and a separate artifact, but omits `permissions: security-events: write` and installs both tools unpinned
- **Evidence**: The `.github/workflows/model-security.yml` example triggers on
  `push` with `paths:` for model extensions, runs
  `promptfoo scan-model models/ --no-write --format sarif --output model-scan.sarif`,
  then `github/codeql-action/upload-sarif@v3` with `if: always()` and
  `actions/upload-artifact@v4`. It installs `npm install -g promptfoo` and
  `pip install modelaudit[all]`, and uses mutable action tags (`@v4`, `@v5`,
  `@v3`). No `permissions:` block is present in the published workflow.
- **Confidence**: settled for the workflow text; emerging for the failure mode
  (the page gives no run log)
- **Quote**: "run: promptfoo scan-model models/ --no-write --format sarif --output model-scan.sarif"
- **Our assessment**: Buy the shape and flag the gaps. The scan step has no
  `continue-on-error`, so the job fails on any nonzero exit — exit 1 (findings)
  and exit 2 (operational) are not distinguished, which is the Side A behavior
  in contradiction #1995. `if: always()` still uploads the SARIF/artifact on
  failure, which is good for evidence but can attempt an upload when no file was
  written. Most concretely, `upload-sarif` requires `security-events: write`;
  the dedicated CI/CD page's SARIF workflow declares it, but this example does
  not, so copying it verbatim can fail at the upload step. And the install path
  is a supply-chain exposure (Claim 12 cross-ref): `npm install -g` resolves
  latest with lifecycle scripts enabled, `pip install modelaudit[all]` is
  unpinned, and `@v4/@v5/@v3` tags are mutable.

### Claim 11: The GitLab recipe is a two-layer gate — it tolerates scanner exit 0/1, fails only on exit >1, then asserts via `jq` that no `critical` issue exists
- **Evidence**: The `.gitlab-ci.yml` example runs
  `promptfoo scan-model models/ --format json --output scan-results.json || scan_status=$?`,
  exits if `scan_status > 1`, then runs
  `jq -e '[.issues[]? | select(.severity == "critical")] | length == 0' scan-results.json`,
  with `artifacts: when: always`.
- **Confidence**: settled (directly readable recipe)
- **Quote**: "if [ \"$scan_status\" -gt 1 ]; then exit \"$scan_status\"; fi"
- **Quote (policy check)**: `jq -e '[.issues[]? | select(.severity == "critical")] | length == 0' scan-results.json`
- **Our assessment**: Buy the pattern — it is the clearest implementation of
  "tool exit status and policy verdict are separate signals," and it matches the
  parent page's exit-1 callout (the Side B pole of #1995). Two caveats. First,
  this recipe scans the whole `models/` directory into one JSON and therefore
  loses the per-file status aggregation the dedicated CI/CD page's GitLab recipe
  preserves (`docs-promptfoo-model-audit-ci-cd.md`, Claim 8); a single directory
  scan can mask which artifact is bad and does not exercise the >1 precedence
  logic across files. Second, the `jq` predicate is keyed on lowercase
  `critical` only (correct per the schema enum in Claim 7), and it fails closed
  if the JSON is missing/malformed — but it silently passes `warning` and
  `info`, so the gate's actual policy is "critical-only," not "no findings."

### Claim 12: The pre-commit hook invokes `promptfoo scan-model` on changed files with `pass_filenames: true` and a broad extension regex — with no `--no-write`, timeout, or size cap
- **Evidence**: The `.pre-commit-config.yaml` example defines a local hook
  `id: modelaudit`, `entry: promptfoo scan-model`, `files:` matching pkl/h5/pb/pt
  and config/archive extensions, and `pass_filenames: true`.
- **Confidence**: settled (directly readable config)
- **Quote**: "entry: promptfoo scan-model"
- **Our assessment**: Buy the integration surface, but do not copy it as a
  hardened gate. As written it blocks a commit on any nonzero exit — including
  exit 1 warnings — which is the strictest pole of #1995, and it omits
  `--no-write` even though the default scan writes results to a database. On a
  developer laptop the DB write may be fine; in a shared or read-only hook
  environment it is not. It also has no `--timeout` / `--max-size`, so a large
  model staged by accident can hang the commit. The broad regex (including
  `json`, `yaml`, `zip`, `onnx`, etc.) means config and archive commits also pay
  scan cost. Use it with explicit flags, or keep it report-only.

### Claim 13: The programmatic entrypoint is `scan_model_directory_or_file`, returning a dict with `issues`, and accepting `blacklist_patterns`, `max_file_size` (bytes), and `timeout` (seconds)
- **Evidence**: The "Programmatic Usage" Python example imports
  `scan_model_directory_or_file` from `modelaudit.core`, scans a path or HF URL,
  iterates `results["issues"]` reading `issue["severity"]` and `issue["message"]`,
  and passes a config dict with `blacklist_patterns`, `max_file_size: 1073741824`
  (1GB), and `timeout: 600`.
- **Confidence**: settled (documented code example)
- **Quote**: "from modelaudit.core import scan_model_directory_or_file"
- **Our assessment**: Buy it. This is the path for an SRE-owned orchestrator that
  wants to scan an artifact inside a job rather than shell out. Note the unit
  mismatch vs the CLI: `max_file_size` is bytes while `--max-size` accepts
  human-readable units (`1GB`), so a policy translated between the two can be
  off by orders of magnitude. The example also shows the same `issues` contract
  as the JSON output (Claim 5), so the finding-accounting rule applies equally to
  the library API.

### Claim 14: `--sbom <path>` emits a CycloneDX SBOM with components, license metadata, risk scoring from findings, and model/dataset classification
- **Evidence**: "Software Bill of Materials (SBOM)" shows
  `promptfoo scan-model models/ --sbom model-sbom.json` and lists the four SBOM
  contents.
- **Confidence**: settled (documented behavior and contents)
- **Quote**: "Generate CycloneDX-compliant SBOMs with license information:"
- **Quote (contents)**: "Risk scoring based on scan findings"
- **Our assessment**: Buy it as a governance artifact. The risk score is derived
  from the same finding set, so it inherits the severity model and the
  `issues`/`checks` accounting caveat — an SBOM risk score is not an independent
  verdict. The parent note's options table lists `--sbom` without an argument;
  this page's example passes an output path, so treat it as taking a filename.
  The SBOM is a useful release artifact (licenses, component hashes), but it does
  not replace the gate.

### Claim 15: Custom scanners subclass `BaseScanner` and must be registered in `modelaudit/scanners/__init__.py`; they cannot be registered at runtime, and the page recommends contributing them upstream for production
- **Evidence**: "Extending ModelAudit → Creating Custom Scanners" gives a
  `BaseScanner` subclass with `name`, `description`, `supported_extensions`,
  `can_handle`, and `scan`, plus a registry snippet; the closing paragraph states
  the runtime restriction and the upstream recommendation.
- **Confidence**: settled (documented extension contract)
- **Quote**: "Custom scanners require integration into the ModelAudit package structure and cannot be dynamically registered at runtime. For production use, consider contributing your scanner to the ModelAudit project."
- **Our assessment**: Buy it, and treat it as a supply-chain/maintenance
  constraint rather than a feature. Extending the scanner means patching the
  installed package or maintaining a fork, so the custom scanner becomes part of
  the gate's trusted compute base and must be pinned, reviewed, and rebuilt with
  the scanner. A team that needs a custom format scanner cannot just drop a
  plugin into CI; it owns the fork. That should be an explicit decision, not a
  side effect.

## Concrete Artifacts

### Remote-auth env-var matrix (condensed from "Cloud & Artifact Registry Authentication")

| Source | Environment variables | Example target |
|---|---|---|
| Hugging Face | `HF_TOKEN` | `hf://your-org/private-model` |
| JFrog Artifactory | `JFROG_URL`, `JFROG_API_TOKEN` or `JFROG_ACCESS_TOKEN` | `https://your-domain.jfrog.io/artifactory/repo/model.pkl` |
| MLflow | `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD` | `models:/model-name/version` |
| Amazon S3 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` | `s3://my-bucket/model.pkl` |
| Google Cloud Storage | `GOOGLE_APPLICATION_CREDENTIALS` | `gs://my-bucket/model.pt` |
| Cloudflare R2 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL` | `r2://my-bucket/model.safetensors` |

Source: docs page, "Authentication and Configuration". Variable names preserved
verbatim; the example targets are the page's examples.

### Removed-flag migration table (verbatim from "Migration from Deprecated Flags")

| Removed Flag | Replacement Environment Variable |
|---|---|
| `--jfrog-api-token` | `JFROG_API_TOKEN` |
| `--jfrog-access-token` | `JFROG_ACCESS_TOKEN` |
| `--registry-uri` | `JFROG_URL` or `MLFLOW_TRACKING_URI` |

Source: docs page, "Migration from Deprecated Flags". The page adds: "Attempting
to use them will result in an error."

### Result-sharing controls (verbatim commands from "Sharing Results")

```bash
# Results are automatically shared when cloud is enabled
promptfoo scan-model models/
# Explicitly enable sharing
promptfoo scan-model models/ --share
# Disable sharing for this scan
promptfoo scan-model models/ --no-share
# Disable sharing globally via environment variable
export PROMPTFOO_DISABLE_SHARING=true
promptfoo scan-model models/
```

Source: docs page, "Configuration Options → Sharing Results".

### JSON finding-accounting contract (verbatim from "JSON Output Format")

> The result includes scan statistics, scanned assets, file metadata, `issues`,
> and `checks`. Treat `issues` as findings. `checks` records performed checks
> and may include a failed check for the same finding, so do not count both
> arrays as separate findings.

> Consumers should tolerate omitted optional fields and new scanner-specific
> fields, especially within `details` and `file_metadata`.

Source: docs page, "JSON Output Format". The page links a JSON Schema and an
example result; both were fetched 2026-11-06.

### Example result: a critical issue with clean execution status (excerpt)

```json
{
  "bytes_scanned": 82,
  "files_scanned": 1,
  "has_errors": false,
  "scanner_names": ["pickle"],
  "total_checks": 5,
  "passed_checks": 4,
  "failed_checks": 1,
  "success": true,
  "issues": [
    {
      "message": "Found REDUCE opcode invoking dangerous global: posix.system",
      "severity": "critical",
      "location": "tests/assets/samples/pickles/malicious_system_call.pkl (pos 79)",
      "details": {
        "opcode": "REDUCE",
        "module": "posix",
        "name": "system",
        "associated_global": "posix.system"
      },
      "why": "The 'posix' module provides direct access to POSIX system calls on Unix-like systems. Like the 'os' module, it can execute arbitrary system commands and manipulate the file system. The 'posix.system' function is equivalent to 'os.system' and poses the same security risks.",
      "type": "pickle_check",
      "rule_code": "S201"
    }
  ],
  "checks": [
    { "name": "Path Exists", "status": "passed", "message": "Path exists" },
    { "name": "Path Readable", "status": "passed", "message": "Path is readable" },
    { "name": "File Type Validation", "status": "passed", "message": "File type validation passed" },
    { "name": "File Integrity Hash", "status": "passed", "message": "File integrity hashes calculated" },
    { "name": "REDUCE Opcode Safety Check", "status": "failed", "message": "Found REDUCE opcode invoking dangerous global: posix.system" }
  ]
}
```

Source: linked example result
`modelaudit-scan-result.example-16b33d7ee497bf9ce1e70621dfa721ce.json`,
condensed (some fields and per-check details elided). The full example contains
5 checks, 4 passed and 1 failed, and a single `critical` issue. Note that
`has_errors` is `false` and `success` is `true` despite the critical finding.

### JSON severity enum (verbatim from the linked schema)

```
"enum": ["debug", "info", "warning", "critical"]
```

Source: linked JSON Schema `IssueSeverity` definition
(`modelaudit-scan-result.schema-bbd62ba3e975b7b3a332de6e23a72504.json`), fetched
2026-11-06. `Issue.severity` defaults to `warning`; `Issue` and `Check` both
allow additional properties.

### SARIF severity mapping (verbatim bullets from "Severity Mapping")

```
CRITICAL → error
WARNING → warning
INFO → note
DEBUG → none
```

Source: docs page, "SARIF Output Format → Severity Mapping".

### SARIF output example (condensed from "SARIF Structure")

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "ModelAudit",
          "version": "0.2.3",
          "rules": [
            {
              "id": "MA-PICKLE-ISSUE",
              "name": "Pickle Security Issue",
              "defaultConfiguration": { "level": "error", "rank": 90.0 }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "MA-PICKLE-ISSUE",
          "level": "error",
          "message": { "text": "Suspicious module reference found: os.system" },
          "locations": [
            { "physicalLocation": { "artifactLocation": { "uri": "model.pkl" } } }
          ]
        }
      ]
    }
  ]
}
```

Source: docs page, "SARIF Structure". Condensed from the page's sample; the
`$schema`, `version`, rule, result, and location fields are as published.

### GitHub Actions workflow (verbatim from "CI/CD Integration → GitHub Actions")

```yaml
# .github/workflows/model-security.yml
name: Model Security Scan
on:
  push:
    paths:
      - 'models/**'
      - '**.pkl'
      - '**.h5'
      - '**.pb'
      - '**.pt'
      - '**.pth'
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          npm install -g promptfoo
          pip install modelaudit[all]
      - name: Scan models
        run: promptfoo scan-model models/ --no-write --format sarif --output model-scan.sarif
      - name: Upload SARIF to GitHub Advanced Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: model-scan.sarif
          category: model-security
      - name: Upload scan results as artifact
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: model-scan-results
          path: model-scan.sarif
```

Source: docs page, "CI/CD Integration → GitHub Actions". Reproduced as
published; note the missing `permissions: security-events: write` and the
mutable action tags.

### GitLab CI two-layer gate (verbatim from "CI/CD Integration → GitLab CI")

```yaml
# .gitlab-ci.yml
model_security_scan:
  stage: test
  image: python:3.10
  script:
    - pip install modelaudit[all]
    - npm install -g promptfoo
    - |
      scan_status=0
      promptfoo scan-model models/ --format json --output scan-results.json || scan_status=$?
      if [ "$scan_status" -gt 1 ]; then exit "$scan_status"; fi
    - jq -e '[.issues[]? | select(.severity == "critical")] | length == 0' scan-results.json
  artifacts:
    paths:
      - scan-results.json
    when: always
  only:
    changes:
      - models/**
      - '**/*.pkl'
      - '**/*.h5'
      - '**/*.pb'
      - '**/*.pt'
      - '**/*.pth'
```

Source: docs page, "CI/CD Integration → GitLab CI". Reproduced as published.

### Pre-commit hook (verbatim from "CI/CD Integration → Pre-commit Hook")

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: modelaudit
        name: ModelAudit
        entry: promptfoo scan-model
        language: system
        files: '\.(pkl|h5|pb|pt|pth|keras|hdf5|json|yaml|yml|zip|onnx|safetensors|bin|tflite|msgpack|pmml|joblib|npy|gguf|ggml)$'
        pass_filenames: true
```

Source: docs page, "CI/CD Integration → Pre-commit Hook". Reproduced as
published; no `--no-write`, `--timeout`, or `--max-size` is present.

### Programmatic Python API (verbatim from "Programmatic Usage")

```python
from modelaudit.core import scan_model_directory_or_file

# Scan a single model
results = scan_model_directory_or_file("path/to/model.pkl")

# Scan a HuggingFace model URL
results = scan_model_directory_or_file("https://huggingface.co/bert-base-uncased")

# Check for issues
if results["issues"]:
    print(f"Found {len(results['issues'])} issues:")
    for issue in results["issues"]:
        print(f"- {issue['severity'].upper()}: {issue['message']}")
else:
    print("No issues found!")

# Scan with custom configuration
config = {
    "blacklist_patterns": ["unsafe_model", "malicious_net"],
    "max_file_size": 1073741824,  # 1GB
    "timeout": 600  # 10 minutes
}
results = scan_model_directory_or_file("path/to/models/", **config)
```

Source: docs page, "Programmatic Usage".

### SBOM command and contents (verbatim from "Software Bill of Materials (SBOM)")

```bash
promptfoo scan-model models/ --sbom model-sbom.json
```

> The SBOM includes:
>
> - Component information (files, types, sizes, checksums)
> - License metadata (detected licenses, copyright holders)
> - Risk scoring based on scan findings
> - Model/dataset classification

Source: docs page, "Software Bill of Materials (SBOM)".

### Troubleshooting error strings (verbatim from "Troubleshooting → Common Issues")

```
Error: h5py not installed, cannot scan Keras H5 files
Error: Scan timeout after 300 seconds
Warning: File too large to scan
Warning: Unknown or unhandled format
```

Source: docs page, "Troubleshooting → Common Issues". The documented remedies
are `pip install h5py tensorflow`, `--timeout 7200`, `--max-size 3GB`, and
"Ensure the file is in a supported format."

## Cross-References

### Candidate notes from `miner-related-notes.md` — cite or dismiss

1. `source-notes/docs-litellm-batches-api.md` — LiteLLM batch rate limiting.
   No overlap with model-file scanning. **Dismiss**.
2. `source-notes/docs-promptfoo-evaluate-coding-agents.md` — agent-eval
   workspace isolation/trajectory CI. No overlap. **Dismiss**.
3. `source-notes/docs-promptfoo-enterprise-guardrails.md` — runtime guardrail
   enforcement (HTTP endpoint, placements, aggregate `action`). Different
   security layer from static model-artifact scanning. **Dismiss**.
4. `source-notes/docs-litellm-evals-api.md` — LiteLLM Evaluations API. No
   overlap. **Dismiss**.
5. `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **Extends**:
   its Claim 4 documents SARIF as an export format with "no upload step, no CI
   job, and no build-blocking behavior"; this page supplies the model-scan
   upload/CI half (Claims 8–10), though the GitHub example still has gaps.
6. `source-notes/docs-promptfoo-model-audit.md` — **Extends**: the sibling
   landing-page note explicitly defers remote-source authentication to this page
   (its Claim 2/Source Context). It also owns the read-only flags (Claim 4), the
   severity vocabulary (Claim 5), the #1995 gate-policy tension (Claim 8), the
   "no scanned files = exit 2" gotcha (Claim 9), and install variants/pinning
   (Claim 10). This note supplies the env-var auth contract, the JSON/SARIF
   output contracts, and the sharing default it did not cover.
7. `source-notes/blog-pagerduty-sre-agent-triage.md` — AI incident triage. No
   overlap. **Dismiss**.
8. `source-notes/docs-promptfoo-pi-scorer.md` — model-graded Pi scorer. No
   overlap. **Dismiss**.
9. `source-notes/docs-google-sre-reliable-product-launches.md` — launch
   coordination engineering. No overlap. **Dismiss**.
10. `source-notes/docs-google-sre-team-lifecycles.md` — SRE team lifecycles.
    No overlap. **Dismiss**.

### Cross-references against existing notes

- **Corroborates**:
  - `docs-promptfoo-model-audit-scanners.md`, Claim 1 — scanner selection is an
    enumerated, *installed-version-dependent* surface. This page supplies the
    catalog-export command (`modelaudit scan --list-scanners --format json`) and
    the repeated-flag form (`--scanners pickle --scanners tf_savedmodel`).
  - `docs-promptfoo-model-audit-scanners.md`, Claim 15 — the weight-distribution
    scanner is the only behavioural/statistical check and its LLM path is
    disabled by default. This page's `--exclude-scanner weight_distribution`
    example is the operational response to a noisy/irrelevant scanner.
  - `failure-litellm-supply-chain-incident-march-2026.md`, Claim 14 — pin
    verified SHAs and add an upgrade cooldown. This page's CI examples use
    `npm install -g promptfoo`, `pip install modelaudit[all]`, and mutable
    `@v4/@v5/@v3` action tags, which is exactly the exposure that rule targets.
  - `docs-promptfoo-code-scan-github-action.md`, Claim 8 — pin third-party
    actions to full commit SHAs. The GitHub Actions recipe here does not.
- **Contradicts**:
  - **#1995** (already filed; no new contradiction). The usage page supplies
    both poles on one page: its GitHub Actions recipe (Claim 10) fails the job
    on any nonzero exit — including exit 1 findings — while its GitLab recipe
    (Claim 11) explicitly tolerates exit 1 and gates only on `critical` via
    `jq`. Its pre-commit hook (Claim 12) blocks on any finding. No verdict is
    asserted here; this is additional evidence for both sides of #1995.
  - No other contradiction found. The default-on cloud sharing (Claim 3) is a
    data-governance hazard, not a claim-vs-claim contradiction with the blog
    note's "runs entirely offline" (that claim is about the scan engine, not
    result egress).
- **Extends**:
  - `docs-promptfoo-model-audit.md`, Claim 2 — the remote-source matrix was
    documented there but authentication was deferred to this page; Claims 1–2
    here supply the env-var contract and the removed-flag migration.
  - `docs-promptfoo-model-audit.md`, Claim 4 — the read-only flags
    (`--no-write`, `--timeout`, `--max-size`) are restated in this page's CI
    recipes; this note adds the pre-commit and programmatic variants.
  - `blog-promptfoo-open-sourcing-modelaudit.md`, Claim 12 — that note records
    SARIF/SBOM as capabilities; this page supplies the SARIF 2.1.0 structure and
    severity mapping (Claim 8), the interop list (Claim 9), and the CycloneDX
    SBOM contents (Claim 14).
  - `docs-promptfoo-model-audit-ci-cd.md`, Claim 1 — the tri-state `0/1/2`
    contract. This page's GitLab recipe (Claim 11) is a second, *single-JSON*
    implementation of the two-layer gate, while the dedicated page's GitLab
    recipe preserves per-file status with max-propagation (Claim 8). Prefer the
    per-file version for multi-artifact scans.
  - `docs-promptfoo-code-scan-github-action.md`, Claim 5 — the code-scan Action
    publishes SARIF only when a scan completes. This page's model-scan GitHub
    recipe uploads with `if: always()` and no completion guard (Claim 10), so
    the same "false clean / confusing upload" caveat applies; the page does not
    document a `sarif-path`-style completion signal.
  - `docs-promptfoo-enterprise-findings-reports.md`, Claim 4 — SARIF export
    without a documented upload/CI path; this page supplies the model-scan
    upload wiring, though not a hard test of the importers.
- **Novel**:
  - The env-var-only remote-auth matrix and the removed-credential-flag
    migration (Claims 1–2).
  - Default-on cloud result sharing and its opt-out controls (Claim 3).
  - The `issues` vs `checks` finding-accounting contract, and the
    `success`/`has_errors`-are-not-verdicts gotcha demonstrated by the linked
    example (Claims 5–7).
  - The SARIF severity mapping and interop list for model-scan findings (Claims
    8–9).
  - The programmatic `scan_model_directory_or_file` API (Claim 13).
  - The pre-commit hook and custom-scanner extension constraints (Claims 12,
    15).
  - The CycloneDX SBOM contents and the `--sbom <path>` form (Claim 14).

## Guide Impact

- **Chapter 06 — "Gating on LLM security scans"** (`guide/06-security-and-trust.md:768`):
  Add a model-artifact gate subsection. Use Claim 5 for finding accounting —
  count `issues`, not `issues` + failed `checks` — and Claim 6 for the strongest
  gotcha: `success`/`has_errors` can be clean while a `critical` issue is
  present, so the gate must key on `issues[].severity` or the process exit code,
  never on `success`. Use Claim 7 for the lowercase severity enum and Claim 8
  for the SARIF mapping when publishing to code scanning. Use Claim 11 as the
  concrete two-layer gate (tolerate exit 1, fail >1, then assert no `critical`)
  and Claim 10 to show the GitHub recipe's gaps (`permissions`, unpinned
  installs, mutable action tags). Keep the #1995 verdict open; present the policy
  as severity-filtered and explicit rather than copying either pole.
- **Chapter 06 — "Supply-chain security for LLM infrastructure"**
  (`guide/06-security-and-trust.md:634`): Add "the scanner is a CI dependency."
  The usage page's GitHub/GitLab examples install `promptfoo`/`modelaudit`
  unpinned and float actions on mutable tags (Claim 10), which is the same
  exposure as the LiteLLM incident's unpinned Trivy
  (`failure-litellm-supply-chain-incident-march-2026.md`, Claim 14). Add the
  custom-scanner rule (Claim 15): a custom scanner means a patched or forked
  package, so it must be pinned, reviewed, and rebuilt with the scanner. Add the
  sharing default (Claim 3) as a data-egress control: private-model scans should
  set `--no-share` or `PROMPTFOO_DISABLE_SHARING=true` deliberately.
- **Chapter 06 — "Gateway credential routing: declare, don't infer"**
  (`guide/06-security-and-trust.md:603`): Add the credential-channel instance from
  Claims 1–2 — secrets belong in env vars, not `argv`, because CLI flags leak
  through shell history and process lists; the vendor removed the flags and made
  use an error. Keep the guide's distinction between *channel* and *selection*:
  the page's env-var contract fixes the channel, but it still relies on ambient
  provider credential chains (`AWS_*`, `GOOGLE_APPLICATION_CREDENTIALS`), so the
  guide's "declare the auth mode" rule is not fully satisfied by an env var
  alone.
- **Chapter 05 — "CI/CD supply-chain isolation"** (`guide/05-llm-ops-reliability.md:1359`):
  Add model-artifact scanning as a pipeline stage with the scanner pinned by
  exact version/digest (Claim 10 + `failure-litellm-supply-chain-incident-march-2026.md`,
  Claim 14). Use Claim 11's two-layer gate as the policy shape and Claim 13's
  programmatic API for an orchestrator that scans in-process. Keep the SBOM
  (Claim 14) as a release artifact, not a substitute for the gate.
- **Chapter 05 — "A gate that cannot fail is not a gate"**
  (`guide/05-llm-ops-reliability.md:655`): Add Claim 6 as a worked example of a
  gate that *can* look green while a critical finding exists: `success: true`,
  `has_errors: false`, and `failed_checks: 1` alongside a `critical` issue. The
  rule is to gate on the severity array or exit code and to keep a negative
  control (a known-bad model file) proving the gate fails. Use Claim 12 as the
  opposite failure — a pre-commit hook that blocks all findings including
  warnings, with no timeout/size cap — to show that "strict" is also a policy
  choice, not a default.

## Extraction Notes

- Source fetched 2026-11-06 from the live page. It is living vendor
  documentation with no publish date; footer "Last updated on **Nov 6, 2026** by
  **Michael**". Flag/format behavior is recorded as of that date.
- Per Prospector triage, this is a **delta extraction**: I did not re-derive the
  pickle-RCE threat model, blocklist-vs-allowlist analysis, GHSAs, format
  coverage, or detection-rate comparisons (settled in
  `blog-promptfoo-open-sourcing-modelaudit.md`, #553, and
  `docs-promptfoo-model-audit.md`, #1948). The sibling CI/CD page (#1949) already
  owns the fuller per-CI workflow detail; this note extracts the usage page's
  distinct recipes and the auth/output contracts it does not cover.
- I followed the two linked substantive assets — the JSON Schema and the example
  result — to verify the `issues`/`checks` accounting and the severity enum
  rather than inferring them. That is why Claim 6 (the clean `success` alongside
  a `critical` issue) and Claim 7 (lowercase enum, no `error` severity) are in
  the note; neither is stated in prose on the page.
- Contradiction handling: no new contradiction filed. The usage page contains
  both poles of the already-open **#1995** (GitHub recipe blocks on any nonzero;
  GitLab recipe tolerates exit 1 and gates on critical). The default-on cloud
  sharing is a new risk, not a contradiction with the blog note's offline-scan
  claim.
- Count/argument reconciliation with the parent note
  `docs-promptfoo-model-audit.md`: (a) its options table lists `--sbom` without
  an argument, while this page passes `--sbom model-sbom.json`; treat it as
  taking an output path. (b) The parent note says the CLI "no scanned files"
  case exits 2; this page's GitLab recipe relies on that `>1` check but does not
  restate it. (c) The parent note's severity vocabulary is uppercase
  (`CRITICAL`/`WARNING`/`INFO`/`DEBUG`); the JSON schema's issue severity enum
  is lowercase (`critical`/`warning`/`info`/`debug`), and SARIF maps to
  `error`/`warning`/`note`/`none`. These are different representations, not
  contradictions.
- Quotes were copied character-for-character from the rendered page. The fetch
  conversion collapsed code-block line breaks, so YAML/Python/JSON indentation
  and line breaks were reconstructed to be valid; command, flag, variable, and
  expression text is unchanged. The example JSON is condensed (some fields and
  per-check details elided) but the fields shown are as published.
- `confidence_overall` is **emerging**: the env-var names, flag removals, output
  formats, schema enums, and recipe text are documented and string-checkable
  (settled as a spec), but there is no independent validation of detection
  quality, the page is drift-prone living docs, and one example's
  `success`/`has_errors` semantics are demonstrated only by the linked artifact,
  not stated as a contract.
- Candidate file read before writing Cross-References; all 10 listed paths were
  either cited or explicitly dismissed. Every cited `Claim N` was re-read in the
  cited note per MINER.md §4b. No `registry/*` file is touched; the derived
  indexes are left to the post-merge rebuild.
