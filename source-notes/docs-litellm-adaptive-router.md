---
source_url: https://docs.litellm.ai/docs/adaptive_router
source_type: docs
title: "[BETA] Adaptive Router — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-16)
date_extracted: 2026-09-16
last_checked: 2026-09-16
status: current
confidence_overall: emerging
issue: "#1345"
---

# [BETA] Adaptive Router (LiteLLM Docs)

> LiteLLM documents a **standalone** `auto_router/adaptive_router` router type —
> distinct from Auto Router v2's `adaptive: true` flag inside
> `complexity_router_config` — that runs a satisfaction-signal bandit over 7
> request types to balance quality against cost, but requires a Postgres
> database to persist what it learns (silently forgetting everything on restart
> without one), scores no latency term, and caps learning at 200 observations
> per cell with no decay.

## Source Context

- **Type**: docs (official LiteLLM product documentation, `[BETA]`-labeled reference page under both "Cost Optimization" and "Routing & Load Balancing").
- **Author credibility**: Vendor-authored reference for a shipped beta feature. Authoritative on config schema, headers, `/state` response shape, and documented behavior (incl. the limitations list); it offers **no benchmarks** for the claimed cost/quality balancing, so effectiveness claims are `emerging` and product-behavior claims are `settled`.
- **Scope**: Standalone Adaptive Router: quick-start config, cost/quality weights, min-quality override, 7-type request taxonomy, satisfaction-signal learning, `/state` inspection endpoint, and a verbatim "Known limitations" list. Does NOT cover: Auto Router v2 / `complexity_router_config` (covered by `blog-litellm-auto-router-v2.md`), benchmarks, or upgrade/compat notes between the two surfaces.

## Extracted Claims

### Claim 1: The standalone Adaptive Router is a separate config surface from Auto Router v2 — `model: auto_router/adaptive_router` with its own `adaptive_router_config` (`available_models`, `weights`) and per-model `adaptive_router_preferences` (`quality_tier` 1|2|3, `strengths`)
- **Evidence**: The Quick start config block shows a router entry (`model: auto_router/adaptive_router`) whose `adaptive_router_config` names `available_models` and `weights: {quality, cost}`, while each backing model carries `model_info.adaptive_router_preferences` with `quality_tier` and `strengths`. No `complexity_router_config` appears anywhere on the page — the config keys live in a different namespace than Auto Router v2's `adaptive: true` knob.
- **Confidence**: settled (documented config schema, verifiable against the reference page)
- **Quote**: (no single prose sentence; see Concrete Artifacts → Quick start config)
- **Our assessment**: This is the crux of contradiction #1150. As of 2026-09-16 the docs publish `auto_router/adaptive_router` as its own beta page with a config namespace independent of `complexity_router_config`, so the "unified Auto Router v2" collapse is evidently not total — the separate Adaptive flavor coexists with v2's `adaptive: true` flag. On the other hand, whether this is a legacy surface retained during migration or a still-actively-shipped product is not stated on the page. We record the taxonomy fact and defer the verdict to #1150 per MINER.md §4a.

### Claim 2: The router balances quality against cost per request type using a multi-armed-bandit-style mechanism — "tracks which model performs best for each type of request and routes accordingly"
- **Evidence**: The intro paragraph describing the mechanism, plus the mechanism's name ("moves the bandit", Claim 7) and the tuning table (Claim 4).
- **Confidence**: settled for the mechanism's existence as documented behavior; emerging for its effectiveness (no benchmarks on the page)
- **Quote**: "The adaptive router does this automatically. It tracks which model performs best for each type of request (code, writing, analysis, etc.) and routes accordingly, balancing quality against cost based on weights you control."
- **Our assessment**: The mechanism framing is a per-request-type, cost-weighted bandit. We buy the mechanism as documented; the page's implicit promise (cheap model when it's good enough, expensive when it matters) is unbenchmarked, which is why overall confidence is `emerging`. Operators adopting it should instrument spending before/after per the `/state` guidance (Claim 9).

