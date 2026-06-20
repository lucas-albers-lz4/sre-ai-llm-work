---
source_url: https://cursor.com/blog/typescript-sdk
source_type: blog-post
title: "Build programmatic agents with the Cursor SDK"
author: Roshan Sadanani (Cursor)
date_published: 2026-04-29
date_extracted: 2026-05-25
last_checked: 2026-05-25
status: current
confidence_overall: emerging
issue: "#467"
---

# Build programmatic agents with the Cursor SDK (Roshan Sadanani, Cursor)

> Cursor's public beta launch of the TypeScript SDK — which opens the same runtime, harness, and models powering Cursor's interactive product to external programmatic use — establishing a unified five-component harness API (context management, MCP, skills, hooks, subagents), three deployment modes (local/cloud/self-hosted), and a fire-and-check-back async execution pattern for CI/CD and embedded-agent use cases.

## Source Context

- **Type**: blog-post (Cursor engineering blog, public beta product announcement, ~6 min read, published April 29, 2026)
- **Author credibility**: Roshan Sadanani writing on the official Cursor blog. This is a vendor product announcement for a beta SDK — commercial motivation is present. The technical specificity (named config paths, concrete TypeScript API surface, three named deployment modes, two code examples with distinct model IDs) is consistent with genuine engineering documentation rather than purely marketing prose. Claims about the SDK's harness capabilities are corroborated by the same capabilities described from an operational perspective in `blog-cursor-continual-harness-improvement.md`. Treat as emerging: directionally reliable for API design and named features; beta status means the API surface may change.
- **Scope**: Covers the SDK's three runtime modes (local, cloud, self-hosted), the five harness components exposed to external developers (context management, MCP servers, skills, hooks, subagents), session persistence behavior, git integration capabilities (PRs, branches), CI/CD and product embedding use cases, and pricing model. Does NOT cover: rate limits, latency characteristics, SDK error handling, webhook/callback patterns for async notifications, authentication token management, SDK versioning strategy, or how the SDK interacts with CursorBench for evaluation.

## Extracted Claims

### Claim 1: The Cursor SDK makes the same runtime, harness, and models powering the Cursor product available to external developers programmatically via TypeScript.

- **Evidence**: Official product announcement; SDK in public beta with an npm package (`@cursor/sdk`). The framing explicitly positions this as the same infrastructure, not a separate simplified interface.
- **Confidence**: emerging (official product announcement; beta status means the API surface may evolve)
- **Quote**: "We're introducing the Cursor SDK so you can build agents with the same runtime, harness, and models that power Cursor."
- **Our assessment**: The "same runtime, harness, and models" claim is the key positioning: this is not a lightweight proxy or simplified API — it is the full production harness exposed externally. Practitioners building on the SDK should have the same context management, tool call reliability, and model access as Cursor's own product. Corroboration: `blog-cursor-continual-harness-improvement.md` describes the same harness components (context management, MCP, model provisioning, hooks) from an internal operational perspective; the SDK announcement describes them as the external API surface. Same harness, two audiences.

### Claim 2: Coding agents are evolving from interactive tools for individual developers to programmatic infrastructure for organizations.

