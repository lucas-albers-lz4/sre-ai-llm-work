---
source_url: https://www.cncf.io/blog/2026/06/08/breaking-free-of-a-single-datacenter-practical-geo-distributed-ai-operations-with-the-k0smos-platforms
source_type: blog-post
title: "Breaking free of a single datacenter: Practical geo-distributed AI operations with the k0smos platforms"
author: "Prithvi Raj (Mirantis), Alexander Acker (Logsight.ai), and Soeren Becker (Logsight.ai)"
date_published: 2026-06-08
date_extracted: 2026-10-20
last_checked: 2026-10-20
status: current
confidence_overall: emerging
issue: "#1806"
---

# Breaking free of a single datacenter: Practical geo-distributed AI operations with the k0smos platforms

> A vendor-authored CNCF Member Post reporting two SPRIND/exalsius field studies that pool fragmented GPU sites (Frankfurt CPU control plane; Nvidia A100s in Quebec; AMD MI300Xs in Atlanta) under k0s + k0smotron hosted control planes + k0rdent multi-cluster management, with measured Cilium/WireGuard cross-site tunnels (~35ms, ~600MB/s); its transferable content is the practitioner-admitted friction — GPU lifecycle drift across sites and latency-sensitive cross-site training sync — and the co-design pattern of matching the training algorithm's communication budget to the WAN links.

## Source Context

- **Type**: blog-post (CNCF Member Post — vendor/practitioner field report; CNCF highlights k0s and Kubernetes).
- **Author credibility**: Prithvi Raj (Mirantis — vendor behind k0s/k0smotron/k0rdent, i.e., the k0smos stack itself) and Alexander Acker & Soeren Becker (Logsight.ai, exalsius collaborators). The architecture framing is vendor promotion of the authors' own projects; the field studies are conducted with the German Federal Agency for Disruptive Innovation (SPRIND) and are backed by a referenced technical report (arXiv:2602.22760, presented at Flower AI Summit 2026 and EuroSys 2026) and public repos (`exalsius/curtail-llm`, `exalsius/flower-operator`). Treat performance numbers as author-reported unless corroborated by the arXiv report.
- **Scope**: Multi-site, cross-vendor (Nvidia + AMD) AI training operations on a Kubernetes multi-cluster control plane — architecture, two field studies (static geo-distributed training; energy-aware dynamic federation), and a conclusion naming where the operational friction actually lies. Does NOT cover SLOs, alerting, incident response, or observability instrumentation; the "all health checks green but degraded" angle is absent (contrast `failure-cncf-kubeflow-cilium-60-idle-gpus.md`). Published reference links for the first study's NeurIPS papers are unresolved placeholders (`[add-links]`, `[add-link]`) on the page.

## Extracted Claims

### Claim 1: GPU efficiency on fragmented infrastructure is an infrastructure problem, not a compute problem
- **Evidence**: Author framing in the opening section, describing fragmented compute across private clouds, research environments, and mixed-generation on-prem/edge hardware.
- **Confidence**: anecdotal
- **Quote**: "Utilizing GPUs efficiently is no longer just a compute problem. It is fundamentally an infrastructure challenge."
- **Our assessment**: Positioning rather than measurement, but it names the substrate the guide's capacity chapters assume away: most organizations do not own one homogeneous datacenter, they inherit silos. Useful as the problem statement for a geo-distributed ops section.

