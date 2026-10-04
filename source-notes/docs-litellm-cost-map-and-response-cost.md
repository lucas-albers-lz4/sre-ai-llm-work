---
source_url: https://docs.litellm.ai/docs/completion/token_usage
source_type: docs
title: "Completion Token Usage & Cost — LiteLLM Python SDK (response_cost, register_model, model_cost, get_max_tokens, custom tokenizers)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; front-matter last_updated 2026-10-03)
date_extracted: 2026-10-04
last_checked: 2026-10-04
status: current
confidence_overall: emerging
issue: "#1586"
---

# Completion Token Usage & Cost — the SDK cost-map write path and the per-call `response_cost` handle

> This is the **new canonical** LiteLLM SDK reference for token usage and cost,
> and it is a strict superset of the older `/token_usage` page mined as
> `docs-litellm-token-usage-helpers.md` (#1300) — which is *still live*, so
> both pages are readable simultaneously and, for one function, say different
> things about where pricing comes from (filed as contradiction **#1591**).
> The corpus-changing material is four surfaces the old page lacks: a
> **per-call cost handle** (`response_cost`, on *every* call, reachable only
> through the private `response._hidden_params` dict), a **runtime write path**
> for the cost map (`register_model`, accepting either an inline dict or a URL
> to a hosted JSON blob, mutating the process-global `litellm.model_cost` in
> place), the **context-window authority** (`get_max_tokens`, plus `model_cost`'s
> own `max_tokens` field), and the **custom-tokenizer escape hatch**
> (`create_pretrained_tokenizer` / `create_tokenizer` → `custom_tokenizer`).
> Ops consequence: one process-global pricing dict now has **three writers and
> one selector, none of which this page reconciles with the others** — the
> import-time hosted fetch, the proxy's `POST /reload/model_cost_map`, and
> (new here) `register_model` at runtime, with `LITELLM_LOCAL_MODEL_COST_MAP`
> choosing between the hosted and the packaged copy at import.

## Source Context

- **Type**: docs — official LiteLLM / BerriAI vendor documentation. A living
  Docusaurus page with no byline and no publication date; front matter carries
  `last_updated: "2026-10-03"`, `canonical_url:
  https://docs.litellm.ai/docs/completion/token_usage`, and a two-entry
  `related:` list (`/docs/caching/all_caches`, `/docs/exception_mapping`).
- **Author credibility**: First-party product documentation. Authoritative for
  the **SDK surface** (helper names, signatures, the documented shape of
  `model_cost`, the existence and location of `LITELLM_LOCAL_MODEL_COST_MAP`).
  **Not** authoritative for behavior: the page publishes no measured figure, no
  version pin, no changelog entry, and — critically — **no failure-mode
  statement for any function on it** (see Claim 11).
- **Scope — the page**: an intro paragraph, a `response_cost` example, a
  ten-bullet helper index, then nine numbered worked examples and a closing
  "Don't pull hosted model_cost_map" block. Covers the **Python SDK** only —
  nothing on the proxy, streaming, the `usage` object's field semantics,
  callbacks, or budget enforcement.
- **Scope — deliberately not re-extracted**, per the triage's explicit bounding
  (the shared three helpers are already covered by
  `docs-litellm-token-usage-helpers.md` **Claims 1–5**, verified):
  `token_counter`'s tokenizer-and-tiktoken-fallback definition, and
  `completion_cost`'s "combines `token_counter` and `cost_per_token`"
  composition. They are cited below as already-covered, not re-mined.
- **Extraction method note**: the page's **raw markdown endpoint**
  (`https://docs.litellm.ai/docs/completion/token_usage.md`, HTTP 200) was used
  as the quoting source, following the precedent set by
  `docs-litellm-mock-requests.md`. It preserves exact line breaks, indentation,
  and trailing whitespace; the rendered HTML fetch collapses newlines inside
  code blocks. **All quotes and code blocks below are byte-exact from the
  markdown endpoint** unless explicitly attributed otherwise.

## Extracted Claims

### Claim 1: LiteLLM attaches a per-call cost figure to **every** call and documents exactly one accessor for it — `response._hidden_params["response_cost"]`, a key on a dict named `_hidden_params` — giving the SDK a cost handle that is neither the response `usage` object nor the `completion_cost` estimator
- **Evidence**: A standalone sentence immediately after the page's
  default-usage sentence, followed by the page's only demonstration: a
  `litellm.completion(...)` call whose last statement is
  `print(response._hidden_params["response_cost"])`.
- **Confidence**: settled that the field and this accessor are documented
  (first-party, and `response_cost` is stated unconditionally). The
  *interpretation* — that this is a third metering path — is our reading, and
  the gaps in it are in Claim 11.
- **Quote**: "LiteLLM returns `response_cost` in all calls."
- **Quote**: `print(response._hidden_params["response_cost"])`
- **Our assessment**: This is the most consequential single line on the page for
  Ch02, and it is under-sold by the page itself. The corpus already distinguishes
  two metering paths — payload `usage` versus local estimation
  (`docs-litellm-token-usage-helpers.md` **Claim 5**, **Claim 4**) — and the
  streaming note establishes that path (i) needs
  `stream_options={"include_usage": True}` on streamed traffic
  (`docs-litellm-streaming-token-usage.md` **Claim 1**). `response_cost` is a
  third surface, and it is the only one the page says is present
  unconditionally, which makes it the natural read for a per-call billing hook.
  Three cautions belong with it, in order of severity:
  1. **`_hidden_params` is by name an internal channel.** The corpus's other
     response-object fields are documented as ordinary attributes
     (`response.response_ms`, `docs-litellm-completion-output.md` **Claim 7**);
     this one is documented only as a subscript into a private dict, and the page
     gives no typed interface, no stability statement, and no
     public-API alternative. The guide should cite it as *what the vendor
     documents*, never as a stable contract to depend on.
  2. **The page's one example is a stub.** The demonstration passes
     `mock_response="Hello world"`, so the only worked instance of "in all
     calls" is a call that by definition incurs no provider cost. The
     universal claim is asserted, never exercised.
  3. **Unqualified "in all calls" carries no error contract.** The page does not
     say what the value is when the model is absent from the map, on a failed
     call, on a fallback attempt, or on a streamed response — precisely the
     cases the corpus's incident record shows are silent
     (`failure-litellm-model-cost-map-silent-fallback.md`, Symptom 2: cost
     tracking "silently returned `cost=0`"). A logger must branch on presence
     rather than assume a float.

### Claim 2: The page's own hyperlink resolves `api.litellm.ai` to `https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json` — so "live list from api.litellm.ai" and the old page's "community resource" are **two names for one artifact**, and the vendor's two live pages disagree only about which end of it to name
- **Evidence**: The `api.litellm.ai` bullet links "all supported models" to the
  GitHub JSON, and the banner sentence immediately below it links "This is a
  community maintained list" to the **same** URL. The old page
  (`https://docs.litellm.ai/token_usage`, HTTP 200, re-fetched this session)
  names "our model_cost map which can be found in `__init__.py` and also as a
  `community resource`" — a packaged location plus the same community file.
- **Confidence**: settled for the link targets (both read directly from the
  page's markdown this session). The identification of the two names is
  arithmetic on those URLs.
- **Quote**: "`api.litellm.ai`: Live token + price count across [all supported models](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json)."
- **Quote**: "📣 [This is a community maintained list](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json). Contributions are welcome! ❤️"
- **Our assessment**: This is the load-bearing finding for the whole page, and it
  cuts in a specific direction: the two pages are **not** describing two pricing
  maps, so the corpus does not need to choose one. But it does not retire the
  disagreement, because *neither page describes the fetch*. The old page names
  the packaged location; the new page names the served endpoint; the only source
  in the corpus that describes the mechanism connecting them is
  `failure-litellm-model-cost-map-silent-fallback.md` ("LiteLLM fetches the
  latest version from `main` at import time; on fetch failure, it falls back to
  a local backup bundled with the package"). Reconciliation therefore requires a
  third source, which is why **#1591 is filed** rather than resolved here. What
  this note can state without a verdict: `api.litellm.ai` is LiteLLM's name for
  the serving endpoint of the same community-maintained JSON file, and
  `__init__.py` holds its packaged copy.

### Claim 3: `LITELLM_LOCAL_MODEL_COST_MAP` is documented as the opt-out of a **hosted pull**, with the motivation stated as network egress and the cost stated as package upgrades — which establishes that the default path reaches out to the network on LiteLLM's own account
- **Evidence**: A bolded section heading, one sentence of motivation, a
  single-line shell export, and one sentence of consequence.
- **Confidence**: settled (verbatim first-party documentation of the env var and
  its stated tradeoff).
- **Quote**: "Don't pull hosted model_cost_map"
- **Quote**: "If you have firewalls, and want to just use the local copy of the model cost map, you can do so like this:"
- **Quote**: "Note: this means you will need to upgrade to get updated pricing, and newer models."
- **Our assessment**: Read as a set, the three fragments triangulate the default
  path in a way none of them states alone: the heading says *hosted*, the body
  says *firewalls*, the note says *upgrade*. An escape hatch whose stated reason
  is a firewall is evidence that the thing being escaped is a network call — so
  **`api.litellm.ai` is a runtime egress dependency of LiteLLM's metering path on
  the default configuration.** That belongs in the dependency-inventory pattern
  the corpus already has: `failure-litellm-model-cost-map-silent-fallback.md`
  **Lesson 5** prescribes cataloging every external dependency with its impact
  and fallback, and its own catalog table lists "Model cost map (GitHub) /
  Cost tracking for newer models / Local backup (now with warning)". This page
  adds the SDK-side name (`api.litellm.ai`) and the SDK-side switch, and it
  supplies the security-flavored reason a firewall team would care about. Note
  also the *shape* of the tradeoff, which is the part that generalizes: pinning
  to local buys egress-predictability and pays in **pricing freshness and new-model
  coverage** — and the second half is enforced by the package release train, so
  the cost of a firewall decision is a permanently drifting cost map.
  (`LITELLM_LOCAL_MODEL_COST_MAP` itself is already in four notes and in
  `guide/05-llm-ops-reliability.md:278-280`; per triage, only the delta above is
  extracted here. The **register_model URL form** — Claim 4 — is the documented
  alternative that does *not* require this pin.)

### Claim 4: `register_model` is a **runtime, in-process write** to the same process-global pricing dict, accepting either an inline cost dictionary or a URL to a hosted JSON blob, and returning the updated dictionary — the corpus's first coverage of a supported way to own the pricing source
- **Evidence**: A one-line helper description, then a worked section with an
  explicit input/output contract, a "Dictionary" example, and a "URL for json
  blob" example.
- **Confidence**: settled for the documented surface (both input forms, the
  documented output, and the mutation of `litellm.model_cost` are stated). The
  interaction with the proxy's reload endpoint is **undocumented** — see Claim 11
  and Open Questions.
- **Quote**: "`register_model`: This registers new / overrides existing models (and their pricing details) in the model cost dictionary."
- **Quote**: "Input: Provide EITHER a model cost dictionary or a url to a hosted json blob"
- **Quote**: "Output: Returns updated model_cost dictionary + updates litellm.model_cost with model details."
- **Our assessment**: Two things here, one obvious and one not.
  The obvious one: `register_model` is *the same map* the corpus's stale-map
  incident is about, writable at runtime rather than only at import. So the
  incident's remediation vocabulary gains an option it did not have — you can now
  register the missing model in-process instead of waiting for a package upgrade
  or a cost-map reload. That directly complements the enablement pattern in
  `guide/05-llm-ops-reliability.md` §"Model enablement and the cost-map reload
  pattern" and the Day-0 notes' `LITELLM_LOCAL_MODEL_COST_MAP=true` caveat
  (`blog-litellm-claude-opus-4-8-day-0.md` **Claim 10**;
  `blog-litellm-claude-fable-5-day-0.md` **Claim 10**).
  The non-obvious one is the **URL form**, and it is the more useful of the two:
  `litellm.register_model(model_cost="https://…/model_prices_and_context_window.json")`
  points the cost map at *any* hosted blob. That is the egress-control answer
  that does **not** cost pricing freshness — an air-gapped or
  vendor-restricted team can host the community JSON internally and still receive
  upstream updates on its own schedule. `LITELLM_LOCAL_MODEL_COST_MAP=True` forces
  a binary choice (no egress *or* upgrade for freshness); `register_model(url=…)`
  removes it. The page does not say whether the URL is fetched once at
  registration or re-fetched, nor how a fetch failure is handled — and given
  this corpus's incident record, "and what happens when that URL 404s on the
  next boot" is the first question an SRE should ask, not a hypothetical.

### Claim 5: `model_cost` returns the whole pricing dictionary, and the page documents exactly three keys per model — `max_tokens`, `input_cost_per_token`, `output_cost_per_token` — making the pricing table simultaneously the context-window authority
- **Evidence**: The helper bullet plus the Example 8 section's single "Output:"
  line and its `print` with an inline comment showing the dict shape.
- **Confidence**: settled for the three documented keys and the printed shape.
  The **completeness** of that list is contradicted by the page itself — see
  Our assessment.
- **Quote**: "`model_cost`: This returns a dictionary for all models, with their max_tokens, input_cost_per_token and output_cost_per_token. It uses the `api.litellm.ai` call shown below."
- **Quote**: "Output: Returns a dict object containing the max_tokens, input_cost_per_token, output_cost_per_token for all models on [community-maintained list](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json)"
- **Quote**: `print(model_cost) # {'gpt-5.6-luna': {'max_tokens': 128000, 'input_cost_per_token': 2e-07, 'output_cost_per_token': 1.2e-06}, ...}`
- **Our assessment**: Two things. First, the operational point: **`max_tokens`
  living in the pricing map means the cost map is also the context-window
  authority.** That is the same single-source-of-truth property
  `docs-litellm-completion-prompt-caching.md` **Claim 11** documents for
  capability probing ("This checks our maintained [model info/cost map]"), seen
  from the other side — so a cost map that is stale, overridden, or replaced is
  *simultaneously* a stale price list and a stale context-window list, and one
  `register_model` override fixes both at once whether or not that is intended.
  Worth stating in the guide explicitly; nothing in the corpus states it.
  Second, a same-page inconsistency worth recording: the three-key list is not the
  real entry shape. The page's own `register_model` example (Claim 4) passes
  `litellm_provider` and `mode` alongside the three pricing keys, and the corpus
  has direct evidence of further keys in the same file
  (`supports_prompt_cache_breakpoint`, per `docs-litellm-completion-prompt-caching.md`
  **Claim 10**). So `model_cost`'s documented "Output" is a **partial view** of
  each entry, and the `...` in the printed sample is the page declining to
  publish the schema. Treat three keys as the *stable core*, not the contract;
  do not build a validator that asserts "only these three keys".

### Claim 6: `get_max_tokens` is the documented single accessor for a model's context ceiling, but the page states no behavior for an unmapped model and delegates the model inventory to a differently-named symbol (`litellm.model_list`) that it never documents
- **Evidence**: The helper bullet, then Example 7's input/output contract and a
  two-line snippet whose inline comment is the page's only worked output.
- **Confidence**: settled for the accessor's existence and the example value.
  The unmapped-model case is an **absence** — graded as such, not as a claim
  about behavior.
- **Quote**: "`get_max_tokens`: This returns the maximum number of tokens allowed for the given model."
- **Quote**: "Input: Accepts a model name - e.g., gpt-5.6-luna (to get a complete list, call litellm.model_list)."
- **Quote**: "Output: Returns the maximum number of tokens allowed for the given model"
- **Quote**: `print(get_max_tokens(model)) # Output: 128000`
- **Our assessment**: This is the helper an SRE wants *before* a call, to avoid a
  provider-side context-window error, and it is exactly the helper whose failure
  mode the page will not state. Given this corpus's evidence — the stale-map
  incident where an unmapped lookup yields a zero cost and **no error**
  (`failure-litellm-model-cost-map-silent-fallback.md`, Symptom 2) — the
  pre-flight check must not assume `get_max_tokens("my-new-model")` raises.
  Whether it returns `None`, raises, or returns `0` is undetermined here, and
  that is a question worth thirty seconds in a REPL before relying on it as a
  guard. The `litellm.model_list` pointer is a second, smaller gap: it is the
  page's only pointer to "the complete list", it uses a **plural** name where
  every other symbol on the page is singular (`model_cost`), and it is documented
  nowhere in the corpus. An operator told to call `litellm.model_list` to
  enumerate models is relying on an undocumented symbol; `model_cost` — the dict,
  plural in content, singular in name — is the documented inventory.

### Claim 7: The tokenizer surface is documented twice on the same page with **two different family lists** — the helper index names five supported families (OpenAI, Cohere, Anthropic, Llama2, Llama3), the two worked examples name four (anthropic, cohere, llama2, openai)
- **Evidence**: The `create_pretrained_tokenizer` / `create_tokenizer` bullet
  enumerates five families; the Example 1 and Example 2 prose lines each
  enumerate four, and neither mentions Llama3. Both example snippets call
  `encode(model="gpt-5.6-luna", …)`, consistent with the four-family list and
  not the five.
- **Confidence**: settled as a **documentation** inconsistency — all three strings
  are on the page, verbatim, and mutually inconsistent. Whether Llama3 tokenizers
  actually work is not determined by this page.
- **Quote**: "`create_pretrained_tokenizer` and `create_tokenizer`: LiteLLM provides default tokenizer support for OpenAI, Cohere, Anthropic, Llama2, and Llama3 models. If you are using a different model, you can create a custom tokenizer and pass it as `custom_tokenizer` to the `encode`, `decode`, and `token_counter` methods."
- **Quote**: "Encoding has model-specific tokenizers for anthropic, cohere, llama2 and openai. If an unsupported model is passed in, it'll default to using tiktoken (openai's tokenizer)."
- **Quote**: "Decoding is supported for anthropic, cohere, llama2 and openai."
- **Our assessment**: The *policy* the page states is the part that matters
  operationally, and it is a good one: **an unsupported model silently degrades to
  tiktoken** rather than erroring. That is the same estimator-divergence hazard
  `docs-litellm-token-usage-helpers.md` **Claim 2** already records for
  `token_counter` (tiktoken fallback ⇒ local counts diverge from
  provider-reported usage), now stated for the raw `encode`/`decode` pair — so a
  team computing token counts or costs by hand inherits the same divergence, and
  inherits it *silently*. The five-vs-four discrepancy is the page telling you it
  has not been reconciled with itself; treat the family list as "whatever is
  bundled for the installed version" and **verify the one family you depend on**
  rather than trusting either list. Nothing else in the corpus covers `encode` or
  `decode` (grep-verified this session: zero hits in `source-notes/` and `guide/`).

### Claim 8: `create_pretrained_tokenizer` takes a **HuggingFace repository id**, making tokenizer construction a documented external download — and the page offers no offline, revision-pinned, or cached alternative
- **Evidence**: Example 4 is the only section on the page with **no prose at
  all** — a code block and two comments. The first call passes the repo id
  `"Xenova/llama-3-tokenizer"`; the second reads a local `tokenizer.json`.
- **Confidence**: settled for the API shape and the repo-id argument. The
  *download-at-construction* reading is our inference from what a HuggingFace
  repo id is, flagged as such; the page documents no network behavior, no
  revision pinning, no cache, and no offline mode.
- **Quote**: `custom_tokenizer_1 = create_pretrained_tokenizer("Xenova/llama-3-tokenizer")`
- **Our assessment**: Two operational consequences, one of them a sharp contrast
  with the page's own advice three sections later. The page tells a
  firewall-restricted team to pin the *cost* map locally because of network
  egress — and then, with no comment on the difference, documents the *tokenizer*
  path as taking a HuggingFace repo id. A team that set
  `LITELLM_LOCAL_MODEL_COST_MAP=True` to satisfy a firewall has **not** thereby
  satisfied it for tokenizers: an uncached `create_pretrained_tokenizer(repo_id)`
  in a startup path is an egress dependency on `huggingface.co`, on a
  community-maintained conversion, with no documented pin to a revision — so the
  tokenizer that prices your tokens is not version-locked. The corpus's only
  statement on HuggingFace as a dependency is the incident's external-dependency
  table row ("HuggingFace model API / HF provider calls fail / None"), which
  covers provider calls, not tokenizer artifacts; this page adds a second,
  undocumented one. The second consequence is the smaller but real one: the
  tokenizer is the thing that produces the token counts every cost figure is
  computed from, so an unpinned tokenizer means an unreproducible cost figure —
  the same "non-hermetic config is non-replayable and non-rollable" property
  `guide/05-llm-ops-reliability.md` states two hundred lines above this note's
  guide home. Recommendation for the guide: if you build a custom tokenizer,
  vendor the `tokenizer.json` into your own artifact and use `create_tokenizer`
  (the second, local form) rather than the repo-id form, and treat the choice as
  part of the deployment's hermeticity story.

### Claim 9: `completion_cost` documents **two input forms** — a `completion()` response object *or* prompt/completion strings — and the page never states whether the response-object form reads the response's reported usage or still re-tokenizes and prices locally, which is the open question that decides whether the corpus's "no provider-side reconciliation" statement holds
- **Confidence**: settled that both forms exist and that the page is silent on
  the accounting basis. The consequence for the corpus's existing claim is our
  reading and is graded as an open question, not a finding.
- **Evidence**: Example 6 is the only section with a typed input/output contract,
  and it is split into two labeled subsections — "**litellm.completion()**" and
  "**prompt + completion string**" — with a different call shape in each. The
  first passes `completion_response=response` where `response` is a real
  `bedrock/us.anthropic.claude-sonnet-5` completion; the second passes
  `prompt="Hey!"` and `completion="How's it going?"`. The page says nothing about
  what changes between them.
- **Quote**: "Input: Accepts a `litellm.completion()` response **OR** prompt + completion strings"
- **Quote**: "Output: Returns a `float` of cost for the `completion` call"
- **Quote**: `cost = completion_cost(completion_response=response)`
- **Quote**: `cost = completion_cost(model="bedrock/us.anthropic.claude-sonnet-5", prompt="Hey!", completion="How's it going?")`
- **Our assessment**: This is the sharpest thing the page does *not* say, and it
  matters because the corpus has already published a rule built on the other
  answer. `docs-litellm-token-usage-helpers.md` **Claim 4** records
  `completion_cost` as composing `token_counter` and `cost_per_token` — i.e.
  re-tokenizing locally and pricing from the cost map — and
  `guide/05-llm-ops-reliability.md:1227-1235` has generalized that into guide
  prose: the helpers "compute usage and USD locally from the running package's
  bundled `model_cost` map, with **no provider-side reconciliation**". That claim
  is verified for the **string** form, where there is nothing else it could read.
  The **response** form has a `usage` object available, and if LiteLLM uses it,
  then `completion_cost(completion_response=…)` is a *provider-reconciled*
  figure while `completion_cost(prompt=…, completion=…)` is a local estimate —
  two different accuracies behind one function name, selected by argument shape.
  The page gives no basis to choose, and this note does not guess: the honest
  statement is that the corpus's "no provider-side reconciliation" is verified
  **only** for the string form and is **unverified** for the response form. The
  cheap resolution is empirical — call it both ways on one real request and
  compare against the invoice. Until someone does, the guide should either
  restrict its "estimator output" label to the string form or hedge it. Related:
  the page's response-object form is the SDK counterpart of the proxy's
  `x-litellm-response-cost` header, which
  `docs-litellm-completion-prompt-caching.md` **Claim 12** already grades as "a
  map-derived estimate" — so if the two agree, the response form is also
  map-derived, and if they disagree on a cache-heavy request, the header is the
  one to distrust. That comparison is a one-request experiment and would settle
  both questions at once.

### Claim 10: Three of the page's nine examples are not runnable as printed, and the `token_counter` example — the page's *only* illustration of a message-dict input — transposes the `role` key and value, so it would not be a valid chat message
- **Confidence**: settled as a **documentation** finding; every defect below is
  verified character-for-character against the page's own markdown this session,
  and where possible against the older page's version of the same example.
- **Evidence**: (a) Example 3 writes
  `messages = [{"user": "role", "content": "Hey, how's it going"}]` — key `"user"`,
  value `"role"`, which is the inverse of the OpenAI shape. (b) Example 4 calls
  `json.load(f)` and `json.dumps(...)` with no `import json` in the block.
  (c) The `response_cost` block imports the symbol `completion` but then calls
  `litellm.completion(...)`, and the `completion_cost(completion_response=…)`
  block references a `messages` variable it never defines. (d) The **older**
  page's `token_counter` example has the correct form —
  `messages = [{"role": "user", "content": "Hey, how's it going"}]` — so (a) is a
  regression introduced on this page, not a shared legacy typo.
- **Quote**: `messages = [{"user": "role", "content": "Hey, how's it going"}]`
- **Quote**: `from litellm import create_pretrained_tokenizer, create_tokenizer` (Example 4's only import line — the block's next two statements are `json_data = json.load(f)` and `json_str = json.dumps(json_data)`)
- **Our assessment**: Low operational stakes individually, high collectively, and
  worth recording for the reason
  `docs-litellm-mock-requests.md` **Claims 6 and 8** give: a page whose examples
  have never been run is a page whose *prose* is the only thing you can trust,
  so the prose gets audited harder. (a) is the one to notice — it is the page's
  only example of how to hand `messages` to a LiteLLM helper, and it teaches the
  wrong shape, in the one place an SRE is most likely to copy from. (d) is what
  makes it a defect rather than a stylistic quirk: the correct line exists in the
  vendor's other page, published simultaneously, for the same helper. Combined
  with the five-vs-four tokenizer lists (Claim 7), the three-key `model_cost`
  schema that its own `register_model` example contradicts (Claim 5), and the
  `"in all calls"` claim demonstrated only on a `mock_response` stub (Claim 1),
  the page-level conclusion is specific and usable: **the prose is authoritative
  and the examples are not** — which is exactly the corpus's existing precedent
  from the promptfoo and mock_requests notes, now established for this page.

### Claim 11: The page documents **no failure behavior for any function on it** — not for `cost_per_token`, `model_cost`, `get_max_tokens`, `response_cost`, or `register_model` — so every unmapped-model, unreachable-URL, and malformed-model-name case is undocumented at the exact point where the corpus has a recorded history of silence
- **Confidence**: settled (that the documentation is silent); graded explicitly
  as an absence, per MINER.md §2a, with the corpus's incident record used as the
  reason it matters rather than as evidence of what the code does.
- **Evidence**: A complete read of the page's markdown yields no error-handling
  sentence, no `try`/`except`, no "if the model is not found" clause, no `None`
  return, and no raise. The single unconditional statement about a
  missing-entry situation is Claim 1's "in all calls" — which is about presence,
  not about value. Verified absences on this page: behavior for an unmapped
  model in `get_max_tokens`; behavior for an unreachable `model_cost=` URL in
  `register_model`; the value of `response_cost` on a failed or fallback call;
  whether `register_model` persists across `POST /reload/model_cost_map`; and
  whether the model-cost map is re-read after registration.
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This claim exists because the gap is not neutral. This
  corpus holds a root-caused vendor incident whose entire impact was that a
  missing map entry produced a **zero cost and no error**
  (`failure-litellm-model-cost-map-silent-fallback.md`, Symptoms 1–3: silent
  fallback, "no warning was logged", and the map being "not in the request
  path"), with **Lesson 3** concluding that out-of-band functions need their own
  probes because request success metrics cannot see them. Here, the *reference
  page* for those same functions repeats none of that — so a team writing a spend
  pipeline from this page alone inherits the incident's failure mode with no
  warning in the documentation to catch it. The guide rule that follows: every
  LiteLLM cost/context read used for a gate, a budget, or a dashboard needs an
  explicit **presence-and-plausibility check** (is the value non-`None`, and is
  the implied price per token in a sane range for the model?), because LiteLLM's
  documented behavior on the unhappy path is not a guarantee and its documented
  history is silence. Do **not** read this claim as "LiteLLM returns garbage on
  errors" — it is "the docs promise nothing, and we have previously been burned
  assuming they did."

## Concrete Artifacts

All blocks below are byte-exact from `https://docs.litellm.ai/docs/completion/token_usage.md`
(the page's own raw markdown endpoint, which preserves line breaks, indentation,
and trailing whitespace). Inline-code spans are reproduced as they read in the
source.

**Front matter, verbatim** — the `last_updated` date, the canonical URL, and the
two-entry `related:` list:

```yaml
title: "Completion Token Usage & Cost"
url: "/docs/completion/token_usage"
canonical_url: "https://docs.litellm.ai/docs/completion/token_usage"
type: "docs"
last_updated: "2026-10-03"
summary: "By default LiteLLM returns token usage in all completion requests (See here)"
related:
  - "/docs/caching/all_caches"
  - "/docs/exception_mapping"
```

**The `response_cost` example, verbatim** (Claim 1) — note the `mock_response`
stub and that `litellm.` is used while only the symbol `completion` was imported:

```python
from litellm import completion 

response = litellm.completion(
            model="gpt-5.6-luna",
            messages=[{"role": "user", "content": "Hey, how's it going?"}],
            mock_response="Hello world",
        )

print(response._hidden_params["response_cost"])
```

**`register_model` — both documented input forms, verbatim** (Claim 4):

```python
import litellm

litellm.register_model({
        "gpt-5.6-terra": {
        "max_tokens": 128000, 
        "input_cost_per_token": 0.000002, 
        "output_cost_per_token": 0.000012, 
        "litellm_provider": "openai", 
        "mode": "chat"
    },
})
```

```python
import litellm

litellm.register_model(model_cost=
"https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json")
```

**The hosted-pull opt-out, verbatim** (Claim 3) — heading, rationale, export, and
consequence, as they appear in that order on the page:

```markdown
**Don't pull hosted model_cost_map**  
If you have firewalls, and want to just use the local copy of the model cost map, you can do so like this:
```bash
export LITELLM_LOCAL_MODEL_COST_MAP="True"
```

Note: this means you will need to upgrade to get updated pricing, and newer models.
```

**`get_max_tokens`, verbatim** (Claim 6) — the `# Output: 128000` comment is the
page's only worked value for the context ceiling:

```python 
from litellm import get_max_tokens 

model = "gpt-5.6-luna"

print(get_max_tokens(model)) # Output: 128000
```

**`model_cost`, verbatim** (Claim 5) — the `...` is the source's own elision:

```python 
from litellm import model_cost 

print(model_cost) # {'gpt-5.6-luna': {'max_tokens': 128000, 'input_cost_per_token': 2e-07, 'output_cost_per_token': 1.2e-06}, ...}
```

**The custom-tokenizer pair, verbatim** (Claim 8) — `json` is used and never
imported, and there is no prose anywhere in this section:

```python
from litellm import create_pretrained_tokenizer, create_tokenizer

# get tokenizer from huggingface repo
custom_tokenizer_1 = create_pretrained_tokenizer("Xenova/llama-3-tokenizer")

# use tokenizer from json file
with open("tokenizer.json") as f:
    json_data = json.load(f)

json_str = json.dumps(json_data)

custom_tokenizer_2 = create_tokenizer(json_str)
```

**The two `completion_cost` input forms, verbatim** (Claim 9) — `messages` is
referenced in the first and never defined in it:

```python
from litellm import completion, completion_cost

response = completion(
            model="bedrock/us.anthropic.claude-sonnet-5",
            messages=messages,
            request_timeout=200,
        )
# pass your response from completion to completion_cost
cost = completion_cost(completion_response=response)
formatted_string = f"${float(cost):.10f}"
print(formatted_string)
```

```python
from litellm import completion_cost
cost = completion_cost(model="bedrock/us.anthropic.claude-sonnet-5", prompt="Hey!", completion="How's it going?")
formatted_string = f"${float(cost):.10f}"
print(formatted_string)
```

**The transposed message dict, verbatim** (Claim 10) — for comparison, the
**older** page's `token_counter` example, fetched this session from
`https://docs.litellm.ai/token_usage`, carries the correct form:

```python
from litellm import token_counter

messages = [{"user": "role", "content": "Hey, how's it going"}]
print(token_counter(model="gpt-5.6-luna", messages=messages))
```

```python
# from https://docs.litellm.ai/token_usage (the older, still-live page; rendered HTML, whitespace normalized)
messages = [{"role": "user", "content": "Hey, how's it going"}]
print(token_counter(model="gpt-3.5-turbo", messages=messages))
```

**The two provenance sentences for `cost_per_token`, side by side** (Claim 2 /
contradiction **#1591**) — same function, same vendor, both pages live as of
2026-10-04:

```markdown
# https://docs.litellm.ai/docs/completion/token_usage  (this source)
- `cost_per_token`: This returns the cost (in USD) for prompt (input) and completion (output) tokens. Uses the live list from `api.litellm.ai`.
```

```markdown
# https://docs.litellm.ai/token_usage  (the older page, mined as #1300)
- `cost_per_token`: This returns the cost (in USD) for prompt (input) and completion (output) tokens. It utilizes our model_cost map which can be found in __init__.py and also as a community resource.
```

**Quotation caveat on the two comparison blocks above and the `/token_usage`
snippet immediately above them**: the older page was read from its **rendered
HTML** (`https://docs.litellm.ai/token_usage`, HTTP 200), because its raw-markdown
variant `/token_usage.md` returns 404. Rendered HTML cannot be searched for
inline-code or link markup, so for that page only, backticks around `__init__.py`
and `community resource` are **not** asserted here — the wording is given flat,
matching the quotation convention already used in
`docs-litellm-token-usage-helpers.md` **Claim 3** (which quotes the same
sentence). Everything else in this note is byte-exact from the `.md` endpoint of
the page it belongs to.

## Cross-References

**Candidates from `miner-related-notes.md`** (read before Cross-References per
MINER.md §4; all ten pre-computed candidates cited or dismissed below). The
retrieval was lexical against the page URL and returned generic
`/docs/completion/*` LiteLLM neighbors — the notes that actually matter for this
page (`docs-litellm-token-usage-helpers.md`, the cost-map failure note, the
Day-0 enablement notes) were **absent** from the candidate list and were found by
searching `source-notes/` directly, which MINER.md §4 explicitly permits.

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**. Batch JSONL rate
  limiting, per-record TPM reservations, `batch_enqueued_token_limit`. Shares only
  the vocabulary of token counting. It is in fact the useful *counterexample*:
  there, LiteLLM computes token counts before forwarding and enforces on them;
  here, the SDK hands the counting and the pricing to the caller with no
  enforcement path.
- `source-notes/docs-litellm-completion-input-params.md` — **Dismissed**. The
  request-parameter reference (supported-params gate, `max_retries`/`num_retries`
  mismatch, `context_window_fallback_dict`, 600-second default timeout). The
  `custom_tokenizer` documented on this page is a parameter to `encode` /
  `decode` / `token_counter`, **not** to `completion()`, so the input-params note's
  kwarg pass-through rules do not apply and no claim here corroborates or
  extends it. (Adjacency only: both are SDK function references on the same
  `/docs/completion/` subtree.)
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**. Bedrock native
  Invoke passthrough routing and the bearer-token auth swap. Its model alias /
  `config.yaml` registration is unrelated to the process-global pricing dict this
  page documents.
- `source-notes/docs-litellm-mock-requests.md` — **Cited** (Corroborates,
  Extends). **Claim 2** (the documented mock response carries a `usage` object
  whose three token fields are all `null`) and **Claim 9** (the vendor frames the
  stub as cost-avoidance, never coverage) are the corpus's existing statement of
  the hazard this page's `response_cost` handle walks into: the `response_cost`
  example on this page is itself a `mock_response` call, so the one worked
  instance of a per-call cost handle is a call whose `usage` is null by
  construction and whose cost is zero. That note's Cross-References already names
  `docs-litellm-token-usage-helpers.md` **Claim 4** as the recovery path for
  null-usage responses; this page's `response_cost` is a third option the corpus
  did not have.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Cited**
  (Corroborates). **Claim 2**: advisor spend is split out of the top-level
  `usage` object, top-level `usage` reflects executor tokens only, and advisor
  tokens are reachable only via `usage.iterations[]`. That is the corpus's proof
  that **LiteLLM's `usage` object under-reports total spend by construction** on
  a first-class feature — which is precisely why a separate per-call cost handle
  matters, and why Claim 1's "in all calls" is a meaningful upgrade over reading
  `usage` for a spend total.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **Cited** (Corroborates, as
  a contrast, following the precedent set in
  `docs-litellm-mock-requests.md`). **Claim 3** makes a gateway-configured
  per-agent cost "a gateway-declared synthetic charge … with no documented
  linkage to the agent's measured token usage or upstream model cost". That is
  the *declared* position on the axis this page occupies: a dollar figure that is
  not a measurement. `cost_per_token` / `completion_cost` are the *derived*
  position (a measurement-shaped number computed from a price table), and
  `response_cost` is a fourth position the corpus had not separated — computed
  inside the SDK from the same table. Neither equals an invoice.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**.
  Transcription-endpoint fallbacks and `mock_testing_fallbacks`. No cost-map or
  tokenizer surface.
- `source-notes/docs-litellm-completion-message-trimming.md` — **Cited**
  (Corroborates). **Claim 1**: `trim_messages()` is "a client-side, in-process,
  pre-call helper whose entire documented contract is a single inequality — the
  page states no return type, no error mode, and no guarantee beyond it". That is
  the same documentation posture as this page's helper surface (Claim 11) and the
  same class of helper — in-process, before the call, no error contract — so the
  two notes together establish that **the LiteLLM SDK's pre-call helpers are
  documented as pure functions with unspecified unhappy paths.** Its **Claim 5**
  (the `max_tokens` parameter-name collision between the trim helper's
  input-payload cap and OpenAI's output-token `max_tokens`) is a precedent for the
  kind of parameter-ambiguity finding this page supports: `max_tokens` here lives
  inside a *pricing* dict rather than a request, a third meaning.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**. A2A
  agent-loop `max_iterations` / `max_budget_per_session` caps and the
  `"type": "budget_exceeded"` 429 shape. Enforcement and observability of a
  budget; no cost-map write path or tokenizer surface. (Its Lesson-5 dependency
  framing is echoed in Claim 3, but the note is not evidence for anything here.)
- `source-notes/docs-litellm-bedrock-converse.md` — **Dismissed**. Bedrock
  native Converse passthrough routing and the End-user-Tracking ❌ row. Different
  endpoint family, no cost-map or tokenizer content.

**Additional cross-references found by searching `source-notes/` and `guide/`
directly** (all verified per MINER.md §4b before citation):

- `source-notes/docs-litellm-token-usage-helpers.md` (#1300) — **primary
  overlap**, **Cited** (Extends, and the Con*tradicts* target of **#1591**).
  Verified this session by re-reading the note and re-fetching its `source_url`:
  **Claims 1–5** cover `token_counter`, `cost_per_token`, `completion_cost`, and
  the payload-vs-estimator distinction. This page is a strict superset of that
  page's helper list (three shared, six added) and its **Claim 3** carries the
  other half of contradiction **#1591** — the "bundled `__init__.py`" provenance
  reading the guide has published. This note does not re-extract those three
  helpers, per the triage's bounding.
- `source-notes/docs-litellm-completion-output.md` (#1540) — **Cited**
  (Corroborates). **Claim 7** (`response.response_ms` as a per-call float exposed
  directly on the response object, documented only by a single `print`) is the
  structural precedent for Claim 1: the corpus already accepted one
  number-on-the-response-object field, with the same caveat about undocumented
  units and behavior on error. **Claim 10**
  (`general_settings: always_include_stream_usage: true` force-injecting the
  streaming opt-in at the gateway) is the reason `response_cost` is worth having
  on streamed traffic, where `usage` is absent by default. **Claim 3** (the
  response is readable as both dict and class) is why `response._hidden_params`
  being a *dict subscript* rather than an attribute matters to a consumer.
- `source-notes/docs-litellm-streaming-token-usage.md` (#1286) — **Cited**
  (Corroborates, Extends). **Claim 1** (streamed usage is opt-in via
  `stream_options={"include_usage": True}`, so a streamed request is usage-blind
  by default) is the precondition that makes Claim 1's per-call handle valuable;
  **Claim 2** (the usage chunk arrives before `data: [DONE]` with empty `choices`)
  is the wire-level reason a logger on a stream has no single response object to
  read a cost off — and, stated negatively, the reason `_hidden_params` on the
  final chunk may be the only per-call cost signal available. This page restates
  the non-streamed default ("By default LiteLLM returns token usage in all
  completion requests"), which is consistent with that note's reading and adds no
  conflict. The page contains **no** streaming content — `stream`,
  `stream_options`, and `include_usage` return zero hits in its markdown.
- `source-notes/docs-litellm-completion-prompt-caching.md` (#1556) — **Cited**
  (Corroborates, Extends). **Claim 12** (`x-litellm-response-cost` as the proxy
  response header, graded "a map-derived estimate" so "the provider invoice
  remains the only ground truth") is the same quantity this page documents on the
  SDK object — and the natural experiment to settle Claim 9's open question.
  **Claim 11** (`supports_prompt_caching()` answering from "our maintained
  model info/cost map", so a `False` is ambiguous between unsupported and
  not-yet-added) is the single-source-of-truth property Claim 5 extends: the cost
  map is the capability registry and the context-window registry as well as the
  price list. **Claim 10** (`supports_prompt_cache_breakpoint: true` as a cost-map
  key) is direct evidence that the real map carries more than the three keys this
  page's `model_cost` "Output" line promises.
- `source-notes/failure-litellm-model-cost-map-silent-fallback.md` (#632) —
  **Cited by section name**, not claim number, per MINER.md §4b rule 4 (this
  note's claims are `Symptom 1-3` / `Root Cause` / `Lesson 1-5` headings, not
  `### Claim N`). **Symptom 2** ("Cost tracking silently returned `cost=0`") and
  **Symptom 3** ("The model cost map is not in the request path") are what
  `register_model` (Claim 4) and `LITELLM_LOCAL_MODEL_COST_MAP` (Claim 3) are
  remedies *and* risk surfaces for. **Lesson 4** names
  `LITELLM_LOCAL_MODEL_COST_MAP=True` as the mechanism for pinning to the local
  copy permanently, and its quoted escape hatch — "Enterprises that require zero
  external dependencies at import time can set `LITELLM_LOCAL_MODEL_COST_MAP=True`
  to skip the GitHub fetch entirely" — is the same egress reason this page gives
  as "If you have firewalls". **Lesson 5** (the dependency-inventory table) is
  where Claim 3's `api.litellm.ai` egress finding belongs. Its **External-dependency
  catalog** artifact also supplies the HuggingFace row that Claim 8 extends.
- `source-notes/blog-litellm-claude-opus-4-8-day-0.md` — **Cited** (Extends).
  **Claim 10**: the Opus 4.8 enablement procedure distinguishes the remote
  cost-map path (reload, no upgrade) from `LITELLM_LOCAL_MODEL_COST_MAP=true`
  ("The cost map is baked into the image, so the Reload button won't reach it.
  Pull v1.88.0-dev.1 or later"). `register_model` (Claim 4) is the SDK-side
  third option this note's guide home does not yet list.
- `source-notes/blog-litellm-claude-fable-5-day-0.md` — **Cited** (Extends).
  **Claim 10**: the same remote-map-vs-baked-map enablement split at
  `v1.89.0-rc.2`. Verified this session; cited to establish that the
  `LITELLM_LOCAL_MODEL_COST_MAP` trade-off this page documents as a one-line
  export is, in practice, the difference between a reload and an image pull on
  the guide's own enablement path.
- `source-notes/blog-litellm-gpt-5-6-sol-terra-luna-day-0.md` — **Cited**
  (Extends). **Claim 6**: GPT-5.6 requires no Docker image upgrade and routes
  through the existing provider config, while its bundled cost tracking requires
  at least a dev-nightly tag "when using `LITELLM_LOCAL_MODEL_COST_MAP=true`" —
  the corpus's sharpest existing statement that *routing* enablement and *pricing*
  enablement are separate, which is exactly the split `register_model` lets an
  operator resolve independently.
- `source-notes/docs-litellm-caching-all-caches.md` (#1431) — **Cited** (only to
  record that it is this page's own `related:` entry and is already mined;
  nothing quoted, no claim cited). Read to confirm the overlap and to avoid a
  duplicate note.
- `source-notes/docs-litellm-caching-hosted-cache.md` (#1432) — **Cited** by
  section name only: it is the corpus's only prior note to name `api.litellm.ai`,
  and it uses the name for a **different** service (the vendor-hosted response
  cache, `Cache(type="hosted")`). Recorded so the Smith does not conflate
  "hosted at api.litellm.ai" (payload storage, a Ch06 egress/residency matter)
  with "hosted pricing list from api.litellm.ai" (a cost-map read dependency, a
  Ch05 availability matter). Same hostname, two unrelated dependencies.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-completion-output.md` **Claim 7** — the
    response-object number field. The corpus already accepted
    `response.response_ms` on the strength of a single `print` with no units
    documented; `response._hidden_params["response_cost"]` is the same class of
    claim, with the added wrinkle that it lives on a private dict.
  - `source-notes/docs-litellm-streaming-token-usage.md` **Claim 1** and
    `source-notes/docs-litellm-completion-output.md` **Claim 10** — the two
    independent reasons a per-call cost handle that does not depend on `usage` is
    operationally valuable: streams are usage-blind by default, and the gateway
    auto-injection that would fix that is itself a deployment flag.
  - `source-notes/docs-litellm-completion-prompt-caching.md` **Claim 11** — the
    cost map as the single registry for capabilities, prices, and (Claim 5) the
    context window. Same-source dependency, three consumers.
  - `source-notes/docs-litellm-anthropic-advisor-tool.md` **Claim 2** — `usage`
    under-reports total spend by construction, so a separate cost handle is not
    redundant.
  - `source-notes/docs-litellm-a2a-cost-tracking.md` **Claim 3** and
    `source-notes/docs-litellm-mock-requests.md` **Claims 2 and 9** — the corpus's
    existing positions on "a dollar figure that is not an invoice". This page
    adds the derived-estimate and per-call-handle positions to that set.
  - `source-notes/docs-litellm-completion-message-trimming.md` **Claim 1** — the
    documented posture of LiteLLM's in-process pre-call helpers: a contract with
    no stated error mode.

- **Contradicts**:
  - **Contradiction [#1591](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1591)
    — filed by this Miner before opening this PR, per MINER.md §4a. Referenced
    here with **no verdict stated**, per §4a step 3.**
    - **Side A**: `docs-litellm-token-usage-helpers.md` (#1300) **Claim 3** —
      `cost_per_token`'s USD "utilizes our model_cost map which can be found in
      `__init__.py` and also as a community resource" — i.e. the packaged dict is
      the authority. `guide/05-llm-ops-reliability.md:1227-1235` has published this
      reading as a rule: the helpers "compute usage and USD locally from the
      running package's bundled `model_cost` map, with no provider-side
      reconciliation … bounded by the installed package's map version".
    - **Side B**: this page — `cost_per_token` "Uses the live list from
      `api.litellm.ai`", `model_cost` "uses the `api.litellm.ai` call shown
      below", and the documented opt-out is to stop pulling the **hosted**
      `model_cost_map`.
    - **Why it is fileable rather than a naming difference**: the two pages are
      live at the same time (both HTTP 200, verified this session), name the same
      function, and describe the *same default path*. Claim 2 establishes they
      are not describing two different maps — the page's own hyperlink resolves
      `api.litellm.ai` to the very `model_prices_and_context_window.json` the old
      page calls the "community resource" — but neither page describes the fetch
      that connects the endpoint to the packaged dict. The only corpus source that
      describes that mechanism is the incident note ("fetches the latest version
      from `main` at import time; on fetch failure, it falls back to a local
      backup bundled with the package"), which means the guide's published word
      "bundled" is doing load-bearing work that rests on **one** of **two** live
      vendor pages and on a blog post about a malformed-JSON incident. Under
      `LITELLM_LOCAL_MODEL_COST_MAP=True` the guide is right; on the default
      path, "bundled" and "live list" give the operator different instructions
      about where to look when a price is wrong.
    - **What is deliberately NOT claimed here**: that the two pages describe
      different pricing systems, or that any cost figure is wrong. #1591 states
      both sides and stops.
  - **Also recorded, not filed as a contradiction** (MINER.md §4a "when NOT to
    file" — these are *conditioning variables* and *documentation defects*, not
    opposing positions on an operational question):
    - `api.litellm.ai` as a **cache backend**
      (`docs-litellm-caching-hosted-cache.md`, #1432, **Claim 1**) versus as a
      **pricing source** (this page) — same hostname, unrelated features. A
      naming collision, not a disagreement; flagged for the Smith so the two are
      never conflated.
    - The intra-page defects in Claims 5, 7, and 10 (three-key `model_cost`
      schema contradicted by its own `register_model` example; five-vs-four
      tokenizer families; a transposed `role` key and two unrunnable snippets).
      MINER.md §4a covers "a source disagrees with itself", but these are
      defects in a vendor reference page's examples, not disagreements between two
      positions on an operational question — the same distinction
      `docs-litellm-mock-requests.md` drew when it declined to file on its
      intra-page inconsistencies. They are recorded as claims and as Guide Impact
      instead.

- **Extends**:
  - `source-notes/docs-litellm-token-usage-helpers.md` (#1300) — six helpers
    added to its three (`encode`, `decode`, `create_pretrained_tokenizer`,
    `create_tokenizer`, `get_max_tokens`, `model_cost`, `register_model`), the
    per-call `response_cost` handle, and the provenance half of #1591. Also
    **Claim 4**'s "no provider-side reconciliation" reading is now
    *conditionally* verified rather than universal (Claim 9).
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` (#632) —
    **Lesson 4** offers `LITELLM_LOCAL_MODEL_COST_MAP=True` as the permanent
    pin; **Claim 4** here adds the runtime write (`register_model`) and its URL
    form, which the incident note could not have recommended because that page
    documents the *failure*, not the *remedy surface*. **Lesson 5**'s dependency
    catalog gains two rows — `api.litellm.ai` for the cost map (Claim 3) and
    HuggingFace repo downloads for custom tokenizers (Claim 8).
  - `source-notes/blog-litellm-claude-opus-4-8-day-0.md` **Claim 10** /
    `blog-litellm-claude-fable-5-day-0.md` **Claim 10** /
    `blog-litellm-gpt-5-6-sol-terra-luna-day-0.md` **Claim 6** — the Day-0
    enablement ladder is reload → image-pull → and now, per this page,
    in-process `register_model`. The corpus's enablement advice assumed the first
    two were the only options; for SDK users they were not the only options, and
    the third has none of the "is it reachable yet?" risk the reload path carries
    (which is why `failure-litellm-wildcard-model-access-desync.md` exists).
  - `source-notes/docs-litellm-completion-prompt-caching.md` (#1556) —
    **Claim 11**'s "answers from our maintained cost map" gains a third consumer
    (`get_max_tokens`, Claim 5/6) and gains a documented *writer*
    (`register_model`), so the map is now read by capability probes, by context
    checks, by price lookups, and written at runtime.
  - `source-notes/docs-litellm-mock-requests.md` (#1523) — its **Claim 2** null-`usage`
    hazard had exactly two documented ways out (read `usage`, or compute
    locally). `response_cost` is a third, and the fact that the vendor's only
    example of it is a `mock_response` call is a small, checkable irony worth
    recording.

- **Novel**: First corpus coverage of all of the following (each grep-verified
  this session across `source-notes/` and `guide/`, zero prior hits):
  **`response_cost`**; **`_hidden_params`**; **`register_model`**;
  **`get_max_tokens`**; **`create_pretrained_tokenizer`**; **`create_tokenizer`**;
  **`custom_tokenizer`**; the bare `encode` / `decode` helpers; and
  **`api.litellm.ai` as a pricing source** (the only prior note naming the
  hostname is `docs-litellm-caching-hosted-cache.md` #1432, for the hosted
  *cache*). Substantively new, beyond the identifiers: (a) a supported
  **runtime write path** to the pricing dict, including a **URL form** that
  removes the egress-versus-freshness tradeoff `LITELLM_LOCAL_MODEL_COST_MAP`
  forces; (b) the vendor's **own confirmation that the default pricing path is a
  hosted pull**, which is the first SDK-side statement of that architecture and
  the trigger for #1591; (c) `max_tokens` as a **pricing-map field**, making the
  cost map the context-window authority; (d) the **`completion_response=` input
  form** of `completion_cost` and its unexplained accounting basis; (e) the
  documented **absence of any error contract** on the whole cost surface
  (Claim 11); (f) **HuggingFace repo ids as a tokenizer dependency**, unpinned.

## Guide Impact

Verified before writing: `grep -rnE "register_model|response_cost|get_max_tokens|create_pretrained_tokenizer|_hidden_params|custom_tokenizer"` over `guide/` and `source-notes/` returns **zero**
matches (re-verified this session, after this note was drafted).
`guide/05-llm-ops-reliability.md` has no `register_model`, no `response_cost`, no
`get_max_tokens`, and no custom-tokenizer content; its cost material is
§"Model enablement and the cost-map reload pattern" (lines ~266-302, which
covers reload, the `LITELLM_LOCAL_MODEL_COST_MAP=true` image-pull branch at
~278-280, and the reload-success-≠-reachability rule) and the metering-paths
paragraph at ~1218-1242 (streaming opt-in, then the "bundled `model_cost` map"
estimator claim). So: mostly net-new, with **one precision correction required**
in an existing paragraph.

- **Chapter 05 (LLM Ops Reliability) — "Model enablement and the cost-map reload
  pattern": add `register_model` as a third enablement path, and stop calling
  the map "bundled".** The section currently offers exactly two options —
  `POST /reload/model_cost_map`, or an image pull under
  `LITELLM_LOCAL_MODEL_COST_MAP=true` (guide lines ~271-284, sourced from
  `blog-litellm-claude-fable-5-day-0` **Claim 10**). Add a third row for SDK
  users: `litellm.register_model({...})` registers or overrides a model **and its
  pricing** in the process-global `litellm.model_cost` with no reload and no
  upgrade — and, per Claim 4, `litellm.register_model(model_cost="https://…json")`
  repoints the whole map at any hosted blob, which is the documented way to keep
  egress under your own control *without* paying the upgrade-for-freshness cost of
  `LITELLM_LOCAL_MODEL_COST_MAP=True`. Two sentences must change with it: the
  §"Reload success ≠ model reachability" rule (guide ~286-302) should gain the
  inverse check — a `register_model` override can equally be *reported* applied
  while a later reload replaces the dict underneath it, which this page does not
  document either way and which the guide should therefore mark as an open
  dependency (see Open Questions), not as a guarantee. **Do not state that a
  `register_model` override survives or is wiped by a reload** — the source is
  silent and the guide must not guess.
- **Chapter 05 — metering paragraph (~1218-1242): the "bundled `model_cost` map"
  sentence needs a precision correction, and this is the guide change that
  contradiction #1591 exists to review.** The paragraph is currently true *only*
  under `LITELLM_LOCAL_MODEL_COST_MAP=True`. On the default path this page
  documents the pricing source as a live hosted list. Recommend rewording from
  "bounded by the installed package's map version" to "bounded by the cost-map
  snapshot the process loaded — the hosted list on the default path, the packaged
  copy when `LITELLM_LOCAL_MODEL_COST_MAP=True`" — **pending the #1591 verdict**,
  since that issue may land on different wording. Also add the SDK-side egress
  rule from Claim 3: if your firewall is why you pinned the map, then
  `api.litellm.ai` is the dependency you were avoiding and you should either pin
  it deliberately or host the JSON yourself via `register_model`.
- **Chapter 02 (Observability) — three metering paths, not two.** The guide's
  current metering story (guide ~1210-1242) distinguishes payload `usage` from
  local estimation. Add the third surface this page documents: **every call
  carries a cost figure, readable at `response._hidden_params["response_cost"]`.**
  State the two caveats the source forces, because both are the kind of thing a
  reader will otherwise get wrong: (i) `_hidden_params` is a private dict — cite
  it as documented-but-internal, never as a stable contract, and pair it with
  `response.response_ms` (`docs-litellm-completion-output.md` **Claim 7**) as the
  corpus's other number-on-the-response-object field; (ii) the page documents no
  behavior for the unhappy path (Claim 11), so a spend logger built on it must
  branch on presence and sanity-check the implied per-token price rather than
  assuming a float. Then carry the under-reporting warning forward: LiteLLM's
  `usage` object can *both* under-report spend (advisor tool,
  `docs-litellm-anthropic-advisor-tool.md` **Claim 2**) and over-report it
  (`prompt_tokens` including cache hits,
  `docs-litellm-completion-prompt-caching.md` **Claim 4**), so
  `response_cost` should be labeled "SDK-computed per-call figure, map-derived"
  and reconciled against the invoice.
- **Chapter 05 — "estimator output" label: scope it to the verified form.** The
  guide currently labels `completion_cost` output as estimator output without
  qualification. Per Claim 9, that label is verified only for the
  `prompt=`/`completion=` string form; the `completion_response=` form's basis is
  undocumented and *may* be provider-reconciled. Recommend either restricting the
  label or hedging it, and add the one-request experiment that would settle it
  (call it both ways on the same request; compare against
  `x-litellm-response-cost` and the invoice).
- **Chapter 05 — token counting: name the tokenizer as a dependency.** Add
  `get_max_tokens(model)` as the documented pre-flight context-ceiling check, with
  the explicit warning that the page states no behavior for an unmapped model and
  that this corpus has a recorded incident of unmapped lookups returning
  `cost=0` with no error. Where the guide recommends estimating tokens or cost
  locally, add that the tokenizer degrades **silently** to tiktoken for
  unsupported families and that the supported-family list is stated twice
  inconsistently on the vendor's own page (five names vs four) — so verify the
  family you depend on. If the guide ever recommends a custom tokenizer, require
  the vendored `tokenizer.json` + `create_tokenizer` form over the
  HuggingFace-repo-id form, on hermeticity grounds
  (`guide/05-llm-ops-reliability.md` already states the principle at ~line 264:
  "Non-hermetic config is non-replayable and non-rollable").
- **Chapter 06 (Security and Trust) — one new egress dependency, one
  non-dependency.** `api.litellm.ai` is a runtime egress endpoint for the pricing
  map on the default configuration; that belongs in whatever egress/residency
  list Ch06 keeps (the corpus's existing `api.litellm.ai` material,
  `docs-litellm-caching-hosted-cache.md` #1432, is the *cache* — different
  feature, and the two must not be merged in the guide's text). Conversely, note
  what this source does **not** license: it says nothing about prompt or response
  payloads reaching `api.litellm.ai` for *pricing* purposes, so the guide must not
  extend the hosted-cache residency warning to the cost-map path.

## Extraction Notes

- **Read in full**, via the page's raw markdown endpoint
  (`https://docs.litellm.ai/docs/completion/token_usage.md`, HTTP 200, 7,649
  bytes, front matter `last_updated: "2026-10-03"`), cross-checked against the
  rendered HTML (`https://docs.litellm.ai/docs/completion/token_usage`, HTTP
  200, 74,681 bytes). The markdown endpoint is the quoting source for every
  `Quote` and every code block above, because the rendered HTML collapses line
  breaks inside code blocks — the same reason `docs-litellm-mock-requests.md`
  used it.
- **One linked page followed** per MINER.md §1, plus one comparison fetch, both
  recorded so the work is not lost:
  - The page's opening claim links "See here" to
    `https://litellm.readthedocs.io/en/latest/output/`. **It does not resolve** —
    HTTP 404, as does the host root, so this is a host-level retirement rather
    than a page-specific dead link, and I cannot say which. The claim it was
    meant to support is therefore **not** independently verifiable from here; the
    corpus's equivalent claim rests on
    `docs-litellm-streaming-token-usage.md` and
    `docs-litellm-completion-prompt-caching.md` instead.
  - The **older** `https://docs.litellm.ai/token_usage` (HTTP 200) was fetched in
    full because it is the `source_url` of `docs-litellm-token-usage-helpers.md`
    and both pages are live simultaneously. That comparison produced Claims 2
    and 10(a)/(d) and contradiction **#1591**. Note for the corpus: the old
    page's `.md` variant (`/token_usage.md`) returns 404 while the rendered page
    returns 200 — Docusaurus only exposes `.md` for current docs-tree routes, so
    a Miner following the `docs-litellm-mock-requests.md` markdown-first
    technique on an older URL will get a misleading 404.
  - The page's `related:` entries are `/docs/caching/all_caches` (already mined as
    `docs-litellm-caching-all-caches.md`, #1431) and `/docs/exception_mapping`
    (no corpus note). Neither was mined — different sources, own `source_url`s,
    and outside this issue's scope. The `model_prices_and_context_window.json`
    file the page links twice was **not** fetched or mined, per the triage's
    explicit instruction; it is recorded as an external dependency only.
- **Triage bounding honored.** The three shared helpers (`token_counter`,
  `cost_per_token`'s definition, `completion_cost`'s composition) are cited as
  already-covered in `docs-litellm-token-usage-helpers.md` **Claims 1–4** rather
  than re-extracted; streaming and `always_include_stream_usage` are cited to
  `docs-litellm-streaming-token-usage.md` and
  `docs-litellm-completion-output.md` **Claim 10**; `LITELLM_LOCAL_MODEL_COST_MAP`
  is extracted only as the *delta* (hosted-pull opt-out, firewall motivation,
  egress dependency) per Claims 3 and the register_model alternative.
- **`confidence_overall: emerging`**, set explicitly rather than left as the
  template placeholder, per the triage's guidance and the standard the two
  sibling token-usage notes set. The API surface in Claims 1–9 is settled
  first-party documentation and could each be graded `settled` in isolation; the
  note is `emerging` because its load-bearing content is (a) a **living vendor
  page with no version pin** whose examples are demonstrably unrun (Claim 10),
  (b) an unresolved provenance question that required filing #1591 rather than
  reading the docs (Claims 2, and the cross-page reading in Cross-References),
  and (c) an explicitly open question about the `completion_response=` accounting
  basis (Claim 9) that no amount of reading this page can close. Nothing here was
  executed against a live LiteLLM install.
- **Every `Quote` field is a contiguous, character-for-character fragment of the
  page's markdown**, including its backticks, bold markers, and link syntax
  (following `docs-litellm-completion-prompt-caching.md`). No quote splices two
  non-adjacent sentences. Where the meaning was my synthesis across multiple
  source strings — the "third metering path" reading (Claim 1), the
  "partial view" reading of the three-key schema (Claim 5), the
  multiple-writer conflict (header), the egress inference in Claim 8, and all of
  Claim 11 — it sits in `Our assessment` and is labelled as our reading.
  Claim 11 carries an explicit no-quote marker rather than a reconstructed line.
- **Open Questions recorded rather than answered** (each would take minutes in a
  REPL and none is answered by this page):
  1. Does `completion_cost(completion_response=…)` read the response's reported
     `usage`, or re-tokenize locally? (Claim 9 — decides whether the guide's
     "no provider-side reconciliation" holds for that form.)
  2. Does a `register_model` override survive `POST /reload/model_cost_map`? The
     reload is documented as a refetch-and-replace; the override is documented as
     a mutation of the same global; the page never reconciles them.
  3. What is `response_cost` on a failed call, a fallback attempt, a streamed
     response, and a model absent from the map?
  4. Does `get_max_tokens` raise, return `None`, or return `0` for an unmapped
     model?
  5. Is the `register_model(model_cost=<url>)` blob fetched once at registration
     or re-fetched, and what happens if it is unreachable on a later boot?
  6. Do Llama3 tokenizers actually work, given the five-vs-four discrepancy?
- **No contradiction issue filed for anything except #1591**, per MINER.md §4a.
  Checked `CONTRADICTIONS.md` (no entries — "No open contradictions at MVP
  bootstrap") and all 15 open `contradiction`-labeled issues; none covers
  cost-map provenance. The intra-page findings (Claims 5, 7, 10) and the
  `api.litellm.ai` hostname collision between the pricing path and the
  hosted-cache path were deliberately **not** filed — §4a's "when NOT to file"
  covers documentation defects and naming collisions, and neither would split
  guide advice. Issue #1591 *was* filed because it is a source-vs-source and
  source-vs-chapter disagreement about which artifact is authoritative on the
  default path, on a word (`bundled`) the guide already publishes as a rule; that
  is §4a's third "when to file" case. The triage's own guidance pointed both
  ways (two comments suggested a provenance clarification rather than a filing,
  one flagged "bundled" as load-bearing); I filed it because the two pages are
  live simultaneously, name the same function, and the reconciling mechanism is
  documented in neither — and recorded in #1591 that Claim 2 identifies them as
  two names for one artifact, so the resolver is not left with a false dilemma.
- `registry/sources.json` and `registry/claims-index.json` were **not** edited;
  they are derived indexes rebuilt by `registry-rebuild.yml` after merge.
- `miner-related-notes.md` was read before writing Cross-References and is **not
  committed** (it is untracked; see `.gitignore`).