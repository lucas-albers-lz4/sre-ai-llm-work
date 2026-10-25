---
source_url: https://www.cncf.io/blog/2026/07/30/runtime-supply-chain-verification-using-the-node-resource-interface-nri
source_type: blog-post
title: "Runtime Supply Chain Verification using the Node Resource Interface (NRI)"
author: "Sascha Grunert (CRI-O maintainer, CNCF)"
date_published: 2026-07-30
date_extracted: 2026-10-25
last_checked: 2026-10-25
status: current
confidence_overall: emerging
issue: "#1885"
---

# Runtime Supply Chain Verification using the Node Resource Interface (NRI)

> Admission webhooks verify what the API server sees; a synchronous NRI
> `CreateContainer` hook verifies what the container runtime actually executes.
> The article supplies the missing runtime layer for the guide's supply-chain
> section — a concrete bypass taxonomy for admission control, SLSA/VEX/VSA
> attestation verification at container creation, an explicit fail-open vs
> fail-closed trade-off matrix, and an observe → tighten → enforce rollout with
> a Prometheus signal for each phase.

## Source Context

- **Type**: blog-post (CNCF project post, first-party implementation write-up
  for the Supply Chain NRI Plugin).
- **Author credibility**: High for *what the plugin does and how it is
  configured*. Sascha Grunert is a CRI-O maintainer and the plugin's author; the
  post names the hook point, the attestation specifications (SLSA Provenance
  v1, OpenVEX v0.2.0), the verification library (sigstore-go), the metric name,
  the config schema, and the upstream CRI limitation. The configuration and CLI
  output are shown verbatim and the plugin is public
  (`github.com/saschagrunert/nri-supply-chain`), so the mechanics are checkable.
  The post is still a vendor-maintainer self-report: it contains no independent
  benchmark, no production adoption data, and no measured latency or
  false-positive rate.
- **Scope**: Covers the admission-webhook bypass gap, NRI as the runtime hook
  point, the three attestation types and their precedence, the fetch/cache/
  circuit-breaker resilience design, the two-layer config split, deployment
  forms, the three-phase rollout, and an explicit failure-mode/threat-model
  section. Does NOT cover LLM-specific workloads, any measured reliability or
  cost numbers, air-gapped operation (explicitly unsupported), or the internal
  implementation of sigstore-go beyond the verification mode it offers.
- **Prospector framing**: Three concurrent triage runs routed this as
  `triaged:text`, novelty high, priority high. Primary chapter Ch06 (supply-chain
  security), with Ch02 (verification metrics/alerting), Ch01 (fail-closed
  deadlock and node recovery), and Ch05 (failure-policy and rollout trade-offs)
  secondary. The intended value is the runtime enforcement layer and its
  explicit availability trade-offs, not a generic "sign your images" message.

## Extracted Claims

### Claim 1: Admission webhooks are a necessary but insufficient layer — they depend on explicit configuration and network reachability, so misconfigured selectors, webhook outages, static pods, and direct kubelet access can skip verification entirely
- **Evidence**: The post enumerates each bypass path and grounds static pods in
  Kubernetes' own documentation; it frames the result as both a security gap
  (containers missed) and an availability gap (recovery blocked).
- **Confidence**: settled (the bypass paths are documented Kubernetes behavior)
- **Quote**: "However, admission webhooks depend on explicit configuration and network connectivity. Misconfigured namespace selectors can silently skip verification. An admission webhook outage forces a choice between cluster lockup and silent bypass. Static pods and direct kubelet API access bypass admission webhooks entirely."
- **Our assessment**: Buy it. This is the clearest statement in the corpus of
  *why* admission-layer verification is not a complete control. The important
  framing for the guide is that the failure is silent: a misconfigured selector
  produces no alert, so the operator believes verification is on when it is not.

### Claim 2: Static pods can run even when their mirror pod fails admission, and a static pod with an invalid namespace is invisible to the API server — so admission verification never applies to them
- **Evidence**: Kubernetes documents static pods as kubelet-managed; the post
  walks through both the admission-failure and invalid-namespace cases.
