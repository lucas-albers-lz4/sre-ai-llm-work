---
source_url: https://docs.litellm.ai/docs/interactions
source_type: docs
title: "/interactions — LiteLLM AI Gateway Documentation (unified Interactions endpoint with a `/responses` bridge)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-22)
date_extracted: 2026-10-22
last_checked: 2026-10-22
status: current
confidence_overall: emerging
issue: "#1839"
---

# /interactions — the unified Interactions endpoint and its `/responses` bridge (LiteLLM Docs)

> LiteLLM exposes `/v1beta/interactions` as a **provider-agnostic** unified
> endpoint: only Google AI Studio is served natively, and *every other*
> chat-completion provider (`openai`, `anthropic`, `bedrock`, `vertex_ai`,
> `gemini`, `azure`, `azure_ai`, …) is reached by **translating the Interactions
> request into LiteLLM's own `/responses` endpoint** — so an Interactions client
> silently inherits the `/responses` translation hazards and the `/responses`
> usage/state shape, and multi-turn state is an opaque, gateway/provider-held
> `previous_interaction_id` that the page documents as a *request field* but never
> says where it is stored or what happens to it on failover.

## Source Context

- **Type**: docs (single-page LiteLLM gateway endpoint reference under
  `/docs/interactions`, listed in the "Reference → Supported Endpoints" nav).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented endpoint surface* — route shapes, request
  parameters, the response envelope, and the explicit "bridge" statement. It is
  **thin**: no publication date, no version anchor, no latency/overhead numbers,
  no failure modes, and no per-provider parity matrix. The page does not name the
  implementing file, unlike the sibling `/v1/messages`→`/responses` mapping page
  ([docs-litellm-messages-to-responses-mapping](#cross-references)).
- **Scope**: The Interactions endpoint (`POST /v1beta/interactions`,
  `GET /v1beta/interactions/{interaction_id}`), the Python SDK entry points
  `litellm.interactions.create` / `acreate`, the request/response schema, the
  `/interactions` → `/responses` bridge, and a two-row provider table. Does
  **not** cover: streaming wire format, the bridge's field-level drop behavior,
  where `previous_interaction_id` state lives, guardrail coverage, spend/cost
  config, or fallbacks.
- **Triage framing** (issue #1839, three Prospector comments): extract the
  endpoint surface, the bridge architecture, the usage-field shape, the
  `previous_interaction_id` statefulness question, and the Google GenAI SDK
  `http_options.base_url` redirection; treat the bridge and usage-shape claims as
  *documented-but-unverified*; do **not** credit the feature-checklist rows as
  validated capability (the Fallbacks/Loadbalancing qualifier "between supported
  models" applies).
- **Redundancy**: no existing note covers this endpoint. It generalizes the
  managed-agent Interactions usage in
  [blog-litellm-google-ai-studio-managed-agents](#cross-references) (where
  `/v1beta/interactions` routes to an **agent**, not a model) to the generic
  *model*-facing API documented here.

## Extracted Claims

### Claim 1: `/v1beta/interactions` is documented as a provider-agnostic unified endpoint — its "Supported LLM providers" is "All LiteLLM supported CHAT COMPLETION providers," naming `openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`, `azure_ai` etc.
- **Evidence**: The page's "Supported LLM providers" call-out names the whole chat-completion provider set ("All LiteLLM supported CHAT COMPLETION providers"), not just Gemini.
- **Confidence**: settled (explicit documented provider list)
- **Quote**: "**All LiteLLM supported CHAT COMPLETION providers**" / "`openai`, `anthropic`, `bedrock`, `vertex_ai`, `gemini`, `azure`, `azure_ai` etc."
- **Our assessment**: This is the load-bearing breadth claim, and it is broader than the endpoint's *native* scope. Only Google AI Studio serves the Interactions API natively (Claim 4); the rest are the bridge. The phrase "CHAT COMPLETION providers" is itself a scope-narrowing qualifier the page states but does not explain — it implies non-chat providers (embeddings, rerank) are out. Read the breadth as "reachable via bridge," not "native."

### Claim 2: The endpoint surface is `POST /v1beta/interactions` (create; `stream: true` for streaming) and `GET /v1beta/interactions/{interaction_id}` (retrieve), with `litellm.interactions.create` / `litellm.interactions.acreate` in the Python SDK
- **Evidence**: The proxy curl examples hit `POST /v1beta/interactions` and `GET /v1beta/interactions/{interaction_id}`; the SDK examples call `litellm.interactions.create(...)` and `await litellm.interactions.acreate(...)`; the streaming curl uses `curl -N -X POST "http://localhost:4000/v1beta/interactions"` with `"stream": true`.
- **Confidence**: settled (explicit routes and SDK calls)
- **Quote**: "curl -X POST \"http://localhost:4000/v1beta/interactions\"" / "curl \"http://localhost:4000/v1beta/interactions/{interaction_id}\""
- **Our assessment**: The route is versioned `/v1beta/...`, the same prefix as the managed-agents endpoint (`/v1beta/agents`) in the sibling blog note — consistent with a beta surface. The retrieve route keys on an opaque `interaction_id`, so the same "state lives somewhere addressable by ID" property applies as for `/responses` (Claim 7).

### Claim 3: The request parameters are exactly `model`, `input`, `stream`, `tools`, `system_instruction`, `generation_config`, and `previous_interaction_id` — with `model` and `input` the only required fields, and `previous_interaction_id` documented only as "ID of previous interaction for context"
- **Evidence**: The "Request Parameters" table lists the seven parameters and their required flags.
- **Confidence**: settled (explicit table)
- **Quote**: "`previous_interaction_id` | string | No | ID of previous interaction for context"
- **Our assessment**: Two operators' notes. (1) `previous_interaction_id` is the *only* documented multi-turn mechanism, and its one-line description — "for context" — does not say whether context is replayed from gateway memory or resolved provider-side. That is the operational black box flagged in the triage (Claim 8). (2) The parameter set is small and Interactions-shaped (`input`, `system_instruction`, `generation_config`), which is precisely the shape a bridge must map onto `/responses` form — the surface where silent narrowing would occur (Claim 5).

### Claim 4: Google AI Studio is served natively; a two-row "Supported Providers" table sends "Google AI Studio" to the native quick-start and "All other LiteLLM providers" to the bridge usage — so every non-Google provider is documented as bridge-served
- **Evidence**: The closing "Supported Providers" table, two rows, with the second row's link anchor `#calling-non-interactions-api-endpoints-interactions-to-responses-bridge`.
- **Confidence**: settled (explicit two-row routing table)
- **Quote**: "All other LiteLLM providers" / "Bridge Usage"
- **Our assessment**: This is the page's own statement that only one provider has a native path and everything else is translation. It directly qualifies Claim 1's breadth: "supported" for non-Google providers means "bridged." Contrast with `/generateContent` (docs-litellm-generate-content), which is a single-provider Google-native passthrough with no fan-out — `/interactions` is the fan-out endpoint whose native leg is Google and whose other legs are translations.

### Claim 5: For "OpenAI, Anthropic, and other providers that don't natively support the Interactions API," LiteLLM "call[s]" them "via a bridge to LiteLLM's `/responses` endpoint" — a gateway translation layer, not a native passthrough
- **Evidence**: The section heading "Calling non-Interactions API endpoints (`/interactions` to `/responses` Bridge)" and its intro sentence; the worked non-streaming SDK example calls `model="gpt-6.1-sol"` through `litellm.interactions.create`.
- **Confidence**: settled (explicit architectural statement)
- **Quote**: "LiteLLM allows you to call non-Interactions API models via a bridge to LiteLLM's `/responses` endpoint. This is useful for calling OpenAI, Anthropic, and other providers that don't natively support the Interactions API."
- **Our assessment**: The core architectural finding. "Bridge to `/responses`" means the Interactions request is translated into a `/responses` request, and the `/responses` response is translated back into an Interactions envelope. That is a *second* translation hop: the `/responses` endpoint itself may then bridge `/responses` → `/v1/chat/completions` for providers without a native Responses API (see docs-litellm-messages-to-responses-mapping / the `/responses` docs). The page does not document the bridge's field-level behavior, so any field the Interactions schema carries that `/responses` does not model is a candidate silent drop — documented-by-omission, not asserted. The Alice/`previous_interaction_id` state (Claim 3) must also survive this translation, and the page is silent on how.

### Claim 6: The response envelope is `id` / `object` ("interaction") / `model` / `status` ("completed") / `created` / `updated` / `role` ("model") / `outputs[]` (typed entries, e.g. `{"type": "text", "text": ...}`) / `usage` — an Interactions-shaped envelope, not the OpenAI Responses envelope
- **Evidence**: The worked "Response Format" JSON block.
- **Confidence**: settled (explicit example response)
- **Quote**: "{  \"id\": \"interaction_abc123\",  \"object\": \"interaction\",  \"model\": \"gemini-3.8-flash\",  \"status\": \"completed\", ..."
- **Our assessment**: The envelope differs from both the OpenAI chat-completions envelope and the `/responses` envelope documented in docs-litellm-messages-to-responses-mapping (which returns Responses-API-shaped output). A client written to the Interactions envelope (`outputs[-1].text`, per the quick-start example `print(response.outputs[-1].text)`) depends on LiteLLM synthesizing that shape back from the `/responses` response on the bridge — a third transform in the chain. No drop is documented; the absence of a mapping spec is the risk.

### Claim 7: The `usage` object in the response is `total_input_tokens` / `total_output_tokens` / `total_tokens` — a different field vocabulary from the OpenAI-style `prompt_tokens` / `completion_tokens`, and also different from the `/responses` `input_tokens` / `output_tokens`
- **Evidence**: The response example's `usage` block.
- **Confidence**: settled (explicit example) — but see assessment, which is emerging on the "is this the wire shape actually emitted" question
- **Quote**: "\"usage\": {    \"total_input_tokens\": 10,    \"total_output_tokens\": 15,    \"total_tokens\": 25  }"
- **Our assessment**: The triage's Ch02 question. If this is the wire shape, any cost/token parser that reads `prompt_tokens`/`completion_tokens` (the OpenAI chat shape) or `input_tokens`/`output_tokens` (the `/responses` shape) will read nothing from an Interactions response. It is `settled` that the *example* uses this vocabulary; it is `emerging` that the proxy emits it for all providers, because the page shows a single Gemini-native example and does not show the bridged response body. Flag for verification against a live proxy, not asserted as emitted wire shape (per triage).

### Claim 8: The Google GenAI SDK is pointed at the LiteLLM proxy via `genai.Client(api_key=..., http_options={"base_url": "http://localhost:4000"})`, then calls `client.interactions.create(...)` / `create_stream(...)` — a different redirection mechanism from the env-var approach documented for `/generateContent`
- **Evidence**: The "Point the Google GenAI SDK to LiteLLM Proxy" code block sets `http_options={"base_url": "http://localhost:4000"}` and uses `client.interactions.create` and `client.interactions.create_stream`.
- **Confidence**: settled (explicit code)
- **Quote**: "client = genai.Client(    api_key=\"sk-<your-litellm-api-key>\",  # Your LiteLLM API key    http_options={\"base_url\": \"http://localhost:4000\"},)"
- **Our assessment**: An operator-facing migration knob distinct from the `GOOGLE_GEMINI_BASE_URL` env var in docs-litellm-generate-content (Claim 8). Here the base URL is a *client-construction* argument. The SDK also exposes streaming via a separate method name (`create_stream`), while the proxy uses a `stream: true` body field — two different streaming interfaces for the same backend capability.

### Claim 9: The feature checklist claims Logging ("Works across all integrations"), Streaming, and Loadbalancing (qualified "Between supported models") — but the page documents no per-provider parity and does not state that these hold on the bridged path specifically
- **Evidence**: The opening feature table's three rows and notes.
- **Confidence**: emerging (vendor surface claim; no validation detail, no per-provider matrix)
- **Quote**: "Logging" / "✅" / "Works across all integrations" / "Between supported models"
- **Our assessment**: Per triage, do not credit these as validated. "Between supported models" is the same qualifier docs-litellm-generate-content Claim 6 records for Fallbacks/Loadbalancing. Since non-Google providers are bridge-served, the checklist's claims are least verified exactly where they matter most (the bridged leg). Record as a vendor claim and verify per provider/leg.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/interactions.

### Feature table (verbatim)

| Feature | Supported | Notes |
|---|---|---|
| Logging | ✅ | Works across all integrations |
| Streaming | ✅ | |
| Loadbalancing | ✅ | Between supported models |

### Native Gemini quick-start — Python SDK (verbatim)

```python
import litellm
import os
os.environ["GEMINI_API_KEY"] = "your-api-key"

response = litellm.interactions.create(
    model="gemini/gemini-3.8-flash",
    input="Tell me a short joke about programming."
)
print(response.outputs[-1].text)
```

### Proxy config (verbatim)

```yaml
model_list:
  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-3.8-flash
      api_key: os.environ/GEMINI_API_KEY
```

### Proxy create + retrieve (verbatim)

```bash
curl -X POST "http://localhost:4000/v1beta/interactions" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini/gemini-3.8-flash",
    "input": "Tell me a short joke about programming."
  }'

curl "http://localhost:4000/v1beta/interactions/{interaction_id}" \
  -H "Authorization: Bearer $LITELLM_API_KEY"
```

### Google GenAI SDK redirection (verbatim)

```python
from google import genai

# Point SDK to LiteLLM Proxy
client = genai.Client(
    api_key="sk-<your-litellm-api-key>",  # Your LiteLLM API key
    http_options={"base_url": "http://localhost:4000"},
)

# Create an interaction
interaction = client.interactions.create(
    model="gemini/gemini-3.8-flash",
    input="Tell me a short joke about programming."
)
print(interaction.outputs[-1].text)
```

### Response format (verbatim)

```json
{
  "id": "interaction_abc123",
  "object": "interaction",
  "model": "gemini-3.8-flash",
  "status": "completed",
  "created": "2025-01-15T10:30:00Z",
  "updated": "2025-01-15T10:30:05Z",
  "role": "model",
  "outputs": [
    {
      "type": "text",
      "text": "Why do programmers prefer dark mode? Because light attracts bugs!"
    }
  ],
  "usage": {
    "total_input_tokens": 10,
    "total_output_tokens": 15,
    "total_tokens": 25
  }
}
```

### Bridge usage — non-Interactions provider via SDK (verbatim)

```python
import litellm
import os

# Set API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Non-streaming interaction
response = litellm.interactions.create(
    model="gpt-6.1-sol",
    input="Tell me a short joke about programming."
)
print(response.outputs[-1].text)
```

### Supported providers table (verbatim)

| Provider | Link to Usage |
|---|---|
| Google AI Studio | [Usage](#quick-start) |
| All other LiteLLM providers | [Bridge Usage](#calling-non-interactions-api-endpoints-interactions-to-responses-bridge) |

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; each of the 10
listed paths is addressed):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch input-file
  rate limiting on `POST /v1/batches`; no overlap with the Interactions
  request/response contract.
- `source-notes/docs-litellm-completion-web-search.md` — **Dismissed**:
  provider web-search feature boundary across chat/responses/image; the
  Interactions page names `tools` but documents no web-search semantics.
- `source-notes/docs-litellm-evals-api.md` — **Dismissed**: OpenAI Evaluations
  API served by the proxy; unrelated surface.
- `source-notes/docs-litellm-generate-content.md` — **Cited** (Extends /
  Contradicts-adjacent, see below): the sibling Google-native passthrough route
  and the SDK-redirection contrast (its Claim 8 `GOOGLE_GEMINI_BASE_URL` vs
  Claim 8 here `http_options.base_url`).
- `source-notes/docs-litellm-enterprise.md` — **Dismissed**: license/feature
  tiering; no endpoint-contract overlap.
- `source-notes/docs-litellm-files-endpoints.md` — **Dismissed**: provider
  `/files` object lifecycle; different endpoint.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Cited** (Extends): the
  native Bedrock `/invoke` passthrough is a per-provider wire-format route; the
  Interactions page's bridge is the *opposite* design (one client format,
  fan-out to many providers by translation).
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  audio-transcription fallback/mode config; different route and concern.
- `source-notes/docs-litellm-completion-input-params.md` — **Cited** (Extends):
  the supported-params gate and the "any non-OpenAI param is assumed
  provider-specific" rule (Claim 3) is the generic mechanism behind a bridge's
  field handling; the Interactions page documents no such gate for its bridge.
- `source-notes/docs-litellm-creating-adapters.md` — **Dismissed as duplicate
  mechanism, noted**: adapters are a bidirectional format-translation layer, but
  they are registered process-globally via `litellm.adapters` and invoked with
  `adapter_completion`; the `/interactions`→`/responses` bridge is an internal
  route-to-route translation, not the user-facing adapter contract. No claim
  overlap beyond the shared "translate in, translate out" shape.

**Additional cross-references found by searching `source-notes/` and the issue
triage comments:**

- **Corroborates**:
  - `source-notes/blog-litellm-google-ai-studio-managed-agents.md` **Claim 5** —
    that note documents `/v1beta/interactions` as the *agent*-routed path
    (`agent` field, Gemini-only). This page documents the same endpoint's
    *model*-routed path (`model` field, all chat-completion providers). The two
    together show `/v1beta/interactions` has two routing dimensions on one
    route: `agent` (managed agents, Gemini-only) and `model` (models, native
    Gemini or bridge). Neither note states they coexist; both should be read as
    partial views of one endpoint.
  - `source-notes/docs-litellm-generate-content.md` **Claim 1 and Claim 10** —
    same Google-native-on-a-gateway pattern; the `/interactions` page's native
    leg for Google AI Studio is the Interactions analogue of the
    `/generateContent` passthrough.
  - `source-notes/docs-litellm-bedrock-invoke.md` **Claim 3** — that note
    records the Bedrock page's support matrix as "a vendor surface claim with no
    per-provider parity." The `/interactions` feature table (Claim 9 here) is
    the same kind of vendor surface claim, with the same missing per-provider
    matrix.
- **Contradicts**: None filed. The nearest candidate is
  `docs-litellm-generate-content.md` Claim 8's SDK-redirection *mechanism*
  (`GOOGLE_GEMINI_BASE_URL` for `generateContent` vs `http_options.base_url` for
  `/interactions`) — but these are two different endpoints using two documented
  SDK knobs, not opposing claims about one surface. Per MINER.md §4a, differing
  mechanisms on different routes are conditioning variables, not a
  contradiction. No contradiction issue filed. No existing open contradiction
  issue (checked the open `contradiction` list, e.g. #1408, #1591) covers the
  Interactions endpoint.
- **Extends**:
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` (entire note) —
    this is the **translation spec for the bridge's destination**. That note
    documents the `/v1/messages` → Responses translation on the OpenAI/Azure
    path (silent drops, `prompt_cache_key` derivation, `thinking`→`reasoning`
    quantization, structural tool hoisting, response-direction lossiness). The
    `/interactions` bridge lands on the same `/responses` endpoint, so any
    Interactions request field that `/responses` does not model is exposed to
    the same class of silent translation the mapping note catalogues. That note
    is the field-level detail this page lacks; this page is the *new ingress*
    onto that destination. Their combination is a guide-relevant warning: the
    mapping note's hazards now apply transitively to Interactions clients,
    **unless** LiteLLM's Interactions→Responses adapter differs — which this
    page does not document. Do not assert the hazards apply; flag them as the
    verification target.
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 1, Claim 2** — the
    `/v1/messages` unified endpoint is the corpus's prior fan-out precedent (one
    client format, many providers). `/interactions` is a second fan-out endpoint
    with different client-format and native-provider choices; the two are the
    fan-out family, and the Interactions page's "Supported LLM providers" breadth
    claim mirrors the unified page's broad matrix claim.
  - `source-notes/docs-litellm-generic-guardrail-api.md` **Claim 2** — the
    guardrail interception list names eight concrete endpoints plus a
    catch-all "Pass-through endpoints" bullet; `/v1beta/interactions` is neither
    named nor explicitly excluded. Same open coverage question as
    `/generateContent` had (see docs-litellm-generate-content Claim 5): whether
    a bridge-served Interactions request is guardrail-inspected is unstated.
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 9** and
    `docs-litellm-streaming-token-usage.md` **Claim 1/Claim 2** — usage-shape
    baseline. The Interactions `usage` vocabulary (Claim 7 here) is a *third*
    shape after `prompt_tokens`/`completion_tokens` and
    `input_tokens`/`output_tokens`. Any cost/log consumer must key on the route,
    not assume one vocabulary.
  - `source-notes/blog-litellm-google-ai-studio-managed-agents.md` **Claim 1 and
    Claim 7** — versioned, pass-through-proxy design for the same endpoint
    family; that note's out-of-band state-inconsistency warning (agent deleted
    provider-side, proxy unaware) is the analogous state-retention question for
    `previous_interaction_id` (Claim 8 here): if interaction state is held
    provider- or gateway-side, its lifecycle is not visible to the caller.
- **Novel**:
  - First corpus coverage of the **`/v1beta/interactions` unified endpoint** and
    its **`/interactions` → `/responses` bridge**. Nothing in `source-notes/` or
    `guide/` documents this route.
  - The **three-vocabulary usage shape** observation (`total_input_tokens` /
    `total_output_tokens` on Interactions vs `prompt_tokens`/`completion_tokens`
    on chat vs `input_tokens`/`output_tokens` on `/responses`) is new.
  - The **`previous_interaction_id` statefulness-as-request-field** framing
    (documented as a request param, silent on storage/failover) is new.
  - The **`http_options.base_url` SDK-redirection** mechanism for the Google
    GenAI SDK (distinct from the env-var mechanism on `/generateContent`) is new.

## Guide Impact

- **Chapter 05 — "Provider parity in the shared forwarding path"
  (guide/05-llm-ops-reliability.md:343)**: This source is a second fan-out
  endpoint (`/interactions`) whose non-native legs are served by *route-to-route
  translation* rather than a shared forwarding path. Add it as a distinct
  disposition: a unified client format served by bridging to an internal
  endpoint inherits the destination endpoint's translation hazards transitively
  (see docs-litellm-messages-to-responses-mapping) [Claim 5] [settled for the
  bridge's existence; field-level behavior emerging]. Recommends verifying the
  bridge's outbound request shape per provider, as the chapter already does for
  the shared forwarding path.
- **Chapter 05 — "Parameter migration hazards"
  (guide/05-llm-ops-reliability.md:327)**: Add that a bridge to `/responses`
  means an Interactions caller's parameters (`input`, `system_instruction`,
  `generation_config`, `tools`, `previous_interaction_id`) are re-expressed in
  another endpoint's vocabulary [Claim 3, Claim 5] [settled]; any field the
  destination does not model is a candidate silent drop (the destination page
  catalogues exactly such drops). Verify the outbound request, not just the 200.
- **Chapter 05 — "Silent model fallback breaks attribution"
  (guide/05-llm-ops-reliability.md:972)**: Add `/interactions` usage shape as an
  attribution caveat. The response `usage` uses `total_input_tokens` /
  `total_output_tokens` / `total_tokens` [Claim 7] [settled as the example
  shape], so a cost/log parser keyed on `prompt_tokens`/`completion_tokens`
  (chat) or `input_tokens`/`output_tokens` (`/responses`) reads zero here.
  Recommend route-keyed usage parsing and a reconciliation sample.
- **Chapter 05 — "Session-affine routing preserves provider-side prompt caches"
  (guide/05-llm-ops-reliability.md:1056)**: Add `previous_interaction_id` as an
  operational dependency on gateway- or provider-side state retention [Claim 3]
  [emerging]. The page documents the field but not where the state lives or what
  happens on failover/multi-instance deployments (the triage's key question).
  Recommend treating multi-turn Interactions sessions as stateful until the
  storage location is verified, mirroring how the chapter treats `/responses`
  `previous_response_id` affinity.
- **Chapter 02 (Observability)**: Add the third usage vocabulary (Claim 7) to
  the list of per-route token-field shapes; and note that the Interactions
  envelope (`outputs[]`, `id`/`object`/`status`) [Claim 6] is yet another
  response shape a mid-path inspector may see.
- **Chapter 06 (Security and Trust)**: One caution. `/v1beta/interactions` is a
  bridge-served route on the same undocumented "pass-through endpoint" boundary
  as `/generateContent` (docs-litellm-generate-content Claim 5 /
  docs-litellm-generic-guardrail-api Claim 2). The page documents no guardrail
  coverage for it. Recommend naming it as a route whose guardrail coverage must
  be confirmed per route, not assumed from "guardrails are configured."

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/interactions`, HTTP 200, no paywall). The page
  is short (one feature table, native + bridge usage snippets, request/response
  schema, a two-row provider table). The `/responses` destination was spot-read
  (`https://docs.litellm.ai/docs/response_api`, HTTP 200) to confirm the bridge
  destination's own usage/state shape (`input_tokens`/`output_tokens`, and
  `previous_response_id` with `store: True` multi-turn semantics) referenced in
  Claims 5-7. No further sub-pages followed; the sibling notes listed in the
  triage comments were read/verified instead.
- All `Quote` fields are character-for-character contiguous fragments from the
  fetched page prose, tables, or code blocks; no splicing across non-adjacent
  sentences. For code-block quotes I preserved the source's own characters
  (including the `\n`-joined single-line rendering WebFetch produced for curl
  snippets, hence the shorter route fragments quoted from code).
- **Contradiction check (MINER §4a)**: no contradiction issue filed. The only
  near-neighbour is the SDK-redirection mechanism difference vs
  docs-litellm-generate-content Claim 8 — different endpoints, different
  documented knobs, not opposing claims. Verified against the open
  `contradiction`-labeled issues (#1633, #1597, #1593, #1591, #1565, #1562,
  #1550, #1548, #1534, #1517, #1514, #1486, #1462, #1461, #1408, #1352, #1338,
  #1322, #1307, #1150) and `CONTRADICTIONS.md` (no `C-NNN` entries) — none cover
  `/interactions`.
- **Candidate file**: `miner-related-notes.md` (repo root) was read in full and
  not committed. All 10 listed candidates are cited or dismissed above.
- **Verification-open items recorded, not asserted** (per triage): (1) whether
  the Interactions→`/responses` bridge silently drops fields `/responses` does
  not model (Claim 5) — the page states the bridge but documents no field
  mapping, so this is documented-by-omission; (2) whether
  `usage.total_input_tokens`/`total_output_tokens` is the emitted wire shape on
  the bridged path (Claim 7) — the only example is Gemini-native; (3) where
  `previous_interaction_id` state is stored and its failover behavior (Claim 3);
  (4) whether `/v1beta/interactions` is guardrail-covered. None of these is
  promoted to a settled claim; all require proxy-source or live-proxy
  verification.
- Cross-reference verification (MINER §4b): re-read the cited claims in
  `docs-litellm-messages-to-responses-mapping.md` (Claims 1-11, particularly
  the translation tables), `docs-litellm-generate-content.md` (Claims 1, 5, 6,
  8, 10), `docs-litellm-anthropic-unified.md` (Claims 1, 2, 9),
  `docs-litellm-generic-guardrail-api.md` (Claim 2),
  `docs-litellm-bedrock-invoke.md` (Claims 1, 3),
  `blog-litellm-google-ai-studio-managed-agents.md` (Claims 1, 5, 7),
  `docs-litellm-streaming-token-usage.md` (Claims 1, 2), and
  `docs-litellm-completion-input-params.md` (Claim 3), and confirmed the
  numbered claims match their cited content. No claim numbers invented.
- `confidence_overall` set to `emerging`: the endpoint surface, provider breadth,
  bridge statement, request params, response envelope, and SDK redirection are
  settled first-party documentation of an API contract, but every
  operationally-interesting question (bridge field behavior, usage wire shape,
  state storage/lifecycle) is undocumented and unverified, matching the
  `emerging` rating on the sibling LiteLLM docs notes.
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain.
