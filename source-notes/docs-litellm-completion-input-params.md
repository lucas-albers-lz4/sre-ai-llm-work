---
source_url: https://docs.litellm.ai/docs/completion/input
source_type: docs
title: "Input Params | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-29)
date_extracted: 2026-09-29
last_checked: 2026-09-29
status: current
confidence_overall: emerging
issue: "#1495"
---

# Input Params — `litellm.completion()` (LiteLLM Docs)

> The reference page for the `litellm.completion()` request body, and the only
> corpus source that states the *scope* of the gateway's parameter-support gate
> rather than just its polarity: the gate covers only params LiteLLM recognizes
> as OpenAI params, and **three names are hard-coded to bypass it entirely**
> (`stream_options`, `extra_headers`, `max_retries`). It is also the corpus's
> only record of a **documented 600-second default client timeout**, of a
> **second fallback mechanism keyed on a context-window error**
> (`context_window_fallback_dict`), and of a **silent request mutation with no
> knob list and no signal** (a `stop` list longer than 4 is truncated to the
> first 4, exit via `litellm.disable_stop_sequence_limit = True`). It also
> carries a documented liveness failure mode worth a runbook: JSON mode without
> an explicit "return JSON" instruction produces an unbounded whitespace stream
> that the vendor itself describes as a "seemingly stuck" request.

## Source Context

- **Type**: docs (single-page LiteLLM SDK reference at
  `/docs/completion/input` — verified HTTP 200 this session, matching
  `source_url`. The `/docs/` form and the bare `/completion/input` form are the
  same document; `curl -L` resolves the former to the latter.) Site breadcrumb
  per the page's own nav: "LiteLLM Python SDK → SDK Functions →
  `completion()`". Siblings in the same section: `/completion/output`,
  `/completion/batching`, `/completion/reliable_completions`,
  `/completion/drop_params`.
- **Author credibility**: LiteLLM (BerriAI) first-party product
  documentation. Authoritative for the *documented* request surface: it ships the
  `completion()` signature, a 25-provider × 20-param support matrix, the
  introspection helper, and a named litellm-specific parameter section. This is
  the vendor describing its own product — no independent validation, no metrics,
  no test output, no changelog, and the page is undated.
- **Scope**: The `completion()` **input** surface only: the translated-OpenAI
  params, the supported-params matrix, `stream_options` / `extra_headers` /
  `max_retries` gate exemptions, the standard OpenAI param glossary, deprecated
  params, and the litellm-specific params (endpoint selection, retry, two
  fallbacks, metadata, custom cost, custom prompt template). Does NOT cover: the
  response shape (that is `/completion/output`), the OpenAI-compatible
  **proxy** surface (`/v1/chat/completions` config, guardrails, rate limits,
  batch accounting), the Router, or the parameter-drop gate's knob surface (that
  is `/completion/drop_params`).
