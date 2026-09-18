---
source_url: https://docs.litellm.ai/docs/adding_provider/generic_prompt_management_api
source_type: docs
title: "[BETA] Generic Prompt Management API — Integrate Without a PR (LiteLLM Docs)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; BETA as of 2026-09-17)
date_extracted: 2026-09-17
last_checked: 2026-09-17
status: current
confidence_overall: emerging
issue: "#1360"
---

# [BETA] Generic Prompt Management API (LiteLLM Docs)

> LiteLLM's PR-less prompt-management integration contract — a prompt store
> implements `GET /beta/litellm_prompt_management` and is fetched by the
> gateway on the request path — whose operationally load-bearing part is the
> **default-on override precedence**: a prompt-store response carries
> `prompt_template_model` and `prompt_template_optional_params` that by
> default replace the model and sampling parameters the caller asked for,
> with a hard in-request-path dependency on every cache miss and **no
> documented failure behavior** (no fallback, stale-serve, or timeout
> semantics) for a prompt-fetch error.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, BETA
  page under "\[Beta\] Prompt Management > Contributing to Prompt Management"
  in the docs nav).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented surface* — config keys, endpoint,
  request/response schema, default values, and the explicit override
  semantics. The page is `[BETA]` ("This is a **beta API**. We're actively
  improving it based on feedback."), carries zero measured data (no latency,
  no success/failure statistics, no production case), and the "Security
  Considerations" and "Troubleshooting" sections are generic advice. Everything
  here reads as "the gateway documents this contract," not "this has survived
  production."
- **Scope**: A single self-contained integration page: the PR-less `prompts:`
  config surface (`prompt_integration`, `provider_specific_query_params`,
  `api_base`, `api_key`, `ignore_prompt_manager_model`,
  `ignore_prompt_manager_optional_params`), the `GET /beta/litellm_prompt_management`
  request/response contract (`prompt_id`, `prompt_template`,
  `prompt_template_model`, `prompt_template_optional_params`), variable
  substitution (`{variable}` / `{{variable}}`), in-memory caching keyed on
  prompt_id/label/version, model-override and parameter-merging precedence,
  a reference FastAPI implementation (linked to `mock_prompt_management_server.py`
  in the LiteLLM cookbook), and generic security/troubleshooting advice. Does
  NOT cover: the product-side prompt-management features (covered by
  `docs/proxy/prompt_management` and sibling pages), operational
  observability of the override, or any failure/timeout/retry semantics. No
  sub-pages were needed — the page is self-contained (the sibling pages
  `docs/proxy/litellm_prompt_management`, `docs/proxy/custom_prompt_management`,
  `docs/proxy/native_litellm_prompt`, and `docs/proxy/arize_phoenix_prompts`
  are listed in Related Documentation but are separate integration surfaces).

## Extracted Claims

### Claim 1: LiteLLM offers a PR-less prompt-management integration contract — a provider implements a single `GET /beta/litellm_prompt_management` endpoint and attaches it under a `prompts:` block in `config.yaml` with `prompt_integration: "generic_prompt_management"`, avoiding PR review/merge and provider-specific code in LiteLLM's codebase
- **Evidence**: The "The Problem"/"The Solution" framing and the "Get Started
  in 3 Steps" walkthrough, with the config block under "Step 1: Configure
  LiteLLM" and the endpoint contract under "API Contract".
- **Confidence**: settled (documented contract mechanics)
- **Quote**: "The **Generic Prompt Management API** lets you integrate with LiteLLM **instantly** by implementing a simple API endpoint. No PR required."
- **Our assessment**: The architectural fact that matters for the guide is the
  same one the sibling Generic Guardrail API raises (`docs-litellm-generic-guardrail-api.md`):
  the prompt store is not code inside the gateway — it is a separate network
  service the gateway calls at request time. The "No PR Needed - Deploy and
  integrate immediately" framing is the vendor's pitch; the SRE-relevant
  corollary is that a third-party service has been handed control of what gets
  sent to the model (Claims 3-4) without a deploy of the calling service.

