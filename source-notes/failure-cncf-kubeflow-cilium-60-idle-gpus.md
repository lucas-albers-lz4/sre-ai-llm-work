---
source_url: https://www.cncf.io/blog/2026/07/23/when-kubeflow-meets-cilium-debugging-60-idle-gpus-in-kubernetes
source_type: failure-report
title: "When Kubeflow meets Cilium: Debugging 60% idle GPUs in Kubernetes"
author: "Ramkumar Nagaraj (Adobe), Bingi Narasimha Karthik (Adobe)"
date_published: 2026-07-23
date_extracted: 2026-10-16
last_checked: 2026-10-16
status: current
confidence_overall: emerging
issue: "#1750"
---

# When Kubeflow meets Cilium: Debugging 60% idle GPUs in Kubernetes

> A topology-aware CNI (Cilium) and a topology-agnostic scheduler (Kubernetes/Kubeflow) each make correct decisions that silently break distributed training when the coordinator and GPU workers land in different zones, leading to 60% GPU idling with all health checks green.

## Source Context

- **Type**: blog-post (CNCF Member Post, practitioner writeup)
- **Author credibility**: Ramkumar Nagaraj (Golden Kubestronaut, Adobe) and Bingi Narasimha Karthik (Golden Kubestronaut, Adobe). The authors report from production debugging and provide a reproducible lab.
- **Scope**: A concrete failure mode where CiliumNetworkPolicy zone boundaries are invisible to the Kubernetes scheduler, causing silent failures in distributed training (Kubeflow) when coordinator and workers land in different zones. The article describes three manifestations of the same root cause, the fix, and a lab repo.
- **Limitations**: The article prints no YAML, log excerpts, or raw telemetry queries. The 30-60% throughput loss and 40%→85% GPU utilization figures are lab/observed outcomes rather than detailed production benchmarks. No specific Kubernetes/Kubeflow/Cilium/NCCL version numbers are given.

## What Was Attempted

- **Goal**: Run distributed training jobs via Kubeflow on Kubernetes with GPU workers, in a cluster where operators use CiliumNetworkPolicy to enforce zone boundaries for isolation/compliance/cost control.
- **Setup**: Kubernetes + Kubeflow scheduling GPU training jobs; Cilium enforcing topology-aware network policies (zone boundaries); distributed training uses a coordinator + GPU workers synchronizing gradients (e.g. NCCL AllReduce).
- **Expected outcome**: Scheduled pods run, health checks pass, training progresses using allocated GPUs.

## What Went Wrong

The core issue: two systems acting correctly in isolation produce silent degradation.

- **Symptoms**: 
  1. **Hard block** (seconds) — zone-boundary network policy denies connection; workers cannot reach coordinator; training never starts.
  2. **Cross-zone latency** (hours) — no hard block, but cross-zone round-trip causes NCCL AllReduce to pay latency; throughput drops 30-60% with no errors/logs indicating failure; all pods healthy, all health checks green.
  3. **Cross-AZ egress cost** (days) — traffic crosses AZs; cost appears only on the cloud bill as inter-AZ data transfer.

- **Severity**: High impact — >50% GPU idling in the reported case; paid-for capacity wasted; failure is silent (no alerts/errors) and hard to detect without the right metrics.
- **Key observation**: "A distributed training job was scheduled and healthy — every pod was running, no crashes, no OOMKills, nothing in the logs. And yet more than half the GPUs we were paying for sat idle, and training never actually started. Every health check was green, and nothing was computing."

## Root Cause

- **Author's diagnosis**: Kubernetes scheduler is topology-agnostic (places pods by CPU/memory/GPU availability). Kubeflow inherits this. Cilium is topology-aware (zone boundaries via CiliumNetworkPolicy) and cannot reschedule pods after placement. The coordinator lands in one zone, GPU workers in another; network policy silently blocks or degrades connectivity between them. No single system has the combined view of placement + network topology constraints.
- **Quote**: "Kubernetes scheduling is topology-agnostic by design... Cilium, on the other hand, is topology-aware. Operators use CiliumNetworkPolicy to draw zone boundaries... Put those two together and you get a class of problem where each system makes an individually correct decision, and together they’re wrong. The coordinator lands in one zone, the GPU workers in another, and the network silently blocks the connection between them. No one holds the single map that shows both the pod placement and the locked doors at once."
- **Confidence**: emerging (clear diagnosis from lab + production observation; generalizes to any topology-aware CNI + topology-agnostic scheduler + distributed training).

## Recovery Path

