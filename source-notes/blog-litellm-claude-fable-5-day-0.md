---
source_url: https://docs.litellm.ai/blog/claude_fable_5
source_type: blog-post
title: "Day 0 Support: Claude Fable 5"
author: "Mateo Wang (AI Engineer, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-06-10
date_extracted: 2026-07-15
last_checked: 2026-07-15
status: current
confidence_overall: emerging
issue: "#258"
---

# Day 0 Support: Claude Fable 5

> A LiteLLM vendor announcement documenting how to run Claude Fable 5 through
> the LiteLLM gateway across Anthropic, Azure, Vertex AI, and Bedrock —
> capturing the provider-specific opt-in requirements, the cost-map reload
> path used to pick the model up, adaptive-thinking / effort-level parameter
> mapping, and Bedrock-specific constraints that are the operationally
> load-bearing details for a gateway operator.

## Source Context

- **Type**: blog-post (vendor "Day 0 support" product announcement on
  `docs.litellm.ai/blog`), tagged `anthropic`, `claude`, `fable 5`,
  `day 0 support`.
- **Author credibility**: High for *how LiteLLM itself routes and configures
  the model* — authored by a LiteLLM AI Engineer (Mateo Wang) and the
  company's CEO (Krrish Dholakia) and CTO (Ishaan Jaffer), i.e. the
  maintainers of the gateway. The config/opt-in/parameter-mapping detail is
  first-party documentation. The *model-capability* claims (benchmarks,
  fallback rate, context length) are explicitly attributed to Anthropic and
  are vendor-reported, not independently measured here.
- **Scope**: Covers (1) multi-provider Day-0 availability through one
  OpenAI-compatible interface, (2) Fable 5 specs and pricing as the gateway
  sees them, (3) per-cloud data-sharing opt-ins, (4) how to enable the model
  (remote vs. local cost map), (5) per-provider `config.yaml` examples, and
  (6) adaptive-thinking / effort-level parameter mapping. Does NOT cover:
  production metrics, latency/throughput measurements, failure analysis, or
  any practitioner outcome — it is a launch/how-to post.

## Extracted Claims

### Claim 1: LiteLLM supports Claude Fable 5 on Day 0 across four provider backends behind one OpenAI-compatible request
- **Evidence**: Opening statement of the post; the entire body then shows one
  `model_name: claude-fable-5` alias configured against Anthropic, Azure,
  Vertex AI, and Bedrock backends.
- **Confidence**: settled (it is the vendor documenting its own supported
  routing; the config examples are concrete).
- **Quote**: "LiteLLM now supports Claude Fable 5 on Day 0. Use it across Anthropic, Azure, Vertex AI, and Bedrock through the LiteLLM AI Gateway. Call it with the same OpenAI-compatible request you already use, and track spend, rate limits, and logging in one place."
- **Our assessment**: This is the load-bearing operational value — one alias,
  four backends, unified spend/rate-limit/logging. It is exactly the
  model-gateway responsibility set the corpus already documents (see
  Cross-References), applied to a specific new model. Credible and concrete.

### Claim 2: Fable 5 is Anthropic's first publicly available Mythos-class model, priced at 2x Opus 4.8
- **Evidence**: Stated as the framing for "what's new"; positioning claim
  attributed to the model's release.
- **Confidence**: emerging (vendor/positioning claim; "Mythos-class" is a
  marketing tier label, and the 2x-Opus price ratio is a point-in-time fact
  tied to a specific release).
- **Quote**: "Fable 5 is Anthropic's first publicly available Mythos-class model, priced at 2x Opus 4.8."
- **Our assessment**: Useful only as a relative-cost anchor (Fable 5 ≈ 2x
  Opus 4.8) for capacity/spend planning. The tier label is not operationally
  actionable. Ephemeral — pricing ratios change across releases.

### Claim 3: Fable 5 offers a 1M-token context window and up to 128K output tokens for long-horizon agentic work
- **Evidence**: Listed under "What's new," attributed to the model's design
  for long-running tasks.
