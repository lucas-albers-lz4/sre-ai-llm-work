---
source_url: https://docs.litellm.ai/blog/anthropic-wildcard-model-access-incident
source_type: failure-report
platform: blog
title: "Incident Report: Wildcard Blocking New Models After Cost Map Reload"
author: "Sameer Kankute (SWE @ LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-02-23
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#133"
---

# Failure Report: LiteLLM wildcard rejected new models after a cost-map reload left the in-memory known-models set stale

> A runtime config reload updated `litellm.model_cost` but never re-ran `add_known_models()`, so the in-memory provider set (`litellm.anthropic_models`) went stale and the `anthropic/*` wildcard returned 401 for every newly-added model for ~3 hours.

## Source Context

- **Platform**: Vendor engineering incident blog (`docs.litellm.ai/blog`), published 2026-02-23.
- **Author credibility**: Practitioner-level, and high: the report is co-authored by LiteLLM's own SWE (Sameer Kankute), CEO (Krrish Dholakia), and CTO (Ishaan Jaffer). It includes before/after code patches with line-level GitHub references (`proxy_server.py#L4393`, `#L11904`, `__init__.py#L617`) and two regression tests.
- **Community response**: None captured on-page (single-vendor self-posted incident report).
- **Scope**: A specific, fully root-caused and remediated production incident in LiteLLM's proxy. It generalizes to a class of bugs — derived in-memory state that must be recomputed atomically with a primary cache on every reload path.

## What Was Attempted

- **Goal**: Roll out a newly-released Anthropic model (`claude-sonnet-4-6`) to LiteLLM proxy users whose keys/teams were authorized via the provider wildcard `models=['anthropic/*']`, without restarting the proxy.
- **Tool/approach**: LiteLLM proxy. The model was added to the shared cost map (`model_prices_and_context_window.json`), then a cost-map reload was triggered (intended to pick up the new model live).
- **Setup**: LiteLLM proxy with provider-level wildcard access rules; cost map auto-reloaded every 10 s (`_check_and_reload_model_cost_map`) and manually via the `/reload/model_cost_map` admin endpoint.

## What Went Wrong

- **Symptoms**: Every request to the new model returned a 401 with the message: `key not allowed to access model. This key can only access models=['anthropic/*']. Tried to access claude-sonnet-4-6.` The reload reported success and the cost map clearly contained the new model, yet access was denied.
- **Severity**: High for any user relying on provider wildcard access rules (new models blocked entirely); bounded — only models missing from the stale in-memory set were impacted.
- **Reproducibility**: Consistent and deterministic for any newly-added model after a reload; pre-existing models were unaffected.

### Symptom 1: New models blocked with 401 while the cost map already knew them
- **Evidence**: The report's summary states the reload succeeded at the cost-map layer but not at the resolver layer.
- **Quote**: "When a new Anthropic model (e.g. claude-sonnet-4-6) was added to the LiteLLM model cost map and a cost map reload was triggered, requests to the new model were rejected with: key not allowed to access model. This key can only access models=['anthropic/*']. Tried to access claude-sonnet-4-6."
- **Confidence**: settled (verbatim incident summary; reproduced and fixed by vendor).

### Symptom 2: Only newly-added models were hit; existing models fine
- **Evidence**: Scope boundaries stated explicitly in the Summary.
- **Quote**: "LLM calls: All requests to newly-added Anthropic models were blocked with a 401. Existing models: Unaffected — only models missing from the stale provider set were impacted."
- **Confidence**: settled.

### Symptom 3: Every reload re-broke access (root cause not addressed by reloading)
- **Evidence**: Timeline shows the admin reloaded the cost map again mid-incident with the same result.
- **Quote**: "Admin reloads cost map again — same result (root cause not addressed)"
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: `add_known_models()` is invoked **once at import time** to populate `litellm.anthropic_models` (and sibling sets). Both reload paths updated `litellm.model_cost` with the fresh map but never re-invoked `add_known_models()`, so the in-memory provider set never learned about the new model. The wildcard resolver (`get_llm_provider()` → `_model_custom_llm_provider_matches_wildcard_pattern`) then failed to map `claude-sonnet-4-6` → `"anthropic"`, so the wildcard match evaluated to `False` and the request was rejected.
- **Our assessment**: Agree. The mechanism is precisely stated and the fix + regression tests confirm it. The deeper lesson is a classic derived-state-vs-primary-cache desync: two in-memory structures seeded from the same source (`model_cost`) were updated non-atomically. This is the same shape as cache-coherence bugs elsewhere; here it's made worse by the module-level global being the iteration target, so a later reload silently iterated stale data.
- **Category**: genuine-bug (in LiteLLM), but it is a representative instance of a generic anti-pattern — partial config reload that updates one derived structure but not all of them.

