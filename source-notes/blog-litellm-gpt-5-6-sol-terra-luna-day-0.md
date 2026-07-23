---
source_url: https://docs.litellm.ai/blog/gpt_5_6
source_type: blog-post
title: "Day 0 Support: GPT-5.6 (Sol, Terra, Luna)"
author: "Mateo Wang (AI Engineer, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-07-09
date_extracted: 2026-07-23
last_checked: 2026-07-23
status: current
confidence_overall: emerging
issue: "#437"
---

# Day 0 Support: GPT-5.6 (Sol, Terra, Luna)

> A LiteLLM vendor announcement for OpenAI's GPT-5.6 family (Sol, Terra, Luna)
> Day 0 support. Operationally novel within the Day-0 template corpus for five
> patterns: (1) a **three-tier durable naming convention** (Sol/Terra/Luna)
> replacing the previous model-name-suffix approach, (2) **Azure availability at
> launch** (contrast with GPT-5.5 which was OpenAI-direct only), including
> **regional Azure pricing** with automatic 10% uplift tracking via model-name
> prefixes, (3) a new **`max` reasoning effort and `ultra` subagent coordination
> mode** — new OpenAI API capabilities not previously documented in the corpus,
> (4) a **"living post" documentation pattern** stating the page will be updated
> as support expands, and (5) a **dev-nightly Docker tag** (`v1.93.0-dev.2`)
> compared to GPT-5.5's stable tag (`v1.83.7-stable`). The "no Docker image
> upgrade needed" backward-compatible enablement pattern from GPT-5.5 is
> corroborated and extended.

## Source Context

- **Type**: blog-post (vendor "Day 0 support" product announcement on
  `docs.litellm.ai/blog`), tagged `openai`, `gpt-5.6`, `gpt-5.6-sol`,
  `gpt-5.6-terra`, `gpt-5.6-luna`, `completion`, `day 0 support`.
- **Author credibility**: High for *how LiteLLM itself routes and configures
  the model* — authored by a LiteLLM AI Engineer (Mateo Wang) and the company's
  CEO (Krrish Dholakia) and CTO (Ishaan Jaffer), i.e. the maintainers of the
  gateway. The config and parameter-mapping detail is first-party documentation.
  Model-capability claims ("new state of the art on Terminal-Bench 2.1") are
  attributed to OpenAI, not independently measured here.
- **Scope**: Covers (1) Day-0 availability through LiteLLM, (2) the three-tier
  Sol/Terra/Luna naming convention and its implications for routing configuration,
  (3) the new `max` reasoning effort and `ultra` subagent-coordination mode,
  (4) Azure availability at launch with global and regional pricing, (5) per-model
  pricing with a 272K token context threshold, (6) the no-Docker-upgrade
  backward-compatible enablement pattern corroborating GPT-5.5, and (7) cost-map
  reload enablement. Does NOT cover: production metrics, latency/throughput
  measurements, failure analysis, or any practitioner outcome — it is a
  launch/how-to post structurally following the same LiteLLM "Day 0 Support"
  template as the other 7+ Day-0 notes in the corpus.

## Extracted Claims

### Claim 1: GPT-5.6 introduces a three-tier durable naming convention (Sol/Terra/Luna) replacing the previous model-name-suffix approach, requiring three model entries in the routing catalog
- **Evidence**: The opening body paragraph explains the naming system explicitly;
  the Proxy config.yaml example shows three separate `model_list` entries
  (`gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`).
- **Confidence**: settled (first-party documentation of a concrete naming taxonomy).
- **Quote**: "GPT-5.6 introduces a new naming system where the number identifies
  the generation and the tier name identifies a durable capability level.
  `gpt-5.6-sol` is the flagship for complex reasoning and agentic workloads,
  `gpt-5.6-terra` is a balanced model for everyday work with performance
  competitive with GPT-5.5 at roughly half the cost, and `gpt-5.6-luna` is the
  fastest and most affordable tier."
