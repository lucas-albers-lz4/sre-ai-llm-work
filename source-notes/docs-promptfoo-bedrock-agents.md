---
source_url: https://www.promptfoo.dev/docs/providers/bedrock-agents
source_type: docs
title: "Promptfoo Providers: AWS Bedrock Agents — the Silent InvokeAgent Config Omission and the Two Trace Planes"
author: "Promptfoo (vendor documentation)"
date_published: unknown (living vendor docs; last updated 2026-11-03)
date_extracted: 2026-11-03
last_checked: 2026-11-03
status: current
confidence_overall: emerging
issue: "#2004"
---

# Promptfoo Providers: AWS Bedrock Agents

> The vendor reference for promptfoo's `bedrock-agent` provider makes an
> eval-validity admission that generalizes well beyond one provider: several
> safety- and behavior-relevant config keys (`guardrailConfiguration`,
> `inferenceConfig`, `promptOverrideConfiguration`, `actionGroups`,
> `inputDataConfig`) are accepted "for compatibility" but the AWS SDK omits
> them from the `InvokeAgent` runtime request — so a green eval neither applies
> the guardrail it appears to configure nor proves one ran. Verification has to
> move to the deployed agent and the Bedrock-native trace, which is a *separate
> plane* from promptfoo's OpenTelemetry trace.

## Source Context

- **Type**: docs (vendor provider reference — promptfoo `/docs/providers/bedrock-agents`,
  the "AWS Bedrock Agents" page in the Providers section; auto-discovered from
  the `promptfoo-docs` site-crawl seed)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  This is first-party documentation of the product's own provider adapter, so it
  is authoritative for the config surface and for what the adapter claims to
  send to AWS. It is vendor-positioned and evidence-thin: there are no run
  results, measured coverage, or independent verification, and the page's
  statements about AWS `InvokeAgent` are assertions rather than cited API
  documentation. The central omission claim is directly checkable against the
  AWS SDK, which is what makes it worth carrying.
- **Scope**: Covers the `bedrock-agent` provider config surface, session/memory
  handling, knowledge-base retrieval overrides, action-group configuration, the
  guardrail/runtime-omission caveats, the two trace planes, authentication,
  response shape, error taxonomy, caching, and troubleshooting. Does NOT cover:
  Bedrock Agents deployment/IAM setup, the AWS `InvokeAgent` request schema
  itself, raw Bedrock model invocation (a different provider page, see
  `docs-litellm-bedrock-invoke.md` / `docs-litellm-bedrock-converse.md` for the
  gateway-side mechanics), or concrete evaluation methodology like baselines and
  thresholds.
- **Last updated**: Nov 3, 2026 by `dependabot[bot]` (page footer). This is a
  living vendor page edited the same day as extraction, so `last_checked` is
  set to the extraction date; the claims below are only as current as that
  revision.

## Extracted Claims

### Claim 1: The `bedrock-agent` provider evaluates a *deployed* Bedrock Agent through AWS `InvokeAgent`, addressed as `bedrock-agent:<agentId>` and requiring an active agent alias — not a raw foundation model
- **Evidence**: Prerequisites and Basic Configuration sections. The provider id is
  `bedrock-agent:YOUR_AGENT_ID`; `agentAliasId` is marked required.
- **Confidence**: settled (documented provider contract; directly checkable)
- **Quote**: "A deployed Bedrock agent with an active alias"
- **Our assessment**: This is the load-bearing prerequisite for the rest of the
  page. Because the thing under test is a *deployed* managed agent, the eval
  provider is a thin runtime adapter, not the place where agent behavior is
  defined. That is why the next claim is a structural consequence rather than a
  bug: the deployed agent owns the guardrails, inference settings, and action
  groups.

