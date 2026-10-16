---
source_url: https://docs.litellm.ai/docs/generateContent
source_type: docs
title: "/generateContent — LiteLLM AI Gateway Documentation (Google-native generateContent passthrough)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; front-matter `last_updated: 2026-10-15`)
date_extracted: 2026-10-16
last_checked: 2026-10-16
status: current
confidence_overall: emerging
issue: "#1736"
---

# /generateContent — Google-native generateContent passthrough (LiteLLM Docs)

> LiteLLM exposes Google's native `generateContent` endpoint as a per-model
> proxy route (`POST /v1beta/models/<alias>:generateContent`) whose contract is a
> deliberate **verbatim passthrough**: the top-level `GenerateContentRequest`
> siblings of `generationConfig` (`safetySettings`, `toolConfig`,
> `cachedContent`, `labels`) are forwarded to Google unmodified without
> `extra_body` wrapping, and an explicit `extra_body` value wins on conflict —
> the opposite direction from the gateway's OpenAI-param drop/strip gates.

## Source Context

- **Type**: docs (LiteLLM gateway documentation, `/docs/generateContent`).
- **Author credibility**: LiteLLM (BerriAI) official vendor documentation. The
  page is the authoritative statement of the gateway's own translation
  contract, but it is thin: no publication date, no version anchor, and no
  benchmarks, latency, rate-limit, or spend data. Front-matter
  `last_updated: "2026-10-15"`.
- **Scope**: How to call Google AI's `generateContent` endpoints through
  LiteLLM's Python SDK and proxy, the feature-support matrix for the native
  route, and the "Native request fields" passthrough/precedence rule. Does
  **not** cover: the streaming variant's native-field behavior, per-provider
  fallback/LB parity, spend/usage measurement detail, or the interaction with
  guardrails.
