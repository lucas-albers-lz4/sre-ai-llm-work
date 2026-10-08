---
source_url: https://www.cncf.io/blog/2026/07/01/understanding-dynamic-resource-allocation-in-kubernetes
source_type: blog-post
title: "Understanding dynamic resource allocation in Kubernetes"
author: "ChengHao Yang (CNCF Ambassador)"
date_published: 2026-07-01
date_extracted: 2026-10-08
last_checked: 2026-10-08
status: current
confidence_overall: emerging
issue: "#1634"
---

# Understanding dynamic resource allocation in Kubernetes

> A practitioner tutorial describing Dynamic Resource Allocation (DRA) in Kubernetes, with concrete examples demonstrating device selection via CEL expressions, ResourceClaim/ResourceClaimTemplate semantics, fallback behavior, capacity constraints, and GPU time-slicing. Includes operational observations about claim lifecycle behavior during rolling updates and version-specific notes about DRA GA and device health reporting.

## Source Context

- **Type**: blog-post (CNCF Ambassador Post — hands-on practitioner tutorial)
- **Author credibility**: ChengHao Yang, CNCF Ambassador. Lab-based writeup using CNTUG Infra Labs hardware with concrete, reproducible commands, YAML examples, and observed outputs.
- **Scope**: Covers DRA primitives (DeviceClass, ResourceSlice, ResourceClaim, ResourceClaimTemplate), device selection via CEL (product name, memory capacity), firstAvailable fallback, sharing semantics, and time-slicing configuration. Focuses on NVIDIA GPU allocation with DRA driver. Does NOT provide production metrics or incident data; tests are lab-scale (3 workers with specific GPU mix).

## Extracted Claims

### Claim 1: DRA reached GA in Kubernetes v1.35
- **Evidence**: The author states DRA recently reached GA and notes NVIDIA moved dra-driver-nvidia-gpu into Kubernetes SIGs with documentation dropping the Beta label.
- **Confidence**: emerging
- **Quote**: "Dynamic Resource Allocation (DRA) recently reached GA in Kubernetes v1.35, and I believe many of us are eager to give it a try. Adding to the momentum, NVIDIA has moved dra-driver-nvidia-gpu into Kubernetes SIGs, with the documentation dropping the Beta label — a sign that the technology and its standards are gradually maturing."
- **Our assessment**: This is a version-specific status claim about DRA reaching GA in v1.35. As an API stability/version claim, it should be pinned with dates and versions; the author explicitly gives the lab versions (K8s v1.35.3). Downgraded from `settled` to `emerging`: the sole evidence is the author's assertion in a single lab-scale blog post and the claim is not verifiable within the corpus. It should be confirmed against the Kubernetes v1.35 release notes / DRA KEP before the guide relies on it.

### Claim 2: Device health reporting becomes available starting in Kubernetes v1.36
- **Evidence**: The summary section notes that starting with K8s v1.36, device health reporting is available.
- **Confidence**: emerging
- **Quote**: "Starting with K8s v1.36, device health reporting is also available, so Pods no longer simply show Error — we can tell whether the failure stems from the device or from the application."
- **Our assessment**: Version-specific claim about observability/fault attribution capability arriving in v1.36. This is relevant to incident triage doctrine (distinguishing device faults from application faults). Downgraded from `settled` to `emerging`: as with Claim 1, the sole evidence is a single lab-scale post and the claim is not verifiable within the corpus. Confirm against Kubernetes v1.36 release notes before the guide cites the v1.36 version boundary.

### Claim 3: ResourceSlice has a maximum device entry limit of 128, or 64 when any device uses taints or counters
- **Evidence**: The author explains ResourceSlice behavior, including splitting when device count exceeds what fits in a single object.
- **Confidence**: emerging
- **Quote**: "When the device count exceeds what fits in a single object (up to 128 entries, or 64 if any device uses taints or counters), the driver splits the Pool across multiple ResourceSlices."
- **Our assessment**: Concrete implementation constraint documented in the post — a specific operational detail about ResourceSlice scaling limits. Downgraded from `settled` to `emerging`: the sole evidence is the author's prose in a single lab-scale post (the 128/64 figures are not demonstrated by a ResourceSlice dump in the source, and are not verifiable within the corpus). Confirm against the DRA ResourceSlice API documentation before the guide states the limits as fact.

### Claim 4: DRA abstracts device allocation in a Storage-like model (DeviceClass ≈ StorageClass, ResourceClaim ≈ PVC)
- **Evidence**: The author draws the analogy explicitly when introducing ResourceClaim/ResourceClaimTemplate.
- **Confidence**: settled
- **Quote**: "Do these concepts feel familiar? DRA is modeled after Storage in Kubernetes — PersistentVolumeClaim and PersistentVolumeClaimTemplate (the latter only existing inside StatefulSet), with DeviceClass playing roughly the role of StorageClass."
- **Our assessment**: Conceptual framing explaining the design lineage. The analogy helps clarify semantics (claim independence vs. template-generated per-pod claims).

