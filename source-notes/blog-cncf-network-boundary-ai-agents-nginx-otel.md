---
source_url: https://www.cncf.io/blog/2026/07/08/network-boundary-for-ai-agents-using-nginx-and-opentelemetry
source_type: blog-post
title: "Network boundary for AI agents using NGINX and OpenTelemetry"
author: Marko Sluga (F5)
date_published: 2026-07-08
date_extracted: 2026-10-04
last_checked: 2026-10-04
status: current
confidence_overall: emerging
issue: "#1584"
---
# Network boundary for AI agents using NGINX and OpenTelemetry

> A design pattern describing an architecture where NGINX serves as both reverse proxy and the sole permitted forward proxy for agent egress, with iptables dropping all other outbound traffic, and the NGINX OpenTelemetry module emitting a span per request to create an auditable egress trail.

## Source Context

- **Type**: blog-post (CNCF Member Post, vendor-adjacent practitioner design narrative)
- **Author credibility**: Marko Sluga works for F5, which stewards NGINX. The article presents a hands-on design pattern (tested in a single-node Kubernetes lab with four workloads) and closes by discussing how the forward-proxy capability relates to NGINX Ingress Controller and NGINX Gateway Fabric. The author is a practitioner reporting on a passion project (OpenClaw context).
- **Scope**: Covers network enforcement for AI agents using dual-role NGINX (reverse proxy for ingress, forward proxy for all outbound agent traffic) with iptables enforcing "no second path" (all non-proxy egress dropped), and NGINX's native OpenTelemetry module emitting spans per request routed via OTel Collector to audit/observability systems. Also notes limitations: network control is not agent-intent understanding; the proxy is another component needing hardening. Does NOT include code/YAML snippets, metrics/latency numbers, or a public repo reference in the article text.

## Extracted Claims

### Claim 1: The boundary must be architectural (enforced regardless of application policy)
- **Evidence**: The article describes placing a single NGINX instance as both reverse proxy and mandatory forward proxy, with iptables rules dropping all other egress traffic so the agent cannot route traffic around the proxy.
- **Confidence**: emerging
- **Quote**: "We can control the flow with iptables rules that drop all other egress traffic, so there is no second path. That makes the boundary a property of the architecture, not a policy we hope the application respects."
- **Our assessment**: This is a useful design principle for agent containment. Rather than relying on application-level allowlists (which an agent with sufficient privileges/tool access might bypass), the network layer enforces egress only through the designated proxy. It's sound as a defense-in-depth control. However, the evidence is descriptive (no concrete iptables rules shown, no test demonstrating enforcement against bypass attempts).

### Claim 2: A single proxy instance can serve dual roles (ingress reverse proxy and egress forward proxy)
- **Evidence**: The flow description has NGINX on both sides — reverse proxy for inbound TLS-terminated traffic to the agent, and forward proxy for all outbound agent requests.
- **Confidence**: emerging
- **Quote**: "Because NGINX sits on both sides of the flow, it performs the reverse proxy role for inbound traffic, terminates TLS, and forwards requests for the agent. For outbound traffic, the same instance acts as a forward proxy through which every agent request must pass."
- **Our assessment**: The pattern is concrete and operationally convenient (single control point). Co-locating ingress and egress control in one proxy simplifies correlation of user interactions to outbound calls. The trade-off (blast radius if proxy compromised, throughput bottleneck) is implied but not quantified.

### Claim 3: Every outbound agent request becomes an audited span at the proxy
- **Evidence**: NGINX's native OpenTelemetry module emits an OTEL span for every request; spans are routed via OpenTelemetry Collector to audit log, Jaeger, Grafana, or SIEM.
- **Confidence**: emerging
- **Quote**: "The NGINX native OpenTelemetry module allows us to emit an OTEL span for every request. Now we are getting traffic flow observability using a format that our tooling already understands, allowing us to correlate user interactions with the external calls made by the agent on their behalf. An OpenTelemetry Collector can persist those spans to an audit log, or we can feed them into observability and security tooling such as Jaeger, Grafana, or a SIEM platform."
- **Our assessment**: The key value is correlation — linking a user interaction to external calls the agent makes on their behalf. This is distinct from application logs (which may not capture raw egress decisions or be bypassable) and from LLM-gateway traces (which focus on model/tool calls rather than enforced network egress). The span-per-request audit plane is plausible, but no span schema fields or example spans are provided in the article.

