---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-openai-assistants
source_type: docs
title: "Promptfoo Guide: Evaluating OpenAI Assistants — Provider Sunset and API-Base-URL Retargeting"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-23
date_extracted: 2026-10-24
last_checked: 2026-10-24
status: current
confidence_overall: emerging
issue: "#1708"
---

# Promptfoo Guide: Evaluating OpenAI Assistants

> The native OpenAI Assistants API shut down on 2026-08-26. The page preserves a legacy evaluation workflow for Assistants-compatible endpoints, and its SRE-relevant substance is the provider-lifecycle risk (pinned `openai:assistant:` configs becoming invalid on vendor schedule) and the documented escape hatch for retargeting to compatible gateways via `OPENAI_API_BASE_URL` or per-provider `config.apiBaseUrl`.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "How to evaluate OpenAI Assistants" under Evals → Guides → Integrations). Single guide page, auto-discovered from the registered `promptfoo-docs` site-crawl seed.
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor. First-party documentation of a legacy integration path; the deprecation notice and retargeting instructions are authoritative for the documented workflow.
- **Scope**: Covers (1) creating/selecting an assistant on an Assistants-compatible endpoint, (2) basic `promptfooconfig.yaml` with `prompts`/`providers`/`tests` referencing `openai:assistant:<asst_id>`, (3) running `npx promptfoo eval`, (4) comparing multiple assistants or different versions of the same assistant via provider `config` overrides, and (5) adding assertions. **Explicitly deprecated** — native OpenAI Assistants API shut down 2026-08-26; examples only work against Assistants-compatible endpoints. Does NOT cover CI gating, thresholds-as-gates, cost/latency, thread/run lifecycle detail, or production monitoring.
- **Caveat**: This is legacy/migration material, not current recommended practice. Assertions (`contains`, `similar` with thresholds) are already covered by existing notes — not re-extracted here per Prospector guidance.

## Extracted Claims

### Claim 1: The native OpenAI Assistants API shut down on 2026-08-26, and the legacy examples no longer work against OpenAI's native API — an eval suite pinned to `openai:assistant:<asst_id>` is invalidated by vendor sunset on the vendor's schedule, not the operator's
- **Evidence**: The page's warning banner at the top stating the shutdown date and that legacy examples no longer work against OpenAI's native API.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "The native OpenAI Assistants API shut down on August 26, 2026. Use the Responses API for new integrations and follow OpenAI's [Assistants migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses#assistants-api)."
- **Quote**: "The legacy examples below require an endpoint that still implements the Assistants API. Set `OPENAI_API_BASE_URL` to your compatible endpoint, or set `config.apiBaseUrl` for each provider. These examples no longer work against OpenAI's native API."
- **Our assessment**: A concrete instance of provider lifecycle risk for eval harnesses. A stored eval config referencing `openai:assistant:asst_...` becomes a broken dependency due to a vendor control-plane change outside the operator's release cycle. This is durable operational risk for Ch05 — eval suites are dependencies on vendor API surfaces, and stateful assistant objects are especially brittle to deprecation.

### Claim 2: The documented escape hatch is to retarget to an Assistants-compatible endpoint via `OPENAI_API_BASE_URL` (global) or per-provider `config.apiBaseUrl`, while still using the same `openai:assistant:<id>` provider shape and allowing per-provider config overrides of `modelName`, `instructions`, and `tools` (`code_interpreter`, `file_search`)
- **Evidence**: The warning banner's instructions for retargeting, plus the "Comparing different versions of the same assistant" section showing provider-level `config` with `modelName`, `instructions`, and `tools`.
- **Confidence**: settled (documented configuration pattern)
- **Quote**: "Set `OPENAI_API_BASE_URL` to your compatible endpoint, or set `config.apiBaseUrl` for each provider."
- **Quote**: "To override the saved configuration of an assistant, use the provider's `config` section. For example:"
- **Our assessment**: The retargeting pattern is the SRE-relevant escape hatch — keep the eval config shape intact and redirect traffic to a compatible gateway instead of rewriting tests. The ability to override `modelName`, `instructions`, and `tools` from the eval config (A/B-ing stored vs overridden server-side config) is a config-surface detail worth recording, explicitly flagged as applying to a deprecated integration path.

