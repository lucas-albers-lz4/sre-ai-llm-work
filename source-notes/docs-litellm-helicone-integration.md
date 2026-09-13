---
source_url: https://docs.litellm.ai/docs/observability/helicone_integration
source_type: docs
title: "Helicone — liteLLM Documentation"
author: "LiteLLM (community-maintained docs page)"
date_published: unknown (living vendor docs; current as of 2026-09-12)
date_extracted: 2026-09-12
last_checked: 2026-09-12
status: current
confidence_overall: emerging
issue: "#1284"
---

# Helicone — liteLLM Documentation

> A community-maintained vendor integration page documenting how to ship LiteLLM
> telemetry to Helicone — two placement modes (in-path provider gateway vs
> out-of-path callback), a manual per-request session-correlation header pair for
> multi-step agent traces, and a policy-header surface that re-implements caching,
> rate limiting, retries, and fallbacks underneath a router that already owns
> those controls.

## Source Context

- **Type**: docs (vendor integration page, LiteLLM × Helicone)
- **Author credibility**: Low-to-medium. The page header states it is
  community-maintained, not first-party-validated:
  > "This is community maintained. Please make an issue if you run into a bug: https://github.com/BerriAI/litellm"
  Config snippets are therefore "the documented wiring," not "the wiring that has
  survived production." The page asserts vendor capability (e.g., Helicone's AI
  Gateway "provides advanced functionality like caching, rate limiting, LLM
  security") with no evidence, metrics, or operator experience.
- **Scope**: Covers two integration methods (Helicone as a provider vs Helicone as
  a `success_callback`), the supported-provider list, the full Helicone
  metadata/header surface (caching, rate limit, retry, fallbacks, session
  tracking, omit-request/response, LLM security/moderations flags), session
  tracking via `Helicone-Session-Id` / `Helicone-Session-Path`, and retry/fallback
  mechanisms. Does NOT cover: failure modes, callback buffering/drop semantics,
  metrics or overhead numbers, SLO guidance, or production experience. The page is
  a thin vendor tutorial (priority:low); the triage bounded extraction to at most
  one short claim plus the layered-authority observation.
- **Extraction note**: Extracted from the **canonical** URL
  (`/docs/observability/helicone_integration`) per the triage reconciliation on
  #1284, not the legacy alias (`/observability/helicone_integration`), which serves
  superseded content (`litellm.api_url`, PaLM, `gpt-3.5-turbo`).

## Extracted Claims

### Claim 1: LiteLLM offers two integration paths for Helicone telemetry — Helicone as a provider (requests route through Helicone's AI Gateway via a `helicone/...` model prefix or an `api_base` rewrite, putting the vendor inside the request path) vs. Helicone as a `success_callback` (out-of-path, provider-agnostic logging)
- **Evidence**: The "Integration Methods" section enumerates exactly two approaches,
  and the page walks through concrete wiring for each: `model="helicone/gpt-5.6-luna"`
  (Provider mode) vs `litellm_settings: success_callback: ["helicone"]` + `HELICONE_API_KEY`
  (Callback mode, "Use just 1 line of code to instantly log your responses across all
  providers with Helicone"). The "Supported LLM Providers" list (OpenAI, Azure,
  Anthropic, Gemini, Groq, Cohere, Replicate, and more) applies to both paths via the
  proxy `config.yaml` examples.
- **Confidence**: settled (factual description of the documented config surface)
- **Quote**: "There are two main approaches to integrate Helicone with LiteLLM:  As a Provider: Use Helicone to log requests for all models supported  Callbacks: Log to Helicone while using any provider"
- **Our assessment**: This is the gateway-placement decision point with a reliability
  consequence: in Provider mode every LLM call traverses Helicone's gateway, so the
  observability vendor becomes a latency and availability dependency of the critical
  path; in Callback mode the logging path is out-of-band and a failure is non-fatal to
  the request. The page documents the wiring but does not itself make that
  reliability argument — that framing is our synthesis for Ch05.

