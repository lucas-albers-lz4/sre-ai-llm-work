---
source_url: https://docs.litellm.ai/docs/anthropic_unified/messages_to_responses_mapping
source_type: docs
title: "v1/messages → /responses Parameter Mapping — liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-22)
date_extracted: 2026-09-22
last_checked: 2026-09-22
status: current
confidence_overall: emerging
issue: "#1390"
---

# v1/messages → /responses Parameter Mapping (liteLLM Docs)

> LiteLLM's bidirectional translation spec for what happens when a client sends
> a `/v1/messages` request targeting an **OpenAI or Azure** model: the gateway
> silently re-routes it through the OpenAI **Responses API**, translating every
> parameter in both directions in
> `litellm/llms/anthropic/experimental_pass_through/responses_adapters/transformation.py`.
> The ops-relevant content is a **gateway translation hazard catalogue**: silent
> drops (`stop_sequences`, `top_k` — ❌ Not mapped), an identity-derived
> `prompt_cache_key` truncated to OpenAI's 64-char limit whose cache affinity is
> topology-dependent (proxy-in-front-of-proxy deployments never get it), a lossy
> bucket-quantization of `thinking.budget_tokens` into `reasoning.effort`
> (`>=10000`→`high`, `>=5000`→`medium`, `>=2000`→`low`, `<2000`→`minimal`, with
> `summary` forced to `"detailed"`), the structural hoist of `tool_result` /
> `tool_use` blocks to top-level Responses input items, and a lossy response
> direction (`model` falls back to `"unknown-model"`, `stop_sequence` is always
> `null`). Not marketing — the page's own tables and the named implementation
> file are the evidence.

## Source Context

