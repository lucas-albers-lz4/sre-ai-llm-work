---
source_url: https://docs.litellm.ai/blog/gpt_5_5
source_type: blog-post
title: "Day 0 Support: GPT-5.5 and GPT-5.5 Pro"
author: "Mateo Wang (AI Engineer, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-04-24
date_extracted: 2026-07-22
last_checked: 2026-07-22
status: current
confidence_overall: emerging
issue: "#419"
---

# Day 0 Support: GPT-5.5 and GPT-5.5 Pro

> A LiteLLM vendor announcement for OpenAI GPT-5.5 and GPT-5.5 Pro Day 0
> support. Operationally novel within the Day-0 template corpus for three
> patterns: (1) **no Docker image upgrade needed** — the model routes through
> the existing `OpenAIGPT5Config`, a backward-compatible enablement pattern,
> (2) a **transparent completion-to-Responses API bridge** for the Pro variant
> (the first documented instance of this LiteLLM feature), and (3) **per-model
> reasoning effort caps with local enforcement** via `UnsupportedParamsError`.

## Source Context

- **Type**: blog-post (vendor "Day 0 support" product announcement on
  `docs.litellm.ai/blog`), tagged `openai`, `gpt-5.5`, `gpt-5.5-pro`,
  `completion`, `day 0 support`.
