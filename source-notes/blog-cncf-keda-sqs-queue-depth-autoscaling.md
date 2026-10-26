---
source_url: https://www.cncf.io/blog/2026/07/31/scaling-kubernetes-pods-with-keda-based-on-amazon-sqs-queue-depth
source_type: blog-post
title: "Scaling Kubernetes pods with KEDA based on Amazon SQS queue depth"
author: "Albena Galabova (Itgix)"
date_published: 2026-07-31
date_extracted: 2026-10-26
last_checked: 2026-10-26
status: current
confidence_overall: emerging
issue: "#1884"
---

# Scaling Kubernetes pods with KEDA based on Amazon SQS queue depth

> A CNCF Member Post walkthrough of backlog-driven autoscaling for EKS
> workers: KEDA polls SQS queue attributes and drives an HPA, desired replicas
> are `ceil(outstanding / queueLength)`, and the non-obvious operational work
> is in choosing what counts as outstanding, separating the scale-to-zero and
> steady-state thresholds, and tuning KEDA's cooldown independently of the
> HPA's scale-down stabilization window. It contains no LLM content and no
> measured results; the transfer to queue-driven LLM workers is ours to make.

## Source Context

- **Type**: blog-post (CNCF Member Post, vendor-authored by Albena Galabova of
  Itgix, a cloud-native consultancy). CNCF highlights KEDA and Kubernetes.
- **Author credibility**: The author is a practitioner at a cloud-native
  consultancy and supplies complete, reproducible manifests, an IAM policy, a
  verification procedure, and a troubleshooting table. The post is a technical
  walkthrough rather than product placement (no product is being sold), but it
  reports no throughput, cost, latency, or scaling-time measurements, so the
  operational outcomes are asserted rather than demonstrated.
- **Scope**: Covers installing KEDA on EKS, authenticating to SQS with pod
  identity, a `ScaledObject` for an SQS consumer, KEDA's replica-calculation
  logic, a manual verification procedure, a four-row troubleshooting table,
  and four tuning tips. Does NOT cover LLM/AI workloads, queue-message schema,
  consumer concurrency/prefetch, dead-letter queues, SQS FIFO ordering, scale-up
  latency, cost measurements, or any before/after production data. The entire
  article is AWS/EKS/SQS-specific even though the conclusion claims the pattern
  generalizes.

## Extracted Claims

### Claim 1: For asynchronous queue workers, backlog — not CPU or memory utilization — is the scaling signal that reflects real demand
- **Evidence**: The author contrasts an idle-looking worker with a queue holding thousands of messages, and pods that keep running after a spike has passed; the rest of the post implements the backlog signal. No measurements are supplied.
- **Confidence**: emerging (well-established design principle; practitioner assertion here, not measured)
- **Quote**: "For asynchronous, queue-based workloads, backlog is the true scaling signal – not infrastructure utilization."
- **Our assessment**: Buy the principle. Utilization is a lagging, per-pod measure of how busy the workers already are; queue depth is a leading measure of work not yet started. The important caveat the post does not state is that queue depth is only a valid signal if the queue is the actual admission point and workers cannot bypass it. For LLM batch inference, embedding backfills, and agent job queues, this is usually true; for request/response inference behind a load balancer, in-flight concurrency or token backlog may be the better signal.

### Claim 2: KEDA implements backlog autoscaling by polling SQS queue attributes and writing target metrics to a Kubernetes HPA, which then scales the worker Deployment
- **Evidence**: The architecture section describes the request flow step by step (producers → SQS → KEDA → HPA → Deployment → pods → drain), and the manifests configure a `ScaledObject` rather than a standalone HPA.
- **Confidence**: settled (documented KEDA mechanism)
- **Quote**: "This architecture relies on KEDA observing Amazon SQS queue metrics and managing a Kubernetes Horizontal Pod Autoscaler (HPA) based on backlog."
- **Our assessment**: The split is worth internalizing: KEDA is the external-metric adapter and activation controller; the HPA is the actual replica controller. That means two control loops and two sets of tuning knobs, which is the root of the scale-down confusion in Claim 8. Treat the HPA that KEDA creates as managed — editing it directly is the wrong layer.