### Claim 3: Postgres is a hard requirement for learned state — "Without a database the router works but forgets everything learned on restart"
- **Evidence**: The Requirements callout directly under the `[BETA]` label.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Quality estimates are stored in Postgres and loaded on startup. Without a database the router works but forgets everything learned on restart."
- **Our assessment**: Highest-value reliability claim on the page. Restart is a silent-reliability hazard: the router keeps serving but its bandit resets to cold-start priors with **no error and no warning signal**, so "it was learning our traffic" quietly becomes "it is using my declared tiers again." This is a textbook silent-degradation mode in the same family as `failure-litellm-model-cost-map-silent-fallback.md` (state/information loss outside the request path with no observability hook). A restart after a long training run is a routing-behavior change that no alert would fire for — it needs a planned check (see `/state`, Claim 9).

### Claim 4: `weights.quality` + `weights.cost` must sum to 1.0; published presets span 0.3/0.7 (cost-first) to 0.9/0.1 (quality non-negotiable), with quality-first 0.7/0.3 as the default
- **Evidence**: The config comment `# must sum to 1.0 with quality` and the full "Tuning cost vs. quality" table (Concrete Artifacts).
- **Confidence**: settled (documented config constraint and presets)
- **Quote**: "The `weights` are your main lever:"
- **Our assessment**: A validation gotcha (constraint that must hold or config is rejected) plus the primary operational lever. The 0.3/0.7 cost-first preset is stated but the "raise this if quality complaints; lower if bill too high" guidance is the extent of intent tuning — no guidance on how changing weights interacts with already-learned cells or cold-start.

### Claim 5: Cold-start is explicit — "For the first ~10 requests per model, it relies on the tiers you declared. After that, real performance data takes over"
- **Evidence**: The "Tuning cost vs. quality" section sentence following the weights table.
- **Confidence**: settled (documented behavior, with the "~" caveat)
- **Quote**: "The router learns over time. For the first ~10 requests per model, it relies on the tiers you declared. After that, real performance data takes over."
- **Our assessment**: Operator-visible blast-radius fact: the declared `quality_tier` is not just a fallback but the *initial policy* for roughly the first 10 requests per model. Combined with the `/state` `samples` field (starts at 0, cold-start prior mass excluded), an operator has a concrete "has it learned yet?" check rather than guessing.

