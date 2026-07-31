---
source_url: https://docs.litellm.ai/blog/security-update-march-2026
source_type: failure-report
platform: blog
title: "Security Update: Suspected Supply Chain Incident"
author: "Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-03-24
date_extracted: 2026-07-31
last_checked: 2026-07-31
status: current
confidence_overall: settled
issue: "#687"
---

# Failure Report: LiteLLM PyPI Supply Chain Compromise — Credential Stealer in v1.82.7/v1.82.8 (March 2026)

> The LiteLLM supply-chain incident report: PyPI packages `litellm==1.82.7` and
> `litellm==1.82.8` shipped a credential stealer (harvesting env vars, SSH keys,
> cloud/DB credentials, K8s tokens and exfiltrating to `models.litellm[.]cloud`)
> after a suspected maintainer-PyPI-account compromise bypassed official CI/CD and
> uploaded directly to PyPI. Live ~40 minutes on 2026-03-24 (10:39 UTC) before
> PyPI quarantine. Official Docker image (`ghcr.io/berriai/litellm`), LiteLLM Cloud,
> and source installs were unaffected; pip installs without pinned versions — including
> transitive/unpinned dependencies via AI agent frameworks and MCP servers — were
> exposed. Remediation: v1.83.0 via the new CI/CD v2 pipeline (isolated environments,
> security gates, safer release separation), cosign-signed Docker images, and
> SHA-256-verified safe-version lists. This is the primary incident record that the
> already-mined April security-hardening post references as background motivation.

## Source Context

- **Type**: failure-report (vendor supply-chain security incident disclosure). The
  page is tagged `security`, `incident-report` and is the vendor's live "Status:
  Active investigation" disclosure, updated in place 2026-03-25 through 2026-03-30.
- **Platform**: Vendor blog post on `docs.litellm.ai/blog` (Docusaurus), published
  2026-03-24 by LiteLLM leadership.
- **Author credibility**: High for incident facts — authored by Krrish Dholakia
  (CEO) and Ishaan Jaffer (CTO) of LiteLLM/BerriAI, describing their own package
  distribution pipeline and response. The post documents concrete, checkable facts
  (exact versions, UTC timestamps, IoCs, SHA-256 digests) rather than marketing.
  Caveat: the root-cause attribution ("suspected maintainer account compromise,"
  "may be linked to the broader Trivy security compromise") is explicitly labeled
  as an active investigation, so those attribution claims are lower-confidence than
  the incident facts themselves.
- **Scope**: Covers the compromise vector, affected/not-affected version scoping,
  IoCs, immediate-action playbook for affected users, response/remediation steps
  (credential rotation, Mandiant forensics, cosign signing, CI/CD v2 release), and
  the SHA-256 "verified safe versions" audit. Does NOT cover the three CVEs disclosed
  the following month (that is `failure-litellm-security-hardening-april-2026.md`),
  other LiteLLM vulnerabilities, or product/roadmap content.
- **Relationship to sibling notes**: The Prospector triage confirms this is the
  incident report for the compromise that `failure-litellm-security-hardening-april-2026.md`
  references only as background ("the supply chain incident that prompted the audit").
  It is the earliest disclosed LiteLLM security incident in the corpus, chronologically
  preceding the guardrail-logging leak (2026-03-18, note already mined), the April
  hardening post (2026-04-03), and the April townhall's CI/CD v2 rollout (2026-04-10).

## What Was Attempted

- **Attacker goal**: Distribute a credential-stealing payload to LiteLLM users
  through the official Python package distribution channel. The attacker bypassed
  LiteLLM's official CI/CD workflows and uploaded malicious packages directly to
  PyPI under the `litellm` name.
- **Technique (as disclosed)**: Suspected compromise of a maintainer's PyPI
  account, used to publish `litellm==1.82.7` and `litellm==1.82.8` on 2026-03-24.
  The vendor explicitly frames this as a publishing-pipeline compromise rather than
  a source-repo compromise: "We have also verified the codebase is safe and no
  malicious code was pushed to main."
- **Payload**: A credential stealer embedded in the LiteLLM AI Gateway
  `proxy_server.py`, plus a `litellm_init.pth` file (Python `site-packages` auto-import
  hook) in v1.82.8 that would execute on interpreter startup.

## What Went Wrong

