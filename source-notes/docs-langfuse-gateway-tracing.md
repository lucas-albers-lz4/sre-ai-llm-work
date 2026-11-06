---
source_url: https://langfuse.com/docs/gateway/features/tracing
source_type: docs
title: "Tracing with the Langfuse AI Gateway (beta)"
author: "Langfuse (Langfuse GmbH / Finto Technologies Inc.)"
date_published: n.d. (living documentation; gateway in public beta, current as of 2026-11-06)
date_extracted: 2026-11-06
last_checked: 2026-11-06
status: current
confidence_overall: emerging
issue: "#2044"
---

# Tracing with the Langfuse AI Gateway (beta)

> Vendor documentation for an LLM gateway's *tracing contract*: the
> organization-wide `FULL` / `USAGE` / `NONE` ingestion modes (a
> retention-vs-quality tradeoff, not a log level), the `langfuse-*` request
> headers that enrich traces, W3C `traceparent` / `baggage` propagation into
> existing traces, silent-degradation limits on those headers, and the response
> correlation IDs an SRE needs for incident support. First note in the corpus to
> cover Langfuse AI Gateway; all claims are beta vendor surface, not measured
> production outcomes.

## Source Context

- **Type**: docs (first-party product documentation — Langfuse AI Gateway,
  currently in public beta)
- **Author credibility**: Langfuse is a widely used open-source LLM
  observability/evaluation platform. This page is first-party documentation of
  its AI Gateway tracing feature, so claims about what the gateway records,
  accepts, and returns are authoritative for the product's intended surface.
  It is vendor-authored, beta, and carries no independent practitioner
  validation or production measurements. The page itself warns the feature
  "is in public beta and can still change."
- **Scope**: Covers (1) the three organization-level ingestion modes and the
  fields each records, (2) the optional `langfuse-*` request headers and their
  precedence/validation rules, (3) W3C trace-context and baggage propagation into
  an existing trace, (4) the double-instrumentation hazard, (5) inferred coding-
  agent context, and (6) response headers / request IDs for support. Does NOT
  cover: gateway routing, auth, key management, cost accounting internals, or
  self-hosting operations — the page links to sibling pages for those. It does
  not describe gateway overhead, sampling behavior, or measured trace
  completeness.
- **Maturity note**: Everything product-specific here (header names, size caps,
  fallback behavior, ingestion-mode semantics) is beta vendor surface as of
  2026-11-06. Treat it as "what Langfuse's gateway documents today," not as an
  ecosystem-wide invariant or a guaranteed stable API.

## Extracted Claims

### Claim 1: The AI Gateway records every routed model call as a Langfuse generation, but the feature is in public beta and may change
- **Evidence**: The page opens by defining the recording contract and immediately
  flags beta status in a callout. Gateway traces are described as regular
  Langfuse traces that can be filtered, evaluated, and charted like SDK traces.
- **Confidence**: settled (that the product does this) / beta caveat applies to
  stability of the contract
- **Quote**: "The gateway records every model call it routes as a Langfuse generation." / "The Langfuse AI Gateway is in public beta and can still change."
- **Our assessment**: The "every routed call becomes a generation" model is the
  useful architectural point: a gateway is an observation point that does not
  require application code changes. But "every" should be read against Claim 12's
  best-effort caveat — recording is attempted for every call, not guaranteed to
  persist. The beta flag means the header/limit details below should be
  date-stamped, which this note does.

### Claim 2: Ingestion mode is an organization-wide retention decision with three settings — `FULL`, `USAGE` (default), and `NONE` — not a per-request log level
- **Evidence**: The "Ingestion modes" section states gateway managers set the mode
  for the whole organization under Organization settings → AI Gateway → Setup, and
  gives a three-row table of what is recorded and when to use each. `NONE` is
  marked self-hosted only.
- **Confidence**: settled (documented product behavior) / emerging as guide advice
- **Quote**: "There are different ingestion modes, which gateway managers set for the whole organization in **Organization settings → AI Gateway → Setup**:" / "You want to debug, evaluate, or build datasets from real prompts and responses" / "You need cost, usage, and an audit trail, but prompts and responses must not be stored in Langfuse" / "You only want to hand out gateway keys instead of provider keys, without any traces"
- **Our assessment**: This is the highest-value claim for the guide. Framing
  prompt retention as an org-wide mode rather than a log level forces an explicit
  decision: "we need cost + audit but must not store prompts" maps directly to
  `USAGE`. The `NONE` mode isolates the gateway-key-distribution use case from
  observability, which is a real deployment shape. The tradeoff is genuinely
  bidirectional: `USAGE` protects prompt data but forecloses quality debugging.