- **Confidence**: emerging (vendor-reported spec; not measured in-post).
- **Quote**: "A 1M-token context window and up to 128K output tokens, with focus that holds across millions of tokens in long-horizon agentic tasks."
- **Our assessment**: The 1M-context / 128K-output figures are the
  operationally relevant part for anyone sizing prompts, chunking, or
  budgeting output caps at the gateway. The "focus that holds across millions
  of tokens" phrasing is a qualitative vendor claim, not a benchmark — treat
  as marketing, not a guarantee.

### Claim 4: Fable 5 supports adaptive thinking only; fixed thinking budgets, temperature, top_p, and assistant-message prefill are not supported
- **Evidence**: Stated in "What's new" and reinforced in the Advanced
  Features → Adaptive Thinking note, which says explicit budgets return a 400.
- **Confidence**: settled (this is a hard API constraint the gateway must
  honor; the post states the exact rejection behavior).
- **Quote**: "Fable 5 decides how deeply to think on its own. You steer it per request with reasoning_effort or output_config.effort; fixed thinking budgets, temperature, top_p, and assistant message prefill are not supported by the model."
- **Our assessment**: This is the highest-value operational gotcha in the
  post. Teams migrating existing prompts to Fable 5 that set `temperature`,
  `top_p`, prefill, or explicit thinking budgets will hit failures or silent
  no-ops. A gateway operator should strip/reject those params for this model.
  See Claim 8 for the exact 400 behavior on explicit budgets.

### Claim 5: Pricing is $10/MTok input and $50/MTok output, with prompt caching at $1.00/MTok read and $12.50/MTok write, plus a Bedrock regional premium
- **Evidence**: Enumerated pricing bullet; Bedrock `us.`/`eu.` inference
  profiles are stated to carry a 10% premium over `global.`.
- **Confidence**: emerging (point-in-time pricing tied to this release;
  vendor-reported).
- **Quote**: "$10 / MTok input and $50 / MTok output, with prompt caching at $1.00 / MTok (read) and $12.50 / MTok (write). On Bedrock, the us. and eu. inference profiles carry the usual 10% regional premium while global. stays at base price; LiteLLM tracks every variant automatically."
- **Our assessment**: The concrete spend-planning inputs. The
  operationally novel detail is the **Bedrock regional premium** (`us.`/`eu.`
  +10% vs `global.` base) and that LiteLLM tracks each inference-profile
  variant as a distinct priced entity — relevant to anyone doing per-region
  cost attribution. Pricing itself is ephemeral; the *structure* (regional
  premium on inference-profile prefixes) is the reusable takeaway.

### Claim 6: On flagged cybersecurity and biology requests (<5% of sessions), the response is served by Opus 4.8 instead of Fable 5
- **Evidence**: Listed under "What's new"; rate and framing attributed to
  Anthropic.
