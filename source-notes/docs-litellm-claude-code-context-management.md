---
source_url: https://docs.litellm.ai/docs/claude_code_context_management
source_type: docs
title: "Claude Code - Context Management — LiteLLM Documentation"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-24)
date_extracted: 2026-09-24
last_checked: 2026-09-24
status: current
confidence_overall: emerging
issue: "#1445"
---

# Claude Code - Context Management (LiteLLM Docs)

> LiteLLM's in-gateway polyfill for Anthropic's `context_management` beta (as
> sent by Claude Code on `/v1/messages`): the spec is passed through natively on
> Anthropic / Bedrock-Anthropic / OpenAI-Responses targets and *edited into the
> message array* by LiteLLM for every other provider. The ops-relevant content
> is the operator-visible contract of that polyfill — the routing-dependent
> semantics, two supported edit types (`clear_tool_uses_20250919`,
> `compact_20260112`) plus the `clear_thinking_20251015` gap, a hard 50,000-token
> trigger floor enforced as HTTP 400, a best-effort failure taxonomy
> (`applied_edits[].error` ∈ `summary_model_not_configured` /
> `summary_call_failed` / `summary_extraction_failed`) that degrades fail-open
> to the uncompacted conversation, accepted-but-ignored knobs, the
> `drop_params: true` false-assumption, and the `applied_edits` response
> telemetry (streaming: final `message_delta` SSE event). Not marketing — full
> knob tables, a provider support matrix, and error enums are the evidence.

## Source Context

- **Type**: docs (single-page LiteLLM gateway feature reference, part of the
  `litellm-docs` site-crawl seed, under the Claude Code tutorial family at
  `docs/tutorials/claude_code_context_management`).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented* polyfill surface — page gives knob tables,
  defaults, a provider support matrix, error enums, and worked request/response
  examples. This is vendor documentation of the product's own behavior: no
  independent validation exists, and the page itself labels two knobs surfaces
  as `(v0)` behavior that may change. Behavioral claims are treated as settled
  for LiteLLM product behavior per the Prospector's instruction, with the
  vendor-only provenance noted.
