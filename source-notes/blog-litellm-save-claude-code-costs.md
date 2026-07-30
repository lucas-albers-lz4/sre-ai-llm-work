---
source_url: https://docs.litellm.ai/blog/save-claude-code-costs-with-litellm
source_type: blog-post
title: "5 ways to cut Claude Code costs with LiteLLM"
author: "Krrish Dholakia (CEO, LiteLLM)"
date_published: 2026-07-04
date_extracted: 2026-07-30
last_checked: 2026-07-30
status: current
confidence_overall: emerging
issue: "#668"
---

# 5 Ways to Cut Claude Code Costs with LiteLLM

> A vendor blog post from LiteLLM's CEO describing five composable proxy-level levers for reducing Claude Code input-token spend — budget windows + fallback chains, automatic prompt caching injection, prompt compression (Headroom), MCP tool search, and auto routing — each with concrete config examples and the claim that they compose orthogonally without client-side changes.

## Source Context

- **Type**: blog-post (vendor engineering blog on docs.litellm.ai), tagged `claude-code`, `cost`, `budgets`, `headroom`, `mcp`, `prompt-caching`. Published July 4, 2026.
- **Author credibility**: Krrish Dholakia is CEO of LiteLLM (BerriAI). Claims about how LiteLLM features work are authoritative for LiteLLM product behavior. Claims about cost savings are vendor marketing without independent methodology, benchmarks, or user studies. The config examples (curl commands, YAML) are concrete and reproducible.
- **Scope**: Covers (1) budget windows with stacked durations, (2) budget fallback chains with per-model limits, (3) automatic prompt caching injection via `cache_control_injection_points`, (4) prompt compression via Headroom sidecar guardrail, (5) MCP tool search as a token-overhead reduction pattern, (6) auto routing with three flavors (complexity/semantic/adaptive), (7) the composition insight that all five levers work together. Does NOT cover: independent benchmarks, latency impact measurements, failure modes, or comparison with other cost-optimization approaches.

## Extracted Claims

### Claim 1: Budget windows with stacked durations cap virtual-key spend within rolling time periods, resetting automatically — multiple windows can be stacked to prevent a short burst from exhausting a monthly budget
- **Evidence**: The article explicitly describes the feature with a curl example showing `budget_limits` with two stacked windows (24h $10 + 30d $100), explaining that LiteLLM resets the counter at the end of every window.
- **Confidence**: settled (documented LiteLLM product feature, verifiable from config)
- **Quote**: "Budget windows cap how much the key can spend inside a rolling time period. Set max_budget (dollars) and budget_duration ("24h", "7d", "30d", etc). LiteLLM resets the counter automatically at the end of every window. You can stack windows too, e.g. $10/day AND $100/month, so one bad afternoon can't burn the whole month"
- **Our assessment**: A concrete, configurable spend-control feature. The stacked-window pattern is notable as a defense against burst spend within a monthly budget. This is the corpus's first coverage of budget windows with stacked durations at the proxy level.

### Claim 2: Budget fallback chains route requests to cheaper models when a per-model budget is exhausted — the request silently falls to the first fallback still under its own budget, without erroring at the developer's terminal
- **Evidence**: Config example shows `model_max_budget` with per-model daily limits (Opus $20/d, Sonnet $10/d, Haiku $5/d) and `budget_fallbacks` chains (Opus → Sonnet → Haiku). The article explains the cascade behavior.
- **Confidence**: settled (documented LiteLLM product feature with concrete config)
- **Quote**: "Budget fallbacks decide what happens once a per-model budget is exhausted. Instead of erroring at the developer's terminal, attach model_max_budget per model and a budget_fallbacks chain naming the cheaper models to reroute to. The request silently falls to the first fallback still under its own budget"
- **Our assessment**: This is the most novel budget pattern in the source — it provides a graceful degradation path for spend governance that is transparent to the developer. The per-model budget limits create a multi-level cost ceiling without hard-blocking work. Fallback models without a `model_max_budget` entry are treated as unlimited, which is an important operational detail for configuration.

