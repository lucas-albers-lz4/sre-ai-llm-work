---
source_url: https://docs.litellm.ai/blog/claude_opus_4_7
source_type: blog-post
title: "Day 0 Support: Claude Opus 4.7"
author: "Sameer Kankute (SWE, LiteLLM), Ishaan Jaffer (CTO, LiteLLM), Krrish Dholakia (CEO, LiteLLM)"
date_published: 2026-04-16
date_extracted: 2026-07-18
last_checked: 2026-07-18
status: current
confidence_overall: emerging
issue: "#287"
---

# Day 0 Support: Claude Opus 4.7

> A LiteLLM vendor announcement documenting Day-0 proxy support for Claude
> Opus 4.7 across Anthropic, Azure, Vertex AI, and Bedrock. Operationally
> it is the same per-provider config template and adaptive-thinking-only
> parameter map as the sibling Fable 5 post, but serves as the historical
> origin of the `xhigh` effort level and uses a stable-release image tag
> (v1.83.3-stable) rather than an RC — documenting an earlier point in
> LiteLLM's release-tag evolution where Bedrock still accepted direct model
> IDs (no inference-profile prefix required) and the post carried no
> data-sharing opt-in, pricing, or silent-fallback sections.

## Source Context

- **Type**: blog-post (vendor "Day 0 support" product announcement on
  `docs.litellm.ai/blog`), tagged `anthropic`, `claude`, `opus 4.7`.
- **Author credibility**: First-party LiteLLM documentation — authored by
  Sameer Kankute (SWE, LiteLLM), Ishaan Jaffer (CTO, LiteLLM), and Krrish
  Dholakia (CEO, LiteLLM). The config/parameter-mapping detail is the
  gateway maintainer documenting their own supported routing.
- **Scope**: Covers (1) multi-provider Day-0 availability through one
  OpenAI-compatible interface, (2) per-provider `config.yaml` examples
  (Anthropic, Azure, Vertex AI, Bedrock), (3) adaptive-thinking parameter
  mapping, and (4) effort levels including `xhigh` as a new tier. Does NOT
  cover: pricing, data-sharing opt-ins, model specs (context length, output
  tokens), silent fallback behavior, or production metrics — all absent
  from this post and present in the later Fable 5 Day 0 post.

## Extracted Claims

### Claim 1: LiteLLM supports Claude Opus 4.7 on Day 0 across four provider backends via the same OpenAI-compatible interface as other models
- **Evidence**: Opening paragraph of the post; the body then provides
  per-provider tabs for Anthropic, Azure, Vertex AI, and Bedrock.
- **Confidence**: settled (first-party vendor documentation of supported
  routing).
- **Quote**: "LiteLLM now supports Claude Opus 4.7 on Day 0. Use it across
  Anthropic, Azure, Vertex AI, and Bedrock through the LiteLLM AI Gateway."
- **Our assessment**: Same operational pattern as the Fable 5 Day 0 post
  (one alias, four backends). Credible and concrete. This is the standard
  LiteLLM "Day 0 Support" template applied to Opus 4.7.

### Claim 2: Opus 4.7 is shipped on the stable release branch at image tag v1.83.3-stable, not an RC
- **Evidence**: The Docker image tag embedded in every per-provider example
  uses the `litellm_stable_release_branch-v1.83.3-stable.opus-4.7` tag.
- **Confidence**: settled (concrete, named image tag published by the
  vendor).
- **Quote**: "docker pull ghcr.io/berriai/litellm:litellm_stable_release_branch-v1.83.3-stable.opus-4.7"
- **Our assessment**: By the 4-tier release-tag taxonomy documented in the
  April 2026 Townhall note (Dev/Nightly/RC/Stable), this is a **Stable**
  tag — it carries both `-stable` suffix and `stable_release_branch`
  branch identifier. The Fable 5 post (June 2026) shipped on
  `v1.89.0-rc.2`, a release-candidate tag. This indicates that Day-0 model
  support can land on either a Stable or RC image depending on timing and
  release cycle — a conditioning variable for operators weighing adoption
  risk. See Cross-References §Extends.

### Claim 3: On Bedrock, Opus 4.7 is invoked via direct model ID (`bedrock/anthropic.claude-opus-4-7`), not through an inference-profile prefix
- **Evidence**: Bedrock config.yaml uses `model: bedrock/anthropic.claude-opus-4-7`
  with no `us.`/`eu.`/`global.` prefix.
