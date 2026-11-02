---
source_url: https://www.cncf.io/blog/2026/08/07/does-kubernetes-dra-replace-hami
source_type: blog-post
title: "Does Kubernetes DRA Replace HAMi?"
author: "Mesut Oezdil (HAMi contributor; CNCF TAG Infrastructure Tech Lead)"
date_published: 2026-08-07
date_extracted: 2026-11-01
last_checked: 2026-11-01
status: current
confidence_overall: emerging
issue: "#1981"
---

# Does Kubernetes DRA Replace HAMi?

> A HAMi-contributor analysis separating what DRA absorbs (fractional-GPU request
> encoding and scheduler-side capacity bookkeeping) from what it does not
> (runtime enforcement inside the container), with the HAMi-DRA migration
> architecture, version/feature-gate adoption gates, and two concrete operational
> hazards: mixed DRA/device-plugin mode and topology-blind placement.

## Source Context

- **Type**: blog-post (CNCF Project Maintainer Post; CNCF highlights HAMi, Helm, Kubernetes, and Linkerd)
- **Author credibility**: Mesut Oezdil is a DevOps engineer, CNCF TAG Infrastructure Tech Lead, and a HAMi contributor. He writes from the project's perspective and the post is partly a positioning piece for HAMi's 2026 DRA roadmap. The API/version/feature-gate facts and the YAML are checkable; the migration advice and HAMi-favourable comparisons are author framing.
- **Scope**: Covers why HAMi's traditional fractional-GPU pipeline existed (webhook + scheduler extender + annotation + in-container enforcement), what core DRA and consumable capacity replace, what remains enforcement, the three HAMi-DRA repositories, the Helm install path, prerequisites/feature-gate gates, a legacy-vs-native YAML comparison, a feature table, and a mid-2026 decision tree. Does NOT provide production metrics, incident data, or an independent benchmark; the "10,000+ GPUs at DaoCloud", "16 releases", and "3x utilization gains" figures are restated project claims, not measured here.

## Extracted Claims

### Claim 1: Core DRA graduated to GA in Kubernetes v1.34 and is locked on since v1.35; extensions graduate on their own schedule (prioritized device lists stable v1.36; consumable capacity and partitionable devices beta v1.36)
- **Evidence**: The post's timeline paragraph cites the Kubernetes DRA documentation and the feature-gates reference. Verified against primary sources: the official Kubernetes blog is titled "Kubernetes v1.34: DRA has graduated to GA" and states "The headline feature of the v1.34 release is that the core of DRA has graduated to General Availability"; the official feature-gates table lists `DynamicResourceAllocation` as Stable since 1.34 (locked on from 1.35), `DRAConsumableCapacity` Alpha 1.34–1.35 / Beta 1.36–, `DRAPrioritizedList` Stable 1.36, and `DRAPartitionableDevices` Beta 1.36–.
- **Confidence**: settled (primary release notes + feature-gates table)
- **Quote**: "Core DRA went GA in Kubernetes v1.34 and is locked on since v1.35."
- **Our assessment**: Buy the v1.34 GA boundary — it is confirmed by the official v1.34 release blog and the feature-gates table, not just this post. Two nuances the guide should state precisely: (a) the post's earlier sentence "enabled by default since v1.35" is imprecise; the v1.34 release blog says DRA is enabled by default starting in v1.34, and v1.35 is the lock-on release; (b) "consumable capacity" is **not** part of core GA — it was alpha behind `DRAConsumableCapacity` in v1.34–v1.35 and beta/default-on only in v1.36. This resolves the open verification item in `blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` Claim 1 (which says GA in v1.35); contradiction filed as #1991.

### Claim 2: DRA (including consumable capacity) is only a scheduling-time promise tracker — it prevents over-commitment but does nothing about a container that exceeds its grant at runtime
- **Evidence**: The article's central architectural distinction, argued from what the scheduler books versus what CUDA does at call time. The named failure mode is one greedy `cudaMalloc()` loop consuming VRAM a neighbour was promised.
- **Confidence**: settled (scope boundary of the API/scheduler mechanism)
- **Quote**: "DRA, consumable capacity included, is a promise tracker. It guarantees the scheduler never promises more than a device has. It does nothing about a container that breaks the promise at runtime, and with GPUs that’s the failure mode that actually hurts: CUDA doesn’t care what a `ResourceClaim` says, and one greedy `cudaMalloc()` loop will happily take VRAM a neighbor was counting on."
- **Our assessment**: Buy this as the load-bearing claim of the source. Scheduler bookkeeping is admission-time accounting; it is not a cgroup-like runtime quota for device memory. The guide currently has no statement of this accounting-vs-enforcement split, and any DRA recommendation that omits it will over-promise isolation.