- **Author credibility**: High for *how LiteLLM itself routes and configures
  the model* — authored by a LiteLLM AI Engineer (Mateo Wang) and the
  company's CEO (Krrish Dholakia) and CTO (Ishaan Jaffer), i.e. the
  maintainers of the gateway. The config and parameter-mapping detail is
  first-party documentation. Model-capability claims ("smartest and most
  intuitive to use model") are attributed to OpenAI.
- **Scope**: Covers (1) Day-0 availability through LiteLLM, (2) configuration
  via `config.yaml`, Docker, curl, and Python SDK, (3) the observation that
  no Docker image upgrade is needed, (4) per-model reasoning effort tables,
  (5) the Responses API bridge for GPT-5.5 Pro, and (6) cost-map reload
  enablement. Does NOT cover: production metrics, latency/throughput
  measurements, failure analysis, or any practitioner outcome — it is a
  launch/how-to post structurally following the same LiteLLM "Day 0 Support"
  template as the other Day-0 notes (6+ instances in the corpus).

## Extracted Claims

### Claim 1: LiteLLM supports GPT-5.5 and GPT-5.5 Pro on Day 0 through the existing `OpenAIGPT5Config` — no Docker image upgrade is needed
- **Evidence**: Opening statement of the post; a dedicated "note" callout states
  explicitly that no upgrade is needed because the model routes through an
  existing configuration class.
- **Confidence**: settled (the vendor documenting its own supported routing;
  the claim is concrete and testable).
- **Quote**: "No Docker image upgrade needed. GPT-5.5 routes through the
  existing `OpenAIGPT5Config` in LiteLLM, so any recent version works out of
  the box."
- **Our assessment**: This is the most operationally novel detail in the post.
  Every prior Day-0 post (Claude Opus 4.7, Opus 4.8, Fable 5, Gemini 3.5 Flash,
  GPT-5.3-Codex) required a specific version-pinned Docker image. This post is
  the first in the corpus to document that a model can be enabled on *any*
  recent LiteLLM proxy version with just a cost-map reload. The enablement cost
  (operator effort) varies meaningfully per model — some require a container
  restart with a new image, others only a button click. This is a new data point
  for the model enablement workflow in Chapter 05.

### Claim 2: GPT-5.5 supports both `/v1/chat/completions` and `/v1/responses` endpoints; GPT-5.5 Pro is Responses API-only
- **Evidence**: The post shows a curl example targeting
  `/v1/chat/completions` for GPT-5.5 and a separate curl example targeting
  `/v1/responses`. The Pro variant notes state
  `mode: "responses"` explicitly.
- **Confidence**: settled (concrete endpoint examples in the vendor's own
  documentation).
- **Quote**: (no single direct quote captures both endpoints; the
  `/chat/completions` curl targets `http://0.0.0.0:4000/chat/completions`,
  and the Responses API curl targets `http://0.0.0.0:4000/v1/responses`)
- **Our assessment**: This dual-endpoint support within a single model family
  contrasts with GPT-5.3-Codex (`blog-litellm-gpt-5-3-codex-day-0.md`), which
  was exclusively `/v1/responses` with no alternative. Operators routing
  GPT-5.5 standard can use `/chat/completions` (keeping existing client code
  unchanged), while GPT-5.5 Pro requires the Responses API path — or benefits
  from the transparent bridge (Claim 3). The routing catalog in Chapter 05
  should note that endpoint exclusivity is per-model, not per-model-family.

### Claim 3: LiteLLM's Responses API bridge transparently translates `completion()` SDK calls to `/v1/responses` for Responses-only models
- **Evidence**: Explicit statement in the post's "Notes" section.
- **Confidence**: settled (first-party documentation of the gateway's own
  translation behavior).
- **Quote**: "gpt-5.5-pro is a Responses API-only model (`mode: \"responses\"`).
  LiteLLM's Responses API bridge transparently translates `completion()` calls
  to `/v1/responses`, so the SDK example above works without code changes."
- **Our assessment**: This is a new LiteLLM capability not documented in any
  prior Day-0 note. GPT-5.3-Codex was also Responses API-only (`/v1/responses`)
  but its post showed the OpenAI Responses API client (`client.responses.create()`)
  directly — there was no SDK bridge. Here, LiteLLM automatically translates
  the familiar `completion()` call to the Responses API under the hood. This
  means operators of GPT-5.5 Pro can use the same `completion()` SDK calls they
  already have, with no client-side code changes, even though the model uses a
  different wire protocol. This is a meaningful improvement in the gateway's
  abstraction layer — the bridge absorbs API surface fragmentation so client
  code doesn't have to.

### Claim 4: Per-model reasoning effort defaults and allowed values differ between GPT-5.5 and GPT-5.5 Pro, with local enforcement
- **Evidence**: A table of values "verified against OpenAI's live API on
  2026-04-24" and an explicit enforcement note.
- **Confidence**: settled (verified against OpenAI's live API; the table is
  concrete and testable).
- **Quote** (table extracted as rendered on page):
  "| Model | Default | Allowed values |
  |---|---|---|
  | `gpt-5.5` | `medium` | `none`, `low`, `medium`, `high`, `xhigh` |
  | `gpt-5.5-pro` | `high` | `medium`, `high`, `xhigh` |"
- **Quote**: "LiteLLM enforces these caps locally — passing an unsupported
  value (e.g. `minimal`) raises an `UnsupportedParamsError` instead of
  round-tripping to OpenAI for a 400."
- **Our assessment**: Two notable observations. First, the two GPT-5.5 variants
  have *different* defaults and *different* allowed ranges — GPT-5.5 offers
  five levels including `none` and `low` (casual/light use), while GPT-5.5 Pro
  omits those and starts at `medium`, defaulting to `high`. This is the first
  time in the corpus that reasoning effort defaults differ between model
  variants within the same release. Second, the local enforcement via
  `UnsupportedParamsError` is a change from the implicit "let the API reject it"
  pattern — LiteLLM now validates before sending. For gateway operators, this
  means faster error feedback but also means the error surface shifts from
  OpenAI API errors to LiteLLM errors, which may have different monitoring and
  alerting paths.

### Claim 5: Long-context pricing tier kicks in above 272K tokens — the first mention of a tier threshold in any Day-0 note
- **Evidence**: Single sentence in the "Notes" section.
- **Confidence**: settled (explicitly stated in the vendor documentation).
- **Quote**: "Context window: 1.05M input tokens / 128K output tokens.
  Long-context tier pricing kicks in above 272K tokens."
- **Our assessment**: This is the first mention of a pricing tier threshold in
  any Day-0 note in the corpus. No prior model documentation included a token
  threshold at which pricing changes. For capacity planners operating at high
  throughput, this means the effective per-token cost for GPT-5.5 varies by
  input length — prompts above 272K tokens incur a higher rate. The model's
  total context window (1.05M input / 128K output) is also the largest
  documented in the corpus for an OpenAI model, surpassing the standard 128K
  input windows seen in earlier notes.

### Claim 6: GPT-5.5 supports reasoning, function calling, parallel tool calls, vision, PDF input, prompt caching, web search, and structured output
- **Evidence**: A capability list in the "Notes" section.
- **Confidence**: settled (standard spec list from the vendor).
- **Quote**: "GPT-5.5 supports reasoning, function calling, parallel tool calls,
  vision (image input), PDF input, prompt caching, web search, and structured
  output — see the OpenAI provider docs for advanced usage."
- **Our assessment**: Standard capability enumeration. Web search support is
  notable — it is not universally available across OpenAI models in the corpus
  and may have rate-limitting or reliability implications for gateway operators
  routing high volumes of search-enabled requests. The prompt caching mention
  connects to the existing literature on cache-invalidation incidents.

### Claim 7: GPT-5.5 and GPT-5.5 Pro are not yet available on Azure — OpenAI direct only
- **Evidence**: Explicit statement at the end of the "Notes" section.
- **Confidence**: settled (stated explicitly; absence on Azure is a fact, not
  an opinion).
- **Quote**: "Azure availability: not yet — this post covers OpenAI direct only."
- **Our assessment**: A straightforward constraint. Azure-only customers cannot
  adopt GPT-5.5 through LiteLLM at launch. This limits the deployment surface
  for organizations that exclusively use Azure OpenAI. The timing of Azure
  availability tends to lag OpenAI direct by weeks to months, consistent with
  patterns observed in prior model launches.

### Claim 8: The recommended Docker image is the general stable release `v1.83.7-stable` — not a model-pinned tag
- **Evidence**: The Docker pull and run commands specify this exact image tag.
- **Confidence**: settled (concrete deploy instruction from the vendor).
- **Quote**: "`ghcr.io/berriai/litellm:v1.83.7-stable`"
- **Our assessment**: This is a general stable image tag, unlike GPT-5.3-Codex's
  model-pinned tag (`v1.81.12-stable.gpt-5.3`). Combined with Claim 1 (no
  upgrade needed), the fact that the example *still* specifies a concrete stable
  tag suggests the tag is a recommendation for new deployments rather than a
  requirement — existing deployments on any v1.76.0+ image work without changes.
  Note: `v1.83.7-stable` also contains the fix for CVE-2026-42208 (SQL injection
  in the proxy), though the post does not mention this.

## Concrete Artifacts

All artifacts below are extracted from the source page. Inline-code spans in
the rendered page (e.g. YAML keys, model IDs) are reproduced as rendered.

### Proxy `config.yaml` (verbatim)

```yaml
model_list:
  - model_name: gpt-5.5
    litellm_params:
      model: openai/gpt-5.5
      api_key: os.environ/OPENAI_API_KEY
  - model_name: gpt-5.5-pro
    litellm_params:
      model: openai/gpt-5.5-pro
      api_key: os.environ/OPENAI_API_KEY
```

### Docker run command (verbatim)

```bash
docker run -d \
  -p 4000:4000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/config.yaml:/app/config.yaml \
  ghcr.io/berriai/litellm:v1.83.7-stable \
  --config /app/config.yaml
```

### curl test — chat completions (verbatim)

```bash
curl -X POST "http://0.0.0.0:4000/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -d '{
    "model": "gpt-5.5",
    "messages": [
      {"role": "user", "content": "Write a Python function to check if a number is prime."}
    ]
  }'
```

### curl test — Responses API (verbatim)

```bash
curl -X POST "http://0.0.0.0:4000/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -d '{
    "model": "gpt-5.5",
    "input": "Plan and write a Python script that scrapes a webpage and summarizes it."
  }'
```

### LiteLLM SDK — GPT-5.5 (verbatim)

```python
from litellm import completion

response = completion(
    model="openai/gpt-5.5",
    messages=[
        {"role": "user", "content": "Write a Python function to check if a number is prime."}
    ],
)
print(response.choices[0].message.content)
```

### LiteLLM SDK — GPT-5.5 Pro (verbatim)

```python
# GPT-5.5 Pro
response = completion(
    model="openai/gpt-5.5-pro",
    messages=[
        {"role": "user", "content": "Prove that the sum of two odd integers is even."}
    ],
)
print(response.choices[0].message.content)
```

### Reasoning effort table (verbatim as rendered)

| Model | Default | Allowed values |
|---|---|---|
| `gpt-5.5` | `medium` | `none`, `low`, `medium`, `high`, `xhigh` |
| `gpt-5.5-pro` | `high` | `medium`, `high`, `xhigh` |

### Reasoning effort Python example (verbatim)

```python
from litellm import completion

response = completion(
    model="openai/gpt-5.5",
    messages=[{"role": "user", "content": "Solve: what is the optimal strategy for..."}],
    reasoning_effort="high",
)
```

### Cost-map reload note (verbatim)

> "For cost tracking on gpt-5.5 and gpt-5.5-pro, hit the Reload Model Cost Map
> button in the Admin UI (or POST /reload/model_cost_map). Works on any LiteLLM
> version v1.76.0 or newer — no container restart or image upgrade required."

## Cross-References

- **Corroborates**:
  - `blog-litellm-gpt-5-3-codex-day-0.md` (Claim 2 — `/v1/responses` endpoint
    support). Both GPT-5.3-Codex and GPT-5.5 Pro access the Responses API;
    this post adds GPT-5.5 standard as a dual-endpoint model. The Day-0
    template (config.yaml, Docker, curl, SDK examples) is structurally
    identical across both posts, confirming the template's stability.
  - All other LiteLLM Day-0 notes — same Day-0 template pattern across models
    and providers, each with per-model operational detail.
  - `blog-litellm-claude-opus-4-8-day-0.md` (Claim 10 — cost-map reload
    enablement). The same `POST /reload/model_cost_map` path is the
    recommended enablement procedure. This post additionally notes that cost
    tracking requires `v1.76.0` or newer.
  - `failure-litellm-wildcard-model-access-desync.md` — The cost-map reload
    path is the same endpoint whose partial-reload desync was the subject of
    that incident report. The caution applies: reload success ≠ end-to-end
    health.

- **Contradicts**: None. No contradiction issue filed. Verified against all
  existing source notes and `CONTRADICTIONS.md` (no open `C-NNN` entries).
  The different endpoint patterns (GPT-5.3-Codex: exclusive `/v1/responses`
  without bridge; GPT-5.5: dual endpoint; GPT-5.5 Pro: Responses-only with
  bridge) are model-specific conditioning variables, not contradictions.

- **Extends**:
  - `blog-litellm-gpt-5-3-codex-day-0.md` — Adds the "backward-compatible
    enablement" pattern (no Docker upgrade needed), which is absent from the
    Codex note (Codex required a model-pinned stable image). Adds the first
    documented instance of the Responses API bridge — the Codex note showed
    direct `client.responses.create()` usage without mentioning any SDK
    translation layer. Extends the `/v1/responses` endpoint documentation from
    "exclusive" (Codex) to "available, also available via `/chat/completions`"
    (GPT-5.5) and "Responses-only with transparent bridge" (GPT-5.5 Pro).
  - `blog-litellm-claude-opus-4-8-day-0.md` — Adds a second data point on
    the cost-map reload enablement pattern (same endpoint). Adds the
    observation that some models require no image upgrade while others
    require pinned tags — extending the Day-0 enablement cost documentation.
  - All LiteLLM Day-0 notes — Every LiteLLM Day-0 note to date has used a
    version-pinned image for the model being announced. This post introduces
    a variant: *optionally* pinned (the post shows a concrete tag) but
    *functionally* unnecessary (the model works on any recent version). This
    extends the corpus's understanding of the Day-0 enablement surface.

- **Novel**: First source note in the corpus to capture:
  - **No Docker upgrade pattern** — backward-compatible enablement where the
    model routes through an existing config class (`OpenAIGPT5Config`),
    requiring only a cost-map reload. All prior Day-0 models required a
    specific image tag.
  - **Responses API bridge** — the `completion()` → `/v1/responses` transparent
    translation. A new LiteLLM gateway capability not documented in any prior
    note.
  - **Dual-endpoint support within one model family** — GPT-5.5 uses both
    `/v1/chat/completions` and `/v1/responses`; GPT-5.5 Pro is Responses-only
    with a bridge. Prior notes documented single-endpoint or multi-endpoint
    support but never a split-variant pattern within one family.
  - **Long-context pricing tier at 272K tokens** — the first mention of a
    token-count-based pricing threshold in the corpus.
  - **Per-variant reasoning effort defaults** — GPT-5.5 defaults to `medium`/
    GPT-5.5-Pro defaults to `high`, with different allowed ranges. The first
    time within-model-family effort default divergence is documented.
  - **Local enforcement of reasoning effort caps** — `UnsupportedParamsError`
    at the gateway instead of round-tripping to OpenAI for a 400. A new
    error-surface pattern not previously documented.
  - **GPT-5.5 and GPT-5.5 Pro model IDs** for the routing catalog.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) / model enablement workflow**: Add that
  the Day-0 enablement cost (operator effort) varies per model. Document a
  spectrum from "no-op (just cost-map reload)" for backward-compatible models
  like GPT-5.5 to "container restart with pinned image" for models like
  GPT-5.3-Codex and Claude Fable 5. This post provides the first data point
  for the low-effort end of the spectrum.