### Claim 3: KEDA computes outstanding work as visible messages plus not-visible (in-flight) messages, plus delayed messages when enabled, and sets desired replicas to `ceil(outstanding / queueLength)`
- **Evidence**: The post states the outstanding-work formula and the replica formula, with a worked numeric example. This is KEDA's documented SQS trigger behavior, reproduced as prose rather than as code.
- **Confidence**: settled (documented algorithm; the post's example arithmetic checks out)
- **Quote**: "desired replicas = ceil(outstanding messages / queueLength)"
- **Our assessment**: The ceiling means any non-zero backlog above the per-pod target produces at least one replica — a useful property for burst handling, but it also means the activation threshold (Claim 7) and the per-pod target (Claim 6) jointly decide whether a small backlog is worth waking anything. The formula is only as good as the definition of "outstanding": visible + not-visible + delayed is a policy choice, not a neutral measurement (see Claim 5).

### Claim 4: With `queueLength: "10"`, 0 messages maps to 0 pods, 8 to 1, 25 to 3, and 95 to 10 — the value is an illustration, not a recommendation
- **Evidence**: The author's arithmetic example under "Replica Calculation Logic," using the formula from Claim 3.
- **Confidence**: settled (arithmetic), anecdotal (whether 10 is appropriate for any real workload)
- **Quote**:
  ```
  -   0 messages → 0 pods
  -   8 messages → 1 pod
  -   25 messages → 3 pods
  -   95 messages → 10 pods
  ```
- **Our assessment**: Use this to explain the shape of the curve, not as a default. The post itself says to choose `queueLength` from throughput (Claim 6), and the Prospector explicitly warned not to import `10` as a recommendation. The example also silently assumes one message per unit of worker capacity; if a consumer prefetches in batches, the effective per-pod target is `queueLength × batch size`, not `queueLength`.

### Claim 5: Counting in-flight (`ApproximateNumberOfMessagesNotVisible`) messages as backlog is a policy choice that can over-scale, and it must be decided against the SQS visibility timeout
- **Evidence**: The troubleshooting table names in-flight counting as the cause of "too many pods" and points the operator at `scaleOnInFlight` and the SQS visibility timeout; a tuning tip repeats the decision.
- **Confidence**: emerging (practitioner checklist; no measured over-scaling example or guidance on which setting to choose)
- **Quote**: "Cause: In-flight messages counted"
- **Our assessment**: Real trap, and more subtle than the post lets on. In-flight messages have already been handed to a consumer, so counting them as backlog can double-count capacity that is already working. But if the visibility timeout is short relative to processing time, those messages will return to the queue and become real backlog again. The correct choice therefore depends on prefetch/concurrency, batch size, and the visibility timeout — three variables the post names but does not connect. For LLM workers, where a single inference can run for minutes, a visibility timeout shorter than the inference duration is a reliable way to manufacture phantom backlog.

### Claim 6: `queueLength` is a per-pod throughput target that must be derived from measured throughput, not copied from an example
- **Evidence**: The production-tuning section states the rule directly; it supplies no method or measurements for deriving the value.
- **Confidence**: emerging (sound rule; no derivation procedure)
- **Quote**: "Choose queueLength based on throughput, not guesswork"
- **Our assessment**: Buy the rule and treat the omission as a gap. For an LLM worker, the denominator is not messages/second but messages/second at the worker's real concurrency and latency — a value that changes with model, prompt length, batch size, and hardware. The guide should say "measure sustainable drain rate per replica under production-shaped load, then set the target," not "set it to 10."

### Claim 7: `activationQueueLength` and `queueLength` are separate thresholds — one controls activation from zero, the other the steady-state per-pod target
- **Evidence**: The example `ScaledObject` sets `queueLength: "10"` and `activationQueueLength: "1"`, and the accompanying explanation says each pod targets 10 messages while scale-to-zero happens when the queue is empty.
- **Confidence**: emerging (shown in configuration; the post does not document the semantics or interaction of the two fields)
- **Quote**: "Each pod targets 10 messages, and scale-to-zero is enabled when the queue is empty."
- **Our assessment**: This is the most useful configuration distinction in the post, but the post underexplains it: the reader has to know from KEDA documentation that `activationQueueLength` is the backlog at which a zero-replica workload activates, while `queueLength` drives the HPA target once active. The operational consequence is that an activation threshold set too high lets a small but real backlog sit unprocessed indefinitely; setting it to 1 makes any message wake the worker. Which is right depends on cold-start cost (see Cross-References).

### Claim 8: KEDA's `cooldownPeriod` and the HPA's `scaleDown.stabilizationWindowSeconds` are independent scale-down paths and must be tuned separately
- **Evidence**: The `ScaledObject` sets `cooldownPeriod: 120` and `scaleDown.stabilizationWindowSeconds: 60`; the tuning section states that they control different paths.
- **Confidence**: emerging (author recommendation; no measured interaction or worked example)
- **Quote**: "Tune cooldown and HPA behavior separately – they control different scale-down paths"
- **Our assessment**: Important and easy to miss. KEDA's cooldown governs when the trigger is considered inactive (including the path back to zero), while the HPA stabilization window delays downward replica decisions above zero. Because they act in series, the effective scale-down can be slower than either value suggests, and changing one while leaving the other at its default produces behaviour that looks like a bug. The post does not say how the two compose, so the guide should present this as "verify the effective delay end to end," not as a formula.

### Claim 9: `minReplicaCount: 0` enables scale-to-zero and `maxReplicaCount` bounds the autoscaler; the example uses 0 and 30
- **Evidence**: The `ScaledObject` manifest and the statement that final replica counts are bounded by both fields.
- **Confidence**: settled (KEDA configuration semantics)
- **Quote**: "Final replica counts are bounded by minReplicaCount and maxReplicaCount."
- **Our assessment**: The maximum is a cost and quota guard, not a capacity plan. KEDA will happily scale to `maxReplicaCount` even if the downstream database, model server, or cloud quota cannot absorb it — the autoscaler has no model of downstream saturation. Pair the maximum with the overload/dependency analysis already in the corpus rather than treating it as a sufficient safety limit.

### Claim 10: Fallback replicas protect queue processing when the autoscaler cannot fetch metrics
- **Evidence**: One tuning tip recommends enabling fallback replicas for resilience; the troubleshooting table says "HPA exists but no scaling" can be caused by authentication or metric-fetch errors and points at KEDA logs and fallback status.
- **Confidence**: anecdotal (recommendation only; no `fallback` configuration is shown or tested)
- **Quote**: "Enable fallback replicas for resilience if metrics become unavailable"
- **Our assessment**: The failure mode is the important part: with `minReplicaCount: 0`, a metrics outage can leave the workload at zero even while the queue fills, because the autoscaler has no way to observe demand. The post recommends fallback replicas but does not show the KEDA `fallback` block, so the guide cannot copy a complete configuration from this source. Treat "autoscaler metric outage must not become a queue stall" as the rule; test it by blocking metric access.

### Claim 11: The troubleshooting table maps four symptoms to distinct causes — no scale-out, too many pods, never scaling to zero, and HPA present but no scaling
- **Evidence**: The "Troubleshooting Common Issues" section, reproduced in Concrete Artifacts.
- **Confidence**: emerging (practitioner checklist; no evidence of how often each cause occurs)
- **Quote**: "Cause: Authentication or metric fetch errors"
- **Our assessment**: High-value operator artifact because the four rows correspond to four different layers: queue address/permissions, backlog definition, message lifecycle, and the KEDA→HPA control path. That is a better diagnostic ordering than "check the autoscaler" because it forces the operator to ask whether the queue is reachable, whether the signal is defined correctly, and whether messages are actually leaving the queue. Add "queue age" to the table: a workload can scale out and still never drain if per-message processing is slower than arrival.

### Claim 12: KEDA authenticates to SQS through AWS pod identity and a `TriggerAuthentication`, with least-privilege IAM and the queue URL sourced from the environment
- **Evidence**: The `TriggerAuthentication` uses `podIdentity.provider: aws`; the IAM policy grants only the five SQS actions the consumer needs; the trigger uses `queueURLFromEnv: QUEUE_URL`.
- **Confidence**: settled (configuration/security best practice)
- **Quote**: "Using queueURLFromEnv avoids hardcoding the queue URL."
- **Our assessment**: Correct and transferable, but not novel. The useful detail is that the autoscaler and the consumer need overlapping but not identical permissions — KEDA needs `GetQueueAttributes`/`GetQueueUrl`, the worker needs `ReceiveMessage`/`DeleteMessage`/`ChangeMessageVisibility`. The post grants the union to one identity; a stricter deployment would split them, so the autoscaler cannot consume and the consumer cannot reconfigure the queue.

### Claim 13: The author claims the backlog-signal pattern generalizes beyond SQS/EKS/KEDA to other event-driven platforms
- **Evidence**: The conclusion's generalization, unsupported by any second platform or non-AWS example.
- **Confidence**: anecdotal (asserted, not demonstrated)
- **Quote**: "Although this article demonstrated the approach using Amazon SQS, Amazon EKS, and KEDA, the same design pattern applies across many event-driven architectures and messaging platforms."
- **Our assessment**: The generalization is reasonable at the level of "scale on outstanding work," but the mechanics are platform-specific: visibility timeouts, dead-letter behaviour, delayed delivery, and per-message acknowledgement differ across SQS, Kafka, Pub/Sub, and Redis streams. Carry the principle into the guide; do not carry the SQS-specific formula unchanged.

## Concrete Artifacts

**KEDA installation (verbatim from source):**
```bash
# Add the KEDA Helm repository
helm repo add kedacore https://kedacore.github.io/charts
helm repo update

# Install KEDA into a dedicated namespace
helm install keda kedacore/keda \
  --namespace keda \
  --create-namespace
```

**Least-privilege SQS consumer IAM policy (verbatim from source):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ConsumeFromQueue",
      "Effect": "Allow",
      "Action": [
        "sqs:GetQueueAttributes",
        "sqs:GetQueueUrl",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:ChangeMessageVisibility"
      ],
      "Resource": "arn:aws:sqs:us-east-1:123456789012:orders-queue"
    }
  ]
}
```

**TriggerAuthentication and ScaledObject (verbatim from source):**
```yaml
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: sqs-processor-auth
  namespace: workers
