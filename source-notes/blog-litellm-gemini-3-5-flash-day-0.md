---
source_url: https://docs.litellm.ai/blog/gemini_3_5_flash
source_type: blog-post
title: "Day 0 Support: Gemini 3.5 Flash on LiteLLM"
author: "Sameer Kankute (SWE, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-05-19
date_extracted: 2026-07-20
last_checked: 2026-07-20
status: current
confidence_overall: emerging
issue: "#372"
---

# Day 0 Support: Gemini 3.5 Flash on LiteLLM

> A LiteLLM vendor announcement documenting how to run Gemini 3.5 Flash
> through the LiteLLM gateway — capturing the Gemini-specific parameter
> mapping (`reasoning_effort` → `thinkingLevel`), strict function-call
> round-tripping with thought signatures, Google's deprecation guidance
> for sampling parameters (`temperature`/`top_p`/`top_k`), and the standard
> LiteLLM Day-0 config template extended for a Google provider.

## Source Context

- **Type**: blog-post (vendor "Day 0 support" product announcement on
  `docs.litellm.ai/blog`), tagged `gemini`, `day 0 support`, `llms`.
- **Author credibility**: High for *how LiteLLM itself routes and configures
  the model* — authored by a LiteLLM SWE (Sameer Kankute) and the company's
  CEO (Krrish Dholakia) and CTO (Ishaan Jaffer), i.e. the maintainers of the
  gateway. The config/parameter-mapping detail is first-party documentation.
- **Scope**: Covers (1) Day-0 availability through a unified OpenAI-compatible
  interface, (2) Gemini-specific features: minimal thinking level, strict
  function calling with thought signatures, sampling parameter deprecation,
  (3) config.yaml examples for both direct Gemini API and Vertex AI, (4) Docker
  and pip deployment, (5) supported endpoints including `/v1/responses` and
  `/v1/generateContent`. Does NOT cover: production metrics, latency/throughput
  measurements, failure analysis, or any practitioner outcome — it is a
  launch/how-to post. Structurally follows the same LiteLLM "Day 0 Support"
  template as the Claude Day-0 posts (`blog-litellm-claude-fable-5-day-0.md`,
  `blog-litellm-claude-opus-4-8-day-0.md`, `blog-litellm-claude-opus-4-7-day-0.md`)
  but adapted for a Google/Gemini provider with provider-specific parameter
  quirks not present in the Claude notes.

## Extracted Claims

### Claim 1: LiteLLM supports Gemini 3.5 Flash on Day 0 behind an OpenAI-compatible interface, with both Gemini API key and Vertex AI authentication backends
- **Evidence**: Opening statement of the post; the `config.yaml` example shows
  two model entries — one via `gemini/gemini-3.5-flash` with a `GEMINI_API_KEY`
  and one via `vertex_ai/gemini-3.5-flash` with `vertex_project` and
  `vertex_location`.
- **Confidence**: settled (the vendor documenting its own supported routing;
  the config examples are concrete).
- **Quote**: "LiteLLM now supports `gemini-3.5-flash` with full day 0 support!"
- **Our assessment**: This is the same Day-0 enablement template as the Claude
  model posts, now covering a Google provider. The dual-backend setup (Gemini
  API key vs Vertex AI) is a structural difference from the Claude notes — those
  cover four backends (Anthropic, Azure, Vertex AI, Bedrock), while this post
  covers two (Gemini API + Vertex AI). Credible and concrete.

### Claim 2: New Gemini-specific features (thinking levels, strict function-call IDs, thought signatures) require LiteLLM `v1.87.0-dev.1` or above; cost tracking works on any current version
- **Evidence**: Stated as a highlighted note before the "What's New" section,
  with specific version pin.
- **Confidence**: settled (specific version requirement documented by the
  gateway maintainer).
- **Quote**: "Cost tracking works on any current LiteLLM version with no changes
  needed. To access new features like \"thinking levels, strict function-call
  IDs, and thought signatures,\" users need `v1.87.0-dev.1` or above."
- **Our assessment**: This is the same enablement pattern as the Claude Day-0
  posts — base functionality (cost tracking) on any version, but
  model-specific features on a specific build. The version tag `v1.87.0-dev.1`
  is a **Nightly Dev** build per the 4-tier release taxonomy documented in
  `blog-litellm-april-townhall-updates.md` (Claim 6). This is consistent with
  the Claude posts: Opus 4.7 shipped on stable, Fable 5 on RC, and this Gemini
  model ships on a Dev nightly — the Day-0 tag maturity varies by model timing.

