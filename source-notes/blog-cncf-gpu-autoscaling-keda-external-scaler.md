---
source_url: https://www.cncf.io/blog/2026/05/27/gpu-autoscaling-on-kubernetes-with-keda-building-an-external-scaler
source_type: blog-post
title: "GPU autoscaling on Kubernetes with KEDA: Building an external scaler"
author: "Pavan Madduri (Senior Cloud Platform Engineer @ Grainger | CNCF Golden Kubestronaut)"
date_published: 2026-05-27
date_extracted: 2026-10-26
last_checked: 2026-10-26
status: current
confidence_overall: emerging
issue: "#1898"
---

# GPU autoscaling on Kubernetes with KEDA: Building an external scaler

> A practitioner CNCF Community Post that explains why KEDA cannot scale on
> GPU metrics natively — KEDA core is built `CGO_ENABLED=0` while NVML needs
> CGO, and NVML reads are node-local while the KEDA operator is a single
> Deployment — and supplies the reference architecture that follows from those
> two constraints: one DaemonSet per GPU node calling go-nvml and answering
> KEDA's `ExternalScaler` gRPC interface, with pre-built workload profiles and
> a mock collector for GPU-free CI. It publishes no measurements, so the
> thresholds are defaults to tune, not validated recommendations.

## Source Context