### Claim 3: HAMi-core enforces the granted limits at CUDA/NVML call granularity via `libvgpu.so` preloaded into the container, so an over-allocating pod hits OOM at its own boundary while its neighbour is unaffected
- **Evidence**: The author describes HAMi-core as a C library that interposes CUDA and NVML calls and applies the granted limits from user space, and describes a reproducible test: two pods with 8,000 MiB grants, one deliberately allocates past its limit.
- **Confidence**: emerging (project-described behaviour; no transcript or benchmark shown)
- **Quote**: "Enforcement is HAMi’s second job, and it lives in HAMi-core, a C library (`libvgpu.so`) preloaded into the container that intercepts CUDA and NVIDIA Management Library (NVML) calls and applies the granted limits from user space."
- **Our assessment**: The mechanism is plausible and matches HAMi's documented design (library interposition plus `CUDA_DEVICE_MEMORY_LIMIT_0` / `CUDA_DEVICE_SM_LIMIT`). Treat the precise OOM-at-boundary behaviour as project-described rather than independently measured here. The transferable point is that enforcement is a separate userspace layer, not a DRA feature.

### Claim 4: Library-interposition enforcement is escapable — statically linked workloads, `CUDA_DISABLE_CONTROL`, and containers-in-containers bypass it — so it is unsuitable as an adversarial multi-tenant boundary
- **Evidence**: The author's explicit "ceiling" paragraph, naming three bypass surfaces.
- **Confidence**: settled (limitation of the mechanism); anecdotal (real-world prevalence)
- **Quote**: "I’ll be equally honest about the ceiling: this is software enforcement via library interposition. A workload that bypasses the preload (static linking against the driver, `CUDA_DISABLE_CONTROL`, containers-in-containers) escapes it."
- **Our assessment**: Buy the bypass list as a trust-boundary rule. The critical operational implication is that the tenant controls the container spec that supplies `LD_PRELOAD` and `CUDA_DISABLE_CONTROL`; interposition therefore assumes cooperative tenants. For adversarial multi-tenancy, use hardware partitioning (MIG) rather than treating interposition as a security control.

### Claim 5: Interposition trades isolation for granularity — 1 MiB memory and 1% compute steps versus MIG's fixed profiles — and is the better fit for cooperative teams sharing expensive cards
- **Evidence**: The author's comparison of interposition granularity with NVIDIA MIG profiles; no benchmark or measured isolation/performance data.
- **Confidence**: emerging (feature comparison; recommendation is author framing)
- **Quote**: "for cooperative teams sharing expensive cards, interception is the granularity winner: 1 MiB memory steps and 1% compute steps against MIG’s fixed profiles."
- **Our assessment**: The granularity mechanism is plausible — a software quota can be finer-grained than a fixed MIG profile. "Winner" is the author's framing and ignores what MIG buys: hardware-enforced isolation, predictable performance, and fault containment. Carry the trade-off ("fine-grained cooperative sharing vs coarse hardware isolation"), not the verdict.

### Claim 6: DRA mode and traditional device-plugin mode must never run in the same cluster simultaneously, because two independent bookkeepers would each believe they own the same VRAM
- **Evidence**: HAMi's DRA documentation states the constraint flatly; the author supplies the failure mechanism: the scheduler extender and the DRA scheduler each account for the same device without seeing the other's promises.
- **Confidence**: settled (documented project constraint; mechanism is coherent)
- **Quote**: "DRA mode and traditional device-plugin mode must not run in the same cluster simultaneously."
- **Quote**: "two bookkeepers, the scheduler extender and the DRA scheduler, would each believe they own the same VRAM, and neither sees the other’s promises. Pick one mode per cluster."
- **Our assessment**: Buy as a hard operational guardrail. This is a concrete misconfiguration → silent double-allocation failure mode: each scheduler believes capacity is free, so both can grant the same VRAM. The guide should make this an explicit migration/upgrade check rather than a footnote.