### Root-cause detail A: The two reload paths both skipped `add_known_models()`
- **Evidence**: Author enumerates both reload entry points; code before the fix shown with the missing call annotated.
- **Quote**: "add_known_models() is called once at module import time. Both reload paths in proxy_server.py updated litellm.model_cost with the fresh map but never called add_known_models() again:"
- **Quote**: "The gap existed in two places: _check_and_reload_model_cost_map — the periodic automatic reload (every 10 s); The /reload/model_cost_map admin endpoint — the manual reload"
- **Confidence**: settled.

### Root-cause detail B: The resolver relies on an import-time-populated Python set
- **Evidence**: Background section explains the data flow from model name to provider.
- **Quote**: "litellm.anthropic_models is a Python set populated at import time by add_known_models(). It is the source get_llm_provider() consults to map a bare model name like claude-sonnet-4-6 to the provider string \"anthropic\"."
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: Not a switch — a code fix. After every reload, `add_known_models(model_cost_map=new_model_cost_map)` is now called with the freshly fetched map passed explicitly, and `add_known_models()` was changed to accept an optional explicit map so callers can never accidentally iterate the stale module-level global.
- **Workaround**: Restarting the proxy would have repopulated the sets at import time, but the fix removes the need for restarts entirely.
- **Unresolved**: None stated; status is Resolved.

### Fix detail A: Explicit map passed after reload (both paths)
- **Evidence**: After-fix code snippet.
- **Quote**: "After each reload, add_known_models() is called with the freshly fetched map passed explicitly. Passing the map directly (rather than relying on the module-level reference) removes any ambiguity about which dict is iterated"
- **Confidence**: settled.

### Fix detail B: `add_known_models()` signature hardened
- **Evidence**: Before/after function signatures shown in the Fix section.
- **Quote**: "def add_known_models(model_cost_map: Optional[Dict] = None): _map = model_cost_map if model_cost_map is not None else model_cost for key, value in _map.items(): # always iterates the map you just fetched"
- **Confidence**: settled.

### Fix outcome
- **Evidence**: Closing statement of the Fix section.
- **Quote**: "After the fix, the provider sets (anthropic_models, open_ai_chat_completion_models, etc.) are always consistent with litellm.model_cost immediately after every reload. New models become accessible via wildcard rules without any proxy restart."
- **Confidence**: settled.

## Concrete Artifacts

All artifacts verbatim from the source.

**Before the fix — both reload paths (periodic + admin endpoint):**
```
new_model_cost_map = get_model_cost_map(url=model_cost_map_url)
litellm.model_cost = new_model_cost_map            # ✅ cost map updated
_invalidate_model_cost_lowercase_map()               # ✅ cache cleared
# ❌ add_known_models() never called
#    → litellm.anthropic_models still has the old set
#    → new model not in the set
#    → get_llm_provider() raises for the new model
#    → wildcard match returns False
#    → 401 for every request to the new model
```

**After the fix — both reload paths now do:**
```
new_model_cost_map = get_model_cost_map(url=model_cost_map_url)
litellm.model_cost = new_model_cost_map
_invalidate_model_cost_lowercase_map()
litellm.add_known_models(model_cost_map=new_model_cost_map)      # ✅ sets repopulated
```

**`add_known_models()` before (reads the ambiguous module global):**
```
def add_known_models():
    for key, value in model_cost.items():       # reads module global — ambiguous after reload
        ...
```

**`add_known_models()` after (caller supplies the map it just fetched):**
```
def add_known_models(model_cost_map: Optional[Dict] = None):
    _map = model_cost_map if model_cost_map is not None else model_cost
    for key, value in _map.items():             # always iterates the map you just fetched
        ...
```

**Remediation table (verbatim):**
```
# Action Status Code
1 Call add_known_models(model_cost_map=...) in the periodic reload path ✅ Done  proxy_server.py#L4393
2 Call add_known_models(model_cost_map=...) in the /reload/model_cost_map endpoint ✅ Done  proxy_server.py#L11904
3 Update add_known_models() to accept an explicit map parameter ✅ Done  __init__.py#L617
4 Regression test: add_known_models(model_cost_map=...) populates provider sets ✅ Done  test_auth_checks.py
5 Regression test: anthropic/* wildcard grants/denies access correctly after reload ✅ Done  test_auth_checks.py
```

**Incident metadata (verbatim):**
```
Date: Feb 23, 2026
Duration: ~3 hours
Severity: High (for users with provider wildcard access rules)
Status: Resolved
```

## Extracted Lessons

### Lesson 1: Every config-reload path must recompute ALL derived structures, not just the primary cache
- **Evidence**: The bug was that `litellm.model_cost` (primary) was refreshed but `litellm.anthropic_models` (derived set) was not, across both reload paths.
- **Quote**: "The reload updated litellm.model_cost correctly but never re-ran add_known_models(), so litellm.anthropic_models (the in-memory set used by the wildcard resolver) remained stale."
- **Confidence**: emerging (single well-documented incident, but the principle is a general SRE heuristic).
- **Actionable as**: When adding a runtime reload/refresh for any cache, audit every structure seeded from that cache and force-recompute them in the same reload path; add a test that reloads and then exercises each dependent code path.