### Claim 2: Helicone session correlation is a manual, per-request application-context layer — the app must set `Helicone-Session-Id` (groups related requests) and `Helicone-Session-Path` (hierarchical `parent/child` traces) on every request; nothing auto-propagates them
- **Evidence**: The "Session Tracking and Tracing" section's headlines and both code
  paths. The LiteLLM SDK path passes both ids in a per-call `metadata={...}` dict; the
  OpenAI/proxy path passes them as `extra_headers` on every request, with each follow-up
  request in the conversation repeating `Helicone-Session-Id` and a new
  `Helicone-Session-Path`. The section defines the pair:
  `Helicone-Session-Id` = "Unique identifier for the session to group related requests",
  `Helicone-Session-Path` = "Hierarchical path to represent parent/child traces
  (e.g., "parent/child")".
- **Confidence**: settled (factual description of the documented wiring)
- **Quote**: "Track multi-step and agentic LLM interactions using session IDs and paths:"
- **Our assessment**: This is a concrete vendor instantiation of the Ch02 rule that
  "auto-instrumentation covers the framework layer; application context is manual" —
  a single per-request trace is not enough for multi-step agent sessions, and the
  correlation ids that group those requests are hand-set by the caller on every
  request. The same boundary appears as `gen_ai.conversation.id` in the Honeycomb
  note (a mandatory attribute on every span) and as the Trace→Session hierarchy in the
  Langfuse glossary — Helicone's variant is HTTP-header-based and proprietary, the
  least portable of the three mechanisms. See Cross-References.

### Claim 3: Helicone headers re-implement caching, rate limiting, retries, and fallbacks at the vendor boundary underneath a LiteLLM router that also exposes these controls, and the page's own examples stack two fallback authorities on one request path with no documented precedence
- **Evidence**: The "Advanced Usage" metadata block advertises `Helicone-Cache-Enabled` +
  `Cache-Control` (cache), `Helicone-RateLimit-Policy` (`"10;w=60;s=user"`), and
  `Helicone-Retry-Enabled` + `helicone-retry-num` + `helicone-retry-factor`
  (retries with backoff). The "Retry and Fallback Mechanisms" proxy `config.yaml`
  sets `Helicone-Fallbacks: '["gpt-5.6-luna", "gpt-5.6-terra"]'` via
  `default_litellm_params.headers`, while the SDK example's model string itself embeds
  a fallback chain — `model="helicone/gpt-5.6-luna/openai,claude-sonnet-5/anthropic"`
  with the comment "Try OpenAI first, then fallback to Anthropic, then continue with
  other models" — i.e., two separate fallback authorities configured simultaneously.
  The page states Helicone's gateway "provides advanced functionality like caching,
  rate limiting, LLM security, and more," but never discusses precedence against the
  router's own caching/rate-limit/retry/fallback controls.
- **Confidence**: emerging (the layered-authority reading is concrete but is our
  synthesis; the page is silent on precedence)
- **Quote**: "Helicone's AI Gateway provides advanced functionality like caching, rate limiting, LLM security, and more."
- **Our assessment**: This is a design hazard worth recording specifically: routing
  policy via vendor headers shadows the gateway's own policy layer, and the two can
  fight (e.g., a router-level retry racing an in-gateway retry, or a router fallback
  beside a `Helicone-Fallbacks` chain). The page gives no precedence rule, so an
  operator reading this docs page can unknowingly configure two authorities for the
  same decision. We would not recommend the in-gateway policy headers unless the
  operator explicitly wants the vendor to own policy; otherwise disable them and let
  the LiteLLM router be the single authority.