- **Redundancy / what this page owns**: the parameter-gate polarity and knob
  surface are already owned by `docs-litellm-drop-params.md` (#1480) and are
  **not** re-derived here. What this page adds is everything the gate page
  treats as out of scope: the gate's *boundary* (Claim 3), its *exemptions*
  (Claim 2), the retry/fallback/timeout defaults (Claims 4, 5, 13), the
  request-mutating `stop` truncation (Claim 6), and the JSON-mode liveness
  failure (Claim 7). This page also restates the drop-gate note and the
  introspection helper; those restatements are recorded as corroboration, not as
  new claims.

## Extracted Claims

### Claim 1: The supported-params gate has a hard-coded exemption list that bypasses the matrix entirely — `stream_options`, `extra_headers` and `max_retries` are not checked against the support list and are accepted for every provider
- **Evidence**: A single sentence immediately under the provider × model
  support table, in the same paragraph as the table's own caption. It is the
  only statement of exemptions anywhere on the page.
- **Confidence**: settled (explicit vendor statement, unqualified)
- **Quote**: "stream_options, extra_headers and max_retries are not checked against this list and are accepted for every provider, and stream_options={"include_usage": True} returns usage on the final chunk for every provider"
- **Our assessment**: We buy the statement as a *documented* contract and do not
  buy "for every provider" as a *verified* one. The operational value is that it
  bounds the gate: an operator cannot use "is this param in the support matrix"
  as the rule for "will the gateway reject this", because three names are exempt
  by construction. That is a three-name hole in the `drop_params` /
  `allowed_openai_params` model documented at
  `docs-litellm-drop-params.md` — which documents the *operator-facing* bypass
  (`allowed_openai_params`) but never mentions these three hard-coded
  exemptions, so an operator who read only the gate page will over-predict
  rejections. The second half of the sentence is a *uniformity guarantee*
  ("for every provider") stated with no matrix, no wire capture and no test —
  the same class of assertion that `docs-litellm-streaming-token-usage.md`
  Claim 3 downgraded to `anecdotal`. Two independent LiteLLM pages now assert
  provider-uniform streaming usage (see Cross-References); that is more
  corroboration, not more evidence, and the claim stays a vendor assertion.

### Claim 2: The page names `max_retries` in the exemption sentence but documents the retry parameter as `num_retries` — the two names are never reconciled, and neither appears in the `completion()` signature
- **Evidence**: String counts over the fetched page: `max_retries` occurs
  **once** (in the exemption sentence) and `num_retries` occurs **once** (in the
  litellm-specific params list). Neither occurs in the signature block, which
  routes them through `**kwargs`. The linked reliability page
  (`/docs/completion/reliable_completions`) uses `num_retries` throughout and
  never mentions `max_retries`.
- **Confidence**: settled as a *documentation* observation (both counts are
  directly re-checkable against the fetched page); the runtime behavior of a
  `max_retries` kwarg is **not** asserted — see Our assessment
- **Quote**: "stream_options, extra_headers and max_retries are not checked against this list and are accepted for every provider" / "num_retries: int (optional) - The number of times to retry the API call if an APIError, TimeoutError or ServiceUnavailableError occurs"
- **Our assessment**: This is the page's sharpest operational defect, and it is
  a two-step trap rather than a cosmetic naming slip. An operator auditing which
  params are gate-exempt reads `max_retries`, concludes retries are exempt
  everywhere, and writes `completion(..., max_retries=3)`. Per Claim 3, a kwarg
  LiteLLM does not recognize as an OpenAI param is *assumed provider-specific
  and passed into the request body* — so the mistyped retry knob most likely
  does not error, does not retry, and ships an unknown field to the provider.
  The page nowhere tells the reader that `max_retries` is not a parameter. We
  deliberately do **not** assert that the gateway silently accepts it; the
  honest statement is that the documentation is internally inconsistent on a
  name that changes failure behavior, and that Claim 3's pass-through rule makes
  the consequence of guessing wrong quiet rather than loud. The guide-relevant
  form of this is a rule about *verifying the knob name against the
  litellm-specific list before relying on an exemption sentence.*

### Claim 3: The gate's scope is bounded by LiteLLM's own OpenAI-param recognition — any parameter it does not classify as an OpenAI param is assumed provider-specific and passed into the request body as a kwarg
- **Evidence**: The closing two sentences of the admonition box that also states
  the default-raise rule, in bold and unmissed form.
- **Confidence**: settled (explicit vendor statement of both the limit and the
  fallback behavior)
- **Quote**: "This ONLY DROPS UNSUPPORTED OPENAI PARAMS." / "LiteLLM assumes any non-openai param is provider specific and passes it in as a kwarg in the request body"
- **Our assessment**: This is the central mechanism on the page and it is
  **absent from the corpus**. `docs-litellm-drop-params.md` Claim 1 documents the
  gate's *polarity* (raise by default, `drop_params` inverts to silent) and its
  Claim 2 documents the matrix keying, but nothing in that note — and nothing
  in `guide/` — says the gate has an *outer boundary*. The boundary has two
  consequences the guide does not currently state. (1) **A misspelled or
  renamed OpenAI param is not gated at all.** If a client sends
  `max_token` instead of `max_tokens`, LiteLLM does not recognize it as an
  OpenAI param, so `drop_params` cannot drop it, the default-raise rule cannot
  fire on it, and the typo reaches the provider as a kwarg — the exact
  "silently ignored" outcome that `guide/05-llm-ops-reliability.md` ~L340 warns
  about, arrived at by a route the gate cannot catch. (2) The pass-through is
  unconditional, so the gate provides **no** protection against a provider
  rejecting an unknown kwarg; the failure moves upstream and changes error
  class. Combined with Claim 2, this is a coherent story: the gate is a
  namespace-scoped validator, not a schema validator.

### Claim 4: `context_window_fallback_dict` is a second fallback mechanism with a *different* trigger from `fallbacks` — it fires only on a context-window error, where `fallbacks` fires on any call failure
- **Evidence**: One-line type-and-trigger definition in the litellm-specific
  params section, immediately above the `fallbacks` line. The linked reliability
  page supplies the worked mapping (a 4k model falling back to its 16k variant)
  and the framing that the dict maps "those models which have larger
  equivalents".
- **Confidence**: settled (explicit trigger clause; the mechanism's trigger is
  stated, its *mechanics* are not)
- **Quote**: "context_window_fallback_dict: dict (optional) - A mapping of model to use if call fails due to context window error" / "fallbacks: list (optional) - A list of model names + params to be used, in case the initial call fails"
- **Our assessment**: Novel to the corpus (zero hits for
  `context_window_fallback_dict` or `longer_context_model_fallback_dict` across
  `source-notes/` and `guide/`, re-verified this session), and it is a
  **third** silent-model-substitution authority in the corpus, alongside the
  response-`model` fallback on flagged cybersecurity/biology requests
  (`guide/05-llm-ops-reliability.md` ~L973-985) and the prompt-store
  `prompt_template_model` override documented at `docs-litellm-generic-prompt-management-api.md`
  Claim 3. It matters for a specific reason the general fallback does not: the
  trigger is **input-dependent**, so whether a request is substituted depends on
  the *size of that request's context*. A single regression test or eval suite
  whose prompts grew past a context boundary can start being answered by a
  different model with no error, no header (per Claim 13 the `fallbacks` path
  does emit a header; the page documents none for this path), and no change to
  the request. The page states the trigger and not the mechanics, so whether
  this path logs, retries, or emits any signal is undetermined here — flagged as
  an open sub-question rather than filled in by assumption.

### Claim 5: The documented default client timeout is **600 seconds** — and the page's own signature declares `timeout: Optional[Union[float, int]] = None`, so the prose default and the code default on the same page disagree
- **Evidence**: The `timeout` entry in Optional Fields, and the `timeout` line in
  the verbatim signature block reproduced in Concrete Artifacts. No derivation,
  measurement, or rationale accompanies either.
- **Confidence**: settled as a *documentation* observation (both statements are
  on the page, verbatim); the *effective* default is **emerging** — the page
  does not say which of the two a reader is meant to apply
- **Quote**: "timeout: int (optional) - Timeout in seconds for completion requests (Defaults to 600 seconds)"
- **Our assessment**: The first corpus record of any default timeout anywhere
  (re-verified: zero hits for "600 second" or "Defaults to 600" in
  `source-notes/` and `guide/`). Two things make it consequential rather than
  trivia. (1) **It is a liveness budget, not a tuning knob.** A client that
  inherits the default can hold a connection and an in-process worker for ten
  minutes, which is the entire observed duration of the JSON-mode whitespace
  failure in Claim 7 — the two claims compose into a single incident shape
  ("stuck" request that resolves only at the 600s ceiling). (2) **It lands in a
  corpus that already has two other unsourced LiteLLM timeout numbers**:
  `docs-litellm-completion-http-handler-config.md` Claim 7 records three
  mutually inconsistent `aiohttp.ClientTimeout` profiles on the transport page
  (180s in the main example, 60s dev, 300s production) with no stated
  derivation. 600s is a *fourth* number, on a *fourth* surface, again with no
  derivation — and it is 2× the transport page's largest. The honest synthesis
  is that **no LiteLLM timeout number in the corpus is sourced**, and none
  should be cited as evidence-backed in the guide. The signature/prose
  disagreement is separately worth recording: a reader copying the signature
  concludes the default is `None` and infers "no default", which is a different
  operational belief from "600s unless I override it".

### Claim 6: A `stop` list longer than 4 sequences is silently truncated to the first 4, with the single exit `litellm.disable_stop_sequence_limit = True` — a request-mutating behavior with no warning emitted
- **Evidence**: A `Note:` callout directly under the `stop` field definition,
  naming the OpenAI limit, the truncation, and the one module-global override.
- **Confidence**: settled (explicit vendor statement of the mutation, the
  direction of truncation, and the opt-out)
- **Quote**: "Note: OpenAI supports a maximum of 4 stop sequences. If you provide more than 4, LiteLLM will automatically truncate the list to the first 4 elements. To disable this automatic truncation, set litellm.disable_stop_sequence_limit = True."
- **Our assessment**: Novel to the corpus (zero hits for
  `disable_stop_sequence_limit`, re-verified this session) and structurally the
  **same failure shape** as the silent branch in
  `docs-litellm-drop-params.md` Claim 1 — with one difference that makes it
  worse. `drop_params` silently *omits* a whole parameter, so the request still
  means what the caller meant minus one knob. Silent `stop` truncation is
  **partial and silent**: the caller receives a valid 200, N−4 of its stop
  sequences never take effect, and generation can run past every boundary past
  the 4th. For the guide this is the sharpest form of the ~L340 hazard
  ("Parameters valid on earlier models may be silently ignored") because the
  parameter is *valid and supported* on the target — it is the gateway, not the
  model, that discards it. Note the knob is module-global
  (`litellm.disable_stop_sequence_limit`), i.e. process-wide, so the
  remediation has a fleet-wide blast radius and a per-deployment / per-request
  alternative does not exist on this page. We do not know whether a log line is
  emitted; the page documents none either way.

### Claim 7: JSON mode without an explicit instruction is a documented liveness failure — the model emits an unbounded whitespace stream until the token limit, which the vendor describes as a long-running, "seemingly stuck" request; and `finish_reason="length"` can leave the content cut off mid-JSON
- **Evidence**: An `Important:` callout under the `response_format` field
  definition, containing both failure modes. The page also softens the headline
  guarantee ("guarantees the message the model generates is valid JSON") in the
  same callout, by attaching the `finish_reason="length"` caveat to it.
- **Confidence**: settled (explicit vendor statement of the symptom, the
  precondition that triggers it, and the truncation caveat)
- **Quote**: "Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if finish_reason="length", which indicates the generation exceeded max_tokens or the conversation exceeded the max context length."
- **Our assessment**: This is the most runbook-shaped item on the page and the
  only one with a *named symptom* rather than a config surface. Two separable
  symptoms. (1) **A missing prompt instruction, not a misconfiguration, is
  sufficient to cause it** — the caller did everything the field definition
  asks for (`response_format={"type": "json_object"}`) and still gets a
  request that looks hung. The observable is a request whose token consumption
  climbs to the cap while the content is whitespace, which at the documented
  600s default (Claim 5) is a ten-minute occupancy. (2) **"Guarantees valid
  JSON" is conditional on not hitting the length cap** — the same callout admits
  partial truncation at `finish_reason="length"`, so the realistic downstream
  symptom of a long structured answer is a JSON *parse error* in the caller's
  code, not a clean truncation notice. The guide-relevant rule is that
  `finish_reason` must be checked before trusting a structured response, and
  that a `json_object`-mode call needs its instruction present in the prompt —
  both checkable in a runbook. The whitespace-stream failure is a documented
  vendor statement, not a failure we observed.

### Claim 8: The published support matrix is a per-model snapshot the page itself disclaims — the executable `get_supported_openai_params(model, custom_llm_provider)` is given as the source of truth, with Bedrock Llama as the worked reason provider-level tables are wrong
- **Evidence**: The table's caption paragraph, immediately before the table, plus
  the two-line code example above it, whose printed output is a 4-element list.
- **Confidence**: settled (explicit vendor statement plus a runnable
  introspection call and a worked counterexample)
- **Quote**: "This table is the output of litellm.get_supported_openai_params() for the model shown in each row. Support is model dependent within a provider (for example Bedrock Llama models do not list tools or tool_choice), so call the function for the exact model you use"
- **Our assessment**: Corroborates and sharpens `docs-litellm-drop-params.md`
  Claim 2, which already established the per-provider-**and**-model keying and
  the single-argument helper form. The delta here is two things. (1) The page
  **disclaims its own table** — "so call the function for the exact model you
  use" is the vendor telling operators the published matrix is a convenience,
  not a contract, which is stronger than the drop-params page's framing. (2)
  The helper is documented in its **two-argument** form
  (`model=..., custom_llm_provider=...`), and its printed output in the example
  is a **4-element list for a Bedrock Anthropic model** (`["max_tokens",
  "tools", "tool_choice", "stream"]`) — so the same function that the
  drop-params page shows as `get_supported_openai_params("command-r")` needs the
  provider argument to disambiguate. For `guide/05-llm-ops-reliability.md` ~L338-341
  ("audit existing request parameters against the model's supported set before
  routing production traffic") this settles *how* the audit is done: one
  function call per candidate model+provider, run before traffic is routed,
  never a provider capability table. The example output is also a useful
  reality check — a modern Anthropic model via Bedrock supporting four OpenAI
  params is a far narrower surface than the matrix's `Anthropic` row suggests.

### Claim 9: `stream_options={"include_usage": True}` is documented as returning usage on the final chunk for every provider, and the wire shape is an extra chunk before `data: [DONE]` with an empty `choices` array while all other chunks carry `usage: null`
- **Evidence**: The `include_usage` sub-field definition under `stream_options`,
  carrying the full wire contract, plus the provider-uniformity clause in the
  exemption sentence (Claim 1).
- **Confidence**: settled for the **wire shape** (explicit and complete
  vendor specification, consistent with OpenAI's documented streaming format);
  **anecdotal** for the **"every provider"** clause (uniformity assertion, no
  matrix, no wire captures, no tests — see `Our assessment` of Claim 1)
- **Quote**: "If set, an additional chunk will be streamed before the data: [DONE] message. The usage field on this chunk shows the token usage statistics for the entire request, and the choices field will always be an empty array. All other chunks will also include a usage field, but with a null value."
- **Our assessment**: The single strongest cross-source corroboration in the
  corpus for any LiteLLM claim. `docs-litellm-streaming-token-usage.md` Claim 2
  states this wire contract from a different page, in near-identical vendor
  wording, and its Claim 3 records the *other* page's uniformity assertion
  ("Supported across all providers. Works the same as openai") as
  `anecdotal` for the same reason we grade the "every provider" clause here.
  Two pages agreeing is better than one, but both are the same vendor making
  the same unsourced claim, so the grade does not move — the **wire shape** is
  now `settled` across two independent pages, the **provider uniformity** stays
  `anecdotal`. One operational consequence is worth carrying forward and is
  *not* in the streaming note: the guarantee is **conditional on the caller
  opting in**. A streamed request without `stream_options` is usage-blind, and
  this page's framing ("returns usage on the final chunk **for every
  provider**") can easily be misread as "LiteLLM returns usage on streaming
  responses" — which is false by default. For a gateway team auditing spend
  coverage, the check is therefore per-caller opt-in, not per-provider.

### Claim 10: `seed` is documented as best-effort Beta with determinism explicitly **not** guaranteed, and `system_fingerprint` is named as the signal for detecting backend drift
- **Evidence**: The `seed` field definition, with the non-guarantee clause and the
  named response parameter.
- **Confidence**: settled as a documented **non**-guarantee (the vendor states
  the limit explicitly, which is stronger evidence than a guarantee would be)
- **Quote**: "This feature is in Beta. If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result. Determinism is not guaranteed, and you should refer to the system_fingerprint response parameter to monitor changes in the backend."
- **Our assessment**: This bears directly on
  `guide/05-llm-ops-reliability.md` ~L1001's concern that "a deterministic eval
  or regression suite running through that path is silently reconfigured" —
  this gives the vendor's own reason and, more usefully, the one concrete
  detection field the corpus has never recorded: **`system_fingerprint`**.
  No source note documents `system_fingerprint`'s *role* as a drift signal —
  the only corpus occurrence is as a literal response key in
  `docs-litellm-completion-batching.md`'s artifacts
  (`"system_fingerprint": "fp_179b0f92c9"` and `"system_fingerprint": null`),
  and `guide/` never mentions it (re-verified this session). The operational
  rule that falls out: a seeded eval run is not
  reproducible by contract, and backend drift is detectable only if
  `system_fingerprint` is recorded per response — which means an eval harness
  that stores only outputs cannot distinguish "the model changed behavior" from
  "the model changed weights". Note also that this is the *provider-side*
  contract as surfaced by the gateway; the page does not say whether LiteLLM
  pins or forwards `seed` per provider, so cross-provider seed equivalence is
  undetermined here.

### Claim 11: `input_cost_per_token` and `output_cost_per_token` are per-call cost overrides sitting on the same request body as `metadata` — a spend-*attribution* surface whose blast radius depends on who can set them
- **Evidence**: A `CUSTOM MODEL COST` subsection under litellm-specific params
  giving the two fields as floats, defined as "the cost per ... token for the
  completion call".
- **Confidence**: settled for the **surface** (two named float fields with
  per-call scope); the **effect** — whether the override changes what is
  *charged* or only what is *recorded* — is **not** stated on the page and is
  recorded as an open question, not assumed
- **Quote**: "input_cost_per_token: float (optional) - The cost per input token for the completion call" / "output_cost_per_token: float (optional) - The cost per output token for the completion call"
- **Our assessment**: Extends the corpus's existing placement of the same knob at
  *deployment* level — `docs-litellm-adaptive-router.md` carries
  `input_cost_per_token: 0.000002` under a router entry's `model_info` (its
  Concrete Artifacts) as a sibling of that entry's `litellm_params`, i.e. the
  operator-set, config-file placement. This page
  documents the **per-request** placement, which is the placement with a
  different risk profile: a value that arrives in the request body is a value a
  *caller* can set. If the override feeds the gateway's spend ledger, then
  `input_cost_per_token=0.0000001` is a caller-supplied discount on recorded
  spend, and a fleet's cost attribution becomes only as trustworthy as its
  caller population. We do not assert that this is the behavior — the page
  documents neither the effect nor any restriction on who may set it, and the
  Proxy's own spend-tracking surface is out of this page's scope. What the page
  *does* establish is that the knob is request-scoped, which is the precondition
  the question needs. Adjacent and also request-scoped: `metadata` ("Any
  additional data you want to be logged when the call is made (sent to logging
  integrations, eg. promptlayer and accessible via custom callback function)"),
  which is the documented per-call tagging hook.

### Claim 12: `tools[].type` may be `"mcp"`, so the ordinary `/chat/completions` path can invoke LiteLLM-registered MCP servers directly — a world-mutating capability on the main request surface
- **Evidence**: The `type` sub-field definition under `tools`, naming both
  accepted values and the effect of the second.
- **Confidence**: settled (explicit vendor statement of the accepted value and
  the call target)
- **Quote**: "type: string - The type of the tool. You can set this to "function" or "mcp" (matching the /responses schema) to call LiteLLM-registered MCP servers directly from /chat/completions."
- **Our assessment**: Recorded per the Prospector's instruction to flag rather
  than mine, but the cross-reference is substantive rather than decorative,
  because it changes the *threat surface* of the main endpoint. The corpus
  already treats MCP as a distinct surface with its own hardening requirements:
  `docs-litellm-gateway-auth-reference.md` Claim 1 records that the MCP ASGI
  routes "bypass the standard FastAPI auth dependency" and Claim 2 that MCP
  outbound auth is a nine-valued per-server `auth_type`; and
  `failure-litellm-mcp-stdio-command-injection.md` documents an authenticated
  RCE in MCP server *creation* (three affected surfaces: creation, preview
  endpoints, rehydrated servers). If a registered MCP server is reachable from
  `/chat/completions` by a normal client request, then the MCP registration
  surface and the chat-completions surface are coupled, and an operator who
  hardened `/mcp` as a separate endpoint has to reason about the coupling. The
  page states the capability and none of its controls — no auth statement, no
  per-caller restriction, no allowlist. The countervailing corpus position is
  `docs-google-sre-prodcast-04-09-ai-agents.md` Claim 3: the default guardrail
  is to deny an agent any world-mutating action and require explicit human
  permission per write. Whether a `tools[].type: "mcp"` call is gated that way
  on this path is **not** documented here — an open sub-question, not a
  conclusion.

### Claim 13: SDK-level `fallbacks` has no time budget, no loop and no cooldown — each entry is tried exactly once in order, total failure raises the last error suffixed `All fallback attempts failed`, and the successful response carries an `x-litellm-attempted-fallbacks` header
- **Evidence**: The "How does fallbacks work" section of the linked page
  `https://docs.litellm.ai/docs/completion/reliable_completions` (HTTP 200,
  read in full), whose input page is the one this note's `fallbacks` definition
  points at. The section is five consecutive prose sentences plus a routing
  recommendation.
- **Confidence**: settled (explicit vendor statement of the attempt order, the
  loop policy, the failure string, the response header, and the recommended
  alternative)
- **Quote** (from https://docs.litellm.ai/docs/completion/reliable_completions): "When you pass fallbacks to completion, LiteLLM builds the attempt list [model] + fallbacks and calls each entry once, in order. The first response that comes back is returned; a failing entry is logged and the next one is tried. There is no time budget, no repeated loop over the list and no cooldown: once every entry has failed, completion raises an exception carrying the last error, suffixed with All fallback attempts failed."
- **Quote** (same page): "The successful response carries the x-litellm-attempted-fallbacks header with the number of fallbacks that were attempted before it."
- **Quote** (same page): "If you need cooldowns for failing deployments or retries with backoff, use the Router, which tracks deployment health and cooldown periods; see the proxy reliability docs."
- **Our assessment**: The single most ops-valuable item across both pages, and
  it is the **first partial answer in the corpus to
  `guide/05-llm-ops-reliability.md`'s "Silent model fallback breaks
  attribution" rule (~L973-985)**. That rule currently prescribes reading the
  response `model` field, which does catch model *substitution* on this path
  (the responding model is the fallback model, so the field changes). What it
  does not catch is *how many* attempts it took to get there — and this header
  is exactly that number, on the successful response, at zero extra
  configuration. That makes "record `x-litellm-attempted-fallbacks`" a
  concrete, cheap addition to the chapter's rule, and the symmetric case is
  worth stating too: a value of 0 is a positive signal (no degradation), which
  no error-rate metric provides. The three negative facts are equally
  consequential. (1) **No time budget**: a fallback chain of length N has
  worst-case latency of N × the per-attempt timeout, and with the 600s default
  of Claim 5 that is a multi-hour worst case that no single caller-side timeout
  can bound. (2) **No loop and no cooldown**: retry/backoff is explicitly
  delegated to the Router, so an SDK caller who reads `fallbacks` as
  "resilience" gets exactly one pass with no backoff. (3) The failure string is
  only a **suffix on the last error**, so an alerting rule matching on exception
  type will not see a distinct "all fallbacks exhausted" class. Note also that
  `fallbacks` and `context_window_fallback_dict` (Claim 4) are governed by this
  same attempt-list machinery or not is **not** stated — an open sub-question,
  since a context-window retry with no time budget has a different worst case
  than a generic one. The `num_retries` composition question raised by
  `docs-litellm-completion-batching.md` Claim 9 (does a hedged request also
  retry?) is **not** answered by either page and stays open.

## Concrete Artifacts

### `completion()` signature (verbatim, as published)

Line breaks and structure are the rendered code block's; the page's own copy
renders the trailing `**kwargs,` and `) -> ModelResponse: ...` on separate
lines.

```python
def completion(
    model: str,
    messages: List = [],
    # Optional OpenAI params
    timeout: Optional[Union[float, int]] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    n: Optional[int] = None,
    stream: Optional[bool] = None,
    stream_options: Optional[dict] = None,
    stop=None,
    max_completion_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    logit_bias: Optional[dict] = None,
    user: Optional[str] = None,
    # openai v1.0+ new params
    response_format: Optional[dict] = None,
    seed: Optional[int] = None,
    tools: Optional[List] = None,
    tool_choice: Optional[str] = None,
    parallel_tool_calls: Optional[bool] = None,
    logprobs: Optional[bool] = None,
    top_logprobs: Optional[int] = None,
    safety_identifier: Optional[str] = None,
    deployment_id=None,
    # soon to be deprecated params by OpenAI
    functions: Optional[List] = None,
    function_call: Optional[str] = None,
    # set api_base, api_version, api_key
    base_url: Optional[str] = None,
    api_version: Optional[str] = None,
    api_key: Optional[str] = None,
    model_list: Optional[list] = None, # pass in a list of api_base,keys, etc.
    # Optional liteLLM function params
    **kwargs,

) -> ModelResponse: ...
```

Two things to read off this block, both cited above: `timeout` defaults to
`None` here while the prose says 600 seconds (Claim 5); and **neither
`num_retries` nor `max_retries` appears in the signature** — both arrive through
`**kwargs`, which is why the page's own naming inconsistency (Claim 2) is
invisible to anyone reading only the signature.

### Parameter-gate admonition (verbatim prose, all four sentences)

> By default, LiteLLM raises an exception if the openai param being passed in
> isn't supported.
>
> To drop the param instead, set `litellm.drop_params = True` or
> `completion(..drop_params=True)`.
>
> This **ONLY DROPS UNSUPPORTED OPENAI PARAMS**.
>
> LiteLLM assumes any non-openai param is provider specific and passes it in as
> a kwarg in the request body

### Support-matrix caption and gate exemptions (verbatim prose, one paragraph)

> This table is the output of litellm.get_supported_openai_params() for the
> model shown in each row. Support is model dependent within a provider (for
> example Bedrock Llama models do not list tools or tool_choice), so call the
> function for the exact model you use
>
> stream_options, extra_headers and max_retries are not checked against this
> list and are accepted for every provider, and
> stream_options={"include_usage": True} returns usage on the final chunk for
> every provider

### Introspection example (verbatim code block)

```python
from litellm import get_supported_openai_params

response = get_supported_openai_params(model="anthropic.claude-sonnet-5", custom_llm_provider="bedrock")

print(response) # ["max_tokens", "tools", "tool_choice", "stream"]
```

### litellm-specific params (verbatim, as published)

```
api_base: string (optional) - The api endpoint you want to call the model with
api_version: string (optional) - (Azure-specific) the api version for the call
num_retries: int (optional) - The number of times to retry the API call if an APIError, TimeoutError or ServiceUnavailableError occurs
context_window_fallback_dict: dict (optional) - A mapping of model to use if call fails due to context window error
fallbacks: list (optional) - A list of model names + params to be used, in case the initial call fails
metadata: dict (optional) - Any additional data you want to be logged when the call is made (sent to logging integrations, eg. promptlayer and accessible via custom callback function)
CUSTOM MODEL COST
input_cost_per_token: float (optional) - The cost per input token for the completion call
output_cost_per_token: float (optional) - The cost per output token for the completion call
CUSTOM PROMPT TEMPLATE (See prompt formatting for more info)
initial_prompt_value: string (optional) - Initial string applied at the start of the input messages
roles: dict (optional) - Dictionary specifying how to format the prompt based on the role + message passed in via messages.
final_prompt_value: string (optional) - Final string applied at the end of the input messages
bos_token: string (optional) - Initial string applied at the start of a sequence
eos_token: string (optional) - Initial string applied at the end of a sequence
hf_model_name: string (optional) - [Sagemaker Only] The corresponding huggingface name of the model, used to pull the right chat template for the model.
```

Note the section is titled "litellm-specific params" and then contains a
`CUSTOM PROMPT TEMPLATE` block; the page's own link for the prompt-formatting
detail is `/docs/completion/input#prompt-formatting`, and the standalone
`/docs/prompt_formatting` path returned **HTTP 404** when fetched this session
(the page uses an anchor on this URL instead). The first three lines are the
excerpt cited in Claims 2, 4, and 11.

### Multimodal `content` block types (verbatim, as published)

| Type | Description | Docs |
| --- | --- | --- |
| text | Text content | Type Definition |
| image_url | Images | Vision |
| input_audio | Audio | input Audio |
| video_url | Video input | Type Definition |
| file | Files | Document Understanding |
| document | Documents/PDFs | Document Understanding |

```python
# Text
messages=[{"role": "user", "content": [{"type": "text", "text": "Hello!"}]}]

# Image
messages=[{"role": "user", "content": [{"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}]}]

# Audio
messages=[{"role": "user", "content": [{"type": "input_audio", "input_audio": {"data": "<base64>", "format": "wav"}}]}]

# Video
messages=[{"role": "user", "content": [{"type": "video_url", "video_url": {"url": "https://example.com/video.mp4"}}]}]

# File
messages=[{"role": "user", "content": [{"type": "file", "file": {"file_id": "https://example.com/doc.pdf"}}]}]

# Document
messages=[{"role": "user", "content": [{"type": "document", "source": {"type": "text", "media_type": "application/pdf", "data": "<base64>"}}]}]

# Combining multiple types (multimodal)
messages=[{"role": "user", "content": [
 {"type": "text", "text": "Generate a product description based on this image"},
 {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
]}]
```

The `document` block and the `video_url` block are the two types in this table
that no other LiteLLM source note in the corpus inventories; recorded as
surface inventory, not as a claim about provider support (the page does not say
which providers accept them).

### SDK fallback code samples (verbatim, from
`https://docs.litellm.ai/docs/completion/reliable_completions`)

```python
from litellm import completion
fallback_dict = {"gpt-3.5-turbo": "gpt-3.5-turbo-16k"}
messages = [{"content": "how does a court case get to the Supreme Court?" * 500, "role": "user"}]
completion(model="gpt-3.5-turbo", messages=messages, context_window_fallback_dict=fallback_dict)
```

```python
response = completion(model="bad-model", messages=messages, 
 fallbacks=["gpt-5.6-luna", "command-nightly"])
```

```python
api_key="bad-key"
response = completion(model="azure/gpt-5.6-terra", messages=messages, api_key=api_key,
 fallbacks=[{"api_key": "good-key-1"}, {"api_key": "good-key-2", "api_base": "good-api-base-2"}])
```

The second sample is the page's own worked example of a *failed primary*:
`"Completion with 'bad-model': got exception Unable to map your input to a model.
Check your input - {'model': 'bad-model'"` followed by a successful
`"completion call gpt-5.6-luna"` and a full response body. The third shows that
a fallback entry may be a **dict of completion kwargs** (a different `api_key` /
`api_base`) rather than a model name — so `fallbacks` is not a model list, it is
an ordered list of call shapes.

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path is cited or
dismissed below):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch
  input-file rate limiting, per-record token charging, and
  `batch_enqueued_token_limit`; this page is the per-request input surface with
  no batch accounting.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed** as a
  cross-reference, with one surface adjacency worth recording: that note's Claim
  1 covers the *native Bedrock Invoke passthrough* route
  (`POST /bedrock/model/<model_name>/invoke`), whereas Bedrock here is a **row
  in the support matrix** (the `Bedrock / anthropic.claude-3-5-sonnet-...` row)
  and the caption's Bedrock-Llama counterexample. Two different Bedrock
  surfaces; no claim overlap.
- `source-notes/docs-litellm-audio-transcription.md` — **Cited (Extends /
  Corroborates)**: **Claim 6** of that note establishes that "the support
  matrix is a recurring per-endpoint feature-support contract across the
  LiteLLM docs, not a one-off table." This page supplies the *other* instance and
  a second matrix kind — a **param** matrix (20 OpenAI params × 25 providers)
  alongside the **feature** matrix that note documents for
  `/v1/audio/transcriptions`. That note's Claim 4 (a transcription model must be
  registered with `model_info: mode: audio_transcription` or the non-chat
  endpoint is not routable) is the same *registration-gates-routability*
  mechanism in a different place. No conflict.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Cited, with a
  tension recorded and reconciled (no contradiction filed)**: that note's
  **Claim 2** states advisor tokens are "reachable only via
  `usage.iterations[]` entries" and that top-level `usage` is "executor tokens
  only", while this page's `include_usage` contract says the usage chunk "shows
  the token usage statistics for the **entire request**". Read together these
  are consistent — the streamed chunk carries the same top-level `usage`
  object, so "entire request" scopes the chunk to the whole request rather than
  to the chunk, and the advisor's sub-inference tokens remain outside top-level
  `usage` by that note's own finding. The reconciliation is recorded in
  Extraction Notes per MINER §4a; the operational caution stands: a
  gateway-wide "streamed usage covers the request" rule has an
  advisor-tool-shaped exception.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Cited (Extends)**:
  that note's **Claim 1** documents the A2A gateway's two per-session
  cost controls (`max_iterations`, `max_budget_per_session`) and its **Claim 4**
  the budget's asymmetric timing. This page documents the plain-`completion()`
  surface those controls are *absent* from: the only cost-related per-call knobs
  on the SDK input surface are the two **price-reporting** overrides
  (`input_cost_per_token` / `output_cost_per_token`, Claim 11), not a spend
  **cap**. So the corpus's only documented per-session spend ceiling is on the
  A2A gateway; a plain SDK caller routed through the same gateway has no
  documented in-band budget stop and must rely on the proxy/Router surfaces.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **Cited (Extends /
  Contrast)**: that note's **Claim 3** establishes that the A2A flat per-query
  cost is "a gateway-declared synthetic charge" with "no documented linkage to
  the agent's measured token usage or upstream model cost", and its **Claim 4**
  that configured agent cost is attributed to the calling key. This page's
  `input_cost_per_token` (Claim 11) is the mirror image: a synthetic price that
  is **caller-supplied** rather than operator-declared. Both are gateway
  price declarations disconnected from measured upstream cost; they differ in
  *direction of control*, and that difference is the reason the question in
  Claim 11's assessment ("does a caller-supplied price move the ledger?") is
  worth asking. No conflict.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: Langfuse's own
  public documentation MCP server (endpoint, transports, per-client config);
  unrelated product. Noted only because this page's `tools[].type: "mcp"`
  (Claim 12) is also an MCP surface — different product, different registry,
  no claim overlap.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Cited
  (Extends)**: **Claim 3** — "The default guardrail is to deny agents any
  world-mutating action and require explicit human permission before any
  write". This page puts a world-mutating capability (registered MCP tool
  invocation) on the ordinary `/chat/completions` request path (Claim 12) and
  documents no gate on it. The corpus's canonical guardrail statement and this
  page's capability are complementary: the Prodcast claim says what the default
  should be, this page shows a surface where the default is unstated. Recorded
  as an open sub-question in Claim 12's assessment, not as a contradiction.