### Claim 4: Network control differs from understanding agent intent
- **Evidence**: The article explicitly distinguishes between controlling/observing network behavior and understanding what an agent intends to do with allowed destinations.
- **Confidence**: settled (stated limitation)
- **Quote**: "This approach focuses on controlling and observing network behavior, not understanding agent intent. Restricting where an agent can communicate does not guarantee that its decisions are correct or safe."
- **Our assessment**: This is an important caveat. The boundary enforces *who/where* the agent can call (egress allowlist at network layer), not *why* or whether the call is harmful given the context. The author correctly frames this as one layer in a defense-in-depth stack, not a complete solution.

### Claim 5: The proxy introduces its own operational/security surface
- **Evidence**: The design adds a proxy component that must itself be secured and monitored as part of the architecture.
- **Confidence**: settled (stated limitation)
- **Quote**: "Additionally, proxy-based enforcement introduces another operational component that must be secured and monitored. Like any control plane, it must be hardened against compromise and failure."
- **Our assessment**: This is a straightforward but necessary acknowledgment. The control becomes a potential choke point and attack surface. The tradeoff is acceptable if the auditability/deny-by-default property is valued, but the article doesn't quantify the operational burden.

### Claim 6: The pattern generalizes beyond the specific implementation
- **Evidence**: The author states the approach could be implemented with other proxy technologies, service mesh egress gateways, or network policy solutions; notes NGINX Ingress Controller and Gateway Fabric will inherit forward-proxy capabilities over time.
- **Confidence**: emerging
- **Quote**: "While this implementation uses NGINX as the enforcement point, similar patterns could also be implemented using other proxy technologies, service mesh egress gateways, or network policy solutions."
- **Our assessment**: This correctly positions the pattern as portable. The core architectural properties are: sole egress path (deny alternatives at network layer), forward proxy as enforcement point, and per-request observability/audit at that boundary. The choice of proxy is implementation detail.

## Concrete Artifacts

### Artifact 1: Deployment context (lab validation)
- **Description**: Single-node Kubernetes cluster running four workloads in the same namespace: NGINX, Ollama, OpenClaw, and an OpenTelemetry Collector.
- **Type**: experimental deployment description
- **Attribution**: Described in "Validating the Idea" section of the article.
- **Notes**: No manifests, Helm charts, or configs provided. The setup uses consumer NVIDIA GPU hardware (mentioned in accompanying context from issue triage). This confirms the pattern was exercised in a real lab, but is not reproducible from the article alone.

### Artifact 2: Enforcement mechanism
- **Description**: Dual-role NGINX (reverse proxy + forward proxy) with iptables dropping all other egress traffic so "there is no second path."
- **Type**: architectural mechanism
- **Attribution**: Main body of article.
- **Notes**: The article does not show iptables rules or NGINX forward-proxy config. Extracted as the core enforcement property.

### Artifact 3: Audit/observability mechanism
- **Description**: NGINX native OpenTelemetry module emits OTEL span per request; spans flow through OTel Collector to audit log / Jaeger / Grafana / SIEM for correlation of user interaction to agent's external calls.
- **Type**: observability/audit pattern
- **Attribution**: Main body of article.
- **Notes**: Span schema not specified; correlation mechanism described at high level.

## Cross-References

- **Corroborates**:
  - `source-notes/blog-linsun-pod-deployment-unit-ai-agent.md` — The closest corpus neighbor on the *enforcement locus*. Linsun's Claim 16 makes actor egress default-deny and per-actor, subject to an explicit policy rule; Claim 2 notes that "Existing network policies, admission policies, and security controls continue to work without modification" once the agent is a Pod; Claim 9 quotes "native zero-trust kernel and network isolation." All three independently put the enforcement point at the network layer, the same locus this note occupies with its forward proxy + iptables deny-all-other. The two sources also agree that a funneled egress path is where agent telemetry lands.
  - **Tension to record (not a contradiction):** linsun's Claim 12(c) documents that funneling actor telemetry through an egress gateway *degrades* span attribution — a collector enriching by source IP attaches the gateway's Pod identity to the actor's spans, and "The collector sees the gateway, not the actor." This note presents egress-funneled spans as the audit win (Claim 3). Both are true at once: the network boundary *provides* an audit plane, but the proxy/gateway's own transport identity does not *preserve* actor identity. The combined guide lesson is that an egress-boundary span must carry actor identity as an explicit attribute stamped by the caller or an injecting layer, not rely on the source identity of the connection that happened to carry it. That is the same failure class as linsun Claim 12(a) and the corpus's general pattern that agent identity must be threaded explicitly at every hop rather than inferred from the transport (`docs-litellm-a2a-agent-gateway.md` Claim 2 — trace grouping and spend attribution are a forwarding obligation, not a gateway guarantee).
