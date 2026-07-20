---
source_url: https://docs.litellm.ai/blog/gemini_3_flash
source_type: blog-post
title: "DAY 0 Support: Gemini 3 Flash on LiteLLM"
author: "Sameer Kankute (SWE, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2025-12-17
date_extracted: 2026-07-20
last_checked: 2026-07-20
status: current
confidence_overall: emerging
issue: "#373"
---

# Day 0 Support: Gemini 3 Flash on LiteLLM

> A LiteLLM vendor announcement documenting Day-0 proxy support for Google's
> Gemini 3 Flash model. Unlike the Claude-model day-0 posts, this is a
> **cross-provider parameter translation** page — it shows how LiteLLM maps
> OpenAI's `reasoning_effort` to Google Gemini's `thinkingLevel`, how it handles
> Gemini-specific thought signatures (including a dummy-signature fallback for
> missing ones), and which API endpoints (/chat/completions, /responses,
> /messages, /generateContent) it exposes for this model.

## Source Context

- **Type**: blog-post (vendor "Day 0 Support" product announcement on
  `docs.litellm.ai/blog`), tagged `gemini`, `day 0 support`, `llms`.
- **Author credibility**: First-party LiteLLM documentation — authored by
  Sameer Kankute (SWE, LiteLLM), Krrish Dholakia (CEO, LiteLLM), and Ishaan
  Jaffer (CTO, LiteLLM), the gateway maintainers. The config, parameter
  mapping, and endpoint compatibility detail is authoritative for how LiteLLM
  itself routes requests for this model.
- **Scope**: Covers (1) Day-0 availability of `gemini-3-flash-preview`, (2) the
  new `thinkingLevel` parameter (MINIMAL, LOW, MEDIUM, HIGH) replacing
  `thinkingBudget`, (3) automatic mapping from OpenAI `reasoning_effort` to
  Gemini `thinkingLevel`, (4) thought signature handling with dummy fallback,
  (5) four supported endpoint types, (6) per-deployment-approach config
  examples (SDK / PROXY), and (7) the pinned version tag. Does NOT cover:
  pricing, production metrics, latency/throughput measurements, failure
  analysis, or any practitioner outcome — it is a launch/how-to post.

## Extracted Claims

### Claim 1: LiteLLM supports `gemini-3-flash-preview` on Day 0, including all new API changes
- **Evidence**: Opening statement of the post; the entire body then shows
  SDK and PROXY config examples using the `gemini/gemini-3-flash-preview` model
  ID with the new `thinkingLevel` parameter.
- **Confidence**: settled (the vendor documenting its own supported routing;
  the config examples are concrete).
- **Quote**: "LiteLLM now supports `gemini-3-flash-preview` and all the new API
  changes along with it."
- **Our assessment**: This is the same Day-0 enablement pattern documented in
  the existing Claude-model day-0 notes (Fable 5, Opus 4.8, Opus 4.7), now
  extended to a Google/Gemini model. Credible and concrete. The cross-provider
  dimension is new — LiteLLM routes a Google model through an OpenAI-compatible
  interface, which requires parameter translation not present in the
  same-provider (Anthropic/Claude) day-0 notes.

### Claim 2: Gemini 3 Flash introduces `thinkingLevel` (MINIMAL/MEDIUM/HIGH) replacing the older `thinkingBudget` parameter
- **Evidence**: Explicitly stated under "1. New Thinking Levels"; the version
  note at the top also flags that "thinking levels" require
  v1.80.8-stable.1 or above.
- **Confidence**: settled (first-party vendor documentation of a concrete API
  parameter change).
- **Quote**: "Gemini 3 Flash introduces granular thinking control with
  `thinkingLevel` instead of `thinkingBudget`."
- **Our assessment**: This is the specific Google API parameter change that
  a gateway operator must accommodate. Unlike the Claude side where
  `reasoning_effort` maps to an Anthropic-internal adaptive thinking mode,
  here `thinkingLevel` is a first-class Gemini API parameter with three named
  levels (MINIMAL, MEDIUM, HIGH). The `thinkingBudget` → `thinkingLevel`
  migration is analogous to the `thinking: {type: "enabled", budget_tokens: N}`
  → adaptive thinking change on the Claude side, but with different parameter
  names and semantics.

