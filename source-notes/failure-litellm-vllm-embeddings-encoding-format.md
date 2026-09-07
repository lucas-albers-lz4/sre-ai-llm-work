---
source_url: https://docs.litellm.ai/blog/vllm-embeddings-incident
source_type: failure-report
platform: blog
title: "Incident Report: vLLM Embeddings Broken by encoding_format Parameter"
author: "Sameer Kankute (SWE @ LiteLLM, LLM Translation), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-02-18
date_extracted: 2026-09-07
last_checked: 2026-09-07
status: current
confidence_overall: settled
issue: "#1232"
---

# Failure Report: LiteLLM vLLM embeddings broken by `encoding_format` parameter

> Commit `dbcae4a`, meant to stop the OpenAI SDK from defaulting `encoding_format` to `"float"`, changed the gateway from *omitting* the parameter to *explicitly passing `None`*. OpenAI was unaffected, but vLLM strictly validates `encoding_format` (accepts only `"float"`, `"base64"`, or complete omission) and rejected every embedding request with `"unknown variant ``, expected float or base64"` for ~3 hours. Fix `55348dd` filters `None`/empty-string values out of `optional_params` before forwarding to OpenAI-like providers — omitting the param entirely instead of sending an explicit null.

## Source Context

- **Platform**: Vendor engineering incident blog on `docs.litellm.ai/blog` (Docusaurus), tagged `incident-report`, `embeddings`, `vllm`. Published 2026-02-18. The issue (#1232) was filed against the tag-index page `https://docs.litellm.ai/blog/tags/vllm` ("One post tagged with 'vllm'"); that index resolves to this single article, which is the source mined here.
- **Author credibility**: High — co-authored by LiteLLM's SWE on LLM Translation (Sameer Kankute), CEO (Krrish Dholakia), and CTO (Ishaan Jaffer). The report includes both commit hashes (`dbcae4a` breaking change, `55348dd` fix), before/after code, the exact error string, incident metadata, and a remediation table — the same genre as LiteLLM's other incident reports (server-root-path, bedrock invoke, httpx cache eviction).
- **Scope**: A specific, fully root-caused and remediated provider-parity regression in LiteLLM's OpenAI-compatible embedding path. Generalizes to a failure class: a gateway normalizing SDK default-injection for one provider can break a stricter sibling provider through the shared forwarding path when it passes explicitly-falsy (rather than omitted) parameter values.

## What Was Attempted

- **Goal**: Prevent the OpenAI SDK from injecting its `"float"` default into the `encoding_format` param for embeddings requests, so LiteLLM controls the value (or absence) of the parameter.
- **Tool/approach**: LiteLLM proxy, commit `dbcae4a` in `litellm/main.py`. Instead of *omitting* `encoding_format` when not set, the code was changed to *explicitly set* `optional_params["encoding_format"] = None`, so the OpenAI SDK would not add its default.
- **Setup**: LiteLLM proxy routing embedding requests to multiple OpenAI-compatible backends, including vLLM-served embeddings, through the shared OpenAI-compat translation path.

## What Went Wrong

- **Symptoms**: Every vLLM embedding request failed for ~3 hours with the error `"unknown variant `None`, expected float or base64"`. vLLM's strict request validation rejects explicit `None`/empty-string values for `encoding_format`. OpenAI and other providers were unaffected (each request succeeded), and non-embedding vLLM operations were unaffected.
- **Severity**: High (for vLLM embedding users).
- **Duration**: ~3 hours (incident dated Feb 16, 2026).
- **Reproducibility**: Deterministic for any vLLM embedding request through the gateway while the breaking commit was live; invisible to OpenAI-path testing.
- **Detection**: Incident was resolved within ~3 hours; the report does not detail the detection channel.

### Symptom A: Complete failure of vLLM embedding calls via a strict-parameter rejection
- **Evidence**: The Summary bullet list scopes the blast radius explicitly.
- **Quote**: "vLLM rejects this with error: `"unknown variant \`\`, expected float or base64"`."
- **Confidence**: settled.

### Symptom B: OpenAI and other providers, plus all other vLLM operations, unaffected
- **Evidence**: The Summary's impact bullets enumerate what was and was not affected.
- **Quote**: "Other providers: No impact - OpenAI and other providers functioned normally"
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: The `encoding_format` parameter has provider-divergent semantics. The OpenAI SDK, when the param is omitted, injects a default of `"float"`. vLLM strictly validates the param and accepts only `"float"`, `"base64"`, or complete omission, rejecting `None`/empty-string values. Commit `dbcae4a` — a "well-intentioned fix for OpenAI SDK behavior" — set `encoding_format=None` instead of omitting it. Correct for OpenAI, fatal for vLLM. Both providers share the same OpenAI-compat forwarding path, so the fix broke the sibling provider it was never validated against.
- **Our assessment**: Agree completely. This is the "SDK idioms are not portable across OpenAI-compatible backends" failure archetype: a compatibility-layer normalization validated against one provider's SDK behavior silently violated a sibling provider's stricter validation contract. The root cause is semantic — `None`/omitted are *not* equivalent across these two endpoints even though both are "OpenAI-compatible."
- **Category**: genuine-bug (gateway param passthrough hygiene), representative of a generic anti-pattern — **a gateway that normalizes provider-SDK default injection must filter-to-omit rather than pass explicitly-falsy values to strict-validating providers**.

### Root-cause detail A: The breaking diff — explicit `None` instead of omission
- **Evidence**: The Root cause section shows the exact added code in `litellm/main.py`.
- **Quote**: "Omitting causes openai sdk to add default value of \"float\"" (comment in the added code)
- **Confidence**: settled.

### Root-cause detail B: Provider-divergent validation on the same parameter
- **Evidence**: The Background section contrasts OpenAI SDK vs vLLM behavior for the same `encoding_format` param.
- **Quote**: "vLLM: Strictly validates `encoding_format` - only accepts `"float"`, `"base64"`, or complete omission. Rejects `None` or empty string values."
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: Fix commit `55348dd` in `litellm/llms/openai_like/embedding/handler.py`. Before sending requests to OpenAI-like providers (including vLLM), `None` and empty-string values are filtered out of `optional_params` — the parameter is omitted entirely rather than sent as an explicit null. Valid values (`"float"`, `"base64"`) still pass through.
- **Remediation (all ✅ Done)**: (1) filter `None`/empty-string values in the OpenAI-like embedding handler; (2) unit tests for parameter filtering (None, empty string, valid values) in `test_openai_like_embedding.py`; (3) transformation tests for `hosted_vllm` embedding config in `test_hosted_vllm_embedding_transformation.py`; (4) E2E tests against an actual vLLM endpoint in `test_hosted_vllm_embedding_e2e.py`; (5) validate the JSON payload structure matches vLLM expectations — the tests assert the exact JSON sent to the endpoint.
- **Unresolved**: None stated; status is Resolved.

### Fix detail A: Filter-to-omit — the safe normalization
- **Evidence**: The fix section shows the before/after code in `litellm/llms/openai_like/embedding/handler.py`.
- **Quote**: "filtered_optional_params = {k: v for k, v in optional_params.items() if v not in (None, '')}"
- **Confidence**: settled.

### Fix detail B: The fix keeps the OpenAI defaulting fixed because LiteLLM handles the parameter upstream
- **Evidence**: The fix section enumerates the three consequences of filtering.
- **Quote**: "OpenAI SDK no longer adds defaults because liteLLM handles the parameter upstream"
- **Confidence**: settled.

## Concrete Artifacts

**Incident metadata (verbatim from source):**
```
Date: Feb 16, 2026 Duration: ~3 hours Severity: High (for vLLM embedding users) Status: Resolved
```

**Impact scoping (verbatim from source):**
```
-   **vLLM embedding calls:** Complete failure - all requests rejected
-   **Other providers:** No impact - OpenAI and other providers functioned normally
-   **Other vLLM functionality:** No impact - only embeddings were affected
```

**The breaking change — `dbcae4a` in `litellm/main.py` (verbatim from source):**
```python
# Added in dbcae4a
if encoding_format is not None:
    optional_params["encoding_format"] = encoding_format
else:
    # Omitting causes openai sdk to add default value of "float"
    optional_params["encoding_format"] = None
```

**The fix — `55348dd` in `litellm/llms/openai_like/embedding/handler.py` (verbatim from source):**
```python
# Before (broken)
data = {"model": model, "input": input, **optional_params}
# After (fixed)
filtered_optional_params = {k: v for k, v in optional_params.items() if v not in (None, '')}
data = {"model": model, "input": input, **filtered_optional_params}
```

**Remediation table (verbatim from source):**

| # | Action | Status | Code |
|---|--------|--------|------|
| 1 | Filter `None` and empty string values in OpenAI-like embedding handler | ✅ Done | [`handler.py#L108`](https://github.com/BerriAI/litellm/blob/main/litellm/llms/openai_like/embedding/handler.py#L108) |
| 2 | Unit tests for parameter filtering (None, empty string, valid values) | ✅ Done | [`test_openai_like_embedding.py`](https://github.com/BerriAI/litellm/blob/main/tests/test_litellm/llms/openai_like/embedding/test_openai_like_embedding.py) |
| 3 | Transformation tests for hosted_vllm embedding config | ✅ Done | [`test_hosted_vllm_embedding_transformation.py`](https://github.com/BerriAI/litellm/blob/main/tests/test_litellm/llms/hosted_vllm/embedding/test_hosted_vllm_embedding_transformation.py) |
| 4 | E2E tests with actual vLLM endpoint | ✅ Done | [`test_hosted_vllm_embedding_e2e.py`](https://github.com/BerriAI/litellm/blob/main/tests/test_litellm/llms/hosted_vllm/embedding/test_hosted_vllm_embedding_e2e.py) |
| 5 | Validate JSON payload structure matches vLLM expectations | ✅ Done | Tests verify exact JSON sent to endpoint |

## Extracted Claims

### Claim 1: A gateway fix that stops one provider's SDK from injecting a default can break a stricter sibling provider by passing an explicit `None` instead of omitting the parameter
- **Evidence**: Commit `dbcae4a` explicitly set `optional_params["encoding_format"] = None` when `encoding_format` was not provided, to stop the OpenAI SDK from injecting its `"float"` default. vLLM strictly validates the param and rejected every embedding request.
- **Confidence**: settled
- **Quote**: "A commit ([`dbcae4a`](https://github.com/BerriAI/litellm/commit/dbcae4aca5836770d0e9cd43abab0333c3d61ab2)) intended to fix OpenAI SDK behavior broke vLLM embeddings by explicitly passing `encoding_format=None` in API requests."
- **Our assessment**: This is the core, high-value claim. The failure is not a LiteLLM-version quirk — it is a semantic divergence between two "OpenAI-compatible" backends over how a parameter's *absence* is expressed. A compatibility-layer change validated against one provider's SDK behavior (OpenAI's default injection) silently violated a sibling provider's stricter validation contract (vLLM rejects explicit null). The lesson generalizes to any gateway that shares one forwarding path across multiple OpenAI-compatible backends.

### Claim 2: `Some providers treat omitted and explicitly-null parameter values differently` — present-but-null versus omitted is a compatibility surface, not an implementation detail
- **Evidence**: The Background section contrasts the two providers' handling of `encoding_format`. OpenAI's SDK injects `"float"` when omitted; vLLM accepts only `"float"`, `"base64"`, or complete omission and rejects `None` or empty strings.
- **Confidence**: settled
- **Quote**: "**OpenAI SDK:** If `encoding_format` is omitted, the SDK adds a default value of `"float"`" / "**vLLM:** Strictly validates `encoding_format` - only accepts `"float"`, `"base64"`, or complete omission. Rejects `None` or empty string values."
- **Our assessment**: The report's Background is the transferable knowledge: parameter semantics (especially null-vs-omitted) differ across OpenAI-compatible backends. Gateway request-transformation code must treat these semantics as a compat surface and know, per backend family, whether falsy values are meaningful, rejected, or equivalent to omission.

### Claim 3: The impact was scoped — complete failure of vLLM embeddings for ~3 hours while OpenAI and other providers, and other vLLM operations, were unaffected
- **Evidence**: The Summary's impact bullets and the incident metadata (`Duration: ~3 hours`, `Severity: High (for vLLM embedding users)`).
- **Confidence**: settled
- **Quote**: "**vLLM embedding calls:** Complete failure - all requests rejected"
- **Our assessment**: The blast-radius scoping is diagnostic gold: a regression confined to one provider subclass (vLLM) and one operation (embeddings) while the rest of the fleet stayed green. Ch02 (observability) relevance: fleet-wide error monitors would see this as a small dip (one provider's subset of traffic), not a service outage — the failure is only visible if erroring is broken down by provider/operation, or if vLLM-embedding traffic is watched as its own population.

### Claim 4: The fix is to filter `None`/empty-string values out of `optional_params` before forwarding to OpenAI-like providers — omit the parameter entirely rather than pass an explicit falsy value
- **Evidence**: Fix commit `55348dd` filters `optional_params` with `{k: v for k, v in optional_params.items() if v not in (None, '')}` in `litellm/llms/openai_like/embedding/handler.py`, preserving valid values (`"float"`, `"base64"`) and omitting falsy ones.
- **Confidence**: settled
- **Quote**: "filtered_optional_params = {k: v for k, v in optional_params.items() if v not in (None, '')}"
- **Our assessment**: Filter-to-omit is the safe normalization for this failure class: it preserves the OpenAI-side intent (no default injected) while never sending an explicitly-falsy value to a strict validator. This one-line shape is directly reusable guidance for any gateway/translation layer facing providers with differing null sensitivity.

### Claim 5: The filter is applied specifically in the OpenAI-like embedding handler, and all valid parameter values still pass through
- **Evidence**: The fix section states the filter location and its three guarantees (valid values preserved, `None`/empty filtered, OpenAI SDK no longer adds defaults).
- **Confidence**: settled
- **Quote**: "Valid values (`"float"`, `"base64"`) are preserved and sent / `None` and empty string values are filtered out (parameter omitted entirely) / OpenAI SDK no longer adds defaults because liteLLM handles the parameter upstream"
- **Our assessment**: The choice to fix in the `openai_like/embedding/handler.py` path (rather than reverting `dbcae4a` wholesale) keeps the OpenAI-side fix while neutralizing the sibling-provider breakage. The placement matters: filtering at the shared forwarding boundary protects every OpenAI-compatible backend, not just vLLM.

### Claim 6: The regression defense is tests that assert the exact JSON payload sent to the vLLM endpoint — unit, transformation, and E2E layers
- **Evidence**: The remediation table lists three test files (parameter-filtering unit tests, `hosted_vllm` transformation tests, E2E tests with an actual vLLM endpoint) plus item 5, "Tests verify exact JSON sent to endpoint."
- **Confidence**: settled
- **Quote**: "Validate JSON payload structure matches vLLM expectations - Tests verify exact JSON sent to endpoint"
- **Our assessment**: Asserting the exact wire payload per backend is the correct regression guard for provider-parity failures: a transformation change that produces a semantically-different-but-schema-valid payload is exactly what catches this class. The E2E test against a real vLLM endpoint is what makes it trustworthy (the unit/transformation tests alone would have passed `dbcae4a`). This corroborates the "assert a behavioral/concrete invariant rather than implementation detail" testing theme in the LiteLLM corpus.

### Claim 7: The incident was ~3 hours and resolved — a much faster cycle than the other LiteLLM gateway regressions in this corpus
- **Evidence**: Incident metadata: `Date: Feb 16, 2026 Duration: ~3 hours Severity: High (for vLLM embedding users) Status: Resolved`.
- **Confidence**: settled
- **Quote**: "**Date:** Feb 16, 2026 **Duration:** ~3 hours **Severity:** High (for vLLM embedding users) **Status:** Resolved"
- **Our assessment**: Contrast with the server-root-path regression (~4 days) and the httpx cache eviction (~6 days) at the same vendor. The faster cycle is notable given the fix required a code change plus three test layers — even with remediation, the detection→fix loop was hours, not days. The reason is likely that the failure was complete and unambiguous (every vLLM embedding call), unlike silent regressions. Suggests severity/clarity of failure drives time-to-detection more than the fix complexity.

## Cross-References

- **Corroborates**:
  - `failure-litellm-server-root-path-regression.md` (Claims 1, 3) — Closest analogue in the corpus. Both are gateway changes meant to fix one behavior that broke a subset of requests with a *deterministic, subset-scoped* failure: the server-root-path note documents an unrelated PR silently breaking UI routing for non-default (path-prefixed) deployments, invisible to default-path CI. This incident: a fix validated against OpenAI's SDK behavior breaking a stricter sibling provider. Common theme: a change validated against one population (default deployments / OpenAI) silently breaks a different population (path-prefixed / vLLM). Distinct mechanisms (dropped config param vs param-semantics divergence).
  - `failure-litellm-bedrock-invoke-prompt-cache.md` (Claim 1) — The Bedrock Invoke note documents a translation-layer change that kept payloads semantically equivalent but broke a provider-specific caching contract; this incident documents a translation-layer change that broke a provider-specific *validation* contract. Both are "gateway request-transformation altered a provider-specific contract the change was never validated against." Different contract violated (prefix cache vs strict request validation), same failure shape.
  - `blog-litellm-gemini-3-flash-day-0.md` (Claims 2, 6) and `blog-litellm-gemini-3-5-flash-day-0.md` — These day-0 notes document LiteLLM's cross-provider parameter translation (OpenAI `reasoning_effort` → Gemini `thinkingLevel`) as a feature. This incident is the failure counterpart: the same translation layer, on a different parameter/backend pair, broke because param semantics diverge across providers. The day-0 notes show the translation surface is *inherently provider-divergent*; this note shows the consequence when a divergence is missed.
  - `blog-litellm-fastapi-middleware-performance.md` — Same FastAPI proxy request path as a recurring fragility point; this incident adds the param-translation handler (embeddings) as another surface in the same path where provider divergence bites. Compatible direction, no contradiction.

- **Contradicts**: None. Verified against `CONTRADICTIONS.md` (no open `C-NNN` entries) and all corpus notes. No existing note claims `encoding_format`/vLLM embedding params are provider-uniform, or that explicitly-null optional params are safe to forward to OpenAI-compatible backends. The Gemini day-0 notes cover *different* parameters (`reasoning_effort`, `thinkingLevel`), not embeddings. No contradiction issue filed.

- **Extends**:
  - `failure-litellm-server-root-path-regression.md` (Claim 5, Guide Impact) — That note's remedy prescribed PR-gated CI that boots the *non-default* configuration. This incident extends the pattern with the provider-dimension analog: test the *non-default provider* (vLLM) with exact-payload assertions, because default-path (OpenAI-SDK) testing passed this fix. The "coverage gap is invisible to the default population" lesson now spans deployment-config (root-path) and provider-compat (vLLM) dimensions.
  - `blog-litellm-gemini-3-flash-day-0.md` (Guide Impact) — Its guide suggestion (Ch05 cross-provider parameter mapping) is the positive half; this incident supplies the failure-mode half: parameter translation must account for null-vs-omitted semantics per backend family.

- **Novel**: First source note in the corpus covering:
  1. **The `encoding_format` / vLLM embeddings parameter-translation failure** — no existing note covers vLLM, embeddings, `encoding_format`, or OpenAI-compatible param passthrough to a strict-validating backend.
  2. **The "SDK idioms are not portable across OpenAI-compatible backends" failure archetype** — a gateway normalization (filtering/omitting a param to control one provider's SDK defaulting) that breaks a sibling endpoint with stricter validation on the *same* parameter.
  3. **Present-but-null vs omitted as a compatibility surface** — the specific semantic that `None` and omission are *not* equivalent across providers, captured as an explicit rule ("filter-to-omit is the safe normalization").
  4. **Per-backend exact-payload tests as the provider-parity regression guard** — unit + transformation + E2E layers asserting the exact JSON sent to the vLLM endpoint.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — gateway/provider parity)**: Add the failure pattern **"a gateway fix validated against one provider's SDK behavior can break a stricter sibling provider through the shared forwarding path."** Use this incident as the case study: `dbcae4a` set `encoding_format=None` to stop the OpenAI SDK defaulting to `"float"`; vLLM's strict validation rejected every embedding request for ~3h (`unknown variant \`\`, expected float or base64`) while OpenAI stayed green. Specific guidance: (a) when normalizing provider-SDK default injection, **filter-to-omit** rather than pass explicitly-falsy values — omit the param entirely (`filtered_optional_params = {k: v for k, v in optional_params.items() if v not in (None, '')}`); (b) treat present-but-null vs omitted as a per-backend compat surface, since semantics differ across "OpenAI-compatible" providers.

- **Chapter 05 or Chapter 02 (Testing / CI for LLM ops)**: Add the provider-parity regression-defense pattern from the remediation: assert the **exact JSON payload** sent to each backend (unit tests for parameter filtering, transformation tests per provider class, and E2E tests against a real vLLM endpoint). Note that transformation/unit tests alone would have passed the breaking commit — the E2E payload assertion against the actual backend is what validates the wire contract.

- **Chapter 02 (Observability)**: Use the impact scoping as a diagnostic example: a failure isolated to one provider subclass (vLLM) and one operation (embeddings) is nearly invisible to fleet-wide error monitors — break error rates down by provider/operation, or track provider-subsets as their own populations, or this class of incident reads as background noise.

- **Chapter 01 (Incident Response)**: Optional light usage — contrast the ~3h detection→fix cycle here (complete, unambiguous failure) with the ~4-6 day cycles of the server-root-path and httpx cache-eviction incidents (silent or confounded regressions). Failure clarity drives time-to-detection; silent regressions need proactive monitors, not just fast incident response.

## Extraction Notes

- The issue (#1232) was filed against the Docusaurus tag-index page `https://docs.litellm.ai/blog/tags/vllm` ("One post tagged with 'vllm'"). That index is a navigation page with no extractable content; per the Prospector triage, the mined source is its single underlying article — `https://docs.litellm.ai/blog/vllm-embeddings-incident` (2026-02-18) — which was fetched in full via WebFetch and read deeply. No paywall, no truncation.
- All quotes copied character-for-character from the rendered page text, including the error string `"unknown variant \`\`, expected float or base64"` and the before/after code blocks. The remediation table is reproduced as rendered. Two formatting normalizations were applied to code artifacts, matching the convention in sibling LiteLLM notes: the `dbca...e4a` breaking-change snippet is rendered with the inline `# Added in dbcae4a` comment as-is (the source renders it with no spacing before the code), and the error string's inner backticks/UNICODE escape are preserved.
- Linked files (`handler.py#L108`, the three test files) are cited as identifiers only, not fetched — they are referenced in this note as the report describes them (remediation table, `✅ Done` status). Verbatim claims about their contents, beyond what the source page itself states, were not made.
- `confidence_overall: settled` — vendor-authored postmortem with both commit hashes, before/after code, exact error string, documented impact scoping, incident metadata, and a five-item all-Done remediation table.
- No contradiction issue filed: verified against CONTRADICTIONS.md and all existing source notes; nothing in the corpus claims `encoding_format`/vLLM embedding-param semantics are provider-uniform, and no existing note covers this parameter or backend.
- Cross-reference candidates from `miner-related-notes.md` not cited above, each dismissed in one line (lexical retrieval returned no vLLM / embeddings / param-translation notes):
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — AI-agent spectrum/guardrails, unrelated to provider-param semantics.
  - `blog-litellm-auto-router-v2.md` — Auto Router v2 routing collapse, unrelated to embedding param passthrough.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server, unrelated.
  - `docs-google-sre-eliminating-toil.md` — SRE toil definition, unrelated.
  - `docs-langfuse-security-and-guardrails.md` — Security/guardrail stacks, unrelated.
  - `blog-litellm-save-claude-code-costs.md` — LiteLLM cost-cutting features, unrelated to param-translation failures.
  - `blog-litellm-valkey-semantic-caching.md` — Semantic caching on Valkey, unrelated.
  - `docs-google-sre-data-processing-pipelines.md` — Pipeline SLOs, unrelated.
  - `docs-google-sre-reliable-product-launches.md` — Launch checklists, unrelated.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO fundamentals, unrelated.