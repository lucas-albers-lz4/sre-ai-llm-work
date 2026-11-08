---
source_url: https://www.promptfoo.dev/docs/providers/anthropic
source_type: docs
title: "Promptfoo Providers: Anthropic — Model Lifecycle, Per-Model Parameter Suppression, and the Claude Code OAuth Credential Path"
author: "Promptfoo (vendor documentation)"
date_published: "unknown (page last updated 2026-11-08)"
date_extracted: 2026-11-08
last_checked: 2026-11-08
status: current
confidence_overall: emerging
issue: "#1986"
---

# Promptfoo Providers: Anthropic — Model Lifecycle, Per-Model Parameter Suppression, and the Claude Code OAuth Credential Path

> The vendor reference for promptfoo's `anthropic:messages:` provider — a
> per-model normalization layer that silently drops sampling/thinking/tool
> parameters, rewrites request shape rather than erroring, maps one model name
> across four platforms, and can authenticate eval spend with a developer's
> Claude Code OAuth credential instead of an attributable API key.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Providers >
  Anthropic" reference page under `/docs/providers/anthropic`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (part of OpenAI per the site banner). First-party documentation of what the
  harness does with an Anthropic request, so authoritative for promptfoo's own
  normalization behavior and configuration surface. It is vendor-positioned:
  the page reports no measured eval outcomes, no false-pass rate, and no
  independent validation, and its model/pricing tables are the vendor's
  transcription of Anthropic's catalog. The behavior is checkable against an
  installed CLI and an Anthropic-compatible endpoint.
- **Scope**: A single self-contained provider reference. Covers setup and auth
  (Console API key and Claude Code OAuth reuse), the current/retired model
  catalog and aliases, the cross-platform model-ID map (Anthropic API, Azure
  AI Foundry, AWS Bedrock, GCP Vertex), supported parameters, prompt template
  and assistant-prefill rules, classifier refusals, tool calling (including
  web search / web fetch / memory), MCP, vision, prompt caching, citations,
  PDFs, per-model notes (Fable/Mythos 5/5.1, Opus 5/5.5, Sonnet 5/5.5, Haiku
  5.5, Opus 4.7/4.8), extended thinking, effort levels, structured outputs,
  and model-graded tests. Does NOT cover the sibling OpenAI, Bedrock, Vertex,
  or Azure provider pages, nor the separate Claude Agent SDK provider; the
  page defers rate-limit behavior to the sibling rate-limits page.
- **Last updated**: Nov 8, 2026 by renovate[bot]; page is undated but documents
  the current Claude 5.x era.

## Extracted Claims

### Claim 1: Retired Anthropic model IDs return `404 not_found_error` on a direct `anthropic:messages:` call, and promptfoo retains their pricing only for historical cost attribution
- **Evidence**: The "Retired on the Anthropic API" section, which lists nine
  retired IDs with suggested replacements and states the wire failure
  explicitly.
- **Confidence**: settled (documented product behavior; the 404 is checkable)
- **Quote**: "These IDs return `404 not_found_error` from Anthropic, so a direct `anthropic:messages:` call will fail. Promptfoo still keeps their pricing, because cost attribution on historical evals needs it and because partner platforms set their own lifecycle dates."
- **Our assessment**: Buy it as a product fact with a useful operational edge:
  a model can remain in the *cost map* long after it is unreachable, so a
  successful cost lookup is not evidence the model exists. This is the same
  "known-model metadata ≠ reachable model" separation the guide already draws
  for LiteLLM cost-map reloads, here expressed as an intentional vendor
  behavior rather than a bug.

### Claim 2: Three retired IDs are also withdrawn from Bedrock and are rejected *locally* with `Unknown Amazon Bedrock model` rather than by an upstream 404
- **Evidence**: The same retirement section calls out the Bedrock exception
  and names the three IDs.
- **Confidence**: settled (explicit, checkable list)
- **Quote**: "Three of these are withdrawn from Bedrock as well (`claude-3-opus-20240229`, `claude-opus-4-20250514`, `claude-3-5-haiku-20241022`) and are rejected locally with `Unknown Amazon Bedrock model`."
- **Our assessment**: Buy it. This is a second, distinct failure shape for the
  guide's "reload success ≠ model reachability" rule: a direct Anthropic call
  fails upstream with a provider 404, while a Bedrock call can fail before any
  network request because the SDK's local model allow-list does not know the
  ID. A reachability probe that only checks "did the request leave the process"
  or only checks one backend will miss the other class.

