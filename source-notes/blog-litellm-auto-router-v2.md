---
source_url: https://docs.litellm.ai/blog/autorouter-v2
source_type: blog-post
title: "Auto Router v2: one router for complexity, semantic, and adaptive routing"
author: "Krrish Dholakia (CEO, LiteLLM)"
date_published: 2026-07-13
date_extracted: 2026-08-30
last_checked: 2026-08-30
status: current
confidence_overall: emerging
issue: "#1143"
---

# Auto Router v2: one router for complexity, semantic, and adaptive routing

> LiteLLM's Auto Router v2 (shipping v1.94.x, dev cut 2026-07-14) collapses the three prior routing flavors — complexity, semantic, and adaptive — into a single `auto_router/complexity_router` config, adding LLM classification, keyword escalation, Thompson-sampled tier pools, session affinity for prompt-cache preservation, a greppable per-request decision log, and a roadmap of cost-cascade guards and attributable decisions.

## Source Context

- **Type**: blog-post (vendor engineering post on docs.litellm.ai, tagged `routing`, `complexity-router`, `semantic-router`, `adaptive`, `product`), published July 13, 2026.
- **Author credibility**: Krrish Dholakia is CEO and a founding engineer of LiteLLM/BerriAI. Claims about LiteLLM product behavior (config schema, decision-log format, PR-merged fixes) are authoritative for the product and verifiable against the open-source codebase and the referenced PRs/discussions. No independent benchmarks or third-party validation are offered; the "What's next" roadmap items are forward-looking and not shipped as of this post.
- **Scope**: Covers (1) the unified `complexity_router_config` schema that replaces the pre-v2 routing taxonomy, (2) the per-modal classification additions (LLM classifier with heuristic fallback, keyword rules with tier escalation, semantic keyword matching with MAX aggregation), (3) adaptive Thompson-sampled tier pools, (4) opt-in session affinity, (5) the greppable decision log format, (6) two gateway-behavior bug fixes (`litellm_params` merge, Anthropic Responses API `tool_choice`), and (7) a roadmap (router plugins, escalation ceilings on fallback chains, attributable decisions). Does NOT cover: the semantic auto router's details, UI operations beyond Test Connection/validation, or benchmarks of routing quality/cost savings.

## Extracted Claims