- **Contradicts**: None identified. The pattern complements rather than contradicts application-layer guardrails (and explicitly acknowledges intent vs network control).
- **Extends**:
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` — This focuses on instrumenting agent internals (LLM/tool spans, conversation IDs, Agent Timeline) for debugging. The CNCF source extends by adding a *network enforcement boundary* plus per-request proxy spans as an audit plane. Both use OTel; the former is telemetry inside the agent execution graph, the latter is telemetry at the egress control point.
- **Novel**:
  - The "sole egress path enforced at network layer via forward proxy + iptables deny-all-other" pattern for autonomous agents is not represented in existing source notes (`grep -rli "forward proxy" source-notes/` returns only this note). **Scope correction:** the *general* idea of an egress boundary carrying agent telemetry is already in the corpus — `source-notes/blog-linsun-pod-deployment-unit-ai-agent.md` Claim 12(c) documents agent telemetry routed through an egress gateway. The novelty here is the specific *enforcement* mechanism (one NGINX instance as both reverse and forward proxy, with kernel-level denial of every other egress path), not egress-as-an-audit-plane.
  - The explicit framing "boundary is a property of the architecture, not a policy we hope the application respects" as applied to agent egress.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Recommend adding content about network-layer egress boundaries for AI agents as defense-in-depth. This source provides the concrete enforcement architecture (dual-role proxy as sole egress path with iptables denying alternatives) that complements existing guardrail content. The distinction between "controlling network behavior" vs "understanding agent intent" (Claim 4) is important framing.
- **Chapter 02 (Observability)**: The pattern of emitting per-request spans at the egress boundary (Claim 3) and feeding them into OTel Collector for correlation/audit is relevant. It shows how network-layer telemetry can complement application-layer agent tracing (see extends to Honeycomb note) to create a more complete audit trail.
- **Chapter 05 (LLM Ops Reliability)**: The boundary as architectural property supports operational safety; the stated limitations remind operators about the proxy as an additional component requiring hardening and monitoring.

## Extraction Notes

- Source is a vendor-adjacent blog post (F5 author, CNCF Member Post). Claims are presented as a design pattern from lab testing; no quantitative evidence (latency, throughput, error rates, coverage of bypass attempts) is provided. Confidence is marked `emerging` accordingly.
- The article mentions "OpenClaw Network Boundary" repo in passing context (per issue triage), but the URL is not present in the extracted text shown; no repo link appears in the article's main content as rendered. We did not fabricate a repo URL.
- Key phrases quoted verbatim where they capture the core architectural claims (especially the "no second path / property of the architecture" and the audit/span correlation). All quotes match the source text.
- **Claim 3 quote re-verified contiguous (Assayer follow-up)**: re-fetched the source and extracted the paragraph HTML. The Claim 3 quote is a single contiguous paragraph, character-for-character, with no elision — the three sentences ("The NGINX native OpenTelemetry module allows us to emit an OTEL span for every request. Now we are getting traffic flow observability ... An OpenTelemetry Collector can persist those spans to an audit log ...") appear in that order with no intervening sentence. No ellipsis is required. Claims 1 and 2 quotes were re-checked in the same pass and are also contiguous.
- Cross-references note overlap with Honeycomb's agent OTel instrumentation (complementary) and with `blog-linsun-pod-deployment-unit-ai-agent.md` (same network-layer enforcement locus, plus the recorded tension that an egress funnel degrades span attribution). The forward-proxy + iptables mechanism specifically remains unique in the corpus; the broader "egress boundary as an audit plane" idea does not.
