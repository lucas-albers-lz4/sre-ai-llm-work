---
source_url: https://www.honeycomb.io/blog/instrumenting-ai-agents-agent-timeline-opentelemetry-guide
source_type: blog-post
title: "Instrumenting AI Agents for the Agent Timeline: A Practical OpenTelemetry Guide"
author: Dan Juengst (Honeycomb)
date_published: 2026-06-29
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: emerging
issue: "#2-hy3-eval"
---

# Instrumenting AI Agents for the Agent Timeline

> A practitioner guide from Honeycomb engineering on instrumenting AI agents with OpenTelemetry GenAI semantic conventions, centered on the assertion that the LLM is rarely the root cause of agent failures — tool calls, downstream services, and multi-agent handoffs are where agents actually break, and the Agent Timeline makes these first-class debugging primitives.

## Source Context

- **Type**: blog-post (practitioner writeup from Honeycomb engineering)
- **Author credibility**: Dan Juengst is a Honeycomb engineer writing on the company's official engineering blog. Honeycomb operates an observability platform that includes the Agent Timeline feature described in the article (announced in Early Access May 2026). The author has direct experience building and instrumenting the patterns described. The article is accompanied by a live product feature and public documentation at `docs.honeycomb.io`. The guidance is consistent with the OpenTelemetry GenAI semantic conventions (a vendor-neutral standard), not purely a Honeycomb-specific pitch.
- **Scope**: Covers end-to-end OpenTelemetry instrumentation for AI agents — the three required attributes, the definition of a "GenAI span," span naming, tool call instrumentation with error propagation, multi-agent handoff patterns, token tracking, model identification (request vs response), prompt/response capture with PII caveats, failure signal propagation, evaluation event attachment, and framework-specific guidance for OpenAI, Anthropic, and LangChain. Also covers the OTel Collector transform processor for remapping non-conforming telemetry (Claude Code example), drawn from linked Honeycomb docs. Does NOT cover: dedicated metrics/logs collection design, alerting rules, SLO definitions, or cost optimization beyond per-span token counting.
- **Linked pages followed for extraction**: `docs.honeycomb.io/send-data/agents` (agent instrumentation attribute registry, span-naming table, agent-to-agent guidance, error-recording spec, Claude Code Collector remapping config) and `docs.honeycomb.io/investigate/observe/agent-timeline` (Agent Timeline UI feature spec: conversation metrics, swim-lane timeline, Gen AI tab). Both were fetched and their prose read verbatim; they added the full 8-value `gen_ai.operation.name` registry, the span-naming table, and the Claude Code Collector YAML that the blog post only summarizes.

## Extracted Claims

### Claim 1: The LLM is rarely the root cause of agent failures
- **Evidence**: Stated as the article's central thesis — both in the page's meta description and in the closing of the body. The surrounding argument (tool calls, handoffs, downstream spans are the actual failure surface) is developed across the "Tool calls," "Multi-agent instrumentation," and "What you'll see when it works" sections.
- **Confidence**: emerging
- **Quote**: "The LLM is rarely the root cause of agent failures."
- **Our assessment**: Plausible and consistent with agent architecture: LLM calls are stateless API requests with well-defined error surfaces, whereas tool execution involves arbitrary I/O, side effects, and external dependencies. Useful as a debugging heuristic — start at tool calls and handoff boundaries, not the model response. However, this is a practitioner observation, not a quantitative study; no failure-distribution data is presented. Note: the body makes the same point with "But the root cause isn't often the LLM" and "The model is rarely the root cause" — same claim, softer wording.

### Claim 2: Three attributes are mandatory on every span for the Agent Timeline to function
- **Evidence**: Concrete attribute names with "required" typing in the Honeycomb "Send Data: Agents" docs, plus the blog's "three attributes you need to start" section. The docs specify these as required fields with explicit grouping behavior; the blog states the consequence of omission (LLM-only view).
- **Confidence**: settled (for any Agent-Timeline-style view; the OTel GenAI semconv codifies the same three as the minimum grouping contract)
- **Quote**: "To make that work, every span in your agent's execution chain needs three attributes:"
- **Our assessment**: `gen_ai.conversation.id` (grouping key), `gen_ai.agent.name` (swim lanes), `gen_ai.operation.name` (type-specific UI rendering) form the minimum viable contract for any agent tracing system, not just Honeycomb's. This is the single most extractable pattern in the source — any guide chapter on agent observability should reference this trio as the baseline. The blog also stresses propagation: "Thread conversation_id through your call stack so every span, including downstream HTTP clients, database queries, and queue workers can attach it."