- **Symptoms**: Compromised PyPI packages served malicious code to anyone who
  installed them. Concrete timeline from the TLDR:
  - **Quote**: "The compromised PyPI packages were litellm==1.82.7 and litellm==1.82.8. Those packages were live on March 24, 2026 from 10:39 UTC for about 40 minutes before being quarantined by PyPI."
- **Severity**: Critical by nature (credential exfiltration of production secrets),
  but blast radius was bounded by deployment path: the official Docker image, LiteLLM
  Cloud, and source installs were explicitly not affected. The high-risk population was
  pip users who installed without pinning, including transitive/unpinned dependency
  consumers.
- **Malicious payload mechanics** — the credential stealer:
  - **Quote**: "These compromised versions appear to have included a credential stealer designed to:"
  - Harvest list (verbatim bullets): "environment variables", "SSH keys",
    "cloud provider credentials (AWS, GCP, Azure)", "Kubernetes tokens",
    "database passwords".
  - **Quote**: "Encrypt and exfiltrate data via a POST request to models.litellm.cloud, which is not an official BerriAI / LiteLLM domain"
- **Affected-version payloads (verbatim from "Confirmed affected versions")**:
  - "v1.82.7: contained a malicious payload in the LiteLLM AI Gateway proxy_server.py"
  - "v1.82.8: contained litellm_init.pth and a malicious payload in the LiteLLM AI Gateway proxy_server.py"
  - "Note: These versions have already been removed from PyPI."
- **Impact scoping — who IS affected** (verbatim, condensed from the four-condition list):
  - "You installed or upgraded LiteLLM via pip on March 24, 2026, between 10:39 UTC and 16:00 UTC"
  - "You ran pip install litellm without pinning a version and received v1.82.7 or v1.82.8"
  - "You built a Docker image during this window that included pip install litellm without a pinned version"
  - "A dependency in your project pulled in LiteLLM as a transitive, unpinned dependency (for example through AI agent frameworks, MCP servers, or LLM orchestration tools)"
- **Impact scoping — who is NOT affected** (verbatim, condensed):
  - "Customers running the official LiteLLM Proxy Docker image were not impacted. That deployment path pins dependencies in requirements.txt and does not rely on the compromised PyPI packages."
  - "You are using LiteLLM Cloud"
  - "You are using the official LiteLLM AI Gateway Docker image: ghcr.io/berriai/litellm"
  - "You are on v1.82.6 or earlier and did not upgrade during the affected window"
  - "You installed LiteLLM from source via the GitHub repository, which was not compromised"
- **Indicators of compromise (IoCs)**:
  - "litellm_init.pth present in your site-packages"
  - "Outbound traffic or requests to models.litellm[.]cloud" — "This domain is not affiliated with LiteLLM"
  - "Outbound traffic or requests to checkmarx[.]zone" — "This domain is not affiliated with LiteLLM"
    (`checkmarx[.]zone` was added to the IoC list on 2026-03-26, two days after first
    publication.)
- **Detection tooling**: On 2026-03-25 the vendor added community-contributed
  scanning scripts for GitHub Actions and GitLab CI pipelines (credited to "@Zach Fury")
  that replay the incident window and flag any workflow job that installed 1.82.7/1.82.8.

## Root Cause (if identified)

- **Author's diagnosis (suspected, investigation ongoing at publication)**:
  1. Maintainer PyPI account compromise: "Current evidence suggests a maintainer's PyPI account may have been compromised and used to distribute malicious code."
  2. CI/CD bypass: "Initial evidence suggests the attacker bypassed official CI/CD workflows and uploaded malicious packages directly to PyPI."
  3. Trivy-dependency linkage: "We believe that the compromise originated from the Trivy dependency used in our CI/CD security scanning workflow." and "At this time, we believe this incident may be linked to the broader Trivy security compromise, in which stolen credentials were reportedly used to gain unauthorized access to the LiteLLM publishing pipeline."