### Claim 3: LiteLLM automatically maps OpenAI's `reasoning_effort` parameter to Gemini's `thinkingLevel` values
- **Evidence**: Stated in the "1. New Thinking Levels" section; the full
  mapping table is provided at the bottom of the page under "`reasoning_effort`
  Mapping for Gemini 3+".
- **Confidence**: settled (concrete, tabular mapping published by the gateway
  maintainer; the mapping is testable).
- **Quote**: "LiteLLM automatically maps the OpenAI `reasoning_effort`
  parameter to Gemini's `thinkingLevel`, so you can use familiar
  `reasoning_effort` values (`minimal`, `low`, `medium`, `high`) without
  changing your code!"
- **Our assessment**: This is the load-bearing operational value of the post
  and the most novel claim for the corpus. The existing day-0 notes all
  document same-provider param mapping (OpenAI reasoning_effort → Claude
  adaptive thinking, which is Anthropic-API-native). This is the first
  documented instance of **cross-provider parameter translation** by the
  gateway: OpenAI's reasoning_effort → Google Gemini's thinkingLevel. The
  mapping table additionally shows that `disable` and `none` both resolve to
  `minimal` — an edge case not present in the Claude mapping (where effort
  values are strictly "low/medium/high/xhigh/max"). See the Concrete Artifacts
  section for the full table.

### Claim 4: LiteLLM handles Gemini thought signatures for tool calls, including dummy signature injection when signatures are missing
- **Evidence**: Stated under "2. Thought Signatures"; an explicit "Edge Case
  Handling" sub-note describes the dummy fallback.
- **Confidence**: settled (specific, documented gateway behavior for a known
  API edge case).
- **Quote**: "Like `gemini-3-pro`, this model also includes thought signatures
  for tool calls. LiteLLM handles signature extraction and embedding internally."
- **Quote**: "If thought signatures are missing in the request, LiteLLM adds a
  dummy signature ensuring the API call doesn't break"
- **Our assessment**: Thought signatures are a Gemini-specific concept
  (reasoning trace identifiers attached to tool calls) with no equivalent on
  the Anthropic/Claude side. The dummy-signature fallback is a concrete example
  of provider-specific edge-case handling in a gateway — LiteLLM is not merely
  passing through parameters but actively compensating for missing required
  fields. This is a novel pattern for the corpus: a gateway adding synthetic
  data to satisfy a provider's API contract. Operators should be aware that
  this injection happens transparently; if thought signatures are used for
  audit or tracing, the dummy signature will be indistinguishable from a real
  one in LiteLLM's response.

### Claim 5: LiteLLM exposes Gemini 3 Flash through four different endpoint types: OpenAI-compatible, Responses API, Anthropic-compatible, and Google Gemini native
- **Evidence**: Listed under "Supported Endpoints" as a bullet list with four
  endpoints, each with brief descriptions.
- **Confidence**: settled (first-party vendor documentation of supported
  endpoint routes).
- **Quote**: "LiteLLM provides full end-to-end support for Gemini 3 Flash on:"
- **Our assessment**: The multi-endpoint surface is broader than what the
  Claude-model day-0 notes document for their models. The Claude posts show
  examples only for `/v1/chat/completions` (OpenAI-compatible) and/or
  `/v1/messages` (Anthropic native); this Gemini post additionally lists
  `/v1/responses` (OpenAI Responses API) and `/v1/generateContent` (Google
  Gemini native). This establishes that the breadth of endpoint coverage varies
  by model provider in LiteLLM's Day-0 posts. Worth noting: the endpoint list
  includes the typo "Converstion" (should be "Conversion") as a listed feature.

### Claim 6: All four endpoints support streaming, function calling with thought signatures, multi-turn conversations, and provider-specific thinking param conversion
- **Evidence**: Sub-bullet list under "Supported Endpoints" enumerating shared
  capabilities.
- **Confidence**: settled (first-party documentation of supported features per
  endpoint).
- **Quote**: "All endpoints support: Streaming and non-streaming responses /
  Function calling with thought signatures / Multi-turn conversations / All
  Gemini 3-specific features / Converstion of provider specific thinking
  related param to thinkingLevel"