### Claim 4: The page is explicitly community-maintained, so its config snippets carry no production-validation warranty
- **Evidence**: The page's tip banner.
- **Confidence**: settled
- **Quote**: "This is community maintained. Please make an issue if you run into a bug: https://github.com/BerriAI/litellm"
- **Our assessment**: This bounds every claim above — all of them describe "the
  documented wiring," not "wiring validated in production." Also relevant: the non-
  `/docs/` alias of this page serves a superseded legacy build (deprecated
  `litellm.api_url`, PaLM-era examples), a crawl/canonicalization hazard documented in
  the #1284 triage reconciliation and worth a maintainer note.

## Concrete Artifacts

### Artifact 1: Callback-mode wiring (from "Quick Start" / LiteLLM Proxy tab, verbatim)
```yaml
model_list:
  - model_name: gpt-5.6-terra
    litellm_params:
      model: gpt-5.6-terra
      api_key: os.environ/OPENAI_API_KEY

# Add Helicone callback
litellm_settings:
  success_callback: ["helicone"]

# Set Helicone API key
environment_variables:
  HELICONE_API_KEY: "your-helicone-key"
```
The page advertises this as "Use just 1 line of code to instantly log your responses
**across all providers** with Helicone".

### Artifact 2: Full Helicone header surface (from "Method 1: Using Helicone as a Provider → Advanced Usage", verbatim)
```python
litellm.metadata = {
    "Helicone-User-Id": "user-abc",  # Specify the user making the request
    "Helicone-Property-App": "web",  # Custom property to add additional information
    "Helicone-Property-Custom": "any-value",  # Add any custom property
    "Helicone-Prompt-Id": "prompt-supreme-court",  # Assign an ID to associate this prompt with future versions
    "Helicone-Cache-Enabled": "true",  # Enable caching of responses
    "Cache-Control": "max-age=3600",  # Set cache limit to 1 hour
    "Helicone-RateLimit-Policy": "10;w=60;s=user",  # Set rate limit policy
    "Helicone-Retry-Enabled": "true",  # Enable retry mechanism
    "helicone-retry-num": "3",  # Set number of retries
    "helicone-retry-factor": "2",  # Set exponential backoff factor
    "Helicone-Model-Override": "gpt-5.6-luna",  # Override the model used for cost calculation
    "Helicone-Session-Id": "session-abc-123",  # Set session ID for tracking
    "Helicone-Session-Path": "parent-trace/child-trace",  # Set session path for hierarchical tracking
    "Helicone-Omit-Response": "false",  # Include response in logging (default behavior)
    "Helicone-Omit-Request": "false",  # Include request in logging (default behavior)
    "Helicone-LLM-Security-Enabled": "true",  # Enable LLM security features
    "Helicone-Moderations-Enabled": "true",  # Enable content moderation
}
```
Telemetry-privacy flags present in the surface: `Helicone-Omit-Request` /
`Helicone-Omit-Response`.

### Artifact 3: Session correlation — the per-request ids the app sets itself (from "Session Tracking and Tracing" / LiteLLM Proxy tab, verbatim)
```python
import openai

client = openai.OpenAI(
    api_key="anything",
    base_url="http://localhost:4000"
)

# First request in session
response1 = client.chat.completions.create(
    model="gpt-5.6-terra",
    messages=[{"role": "user", "content": "Hello"}],
    extra_headers={
        "Helicone-Session-Id": "session-abc-123",
        "Helicone-Session-Path": "conversation/greeting"
    }
)

# Follow-up request in same session
response2 = client.chat.completions.create(
    model="gpt-5.6-terra",
    messages=[{"role": "user", "content": "Tell me more"}],
    extra_headers={
        "Helicone-Session-Id": "session-abc-123",
        "Helicone-Session-Path": "conversation/follow-up"
    }
)
```
Section definitions (verbatim): "`Helicone-Session-Id`: Unique identifier for the
session to group related requests" and "`Helicone-Session-Path`: Hierarchical path to
represent parent/child traces (e.g., "parent/child")".