- **Our assessment**: The vendor is appropriately careful — the "suspected" qualifiers
  reflect an active investigation (Mandiant engaged). Three distinct supply-chain
  failure patterns are nevertheless visible and independently credible: (1) a
  publishing credential (PyPI account/token) that was not protected by the official
  CI/CD path — the attacker could upload directly, bypassing the pipeline that was
  supposed to be the release gate; (2) a security-scanning *dependency* (Trivy) being
  in the threat model at all, i.e., the very tool meant to detect compromise becoming
  a suspected compromise vector; (3) no signed-artifact/verifiable-release mechanism
  in place at the time — the response added cosign signing only *after* the incident
  ("Starting from v1.83.0-nightly"). The "no malicious code was pushed to main" detail
  is important: a CI/CD-bypass attack can publish packages without touching source
  control, so repo integrity is not a sufficient control.
- **Category**: vendor-supply-chain compromise (external attacker), with the caveat
  that root-cause attribution is suspected, not confirmed, at the time of extraction.

## Recovery Path

- **What they switched to** (response and remediation, verbatim action list):
  - "Removed compromised packages from PyPI"
  - "Rotated maintainer credentials and established new authorized maintainers"
  - "Engaged Google's Mandiant security team to assist with forensic analysis of the build and publishing chain"
- **Clean release**: v1.83.0 released 2026-03-30 via the new CI/CD v2 pipeline.
  - **Quote**: "A new clean version of LiteLLM is now available (v1.83.0). This was released by our new CI/CD v2 pipeline which added isolated environments, stronger security gates, and safer release separation for LiteLLM."
  - **Quote**: "We have also verified the codebase is safe and no malicious code was pushed to main."
- **Release freeze during investigation**: "We have paused all new LiteLLM releases until we complete a broader supply-chain review and confirm the release path is safe."
- **Artifact signing added**: "Starting from v1.83.0-nightly, all LiteLLM Docker images published to GHCR are signed with cosign. Every release is signed with the same key introduced in commit 0112e53." (See Concrete Artifacts for the verify commands.)
- **Safe-version audit**: "We have audited every LiteLLM release published between v1.78.0 and v1.82.6 across both PyPI and Docker" with three verification steps (see Concrete Artifacts). "All versions listed below are confirmed clean."
- **Immediate user actions (verbatim guidance)**:
  1. Rotate all secrets: "Treat any credentials present on the affected systems as compromised, including: API keys / Cloud access keys / Database passwords / SSH keys / Kubernetes tokens / Any secrets stored in environment variables or configuration files".
  2. Inspect filesystem for `litellm_init.pth`; if present: "remove it immediately", "investigate the host for further compromise", "preserve relevant artifacts if your security team is performing forensics".
  3. Audit version history (local environments, CI/CD pipelines, Docker builds, deployment logs) and "Pin LiteLLM to a known safe version such as v1.82.6 or earlier, or to a later verified release once announced."
- **Unresolved**: Root-cause attribution (maintainer account, Trivy linkage) remains
  "suspected" at the last page update (2026-03-30). The broader supply-chain review
  was completed enough to resume releases (v1.83.0), but the vendor does not publish
  a final attribution.

## Concrete Artifacts

### Indicators of compromise (verbatim from "Indicators of compromise (IoCs)")

```
Review affected systems for the following indicators:

- litellm_init.pth present in your site-packages

- Outbound traffic or requests to models.litellm[.]cloud
  This domain is not affiliated with LiteLLM

- Outbound traffic or requests to checkmarx[.]zone
  This domain is not affiliated with LiteLLM
```

### Filesystem inspection command (verbatim from "Immediate actions")

```
Check your site-packages directory for a file named litellm_init.pth:

find /usr/lib/python3.13/site-packages/ -name "litellm_init.pth"
```

### Version check commands (verbatim from "How to check if you are affected")

```
SDK:   pip show litellm
PROXY: Go to the proxy base url, and check the version of the installed LiteLLM.
```

### GitHub Actions detection script — detection constants and match logic (verbatim excerpt from `find_litellm_github.py`)

The full script (contributed by @Zach Fury, "original gist") enumerates an org's
repos, fetches workflow-run/job logs inside the incident window, and flags any job
whose log mentions the compromised versions. Detection-relevant constants verbatim:

```python
"""
Scan all GitHub Actions jobs in a GitHub org that ran between
0800-1244 UTC today and identify any that installed litellm 1.82.7 or 1.82.8.

Adjust WINDOW_START / WINDOW_END to cover March 24, 2026 if running later.
"""
TARGET_VERSIONS = {"1.82.7", "1.82.8"}
VERSION_PATTERN = re.compile(r"litellm[=\-](\d+\.\d+\.\d+)", re.IGNORECASE)
```