### Claim 6: The router classifies every request into one of 7 types and tracks each model's performance per type independently — a model can win factual requests and lose code requests
- **Evidence**: The "What's being learned" section with the 7-type table (`code_generation`, `code_understanding`, `technical_design`, `analytical_reasoning`, `writing`, `factual_lookup`, `general`).
- **Confidence**: settled (documented classifier contract / taxonomy)
- **Quote**: "The router classifies each request into one of 7 types and tracks how each model performs on each independently. A model that's great at factual lookup but poor at code will win factual requests and lose code requests, even if it's cheaper overall."
- **Our assessment**: The 7-type contract is the concrete classifier surface an operator inherits: strengths are declared against exactly these type names (`strengths: ["code_generation", "analytical_reasoning"]` in the config), so a typing mistake (or a workload the taxonomy doesn't fit) falls into `general` "anything else". Note the taxonomy is a fixed enum with no documented way to extend it.

### Claim 7: Learning is driven by satisfaction signals on courtesy turns ("thanks!") that "move the bandit"; the signal design is regex-based and English-biased with no LLM judge, inspired by academic trajectory-sampling work
- **Evidence**: The curl example's trailing "thanks!" turn with the page's explanation, plus the inspiration citation link to an arXiv paper and the "Signals are regex-based and English-biased; there is no LLM judge" limitation.
- **Confidence**: settled (documented signal mechanism and signal-type limitation)
- **Quote**: "The \"thanks!\" turn in the example above fires a satisfaction signal, and that's what moves the bandit."
- **Quote**: "Learning signals are inspired by Signals: Trajectory Sampling and Triage for Agentic Interactions."
- **Our assessment**: Two operational consequences. First, the bandit's training signal depends on classifying courtesy turns in multi-turn sessions — a traffic pattern where users never say "thanks" (one-shot calls, strict output contracts, tool-heavy calls with no natural gratitude turn) produces very few/zero positive signals, so "learns from live traffic" can mean "learns from a thin slice of traffic." Second, regex-based, English-biased signals with no LLM judge means non-English or unusually-phrased interactions contribute noisily or not at all. The mechanism is honest documentation, which an SRE should weigh before trusting the bandit's quality estimates.

### Claim 8: Two escape hatches — `x-litellm-min-quality-tier` request header / `min_quality_tier` metadata forces a quality floor regardless of cost, and the `x-litellm-adaptive-router-model` response header reveals which model actually served
- **Evidence**: The "Force a minimum quality tier per request" section and the response-header example after the quick-start curl.
- **Confidence**: settled (documented headers)
- **Quote**: "If a specific request needs a frontier model regardless of cost, pass this header:"
- **Quote**: "You can also pass `min_quality_tier` via request metadata instead of a header."
- **Quote**: "The response includes a header telling you which model was actually picked:" (`x-litellm-adaptive-router-model: gpt-5.6-terra`)
- **Our assessment**: The min-quality override is the bandit's kill-switch for cost-independent quality requirements — the documented lever to say "this request must be frontier, do not let the weight function optimize this one." The response header gives per-request attribution of which model served, the counterpart to Auto Router v2's decision log. Together they form a minimum viable "force + verify" loop for routing policy.

### Claim 9: `GET /adaptive_router/{router_name}/state` exposes per-request-type × per-model cells of `quality_mean` and `samples`, where `samples` counts only real observations (cold-start prior mass excluded, starts at 0)
- **Evidence**: The "Inspect the current state" section with its sample JSON and the two explanatory sentences.
- **Confidence**: settled (documented endpoint and response shape)
- **Quote**: "Returns current quality estimates per model per request type. Useful for understanding why a model is or isn't being picked."
- **Quote**: "`quality_mean` is the key number: the router's current estimate of how well that model handles that request type. `samples` counts how many real observations have moved the prior (starts at 0; the cold-start prior mass is excluded)."
- **Our assessment**: Concrete inspection endpoint for Ch02. The `samples` semantic is important and easy to miss: it measures *learning progress*, not absolute request volume — a restart without Postgres (Claim 3) resets it to 0, so the endpoint doubles as the "did my router forget?" check. `quality_mean` at low `samples` is still mostly declared-tier prior, so operators should not read it as measured model quality until samples accumulate.

### Claim 10: Known limitations (vendor-stated): latency is not scored; signals are regex-based/English-biased with no LLM judge; a hard cap of 200 observations per cell with no decay; and only the session-selected model's turns contribute to learning
- **Evidence**: The verbatim "Known limitations" list at the end of the page.
- **Confidence**: settled (vendor-authored, documented behavior)
- **Quote**: "Latency isn't scored; a slow model can still win on quality + cost" / "Signals are regex-based and English-biased; there is no LLM judge" / "Hard cap of 200 observations per cell; no decay yet" / "Once a model is picked for a session, other models' turns in that session don't contribute to learning"
- **Our assessment**: The most candid vendor material on the page — a bounded-learning contract. Reading literally: (a) no latency term means a model that is slower but marginally better on quality+cost will win cells — for latency-sensitive agents this can be perverse; (b) a hard 200-observation cap **without decay** means non-stationary workloads (request-mix shifts, model upgrades) leave stale priors locked in beyond the cap, since further observations can't push the estimate toward the new reality; (c) per-session credit exclusion means multi-turn sessions rapidly hit the cap with unlearned marginal turns. Combined with Claim 3 (Postgres persistence) these are exactly the properties a routing SRE should put in front of "just trust the bandit."

### Claim 11: The feature is explicitly beta — "Beta feature"
- **Evidence**: The `[BETA]` heading and the info callout under it.
- **Confidence**: settled (documented status)
- **Quote**: "Beta feature. Share feedback on Discord or Slack."
- **Our assessment**: Status evidence directly material to contradiction #1150: the standalone Adaptive Router still ships as beta with its own config surface as of 2026-09-16, independent of Auto Router v2 (which is *also* beta-labeled per its own docs/blog). The beta label weakens any reading that "v2 replaced adaptive routing" wanted to pin as settled. No verdict picked here per MINER.md §4a.

## Concrete Artifacts

All artifacts below are verbatim from https://docs.litellm.ai/docs/adaptive_router (rendered content, checked 2026-09-16).

### Quick start config (verbatim)

```yaml
model_list:
  - model_name: gpt-5.6-terra
    litellm_params:
      model: openai/gpt-5.6-terra
    model_info:
      input_cost_per_token: 0.000002
      adaptive_router_preferences:
        quality_tier: 3
        # 1=budget, 2=mid, 3=frontier
        strengths: ["code_generation", "analytical_reasoning"]
  - model_name: gpt-5.6-luna
    litellm_params:
      model: openai/gpt-5.6-luna
    model_info:
      input_cost_per_token: 0.0000002
      adaptive_router_preferences:
        quality_tier: 2
        strengths: ["factual_lookup"]
  - model_name: my-router
    litellm_params:
      model: auto_router/adaptive_router
      adaptive_router_config:
        available_models: ["gpt-5.6-terra", "gpt-5.6-luna"]
        weights:
          quality: 0.7   # raise this if quality complaints; lower if bill too high
          cost: 0.3      # must sum to 1.0 with quality
```

### Example request with the satisfaction-signal turn (verbatim)

```
curl -X POST {{baseURL}}/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -d '{
    "model": "my-router",
    "messages": [
      {"role": "user", "content": "build me a python script that parses CSV"},
      {"role": "assistant", "content": "Here is a script using csv.DictReader..."},
      {"role": "user", "content": "now add error handling for missing files"},
      {"role": "assistant", "content": "Wrap the open() call in a try/except FileNotFoundError..."},
      {"role": "user", "content": "perfect, that worked. thanks!"}
    ]
  }'
```

### Weights tuning table (verbatim)

| Goal | quality | cost |
|---|---|---|
| Minimize cost, quality is secondary | 0.3 | 0.7 |
| Balanced | 0.5 | 0.5 |
| Quality-first (default) | 0.7 | 0.3 |
| Quality non-negotiable | 0.9 | 0.1 |

### 7-type request taxonomy (verbatim)

| Type | Example |
|---|---|
| `code_generation` | "write me a Python sort function" |
| `code_understanding` | "explain what this function does" |
| `technical_design` | "how should I design this API?" |
| `analytical_reasoning` | "calculate the probability that..." |
| `writing` | "draft an email to my team about..." |
| `factual_lookup` | "what is the capital of France?" |
| `general` | anything else |

### `/state` response shape (verbatim)

```
GET /adaptive_router/{router_name}/state

{
  "routers": [
    {
      "router_name": "smart-cheap-router",
      "available_models": ["fast", "smart"],
      "weights": { "quality": 0.7, "cost": 0.3 },
      "cells": [
        {
          "request_type": "analytical_reasoning",
          "model": "fast",
          "quality_mean": 0.5,
          "samples": 0
        },
        {
          "request_type": "analytical_reasoning",
          "model": "smart",
          "quality_mean": 0.95,
          "samples": 0
        }
      ]
    }
  ]
}
```

### Known limitations list (verbatim)

- Latency isn't scored; a slow model can still win on quality + cost
- Signals are regex-based and English-biased; there is no LLM judge
- Hard cap of 200 observations per cell; no decay yet
- Once a model is picked for a session, other models' turns in that session don't contribute to learning

## Cross-References

- **Corroborates**:
  - `blog-litellm-may-townhall-updates.md` **Claim 9** ("LiteLLM launched Adaptive Routing ... among a product batch") — this page documents that launched Adaptive Routing as a concrete, configurable standalone router, corroborating the launch claim with a full schema and behavior contract.
  - `blog-litellm-save-claude-code-costs.md` **Claim 7** — that note's Adaptive flavor description ("learns from live traffic, beta") matches the bandit mechanics and beta label documented here; the mechanism claim is corroborated and now has a full config surface behind it.
  - `blog-litellm-auto-router-v2.md` **Claim 6** (`adaptive: true` tier pools: "Feedback attributes back to the model that actually served the previous turn") — the standalone router's per-session credit rule (only the picked model's turns contribute) is the same credit-attribution philosophy, applied as a standalone product rather than a flag inside `complexity_router_config`.
  - `blog-litellm-save-claude-code-costs.md` **Claim 2** (budget fallbacks "silently fall to the first fallback still under its own budget") — same family of silent, non-erroring gateway behavior, echoed by the adaptive router's silent forget-on-restart (Claim 3 here).