### Claim 5: A Pod rebuilt by RollingUpdate does not reclaim its previous GPU because the old ResourceClaim is not yet released
- **Evidence**: The author explicitly warns about this behavior in Scenario II when deleting the A5000 Pod with Deployment default RollingUpdate strategy.
- **Confidence**: settled
- **Quote**: "With the configuration above, no, it won’t return to A5000. The Deployment default strategy.type is RollingUpdate; while the old Pod is Terminating, its ResourceClaim hasn’t been released yet. The Deployment controller immediately creates a new Pod and a new ResourceClaim from the ResourceClaimTemplate. Since the A5000 is still held by the old Pod, the new claim falls back to T10."
- **Our assessment**: This is the most operationally significant finding. It describes a rollout timing/claim lifecycle trap where fallback behavior interacts with RollingUpdate to prevent returning to the preferred device. The author characterizes this as a consequence of claim retention during termination, not a bug. This is a concrete failure/reliability concern for GPU-serving workloads during rolling updates.

### Claim 6: Capacity-based selection with CEL can produce a Pending Pod when no device meets the threshold
- **Evidence**: Scenario III demonstrates scaling to 2 replicas when requesting GPUs with >20GiB memory; the second Pod becomes Pending with scheduler event "0/4 nodes are available: ... 3 cannot allocate all claims."
- **Confidence**: settled
- **Quote**: "After scaling, check whether a new Pod was added: ... NAME gt20g-deploy-5ff576476-vjss8 0/1 Pending 0 26s. Run describe on the gt20g-deploy-5ff576476-vjss8 Pod: ... Warning  FailedScheduling  98s   default-scheduler  0/4 nodes are available: 1 node(s) had untolerated taint(s), 3 cannot allocate all claims. still not schedulable, preemption: 0/4 nodes are available: 4 Preemption is not helpful for scheduling."
- **Our assessment**: Concrete example showing how capacity constraints translate to FailedScheduling/claims allocation failures. This is operationally relevant to capacity planning for inference workloads with specific memory requirements.

### Claim 7: firstAvailable with ranked selectors enables fallback behavior (e.g., A5000 preferred, fall back to T10)
- **Evidence**: Scenario II shows the first Pod gets A5000, second Pod (when A5000 taken) falls back to T10.
- **Confidence**: settled
- **Quote**: "The first Pod has taken the only A5000, so the second Pod falls back to T10 — exactly the expected behavior of firstAvailable when the top choice is unavailable."
- **Our assessment**: Demonstrates DRA's expressive device selection allowing graceful degradation across heterogeneous GPU types without hardcoding node selectors.

### Claim 8: Multiple containers in the same Pod can share a single allocated GPU device
- **Evidence**: Scenario I shows two containers both referencing the same ResourceClaim and both seeing the same GPU UUID via nvidia-smi.
- **Confidence**: settled
- **Quote**: "In practice, it might not be a T10 — it could just as easily be an A5000. ... [pod/must-nvidia-gpu-pod/ctr0] GPU 0: Tesla T10 (UUID: GPU-dae084a2-974c-00e2-6dec-4ba1999b8652) [pod/must-nvidia-gpu-pod/ctr1] GPU 0: Tesla T10 (UUID: GPU-dae084a2-974c-00e2-6dec-4ba1999b8652)"
- **Our assessment**: Confirms sharing semantics at the device level for containers within a Pod when backed by a single ResourceClaim.

### Claim 9: GPU time-slicing is supported via DRA with GpuConfig sharing strategy (TimeSlicing)
- **Evidence**: Scenario IV demonstrates configuring time-slicing via opaque parameters with apiVersion resource.nvidia.com/v1beta1, kind GpuConfig, sharing.strategy: TimeSlicing, and shows 4 Pods sharing the same ResourceClaim allocated to a single GPU.
- **Confidence**: emerging
- **Quote**: "Specify the device under .spec.devices.config and switch the sharing strategy to TimeSlicing. ... 'sharing': {'strategy': 'TimeSlicing', 'timeSlicingConfig': {'interval': 'Long'}} ... Since all 4 Pods share the same ResourceClaim, kubectl get resourceclaim returns only a single entry — which itself is evidence that they’re sharing."
- **Our assessment**: Demonstrates DRA-based time-slicing configuration. The author explicitly flags this as adapted from source (not documented in official NVIDIA docs as of June 2026) and notes it may change in future releases, hence emerging confidence.