- `source-notes/blog-litellm-auto-router-v2.md` — **Cited (Corroborates +
  Extends)**: **Claim 11** of that note lists as a *roadmap* item "Escalation
  ceilings on fallback chains. Per-request cap on escalations plus a cooldown
  once a key walks the chain N times, so a bad upstream cannot cascade into a
  bill." This note's Claim 13 documents the **shipped SDK** state of the same
  mechanism: "There is no time budget, no repeated loop over the list and no
  cooldown". Read together they are a before/after pair on one mechanism — SDK
  fallbacks have no cooldown today, the Router tracks cooldown, and a per-request
  escalation cap is not yet merged — which is a stronger and more useful record
  than either note alone. That note's **Claim 3** ("predictable beats clever for
  debuggability") is the same philosophy, and Claim 13's response header is the
  concrete instance of it. No conflict: roadmap vs shipped is a time ordering,
  not a disagreement.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **Dismissed**:
  Langfuse's input/output scanner stack and two-pronged security architecture.
  Adjacency noted once: this page's `safety_identifier` is a per-request
  "unique identifier for tracking and managing safety-related requests", which
  is the gateway-side counterpart to that note's per-check score logging, but no
  claim is shared and nothing is cited.

**Additional cross-references found by searching `source-notes/` and `guide/`**
(the candidates file was not exhaustive):