### Claim 3: Anthropic publishes no `-latest` aliases; only the bare family alias resolves, and 4.6+ IDs are already unversioned
- **Evidence**: The "Model aliases" note, with a concrete failing alias.
- **Confidence**: settled (documented, checkable)
- **Quote**: "Anthropic does not publish `-latest` aliases — `claude-sonnet-4-5-latest` returns a `not_found_error`."
- **Our assessment**: Buy it. The pattern matters for migration tooling: a
  config that "pins to latest" by appending `-latest` (a common OpenAI habit)
  fails closed with a 404 rather than tracking a new model. The page also
  documents the opposite trap — the bare family ID resolves to a dated ID
  (`claude-sonnet-4-5` → `claude-sonnet-4-5-20250929`) — so "bare family" is
  a moving alias, not a stable pin.

### Claim 4: The same Claude model has a different ID shape on each platform, and Bedrock even varies the prefix by model (`global.` vs `anthropic.`)
- **Evidence**: The "Cross-Platform Model Availability" table (reproduced in
  Concrete Artifacts) maps every current and retired row across Anthropic API,
  Azure AI Foundry, AWS Bedrock, and GCP Vertex. Sonnet 5.5 is
  `global.anthropic.claude-sonnet-5-5` on Bedrock while Opus 5.5 is
  `anthropic.claude-opus-5-5`; Vertex appends `@<date>` for 4.5-generation
  models.
- **Confidence**: settled (explicit table; vendor transcription of provider
  catalogs)
- **Quote**: "Claude models are available across multiple platforms. Here's how the model names map across different providers:"
- **Our assessment**: Buy the shape, treat individual rows as perishable. The
  table is exactly the conditioning-variable evidence the guide's
  "Per-backend constraints" rule calls for: a model alias is not portable, and
  the *same* Bedrock backend does not use one prefix convention across models.
  The `global.` vs `anthropic.` distinction is especially easy to miss because
  both are valid Bedrock IDs with different reach/region semantics.

### Claim 5: A limited-access model returns the same `not_found_error` as a retired model, so entitlement and retirement are indistinguishable on the wire
- **Evidence**: The Mythos rows carry a "(limited)" marker and the page states
  the shared error behavior explicitly.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The Mythos rows are limited-access models: the ID is correct, but an org without access gets the same `not_found_error` a retired model returns."
- **Our assessment**: Buy it. This is a concrete failure-class for the guide's
  reachability rule: the error code cannot tell an operator whether to request
  entitlement, update a model ID, or check a different backend. The diagnostic
  must come from the catalog/contract, not from the 404 body.

### Claim 6: A classifier refusal is a *successful* Messages response with `stop_reason: refusal`, and promptfoo only produces the top-level `guardrails` signal when `stop_details` is present
- **Evidence**: The "Classifier Refusals" section, which states the success
  status, the normalization shape, and the `stop_details` precondition.
- **Confidence**: emerging (vendor docs; the conditional normalization is
  documented behavior but not independently measured)
- **Quote**: "An Anthropic safety-classifier refusal can arrive as a successful Messages response with `stop_reason: refusal`." and "Promptfoo currently requires `stop_details` to create the top-level `guardrails` signal. A model-written refusal or `stop_reason: refusal` without details is therefore not the same assertion result."
- **Our assessment**: Buy it; this is the producer-side detail the corpus's
  guardrails note was missing. A refusal delivered with HTTP 200 is not a
  transport error, and the assertion outcome depends on a field
  (`stop_details`) that is optional. `not-guardrails` therefore tests the
  *structured classifier signal*, while `is-refusal` tests model-written
  refusal text — two different gates that a casual reader could conflate.

### Claim 7: Refusal billing is category-dependent — pre-output refusals are free unless the category is `bio`, `frontier_llm`, or `reasoning_extraction`
- **Evidence**: The "Classifier Refusals" section's cost paragraph, which
  cites Anthropic's refusal billing rules.
- **Confidence**: emerging (vendor transcription of provider billing rules;
  no worked invoice)
