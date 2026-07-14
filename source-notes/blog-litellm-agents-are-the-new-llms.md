---
source_url: https://docs.litellm.ai/blog/agents-are-the-new-llms
source_type: blog-post
title: "Agents Are the New LLMs: A Unified Agent Control Plane"
author: "Krrish Dholakia (CEO, LiteLLM)"
date_published: 2026-06-10
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#97"
---

# Agents Are the New LLMs: A Unified Agent Control Plane

> A forward-looking strategy post from LiteLLM's CEO laying out the thesis that
> agent infrastructure is separating into models → harnesses → runtimes, and that
> a fourth "unified agent control plane" layer will emerge to route and govern
> agent work across heterogeneous runtimes — the AI gateway moving "up the stack"
> from routing model calls to routing agent sessions.

## Source Context

- **Type**: blog-post (vendor strategy / vision piece), tagged `ideas`,
  `harnesses`, `ai-gateway`, `agents`.
- **Author credibility**: Krrish Dholakia is CEO of LiteLLM, the company behind
  the open-source LLM gateway/proxy. The claims are a vendor's architectural
  thesis and product-direction signal (for LiteLLM Agent Platform / LAP), not a
  practitioner experience report with measured outcomes. Credibility is high for
  *what LiteLLM is building and seeing in its own customer base*, but the
  broader "fourth layer will emerge" prediction is a forecast, not established
  fact.
- **Scope**: Covers the proposed layered agent stack, the motivation (multi-runtime
  fragmentation), why a registry is insufficient (invocation heterogeneity), the
  analogy to the LLM-gateway pattern, the gateway-evolution thesis, and a brief
  description of LAP. Does NOT cover: concrete code, deployable config,
  production metrics, or independent corroboration. LAP is explicitly stated to
  be pre-v0 / experimental.

## Extracted Claims

### Claim 1: Agent infrastructure is separating into three layers (models, harnesses, runtimes) and a fourth — the unified agent control plane — will emerge
- **Evidence**: Author's stated belief / forecast. The post opens with this as its
  central thesis and repeats the four-layer framing throughout. No external data
  or metrics are offered to support the "will emerge" prediction.
- **Confidence**: emerging
- **Quote**: "Agent infrastructure is already separating into three layers: models, harnesses, and runtimes. We believe a fourth layer will emerge: the unified agent control plane. This will allow calling agents living in different agent runtimes, all from 1 place."
- **Our assessment**: The three-layer observation (models / harnesses / runtimes)
  is a reasonable description of current market structure. The "fourth layer will
  emerge" claim is a vendor forecast — plausible and internally consistent, but
  unproven. Treat as a directional signal, not a settled architecture fact.

### Claim 2: Companies will not run every agent on one runtime; different agent types live on different runtimes, which creates demand for a unifying control plane
- **Evidence**: The author grounds this in observed fragmentation — LiteLLM's own
  team reportedly builds across Claude Managed Agents, N8N, and Cursor, and
  expects coding agents on Bedrock AgentCore / Claude Managed Agents, data agents
  in Elastic / Databricks / Snowflake, and internal workflow agents on custom
  infrastructure.
- **Confidence**: emerging
- **Quote**: "The reason is that companies will not run every agent on one runtime. Coding agents may run on Bedrock AgentCore or Claude Managed Agents. Data agents may run inside Elastic, Databricks, or Snowflake. Internal workflow agents may run on custom infrastructure."
- **Our assessment**: This is the most grounded claim in the post — it reports a
  real pattern (heterogeneous agent runtimes per team/use-case). Even if the
  specific vendors shift, the structural observation that agents are not
  single-runtime is credible and is the load-bearing premise for the whole
  control-plane thesis.

### Claim 3: A registry of agents is insufficient — the hard problem is invocation across heterogeneous runtime APIs
- **Evidence**: The post argues "Anyone can build a list of agents" and that the
  difficulty is not cataloging but calling. Agent runtimes expose similar
  primitives (agents, sessions, events, tools) but through different APIs.
- **Confidence**: emerging
- **Quote**: "But a registry alone is not enough. Anyone can build a list of agents."
- **Quote**: "The harder problem is invocation. Agent runtimes expose similar primitives — agents, sessions, events, tools — but they do not expose them through the same APIs."
- **Our assessment**: A sound architectural insight. The gap between "I know this
  agent exists" and "I can invoke it uniformly" is real and mirrors the early
  LLM-landscape problem (many model APIs, one gateway). This is the core
  technical justification for a control plane and is the most reusable takeaway.

