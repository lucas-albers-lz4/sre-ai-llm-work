---
source_url: https://www.honeycomb.io/blog/instrumenting-ai-agents-agent-timeline-opentelemetry-guide
source_type: blog-post
title: "Instrumenting AI Agents for the Agent Timeline: A Practical OpenTelemetry Guide"
author: Dan Juengst (Honeycomb)
date_published: 2026-06-29
date_extracted: 2026-07-25
last_checked: 2026-07-25
status: current
confidence_overall: emerging
issue: "#2-qwen3-5-plus-eval"
---

# Instrumenting AI Agents for the Agent Timeline

> A practitioner guide from Honeycomb engineering on instrumenting AI agents with OpenTelemetry GenAI semantic conventions, centered on the assertion that the LLM is rarely the root cause of agent failures — tool calls, downstream services, and multi-agent handoffs are where agents actually break, and the Agent Timeline makes these first-class debugging primitives.

## Source Context

- **Type**: blog-post (practitioner writeup from Honeycomb engineering)
- **Author credibility**: Dan Juengst is a Honeycomb engineer writing on the company's official engineering blog. Honeycomb operates an observability platform that includes the Agent Timeline feature described in the article. The author has direct experience building and instrumenting the patterns described. The article is accompanied by a live product feature (Agent Timeline, announced May 2026) and public documentation at `docs.honeycomb.io`.
- **Scope**: Covers end-to-end OpenTelemetry instrumentation for AI agents — required attributes, span naming, tool call instrumentation, multi-agent handoff patterns, token tracking, prompt/response capture with PII caveats, failure signal propagation, evaluation event attachment, and framework-specific guidance for OpenAI, Anthropic, and LangChain. Also covers OTel Collector transform processor configuration for remapping non-conforming telemetry (Claude Code example). Does NOT cover: metrics/logs collection, alerting rules, SLO definitions, or cost optimization beyond token counting.
- **Linked pages followed for extraction**: `docs.honeycomb.io/investigate/observe/agent-timeline` (Agent Timeline UI/feature docs) and `docs.honeycomb.io/send-data/agents` (agent instrumentation attribute registry and Claude Code remapping config). Both added substantive detail beyond the blog post — the full attribute registry, Claude Code remapping configuration, and `retrieval`/`create_agent`/`invoke_workflow` operation types not mentioned in the blog.

## Extracted Claims

### Claim 1: The LLM is rarely the root cause of agent failures
- **Evidence**: The author's operational experience building and debugging AI agents at Honeycomb. The article's central thesis is that tool calls, downstream service spans, and multi-agent handoffs carry the actual failure signals, while the LLM call itself is usually healthy.
- **Confidence**: emerging
- **Quote**: "The LLM is rarely the root cause of agent failures."
- **Our assessment**: Plausible and consistent with agent architecture patterns: LLM calls are stateless API requests with well-defined error surfaces, whereas tool execution involves arbitrary I/O, side effects, and external dependencies. The article's framing is useful as a debugging heuristic — start investigation at tool calls and handoff boundaries, not the model response. However, this is a practitioner observation, not a quantitative study. No failure-distribution data is presented.