### Claim 3: LiteLLM maps OpenAI `reasoning_effort` to Gemini's `thinkingLevel`, with the value `minimal` mapping directly; this is the only thinking level exposed for Gemini 3.5 Flash
- **Evidence**: "What's New → Minimal Thinking Level" section states the
  mapping explicitly with a crosswalk table and SDK/curl examples.
- **Confidence**: settled (specific parameter mapping documented by the gateway
  maintainer; the mapping is explicit and testable).
- **Quote**: "LiteLLM maps OpenAI `reasoning_effort` to Gemini's `thinkingLevel`
  — use `reasoning_effort=\"minimal\"`."
- **Our assessment**: This differs from the Claude Day-0 mapping in two ways.
  First, Claude maps `reasoning_effort` to `thinking: {type: "adaptive"}`, while
  Gemini maps it to `thinkingLevel`. Second, Claude supports a five-rung effort
  ladder (low/medium/high/xhigh/max), while this Gemini post only documents a
  single `minimal` value. This is a significant cross-provider parameter mapping
  asymmetry — a gateway operator normalizing across providers cannot assume the
  same `reasoning_effort` value set works on every backend.

### Claim 4: Gemini 3.5+ requires every `functionResponse` to carry the same `id` as the originating `functionCall`, including a thought-signature suffix; LiteLLM round-trips this through OpenAI `tool_calls[].id` / `tool_call_id`
- **Evidence**: "What's New → Strict Function Calling" section with a three-step
  walkthrough and curl examples showing the `TOOL_CALL_ID` extraction and reuse.
- **Confidence**: settled (specific API constraint with a concrete round-trip
  procedure documented by the gateway maintainer).
- **Quote**: "Gemini 3.5+ requires every `functionResponse` to include the same
  `id` as the originating `functionCall`, plus the matching function name.
  LiteLLM handles this round-trip through standard OpenAI fields:
  `tool_calls[].id` on the assistant message and the same value as
  `tool_call_id` on the tool result."
- **Our assessment**: This is a Gemini-specific constraint not present in the
  Claude Day-0 notes. The `id` field contains a thought-signature suffix
  (`__thought__<signature>`) that must be passed back unchanged. This is the
  most operationally novel detail in the post: agentic frameworks that
  construct their own `tool_call_id` values (rather than echoing the one the
  model returned) will silently break on Gemini 3.5+. The step-by-step
  procedure and the `jq`-driven ID extraction in the source are the concrete
  artifacts operators need. See Concrete Artifacts.

### Claim 5: Google recommends moving away from `temperature`, `top_p`, and `top_k` for Gemini 3.5+, favoring system-instruction-based sampling; LiteLLM emits deprecation warnings when these are passed
- **Evidence**: "What's New → Sampling Parameters" section states Google's
  guidance, the deprecation timeline, and LiteLLM's warning behavior.
- **Confidence**: emerging (Google's stated direction; the parameters still
  function currently but may be removed in a future API release).
- **Quote**: "Google recommends moving away from `temperature`, `top_p`, and
  `top_k` for Gemini 3.5+ and instead controlling sampling behavior through
  system instructions. These parameters still function currently but may be
  removed in a future API release. LiteLLM follows this same guidance —
  passing these parameters on Gemini 3+ models will generate a deprecation
  warning in the logs recommending system-instruction-based sampling."
- **Our assessment**: This is a paradigm shift worth flagging for gateway
  operators. Temperature/top_p/top_k are the standard sampling knobs across
  every major LLM provider. If Google removes them in a future release,
  multi-provider routing code that passes `temperature` unconditionally will
  either get a warning (current) or an error (future). The deprecation-warning
  pattern in LiteLLM is a useful intermediate signal — operators can grep for
  it in logs to audit which of their workloads depend on sampling parameters
  for Gemini 3+ models, before the parameters are removed entirely. This is
  entirely novel to the corpus — no existing note covers sampling-parameter
  deprecation.

