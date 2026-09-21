---
source_url: https://docs.litellm.ai/docs/anthropic_count_tokens
source_type: docs
title: "/v1/messages/count_tokens (Anthropic-compatible token counting) — liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-21)
date_extracted: 2026-09-21
last_checked: 2026-09-21
status: current
confidence_overall: emerging
issue: "#1381"
---

# /v1/messages/count_tokens (liteLLM Docs)

> LiteLLM's `/v1/messages/count_tokens` page documents the **provider-side,
> pre-flight** token-counting surface of the gateway, the complement to the
> client-side `token_counter` helpers (#1300): one Anthropic-format endpoint
> that auto-routes to each provider's own counting API (Anthropic Token
> Counting API, OpenAI Responses `/input_tokens`, Vertex AI Partner Models
> Token Counter, Bedrock `CountTokens`, Gemini `countTokens`) and returns
> `{"input_tokens": N}` **before any spend**. The page's ops-relevant details
> are the free-but-logged asymmetry (Cost Tracking ❌ "Token counting only, no
> cost incurred" while Logging ✅, so a pre-flight context-budget gate is
> invisible on spend dashboards), the `vertex_count_tokens_location` override
> required because "count_tokens not available on global location", and the
> two-endpoint auth split between the gateway-normalized path (Bearer key) and
> the Anthropic passthrough (native `x-api-key` + `anthropic-version` +
> `anthropic-beta: token-counting-2024-11-01`).

## Source Context

- **Type**: docs (single-page LiteLLM proxy endpoint reference, part of the
  `litellm-docs` site-crawl scope via spend/accounting)
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* LiteLLM exposes (endpoint path, request and
  response shape, the provider routing table, the `litellm_params` config
  field). Vendor documentation of a proxy capability — the provider-side
  counting numbers are not independently exercised here against any provider.
- **Scope**: The `/v1/messages/count_tokens` endpoint contract — wire contract,
  provider auto-routing table, one `config.yaml` block carrying the
  `vertex_count_tokens_location` constraint, the feature table's
  cost/logging/tracking flags, and the two-endpoint (gateway vs Anthropic
  passthrough) auth comparison. The page has no failure-report, no metrics, and
  nothing on rate limits or production deployment. Per triage, the four
  hello-world curl snippets repeating the `claude-sonnet-5` / "capital of
  France" payload were deliberately skipped. One linked page was followed
  (`/docs/count_tokens`, the "Previous" page and the OpenAI-row reference) and
  adds the SDK method `litellm.acount_tokens()`, the OpenAI-format
  `/v1/responses/input_tokens` endpoint, and the local-tiktoken fallback
  behavior; those items are attributed to the linked page where used.

## Extracted Claims

### Claim 1: The `/v1/messages/count_tokens` endpoint is a pre-flight, Anthropic-format token counting call — `POST` with `{model, messages}` returns `{"input_tokens": N}` and hits a counting API, not the model
- **Evidence**: The Overview labels the endpoint an "Anthropic-compatible token
  counting endpoint" whose purpose is to count "before sending them to the
  model"; the Quick Start curl posts `{model, messages}` in Anthropic format and
  the page shows the expected response `{"input_tokens": 14}`. The Request
  Parameters table lists exactly two required fields (`model`, `messages`),
  and the Response Format section defines `input_tokens` as the count of tokens
  in the input messages. Nothing on the page suggests the calling model is
  invoked — the response carries only a count.
- **Confidence**: settled (documented wire contract; deterministic endpoint
  shape)
- **Quote**: "Anthropic-compatible token counting endpoint. Count tokens for messages before sending them to the model."
- **Our assessment**: This is the structural fact the triage asked for: the
  gateway exposes a *counting* path that is separate from the generation path.
  Because the call returns before any model spend, it is usable as a gate. The
  "expected response" `{"input_tokens": 14}` is the one concrete output shape —
  a single integer field, no `output_tokens`, no cost.

