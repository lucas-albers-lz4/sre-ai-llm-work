---
source_url: https://docs.litellm.ai/docs/extras/gemini_img_migration
source_type: docs
title: "Gemini Image Generation Migration Guide — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; raw front matter last_updated 2026-10-14)
date_extracted: 2026-10-15
last_checked: 2026-10-15
status: current
confidence_overall: emerging
issue: "#1721"
---

# Gemini Image Generation Migration Guide (LiteLLM Docs)

> LiteLLM's migration note for a version-scoped **response-contract break**:
> from **v1.77.0** the Gemini image-generation models on `/chat/completions`
> return images as a **list** at `response.choices[0].message.images` (each
> entry a base64 **data URL**) instead of a single image (described in prose
> as `message.image`, and read in the worked "before" code from
> `message.content`). The page states the rationale (the newer
> `gemini-2.5-flash-image-preview` returns text and image together, and the
> plural name matches OpenRouter), the caller requirement
> (`modalities=["image", "text"]`, with text still in `message.content`), and
> confirms the proxy mirrors the SDK — but documents **no rollback flag, no
> compatibility shim, and no deprecation window**. The extractable operator
> value is not the Gemini field rename; it is the case study that a *minor*
> gateway line bump can silently change a response field.

## Source Context

- **Type**: docs (single-page vendor migration guide under LiteLLM's `extras`
  docs; Docusaurus page at `/docs/extras/gemini_img_migration`, raw markdown
  endpoint `/docs/extras/gemini_img_migration.md` carries front matter with
  `last_updated: "2026-10-14"`). It is a companion to the Gemini image-generation
  feature itself, not an incident report — there is no failure timeline, no
  metric, and no postmortem.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented behavior change (the version number, the
  affected model ids, the before/after access paths, the wire shape). It carries
  no measurement and no independent confirmation, so every claim here stays at
  "the vendor documents this," never "this holds across every route or at
  scale."
- **Scope**: the affected model list, the v1.77.0 `message.image`→`message.images`
  change and its rationale, the new entry wire shape, and the SDK + Proxy usage
  paths. Does **not** cover: rollback, backward compatibility, a deprecation
  window, streaming behavior, the `/images/generations` endpoint, error
  behavior, or whether any other model or route is affected.
- **Prospector guidance honored**: the triage asked for this to be extracted as
  the **response-side mirror** of the guide's existing request-side "Parameter
  migration hazards" and "pin/patch vs line-move" discipline — a minor bump
  silently changing the response contract — paired with the "why the shape
  changed" rationale (Claim 3) and the doc's gaps as a limitation (Claim 7).
  The Gemini-specific field rename itself is not the value.

## Extracted Claims

### Claim 1: From v1.77.0, LiteLLM returns images as a **list** at `response.choices[0].message.images` instead of a single image at `response.choices[0].message.image` — a version-scoped response-contract break for the two Gemini image-generation models on `/chat/completions`
- **Evidence**: The "Key Change" `:::info` callout states the version, the new
  field and the old field; the "Who is impacted" section scopes it to two model
  ids on `/chat/completions`; the "Before and After" code blocks show the old
  and new access paths.
- **Confidence**: settled (explicit, dated, first-party version-scoped statement
  plus worked before/after code)