### Claim 3: `USAGE` mode still records model/cost/perf/audit fields — model, token usage (including cached and reasoning tokens), cost, latency, TTFT, error and warning levels, sessions, trace user, and key/connection metadata — just no input or output
- **Evidence**: The expandable "Full list of fields recorded in `FULL` and `USAGE`
  mode" enumerates the fields. The table says `USAGE` records "The fields listed
  below, without input or output."
- **Confidence**: settled (documented field list)
- **Quote**: "token usage, including cached and reasoning tokens, plus cost, latency, and time to first token" / "level `ERROR` with the provider's status and message for failed calls, and `WARNING` for client cancellations" / "sessions, grouped automatically from each coding agent's own session ID"
- **Our assessment**: This is the operational sweet spot for many teams: enough
  telemetry to run cost, latency, error-rate, and per-key attribution without
  storing message content. Note that `USAGE` still records *metadata* (gateway
  key, key metadata, provider credential metadata under
  `langfuse.gateway.api_key.*` / `langfuse.gateway.connection.*`), so it is not a
  no-data mode — review that metadata before calling it "privacy-safe."

### Claim 4: Only `FULL` ingestion enables the production quality loop — LLM-as-a-Judge on live traffic, annotation queues, and prompt→dataset construction
- **Evidence**: The page states the benefit of `FULL` and gives three concrete
  downstream uses, each linked to its feature page.
- **Confidence**: settled (documented capability) / emerging as a guide rule
- **Quote**: "The benefit of having the `FULL` ingestion mode is that you can observe and improve the quality of the agent's responses."
- **Our assessment**: This makes the privacy/quality tradeoff explicit instead of
  assuming "trace everything." It also means quality evaluation on an existing
  gateway is a *data-retention decision made before the incident*, not a switch
  flipped when quality problems appear. That is a useful planning constraint for
  Ch05/Ch06.

### Claim 5: Traces are enriched by optional `langfuse-*` headers for user, session, environment, tags, metadata, and trace name, with explicit headers taking precedence over inferred values
- **Evidence**: The "Request headers" section supplies a header/format/effect
  table and states these work in both `FULL` and `USAGE` modes. The rules list
  says explicit headers beat inferred values and empty values are ignored.
- **Confidence**: settled (documented header contract)
- **Quote**: "Explicit headers take precedence over values the gateway infers from the agent. Empty values are ignored." / "Splits at the first colon, values stay strings. Percent-encode literal commas (`%2C`)."
- **Our assessment**: This is the correlation-header spec the guide's gateway→
  agent→model discussion currently lacks for the Langfuse case. Two details are
  easy to get wrong in practice: metadata splits only at the *first* colon (values
  can contain colons), and commas inside tags/metadata must be percent-encoded as
  `%2C`. `langfuse-user-id` is only honored for service-account keys — user keys
  always record the key owner.

### Claim 6: Context-header budget is hard and silent — all context headers (including `traceparent` and `baggage`) are ignored when they total more than 8 KiB, each value is capped at 1 KiB, and invalid values are dropped without failing the request
- **Evidence**: Stated directly in a callout in the "Rules" section.
- **Confidence**: settled (documented limit)
- **Quote**: "The gateway ignores **all** context headers of a request, including `traceparent` and `baggage`, when they add up to more than 8 KiB. Each value is also capped at 1 KiB." / "Invalid values are dropped without failing the request."
- **Our assessment**: This is a classic silent-degradation failure mode: the
  request succeeds and returns 200, but trace linkage is gone. An SRE debugging
  "why did this call fork into a new trace?" will not find an error. The guide
  should tell teams to keep baggage/metadata small and to alert on trace-ID
  continuity, not on request success. Note the budget covers `traceparent` and
  `baggage` too, so a noisy upstream propagator can knock out propagation for
  the whole request.

### Claim 7: `langfuse-environment` is silently normalized to `default` when it violates the environment format, while the request still succeeds
- **Evidence**: The rules bullet names the allowed format and states the fallback
  behavior explicitly.