### Claim 2: The gateway fetches the prompt from the external store on the request path — the endpoint receives a GET with `prompt_id` plus any `provider_specific_query_params` at request time — and the page documents *no* failure behavior (no timeout, retry, stale-serve, or fallback) for a prompt-fetch error; the page's in-memory caching means the external service is a hard dependency only on a cache miss
- **Evidence**: The "API Contract" request format definitions ("Your endpoint
  will receive a GET request with query parameters"), the caching section
  ("LiteLLM automatically caches fetched prompts in memory"), and the absence
  of any timeout/error/retry semantics anywhere on the page — the closest the
  page comes to failure guidance is the Troubleshooting items for setup errors
  ("Check that your API endpoint is accessible from LiteLLM"), none of which
  address runtime fetch failure.
- **Confidence**: emerging (the dependency-in-path framing is our synthesis;
  the documented surface itself is settled)
- **Quote**: "GET /beta/litellm_prompt_management?prompt_id={prompt_id}&{custom_params}"
- **Quote**: "This means your API endpoint is only called once per unique prompt configuration."
- **Our assessment**: On a cache miss — first call with a prompt_id, a new
  prompt version/label, or a gateway restart — the request path now spans a
  third-party HTTP service, and the docs specify nothing about what happens if
  that call times out, hangs, or errors. Against the corpus's own reference
  point (`docs-langfuse-prompt-management.md` Claim 2), this is the documented
  absence of a guarantee: Langfuse's page claims no added latency because the
  SDK caches client-side with a fallback chain; this page documents no
  fallback at all. We flag the silence as the finding rather than asserting
  what LiteLLM does at runtime.

### Claim 3: The default model-override contract is on — `prompt_template_model` in the prompt-store response overrides the client's requested model unless `ignore_prompt_manager_model: true` is set (default `false`); a remote prompt store can therefore silently redirect traffic to a different (potentially more expensive) model with no code change in the caller
- **Evidence**: The "Response Format" field contract ("Model to use for this
  prompt (overrides client model unless `ignore_prompt_manager_model: true`)"),
  the Configuration Parameters list stating the default (`default: false`),
  and the "Model Override Behavior" section's worked example.
- **Confidence**: settled (explicit documented default and behavior)
- **Quote**: "`prompt_template_model` (string, optional): Model to use for this prompt (overrides client model unless `ignore_prompt_manager_model: true`)"
- **Quote**: "If your API returns `"prompt_template_model": "gpt-5.6-terra"`, LiteLLM will use `gpt-5.6-terra` regardless of what the client specified."
- **Our assessment**: This is the second, **non-router** place a model can be
  substituted on a live request path — the LiteLLM router (adaptive, complexity,
  fallback chains) is the first. It inverts the usual trust direction: the
  caller explicitly names a model and the prompt store can override it, so cost
  attribution, per-model SLOs, and canary semantics for that path can be
  silently redirected by a service the caller may not even own. Default-on is
  the operational hazard: the escape hatch (`ignore_prompt_manager_model: true`)
  exists but is opt-in.

### Claim 4: Assigning parameter precedence to the prompt: `prompt_template_optional_params` are merged with the client's params with the *prompt's* values winning on collision — e.g. prompt `temperature 0.7` beats client `temperature 0.9` — unless `ignore_prompt_manager_optional_params: true` is set (default `false`)
- **Evidence**: The "Response Format" contract and the "Parameter Merging
  Behavior" section with its worked before/after example.
- **Confidence**: settled (explicit documented precedence and example)
- **Quote**: "Client params are merged with prompt params, with prompt params taking precedence:"
- **Quote**: "`ignore_prompt_manager_optional_params`: If `true`, don't merge prompt's optional params with client params (default: `false`)"
- **Our assessment**: The counterintuitive direction — the caller's explicit
  `temperature 0.9` is silently replaced by the store's `0.7` — is sampling
  drift invisible in the caller's code. For deterministic-eval and
  regression-testing workflows, this is a silent reconfiguration of the model
  call. The merged-result example in the source (`# Final params:
  {"temperature": 0.7, "max_tokens": 500, "top_p": 0.95}`) shows the semantics
  unambiguously: the union of params with prompt-wins on the overlap.

### Claim 5: `provider_specific_query_params` is an out-of-band config channel — arbitrary key/value pairs declared in `config.yaml` are forwarded as query parameters on the gateway's HTTP call to the third-party prompt store, alongside `prompt_id`
- **Evidence**: The Configuration Parameters list ("Custom query parameters
  sent to your API (optional)") and the config-block example passing
  `project_name: litellm` and `slug: hello-world-prompt-2bac`.
- **Confidence**: settled (documented config surface)
- **Quote**: "`provider_specific_query_params`: Custom query parameters sent to your API (optional)"
- **Quote**: "- Custom parameters: Any additional parameters you configured in `provider_specific_query_params`"
- **Our assessment**: A second config-to-runtime channel: beyond overriding
  model/params (Claims 3-4), the gateway config reaches *into the third-party
  call itself*. The example uses it for tenanting/scoping (`project_name`,
  `slug`), but the contract is free-form — any param the store invented ends up
  in the request. This is config-surface drift outside the deploy pipeline: a
  prompt-store operator can add a required query param and the gateway config
  update is a `config.yaml` change that must be coordinated out-of-band.

### Claim 6: The integration adds a config-declared credential surface — `api_key` is an optional bearer credential the gateway presents to the prompt store (`sent as `Bearer` token`), and the page's only security guidance is generic (HTTPS, secrets in env vars, rate limiting, input validation)
- **Evidence**: The Configuration Parameters list and the "Security
  Considerations" section (all six items are one-line generic advice).
- **Confidence**: settled (documented surface; the "generic only" observation
  is directly visible on the page)
- **Quote**: "`api_key`: Optional API key for authentication (sent as `Bearer` token)"
- **Our assessment**: A second credential now sits in the gateway's config and
  is presented on request-path calls (Claim 2). The page's own security section
  recommends nothing novel — store keys in env vars, use HTTPS, validate
  inputs — consistent with the triage's call to not over-extract it. Worth one
  line in the note because it is part of the dependency's credential surface,
  not because the advice is new.

### Claim 7: The integration is explicitly beta — the endpoint lives under `/beta/` and the page closes with an explicit "This is a **beta API**" status, so the contract (endpoints, defaults, response fields) is version-sensitive
- **Evidence**: The endpoint path itself (`/beta/litellm_prompt_management`)
  and the closing "Questions?" section.
- **Confidence**: settled (explicit status on the page)
- **Quote**: "Implement `GET /beta/litellm_prompt_management`"
- **Quote**: "This is a **beta API**. We're actively improving it based on feedback."
- **Our assessment**: The beta label bounds every claim in this note: the two
  override defaults and the escaping flags are current-as-of 2026-09-17 and
  may drift while the API stabilizes. The page is also fresh — its examples
  use `gpt-5.6-terra`, a model the corpus's own Day-0 note
  (`blog-litellm-gpt-5-6-sol-terra-luna-day-0.md`) confirms is current — so
  this is a living page, not archived content.

### Claim 8: The prompt-store contract is a fetch-and-substitute pipeline — the gateway fetches the prompt template, substitutes `{variable}` / `{{variable}}` placeholders from `prompt_variables` (case-sensitive), and makes the model request using the store-provided model and optional params
- **Evidence**: The "Usage" examples (SDK and proxy), the "Variable
  Substitution" section ("Both `{variable}` and `{{variable}}` formats are
  supported"), and the Troubleshooting item "Variables are case-sensitive".
- **Confidence**: settled (documented behavior and worked examples)
- **Quote**: "LiteLLM automatically substitutes variables in your prompt templates using the `{variable}` syntax. Both `{variable}` and `{{variable}}` formats are supported."
- **Quote**: "That's it! LiteLLM fetches your prompt, applies variables, and makes the request"
- **Our assessment**: This completes the request-path picture: prompt
  retrieval, variable rendering, and the model/param substitution (Claims 3-4)
  all happen inside the gateway at request time. The caller's `messages` are
  padded into/around the fetched template, so the effective conversation the
  model sees is a gateway assembly of caller content + store-owned template —
  another non-obvious surface if anyone debugs a prompt after the fact.

### Claim 9: The page documents no way to detect that a prompt-store override was applied — no log line, response header, or metric proving the request was served on the store's model/params, so an operator cannot tell from the request path whether the prompt store (not the router) re-routed the traffic
- **Evidence**: No observability section exists on the page: the "Response
  Format" lists response fields to the *store's caller-side* contract and no
  `x-litellm-*`-style attribution header is specified anywhere; the
  Troubleshooting items address configuration errors ("Model not being
  overridden" → "Check if `ignore_prompt_manager_model: true` is set in
  config"), not runtime attribution.
- **Confidence**: emerging (the absence is directly observable; the operational
  framing is our synthesis)
- **Quote**: "## Troubleshooting" / "-   Check if `ignore_prompt_manager_model: true` is set in config" / "-   Verify your API is returning `prompt_template_model` in the response"
- **Our assessment**: This is the direct answer to the triage key question —
  *how would an operator detect that a request was silently re-routed by the
  prompt store rather than by the router?* — and the docs do not answer it.
  The corpus's routing notes show LiteLLM *can* provide attribution
  (`x-litellm-adaptive-router-model` in `docs-litellm-adaptive-router.md`
  Claim 8; the Auto Router v2 decision log in `blog-litellm-auto-router-v2.md`
  Claim 8); this page specifies no equivalent for the prompt-store override.
  Operators adopting the default behavior get silent substitution with no
  documented hook to distinguish it from router behavior, which breaks the
  Ch05 response-`model`-surface rule.

## Concrete Artifacts

All artifacts below are verbatim from
https://docs.litellm.ai/docs/adding_provider/generic_prompt_management_api
(rendered content, checked 2026-09-17; code blocks re-flowed to line breaks
from the Docusaurus fenced blocks).

### Step 1 config (from "Get Started in 3 Steps", verbatim)

```yaml
prompts:
  - prompt_id: "simple_prompt"
    litellm_params:
      prompt_integration: "generic_prompt_management"
      api_base: http://localhost:8080
      api_key: os.environ/YOUR_API_KEY
```

### Full config with escape hatches (from "LiteLLM Configuration", verbatim)

```yaml
model_list:
  - model_name: gpt-5.6-luna
    litellm_params:
      model: openai/gpt-5.6-luna
      api_key: os.environ/OPENAI_API_KEY
prompts:
  - prompt_id: "simple_prompt"
    litellm_params:
      prompt_integration: "generic_prompt_management"
      provider_specific_query_params:
        project_name: litellm
        slug: hello-world-prompt-2bac
      api_base: http://localhost:8080
      api_key: os.environ/YOUR_PROMPT_API_KEY  # optional
      ignore_prompt_manager_model: true  # optional, keep client's model
      ignore_prompt_manager_optional_params: true  # optional, don't merge prompt manager's params (e.g. temperature, max_tokens, etc.)
```

### Endpoint contract (from "API Contract", verbatim)

```
GET /beta/litellm_prompt_management?prompt_id={prompt_id}&{custom_params}
```

### Example response (from "Response Format", verbatim)

```json
{
  "prompt_id": "hello-world-prompt-2bac",
  "prompt_template": [
    {
      "role": "system",
      "content": "You are a helpful assistant specialized in {domain}."
    },
    {
      "role": "user",
      "content": "Help me with {task}"
    }
  ],
  "prompt_template_model": "gpt-5.6-terra",
  "prompt_template_optional_params": {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9
  }
}
```

### Parameter merging example (from "Parameter Merging Behavior", verbatim)

```
# Prompt returns: {"temperature": 0.7, "max_tokens": 500}
# Client sends: {"temperature": 0.9, "top_p": 0.95}
# Final params: {"temperature": 0.7, "max_tokens": 500, "top_p": 0.95}
```

### Proxy usage with prompt_id (from "Using with LiteLLM Proxy", verbatim)

```
curl http://0.0.0.0:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -d '{
    "model": "gpt-5.6-terra",
    "prompt_id": "simple_prompt",
    "prompt_variables": {
      "domain": "healthcare",
      "task": "patient risk assessment"
    },
    "messages": [
      {"role": "user", "content": "Analyze the following data..."}
    ]
  }'
```

### Configuration Parameters (from "Configuration Parameters", verbatim)

- `prompt_integration`: Must be `"generic_prompt_management"`
- `provider_specific_query_params`: Custom query parameters sent to your API (optional)
- `api_base`: Base URL of your prompt management API
- `api_key`: Optional API key for authentication (sent as `Bearer` token)
- `ignore_prompt_manager_model`: If `true`, use the model specified by client instead of prompt's model (default: `false`)
- `ignore_prompt_manager_optional_params`: If `true`, don't merge prompt's optional params with client params (default: `false`)

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/blog-litellm-auto-router-v2.md` — **cited** (Extends — see
  below).
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session cost/iteration caps (`max_iterations` / `max_budget_per_session`);
  no prompt-store or override-precedence content.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP
  coding-agent intake; unrelated to prompt-management integration.
- `source-notes/docs-litellm-helicone-integration.md` — **cited** (Extends —
  the mining precedent for a LiteLLM vendor integration page; see below).
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  runtime-blocking guardrail scanners and post-hoc tracing; no gateway
  prompt-management contract.
- `source-notes/docs-litellm-generic-guardrail-api.md` — **cited**
  (Corroborates / Extends — the sibling "integrate without a PR" contract,
  issue #1359; see below).
- `source-notes/docs-promptfoo-classifier-grading.md` — **dismissed**:
  HuggingFace classifier graders for eval assertions; unrelated.
- `source-notes/docs-litellm-a2a-invoking-agents.md` — **dismissed**: A2A
  agent invocation over the OpenAI bridge; no prompt-management content.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: per-agent
  declared-charge accounting on the A2A path; unrelated.
- `source-notes/blog-litellm-claude-fable-5-day-0.md` — **dismissed**: Day-0
  model-launch blog (Claude Fable 5); a different model family with no
  prompt-management or override content.

Additional cross-references found by searching `source-notes/` (triage overlap
list plus the corpus search): `docs-litellm-adaptive-router.md`,
`failure-litellm-model-cost-map-silent-fallback.md`,
`docs-langfuse-prompt-management.md`, `blog-litellm-gpt-5-6-sol-terra-luna-day-0.md`
(all cited below).

**Primary cross-references (verified per MINER §4b — claims re-read in the
cited notes before writing):**

- **Corroborates**:
  - `source-notes/docs-litellm-adaptive-router.md` **Claim 8**
    (`x-litellm-adaptive-router-model` response header reveals which model
    actually served) — this page *documents no such attribution hook* for the
    prompt-store override, so the two pages together bound LiteLLM's
    described attribution surface: routing overrides are attributed, prompt
    overrides are not. (Verified: Claim 8 heading + the header quote in that
    note.)
  - `source-notes/blog-litellm-gpt-5-6-sol-terra-luna-day-0.md` **Claim 1**
    (GPT-5.6 introduces the Sol/Terra/Luna three-tier naming) — the example
    model `gpt-5.6-terra` on this page is a real, current model family per the
    corpus's own Day-0 note, confirming the page is living (not stale) content.
    (Verified: Claim 1 heading + naming quote.)
- **Contrasts** (mechanism difference, not a contradiction — no issue filed):
  - `source-notes/docs-langfuse-prompt-management.md` **Claim 2** ("adds no
    application latency and removes availability risk because prompts are
    cached client-side") and **Claim 7** (client-side TTL caching with a
    fallback chain local → API → Redis → PostgreSQL). Langfuse documents a
    client-side cache with a **fallback chain** and no request-path dependency;
    the Generic Prompt Management API documents server-side in-memory caching
    ("your API endpoint is only called once per unique prompt configuration")
    and **no fallback or failure behavior** on a cache miss. Different products,
    different documented guarantees — this note records LiteLLM's silence
    (Claim 2 here) against Langfuse's explicit guarantee rather than claiming
    either is right. (Verified: Claims 2 and 7 in that note.)
- **Extends**:
  - `source-notes/docs-litellm-generic-guardrail-api.md` **Claim 1** (PR-less
    guardrail integration contract — `POST /beta/litellm_basic_guardrail_api`)
    — the prompt-management page is the *second* member of the corpus's
    "LiteLLM generic beta integration contract" family: same "No PR required"
    pitch, same out-of-process third-party service in the gateway path, same
    beta-label. (Verified: Claim 1 heading + the "No PR required" quote.) The
    guardrail page documented its failure semantics (fail-open/fail-closed);
    the prompt page documents none — a useful within-family contrast.
  - `source-notes/docs-litellm-adaptive-router.md` — adds a **second,
    non-router model-substitution authority** to the corpus's routing picture:
    the adaptive router (and Auto Router v2's tier pools) substitute via
    routing logic; the prompt store substitutes via the default-on
    `prompt_template_model` override (Claim 3 here). An operator debugging
    "why did this request hit model X" must now check both surfaces.
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md`
    **Lessons 2-3** — extends the corpus's "silent, request-invisible change
    with cost consequences" thread: that note is about silent fallback to a
    stale cost map surfacing as `cost=0` with no warning log; this page's
    default-on model override surfaces as a silent model/param substitution
    with no documented detection hook. Both are "the degradation is invisible
    to request success metrics." (Verified: Lessons 2-3 in that note.)
  - `source-notes/docs-litellm-helicone-integration.md` — mining precedent:
    that note's framing ("the documented wiring, not the wiring that has
    survived production," community-maintained caveat) governs here too; like
    the Helicone config snippets, these config keys are the documented *surface*,
    not production-validated behavior. (Verified: Claim 4 / community-maintained
    banner in that note.)
  - `source-notes/blog-litellm-auto-router-v2.md` **Claim 3** ("predictable
    beats clever for debuggability") and **Claim 8** (decision log with
    `cause=` attribution) — the routing world gives per-request attributable
    decisions; the prompt-management world (this page) gives none, which is
    exactly the debuggability asymmetry this note's Claim 9 records. (Verified:
    Claim 3 quote and Claim 8 decision-log format in that note.)
- **Novel** (first appearances in the corpus):
  - The **non-router model-substitution authority**: a deployed, external
    prompt store whose response can change the model and sampling params on a
    live request path *without a deploy of the calling service* (Claims 3-4).
  - The **documented-silence finding**: a request-path external dependency
    with in-memory caching keyed on prompt_id/label/version and **no documented
    failure behavior** — contrasted explicitly against Langfuse's documented
    fallback chain (Claim 2).
  - `provider_specific_query_params` as an out-of-band config channel from
    gateway `config.yaml` into a third-party HTTP call (Claim 5).
  - The **no-attribution finding**: no log/header/metric for prompt-store
    overrides, against the adaptive router's `x-litellm-adaptive-router-model`
    header and Auto Router v2's decision log (Claim 9).
- **Contradicts**: None. The Langfuse contrast is a documented-guarantee
  difference across two products ("Langfuse documents a fallback chain;
  LiteLLM's page documents none") rather than two opposing claims about the
  same system. No opposing claim exists in any source note for the override
  semantics. Verified against CONTRADICTIONS.md (no matching `C-NNN` entry)
  and all open `contradiction`-labeled issues (#1150/#1307/#1322/#1338/#1352 —
  none touch prompt management). **No contradiction issue filed.**

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "Silent model fallback breaks
  attribution" (`guide/05-llm-ops-reliability.md:478`)**: Extend the
  substituting-authorities list. Today the chapter covers the Fable 5→Opus 4.8
  silent fallback and the response-`model`-surface rule ("do not infer it from
  the request"). Add the **prompt store as a second substitution source**: when
  prompt management is enabled with the default override behavior, the served
  model/params may come from the store's response, not the router or the
  caller (Claims 3-4), so the response-`model` verification rule covers only
  *model*, not *params* (sampling drift via `prompt_template_optional_params`
  is invisible even under the rule).
- **Chapter 05 (LLM Ops Reliability) — "Parameter migration hazards"
  (`guide/05-llm-ops-reliability.md:245`) and the availability section**:
  Record the prompt-fetch dependency and its undocumented failure behavior
  (Claim 2): on every cache miss (new prompt version/label, restart) the
  request path spans a third-party store with no documented timeout/fallback/
  stale-serve semantics. Recommend, for production adoption: set
  `ignore_prompt_manager_model: true` / `ignore_prompt_manager_optional_params:
  true` unless the store-owned override is an explicit product decision, and
  treat the prompt service as an availability SLO input (error budget member)
  rather than assuming the docs' caching sentence ("called once per unique
  prompt configuration") implies low dependency.
- **Chapter 06 (Security and Trust)**: Add the trust-boundary line for prompt
  management: a remote store can silently redirect traffic to a different
  (potentially more expensive) model (Claim 3), and the gateway holds a second
  config-declared bearer credential presented on request-path calls (Claim 6).
  Cite against Ch06's supply-chain/trust-rollout framing: the store is a
  trustworthy-network component whose response mutates the request before it
  reaches the provider.
- **Chapter 02 (Observability)**: Record the attribution gap (Claim 9): the
  corpus's routing primitives (`x-litellm-adaptive-router-model`,
  `blog-litellm-auto-router-v2.md` decision log) give per-request attribution
  for *routing* overrides; this page specifies no equivalent for prompt-store
  overrides. Recommend requesting/adding one (log line or response header
  naming the effective model/params and the override source) before relying on
  the default-on behavior, and note the beta status (Claim 7) as a
  version-sensitivity caveat for any dashboards built on the contract.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (https://docs.litellm.ai/docs/adding_provider/generic_prompt_management_api,
  HTTP 200, no paywall), 2026-09-17. All `Quote` fields are contiguous verbatim
  strings from the page prose (config-parameter bullets reproduced exactly);
  code blocks in Concrete Artifacts are copied from the page's fenced blocks
  (in-line comments preserved) and re-flowed to line breaks from the
  Docusaurus `token-line` structure. The page is self-contained; no sub-pages
  were fetched (the sibling `docs/proxy/*` prompt pages and the linked
  `mock_prompt_management_server.py` cookbook file are separate surfaces and
  recorded as such, not mined).
- Prospector triage honored: extraction centers the request-path control
  semantics — override precedence (Claims 3-4), the external hot-path
  dependency and its documented-failure-behavior silence (Claim 2), the
  `provider_specific_query_params` config channel (Claim 5), and the detection
  gap (Claim 9) — per its "Specific extraction targets." Per the triage's
  caveats, the beta status is recorded (Claim 7) and the "no production
  evidence" assessment bounds `confidence_overall` to `emerging`; the route
  "config-surface-outside-the-deploy-pipeline" framing motivated the Guide
  Impact, and per the reconciling triage note (`priority:medium` retained) the
  page's real contract + clear Ch05 fit are captured without inflating its
  thin failure-mode content.
- **Contradiction scan (MINER §4a)**: no contradiction issue filed and no new
  one warranted. The Langfuse contrast (fallback chain vs no documented
  behavior) is a cross-product documented-guarantee difference, not an opposing
  claim on shared ground; `CONTRADICTIONS.md` and the five open
  `contradiction`-labeled issues hold nothing on prompt management.
- **Cross-ref verification (§4b)**: before citing, re-read
  `docs-litellm-adaptive-router.md` Claim 8,
  `docs-litellm-generic-guardrail-api.md` Claim 1,
  `failure-litellm-model-cost-map-silent-fallback.md` Lessons 2-3,
  `docs-langfuse-prompt-management.md` Claims 2 and 7,
  `docs-litellm-helicone-integration.md` Claim 4,
  `blog-litellm-auto-router-v2.md` Claims 3 and 8, and
  `blog-litellm-gpt-5-6-sol-terra-luna-day-0.md` Claim 1. No claim numbers
  invented; every `Claim N` citation resolves to a real numbered claim in the
  cited note. Candidate dismissals in Cross-References are grounded in the
  candidates file's stated one-liners.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes:
  the contract mechanics (endpoint, config keys, precedence defaults,
  cache-key semantics) are documented product behavior (`settled` as-
  documented), but the page is BETA, carries no production/measurement
  evidence, and the operational findings this note highlights (availability
  dependency of the fetch in Claim 2, the silent-substitution hazard in Claims
  3-4, the attribution gap in Claim 9) are the Miner's synthesis from that
  documented surface plus its absences — not measured outcomes. Per the
  Prospector's guidance, nothing here is promoted beyond `emerging` without a
  practitioner corroboration.