### Claim 3: A GenAI span is any span in the execution chain, not just LLM calls
- **Evidence**: The blog explicitly broadens the definition, and the Agent Timeline docs confirm the view nests non-GenAI spans under GenAI operation spans grouped by agent.
- **Confidence**: emerging
- **Quote**: "One subtlety that matters: a "GenAI span" is not just an LLM call. It's any span anywhere in the execution chain triggered by an agent, including downstream database queries, third-party API calls, or background jobs that ran because the agent decided to call a tool."
- **Our assessment**: A critical conceptual expansion. Many developers think "LLM observability" = instrument the model call; this source argues the observability surface is the entire agent execution graph. The implication: conversation-ID propagation into downstream systems is not optional — without it you get "the LLM-only view that dedicated AI observability tools stop at." This aligns with distributed-tracing best practice applied to a new domain, and directly supports Claim 1 (you can't see the real failure surface if downstream spans aren't grouped).

### Claim 4: Auto-instrumentation covers LLM-layer spans, but agent-layer attributes must be hand-authored
- **Evidence**: Same pattern given for OpenAI SDK, Anthropic SDK, and LangChain/LangGraph. The docs reinforce it with the Claude Code remapping example — even when a tool emits OTel-compatible telemetry, it uses its own naming, so remapping is needed.
- **Confidence**: emerging
- **Quote**: "Auto-instrumentation can't infer your conversation boundaries or your agent identity. That's a property of your application."
- **Our assessment**: Practical and non-obvious. Framework auto-instrumentation can detect LLM calls via known library hooks, but "which conversation does this belong to?" and "which agent am I?" are application-level concepts no framework can infer. The repeated heuristic — "let the framework instrumentation own the LLM-layer spans, and you own the agent-layer and conversation-layer attributes" — is concise and actionable. The boundary is real but partial: Anthropic/OpenAI contrib auto-instrumentation supplies the LLM-layer spans, yet conversation scoping still requires a parent span you control.