spec:
  podIdentity:
    provider: aws
---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: sqs-processor
  namespace: workers
spec:
  scaleTargetRef:
    name: sqs-processor
  pollingInterval: 10
  cooldownPeriod: 120
  minReplicaCount: 0
  maxReplicaCount: 30
  advanced:
    horizontalPodAutoscalerConfig:
      behavior:
        scaleDown:
          stabilizationWindowSeconds: 60
  triggers:
    - type: aws-sqs-queue
      authenticationRef:
        name: sqs-processor-auth
      metadata:
        queueURLFromEnv: QUEUE_URL
        awsRegion: us-east-1
        queueLength: "10"
        activationQueueLength: "1"
```

**Replica-calculation logic (verbatim from source):**
```
ApproximateNumberOfMessages
+ ApproximateNumberOfMessagesNotVisible
(+ delayed messages, if enabled)

desired replicas = ceil(outstanding messages / queueLength)
```

**Verified example outputs at `queueLength: "10"` (verbatim from source):**
```
-   0 messages → 0 pods
-   8 messages → 1 pod
-   25 messages → 3 pods
-   95 messages → 10 pods
```

**Manual verification procedure (verbatim from source):**
```
1. Send 50 messages to the SQS queue
2. Inspect the ScaledObject:
kubectl get scaledobject sqs-processor -n workers
3. Watch pod scaling:
kubectl get pods -n workers -w
4. Confirm pods scale back to zero after processing completes
```

**Troubleshooting-to-cause table (verbatim from source):**
```
No scale-out
-   Cause: Incorrect queue URL or IAM permissions
-   Check: kubectl describe scaledobject, KEDA operator logs