### Claim 6: Gemini 3.5 Flash is deployed via the standard LiteLLM Day-0 Docker/pip pattern, with version pin `v1.87.0-dev.1`
- **Evidence**: "Deploy This Version" section with both Docker and pip commands.
- **Confidence**: settled (concrete deployment instructions from the vendor).
- **Quote**: "docker run -e STORE_MODEL_IN_DB=True -p 4000:4000 \\
  ghcr.io/berriai/litellm:v1.87.0-dev.1"
- **Quote**: "pip install litellm==1.87.0.dev1"
- **Our assessment**: Standard LiteLLM Day-0 deployment template, matching the
  pattern in the Claude Day-0 posts. The image tag `v1.87.0-dev.1` is a
  **Nightly Dev** build under the release-tag taxonomy from
  `blog-litellm-april-townhall-updates.md`. The Docker command includes
  `STORE_MODEL_IN_DB=True`, which is not present in all Claude Day-0 Docker
  examples — this extra flag enables database-backed model storage, relevant
  for operators who manage models via the LiteLLM UI rather than static config.

### Claim 7: The proxy `config.yaml` supports two authentication models for Gemini 3.5 Flash: direct Gemini API key and Vertex AI project-based auth
- **Evidence**: "Quick Start → Proxy — Step 1: Setup config.yaml" block with
  two model_list entries.
- **Confidence**: settled (first-party config documentation).
- **Quote**: (see Concrete Artifacts → config.yaml for the verbatim block)
- **Our assessment**: This dual-entry pattern (API key vs Vertex AI project
  auth) is unique among the Day-0 notes. The Claude notes cover four backends
  (Anthropic, Azure, Vertex AI, Bedrock) each with its own `api_key` or
  provider-specific auth. This Gemini post covers two backends, both from
  Google — one using a simple API key and the other using Vertex AI
  project/location credentials. The Vertex AI variant uses the
  `vertex_ai/gemini-3.5-flash` model prefix and `vertex_project`/`vertex_location`
  params, matching the established LiteLLM Vertex AI convention from the Claude
  notes.

### Claim 8: LiteLLM provides Gemini 3.5 Flash on four API endpoints: OpenAI-compatible chat completions, Responses API, Anthropic-compatible messages, and Google-native generateContent
- **Evidence**: "Supported Endpoints" section listing all four endpoints with
  checkmarks and feature notes.
- **Confidence**: settled (first-party documentation of supported routes).
- **Quote**: "LiteLLM provides full end-to-end support for Gemini 3.5 Flash on:
  ✅ `/v1/chat/completions` — OpenAI-compatible chat completions
  ✅ `/v1/responses` — OpenAI Responses API (streaming and non-streaming)
  ✅ `/v1/messages` — Anthropic-compatible messages endpoint
  ✅ `/v1/generateContent` — Google Gemini API compatible endpoint"
- **Our assessment**: The `/v1/responses` and `/v1/generateContent` endpoints
  are novel compared to the Claude Day-0 notes, which only document
  `/v1/chat/completions` and `/v1/messages`. The `/v1/responses` endpoint
  (OpenAI Responses API) is a newer OpenAI API surface, and the
  `/v1/generateContent` endpoint is the Google-native API passthrough. This
  means Gemini 3.5 Flash can be consumed through any of four API shapes,
  which is useful for teams standardizing on a particular API dialect.

### Claim 9: All four endpoints support streaming, function calling with thought signatures, multi-turn conversations, all Gemini 3-specific features, and full multimodal input (text, image, audio, video)
- **Evidence**: "Supported Endpoints" section feature list below the endpoint
  enumeration.
- **Confidence**: settled (first-party documentation of capability coverage;
  "full multimodal support" for audio/video is a specific claim unmatched in
  the Claude Day-0 notes).
- **Quote**: "All endpoints support: Streaming and non-streaming responses,
  Function calling with thought signatures, Multi-turn conversations, All Gemini
  3-specific features (thinking levels, thought signatures), Full multimodal
  support (text, image, audio, video)"
- **Our assessment**: The "full multimodal support (text, image, audio, video)"
  claim is notable as a differentiator from the Claude Day-0 notes — LiteLLM's
  Claude support does not claim video input through the same endpoints. This is
  a provider-specific capability difference: Gemini 3.5 Flash natively supports
  audio and video input, and LiteLLM passes that through unchanged. For gateway
  operators handling multimodal workloads, this makes Gemini 3.5 Flash the more
  capable option on this dimension.