- **Confidence**: settled
- **Quote**: "For example, static pods are managed directly by the kubelet. Even when their mirror pod fails admission, the container still runs. A static pod with an invalid namespace name becomes invisible to the API entirely."
- **Our assessment**: Buy it. This is the concrete example that makes the
  defense-in-depth argument non-abstract. Any LLM-ops node running a GPU device
  plugin, CNI, or other static control-plane pod is outside the admission
  control's view.

### Claim 3: Mutating-webhook manipulation to confuse validating webhooks has been disclosed, so admission-layer verification can be silently bypassed rather than only misconfigured
- **Evidence**: Stated as a disclosed technique class, though the post does not
  name a CVE or a specific write-up.
- **Confidence**: emerging (asserted, not cited to a primary disclosure)
- **Quote**: "Techniques using mutating webhook manipulation to confuse validating webhooks have been disclosed, meaning verification can be silently bypassed."
- **Our assessment**: Partially buy it. The mechanism is plausible and matches
  the known ordering of mutating-before-validating webhooks, but the source gives
  no reference, so the guide should present it as a named risk class rather than
  a proven exploit chain.

### Claim 4: Fail-closed admission webhooks can create an availability deadlock — OPA Gatekeeper documents a case where they prevented node recovery after a cluster-wide node deletion
- **Evidence**: Points at Gatekeeper's own "failing closed" documentation and
  restates the deadlock scenario.
- **Confidence**: settled (documented upstream behavior)
- **Quote**: "OPA Gatekeeper’s documentation on failing closed describes a deadlock scenario where fail-closed webhooks prevent node recovery after a cluster-wide node deletion. Admission webhooks can both miss containers (a security gap) and block recovery (an availability gap)."
- **Our assessment**: Buy it. This is the strongest argument that "fail closed
  everywhere" is not a free choice. The guide should treat fail-closed admission
  as a recovery-path hazard to test, not just a security setting.

### Claim 5: NRI is supported by CRI-O 1.28+ and containerd 1.7+ (default-on since containerd 2.0), and a plugin subscribed to `CreateContainer` is called synchronously before the container starts; an error rejects the container
- **Evidence**: Names the runtime versions and the exact lifecycle hook and
  synchronous failure semantics.
- **Confidence**: settled (documented runtime capability)
- **Quote**: "The Node Resource Interface (NRI) is a plugin API supported by both CRI-O (1.28+) and containerd (1.7+, enabled by default since 2.0)."
- **Quote**: "When a plugin subscribes to CreateContainer, the runtime calls it synchronously before the container starts. If the plugin returns an error, the container is rejected."
- **Our assessment**: Buy it. The synchronous call is the whole security
  property: there is no window between the decision and the exec, and no API-layer
  path that can route around the runtime.

### Claim 6: Verification happens at container creation rather than image pull, so pre-pulled and cached images are re-verified before they run
- **Evidence**: The post calls out pre-pulled/cached images explicitly as the
  case pull-time scanning misses.
- **Confidence**: settled (design property of the hook)
- **Quote**: "This includes containers from pre-pulled or cached images. Verification happens at container creation, not at image pull, so even images pulled hours ago without an attestation check get verified before running."
- **Our assessment**: Buy it. This closes a different gap than admission: an
  image can be pulled and admitted while policy was permissive, then executed
  later after policy tightens. Verifying at creation makes the policy in force at
  execution time the one that matters.

### Claim 7: The plugin verifies three attestation types answering distinct questions — SLSA provenance (how it was built), VEX (whether known CVEs are exploitable), and VSA (whether a trusted verifier already checked)
- **Evidence**: Each type is defined with what it proves and what the plugin
  checks; the SLSA check validates signature, builder identity, source repo, and
  build type against the SLSA Provenance v1 predicate.
- **Confidence**: settled for the type definitions; emerging for this
  implementation's completeness
- **Quote**: "Proves the image was produced by a specific builder, from specific source code, in a specific build environment."
- **Our assessment**: Buy it as a taxonomy. It sharpens the guide's existing
  "a SHA pin says what you have; an attestation says who built it" rule into
  three separate questions, and makes clear that signing alone answers none of
  them.

