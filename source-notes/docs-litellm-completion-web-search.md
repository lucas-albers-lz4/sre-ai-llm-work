---
source_url: https://docs.litellm.ai/docs/completion/web_search
source_type: docs
title: "Web Search — LiteLLM Documentation (provider-native web search across /chat/completions, /responses, and Gemini image generation)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; front matter last_updated 2026-10-06)
date_extracted: 2026-10-07
last_checked: 2026-10-07
status: current
confidence_overall: emerging
issue: "#1609"
---

# Web Search (LiteLLM Docs)

> LiteLLM's canonical reference for attaching provider-native web search to LLM
> requests across three endpoints (`/chat/completions`, `/responses`, and Gemini
> `/images/generations`) and six providers (`openai`, `xai`, `vertex_ai`,
> `anthropic`, `gemini`, `perplexity`), with LiteLLM cost tracking claimed since
> `v1.71.0+`. The ops-relevant content is a **cost-attribution surface that a
> token-based meter cannot see**: search spend is additive to token spend, is
> billed in provider-specific units (`per_query` vs `per_prompt`, plus
> per-context-size tiers), is recorded in a separate usage field
> (`usage.prompt_tokens_details.web_search_requests`), and only lands in the
> total if the caller prices the *response object* rather than re-tokenizing.
> Around it sit two routing hazards — an OpenAI capability split between
> `/chat/completions` search models and `/responses` regular models, and a
> `supports_web_search: False` gate that does not actually remove a deployment
> from general routing — plus an xAI compatibility shim that silently drops
> `search_context_size`.

## Source Context

- **Type**: docs (vendor documentation — LiteLLM AI Gateway, a focused topic
  page under "Guides > Tool Calling").
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for *what the gateway documents* (parameter names, provider and
  model lists, pricing-field names, usage-field paths, config surface). It is
  capability documentation only: no measured latency, no failure writeup, no
  production experience, and no rate-limit or fallback guidance.
- **Scope**: the page's own feature matrix; each provider's search backend; the
  OpenAI two-path split; SDK and proxy quick starts for `/chat/completions` and
  `/responses`; `web_search_options` in `config.yaml`; capability discovery
  (`supports_web_search()`, `GET /model_group/info`); and the Web Search Cost
  Tracking section (provider billing units, the two pricing fields, the usage
  path, and the per-provider extraction rules). It does **not** cover rate
  limits, throttling, fallbacks, retries, caching, timeouts, auth/egress,
  response schema, citation payloads, or prompt-injection handling for
  search-derived content.
- **Sibling pages**: the front matter's `related:` list is
  `/docs/completion/function_call` (already mined as
  `docs-litellm-completion-function-call.md`, which explicitly names
  `/docs/completion/web_search` as an unread sibling) and
  `/docs/integrations/websearch_interception` (not followed — a separate
  integration page outside this extraction's scope, recorded as a known unread
  neighbor rather than silently skipped).
