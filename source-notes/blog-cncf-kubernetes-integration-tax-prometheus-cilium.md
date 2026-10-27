---
source_url: https://www.cncf.io/blog/2026/05/28/the-kubernetes-integration-tax-prometheus-cilium-and-production-reality
source_type: blog-post
title: "The Kubernetes integration tax: Prometheus, Cilium and production reality"
author: "Rishi Mondal, SRE at Obmondo and CNCF KubeStellar Maintainer"
date_published: 2026-05-28
date_extracted: 2026-10-27
last_checked: 2026-10-27
status: current
confidence_overall: emerging
issue: "#1897"
---

# The Kubernetes integration tax: Prometheus, Cilium and production reality

> The hidden cost of running multiple CNCF projects together in production is wiring them — the failures live in the gaps between correctly installed projects. The article documents concrete integration failures (Prometheus/kubelet duplicate timestamps, cert-manager HTTP-01 vs ingress redirect, missing Cilium ServiceMonitors) and a structural fix (two-repo GitOps split with generated monitoring and chart-embedded policies).

## Source Context

- **Type**: blog-post (CNCF Community Post — practitioner experience report)
- **Author credibility**: Rishi Mondal, SRE at Obmondo and CNCF KubeStellar maintainer. Experience across multiple cloud providers (AWS, GCP, Azure, Hetzner bare metal). Describes real production failures encountered, but the quantitative claims ("80% of platform team time") are unsourced estimates.
- **Scope**: Covers integration failures between CNCF projects (Prometheus/kubelet, cert-manager/ingress, Cilium/Prometheus), Cluster API multi-cloud patterns, and a two-repo GitOps architecture with generated monitoring (Jsonnet), chart-embedded NetworkPolicies, automated backup provisioning, Sealed Secrets, and policy enforcement. Does NOT cover AI/LLM-specific concerns; focus is general platform engineering. No benchmarks or measurements provided.

## Extracted Claims

### Claim 1: The integration tax is the hidden cost of wiring multiple CNCF projects together — failures live in the gaps between projects, not in individual projects
- **Evidence**: Practitioner experience report based on real incidents across production clusters.
- **Confidence**: emerging
- **Quote**: "This is what’s known as the integration tax. It’s the hidden cost of running multiple CNCF projects together in production, and it’s where most platform teams spend 80% of their time — not installing projects and not tuning them individually, but wiring them together. Hence, they actually talk to each other."
- **Our assessment**: The mechanism is sound — correctly installed projects can be invisible to each other. The "80%" figure is unsourced and should be treated as the author's estimate, not a measured fact.

### Claim 2: Prometheus and kubelet produce duplicate timestamps causing PrometheusDuplicateTimestamps alerts
- **Evidence**: Concrete failure observed in production; root cause identified by reading kubelet source.
- **Confidence**: settled (concrete bug pattern with known fix)
- **Quote**: "kubelet exposes metrics on four scrape paths. Two of them — `/metrics` and `/metrics/probes` — both emit `process_start_time_seconds` with identical timestamps because they’re the same process. Prometheus dutifully scrapes both, sees duplicate samples, and fires `PrometheusDuplicateTimestamps`. The alert is noisy. The root cause is invisible without reading the kubelet source. But the fix is a Jsonnet relabeling rule that drops an entire scrape endpoint."
- **Our assessment**: This is a concrete, reproducible integration defect. The fix pattern (relabel drop) is actionable and should be documented.

### Claim 3: cert-manager HTTP-01 challenges fail silently when ingress controllers enforce global HTTP→HTTPS redirects
- **Evidence**: Observed across three cloud providers in production.
- **Confidence**: settled
- **Quote**: "cert-manager’s HTTP-01 ACME challenge expects to serve a token over plain HTTP. But if your ingress controller enforces a global HTTP-to-HTTPS redirect — which it should for security — every ACME validation request gets 301’d before reaching cert-manager’s solver pod. Certificate renewals fail silently. You find out when customers see expired TLS warnings in their browsers. The fix? DNS-01 challenges via Route53, Cloud DNS, or Azure DNS. But that’s cloud-specific IAM scoping that no Helm chart configures by default."
- **Our assessment**: Classic case where two security controls conflict. The fix requires switching challenge type and proper IAM configuration - important to capture.