## Concrete Artifacts

All artifacts below are extracted from the source page. Config keys, model IDs,
and parameter names in code spans are rendered as literal text from the page.
No words were added or removed.

### Proxy `config.yaml` for Gemini 3.5 Flash (verbatim)

```yaml
model_list:
  - model_name: gemini-3.5-flash
    litellm_params:
      model: gemini/gemini-3.5-flash
      api_key: os.environ/GEMINI_API_KEY  # Or use Vertex AI
  - model_name: vertex-gemini-3.5-flash
    litellm_params:
      model: vertex_ai/gemini-3.5-flash
      vertex_project: your-project-id
      vertex_location: us-central1
```

### Deploy commands (verbatim)

```
docker run -e STORE_MODEL_IN_DB=True -p 4000:4000 \
  ghcr.io/berriai/litellm:v1.87.0-dev.1

pip install litellm==1.87.0.dev1
```

### Minimal thinking level — proxy curl example (verbatim)

```
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR-LITELLM-KEY>" \
  -d '{
    "model": "gemini-3.5-flash",
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "reasoning_effort": "minimal"
  }'
```

### Strict function calling — Step 1: trigger tool call (verbatim)

```bash
curl -sS http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR-LITELLM-KEY>" \
  -d '{
    "model": "gemini-3.5-flash",
    "messages": [
      {
        "role": "user",
        "content": "What is the weather in Tokyo right now?"
      }
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get current weather for a city",
          "parameters": {
            "type": "object",
            "properties": {
              "city": { "type": "string" }
            },
            "required": ["city"]
          }
        }
      }
    ]
  }' | tee /tmp/gemini_tool_step1.json | jq .
```

Extract the tool call ID:

```bash
TOOL_CALL_ID=$(jq -r '.choices[0].message.tool_calls[0].id' /tmp/gemini_tool_step1.json)
echo "$TOOL_CALL_ID"
# e.g. 5x450f94__thought__EvACCu0CAQw51sdR...
```

### Strict function calling — Step 2: return tool result (verbatim)

```bash
WEATHER_RESULT='{"temp_c": 18, "condition": "clear"}'
curl -sS http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR-LITELLM-KEY>" \
  -d "$(jq -n \
    --arg id "$TOOL_CALL_ID" \
    --arg content "$WEATHER_RESULT" \
    '{
      model: "gemini-3.5-flash",
      messages: [
        {role: "user", content: "What is the weather in Tokyo right now?"},
        {
          role: "assistant",
          content: null,
          tool_calls: [{
            id: $id,
            type: "function",
            function: {name: "get_weather", arguments: "{\"city\": \"Tokyo\"}"}
          }]
        },
        {role: "tool", tool_call_id: $id, content: $content}
      ],
      tools: [{
        type: "function",
        function: {
          name: "get_weather",
          description: "Get current weather for a city",
          parameters: {
            type: "object",
            properties: {city: {type: "string"}},
            required: ["city"]
          }
        }
      }]
    }')" | jq .
```

### SDK quick-start (verbatim)

```python
from litellm import completion
response = completion(
    model="gemini/gemini-3.5-flash",
    messages=[{"role": "user", "content": "Summarize this article in 3 bullet points."}],
)
print(response.choices[0].message.content)
```

### SDK with minimal thinking (verbatim)

```python
from litellm import completion
response = completion(
    model="gemini/gemini-3.5-flash",
    messages=[{"role": "user", "content": "What's 2+2?"}],
    reasoning_effort="minimal",
)
print(response.choices[0].message.content)
```

## Cross-References

- **Corroborates**:
  - `blog-litellm-claude-fable-5-day-0.md` (Claim 1, Claim 10) — The Day 0
    Support template is structurally identical: a unified API interface, cost-map
    reload or explicit version pin to enable, per-provider `config.yaml`.
    The deploy commands follow the same pattern (`docker run` / `pip install`
    with a specific tag), and the supported-endpoints list overlaps on
    `/v1/chat/completions` and `/v1/messages`. This Gemini post is a third
    instance of the same template, now applied to a Google provider, confirming
    the pattern's provider-agnostic stability.
  - `blog-litellm-claude-opus-4-8-day-0.md` (Claim 10) — Same enablement pattern
    via version-pinned image and cost-map reload path.
  - `blog-litellm-april-townhall-updates.md` (Claim 6 — the 4-tier release-tag
    taxonomy) — This post's `v1.87.0-dev.1` tag is a **Nightly Dev** build under
    that taxonomy. Consistent with the pattern that Day-0 support lands on a
    pre-stable tag; the specific tier (Dev nightly) differs from Opus 4.7's
    Stable (`v1.83.3-stable`), Opus 4.8's Nightly (`v1.88.0-dev.1`), and
    Fable 5's Release Candidate (`v1.89.0-rc.2`), continuing the observation
    that tag maturity varies by model release timing.