- **Confidence**: settled (first-party config example).
- **Quote**: (verbatim from the rendered page config block):
  ```
  model: bedrock/anthropic.claude-opus-4-7
  aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
  aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
  aws_region_name: us-east-1
  ```
- **Our assessment**: This is the load-bearing delta from the Fable 5 note.
  Fable 5's Bedrock example requires `bedrock/converse/us.anthropic.claude-fable-5`
  (inference-profile prefix) because Bedrock only serves that model through
  inference profiles. Opus 4.7, being an earlier model, accepted direct
  model ID invocations. This confirms that the inference-profile requirement
  is model-specific (not a global Bedrock policy) and was introduced
  sometime between Opus 4.7 (April 2026) and Fable 5 (June 2026). See
  Cross-References §Extends.

### Claim 4: Opus 4.7 supports adaptive thinking only; explicit thinking budgets are rejected with a 400
- **Evidence**: The "Adaptive Thinking" note says explicit budgets are
  rejected; all `reasoning_effort` values map to `{type: "adaptive"}`.
- **Confidence**: settled (specific API constraint documented by the
  gateway maintainer).
- **Quote**: "When using reasoning_effort with Claude Opus 4.7, all values
  (low, medium, high, xhigh, max) are mapped to thinking: {type:
  \"adaptive\"}. Opus 4.7 only supports adaptive thinking; explicit budgets
  via thinking: {type: \"enabled\", budget_tokens: ...} are rejected by the
  Anthropic API with a 400 error. To control thinking depth, pair adaptive
  thinking with output_config.effort (see Effort Levels below) rather than a
  fixed budget."
- **Our assessment**: Identical adaptive-thinking-only constraint to Fable 5,
  confirming this is a model-level (not release-level) constraint for
  Opus 4-class Claude models. Same migration hazard: code with explicit
  thinking budgets will 400 against both Opus 4.7 and Fable 5.

### Claim 5: `xhigh` is introduced as a new effort level with Opus 4.7, positioned above `high` for coding and agentic work
- **Evidence**: The "Effort Levels" section explicitly states `xhigh` is
  new with Opus 4.7; the effort table codifies it as the fourth rung above
  `high`.
- **Confidence**: settled (first-party vendor documentation naming the
  model release as the introduction point).
- **Quote**: "xhigh is a new effort level introduced with Opus 4.7 that sits
  above high and is the recommended starting point for coding and agentic
  work. max sits above xhigh for the absolute highest capability; reserve it
  for genuinely frontier problems, since on most workloads it adds
  significant token cost for relatively small quality gains."
- **Our assessment**: This is the most historically valuable claim in the
  post. The Fable 5 note (published June 2026) presents all five effort
  levels (low/medium/high/xhigh/max) as the standard expected set, with no
  indication that `xhigh` was ever new. This Opus 4.7 post (April 2026) is
  the original announcement that establishes `xhigh` as a new tier —
  important for understanding the evolution of the effort-level framework,
  and potentially for conditioning guidance on which effort levels are
  available on which Claude model generations.

### Claim 6: Opus 4.7's effort-level guide table lists four tiers (low/medium/high/xhigh) and omits `max` from the table while the text acknowledges it
- **Evidence**: The rendered effort-level guide table on the page maps only
  `low`, `medium`, `high (default)`, and `xhigh` to use cases. `max` is
  mentioned in the paragraph above the table but is not given its own table
  row.
- **Confidence**: settled (visible artifact of the source page).
- **Quote**: (verbatim table content from the rendered page):
  ```
  Effort   When to use
  low      Short, fast responses — simple lookups, formatting, classification
  medium   Balanced tradeoff for everyday Q&A and light reasoning
  high (default) Complex reasoning, code generation, analysis
  xhigh    Hardest problems — multi-step math, deep research, agentic planning
  ```
- **Our assessment**: Minor formatting detail, but noteworthy as a
  comparison point: the Fable 5 post's effort table includes an explicit
  `max` row ("The hardest tasks where you want maximum reasoning depth
  regardless of latency (not available on Bedrock)"). The Opus 4.7 post's
  omission of `max` from the table while acknowledging it in prose suggests
  `max` was recognized but not yet operationalized as a documented tier at
  the time of this post.

### Claim 7: This Opus 4.7 post has no data-sharing opt-in, no pricing section, and no silent-fallback disclosure — all absent compared to the later Fable 5 post
- **Evidence**: Absence of sections that are present in the Fable 5 post.
  The Opus 4.7 post is strictly per-provider config + adaptive thinking +
  effort levels.
- **Confidence**: settled (the page was read in full — these sections do
  not exist).
- **Quote**: (no direct quote; absence is the evidence — the source page
  contains no data-sharing, pricing, or fallback content).
- **Our assessment**: The informational scope of "Day 0 Support" posts
  expanded between April and June 2026. The Opus 4.7 post is a simpler,
  earlier instance of the template. The Fable 5 post added data-sharing
  opt-ins (privacy/governance), pricing (spend planning), and the silent
  Opus 4.8 fallback (observability). An operator using only the Opus 4.7
  post might not realize data-sharing opt-ins are model-dependent, or that
  pricing/cost attribution details exist for newer models. Recommend the
  guide note that the "Day 0 Support" template matured over time and newer
  posts may contain operationally critical sections absent from earlier
  ones.

## Concrete Artifacts

All artifacts verbatim from the source page.

### Per-provider `config.yaml` model aliases (verbatim — reconstructed from rendered code blocks)

```yaml
# Anthropic
model_list:
  - model_name: claude-opus-4-7
    litellm_params:
      model: anthropic/claude-opus-4-7
      api_key: os.environ/ANTHROPIC_API_KEY

# Azure (Azure AI Foundry)
model_list:
  - model_name: claude-opus-4-7
    litellm_params:
      model: azure_ai/claude-opus-4-7
      api_key: os.environ/AZURE_AI_API_KEY
      api_base: os.environ/AZURE_AI_API_BASE  # https://<resource>.services.ai.azure.com

# Vertex AI
model_list:
  - model_name: claude-opus-4-7
    litellm_params:
      model: vertex_ai/claude-opus-4-7
      vertex_project: os.environ/VERTEX_PROJECT
      vertex_location: us-east5

# Bedrock (direct model ID — no inference profile prefix)
model_list:
  - model_name: claude-opus-4-7
    litellm_params:
      model: bedrock/anthropic.claude-opus-4-7
      aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
      aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
      aws_region_name: us-east-1
```

### Docker image tag (verbatim from the page)

```
docker pull ghcr.io/berriai/litellm:litellm_stable_release_branch-v1.83.3-stable.opus-4.7
```

### Effort-level guide table (verbatim from the rendered page)

```
Effort   When to use
low      Short, fast responses — simple lookups, formatting, classification
medium   Balanced tradeoff for everyday Q&A and light reasoning
high (default) Complex reasoning, code generation, analysis
xhigh    Hardest problems — multi-step math, deep research, agentic planning
```

### Adaptive thinking / effort levels SDK examples (verbatim)

```python
# OpenAI SDK
import openai
client = openai.OpenAI(
    api_key="your-litellm-key",
    base_url="http://0.0.0.0:4000"
)
response = client.chat.completions.create(
    model="claude-opus-4-7",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    extra_body={"output_config": {"effort": "xhigh"}}
)

# LiteLLM SDK
from litellm import completion
response = completion(
    model="anthropic/claude-opus-4-7",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    output_config={"effort": "xhigh"},
)
```

## Cross-References

- **Corroborates**:
  - `blog-litellm-claude-fable-5-day-0.md` (Claim 8, Claim 9) — The
    adaptive-thinking-only constraint and the five-rung effort ladder match
    identically. The Opus 4.7 post establishes the same parameters
    (`reasoning_effort` → adaptive mapping, `output_config.effort` ladder,
    explicit budgets → 400) that the Fable 5 note documents. The two posts
    together confirm these are cross-model, cross-release constraints for
    this Claude model generation.
  - `blog-litellm-april-townhall-updates.md` (Claim 6 — 4-tier release-tag
    taxonomy) — This post's image tag (`-stable` suffix on a `stable_release_branch`
    tag) is a concrete instance of the **Stable** tier defined in the
    townhall note, corroborating that taxonomy's descriptive accuracy.

- **Contradicts**: None. No contradiction issue filed. Verified against all
  existing source notes and open contradiction-labeled issues on the repo.
  The Fable 5 note's Claim 9 presents all five effort levels as standard
  for that model; this Opus 4.7 post presents `xhigh` as new. This is a
  **temporal difference** (Opus 4.7 predates Fable 5 by ~8 weeks; `xhigh`
  was introduced at Opus 4.7's launch and had become standard by Fable 5's
  release), not a contradiction — both claims are true for their respective
  model releases. The cross-provider differences (Bedrock direct model ID
  for Opus 4.7 vs inference-profile prefix for Fable 5) are model-specific
  **conditioning variables**, not contradictions per MINER.md §4.

- **Extends**:
  - `blog-litellm-claude-fable-5-day-0.md` — This note is the historical
    predecessor to the Fable 5 note. The Fable 5 note documented the mature
    form of the "Day 0 Support" template (with pricing, data-sharing
    opt-ins, silent fallback); this note documents the earlier, simpler
    template version. Together they enable the guide to describe how the
    template evolved and which sections operators should expect (or check
    for) when reading posts from different dates.
  - `blog-litellm-april-townhall-updates.md` (Claim 6) — extends the
    4-tier release-tag taxonomy with a concrete example of a **Stable**
    tier tag (`v1.83.3-stable`) — the townhall post defined the taxonomy
    conceptually; this note applies it to a real image tag.
  - `failure-litellm-wildcard-model-access-desync.md` — Like the Fable 5
    note's Claim 10, this Opus 4.7 post's enablement procedure would rely
    on the same `POST /reload/model_cost_map` path for operators using the
    default remote cost map. The wildcard-desync incident's lesson ("reload
    success ≠ end-to-end health") applies equally here.

- **Novel**: Introduces to the corpus:
  - The historical origin point of `xhigh` as an effort level (explicitly
    introduced with Opus 4.7 in mid-April 2026), establishing that this
    effort tier was not available on earlier Claude models.
  - Evidence that Bedrock's inference-profile-only requirement is
    model-specific: Opus 4.7 accepted direct model IDs
    (`bedrock/anthropic.claude-opus-4-7`), while Fable 5 required the
    inference-profile prefix. This is a conditioning variable for
    Bedrock model-enablement guidance.
  - A timeline data point for the evolution of LiteLLM's Day-0 announcement
    template (April 2026: config-only; June 2026: +pricing, +data-sharing
    opt-ins, +silent fallback disclosure).
  - A Stable-release image tag (`v1.83.3-stable`) as a concrete instance
    of the 4-tier release taxonomy from the townhall note — the Fable 5
    note provided the RC counterpart; this note provides the Stable
    counterpart.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) / new-model enablement**: Add that
  Bedrock's inference-profile-only requirement is model-specific (not a
  global policy). For some models (like Opus 4.7), a direct model ID
  suffices; for others (like Fable 5), the inference-profile prefix is
  mandatory. Gateway operators should check the specific model's
  documentation rather than assuming a single Bedrock invocation pattern.