### Artifact 4: Two stacked fallback authorities in one request path (from "Retry and Fallback Mechanisms" / LiteLLM Proxy tab, verbatim)
```yaml
model_list:
  - model_name: gpt-5.6-terra
    litellm_params:
      model: gpt-5.6-terra
      api_key: os.environ/OPENAI_API_KEY
      api_base: "https://oai.hconeai.com/v1"

default_litellm_params:
  headers:
    Helicone-Auth: "Bearer ${HELICONE_API_KEY}"
    Helicone-Retry-Enabled: "true"
    helicone-retry-num: "3"
    helicone-retry-factor: "2"
    Helicone-Fallbacks: '["gpt-5.6-luna", "gpt-5.6-terra"]'

environment_variables:
  HELICONE_API_KEY: "your-helicone-key"
  OPENAI_API_KEY: "your-openai-key"
```
And the SDK-side example whose model string carries its own fallback chain (verbatim):
```python
response = litellm.completion(
    model="helicone/gpt-5.6-luna/openai,claude-sonnet-5/anthropic", # Try OpenAI first, then fallback to Anthropic, then continue with other models
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed):

- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**: covers the
  agent capability spectrum, guardrail defaults, and the pre-on-caller pattern; no
  telemetry-provider placement or session-correlation content.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: router/scoring config
  and debuggability rationale; no observability-integration overlap.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**: guardrail
  architecture, latency drivers, scanner stacks. Only token-level overlap (this page
  names `Helicone-LLM-Security-Enabled`/`Helicone-Moderations-Enabled` headers but has
  no security-design content).
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: MCP server topic,
  unrelated.
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **dismissed**: pipeline
  data-freshness/correctness SLOs, unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  identification/automation, unrelated.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — **dismissed**: assertion
  types / model-graded metric boundaries, unrelated.
- `source-notes/docs-datadog-llm-observability.md` — **cited** (Corroborates, Claim 2
  below).
- `source-notes/blog-litellm-save-claude-code-costs.md` — **dismissed**: budgets and
  prompt-caching cost controls; different caching mechanism (usage-tracked budget
  windows and `cache_control` markers vs Helicone `Cache-Control` headers).
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **dismissed**: embedding-based
  semantic cache backends; unrelated to header-level response caching.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-datadog-llm-observability.md` **Claim 11** (auto-instrumentation
    covers supported LLM frameworks, "custom calls still need manual instrumentation").
    Helicone's `Helicone-Session-Id`/`Helicone-Session-Path` pair (this note Claim 2)
    is a concrete instance of that boundary: the vendor logs per-request traces, but
    the application context that groups them is set by hand on every request.
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` **Claim 2**
    (`gen_ai.conversation.id` is a mandatory grouping key on every agent span) and
    **Claim 4** ("Auto-instrumentation can't infer your conversation boundaries or your
    agent identity"). Helicone solves the same problem with a proprietary HTTP header
    pair instead of the OTel GenAI attribute — same manual-boundary rule, different and
    less portable mechanism.
  - `source-notes/docs-langfuse-glossary.md` **Claim 1** (Traces are grouped into
    Sessions — a three-level telemetry hierarchy). `Helicone-Session-Id` is the
    vendor-specific expression of the same "session groups requests" concept.
  - `source-notes/docs-langfuse-metrics-overview.md` **Claim 7** (`sessionId` is a
    first-class grouping dimension in the Metrics API v2 observations view). Session is
    a cross-vendor grouping axis in LLM observability products.
- **Contrasts** (mechanism difference, not a contradiction):
  - `source-notes/docs-langfuse-sdk-overview.md` **Claim 10** (`propagate_attributes()`
    auto-distributes `session_id` from a parent observation to all child observations).
    Langfuse propagates the session id through the SDK once on the parent; Helicone
    requires the caller to repeat the ids on every request. Both still need the initial
    manual id — a difference in propagation ergonomics only. No contradiction issue
    filed.
- **Extends**:
  - Builds on the Honeycomb/OTel conversation-id pattern (Honeycomb note Claims 2 and 4)
    with a second, vendor-specific, HTTP-header implementation of the same idea, and
    records the in-path vs out-of-path telemetry placement decision (this note Claim 1),
    which no existing note covers.
- **Novel** (first appearances in the corpus):
  - The gateway-placement decision for third-party LLM telemetry — in-path provider
    gateway (vendor becomes a latency/availability dependency) vs out-of-path callback
    (provider-agnostic, failure non-fatal to the request). (Claim 1)
  - The stacked-authority hazard: vendor headers re-implementing caching, rate
    limiting, retries, and fallbacks underneath a router that already exposes those
    controls, with no documented precedence and, in the source's own example, two
    fallback chains configured on the same request path. (Claim 3)

## Guide Impact

- **Chapter 02 (Observability)**: Add the session-correlation claim (Claim 2) as a
  concrete instance of the "application context is manual" rule already in the chapter
  (citing the Datadog and Honeycomb notes): for multi-step agent sessions, group
  related requests with an explicit session/correlation key per request. Name the three
  mechanisms in the corpus — OTel GenAI `gen_ai.conversation.id` (Honeycomb note,
  portable), Langfuse `sessionId` (SDK-propagated), and Helicone's proprietary
  `Helicone-Session-Id`/`Helicone-Session-Path` headers (manual per-request) — and
  recommend the portable OTel convention over vendor header pairs.
- **Chapter 05 (LLM Ops Reliability)**: Add the stacked-authority hazard (Claim 3) to
  the fallback/routing guidance: when a vendor gateway sits in the request path and its
  headers also configure caching/retry/fallbacks, verify precedence against the
  router's own policy layer and avoid configuring two authorities for the same decision.
  Also add the telemetry-placement tradeoff (Claim 1): prefer out-of-path
  callback-style logging unless the in-path vendor gateway functions are explicitly
  wanted, since in-path placement makes the observability vendor a request-path
  dependency.

## Extraction Notes

- **Source**: the **canonical** `https://docs.litellm.ai/docs/observability/helicone_integration`
  URL was fetched (HTML + raw prose) per the triage reconciliation on #1284. The
  submitted `/observability/...` alias serves a legacy build (deprecated `litellm.api_url`,
  PaLM/`gpt-3.5-turbo` era) and was deliberately **not** extracted; nothing in this note
  quotes or relies on it.