### Claim 8: VEX is evaluated with most-restrictive-wins semantics and any `affected` status blocks the container in enforce mode; the implementation follows OpenVEX v0.2.0
- **Evidence**: Names the four VEX states and the aggregation rule; cites the
  specification version.
- **Confidence**: settled (specified behavior)
- **Quote**: "Any affected status blocks the container in enforce mode."
- **Quote**: "When multiple VEX documents exist, the most restrictive status wins. The implementation follows the OpenVEX v0.2.0 specification."
- **Our assessment**: Buy it. Most-restrictive-wins is the correct default for a
  security control — otherwise a vendor can launder a CVE by publishing a second,
  more permissive VEX document. The guide should state that precedence explicitly
  because it is a policy decision, not an implementation detail.

### Claim 9: A valid passing VSA from a trusted verifier short-circuits SLSA and VEX verification, which is the scale pattern — verify once in CI, attach the VSA, and let nodes validate the summary
- **Evidence**: The post shows the policy `trust.verifiers` entry and the CLI
  output where the reason is "VSA verification passed, skipping direct
  verification"; it explains the per-node cost motivation.
- **Confidence**: emerging (design pattern, no benchmark)
- **Quote**: "If the plugin finds a valid, passing VSA from a trusted verifier, it short-circuits all other checks and admits the image right away. This allows verification to scale across large clusters without repeating cryptographic work per node."
- **Our assessment**: Buy the shape, with a caveat. The trust boundary moves to
  the verifier: a compromised or over-broad verifier can admit anything. The
  guide should pair the VSA pattern with the same trust-root discipline it
  applies to build identities, and note that a failed VSA is a hard rejection
  with no fallback.

### Claim 10: All three attestation types are discovered through a single OCI Referrers API call per digest (with a cosign tag fallback), and signatures are verified with sigstore-go in keyless (Fulcio/OIDC) or key-based mode
- **Evidence**: Names the discovery API, the fallback, and the verification
  library and modes.
- **Confidence**: settled (implementation detail shown)
- **Quote**: "All three attestation types are discovered through a single OCI Referrers API call per image digest (with a cosign tag-based fallback)."
- **Our assessment**: Buy it. The single-referrers-lookup detail matters
  operationally: it bounds registry traffic per digest and makes the network
  dependency predictable, which is exactly what the fail-open/closed decision
  later trades against.

### Claim 11: Resilience is built from per-digest+namespace caching with TTLs, NRI `Synchronize` cache pre-warming on startup, request deduplication, per-registry circuit breakers, a concurrency semaphore, and exponential backoff
- **Evidence**: The post lists each mechanism and the failure it addresses
  (thundering herd, duplicate work, cascading registry failure, unbounded
  concurrency, transient errors).
- **Confidence**: emerging (design description, no measurements)
- **Quote**: "On startup, the plugin receives all running containers via NRI’s Synchronize callback and pre-warms the cache in the background, so restarts don’t cause a thundering herd of registry requests."
- **Quote**: "The plugin also deduplicates concurrent requests: when multiple containers reference the same image, only one verification runs and the rest share its result. Per-registry circuit breakers prevent cascading failures when a registry goes down."
- **Our assessment**: Buy it as an operations checklist. This is the part most
  likely to be skipped by an adopter, and it is where a security control turns
  into a node-availability incident if done naively.

### Claim 12: Operational settings live in a TOML file while per-namespace security policy lives in JSON documents, deliberately so the two can have different owners and change cadences
- **Evidence**: Shows both file forms and the namespace inheritance/override
  model (`default.json`, `production.json`).
- **Confidence**: emerging (a design opinion backed by the config split, not
  measured outcomes)
- **Quote**: "Operational settings like cache size and timeouts change with infrastructure. Security policy, who you trust and what you require, changes with compliance requirements. Keeping them apart means they can be managed by different teams with different change cadences."
- **Our assessment**: Buy it. The split maps a security-policy review cadence
  onto a compliance owner and an ops-tuning cadence onto the platform team. It is
  also the difference between a policy change that needs an auditor and a cache
  TTL change that does not.