Too many pods
-   Cause: In-flight messages counted
-   Check: scaleOnInFlight, SQS visibility timeout

Never scales to zero
-   Cause: Delayed or unacknowledged messages
-   Check: Queue attributes and application behavior

HPA exists but no scaling
-   Cause: Authentication or metric fetch errors
-   Check: KEDA logs and fallback status
```

**Production tuning tips (verbatim from source):**
```
-   Choose queueLength based on throughput, not guesswork
-   Tune cooldown and HPA behavior separately – they control different scale-down paths
-   Enable fallback replicas for resilience if metrics become unavailable
-   Decide whether in-flight messages should count based on visibility timeout behavior
```

## Cross-References

- **Extends**: `source-notes/blog-cncf-running-self-hosted-llm-kubernetes-vllm.md` — that note's **Claim 4** establishes that scaling a self-hosted inference Deployment to zero preserves the PVC and cached weights, and **Claim 5** establishes that readiness arrives only after a multi-minute weight-fetch and engine-init cold start. It explicitly scopes out autoscaling. This source supplies the missing control loop that decides when to scale such a Deployment up and back to zero, and the cold-start finding raises the cost of both directions: over-scaling wastes scarce GPU capacity (Claim 5 here), while under-scaling leaves queue wait that the backlog signal was supposed to prevent (Claim 1 here).

- **Extends**: `source-notes/blog-cncf-kubernetes-health-checks-waking-services.md` — that note's **Claim 1** describes ambient health-check traffic being interpreted as a scale-up signal, so a scale-to-zero service wakes forever. This source is the queue-driven counterpart: KEDA reads backlog from the queue rather than inferring demand from inbound request traffic, so ordinary probes cannot activate the worker. The shared lesson is that the demand signal must represent outstanding *work*, not reachability. The contrast also bounds the claim: queue depth only helps when the queue is the sole admission path.

- **Extends**: `source-notes/docs-google-sre-handling-overload.md` — that note's **Claim 4** recommends configuring the autoscaler to trigger before load shedding, and **Claim 15** warns that an autoscaler scaling against shared quota can starve sibling services. This source provides the concrete metric and replica formula for the queue-worker case (Claims 2–4) plus the `maxReplicaCount` bound (Claim 9). It also operationalizes that note's **Claim 6** autoscaling kill-switch guidance: the troubleshooting table (Claim 11) and the fallback-replica tip (Claim 10) are the queue-specific failure modes an on-call engineer needs to recognize.

- **Extends**: `source-notes/docs-google-sre-reliable-data-processing-minimal-toil.md` — that note's **Claim 16** observes that event-based processing trades batch simplicity for freshness, and that a queue introduces an external dependency affecting the SLO. This source adds the autoscaling response to that dependency: queue depth becomes both the capacity signal and a failure domain (visibility timeout, in-flight accounting, metric-fetch outage). The batch-freshness SLO in that note measures whether work completed; backlog depth here measures whether work is accumulating faster than it drains, which is the leading indicator the freshness SLO lags.

- **Contradicts**: None. No existing note makes a claim about KEDA, `ScaledObject`, SQS queue-depth autoscaling, `activationQueueLength`, or the cooldown/stabilization-window split. Verified against `CONTRADICTIONS.md` (no `C-NNN` entries). No contradiction issue filed.

- **Novel**: First source note in the corpus on queue-depth autoscaling. Specifically new: (1) backlog as the demand signal for async workers, with the visible + not-visible + delayed definition; (2) the `ceil(outstanding / queueLength)` replica math and its worked example; (3) the `activationQueueLength` vs `queueLength` distinction; (4) the two independent scale-down paths (KEDA cooldown vs HPA stabilization window); (5) the four-row autoscaler troubleshooting table; (6) fallback replicas as protection against metric-fetch failure at `minReplicaCount: 0`.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability → Cost, capacity, and fallback patterns)**: Add a subsection on queue-driven worker autoscaling for batch inference, embedding backfills, and agent job queues. Recommend backlog (queue depth or oldest-message age) as the scaling signal rather than CPU/memory [Claim 1], show the `ceil(outstanding / queueLength)` shape [Claims 3–4], and require `queueLength` to be derived from measured sustainable drain rate per replica rather than copied [Claim 6]. Call out the two thresholds [Claim 7] and the two scale-down paths [Claim 8] as separate tuning exercises, and pair `maxReplicaCount` with the downstream dependency/quota analysis already in this chapter [Claim 9; source: docs-google-sre-handling-overload, Claim 15]. Cross-link the self-hosted vLLM note for cold-start cost.

- **Chapter 02 (Observability → Batch-pipeline health signals)**: Add backlog depth and oldest-message age as leading health signals alongside freshness. A worker can be "up" and fully utilized while the queue grows; freshness only notices after the SLO is already breached. Recommend dashboarding visible, in-flight, and delayed counts separately so an operator can tell real backlog from messages a consumer is holding [Claim 5].

- **Chapter 04 (Oncall and Toil → runbook material)**: Add the four-row troubleshooting checklist as the first-response runbook for queue-autoscaler incidents: no scale-out → queue URL/IAM; too many pods → in-flight accounting/visibility timeout; never scales to zero → delayed or unacknowledged messages; HPA present but no scaling → auth/metric-fetch failure and fallback status [Claim 11]. Add the explicit test "block metric access and confirm the queue still drains via fallback replicas" [Claim 10].

- **Chapter 05 (general framing)**: Keep the AI/LLM transfer explicit and conditional. The source contains no LLM content and no measured production results; do not cite it as evidence that backlog autoscaling improves LLM latency or cost. Cite it for the mechanics and the operational traps only.

## Extraction Notes

- Read the full article (single page, no substantive linked sub-pages needed). No paywall. The post is short (roughly 1,200 words) and all substantive content is in the manifests, formulas, troubleshooting table, and tuning tips, all extracted above. I did not follow the KEDA or AWS links because their product documentation is outside the scope of what this note claims.
- All quotes copied character-for-character from the rendered page. Markdown bold markers around tuning tips and troubleshooting headings were treated as formatting and omitted from quoted prose; the underlying text is unchanged. The en dash in "signal – not infrastructure utilization" and the British spelling "behaviour" in the conclusion are reproduced as rendered.
- `confidence_overall: emerging` — the KEDA mechanism and replica math are documented and reproducible, but the source supplies zero measurements (no throughput, cost, scale-up latency, or production case study), the tuning tips are prescriptions without derivations, and the LLM transfer is entirely ours. `queueLength: "10"` is recorded as the source's illustration, not a recommendation, per the Prospector's caveat.
- Related-notes candidates from `miner-related-notes.md`, each cited or dismissed per MINER.md §4:
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — dismissed; agent-platform security architecture on Kubernetes, no autoscaling or queue mechanics.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed; SLO granularity in retail/gaming, unrelated to worker scaling.
  - `docs-google-sre-eliminating-toil.md` — dismissed; toil definition and measurement, not autoscaling mechanics (the connection would be too generic to cite).
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — dismissed; imperative vs declarative change workflows; a `ScaledObject` is declarative but the note makes no claim about reconciliation or intended state.
  - `docs-google-sre-handling-overload.md` — cited (Claim 4, Claim 6, Claim 15 as described above).
  - `docs-google-sre-prodcast-03-01.md` — dismissed; SRE methodology and influence, unrelated.
  - `docs-litellm-batches-api.md` — dismissed; LiteLLM batch TPM/RPM accounting at submission time, not worker autoscaling or queue drain.
  - `blog-litellm-valkey-semantic-caching.md` — dismissed; semantic cache backend, unrelated.
  - `blog-cncf-linkerd-multicluster-federation.md` — dismissed; multi-cluster service federation, unrelated to single-cluster queue workers.
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` — cited (Claim 16, queue as an external dependency affecting the SLO).
- The triage's three overlapping notes were all read and cited: `blog-cncf-kubernetes-health-checks-waking-services.md`, `blog-cncf-running-self-hosted-llm-kubernetes-vllm.md`, and `docs-google-sre-handling-overload.md`. The vLLM note was checked for autoscaling content and has none, which is why the relationship is "extends" rather than overlap.
- Cross-reference claim numbers were re-read and verified against the cited notes before writing (MINER.md §4b). No contradiction found; no contradiction issue filed.