### Claim 10: Cluster Autoscaler may extend to GPU node provisioning in the future
- **Evidence**: Summary section anticipates future integration.
- **Confidence**: speculative
- **Quote**: "Previously, when a K8s cluster ran low on CPU or memory, Cluster Autoscaler could spin up new machines. In the future, the same may apply to GPU shortages — Cluster Autoscaler may provision GPU nodes on demand, enabling more efficient resource allocation."
- **Our assessment**: Forward-looking speculation, not demonstrated in the lab. Marked as speculative per triage guidance.

## Concrete Artifacts

The post provides concrete, reproducible artifacts:

- **Lab environment**: K8s v1.35.3, Containerd 2.2.2, NVIDIA GPU Operator v26.3.1, NVIDIA DRA Driver GPU v25.12.0; node topology (control plane + 3 workers with no GPU, 2× Tesla T10, 1× RTX A5000).
- **Installation examples**: Helm commands and values files for GPU Operator (with note about CONTAINERD_SOCKET for non-standard paths) and DRA Driver GPU (including optional TimeSlicingSettings feature gate).
- **ResourceSlice YAML excerpt**: Shows device attributes (architecture, productName, CUDA compute capability/driver version, PCI bus ID, UUID, memory capacity), pool metadata (generation, resourceSliceCount), ownerReferences to Node.
- **Scenario I (sharing)**: `lab01-rc.yaml` (ResourceClaim requesting 1 GPU), `lab01-pod.yaml` (two containers sharing the claim) with observed outputs showing same GPU UUID.
- **Scenario II (firstAvailable fallback)**: `lab02.yaml` with ResourceClaimTemplate using ranked selectors by productName (`NVIDIA RTX A5000` preferred, `Tesla T10` fallback), Deployment (replicas=1 then scaled to 2), observed logs showing fallback, and ResourceClaim names.
- **Scenario III (capacity filter)**: `lab03.yaml` using CEL `device.capacity["gpu.nvidia.com"].memory.isGreaterThan(quantity("20Gi"))`, with FailedScheduling event when no device meets threshold.
- **Scenario IV (time-slicing)**: `lab04.yaml` with GpuConfig sharing strategy TimeSlicing (Long interval), 4 replicas sharing single ResourceClaim, and `kubectl describe resourceclaim` showing all 4 pods under Reserved For.

## Cross-References

- **Corroborates**: None identified on the DRA/device-allocation axis proper (this is the first source covering DRA device selection and claim mechanics).
- **Contradicts**: None identified.
- **Extends**:
  - `source-notes/docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` — **Claim 3**: "Standard Google infrastructure did not measure accelerators — dashboards showed CPU/memory but \"nothing for how much GPU you were using\" — so Damion had to build accelerator monitoring \"from the ground up\"". That note documents the accelerator-observability *gap*: general infra dashboards omitted GPU/TPU utilization, so Damion pulled the stats himself and built bespoke monitoring. This note's **Claim 2** (device health reporting arriving in v1.36, so Pods no longer simply show `Error` and failure can be attributed to device vs. application) is the platform-level counterpart on the same axis — a device-health signal the Kubernetes/DRA stack now surfaces natively. Damion's note is the historical gap and the hand-rolled workaround; this note is a newer, platform-provided slice of the same signal. Cited for the accelerator-observability/fault-attribution axis only (that note does not cover DRA mechanics).
- **Relates**:
  - `source-notes/docs-google-sre-address-cascading-failures.md` — **Claim 1** and **Claim 2** (both in their `Our assessment` fields) map that chapter's general resource-exhaustion taxonomy onto LLM/GPU serving: Claim 1 — "if one GPU node exhausts memory (OOM) and requests are retried onto other nodes, their cumulative KV-cache pressure can trigger a cascade of OOM failures"; Claim 2 — "memory (KV-cache) and compute (GPU utilization)" as "the primary exhaustion modes". This note's **Claim 6** is the same capacity-pressure mechanism observed one layer earlier: a memory-threshold selector (`>20Gi`) that no free device satisfies produces `FailedScheduling: cannot allocate all claims`, not an application error. Relation: GPU memory exhaustion as a capacity-pressure mechanism — the cascading-failures note treats it as a runtime cascade trigger; this note shows the scheduling-side precondition (capacity-demand mismatch surfacing as unschedulable claims). Not a corroboration of DRA mechanics (that note predates DRA).
- **Novel**: Introduces DRA operational semantics for GPU allocation (claim lifecycle during rolling updates causing fallback to persist, capacity-based CEL selection producing claims-allocation FailedScheduling, ResourceSlice limits 128/64, device health reporting arriving in v1.36) to the corpus.