- **Confidence**: settled (documented validation behavior)
- **Quote**: "lowercase letters, numbers, `-` and `_`, at most 40 characters, and not starting with `langfuse`. Any other value is recorded as `default`, and the request still succeeds."
- **Our assessment**: This is the same silent-degradation class as Claim 6, but
  for a value SREs commonly wire from CI/CD (`staging`, `prod`, a branch name).
  Uppercase or an over-long string produces `default` with no error, which can
  quietly merge environments in dashboards. Validate environment values in CI
  rather than trusting the gateway to reject bad ones.

### Claim 8: Static `langfuse-session-id` or `langfuse-trace-name` values are a config footgun — a static session merges every session into one and a static trace name renames every trace
- **Evidence**: The page puts this in bold as the first "Rules" bullet and
  prescribes per-run environment variables.
- **Confidence**: settled (documented anti-pattern)
- **Quote**: "Do not set a static `langfuse-session-id` or `langfuse-trace-name` in a config file." / "A static session ID merges all your sessions into one, and a static trace name renames every trace. Set them per run from an environment variable, and only when you want that effect, for example in scripted or CI runs."
- **Our assessment**: This is a concrete, checkable configuration guardrail: the
  header must be generated per run, never baked into a static config file. The
  failure is invisible at request time but destroys session grouping and naming
  across all traffic, so it is worth a lint/review check in the gateway config.

### Claim 9: The gateway honors W3C `traceparent` — nesting its generation under the calling span and keeping `tracestate` — and reads W3C `baggage` keys that mirror the `langfuse-*` headers, with headers winning on conflict
- **Evidence**: The "Trace context and baggage" section describes `traceparent`
  behavior and provides a baggage-key→header mapping table. It states the header
  wins when both are set.
- **Confidence**: settled (documented propagation contract) / emerging as a guide
  worked example
- **Quote**: "the gateway uses its trace ID and nests the generation under the calling span. `tracestate` is kept." / "When both are set, the `langfuse-*` header wins over the baggage entry. User keys ignore `langfuse_user_id`, like the header."
- **Our assessment**: This is the vendor-specific instance of the generic W3C
  pattern the guide already discusses: a gateway should join an existing trace
  rather than start a parallel one. The baggage key names differ from the header
  names (`langfuse_user_id` vs `langfuse-user-id`, `langfuse_metadata_<key>` vs
  `langfuse-metadata`), so copy them exactly. The precedence rule is
  deterministic and worth documenting so teams do not rely on ambiguous merge
  behavior.

### Claim 10: Do not double-instrument a call through both the gateway and a provider SDK integration — the call is recorded twice
- **Evidence**: A callout after the trace-context section names the Langfuse OpenAI
  integration specifically and explains the duplication.
- **Confidence**: settled (documented anti-pattern) / emerging as a general guide
  rule
- **Quote**: "Don't also trace the same model call with a provider SDK integration, such as the Langfuse OpenAI integration. The call would be recorded twice: once by the integration and once by the gateway."
- **Our assessment**: A real cost/duplicate-metric trap. The gateway observes the
  call from the routing layer; the SDK integration observes it from the client.
  Both create generations, so cost, token counts, and trace volume double. This
  is broader than Langfuse — any gateway-plus-SDK pairing needs an explicit
  "instrument at exactly one layer per call" rule. It belongs alongside the
  guide's existing double-instrumentation warnings.

### Claim 11: Every gateway response carries `langfuse-request-id` (UUIDv7) — including auth failures, gateway errors, and streams — and generation calls also carry `langfuse-trace-id` / `langfuse-observation-id`, even on 502/504 provider failures
- **Evidence**: The response-header table lists each header, its trigger
  condition, and its value. The text below enumerates which endpoints produce a
  generation and which responses still set trace/observation IDs.
- **Confidence**: settled (documented response contract)
- **Quote**: "Every response, including authentication failures, gateway errors, and streams (sent with the first headers)" / "The trace and observation IDs are also set on `502` and `504` responses for provider failures, which still record a generation." / "Model listings, `count_tokens`, and requests rejected before they reach the provider (for example, with a `401`) omit them."
- **Our assessment**: This is the "give support a request ID" runbook pattern: a
  UUIDv7 present even on auth failures means every failed request is traceable
  back to a gateway log, while trace/observation IDs on 502/504 preserve
  provider-failure evidence. Note the asymmetry: a 401 has a request ID but no
  trace ID because no generation was recorded. The guide should tell operators to
  capture `langfuse-request-id` in client error logs, not just on success.

