---
source_url: https://docs.litellm.ai/docs/completion/json_mode
source_type: docs
title: "Structured Outputs (JSON Mode) — liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-29)
date_extracted: 2026-09-29
last_checked: 2026-09-29
status: current
confidence_overall: emerging
issue: "#1496"
---

# Structured Outputs (JSON Mode) — `/v1/chat/completions` (liteLLM Docs)

> The `/v1/chat/completions` structured-output page documents three things a
> gateway operator needs and cannot get from an endpoint contract: (1)
> capability is discoverable only at **runtime**, through two *different*
> predicates — `get_supported_openai_params` for bare `response_format` and
> `supports_response_schema` for the strict `json_schema` form — plus a
> separately hosted `model_prices_and_context_window.json`; (2) the strictness
> guarantee is a **config flag that moves enforcement from the provider to the
> caller** — `litellm.enable_json_schema_validation=True` /
> `litellm_settings: enable_json_schema_validation: True` makes LiteLLM
> "validate the json response using `jsonvalidator`" client-side, and the page
> documents **no error type, status, or retry contract** for a validation miss;
> (3) a same-vendor, **version-keyed schema-dialect split** — Gemini 2.0+ gets
> native `responseJsonSchema` (standard JSON Schema, `additionalProperties`
> ✅) while Gemini 1.5 gets `responseSchema` (OpenAPI dialect,
> `additionalProperties` ❌), "automatically select[ed]" by model version. The
> support list itself is a flat 10-provider "Works for:" with no ❌ cells, no
> native-vs-post-hoc distinction, and no per-model granularity — so a gateway
> cannot assume `response_format` means the same thing on two backends behind
> one endpoint, and cannot tell from the docs whether a given row is enforced
> or merely re-checked after the fact.

## Source Context

- **Type**: docs (single-page LiteLLM gateway parameter/feature reference at
  `/docs/completion/json_mode` — verified HTTP 200 this session, matching
  `source_url`). Site breadcrumb: "Guides → Core Requests → Structured Outputs
  (JSON Mode)". Nav siblings: `completion/batching` (Previous) and
  `reasoning_content` (Next). Every section is duplicated as an SDK + PROXY
  (+ curl) triple; 17 code blocks on the page.
- **Author credibility**: LiteLLM (BerriAI) first-party product
  documentation. Authoritative for the *documented* surface: the parameter
  shape, the support list, the two introspection helpers, the validation knob's
  two placements, the Gemini dialect table, and a permalink into the
  implementing source
  (`litellm/litellm_core_utils/json_validation_rule.py#L4`, pinned to commit
  `671d8ac496b6229970c7f2a3bdedd6cb84f0746b`). Vendor documentation of the
  product's own behavior — no independent validation, no metrics, no test
  output, no failure write-ups, and the page is undated.