- **Quote**: "refusals before any output cost zero unless the category is `bio`, `frontier_llm`, or `reasoning_extraction`. Those categories and refusals after output begins use normal token pricing."
- **Our assessment**: Buy it for cost accounting on red-team suites, where
  refusals are the expected outcome. A red-team budget that assumes "blocked
  requests are free" undercounts exactly the high-risk categories the suite is
  designed to probe, and refusals that begin after partial output bill
  normally regardless of category.

### Claim 8: A `pause_turn` response is resumed up to 5 times with the code-execution container preserved and usage/cost summed; exhaustion returns partial output, warns, and is not cached
- **Evidence**: The "Paused Turns" subsection, which spells out the retry
  budget, container preservation, cost summing, and failure behavior.
- **Confidence**: settled (documented product behavior)
- **Quote**: "A long server-tool run can stop with `stop_reason: pause_turn` before Claude finishes. Promptfoo resumes it up to 5 times, preserving the code execution container and summing each request's usage and cost." and "If resuming fails or reaches the limit, the result keeps its partial output with `finishReason: pause_turn`, logs a warning, and is not cached."
- **Our assessment**: Buy it, and treat it as a reliability/cost contract, not
  just a retry note. One logical eval case can be up to five billed requests
  whose cost is invisible in a case-level pass/fail, and the partial-output
  result is a distinct outcome (`finishReason: pause_turn`) that a gate must
  decide how to score rather than silently accepting. The no-cache rule also
  means pause-turn cases are re-billed on every rerun.

### Claim 9: Sampling parameters are silently omitted per model, including promptfoo's built-in `temperature: 0` default, with only a one-time warning
- **Evidence**: The "Supported Parameters" note plus the Opus 5/5.5, Sonnet
  5/5.5, Haiku 5.5, Opus 4.7, and Opus 4.8 model notes, all of which describe
  omission rather than a hard error.
- **Confidence**: emerging (vendor docs; the omission is documented but its
  effect on eval conclusions is our inference)
- **Quote**: "Sampling support varies by model. Promptfoo omits unsupported `temperature`, `top_p`, and `top_k` settings; see the model notes below." and "Like Opus 4.7/4.8, Opus 5 rejects `temperature`, `top_p`, and `top_k` with a 400; promptfoo omits all three from every request, including its built-in `temperature: 0` default." and "Setting any of them in config or `ANTHROPIC_TEMPERATURE` logs a one-time heads-up so you can clean the values out of your eval."
- **Our assessment**: Buy it; this is the page's core cross-chapter finding. A
  config that reads "temperature 0, deterministic" is not what executes on
  these models, and because the warning is emitted once per run, a run that
  silently sampled differently still exits green. The guide's "Provider
  parity" rule already says present-but-null and omitted are not equivalent;
  this page adds the harness-side variant: *omitted is not rejected*, so the
  gate must assert the exact wire payload rather than trust the YAML.

### Claim 10: Forced tool use and disabled thinking are model-gated, and promptfoo rewrites or drops them rather than surfacing an error
- **Evidence**: The per-model notes and the "Extended Thinking" section. Sonnet
  5.5 substitutes `between_tools` for `disabled`; Opus 5.5/Fable 5.1/Mythos 5.1
  drop forced `tool_choice` and `disabled` thinking; Opus 5 rejects `disabled`
  above `high` effort.
- **Confidence**: emerging (documented normalization behavior; effect on eval
  validity is our inference)
- **Quote**: "Forced tool use (`tool_choice` type `any` or `tool`) is incompatible with manual thinking and with Opus 5.5, Sonnet 5.5, Fable 5.1, and Mythos 5.1. Promptfoo omits it with a warning in those cases; use `auto` or `none`." and "`thinking: { type: 'disabled' }` is only accepted at `effort` `high` or below; pairing it with `xhigh` or `max` returns a 400."
- **Our assessment**: Buy it. The guide's "Parameter migration hazards" rule
  covers parameters that are *rejected*; this page adds parameters that are
  *rewritten* (`enabled` → `adaptive`, `disabled` → `between_tools`) or
  dropped. A tool-choice assertion that expects "the model was forced to call
  this function" is not testing that on a model where the forcing directive
  was omitted — it is testing the model's unforced preference.

