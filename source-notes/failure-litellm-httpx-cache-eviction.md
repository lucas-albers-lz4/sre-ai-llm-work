---
source_url: https://docs.litellm.ai/blog/httpx-cache-eviction-incident
source_type: failure-report
platform: blog
title: "Incident Report: Cache Eviction Closes In-Use httpx Clients"
author: "Ryan Crabbe (Performance Engineer, LiteLLM), Ishaan Jaffer (CTO, LiteLLM), Krrish Dholakia (CEO, LiteLLM)"
date_published: 2026-02-27
date_extracted: 2026-07-24
last_checked: 2026-07-24
status: current
confidence_overall: settled
issue: "#461"
---

# Failure Report: LiteLLM cache eviction closed httpx clients still in active use

> A `_remove_key` override intended to prevent Redis connection-pool leaks on cache eviction indiscriminately called `aclose()`/`close()` on evicted values regardless of ownership semantics. This destroyed httpx-backed SDK clients (OpenAI, Anthropic, etc.) that were shared references still held and actively used by router/model instances, causing LLM provider requests to fail with connection errors on every cache eviction.

## Source Context

- **Platform**: Vendor engineering incident blog published on `docs.litellm.ai/blog`, by the LiteLLM engineering team (Ryan Crabbe, Ishaan Jaffer, Krrish Dholakia).
- **Author credibility**: High — vendor-authored incident report with clear root cause, code-level diffs, PR references, and remediation guidance. LiteLLM is a widely-used open-source LLM gateway/proxy. The report follows the same incident-report format as LiteLLM's other postmortems (wildcard desync, guardrail logging exposure, SQL injection CVE).
- **Scope**: A specific, fully root-caused and remediated production regression in LiteLLM's client caching layer. It generalizes to a class of bugs — a shared TTL cache that stores both exclusively-owned resources and shared references under the same eviction policy, where eviction cleanup assumes sole ownership.

## What Was Attempted

- **Goal**: Improve Redis connection-pool cleanup by closing async Redis clients when they are evicted from `LLMClientCache`, preventing connection-pool leaks.
- **Tool/approach**: LiteLLM Proxy's `LLMClientCache` (an in-memory TTL cache extending `InMemoryCache`). PR #21717 overrode `_remove_key()` to call `aclose()`/`close()` on evicted values.
- **Setup**: LiteLLM proxy deployment with client caching enabled (default: 200 entry capacity, 10-minute TTL).

## What Went Wrong