### Claim 7: HAMi-DRA's mutating webhook rewrites legacy `nvidia.com/gpu|gpumem|gpucores` extended resources into native `ResourceClaim`s at admission, so existing manifests need no change and third-party schedulers need no HAMi-specific integration
- **Evidence**: The article describes the webhook, names the configurable chart values (`resourceName`, `resourceMem`, `resourceCores`), and shows the legacy and native YAML side by side. It contrasts this with the traditional pipeline, which had to inject a scheduler extender.
- **Confidence**: emerging (project-described architecture; no independent deployment shown)
- **Quote**: "It’s a mutating admission webhook that strips the classic extended resources out of incoming pods and generates the equivalent `ResourceClaims` on the fly, preserving the familiar UUID and device-type annotations for targeting."
- **Our assessment**: Buy the compatibility mechanism and its decoupling payoff: because the request becomes a standard object, Volcano/KAI/other DRA-aware schedulers need no vendor patch. Important caveat: the shim preserves the *syntax*, not the old *semantics* — the resulting scheduling is done by the upstream scheduler, which is topology-blind (Claim 8).

### Claim 8: Delegating placement to upstream kube-scheduler is topology-blind — HAMi-DRA ships no scheduler, so it cannot prefer NVLink-connected GPU pairs and hands the scheduler "a count and a capacity, not a topology constraint"
- **Evidence**: The author's explicit trade-off section, using an NVLink example (GPU0 reaches GPU1/GPU2 at high bandwidth but not GPU3) where a two-GPU claim should avoid the slow path.
- **Confidence**: settled (architectural consequence of delegating scheduling)
- **Quote**: "HAMi-DRA ships no scheduler of its own, so it can’t make topology-aware placement decisions."
- **Quote**: "It hands the scheduler a count and a capacity, not a topology constraint."
- **Our assessment**: Buy this as an explicit trade, not a defect: interoperability with standard schedulers costs topology awareness. This is the same failure class as `failure-cncf-kubeflow-cilium-60-idle-gpus.md` Claim 1 — a placement-relevant constraint the scheduler cannot see — but here the invisible constraint is NVLink bandwidth rather than CNI zone boundaries. Workloads where inter-GPU bandwidth matters must stay on a topology-modelling scheduler or accept bandwidth-blind placement.

### Claim 9: DRA-mode adoption is gated by Kubernetes v1.34+ with `DRAConsumableCapacity` enabled, a CDI-capable containerd/CRI-O, NVIDIA driver 440+, and a DRA driver for the silicon; alpha/off-by-default on v1.34–v1.35 blocks managed clusters that do not expose control-plane flags, while beta/default-on in v1.36 removes the biggest blocker
- **Evidence**: The prerequisites list, cross-checked against the official feature-gates table (`DRAConsumableCapacity`: false/Alpha 1.34–1.35, true/Beta 1.36–). The CDI and driver-440 requirements are stated by the author.
- **Confidence**: settled (version/feature-gate facts verified); emerging (managed-cluster availability is provider-dependent)
- **Quote**: "On v1.34 and v1.35 the gate is alpha and off by default, so it needs to be set on the control plane, which rules out managed clusters that don’t expose API server flags. The gate graduated to beta and turned on by default in v1.36, which quietly removes the biggest adoption blocker."
- **Our assessment**: Buy the version matrix; the feature-gate half is confirmed upstream. Phrase the managed-cluster implication as conditional — "unless the provider exposes control-plane feature gates" — because some managed offerings do. The practical decision gate is v1.36 (default-on) versus self-managed v1.34/v1.35 with gate access.

### Claim 10: Under fractional allocation, in-container `nvidia-smi` reports the granted slice (e.g. 10,240 MiB), not the physical card, so card-total GPU capacity dashboards are wrong
- **Evidence**: The author's statement that HAMi-core intercepts NVML the same way in DRA mode, so the container sees the granted slice.
- **Confidence**: emerging (asserted; consistent with the interposition mechanism; no dashboard example)
- **Quote**: "Either way, `nvidia-smi` inside the running container reports 10,240 MiB, the granted slice rather than the physical card, because HAMi-core is doing the same interception it always did."
- **Our assessment**: Buy the consequence: capacity dashboards built on per-container `nvidia-smi` totals will under-count physical capacity and misattribute the slice as the card. Under fractional allocation, monitor the allocation object (`ResourceClaim` capacity requests/status) and the DRA monitor, not the container's device view. This also qualifies the "GPU utilization is the observable signal" lesson in the Cilium/Kubeflow note — the signal must come from the right layer.