### Claim 13: The plugin ships disabled by default and supports a three-phase rollout — observe with `warn` + `missingPolicy: allow`, tighten per namespace, then enforce — with a Prometheus counter and startup warnings as the phase signals
- **Evidence**: Each phase names its config and its observable signal; the
  startup-warning behavior is described concretely.
- **Confidence**: emerging (first-party operational guidance)
- **Quote**: "The plugin ships with verification = “disabled” by default, meaning it does nothing until explicitly configured."
- **Quote**: "The plugin runs verification on every container but never blocks anything. Failed verifications get logged and counted."
- **Quote**: "The plugin will log warnings at startup if permissive defaults are still in place, like fetch_failure_policy set to warn or any missingPolicy set to allow. It actively tells you what to tighten."
- **Our assessment**: Buy it. The "warn mode counts what would have been
  blocked" loop is the reusable rollout pattern: measure the blast radius of
  enforcement before accepting it. The startup warnings are a nice touch because
  they make an accidentally-permissive enforce configuration self-announcing.

### Claim 14: `fetch_failure_policy` defaults to `warn`, which is explicitly fail-open — containers pass when the registry is unreachable — while `deny` trades availability for security by preventing new containers from starting
- **Evidence**: The post states the default, the resulting behavior, and the
  trade-off in plain terms, and says the documentation calls the fail-open
  behavior out.
- **Confidence**: settled (default and behavior stated; the trade-off is a
  design choice)
- **Quote**: "The default is warn: containers pass, a warning gets logged, and the fetch error counter increments. This is explicitly fail-open, and the documentation calls it out. Setting it to deny trades availability for security: registry outages prevent new containers from starting."
- **Our assessment**: Buy it. This is the most reusable artifact in the post for
  the guide: a security control with a documented, configurable availability
  trade-off instead of an implicit one. The guide should not prescribe a default
  — it should require the choice to be explicit and tested.

### Claim 15: The per-registry circuit breaker amplifies the failure-policy choice — in `warn` mode it lets never-verified images bypass verification during cooldown, while in `deny` mode it prevents cascading registry timeouts from blocking the whole node
- **Evidence**: Explains both directions and notes that images cached before the
  outage still verify.
- **Confidence**: settled for the mechanism; emerging for the operational impact
- **Quote**: "In warn mode, this means new, never-verified images from that registry bypass verification during the cooldown. Images verified before the outage are still served from cache. In deny mode, the circuit breaker prevents cascading timeouts from blocking the entire node."
- **Our assessment**: Buy it. The non-obvious interaction is the point: the
  circuit breaker is a resilience feature that *weakens* a fail-open control and
  *strengthens* a fail-closed one. Any operator copying the config without
  understanding this will get a different security posture than they think.

### Claim 16: Missing-attestation policy is per type — an operator can require SLSA provenance with `missingPolicy: deny` while tolerating absent VEX documents with `missingPolicy: allow`
- **Evidence**: The post gives the exact per-type policy keys and the adoption
  rationale.
- **Confidence**: settled (configuration behavior)
- **Quote**: "You might require SLSA provenance (missingPolicy: “deny”) but tolerate missing VEX documents (missingPolicy: “allow”) if your organization hasn’t adopted VEX in its build pipeline yet."
- **Our assessment**: Buy it. Per-type policy is the pragmatic migration path:
  it lets a team enforce the attestation it can produce today without blocking
  on the one the ecosystem has not adopted. It also means "verification enabled"
  is not a single yes/no fact, which the guide should make explicit.

### Claim 17: The threat model assumes node integrity — root can kill the plugin, replace policy files on disk, or disable NRI in the runtime config, so runtime verification does not defend against a fully compromised node
- **Evidence**: The post states the assumption and names the exact disable
  switches (`nri: { disable: true }` in containerd, `--enable-nri=false` in
  CRI-O).