### Claim 2: Safety- and behavior-relevant provider keys are accepted "for compatibility" but silently omitted from the runtime request — `inferenceConfig`, `guardrailConfiguration`, `promptOverrideConfiguration`, `actionGroups`, and `inputDataConfig` do not reach `InvokeAgent`
- **Evidence**: The "Full Configuration Options" note.
- **Confidence**: settled (vendor statement about its own adapter/SDK behavior;
  checkable against the AWS SDK)
- **Quote**: "Legacy inference, guardrail, prompt override, action-group, and input filtering settings shown below are accepted for compatibility but are omitted from runtime requests by the AWS SDK."
- **Our assessment**: The single most important claim on the page and the reason
  to carry a provider reference as a source. The failure is not a validation
  error or a dropped run — the config loads and the eval executes. An operator
  reading a green result has no in-band signal that the safety knobs were inert.
  For the guide, the general rule is: **eval config is not runtime config** for
  managed agent runtimes; verify the setting where the runtime reads it.

### Claim 3: Setting `guardrailConfiguration` in promptfoo does not apply a guardrail — the `InvokeAgent` API does not accept the field; the guardrail must be attached to the deployed agent
- **Evidence**: The "Guardrails" section states the limitation directly and
  tells the reader to configure guardrails on the deployed agent.
- **Confidence**: settled (documented product/AWS-API behavior)
- **Quote**: "Configure guardrails on the deployed agent. The AWS `InvokeAgent` API does not accept `guardrailConfiguration`, so setting that provider option does not apply a guardrail."
- **Our assessment**: Direct security consequence. A security eval that "sets" a
  guardrail in the provider block can run against an agent with no guardrail, or
  a different guardrail than the production alias uses, and still report green.
  The configuration is not merely unverified — it is incapable of affecting the
  request.

### Claim 4: Promptfoo cannot tell from configuration whether a guardrail ran — the only evidence is the agent trace, so a green eval does not prove guardrail enforcement
- **Evidence**: The same "Guardrails" section, immediately after the omission
  statement.
- **Confidence**: settled (vendor statement; the absence of a config-level signal
  is directly checkable)
- **Quote**: "Promptfoo cannot infer whether a guardrail ran from configuration alone; inspect the agent trace."
- **Our assessment**: This pushes the requirement from "configure the deployed
  agent" to "assert on runtime evidence". Without a trace-level assertion,
  guardrail coverage is unverified even when the deployed agent *does* have a
  guardrail attached. It is the Bedrock Agents-specific reason the `guardrails`
  assertion's fail-open behavior matters (see
  `docs-promptfoo-guardrails-assertions.md` Claim 3).

### Claim 5: Per-request inference and action-group definitions are also not accepted by `InvokeAgent` — existing keys are retained for compatibility but omitted at runtime
- **Evidence**: The "Inference Control" section repeats and narrows Claim 2 to
  `inferenceConfig`, `promptOverrideConfiguration`, and `actionGroups`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "`InvokeAgent` does not accept per-request `inferenceConfig`, `promptOverrideConfiguration`, or `actionGroups` definitions. Existing provider configuration keys are retained for compatibility, but the AWS SDK omits these fields from runtime requests."
- **Our assessment**: This is the most specific statement of the omission and
  should be the citation of record. It also creates the page's internal
  contradiction with the "Performance Optimization" section (Claim 13). For
  eval design, inference caps and prompt overrides belong to the deployed agent's
  configuration; the eval provider cannot supply them.

### Claim 6: The provider exposes two separate trace planes — Bedrock-native agent trace (`context.providerResponse.metadata.trace`, enabled by `enableTrace: true`) and promptfoo's OpenTelemetry `context.trace` — and assertions must target the right one
- **Evidence**: The "Trace Information" note.
- **Confidence**: settled (documented response shape and trace locations)
- **Quote**: "`enableTrace` exposes Amazon Bedrock's native agent trace in `context.providerResponse.metadata.trace`. That is separate from promptfoo's OpenTelemetry `context.trace`."
- **Our assessment**: A silent-no-op trap, not just a terminology issue. A
  `trajectory:*` assertion reads the OTEL plane and cannot prove a Bedrock
  action-group call happened; a JavaScript assertion over `metadata.trace`
  reads the Bedrock plane and does not benefit from promptfoo's trajectory
  normalizers. The guide should name both planes whenever it discusses agent
  trace assertions. The producer-side counterpart for OTEL is documented in
  `docs-promptfoo-evaluate-openai-agents-python.md` Claims 2-3.