- **Type**: docs (single-page LiteLLM proxy endpoint reference — a
  bidirectional request/response transformation spec, the detail page behind
  the `/v1/messages` unified-endpoint overview at
  `docs/anthropic_unified`[#1382]).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented translation surface* — the page names the
  implementing file
  (`litellm/llms/anthropic/experimental_pass_through/responses_adapters/transformation.py`)
  and gives complete mapping tables in both directions. This is vendor
  documentation of a translation layer: the mappings describe what LiteLLM is
  *documented to do*, not independently exercised behavior against a live
  OpenAI/Azure endpoint. The page carries no metrics, no failure reports, and
  no tests.
- **Scope**: The full `/v1/messages`→Responses translation: top-level parameter
  mapping (request direction), per-message-block expansion into input items,
  `tools` / `tool_choice` / `thinking` / `context_management` transforms, and
  the response direction (Responses API → Anthropic `AnthropicMessagesResponse`).
  Does NOT cover: the native Anthropic passthrough, other providers' fan-out
  (that is the overview page #1382), the chat-completions path in any detail
  beyond the two-difference note, routing/fallbacks, or deployment. The page is
  undated; per Prospector triage it is current (fetched 2026-09-20, HTTP 200;
  the `compact_20260112` compaction type it documents is post-Dec-2025).
- **Redundancy**: The parent overview note `docs-litellm-anthropic-unified.md`
  (#1382) covers the unified endpoint's *feature matrix and field contract*;
  this page supplies the *translation tables the overview only gestures at*.
  Per the Prospector's explicit instruction, the overview material is
  cross-linked, not restated. The Prospector's triage key question — "which
  request parameters are silently dropped and how does the derived
  `prompt_cache_key` behave across providers and proxy hops" — is answered
  claim-by-claim below.

## Extracted Claims

### Claim 1: On the `/v1/messages` → OpenAI/Azure path, `stop_sequences` and `top_k` are silently dropped — a caller setting them gets a 200 with no error and no telemetry that the constraint was ignored, while `speed` is only used for Anthropic beta headers on the native path
- **Evidence**: The "Top-level parameters" table marks both `stop_sequences`
  and `top_k` as "❌ Not mapped" with the note "Dropped silently", and `speed`
  as "❌ Not mapped" with "Only used to set Anthropic beta headers on the native
  path". The page's intro establishes that this table is exactly what happens
  when "you send a request to `/v1/messages` targeting an OpenAI or Azure model".
- **Confidence**: settled (a documented table row is the explicit contract;
  the "no error surface" reading is the page's own "Dropped silently" wording)
- **Quote**: "`stop_sequences`" / "❌ Not mapped" / "Dropped silently" / "Only used to set Anthropic beta headers on the native path"
- **Our assessment**: This is the sharpest reliability claim on the page and
  directly extends the guide's Ch05 rule
  ("audit existing request parameters against the model's supported set before
  routing production traffic", guide/05-llm-ops-reliability.md ~L338-341). The
  distinct mechanism matters: the model-side rejections the corpus already
  documents (`blog-litellm-claude-fable-5-day-0` Claim 4 — `temperature`,
  `top_p`, fixed budgets → 400) are **loud**; these drops are **silent**. An
  operator setting `stop_sequences` for a safety or cost reason on a route that
  lands on OpenAI/Azure has the constraint not applied with zero signal. A
  caller cannot tell from the 200 that behavior changed — the only detection is
  post-routing verification of the outbound request.

### Claim 2: `prompt_cache_key` is derived from `metadata.user_id`, truncated to OpenAI's 64-character key limit, so one user's requests keep hitting the same prompt cache; it is not set when `user_id` is empty or null, and an explicit body `prompt_cache_key` wins over the derived one
- **Evidence**: The top-level table's `metadata.user_id` → `prompt_cache_key`
  row, with the full note text.
- **Confidence**: settled (explicit documented derivation rule)
- **Quote**: "Same value, truncated to 64 characters (OpenAI's key limit), so one user's requests keep hitting the same prompt cache. Not set when `user_id` is empty or null. A `prompt_cache_key` sent in the request body wins over the derived one"
- **Our assessment**: A cache-affinity mechanism distinct from the 
  routing-affinity mechanisms in the corpus: this is *identity-derived cache-key
  pinning* (per-user cache affinity), not deployment/session pinning. The
  truncation asymmetry is the operative detail: two users whose IDs share a
  64-char prefix collide on the same cache key (cross-tenant cache sharing), and
  silent truncation of a longer ID is invisible to the caller. A caller that
  supplies a body-level `prompt_cache_key` opts out of the derivation cleanly —
  the only documented way to override it. The Ch06 open question (per the
  Prospector's "check, not assume" instruction): the page documents that cache
  affinity is *derived from a client-supplied value* but reports no exposure;
  whether a multi-tenant caller can deliberately influence cross-tenant cache
  affinity by choosing `metadata.user_id` is not claimed as a vulnerability and
  should not be recorded as one — but the derivation rule makes it a legitimate
  audit question for identity-bound trust boundaries.

### Claim 3: On the chat-completions path the same two parameters are derived differently — `user` is passed through untruncated, and `prompt_cache_key` is only set when the target provider's supported-params list includes it (OpenAI/Azure OpenAI yes; Gemini, Vertex AI, Bedrock, Anthropic no)
- **Evidence**: The paragraph following the top-level table, describing the
  `use_chat_completions_url_for_anthropic_messages: true` path and every
  non-OpenAI provider.
- **Confidence**: settled (explicit documented path split with a named
  provider list)
- **Quote**: "The chat-completions path (`litellm_settings.use_chat_completions_url_for_anthropic_messages: true`, and every non-OpenAI provider) derives the same two parameters from `metadata.user_id`, with two differences: `user` is passed through untruncated, and `prompt_cache_key` is only set when the target provider's supported params include it. OpenAI, Azure OpenAI and other OpenAI-compatible providers do; Gemini, Vertex AI, Bedrock and Anthropic do not."
- **Our assessment**: The derivation is *path- and provider-gated*: the same
  request yields cache affinity on OpenAI/Azure but not on Gemini/Vertex/Bedrock/
  Anthropic via chat-completions. For a multi-backend gateway with fallbacks,
  the prompt-cache property of a request is not a constant — it depends on which
  backend wins the route. Note the practical consequence for Anthropic:
  Anthropic-side prompt caching on this surface is not achieved via a derived
  key at all (Anthropic uses its own auto-caching / `cache_control` markers; see
  `blog-litellm-save-claude-code-costs` Claim 3) — the `prompt_cache_key` field
  is an OpenAI-family mechanism.

### Claim 4: `litellm_proxy/` deployments (one LiteLLM proxy in front of another) never get the derived `prompt_cache_key` because the downstream proxy's real provider is unknown — a chained gateway silently loses prompt-cache affinity, so hit rate and cost shift with topology
- **Evidence**: The closing sentence of the chat-completions-path paragraph,
  naming the proxy-hop condition and the `drop_params` escape valve.
- **Confidence**: settled (explicit documented condition; the cache/cost-topology
  reading is the Miner's synthesis of the stated mechanism)
- **Quote**: "`litellm_proxy/` deployments (one LiteLLM proxy in front of another) never get the derived key, because the downstream proxy's real provider is unknown and would reject it unless `drop_params` is set there."
- **Our assessment**: The operational payoff claim. The justification is the
  *safe-degradation* one: sending an unknown provider a param it does not
  support risks a rejected request, so the key is simply omitted — cache
  affinity is silently traded away in exchange for forward compatibility. There
  is no documented signal that the derived key was withheld. This is
  topology-dependent behavior behind an unchanged client request: the same
  request keeps cache affinity when issued directly to a single-hop proxy and
  loses it when the topology adds a hop. Cost/cache dashboards must be read
  with topology in mind (see Guide Impact).

### Claim 5: `thinking.budget_tokens` is quantized into a coarse four-rung `reasoning.effort` ladder (`>=10000`→`high`, `>=5000`→`medium`, `>=2000`→`low`, `<2000`→`minimal`) with `summary` forced to `"detailed"`; any `thinking.type` other than `"enabled"` means the `reasoning` field is not sent at all — inferred thinking depth is lossy after translation
- **Evidence**: The "thinking → reasoning" section gives the bucket table and
  the two unconditional statements on `summary` and `type`.
- **Confidence**: settled for the documented mapping (unconditional wording);
  "lossy inference-depth" is the Miner's reading of the bucket granularity
- **Quote**: "The `budget_tokens` value is mapped to a string effort level. `summary` is always set to `\"detailed\"`." / "If `thinking.type` is anything other than `\"enabled\"`, the `reasoning` field is not sent at all."
- **Our assessment**: Three distinct hazards. (1) Bucket collapse: budgets of
  2000 and 4999 map to the same `low` effort and budgets of 10000 and 40000 to
  the same `high` — cost and latency characteristics change without any
  request-level signal. (2) `summary` is unconditionally overwritten to
  `"detailed"`, which **contradicts the overview page's "preserved and
  forwarded" claim** on the same surface (see Cross-References → Contradicts,
  issue **#1408**). (3) `thinking.type: "adaptive"` (or any non-`"enabled"`
  value) silently drops the reasoning field entirely — an adaptive-thinking
  caller's intent is not only unbucketed but absent. Contrast with the native
  Anthropic path in `blog-litellm-claude-fable-5-day-0` (explicit budgets → 400,
  loud) and the Gemini path in `blog-litellm-gemini-3-5-flash-day-0` (a
  different effort mapping entirely).

### Claim 6: Each Anthropic message is expanded into one or more Responses API input items, and `tool_result` / `tool_use` blocks are hoisted out of their message into *top-level* items (`function_call_output` / `function_call`) rather than nested — image blocks become `input_image` (data-URI or URL), thinking blocks become `output_text`
- **Evidence**: The "How messages get converted" section's full expansion
  table, whose per-row notes state the hoisting ("pulled out of the message
  entirely") and the top-level item shapes.
- **Confidence**: settled (explicit table of mechanical per-block transforms)
- **Quote**: "Each Anthropic message is expanded into one or more Responses API input items. The key difference is that `tool_result` and `tool_use` blocks become **top-level items** in the input array rather than being nested inside a message." / "pulled out of the message entirely"
- **Our assessment**: Structural, not semantic: the *shape* of the input changes
  (message-nested blocks → top-level items) while the *meaning* is preserved.
  The hoisting is the correct Responses-API-shaped form, but any middleware —
  guardrail, log scrubber, or e2e assertion — that assumes Anthropic message
  structure sees a different structure after the first hop, and a monitor that
  counts "messages" on the outbound request will under-count tool-carrying turns
  by the number of hoisted items. This is the same "path changes what a tool
  sees" theme as the A2A chat-completions bridge's structural collapse in the
  corpus ([docs-litellm-a2a-invoking-agents, Claim 2]) — the lossy/invasive
  surface belongs to whoever inspects mid-path, which is a guardrail-operator
  concern in Ch06 terms.

### Claim 7: `tools` and `tool_choice` are type-remapped, not passed through — Anthropic web-search tools become `{"type": "web_search_preview"}`; `tool_choice` `"any"` becomes `{"type": "required"}` and `"tool"` becomes `{"type": "function", "name": ...}`
- **Evidence**: The "tools" and "tool_choice" sections' mapping tables; the
  tool_choice remap of `"any"` → `{"type": "required"}` is a semantic
  strengthening (Anthropic "use any available tool" → OpenAI "a tool call is
  required").
- **Confidence**: settled (explicit tables)
- **Quote**: "Any tool where `type` starts with `\"web_search\"` or `name == \"web_search\"`" / "All other tools" / "`\"any\"`" / "`{\"type\": \"required\"}`"
- **Our assessment**: The `"any"` → `required` remap is a subtle behavior
  change a caller would not notice: Anthropic's `tool_choice: "any"` permits the
  model to call a tool (and still complete without one); OpenAI's `required`
  demands a function call. An agent scripted against `"any"` semantics can
  diverge (forced tool call) after translation. This is the same class of
  forward-shape translation bug the corpus already records on this exact
  surface — `blog-litellm-auto-router-v2` Claim 10 (`/v1/messages`→Responses
  `tool_choice` shape bug on Bedrock-backed routers) — here documented as
  intended behavior rather than a bug.

### Claim 8: `system` content-block lists are lossy-joined — text blocks are joined with `\n` and non-text blocks are silently ignored — and `context_management` is converted from an Anthropic nested dict with an `edits` array into a flat OpenAI array of compaction objects
- **Evidence**: The top-level table's `system` (list) row note; the
  "context_management" section with the worked `{"edits":[...]}` →
  `[{"type": "compaction", ...}]` example.
- **Confidence**: settled (explicit notes + worked conversion example)
- **Quote**: "Text blocks are joined with `\n`; non-text blocks are ignored" / "Anthropic uses a nested dict with an `edits` array. OpenAI uses a flat array of compaction objects."
- **Our assessment**: Two silent transforms of request content. Dropping
  non-text system blocks (e.g. a thinking image or a `tool_use`-style block in
  `system`) is a content-loss path with no error; and the compaction conversion
  (`compact_20260112` + input-token trigger → `compact_threshold`) maps an
  Anthropic-shaped control over context trimming onto OpenAI's flat form — the
  "dict → array" conversion in Concrete Artifacts is the doc's only worked
  example of the nested-to-flat pattern and is the reference for anyone modeling
  the compaction surface.

### Claim 9: The response direction is also lossy — `response.model` falls back to `"unknown-model"` when missing, `stop_sequence` is always `null` on this path, and `type: "message"` / `role: "assistant"` are hardcoded
- **Evidence**: The "Response: Responses API → Anthropic" table rows for
  `model` (with fallback note), `stop_sequence` ("Always null on this path"),
  and `type` / `role` ("Always set").
- **Confidence**: settled (explicit table)
- **Quote**: "Falls back to `\"unknown-model\"` if missing" / "Always null on this path" / "Always set"
- **Our assessment**: Attribution/observability caveats. `"unknown-model"`
  interacts directly with the guide's "Silent model fallback breaks attribution"
  section (guide/05-llm-ops-reliability.md ~L972-985): a response whose `model`
  this page documents as falling back to a placeholder is the modeled-unknown
  case of that rule — an operator who surfaces the response-`model` field per
  that rule must also handle the literal `"unknown-model"` value, not assume the
  requested model name. `stop_sequence: null` always means a caller branching on
  `stop_sequence` (valid on native Anthropic paths, where the overview page
  lists it as a possible `stop_reason` value) cannot distinguish "no stop
  sequence" from "stop-sequence feature absent" on this path. There is no error
  surface for any of it.

### Claim 10: In the response direction, `function_call` presence yields `stop_reason: "tool_use"`, `response.status == "incomplete"` yields `stop_reason: "max_tokens"` — stated to "Take[] precedence over the default" (`end_turn`) — but the page does not state the relative precedence between the `tool_use` and `max_tokens` triggers
- **Evidence**: The response table's three `stop_reason` rows. The precedence
  note ("Takes precedence over the default") is attached only to the
  `incomplete` → `max_tokens` row, whose "default" is the "Everything else →
  end_turn" row; no row or note resolves what happens when a response is *both*
  truncated and tool-calling.
- **Confidence**: emerging for the mapping rows (explicit); the
  conflicted-case behavior is **not** documented by the page and is flagged
  open pending verification against the named implementation file
  (`transformation.py`), per the Prospector's instruction not to treat the
  sharpest claim as settled without verification
- **Quote**: "Takes precedence over the default"
- **Our assessment**: The Prospector's triage flagged this as the sharpest
  claim on the page: whether a client can detect truncation from `stop_reason`
  when a response is both truncated and contains a tool call. Two triage passes
  on #1390 disagreed on the reading (one asserted `tool_use` wins, one asserted
  `max_tokens` wins). The page itself does neither — it attaches "Takes
  precedence over the default" to the `incomplete` row (precedence over
  `end_turn`) and leaves the trigger-trigger conflict unstated. Verified the
  same way the Prospector did (both mapping rows present, one note). The Miner
  did **not** fit the code (no network access to the repo file), so the
  conflicted-case behavior remains open: a downstream agent loop that treats
  `stop_reason: "tool_use"` as terminal could misbehave on a truncated+tool
  response if `tool_use` wins, and one that treats `max_tokens` as terminal
  could drop a usable tool call if `max_tokens` wins. Record as a
  verification-open claim, not settled behavior.

### Claim 11: Response fields map cleanly in one direction and are JSON-reconstructed in the other — `input_tokens`/`output_tokens` map field-for-field, `arguments` is JSON-parsed back into a dict for `tool_use.input`, and each non-empty `ResponseReasoningItem.summary[*].text` becomes a `{"type": "thinking", "thinking": "..."}` content block
- **Evidence**: The response table rows for usage, `ResponseFunctionToolCall`
  (with "`arguments` is JSON-parsed back into a dict"), and
  `ResponseReasoningItem` (with "Each non-empty summary text becomes a thinking
  block").
- **Confidence**: settled (explicit table)
- **Quote**: "`arguments` is JSON-parsed back into a dict" / "Each non-empty summary text becomes a thinking block"
- **Our assessment**: The reverse direction reconstructs Anthropic content
  blocks, so `usage` accounting stays attributable (pairing with
  `docs-litellm-anthropic-unified` Claim 9's cache-token fields) and tool-call
  round-trips work — with the caveat that thinking blocks are rebuilt only from
  *non-empty* summaries, so reasoning items with empty summaries vanish from
  the Anthropic-shaped response.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/anthropic_unified/messages_to_responses_mapping.

### Top-level parameter mapping, request direction (verbatim table)

| Anthropic (`/v1/messages`) | Responses API | Notes |
|---|---|---|
| `model` | `model` | Passed through as-is |
| `messages` | `input` | Structurally transformed — see the messages section below |
| `system` (string) | `instructions` | Passed as a plain string |
| `system` (list of content blocks) | `instructions` | Text blocks are joined with `\n`; non-text blocks are ignored |
| `max_tokens` | `max_output_tokens` | Renamed |
| `temperature` | `temperature` | Passed through as-is |
| `top_p` | `top_p` | Passed through as-is |
| `tools` | `tools` | Format-translated — see the tools section below |
| `tool_choice` | `tool_choice` | Type-remapped — see the tool_choice section below |
| `thinking` | `reasoning` | Budget tokens mapped to effort level — see the thinking section below |
| `output_format` or `output_config.format` | `text` | Wrapped as `{"format": {"type": "json_schema", "name": "structured_output", "schema": ..., "strict": ...}}`. `strict` is copied from the request's `strict` flag and defaults to `false`, so schemas with optional properties pass through; set `strict: true` to opt into OpenAI strict mode, which requires every property in `required` |
| `context_management` | `context_management` | Converted from Anthropic dict to OpenAI array format — see the context_management section below |
| `metadata.user_id` | `user` | Extracted from the metadata object and truncated to 64 characters |
| `metadata.user_id` | `prompt_cache_key` | Same value, truncated to 64 characters (OpenAI's key limit), so one user's requests keep hitting the same prompt cache. Not set when `user_id` is empty or null. A `prompt_cache_key` sent in the request body wins over the derived one |
| `stop_sequences` | ❌ Not mapped | Dropped silently |
| `top_k` | ❌ Not mapped | Dropped silently |
| `speed` | ❌ Not mapped | Only used to set Anthropic beta headers on the native path |

### Messages → input items expansion (verbatim table)

| Anthropic message | Responses API input item |
|---|---|
| `user` role, string content | `{"type": "message", "role": "user", "content": [{"type": "input_text", "text": "..."}]}` |
| `user` role, `{"type": "text"}` block | `{"type": "input_text", "text": "..."}` inside a user message |
| `user` role, `{"type": "image", "source": {"type": "base64"}}` | `{"type": "input_image", "image_url": "data:<media_type>;base64,<data>"}` inside a user message |
| `user` role, `{"type": "image", "source": {"type": "url"}}` | `{"type": "input_image", "image_url": "<url>"}` inside a user message |
| `user` role, `{"type": "tool_result"}` block | Top-level `{"type": "function_call_output", "call_id": "...", "output": "..."}` — pulled out of the message entirely |
| `assistant` role, string content | `{"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "..."}]}` |
| `assistant` role, `{"type": "text"}` block | `{"type": "output_text", "text": "..."}` inside an assistant message |
| `assistant` role, `{"type": "tool_use"}` block | Top-level `{"type": "function_call", "call_id": "<id>", "name": "...", "arguments": "<JSON string>"}` — pulled out of the message entirely |
| `assistant` role, `{"type": "thinking"}` block | `{"type": "output_text", "text": "<thinking text>"}` inside an assistant message |

### `thinking` → `reasoning` bucket table (verbatim)

| `thinking.budget_tokens` | `reasoning.effort` |
|---|---|
| \>= 10000 | `"high"` |
| \>= 5000 | `"medium"` |
| \>= 2000 | `"low"` |
| < 2000 | `"minimal"` |

### `context_management` conversion (verbatim worked example)

```
Anthropic input:
{
  "edits": [
    {
      "type": "compact_20260112",
      "trigger": {"type": "input_tokens", "value": 150000}
    }
  ]
}
Responses API output:
[
  {"type": "compaction", "compact_threshold": 150000}
]
```

### Response direction: Responses API → Anthropic (verbatim table)

| Responses API field | Anthropic response field | Notes |
|---|---|---|
| `response.id` | `id` | |
| `response.model` | `model` | Falls back to `"unknown-model"` if missing |
| `ResponseReasoningItem` — `summary[*].text` | `content` block `{"type": "thinking", "thinking": "..."}` | Each non-empty summary text becomes a thinking block |
| `ResponseOutputMessage` — `content[*]` where `type == "output_text"` | `content` block `{"type": "text", "text": "..."}` | |
| `ResponseFunctionToolCall` — `{call_id, name, arguments}` | `content` block `{"type": "tool_use", "id": "...", "name": "...", "input": {...}}` | `arguments` is JSON-parsed back into a dict |
| Any `function_call` present in output | `stop_reason: "tool_use"` | |
| `response.status == "incomplete"` | `stop_reason: "max_tokens"` | Takes precedence over the default |
| Everything else | `stop_reason: "end_turn"` | Default |
| `response.usage.input_tokens` | `usage.input_tokens` | |
| `response.usage.output_tokens` | `usage.output_tokens` | |
| *(hardcoded)* | `type: "message"` | Always set |
| *(hardcoded)* | `role: "assistant"` | Always set |
| *(hardcoded)* | `stop_sequence: null` | Always null on this path |

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/blog-litellm-auto-router-v2.md` — **Cited** (Corroborates /
  Extends, see below): Claim 10 documents the `/v1/messages`→Responses API
  `tool_choice` shape bug as history; this page documents the *current*
  intended `tool_choice` remap on the same surface (Claim 7 here).
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session cost/iteration caps; no Anthropic/Responses parameter translation.
- `source-notes/docs-litellm-a2a-invoking-agents.md` — **Dismissed** as a
  translation source, but the structural-collapse precedent is noted in Claim 6:
  the "task-shaped agent → one chat.completions round-trip" collapse is the same
  "path re-shapes what a mid-path tool sees" theme.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **Dismissed**:
  Langfuse guardrail-scanner stacks and latency drivers; unrelated to this
  translation surface.
- `source-notes/docs-litellm-a2a-agent-card.md` — **Dismissed**: A2A agent-card
  passthrough matrix; unrelated to parameter translation.
- `source-notes/docs-litellm-generic-guardrail-api.md` — **Cited** (Extends, see
  below): guardrail interception of `/v1/messages` and tool-forwarding scope are
  the *inbound* surface; this page's translation is what the outbound request
  looks like after interception.
- `source-notes/blog-litellm-gemini-3-5-flash-day-0.md` — **Cited**
  (Corroborates, see below): a different provider's thinking-effort mapping
  ([Claim 3]`reasoning_effort` → Gemini `thinkingLevel`) plus `top_k`
  deprecation warnings ([Claim 5]) contrast with this page's silent `top_k`
  drop on the OpenAI path.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **Dismissed**: A2A
  cost-tracking ledger; unrelated.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: Langfuse docs MCP
  server; unrelated.
- `source-notes/docs-litellm-anthropic-count-tokens.md` — **Cited** (see below):
  sibling `/v1/messages` surface — the token-counting pre-flight endpoint from
  the same docs family; its "verify per-provider" lesson applies to the
  cache-key derivation here too.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-anthropic-unified.md` (issue #1382, the parent
    overview note) — the two notes describe the same endpoint family: this page
    is the *translation tables* behind the overview's fan-out surface. Overview
    Claim 6 (thinking `budget_tokens` range constraints, `0 < temperature < 1`)
    and Claim 8 (Anthropic response field contract) both appear here as explicit
    per-field mapping rows on the OpenAI/Azure path. Overview Claim 9
    (cache-token accounting on the response) pairs with Claim 11 here (usage
    maps field-for-field). No conflict on those — the conflict is on `summary`
    (see **Contradicts**).
  - `source-notes/blog-litellm-gemini-3-5-flash-day-0.md` **Claim 5** — Google
    deprecation-warns on `top_k` for Gemini 3.5+; this page **silently drops**
    `top_k` on the OpenAI/Azure Responses path. Same parameter, different
    failure style (warning vs silent) — both are gateway translation responses
    to a parameter the downstream model cannot interpret.
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claims 1-2** —
    a gateway translation change that "can still silently destroy a provider's
    prefix-based prompt cache" while returning 200s. This page's Claim 4
    (proxy-hop topology silently loses cache affinity) is the same family: the
    gateway silently degrades cache behavior without an error surface.
- **Contradicts**:
  - **`source-notes/docs-litellm-anthropic-unified.md` Claim 7** — that note's
    overview page states: "When routing to non-Anthropic providers (e.g.,
    `openai/gpt-5.6-terra`), the `summary` value is preserved and forwarded to
    the downstream API." This page states the `thinking`→`reasoning`
    translation "always set[s]" `summary` to `"detailed"` on the OpenAI/Azure
    Responses path (Claim 5 here) — i.e. the caller's `summary` choice does not
    survive that path. **Contradiction issue [#1408](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1408)
    filed** per MINER.md §4a (filer's advisory verdict: `debated` — likely
    path-dependent between the Responses adapter and a chat-completions path;
    do not pick a verdict here). This is the note's only contradiction; details
    in the issue. Also checked the other open contradiction issues (#1150,
    #1307, #1322, #1338, #1352) and `CONTRADICTIONS.md` (no `C-NNN` entries) —
    none cover this surface.
- **Extends**:
  - `source-notes/failure-litellm-encrypted-content-affinity.md` — per the
    Prospector's explicit instruction: **cross-link, do not merge**. That
    incident is *routing* affinity for encrypted content on the Responses path
    (pin follow-up requests to the creating deployment); this page is *cache-key
    derivation* for prompt-cache affinity (same-value truncation of
    `metadata.user_id`). Both are gateway mechanisms that determine where a
    follow-up request lands/caches, but one pin is deployment identity and the
    other is user identity — operators should not conflate the two affinity
    axes.
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 3** — that
    note's proxy-injected `cache_control` markers are how Anthropic-side prompt
    caching is achieved without client changes; this page's derived
    `prompt_cache_key` is a separate, OpenAI-family identity-based cache-affinity
    mechanism. Together they give the gateway operator two cache-affinity tools
    that do not transfer across provider families.
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 4** — the guardrail
    "non-streaming only" carve-out plus this page's translation together mean a
    guardrail on `/v1/messages` inspects Anthropic-shaped input while the
    outbound OpenAI/Azure request is structurally different (Claim 6 here):
    mid-path enforcement must expect the translated shape.
  - `source-notes/docs-litellm-generic-guardrail-api.md` **Claims 2 & 5** — the
    guardrail intercepts `/v1/messages` and forwards `tools`/`tool_calls`; this
    page documents the translation those tool shapes go through afterwards
    (top-level `function_call_output`/`function_call`, Cite 7 remap).
  - `source-notes/blog-litellm-auto-router-v2.md` **Claim 10** — the corpus's
    prior `/v1/messages`→Responses `tool_choice` translation bug (Bedrock-backed
    routers) is extended by this page into a complete, documented translation
    spec for the OpenAI/Azure path.
  - `source-notes/docs-litellm-anthropic-count-tokens.md` — the "verify per
    provider, don't assume uniformity" lesson (its Claims 2, 3) applies to the
    cache-key derivation here: whether a request gets a `prompt_cache_key`
    depends on the routed provider's supported-params list (Claim 3 here).
- **Novel**: First corpus coverage of the **`/v1/messages` → Responses API
  bidirectional translation spec** — nothing in `source-notes/` or `guide/`
  contains `messages_to_responses`, `responses_adapters`, or `prompt_cache_key`
  (re-verified this session, matching the Prospector's zero-hit grep).
  Specifically new: the silent drops (`stop_sequences`, `top_k`, and the
  `speed` beta-header note); the identity-derived `prompt_cache_key` (64-char
  truncation, empty/body-override rules, chat-completions path asymmetry, and
  the proxy-hop "never get the derived key" caveat); the `budget_tokens` →
  `reasoning.effort` 4-bucket quantization with forced `summary`; the
  tool/`tool_choice` type-remaps (`"any"` → `{"type": "required"}`,
  web-search → `web_search_preview`); the `tool_result`/`tool_use` top-level
  hoisting; the `context_management` dict→array conversion; and the response
  direction's `"unknown-model"` fallback / always-null `stop_sequence` /
  hardcoded `type`/`role` / `stop_reason` precedence rows.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Parameter migration hazards"
  (guide/05-llm-ops-reliability.md ~L327-341)**: The chapter's existing rule —
  "audit existing request parameters against the model's supported set before
  routing production traffic … Parameters valid on earlier models may be
  silently ignored or explicitly rejected" — is currently illustrated only by
  *model-side* rejections (Fable 5's 400s). Extend it with the *gateway-induced*
  drop class this page documents [source: docs-litellm-messages-to-responses-mapping,
  Claim 1] [settled]: when a gateway translates a request onto another API
  family (here `/v1/messages`→Responses for OpenAI/Azure), parameters may be
  dropped *silently* (`stop_sequences`, `top_k`) with a 200 and no
  error/telemetry. Add the consequence from Claim 1: parameter intent must be
  verified **after** routing (inspect or test the outbound request), not only
  at the client, because the 200 gives no signal the constraint was ignored.
- **Chapter 05, "Silent model fallback breaks attribution"
  (guide/05-llm-ops-reliability.md ~L972-985)** — the section's rule is to
  "surface the `model` field from the response metadata." Add that this field is
  itself lossy on this path: `response.model` falls back to the literal
  `"unknown-model"` when missing [Claim 9] [settled], so attribution must also
  branch on that sentinel — requesting-model, responded-model, and
  `"unknown-model"` are three distinguishable states after translation.
- **Chapter 05, "Session-affine routing preserves provider-side prompt caches"
  (guide/05-llm-ops-reliability.md ~L1056-1071)**: The chapter treats cache
  preservation as a routing/affinity property. Add the *identity-derived cache
  key* as a second, orthogonal cache-affinity mechanism: LiteLLM derives
  `prompt_cache_key` from `metadata.user_id` (64-char truncation; body-level key
  wins; absent when `user_id` empty) [Claim 2] [settled], gated per provider and
  per path (OpenAI/Azure yes, Gemini/Vertex/Bedrock/Anthropic no on the
  chat-completions path; Responses path derives only for OpenAI/Azure) [Claim 3]
  [settled], and **topology-dependent** — `litellm_proxy/` chained deployments
  never receive it [Claim 4] [settled]. Recommendation: cache hit-rate and cost
  telemetry must be read with topology in mind; a topology change (adding a
  proxy hop) can silently move a request class from cache-hit to cache-miss.
- **Chapter 05, "A multi-backend fallback that silently shifts … changes the
  model's reasoning behavior" (~L320-325)**: Add the effort-bucket loss: a
  same-request thinking budget is quantized to a four-rung `reasoning.effort`
  ladder on the OpenAI/Azure path, so budgets inside one bucket are
  indistinguishable and cost/latency change without a request-level signal;
  `summary` is forced to `"detailed"`; non-`"enabled"` `thinking.type` omits the
  `reasoning` field entirely [Claim 5] [settled]. Verify the file
  (`responses_adapters/transformation.py`) before instructing on behavior when a
  response is both truncated and tool-calling — the push `stop_reason`
  precedence is not documented by the page [Claim 10] [emerging].
- **Chapter 02 (Observability)**: Add `"unknown-model"` and always-null
  `stop_sequence` as expected response values on translation paths (Claim 9)
  so monitors/eval scrapers branch on them rather than alerting on an
  "unknown model" ghost; and note that a mid-path inspector (log scrubber,
  guardrail, e2e assert) sees Responses-API-shaped input items after
  translation — including hoisted `function_call_output`/`function_call` — not
  Anthropic message blocks [Claim 6] [settled].
- **Chapter 06 (Security and Trust)**: Two notes, both cautious. (1) The derived
  `prompt_cache_key` is computed from a *client-supplied* `metadata.user_id`,
  truncated to 64 chars [Claim 2] [settled] — record as an open audit question
  for identity-bound cache affinity on multi-tenant gateways (whether a caller
  can influence cross-tenant cache affinity by choosing `user_id`); the source
  reports no exposure and none is claimed here. (2) Guardrail coverage on
  `/v1/messages` is shaped by the translation: the interception sees
  Anthropic-shaped input while the outbound request is structurally different
  [Claim 6, with docs-litellm-generic-guardrail-api] — enforcement surfaces on
  the intermediary must be validated against the translated shape.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/anthropic_unified/messages_to_responses_mapping`,
  HTTP 200, no paywall). The page is table-dense; per the Prospector's explicit
  instruction ("extract the tables rather than paraphrase them"), the full
  mapping tables are reproduced verbatim in Concrete Artifacts. No sub-pages
  followed: the only outbound links are nav siblings (the overview page #1382,
  `structured_output` #1391, `native_passthrough`) whose scope the Prospector
  already scoped out; the overview note (#1382) was read in full in its merged
  form since the two pages are the overview/detail pair.
- All `Quote` fields are character-for-character contiguous fragments from the
  fetched page prose or table cells; no splicing across non-adjacent sentences.
  Table notes are quoted as single cells. In the `thinking`→`reasoning` quotes,
  inner double quotes are escaped as they render in the page text.
- **Contradiction issue [#1408](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1408)
  filed** per MINER.md §4a before this PR: the overview note's Claim 7
  ("`summary` … preserved and forwarded to the downstream API" when routing to
  non-Anthropic providers) is opposed by this page's unconditional "`summary`
  is always set to `"detailed"`" on the OpenAI/Azure Responses path (Claim 5
  here). No verdict picked in this note; verified no existing open
  contradiction covers it (#1150, #1307, #1322, #1338, #1352 open; 
  `CONTRADICTIONS.md` has no `C-NNN` entries). This note carries the reference
  under **Contradicts:** per MINER.md §4a step 2.
- **Verification-open item recorded, not resolved**: the triage's sharpest
  claim (whether `stop_reason: "tool_use"` or `incomplete`→`"max_tokens"`
  wins when a response is both truncated and tool-calling) is *not* stated by
  the page — "Takes precedence over the default" is attached to the
  `incomplete`→`max_tokens` row, whose default is `end_turn`. The Miner could
  not reach the referenced implementation file
  (`litellm/llms/anthropic/experimental_pass_through/responses_adapters/transformation.py`)
  from this runner; per the Prospector's instruction the claim is left
  `emerging` and flagged open in Claim 10 rather than asserted.
- **Ch06 open question recorded, not asserted**: the page derives
  `prompt_cache_key` from client-supplied `metadata.user_id`; the Prospector's
  instruction was to note the tenant-influence question with the documented
  derivation/truncation rules, without recording a vulnerability (the source
  reports none). Done in Claim 2 and Guide Impact (Ch06).
- Cross-reference verification (MINER §4b): re-read the cited claims in
  `docs-litellm-anthropic-unified.md` (Claims 6-9), `blog-litellm-gemini-3-5-flash-day-0.md`
  (Claims 3, 5), `failure-litellm-bedrock-invoke-prompt-cache.md` (Claims 1-2),
  `blog-litellm-save-claude-code-costs.md` (Claim 3),
  `docs-litellm-generic-guardrail-api.md` (Claims 2, 5),
  `blog-litellm-auto-router-v2.md` (Claim 10), and
  `docs-litellm-anthropic-count-tokens.md` (Claims 2-3) and confirmed numbered
  claims match their cited content. No claim numbers invented.
- `confidence_overall` set to `emerging`: every mapping row is settled first-party
  API-surface documentation, but the note's guide value is in the synthesis
  (silent-drop and cache-affinity losses, bucket-quantization) plus one
  explicitly unverified precedence question and one freshly filed contradiction
  — none of it exercised against a live backend. Matches the `emerging` ratings
  on the sibling LiteLLM docs notes (#1286, #1359, #1381, #1382).
- `date_published` unknown (undated living docs page); `date_extracted` and
  `last_checked` both 2026-09-22 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) — production-shaped drain.