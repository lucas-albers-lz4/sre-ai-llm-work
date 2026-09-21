---
source_url: https://docs.litellm.ai/docs/anthropic_unified
source_type: docs
title: "/v1/messages (Anthropic messages format unified endpoint) — liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-21)
date_extracted: 2026-09-21
last_checked: 2026-09-21
status: current
confidence_overall: emerging
issue: "#1382"
---

# /v1/messages — Anthropic messages format unified endpoint (liteLLM Docs)

> LiteLLM's `/v1/messages` page documents the **Anthropic-format unified
> endpoint**: one `acreate` call / one proxy route that serves the Anthropic
> messages wire format against *any* LiteLLM-supported provider
> (`openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`,
> `azure_ai`, etc.), with the feature table claiming Cost Tracking, Logging,
> End-user Tracking, Streaming, Fallbacks, Loadbalancing, and Guardrails all
> ✅. The ops-relevant details are (1) the **Guardrails scoping**: "Applies to
> input and output text (non-streaming only)" — a streaming carve-out the
> guide's Ch05/Ch06 guardrail sections do not yet model; (2) the
> **cross-provider fan-out contract**: request/response follow the Anthropic
> messages spec (string↔content-block message equivalence, `0 < temperature <
> 1`, thinking `budget_tokens` min 1024 and `< max_tokens`), and (3) the
> Audited-surface claim that Fallbacks/Loadbalancing work only "between
> supported models". This note has **no claim-level disagreement** with the
> corpus (no document asserts an inclusive temperature range `0 ≤ t ≤ 1` or
> that guardrails run on streaming, so there is nothing to file under
> `CONTRADICTIONS.md`).

## Source Context

- **Type**: docs (single-page LiteLLM proxy/SDK endpoint reference, part of the
  `litellm-docs` site-crawl seed via `anthropic_unified`)
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* LiteLLM exposes (route, feature flags,
  request/response field contract). Vendor documentation of a translation
  layer — the cross-provider guarantees (`x` key accepted, `y` field mirrored
  to `openai/gpt-5.6-terra`) are documented claims, not independently exercised
  here against any downstream API.
- **Scope**: The `/v1/messages` endpoint contract — feature matrix, SDK +
  proxy + curl usage, request format (required + optional fields), response
  format (content blocks, `stop_reason`, `usage` including cache-token
  accounting). The page has no failure reports, no metrics, no rate-limit or
  streaming-quality discussion, and no per-backend behavior matrix beyond the
  generic feature flags.