Attribution: community-contributed scripts, added 2026-03-25. Page warning:
"CI/CD scripts contributed by the community (original gist). Review before running."

### cosign Docker image verification (verbatim from "Verify Docker image signatures")

```
# Verify using the pinned commit hash (recommended):
cosign verify \
--key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub \
ghcr.io/berriai/litellm:<release-tag>

# Verify using a release tag (convenience):
cosign verify \
--key https://raw.githubusercontent.com/BerriAI/litellm/<release-tag>/cosign.pub \
ghcr.io/berriai/litellm:<release-tag>
```

"A commit hash is cryptographically immutable, so this is the strongest way to ensure
you are using the original signing key:" — "Tags are protected in this repository and
resolve to the same key. This option is easier to read but relies on tag protection
rules." Replace `<release-tag>` with the version you are deploying (e.g. `v1.83.0-stable`).
Expected output: "The cosign claims were validated" / "The signatures were verified
against the specified public key".

### Verified safe-version audit method (verbatim from "Verified safe versions")

```
We have audited every LiteLLM release published between v1.78.0 and v1.82.6 across
both PyPI and Docker. Each artifact was verified by:

- Downloading the published artifact and computing its SHA-256 digest
- Scanning for the known indicators of compromise (IOCs)
- Comparing the artifact contents against the corresponding Git commit in the
  BerriAI/litellm repository

All versions listed below are confirmed clean.
```

### Verified safe-version table excerpt (PyPI rows, verbatim from the rendered table)

| Version | SHA-256 (prefix) | Clean of IOCs | Matches Git | Status |
|---------|------------------|---------------|-------------|--------|
| 1.82.6 | 164a3ef3e19f309e… | ✔ CLEAN | ✔ YES | ✔ CLEAN |
| 1.82.5 | e1012ab816352215… | ✔ CLEAN | ✔ YES | ✔ CLEAN |
| 1.82.4 | d37c34a847e7952a… | ✔ CLEAN | ✔ YES | ✔ CLEAN |
| 1.82.3 | 609901f6c5a5cf8c… | ✔ CLEAN | ✔ YES | ✔ CLEAN |
| 1.82.2 | 641ed024774fa3d5… | ✔ CLEAN | ✔ YES | ✔ CLEAN |
| 1.82.1 | a9ec3fe42eccb161… | ✔ CLEAN | ✔ YES | ✔ CLEAN |
| 1.82.0 | 5496b5d4532cccdc… | ✔ CLEAN | ✔ YES | ✔ CLEAN |
| 1.81.16 | d6bcc13acbd26719… | ✔ CLEAN | ✔ YES | ✔ CLEAN |

(The page lists 20 PyPI rows through v1.81.3 plus a 19-row Docker-image table; all
rows carry the same four-column "CLEAN / YES / CLEAN" result. Full SHA-256 digests
are truncated in the rendered page.)

## Extracted Lessons

### Lesson 1: An LLM gateway's package-publishing pipeline is a critical supply-chain surface — a compromised publishing credential can bypass the entire official CI/CD release gate and publish directly to the package registry
- **Evidence**: "Initial evidence suggests the attacker bypassed official CI/CD workflows and uploaded malicious packages directly to PyPI." Combined with the vendor's confirmation that "no malicious code was pushed to main," this shows the attack reached users without any source-repo change.
- **Confidence**: settled (the bypass fact) / emerging (the exact credential compromise mechanism, which remains "suspected").
- **Quote**: "Initial evidence suggests the attacker bypassed official CI/CD workflows and uploaded malicious packages directly to PyPI."
- **Our assessment**: Buy it. The "published to PyPI without touching main" detail is decisive: repo integrity ≠ release integrity. For operators of LLM gateways and for anyone distributing gateway software, the release path itself must be hardened (least-privilege publishing credentials, MFA, no direct-upload capability outside CI, signed artifacts). This is the concrete failure the CI/CD v2 goals in the April townhall are responding to.