- **Symptoms**: When a cache entry expired or was evicted, `_remove_key()` called `aclose()` on the evicted value. This worked correctly for Redis clients (owned exclusively by the cache) but destroyed httpx-backed SDK clients (`AsyncOpenAI`, `AsyncAnthropic`, etc.) that were shared references still held by router/model instances and actively used for LLM API calls. "Causing requests to LLM providers to fail with connection errors."
- **Severity**: High — any proxy instance that hit the cache TTL (default 10 minutes) or capacity limit (200 entries) would have its httpx clients closed out from under it.
- **Duration**: ~6 days (Feb 21 merge of PR #21717 → Feb 27 fix in PR #22247).
- **Reproducibility**: Deterministic — any cache eviction (capacity or TTL) of a cached httpx-backed client would trigger the connection teardown.

### Symptom A: httpx transport closed on cache eviction — connection errors on active LLM requests
- **Evidence**: Blog post's Root Cause section describes the mechanism. The `_remove_key` override called `aclose()` on every evicted value; httpx clients inherit `aclose()` from the httpx library, and closing the transport while it's still in use produces connection errors.
- **Quote**: "So when the cache evicted an entry, it would call aclose() on an httpx client that was still being used for active LLM requests → closed transport → connection errors."
- **Confidence**: settled.

### Symptom B: Redis clients unaffected; only shared httpx clients hit
- **Evidence**: Blog post distinguishes between Redis clients (owned exclusively by cache) and httpx clients (shared references). Redis clients were correctly cleaned up; httpx clients were the collateral damage.
- **Quote**: "The new cleanup code called aclose()/close() on the evicted value which worked correctly for Redis clients, but destroyed httpx clients that other parts of the system still held references to and were actively using for LLM API calls."
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: The `LLMClientCache` is a mixed-ownership cache: it stores both Redis clients (owned exclusively by the cache, safe to close on eviction) and httpx-backed SDK clients (shared references still in use by router/model instances). PR #21717 overrode `_remove_key()` to call `aclose()`/`close()` on evicted values without discriminating between owned and shared references. The intent was correct for Redis clients (preventing connection pool leaks), but the override was applied unconditionally to all cached values.
- **Our assessment**: Agree. The root cause is a **shared-vs-owned resource lifecycle ambiguity** in a cache that serves dual purposes. `LLMClientCache` was originally designed to cache SDK clients for performance (avoid re-creation on every request), and later Redis client caching was added under the same abstraction. When Redis-specific cleanup was added, the code assumed the cache owned all cached values exclusively. This is a classic anti-pattern: a cache with a single eviction policy but multiple ownership semantics for its values. The lesson extends beyond LiteLLM to any cache that stores both exclusive and shared resources.
- **Category**: genuine-bug (LiteLLM code defect), but more broadly a **design-level ambiguity** where the cache's ownership contract was implicit rather than documented or enforced by type.

### Root-cause detail A: The `_remove_key` override closed all evicted values uniformly
- **Evidence**: Blog post shows the problematic code from PR #21717. The override retrieved the value from the cache, removed the key via `super()`, then attempted to call `aclose()` or `close()` on the value if the method existed — with no check on whether the value was exclusively owned by the cache.
- **Quote**: "PR #21717 overrode _remove_key() in LLMClientCache to close async clients on eviction"
- **Confidence**: settled.

### Root-cause detail B: httpx clients inherit `aclose()` — the presence of a `close` method is not evidence of cache ownership
- **Evidence**: Blog post notes that httpx-backed SDK clients have `aclose()` inherited from the httpx library, not from any cache-ownership interface. The override detected `aclose` via `getattr(value, "aclose", None)` which matched both Redis-owned and httpx-shared clients.
- **Quote**: "These clients: Have an aclose() method (inherited from httpx); Are still held by references elsewhere in the codebase (router, model instances); Were being closed without any check on whether they were still in use"
- **Confidence**: settled.

### Root-cause detail C: Mixed-ownership cache design — the fundamental tension
- **Evidence**: Blog post describes the two client types stored in `LLMClientCache` with different ownership semantics. The triage assessment calls this out as the core failure pattern: "TTL cache eviction with shared mutable references — when a cache stores objects (httpx clients) that are still referenced and actively used by other code, eviction cleanup (aclose()/close()) that assumes sole ownership destroys the live shared references, causing connection errors."
- **Quote**: "The cached values are a mix of: Redis/async Redis clients — owned exclusively by the cache, safe to close on eviction; httpx-backed SDK clients (OpenAI, Anthropic, etc.) — shared references, still in use by router/model instances"
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: Removed the `_remove_key` override entirely (PR #22247). Eviction now simply drops the reference and lets Python's GC handle cleanup. This is safe because httpx clients still referenced elsewhere stay alive, and unreferenced clients get cleaned up by GC naturally.
- **Quote**: "The eviction now simply drops the reference and lets Python's GC handle cleanup, which is safe because: httpx clients that are still referenced elsewhere stay alive; Unreferenced clients get cleaned up by GC naturally"
- **Workaround**: No explicit workaround given beyond upgrading. The bug was introduced in the merge of PR #21717 and fixed in PR #22247; upgrading past the fix version resolves it.
- **Unresolved**: None stated; status is Resolved.

### Fix detail A: Other improvements from PR #21717 were retained
- **Evidence**: Blog post explicitly states which improvements were kept after removing the `_remove_key` override.
- **Quote**: "The other improvements from PR #21717 were kept: max_connections respected for URL-based Redis configs, previously silently dropped; disconnect() now closes both sync and async Redis clients, sync client was previously leaked; Connection pool passthrough, when a pool is provided with a URL config, it's used directly instead of creating a duplicate"
- **Confidence**: settled.

### Fix detail B: E2e regression tests assert evicted clients remain functional
- **Evidence**: Two e2e tests were added in PR #22313: one for eviction by capacity, one for eviction by TTL. Both go through `get_async_httpx_client()` — the same code path the proxy uses in production — and assert the client is still functional after eviction.
- **Quote**: "These run in CI on every PR against main. If anyone modifies LLMClientCache eviction behavior, overrides _remove_key, or adds any form of client cleanup on eviction, these tests will fail regardless of the implementation approach."
- **Confidence**: settled.

## Concrete Artifacts

**Incident metadata (verbatim from source):**
```
Date: February 27, 2026
Duration: ~6 days (Feb 21 merge -> Feb 27 fix)
Severity: High
Status: Resolved
Note: This fix is available starting from LiteLLM v1.81.14.rc.2 or higher.
```

**Problematic `_remove_key` override from PR #21717 (verbatim from source):**
```python
class LLMClientCache(InMemoryCache):
    def _remove_key(self, key: str) -> None:
        value = self.cache_dict.get(key)
        super()._remove_key(key)
        if value is not None:
            close_fn = getattr(value, "aclose", None) or getattr(value, "close", None)
            if close_fn and asyncio.iscoroutinefunction(close_fn):
                try:
                    asyncio.get_running_loop().create_task(close_fn())
                except RuntimeError:
                    pass
            elif close_fn and callable(close_fn):
                try:
                    close_fn()
                except Exception:
                    pass
```

**The fix diff from PR #22247 (verbatim from source):**
```python
 class LLMClientCache(InMemoryCache):
-    def _remove_key(self, key: str) -> None:
-        """Close async clients before evicting them to prevent connection pool leaks."""
-        value = self.cache_dict.get(key)
-        super()._remove_key(key)
-        if value is not None:
-            close_fn = getattr(value, "aclose", None) or getattr(
-                value, "close", None
-            )
-            ...
     def update_cache_key_with_event_loop(self, key):
```

**Remediation table (verbatim from source):**
| Action | Status | Code |
|---|---|---|
| Remove `_remove_key` override that closes shared clients on eviction | ✅ Done | PR #22247 |
| Add e2e test: evicted client still usable (capacity) | ✅ Done | PR #22313 |
| Add e2e test: expired client still usable (TTL) | ✅ Done | PR #22313 |

## Extracted Claims

### Claim 1: A cache-eviction cleanup method that indiscriminately closes cached objects can destroy shared references still in active use
- **Evidence**: The `_remove_key` override in PR #21717 called `aclose()` on every evicted value, regardless of whether the cache held exclusive ownership or a shared reference. httpx clients (shared references) were closed while router/model instances still held them and were actively making LLM API calls.
- **Confidence**: settled
- **Quote**: "The new cleanup code called aclose()/close() on the evicted value which worked correctly for Redis clients, but destroyed httpx clients that other parts of the system still held references to and were actively using for LLM API calls."
- **Our assessment**: This is a well-documented, fully-root-caused incident from a major LLM gateway project. The root cause is clearly stated and the fix is validated by e2e regression tests. The claim is settled for the specific mechanism; the broader principle (mixed-ownership caches need ownership-aware eviction) is emerging as a design lesson.

### Claim 2: `LLMClientCache` is a mixed-ownership cache — it stores both exclusive (Redis) and shared (httpx-backed SDK) resources under the same eviction policy
- **Evidence**: The Background section documents two distinct value types stored in the cache: Redis/async Redis clients (owned exclusively by the cache) and httpx-backed SDK clients (shared references still in use by router/model instances). Both are evicted by the same `InMemoryCache.evict_cache()` → `_remove_key()` path.
- **Confidence**: settled
- **Quote**: "The cached values are a mix of: Redis/async Redis clients — owned exclusively by the cache, safe to close on eviction; httpx-backed SDK clients (OpenAI, Anthropic, etc.) — shared references, still in use by router/model instances"
- **Our assessment**: This is a factual description of the cache's design. The mixed-ownership pattern is the architectural root cause of the incident — if the cache had stored only exclusively-owned resources, the `_remove_key` override would have been correct. The design ambiguity (the cache contract does not specify ownership semantics for cached values) is the lesson.

### Claim 3: The fix was to remove the `_remove_key` override entirely rather than attempt ownership-aware selective cleanup
- **Evidence**: PR #22247 removed the `_remove_key` method body entirely. The blog post shows the diff as a deletion with no replacement — eviction now drops references and relies on Python's GC.
- **Confidence**: settled
- **Quote**: "The eviction now simply drops the reference and lets Python's GC handle cleanup, which is safe because: httpx clients that are still referenced elsewhere stay alive; Unreferenced clients get cleaned up by GC naturally"
- **Our assessment**: This is a pragmatically correct fix for this specific codebase. Adding ownership tracking to `LLMClientCache` (e.g., tagging cached values as "owned" vs "shared") would have been a larger refactor with more risk. Removing the override entirely retains the optimization benefits of the cache (client reuse) while eliminating the regression. However, the GC-only approach means Redis clients owned by the cache are also no longer explicitly closed on eviction, relying on GC + the existing `disconnect()` improvements for cleanup.

### Claim 4: E2e tests that assert an evicted client remains functional can prevent regression of this failure class
- **Evidence**: PR #22313 added two e2e tests (capacity eviction and TTL expiry) that go through `get_async_httpx_client()` and assert the client is still usable after eviction. The blog post states these tests run in CI on every PR and "will fail regardless of the implementation approach" if eviction cleanup is re-introduced.
- **Confidence**: settled
- **Quote**: "These run in CI on every PR against main. If anyone modifies LLMClientCache eviction behavior, overrides _remove_key, or adds any form of client cleanup on eviction, these tests will fail regardless of the implementation approach."
- **Our assessment**: The testing approach is sound: the tests exercise the exact code path used in production (`get_async_httpx_client()`) and assert a behavioral invariant (client still functional after eviction) rather than an implementation detail. The "regardless of the implementation approach" property is valuable — it makes the tests resilient to refactoring of the eviction logic.

### Claim 5: The bug was live for ~6 days before detection and fix, demonstrating the difficulty of detecting ownership-violation regressions in mixed-ownership caches
- **Evidence**: The incident timeline states "~6 days (Feb 21 merge -> Feb 27 fix)" — approximately 6 days between merge and fix. The blog post does not detail the detection mechanism (monitoring alert, user report, or internal discovery).
- **Confidence**: settled
- **Quote**: "Duration: ~6 days (Feb 21 merge -> Feb 27 fix)"
- **Our assessment**: A 6-day window suggests this regression was not caught by existing CI or monitoring. The most likely reason is that existing tests did not exercise the code path where an evicted httpx client is used for a subsequent LLM call (the e2e tests that catch this were added as part of the remediation, not pre-existing). This supports the triage assessment's point that shared-reference lifecycle violations are non-trivial to detect without specific behavioral tests.

## Cross-References

- **Corroborates failures in**:
  - `failure-litellm-wildcard-model-access-desync.md` — Same vendor (LiteLLM), same theme of subtle runtime state-management bugs. That note covers a config-reload path that updated the primary cache but not derived in-memory structures (known-model sets), resulting in wildcard auth failures. This note covers cache eviction cleanup that didn't account for shared ownership. Together they establish a pattern: LiteLLM's internal state management has recurring integration-boundary bugs where a change in one subsystem inadvertently breaks another via shared mutable state.
  - `failure-litellm-guardrail-logging-secret-exposure.md` — Same vendor, same theme of an integration point that operated without sufficient awareness of the data it was handling. The guardrail logging path passed internal request data to spend logs and OTEL traces (credential leak); the cache eviction path closed shared resources assuming exclusive ownership. Both are "assumed invariants violated by unexamined integration" failures.

- **Contradicts**: None. No existing source note claims that closing cached resources on eviction is safe for mixed-ownership caches, or that GC-based cleanup is insufficient.

- **Extends / thematically adjacent**:
  - `docs-google-sre-nalsd-classroom.md` — Discusses stale-data fallback patterns and the risk of assuming cached state is still valid. The LiteLLM failure extends this by showing that cache eviction can also be destructive: not just stale data but actively-destructive cleanup (closing a resource that's still in use).
  - `blog-pagerduty-production-ai-agent-gaps.md` — Describes a gateway component pattern (authn/authz, rate limits, routing) but does not address client-caching lifecycle or ownership semantics. The LiteLLM failure provides a concrete failure case for the gateway caching layer that the PagerDuty note does not cover.

- **Novel**: This is the first source note covering:
  1. **Shared-vs-owned resource lifecycle in TTL caches** — the concept that a cache can store both exclusively-owned and shared-reference resources, and that eviction cleanup must account for ownership semantics.
  2. **The `aclose()` duck-typing trap** — the `_remove_key` override used `getattr(value, "aclose", None)` to detect closeability, but httpx clients happen to have `aclose()` inherited from httpx, making the duck-type check match non-owned resources. This is a novel failure mechanism for the corpus.
  3. **E2e tests asserting post-eviction functionality** — the specific testing pattern (assert client is usable after cache eviction) as a regression-prevention technique.
  4. **GC-as-fallback for cache cleanup** — the design choice to drop references and rely on GC rather than implementing ownership-aware eviction, with the tradeoffs explicitly documented.

## Guide Impact

- **Chapter 03 (Resilience & Reliability Patterns) or Chapter 05 (LLM Ops Reliability)**: Add a design anti-pattern: "Shared TTL caches with mixed ownership semantics — when a cache stores both exclusively-owned resources (connection pools, dedicated clients) and shared references (SDK clients reused across subsystems), eviction cleanup that assumes sole ownership destroys live shared references." Include the LiteLLM `LLMClientCache` as a case study, with the specific failure mechanism (`_remove_key` override calling `aclose()` on all evicted values) and the fix (remove override, rely on GC + behavioral e2e tests).

- **Chapter 06 (Failure Patterns / Infrastructure Failure Patterns)**: Add the shared-reference lifecycle violation as a distinct failure class for LLM infrastructure — distinct from memory leaks (resources not cleaned up) and resource exhaustion (too many connections) because it is *actively-destructive cleanup* (calling `close()` on a resource that is still in use). The 6-day detection window demonstrates the stealthiness of this failure class.

- **Chapter 02 (Production Deployments — testing)**: Add the e2e testing pattern: "Test that a cached client remains functional after cache eviction (both capacity and TTL expiry). This behavioral invariant test catches any eviction cleanup that would destroy shared references, regardless of implementation approach." Reference PR #22313 as the canonical implementation in the LiteLLM codebase.

- **Chapter 01 (Incident Response)**: Use this incident's timeline (~6 days from merge to fix) and the remediation actions table (remove override + add e2e tests) as a case study template for "regression introduced by well-intentioned cleanup" incidents. The triage framework (mixed-ownership cache → indiscriminate cleanup → shared-reference destruction) is a reusable diagnosis heuristic.

## Extraction Notes

- Source read in full via direct HTTP (Docusaurus blog page, ~5 KB of extractable text). Complete article content extracted from rendered HTML — no paywall, no truncation.
- The source is a single-page incident report with code-level diffs, PR references, and a remediation table. All code blocks were extracted verbatim from the HTML (the `codeBlockLines_e6Vv` spans contained the formatted Python).
- No sub-pages were linked beyond the blog post itself. The adjacent blog posts (Day 0 support announcements) are unrelated.
- No contradiction issue filed: verified against all existing source notes. The shared-vs-owned cache lifecycle failure pattern is genuinely uncovered in the corpus. The existing LiteLLM failure reports cover orthogonal failure classes (SQL injection, guardrail logging exposure, wildcard desync). The closest thematic adjacency is the wildcard desync note (both are "subtle state-management bugs in LiteLLM") but they describe distinct mechanisms and do not contradict each other.