- **Contradicts**: None. No contradiction issue filed. Verified against all
  existing source notes and `CONTRADICTIONS.md` (no open `C-NNN` entries).
  The cross-provider parameter mapping differences between this post and the
  Claude Day-0 notes (`reasoning_effort` → `thinkingLevel` vs → `thinking:
  {type: "adaptive"}`; single `minimal` value vs five-rung effort ladder) are
  **provider-specific conditioning variables** — different providers have
  different parameter surfaces. Per MINER.md §4, "Claims differ only in
  context … that's not a contradiction, that's a conditioning variable."

- **Extends**:
  - `blog-litellm-claude-fable-5-day-0.md` — This note adds the third data point
    in the "Day 0 model enablement" pattern, extending it from Anthropic/Claude
    models to Google/Gemini. It introduces provider-specific elements absent
    from the Claude notes: (1) `reasoning_effort` → `thinkingLevel` mapping
    (vs → adaptive thinking), (2) Gemini thought-signature round-tripping in
    tool call IDs (a constraint not present for Claude), (3) sampling parameter
    deprecation guidance, (4) the `/v1/responses` and `/v1/generateContent`
    endpoints, and (5) audio/video multimodal input support.
  - `blog-litellm-claude-opus-4-8-day-0.md` — Extends the same provider catalog
    expansion and the endpoint surface comparison.
  - `blog-litellm-claude-opus-4-7-day-0.md` — Same provider catalog extension.
  - `failure-litellm-wildcard-model-access-desync.md` — Like the Claude Day-0
    notes, this post's enablement procedure would rely on the
    `POST /reload/model_cost_map` path for operators using the default remote
    cost map (for `v1.87.0-dev.1` only — the new Gemini features require that
    specific version; the endpoint itself is unchanged). The wildcard-desync
    incident's lesson ("reload success ≠ end-to-end health") applies equally
    here: a reported-successful cost-map reload on an older version wouldn't
    enable the new thinking-level or function-call features.

- **Novel**: First source note in the corpus to capture:
  - **`reasoning_effort` → `thinkingLevel` mapping** — a cross-provider parameter
    mapping that differs structurally from the Claude adaptive-thinking mapping.
    Establishes that `reasoning_effort` is not a universal parameter whose
    behavior is consistent across providers.
  - **Single-value `minimal` thinking level** — while Claude supports a five-rung
    effort ladder, Gemini 3.5 Flash exposes only `minimal`. This asymmetry is
    significant for multi-provider routing: a workload asking for `high` effort
    on Gemini would get an error or no-op.
  - **Thought-signature round-tripping in tool call IDs** — the requirement to
    echo the exact `id` (including `__thought__<signature>` suffix) from the
    model's `tool_calls` back as `tool_call_id`. This is a Gemini-specific
    constraint with no Claude equivalent.
  - **Sampling parameter deprecation** — Google's stated direction to move away
    from `temperature`/`top_p`/`top_k` for Gemini 3.5+ in favor of
    system-instruction-based sampling. Entirely new to the corpus; no existing
    note discusses parameter deprecation at the provider level.
  - **Four-endpoint support including `/v1/responses` and `/v1/generateContent`**
    — the Claude Day-0 notes only document `/v1/chat/completions` and
    `/v1/messages`. The OpenAI Responses API endpoint and the Google-native
    passthrough are new to the corpus.
  - **Full audio/video multimodal support** — the claim of audio and video input
    through the LiteLLM gateway extends beyond what the Claude notes cover
    (text, image, PDF).
  - **First Google/Gemini provider Day-0 note** — all prior Day-0 notes cover
    Anthropic/Claude models. This extends the corpus's provider catalog.

## Guide Impact