### Lesson 2: A credential stealer can be smuggled into an LLM gateway package via a `.pth` file in site-packages — an interpreter-startup code path that standard dependency review may not flag
- **Evidence**: v1.82.8 "contained litellm_init.pth and a malicious payload in the LiteLLM AI Gateway proxy_server.py." Python `.pth` files in site-packages execute code on interpreter startup, so merely importing/starting the package (or any process on the host) could trigger the payload.
- **Confidence**: settled (the file existed and was treated as an IoC).
- **Quote**: "v1.82.8: contained litellm_init.pth and a malicious payload in the LiteLLM AI Gateway proxy_server.py"
- **Our assessment**: Buy it. The `.pth` mechanism is a known Python supply-chain technique (auto-executed import hooks). The lesson for gateway operators: a dependency-scanning policy that only reviews the main module tree misses interpreter-level persistence like `.pth`/`sitecustomize`/`.pth`-executed code. IoC checks (scan site-packages for unexpected `.pth` files, monitor outbound POSTs to non-official domains) should be part of post-incident detection.

### Lesson 3: The credential stealer targeted exactly the secrets LLM gateway hosts carry — env vars, SSH keys, cloud provider credentials (AWS/GCP/Azure), Kubernetes tokens, database passwords — and exfiltrated to a look-alike domain
- **Evidence**: The payload's harvest list plus "Encrypt and exfiltrate data via a POST request to models.litellm.cloud, which is not an official BerriAI / LiteLLM domain." `models.litellm.cloud` is a subdomain that visually resembles the legitimate vendor domain, and `checkmarx[.]zone` was added as a second IoC two days later.
- **Confidence**: settled.
- **Quote**: "Encrypt and exfiltrate data via a POST request to models.litellm.cloud, which is not an official BerriAI / LiteLLM domain"
- **Our assessment**: Buy it, and note the targeting is unsurprising: LLM gateways sit between the API key and the model providers and frequently run in cloud/K8s environments with broad credentials. The exfiltration-destination IoC (a near-vendor domain) is the key detection primitive — outbound egress monitoring for non-official domains is the control that would catch this class early.

### Lesson 4: Impact scoping must be deployment-path-aware — pinned-Docker/source/Cloud installs were safe, while pip installs without pinned versions (including transitive/unpinned deps via AI agent frameworks and MCP servers) were the exposed population
- **Evidence**: The four "affected if" conditions and five "not affected if" conditions, including the transitive-dependency clause.
- **Confidence**: settled.
- **Quote**: "A dependency in your project pulled in LiteLLM as a transitive, unpinned dependency (for example through AI agent frameworks, MCP servers, or LLM orchestration tools)"
- **Our assessment**: Buy it. The scoping is the operational core of the post. Two takeaways: (1) pinned dependencies in a container image (`requirements.txt` in the official image) were the difference between safe and compromised — pinning is a supply-chain control, not a style choice; (2) LLM gateway exposure is not limited to direct `pip install litellm` users — agent frameworks, MCP servers, and orchestration tools that transitively depend on it become an attack-vector multiplier. Teams running agent infrastructure should inventory which of their dependencies pull in LLM gateway/SDK packages and pin them.

### Lesson 5: Post-incident remediation was an ordered playbook — remove, rotate, contain, harden, re-release, verify — that itself became the vendor's CI/CD v2 hardening program
- **Evidence**: The action list (removed packages, rotated maintainer credentials, engaged Mandiant) plus the 2026-03-30 CI/CD v2 re-release, plus the SHA-256 safe-version audit.
- **Confidence**: settled (facts) / emerging (CI/CD v2 maturity, corroborated later by the April townhall).
- **Quote**: "Rotated maintainer credentials and established new authorized maintainers" / "Engaged Google's Mandiant security team to assist with forensic analysis of the build and publishing chain"
- **Our assessment**: Buy it. The sequence (quarantine → credential rotation → external forensics → release freeze → hardened rebuild → signed artifacts → safe-version audit) is a reusable incident-response template for package-supply-chain incidents. Note the release freeze: the vendor paused ALL releases until the pipeline was re-verified, trading availability for integrity — the correct call for a distribution-pipeline compromise.