### Claim 4: The control plane must manage agent runtimes, schedules, memory, and sessions — not just list agents
- **Evidence**: Stated as the consequence of the invocation gap: to actually use
  agents in one place, the control plane has to own lifecycle concerns
  (runtimes, schedules, memory, sessions) that today live inside each runtime.
- **Confidence**: emerging
- **Quote**: "So if you want one place to actually use these agents, not just list them, the control plane has to manage agent runtimes, schedules, memory, and sessions."
- **Our assessment**: This is the concrete responsibility list for the proposed
  layer. It is a sensible decomposition (lifecycle/scheduling/memory/sessions are
  exactly the stateful concerns that differ across runtimes), but it is asserted,
  not demonstrated — LAP is pre-v0, so there is no evidence the decomposition
  actually works at scale.

### Claim 5: The agent-control-plane pattern mirrors the LLM-gateway pattern; the primitive shifts from the model call to the agent session
- **Evidence**: Direct analogy to LiteLLM's own history: companies needed one
  interface to call many models, not just a catalog. The post argues the same
  dynamic now applies to agents, with the unit of abstraction changing.
- **Confidence**: emerging
- **Quote**: "This is the same pattern LiteLLM saw with models. Companies did not just need a catalog of models. They needed one interface to call them. The only change, is that the primitive is now the agent session, not the model call."
- **Our assessment**: The analogy is the post's strongest rhetorical device and is
  logically coherent: gateways standardized model access; a control plane would
  standardize agent access. The subtle but important difference — agent sessions
  are stateful, long-running, and tool-heavy, whereas model calls are
  stateless-ish request/response — is acknowledged later (LAP starts with coding
  agents precisely because they are "long-running, stateful, tool-heavy"). The
  analogy holds but the stateful nature makes the control plane harder than a
  model gateway.

### Claim 6: The gateway is shifting from routing model calls to routing agent work
- **Evidence**: Presented as "the important shift" and reinforced as the reason
  the AI gateway "moves up the stack."
- **Confidence**: emerging
- **Quote**: "The important shift is that the gateway is no longer just routing model calls. It is routing agent work."
- **Our assessment**: This is the thesis in one sentence. It is a forecast about
  gateway product scope, consistent with the multi-runtime fragmentation claim.
  Note it *extends* (does not contradict) the existing corpus's model-call
  gateway concept — it argues the gateway's scope grows, not that the gateway
  disappears.

### Claim 7: The future agent stack mirrors the model stack layer-for-layer (models → harnesses, inference providers → agent runtimes, gateway → control plane)
- **Evidence**: The post enumerates both stacks explicitly and states "Each
  model-stack layer has a mirror in the agent stack."
- **Confidence**: emerging
- **Quote**: "Models: Claude, GPT, Gemini, open-source models / Harnesses: Claude Code, Codex, OpenCode, Hermes, DeepAgents / Agent runtimes: Claude Managed Agents, Bedrock AgentCore, Gemini Enterprise Agent Platform, self-hosted runtimes / Agent control plane: multi-runtime platform where teams manage agent runtimes, schedules, memory, and sessions. / Applications: coding agents, support agents, data agents, security agents"
- **Our assessment**: A clean mnemonic. The mapping is illustrative and useful for
  mental modeling, but the "harnesses" layer (Claude Code, Codex, OpenCode,
  Hermes, DeepAgents) is the one genuinely new category the post introduces — the
  agent frameworks/CLIs that sit between raw models and deployed runtimes.
  Reasonable as a framework, not as a proven taxonomy.

### Claim 8: Two layers of the agent stack are open gaps ("?") — no unified "one API across agent runtimes" and no clear winner yet in fast harness serving
- **Evidence**: The side-by-side diagram marks two model-stack layers with no
  agent-stack counterpart: the "one API across 100+ models" role has only a "?"
  for "one API across agent runtimes," and the vLLM "fast model serving" role has
  only a "?" for "fast harness serving," annotated "open gap — no clear winner
  yet."
- **Confidence**: emerging
- **Quote**: "one API across agent runtimes"  (marked "?" in the diagram)
- **Quote**: "fast harness serving"  (marked "?" in the diagram; caption: "open gap — no clear winner yet")
- **Our assessment**: Honest self-assessment by the author — the post admits the
  control-plane and high-performance-harness-serving layers are unsolved. This is
  the most credible part of a vision post: it names what does NOT yet exist.
  Useful for the guide as a "known-open-problems" pointer.