### Claim 3: LiteLLM auto-injects cache_control markers at configurable injection points (system message or second-to-last user turn), enabling Claude's prompt cache without client-side changes, and can optionally route to the initially used deployment when multiple deployments of the same model exist
- **Evidence**: Two config.yaml examples show per-model and global `cache_control_injection_points` configuration, plus `optional_pre_call_checks: ["prompt_caching"]` for multi-deployment routing. The article states prompt cache hits cost "roughly 10% of the price of a fresh input token."
- **Confidence**: settled (documented product feature)
- **Quote**: "Claude's prompt cache reads a cache hit for roughly 10% of the price of a fresh input token, but only if the request marks the right message with cache_control. LiteLLM injects that marker for you: point cache_control_injection_points at the system message (or the second-to-last user turn), and every Claude Code call through the proxy carries the checkpoint without any client-side edit."
- **Quote**: "Turning on 'prompt_caching' as a pre call check, means if you run multiple deployments of the same Claude model, LiteLLM will intelligently route to the model deployment which was initially used for the request."
- **Our assessment**: The auto-injection pattern eliminates the most common barrier to prompt caching adoption — correct placement of `cache_control` markers. The dual config modes (per-model vs. global `default_litellm_params`) provide deployment flexibility. The 10% cache-hit pricing is Claude API pricing, not a LiteLLm claim; the contribution is the proxy-side injection mechanism. This is the corpus's first coverage of proxy-side automatic cache_control injection.

### Claim 4: The MCP Tool Search feature replaces the full MCP tool catalog with two virtual search/call tools (mcp_tool_search and mcp_tool_call), collapsing token overhead from hundreds of tool schemas to two
- **Evidence**: The article describes the problem (hundreds of tools, every schema on every `tools/list` call) and the mechanism (enabling `mcp_tool_search_enabled` on the virtual key replaces the catalog with two tools). A curl example shows the configuration on `/key/generate`.
- **Confidence**: settled (documented product feature with config example)
- **Quote**: "A Claude Code session that connects to five or six MCP servers can easily surface a few hundred tools, and every one of those tool schemas ships on every tools/list call. That is pure input-token overhead on a workload where the model uses two or three tools per turn."
- **Quote**: "Turn on mcp_tool_search_enabled on the virtual key, and LiteLLM replaces the full catalog with two virtual tools, mcp_tool_search and mcp_tool_call. The model searches by keyword, gets the ranked matches back, and calls the one it wants. The token cost of tool listing collapses from hundreds of schemas to two."
- **Our assessment**: This is a significant token-optimization pattern for tool-heavy Claude Code sessions. The insight is that most tool schemas are never used in a given turn but still consume input tokens on every request. Replacing the full catalog with a search interface is an elegant proxy-level solution. This is entirely novel for the corpus — no existing note covers MCP tool search as a token-cost reduction pattern.

### Claim 5: MCP Tool Search uses token-overlap ranking over name + description with no embedding dependency, and does not widen the access surface — search only returns tools the key was already allowed to call
- **Evidence**: The article states both properties explicitly.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Ranking is token-overlap over name + description, so there is no embedding dependency to run. The access surface does not widen; search only returns tools the key was already allowed to call."
- **Our assessment**: The no-embedding-dependency design is a pragmatic operational choice — it means zero additional infrastructure (no vector DB, no embedding API) and no cold-start issue for new tools. The access-preservation property is security-critical: the tool search only surfaces tools the key already has permission to call, so enabling the feature cannot inadvertently broaden access. Both properties are worth capturing for the guide.

### Claim 6: The Complexity router classifies Claude Code requests into four tiers (SIMPLE → MEDIUM → COMPLEX → REASONING) and routes to the appropriate model — it is rule-based, requires zero external API calls, and is the fastest auto-routing flavor to set up
- **Evidence**: Config.yaml example shows `auto_router/complexity_router` with `complexity_router_config` mapping the four tiers to specific models (gpt-4o-mini, gpt-4o, claude-sonnet, o1-preview). The article describes it as "the fastest to set up" and the Claude Code endpoint is `smart-router`.
- **Confidence**: settled (documented product feature with concrete config)
- **Quote**: "Complexity router is the fastest to set up. Point Claude Code at smart-router and it classifies each request into a tier"
- **Our assessment**: The four-tier classification (SIMPLE → MEDIUM → COMPLEX → REASONING) maps well to common Claude Code workloads. The zero-external-call design (rule-based classification, no embedding API call) is a pragmatic choice for latency-sensitive proxy routing. The config is immediately reproducible. This is the corpus's first coverage of proxy-level request routing by complexity for Claude Code.

