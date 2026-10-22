---
source_url: https://www.cncf.io/blog/2026/06/03/inspektor-gadget-results-from-the-first-security-audit
source_type: blog-post
title: "Inspektor Gadget: Results from the first security audit"
author: "Brian Benz, Francis Laniel, Maya Singh, Helen Woeste, and Pietro Tirenna (Inspektor Gadget)"
date_published: 2026-06-03
date_extracted: 2026-10-22
last_checked: 2026-10-22
status: current
confidence_overall: emerging
issue: "#1836"
---

# Inspektor Gadget: Results from the first security audit

> A first-party summary of OSTIF/Shielder's independent audit of the eBPF-based
> Kubernetes observability toolkit: three CVEs (none Critical/High), six hardening
> recommendations, and — most transferable to this guide — two explicit limits on
> kernel-level visibility: a fixed 256 KB ring buffer whose overflow **silently
> drops other containers' events**, and six gadget-bypass scenarios proving eBPF
> tracing is evadable at the syscall boundary.

## Source Context

- **Type**: blog-post (CNCF Project Post — the Inspektor Gadget maintainers'
  write-up of the project's first independent security audit, with links to the
  full Shielder report and the individual CVE advisories).
- **Author credibility**: First-party project maintainers (Brian Benz, Francis
  Laniel, Maya Singh, Helen Woeste, Pietro Tirenna), summarizing an audit performed
  independently by Shielder for OSTIF with CNCF funding. The *findings* come from
  an external security firm and are backed by CVE IDs, fixed versions, and a
  downloadable report; the *post* is the maintainers' narrative and compresses the
  six bypass scenarios into named examples rather than a full enumeration. No CVSS
  scores are given — only the Critical/High/Medium/Low labels.
- **Scope**: Covers what Inspektor Gadget is, why the audit was scoped, the audit
  methodology and lab environments, the three vulnerabilities, six hardening
  recommendations, the gadget-bypass testing, and the update recommendation. Does
  NOT cover: the source code of the fixes, exploit details, per-finding CVSS
  vectors, or any LLM/AI-specific workload. Relevance to this guide is (1) any
  observability claim that rests on kernel-level tracing and (2) the threat model
  of a privileged observability agent running beside model-serving workloads.
- **Prospector framing**: `triaged:text`, novelty medium, priority medium, relevant
  to Ch02 (Observability) and Ch06 (Security & Trust). Intended as an additive
  scoping correction, not a contradiction — the guide currently makes no eBPF
  claims.

## Extracted Claims

### Claim 1: Inspektor Gadget is an eBPF-based toolkit for Kubernetes observability and Linux host inspection; its first independent audit was coordinated by OSTIF, funded by CNCF, and performed by Shielder, and every reported vulnerability now has a patch
- **Evidence**: Stated project and engagement facts with links to OSTIF, Shielder,
  the full PDF report, the CVE advisories, and the fixed release v0.50.1.
- **Confidence**: settled (independently performed audit with public report and
  CVE records).
- **Quote**: "Inspektor Gadget, the open source eBPF-based toolkit for Kubernetes observability and Linux host inspection, has completed its first independent security audit."
- **Quote**: "The findings, the fixes, and the hardening recommendations are now public, and every reported vulnerability has a patch available."
- **Our assessment**: Buy it. The important calibration is that this is a genuine
  independent review, not a self-assessment with a vendor logo — OSTIF engaged
  Shielder, and the report is public. It gives the guide a credible, checkable data
  point about what kernel-level tracing can and cannot promise.

### Claim 2: The value proposition is runtime eBPF instrumentation with no image rebuilds, sidecars, debuggers/strace, workload restarts, or custom kernel modules — applications keep running unchanged
- **Evidence**: The article's "What is Inspektor Gadget?" section, framing the
  operational tradeoff the project exists to remove; "gadgets" are packaged as OCI
  images and loaded at runtime.
- **Confidence**: settled (product definition, consistent with how eBPF tooling
  works).
- **Quote**: "There is no need to rebuild container images with extra instrumentation, inject sidecars into every pod, attach debuggers or strace to running processes, restart workloads to toggle tracing on and off, or ship custom kernel modules to nodes."
- **Quote**: "Instead, eBPF programs are loaded into the kernel at runtime to safely observe syscalls, network activity, and file access. Applications keep running unchanged while operators get the data they need."
- **Our assessment**: This is the honest upside: zero-instrumentation observability
  is a real operational win for a running LLM-serving fleet where restarting pods to
  attach a tracer is expensive or forbidden. Keep it paired with Claims 10-11 — the
  same mechanism narrows *which* operations are visible, so "no instrumentation
  required" is not the same as "complete visibility."