- **Chapter 05 / effort-level guidance**: Record that `xhigh` was
  introduced with Claude Opus 4.7 (April 2026) and is not available on
  earlier Claude model generations. The five-rung effort ladder
  (low/medium/high/xhigh/max) applies to Opus 4.7 and later models only.
- **Chapter 05 / release-tag conditioning**: Capture the observation that
  Day-0 model support can ship on Stable tags (this post's
  `v1.83.3-stable`) or RC tags (Fable 5's `v1.89.0-rc.2`) depending on
  the vendor's release cycle timing. Operators should not assume a default
  tag maturity — check the specific post.
- **Chapter 05 / vendor documentation evolution**: Note that LiteLLM's
  "Day 0 Support" template expanded over time: earlier posts (Opus 4.7,
  April 2026) lacked pricing, data-sharing opt-ins, and silent-fallback
  disclosures that later posts (Fable 5, June 2026) carry. Operators
  consuming an older announcement for an earlier model should verify
  whether post-enablement compliance steps (data-sharing opt-in, security
  review) exist but were simply not documented in the older post format.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/claude_opus_4_7`, published April 16, 2026.
  Page fetched via direct HTML-to-text extraction. All quoted passages were
  copied character-for-character from the rendered page text.
- The page is self-contained (a single announcement with per-provider tabs).
  The only outbound links are "Newer post" / "Older post" sidebar
  navigations to unrelated articles, not followed.
- `confidence_overall` set to `emerging`: the first-party config and
  parameter-mapping detail is settled how-to documentation, but the post as
  a whole is a thin template announcement. Its primary value is as a
  historical/comparative data point against the Fable 5 note, and the
  temporal-placement conclusions drawn in this note (xhigh origin, Bedrock
  ID-evolution, template maturation) are this extractor's inferences from
  comparing two posts, not claims made by the source itself.
- No contradiction issue filed: verified against all existing source notes
  and open contradiction-labeled issues. The inter-post differences (effort
  framework awareness, Bedrock invocation style, template scope) are
  temporal evolution, not contradiction.
- Novelty per triage: low. This note is intentionally concise relative to
  the Fable 5 note — it extracts the delta rather than re-documenting the
  full operational pattern already captured there.