### Claim 12: Recording is best-effort — a returned trace ID may have no stored trace — so trace completeness should not be treated as an audit guarantee or SLO
- **Evidence**: Stated directly as a caveat in the response-headers FAQ.
- **Confidence**: settled (documented limitation)
- **Quote**: "Recording is best-effort, so in rare cases a returned trace ID has no stored trace."
- **Our assessment**: Important scoping claim. A client can receive a trace ID and
  still find nothing in the trace store. For incident response this means the
  trace ID is a lookup hint, not proof of persistence; for compliance it means
  gateway tracing is not a complete audit log. The guide should not equate trace
  coverage with a reliability or audit SLO without independent verification.

### Claim 13: The gateway stores its request ID and the client's request ID under distinct metadata keys, never lets the client `x-request-id` replace the gateway ID, does not forward the client ID upstream, and relays the provider's request ID unchanged
- **Evidence**: The FAQ bullets describe error-body `request_id`, the stored
  metadata key, the `x-request-id` handling, and provider header relay. There is
  also a top-level `request_id` in gateway error bodies.
- **Confidence**: settled (documented behavior)
- **Quote**: "Your own `x-request-id` header never replaces the gateway request ID. It is stored separately as `langfuse.gateway.client.request.id`, and is not forwarded to the provider." / "Gateway error bodies also carry the request ID as a top-level `request_id` field, in the native error format of each namespace." / "The provider's own request ID header (OpenAI `x-request-id`, Anthropic `request-id`) is still relayed unchanged."
- **Our assessment**: Three different request IDs coexist (gateway, client, provider).
  Support workflows must standardize on `langfuse-request-id` /
  `langfuse.gateway.request.id`; a client correlating on its own `x-request-id`
  will not find the gateway-side record because it is stored under a different
  key. This is a concrete runbook detail, not just documentation trivia.

### Claim 14: For supported coding agents the gateway infers session and agent context from the agent's own headers/body, prefixing sessions with the agent name and storing the provider request ID under `langfuse.gateway.upstream.request.id`
- **Evidence**: The FAQ "What context does the gateway infer from coding agents?"
  lists the inferred session naming and the `agent.*` metadata keys, plus the
  provider-request-ID metadata key.
- **Confidence**: settled (documented behavior)
- **Quote**: "The session ID becomes the Langfuse session, prefixed with the agent name (for example `claude-code:<session uuid>`)." / "The provider's request ID is stored in the metadata key `langfuse.gateway.upstream.request.id`. Filter on it to find a single call." / "The original agent IDs are kept in metadata under `agent.*`: `agent.name`, `agent.session_id`, `agent.id` for subagents, `agent.parent_session_id`, and several Codex turn fields."
- **Our assessment**: Useful for coding-agent observability: turn/session grouping
  works out of the box for supported agents, and the `agent.*` metadata preserves
  subagent/parent relationships. The caveat is that this is agent-specific
  inference — "supported coding agents" is load-bearing, and unsupported clients
  fall back to explicit headers (Claim 5).

## Concrete Artifacts

Ingestion-mode table, extracted from the "Ingestion modes" section:

| Mode | Recorded | Use when |
| --- | --- | --- |
| `FULL` | Everything `USAGE` records, plus the full input (system prompt, tool definitions, messages, tool calls and results) and the streamed output (text, reasoning or thinking, and tool calls with parsed arguments) | You want to debug, evaluate, or build datasets from real prompts and responses |
| `USAGE` (default) | The fields listed below, without input or output | You need cost, usage, and an audit trail, but prompts and responses must not be stored in Langfuse |
| `NONE` (self-hosted only) | Nothing. The gateway only routes requests. | You only want to hand out gateway keys instead of provider keys, without any traces |

Request-header example, extracted verbatim from the "Headers" subsection:

```text
langfuse-user-id: jane@example.com
langfuse-environment: ci
langfuse-tags: claude-code,platform-team
langfuse-metadata: repo:langfuse-docs,branch:main
```

W3C baggage key → `langfuse-*` header mapping, extracted from the "Trace context
and baggage" section:

| Baggage key | Same as |
| --- | --- |
| `langfuse_user_id` | `langfuse-user-id` |
| `langfuse_session_id` | `langfuse-session-id` |
| `langfuse_trace_name` | `langfuse-trace-name` |
| `langfuse_environment` | `langfuse-environment` |
| `langfuse_tags` | `langfuse-tags` |
| `langfuse_metadata_<key>` | `langfuse-metadata` |