- **Chapter 05 / API surface evolution (Responses API bridge)**: Add that
  LiteLLM's Responses API bridge transparently translates `completion()` SDK
  calls to `/v1/responses` for Responses-only models. This means operators can
  use a single SDK pattern (`completion()`) across models that use either the
  chat completions or Responses API wire protocol. The bridge absorbs API
  surface fragmentation so client code doesn't have to. Compare with
  `blog-litellm-gpt-5-3-codex-day-0.md` which shows the direct
  `client.responses.create()` pattern.
- **Chapter 05 / reasoning effort enforcement**: Add that LiteLLM now enforces
  per-model reasoning effort caps locally via `UnsupportedParamsError`, rather
  than letting the upstream API reject invalid values. This changes the error
  surface — operators should add LiteLLM error monitoring for
  `UnsupportedParamsError` alongside upstream API error monitoring. Document
  the specific tables for GPT-5.5 (default `medium`, allowed `none`/`low`/
  `medium`/`high`/`xhigh`) and GPT-5.5 Pro (default `high`, allowed
  `medium`/`high`/`xhigh`).
- **Chapter 05 / capacity & spend**: Add the long-context pricing tier at 272K
  tokens as the first documented token-count-based pricing threshold. Prompts
  exceeding 272K tokens incur a higher per-token rate. This is new — prior
  model documentation did not include tier thresholds.