### Claim 7: Action-group invocation is verified against the Bedrock-native trace with a JavaScript assertion on `actionGroupTrace.actionGroupName`, not from provider config or the OTEL trace
- **Evidence**: The "Tool Usage Verification" example and the "Trace Information"
  guidance; the page supplies a working JS assertion for the weather tool.
- **Confidence**: settled for the documented mechanism; the page offers no
  measured coverage for the assertion
- **Quote**: "Use JavaScript assertions against `metadata.trace` for Bedrock-specific action group details, and use [promptfoo tracing](/docs/tracing/) plus trajectory assertions when you want OTEL-based workflow checks."
- **Our assessment**: The concrete verification path is stronger than the
  config-driven alternative, which is inert by Claim 2. Note that the example
  still includes `actionGroups` in provider config; per the omission note that
  block is decorative, and the *assertion* is what carries the test. The guide
  should present the trace assertion, not the config block, as the tool-use
  check.

### Claim 8: Knowledge-base config is the exception to the blanket omission — associations must be on the deployed agent, but entries carrying `retrievalConfiguration` *do* override retrieval settings for the request, while legacy `knowledgeBaseId`-only entries are omitted from session overrides
- **Evidence**: The "Knowledge Base Integration" section.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Configure the knowledge-base association on the deployed agent first. Entries with `retrievalConfiguration` override retrieval settings for the request. Legacy entries containing only `knowledgeBaseId` use the deployed settings and are omitted from the request's session overrides."
- **Our assessment**: Important nuance that prevents overgeneralizing "all config
  is ignored": retrieval settings *are* live when sent in the override shape,
  but the KB association itself is not. An eval that only lists
  `knowledgeBaseId` is testing the deployed settings, not the KB it appears to
  name. This affects what a green RAG eval actually demonstrates.

### Claim 9: Knowledge-base metadata filters must use AWS `RetrievalFilter`'s `andAll`/`orAll` operator shape — flat metadata maps are rejected locally, so a filter that looks valid in a generic promptfoo config fails before reaching the agent
- **Evidence**: The "Knowledge Base Integration" section and its `andAll`
  example.
- **Confidence**: settled (documented local validation behavior)
- **Quote**: "Flat metadata maps are rejected locally. Combine conditions with `andAll` or `orAll`."
- **Our assessment**: This is the favorable failure mode — loud local rejection
  instead of a silent drop — but it means RAG config is not portable from other
  vector stores without translation. The guide should call out the AWS
  `RetrievalFilter` shape as a config-portability trap, distinct from the silent
  omissions above.

### Claim 10: Multi-turn eval is encoded by reusing a `sessionId` across test cases with `sessionState` attributes, `endSession: false` keeps the session alive, and memory type must match the deployed agent
- **Evidence**: "Session Management", "Memory Types", and the "Multi-Turn
  Conversation Testing" example.
- **Confidence**: settled (documented config and worked example)
- **Quote**: "Ensure consistent session IDs and correct memory type:"
- **Our assessment**: Multi-turn coverage is real but state is external to the
  test row. Reusing a session ID makes tests order-dependent and lets one test's
  state leak into the next; the page gives no isolation/reset contract beyond
  `endSession`. Treat session IDs as fixtures the suite must manage, and pair
  this with caching discipline (Claim 11).