### Claim 11: `effort` defaults drift between models (Opus 5.5 `medium`, other effort-capable models `high`), so comparisons that do not set it explicitly measure reasoning depth, not model quality
- **Evidence**: The "Effort Level" section's support table and default
  sentence.
- **Confidence**: emerging (vendor docs; comparison consequence is our
  inference)
- **Quote**: "The API defaults to `medium` on Opus 5.5 and `high` on the other models that support effort. Set it explicitly when comparing models."
- **Our assessment**: Buy it. This is a measurement-methodology trap: an eval
  that swaps model IDs while leaving `effort` unset is not a controlled
  comparison. It extends the guide's evaluation-methodology rule that a metric
  without a unit is noise — here the missing unit is the reasoning-effort
  setting, and the drift is in the *default*, not the model name.

### Claim 12: Claude 4.6 and later reject assistant-message prefill, while 4.5 models still accept it
- **Evidence**: The "Prompt Template" section's assistant-prefill callout.
- **Confidence**: settled (documented model behavior)
- **Quote**: "Claude 4.6 and later models reject prompts ending with an `assistant` message."
- **Our assessment**: Buy it. A concrete migration hazard for the guide's
  "Parameter migration hazards" rule: a prompt-construction pattern that
  constrained output format on 4.5 fails on 4.6+, and the documented
  replacements (structured outputs or a system instruction) change the eval's
  request shape. The page does not say whether promptfoo auto-strips the
  trailing assistant message, so a migration test should assume it does not.

### Claim 13: `apiKeyRequired: false` makes the harness reuse a local Claude Code OAuth credential, with a fixed discovery order, Bearer + beta headers, an injected identity system block, and subscription billing
- **Evidence**: The "Authenticating via a Claude Code session" section, which
  documents the keychain/file lookup order, `CLAUDE_CONFIG_DIR` relocation, the
  beta headers, the identity system block, and the billing expectation.
- **Confidence**: emerging (vendor docs; billing behavior is explicitly
  "expected" and deferred to Anthropic)
- **Quote**: "When `apiKeyRequired` is `false` and no `ANTHROPIC_API_KEY` is available, Promptfoo loads the Claude Code OAuth credential from:" and "Promptfoo authenticates requests with a Bearer token, sends the `claude-code-20250219,oauth-2025-04-20` beta headers, and prepends the required Claude Code identity system block (`\"You are Claude Code, Anthropic's official CLI for Claude.\"`) to every Messages request." and "Requests made this way are expected to count against your Claude subscription the same way calls from the Claude Code CLI do"
- **Our assessment**: Buy it; this is the strongest cross-chapter item. The
  credential source is inferred from the developer's local profile (keychain →
  home-directory file → Windows profile file) rather than declared, and the
  page documents no ambiguity error when both an env API key and an OAuth
  credential exist — the `apiKeyRequired: false` path is gated on "no
  `ANTHROPIC_API_KEY` is available", so the env key simply wins. That is a
  conditioning variable for the guide's "declare, don't infer" rule rather than
  a contradiction: the rule governs gateway routing, while this is a local eval
  harness inheriting a developer seat. The spend-attribution consequence is the
  part to surface: eval cost lands on a subscription, not an attributable API
  key.

### Claim 14: Cost overrides are asymmetric-rate-hostile — legacy `cost` applies to both input and output, so fast-mode/asymmetric rates need `inputCost`/`outputCost`; cache writes cost 1.25×/2× and U.S. inference adds 10%
- **Evidence**: The Opus 5 pricing paragraph, the prompt-caching section, and
  the "Additional Capabilities" cost note.
- **Confidence**: settled for the mechanics (documented); emerging for the
  exact per-model rates (vendor transcription, perishable)
- **Quote**: "a single `cost` cannot express asymmetric rates, because it is applied as both the input and the output per-token price." and "five-minute writes cost 1.25 times the base input rate, and one-hour writes cost twice the base input rate." and "For Claude 4.6 and later, U.S. inference adds 10% to token costs, including cache reads and writes."
- **Our assessment**: Buy the mechanics. The guide's cost-map material treats
  per-token pricing as a two-number tuple; this page shows the harness surface
  can collapse it into one number unless the operator uses the split fields.
  The cache-write multiplier and the data-residency surcharge are additional
  cost dimensions that a naive `inputCost`/`outputCost` override will not
  capture, so a cost gate built on overrides can undercount.