### Lesson 6: After a publishing-pipeline compromise, artifact signing plus a reproducible safe-version audit (SHA-256 digest + IoC scan + Git-commit match) is the trust-restoration mechanism
- **Evidence**: "Starting from v1.83.0-nightly, all LiteLLM Docker images published to GHCR are signed with cosign. Every release is signed with the same key introduced in commit 0112e53." and the three-step verified-safe-versions method.
- **Confidence**: settled.
- **Quote**: "A commit hash is cryptographically immutable, so this is the strongest way to ensure you are using the original signing key:"
- **Our assessment**: Buy it. The three-way audit (published artifact → SHA-256; scan → IoCs; compare → matching Git commit) is a strong, generalizable pattern: it ties a binary artifact back to source control and to a clean scan, which is exactly what users need to trust a post-incident release. The cosign-by-pinned-commit-key guidance (rather than trusting the current tag) addresses the chicken-and-egg problem of verifying the verifier after a compromise.

## Cross-References

- **Corroborates**:
  - `blog-litellm-april-townhall-updates.md` **Claim 1** (CI/CD v2 is organized around four goals: "Limit what each package can access / Reduce the number of sensitive environment variables / Avoid compromised packages / Reduce the risk of release tampering"), **Claim 2** (isolated environments per CI/CD stage "to reduce the chance that a single compromised step can inherit broad access across the entire pipeline"), and **Claim 3** (independent verification of release artifacts "while reducing reliance on any single credential or release path"). This March incident report is the concrete motivation and implementation record for those goals: v1.83.0 "was released by our new CI/CD v2 pipeline which added isolated environments, stronger security gates, and safer release separation." The April townhall describes the pipeline the incident forced into being; this note documents the incident itself. The "avoid compromised packages" goal reads as a direct response to the Trivy-linked compromise suspected here.
  - `failure-litellm-security-hardening-april-2026.md` **Concrete Artifacts → Bug bounty program** — the April bug bounty table lists "Supply chain compromise" as the example for the Critical/P0 tier; this March incident is the concrete instance of that category. The two notes are the two halves of the same security wave: the incident (here) and the audit it prompted (there).
- **Contradicts**: None. No existing source note makes claims about the March supply-chain incident, LiteLLM's PyPI publishing pipeline, or the safety of the affected versions. The April hardening post explicitly *defers* this incident ("Does not cover the supply chain incident that prompted the audit") rather than contradicting it. The sibling LiteLLM failure notes cover different failure classes (auth bypass, observability leak, SQL injection) that are orthogonal. No contradiction issue filed.
- **Extends**:
  - `failure-litellm-security-hardening-april-2026.md` — provides the primary incident record that note references only as background. Together they form a complete timeline: supply-chain compromise (2026-03-24) → audit/hardening disclosures (2026-04-03, three CVEs) → CI/CD v2 (2026-04-10). This note is the chronological and causal root of the security wave documented across the April/May notes.
  - `blog-litellm-april-townhall-updates.md` — extends its CI/CD v2 *goal* claims (Claims 1–3) with the incident *evidence* that motivated them. The April note's Claim 1 threat model ("compromised-package propagation and single-credential release tampering") is exactly what happened here; this note is the proof case.
  - `blog-litellm-may-townhall-updates.md` — the May note's **Claim 1** (PEP-440/SemVer from v1.84.0, "No more -stable") postdates this incident, whose own artifacts still reference the old suffix naming (`v1.83.0-stable` in the cosign example) — this note documents the pre-change naming era and the incident that prompted the release-hardening that culminated in the versioning change. The May note's **Claim 11** security roadmap ("Further CI pipeline improvements", "Define support window for prior releases") is the continuation of this incident's CI/CD v2 remediation.
  - `failure-litellm-proxy-sql-injection-cve-2026-42208.md` — same vendor, same coordinated-disclosure/fix-first posture, part of the same 2026 security wave. That note covers an application-layer SQLi CVE; this note covers the distribution-pipeline compromise. Both establish that LiteLLM's 2026 security history spans both code defects and supply-chain incidents.
  - `failure-litellm-host-header-auth-bypass.md`, `failure-litellm-guardrail-logging-secret-exposure.md` — same vendor, different failure classes (auth-bypass route resolution; credential leak via observability), same time window. Together the LiteLLM failure notes now bracket both *code-level* security defects and *distribution-level* supply-chain risk — distinct categories the guide should treat separately.
  - `blog-promptfoo-open-sourcing-modelaudit.md` — thematically adjacent on "LLM supply-chain security" but from a different attack surface: that note covers ML *model-file* supply chain (pickle deserialization RCE in Hugging Face artifacts, see its Claims 1–2), while this note covers *software-package* supply chain (PyPI credential stealer). Both argue the supply chain is the neglected LLM-infrastructure security surface, from opposite ends (model artifacts vs. runtime dependencies).