- **Our assessment**: The fifth bullet ("Converstion of provider specific
  thinking related param to thinkingLevel") is the cross-provider parameter
  translation from Claim 3, listed here as an endpoint-level feature. The typo
  ("Converstion") is reproduced verbatim from the source. The functional claim
  is that regardless of which endpoint convention a caller uses, the
  `reasoning_effort` → `thinkingLevel` mapping applies uniformly.

### Claim 7: The model requires v1.80.8-stable.1 (Docker) or v1.80.8.post1 (Pip) for thinking levels support, though basic cost tracking works on any version
- **Evidence**: Version note at the top of the post plus explicit deploy
  commands with versioned image tags.
- **Confidence**: settled (named, published image and package versions).
- **Quote**: "if you want the support for new features introduced along with it
  like thinking levels, you will need to use v1.80.8-stable.1 or above."
- **Our assessment**: Unlike the Claude day-0 notes which ship on varying image
  maturity tiers (Fable 5: `v1.89.0-rc.2` RC; Opus 4.8: `v1.88.0-dev.1`
  Nightly; Opus 4.7: `v1.83.3-stable` Stable), this Gemini 3 Flash post pins to
  `v1.80.8-stable.1`, a Stable tag. The post also notes that basic cost
  tracking works without upgrading — only the new features (thinking levels)
  require the pin. This is the first day-0 note to explicitly separate
  "cost tracking" from "feature enablement" in its version guidance.

### Claim 8: When using this model via Vertex AI, only the `global` location is supported
- **Evidence**: A `note` block at the bottom of the page states the location
  constraint.
- **Confidence**: settled (explicit first-party constraint documented by the
  vendor).
- **Quote**: "If using this model via vertex_ai, keep the location as global as
  this is the only supported location as of now."
- **Our assessment**: This is a deployment-specific constraint not present in
  any of the existing Claude day-0 notes. It affects operators who route
  through Vertex AI and may have regional data residency requirements; the
  `global` endpoint may not satisfy all compliance zones. This is analogous in
  spirit to the Bedrock inference-profile-prefix requirement in the Fable 5
  note (Claim 11) — a provider-specific deployment constraint that a gateway
  operator must know.

### Claim 9: Gemini 2.5 models continue using `thinkingBudget` — the change only applies to Gemini 3+ models
- **Evidence**: Listed as the fourth bullet in "Key Features".
- **Confidence**: settled (explicit backward-compatibility statement from the
  vendor).
- **Quote**: "Backward Compatible: Gemini 2.5 models continue using
  `thinkingBudget`"
- **Our assessment**: This establishes that the `thinkingLevel` vs
  `thinkingBudget` split is a version-boundary change (Gemini 2.5 → Gemini 3+),
  not a global Google API change. A gateway operator routing mixed Gemini
  model versions must use different thinking parameters depending on the model
  version. This is directly analogous to the Claude side where
  adaptive-thinking-only models (Fable 5, Opus 4.8, Opus 4.7) coexist with
  older models that accept explicit `thinking` budgets.

## Concrete Artifacts

All artifacts below are extracted from the source page. Inline-code spans in
the rendered page (parameter names, model IDs) are reproduced as they read on
the page.

### `reasoning_effort` → `thinkingLevel` mapping table (verbatim)

```
reasoning_effort  thinking_level
minimal           minimal
low               low
medium            medium
high              high
disable           minimal
none              minimal
```

### Deploy commands (verbatim from the page tabs)

```docker
docker run \
  -e STORE_MODEL_IN_DB=True \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-v1.80.8-stable.1
```

```pip
pip install litellm==1.80.8.post1
```

### SDK code example with MEDIUM thinking (verbatim)

```python
from litellm import completion

# No need to make any changes to your code as we map openai reasoning param to thinkingLevel
response = completion(
    model="gemini/gemini-3-flash-preview",
    messages=[{"role": "user", "content": "Solve this complex math problem: 25 * 4 + 10"}],
    reasoning_effort="medium",  # NEW: MEDIUM thinking level
)
print(response.choices[0].message.content)
```

### PROXY config.yaml (verbatim)

```yaml
model_list:
  - model_name: gemini-3-flash
    litellm_params:
      model: gemini/gemini-3-flash-preview
      api_key: os.environ/GEMINI_API_KEY
```

### PROXY curl example (verbatim)

```
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR-LITELLM-KEY>" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [{"role": "user", "content": "Complex reasoning task"}],
    "reasoning_effort": "medium"
  }'
```

### Key Features list (verbatim)

```
✅ Thinking Levels: MINIMAL, LOW, MEDIUM, HIGH
✅ Thought Signatures: Track reasoning with unique identifiers
✅ Seamless Integration: Works with existing OpenAI-compatible client
✅ Backward Compatible: Gemini 2.5 models continue using thinkingBudget
```

### Upgrade / usage snippet (verbatim)

```
pip install litellm --upgrade

import litellm
from litellm import completion
response = completion(
    model="gemini/gemini-3-flash-preview",
    messages=[{"role": "user", "content": "Your question here"}],
    reasoning_effort="medium",  # Use MEDIUM thinking
)
print(response)
```

## Cross-References

- **Corroborates**:
  - `blog-litellm-claude-fable-5-day-0.md` — The Day-0 Support template is
    structurally identical: vendor announcement, version-pinned deploy commands,
    multi-provider config examples, parameter mapping table, and supported
    endpoint documentation. This Gemini 3 Flash post is a third instance (after
    Fable 5 and Opus 4.8/4.7) of the same template, now applied to a
    Google/Gemini model.
  - `blog-litellm-claude-opus-4-8-day-0.md` — Same template; also corroborates
    that the Day-0 post format varies in scope by model (this Gemini post adds
    thought signatures and a location constraint that the Claude posts lack).
  - `blog-litellm-claude-opus-4-7-day-0.md` — Earliest template instance;
    this Gemini post shares its per-provider config and parameter-mapping
    structure but adds provider-specific sections (Vertex AI location,
    thought signatures) absent from the earlier Claude-only template.

- **Contradicts**: None. No contradiction issue filed. Verified against all
  existing source notes and open contradiction-labeled issues (none found).
  This is a new model (Google Gemini 3 Flash) with no existing note making
  opposing claims about its LiteLLM support. The differences from the Claude
  day-0 notes (different parameter mapping, different endpoints, different
  edge cases) are model- and provider-specific variation, not contradiction.

- **Extends**:
  - `blog-litellm-claude-fable-5-day-0.md`, `blog-litellm-claude-opus-4-8-day-0.md`,
    `blog-litellm-claude-opus-4-7-day-0.md` — Extends the "Day 0 Support"
    pattern corpus with a **cross-provider** instance (Google/Gemini instead of
    Anthropic/Claude). The existing notes all document same-provider routing
    (Claude through an OpenAI-compatible interface); this note adds
    cross-provider parameter translation (`reasoning_effort` → `thinkingLevel`),
    a new parameter scheme (`thinkingLevel` instead of `thinkingBudget`), a
    new provider-specific edge case (thought signature dummy injection), and a
    broader endpoint surface (4 endpoint types vs 1-2 in the Claude posts).
  - `failure-litellm-wildcard-model-access-desync.md` — As with all Day-0
    posts, an operator following this post's enablement instructions would use
    `POST /reload/model_cost_map` (the default path) or pull a new image (the
    local cost-map path). The wildcard-desync incident's lesson ("reload success
    ≠ end-to-end health") applies: a successful cost-map reload does not prove
    the model is reachable. A post-enablement end-to-end health check is
    recommended.
  - `blog-litellm-april-townhall-updates.md` (Claim 6 — the 4-tier release-tag
    taxonomy) — This post ships on `v1.80.8-stable.1`, a **Stable** tag. This
    is the second Stable-tagged Day-0 instance in the corpus (after Opus 4.7's
    `v1.83.3-stable`), continuing the pattern that Day-0 support can land on
    Stable, RC (Fable 5), or Nightly (Opus 4.8) tags depending on release
    timing.

- **Novel**: First source note in the corpus to capture:
  - **Cross-provider parameter translation** by an LLM gateway: OpenAI's
    `reasoning_effort` → Google Gemini's `thinkingLevel`. The existing notes
    all document same-provider mapping (OpenAI param → Claude-native feature).
    This establishes that LiteLLM's parameter mapping responsibility spans
    provider boundaries.
  - **Provider-specific edge-case compensation**: LiteLLM injecting a dummy
    thought signature when the Gemini API requires one but the request lacks
    it. This is a novel gateway behavior pattern — actively compensating for
    missing required fields — with audit/tracing implications.
  - **`disable`/`none` → `minimal` fallback mapping**: The `reasoning_effort`
    mapping table maps `disable` and `none` to `minimal`. This is an edge case
    not present in the Claude mapping (which has no "disable reasoning" value).
  - **Four-endpoint surface for a single model**: `/v1/chat/completions`,
    `/v1/responses`, `/v1/messages`, `/v1/generateContent` — broader than
    the 1-2 endpoints shown in any Claude day-0 post.
  - **Vertex AI location constraint**: `global` only — a deployment-specific
    constraint analogous to the Bedrock inference-profile requirement in the
    Fable 5 note but for a different provider's cloud platform.
  - **Version-gated feature enablement**: The post explicitly separates "cost
    tracking" (works on any version) from "feature enablement" (requires
    v1.80.8-stable.1), a distinction not made in the Claude day-0 notes.
  - **Backward compatibility boundary**: The `thinkingBudget` → `thinkingLevel`
    change is model-version-gated (Gemini 2.5 vs Gemini 3+), establishing that
    parameter migration is a model-generation boundary, not a global API change.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) / cross-provider parameter mapping**: Add
  that an LLM gateway may need to translate reasoning/thinking parameters
  **across** providers, not just from one standard interface (OpenAI) to a
  single backend. The `reasoning_effort` → `thinkingLevel` mapping is a
  concrete example: a gateway operator supporting both Claude and Gemini models
  behind one OpenAI-compatible interface will route the same `reasoning_effort`
  value to different parameter names (`thinking: {type: "adaptive"}` for Claude,
  `thinkingLevel: "medium"` for Gemini). The mapping table also shows that
  `disable`/`none` resolve to `minimal` — a fallback for effort-disabling
  values that the Claude side may handle differently. Recommend documenting
  that parameter translation is provider- and model-specific, not one-to-one.
