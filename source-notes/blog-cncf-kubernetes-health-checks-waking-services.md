---
source_url: https://www.cncf.io/blog/2026/07/29/your-kubernetes-health-checks-are-accidentally-waking-your-services-heres-the-fix
source_type: blog-post
title: "Your Kubernetes health checks are accidentally waking your services. Here’s the fix."
author: "KubeElasti Maintainers"
date_published: 2026-07-29
date_extracted: 2026-10-23
last_checked: 2026-10-23
status: current
confidence_overall: emerging
issue: "#1852"
---

# Your Kubernetes health checks are accidentally waking your services. Here’s the fix.

> Ambient health-check traffic — cloud load balancers, ingress-replicated
> Kubernetes probes, service-mesh checks, and uptime monitors — is routinely
> interpreted by scale-to-zero resolvers as real demand, so workloads wake
> forever and never deliver idle savings; the durable pattern is to match and
> answer synthetic probes at the interception tier that is already in the path
> while a service sits at zero replicas, not to repoint or duplicate health
> endpoints.

## Source Context

- **Type**: blog-post (CNCF Project Post, vendor-authored by the KubeElasti
  maintainers). CNCF highlights KubeElasti and Kubernetes.
- **Author credibility**: The KubeElasti maintainers are the authors of the
  scale-to-zero project whose `ProbeResponse` feature the post announces. They
  understand the resolver mechanics they describe, but every product-specific
  claim (zero overhead, zero-cost interception, genuine idle time) is
  first-party and unvalidated by an independent deployment.
- **Scope**: Explains why scale-to-zero fails behind active health checking,
  names the three classes of probe traffic, argues against the conventional
  fixes, and documents the `ProbeResponse` matching layer with a YAML example,
  matching semantics, architecture claims, example workloads, and an audit
  checklist. Does NOT include measured savings, production telemetry,
  benchmarks, failure data, or evidence from workloads with real request
  queuing at the moment of wake. The "0% of potential savings" figure is
  asserted, not measured.

## Extracted Claims

### Claim 1: A healthy scale-to-zero configuration can be defeated entirely by ordinary health-check traffic, because the resolver reasonably treats any request as a scale-up signal
- **Evidence**: The author walks through the default production sequence: service scales down after inactivity, the LB is health-checking every 30 seconds, the last pod terminates, the service points at the resolver, the LB sends `GET /healthz`, and the resolver begins scaling up.
- **Confidence**: settled (mechanism), anecdotal (frequency/impact in any given fleet)
- **Quote**: "Then you deploy it in production and discover a problem nobody warned you about: your load balancer doesn’t know your pods are intentionally gone. It keeps sending health checks. Every health check hits your resolver. Your resolver, doing its job, interprets traffic as a scale-up signal. Your pods wake up."
- **Our assessment**: The core failure loop is real and does not depend on KubeElasti: any request-driven activator treats liveness/readiness traffic as demand. This is a design-level conflict, not a bug, and the post is right to frame it that way.

### Claim 2: The conflict is structural — load balancers need proof a service is alive while autoscalers need proof it is dead
- **Evidence**: Argued from the architecture of cloud load balancers and Kubernetes autoscaling, and from the history of zero-replica deployments behind cloud LBs.
- **Confidence**: settled (as a systems framing)
- **Quote**: "This isn’t a KubeElasti bug. It’s a fundamental tension in how modern infrastructure is stitched together. Load balancers need to know a service is alive. Kubernetes autoscalers need to know a service is dead. These two things have been at odds since the first team tried running zero-replica deployments behind a cloud load balancer."
- **Our assessment**: Buy the framing. Availability checking and demand detection are both "is this endpoint reachable?" questions asked by different control planes with opposite desired answers. Scale-to-zero exposes the ambiguity.

### Claim 3: Probe traffic comes from three independent sources — cloud load balancers, Kubernetes liveness/readiness probes replicated at ingress, and platform monitoring such as Istio, Prometheus Blackbox Exporter, or Datadog synthetics
- **Evidence**: The post enumerates the three classes and notes that the third class does not distinguish a degraded service from a deliberately idle one.
- **Confidence**: emerging (a useful taxonomy; no measured probe rates or fleet data)
- **Quote**: "None of them distinguish between a degraded service and a deliberately idle one."
- **Our assessment**: The taxonomy is the durable part of this post and matches how production clusters accumulate probes: each tool is configured by a different team for a different purpose, and none knows the service is intentionally at zero. Treat it as an audit checklist, not an exhaustive list.