- **Novel**: First source note in the corpus covering:
  1. A **package/registry supply-chain compromise** in the LLM ecosystem (PyPI credential stealer), as opposed to model-file supply chain (`blog-promptfoo-open-sourcing-modelaudit.md`) or application-layer CVEs (the other LiteLLM failure notes).
  2. The **CI/CD-bypass publish vector** — attacker uploading directly to PyPI, bypassing official CI/CD, with "no malicious code was pushed to main." The repo-vs-release integrity distinction is new to the corpus.
  3. **Credential-stealer payload mechanics in an LLM gateway package**: the `.pth`-in-site-packages IoC, the exact secret-harvest list, and the look-alike-domain exfiltration destination (`models.litellm[.]cloud`, `checkmarx[.]zone`).
  4. The **deployment-path-aware impact model** for an LLM gateway incident: pinned Docker / Cloud / source = safe; unpinned pip + transitive deps via agent frameworks/MCP servers = exposed. No prior note scopes a failure by install path.
  5. The **post-incident trust-restoration stack**: release freeze, CI/CD v2 hardened rebuild, cosign signing pinned to a commit key, and the SHA-256 + IoC-scan + Git-commit-match safe-version audit. The cosign verify commands and the verified-safe-version table are the first such artifacts in the corpus.
  6. **Community CI/CD scanning scripts** (GitHub Actions/GitLab) as a detection-tooling pattern for compromised-version exposure — the first incident-detection artifact in the corpus aimed at CI pipelines rather than runtime metrics.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Add a **supply-chain / dependency-integrity subsection** for LLM gateway infrastructure, with this incident as the lead case study. Specific additions:
  1. "LLM gateway and SDK packages MUST be installed with pinned versions. Unpinned `pip install litellm`-style installs are a supply-chain exposure; official container images that pin `requirements.txt` are the safe deployment path." (Cite the affected/not-affected scoping.)
  2. "Treat transitive, unpinned dependencies as first-class exposure: AI agent frameworks, MCP servers, and LLM orchestration tools that pull in a gateway/SDK package expand the blast radius of any package compromise. Inventory and pin the full dependency tree." (Cite the transitive-dependency condition.)
  3. "Release integrity is distinct from repo integrity: verify that a package/artifact can only be published through the official CI/CD pipeline with signed output, because a compromised publishing credential can bypass CI/CD and publish directly to the registry without any source-repo change." (Cite "no malicious code was pushed to main" + CI/CD bypass.)
  4. "Post-incident trust restoration should include artifact signing (e.g. cosign pinned to a commit hash) and a reproducible safe-version audit (SHA-256 digest + IoC scan + Git-commit match)." (Cite the cosign section and the verified-safe-versions method.)
- **Chapter 01 (Incident Response)**: Add this incident as a **package-supply-chain IR template**: incident timeline (compromised-version window + UTC timestamps), IoC list (`.pth` file, outbound POSTs to look-alike domains), impact scoping by deployment path, immediate-action playbook (rotate all secrets / inspect filesystem / audit version history), and detection tooling (CI/CD log scanning scripts that replay the exposure window). The "checkmarx[.]zone added two days later" detail is a useful example of IoC lists being updated during an active investigation.
- **Chapter 05 (LLM Ops Reliability)**: Add **unpinned/transitive dependency risk in LLM gateway deployments** to the deployment-hardening material, and the **Docker-path safety pattern** (official image pins dependencies in `requirements.txt` → unaffected). Add the release-freeze decision ("paused all new releases until the release path is safe") as a reliability-vs-integrity tradeoff example, and the cosign + safe-version audit as release-verification practices. Cross-reference the CI/CD v2 material already recommended from `blog-litellm-april-townhall-updates.md` — this incident is the motivating evidence for that chapter's CI/CD hardening guidance.
- **Chapter 04 (On-call and Toil)** (light): The detection tooling (community GitHub Actions/GitLab CI scanning scripts) is a concrete runbook artifact for "did my CI pipeline install the compromised versions during the window?" — recommend adding a supply-chain exposure check to incident-runbook tooling.
- **Chapter 02 (Observability)**: Add **egress monitoring for non-official domains** as an early-warning control for credential exfiltration: the IoCs here are outbound requests to `models.litellm[.]cloud` and `checkmarx[.]zone`, both explicitly "not affiliated with LiteLLM." Network-egress observability would flag this class before the package quarantine.

