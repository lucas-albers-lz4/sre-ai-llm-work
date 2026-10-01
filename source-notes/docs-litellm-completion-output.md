---
source_url: https://docs.litellm.ai/docs/completion/output
source_type: docs
title: "Output | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-10-01)
date_extracted: 2026-10-01
last_checked: 2026-10-01
status: current
confidence_overall: emerging
issue: "#1540"
---

# Output — `litellm.completion()` response shape (LiteLLM Docs)

> The response-side counterpart to `docs-litellm-completion-input-params.md`
> (#1495), which explicitly scoped the response contract out and named this
> page as its owner. It contributes the corpus's **only** record of the
> gateway's `finish_reason` **normalization contract** — all provider-native
> stop values are mapped onto a fixed five-value OpenAI set, and the original
> is preserved under `provider_specific_fields["native_finish_reason"]` *only
> when the values diverge* — which makes field **absence** ambiguous and is the
> one thing an agent loop cannot infer. It also contributes the corpus's only
> record of `response.response_ms` as a per-call latency field, and a
> documented instance of a *failed* tool call (`MALFORMED_FUNCTION_CALL`)
> normalized to look like a *successful* completion (`stop`).

## Source Context

- **Type**: docs (single-page LiteLLM SDK reference at
  `/docs/completion/output` — verified HTTP 200 this session, 60,299 bytes,
  body read in full via both the rendered markdown and a `<pre>`-block
  extraction of the raw HTML). Page breadcrumb per its own nav:
  "Supported Endpoints → /chat/completions → Output". Siblings in the same
  section: `/completion/input` (mined, #1495), `/completion/usage` (mined in
  this note, Claims 10-12), `/completion/http_handler_config` (#1482).
- **Author credibility**: LiteLLM (BerriAI) first-party product
  documentation. Authoritative for the *documented* response surface — it is
  the vendor stating its own normalization contract. This is the vendor
  describing its own product: no metrics, no wire captures, no test output, no
  changelog, no third-party confirmation, and the page is undated. Two of its
  three sections are short prose plus a code block, with no support matrix, no
  per-provider table, and no worked provider comparison.
- **Scope**: The **response** surface of `litellm.completion()`, in three
  sections: "Format" (the top-level type skeleton and one filled example),
  "Native Finish Reason" (the normalization rule and the divergence-preserving
  key), "Additional Attributes" (latency). Does **not** cover: the request
  surface (that is `/completion/input`), token-usage and cost helpers
  (`/completion/usage`, `/sdk_custom_pricing`), the OpenAI-compatible **proxy**
  surface, the Router, error shapes, or streaming chunk layout.
- **Redundancy / what this page owns**: this is the page
  `docs-litellm-completion-input-params.md` (#1495) names as the owner of the
  response shape and declines to cover. The `stream_options={"include_usage":
  True}` contract also restated here is **not** re-derived — it belongs to
  `docs-litellm-streaming-token-usage.md` (#1286) and #1495 Claim 9, and is
  recorded here as corroboration only. What is genuinely new to the corpus is
  the `finish_reason` normalization contract, the divergence-only preservation
  of `native_finish_reason`, the `response_ms` latency field, and the
  dict-or-class dual-access guarantee.
- **A note on the page's artifacts**: all five code blocks on this page are
  published with their **line breaks collapsed** — each renders as a single
  unbroken run of text (see Concrete Artifacts; verified by extracting every
  `<pre>` block from the raw HTML). This is a property of the live page, not of
  the extraction: contrast the sibling input page, whose `completion()`
  signature renders across 40 lines in the corpus note for it. None of the four
  artifacts below is copy-pasteable as published. Recorded as Claim 9.

## Extracted Claims

### Claim 1: The page documents a **four-key** top-level response contract — `choices`, `created`, `model`, `usage` — and does not document `id`, `object`, `system_fingerprint`, or `tool_calls` anywhere, so the "exact json output" claim is narrower than the wire shape the rest of the corpus has captured
- **Evidence**: The "Format" section's one-sentence scope claim followed by the
  type-annotated skeleton; then the "Here's what an example response looks
  like" block, which is the page's only filled response. The page has no other
  sections and no field table.
- **Confidence**: settled that the page documents four keys (the enumeration
  is explicit and complete on the page); **emerging** for any inference about
  the wire shape itself, which this page cannot establish
- **Quote**: "Here's the exact json output and type you can expect from all
  litellm `completion` calls for all models"
- **Our assessment**: The "exact" framing is the vendor claiming completeness,
  and the enumeration is demonstrably incomplete against the corpus's own
  captured payloads. The three keys it omits are not speculative — each appears
  in an existing note's verbatim artifacts: `docs-litellm-completion-batching.md`
  (Concrete Artifacts) shows `"object": "chat.completion"`, an `id` of
  `chatcmpl-e673ec8e-…` and `"system_fingerprint": "fp_179b0f92c9"`, and
  `docs-litellm-completion-input-params.md` **Claim 10** names
  `system_fingerprint` as *the* field to record for backend-drift detection.
  `tool_calls` is the more consequential omission, because it is one of the two
  values in this page's own normalized `finish_reason` set
  (`docs-litellm-completion-input-params.md` **Claim 12** documents
  `tools[].type` as a first-class request surface) — the page defines a
  stop reason for tool calls without ever documenting where the tool calls
  live. So this page must **not** be used as the schema of record: it is
  authoritative only for the four keys it names, and an integrator who treats
  it as the complete envelope will write a parser that drops `id` and
  `system_fingerprint`. The rule that falls out for the guide: the corpus's
  effective response contract is the *union* of this page's four keys and the
  `id`/`object`/`system_fingerprint` triple observed in the batching page's
  artifacts, and `tool_calls` is the known hole.

### Claim 2: `created` and `model` are annotated as strings whose values are `None` on the type skeleton, while the page's own example supplies a float epoch and a concrete model id — the page's declared types and its only worked example disagree
- **Evidence**: Side by side in the same "Format" section — the skeleton's
  trailing `# String: None` comments on both fields, and the example's
  `'created': 1691429984.3852863, 'model': 'claude-sonnet-5'`. The literal
  `1691429984.3852863` is a float, not a string, and is not `None`.
- **Confidence**: settled as a **documentation** observation (both values are
  directly observable on the fetched page and re-checkable); no claim is made
  about runtime types
- **Quote**: "'created': str,               # String: None" / "'created':
  1691429984.3852863, 'model': 'claude-sonnet-5',"
- **Our assessment**: Recorded as a caveat, **not** as a claim about runtime
  behavior, and it is not a contradiction (see Cross-References). Two things
  make it more than cosmetic. (1) The `created` value is a **float with
  sub-second precision**, which matters to anyone writing a time-window filter
  or a dedup key off it: `1691429984.3852863` is not a Unix second boundary, and
  a collector that coerces it to `int` loses the fraction — the same shape of
  problem the corpus already records in
  `docs-litellm-completion-batching.md` **Claim 12**, which independently
  notes a float `created` on a sibling page. (2) The `# String: None` comment
  is the more useful half: if a reader takes it at face value, the honest
  downstream behavior for both fields is *no default and no type guarantee*, so
  `response.model` must be read defensively before being used as an
  attribution key. Ch05's existing rule ("Surface the `model` field from the
  response metadata in observability dashboards") is correct but currently
  assumes a field that this page declines to promise. Note the
  `1691429984` epoch also dates the sample to September 2023, which puts it in
  the same staleness class #1495 and the batching note already flag.

### Claim 3: The response is guaranteed to be readable as **both** a dict and a class object, and the page's own demonstration is that both accessors return the same content
- **Evidence**: A single sentence in the "Format" section followed by a
  one-line code block printing the identical string twice through the two
  access paths. This is the only statement of access-mode on the page.
- **Confidence**: settled (explicit vendor statement plus a worked example of
  equivalence)
- **Quote**: "You can access the response as a dictionary or as a class object,
  just as OpenAI allows you"
- **Our assessment**: The dual-access guarantee is what makes this page
  *necessary* rather than redundant with every other LiteLLM note in the
  corpus: the batching note's own artifacts show the three sibling response
  objects rendering under three different Python types (`<ModelResponse
  chat.completion …>`, `<OpenAIObject chat.completion …>`, and a bare
  `chat.completion` id), which is exactly the ambiguity this sentence resolves.
  The operational cost of the guarantee is one the page does not mention: **a
  missing key raises a different exception per mode** — `KeyError` via
  subscript, `AttributeError` via attribute — and `provider_specific_fields`
  is the field most likely to be missing (Claims 5-6). An agent loop that wraps
  response reads in a single `except Exception` will be fine; one that catches
  `KeyError` because it was written against dict access will silently miss
  every attribute-access failure. The guide-relevant rule is that any
  defensive read of a *possibly-absent* response field must handle both
  exception classes, or use the `.get()`-style form the vendor's own native-
  finish-reason sample uses.

### Claim 4: `finish_reason` is a **total** normalization target — LiteLLM states that *all* provider-specific `finish_reason` values are mapped into a fixed five-value OpenAI set (`stop`, `length`, `tool_calls`, `function_call`, `content_filter`) — and the page never publishes the source-to-target table that would make the mapping checkable
- **Evidence**: The first sentence of the "Native Finish Reason" section, with
  the five target values enumerated inline in backticks. It is the only
  statement of the value set anywhere on the page, and the only place in the
  corpus where a *closed* set of `finish_reason` values is enumerated.
- **Confidence**: settled as a **documented contract** (explicit, unqualified,
  and enumerable); **emerging** for the word "all", which is a totality claim
  with no per-provider table, no wire capture and no test behind it — the same
  grade the corpus already assigns to the sibling provider-uniformity
  assertions (see Cross-References)
- **Quote**: "LiteLLM maps all provider-specific `finish_reason` values to
  OpenAI-compatible values (`stop`, `length`, `tool_calls`, `function_call`,
  `content_filter`)."
- **Our assessment**: This is the page's load-bearing claim and the first
  closed value-set for `finish_reason` in the corpus — `guide/` does not
  mention `finish_reason` at all (re-verified this session), and the five
  existing notes that contain the string treat it as a single value to
  compare against (`== "stop"`, `== "length"`), never as an enumerated
  contract. The gap inside the claim is the part that matters for guide
  advice: the page names the five targets and **no source values at all**. So
  the mapping is unfalsifiable from this page — an integrator cannot learn
  which native value becomes which OpenAI value, and in particular cannot learn
  what a *provider-native* `stop_sequence` (a real Anthropic stop reason, per
  `docs-litellm-anthropic-unified.md` **Claim 8**) collapses into. Given that
  the corpus records four distinct Anthropic `stop_reason` values mapping onto
  five OpenAI values, the map is necessarily many-to-one, and many-to-one over
  stop reasons is lossy by construction: two materially different end-states
  (`end_turn` and `stop_sequence`) can land on the same `stop`. That is a
  guide rule, not just a curiosity: **never branch exhaustively on the five
  values with no default branch**, because the vendor's own totality claim and
  the corpus's own native vocabularies jointly imply more native states than
  target states.

### Claim 5: The divergent native value is preserved under `provider_specific_fields["native_finish_reason"]` **only on divergence** — the field is absent whenever the provider already returned an OpenAI-compatible value, so field absence carries no information
- **Evidence**: Two sentences that together define the preservation condition:
  the section's first sentence states the condition ("When the original
  provider value differs from the mapped value, it is preserved…"), and a
  standalone sentence after the code sample states the negative case
  explicitly. This is the page's genuinely novel claim and the reason the page
  is worth mining despite its length.
- **Confidence**: settled (the vendor states both the positive and the negative
  condition, explicitly and unconditionally)
- **Quote**: "When the original provider value differs from the mapped value,
  it is preserved in `provider_specific_fields[\"native_finish_reason\"]`." /
  "When the provider already returns an OpenAI-compatible value (e.g.,
  `stop`), `native_finish_reason` is not set."
- **Our assessment**: Novel to the corpus — `native_finish_reason` returns
  **zero** hits across `source-notes/` and `guide/` (re-verified this session).
  The operational consequence is an **absence-is-not-signal** problem, and it
  is sharper than the page's framing suggests for two reasons. (1) The
  divergence condition is *silent*: the caller receives a normal 200 with
  ordinary `finish_reason: "stop"` whether or not a rewrite happened, and the
  only difference is a key's presence. So `native_finish_reason is None` is
  consistent with at least three distinct worlds — the provider natively said
  `stop`; the provider said something that mapped to `stop` but the
  preservation did not fire; or the field's parent container is absent
  altogether. A caller cannot distinguish them from the response, and the page
  gives no provider-aware check that would. **Never treat the presence of
  `native_finish_reason` as a proxy for "something unusual happened", and never
  treat its absence as "nothing unusual happened".** (2) The container itself,
  `provider_specific_fields`, is *not* a
  finish-reason-only field in this gateway — the corpus already has a second,
  differently-keyed member of the same container
  (`docs-litellm-knowledgebase-vector-stores.md` **Claim 6**, the undocumented
  `vector_store_search_failures` key that **Claim 4** of that note shows is
  gated on `finish_reason == "stop"` on the streaming path). So the same
  container is the gateway's general out-of-band channel, which means
  "container present but `native_finish_reason` missing" is the **normal**
  state, not an anomaly. This is the strongest single addition this page makes
  to the corpus.

### Claim 6: The page's own sample uses **two different absence mechanisms at two different levels** — `hasattr()` on the container, `.get()` on the key — and the prose explains only the second; a failed tool call (`MALFORMED_FUNCTION_CALL`) is normalized to `stop`, so a `stop`-terminating agent loop cannot tell a malformed tool call from a clean completion
- **Evidence**: The "Native Finish Reason" code sample, reproduced verbatim in
  Concrete Artifacts. The `hasattr`/`and` guard tests the *container*; the
  `.get()` tests the *key*; the `if native == "MALFORMED_FUNCTION_CALL"`
  comparison is the branch the sample exists to demonstrate. The section's
  second sentence frames the purpose in agent terms.
- **Confidence**: settled for the guard's structure and the mapped value (both
  explicit in the sample); the failure consequence in Our assessment is ours
- **Quote**: "This is useful for agent loops that need to distinguish between
  different stop conditions (e.g., Gemini's `MALFORMED_FUNCTION_CALL` vs a
  normal `stop`)."
- **Our assessment**: Two findings, and the second is the sharpest thing on
  the page. (1) **The two-level guard is under-explained.** The prose
  documents absence of the *key* (Claim 5) and is silent about absence of the
  *container*, yet the sample guards the container with `hasattr` **and** a
  truthiness check. So the sample is defensive against a condition the
  documentation does not describe, which is a signal that container-absence is
  a real observed state the prose omits. Practical upshot: the vendor's own
  guard — `hasattr(x, "provider_specific_fields") and
  x.provider_specific_fields` before `.get(...)` — is the minimum correct
  pattern, and a caller who writes only `.get("native_finish_reason")` on the
  container without the guard is relying on a field the page does not promise.
  (2) **A failed tool call is normalized to a successful-looking completion.**
  The one worked example on the page is a *malformed* function call
  (`MALFORMED_FUNCTION_CALL`, a Gemini-native value) whose mapped
  `finish_reason` the sample itself prints as `"stop"`. So the page's own
  demonstrated agent-loop pattern — print `finish_reason`, branch on it, and
  consult `native_finish_reason` only when you care about the specific native
  case — has a failure mode at its center: an agent loop that terminates on
  `finish_reason == "stop"` terminates **successfully** on a tool call the
  provider could not parse, with an empty or unusable `tool_calls` and no error
  and no exception. The guide rule this forces is that **`finish_reason` alone
  is not a sufficient success predicate for a tool-using loop**; a loop that
  branches on stop condition must either assert a non-empty
  `tool_calls`/parsed-arguments set, or record
  `native_finish_reason` on every call so malformed invocations are countable
  after the fact. Note the page nowhere lists `tool_calls` as a response field
  (Claim 1), so that assertion currently has no documented field to read —
  recorded as an open sub-question, not filled in by assumption.

### Claim 7: `response.response_ms` is a per-call latency float exposed directly on the response object, documented only by a single `print` and its printed value
- **Evidence**: The page's entire "Additional Attributes" section is one
  sentence and one seven-line code block, whose final two lines are the call
  and its printed output.
- **Confidence**: emerging (documented as an accessible attribute with a
  worked printed value; the page gives no definition — not of units, not of
  what is included in the measurement, not of its behavior on error or on
  retries)
- **Quote**: "You can also access information like latency." / "print(response.response_ms) # 616.25"
- **Our assessment**: Novel to the corpus — `response_ms` returns **zero**
  hits across `source-notes/` and `guide/` (re-verified this session), and the
  Prospector's triage flagged it as a cheap observability hook. We take the
  *existence* of the field and decline the *meaning* of the number, because
  the page documents neither. The two questions a runbook needs and the page
  does not answer are: **what is in the measurement** (gateway queueing plus
  provider time, or provider time only — undeterminable here), and **what
  happens on a retried or failed call** (there is no error case shown, and a
  response that never materialized has no object to carry the field). Both are
  open sub-questions, recorded as such. What the field *is* good for, stated
  carefully, is per-call latency attribution in the client process with zero
  extra configuration — which is the gap the corpus's own observability notes
  keep circling: Ch02 currently prescribes that a span carries "metrics
  (`input_tokens`, `output_tokens`)" and names no latency field on the LLM
  span, and `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
  **Claim 2** states that a mandatory attribute set is required on every span.
  So this gives the LiteLLM-SDK case a named, vendor-blessed field for a metric
  the guide's own span schema currently leaves unspecified — with the caveat
  that a client-side `response_ms` is a different quantity from a gateway-side
  latency, and the guide should not present it as a substitute for the proxy's
  own metrics.

### Claim 8: The response shape is declared provider-invariant, and the only filled example on the page is an **Anthropic** model served through the gateway — so the single worked instance exercises the exact path the normalization contract exists to abstract
- **Evidence**: The "Format" section's scope sentence claims the shape and type
  for "all litellm `completion` calls for all models", and the sole example
  response is `'model': 'claude-sonnet-5'` with Anthropic-flavored content
  ("I am Claude, an AI assistant created by Anthropic.").
- **Confidence**: settled that the page claims invariance and shows one
  Anthropic-served example; **anecdotal** for the invariance itself (a
  one-example demonstration, no per-provider table — graded consistently with
  the corpus's existing treatment of LiteLLM provider-uniformity assertions)
- **Quote**: "Here's the exact json output and type you can expect from all
  litellm `completion` calls for all models"
- **Our assessment**: The example is load-bearing in a way that cuts against
  the claim it illustrates. The gateway's whole reason for existing is
  cross-provider shape unification, and the one response the page shows is
  served by a single provider whose native `stop_reason` vocabulary the corpus
  already records as four distinct values
  (`docs-litellm-anthropic-unified.md` **Claim 8**:
  `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`). So the page
  demonstrates its invariant with a non-differentiating instance, and the
  provider where the mapping does the most work is the one with no worked
  example. Combined with Claim 4's missing source-to-target table, the honest
  guide position is: **treat the five-value `finish_reason` set and the
  four-key envelope as a documented vendor contract, cite them as such, and do
  not present them as verified cross-provider behavior.** Note also that the
  example's own content is the trap `docs-litellm-completion-batching.md`
  **Claim 12** already named — a model that self-identifies as Claude while
  being served under a gateway response; the only trustworthy attribution
  field is `model`, and per Claim 2 that field is not even type-promised.

### Claim 9: All five code blocks on the page are published with their line breaks collapsed, so none of the page's four artifacts is copy-pasteable as rendered
- **Evidence**: Direct observation, verified two ways this session: the
  rendered markdown fetch returns each block as one unbroken run, and
  extracting all five `<pre>` elements from the page's raw HTML yields the
  same five single-line strings. The 4-key skeleton, the dual-access print, the
  example response, the native-finish-reason sample, and the `response_ms`
  sample are each one line in the source document.
- **Confidence**: settled (directly observable and re-checkable against the
  live page; quoted verbatim in Concrete Artifacts)
- **Quote**: (no direct quote; the defect is in the artifacts' whitespace, not
  in prose — the five blocks are reproduced verbatim in Concrete Artifacts so
  the Assayer can re-verify against the live page)
- **Our assessment**: Small, but worth recording because it explains the
  page's most confusing feature and it is a *usable* signal for anyone
  evaluating these docs. A reader who copies the native-finish-reason sample
  gets `response = completion(model="gemini/gemini-3.8-flash",
  messages=messages)choice = response.choices[0]print(choice.finish_reason)  #
  "stop" (OpenAI-compatible)# Access the original…` — a single unparseable
  line, from which the `if` nesting (and therefore the guard structure that
  Claim 6 depends on) is invisible. The corpus already has precedent for
  treating this class of defect as substantive rather than cosmetic:
  `docs-litellm-completion-input-params.md` **Claim 2** records a two-name
  retry-parameter inconsistency on the sibling page as a *quiet-failure* trap,
  and the same note flags that the sibling page's own prompt-formatting link
  404s. The pattern across the two pages is that this section's code samples
  are not maintained as runnable artifacts, so **an operator should treat
  LiteLLM SDK code samples as illustrative, and verify any guard or branch
  logic against the prose and against library source before relying on it** —
  which is the same conclusion the corpus reached independently for the
  batching page's sample payloads.

### Claim 10: A proxy setting, `general_settings: always_include_stream_usage: true`, force-injects `stream_options={"include_usage": True}` into **all** streaming requests, so the response's `usage` object is availability-gated on a gateway deployment flag, not only on caller opt-in
- **Evidence**: The "Proxy: Always Include Streaming Usage" section of the
  `Next`-sibling page, read in full this session
  (`https://docs.litellm.ai/docs/completion/usage`, HTTP 200): a `config.yaml`
  block, a five-step UI path, a four-item "How it works" list, and a `curl`
  example whose request body omits `stream_options` entirely. Verified absent
  from the corpus: zero hits for `always_include_stream_usage` in
  `source-notes/` or `guide/`.
- **Confidence**: settled as a **documented** configuration surface (config
  key, UI path, and four explicit behavioral bullets are all stated); the
  four bullets are the vendor's claims, unverified
- **Quote** (from https://docs.litellm.ai/docs/completion/usage): "All
  streaming requests will automatically have
  `stream_options={\"include_usage\": True}` added" / "Clients will receive
  usage information in the final chunk, even if they didn't explicitly request
  it" / "If a client already provides `stream_options`, `include_usage: True`
  will be added without overwriting other options" / "Non-streaming requests
  are not affected"
- **Our assessment**: Novel to the corpus, and it **corrects a rule the corpus
  currently states as absolute**. Both
  `docs-litellm-streaming-token-usage.md` **Claim 1** ("A streaming
  completion does not report token usage unless the client opts in") and
  `docs-litellm-completion-input-params.md` **Claim 9** (the opt-in is a
  per-caller decision) are true *of the SDK call surface* and false *of a
  proxy deployment with this flag on*. The fourth bullet bounds it exactly as
  the corpus would want — non-streaming requests are unaffected, so the
  four-key `usage` object on the ordinary non-streaming response (Claim 1) is
  untouched. The three consequences worth carrying. (1) **Spend-accounting
  coverage becomes a deployment property.** The corpus's stated rule is
  "per-caller opt-in, not per-provider"
  (`docs-litellm-completion-input-params.md` **Claim 9** assessment); this
  adds a third axis, and the correct one to audit first is the gateway's
  `config.yaml`, because it is the only one an operator controls
  fleet-wide. (2) **A client cannot detect the rewrite from the request** —
  the flag is injected server-side, so two callers sending byte-identical
  bodies get different response shapes depending on which proxy fronted them.
  A collector that infers "was usage requested?" from the request body will be
  wrong for every streaming call behind a flag-on proxy. (3) The merge is
  documented as **non-destructive** ("without overwriting other options"),
  which is the specific detail that makes the flag safe to enable and the
  detail a naive string-merge implementation would get wrong. Note the page
  documents this under the **Proxy**, not the SDK, and this note's source URL
  is the SDK output page — cited as a followed sibling per MINER §1, and
  quoted from its own URL above.

### Claim 11: LiteLLM supports **endpoint bridging** — a request to an endpoint the model does not natively support is silently re-routed to a different endpoint family (`/chat/completions` ↔ `/responses`) based on the model's `mode` in `model_prices_and_context_window`
- **Evidence**: A `Note:` callout on the usage page, immediately after the
  `print(response.usage)` quick-start, naming both bridged directions and the
  single field that decides which. The field it names is a file the corpus
  already knows from `docs-litellm-token-usage-helpers.md` **Claim 3**
  (`model_cost` mirrored as the `model_prices_and_context_window.json`
  community resource).
- **Confidence**: settled as a **documented** behavior (explicit statement,
  named trigger, named config source); the resulting response-shape
  consequences are ours
- **Quote** (from https://docs.litellm.ai/docs/completion/usage): "LiteLLM
  supports endpoint bridging. If a model does not natively support a requested
  endpoint, LiteLLM will automatically route the call to the correct supported
  endpoint (such as bridging `/chat/completions` to `/responses` or vice
  versa) based on the model's `mode`set in `model_prices_and_context_window`."
  (the missing space in "mode`set" is the page's own)
- **Our assessment**: This is the mechanism that makes Claim 4's totality
  claim and Claim 8's invariance claim *non-trivial*, and it is a silent
  request-routing decision of exactly the class Ch05 already legislates for
  model substitution. The trigger is **not** the caller's request — it is a
  field in a community-maintained JSON file keyed on the model name. So the
  same request body, from the same client, against the same model string, can
  be served by a different **endpoint family** depending on that file's
  contents, and the page documents no signal on the response identifying which
  path ran. That compounds the corpus's existing findings rather than
  contradicting them: the corpus already records that the *response* `model`
  field is the only trustworthy attribution signal and that self-identification
  is worthless (`docs-litellm-completion-batching.md` **Claim 12**), and
  separately that `model_prices_and_context_window` governs client-side cost
  math (`docs-litellm-token-usage-helpers.md` **Claim 3**). What is new is
  that the same file also silently decides the **request** path — so a
  gateway team's endpoint-parity testing, which would naturally be written
  against a fixed model string, is testing a value that a mutable community
  file can change underneath it. The guide rule: a claim of "LiteLLM returns
  the OpenAI-compatible shape for all models" holds only per *resolved* model
  entry, and endpoint resolution is a second, undocumented-in-signal
  substitution authority alongside the three Ch05 already names.

### Claim 12: The usage object is declared provider-invariant as a first-class guarantee, on the same assertion-only footing the corpus already grades `anecdotal`
- **Evidence**: The usage page's opening sentence, above the three-key
  `usage` type block — a bare declarative sentence with no qualification, no
  matrix and no derivation.
- **Confidence**: **anecdotal** (a vendor uniformity assertion with no
  supporting evidence on the page; graded identically to the corpus's existing
  treatment of the two sibling uniformity claims — see Cross-References)
- **Quote** (from https://docs.litellm.ai/docs/completion/usage): "LiteLLM
  returns the OpenAI compatible usage object across all providers."
- **Our assessment**: Recorded rather than bought, for a reason the corpus has
  already established twice: `docs-litellm-completion-input-params.md`
  **Claim 1** grades the input page's "accepted for every provider" `anecdotal`,
  and `docs-litellm-streaming-token-usage.md` **Claim 3** grades
  "Supported across all providers. Works the same as openai" `anecdotal` — and
  #1495's assessment makes the methodological point explicitly: *two pages
  agreeing is more corroboration, not more evidence, when both are the same
  vendor making the same unsourced claim.* This is now the fourth such
  assertion in the corpus on this gateway's usage/shape surface. The
  consistent position, which the guide should state once rather than
  re-litigate per page, is: **LiteLLM's provider-uniformity claims are
  documented but unverified throughout, so treat them as a design intent to be
  tested in your own deployment, not as a contract to be relied on.** A
  concrete reason to test rather than rely: the same corpus records a case
  where a uniform-looking top-level `usage` was **wrong** —
  `docs-litellm-anthropic-advisor-tool.md` **Claim 2** documents that
  top-level `usage` reflects *executor tokens only*, with the advisor's
  sub-inference tokens reachable only through `usage.iterations[]`. So a
  uniform `usage` object is guaranteed in *shape* per this page while having
  already been shown to be non-exhaustive in *content*. Shape uniformity and
  content completeness are different claims and the guide should not merge
  them.

## Concrete Artifacts

All five `<pre>` blocks from `https://docs.litellm.ai/docs/completion/output`,
extracted verbatim from the page's raw HTML this session. **As published,
every block is a single unbroken line** — see Claim 9. Reproduced unaltered.

**The declared response type, with the page's own annotations** ("Format"
section, first block, verbatim):

```
{  'choices': [    {      'finish_reason': str,     # String: 'stop'      'index': int,             # Integer: 0      'message': {              # Dictionary [str, str]        'role': str,            # String: 'assistant'        'content': str          # String: "default message"      }    }  ],  'created': str,               # String: None  'model': str,                 # String: None  'usage': {                    # Dictionary [str, int]    'prompt_tokens': int,       # Integer    'completion_tokens': int,   # Integer    'total_tokens': int         # Integer  }}
```

**Dual dict-or-class access** ("Format" section, second block, verbatim — two
prints that the page presents as returning the same value):

```
print(response.choices[0].message.content)print(response['choices'][0]['message']['content'])
```

**The page's only filled example response** ("Format" section, third block,
verbatim — note `'created'` is a float and `'model'` is a concrete id, both
contradicting the annotations above; Claims 2 and 8):

```
{  'choices': [     {        'finish_reason': 'stop',        'index': 0,        'message': {           'role': 'assistant',            'content': " I'm doing well, thank you for asking. I am Claude, an AI assistant created by Anthropic."        }      }    ], 'created': 1691429984.3852863, 'model': 'claude-sonnet-5', 'usage': {'prompt_tokens': 18, 'completion_tokens': 23, 'total_tokens': 41}}
```

**The native-finish-reason agent-loop sample** ("Native Finish Reason"
section, fourth block, verbatim — this is the artifact Claims 5 and 6 are
read from; note the two-level guard `hasattr(...) and ...` on the container
followed by `.get(...)` on the key, and the mapped value printed as `"stop"`
for a `MALFORMED_FUNCTION_CALL`):

```
response = completion(model="gemini/gemini-3.8-flash", messages=messages)choice = response.choices[0]print(choice.finish_reason)  # "stop" (OpenAI-compatible)# Access the original provider value when it differs:if hasattr(choice, "provider_specific_fields") and choice.provider_specific_fields:    native = choice.provider_specific_fields.get("native_finish_reason")    if native == "MALFORMED_FUNCTION_CALL":        # Handle malformed function call differently from a normal stop        pass
```

**The `response_ms` latency sample** ("Additional Attributes" section, fifth
block, verbatim — the whole section is this block; the doubled `# 616.25` is
the page showing the printed value after the call):

```
from litellm import completionimport osos.environ["ANTHROPIC_API_KEY"] = "your-api-key"messages=[{"role": "user", "content": "Hey!"}]response = completion(model="claude-sonnet-5", messages=messages)print(response.response_ms) # 616.25# 616.25
```

**From the followed sibling page**
(`https://docs.litellm.ai/docs/completion/usage`, read in full; Claim 10) —
the proxy setting and the config block the page gives for it:

```yaml
general_settings:
  always_include_stream_usage: true
```

and the `curl` request the page says will receive usage regardless, note the
**absent** `stream_options` in the body:

```
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{    "model": "gpt-5.6-terra",    "messages": [{"role": "user", "content": "Hello!"}],    "stream": true  }'
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path is cited or
dismissed below):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch TPM/RPM
  accounting, per-record token charging, and
  `batch_enqueued_token_limit` on `POST /v1/batches`. This page is the
  per-response SDK surface with no batch accounting. No claim overlap.
- `source-notes/docs-litellm-completion-input-params.md` — **Cited (Extends,
  and it supplies the gap this page fills)**: that note's *Source Context*
  section states the page "Does NOT cover: the response shape (that is
  `/completion/output`)" — an explicit hand-off, and this note is the
  counterpart it names. Two specific claims are extended by the other
  direction. That note's **Claim 10** names `system_fingerprint` as the
  backend-drift signal and records that the only corpus occurrence of the name
  was a literal response key in the batching page's artifacts; this page
  documents `created`/`model` but *not* `system_fingerprint` (Claim 1), so the
  drift-detection field the corpus relies on is undocumented on the page that
  claims to give the exact output. That note's **Claim 9**'s assessment
  concludes streamed usage coverage is "per-caller opt-in, not per-provider";
  Claim 10 here adds the third axis (a gateway flag) that makes that rule
  incomplete as stated.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**: an
  endpooint feature-support matrix and transcription fallback semantics on
  `/v1/audio/transcriptions`. Adjacency only: that note's **Claim 5** records
  a support matrix whose lone qualified row is "Applies to output transcribed
  text (non-streaming only)", the same non-streaming/streaming asymmetry that
  bounds Claim 10 here. Noted once, nothing cited.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: the native
  Bedrock Invoke passthrough (`POST /bedrock/model/<model_name>/invoke`), its
  model registration requirements, and SigV4→bearer auth swapping. A
  passthrough route is, if anything, the strongest *counter*-example to this
  page's normalization claim (a passthrough is by construction not normalized),
  but that note makes no claim about `finish_reason` on that route, so there is
  nothing to reconcile. Recorded as an open adjacency: whether
  `/bedrock/invoke` responses carry the five-value set or raw Bedrock values
  is **not** documented in either note.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Cited
  (Extends)**: **Claim 1** establishes the agent spectrum and **Claim 5** that
  the agent acts as a pre-on-caller, triaging before the human. Claim 6 here
  is the mechanism that makes an agent's *own* loop terminate wrongly: a
  malformed tool call normalizes to `stop`, so the loop exits on its success
  path and the pre-on-caller's work is silently short. Complementary, not
  conflicting.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Cited
  (Corroborates + Extends)**: **Claim 2** states that "advisor tokens are
  reachable only via `usage.iterations[]` entries carrying `type:
  \"advisor_message\"`" while top-level `usage` is "executor tokens only".
  That note's Concrete Artifacts also record the advisor's own round-trip via
  `provider_specific_fields` — so this is the **second** member of the
  `provider_specific_fields` container in the corpus after
  `docs-litellm-knowledgebase-vector-stores.md` **Claim 6**'s
  `vector_store_search_failures`, and it materially strengthens Claim 5's
  assessment: the container is the gateway's general out-of-band channel with
  at least three distinct key namespaces, none of which shares the
  `native_finish_reason` divergence-only presence rule. Also note this note's
  **Claim 3** records that page's own `usage` example is *arithmetically
  inconsistent*, which is direct support for grading Claim 12's uniformity
  assertion `anecdotal`: the one LiteLLM `usage` example in the corpus that
  was checked against its own arithmetic is wrong.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Cited (Extends)**:
  **Claim 1** documents the A2A gateway's two per-session loop controls
  (`max_iterations`, `max_budget_per_session`) and **Claim 3** that the
  iteration cap is a per-call counter returning HTTP 429. Claim 6 here is the
  *other* half of loop termination that those controls do not cover: a
  capped counter bounds how long a loop runs, and `finish_reason` decides how
  the loop *ends* — and on this surface it can report `stop` for a call that
  failed to parse. So a session can stay inside its budget and iteration cap
  and still terminate on a malformed step. No conflict; different control
  axis.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **Dismissed**: the A2A
  admin-UI per-agent cost-configuration panel and usage dashboards. Gateway
  cost *declaration* surfaces, not response shape. Nothing shared.
- `source-notes/docs-google-sre-eliminating-toil.md` — **Dismissed**: the SRE
  Workbook chapter on toil characterization and the 50% cap. Retrieved
  lexically; no claim-level relationship to a response contract. Claim 10's
  flag-on proxy does reduce a per-caller accounting chore, but that is our
  inference, not a shared claim, and nothing is cited.
- `source-notes/blog-litellm-auto-router-v2.md` — **Cited (Extends)**:
  **Claim 3** — "predictable beats clever for debuggability", with a fixed,
  versioned capability→model mapping as what makes "why did this response
  cost 4x today" answerable. Claim 4's assessment is the same argument applied
  to `finish_reason`: the five-value set is a deliberate predictability
  contract, and the missing source→target table (Claim 4) plus the
  collapse-to-`stop` behavior (Claim 6) are exactly the debuggability gaps
  that philosophy is meant to close. **Claim 10** of that note (the
  `/v1/messages`→Responses `tool_choice` shape bug) is the precedent for the
  guide's general form of the Claim 11 finding: forwarded-shape ≠
  honored-shape. No conflict.

**Additional cross-references found by searching `source-notes/` and `guide/`**
(the candidates file was not exhaustive; the candidates file covered none of
the following, all found by `grep` for `finish_reason`, `response_ms`,
`native_finish_reason`, and `provider_specific_fields`):

- **Corroborates**:
  - `source-notes/docs-litellm-knowledgebase-vector-stores.md` **Claim 4** —
    "Search results are always in:
    `response.choices[0].message.provider_specific_fields[\"search_results\"]`",
    present on streaming only on the chunk gated on
    `finish_reason == "stop"`. This is independent, same-vendor corroboration
    of two things at once: that `provider_specific_fields` is the gateway's
    out-of-band channel on the response object, and that `stop` is the
    *conforming* value that both the SDK and the streaming collector branch
    on. Its own streaming snippet
    (`if chunk.choices[0].finish_reason == "stop":`) is a second worked
    instance of the five-value set in practice.
  - `source-notes/docs-litellm-knowledgebase-vector-stores.md` **Claim 6** —
    the undocumented `vector_store_search_failures` key in the same container,
    attached out-of-band. Directly supports Claim 5's "container is a general
    channel" and its "absence is normal" reading.
  - `source-notes/docs-litellm-completion-input-params.md` **Claim 7** — the
    JSON-mode callout's "the message content may be partially cut off if
    `finish_reason=\"length\"`". Confirms `length` is in the normalized set and
    that it is the *truncation* signal, which is the second of the five values
    a caller must handle distinctly.
  - `source-notes/docs-promptfoo-guardrails-assertions.md` **Claim 11** — "AWS
    `ApplyGuardrail` returns HTTP 200 with an action, Azure can return a
    successful completion with `finish_reason: content_filter`, and Anthropic
    a successful message with `stop_reason: refusal`". Confirms
    `content_filter` is in the set and, importantly, that it signals an
    *intervention on a successful response* rather than a transport error — so
    `content_filter` is a third value a `stop`-terminating loop must not treat
    as success.
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 8** — the
    Anthropic-native `stop_reason` ∈ `end_turn`, `max_tokens`,
    `stop_sequence`, `tool_use`. This is the *source* side of Claim 4's
    mapping, recorded independently in the corpus, and it is what makes the
    many-to-one argument in Claim 4's assessment concrete.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` **Claim 9** —
    "response.model falls back to `\"unknown-model\"` when missing,
    `stop_sequence` is always `null` on this path". A third independent
    record that LiteLLM's response-side fields are path-dependent, and that
    `stop_sequence` specifically is a value this corpus has now seen in three
    different roles (native Anthropic reason, always-null placeholder,
    and — see Contradicts below — a literal `finish_reason` value in a
    LiteLLM sample payload).
  - `source-notes/docs-litellm-completion-batching.md` **Claim 12** — "the
    samples are illustrative, not evidence" for LiteLLM example payloads.
    Corroborates the treatment of this page's own samples in Claims 2, 8 and 9.
- **Contradicts**: **None filed, and no self-contradiction within the source.**
  Three candidate conflicts were examined and all three resolve to
  conditioning-variable differences or to already-reconciled findings, per
  MINER §4a "when NOT to file". Recorded here so the Assayer can see the work
  rather than infer its absence:
  (a) **The five-value normalization set vs. the literal
  `"finish_reason": "stop_sequence"` in
  `docs-litellm-completion-batching.md`'s Concrete Artifacts** (from
  `/docs/completion/batching`'s all-responses sample, on a
  `"model": "claude-sonnet-5"` response). `stop_sequence` is outside this
  page's declared set and is the Anthropic-native value per
  `docs-litellm-anthropic-unified.md` **Claim 8** — so at first read this
  looks like a genuine conflict on a *closed* enumeration. It is not one, for
  a reason already recorded in the corpus: that note's own **Claim 12**
  characterizes its sample payloads as "stale and internally inconsistent" and
  concludes the operator "should not treat the example payloads as a
  wire-format contract" (it independently notes a float `created` on the same
  samples, exactly as Claim 2 does here). A vendor example that the corpus has
  already disclaimed as illustrative cannot contradict a vendor's normative
  contract statement. The finding is instead folded into Claim 4's assessment
  as the reason to **always keep a default branch** when branching on
  `finish_reason`, which is the honest reading of a totality claim that ships
  with a counterexample in the vendor's own examples. Verified before
  deciding: all eleven open `contradiction`-labeled issues (#1150, #1307,
  #1322, #1338, #1352, #1408, #1461, #1462, #1486, #1514, #1517) and
  `CONTRADICTIONS.md` (no `C-NNN` entries yet) cover none of this surface.
  (b) **The `created`/`model` annotation-vs-sample mismatch (Claim 2)** — this
  is a defect *within* one page, not a disagreement between sources, and the
  Prospector's triage for this issue explicitly directed it to be recorded as
  a documentation caveat rather than filed. Done, in Claim 2.
  (c) **The dual-access guarantee (Claim 3) vs. the three response types in
  the batching note's artifacts** (`ModelResponse`, `OpenAIObject`, bare
  `chat.completion`) — complementary, not opposing: the guarantee is about
  *access syntax*, the artifact difference is about *runtime class*, and both
  are satisfied simultaneously by the same object.
- **Extends**:
  - `source-notes/docs-litellm-drop-params.md` **Claim 9** (per #1495's
    Cross-References) — that note's most consequential claim is an *absence*:
    the gate page documents no log line, metric, response field or header for
    a drop, so "param honored" and "param silently stripped" are
    indistinguishable. This page is a partial answer on the *response* side of
    the same problem class: `native_finish_reason` (Claim 5) and
    `response_ms` (Claim 7) are two response-carried signals, and
    `x-litellm-attempted-fallbacks` (from #1495 Claim 13) is a third on the
    header side. What the trio establishes is an asymmetry worth stating once
    in the guide: **some gateway behaviors are attributable from the response
    and some are not**, and a response-contract chapter should classify each
    documented behavior by whether it leaves a trace. This page is also the
    first source note to state the *positive* side of that ledger for the
    `/chat/completions` response object specifically.
  - `source-notes/docs-litellm-completion-batching.md` **Claim 7** — the same
    comma-separated `model` string yields two different JSON types depending
    on a flag (list of `ChatCompletion` vs. a single `chat.completion`). That
    note documents response *type* variance across LiteLLM surfaces; this page
    documents that even the single-object form's field set is not fully
    enumerated (Claim 1). Together: a consumer of LiteLLM responses must
    branch on both shape *and* field set, and neither is discoverable from
    this page alone.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` **Claim 7**
    ("Capturing both is how you debug behavior changes after a silent
    provider-side model upgrade") and **Artifact 5 → Optional Span
    Attributes Registry** (cited by section name per MINER §4b, not by claim
    number, because it is an artifact table rather than a numbered claim) —
    that table defines `gen_ai.response.finish_reasons` as **`string[]`**
    ("Why the model stopped, e.g., `[\"stop\"]`, `[\"tool_calls\"]`") alongside
    `gen_ai.response.model`. This note's Claims 1, 2 and 4 are the SDK-side
    substrate for exactly those two attributes, and they surface a **concrete
    mapping mismatch the corpus has not recorded**: OTel models finish reason
    as an *array*, while the LiteLLM/OpenAI response carries a **scalar**
    `finish_reason` per element of `choices[]`. So a collector mapping
    `response.choices[0].finish_reason` → `gen_ai.response.finish_reasons`
    must wrap the scalar, and must decide a policy for `n > 1`, where the
    response holds several scalar reasons and the attribute accepts a list —
    a decision no source in the corpus documents. And because of Claim 5,
    `native_finish_reason` is the only field that can recover *why* a mapped
    `stop` happened, with the absence-is-not-signal caveat attached. That makes
    this note the first in the corpus to say anything actionable about
    **populating a standard finish-reason attribute from a LiteLLM response**,
    which Ch02 does not currently cover (`guide/` contains zero occurrences of
    `finish_reason`).
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claim 3** — the
    `model_cost` map mirrored as the `model_prices_and_context_window.json`
    community resource. Claim 11 here identifies that same file as the input to
    LiteLLM's *request*-side endpoint-bridging decision, so one community file
    governs both local cost math and gateway route selection. Claim 5 of that
    note ("By default LiteLLM returns token usage in all completion requests")
    is also the counterpart Claim 10 narrows: true for non-streaming, and
    flag-dependent for streaming.
- **Novel** (verified by re-running the searches this session: zero hits in
  `source-notes/` for `native_finish_reason` and `response_ms`, and zero hits
  in `guide/` for `native_finish_reason`, `response_ms`, **and
  `finish_reason` itself**):
  1. The **`finish_reason` normalization contract** — a closed five-value
     OpenAI target set that all provider-native values are mapped onto
     (Claim 4). The corpus had five occurrences of the string `finish_reason`
     and **zero** occurrences of any mapping rule.
  2. **`provider_specific_fields["native_finish_reason"]`** and its
     divergence-only presence condition, including the vendor's explicit
     negative case (Claim 5). Brand new, and the first documented statement in
     the corpus that a response field's *absence* is uninformative.
  3. **A malformed tool call normalizing to `stop`**, with the vendor's own
     agent-loop sample demonstrating it (Claim 6).
  4. **`response.response_ms`** as a per-call latency float on the response
     object (Claim 7).
  5. **The dict-or-class dual-access guarantee** as an explicit documented
     contract (Claim 3).
  6. **`always_include_stream_usage`** as a proxy `general_settings` flag that
     makes streamed `usage` availability a deployment property (Claim 10).
  7. **Endpoint bridging** as a silent, file-driven request-routing
     substitution authority (Claim 11).

## Guide Impact

- **Chapter 05 (llm-ops-reliability)**: The "Silent model fallback breaks
  attribution" section (rule at ~L982) currently gives exactly one
  response-side check — "Surface the `model` field from the response
  metadata in observability dashboards — do not infer it from the request."
  Three additions, each with a source behind it.
  (1) **The rule is incomplete as written**, because the field it depends on
  is not type-promised: this page declares `created: str` / `model: str` with
  `# String: None` and then shows a float epoch and a concrete id (Claim 2).
  Recommend the rule read "read `response.model` defensively — the documented
  type allows `None` and the documented example is not a string — and fall
  back to flagging the span as unattributed rather than assuming a value."
  (2) **Add `system_fingerprint` to the same rule.** It is the field
  #1495 **Claim 10** names as *the* backend-drift detector, and this page —
  the one that claims the "exact json output" — does not document it (Claim
  1), which means the drift-detection field has no page of record. Until a
  Smith has a documented shape for it, the rule should be explicit that drift
  detection is best-effort.
  (3) **Name a fourth substitution authority.** The section currently names
  three (response-`model` fallback, `prompt_template_model`, prompt-param
  precedence). This note adds a fourth that is *request-side* and
  file-driven: `mode`-based endpoint bridging in
  `model_prices_and_context_window` silently reroutes a request to a
  different endpoint family with no response signal (Claim 11). Because
  endpoint parity tests are naturally written against a fixed model string,
  recommend the chapter state that route resolution must be audited per
  resolved model entry, not per requested endpoint.
- **Chapter 02 (observability)**: The chapter's span schema (LLM spans carry
  "metrics (`input_tokens`, `output_tokens`)") names **no latency field** on
  the LLM span, and `guide/` has zero occurrences of `finish_reason`. Two
  concrete additions. (1) **Populate `gen_ai.response.finish_reasons` from
  `choices[0].finish_reason`, and document the two decisions the mapping
  requires**: wrap the scalar in an array, and choose a policy for `n > 1`
  (Claim 4 + honeycomb Artifact 5). (2) **Record
  `provider_specific_fields["native_finish_reason"]` when present**, with an
  explicit note in the chapter that its absence means nothing (Claim 5) —
  the collector must not emit a "clean stop" signal on its absence, and should
  separately alert on other `provider_specific_fields` keys (the corpus
  already has a documented precedent for exactly that in
  `docs-litellm-knowledgebase-vector-stores.md` **Claim 6**'s
  `vector_store_search_failures`). (3) For LiteLLM SDK callers, name
  `response.response_ms` as the available per-call latency field while stating
  plainly that it is a client-side measurement whose composition the vendor
  does not define, and is not a substitute for proxy metrics (Claim 7).
- **Chapter 03 (runbooks-and-agents)**: The chapter has no stop-condition
  material today (zero matches for "stop condition" / "stop_reason" / "agent
  loop"). This page supplies the missing content: **`finish_reason` is not a
  sufficient success predicate for a tool-using agent loop**, because the
  vendor's own example shows a `MALFORMED_FUNCTION_CALL` — a failed tool call
  — mapped to `stop` (Claim 6). Recommend a runbook step that asserts a
  non-empty, *parsed* tool-call set before treating a stop as success, and
  that records `native_finish_reason` so malformed invocations are countable
  after the fact. Note the honest limit for the Smith: this page defines
  `tool_calls` as a `finish_reason` value but never documents a `tool_calls`
  field on the response (Claim 1), so the assertion currently has no
  documented field to read — the chapter should state the requirement and flag
  the field as an open documentation gap rather than invent a shape.
- **Chapter 05, spend/spend-accounting**: `docs-litellm-completion-input-params.md`
  **Claim 9**'s assessment concludes streamed usage coverage is "per-caller
  opt-in, not per-provider." Recommend the guide add the third axis: a proxy
  running `general_settings: always_include_stream_usage: true` makes usage
  coverage a **deployment** property, and it is the only one of the three an
  operator controls fleet-wide (Claim 10). Pair it with the collector rule
  from Ch02 above: do not infer "was usage requested?" from the request body,
  because the flag is injected server-side.
- **Cross-cutting, for the Smith**: this note is the corpus's first
  response-contract reference. If a response-shape subsection is ever added,
  it must be assembled as the **union** of this page's four keys and the
  `id` / `object` / `system_fingerprint` triple observed in the batching
  page's artifacts, with `tool_calls` marked as a known gap (Claim 1) — not
  from this page alone, which claims "exact" coverage and does not deliver it.

## Extraction Notes

- The page is **short** — three sections ("Format", "Native Finish Reason",
  "Additional Attributes"), roughly one screen of prose plus five code blocks.
  The Prospector's triage explicitly warned against padding, so the note does
  not: 12 claims is what the page supports, and each maps to a distinct
  sentence, code block, or a documented internal inconsistency rather than to
  a re-derivation. Where the page is thin, the claim records the thinness
  (Claims 7, 8, 12) instead of manufacturing depth.
- **Sub-page followed** (MINER §1): the `Next` sibling
  `https://docs.litellm.ai/docs/completion/usage` was fetched and read in full
  and yielded three claims (10, 11, 12) plus the `config.yaml` and `curl`
  artifacts. Two of those three are corpus-novel. The other two siblings were
  checked and not followed further: `/completion/input` is already mined
  (#1495) and this note cites it rather than re-extracting it, and
  `/completion/http_handler_config` is already mined (#1482) and is a
  transport-configuration page with no response-shape content.
- **Quote fidelity**: every `Quote` field and every quoted passage was copied
  from the live page this session. The five code blocks were extracted from the
  raw HTML's `<pre>` elements specifically, to confirm that the collapsed
  whitespace is the page's own state and not an artifact of the markdown
  fetch (it is the page's own — see Claim 9). No quote is reconstructed or
  spliced. The two `mode`set` / `mode``set` occurrences in Claim 11's quote
  preserve the page's own missing space.
- **Attempted and failed**: the upstream markdown sources
  (`raw.githubusercontent.com/BerriAI/litellm/main/docs/my-website/docs/
  completion/output.md` and the `usage` equivalent) both returned **HTTP
  404**, so the rendered page is the only available source and no
  `date_published` could be recovered. Recorded as `unknown` in frontmatter.
- **Contradiction issues filed: none.** One candidate conflict was examined
  and dismissed with reasoning (the `stop_sequence` value in the batching
  note's sample artifacts vs. this page's closed five-value set); see
  Cross-References → Contradicts (a) for the full argument and the
  `contradiction`-label issue audit performed before deciding.
- **Not extracted, deliberately**: this page carries no pricing, no marketing
  and no provider-support matrix, and the `LiteLLM Enterprise` / `Trust
  Center` / `SOC 2 Type II` chrome in the site footer was ignored per the
  issue's crawl scope. The `Explore docs` / `Models & Pricing` nav and the
  Changelog link were not followed — the triage scoped this to
  routing/reliability behavior, and a changelog would be a separate source.
- **Confidence**: rated `emerging` overall, consistent with every other
  LiteLLM vendor-docs note in the corpus and with the Prospector's caveat.
  The specific downgrade is Claim 12 and the "all"/"for all models" clauses
  of Claims 4 and 8, which are graded `anecdotal` for provider-uniformity
  (a vendor assertion with no matrix, no wire capture and no third-party
  confirmation) using the precedent already set in
  `docs-litellm-completion-input-params.md` **Claim 1** and
  `docs-litellm-streaming-token-usage.md` **Claim 3**. Claims 2, 3, 5, 6 and
  9 are `settled` as *documentation* observations — each is directly
  re-checkable against the fetched page. The corpus's precedent for reading
  first-party docs this way is `docs-litellm-completion-batching.md` **Claim
  12** (a documentation defect graded `settled`) versus **Claim 6** (a runtime
  behavior graded `emerging`).