- **Our assessment**: This is the most operationally significant difference from
  prior Day-0 notes. GPT-5.5 used a single version number (gpt-5.5) and a Pro
  suffix (gpt-5.5-pro). GPT-5.6 replaces this with three distinct tier names
  (Sol, Terra, Luna) within the same `gpt-5.6` generation. For gateway operators,
  this means configuring three model entries instead of one or two. The tier names
  are advertised as "durable" — meaning they should persist across model updates
  within the generation, reducing the need to update routing config every time
  OpenAI releases a minor model refresh. This is a new model taxonomy for the
  routing catalog in Chapter 05.

### Claim 2: GPT-5.6 adds a `max` reasoning effort (beyond the existing `xhigh` level) and an `ultra` mode that coordinates subagents on complex tasks
- **Evidence**: Stated in the opening paragraph alongside the model-tier
  descriptions. This is an OpenAI-native capability that LiteLLM proxies through.
- **Confidence**: emerging (stated by the vendor as an OpenAI capability; no
  example code, parameter table, or supported-values enum is shown in the post.
  The `max` effort level and `ultra` mode are not demonstrated with config or
  API parameter examples.)
- **Quote**: "GPT-5.6 also adds a new `max` reasoning effort for the deepest
  single-agent thinking and an `ultra` mode that coordinates subagents on the
  most complex tasks."
- **Our assessment**: If real, this is a significant new capability in the
  reasoning-effort spectrum — the existing corpus documents levels from `none`
  to `xhigh` across various models (GPT-5.5: `none`/`low`/`medium`/`high`/`xhigh`;
  see `blog-litellm-gpt-5-5-day-0.md` Claim 4). A `max` tier would extend the
  top end of the spectrum. The `ultra` mode is more novel — subagent coordination
  at the model level is not currently documented in any existing source note.
  However, confidence is `emerging` because the post provides no concrete
  parameter-mapping detail or example for either feature. Operators should verify
  whether `ultra` is a LiteLLM abstraction or an OpenAI-native API mode before
  building routing logic around it. The lack of a parameter table (contrast with
  GPT-5.5's reasoning effort table in the sibling note) may indicate these
  features were not yet available in the underlying API at the time of writing.

### Claim 3: GPT-5.6 ships with Azure OpenAI availability at launch, unlike GPT-5.5 which was OpenAI-direct only
- **Evidence**: A prominent "Living post" info admonition in the post explicitly
  states Azure availability. The post includes a dedicated Azure OpenAI tab in
  the "Usage" section with config.yaml examples and SDK code.
- **Confidence**: settled (first-party vendor documentation; concrete config
  examples for Azure deployments).
- **Quote**: "GPT-5.6 is now available on Azure OpenAI in addition to OpenAI direct.
  Global Azure deployments match OpenAI list pricing, and regional deployments
  (`azure/us/*` and `azure/eu/*`) are tracked with the standard 10% regional uplift."
- **Our assessment**: This is a meaningful contrast with GPT-5.5, which explicitly
  stated "Azure availability: not yet — this post covers OpenAI direct only"
  (see `blog-litellm-gpt-5-5-day-0.md` Claim 7). GPT-5.6 eliminates that
  constraint at launch. For operators with Azure-only procurement or compliance
  requirements, this means GPT-5.6 can be adopted immediately without waiting
  for the Azure availability lag that has affected prior model launches. The
  Azure support covers all three tiers (Sol, Terra, Luna) under the same
  `azure/gpt-5.6-*` naming convention.

### Claim 4: Regional Azure deployments use `azure/us/*` and `azure/eu/*` model-name prefixes that trigger automatic cost-uplift tracking in LiteLLM
- **Evidence**: The Azure tab explains the naming convention; the Azure pricing
  note at the end of the post confirms the 10% uplift mechanism.
- **Confidence**: settled (concrete model-name prefix conventions documented
  with example config; the automatic tracking behavior is stated as a LiteLLM
  feature).
- **Quote**: "Point `model` at the Azure deployment name. Global deployments use
  the `azure/gpt-5.6-*` names; regional deployments use `azure/us/gpt-5.6-*` or
  `azure/eu/gpt-5.6-*` so cost tracking picks up the regional uplift automatically."
- **Quote** (pricing note): "Regional deployments (`azure/us/gpt-5.6-*` and
  `azure/eu/gpt-5.6-*`) carry the standard 10% uplift on the base rate; LiteLLM
  tracks the difference automatically once you route through the regional model
  name."