- **Contradicts**:
  - **`blog-litellm-auto-router-v2.md` Claims 1 and 6** — the v2 blog asserts the three routing strategies "collapse into a single `auto_router/complexity_router`" and describes adaptive routing solely as `adaptive: true` inside `complexity_router_config`. This docs page ships `auto_router/adaptive_router` as a **separate config namespace** (`adaptive_router_config`, `adaptive_router_preferences`) and remains `[BETA]`-labeled as of 2026-09-16. That is direct evidence for open **contradiction [#1150](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1150)** ("three separate flavors, Adaptive 'beta' ... vs unified Auto Router v2"): the standalone flavor demonstrably still exists alongside the v2 knob. **No verdict assigned here** per MINER.md §4a — #1150 is already open, so no new contradiction issue was filed.
  - **`blog-litellm-save-claude-code-costs.md` Claim 7** — that note concluded "Only the Complexity router is documented with a concrete config example" and "Adaptive ... production readiness is unclear." This page contradicts the *documentation* half: the Adaptive Router now has a full config example, an `/state` endpoint, and a limitations list (still beta-labeled, so the readiness-clear caveat holds). This is within the scope of the already-filed #1150; no separate filing.

- **Extends**:
  - `blog-litellm-auto-router-v2.md` **Claim 6** — extends adaptive-routing coverage from a flag with Thompson-sampled pools inside `complexity_router_config` to a full standalone bandit product: its own config namespace (Claim 1 here), Postgres-persisted learned state (Claim 3), cold-start semantics (Claim 5), 7-type taxonomy (Claim 6), satisfaction-signal learning (Claim 7), min-quality override + attribution header (Claim 8), `/state` inspection (Claim 9), and the bounded-learning limitations (Claim 10).
  - `blog-litellm-may-townhall-updates.md` **Claim 9** — extends the Adaptive Routing launch mention (no config in that source) into a complete configuration and operations surface.
  - `failure-litellm-model-cost-map-silent-fallback.md` **Lessons 2–3** — extends the corpus's "silent state loss with no warning signal" thread: the forget-on-restart behavior (Claim 3 here) is out-of-path state erosion that request success metrics won't surface, directly parallel to "A fallback to cached/stale data ... MUST log a warning" and "if the failure is invisible to request success metrics, you need separate health checks." The no-decay 200-observation cap (Claim 10) is also a stale-state hazard: learned estimates stop tracking a shifting workload, and nothing logs it.

- **Novel**: First corpus coverage of:
  - The standalone `auto_router/adaptive_router` config surface (`adaptive_router_config` + per-model `adaptive_router_preferences` with `quality_tier` 1|2|3 and `strengths`) — distinct namespace from `complexity_router_config` (Claim 1).
  - The **7-way request taxonomy** as a fixed enum (`code_generation` … `general`), the `strengths` declaration contract against it, and the satisfaction-signal (gratitude-turn) learning mechanism (Claims 6, 7).
  - The **Postgres-forget-on-restart** silent-degradation mode and the `/state` endpoint's `samples`-starts-at-0 "has it learned yet" check (Claims 3, 9).
  - The `x-litellm-min-quality-tier` / `min_quality_tier` cost-independent quality floor and `x-litellm-adaptive-router-model` attribution header (Claim 8).
  - The vendor-stated bounded-learning limitations: no latency term, no LLM judge, 200-observations-per-cell cap with no decay, session-picked-model-only credit (Claim 10).

## Guide Impact

- **Chapter 05 (LLM Ops — Reliability / Routing)**: Add the standalone `auto_router/adaptive_router` as a **second, still-shipping adaptive surface** alongside Auto Router v2 (Claim 1), pending resolution of #1150. Specifically:
  - **Postgres-is-not-optional warning** (Claim 3): learned routing state lives in Postgres and is silently forgotten on restart without a DB. Recommend requiring Postgres and adding a scheduled `/state` check that samples > 0 per active cell (a restart wipes estimates with no alert).
  - **Bounded-learning caveat** (Claim 10): routing on this bandit inherits "no decay, 200 obs/cell, latency-blind, courtesy-turn-only signals" — do not rely on it as a quality oracle for non-stationary or latency-sensitive agent workloads; treat learned estimates as advisory and spot-check quality floors with `x-litellm-min-quality-tier`.
  - **Cold-start semantics** (Claim 5): first ~10 requests per model run on declared tiers — rollouts must budget the declared `quality_tier` policy as the actual initial behavior.
- **Chapter 02 (Observability)**: Add `GET /adaptive_router/{router_name}/state` and the `x-litellm-adaptive-router-model` response header as concrete routing-observability primitives (Claims 8, 9), with the `samples` field as a learning-progress metric (excludes cold-start prior mass; 0 = "not learned yet"). This is the standalone router's counterpart to Auto Router v2's decision log (`blog-litellm-auto-router-v2.md` Claim 8).
- **Chapter 04 (Oncall & Toil / debuggability)**: Document the debug limits — signals are regex-based and English-biased with no LLM judge (Claim 7), so "why is the bandit routing this way" is only partially answerable; and the `weights` "must sum to 1.0" validation gotcha (Claim 4) as a config-rejection trap. Pair the forget-on-restart mode with the corpus's silent-state-loss guidance (`failure-litellm-model-cost-map-silent-fallback.md` Lessons 2–3).

## Extraction Notes

- Source read in full via WebFetch (rendered page, checked 2026-09-16). No paywall or truncation.
- Followed the linked `[Beta] Auto Routing` page (`docs/proxy/auto_routing`) to establish the two-surface taxonomy claim (Claim 1): that page documents `auto_router/complexity_router` with `adaptive: true` as one of many knobs inside `complexity_router_config`, while this page documents `auto_router/adaptive_router` with independent keys. Confirmed they are separate shipped surfaces, not one superseding the other.
- The classifier source link on the page (`.../litellm/router_strategy/adaptive_router/classifier.py` on branch `litellm_adaptive_routing`) 404'd on fetch, so classifier internals were not verified beyond the page's own 7-type table and "regex-based, English-biased, no LLM judge" statement — claims are scoped to what the docs state.
- **Contradiction**: found both an internal-taxonomy tension (v2 blog "collapse" vs this standalone surface) and an external one (save-claude-code-costs Claim 7 "only Complexity documented"). Both map to **already-open contradiction #1150** — per MINER.md §4a the contradiction was NOT re-filed; this note records the evidence and defers the verdict.
- **Candidate dismissal** (from `miner-related-notes.md`, all read before writing Cross-References):
  - `docs-litellm-a2a-iteration-budgets.md` — A2A agent-loop cost caps (max_iterations / max_budget_per_session), unrelated to adaptive routing. Dismissed.
  - `docs-litellm-helicone-integration.md` — Helicone telemetry integration paths, unrelated to router config. Dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent-spectrum taxonomy, unrelated. Dismissed.
  - `docs-litellm-a2a-cost-tracking.md` — A2A per-agent cost tracking/chargeback, unrelated. Dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server, unrelated. Dismissed.
  - `docs-google-sre-eliminating-toil.md` — toil-reduction framework, unrelated. Dismissed.
  - `docs-langfuse-security-and-guardrails.md` — guardrail/security libraries, unrelated to routing. Dismissed.
  - `docs-litellm-a2a-agent-card.md` — A2A agent-card passthrough matrix, unrelated. Dismissed.
  - `blog-litellm-auto-router-v2.md` — cited (Contradicts Claims 1/6; Corroborates Claim 6; Extends Claim 6).
  - `blog-litellm-save-claude-code-costs.md` — cited (Corroborates Claims 2/7; Contradicts Claim 7; Extends Claim 7).
- Cross-references beyond the candidate list were verified directly against the cited notes (`blog-litellm-may-townhall-updates.md` Claim 9; `failure-litellm-model-cost-map-silent-fallback.md` Lessons 2–3) per MINER.md §4b.
- `confidence_overall` is `emerging`: config schema, headers, `/state` shape, requirements, and limitation behavior are individually `settled` (documented product behavior), but the feature is beta-labeled, its effectiveness/cost-savings claims are unbenchmarked, and — per the Prospector's guidance — the page's own candid limitations mean the overall operational trustworthiness story is not settled.
- This source was extracted under live trial #571 (zen-free OpenCode runner, model `opencode/big-pickle`).