- **Confidence**: emerging (vendor-reported behavior; the "under 5%" figure
  is Anthropic's, not measured here).
- **Quote**: "On flagged cybersecurity and biology requests (under 5% of sessions, per Anthropic), the response is served by Opus 4.8 instead."
- **Our assessment**: A genuinely operational surprise: a request billed and
  routed as Fable 5 may be silently answered by a *different model*. For
  observability this matters — response quality, latency, and (potentially)
  model-attribution in logs can vary on a minority of requests for these
  domains. Teams doing eval or per-model SLOs should account for this
  invisible fallback. This is the most novel detail in the post for the
  guide's observability/attribution material.

### Claim 7: Fable 5 requires a per-cloud data-sharing opt-in; prompts are shared with Anthropic and retained up to 30 days
- **Evidence**: Stated in "Before you flip it on," with distinct opt-in steps
  per cloud (Bedrock, Vertex AI, Azure AI Foundry).
- **Confidence**: settled (concrete, provider-specific enablement
  requirements the operator must satisfy before the model works).
- **Quote**: "Fable 5 requires a data sharing opt-in on some clouds; prompts are shared with Anthropic and retained for up to 30 days."
- **Quote**: "Bedrock: set your account's data retention mode to provider_data_share, and invoke through an inference profile (us., eu., or global. prefix); direct model ID invocation is not supported."
- **Our assessment**: This is a compliance/governance gate, not just a config
  step — enabling Fable 5 means opting into 30-day prompt retention at
  Anthropic. That has direct data-governance implications for regulated
  workloads and should be surfaced to a security/compliance owner before
  enablement, not treated as a routine model add. The per-cloud opt-in
  mechanics (data-retention mode on Bedrock, Model Garden terms on Vertex,
  deployment + quota on Azure) are the concrete blockers a gateway operator
  hits first.

### Claim 8: `reasoning_effort` is mapped to adaptive thinking; explicit thinking budgets are rejected by the Anthropic API with a 400
- **Evidence**: Advanced Features → Adaptive Thinking note states the exact
  mapping and the exact failure mode for explicit budgets.
- **Confidence**: settled (specific, testable API behavior documented by the
  gateway maintainer).
- **Quote**: "When using reasoning_effort with Claude Fable 5, all values are mapped to thinking: {type: \"adaptive\"}. Fable 5 only supports adaptive thinking; explicit budgets via thinking: {type: \"enabled\", budget_tokens: ...} are rejected by the Anthropic API with a 400 error."
- **Our assessment**: The concrete mechanism behind Claim 4. Operationally:
  code that passes `thinking: {type: "enabled", budget_tokens: N}` (valid on
  earlier Claude models) will 400 against Fable 5. The migration path is to
  drop explicit budgets and use `reasoning_effort` / `output_config.effort`.
  A gateway can normalize this, but callers hitting the model directly will
  break — a real migration hazard.

### Claim 9: Fable 5 exposes a five-rung effort ladder (low/medium/high/xhigh/max) via `output_config.effort`, but Bedrock caps effort at `xhigh`
- **Evidence**: Advanced Features → Effort Levels enumerates the ladder,
  names `high` as default, and states the Bedrock cap explicitly.
- **Confidence**: settled (explicit, provider-conditioned behavior with a
  documented ceiling).
- **Quote**: "Claude Fable 5 supports the full effort ladder: low, medium, high (default), xhigh, and max."
- **Quote**: "On Bedrock, output_config.effort caps at xhigh; the other providers accept the full ladder up to max."
- **Our assessment**: The Bedrock `xhigh` cap is a real cross-provider
  behavior divergence: the *same* alias produces different maximum reasoning
  depth depending on backend. For a multi-backend gateway with fallbacks,
  a request asking for `max` effort will not behave identically if it lands
  on Bedrock vs Anthropic/Azure/Vertex — a subtle correctness/consistency
  concern for routing and evals. This is a conditioning variable, not a
  contradiction (see Cross-References).

### Claim 10: The model is picked up via a cost-map reload (remote map) or a proxy image upgrade (local baked map), shipping first in `v1.89.0-rc.2`
- **Evidence**: "Enabling Fable 5" section distinguishes the default remote
  cost-map path (reload, no upgrade) from `LITELLM_LOCAL_MODEL_COST_MAP=true`
  (baked map, requires pulling the new image).
- **Confidence**: settled (specific enablement procedure with a named image
  tag and admin endpoint).
- **Quote**: "In the LiteLLM UI, open the Price Data tab under Models + Endpoints and click Reload Price Data (or, as a proxy admin, POST /reload/model_cost_map). This refetches the latest pricing from LiteLLM's cost map and re-registers provider routing in one step, so claude-fable-5 becomes available across Anthropic, Azure, Vertex AI, and Bedrock, even if you're on an older proxy version."
- **Quote**: "Running LITELLM_LOCAL_MODEL_COST_MAP=true? The cost map is baked into the image, so the Reload button won't reach it. Pull v1.89.0-rc.2 or later to get the bundled Fable 5 metadata"
- **Our assessment**: This is the operational crux — and it connects directly
  to the wildcard-desync incident in the corpus (see Cross-References →
  Extends). The post tells operators to `POST /reload/model_cost_map` to make
  a *new model* available; that is the very reload path whose partial-reload
  desync once returned 401 for newly-added models. Anyone following this
  enablement procedure should validate the model is actually reachable
  (end-to-end request), not just that the cost map reload "succeeded."

### Claim 11: On Bedrock the model must be invoked through an inference profile prefix; the bare model ID returns a validation error
- **Evidence**: Bedrock usage `note` block and the data-sharing opt-in both
  state the inference-profile requirement; the `config.yaml` uses
  `bedrock/converse/us.anthropic.claude-fable-5`.
- **Confidence**: settled (explicit constraint with a named failure mode).
- **Quote**: "Bedrock only serves Fable 5 through inference profiles, so the model ID must carry a us., eu., or global. prefix. Invoking the bare anthropic.claude-fable-5 model ID returns a validation error."
- **Our assessment**: A precise Bedrock-specific footgun. Combined with the
  regional-premium pricing (Claim 5) and the `xhigh` effort cap (Claim 9),
  Bedrock is the most constrained of the four backends for this model — worth
  calling out for teams standardizing on Bedrock.

### Claim 12: Full feature surface (vision, PDF input, computer use, tool calling, prompt caching, adaptive thinking, structured output) is available across all four backends with unified spend/logging/fallbacks
- **Evidence**: Final "What's new" bullet enumerating supported capabilities
  and the unified operational surface.
- **Confidence**: emerging (vendor claim of feature parity across backends;
  not independently verified, and Claim 9's Bedrock cap shows parity is not
  total).
- **Quote**: "Vision, PDF input, computer use, tool calling, prompt caching, adaptive thinking, and structured output, all available across Anthropic, Azure, Vertex AI, and Bedrock with unified spend tracking, logging, and fallbacks."
- **Our assessment**: The "all available across [all backends]" framing is
  slightly overstated given the post itself documents Bedrock-specific
  limits (inference-profile-only, `xhigh` effort cap, regional premium).
  Read it as "broadly available, with backend-specific caveats documented
  elsewhere in the same post." Useful as a capability checklist, not as a
  guarantee of exact cross-backend parity.

## Concrete Artifacts

All artifacts below are copied from the source page. Inline-code spans in the
rendered page (e.g. YAML keys, model IDs) are reproduced as they read on the
page; no words were added or removed.

### Per-provider `config.yaml` model aliases (verbatim)

```yaml
# Anthropic
model_list:
  - model_name: claude-fable-5
    litellm_params:
      model: anthropic/claude-fable-5
      api_key: os.environ/ANTHROPIC_API_KEY

# Azure (Azure AI Foundry)
model_list:
  - model_name: claude-fable-5
    litellm_params:
      model: azure_ai/claude-fable-5
      api_key: os.environ/AZURE_AI_API_KEY
      api_base: os.environ/AZURE_AI_API_BASE  # https://<resource>.services.ai.azure.com

# Vertex AI
model_list:
  - model_name: claude-fable-5
    litellm_params:
      model: vertex_ai/claude-fable-5
      vertex_project: os.environ/VERTEX_PROJECT
      vertex_location: global

# Bedrock (inference-profile prefix required)
model_list:
  - model_name: claude-fable-5
    litellm_params:
      model: bedrock/converse/us.anthropic.claude-fable-5
      aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
      aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
      aws_region_name: us-east-1
```

### Enabling the model — local baked cost map path (verbatim command)

```
docker pull ghcr.io/berriai/litellm:v1.89.0-rc.2
```

### Adaptive thinking via `reasoning_effort` (verbatim request)

```
curl --location 'http://0.0.0.0:4000/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer $LITELLM_KEY' \
--data '{
  "model": "claude-fable-5",
  "messages": [
    {
      "role": "user",
      "content": "Solve this complex problem: What is the optimal strategy for..."
    }
  ],
  "reasoning_effort": "high"
}'
```

### Effort levels via `output_config.effort` — SDK forms (verbatim)

```python
# OpenAI SDK
import openai
client = openai.OpenAI(
    api_key="your-litellm-key",
    base_url="http://0.0.0.0:4000"
)
response = client.chat.completions.create(
    model="claude-fable-5",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    extra_body={"output_config": {"effort": "max"}}
)

# LiteLLM SDK
from litellm import completion
response = completion(
    model="anthropic/claude-fable-5",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    output_config={"effort": "max"},
)
```

### Effort-level guide (verbatim table content)

```
Effort   When to use
low      Short, fast responses for simple lookups, formatting, and classification
medium   Balanced tradeoff for everyday Q&A and light reasoning
high     (default) Complex reasoning, code generation, analysis
xhigh    Hard problems like multi-step math, deep research, and agentic planning
max      The hardest tasks where you want maximum reasoning depth regardless of
         latency (not available on Bedrock)
```

## Cross-References

- **Corroborates**:
  - `blog-litellm-agents-are-the-new-llms.md` (Concrete Artifacts →
    "Model-gateway responsibilities the post says the control plane builds
    on", verbatim: "Gateway: routing, fallbacks, logging, spend tracking,
    auth, billing"). This Fable 5 post is a concrete instance of exactly
    those gateway responsibilities — "track spend, rate limits, and logging
    in one place" (Claim 1) and "unified spend tracking, logging, and
    fallbacks" (Claim 12). Same vendor; that note describes the gateway
    responsibility set in the abstract, this one exercises it for a specific
    model.

- **Contradicts**: None. No contradiction issue filed. Verified against all
  existing source notes: no note asserts Fable 5 specs, pricing, or
  parameter support, so there is nothing to oppose. The cross-provider
  divergences inside this post (Bedrock `xhigh` effort cap vs `max`
  elsewhere; regional pricing premium) are **conditioning variables**
  (behavior differs *by backend*), not contradictions per MINER.md §4
  ("Claims differ only in context … that's not a contradiction, that's a
  conditioning variable").

- **Extends**:
  - `failure-litellm-wildcard-model-access-desync.md` — HIGH-VALUE link.
    That incident report documents how `POST /reload/model_cost_map` (its
    Concrete Artifacts show that exact endpoint and the periodic
    `_check_and_reload_model_cost_map` path) once updated the cost map but
    left the in-memory provider set stale, returning 401 for *newly-added
    models*. This post's Claim 10 tells operators to use that same reload
    path to make a newly-added model (`claude-fable-5`) available. Its
    Lesson 4 ("A successful reload that updates the primary cache can still
    silently break dependent access control — reload success ≠ end-to-end
    health") is the exact caution that applies to anyone enabling Fable 5 by
    reload. This post is the *routine operation* whose failure mode that
    incident report analyzes.
  - `blog-litellm-april-townhall-updates.md` (Claim 6 — the 4-tier
    release-tag taxonomy: Dev / Nightly / Release Candidate / Stable) — this
    post ships Fable 5 first in `v1.89.0-rc.2`, i.e. a **Release Candidate**
    tag under that taxonomy. Concrete illustration that Day-0 model support
    lands on an RC image (per that note's definition, "Passes all CI/CD
    checks + manual UI QA") before a Stable release, which is worth flagging
    for operators weighing whether to adopt a new model on an RC build.

- **Novel**: First source note in the corpus to capture:
  - Model-specific gateway enablement mechanics for a single Claude model
    across Anthropic / Azure / Vertex AI / Bedrock (per-provider
    `config.yaml` aliases and env wiring).
  - The **silent minority fallback** to a different model (Opus 4.8 on
    flagged cybersecurity/biology requests, <5% of sessions) — new to the
    corpus as an observability/attribution hazard.
  - **Adaptive-thinking-only** parameter constraints (no fixed budgets,
    `temperature`, `top_p`, or prefill; explicit budgets → 400) and the
    `reasoning_effort` → adaptive mapping.
  - The five-rung effort ladder (low/medium/high/xhigh/max) with a
    **Bedrock `xhigh` cap** — a documented cross-provider behavior
    divergence.
  - Provider **data-sharing opt-ins with 30-day prompt retention** as a
    precondition to enablement (a governance gate, not just config).
  - Bedrock **inference-profile-prefix requirement** (bare model ID → 400
    validation error) and the `us.`/`eu.` **10% regional pricing premium**
    over `global.`.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add a "new-model enablement" note:
  when adopting a new model on an LLM gateway, enablement may be a cost-map
  reload (`POST /reload/model_cost_map`) rather than a redeploy — and, per
  the wildcard-desync incident, a reported-successful reload is not proof the
  model is actually reachable. Recommend a post-enablement end-to-end health
  check (a real request to the new alias on each backend), not just "cost map
  reloaded." Also capture that Day-0 support may only be on a Release
  Candidate image (`v1.89.0-rc.2`), so adopting a new model can mean running
  an RC build.
- **Chapter 05 / capacity & spend**: Record the reusable *structure* (not the
  ephemeral numbers): inference-profile-prefixed backends can carry a regional
  pricing premium (Bedrock `us.`/`eu.` +10% vs `global.`), and a gateway
  should track each variant as a distinct priced entity for accurate
  per-region cost attribution.
- **Chapter 02 (Observability) / model attribution**: Add the silent-fallback
  hazard — a request routed and billed as one model may be served by another
  (Fable 5 → Opus 4.8 on flagged cyber/bio requests). Per-model SLOs, evals,
  and cost/quality attribution must not assume the responding model equals the
  requested model for the affected request classes.
- **Chapter 05 / migration hazards**: Document adaptive-thinking-only models
  as a migration break: prompts/params valid on earlier Claude models
  (`temperature`, `top_p`, assistant prefill, explicit `thinking` budgets)
  are unsupported and explicit budgets return a 400; migrate to
  `reasoning_effort` / `output_config.effort`. Note the cross-provider effort
  ceiling (Bedrock caps at `xhigh`) as a consistency caveat for multi-backend
  routing and fallbacks.
- **Chapter 06 (Security and Trust) / data governance**: Add that enabling
  some hosted models requires opting into provider data sharing with a defined
  retention window (here, prompts shared with Anthropic, retained up to 30
  days). Frame enablement of such a model as a compliance decision with a
  named owner, not a routine config change.

## Extraction Notes

- Source read in full. Docusaurus blog post at
  `https://docs.litellm.ai/blog/claude_fable_5`. WebFetch returned an empty
  response for this host (the same behavior the sibling LiteLLM notes
  recorded), so the page was fetched via direct HTTP (curl) and
  HTML-to-text extraction. All quoted passages were copied from the rendered
  page text; where the page renders values inside inline `<code>` spans
  (YAML keys, model IDs, parameter names), the surrounding spacing was
  normalized to how the sentence reads on the page — no words were added,
  removed, or reordered inside any quote.
- The page is self-contained (a single announcement with per-provider tabs);
  the only outbound link is "details from Anthropic" for benchmark claims,
  which was not followed because the benchmark figures are explicitly
  attributed to Anthropic and are not the mineable LiteLLM-specific content
  the triage asked for. Nothing paywalled or truncated.
- `confidence_overall` set to `emerging`: the first-party config, opt-in, and
  parameter-mapping detail is effectively settled how-to, but the post as a
  whole mixes that with ephemeral, release-tied specs (pricing, image tag)
  and vendor/Anthropic-attributed capability claims (benchmarks, context
  length, <5% fallback rate) that are not independently verified. This
  matches the `emerging` rating on the two sibling LiteLLM blog notes.
- Novelty per triage: low (a standard "Day 0 support" announcement). The
  mineable, non-obvious content is the LiteLLM-specific operational detail —
  the cost-map reload enablement path (and its tie to the wildcard-desync
  incident), the silent Opus 4.8 fallback, the adaptive-thinking-only
  parameter constraints, the Bedrock inference-profile / effort-cap /
  regional-premium specifics, and the 30-day data-sharing opt-in — all
  captured above.
- No contradiction issue filed: verified against all existing source notes
  and `CONTRADICTIONS.md` (no open `C-NNN` entries). No note makes an opposing
  claim about Fable 5 or its parameters; the intra-post cross-provider
  differences are conditioning variables, not contradictions.
- The page header renders the byline date as "June 10, 2026"; recorded as
  `date_published: 2026-06-10`. Flagged here because it coincides with a
  sibling LiteLLM post's date and may be a template/byline artifact rather
  than the true publish date — the Assayer may wish to spot-check.
