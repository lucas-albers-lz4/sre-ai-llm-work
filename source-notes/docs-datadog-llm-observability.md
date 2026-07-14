---
source_url: https://docs.datadoghq.com/llm_observability/
source_type: docs
title: "Datadog Agent Observability (LLM Observability) — Product Documentation"
author: Datadog (vendor documentation)
date_published: unknown (vendor docs, continuously updated; landing page current as of extraction)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#91"
---

# Datadog Agent Observability (LLM Observability)

> A vendor documentation reference that maps the observable dimensions of LLM
> workloads (traces/spans, span kinds, operational metrics, quality evaluations,
> cost, safety) into a concrete product taxonomy — useful as a reference point
> for the guide's observability framework, not as practitioner-validated
> guidance.

## Source Context

- **Type**: docs (vendor product documentation landing page + followed sub-pages)
- **Author credibility**: Datadog, a major commercial observability vendor. The
  content is first-party product documentation describing what the Agent
  Observability product does. It is authoritative about Datadog's own feature
  set but is marketing-adjacent: it asserts capabilities without independent
  practitioner validation, failure data, or comparison against alternatives.
  Treat capability claims as "what the product exposes," not "what works well in
  production."
- **Scope**: Covers the Agent Observability (formerly "LLM Observability") product:
  end-to-end tracing of LLM/agent workloads, the span-kind taxonomy, operational
  dashboards (cost/latency/usage/errors), the Patterns topic-clustering feature,
  managed + custom evaluations, Insights/outlier detection, sensitive-data
  scanning and prompt-injection detection, SDK/auto-instrumentation, and the
  OpenTelemetry GenAI semantic-convention bridge. Does NOT cover: SLAs, pricing
  specifics, quantitative accuracy/benchmark results, or practitioner
  war-stories. The landing page is a feature overview; substantive technical
  detail lives in the Terms, Patterns, Managed Evaluations, and Auto-Instrumentation
  sub-pages, which were followed.
- **Extraction note**: This is a vendor landing page per the Prospector triage
  (novelty: low; thin evidence at the top level). The Miner followed four
  substantive sub-pages (terms, patterns, managed evaluations, auto-instrumentation)
  to reach the implementation-level detail (span-kind taxonomy, clustering
  algorithm, OTel bridge) that is genuinely useful to the guide.

## Extracted Claims

### Claim 1: Agent Observability frames an LLM app request as a single "trace" you can monitor, troubleshoot, and evaluate
- **Evidence**: Landing page overview. Each request is represented as a trace on the Agent Observability page; the product positions itself around monitoring performance, cost, traces, token usage, and errors.
- **Confidence**: emerging (vendor capability claim; the conceptual model — one trace per request — is a settled tracing convention, but the surrounding product framing is vendor-specific)
- **Quote**: "With Agent Observability, you can monitor, troubleshoot, and evaluate your LLM-powered applications, such as chatbots. You can investigate the root cause of issues, monitor operational performance, and evaluate the quality, privacy, and safety of your LLM applications."
- **Our assessment**: The framing matches standard distributed-tracing orthodoxy (one trace per unit of work) applied to LLM apps. Useful as a vocabulary anchor for the guide's observability chapter. No practitioner evidence is offered for the troubleshoot/evaluate efficacy.

### Claim 2: A trace can take three shapes — single LLM inference, predetermined workflow, or dynamic agent
- **Evidence**: Terms page distinguishes LLM Inference Monitoring (single LLM span), LLM Workflow Monitoring (root workflow span + nested spans), and LLM Agent Monitoring (root agent span + nested workflows/LLMs/tools). This is a maturity ladder for tracing complexity.
- **Confidence**: emerging (vendor taxonomy; structurally sound and maps cleanly onto the OTel GenAI operation model — see Cross-References)
- **Quote**: "A trace can represent: - An individual LLM inference, including tokens, error information, and latency - A predetermined LLM workflow, which is a grouping of LLM calls and their contextual operations, such as tool calls or preprocessing steps - A dynamic LLM workflow executed by an LLM agent"
- **Our assessment**: This three-tier model (inference → workflow → agent) is a clean way to scope observability effort by application complexity, and it directly informs what instrumentation is even possible. It is a good conceptual ladder for the guide to adopt. It also explains *why* naive "just trace the LLM call" coverage is insufficient for agents — the workflow/agent tiers require grouping surrounding operations.

