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
issue: "#2-deepseek-v4-flash-free-eval"
---

# Instrumenting AI Agents for the Agent Timeline

> A practitioner guide from Honeycomb engineering on instrumenting AI agents with OpenTelemetry GenAI semantic conventions. The central thesis is that the LLM is rarely the root cause of agent failures — tool calls, downstream service spans, and multi-agent handoffs carry the real failure signals, and the Agent Timeline makes these first-class debugging primitives.

## Source Context

- **Type**: blog-post (practitioner writeup from Honeycomb engineering)
- **Author credibility**: Dan Juengst is a Honeycomb engineer writing on the company's official engineering blog. Honeycomb operates the observability platform that includes the Agent Timeline feature described in the article. The author has direct experience building and instrumenting the patterns described. The article is accompanied by a live product feature (Agent Timeline, announced May 2026) and public documentation at `docs.honeycomb.io`.
- **Scope**: Covers end-to-end OpenTelemetry instrumentation for AI agents — the three required attributes for Agent Timeline, token tracking, model identification, tool call instrumentation with error propagation, multi-agent handoff patterns, prompt/response capture with PII caveats, evaluation result attachment, and framework-specific guidance for OpenAI, Anthropic, and LangChain SDKs. Also includes span naming conventions. Does NOT cover: metrics collection, alerting, SLO definitions, or cost optimization beyond token counting.

## Extracted Claims

### Claim 1: The LLM is rarely the root cause of agent failures
- **Evidence**: The article's opening and closing paragraphs state this as its central operating thesis. The author grounds this in operational experience building and debugging AI agents, reinforced by the article's structure which devotes most of its space to tool calls, handoffs, and downstream service spans rather than LLM call instrumentation.
- **Confidence**: emerging
- **Quote**: "The LLM is rarely the root cause of agent failures."
- **Our assessment**: This is presented as a practitioner observation rather than a quantitative study — no failure-distribution data is cited. However, it is consistent with the architectural reality that LLM calls are stateless API requests with bounded error surfaces, while tool execution involves arbitrary I/O and external dependencies. The article's framing is valuable as a debugging heuristic: start investigation at tool calls and handoff boundaries. We accept this as a useful pattern, not a settled fact.