### Candidates from miner-related-notes.md
- `source-notes/docs-google-sre-prodcast-03-11-embracing-complexity.md` (score 0.2174): Dismissed — sociotechnical complexity/mental models; no GPU scheduling/DRA content. No direct relevance to extracted claims.
- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` (0.2174): Dismissed — SLOs in retail/gaming; no GPU/DRA.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` (0.1957): Dismissed — imperative vs declarative config; while DRA is declarative API surface, the topic focus differs (state reconciliation model vs device allocation semantics). Not directly corroborating the operational failure modes extracted.
- `source-notes/docs-google-sre-eliminating-toil.md` (0.1739): Dismissed — toil management; no GPU/DRA.
- `source-notes/docs-google-sre-reliable-data-processing-minimal-toil.md` (0.1522): Dismissed — batch jobs; no GPU/DRA.
- `source-notes/docs-google-sre-reliable-product-launches.md` (0.1522): Dismissed — launch process; no GPU/DRA.
- `source-notes/docs-google-sre-on-call.md` (0.1522): Dismissed — on-call; no GPU/DRA.
- `source-notes/docs-google-sre-prodcast-03-06-incident-response-tooling.md` (0.1522): Dismissed — incident response tooling; device health reporting (Claim 2) relates tangentially to observability/fault attribution, but the note content is tooling-focused (chat/paging/OTel etc.) not GPU/DRA.
- `source-notes/docs-google-sre-prodcast-03-01.md` (0.1522): Dismissed — SRE methodology; no GPU/DRA.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` (0.1522): Dismissed — LiteLLM advisor orchestration; no GPU/DRA.

No existing notes cover DRA or device-allocation mechanics. The two notes cited under `Extends`/`Relates` above overlap only on *adjacent* axes (accelerator observability; GPU capacity pressure) and were found by searching `source-notes/` directly — they were not among the candidates supplied for this run. No contradictions found.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add content addressing supply-side capacity for GPU-backed inference. Currently guide/05-llm-ops-reliability.md:1120 covers gateway capacity planning for agent-session traffic; this source introduces DRA semantics relevant to GPU substrate: (1) rolling update claim-release behavior causing preferred-device fallback to persist (operational gotcha when tuning rollout strategy/maxUnavailable/maxSurge and when expecting sticky device placement), (2) capacity-based selection producing `FailedScheduling: cannot allocate all claims` when requests exceed available device memory/capacity (distinct from application startup errors), (3) fallback via ranked `firstAvailable` selectors as a pattern for graceful degradation across heterogeneous accelerators. Recommend adding a subsection on "GPU/accelerator allocation with DRA" covering claim lifecycle and scheduling failure modes.
- **Chapter 02 (Observability)**: Device health reporting in v1.36 (Claim 2) enables distinguishing device faults from application faults. Recommend updating observability guidance to note DRA device health signals where relevant for incident triage (correlating scheduler events/claims allocation with device health).

## Extraction Notes

- Deep-read of full article including all four scenarios, YAML examples, ResourceSlice dump excerpt, and summary. Followed the code/YAML artifacts verbatim as presented.
- Extracted operational failure modes (rolling update claim retention, capacity threshold causing Pending/FailedScheduling) as primary value per triage guidance; treated tutorial mechanics as supporting evidence.
- Version claims (GA in v1.35, device health in v1.36, ResourceSlice 128/64 limit) pinned explicitly but graded `emerging`: their sole evidence is a single lab-scale blog post, so they are unverifiable within the corpus and should be checked against Kubernetes release notes / the DRA API docs before the guide relies on them. Time-slicing marked emerging due to author noting undocumented state as of June 2026 and potential future changes.
- `confidence_overall` is `emerging`, consistent with the per-claim grades after the version-status downgrade (5 settled, 4 emerging, 1 speculative): the operational failure modes are settled as accounts of what the tutorial demonstrates, but the version-status and forward-looking claims are not, and the whole source is lab-scale (3 workers) with no production metrics.
- Cross-references were expanded on Assayer review: `docs-google-sre-prodcast-05-08-damion-yates-ai-systems` (Claim 3, accelerator-observability gap) and `docs-google-sre-address-cascading-failures` (Claims 1/2 `Our assessment`, GPU-memory capacity pressure) were missed in the first pass because the cross-reference axis had been read too narrowly as "DRA/GPU scheduling". Both cited notes and their claim numbers were re-read and verified before citation (MINER.md §4b).
- Autoscaler speculation marked speculative. Lab scale caveat noted (3 workers, specific GPU mix) — evidence is tutorial/lab-level, not production-scale.
- No paywall; fully readable.