- **Triage framing** (issue #1736): scoped to the passthrough/precedence rule;
  the capability-checklist rows and Enterprise upsell are explicitly out of
  scope (do not extract marketing).

## Extracted Claims

### Claim 1: The page documents a Google-native `generateContent` route exposed alongside LiteLLM's OpenAI-compatible surface.
- **Evidence**: Front-matter `canonical_url` `/docs/generateContent`; the proxy curl route `POST /v1beta/models/gemini-flash:generateContent`; four Python SDK entry points (`generate_content`, `generate_content_stream`, `agenerate_content`, `agenerate_content_stream`).
- **Confidence**: settled
- **Quote**: "Use LiteLLM to call Google AI's generateContent endpoints for text generation, multimodal interactions, and streaming responses."
- **Our assessment**: Buy it. The route shape mirrors Google's Generative Language REST path (`/v1beta/models/{model}:generateContent`), and the page's whole structure is a per-endpoint reference for this native surface. This is the same class of provider-native passthrough as the Bedrock `/invoke` route (see Cross-References).

### Claim 2: The passthrough contract is explicit — top-level siblings of `generationConfig` are forwarded to Google verbatim without `extra_body`, and the named field set is exactly `safetySettings`, `toolConfig`, `cachedContent`, `labels`.
- **Evidence**: The "Native request fields" prose plus a worked curl and Python SDK example that pass `safetySettings` and `toolConfig` at the top level of the body.
- **Confidence**: settled
- **Quote**: "so the top-level fields that Google's `GenerateContentRequest` carries as siblings of `generationConfig` are forwarded to Google verbatim. This covers `safetySettings`, `toolConfig`, `cachedContent`, and `labels`." / "Send them at the top level of the request body exactly as you would when calling Google directly; there is no need to wrap them in `extra_body`."
- **Our assessment**: This is the operator finding the issue asked for. "Verbatim" is a strong, testable contract statement, but note the field set is a **named allowlist of four** — not a general "anything native passes through" guarantee. Treat fields outside the four as undocumented pending verification.

### Claim 3: Precedence rule — an explicit `extra_body` value overrides the top-level native field on conflict.
- **Evidence**: Direct statement in the "Native request fields" section.
- **Confidence**: settled
- **Quote**: "If you do pass `extra_body`, an explicit value there wins on conflict."
- **Our assessment**: Buy it, and flag the inversion: on most LiteLLM paths `extra_body` is where you tuck provider-native fields *because* they would otherwise be dropped; on this route the top-level form is already native and `extra_body` is the override channel. Operators carrying configs across routes can get the precedence backwards.

### Claim 4: The passthrough rule is documented for `generateContent` only — the `:streamGenerateContent` variant is shown without any native top-level fields, so streaming passthrough is undocumented.
- **Evidence**: The "Native request fields" heading and prose name `generateContent` exclusively (no mention of the stream route); the streaming curl example carries only `contents` and `generationConfig`. The `:streamGenerateContent` route exists in the usage section.
- **Confidence**: anecdotal (absence of documentation, not a stated limitation)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The issue's second question is answered by omission. Nothing on the page says streaming behaves differently, but nothing confirms parity either. An operator must test the stream route with `safetySettings`/`toolConfig`/`cachedContent`/`labels` before assuming the same verbatim contract — a documented gap, not a documented failure. This is an absence claim and should not be promoted to a hard "streaming drops fields" claim.

### Claim 5: Governance consequence — a client-supplied `safetySettings` block (including `threshold: BLOCK_NONE`) is delivered to Google as-is; the page documents no gateway-side normalization or re-application of safety policy on this route, and exists on a route where documented guardrail coverage is ambiguous.
- **Evidence**: The worked native-fields example passes `{"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}` at the top level, and by Claim 2 that body is forwarded verbatim. The page itself says nothing about guardrails on this route. The nearest coverage statement is `docs-litellm-generic-guardrail-api.md` Claim 2, whose interception list names eight endpoints (`/v1/chat/completions`, `/v1/completions`, `/v1/responses`, `/v1/images/generations`, `/v1/audio/transcriptions`, `/v1/audio/speech`, `/v1/messages`, `/v1/rerank`) **and then a catch-all "Pass-through endpoints" bullet** — so `/generateContent` is neither named nor explicitly excluded.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is our synthesis, not a page statement — the page never frames `safetySettings` as a governance control. The mechanism is still worth flagging: if the native route forwards safety settings verbatim, the provider safety policy (or its suppression) is a client-supplied request field. But the coverage question is **open, not answered** — the generic-guardrail note's "Pass-through endpoints" bullet could cover `/generateContent` or not, and neither page resolves it. Do not state that guardrails skip this route; state that documented guardrail coverage for the native route is unstated. Verify against proxy source before any guide advice.

### Claim 6: The feature-support matrix claims Cost Tracking, Logging (all integrations), End-user Tracking, Streaming, Fallbacks, Loadbalancing, and Metadata Tracking all ✅ on this route — but the Fallbacks and Loadbalancing rows are qualified "between supported models".
- **Evidence**: Overview feature table.
- **Confidence**: emerging
- **Quote**: "between supported models"
- **Our assessment**: Record the qualification, not just the checkmarks. "Between supported models" means fallback/LB on the native route is not universal — a native-route deployment may only interoperate with other deployments that expose the same native surface. The page gives no parity matrix, so the qualifier's actual boundary is unverified.

### Claim 7: Metadata Tracking is claimed on this route and is said to pass the trace ID and metadata to observability callbacks such as S3 and Langfuse.
- **Evidence**: Overview feature table, Metadata Tracking row.
- **Confidence**: emerging
- **Quote**: "passes trace ID, metadata to observability callbacks (e.g. S3, Langfuse)"
- **Our assessment**: Directly relevant to Ch02's observability-callback transport, but the page gives no wire shape, no field names, and no statement that it matches the OpenAI-path behavior. Enough to note that the native route participates in callback propagation; not enough to specify how.

### Claim 8: The official Google GenAI SDK can be pointed at the LiteLLM proxy by setting `GOOGLE_GEMINI_BASE_URL`, with no application code change beyond credentials.
- **Evidence**: The "Google GenAI SDK with LiteLLM Proxy" snippet sets `GOOGLE_GEMINI_BASE_URL` and `GEMINI_API_KEY`, then keeps the stock `client.models.generate_content(...)` call.
- **Confidence**: settled
- **Quote**: "Configure Google GenAI SDK to use LiteLLM proxy"
- **Our assessment**: Buy it — this is the operator-facing migration knob. Note the issue triage referred to it as `GEMINI_BASE_URL`; the page's actual variable is `GOOGLE_GEMINI_BASE_URL`. The application code path is unchanged, which means the gateway absorbs the endpoint redirect transparently (analogous to the Bedrock `/invoke` `endpoint_url` swap).

### Claim 9: The SDK surface is exactly four entry points — `generate_content` / `generate_content_stream` (sync) and `agenerate_content` / `agenerate_content_stream` (async) — all from `litellm.google_genai`.
- **Evidence**: The four code blocks' imports.
- **Confidence**: settled
- **Quote**: (code imports; see Concrete Artifacts)
- **Our assessment**: Minor but pinned: the sync/async split and the `google_genai` module namespace are the callable contract. The model string is `gemini/gemini-3.8-flash`, while the proxy alias in the same page is `gemini-flash` — an alias illustration, not a claim.

### Claim 10: Proxy routing is per-`model_name` alias — the client hits `/v1beta/models/<alias>:generateContent` (and `:streamGenerateContent`), and the alias is registered in `model_list`.
- **Evidence**: `config.yaml` snippet plus the two curl routes, both using `gemini-flash` as the path segment.
- **Confidence**: settled
- **Quote**: (no direct quote; see Concrete Artifacts)
- **Our assessment**: The alias-in-path pattern matches the Bedrock `/invoke` route's model-alias-in-path design. The real model id (`gemini/gemini-3.8-flash`) is resolved gateway-side from `model_list`.

### Claim 11: The page is undated, thin, and carries no version anchor — no benchmarks, latency, rate limits, spend detail, or production guidance.
- **Evidence**: Front-matter has only `last_updated: "2026-10-15"`; body is a feature table, four SDK snippets, one config block, and two curl routes.
- **Confidence**: settled
- **Quote**: "last_updated: \"2026-10-15\""
- **Our assessment**: Buy it, and it governs the grades above — the passthrough contract is explicit enough to be `settled` as a documented contract, but every operational claim (matrix rows, metadata callbacks, streaming parity) is `emerging`/`anecdotal` for lack of corroborating detail or a verifiable version.

## Concrete Artifacts

Proxy `model_list` registration (source-attributed):

```yaml
model_list:
    - model_name: gemini-flash
      litellm_params:
        model: gemini/gemini-3.8-flash
        api_key: os.environ/GEMINI_API_KEY
```

Native top-level fields via the Python SDK (source-attributed):

```python
from litellm.google_genai import generate_content
import os

os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

response = generate_content(
    model="gemini/gemini-3.8-flash",
    contents=[{"role": "user", "parts": [{"text": "Say hi"}]}],
    safetySettings=[
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}
    ],
    toolConfig={"functionCallingConfig": {"mode": "AUTO"}},
)
print(response)
```

Native top-level fields via the proxy (`safetySettings` + `toolConfig` as siblings of `generationConfig`), source-attributed body:

```bash
curl -L -X POST 'http://localhost:4000/v1beta/models/gemini-flash:generateContent' \
-H 'content-type: application/json' \
-H "authorization: Bearer $LITELLM_API_KEY" \
-d '{
  "contents": [{"parts": [{"text": "Say hi"}], "role": "user"}],
  "generationConfig": {"maxOutputTokens": 100},
  "safetySettings": [
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}
  ],
  "toolConfig": {"functionCallingConfig": {"mode": "AUTO"}}
}'
```

Streaming route (source-attributed) — note it carries **no** native top-level fields, which is the basis of Claim 4:

```bash
curl -L -X POST 'http://localhost:4000/v1beta/models/gemini-flash:streamGenerateContent' \
-H 'content-type: application/json' \
-H "authorization: Bearer $LITELLM_API_KEY" \
-d '{
  "contents": [{"parts": [{"text": "Write a long story about space exploration"}], "role": "user"}],
  "generationConfig": {"maxOutputTokens": 500}
}'
```

## Cross-References

Candidate file `miner-related-notes.md` (repo root) was read in full; each candidate is cited or explicitly dismissed in Extraction Notes.

- **Corroborates**:
  - `docs-litellm-provider-specific-params.md` Claim 1 — "General pass-through rule — any non-OpenAI param is treated as provider-specific and passed to the provider in the request body as a kwarg." The generateContent passthrough is the native-endpoint instance of the same class of rule, with an explicit four-field allowlist and a precedence statement this note lacks.
  - `docs-litellm-provider-specific-params.md` Claim 5 — provider-specific metadata params documented for Gemini/Vertex include `labels`, one of the four fields this page forwards verbatim.
  - `docs-litellm-bedrock-invoke.md` Claim 1 — the Bedrock native `/invoke` passthrough is routed by the `model_name` alias in the path and speaks the provider wire format directly. `generateContent` is the Google-native analog (`/v1beta/models/<alias>:generateContent`, Google's body shape).
  - `docs-litellm-bedrock-invoke.md` Claim 3 — the Bedrock page's support matrix is likewise a vendor surface claim ("a vendor surface claim with no per-provider parity and no caching caveat"), matching the qualified/unverified character of Claim 6 here.
  - `docs-litellm-anthropic-unified.md` Claim 1 — documents the same provider-native-vs-shared-surface duality: one route that fans out across backends. The generateContent page is the Google-native counterpart.
  - `blog-litellm-gemini-3-flash-day-0.md` Claim 5 and `blog-litellm-gemini-3-5-flash-day-0.md` Claim 8 — both name the Google-native `generateContent` surface as one of four endpoints. Those notes state the endpoint exists; this page is the per-endpoint contract for it. Note the Gemini day-0 notes write the path as `/v1/generateContent` while this page uses `/v1beta/models/{model}:generateContent`; the path-shape difference is not reconciled on this page.

- **Contradicts**:
  - None filed. The nearest neighbor is `docs-litellm-drop-params.md`, which documents the gateway *removing* unsupported OpenAI params (Claim 1: default raise, `drop_params` converts to silent omit; Claim 4: `additional_drop_params` strips a named list regardless of support). That gate and this page's verbatim passthrough act on **different routes and different parameters**: `drop_params` governs the OpenAI-param support check on the OpenAI-compatible path, while `/generateContent` is a native route documented to forward its four named fields. These are different mechanisms, not opposing claims on one topic, so no contradiction issue was filed under MINER §4a. The distinction is still guide-relevant and is captured under Extends below.

- **Extends**:
  - `docs-litellm-drop-params.md` Claim 1, Claim 4 — supplies the inverse mechanism to this page's passthrough. Together they frame the gateway's parameter-handling spectrum: strip/drop on the OpenAI path vs. forward-verbatim on the native Google path.
  - `docs-litellm-completion-input-params.md` Claim 3 — "The gate's scope is bounded by LiteLLM's own OpenAI-param recognition — any parameter it does not classify as an OpenAI param is assumed provider-specific and passed into the request body as a kwarg." That is the generic mechanism; `generateContent` documents an explicit, narrowed allowlist and a precedence rule on top.
  - `docs-litellm-message-sanitization.md` Claim 7 — "The sanitization logic is described as provider-agnostic but applied only in the Anthropic transformation pipeline." Contrast case: on the Anthropic path the gateway *mutates* caller messages; on the native generateContent path it forwards verbatim. Two routes, opposite dispositions toward the request body.
  - `docs-litellm-generic-guardrail-api.md` Claim 2 — the interception list names eight concrete endpoints plus a catch-all "Pass-through endpoints" bullet, but does not name `/generateContent`. This is the coverage-side context for Claim 5's open question: the native route is neither named nor excluded, so documented guardrail coverage for it is unstated.
  - `docs-litellm-apply-guardrail-endpoint.md` Claim 5 — client-supplied `metadata` is a policy channel to a guardrail; the same "control input comes from the caller" pattern is what Claim 5 here flags for `safetySettings`.
  - `docs-litellm-gemini-image-migration.md` Claim 10 — the same Gemini-on-LiteLLM surface, framed as a minor line bump silently changing a contract. This page documents a contract that is version-unanchored, so the migration-discipline lesson applies.

- **Novel**:
  - The explicit `extra_body`-wins-on-conflict precedence (Claim 3) appears nowhere else in the notes reviewed.
  - The named four-field native passthrough allowlist (`safetySettings`, `toolConfig`, `cachedContent`, `labels`) for a Google-native route is new to the corpus.
  - The observation that the streaming variant's native-field behavior is undocumented (Claim 4) is new.

## Guide Impact

- **Chapter 05 — "Provider parity in the shared forwarding path" (guide/05-llm-ops-reliability.md:343)**: The existing rule is filter-to-omit at the shared boundary (never forward an explicitly-falsy param to an untested backend). This source is the deliberate exception that proves the rule: `/generateContent` is a *native* route whose documented contract is forward-verbatim, and it is outside the OpenAI-param support gate entirely. Recommend a short addition: provider-native passthrough routes are a **separate disposition** from the shared OpenAI forwarding path — on the native route the exact-wire discipline still applies, but the default is "forward everything named, verbatim," so the regression guard is an assertion that native siblings *survive*, not that unsupported params are filtered.
- **Chapter 05 — "Parameter migration hazards" (guide/05-llm-ops-reliability.md:327)**: Add that native top-level fields are provider-version contracts forwarded verbatim (Claim 2), and that `extra_body` is the override channel on this route (Claim 3) — the inverse of its usual role. Migrating prompts to a native route changes which body shape reaches the provider.
- **Chapter 02 — observability callbacks**: Claim 7 gives a concrete transport claim — metadata/trace ID propagated to observability callbacks (S3, Langfuse) on the native generateContent route. Recommend adding the native route to the list of paths that participate in callback propagation, flagged as vendor-claimed without a wire shape.
- **Chapter 06 — "A guardrail is an egress boundary" (guide/06-security-and-trust.md:547)**: Claim 5 raises a coverage question this chapter should name: the native `/generateContent` page documents no guardrail behavior, and the generic-guardrail interception list (`docs-litellm-generic-guardrail-api.md` Claim 2) names eight endpoints plus a catch-all "Pass-through endpoints" bullet without naming this route. Recommend adding a sentence that "guardrails are configured" must be scoped per route, and that provider-native routes may forward provider safety settings with documented guardrail coverage left unstated. Keep this a coverage question to verify against proxy source, not a claim that guardrails skip the route (Claim 5 is `emerging`).

## Extraction Notes

- **Candidate file**: `miner-related-notes.md` was read in full and not committed. Dispositions of the 10 candidates: cited #4 `docs-litellm-bedrock-invoke.md` (native passthrough analogue, Claim 1/Claim 3) and #6 `docs-litellm-completion-input-params.md` (Claim 3, generic passthrough). Explicitly dismissed: #1 `docs-litellm-batches-api.md` (batch input-file rate limiting — no overlap with a per-request passthrough contract); #2 `docs-litellm-completion-web-search.md` (provider web-search feature boundary — unrelated surface); #3 `docs-litellm-files-endpoints.md` (provider `/files` object lifecycle — different endpoint); #5 `docs-litellm-audio-transcription.md` (audio fallback/mode config — different route); #7 `docs-litellm-creating-adapters.md` (custom-format translation layer, not a native passthrough); #8 `docs-litellm-completion-web-fetch.md` (Anthropic server-tool surface — different provider/mechanism); #9 `docs-litellm-a2a-iteration-budgets.md` (agent-loop cost controls — unrelated); #10 `docs-google-sre-prodcast-04-09-ai-agents.md` (agent write-permission framing — no claim overlap).
- **Additional cross-refs beyond the candidate file**: the two issue-triage comments pointed at `docs-litellm-drop-params.md` and `docs-litellm-gemini-image-migration.md`; both were read and cited (Extends), and neither warranted a contradiction issue (see Contradicts). `docs-litellm-provider-specific-params.md`, `docs-litellm-anthropic-unified.md`, `docs-litellm-generic-guardrail-api.md`, `docs-litellm-apply-guardrail-endpoint.md`, `docs-litellm-message-sanitization.md`, and the two Gemini day-0 blog notes were found by searching `source-notes/` and cited per §4b.
- **Quotes**: all claim quotes were copied character-for-character from the fetched source markdown (`https://docs.litellm.ai/docs/generateContent`, `<last_updated>` 2026-10-15), fetched twice for confirmation. Claim 4 uses the `(no direct quote; see paraphrase in Our assessment)` convention because it is an absence claim — the page states nothing about streaming native fields, so no quote exists; no quote was fabricated. Claim 5 is our synthesis across the page and a cross-referenced note and is likewise marked without a quote.
- **Scope discipline**: per triage, the SDK boilerplate, `config.yaml`, curl snippets, and the Enterprise footer were extracted only as Concrete Artifacts where they carry the passthrough contract; the capability-checklist rows were recorded but not expanded into a provider-capability claim.
- **Thin-source caveat for the Assayer**: this is an undated, version-unanchored reference page. The primary passthrough/precedence contract (Claims 2–3) is explicit and graded `settled` as *documentation*; operational claims (matrix, metadata callback, streaming parity, the safety-settings coverage gap) are graded `emerging`/`anecdotal` and should not be promoted to guide rules without proxy-source verification.