### Claim 4: Missing ServiceMonitors for Cilium agent and operator pods leave Grafana panels blank while Hubble metrics appear healthy
- **Evidence**: Direct production incident.
- **Confidence**: settled
- **Quote**: "Grafana dashboards showed blank panels for Cilium network metrics. Hubble was working fine — DNS visibility, TCP flows, and HTTP latency were all there in the Hubble UI. But the on-call engineer staring at Grafana at 2 AM couldn’t see any of it. The reason? Prometheus had no ServiceMonitors wired to Cilium’s agent and operator pods."
- **Our assessment**: Demonstrates projects can be functional independently but not integrated. Highlights importance of wiring.

### Claim 5: A two-repo GitOps split (platform repo + per-environment config repo) prevents per-cluster ticket proliferation for integration fixes
- **Evidence**: Architecture used successfully across AWS, GCP, Azure, bare metal.
- **Confidence**: emerging
- **Quote**: "Platform repo: 100+ Helm charts with production-tested defaults. Cilium NetworkPolicies baked into each chart. Prometheus ServiceMonitors pre-wired. cert-manager annotations are configured for the right challenge type. This configuration is shared across all clusters in all clouds. Config repo: One per customer or environment. Only values that genuinely vary between clusters: domain names, node counts, GCP project IDs, AWS account roles, and Hetzner server types. ArgoCD watches both. When we fix the Prometheus duplicate timestamps issue in the platform repo, that fix propagates to every cluster (AWS, GCP, Azure, bare metal) via a version bump. One pull request. No per-cluster tickets."
- **Our assessment**: Strong structural pattern for managing integration toil. The "platform + config split" is a concrete implementation pattern worth documenting.

### Claim 6: Generate monitoring with Jsonnet rather than hand-assembling YAML to make upgrades diffable and reproducible
- **Evidence**: Production practice.
- **Confidence**: emerging
- **Quote**: "We use Jsonnet to produce the entire kube-prometheus stack from a single per-cluster vars file. Custom alerting mixins — Velero backup age, CloudNativePG replication lag, kubelet certificate expiry — live as Jsonnet libraries alongside upstream rules. A single build.sh produces everything. Reproducible. Diffable. Version-controlled. When Prometheus upgrades break your custom rules, the diff is immediate, and the fix is testable before it reaches production."
- **Our assessment**: Good practice for managing complex observability stacks. Reduces toil during upgrades.

### Claim 7: Embed NetworkPolicies in Helm charts rather than reverse-engineering them from Hubble flows post-deployment
- **Evidence**: Production practice.
- **Confidence**: emerging
- **Quote**: "We ship Cilium NetworkPolicy templates inside 20+ Helm charts. Each chart declares its own egress requirements: what external APIs it calls and what internal services it needs. Reverse-engineering network rules from Hubble flow logs after deployment is like writing tests after shipping. Your policies drift. Security becomes guesswork. Embedding them in charts means the policy lives where it’s maintained."
- **Our assessment**: Shifts policy left - good principle. Prevents drift.

### Claim 8: Automate disaster recovery prerequisites (Velero backup buckets) at cluster bootstrap
- **Evidence**: Production practice.
- **Confidence**: emerging
- **Quote**: "Our provisioning creates cloud storage buckets (S3, GCS, Azure Blob) for Velero backups during initial cluster setup — not as a follow-up task that lives in a Jira ticket for six months. If you can run the bootstrap, you can recover from total cluster loss. Disaster recovery stops being a hope and becomes a testable reality."
- **Our assessment**: Good operational practice - make recovery testable from day one.

### Claim 9: Encrypt secrets with Sealed Secrets and commit them to Git for full auditability
- **Evidence**: Production practice.
- **Confidence**: emerging
- **Quote**: "Every credential — deploy keys, cloud IAM, and TLS certs — gets encrypted with Sealed Secrets before it touches Git. The decryption key gets backed up to cloud storage. Your Git repository becomes a complete, auditable record of every cluster’s state, including secrets. Drift detection works. Recovery is one pull request and one clusterctl move away."
- **Our assessment**: Enables GitOps for secrets. Note this is one approach; External Secrets Operator is another (mentioned in related notes).

### Claim 10: The integration tax compounds with every upgrade and new project - wiring debt grows over time
- **Evidence**: Author's observation from long-term operations.
- **Confidence**: emerging
- **Quote**: "The integration tax isn’t a one-time fee. Every Kubernetes version bump, every Helm chart upgrade, and every new CNCF project introduces new integration surfaces. If your monitoring is hand-crafted YAML, upgrading kube-prometheus from v0.13 to v0.17 means manually diffing hundreds of generated files. If it’s Jsonnet, it’s one line — the debt compounds."
- **Our assessment**: Strong point about compounding maintenance cost. Architecture choices matter for long-term toil.