### Claim 11: Responses are cached by default with no per-provider flag, so a stateful agent eval can serve a stale response unless caching is disabled globally
- **Evidence**: "Performance Optimization", item 1.
- **Confidence**: settled (documented default and disable mechanism)
- **Quote**: "Responses are cached by default — there is no per-provider flag. Disable caching with `promptfoo eval --no-cache` or `PROMPTFOO_CACHE_ENABLED=false`."
- **Our assessment**: The page frames caching as a performance win, but for an
  agent whose behavior depends on deployed-agent config, session state, or
  knowledge-base contents, a cached response can hide exactly the change the
  eval is meant to detect. The general agent-eval guidance to use `--no-cache`
  during development (`docs-promptfoo-evaluate-coding-agents.md` Claim 10)
  applies here with extra force.

### Claim 12: The provider publishes a narrow AWS error taxonomy — `ResourceNotFoundException`, `AccessDeniedException`, `ValidationException`, `ThrottlingException` — with no retry/backoff or per-error eval-failure semantics
- **Evidence**: "Error Handling" section; the four errors are listed with
  one-line causes.
- **Confidence**: settled for the taxonomy; the missing retry semantics is an
  absence in the page, not a positive claim
- **Quote**: "The provider includes specific error messages for common issues:"
- **Our assessment**: The taxonomy is useful for triage — alias/agent missing,
  IAM, invalid config, and rate limit are operationally distinct — but the page
  does not say whether promptfoo retries `ThrottlingException`, whether an
  error fails the test or is reported in the response `error` field, or how a
  batch run should back off. `ThrottlingException` is the one to watch for
  regression suites that hit a deployed agent repeatedly.

### Claim 13: The page contradicts itself on inference control — the "Performance Optimization" recipe prescribes `inferenceConfig.maximumLength` to limit response size even though "Inference Control" says the field is omitted from `InvokeAgent`
- **Evidence**: "Performance Optimization" item 3 ("Control Response Length")
  versus "Inference Control".
- **Confidence**: settled that the contradiction exists; the actual runtime
  effect is unresolved
- **Quote**: "inferenceConfig:\n  maximumLength: 1024 # Limit response size"
- **Our assessment**: A real self-contradiction in the vendor page, not a
  context-dependent variant: one section says the field is dropped at the SDK
  layer, the other tells the reader to set it for response-length control. Filed
  as contradiction #2007. We do **not** pick a verdict here; until resolved, the
  guide should not recommend `inferenceConfig.maximumLength` as a working
  Bedrock Agents control.

## Concrete Artifacts

Basic provider shape, verbatim from "Basic Configuration":

```yaml
providers:
  - id: bedrock-agent:YOUR_AGENT_ID
    config:
      agentAliasId: PROD_ALIAS_ID # Required
      region: us-east-1
```

The omission note, verbatim from "Full Configuration Options":

> Legacy inference, guardrail, prompt override, action-group, and input filtering settings shown below are accepted for compatibility but are omitted from runtime requests by the AWS SDK. Configure those settings on the deployed agent.

Knowledge-base `RetrievalFilter` shape, verbatim from "Knowledge Base Integration":

```yaml
config:
  knowledgeBaseConfigurations:
    - knowledgeBaseId: 'technical-docs-kb'
      retrievalConfiguration:
        vectorSearchConfiguration:
          numberOfResults: 10
          overrideSearchType: HYBRID
          filter:
            andAll:
              - equals:
                  key: documentType
                  value: 'manual'
              - equals:
                  key: product
                  value: 'widget-pro'
```

Action-group verification against the Bedrock-native trace, verbatim from "Tool Usage Verification":

```javascript
context.providerResponse?.metadata?.trace?.some(trace =>
  trace.actionGroupTrace?.actionGroupName === 'weather-api'
)
```

Response shape, verbatim from "Response Format":

```ts
{
  output: string;           // Agent's response text
  metadata?: {
    sessionId?: string;     // Session identifier
    memoryId?: string;      // Memory type used
    trace?: Array<any>;     // Execution traces (if enableTrace: true)
  };
  cached?: boolean;         // Whether response was cached
  error?: string;           // Error message if failed
}
```