### Claim 5: Tool calls are where most agentic failures live
- **Evidence**: The blog provides a complete tool execution span example with try/except error propagation; the docs specify `error.type`/`error.message`/`error.stacktrace` and require tool-call failure propagation to the parent span.
- **Confidence**: emerging
- **Quote**: "Tool calls are where most agentic failures live."
- **Our assessment**: Consistent with Claims 1 and 3 — tool execution spans are the highest-value instrumentation target because they involve arbitrary external I/O. The concrete pattern (set `error.type`, propagate error status to parent, use the Timeline's "Show Failures Only" filter) is directly applicable to any agent observability setup. The article's error-handling code (`span.set_attribute("error.type", type(e).__name__)` + `span.set_status(Status(StatusCode.ERROR, str(e)))`) is production-grade.

### Claim 6: Multi-agent systems require distinct agent names per sub-agent and an explicit caller-emitted handoff span
- **Evidence**: The blog's multi-agent section gives two rules; the docs restate both and add that missing names surface as "Unknown." Code example shows the orchestrator emitting `invoke_agent billing_agent` under `gen_ai.agent.name = "orchestrator"`.
- **Confidence**: emerging
- **Quote**: "Sub-agents use their own distinct names; they don't inherit from the parent."
- **Our assessment**: The most opinionated claim. Not all frameworks model sub-agents with distinct identities — some treat them as internal function calls under one agent name. The pattern (caller emits `invoke_agent`, callee uses its own name) creates clean swim-lane separation but requires discipline: every agent named, consistently. Good architecture, possibly aspirational for ad-hoc agent graphs. The docs add the failure mode: "If gen_ai.agent.name is omitted on a span, it will show up as "Unknown" on the Agent Timeline."

### Claim 7: Capture both requested and actual response model names to debug silent provider-side model upgrades
- **Evidence**: Concrete attribute names (`gen_ai.request.model`, `gen_ai.response.model`) with a worked example: request `gpt-4o`, receive `gpt-4o-2024-08-06`. The docs list both as optional string attributes and note "This can differ from the requested model."
- **Confidence**: anecdotal
- **Quote**: "Capturing both is how you debug behavior changes after a silent provider-side model upgrade."
- **Our assessment**: Sharp operational insight. Providers routinely roll out minor version updates that change behavior subtly. Having both attributes on every LLM span yields a queryable diff — "show conversations where response model ≠ request model, correlated with error-rate changes." Generalizes beyond OpenAI to any provider.

### Claim 8: Prompt/response capture accelerates root-cause investigation but requires PII handling
- **Evidence**: The blog lists `gen_ai.input.messages` and `gen_ai.output.messages` as span events (deliberate, so a Collector can filter them). The docs warn "GenAI prompts or chats may contain PII or other sensitive data" and prescribe span events so "your OTel Collector can filter them before they reach Honeycomb."
- **Confidence**: settled
- **Quote**: "These make root-cause investigation dramatically faster because you can read what the agent was told and what it said."
- **Our assessment**: The source handles PII honestly. Storing prompt/response as span events rather than attributes is a meaningful architectural decision: events can be stripped by a Collector processor without code changes. The three-tier mitigation (redact at app layer, scrub at Collector, restrict to non-prod) covers teams at different maturity levels. This should be the guide's recommended pattern for any LLM I/O capture. Note the conditional "by default" in the blog ("They also capture PII and sensitive data by default") — the risk is default-on, so gating is mandatory, not optional.

### Claim 9: Setting `error.type` and propagating error status turns failures into first-class navigation primitives
- **Evidence**: The tool-call code sets `error.type` and `span.set_status(Status(StatusCode.ERROR))` in the except block; the Agent Timeline docs describe a "Show Failures Only" toggle and a conversation-level failure count that depend on these signals.
- **Confidence**: emerging
- **Quote**: "This is what turns failures into first-class navigation primitives instead of needles in a haystack."
- **Our assessment**: Standard OpenTelemetry error semantics applied to a new, high-entropy domain. Without `error.type` on spans, an operator searching failures across thousands of agent conversations has no queryable surface. Low-effort, high-impact: two lines in the exception handler. The docs make the rule explicit: "For tool call failures, propagate the error status to the parent span."

### Claim 10: An OTel Collector transform processor can remap non-conforming agent telemetry to GenAI semantic conventions
- **Evidence**: The Honeycomb "Send Data: Agents" docs provide a complete, production-grade OTel Collector `transform` processor YAML for remapping Claude Code's emitted spans to GenAI semconv (span renaming, attribute mapping, token alias remapping, tool-detail remapping).
- **Confidence**: emerging
- **Quote**: "Claude Code can emit telemetry using the OpenTelemetry protocol, but does not yet use the OpenTelemetry semantic conventions."
- **Our assessment**: High-value concrete artifact that extends Claim 4. Even when a tool emits OTel-compatible telemetry, it uses its own naming; the transform processor bridges the gap without code changes in the agent framework. Applies to any framework emitting non-conforming OTel spans, not just Claude Code. The env-var gating (`OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`) for tool argument/result capture is a smart privacy-preserving pattern.

### Claim 11: Evaluation results should attach as span events to GenAI operation spans
- **Evidence**: The blog mentions `gen_ai.evaluation.result` as an event closing the cost/latency/quality loop; the docs confirm: "Attach gen_ai.evaluation.result events to the GenAI operation span to review evaluations in the GenAI tab."
- **Confidence**: anecdotal
- **Quote**: "Attach gen_ai.evaluation.result events to the GenAI operation span to review evaluations in the GenAI tab."
- **Our assessment**: Aspirational for most teams (few have automated eval pipelines wired into observability). The pattern is powerful in principle — eval results on the same spans as token usage and latency give a cost/latency/quality triangle in one query. The docs provide the verbatim event name and storage location; the blog provides no code example, so this is the least substantiated claim.

### Claim 12: Span naming follows a strict `<operation> <target>` pattern for the Agent Timeline
- **Evidence**: Both the blog and the "Send Data: Agents" docs provide a span-naming table. The docs list 8 operation types with patterns: `chat {model}`, `create_agent {agent_name}`, `execute_tool {tool_name}`, `invoke_agent {agent_name}`, `embeddings {model}`, `retrieval {data_source}`, `generate_content {model}`, `text_completion {model}`.
- **Confidence**: settled (for Honeycomb's implementation; the convention is framework-agnostic and follows OTel low-cardinality naming guidance)
- **Quote**: "Naming your spans this way ensures the Agent Timeline can understand the operation type and display it meaningfully."
- **Our assessment**: Simple, grep-able, machine-parseable — encodes operation type and target in the name so span lists are readable without inspecting attributes. Good for the guide to recommend even for non-Honeycomb teams. Note the docs reveal three operation types the blog omits: `create_agent`, `retrieval`, `invoke_workflow` (the blog's `gen_ai.operation.name` list in code only shows chat/execute_tool/invoke_agent).

### Claim 13: Without conversation-ID propagation into downstream spans you get an LLM-only view that misses the real failure surface
- **Evidence**: The blog's "three attributes" section argues the conversation ID must reach downstream HTTP clients, database queries, and queue workers; otherwise you reproduce the LLM-only view that dedicated AI observability tools stop at.
- **Confidence**: emerging
- **Quote**: "Without the conversation ID propagating into your downstream system spans, you get the LLM-only view that dedicated AI observability tools stop at, except in production."
- **Our assessment**: This is the operational payoff of Claim 2/3 and the refutation of the "just instrument the LLM" instinct in Claim 1. The phrase "except in production" is a pointed jab: dedicated AI-observability tools give an LLM-only lens even where they claim more. The claim is sound — distributed tracing has always required context propagation into downstream services; agents just make the downstream work (tools, handoffs) the dominant failure surface.

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
(Source: honeycomb.io blog, "A minimum viable example")

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
(Source: honeycomb.io blog, "Tool calls")

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
(Source: honeycomb.io blog, "Multi-agent instrumentation")

### Artifact 4: Required Span Attributes Registry

From the Honeycomb "Send Data: Agents" documentation (`docs.honeycomb.io/send-data/agents`):

| Attribute | Type | Required | Purpose |
|---|---|---|---|
| `gen_ai.conversation.id` | string | Yes | Unique identifier for the conversation or session. Used to group all traces and spans belonging to the same agent conversation. |
| `gen_ai.agent.name` | string | Yes | Name of the agent emitting the span. In multi-agent workflows each agent should have a unique name. |
| `gen_ai.operation.name` | string | Yes | Type of agentic operation occurring: `chat`, `create_agent`, `embeddings`, `execute_tool`, `generate_content`, `invoke_agent`, `invoke_workflow`, `retrieval`, `text_completion` |

### Artifact 5: Optional Span Attributes Registry

From the Honeycomb "Send Data: Agents" documentation:

| Attribute | Type | Purpose |
|---|---|---|
| `gen_ai.usage.input_tokens` | int | Number of tokens used in the GenAI input prompt. |
| `gen_ai.usage.output_tokens` | int | Number of tokens used in the GenAI response. |
| `gen_ai.request.model` | string | Name of the model requested. |
| `gen_ai.response.model` | string | Name of the model that generated the response. This can differ from the requested model. |
| `gen_ai.response.finish_reasons` | string[] | Why the model stopped generating tokens. Examples: `["stop"]`, `["tool_calls"]`, `["stop", "length"]` |
| `gen_ai.tool.name` | string | Name of the tool called by the agent. |
| `gen_ai.tool.call.id` | string | Unique identifier for the tool call. |
| `gen_ai.tool.call.arguments` | object \| json | Parameters passed to the tool call. |
| `gen_ai.tool.call.result` | string | Result returned by the tool call (if any). |

### Artifact 6: Span Events (filterable at the Collector)

From the Honeycomb "Send Data: Agents" documentation:

| Event Field | Type | Notes |
|---|---|---|
| `gen_ai.input.messages` | object \| json | Chat history or input prompts provided to the model. **May contain PII.** |
| `gen_ai.output.messages` | object \| json | Messages returned by the model. **May contain PII.** |
| `gen_ai.evaluation.result` | string | Attach to the GenAI operation span to review evaluations in the GenAI tab. |

The docs' rationale for span events over attributes: "Store them in span events where your OTel Collector can filter them before they reach Honeycomb."

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

From the Honeycomb "Send Data: Agents" documentation (following the OTel error-recording spec):

- `error.type` / `exception.type`
- `error.message` / `exception.message`
- `error.stacktrace` / `exception.stacktrace`

Rule for tool-call failures: "For tool call failures, propagate the error status to the parent span."

### Artifact 9: OTel Collector Transform Processor — Claude Code Remapping (verbatim YAML)

From the Honeycomb "Send Data: Agents" documentation. This is the full production-grade config the blog summarizes:

```yaml
processors:
  # Detailed Beta names spans `claude_code.*` and uses bare-namespace
  # attribute keys (session.id, input_tokens, …). The transform processor
  # remaps both names and attributes to the GenAI semconv on the way
  # through. Statements run in order, per OTTL context.
  transform:
    error_mode: ignore
    trace_statements:
      - context: resource
        statements:
          # Set service.name to identify your agent.
          - set(attributes["service.name"], "<AGENT NAME>")
      - context: span
        statements:
          # ---- Identity attributes added to every span ----
          # The AI Conversations viewer and Agent Timeline both key on
          # gen_ai.conversation.id; Detailed Beta carries the same value
          # under `session.id`.
          - set(attributes["gen_ai.agent.name"], "<AGENT NAME>")
          - set(attributes["gen_ai.conversation.id"], attributes["session.id"]) where attributes["session.id"] != nil
          # ---- claude_code.interaction → invoke_agent claude ----
          # Order matters. Rename the span first, then set
          # gen_ai.operation.name keyed off the new name. Detailed Beta
          # emits exactly one interaction span per Claude invocation.
          - set(name, "invoke_agent <AGENT NAME>") where name == "claude_code.interaction"
          - set(attributes["gen_ai.operation.name"], "invoke_agent") where name == "invoke_agent <AGENT NAME>"
          # ---- claude_code.llm_request → chat {model} ----
          # gen_ai.request.model is already populated by Detailed Beta.
          # If it is missing on some build, leave the original name in
          # place rather than renaming to "chat ".
          - set(name, Concat(["chat ", attributes["gen_ai.request.model"]], "")) where name == "claude_code.llm_request" and attributes["gen_ai.request.model"] != nil
          - set(attributes["gen_ai.operation.name"], "chat") where IsMatch(name, "^chat ")
          # ---- claude_code.tool → execute_tool {tool_name} ----
          # Detailed Beta names the wrapping tool span `claude_code.tool`
          # and carries the tool identity in the `tool_name` attribute.
          - set(name, Concat(["execute_tool ", attributes["tool_name"]], "")) where name == "claude_code.tool" and attributes["tool_name"] != nil
          - set(attributes["gen_ai.operation.name"], "execute_tool") where IsMatch(name, "^execute_tool ")
          - set(attributes["gen_ai.tool.name"], attributes["tool_name"]) where IsMatch(name, "^execute_tool ")
          # ---- Token alias (Detailed Beta llm_request) ----
          # Detailed Beta puts some tokens in gen_ai.* and others in the
          # bare namespace. Alias the bare ones up so the GenAI consumers
          # see the full set on each chat {model} span.
          - set(attributes["gen_ai.usage.input_tokens"], attributes["input_tokens"]) where attributes["input_tokens"] != nil
          - set(attributes["gen_ai.usage.output_tokens"], attributes["output_tokens"]) where attributes["output_tokens"] != nil
          - set(attributes["gen_ai.usage.cache_read_input_tokens"], attributes["cache_read_tokens"]) where attributes["cache_read_tokens"] != nil
          - set(attributes["gen_ai.usage.cache_creation_input_tokens"], attributes["cache_creation_tokens"]) where attributes["cache_creation_tokens"] != nil
          # ---- Tool args / result remap ----
          # With OTEL_LOG_TOOL_DETAILS=1 + OTEL_LOG_TOOL_CONTENT=1
          # claude_code.tool spans carry two content attributes:
          #   * `tool_input`  — the tool arguments JSON, prefixed with "[TOOL INPUT: <Name>]\n"
          #   * `new_context` — the tool result JSON, prefixed with "[TOOL RESULT: <Name>]\n"
          # Alias them onto gen_ai.tool.call.arguments / .result.
          # gen_ai.tool.call.id has no Detailed Beta equivalent, so it stays absent.
          - set(attributes["gen_ai.tool.call.arguments"], attributes["tool_input"]) where IsMatch(name, "^execute_tool ") and attributes["tool_input"] != nil
          - set(attributes["gen_ai.tool.call.result"], attributes["new_context"]) where IsMatch(name, "^execute_tool ") and attributes["new_context"] != nil
```
(Source: docs.honeycomb.io/send-data/agents, "Remapping existing telemetry")

### Artifact 10: Agent Timeline UI Feature Summary

From the Honeycomb "Agent Timeline" documentation (`docs.honeycomb.io/investigate/observe/agent-timeline`):

**Conversation-level metrics bar:**
- **Duration**: How long the conversation or session lasted
- **Traces**: Count of traces
- **LLM Calls**: Number of GenAI spans where `gen_ai.operation.name` ∈ `{"chat", "generate_content", "text_completion"}`
- **Tool Calls**: Count of GenAI spans where `gen_ai.operation.name` = `"execute_tool"`
- **Failures**: Error/exception count
- **Total Tokens**: Total input + output tokens

**Timeline view**: GenAI spans grouped by `gen_ai.agent.name` into swim lanes; within each agent group, spans nested by operation type (Agent Invocations, LLM Operations, Tool Calls). "Show Failures Only" toggle (`Toggle Show Failures Only to only show spans with errors on the timeline`). Expand/collapse agent groups.

**Gen AI tab (three detail tabs: Gen AI, Fields, Links)** — for LLM operation spans shows Provider, Model, Response Model, Parameters (Temperature, Max Tokens, Top P), Finish Reasons, Performance (TTFT, Input/Output/Cache tokens), and the Messages section.

**Navigation entry points** (per docs): Select Agent Timeline from main navigation; enter a `gen_ai.conversation.id` directly or browse recent conversations; or select a `gen_ai.conversation.id` from a Query Results view to open that conversation. The Conversations view lists agent conversations from the last 60 days with agent counts, tool calls, tokens, P95 latency, and failure counts.

## Cross-References

- **Corroborates**: None of the other merged source notes cover OpenTelemetry or GenAI semantic conventions. `blog-pagerduty-production-ai-agent-gaps.md` discusses observability only at a high level (traces/logs/metrics, a referenced companion "end-to-end observability for AI agents" article) and does not endorse or describe specific GenAI span attributes — so it neither corroborates nor contradicts this source's concrete patterns. This note's claims stand as the corpus's first detailed treatment of agent OTel instrumentation.
- **Contradicts**: None. No existing note opposes the three-attribute contract, the auto-vs-manual boundary, the handoff pattern, or the Collector remap approach.
- **Extends**: None directly — this source establishes a new coverage domain (agent observability with OTel GenAI semconv) that future sources can build on.
- **Novel**: The entire content domain is novel to the corpus:
  - The three-attribute contract (`gen_ai.conversation.id`, `gen_ai.agent.name`, `gen_ai.operation.name`) as the minimum viable agent tracing surface
  - The "GenAI span = any execution-chain span" definition and the downstream-propagation requirement
  - The auto-vs-manual instrumentation boundary rule ("framework owns LLM-layer, you own agent-layer")
  - The multi-agent handoff span pattern with distinct sub-agent naming
  - The OTel Collector transform processor pattern for remapping non-conforming agent telemetry to GenAI semconv (Claude Code config)
  - The Agent Timeline UI data model (swim lanes, operation-type nesting, conversation-level metric aggregation)
- **Baseline comparison (this is the Hy3 eval replay of golden issue #2)**: The merged DeepSeek baseline for this URL is `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (issue `#2`, PR #6). This Hy3 note re-extracted the same blog post plus both linked Honeycomb docs pages independently. Agreement: all 12 baseline claims are reproduced and their thesis, attributes, patterns, and artifacts match. Refinements in this eval: (a) Claim 1's thesis quote is sourced from the page's meta description ("The LLM is rarely the root cause of agent failures.") — the baseline also cites this sentence but presents it without noting it is the meta description rather than body prose; the body states the same point as "But the root cause isn't often the LLM" and "The model is rarely the root cause." (b) Claims 10, 11, and 12 here quote the linked docs verbatim (Claude Code transform config rationale, the `gen_ai.evaluation.result` event line, and the span-naming-table rationale) where the baseline marked those as "(no direct quote; see paraphrase)." (c) This note adds Claim 13 (downstream-ID propagation / LLM-only-view failure) and captures the full verbatim Claude Code Collector YAML (Artifact 9) rather than a summarized rule list. No contradiction with the baseline — this is an independent corroboration at the editor's request.

## Guide Impact

- **Chapter 02 (Observability)**: This source provides the concrete attribute-level contract for tracing AI agents with OpenTelemetry. Recommend adding a section covering the three required attributes (`gen_ai.conversation.id`, `gen_ai.agent.name`, `gen_ai.operation.name`) as the baseline for any agent observability setup. The span-naming convention table (Artifact 7) and the auto-vs-manual instrumentation boundary (Claim 4) should be adapted as recommended patterns. The OTel Collector transform processor pattern (Artifact 9) is directly applicable as a "bridge non-conforming telemetry" pattern, and Claim 13 should inform any guidance on context propagation into downstream services.

- **Chapter 05 (LLM Ops Reliability)**: The failure-signal chain (Claim 9 — `error.type` + span status → "Show Failures Only" navigation) and tool-call instrumentation pattern (Artifact 2) are directly applicable to production debugging. The model version drift pattern (Claim 7) should be cited as a specific reliability practice: always capture both `gen_ai.request.model` and `gen_ai.response.model` to detect silent provider-side upgrades. The prompt/response capture with PII mitigation (Claim 8) should inform any guidance on LLM I/O logging in production.

- **New coverage opportunity**: If the guide adds a chapter or appendix on agent framework instrumentation, the Claude Code remapping config (Artifact 9) and the framework-specific guidance (OpenAI/Anthropic/LangChain, Claim 4) provide ready-to-adapt patterns.

## Extraction Notes

- **Linked pages followed (verbatim)**: Two Honeycomb documentation pages were fetched and read in full: `docs.honeycomb.io/send-data/agents` (attribute registry, span-naming table, agent-to-agent guidance, error-recording spec, Claude Code Collector remapping YAML) and `docs.honeycomb.io/investigate/observe/agent-timeline` (UI feature spec). Both added substantive detail beyond the blog post — the full 8-value `gen_ai.operation.name` registry (`retrieval`, `create_agent`, `invoke_workflow` are absent from the blog's code examples), the complete Claude Code Collector YAML, and the conversation-metric definitions. All quotes from these pages are copied character-for-character from the fetched docs text (including the docs' own typos, e.g., "Cache Read Rokens" in the Agent Timeline doc, which I did not reproduce because I cited the registry table from the send-data page instead).
- **Quote sourcing**: Every `Quote` field was verified against the fetched source text. Blog quotes come from the rendered article body or meta description; docs quotes come from the rendered docs pages. Where a claim's meaning is my synthesis across sentences (e.g., Claim 1's assessment), it is placed in `Our assessment`, not `Quote`.
- **Code blocks**: All three Python examples (Artifacts 1–3) are transcribed verbatim from the blog post. The attribute registries (Artifacts 4–6), span-naming table (Artifact 7), and error attributes (Artifact 8) are transcribed from the send-data docs tables. The Claude Code Collector YAML (Artifact 9) is the full config from the send-data docs, not a paraphrase.
- **Eval context**: This note is the Hy3-model replay of golden issue #2, written to the `*-hy3-eval.md` filename and `issue: "#2-hy3-eval"` frontmatter per the eval protocol. It does not modify the merged DeepSeek baseline note; see Cross-References → Baseline comparison.