- **Triage bounding honored**: `priority:low` — the note records the two extractable
  patterns (session correlation; layered authority) that the triage reconciliation
  named, plus the placement framing and the community-maintained caveat. It does not
  over-read the page into failure-mode, buffering, or SLO claims that are absent.
- **Quote sourcing**: All `Quote` fields are verbatim from the rendered page prose
  (verified against stripped HTML text of the fetched page). Code-block artifacts were
  reconstructed from the HTML `token-line`/`<br>` structure and cross-checked against
  the Docusaurus-rendered Markdown; attribute-to-comment alignment is preserved.
- **No contradiction found**: no existing source note claims anything the Helicone page
  opposes. The Langfuse-SDK auto-propagation contrast (Claim 10 there) is a mechanism
  difference, not a disagreement. No contradiction issue filed.
- **Pending sibling note**: issue #1274 (LiteLLM callbacks page, `mining-queued`)
  already documents the `success_callback: ["helicone"]` quick-start. This note does not
  re-derive that wiring beyond the config artifact needed for the placement claim, and
  defers to #1274 for the general callback API surface.
- **Maintainer note (crawl canonicalization)**: `registry/site-crawl-state.json` tracks
  both the legacy (`/observability/...`) and canonical (`/docs/observability/...`) paths
  as separate URLs for seed `litellm-docs`; the legacy path serves superseded content.
  Worth normalizing crawl keys to `/docs/` (same hazard noted for the sibling
  `supabase_integration` page, #1285).