- **Type**: blog-post (CNCF Community Post, authored by the reference
  implementation's own author). CNCF highlights KEDA and Kubernetes.
- **Author credibility**: Pavan Madduri is a Senior Cloud Platform Engineer at
  Grainger and a CNCF Golden Kubestronaut. He wrote the `keda-gpu-scaler`
  reference implementation the post announces, so he understands the
  `ExternalScaler` mechanics he describes — and is also advocating his own
  artifact. The post is technical rather than marketing, but it is a
  reference-implementation announcement, not an independent evaluation.
- **Scope**: Covers the two structural reasons a native KEDA GPU scaler does
  not exist, the per-node DaemonSet + gRPC `ExternalScaler` architecture, the
  five exposed GPU metrics and their aggregation modes, four workload
  profiles, Helm installation with NVIDIA node targeting and a host-mount
  fallback, a `ScaledObject` example, and a mock-collector e2e test setup.
  Does NOT include throughput, latency, cost, energy, or scaling-time
  measurements; no production case study; no guidance on node-level (cluster)
  autoscaling, multi-tenant GPU sharing, or failure modes after a scaler pod
  dies. The GreenOps/emissions motivation is asserted, not quantified.

## Extracted Claims

### Claim 1: The default Kubernetes autoscaling path reasons about CPU and memory while the GPU actually doing the work stays invisible, which wastes accelerator capacity, raises inference latency, and adds unnecessary power draw
- **Evidence**: The author's problem framing, stated as the motivation for the whole project; no measurements are supplied.
- **Confidence**: emerging (well-known limitation; practitioner assertion here, not measured)
- **Quote**: "If you run GPU workloads on Kubernetes — vLLM, Triton, training jobs, or the newer agentic inference stacks — you’ve probably hit a familiar problem: the default autoscaling path still reasons about CPU and memory, while the GPU that is actually doing the work stays hidden. That mismatch wastes expensive accelerator capacity, pushes up inference latency, and creates unnecessary power draw at exactly the point where enterprises are trying to scale LLMs and Agentic Ops responsibly."
- **Our assessment**: Buy the mechanism. CPU/memory HPA is blind to the accelerator: a vLLM pod can hold a GPU at high utilization while pod CPU sits low, and it can look "busy" on CPU while the GPU is idle. The specific consequence magnitudes (latency, power) are plausible but unmeasured here. This is the premise the rest of the post operationalizes.

### Claim 2: KEDA core is compiled with `CGO_ENABLED=0` while NVML requires CGO, so a GPU scaler cannot simply be added to KEDA core the way a Prometheus or Kafka scaler is
- **Evidence**: Stated as the first hard constraint; it is a verifiable build property of KEDA and a documented dependency of NVML.
- **Confidence**: settled (build/dependency constraint)
- **Quote**: "KEDA is built with CGO_ENABLED=0. The NVIDIA Management Library (NVML) – the standard way to read GPU metrics – requires CGO. So you can’t just add a GPU scaler to KEDA core the way you’d add a Prometheus or Kafka scaler."
- **Our assessment**: This is the transferable architectural insight and the reason the post exists. It also generalizes beyond GPUs: any metric source that needs cgo (vendor SDKs, some hardware libraries) cannot live in KEDA core and must arrive through an external scaler or an existing metrics API. Note the asymmetry: the constraint is about the *core binary*, not about KEDA's plugin surface.

### Claim 3: NVML calls are node-local, and because KEDA's operator runs as a single Deployment, a centralized operator-side scaler cannot read a GPU on another node
- **Evidence**: The second named constraint, argued from how NVML reads device metrics and how the operator is deployed.
- **Confidence**: settled (architecture constraint)
- **Quote**: "There’s a second problem too. KEDA’s operator runs as a single deployment. NVML calls are local — they read metrics from the GPU on the same node. You can’t query GPU 0 on node-A from a pod running on node-B."
- **Our assessment**: Correct and operationally decisive. Even if the CGO problem were solved, a single operator pod would only ever see the GPUs on its own node. The two constraints together force a per-node agent; either one alone would not. This is the load-bearing reasoning chain the guide should preserve rather than just the conclusion.

### Claim 4: The working architecture is a per-node DaemonSet that reads local GPU metrics via go-nvml, serves them over gRPC implementing KEDA's `ExternalScaler` interface, and lets the KEDA operator drive HPA decisions
- **Evidence**: The architecture section enumerates the three responsibilities of each pod and links the reference implementation; the `ScaledObject` example in the post shows the external trigger pointing at the DaemonSet's service.
- **Confidence**: emerging (implemented in the author's repo; not independently validated in production)
- **Quote**: "To solve this, we can build a custom DaemonSet (you can view my reference implementation here: keda-gpu-scaler) that runs on GPU nodes. In this architecture, each pod:  
1. Calls NVML via [go-nvml] to read local GPU metrics.

2. Serves them over gRPC using KEDA’s ExternalScaler interface.

3. KEDA operator connects to the scaler and drives HPA decisions."
- **Our assessment**: The shape is sound and matches how the ecosystem already solves node-local hardware exposure. The operational cost is the part the post undersells: you now own a DaemonSet on every GPU node plus a gRPC service that sits in the scaling control path, so a scaler pod that crashes or cannot be scheduled can stall scaling even while the workload is healthy. That is a new failure domain, not just a new component.

### Claim 5: The per-node agent pattern is the same one Kubernetes uses for device plugins and the metrics server
- **Evidence**: Author's analogy, not a code-level comparison.
- **Confidence**: emerging (reasonable architectural analogy; no shared implementation shown)
- **Quote**: "This is the same pattern Kubernetes uses for device plugins and the metrics server — a per-node agent that collects local hardware data."
- **Our assessment**: Useful for explaining *why* the DaemonSet shape is idiomatic rather than a workaround. The analogy is structural, not literal: device plugins use a different registration protocol and the metrics server exposes the resource metrics API, whereas this scaler speaks KEDA's `ExternalScaler` gRPC contract. Carry the "node-local data needs a node-local agent" principle; do not imply the implementations are interchangeable.

### Claim 6: The scaler exposes five per-GPU metrics, and compute utilization, memory-controller utilization, and VRAM percentage are three distinct signals
- **Evidence**: The explicit metric list and its one-line definitions.
- **Confidence**: settled (metric definitions)
- **Quote**: "The scaler exposes these metrics per GPU:

-   gpu\_utilization – SM (compute) utilization percentage
-   memory\_utilization – memory controller utilization
-   memory\_used\_percent – VRAM usage as a percentage
-   temperature – GPU die temperature in celsius
-   power\_draw – current power consumption in watts"
- **Our assessment**: The three-way distinction matters more than the list. `gpu_utilization` is SM (compute) busy-ness, `memory_utilization` is memory-controller busy-ness, and `memory_used_percent` is VRAM occupancy. On inference they diverge: a server holding weights can consume most VRAM at low SM utilization, which is exactly why the `vllm-inference` profile scales on `memory_used_percent` rather than compute. Do not treat "GPU utilization" as one number; name which of the three a policy uses.

### Claim 7: For multi-GPU nodes the operator chooses an aggregation (`max`, `min`, `avg`, `sum`) or targets a specific GPU index
- **Evidence**: One sentence in the metric section; no worked example or guidance on which aggregation fits which workload.
- **Confidence**: settled (feature statement); anecdotal (choice guidance absent)
- **Quote**: "For multi-GPU nodes, you pick an aggregation: `max`, `min`, `avg`, or `sum`. Or target a specific GPU index."
- **Our assessment**: Necessary surface, but the post leaves the policy question open. `max` triggers on the hottest GPU (good for "is any device saturated?"), `avg` hides a single hot device, and `sum` changes the meaning of the target entirely. The guide should say the aggregation is part of the scaling semantics and must be chosen with the target value, not left at a default. Targeting an index is only safe when replicas map predictably to devices — which is a DRA/device-claim concern, not an autoscaler one.

### Claim 8: The post ships four workload profiles — `vllm-inference` (memory 80% / activation 5%), `triton-inference` (utilization 75% / 10%), `training` (utilization 90% / 0%, no scale-to-zero), and `batch` (memory 70% / 1%)
- **Evidence**: The profile table, plus a YAML trigger using `profile: "vllm-inference"`; the values are stated defaults with no measurement behind them.
- **Confidence**: emerging (concrete configuration; unvalidated tuning)
- **Quote**: "Most people run one of a few GPU workload types, so I added profiles that set sensible defaults:"
- **Our assessment**: Record the table as a starting proposal, not a benchmark. The structural insight is that the profile changes *which* metric is authoritative by workload class: request-serving LLMs scale on memory occupancy, Triton on compute, training on compute with scale-to-zero disabled, batch on memory with aggressive scale-down. The numbers themselves (80/75/90/70) are guesses until measured against a real workload; the Prospector's caveat applies. Training's activation of 0% is the notable exception — it deliberately opts out of scale-to-zero.

### Claim 9: The `activationThreshold` is the scale-to-zero gate and is a separate, per-workload number from the steady-state `targetValue`
- **Evidence**: The profile table's "Activation" column varies by profile (5%, 10%, 0%, 1%), and the post says any value may be overridden or the profile skipped in favor of setting `metricType`, `targetValue`, and `activationThreshold` directly.
- **Confidence**: emerging (semantics shown by configuration; the post does not explain how activation and target interact)
- **Quote**: "You can override any value. Or skip profiles entirely and set metricType, targetValue, activationThreshold directly."
- **Our assessment**: This is the operationally load-bearing number for cost, and the post gives it one sentence. The activation threshold decides whether a zero-replica workload wakes at all; set it too high and idle-but-real demand never activates a pod, set it too low and background memory occupancy (or a resident process) keeps the GPU alive forever. Pairing a 5% activation gate with a self-hosted vLLM deployment is a direct trade against multi-minute cold start. The corpus already has the cold-start cost; this note supplies the gate that trades against it. The article does not give a method for choosing either number — mark it as tune-and-measure.

### Claim 10: The Helm chart targets nodes labelled `nvidia.com/gpu.present=true`, tolerates the `nvidia.com/gpu` taint, and falls back to host device mounts when the NVIDIA container runtime is absent
- **Evidence**: The install command followed by the chart's placement and runtime behavior.
- **Confidence**: settled (configuration statement)
- **Quote**: "The chart deploys a DaemonSet that targets nodes with nvidia.com/gpu.present=true and tolerates the nvidia.com/gpu taint. It uses the NVIDIA container runtime by default — if your cluster doesn’t have that, set nvmlHostMounts.enabled=true to mount the device files directly."
- **Our assessment**: The node targeting and toleration are standard for GPU DaemonSets and worth copying as a pattern. The `nvmlHostMounts.enabled=true` fallback is the more interesting operational detail: it lets the scaler read device files on clusters without the NVIDIA runtime, at the cost of mounting host device nodes directly. That is a portability escape hatch, and also a privilege/security decision that the post does not discuss — a host device mount widens the pod's access to the node.

### Claim 11: A `ScaledObject` with `minReplicaCount: 0` and the external trigger pointed at the scaler service scales a vLLM Deployment on GPU memory usage, including to zero when idle
- **Evidence**: The complete `ScaledObject` manifest in the post and the closing sentence of the Quick start section.
- **Confidence**: settled (KEDA configuration semantics)
- **Quote**: "That’s it. KEDA will now scale your vLLM deployment based on GPU memory usage, including scale-to-zero when idle."
- **Our assessment**: Mechanically correct for KEDA, but "that's it" understates the prerequisites: the workload must already be a GPU-scheduled Deployment, the scaler must be reachable at `scalerAddress`, and scale-to-zero still pays the vLLM cold start. The `maxReplicaCount: 8` in the example is a cost/quota guard, not a capacity plan — the autoscaler has no model of downstream saturation (gateway, model server, cloud GPU quota).

### Claim 12: A mock collector mode lets the full `IsActive → GetMetricSpec → GetMetrics` gRPC flow and 11 e2e tests run in CI with no GPU hardware
- **Evidence**: The testing section describes a real gRPC server with fake GPU data and lists the test coverage; the repo is linked and the test command is given.
- **Confidence**: emerging (author's repo; the claim is verifiable but not independently run here)
- **Quote**: "The scaler has a mock collector mode for testing. The e2e test suite spins up a real gRPC server with fake GPU data and exercises the full IsActive → GetMetricSpec → GetMetrics flow. 11 tests covering profiles, error paths, streaming, aggregation modes. All run in CI without any GPU hardware."
- **Our assessment**: This is the most transferable engineering practice in the post, even for teams that never write a scaler. A hardware-dependent control loop is testable if the hardware read is behind an interface and the control protocol is gRPC: mock the collector, exercise the real server, and assert on the protocol messages. It is the difference between "we can only test on the GPU node" and a CI gate. The 11-test count is the author's, not a coverage guarantee.

### Claim 13 (vendor-aligned): Building custom external scalers is a general way to extend KEDA without forcing new workload types into an existing abstraction
- **Evidence**: The conclusion's framing, plus the reference implementation as the concrete example.
- **Confidence**: anecdotal (advocacy for the author's own approach; no comparison with alternatives)
- **Quote**: "Building custom external scalers is a powerful way to extend the CNCF ecosystem. It shows how a graduated project like KEDA can remain flexible, allowing engineers to build custom DaemonSets that fit newer AI infrastructure patterns without forcing every workload into the same abstraction."
- **Our assessment**: Reasonable but self-interested. The external-scaler interface is genuinely an extension point, and the "don't force every workload into one abstraction" argument is sound. The missing alternative analysis is the one that matters operationally: exporting GPU metrics to Prometheus and using KEDA's Prometheus scaler (or the resource metrics API) avoids owning a DaemonSet and gRPC service, at the cost of metric-pipeline latency and cardinality. The guide should present both architectures and their trade-off, not just this one.

### Claim 14: The author frames accelerator waste as a GreenOps problem, asserting that wasted GPU cycles translate directly into wasted energy and higher Scope 3 emissions
- **Evidence**: Asserted in the introduction; no energy, power, or emissions measurements are supplied, even though the scaler exposes `power_draw`.
- **Confidence**: anecdotal (directionally plausible, unquantified)
- **Quote**: "In practice, this is not only a cost problem. It is also a GreenOps problem, because wasted GPU cycles translate directly into wasted energy and higher Scope 3 emissions."
- **Our assessment**: The direction is right — idle accelerators draw power — but "translate directly" is doing a lot of work with no numbers, and Scope 3 attribution is an accounting exercise the post does not attempt. The corpus's Kepler note is the relevant counterweight: GPU power monitoring there is still experimental and unvalidated. Use this claim for motivation, not as evidence of savings.

## Concrete Artifacts

**Profile table (verbatim from source):**
```
Profile           Metric                Target  Activation  Use Case
vllm-inference    memory_used_percent   80%     5%          LLM serving, scale-to-zero
triton-inference  gpu_utilization       75%     10%         Triton model serving
training          gpu_utilization       90%     0%          Training jobs, no scale-to-zero
batch             memory_used_percent   70%     1%          Batch inference, aggressive scale-down
```
(The source renders this as a five-column HTML/Markdown table; values reproduced
exactly, column header order preserved.)

**Profile trigger snippet (verbatim from source):**
```yaml
triggers:
  - type: external
    metadata:
      scalerAddress: "keda-gpu-scaler.gpu-scaler.svc.cluster.local:6000"
      profile: "vllm-inference"
```

**Helm install (verbatim from source):**
```bash
helm install gpu-scaler deploy/helm/keda-gpu-scaler \
  --namespace gpu-scaler --create-namespace
```

**`ScaledObject` example (verbatim from source):**
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: vllm-gpu-scaler
spec:
  scaleTargetRef:
    name: vllm-deployment
  minReplicaCount: 0
  maxReplicaCount: 8
  triggers:
    - type: external
      metadata:
        scalerAddress: "keda-gpu-scaler.gpu-scaler.svc.cluster.local:6000"
        profile: "vllm-inference"
```

**Metric list (verbatim from source):**
```
-   gpu_utilization – SM (compute) utilization percentage
-   memory_utilization – memory controller utilization
-   memory_used_percent – VRAM usage as a percentage
-   temperature – GPU die temperature in celsius
-   power_draw – current power consumption in watts
```

**GPU-free e2e test command (verbatim from source):**
```bash
go test -v -tags=e2e -race ./tests/e2e/
```

**Reference implementation (verbatim from source):** `https://github.com/pmady/keda-gpu-scaler`

## Cross-References

- **Extends**: `source-notes/blog-cncf-keda-sqs-queue-depth-autoscaling.md` — same KEDA `ScaledObject` machinery, different demand signal. That note's **Claim 1** establishes backlog as the true signal for asynchronous queue workers, **Claim 7** separates `activationQueueLength` from `queueLength`, and **Claim 9** covers `minReplicaCount: 0`. This source is the accelerator counterpart: **Claim 9** here separates a GPU `activationThreshold` from the steady-state `targetValue`, and **Claim 11** uses the same zero-minimum `ScaledObject`. The contrast is the guide-relevant part: queue depth is a *leading* signal of work not yet started, while GPU utilization/memory is a *lagging*, per-pod measure of work already running. They are complements for different workload classes (queue workers vs request-serving), not substitutes — which is why this is an extension, not a contradiction. That note's **Claim 10** (fallback replicas when metrics are unavailable) also applies unchanged to a `minReplicaCount: 0` GPU workload.

- **Extends**: `source-notes/blog-cncf-running-self-hosted-llm-kubernetes-vllm.md` — that note's **Claim 4** establishes that scaling to zero preserves the PVC and cached weights, and **Claim 5** establishes a multi-minute cold start dominated by weight fetch + engine init. This source supplies the autoscaling control loop that decides when to pay that cold start, and the `vllm-inference` profile's 5% activation gate (**Claim 9** here) is the exact knob that trades idle savings against repeated cold starts. The two notes together define the cost equation the guide should present: scale-to-zero only pays if genuine idle time exceeds cold-start amortization.

- **Extends**: `source-notes/blog-cncf-kubernetes-health-checks-waking-services.md` — that note's **Claim 1** shows ambient probe traffic being read as demand, so a request-activated service never stays at zero, and **Claim 11** calls GPU pods a primary beneficiary of fixing that loop. This source is a different activation path: KEDA reads GPU metrics from a side agent rather than inferring demand from inbound requests, so probe traffic does not wake it. That makes the two mechanisms complementary — but only if the GPU signal itself returns to idle; a resident process holding VRAM can defeat scale-to-zero just as probes do, which is why the activation threshold here (**Claim 9**) is the analogue of that note's probe-matching gate.

- **Extends**: `source-notes/blog-cncf-kepler-rearchitected-power-accuracy.md` — that note's **Claim 10** states that GPU power monitoring in Kepler is behind an experimental flag and explicitly seeks end-user validation, and **Claim 11** describes power attribution as a hardware-meter → process → pod pipeline. This source exposes `power_draw` directly from NVML (**Claim 6**) and proposes it as a scaling signal, which is a narrower and more mature use than per-workload energy attribution: device watts are available, but the emissions/Scope 3 claim (**Claim 14** here) still needs the validation that Kepler is asking for. Do not let the guide treat "we can read power draw" as "we can account for energy cost."

- **Extends**: `source-notes/blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` — that note's **Claim 10** notes that Cluster Autoscaler may provision GPU nodes on demand in the future, and its device-allocation claims (e.g. **Claim 9** time-slicing) concern how GPUs are assigned to pods. This source scales *replicas of a workload on existing GPU nodes* (HPA via KEDA), not the node pool; it assumes the GPU is already schedulable. Pair the two: accelerator capacity control has a node-provisioning layer and a pod-replica layer, and this note covers only the second.

- **Corroborates**: `source-notes/failure-cncf-kubeflow-cilium-60-idle-gpus.md` — that note's **Claim 4** treats GPU utilization as the observable signal for wasted accelerator spend ("In our lab, GPU utilization went from around 40% to around 85% the moment the group was co-located."), and **Claim 6** says GPU utilization plus pod-zone metrics exposed the problem in seconds. This source agrees that GPU utilization is the right observability signal and goes one step further, making it the autoscaling input. The difference in root cause (topology mismatch there vs a missing scaling signal here) is exactly the point: both notes arrive at "instrument GPU utilization or idle spend stays invisible."

- **Contradicts**: None. The Prospector flagged the queue-depth note's **Claim 1** against GPU metrics, but those claims apply to different workload classes (asynchronous queue workers vs request-serving inference), so it is a conditioning variable, not a conflict. Verified against `CONTRADICTIONS.md` (no `C-NNN` entries) and open `contradiction`-labeled issues; no contradiction issue filed.

- **Novel**: First source note in the corpus on accelerator-aware autoscaling. Specifically new: (1) the two-constraint reasoning chain (`CGO_ENABLED=0` in KEDA core + node-local NVML) that rules out both a native scaler and a centralized operator-side scaler; (2) the per-node DaemonSet speaking `ExternalScaler` over gRPC as the resulting architecture; (3) the five-metric surface and the compute/memory-controller/VRAM distinction; (4) the four profile defaults and the activation-vs-target split for GPU workloads; (5) NVIDIA node targeting, taint toleration, and the `nvmlHostMounts` fallback; (6) the mock-collector e2e pattern for testing a hardware-dependent control loop in CI.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability → Cost, capacity, and fallback patterns)**: Add a subsection on accelerator-aware autoscaling for self-hosted inference. Explain why CPU/memory HPA is blind to the GPU [Claim 1], then present the two architectural options: export GPU metrics to Prometheus and use KEDA's Prometheus scaler, or run a per-node `ExternalScaler` DaemonSet [Claims 2–4; Claim 13's missing alternative analysis]. If the latter, state the new failure domain plainly — a scaler pod that cannot be scheduled or crashes can stall scaling. Present the four profiles as starting defaults, not recommendations [Claim 8], and require `targetValue` and `activationThreshold` to be chosen per workload and measured [Claim 9]. Tie the `vllm-inference` activation gate to the cold-start cost already cited in this chapter [source: blog-cncf-running-self-hosted-llm-kubernetes-vllm, Claims 4–5]. Pair `maxReplicaCount` with the downstream saturation/quota analysis already in the chapter [source: blog-cncf-keda-sqs-queue-depth-autoscaling, Claim 9].

- **Chapter 02 (Observability → GPU and capacity signals)**: Add the three-way metric distinction — SM utilization, memory-controller utilization, VRAM percentage — and require dashboards/policies to name which one they use [Claim 6]. Note that inference commonly holds high VRAM at low SM utilization, which is why a memory-based policy is the `vllm-inference` default. Add per-GPU aggregation as an explicit policy choice (`max` vs `avg` vs `sum`) rather than a default [Claim 7]. Cross-link the Kepler note for power-draw attribution and flag that GPU energy accounting is still experimental [source: blog-cncf-kepler-rearchitected-power-accuracy, Claims 10–11; Claim 14 here].

- **Chapter 04 (Oncall and Toil → autoscaler runbooks)**: Add GPU-autoscaler failure modes to the runbook: scaler DaemonSet not scheduled on a GPU node (missing label/taint tolerance) [Claim 10], scaler unreachable at `scalerAddress`, a resident process holding VRAM so the workload never scales to zero [Claim 9], and a `maxReplicaCount` that masks a downstream bottleneck [Claim 11]. Reuse the queue-note runbook structure [source: blog-cncf-keda-sqs-queue-depth-autoscaling, Claim 11]. Add the explicit test "scale to zero, confirm the workload actually reaches zero and the cold start is acceptable" rather than assuming the configuration works.

- **Chapter 00 (Principles → cost/efficiency of accelerator capacity)**: Add the framing that idle accelerator capacity is both a cost and an energy problem [Claim 1; Claim 14], while marking the GreenOps/Scope 3 claim as motivation rather than measured evidence. The actionable principle is "the scaling signal must observe the resource that actually constrains the workload" — CPU/memory for ordinary services, GPU metrics for request-serving inference, backlog for queue workers [source: blog-cncf-keda-sqs-queue-depth-autoscaling, Claim 1].

## Extraction Notes

- Read the full article (single page, no substantive linked sub-pages followed). The post links to the `keda-gpu-scaler` GitHub repo and NVIDIA's go-nvml; I did not deep-read the repo because the note's claims are scoped to what the post states, and the repo was treated as the artifact the post announces rather than an independent source. No paywall; fully readable.
- All quotes copied character-for-character from the rendered page, including the curly apostrophes and the en dash in the NVML definition. The profile table is rendered on the page as an HTML table with bold headers; I reproduced the cell values exactly in a fenced block and preserved the header order (`Profile`, `Metric`, `Target`, `Activation`, `Use Case`), noting the formatting conversion. The architecture quote retains the source line break after "each pod:" and the numbered list.
- `confidence_overall: emerging` — the two structural constraints and the configuration mechanics are settled and reproducible, but the source supplies zero measurements (no throughput, latency, cost, energy, or scaling-time data), every profile value is an unvalidated default, and the GreenOps/emissions claim is asserted. This matches the Prospector's caveat; treat thresholds as proposals to tune.
- Related-notes candidates from `miner-related-notes.md`, each cited or dismissed per MINER.md §4:
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed; retail/gaming SLO granularity, no autoscaling or GPU content.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — dismissed; multi-agent security platform deployment; its HPA mention is ordinary microservice scaling, no GPU metrics.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — dismissed; imperative vs declarative change workflows, no autoscaler mechanics.
  - `docs-google-sre-reliable-product-launches.md` — dismissed; launch coordination/checklists, unrelated.
  - `docs-google-sre-configuration-specifics.md` — dismissed; configuration toil and DSL design, not autoscaling configuration.
  - `docs-google-sre-slo-engineering-case-studies.md` — dismissed; SLO adoption case studies, no capacity-control loop.
  - `docs-google-sre-prodcast-03-01.md` — dismissed; SRE methodology and organizational influence, unrelated.
  - `docs-google-sre-prodcast-03-09-profiling-data.md` — dismissed; profiling-data modalities and analysis methods, not hardware scaling signals.
  - `docs-litellm-anthropic-advisor-tool.md` — dismissed; within-request model composition, no serving capacity control.
  - `docs-litellm-completion-function-call.md` — dismissed; function-calling capability predicates, unrelated.
- The Prospector's four overlapping notes were all read and cited: `blog-cncf-keda-sqs-queue-depth-autoscaling.md`, `blog-cncf-running-self-hosted-llm-kubernetes-vllm.md`, `blog-cncf-kubernetes-health-checks-waking-services.md`, and `blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md`. Two additional notes were found by searching `source-notes/`: `failure-cncf-kubeflow-cilium-60-idle-gpus.md` (GPU utilization as the observability signal) and `blog-cncf-kepler-rearchitected-power-accuracy.md` (GPU power attribution maturity).
- Cross-reference claim numbers were re-read and verified against the cited notes before writing (MINER.md §4b). No contradiction found; no contradiction issue filed.