- **Quotation source**: this note quotes the page's **raw markdown endpoint**
  (`https://docs.litellm.ai/docs/completion/web_search.md`, HTTP 200), which
  preserves the exact table markup, code fences, and front matter; the rendered
  HTML fetch collapses some newlines. Following the precedent of
  `docs-litellm-mock-requests.md` (#1275) and
  `docs-litellm-cost-map-and-response-cost.md` (#1586). Every `Quote` below is a
  character-for-character contiguous fragment from that markdown.
- **Prospector caveat honored**: the triage warned the page carries no
  publication or last-updated date. The raw front matter does carry
  `last_updated: "2026-10-06"` (the rendered page hides it), so
  `date_published` is recorded as unknown and `last_checked` is that date.
  The triage also warned the page documents no rate limits or fallback
  behavior; Claim 15 records that absence rather than inferring from it.

## Extracted Claims

### Claim 1: The page's support matrix is the feature-boundary contract — three endpoints, six providers, cost tracking supported, and a stated minimum SDK version
- **Evidence**: The opening "Use web search with litellm" feature table lists
  the supported endpoints, providers, cost tracking, and version.
- **Confidence**: settled (first-party feature table)
- **Quote**: "Use web search with litellm"
- **Quote**: "LiteLLM Cost Tracking | ✅ Supported"
- **Quote**: "LiteLLM Version | `v1.71.0+`"
- **Our assessment**: This is a second, broader capability surface than the
  sibling `docs-litellm-completion-web-fetch.md` (#1608), which is
  Anthropic-only and one endpoint. Here the gateway accepts web search on the
  two main chat shapes plus Gemini image generation, so a single proxy config
  can route search-enabled traffic across six providers. The version floor
  (`v1.71.0+`) is the only pin on the page — useful for the guide's
  "pin versions, then audit capability" posture, and the page never states a
  deprecation or removal path for the feature.

### Claim 2: Each provider runs its own search backend — the gateway normalizes the *request* surface but not the search index or the result semantics
- **Evidence**: The "Which Search Engine is Used?" table gives a distinct
  backend and note per provider.
- **Confidence**: settled (first-party table)
- **Quote**: "Each provider uses their own search backend:"
- **Quote**: "**Google AI/Vertex** (`gemini-2.0-flash`) | **Google Search** | Uses actual Google search results"
- **Our assessment**: The operator is standardizing the *interface*
  (`web_search_options` / `web_search_preview`), not the *evidence*.
  Google Grounding, OpenAI's internal index, and Perplexity's engine are
  different corpora, so a fallback between providers can change the answer, the
  citation set, and the result-freshness properties behind an unchanged client
  request. The page presents the uniformity of the request as the feature and
  never names the non-uniformity of the ground truth — the guide should carry
  that gap explicitly.

### Claim 3: OpenAI restricts `web_search_options` to dedicated search models — regular frontier models (`gpt-5.6-terra`, `gpt-5.6-luna`) are documented as *not* supporting it
- **Evidence**: A `:::warning` block under the search-engine table with an
  explicit exclusion list.
- **Confidence**: settled (explicit vendor warning)
- **Quote**: "For OpenAI, only dedicated search models support the `web_search_options` parameter:"
- **Quote**: "**Regular models like `gpt-5.6-terra` and `gpt-5.6-luna` do not support `web_search_options`**"
- **Our assessment**: This is the page's sharpest capability boundary and it
  sits on the same surface the corpus already documents as drift-prone:
  `docs-litellm-completion-function-call.md` Claims 2-3 establish that the
  `supports_*()` predicates are fail-closed lookups over a remote cost map, so
  an operator building a search tier on `supports_web_search()` is trusting a
  declared flag whose prose list here (`gpt-5-search-api`,
  `gpt-4o-search-preview`, `gpt-4o-mini-search-preview`) is a moving target.
  The warning's practical shape: a gateway that sends `web_search_options` to a
  regular OpenAI model is outside the documented contract, and the page gives no
  error behavior for that mismatch — so "attach search options, let the model
  sort it out" is not a safe pattern.

### Claim 4: Search models search *automatically* even without `web_search_options` — the parameter is an opt-in tuning surface (`search_context_size`, `user_location`), not a search on/off switch
- **Evidence**: A `:::tip` block that follows the warning and is repeated in the
  "OpenAI Web Search: Two Approaches" section.
- **Confidence**: settled (explicit vendor tip)
- **Quote**: "Search models (like `gpt-4o-search-preview`) **automatically search the web** even without the `web_search_options` parameter."
- **Quote**: "Use `web_search_options` when you need to:\n- Adjust `search_context_size` (`\"low\"`, `\"medium\"`, `\"high\"`)\n- Specify `user_location` for localized results"
- **Our assessment**: The on/off intuition is backwards for dedicated search
  models: omitting `web_search_options` does **not** mean "no search", so a
  deployment that expects plain completion behavior from a search model gets a
  search (and a search bill) anyway. This is the same "the capability is on
  whether you asked or not" shape as the automatic caching in
  `docs-litellm-completion-prompt-caching.md` Claim 9 (OpenAI prompt caching is
  "automatic"), and it is the cost-attribution reason Claim 10+ below matter:
  the only per-request documentation of whether search ran is the usage field
  and the price, not the presence of the parameter.

### Claim 5: The two OpenAI paths are disjoint by model — search models work only on `/chat/completions` via `web_search_options`, regular models only on `/responses` via the `web_search_preview` tool
- **Evidence**: The "OpenAI Web Search: Two Approaches" table, and the
  `/responses` section's `:::info` block stating the inverse exclusion.
- **Confidence**: settled (explicit table + explicit info block)
- **Quote**: "OpenAI offers two distinct ways to use web search depending on the endpoint and model:"
- **Quote**: "Search-dedicated models like `gpt-5-search-api` and `gpt-4o-search-preview` do **not** support the `/responses` endpoint. Use them with `/chat/completions` + `web_search_options` instead (see above)."
- **Our assessment**: The gateway makes one capability look like one feature
  while it is really two mutually exclusive endpoint/model pairings. The
  operational consequence is a routing matrix the client cannot express: a
  client that switches from `/chat/completions` to `/responses` (or vice versa)
  must also switch which model it requests, or the search silently does not
  exist for that call. Combined with Claim 3, the OpenAI search surface is
  four-way (endpoint × model-class) with no documented error for the wrong pair
  — exactly the kind of "the docs describe a shape, the operator must encode the
  constraints" gap the corpus treats as a gate/reliability item.

### Claim 6: xAI is a compatibility shim — LiteLLM reroutes search requests to xAI's Responses API and back-converts, and `search_context_size` is silently dropped
- **Evidence**: The xAI sub-block under "Search context size" states the
  rerouting and the dropped parameter.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "xAI no longer runs web search on its own `/chat/completions`, so when `web_search_options` is set LiteLLM sends the request to xAI's Responses API with a `web_search` tool and converts the result back to a chat completion. xAI does not support `search_context_size`, so it is dropped"
- **Quote**: `web_search_options={}  # search_context_size is ignored for xAI`
- **Our assessment**: This is a "the gateway behaves differently by route and
  does not tell the caller" finding, matching
  `docs-litellm-messages-to-responses-mapping.md` Claim 1's silent-drop class
  (`stop_sequences`/`top_k` dropped with no telemetry). An operator tuning
  `search_context_size: "high"` on an xAI deployment gets no effect and no
  warning; the request returns a normal 200. It also means the xAI path
  traverses LiteLLM's Responses adapter, so the translation hazards documented
  in that note (tool-shape remapping, response-field fallbacks) apply
  underneath a feature the web_search page describes in one paragraph.

### Claim 7: `web_search_options` can be set per-deployment in `config.yaml` (`{}` enables defaults), applies to every request to that model, and request-level values override it
- **Evidence**: The "Configuring Web Search in config.yaml" section's "Default
  Web Search" block and its closing note.
- **Confidence**: settled (explicit config surface + explicit override rule)
- **Quote**: "web_search_options: {}  # Enables web search with default settings"
- **Quote**: "**Note:** When `web_search_options` is set in the config, it applies to all requests to that model. Users can still override these settings by passing `web_search_options` in their API requests."
- **Our assessment**: This is a gateway *default*, not a per-request control, so
  a deployment-level `{}` turns search on for every caller of that model,
  including callers who did not ask — and the config's own override note means
  the effective value depends on request shaping the operator does not control.
  For cost governance this is the reverse of the safety property an operator
  wants (defaults should be the cheap path). It is also the mechanism that makes
  Claim 4's automatic-search behavior unavoidable at the fleet level: one YAML
  line can add a per-call search fee to an entire model group.

### Claim 8: `supports_web_search: False` in a deployment's `model_info` does not remove the deployment from general routing — LiteLLM still routes LLM requests to it and only narrows *WebSearch* traffic
- **Evidence**: The "Advanced" subsection's two-deployment example
  (`gpt-5.6-terra` OpenAI + `gpt-5.6-terra` Azure with
  `supports_web_search: False`) and the sentence immediately following it.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "In this example, LiteLLM will still route LLM requests to both deployments, but for WebSearch, will solely route to OpenAI."
- **Quote**: "supports_web_search: False <---- KEY CHANGE!"
- **Our assessment**: This is the Prospector's "partial-drain footgun" and the
  page states it plainly. An operator who sets `supports_web_search: False` to
  *isolate* a non-search-capable deployment (e.g. an Azure replica) gets the
  opposite of isolation: the deployment keeps serving ordinary traffic and
  "WebSearch"-classified traffic is steered to the other deployment. Because
  "WebSearch" classification is internal to the router, the operator cannot see
  from the config which requests will be re-routed. It belongs next to the
  corpus's capability-discovery material
  (`docs-litellm-completion-function-call.md` Claims 3-4: capability is a
  cost-map field, and provider info can outrank the map), because a
  routing-affecting flag that is not a routing control is a correctness hazard
  dressed as a capability declaration.

### Claim 9: Capability discovery is `litellm.supports_web_search(model=...)` and `GET /model_group/info` — but the page documents no failure mode, and this predicate family is a fail-closed cost-map lookup
- **Evidence**: The "Checking if a model supports web search" section — an SDK
  block of bare `assert ... == True` lines, a `/model_group/info` curl, and an
  "Expected Response" JSON carrying `supports_web_search` per model group.
- **Confidence**: settled that the page documents these accessors and no failure
  mode; emerging for the behavior on unmapped models (inferred from the verified
  sibling note, not stated here)
- **Quote**: "Use `litellm.supports_web_search(model=\"model_name\")` -> returns `True` if model can perform web searches"
- **Quote**: "Call `/model_group/info` to check if a model supports web search"
- **Quote**: (no direct quote; see paraphrase in Our assessment — the page states
  no behavior for an unmapped model)
- **Our assessment**: Same accessor family, same documented silence. The page
  says only what a `True` means; it never says what an unmapped model, a missing
  cost-map key, or a provider-config exception returns. The sibling
  `docs-litellm-completion-function-call.md` **Claims 2, 3, and 4** already
  verified (against shipped `v1.103.2`) that these predicates are fail-closed
  lookups into the remote, reloadable
  `model_prices_and_context_window.json`, with a provider-info override and a
  `return False` on every uncertain path. So `supports_web_search() == False` is
  ambiguous between "cannot search" and "not in our map yet", and the five bare
  `assert`s on this page are illustrative, not fixtures — precisely the Claim 14
  lesson from that note. Recommend the guide route search-capability gating
  through the same "declared capability, not actual capability" rule.

### Claim 10: Web search cost is additive to token cost and is billed in provider-specific units defined in the same pricing map as token prices
- **Evidence**: The "Web Search Cost Tracking" intro and the "How providers
  charge for web search" table.
- **Confidence**: settled (explicit first-party statement + table)
- **Quote**: "LiteLLM tracks web search costs automatically based on provider-specific billing models. The cost is added on top of the standard token-based pricing."
- **Quote**: "**Gemini 3.x** (3-flash, 3-pro, 3.1-*) | Per search query | Each internal search query is billed individually. One prompt may trigger multiple queries."
- **Quote**: "**Gemini 2.x** (2.0-flash, 2.5-flash, 2.5-pro) | Per grounded prompt | Flat fee per API call that uses grounding, regardless of how many queries are executed internally."
- **Our assessment**: This is the strongest chapter hook, and it is a *second,
  non-token cost dimension* living in the file the corpus already treats as the
  pricing and context-window authority:
  `docs-litellm-cost-map-and-response-cost.md` Claim 5 (the map is
  simultaneously the context-window authority) and
  `docs-litellm-completion-prompt-caching.md` Claim 11 (the map is also the
  capability registry). The guide's existing rule that a spend dashboard is
  bounded by the installed map version now needs a companion: a dashboard built
  from `input_cost_per_token × prompt_tokens + output_cost_per_token ×
  completion_tokens` **understates** any search-enabled request by the entire
  search fee, and the fee is not derivable from the response's headline `usage`
  object. The token-price audit questions rotate to "which search tier, and
  which billing unit, does my route resolve to?"

### Claim 11: The billing unit defaults to `per_prompt`, so one prompt that fires N internal queries is billed as one — an under-attribution risk for any model whose unit is not explicitly `per_query`
- **Evidence**: The two pricing fields, the `:::info` default statement, and the
  Gemini 2.x "clamped to 1" extraction rule.
- **Confidence**: settled (explicit default statement)
- **Quote**: "**`web_search_billing_unit`** *(on Gemini models)*: `\"per_query\"` (each search query is billed individually) or `\"per_prompt\"` (default; flat fee per API call that uses search)."
- **Quote**: "Models without `web_search_billing_unit` default to `\"per_prompt\"`: one flat charge per API call that uses web search, regardless of how many internal queries the model executes."
- **Our assessment**: The default is the *optimistic* accounting choice, and the
  page is explicit about the tradeoff: Gemini 3.x bills per internal query, the
  same page says "One prompt may trigger multiple queries", and a model that
  omits the unit is charged one flat fee. `web_search_billing_unit` is
  overridable per deployment via `model_info` (the "Pricing configuration"
  example), so an operator can align the map to the invoice — but *only if they
  know the provider's unit*. Cross-check: the promptfoo provider-search cost
  tiers record "$35/1k Gemini grounded prompts, $45/1k Vertex Web Grounding"
  (`docs-promptfoo-model-graded-metrics.md` Claim 12) — a per-prompt figure,
  which is the same optimistic unit this page defaults to; two independent
  sources agreeing on the cheap assumption is exactly when a guide should
  flag the under-count, not the agreement.

### Claim 12: Per-provider usage extraction is heterogeneous — search-request counts come from different provider response fields, and xAI reports to a different field entirely
- **Evidence**: The "How LiteLLM tracks search usage" bullet list.
- **Confidence**: settled (explicit per-provider list)
- **Quote**: "The number of web search requests is stored in `usage.prompt_tokens_details.web_search_requests`. LiteLLM extracts this from each provider's response:"
- **Quote**: "**Gemini**: Extracted from `groundingMetadata.webSearchQueries` in the response. For Gemini 2.x, clamped to 1 (per-prompt billing)."
- **Quote**: "**Anthropic**: Reported via `server_tool_use.web_search_requests`."
- **Quote**: "**xAI**: Reported in `usage.server_side_tool_usage_details.web_search_calls` rather than `web_search_requests`. `num_sources_used` is not read. When xAI returns `usage.cost`, LiteLLM uses it as the response cost, which already includes the search charge"
- **Our assessment**: The normalized surface is the *path*
  (`usage.prompt_tokens_details.web_search_requests`), but the page's own bullet
  list shows it is assembled from four structurally different vendor fields, and
  one provider (xAI) does not use the normalized count field at all. The
  `num_sources_used` "is not read" note is a recorded drop, so any monitor
  expecting a source-count signal from xAI gets nothing. For Ch02 this is the
  concrete caution behind "normalized usage is a translation, not a
  measurement": the same field name has per-provider provenance and one
  provider's count is clamped (Gemini 2.x) rather than observed.

### Claim 13: When xAI returns `usage.cost`, LiteLLM adopts it verbatim as the response cost — a provider-supplied price that bypasses the local token computation for that call
- **Evidence**: Same xAI bullet as Claim 12, plus the closing sentence of the
  "How LiteLLM tracks search usage" section's example, which routes total cost
  through `litellm.completion_cost(completion_response=response)`.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "When xAI returns `usage.cost`, LiteLLM uses it as the response cost, which already includes the search charge"
- **Our assessment**: This is the one documented case on the page where the
  gateway's cost figure is *provider-reported* rather than map-derived — and it
  is the opposite of the corpus's standing assumption that
  `completion_cost`/`cost_per_token` compute locally from the bundled map with
  "no provider-side reconciliation"
  (`docs-litellm-token-usage-helpers.md` Claims 1 and 4). It also compounds the
  open question in `docs-litellm-cost-map-and-response-cost.md` Claim 9 (does
  `completion_cost(completion_response=…)` read the response's reported usage or
  re-tokenize?): on the xAI path the answer is "whatever xAI's `usage.cost`
  says", so the same call shape produces a provider-reconciled number on xAI and
  a map-derived estimate elsewhere. A spend pipeline must not assume one
  provenance across providers; the page is the first corpus source to mix them
  in one function.

### Claim 14: The page's own worked idiom for recovering total cost is `litellm.completion_cost(completion_response=response)` with the inline comment "includes token cost + web search cost" — so a token recomputation does not
- **Evidence**: The closing code block of the cost-tracking section.
- **Confidence**: settled (documented idiom)
- **Quote**: "# Get total cost (includes token cost + web search cost)"
- **Quote**: `cost = litellm.completion_cost(completion_response=response)`
- **Our assessment**: The comment is the page admitting the two cost components
  are only combined on the response-object code path. An operator who computes
  spend from `usage.prompt_tokens`/`completion_tokens` (the cheaper, more common
  pattern, and the one the prompt-caching note's Claim 4 warns overstates cached
  traffic) misses search spend entirely. On a search-heavy route that is a
  systematic understatement of exactly the newest cost line. This is a
  Ch02/Ch05 observability rule: the per-request cost figure and the token
  recomputation are different numbers, and the guide should require the former
  for any search-enabled route (with the Claim 13 provenance caveat attached).

### Claim 15: The page documents no rate limits, fallbacks, retries, caching, timeouts, auth, or error semantics for the search path, and `perplexity` is listed as supported with no example
- **Evidence**: Full read of the page. The only operational sections are the
  config, capability check, and cost tracking; the cost example is the only
  async/response handling; `perplexity` appears in the provider table, the
  search-backend table, and the billing table but in neither the quick starts
  nor the config examples.
- **Confidence**: settled (negative evidence from a complete read)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Recorded as an absence, per the sibling web-fetch note's
  Claim 6 pattern. The Prospector explicitly warned against inferring rate
  limits or fallback behavior from this page, and the page confirms the warning
  — `fallback`, `retry`, `rate limit`, and `timeout` do not appear in a
  functional sense. The `perplexity` asymmetry is a smaller documentation gap:
  a first-class listed provider has a billing model but no wiring example, so
  the operator is left to infer its request shape. Neither gap should be filled
  from upstream provider docs in this note; they are the finding.

### Claim 16: The page is internally inconsistent on model identities — its Anthropic supported-model list excludes the model every Anthropic example uses, and its Google model strings differ between table, examples, and pricing JSON
- **Evidence**: The Anthropic `:::info` list (`claude-3-5-sonnet-latest`,
  `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-latest`,
  `claude-3-5-haiku-20241022`, `claude-3-7-sonnet-20250219`) versus the Anthropic
  example's `model="anthropic/claude-sonnet-5"`; the search-engine table's
  `gemini-2.0-flash` versus the code examples' `gemini-3.8-flash` and the pricing
  JSON's `gemini/gemini-3.8-flash` / `gemini/gemini-2.5-flash`.
- **Confidence**: settled (both strings are on the page, verbatim, and
  mutually inconsistent)
- **Quote**: "Claude models that support web search: `claude-3-5-sonnet-latest`, `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-latest`, `claude-3-5-haiku-20241022`, `claude-3-7-sonnet-20250219`"
- **Our assessment**: Recorded, not resolved — the same model-table-vs-example
  drift `docs-litellm-completion-web-fetch.md` Claim 7 records on the sibling
  page. Either the list is stale or the examples use unsupported models; both
  readings yield the same guide advice (verify model support against the current
  list before relying on search). Per MINER.md §4a this is recorded rather than
  filed as a contradiction: it does not change guide advice and no existing
  source note takes an opposing position. Also note the xAI section's internal
  tension with the search-engine table — the table attributes xAI search to
  "xAI's search + X/Twitter" while the later paragraph says xAI "no longer runs
  web search on its own `/chat/completions`"; the second is the current
  mechanism and the table is the stale summary.

## Concrete Artifacts

All artifacts below are verbatim from
`https://docs.litellm.ai/docs/completion/web_search.md` (raw markdown endpoint),
unless attributed otherwise.

### Feature matrix (page top)

| Feature | Details |
|---------|---------|
| Supported Endpoints | - `/chat/completions` <br/> - `/responses` <br/> - `/images/generations` (Gemini image models only) |
| Supported Providers | `openai`, `xai`, `vertex_ai`, `anthropic`, `gemini`, `perplexity` |
| LiteLLM Cost Tracking | ✅ Supported |
| LiteLLM Version | `v1.71.0+` |

### Provider search backends (page, "Which Search Engine is Used?")

| Provider | Search Engine | Notes |
|----------|---------------|-------|
| **OpenAI** (`gpt-5-search-api`, `gpt-4o-search-preview`, `gpt-4o-mini-search-preview`) | OpenAI's internal search | Real-time web data |
| **xAI** (`grok-3`) | xAI's search + X/Twitter | Real-time social media data |
| **Google AI/Vertex** (`gemini-2.0-flash`) | **Google Search** | Uses actual Google search results |
| **Anthropic** (`claude-3-5-sonnet`) | Anthropic's web search | Real-time web data |
| **Perplexity** | Perplexity's search engine | AI-powered search and reasoning |

### OpenAI two-approaches table (page, "OpenAI Web Search: Two Approaches")

| Approach | Endpoint | Models | How to enable |
|----------|----------|--------|---------------|
| **Search Models** | `/chat/completions` | `gpt-5-search-api`, `gpt-4o-search-preview`, `gpt-4o-mini-search-preview` | Pass `web_search_options` parameter |
| **Web Search Tool** | `/responses` | `gpt-5`, `gpt-4.1`, `gpt-4o`, and other regular models | Pass `web_search_preview` tool |

### Provider billing units (page, "How providers charge for web search")

| Provider | Billing Unit | How it works |
|----------|-------------|--------------|
| **Gemini 3.x** (3-flash, 3-pro, 3.1-*) | Per search query | Each internal search query is billed individually. One prompt may trigger multiple queries. |
| **Gemini 2.x** (2.0-flash, 2.5-flash, 2.5-pro) | Per grounded prompt | Flat fee per API call that uses grounding, regardless of how many queries are executed internally. |
| **OpenAI** (gpt-4o-search, gpt-5-search) | Per search context size | Cost varies by `search_context_size` (`low`, `medium`, `high`). |
| **Anthropic** (Claude with web search) | Per search request | Fixed cost per web search tool invocation. |
| **Perplexity** (sonar, sonar-pro) | Per search context size | Cost varies by `search_context_size`. |

### Pricing configuration, verbatim (page, "Pricing configuration")

```json
{
    "gemini/gemini-3.8-flash": {
        "web_search_billing_unit": "per_query",
        "search_context_cost_per_query": {
            "search_context_size_low": 0.014,
            "search_context_size_medium": 0.014,
            "search_context_size_high": 0.014
        }
    },
    "gemini/gemini-2.5-flash": {
        "search_context_cost_per_query": {
            "search_context_size_low": 0.035,
            "search_context_size_medium": 0.035,
            "search_context_size_high": 0.035
        }
    }
}
```

Note the second entry omits `web_search_billing_unit`, demonstrating the
`per_prompt` default (Claim 11). The `model_info` override form is the same two
fields under a deployment:

```yaml
    model_info:
      web_search_billing_unit: per_query
      search_context_cost_per_query:
        search_context_size_low: 0.014
        search_context_size_medium: 0.014
        search_context_size_high: 0.014
```

### Usage extraction, verbatim (page, "How LiteLLM tracks search usage")

> The number of web search requests is stored in
> `usage.prompt_tokens_details.web_search_requests`. LiteLLM extracts this from
> each provider's response:
>
> - **Gemini**: Extracted from `groundingMetadata.webSearchQueries` in the
>   response. For Gemini 2.x, clamped to 1 (per-prompt billing).
> - **OpenAI**: Reported directly in the usage metadata.
> - **Anthropic**: Reported via `server_tool_use.web_search_requests`.
> - **xAI**: Reported in `usage.server_side_tool_usage_details.web_search_calls`
>   rather than `web_search_requests`. `num_sources_used` is not read. When xAI
>   returns `usage.cost`, LiteLLM uses it as the response cost, which already
>   includes the search charge

### The total-cost idiom, verbatim (page, closing example)

```python
response = litellm.completion(
    model="gemini/gemini-3.8-flash",
    messages=[{"role": "user", "content": "Latest tech news?"}],
    web_search_options={"search_context_size": "medium"},
)

# Check web search usage
print(response.usage.prompt_tokens_details.web_search_requests)  # e.g., 3

# Get total cost (includes token cost + web search cost)
cost = litellm.completion_cost(completion_response=response)
print(f"Total cost: ${cost}")
```

### The partial-drain config, verbatim (page, "Advanced")

```yaml
  - model_name: gpt-5.6-terra
    litellm_params:
      model: openai/gpt-5.6-terra
  - model_name: gpt-5.6-terra
    litellm_params:
      model: azure/gpt-5.6-terra
      api_base: "x.openai.azure.com/"
      api_version: 2025-03-01-preview
    model_info:
      supports_web_search: False <---- KEY CHANGE!
```

With the page's own verdict: "In this example, LiteLLM will still route LLM
requests to both deployments, but for WebSearch, will solely route to OpenAI."

### `GET /model_group/info` expected response, verbatim (abridged to first two entries)

```json
{
  "data": [
    {
      "model_group": "gpt-5-search-api",
      "providers": ["openai"],
      "max_tokens": 128000,
      "supports_web_search": true
    },
    {
      "model_group": "gpt-4o-search-preview",
      "providers": ["openai"],
      "max_tokens": 128000,
      "supports_web_search": true
    }
  ]
}
```

## Cross-References

**Candidates from `miner-related-notes.md`** (read before Cross-References per
MINER.md §4; all ten pre-computed candidates are cited or explicitly dismissed):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**. Batch JSONL
  rate-limiting and enqueued-token reservations. Different endpoint and
  accounting contract; it is the useful neg*ative* example (LiteLLM meters batch
  input locally and enforces on it), whereas this page documents a cost
  dimension LiteLLM reads back from providers and never enforces.
- `source-notes/docs-litellm-completion-web-fetch.md` — **Cited** (Extends,
  Corroborates; see below). Direct sibling: retrieval vs discovery, and the same
  "operational documentation is absent" finding (its Claim 6).
- `source-notes/docs-litellm-completion-input-params.md` — **Cited** (Extends).
  **Claim 11** documents `input_cost_per_token` / `output_cost_per_token` as
  per-call cost *overrides* on the request body; this page's
  `model_info.search_context_cost_per_query` is the same class of declaration at
  deployment scope for a non-token cost dimension. Together they show LiteLLM's
  cost model has multiple operator-settable price surfaces.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**. Bedrock native
  Invoke passthrough and bearer-token auth swap; no search surface.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**.
  Non-chat-endpoint fallbacks and the support-matrix genre; no search cost or
  routing content. (Its Claim 6's observation that the support-matrix genre
  recurs across LiteLLM docs is adjacent but not evidence for anything here.)
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **Cited**
  (Corroborates, Extends; see below). **Claim 7** documents the gateway's
  `web_search*` tool type-remap on the `/v1/messages`→Responses path, which is
  the mechanism underneath this page's xAI shim (Claim 6).
- `source-notes/docs-litellm-mock-requests.md` — **Dismissed**. Mock responses
  and null-usage stubs; no search-path content.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**. A2A
  per-session iteration/budget caps; different capability and enforcement model.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**. Langfuse docs MCP
  server; unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **Dismissed**. Toil
  taxonomy and measurement; no LLM cost/routing content.

**Primary cross-references** (every cited claim number re-read and verified per
MINER.md §4b before writing; no cross-note quote is reproduced, so there is no
cross-note quote-verification risk):

- **Corroborates**:
  - `source-notes/docs-litellm-completion-function-call.md` **Claims 2, 3, 4** —
    the verified behavior of the `supports_*()` predicate family (fail-closed
    cost-map lookup, remote/reloadable map, provider-info override). This page
    documents `supports_web_search()` as a sibling accessor and gives no failure
    mode (Claim 9 here); the function_call note supplies the verified mechanism
    this page omits.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` **Claim 7** —
    the gateway type-remaps Anthropic web-search tools to
    `{"type": "web_search_preview"}` on the Responses path. This page's xAI shim
    (Claim 6) is the same class of provider-boundary normalization: a search
    capability is rewritten to another API's tool shape in flight.
  - `source-notes/docs-litellm-completion-prompt-caching.md` **Claim 11** — the
    same "`supports_*() == False` means 'not in our map' as much as
    'unsupported'" reading, and the cost map as capability registry. This page's
    Claim 9 is the web-search instance.
  - `source-notes/docs-litellm-completion-stream.md` **Claim 9** — a
    source-verified guard carved out explicitly for "Vertex Gemini (Flash /
    Flash Lite with web search)" because those routes emit metadata-only /
    usage-only chunks. That is the streaming-side failure mode of the usage
    extraction this page documents in Claim 12.
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 12** — search
    cost tiers of roughly $10–45 per 1,000 search calls across the same provider
    family. The LiteLLM pricing JSON's 0.014/0.035 per-query figures fall in
    that band, so the two independent sources corroborate the *order of
    magnitude* of search spend (while agreeing on the optimistic per-prompt unit
    — Claim 11 here).
- **Contradicts**: **none.** The page is internally inconsistent on model
  identities (Claim 16) and on whether xAI searches natively, but both are
  stale-summary artifacts that do not change guide advice, so per MINER.md §4a
  no contradiction issue was filed. No existing source note opposes a claim
  here. The nearest tensions are conditioning variables, not contradictions:
  `docs-litellm-token-usage-helpers.md` Claims 1 and 4 ("no provider-side
  reconciliation") versus this page's Claim 13 (xAI `usage.cost` is adopted as
  the response cost) is a per-provider provenance split the page itself states,
  not a disagreement between sources — recorded in Claim 13, not filed. Checked
  the open `contradiction`-labeled issues and `CONTRADICTIONS.md` (no `C-NNN`
  entries): none cover this surface.
- **Extends**:
  - `source-notes/docs-litellm-cost-map-and-response-cost.md` **Claims 1, 4, 5,
    9** — the cost-map write path, `completion_cost`'s two input forms, the
    map-as-context-window authority, and the open question of whether the
    response-object form is provider-reconciled. This page's pricing fields
    live in that same map (Claim 10) and its Claim 14 idiom is exactly the
    response-object form that note's Claim 9 leaves open; Claim 13 here is one
    provider on which that question is answered.
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claims 1 and 4** — the
    local-estimator model (`token_counter` + bundled map) this page's additive
    search fee sits on top of, and which Claim 14 shows is insufficient for a
    search-enabled total.
  - `source-notes/docs-litellm-completion-web-fetch.md` (the sibling page) —
    **Claims 5, 6, 7, 8**: the request-path egress/completeness caveats, the
    "no operational documentation is itself a finding" posture, and the
    model-table-vs-example inconsistency pattern. This page is the discovery half
    of the same capability pair.
  - `source-notes/docs-litellm-completion-input-params.md` **Claim 11** — the
    request-body per-call cost overrides; this page's `model_info` search-price
    override is the deployment-scoped non-token analogue.
- **Novel**: First corpus coverage of the LiteLLM web-search surface itself —
  the feature matrix, the provider search backends, the OpenAI two-path model
  split, `web_search_options` as an automatic-search tuning surface,
  `supports_web_search` discovery plus the partial-drain semantics of
  `supports_web_search: False`, the `search_context_cost_per_query` /
  `web_search_billing_unit` pricing fields and the `per_prompt` default, the
  `usage.prompt_tokens_details.web_search_requests` path with its per-provider
  provenance, and the xAI `usage.cost`/shim behavior. The corpus previously
  named web search only as (a) an eval-grader cost tier and grader tool config
  (`docs-promptfoo-search-rubric.md`, `docs-promptfoo-model-graded-metrics.md`
  Claim 12), (b) a `/v1/messages`→Responses tool remap
  (`docs-litellm-messages-to-responses-mapping.md` Claim 7), (c) a GPT-5.5
  capability-list item (`blog-litellm-gpt-5-5-day-0.md` Claim 6), and (d) the
  sibling web-fetch page's contrast. Nothing in `source-notes/` or `guide/`
  documented the gateway's search-cost attribution or search-routing surface.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — cost-map / spend-accounting sections**:
  add a "search is a second, non-token cost line" rule. Token-derived spend
  (`input_cost_per_token × prompt_tokens + …`), and any dashboard built from it,
  **understates** every search-enabled request by the full search fee; the
  search fee is billed in provider-specific units
  (`search_context_cost_per_query`, `web_search_billing_unit`, default
  `per_prompt`) and only lands in the total when the caller uses
  `litellm.completion_cost(completion_response=…)` [Claims 10, 11, 14]
  [settled]. Add the provenance caveat that on xAI the response cost is the
  provider's own `usage.cost`, so one function returns provider-reconciled and
  map-derived figures on different routes [Claim 13] [settled]; this sharpens
  the guide's existing "estimator output, reconcile against the invoice" rule
  (`docs-litellm-token-usage-helpers.md`, `docs-litellm-cost-map-and-response-cost.md`)
  rather than replacing it.
- **Chapter 05 — capability discovery / cost-map-reload section**: place
  `supports_web_search()` and `GET /model_group/info` under the existing
  "declared capability, not actual capability" rule that
  `docs-litellm-completion-function-call.md` Claims 2-4 established for the
  `supports_*()` family: a `False` is ambiguous between "cannot search" and "not
  in the map", the map is remote and reloadable, and the page's bare `assert`
  examples are illustrative, not fixtures [Claim 9] [settled surface / emerging
  behavior]. File it beside the capability-discovery material the Prospector
  named.
- **Chapter 05 — routing / partial-drain**: document that
  `supports_web_search: False` on a deployment does **not** drain it from
  general routing; it only narrows WebSearch-classified traffic to supporting
  deployments [Claim 8] [settled]. The guide's advice should be: a capability
  flag is not a routing control — if you need to drain a deployment, use a
  routing mechanism, and audit which requests the router classifies as
  "WebSearch" before assuming isolation.
- **Chapter 05 — model-enablement audit**: the OpenAI search split is a
  four-way endpoint × model-class constraint (`web_search_options` only on
  search-dedicated models via `/chat/completions`; `web_search_preview` only on
  regular models via `/responses`), with no documented error for the wrong pair
  [Claims 3, 5] [settled]. Recommend an explicit route/matrix test rather than
  "attach options and see".
- **Chapter 02 (Observability)**: add the search-usage field and its
  per-provider provenance to the metering section. Read
  `usage.prompt_tokens_details.web_search_requests` for search counts, knowing
  its source differs per provider (Gemini `groundingMetadata.webSearchQueries`,
  Anthropic `server_tool_use.web_search_requests`, OpenAI usage metadata) and
  that xAI reports to `usage.server_side_tool_usage_details.web_search_calls`
  and `num_sources_used` is not read [Claim 12] [settled]; on streamed Vertex
  Gemini web-search routes, expect metadata-only/usage-only chunks
  (`docs-litellm-completion-stream.md` Claim 9). Keep the payload-usage path and
  the `completion_cost` path distinct, as the guide already does.
- **Chapter 06 (Security and Trust)**: a caution, not a finding. The page
  documents request-path search with no prompt-injection or trust section
  [Claim 15] [settled absence]; the sibling web-fetch note (Claims 3, 10) and
  `blog-promptfoo-indirect-prompt-injection-web-agents.md` cover the injected-
  content risk class. Recommend the guide state that search results re-enter
  context as provider-generated content with no documented boundary on this
  path, and that `web_search_options` scoping (`user_location`) is not an egress
  control.

## Extraction Notes

- Full read of the page's raw markdown (`/docs/completion/web_search.md`,
  HTTP 200) per MINER.md §1, including the front matter, both `:::warning` /
  `:::tip` / `:::info` blocks, both quick starts (SDK + proxy), the config
  section, the capability-check section, and the full cost-tracking section.
  The rendered HTML was also fetched to confirm the same content; quotes are
  taken from the raw markdown. No linked sub-page was mined: the `related:`
  entries are `function_call` (already a corpus note) and
  `websearch_interception` (a separate integration page, explicitly recorded as
  unread rather than silently dropped).
- All `Quote` fields are character-for-character contiguous fragments from the
  raw markdown page; no splicing across non-adjacent sentences. Table cells are
  quoted as single cells. Where the page renders escaped quotes inside inline
  code (`\"low\"` etc.), they are reproduced as they read in the markdown.
- `miner-related-notes.md` candidates (ten) were each cited or dismissed in
  Cross-References per MINER.md §4. Additional cross-refs were found by
  searching `source-notes/` directly (the function_call, cost-map,
  token-usage-helpers, prompt-caching, completion-stream, promptfoo, and
  gpt-5-5 notes), permitted by §4. Every cited claim number was re-read in its
  note before writing (§4b); no claim number is invented and no cross-note quote
  is reproduced.
- **No contradiction issue filed.** The page's two internal inconsistencies
  (Anthropic/Google model IDs; xAI native-search table vs paragraph) do not
  change guide advice and no existing note takes an opposing position, so §4a's
  "when NOT to file" applies. `CONTRADICTIONS.md` has no `C-NNN` entries and no
  open `contradiction`-labeled issue covers this surface; the nearest tension
  (this page's xAI provider-cost adoption vs `docs-litellm-token-usage-helpers`
  Claims 1/4) is a per-provider provenance split the page itself states and is
  recorded in Claim 13, not filed.
- The Prospector's key question — how a gateway attributes *search-query* cost
  and routes web-search traffic separately from ordinary completion traffic — is
  answered claim-by-claim: cost via the additive pricing fields, the usage path,
  and the `completion_cost` idiom (Claims 10-14); routing via the per-deployment
  default, the `supports_web_search` gate, and its documented partial-drain
  semantics (Claims 7-8).
- `confidence_overall` set to `emerging`: the documented surface (fields, paths,
  tables) is settled first-party documentation, but the guide value is the
  synthesis (the non-token cost gap, the routing footgun, the provenance split)
  plus the page's documented absences and internal inconsistencies — none of it
  exercised against a live provider. Matches the `emerging` rating on the
  sibling LiteLLM docs notes (#1586, #1608, #1390).
- `date_published` unknown (undated living docs page; raw front matter carries
  `last_updated: "2026-10-06"`); `date_extracted` and `last_checked` both
  2026-10-07 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain.