- **Confidence**: settled (explicitly stated limitation)
- **Quote**: "This approach assumes node integrity. An attacker with root access can kill the plugin process, replace policy files on disk, or disable NRI in the runtime configuration entirely (e.g., nri: { disable: true } in containerd, --enable-nri=false in CRI-O)."
- **Our assessment**: Buy it, and the guide must carry it. Runtime enforcement
  moves the trust boundary down but does not remove it. A node-level compromise
  is game over for this control; that is why the post calls it defense-in-depth,
  not a replacement for node hardening.

### Claim 18: The plugin is not usable in air-gapped environments today, and attestation failures surface to operators as a generic CRI `CreateContainerError` because CRI has no precise attestation error type
- **Evidence**: Both are listed under "What's next"; the air-gap limit is a
  consequence of fetching attestations at container-creation time.
- **Confidence**: settled for the current limitation; emerging for the upstream
  fix
- **Quote**: "The plugin currently requires registry connectivity to fetch attestations at container creation time, which means air-gapped environments are not yet supported."
- **Quote**: "Further out, extending CRI error types upstream in Kubernetes would let the kubelet surface precise attestation failure reasons instead of a generic CreateContainerError."
- **Our assessment**: Buy it. The generic error is an operability cost: the
  kubelet tells the operator the container failed, not that attestation was the
  reason. Until CRI exposes a typed error, teams need the plugin's own logs and
  metrics to diagnose a block.

### Claim 19: The plugin deploys as a hardened DaemonSet (DNS+HTTPS egress NetworkPolicy, non-root, read-only rootfs, no capabilities, seccomp, system-node-critical priority), as a sandboxed systemd service, or as a pre-installed NRI plugin for immutable node images
- **Evidence**: The post names each deployment form and the security controls in
  the provided manifests and systemd unit.
- **Confidence**: settled (deployment artifacts described)
- **Quote**: "The provided manifests include a security-hardened container with a NetworkPolicy restricting egress to DNS and HTTPS only. The container runs non-root with a read-only rootfs, no capabilities, a seccomp profile, and system-node-critical priority."
- **Our assessment**: Buy it. `system-node-critical` is the right priority for a
  synchronous admission path — deprioritizing it would turn verification into a
  node-wide container-start outage — but it also means the plugin's own failure
  budget is the node's.

## Concrete Artifacts

### Layering diagram (verbatim from the post)

```
+-------------------------------------------------------------------+
|                         Kubernetes API                            |
|  (Bypassed by static pods, direct kubelet access, or outages)      |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                        Container Runtime                          |
|                     (CRI-O / containerd)                          |
+-------------------------------------------------------------------+
                                  |
                      Synchronous NRI Hook Call
                                  v
+-------------------------------------------------------------------+
|                    Supply Chain NRI Plugin                        |
|   (Verifies SLSA, VEX, & VSA attestations before container start) |
+-------------------------------------------------------------------+
```

### Operational TOML config (verbatim)

```
verification = "enforce"
fetch_timeout = "30s"
fetch_failure_policy = "warn"
cache_ttl = "24h"
cache_failure_ttl = "5m"
policy_dir = "/etc/nri-supply-chain/policies"
```

### Per-namespace policy JSON (verbatim)

```
{
  "trust": {
    "issuers": ["https://token.actions.githubusercontent.com"],
    "sanPatterns": ["https://github.com/saschagrunert/nri-supply-chain/**"],
    "sources": ["github.com/saschagrunert/*"]
  },
  "slsa": { "missingPolicy": "deny" },
  "vex": { "missingPolicy": "deny" }
}
```

### VSA verifier trust entry and short-circuit output (verbatim)

```
{
  "trust": {
    "issuers": ["https://token.actions.githubusercontent.com"],
    "sanPatterns": ["https://github.com/saschagrunert/nri-supply-chain/**"],
    "sources": ["github.com/saschagrunert/*"],
    "verifiers": [
      {
        "id": "https://github.com/saschagrunert/nri-supply-chain/.github/workflows/release.yml"
      }
    ]
  },
  "slsa": { "missingPolicy": "deny" },
  "vex": { "missingPolicy": "deny" }
}
```

