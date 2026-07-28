---
source_url: https://docs.litellm.ai/blog/model-cost-map-incident
source_type: failure-report
platform: blog
title: "Incident Report: Invalid model cost map on main"
author: "Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-02-10
date_extracted: 2026-07-28
last_checked: 2026-07-28
status: current
confidence_overall: emerging
issue: "#632"
---

# Failure Report: LiteLLM silent fallback to stale local model cost map after invalid JSON merged to main

> A malformed JSON entry in LiteLLM's `model_prices_and_context_window.json` merged to main caused the GitHub fetch at import time to fail, triggering a **silent fallback** to a stale local backup — users on older packages lost cost tracking for newer models with no warning logged and no diagnostic signal beyond `cost=0`.

## Source Context

- **Platform**: Vendor engineering blog (docs.litellm.ai/blog), published 2026-02-10, authored by LiteLLM's CTO Ishaan Jaffer.
- **Author credibility**: Very high — the CTO of the project owning and remediating the incident, with specific commit, file, and line-level code references to the fix.
- **Scope**: A specific, root-caused, and remediated low-severity production incident affecting cost tracking in the LiteLLM proxy. Generalizes to an anti-pattern class: silent fallback to stale local data when an external configuration fetch fails, combined with no CI validation on that config file's format.

## What Was Attempted

- **Goal**: Maintain a machine-readable model-pricing configuration file (`model_prices_and_context_window.json`) that LiteLLM fetches from GitHub `main` at import time, enabling spend calculation for LLM calls routed through the proxy.
- **Tool/approach**: LiteLLM proxy. The model cost map is a JSON file updated by contributors to add pricing for new models as they launch. LiteLLM fetches the latest version from `main` at import time; on fetch failure, it falls back to a local backup bundled with the package.
- **Setup**: Open-source LiteLLM project on GitHub; the cost map is a shared configuration file maintained by community PRs from contributors.

## What Went Wrong

- **Symptoms**: Users saw `"This model isn't mapped yet"` for newer models (e.g. `azure/gpt-5.2`). Cost tracking silently returned `cost=0` for those requests. No LLM calls were blocked — the only observable symptom was missing cost data.
- **Severity**: Low. Only cost tracking for newer models on older package versions was impacted. LLM calls and proxy routing were completely unaffected.
- **Reproducibility**: Deterministic for any installation using a package version whose bundled backup was missing the newer model entries.

### Symptom 1: Silent fallback with no warning logged

- **Evidence**: The blog explicitly states the fallback was silent before this incident.
- **Quote**: "Before this incident, the fallback was completely silent -- no warning was logged."
- **Confidence**: settled (vendor CTO, line-level fix references).

### Symptom 2: Cost tracking silently missing for newer models only

- **Evidence**: Impact description in the Summary, and the Background section explaining how cost map lookup works.
- **Quote**: "Users on older package versions lost cost tracking for newer models only (e.g. `azure/gpt-5.2`)."
- **Quote**: "Both paths return a response to the caller. When the cost map lookup fails, the only difference is `cost=0` on that request."
- **Confidence**: settled.

### Symptom 3: The failure was invisible to request-level success metrics