### Claim 2: A single Kubernetes cluster cannot span geographies, so multi-cluster orchestration becomes non-negotiable for geo-distributed AI
- **Evidence**: Author architectural argument; no counterexample given, and the field studies are built on the multi-cluster premise.
- **Confidence**: emerging
- **Quote**: "This is where multi-cluster orchestration becomes non-negotiable. A single cluster cannot span these geographies, and a manually managed fleet will quickly break teams."
- **Our assessment**: Buy the constraint (etcd/latency and operational reality bound a single cluster's footprint) while noting it is the vendor's framing that conveniently motivates their stack. The "manually managed fleet will quickly break teams" half is asserted, not evidenced — treat as vendor claim.

### Claim 3: The k0smos stack separates node runtime (k0s), hosted control planes (k0smotron), and declarative multi-cluster lifecycle (k0rdent)
- **Evidence**: Architecture description of the three layers: k0s as zero-dependency CNCF-conformant runtime; k0smotron running control planes as isolated, versioned pods in a central management cluster; k0rdent declaring clusters via Kubernetes-native APIs in a GitOps workflow across providers (bare metal, OpenStack, AWS, vSphere).
- **Confidence**: emerging
- **Quote**: "k0smotron operates as the engine for hosted control planes (HCPs). It is a Kubernetes operator that deploys k0s control planes as isolated, versioned pods inside a central management cluster, completely decoupling the control plane from the worker nodes."
- **Our assessment**: The hosted-control-plane pattern (control plane as a scheduled workload, workers attached remotely) is the transferable architectural idea — CPU-only control plane capacity is cheap relative to GPU worker capacity, and control planes become versioned, relocatable pods. The specific product stack is vendor-supplied; the pattern is what to record.

### Claim 4: A cross-border, cross-vendor environment (A100 in Quebec, MI300X in Atlanta, CPU-only control plane in Frankfurt) was operated as one system
- **Evidence**: Field-study topology description; workers provisioned via the k0smotron ClusterAPI provider with vendor-specific GPU software stacks (Nvidia GPU operator for A100s, ROCm operator for MI300Xs).
- **Confidence**: emerging
- **Quote**: "we set up an environment that bridges Nvidia A100 nodes in Quebec with AMD MI300X nodes in Atlanta. The cluster control plane is hosted on CPU-only nodes in Frankfurt, Germany."
- **Our assessment**: The concrete topology is the independent-value part of this vendor post: heterogeneous GPU vendors on different continents with the control plane in a third country, run for two field studies with a referenced technical report. The per-site vendor-operator split (Nvidia operator vs ROCm operator) is the honest detail — heterogeneity is absorbed at the node level, not papered over.

### Claim 5: Cross-site data plane runs over direct Cilium WireGuard P2P tunnels (~35ms latency, ~600MB/s), bypassing centralized VPN gateways while cluster state stays central
- **Evidence**: Author-reported measurements from the field environment; no methodology, packet-size, or variance detail given.
- **Confidence**: anecdotal
- **Quote**: "we deployed the CNCF project Cilium as our CNI, establishing secure, direct Wireguard P2P tunnels (~35ms latency, ~600MB/s) between the worker nodes. Data plane traffic bypasses centralized VPN gateways entirely, while cluster state remains centrally managed in Frankfurt."
- **Our assessment**: The split — encrypted peer-to-peer data plane, centrally managed control state — is the operationally interesting design: throughput scales with direct paths instead of funneling through a hub. The numbers are single-environment, author-reported, and unmethodologized; record them as measured-here, not as expectations for any link. ~35ms RTT is consistent with North-Atlantic-ish intra-continent paths (Quebec–Atlanta is more like ~15-20ms, so the figure likely reflects the worst or average pair — the source does not say).

### Claim 6: AI frameworks (PyTorch Elastic, Ray, vLLM) were integrated on top via k0rdent ServiceTemplates and Helm, provisioned through the state manager using Sveltos
- **Evidence**: Toolchain listing in the Operation step of field study 1.
- **Confidence**: anecdotal
- **Quote**: "we integrated AI frameworks like PyTorch Elastic, Ray, and vLLM using custom k0rdent ServiceTemplates and Helm charts, provisioned via the k0rdent state manager (KSM) using Sveltos."
- **Our assessment**: Asserted integration, not demonstrated configuration — no templates or charts are printed. Worth recording only as the claim that the multi-cluster layer is meant to be the delivery vehicle for the ML toolchain, not just cluster bootstrap.

### Claim 7: Long-haul P2P links were prevented from becoming the bottleneck by co-designing a low-communication training method (decoupled momentum optimization) with the infrastructure
- **Evidence**: Author statement of the co-design; the specialized training layer is said to have "drastically reduced the cross-site communication demands"; details deferred to the NeurIPS publications (placeholder links on the page) and code repo.
- **Confidence**: emerging
- **Quote**: "To prevent our long-distance P2P links from becoming a bottleneck, we implemented a distributed, low-communication training approach utilizing decoupled momentum optimization"
- **Our assessment**: The highest-value pattern in the post: when the interconnect is a WAN, the training algorithm's communication frequency is an infrastructure design parameter, not just an ML choice. This is the geo-distributed analogue of the cross-zone AllReduce penalty documented in `failure-cncf-kubeflow-cilium-60-idle-gpus.md` — there, latency silently ate throughput; here, the workload was reshaped to fit the link. Note the evidence gap: the placeholder reference links mean the quantitative claims behind "drastically reduced" are not verifiable from this page.

### Claim 8: Field study 1 trained five reference model families directly across the mixed AMD/Nvidia nodes, showing distance and heterogeneity are not absolute barriers
- **Evidence**: Author-reported outcome listing GPT-NeoX (LLM), ResNet (CV), GCN (graph), PPO (RL), Wav2Vec2 (audio) trained across the sites; no loss curves, convergence times, or throughput comparisons printed in the post.
- **Confidence**: emerging
- **Quote**: "We successfully trained a diverse set of reference models, spanning GPT-NeoX for LLMs, ResNet for computer vision, GCN for graph learning, PPO for reinforcement learning, and Wav2Vec2 for audio, directly across the AMD and Nvidia nodes."
- **Our assessment**: The breadth (five framework families, two GPU vendors) is more informative than any single number would be — it says the orchestration layer is workload-agnostic in practice. But "successfully trained" without metrics is a smoke-test claim; the arXiv report is where the evidence would live, and it was not fetched for this extraction (see Extraction Notes).

### Claim 9: Field study 2 drove worker provisioning from energy-availability signals (WattTime), turning the GPU pool into an ephemeral, churn-heavy fleet
- **Evidence**: Description of the dynamic setting plus the implementation: an API letting the scheduler provision/deprovision workers on real-time energy-abundance signals, with a custom k0smotron extension translating the signals.
- **Confidence**: emerging
- **Quote**: "We exposed an API allowing the orchestration scheduler to provision and deprovision workers based on real-time energy abundance signals provided by our non-profit partner, WattTime. A custom k0smotron extension translates these signals, activating GPU capacity during favorable windows and releasing it as conditions change."
- **Our assessment**: Novel operational pattern for the corpus: capacity that arrives and departs on an external, non-IT signal (grid carbon/price windows) rather than demand. The SRE implication — the training job must tolerate membership churn as a normal state, not an incident — is the transferable lesson, independent of the energy use case.

### Claim 10: A custom Flower operator reconciles a declarative "Federation" custom resource so nodes join and exit the federation gracefully as they are provisioned/deprovisioned
- **Evidence**: Description of the Kubernetes operator deployed via the k0rdent state manager; repo referenced (`exalsius/flower-operator`).
- **Confidence**: emerging
- **Quote**: "Newly spun-up nodes instantly join the federation as eligible training sites, while deprovisioned nodes exit the reconciliation loop gracefully."
- **Our assessment**: The reconciliation-loop framing is what makes churn survivable: membership is desired state, not a login event. This is the Kubernetes-native shape of federated learning applied to an ephemeral fleet. Single-vendor implementation, but the pattern (declarative membership CR + graceful exit) generalizes.

### Claim 11: Runtime coordination across the ephemeral fleet uses gRPC over the P2P network plus a Redis Pub/Sub queue broadcasting round completions and shutdown signals
- **Evidence**: Description of the custom server-side scheduling strategy in field study 2.
- **Confidence**: anecdotal
- **Quote**: "At runtime, the coordinator and active sites communicate via gRPC over our established secure P2P network. We implemented a custom server-side scheduling strategy, relying on a Redis Publish-Subscribe queue to reliably broadcast round completions and shutdown signals across the ephemeral fleet."
- **Our assessment**: Concrete enough to extract: pub/sub for broadcast control signals (round boundaries, shutdown) decouples the coordinator from knowing the current membership — a necessary property when workers vanish with energy windows. No failure-mode discussion (what happens to an in-flight round when a site drops mid-step), which is exactly the question an SRE would ask.

### Claim 12: The real friction in fragmented environments was GPU lifecycle management and cross-site networking — not the control-plane stack
- **Evidence**: The conclusion's candid post-mortem of the two field studies: cloud-specific kernels, conflicting pre-installed drivers, and partially configured node states despite Nvidia/ROCm operators; site-specific network restrictions and latency-sensitive `torch.distributed` synchronization despite WireGuard/Cilium.
- **Confidence**: emerging
- **Quote**: "While the k0smos stack provided a highly stable, cloud-native foundation, these field studies highlighted where friction lies in fragmented environments: GPU lifecycle management and cross-site networking."
- **Quote**: "Despite the heavy lifting done by the Nvidia and ROCm operators, dealing with cloud-specific kernels, conflicting pre-installed drivers, and partially configured states requires deep operational awareness."
- **Quote**: "Similarly, while WireGuard and Cilium handled secure cross-site connectivity with negligible bandwidth overhead, managing site-specific network restrictions and latency-sensitive synchronization for distributed training (like torch.distributed) remains a complex engineering challenge."
- **Our assessment**: This is the most SRE-relevant passage and the reason to mine the post despite the vendor framing: the authors, having built the orchestration stack themselves, report that the residual failure class is node-level GPU bring-up drift (drivers/kernels/half-configured states) and WAN-sensitive collectives — i.e., the boring, per-site toil and the physics of synchronization, not the multi-cluster control plane. "Getting nodes into a clean, GPU-ready state" as a recurring, site-specific activity is a capacity/readiness precondition the guide should name.

## Concrete Artifacts

**Field-study 1 operational procedure (verbatim structure from source; the three numbered layers):**
```
1. Provisioning: We utilized the k0smotron ClusterAPI provider to trigger deployments directly from our management cluster in Frankfurt. The workers in Quebec and Atlanta were provisioned with k0s and their respective, vendor-specific GPU software stacks (the Nvidia GPU operator for the A100s, and the ROCm operator for the MI300Xs).

2. Operation: For cross-site connectivity, we deployed the CNCF project Cilium as our CNI, establishing secure, direct Wireguard P2P tunnels (~35ms latency, ~600MB/s) between the worker nodes. Data plane traffic bypasses centralized VPN gateways entirely, while cluster state remains centrally managed in Frankfurt. On top of this network, we integrated AI frameworks like PyTorch Elastic, Ray, and vLLM using custom k0rdent ServiceTemplates and Helm charts, provisioned via the k0rdent state manager (KSM) using Sveltos.

3. Orchestration: We added the operational abstraction and business logic required to execute distributed training and batch workloads reliably over the P2P network.
```
*(Source: CNCF blog post, "Field studies built on top of a geo-distributed heterogeneous AI infrastructure" section.)*

**Field-study 2 dynamic-churn implementations (verbatim structure from source; the three numbered implementations):**
```
1. We exposed an API allowing the orchestration scheduler to provision and deprovision workers based on real-time energy abundance signals provided by our non-profit partner, WattTime. A custom k0smotron extension translates these signals, activating GPU capacity during favorable windows and releasing it as conditions change.

2. We developed a custom Kubernetes operator for the Flower AI framework (github links in References). Deployed via the k0rdent state manager (KSM), this operator reconciles a declarative "Federation" custom resource. Newly spun-up nodes instantly join the federation as eligible training sites, while deprovisioned nodes exit the reconciliation loop gracefully.

3. At runtime, the coordinator and active sites communicate via gRPC over our established secure P2P network. We implemented a custom server-side scheduling strategy, relying on a Redis Publish-Subscribe queue to reliably broadcast round completions and shutdown signals across the ephemeral fleet.
```
*(Source: same section, second field study. The rendered page uses curly quotes around "Federation".)*

**Measured cross-site network figures (author-reported):** WireGuard P2P tunnels between worker nodes at ~35ms latency and ~600MB/s; "negligible bandwidth overhead" for WireGuard/Cilium per the conclusion. No test methodology given.

**Referenced repositories and report (from the post's References section):**
```
k0s:              https://github.com/k0sproject/k0s
k0smotron:        https://github.com/k0sproject/k0smotron
k0rdent:          https://github.com/k0rdent/k0rdent
Cilium:           https://github.com/cilium/cilium
Technical report: https://arxiv.org/abs/2602.22760   (Dynamic energy-aware AI workload orchestration)
curtail-llm:      https://github.com/exalsius/curtail-llm
Flower operator:  https://github.com/exalsius/flower-operator
Presentation:     https://youtu.be/VKC5r0wBgm0
```
Caveat: the first field study's NeurIPS paper and code links are unresolved placeholders (`[add-links]`, `[add-link]`) in the published post; the second study's links resolve.

## Cross-References

- **Corroborates**:
  - `failure-cncf-kubeflow-cilium-60-idle-gpus.md` — **Claim 3** (same root cause manifests as cross-zone latency where "gradient synchronization (NCCL AllReduce) pays cross-zone round-trip time on every step. Throughput quietly drops 30–60% with no error at all") and **Claim 7** ("The pattern generalizes. Any topology-aware CNI plus any distributed ML framework can hit the same wall"). This note's Claim 7 (co-design a low-communication training method so WAN links are not the bottleneck) and Claim 12 (latency-sensitive `torch.distributed` sync "remains a complex engineering challenge") are the geo-scale confirmation of the same binding constraint: inter-node RTT, not node health, governs distributed-training throughput. Different remedies — co-location within a zone there, algorithm/communication co-design here — which is the expected conditioning variable (sites you control vs. sites you deliberately span). Both posts use Cilium, but for opposite purposes (zone-boundary network policy vs. cross-site WireGuard tunnels).
  - `blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` — **Claim 7** ("The first Pod has taken the only A5000, so the second Pod falls back to T10 — exactly the expected behavior of firstAvailable when the top choice is unavailable"), the heterogeneous-GPU-selection-within-one-cluster case. This note extends the heterogeneity axis across clusters, vendors (Nvidia + AMD), and borders; DRA-style device selection is intra-cluster, whereas here heterogeneity is absorbed per-site via vendor-specific operators (Nvidia GPU operator / ROCm operator). Complementary layers, same fragmentation problem.

- **Contradicts**: None. No existing note claims geo-distributed AI operations are easy, that a single cluster spans regions, or that cross-site latency is a solved problem; the kubeflow/Cilium note's "all health checks green but degraded" failure mode is simply out of scope here (this post describes no monitoring at all). Verified against `CONTRADICTIONS.md` and open `contradiction`-labeled issues — no entry. No contradiction issue filed.

- **Extends**:
  - `blog-cncf-running-self-hosted-llm-kubernetes-vllm.md` — single-namespace, single-node, CPU-only vLLM serving lab. This note is the multi-site counterpart: the same "run AI on Kubernetes" territory at geo-distributed, GPU, cross-vendor scale, where the failure surface moves from pod bootstrap to GPU lifecycle drift, WAN latency, and membership churn.
  - `docs-google-sre-prodcast-04-06-fletcher-vibe-coding.md` — **Claim 3**'s theme (reliability must account for a composition of components with partly-opaque ceilings) has a physical-substrate instance here: a fleet composed of sites with different kernels, drivers, and network restrictions, each with its own readiness ceiling.

- **Novel**: First source note in the corpus covering:
  1. **Geo-distributed, cross-vendor (Nvidia + AMD) AI training operations** on a Kubernetes multi-cluster control plane — no existing note covers multi-site GPU fleets.
  2. **Hosted control planes (k0smotron) decoupling CP from GPU workers** as an AI-infrastructure pattern (CP CPU-only in a third region).
  3. **Measured cross-site Cilium WireGuard P2P figures** (~35ms, ~600MB/s) with a data plane that bypasses central VPN gateways.
  4. **Energy-window-driven capacity churn** (WattTime signals → provision/deprovision) with federated-learning membership reconciliation (Flower operator, declarative Federation CR, Redis Pub/Sub round/shutdown broadcast).
  5. **The practitioner-admitted residual friction class**: GPU lifecycle drift across sites (cloud-specific kernels, conflicting pre-installed drivers, partially configured states) surviving even vendor GPU operators — the failure mode that is invisible to cluster-lifecycle tooling.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — Cost, capacity, and fallback patterns, guide/05-llm-ops-reliability.md:970)**: Add a "geo-distributed capacity" subsection: (a) GPU readiness is a capacity precondition — nodes joining a GPU fleet arrive with cloud-specific kernels, conflicting pre-installed drivers, and partial configuration; treat "clean, GPU-ready state" as a recurring per-site bring-up activity, not a one-time install [source: blog-cncf-geo-distributed-ai-k0smos, Claim 12]; (b) when training/serving spans WAN links, the workload's communication pattern is an infrastructure design parameter — budget cross-site RTT against the collective/sync frequency (here: ~35ms motivated a low-communication training method) [Claim 5, Claim 7]; (c) for ephemeral/churn-driven capacity, membership must be reconciled desired-state (declarative federation CR, graceful exit) with broadcast control signals (pub/sub), not static roster assumptions [Claim 10, Claim 11].

- **Chapter 05 (distributed training failure classes)**: Pair with the existing Kubeflow/Cilium cross-zone finding: the corpus now has both directions of the same constraint — cross-zone RTT silently destroying AllReduce throughput within one cluster, and WAN RTT reshaping the training algorithm across clusters. Recommend one paragraph citing both, making explicit that `torch.distributed`/NCCL synchronization latency is the axis to reason about, at whatever geographic scale.

- **Chapter 02 (Observability)**: This source is a negative example — it reports zero SLOs, alerts, or instrumentation for a fleet whose membership changes with grid-energy windows. Recommend the guide state that dynamic-capacity training fleets need per-site GPU utilization and membership-churn telemetry (the kubeflow note's GPU-util + pod-zone metrics are the intra-cluster precedent) before the fleet is ephemeral, not after an incident.

- **Chapter 00 (Principles)**: Supports the fragmentation/heterogeneity premise ("compute resources are fragmented across private clouds, research environments, and mixed generations of on-prem and edge hardware" [Claim 1]) and the field-study-before-scale pattern — two validation field studies (static, then churn) precede any production claim. One-line citation only.

## Extraction Notes

- Deep-read of the full CNCF Member Post (single page) on 2026-10-20; all quotes copied character-for-character from the fetched page, including the source's own spelling variance ("Wireguard" in the Operation step vs "WireGuard" in the conclusion) and the curly quotes around "Federation". No paywall. No substantive sub-pages followed: the post's outbound links are GitHub repos and the arXiv report; the first field study's NeurIPS/code links are unresolved placeholder text (`[add-links]`, `[add-link]`) on the page itself, so the quantitative backing for the low-communication-training claims was not directly verifiable from this source (arXiv:2602.22760 not fetched; kept out of the note per no-guessing). Second study's links (curtail-llm, flower-operator, arXiv, video) resolve in the References list and are recorded as artifacts.
- Per the Prospector triage, product/diagram marketing language was not extracted; architecture claims are recorded with vendor framing flagged (Claims 2, 3, 6 are the vendor-supplied product story), and the field-study numbers/friction (Claims 4, 5, 8-12) are the independent-value material.
- `confidence_overall: emerging` — concrete topology and candid friction from two field studies with a peer-reviewed technical report referenced, but every performance figure is author-reported without methodology, the first study's evidence links are placeholders on the page, and the whole stack is the authors' own product line.
- Cross-reference candidates from `miner-related-notes.md`, each dismissed in one line (lexical retrieval returned SRE prodcasts / LiteLLM-param docs / launch-process material, none on geo-distributed GPU ops):
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SLOs; no infrastructure-distribution content.
  - `docs-google-sre-reliable-product-launches.md` — launch checklists; unrelated.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — multi-agent security platform on Kubernetes, but single-cluster agent-deployment concerns (mTLS, policy-as-code); no multi-site or GPU-lifecycle material.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative vs declarative config; k0rdent is declarative GitOps but the reconciliation-model topic does not touch this note's claims.
  - `docs-google-sre-team-lifecycles.md` — SRE team formation; unrelated.
  - `docs-litellm-batches-api.md` — LiteLLM batch rate limiting; unrelated.
  - `docs-google-sre-eliminating-toil.md` — toil definition/measurement; the GPU bring-up friction (Claim 12) is toil-adjacent but the note's taxonomy adds nothing to the extraction.
  - `docs-google-sre-slo-engineering-case-studies.md` — SLO adoption case studies; unrelated (and this source has no SLOs).
  - `docs-litellm-anthropic-advisor-tool.md` — LiteLLM advisor tool; unrelated.
  - `docs-litellm-completion-function-call.md` — LiteLLM function-calling semantics; unrelated.
- The three cited cross-references (`failure-cncf-kubeflow-cilium-60-idle-gpus`, `blog-cncf-understanding-dynamic-resource-allocation-kubernetes`, `blog-cncf-running-self-hosted-llm-kubernetes-vllm`, plus the fletcher Prodcast for the Extends line) were re-read and their claim numbers verified against the cited content before writing (MINER.md §4b). A direct search of `source-notes/` for `geo-distribut|multi-cluster|k0rdent|k0smotron|wireguard|federated|energy-aware|wattime|cross-site` confirmed no other overlapping note exists. No contradiction found; no contradiction issue filed.