### Claim 3: The audit methodology combined collaborative threat modeling, manual source review, dynamic testing in three deployment-shaped lab environments, static analysis (Semgrep, GoSec), and AI-assisted code review
- **Evidence**: The article's "How the audit was scoped" list and the description of
  the three environments.
- **Confidence**: settled (methodology is stated explicitly).
- **Quote**: "Their methodology combined:"
- **Quote**: "Collaborative threat modeling with the Inspektor Gadget maintainers"
- **Quote**: "Dynamic testing on dedicated lab environments"
- **Quote**: "Static analysis using tools such as Semgrep and GoSec"
- **Quote**: "AI-assisted code review for broader coverage"
- **Quote**: "The researchers built three test environments that reflect how Inspektor Gadget is deployed in the wild: a local Linux host deployment, a remote daemon deployment, and a Kubernetes deployment on minikube."
- **Our assessment**: A useful reference model for auditing observability
  infrastructure: threat-model with the maintainers, then test each real deployment
  shape (host, remote daemon, cluster). The lab-environment detail matters because
  the daemon's remote-listener and RBAC findings (Claims 6, 9) only exist in the
  remote/Kubernetes configurations — an audit that tested only the local binary
  would have missed them.

### Claim 4: The audit found three vulnerabilities — two Medium and one Low, none Critical or High — and the auditors' overall conclusion was that the project's security posture is "adequately mature"
- **Evidence**: The findings section and Shielder's quoted conclusion from the final
  report; links to the full report.
- **Confidence**: settled for the finding count and severity labels; emerging for
  the "adequately mature" judgment (a qualitative auditor conclusion).
- **Quote**: "The audit identified three vulnerabilities. None were rated Critical or High severity."
- **Quote**: "the overall security posture of Inspektor Gadget is adequately mature from both a secure coding and design point of view."
- **Our assessment**: Buy the calibration point and use it against headline-driven
  security narratives: an independent audit producing no Critical/High findings is a
  meaningful positive signal, and "security audit completed" should not be read as
  "severe defects found." The three findings are still real and specific (Claims
  5-7), so "adequately mature" is not "nothing to fix."

### Claim 5: CVE-2026-24905 is a Medium-severity command injection in `ig image build` — Makefiles embedded user-controlled input without escaping — which matters most when CI/CD builds untrusted gadgets; fixed in v0.48.1
- **Evidence**: Named CVE, mechanism, affected surface, and fixed version; linked
  advisory.
- **Confidence**: settled (CVE + fixed release).
- **Quote**: "The image build process used Makefiles that embedded user-controlled input without proper escaping, creating a command injection vector. This matters most in CI/CD pipelines that build untrusted gadgets."
- **Our assessment**: A supply-chain-adjacent build finding: the tool that observes
  production is itself a build-time code-execution surface when fed untrusted input.
  For the guide's pinning/CI material, the transferable point is narrower than "pin
  dependencies" — it is that *build tooling which embeds user-controlled strings in
  shell/Make contexts* is an injection boundary even when the tool is a security
  product.

### Claim 6: CVE-2026-25996 is a Low-severity terminal escape injection — ANSI escape sequences in rendered event columns were not sanitized, so a compromised container could write escape codes into an operator's terminal; fixed in v0.49.1
- **Evidence**: Named CVE, rendering path, attacker precondition (compromised
  container), and fixed version.
- **Confidence**: settled (CVE + fixed release).
- **Quote**: "When rendering events in the terminal, Inspektor Gadget did not sanitize ANSI escape sequences, allowing a compromised container to inject terminal escape codes into an operator’s display."
- **Our assessment**: Low severity, but the class is worth recording: telemetry
  consumers render attacker-influenced strings, so an observability tool is an input
  path into the operator's terminal. It is the same "output is untrusted input"
  discipline the guide applies to logs and model output, applied to a CLI viewer.