### Claim 9: LiteLLM Agent Platform (LAP) is a Rust-based AI Gateway + Agent Control Plane to register, invoke, observe, and govern agents across runtimes, starting with coding agents
- **Evidence**: Product description. LAP is positioned as LiteLLM's experiment in
  the direction described; coding agents chosen first because they are
  "long-running, stateful, tool-heavy, and expensive enough to require real
  infrastructure."
- **Confidence**: emerging
- **Quote**: "LiteLLM Agent Platform is a Rust-based AI Gateway and Agent Control Plane. The goal is to let teams register, invoke, observe, and govern agents across multiple runtimes."
- **Quote**: "We are starting with coding agents because the need is obvious. They are long-running, stateful, tool-heavy, and expensive enough to require real infrastructure."
- **Our assessment**: This is a product announcement, not an architecture proof.
  The four verbs (register, invoke, observe, govern) operationalize the control
  plane's responsibilities from Claim 4. Treat as a data point that at least one
  vendor is building in this direction — evidence the thesis is being acted on,
  not that it has succeeded.

### Claim 10: LAP is explicitly experimental and pre-v0 — APIs may change; it is not a second LiteLLM product
- **Evidence**: Two FAQ entries state plainly that LAP is an experiment and
  pre-v0. This is a critical credibility caveat that bounds every other claim.
- **Confidence**: settled
- **Quote**: "LAP is an experimental project. The goal is to learn quickly and bring the right pieces into LiteLLM over time."
- **Quote**: "No. LAP is pre-v0. APIs may change as we work with early users and contributors."
- **Our assessment**: The author is transparent that this is pre-production. The
  Assayer and Smith should weight all LAP-specific claims as directional/volatile.
  This caveat is why confidence_overall is `emerging` rather than `settled`.

## Concrete Artifacts

### Proposed stack comparison (reconstructed from the post's side-by-side diagram)

The original is a visual diagram; the text mapping below is reconstructed from the
page. Left column = today's model stack, right column = the post's proposed future
agent stack. The "→" marks a mirror relationship; "?" marks an open gap.

```
MODEL STACK (today)              AGENT STACK (future)
-------------------              -------------------
LiteLLM                          ?
one API across 100+ models   →   one API across agent runtimes   [ ? open gap ]

Bedrock                          Claude Managed Agents
cloud model inference        →   cloud model + harness API

SageMaker                         ?
deploy OSS models            →   deploy OSS harnesses

vLLM                             ?
fast model serving (throughput/  fast harness serving            [ ? open gap ]
 latency engine)                 "open gap — no clear winner yet"

Caption: "Each model-stack layer has a mirror in the agent stack.
         Dashed boxes mark open opportunities."
```

### Enumerated agent stack (verbatim bullets from the post)

```
Models:          Claude, GPT, Gemini, open-source models
Harnesses:       Claude Code, Codex, OpenCode, Hermes, DeepAgents
Agent runtimes:  Claude Managed Agents, Bedrock AgentCore,
                 Gemini Enterprise Agent Platform, self-hosted runtimes
Agent control plane: multi-runtime platform where teams manage
                 agent runtimes, schedules, memory, and sessions.
Applications:    coding agents, support agents, data agents, security agents
```

### Model-gateway responsibilities the post says the control plane builds on (verbatim)

```
Gateway: routing, fallbacks, logging, spend tracking, auth, billing
```

### LAP's stated four control-plane verbs (verbatim)

```
register, invoke, observe, and govern agents across multiple runtimes
```

## Cross-References

- **Corroborates**: None directly. No existing source note asserts a four-layer
  agent stack or a dedicated "agent control plane." The post's multi-runtime
  fragmentation observation is plausible but uncorroborated in the corpus.

- **Contradicts**: None. The post's gateway-evolution thesis does NOT oppose the
  existing corpus's model-call gateway concept — it argues the gateway's scope
  *expands* to agent sessions, which is complementary. No contradiction issue
  filed.