## Concrete Artifacts

### PrometheusDuplicateTimestamps root cause and fix
```text
kubelet scrape paths: /metrics and /metrics/probes both emit process_start_time_seconds 
with identical timestamps (same process). Prometheus sees duplicate samples → 
PrometheusDuplicateTimestamps alert. Fix: Jsonnet relabeling rule dropping one endpoint.
```

### cert-manager ACME HTTP-01 vs ingress redirect
```text
Ingress controller enforces global HTTP→HTTPS 301 redirect → ACME HTTP-01 validation 
request intercepted before reaching solver pod → renewal fails silently → expired TLS 
warnings appear. Fix: use DNS-01 challenges (Route53/Cloud DNS/Azure DNS) with 
appropriate cloud IAM scoping.
```

### Two-repo GitOps structure
```text
Platform repo (shared across all clusters): 100+ Helm charts with baked-in NetworkPolicies, 
pre-wired ServiceMonitors, correct cert-manager annotations
Config repo (per-environment): only varying values (domains, node counts, cloud-specific IDs/roles)
ArgoCD watches both → integration fixes propagate via single version bump
```

## Cross-References

- **Corroborates**:
  - [blog-cncf-4-body-problem-sre-context.md](blog-cncf-4-body-problem-sre-context.md) Claim 2 — both note failures live at intersections between systems (code/infrastructure/runtime/knowledge bodies vs. between CNCF projects). Different framing but same core thesis.
  - [failure-cncf-kubeflow-cilium-60-idle-gpus.md](failure-cncf-kubeflow-cilium-60-idle-gpus.md) — another example of Cilium integration issues causing unexpected behavior; different root cause than missing ServiceMonitors.
  
- **Contradicts**: None identified.

- **Extends**:
  - [blog-cncf-telemetry-that-matters-observability-pipelines.md](blog-cncf-telemetry-that-matters-observability-pipelines.md) — extends observability discussions with concrete scrape-path duplication issues and integration gotchas.
  - [blog-cncf-secret-sprawl-external-secrets-operator.md](blog-cncf-secret-sprawl-external-secrets-operator.md) — relates to secrets management; Sealed Secrets vs External Secrets are different approaches with different trade-offs.
  
- **Novel**:
  - Concrete integration failure modes between specific CNCF projects (kubelet/Prometheus duplicate timestamps, cert-manager ingress redirect collision, Cilium Prometheus invisibility)
  - The "integration tax" framing as quantifiable toil
  - Two-repo GitOps split as systematic solution to integration tax
  - Jsonnet-generated monitoring as defense against compounding integration debt
  - Chart-embedded NetworkPolicies as "shift-left" for network policy management

## Guide Impact

- **Chapter 02 (Observability)**: Add concrete Prometheus/kubelet scrape path collision case with relabel fix. Document that even "healthy" components (Hubble UI working) can have missing observability wiring. Include ServiceMonitor coverage as a checklist item.
- **Chapter 03 (Runbooks and Agents)**: The integration tax applies to agent/tooling stacks too - different components may be correct individually but fail to interoperate. The two-repo pattern for managing configuration across environments is relevant.
- **Chapter 04 (On-call and Toil)**: Strong support for toil-reduction via automation and standardization. The "generate, don't assemble" pattern reduces toil from upgrades. Chart-embedded policies reduce toil from post-hoc network policy engineering.
- **Chapter 06 (Security and Trust)**: cert-manager HTTP-01 vs redirect is a good example of conflicting security controls requiring careful configuration. Sealed Secrets pattern for GitOps is relevant.

## Extraction Notes

- Read full article via WebFetch. No sub-pages followed.
- All quotes are verbatim from the source text.
- The "80% of platform team time" and "20-30 cloud native tools" figures are unsourced estimates from the author - recorded as claims but marked as unmeasured.
- No AI/LLM-specific content; relevance is purely to general SRE/platform engineering as noted by Prospector.
- Cross-references checked against existing source notes. The failures described (PrometheusDuplicateTimestamps, ACME/redirect collision) don't appear to be covered elsewhere.
- No contradiction with existing notes found.
