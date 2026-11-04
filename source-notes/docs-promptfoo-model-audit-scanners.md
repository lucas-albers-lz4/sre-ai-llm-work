---
source_url: https://www.promptfoo.dev/docs/model-audit/scanners
source_type: docs
title: "Promptfoo ModelAudit — Scanners: Per-Format Artifact Checks, Resource-Exhaustion Controls, and the Skops CVE Gate"
author: "Promptfoo (vendor documentation)"
date_published: null
date_extracted: 2026-11-04
last_checked: 2026-11-04
status: current
confidence_overall: emerging
issue: "#1950"
---

# Promptfoo ModelAudit — Scanner Catalogue (per-format checks)

> The catalogue behind the ModelAudit architecture claim: a per-format mapping of
> which model artifact types carry deserialization/code-execution risk, what each
> scanner checks, which checks are resource-exhaustion (DoS) defences rather than
> RCE controls, and the explicit `skops < 0.12.0` version gate for three named
> CVEs. It is documentation of a vendor's own tool — a checklist, not independent
> validation — but it is the concrete "which file extensions are code, not data"
> table the guide currently lacks.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "Model Audit >
  Scanners" reference page; living docs, no publish date, footer "Last updated on
  **Nov 4, 2026** by **renovate\[bot\]**").
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team/security
  vendor that ships ModelAudit inside `promptfoo`. Authoritative as a
  *specification* of what scanners exist and which checks each claims to perform
  at the extraction date; every scanner name, flag, file extension, threshold
  default, and CVE ID is string-checkable against the installed tool and public
  advisories. It is **not** measurement: the page publishes no detection rate,
  false-positive rate, bypass analysis, or independent validation for any
  scanner. Per Prospector triage, treat the check lists as documentation claims.
