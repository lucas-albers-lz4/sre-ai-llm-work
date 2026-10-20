---
source_url: https://docs.litellm.ai/docs/embedding/supported_embedding
source_type: docs
title: "/embeddings | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; page footer reads "© 2026 LiteLLM")
date_extracted: 2026-10-20
last_checked: 2026-10-20
status: current
confidence_overall: emerging
issue: "#1678"
---

# /embeddings — LiteLLM SDK reference (provider-divergent embedding parameter semantics)

> LiteLLM's canonical `/embeddings` reference documents several embedding
> parameters whose semantics are *provider-divergent on the same call path*,
> including one (`input_type`) the vendor itself warns degrades retrieval
> performance silently when mis-set — no error, just worse results — plus a
> Gemini-API-vs-Vertex result-cardinality divergence, a `drop_params`-gated
> silent-drop on Gemini file blocks, and the documented `encoding_format="float"`
> baseline underneath the corpus's existing vLLM embeddings incident.

## Source Context

- **Type**: docs (LiteLLM first-party SDK-function reference for
  `litellm.embedding()` / `aembedding()`; breadcrumb "Python SDK → SDK Functions
  → `embedding()`"; canonical `/docs/` path, verified HTTP 200 on 2026-10-20).
  Living/undated — footer reads "© 2026 LiteLLM".
- **Author credibility**: BerriAI / LiteLLM, the gateway vendor. Authoritative
  for the *documented* request surface (param glossary, provider invocation
  examples, the `input_type` warning, the Gemini response-shape callout).
  Capability documentation only — no metrics, no incident data, no independent
  validation; every claim stays "the vendor documents this".
- **Scope**: The `embedding()` input surface (required/optional params, input
  ceilings, `input_type`, `dimensions`, `encoding_format`, `timeout`) plus the
  provider-divergent behavior sections (NVIDIA/E5 dual-mode, Gemini
  multimodal/nested-list/file-block semantics, TwelveLabs/Bedrock async,
  Cohere `input_type`). Explicitly **not** mined: the provider → model-name
  support catalogue that makes up the bulk of the page (per Prospector triage
  on #1678, catalogues are crawl noise under the `litellm-docs` seed scope;
  precedent #1262).

## Extracted Claims

### Claim 1: Dual-mode embedding models (NVIDIA NIM QA models, E5 family) require `input_type="passage"` for indexing and `"query"` for retrieval, and the vendor explicitly warns that mis-use silently drops retrieval quality — no error, no signal
- **Evidence**: The dedicated "`input_type` Parameter for Embedding Models"
  section, with a warning callout. The failure mode is a *quality* failure
  with a 200 response — the same silent-failure class as the corpus's vLLM
  `encoding_format` incident, but quality-scoped rather than error-scoped.
- **Confidence**: settled (explicit vendor warning, unqualified)
- **Quote**: "Certain embedding models, such as `nvidia/embed-qa-4` and the E5 family, operate in **dual modes**: one for **indexing documents (passages)** and another for **querying**. Set the `input_type` parameter correctly so retrieval accuracy stays high." / "Incorrect usage of `input_type` can lead to a significant drop in retrieval performance."
- **Our assessment**: Highest-value item on the page. This is a
  vendor-documented *silent degradation* parameter: a wrong (or omitted)
  `input_type` on a dual-mode model returns HTTP 200 with a worse vector.
  Alerts will never see it; only retrieval evals (recall@k against a labeled
  query set) catch it. It also has a cross-cutting consequence: a gateway
  config that sets `input_type: search_document` in `litellm_params` (as the
  page's Cohere example shows) bakes *indexing* semantics into every call on
  that model entry — including query-time calls — silently degrading
  retrieval if that entry serves both roles. Ch02/Ch05 relevant.

### Claim 2: The same logical `gemini-embedding-2` embedding call returns *per-input* vectors on the Gemini API path but a *single combined vector* on the Vertex AI path — result cardinality diverges by backend without any error
- **Evidence**: The "Response shape" callout in the Gemini Embedding 2
  Preview section. LiteLLM routes the Gemini API path to `batchEmbedContents`
  with one `EmbedContentRequest` per input (OpenAI-compatible cardinality);
  Vertex "combines all parts into a single unified vector".
- **Confidence**: settled (explicit vendor statement of both shapes)
- **Quote**: "For the Gemini API path (`gemini/gemini-embedding-2-preview`), each input element returns its **own** embedding (indexed `0..N-1`), the same semantics as OpenAI's `/embeddings`. LiteLLM routes to Gemini's `batchEmbedContents` endpoint with one `EmbedContentRequest` per input. This differs from the Vertex AI path, which combines all parts into a single unified vector"
- **Our assessment**: A textbook provider-parity trap on a shared gateway
  path: re-pointing a model entry from `gemini/...` to `vertex_ai/...` (or
  failover between them) changes `len(response.data)` for the same request
  body. A downstream RAG indexer that zips inputs to embeddings by index will
  silently mis-index (or crash on a count assertion) with no upstream error.
  This is the documented-divergence counterpart to the corpus's incident-
  established provider-divergence class — see Extends.

### Claim 3: On the Gemini API path only, wrapping input elements in a nested list changes output cardinality — flat list → one embedding per element, nested list → one combined embedding — while Vertex AI always returns a single combined vector regardless of input shape
- **Evidence**: "Combined Multimodal Embeddings" section with SDK/curl
  examples annotating `response.data` counts (2 embeddings, 1 embedding,
  mixed → 2 embeddings).
- **Confidence**: settled (explicit vendor statement with worked examples)
- **Quote**: "By default, each element in the `input` list produces a **separate** embedding (OpenAI-compatible). To combine multiple inputs into a **single** embedding (e.g., text + image representing one entity), wrap them in a nested list:" / "Gemini API only. Vertex AI always returns a single combined vector regardless of input shape"
- **Our assessment**: The nesting level of a JSON array is an unusual
  semantic switch — schema-valid on both shapes, so a client bug (or a
  serialization layer that adds/removes a level) changes embedding semantics
  without failing validation. Combined with Claim 2, the Gemini embeddings
  surface has *two* independent cardinality controls (backend choice, list
  nesting), neither visible in the OpenAI-shaped response contract.

### Claim 4: `dimensions` is documented as supported only on OpenAI/Azure `text-embedding-3` and later; on Gemini it is a documented translation to `outputDimensionality` — the page documents no behavior for providers that support neither
- **Evidence**: The optional-fields glossary and the Gemini section's
  one-line mapping note.
- **Confidence**: settled as documentation; unlisted-provider behavior is
  undocumented (the page is silent, not wrong)
- **Quote**: "`dimensions`: *integer (Optional)* The number of dimensions the resulting output embeddings should have. Only supported in OpenAI/Azure text-embedding-3 and later models." / "**Optional:** `dimensions` maps to Gemini's `outputDimensionality`."
- **Our assessment**: A `dimensions` value in a shared client config follows
  the model routing: fine on OpenAI/Azure v3+ and Gemini, and the page gives
  no contract for the other ~10 providers in its own catalogue (ignore vs
  reject). Combined with Claim 2/3, dimension *and* cardinality both drift
  with backend choice — index-compatibility checks should pin both.

### Claim 5: `encoding_format` defaults to `"float"` (float|base64) — the documented baseline of the exact parameter whose explicit-null mishandling broke vLLM embeddings for ~3 hours in the corpus's existing incident note
- **Evidence**: The optional-fields glossary on the same page the corpus's
  incident postmortem describes; the page documents the intended default the
  breaking commit (`dbcae4a`) tried to control.
- **Confidence**: settled (explicit vendor default)
- **Quote**: "`encoding_format`: *string (Optional)* The format to return the embeddings in. Can be either `\"float\"` or `\"base64\"`. Defaults to `encoding_format=\"float\"`"
- **Our assessment**: Corroborating documentation, not new evidence: this is
  the "what correct looks like" baseline for
  `failure-litellm-vllm-embeddings-encoding-format.md` (Claim 1 / Claim 2 of
  that note — SDK default injection vs strict omission semantics). Recorded
  here so the documented default and the incident are cross-linked in the
  corpus.

### Claim 6: The documented default client timeout for embeddings calls is 600 seconds (10 minutes)
- **Evidence**: The optional-fields glossary. The same 600s figure is the
  documented prose default on the `completion()` input page (already noted
  there with a prose-vs-signature disagreement).
- **Confidence**: settled (explicit vendor default)
- **Quote**: "`timeout`: *integer (Optional)* - The maximum time, in seconds, to wait for the API to respond. Defaults to 600 seconds (10 minutes)."
- **Our assessment**: A 10-minute default on an embeddings call is a long
  silent hold for a synchronous retrieval path — a wedged provider holds the
  request (and the client worker) for 10 minutes before any error. For RAG
  request paths this default is almost always wrong; set an explicit timeout
  per route. Worth noting the gateway retry/failover implication: retries
  stack on top of the timeout, so worst-case latency is timeout × attempts.
  The embeddings page carries no retry/failover guidance of its own.

### Claim 7: An unknown key anywhere in a Gemini embeddings file content block is answered with a 400 naming it — or silently dropped when `drop_params` is set globally or on the request
- **Evidence**: The "Video Clips and Explicit MIME Types" section's field
  description paragraph. Silent-drop under `drop_params` is the same
  hazard class as an unsupported parameter being dropped.
- **Confidence**: settled (explicit vendor statement of both branches)
- **Quote**: "An unknown key anywhere in the block (for example chat's `detail`) answers 400 naming it, or is dropped when `drop_params` is set globally or on the request, the same way an unsupported parameter is."
- **Our assessment**: `drop_params` converts a loud contract violation into
  a silent field drop *inside a structured input element* — e.g., a typo'd
  `video_metadata` key means the fps/offset window is silently ignored and
  the whole video (not the clip) is embedded: more cost, wrong vector, HTTP
  200. This is the explicitly-falsy-vs-omitted hazard's sibling: the same
  gateway knob (`drop_params`) that protects against strict-validator 400s
  on one provider simultaneously creates silent input mutation on another.
  Operators enabling `drop_params` fleet-wide for vLLM-style strictness get
  Gemini file-block typos for free.

### Claim 8: Input ceilings are per-model and per-shape — input must not exceed the model's max input tokens (8192 for ada-002), a token-array input must be 2048 dimensions or less, and an empty string is rejected
- **Evidence**: The `input` field description in the Required Fields list.
- **Confidence**: settled (explicit vendor statement; the 8192 figure is
  model-specific and the general rule is "the model's max")
- **Quote**: "The input must not exceed the max input tokens for the model (8192 tokens for text-embedding-ada-002), cannot be an empty string, and any array must be 2048 dimensions or less."
- **Our assessment**: Ordinary validation contract; the ops-relevant point is
  that the ceiling is *per-model* on a gateway whose model entries are
  re-pointable — a chunker sized for ada-002's 8192 silently overflows when
  the entry is swapped to a smaller-context embedding model. Low signal on
  its own; kept because it bounds the same `/embeddings` contract the other
  claims touch.

### Claim 9: Gemini embeddings always run OCR on PDF inputs — there is no parameter to toggle it — so PDF cost/latency (OCR included) is fixed by the provider, not controllable at the gateway
- **Evidence**: The "PDF OCR" callout in the Gemini Embedding 2 Preview
  section.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "The Gemini embeddings API always runs OCR on PDF inputs and has no parameter to turn it on or off, so there is nothing to pass for it."
- **Our assessment**: A fixed, uncontrollable cost/latency multiplier on one
  provider: routing PDF embedding traffic to Gemini includes OCR per call
  whether or not the text layer was the point. Operators doing cost
  attribution per embedding call should treat Gemini-PDF as a distinct cost
  class; there is no knob to trade OCR off for speed.

### Claim 10: Bedrock async embeddings require `output_s3_uri` (results land in S3, not the response), and TwelveLabs Marengo sync mode is text-only while async covers all input types — the async path is a different result-delivery contract, not just a different call shape
- **Evidence**: The Bedrock model table (Nova async and TwelveLabs async
  function-call rows carry `output_s3_uri`) and the TwelveLabs section's
  supported-models table ("All input types, requires `output_s3_uri`" vs
  sync "Text embeddings only").
- **Confidence**: settled (explicit vendor tables)
- **Quote**: "All input types, requires `output_s3_uri`"
- **Our assessment**: Async embeddings through the gateway are a
  fire-and-fetch-S3 pattern: the embeddings result is *not* in the
  synchronous response, so any pipeline written against the OpenAI-shaped
  `response.data` contract breaks on these model entries without an error
  shape mismatch being obvious up front. Sync-vs-async also gates which
  modalities exist (TwelveLabs: text-only sync). Same theme as Claims 2–3:
  one `/embeddings` call path, multiple result contracts.

### Claim 11: Any non-OpenAI parameter on the embeddings path is treated as provider-specific and forwarded as a kwarg in the request body — and `input_type` is the worked example, settable per-call, or pinned for a model entry in `config.yaml`
- **Evidence**: The info admonition (stated twice, once mid-page and once in
  the VoyageAI "Provider-specific Params" section), plus the Cohere example
  showing `input_type` in `litellm_params` and in a proxy request body.
- **Confidence**: settled (explicit vendor statement; config/request examples
  shipped)
- **Quote**: "Any non-openai params, will be treated as provider-specific params, and sent in the request body as kwargs to the provider."
- **Our assessment**: This is the passthrough rule that makes Claims 1 and 10
  gateway-relevant: `input_type` is not a normalized, cross-provider LiteLLM
  param — it is a provider kwarg that happens to have documented meaning on
  NVIDIA/E5, Cohere v3, TwelveLabs, and HuggingFace, with *different value
  vocabularies* on each (`"passage"`/`"query"` vs `search_document`/
  `search_query`/`classification`/`clustering` vs `"text"`/`"image"`/
  `"video"`/`"audio"` vs `"feature-extraction"`/`"sentence-similarity"`).
  A config that pins one `input_type` string across model entries is wrong
  for all but one provider family — and per Claim 1, wrongness is silent.

## Concrete Artifacts

**The `input_type` silent-degradation warning (verbatim from source, callout in the NVIDIA NIM `input_type` section):**

```
Warning: Incorrect usage of input_type can lead to a significant drop in retrieval performance.
```

**Cohere `input_type` value vocabulary (verbatim from source, Provider-specific Params section):**

```
-   `input_type="search_document"`: (default) Use this for texts (documents) you want to store in your vector database
-   `input_type="search_query"`: Use this for search queries to find the most relevant documents in your vector database
-   `input_type="classification"`: Use this if you use the embeddings as an input for a classification system
-   `input_type="clustering"`: Use this if you use embeddings for text clustering
```

**`input_type` pinned at the model-entry level in `config.yaml` (verbatim from source) — note this bakes indexing semantics into every call routed to the entry:**

```yaml
model_list:
  - model_name: "cohere-embed"
    litellm_params:
      model: embed-english-v3.0
      input_type: search_document # PROVIDER-SPECIFIC PARAM
```

**Nested-list cardinality switch — Gemini API path (verbatim from source, Combined Multimodal Embeddings SDK example):**

```python
from litellm import embedding

# Separate: 2 inputs → 2 embeddings
response = embedding(
    model="gemini/gemini-embedding-2-preview",
    input=["a red shoe", "data:image/png;base64,..."],
)
# response.data has 2 embeddings

# Combined: text + image → 1 embedding
response = embedding(
    model="gemini/gemini-embedding-2-preview",
    input=[["a red shoe", "data:image/png;base64,..."]],
)
# response.data has 1 embedding representing both together

# Mixed: 1 combined + 1 separate → 2 embeddings
response = embedding(
    model="gemini/gemini-embedding-2-preview",
    input=[["a red shoe", "data:image/png;base64,..."], "just text"],
)
# response.data has 2 embeddings
```

**Gemini file content block — the `drop_params` silent-drop clause and field contract (verbatim from source):**

```
Field            Description
file.file_id     gs://bucket/clip.mp4, a Gemini Files API reference files/abc123, or the id /v1/files returns for a Gemini upload (https://generativelanguage.googleapis.com/v1beta/files/abc123)
file.file_data   A data URI, data:video/mp4;base64,<encoded_data>
file.format      Optional MIME type that overrides the one inferred from the extension or the data URI
file.video_metadata   Optional fps (number), start_offset and end_offset (strings such as "3s"), converted to Gemini's startOffset and endOffset

An unknown key anywhere in the block (for example chat's `detail`) answers
400 naming it, or is dropped when `drop_params` is set globally or on the
request, the same way an unsupported parameter is.
```

**The parameter glossary lines carrying the defaults (verbatim from source, Optional LiteLLM Fields):**

```
-   `dimensions`: *integer (Optional)* The number of dimensions the resulting output embeddings should have. Only supported in OpenAI/Azure text-embedding-3 and later models.

-   `encoding_format`: *string (Optional)* The format to return the embeddings in. Can be either "float" or "base64". Defaults to encoding_format="float"

-   `timeout`: *integer (Optional)* - The maximum time, in seconds, to wait for the API to respond. Defaults to 600 seconds (10 minutes).
```

## Cross-References

- **Corroborates**:
  - `failure-litellm-vllm-embeddings-encoding-format.md` (Claims 1, 2) —
    that note's Claim 1 (explicit-`None` instead of omission broke vLLM) and
    Claim 2 (`encoding_format` semantics diverge across OpenAI-compatible
    backends) are the incident-established version of this page's
    documented baseline: the glossary's `Defaults to encoding_format="float"`
    is the intended default the breaking commit tried to control. This page
    adds no new incident evidence; it is the vendor-docs counterpart.
  - `docs-litellm-completion-input-params.md` (Claims 3, 5) — Claim 3 of
    that note ("any parameter it does not classify as an OpenAI param is
    assumed provider-specific and passed into the request body as a kwarg")
    is restated on this page for the embeddings path (this note's Claim 11);
    its Claim 5's documented 600-second default timeout matches this page's
    embeddings `timeout` default (this note's Claim 6) — the 600s figure is
    now documented on two SDK-function reference pages.
  - `docs-litellm-caching-all-caches.md` (Claim 2) — that note records
    `supported_call_types` defaulting to include `embedding`/`aembedding`;
    this note's Claim 1 (silent `input_type` degradation) bears directly on
    semantic-cache correctness, since a dual-mode embedding model behind a
    semantic cache whose queries and prompts are embedded with the same
    pinned `input_type` (per that note's Claim 5, cache keys compose from
    `model + messages + ...`) is exactly the misconfiguration the vendor
    warns about.

- **Contradicts**: None. Verified against `CONTRADICTIONS.md` and the
  corpus notes above. No existing note claims embeddings parameters are
  provider-uniform, that `input_type` is normalized across providers, or
  that Gemini API and Vertex AI return the same cardinality. No
  contradiction issue filed.

- **Extends**:
  - `failure-litellm-vllm-embeddings-encoding-format.md` (primary extension
    target per Prospector triage) — that note establishes "provider param
    semantics diverge across OpenAI-compatible backends" from one incident
    (`encoding_format`); this page shows the divergence is *documented vendor
    behavior* on at least two more surfaces: `input_type` (Claim 1, a silent
    *quality* divergence rather than a hard error) and Gemini-API-vs-Vertex
    response cardinality (Claims 2–3). The failure class now has a
    quality-silent member in addition to the error-loud vLLM member.
  - `blog-litellm-valkey-semantic-caching.md` (Claims 6, 7) — that note's
    KNN-on-embedding correctness risk (threshold-gated similarity) composes
    with this note's Claim 1: a dual-mode model mis-configured with
    `input_type` on one side of the cache comparison shifts the similarity
    distribution underneath the fixed threshold, degrading hit precision in
    a way neither the cache nor the gateway can signal.
  - `docs-promptfoo-answer-relevance.md` (Claims 1, 3) — that note's
    two-slot grading (text provider + embedding provider) and its
    score-comparability caveat ("the absolute meaning shifts when the
    embedding model ... changes") are the eval-side twin of this page's
    parameter divergences: `input_type` or `dimensions` drift on the
    embedding provider shifts answer-relevance scores the same way a model
    swap does, without changing any pinned model ID.
  - `docs-litellm-knowledgebase-vector-stores.md` (Claim 1 area —
    gateway-side retrieval augmentation) — adjacent surface: that note's
    silent no-op when a vector store is unregistered is a silent *grounding*
    failure; this note's Claim 1 is a silent *index/query mismatch* failure.
    Both feed the same Ch02 point — retrieval correctness failures at this
    gateway are overwhelmingly silent.

- **Novel**: First corpus coverage of:
  1. The vendor-documented `input_type` silent-retrieval-degradation warning
     (NVIDIA/E5 dual-mode; also required on TwelveLabs, optional on Cohere v3
     and HuggingFace, with four different value vocabularies).
  2. The Gemini-API-vs-Vertex result-cardinality divergence on the same
     `gemini-embedding-2` model (per-input vectors vs single unified vector).
  3. The nested-list input-shape cardinality switch (Gemini API only).
  4. The `drop_params`-gated silent drop of unknown keys *inside Gemini file
     content blocks* (input mutation, not just param dropping).
  5. Gemini PDF OCR being always-on with no toggle (fixed cost/latency
     multiplier).
  6. Bedrock async embeddings' S3 result-delivery contract
     (`output_s3_uri`) as a distinct result shape on the `/embeddings` path.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — gateway/provider parity)**: Extend the
  existing `encoding_format` provider-divergence rule (sourced from
  `failure-litellm-vllm-embeddings-encoding-format.md`) with the documented
  divergences from this note: (a) treat `input_type` as a
  retrieval-correctness parameter, not a tuning knob — pin it per *role*
  (index vs query), never per model entry alone, and never as a shared
  `litellm_params` default for a dual-mode model serving both roles
  (Claims 1, 11); (b) pin *result cardinality* assumptions when a model
  entry can route to Gemini API or Vertex AI — they disagree on
  `len(response.data)` for the same request (Claims 2–3); (c) treat
  `dimensions` as supported-contract-limited (OpenAI/Azure v3+ and Gemini's
  `outputDimensionality` translation) and check it against the routed
  provider, not the client config (Claim 4); (d) note that `drop_params`,
  the documented remedy for strict-validator 400s, simultaneously enables
  *silent input mutation* on Gemini file blocks — scope it narrowly
  (Claim 7).

- **Chapter 02 (Observability — silent failure modes)**: Add `input_type`
  mis-configuration as the canonical *eval-gated, not alert-gated* silent
  failure on the embeddings path: HTTP 200, degraded recall, vendor-warned.
  Recommend a retrieval-quality canary (labeled query set, recall@k trend)
  whenever an embedding model entry, provider route, or `input_type` value
  changes — error monitors cannot see this class. The Gemini/Vertex
  cardinality divergence (Claim 2) is the second silent entry: an index
  ingestion bug with no upstream error.

- **Chapter 05 (caching, light)**: One paragraph tying Claim 1 to the
  semantic-cache notes (`docs-litellm-caching-all-caches.md` Claim 5,
  `blog-litellm-valkey-semantic-caching.md`): semantic-cache correctness
  assumes stable embedding semantics; `input_type` and `dimensions` drift
  invalidate that assumption under a fixed similarity threshold.

## Extraction Notes

- Source fetched in full via WebFetch on 2026-10-20 (HTTP 200, canonical
  `/docs/embedding/supported_embedding` URL, no redirects, no paywall). The
  page is substantive (~24k chars of article text) but ~80–90% is a
  provider→model-name support catalogue, which was deliberately **not**
  mined per the Prospector's scope guidance on #1678 (catalogue = crawl
  noise; precedent #1262). Only the parameter-semantics and
  provider-divergence sections were extracted; the note is intentionally
  short relative to page length.
- All quotes copied character-for-character from the fetched page text
  (Docusaurus render), including bold markers and inline code. Code
  artifacts reproduced as rendered, with the source's own inline comments
  (e.g., `# PROVIDER-SPECIFIC PARAM`) preserved. Where a quote spans a
  rendered table, the table cell contents are reproduced as a contiguous
  fragment, not spliced from non-adjacent cells.
- The Prospector triage also mentioned a `timeout`/retry-failover framing
  and input ceilings; both are captured (Claims 6, 8). The Gemini
  video-clip `videoMetadata` field contract is recorded in Concrete
  Artifacts as the context for the `drop_params` clause (Claim 7) but not
  promoted to its own claim — the ops signal is the silent-drop, not the
  clip-windowing feature.
- `confidence_overall: emerging` — first-party vendor documentation of the
  documented contract, with one vendor warning callout (`input_type`) but
  no measurements, no incident data, and no independent validation of the
  divergences. Triaged `priority:low` as documentation corroboration.
- No contradiction issue filed: verified against `CONTRADICTIONS.md` and
  all overlapping notes; nothing in the corpus disagrees with these
  documented divergences.
- Cross-reference candidates from `miner-related-notes.md` — each cited
  above or dismissed here:
  - `docs-litellm-batches-api.md` — batch rate-limit/token-reservation
    contract; unrelated to embedding param semantics.
  - `docs-litellm-completion-web-search.md` — provider-native web search
    surfaces; gateway-normalizes-request-not-semantics theme is adjacent but
    a different feature area.
  - `docs-litellm-generate-content.md` — Google-native `generateContent`
    passthrough; different route, different contract (top-level field
    passthrough, not embeddings).
  - `docs-litellm-audio-transcription.md` — audio-transcription fallbacks
    and `mode:` routing; unrelated to embeddings parameters.
  - `docs-litellm-creating-adapters.md` — adapter format-translation layer;
    unrelated to embedding param passthrough.
  - `docs-litellm-files-endpoints.md` — provider `/files` passthrough;
    unrelated (the TwelveLabs `output_s3_uri` async pattern here is
    S3-delivery, not the files API).
  - `docs-litellm-bedrock-invoke.md` — Bedrock native Invoke passthrough
    for chat; this note's Bedrock touchpoint is the async *embeddings*
    S3 result contract, a different route and result shape.
  - `docs-litellm-completion-web-fetch.md` — Anthropic web_fetch tool via
    the gateway; unrelated.