```
{
  "image": "ghcr.io/saschagrunert/nri-supply-chain:0.1.5",
  "digest": "sha256:1a8b39eeff74b8bb3e20c7f9fa773d4a9935241f7cc4e1217067c8186c2cee3c",
  "namespace": "default",
  "allowed": true,
  "reason": "VSA verification passed, skipping direct verification",
  "checkResults": [
    {
      "type": "vsa",
      "passed": true,
      "status": "pass",
      "detail": "VSA verification passed"
    }
  ]
}
```

### CLI pre-flight invocations (verbatim)

```
$ nri-supply-chain --config config.toml \
    --verify-image ghcr.io/saschagrunert/nri-supply-chain:0.1.5
```

The post also documents `--validate` for checking config and policy files
without contacting a registry.

### Three-phase rollout signals (paraphrased from the post)

- **Observe**: permissive `default.json` (`missingPolicy: allow`) plus
  `verification = "warn"`; failures logged and counted.
- **Tighten**: namespace-specific policy files; production requires SLSA while
  dev stays permissive; infrastructure images excluded via glob patterns.
- **Enforce**: `verification = "enforce"`; startup warnings for remaining
  permissive defaults; failures appear in pod events as
  `supply chain verification failed: SLSA provenance: builder “X” not in trusted builders list`.

## Cross-References

- **Corroborates**:
  - `failure-litellm-supply-chain-incident-march-2026` — Claim 13 (Cosign
    signing shipped for all GHCR images) and Claim 8 (all GitHub Actions
    pinned) establish build/release-time integrity controls. This source is the
    consumption-side control that verifies those signed artifacts at execution
    time; it does not duplicate them.
  - `blog-cncf-securing-cicd-credentials-verification` — Claim 5 (keyless Cosign
    signing) and Claim 8 (no SLSA provenance, so consumers can verify *who*
    signed but not *how* it was built). The NRI plugin verifies exactly the SLSA
    provenance that note identifies as missing, plus VEX and VSA.
- **Contradicts**: None filed. The explicit fail-open `warn` default could look
  like it opposes the corpus's general "fail closed" advice, but the source
  frames it as a configurable availability/security trade-off, not a universal
  recommendation — a conditioning variable, not a contradiction. No
  contradiction issue was filed.
