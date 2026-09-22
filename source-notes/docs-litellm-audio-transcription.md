---
source_url: https://docs.litellm.ai/docs/audio_transcription
source_type: docs
title: "/audio/transcriptions — LiteLLM AI Gateway Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; documents Proxy v1.85.0 behavior)
date_extracted: 2026-09-22
last_checked: 2026-09-22
status: current
confidence_overall: emerging
issue: "#1401"
---

# /audio/transcriptions (LiteLLM Docs)

> LiteLLM's /audio/transcriptions endpoint reference carries one
> version-gated operational trap — starting in Proxy v1.85.0 the
> `mock_testing_fallbacks` flag is stripped from incoming Proxy requests and
> silently has no effect, so any proxy fallback regression suite that relied
> on it is now testing nothing — and a support matrix whose only qualified row
> is Guardrails, scoped "Applies to output transcribed text (non-streaming
> only)".

## Source Context

- **Type**: docs (official vendor endpoint reference — LiteLLM AI Gateway,
  `/v1/audio/transcriptions`, one page under "Supported Endpoints" in the
  docs nav; also the `transcription()` SDK-function page).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented surface (the support matrix, the fallback
  parameter shape, the `mock_testing_fallbacks` removal, the config contract).
  The page carries no measured data — no latency, no throughput, no
  rate-limit interaction — so every claim here stays at "the vendor documents
  this," never "this holds at scale."
- **Scope**: The support matrix, the model-registration contract, and the
  fallback mechanism (per-request `fallbacks[]` plus the testability change).
  Per the triage, the provider-by-provider quick-start config blocks
  (OpenAI/Azure/Gemini/Groq/Deepgram/Mistral), the provider list, and the
  SDK hello-world are product-usage documentation with no SRE angle and are
  **not** extracted. There is no incident, metric, or failure timeline on this
  page.
- **URL note**: the submitted URL `https://docs.litellm.ai/docs/audio_transcription`
  (HTTP 200) renders the page whose `<h1>` and proxied endpoint path are
  `/audio/transcriptions` — i.e. `POST /v1/audio/transcriptions` against the
  proxy. The `/audio/transcriptions` sidebar entry links to this same URL; the
  endpoint path is the canonical one.

## Extracted Claims

### Claim 1: Starting in LiteLLM Proxy v1.85.0, `mock_testing_fallbacks` is stripped from incoming Proxy requests and has no effect — it remains supported only for direct `litellm.Router` calls in tests
- **Evidence**: The "Testing Fallbacks" section, headed "Deprecated for Proxy
  requests", states the version-scoped change and its Scope-of-survival
  (direct `litellm.Router`).
- **Confidence**: settled (explicitly versioned, directly stated documented
  behavior)
- **Quote**: "Starting in LiteLLM Proxy v1.85.0, `mock_testing_fallbacks` is stripped from incoming Proxy requests and has no effect. It remains supported only for direct `litellm.Router` calls in tests."
- **Our assessment**: The high-value nugget on this page and the reason the
  note exists. A team whose fallback validation relied on passing
  `mock_testing_fallbacks` through the proxy gets green tests that exercise
  nothing after the upgrade — the Proxy strips the flag and the page documents
  no error, no warning log, no metric emitted when it is present. This is a
  documented, version-gated degradation of fallback *testability* at the proxy
  boundary, distinct from the corpus's other silent-fallback failure note
  (`failure-litellm-model-cost-map-silent-fallback.md`, where *data* silently
  falls back to a stale copy rather than a test input silently being ignored).
  Both share the detectability failure: the degradation is invisible to normal
  request success metrics.

### Claim 2: The vendor-documented replacement for validating audio-transcription fallbacks through the Proxy is to trigger an actual provider error in a non-production environment and send a normal request with the fallback configuration
- **Evidence**: The sentence immediately following Claim 1's statement in the
  "Testing Fallbacks" section.
