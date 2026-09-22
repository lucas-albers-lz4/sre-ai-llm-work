---
source_url: https://docs.litellm.ai/docs/anthropic_unified/structured_output
source_type: docs
title: "Structured Output /v1/messages — liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-22)
date_extracted: 2026-09-22
last_checked: 2026-09-22
status: current
confidence_overall: emerging
issue: "#1391"
---

# Structured Output /v1/messages (liteLLM Docs)

> The `/v1/messages` structured-output child page documents the
> Anthropic-format `output_format` parameter (`{"type": "json_schema",
> "schema": {...}}`) with a **four-row, Anthropic-family-only support table**
> (Anthropic native, Azure AI, Bedrock Converse, Bedrock Invoke) — a
> per-feature capability boundary on the same endpoint whose parent matrix
> (#1382) advertises **all** LiteLLM providers — and an example response in
> which the structured payload arrives as a **JSON string inside
> `content[0].text`** with an ordinary `stop_reason: "end_turn"` and **no
> documented schema-violation signal**. The ops-relevant facts are (1) the
> feature matrix is the feature matrix — `output_format` support is narrower
> than `/v1/messages` endpoint support, and the two must not be conflated; (2)
> a caller who trusts `output_format` without parsing and schema-validating the
> text block gets a 200 with an unvalidated string; and (3) the page documents
> **no streaming statement and no error behavior** for `output_format` — both
> recorded as explicit absences, not inferred.

## Source Context

- **Type**: docs (single-page LiteLLM proxy endpoint reference — the
  structured-output child page of `/v1/messages`, under Supported Endpoints →
  `/v1/messages` in the docs nav).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented surface* — the parameter name/field
  contract and the per-backend support table. Vendor documentation of a
  translation layer, not independently exercised against any live backend; the
  ✅ cells are vendor assertions with no test matrix, wire captures, or
  schema-adherence evidence ("Supported" is not documented to mean
  "byte-identical schema enforcement across backends").
- **Scope**: The `output_format` structured-output contract on `/v1/messages`:
  a 4-row provider support table, four near-identical `config.yaml` + `curl`
  recipes (Anthropic / Azure AI / Bedrock Converse / Bedrock Invoke), one
  example response, and the request-format field reference. Does **not** cover:
  the endpoint's feature matrix (Cost Tracking, Logging, Streaming, Fallbacks,
  Guardrails — that is the parent page #1382), streaming behavior for
  `output_format`, schema-violation/refusal behavior, or any error path. The
  page is undated and carries no metrics or failure reports.
- **Redundancy**: No existing corpus note covers the native structured-output
  surface. A corpus grep for `output_format`/`json_schema` returns zero hits
  across `guide/`; in `source-notes/` the sole prior mention outside this note
  is a single mapping-table row in `docs-litellm-messages-to-responses-mapping.md`
  (#1390, line 288: `output_format` or `output_config.format` → `text`), which
  documents the OpenAI/Azure **translated** path — not the native
  `output_format` parameter contract, its field shape, or its per-backend
  support matrix. The parent note `docs-litellm-anthropic-unified.md` (#1382)
  owns the endpoint overview and is cross-linked, not restated. The sibling
  `docs-litellm-messages-to-responses-mapping.md` (#1390) documents what
  happens to `output_format` on the OpenAI/Azure path (translation to the
  Responses API) — see Cross-References; the three notes are the
  overview/feature/translation triple of the same endpoint family.
- **Contradiction scan (MINER §4a)**: No contradiction issue filed. The
  apparent tensions were checked per the Prospector's instruction and each
  resolved as a *different surface*, not an opposing claim:
  1. Parent #1382 Claim 1 ("**All LiteLLM supported providers**" for
     `/v1/messages` fan-out) vs this page's 4-row table — the parent's claim is
     about the *endpoint surface* (which providers can be routed through the
     Anthropic-shaped canvas); this page's table is the *per-feature*
     `output_format` capability. Same endpoint, different claim dimensions. The
     parent note itself reads its ✅ matrix as "surface support, not per-provider
     parity" (its Claim 2 assessment). Not a contradiction — a documented
     capability boundary on a uniformly-advertised surface, the same shape as
     the guardrail "(non-streaming only)" carve-out recorded in #1382 Claim 4.
  2. `blog-litellm-claude-fable-5-day-0.md` Claim 12 ("structured output, all
     available across Anthropic, Azure, **Vertex AI**, and Bedrock") vs this
     page's table (no Vertex AI row) — that is a *model-parity* claim on the
     OpenAI-compatible request surface, not a *unified-endpoint support-table*
     claim; the two pages are not asserting the same thing. Different surfaces,
     so the Vertex discrepancy is reported here as an open guide question, not
     filed (per the Prospector's "if they are different surfaces, say so and
     drop it").
  3. `#1390`'s `output_format` → `text` mapping row on the OpenAI/Azure path —
     composition, not opposition: it documents the *translated* path for
     OpenAI/Azure and is cross-linked, while this page's table is the *native*
     support matrix. See Cross-References.
  Verified no existing open contradiction covers this surface (open issues
  #1150, #1307, #1322, #1338, #1352, #1408; `CONTRADICTIONS.md` has no
  matching `C-NNN` entries).

## Extracted Claims

### Claim 1: On `/v1/messages`, structured output (`output_format`) is documented for exactly four Anthropic-family backends — Anthropic (native), Azure AI (Anthropic models), Bedrock Converse (Anthropic), Bedrock Invoke (Anthropic) — with no OpenAI, Gemini, or Vertex AI row
- **Evidence**: The "Supported Providers" table contains exactly four rows, each
  an Anthropic-model backend; the word "vertex" does not appear anywhere on the
  page. The table is the entire coverage statement for the feature.
- **Confidence**: settled (explicit documented table)
- **Quote**: "Anthropic ✅ Native support" / "Azure AI (Anthropic models) ✅ Claude models on Azure AI" / "Bedrock (Converse Anthropic models) ✅ Claude models via Bedrock Converse API" / "Bedrock (Invoke Anthropic models) ✅ Claude models via Bedrock Invoke API"
- **Our assessment**: This is the load-bearing claim for the guide and the
  direct answer to the Prospector's key question. The parent page (#1382) sells
  `/v1/messages` as "all LiteLLM supported providers"; a request body that fans
  out fine for `messages` does **not** carry the same guarantee for
  `output_format`. The "capability coverage is per-feature, not endpoint-wide"
  pattern is exactly the silent-narrowing class Ch05/Ch06 care about — the same
  shape as the guardrail non-streaming carve-out on the parent page. Operators
  must consult the per-feature matrix, not the endpoint feature matrix, before
  routing structured-output traffic; "OpenAI/Gemini/Vertex are absent" is
  recorded as the documented boundary, not inferred as "unsupported" (the page
  has no ❌ cells; the OpenAI/Azure translated path is documented in #1390).

### Claim 2: The Anthropic-shaped field name is `output_format` (not OpenAI's `response_format`), shaped `{"type": "json_schema", "schema": {...}}`, with `type` Must be `"json_schema"`
- **Evidence**: The "Request Format" section: "The `output_format` parameter
  specifies the structured output format." followed by the field reference, in
  which `type` is "Must be `"json_schema"`" and `schema` is "A JSON Schema
  object defining the expected output structure".
- **Confidence**: settled (explicit field contract)
- **Quote**: "The `output_format` parameter specifies the structured output format." / "**type** (string): Must be `\"json_schema\"`" / "**schema** (object): A JSON Schema object defining the expected output structure"
- **Our assessment**: A concrete migration hazard for anyone porting an
  OpenAI-shaped caller onto `/v1/messages`: the parameter is renamed
  (`response_format` → `output_format`) and its value shape differs (OpenAI
  nests the schema under `json_schema.schema` with name/strict keys; here the
  schema sits directly under `schema` and there is no `strict` flag documented
  on this page). Closing that last point across surfaces: #1390's mapping row
  records the proxy also accepting an `output_config.format` alias for
  `output_format` and wrapping the translated result with a `strict` value
  "copied from the request's `strict` flag and defaults to `false`"
  (Concrete Artifacts → "Top-level parameter mapping, request direction", line
  288). So a request-level `strict` flag is part of the proxy's Anthropic-shaped
  translation input on that path, even though *this* page never documents one —
  which is why the alias and the `strict` default are recorded here as a
  cross-surface observation from #1390, not as documented behaviour of the
  native `output_format` parameter (it remains unverified whether the native
  path honours the same flag). This is the same family of forward-shape
  translation the corpus records for `tool_choice` in
  `blog-litellm-auto-router-v2.md` (Claim 10), but here it is the
  *client-facing* contract — a caller that assumes OpenAI's shape gets a
  param-name error or a silent no-op rather than a translation.

### Claim 3: `additionalProperties: false` is documented as enforcing "strict schema adherence" — the vendor's strength claim for the control; the page gives no statement on what happens on schema violation or whether enforcement is provider-side or proxy-side
- **Evidence**: The `output_format.schema` field reference lists
  `additionalProperties` "(boolean): Set to `false` to enforce strict schema
  adherence". No other sentence on the page describes enforcement mechanics,
  violation behavior, or refusal paths.
- **Confidence**: emerging (settled as a documented instruction; the
  enforcement semantics are documented absence)
- **Quote**: "**additionalProperties** (boolean): Set to `false` to enforce strict schema adherence"
- **Our assessment**: The vendor's strength claim for the control is the exact
  phrase recorded. What is **not** documented is everything an operator needs to
  depend on it as a contract: where strictness is enforced (the provider's API
  vs the gateway's validation), what the client receives on violation, and
  whether all four backends enforce identically. Per the Prospector's
  "documented shape only, not verified behaviour" instruction, this claim stays
  at "the page asks the operator to set `additionalProperties: false` for strict
  adherence," not "strict adherence is guaranteed."

### Claim 4: The structured payload arrives as a stringified JSON blob inside `content[0].text` with `stop_reason: "end_turn"` — no distinct structured-output stop reason, content type, or schema-violation signal is documented
- **Evidence**: The "Example Response" shows
  `"content": [{"type": "text", "text": "{\"name\":\"John Smith\",\"email\":\"john@example.com\",\"plan_interest\":\"Enterprise\",\"demo_requested\":true}"}]`
  with `"stop_reason": "end_turn"` and a normal `usage` block — no
  structured/native JSON content type, no tool-use stop, no validation flag.
- **Confidence**: settled (documented example payload shape); the
  "no schema-violation signal" reading is documented absence
- **Quote**: "content" / "{\"name\":\"John Smith\",\"email\":\"john@example.com\",\"plan_interest\":\"Enterprise\",\"demo_requested\":true}" / "stop_reason" / "end_turn"
- **Our assessment**: The operational punchline. The gateway returns a **200
  with an unvalidated string**; the schema constraint is not, on this evidence,
  a validated contract at the client boundary. A caller that mis-parses the text
  block, or that treats `stop_reason` as a schema-success signal, gets no error
  to alert on — malformed structured output is neither a 5xx nor a distinct
  `stop_reason`, so it will not appear in gateway error metrics (Ch02) and an
  agent layer that trusts `output_format` without its own parse+validate step
  can silently consume bad rows (Ch03). This mirrors `docs-datadog-llm-
  observability`'s span model, where a span records an error only when the
  library tags one; a schema-violating but 200 response is invisible to that
  layer too.

### Claim 5: The Bedrock rows split into two distinct service names — Converse API (`bedrock/global.anthropic.claude-sonnet-5`) vs Invoke API (`bedrock/invoke/global.anthropic.claude-sonnet-5`) — the concrete config indirection for the two Bedrock paths
- **Evidence**: The Bedrock (Converse) tab configures
  `model: bedrock/global.anthropic.claude-sonnet-5`; the Bedrock (Invoke) tab
  configures `model: bedrock/invoke/global.anthropic.claude-sonnet-5` — both
  otherwise identical (env-key AWS auth, `us-west-2`).
- **Confidence**: settled (verbatim config values)
- **Quote**: "model: bedrock/global.anthropic.claude-sonnet-5" / "model: bedrock/invoke/global.anthropic.claude-sonnet-5"
- **Our assessment**: The support table's two "Bedrock" rows are two distinct
  LiteLLM provider prefixes with different plumbing. For the Ch05 fallback
  question this sharpens the surface: the four backends are not four
  interchangeable Claude executions — a fallback chain that crosses Invoke ↕
  Converse (or ↕ Azure AI, ↕ Anthropic native) changes provider path, and the
  page documents no guarantee that `output_format` schema strictness survives
  the switch. Worth recording verbatim as the config indirection, and the guide
  should treat each Bedrock row as its own backend, not a single entry.

### Claim 6: The proxy-side curls authenticate `/v1/messages` with `Authorization: Bearer $LITELLM_API_KEY` plus `anthropic-version: 2023-06-01` — a Bearer-token header style that diverges from the parent page's `x-api-key` curl example
- **Evidence**: All four "Test it!" curl examples send
  `-H "Authorization: Bearer $LITELLM_API_KEY" -H "anthropic-version: 2023-06-01"`;
  the parent page's curl used `-H "x-api-key: $LITELLM_API_KEY"` (see
  `docs-litellm-anthropic-unified.md`, Concrete Artifacts).
- **Confidence**: settled (verbatim headers on both pages)
- **Quote**: "-H \"Authorization: Bearer $LITELLM_API_KEY\" \\" / "-H \"anthropic-version: 2023-06-01\" \\"
- **Our assessment**: Minor but real: the same endpoint is documented with two
  different bearer styles across sibling pages of the same docs family. Both are
  presumably accepted server-side (the parent's SDK example also passes the key
  via `base_url`+`api_key`), but the divergence is exactly the kind of detail an
  operator copies into a runbook. Do not assert one is invalid; record the
  divergence and let gateway auth reference material resolve which headers the
  proxy actually accepts.

### Claim 7: The page documents no streaming behavior for `output_format` and carries none of the parent page's observed feature rows (cost tracking, logging, fallbacks, load balancing, guardrails) — recorded as explicit absence, not inferred either direction
- **Evidence**: The page's sections are Supported Providers, Usage, Example
  Response, Request Format — nothing on streaming, cost, logging, fallbacks, or
  guardrails. The parent page's feature matrix (shown in
  `docs-litellm-anthropic-unified.md` Concrete Artifacts) covers those features
  for the endpoint generally; this child page does not restate any of them for
  the structured-output feature.
- **Confidence**: emerging (documented absence; the page is silent, so no
  behavior is asserted)
- **Quote**: (no direct quote — the absence is in what the page does not
  contain; see the four section headings under Usage)
- **Our assessment**: Two load-bearing gaps. First, **streaming**: the parent
  page claims Streaming ✅ for `/v1/messages` while carving guardrails to
  non-streaming only; the structured-output page says nothing about whether
  `output_format` works in a stream or how the stringified JSON arrives across
  SSE chunks. Second, **fallbacks**: the parent claim "Fallbacks ✅ Works between
  supported models" does not cover the `output_format` feature — the four
  Anthropic-family backends here are exactly the "supported models" for this
  feature, but the page does not state that a fallback between them preserves
  schema strictness. Both stay un-inferred: recorded as documentation holes the
  Smith should flag, not as failures.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/anthropic_unified/structured_output (verified against rendered HTML).

### Supported Providers table (verbatim)

| Provider | Supported | Notes |
|---|---|---|
| Anthropic | ✅ | Native support |
| Azure AI (Anthropic models) | ✅ | Claude models on Azure AI |
| Bedrock (Converse Anthropic models) | ✅ | Claude models via Bedrock Converse API |
| Bedrock (Invoke Anthropic models) | ✅ | Claude models via Bedrock Invoke API |

### Example response (verbatim)

```json
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "{\"name\":\"John Smith\",\"email\":\"john@example.com\",\"plan_interest\":\"Enterprise\",\"demo_requested\":true}"
    }
  ],
  "model": "claude-sonnet-5",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 75,
    "output_tokens": 28
  }
}
```

### Request format — `output_format` (verbatim)

```
{
  "output_format": {
    "type": "json_schema",
    "schema": {
      "type": "object",
      "properties": {
        "field_name": {"type": "string"},
        "another_field": {"type": "integer"}
      },
      "required": ["field_name", "another_field"],
      "additionalProperties": false
    }
  }
}
```

### Config + curl shape (Anthropic tab, verbatim)

```yaml
model_list:
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-5
      api_key: os.environ/ANTHROPIC_API_KEY
```

```bash
curl http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-sonnet",
    "max_tokens": 1024,
    "messages": [{ "role": "user", "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm." }],
    "output_format": {
      "type": "json_schema",
      "schema": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "email": {"type": "string"},
          "plan_interest": {"type": "string"},
          "demo_requested": {"type": "boolean"}
        },
        "required": ["name", "email", "plan_interest", "demo_requested"],
        "additionalProperties": false
      }
    }
  }'
```

The other three tabs differ only in the `litellm_params.model` value and the
body `model` name: `model: azure_ai/claude-sonnet-5` (`azure-claude-sonnet`),
`model: bedrock/global.anthropic.claude-sonnet-5` (`bedrock-claude-sonnet`),
`model: bedrock/invoke/global.anthropic.claude-sonnet-5`
(`bedrock-claude-invoke`); the request body and headers are identical.

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/blog-litellm-auto-router-v2.md` — **cited** (Claim 10: the
  `/v1/messages`→Responses `tool_choice` shape bug is the precedent that
  translation between API surfaces is lossy/breaking; Claim 3 here's
  parameter-name divergence is the same family on the request side).
- `source-notes/blog-litellm-claude-fable-5-day-0.md` — **cited** (Claim 12:
  "structured output, all available across Anthropic, Azure, **Vertex AI**, and
  Bedrock" — a *model-parity* claim on the OpenAI-compatible surface; this
  page's table is the *unified-endpoint* `output_format` matrix with no Vertex
  row. Different surfaces — see Source Context, contradiction scan item 2: not
  filed, recorded as an open cross-check).
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **cited**
  (Concrete Artifacts → "Top-level parameter mapping, request direction"
  table: `output_format` or `output_config.format` → `text`, "Wrapped as
  `{"format": {"type": "json_schema", "name": "structured_output", "schema":
  ..., "strict": ...}}`" — the OpenAI/Azure translated path, including the
  `output_config.format` alias and the request-level `strict` handling, that
  this page's 4-row native table does not mention).
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session budget/iteration caps; no `/v1/messages` or output-format content.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: A2A
  per-agent cost ledger; different routing surface.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization/measurement; no endpoint contract.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  Langfuse app-layer guardrail scanners; no `output_format`/gateway path content.
- `source-notes/docs-litellm-generic-guardrail-api.md` — **cited** (Claim 2:
  `/v1/messages` is a guardrail-intercepted endpoint — the control-coverage
  surface this page's `output_format` feature rides on; Claim 5-adjacent
  "enforcement surface is narrower than interception" framing applies to the
  structured-output table too).
- `source-notes/blog-litellm-save-claude-code-costs.md` — **cited** (Claim 2:
  budget fallback chains silently reroute requests — the fallback mechanism that
  Claim 7 here shows is unqualified for `output_format`; a budget-driven silent
  reroute between Anthropic-family backends is exactly the surface with no
  documented schema-strictness guarantee).
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: Langfuse docs MCP
  server; unrelated.

Wider corpus (beyond the candidate list, per the Prospector's overlap list):

- **Corroborates**:
  - `source-notes/docs-litellm-anthropic-unified.md` (#1382, the parent
    overview note) — same endpoint family. Its **Claim 1** ("**All LiteLLM
    supported providers**") and **Claim 2** (feature matrix, with the assessment
    "surface support, not per-provider parity") are the universal-surface
    claims this page narrows per-feature; its **Claim 4** (guardrails
    "non-streaming only") is the prior instance of the documented-capability-
    boundary shape. Read together: Claim 1 here is the third instance of the
    "coverage is narrower than the advertisement" pattern on this endpoint.
  - `source-notes/docs-litellm-streaming-token-usage.md` — the closest
    structural analogue from the same `litellm-docs` crawl: a thin
    single-mechanism page whose ops value is a documented wire-level detail and
    a silent gap (streaming usage is opt-in). Claim 7 here's streaming hole is
    the same "what the page does not say is load-bearing" genre.
  - `source-notes/docs-litellm-a2a-agent-card.md` — methodological sibling: a
    per-field/per-backend support matrix with silent omissions
    (pushNotifications ❌ vs forwarded methods, its Claim 4). Claim 1 here is
    the same shape on the model path: the support table is the only coverage
    statement and omits names a reader might expect.
- **Contradicts**: **None — no contradiction issue filed.** Following the
  Prospector's explicit instruction, each apparent tension was checked and
  resolved as a different surface (endpoint-universality vs per-feature matrix
  vs model-parity claim vs translated path). See Source Context → contradiction
  scan for the itemized reasoning. Open contradiction issues #1150, #1307,
  #1322, #1338, #1352, #1408 and `CONTRADICTIONS.md` (no matching `C-NNN`)
  hold nothing on this surface.
- **Extends**:
  - `source-notes/docs-litellm-anthropic-unified.md` — adds the third
    capability-boundary data point (per-feature `output_format` matrix) to that
    note's guardrail carve-out, and answers its Claim 2 "surface support, not
    per-provider parity" with this page's concrete 4-row instantiation.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — this page's
    4-row native table + #1390's `output_format`→`text` translation row
    together give the full picture: Anthropic-family backends get the native
    `output_format`; OpenAI/Azure get the Responses-path `text.format`.
    `json_schema` wrapper (`strict` defaulting to `false`); Gemini/Vertex have
    neither on record.
  - `source-notes/docs-datadog-llm-observability.md` — its span model records
    an error only when the library tags one. Claim 3 defines the span as the
    unit of work ("A span is a unit of work representing an operation in your
    LLM application, and is the building block of a trace."); the attribute list
    that carries the error detail lives in Concrete Artifacts → Artifact 1
    (span attributes: "Error type/message/traceback", i.e. error detail is a
    span attribute set by instrumentation, not an automatic property of any
    failed request). A schema-violating but 200 structured-output response is
    invisible to observability layers built on that model — Claim 4 here is the
    concrete probe for the Ch02 argument that correctness signals need explicit
    instrumentation.
  - `source-notes/blog-litellm-save-claude-code-costs.md` + `source-notes/docs-litellm-generic-guardrail-api.md` — the fallback (Claim 2) and guardrail
    (Claim 2) mechanisms that operate on the model path; Claim 7 here documents
    the feature for which both are unqualified on this page.
- **Novel**: First corpus coverage of **structured output (`output_format`) on
  LiteLLM's `/v1/messages`**: the Anthropic-only native support boundary (four
  backends), the `output_format` field contract with
  `additionalProperties: false` as the documented strictness control, the
  stringified-JSON-in-`content[0].text` delivery shape, the Bedrock
  Converse/Invoke service split, the Bearer-vs-`x-api-key` header divergence
  between sibling pages, and the two explicit documentation absences (streaming,
  schema-violation behavior). Provenance of the novelty claim (re-verified this
  session): no existing note covers the native `output_format` surface; a
  corpus grep for `output_format`/`json_schema` returns zero hits across
  `guide/`, and the sole prior mention in `source-notes/` is #1390's single
  `output_format` → `text` mapping row (line 288), which records the
  OpenAI/Azure translated path rather than the native surface documented here.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), provider/feature matrices**: Add the
  "capability coverage is per-feature, not endpoint-wide" rule. On `/v1/messages`,
  `output_format` is documented for exactly four Anthropic-family backends
  (Claim 1 [settled]) even though the endpoint itself is advertised across all
  LiteLLM providers (#1382 Claim 1). Recommend: before routing a structured-output
  workload, validate the **per-feature** support matrix (not the endpoint feature
  matrix), exactly as the guide already treats per-provider guardrail coverage.
- **Chapter 05, fallback semantics**: A fallback on `/v1/messages` that moves a
  request between the four Anthropic-family backends (Anthropic native, Azure
  AI, Bedrock Converse, Bedrock Invoke — distinct provider prefixes, Claim 5
  [settled]) has **no documented schema-strictness guarantee**; the page says
  nothing about `output_format` across fallbacks (Claim 7 [emerging]). Call out
  that a fallback preserves availability while potentially degrading output
  guarantees — the Ch05 concern the Prospector flagged — and that the parent
  page's "Fallbacks ✅ Works between supported models" does not extend to this
  feature. Also note `literature`'s silent budget-fallback rerouting
  (save-claude-code-costs Claim 2) as a mechanism that can trigger such a switch
  without a request-level signal.
- **Chapter 03 (Runbooks and Agents)**: Callers consuming `/v1/messages`
  structured output must treat `content[0].text` as a JSON **string to be parsed
  and schema-validated at the client**; `stop_reason: "end_turn"` is not a
  schema-success signal and there is no structured content type (Claim 4
  [settled]). Agent loops that trust `output_format` without a parse+validate
  step can silently consume malformed rows.
- **Chapter 02 (Observability)**: Malformed/schema-violating structured output
  is a **200 with an unvalidated string** — it is not a 5xx and has no distinct
  `stop_reason`, so it will not surface in gateway error metrics; per-page it is
  also invisible to span-based observability (docs-datadog Claim 3). Instrument
  parse-success/schema-adherence as a first-class metric and alert on it,
  mirroring the streaming-usage "silent gap needs explicit instrumentation"
  lesson (docs-litellm-streaming-token-usage Claim 1).
- **Chapter 06 (Security and Trust)**: `additionalProperties: false` is the
  documented control for "strict schema adherence" (Claim 3 [emerging]) but the
  page does not state where strictness is enforced (provider vs proxy) or what a
  violation yields — record as an **open verification item**, not a guarantee;
  treat it as an output-validation control of documented shape only until
  verified. Open sub-question worth flagging alongside it, since the two knobs
  are easy to conflate: this page documents `additionalProperties: false`
  (a **schema-level** control) and does not document any request-level `strict`
  flag, while #1390 records the proxy copying a request-level `strict` on the
  translated path that **defaults to `false`** (its mapping-row note: schemas
  with optional properties pass through unless the caller opts in). Whether the
  native `output_format` path has an equivalent request-level strictness switch,
  and whether `additionalProperties: false` alone is sufficient there, is
  unverified — do not present either knob as a guarantee.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/anthropic_unified/structured_output`, HTTP
  200, no paywall), then quotes and code blocks verified against a direct raw-HTML
  fetch of the same URL. The page body is ~6k chars; all four provider tabs and
  both code sections were read, not just the first.
- No sub-pages followed: the only outbound links are nav siblings (the overview
  `/#1382`, `messages_to_responses_mapping #1390`, `native_passthrough`), whose
  scope the Prospector reserved for their own issues. The parent note (#1382)
  was read in full in its merged form since the two pages are the
  overview/child pair, and #1390 was read in full for its `output_format`
  translation row.
- All `Quote` fields are contiguous verbatim fragments from the fetched page
  prose or code blocks; no splicing across non-adjacent sentences. JSON/quoted
  fragments with inner quotes are reproduced with the escaping as rendered.
- **Contradiction handling (MINER §4a/§4b)**: no contradiction issue filed. The
  Prospector's triage explicitly instructed checking (1) whether this page's
  4-row table opposes #1382's universality claim and (2) whether it opposes
  Fable-5 Claim 12's Vertex AI mention. Both resolved as different surface
  dimensions (endpoint vs per-feature claim; model-parity claim vs endpoint
  support table) — per the instruction, "say so and drop it." See Source Context
  for the itemized reasoning. Each cited claim (parent #1382 Claims 1/2/4,
  Fable-5 Claim 12, mapping note Concrete Artifacts row, auto-router Claim 10,
  guardrail-api Claim 2, save-claude-code-costs Claim 2, a2a-agent-card Claim 4,
  datadog Claim 3, streaming-token-usage Claim 1) was re-read in the cited note
  before writing; no claim numbers invented, non-numbered sections cited by name.
- **Open cross-check recorded, not resolved**: Fable-5's model-level "structured
  output across Vertex AI" vs this page's Anthropic-only matrix — different
  surfaces, so not a contradiction, but the discrepancy is a live question for
  the guide (which surface should a Vertex-structured-output caller use?). Left
  open for the Smith, per the Prospector.
- **Fallback-strictness question left open**: the Prospector asked the Miner to
  interrogate whether a fallback between the four backends preserves the
  structured-output contract. The page is silent (Claim 7); the Miner did not
  fit the LiteLLM codebase (no network access to the repo from this runner), so
  it is recorded as a documentation absence and a verification item, not
  asserted.
- `confidence_overall` set to `emerging`: the parameter contract, the support
  table, the response shape, and the config values are settled first-party
  documentation, but the page is undated living docs, the ✅ cells are vendor
  assertions with no adherence evidence, the enforcement and failure semantics
  are documented absences, and the guide-value claims (per-feature narrowing,
  silent-unvalidated-string) are the Miner's synthesis from that surface.
  Matches the `emerging` ratings on the sibling LiteLLM docs notes (#1286,
  #1359, #1381, #1382, #1390).
- `date_published` unknown (undated living docs page); `date_extracted` and
  `last_checked` both 2026-09-22 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain.