- **Extends**:
  - `blog-cncf-securing-cicd-locking-down-dependencies` — Claim 1 ("a pinned
    workflow that fetches a compromised dependency is still a compromised
    workflow") makes the build-time trust argument. This source adds the runtime
    enforcement point where the same question is asked about the artifact that
    is about to execute.
  - `blog-cncf-cloud-native-agentic-ai-security-platform` — Claim 3 places agent
    safety constraints in OPA/Kyverno admission policy. That is the API-layer
    enforcement point this source argues is necessary but bypassable; NRI is the
    lower layer for the same policy-as-code instinct.
  - `blog-cncf-inspektor-gadget-security-audit` — Claim 11 documents six
    eBPF-tracing bypass scenarios (e.g. `openat2`, `io_uring`, statically linked
    libraries). It is the runtime-observability analogue of this post's admission
    bypass taxonomy, and it reinforces the same limit: no single node-level layer
    is complete.
  - `failure-litellm-supply-chain-compromise-march-2026` — Lesson 1 (the
    publishing pipeline is a critical supply-chain surface) and Lesson 6
    (artifact signing plus a safe-version audit as the trust-restoration
    mechanism). This source adds the enforcement step after signing, but also
    exposes the boundary: a compromised trusted builder can still produce a
    valid attestation.
- **Novel**: The NRI `CreateContainer` runtime enforcement layer itself. No
  existing note covers NRI, runtime attestation enforcement, SLSA/VEX/VSA
  precedence, VSA short-circuiting, or the `fetch_failure_policy`/circuit-breaker
  interaction. The admission-webhook bypass taxonomy and the fail-closed
  node-recovery deadlock are also new to the corpus.
- **Candidate dismissals**: `docs-google-sre-prodcast-03-07-retail-gaming`,
  `docs-google-sre-slo-engineering-case-studies`,
  `docs-google-sre-ai-engineering-reliable-operations`,
  `docs-google-sre-prodcast-03-13-imperative-declarative`,
  `docs-google-sre-reliable-data-processing-minimal-toil`,
  `docs-google-sre-configuration-specifics`,
  `blog-cncf-agent-doc-access-tool-mix`, and
  `blog-linsun-pod-deployment-unit-ai-agent` were retrieved on lexical overlap
  only and are unrelated to runtime supply-chain enforcement; none is cited.
  `blog-cncf-policy-engine-offline-production-fidelity` was also considered and
  dismissed: it is Kyverno CLI offline-testing work at the admission layer, not
  runtime enforcement.

## Guide Impact

- **Chapter 06 — "Supply-chain security for LLM infrastructure"**: add a
  subsection after "A SHA pin says what you have; an attestation says who built
  it" covering the runtime layer. Specific content: the admission-webhook bypass
  taxonomy (static pods, direct kubelet access, misconfigured selectors, webhook
  outage), the synchronous NRI `CreateContainer` hook, the SLSA/VEX/VSA
  questions and VSA short-circuit, and the explicit threat-model limit (node
  integrity assumed; root can disable NRI). This closes the gap the section
  currently leaves open — it verifies artifacts at build/release time but never
  states who verifies them at execution time.
- **Chapter 06 — fail-open/fail-closed framing**: add the `fetch_failure_policy`
  matrix and the circuit-breaker amplification as the worked example of choosing
  an availability/security trade-off explicitly instead of inheriting a default.
  Recommend that LLM-infra teams document which policy they chose and why, and
  test registry-unreachable behavior before enabling enforcement.
- **Chapter 02 — observability**: add `nri_supply_chain_verification_total{result="fail"}`
  (and circuit-breaker trips / fetch error rates) as the supply-chain posture
  signal, with the observe-phase use case: in `warn` mode this counter measures
  how many containers enforcement would have blocked. This gives Ch02 a concrete
  security SLI instead of only request-path metrics.
- **Chapter 01 — incident response**: add the Gatekeeper fail-closed deadlock
  (fail-closed webhooks preventing node recovery after cluster-wide node
  deletion) to the recovery-path hazards. Recommendation: any fail-closed
  admission control must be tested against node-loss/recovery, and a runtime
  layer's own failure policy must be part of the incident runbook.
- **Chapter 05 — release/config-change trade-offs**: the two-layer config split
  (operational TOML vs per-namespace JSON policy) and the three-phase rollout
  (observe → tighten → enforce) are a concrete instance of separating change
  cadences and gating enforcement on measured blast radius. Recommend adding the
  observe-phase counter as the gate to enforcement, not a date.

## Extraction Notes

- Read the full article, including the layering diagram, both config layers, the
  VSA example, the deployment section, the rollout phases, and the "What's next"
  limitations. No sub-pages were needed; the linked plugin config/operations docs
  are implementation references, not additional argument.
- The source is a first-party maintainer post with no independent measurement.
  Confidence is `emerging` overall: the mechanism and config claims are checkable
  and settled, but adoption/latency/false-positive claims are absent, and the
  mutating-webhook technique (Claim 3) is asserted without a citation.
- All quotes were copied from the article text as fetched; where the source uses
  curly quotes/apostrophes they are preserved.
- Candidate handling per MINER.md §4: the eight unrelated candidates are
  explicitly dismissed above; `blog-cncf-securing-cicd-credentials-verification`
  and `blog-cncf-cloud-native-agentic-ai-security-platform` are cited after
  re-reading their numbered claims. All other cross-references were verified
  against the cited notes' claim headings/lesson headings before writing.
- No contradiction issue was filed. The only apparent tension (fail-open default
  vs general fail-closed advice) is a documented conditioning variable, not a
  material disagreement.
- Did not touch `guide/`, `registry/sources.json`, or
  `registry/claims-index.json`; those are for Smith/derived rebuild.