## Concrete Artifacts

Copied from https://www.promptfoo.dev/docs/guides/evaluate-openai-assistants. Treat as legacy/migration examples only.

### Basic config referencing an assistant (verbatim)
```yaml
prompts:
  - 'Help me out with this: {{message}}'
providers:
  - openai:assistant:asst_fEhNN3MClMamLfKLkIaoIpgB
tests:
  - vars:
      message: write a tweet about bananas
  - vars:
      message: what is the sum of 38.293 and the square root of 30300300
  - vars:
      message: reverse the string "all dogs go to heaven"
```

### Per-provider config override (verbatim)
```yaml
providers:
  - id: openai:assistant:asst_fEhNN3MClMamLfKLkIaoIpgB
    config:
      modelName: gpt-4.1
      instructions: 'Enter a replacement for system-level instructions here'
      tools:
        - type: code_interpreter
        - type: file_search
```

### Comparing original vs modified assistant (verbatim)
```yaml
providers:
  # Original
  - id: openai:assistant:asst_fEhNN3MClMamLfKLkIaoIpgB
  # Modified
  - id: openai:assistant:asst_fEhNN3MClMamLfKLkIaoIpgB
    config:
      modelName: gpt-4.1
      instructions: 'Always talk like a pirate'
```

## Cross-References

### Overlap with existing notes (as guided by Prospector)
- **Corroborates / relates to**: `docs-litellm-messages-to-responses-mapping.md` — covers the Responses API migration surface; this page's deprecation points in the same direction (move off Assistants to Responses).
- **Already covered elsewhere (not re-extracted)**: `docs-promptfoo-assertions-metrics.md`, `docs-promptfoo-deterministic-metrics.md` — own `contains`/`similar` assertion catalog; `docs-promptfoo-similar-assertion.md` details `similar` semantics. The page's assertion examples are not extracted here.
- **Related config patterns**: `docs-promptfoo-configuration-guide.md` owns general provider/config basics; sibling evaluate-* pages cover other agent frameworks.

**Novel**: First corpus coverage of the OpenAI Assistants API sunset impact on promptfoo eval configs and the `OPENAI_API_BASE_URL` / per-provider `config.apiBaseUrl` retargeting escape hatch for `openai:assistant:` providers.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add provider lifecycle risk to the "eval dependencies" discussion — eval suites pinned to vendor-specific stateful APIs (like `openai:assistant:`) can be invalidated by vendor deprecation/sunset on the vendor's schedule. Record the retargeting pattern (`OPENAI_API_BASE_URL` or `config.apiBaseUrl`) as a migration escape hatch when a compatible endpoint exists, but treat it as temporary/legacy. Explicitly call out that deprecation dates must be tracked for pinned provider integrations.

## Extraction Notes

- Source read in full via WebFetch (https://www.promptfoo.dev/docs/guides/evaluate-openai-assistants). Page states "Last updated on Oct 23, 2026" in footer.
- Followed Prospector guidance strictly: only extracted Claims 1 and 2 (provider sunset/lifecycle risk and escape hatch/retargeting). Did not re-extract assertion catalog (`contains`, `similar`/threshold) as it is already covered by existing notes.
- Treated entire page as legacy/migration material (native Assistants API shut down 2026-08-26). Carried explicit deprecation caveats on claims.
- `confidence_overall` = `emerging`: first-party vendor documentation of a deprecated integration path with clear statements about sunset and retargeting; operational impact is clear but the page itself is thin and explicitly marks the examples as non-functional against the native API.
- `registry/sources.json` and `registry/claims-index.json` were intentionally not edited.