- **Corroborates**:
  - `source-notes/docs-litellm-drop-params.md` **Claim 1** — "By default,
    LiteLLM raises an exception if you send a parameter to a model that doesn't
    support it" / "`drop_params=True` … will drop the unsupported parameter
    instead of raising an exception." This page's admonition box states the
    same polarity in different words and with one addition that note does not
    have (Claim 3's scope limit). No conflict; this page is a second,
    independent restatement of the polarity.
  - `source-notes/docs-litellm-drop-params.md` **Claim 2** — the
    per-provider-**and**-model keying and the
    `litellm.get_supported_openai_params(...)` introspection form. This page's
    Claim 8 corroborates it and adds the two-argument form, the printed
    four-element Bedrock output, and the vendor's own disclaimer of the
    published table.
  - `source-notes/docs-litellm-streaming-token-usage.md` **Claims 1 and 2** —
    the `include_usage` opt-in and the "additional chunk … empty array … other
    chunks … null" wire contract. This page's Claim 9 states the same contract
    in near-identical vendor wording from a second page. Claim 3 of that note
    grades the *other* page's provider-uniformity assertion `anecdotal`; this
    page's "for every provider" clause is graded the same way, for the same
    reason (see Claim 1's assessment).
  - `source-notes/docs-litellm-completion-batching.md` **Claim 9** — that note
    records as an open question "does the fastest-response flag compose with
    router fallbacks and `num_retries`, or replace them". This note supplies
    the *retry* half of that question's vocabulary (`num_retries`, Claim 2) and
    the *fallback* execution model (Claim 13: one pass, no loop, no cooldown),
    but neither page states how the two compose for a hedged request, so the
    question remains open and is restated as such rather than answered.
- **Contradicts**: None filed, and no self-contradiction in the source. Two
  tensions were examined and both are **conditioning-variable** differences
  rather than claim conflicts, per MINER §4a "when NOT to file":
  (a) the 600s default here vs the three `aiohttp` timeout profiles in
  `docs-litellm-completion-http-handler-config.md` **Claim 7** — different
  surfaces (per-request completion timeout vs. a custom client-session
  transport profile), and *neither* page derives its numbers, so the shared
  finding is "no LiteLLM timeout number in the corpus is sourced", not a
  disagreement about a fact; and (b) the advisor-tool `usage` composition noted
  above. Verified before deciding: all nine open `contradiction`-labeled issues
  (#1150, #1307, #1322, #1338, #1352, #1408, #1461, #1462, #1486 — routing,
  promptfoo, A2A storage, `thinking.summary`, advisor tool) and
  `CONTRADICTIONS.md` (no `C-NNN` entries) cover none of this surface.
- **Extends**:
  - `source-notes/docs-litellm-drop-params.md` **Claim 9** — that note's
    most consequential claim is an *absence*: the page documents no log line,
    metric, response field or header for a drop, so "param honored" and "param
    silently stripped" are indistinguishable. This note records the two
    **positive** signal cases in the same neighborhood that note could not find:
    `x-litellm-attempted-fallbacks` on a successful fallback response
    (Claim 13) and the named `system_fingerprint` drift signal (Claim 10).
    Together the three notes give the guide a usable asymmetry — some gateway
    behaviors are attributable and some are not — where the drop-params note
    alone could only report the negative half.
  - `source-notes/docs-litellm-drop-params.md` **Claim 3** — that note
    records `drop_params` in four placements with no documented precedence. This
    page adds a *fifth* control in the same namespace that has no precedence
    statement and no per-deployment form at all: `litellm.disable_stop_sequence_limit`
    (Claim 6), documented as a module-global only. Same failure class, more
    constrained remediation.
  - `source-notes/docs-litellm-adaptive-router.md` — **cited by section**, per
    MINER §4b: its **Concrete Artifacts** carry
    `input_cost_per_token: 0.000002` under a router entry's `model_info` (a
    sibling of that entry's `litellm_params`), i.e. the operator/deployment-level
    placement of the same knob that this page documents at request scope
    (Claim 11). No numbered claim in that note is about the knob, so it is cited
    by section rather than by claim number.
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claims 1 and 2** —
    MCP ASGI routes bypassing the standard FastAPI auth dependency, and MCP
    outbound auth as a nine-valued per-server `auth_type`. This is the
    registration/auth surface that `tools[].type: "mcp"` (Claim 12) calls into;
    the input page documents none of its controls.
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md` — **cited by
    section**, per MINER §4b: its **"Vulnerability Detail C: Three affected
    surfaces — server creation, preview endpoints, and rehydrated servers"** and
    **"Fix Layer 1: `MCP_STDIO_ALLOWED_COMMANDS` frozenset allowlist"** are the
    hardening this page's `mcp` tool type would need to inherit if
    `/chat/completions` can reach a registered server (Claim 12).
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — **cited
    by section**, per MINER §4b: **"Symptom 1: Silent fallback with no warning
    logged"** and **"Lesson 2: Silent fallback to stale local data is worse than
    failing loudly"** are the corpus's failure-report framing for the same
    hazard this page's `context_window_fallback_dict` (Claim 4) and
    silent `stop` truncation (Claim 6) instantiate on the request path — the
    report's recommendation (log the substitution) is exactly the control
    neither this page nor the linked reliability page documents for these two
    paths.
- **Novel**: First corpus coverage of the **`completion()` input surface
  itself**; verified this session that `source-notes/` and `guide/` contain
  **zero** occurrences of `context_window_fallback_dict`,
  `disable_stop_sequence_limit`, `x-litellm-attempted-fallbacks`,
  `All fallback attempts failed`, "600 second", or "completion/input". The
  string `system_fingerprint` is **not** a zero-hit term — it appears as a
  literal response key in `docs-litellm-completion-batching.md`'s artifacts —
  but no source note documents its **role** as a drift signal, and `guide/`
  never mentions it. Specifically new to the corpus: the gate's **outer
  boundary** — non-OpenAI params are assumed provider-specific and passed
  through as request-body kwargs, so `drop_params` cannot catch a misspelled
  OpenAI param (Claim 3); the gate's **three hard-coded exemptions** and the
  page's own `max_retries` / `num_retries` naming inconsistency (Claims 1, 2);
  the **600s documented default timeout** and the signature/prose disagreement
  about it (Claim 5); **silent 4-element `stop` truncation** with a
  module-global-only opt-out (Claim 6); the **JSON-mode whitespace-stream
  liveness failure** and the `finish_reason="length"` truncation caveat on the
  "guarantees valid JSON" promise (Claim 7); `context_window_fallback_dict` as a
  second, trigger-keyed fallback mechanism (Claim 4); the SDK fallback execution
  model — one pass, no time budget, no cooldown — together with the
  `x-litellm-attempted-fallbacks` response header, the first positive
  attribution signal in the corpus for silent fallback (Claim 13);
  `seed`'s documented non-guarantee plus `system_fingerprint` as the named
  drift signal (Claim 10); the request-scoped cost overrides (Claim 11); and
  `tools[].type: "mcp"` on `/chat/completions` (Claim 12).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Parameter migration hazards"
  (~L327-341)**: The chapter's Rule — "Parameters valid on earlier models may be
  silently ignored or explicitly rejected" — has been given its determination by
  `docs-litellm-drop-params.md` (the branch is a config flag). Add the two
  boundaries this source supplies. (1) **A third silent branch exists and it is
  not a param-support problem at all**: a `stop` list longer than 4 is truncated
  to the first 4 by the gateway, silently, with a module-global-only opt-out
  [Claim 6] [settled] — the parameter is fully supported; the gateway discards
  part of it, so a caller can receive a valid 200 with N−4 of its stop
  sequences inert. (2) **The support gate is namespace-scoped, not
  schema-scoped**: a param LiteLLM does not recognize as an OpenAI param is
  passed into the request body as a kwarg [Claim 3] [settled], so a *typo'd*
  OpenAI param is neither dropped nor rejected — it goes upstream. The
  migration audit therefore needs a second check the chapter does not
  currently have: verify parameter **names**, not just support sets, since the
  audit tool that does this is already the documented one —
  `get_supported_openai_params(model, custom_llm_provider)` run per candidate
  model+provider before routing traffic [Claim 8] [settled]. Do **not** state
  any LiteLLM timeout number as evidence-backed: the 600s default is
  unsourced [Claim 5] and the transport page's profiles are already recorded as
  unsourced in `docs-litellm-completion-http-handler-config.md` Claim 7.
- **Chapter 05, "Cost, capacity, and fallback patterns" → "Silent model
  fallback breaks attribution" (~L971-985)**: The chapter's Rule today is to
  surface the response `model` field. Add the missing half and a fourth
  substitution authority. (1) **Read `x-litellm-attempted-fallbacks` on the
  successful response** — it carries the number of fallbacks attempted before
  the response that was returned [Claim 13] [settled]. It catches what the
  `model` field cannot: *how much degradation it took*, and it makes "this
  request was answered by the primary" a positive signal (value 0) rather than
  an absence of evidence. (2) **Record the worst case, because it is
  multiplicative**: SDK `fallbacks` has "no time budget, no repeated loop over
  the list and no cooldown", and each entry is tried exactly once [Claim 13]
  [settled], so a chain of length N has worst-case latency N × per-attempt
  timeout — and the documented per-attempt default is 600s [Claim 5]. A caller
  cannot bound this with a single client timeout. (3) **Retry/backoff is the
  Router's job, not the SDK's** — the vendor says so explicitly [Claim 13], so
  a runbook that instructs "add fallbacks" without mentioning the Router
  recommends the option with no backoff. (4) **Add `context_window_fallback_dict`
  to the chapter's list of substitution authorities**, keyed on a
  *context-window error* rather than a general failure [Claim 4] [settled]. It
  is the dangerous one for evaluation work, because whether a request is
  substituted depends on the size of that request's context: a regression suite
  whose prompts grew past a boundary can start being answered by a different
  model with no error. No header is documented for this path, so the response-
  `model` check is the only available control — the chapter should say so
  explicitly rather than leave the reader assuming the header covers all
  fallback mechanisms.
- **Chapter 05 / evaluation guidance, seeded-reproducibility rule (~L1001)**:
  The chapter's concern that "a deterministic eval or regression suite running
  through that path is silently reconfigured" now has the vendor's own answer:
  seeded sampling is a documented **best-effort Beta** with determinism
  "not guaranteed", and the named detection signal is
  `system_fingerprint` [Claim 10] [settled]. Add the concrete rule: record
  `system_fingerprint` per response, because a harness that stores only outputs
  cannot distinguish "the model behaved differently" from "the backend changed".
  Also add the JSON-mode precondition from this page, which is a *prompt*
  requirement rather than a config one: a `response_format={"type":
  "json_object"}` call with no explicit "return JSON" instruction can emit an
  unbounded whitespace stream to the token limit, which the vendor describes as
  a "seemingly stuck" request [Claim 7] [settled] — so structured-output
  harnesses must both include the instruction and check `finish_reason` before
  trusting a parse, because the same callout admits content can be cut off at
  `finish_reason="length"`.
- **Chapter 05, "Cost, capacity, and fallback patterns" (spend attribution)**:
  The corpus's only documented per-session spend **cap** is on the A2A gateway
  (`docs-litellm-a2a-iteration-budgets.md` Claim 1). This source establishes
  that the plain `completion()` surface carries per-call cost *overrides* —
  `input_cost_per_token` / `output_cost_per_token`, settable **per request**
  [Claim 11] [settled-for-surface]. The chapter should state that a
  request-scoped price knob exists and that, on this page, its effect on the
  spend ledger is not documented — an open question, not a warning. The
  operator-set placement of the same knob is already in the corpus
  (`docs-litellm-adaptive-router.md`, Concrete Artifacts — a router entry's
  `model_info`), so the guidance
  should distinguish operator-set from caller-set. Pair with `metadata`, which
  this page documents as the per-call hook "sent to logging integrations" —
  the tagging surface for attributing a request's spend to a caller.
- **Chapter 02 (Observability), absent-signal rule**: `docs-litellm-drop-params.md`
  Guide Impact asks the Smith to add an absent-signal rule for the drop path.
  This source supplies the counterweight the guide needs to state both halves:
  three gateway behaviors **are** attributable — `x-litellm-attempted-fallbacks`
  on a fallback response, `system_fingerprint` on every response, and the
  response `model` field — while `stop` truncation, non-OpenAI kwarg
  passthrough, and the `context_window_fallback_dict` path have **no**
  documented signal [Claims 3, 4, 6, 10, 13] [mixed settled / documented-
  absence]. The rule worth writing: build the gateway dashboard on the
  documented signal set, and treat everything outside it as an unmonitored
  parameter surface — which is now a *specific, enumerated* list rather than
  the general worry the drop-params note could only state.
- **Chapter 03 (Runbooks and agents) — agent guardrails**: Pair with
  `docs-google-sre-prodcast-04-09-ai-agents.md` Claim 3 ("the default guardrail
  is to deny agents any world-mutating action and require explicit human
  permission before any write"). This source documents that a normal
  `/chat/completions` client request can invoke a **LiteLLM-registered MCP
  server** via `tools[].type: "mcp"` [Claim 12] [settled], and documents no auth
  gate, per-caller restriction, or allowlist on that path. A runbook that
  permits agents to call `/chat/completions` with tools should either forbid the
  `mcp` tool type explicitly or require the server registration to sit behind
  the controls the corpus already records for the MCP surface
  (`docs-litellm-gateway-auth-reference.md` Claims 1-2;
  `failure-litellm-mcp-stdio-command-injection.md`, Fix Layer 1). Do not state
  a control that exists — this source shows the coupling and the silence, and
  the guide should be explicit that the silence is undocumented rather than
  absent.

## Extraction Notes

- Source read in full via `curl` (HTTP 200, ~100 KB) with the `<article>`
  body converted to text; all four code blocks, the 25-row × 20-column support
  matrix, the content-types table, and every prose section were extracted.
  Nothing was skipped, and no part of the page was paywalled, gated, or
  behind auth. Two additional pages were read in full because this page's own
  prose points at them and the Prospector asked for the retry/fallback
  semantics specifically: `https://docs.litellm.ai/docs/completion/reliable_completions`
  (HTTP 200) and `https://docs.litellm.ai/docs/completion/output` (HTTP 200).
  `https://docs.litellm.ai/docs/prompt_formatting` returned **HTTP 404** — the
  page links prompt-formatting detail to an anchor on its own URL instead
  (recorded in Concrete Artifacts).
- **Quote attribution policy.** Every `Quote` on Claims 1-12 is a
  character-for-character contiguous fragment of
  `https://docs.litellm.ai/docs/completion/input`, verified by locating the
  passage in the fetched HTML and copying it. Claim 13's three quotes are from
  `https://docs.litellm.ai/docs/completion/reliable_completions` and each
  carries its source URL inline in the `Quote` label, because the Assayer
  spot-checks against `source_url`. No quote is spliced across non-adjacent
  sentences; where two sentences of the same paragraph are both essential
  (e.g. the gate note, the litellm-specific param definitions) they appear as
  separate slash-delimited fragments of the same contiguous passage.
  Interpreted consequences are in `Our assessment`, never in `Quote`. Quotes
  containing the page's own double quotes (the JSON-mode "stuck" callout) keep
  them as rendered.
- **Claim 2 is a verified string count, not a reading impression.** `max_retries`
  occurs exactly once in the fetched page (the exemption sentence) and
  `num_retries` exactly once (the litellm-specific params list); neither occurs
  in the signature block. This is re-checkable by anyone who greps the page. The
  claim deliberately stops short of asserting what the gateway *does* with a
  `max_retries` kwarg — that is not documented, and Claim 3's pass-through rule
  is cited as the reason the consequence is quiet, not as proof that it is
  accepted.
- **Claim 5 splits its confidence on purpose.** The prose default ("Defaults to
  600 seconds") and the signature default (`= None`) are both verbatim from the
  page and their disagreement is `settled`; which one an operator should apply
  is `emerging` because the page does not say. The claim asserts no effective
  runtime value, and the Guide Impact entry explicitly instructs the Smith not
  to cite any LiteLLM timeout number as evidence-backed.
- **Advisor-tool `usage` tension examined, no contradiction filed** (MINER §4a
  "when NOT to file"): `docs-litellm-anthropic-advisor-tool.md` Claim 2 states
  advisor tokens are reachable only via `usage.iterations[]` and that top-level
  `usage` is "executor tokens only"; this page's `include_usage` contract says
  the usage chunk "shows the token usage statistics for the entire request".
  These reconcile — the streamed chunk carries the same top-level `usage`
  object, so "entire request" scopes the chunk to the request rather than to the
  chunk, and the advisor's sub-inference tokens stay outside top-level
  `usage` — so the two claims are both true and describe different objects.
  Recorded as a caution (a gateway-wide "streamed usage covers the request"
  rule has an advisor-tool-shaped exception) rather than filed.
- **Timeout-profile tension examined, no contradiction filed**: this page's
  600s default vs the three `aiohttp` profiles in
  `docs-litellm-completion-http-handler-config.md` Claim 7 are different
  surfaces (per-request completion timeout vs. a custom client-session transport
  profile) and neither page derives its numbers, so the shared finding is that
  no LiteLLM timeout number in the corpus is sourced — not a factual
  disagreement. Per §4a this is a conditioning variable, not a contradiction.
  Checked all nine open `contradiction`-labeled issues and `CONTRADICTIONS.md`
  (no `C-NNN` entries) before deciding.
- **Cross-reference verification (MINER §4b)**: every numbered `Claim N` cited
  above was re-read in its source note and the number confirmed to match the
  cited content — `docs-litellm-drop-params.md` Claims 1, 2, 3, 9;
  `docs-litellm-streaming-token-usage.md` Claims 1, 2, 3;
  `blog-litellm-auto-router-v2.md` Claims 3, 11;
  `docs-litellm-audio-transcription.md` Claims 4, 6;
  `docs-litellm-a2a-iteration-budgets.md` Claims 1, 4;
  `docs-litellm-a2a-cost-tracking.md` Claims 3, 4;
  `docs-litellm-completion-batching.md` Claim 9;
  `docs-litellm-completion-http-handler-config.md` Claim 7;
  `docs-litellm-gateway-auth-reference.md` Claims 1, 2;
  `docs-google-sre-prodcast-04-09-ai-agents.md` Claim 3;
  `docs-langfuse-mcp-server.md` Claims 1-7 (dismissed);
  `docs-langfuse-security-and-guardrails.md` Claims 1-11 (dismissed);
  `docs-litellm-bedrock-invoke.md` Claims 1-10 (dismissed);
  `docs-litellm-batches-api.md` Claims 1-11 (dismissed). Three notes are cited
  **by section name, not by claim number**, per §4b step 4, because the
  material lives outside numbered claims:
  `docs-litellm-adaptive-router.md` (Concrete Artifacts — the `input_cost_per_token`
  config value), `failure-litellm-mcp-stdio-command-injection.md`
  ("Vulnerability Detail C" and "Fix Layer 1"), and
  `failure-litellm-model-cost-map-silent-fallback.md` ("Symptom 1" and
  "Lesson 2"). No claim number was invented.
- **No claim number in this note is asserted from LiteLLM source code.** The
  page links `litellm/utils.py` only from the *other* page (drop_params); this
  page's only external links are the content-type doc anchors and the
  prompt-formatting anchor, none of which were fetched (they resolve to the
  same page's anchors or to a 404). Every assertion is scoped to what the
  documentation says, and the four places where the documentation's silence is
  itself the finding (Claims 4, 6, 11, 12) say so explicitly rather than
  inferring behavior.
- **Duplicate-history note (context for the Assayer, not a re-litigation):**
  this URL was triaged and rejected once before, as #1252, on a stale read of an
  earlier revision. The Prospector's correction on #1495 verified that the page
  has since been rewritten — the four litellm-specific args #1252 read
  (`force_timeout`, `logger_fn`, `verbose`) are **absent** from the current
  revision, re-confirmed this session (zero occurrences of `force_timeout`;
  the only litellm-specific params present are `api_base`, `api_version`,
  `num_retries`, `context_window_fallback_dict`, `fallbacks`, `metadata`, the two
  cost overrides, and the prompt-template block). The `azure` arg is likewise
  absent as a named param. This note therefore describes the current revision
  only, and `last_checked` is set accordingly. Per the Prospector, the
  parameter-gate material that #1252's rejection was *partly* about is not
  re-derived here — it is cited as corroboration and extended (Claim 3) rather
  than restated as a new claim.