Response headers, extracted from the FAQ "Which headers does the gateway add to
its responses?":

| Header | When | Value |
| --- | --- | --- |
| `langfuse-request-id` | Every response, including authentication failures, gateway errors, and streams (sent with the first headers) | The gateway request ID, a UUIDv7 |
| `langfuse-trace-id` | Responses to calls that produce a generation | The generation's trace ID, after `traceparent` and agent turn grouping |
| `langfuse-observation-id` | Responses to calls that produce a generation | The generation's observation ID |
| `langfuse-organization-id` | After the gateway key is resolved | Your Langfuse organization ID |
| `langfuse-project-id` | After the gateway key is resolved, when an ingestion project is set | The ingestion project ID |
| `langfuse-provider` | After the gateway called a provider | `openai` or `anthropic` |
| `langfuse-provider-connection-id` | After the gateway called a provider | The ID of the provider credential that served the call |

Inspection command from the page (reads the response headers with `curl -i`):

```sh
curl -si "$LANGFUSE_GATEWAY_HOST/openai/v1/chat/completions" \
  -H "Authorization: Bearer $LANGFUSE_GATEWAY_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model-id>","messages":[{"role":"user","content":"Say hello"}]}' \
  | grep -i '^langfuse-'
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-langfuse-sdk-overview.md`, Claim 5 — Langfuse's data model
    maps an OTel Trace ID to a Langfuse Trace and an OTel Span to a Langfuse
    Observation. That is the same mapping this page relies on when `traceparent`
    makes the gateway "nest the generation under the calling span"; the SDK note
    explains the client side, this note explains the gateway side.
  - `source-notes/docs-langfuse-evaluate-production-traffic.md`, Claim 1 and
    Claim 2 — the rule/sampling machinery for online LLM-as-a-Judge presumes the
    observations exist. Claim 4 here names `FULL` ingestion as the precondition
    for running that judge on production traffic; the two notes are complementary
    halves of the same quality loop.
- **Contradicts**: None. The gateway's W3C propagation requirement is a different
  product surface from LiteLLM's `X-LiteLLM-*` gateway headers, not a conflicting
  claim. No existing source note makes an opposing claim about gateway retention
  modes or trace-header limits.
