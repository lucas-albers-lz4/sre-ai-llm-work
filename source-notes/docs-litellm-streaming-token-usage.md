---
source_url: https://docs.litellm.ai/stream
source_type: docs
title: "Streaming Responses & Async Completion"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-13)
date_extracted: 2026-09-13
last_checked: 2026-09-13
status: current
confidence_overall: emerging
issue: "#1286"
---

# Streaming Responses & Async Completion (liteLLM Docs)

> The LiteLLM docs' streaming page documents one ops-relevant mechanism: a
> streaming (SSE) completion reports token usage **only** when the client opts
> in with `stream_options={"include_usage": True}`, and that usage arrives as a
> single additional chunk emitted before `data: [DONE]` — an empty-`choices`
> chunk carrying the whole request's token totals, while every preceding chunk
> carries `usage: null`. The operational consequence: a gateway or telemetry
> exporter that records cost/usage from streamed responses without this flag
> silently has nothing to count.

## Source Context

- **Type**: docs (single-page LiteLLM SDK/proxy usage tutorial, part of the
  `litellm-docs` site-crawl scope via spend/accounting)
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Claims about the mechanism LiteLLM documents (the `stream_options` parameter,
  the chunk layout) are authoritative for the LiteLLM surface but are vendor
  documentation of an OpenAI-compatible wire contract — not independently
  verified behavior against any live provider.
- **Scope**: Three short sections — "Streaming Responses" (`stream=True`
  + iterate `chunk['choices'][0]['delta']`), "Async Completion" (`acompletion`
  under `asyncio.run`), and "Streaming Token Usage" (`stream_options={"include_usage": True}`,
  documented for both the SDK and the proxy). Only the third section carries
  ops content; sections 1-2 are boilerplate SDK usage. The page contains nothing
  on routing, rate limits, fallbacks, or production deployment.
- **Extraction note**: Per the Prospector's scoped key question (#1286), this
  note extracts only the streaming usage-accounting contract. The `stream=True`/
  `acompletion` hello-world examples were deliberately skipped as having no ops
  content, per triage instruction.

## Extracted Claims

### Claim 1: A streaming completion does not report token usage unless the client opts in with `stream_options={"include_usage": True}` — the account of a streamed request is usage-blind by default
- **Evidence**: The "Streaming Token Usage" section introduces the opt-in
  parameter and conditions the usage chunk on it: the parameter is presented
  bare (`stream_options={"include_usage": True}`) followed by "If set, an
  additional chunk will be streamed before the data: [DONE] message." Both the
  SDK example and the PROXY curl example pass the flag. The page never shows a
  streamed response carrying usage without the flag.
- **Confidence**: emerging (documented mechanism; the "usage-blind by default"
  reading follows from the "If set" conditional, and matches the OpenAI chat
  completions streaming contract LiteLLM mirrors, but the page does not state
  the negative case explicitly)
- **Quote**: "If set, an additional chunk will be streamed before the data: [DONE] message."
- **Our assessment**: This is the spend/accounting hazard worth recording: an
  operator who records cost from streaming traffic and skips this parameter gets
  a response with no token counts to multiply against the model price map. For
  gateways that estimate cost from response `usage` on `success_callback`, a
  streaming request without `include_usage` yields nothing to log. Default-opt-in
  would be safer, but the flag is opt-in by design — so any deployment that
  serves streamed traffic must decide to pass it at the call site (or rewrite it
  into the request at the gateway). LiteLLM does not document gateway-side
  auto-injection of this flag on this page, so the decision belongs to whoever
  builds the request.

### Claim 2: Wire format — the usage chunk is an additional chunk streamed before `data: [DONE]` carrying the entire request's token totals with an empty `choices` array, while all other chunks carry `usage: null`
- **Evidence**: The "Streaming Token Usage" section spells out the chunk layout:
  the usage field on the extra chunk shows "the token usage statistics for the
  entire request," its `choices` field "will always be an empty array," and "all
  other chunks will also include a usage field, but with a null value."
- **Confidence**: emerging (vendor documentation of the OpenAI-compatible wire
  contract; consistent with OpenAI's documented streaming format, not
  independently exercised by us)