- **Our assessment**: This introduces a model-name-prefix-based regional pricing
  mechanism not previously documented in any Day-0 note. Operators deploying in
  Azure regions with the 10% uplift can rely on LiteLLM's cost tracking to record
  the uplift rate automatically, provided they use the `azure/us/` or `azure/eu/`
  prefix. This is a new deploy-target pricing pattern worth documenting in the
  capacity & spend material. The `azure/gpt-5.6-*` (global) variant provides a
  pricing reference without uplift — operators tracking actual vs. billed cost
  should be aware of the difference.

### Claim 5: This post follows a "living post" pattern stating it will be updated as support expands — a change from the static Day-0 announcements used for all prior models
- **Evidence**: An info admonition at the top of the post is titled "Living post"
  and states that the content will be updated over time.
- **Confidence**: settled (the admonition is clearly visible at the top of the
  page with the heading "Living post").
- **Quote**: "**This post is updated as GPT-5.6 support expands.**"
- **Our assessment**: This is a documentation-pattern change. Every prior LiteLLM
  Day-0 post (Claude Opus 4.7, Opus 4.8, Fable 5, Gemini 3.5 Flash, GPT-5.5,
  GPT-5.3-Codex, and others) presented a static snapshot of Day-0 capabilities.
  This post explicitly signals that the documentation will evolve, and indeed
  the "Living post" admonition already reflects post-publication additions:
  it mentions Azure availability, which is a new addition beyond the original
  Day-0 scope. For operators, this means the source URL should be rechecked
  periodically for updates rather than treated as a one-time reference. The
  pattern also implies LiteLLM may publish Day-0 posts earlier (before all
  backends are ready) and expand them over time — operators should verify
  claimed support with a test request rather than assuming all advertised
  features were available on Day 0.

### Claim 6: The recommended Docker image for GPT-5.6 support is `v1.93.0-dev.2`, a dev-nightly tag — contrasting with GPT-5.5's stable tag `v1.83.7-stable`
- **Evidence**: The Docker pull/run commands specify this exact image tag.
- **Confidence**: settled (first-party deploy instruction; the tag is concrete and
  referenced in both pull and run commands).
- **Quote**: "`ghcr.io/berriai/litellm:v1.93.0-dev.2`"
- **Our assessment**: This tag represents a different release-track maturity than
  GPT-5.5's `v1.83.7-stable`. Under the release-tag taxonomy documented in
  `blog-litellm-april-townhall-updates.md` (Claim 6 — the 4-tier release-tag
  taxonomy), `-dev.2` is a **Nightly Dev** build — the least mature tier, below
  Release Candidate and Stable. This contrasts with GPT-5.5 (Stable) and
  GPT-5.3-Codex (Stable with model-pinned suffix), but matches Opus 4.8
  (`v1.88.0-dev.1`, also Nightly Dev). Operators with policies against pre-release
  software should note that the pricing/metadata are bundled starting at this tag,
  and the post's own note says "any recent version works out of the box" for
  routing — but the bundled cost tracking requires at least this dev tag when
  using `LITELLM_LOCAL_MODEL_COST_MAP=true`. The CAUTION from the wildcard-desync
  incident (`failure-litellm-wildcard-model-access-desync.md`) applies doubly here:
  dev-nightly images may carry additional instability or behavior changes beyond
  the known cost-map-reload issue.

### Claim 7: GPT-5.6 requires no Docker image upgrade — it routes through the existing `OpenAIGPT5Config`, corroborating and extending the backward-compatible enablement pattern first documented for GPT-5.5
- **Evidence**: A prominent "note" admonition states this explicitly, adding a
  new detail: the version classifier matches `gpt-5.4` and newer.
- **Confidence**: settled (the vendor documenting its own supported routing; the
  version-classifier detail is concrete and testable).