- **Chapter 05 / gateway edge-case handling**: Add the thought-signature dummy
  injection pattern as an example of a gateway compensating for a
  provider-specific API requirement. Note the audit/tracing implication: if
  thought signatures are used for request tracing or compliance, dummy
  signatures injected by the gateway are indistinguishable from real ones in
  the response. Operators should know this injection happens transparently.
- **Chapter 05 / multi-endpoint routing**: Add that a single model may be
  exposed through multiple API convention endpoints (OpenAI, Responses API,
  Anthropic-compatible, Google native) by the same gateway. The feature
  surface (streaming, function calling, multi-turn) is consistent across
  endpoints, but the parameter names differ per endpoint convention.
- **Chapter 05 / model enablement checklist**: Add the Vertex AI location
  constraint (`global` only) as an item in the provider-specific deployment
  checklist. Operators with regional data residency requirements should verify
  location support before enabling a model on Vertex AI.
- **Chapter 05 / version guidance**: Add that some Day-0 posts distinguish
  between "cost tracking" (works on any version) and "feature enablement"
  (requires a specific pin). An operator who only wants to track spend on a
  new model may not need to upgrade; one who needs the full feature surface
  does. This is a nuance not present in the Claude day-0 notes, which present
  enablement as all-or-nothing.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/gemini_3_flash`, published December 17, 2025.
  Fetched via HTTP (curl) and processed by HTML-to-text extraction. All quoted
  passages were copied character-for-character from the rendered page text.
- The page is self-contained (a single announcement with SDK/PROXY tabs). The
  only substantive outbound link is "Learn more about thought signatures"
  pointing to `/blog/gemini_3#thought-signatures` — not followed because it
  documents a different model's (gemini-3-pro) thought signature behavior, not
  LiteLLM-specific content.
- `confidence_overall` set to `emerging`: the first-party config, parameter
  mapping, and endpoint detail is effectively settled how-to, but the post is
  a vendor announcement tied to a specific model release and image version
  (v1.80.8-stable.1) that may change. This matches the `emerging` rating on
  all three sibling LiteLLM day-0 notes.
- Novelty per triage: low (a standard "Day 0 Support" announcement repeating
  the same template). This extraction found higher novelty than the Prospector
  assessed because the existing corpus only documents Claude-model day-0 posts;
  this is the first Google/Gemini instance and introduces cross-provider
  parameter translation, a provider-specific edge case (thought signature
  dummy injection), a broader endpoint surface, and a Vertex AI location
  constraint — all new to the corpus.
- No contradiction issue filed: verified against all existing source notes and
  open contradiction-labeled issues (none found). This post documents a
  different model from a different provider; its differences from the Claude
  day-0 notes are model- and provider-specific variation, not contradiction.