- **Evidence**: Cursor's own editorial framing of the SDK's positioning; corroborated by CI/CD use cases and product embedding examples in the same post.
- **Confidence**: emerging (Cursor's editorial framing; consistent with adoption patterns described across corpus)
- **Quote**: "Coding agents are evolving from interactive tools for individual developers to programmatic infrastructure for organizations."
- **Our assessment**: This framing redefines the design space. An interactive tool optimizes for developer UX (low latency, clear feedback, conversational flow). Programmatic infrastructure optimizes for reliability, orchestratability, and integration with existing pipelines. The SDK is the concrete step from one to the other: the same underlying agent, now with an API surface that makes it composable with CI/CD, batch jobs, and customer-facing products. For the guide: this is the clearest statement that "building with AI" and "using AI as a developer tool" are diverging design regimes.

### Claim 3: Three deployment modes share a single SDK: local (developer machine), cloud (Cursor-hosted VMs), and self-hosted (customer's own infrastructure).

- **Evidence**: Code examples demonstrate local and cloud options explicitly; self-hosted described as a distinct option using the same SDK. The single `Agent.create()` call accepts `local:` or `cloud:` runtime configuration.
- **Confidence**: emerging (official product description; local and cloud modes are demonstrated in code; self-hosted described)
- **Quote**: "The same SDK can run agents on self-hosted workers, keeping code and tool execution inside your network, or locally on your machine for fast iteration."
- **Our assessment**: A single SDK interface that works across all three modes means organizations can develop locally for fast iteration, deploy to cloud for production long-running tasks, and deploy self-hosted where data security requirements prevent cloud execution. This runtime polymorphism mirrors the deployment flexibility described in `blog-cursor-self-hosted-cloud-agents.md` — now surfaced as an explicit SDK option. The self-hosted mode is the same architecture (outbound HTTPS worker, split inference/execution) as that source documents, now accessible via SDK.

### Claim 4: Cloud agents run in dedicated VMs with full development environments and produce git artifacts (PRs, branches, screenshots) when finished.

- **Evidence**: Product description with a code example showing `autoCreatePR: true` and `result.git?.branches[0]?.prUrl` in the API response.
- **Confidence**: emerging (product description backed by code example showing the PR URL retrieval pattern)
- **Quote**: "its own dedicated VM with strong sandboxing, a clone of the repo, and a fully configured development environment." And: "When the agent finishes, it can open a PR, push a branch, or attach demos and screenshots."
- **Our assessment**: The VM-per-session isolation is the same pattern described in `blog-cursor-self-hosted-cloud-agents.md` Claim 4 ("Dedicated machines per agent without resource sharing"), confirmed here as available via SDK. The git integration (`autoCreatePR`, `prUrl`) surfaces what was previously an internal Cursor capability (agents generating PRs) as a programmable output of the API call. For CI/CD integration: the async pattern (initiate → get run ID → wait for result → read prUrl) is the concrete TypeScript pattern for triggering agents from automation pipelines and collecting their output.

### Claim 5: Session persistence across network interruptions and device sleep enables fire-and-check-back async workflows distinct from synchronous streaming.

- **Evidence**: Code example showing `Agent.getRun(run.id, ...)` as a separate call from the initial send — enabling checking back on a cloud run from a different context. Explicit persistence description.
- **Confidence**: emerging (product description + code example showing the async get-run pattern)
- **Quote**: "Agents keep going when your laptop sleeps or network drops. You can stream the conversation and reconnect later."
- **Our assessment**: The fire-and-check-back pattern is architecturally distinct from the streaming pattern (local mode: `for await (const event of run.stream())`). In local mode, you stream events synchronously. In cloud mode, you initiate, record the run ID, and can re-attach from any context — the agent continues regardless of client connectivity. This is consistent with `blog-cursor-cloud-agent-lessons.md` Claim 4 (Temporal enables runs that "stretch across days or even weeks") and Claim 7 (conversation storage and streaming separated from core agent workflow). The SDK surfaces these architectural properties through `getRun()` + `.wait()`.

### Claim 6: Intelligent context management via codebase indexing, semantic search, and grep is part of the harness the SDK inherits.

- **Evidence**: Explicit product description under "Use the full Cursor harness."
- **Confidence**: emerging (product description; consistent with harness capabilities described in `blog-cursor-continual-harness-improvement.md`)
- **Quote**: "Codebase indexing, semantic search, and instant grep help agents get to the right outcome faster and more efficiently."
- **Our assessment**: SDK-launched agents have the same retrieval and indexing infrastructure as interactive Cursor. Practitioners building on the SDK do not need to implement their own RAG pipeline for the codebase — the harness handles it. The context management layer abstracts away retrieval mechanics, letting agent prompts focus on task description rather than retrieval instruction. This is the SDK-exposed version of the static-to-dynamic context evolution described in `blog-cursor-continual-harness-improvement.md` Claim 12 — dynamic retrieval is built in, not bolted on.

### Claim 7: MCP server integration allows agents to connect to external tools and data sources over stdio or HTTP, configurable at the repo level or inline per SDK call.

- **Evidence**: Explicit product description with named configuration paths.
- **Confidence**: emerging (product description with specific configuration path)
- **Quote**: "Agents can connect to external tools and data sources over stdio or HTTP, either through a `.cursor/mcp.json` config file or passed inline on the call."
- **Our assessment**: The dual configuration approach (`.cursor/mcp.json` for persistent repo-level config; inline for programmatic/per-call config) is the SDK-specific addition beyond standard MCP. The inline option is particularly significant for programmatic use: it allows SDK callers to inject MCP server configurations at runtime without requiring repo-level configuration — essential for dynamic deployment scenarios where different agents connect to different customer databases or services. This extends standard MCP usage patterns by making server configuration a runtime parameter rather than a static repo artifact.

### Claim 8: Skills from `.cursor/skills/` are auto-picked up by agents, providing a reusable library pattern for common capabilities.

- **Evidence**: Explicit product description with named configuration path.
- **Confidence**: emerging (product description; the auto-pickup behavior is the notable implementation detail)
- **Quote**: "Agents pick up skills automatically from your repo's `.cursor/skills/` directory."
- **Our assessment**: Auto-pickup means any agent launched in a repository inherits its skill library without explicit configuration — convention over configuration. For teams building multi-agent systems on the SDK: skills are the reuse mechanism for common agent sub-capabilities (specific search patterns, custom tools, domain-specific procedures). The Cursor native `/sdk` skill mentioned in the post's closing section is an example of this pattern applied reflexively to SDK development itself, where the SDK's own guidance is available as a skill.

### Claim 9: Hooks allow observing, controlling, and extending the agent loop across all three runtimes via `.cursor/hooks.json`.

- **Evidence**: Explicit product description naming the configuration file and covering all three runtimes.
- **Confidence**: emerging (product description; no detail on hook event types, payload format, or programmatic callback API — the most underspecified feature in the post)
- **Quote**: "Observe, control, and extend the agent loop across cloud, self-hosted, and local with a `.cursor/hooks.json` file."
- **Our assessment**: Hooks are the observability and control plane for the agent loop. The three verbs (observe, control, extend) suggest distinct capabilities: observation (logging/monitoring), control (approval gates, loop termination), extension (adding steps to the loop). Cross-runtime support means the same hook configuration applies regardless of deployment mode. For practitioners: hooks are the mechanism for human-in-the-loop patterns (e.g., requiring human approval before a destructive tool call) and for integrating external monitoring systems. No code examples are provided — this is the most underspecified feature and the highest-priority gap for follow-up SDK documentation.

### Claim 10: Subagents are spawned by the main agent via the `Agent` tool, with independent prompts and models per subagent.

- **Evidence**: Explicit product description naming the tool mechanism.
- **Confidence**: emerging (product description; consistent with multi-agent patterns in the corpus)
- **Quote**: "Delegate subtasks to named subagents with their own prompts and models, which the main agent spawns via the `Agent` tool."
- **Our assessment**: The `Agent` tool as the spawning mechanism is the SDK's multi-agent composition primitive. "Named subagents with their own prompts and models" means each subagent gets independent task specification and can use a different model — enabling cost optimization (cheaper model for simpler subtasks) and specialization (stronger model for complex reasoning). This extends the planner-worker architecture described in `blog-cursor-multi-agent-kernels.md` with a concrete TypeScript API surface. For practitioners: the subagent pattern enables hierarchical task decomposition without custom orchestration infrastructure — the parent agent handles delegation via a standard tool call.

### Claim 11: Teams use the SDK for CI/CD automation, root cause analysis, PR generation, and embedding agents in customer-facing products.

- **Evidence**: Multiple named use cases with specific workflow descriptions.
- **Confidence**: emerging (vendor-described use cases; not validated by named customers; consistent with the adoption trajectory described across corpus)
- **Quote**: "Many teams are invoking agents directly from CI/CD pipelines, creating automations for end-to-end workflows, and embedding agents into their core products." And: "programmatic agents that are kicked off directly from CI/CD to summarize changes, identify root causes for CI failures, and update PRs with fixes." And: "Some customers are even embedding Cursor directly into customer-facing products, where end users now get an agent experience without leaving the host application."
- **Our assessment**: Three distinct architectural roles emerge: (1) pipeline automation (agent as CI step), (2) internal tooling (agent as service within organization), (3) product embedding (agent as end-user feature). Each has different reliability, latency, and cost requirements. The customer-facing embedding case is the most novel: when agents are embedded in customer-facing products, the design domain shifts from developer tool to product infrastructure, with SLA obligations toward end users rather than internal developers.

### Claim 12: The SDK is available to all Cursor users in public beta, billed on token-based consumption pricing.

- **Evidence**: Official pricing and availability statement.
- **Confidence**: settled (official product statement)
- **Quote**: "The Cursor SDK is available to all users and is billed based on standard, token-based consumption pricing."
- **Our assessment**: Token-based consumption pricing (vs. seat-based subscription) means cost scales with actual agent usage, not seat count — economically rational for automation use cases where agents run without a developer present. For teams evaluating SDK adoption: the cost model aligns with programmatic batch use rather than per-developer interactive use.

## Concrete Artifacts

### Local Agent: Streaming Pattern

```typescript
// Source: https://cursor.com/blog/typescript-sdk (April 29, 2026)
// Local agent with synchronous streaming output

import { Agent } from "@cursor/sdk";

const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  local: { cwd: process.cwd() },
});

const run = await agent.send("Summarize what this repository does");

for await (const event of run.stream()) {
  console.log(event);
}
```

### Cloud Agent: Fire-and-Check-Back Pattern

```typescript
// Source: https://cursor.com/blog/typescript-sdk (April 29, 2026)
// Cloud agent with async initiation and later retrieval

// Initiate cloud agent to start a task...:
const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "gpt-5.5" },
  cloud: {
    repos: [{ url: "https://github.com/cursor/cookbook", startingRef: "main" }],
    autoCreatePR: true,
  },
});

const run = await agent.send("Fix the auth token expiry bug");
console.log(`Started ${run.id}`);

// ...check back in later, from anywhere:
const result = await (
  await Agent.getRun(run.id, { runtime: "cloud", agentId: run.agentId })
).wait();
console.log(result.git?.branches[0]?.prUrl);
```

### SDK Harness Feature Summary

```
# Cursor SDK harness features (April 2026)
# Source: https://cursor.com/blog/typescript-sdk

CONTEXT MANAGEMENT
  - Codebase indexing, semantic search, instant grep
  - "help agents get to the right outcome faster and more efficiently"
  - Inherited from the same harness that powers Cursor desktop/CLI/web

MCP SERVERS
  - Connect to external tools/data sources over stdio or HTTP
  - Configuration: .cursor/mcp.json (repo-level) OR inline on the call
  - Inline option enables per-call dynamic tool configuration

SKILLS
  - Auto-picked up from .cursor/skills/ directory
  - Reusable library pattern for common agent sub-capabilities
  - Convention: put skills in repo, all agents launched there inherit them

HOOKS
  - Observe, control, and extend the agent loop
  - Configuration: .cursor/hooks.json
  - Works across all three runtimes (cloud, self-hosted, local)
  - No code examples provided; event/payload format not specified (gap)

SUBAGENTS
  - Named subagents with independent prompts and models
  - Spawned by main agent via the Agent tool
  - Enables hierarchical task decomposition and model specialization

DEPLOYMENT MODES
  - Local: developer machine, fast iteration, synchronous event streaming
  - Cloud: dedicated VM, sandboxed environment, cloned repo,
           git artifact output (PR URL, branch, screenshots)
  - Self-hosted: customer's own infrastructure, code and tool execution
                 stays inside customer's network
```

### Async Execution Pattern: Local vs. Cloud

```
# SDK execution patterns compared (April 2026)
# Source: https://cursor.com/blog/typescript-sdk

LOCAL MODE (synchronous streaming):
  agent.send(prompt)
    → run.stream()     [async iterator, event-by-event, synchronous lifecycle]

CLOUD MODE (async fire-and-check-back):
  agent.send(prompt)
    → run.id           [persisted; agent continues independently of client]
  (later, from any context, any process)
  Agent.getRun(run.id, { runtime: "cloud", agentId: run.agentId })
    → .wait()          [blocks until agent completes]
    → result.git?.branches[0]?.prUrl  [git artifact from completed run]

Session persistence properties (cloud mode):
  - Survives: laptop sleep, network drop, client disconnection
  - "Agents keep going when your laptop sleeps or network drops."
  - "You can stream the conversation and reconnect later."
  - Infrastructure basis: Temporal durable execution
    (see blog-cursor-cloud-agent-lessons.md Claim 4)
```

## Cross-References

- **Corroborates**: `blog-cursor-cloud-agent-lessons.md` — Claim 4 in that note (Temporal enables "runs that stretch across days or even weeks") is the infrastructure explanation for session persistence in Claim 5 here ("Agents keep going when your laptop sleeps or network drops"). Claim 6 in that note (three-component decoupling: agent loop / machine state / conversation state) explains how `Agent.getRun(run.id)` works architecturally: the Temporal-based agent loop runs independently of the client connection, and conversation state streams out as a separate layer. The fire-and-check-back SDK pattern is the developer-facing API for the three-component decoupling architecture described internally.

- **Corroborates**: `blog-cursor-self-hosted-cloud-agents.md` — Claim 2 (outbound-only HTTPS worker pattern) and Claim 3 (split inference/cloud from execution/on-prem) describe the same self-hosted execution architecture that the SDK's third deployment mode exposes. The SDK's self-hosted option ("keeping code and tool execution inside your network") aligns precisely with the architectural description in that note. The SDK adds the developer API surface; the self-hosted note covers the deployment and security architecture behind it.

- **Corroborates**: `blog-cursor-continual-harness-improvement.md` — The harness features described in that note (Claims 4, 8, 12: tool-call error taxonomy, model-specific tool format provisioning, dynamic context) are the operational implementation of what the SDK exposes externally. The SDK's "same harness" framing is verifiable by comparison: context management, MCP integration, and model provisioning described here match what the harness improvement post describes as Cursor's production harness. Two sources; same harness described from operator and developer perspectives.

- **Extends**: `blog-cursor-multi-agent-kernels.md` — The kernel optimization system used a planner-worker architecture described from an internal perspective. The SDK's subagent pattern (Claim 10: "Delegate subtasks to named subagents with their own prompts and models, which the main agent spawns via the `Agent` tool") is the external TypeScript API that enables this architecture for third-party developers. The SDK provides the concrete API; the kernel optimization post demonstrates the architecture's production results.

- **Extends**: `blog-cursor-cloud-agent-dev-environments.md` — That post covers what cloud agent development environments must contain (multi-repo, Dockerfile configuration, credentials, test execution access). The SDK's cloud mode (Claim 4: dedicated VM with "a clone of the repo, and a fully configured development environment") is the API for accessing those environments. Together: the dev environments post describes what the cloud environment provides; this post describes how to access it programmatically.

- **Extends**: `blog-cursor-composer2-technical-report.md` — That report covers how Composer 2 was trained. The SDK's model field (`model: { id: "composer-2" }`) is the external API for accessing that trained model. The SDK is the deployment path for what the technical report describes internally; practitioners can access Composer 2 with a single configuration field.

- **Novel**:
  - **External programmatic API for the full Cursor harness**: No other corpus source describes an SDK that exposes the same runtime/harness/models as the Cursor interactive product to external developers. This is the first source documenting a programmatic API surface for the harness as a whole.
  - **Hooks as cross-runtime control plane**: The `.cursor/hooks.json` mechanism (observe, control, extend the agent loop across all three runtimes) is not described in any other source. It is the first documented mechanism for agent loop observability and control available to third-party developers.
  - **Inline MCP server configuration per SDK call**: The ability to pass MCP server configuration inline on a per-call basis (not just via `.cursor/mcp.json`) enables dynamic agent configurations without static repo-level config — essential for multi-tenant or dynamic deployment scenarios. Not described in any other corpus source.
  - **Fire-and-check-back async pattern via `getRun()`**: The specific TypeScript API pattern (initiate → `run.id` → `Agent.getRun()` → `.wait()`) for async cloud agent sessions is the concrete developer API for the cloud agent durability architecture. No other source shows this API pattern.
  - **Model selection as an explicit per-call SDK parameter**: The code examples show two different model IDs (`composer-2` for local, `gpt-5.5` for cloud), establishing that model selection is a per-agent-call decision at the SDK level. This is the first corpus source to show model selection as an explicit parameter in a coding agent API call.
  - **Agent embedding in customer-facing products**: The product embedding use case (Claim 11: "Some customers are even embedding Cursor directly into customer-facing products, where end users now get an agent experience") extends the guide's coverage beyond developer-tool use cases into AI-native product design.

## Guide Impact

- **Chapter 02 (Harness Engineering)**: Add the SDK's five harness components (context management, MCP, skills, hooks, subagents) as the concrete external API surface for Cursor's harness. Cite alongside `blog-cursor-continual-harness-improvement.md` — the SDK announcement provides the "what is available externally" description; the harness improvement post provides the "how it's maintained internally" description. Together they give practitioners both the API surface to build on and the operational principles behind it.

- **Chapter 02 (Harness Engineering — deployment modes)**: Add the three-runtime model (local/cloud/self-hosted via a single SDK) as a reference architecture for deployment polymorphism. The single `Agent.create()` call accepting different runtime configurations is a concrete design pattern for agent infrastructure that supports multiple deployment targets from the same codebase.

- **Chapter 02 (Harness Engineering — hooks and observability)**: Add the hooks mechanism as the recommended pattern for agent loop observability and control at the API level. Currently no chapter covers hooks as a named harness observability primitive for external developers. The `.cursor/hooks.json` approach should be documented alongside programmatic alternatives (when SDK exposes programmatic hook registration, if it does). The underspecification of this feature makes it a candidate for a follow-up documentation fetch.

- **Chapter 07 (Multi-agent systems)**: The `Agent` tool as the subagent spawning primitive (Claim 10) should be documented as the concrete TypeScript API for the planner-worker composition pattern. Cite alongside `blog-cursor-multi-agent-kernels.md` to connect abstract architecture to TypeScript API. The per-subagent model selection (each subagent gets its own `model:` field) is an additional architectural affordance that enables heterogeneous-model agent teams.

- **Chapter 04 (Context Engineering)**: MCP inline configuration per SDK call (Claim 7) should be added to the MCP section. The per-call inline configuration capability enables dynamic agent context injection not possible with static `.cursor/mcp.json` configurations — relevant for multi-tenant deployment scenarios.

- **Chapter 01 (Daily Workflows — agent adoption trajectory)**: The customer-facing product embedding use case (Claim 11) anchors a discussion of AI-native products vs. AI-assisted development. When agents are embedded in customer-facing products, the design domain shifts from developer tool to product infrastructure — with reliability, latency, and cost requirements that differ from internal developer use.

## Extraction Notes

- Source was fetched from https://cursor.com/blog/typescript-sdk across multiple targeted fetches. The WebFetch tool returned summaries rather than complete verbatim text; all quotes were specifically requested and verified as verbatim through targeted fetch operations.
- Author confirmed as Roshan Sadanani from blog post metadata. Publication date (April 29, 2026) confirmed from the RSS entry in the issue body.
- The blog post is a product announcement, not a technical deep-dive — the SDK features are described but not specified in detail (no hook payload format, no error handling patterns, no rate limit documentation).
- The hooks feature (Claim 9) is the most underspecified. The blog names it and provides the config file path but gives no detail on event types, payload format, or callback mechanisms. A follow-up extraction from SDK documentation (if available) would be high-value.
- No contradictions to file: the three-runtime model is consistent with `blog-cursor-self-hosted-cloud-agents.md` and `blog-cursor-cloud-agent-lessons.md`. Harness features match `blog-cursor-continual-harness-improvement.md`. Subagent spawning corroborates (not contradicts) the multi-agent architecture in `blog-cursor-multi-agent-kernels.md`.
- Previous mining attempt (PR #667, branch `miner/issue-467-r25685290933`) was closed for a pipeline dispatch-rate-limit issue, not a quality rejection. This note is a fresh extraction on the same source.