- **Quote**: "No Docker image upgrade needed. GPT-5.6 routes through the existing
  `OpenAIGPT5Config` in LiteLLM (the version classifier already matches `gpt-5.4`
  and newer), so any recent version works out of the box."
- **Our assessment**: This corroborates the pattern first documented in
  `blog-litellm-gpt-5-5-day-0.md` Claim 1, and extends it with a new detail: the
  version classifier matches `gpt-5.4` and newer (the GPT-5.5 note did not
  mention this classifier behavior). The parenthetical explains *why* the
  backward-compatible routing works: LiteLLM's `OpenAIGPT5Config` classifier
  uses a version-range check (`>= gpt-5.4`), so any model id starting with
  `gpt-5.4`, `gpt-5.5`, or `gpt-5.6` is automatically matched. This means
  future GPT-5.x models up until a hypothetical GPT-6.0 breaking change would
  also route through this same config class without code changes. The practical
  implication: the "no Docker upgrade" pattern is not a GPT-5.5 special case but
  an intentional design choice by LiteLLM for the entire 5.x generation.

### Claim 8: GPT-5.6 pricing follows the same 272K long-context threshold as GPT-5.5, with per-tier pricing ranging from $1/$2 (Luna) to $5/$10 (Sol) input and $6/$9 (Luna) to $30/$45 (Sol) output
- **Evidence**: A pricing table with per-model prices at short (≤272K) and long
  (>272K) context lengths.
- **Confidence**: settled (standard price table from the vendor).
- **Quote**: "Prices are per 1M tokens (USD), shown as short context (≤272K tokens)
  / long context (>272K tokens)."
- **Quote** (pricing table, rendered as text from HTML table):
  "| Model | Input | Cached input | Cache write | Output |
  |---|---|---|---|---|
  | `gpt-5.6-sol` | $5.00 / $10.00 | $0.50 / $1.00 | $6.25 / $12.50 | $30.00 / $45.00 |
  | `gpt-5.6-terra` | $2.50 / $5.00 | $0.25 / $0.50 | $3.125 / $6.25 | $15.00 / $22.50 |
  | `gpt-5.6-luna` | $1.00 / $2.00 | $0.10 / $0.20 | $1.25 / $2.50 | $6.00 / $9.00 |"
- **Our assessment**: The 272K threshold first documented in GPT-5.5
  (`blog-litellm-gpt-5-5-day-0.md` Claim 5) is now corroborated on a second
  model family, confirming it is an OpenAI pricing convention rather than a
  GPT-5.5-specific anomaly. The per-tier pricing spans a 5× range from Luna
  ($1 input) to Sol ($5 input short context), and the output pricing spans a
  5× range ($6 to $30). For capacity planners, the pricing spread within a single
  generation is wider than GPT-5.5's two-variant spread (GPT-5.5 standard vs Pro),
  suggesting a tier-based pricing strategy that may continue in future OpenAI
  releases. The Terra tier at $2.50 input / $15 output is positioned at roughly
  half the cost of Sol — the post explicitly states Terra is "competitive with
  GPT-5.5 at roughly half the cost" of GPT-5.5, implying a strategic
  price-performance tier between the flagship (Sol) and the budget (Luna).

## Concrete Artifacts

All artifacts below are extracted from the source page HTML. Inline-code spans
in the rendered page (e.g. YAML keys, model IDs) are reproduced as rendered.

### Proxy `config.yaml` (verbatim from the Proxy tab)

```yaml
model_list:
  - model_name: gpt-5.6-sol
    litellm_params:
      model: openai/gpt-5.6-sol
      api_key: os.environ/OPENAI_API_KEY
  - model_name: gpt-5.6-terra
    litellm_params:
      model: openai/gpt-5.6-terra
      api_key: os.environ/OPENAI_API_KEY
  - model_name: gpt-5.6-luna
    litellm_params:
      model: openai/gpt-5.6-luna
      api_key: os.environ/OPENAI_API_KEY
```

### Docker run command (verbatim)

```bash
docker run -d \
  -p 4000:4000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/config.yaml:/app/config.yaml \
  ghcr.io/berriai/litellm:v1.93.0-dev.2 \
  --config /app/config.yaml
```