The contradictory performance recipe, verbatim from "Performance Optimization":

```yaml
inferenceConfig:
  maximumLength: 1024 # Limit response size
```

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-guardrails-assertions.md` Claim 3 — the `guardrails` assert
    fail-opens when the provider omits the `guardrails` field. This page supplies
    the Bedrock Agents-specific reason the field can be absent: the provider
    never applies `guardrailConfiguration`, so the runtime has nothing to report
    from that config.
  - `docs-promptfoo-configuration-tools.md` Claim 4 — `strict` is *silently
    ignored* on Bedrock Converse and Google. Same family of provider-specific
    config that is accepted at load time and then dropped downstream.
- **Contradicts**:
  - **Internal to this source**: #2007 — "Inference Control" says `InvokeAgent`
    does not accept per-request `inferenceConfig`, while "Performance
    Optimization" tells readers to set `inferenceConfig.maximumLength` to limit
    response length. No verdict picked here.
- **Extends**:
  - `docs-promptfoo-evaluate-openai-agents-python.md` Claims 2-3 — the
    producer-side trace bridge and the failure mode where missing trace data
    silently degrades a trajectory eval to output-only. This page adds a second
    trace plane: Bedrock-native `metadata.trace` in addition to OTEL
    `context.trace`, so the wrong-plane assertion is an additional silent no-op.
  - `docs-promptfoo-configuration-tools.md` Claim 7 — Bedrock translation is
    lossy/asymmetric (`'none'` tool_choice omitted). This page adds another
    Bedrock-specific "the field you configured is not the field that is sent"
    case, but at the agent-runtime boundary rather than the tool-schema boundary.
  - `docs-promptfoo-evaluate-coding-agents.md` Claim 3 — provider selection is a
    runtime-boundary decision with a per-provider safety posture. Here the
    boundary is explicitly split between eval-provider config and deployed-agent
    config, and Claim 10's `--no-cache` discipline applies to the stateful
    `sessionId` eval shape.
  - `docs-litellm-bedrock-invoke.md` Claim 10 — LiteLLM's Bedrock passthrough
    has a direct-passthrough mode claiming all Bedrock endpoints including
    agents, which is a *different* route to Bedrock Agents than promptfoo's
    `InvokeAgent` provider. Useful to distinguish gateway-passthrough mechanics
    from eval-provider mechanics in the guide.
- **Novel**:
  - The Bedrock Agents (`InvokeAgent`) provider itself, and the SDK-layer silent
    omission of `guardrailConfiguration` / `inferenceConfig` /
    `promptOverrideConfiguration` / `actionGroups` / `inputDataConfig`.
  - The dual-trace-plane model (Bedrock-native agent trace vs promptfoo OTEL
    trace) and the guidance to use JavaScript assertions against
    `metadata.trace` for action-group details.
  - The knowledge-base exception: `retrievalConfiguration` entries are live
    request overrides while `knowledgeBaseId`-only entries are omitted from
    session overrides.
  - The Bedrock Agents-specific error taxonomy (including `ThrottlingException`)
    and the default-on caching behavior with no per-provider flag.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability / eval methodology)**: Add a rule that
  **eval-provider config is not runtime config** for managed agent runtimes.
  Cite Claims 2, 3, and 5: a green `bedrock-agent` eval proves only that the
  deployed agent responded; it does not prove the guardrail, inference cap, or
  action-group definitions in the eval YAML were applied. The deployment
  artifact — not the eval config — is the source of truth.
- **Chapter 06 (Security & Trust / guardrails)**: Change guardrail guidance from
  "configure the guardrail in the eval target" to "attach the guardrail to the
  deployed agent **and** assert from the runtime trace." Cite Claims 3-4 plus
  `docs-promptfoo-guardrails-assertions.md` Claim 3. A `guardrails` assertion
  with no trace evidence is a verdict reader over a possibly-absent signal.
- **Chapter 02 (Observability / tracing)**: Add the two-plane distinction from
  Claim 6: Bedrock-native `context.providerResponse.metadata.trace` for
  action-group details, promptfoo OTEL `context.trace` for trajectory/workflow
  assertions. Warn that an assertion against the wrong plane silently checks
  nothing.
- **Chapter 03 (Agent evaluation)**: Document the multi-turn pattern (Claim 10)
  and pair it with `--no-cache` (Claim 11) because state and caching both make
  results order-dependent; add the action-group check as a trace assertion
  (Claim 7), not a provider-config block; note the KB `retrievalConfiguration`
  exception (Claim 8) so RAG evals are not over-read.

## Extraction Notes

- Read the full page on 2026-11-03. No sub-pages were followed: the linked AWS
  API/guardrail pages are external reference material, and the internal links
  (`/docs/providers/aws-bedrock/`, `/docs/tracing/`) are separate provider and
  tracing surfaces already represented in the corpus. The page is moderately
  long but much of it is optional-config listing; extraction focused on the
  runtime-omission caveat, the two trace planes, the KB exception, and the
  self-contradiction.
- The page is a living vendor doc last edited 2026-11-03 (dependabot), so quotes
  are pinned to that revision.
- All `Quote` fields were copied character-for-character from the page. The
  `inferenceConfig` quote in Claim 13 is a two-line YAML fragment reproduced
  exactly, not a splice.
- The `actionGroups` block in the "Tool Usage Verification" example is retained
  in the source but is inert per the Full Configuration note; the artifact
  included above is the *assertion*, not the misleading config block.
- Candidate-file disposition (`miner-related-notes.md`, read before writing
  Cross-References):
  - `docs-litellm-batches-api.md` — dismissed: batch rate-limit accounting, no
    relation to Bedrock Agents or provider config omission.
  - `docs-promptfoo-evaluate-coding-agents.md` — cited (Extends, Claims 3/10):
    runtime-boundary framing and the `--no-cache` eval discipline.
  - `docs-promptfoo-evaluate-openai-agents-python.md` — cited (Extends,
    Claims 2-3): producer-side trace bridge and silent trace degradation.
  - `docs-promptfoo-enterprise-findings-reports.md` — dismissed: findings
    triage/export surface, unrelated.
  - `docs-promptfoo-multimodal-red-team.md` — dismissed: multimodal red-team
    channel selection, unrelated.
  - `docs-promptfoo-pi-scorer.md` — dismissed: `pi` model-graded scorer,
    unrelated.
  - `docs-langfuse-mcp-server.md` — dismissed: documentation MCP server,
    unrelated.
  - `blog-promptfoo-owasp-red-teaming.md` — dismissed: red-team process/SDLC
    framing; no Bedrock Agents provider detail.
  - `docs-promptfoo-enterprise-guardrails.md` — dismissed: promptfoo's own
    runtime guardrail HTTP contract, not Bedrock-native guardrail config; the
    enforcement surface is different even though both concern guardrails.
  - `docs-litellm-evals-api.md` — dismissed: stored-completion Evaluations API,
    unrelated.
- Additional cross-references found by searching `source-notes/`:
  `docs-promptfoo-guardrails-assertions.md`,
  `docs-promptfoo-configuration-tools.md`,
  `docs-litellm-bedrock-invoke.md`, and
  `docs-litellm-bedrock-converse.md`. The `bedrock-agent` /
  `guardrailConfiguration` search also hit
  `docs-litellm-mcp-aws-sigv4.md` (AgentCore MCP, a different service) and
  `docs-datadog-llm-observability.md` (generic span/trace framing), neither of
  which makes the runtime-omission claim.
- No existing source note makes a contrary claim about Bedrock Agents. The only
  contradiction surfaced is internal to this page and is filed as #2007.