- **Quote**: "The usage field on this chunk shows the token usage statistics for the entire request, and the choices field will always be an empty array. All other chunks will also include a usage field, but with a null value."
- **Our assessment**: Two operational consequences. First, naive per-chunk
  aggregation is a silent-zero path: summing `usage` over chunks yields `null`
  for every chunk except the last, so a consumer that adds chunk usage without
  guarding for `null` records nothing (or zeroes, depending on the reducer).
  Second, the page's own SDK example iterates `for chunk in response:
  print(chunk['choices'][0]['delta'])` — on the final usage chunk `choices` is
  empty, so `chunk['choices'][0]` is an index error. The documented example
  itself would fail on the usage chunk; consumers must branch on `usage is not
  None` (or a non-empty `choices`) rather than printing every chunk blindly. A
  correct consumer unreels the totals from the final chunk once, not from each
  delta.

### Claim 3: LiteLLM asserts the streaming-usage mechanism is "supported across all providers" and "works the same as openai"
- **Evidence**: The "Streaming Token Usage" section's opening two sentences,
  stated without any qualification or test evidence.
- **Confidence**: anecdotal (unsupported vendor uniformity assertion; the page
  offers no provider matrix, no wire captures, no tests)
- **Quote**: "Supported across all providers. Works the same as openai."
- **Our assessment**: Record as a vendor claim, not a verified guarantee.
  Streaming usage reporting is a known site of provider divergence in the
  OpenAI-compatible ecosystem, and "works the same as openai" is exactly the
  kind of uniformity assertion that breaks on a long tail of providers. If the
  guide relies on streaming usage accounting across heterogeneous providers,
  this claim should be verified per provider rather than taken as settled.

## Concrete Artifacts

Both artifacts are extracted verbatim from the "Streaming Token Usage" section's
code blocks (SDK and PROXY tabs). Note the same flag in both call shapes — the
SDK passes it as a Python keyword argument, the proxy request passes it as a
JSON body field — and that the PROXY artifact is the OpenAIOpenAI-compatible
`/v1/chat/completions` shape LiteLLM proxies.

### SDK call shape (verbatim from the "Streaming Token Usage" section's `SDK` tab)

```python
from litellm import completion
import os
os.environ["OPENAI_API_KEY"] = ""

response = completion(model="gpt-3.5-turbo", messages=messages, stream=True, stream_options={"include_usage": True})
for chunk in response:
    print(chunk['choices'][0]['delta'])
```

Source: https://docs.litellm.ai/stream — "Streaming Token Usage / SDK".

### PROXY call shape (verbatim from the "Streaming Token Usage" section's `PROXY` tab)

```
curl https://0.0.0.0:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ],
    "stream": true,
    "stream_options": {"include_usage": true}
  }'
```

Source: https://docs.litellm.ai/stream — "Streaming Token Usage / PROXY".

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/docs-google-sre-eliminating-toil.md` — **Dismissed**: toil
  characterization and toil-reduction measurement; no token-usage or streaming
  content.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Dismissed**:
  agent capability spectrum, write-permission guardrails, pre-on-caller pattern;
  no usage-accounting content.
- `source-notes/blog-litellm-auto-router-v2.md` — **Dismissed**: router/scoring
  config and debuggability rationale; no usage accounting on the wire.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: docs MCP server
  topic; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **Cited** (Extends, see
  below).