### Claim 1: Auto Router v2 collapses complexity, semantic, and adaptive routing into a single `auto_router/complexity_router` config, shipping in v1.94.x
- **Evidence**: Opening paragraph plus the "Availability" line naming the exact version and first dev-release date; the "One config, all the knobs" section then shows one YAML block carrying every handle (tiers, LLM classifier, keyword rules, semantic matching, adaptive, session affinity).
- **Confidence**: settled (concrete shipped-feature claim, verifiable against the config schema and release)
- **Quote**: "Auto Router v2 collapses complexity, semantic, and adaptive routing into a single `auto_router/complexity_router`. One config now covers heuristic scoring, LLM classification, lexical or semantic keyword rules, and Thompson-sampled tier pools."
- **Our assessment**: This is the direct supersession of the "three-flavor taxonomy with one documented path" takeaway in `blog-litellm-save-claude-code-costs.md` Claim 7 (see Cross-References — contradiction #1150). We buy the collapse claim: the config in the source is concrete, backward-compatible ("Existing complexity router configs keep working," Claim 12), and internally consistent with the table of what v2 adds.

### Claim 2: The collapse into one router was community-pushed — discussion #32168 argued the three routing strategies should converge so users are not forced to pick a mode up front
- **Evidence**: Two paragraphs attribute the design path to specific GitHub discussions (#32168 for convergence, #32172 for debuggability), with a rationale statement rather than internal-product reasoning.
- **Confidence**: emerging (vendor account of community motivation, though the cited discussions are public and checkable)
- **Quote**: "The push came from the community. On discussion #32168, users pointed out that all three routing strategies should converge into a single Auto Router."
- **Our assessment**: Plausible and consistent with the general LiteLLM pattern of development driven by GitHub discussions (the source cites #32168 repeatedly). We rate emerging because the direction-of-influence claim is the vendor's framing; nothing here changes the value of the converged design itself.

### Claim 3: The operational rationale is "predictable beats clever for debuggability" — a fixed, versioned capability→model mapping is what makes "why did this response cost 4x today" answerable after the fact
- **Evidence**: Stated design principle attributed to discussion #32172.
- **Confidence**: settled (a stated design rationale; the principle is a guide-relevant SRE tenet)
- **Quote**: "predictable beats clever for debuggability. A fixed, versioned mapping from capability class to model is what makes \"why did this response cost 4x today\" answerable after the fact."
- **Our assessment**: Strong, guide-usable principle: determinism/versioning in routing decisions is an observability property. It directly supports treating the decision log (Claim 8) and roadmap "attributable decisions" (Claim 11) as first-class reliability features rather than polish. We buy it.

### Claim 4: The optional LLM classifier (`classifier_type: llm`) runs through the same `Router` instance (so credentials, budgets, and fallbacks apply) and falls back to the heuristic scorer on timeout, empty content, or schema mismatch
- **Evidence**: Prose note describing the classifier path and its failure behaviors, plus the `classifier_llm_config` keys in the config block (`model`, `timeout_ms: 2000`).
- **Confidence**: settled (documented product behavior with config)
- **Quote**: "LLM classifier goes through the same `Router` instance, so credentials, budgets, and fallbacks apply. Timeout, empty content, or schema mismatch falls back to the heuristic scorer."
- **Our assessment**: The same-`Router`-instance property is operationally important: classifier calls inherit existing governance (budgets, fallbacks) instead of being a second-class side path. The fallback-to-heuristic behavior is a sensible degradation order for a routing-critical call. We buy it; it makes the LLM classifier a low-risk addition to an existing complexity router.

### Claim 5: Keyword rules run before the scorer; multiple matches escalate to the highest matched tier (SIMPLE < MEDIUM < COMPLEX < REASONING) so rule order does not silently change behavior; semantic matching uses MAX aggregation (was MEAN)
- **Evidence**: Prose in "Notes on the new pieces" plus the `keyword_tier_rules` YAML (e.g., `["kubernetes", "k8s", "istio"] → REASONING`).
- **Confidence**: settled (documented product behavior with config)
- **Quote**: "Keyword rules run before the scorer. Multiple matches escalate to the highest tier (SIMPLE < MEDIUM < COMPLEX < REASONING), so rule order does not silently change behavior. Semantic matching uses MAX aggregation (was MEAN), so one strong keyword match is not diluted by other utterances on the tier."
- **Our assessment**: Both properties are good design-for-determinism: order-independence removes a whole class of "the config I wrote doesn't behave like I expect" bugs, and MAX (vs MEAN) aggregation prevents weak utterances on a tier from washing out a strong match. Config-reviewable and consistent with Claim 3's predictability principle.

### Claim 6: `adaptive: true` turns tier pools into Thompson-sampled learning pools — cold requests sample only inside the classified tier instead of collapsing on the cheapest model, and feedback attributes to the model that actually served the previous turn
- **Evidence**: Prose in "Notes on the new pieces" describing cold-start sampling and credit attribution, plus the `adaptive: true` flag in the config.
- **Confidence**: emerging (mechanism is documented and configurable, but its real-world cost/quality effect is unverified in this source)
- **Quote**: "Adaptive turns tier pools into learning pools. Cold requests sample only inside the classified tier instead of collapsing on the cheapest model. Feedback attributes back to the model that actually served the previous turn, even when stateless routing picks a different one this turn."
- **Our assessment**: Two details are notable for operations: cold-request sampling confined to the classified tier prevents early-traffic collapse onto the cheapest model (a naive bandit failure mode), and credit attribution follows the actually-serving model so reward feedback stays correct across routing changes. The effectiveness claims (savings, quality) are not benchmarked here, so we keep this emerging.

### Claim 7: Opt-in `session_affinity` pins the first-turn model for a session and skips reclassification on later turns, preserving provider-side prompt caches keyed to that model (TTL defaults to 3600s; `session_id` from request metadata)
- **Evidence**: Prose describing the mechanism and its motivation, linked to PR #33126, with `session_affinity_ttl_seconds: 3600` in the config.
- **Confidence**: settled (documented product behavior + PR reference)
- **Quote**: "Session affinity (opt-in) pins the first-turn model for a session and skips reclassification on later turns, so provider-side prompt caches keyed to that model do not get invalidated when a follow-up (\"thanks!\") would otherwise classify into a different tier (#33126). TTL defaults to 3600s."
- **Our assessment**: This is the highest-value operational idea in the post for gateways serving agent workloads: per-request reclassification is cache-hostile, because a cheap follow-up that classifies into a different tier forces a cache re-write on the expensive model. Pinning the session to the first-turn model converts session continuity into cache hits. We buy it, with the caveat that pinning also means the whole session inherits the first turn's tier (the source does not state this trade-off, but it is the natural consequence).

### Claim 8: The decision log emits one greppable line per request with a `cause=` marker (`complexity_scorer | literal_keyword_match | semantic_keyword_match | session_affinity_pin`), plus tier, score/signals, and routed model
- **Evidence**: The labeled "Decision log" block showing four verbatim single-line records with the four `cause=` values; the "What v2 adds" table lists the before/after (`"keyword rule fired"` → `cause=literal_keyword_match | semantic_keyword_match | complexity_scorer`).
- **Confidence**: settled (concrete output format)
- **Quote**: "Decision log emits one greppable line per request:"
- **Our assessment**: A concrete, low-friction observability pattern — routing decisions become grep-able log lines with structured cause attribution (full format in Concrete Artifacts). This is exactly the kind of "attributable decision" primitive that makes per-request routing costs explainable, and it pairs with Claim 3's debuggability rationale and chapter 02 observability work.

### Claim 9: `litellm_params` set on the auto router alias (e.g. `drop_params`, `cache_control_injection_points`) used to be silently dropped when a tier was picked; v2 merges them into the outbound request without overriding anything the caller passed explicitly
- **Evidence**: The "Fixes worth calling out" section naming the behavior change and PR #32974.
- **Confidence**: settled (documented bug fix with PR reference)
- **Quote**: "`drop_params`, `cache_control_injection_points`, and any other `litellm_params` set on the auto router alias itself used to vanish when the router picked a tier. They now merge into the outbound request, without overriding anything the caller passed explicitly (#32974)."
- **Our assessment**: This is the kind of gateway-behavior gotcha that produces "the config is ignored and nobody notices" incidents: alias-level parameters silently vanished only on routed requests, so behavior was conditional on routing state. The fix (merge, caller-precedence) is the idiomatic resolution. Operational takeaway for the guide: alias-level params on a router must be assumed to have routed-conditionally, and clean-up now restores them on v1.94.x+.

### Claim 10: The same PR (#32974) fixes an Anthropic `/v1/messages`→Responses API `tool_choice` shape bug that broke Bedrock-backed complexity routers
- **Evidence**: The "Fixes worth calling out" section explicitly ties the fix to a bug reported in discussion #32168 by @icsy7867.
- **Confidence**: settled (documented bug fix with PR and reporter reference)
- **Quote**: "Same PR fixes an Anthropic `/v1/messages` to Responses API `tool_choice` shape bug that broke Bedrock-backed complexity routers (reported in discussion #32168 by @icsy7867)."
- **Our assessment**: A second gateway-translation gotcha: request-shape translation between API surfaces (Anthropic → Responses) broke a router family on a specific backend. Both this and Claim 9 come from the same PR, indicating the fixes clustered around correctly passing routing-time configuration and tool-shape through the outbound path. Valuable as a provider-shape-translation failure pattern for the guide's gateway gotchas.

### Claim 11: Roadmap: escalation ceilings with cooldown on fallback chains ("a bad upstream cannot cascade into a bill"), and attributable decisions (stamp routed model + routing-table version on every response; export structured decision traces via logging integrations)
- **Evidence**: The "What's next" section listing both items as "Also on the list," with the concrete mechanism for each.
- **Confidence**: emerging (roadmap items, not shipped as of this post)
- **Quote**: "Escalation ceilings on fallback chains. Per-request cap on escalations plus a cooldown once a key walks the chain N times, so a bad upstream cannot cascade into a bill."
- **Quote**: "Attributable decisions. Stamp the routed model and routing-table version on every response, and export structured decision traces (candidates, scores, fallbacks, latency) through the standard logging integrations."
- **Our assessment**: Both are cost-control/observability primitives the guide should track. The escalation-ceiling/cooldown design directly addresses a failure the corpus has flagged elsewhere (see `failure-litellm-model-cost-map-silent-fallback.md`, where cost-influencing routing raises incident stakes): a misbehaving upstream currently escalates spend with no cap. The decision-traces item extends the per-request decision log (Claim 8) into a full trace. Emerging because neither is merged at publication.

### Claim 12: v2 is backward compatible and additive — existing complexity router configs keep working; v2 features are new keys (`keyword_tier_rules`, `classifier_type: llm`, `adaptive: true`, `session_affinity: true`, or a list value on a tier)
- **Evidence**: The "Try it" section explicitly listing the opt-in additions to an existing config.
- **Confidence**: settled (stated product behavior)
- **Quote**: "Existing complexity router configs keep working. To try v2, add `keyword_tier_rules`, `classifier_type: llm`, `adaptive: true`, `session_affinity: true`, or a list value on a tier to your existing `complexity_router_config`."
- **Our assessment**: The additive, backward-compatible upgrade path is a strong deployment property — operators can adopt the v2 surface incrementally (e.g., start with keyword rules, then a class-tier list, then session affinity) without a config rewrite. This materially lowers migration risk for existing v1 complexity routers documented in `blog-litellm-save-claude-code-costs.md`.

## Concrete Artifacts

All artifacts below are verbatim from https://docs.litellm.ai/blog/autorouter-v2 (verified against rendered HTML).

### The unified v2 config ("One config, all the knobs" section, verbatim)

```yaml
model_list:
  - model_name: smart-router
    litellm_params:
      model: auto_router/complexity_router
      drop_params: true
      complexity_router_config:
        tiers:
          SIMPLE:    ["gpt-4o-mini", "claude-haiku-4-5"]   # random-pick pool
          MEDIUM:    gpt-4o                                 # single pin
          COMPLEX:   claude-sonnet-5
          REASONING: gpt-5.5

        # optional: LLM classifier instead of heuristic scorer
        classifier_type: llm
        classifier_llm_config:
          model: claude-haiku-4-5-20251001
          timeout_ms: 2000

        # optional: keyword rules, escalate to highest matched tier
        keyword_tier_rules:
          - keywords: ["hi", "hello", "thanks"]
            tier: SIMPLE
          - keywords: ["kubernetes", "k8s", "istio"]
            tier: REASONING
        semantic_keyword_matching: true
        embedding_model: voyage-3-5
        match_threshold: 0.5

        # optional: append to the built-in technical keyword list
        custom_technical_keywords: [kafka, redis, postgresql, udp, dns]

        # optional: Thompson-sample within the tier's pool
        adaptive: true

        # optional: pin a session to its first-turn model (preserves prompt cache)
        session_affinity: true
        session_affinity_ttl_seconds: 3600

      complexity_router_default_model: claude-sonnet-5
```

### Decision log line format ("Notes on the new pieces — Decision log" section, verbatim)

```
ComplexityRouter: routing decision cause=complexity_scorer,      tier=SIMPLE,     score=-0.150, signals=['short (7 tokens)', 'simple (what is)'], routed_model=gpt-4o-mini
ComplexityRouter: routing decision cause=literal_keyword_match,  tier=REASONING,                                                                    routed_model=gpt-5.5
ComplexityRouter: routing decision cause=semantic_keyword_match, tier=REASONING,                                                                    routed_model=gpt-5.5
ComplexityRouter: routing decision cause=session_affinity_pin,                                                                                      routed_model=gpt-5.5
```

### "What v2 adds" before/after table ("What v2 adds" section, verbatim rows)

| Capability | Before | After |
|---|---|---|
| Classification | Heuristic scorer only | Heuristic, LLM classifier, lexical or semantic keyword rules (#32169, #32859) |
| Tier value | One model per tier | One model, random-pick pool, or Thompson-sampled pool (#32967, #32947) |
| Technical keywords | Fixed built-in list | `custom_technical_keywords` appends without replacing (#32262) |
| Decision log | "keyword rule fired" | `cause=literal_keyword_match | semantic_keyword_match | complexity_scorer` (#32943) |
| Alias `litellm_params` | Silently dropped | Merged into outbound request (#32974) |
| Session affinity | Reclassified every turn | Opt-in `session_affinity`: pin the first-turn model for the session, skip reclassification (#33126) |

### Router plugins — end-to-end pipeline sketch ("What's next — Router plugins" section, verbatim)

1. User sends a request.
2. Language plugin detects `en`.
3. Domain classifier labels it `coding` with 0.93 confidence.
4. Tenant policy limits allowed providers to OpenAI and Anthropic.
5. Budget plugin removes models exceeding the tenant's cost cap.
6. Auto Router picks the best remaining model from the enriched context.

Config sketch (verbatim):

```yaml
router_settings:
  plugins:
    - name: language-detector
    - name: domain-classifier
      params:
        provider: openai/gpt-5-mini
    - name: budget-policy
      params:
        daily_limit: 100
    - name: tenant-policy
    - name: custom-python
      path: ./plugins/my_router.py
```

## Cross-References

- **Corroborates**:
  - `blog-litellm-save-claude-code-costs.md` **Claim 6** (four-tier complexity router, SIMPLE→MEDIUM→COMPLEX→REASONING on `auto_router/complexity_router` behind a `smart-router` alias) — v2 retains that exact tier ladder, alias, and `complexity_router_default_model` (Claim 1/12 here, Concrete Artifacts config). The four-tier model and the alias convention are directly carried over, confirming the v1 complexity router was the seed of the unified v2 config.
  - `blog-litellm-may-townhall-updates.md` **Claim 9** (Adaptive Routing launched among a product batch) — v2 confirms Adaptive continues to exist and makes it a concrete, documented config knob (`adaptive: true`, Thompson-sampled pools, Claim 6 here), rather than the launch-only mention that note recorded.

- **Contradicts**:
  - **`blog-litellm-save-claude-code-costs.md` Claim 7** — that note concluded "LiteLLM ships three auto-routing flavors — Semantic (embedding match), Complexity (rule-based, zero external call), and Adaptive (learns from live traffic, beta)" with the assessment that "Only the Complexity router is documented with a concrete config example. Semantic routing is mentioned but not configurable from this source. Adaptive routing is labeled beta... The guide should treat this as a three-option taxonomy with only one documented path currently." Auto Router v2 directly contradicts the "single documented path / Semantic not configurable / Adaptive production-readiness unclear" takeaway: v2 ships one documented `complexity_router_config` covering heuristic scoring, LLM classification, `semantic_keyword_matching` (with embedding model + threshold), keyword rules, and `adaptive: true` pool sampling (Claims 1, 5, 6 here, Concrete Artifacts config), in v1.94.x. **Contradiction issue [#1150](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1150) filed (advisory verdict: superseded — the unified feature is still labeled beta, but configurability/documentation has changed).** No verdict assigned here per MINER.md §4a.

- **Extends**:
  - `blog-litellm-save-claude-code-costs.md` **Claim 6** — the v1 complexity-router coverage (four tiers, zero external calls, "fastest to set up") is extended by v2 into the full unified config: tier values now also accept random-pick lists and Thompson-sampled pools (Claim 1), and the optional LLM classifier (Claim 4), keyword escalation (Claim 5), adaptive pools (Claim 6), session affinity (Claim 7), and decision log (Claim 8) are all new opt-in dimensions on the same router. Operators who adopted the v1 config from that note can adopt v2 additively (Claim 12).
  - `blog-litellm-may-townhall-updates.md` **Claim 9** — extends the Adaptive Routing launch mention (no config in that source) into a fully documented configuration surface for adaptive, semantic, and complexity signals under one router.
  - `failure-litellm-model-cost-map-silent-fallback.md` — that note flagged (Root Cause assessment) that the silent cost-map fallback "could have been much worse" "in a system where cost influenced routing or quota enforcement." The v2 roadmap's escalation ceilings + cooldown on fallback chains ("a bad upstream cannot cascade into a bill," Claim 11) is a concrete mechanism in that direction: bounding cost escalation from a bad upstream before it becomes an incident. Extends the corpus's LiteLLM gateway cost-control thread from detection to prevention.

- **Novel**: First corpus coverage of:
  - **The unified `auto_router/complexity_router` config** collapsing complexity/semantic/adaptive signals into one schema (Claim 1, Concrete Artifacts config) — replaces the prior corpus's three-flavor taxonomy.
  - **The per-request decision log** with `cause=complexity_scorer | literal_keyword_match | semantic_keyword_match | session_affinity_pin` one-line records (Claim 8) — a concrete, greppable attribution pattern, the first in the corpus for gateway routing decisions.
  - **Session affinity to preserve provider-side prompt caches** (Claim 7) — first corpus coverage of routing-level cache preservation (pin first-turn model, TTL 3600s).
  - **Keyword-rule tier escalation** (order-independent, escalate-to-highest) and **MAX aggregation** for semantic matching (Claim 5).
  - **LLM classifier with heuristic fallback** on timeout/empty/schema-mismatch, running on the same `Router` instance (Claim 4).
  - **Adaptive Thompson-sampled tier pools** with cold-start sampling confined to the classified tier and served-model credit attribution (Claim 6).
  - **The alias-`litellm_params` silent-drop gotcha and its merge fix** (#32974), plus the Anthropic `/v1/messages`→Responses API `tool_choice` bug (Claims 9, 10) — gateway behavior gotchas not documented elsewhere in the corpus.
  - **Roadmap primitives**: escalation ceilings + cooldown on fallback chains and response-stamped attributable decisions (Claim 11).

## Guide Impact

- **Chapter 05 (LLM Ops — Reliability / Routing)**: Overhaul the auto-routing guidance. Replace the "three flavors, only Complexity documented, Adaptive beta" framing (from `blog-litellm-save-claude-code-costs.md`, see contradiction #1150) with the unified v1.94.x `auto_router/complexity_router` config (Claims 1, 12; Concrete Artifacts). Specific additions:
  - **Tier-value forms**: single pin vs random-pick pool vs Thompson-sampled pool (Claims 1, 6) — recommend starting with pinned/list tiers and adding `adaptive: true` only when pool behavior is understood (cold-start sampling + served-model attribution).
  - **Keyword escalation** (Claim 5): order-independent "escalate to highest matched tier" rules as a deterministic, low-overhead routing layer; note MAX aggregation for semantic matching.
  - **LLM classifier with fallback** (Claim 4): heuristic fallback on timeout/empty/schema-mismatch and shared governance via the same `Router` instance — keeps the classifier a low-risk addition.
  - **Cost-cascade guard** (Claim 11): once shipped, recommend escalation ceilings + cooldown on fallback chains ("a bad upstream cannot cascade into a bill") — connecting to the corpus's gateway cost-control thread (`failure-litellm-model-cost-map-silent-fallback.md`).
  - **Gateway gotchas** (Claims 9, 10): alias-level `litellm_params` are no longer silently dropped on routed requests as of v1.94.x, and the Anthropic→Responses `tool_choice` translation bug on Bedrock-backed routers was fixed — worth a "route-aware config gotchas" note for operators of pre-v1.94 gateways.

- **Chapter 02 (Observability)**: Add the **per-request routing decision log** (Claim 8) as a concrete attribution pattern — one greppable line per decision with `cause=`, `tier=`/`score=`/`signals=` and `routed_model=` — plus the roadmap's attributable-decisions design (stamp routed model + routing-table version, structured decision traces via logging integrations, Claim 11). Pair with the "predictable beats clever" principle (Claim 3): versioned, deterministic routing is what makes per-request cost questions answerable post-hoc.

- **Chapter 04 (Oncall & Toil)**: Add the debuggability rationale (Claim 3) — "why did this response cost 4x today" — as the on-call framing for routing-attribution: fixed capability→model maps keep cost surprises attributable. Optionally tie to the session-affinity/cache interplay (Claim 7) when diagnosing "why did a session suddenly cost more" (cache invalidation from reclassification).

## Extraction Notes

- Source read in full via WebFetch and verified against raw HTML fetched directly (curl) — the code blocks and quoted passages were copied character-for-character from the rendered HTML (the page tokenizes code lines with `<br>` separators; newlines were reconstructed from those markers). No paywall or truncation.
- The blog post links to the full reference on the [Auto Routing docs page](/docs/proxy/auto_routing); I followed that linked page to confirm the current reference surface. That page adds material beyond the blog post (classifier context window, effort ladders, deployment-affinity pre-call checks, reported-savings methodology, the `[Beta] Auto Routing` label, a "Changed default" note that `session_affinity` at one point defaulted to `true` then `false`) — those are NOT extracted here because they post-date/override the blog post's claims; the Assayer should treat this note as scoped to the blog post URL. Only the blog post's own statements are quoted.
- **Contradiction issue [#1150](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1150) filed** per MINER.md §4a: `blog-litellm-save-claude-code-costs.md` Claim 7 ("three flavors, one documented path; Semantic not configurable; Adaptive beta/unclear") vs this source's unified v2 config. Filer's advisory verdict: `superseded`. The verdict is deliberately NOT picked in this note.
- `confidence_overall` is `emerging`: config schema, decision-log format, and bug-fix claims (Claims 1, 4-10, 12) describe shipped/documented v1.94.x behavior and are individually `settled`, but the feature overall remains beta-labeled, the adaptive/semantic effectiveness evidence is absent, and the roadmap claims (Claim 11, router plugins) are forward-looking.
- **Candidate dismissal** (from `miner-related-notes.md`, all read before writing Cross-References):
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent spectrum / guardrail taxonomy, unrelated to LLM gateway routing config. Dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server, unrelated. Dismissed.
  - `docs-google-sre-eliminating-toil.md` — toil reduction, unrelated. Dismissed.
  - `docs-langfuse-security-and-guardrails.md` — guardrail/security libraries, unrelated to routing. Dismissed.
  - `blog-litellm-save-claude-code-costs.md` — cited (Corroborates Claim 6; Extends Claim 6; Contradicts Claim 7, filed as #1150).
  - `docs-google-sre-data-processing-pipelines.md` — pipeline SLOs, unrelated. Dismissed.
  - `docs-google-sre-reliable-product-launches.md` — launch coordination, unrelated. Dismissed.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO fundamentals, unrelated. Dismissed.
  - `docs-datadog-llm-observability.md` — trace/span observability model for LLM apps; the decision log here is a router-cause attribution signal, a different (pre-trace) layer. Dismissed as not overlapping.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative vs declarative change workflows, unrelated. Dismissed.
  Cross-references beyond the candidate list were verified directly against the cited notes (`blog-litellm-save-claude-code-costs.md` Claims 6-7, `blog-litellm-may-townhall-updates.md` Claim 9, `failure-litellm-model-cost-map-silent-fallback.md` Root Cause assessment) per MINER.md §4b.
- This source was extracted under live trial #571 (zen-free OpenCode runner, model `opencode/big-pickle`).