- **Quote**: "From v1.77.0, LiteLLM will return the List of images in `response.choices[0].message.images` instead of a single image in `response.choices[0].message.image`."
- **Our assessment**: The load-bearing fact is the *break*, not the Gemini
  detail. The same request body now yields a different response field, so a
  downstream parser or content-extraction step that read the old path keeps
  executing and quietly produces nothing (or raises on the missing key) — the
  response-side analogue of the request-side silent-mutation class the corpus
  already records (`docs-litellm-drop-params.md` Claim 9, the "param honored vs
  param stripped is indistinguishable" absence). Nothing on the page warns that
  a client that does not update will fail silently; the migration is presented
  as a simple field swap, and the only version anchor is the top-level "v1.77.0."

### Claim 2: Each image is returned as a structured entry whose `image_url.url` is a base64 **data URL** — so the image bytes ride inside the response body, which matters for log/span payload size and any middleware that buffers responses
- **Evidence**: The sentence under the info callout ("with base64 data URLs")
  and the "Response Format" block giving the entry shape.
- **Confidence**: settled (explicit vendor statement plus a worked wire shape)
- **Quote**: "Gemini models now support image generation through chat completions. Images are returned in `response.choices[0].message.images` with base64 data URLs."
- **Our assessment**: Buy as documented. The `data:image/png;base64,...` form is
  what the "After" example prints (`... "data:image/png;base64,..."`), and the
  entry is OpenAI-chat-shaped (`type: "image_url"`, `image_url.detail: "auto"`).
  The operational note the page omits: a list of base64 data URLs is a
  potentially large response body, so observability pipelines that log full
  response bodies, or middleware that buffers them, inherit a payload-size change
  at the same moment the field name changes. The page documents none of this —
  it is our reading of the wire shape, so the size consequence is flagged, not
  asserted.

### Claim 3: The stated rationale is that the newer `gemini-2.5-flash-image-preview` returns text and image in one response (so a structured field replaces content-scanning), and the plural name is deliberately aligned with the OpenRouter API
- **Evidence**: The "Why the change?" section's two paragraphs.
- **Confidence**: settled (explicit vendor rationale)
- **Quote**: "Because the newer `gemini-2.5-flash-image-preview` model sends both text and image responses in the same response. This interface allows a developer to explicitly access the image or text components of the response. Before a developer would have needed to search through the message content to find the image generated by the model."
- **Our assessment**: Buy the rationale as the "why the shape changed" context the
  Prospector asked for. Two design drivers are named: (1) a model that returns
  text *and* image together makes content-scanning fragile, so a typed field is
  the fix; (2) the plural list is chosen for interface consistency with
  OpenRouter (quoted verbatim as "to be consistent with the OpenRouter API").
  This is a forward-looking API-shape decision, which is why the entry can hold
  more than one image — an integrator should not assume exactly one.

### Claim 4: The caller must pass `modalities=["image", "text"]`, and text still lands in `message.content` — the `images` field is additive, not a replacement for text
- **Evidence**: All three call examples (SDK, OpenAI SDK against the proxy,
  curl) carry `modalities=["image", "text"]`, and the new access example still
  reads `message.content` for the text part.
- **Confidence**: settled (consistent across every worked example)
- **Quote**: "print(response.choices[0].message.content)  # Text response (if any)"
- **Our assessment**: Buy. Two things fall out. (1) The change is not
  image-only: a caller's response handling must read *both* `message.content`
  (text) and `message.images` (images) — the page shows both reads side by side.
  (2) `modalities` is a required part of the contract that appears in every
  example but is never stated as a rule in prose; an operator copying only the
  prose ("images are returned in `message.images`") without the request
  `modalities` field has an incomplete mental model. The page never documents
  what happens if `modalities` omits `"image"`.

### Claim 5: Through the LiteLLM Proxy the response mirrors the SDK — the `images` array sits inside `choices[0].message` alongside a `usage` block — so a proxy front-end passes the break through to its clients unchanged
- **Evidence**: The "Response format from proxy" JSON block, framed by the same
  "Key Change" diff (`"content": "base64-image-data..."` → `"images": [{...}]`).
- **Confidence**: settled (documented proxy response payload)
- **Quote**: (no direct quote; see the proxy response artifact in Concrete Artifacts)
- **Our assessment**: Buy. This is the operationally important scope statement:
  the proxy does not normalize the response back to the old shape, so the break
  reaches SDK, OpenAI-SDK-via-proxy, and raw-curl clients alike. A gateway
  operator who upgrades LiteLLM behind a proxy must coordinate client updates;
  there is no server-side translation layer preserving the previous field. The
  page documents no proxy-side compatibility option.

### Claim 6: The documented blast radius is two experimental model ids on `/chat/completions` — `gemini/gemini-2.0-flash-exp-image-generation` and `vertex_ai/gemini-2.0-flash-exp-image-generation`
- **Evidence**: The "Who is impacted" list.
- **Confidence**: settled (explicit vendor scope)
- **Quote**: "Anyone using the following models with /chat/completions:"
- **Our assessment**: Buy, and record it as a *scoping* fact rather than a
  reassurance: the change is confined to experimental image-generation ids, so
  most gateway traffic is unaffected — which is also why this class of break is
  easy to miss in fleet-wide monitoring, the same "subset-scoped regression
  invisible at aggregate level" shape as
  `failure-litellm-vllm-embeddings-encoding-format.md` Claim 3.

### Claim 7: The change is documented as a hard cutover — no rollback flag, no compatibility shim, no deprecation window — with v1.77.0 as the only version anchor
- **Evidence**: Full read of the page: there is no "rollback", "compatibility",
  "deprecat", or "flag" content anywhere; the only version reference is the
  v1.77.0 line in the Key Change callout.
- **Confidence**: settled (negative evidence from a complete read; the version
  anchor is positive)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Recorded as an absence, per the sibling LiteLLM docs-note
  pattern. The document tells an operator what changed and how to update, but
  documents no transition period, no env flag to restore the previous field, and
  no per-deployment opt-out. Combined with Claim 5 (the proxy passes it through),
  the practical consequence is that the only operator controls are "upgrade and
  update clients together" or "stay on the pre-change line" — which is exactly
  why this page attaches to the pin/patch-vs-line-move discipline (see
  Cross-References). We do not infer that no shim *exists*, only that this page
  documents none.

### Claim 8: The page is internally inconsistent about the **pre**-change access path — the info callout names a singular `response.choices[0].message.image`, while the worked "Before" code reads `response.choices[0].message.content`
- **Evidence**: The Key Change callout versus the "Before" code block (and the
  SDK key-change diff), both on the same page.
- **Confidence**: settled (both strings are on the page, verbatim, and mutually
  inconsistent)
- **Quote**: "instead of a single image in `response.choices[0].message.image`" / "base_64_image_data = response.choices[0].message.content"
- **Our assessment**: Recorded, not resolved, and not filed as a contradiction
  per MINER §4a: it is a documentation defect *within one page*, it does not
  change guide advice, and no existing source note takes an opposing position.
  The consequence is minor but real for a migrating operator — a reader cannot
  tell from this page whether their pre-upgrade code was reading a singular
  `message.image` field or scraping image bytes out of `message.content`; the two
  require different migration edits. The safest reading is that the "before"
  behavior was provider/version-dependent, which is itself a reason to assert
  the response shape after the bump rather than trust a drop-in edit.

### Claim 9: The proxy config example registers a model (`vertex_ai/gemini-2.5-flash-image-preview`) that is **not** in the impacted list, and the "Response Format" block is fenced as `python` while containing JSON
- **Evidence**: The `config.yaml` example's `vertex-image-gen` entry versus the
  "Who is impacted" list; the "Response Format" block's ` ```python ` fence
  around a JSON object.
- **Confidence**: settled (both are directly observable on the page)
- **Quote**: "model: vertex_ai/gemini-2.5-flash-image-preview"
- **Our assessment**: Recorded as a documentation-quality observation, consistent
  with the corpus's treatment of LiteLLM docs-page model-string drift
  (`docs-litellm-completion-web-search.md` Claim 16). The config example mixes a
  migration-impacted id (`gemini-image-gen`) with a non-impacted preview id
  (`vertex-image-gen`), so a reader cannot use the example as a definitive
  "affected vs unaffected" fixture. Minor on its own; worth knowing before
  treating the page's examples as a contract.

### Claim 10: This page is a concrete instance of a **minor gateway line bump silently changing the response contract** — the case the version-support discipline's "line moves need release-notes review" rule exists to catch
- **Evidence**: The page dates the change to v1.77.0 (a minor line), changes a
  response field with no shim, and offers no signal to a client that did not read
  the migration note; the corpus's version-support note states that a minor line
  move is where behavior can change and requires release-notes review.
- **Confidence**: emerging (synthesis across this page and
  `blog-litellm-version-support.md` Claim 7, not a statement either source makes
  about the other)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the extractable operator pattern the Prospector
  flagged. The corpus already carries the *rule* — patch-within-a-line is a
  drop-in, line moves are where you check the release notes. This page is a
  worked counterexample to the intuition that a "drop-in" version bump is
  behavior-preserving: v1.77.0 is a line move that renamed a response field, and
  nothing on the response tells an old client that it changed. The guide
  consequence is that the line-move checklist must include a **response-shape
  assertion per pinned line**, not just a request-parameter audit — the
  response-side counterpart to the request-side exact-wire rule at
  `guide/05-llm-ops-reliability.md:383`.

## Concrete Artifacts

All artifacts verbatim from the raw markdown endpoint
`https://docs.litellm.ai/docs/extras/gemini_img_migration.md` (front matter
`last_updated: "2026-10-14"`), fetched this session.

### Before / After access path (page, "Before and After")

```python
# Before
from litellm import completion

response = completion(
    model="gemini/gemini-2.0-flash-exp-image-generation",
    messages=[{"role": "user", "content": "Generate an image of a cat"}],
    modalities=["image", "text"],
)

base_64_image_data = response.choices[0].message.content
```

```python
# After
from litellm import completion

response = completion(
    model="gemini/gemini-2.0-flash-exp-image-generation",
    messages=[{"role": "user", "content": "Generate an image of a cat"}],
    modalities=["image", "text"],
)

# Image is now available in the response
image_url = response.choices[0].message.images[0]["image_url"]["url"]  # "data:image/png;base64,..."
```

Note the "Before" path reads `message.content`, while the Key Change callout
describes the old field as `message.image` (Claim 8).

### The image entry wire shape (page, "Response Format")

```
{
    "image_url": {
        "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
        "detail": "auto"
    },
    "index": 0,
    "type": "image_url"
}
```

### Proxy response format (page, "Response format from proxy")

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1704089632,
  "model": "gemini-image-gen",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here's an image of a cat for you!",
        "images": [{
          "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
            "detail": "auto"
          },
          "index": 0,
          "type": "image_url"
        }]
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```

### Proxy model config (page, "Configure your models in `config.yaml`")

```yaml
model_list:
  - model_name: gemini-image-gen
    litellm_params:
      model: gemini/gemini-2.0-flash-exp-image-generation
      api_key: os.environ/GEMINI_API_KEY
  - model_name: vertex-image-gen  
    litellm_params:
      model: vertex_ai/gemini-2.5-flash-image-preview
      vertex_project: your-project-id
      vertex_location: us-central1

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY  # Your proxy API key
```

The trailing spaces after `vertex-image-gen` are the page's own.

## Cross-References

**Candidates from `miner-related-notes.md`** (read before Cross-References per
MINER.md §4; all ten pre-computed candidates are cited or explicitly dismissed):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch TPM/RPM
  accounting and per-record token charging on `POST /v1/batches`; no
  chat-completions response field.
- `source-notes/docs-litellm-completion-web-search.md` — **Cited (Extends)**: its
  **Claim 1** feature matrix lists `/images/generations` as a supported endpoint
  "Gemini image models only" — the same vendor image-generation surface family,
  though that note documents search attached to image generation rather than the
  image output field on `/chat/completions`. Confirmed the two pages share the
  Gemini image-model surface without overlapping on this field.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: native Bedrock
  Invoke passthrough and SigV4→bearer auth swap; a passthrough route with no
  `message.images` content.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**: the
  `/v1/audio/transcriptions` feature matrix and per-request fallbacks. Adjacency
  only — it is the corpus's other non-text-modality endpoint note; no image
  output field, so nothing cited.
- `source-notes/docs-litellm-completion-input-params.md` — **Cited (Extends)**:
  its *Source Context* section explicitly declares "Does NOT cover: the response
  shape (that is `/completion/output`)", i.e. it owns the request surface and
  hands off the response surface. This note is an instance of the response
  surface drifting. Its Concrete Artifacts → **Multimodal `content` block types**
  section inventories the *input* `image_url` block, the request-side counterpart
  to this page's output `image_url` entry. (Cited by section name per MINER §4b:
  it is an artifact table, not a numbered claim.)
- `source-notes/docs-litellm-creating-adapters.md` — **Dismissed**: adapters are a
  bidirectional *format-translation* layer registered module-globally; a
  different mechanism and no image-response contract.
- `source-notes/docs-litellm-completion-web-fetch.md` — **Dismissed**: the
  Anthropic `web_fetch_20250910` server tool; unrelated capability.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session `max_iterations` / `max_budget_per_session` caps; no response shape.
- `source-notes/docs-google-sre-eliminating-toil.md` — **Dismissed**: toil
  taxonomy and the 50% cap. Retrieved lexically; no gateway-response content and
  no shared claim, so nothing cited.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Cited (Extends)**:
  its **Claim 2** documents a response-object shape nuance on the same
  `/chat/completions` family — top-level `usage` reflects executor tokens only,
  with advisor tokens reachable solely via `usage.iterations[]`. Both notes are
  about a response object carrying more structure than a naive client assumes;
  this page's parallel is "the response now carries a list of images the old
  parser never looked for."

**Additional cross-references found by searching `source-notes/` and `guide/`**
(the candidates file was not exhaustive):

- **Corroborates**:
  - `source-notes/docs-litellm-completion-output.md` **Claim 1** — that page
    presents itself as "the exact json output and type you can expect from all
    litellm `completion` calls for all models," yet documents a four-key envelope
    with `message` limited to `role`/`content` and does **not** document
    `message.images` anywhere. This page is direct evidence that the response
    envelope has a documented multimodal-output field the output page omits, so
    "the response contract page is complete" is false on a second axis beyond
    the `id`/`object`/`system_fingerprint`/`tool_calls` gaps that note already
    records.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` **Claim 9** —
    the response direction is lossy (`response.model` falls back to
    `"unknown-model"`, `stop_sequence` always `null`). Both notes document that
    LiteLLM's response fields are path- and version-dependent rather than a
    fixed envelope; different surface, same finding.
  - `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` **Claim 1**
    and **Claim 6** — the request-side counterpart and its regression guard:
    a gateway change validated against one behavior broke a sibling, and the
    defense was exact-wire assertions per backend. This page supplies the
    response-side instance of the same "a gateway change altered a wire contract
    a client relied on" class, and the same remedy — assert the exact payload —
    applies to the response field.
  - `source-notes/blog-litellm-version-support.md` **Claim 7** — the pin/patch vs
    line-move rule: "Patching within a line is a drop-in; moving up a line is
    where you'd check the release notes for changes." This page is a concrete
    v1.77.0 line move that changed response behavior, which is why the rule's
    "check the release notes" step is load-bearing, not ceremonial.