- **Fix**: Make the scheduler topology-aware for this workload by enforcing co-location in a zone that allows traffic. Do not weaken network policy or change CNI/framework.
- **Implementation** (Kubernetes-native): Add `nodeAffinity` to pin the group to the GPU zone, `topologySpreadConstraints` to co-locate coordinator and workers, and a `toleration` so the coordinator can land on GPU-tainted nodes. As a portable alternative, use `podAffinity` with a zone topology key (place workers in whatever zone the coordinator lands in).
- **Result**: In the lab, GPU utilization went from ~40% to ~85% after co-location; hard block disappears, cross-zone latency disappears, cross-AZ egress disappears.
- **Quote**: "We didn’t touch Cilium — the locked doors stay locked... We simply gave the scheduler the one piece of information it was missing: keep the whole training group together, in a zone whose network path is open."

## Extracted Lessons

- **Topology blindness is the bug class**: When a topology-aware control (CNI policy) is invisible to the placement control (scheduler), distributed workloads can silently fail. The failure is not in either system alone.
- **Silent failures require the right telemetry**: GPU utilization + pod-zone metrics in Prometheus/Grafana exposed the issue; without them detection could take hours/days. Health checks and logs were all green.
- **Fix at the right layer**: Giving the scheduler topology constraints is simpler and safer than weakening network policy. Keep the security boundary intact.
- **Generalizes**: Any topology-aware CNI + any distributed ML framework (not just Cilium/Kubeflow) can hit this. Version-agnostic pattern.

## Extracted Claims

### Claim 1: Topology-aware CNI policies are invisible to the Kubernetes scheduler
- **Evidence**: CiliumNetworkPolicy enforces zone boundaries; Kubernetes scheduler places pods by resource availability without knowing those boundaries.
- **Confidence**: settled
- **Quote**: "Kubernetes scheduling is topology-agnostic by design. It places pods based on available resources — CPU, memory, GPU count — without reasoning about which availability zone a pod lands in. Kubeflow inherits that assumption. Cilium, on the other hand, is topology-aware. Operators use CiliumNetworkPolicy to draw zone boundaries for blast-radius isolation, compliance, cost control, or to protect an expensive dedicated GPU pool."
- **Our assessment**: This is the root cause class. The two systems operate on different topology views with no coordination.

### Claim 2: Correct systems can produce silent collective failure
- **Evidence**: Each system makes individually correct decisions; together they break distributed training with no errors.
- **Confidence**: settled
- **Quote**: "Put those two together and you get a class of problem where each system makes an individually correct decision, and together they’re wrong. The coordinator lands in one zone, the GPU workers in another, and the network silently blocks the connection between them. No one holds the single map that shows both the pod placement and the locked doors at once."
- **Our assessment**: Classic "local correctness, global wrongness" — important SRE failure pattern.

### Claim 3: Same root cause manifests in three time horizons (hard block, latency, cost)
- **Evidence**: Production observations show three distinct symptoms from the same placement+policy mismatch.
- **Confidence**: emerging
- **Quote**: "It’s a spectrum, not a single bug. What surprised us most is that the same root cause shows up three different ways in production: 1. Hard block. A zone-boundary network policy denies the connection outright. Workers can’t reach the coordinator and training never starts. You notice in seconds. 2. Cross-zone latency. With no hard block, just distance, gradient synchronization (NCCL AllReduce) pays cross-zone round-trip time on every step. Throughput quietly drops 30–60% with no error at all. You notice in hours, if you’re paying attention. 3. Cross-AZ egress cost. The traffic crosses availability zones and shows up only on the cloud bill as inter-AZ data transfer. You notice in days, on the invoice."
- **Our assessment**: The silent variants (latency/cost) are most dangerous — they look like normal operation. The 30-60% figure is asserted from observation; treat as lab/observed, not universal constant.

### Claim 4: GPU utilization drop is the observable signal
- **Evidence**: Lab measurement shows GPU utilization improving after co-location.
- **Confidence**: emerging
- **Quote**: "In our lab, GPU utilization went from around 40% to around 85% the moment the group was co-located."
- **Our assessment**: GPU utilization is the key metric that exposed idle GPUs; in conjunction with pod-zone mapping, it makes the silent failure visible.

### Claim 5: Kubernetes-native fix — give scheduler topology constraints without weakening policy
- **Evidence**: Fix uses `nodeAffinity`, `topologySpreadConstraints`, toleration (or `podAffinity` with zone topology key); no CNI change, no Kubeflow/K8s patch.
- **Confidence**: settled
- **Quote**: "We didn’t touch Cilium — the locked doors stay locked, because the security policy was never the problem. And we didn’t patch Kubernetes or Kubeflow. We simply gave the scheduler the one piece of information it was missing: keep the whole training group together, in a zone whose network path is open... In practice that’s a few lines of Kubernetes-native YAML on the workload spec: nodeAffinity to pin the group to the GPU zone, topologySpreadConstraints to co-locate the coordinator and workers, and a toleration so the coordinator can actually land on the GPU-tainted nodes. Once every communicating pod shares a zone, the traffic is intra-zone — the hard block disappears, the latency disappears, and the cross-AZ egress disappears. One fix, all three symptoms. If you don’t want to hard-code a zone name, podAffinity with a zone topology key achieves the same thing by relationship: place the workers in whatever zone the coordinator landed in. Same idea, portable across clusters."
- **Our assessment**: Correct fix — encode the communication constraint in scheduling, not by weakening network isolation.