- **Extends**:
  - `blog-pagerduty-production-ai-agent-gaps.md` — its "Minimum Reference
    Architecture" describes a **Gateway** component responsible for
    "authentication, authorization, rate limits, policies, routing," at the
    model-call level (see that note's "Concrete Artifacts → Minimum Reference
    Architecture" and "Agent Routing and Permissions" sections). The LiteLLM post
    *extends* this same gateway concept upward: the gateway must move from routing
    model calls to managing agent sessions (lifecycle, memory, scheduling). Same
    primitive family, larger scope. This is the closest conceptual cousin in the
    corpus and the natural place for the Smith to connect the two.
  - `failure-litellm-wildcard-model-access-desync.md` — that incident report
    documents LiteLLM's *actual* model-gateway capabilities in production
    (routing, fallbacks, logging, spend tracking, auth/billing — exactly the
    "Gateway" layer the post describes) and a real reload-desync failure in that
    layer. It provides the grounded, remediated reality behind the "Gateway" row
    the post builds on when arguing the gateway should grow into a control plane.
    Note it is a different LiteLLM artifact type (incident report vs. strategy
    post) and different scope (model calls vs. agent sessions).

- **Novel**: First source note to introduce:
  - The four-layer agent-stack framework (models → harnesses → runtimes → agent
    control plane) and the "agent control plane" abstraction.
  - The "harnesses" layer as a distinct category (Claude Code, Codex, OpenCode,
    Hermes, DeepAgents) between models and runtimes.
  - Multi-runtime agent orchestration / unified agent *invocation* across
    heterogeneous runtime APIs as a first-class problem.
  - The explicit open-gap admissions ("?" cells): no unified cross-runtime agent
    API and no clear fast-harness-serving winner yet.
  - The first LiteLLM *strategy/vision* note (the other LiteLLM note is a
    failure report), giving the corpus a vendor-direction signal to balance the
    incident-level view.

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Add the agent-control-plane framing as an
  emerging architectural layer. Specific additions:
  - The multi-runtime fragmentation reality: agents increasingly span runtimes
    (Claude Managed Agents, Bedrock AgentCore, Gemini Enterprise Agent Platform,
    self-hosted), so "which runtime owns this agent" is becoming a real
    operational concern.
  - The distinction between *registering* agents (a registry) and *invoking*
    them uniformly (the hard problem) — useful when discussing agent
    discoverability and invocation in runbook/agent designs.
  - The "harnesses" concept (agent frameworks/CLIs like Claude Code, Codex) as a
    layer the guide can reference between raw models and deployed runtimes.

- **Chapter 05 (LLM Ops Reliability)**: Add the gateway-evolution thesis as a
  directional signal:
  - LLM gateways today do routing / fallbacks / logging / spend / auth / billing
    for *model calls*; the post argues they must expand to *govern agent
    sessions* (lifecycle, scheduling, memory, observability) as agents become the
    dominant use-case. Frame as a forward-looking trend, not a deployable pattern.
  - The control plane's four verbs — register, invoke, observe, govern — map
    cleanly onto reliability concerns (observability + governance of agents
    across runtimes). Use as a checklist for "what would a multi-runtime agent
    control plane need to do reliably."
  - Include the honest open-gap caveat: the cross-runtime agent API and
    fast-harness-serving layers are unsolved (pre-v0), so practitioners should
    not assume a turnkey control plane exists yet.

- **Chapter 02 / gateway material**: Connect to the existing PagerDuty gateway
  component description (auth, authorization, rate limits, policies, routing) and
  note the proposed scope expansion from model calls to agent sessions.

## Extraction Notes

- Source read in full. The page is a Docusaurus blog post (published June 10,
  2026; last updated June 2026; tagged `ideas`). WebFetch returned empty for this
  host, so the page was fetched via direct HTTP (curl) and HTML-to-text
  extraction; all quoted passages were copied character-for-character from the
  rendered page text.
- This is explicitly a vision/strategy post, not a practitioner experience
  report. It contains no code, no deployable config, no production metrics, and
  no independent corroboration. LiteLLM Agent Platform (LAP) is stated to be
  pre-v0 and experimental. Consequently, confidence_overall is set to `emerging`
  (a coherent vendor thesis grounded in an observed fragmentation pattern, but
  unproven and pre-production) rather than `settled`.
- The side-by-side "stack of the future" diagram is a visual; the table in
  Concrete Artifacts is a faithful reconstruction of its text mapping (left =
  model stack, right = agent stack, "?" = open gap), not a verbatim copy of
  rendered table cells. The enumerated agent-stack bullets and the gateway/LAP
  phrases are verbatim.
- No contradiction issue filed: verified against all existing source notes; the
  gateway-evolution thesis complements (does not oppose) the model-call gateway
  concept present in `blog-pagerduty-production-ai-agent-gaps.md` and the
  LiteLLM incident report. The only "control plane" / "harness" string hits
  elsewhere in the corpus (docs-google-sre-prodcast*.md) refer to unrelated
  concepts (SRE evaluation harness, SRE-with-AI agents), not this agent
  control-plane thesis.
- novelty: medium per triage; this is the first LiteLLM strategy note and the
  first agent-control-plane framing in the repo.