### Claim 7: LiteLLM ships three auto-routing flavors — Semantic (embedding match), Complexity (rule-based, zero external call), and Adaptive (learns from live traffic, beta)
- **Evidence**: The article enumerates all three flavors in a single sentence.
- **Confidence**: emerging (feature existence is settled, but Adaptive is labeled beta and no config examples are provided for Semantic or Adaptive)
- **Quote**: "LiteLLM ships three flavors: Semantic (embedding match), Complexity (rule-based, zero external call), and Adaptive (learns from live traffic, beta)."
- **Our assessment**: Only the Complexity router is documented with a concrete config example. Semantic routing is mentioned but not configurable from this source. Adaptive routing is labeled beta, meaning its production readiness is unclear. The guide should treat this as a three-option taxonomy with only one documented path currently.

### Claim 8: The five cost-cutting features compose orthogonally — budget fallbacks, prompt caching, Headroom compression, MCP tool search, and auto routing can be enabled together on the same proxy without client-side changes, and each targets a different cost dimension
- **Evidence**: The "Stacking the levers" section explicitly describes how the five features compose and why they are dimensionally independent.
- **Confidence**: emerging (vendor claim; no independent validation of the composition claim)
- **Quote**: "The five features compose. Budget-based fallbacks bound the total spend regardless of what else you do. Prompt cache checkpoints and Headroom compression each shave a different slice of the request payload before it hits the model. MCP tool search cuts the tool schema overhead at the front of every turn. Auto routing sends every request to the smallest model that can handle it. Turn them on together and the same Claude Code workload runs on a fraction of the input tokens it did before, without touching a single developer machine."
- **Our assessment**: This is the key architectural takeaway — the five levers are not mutually exclusive alternatives; they target different cost dimensions (spend cap, token cost per input, payload size, schema overhead, model selection) and can be composed additively. The claim of "no client-side changes" is consistent across all five levers. We rate this emerging rather than settled because the article provides no benchmarks or production case studies demonstrating the combined effect.

### Claim 9: Headroom compression (claimed 60-95% reduction on compressible portion) and prompt caching target different payload slices and are complementary — "Prompt cache trims the static prefix; Headroom trims the dynamic middle"
- **Evidence**: The article distinguishes the two mechanisms and shows a guardrail config for Headroom as a `pre_call` sidecar. Reported savings are stated as "60-95% on the compressible portion of Claude Code traffic."
- **Confidence**: anecdotal (the compression savings are vendor-marketed with no independent benchmarks; the architecture distinction is settled)
- **Quote**: "Prompt cache trims the static prefix; Headroom trims the dynamic middle."
- **Our assessment**: The architectural distinction — static prefix (caching) vs. dynamic middle (compression) — is a useful framing for understanding when each mechanism applies. The savings range (60-95%) is unsupported vendor marketing per `blog-litellm-headroom-integration.md` Claim 4's analysis. The complementary nature of the two mechanisms is the key insight: they are not competing approaches but address different segments of the input payload.