### Claim 2: One LiteLLM endpoint auto-routes to six provider-specific counting implementations, chosen from the model name — Anthropic Token Counting API, OpenAI Responses API `/input_tokens`, Vertex AI Partner Models Token Counter, Bedrock `CountTokens`, Gemini `countTokens`, Vertex AI (Gemini) `countTokens`
- **Evidence**: The "Supported Providers" intro sentence states the routing
  behavior; the routing table assigns a distinct counting method per provider
  row, and the feature table's "Supported Providers" row adds "Auto-routes to
  provider-specific token counting APIs".
- **Confidence**: settled (documented provider matrix on the page)
- **Quote**: "The `/v1/messages/count_tokens` endpoint automatically routes to the appropriate provider-specific token counting API:"
- **Our assessment**: The routing is a normalization claim worth recording as a
  capability surface: a single gateway endpoint hides six distinct upstream
  counting contracts. Two caveats the page does not make but the corpus does
  (see Cross-References): first, the numbers these APIs return are
  provider-tokenized and can differ from LiteLLM's local `token_counter`
  estimate; second, the sibling `/docs/count_tokens` page (followed sub-page)
  shows routing is *not* total — providers without a counting API (and
  missing-API-key cases) fall back to local tiktoken counting on the proxy
  (Claim 7 here).

### Claim 3: Vertex AI (Claude) configurations must set `vertex_count_tokens_location` to a regional location — "count_tokens not available on global location" — so a Vertex `location: global` config that works for inference will fail token counting
- **Evidence**: The "LiteLLM Proxy Configuration" `config.yaml` block declares
  `vertex_count_tokens_location: us-east5` on the `claude-vertex` model entry
  with the inline comment stating why. The value is an optional `litellm_params`
  override distinct from `vertex_location`.
- **Confidence**: settled (documented config contract; the failure mode is the
  Miner's reading of the page's own "not available" annotation)
- **Quote**: "count_tokens not available on global location"
- **Our assessment**: This is the single most concrete ops item on the page — a
  deploy-time constraint that inference smoke tests will not surface. A
  Vertex-backed gateway configured with `vertex_location: global` answers
  completions fine, so the misconfiguration passes pre-deploy validation; the
  first `count_tokens` call in production then errors on the counting API. Any
  context-budget gate that depends on this endpoint inherits the constraint,
  so the guide's runbook should verify the override on Vertex models rather
  than assuming the counting path mirrors the inference path.

### Claim 4: Token counting incurs no cost but is logged and end-user-tracked — "Cost Tracking ❌ (Token counting only, no cost incurred)" with "Logging ✅" and "End-user Tracking ✅" — so count_tokens calls generate log/attribution volume with no spend line
- **Evidence**: The Overview feature table's three rows: Cost Tracking ❌ with
  note "Token counting only, no cost incurred", Logging ✅, End-user Tracking ✅.
- **Confidence**: settled (documented feature table)
- **Quote**: "Token counting only, no cost incurred"
- **Our assessment**: The asymmetry the triage called the free-but-logged
  hazard: a pre-flight context-budget gate built on this endpoint costs nothing,
  so it never appears on spend dashboards, yet every count lands in the request
  log and end-user attribution. An operator computing "spend per user" or
  "spend per key" from gateway cost records will silently under-count all
  requests that were gated and rejected by the count; the only signal is request
  logs. This is the same "cost surface is incomplete without an explicit
  accounting decision" theme the streaming note (#1286) records — but here the
  blind spot is a *free* call class rather than an opt-in flag miss.

### Claim 5: Two endpoints expose token counting with different auth contracts — gateway-normalized `/v1/messages/count_tokens` (Bearer key, all providers) vs Anthropic passthrough `/anthropic/v1/messages/count_tokens` (native `x-api-key` + `anthropic-version` + `anthropic-beta: token-counting-2024-11-01`, Anthropic only)
- **Evidence**: The "Comparison with Anthropic Passthrough" endpoint table
  distinguishes the two paths ("LiteLLM's Anthropic-compatible endpoint" vs
  "Pass-through to Anthropic API"), and the passthrough curl carries the three
  native headers including `anthropic-beta: token-counting-2024-11-01`.