### Claim 2: Three attributes are mandatory on every span for Agent Timeline to function
- **Evidence**: The article specifies three required attributes with concrete names, types, and scope rules. It explains that "every span in your agent's execution chain needs three attributes" and describes the consequence of omission. The Honeycomb docs referenced in the article specify these as required fields.
- **Confidence**: settled (for Honeycomb's Agent Timeline; the broader OTel GenAI semantic conventions codify similar requirements)
- **Quote**: "To make that work, every span in your agent's execution chain needs three attributes:"
- **Our assessment**: These three attributes (`gen_ai.conversation.id`, `gen_ai.agent.name`, `gen_ai.operation.name`) form the minimum viable contract for any agent tracing system. The conversation ID is the grouping key, the agent name creates swim lanes, and the operation name enables type-specific UI rendering. This is the single most extractable pattern from the source — any guide chapter on agent observability should reference this trio as the baseline instrumentation contract.

### Claim 3: A GenAI span is not just an LLM call — it's any span in the agent's execution chain
- **Evidence**: The article explicitly broadens the definition: "a 'GenAI span' is not just an LLM call." It explains that downstream database queries, third-party API calls, and background jobs that execute because the agent decided to do something all qualify as GenAI spans if they carry the conversation ID.
- **Confidence**: emerging
- **Quote**: "One subtlety that matters: a \"GenAI span\" is not just an LLM call."
- **Our assessment**: This is a critical conceptual expansion. Many practitioners think of "LLM observability" as instrumenting the model call; this source argues the observability surface is the entire agent execution graph. The implication is that conversation ID propagation into downstream systems is not optional — without it, you lose visibility into the parts of the system most likely to fail (per Claim 1). This aligns with distributed tracing best practices but applies them to the new domain of agent systems.

### Claim 4: Auto-instrumentation covers LLM-layer spans, but agent-layer attributes must be hand-authored
- **Evidence**: The article provides specific guidance for OpenAI SDK, Anthropic SDK, and LangChain/LangGraph, each following the same pattern: drop in auto-instrumentation and you get LLM-layer telemetry for free, but you must still set `gen_ai.conversation.id` and `gen_ai.agent.name` yourself in a parent span you control.
- **Confidence**: emerging
- **Quote**: "Auto-instrumentation can't infer your conversation boundaries or your agent identity."
- **Our assessment**: This is a non-obvious rule that is critical for teams adopting agent frameworks. Framework auto-instrumentation can detect LLM calls because they go through known library hooks, but "which conversation does this belong to?" and "which agent am I?" are application-level concepts no framework can infer. The article's universal pattern — "let the framework instrumentation own the LLM-layer spans, and you own the agent-layer and conversation-layer attributes" — is a concise, actionable heuristic.

### Claim 5: Tool calls are where most agentic failures live
- **Evidence**: The article provides a complete tool execution span code example with try/except error propagation, including `error.type` attribute setting and `span.set_status(Status(StatusCode.ERROR, str(e)))`. The article asserts this directly.
- **Confidence**: emerging
- **Quote**: "Tool calls are where most agentic failures live."
- **Our assessment**: Consistent with Claim 1 and Claim 3. Tool execution spans are the highest-value instrumentation target because they involve arbitrary external I/O. The concrete pattern — set `error.type` on exception, propagate error status to the parent span, use the Timeline's "Show Failures Only" filter — is production-grade and directly applicable to any agent observability setup.

### Claim 6: Multi-agent systems require distinct agent names per sub-agent and explicit handoff spans
- **Evidence**: Code example showing orchestrator emitting `invoke_agent billing_agent` span with `gen_ai.agent.name = "orchestrator"`, while the called `billing_agent` emits its own spans with `gen_ai.agent.name = "billing_agent"`. The article explains that missing agent names show spans as "Unknown."
- **Confidence**: emerging
- **Quote**: "Sub-agents use their own distinct names; they don't inherit from the parent."
- **Our assessment**: This is the most opinionated pattern in the article. Not all agent frameworks model sub-agents with distinct identities — some treat them as internal function calls under a single agent name. The article's pattern (caller emits `invoke_agent`, callee uses its own name) creates clean swim-lane separation but requires discipline: every agent must be named, and naming must be consistent across invocations. This is good architecture but may be aspirational for teams with ad-hoc agent graphs.

### Claim 7: Capturing both requested and actual response model names enables debugging silent provider-side model upgrades
- **Evidence**: The article provides concrete attribute names (`gen_ai.request.model` and `gen_ai.response.model`) with a worked example: requesting `gpt-4o` but receiving `gpt-4o-2024-08-06`.
- **Confidence**: anecdotal
- **Quote**: "Capturing both is how you debug behavior changes after a silent provider-side model upgrade."
- **Our assessment**: This is a sharp operational insight. Model providers routinely roll out minor version updates that can change agent behavior in subtle ways. Having both attributes on every LLM span gives a queryable diff. The pattern generalizes beyond OpenAI to any model provider. This is a low-effort, high-value instrumentation practice.

### Claim 8: Prompt and response capture dramatically accelerates root-cause investigation but requires PII handling
- **Evidence**: The article recommends `gen_ai.input.messages` and `gen_ai.output.messages` as span events (not attributes) and offers three mitigation strategies: redact at the application layer, scrub at the OTel Collector, or restrict to non-production environments.
- **Confidence**: settled
- **Quote**: "These make root-cause investigation dramatically faster because you can read what the agent was told and what it said."
- **Our assessment**: Storing prompt/response as span events rather than span attributes is a meaningful architectural decision — events can be stripped by a Collector processor without touching application code. The three-tier mitigation strategy (app layer, Collector, environment-gating) is practical and covers teams at different maturity levels. This should be the guide's recommended pattern for any LLM I/O capture.

### Claim 9: Setting error.type and propagating error status turns failures into first-class navigation primitives
- **Evidence**: The tool call code example shows `error.type` being set and `span.set_status(Status(StatusCode.ERROR))` in the except block. The article describes the Timeline's "Show Failures Only" toggle and conversation-level failure count.
- **Confidence**: emerging
- **Quote**: "This is what turns failures into first-class navigation primitives instead of needles in a haystack."
- **Our assessment**: This is standard OpenTelemetry error semantics applied to a new domain. The article correctly identifies that agent debugging without structured error signals is uniquely painful because of nondeterminism. The "needles in a haystack" framing is apt — without `error.type` on spans, an operator searching for failures across thousands of agent conversations has no queryable surface.

### Claim 10: Span naming follows a strict `<operation> <target>` pattern for the Agent Timeline
- **Evidence**: The article provides a span naming table with eight operation types and their span name patterns: `chat {model}`, `execute_tool {tool_name}`, `invoke_agent {agent_name}`, `embeddings {model}`, `generate_content {model}`, `text_completion {model}`, plus retrieval and create_agent patterns.
- **Confidence**: settled (for Honeycomb's implementation)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The `<operation> <target>` naming convention is simple, grep-able, and machine-parseable. It encodes both the operation type and its target in the span name, making span lists readable without inspecting attributes. This is a good convention for the guide to recommend even for teams not using Honeycomb.

### Claim 11: Evaluation results should be attached as span events to GenAI operation spans
- **Evidence**: The article mentions `gen_ai.evaluation.result` as a span event that closes the feedback loop between cost (tokens), latency (span duration), and quality (eval result).
- **Confidence**: anecdotal
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Most teams do not have automated eval pipelines wired into their observability stack, making this aspirational. The pattern is powerful in principle but the article provides no code example for eval attachment, making this the least substantiated claim.

### Claim 12: The three required attributes must propagate to every span including downstream system spans
- **Evidence**: The article explicitly states that every span "including downstream database queries, third-party API calls, or background jobs that ran because the agent decided to call a tool" must carry the conversation ID. It emphasizes that "without the conversation ID propagating into your downstream system spans, you get the LLM-only view."
- **Confidence**: settled
- **Quote**: "If a span exists because the agent did something, it should carry the conversation ID."
- **Our assessment**: This is the logical consequence of Claim 3. The entire value proposition of the Agent Timeline — seeing the full execution graph including non-LLM spans — depends on conversation ID propagation. This is technically challenging because it requires threading a correlation ID through arbitrary I/O boundaries (HTTP calls, queue messages, database connections). The article acknowledges this implicitly but does not provide a propagation implementation pattern.

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

### Artifact 4: Attribute Quick Reference

From the blog post, synthesized across sections:

**Required attributes (every span):**
- `gen_ai.conversation.id` (string) — unique conversation or session identifier
- `gen_ai.agent.name` (string) — name of the agent emitting the span
- `gen_ai.operation.name` (string) — operation type (chat, execute_tool, invoke_agent, embeddings, generate_content, text_completion)

**Token tracking attributes:**
- `gen_ai.usage.input_tokens`
- `gen_ai.usage.output_tokens`
- `gen_ai.usage.cache_read.input_tokens`
- `gen_ai.usage.cache_creation.input_tokens`

**Model identification attributes:**
- `gen_ai.request.model` — what you asked for
- `gen_ai.response.model` — what you got

**Tool call attributes:**
- `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`

**Error attributes:**
- `error.type`, `error.message`, `error.stacktrace`; span status set to ERROR

**Prompt/response span events:**
- `gen_ai.input.messages` — may contain PII
- `gen_ai.output.messages` — may contain PII

**Evaluation span events:**
- `gen_ai.evaluation.result`

## Cross-References

- **Corroborates**: None directly at time of extraction. The baseline note (`blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`, issue #2) is the merged DeepSeek/Flash production note for this same URL. The Datadog LLM observability note (`docs-datadog-llm-observability.md`) independently validates OTel GenAI semantic conventions as vendor-neutral. The Langfuse glossary (`docs-langfuse-glossary.md`) confirms "Langfuse is built on OpenTelemetry" and its observation taxonomy parallels the span types in this source. The customer-centric monitoring discussion (`discussion-google-sre-prodcast-customer-centric-monitoring.md`) establishes the telemetry/observability/monitoring vocabulary that this source operationalizes with OTel spans.
- **Contradicts**: None identified.
- **Extends**: The conceptual precursor of conversation-ID propagation as "per-request-ID breadcrumb tracing" (Claim 2 in `discussion-google-sre-prodcast-customer-centric-monitoring.md`) is given concrete attribute names and a propagation pattern by this source. The OTel-as-observability-substrate argument from `docs-google-sre-prodcast-03-01.md` is operationalized here with GenAI-specific semantic conventions.
- **Novel**: Entire content domain is novel to the corpus — this is the first source note covering OTel GenAI semantic conventions for agent instrumentation. Key novel patterns: (1) the three-attribute contract, (2) the auto-vs-manual instrumentation boundary rule, (3) the multi-agent handoff span pattern with distinct sub-agent naming, (4) tool call error propagation as a first-class failure debugging mechanism, (5) the span naming convention table.

## Guide Impact

- **Chapter 02 (Observability)**: This source provides the concrete attribute-level contract for tracing AI agents with OpenTelemetry. Recommend adding a new section covering the three required attributes (`gen_ai.conversation.id`, `gen_ai.agent.name`, `gen_ai.operation.name`) as the baseline for any agent observability setup. The span naming convention table and the auto-vs-manual instrumentation boundary rule should be adapted as recommended patterns.

- **Chapter 05 (LLM Ops Reliability)**: The failure-signal chain (Claim 9 — `error.type` + span status → "Show Failures Only" navigation) and tool-call instrumentation pattern (Artifact 2) are directly applicable to production debugging workflows. The model version drift pattern (Claim 7) should be cited as a specific reliability practice: always capture both `gen_ai.request.model` and `gen_ai.response.model` to detect silent provider-side upgrades. The prompt/response capture with PII mitigation (Claim 8) should inform any guidance on LLM I/O logging in production.

## Extraction Notes

- Baseline comparison note: `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (merged via PR #6, DeepSeek/Flash baseline). This eval note was produced by the DeepSeek V4 Flash Free model (via OpenCode Action) for quality comparison against that baseline.
- The source article was read in full via webfetch. All three Python code examples were extracted verbatim from the source. Quotes were verified against the fetched source content.
- No linked documentation pages were followed for this eval extraction (the production baseline note did follow two Honeycomb docs pages — see the baseline note's Extraction Notes for those details).
- This eval note follows the same template and quality bar as production source notes, per EVAL MODE rules.