### Claim 10: Enabling the five levers requires no changes to developer machines or workflows — the platform admin configures the proxy, and developers only need ANTHROPIC_BASE_URL set
- **Evidence**: The article opens by stating this premise and closes by repeating that the features work "without touching a single developer machine."
- **Confidence**: settled (consistent across all five levers' documented configuration)
- **Quote**: (from article summary) "if Claude Code already points at a LiteLLM proxy via ANTHROPIC_BASE_URL, there are five levers the platform admin can pull to bring that cost down"
- **Our assessment**: This is a consistent architectural claim across all five features — none require client-side code changes, proxy configuration changes, or developer opt-in. The admin controls all levers through virtual key configuration, config.yaml, and environment variables. This admin-to-developer separation of concerns is the same pattern documented in `blog-litellm-headroom-integration.md` Claim 7 for the Headroom guardrail, now generalized to a five-lever cost-optimization playbook.

## Concrete Artifacts

### Budget windows with stacked durations (curl, verbatim from article)

```bash
curl 'http://0.0.0.0:4000/key/generate' \
  --header 'Authorization: Bearer <your-master-key>' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "budget_limits": [
      {"budget_duration": "24h", "max_budget": 10},
      {"budget_duration": "30d", "max_budget": 100}
    ]
  }'
```

Source: https://docs.litellm.ai/blog/save-claude-code-costs-with-litellm — "Budget windows + budget fallbacks" section.

### Budget fallback chains with per-model limits (curl, verbatim from article)

```bash
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_max_budget": {
      "claude-opus-4-8":   {"budget_limit": 20.0, "time_period": "1d"},
      "claude-sonnet-5":   {"budget_limit": 10.0, "time_period": "1d"},
      "claude-haiku-4-5":  {"budget_limit": 5.0,  "time_period": "1d"}
    },
    "budget_fallbacks": {
      "claude-opus-4-8":  ["claude-sonnet-5", "claude-haiku-4-5"],
      "claude-sonnet-5":  ["claude-haiku-4-5"]
    }
  }'
```

Source: https://docs.litellm.ai/blog/save-claude-code-costs-with-litellm — "Budget windows + budget fallbacks" section.

### Automatic prompt caching injection — per-model config (verbatim from article)

```yaml
model_list:
  - model_name: claude-sonnet-4-5
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: os.environ/ANTHROPIC_API_KEY
      cache_control_injection_points:
        - location: message
          role: system
router_settings:
  optional_pre_call_checks: ["prompt_caching"]
```

Source: https://docs.litellm.ai/blog/save-claude-code-costs-with-litellm — "Automatic Prompt Caching" section.

### Automatic prompt caching injection — global default config (verbatim from article)

```yaml
model_list:
  - model_name: claude-sonnet-4.5-20250929
    litellm_params:
      model: vertex_ai/claude-sonnet-4-5@20250929
router_settings:
  default_litellm_params:
    cache_control_injection_points:
      - location: message
        role: system
  optional_pre_call_checks: ["prompt_caching"]
```

Source: https://docs.litellm.ai/blog/save-claude-code-costs-with-litellm — "Automatic Prompt Caching" section.

### MCP Tool Search configuration (curl, verbatim from article)

```bash
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "object_permission": {
      "mcp_tool_search_enabled": true,
      "mcp_servers": ["github", "slack", "linear", "jira"]
    }
  }'
```

Source: https://docs.litellm.ai/blog/save-claude-code-costs-with-litellm — "Defer MCP tools" section.

### Complexity router tiers config (verbatim from article)

```yaml
model_list:
  # Target models
  - model_name: gpt-4o-mini
    litellm_params:
      model: gpt-4o-mini
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
  - model_name: claude-sonnet
    litellm_params:
      model: claude-sonnet-4-20250514
  - model_name: o1-preview
    litellm_params:
      model: o1-preview
  # Complexity router
  - model_name: smart-router
    litellm_params:
      model: auto_router/complexity_router
      complexity_router_config:
        tiers:
          SIMPLE: gpt-4o-mini
          MEDIUM: gpt-4o
          COMPLEX: claude-sonnet
          REASONING: o1-preview
      complexity_router_default_model: gpt-4o
```

Source: https://docs.litellm.ai/blog/save-claude-code-costs-with-litellm — "Auto routing" section.

## Cross-References

- **Corroborates**:
  - `blog-litellm-headroom-integration.md` — The Headroom compression lever (lever 3 in this post's 5-lever framework) is fully documented in the existing note. The current source's description of Headroom as a `pre_call` guardrail (Config 3 in Concrete Artifacts) and the cache-vs-compression distinction ("Prompt cache trims the static prefix; Headroom trims the dynamic middle," Claim 9 here) corroborate that note's Claims 1 (sidecar architecture) and 5 (retrieve_headroom tool), while the savings claim (60-95%) is identically unsupported, matching the existing note's Claim 4 evaluation. This source contributes no new Headroom-specific claims beyond the composition framing.
  - `blog-litellm-redis-circuit-breaker.md` **Claim 1** — Establishes Redis as a hot-path dependency for the LiteLLM gateway's rate limiting, caching, and spend tracking. Budget windows and budget fallbacks (Claims 1-2 here) operate through the same Redis-backed spend tracking infrastructure. Not a direct corroboration of the same claim, but the operational context (Redis in the hot path) is shared infrastructure.

- **Extends**:
  - `blog-litellm-headroom-integration.md` — Extends the Headroom coverage (lever 3 in this post) from an isolated integration pattern into a multi-lever cost-optimization playbook. The existing note covers Headroom's architecture, configuration, and failure reports in depth (9 claims). This source places it alongside budget controls, prompt caching, MCP tool search, and auto routing as one of five composable levers that "each shave a different slice of the request payload" (Claim 8). The Smith should use both notes together: the existing note for operational depth on Headroom, this note for the composition framework.
  - `blog-litellm-redis-circuit-breaker.md` — That note's budget windows (implicit in the spend-tracking infrastructure, Claim 1) are extended here to budget fallback chains with per-model limits (Claim 2) — a spend-governance pattern absent from the circuit-breaker source. The circuit-breaker note covers resilience under Redis degradation; this note covers spend control at the proxy level. Together they bracket LiteLLM's budget infrastructure: capacity protection and cost governance.

- **Novel** (new to the corpus):
  - **MCP Tool Search** — `mcp_tool_search_enabled` replacing the full MCP tool catalog with two virtual search/call tools (`mcp_tool_search`, `mcp_tool_call`). Including: token-overlap ranking with no embedding dependency (Claim 5), access-surface preservation (search returns only permitted tools), and the curl configuration pattern. No existing note covers any form of MCP tool schema-collapse pattern for token-cost reduction.
  - **Budget fallback chains** — `model_max_budget` per model + `budget_fallbacks` chains for silent rerouting to cheaper models when budgets exhaust (Claim 2). First corpus coverage of proxy-level budget cascading for Claude Code. The stacked budget windows pattern (Claim 1) with `budget_limits` combining multiple durations (24h + 30d) is also novel.
  - **Auto routing by complexity** — The `complexity_router` with four classification tiers (SIMPLE → MEDIUM → COMPLEX → REASONING) mapped to specific models (Claim 6). Also the three-flavor taxonomy (Semantic, Complexity, Adaptive) as a routing design space (Claim 7). First corpus coverage of request-routing by complexity at the proxy level.
  - **Automatic prompt caching injection** — `cache_control_injection_points` with `optional_pre_call_checks: ["prompt_caching"]` (Claim 3). While prompt caching is discussed in multiple corpus notes (Anthropic API patterns, model feature support), no existing note covers the *proxy-side automatic injection* of cache_control markers. The per-model vs. global config duality is also new.
  - **The "stacking the levers" composition insight** — The claim (Claim 8) that five distinct cost-optimization dimensions (spend caps, token price, payload compression, schema overhead, model selection) compose orthogonally on a single proxy without client-side changes. This architectural framing — that cost optimization is a multi-dimensional, composable concern rather than a single lever — is new to the corpus.

- **Contradicts**: None identified. All claims extend or corroborate existing source notes; no claim opposes an existing position. The Headroom savings claim (60-95%, Claim 9) matches the identical vendor-marketed claim in `blog-litellm-headroom-integration.md` Claim 4 (rated anecdotal there), so there is no contradiction between the two sources. No contradiction issue filed.

## Guide Impact

- **Chapter 05 (LLM Ops — Cost Optimization)**: Add a new **multi-lever cost-optimization framework** section covering the five composable proxy-level levers documented in this source. Specific additions:
  - **Budget windows + budget fallback chains** (Claims 1-2): Add budget windows with stacked durations as a spend-control pattern. Add budget fallback chains as a novel spend-governance pattern — per-model daily limits with automatic silent rerouting to cheaper models when budgets exhaust. The Opus → Sonnet → Haiku fallback chain (see Concrete Artifacts) is an immediately reproducible pattern for any gateway operator.
  - **Automatic prompt caching injection** (Claim 3): Add proxy-side cache_control injection as an alternative to client-side cache marker placement. Document the two config modes (per-model `litellm_params` vs. global `default_litellm_params`). Include the `optional_pre_call_checks: ["prompt_caching"]` routing hint for multi-deployment setups.
  - **MCP Tool Search** (Claims 4-5): Add the tool-schema-collapse pattern as a token-cost reduction technique for tool-heavy Claude Code sessions. Document the token-overlap ranking design (no embedding dependency, no vector DB required) and the access-preservation property.
  - **Auto routing by complexity** (Claims 6-7): Add the four-tier complexity router as a concrete routing pattern. Document the three-flavor taxonomy (Semantic/Complexity/Adaptive) as a routing design space, with Complexity as the recommended starting point due to zero external API calls.
  - **The composition insight** (Claim 8): Add the framing that these five levers target different cost dimensions and compose additively. This is the most actionable architectural takeaway: teams should implement all levers that apply to their deployment rather than picking one.

- **Chapter 02 (Architecture — Proxy Patterns)**: Add auto routing as a proxy-level routing pattern for Claude Code, using the Complexity Router tiers (SIMPLE→MEDIUM→COMPLEX→REASONING) as a reference classification. Add MCP Tool Search as a proxy-level optimization for MCP-heavy deployments where tool schema overhead dominates input token consumption.

- **Chapter 06 (MCP / Tools — Tool Optimization)**: Add the MCP Tool Search pattern as a dedicated subsection. The token-overlap ranking (no embedding dependency), the two-virtual-tool interface (`mcp_tool_search`/`mcp_tool_call`), and the access-preservation guarantee are specific design decisions the guide should document for teams operating MCP at scale through a gateway.

- **Chapter 04 (Guardrails — Prompt Compression)**: The Headroom compression section is already covered by `blog-litellm-headroom-integration.md`'s Guide Impact. This note adds the complementary relationship between compression and caching (Claim 9) — the Smith should update the Headroom subsection to note that compression (dynamic payload) and caching (static prefix) target different payload segments and should both be enabled.

## Extraction Notes

- Source fetched and read in full via HTTP. The article is a Docusaurus blog post (~2,000 words of article content with 4 curl examples and 3 config.yaml blocks, plus sidebar and navigation).
- The article is authored by Krrish Dholakia (CEO, LiteLLM), published July 4, 2026. All quoted passages in this note were extracted from the rendered HTML via direct HTTP fetch and HTML-to-text extraction. The WebFetch tool's 125-character single-quote limit prevented verbatim extraction through that channel; direct curl was used instead. Quotes were copied character-for-character from the extracted text.
- `confidence_overall` is `emerging`: the config examples and feature descriptions (Claims 1-6) are settled LiteLLM product behavior and could be verified against the open-source codebase. The composition insight (Claim 8) is a vendor-marketed claim without independent validation. The auto-routing taxonomy (Claim 7) includes a beta feature (Adaptive). The Headroom savings claim (Claim 9) is anecdotal vendor marketing, consistent with the identical claim in `blog-litellm-headroom-integration.md`.
- The source is specifically about Claude Code cost optimization — unlike more general LiteLLM blog posts, every section addresses how the feature applies to Claude Code workloads, making it uniquely valuable for the Guide's Claude Code-focused chapters.
- **Candidate dismissal** (from `miner-related-notes.md`): All 10 candidate source notes were reviewed and dismissed as not directly relevant to LiteLLM proxy cost-optimization levers for Claude Code: `docs-langfuse-mcp-server.md` (Langfuse MCP documentation server — unrelated to proxy cost levers), `docs-google-sre-reliable-product-launches.md` (launch coordination — unrelated), `docs-google-sre-prodcast-04-05-furino-slos.md` (SLOs — unrelated), `blog-incidentio-ai-sre-incident-run.md` (incident response AI agent — unrelated), `docs-langfuse-security-and-guardrails.md` (guardrail libraries — unrelated), `blog-anthropic-building-effective-agents.md` (agent design patterns — unrelated to proxy cost levers), `docs-google-sre-prodcast-03-07-retail-gaming.md` (retail/gaming SRE — unrelated), `docs-google-sre-prodcast-04-09-ai-agents.md` (AI agent architecture — unrelated), `docs-google-sre-prodcast-03-09-profiling-data.md` (profiling data — unrelated), `blog-litellm-april-townhall-updates.md` (LiteLLM CI/CD and release process — different topic from cost-optimization levers). Relevant cross-references were identified via search of `source-notes/` for LiteLLM notes with overlapping topics and are cited above.
- No contradiction issue filed: verified against all existing source notes and open contradiction-labeled issues. The only overlapping claims (Headroom savings range in `blog-litellm-headroom-integration.md` Claims 4, this note's Claim 9) are identical vendor-marketed figures with the same confidence rating (anecdotal), not contradictions.