### curl test — chat completions (verbatim)

```bash
curl -X POST "http://0.0.0.0:4000/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -d '{
    "model": "gpt-5.6-sol",
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
    "model": "gpt-5.6-sol",
    "input": "Plan and write a Python script that scrapes a webpage and summarizes it."
  }'
```

### LiteLLM SDK examples — all three tiers (verbatim)

```python
from litellm import completion

response = completion(
    model="openai/gpt-5.6-sol",
    messages=[
        {"role": "user", "content": "Write a Python function to check if a number is prime."}
    ],
)
print(response.choices[0].message.content)
```

```python
# gpt-5.6-terra for balanced, cost-efficient everyday work
response = completion(
    model="openai/gpt-5.6-terra",
    messages=[
        {"role": "user", "content": "Summarize the key ideas in this design doc."}
    ],
)
print(response.choices[0].message.content)
```

```python
# gpt-5.6-luna for the fastest, lowest-cost tier
response = completion(
    model="openai/gpt-5.6-luna",
    messages=[
        {"role": "user", "content": "Classify this ticket as bug, feature, or question."}
    ],
)
print(response.choices[0].message.content)
```

### Azure config.yaml (verbatim)

```yaml
model_list:
  - model_name: gpt-5.6-sol
    litellm_params:
      model: azure/gpt-5.6-sol
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      api_version: os.environ/AZURE_API_VERSION
  - model_name: gpt-5.6-terra
    litellm_params:
      model: azure/gpt-5.6-terra
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      api_version: os.environ/AZURE_API_VERSION
```

### Azure SDK example (verbatim)

```python
from litellm import completion

response = completion(
    model="azure/gpt-5.6-sol",
    messages=[
        {"role": "user", "content": "Write a Python function to check if a number is prime."}
    ],
)
print(response.choices[0].message.content)
```

### Pricing table (verbatim from HTML table)

| Model | Input | Cached input | Cache write | Output |
|---|---|---|---|---|
| `gpt-5.6-sol` | $5.00 / $10.00 | $0.50 / $1.00 | $6.25 / $12.50 | $30.00 / $45.00 |
| `gpt-5.6-terra` | $2.50 / $5.00 | $0.25 / $0.50 | $3.125 / $6.25 | $15.00 / $22.50 |
| `gpt-5.6-luna` | $1.00 / $2.00 | $0.10 / $0.20 | $1.25 / $2.50 | $6.00 / $9.00 |

### Cost-map reload note (verbatim)

> "For cost tracking on the GPT-5.6 models, hit the **Reload Model Cost Map**
> button in the Admin UI (or `POST /reload/model_cost_map`). Works on any
> LiteLLM version `v1.76.0` or newer, with no container restart or image upgrade
> required."

## Cross-References

- **Corroborates**:
  - `blog-litellm-gpt-5-5-day-0.md` (Claim 1 — no Docker image upgrade needed
    via `OpenAIGPT5Config`). GPT-5.6 confirms this is not a GPT-5.5 special case
    but an intentional design for the entire 5.x generation, adding the detail
    that the version classifier matches `gpt-5.4` and newer (Claim 7 in this
    note). Also corroborates (Claim 5 — 272K long-context pricing tier). The
    272K threshold is now observed across two distinct model families, confirming
    it as an OpenAI pricing convention (Claim 8 in this note).
  - `blog-litellm-gpt-5-3-codex-day-0.md` — Same Day-0 template pattern, now
    applied to three-tier naming. The `/v1/responses` endpoint curl example in
    this post confirms the Responses API is a continuing pattern across GPT
    model families.
  - `blog-litellm-claude-opus-4-8-day-0.md` (Claim 10 — cost-map reload
    enablement). The same `POST /reload/model_cost_map` path is the recommended
    enablement procedure. This post additionally uses a Nightly Dev tag
    (`v1.93.0-dev.2`), matching Opus 4.8's `v1.88.0-dev.1` — both are Dev-nightly
    builds under the 4-tier release-tag taxonomy.
  - `failure-litellm-wildcard-model-access-desync.md` — The cost-map reload
    path is the same endpoint whose partial-reload desync was the subject of
    that incident report. Operators adding GPT-5.6 via cost-map reload should
    verify end-to-end access before assuming the reload succeeded — the caution
    from that incident applies.