### Claim 11: HAMi's observability carries over to DRA mode via a DRA monitor enabled by default, exposing per-container device metrics over Prometheus on port 31995
- **Evidence**: The author's statement about the HAMi DRA monitor component; no scrape config or metric names are given.
- **Confidence**: emerging (project-specific surface; unverified in this extraction)
- **Quote**: "the DRA monitor component is enabled by default and exposes per-container device metrics over Prometheus (port 31995), so dashboards built against HAMi’s exporters survive the switch."
- **Our assessment**: Record the continuity claim, but do not generalize port 31995 as a Kubernetes/DRA convention — it is HAMi's exporter. The durable principle is that the monitor reads the allocation layer, which is why the dashboards survive the request-language change.

### Claim 12: HAMi's traditional pipeline existed because the device-plugin API could only count opaque integers; it used a mutating webhook, a scheduler extender, an annotation, and in-container enforcement, and DRA absorbs the encoding half while leaving enforcement unchanged
- **Evidence**: The historical walkthrough, including the annotation format and the explanation that extended resources are opaque to the default scheduler.
- **Confidence**: settled (architecture description)
- **Quote**: "So HAMi routes the pod through a mutating webhook to its own scheduler extender, which filters nodes, scores cards, picks a specific device UUID, and records the decision where the API has room for it: an annotation."
- **Our assessment**: Useful causal history: the webhook existed because the scheduler could not parse the request; the annotation existed because the API had no field for "which card and how much". The "workaround" framing is the author's, but the structural account is accurate and explains why DRA is convergence rather than a competing feature.

### Claim 13: Mid-2026 decision tree — managed Kubernetes without feature-gate access on v1.34/v1.35 (or older) and mixed-vendor fleets stay on traditional mode; NVIDIA clusters on v1.34+ with control-plane access, and anyone on v1.36, should stand up DRA mode in staging first
- **Evidence**: The author's explicit recommendation section, conditioned on version, control-plane access, and vendor coverage.
- **Confidence**: emerging (recommendation; vendor-adjacent author)
- **Quote**: "Managed Kubernetes without feature-gate access on v1.34 or v1.35, or anything older: traditional mode, no hesitation."
- **Our assessment**: The decision tree is a reasonable conditional synthesis and its gates match the verified version matrix. Treat it as author perspective, not independent evaluation, and do not import the restated production-mileage figures ("16 releases", "10,000+ GPUs", "3x utilization gains") as evidence — they are uncited secondhand claims in this source.

### Claim 14: Core DRA's baseline sharing model is multiple pods referencing one `ResourceClaim` (a shared allocation), not independently accounted slices; consumable capacity adds `allowMultipleAllocations` plus capacity requests to get per-claim accounting
- **Evidence**: The author's explanation of the consumable-capacity feature: a driver marks a device with `allowMultipleAllocations`, and a claim requests a quantity of a named resource instead of the whole device.
- **Confidence**: settled (API semantics; consistent with the existing DRA note)
- **Quote**: "Core DRA alone doesn’t give you HAMi-style sharing. Its baseline sharing model is multiple pods referencing one `ResourceClaim`, which means they share the same allocation rather than each getting an accounted slice."
- **Our assessment**: Buy; this is the distinction readers most often miss. "Pods share a claim" is not "pods each get a quota". Per-claim accounting (the thing HAMi-style sharing needs) is the consumable-capacity extension, which is beta in v1.36 — not core GA DRA.

## Concrete Artifacts

**Legacy HAMi extended-resource request** (source: article, "How GPU sharing worked when the API couldn't help"; auto-link markup removed from the rendered page):

```yaml
resources:
  limits:
    nvidia.com/gpu: 1        # device IDs from 1 physical card
    nvidia.com/gpumem: 8000  # MiB of that card's VRAM
    nvidia.com/gpucores: 10  # 10% of compute, in 1% steps
```