- **Redundancy**: No other corpus note describes Anthropic-format requests
  fanned out to non-Anthropic providers. `docs-litellm-anthropic-count-tokens`
  (#1381) covers a *pre-flight counting* sibling endpoint; `blog-litellm-
  claude-opus-4-8-day-0` (#1325) only routes Claude→Claude through `messages`;
  `blog-litellm-claude-fable-5-day-0` (#1287) has a thinking-field Fan-Out
  claim but is a single-provider note (see Cross-References).
- **Contradiction scan**: `rg` for "temperature" / "top_p" / "cache_*" across
  `source-notes/` surfaced no corpus claim of an inclusive Anthropic-spec
  temperature range, and `guide/` does not assert `0 ≤ temperature ≤ 1`.
  Per MINER's contradiction rule, a filable contradiction needs two opposing
  *existing* claims; the `0 < temperature < 1` and `summary`-forwarding
  constraints here have no live opposing position in the corpus, so nothing
  is filed. Open `contradiction` issues (#1150, #1307, #1322, #1338, #1352)
  are all unrelated to this surface.

## Claims

### Claim 1: `/v1/messages` is a unified Anthropic-messages-format endpoint across all LiteLLM-supported providers — one SDK call / one proxy route serves `openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`, `azure_ai`, etc.

- **Evidence**: The page opens "Use LiteLLM to call all your LLM APIs in the
  Anthropic `v1/messages` format." The feature table's "Supported Providers"
  row reads "**All LiteLLM supported providers**" then lists
  "`openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`,
  `azure_ai`, etc." Usage shows one `litellm.anthropic.messages.acreate(`
  signature exercised against Anthropic, OpenAI (`openai/gpt-5.6-terra`),
  Gemini (`gemini/gemini-3.8-flash`), Vertex AI (`vertex_ai/gemini-3.8-flash`),
  and Bedrock (`bedrock/us.anthropic.claude-sonnet-5`).
- **Confidence**: settled (documented surface; the endpoint exists and is a
  known LiteLLM feature — this is what the page's title claims and what the
  triage asked to verify).
- **Quote**: "Use LiteLLM to call all your LLM APIs in the Anthropic `v1/messages` format." / "**All LiteLLM supported providers**" / "`openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`, `azure_ai`, etc."
- **Our assessment**: The Anthropic-shaped request is the *canvas* — the
  guarantee a client gets is "Anthropic wire format in", regardless of which
  backend executes it. This is the headline capability and the anchor for the
  three fields below.

### Claim 2: The feature matrix claims Cost Tracking, Logging, End-user Tracking, Streaming, Fallbacks, Loadbalancing, and Guardrails are all ✅ on `all supported models` — with no per-backend granularity in the table

- **Evidence**: The "Feature / Supported / Notes" table lists Cost Tracking ✅
  "Works with all supported models", Logging ✅ "Works across all
  integrations", End-user Tracking ✅, Streaming ✅, Fallbacks ✅ "Works between
  supported models", Loadbalancing ✅ "Works between supported models",
  Guardrails ✅ "Applies to input and output text (non-streaming only)".
- **Confidence**: settled for the documented flags; the *applies-to-every-
  model* reading is a vendor claim (no backend-specific matrix is given).
- **Quote**: "Cost Tracking ✅ Works with all supported models" and "Logging ✅ Works across all integrations" and "Streaming ✅" and "Guardrails ✅ Applies to input and output text (non-streaming only)".
- **Our assessment**: The table is a single switchboard — it does not
  disclose which backends actually honor, e.g., streaming or end-user
  tracking. The only scoping notes are the "between supported models" one and
  the streaming carve-out (Claim 4). Operators should treat the ✅ flags as
  surface support, not per-provider parity.

### Claim 3: The proxy serves `/v1/messages` under the Anthropic SDK contract — `x-api-key` plus `anthropic-version: 2023-06-01`, with the `base_url` pointed at the proxy

- **Evidence**: The Proxy section shows `client = anthropic.Anthropic(base_url="http://0.0.0.0:4000", api_key="sk-<your-litellm-api-key>")` then `client.messages.create(...)` against any configured model_name (`anthropic-claude`, `openai-gpt4`, `gemini-2-flash`, `vertex-gemini`, `bedrock-claude`), and the curl example: `curl -L -X POST 'http://0.0.0.0:4000/v1/messages' -H 'content-type: application/json' -H "x-api-key: $LITELLM_API_KEY" -H 'anthropic-version: 2023-06-01'`.
- **Confidence**: settled (documented wire contract; the SDK contract mirrors
  native Anthropic requests — the auth header is the standard
  `anthropic-version`, see the auth-family split in
  `docs-litellm-anthropic-count-tokens` Claim 5).
- **Quote**: "curl -L -X POST 'http://0.0.0.0:4000/v1/messages'" / "'anthropic-version: 2023-06-01'" / "point anthropic sdk to litellm proxy".
- **Our assessment**: For a client this is a drop-in Anthropic base-URL swap —
  the same pattern `blog-litellm-save-claude-code-costs` documents for Claude
  Code (`ANTHROPIC_BASE_URL`). But the "package" a client gets is only
  Anthropic-shaped; backend identity is hidden behind `model_name`. That
  indirection is where the degradation risk lives (Claims 4, 6, 7).

### Claim 4: Guardrails on `/v1/messages` apply "only" to non-streaming input and output text — streaming requests on this route get no documented guardrail coverage

- **Evidence**: Guardrails row: ✅ with note "Applies to input and output text
  (non-streaming only)". Streaming is advertised only as a separate ✅ row.
  `docs-litellm-generic-guardrail-api` (Claim 2) already documents that the
  guardrail hook intercepts `/v1/messages` among its supported endpoints —
  this page adds the explicit streaming carve-out.
- **Confidence**: emerging (single vendor note spelling out the carve‑out;
  not independently exercised, but unambiguous in wording).
- **Quote**: "Guardrails ✅ Applies to input and output text (non-streaming only)".
- **Our assessment**: Highest-value claim for the guide. Ch06
  (`06-security-and-trust.md`, "Coverage is narrower than interception") lists
  guardrails on `/v1/messages` as tool-inspecting surface; Ch05 models a
  guardrail as an availability dependency. Neither models a *streaming bypass*:
  an agent streaming via `/v1/messages` runs its request path with no
  guardrail. Operators must verify guardrail coverage per endpoint *and per
  stream mode*.

### Claim 5: The request body follows the Anthropic messages spec — `model`, `max_tokens` (must be > 1), and `messages` the only required fields, with string↔content-block message equivalence

- **Evidence**: "Request body will be in the Anthropic messages API format.
  **litellm follows the Anthropic messages specification for this endpoint.**"
  Required: `model` (string), `max_tokens` (integer, "value must be greater
  than 1"), `messages` (array of `{role: user|assistant, content: string | array
  of content blocks}`). Docs show `{"role": "user", "content": "Hello, Claude"}`
  is "equivalent to" `{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}`.
- **Confidence**: settled (explicit spec-attribution sentence + field list).
- **Quote**: "litellm follows the Anthropic messages specification for this endpoint." / "The model may stop before reaching this limit; value must be greater than 1." / "is equivalent to".
- **Our assessment**: The Anthropic-spec framing is the guarantee: consumers
  get the Anthropic field contract (both directions), validated and then
  translated per-backend. The strict `max_tokens > 1` requirement is a routing
  constraint — a `max_tokens: 1` request is invalid at the gateway even if the
  downstream model would accept it.

### Claim 6: Sampling and extended-thinking fields carry range constraints on this route — `0 < temperature < 1`, `0 < top_p < 1`, thinking `budget_tokens` ≥ 1024 and `< max_tokens`

- **Evidence**: Optional-field docs: temperature "Valid range: `0 < temperature < 1`"; top_p "Valid range: `0 < top_p < 1`"; thinking.budget_tokens "Minimum of 1024 tokens (and less than `max_tokens`)"; thinking.type e.g. `"enabled"`; thinking.summary optional with possible values `"auto"`, `"concise"`, `"detailed"`, `"disabled"`.
- **Confidence**: emerging (explicit ranges in vendor docs; the strict-exclusive
  range reading is a server-enforced constraint LiteLLM documents about its
  own route, not about Anthropic's API).
- **Quote**: "Valid range: `0 < temperature < 1`." / "Valid range: `0 < top_p < 1`." / "Minimum of 1024 tokens (and less than `max_tokens`)."
- **Our assessment**: These are gateway-side validation bounds that a client
  must respect *before* Anthropic's own constraints apply. A client that sends
  `temperature: 0` (legal per Anthropic's public spec in some models) or
  `top_p: 1` would be rejected by this route even when the downstream model
  accepts it — a silent-degradation window worth noting but not filable as a
  contradiction because the corpus asserts no inclusive range.

### Claim 7: The `thinking.summary` value is "preserved and forwarded" verbatim to non-Anthropic providers — an Anthropic-shaped parameter carried across the fan-out boundary, with no documented per-backend acceptance matrix

- **Evidence**: Under thinking.summary: "When routing to non-Anthropic
  providers (e.g., `openai/gpt-5.6-terra`), the `summary` value is preserved
  and forwarded to the downstream API."
- **Confidence**: emerging (single vendor sentence; no evidence of whether or
  how `openai/gpt-5.6-terra` consumes a `summary` string).
- **Quote**: "When routing to non-Anthropic providers (e.g., `openai/gpt-5.6-terra`), the `summary` value is preserved and forwarded to the downstream API."
- **Our assessment**: Directly answers the triage's cross-provider question:
  LiteLLM *guarantees forwarding*, not *semantic parity*. A non-Anthropic
  backend that ignores unknown fields silently drops the summary; one that
  errors would fail the request. This is the same translation-layer pattern as
  the `/v1/messages`→Responses `tool_choice` shape bug documented in
  `blog-litellm-auto-router-v2` (Claim 10) — forwarded-shape ≠ honored-shape.

### Claim 8: The response is Anthropic-format — `content` blocks of type `text`, `tool_use`, `thinking`, or `redacted_thinking`; `stop_reason` ∈ `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`; `type: "message"`, `role: "assistant"`

- **Evidence**: Response-format section: "Responses will be in the Anthropic
  messages API format." Content block `type` "Indicates the type of content
  (e.g., `"text"`, `"tool_use"`, `"thinking"`, or `"redacted_thinking"`)."
  `stop_reason` "Possible values include" `end_turn`, `max_tokens`,
  `stop_sequence`, `tool_use`, each with a one-line gloss.
- **Confidence**: settled (spec-attribution sentence + explicit field list).
- **Quote**: "Responses will be in the Anthropic messages API format." / "Indicates the type of content (e.g., `"text"`, `"tool_use"`, `"thinking"`, or `"redacted_thinking"`)."
- **Our assessment**: Downstream consumers get Anthropic-shaped output blocks
  regardless of backend — so tool orchestration, thinking handling, and
  stop-reason branching are written once against this shape. The translation
  risk is inverted: the *provider* sees a converted request, the *client* sees
  Anthropic output. Cross-check with `failure-litellm-encrypted-content-
  affinity`, where streaming path differences surfaced as separate behaviors.

### Claim 9: The response `usage` object exposes cache-token accounting — `cache_creation_input_tokens` and `cache_read_input_tokens` alongside `input_tokens`/`output_tokens`

- **Evidence**: The example response shows `usage: { input_tokens: 2095,
  output_tokens: 503, cache_creation_input_tokens: 2095, cache_read_input_tokens: 0 }`.
  The response-field docs list `cache_creation_input_tokens` ("Number of
  tokens used to create a cache entry") and `cache_read_input_tokens`
  ("Number of tokens read from the cache"), both `integer or null`.
- **Confidence**: settled (documented payload shape present in the page's own
  example).
- **Quote**: "cache_creation_input_tokens" / "cache_read_input_tokens" / "Number of tokens used to create a cache entry." / "Number of tokens read from the cache."
- **Our assessment**: Cache-token spend is visible *on the response object* of
  this route — an observability win for Ch02 (cost/usage attribution) and
  complements `docs-litellm-token-usage-helpers` (which tracks usage fields on
  the general response path) without duplicating its scope. It also interlocks
  with `blog-litellm-save-claude-code-costs` (Claim 3): proxy-side cache
  injection produces cache-*read* tokens that now surface here.

### Claim 10: `messages` content strings and the content-block array form are explicitly equivalent — `{"role": "user", "content": "Hello, Claude"}` ≡ `{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}`

- **Evidence**: Under the `messages.content` definition, the string form "is
  equivalent to" the block-array form, shown side by side. `content` is
  "string or array of content blocks" where blocks are objects with a `type`
  such as `"text"`.
- **Confidence**: settled (explicit equivalence statement in the docs).
- **Quote**: "The text or content blocks (e.g., an array containing objects with a `type` such as `"text"`) that form the message." / "is equivalent to".
- **Our assessment**: A documented normalization guarantee — LiteLLM
  canonicalizes string→block before provider translation, so mixed callers
  (SDK, proxy, curl) hit one contract. A minor but concrete "what the gateway
  promises the caller" fact for the unified-surface story.

## Concrete Artifacts

Feature table (verbatim):

| Feature | Supported | Notes |
|---|---|---|
| Cost Tracking | ✅ | Works with all supported models |
| Logging | ✅ | Works across all integrations |
| End-user Tracking | ✅ | (no note) |
| Streaming | ✅ | (no note) |
| Fallbacks | ✅ | Works between supported models |
| Loadbalancing | ✅ | Works between supported models |
| Guardrails | ✅ | Applies to input and output text (non-streaming only) |
| Supported Providers | **All LiteLLM supported providers** | `openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`, `azure_ai`, etc. |

SDK fan-out example (Anthropic + OpenAI, verbatim shape):

```python
import litellm
# Anthropic
response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    api_key=api_key,
    model="anthropic/claude-sonnet-5",
    max_tokens=100,
)
# OpenAI — same call shape, different model
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
response = await litellm.anthropic.messages.acreate(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="openai/gpt-5.6-terra",
    max_tokens=100,
)
```

Streaming variant: same `acreate` with `stream=True` returns an async
iterator (`async for chunk in response: print(chunk)`), exercised against all
five example providers.

Proxy usage (config → SDK → curl, verbatim):

```yaml
model_list:
    - model_name: anthropic-claude
      litellm_params:
        model: claude-sonnet-5
        api_key: os.environ/ANTHROPIC_API_KEY
```

```python
import anthropic
# point anthropic sdk to litellm proxy
client = anthropic.Anthropic(
    base_url="http://0.0.0.0:4000",
    api_key="sk-<your-litellm-api-key>",
)
response = client.messages.create(
    messages=[{"role": "user", "content": "Hello, can you tell me a short joke?"}],
    model="anthropic-claude",
    max_tokens=100,
)
```

```bash
curl -L -X POST 'http://0.0.0.0:4000/v1/messages' \
-H 'content-type: application/json' \
-H "x-api-key: $LITELLM_API_KEY" \
-H 'anthropic-version: 2023-06-01' \
-d '{
  "model": "anthropic-claude",
  "messages": [{"role": "user", "content": "Hello, can you tell me a short joke?"}],
  "max_tokens": 100
}'
```

Example response (verbatim):

```json
{
  "content": [{"text": "Hi! this is a very short joke", "type": "text"}],
  "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
  "model": "claude-sonnet-5",
  "role": "assistant",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "type": "message",
  "usage": {
    "input_tokens": 2095,
    "output_tokens": 503,
    "cache_creation_input_tokens": 2095,
    "cache_read_input_tokens": 0
  }
}
```

Config indirection (verbatim): `model_name` → `litellm_params.model` mapping
is shown for `anthropic-claude`, `openai-gpt4` (`openai/gpt-5.6-terra`),
`gemini-2-flash` (`gemini/gemini-3.8-flash`), `vertex-gemini`
(`vertex_ai/gemini-3.8-flash`), `bedrock-claude`
(`bedrock/us.anthropic.claude-sonnet-5`).

## Cross-References

Candidates from `miner-related-notes.md` (cite or dismiss each):

- `source-notes/blog-litellm-auto-router-v2.md` — **cited** (Claim 10: the
  `/v1/messages`→Responses API `tool_choice` shape bug is the precedent that
  light "forwarded, not honored" translation loss — reinforce with Claim 7).
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session budget/iteration-controller notes; nothing on `/v1/messages` or
  the Anthropic wire format.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent-spectrum/read-write guardrail taxonomy; no LiteLLM endpoint contract.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **cited**
  (Claim 3: proxy-side `cache_control` injection pairs with Claim 9's
  `cache_read_input_tokens`; Claim 10: `ANTHROPIC_BASE_URL` client-identical
  to the `base_url`/SDK swap in Claim 3 of this note).
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: A2A cost
  tracking ledger; different routing surface.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: Langfuse/MCP
  observability; no Anthropic-shape periphery.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**:
  Helicone logging integration; no endpoint-contract claims.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: FM/LLM
  ops editorial; no endpoint-contract claims.
- `source-notes/blog-litellm-claude-fable-5-day-0.md` — **cited** (Claim 4:
  thinking/`budget_tokens`/temperature/top_p acceptance is *model-dependent*
  at the provider — confirms Claim 7's forwarded-not-honored reading on the
  non-Anthropic side and Claim 6's validation-bound framing).
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  Langfuse guardrail evaluation; LiteLLM guardrail surface already covered by
  `docs-litellm-generic-guardrail-api`.

Wider corpus:

- `source-notes/docs-litellm-generic-guardrail-api.md` — **cited** (Claim 2:
  `/v1/messages` is a guardrail-intercepted endpoint; Claims 8/9: fail-open/
  fail-closed semantics, which the streaming carve-out of Claim 4 bypasses
  entirely; reinforced in guide Ch06).
- `source-notes/blog-litellm-claude-opus-4-8-day-0.md` — **cited** (Claim 2-adjacent
  `/v1/messages` passthrough for mid-task system messages — Anthropic-only
  routing that contrasts with Claim 1's fan-out to *all* supported providers).
- `source-notes/failure-litellm-encrypted-content-affinity.md` — **cited**
  (Lesson 4: streaming-vs-non-streaming treated as separate surfaces — the same
  asymmetry shaped by Claim 4's non-streaming guardrail).
- `source-notes/docs-litellm-streaming-token-usage.md` — **cited** (Claim 1:
  `stream_options.include_usage` opt-in shows streaming usage accounting is
  config-gated elsewhere; complements Claim 9's usage fields on this route).
- `source-notes/docs-litellm-token-usage-helpers.md` — **cited** (Claim 5:
  usage surfaced on the general response path; this note adds the
  cache-accounting fields to that picture for `/v1/messages`).
- `source-notes/docs-litellm-anthropic-count-tokens.md` — **cited** (Claim 5:
  the gateway-normalized vs Anthropic-passthrough auth split — this note's
  Claim 3 (x-api-key + anthropic-version) is the proxy-normalized side of that
  split; sibling Anthropic-shaped surface).
- `source-notes/docs-litellm-gateway-auth-reference.md` — **cited** (drive/post
  the `x-api-key`/`anthropic-version` header family this route requires).
- `source-notes/blog-litellm-gemini-3-5-flash-day-0.md` — **cited** (Claim 8:
  Gemini 3.5 Flash exposed on four endpoints incl. the Anthropic-compatible
  messages endpoint — a real-world instance of Claim 1's cross-provider
  fan-out).

**Contradiction**: none — no corpus claim asserts an inclusive `temperature`
range, streaming guardrail coverage, or summary-backend parity, so there is no
second position to dispute. See the Contradiction-scan note in Source Context.

## Guide Impact

- **Ch05 (LLM Ops Reliability)**: Extend the "A guardrail in the request path
  is an availability dependency" section: add a third axis to guardrail
  modeling — *routed coverage* — the `/v1/messages` guardrail applies to
  input/output text "non-streaming only" (Claim 4), so a stream-mode agent's
  guardrail is absent rather than fail-closed when its path is degraded; a
  canary that only streams never exercises the guardrail at all.
- **Ch05**: Add the fallback/load-balancing scoping fact to the routing/
  failover guidance: Fallbacks / Loadbalancing on this route work "between
  supported models" only (Claim 2), so a fallback chain that mixes a
  non-`/v1/messages`-capable provider is outside the documented envelope.
- **Ch06 (Security and Trust)**: In "Coverage is narrower than interception",
  add the streaming carve-out explicitly: the same `/v1/messages` endpoint that
  is tool-inspecting for non-streaming text has no documented guardrail on
  streaming, and `summary` is forwarded to non-Anthropic backends with no
  documented enforcement/acceptance guarantee (Claims 4, 7).
- **Ch06**: Extend the guardrail hook table (from generic-guardrail-api) with
  a routable-streaming note and a cross-check that tool-inspection claims
  (`/v1/chat/completions`, `/v1/responses`, `/v1/messages`) are documented for
  non-streaming output only.
- **Ch02 (Observability)**: Add `/v1/messages` as a usage/cache-token source:
  `cache_creation_input_tokens` / `cache_read_input_tokens` arrive on the
  response object (Claim 9), so cache-key spend is billable/attributable on
  this route without extra config (contrast with the opt-in
  `stream_options.include_usage` on the OpenAI surface).
- **Guide-global (cross-provider migration)**: Add the unified-endpoint fact
  (Claim 1) to provider-fan-out sections: any Anthropic-shaped client can be
  retargeted to any LiteLLM-supported provider with a `model_name`/`base_url`
  change, but the *guarantee boundary* is shape (Claims 5, 8) rather than
  semantics (Claims 6, 7).