- **Confidence**: settled (explicit documented instruction)
- **Quote**: "To validate audio transcription fallbacks through the Proxy, trigger an actual provider error in a non-production environment and send a normal request with the fallback configuration."
- **Our assessment**: The synthetic test harness goes away; fallback validation
  now couples to the operator's ability to inject a real provider failure in a
  staging environment. For a gateway operator this raises the cost and the
  blast-radius of fallback testing (an induced provider error can trip provider
  rate limits or cooldowns), and it makes "do fallbacks actually work?"
  harder to verify as a CI/regression step. This is the operational constraint
  the triage flagged: "you cannot synthetically exercise proxy fallbacks
  anymore; fallback validation now requires an induced provider failure in
  staging."

### Claim 3: Audio-transcription fallbacks are configured per-request in the request body — a `fallbacks[]` form field on the curl path and `extra_body={"fallbacks": [...]}` via the OpenAI SDK — documented as auto-retry with different models if the primary model fails
- **Evidence**: The "Fallbacks" section intro and its two call-shape examples
  (curl `--form 'fallbacks[]="openai/whisper-1"'`; SDK
  `extra_body={"fallbacks": ["openai/whisper-1"]}`).
- **Confidence**: settled (documented config surface with verbatim examples)
- **Quote**: "You can configure fallbacks for audio transcription to automatically retry with different models if the primary model fails."
- **Our assessment**: The fallback list is a request-body parameter on this
  endpoint rather than (only) a router-level config. The page does **not**
  state whether this exercises the same engine as router-level fallbacks or a
  separate per-request path — that question (raised by the Prospector) is
  unanswered on this page; the support matrix's "Fallbacks ✅ Works between
  supported models" row is the extent of the relationship statement. We record
  the per-request mechanism, not the engine identity.

### Claim 4: A transcription model must be registered in the proxy `model_list` with `model_info: mode: audio_transcription` in `litellm_params` to be served on `/v1/audio/transcriptions` — the `mode` field is what makes this non-chat endpoint routable
- **Evidence**: The "Add model to config" tab's OpenAI configuration block
  (and the Azure variant), registering `model_name: whisper` with
  `mode: audio_transcription`.
- **Confidence**: settled (documented config contract)
- **Quote**: (see Concrete Artifacts for the verbatim YAML config)
- **Our assessment**: Same registration genre as `mode: realtime` for WebRTC
  traffic in `blog-litellm-realtime-webrtc-http-endpoints.md` (Claim 3): the
  `mode` field is the routing discriminant that makes a non-chat endpoint
  reachable. An operator adding an audio transcription model who omits
  `model_info.mode` registers a model the proxy will not route transcription
  requests to — the mode must be explicit, not inferred.