### Claim 7: The Medium-severity event-flooding DoS used the eBPF ring buffer's hard-coded 256 KB size — one malicious container floods it and the system **silently drops events from other containers**, letting an attacker hide activity behind noise; fixed in v0.50.1
- **Evidence**: Named vulnerability class, the fixed buffer size, the cross-tenant
  impact (other containers' events dropped), the security-monitoring consequence,
  and the fixed version.
- **Confidence**: settled for the mechanism and fix (CVE + fixed release); emerging
  for how often this class appears in other telemetry pipelines (single-vendor
  finding).
- **Quote**: "A malicious container could flood the eBPF ring buffer (hard-coded to 256 KB), causing the system to silently drop events from other containers."
- **Quote**: "For teams using Inspektor Gadget as part of a security monitoring pipeline, this could allow an attacker to hide activity by generating noise."
- **Our assessment**: This is the source's most transferable claim for Ch02. A
  fixed-size event buffer is a **denial-of-visibility** surface, and the dangerous
  property is not the overflow — it is the *silence*. A drop that is not emitted as a
  metric/alert is indistinguishable from a quiet workload, so an attacker who can
  generate volume controls what the defender sees. The guide's rule should be:
  instrument the drop path (buffer-full / dropped-event counters) and alert on it;
  never let overflow degrade to silent sampling.

### Claim 8: Hardening recommendation — enforce TLS by default on the daemon's TCP listener; today it logs a warning and continues in plaintext, so the recommendation is an explicit opt-out flag
- **Evidence**: Stated current behavior and the recommended change.
- **Confidence**: settled (author-stated current behavior and recommendation).
- **Quote**: "Enforce TLS by default on TCP listeners. When the daemon starts a TCP listener without TLS, it currently logs a warning and continues in plaintext. The recommendation is to require an explicit opt-out flag."
- **Our assessment**: A clean instance of the guide's "secure default, explicit
  opt-out" rule: a warning in a log is not a security control, because the insecure
  path remains the default and the warning is easy to miss. For remote
  observability daemons carrying cluster telemetry, plaintext-by-default should be
  treated as a misconfiguration, not a supported mode.

### Claim 9: Hardening recommendation — reduce the DaemonSet's RBAC, specifically the `nodes/proxy` GET permission, which is a privilege-escalation path if the service account token is compromised
- **Evidence**: Named permission and the stated escalation precondition; the article
  notes the RBAC refactor is not yet complete.
- **Confidence**: settled that the permission exists and is over-broad relative to
  need; emerging for the exploitability assessment (no exploit chain shown).
- **Quote**: "Reduce RBAC permissions on the DaemonSet pod — specifically the nodes/proxy GET permission, which could be leveraged for privilege escalation if the service account token is compromised."
- **Quote**: "Some are already merged; others, notably the RBAC refactor and namespace blocklist, will take more time."
- **Our assessment**: Buy the least-privilege point. A privileged observability agent
  is a high-value target: it already runs with node-level access, so any extra API
  permission on its service account widens the blast radius of a token theft. The
  guide should apply the same "the monitoring plane is part of the attack surface"
  framing it uses for gateways and CI, rather than treating observability agents as
  trusted infrastructure.

### Claim 10: Hardening recommendation — add a Kubernetes namespace blocklist so the agent does not trace sensitive namespaces such as `kube-system`, and restrict remote clients from enabling host-level tracing through the daemon
- **Evidence**: Two named recommendations; the article links them to the privileged
  remote-daemon deployment mode.
- **Confidence**: settled (author-stated recommendations).
- **Quote**: "Implement a Kubernetes namespace blocklist to prevent unintended tracing on sensitive namespaces such as kube-system."
- **Quote**: "Restrict remote clients from enabling host-level tracing through the daemon, or clearly document the risk."
- **Our assessment**: The control is about *scope of collection*, not just access to
  the collected data: an observability agent with cluster-wide reach will observe
  control-plane and secret-adjacent activity unless explicitly bounded. For LLM
  fleets, the analogous scope is namespaces holding model weights, prompt stores, and
  gateway credentials — default-deny the sensitive namespaces rather than relying on
  operators to remember them.

### Claim 11: Gadget-bypass testing found six scenarios where a compromised container performs a traced operation without generating events — including newer syscalls a gadget does not hook (`openat2` vs `openat`), `io_uring`, and statically linked libraries
- **Evidence**: The audit's bypass-testing section; the post names three example
  classes out of the six and links the full report.
- **Confidence**: settled that bypasses exist and were demonstrated; emerging for
  the completeness/exploitability of each of the six (only three are named in the
  post).
- **Quote**: "They identified six bypass scenarios, ranging from using newer Linux syscalls that certain gadgets don’t hook (for example, openat2 instead of openat) to evasion through io_uring and statically linked libraries."
- **Quote**: "These results reflect the cat-and-mouse nature of kernel-level tracing."
- **Our assessment**: High-value scoping claim. Kernel-level tracing is not a
  complete-visibility guarantee; it is coverage of *the syscalls a given gadget
  hooks, for the binaries and runtimes it can see*. The guide should not present eBPF
  tracing as a universal detector, and should require any "we trace every syscall"
  claim to state its hook surface and known bypass classes. This is a limitation of
  the technique, not a defect unique to Inspektor Gadget — the article frames it as
  inherent.

### Claim 12: The maintainers are documenting the inherent limitations so operators know what eBPF tracing can and cannot guarantee, and have already addressed several bypass gaps
- **Evidence**: Stated maintainer response to the bypass findings.
- **Confidence**: emerging (a process statement, not a completed deliverable in the
  post).
- **Quote**: "The Inspektor Gadget maintainers have already addressed several of the identified gaps and are documenting the inherent limitations of the approach so operators understand what eBPF tracing can and cannot guarantee."
- **Our assessment**: The right response pattern: publish the limitation rather than
  silently patching individual bypasses. For the guide, this supports a rule that
  observability vendors/teams should document *coverage boundaries* alongside
  features, because an operator who assumes total coverage will mis-weight the
  signal.

### Claim 13: Hardening recommendation — pin and verify external build dependencies in CI/CD; several were downloaded without hash or signature verification, and most fixes are already landed or in PRs
- **Evidence**: The recommendation plus the current status statement.
- **Confidence**: settled (author-stated audit finding and remediation status).
- **Quote**: "Pin and verify external dependencies in CI/CD. Several build dependencies were downloaded without hash or signature verification."
- **Quote**: "The project has already landed fixes or has pull requests open for most of these."
- **Our assessment**: Straight corroboration of the guide's existing "pin everything;
  verify releases" rule, not new ground. The value is an independent-audit instance
  of the same failure class the LiteLLM supply-chain incident produced: security
  tooling is not exempt from dependency-integrity hygiene.

### Claim 14: The actionable recommendation is to update to v0.50.1 or later, which contains fixes for all three vulnerabilities
- **Evidence**: Stated update guidance with a link to the release.
- **Confidence**: settled (version + included fixes).
- **Quote**: "The actionable step for organizations running Inspektor Gadget is to update to v0.50.1 or later, which includes fixes for all three reported vulnerabilities."
- **Our assessment**: Buy it. For the guide's operational material, the useful
  pattern is version-scoped remediation: name the exact minimum fixed version rather
  than "update to latest," so an operator can check fleet state deterministically.

## Concrete Artifacts

### Vulnerability summary (from the "What the audit found" section)

| ID | Severity | Issue | Fixed in |
|---|---|---|---|
| CVE-2026-24905 | Medium | Command injection in `ig image build` | v0.48.1 |
| (event-flooding DoS, CVE not named in post) | Medium | 256 KB eBPF ring-buffer flooding; silently drops other containers' events | v0.50.1 |
| CVE-2026-25996 | Low | Unsanitized ANSI escape sequences in columns output | v0.49.1 |

The post states the two Medium findings as: "Command injection in ig image build" and
"Denial of service via event flooding." No CVSS scores are given.

### Hardening recommendations (verbatim bullets from the post)

```
- Enforce TLS by default on TCP listeners. When the daemon starts a TCP listener
  without TLS, it currently logs a warning and continues in plaintext. The
  recommendation is to require an explicit opt-out flag.
- Pin and verify external dependencies in CI/CD. Several build dependencies were
  downloaded without hash or signature verification. The project has already landed
  fixes or has pull requests open for most of these.
- Implement a Kubernetes namespace blocklist to prevent unintended tracing on
  sensitive namespaces such as kube-system.
- Restrict remote clients from enabling host-level tracing through the daemon, or
  clearly document the risk.
- Automate third-party vulnerability scanning for project dependencies.
- Reduce RBAC permissions on the DaemonSet pod — specifically the nodes/proxy GET
  permission, which could be leveraged for privilege escalation if the service
  account token is compromised.
```

### Audit methodology (verbatim bullets from "How the audit was scoped")

```
- Collaborative threat modeling with the Inspektor Gadget maintainers
- Manual source code review
- Dynamic testing on dedicated lab environments
- Static analysis using tools such as Semgrep and GoSec
- AI-assisted code review for broader coverage
```

The three test environments, verbatim: "a local Linux host deployment, a remote
daemon deployment, and a Kubernetes deployment on minikube."

### Gadget-bypass examples named in the post

The post says there were six scenarios but names only three classes:

```
using newer Linux syscalls that certain gadgets don’t hook (for example, openat2
instead of openat) ... evasion through io_uring and statically linked libraries
```

The full enumeration is in the linked Shielder PDF report (not fetched for this
note; the source-note claims are scoped to the post's summary).

## Cross-References

**Candidates from `miner-related-notes.md` (all ten listed paths evaluated; two
cited, eight dismissed):**

- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**:
  retail/gaming SLO granularity and platform migration; no tracing, monitoring-agent,
  or supply-chain content.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
  **dismissed**: imperative vs declarative change workflows; unrelated to event
  visibility or privileged agents.
- `source-notes/docs-google-sre-prodcast-05-05-brady-operating-systems.md` —
  **dismissed**: gLinux fleet testing/canary/Puppet; Linux-adjacent but no eBPF,
  syscall tracing, or observability-agent threat model.
- `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` — **cited**
  (Extends / scoping): its pipeline artifact describes the corpus's other eBPF data
  point — "Falco with eBPF intercepts every syscall on the workloads we monitor"
  (**Concrete Artifacts → System pipeline and topology**, not a numbered claim). That
  note treats syscall interception as a working detection layer; this note supplies
  the counter-case: interception covers the hooked syscall surface and is evadable
  (Claim 11), and its event buffer can be flooded into silence (Claim 7). The two are
  complementary halves — one shows the detection architecture, the other bounds the
  visibility guarantee — not a contradiction (see Contradicts below).
- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **dismissed**:
  red-team finding disposition/export formats; no event-collection or tracing layer.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  definition/measurement; no overlap with telemetry loss or privileged agents.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch coordination checklists; unrelated.
- `source-notes/docs-google-sre-on-call.md` — **dismissed**: pager load/alerting
  hygiene; the shared word "alerting" does not make this an evidential cross-ref,
  since that note has no event-drop or tracing-coverage claim.
- `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **dismissed**: audit
  event taxonomy and record schema; it is about *what is deliberately logged*, not
  about a telemetry pipeline silently losing events.
- `source-notes/docs-promptfoo-enterprise-guardrails.md` — **cited** (Contrast /
  Extends): **Claim 2** documents a deliberate fail-open trap — the `warn` and
  `error` aggregate actions "need caller-defined handling or they fall through."
  That is the *known-and-documented* version of the same failure direction this
  source reports for the ring buffer (Claim 7), where overflow falls through to
  silence with no documented caller contract. Pair the two when the guide states the
  fail-loud rule: one is a documented degradation, the other is an undocumented one.

**Additional cross-references found by searching `source-notes/` beyond the
candidate list:**

- **Corroborates**:
  - `source-notes/docs-litellm-generic-guardrail-api.md` **Claim 9** (verified) —
    the corpus's model for a fail-open path that is at least *auditable*: every
    bypass "is logged at critical level ... with the call id and trace id, so you
    can alert on it and audit how often it happens." That is exactly the drop-path
    instrumentation this source says the ring buffer lacked (Claim 7). The guide can
    cite the two together: fail-open is tolerable only when the bypass is logged,
    counted, and alertable; silent drop is the unacceptable variant.
  - `source-notes/blog-cncf-telemetry-that-matters-observability-pipelines.md`
    **Claim 7** (verified) — tail/pattern-based sampling should "drop boring,
    successful requests while capturing 100% of anomalies or failures"; **Claim 14**
    (verified) — audit each stream with "If this specific data stream stopped flowing
    tomorrow, what would we actually lose?" Together they distinguish *deliberate,
    policy-driven* volume reduction from the ring buffer's *involuntary, silent*
    drop under attacker-controlled load. Same outcome (fewer events), opposite
    control property.
  - `source-notes/blog-cncf-securing-cicd-locking-down-dependencies.md` **Claim 1**
    (verified) — "A pinned workflow that fetches a compromised dependency is still a
    compromised workflow." The audit's unverified build dependencies (Claim 13) and
    the `ig image build` injection (Claim 5) are two build-pipeline instances of that
    composition rule.
  - `source-notes/failure-litellm-supply-chain-compromise-march-2026.md` **Lesson 4**
    (verified; this note uses `### Lesson N`, not `### Claim N`) — impact scoping is
    deployment-path-aware: pinned container/source installs were safe while unpinned
    package intake was exposed. Same framing applies to the audit's remediation:
    update to the named fixed version (Claim 14) rather than assuming a fleet is safe
    because "we run Inspektor Gadget."
- **Extends**:
  - `source-notes/blog-cncf-kepler-rearchitected-power-accuracy.md` **Claim 1**
    (verified) — eBPF required `CAP_BPF` and `CAP_SYSADMIN`, "a blocker for many
    production environments," and the Kepler rewrite traded eBPF for read-only
    `/proc`+`/sys`. **Claim 2** (verified) — eBPF was "error-prone when it comes to
    tracking fine-grained, kernel-level processes at this level of accuracy." This
    source extends that privilege/accuracy thread into *security telemetry*: the
    agent runs with root-level access (Claim 9's threat model), and the accuracy
    question becomes the bypass-coverage question (Claim 11). Kepler's story says
    eBPF has a deployment-permission cost; this source adds that it also has a
    visibility-coverage cost.
  - `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` — see
    candidate entry above. Its **Claim 2** (cert-manager per-agent identities +
    CiliumNetworkPolicy) is the identity-scoped-reachability pattern that the
    observability DaemonSet here lacks; this source's `nodes/proxy` RBAC finding
    (Claim 9) is the least-privilege gap at a different control point.
- **Contradicts**: **none filed.** The only apparent tension is with
  `blog-cncf-cloud-native-agentic-ai-security-platform`'s use of Falco-with-eBPF as a
  working detection layer (Concrete Artifacts → pipeline). It does not rise to a
  contradiction under MINER.md §4a: that source does not claim eBPF visibility is
  complete or unbypassable, and this source does not claim eBPF is ineffective — it
  bounds the guarantee (hooked syscalls, visible binaries) and reports fixes rather
  than abandonment. The two are a conditioning/scope pair (detection architecture vs.
  coverage limit), so both are captured normally. `CONTRADICTIONS.md` and open
  `contradiction`-labeled issues were checked; no existing entry covers eBPF coverage
  or event-buffer semantics.
- **Novel** (new to the corpus):
  - The first note on **eBPF-based Kubernetes observability tooling as a security
    surface** — the corpus previously had eBPF only as (a) a working Falco detection
    layer and (b) a technique Kepler deliberately abandoned.
  - **Fixed-size event buffer as a denial-of-visibility surface**, with the
    fail-silent (not fail-loud) drop path as the core defect (Claim 7).
  - An explicit **what-eBPF-tracing-cannot-guarantee** list: bypass via unhooked newer
    syscalls (`openat2`), `io_uring`, and statically linked binaries (Claim 11).
  - A **privileged-observability-agent threat model**: `nodes/proxy` GET RBAC as a
    token-theft escalation path, namespace blocklists for sensitive namespaces, and
    TLS-by-default with an explicit opt-out instead of warning-and-continue (Claims
    8-10).
  - **Audit-severity calibration**: an independent audit can conclude "adequately
    mature" with no Critical/High findings — useful against treating the phrase
    "security audit" as evidence of severe defects (Claim 4).

## Guide Impact

- **Chapter 02 (Observability)** — add a short section on **instrumentation
  coverage and drop visibility**:
  1. State the rule from Claim 7: *a fixed-size event buffer is a denial-of-
     visibility surface; instrument buffer-full/dropped-event counts and alert on
     them.* Generalize the existing silent-data-pipeline-failure principle
     (`guide/02-observability.md:278`) from batch freshness to the collection path: a
     drop is an error condition, not backpressure to be absorbed silently.
  2. State the scoping rule from Claim 11: *kernel-level tracing is coverage of the
     hooked syscall surface, not complete visibility* — require any "we trace every
     syscall" claim to name the hook surface and known bypass classes (unhooked newer
     syscalls, `io_uring`, statically linked binaries). This is an additive correction,
     not a rewrite: Ch02 currently makes no eBPF claims.
  3. Cross-link the deliberate-vs-silent distinction (`blog-cncf-telemetry-that-
     matters-observability-pipelines`, Claims 7/14) and the logged-fail-open pattern
     (`docs-litellm-generic-guardrail-api`, Claim 9): sampling and fail-open are
     acceptable only when policy-driven, counted, and alertable.
- **Chapter 06 (Security & Trust)** — extend the infrastructure/supply-chain material:
  1. Under `### Pin everything; verify releases` (`guide/06-security-and-trust.md:636`),
     add Claim 13 as an independent-audit instance: *security/observability build
     tooling is not exempt from hash/signature verification of build dependencies*,
     and pair the `ig image build` injection (Claim 5) with the existing CI/CD
     anti-patterns section as a build-time injection class.
  2. Add a **privileged observability agent** paragraph to the trust-boundary
     material: a node-level agent is part of the attack surface (Claim 9). Apply
     least-privilege RBAC (notably `nodes/proxy` GET), namespace blocklists for
     sensitive namespaces such as `kube-system` (Claim 10), TLS by default with an
     explicit opt-out rather than a warning-and-continue (Claim 8), and version-scoped
     remediation to the named fixed release (Claim 14). Frame it with the same
     "unconfigured is full access, not least privilege" logic the guide already uses
     for agent gateways (`guide/06-security-and-trust.md:316`): an observability agent
     with cluster-wide reach is a collection-scope decision, not a default.
  3. Use Claim 4 to calibrate how the guide talks about audits: report the severity
     profile and the auditors' conclusion together; "audited" is not a synonym for
     "vulnerable" or for "safe."

## Extraction Notes

- Deep-read the full CNCF post (fetched 2026-10-22). The linked Shielder PDF report,
  the Inspektor Gadget/OSTIF/Shielder/Microsoft announcement posts, and the GitHub
  security advisories were **not** fetched — this note cites only what the CNCF post
  states, and claims are scoped accordingly. In particular, the **six bypass
  scenarios are not individually enumerated in the post** (only `openat2`-style
  unhooked syscalls, `io_uring`, and statically linked libraries are named), so Claim
  11 is worded to match the post rather than inventing the other three.
- **Quote fidelity**: every `Quote` and quoted artifact passage was copied
  character-for-character from the fetched page, including the source's curly
  apostrophe in "operator’s display" and its em dashes. No non-adjacent sentences
  were spliced; where the post presents bullets, the artifact block reproduces the
  bullets verbatim and the claim quote uses the case's leading sentence only.
- **Evidence caveats**: this is a first-party summary of an independent audit. The
  vulnerability facts (CVE IDs, severities, fixed versions) are checkable and treated
  as settled; the "adequately mature" conclusion is the auditors' qualitative
  judgment; the bypass scenarios are summarized rather than enumerated, so their
  individual exploitability is not established here. The post gives no CVSS scores,
  no exploit code, and no measurement of how often the ring-buffer drop occurs in
  practice.
- **`miner-related-notes.md` disposition**: all ten candidate paths evaluated — two
  cited (`blog-cncf-cloud-native-agentic-ai-security-platform`,
  `docs-promptfoo-enterprise-guardrails`), eight explicitly dismissed (see
  Cross-References). Additional cross-refs (`docs-litellm-generic-guardrail-api`,
  `blog-cncf-telemetry-that-matters-observability-pipelines`,
  `blog-cncf-securing-cicd-locking-down-dependencies`,
  `failure-litellm-supply-chain-compromise-march-2026`,
  `blog-cncf-kepler-rearchitected-power-accuracy`) were found by searching
  `source-notes/`. Every cited `Claim N` / `Lesson N` was re-read and verified
  against the named note per MINER.md §4b; the one non-numbered citation (the Falco
  pipeline artifact) is cited by section name as §4b rule 4 requires.
- **No contradiction issue filed**: the Falco/eBPF tension is a coverage-scope pair,
  not opposing guide advice (see Cross-References → Contradicts). No `guide/` edits,
  no `registry/*` edits — registry indexes are rebuilt after merge from this note's
  frontmatter and claim headings.
- `date_extracted` / `last_checked` set to 2026-10-22 UTC (page fetched and
  quote-verified on that date). `confidence_overall: emerging` — the audit facts are
  concrete and settled, but the guide-relevant extrapolations (drop-path rule,
  bypass scoping, privileged-agent threat model) rest on a maintainer summary of a
  single project's audit with no LLM-specific evidence.