- **Chapter 05 / endpoint routing catalog**: Add GPT-5.5 (dual endpoint:
  `/v1/chat/completions` AND `/v1/responses`) and GPT-5.5 Pro (Responses
  API-only with `completion()` bridge) to the routing catalog. Note that
  variant-specific endpoint exclusivity exists within the same model family,
  extending the pattern observed in GPT-5.3-Codex (exclusive `/v1/responses`).

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/gpt_5_5`, published April 24, 2026.
  Page fetched via direct HTTP (curl) with HTML-to-text extraction, then
  verified against the rendered page for verbatim quote accuracy. All quoted
  passages were copied character-for-character from the rendered page text.
- The page is self-contained (single announcement with config, Docker, curl,
  and SDK examples). No outbound links to substantive related pages were found
  in the announcement body beyond a reference to "OpenAI provider docs" and
  OpenAI's announcement. Nothing paywalled or truncated.
- The post is a standard LiteLLM Day-0 announcement matching the same template
  as all others in the corpus. The operationally novel details are concentrated
  in three areas: backward-compatible enablement, Responses API bridge, and
  per-variant reasoning effort caps with local enforcement.
- `confidence_overall` set to `emerging`: the first-party config and parameter
  detail is effectively settled how-to, but the post as a whole is a thin Day-0
  announcement. This matches the `emerging` rating on all sibling LiteLLM Day-0
  notes.
- No contradiction issue filed: verified against all existing source notes and
  open contradiction-labeled issues on the repo. Differences from prior notes
  are model-specific conditioning variables, not contradictions.
- Novelty per triage: low (standard Day-0 announcement in a well-documented
  template). The genuinely novel elements extracted are the three operational
  patterns listed in the summary, plus the 272K token pricing tier and local
  effort enforcement.
- The Docker image tag `v1.83.7-stable` also appears in the failure note
  `failure-litellm-proxy-sql-injection-cve-2026-42208.md` as the fix version
  for CVE-2026-42208. The coincidence is noted — operators on this image are
  also patched against that vulnerability, though the post does not mention
  this.