### Claim 6: Instrumentation is essential for detection
- **Evidence**: GPU utilization + pod-zone metrics in Prometheus/Grafana surfaced the issue quickly.
- **Confidence**: settled
- **Quote**: "Instrument before you need it. GPU utilization and pod-zone metrics in Prometheus and Grafana exposed this for us in seconds; without them it can take days."
- **Our assessment**: Classic observability lesson — without the right signal (GPU util by zone/pod), a silent degradation goes undetected for long periods.

### Claim 7: Pattern generalizes beyond Cilium/Kubeflow
- **Evidence**: Authors state generalization to any topology-aware CNI + any distributed ML framework.
- **Confidence**: emerging
- **Quote**: "The pattern generalizes. Any topology-aware CNI plus any distributed ML framework can hit the same wall. It isn’t specific to Cilium or Kubeflow."
- **Our assessment**: Reasonable generalization — failure class is scheduler/CNI topology mismatch affecting any tightly-coupled distributed workload.

## Concrete Artifacts

- **Reproducible lab**: `https://github.com/ram2valar/kubeflow-cilium-lab` — kind cluster with GPU and CPU zones, Cilium policy, Prometheus recording rules, Grafana dashboard, before/after demo scripts.
- **Talk recording**: KubeCon + CloudNativeCon India 2026 — `https://www.youtube.com/watch?v=BG9XGouyM9c`
- **Fix pattern (described)**: `nodeAffinity` (GPU zone), `topologySpreadConstraints` (co-locate coordinator+workers), `toleration` (GPU-tainted nodes). Portable variant: `podAffinity` with zone topology key.

## Cross-References

- **Corroborates**:
  - `source-notes/blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` — Also covers GPU/device allocation in Kubernetes (DRA); this source is complementary (placement/topology + network reachability vs device selection).
  - `source-notes/blog-cncf-running-self-hosted-llm-kubernetes-vllm.md` — GPU utilization concerns for AI workloads on Kubernetes (serving); different workload class (distributed training vs inference) but same observability theme (GPU utilization as key signal).
  - `source-notes/blog-cncf-goodput-more-than-throughput-llm-serving.md` — Focus on goodput/throughput for LLM serving; cross-zone latency causing 30-60% throughput loss parallels goodput degradation concerns.
  - `source-notes/docs-google-sre-handling-overload.md` — Shares "silent degradation without explicit errors" theme; this adds network-topology mechanism as concrete root cause.

- **Extends**:
  - `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md` — Adjacent CNI/network-boundary enforcement patterns; focuses on agent egress auditing via proxy, while this focuses on distributed training placement causing silent connectivity issues.

- **Novel**:
  - Explicit failure class: "topology-aware CNI × topology-agnostic scheduler" causing silent distributed training failure. Not covered by existing notes.
  - Three-symptom spectrum (hard block/latency/cost) from same root cause with different detection latencies (seconds/hours/days).
  - Kubernetes-native remediation keeping network policy intact (co-locate via scheduling constraints) as the answer.

## Guide Impact

- **Chapter 01 (Incident Response)**: Add pattern for silent degradation — when health checks/logs are green but business metric (GPU utilization/cost) is bad, suspect topology/CNI-scheduler mismatch. Detection needs metrics beyond "pod running/ready".
- **Chapter 02 (Observability)**: Emphasize GPU utilization + pod-zone mapping as critical telemetry for GPU workloads; cross-zone latency/cost can be invisible without these. Prometheus recording rules/Grafana dashboard from lab are concrete artifacts.
- **Chapter 05 (LLM Ops Reliability)**: Document this failure class for distributed training on Kubernetes. Recommend encoding communication topology constraints in workload specs (nodeAffinity/topologySpreadConstraints/podAffinity) when using topology-aware CNIs. Keep network policy intact.
- **Chapter 06 (Security/Trust)**: Note that security boundaries (zone isolation) must be complemented by scheduler awareness — defense-in-depth doesn't require weakening policy; encode constraints in placement instead.

## Extraction Notes

- Source read in full from CNCF blog (2026-07-23). All quoted passages copied character-for-character from extracted text.
- Treated as `failure-report` (silent partial failure). Extracted three-symptom spectrum, root cause, remediation, metrics (40%→85%, 30-60%).
- Cross-referenced relevant CNCF GPU/K8s notes; no existing note covers CNI-scheduler topology disagreement. No contradiction found.
- Candidates from `miner-related-notes.md` are mostly unrelated (retail/gaming, declarative config, etc.) — dismissed as not addressing this specific failure class.