### Claim 3: A span is the unit of work; a trace is one or more nested spans with a root span marking start/end
- **Evidence**: Terms overview table and Spans section. A span carries name, timing, error info, inputs/outputs, metadata (e.g., `temperature`, `max_tokens`), metrics (`input_tokens`, `output_tokens`), and tags.
- **Confidence**: settled (standard OpenTelemetry span definition, restated by the vendor)
- **Quote**: "A span is a unit of work representing an operation in your LLM application, and is the building block of a trace."
- **Our assessment**: Restates the canonical span/trace model. The interesting, non-obvious part is which attributes Datadog puts on a span (inputs/outputs as text, model params as metadata, token counts as metrics) — this is what makes LLM spans richer than generic spans and is worth mirroring in the guide's instrumentation contract.

### Claim 4: Spans are categorized by "span kind" into seven types — LLM, Workflow, Agent, Tool, Task, Embedding, Retrieval
- **Evidence**: Terms page "Span kinds" table. Each kind defines the type of work and whether it can be a root span. LLM/Workflow/Agent are valid root spans; Tool/Task/Embedding/Retrieval are not. Examples given: LLM = "A call to a model, such as OpenAI GPT-4"; Tool = "A call to a web search API or calculator"; Retrieval = "A call to a vector database that returns an array of ranked documents."
- **Confidence**: settled (this is the product's concrete, enumerated taxonomy — a factual description of the product, and it aligns with the OTel GenAI operation types)
- **Quote**: "Agent Observability categorizes spans by their span kind, which defines the type of work the span is performing."
- **Our assessment**: This seven-kind taxonomy is the single most extractable artifact from the source. It is directly comparable to the OTel GenAI `gen_ai.operation.name` set (chat, execute_tool, retrieval, embeddings, invoke_agent, invoke_workflow) documented in the Honeycomb note — see Cross-References. The guide's observability chapter should treat this as a vendor-validated instantiation of the operation-type model. The Retrieval/Tool/Workflow kinds are precisely the "contextual operations" the Honeycomb note argues are where agents actually fail (tool calls, retrieval, handoffs).

### Claim 5: Out-of-the-box operational dashboards monitor cost, latency, performance, and usage trends across all LLM applications
- **Evidence**: Landing page "Monitor operational metrics and optimize cost" section; links to an "Operational Insights" integration dashboard.
- **Confidence**: emerging (vendor feature claim; no metrics, no accuracy data)
- **Quote**: "Monitor the cost, latency, performance, and usage trends for all your LLM applications with out-of-the-box dashboards"
- **Our assessment**: Cost/latency/token-usage tracking is table-stakes for any LLM observability tool and is the operational half of the cost/latency/quality triangle the guide's LLM-Ops chapter targets. Useful as confirmation that cost belongs alongside latency and errors as a first-class operational signal, not an afterthought.

### Claim 6: "Patterns" automatically clusters production traffic into a topic hierarchy using embeddings + UMAP + HDBSCAN, without manual tagging
- **Evidence**: Patterns page "How it works" — summarizes each interaction with AI-generated text, computes embeddings via a self-hosted open-source model, forms clusters with UMAP and HDBSCAN, generates topic names with AI, attributes each interaction to a topic, and builds a parent/child hierarchy. Caps at 10,000 records per run (randomly sampled if exceeded).
- **Confidence**: emerging (concrete algorithm described, but it is a vendor feature with no validation of cluster quality or cost)
- **Quote**: "Patterns automatically clusters your LLM application's production traffic into meaningful topics, helping you understand what users are asking, identify coverage gaps, and diagnose failure modes."
- **Our assessment**: This is the most novel, non-vendor-generic idea in the source: unsupervised topic clustering of production LLM traffic as a standing observability primitive. The specific stack (self-hosted open-source embeddings + UMAP + HDBSCAN for clustering) is concrete and reproducible. It maps directly onto guide concerns: "identify coverage gaps" ↔ eval-coverage gaps; "diagnose failure modes" ↔ the Honeycomb claim that failures live in tool calls. The 10,000-record cap and 5–10 minute background runtime are real operational constraints worth noting — this is not real-time.

### Claim 7: Patterns surfaces three summary metrics and a per-topic table with cost, tokens, errors, and latency
- **Evidence**: Patterns page "Read the summary metrics" and "Navigate the topic list" — Total interactions, Identified topics, Classified %; topic table columns include Cost (estimated LLM cost), Tokens, Errors (count + rate), Latency (median), and Online Evals.
- **Confidence**: emerging
- **Quote**: "Each topic shows its interaction volume and share of total traffic. Interactions that don't fit any cluster are collected into an Outliers group."
- **Our assessment**: The per-topic cost/error/latency breakdowns turn topic clustering into an actionable triage surface — "which topic has unexpectedly high error rate or latency relative to volume" (the scatter plot's stated purpose). This closes the loop between the Patterns feature and the operational/eval dimensions. The "Outliers group" for unclustered traffic is a honest hedge worth copying.

### Claim 8: Insights performs outlier/anomaly detection across span name, workflow type, and Patterns topics, analyzed over the past week
- **Evidence**: Landing page "See anomalies highlighted as insights" — outlier detection across Span name, Workflow type, and Patterns input/output topics; analyzed over the past week and surfaced in the user's selected time window. Stated purpose: "proactively detect regressions, performance drifts, or unexpected behavior."
- **Confidence**: emerging
- **Quote**: "Outlier detection is performed across key dimensions: - Span name - Workflow type - Patterns input/output topics"
- **Our assessment**: The choice of dimensions (span name, workflow type, topic) is itself a useful anomaly-detection blueprint for the guide — it tells you *where* to look for LLM-app regressions. The "past week" baseline is a concrete, if arbitrary, window. No detection methodology (z-score, robust stats) is disclosed.

### Claim 9: Managed evaluations ship built-in quality and safety checks (Language Mismatch, Sensitive Data Scanning); custom evals and NeMo integration are also supported
- **Evidence**: Managed Evaluations page lists two supported managed evaluations: Language Mismatch ("Flags responses that are written in a different language than the user's input") and Sensitive Data Scanning ("Flags the presence of sensitive or regulated information in model inputs or outputs"). Terms page adds the option to submit custom evaluations or integrate with NVIDIA NeMo.
- **Confidence**: emerging
- **Quote**: "Managed evaluations are built-in tools to assess your LLM application. Agent Observability associates evaluations with individual spans so you can view the inputs and outputs that led to a specific evaluation."
- **Our assessment**: Associating an evaluation with the specific span (inputs/outputs) that produced it is the key design point — it makes eval failures debuggable rather than just a dashboard number, mirroring the Honeycomb note's "attach eval result as a span event" pattern. The built-in set is small (two evals documented here); the real value is the custom/Nemo path. Treat "managed evaluations" as a starting point, not a complete eval harness.

### Claim 10: The Sensitive Data Scanner is natively integrated so input/output is scanned and redacted
- **Evidence**: Terms page — "Datadog's Sensitive Data Scanner is natively integrated with Agent Observability, so you can ensure any sensitive data in your input and output is scanned and redacted." Landing page also cites "Automatically scan and redact any sensitive data in your AI applications and identify prompt injections."
- **Confidence**: emerging
- **Quote**: "Sensitive Data Scanner is natively integrated with Agent Observability, so you can ensure any sensitive data in your input and output is scanned and redacted."
- **Our assessment**: This is the security-and-trust half of the product and connects to the guide's Security chapter: PII in prompts/completions is a first-class risk (the Honeycomb note flags the same PII tension for prompt/response capture). Datadog's answer is scan-and-redact at the pipeline; the guide should present this as one mitigation tier alongside the Honeycomb note's app-layer / Collector-layer / env-gating tiers.

### Claim 11: Auto-instrumentation traces supported LLM frameworks "without you having to change your code," but custom calls still need manual instrumentation
- **Evidence**: Auto-Instrumentation page — integrations are enabled by default when running with the Agent Observability SDK and "provide out-of-the-box traces and observability, without you having to change your code." Caveat: "Automatic instrumentation works for calls to supported frameworks and libraries. To trace other calls (for example: API calls, database queries, internal functions), see the Agent Observability SDK reference for how to add manual instrumentation."
- **Confidence**: emerging (vendor claim; the auto/manual boundary is a real, well-known instrumentation fact)
- **Quote**: "Agent Observability can automatically trace and annotate calls to supported LLM frameworks and libraries through various LLM integrations. When you run your LLM application with the Agent Observability SDK, these LLM integrations are enabled by default and provide out-of-the-box traces and observability, without you having to change your code."
- **Our assessment**: This is consistent with, and not contradictory to, the Honeycomb note's Claim 4 ("Auto-instrumentation can't infer your conversation boundaries or your agent identity"). Both agree: framework auto-instrumentation covers the LLM/framework call layer; application-level context (conversation id, agent identity, custom spans) still requires manual instrumentation. Datadog's framing is the vendor-neutral version of the same boundary — useful corroboration. Note the supported-framework list is long and concrete (see Concrete Artifacts).

### Claim 12: Frameworks emitting OpenTelemetry GenAI semantic convention v1.37+ compliant spans are supported without the Datadog SDK
- **Evidence**: Auto-Instrumentation page — "Agent Observability also supports any framework that natively emits OpenTelemetry GenAI semantic convention v1.37+-compliant spans, without requiring the Datadog SDK."
- **Confidence**: settled (factual statement about product interoperability; notable because it confirms vendor alignment with the open standard)
- **Quote**: "Agent Observability also supports any framework that natively emits OpenTelemetry GenAI semantic convention v1.37+-compliant spans, without requiring the Datadog SDK."
- **Our assessment**: This is the highest-value cross-cutting fact in the source for the guide. A major vendor publicly commits to ingesting OTel GenAI semantic-convention spans natively — which means the guide can recommend the OTel GenAI operation/attribute model (per the Honeycomb note) as a vendor-neutral standard that Datadog *and* Honeycomb both consume. It weakens any "you must adopt a proprietary schema" argument. This is a point of strong corroboration with the Honeycomb note, not a contradiction.

## Concrete Artifacts

### Artifact 1: Span-kind taxonomy (from Terms and Concepts page)

| Kind | Represents | Valid Root span? | Example |
| --- | --- | --- | --- |
| LLM | A call to an LLM | Yes | A call to a model, such as OpenAI GPT-4 |
| Workflow | Any predetermined sequence of operations including LLM calls and contextual operations | Yes | A service that takes a URL and returns a summary (tool call + text processing + LLM summarization) |
| Agent | A series of decisions/operations made by an autonomous agent (nested workflows, LLMs, tools, task calls) | Yes | A chatbot that answers customer questions |
| Tool | A call to a program/service where arguments are generated by an LLM | No | A call to a web search API or calculator |
| Task | A standalone step that does not involve an external service call | No | A data preprocessing step |
| Embedding | A call to a model/function that returns an embedding (subcategory of Tool) | No | A call to text-embedding-ada-002 |
| Retrieval | A data retrieval operation from an external knowledge base (subcategory of Tool) | No | A vector DB call returning ranked documents |

A span's attributes (from the Spans section): Name; Start time and duration; Error type/message/traceback; Inputs and outputs (LLM prompts and completions); Metadata (LLM params such as `temperature`, `max_tokens`); Metrics such as `input_tokens` and `output_tokens`; Tags.

### Artifact 2: Patterns clustering pipeline (from Patterns "How it works")

When a Pattern runs, it:
1. Pulls LLM interactions from production traffic based on filter + sampling config
2. Summarizes each interaction with AI-generated text
3. Computes text embeddings of these summaries using a self-hosted, open-source model
4. Forms clusters using machine learning (UMAP and HDBSCAN)
5. Reviews each cluster and generates meaningful topics with AI-generated text
6. Attributes each interaction to a single topic
7. Builds a hierarchy using AI by grouping similar topics together

Constraints (verbatim from source): "Patterns processes up to 10,000 records per run; if your filter matches more than that, records are randomly sampled down to the cap." Pipeline runs in the background and "takes 5 to 10 minutes."

### Artifact 3: Supported managed evaluations (from Managed Evaluations page)

- **Language Mismatch** — "Flags responses that are written in a different language than the user's input"
- **Sensitive Data Scanning** — "Flags the presence of sensitive or regulated information in model inputs or outputs"

Terms page also lists evaluation options: managed evaluations, submit custom evaluations, integrate with frameworks like NVIDIA NeMo.

### Artifact 4: Auto-instrumentation supported frameworks (from Automatic Instrumentation page, Python/Node excerpts)

Python SDK (`ddtrace`) supports auto-instrumentation for, among others:
Amazon Bedrock (>=1.31.57), Amazon Bedrock Agents, Anthropic (>=0.28.0), Claude Agent SDK (>=0.0.23), CrewAI, Google ADK, Google GenAI, LangChain (>=0.1.0), LangGraph, LiteLLM, MCP, OpenAI / Azure OpenAI (>=1.0.0), OpenAI Agents, Pydantic AI, Strands Agents, Vertex AI, vLLM.

Node.js (`dd-trace`) supports: Amazon Bedrock, Anthropic, LangChain, MCP, OpenAI/Azure OpenAI, Vercel AI SDK, Vertex AI, Google GenAI.

Captured fields (verbatim): "Datadog's LLM integrations capture latency, errors, input parameters, input and output messages, and token usage (when available) for traced calls."

### Artifact 5: Insights outlier-detection dimensions (from landing page)

Outlier detection is performed across:
- Span name
- Workflow type
- Patterns input/output topics

"These outliers are analyzed over the past week and automatically surfaced in the corresponding time window selected by the user. This enables teams to proactively detect regressions, performance drifts, or unexpected behavior in their LLM applications."

## Cross-References

- **Corroborates**:
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (Honeycomb OTel GenAI note) — multiple alignment points:
    - Datadog's seven span kinds (Claim 4) map onto the Honeycomb note's OTel GenAI `gen_ai.operation.name` set (Artifact 4/7 there): LLM↔`chat`, Workflow↔`invoke_workflow`, Agent↔`invoke_agent`, Tool↔`execute_tool`, Embedding↔`embeddings`, Retrieval↔`retrieval`, Task↔(task/preprocessing, no direct OTel op). Two independently-authored vendor docs converge on the same operation taxonomy — strong signal this is the emerging standard shape.
    - Datadog's auto/manual instrumentation boundary (Claim 11) matches Honeycomb Claim 4 ("Auto-instrumentation can't infer your conversation boundaries or your agent identity"). Both: framework covers LLM-layer, you cover app-layer.
    - Datadog's OTel GenAI v1.37+ native ingestion (Claim 12) directly validates the Honeycomb note's premise that OTel GenAI semantic conventions are the vendor-neutral contract to recommend.
    - Datadog's eval-associated-with-span design (Claim 9) matches Honeycomb Claim 11 (attach eval result as a span event to the GenAI operation span).
- **Contradicts**: None. No contradiction found with existing notes. The Datadog auto-instrumentation "without code changes" claim is narrower than the Honeycomb note's caveat (it only covers supported frameworks; custom spans still need manual instrumentation) — this is a conditioning variable, not a contradiction. No contradiction issue filed.
- **Extends**:
  - Builds on the Honeycomb note by adding a *second, independent vendor* that adopts the same span-kind / OTel-GenAI model, raising it from "one vendor's convention" toward "emerging industry pattern."
  - Adds the Patterns feature (Claim 6/7) — unsupervised topic clustering of production LLM traffic — as a concrete, algorithm-named observability primitive not present in any existing note.
  - Adds the Insights outlier-detection dimension list (Claim 8) as a specific anomaly-detection blueprint.
- **Novel**: To the corpus, this source is the first vendor *product* reference for LLM observability dimensions and the first to document:
  - A concrete clustering stack for production-traffic topic mining (UMAP + HDBSCAN over self-hosted embeddings).
  - A public vendor commitment to native OTel GenAI semantic-convention ingestion.
  - The "inference → workflow → agent" tracing-maturity ladder (Claim 2).

## Guide Impact

Chapters 02, 05, and 06 are currently stubs ("No sourced claims yet"). This source is a strong foundational vendor reference for all three.

- **Chapter 02 (Observability)**: Adopt the span-kind taxonomy (Artifact 1) and the "inference → workflow → agent" tracing ladder (Claim 2/4) as the canonical model for *what* to instrument in an LLM app. Recommend the OTel GenAI operation/attribute model (per the Honeycomb note) as the vendor-neutral schema, now corroborated by Datadog's native v1.37+ ingestion (Claim 12). The auto-vs-manual instrumentation boundary (Claim 11) should be stated as a rule: framework auto-instrumentation covers the LLM/framework call layer; application-level context (conversation id, agent identity, custom spans) is manual.

- **Chapter 05 (LLM Ops Reliability)**: Use the operational signal set — cost, latency, token usage, errors (Claims 5, 7) — as the first-class dashboard dimensions, and present the Patterns feature (Claims 6/7) as a concrete way to find eval-coverage gaps and failure-mode concentrations in production traffic. The Insights dimension list (Claim 8) is a ready-made anomaly-detection blueprint (span name, workflow type, topic). Frame managed evals (Claim 9) as a starting point, with custom/Nemo evals as the real eval harness.

- **Chapter 06 (Security and Trust)**: Present Datadog's Sensitive Data Scanner / prompt-injection detection (Claim 10) as one mitigation tier for PII in prompts/completions, alongside the Honeycomb note's app-layer / Collector-layer / env-gating tiers. The shared risk is identical: capturing LLM I/O for debugging collides with PII exposure.

- **Cross-chapter**: Add a "vendor landscape" note that at least two major vendors (Datadog, Honeycomb) now converge on the OTel GenAI span/operation model — the guide can confidently standardize on it rather than a proprietary schema.

## Extraction Notes

- **Linked pages followed** (per MINER.md §1, "follow up to 5 linked pages"): the landing page is a thin feature overview, so four substantive sub-pages were fetched as Markdown (Datadog publishes a `.md` mirror of each docs page) to reach implementation-level detail:
  1. `llm_observability/terms` — span/trace/evaluation definitions and the seven-kind span taxonomy
  2. `llm_observability/monitoring/patterns` — the clustering algorithm and topic-table model
  3. `llm_observability/evaluations/managed_evaluations` — built-in eval list
  4. `llm_observability/setup/auto_instrumentation` — the auto-instrumentation mechanism, supported framework table, and OTel bridge
- **Quote sourcing**: All `Quote` fields were copied verbatim from the fetched Datadog Markdown mirrors (the canonical docs text), not reconstructed. Where the landing page and a sub-page said the same thing, the more precise sub-page wording was quoted.
- **No contradiction filed**: The only apparent tension — Datadog "without code changes" vs Honeycomb "auto-instrumentation can't infer conversation boundaries" — resolved as a conditioning variable (Datadog's claim is scoped to supported frameworks; custom spans still need manual instrumentation). Not a contradiction per MINER.md §4a.
- **Triage caveats honored**: The Prospector flagged this as a low-novelty vendor landing page with thin top-level evidence. The Miner did not extract bare feature claims as proven practice; instead it extracted the *observable-dimension taxonomy* and *concrete algorithms* (span kinds, UMAP/HDBSCAN clustering, OTel bridge) as reference points, with each claim flagged `emerging` unless it restates a settled standard (span/trace definition, OTel ingestion).