### Claim 4: Organizations that configure scale-to-zero can realize none of the expected savings because their monitoring stack never lets the workload stay at zero
- **Evidence**: Asserted as the typical outcome; no measurements, fleet data, or case studies are supplied.
- **Confidence**: anecdotal
- **Quote**: "The result: teams that configure scale-to-zero achieve exactly 0% of the potential savings because their monitoring stack never lets them stay at zero."
- **Our assessment**: Directionally credible — the loop in Claim 1 necessarily prevents sustained zero — but the "exactly 0%" figure is rhetorical. The guide should carry the mechanism and the diagnostic, not the number.

### Claim 5: The conventional "separate the health check onto another service" fix fails because teams do not control cloud-LB probe configuration, split routing drifts, and the health endpoint is the application endpoint
- **Evidence**: Three named reasons: cloud LBs check the registered IP/port, routing separation adds unmaintained complexity, and `/healthz` is itself the path being routed.
- **Confidence**: emerging (reasoned argument, no experiments comparing the alternatives)
- **Quote**: "First, you don’t always control the health check configuration. Cloud load balancers check the IP and port your service is registered on. You can’t tell an AWS ALB to use a different backend for /healthz."
- **Quote**: "Third, and most importantly: the health check endpoint IS your application endpoint. The /healthz path is the path. Rerouting it defeats the purpose."
- **Our assessment**: The first and second objections are concrete operational constraints (platform teams often cannot change an ALB target group's probe path). The third is partly vendor framing — a separate always-on probe responder is a legitimate pattern even if it duplicates an endpoint. Keep the constraints, discount the absolutism.

### Claim 6: An always-on proxy solves interception but imposes a permanent latency and architectural cost
- **Evidence**: Describes the alternative architecture and explicitly labels the trade-off.
- **Confidence**: emerging
- **Quote**: "Other tools solve this by keeping a proxy permanently in the request path — even when the service is running. You trade latency for the ability to intercept health checks at all times."
- **Our assessment**: Fair characterization of the trade-off space: interceptability vs. steady-state overhead. The post's own alternative is only better if interception at zero replicas is genuinely free, which is a vendor claim (see Claim 12).

### Claim 7: The proposed gate answers matching probe requests directly at the resolver, with first-match-wins rules over method, path (Exact/PathPrefix/Regex), headers, and query parameters
- **Evidence**: Documented feature behavior plus the YAML artifact reproduced below.
- **Confidence**: emerging (feature documentation from the vendor)
- **Quote**: "If a request matches a probe rule, the resolver answers it directly — with the status code and body you define — and never notifies the operator. The workload stays at zero. The health check receives a 200 OK. Everyone is happy."
- **Our assessment**: The generalizable pattern — classify synthetic probe traffic at the tier that already intercepts zero-replica traffic, answer it locally, and leave the real-demand path unchanged — is sound. The specific rule schema is KubeElasti's, and other activators (Knative, KEDA, OpenFaaS, custom resolvers) would implement the same pattern differently.

### Claim 8: Unmatched requests retain normal scale-to-zero semantics, so the gate does not suppress real demand
- **Evidence**: Rule evaluation order and explicit design statement.
- **Confidence**: emerging
- **Quote**: "Rules are evaluated top to bottom. First match wins. If no rule matches, normal behavior applies — the request queues and triggers a scale-up."
- **Quote**: "This design is intentional. ProbeResponse is a gate, not a replacement for scaling. Real traffic still wakes your service. Synthetic health traffic stays synthetic."
- **Our assessment**: This is the correct safety property to insist on. A probe-response layer that swallowed unmatched traffic would be a silent outage generator; first-match-wins with a default-to-scale path keeps the failure mode visible. Verify this property in any implementation before adopting the pattern.

### Claim 9: Probe matching is active only while the service is at zero replicas, so it adds no steady-state request-path hop
- **Evidence**: Architecture description: the resolver is in the path in proxy mode and out of the path in serve mode.
- **Confidence**: emerging (architectural claim from the vendor)
- **Quote**: "ProbeResponse rules only apply when the resolver is active, which is only when your service is at zero replicas."
- **Quote**: "No latency penalty when your service is running"
- **Our assessment**: Plausible if the resolver truly leaves the data path once pods are active, and the pattern's value depends on it. But this is exactly the kind of "zero overhead" claim that needs independent verification under load; do not state it as settled in the guide.

### Claim 10: The diagnostic signature of health-check-driven wake loops is scale-up events in logs with no corresponding user traffic
- **Evidence**: Author's description of what deployments without probe handling look like.
- **Confidence**: emerging
- **Quote**: "The logs show scale-up events but no corresponding user traffic."
- **Our assessment**: High-value operational tell, and cheap to instrument: correlate activation events with request-rate or ingress traffic. This belongs in a runbook even for teams that never adopt KubeElasti.

### Claim 11: GPU pods are a primary beneficiary because cold-start fear plus health-check-triggered wakeups keeps expensive accelerators running
- **Evidence**: Asserted scenario; no GPU utilization, cost, or cold-start measurements.
- **Confidence**: anecdotal
- **Quote**: "ProbeResponse makes genuine GPU idle time achievable — answer the health check from the resolver, keep the GPU pod terminated until real inference traffic arrives."
- **Our assessment**: The economic logic is strong — GPU and per-instance-licensed workloads have the largest gap between idle cost and cold-start tolerance — but the post supplies no numbers. Use this as motivation for the pattern, not as evidence of savings.

### Claim 12 (vendor claim): The interception layer is "genuinely zero-cost" because it reuses the resolver already present during proxy mode
- **Evidence**: Author's architecture argument: no extra hop, no additional component, no always-on proxy.
- **Confidence**: anecdotal
- **Quote**: "It’s genuinely zero-cost when your service is active."
- **Our assessment**: Do not carry this into the guide as fact. It is a reasonable design goal and may be true for KubeElasti's data path, but "zero-cost" is unmeasured and the vendor is describing its own feature. The transferable claim is narrower: interception at an existing zero-replica choke point avoids adding a new always-on hop.

### Claim 13: Before configuring probe matching, teams should audit four probe sources — cloud LB config, ingress annotations (NGINX/Traefik/Istio), uptime monitors (Prometheus Blackbox/Datadog synthetics), and service-mesh checks (Istio/Linkerd)
- **Evidence**: The "Practical Recommendations" checklist, which also advises matching response bodies exactly and using headers/query params to disambiguate shared paths.
- **Confidence**: emerging (practitioner checklist, no validation data)
- **Quote**: "Before configuring ProbeResponse, audit your health check sources:"
- **Quote**: "Use header and query parameter matchers to disambiguate health checks from real traffic when they share the same path. Some monitoring tools set identifying headers you can use for this purpose."
- **Our assessment**: This checklist is the most reusable artifact in the post and is independent of the product. Matching on path alone is fragile when synthetic and real traffic share `/healthz`; header/query disambiguation (for example a monitor-specific User-Agent or query token) is the safer rule.

## Concrete Artifacts

**Probe-response rule configuration (verbatim from source):**
```yaml
probeResponse:
  - method: GET
    path:
      type: PathPrefix
      value: /healthz
    response:
      status: 200
      body: '{"ok":true}'
  - method: HEAD
    path:
      type: Exact
      value: /ready
    response:
      status: 204
      body: '{}'
```

**Matching semantics (verbatim from source):**
```
-   HTTP method (GET, HEAD, POST, etc.)
-   Path matching: Exact, PathPrefix, or RegularExpression
-   Header matchers (all ANDed)
-   Query parameter matchers (all ANDed)
```
Rules are evaluated top to bottom; first match wins; unmatched requests queue and trigger a scale-up.

**Pre-adoption audit checklist (verbatim from source):**
```
1.  Check your cloud load balancer health check configuration — identify the path, method, and frequency.
2.  Review your Kubernetes ingress annotations — NGINX, Traefik, and Istio all have configurable health check behaviors.
3.  Check your uptime monitoring — if you’re using Prometheus Blackbox Exporter, Datadog synthetic monitors, or any external uptime tool, note which endpoints they probe.
4.  Review your service mesh configuration — Istio, Linkerd, and similar tools often run health checks as part of their sidecar behavior.
```

**Key takeaways (verbatim from source):**
```
-   Health checks are the most common reason scale-to-zero fails to deliver savings in production
-   ProbeResponse lets the KubeElasti resolver answer configured probe requests directly, without triggering scale-up
-   Rules match on method, path (Exact/PathPrefix/Regex), headers, and query params
-   ProbeResponse only applies in proxy mode — zero overhead when your service is running
-   GPU workloads, licensed software, and internal services gain the most from this feature
-   Audit your health check sources before configuring — cloud LBs, service meshes, uptime monitors, and ingress controllers all probe independently
```

## Cross-References

- **Extends**: `source-notes/blog-cncf-running-self-hosted-llm-kubernetes-vllm.md`
  — Claim 4 establishes that scaling to zero preserves the PVC and cached
  weights, and Claim 5 that readiness arrives only after a multi-minute cold
  start. This source supplies the missing half of the scale-to-zero story:
  even a correctly configured idle Deployment may never reach zero because
  probes keep reactivating it, and each reactivation pays that cold-start
  cost again.
- **Extends**: `source-notes/docs-google-sre-handling-overload.md` — Claim 5
  describes "lame duck" mode, where a backend deliberately fails health
  checks so the load balancer removes it. This source is the inverse case:
  health checks are a control signal that can *cause* capacity to appear.
  Together they support a general rule that health-check semantics are an
  availability control plane and must be designed, not assumed.
- **Extends**: `source-notes/docs-google-sre-address-cascading-failures.md`
  — Claim 9 names cold caches as a startup vulnerability: newly started
  servers underperform until warmed. This source adds a recurring-trigger
  mechanism: probe-driven wake loops force repeated cold starts, so the
  vulnerability is exercised continuously rather than only after an incident.
- **Corroborates**: `source-notes/failure-cncf-kubeflow-cilium-60-idle-gpus.md`
  — Claim 4 treats GPU utilization as the observable signal for wasted
  accelerator spend. This source describes a different root cause (probe
  traffic preventing zero replicas, rather than topology mismatch), but both
  arrive at the same SRE lesson: idle GPU cost is invisible unless utilization
  and activation events are instrumented.
- **Novel**: The corpus has no existing note on health-check traffic defeating
  scale-to-zero, on the three-source probe taxonomy, or on answering synthetic
  probes at a zero-replica interception tier. This is the first treatment of
  ambient monitoring traffic as a demand-side actor.

## Guide Impact

- **Chapter 02 (Observability)**: Add a subsection on monitoring traffic as an
  actor in the system. Recommend auditing all probe sources (cloud LB, ingress
  annotations, uptime monitors, service mesh) and distinguishing synthetic
  health traffic from user traffic in dashboards and alerts. Add the
  diagnostic: correlate activation/scale-up events with request rate; a
  scale-up with no user traffic is a probe loop, not demand. Cite this note,
  not the product feature.
- **Chapter 05 (LLM Ops Reliability)**: In the cost/capacity material, add a
  rule for GPU and licensed workloads: before claiming scale-to-zero savings,
  prove the workload actually reaches zero. Where it cannot, gate matching
  synthetic probes at the tier already intercepting zero-replica traffic,
  with first-match-wins rules and a default-to-scale path for unmatched
  requests. Mark the mechanism as emerging and the KubeElasti YAML as
  illustrative, not a recommendation.
- **Chapter 01 (Incident Response)**: Add "activation events without
  corresponding user traffic" to the runbook for unexpected resource
  consumption or cost spikes, alongside the existing cold-start and overload
  checks.

## Extraction Notes

- Read the full post (single page, no substantive linked sub-pages needed).
  Product behavior is attributed to KubeElasti throughout; no independent
  KubeElasti documentation was followed because the product-specific claims
  are out of scope for the guide.
- The post provides no metrics, benchmarks, production case study, or failure
  data. `confidence_overall` is therefore `emerging`: the conflict mechanism
  and audit checklist are durable and consistent with how activators work,
  while savings and zero-overhead claims remain vendor assertions.
- Related-notes candidates reviewed per MINER.md §4:
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed; retail/gaming
    SLO granularity, no scale-to-zero or probe content.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — dismissed; agent
    platform security and Kubernetes deployment mechanics, no probe interaction.
  - `docs-google-sre-prodcast-03-01.md` — dismissed; SRE methodology and
    organizational influence, not workload lifecycle.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — dismissed;
    imperative vs. declarative change workflows, unrelated.
  - `docs-google-sre-on-call.md` — dismissed; pager load and alerting hygiene,
    unrelated to probe-driven activation.
  - `docs-google-sre-slo-engineering-case-studies.md` — dismissed; SLO adoption
    case studies, no idle/activation mechanism.
  - `docs-google-sre-handling-overload.md` — cited (Claim 5, lame duck).
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` — dismissed;
    batch-job reliability, not request-driven serving.
  - `docs-google-sre-reliable-product-launches.md` — dismissed; launch process
    and checklists, unrelated.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — dismissed; SRE
    transferability and scale shock, no serving-lifecycle content.
- Additional notes found by searching `source-notes/`: the vLLM, Kubeflow/Cilium
  idle-GPU, and cascading-failures notes cited above. `blog-cncf-goodput-more-than-throughput-llm-serving.md`
  was considered but not cited: its cost/efficiency angle concerns latency
  targets under load, not idle workload activation.
- No contradiction found with an existing note; this source describes a
  different root cause for idle GPU spend than `failure-cncf-kubeflow-cilium-60-idle-gpus.md`.