- **Contradicts**: **None.** No existing source note claims the Gemini image
  response shape is stable across v1.77.0, and no note takes an opposing position
  on response-field stability. The page's own internal inconsistency (Claim 8)
  is a within-page documentation defect that does not change guide advice, so per
  MINER §4a "when NOT to file" no contradiction issue was filed. Verified against
  `CONTRADICTIONS.md` (no `C-NNN` entries) and all open `contradiction`-labeled
  issues (#1633, #1597, #1593, #1591, #1565, #1562, #1550, #1548, #1534, #1517,
  #1514, #1486, #1462, #1461, #1408, #1352, #1338, #1322, #1307, #1150) — none
  touch Gemini image generation, `message.images`, or this page.
- **Extends**:
  - `source-notes/docs-litellm-completion-output.md` (the response-contract page)
    — this note adds the multimodal-output response field that page does not
    carry (Claim 1 there; Claim 2 here).
  - `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` — the
    request-side exact-wire rule (`guide/05-llm-ops-reliability.md:383`) gains a
    response-side twin (Claim 10 here).
  - `source-notes/blog-litellm-version-support.md` **Claim 7** — supplies a
    worked instance of the "line move = behavior can change" clause.
  - `source-notes/docs-litellm-completion-web-search.md` **Claim 1** — adds the
    `/images/generations` image surface to the picture this page's
    `/chat/completions` image output sits beside.
- **Novel**: First source note in the corpus covering: (1) the
  `message.image`→`message.images` response-field change on Gemini image
  generation (zero hits for `message.images` or
  `gemini-2.0-flash-exp-image-generation` across `source-notes/` and `guide/`);
  (2) the base64-data-URL image list as a `/chat/completions` response contract;
  and (3) a worked example of a **minor-line gateway bump that changed the
  response contract** — the response-side counterpart the corpus's gateway-drift
  material was missing.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "Parameter migration hazards"
  (`guide/05-llm-ops-reliability.md:327`)**: this section is currently
  request-side only ("audit existing request parameters against the model's
  supported set"). Add the **response-side mirror**: from LiteLLM v1.77.0 the
  Gemini image-generation models moved images from a single field to a list at
  `message.images`, so a client that kept reading the old path produced nothing
  while still receiving a 200 [Claims 1, 5]. Recommend the rule be stated
  symmetrically: when moving a gateway line, audit **response parsers and
  response-shape assertions** as well as request parameters, because a
  response-contract change breaks a client that never needs a request change.
- **Chapter 05 — "Pin to a supported line; separate patching from line moves"
  (`guide/05-llm-ops-reliability.md:79`)**: add that the line-move checklist must
  include a **response-shape assertion per pinned line**, using this page as the
  worked case — a minor bump (v1.77.0) renamed a response field with no rollback
  flag, no compatibility shim, and no deprecation window [Claims 1, 5, 7, 10].
  This sharpens the existing "check the release notes for changes" clause with a
  concrete, testable step.
- **Chapter 05 — "Provider parity in the shared forwarding path"
  (`guide/05-llm-ops-reliability.md:343`)**: the existing rule asserts the exact
  **request** wire payload per backend. Add the response-side counterpart: assert
  the exact response fields (not just that the call succeeded), because a
  response-field rename is invisible to a request-only assertion and to
  success-rate monitoring [Claims 1, 6, 10].
- **Chapter 02 (Observability)**: note that multimodal responses carry base64
  data URLs inside the response body [Claim 2], so any pipeline that logs or
  buffers full response bodies inherits a payload-size change at the same moment
  the field name changes — and that a field rename is not detectable from
  per-request success metrics [Claims 1, 6].

## Extraction Notes

- Source read in full twice: the rendered page
  (`https://docs.litellm.ai/docs/extras/gemini_img_migration`, HTTP 200) and the
  raw markdown endpoint (`.../gemini_img_migration.md`, HTTP 200, 5,716 bytes)
  which preserves the front matter, the exact code fences, and the `:::info`
  callout. All `Quote` fields are character-for-character contiguous fragments
  from the raw markdown; the prose date is unstated, and `date_published` is
  recorded as unknown with `last_checked` set to the front matter's
  `last_updated: "2026-10-14"`.
- No sub-pages were followed: the only outbound reference in the page body is the
  `llms.txt` docs index line (a navigation artifact), and the page declares no
  `related:` siblings. The migration note is self-contained.
- `miner-related-notes.md` candidates (ten) were each cited or dismissed in
  Cross-References per MINER.md §4. Additional cross-references (`completion-output`,
  `messages-to-responses-mapping`, `vllm-embeddings-encoding-format`,
  `blog-litellm-version-support`) were found by searching `source-notes/` and
  `guide/` directly. Every cited `Claim N` was re-read in its note before writing
  (§4b), and no cross-note quote is reproduced, so there is no cross-note
  quote-verification risk.
- **No contradiction issue filed.** The one candidate is the page's own
  within-page inconsistency about the pre-change access path (Claim 8 —
  `message.image` in the callout vs `message.content` in the code), which is a
  documentation defect that does not change guide advice and opposes no existing
  source note, so MINER §4a "when NOT to file" applies. Checked
  `CONTRADICTIONS.md` (no `C-NNN` entries) and all open `contradiction`-labeled
  issues — none cover this surface.
- `confidence_overall` set to `emerging`: the documented facts (the version, the
  field rename, the wire shape, the affected models) are settled first-party
  documentation, but the page is thin, carries no measurement or independent
  confirmation, and the guide value is our synthesis (the response-contract-drift
  pattern and its coupling to the line-move discipline). This matches the
  `emerging` rating on the sibling LiteLLM docs notes (#1540, #1609, #1401).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain.