- **Scope**: Structured output on the OpenAI-compatible
  `POST /v1/chat/completions` surface: `response_format={"type":"json_object"}`,
  `response_format={"type":"json_schema", ...,"strict":true}`,
  `response_format=<Pydantic Model>`; the two runtime capability checks; the
  provider support list; the client-side validation fallback; and the Gemini
  2.0+ / 1.5 native-format split. Does **NOT** cover: the Anthropic-shaped
  `output_format` on `/v1/messages` (that is
  `docs-litellm-anthropic-unified-structured-output.md`, #1391), the
  unsupported-parameter gate (`docs-litellm-drop-params.md`, #1480), streaming
  behavior, error/failure semantics, telemetry, or fallback behavior.
- **Redundancy**: Not a duplicate of #1391. Different endpoint
  (`/v1/chat/completions` vs `/v1/messages`), different parameter name
  (`response_format` vs `output_format`), and this page adds the
  client-side-validation fallback that #1391 has no counterpart for. A corpus
  grep for `response_format` / `json_schema` in `source-notes/` returns only
  incidental hits: `docs-litellm-drop-params.md` (as the parameter name in its
  `additional_drop_params=["response_format"]` example) and
  `docs-litellm-messages-to-responses-mapping.md` (a single `output_format` →
  `text` mapping row). No existing note owns this page's surface.
- **Contradiction scan (MINER §4a)**: No contradiction issue filed. Every
  apparent tension was checked and each resolved as a *different surface* or
  *different layer*, not an opposing claim:
  1. This page's 10-item "Works for:" list vs #1391's four-row Anthropic-family
     `output_format` table — different endpoint **and** different parameter
     name. They agree where they overlap (Anthropic, Bedrock both appear in
     both). The same reconciliation #1391 already recorded for its own
     parent page, applied again: an endpoint's advertised provider fan-out is
     not a per-feature support matrix, and here the parameter names differ too.
  2. `blog-litellm-claude-fable-5-day-0.md` Claim 12 ("structured output, all
     available across Anthropic, Azure, **Vertex AI**, and Bedrock") vs this
     page's 10-item list — Fable-5's four names are a **subset** of this list,
     not a competing enumeration; Fable-5 makes no exclusivity claim. The
     Vertex-AI discrepancy #1391 flagged is *resolved* in Fable-5's favor by
     this page: "Vertex AI models (Gemini + Anthropic)" is a row here.
  3. `docs-litellm-drop-params.md` Claim 1 (unsupported params raise by default)
     vs this page's unconditional 10-provider list — different gates. The
     drop gate is a *supported-params* validation keyed on a per-provider-and-
     -model matrix; this page is a *schema-enforcement* surface. The page
     makes no claim that the two share a gate, and its validation section
     describes a third mechanism (client-side re-validation). Layer difference
     per §4a "when NOT to file."
  4. Within-source: "Works for: [10 providers]" (no qualification) vs
     "Not all models support passing the json_schema to them natively" — this
     is complementarity, not self-contradiction: the first is a support list,
     the second says support is not uniformly *native*. The defect is that
     the page never maps the two together (which rows are native, which are
     post-hoc), which is recorded as a documentation gap in Claims 2 and 4,
     not filed.
  Verified no open `contradiction`-labeled issue covers this surface (#1150,
  #1307, #1322, #1338, #1352, #1408, #1461, #1462, #1486 — routing, A2A,
  `thinking.summary`, advisor tool, promptfoo); `CONTRADICTIONS.md` has no
  matching `C-NNN` entries.

## Extracted Claims

### Claim 1: Structured-output capability is discoverable only at runtime, and the page requires **two different predicates** — `get_supported_openai_params` for bare `response_format`, `supports_response_schema` for the strict `json_schema` form — plus an externally hosted JSON file
- **Evidence**: Two numbered subsections under "Check Model Support", each with
  its own one-line purpose statement and one code block, followed by a pointer
  to a raw GitHub-hosted file. Neither helper is a superset of the other in
  the page's own framing: the first is scoped to `response_format`, the second
  to `json_schema` / Pydantic-model form.
- **Confidence**: settled (explicit first-party documentation of both helpers
  and their distinct scopes)
- **Quote**: "Call `litellm.get_supported_openai_params` to check if a model/provider supports `response_format`." / "This is used to check if you can pass" / "Check out `model_prices_and_context_window.json` for a full list of models and their support for `response_schema`."
- **Our assessment**: This is the documented answer to "can I send this to
  that backend?", and the two-helper split is the load-bearing detail: a
  gateway that gates on `get_supported_openai_params` alone will report
  `response_format` supported while `json_schema` silently degrades on the
  same model, because the page documents them as separate checks with separate
  scopes. Both examples key on `(model, custom_llm_provider)` — i.e. the
  predicate is **per provider-and-model**, matching
  `docs-litellm-drop-params.md` Claim 2's support-matrix keying, so "provider X
  supports structured output" is not a usable precondition. Note also that the
  two introspection examples pass a **bare model ID plus a separate
  `custom_llm_provider=` argument** (`model="anthropic.claude-sonnet-5",
  custom_llm_provider="bedrock"`, `model="gemini-3.1-pro-preview",
  custom_llm_provider="bedrock"`) while every routing example on the page uses
  a **prefixed model string** (`gemini/gemini-3.8-flash`, `gpt-5.6-terra`) —
  two naming conventions on one page, and a tripped wire for anyone
  copy-pasting a `config.yaml` model name into the check. And
  `model_prices_and_context_window.json` is the third, *separately versioned*
  source of truth — a moving remote artifact the page does not version-pin,
  so "what did the docs say last month" has no stable answer for it.

### Claim 2: The support statement is a flat, unqualified 10-item "Works for:" list — no ❌ cells, no per-model granularity, and no native-vs-post-hoc distinction, even though the same page says native support is not universal
- **Evidence**: The complete "Works for:" bullet list under "Pass in
  'json_schema'", followed three sections later by "Not all models support
  passing the json_schema to them natively." The two statements are never
  reconciled: the list has no column, annotation, or footnote for enforcement
  location.
- **Confidence**: settled (the list is verbatim documentation; the
  unreconciled gap is the finding)
- **Quote**: "Works for:" / "OpenAI models" / "Azure OpenAI models" / "xAI models (Grok-2 or later)" / "Google AI Studio - Gemini models" / "Vertex AI models (Gemini + Anthropic)" / "Bedrock Models" / "Anthropic API Models" / "Groq Models" / "Ollama Models" / "Databricks Models"
- **Our assessment**: A support list with no negative rows and no
  enforcement-location column is a *capability advertisement*, not a
  contract. Three concrete consequences for a Ch05 provider-parity argument.
  (1) "Works for: Databricks Models" is a *provider* row — but the page's own
  check helpers are keyed on provider **and model**, so the row cannot be read
  as "every Databricks model." (2) "Bedrock Models" is one row, while the
  corpus already knows LiteLLM exposes **three distinct Bedrock routes** with
  different wire formats (see Cross-References) — the row does not say which
  route it means or whether structured output is uniform across them.
  (3) Because no row is marked native or post-hoc, an operator reading only
  this list will assume provider-side enforcement for all ten. The one
  per-model verdict on the page (the Gemini table, Claims 6-7) is a *format*
  statement, not a *support* statement, and it is scoped to a single vendor.
  The correct guide reading: treat "Works for:" as a routing-eligibility hint
  and gate the actual feature with the two runtime predicates (Claim 1).

### Claim 3: Where a provider cannot enforce the schema natively, the strictness guarantee moves from the provider to the caller — a **post-hoc, caller-side** check on a config flag, implemented with `jsonvalidator`
- **Evidence**: The "Validate JSON Schema" section: the gap statement, the
  one-line knob, the mechanism sentence, and a permalink into the implementing
  module. Two placement examples follow — an SDK module-global assignment and
  a `litellm_settings` proxy block.
- **Confidence**: settled (explicit first-party statement of both the knob and
  the mechanism)
- **Quote**: "Not all models support passing the `json_schema` to them natively. To solve this, LiteLLM supports client-side validation of the json schema." / "If `litellm.enable_json_schema_validation=True` is set, LiteLLM will validate the json response using `jsonvalidator`."
- **Our assessment**: The load-bearing security/ops claim, and it is a
  **posture change, not a repair**. With the flag off, the caller's guarantee
  is whatever the provider does — and if the provider does nothing, the caller
  receives a 200 with a string that violates the schema. With the flag on,
  the check happens *after* the response exists, in the caller's own process,
  against a third-party validator whose failure behavior the page never
  describes (Claim 4). So the flag does not move the guarantee back to the
  provider; it moves it from *nobody* to *you, locally, too late to have
  influenced generation*. Two operational points the page leaves open and the
  guide should say out loud: (a) the flag is **process-global** in SDK mode
  (`litellm.enable_json_schema_validation = True`) and **proxy-global** in
  proxy mode (`litellm_settings`) — it cannot be scoped per model or per
  request, so one deployment's post-hoc validation contract applies to every
  model the proxy serves, including the ten rows that *are* natively enforced.
  This is the same four-placements-no-precedence hazard
  `docs-litellm-drop-params.md` Claim 3 documents for `drop_params`, reduced
  to two placements here and with the same missing precedence statement.
  (b) Validation that happens after generation cannot influence generation:
  it is a **detection** control, not a **shaping** control. Any guide advice
  that treats `enable_json_schema_validation` as an output-safety guarantee is
  overstating it.

### Claim 4: The page documents **no failure contract at all** for the validation fallback — no error type, no exception name, no HTTP status, no partial-response behavior, no retry guidance — recorded as an explicit absence
- **Evidence**: Full-page read. The "Validate JSON Schema" section contains a
  gap statement, a one-line knob, a one-sentence mechanism, a source
  permalink, and two runnable examples. Neither example shows a response, a
  failure, or a raised error. The page names exactly one error-adjacent
  mechanism (the `jsonvalidator` library) and zero exception types; the words
  "error", "exception", "raise", "retry", and "invalid" do not appear in any
  prose on the page.
- **Confidence**: settled as an **absence** claim (the page is short and
  fully read; the omission is checkable by re-reading it). It is an absence in
  *documentation*, not a claim that LiteLLM emits nothing.
- **Quote**: (no direct quote; the absence is in what the page does not
  contain — see the five-item section inventory under "Validate JSON Schema"
  reproduced in Concrete Artifacts)
- **Our assessment**: This is the gap the guide most needs, and the reason
  this note is `emerging` rather than `settled`. The Prospector's key
  question — *does a schema violation surface as a non-200, or as a 200
  carrying an unvalidated string that only fails later at
  `model_validate_json(...)`?* — is **not answered by the page in either
  direction**. What we can say from the documentation: with the flag **off**,
  nothing in the page promises enforcement, and the page's own Pydantic
  example has the caller validate the returned string itself
  (`EventsList.model_validate_json(resp.choices[0].message.content)`,
  Claim 8) — i.e. the documented happy path *is* a 200-plus-caller-parse.
  With the flag **on**, whether a validation miss becomes a 4xx/5xx, an
  exception, or a silently returned invalid payload is undocumented. A guide
  rule must therefore be written as an **open verification item**, not a
  guarantee, and an operator who depends on it must measure the actual failure
  mode on their own stack before alerting on it. Corroborates the
  "capability documented, governance absent" pattern already recorded for the
  sibling `docs/completion/*` page in
  `docs-litellm-completion-batching.md` Claim 4 (documented cancellation, no
  published billing semantics) and Claim 9 (documented N-way race, no
  concurrency/limit/fallback semantics).

### Claim 5: The SDK example that demonstrates the validation fallback is the page's only introspection affordance — it enables `set_verbose` to see the raw request — and it carries a provider-prefix/auth mismatch: a `gcloud auth … vertex credentials` comment above a `gemini/`-prefixed model
- **Evidence**: The SDK code block's first line is the gcloud comment; the
  `completion(...)` call uses `model="gemini/gemini-3.1-pro-preview"`, which is
  the Google AI Studio prefix, not `vertex_ai/`. The page's own "Works for:"
  list keeps "Google AI Studio - Gemini models" and "Vertex AI models (Gemini +
  Anthropic)" as two separate rows, and the *proxy* example for the same
  feature registers `model: "gemini/gemini-3.8-flash"` with an API key, not
  ADC. The block also sets `litellm.set_verbose = True` with an inline
  comment.
- **Confidence**: settled (both strings verbatim; the mismatch is a
  re-checkable property of the page's own code, not an inference about
  LiteLLM behavior)
- **Quote**: "# !gcloud auth application-default login - run this to add vertex credentials to your env" / "litellm.set_verbose = True # see the raw request made by litellm" / 'model="gemini/gemini-3.1-pro-preview"'
- **Our assessment**: Two things worth carrying forward. First, `set_verbose`
  is the page's answer to "what did LiteLLM actually send?" — the same
  verify-after-routing reflex
  `docs-litellm-drop-params.md` Claims 6 and 9 arrive at from the other
  direction (a drop leaves no marker, so diff the outbound payload). On a
  structured-output route, the *outbound schema* and the *inbound payload* are
  both load-bearing and neither is echoed in the response, so `set_verbose`
  is the documented way to close the loop. Second, the prefix mismatch is a
  small but real trap for a runbook: an operator following the comment
  provisions Vertex ADC credentials and then routes to a `gemini/` model,
  which is a different auth path and a different LiteLLM provider. It also
  echoes the corpus's existing Bedrock lesson
  (`blog-litellm-claude-fable-5-day-0.md` Claim 11: on Bedrock the model must
  be invoked through an inference-profile prefix; the bare ID errors) — a
  provider prefix is a routing contract, not cosmetic. Do not assert the
  example is wrong; record that the comment and the model string point at
  two different providers and that the page never reconciles them.

### Claim 6: The page documents a same-vendor, version-keyed **schema-dialect split** for Gemini — 2.0+ uses native `responseJsonSchema` (standard JSON Schema), 1.5 uses `responseSchema` (OpenAPI) — selected automatically by model version, with `additionalProperties` supported on one and not the other
- **Evidence**: A dedicated section heading scoped to Gemini 2.0+, a four-item
  benefits list, and a two-row "Model Behavior" table whose columns are
  `additionalProperties` Support, closing with the auto-selection sentence.
- **Confidence**: settled (explicit two-row table plus an explicit
  auto-selection statement)
- **Quote**: "Gemini 2.0+ models automatically use the native `responseJsonSchema` parameter, which provides better compatibility with standard JSON Schema format." / "`responseJsonSchema` (JSON Schema)" / "`responseSchema` (OpenAPI)" / "LiteLLM automatically selects the appropriate format based on the model version."
- **Our assessment**: The concrete instance of the "provider parity by model
  *version*" class that `failure-litellm-vllm-embeddings-encoding-format.md`
  argues for — same vendor, same product line, sibling model generation, and a
  parameter that is meaningful on one and unusable on the other. The
  operational shape is worse than a plain "unsupported": it is an
  **implicit, version-keyed behavior switch**. The caller sends one
  `response_format` and LiteLLM *translates* it into a different vendor
  parameter, on a different schema dialect, with different keyword support,
  chosen by a model-version test the caller cannot see, override, log, or
  assert on. A caller who relies on `additionalProperties: false` for
  strictness and is silently routed to a 1.5-era model gets a schema that is
  **weaker than the caller believes** — the constraint is not honored, not
  rejected, and the ❌ cell is a capability statement, not a documented error.
  This is the same dialect-drift shape the corpus records for OpenAI↔Anthropic
  translation (`docs-litellm-messages-to-responses-mapping.md`) applied
  *within* one vendor. It also compounds with `drop_params`: if a
  version-dialect downgrade silently weakens a schema and
  `additional_drop_params` can name `response_format` for removal
  (`docs-litellm-drop-params.md` Claim 4), the operator can in one config
  change remove the whole feature without an error.

### Claim 7: The four Gemini-2.0+ "benefits" are stated as **format-compatibility** properties, not enforcement properties — the strongest one is "No `propertyOrdering` required"
- **Evidence**: The four-item "Benefits (Gemini 2.0+):" list. Three describe
  syntax compatibility with standard JSON Schema and Pydantic output; none
  describes an enforcement guarantee, an error, or a validation result.
- **Confidence**: settled (the list is verbatim; the format-vs-enforcement
  reading is the Miner's assessment of what the items do and do not claim)
- **Quote**: "Standard JSON Schema format (lowercase types like `string`, `object`)" / "Supports `additionalProperties: false` for stricter validation" / "Better compatibility with Pydantic's `model_json_schema()`" / "No `propertyOrdering` required"
- **Our assessment**: Read carefully, the list is about the *shape of the
  request LiteLLM will send upstream*, not about what the provider will do
  with it. "Better compatibility with Pydantic's `model_json_schema()`" is
  about serializing your Pydantic class, not about the response honoring it.
  The one item that touches strictness — "Supports `additionalProperties:
  false` for stricter validation" — describes a keyword that survives the
  translation on 2.0+ and is ❌ on 1.5; it does **not** say the provider
  enforces it. This is the same gap `docs-litellm-anthropic-unified-structured-output.md`
  Claim 3 recorded for `additionalProperties: false` on `/v1/messages` —
  "enforce strict schema adherence" is documented as an instruction with no
  stated enforcement location. Two notes for the guide. (a) Both Gemini
  examples on this page (SDK and PROXY) omit the `strict` key entirely while
  every OpenAI example sets `"strict": true` explicitly — so the
  `strict` knob's behavior on the Gemini path is undocumented, and the
  SDK's `.parse()` / `model_validate_json()` layer is doing whatever
  strictness the caller gets. (b) The corollary of the auto-selection is that
  a schema pinned to the 2.0+ dialect is not portable to a 1.5 route *through
  the same gateway* — the caller cannot express "require 2.0+ semantics"
  in the request, because the version is a routing decision, not a request
  field.

### Claim 8: The feature has three documented request shapes, and the Pydantic shape's happy path is explicitly "the gateway returns a string, the caller validates it" — `model_validate_json(resp.choices[0].message.content)`
- **Evidence**: The Quick Start uses `response_format={"type":"json_object"}`;
  the "Pass in 'json_schema'" section uses the raw dict
  `response_format: { "type": "json_schema", "json_schema": … , "strict": true }`;
  the same section's SDK example passes a Pydantic class
  (`response_format=EventsList`) and then calls
  `EventsList.model_validate_json(resp.choices[0].message.content)` on the
  returned message content.
- **Confidence**: settled (three verbatim request shapes plus the
  client-side validate call)
- **Quote**: "To use Structured Outputs, simply specify" / "response_format: { \"type\": \"json_schema\", \"json_schema\": … , \"strict\": true }" / "response_format=EventsList" / "events_list = EventsList.model_validate_json(resp.choices[0].message.content)"
- **Our assessment**: This is the page's most transferable finding, and it
  lands exactly where the corpus already is. Three shapes with three
  different enforcement stories, all behind one endpoint: `json_object` is
  loose (no schema at all — the Quick Start's only guardrail is a system
  prompt saying "You are a helpful assistant designed to output JSON."), the
  raw dict is the provider-facing strict form, and the Pydantic form is a
  **caller-side contract**: LiteLLM hands back
  `choices[0].message.content` as a string and the caller's own Pydantic
  validator is what decides whether it conforms. That is the same
  "200 with an unvalidated string" delivery shape
  `docs-litellm-anthropic-unified-structured-output.md` Claim 4 documents for
  the `/v1/messages` surface, here reached on the `/v1/chat/completions`
  surface through the *documented happy path* rather than through a gap. Two
  guide-level consequences. (1) A schema-violating structured response is
  **not** a 5xx and carries no distinct field, so it is invisible to
  gateway error metrics and to span-based observability (cf.
  `docs-datadog-llm-observability.md` Claim 3: a span is the unit of work, and
  error detail is an attribute instrumentation sets — nothing sets one here).
  Instrument parse-success/schema-adherence as a first-class metric.
  (2) If you use the Pydantic shape, the validation is **yours**, in **your**
  process, after the tokens are already billed — the page's own code is the
  proof, and it is the good version of the pattern, because the validator
  call is visible in the client. The bad version is relying on
  `enable_json_schema_validation` as if it moved the check upstream (Claim 3).

### Claim 9: The proxy's documented OpenAI-SDK path routes structured output through a **`beta`** endpoint and a client-side `.parsed` field — a second, independent validation layer that the page never distinguishes from LiteLLM's own `jsonvalidator`
- **Evidence**: The "PROXY" tab's "OpenAI SDK" block instructs swapping
  `base_url` and calls `client.beta.chat.completions.parse(...)`, reading
  `completion.choices[0].message.parsed`. The same page's "Validate JSON
  Schema" section introduces `jsonvalidator` as LiteLLM's mechanism. The two
  are never mentioned in the same sentence.
- **Confidence**: settled (both mechanisms verbatim; the observation that the
  page does not relate them is the finding)
- **Quote**: "Just replace the 'base_url' in the openai sdk, to call the proxy with 'json_schema' for openai models" / "completion = client.beta.chat.completions.parse(" / "math_reasoning = completion.choices[0].message.parsed"
- **Our assessment**: The page documents **three** places a schema can be
  checked on this route — the provider (native, for the ten "Works for" rows),
  the OpenAI SDK's `.parse()` in the client process, and LiteLLM's
  `jsonvalidator` when the flag is on — and never says which one applies to a
  given request, or whether they compose. That is a genuine ambiguity, not a
  nit: an operator debugging "why did this response not conform?" has three
  candidate checkers and no documented precedence. Two flags for the guide.
  (1) `beta.chat.completions.parse` is on a **beta** namespace; a runbook that
  depends on `.parsed` inherits that surface's stability, which is worth a
  one-line note since the rest of the page's curl path is a stable
  `POST /v1/chat/completions`.
  (2) `.parsed` being a *field on the response object* (rather than a value
  the caller must parse out of a string) is the one place on this page where
  a schema-conformance signal reaches the caller. That is a meaningfully
  different observability posture from Claims 3/4/8 — and the page does not
  say whether `.parsed` is populated by the proxy, by the SDK, or requires the
  LiteLLM flag. Recorded as an open question, not a claim.

### Claim 10: The proxy's four curls use **two different auth env-var names**, and the OpenAI-SDK example states the proxy key "can be anything, if master_key not set"
- **Evidence**: The Quick Start curl uses `$LITELLM_KEY`; the "Pass in
  'json_schema'" curl, the "Validate JSON Schema" curl, and the Gemini PROXY
  curl all use `$LITELLM_API_KEY`. The SDK block annotates its key value
  inline.
- **Confidence**: settled (verbatim header strings; the divergence is a
  re-checkable property of the page's own four blocks)
- **Quote**: "-H \"Authorization: Bearer $LITELLM_KEY\"" / "-H \"Authorization: Bearer $LITELLM_API_KEY\"" / "api_key=\"anything\", # 👈 PROXY KEY (can be anything, if master_key not set)"
- **Our assessment**: Cosmetic in isolation, load-bearing in a runbook. Four
  copy-pasteable request examples on one page use two names for the same
  credential, and the SDK example explicitly invites *any* string when
  `master_key` is unset — so a reader cannot tell from the page whether the
  gateway is authenticated. The conditional ("if master_key not set") is the
  important half: it means the page's own auth story is configuration-
  dependent, and an operator who skips the condition ships a proxy with an
  open endpoint. This is a small instance of a rule the corpus already
  supports (`docs-litellm-gateway-auth-reference.md` owns the auth surface);
  record the divergence, do not assert either name is wrong, and point the
  guide at the auth reference for which headers the proxy actually accepts.

### Claim 11: The "Validate JSON Schema" PROXY curl is **not runnable as printed** — two trailing commas make the request body invalid JSON — and it sends a `math_reasoning` schema that matches neither the section's SDK example nor its own messages
- **Evidence**: The block's `messages` array ends `...science fair on Friday."},\n    ]`
  and its `response_format` object ends `"strict": true\n        }\n    },\n  }`.
  The `-d '{...}'` payload of all four curls was extracted from the rendered
  HTML and fed to a JSON parser: payloads 1, 2 and 4 (Quick Start, "Pass in
  'json_schema'", Gemini PROXY) parse cleanly; **payload 3 — this one — fails**
  with `Expecting value` at the trailing comma, char 218. Schema content:
  the block sends `"name": "math_reasoning"` with `steps`/`final_answer`,
  while the SDK example in the same section defines `CalendarEvent`
  (`name`/`date`/`participants`) and the messages are
  "Extract the event information." / "Alice and Bob are going to a science
  fair on Friday."
- **Confidence**: settled (a mechanically re-checkable property of the
  reproduced artifact; explicitly **not** a claim about LiteLLM behavior)
- **Quote**: (no prose quote — the defect is in the code block itself;
  reproduced verbatim in Concrete Artifacts → "Validate JSON Schema — PROXY
  curl, as published (does not parse as JSON)")
- **Our assessment**: A documentation defect in the one example that
  demonstrates the feature's fallback path, and it fails the way a bad
  example fails worst: by being pasted into a runbook. The operator copies it,
  the proxy returns a JSON parse error, and the natural (wrong) conclusion is
  that the *validation fallback* is broken — when in fact the request never
  reached it. The schema/messages mismatch compounds it: a reader who fixes
  only the trailing comma sends a `math_reasoning` schema to a request whose
  example prose extracts a `CalendarEvent`, which will "work" and return
  fields the caller did not ask for. This is a formatting/example-quality
  observation about the page, not a product bug, and it is reported so the
  guide does not reproduce the block. Note this **corrects one of the
  Prospector's triage observations**: that comment said the curl "omits the
  outer `\"type\": \"json_schema\"` / `\"name\"` wrapper keys." It does not —
  the block contains both `"type": "json_schema"` and
  `"name": "math_reasoning"`, and the sibling "Pass in 'json_schema'" curl
  parses cleanly with the same wrapper keys. The only defect in that block is
  the trailing comma. The triage comment's *other* observation (the
  `math_reasoning`-vs-`CalendarEvent` mismatch) is confirmed.

### Claim 12: The page carries no statement about streaming, telemetry, or fallbacks for structured output — recorded as three explicit absences, not inferred in either direction
- **Evidence**: The page's seven sections are Quick Start, Check Model Support
  (2 subsections), Pass in 'json_schema', Validate JSON Schema, Gemini -
  Native JSON Schema Format (Benefits / Usage / Model Behavior). None of them
  mentions `"stream": true`, logging, metrics, callbacks, response headers, or
  fallbacks. Every one of the 17 code blocks is a non-streaming request.
- **Confidence**: settled as an **absence** claim (verified by full-page read;
  the page is short and the omission is checkable)
- **Quote**: (no direct quote; the absence is in what the page does not
  contain — see the section inventory under Source Context)
- **Our assessment**: Three holes, all load-bearing, none inferred.
  **Streaming**: with 17 non-streaming examples and zero mention of
  `"stream"`, the page leaves open whether a JSON-schema response can be
  delivered as SSE at all, and if so how a strict-schema contract survives
  incremental decoding. That is a real gap for Ch05, where streaming is the
  default posture for latency-sensitive agents. **Telemetry**: no statement
  that a validation miss is logged, counted, or exposed — which is the same
  absent-signal hole `docs-litellm-drop-params.md` Claim 9 records for dropped
  parameters, on the adjacent gate. **Fallbacks**: no statement that a
  fallback between two rows of the "Works for:" list preserves the schema
  contract — and Claim 6 shows a *within-vendor* version change is already
  enough to alter the schema dialect, so a fallback from a 2.0+ Gemini route
  to a 1.5 route silently weakens `additionalProperties` with no signal. The
  corpus has already established the pattern from the other side
  (`blog-litellm-save-claude-code-costs.md` Claim 2: budget fallbacks reroute
  without a request-level signal). Per §4a this is recorded as documentation
  absence, not as a contradiction and not as an assertion that fallback breaks
  the contract.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/completion/json_mode
(HTTP 200, verified against rendered HTML; code-block line structure recovered
from the `<br>`-delimited token lines, trailing spaces as published).

### "Works for:" support list (verbatim)

> Works for:
>
> - OpenAI models
> - Azure OpenAI models
> - xAI models (Grok-2 or later)
> - Google AI Studio - Gemini models
> - Vertex AI models (Gemini + Anthropic)
> - Bedrock Models
> - Anthropic API Models
> - Groq Models
> - Ollama Models
> - Databricks Models

### Runtime capability checks (verbatim)

```python
from litellm import get_supported_openai_params

params = get_supported_openai_params(model="anthropic.claude-sonnet-5", custom_llm_provider="bedrock")

assert "response_format" in params
```

```python
from litellm import supports_response_schema

assert supports_response_schema(model="gemini-3.1-pro-preview", custom_llm_provider="bedrock")
```

### Client-side validation — SDK (verbatim)

```python
# !gcloud auth application-default login - run this to add vertex credentials to your env
import litellm, os
from litellm import completion 
from pydantic import BaseModel 


messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
    ]

litellm.enable_json_schema_validation = True
litellm.set_verbose = True # see the raw request made by litellm

class CalendarEvent(BaseModel):
  name: str
  date: str
  participants: list[str]

resp = completion(
    model="gemini/gemini-3.1-pro-preview",
    messages=messages,
    response_format=CalendarEvent,
)

print("Received={}".format(resp))
```

### Client-side validation — PROXY config (verbatim)

```yaml
model_list:
  - model_name: "gemini-3.8-flash"
    litellm_params:
      model: "gemini/gemini-3.8-flash"
      api_key: os.environ/GEMINI_API_KEY

litellm_settings:
  enable_json_schema_validation: True
```

Note the asymmetry: the SDK form assigns a Python `True`, the proxy form uses
YAML `True`, and the section's one-line knob is printed as
`litellm.enable_json_schema_validation=True` (no spaces) — three renderings of
the same flag.

### Validate JSON Schema — PROXY curl, as published (does **not** parse as JSON)

```bash
curl http://0.0.0.0:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -d '{
    "model": "gemini-3.8-flash",
    "messages": [
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
    ],
    "response_format": { 
        "type": "json_schema",
        "json_schema": {
          "name": "math_reasoning",
          "schema": {
            "type": "object",
            "properties": {
              "steps": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "explanation": { "type": "string" },
                    "output": { "type": "string" }
                  },
                  "required": ["explanation", "output"],
                  "additionalProperties": false
                }
              },
              "final_answer": { "type": "string" }
            },
            "required": ["steps", "final_answer"],
            "additionalProperties": false
          },
          "strict": true
        }
    },
  }'
```

Two trailing commas (`},` after the last `messages` element; `},` after the
`response_format` object) — `json.loads` rejects this payload with
`Expecting value: line 1 column 219 (char 218)`. Schema content is
`math_reasoning` (`steps` / `final_answer`), which does not match the
`CalendarEvent` model or the extraction messages used in the SDK tab above it
(Claim 11). The three sibling curls (Quick Start, "Pass in 'json_schema'",
Gemini PROXY) were extracted the same way and parse cleanly.

### "Pass in 'json_schema'" — PROXY curl, OpenAI SDK path (verbatim; parses cleanly)

```python
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(
    api_key="anything", # 👈 PROXY KEY (can be anything, if master_key not set)
    base_url="http://0.0.0.0:4000" # 👈 PROXY BASE URL
)

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

completion = client.beta.chat.completions.parse(
    model="gpt-5.6-terra",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
        {"role": "user", "content": "how can I solve 8x + 7 = -23"}
    ],
    response_format=MathReasoning,
)

math_reasoning = completion.choices[0].message.parsed
```

### The `strict`-carrying dict shape (verbatim, from "Pass in 'json_schema'")

```
response_format: { "type": "json_schema", "json_schema": … , "strict": true }
```

### Pydantic shape — the caller validates the returned string (verbatim)

```python
class EventsList(BaseModel):
    events: list[CalendarEvent]

resp = completion(
    model="gpt-5.6-terra",
    messages=messages,
    response_format=EventsList
)

print("Received={}".format(resp))

events_list = EventsList.model_validate_json(resp.choices[0].message.content)
```

### Gemini 2.0+ — Model Behavior table (verbatim)

| Model | Format Used | `additionalProperties` Support |
|---|---|---|
| Gemini 2.0+ | `responseJsonSchema` (JSON Schema) | ✅ Yes |
| Gemini 1.5 | `responseSchema` (OpenAPI) | ❌ No |

> LiteLLM automatically selects the appropriate format based on the model
> version.

### Benefits (Gemini 2.0+): (verbatim)

> - Standard JSON Schema format (lowercase types like `string`, `object`)
> - Supports `additionalProperties: false` for stricter validation
> - Better compatibility with Pydantic's `model_json_schema()`
> - No `propertyOrdering` required

### Gemini 2.0+ SDK example — note the absent `strict` key and the version-scoped comment (verbatim)

```python
response = completion(
    model="gemini/gemini-3.8-flash",
    messages=[{"role": "user", "content": "Extract: John is 25 years old"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "user_info",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"],
                "additionalProperties": False  # Supported on Gemini 2.0+
            }
        }
    }
)
```

Neither the SDK nor the PROXY Gemini example carries a `strict` key, while
every OpenAI example on the page sets `"strict": true` explicitly (Claim 7).

### Auth-header divergence across the page's four curls (verbatim fragments)

> `-H "Authorization: Bearer $LITELLM_KEY" \`  *(Quick Start)*
>
> `-H "Authorization: Bearer $LITELLM_API_KEY" \`  *(all three other curls)*

### Source permalink for the validation mechanism (as printed on the page)

> [**See Code**](https://github.com/BerriAI/litellm/blob/671d8ac496b6229970c7f2a3bdedd6cb84f0746b/litellm/litellm_core_utils/json_validation_rule.py#L4)

Pinned to commit `671d8ac496b6229970c7f2a3bdedd6cb84f0746b` — a
version-stable citation, unlike the `model_prices_and_context_window.json`
pointer in Claim 1, which tracks `main` and is not pinned.

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every one of
the ten listed paths is addressed):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: `POST /v1/batches`
  input-file rate limiting, per-record token charging, and
  `batch_enqueued_token_limit`; no structured-output parameter surface.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Cited** (Extends, route
  disambiguation). **Claim 1** records the native Invoke passthrough as
  `POST /bedrock/model/<model_name>/invoke` with the
  `anthropic_version: "bedrock-2023-05-31"` wire body, and **Claim 5** records
  that the Claude Code + Bedrock pairing is constrained on that route. This
  page's "Bedrock Models" support row (Claim 2) and its two
  `custom_llm_provider="bedrock"` introspection examples (Claim 1) do **not**
  say which Bedrock route or wire format they mean — and the corpus already
  knows LiteLLM has three (native Invoke, native Converse, standard
  OpenAI-compatible `bedrock/<id>` chat-completions). A single unqualified
  "Bedrock Models" row cannot be uniform across routes that use three
  different wire formats; that is the concrete instance for the guide's
  "assert per backend, test the non-default provider" rule.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  audio-transcription endpoint config (`mode: audio_transcription`
  registration) and mock-testing fallbacks; no `response_format` or schema
  surface.
- `source-notes/blog-litellm-auto-router-v2.md` — **Cited** (Corroborates,
  principle-level). **Claim 3** states the operational rationale as
  "predictable beats clever for debuggability. A fixed, versioned mapping from
  capability class to model is what makes \"why did this response cost 4x
  today\" answerable after the fact." Claim 1 here is the same principle
  applied to *capability* rather than *cost*: a versioned, queryable
  capability→model mapping (two runtime predicates plus a versioned cost/cap
  map) is what makes "which backend would have enforced this schema?" and
  "what did the docs support last month?" answerable. The auto-selection
  behavior in Claim 6 is the same principle's *violation* — an unlogged,
  version-keyed switch with no decision record.
- `source-notes/docs-litellm-completion-batching.md` — **Cited**
  (Corroborates, genre; the sibling `docs/completion/*` page). **Claim 4**
  ("the page documents cancellation and publishes *no* billing semantics for
  the cancelled calls") and **Claim 9** ("nothing on the page describes the
  concurrency mechanism, and nothing describes the rate-limit, retry, or
  fallback interaction") are the same genre as Claims 4 and 12 here: a
  capability is documented thoroughly and its failure/governance semantics are
  absent. That a *second* page in the same nav section repeats the pattern
  makes it a property of the documentation surface, not a one-off omission.
  Not a duplicate: different feature, different endpoint path.
- `source-notes/docs-litellm-a2a-agent-card.md` — **Cited** (methodological
  sibling). Its **Claim 4** is the corpus's other instance of
  "capability advertisement and the routed surface disagree" —
  `capabilities.pushNotifications` is ❌ while every push-notification RPC
  method is ✅ forwarded upstream, with no reconciling statement. Claim 2 here
  is the same shape on the model path: a support list that is the only
  coverage statement and that no other page on the site reconciles against
  the runtime predicates or the validation flag.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session `max_iterations` / `max_budget_per_session` caps keyed on
  `x-litellm-trace-id`; no structured-output or parameter-support surface.
- `source-notes/docs-litellm-bedrock-converse.md` — **Cited** (Extends, same
  route-disambiguation point as the Invoke note). **Claim 1** records the
  native Converse passthrough as `POST /bedrock/model/<model_name>/converse`
  and its table shows exactly four model routes under the `.../bedrock` base.
  Together with the Invoke note's Claim 1, this establishes the three-route
  Bedrock topology that this page's unqualified "Bedrock Models" row does not
  distinguish.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: Langfuse's docs
  MCP server transport/auth config; unrelated to gateway parameter surfaces.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Dismissed**: the
  advisor tool's within-request model composition and `usage.iterations[]`
  advisor-token accounting. Its Claim 4 (a non-streaming hop inside a
  streaming request) is adjacent to Claim 12's streaming hole, but the advisor
  loop is a different mechanism from `response_format` and the page here
  documents nothing about either.

**Wider corpus** (found by searching `source-notes/` and `guide/`, beyond the
candidate list):

- **Corroborates**:
  - `source-notes/docs-litellm-drop-params.md` — the grounding reference for
    three things here. **Claim 2** ("the support matrix is keyed on provider
    *and* model (not provider)… `litellm.get_supported_openai_params("<model>")`")
    is the same executable-introspection answer that Claim 1 gives for
    structured output, and it is why the ten-row "Works for:" list cannot be
    read as a per-model guarantee. **Claim 1** (default is a hard raise;
    `drop_params` flips it to a silent omission) establishes the gate's
    *polarity*, which is the polarity a reader will bring to this page's
    unqualified support list — and which the page neither confirms nor
    contradicts for `json_schema`. **Claim 3** (four placements, no stated
    precedence) is the template for reading this page's
    `enable_json_schema_validation` flag: two documented placements, one
    process-global and one proxy-global, no precedence statement, both
    global-scoped. **Claim 9** (no documented signal for a drop) is the
    absent-telemetry hole Claim 12 here reports from the other gate.
  - `source-notes/docs-litellm-anthropic-unified-structured-output.md` (#1391) —
    the sibling structured-output note, cross-linked rather than merged. Its
    **Claim 4** ("The structured payload arrives as a stringified JSON blob
    inside `content[0].text` with `stop_reason: \"end_turn\"` — no distinct
    structured-output stop reason, content type, or schema-violation signal
    is documented") is the `/v1/messages` instance of what Claim 8 documents
    here on `/v1/chat/completions` through the *happy path*:
    `model_validate_json(resp.choices[0].message.content)`. Its **Claim 3**
    (`additionalProperties: false` documented as "enforce strict schema
    adherence" with no stated enforcement location) is exactly the gap Claim 7
    identifies in this page's Gemini benefits list. Its **Claim 7** (no
    streaming and no fallback statement for `output_format`) is the same
    documented-absence genre as Claim 12 here. Its **Claim 1** (four-row
    Anthropic-family-only `output_format` table) does *not* conflict with this
    page's ten-row list — different endpoint, different parameter name; see
    Source Context contradiction-scan item 1.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — **Cited**
    (Extends). Its Concrete Artifacts → "Top-level parameter mapping, request
    direction" row records `output_format` / `output_config.format` → `text`,
    wrapped as `{"format": {"type": "json_schema", "name": "structured_output",
    "schema": ..., "strict": ...}}` with `strict` "copied from the request's
    `strict` flag and defaults to `false`". That row is the *translated*
    OpenAI/Azure path; this page is the *native* `response_format` path with
    `"strict": true` set explicitly in every OpenAI example. Read together
    they give the full structured-output surface: the same idea in three
    dialects (`response_format` dict, Anthropic `output_format`, Responses
    `text.format`) with `strict` defaulted `false` on one and set `true` on
    another. Also its **Claim 1** (silent drops of `stop_sequences` / `top_k`
    on the translation adapter) is the concrete precedent for the
    dialect-drift shape in Claim 6.
  - `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` —
    **Cited** (Corroborates, the class). **Claim 2** establishes that
    parameter *semantics* differ across "OpenAI-compatible" backends and that
    this is "a compatibility surface, not an implementation detail"; Claim 6
    here is the vendor's own documented instance of that, on a different
    parameter and inside a single vendor: a schema keyword
    (`additionalProperties`) that is honored on one model generation and ❌ on
    the sibling, auto-selected with no signal. Its **Claim 6** (assert the
    exact wire payload per backend, test the non-default provider) is the
    regression guard this page's surface needs and does not have.
  - `source-notes/docs-datadog-llm-observability.md` — **Cited** (Extends).
    **Claim 3**: "A span is the unit of work; a trace is one or more nested
    spans with a root span marking start/end." Error detail lives in span
    *attributes* that instrumentation sets (that note's Concrete Artifacts,
    span attributes: "Error type/message/traceback"). Claims 3, 4, 8 and 12
    here all describe a condition — schema non-conformance, a validation miss
    — that produces no error, no status change, and no span attribute, so it
    is invisible to that layer. This page supplies the concrete probe for
    Ch02's "correctness signals need explicit instrumentation" argument.
  - `source-notes/blog-litellm-claude-fable-5-day-0.md` — **Cited**
    (Corroborates, with a discrepancy now resolved). **Claim 12**: "Vision,
    PDF input, computer use, tool calling, prompt caching, adaptive thinking,
    and structured output, all available across Anthropic, Azure, Vertex AI,
    and Bedrock with unified spend tracking, logging, and fallbacks." This
    page's "Works for:" list **includes all four of those names** (plus six
    more), so the Vertex-AI discrepancy #1391 flagged as an open cross-check
    is resolved in Fable-5's favor. Fable-5's list is a subset, not a
    competing enumeration — no exclusivity claim, hence no contradiction.
    **Claim 11** (on Bedrock the model must be invoked through an
    inference-profile prefix; the bare ID returns a validation error) is the
    corpus precedent for treating a provider prefix as a routing contract,
    which is what Claim 5's `gemini/`-vs-Vertex-ADC mismatch is an instance of.
- **Contradicts**: **None — no contradiction issue filed.** Four candidate
  tensions were checked and each resolved as a different surface or a
  different layer (see Source Context → contradiction scan, items 1-4).
  Verified against all ten open `contradiction`-labeled issues (#1150, #1307,
  #1322, #1338, #1352, #1408, #1461, #1462, #1486) and `CONTRADICTIONS.md`
  (no `C-NNN` entries) before deciding.
- **Extends**:
  - `source-notes/docs-litellm-drop-params.md` — adds the *schema*-side of
    the same governance story: the knob family that decides whether a param is
    forwarded, stripped, or force-passed (its Claims 1-3, 7-9) is
    complemented by the knob that decides whether the *response* is checked
    (Claim 3 here). Together they define the four failure branches a
    structured-output request can take on one gateway: raise, silent drop,
    native enforcement, or post-hoc caller-side check — with the last two
    selected by config flags whose placements have no documented precedence.
  - `source-notes/docs-litellm-anthropic-unified-structured-output.md` — this
    page is the second data point for the guide's per-feature-coverage rule
    and, unlike #1391, it also documents the *remedy* the Anthropic page has
    no counterpart for (client-side validation). #1391's Claim 1 is a
    capability boundary on `/v1/messages`; Claim 2 here is a capability
    boundary on `/v1/chat/completions`. They must cross-link, not merge.
  - `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` — this
    page supplies the *documented, not incidental* version-keyed dialect
    switch that note's failure mode argues must be tested per backend family.
  - `source-notes/blog-litellm-claude-fable-5-day-0.md` — its Claim 12
    "structured output … across Anthropic, Azure, Vertex AI, and Bedrock"
    gains a documented support list and two runtime checks (Claims 1-2), and
    a documented gap it does not mention (post-hoc validation, Claims 3-4).
- **Novel**: First corpus coverage of **structured output on LiteLLM's
  OpenAI-compatible `/v1/chat/completions` surface**. Specifically new: the
  two-runtime-predicate capability-discovery contract and the unpinned
  `model_prices_and_context_window.json` as a third source of truth (Claim 1);
  the flat 10-provider "Works for:" list with no ❌ cells and no
  native-vs-post-hoc column (Claim 2); `enable_json_schema_validation` as a
  **post-hoc caller-side** enforcement switch with process-global /
  proxy-global scope, no documented failure contract, and no documented
  telemetry (Claims 3, 4, 12); the Gemini 2.0+ / 1.5 `responseJsonSchema` vs
  `responseSchema` dialect split with automatic version-keyed selection
  (Claims 6, 7); the three request shapes (`json_object`, raw
  `json_schema` dict, Pydantic model) and the Pydantic shape's documented
  caller-side `model_validate_json` on a returned string (Claim 8); the
  `beta.chat.completions.parse` / `.parsed` proxy path as a second,
  unreconciled validation layer (Claim 9); and the page's own runnable-
  example defect and auth-header divergence (Claims 10, 11). Provenance of
  the novelty claim, re-verified this session: a corpus grep for
  `response_format` / `json_schema` across `source-notes/` returns only the
  `additional_drop_params=["response_format"]` example in
  `docs-litellm-drop-params.md` and one `output_format` → `text` mapping row
  in `docs-litellm-messages-to-responses-mapping.md`; `guide/` contains no
  occurrence of `response_format`, `json_schema`, or `enable_json_schema_validation`.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Provider parity in the shared
  forwarding path" (guide/05-llm-ops-reliability.md ~L343-384)**: The
  section currently argues parity from a *request-side* failure (present-but-null
  vs omitted, `encoding_format`). Add the **response-side** half: the same
  forwarding path also carries a *schema-dialect* parity hazard that the
  gateway resolves silently and by model version. Concretely, a caller
  sending `additionalProperties: false` gets a schema that survives
  translation on Gemini 2.0+ (`responseJsonSchema`) and loses it on 1.5
  (`responseSchema`), because "LiteLLM automatically selects the appropriate
  format based on the model version" [Claim 6, settled] with no request-level
  field, log line, or header to assert the choice. The rule to add: **a
  structured-output guarantee is a property of (provider, model, version) —
  never of the endpoint** — and the documented check is a runtime call, not a
  support list. The ten-row "Works for:" list [Claim 2, settled] cannot
  discharge that obligation, because it is keyed on *provider*, carries no ❌
  cells, and the page's own validation section says native support is not
  universal.
- **Chapter 05, "Parameter migration hazards" (~L327-341)**: The chapter's
  rule is "audit existing request parameters against the model's supported set
  before routing production traffic." Add the response-side twin: the audit
  is per **feature**, and structured output has a *second* support axis the
  audit must cover — whether enforcement is native or post-hoc. The two
  documented predicates are the executable form of the audit
  [Claim 1, settled]: `get_supported_openai_params(model=…, custom_llm_provider=…)`
  for `response_format`, `supports_response_schema(...)` for the strict
  `json_schema` form. Note the parameter-naming trap when wiring the audit:
  the checks take a bare model ID plus a separate provider argument, while
  `config.yaml` takes a prefixed model string [Claim 1, settled].
- **Chapter 05 / any runbook that enables `enable_json_schema_validation`**:
  add the posture statement. The flag is a **detection** control, not a
  shaping one — validation runs after generation, in the caller's own process,
  against `jsonvalidator` [Claim 3, settled] — and the page documents **no**
  error type, HTTP status, or retry behavior for a validation miss
  [Claim 4, settled-as-documented-absence]. So: (a) do not present it as an
  output-safety guarantee; (b) treat the failure mode as an open verification
  item to be measured on your own stack before you alert on it; (c) its scope
  is global (SDK module attribute or `litellm_settings`), so it cannot be
  turned on for the three models that need it without applying it to every
  model the proxy serves — the same "audit the blast radius of a global knob"
  rule `docs-litellm-drop-params.md` Claim 3 supports for `drop_params`.
- **Chapter 02 (Observability)**: Add a first-class **schema-adherence
  metric**. A structured response that violates its schema is a 200 with an
  unvalidated string — the page's own Pydantic happy path has the caller do
  `EventsList.model_validate_json(resp.choices[0].message.content)`
  [Claim 8, settled] — with no error, no status change, and no span attribute
  [Claims 4, 12; cf. `docs-datadog-llm-observability.md` Claim 3]. The
  `enable_json_schema_validation` path does not fix this either: the page
  documents no log, metric, or header for a validation miss [Claims 4, 12].
  Rule: if you route structured output, instrument parse-success and
  schema-adherence as an explicit metric with its own alert, because the
  gateway's error metrics are structurally blind to this failure. Pair it
  with the from-the-other-side rule already in the chapter: `set_verbose` /
  outbound-payload diffing is the only documented way to confirm what schema
  was actually sent [Claim 5, settled].
- **Chapter 03 (Runbooks and agents)**: Add the three-shapes table, because an
  agent author picking a shape is picking an enforcement level: `json_object`
  (no schema — the Quick Start's only guard is a system prompt), raw
  `json_schema` dict with `"strict": true` (provider-facing), and
  `response_format=<Pydantic Model>` (caller-side, you validate the string)
  [Claim 8, settled]. For agent loops the practical rule is the third shape
  *on purpose* — client-side validation is visible in your own code, which is
  strictly better than relying on a flag whose failure behavior is undocumented
  — with the cost stated honestly: the tokens are already billed when the
  validator runs. Do **not** reproduce the page's "Validate JSON Schema" PROXY
  curl in any runbook: as published it is invalid JSON (trailing comma) and its
  schema does not match its own example [Claim 11, settled].
- **Chapter 05, fallback semantics** (pairs with the chapter's existing work
  on silent fallback breaking attribution): the page documents **no** fallback
  behavior for structured output [Claim 12, settled-as-absence]. The concrete
  risk the Smith should state: a fallback between two rows of the "Works for:"
  list can change the *schema dialect*, not just the price — a 2.0+ Gemini
  route falling back to a 1.5 route silently drops `additionalProperties`
  [Claim 6] with no signal. This is the same hazard
  `blog-litellm-save-claude-code-costs.md` Claim 2 records for budget-driven
  reroutes, applied to an output *correctness* property rather than a cost
  one. Assert, do not assume: if a structured-output workload has a fallback
  chain, the chain must be constrained to a single model version per provider.
- **Chapter 06 (Security and Trust)**: the `enable_json_schema_validation`
  flag is an output-validation control of **documented shape with undocumented
  failure semantics** [Claims 3, 4]. Record it as an open verification item,
  not a guarantee — the same treatment
  `docs-litellm-anthropic-unified-structured-output.md` Guide Impact gives the
  `/v1/messages` `additionalProperties: false` control. Also add the
  auth caveat from Claim 10 [settled]: the page's own OpenAI-SDK example
  invites `api_key="anything"` when `master_key` is unset, so a proxy deployed
  from these examples without `master_key` has an open endpoint — the
  structured-output feature is not the risk there, but the runbook that
  configures it is.

## Extraction Notes

- Source read in full via WebFetch (markdown) **and** re-fetched with `curl`
  to recover exact code-block line structure and to parse the curl request
  bodies, since the markdown pass flattened newlines inside fenced blocks.
  Canonical URL `https://docs.litellm.ai/docs/completion/json_mode`, HTTP 200,
  size 103,454 bytes of rendered HTML, no paywall, no auth. All 17 code
  blocks, all seven sections, the "Works for:" list, the "Benefits" list, and
  the two-row "Model Behavior" table were extracted; nothing was skipped.
- **Quote fidelity re-verified programmatically this session.** 50 candidate
  quote strings were checked against the de-tagged page text; all 50 are
  present as contiguous, character-for-character fragments (the only
  normalization applied is that the page renders backticked tokens as `<code>`
  spans, so the quotes carry the backticks a reader sees). No quote is spliced
  across non-adjacent sentences. The two filename references
  (`model_prices_and_context_window.json`) and the `See Code` permalink are
  reproduced as the page renders them — link text plus the surrounding prose,
  with the target URL given in Concrete Artifacts. Claims whose evidence is an
  *absence* (4, 9, 12) and Claims 10-11 whose evidence is a property of code
  blocks rather than a sentence carry explicit `Quote:` markers and reproduce
  the evidence verbatim in Concrete Artifacts instead, per MINER §2a.
- The four `-d '{...}'` payloads were extracted from the rendered HTML,
  de-tagged, and run through `json.loads`: payloads 1 (Quick Start), 2 ("Pass
  in 'json_schema'" PROXY curl) and 4 (Gemini PROXY curl) parse cleanly;
  **payload 3 ("Validate JSON Schema" PROXY curl) fails** at the trailing
  comma. That mechanical result is the sole basis for Claim 11, which is
  scoped to the page's published block and makes no claim about LiteLLM
  behavior. Reproducible from the note's own verbatim artifact.
- **The Prospector's triage is corrected on one point.** Triage comment
  (Prospector, 2026-09-28) stated that the "Validate JSON Schema" proxy curl
  "has a trailing comma before the closing brace and omits the outer
  `\"type\": \"json_schema\"`/`\"name\"` wrapper keys." The trailing comma is
  confirmed (twice: after the last `messages` element and after the
  `response_format` object). The missing-wrapper-keys half is **not**
  correct: the block contains both `"type": "json_schema"` and
  `"name": "math_reasoning"`, and it is the *sibling* curl in the previous
  section that carries the same wrapper keys and parses cleanly. The triage's
  separate observation — that the curl's `math_reasoning` schema does not
  match the surrounding `CalendarEvent` example — is confirmed and is part of
  Claim 11.
- **Prospector's other requested extractions, all delivered**: the two
  runtime predicates plus the externally-hosted
  `model_prices_and_context_window.json` (Claim 1); the
  `enable_json_schema_validation` degradation path and the **explicit absence**
  of a failure contract for a validation miss (Claims 3, 4); the Gemini
  version-split as a "provider parity by model version" instance
  (Claims 6, 7); and the provider-list breadth cross-checked against
  `docs-litellm-anthropic-unified-structured-output.md` (Cross-References —
  the two pages do **not** disagree; see contradiction-scan item 1, and
  Fable-5 Claim 12's Vertex-AI question is now answered in its favor).
  Prospector's "documented absences" instruction (no error/exception names,
  no retry guidance, no streaming statement) is recorded as Claim 4 and
  Claim 12 rather than inferred.
- **Contradiction handling (MINER §4a/§4b)**: no contradiction issue filed.
  Four candidate tensions checked and each resolved as a different surface or
  layer (Source Context, items 1-4). Verified against all ten open
  `contradiction`-labeled issues and `CONTRADICTIONS.md` (no `C-NNN` entries)
  before deciding. Per §4a, no verdict is recorded in this note.
- **Cross-reference verification (MINER §4b)**: every cited claim was re-read
  in the cited note before being written here —
  `docs-litellm-drop-params.md` Claims 1, 2, 3, 9;
  `docs-litellm-anthropic-unified-structured-output.md` Claims 1, 3, 4, 7;
  `docs-litellm-messages-to-responses-mapping.md` Claim 1 plus its Concrete
  Artifacts mapping row; `failure-litellm-vllm-embeddings-encoding-format.md`
  Claims 2 and 6; `docs-datadog-llm-observability.md` Claim 3;
  `blog-litellm-auto-router-v2.md` Claim 3;
  `blog-litellm-claude-fable-5-day-0.md` Claims 11 and 12;
  `docs-litellm-bedrock-invoke.md` Claims 1 and 5;
  `docs-litellm-bedrock-converse.md` Claim 1;
  `docs-litellm-completion-batching.md` Claims 4 and 9;
  `docs-litellm-a2a-agent-card.md` Claim 4. No claim numbers invented; where
  material lives in a non-numbered section (the mapping table, the config
  snippets, the support lists) it is cited by section name.
- No sub-pages followed: the only outbound links are the nav siblings
  `completion/batching` (mined as `docs-litellm-completion-batching.md`, #1467)
  and `reasoning_content`, plus the pinned permalink into
  `litellm/litellm_core_utils/json_validation_rule.py#L4` and the unpinned
  `model_prices_and_context_window.json` blob. The two GitHub URLs were **not**
  fetched — no assertion in this note is derived from LiteLLM source code or
  from the cost-map file; Claims 3 and 6 are scoped to what the page says.
  The nine non-candidate cross-referenced notes were read in full or to the
  cited claim in this checkout.
- `confidence_overall` set to `emerging`: the parameter shapes, the support
  list, the two introspection helpers, the validation knob and its two
  placements, the Gemini dialect table, and all 17 code blocks are settled
  first-party documentation — but the page is undated living docs, the support
  list is a vendor assertion with no adherence evidence, the enforcement and
  failure semantics are documented *absences* (Claims 4, 12), and the
  guide-relevant readings (silent dialect downgrade, post-hoc-not-provider
  enforcement, the unmonitored correctness surface) are the Miner's synthesis
  from that surface. Matches the `emerging` rating on the sibling LiteLLM docs
  notes (#1380, #1391, #1467, #1480).
- `date_published` unknown (undated living docs page); `date_extracted` and
  `last_checked` both 2026-09-29 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain.
