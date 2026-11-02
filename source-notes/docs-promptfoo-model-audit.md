---
source_url: https://www.promptfoo.dev/docs/model-audit
source_type: docs
title: "Promptfoo ModelAudit — Model Scanning: Remote-Source Matrix, Scanner Selection Flags, and the Severity/Exit-Code Gate Contract"
author: "Promptfoo (vendor documentation)"
date_published: null
date_extracted: 2026-11-02
last_checked: 2026-11-02
status: current
confidence_overall: emerging
issue: "#1948"
---

# Promptfoo ModelAudit — Model Scanning (docs landing page)

> The reference/landing page behind the ModelAudit announcement. The novel delta
> over `blog-promptfoo-open-sourcing-modelaudit.md` is the operational interface
> for running model scanning as a pipeline stage: the in-place remote-source
> matrix (`hf://`, `s3://`, `gs://`, `r2://`, `models:/`, JFrog, DVC), the
> scanner-selection and read-only/caching flags, the CRITICAL/WARNING/INFO/DEBUG
> severity model, the artifact-format scope table, and the documented gate
> policy — whose CI/CD Best Practice callout says exit-1 findings need not block,
> contradicting the page's own blocking example and the blog note's `--strict`
> production-gate advice.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "Model Audit >
  Model Scanning" landing page; living docs, no publish date, footer "Last
  updated on **Nov 2, 2026** by **renovate[bot]**").
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team/security
  vendor. First-party documentation of its own `promptfoo scan-model` wrapper
  and the `modelaudit` package — authoritative as a *specification* of flag
  names, URL schemes, defaults, and exit codes, all of which are string-checkable
  against the installed CLI. Not measurement: the page publishes no detection
  rate, false-positive rate, runtime benchmark, or independent validation. The
  CLI surface is explicitly drift-prone (living docs; the footer bot update
  means the "last updated" date is not an editorial revision).