- **Contradicts**: None. No contradiction issue filed. Verified against all
  existing source notes, `CONTRADICTIONS.md` (no open `C-NNN` entries), and
  open contradiction-labeled issues (none). The Azure availability at launch
  (Claim 3) is the inverse of `blog-litellm-gpt-5-5-day-0.md` Claim 7 ("Azure
  availability: not yet"), but this is product evolution, not a contradiction —
  two different model releases with different deployment timelines. The
  different naming conventions (Sol/Terra/Luna vs. GPT-5.5/5.5-Pro) and
  different Docker tag maturities (dev-nightly vs. stable) are model-specific
  operational variations, not contradictions.

- **Extends**:
  - `blog-litellm-gpt-5-5-day-0.md` — Adds the three-tier naming convention
    (Sol/Terra/Luna) to the model taxonomy documentation. Adds Azure
    availability with regional pricing (not present in GPT-5.5). Adds the `max`
    reasoning effort and `ultra` subagent coordination mode as new API
    capabilities (the GPT-5.5 note documented effort levels only through `xhigh`
    and had no equivalent of `ultra` mode). Extends the no-Docker-upgrade
    pattern with the version-classifier detail (`gpt-5.4` and newer). Extends
    the pricing table with three tiers spanning a 5× input-cost range.
  - `blog-litellm-claude-opus-4-8-day-0.md` — Adds a second data point on the
    Nightly Dev Docker tag pattern. Adds a third data point on the cost-map
    reload enablement pattern across distinct model vendors.
  - All LiteLLM Day-0 notes — This post introduces a "living post" pattern not
    seen in any prior Day-0 note (static announcements only). The documentation
    will evolve over time, which changes how operators should treat the source
    as a reference.

- **Novel**: First source note in the corpus to capture:
  - **Three-tier durable naming convention** — Sol/Terra/Luna replacing the
    earlier capabilty-suffix model (Pro, mini, nano). A new model taxonomy for
    the routing catalog: operators now need three model entries per generation.
  - **`max` reasoning effort** — a new level above `xhigh`, extending the
    reasoning-effort spectrum.
  - **`ultra` subagent coordination mode** — model-level orchestration of
    subagents, an entirely new capability category not previously documented
    in the corpus. (Confidence: emerging — no concrete API parameter mapping
    provided.)
  - **Azure availability at launch** — the first OpenAI model to ship with
    Azure support on Day 0, ending the Azure availability lag pattern observed
    for all prior OpenAI model launches.
  - **Regional Azure pricing via model-name prefix** — `azure/us/*` and
    `azure/eu/*` prefixes with automatic 10% uplift tracking. A new
    deploy-target pricing pattern.
  - **"Living post" documentation pattern** — the post states it will be
    updated, a departure from the static Day-0 announcement format used for
    all 7+ prior models.
  - **Version-classifier range detail** — `OpenAIGPT5Config` matches `gpt-5.4`
    and newer, explaining the mechanism behind the no-Docker-upgrade pattern.
  - **GPT-5.6 model IDs** (gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna) for the
    routing catalog, with their per-tier pricing and capability positioning.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) / routing catalog**: Add the three GPT-5.6
  model IDs (`gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`) as a new tier-based
  model taxonomy. This is the first model family in the corpus using durable
  tier names instead of capability suffixes. The routing catalog should reflect
  that operators need three entries per generation under this new naming scheme.
  Document the durability claim — tier names are intended to persist across
  minor model updates within the generation, potentially reducing config churn.

- **Chapter 05 / model enablement workflow**: Add that the "no Docker upgrade
  needed" backward-compatible pattern now spans two OpenAI model families
  (GPT-5.5 and GPT-5.6), confirming it is an intentional `OpenAIGPT5Config`
  design for the 5.x generation with the classifier matching `gpt-5.4` and newer.
  Operators adding GPT-5.x models should first verify whether the model routes
  through the existing config before planning a container restart. However, the
  Docker tag maturity varies: GPT-5.6 ships on a Nightly Dev tag
  (`v1.93.0-dev.2`), contrasting with GPT-5.5's Stable tag (`v1.83.7-stable`).
  Document the tag-maturity range as part of the enablement cost assessment.