## Extraction Notes

- Primary source read in full: https://docs.litellm.ai/blog/security-update-march-2026 (fetched via direct HTTP; HTML-to-text extraction). The page is a single, self-contained incident report (~10 KB of extractable text) with in-place update banners dated 2026-03-25 through 2026-03-30. All quoted passages were copied character-for-character from the extracted text. No sub-pages were linked that required following: the townhall "Learn more" link resolves to the separately-mined `blog-litellm-april-townhall-updates.md`, and the two community scanning scripts are embedded in full on this page (only detection-relevant excerpts were carried into Concrete Artifacts; the full scripts are on the page).
- `date_published` set to 2026-03-24 (page dateline); the page documents updates through 2026-03-30 (v1.83.0 release) and lists "Status: Active investigation / Last updated: March 27, 2026" in its header. `date_extracted`/`last_checked` set to 2026-07-31 UTC.
- `confidence_overall` set to `settled`: the incident facts (compromised versions, exposure window, IoCs, impact scoping, remediation, safe-version audit) are concrete, checkable vendor disclosures with timestamps and digests. The root-cause attribution (maintainer-account compromise, Trivy linkage) is explicitly "suspected" and is graded `emerging` at the claim level rather than driving the overall confidence down.
- The `miner-related-notes.md` candidates list was read per MINER.md §4 before writing Cross-References. All 10 listed candidates were evaluated:
  - `failure-litellm-proxy-sql-injection-cve-2026-42208.md` — cited under Extends (same vendor, same disclosure wave; app-layer CVE vs distribution-pipeline incident).
  - `blog-litellm-may-townhall-updates.md` — cited under Extends (versioning-era evidence in the cosign example; security-roadmap continuation).
  - `docs-langfuse-security-and-guardrails.md` — not cited; its guardrail-library/observability content (PII anonymization, scanner composition) is a different security domain (application-layer content filtering) with no overlap with package-supply-chain compromise. Dismissed.
  - `docs-langfuse-mcp-server.md` — not cited; MCP server documentation is unrelated to the supply-chain incident. The incident names MCP servers only as one example of a transitive-dependency carrier. Dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — not cited; its agent-capability and guardrail claims make no claims about dependency supply chains. The incident's "AI agent frameworks, MCP servers, or LLM orchestration tools" transitive-exposure clause is adjacent to that note's subject matter, but the note itself contains nothing to corroborate or contradict. Dismissed as non-overlapping.
  - `blog-litellm-save-claude-code-costs.md` — not cited; cost optimization is unrelated to supply-chain security. Dismissed.
  - `docs-google-sre-reliable-product-launches.md` — not cited; launch-coordination engineering is unrelated. Dismissed.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — not cited; SLO framework is unrelated. Dismissed.
  - `blog-incidentio-ai-sre-incident-run.md` — not cited; AI-assisted incident-response methodology (pre-launch product narrative) does not address package-supply-chain detection or remediation. Dismissed.
  - `blog-litellm-google-ai-studio-managed-agents.md` — not cited; managed-agents API feature is unrelated to the incident. Dismissed.
  Additional cross-references (`failure-litellm-security-hardening-april-2026.md`, `blog-litellm-april-townhall-updates.md`, `failure-litellm-host-header-auth-bypass.md`, `failure-litellm-guardrail-logging-secret-exposure.md`, `blog-promptfoo-open-sourcing-modelaudit.md`) were discovered by searching `source-notes/` per the Prospector's triage guidance and MINER.md §4; each cited claim/section was re-read and verified before citation.
- No contradiction issue filed: verified against all existing source notes and the CONTRADICTIONS.md index. The `failure-litellm-security-hardening-april-2026.md` note explicitly defers this incident rather than contradicting it; the other LiteLLM failure notes cover orthogonal failure classes; no open `contradiction`-labeled issue exists for this topic.
