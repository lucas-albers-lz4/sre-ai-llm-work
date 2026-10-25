---
source_url: https://www.cncf.io/blog/2026/07/21/platform-engineering-for-the-agentic-enterprise-managing-applications-resources-and-ai-agents
source_type: blog-post
title: "Platform engineering for the agentic enterprise: Managing applications, resources, and AI agents"
author: "Lakmal Warusawithana (WSO2, CNCF Member Post)"
date_published: 2026-07-21
date_extracted: 2026-10-25
last_checked: 2026-10-25
status: current
confidence_overall: anecdotal
issue: "#1719"
---

# Platform engineering for the agentic enterprise: Managing applications, resources, and AI agents

> A vendor-authored CNCF Member Post (by WSO2, tied to OpenChoreo) arguing that the agentic enterprise expands platform scope to three first-class entities (applications, resources, AI agents), makes AI agents first-class platform consumers served via interfaces like MCP with the same identity/scoped permissions/audit trail as humans, and treats context as a first-class platform capability — presented as an architectural proposal with no concrete evidence, metrics, or artifacts.

## Source Context

- **Type**: blog-post (CNCF Member Post — vendor-authored thought leadership)
- **Author credibility**: Lakmal Warusawithana (WSO2). Tied to OpenChoreo (CNCF Sandbox project stewarded by the author's employer). Evidence base: assertion only — no code, manifests, configs, benchmarks, metrics, cost/latency figures, adoption numbers, or incident postmortems. The only incident-flavored passage is a hypothetical ("an agent investigating a failed deployment"). Product illustration is limited to naming OpenChoreo ecosystem modules (Agent Manager, AI Gateway, sandboxing, evaluation frameworks) with no description of behavior.
- **Scope**: Covers platform evolution from human-developer-centric IDPs to serving both humans and AI agents; taxonomy of three entities (applications, resources, AI agents); interface symmetry with uniform governance; context as a first-class platform capability; OpenChoreo as a practical example. Does NOT cover implementation details, measurements, or concrete operational patterns beyond naming.

## Extracted Claims

### Claim 1: AI agents become first-class platform consumers alongside humans, and must be governed with the same identity, scoped permissions, and audit trail across different interfaces
- **Evidence**: Architectural assertion; no examples, no enforcement mechanism details, no metrics.
- **Confidence**: anecdotal
- **Quote**: "A developer using a portal, an SRE using a CLI/GitOps, and an AI agent invoking an MCP server may interact with the platform differently, but their actions should be governed through consistent security controls, policy boundaries, and operational guardrails."
- **Our assessment**: This is the clearest extractable contribution. The corpus treats MCP primarily as a hardening/credential-resolution concern (e.g. docs-litellm-a2a-agent-permissions, guide Ch06 MCP resolver material), while this post frames MCP as the platform's agent-facing interface deliberately symmetric with human-facing interfaces. The symmetry claim (same governance, different interfaces) is worth capturing as a framing principle, but with no concrete evidence in the source it remains a vendor proposal rather than settled practice.

### Claim 2: The platform must manage applications, resources, and AI agents as three first-class software entities; resources become the common foundation linking apps and agents
- **Evidence**: Taxonomic assertion; definitions given but no operational model, schema, or examples with concrete behavior.
- **Confidence**: anecdotal
- **Quote**: "Applications remain central to enterprise software. ... Resources provide the capabilities that make those applications possible. ... AI agents introduce a fundamentally different kind of software actor. ... Resources therefore become the common foundation that connects applications and AI agents within the enterprise software estate."
- **Our assessment**: The three-entity taxonomy is a naming frame. It overlaps with existing corpus discussions of agents as platform actors/deployment units, but the explicit triad "applications + resources + AI agents" as co-equal first-class entities with resources as the connecting substrate is a compact articulation. Still vendor-positioning with no evidence; treat as a conceptual model to name, not proof.

### Claim 3: Context is becoming a first-class platform capability — a shared model of deployment history, ownership, topology, dependencies, policies, operational history, and organizational knowledge that both humans and AI agents reason over
- **Evidence**: Architectural assertion contrasting descriptive telemetry (logs/metrics/traces/events tell what happened) with contextual understanding (why/how related); hypothetical example of an agent investigating a failed deployment. No implementation details, no measurements.
- **Confidence**: anecdotal
- **Quote**: "Traditional observability platforms already collect enormous amounts of operational data. Logs record events, metrics measure system behavior, traces reveal request flows, and events capture changes across infrastructure and applications. These signals remain essential, but they are fundamentally descriptive. They tell us what happened, but rarely explain why it happened or how one event relates to another."
- **Our assessment**: Strong overlap with blog-cncf-4-body-problem-sre-context (which argues context integration is the binding constraint, proposes four bodies of truth, substrate-before-agents, decision traces). This post makes a similar "context as substrate" argument but is less specific (no four-body taxonomy, no decision-trace schema, no substrate-before-agents ordering). It adds the symmetry point (context exposed via same model to humans and agents over different interfaces) which is adjacent; on the core "context is descriptive not explanatory" thesis it restates rather than extends the more detailed treatment in the StackGen note.

## Concrete Artifacts

None extractable. The source names OpenChoreo ecosystem modules (Agent Manager, AI Gateway, sandboxing, evaluation frameworks) but provides no code, YAML/manifests, configuration snippets, metrics, benchmarks, error traces, or operational procedures. All are product references without technical detail.

## Cross-References

- **Corroborates**: 
  - `source-notes/blog-cncf-4-body-problem-sre-context.md` (same "context is descriptive, not explanatory" / context-as-substrate framing; both vendor-authored CNCF Member Posts arguing context must come before/alongside agents). This post is less specific than the StackGen note.
  - `source-notes/blog-linsun-pod-deployment-unit-ai-agent.md` — agents treated as ordinary platform actors requiring integration with existing platform machinery rather than a wholly separate stack.
  - `source-notes/blog-linsun-sandboxing-agent-not-enough.md` — agents inherit platform concerns (isolation/governance) rather than being exempt from them.
  - `source-notes/docs-litellm-a2a-agent-permissions.md` — centralization of agent policy/authorization; this post extends that to "same governance across all interfaces (portal/CLI/GitOps/MCP)".
  - `source-notes/docs-litellm-a2a-agent-gateway.md` — AI gateway as control point for agent traffic/policy.
  - `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md` — centralizing agent control at a boundary with uniform policy.
- **Contradicts**: None identified.
- **Extends**: 
  - `source-notes/docs-litellm-a2a-agent-permissions.md` — reframes MCP from a hardening/credential-resolution problem to the agent-facing interface that must be symmetric with human interfaces under uniform governance.
- **Novel**: 
  - Explicit articulation of "applications + resources + AI agents" as three first-class entities with resources as the common foundation connecting them.
  - The interface-symmetry principle stated clearly: same identity, scoped permissions, audit trail regardless of interface (portal/CLI/GitOps for humans vs MCP for agents).

## Guide Impact

- **Chapter 03 (Runbooks and Agents / The emerging agent control plane)**: Consider noting the "three first-class entities" taxonomy (applications, resources, AI agents) and the implication that agent consumers change what the platform manages. The key point is interface symmetry with uniform governance — if the guide discusses agent access patterns, this post frames MCP as equivalent in policy requirements to human interfaces rather than a special case. Treat as a vendor framing; do not adopt wholesale without corroborating evidence.
- **Chapter 06 (Security and Trust)**: Reinforce that agent governance must be uniform across interfaces (portal/CLI/GitOps/MCP) with distinct identity, scoped permissions, and audit trails for each actor. This sharpens the existing MCP/hardening discussions by making symmetry an explicit principle. Still anecdotal; useful as a design principle to consider alongside more concrete enforcement patterns in the corpus.

## Extraction Notes

- Read the full article text (blog post). No sub-pages followed as they weren't substantive linked pages in the content; the post is self-contained.
- Pure architecture-positioning piece with vendor interest (WSO2/OpenChoreo). No concrete artifacts extracted — consistent with Prospector guidance.
- Overlap with `blog-cncf-4-body-problem-sre-context.md` is significant on context framing; treated as restatement rather than duplication, with the symmetry/interface points noted as the distinguishing (if thin) contributions.
- Confidence marked anecdotal overall per source quality (assertion-only, conflict of interest). Claims marked anecdotal accordingly.