- **Chapter 05 / API surface evolution (reasoning efforts and ultra mode)**: Add
  that GPT-5.6 introduces a `max` reasoning effort (above `xhigh`) and an `ultra`
  subagent-coordination mode. The `ultra` mode is a genuinely new capability —
  model-level subagent orchestration — not previously documented in the corpus.
  Flag this as emerging: the source provides no concrete parameter mapping,
  and operators should verify the API surface (is `ultra` an OpenAI-native mode
  or a LiteLLM abstraction?) before building routing logic around it. Tracking
  this in the capabilities registry is valuable even without the parameter
  details, since it signals an upcoming API pattern.

- **Chapter 05 / deploy targets (Azure)**: Add that GPT-5.6 is the first OpenAI
  model in the corpus to ship with Azure support at launch. This eliminates the
  Azure availability lag that affected GPT-5.5 and earlier models. Document the
  Azure model-name convention: global (`azure/gpt-5.6-*`), regional US
  (`azure/us/gpt-5.6-*`), and regional EU (`azure/eu/gpt-5.6-*`).

- **Chapter 05 / capacity & spend**: Add the three-tier pricing structure for
  GPT-5.6 to the capacity & spend documentation. The 272K context threshold is
  now corroborated across two model families, confirming it as an OpenAI pricing
  convention rather than a GPT-5.5 anomaly. Add the regional Azure uplift
  (10%) cost tracking via model-name prefixes — a new pricing-dimension pattern.
  The per-tier pricing spread (5× from Luna to Sol) should inform capacity
  planning guidance.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/gpt_5_6`, published July 9, 2026.
  Page fetched via direct HTTP (curl) with the full HTML read and inspected for
  verbatim quote accuracy. All quoted passages were copied character-for-character
  from the rendered page HTML text.
- The page is self-contained (single announcement with config, Docker, curl,
  and SDK examples across three usage tabs). No outbound links to substantive
  related pages were followed — the only outbound link is to the OpenAI
  GPT-5.6 announcement page, a general OpenAI provider docs link, and references
  to LiteLLM's Admin UI. Nothing paywalled or truncated.
- The post is a standard LiteLLM Day-0 announcement matching the same template
  as all others in the corpus, with one structural addition: the "Living post"
  admonition (a new pattern not seen in prior Day-0 notes) and an Azure tab
  in the Usage section (also new — prior notes were OpenAI-direct only or had
  Azure as a separate config section).
- `confidence_overall` set to `emerging`: the first-party config, pricing, and
  Azure routing detail is effectively settled how-to, but the post as a whole is
  a thin Day-0 announcement. The novel patterns (max/ultra capabilities, Azure
  regional pricing, living post) are stated without the depth of parameter tables
  or example code that would raise confidence to `settled` for the API-capability
  claims. This matches the `emerging` rating on all sibling LiteLLM Day-0 notes.
- No contradiction issue filed: verified against all existing source notes,
  `CONTRADICTIONS.md` (no open `C-NNN` entries), and open contradiction-labeled
  issues (none). Differences from prior notes are model-specific operational
  variations or product evolution, not contradictions.
- Novelty per triage: medium. While the Day-0 template is well-documented
  (7+ instances in the corpus across providers), this post introduces several
  genuinely new patterns beyond the template: three-tier naming, Azure Day-0,
  regional pricing prefixes, max/ultra capabilities, and the living post pattern.
  The novel content density is higher than GPT-5.5 or GPT-5.3-Codex.
- The `max` reasoning effort and `ultra` mode are claimed as OpenAI-native
  capabilities but no parameter-mapping detail is provided. The triage question
  "are these LiteLLM abstractions or OpenAI-native features?" cannot be answered
  from this source alone — the post attributes them to GPT-5.6 generally.
  Recommend flagging this for Smith to investigate against the OpenAI API docs.