- **Scope**: Covers the `promptfoo scan-model` command, standalone `modelaudit`
  install, Docker images, options table, examples (including remote sources), the
  web UI at `/model-audit`, the supported-format table, the remote-source table,
  the security-check list, severity levels, a CI/CD example + exit codes, and
  per-format runtime dependencies. Does **not** cover the CI/CD workflow YAML
  and PR-vs-scheduled scanning (child page `/docs/model-audit/ci-cd`, issue
  #1949), per-scanner internals (child page `/docs/model-audit/scanners`, issue
  #1950), or remote-source *authentication* setup (deferred to
  `/docs/model-audit/usage`). Does not re-argue the pickle-RCE threat model,
  blocklist-vs-allowlist architecture, GHSAs, or detection-rate comparisons —
  those are settled in `blog-promptfoo-open-sourcing-modelaudit.md` (#553) and
  deliberately not re-extracted here.
- **Relationship to sibling pages**: this is the index page for the ModelAudit
  docs section. Per Prospector triage, this note is index-only; #1949 and #1950
  own the CI/CD workflow detail and per-scanner internals.

## Extracted Claims

### Claim 1: ModelAudit is invoked as `promptfoo scan-model [OPTIONS] PATH...`, and the standalone `modelaudit scan` command behaves the same — the scanner is an installable local artifact, not a hosted scanning service
- **Evidence**: The "Basic Command Structure" block and the "Alternative
  Installation and Usage" note; the install section gives both `npm install -g
  promptfoo` + `pip install modelaudit` and a standalone `pip install modelaudit`.
- **Confidence**: settled (documented CLI contract; checkable against the
  installed command)
- **Quote**: "`modelaudit scan` behaves the same as `promptfoo scan-model`."
- **Our assessment**: This is the structural fact that makes model scanning
  placeable in an SRE-owned pipeline: the gate runs as a local process over
  files or URLs, with no vendor API in the scan path. It distinguishes
  ModelAudit from Promptfoo's hosted code-scanning CLI, which requires a
  Promptfoo account and defaults to `https://api.promptfoo.app`
  (`docs-promptfoo-code-scan-cli.md`, Claim 2). Buy it as documented behavior;
  the "behaves the same" equivalence is a vendor claim, not independently
  verified.

### Claim 2: `scan-model` accepts remote model sources in place — Hugging Face (`https://huggingface.co/`, `https://hf.co/`, `hf://`), S3 (`s3://`), GCS (`gs://`), Cloudflare R2 (`r2://`), MLflow (`models:/`), JFrog Artifactory (`https://*.jfrog.io/`), and DVC-tracked `.dvc` files — so a gate can scan a registry/bucket path without a separate download step
- **Evidence**: The "Examples" block's remote-source commands and the
  "Supported Formats → Remote Sources" table (reproduced in Concrete
  Artifacts). The page defers authentication detail to the Advanced Usage
  guide.
- **Confidence**: settled (documented URL schemes and examples; string-checkable)
- **Quote**: "# Scan a model directly from HuggingFace without downloading"
- **Our assessment**: This is the highest-value delta on the page for an SRE
  audience. In-place scanning means the artifact can be evaluated where it is
  stored — the registry entry, bucket object, or DVC pointer — rather than
  pulling multi-GB weights onto a CI runner first. R2, MLflow, JFrog, and DVC
  are new relative to the blog note's S3/GCS/HF mention. Caveat: the page gives
  no authentication or credential-scoping guidance here (deferred to the
  Advanced Usage page), so the guide should not present remote scanning as
  turnkey until #1949/usage cover auth. Also note the gate now trusts a remote
  fetch path; the scanner image and its cloud SDKs become part of the supply
  chain.

### Claim 3: Scanner selection is explicit — `--list-scanners` prints scanner IDs, `--scanners` runs only a chosen set, and `--exclude-scanner` removes scanners from the default set — which is what lets a pipeline split a fast changed-file scan from a full scan
- **Evidence**: The options table entries ("Print available scanner IDs and
  class names", "Only run selected scanners", "Exclude scanners from the
  default scanner set") and the example `promptfoo scan-model models/
  --scanners pickle,tf_savedmodel`.
- **Confidence**: settled (documented flag surface)
- **Quote**: "Only run selected scanners"
- **Our assessment**: Buy it as a documented knob. The operational value is
  that scanner IDs are a stable selection unit (the example uses
  `pickle,tf_savedmodel`), so a PR gate can run only the scanners relevant to
  the changed artifact types while a scheduled full scan runs everything. This
  mirrors the code-scanning CLI's `--diffs-only` tradeoff
  (`docs-promptfoo-code-scan-cli.md`, Claim 5): narrow the scan for per-PR
  latency, widen it for scheduled coverage. The page does not publish per-scanner
  runtimes, so the latency split is an inference, not a vendor benchmark.

### Claim 4: The scanner exposes read-only and cache-control flags — `--no-cache`, `--no-write`, `--dry-run`, `--quiet`, `--progress`, `--timeout` (default 300s), and `--max-size` — sufficient to run it safely on an ephemeral or read-only CI runner
- **Evidence**: The options table (entries reproduced in Concrete Artifacts)
  and the SARIF example `promptfoo scan-model model.pkl --no-write --format
  sarif --output results.sarif`.
- **Confidence**: settled (documented flag surface and defaults)
- **Quote**: "Skip writing results to database"
- **Our assessment**: Buy it. `--no-write` is the important one for CI: the
  default scan writes results to a database, which a read-only runner cannot
  do, so the documented SARIF example explicitly pairs `--no-write` with
  `--output`. `--no-cache` disables caching of downloaded files — relevant for
  ephemeral runners and for remote-source scans where a stale cache could hide
  a changed artifact. `--max-size` and `--timeout` are the guardrails that stop
  a large or pathological artifact from hanging the job; the 300s default is a
  starting point, not a validated CI budget.

### Claim 5: Findings are graded CRITICAL / WARNING / INFO / DEBUG, with DEBUG shown only under `--verbose` and some findings carrying a per-finding "Why" explanation — a four-level severity vocabulary to map onto alert/block policy
- **Evidence**: The "Interpreting Results" section's severity bullets and the
  sample finding (reproduced in Concrete Artifacts) that includes a `Why:`
  line explaining the risk.
- **Confidence**: settled (documented severity vocabulary)
- **Quote**: "The scan results are classified by severity:"
- **Our assessment**: The severity set is coarser than the code-scanning
  product's `low|medium|high|critical` threshold (`docs-promptfoo-code-scan-cli.md`,
  Claim 6) and has no documented numeric mapping, so the guide should not
  pretend the two thresholds are interchangeable. The useful part is the
  per-finding `Why` text: it is the triage input a responder reads, and it is
  present in the human/text output. The page does not say whether `Why` is in
  the JSON/SARIF output, so a machine gate should key on severity, not on
  parsing the explanation.

### Claim 6: The page claims 30+ specialized file-format scanners spanning PyTorch, TF SavedModel/TFLite, TensorRT, Keras, ONNX, SafeTensors, GGUF/GGML, Flax/JAX, pickle/dill, joblib, NumPy, PMML, ZIP archives, OCI container manifests, and auto-detected binaries — this is the scope a model gate actually covers, and by omission the artifact types it does not
- **Evidence**: The "Supported Formats" intro ("ModelAudit supports scanning
  30+ specialized file format scanners across major ML frameworks") and the
  format table (reproduced in Concrete Artifacts).
- **Confidence**: emerging (vendor count; the table enumerates ~18 format
  categories, and the page's 30+ scanners vs the blog's 42+ formats are different
  units)
- **Quote**: "ModelAudit supports scanning 30+ specialized file format scanners across major ML frameworks:"
- **Our assessment**: Buy the *coverage list* as documented scope; treat the
  count as vendor-defined. This page says "30+ specialized file format
  scanners while the blog note (#553, Claim 6) says 42+ formats — those are
  not the same unit (scanners vs formats), so this is **not** a contradiction,
  but the guide must not mix the numbers. The SRE-relevant reading is the
  boundary: a gate covers these formats and silently misses anything outside
  them (e.g. arbitrary Python source, notebook files, prompt/config artifacts).
  A pipeline should state its covered extensions rather than claim "models are
  scanned."

### Claim 7: Beyond pickle analysis, the security checks include XXE in PMML, zip bombs/decompression attacks, embedded PE/ELF/Mach-O executables, OCI/Docker container-layer scanning, weight-anomaly statistical backdoor detection, AGPL license compliance, embedded secrets, and network-egress indicators — several of which the blog note did not enumerate
- **Evidence**: The "Security Checks Performed" bullet list (reproduced in
  Concrete Artifacts).
- **Confidence**: emerging (vendor list; no per-check detection evidence on
  this page)
- **Quote**: "**Compression Attacks**: Detecting zip bombs and decompression attacks"
- **Our assessment**: Buy the list as declared scope, not as validated
  detection. The items the blog note did not enumerate are the operationally
  interesting ones for an SRE gate: zip bombs and decompression attacks are
  availability threats to the scanner runner itself (why `--max-size` and
  `--timeout` matter), container-layer scanning extends coverage to OCI
  artifacts, and license compliance (AGPL) plus secrets detection are
  governance findings rather than exploit findings. Weight-anomaly backdoor
  detection is a statistical claim with no methodology on this page — treat it
  as emerging and do not let it substitute for provenance controls.

### Claim 8: The page's own "CI/CD Best Practice" callout says exit 1 findings "should be reviewed but don't necessarily block deployment" and that only exit 2 represents actual scan failures — directly opposing its example script, which fails the build on any nonzero exit
- **Evidence**: The "Integration in Workflows" example (`if [ $? -ne 0 ]; then
  ... exit 1; fi`) and the immediately following "Exit Codes" callout.
- **Confidence**: settled (both passages are on the page; the conflict is
  textual)
- **Quote**: "In CI/CD pipelines, exit code 1 indicates findings that should be reviewed but don't necessarily block deployment. Only exit code 2 represents actual scan failures."
- **Our assessment**: This is a genuine internal contradiction and a
  cross-source one: `blog-promptfoo-open-sourcing-modelaudit.md` recommends
  gating production deployments with `--strict` (fail on warnings), which is
  the opposite of saying findings need not block. A team cannot implement
  both as the default. Filed as contradiction **#1995**. The guide should not
  copy the example verbatim; the defensible pattern is to hard-fail on exit 2
  (operational/inconclusive), parse findings and fail on CRITICAL (optionally
  WARNING), and reserve `--strict` for a promotion gate — pending human verdict.

### Claim 9: A scan that matches no files is an operational error (exit 2), not a clean pass — an empty glob or wrong path cannot be read as a successful scan
- **Evidence**: The exit-code 2 definition explicitly lists "no scanned files"
  among operational/inconclusive causes.
- **Confidence**: settled (documented exit-code semantics)
- **Quote**: "**2**: Operational errors or inconclusive scans occurred (installation, file access, timeouts, no scanned files, etc.) 🔴"
- **Our assessment**: High-value gate gotcha and the direct model-artifact
  analogue of the code-scanning rule "a zero-finding result and a skipped scan
  must be distinguishable" (`docs-promptfoo-code-scan-cli.md`, Claim 9;
  `docs-promptfoo-code-scan-github-action.md`, Claim 5). If a pipeline gates
  only on exit 1, an exit-2 "no scanned files" is silently treated as success
  by a naive `if exit == 1` check — so the gate must fail on any nonzero *or*
  explicitly treat 2 as failure and 1 as severity-filtered. This strengthens
  the case for the severity-filtered policy in Claim 8.

### Claim 10: Deployment variants are pip extras (`modelaudit[tensorflow,h5,pytorch]`, `[all]`, `[cloud,mlflow]`, `[numpy1]`) and GHCR image tags (`latest`, `latest-full`, `latest-tensorflow`), with per-format runtime dependencies — choices that change CI image size, offline capability, and which formats a gate can actually parse
- **Evidence**: The "Installation → Standalone Installation" and "Docker"
  blocks, plus the "Requirements" section listing `tensorflow`, `torch`,
  `h5py`, `pyyaml`, `safetensors`, `huggingface-hub`, `boto3
  google-cloud-storage`, and `mlflow` (reproduced in Concrete Artifacts).
- **Confidence**: settled (documented packaging surface)
- **Quote**: "ModelAudit is included with Promptfoo, but specific model formats may require additional dependencies:"
- **Our assessment**: Buy the packaging facts; they have direct CI
  consequences. `latest-full` ("All ML frameworks") is a large image, while
  `latest` + selective extras keeps the runner lean — but a lean image silently
  cannot parse formats whose dependencies are absent, so a "clean" scan on a
  minimal image is a coverage statement, not a safety statement. The `cloud`
  and `mlflow` extras are what make the remote-source matrix in Claim 2 work.
  Supply-chain note: `latest*` tags are mutable; per the guide's pin rule
  (`failure-litellm-supply-chain-incident-march-2026.md`, Claim 14), pin the
  scanner image by digest, especially since the scanner is itself a CI
  dependency.

### Claim 11: The same scanner is exposed through a web UI at `/model-audit` (via `promptfoo view`, default `http://localhost:15500/model-audit`) with GUI configuration, live progress, severity-colour-coded results, scan history, and automatic installation detection
- **Evidence**: The "Web Interface" section.
- **Confidence**: settled (documented UI surface)
- **Quote**: "Promptfoo includes a web interface for ModelAudit at `/model-audit` with visual path selection, real-time progress tracking, and detailed results visualization."
- **Our assessment**: Buy it as a documented surface, but it is secondary for
  an SRE gate — the CLI is the automatable path. The useful operational detail
  is "automatic installation detection": the UI surfaces missing format
  dependencies, which is exactly the coverage gap from Claim 10. Treat the UI
  as the human triage view (inspect findings, browse history), not as the
  enforcement point.

## Concrete Artifacts

### Remote-source URL matrix (verbatim table from "Supported Formats → Remote Sources")

| Source | URL Format | Example |
|---|---|---|
| HuggingFace Hub | `https://huggingface.co/`, `https://hf.co/`, `hf://` | `hf://microsoft/resnet-50` |
| Amazon S3 | `s3://` | `s3://my-bucket/model.pt` |
| Google Cloud Storage | `gs://` | `gs://my-bucket/model.h5` |
| Cloudflare R2 | `r2://` | `r2://my-bucket/model.safetensors` |
| MLflow Registry | `models:/` | `models:/MyModel/1` |
| JFrog Artifactory | `https://*.jfrog.io/` | `https://company.jfrog.io/artifactory/models/model.pkl` |
| DVC | `.dvc` files | `model.pkl.dvc` |

Source: docs page, "Supported Formats → Remote Sources".

### Remote-source scan examples (verbatim from "Usage → Examples")

```bash
# Scan a model directly from HuggingFace without downloading
promptfoo scan-model https://huggingface.co/bert-base-uncased
promptfoo scan-model hf://microsoft/resnet-50
# Scan from cloud storage
promptfoo scan-model s3://my-bucket/model.pt
promptfoo scan-model gs://my-bucket/model.h5
# Scan from MLflow registry
promptfoo scan-model models:/MyModel/1
```

Source: docs page, "Usage → Examples".

### Options table (verbatim from "Usage → Options")

| Option | Description |
|---|---|
| `--blacklist`, `-b` | Additional blacklist patterns to check against model names |
| `--format`, `-f` | Output format (`text` \| `json` \| `sarif`) [default: text] |
| `--output`, `-o` | Output file path (prints to stdout if not specified) |
| `--timeout`, `-t` | Scan timeout in seconds [default: 300] |
| `--verbose`, `-v` | Enable verbose output |
| `--max-size` | Maximum total size to scan (e.g., `500MB`, `1GB`) |
| `--sbom` | Generate CycloneDX Software Bill of Materials with license info |
| `--strict` | Fail on warnings; enable stricter validation |
| `--dry-run` | Preview scan without processing files |
| `--scanners` | Only run selected scanners |
| `--exclude-scanner` | Exclude scanners from the default scanner set |
| `--list-scanners` | Print available scanner IDs and class names |
| `--quiet` | Suppress non-critical output |
| `--progress` | Force-enable progress reporting |
| `--no-cache` | Disable caching of downloaded files |
| `--no-write` | Skip writing results to database |

Source: docs page, "Usage → Options".

### Supported-format scope table (condensed from "Supported Formats → Model Formats")

| Format | Extensions | Description |
|---|---|---|
| PyTorch | `.pt`, `.pth`, `.bin` | PyTorch model files and checkpoints |
| TensorFlow SavedModel | `.pb`, directories | TensorFlow's standard model format |
| TensorFlow Lite | `.tflite` | Mobile-optimized TensorFlow models |
| TensorRT | `.engine`, `.plan` | NVIDIA GPU-optimized inference engines |
| Keras | `.h5`, `.keras`, `.hdf5` | Keras/TensorFlow models in HDF5 format |
| ONNX | `.onnx` | Open Neural Network Exchange format |
| SafeTensors | `.safetensors` | Hugging Face's secure tensor format |
| GGUF/GGML | `.gguf`, `.ggml`, `.ggmf`, `.ggjt`, `.ggla`, `.ggsa` | Quantized models (LLaMA, Mistral, etc.) |
| Flax/JAX | `.msgpack`, `.flax`, `.orbax`, `.jax` | JAX-based model formats |
| JAX Checkpoints | `.ckpt`, `.checkpoint`, `.orbax-checkpoint` | JAX training checkpoints |
| Pickle | `.pkl`, `.pickle`, `.dill` | Python serialization (includes Dill) |
| Joblib | `.joblib` | Scikit-learn and general ML serialization |
| NumPy | `.npy`, `.npz` | NumPy array storage formats |
| PMML | `.pmml` | Predictive Model Markup Language (XML) |
| ZIP Archives | `.zip` | Compressed model archives with recursive scanning |
| Container Manifests | `.manifest` | OCI/Docker layer scanning |
| Binary Files | `.bin` | Auto-detected format (PyTorch, ONNX, SafeTensors, etc.) |

Source: docs page, "Supported Formats → Model Formats".

### Security checks (verbatim bullets from "Security Checks Performed")

```
Malicious Code: Detecting potentially dangerous code in pickled models
Suspicious Operations: Identifying risky TensorFlow operations and custom ONNX operators
Unsafe Layers: Finding potentially unsafe Keras Lambda layers
Blacklisted Names: Checking for models with names matching suspicious patterns
Dangerous Serialization: Detecting unsafe pickle opcodes, nested pickle payloads, and decode-exec chains
Enhanced Dill/Joblib Security: ML-aware scanning with format validation and bypass prevention
Encoded Payloads: Looking for suspicious strings that might indicate hidden code
Risky Configurations: Identifying dangerous settings in model architectures
XML Security: Detecting XXE attacks and malicious content in PMML files
Embedded Executables: Detecting Windows PE, Linux ELF, and macOS Mach-O files
Container Security: Scanning model files within OCI/Docker container layers
Compression Attacks: Detecting zip bombs and decompression attacks
Weight Anomalies: Statistical analysis to detect potential backdoors
Format Integrity: Validating file format structure
License Compliance: Detecting AGPL obligations and commercial restrictions
DVC Integration: Automatic resolution and scanning of DVC-tracked models
Secrets Detection: Finding embedded API keys, tokens, and credentials
Network Analysis: Detecting URLs, IPs, and socket usage that could enable data exfiltration
JIT Code Detection: Scanning TorchScript, ONNX custom ops, and other JIT-compiled code
```

Source: docs page, "Security Checks Performed" (bullet labels preserved, bold
markup removed).

### Severity levels and sample finding (verbatim from "Interpreting Results")

```
CRITICAL: Definite security concerns that should be addressed immediately
WARNING: Potential issues that require review
INFO: Informational findings, not necessarily security concerns
DEBUG: Additional details (only shown with --verbose)
```

```
1. suspicious_model.pkl (pos 28): [CRITICAL] Suspicious module reference found: posix.system   Why: The 'os' module provides direct access to operating system functions.
```

Source: docs page, "Interpreting Results".

### CI/CD example and exit-code contract (verbatim from "Integration in Workflows")

```bash
# Example CI/CD script segment
npm install -g promptfoo
pip install modelaudit
promptfoo scan-model --format json --output scan-results.json ./models/
if [ $? -ne 0 ]; then
  echo "Security issues found in models! Check scan-results.json"
  exit 1
fi
```

```
0: No security issues found ✅
1: Security issues detected (warnings or critical) 🟡
2: Operational errors or inconclusive scans occurred (installation, file access, timeouts, no scanned files, etc.) 🔴
```

> CI/CD Best Practice: In CI/CD pipelines, exit code 1 indicates findings that
> should be reviewed but don't necessarily block deployment. Only exit code 2
> represents actual scan failures.

Source: docs page, "Integration in Workflows" and "Exit Codes". The example
and the callout disagree — see Claim 8 and contradiction #1995.

### Installation variants (verbatim from "Installation")

```bash
# Basic installation
pip install modelaudit
# With optional dependencies for specific model formats
pip install modelaudit[tensorflow,h5,pytorch]
# For all dependencies
pip install modelaudit[all]
# Or install specific components:
pip install modelaudit[tensorflow,h5,pytorch]  # Core ML frameworks
pip install modelaudit[cloud,mlflow]           # Remote model access
pip install modelaudit[numpy1]                 # NumPy 1.x compatibility
```

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/promptfoo/modelaudit:latest
# Use specific variants
docker pull ghcr.io/promptfoo/modelaudit:latest-full        # All ML frameworks
docker pull ghcr.io/promptfoo/modelaudit:latest-tensorflow  # TensorFlow only
# Run with Docker
docker run --rm -v $(pwd):/data ghcr.io/promptfoo/modelaudit:latest scan /data/model.pkl
```

### Per-format runtime dependencies (verbatim from "Requirements")

```bash
# For TensorFlow models
pip install tensorflow
# For PyTorch models
pip install torch
# For Keras models with HDF5
pip install h5py
# For YAML configuration scanning
pip install pyyaml
# For SafeTensors support
pip install safetensors
# For HuggingFace URL scanning
pip install huggingface-hub
# For cloud storage scanning
pip install boto3 google-cloud-storage
# For MLflow registry scanning
pip install mlflow
```

Source: docs page, "Requirements".

## Cross-References

### Candidate notes from `miner-related-notes.md`

1. `source-notes/docs-promptfoo-enterprise-guardrails.md` — runtime guardrail
   *enforcement* plane (HTTP endpoint, placements, aggregate `action`). Different
   security layer from static model-file scanning; no claim overlap. **Dismiss**
   as a cross-ref (complementary runtime control, not corroboration).
2. `source-notes/docs-promptfoo-evaluate-coding-agents.md` — agent eval
   workspace isolation. No overlap with model artifact scanning. **Dismiss**.
3. `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — agent
   tracing/OTLP bridge. No overlap. **Dismiss**.
4. `source-notes/docs-litellm-evals-api.md` — LiteLLM Evaluations API. No
   overlap. **Dismiss**.
5. `source-notes/docs-litellm-batches-api.md` — LiteLLM batch rate limiting.
   No overlap. **Dismiss**.
6. `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **Extends**:
   its Claim 4 documents SARIF as an export format with "no upload step, no CI
   job, and no build-blocking behavior"; this page supplies the missing
   build-blocking half (CI example + exit codes) for the model-scan family,
   though still without a complete workflow (that is #1949's child page).
7. `source-notes/blog-pagerduty-sre-agent-triage.md` — AI incident triage.
   No overlap. **Dismiss**.
8. `source-notes/docs-promptfoo-pi-scorer.md` — model-graded Pi scorer. No
   overlap. **Dismiss**.
9. `source-notes/docs-google-sre-reliable-product-launches.md` — launch
   coordination. No overlap. **Dismiss**.
10. `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — agent
    capability/safety spectrum. Different security layer (agent behavior vs
    model artifact). **Dismiss**.

### Cross-references against existing notes

- **Corroborates**: `failure-litellm-supply-chain-incident-march-2026.md`,
  Claim 14 — pin CI dependencies to verified SHAs and add an upgrade cooldown
  period. This page's mutable `ghcr.io/promptfoo/modelaudit:latest*`
  tags are exactly the kind of unpinned CI dependency that rule targets, and
  Claim 3 of that note (a compromised unpinned Trivy scanner) is the cautionary
  case for treating a security scanner as trusted-by-default.
- **Contradicts**:
  - **#1995** — the page's CI/CD Best Practice callout (exit-1 findings need
    not block; only exit 2 is a real scan failure) vs. its own blocking example
    (`if [ $? -ne 0 ]`) and vs.
    `blog-promptfoo-open-sourcing-modelaudit.md`'s Guide Impact recommendation
    to "Gate production deployments with `--strict` mode" (warnings fatal). See
    Claim 8. No verdict is asserted here.
  - No other contradictions found.
- **Extends**:
  - `blog-promptfoo-open-sourcing-modelaudit.md` — Claim 12 (SARIF/SBOM/secret
    scanning/license detection capabilities) and Claim 10 (offline, no ML
    framework dependencies). This note supplies the concrete CLI surface behind
    those capabilities: exact flags, defaults, remote-source URL schemes, and
    install variants. It does **not** re-derive the blog note's threat model,
    GHSA analysis, or detection-rate comparisons.
  - `docs-promptfoo-code-scan-cli.md` — Claim 5 (`--diffs-only` as the
    cost/coverage control), Claim 6 (`minSeverity` as the alert-fatigue knob),
    and Claim 9 (`skipReason`: an empty result is not a clean result). This
    note's `--scanners`/`--exclude-scanner`, severity levels, and "no scanned
    files = exit 2" are the model-artifact analogues of the same gate design.
  - `docs-promptfoo-code-scan-github-action.md` — Claim 5 (publish SARIF only
    when a scan actually completes). Same "gate on completion signal, not
    findings count" principle applied to model artifacts.
  - `blog-promptfoo-building-security-scanner-llm-apps.md` — Claim 10 (custom
    guidance tunes strictness vs. alert fatigue). This page's `--strict` and
    severity model are the analogous strictness controls at the model-file
    layer rather than the application-code layer.
- **Novel**: The in-place remote-source matrix (`r2://`, `models:/`,
  `https://*.jfrog.io/`, `.dvc`) — the blog note mentions only S3/GCS/HF; the
  scanner-selection and read-only/caching flag surface; the zero-scanned-files
  exit-2 gotcha; the four-level severity vocabulary and per-finding "Why"; and
  the artifact-format scope table with container-manifest/binary coverage.

## Guide Impact

- **Chapter 06 §Supply-chain security for LLM infrastructure**: Add a
  "Scan model artifacts where they are stored" subsection. Use Claim 2's
  remote-source matrix to show that the gate can point at the registry/bucket/
  DVC path instead of downloading weights to the runner, and Claim 6's scope
  table to state explicitly which artifact formats the gate covers — and
  therefore which it silently misses. Add Claim 7's non-pickle checks
  (zip bombs, container layers, embedded executables, secrets, AGPL) as the
  declared coverage, with weight-anomaly backdoor detection marked emerging.
  Tie the scanner image to the chapter's existing pin rule: `latest*` GHCR tags
  are mutable, so pin by digest (Claim 10; corroborates
  `failure-litellm-supply-chain-incident-march-2026.md`, Claim 14).
- **Chapter 06 §Gating on LLM security scans**: Extend the existing "gate on
  the scan's completion signal, never on its findings count" rule to model
  artifacts. A model scan that matches zero files exits 2, not 0 (Claim 9), so
  an empty glob must fail the gate rather than publish a clean result — the
  model-scan counterpart of the code-scan `skipReason`/SARIF rule
  (`docs-promptfoo-code-scan-cli.md`, Claim 9;
  `docs-promptfoo-code-scan-github-action.md`, Claim 5). Do **not** adopt the
  page's example verbatim: it blocks on any nonzero while its own callout says
  findings need not block (Claim 8, contradiction #1995). State the gate policy
  as severity-filtered (hard-fail exit 2; fail on CRITICAL, optionally WARNING)
  pending the #1995 verdict, and keep `--strict` for a promotion gate.
- **Chapter 05 §CI/CD supply-chain isolation**: Add model-artifact scanning as
  a pipeline stage alongside application-code scanning, using Claim 3 to split
  per-PR scans (selected scanners, changed files) from scheduled full scans,
  and Claim 4's `--no-write`/`--no-cache` for read-only ephemeral runners. Note
  that the scanner's `cloud`/`mlflow` extras and `latest-full` image change
  runner size and format coverage (Claim 10), so the stage's image choice is a
  coverage decision, not just a cost decision.

## Extraction Notes

- Source fetched 2026-11-02 from the live page. It is living vendor
  documentation with no publish date; `date_published` is `null` and flag names
  are recorded as of the extraction date (footer: last updated 2026-11-02 by
  renovate[bot]).
- Per Prospector triage, this is an **index-only** extraction: I did not
  re-derive the pickle-RCE argument, blocklist-vs-allowlist analysis, GHSA
  list, or detection-rate comparisons (settled in
  `blog-promptfoo-open-sourcing-modelaudit.md`, #553). Child pages
  `/docs/model-audit/ci-cd` (#1949) and `/docs/model-audit/scanners` (#1950)
  own the workflow YAML and per-scanner internals; I did not mine them here.
- Count reconciliation: this page says 30+ specialized file format scanners
  while the blog note says 42+ formats. These are different units (scanners
  vs. formats), so I did **not** file this as a contradiction; the guide should
  cite each with its own unit and not blend them.
- One contradiction **was** filed: #1995 (exit-1 gate policy vs. the page's own
  blocking example and the blog note's `--strict` advice). The page's CI example
  and its "CI/CD Best Practice" callout are both quoted in Concrete Artifacts.
- Quotes were copied character-for-character from the rendered page. Code-block
  line breaks were restored where the fetch conversion collapsed them; the
  command/comment text itself is unchanged. Table artifacts are reproduced from
  the page's tables with markup normalized.
- `confidence_overall` is **emerging**: the flag/URL/exit-code surface is
  documented and string-checkable (settled as a spec), but there is no
  independent validation of detection quality, the counts are vendor-defined,
  the CLI is drift-prone living docs, and the page contradicts itself on gate
  policy.
- No source-note PR is opened for this file alone; registry indexes are left to
  the post-merge rebuild.