- **Extends**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md`, Claim 2 — that note
    establishes the general principle that gateway trace grouping is a
    *forwarding obligation, not a gateway guarantee*. This note adds the concrete
    Langfuse instance: the exact `traceparent` / `baggage` / `langfuse-*` header
    contract, precedence rules, and the silent 8 KiB / 1 KiB caps that make the
    obligation fail without an error.
  - `source-notes/docs-langfuse-metrics-overview.md`, Claim 7 — the metrics layer
    aggregates latency, `totalTokens`, `totalCost`, and `timeToFirstToken` by
    dimension; this note supplies the per-generation fields a gateway emits
    (cached/reasoning tokens, TTFT, `ERROR`/`WARNING` level) that feed those
    aggregates.
- **Novel**:
  - First source in the corpus to document an LLM gateway's ingestion-mode
    retention policy (`FULL` / `USAGE` / `NONE`) as an organization-wide data
    governance lever.
  - The Langfuse `langfuse-*` request-header contract, its baggage equivalents,
    header-over-baggage precedence, and the environment-format fallback.
  - The 8 KiB total / 1 KiB per-value context-header budget with silent drops.
  - The static-session/static-trace-name config footgun and the gateway-vs-SDK
    double-instrumentation hazard.
  - Response-side correlation IDs (`langfuse-request-id` on every response
    including auth failures; trace/observation IDs on 502/504) and the
    gateway-vs-client-vs-provider request-ID distinction.

## Guide Impact

- **Chapter 02 (Observability)**: Add a worked gateway example to the existing
  "Correlation survives an agent hop only if the hop re-sends it" section
  (around `guide/02-observability.md:85-114`). The current text covers LiteLLM's
  `X-LiteLLM-Trace-Id` forwarding obligation; this source adds the W3C variant:
  send `traceparent` so the gateway nests its generation under the caller's span,
  keep `tracestate`, and use `baggage` / `langfuse-*` headers for user/session
  metadata. Add the concrete guardrail: context headers over 8 KiB total or 1 KiB
  per value are ignored silently, so a successful request is not evidence that
  trace linkage survived.
- **Chapter 02 (Observability)**: Add the response-side incident runbook detail —
  capture `langfuse-request-id` (UUIDv7, present even on auth failures and
  streams) and `langfuse-trace-id` / `langfuse-observation-id` (present on
  generation calls, including 502/504 provider failures), and standardize on the
  gateway request ID rather than the client's `x-request-id`.
- **Chapter 05 (LLM Ops Reliability)**: Add two gateway-operations rules. (1)
  Instrument each model call at exactly one layer: tracing a call through both a
  gateway and a provider SDK integration records it twice, doubling cost and
  token metrics. (2) Treat trace recording as best-effort — a returned trace ID
  may have no stored trace — so do not make trace completeness an SLO or an audit
  guarantee without independent verification.
- **Chapter 06 (Security and Trust)**: Add ingestion modes as a retention-by-
  default control. `USAGE` is the mode for "cost + audit but prompts must not be
  stored"; `FULL` is required for LLM-as-a-Judge, annotation queues, and dataset
  construction on production traffic; `NONE` (self-hosted) is routing-only. Frame
  the choice as an explicit, org-wide privacy/quality tradeoff decided before
  incidents, and note that `USAGE` still records key/connection metadata even
  without prompt content.
- **Chapter 06 (Security and Trust)**: Add header validation as an input-
  validation surface: invalid `langfuse-environment` values silently become
  `default`, and oversized/invalid context headers are dropped while the request
  still succeeds. Validate these values in CI/config review rather than assuming
  the gateway rejects them.

## Extraction Notes

- The page is short and was read end-to-end, including the expandable field list,
  the rules callout, the baggage table, the response-header table, and the FAQ.
  No paywall. No substantive sub-pages were needed: the header contract and
  ingestion modes are fully specified on this page, and the linked sibling pages
  (data-model, users, sessions, environments, key metadata) are concept pages
  already represented elsewhere in the corpus.
- Related-notes candidate file was read. Dispositions for every listed candidate:
  - `source-notes/docs-langfuse-security-and-guardrails.md` — dismissed as a
    direct cross-reference: it covers a PII anonymize/deanonymize guardrail
    pipeline, not gateway retention modes or trace propagation. Related only at
    the broad "LLM security" level.
  - `source-notes/docs-langfuse-mcp-server.md` — dismissed: docs MCP server, no
    tracing/gateway overlap.
  - `source-notes/docs-langfuse-agent-skill.md` — dismissed: agent skill packaging,
    no tracing/gateway overlap.
  - `source-notes/docs-litellm-evals-api.md` — dismissed: LiteLLM's managed
    Evaluations API surface, not tracing or ingestion-mode retention.
  - `source-notes/docs-langfuse-roadmap.md` — dismissed: roadmap items, no
    gateway tracing contract.
  - `source-notes/docs-langfuse-sdk-overview.md` — cited (Corroborates, Claim 5).
  - `source-notes/docs-litellm-batches-api.md` — dismissed: batch rate-limit
    accounting, unrelated.
  - `source-notes/docs-litellm-bedrock-invoke.md` — dismissed: Bedrock invoke
    passthrough, unrelated.
  - `source-notes/blog-litellm-auto-router-v2.md` — dismissed: routing strategy,
    no tracing contract.
  - `source-notes/docs-litellm-files-endpoints.md` — dismissed: provider files
    endpoints, unrelated.
- Additional cross-references found by searching `source-notes/`:
  `docs-langfuse-evaluate-production-traffic.md` (cited, Corroborates) and
  `docs-langfuse-metrics-overview.md` (cited, Extends). The triage also named
  `docs-langfuse-security-and-guardrails.md`, `blog-cncf-jaeger-ai-agent-tracing-opentelemetry.md`,
  and `docs-datadog-llm-observability.md` as adjacent; they are genuinely
  adjacent (generic W3C/OTel tracing and competing vendor observability) but do
  not make a claim specific enough to cite, so no claim numbers are used for
  them here.
- No contradiction issue was filed: no existing note opposes this page's claims.
  The apparent difference with LiteLLM's `X-LiteLLM-*` headers is a product
  difference (two different gateways), not a contradiction.
- Confidence is `emerging` overall: vendor documentation for a public-beta
  feature, documenting intended behavior rather than measured production
  outcomes. Individual "what the product documents" claims are marked settled;
  guide advice derived from them remains emerging.