- **Chapter 02 (LLM Gateway / Proxy configuration) / cross-provider parameter
  mapping**: Add that `reasoning_effort` is not a universal parameter — it maps
  to `thinkingLevel` on Gemini (vs adaptive thinking on Claude), and the value
  set differs (`minimal` on Gemini vs low/medium/high/xhigh/max on Claude). A
  gateway operator normalizing across providers needs provider-specific mapping
  tables, not a single `reasoning_effort` passthrough. This source provides the
  data point for Google/Gemini in that table.
- **Chapter 04 (Model Management & Deployment) / tool-call compatibility**: Add
  that Gemini 3.5+ requires strict tool_call_id round-tripping with thought
  signatures — the `id` from the model's `tool_calls` must be echoed verbatim
  in the `tool_call_id` of the tool result. Agentic frameworks or middleware
  that construct or transform `tool_call_id` values will break on Gemini.
  Document the extraction-and-reuse pattern shown in the source (Step 1: capture
  `TOOL_CALL_ID` via `jq`; Step 2: pass it back as `tool_call_id`).
- **Chapter 04 / sampling parameter management**: Add a note on Google's
  deprecation direction for `temperature`/`top_p`/`top_k` on Gemini 3.5+.
  Gateway operators should audit their Gemini 3+ workloads for reliance on
  these parameters and plan migration to system-instruction-based sampling.
  LiteLLM's deprecation warning in the logs is a useful signal for discovery.
- **Chapter 04 / gateway endpoint surface**: Add that LiteLLM now routes Gemini
  3.5 Flash through four API shapes, including `/v1/responses` (OpenAI Responses
  API) and `/v1/generateContent` (Google-native passthrough), in addition to the
  standard `/v1/chat/completions` and `/v1/messages`. This expands the
  gateway's endpoint catalog beyond what the Claude Day-0 notes document.
- **Chapter 04 / provider capability catalog**: Record that Gemini 3.5 Flash
  supports audio and video input through LiteLLM — a capability that the
  Anthropic/Claude models listed in existing notes do not claim. Useful for
  multimodal workload routing decisions.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/gemini_3_5_flash`, published May 19, 2026.
  Page fetched via `WebFetch` (HTML-to-text extraction) and cross-checked with
  a second prompt for verbatim passages. All quoted passages were copied from
  the rendered page text character-for-character.
- The page is self-contained (a single announcement with SDK and proxy
  examples). The "Newer post" / "Older post" sidebar links were not followed
  (unrelated topics). The sidebar enterprise callout is marketing copy, not
  extracted.
- `confidence_overall` set to `emerging`: the first-party config and
  parameter-mapping detail is effectively settled how-to documentation, but
  the post as a whole is a thin Day-0 announcement whose primary value is the
  Gemini-specific parameter quirks. The sampling-parameter deprecation guidance
  is stated as Google's direction (not LiteLLM's own assertion) and the
  parameters still function — the deprecation timeline is uncertain. This
  matches the `emerging` rating on the sibling LiteLLM Day-0 notes (Claude
  Fable 5, Opus 4.8, Opus 4.7).
- No contradiction issue filed: verified against all existing source notes and
  open contradiction-labeled issues on the repo. The parameter mapping
  differences between this note and the Claude Day-0 notes are cross-provider
  conditioning variables, not contradictions. The sampling-parameter deprecation
  is entirely novel — no note asserts that temperature/top_p/top_k are
  universally stable or permanently available.
- Novelty per triage: medium. The Day-0 Support template itself is now a
  well-documented pattern (three instances in the corpus). The novel, mineable
  content is the Gemini-specific operational detail — the `minimal` thinking
  level mapping, the thought-signature round-tripping constraint, the sampling
  parameter deprecation paradigm, and the expanded endpoint catalog including
  `/v1/responses` and `/v1/generateContent`.
- The page renders the byline date as "May 19, 2026"; recorded as
  `date_published: 2026-05-19`. The author byline reads "Sameer Kankute (SWE @
  LiteLLM, LLM Translation), Krrish Dholakia (CEO), and Ishaan Jaffer (CTO)".
  The author list is structurally similar to the Claude Day-0 posts (Sameer
  Kankute + Krrish Dholakia + Ishaan Jaffer), differing from the Fable 5 and
  Opus 4.8 posts which list Mateo Wang as first author instead of Sameer
  Kankute.