### Claim 5: The support matrix documents Cost Tracking, Logging, End-user Tracking, Fallbacks, and Loadbalancing as ✅ on this non-chat endpoint, and qualifies the lone Guardrails row as "Applies to output transcribed text (non-streaming only)"
- **Evidence**: The Overview feature table — five unconditional ✅ rows (Cost
  Tracking "Works with all supported models", Logging "Works across all
  integrations", End-user Tracking no note, Fallbacks and Loadbalancing "Works
  between supported models") and the sixth Row (Guardrails) carrying a scoping
  note.
- **Confidence**: settled (explicit matrix)
- **Quote**: "Applies to output transcribed text (non-streaming only)"
- **Our assessment**: Two operational facts. (1) The gateway asserts cost
  tracking, logging, and end-user attribution all apply to this non-text
  endpoint — useful evidence for the guide's spend/observability material on
  non-chat modalities. (2) Guardrail coverage is bounded by the endpoint *and*
  by streaming mode: the guardrail sees the transcribed output only in the
  non-streaming path, so a streaming transcription request passes guardrail-free
  by documented design — a coverage gap, not a config error.

### Claim 6: The support matrix is a recurring per-endpoint feature-support contract across the LiteLLM docs, not a one-off table — the `/v1/messages` page repeats the same row vocabulary and the same non-streaming guardrail carve-out, while the `/v1/messages/count_tokens` page keeps the genre in a thinner, differently-shaped matrix
- **Evidence**: Cross-page comparison against the `/v1/messages` feature table
  (`docs-litellm-anthropic-unified.md` Claim 2), which uses the same row
  vocabulary for the rows both pages carry — Cost Tracking "Works with all
  supported models", Logging "Works across all integrations", End-user
  Tracking with no note, Fallbacks and Loadbalancing "Works between supported
  models" — and the same non-streaming guardrail carve-out (that page's
  Guardrails note reads "Applies to input and output text (non-streaming
  only)"; this page's reads "Applies to output transcribed text (non-streaming
  only)" — same carve-out, different scope wording). Contrasted with the
  `/v1/messages/count_tokens` overview table
  (`docs-litellm-anthropic-count-tokens.md` Claim 4), which keeps the matrix
  genre but not its shape: three rows only (Cost Tracking ❌ "Token counting
  only, no cost incurred", Logging ✅, End-user Tracking ✅), with no Fallbacks,
  Loadbalancing, Streaming, or Guardrails rows at all.
- **Confidence**: emerging (the recurrence is established by comparing three
  vendor pages; the interpretation is the Miner's synthesis)
- **Quote**: (no single direct quote — the recurrence is a comparison of three
  pages; see the cited notes)
- **Our assessment**: The guide may cite this matrix genre as a
  vendor-standard "Feature / Supported / Notes" contract repeated per
  endpoint — with the caveat that ✅ is *surface support*, not per-provider
  parity (matching the assessment in `docs-litellm-anthropic-unified.md`
  Claim 2). The recurrence is in the *format and row vocabulary*, not in an
  identical table: which rows appear at all varies by endpoint (the
  count-tokens page has no Fallbacks, Loadbalancing, or Guardrails row), and
  the per-page *note* column is where the genuinely different limitations live
  (here: the non-streaming guardrail carve-out scoped to output transcribed
  text). Claims of an endpoint-to-endpoint "identical parity contract" should
  therefore not be made at a granularity finer than the shared rows.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(https://docs.litellm.ai/docs/audio_transcription), verified against the raw
HTML.

### Support matrix (from "Overview", verbatim)

| Feature | Supported | Notes |
|---------|-----------|-------|
| Cost Tracking | ✅ | Works with all supported models |
| Logging | ✅ | Works across all integrations |
| End-user Tracking | ✅ | |
| Fallbacks | ✅ | Works between supported models |
| Loadbalancing | ✅ | Works between supported models |
| Guardrails | ✅ | Applies to output transcribed text (non-streaming only) |

### Model registration (from "LiteLLM Proxy → Add model to config → OpenAI", verbatim)

```yaml
model_list:
- model_name: whisper
  litellm_params:
    model: whisper-1
    api_key: os.environ/OPENAI_API_KEY
  model_info:
    mode: audio_transcription

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
```

### Per-request fallbacks — curl (from "Fallbacks → Test with cURL and Fallbacks", verbatim)

```bash
curl --location 'http://0.0.0.0:4000/v1/audio/transcriptions' \
--header "Authorization: Bearer $LITELLM_API_KEY" \
--form 'file=@"gettysburg.wav"' \
--form 'model="groq/whisper-large-v3"' \
--form 'fallbacks[]="openai/whisper-1"'
```

### Per-request fallbacks — OpenAI SDK (from "Fallbacks → Test with OpenAI Python SDK and Fallbacks", verbatim)

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-<your-litellm-api-key>",
    base_url="http://0.0.0.0:4000")

audio_file = open("gettysburg.wav", "rb")

transcript = client.audio.transcriptions.create(
    model="groq/whisper-large-v3",
    file=audio_file,
    extra_body={
        "fallbacks": ["openai/whisper-1"]
    })
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-a2a-cost-tracking.md` — **cited** (Extends — see
  below).
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: routing-flavor
  collapse and the classifier's fallback to a heuristic scorer; no proxy
  fallback-chain or fallback-testing content.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum and write-permission governance; unrelated.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch input-file
  TPM/RPM limiting; a different endpoint and a different rate-limit surface,
  no audio fallback or guardrail content.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**:
  per-session agent-loop iteration/budget caps; no audio content.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP
  coding-agent intake; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  observability integration; its Claim 3 mentions fallbacks only as a
  vendor-boundary header stack-up, not the proxy's audio fallback mechanism.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization/measurement; unrelated.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  app-layer Langfuse scanner stacks; no gateway endpoint-coverage matrix.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: the A2A
  agent-card per-field ✅/❌ matrix; a different surface genre with no audio
  content.

Additional cross-references found by searching `source-notes/` (the triage's
overlap list plus cross-page matrix comparison):
`docs-litellm-anthropic-unified.md`, `docs-litellm-anthropic-count-tokens.md`,
`docs-litellm-generic-guardrail-api.md`, `blog-litellm-realtime-webrtc-http-endpoints.md`
(all cited below); `docs-litellm-streaming-token-usage.md`,
`failure-litellm-model-cost-map-silent-fallback.md`,
`failure-litellm-encrypted-content-affinity.md`,
`blog-litellm-redis-circuit-breaker.md` (cited/dismissed below).

**Primary cross-references (verified per MINER §4b — claims re-read in the
cited notes before writing):**

- **Corroborates**:
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 2** (the same
    "Cost Tracking ✅ Works with all supported models" / "Logging ✅ Works
    across all integrations" / "Fallbacks ✅ Works between supported models"
    row texts and the same non-streaming guardrail carve-out on
    `/v1/messages`) — the evidence behind Claim 6 here: the matrix format and
    row vocabulary recur across endpoint pages, with the Guardrails note
    worded for a different scope ("input and output" there vs "output
    transcribed" here). (Verified: Claim 2's evidence lists those row texts
    and the non-streaming carve-out; the guardrail wording difference is
    verbatim.)
  - `source-notes/failure-litellm-encrypted-content-affinity.md` **Lesson 4**
    ("Streaming and non-streaming responses need separate treatment" — a
    gateway bug where a fix covered only the final-response path and missed
    the streaming iterator) — corroborates that streaming and non-streaming
    are distinct code paths on this gateway, which is why the documented
    non-streaming-only guardrail carve-out is a real coverage boundary rather
    than a doc quirk.
- **Contrasts** (same genre, different shape — not a contradiction, so no
  issue filed): `source-notes/docs-litellm-anthropic-count-tokens.md`
  **Claim 4** — `/v1/messages/count_tokens` keeps the Feature / Supported /
  Notes matrix genre, but its table is three rows (Cost Tracking ❌ with the
  negation note "Token counting only, no cost incurred", Logging ✅, End-user
  Tracking ✅) and carries none of the Fallbacks, Loadbalancing, Streaming, or
  Guardrails rows this page has. It is therefore a counterexample to any
  reading of Claim 6 as an identical contract repeated verbatim across
  endpoints, and is cited here for that reason rather than as corroboration.
  (Verified: Claim 4's evidence and the note's Concrete Artifacts table at
  `docs-litellm-anthropic-count-tokens.md:181` list exactly those three rows.)
- **Contradicts**: None. No existing source note claims `mock_testing_fallbacks`
  works through the proxy, or that guardrails reach streaming transcription
  (the `/v1/messages` guardrail row carries the same non-streaming carve-out,
  agreeing rather than opposing). No within-source contradiction — the
  Guardrails ✅ row carries its own caveat. Verified against the open
  `contradiction`-labeled issues (#1408/#1352/#1338/#1322/#1307/#1150) and
  CONTRADICTIONS.md (no related `C-NNN` entries). No contradiction issue filed.
- **Extends**:
  - `source-notes/docs-litellm-generic-guardrail-api.md` **Claim 2** — the
    generic guardrail API intercepts `/v1/audio/transcriptions` on the model
    path ("one guardrail config spans chat, image, audio, and rerank traffic").
    This page adds the *bound* on that interception: the same audio endpoint's
    guardrail row is scoped to output text and non-streaming only. Combined,
    they give the guide its second guardrail narrowness axis — the generic
    guardrail reaches the audio endpoint, but not its streaming path.
    (Verified: Claim 2's supported-endpoint list includes
    `/v1/audio/transcriptions`.)
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — the
    silent-degradation-with-no-warning failure class. Both notes document a
    failure that is invisible to normal request metrics: there, a fallback to a
    stale cost map with no warning log; here, a test-input flag that the proxy
    silently strips. Different mechanisms, same detectability failure —
    "your fallback facility silently stopped doing what a green signal claims
    it is doing."
  - `source-notes/docs-litellm-streaming-token-usage.md` **Claim 1** ("a
    streaming completion does not report token usage unless the client opts
    in") — the shared theme that the streaming path on this gateway has its
    own separate, easy-to-miss contract surface: there the usage account, here
    the guardrail coverage. (Verified: Claim 1 heading and quote.)
  - `source-notes/blog-litellm-realtime-webrtc-http-endpoints.md` **Claim 3**
    (`model_info: mode: realtime` registration for the WebRTC path) — audio
    transcription's `mode: audio_transcription` is the same non-chat `mode`
    registration genre. (Verified: Claim 3 heading and config artifact.)
  - `source-notes/docs-litellm-a2a-cost-tracking.md` **Claim 1** (the gateway
    exposes explicit cost-tracking surface on a non-chat A2A path) — the same
    theme that non-chat endpoints still carry the gateway's
    accounting/attribution rows. (Verified: Claim 1 heading and quote.)
- **Novel**: First source note in the corpus covering the proxy's
  `/v1/audio/transcriptions` endpoint, the `mode: audio_transcription`
  registration, the per-request `fallbacks[]` mechanism on it — and, the
  genuinely new operational fact, the **version-gated removal of proxy-side
  fallback testability** (`mock_testing_fallbacks` stripped at Proxy v1.85.0
  with no error): a "your fallback regression suite silently stopped
  validating" trap that no existing note — over 40 LiteLLM entries — records.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "Cost, capacity, and fallback patterns"
  (`guide/05-llm-ops-reliability.md:970`)**: Add the fallback-validation rule
  from Claim 1-2 to the fallback thread (the silent-substitution /
  substitution-authority material at `:972` and `:987`): since Proxy v1.85.0 a
  team cannot synthetically exercise proxy fallbacks via `mock_testing_fallbacks`
  — the flag is stripped and inert — so any fallback-test regression suite that
  passed through the proxy before the upgrade was silently testing nothing
  afterward, and validation now requires inducing an actual provider failure in
  a non-production environment. Recommend that teams pin fallback-validation
  suites to a proxy version they still trust, or re-point them at induced
  provider error injection, and treat "green on `mock_testing_fallbacks`" as
  no evidence of proxy fallback behavior after the upgrade.
- **Chapter 05 — "A guardrail in the request path is an availability
  dependency" (`guide/05-llm-ops-reliability.md:1307`)**: Add per-endpoint and
  per-streaming-mode coverage verification: the guardrail rows on
  `/v1/audio/transcriptions` document coverage of output text **non-streaming
  only**, so a streaming transcription path is guardrail-free by design. The
  rule "verify per endpoint that guardrail coverage is in scope on the paths
  your agents actually use" (Ch06's version at
  `guide/06-security-and-trust.md:302`) extends to verifying per streaming mode.
- **Chapter 06 (Security and Trust) — "Coverage is narrower than interception"
  (`guide/06-security-and-trust.md:302`)**: The guardrail caveat here is a
  second, independent narrowness axis for the existing claim: coverage varies
  per endpoint (tools on three endpoints only) **and** per streaming mode
  (guardrail reaches audio output only when non-streaming). Cite Claim 5-6 as
  evidence alongside `docs-litellm-generic-guardrail-api` Claim 5.
- **Chapter 02 (Observability) — cost/logging for non-text modalities**: The
  support matrix's Cost Tracking ✅ / Logging ✅ rows (Claim 5-6) document that
  the gateway's spend/attribution accounting extends to this non-chat endpoint,
  with the "✅ = surface support, not per-provider parity" caveat.

## Extraction Notes

- Source read in full (direct fetch of `https://docs.litellm.ai/docs/audio_transcription`,
  HTTP 200, no paywall, no truncation), first as markdown then re-fetched as
  raw HTML to verify every quote and code artifact character-for-character
  (the markdown rendering flattened YAML indentation and fenced-block wrapping).
  All `Quote` fields are contiguous verbatim strings from the rendered page
  prose; code blocks in Concrete Artifacts are copied from the page's own
  fenced blocks. Quote-locations for re-verification: Claim 1-2 quotes are the
  two sentences in the "Testing Fallbacks" section under the "Deprecated for
  Proxy requests" callout; Claim 3's intro sentence opens the "Fallbacks"
  section; Claim 5's quote is the Guardrails row's Notes cell in the Overview
  table.
- Triage honored (three concurrent Prospector runs, reconciled to
  `priority:medium`): extraction leads with the `mock_testing_fallbacks`
  v1.85.0 change (Claim 1-2) and the non-streaming-only guardrail caveat
  (Claim 5), per the reconciled key question; per-request `fallbacks[]`, the
  `mode` registration, and the matrix-parity question round it out. The
  provider quick-starts, provider list, and SDK hello-world were deliberately
  not extracted per triage (product-usage docs, no SRE angle). The triage's
  URL note is recorded in Source Context and checked against the raw HTML
  `<title>` and `<h1>`.
- The triage's open question — whether per-request `fallbacks[]` is the same
  engine as router-level fallbacks or a separate path — is **not answered by
  the page**; recorded in Claim 3's assessment as unresolved, not assumed.
  Similarly the triage's "general per-endpoint parity contract vs one-off
  table" question is answered by Claim 6 via cross-page comparison, with the
  comparison restricted to notes already in the corpus.
- **Contradiction scan (MINER §4a)**: no contradiction issue filed. No existing
  source-note claim opposes the two extractable facts, the `/v1/messages`
  guardrail row agrees (same non-streaming carve-out), and the 
  `mock_testing_fallbacks` change is a versioned product change rather than a
  live position. Verified against CONTRADICTIONS.md (no matching `C-NNN`) and
  all open `contradiction`-labeled issues (#1408/#1352/#1338/#1322/#1307/#1150
  — none touch this page or proxy fallback testing).
- **Cross-ref verification (§4b)**: re-read before citing —
  `docs-litellm-anthropic-unified.md` Claim 2 (the same row texts for the
  rows both pages carry, and the same "non-streaming only" guardrail carve-out
  under a differently-worded scope),
  `docs-litellm-anthropic-count-tokens.md` Claim 4 (cited as a **contrast**,
  not corroboration — its matrix is three rows and carries no
  Fallbacks/Loadbalancing/Guardrails rows),
  `docs-litellm-generic-guardrail-api.md` Claim 2 (intercepted-endpoint list
  includes `/v1/audio/transcriptions`),
  `blog-litellm-realtime-webrtc-http-endpoints.md` Claim 3 (`mode: realtime`
  registration),
  `docs-litellm-a2a-cost-tracking.md` Claim 1 (non-chat cost-tracking surface),
  `docs-litellm-streaming-token-usage.md` Claim 1 (streaming usage opt-in),
  `failure-litellm-encrypted-content-affinity.md` Lesson 4 (streaming vs
  non-streaming code paths), and
  `failure-litellm-model-cost-map-silent-fallback.md` (silent-fallback failure
  class). No claim numbers invented; every `Claim N` citation resolves to a
  real numbered claim in the cited note.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes:
  the extractable facts are explicitly documented, version-scoped vendor
  behavior (settled-as-documented), but the page is thin, carries no measured
  data, and the operational consequences in `Our assessment` — the silent
  unvalidation trap, the induced-provider-failure coupling, the guardrail
  coverage boundary — are the Miner's reading of that documented surface, not
  measurements.