- **Confidence**: settled (documented endpoint table + curl artifact)
- **Quote**: "Direct Anthropic API access with native headers"
- **Our assessment**: The two path shapes enforce different auth and different
  provider scope — the gateway path normalizes to LiteLLM's own Bearer key and
  works across providers; the passthrough requires the Anthropic-native headers
  (including the `token-counting-2024-11-01` beta header) and targets Anthropic
  only. An operator writing a context-budget middleware against the gateway
  should use the normalized path and must not assume the passthrough's native
  headers are interchangeable with it.

### Claim 6: Because counting is pre-flight and free, the endpoint yields a no-spend context-budget gate — a request can be rejected on counted input tokens before any model call, and the gate is documented as serving "cost estimation and context window management"
- **Evidence**: The anchor page's purpose line (Claim 1 quote) plus the followed
  `/docs/count_tokens` sub-page's overview, which pairs counting with "cost
  estimation and context window management." The free-and-logged properties from
  Claims 1 and 4 give the gate its economics.
- **Confidence**: emerging (the documented purpose sentence is verbatim; the
  "no-spend gate" reading is the Miner's synthesis of the free-count + pre-flight
  combination, not a page claim)
- **Quote**: "This gives you accurate token counts before sending requests, helping with cost estimation and context window management."
- **Our assessment**: This is the operational answer to the triage key question:
  LiteLLM's documented purpose for provider-side counting is pre-spend context
  sizing. The page establishes the *what* (free, pre-flight, provider-counted
  `input_tokens`) but says nothing about rate limits, caching, or failure of the
  counting call itself — an operator who gates requests on it should treat the
  counting call as a new dependency with its own failure mode (see Claim 3's
  Vertex constraint for the one documented instance).

### Claim 7: Provider routing is not total — streaming/unsupported providers and missing API keys fall back to local tiktoken counting on the proxy, which runs in a worker thread with bounded concurrency (`TOKEN_COUNTER_MAX_CONCURRENT_COUNTS` default 4) and sampling-based bound on exact chars (`TOKEN_COUNTER_MAX_EXACT_CHARS` default 4,000,000)
- **Evidence**: The followed `/docs/count_tokens` sub-page's "Fallback Behavior"
  section states the automatic fallback for unsupported providers or missing
  keys, and the proxy paragraph documents the worker-thread model and the two
  env-var bounds.
- **Confidence**: emerging (documented vendor mechanism on the linked page; not
  independently exercised)
