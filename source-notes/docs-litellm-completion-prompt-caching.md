---
source_url: https://docs.litellm.ai/docs/completion/prompt_caching
source_type: docs
title: "Prompt Caching — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; footer "© 2026 LiteLLM")
date_extracted: 2026-10-02
last_checked: 2026-10-02
status: current
confidence_overall: settled
issue: "#1556"
---

# LiteLLM Prompt Caching Reference (provider-side cache markers, minimums, usage and cost surfaces)

> The canonical provider-prompt-caching reference for LiteLLM: the per-model minimum-token matrix below which caching is **silently skipped with no error returned**, the cross-provider translation contract (one Anthropic-style `cache_control` marker → Bedrock `cachePoint` / Gemini `cachedContents`), OpenAI's automatic-plus-`prompt_cache_key` model, GPT-5.6 explicit breakpoints gated on LiteLLM's cost map, and the exact usage fields (`prompt_tokens_details.cached_tokens`, Anthropic-only `cache_creation_input_tokens`) an operator must read to prove a cache engaged.

## Source Context

- **Type**: docs — LiteLLM configuration reference page (`/docs/completion/prompt_caching`), one page of the LiteLLM Python SDK / Proxy "Prompts & Context" tree on `docs.litellm.ai`, rendered by Docusaurus. No byline; footer "© 2026 LiteLLM".
- **Author credibility**: First-party vendor documentation for LiteLLM (BerriAI), a widely used open-source LLM gateway/SDK. Authoritative on **what the config surface is** (parameter names, enum values, per-model minimums, documented error behavior) and on what LiteLLM *translates* to each provider. **Not** authoritative on production outcomes: the page reports no hit-rate, no latency, no measured cost saving, and no break-even for cache writes. Where it describes a minimum, the minimum is a property of the *provider*, which LiteLLM merely mirrors.
- **Scope**: The provider-side prompt-caching tier only — markers, minimums, per-provider translation, usage-object shape, cost helpers, capability probing. Explicitly **out of scope**, and linked out: (a) the linked "Auto-Inject Prompt Caching Checkpoints" tutorial (`/docs/tutorials/prompt_caching`), which is proxy-side injection config and is partially covered by `blog-litellm-save-claude-code-costs.md` (#668); (b) LiteLLM's own response caches (`/docs/caching/all_caches` #1431, `/docs/caching/caching_api` #1432). The tutorial is a separate URL and is **not** mined here.
- **Corpus gap this fills**: `docs-litellm-caching-all-caches.md` (#1431) covers the *SDK response* cache and explicitly links provider prompt caching out to this page; `docs-litellm-bedrock-invoke.md` Claim 8 records that the Bedrock pages are silent on prompt caching. Until this note, the corpus documented provider prompt caching only by absence and by one failure report (`failure-litellm-bedrock-invoke-prompt-cache.md` #697).

## Extracted Claims

### Claim 1: Prompt caching is silently skipped below the provider's minimum input-token count and **no error is returned** — the request returns 200 with a correct completion and no cache

- **Evidence**: A dedicated "Minimum token requirements" paragraph at the very top of the page, before any provider example. The same sentence is repeated in the Anthropic and Bedrock per-model sections as a section-level note.
- **Confidence**: settled (documented, checkable behavior — verifiable by sending a sub-minimum prompt and inspecting the usage object)
- **Quote**: "Prompt caching is silently skipped when the input is below the provider's minimum, and **no error is returned**. Always verify caching occurred by checking `cache_creation_input_tokens` in the response."
- **Quote**: "Prompts below the minimum are processed without caching, and no error is returned. Check `cache_creation_input_tokens` in the response."
- **Our assessment**: This is the page's whole operational thesis and the corpus's sharpest new caching fact. A cache miss that is indistinguishable from a cache hit by status code: every request succeeds, every completion is correct, and the only symptoms are a `cache_creation_input_tokens` of 0 and a bill at full uncached input price. It slots directly under `failure-litellm-bedrock-invoke-prompt-cache.md` Claim 2 (a real LiteLLM cache regression whose "only signal was cache-read token counts, which nothing in our CI or monitoring measured") as the *second, cheaper* way the same blind spot is created — there the cache broke for a structural reason, here it never engaged because a prompt was 200 tokens short. Both argue the guide's rule should be: **never infer cache engagement from a 200; read a usage field.**

### Claim 2: The minimum is a **per-model-family** property, not a per-provider property, and the tiers run 512 / 1,024 / 2,048 / 4,096 tokens — an 8x spread between the cheapest and most expensive model on the same vendor

- **Evidence**: Three separate tables on the page — a cross-provider summary table at the top and per-model tables in the Anthropic and Bedrock sections. (Tables reproduced verbatim in Concrete Artifacts.)
- **Confidence**: settled (documented per-model enum; a living vendor table that will drift — treat the tier *structure* as durable and the numbers as point-in-time)
- **Quote**: "See [Anthropic's prompt caching docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) for the full list; these minimums apply on every platform where each model is available."
- **Our assessment**: Two things the guide should carry. First, **model choice is a caching decision**: routing a static prefix to Haiku 4.5 / Opus 4.5+ requires a 4,096-token prefix (4x the volume of Opus 5's 512) before any saving appears, so a team that sized its reusable prefix against a cheap model may see zero caching and conclude caching is broken. Second, the minimum is not a gateway policy an operator can tune — it is set by the provider and only mirrored by LiteLLM, so it cannot be raised by configuration. A cached-prefix budget is therefore a **model-dependent constant** that has to be re-derived whenever the route changes; a prefix sized for the cheapest tier is safe fleet-wide, one sized to the exact model is not.

### Claim 3: The page's own verification instruction is provider-mismatched — it tells every reader to verify via `cache_creation_input_tokens` while simultaneously documenting that field as `ANTHROPIC_ONLY`

- **Evidence**: The instruction in Claim 1's quote sits above a summary table whose rows include OpenAI, Bedrock and Google Gemini. The usage-object contract in the very next section labels `cache_creation_input_tokens` `# ANTHROPIC_ONLY`. The page never tells a non-Anthropic reader which field to check.
- **Confidence**: settled (both halves are on the same page, uncontradicted; the mismatch is our reading of their juxtaposition, not a stated admission)
- **Quote**: "`cached_tokens`: Tokens that were a cache-hit for that call."
- **Quote**: "**ANTHROPIC\_ONLY**: `cache_creation_input_tokens` are the number of tokens that were written to cache. (Anthropic charges for this)."
- **Our assessment**: A genuine documentation defect and the highest-value synthesis on this page. The only field that works across every supported provider is `prompt_tokens_details.cached_tokens` (nested inside the OpenAI-shaped `usage` object that LiteLLM normalizes to for all of them) — but the page's actionable instruction points at a field that, for OpenAI / Bedrock / Gemini traffic, is either absent or always 0. An operator who follows the instruction literally on a Gemini route concludes caching never works. The correct portable check, which the page never states in prose, is: **read `usage.prompt_tokens_details.cached_tokens` on every provider; on Anthropic-family routes additionally read `cache_creation_input_tokens` (the write) and know that its absence means "never written", not "not instrumented."** Filed here as a claim about the documentation, not as a verified LiteLLM bug — we did not execute requests against the proxy to confirm what non-Anthropic routes actually return.

### Claim 4: `prompt_tokens` is **not** net of cache — the page states it explicitly includes both cache-miss and cache-hit input tokens, so a naive `prompt_tokens × unit-price` spend calculation overstates cached traffic at full input price

- **Evidence**: The usage-object field glossary states the inclusion directly.
- **Confidence**: settled (documented field semantics)
- **Quote**: "`prompt_tokens`: These are all prompt tokens including cache-miss and cache-hit input tokens."
- **Quote**: "`total_tokens`: Sum of prompt_tokens + completion_tokens."
- **Our assessment**: The accounting hazard is direct and worth stating plainly: a cache hit does **not** reduce `prompt_tokens`, so any dashboard, budget guard, or per-request cost calculator that reads `prompt_tokens` and multiplies by the standard input price will bill cached tokens at the uncached rate — the opposite error from the `advisor` tool's under-reporting (`docs-litellm-anthropic-advisor-tool.md` Claim 2), and worth pairing with it as the two directions a `usage` object can mislead. This also means **`prompt_tokens` alone cannot be used to detect a cache miss**; the cached/miss split lives one level down in `prompt_tokens_details`. The corpus's only worked example uses 2,006 prompt tokens with 1,920 cached — i.e. ~96% of the prompt served from cache while the headline number barely moves.

### Claim 5: A third usage field, `cache_read_input_tokens`, appears **only inside a code comment** in the Bedrock example and is never defined in the usage-object contract

- **Evidence**: The Bedrock SDK example's trailing comment names it; the page's usage-object JSON and glossary do not contain it.
- **Confidence**: settled (the absence from the contract is directly checkable by reading both sections)
- **Quote**: "# cache_creation_input_tokens > 0 on first call (cache written)# cache_read_input_tokens > 0 on subsequent calls (cache hit)"
- **Our assessment**: Small but consequential for anyone writing a cache-hit alert: on Bedrock the page's own example tells you to read a field the page never defines, and tells you nothing about where it lives in the returned object. It is also the field `failure-litellm-bedrock-invoke-prompt-cache.md` measured its 90% → 25-45% hit-rate collapse against ("cache read (0.1x)" in that report's pricing ladder), so it is the corpus's load-bearing observability field on exactly the platform where it is least documented here. Record the three-field set as: `cached_tokens` (read/hit, all providers), `cache_read_input_tokens` (read/hit, Bedrock-family, undocumented on this page), `cache_creation_input_tokens` (write, Anthropic-only, billed).

### Claim 6: Bedrock requires **no code change** — LiteLLM translates the OpenAI-format `cache_control` marker to Bedrock's native `cachePoint`, and every listed model supports the same two TTL options (5 min, 1 hour), including cross-region inference profiles

- **Evidence**: The Bedrock section's opening sentence, plus the supported-models table with its `TTL Options` column (identical "5 min, 1 hour" on all ten rows).
- **Confidence**: settled (documented translation contract + a per-model table; no wire capture performed)
- **Quote**: "LiteLLM automatically translates OpenAI-format `cache_control` markers to Bedrock's native `cachePoint` format, so no changes are needed to your existing code if you're already using `cache_control`."
- **Quote**: "Cross-region inference profiles are also supported for the models above."
- **Our assessment**: The portability property is the useful part and it is the same property the Bedrock *incident* report was about the other side of: #697 showed a translation change silently breaking Bedrock's prefix cache. The distinction the guide must draw is that **marker translation and cache-contract preservation are different guarantees**. This page guarantees only the first — it says the marker becomes `cachePoint`; it says nothing about preserving prefix bytes. Given #697 Claim 1 (hoisting system entries invalidated every cache breakpoint), an operator should read "no changes needed to your existing code" as *narrower* than it sounds: it covers the marker, not the message array. Also note the TTL uniformity is a genuine cost lever the page does not discuss: 1-hour caches cost more to write than 5-minute ones on Anthropic, so the right TTL is a session-length question, and on Bedrock both are available with the same code.

### Claim 7: Gemini / Vertex is a structurally **different** mechanism — a two-hop `cachedContents` API call whose returned ID is then referenced in the request body — not an inline marker like Anthropic and Bedrock

- **Evidence**: A numbered "How it works under the hood" list, with the 1,024-token floor stated as item 4.
- **Confidence**: settled (documented mechanism, step by step)
- **Quote**: "1. Messages with `cache_control` are separated and sent to Google's `cachedContents` API" / "2. The cached content ID is then passed as `cachedContent` in the Gemini request body" / "3. Works across all three providers: `gemini/` (Google AI Studio), `vertex_ai/`, and `vertex_ai_beta/`" / "4. Requires a minimum of **1024 tokens** in the cached content. Below that, caching is silently skipped"
- **Our assessment**: This is a real operational difference the flat "one marker, many providers" framing hides. Anthropic and Bedrock cache inline in a single request; Gemini requires LiteLLM to **create a separate cache resource first and then reference it by ID**, which means cache *lifetime* is a resource lifecycle rather than a per-request annotation, and a cached prefix that exists is addressable as an object. The guide's portability claim should be stated at the right altitude: the *marker* is portable, the *mechanism* is not. Note also that item 4 is a third independent statement of the silent-skip rule (with the top table, and with the Anthropic/Bedrock section notes) — the page repeats the gotcha at every provider entry point, which is itself evidence the vendor considers it the failure operators actually hit.

### Claim 8: The Anthropic `cache_control` marker is portable and **silently ignored** elsewhere — but the page's "Supported Providers" list mixes providers that need a marker with providers that reject the concept and cache automatically

- **Evidence**: One sentence in the Anthropic section; the supported-provider bullet list at the top of the page.
- **Confidence**: settled for the quote; the "list conflates two mechanisms" half is our assessment
- **Quote**: "This same format also works for [Gemini / Vertex AI](#google-ai-studio--vertex-ai-gemini-example). For other providers, it will be ignored."
- **Our assessment**: "For other providers, it will be ignored" is the safe-by-default property worth having — a stray `cache_control` block cannot cause a provider-side rejection, so the marker is safe to leave in shared code. But the top-of-page **Supported Providers** list (`openai/`, `anthropic/`, `gemini/`, `vertex_ai/`, `vertex_ai_beta/`, `bedrock/`, `bedrock/invoke/`, `bedrock/converse`, `deepseek/`, `xai/`) conflates two different things: providers where LiteLLM **translates a marker** (Anthropic, Bedrock, Gemini, Vertex) and providers where caching happens **automatically with no marker at all** (OpenAI, DeepSeek, xAI — the DeepSeek section says only "Works the same as OpenAI." and xAI gets no example at all despite being listed). So the list answers "does this provider cache?" for both kinds while only documenting the mechanism for the first. The portable-marker rule for the guide: **write `cache_control` for Anthropic/Bedrock/Gemini/Vertex, omit it for OpenAI/DeepSeek/xAI, and do not read the provider list as a statement that markers work everywhere.**

### Claim 9: OpenAI caching needs **no annotation**; the two optional controls are a **backend-affinity hint** and a **TTL selector** — and `prompt_cache_key` is not a cache key

- **Evidence**: A dedicated subsection with bullet definitions for both parameters plus SDK and proxy code examples.
- **Confidence**: settled (documented parameter semantics)
- **Quote**: "OpenAI prompt caching is [**automatic**](https://platform.openai.com/docs/guides/prompt-caching); no `cache_control` message annotations are needed. Any request with 1024+ prompt tokens is eligible for caching."
- **Quote**: "**`prompt_cache_key`** (string): a routing hint that improves cache hit rates for requests sharing long common prefixes. Requests with the same cache key are routed to the same backend, increasing the likelihood of a cache hit."
- **Quote**: "**`prompt_cache_retention`** (`\"in_memory\"` or `\"24h\"`): controls cache TTL. Default is `\"in_memory\"` (5–10 min). Set to `\"24h\"` for extended caching that offloads KV tensors to GPU-local storage."
- **Our assessment**: The name is a trap worth flagging explicitly: **`prompt_cache_key` is a routing-affinity hint, not a cache key.** It does not select or namespace cache entries; it steers requests with the same value to the same backend so a warm prefix is reachable. That is the same class of concern as the cross-replica cache notes in `docs-litellm-caching-all-caches.md` Claim 1 (a per-process cache shares no hits across replicas) — for provider prompt caching the fix is upstream affinity rather than a shared store, which is why the parameter exists. The second point: the OpenAI threshold is stated as an **eligibility** condition ("eligible for caching") while Anthropic/Bedrock/Gemini minimums are stated as a hard skip. Those are different failure semantics for the same 1,024-token number — OpenAI can decline to cache an eligible request (and says so only via `cached_tokens == 0`), so the Claim 1 verification rule is the only portable check here too, and "we're over the minimum" is *not* a sufficient condition on any provider.

### Claim 10: GPT-5.6+ explicit breakpoints are a **two-part** surface (per-block `prompt_cache_breakpoint` + request-level `prompt_cache_options{mode, ttl}`) whose support is resolved from LiteLLM's cost map — with a **model-name-version fallback** when the map has not flagged the model

- **Evidence**: A dedicated subsection with SDK and proxy examples, and an explicit sentence naming the capability flag and the fallback.
- **Confidence**: settled (documented parameter surface and documented resolution order)
- **Quote**: "GPT-5.6 and newer also accept [explicit cache breakpoints](https://developers.openai.com/api/docs/guides/prompt-caching#prompt-cache-breakpoints): a `prompt_cache_breakpoint` marker on a content block plus a request-level `prompt_cache_options` that picks the mode (`implicit` keeps OpenAI's automatic breakpoint on the latest message alongside yours, `explicit` uses only yours) and the cache `ttl` (`30m`). LiteLLM passes both through on `/chat/completions`, `/responses` and, for Anthropic-shaped clients, `/v1/messages`. Models that accept the marker carry `supports_prompt_cache_breakpoint: true` in the cost map, and a GPT-5.6 or newer OpenAI model name the map has not flagged yet is treated the same way."
- **Our assessment**: Three separable points, and the third is the one that generalizes. (a) Breakpoints are **explicit and two-part** — a marker alone does nothing without `prompt_cache_options` at the request root, and the two endpoints' shapes differ (`print(response.usage.prompt_tokens_details)` on `/chat/completions` vs `print(response.usage.input_tokens_details)` on `/responses`). (b) The same capability crosses three endpoints, `/responses` included, so a Claude Code-shaped client on `/v1/messages` and an OpenAI-native client on `/responses` share one caching model — a genuine parity claim worth carrying. (c) **The fallback is the interesting part.** LiteLLM prefers its maintained cost map, and when the map lacks an entry it decides capability by substring-matching the model name's version. That is a deliberate, documented, *silent* capability inference from a string — the same mechanism `failure-litellm-bedrock-invoke-prompt-cache.md` Claim 7 identifies as the trap that broke Claude Code on Bedrock Invoke (an alias with no version substring is assumed to have the newest feature set). LiteLLM applies that inference to itself: for a not-yet-mapped GPT-5.6-or-newer name it *assumes support* rather than refusing, so an unflagged model silently gains a marker; and the mirror-image risk is a model name carrying a version substring that the flag would have excluded. See Cross-References for why this is recorded as Extends rather than filed as a contradiction.

### Claim 11: Capability probing answers from LiteLLM's **maintained cost map**, not from the provider — so `supports_prompt_caching() == False` means "not in our map" as much as "not supported"

- **Evidence**: A "Check Model Support" section with an SDK helper call, a `/model/info` curl, and a named expected-response field.
- **Confidence**: settled (documented lookup target); the "means not-in-our-map too" reading is our assessment, not a stated admission
- **Quote**: "Check if a model supports prompt caching with `supports_prompt_caching()`"
- **Quote**: "This checks our maintained [model info/cost map](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json)"
- **Quote**: "\"supports_prompt_caching\": true # 👈 LOOK FOR THIS!"
- **Our assessment**: A pre-flight check that answers the wrong question for the operator's actual problem. `supports_prompt_caching()` is a statement about **LiteLLM's map**, so a `False` is ambiguous between "the provider cannot cache this" and "we have not added this model yet" — and LiteLLM's own corpus contains a postmortem for exactly that second case (`failure-litellm-model-cost-map-silent-fallback.md`, where a malformed cost map made lookups fall back to a packaged snapshot with no warning, so cost tracking silently reported zero for newer models). The usable discipline: `supports_prompt_caching()` is a **necessary but not sufficient** gate; the sufficient check is a real two-request round trip asserting `usage.prompt_tokens_details.cached_tokens > 0`, which is exactly what every Quick Start example on this page does — note that all of them loop twice (`for _ in range(2):`) precisely because the first call can only ever write, never read. Two minor interface asymmetries worth knowing: the SDK example probes with a fully-qualified provider string (`model="anthropic/claude-sonnet-5"`) while the proxy example probes by `model_name` alias, and the two return different shapes (`bool` vs a flag nested under `model_info`).

### Claim 12: Cost attribution runs through `completion_cost()` and the `x-litellm-response-cost` response header — but both are map-derived estimates, so the provider invoice remains the only ground truth

- **Evidence**: A "Calculate Cost" section with the helper call, a link to LiteLLM's Anthropic cost-calculation module, and a proxy snippet reading the header.
- **Confidence**: settled (documented API surface); the "estimate vs invoice" framing is our assessment, corroborated by `docs-litellm-token-usage-helpers.md` Claim 4
- **Quote**: "Cost cache-hit prompt tokens can differ from cache-miss prompt tokens."
- **Quote**: "Use the `completion_cost()` function for calculating cost ([handles prompt caching cost calculation](https://github.com/BerriAI/litellm/blob/f7ce1173f3315cc6cae06cf9bcf12e54a2a19705/litellm/llms/anthropic/cost_calculation.py#L12) as well)."
- **Quote**: "LiteLLM returns the calculated cost in the response headers - `x-litellm-response-cost`"
- **Our assessment**: The documentation is careful to say "calculating cost", not "billing cost", and the distinction is the operationally important one. `docs-litellm-token-usage-helpers.md` Claim 4 (verified) documents `completion_cost` as composing `token_counter` and `cost_per_token` — i.e. **re-tokenizing locally and pricing from the bundled map** rather than reading provider-reported usage — so the cache-aware behavior this page points at lives in LiteLLM's code, keyed on map entries, not on the invoice. The rule for the guide: **`x-litellm-response-cost` is an estimate whose fidelity is bounded by the model cost map; alert on spend, but reconcile against the provider bill.** That is precisely how #697 was detected — cache-read token counts and the bill were the only signals that moved, while every request stayed a 200. Note also that `x-litellm-response-cost` is a *response header*, so it exists on the streaming path too, whereas `docs-litellm-streaming-token-usage.md` Claim 1 records that streamed `usage` is opt-in via `stream_options={"include_usage": True}` — a deployment that reads usage off streamed responses without that flag has neither the cached-token count nor the per-request header to fall back on.

## Concrete Artifacts

### Cross-provider minimum-token summary table (top of page)

| Provider | Minimum input tokens |
| --- | --- |
| OpenAI | 1,024 |
| Anthropic (Claude Opus 5, Fable 5, Mythos 5) | 512 |
| Anthropic (Claude Sonnet 5, Opus 4.8, Sonnet 4.x, Opus 4, 4.1, Claude 3.x) | 1,024 |
| Anthropic (Claude Haiku 4.5, Opus 4.5, 4.6) | 4,096 |
| Bedrock (Claude Opus 5) | 512 |
| Bedrock (Claude Sonnet 5, Opus 4.8, Sonnet 4.x, Claude 3.5, 3.7) | 1,024 |
| Bedrock (Claude Haiku 4.5, Opus 4.5, 4.6, 4.7) | 4,096 |
| Google Gemini | 1,024 |

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Minimum token requirements" section. **Note the divergence from the per-model tables below: Opus 4.7 and Claude 3.5 Haiku (both 2,048 in the Anthropic table) do not appear in this summary at all, and Opus 4.7 is listed here at 4,096 under Bedrock. Filed as contradiction #1562.**

### Usage object contract (page reproduces OpenAI's shape for all supported providers)

```json
"usage": {
  "prompt_tokens": 2006,
  "completion_tokens": 300,
  "total_tokens": 2306,
  "prompt_tokens_details": {
    "cached_tokens": 1920
  },
  "completion_tokens_details": {
    "reasoning_tokens": 0
  }
  # ANTHROPIC_ONLY
  "cache_creation_input_tokens": 0
}
```

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Minimum token requirements" section. Indentation restored from the page's rendered output; token values, field names, and the `# ANTHROPIC_ONLY` comment marker are verbatim. The page's worked example is ~96% cache-served (1,920 of 2,006 prompt tokens) while `prompt_tokens` barely moves — see Claim 4.

### Minimum tokens (Anthropic) — per-model table

| Model | Min tokens |
| --- | --- |
| Claude Opus 5, Fable 5, Mythos 5 | 512 |
| Claude Sonnet 5, Opus 4.8 | 1,024 |
| Claude Opus 4.7 | 2,048 |
| Claude Haiku 4.5, Opus 4.5, Opus 4.6 | 4,096 |
| Claude Sonnet 4, Sonnet 4.5, Sonnet 4.6, Opus 4, Opus 4.1 | 1,024 |
| Claude 3.5 Haiku | 2,048 |
| Claude 3.x Haiku, Sonnet, Opus, 3.5 Sonnet, 3.7 Sonnet | 1,024 |

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Minimum tokens (Anthropic)" table.

### Minimum tokens (Bedrock) — per-model table

| Model family | Min tokens per request |
| --- | --- |
| Claude Opus 5 | 512 |
| Claude Sonnet 5, Opus 4.8 | 1,024 |
| Claude Haiku 4.5, Opus 4.5, Opus 4.6, Opus 4.7 | 4,096 |
| Claude Sonnet 4.5, 4.6 | 1,024 |
| Claude 3.5 Sonnet v2, Claude 3.7 Sonnet | 1,024 |

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Minimum tokens (Bedrock)" table. **Opus 4.7 is 4,096 here and 2,048 in the Anthropic table above — contradiction #1562.**

### Supported Bedrock models (Model ID / minimum / TTL options)

| Model | Bedrock Model ID | Min Tokens | TTL Options |
| --- | --- | --- | --- |
| Claude Opus 5 | `anthropic.claude-opus-5` | 512 | 5 min, 1 hour |
| Claude Sonnet 5 | `anthropic.claude-sonnet-5` | 1,024 | 5 min, 1 hour |
| Claude Opus 4.8 | `anthropic.claude-opus-4-8` | 1,024 | 5 min, 1 hour |
| Claude 3.5 Sonnet v2 | `anthropic.claude-3-5-sonnet-20241022-v2:0` | 1,024 | 5 min, 1 hour |
| Claude 3.7 Sonnet | `anthropic.claude-3-7-sonnet-20250219-v1:0` | 1,024 | 5 min, 1 hour |
| Claude Opus 4 | `anthropic.claude-opus-4-20250514-v1:0` | 1,024 | 5 min, 1 hour |
| Claude Sonnet 4.5, 4.6 | `us.anthropic.claude-sonnet-4-5-*`, `us.anthropic.claude-sonnet-4-6-*` | 1,024 | 5 min, 1 hour |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-*` | 4,096 | 5 min, 1 hour |
| Claude Opus 4.5, 4.6, 4.7 | `us.anthropic.claude-opus-4-5-*`, `us.anthropic.claude-opus-4-6-*`, `us.anthropic.claude-opus-4-7-*` | 4,096 | 5 min, 1 hour |

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Supported Bedrock models" table. Every row offers the same two TTL options, and the cross-region inference-profile `us.anthropic.*` IDs are listed alongside the bare IDs.

### Gemini / Vertex internals (the only numbered mechanism description on the page)

```
1. Messages with `cache_control` are separated and sent to Google's `cachedContents` API
2. The cached content ID is then passed as `cachedContent` in the Gemini request body
3. Works across all three providers: `gemini/` (Google AI Studio), `vertex_ai/`, and `vertex_ai_beta/`
4. Requires a minimum of **1024 tokens** in the cached content. Below that, caching is silently skipped
```

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Google AI Studio / Vertex AI (Gemini) Example" → "How it works under the hood".

### Bedrock read/write field names (from the SDK example's trailing comment)

```python
print(response.usage)
# cache_creation_input_tokens > 0 on first call (cache written)
# cache_read_input_tokens > 0 on subsequent calls (cache hit)
```

Source: https://docs.litellm.ai/docs/completion/prompt_caching — Bedrock Example, SDK tab. The two comment lines are adjacent in the source and quoted contiguously; they are the page's only mention of `cache_read_input_tokens`.

### Capability probe — SDK helper and proxy `/model/info` expected response

```python
from litellm.utils import supports_prompt_caching
supports_pc: bool = supports_prompt_caching(model="anthropic/claude-sonnet-5")
assert supports_pc
```

```json
{
    "data": [
        {
            "model_name": "claude-sonnet-5",
            "litellm_params": {
                "model": "anthropic/claude-sonnet-5"
            },
            "model_info": {
                "key": "claude-sonnet-5",
                ...
                "supports_prompt_caching": true # 👈 LOOK FOR THIS!
            }
        }
    ]
}
```

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Check Model Support" section. Line breaks and indentation restored from the page's rendered output; identifiers, values, the `...` elision, and the `# 👈 LOOK FOR THIS!` comment are verbatim. The page states immediately after: "This checks our maintained [model info/cost map](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json)".

### Per-response cost header (proxy)

```python
response = client.chat.completions.with_raw_response.create(...)
print(response.headers.get('x-litellm-response-cost'))
completion = response.parse()  # get the object that `chat.completions.create()` would have returned
```

Source: https://docs.litellm.ai/docs/completion/prompt_caching — "Calculate Cost" → "Usage". `with_raw_response` is required to reach headers on the OpenAI SDK path; the header is not on the parsed completion object.

## Cross-References

- **Corroborates**:
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 2** ("Every response was a 200 with a correct completion. The only signal was cache-read token counts, which nothing in our CI or monitoring measured"). This page documents the *design-time* half of the same blind spot: below the minimum, caching never engages and the response is still a 200. The incident is the structural case, this is the threshold case, and both are caught by the same usage field. (Verified: #697 Claim 2.)
  - `source-notes/docs-litellm-caching-all-caches.md` **Claim 2** (`supported_call_types` is an allow-list, and call types outside it are never cached). Two different layers, one identical failure mode — a LiteLLM-owned gate that silently declines to cache — which is why the response cache and the prompt cache should never be conflated but should share the guide's "verify, don't infer" rule. (Verified: #1431 Claim 2.)
  - `source-notes/docs-litellm-caching-all-caches.md` **Claim 6** (`kwarg["cache_hit"]` is the response cache's per-request hit signal). This page supplies the missing counterpart for the provider tier: `usage.prompt_tokens_details.cached_tokens`. An operator now has a named field per tier, and the guide's Ch02 hook should name both. (Verified: #1431 Claim 6.)
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claim 4** (`completion_cost` composes `token_counter` and `cost_per_token`, re-tokenizing locally and pricing from the map rather than reading provider-reported usage). This page points at `completion_cost()` as the cost path for cache-aware pricing; that note documents what it is actually built on, which is why Claim 12 treats `x-litellm-response-cost` as a map-derived estimate. Consistent, and jointly load-bearing. (Verified: #1300 Claim 4.)
  - `source-notes/docs-litellm-anthropic-advisor-tool.md` **Claim 2** (top-level `usage` reflects executor tokens only; the expensive half of the call hides in `usage.iterations[]`). Same class, opposite direction: there the headline token counts *under*-report spend, here they *over*-report it (Claim 4, `prompt_tokens` includes cache-hit tokens at full price). Together they make the general rule "a `usage` object is not a spend statement; know which field carries the expensive path." (Verified: #1456 Claim 2.)
  - `source-notes/docs-litellm-streaming-token-usage.md` **Claim 1** (a streamed completion reports no usage unless the caller passes `stream_options={"include_usage": True}`). Read with Claim 12: on the streaming path, skipping that flag removes both the cached-token count and the usage object, leaving `x-litellm-response-cost` as the only cache-related signal. (Verified: #1286 Claim 1.)
  - `source-notes/docs-litellm-completion-input-params.md` **Claim 3** ("LiteLLM assumes any non-openai param is provider specific and passes it in as a kwarg in the request body"). This explains *how* the OpenAI-only controls reach a non-Openai provider here: `prompt_cache_key`, `prompt_cache_retention` and `prompt_cache_options` are not OpenAI chat-completions params, so they ride the undocumented pass-through rather than the support matrix — which is also why the page's proxy examples wrap them in `extra_body={...}` instead of passing them as top-level client kwargs. (Verified: #1495 Claim 3.)

- **Extends**:
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — **Extracted Lessons → Lesson 2** (silent fallback to stale local data is worse than failing loudly; a fallback must log a warning) and **Lesson 3** (non-request-path functions that fail silently erode observability; add separate health probes). This page extends that failure class to capability resolution: `supports_prompt_caching()` and the GPT-5.6 breakpoint decision both read the same maintained cost map, and the breakpoint path documents a **silent** fallback to model-name substring matching with no warning and no log line. The cost-map postmortem's remedy (never fall back silently; probe out-of-band functions) applies verbatim. Cited by lesson heading because these are lesson sections, not numbered claims (MINER.md §4b rule 4). (Verified by reading Lessons 2 and 3; note #632.)
  - `source-notes/docs-litellm-bedrock-invoke.md` **Claim 8** (the Bedrock passthrough pages are silent on prompt caching, so an operator cannot tell from them whether the route is cache-safe). This page closes part of that recorded gap: it documents Bedrock's marker translation, minimums and TTLs. It does **not** close the rest — it says nothing about whether the passthrough preserves the cached prefix, which is the actual question Claim 8 raised. The guide should now say "documented thresholds exist, cache-contract preservation is still undocumented." (Verified: #1417 Claim 8.)
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 1** (a gateway translation change that keeps payloads semantically equivalent can still silently destroy a provider's prefix cache) and **Claim 4** (Anthropic prompt caching is prefix-based, so each newly written mid-conversation system message invalidated the cache). This page supplies the *mechanism* that incident lacked — where to place the marker so the prefix is stable — and its per-provider minimums are the sizing constraint that makes a prefix cacheable at all. Together: the incident explains how caches break, this page explains how to build one that holds. (Verified: #697 Claims 1 and 4.)
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 7** (alias-based capability detection is a version-gating trap: an alias with no version substring makes the client assume the newest feature set). Claim 10 is LiteLLM applying exactly that inference to itself — when its cost map lacks an entry, it decides a model's breakpoint support from the model name's version string. Recorded as Extends rather than a contradiction because it is *conditional*, not opposing: LiteLLM prefers the maintained map (the correct design) and only falls back to string inference for models the map has not flagged. The guide's rule is the resolution — version metadata must be explicit, and where a layer falls back to name substrings, treat it as an unverified guess. (Verified: #697 Claim 7.)
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 3** (LiteLLM auto-injects `cache_control` markers at configurable injection points, enabling Claude's prompt cache without client-side changes; and prompt cache hits cost roughly 10% of a fresh input token). This page is the manual counterpart — it documents the marker, minimums and usage fields that the auto-injection produces, which is the only way to tell whether an injected checkpoint actually engaged. Per the Prospector triage I did **not** re-derive the injection mechanism (that is #668's territory); this note stops at the provider-side surface and links the tutorial out. (Verified: #668 Claim 3.)
  - `source-notes/docs-litellm-caching-hosted-cache.md` **Claim 4** (the hosted tier documents no TTL, no eviction behavior, no observability, and no retention statement). Provider prompt caching has the mirror-image documentation shape — a rich config surface, but also no documented cache-lifecycle contract for Anthropic: TTL options appear only in the Bedrock table, and the page never states how to select a 5-minute vs 1-hour Anthropic cache. Both tiers are configurable-but-unlifecycle-documented, which is worth one guide paragraph rather than two. (Verified: #1432 Claim 4.)
  - `source-notes/blog-litellm-claude-opus-4-8-day-0.md` **Claim 3** (Opus 4.8 prompt caching priced at $0.50/MTok read and $6.25/MTok write). The only per-model caching price in the corpus; consistent with this page's statement that Anthropic charges for cache writes, and it establishes the write-premium that makes `prompt_cache_retention="24h"` and Bedrock's 1-hour TTL genuine cost decisions rather than free upgrades. (Verified: #288 Claim 3.)

- **Contradicts**: Filed as **#1562** (`[contradiction] LiteLLM prompt-caching minimums: Claude Opus 4.7 = 2,048 ... vs 4,096`), labels `contradiction` / `needs-resolution` / `no-triage`. This is a **source-internal** contradiction: the page's "Minimum tokens (Anthropic)" table lists **Claude Opus 4.7 → 2,048** and is followed by the sentence "these minimums apply on every platform where each model is available," while both Bedrock tables on the same page list **Opus 4.7 → 4,096**. The page's own portability sentence rules out the "different platform, different minimum" reconciliation, and the stakes are the silent-skip behavior it warns about three times on the same page. Secondary gap recorded in the same issue: the top-of-page summary table omits Opus 4.7 and Claude 3.5 Haiku entirely (it collapses Anthropic into 512 / 1,024 / 4,096). **No verdict is picked here** — the Miner cannot resolve it from this page, and the issue asks a resolver to check the two upstream tables the page defers to. No other contradiction found: `CONTRADICTIONS.md` has no open `C-NNN` entries (only the unfilled template heading) and no existing corpus note asserts a prompt-cache minimum, a translation behavior, or a cost-accounting mechanism that this page opposes.

- **Novel** (new to the corpus):
  - **The silent-skip-below-minimum rule with an explicit "no error is returned"** — the corpus previously had only the *structural* silent cache regression (#697), never the threshold case (Claim 1).
  - **The full per-model minimum matrix** (512 / 1,024 / 2,048 / 4,096 across OpenAI, Anthropic, Bedrock, Gemini) — nothing in the corpus stated any prompt-cache minimum at all (Claims 2, plus #1562 for the Opus 4.7 divergence).
  - **The portable-marker contract**: one `cache_control: {"type": "ephemeral"}` marker translated to Bedrock `cachePoint` and to Gemini's two-hop `cachedContents` → `cachedContent` resource, with the Anthropic table the reference and unmatched providers silently ignoring the marker (Claims 6, 7, 8). The corpus had the marker *syntax* piecemeal but never the translation contract.
  - **The three cache usage fields and their provider scoping** — `cached_tokens` (all providers), `cache_creation_input_tokens` (Anthropic-only, billed writes), `cache_read_input_tokens` (Bedrock, undocumented on the page) — plus the fact that `prompt_tokens` includes cache-hit tokens and so is not net of cache (Claims 3, 4, 5).
  - **`prompt_cache_key` as a backend-affinity hint rather than a cache key, and `prompt_cache_retention` (`in_memory` 5–10 min vs `24h`) as a TTL selector** — neither parameter appears anywhere in the corpus (Claim 9).
  - **GPT-5.6 explicit breakpoints as a two-part surface resolved from the cost map with a model-name fallback** (Claim 10) — no corpus coverage of `prompt_cache_breakpoint` / `prompt_cache_options`, nor of capability resolution falling back to string matching.
  - **Capability probing via `supports_prompt_caching()` and `/model/info`'s `model_info.supports_prompt_caching`, explicitly documented as reading the maintained cost map** — the corpus had no pre-flight capability check for prompt caching (Claim 11).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — new subsection: "Provider prompt caching")**: The guide has no prompt-caching content today; `docs-litellm-caching-all-caches.md` covers only the SDK response cache. Add a provider-prompt-caching subsection carrying five specific rules: (1) **caching is silently skipped below a per-model minimum with no error returned** — quote the minimums matrix and state the tier *structure* (512 / 1,024 / 2,048 / 4,096) as the durable fact, with the numbers flagged as a living vendor table; (2) **model choice is a caching decision** — a 4,096-token prefix requirement on Haiku 4.5 / Opus 4.5+ versus 512 on Opus 5 means a prefix sized for the cheap tier is the only fleet-safe choice, and route changes require re-deriving it; (3) **the portable marker** — write `cache_control: {"type": "ephemeral"}` for Anthropic/Bedrock/Gemini/Vertex and omit it for OpenAI/DeepSeek/xAI (which cache automatically), with the "ignored by other providers" safety property; (4) **verify with a usage field, never with a 200** — `usage.prompt_tokens_details.cached_tokens > 0`, asserting on a *second* request because the first can only write (every page example loops twice); (5) **marker translation ≠ cache-contract preservation** — carry #697 alongside this page rather than letting "no changes needed to your existing code" read as a cache-safety guarantee.
- **Chapter 05 (same subsection — cost)**: Record that Anthropic **bills cache writes** (`cache_creation_input_tokens`) and that `prompt_tokens` **includes** cache-hit tokens, so a naive `prompt_tokens × unit-price` calculation bills cached tokens at the uncached rate. State that `prompt_cache_retention="24h"` and Bedrock's 1-hour TTL are paid upgrades whose break-even depends on session length — and note that this page gives **no measured break-even**, so any figure the guide uses must be attributed, not synthesized. Do not carry a bare "prompt caching saves X%" number from this source; it publishes none.
- **Chapter 02 (Observability)**: Give the cache-hit signal a named accessor per tier — `kwarg["cache_hit"]` for LiteLLM's response cache (`docs-litellm-caching-all-caches.md` Claim 6) and `usage.prompt_tokens_details.cached_tokens` for provider prompt caching — and state the rule that a `200` proves nothing about cache engagement. Add the accounting-direction warning: a `usage` object can both under-report spend (`usage.iterations[]`, advisor tool) and over-report it (`prompt_tokens` including cache hits), so dashboards must read the cached-token detail rather than headline counts. Flag the streaming gap: without `stream_options={"include_usage": True}`, streamed responses carry neither the cached-token count nor a usage object, leaving `x-litellm-response-cost` as the only cache-related signal. Set the alert on **hit rate and spend**, reconciled against the provider bill, because `x-litellm-response-cost` is a map-derived estimate.
- **Chapter 05 (capability probing / pre-flight)**: Add the pre-flight rule with its caveat — `supports_prompt_caching()` and `/model/info`'s `model_info.supports_prompt_caching` answer from LiteLLM's maintained cost map, so a `False` is ambiguous between "unsupported" and "not yet added", and a `True` is necessary but not sufficient. Require a two-request round trip asserting the cached-token field as the gating check. Pair with the general rule from `failure-litellm-model-cost-map-silent-fallback.md` Lesson 2: a capability lookup that falls back must not do so silently — which is exactly the untested behavior of the GPT-5.6 model-name fallback in Claim 10.
- **Chapter 06 (Security and Trust — prefix sharing)**: Flag as a *review question*, not a recommendation: this page documents that the cache marker is `cache_control` and says nothing about **whose** cache a hit shares or whether a cached prefix is isolated per tenant. The corpus's only statement on provider-cache sharing is the tutorial page this note does not mine (`/docs/tutorials/prompt_caching` → "Who the cache is shared with"), so the guide must not assert either isolation or non-isolation for provider prompt caching on this source. The tenant-isolation rule the guide *can* state today remains the response-cache one from `docs-litellm-caching-all-caches.md` Claim 5 (cache keys must include tenant scope explicitly).
- **Chapter 01 or 05 (contradiction surfaced to the Smith)**: **#1562 is unresolved** — Opus 4.7's minimum is documented as 2,048 on the Anthropic path and 4,096 on Bedrock, on the same page, with a portability sentence that rules out the reconciliation. Until a resolver settles it against the two upstream tables, the guide must **not** state a single Opus 4.7 minimum. If Ch05 is written before resolution, use the `**Debated:**` block pattern from `agents/SMITH.md` §5.

## Extraction Notes

- Source read in full via direct HTTP fetch of the rendered Docusaurus page (single self-contained page, no paywall, no truncation, no login). One linked sub-page followed per MINER.md §1: `/docs/tutorials/prompt_caching` ("Auto-Inject Prompt Caching Checkpoints"), read to confirm what #668 covers and to avoid re-deriving it. It **is** a distinct URL and **is not mined here** — per the Prospector triage, the proxy-side `cache_control_injection_points` mechanism belongs to `blog-litellm-save-claude-code-costs.md` (#668). Two observations from that read, recorded so they are not lost: (a) the tutorial states provider prompt caching is shared against **upstream credentials**, not against the LiteLLM key/team/end user, and bounds the leakage to "whether a prompt the caller already holds was sent" — that is directly relevant to the Ch06 prefix-sharing question and is *not* on this page; (b) it documents an Anthropic TTL knob (`anthropic_prompt_caching_ttl`, 5m vs 1h) that this page does not. If the Smith wants either, it needs its own source note / issue — I did not file one because this Miner run is scoped to #1556.
- Other outbound links (`platform.openai.com` prompt-caching guide, `ai.google.dev/api/caching`, the cost-calculation module on GitHub, `docs/completion/token_usage`) were cited as identifiers, not read; the upstream Anthropic and AWS minimum tables are precisely what contradiction **#1562** needs and are deliberately left to a resolver.
- Every `Quote` field is copied character-for-character from the rendered page text, including its punctuation and bold markers. Per MINER.md §2a I did **not** reconstruct anything into a quote. Where the meaning I wanted was synthesis across multiple sentences (Claims 1-vs-3 field mismatch, Claim 4's over-reporting consequence, Claim 8's provider-list conflation, Claim 11's "not-in-our-map too"), it is in `Our assessment`, not in a quote.
- Code/JSON blocks: the HTTP fetch flattened the page's line breaks inside several code blocks. For the five blocks reproduced above I **restored line breaks and indentation** and labeled each block's provenance line accordingly; identifiers, values, comments, and elisions are verbatim, but the whitespace is mine and should not be treated as character-exact. The two `# cache_creation_input_tokens ... / # cache_read_input_tokens ...` lines in the Bedrock artifact are quoted **contiguously** from adjacent source lines, not spliced. The long Quick Start SDK/proxy examples (the `for _ in range(2):` legal-agreement loops, the OpenAI and DeepSeek examples) are **not** reproduced: the fetch collapsed them into single unbroken lines, and reconstructing them would have been fabrication. Their behavior is described in Claims 9 and 11 where load-bearing.
- Confidence assignment: `confidence_overall: settled` for the note, against the triage's "settled on documented API surface / emerging on production impact" guidance. Justification for `settled` rather than `emerging`: the entire note is documented API/config surface — parameter names, enum values, per-model minimums, documented error behavior, translation contract, usage-field semantics — all first-party and all checkable against the open-source code or by sending a request. This page publishes **no** hit-rate, latency, or cost figures, so every claim here is a config/behaviour claim and none asserts a production outcome; the operational *consequences* in `Our assessment` are labelled as our reading rather than promoted to claims. This is the same rationale `docs-litellm-bedrock-invoke.md` uses for its config-surface claims and is deliberately different from `docs-litellm-caching-all-caches.md`'s `emerging`, which carries operational inferences the docs do not state.
- Claim 3 (the provider-mismatched verification instruction) and Claim 11 ("not in our map too") are the two claims I am most confident are *correct readings* but which are **not** stated by the source. Both are framed as documentation findings with the quoted text adjacent, and I did **not** run requests against a LiteLLM proxy to confirm what non-Anthropic routes actually return in `cache_creation_input_tokens`, nor what `supports_prompt_caching()` returns for an unmapped model. If the Assayer wants these at `emerging` or dropped, they are the two to revisit.
- Contradiction **#1562** was filed *before* this PR, per MINER.md §4a, and is referenced under `**Contradicts:**` with no verdict stated. It is a source-internal disagreement (same page, same model, same quantity) rather than a new-source-vs-existing-note conflict; MINER.md §4a covers that case under "a source disagrees with itself". I checked `CONTRADICTIONS.md` first — it contains only the unfilled `## C-NNN: Short title` template heading and no open entries — and I searched open `contradiction`-labeled issues to avoid duplicating an existing filing. The related tension with `failure-litellm-bedrock-invoke-prompt-cache.md` Claim 7 (LiteLLM's own cost-map model-name fallback) was deliberately **not** filed: it is a conditional difference (flagged vs unflagged models), which MINER.md §4a lists under "when NOT to file", and it is recorded under Extends with the guide rule instead.
- **Candidate handling** (`miner-related-notes.md` read before Cross-References; each of the ten pre-computed candidates cited or dismissed by name):
  - `docs-litellm-batches-api.md` — batch rate limiting and `batch_enqueued_token_limit`; different subsystem, no prompt-caching surface. **Dismissed.**
  - `docs-litellm-bedrock-invoke.md` — **Cited** (Extends, Claim 8). Its recorded prompt-caching documentation gap is what this page partially fills.
  - `docs-litellm-anthropic-advisor-tool.md` — **Cited** (Corroborates, Claim 2) for the `usage`-object accounting-direction pairing.
  - `docs-litellm-completion-input-params.md` — **Cited** (Corroborates, Claim 3); the non-OpenAI-param kwarg pass-through is how the OpenAI-only cache controls reach other providers.
  - `docs-litellm-audio-transcription.md` — transcription fallbacks and `mock_testing_fallbacks`; no caching surface. **Dismissed.**
  - `blog-litellm-auto-router-v2.md` — complexity/semantic/adaptive routing; a distinct feature with no prompt-cache surface. **Dismissed.** (Its "predictable beats clever for debuggability" rationale is thematically adjacent but not evidence for any claim here.)
  - `docs-litellm-completion-message-trimming.md` — client-side `trim_messages()` pre-call helper; adjacent context-management surface, no caching. **Dismissed.**
  - `blog-litellm-save-claude-code-costs.md` — **Cited** (Extends, Claim 3), with its injection mechanism deliberately not re-derived per the triage.
  - `blog-litellm-valkey-semantic-caching.md` — semantic (similarity) response caching via Valkey; a different layer and a different cache. **Dismissed** as a citation; its per-request scope isolation remains the corpus's only response-cache tenant-isolation claim and is referenced from Ch06 above.
  - `docs-litellm-a2a-iteration-budgets.md` — A2A agent-loop cost caps (`max_iterations` / `max_budget_per_session`); budget controls, not cache accounting. **Dismissed.** (Its "a cost cap surfaces as the same status class as rate limiting" point is the same observability-shape family as Claim 4, but it is not evidence for it.)
  - Additional cross-references found by searching `source-notes/` beyond the candidate list, all verified per MINER.md §4b before citation: `docs-litellm-caching-all-caches.md` (#1431), `docs-litellm-caching-hosted-cache.md` (#1432), `failure-litellm-bedrock-invoke-prompt-cache.md` (#697), `failure-litellm-model-cost-map-silent-fallback.md` (cited by lesson heading, not a claim number, because those are lesson sections — MINER.md §4b rule 4), `docs-litellm-token-usage-helpers.md`, `docs-litellm-streaming-token-usage.md`, `blog-litellm-claude-opus-4-8-day-0.md`.
  - Issue numbers in parentheses are the frontmatter `issue:` values of the cited notes, recorded for the Assayer's convenience.
- `registry/sources.json` and `registry/claims-index.json` were **not** edited — they are derived indexes rebuilt by `registry-rebuild.yml` after merge.