### Claim 2: Three attributes are mandatory on every span for the Agent Timeline to function
- **Evidence**: Concrete attribute names with types and scope rules, backed by both the blog post and the Honeycomb "Send Data: Agents" documentation page. The docs page specifies these as required fields with explicit type definitions and the consequence of omission.
- **Confidence**: settled (for Honeycomb's Agent Timeline; the OTel GenAI semconv spec codifies similar requirements)
- **Quote**: "To make that work, every span in your agent's execution chain needs three attributes:"
- **Our assessment**: These three attributes (`gen_ai.conversation.id`, `gen_ai.agent.name`, `gen_ai.operation.name`) form the minimum viable contract for any agent tracing system, not just Honeycomb's. The conversation ID is the grouping key, the agent name creates swim lanes, and the operation name enables type-specific UI rendering. This is the single most extractable pattern in the source — any guide chapter on agent observability should reference this trio as the baseline.

### Claim 3: A GenAI span is any span in the agent's execution chain, not just LLM calls
- **Evidence**: The article explicitly broadens the definition to include downstream DB queries, third-party API calls, and background jobs — any span carrying the conversation ID. The Agent Timeline docs confirm that the view nests non-GenAI spans under GenAI operation spans.
- **Confidence**: emerging
- **Quote**: "a 'GenAI span' is not just an LLM call"
- **Our assessment**: This is a critical conceptual expansion. Many developers think of "LLM observability" as instrumenting the model call; this source argues the observability surface is the entire agent execution graph. The implication is that conversation ID propagation into downstream systems is not optional — without it, you lose visibility into the parts of the system most likely to fail (Claim 1). This aligns with distributed tracing best practices but applies them to a new domain.

### Claim 4: Auto-instrumentation covers LLM-layer spans, but agent-layer attributes must be hand-authored
- **Evidence**: The article provides specific guidance for OpenAI SDK, Anthropic SDK, and LangChain/LangGraph, each following the same pattern. The Honeycomb docs reinforce this with the Claude Code remapping example — even when auto-instrumentation exists, remapping is needed because the tool emits non-conforming telemetry.
- **Confidence**: emerging
- **Quote**: "Auto-instrumentation can't infer your conversation boundaries or your agent identity."
- **Our assessment**: This is a practical, non-obvious rule. Framework auto-instrumentation can detect LLM calls because they go through known library hooks, but "which conversation does this belong to?" and "which agent am I?" are application-level concepts no framework can infer. The universal pattern — "let the framework instrumentation own the LLM-layer spans, and you own the agent-layer and conversation-layer attributes" — is a concise, actionable heuristic.

### Claim 5: Tool calls are where most agentic failures live
- **Evidence**: The article provides a complete tool execution span example with try/except error propagation. The Honeycomb docs specify `error.type`, `error.message`, and `error.stacktrace` as the standard error attributes, and tool call failure propagation to the parent span as a requirement.
- **Confidence**: emerging
- **Quote**: "Tool calls are where most agentic failures live."
- **Our assessment**: Consistent with Claim 1 and Claim 3. Tool execution spans are the highest-value instrumentation target because they involve arbitrary external I/O. The concrete pattern — set `error.type` on exception, propagate error status to parent span, and use the Timeline's "Show Failures Only" filter — is directly applicable to any agent observability setup. The article's specific error-handling code pattern (try/except with `span.set_attribute("error.type", type(e).__name__)` and `span.set_status(Status(StatusCode.ERROR))`) is production-grade.

### Claim 6: Multi-agent systems require distinct agent names per sub-agent and explicit handoff spans
- **Evidence**: Code example showing orchestrator emitting `invoke_agent billing_agent` span with `gen_ai.agent.name = "orchestrator"`, then `billing_agent` emitting its own spans with `gen_ai.agent.name = "billing_agent"`. The Honeycomb docs add that `gen_ai.agent.name` is "used to group spans by agent in the timeline" and that missing values show as "Unknown."
- **Confidence**: emerging
- **Quote**: "Each agent gets its own `gen_ai.agent.name`."
- **Quote**: "Sub-agents use their own distinct names; they don't inherit from the parent."
- **Our assessment**: This is the most opinionated and potentially controversial claim in the article. Not all agent frameworks model sub-agents with distinct identities — some treat them as internal function calls under a single agent name. The article's pattern (caller emits `invoke_agent`, callee uses its own name) creates clean swim-lane separation but requires discipline: every agent in the system must be named, and the naming must be consistent across invocations. This is good architecture but may be aspirational for teams with ad-hoc agent graphs.

### Claim 7: The calling agent emits the `invoke_agent` span, not the agent being called
- **Evidence**: Code example and explicit statement in the multi-agent instrumentation section.
- **Confidence**: emerging
- **Quote**: "The calling agent emits the `invoke_agent` span, not the agent being called."
- **Our assessment**: This complements Claim 6 by specifying the handoff mechanics. The caller owns the handoff event; the callee owns its execution spans. This makes handoffs queryable events in the trace, which is useful for latency attribution ("how long did the handoff take?") and failure isolation ("did the handoff fail or did the callee fail?").

### Claim 8: Capturing both requested and actual response model names enables debugging silent provider-side model upgrades
- **Evidence**: The article provides concrete attribute names (`gen_ai.request.model` and `gen_ai.response.model`) with a worked example: requesting `gpt-4o` but receiving `gpt-4o-2024-08-06`. The Honeycomb docs list both as optional span attributes with type `string`.
- **Confidence**: anecdotal
- **Quote**: "Capturing both is how you debug behavior changes after a silent provider-side model upgrade."
- **Our assessment**: This is a sharp operational insight. Model providers routinely roll out minor version updates that can change agent behavior in subtle ways. Having both attributes on every LLM span gives you a queryable diff — "show me all conversations where the response model differed from the request model, correlated with error rate changes." The pattern generalizes beyond OpenAI to any model provider.

### Claim 9: Token usage attributes should include cache read and cache creation tokens
- **Evidence**: The article lists four token attributes: input, output, cache read input, and cache creation input tokens.
- **Confidence**: emerging
- **Quote**: "gen_ai.usage.cache_read.input_tokens" and "gen_ai.usage.cache_creation.input_tokens"
- **Our assessment**: This reflects the state of prompt caching as of mid-2026. Teams using provider-side caching (OpenAI's prompt cache, Anthropic's cache) need these attributes to track cache hit rates and cost savings. The article's inclusion of these attributes is forward-looking and reflects production caching patterns.

### Claim 10: Prompt and response capture dramatically accelerates root-cause investigation but requires PII handling
- **Evidence**: The article lists `gen_ai.input.messages` and `gen_ai.output.messages` as span events (not attributes — a deliberate design choice so an OTel Collector can filter them). Three mitigation strategies are offered: redact at app layer, scrub at Collector, or restrict to non-prod. The Honeycomb docs flag these with a "may contain PII or other sensitive data" warning.
- **Confidence**: settled
- **Quote**: "These make root-cause investigation dramatically faster because you can read what the agent was told and what it said."
- **Our assessment**: The article handles this well — it doesn't sugarcoat the PII risk. Storing prompt/response as span events rather than span attributes is a meaningful architectural decision: events can be stripped by a Collector processor without touching application code. The three-tier mitigation strategy (app, Collector, environment-gating) is practical and covers teams at different maturity levels. This should be the guide's recommended pattern for any LLM I/O capture.

### Claim 11: Setting `error.type` and propagating error status turns failures into first-class navigation primitives
- **Evidence**: The tool call code example shows `error.type` being set and `span.set_status(Status(StatusCode.ERROR))` called in the except block. The Agent Timeline docs describe a "Show Failures Only" toggle and conversation-level failure count that both depend on these attributes.
- **Confidence**: emerging
- **Quote**: "This is what turns failures into first-class navigation primitives instead of needles in a haystack."
- **Our assessment**: This is standard OpenTelemetry error semantics applied to a new domain, but the article correctly identifies that agent debugging without structured error signals is uniquely painful because of nondeterminism. The "needles in a haystack" framing is apt — without `error.type` on spans, an operator searching for failures across thousands of agent conversations has no queryable surface. The pattern is low-effort, high-impact: it's two lines of code in the exception handler.

### Claim 12: Evaluation results should be attached as span events to GenAI operation spans
- **Evidence**: The article mentions attaching `gen_ai.evaluation.result` events to GenAI operation spans for hallucination, bias, relevance, or custom eval signals. The Honeycomb docs confirm it's stored as a span event and displayed in the GenAI tab.
- **Confidence**: anecdotal
- **Quote**: "Attach `gen_ai.evaluation.result` events to GenAI operation spans for hallucination, bias, relevance, or any custom eval signal."
- **Our assessment**: This is aspirational — most teams don't have automated eval pipelines wired into their observability stack. The pattern is powerful in principle: attaching eval results to the same spans that carry token usage and latency gives you a cost/latency/quality triangle in one query. The article provides the attribute name but no code example for eval attachment, making this the least substantiated claim.

### Claim 13: Span naming follows a strict `<operation> <target>` pattern for the Agent Timeline
- **Evidence**: Both the blog post and the Honeycomb docs provide a span naming table. The docs page lists 8 operation types with their span name patterns: `chat {model}`, `execute_tool {tool_name}`, `invoke_agent {agent_name}`, `embeddings {model}`, `retrieval {data_source}`, `create_agent {agent_name}`, `generate_content {model}`, `text_completion {model}`.
- **Confidence**: settled (for Honeycomb's implementation)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The `<operation> <target>` naming convention is simple, grep-able, and machine-parseable. It encodes both the operation type and its target in the span name, making span lists readable without needing to inspect attributes. This is a good convention for the guide to recommend even for teams not using Honeycomb — it's framework-agnostic and follows OpenTelemetry span naming best practices of using a low-cardinality, human-readable name.

### Claim 14: Framework-specific guidance exists for OpenAI, Anthropic, and LangChain/LangGraph
- **Evidence**: The article provides a dedicated section covering each SDK/framework with specific integration patterns.
- **Confidence**: emerging
- **Quote**: "let the framework instrumentation own the LLM-layer spans, and you own the agent-layer and conversation-layer attributes."
- **Our assessment**: This is the universal pattern extracted from the framework-specific guidance. The article covers OpenAI Python SDK (auto-instrumentation via contrib packages), Anthropic Python SDK (same pattern), and LangChain/LangGraph (callback system wiring to OpenTelemetry). The key takeaway is consistent: framework auto-instrumentation handles LLM-layer detection; application code handles conversation and agent identity.

### Claim 15: OTel Collector transform processors can remap non-conforming agent telemetry to GenAI semantic conventions
- **Evidence**: The Honeycomb "Send Data: Agents" docs provide a complete, production-grade OTel Collector `transform` processor YAML configuration for remapping Claude Code's emitted spans to GenAI semconv. The config handles span renaming (`claude_code.interaction` → `invoke_agent {agent_name}`), attribute mapping (`session.id` → `gen_ai.conversation.id`), token alias remapping, and tool detail remapping gated behind environment variables.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is a high-value concrete artifact that extends Claim 4. Even when a tool (Claude Code) emits OTel-compatible telemetry, it uses its own naming conventions, not the GenAI semantic conventions. The Collector transform processor pattern bridges the gap without requiring code changes in the agent framework. This is directly applicable to the guide's observability chapter — the pattern applies to any agent framework that emits non-conforming OTel spans, not just Claude Code. The env-var gating (`OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`) for tool argument/result capture is a smart privacy-preserving pattern worth noting.

## Concrete Artifacts

### Artifact 1: Minimum Viable Agent Instrumentation (Python OTel SDK)

From the blog post, "A minimum viable example" section:

```python
import json
import uuid
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("my-agent")

def run_agent(user_message: str):
    conversation_id = str(uuid.uuid4())

    with tracer.start_as_current_span("invoke_agent support_agent") as span:
        span.set_attribute("gen_ai.conversation.id", conversation_id)
        span.set_attribute("gen_ai.agent.name", "support_agent")
        span.set_attribute("gen_ai.operation.name", "invoke_agent")

        return call_llm(user_message, conversation_id)

def call_llm(message: str, conversation_id: str):
    with tracer.start_as_current_span("chat gpt-4o") as span:
        span.set_attribute("gen_ai.conversation.id", conversation_id)
        span.set_attribute("gen_ai.agent.name", "support_agent")
        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.request.model", "gpt-4o")

        # ... actual LLM call ...

        span.set_attribute("gen_ai.response.model", "gpt-4o-2024-08-06")
        span.set_attribute("gen_ai.usage.input_tokens", 142)
        span.set_attribute("gen_ai.usage.output_tokens", 87)
        return result
```

### Artifact 2: Tool Execution Span with Error Propagation (Python OTel SDK)

From the blog post, "Tool calls" subsection:

```python
with tracer.start_as_current_span(f"execute_tool {tool_name}") as span:
    span.set_attribute("gen_ai.conversation.id", conversation_id)
    span.set_attribute("gen_ai.agent.name", "support_agent")
    span.set_attribute("gen_ai.operation.name", "execute_tool")
    span.set_attribute("gen_ai.tool.name", tool_name)
    span.set_attribute("gen_ai.tool.call.id", tool_call_id)
    span.set_attribute("gen_ai.tool.call.arguments", json.dumps(args))

    try:
        result = execute(tool_name, args)
        span.set_attribute("gen_ai.tool.call.result", json.dumps(result))
        span.set_attribute("gen_ai.response.finish_reasons", json.dumps(["stop"]))
        return result
    except Exception as e:
        span.set_attribute("error.type", type(e).__name__)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise
```

### Artifact 3: Multi-Agent Handoff Instrumentation (Python OTel SDK)

From the blog post, "Multi-agent instrumentation" section:

```python
# Orchestrator agent invoking a specialist agent
with tracer.start_as_current_span("invoke_agent billing_agent") as span:
    span.set_attribute("gen_ai.conversation.id", conversation_id)
    span.set_attribute("gen_ai.agent.name", "orchestrator")   # the caller
    span.set_attribute("gen_ai.operation.name", "invoke_agent")

    # billing_agent emits its own spans under
    # gen_ai.agent.name = "billing_agent"
    return billing_agent.handle(query, conversation_id)
```

### Artifact 4: Required Span Attributes Registry

From the Honeycomb "Send Data: Agents" documentation (`docs.honeycomb.io/send-data/agents`):

| Attribute | Type | Required | Purpose |
|---|---|---|---|
| `gen_ai.conversation.id` | string | Yes | Unique identifier for the conversation or session. Used to group all traces and spans belonging to the same agent conversation. |
| `gen_ai.agent.name` | string | Yes | Name of the agent emitting the span. Each agent should have a unique name. If omitted, shows as "Unknown." |
| `gen_ai.operation.name` | string | Yes | Operation type. Allowed values: `chat`, `create_agent`, `embeddings`, `execute_tool`, `generate_content`, `invoke_agent`, `invoke_workflow`, `retrieval`, `text_completion` |

### Artifact 5: Optional Span Attributes Registry

From the Honeycomb "Send Data: Agents" documentation:

| Attribute | Type | Purpose |
|---|---|---|
| `gen_ai.usage.input_tokens` | int | Tokens used in the GenAI input prompt |
| `gen_ai.usage.output_tokens` | int | Tokens used in the GenAI response |
| `gen_ai.request.model` | string | Name of the model requested |
| `gen_ai.response.model` | string | Name of the model that generated the response (can differ from requested) |
| `gen_ai.response.finish_reasons` | string[] | Why the model stopped, e.g., `["stop"]`, `["tool_calls"]` |
| `gen_ai.tool.name` | string | Name of the tool called by the agent |
| `gen_ai.tool.call.id` | string | Unique identifier for the tool call |
| `gen_ai.tool.call.arguments` | object \| json | Parameters passed to the tool call |
| `gen_ai.tool.call.result` | string | Result returned by the tool call |

### Artifact 6: Span Events (filterable at Collector)

From the Honeycomb "Send Data: Agents" documentation:

| Event Field | Type | Notes |
|---|---|---|
| `gen_ai.input.messages` | object \| json | Chat history or input prompts provided to the model. **May contain PII.** |
| `gen_ai.output.messages` | object \| json | Messages returned by the model. **May contain PII.** |
| `gen_ai.evaluation.result` | string | Attach events to review evaluations in the GenAI tab. |

### Artifact 7: Span Naming Convention Table

From the Honeycomb "Send Data: Agents" documentation:

| Operation | `gen_ai.operation.name` | Span Name Pattern |
|---|---|---|
| Chat | `chat` | `chat {model}` |
| Create GenAI agent | `create_agent` | `create_agent {agent_name}` |
| Tool execution | `execute_tool` | `execute_tool {tool_name}` |
| Agent invocation | `invoke_agent` | `invoke_agent {agent_name}` |
| Embeddings | `embeddings` | `embeddings {model}` |
| RAG retrieval | `retrieval` | `retrieval {data_source}` |
| Multimodal content generation | `generate_content` | `generate_content {model}` |
| Text completions | `text_completion` | `text_completion {model}` |

### Artifact 8: Error Handling Attributes

From the Honeycomb "Send Data: Agents" documentation (following OTel error recording spec):

- `error.type` / `exception.type`
- `error.message` / `exception.message`
- `error.stacktrace` / `exception.stacktrace`

Rule for tool call failures: "propagate the error status to the parent span."

### Artifact 9: OTel Collector Transform Processor — Claude Code Remapping

From the Honeycomb "Send Data: Agents" documentation (abbreviated — full YAML in source):

Key remapping rules applied by the `transform` processor:

1. **Every span**: set `gen_ai.agent.name`; map `session.id` → `gen_ai.conversation.id`
2. **`claude_code.interaction` span**: rename to `invoke_agent {agent_name}`; set `gen_ai.operation.name` = `"invoke_agent"`
3. **`claude_code.llm_request` span**: rename to `chat {model}` (only if `gen_ai.request.model` is non-nil); set `gen_ai.operation.name` = `"chat"`
4. **`claude_code.tool` span**: rename to `execute_tool {tool_name}`; set `gen_ai.operation.name` = `"execute_tool"`; map `tool_name` → `gen_ai.tool.name`
5. **Token aliases**: `input_tokens` → `gen_ai.usage.input_tokens`; `output_tokens` → `gen_ai.usage.output_tokens`; `cache_read_tokens` → `gen_ai.usage.cache_read_input_tokens`; `cache_creation_tokens` → `gen_ai.usage.cache_creation_input_tokens`
6. **Tool details** (gated behind `OTEL_LOG_TOOL_DETAILS=1` and `OTEL_LOG_TOOL_CONTENT=1`): `tool_input` → `gen_ai.tool.call.arguments`; `new_context` → `gen_ai.tool.call.result`. `gen_ai.tool.call.id` has no Claude Code equivalent and stays absent.

Environment: `OTEL_LOG_TOOL_DETAILS=1` and `OTEL_LOG_TOOL_CONTENT=1` must be set for tool argument/result remapping.

### Artifact 10: Agent Timeline UI Feature Summary

From the Honeycomb "Agent Timeline" documentation (`docs.honeycomb.io/investigate/observe/agent-timeline`):

**Conversation-level metrics bar:**
- **Duration**: How long the conversation or session lasted
- **Traces**: Count of traces
- **LLM Calls**: Count of spans where `gen_ai.operation.name` ∈ `{"chat", "generate_content", "text_completion"}`
- **Tool Calls**: Count of spans where `gen_ai.operation.name` = `"execute_tool"`
- **Failures**: Error/exception count
- **Total Tokens**: Combined input and output tokens

**Timeline view**: GenAI spans grouped by `gen_ai.agent.name` into swim lanes; within each agent group, spans nested by operation type (Agent Invocations, LLM Operations, Tool Calls). "Show Failures Only" toggle. Expand/collapse agent groups.

**Span detail panel** (three tabs):
- **Gen AI**: Operation, Conversation ID, Agent, plus type-specific fields (messages, parameters, tool details)
- **Fields**: All span fields, filterable by name or value
- **Links**: Any links present on the span

**Navigation entry points**:
1. Main navigation → Agent Timeline
2. Enter a conversation ID directly
3. Browse recent conversations list (last 60 days)
4. From a Query Results view: select a `gen_ai.conversation.id` to open that conversation

## Cross-References

- **Corroborates**: This eval note corroborates the baseline DeepSeek/Flash source note at `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (issue #2). All 15 claims extracted here align with the 12 claims in the baseline. Both notes extract the same three required attributes, the same tool call error propagation pattern, the same multi-agent handoff pattern, and the same OTel Collector remapping configuration.

- **Contradicts**: None. No contradictions found between this eval extraction and the baseline note.

- **Extends**: This eval note extends the baseline in two minor ways:
  1. **Claim 7** explicitly extracts the handoff ownership rule ("The calling agent emits the `invoke_agent` span, not the agent being called") as a separate claim, whereas the baseline folds it into Claim 6.
  2. **Claim 9** explicitly calls out cache read/creation token attributes as a forward-looking pattern for prompt caching — the baseline mentions these attributes in Artifact 5 but doesn't elevate them to a separate claim.

- **Novel**: No novel claims — this is the same source as the baseline. The extraction depth and claim count (15 vs 12) are comparable, with minor differences in how claims are grouped.

## Guide Impact

- **Chapter 02 (Observability)**: This source provides the concrete attribute-level contract for tracing AI agents with OpenTelemetry. Recommend adding a new section or subsection covering the three required attributes (`gen_ai.conversation.id`, `gen_ai.agent.name`, `gen_ai.operation.name`) as the baseline for any agent observability setup. The span naming convention table (Artifact 7) and the auto-vs-manual instrumentation boundary (Claim 4) should be adapted as recommended patterns. The OTel Collector transform processor pattern (Artifact 9) is directly applicable as a "bridge non-conforming telemetry" pattern.

- **Chapter 05 (LLM Ops Reliability)**: This source's failure-signal chain (Claim 11 — `error.type` + span status → "Show Failures Only" navigation) and tool-call instrumentation pattern (Artifact 2) are directly applicable to production debugging workflows. The model version drift pattern (Claim 8) should be cited as a specific reliability practice: always capture both `gen_ai.request.model` and `gen_ai.response.model` to detect silent provider-side upgrades. The prompt/response capture with PII mitigation (Claim 10) should inform any guidance on LLM I/O logging in production.

- **New coverage opportunity**: If the guide ever adds a chapter or appendix on agent framework instrumentation, the Claude Code remapping config (Artifact 9) and the framework-specific guidance from the blog (OpenAI, Anthropic, LangChain) provide ready-to-adapt patterns.

## Extraction Notes

- **Linked pages followed**: Two Honeycomb documentation pages were fetched for additional depth: `docs.honeycomb.io/investigate/observe/agent-timeline` (Agent Timeline UI/feature specification) and `docs.honeycomb.io/send-data/agents` (agent instrumentation attribute registry and Claude Code remapping config). Both added substantive detail beyond the blog post — the full set of 8 operation types (`retrieval`, `create_agent`, `invoke_workflow` were not in the blog), the Claude Code Collector configuration, and the distinction between span attributes and span events for PII-sensitive data.
- **Quote verification**: All quotes in Claims 1-12 and 14 were verified against the source URL via targeted WebFetch. Quotes shorter than 125 characters were extracted verbatim. Where no exact quote captures the claim, the paraphrase is noted in `Our assessment`.
- **Code blocks**: All three Python code examples were extracted verbatim from the blog post. The attribute registries (Artifacts 4-7) were transcribed from the Honeycomb documentation tables. The Claude Code remapping rules (Artifact 9) were summarized from the Collector YAML config in the docs.
- **Comparison to baseline**: This eval note was produced by qwen3.5-plus (zen backend) as part of a candidate model evaluation. The extraction depth (15 claims vs 12 in baseline), artifact coverage (10 artifacts vs 10 in baseline), and cross-reference analysis are comparable. The main differences are organizational: this note separates the handoff ownership rule (Claim 7) and cache token attributes (Claim 9) into distinct claims, whereas the baseline folds them into broader claims.