- **Scope**: The `context_management` polyfill end-to-end: routing-dependent
  semantics (native pass-through vs in-gateway polyfill), supported edit types,
  `compact_20260112` three-phase flow + summary-model dependency + failure
  taxonomy, `clear_tool_uses_20250919` knobs + hard floor, response shapes
  (non-streaming and streaming), opt-out mechanics, provider support matrix.
  Does NOT cover: `context_management` on the OpenAI Responses API at wire
  depth (that conversion is `docs-litellm-messages-to-responses-mapping.md`
  #1390 — see Cross-References for the layer reconciliation), sibling pages
  (#1444 `claude_code_compatibility`, #1443 `caching/local_caching`), or model
  pricing.
- **Redundancy**: `docs-litellm-messages-to-responses-mapping.md` (#1390)
  documents `context_management` as a *parameter transform* on the
  `/v1/messages`→OpenAI/Azure translation path (dict-with-`edits` → flat
  compaction-object array, its Claim 8 + worked example). This page documents
  what the edits *do* at runtime and who applies them per route. Complementary
  — complement, not duplicate; the two are reconciled explicitly here because
  the Prospector flagged the possible tension (see Extraction Notes).

## Extracted Claims

### Claim 1: Routing-dependent semantics — the same `context_management` spec gets native pass-through on Anthropic, Bedrock-Anthropic, and OpenAI-Responses targets, and an in-gateway polyfill (LiteLLM edits the message array before forwarding) on every other provider
- **Evidence**: The page's opening routing-path table maps each target class to
  an application mode: "Anthropic API" → "Passed through to the Anthropic
  server, which applies edits natively"; "OpenAI Responses API" → "Passed
  through; handled by the Responses API"; "Any other provider (OpenAI, xAI,
  Gemini, Azure, Bedrock non-Anthropic, …)" → "**In-gateway polyfill** - LiteLLM
  applies the edits to the message array before forwarding".
- **Confidence**: settled (explicit vendor routing table; the same request can
  traverse a different code path depending on the routed target — this is the
  "provider parity" hazard the triage called out)
- **Quote**: "When you send a request to `/v1/messages` (or via `litellm.anthropic.messages.*`) with a `context_management` spec, LiteLLM handles it in one of two ways depending on where the request is routed" / "Passed through to the Anthropic server, which applies edits natively" / "Passed through; handled by the Responses API" / "**In-gateway polyfill** - LiteLLM applies the edits to the message array before forwarding"
- **Our assessment**: The core fidelity-claim for the guide: an operator who
  assumes "`context_management` works everywhere" is right about the *surface*
  but wrong about the *mechanism*. Identical requests take three distinct paths
  (provider-native, Responses-native, gateway-edited). The polyfill path is the
  risky one because an operator who tests only on Anthropic never exercises the
  code path that production on OpenAI/Azure/Gemini actually runs. This is the
  same route-dependence class as the messages-to-responses translation note.

### Claim 2: The polyfill gives a write-once/run-anywhere property — the Claude Code tool-loop passes `context_management` as-is and it works regardless of which model is behind the proxy
- **Evidence**: The paragraph directly under the routing table states the
  value proposition.
- **Confidence**: settled (vendor statement of intended product behavior)
- **Quote**: "The polyfill means you write your Claude Code tool-loop once, pass `context_management` as you normally would, and it works regardless of which model is behind the proxy."
- **Our assessment**: This is the headline fine-for-who benefit, but the guide
  should pair it with the fidelity caveats in Claims 5-9: the promise is
  "compile once", not "identical behavior" — the polyfill is best-effort,
  fails open on summary errors, and ignores several accepted knobs. Treat
  "runs anywhere" as a targeting claim and the degradation path as the
  operational contract.

### Claim 3: Two edit types are supported (`clear_tool_uses_20250919`, `compact_20260112`) and `clear_thinking_20251015` is listed as "Coming soon" — a current limitation that will date
- **Evidence**: The "Supported Edit Types" status table; the 
  `clear_thinking_20251015` row carries the ❌ marker.
- **Confidence**: settled (explicit status table; the "Coming soon" wording is
  the doc's own and is expected to change — the note flags it so the guide does
  not fossilize the gap)
- **Quote**: "`clear_tool_uses_20250919`" / "✅ **Supported**" / "Clears old `tool_result` content from conversation history when a trigger threshold is met, keeping only the most recent `N` tool results intact" / "`clear_thinking_20251015`" / "❌ Coming soon" / "Clears extended-thinking blocks from history" / "`compact_20260112`" / "✅ **Supported**" / "Summarisation edit - LiteLLM calls a configured summary model, injects the summary as a system prefix, and returns a `compaction` block in the response"
- **Our assessment**: Three edit types in the Anthropic shape, two
  implemented. The mining date-stamp makes this claim one the Smith should
  re-check: when the "Coming soon" row flips, this note's claim should flip
  with it. Note the edit-type IDs are date-encoded (20250919, 20260112) —
  LiteLLM treats them as stable capability names, which is convenient for
  version pinning but means the capability set is keyed to beta-dated IDs.

### Claim 4: `clear_tool_uses_20250919` preserves the message array structure (same message count, same role order) and rewrites old `tool_result.content` to `"[Cleared by context management]"`, with a hard floor: the most recently completed `tool_result` is never cleared regardless of `keep`
- **Evidence**: The Notes section states the structural-preservation rule
  verbatim; the `clear_tool_uses_20250919` section carries the hard-floor callout
  in a blockquote.
- **Confidence**: settled (explicit vendor statements, both mechanical)
- **Quote**: "**`clear_tool_uses_20250919`** preserves the message array structure: same number of messages, same role order. Only `tool_result.content` inside matching messages is replaced with `"[Cleared by context management]"`." / "**Hard floor:** regardless of `keep`, LiteLLM's polyfill never clears the most recently completed `tool_result` - the one the model is about to reply to."
- **Our assessment**: Two exact behaviors an operator must know. (1) The edit
  is content-scrub, not message-drop — the token savings are bounded by the
  size of the cleared `tool_result` payloads, not by message count. (2) The
  hard floor defines an irreducible token floor: the most recent completed
  `tool_result` is always forwarded, so there is a minimum per-request context
  that no `keep` setting can reduce. That is a real constraint for a
  long-running tool loop on a small-context backend — the floor is the "can't
  shrink below this" number to size budget around.

### Claim 5: `compact_20260112` requires `context_management_summary_model` in `general_settings`; without it the polyfill is a silent no-op — the edit is acknowledged but no compaction is performed
- **Evidence**: The Setup section states the config dependency and the no-op
  result; the Notes section restates it.
- **Confidence**: settled (explicit, stated twice)
- **Quote**: "Without this setting, the polyfill is a no-op and `applied_edits[0].error: \"summary_model_not_configured\"` is returned." / "**`compact_20260112` requires `context_management_summary_model`** to be set in `general_settings`. Without it, the edit is acknowledged but no compaction is performed."
- **Our assessment**: This is the highest-value exact failure surfaced by the
  page. The asymmetry is the trap: the request is *accepted*, the edit is
  *acknowledged*, the response carries an `applied_edits` entry — and nothing
  is compacted. A request-succeeded-write-path monitor sees a healthy call.
  Operators relying on compaction for cost control must alert on
  `summary_model_not_configured` specifically, because the response itself
  looks successful. This is exactly the silent-degradation class Ch05's
  parameter-migration section warns about, but it originates in *config*, not
  in a parameter drop.

### Claim 6: `compact_20260112` runs a three-phase flow — Phase A slices any existing compaction block (dropping everything before it and prepending its summary text to the system prompt), Phase B counts effective input tokens and forwards immediately if at or below threshold, Phase C calls the summary model only when over threshold and injects the result as a `"Previous conversation summary: ..."` system prefix plus a `compaction` content block in the response
- **Evidence**: The "How it works (3 phases)" section spells out A/B/C exactly.
- **Confidence**: settled (explicit procedural description)
- **Quote**: "If the message history already contains a `compaction` block (from a previous compaction round), everything before that block is dropped and its summary text is prepended to the system prompt. This ensures prior context is carried forward." / "LiteLLM counts the effective input tokens of the (sliced) message history. If at or below the trigger threshold, the request is forwarded immediately, with no summary call." / "Injected as a `\"Previous conversation summary: ...\"` prefix in the system message on the downstream model call" / "Returned as a `compaction` content block prepended to the response `content` array, so the Claude Code client can maintain rolling compaction state"
- **Our assessment**: The phased design means each round's summary is
  *carried forward* rather than recomputed from scratch — the previous summary
  becomes the system-prefix seed for the next summary. For cost accounting this
  is a nice property (compaction is incremental), but it also means compaction
  quality is compounding: a weak Phase-C summary degrades every subsequent
  round's context. The `"Previous conversation summary: ..."` system prefix is
  what the downstream model actually sees, so the model's effective context is
  "summary + last user turn" — the pre-compaction history is not visible to it.

### Claim 7: The polyfill is best-effort with a named error taxonomy — on any summary failure the original uncompacted conversation is forwarded unchanged and `applied_edits[0].error` is set to one of `summary_model_not_configured`, `summary_call_failed`, or `summary_extraction_failed`; the summary text must be wrapped in `<summary>...</summary>` tags or extraction fails
- **Evidence**: The "Error handling" section gives the header sentence and the
  three-row error table; the custom-prompt section states the `<summary>` tag
  requirement and the extraction failure path.
- **Confidence**: settled (explicit error enum + behavior sentence; the
  fail-open reading — uncompacted conversation forwarded, no request error — is
  the page's own wording)
- **Quote**: "The polyfill is best-effort. If the summary call fails or returns no parseable summary, the original conversation is forwarded unchanged and `applied_edits[0].error` is set:" / "The summary text must be wrapped in `<summary>...</summary>` tags. If the model returns text without these tags, `applied_edits[0].error: \"summary_extraction_failed\"` is set and the original (uncompacted) conversation is forwarded."
- **Our assessment**: The operational risk, stated plainly: failure is
  fail-open on the cost/context-window dimension. A summary-model outage does
  not fail the request, it silently restores the *full* input-token spend the
  compaction edit was meant to avoid — and the client gets a 200 with the whole
  history. An operator whose cost dashboards are built on "compaction is
  reducing input" will be unpleasantly surprised. The three error values are a
  monitorable enumeration: alert on any non-empty `applied_edits[].error`.
  Note the fail-open here is on *spend/context*, the inverse of a
  fail-open-on-guardrail where the safety control is skipped.

### Claim 8: `compact_20260112` has a hard 50,000-token trigger floor enforced at the proxy — a lower `trigger.value` is rejected with HTTP 400; the default is 150000 and `trigger.type` accepts only `"input_tokens"` (other values fall back with a warning)
- **Evidence**: The compact knobs table rows for `trigger.type` and
  `trigger.value`, plus the Notes bullet that states the 400 enforcement.
- **Confidence**: settled (explicit knob table + Notes restatement)
- **Quote**: "Only `\"input_tokens\"` is supported; other values fall back with a warning" / "Token threshold. Must be ≥ 50,000 or the request is rejected with a 400" / "The 50,000-token minimum for `compact_20260112` trigger is enforced at the proxy; requests with a lower value are rejected with HTTP 400."
- **Our assessment**: The floor is a *configuration* contract hidden from the
  client: a caller setting `trigger.value: 40000` (perfectly reasonable for a
  small-context backend) gets a hard 400 from the gateway even though the
  value is well-formed for the Anthropic API contract. It is the gateway, not
  the client, that owns this constraint, so the client cannot discover it via
  an Anthropic docs page. Contrast with the non-loud class elsewhere in this
  note: here the misconfiguration is *loud* (400), which at least fails closed.
  The fall-back-with-a-warning on non-`input_tokens` trigger types is the
  quieter sibling — a warning, not an error.

### Claim 9: Four knobs are accepted but ignored by the polyfill v0 — `pause_after_compaction`, `clear_at_least`, `exclude_tools`, `clear_tool_inputs` are acknowledged in the request and silently do nothing (a warning is noted in `applied_edits`)
- **Evidence**: The compact knobs table's `pause_after_compaction` row and the
  clear_tool_uses knobs table's `clear_at_least` / `exclude_tools` /
  `clear_tool_inputs` rows all carry the "Accepted" status with the ignored
  description.
- **Confidence**: settled (explicit table rows marking the `(v0)` behavior)
- **Quote**: "Accepted in request but ignored (warning noted in `applied_edits`)" / "Accepted in request but ignored by polyfill (v0)" / "Accepted in request but ignored by polyfill (v0)" / "Accepted in request but ignored by polyfill (v0)"
- **Our assessment**: The silent-acceptance class Ch05 already tracks under
  parameter-migration hazards, now instantiated in a *feature config* rather
  than a request parameter. Worse, these fields come from the Anthropic
  context-management vocabulary, so a config written against the native
  Anthropic API compiles and is accepted on the non-Anthropic polyfill path but
  its intent (`clear_at_least`, `exclude_tools`, `pause_after_compaction`) is
  discarded. The operator-visible signal is only a warning inside
  `applied_edits` on the response — invisible if nothing reads that field. Note
  the asymmetry: three of the four ignored knobs are on the
  *clear_tool_uses* surface, so an operator controlling exactly what gets
  cleared cannot actually do so through the polyfill.

### Claim 10: `drop_params: true` does NOT disable the polyfill — only per-model `additional_drop_params: ["context_management"]` (or omitting the field per-request) does; `drop_params` only drops genuinely unsupported parameters
- **Evidence**: The "Disabling Context Management" section: per-request by
  omission, per-model via `additional_drop_params`, and the explicit
  `drop_params` paragraph.
- **Confidence**: settled (explicit vendor statement negating the common
  assumption)
- **Quote**: "Simply don't include `context_management` in the request body." / "To opt a model out of the polyfill, list `context_management` in that model's `additional_drop_params`. LiteLLM will silently strip `context_management` from requests to that model instead of running the polyfill:" / "`drop_params: true` does not disable the polyfill. `context_management` is a LiteLLM-supported parameter (native on Anthropic, polyfilled elsewhere), and `drop_params` only drops genuinely unsupported parameters."
- **Our assessment**: A plausible operator assumption that is wrong. An operator
  who flips `drop_params: true` to "stop the gateway touching my messages"
  keeps the polyfill active — with a *silent-wrong-outcome* result when the
  knob is meant as a disable switch. The opt-out paths the page offers are
  coarser: omit the field (client must change) or per-model
  `additional_drop_params` (operator sets it once and LiteLLM silently strips
  the parameter, which also removes the edit the caller asked for — worth
  noting that the "disable" is itself silent on the request path).

### Claim 11: The observability surface is the response `context_management.applied_edits` object — present when an edit fires with `cleared_tool_uses`/`cleared_input_tokens` (or `summary_input_tokens`/`summary_output_tokens`), absent when the trigger is not met, and carried in the final `message_delta` SSE event on streaming
- **Evidence**: The Responses sections: the non-streaming response example, the
  "absent if trigger not met" sentence, and the streaming example whose final
  event is `message_delta` carrying `context_management.applied_edits`.
- **Confidence**: settled (explicit response shapes, non-streaming and
  streaming)
- **Quote**: "When at least one edit fires, the response includes a `context_management` field:" / "If the trigger was not met (context is still small), `context_management` is **absent** from the response." / "The `context_management.applied_edits` field is included in the final `message_delta` SSE event:"
- **Our assessment**: The exact signal an operator would alert on to detect a
  polyfill that stopped firing (see Claim 7). Two operational subtleties: (1)
  the *absence* semantics — no edits → no `context_management` field at all,
  so "field missing" is not an error, it is "below threshold"; (2) on streaming
  the edit telemetry is not in the incrementally-streamed content blocks, it
  debounces to the *final* `message_delta`, so an SSE parser that only reads
  `content_block_delta` events will never see it. Both make naive monitors
  blind to the compaction fleet's actual behavior.

### Claim 12: Polyfill threshold checks count tokens with `litellm.token_counter`, using tiktoken `cl100k_base` as the fallback for unknown models — so trigger decisions on non-OpenAI models are made with a possibly non-native tokenizer
- **Evidence**: The Notes bullet under "Token counting".
- **Confidence**: settled for the documented mechanism; the threshold-accuracy
  implication is the Miner's reading (flagged, see Our assessment)
- **Quote**: "**Token counting** for polyfill threshold checks uses `litellm.token_counter` (tiktoken `cl100k_base` fallback for unknown models)."
- **Our assessment**: A documented accuracy caveat for the gate that decides
  *whether an edit fires at all*: the 50,000/100,000/150,000 thresholds are
  enforced against a count produced by `litellm.token_counter`, which falls
  back to the cl100k_base tokenizer when the model is unknown. For an
  Anthropic or Gemini model without a registered tokenizer, the "input_tokens"
  judging the trigger is an approximation, so an edit can fire early or late
  relative to the model's own native count. This pairs with
  `docs-litellm-anthropic-count-tokens`'s per-provider counting caveats: token
  counting is provider/model-dependent across this gateway, and the polyfill
  threshold path inherits that.

### Claim 13: Client-side compaction blocks trigger slice-only forwarding with no summary model call — if the history already contains a `compaction` block but the request has no `compact_20260112` edit, LiteLLM moves the prior summary to the system prefix and sends only the latest user question downstream
- **Evidence**: The "Client-side compaction blocks (no `context_management` edit)"
  section.
- **Confidence**: settled (explicit vendor behavior statement)
- **Quote**: "If the request does **not** include a `compact_20260112` edit but the message history already contains a `compaction` block (e.g. from a previous Claude Code client-side compaction), LiteLLM automatically applies slice-only forwarding: the prior summary is moved to the system prefix and only the latest user question is sent downstream. No summary model call is made."
- **Our assessment**: A path that is *invisible* unless an operator inspects the
  payload: a Claude Code client that has done its own (client-side) compaction
  gets gateway-side slice-only forwarding as a free bonus — but nothing in the
  response flags it (no `context_management` field, since no edit fired). The
  cost effect (dramatically smaller input) shows up in token accounting as a
  drop with no attributed cause, and an operator debugging "why is this turn so
  cheap" will not find the reason in the response. It is the mirror image of
  the silent-no-op in Claim 5: one path *looks* like nothing happened but
  compaction happened; the other looks like everything worked but nothing was
  compacted.

## Concrete Artifacts

All artifacts verbatim from
https://docs.litellm.ai/docs/claude_code_context_management.

### Routing path table (verbatim)

| Routing path | How context_management is applied |
|---|---|
| **Anthropic API** | Passed through to the Anthropic server, which applies edits natively |
| **OpenAI Responses API** (e.g. `gpt-5.x-*`) | Passed through; handled by the Responses API |
| **Any other provider** (OpenAI, xAI, Gemini, Azure, Bedrock non-Anthropic, …) | **In-gateway polyfill** - LiteLLM applies the edits to the message array before forwarding |

### Supported edit types table (verbatim)

| Edit type | Status | What it does |
|---|---|---|
| `clear_tool_uses_20250919` | ✅ **Supported** | Clears old `tool_result` content from conversation history when a trigger threshold is met, keeping only the most recent `N` tool results intact |
| `clear_thinking_20251015` | ❌ Coming soon | Clears extended-thinking blocks from history |
| `compact_20260112` | ✅ **Supported** | Summarisation edit - LiteLLM calls a configured summary model, injects the summary as a system prefix, and returns a `compaction` block in the response |

### Provider support matrix (verbatim)

| Provider | `clear_tool_uses_20250919` | `compact_20260112` |
|---|---|---|
| `anthropic/*` | Native pass-through | Native pass-through |
| `bedrock/anthropic.*` | Native pass-through | Native pass-through |
| `openai/*` (Responses API) | Native pass-through | Native pass-through |
| `openai/*` (chat completions) | Polyfill | Polyfill |
| `azure/*` | Polyfill | Polyfill |
| `xai/*` | Polyfill | Polyfill |
| `gemini/*` | Polyfill | Polyfill |
| `vertex_ai/*` | Polyfill | Polyfill |
| All other providers | Polyfill | Polyfill |

### `compact_20260112` knobs table (verbatim)

| Field | Required | Default | Description |
|---|---|---|---|
| `trigger.type` | No | `"input_tokens"` | Only `"input_tokens"` is supported; other values fall back with a warning |
| `trigger.value` | No | `150000` | Token threshold. Must be ≥ 50,000 or the request is rejected with a 400 |
| `instructions` | No | Anthropic default prompt | Custom summarization prompt; must instruct the model to wrap output in `<summary>` tags |
| `pause_after_compaction` | Accepted | - | Accepted in request but ignored (warning noted in `applied_edits`) |

### `clear_tool_uses_20250919` knobs table (verbatim)

| Field | Required | Default | Description |
|---|---|---|---|
| `trigger.type` | No | `"input_tokens"` | `"input_tokens"` or `"tool_uses"` |
| `trigger.value` | No | `100000` | Threshold; edits fire when current value **exceeds** this |
| `keep.type` | No | `"tool_uses"` | Must be `"tool_uses"` |
| `keep.value` | No | `3` | Number of most-recent tool results to preserve |
| `clear_at_least` | Accepted | - | Accepted in request but ignored by polyfill (v0) |
| `exclude_tools` | Accepted | - | Accepted in request but ignored by polyfill (v0) |
| `clear_tool_inputs` | Accepted | - | Accepted in request but ignored by polyfill (v0) |

### Error handling table (verbatim)

> The polyfill is best-effort. If the summary call fails or returns no parseable summary, the original conversation is forwarded unchanged and `applied_edits[0].error` is set:

| `error` value | Cause |
|---|---|
| `"summary_model_not_configured"` | `context_management_summary_model` not set in `general_settings` |
| `"summary_call_failed"` | The summary model call raised an exception |
| `"summary_extraction_failed"` | Summary model response contained no `<summary>...</summary>` block |

### Summary model setup (verbatim config)

```yaml
# proxy_server_config.yaml
general_settings:
  context_management_summary_model: claude-sonnet-5   # any model alias in your model_list
```

(Source comment "any model alias in your model_list" is the page's own.)

### Per-model opt-out (verbatim config)

```yaml
# proxy_server_config.yaml
model_list:
  - model_name: gpt-4.1
    litellm_params:
      model: openai/gpt-4.1
      additional_drop_params: ["context_management"]
```

### `clear_tool_uses_20250919` response example (verbatim)

```json
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Based on the latest weather data..."}],
  "model": "gpt-5.6-luna",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 620,
    "output_tokens": 45
  },
  "context_management": {
    "applied_edits": [
      {
        "type": "clear_tool_uses_20250919",
        "cleared_tool_uses": 3,
        "cleared_input_tokens": 8240
      }
    ]
  }
}
```

### Streaming telemetry — final `message_delta` SSE event (verbatim, trimmed to the delta event)

```
event: message_delta
data: {
  "type": "message_delta",
  "delta": {"stop_reason": "end_turn", "stop_sequence": null},
  "usage": {"output_tokens": 45},
  "context_management": {
    "applied_edits": [
      {
        "type": "clear_tool_uses_20250919",
        "cleared_tool_uses": 3,
        "cleared_input_tokens": 8240
      }
    ]
  }
}
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/docs-litellm-messages-to-responses-mapping.md` (#1390) —
  **Cited** (see Extends + the layer reconciliation below): its Claim 8 +
  worked example cover the `/v1/messages`→OpenAI/Azure `context_management`
  dict→array *conversion*; this page covers the polyfill's *runtime behavior*.
- `source-notes/blog-litellm-save-claude-code-costs.md` (#668) — **Cited** (see
  Extends): the sibling Claude Code cost playbook, whose five levers this
  source extends with a sixth (conversation-history reduction).
- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch input-file
  rate limiting / enqueued-token reservations; no `context_management` surface.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: Bedrock native
  Invoke passthrough; unrelated to context editing.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session cost/iteration caps; no conversation-history editing.
- `source-notes/docs-litellm-bedrock-converse.md` — **Dismissed**: Bedrock
  Converse passthrough; unrelated to context editing.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: Langfuse docs MCP
  server; unrelated.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  transcription endpoint feature matrix; unrelated.
- `source-notes/docs-litellm-a2a-invoking-agents.md` — **Dismissed**: A2A
  agent invocation surfaces; its Claim 2's "context management" refers to A2A
  task context, a different concept from Anthropic's `context_management`.
- `source-notes/docs-litellm-helicone-integration.md` — **Dismissed**:
  Helicone telemetry integration; unrelated.

**Additional cross-references found by search of `source-notes/`** (the
candidates file's list was not exhaustive):

- **Corroborates**:
  - `source-notes/docs-litellm-anthropic-unified.md` (#1382) — the parent
    `/v1/messages` unified-endpoint note: the context-management polyfill rides
    exactly the cross-provider fan-out surface that note documents (Claim 1: one
    Anthropic-format route across all providers; Claim 5: Anthropic wire-format
    request validated then translated per-backend). This page adds the
    *feature-specific* fork LiteLLM applies inside that fan-out.
  - `source-notes/docs-litellm-anthropic-count-tokens.md` **Claim 7** — token
    counting across this gateway falls back to local tiktoken counting for
    unsupported/missing-key paths; this page's `litellm.token_counter`
    (cl100k_base) threshold path (Claim 12 here) is the same
    "counting is provider/model-dependent" family, now applied to a
    *trigger-gating* decision rather than a pre-flight helper. Both notes warn
    against assuming token counts are provider-native.
  - `source-notes/blog-litellm-headroom-integration.md` **Claim 8** — Headroom
    compression never compresses messages with Anthropic `cache_control`
    markers; the context-management polyfill rewrites `tool_result.content`
    without touching `cache_control` semantics. Both are gateway-side input-token
    reductions with explicit carve-outs that an operator must enumerate before
    trusting the lever.
- **Contradicts**: None filed, and no self-contradiction in the source. The
  one *possible* tension — `docs-litellm-messages-to-responses-mapping`
  (Claim 8) says `context_management` is converted to a flat OpenAI array on
  the `/v1/messages`→OpenAI path, while this page's routing table says the
  OpenAI Responses path "Passed through; handled by the Responses API" — is a
  **layer difference, not a claim conflict** (reconciled below), so no
  contradiction issue was filed (MINER §4a "when NOT to file": claims differ
  only by operation layer). Verified no open `contradiction`-labeled issue
  covers this surface: #1408 is `thinking.summary` on the same
  messages→Responses path (a different field), #1338/#1322 are A2A, and
  #1150/#1307/#1352 are unrelated; `CONTRADICTIONS.md` has no `C-NNN` entries.
- **Extends**:
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` **Claim 8** —
    **layer reconciliation** (per Prospector instruction): that note documents
    the *wire-format transform* — the Anthropic nested dict
    `{"edits":[{"type":"compact_20260112","trigger":{...}}]}` becomes the
    OpenAI flat array `[{"type":"compaction","compact_threshold":150000}]` when
    a `/v1/messages` request is translated toward OpenAI/Azure. This page
    documents *who applies the edits at runtime*: for the OpenAI Responses
    target that translated (converted) parameter is handed to the Responses API
    to apply natively ("handled by the Responses API"), and for every other
    provider LiteLLM itself polyfills the edits onto the message array. The
    mapping note is the translation layer; this page is the application layer.
    Both statements hold simultaneously — the Miner verified the mapping note's
    worked example (dict "edits" → `{"type": "compaction", "compact_threshold":
    150000}`) against this page's trigger-default of 150000 and both
    publications post-date the `compact_20260112` ID, so they describe the same
    feature at two layers. Cross-reference rather than restate, per the
    Prospector's explicit instruction.
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 8** (the five
    levers compose) — that note's cost playbook covers spend caps, fallbacks,
    prompt-cache injection, Headroom compression, MCP tool search, and auto
    routing; `context_management` adds a *history-dimension* lever (Claims 4-9
    here) that composes with rather than duplicates prompt caching (Claim 3
    there, "Prompt cache trims the static prefix") and compression — this source
    targets the conversation history itself. The composition claim there ("five
    features compose … each shave a different slice") now has a sixth slice.
  - `source-notes/docs-litellm-caching-all-caches.md` — response caching is an
    output/semantic cache; context management is an *input/history* edit. The
    two mechanisms target different dimensions and can be enabled on the same
    proxy (per the Prospector's note that this composes with rather than
    contradicts compression/caching input-token reducers).
- **Novel**: First corpus coverage of **gateway-side conversation-history
  editing / context management / compaction** — re-verified this session that
  `context_management`, `clear_tool_uses`, `compact_20260112`, and `compaction`
  appear nowhere in `guide/` (matching the Prospector's zero-hit grep) and only
  in the two translation-surface mentions in
  `docs-litellm-messages-to-responses-mapping.md` (Claim 8 + worked example),
  which do not describe polyfill runtime, knobs, floors, or the failure
  taxonomy. Specifically new: the routing-dependent native-vs-polyfill split;
  the `applied_edits[].error` enum (`summary_model_not_configured`,
  `summary_call_failed`, `summary_extraction_failed`); the 50,000-token HTTP-400
  floor; the hard floor (most recent completed `tool_result` never cleared);
  the accepted-but-ignored knob class (`pause_after_compaction`,
  `clear_at_least`, `exclude_tools`, `clear_tool_inputs`); the
  `drop_params: true` ≠ disable finding; the `applied_edits` streaming location
  (final `message_delta`); and the client-side-slice silent path.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Parameter migration hazards"
  (guide/05-llm-ops-reliability.md ~L327-341)**: The chapter's rule — "audit
  existing request parameters against the model's supported set before routing
  production traffic … may be silently ignored or explicitly rejected" — is
  currently illustrated by model-side rejections (400s) and the
  gateway-translation silent drops. Extend it with the *feature-config*
  version of the same hazard, exact to this surface: LiteLLM's `context_management`
  polyfill **accepts but ignores** `pause_after_compaction`, `clear_at_least`,
  `exclude_tools`, and `clear_tool_inputs` (Claim 9) [settled], so a config
  written against the native Anthropic vocabulary compiles and is acknowledged
  while its intent is discarded — with a warning only inside `applied_edits`.
  Add the Ch05 footgun from Claim 10 [settled]: `drop_params: true` does not
  disable the polyfill; the correct opt-out is per-model
  `additional_drop_params: ["context_management"]` — a plausible and wrong
  assumption.
- **Chapter 05, fail-open degradation on spend/context (extends the guardrail
  fail-open coverage)**: add the fail-open-on-cost class from Claim 7 [settled]:
  when compaction's summary model is missing/broken, the request still returns
  200 but forwards the *uncompacted* conversation — the exact input-token spend
  the edit was meant to prevent. This is fail-open on the cost/context-window
  dimension (the inverse of fail-open-on-security where a control is skipped):
  a compaction outage is invisible to a request-succeeds monitor and only shows
  in token/cost dashboards. Operators must alert on a non-empty
  `applied_edits[].error` (enum in Concrete Artifacts).
- **Chapter 05, "Session-affine routing …" / context-cost controls**: add the
  hard floors as operator-visible contracts: `compact_20260112` rejects
  `trigger.value < 50000` with HTTP 400 (Claim 8) [settled], and
  `clear_tool_uses_20250919` never clears the most recently completed
  `tool_result` (Claim 4) [settled] — an irreducible per-request token floor to
  size small-context backends around.
- **Chapter 02 (Observability), token accounting**: two additions. (1) The
  polyfill's threshold checks use `litellm.token_counter` with cl100k_base
  fallback for unknown models (Claim 12) [settled-mechanism] — trigger
  decisions on non-OpenAI models are made with a possibly non-native tokenizer,
  so "edit fired at N tokens" is not a provider-native count. (2) The
  `applied_edits` telemetry contract (Claim 11) [settled]: field present when an
  edit fires, **absent** when below threshold (absence ≠ error), and on
  streaming it arrives only in the final `message_delta` SSE event — an SSE
  consumer reading only content-block deltas never sees it. Also add the
  client-side-slice path (Claim 13) [settled] as an attributed-cause caveat:
  a pre-existing compaction block triggers slice-only forwarding with no
  response marker, so a cheap turn has no response-side attribution.
- **Chapter 03 (Runbooks and agents), Claude Code tool loops**: add the
  write-once/run-anywhere contract (Claim 2) [settled] plus its prerequisites
  for anyone pointing a Claude Code loop at non-Anthropic backends via a
  gateway: a `context_management_summary_model` in `general_settings` (Claim 5)
  [settled] with the silent-no-op failure if missing, a 50,000-token
  compaction floor (Claim 8) [settled], and the hard floor on tool-result
  clearance (Claim 4) [settled].
- **Chapter 06 (Security and Trust), context-window scale conditions**: the
  hard floors in Claims 4 and 8 bound the "grow context → wait for a model with
  a bigger window" strategy: no `keep` setting clears the most recent completed
  `tool_result` on the polyfill path, and compaction below 50k is refused, so a
  long tool loop has a documented minimum floor regardless of how low the
  operator sets the knobs.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/claude_code_context_management`, HTTP 200, no
  paywall). Single page; the only outbound links are nav siblings (#1444
  `claude_code_compatibility`, #1443 caching) and the next/prev tutorial pages,
  which the Prospector already scoped out — no sub-pages followed.
- The "How It Works" ASCII flow diagram is present on the page but its
  box-drawing characters were flattened by the fetch; its *content* (detect
  routing target → polyfill steps → forward without `context_management` key →
  attach `applied_edits` → optionally prepend compaction block) is captured in
  Claims 1, 6, and 11 and the artifacts above rather than reproduced as a
  garbled block.
- All `Quote` fields are verbatim contiguous fragments from the fetched page
  prose or table cells; quotes from knob tables are single cells; inner quotes
  are escaped as they render in the page. No splicing across non-adjacent
  sentences; interpreted consequences are in `Our assessment`, not in quotes.
- **Layer reconciliation performed, no contradiction filed** (MINER §4a when-NOT
  -to-file): the messages-to-responses mapping note (#1390) Claim 8 documents
  the `context_management` dict→array *wire conversion* on the
  `/v1/messages`→OpenAI/Azure path; this page documents *who applies the edits*
  at runtime (Responses API natively; LiteLLM polyfill for all others). Both
  hold simultaneously — one is the translation layer, the other the application
  layer. Verified the mapping note's worked example values against this page
  (`compact_20260112`, `trigger.value` 150000 default) and both notes agree on
  feature naming. Recorded under Extends so the Assayer/Smith see the explicit
  reconciliation the Prospector requested. Also checked the open
  contradiction issues (#1150, #1307, #1322, #1338, #1352, #1408) and
  `CONTRADICTIONS.md` (no `C-NNN` entries): none cover `context_management`.
- Cross-reference verification (MINER §4b): re-read the cited notes' claims —
  `docs-litellm-messages-to-responses-mapping.md` Claim 8 (conversion worked
  example), `blog-litellm-save-claude-code-costs.md` Claim 8 (composition) and
  Claim 3 (cache prefix), `docs-litellm-anthropic-unified.md` Claims 1 & 5,
  `docs-litellm-anthropic-count-tokens.md` Claim 7 (local tiktoken fallback),
  `blog-litellm-headroom-integration.md` Claim 8 (`cache_control` carve-out),
  `docs-litellm-caching-all-caches.md` (output/semantic cache scope) — and
  confirmed the numbered claims match their cited content. No claim numbers
  invented.
- `confidence_overall` set to `emerging`: the mechanical behaviors (knobs,
  defaults, floors, error enum, provider matrix) are settled first-party
  documentation, but the whole surface is vendor-documented with no independent
  validation, the knob behavior is explicitly labeled `(v0)`, one feature is
  "Coming soon" (will date), and the highest-value synthesis (fail-open cost
  degradation, silent-no-op, token-count accuracy) are the Miner's readings of
  documented mechanics. Consistent with the sibling LiteLLM docs notes
  (#1286, #1359, #1381, #1382, #1390).
- `date_published` unknown (undated living docs page); `date_extracted` and
  `last_checked` both 2026-09-24 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) — production-shaped drain; `miner-related-notes.md` read for candidates and left uncommitted.