- **Evidence**: The cost map is explicitly out of the request path.
- **Quote**: "The model cost map is not in the request path. It is used after the LLM response comes back, inside a try/catch, to calculate spend. A missing entry never blocks a call."
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: Two coincident failures: (1) A contributor PR introduced an extra `{` bracket, producing invalid JSON. (2) The remote fetch failed with `JSONDecodeError`, triggering a silent fallback to a stale local backup. Users on older package versions had backup files missing newer models, so cost tracking silently returned `cost=0` for newer models only.
- **Our assessment**: Agree completely. This is a textbook example of a failure class where two unremarkable single points of failure (a minor typo in a PR and a missing warning log) combine to produce a silent, hard-to-diagnose symptom. The incident earned Low severity only because cost tracking is outside the request path — in a system where cost influenced routing or quota enforcement, this could have been much worse.
- **Category**: genuine-bug (in the LiteLLM project's CI and error-handling design), but representative of a generic anti-pattern: runtime-fetched configuration that silently falls back to a stale local copy on any fetch failure, with no CI validation on the upstream source.

### Root-cause detail A: No CI validation on the JSON file before merge

- **Evidence**: The fix adds CI validation, implying it did not exist before.
- **Quote**: "CI validation on `model_prices_and_context_window.json` — ✅ Done"
- **Confidence**: settled.

### Root-cause detail B: No warning logged on fallback

- **Evidence**: Explicit statement in the Root cause section.
- **Quote**: "Before this incident, the fallback was completely silent -- no warning was logged."
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: The bad commit `562f0a0` was identified and reverted within ~20 minutes.
- **Workaround**: For users who noticed the `"This model isn't mapped yet"` message and identified the root cause, reverting the bad commit restored normal cost tracking immediately. The blog does not describe any manual recovery steps users could take unilaterally (the fix was upstream).
- **Unresolved**: None stated; status is Resolved with all five remediation items marked ✅ Done.

## Extracted Lessons

### Lesson 1: Every runtime-fetched configuration file fetched at import time and cached locally needs CI validation on the upstream source — malformed input bypasses all runtime error handling

- **Evidence**: A single extra `{` bracket from a well-intentioned PR caused the entire config fetch to fail. No CI check caught it.
- **Confidence**: emerging (single incident, but the principle generalizes to any lintable config file in a shared repo).
- **Actionable as**: Add schema/parse validation in CI for any configuration file that is consumed at runtime (JSON, YAML, TOML). This is a pre-merge gate, not a runtime concern.

### Lesson 2: Silent fallback to stale local data is worse than failing loudly — a logged warning lets operators connect symptoms to causes

- **Evidence**: The entire incident's impact was prolonged by the absence of a warning log on fallback. Users saw `cost=0` but had no diagnostic signal pointing to the faulty JSON in the cost map.
- **Confidence**: emerging (single incident; the general principle is an SRE heuristic well-established outside this corpus).
- **Actionable as**: Any fallback to cached/stale data when a remote fetch fails MUST log a warning (structured, with the error and the fallback source). Treat "no warning on fallback" as a reliability bug.

### Lesson 3: Cost tracking (or any non-request-path function) that fails silently erodes observability — if the failure is invisible to request success metrics, you need separate health checks

- **Evidence**: The cost map lookup runs after the response, inside a try/catch. A missing entry never blocks a call, so the failure is invisible to p95 latency or error-rate alerts.
- **Confidence**: emerging (single incident, but a direct corollary of Lesson 2 for out-of-band processing).
- **Actionable as**: Add periodic synthetic checks or health probes for out-of-band functions (cost calculation, audit logging, post-processing) — don't rely on request success metrics to surface failures in these paths.

### Lesson 4: The lineage of a runtime-fetched config file matters — matching the "update at import time, fallback to packaged snapshot" model to the deployment model (frequent vs. pinned versions) determines blast radius

- **Evidence**: Users on older package versions with stale bundled backups were the only ones impacted. Users with the latest package (matching the backup to the active config) were immune.
- **Confidence**: emerging.
- **Actionable as**: When bundling a fallback snapshot of a remotely-fetched config, ensure it covers the same version range as the package itself, or provide a mechanism (env var, CLI flag) to pin to the local copy permanently (as `LITELLM_LOCAL_MODEL_COST_MAP=True` does).

### Lesson 5: Catalog runtime external dependencies by impact and fallback behavior — the table in this report is a template for gateway reliability engineering

- **Evidence**: The "Other dependencies on external resources" table documents five external dependencies with per-row impact and fallback characteristics.
- **Confidence**: emerging (single vendor's table, good structure but not an industry standard).
- **Actionable as**: Maintain an explicit dependency-inventory table covering: dependency name, owner, impact if unavailable, fallback (if any), and whether the fallback degrades gracefully or silently. Review it in every reliability review.

## Concrete Artifacts

**Incident metadata (verbatim from source):**
```
Date: January 27, 2026
Duration: ~20 minutes
Severity: Low
Status: Resolved
```

**Remediation table (verbatim from source):**

| # | Action | Status | Code |
|---|--------|--------|------|
| 1 | CI validation on `model_prices_and_context_window.json` | ✅ Done | `test-model-map.yaml` |
| 2 | Warning log on fallback to local backup | ✅ Done | `get_model_cost_map.py#L57-L68` |
| 3 | `GetModelCostMap` class with integrity validation helpers | ✅ Done | `get_model_cost_map.py#L24-L149` |
| 4 | Resilience test suite (bad hosted map, fallback, completion) | ✅ Done | `test_model_cost_map_resilience.py#L150-L291` |
| 5 | Test that backup model cost map always exists and contains common models | ✅ Done | `test_model_cost_map_resilience.py#L213-L228` |

**External-dependency catalog (verbatim from source):**

| Dependency | Impact if unavailable | Fallback |
|---|---|---|
| Model cost map (GitHub) | Cost tracking for newer models | Local backup (now with warning) |
| JWT public keys (IDP/SSO) | Auth fails | None |
| OIDC UserInfo (IDP/SSO) | Auth fails | None |
| HuggingFace model API | HF provider calls fail | None |
| Ollama tags (localhost) | Ollama model list stale | Static list |

**Timeline (verbatim from source):**
```
1. Malformed JSON merged to main
2. LiteLLM installations fall back to local backup on next import
3. Users report "This model isn't mapped yet" for newer models
4. Bad commit identified and reverted (~20 minutes)
```

**Configuration escape hatch (verbatim from source):**
> "Enterprises that require zero external dependencies at import time can set `LITELLM_LOCAL_MODEL_COST_MAP=True` to skip the GitHub fetch entirely."

## Cross-References

- **Corroborates failures in**:
  - `failure-litellm-wildcard-model-access-desync.md` — Involves the *same* `model_prices_and_context_window.json` file in the *same* LiteLLM subsystem (model cost map), but documents a **different** failure mode (derived-state desync after successful reload). Together the two notes form a complementary pair: one covers "fetch succeeds but derived state goes stale" and this one covers "fetch fails and fallback is silent." Both share the root insight that the cost map is a shared mutable configuration with multiple consumers, and each consumer can independently break.
  - `docs-google-sre-nalsd-classroom.md` — Discusses stale-data fallback patterns as a general reliability concern. The LiteLLM silent-fallback incident is a concrete, code-level example of the abstract principle.
  - `failure-litellm-httpx-cache-eviction.md` — Another LiteLLM failure note that cross-references the stale-data fallback pattern from `docs-google-sre-nalsd-classroom.md`; together these indicate a growing corpus of LiteLLM reliability anti-patterns.

- **Contradicts success in**: None. No existing note claims that silent fallback to stale local data is a safe or recommended pattern.

- **Known issue**: The blog mentions that the incident was brief (20 min) and low-severity precisely because cost tracking is outside the request path. This is consistent with LiteLLM's design — the cost-map lookup is deliberately soft-failing by design. The incident made an existing design trade-off visible rather than changing it.

- **Candidates dismissed** (from `miner-related-notes.md` lexical retrieval; not cited because they do not address the silent-fallback-to-stale-data anti-pattern or LLM-gateway config-fetch reliability):
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — AI agent spectrum, not about external config fetch failures.
  - `docs-google-sre-reliable-product-launches.md` — Launch coordination engineering, not relevant.
  - `blog-litellm-claude-fable-5-day-0.md` — Day-0 model support blog, unrelated to reliability.
  - `docs-langfuse-security-and-guardrails.md` — Security/guardrail patterns for LLM apps, not about config-fetch reliability.
  - `blog-pagerduty-sre-agent-triage.md` — SRE Agent triage patterns, not about silent fallback.
  - `docs-langfuse-mcp-server.md` — MCP server reference, not relevant.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — Database reliability culture, not applicable.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO fundamentals, not directly relevant.
  - `docs-google-sre-prodcast-04-06-fletcher-vibe-coding.md` — Startup reliability, tangentially related but no config-fetch or fallback coverage.
  - `docs-google-sre-prodcast-05-06-ai-safety.md` — AI safety, not relevant.

## Guide Impact

- **Chapter 02 (LLM gateway proxy patterns — cost tracking, model config management)**: Add the silent-fallback anti-pattern as a reliability consideration for cost-tracking subsystems. If the guide recommends importing model pricing from a remote source, it should also recommend: (a) CI validation on the pricing file format before merge, (b) a logged warning when fallback to local data is triggered, (c) an env-var escape hatch to pin to the local copy for air-gapped deployments, and (d) health probes for out-of-band subsystems (cost calculation, audit logging) rather than relying on request metrics.

- **Chapter 04 (CI/CD for LLM ops — configuration validation)**: Add the `test-model-map.yaml` CI pattern as a reference: a workflow that parses and validates any machine-readable configuration file (JSON schema, structural validation) on every PR before merge.

- **Chapter 04 or Chapter 05 (Resilience — external dependency fallbacks)**: Include the external-dependency catalog table structure from this report as a template. LLM gateways typically depend on multiple external resources (model cost maps, JWT endpoints, OIDC providers, model APIs, local provider registries), and each dependency should document its "impact if unavailable" and "fallback" characteristics. The LiteLLM table is a concrete starting point for such a template.

## Extraction Notes

- Source read in full via direct HTTP fetch from the blog page. The page is a compact Docusaurus blog post (~10 KB rendered text) — no paywall, no sub-pages to follow. All quoted passages copied character-for-character from the rendered HTML.
- The incident is low-severity (20 min, cost tracking only), but the *patterns* it surfaces — silent fallback, missing CI validation, invisible failure mode for out-of-band processing — are high-value for a reliability guide. Confidence is `emerging` because the root principle (warn on fallback) is well-established SRE practice, but the specific combination with LLM-gateway cost tracking as an out-of-band function is newly documented here.
- No contradiction issue filed: the complementary note (`failure-litellm-wildcard-model-access-desync.md`) documents a different failure mode in the same subsystem — the two are consistent with each other (they agree that the cost map has reliability blind spots) and disagree only on which blind spot manifested.