### Claim 15: MCP mode disables the disk response cache, and provider labels / custom headers are the documented tenant-isolation carve-outs
- **Evidence**: The "Response caching with MCP" callout and the "Additional
  Capabilities" cache-label paragraph.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The disk response cache is skipped while `mcp.enabled` is `true`, because tool results can be non-deterministic between runs. Use `max_tool_calls` to bound spend." and "assign each provider a distinct, non-secret `label`" and "Requests with custom headers bypass the disk response cache because those headers may contain tenant credentials."
- **Our assessment**: Buy it. Three cache carve-outs with different causes:
  non-deterministic tool results (MCP), cross-tenant isolation (labels), and
  credential-bearing headers (custom headers). The MCP carve-out is a direct
  extension of the corpus's caching note: caching is on by default, but the
  provider-level `mcp.enabled` flag silently turns it off for that provider,
  so a "cached eval" and a "fresh eval" can be the same config with different
  spend and reproducibility.

### Claim 16: The web fetch tool is an egress boundary — trusted environments only, no model-constructed URLs, and `allowed_domains`/`blocked_domains` are mutually exclusive
- **Evidence**: The "Important Security Notes" list under the web fetch tool
  section.
- **Confidence**: settled (documented product guidance)
- **Quote**: "The web fetch tool requires trusted environments due to potential data exfiltration risks" and "The model cannot dynamically construct URLs - only URLs provided by users or from search results can be fetched" and "Only one of `allowed_domains` or `blocked_domains` can be specified, not both"
- **Our assessment**: Buy it. This is the eval-harness instance of the guide's
  "A guardrail is an egress boundary" rule: the tool's own docs recommend the
  allowlist (`allowed_domains`), and the mutual-exclusion constraint means an
  operator cannot layer allowlist and blocklist. The "model cannot construct
  URLs" statement bounds the threat model but does not remove it — fetched
  content can still carry attacker-controlled text into the context.

## Concrete Artifacts

Cross-platform model-ID map (subset reproduced as a markdown table from the
source's "Cross-Platform Model Availability" table; the source also marks
Mythos rows as limited access and retired rows as "Retired on the direct API"):

| Model | Anthropic API | Azure AI Foundry | AWS Bedrock | GCP Vertex AI |
|---|---|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | `claude-fable-5-1` | `anthropic.claude-fable-5-1` | `claude-fable-5-1` |
| Claude Mythos 5.1 | `claude-mythos-5-1` | `claude-mythos-5-1` (limited) | `anthropic.claude-mythos-5-1` (limited) | `claude-mythos-5-1` (limited) |
| Claude Opus 5.5 | `claude-opus-5-5` | `claude-opus-5-5` | `anthropic.claude-opus-5-5` | `claude-opus-5-5` |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | `claude-sonnet-5-5` | `global.anthropic.claude-sonnet-5-5` | `claude-sonnet-5-5` |
| Claude Opus 5 | `claude-opus-5` | `claude-opus-5` | `anthropic.claude-opus-5` | `claude-opus-5` |
| Claude 4.5 Opus | `claude-opus-4-5-20251101` (`claude-opus-4-5`) | `claude-opus-4-5-20251101` | `anthropic.claude-opus-4-5-20251101-v1:0` | `claude-opus-4-5@20251101` |
| Claude 4.5 Sonnet | `claude-sonnet-4-5-20250929` (`claude-sonnet-4-5`) | `claude-sonnet-4-5-20250929` | `anthropic.claude-sonnet-4-5-20250929-v1:0` | `claude-sonnet-4-5@20250929` |
| Claude 4.5 Haiku | `claude-haiku-4-5-20251001` (`claude-haiku-4-5`) | `claude-haiku-4-5-20251001` | `anthropic.claude-haiku-4-5-20251001-v1:0` | `claude-haiku-4-5@20251001` |