- **Quote**: "If a provider doesn't support a token counting API, or if the API key is missing, `acount_tokens()` automatically falls back to local tiktoken-based counting:"
- **Our assessment**: This bounds the "provider-authoritative" reading: the
  endpoint is authoritative only where a provider counting API exists and the key
  is valid. Otherwise the number an operator gates on is the same local
  tiktoken estimate the `token_counter` helper (#1300) produces — so a context
  budget can silently flip from provider counts to local counts without the
  gate's config changing. The concurrency bounds matter for the same reason the
  helpers note's map-dependency matters: the fallback path has its own
  latencies and resource limits (4 concurrent counts per worker, 4M-char
  sampling threshold) that a counting-dependent gate inherits.

## Concrete Artifacts

All artifacts verbatim from the anchor page unless marked as the followed
`/docs/count_tokens` sub-page.

### Feature table (from "Overview", verbatim)

| Feature | Supported | Notes |
|---|---|---|
| Cost Tracking | ❌ | Token counting only, no cost incurred |
| Logging | ✅ | Works across all integrations |
| End-user Tracking | ✅ | |

### Provider auto-routing table (from "Supported Providers", verbatim)

| Provider | Token Counting Method |
|---|---|
| Anthropic | Anthropic Token Counting API |
| OpenAI | OpenAI Responses API `/input_tokens` — see Token Counting |
| Vertex AI (Claude) | Vertex AI Partner Models Token Counter |
| Bedrock (Claude) | AWS Bedrock CountTokens API |
| Gemini | Google AI Studio countTokens API |
| Vertex AI (Gemini) | Vertex AI countTokens API |

### Proxy configuration block including the Vertex constraint (from "LiteLLM Proxy Configuration", verbatim)

```yaml
model_list:
  - model_name: claude-sonnet-5
    litellm_params:
      model: anthropic/claude-sonnet-5
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: claude-vertex
    litellm_params:
      model: vertex_ai/claude-sonnet-5
      vertex_project: my-project
      vertex_location: us-east5
      vertex_count_tokens_location: us-east5 # Optional: Override location for token counting (count_tokens not available on global location)
  - model_name: claude-bedrock
    litellm_params:
      model: bedrock/us.anthropic.claude-sonnet-5
      aws_region_name: us-west-2
```

### Expected response (from "Quick Start", verbatim)

```
{
  "input_tokens": 14
}
```

### Pass-through token-counting call with native headers (from "Comparison with Anthropic Passthrough → Pass-through Example", verbatim)

```
curl --request POST \
    --url http://0.0.0.0:4000/anthropic/v1/messages/count_tokens \
    --header "x-api-key: $LITELLM_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "anthropic-beta: token-counting-2024-11-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-sonnet-5",
        "messages": [
            {"role": "user", "content": "Hello, world"}
        ]
    }'
```

### Proxy-side fallback bounds (from followed `/docs/count_tokens` sub-page, "Fallback Behavior" prose, verbatim)

- "On the proxy, local counting runs in a worker thread, so a large payload does not hold up other requests. Each worker process counts at most `TOKEN_COUNTER_MAX_CONCURRENT_COUNTS` payloads at a time (default 4) and queues the rest, which bounds the memory a burst of large counts can take."
- "Strings longer than `TOKEN_COUNTER_MAX_EXACT_CHARS` characters (default 4,000,000, roughly a million tokens) are estimated by tokenizing 16 evenly spaced samples that together total that many characters and scaling the result by the string's length, which keeps the cost of the largest payloads bounded."

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/blog-litellm-auto-router-v2.md` — **Dismissed**: routing-flavor
  collapse and "predictable beats clever" debuggability rationale; no
  token-counting endpoint content.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  session cost/iteration caps keyed on trace ids; a different gateway cost-bound
  surface with no counting-endpoint mechanism in common with this page. Adjacent
  theme (gateway-side pre-spend controls) only.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **Cited** (Extends, see
  below).
- `source-notes/blog-litellm-save-claude-code-costs.md` — **Dismissed**: spend
  *governance* levers (budget windows, fallback chains, prompt-cache markers,
  MCP tool search); no provider-side counting endpoint.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: docs-as-MCP /
  coding-agent integration; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **Dismissed**: how
  telemetry is *shipped* to a vendor (in-path gateway vs `success_callback`).
  This page's "Logging ✅ Works across all integrations" is a gateway-internal
  flag with no documented callback/shipping contract for the counting path, so
  the two do not endorse a mechanism overlap.
- `source-notes/docs-google-sre-eliminating-toil.md` — **Dismissed**: toil
  characterization and reduction measurement; unrelated.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Dismissed**:
  agent capability spectrum, write-permission guardrails, pre-on-caller pattern;
  no token-accounting content.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — **Dismissed**:
  assertion types and model-graded metric boundaries; unrelated.
- `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` — **Dismissed**:
  Bedrock *Invoke* completions prompt-cache invalidation incident; the count
  path uses the Bedrock `CountTokens` API (a distinct surface the incident does
  not touch).

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claim 2** (local
    `token_counter` counts "can diverge from provider-reported usage").
    This page supplies the *provider side* of that divergence: the provider
    counting APIs in Claim 2 here are precisely the authorities whose own
    tokenization a local tiktoken estimate can disagree with. The helpers note
    names the divergence; this page documents the disjoint set of provider
    counters behind it. Same theme, no conflict.
  - `source-notes/docs-datadog-llm-observability.md` **Claim 3** (span metrics
    include `input_tokens`/`output_tokens` — detail in that claim's *Evidence*
    line) and **Claim 5** (operational dashboards monitor cost/latency/usage).
    Both notes treat token counts as a first-class operational quantity; this
    page shows a *pre-flight* source of that quantity that, per Claim 4 here, is
    deliberately absent from the cost side of those dashboards (free) while
    present in the usage/log side.
- **Contradicts**: None. The nearest candidate tension — this page's
  provider-authoritative counting vs the helpers note's local estimation, or the
  three counting surfaces disagreeing on a number — is a measurement-condition
  (counting method differs by surface), not a claim-level opposition: neither
  note asserts the other's number is wrong for its own method, and the helpers
  note's Claim 2 already frames the divergence as expected behavior. Per MINER.md
  §4a no contradiction issue was filed; verified open contradiction issues
  (#1150, #1307, #1322, #1338, #1352) plus CONTRADICTIONS.md (no entries) cover
  none of this surface.
- **Extends**:
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claims 3 & 5** and
    `source-notes/docs-litellm-streaming-token-usage.md` **Claim 1** — the
    triage's central synthesis: LiteLLM offers **three separate token-counting
    surfaces** whose numbers need not agree. The helpers note covers the
    **local-estimate** surface (`token_counter` over tiktoken + `model_cost`
    map); this page covers the **provider-side pre-flight** surface (claims
    `input_tokens` before spend); the streaming note covers the **post-hoc
    response-usage** surface (requires `stream_options={"include_usage": True}`
    on streams). This page is the missing middle slice that makes the
    estimate / pre-flight / post-hoc three-way split complete.
  - `source-notes/docs-litellm-a2a-cost-tracking.md` **Claim 4** — that note
    documents the gateway request log's cost column as the chargeback surface,
    attributed to the calling API key. This page adds a request class that
    appears in those logs with **no cost row** (Claim 4 here), so per-key spend
    derived from the log's cost column silently excludes gated count_tokens
    traffic. Both notes are the same "the log is the spend surface, and it has
    coverage gaps" theme on LiteLLM's gateway.
  - `source-notes/docs-datadog-llm-observability.md` **Claim 5** — build on that
    note's panel that "usage trends" and cost are monitored; this page explains
    which of those two dimensions a free pre-flight count feeds (usage) and
    which it never appears on (cost).
- **Novel**: First corpus coverage of a **provider-side pre-flight**
  token-counting endpoint. `grep count_tokens` returns zero hits in
  `source-notes/` and `guide/` (re-verified this session, matching the triage
  duplicate check). Specifically new: the provider auto-routing table (six
  counting APIs under one endpoint), the `vertex_count_tokens_location`
  constraint ("count_tokens not available on global location"), the
  free-but-logged `Cost Tracking ❌` asymmetry, the gateway-vs-passthrough auth
  split (`anthropic-beta: token-counting-2024-11-01`), and — from the followed
  sub-page — the local-tiktoken fallback with its proxy concurrency bounds.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)** — the chapter's "Streamed traffic is
  usage-blind by default" section (guide/05-llm-ops-reliability.md, tracking
  from ~line 1209) currently teaches **two** metering paths: the streaming
  opt-in response-usage path and the local-estimator helpers path. Add the
  **third, pre-flight path** this page documents: `POST /v1/messages/count_tokens`
  returns provider-counted `input_tokens` before any spend [source:
  docs-litellm-anthropic-count-tokens, Claim 1] [settled], auto-routes per model
  to each provider's counting API [Claim 2] [settled], and falls back to local
  tiktoken on the proxy for unsupported providers / missing keys [Claim 7]
  [emerging]. Extend that section's rule with two consequences: (a) a
  context-budget gate built on the endpoint is **free** — it never shows on
  spend dashboards, so an operator reconciling "spend per user" against gateway
  cost records must read request logs, not cost records, or gated requests
  silently vanish from spend [Claim 4] [settled]; (b) the gate's number quietly
  switches from provider counts to local counts when the provider has no
  counting API or the key is missing [Claim 7] — verify per provider rather than
  treating the count as uniformly provider-authoritative.
- **Chapter 05 (Model enablement / config verification)** — add the
  `vertex_count_tokens_location` constraint to the section's deployment-check
  guidance (alongside the cost-map reload checks): a Vertex-backed gateway model
  configured with `vertex_location: global` (or the location in a region where
  counting is unavailable) answers inference but **fails token counting** until
  the `vertex_count_tokens_location` override is set to a regional location
  [Claim 3] [settled]. An inference-only smoke test will not catch it; the
  pre-flight check is the surface that errors in production.
- **Chapter 02 (Observability)** — where the chapter treats token counts as a
  metric source (citing the Datadog and Honeycomb notes via the sibling
  LiteLLM notes), keep the pre-flight count distinct from response usage: the
  `input_tokens` from this endpoint is a pre-spend, provider-counted estimate
  (free, logged, end-user-tracked, but not cost-tracked), whereas the
  `input_tokens`/`output_tokens` that ride spans/usage dashboards are
  post-hoc response values. The three surfaces (estimate / pre-flight /
  post-hoc) need not agree — record each as its own measurement rather than
  collapsing them into one "token count" number.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/anthropic_count_tokens`, HTTP 200, no paywall).
  One linked sub-page was followed per MINER.md §1: `/docs/count_tokens` (the
  page's "Previous" nav link and the OpenAI-row reference). Claims 6-7 and two
  Concrete Artifacts draw from that sub-page and are explicitly attributed;
  everything else quotes the anchor page. No other outbound links were followed
  (the remaining nav links are endpoint siblings and the passthrough docs page,
  none of which change the counting contract extracted here).
- Triage bounding honored (`priority:medium`; three Prospector passes on this
  issue converged on the same extraction set): the four hello-world curl/httpx
  snippets repeating the `claude-sonnet-5` payload were skipped as boilerplate;
  the extractable content is the feature table, the auto-routing table, the
  `vertex_count_tokens_location` constraint, the endpoint comparison, and the
  response contract — all captured above. The token-usage helpers (#1300) and
  streaming (#1286) notes were **not** re-extracted; cross-linked instead, per
  the triage's "cross-link rather than re-derive" instruction.
- All `Quote` fields are character-for-character contiguous fragments from the
  fetched page prose or code comments/curls (re-verified against the raw fetch
  this session); no splicing across non-adjacent sentences. Table cells are
  quoted as single cells. The two fallback-bound quotes are contiguous
  sentences from the sub-page prose.
- Cross-reference verification (MINER §4b) re-read the cited claims in
  `docs-litellm-token-usage-helpers.md` (Claims 2, 3, 5), `docs-litellm-streaming-token-usage.md`
  (Claim 1), `docs-litellm-a2a-cost-tracking.md` (Claim 4), and
  `docs-datadog-llm-observability.md` (Claim 3 evidence line and Claim 5), and
  confirmed numbered claims match their cited content. No claim numbers were
  invented.
- No contradiction issue filed. The one candidate tension — the three counting
  surfaces producing different numbers — resolves as a conditioning variable
  (counting method per surface), and the helpers note's Claim 2 already frames
  the local-vs-provider divergence as expected, not as error. Verified open
  contradiction issues (#1150, #1307, #1322, #1338, #1352) and CONTRADICTIONS.md
  (no `C-NNN` entries) confirm no duplicate filing exists.
- `confidence_overall` set to `emerging`: the wire contract, feature table, and
  config constraint (Claims 1-5) are settled first-party API surface, but the
  ops value of this note is the synthesis across the three counting surfaces and
  the free-but-logged cost-governance reading (Claims 4, 6-7), none of it
  exercised against a live provider.
- `date_published` is unknown (living Docusaurus page); `date_extracted` and
  `last_checked` are both 2026-09-21 (UTC).