**HAMi allocation annotation** (source: article, same section):

```text
hami.io/vgpu-devices-allocated: GPU-<device-uuid>,NVIDIA,8000,10:
```

**Native DRA `ResourceClaim` for the same slice** (source: article, "The same GPU slice, old way and new"):

```yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaim
metadata:
  name: gpu-half-claim
spec:
  devices:
    requests:
      - name: gpu
        exactly:
          deviceClassName: hami-core-gpu.project-hami.io
          allocationMode: ExactCount
          count: 1
          capacity:
            requests:
              cores: 50
              memory: "10Gi"
```

**Pod referencing the claim** (source: article, same section):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-test-dra-native
spec:
  containers:
    - name: cuda
      image: nvidia/cuda:13.0.1-base-ubi9
      command: ["sleep", "3600"]
      resources:
        claims:
          - name: gpu
  resourceClaims:
    - name: gpu
      resourceClaimName: gpu-half-claim
  restartPolicy: Never
```

**Helm install sequence** (source: article, "The DRA stack HAMi ships today"):

```bash
helm repo add hami-dra https://project-hami.github.io/HAMi-DRA
helm repo update
helm install hami-dra hami-dra/hami-dra
# add --set drivers.nvidia.containerDriver=false if the NVIDIA driver
# is installed on the host rather than through GPU Operator
```

The article adds: if the GPU Operator manages drivers, install it with `devicePlugin.enabled=false` first, because the DRA stack replaces the device plugin's job. After the release settles, expect three pods (kubelet plugin, webhook, monitor); `kubectl get resourceslice` confirms published capacity and `kubectl get resourceclaim` shows the allocation.

**Feature comparison table** (source: article, "The same GPU slice, old way and new"):

| Feature | Device plugin mode | DRA mode |
|---|---|---|
| Request language | Extended resources, opaque integers | ResourceClaim capacity requests, typed API |
| Scheduling decision | HAMi scheduler extender | Default kube-scheduler |
| Allocation record | Annotation string only HAMi reads | ResourceClaim status, kubectl and RBAC visible |
| Admission webhook | Required, routes pod to extender | Optional, HAMi-DRA translates legacy YAML |
| Kubernetes version | Any supported release | v1.34+ with feature gate; default-on since v1.36 |
| Runtime prerequisites | Standard container runtime | CDI-capable containerd or CRI-O, NVIDIA driver 440+ |
| Vendor coverage | 12+ device families | NVIDIA mature; Ascend, Enflame, Hygon DCU arriving |
| Enforcement | HAMi-core (`libvgpu.so`) | Same HAMi-core, unchanged |
| Observability | HAMi exporters | DRA monitor, Prometheus port 31995 |
| Production mileage | 16 releases, 10,000+ GPUs at DaoCloud | HAMi-DRA v0.2.1, production-ready since v2.9 |
| Coexistence | Never both modes in the same cluster | Same constraint |

## Cross-References

- **Corroborates**:
  - `source-notes/blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` **Claim 4** (DRA is modelled on Storage — DeviceClass ≈ StorageClass, ResourceClaim ≈ PVC). This note's Claim 12/14 uses the same framing to explain why the request became a first-class object. Both describe the same API lineage; this note adds the scheduler-enforcement split that the tutorial note does not cover.
  - `source-notes/blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` **Claim 8** (multiple containers in the same Pod can share one allocated GPU). This note's Claim 14 generalises the sharing semantics: baseline DRA sharing is multiple consumers referencing one `ResourceClaim` (shared allocation, not an accounted slice). Within-Pod vs cross-Pod is a scope difference, not a disagreement.
  - `source-notes/blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` **Claim 9** (GPU time-slicing via DRA `GpuConfig` sharing strategy). That note covers time-slicing as one sharing mechanism; this note adds consumable-capacity *accounted* slices as a different mechanism. The two are complementary: time-slicing shares a device over time, consumable capacity divides it into capacity requests.
- **Contradicts**:
  - `source-notes/blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` **Claim 1** (asserts "DRA recently reached GA in Kubernetes v1.35"). This source says GA was v1.34 and v1.35 is the lock-on release; the official Kubernetes v1.34 release blog and feature-gates table confirm v1.34. **Contradiction issue: #1991** (filed before this PR per MINER.md §4a). No verdict is asserted here; the resolver decides. This note's Claim 1 carries the primary-source evidence.
- **Extends**:
  - `source-notes/failure-cncf-kubeflow-cilium-60-idle-gpus.md` **Claim 1** (a topology-aware control — CiliumNetworkPolicy zone boundaries — is invisible to the topology-agnostic Kubernetes scheduler, producing a silent collective failure). This note's Claim 8 is the same failure class on the accelerator-interconnect axis: HAMi-DRA cannot express an NVLink topology constraint, so a multi-GPU claim can be placed across a slow path with no error. The Cilium note's fix is to give the scheduler the missing constraint; this note shows a case where the chosen architecture (delegate to upstream kube-scheduler) cannot express it at all.
  - `source-notes/failure-cncf-kubeflow-cilium-60-idle-gpus.md` **Claim 4** ("GPU utilization drop is the observable signal") and **Claim 6** ("Instrumentation is essential for detection"). This note's Claim 10 qualifies the signal source: under fractional allocation, in-container `nvidia-smi` reports the granted slice, so a dashboard built on card totals is wrong. The Cilium note's detection lesson still holds, but the metric must be sourced from the allocation layer / DRA monitor rather than the container's device view.
  - `source-notes/blog-cncf-netease-games-llm-cold-starts-kubernetes.md` **Claim 3** (GPU resources were "scarce and heterogeneous", and keeping enough capacity online for every team's peak was inefficient). This note supplies the allocation-layer alternative to over-provisioning whole cards: consumable capacity lets independent claims share one physical device with accounted slices, while the cold-start note addresses the data-path side of the same capacity-efficiency problem.
- **Relates**:
  - `source-notes/blog-cncf-gpu-autoscaling-keda-external-scaler.md` **Claim 1** (the default autoscaling path reasons about CPU/memory while the GPU doing the work is invisible, wasting accelerator capacity). This note is the allocation-layer counterpart: DRA makes the request/allocation a typed object, but it does not by itself give an autoscaler a scaling signal. The KEDA note's metric problem and this note's allocation-accounting problem are adjacent, not substitutes.
- **Novel**: First source in the corpus to cover (a) fractional-GPU sharing with accounted, consumable-capacity slices; (b) the DRA promise-tracker vs runtime-enforcement split; (c) HAMi-core interposition and its bypass ceiling; (d) the DRA/device-plugin coexistence hazard; (e) HAMi-DRA's admission-webhook rewrite and topology-blindness trade-off; (f) the consumable-capacity feature-gate/version matrix and the corrected v1.34 GA boundary.

### Candidates from miner-related-notes.md

The supplied lexical candidates were all off-topic for this source; each is dismissed explicitly below. The useful cross-references came from the Prospector's overlap list and a direct search of `source-notes/`.

- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — Dismissed: retail/gaming SLOs; no GPU, DRA, or scheduling content.
- `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` — Dismissed: agentic-AI security platform; no accelerator allocation or enforcement.
- `source-notes/docs-google-sre-eliminating-toil.md` — Dismissed: toil taxonomy; no GPU/DRA.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` — Dismissed: imperative vs declarative change workflows; DRA is a declarative API, but the note is about reconciliation models, not device allocation.
- `source-notes/docs-google-sre-reliable-product-launches.md` — Dismissed: launch process; no GPU/DRA.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — Dismissed: LiteLLM advisor orchestration; no GPU/DRA.
- `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — Dismissed: promptfoo agent evaluation; no GPU/DRA.
- `source-notes/docs-litellm-batches-api.md` — Dismissed: LiteLLM batch rate limiting; no GPU/DRA.
- `source-notes/docs-google-sre-on-call.md` — Dismissed: on-call policy; no GPU/DRA.
- `source-notes/docs-google-sre-prodcast-03-01.md` — Dismissed: SRE methodology; no GPU/DRA.
- `source-notes/blog-cncf-running-self-hosted-llm-kubernetes-vllm.md` — Dismissed (from the Prospector's overlap list): a whole-card vLLM deployment walkthrough; it assumes one card per workload and makes no fractional-allocation, consumable-capacity, or enforcement claim. Adjacent substrate only.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add a subsection on GPU/accelerator fractional sharing and the **accounting-vs-enforcement split**. Specific recommendation: if the guide recommends DRA or consumable capacity for shared GPUs, state that it is scheduler-side bookkeeping only and pair it with a runtime enforcement layer (HAMi-core interposition for cooperative tenants, MIG for adversarial tenants). Add the adoption gate table: core DRA GA v1.34 / locked on v1.35; `DRAConsumableCapacity` alpha/off v1.34–v1.35, beta/default-on v1.36; prioritized device lists stable v1.36; CDI-capable containerd/CRI-O and NVIDIA driver 440+. Add the topology trade-off: delegating to upstream kube-scheduler buys interoperability but loses NVLink-aware placement, so bandwidth-sensitive multi-GPU workloads need a topology-modelling scheduler.
- **Chapter 02 (Observability)**: Under fractional GPU allocation, in-container `nvidia-smi` reports the granted slice, not the physical card. Recommend that GPU-capacity dashboards read `ResourceClaim` capacity requests/status and the DRA monitor (HAMi's exporter on port 31995) rather than per-container card totals, and that `kubectl get resourceclaim` / ResourceSlice be treated as an allocation-observability surface.
- **Chapter 03 (Runbooks and Agents)**: Add two operational guards: (1) never run DRA mode and traditional device-plugin mode in the same cluster — two bookkeepers can double-allocate the same VRAM; (2) a DRA migration checklist that verifies v1.34+ with control-plane gate access (or v1.36 default-on), CDI runtime, driver 440+, and GPU Operator installed with `devicePlugin.enabled=false`.
- **Chapter 06 (Security and Trust)**: Add the isolation-boundary doctrine for shared accelerators: software interposition is escapable (static linking, `CUDA_DISABLE_CONTROL`, containers-in-containers) and therefore assumes cooperative tenants; use MIG for adversarial multi-tenancy. Do not present `LD_PRELOAD` enforcement as a security boundary.

## Extraction Notes

- Deep-read the full article, including both YAML sections, the feature table, the prerequisites list, the coexistence note, the topology trade-off, and the decision tree. Followed the article's links to the primary Kubernetes release blog and the feature-gates reference to verify the version claims rather than taking them on faith.
- Version verification results: `DynamicResourceAllocation` is Stable since v1.34 (locked on v1.35); `DRAConsumableCapacity` is false/Alpha v1.34–v1.35 and true/Beta v1.36–; `DRAPrioritizedList` is Stable v1.36; `DRAPartitionableDevices` is Beta v1.36–. The post's "GA v1.34" and "beta v1.36" claims are correct; its "enabled by default since v1.35" sentence is imprecise (the v1.34 release blog says default-on starting v1.34). The GA-version conflict with the existing DRA note was filed as contradiction **#1991** before this PR, and no verdict is asserted in the note.
- Bias handling: the author is a HAMi contributor and the post is partly a HAMi positioning piece. The API/version/YAML/bypass-list facts are graded on their own evidence; the migration recommendations, "granularity winner", and production-mileage figures ("16 releases", "10,000+ GPUs at DaoCloud", "3x utilization gains") are marked as author framing and are not carried into the guide as independent evidence. No production metrics or incident data are provided.
- Cross-references were verified by re-reading each cited note and checking the claim number in document order (MINER.md §4b). Claim 1/4/8/9 of the existing DRA note and Claims 1/4/6 of the Cilium/Kubeflow note were checked against their `### Claim:` headings; Claim 3 of the NetEase note and Claim 1 of the KEDA note were checked likewise. No quote from another note is presented as a source quote.
- The `miner-related-notes.md` lexical candidates were all off-topic; each is explicitly dismissed under Cross-References. The useful overlaps were found via the Prospector's triage list and a direct `source-notes/` search.
- No paywall; the source was fully readable. The CNCF page's auto-link rendering of `nvidia.com/gpu` in code blocks was stripped from the artifact, restoring the plain YAML as shown in the article's code block.
- `confidence_overall` is `emerging`: the version/feature-gate and API-scope claims are settled and primary-verified, but the runtime-enforcement behaviour, observability surfaces, and migration guidance are project-described with no independent production evidence, and the author is vendor-adjacent.