Claude Code OAuth credential reuse (config shape as documented; YAML expanded
for readability from the source's inline example):

```yaml
providers:
  - id: anthropic:messages:claude-sonnet-5
    config:
      apiKeyRequired: false
```

Credential discovery order documented by the page:

```text
1. macOS keychain entry `Claude Code-credentials` (darwin only), then
2. $HOME/.claude/.credentials.json on Linux and macOS, or
   %USERPROFILE%\.claude\.credentials.json on Windows.
```

Classifier-refusal normalization (only when `stop_details` is present), quoted
from the source:

```json
{
  "finishReason": "content_filter",
  "guardrails": {
    "flagged": true,
    "reason": "Content refused by Anthropic safety filters — category: ..."
  }
}
```

Effort-level support table (quoted structure from the source's "Effort Level"
section):

| Model family | Supported levels |
|---|---|
| Fable/Mythos 5 and 5.1, Opus 5.5, Opus 5, Sonnet 5, Opus 4.7/4.8 | `low`, `medium`, `high`, `xhigh`, `max` |
| Opus 4.6, Sonnet 4.6 | `low`, `medium`, `high`, `max` (no `xhigh`) |
| Opus 4.5 | `low`, `medium`, `high` |
| Sonnet 4.5, Haiku 4.5 | Not supported — omit `effort` |

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-guardrails-assertions.md` **Claim 11** — that
    note documents the consumer side ("Anthropic can return a successful
    message with `stop_reason: refusal`") and the provider-error-skip rule;
    this page is the Anthropic producer detail and adds the `stop_details`
    precondition. Its **Claim 3** (a missing `guardrails` signal fails open to
    `flagged: false`, passing with score 1) is the reason Claim 6 here matters:
    a refusal without `stop_details` is exactly the "missing signal" case.
    (Verified: #1303 Claims 3 and 11.)
  - `source-notes/docs-promptfoo-portkey-integration.md` **Claim 9** — that note
    documents the "interactive OAuth flow intended for browser clients" as a
    CI trap; this page's local-credential discovery is the same hazard in a
    different integration: an eval harness resolving a credential from the
    developer's interactive session rather than a declared secret. (Verified:
    `docs-promptfoo-portkey-integration.md` Claim 9.)
  - `source-notes/docs-promptfoo-llm-as-a-judge.md` **Claim 6** — documents
    `showThinking: false` for thinking-capable judges so reasoning is not mixed
    into the verdict; this page confirms `showThinking` is a provider-level
    output filter (default `true`) and that `thinking.display: omitted` still
    bills thinking tokens. (Verified: `docs-promptfoo-llm-as-a-judge.md`
    Claim 6.)

- **Contradicts**: None identified, and no contradiction issue filed. Checked
  `CONTRADICTIONS.md` (no relevant open entry) and the open
  `contradiction`-labeled issues; the closest is #1593 (promptfoo
  `tool_choice: 'none'` → Anthropic mapping), which is about a different
  translation table and does not conflict with this page's model-level
  rejection of forced tool use. The apparent tension with the guide's Ch06
  "declare, don't infer" credential rule is a scope difference, not a
  contradiction: the guide rule governs gateway credential routing, while this
  page documents a local eval harness inheriting a developer's Claude Code
  session. Both can be true; the guide should record the conditioning variable
  (local eval vs shared gateway) rather than pick a winner.

- **Extends**:
  - `source-notes/docs-promptfoo-azure-vs-openai.md` **Claim 1** (provider
    identity is asymmetric in config — OpenAI by slug, Azure by deployment name
    plus `apiHost`) — this page supplies the full Anthropic/Azure/Bedrock/Vertex
    ID map that the Azure note's two-provider comparison implies. (Verified:
    #1642 Claim 1; the note's heading reads "Provider identity is asymmetric in
    config".)
  - `source-notes/docs-promptfoo-configuration-tools.md` **Claim 7** (the
    `tool_choice` translation is lossy and asymmetric — `'required'` becomes
    Anthropic `{ type: 'any' }`) — this page adds the *model-level* rejection
    of forced `any`/`tool` on 5.5-class models, which a provider-level
    translation table cannot express. (Verified: Claim 7 heading and body.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 1** (results
    are cached on disk by default) — this page adds the MCP carve-out, the
    tenant-label requirement, and the custom-header bypass, all of which are
    conditions under which that default does not hold. (Verified: Claim 1.)
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 6** (sampling and
    extended-thinking fields carry range constraints on the unified
    `/v1/messages` route) — that note documents the gateway-layer constraints;
    this page documents the harness-layer *suppression* behavior for the same
    parameters. Different layers, same parameter surface. (Verified: Claim 6.)
  - `source-notes/docs-promptfoo-mcp-server.md` **Claim 1** — that note covers
    promptfoo *as* an MCP server (exposing eval tools to agents); this page
    covers promptfoo *as* an MCP client (the Messages provider executing
    `tool_use` against an MCP server) plus the cache-skip behavior. (Verified:
    Claim 1 heading.)
  - `source-notes/docs-promptfoo-choosing-best-gpt-model.md` **Claims 3 and 5**
    (per-test `cost`/`latency` thresholds as the selection gate; the gate, not
    output quality, separated the models) — this page supplies a mechanism that
    can silently change what such a gate is measuring: unset `effort` defaults
    drift between models, and sampling parameters are omitted. (Verified:
    Claims 3 and 5 headings.)

- **Novel**: First corpus coverage of the Anthropic provider's per-model
  normalization layer:
  1. **Retired vs unentitled vs withdrawn** (Claims 1, 2, 5) — three distinct
     unreachability shapes (upstream 404, local `Unknown Amazon Bedrock model`,
     entitlement-masked 404) that a single reachability probe cannot
     distinguish.
  2. **The cross-platform ID map** (Claim 4), including the `global.` vs
     `anthropic.` Bedrock prefix variance and per-platform "(limited)" /
     "Not available" states.
  3. **Silent parameter suppression** (Claims 9-10) — omission instead of a
     400, including the harness's own `temperature: 0` default, with a
     once-per-run warning; the eval-green-but-not-what-you-configured failure
     class.
  4. **Effort-default drift** (Claim 11) as a comparison-validity hazard.
  5. **`pause_turn` resumption economics** (Claim 8) — up to five billed
     requests per logical case, partial output on exhaustion, no caching.
  6. **The `stop_details`-gated refusal signal** (Claim 6) and category-based
     refusal billing (Claim 7).
  7. **Claude Code OAuth credential reuse** (Claim 13) — a local,
     profile-dependent credential path with subscription billing and an
     injected identity system block; no prior corpus note covers
     OAuth/subscription-backed eval credentials.

## Guide Impact

- **Chapter 05 — "Reload success ≠ model reachability"
  (`guide/05-llm-ops-reliability.md:286`)**: Add the two provider-side
  unreachability variants from Claims 1, 2, and 5: (a) a retired ID returns an
  upstream 404 while its pricing stays in the cost map, so cost-map membership
  is not reachability; (b) on Bedrock, three of the same IDs are rejected
  *locally* with `Unknown Amazon Bedrock model`, so "the request never left the
  process" is a different failure from "the provider rejected it"; (c) a
  limited-access model returns the same 404 as a retired one, so the error code
  cannot tell entitlement from retirement. Recommend a per-backend end-to-end
  probe with a known-good ID, not a single alias check.
- **Chapter 05 — "Per-backend constraints are conditioning variables"
  (`guide/05-llm-ops-reliability.md:304`)**: Add the cross-platform ID map
  (Claim 4) as a concrete table, including the Bedrock `global.` vs
  `anthropic.` prefix variance and the Vertex `@<date>` suffix. The existing
  section documents Bedrock's inference-profile prefix and effort cap; this
  source shows the prefix convention itself is not uniform across models on the
  same backend.
- **Chapter 05 — "Parameter migration hazards"
  (`guide/05-llm-ops-reliability.md:327`)**: Extend from "rejected parameters"
  to "rewritten or silently omitted parameters" (Claims 9, 10, 12): sampling
  controls omitted (including the harness default), `thinking: enabled` →
  `adaptive`, `thinking: disabled` → `between_tools` or dropped, forced
  `tool_choice` dropped, and assistant-message prefill rejected on 4.6+. The
  rule should say a migration audit must check the *effective* request, not the
  config file.
- **Chapter 05 — "Provider parity in the shared forwarding path"
  (`guide/05-llm-ops-reliability.md:343`)**: Add the harness-side variant of
  the existing "present-but-null vs omitted" rule: here the harness *omits*
  unsupported parameters rather than rejecting them, and emits a one-time
  warning (Claim 9). A gate that asserts a config value rather than the wire
  payload can exit green on a request that never carried the value.
- **Chapter 05 — "Evaluation and measurement methodology"
  (`guide/05-llm-ops-reliability.md:386`)**: Add three measurement traps:
  (a) `effort` defaults drift between models, so model comparisons must set it
  explicitly (Claim 11); (b) a `pause_turn` case can be up to five billed
  requests with a partial-output outcome, so cost/pass accounting must count
  requests not cases (Claim 8); (c) refusal billing is category-dependent, so
  red-team budgets that assume blocked requests are free undercount the
  high-risk categories (Claim 7).
- **Chapter 06 — "A guardrail gate reads a signal — it does not run a
  guardrail" (`guide/06-security-and-trust.md:387`)**: Add the
  producer-side precondition (Claim 6): a refusal is HTTP 200 with
  `stop_reason: refusal`, and the top-level `guardrails` signal is created only
  when `stop_details` is present. A gate should use `not-guardrails` for the
  structured classifier signal and `is-refusal` for model-written refusal text,
  and should not treat a refusal without details as an equivalent result.
- **Chapter 06 — "A guardrail is an egress boundary — configure what crosses
  it" (`guide/06-security-and-trust.md:547`)**: Add the web fetch tool as a
  concrete harness egress surface (Claim 16): trusted-environment requirement,
  no model-constructed URLs, `allowed_domains` recommended, and
  `allowed_domains`/`blocked_domains` mutually exclusive (so allowlist and
  blocklist cannot be layered).
- **Chapter 06 — "Gateway credential routing: declare, don't infer"
  (`guide/06-security-and-trust.md:603`)**: Add a conditioning note for local
  eval harnesses (Claim 13): `apiKeyRequired: false` resolves a credential by
  inferring the developer's Claude Code profile (keychain → home file →
  Windows profile file), injects the Claude Code identity block, and bills the
  subscription; an env API key silently wins when present. This is not a
  contradiction of the gateway rule — the guide should state that the
  "declare, don't infer" rule applies to shared gateways, and that a local eval
  harness that reuses a developer seat must be treated as an unattributable
  spend path.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/providers/anthropic). Single self-contained
  page; the linked Azure, Bedrock, Vertex, and Claude Agent SDK provider pages
  were not deep-read (they are separate crawl-seed pages and separate source
  notes), so the cross-platform claims are limited to what this page's table
  states.
- `miner-related-notes.md` candidates were reviewed and dispositioned:
  1. `docs-litellm-mcp-linear-server.md` — dismissed: gateway-side hosted MCP
     identity/attribution, not Anthropic provider normalization.
  2. `docs-promptfoo-evaluate-coding-agents.md` — dismissed: agent capability
     tiers and workspace isolation; no shared claim with this page.
  3. `docs-litellm-batches-api.md` — dismissed: batch rate-limit accounting;
     unrelated.
  4. `docs-promptfoo-enterprise-findings-reports.md` — dismissed: red-team
     findings disposition/export; unrelated.
  5. `docs-promptfoo-multimodal-red-team.md` — dismissed: multimodal red-team
     approaches; unrelated.
  6. `docs-promptfoo-pi-scorer.md` — dismissed: third-party scoring model;
     unrelated.
  7. `docs-promptfoo-evaluate-openai-agents-python.md` — dismissed: OpenAI
     Agents Python tracing bridge; unrelated.
  8. `docs-litellm-evals-api.md` — dismissed: gateway-hosted Evaluations API;
     unrelated.
  9. `docs-promptfoo-test-agent-skills.md` — dismissed: skill A/B testing;
     unrelated.
  10. `docs-promptfoo-portkey-integration.md` — **cited** under Corroborates
      (Claim 9, interactive-OAuth CI trap) for the credential-substitution
      hazard.
- Additional cross-references (guardrails, Azure, caching, tools, LiteLLM
  unified messages, promptfoo-as-MCP-server, model selection, LLM-as-judge)
  were discovered by searching `source-notes/` and each cited claim number was
  re-opened and checked against the cited note before writing.
- Confidence is `emerging` overall: the page is first-party documentation of
  promptfoo's own behavior, but it is vendor-positioned, the model/pricing
  tables are perishable, and the eval-validity consequences (silent
  suppression, effort drift, pause-turn cost) are our synthesis rather than
  the vendor's measured claims.