- `source-notes/docs-langfuse-security-and-guardrails.md` — **Dismissed**:
  guardrail scanner stacks and latency drivers; no streaming-wire content.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **Dismissed**:
  budget windows, fallback chains, prompt-cache markers, MCP Tool Search — cost
  *control* mechanisms that presuppose usage accounting but do not touch the
  streaming `include_usage` contract.
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **Dismissed**:
  embedding-based semantic-cache backends; unrelated.
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **Dismissed**:
  pipeline data-freshness/correctness SLOs; unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **Dismissed**:
  launch coordination and launch checklists; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-datadog-llm-observability.md` **Claim 3** (a span carries
    token counts as metrics — `input_tokens`, `output_tokens`) and **Claim 5**
    (out-of-the-box dashboards monitor cost/latency/usage trends). The Datadog
    note establishes token counts as a first-class observability metric; this
    source adds the wire-level precondition for streamed traffic: those counts
    exist on the response only when `stream_options={"include_usage": True}` is
    set. Same token-usage-as-telemetry theme; no conflict.
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
    **Claim 11** ("spans that carry token usage and latency give you a
    cost/latency/quality triangle in one query") and its Concrete Artifacts →
    Optional Span Attributes Registry (`gen_ai.usage.input_tokens`,
    `gen_ai.usage.output_tokens`, optional, type int). Token-usage attributes
    are an optional telemetry layer there too; this source explains where those
    numbers must come from for streamed responses.
- **Contradicts**: None. No existing source note makes a claim about streaming
  token usage that this page opposes (verified against the source-note corpus and
  `CONTRADICTIONS.md`, which has no open `C-NNN` entries). The Prospector
  confirmed no `include_usage`/`stream_options` content anywhere in
  `source-notes/` or `guide/` — I independently re-verified this string search
  (also noting the triage comment's claimed `blog-litellm-rust-launch.md` /
  `blog-litellm-swap-openai-code-interpreter.md` hits are not present in those
  files; neither note contains `include_usage` or `stream_options`, and neither
  needs re-verification here — they are not cited). No contradiction issue
  filed.
- **Extends**:
  - `source-notes/docs-litellm-helicone-integration.md` — That note documents
    how LiteLLM ships request telemetry (including usage) to an observability
    vendor via `success_callback` (its Claim 1, integration paths). This source
    adds the precondition that note's wiring presupposes: for a *streamed*
    response there is no usage to ship unless the client passed
    `stream_options={"include_usage": True}`. The two slot together on the
    "usage telemetry through the gateway" theme.
- **Novel**: First source note in the corpus covering the **streaming
  `include_usage` wire contract** — the opt-in requirement, the placement of the
  real token totals (the final pre-`data: [DONE]` chunk), the `usage: null` /
  empty-`choices` chunk semantics, and the silent-zero failure mode for cost
  accounting on streamed traffic. No `docs-litellm-stream*` note existed; the
  40+ LiteLLM corpus entries cover routing, caching, callbacks, sandboxing,
  model day-0 support, and incidents — none address streaming usage accounting.

## Guide Impact

- **Chapter 02 (Observability)**: The chapter teaches that LLM spans carry token
  metrics — `input_tokens`/`output_tokens` [source: docs-datadog-llm-observability,
  Claim 3] [settled]. Add the streaming precondition: for SSE completions those
  token metrics are only populated if the client passes
  `stream_options={"include_usage": True}` and the exporter reads the single
  final usage chunk (empty `choices`, `usage` populated) rather than summing
  per-chunk `usage` (which is `null` on every delta chunk). Recommend that
  instrumentation emit token metrics from the final usage chunk and branch the
  chunk iterator on non-empty `choices` — the page's own SDK example
  (`chunk['choices'][0]['delta']`) index-errors on the usage chunk.

- **Chapter 05 (LLM Ops Reliability)**: The gateway is described as owning
  "routing, fallbacks, logging, spend tracking, auth, billing"
  [source: blog-litellm-agents-are-the-new-llms, Claim 5, Claim 6] [emerging].
  Add an explicit note that **streamed responses are usage-blind by default**:
  an operator who records cost from streaming without
  `stream_options={"include_usage": True}` — or who naively aggregates per-chunk
  `usage` — silently records zeros/nulls against the model cost map. Recommend
  verifying streaming spend after deploy by diffing gateway-recorded token counts
  against provider billing for a sample of streamed requests, and treat the page's
  "supported across all providers" claim as unverified per-provider (Claims 1-3).

## Extraction Notes

- Source read in full via direct HTTP fetch (HTTP 200; no paywall, no truncation;
  the page is three short sections, ~2.3 KB of body text). No sub-pages followed
  — the page has no substantive outbound links.
- Triage bounding honored (`priority:low`): extraction is scoped to the
  streaming usage-accounting contract only, per the Prospector's key question.
  The `stream=True`/`acompletion` hello-world examples were skipped (no ops
  content). Per the triage's judge call, I judged the single mechanism
  sufficient to stand as a low-priority source note — it is the only LiteLLM
  corpus entry for streaming token accounting, and the guide currently has no
  coverage of it.
- All `Quote` fields are verbatim contiguous fragments from the fetched page
  prose ("Streaming Token Usage" section) and were copied character-for-character;
  no splicing across non-adjacent sentences. Code artifacts were copied from the
  rendered code blocks with blank-line reconstruction as rendered.
- Corroboration: the string search `include_usage|stream_options` returns no
  hits in `source-notes/` or `guide/` (re-verified this session; this contradicts
  the triage comment's incidental-match claim for two blog notes — those two
  notes contain neither string and are not cited here).
- `confidence_overall` set to `emerging`: the mechanism and chunk semantics are
  documented vendor wire-contract behavior consistent with OpenAI's streaming
  format, but this is a single thin vendor docs page, the "supported across all
  providers" uniformity claim is unverified, and we did not exercise the wire
  ourselves.
- No contradiction issue filed — the page opposes nothing in the corpus.