- **Scope**: Covers the scanner-selection surface (`--list-scanners`,
  `--scanners`, `--exclude-scanner`) and 30+ per-format scanners: pickle,
  TF SavedModel, TFLite, TensorRT, Keras H5, Keras ZIP, ONNX, OpenVINO, PyTorch
  ZIP, ExecuTorch, GGUF/GGML, joblib, skops, Flax/JAX, JAX checkpoints, NumPy,
  OCI layers, manifests, text, Jinja2, metadata, PyTorch binary, ZIP/TAR/7-Zip,
  weight distribution, SafeTensors, PaddlePaddle, XGBoost, PMML, plus auto format
  detection, license/SBOM, network, secrets, JIT, and HuggingFace URL handling.
  Does **not** cover the pickle-RCE threat-model argument, blocklist-vs-allowlist
  architecture, GHSA bypasses, or detection-rate comparisons — those are settled
  in `blog-promptfoo-open-sourcing-modelaudit.md` (#553). The run/CI mechanics
  live in the sibling pages `/docs/model-audit` (#1948) and
  `/docs/model-audit/ci-cd` (#1949).
- **Relationship to sibling pages**: this is the child page that
  `docs-promptfoo-model-audit.md` explicitly did **not** mine (#1950). It should
  be cited for the per-format catalogue; #1948 owns the CLI surface and #1949
  the pipeline wiring.

## Extracted Claims

### Claim 1: Scanner selection is an enumerated, version-dependent control surface — `--list-scanners` shows the IDs supported by the *installed* version, then `--scanners` / `--exclude-scanner` narrow or subtract from that set
- **Evidence**: The "Selecting Scanners" section gives the three-step mechanism
  and three example commands, and states the web UI exposes the same catalog in
  Advanced Scan Options.
- **Confidence**: settled (documented CLI contract; checkable against the
  installed command)
- **Quote**: "Use `--list-scanners` to see the scanner IDs supported by your installed ModelAudit version. Then pass IDs or class names to `--scanners` to run only those scanners, or use `--exclude-scanner` to remove scanners from the default set."
- **Our assessment**: Buy the mechanism, **not a frozen scanner list**. The page
  itself says the IDs come from the installed version, so a gate that hard-codes
  `--scanners pickle,tf_savedmodel` is pinning against one release's vocabulary.
  The operational rule is to enumerate the scanner IDs in CI and assert the
  expected coverage set rather than assume the default set is stable. This
  extends the same flags documented on the parent page
  (`docs-promptfoo-model-audit.md`, Claim 3) with the actual catalog they select
  from, and it makes scanner coverage a versioned supply-chain fact.

### Claim 2: The pickle scanner covers the executable-at-load formats (`.pkl`, `.pickle`, `.dill`, `.pt`, `.pth`, `.ckpt`, and pickle-bearing `.bin`) and flags dangerous modules, functions, opcodes, embedded executables, network indicators, credentials, and JIT/script patterns
- **Evidence**: The "Pickle Scanner" section lists the file types and the key
  checks — suspicious module imports (`os`, `subprocess`, `sys`), dangerous
  functions (`eval`, `exec`, `system`), malicious opcodes (`REDUCE`, `INST`,
  `OBJ`, `NEWOBJ`, `STACK_GLOBAL`), encoded payloads, embedded executables,
  network patterns, embedded credentials, and JIT/script execution.
- **Confidence**: settled (documented check list; format coverage is a spec, not
  an efficacy measurement)
- **Quote**: "Pickle files are a common serialization format for ML models but can execute arbitrary code during unpickling. Attackers can craft malicious pickle files that execute harmful commands when loaded."
- **Our assessment**: Buy the file-type mapping and the check categories as the
  catalogue's answer to "which files are code." This note does not re-argue the
  threat model (settled in the blog note, Claim 1); the delta is the concrete
  extension list and that `.pt/.pth/.ckpt` appear under *both* the pickle and
  PyTorch-ZIP scanners, so coverage is not one-scanner-per-extension. The check
  list is a blocklist-style enumeration of dangerous names/opcodes; the blog note
  argues allowlist-first is more robust, so the guide should not read this list
  as proof of completeness.

### Claim 3: TensorFlow SavedModel and TFLite scanners target in-graph execution surfaces — `PyFunc`, filesystem/system operations, custom ops, the Flex delegate, executable metadata, and buffer tampering
- **Evidence**: The SavedModel scanner lists "Operations that allow arbitrary
  code execution (e.g., `PyFunc`)" and file I/O/exec operations; the TFLite
  scanner lists custom operations, Flex delegate ops, executable model metadata,
  suspicious operator configurations, and buffer validation.
- **Confidence**: settled (documented check list)
- **Quote**: "While TensorFlow Lite models are generally safer than full TensorFlow models due to their limited operator set, they can still include custom operations or use the Flex delegate to access the full TensorFlow runtime, potentially introducing security risks."
- **Our assessment**: Buy it as the format-specific control description. The
  important operational point is that "safer format" is relative: TFLite's
  reduced operator set is a real mitigation, but the Flex delegate deliberately
  re-expands the runtime, so a gate must know whether Flex is permitted in its
  models. SavedModel's `PyFunc` is the clearest case of an in-graph escape hatch
  — the artifact is nominally data but contains a callable. The page gives no
  false-positive data for these checks, so treat them as declared coverage.

### Claim 4: TensorRT engine files are treated as potentially executable containers — the scanner looks for embedded shared libraries (`.so`), plugin references, script-execution patterns, and suspicious paths
- **Evidence**: The TensorRT scanner's key checks: suspicious paths (`/tmp/`,
  `../`), embedded shared-library references, `exec`/`eval` script patterns, and
  unauthorized plugin references.
- **Confidence**: settled (documented check list)
- **Quote**: "TensorRT engines can contain custom plugins and operations. While generally safer than pickle files, they could be crafted to include malicious plugins or reference unauthorized system resources."
- **Our assessment**: Buy the taxonomy. `.engine`/`.plan` files are usually
  treated as opaque GPU blobs, but the page explicitly models them as able to
  reference loadable code and unauthorized paths. That is exactly the
  "extension is not a safety class" point. No evidence is offered that these
  checks catch real TensorRT attacks, so this is a control to name, not a
  validated detector.

### Claim 5: Keras models carry Python through Lambda layers in both formats — H5 stores unsafe Lambda layers, and the Keras 3 `.keras` ZIP stores them as base64-encoded functions that execute during inference
- **Evidence**: The Keras H5 scanner flags unsafe Lambda layers and embedded
  code; the Keras ZIP scanner specifically lists "Unsafe Lambda layers with
  base64-encoded Python code" and executables hidden in the archive.
- **Confidence**: settled (documented check list; format behavior is a
  specification of Keras)
- **Quote**: "The new `.keras` ZIP format stores Lambda layers as base64-encoded functions that execute during inference. Malicious actors could embed arbitrary code in these layers or hide executables within the archive structure."
- **Our assessment**: Buy it. This is the non-obvious Keras case: migrating from
  H5 to the newer `.keras` ZIP does not remove executable content, it changes the
  encoding. A model gate that only inspects pickle would miss a Keras Lambda
  layer entirely. The guide should use Keras as the concrete example that
  "safe-ish framework format" still embeds user code by design.

### Claim 6: ONNX and OpenVINO scanners target external-data references and custom operators — path traversal via external data files, custom-op code, malformed XML, and plugin references
- **Evidence**: ONNX checks custom operators, external data references and path
  traversal, tensor size/data integrity, and file-size mismatches. OpenVINO
  checks custom layers, external data path traversal, malformed/oversized XML,
  dangerous layer types, and plugin references.
- **Confidence**: settled (documented check list)
- **Quote**: "ONNX models can reference external data files and custom operators. Malicious actors could exploit these features to include harmful custom operations or manipulate external data references to access unauthorized files on the system."
- **Our assessment**: Buy the taxonomy. The distinctive risk here is not
  deserialization RCE but *reference resolution*: a model file points at external
  data, and a traversal path makes the loader read outside the intended
  directory. That is a different failure class from pickle and argues for a
  format-specific check rather than one generic "unsafe model" verdict. Again,
  no efficacy data on the page.

### Claim 7: Container/archive-style model formats inherit pickle risk through embedded pickles — PyTorch ZIP, ExecuTorch, PaddlePaddle, and XGBoost binary models are unpacked and scanned for embedded pickled data and bundled code
- **Evidence**: PyTorch Zip scanner checks "Malicious pickle files embedded within
  the PyTorch model"; ExecuTorch checks embedded pickle files and bundled Python
  or executables; PaddlePaddle checks embedded pickle data; XGBoost notes
  "Pickle-based custom functions in binary models."
- **Confidence**: settled (documented check list)
- **Quote**: "PyTorch models are essentially ZIP archives containing pickled objects, which can include malicious code. The scanner unpacks these archives and applies pickle security checks to the contents."
- **Our assessment**: Buy it. This is the structural reason a format-level gate
  must recurse: `.pt` is not one format, it is a container around pickle (and
  sometimes code). ExecuTorch is a useful reminder that edge/mobile deployment
  targets are not safer — they just have less monitoring. The catalogue's
  answer is to unpack and re-dispatch to the appropriate scanner, which is the
  right shape for an artifact gate.

### Claim 8: GGUF/GGML scanning includes explicit resource limits and decompression-bomb checks alongside header, metadata, and tensor-integrity validation — i.e. DoS defence, not only RCE defence
- **Evidence**: The GGUF/GGML scanner key checks include "Resource limits:
  Enforces security limits to prevent denial-of-service attacks" and
  "Compression validation: Checks for reasonable tensor sizes and prevents
  decompression bombs," plus header validation, metadata security, and tensor
  integrity.
- **Confidence**: settled (documented check list)
- **Quote**: "While generally safer than pickle formats, they can still contain malicious metadata or be crafted to cause resource exhaustion attacks."
- **Our assessment**: Buy it, and treat the distinction as the important one:
  GGUF is not a pickle-RCE format, but loading it is still an untrusted parse on
  the hot path, so oversized tensors/decompression are availability threats to
  the scanner runner and the serving host. This is the artifact-level analogue
  of the chapter's existing compute-DoS caution. The page gives no numeric
  ratio/dimension defaults for GGUF, so the guide can name the control but not
  cite a threshold from here.

### Claim 9: The joblib scanner is explicitly a compression-bomb defence — it detects suspicious compression ratios, enforces maximum decompressed size, distinguishes ZIP from compressed pickle, and scans the embedded pickle
- **Evidence**: The Joblib scanner key checks: compression bomb detection, size
  limits, format validation, and embedded-pickle decompression-and-scan.
- **Confidence**: settled (documented check list)
- **Quote**: "Additionally, malicious actors could craft compression bombs that consume excessive memory or CPU resources when loaded. The scanner provides safe decompression with security limits."
- **Our assessment**: Buy it. This is one of the clearest "the scanner is itself
  exposed to the artifact" cases: to inspect a joblib you must decompress it, so
  the decompressor needs a bound. The page does not publish the numeric ratio or
  size limit, so the guide should describe the control and require the operator
  to configure/verify the limit rather than quote a default. It corroborates the
  sibling page's zip-bomb/`--max-size`/`--timeout` guidance
  (`docs-promptfoo-model-audit.md`, Claim 7 / Claim 4).

### Claim 10: The skops scanner hard-gates on version — it detects CVE-2025-54412, CVE-2025-54413, and CVE-2025-54886 and flags vulnerable skops versions `< 0.12.0`, because the vulnerabilities are RCE via malicious sklearn estimators, `ColumnTransformer`, and callable estimator arguments
- **Evidence**: The Skops scanner explicitly lists the three CVE IDs, "Version
  detection for vulnerable skops versions (< 0.12.0)," and dangerous sklearn
  components (`Pipeline`, `ColumnTransformer`, `FunctionTransformer`).
- **Confidence**: settled (named CVEs are checkable facts; the page does not
  give CVSS or exploitation detail)
- **Quote**: "Skops versions before 0.12.0 contain multiple critical vulnerabilities allowing remote code execution through specially crafted sklearn estimators."
- **Our assessment**: Buy it as the page's most checkable, non-vendor-opinion
  content: a specific version boundary tied to specific CVE IDs. The guide can
  present this as the model-artifact version-gate example — a safe format
  (`.skops`, built to avoid pickle) is not a safe loader until the library is
  patched. The page lists no CVSS scores, so cite the IDs and the `< 0.12.0`
  boundary, not a severity number from this source.

### Claim 11: Flax/JAX and JAX checkpoint scanners treat custom restore functions and experimental callbacks as execution surfaces — Orbax metadata can carry arbitrary restore functions run at load time
- **Evidence**: The Flax/JAX scanner checks MessagePack structures, embedded code,
  recursive structures, and unusual types; the JAX checkpoint scanner checks
  `jax.experimental.host_callback.call`, "Custom restore functions in Orbax
  checkpoint metadata," dangerous pickle opcodes, directory structure, and
  resource limits.
- **Confidence**: settled (documented check list)
- **Quote**: "Orbax checkpoints may include metadata with arbitrary restore functions that execute during model loading."
- **Our assessment**: Buy it. This is a less-obvious execution path than pickle:
  the checkpoint metadata, not the tensor data, names the callable. It extends
  the "model files are executable at load time" claim (blog note, Claim 1) to a
  framework that is often assumed to be pickle-free. The page's check is
  name/pattern based, so it inherits the completeness limits of a blocklist.

### Claim 12: NumPy scanning separates two risks — object arrays can carry arbitrary Python objects (code), while dimensions/size limits are DoS controls
- **Evidence**: The NumPy scanner key checks: array validation, header integrity,
  dangerous data types such as object arrays, size validation, and dimension
  limits.
- **Confidence**: settled (documented check list)
- **Quote**: "Object arrays can contain arbitrary Python objects (including code), and extremely large arrays can cause denial-of-service attacks."
- **Our assessment**: Buy it. NumPy is commonly treated as inert numeric data, so
  the object-array case is the surprising one: the array is a container for
  arbitrary objects and therefore inherits their deserialization semantics.
  The dimension caps are a DoS bound rather than a code-execution control, which
  is the same split as GGUF/joblib. No numeric dimension limit is published here.

### Claim 13: The archive and container scanners (ZIP, TAR, 7-Zip, OCI layers) are traversal/bomb/nesting controls — they reject `..` and absolute paths, flag compression ratios over 100x, cap nested-archive recursion depth, and recursively re-scan extracted model files
- **Evidence**: ZIP checks directory traversal, "Zip bombs ... compression ratios
  (>100x)," nested archives up to a configurable depth, and per-file dispatch to
  the appropriate scanner. TAR adds symlink attacks and TAR bombs. 7-Zip adds
  encryption and memory/CPU limits. OCI layers safely extract `.tar.gz` layers,
  validate manifests, recursively scan, and prevent traversal.
- **Confidence**: settled (documented check list; the >100x ratio is a stated
  threshold for the ZIP scanner)
- **Quote**: "ZIP archives are commonly used to distribute models and datasets. Malicious actors can craft ZIP files that exploit extraction vulnerabilities, contain malware, or cause resource exhaustion."
- **Our assessment**: Buy it. This is where the catalogue makes the "scan the
  artifact, not just the model file" argument concrete: an OCI image, a `.zip`,
  or a `.tar.gz` can hide a malicious model in a layer, and the extraction step
  is itself an attack surface (traversal, symlink escape, bomb, infinite
  recursion). The 100x ratio is the one numeric limit the page states for ZIP;
  it is a detection heuristic, not a guarantee, so treat it as a starting
  threshold to verify.

### Claim 14: Configuration, template, text, and metadata scanners extend the gate to non-weight files — manifest checks for network/filesystem/execution/credential patterns, Jinja2 checks for SSTI including CVE-2024-34359, and metadata/text checks for hidden payloads and embedded secrets
- **Evidence**: The Manifest scanner blacklists model names and looks for network,
  filesystem, code-execution, and credential patterns; the Jinja2 scanner
  detects SSTI and "CVE-2024-34359 exploitation in GGUF chat templates"; the Text
  and Metadata scanners check for oversized/hidden data, embedded credentials,
  suspicious URLs, and misleading descriptions.
- **Confidence**: settled (documented check list; CVE ID checkable)
- **Quote**: "CVE-2024-34359 affects llama-cpp-python when loading malicious chat templates. Template injection allows full system compromise."
- **Our assessment**: Buy it. The guide-relevant point is that the deployable
  artifact is not just weights: chat templates, `config.json`, model cards, and
  README instructions all ship with the model and can carry injection or
  credential leakage. Jinja2 SSTI in a GGUF chat template is the concrete case
  that a "safe" GGUF container can still deliver a template-injection payload
  when a downstream loader renders it. No exploitation detail is given here, but
  the CVE ID is verifiable.

### Claim 15: The weight-distribution scanner is the only behavioural/statistical check, and its LLM path is disabled by default — thresholds are Z-score 3.0, cosine similarity 0.7, magnitude 3.0, `llm_vocab_threshold` 10,000, and `enable_llm_checks: false`
- **Evidence**: The Weight Distribution scanner's configuration-options list
  states the defaults explicitly, and "Special handling for LLMs" says LLM
  checking must be enabled.
- **Confidence**: emerging (documented defaults are settled as a spec; the
  backdoor-detection efficacy is a vendor claim with no methodology or
  false-positive data on this page)
- **Quote**: "LLM checking is disabled by default but can be enabled via configuration."
- **Our assessment**: Buy the defaults (they are checkable config keys); do not
  buy the detection-efficacy implication. The operational caveat is the headline:
  the scanner's flagship "backdoor detection" feature does nothing for LLMs
  unless `enable_llm_checks` is explicitly turned on, so a clean default scan is
  not evidence of a clean LLM. Even when enabled, the page gives thresholds but
  no validation, so this is a supplementary signal, not a substitute for
  provenance/allowlist controls.

### Claim 16: Auto format detection routes scanners by magic bytes and content rather than file extension, because a `.bin` can be pickle, SafeTensors, ONNX, PyTorch ZIP, or raw tensors
- **Evidence**: The "Auto Format Detection" section lists pickle magic bytes,
  SafeTensors JSON headers, ONNX protobuf signatures, PyTorch ZIP `PK` headers,
  and raw tensors as the detected classes; it states detection uses magic-byte
  analysis and content-based routing.
- **Confidence**: settled (documented behavior)
- **Quote**: "This allows ModelAudit to automatically apply the correct scanner based on the actual file content, not just the extension."
- **Our assessment**: Buy it. It is the right design for an artifact gate because
  extensions are attacker-controlled metadata; a malicious file can be named
  `.bin`. The guide should cite this when explaining why a scanner must inspect
  content, and pair it with Claim 1's version caveat: content routing is only as
  good as the format detectors installed.

### Claim 17: Cross-cutting scanners cover license/SBOM, network egress, secrets, and JIT/script execution — positions that are governance or exfiltration indicators rather than deserialization RCE
- **Evidence**: License checking (AGPL warnings, non-commercial
  restrictions, unlicensed content, CycloneDX SBOM); network detection
  (URLs/IPs/domains, `socket`/`urllib`/`requests` imports, `beacon_url`/
  `callback_url`/`exfil_endpoint`); secrets detection (cloud keys, JWTs, SSH
  keys, DB credentials); JIT/script detection (TorchScript, ONNX custom ops, TF
  eager execution, `eval`/`exec`/`compile`).
- **Confidence**: emerging (vendor list; no per-detector efficacy data)
- **Quote**: "AGPL requires source disclosure for network services, non-commercial licenses block commercial use, and unlicensed datasets create legal risks."
- **Our assessment**: Buy the categories as declared scope. The useful framing
  for an SRE audience is that these are different decision classes: license/SBOM
  findings are governance gates, secrets/network patterns are exfiltration
  indicators (and can be noisy), and JIT detection overlaps the execution-risk
  scanners. Do not flatten them into one severity — the guide should map them to
  separate review owners. No detection rates are published.

## Concrete Artifacts

### Scanner-selection commands (verbatim from "Selecting Scanners")

```bash
promptfoo scan-model --list-scanners
promptfoo scan-model models/ --scanners pickle,tf_savedmodel
promptfoo scan-model models/ --exclude-scanner weight_distribution
```

Source: docs page, "Selecting Scanners".

### Per-format → threat → check matrix (condensed from the scanner sections)

| Artifact format / extensions | Execution or abuse surface stated by the page | Representative checks |
|---|---|---|
| Pickle `.pkl/.pickle/.dill/.bin/.pt/.pth/.ckpt` | Arbitrary code at unpickle time | Module imports (`os`, `subprocess`, `sys`), `eval`/`exec`/`system`, opcodes (`REDUCE`, `INST`, `OBJ`, `NEWOBJ`, `STACK_GLOBAL`), embedded executables, network patterns, credentials, JIT/script |
| TF SavedModel `.pb` + dirs | In-graph execution / file + system access | `PyFunc`, embedded Python calls, file I/O, execution ops |
| TF Lite `.tflite` | Custom ops, Flex delegate re-expands runtime, executable metadata | Custom ops, Flex delegate ops, metadata content, buffer validation |
| TensorRT `.engine/.plan` | Embedded `.so`, plugin refs, script exec | Suspicious paths, `.so` refs, `exec`/`eval`, unauthorized plugins |
| Keras H5 `.h5/.hdf5/.keras` | Unsafe Lambda layers / embedded code | Lambda layers, layer configs, custom layers/metrics, dangerous strings |
| Keras ZIP `.keras` | Base64-encoded Lambda Python executes at inference | Base64 Lambda code, embedded Python/executables, config JSON patterns |
| ONNX `.onnx` | Custom ops; external-data path traversal; tampering | Custom ops, external-data refs, tensor size/integrity, size mismatch |
| OpenVINO IR `.xml/.bin` | Custom layers, external refs, malformed XML, plugins | Custom layers, path traversal, XML structure/size, dangerous layer types |
| PyTorch ZIP `.pt/.pth` | ZIP of pickled objects + bundled code | Embedded pickles, Python files, executables, serialization patterns |
| ExecuTorch `.pte/.pt` | Embedded pickle/code on edge targets | Embedded pickles, bundled Python/executables, custom ops, metadata |
| GGUF/GGML `.gguf/.ggml/.ggmf/.ggjt/.ggla/.ggsa` | Malicious metadata; resource exhaustion / decompression bombs | Header, metadata, tensor integrity, resource limits, compression validation |
| Joblib `.joblib` | Compression bombs; embedded pickle | Compression-ratio detection, max decompressed size, format validation, pickle scan |
| Skops `.skops/.pkl` | CVE-2025-54412 / -54413 / -54886 RCE; vulnerable `< 0.12.0` | CVE rules, version detection, dangerous sklearn components, malicious callables |
| Flax/JAX `.msgpack/.flax/.orbax/.jax` | Crafted MessagePack, embedded code, recursion/exhaustion | MessagePack structures, embedded code, nested/oversized structures |
| JAX checkpoint `.ckpt/.checkpoint/.orbax-checkpoint/.pickle` | Custom restore functions, `host_callback` | Dangerous JAX ops, Orbax restore metadata, opcodes, directory structure, limits |
| NumPy `.npy/.npz` | Object arrays carry arbitrary objects; huge arrays DoS | Array validation, header integrity, object dtype, size/dimension limits |
| OCI/Docker `.manifest` + `.tar.gz` layers | Hidden malicious models in layers; traversal | Layer extraction, manifest validation, recursive scan, path validation |
| Manifests `.json/.yaml/.yml/.xml/.toml/.config` | Network/filesystem/exec/credential config | Blacklisted model names, network/file/exec/credential patterns |
| Text `.txt/.md/.markdown/.rst` | Hidden data in oversized files | Size check, file-type ID, content validation |
| Jinja2 `.gguf/.json/.yaml/.yml/.jinja/.j2/.template` | SSTI; CVE-2024-34359 in GGUF chat templates | SSTI patterns, dangerous filters/functions, unrestricted variable access |
| Metadata `README.md/MODEL_CARD.md/METADATA.md` | Embedded secrets, malicious links, deceptive docs | Credentials, suspicious URLs, malicious repo refs, vulnerable versions |
| PyTorch binary `.bin` | Embedded code/executables (PE/ELF/Mach-O) | Code patterns, executable signatures, shebangs, tensor structure |
| SafeTensors `.safetensors/.bin` | Malicious metadata / encoded payloads | Header JSON, metadata, tensor/offset integrity |
| PaddlePaddle `.pdmodel/.pdiparams` | Custom ops; embedded pickle | Suspicious ops, embedded pickle, custom ops, executable content |
| XGBoost `.bst/.model/.json/.ubj` | Pickled custom functions; embedded code | Custom objectives/metrics, embedded code, callbacks, path traversal |
| PMML `.pmml` | XXE / external resource refs / scripts | `DOCTYPE`/`ENTITY`, defusedxml, `<script>`/`eval`, external URLs |
| ZIP `.zip/.npz` | Traversal, zip bombs (>100x), nested recursion | `..`/absolute paths, ratio >100x, nested-archive depth, per-file rescan |
| TAR `.tar/.tar.gz/.tgz/.tar.bz2` | Traversal, symlink escape, TAR bombs | Traversal, symlinks, bomb ratios, recursive rescan |
| 7-Zip `.7z` | Compression bombs, encryption hides content | Traversal, bomb ratios, encryption, nested archives, memory/CPU limits |

Source: docs page, each scanner section (file types, "Key checks", and "Why it
matters"). This is a condensed catalogue; the page also lists SafeTensors,
PaddlePaddle, XGBoost, and PMML scanners in full.

### Weight-distribution defaults (transcribed from "Weight Distribution Scanner → Configuration options")

```text
z_score_threshold:           default 3.0 (higher for LLMs)
cosine_similarity_threshold: default 0.7
weight_magnitude_threshold:  default 3.0 standard deviations
llm_vocab_threshold:         default 10,000
enable_llm_checks:           default false
```

Source: docs page, "Weight Distribution Scanner → Configuration options". The
page notes LLM checking "is disabled by default but can be enabled via
configuration."

### Named CVE → version gate (verbatim from "Skops Scanner → Key checks")

```text
CVE-2025-54412: Remote code execution via malicious sklearn estimator
CVE-2025-54413: Arbitrary code execution through sklearn.compose.ColumnTransformer
CVE-2025-54886: Code execution via callable arguments in estimators
Version detection for vulnerable skops versions (< 0.12.0)
```

Source: docs page, "Skops Scanner".

### Archive/resource-exhaustion limits (verbatim fragments from "Key checks")

```text
ZIP:   "Zip bombs: Identifies files with suspicious compression ratios (>100x)
        that could cause resource exhaustion"
       "Nested archives: Scans ZIP files within ZIP files up to a configurable
        depth to prevent infinite recursion attacks"
TAR:   "Symlink attacks that could point to sensitive system files"
       "TAR bombs with excessive file counts or decompression ratios"
7-Zip: "Compression bombs with suspicious ratios"
       "Resource limits for memory and CPU usage"
GGUF:  "Resource limits: Enforces security limits to prevent denial-of-service
        attacks"
Joblib:"Size limits: Enforces maximum decompressed size limits to prevent
        memory exhaustion"
NumPy: "Dimension limits: Enforces reasonable limits on array dimensions to
        prevent DoS attacks"
```

Source: docs page, the respective scanner "Key checks" lists.

### Cross-cutting detection categories (transcribed and condensed)

```text
License:  AGPL Warnings; Commercial Restrictions; Unlicensed Content;
          SBOM Generation (CycloneDX)
Network:  URL patterns (HTTP(S), FTP, SSH, WebSocket); IPv4/IPv6 addresses;
          Domain names; socket/urllib/requests and 50+ libraries;
          C&C patterns (beacon_url, callback_url, exfil_endpoint)
Secrets:  API keys (AWS/Azure/GCP/OpenAI); JWT/OAuth/GitHub tokens;
          hardcoded passwords; SSH/SSL/private keys; DB connection strings;
          Slack/Discord webhook URLs
JIT:      TorchScript; ONNX custom ops; TensorFlow eager execution;
          eval()/exec()/compile(); JavaScript/Python/shell injection
```

Source: docs page, "License Checking and Compliance", "Network Communication
Detection", "Secrets Detection", "JIT/Script Detection".

### HuggingFace URL handling (transcribed from "HuggingFace URL Support")

```text
1. Downloads the model: Uses the huggingface-hub library to download all model
   files to a temporary directory
2. Scans all files: Applies appropriate scanners to each file based on its format
3. Cleans up: Automatically removes downloaded files after scanning
```

Source: docs page, "HuggingFace URL Support". Supported forms:
`https://huggingface.co/user/model`, `https://hf.co/user/model`, `hf://user/model`.

## Cross-References

### Candidate notes from `miner-related-notes.md`

1. `source-notes/docs-promptfoo-model-audit.md` — **Extends** (primary
   sibling). Its Claim 3 documents the same `--list-scanners`/`--scanners`/
   `--exclude-scanner` flags; its Claim 6 gives the 30+ format scope table; its
   Claim 7 lists non-pickle checks (zip bombs, container layers, weight
   anomalies, AGPL). This page supplies the per-format internals behind those
   aggregate claims (the actual check lists, the skops CVE IDs, and the weight
   thresholds). Not a duplicate: #1948 is the landing page, this is the catalog.
2. `source-notes/docs-promptfoo-evaluate-coding-agents.md` — agent eval
   workspace isolation. No overlap with model-artifact static analysis.
   **Dismiss**.
3. `source-notes/docs-promptfoo-enterprise-guardrails.md` — runtime guardrail
   enforcement plane. Different security layer (runtime I/O policy vs static
   model-file scan). **Dismiss** as corroboration; complementary control.
4. `source-notes/docs-litellm-evals-api.md` — LiteLLM Evaluations API. No
   overlap. **Dismiss**.
5. `source-notes/docs-litellm-batches-api.md` — LiteLLM batch rate limiting. No
   overlap. **Dismiss**.
6. `source-notes/docs-promptfoo-enterprise-findings-reports.md` — finding
   disposition and export matrix (CSV/SARIF/Colang). No claim about model-file
   scanners; different product surface. **Dismiss**.
7. `source-notes/blog-pagerduty-sre-agent-triage.md` — AI incident triage. No
   overlap. **Dismiss**.
8. `source-notes/docs-promptfoo-pi-scorer.md` — model-graded Pi scorer. No
   overlap. **Dismiss**.
9. `source-notes/docs-google-sre-reliable-product-launches.md` — launch
   coordination engineering. No overlap. **Dismiss**.
10. `source-notes/docs-google-sre-team-lifecycles.md` — SRE team lifecycles. No
    overlap. **Dismiss**.

### Cross-references against existing notes

- **Corroborates**:
  - `blog-promptfoo-open-sourcing-modelaudit.md`, Claim 1 — "Model files are
    executable at load time." Every execution-capable scanner section in this
    catalogue (pickle opcodes, SavedModel `PyFunc`, Keras Lambda layers, JAX/
    Orbax restore functions) is a concrete format-level instance of that same
    claim. This page adds detail; it does not re-argue the thesis.
  - `blog-promptfoo-open-sourcing-modelaudit.md`, Claim 6 — format-specific
    analysis across 42+ formats. This page is the enumeration of that coverage
    (though the page's own scanner count is lower than 42; see Extraction Notes).
- **Contradicts**: None. No existing note makes a claim this page opposes. The
  page's per-format check lists are additive to the blog note's architecture
  argument, and the differing "42+ formats" (blog) vs. scanner-count (this page)
  is a units mismatch already reconciled in `docs-promptfoo-model-audit.md`
  Claim 6, not a contradiction. No contradiction issue filed.
- **Extends**:
  - `docs-promptfoo-model-audit.md`, Claim 3 (scanner selection), Claim 6
    (30+ format scope), Claim 7 (non-pickle checks: zip bombs, container layers,
    weight anomalies, secrets, AGPL). This note is the detailed catalogue behind
    those summaries.
  - `docs-promptfoo-model-audit-ci-cd.md` — its CI wiring (changed-file scans,
    `--strict`, scheduled `--sbom`) is the *enforcement* half; this note is the
    *coverage* half those workflows select from via `--scanners`.
  - `blog-promptfoo-open-sourcing-modelaudit.md`, Claim 12 — CVE detection
    rules, SBOM, secret scanning, license detection. This page names the actual
    CVE rules (skops trio, CVE-2024-34359) and the license/secret detector
    categories behind that capability claim.
  - `failure-litellm-supply-chain-incident-march-2026.md`, Claim 3 and Claim 14 —
    the security scanner itself is a supply-chain dependency and must be pinned.
    This catalogue makes scanner coverage version-dependent (Claim 1), which is
    the same reason a scanner version/image must be pinned and its coverage set
    asserted in CI.
- **Novel**: The per-format control checklist itself (which checks each format
  gets), the named skops CVE trio and the `< 0.12.0` version gate, CVE-2024-34359
  for GGUF chat templates, the weight-distribution threshold defaults with
  `enable_llm_checks: false`, and the explicit split between RCE checks and
  resource-exhaustion limits (joblib/GGUF/NumPy/archives).

## Guide Impact

- **Chapter 06 §Supply-chain security for LLM infrastructure**: Add a **model
  artifact format → threat** table drawn from Concrete Artifacts, so the section
  stops treating "scan dependencies/code" as the whole supply chain. Name the
  execution-capable formats explicitly — pickle family, Keras Lambda layers,
  TF SavedModel `PyFunc`, TensorRT embedded `.so`/plugins, ONNX/OpenVINO
  external-data traversal, Orbax restore functions — and state that a model gate
  must be per-format and recursive (PyTorch ZIP, ExecuTorch, OCI layers). Cite
  this note (Claims 2–7, 11, 13). Do not restate the pickle-RCE thesis; cite
  `blog-promptfoo-open-sourcing-modelaudit.md` Claim 1 for it.
- **Chapter 06 §Gating on LLM security scans**: Add the **artifact-level gate**
  alongside the existing code-scan gate. Two concrete rules this page supports:
  (a) enumerate scanner coverage from the installed tool (`--list-scanners`) and
  assert the expected set in CI, because scanner IDs and coverage are
  version-dependent (Claim 1); (b) treat resource-exhaustion controls as part of
  the gate config — compression-bomb/size/dimension/nesting limits are DoS
  defences, not optional hardening (Claims 8, 9, 12, 13). Cite the zip-bomb
  `>100x` heuristic as a starting threshold, not a guarantee.
- **Chapter 06 §Pin everything; verify releases**: Extend the existing pin rule
  to the model scanner itself. Since coverage is a property of the installed
  scanner version (Claim 1), pin the scanner image/package by digest and record
  its scanner inventory; a floating `latest` silently changes what the gate can
  see. This corroborates `failure-litellm-supply-chain-incident-march-2026.md`
  Claim 3/Claim 14.
- **Chapter 05 §CI/CD supply-chain isolation**: Add model-artifact scanning as a
  pipeline stage, using the format→threat table to scope which file extensions
  trigger which scanner set, and note that config/template/metadata files
  (Claim 14) belong in scope too — a "model-only" extension glob misses the
  Jinja2 chat template and manifest surfaces. The workflow wiring itself lives in
  `docs-promptfoo-model-audit-ci-cd.md`.
- **Chapter 06 (new example, version gate)**: Use the skops trio
  (CVE-2025-54412/-54413/-54886, `< 0.12.0`) as the concrete "a safe format is
  not a safe loader" example: `.skops` exists to avoid pickle, yet the loader
  library still needs a version floor (Claim 10). Pair with the
  `enable_llm_checks: false` caveat (Claim 15) to warn that default scanner
  settings can leave LLM-specific checks off.

## Extraction Notes

- Source fetched 2026-11-04 from the live page (footer: last updated 2026-11-04
  by renovate\[bot\]). It is living vendor documentation with no publish date;
  `date_published` is `null`, and scanner IDs/flags are recorded as of the
  extraction date.
- Per Prospector triage, this is the **catalogue half** of the ModelAudit docs:
  I did not re-derive the pickle-RCE argument, blocklist-vs-allowlist
  architecture, GHSA history, or detection-rate comparisons (settled in
  `blog-promptfoo-open-sourcing-modelaudit.md`, #553). I also did not re-extract
  the CLI surface (#1948) or CI workflow YAML (#1949); I cite those notes.
- **Count reconciliation**: the blog note says "42+ formats" (#553 Claim 6); the
  parent landing page says "30+ specialized file format scanners" (#1948
  Claim 6); this page does not state a total but enumerates ~30 scanner
  sections. These are different units (formats vs. scanners) and a moving
  living-docs target. I did **not** file a contradiction; the guide should cite
  each with its own unit and not blend the numbers.
- **Vendor-claim caution**: every "Key checks" list is promptfoo's description
  of its own tool. The page publishes no detection rate, false-positive rate,
  bypass review, or field validation for any scanner. I graded those claims
  `settled` only where they are checkable specifications (file extensions,
  flags, config defaults, CVE IDs) and `emerging` where they imply detection
  efficacy (weight-distribution backdoors, cross-cutting detectors). No
  independent corroboration was found in the corpus.
- Quotes were copied character-for-character from the rendered page. The
  per-format matrix is a condensed rewrite of the page's scanner sections with
  the page's own terminology; it is not presented as a verbatim quote. The
  archive-limits artifact quotes fragments from the "Key checks" bullets, with
  line breaks normalized.
- No contradiction issue was filed: the only numeric tension (42+ vs 30+) is a
  units mismatch already documented by the sibling notes, not opposing claims.
- No source-note PR is opened for this file alone; registry indexes are left to
  the post-merge rebuild.