### Lesson 2: Prefer passing freshly-fetched data explicitly rather than relying on a module-level global as the iteration target
- **Evidence**: The fix made `add_known_models()` accept `model_cost_map=` and callers pass `new_model_cost_map`.
- **Quote**: "Passing the map directly (rather than relying on the module-level reference) removes any ambiguity about which dict is iterated"
- **Confidence**: emerging.
- **Actionable as**: In reload/hot-config code, thread the new value through explicitly instead of mutating a global and hoping downstream readers see it; this removes whole classes of stale-global bugs.

### Lesson 3: This is a provider-agnostic bug class — any provider wildcard (`openai/*`, `gemini/*`, …) is vulnerable to the same desync
- **Evidence**: The report states the same pattern applies to every provider's known-models set.
- **Quote**: "Other providers: Same bug class existed for any provider wildcard (e.g. openai/*, gemini/*)."
- **Confidence**: emerging.
- **Actionable as**: For any LLM gateway/proxy, treat "wildcard resolves to newly-added model after reload" as a regressed state until proven otherwise; cover all provider wildcards in reload regression tests, not just one.

### Lesson 4: A successful reload that updates the primary cache can still silently break dependent access control — reload success ≠ end-to-end health
- **Evidence**: Cost map updated and reload "succeeds," yet wildcard auth returned 401; the admin reloaded again to no effect.
- **Quote**: "Admin reloads cost map again — same result (root cause not addressed)"
- **Confidence**: emerging.
- **Actionable as**: Add post-reload health checks that exercise a wildcard-routed request to a newly-added model, not just "cost map version bumped" metrics.

## Cross-References

- **Corroborates**: None in corpus. No existing source note documents an LLM-proxy runtime-reload / in-memory derived-state desync.
- **Contradicts**: None. (No contradiction issue filed — verified against all 17 existing notes; the specific failure terms `litellm`, `wildcard`, `add_known_models`, `model_cost` match zero notes, and the broader `proxy`/`gateway`/`stale` hits are about SLO "normal" decay and the PagerDuty AI-agent *gateway* authn/authz component, i.e. conceptual cousins only, not the same failure class.)
- **Extends / thematically adjacent**:
  - `blog-pagerduty-production-ai-agent-gaps.md` describes a "Gateway" component responsible for "authentication, authorization, rate limits, policies, routing" — a conceptual cousin of the LiteLLM proxy, but that note is about AI-agent architecture gaps, not LLM-proxy config-reload bugs. Useful as a pointer that gateway auth is a recurring reliability surface, not as prior coverage of this failure.
  - `docs-google-sre-prodcast-01-04-rethinking-slos.md` (Claim 7: "SLOs are a point-in-time approximation of 'normal' ... they go stale as the system changes") and `docs-google-sre-nalsd-classroom.md` (stale-data fallback) articulate the generic "derived state goes stale" principle — conceptually the same root shape, but neither addresses LLM-proxy reload paths.
- **Novel**: This is the first source note covering (a) LiteLLM, (b) LLM-proxy provider-wildcard access control, and (c) the partial-reload-desync bug class. High novelty, per triage.

## Guide Impact

- **Chapter 02 (LLM gateway auth / access control) or Ch05 (LLM Ops reliability)**: Add a concrete anti-pattern + detection note: "A config/cost-map reload that updates the primary cache but not all derived in-memory structures (provider wildcards, known-model sets) silently breaks access control — a successful reload is not evidence of end-to-end health." Include the explicit-parameter fix pattern and the post-reload wildcard-request health check.
- **Chapter 01 (Incident Response) / Ch04 (Oncall & Toil)**: The ~3-hour lifecycle (reload re-attempted with no effect until root cause found) is a textbook case for "reloading/restarting the same way won't fix a logic gap" — useful as an incident-anatomy example showing how a recurring reload masked rather than fixed the cause.
- **General testing heuristic (new chapter material or Ch05)**: "Every config reload path must recompute ALL structures derived from that config." This generalizes the single incident into a reusable engineering rule for any hot-config system.

## Extraction Notes

- Source read in full (Docusaurus page, ~5 KB of extracted text; complete — nothing paywalled or truncated). Fetched via direct HTTP (WebFetch returned empty for this host) and HTML-to-text extraction; all quoted passages copied character-for-character from the rendered page.
- The report is a vendor-authored, fully-remediated incident with line-level code references and two regression tests, so quotes and artifacts are high-fidelity. Confidence is `emerging` rather than `settled` only because it is a single vendor's single incident; the *generalized* lesson is corroborated by generic SRE cache-coherence / stale-derived-state principles already present in the corpus (see Cross-References), though no other note states it for LLM proxies specifically.
- No contradiction issue filed: verified against all 17 existing source notes; the specific failure pattern is genuinely uncovered.
