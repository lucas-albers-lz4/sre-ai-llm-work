---
source_url: https://docs.litellm.ai/blog/responses-api-encrypted-content-incident
source_type: failure-report
platform: blog
title: "Incident Report: Encrypted Content Failures in Multi-Region Responses API Load Balancing"
author: "Sameer Kankute (SWE @ LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-02-24
date_extracted: 2026-07-30
last_checked: 2026-07-30
status: current
confidence_overall: settled
issue: "#667"
---

# Failure Report: Encrypted Content Failures in Multi-Region Responses API Load Balancing

> When load balancing OpenAI's Responses API across deployments with different API keys (different Azure regions or OpenAI organizations), follow-up requests containing encrypted content items (like `rs_...` reasoning items) failed with `invalid_encrypted_content` because the items are cryptographically tied to the creating organization's key. LiteLLM introduced `encrypted_content_affinity` — a no-cache, on-the-fly routing check that embeds the originating `model_id` into item IDs and encrypted content itself — as a surgical alternative to broader `deployment_affinity` or `session_affinity` mechanisms.

## Source Context

- **Platform**: Vendor engineering incident blog (`docs.litellm.ai/blog`), published 2026-02-24, with a follow-up update dated Mar 3, 2026. Tags: `incident-report`, `proxy`, `responses-api`, `load-balancing`.
- **Author credibility**: Very high — the report is co-authored by LiteLLM's own SWE (Sameer Kankute), CEO (Krrish Dholakia), and CTO (Ishaan Jaffer). It includes before/after code patches with GitHub file references (responses/utils.py, encrypted_content_affinity_check.py, router.py, responses/streaming_iterator.py), a remediation table with status per action item, and configuration migration guidance.
- **Community response**: None captured on-page (single-vendor self-posted incident report). The follow-up fix from Mar 3 was prompted by user reports that streaming clients (like Codex) still encountered the error after the initial fix.
- **Scope**: A specific, fully root-caused and remediated production incident in LiteLLM's Responses API routing. The failure mode and its resolution pattern generalize to any LLM gateway doing multi-region/multi-key load balancing of encrypted/cryptographically-bound content across organizational boundaries.

## What Was Attempted

- **Goal**: Load balance OpenAI Responses API requests across multiple deployments (regions, API keys) to distribute quota, reduce latency, and provide failover.
- **Tool/approach**: LiteLLM proxy's router with `routing_strategy: usage-based-routing-v2`. Users configured multiple Azure/OpenAI deployments under a single model group and expected the router to distribute requests while preserving correctness for encrypted content items.
- **Setup**: LiteLLM proxy deployed with multiple backend deployments (e.g., Azure East US, Azure West Europe) each with different API keys belonging to different OpenAI organizations. Clients using OpenAI's Responses API with encrypted reasoning items (IDs like `rs_...`).

## What Went Wrong

- **Symptoms**: Follow-up Responses API requests containing encrypted content items (reasoning items with IDs like `rs_...`) returned an error from OpenAI: `invalid_encrypted_content`. Initial requests succeeded — only follow-up requests that included previously-returned encrypted items in their input failed intermittently. The error rate correlated with the number of deployments (more deployments = higher chance of routing to the wrong one).
- **Severity**: High — complete failure for Responses API calls with encrypted content when routed to the wrong deployment. Other API endpoints (chat completions, embeddings) were unaffected.
- **Reproducibility**: Consistent and deterministic — a follow-up request with an encrypted content item would always fail if the router directed it to a deployment with a different API key than the one that created the item.

### Symptom 1: Encrypted content items fail with `invalid_encrypted_content` when routed to a different deployment's API key

- **Evidence**: The report's Summary section describes the error directly. The Background section explains why: "Encrypted content items are cryptographically tied to the API key's organization that created them."
- **Quote**: "When load balancing OpenAI's Responses API across deployments with different API keys (e.g., different Azure regions or OpenAI organizations), follow-up requests containing encrypted content items (like `rs_...` reasoning items) would fail with an error indicating the 'encrypted content organization_id did not match the target organization.'"
- **Confidence**: settled.

### Symptom 2: Only follow-up requests with encrypted items were affected; initial requests and other endpoints were fine

- **Evidence**: The Summary explicitly lists scope boundaries.
- **Quote**: "Responses API calls with encrypted content: Complete failure when routed to the wrong deployment. Initial requests: Unaffected — only follow-up requests containing encrypted items failed. Other API endpoints: No impact — chat completions, embeddings, etc. functioned normally."
- **Confidence**: settled.

### Symptom 3: Error rate correlated with the number of deployments

- **Evidence**: The Timeline bullet states the correlation explicitly.
- **Quote**: "Error rate correlated with number of deployments (more deployments = higher chance of routing to wrong one)"
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: OpenAI's Responses API encrypted content items (like `rs_...` reasoning items) are cryptographically bound to the API key's organization at creation time. Decryption requires the same key. LiteLLM's router had no mechanism to track which deployment created specific encrypted content items and route follow-up requests accordingly — it treated all deployments as interchangeable. The 6-step problem flow is described: user calls `router.aresponses()` → load balanced to Deployment A (Azure East US, API Key 1) → response contains `rs_abc123` encrypted with Org 1's key → user makes follow-up request with `rs_abc123` → router load balances to Deployment B (Azure West Europe, API Key 2) → Deployment B tries to decrypt with Org 2's key → fails.
- **Our assessment**: Agree completely. The root cause is a fundamental routing invariant violation: the router assumed all deployments in a model group produce mutually interchangeable responses, but encrypted content items carry an implicit cryptographic dependency on their creating deployment. This is a novel failure mode for LLM gateways because it arises from a property unique to the Responses API (organization-bound encrypted reasoning items) — chat completions and embeddings don't return content that is cryptographically bound to the creating key, so traditional affinity mechanisms never had to handle this.
- **Category**: tool-limitation (affinity mechanism gap in LiteLLM router).

### Root-cause detail A: Three existing affinity mechanisms were insufficient for encrypted content

- **Evidence**: The Background section enumerates all three mechanisms and explains why each falls short.
- **Quote**: "`responses_api_deployment_check`: Requires `previous_response_id` which some clients (like Codex) don't provide. `deployment_affinity`: Too broad — pins *all* requests from a user to one deployment, reducing effective quota by the number of users. `session_affinity`: Requires explicit session IDs and still reduces quota."
- **Confidence**: settled.

### Root-cause detail B: The 6-step problem flow shows exactly when and how the router's interchangeability assumption breaks

- **Evidence**: The report's "The Problem Flow" section walks through six numbered steps.
- **Quote**: "1. User calls `router.aresponses()` with model `gpt-5.1-codex`; 2. Router load balances to Deployment A (Azure East US, API Key 1); 3. Response contains encrypted reasoning item `rs_abc123` (encrypted with Org 1's key); 4. User makes follow-up request with `rs_abc123` in the input; 5. Router load balances to Deployment B (Azure West Europe, API Key 2); 6. Deployment B tries to decrypt `rs_abc123` with Org 2's key → fails"
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: A new `encrypted_content_affinity` pre-call check that intelligently tracks encrypted content and routes follow-up requests only when necessary. No cache, no TTL, no `previous_response_id` required. Normal requests (without encrypted content) continue to load balance freely.
- **Workaround**: Using `deployment_affinity` was possible but reduced effective quota to 1/N where N = number of deployments, which defeats the purpose of multi-region load balancing. Using a single deployment avoided the issue entirely but eliminated redundancy.
- **Unresolved**: None stated; status is Resolved. The initial fix was deployed Feb 24, 2026; a streaming follow-up fix was deployed Mar 3, 2026.

### Fix detail A: Encoding `model_id` into output item IDs and encrypted content itself — two-layer redundancy

- **Evidence**: The Implementation section describes two encoding strategies. Item IDs are transformed: `rs_abc123` becomes `encitem_{base64("litellm:model_id:{model_id};item_id:rs_abc123")}`. Encrypted content is wrapped: `litellm_enc:{base64("model_id:{model_id}")};{original_encrypted_content}`. The dual encoding provides redundancy because "some clients (like Codex) don't consistently send item IDs in follow-up requests, but they always send the `encrypted_content` itself."
- **Quote**: "When a response contains output items with encrypted_content, LiteLLM encodes the originating deployment's model_id in two places for redundancy: 1. Into the item ID (if present) — transforms `rs_abc123` into `encitem_{base64("litellm:model_id:{model_id};item_id:rs_abc123")}` 2. Into the encrypted_content itself — wraps the content with `litellm_enc:{base64("model_id:{model_id}")};{original_encrypted_content}`"
- **Confidence**: settled.

### Fix detail B: `EncryptedContentAffinityCheck` — decode-only, no cache, no TTL

- **Evidence**: The `async_filter_deployments` method decodes `model_id` from item IDs or encrypted content on-the-fly at routing time. No `async_log_success_event`, no cache lookups. The `_extract_model_id_from_input` method tries two sources: decoding from item ID first, then falling back to unwrapping from encrypted_content.
- **Quote**: "The `model_id` is decoded directly from the item ID or encrypted_content. A code block shows the `EncryptedContentAffinityCheck` class with its `async_filter_deployments` method extracting `model_id` from input items (ID or encrypted_content) and pinning to that deployment."
- **Confidence**: settled.

### Fix detail C: Rate limit bypass for affinity-pinned requests

- **Evidence**: The page shows that when encrypted content requires a specific deployment, RPM/TPM limits are bypassed since the request would fail on any other deployment anyway. A code snippet from `router.py` demonstrates: when `_encrypted_content_affinity_pinned` is true and only one healthy deployment exists, it returns that deployment directly, bypassing routing strategy and RPM/TPM checks.
- **Quote**: "When encrypted content requires a specific deployment, RPM/TPM limits are bypassed since the request would fail on any other deployment anyway."
- **Confidence**: settled.

### Fix detail D: After forwarding, LiteLLM restores original IDs and unwraps content upstream

- **Evidence**: The implementation section explicitly states that "before forwarding to the upstream provider, LiteLLM restores the original item IDs and unwraps encrypted_content so the provider never sees the encoded form." A code snippet calls `_restore_encrypted_content_item_ids_in_input`.
- **Confidence**: settled.

### Fix detail E: Streaming response fix (Mar 3, 2026) — the initial fix missed wrapping in streaming events

- **Evidence**: The follow-up section describes how the `_update_encrypted_content_item_ids_in_response` function only modified the final response object (used for non-streaming). For streaming, individual chunks processed by `ResponsesAPIStreamingIterator._process_chunk` were not applying the wrapping logic to streaming events. Clients consuming streams received raw, unwrapped content and sent it back, causing the affinity check to fail.
- **Quote**: "After the initial fix was deployed, users reported the `invalid_encrypted_content` error still occurred when using streaming responses with clients like Codex. Non-streaming responses had encrypted_content correctly wrapped, but individual streaming events contained raw, unwrapped content."
- **Quote** (root cause): "The `_update_encrypted_content_item_ids_in_response` function only modified the final response object (used for non-streaming). For streaming, individual chunks are processed by `ResponsesAPIStreamingIterator._process_chunk`, which was not applying the wrapping logic to streaming events."
- **Confidence**: settled.

## Concrete Artifacts

All artifacts verbatim from the source, extracted via WebFetch.

**Incident metadata (verbatim from source):**
```
Date: Feb 24, 2026
Duration: Ongoing (until fix deployed)
Severity: High (for users load balancing Responses API across different API keys)
Status: Resolved
```

**Remediation table (verbatim from source):**
```
# Action                                                                    Status     Code
1 Encode model_id into encrypted-content item IDs on response               ✅ Done    responses/utils.py
2 Restore original item IDs before forwarding to upstream provider          ✅ Done    responses/main.py
3 EncryptedContentAffinityCheck: decode item IDs to route (no cache)        ✅ Done    encrypted_content_affinity_check.py
4 Add encrypted_content_affinity to OptionalPreCallChecks type              ✅ Done    types/router.py
5 Implement rate limit bypass for affinity-pinned requests                  ✅ Done    router.py
6 Unit tests: encoding/decoding utilities, routing, RPM bypass              ✅ Done    test_encrypted_content_affinity_check.py
7 Documentation: Responses API guide, load balancing guide, config ref.     ✅ Done    Docs
8 [Mar 3] Fix streaming events to wrap encrypted_content                    ✅ Done    responses/streaming_iterator.py
```

**Before config — using `deployment_affinity` (verbatim from source):**
```yaml
routing_strategy: usage-based-routing-v2              # pick the best deployment
enable_pre_call_checks: true
optional_pre_call_checks:
  - deployment_affinity                               # but ALL requests from a user → 1 deployment
                                                      # effective quota = 1/N
```

**After config — using `encrypted_content_affinity` (verbatim from source):**
```yaml
routing_strategy: usage-based-routing-v2              # pick the best deployment
enable_pre_call_checks: true
optional_pre_call_checks:
  - encrypted_content_affinity                        # normal requests load balance freely
                                                      # only encrypted-content requests pin when needed
deployment_affinity_ttl_seconds: 86400
```

**Streaming fix diff — `responses/streaming_iterator.py` (verbatim from source):**
```python
# When encrypted_content_affinity_enabled and the event type is
# response.output_item.added or response.output_item.done:
# 1. Get the item's encrypted_content
# 2. Get model_id from litellm_metadata
# 3. Wrap using _wrap_encrypted_content_with_model_id
# 4. Set wrapped content back on the item
```

**Key benefits list (verbatim from source):**
```
✅ No quota reduction: only pins requests containing encrypted items
✅ Bypasses rate limits: when encrypted content requires a specific deployment,
   RPM/TPM limits don't block it
✅ No previous_response_id required: works by encoding model_id directly into
   the item ID
✅ No cache required: model_id is decoded on-the-fly from the item ID —
   no Redis, no TTL
✅ Globally safe: can be enabled for all models; non-Responses-API calls
   are unaffected
✅ Surgical precision: normal requests continue to load balance freely
```

## Extracted Lessons

### Lesson 1: Encrypted/cryptographically-bound content in API responses creates a routing invariant that traditional affinity mechanisms don't address
- **Evidence**: Three existing affinity mechanisms (`previous_response_id`, `deployment_affinity`, `session_affinity`) all failed at this use case because they either depended on client cooperation (sending `previous_response_id`), were too broad (pinning all user traffic), or required explicit session management. The encrypted content was tied to the *creating deployment* in a way none of them tracked.
- **Quote**: "Encrypted content items are cryptographically tied to the API key's organization that created them."
- **Confidence**: settled (vendor-incident-level confidence for this specific case; generalizable as emerging).
- **Actionable as**: When implementing load balancing for any API that returns content cryptographically bound to the creating key, ensure the router can pin follow-up requests containing that content to the originating deployment — traditional session/affinity mechanisms may be insufficient.

### Lesson 2: Content-aware routing is a surgical alternative to session-wide affinity — it pins only the requests that need pinning, preserving load balancing for the rest
- **Evidence**: The `encrypted_content_affinity` check operates on individual items within a request (item ID or encrypted_content), not on user/session scope. Normal requests (without encrypted items) continue to load balance freely across all deployments. The key benefits list explicitly contrasts this with `deployment_affinity`'s "effective quota = 1/N".
- **Quote**: "Surgical precision: normal requests continue to load balance freely."
- **Confidence**: settled (shipped feature behavior documented by vendor).
- **Actionable as**: Design affinity mechanisms at the *request content* level rather than the *user/session* level when the binding constraint (encrypted content, signed payloads, idempotency keys) is per-item rather than per-session.

### Lesson 3: Encoding routing metadata directly into the response payload (with upstream transparency) eliminates the need for a separate cache or coordination store
- **Evidence**: The `encrypted_content_affinity` implementation embeds `model_id` into item IDs and encrypted content itself using base64 encoding with recognizable prefixes (`encitem_`, `litellm_enc:`). No Redis, no TTL, no `async_log_success_event`. The encoded form is transparent to the upstream provider — it is restored before forwarding.
- **Quote**: "No cache required: `model_id` is decoded on-the-fly from the item ID — no Redis, no TTL"
- **Confidence**: settled.
- **Actionable as**: When follow-up routing depends on information not available at request time (which deployment created a response), encode routing metadata into the response in a reversible, upstream-transparent way rather than maintaining a side-channel cache.

### Lesson 4: Streaming and non-streaming responses need separate treatment — fixing only the final response object misses the streaming path entirely
- **Evidence**: The initial fix (Feb 24) only modified `_update_encrypted_content_item_ids_in_response` which operates on the final response object. The streaming path via `ResponsesAPIStreamingIterator._process_chunk` was not wrapped, so streaming clients (Codex) continued to see the error until the Mar 3 follow-up fix.
- **Quote**: "The `_update_encrypted_content_item_ids_in_response` function only modified the final response object (used for non-streaming). For streaming, individual chunks are processed by `ResponsesAPIStreamingIterator._process_chunk`, which was not applying the wrapping logic to streaming events."
- **Confidence**: settled.
- **Actionable as**: When adding response-wrapping or transformation logic to an LLM gateway, audit both the non-streaming (final response) and streaming (per-chunk event) code paths — they are often implemented in separate components and fixing only one leaves a regression window.

### Lesson 5: Rate limit bypass is justified when a request would fail on any other deployment — traditional throttling does not apply
- **Evidence**: The `router.py` modification bypasses RPM/TPM limits when `_encrypted_content_affinity_pinned` is true and only one healthy deployment exists. The rationale: the request cannot be served by any other deployment, so rejecting it for rate limits would be pointless.
- **Quote**: "When encrypted content requires a specific deployment, RPM/TPM limits are bypassed since the request would fail on any other deployment anyway."
- **Confidence**: settled (vendor-documented design decision).
- **Actionable as**: Affinity-pinned requests should bypass rate limits — if a request is inherently pinned to one deployment, rate-limit checks against the broader pool create false rejections. Design affinity-aware rate limiting rather than applying pool-wide limits to pinned requests.

## Cross-References

- **Corroborates failures in**:
  - `failure-litellm-wildcard-model-access-desync.md` — Same vendor (LiteLLM), same category of router-proxy edge case where state management (in-memory provider sets vs encrypted content binding) caused routing failures. Both incidents involve the router treating deployments as interchangeable when they are not — the wildcard incident for stale provider sets, this one for cryptographically bound content.
  - `blog-litellm-realtime-webrtc-http-endpoints.md` — Describes LiteLLM's encrypted ephemeral token flow for WebRTC routing, where the proxy encodes routing state (target model) into an encrypted token. This incident's `encrypted_content_affinity` uses a similar pattern (encoding `model_id` into encrypted content for routing purposes) but for a different purpose — the WebRTC tokens are for initial connection routing while this incident's encoding is for follow-up request affinity.

- **Contradicts**: None. No existing source note claims that `deployment_affinity` or `session_affinity` are sufficient for encrypted content routing, or that all Responses API deployments produce interchangeable responses.

- **Extends / thematically adjacent**:
  - `failure-litellm-httpx-cache-eviction.md` — Same vendor (LiteLLM), same theme of shared-state management in the proxy layer (cache eviction closing shared httpx clients vs encrypted content items requiring deployment pinning). Both incidents involve the router making assumptions about resource interchangeability that turn out to be incorrect under specific conditions.
  - `blog-litellm-redis-circuit-breaker.md` — Documents LiteLLM's resilience pattern for Redis dependency in the routing hot path. This incident's `encrypted_content_affinity` eliminates Redis entirely for the affinity concern (no cache, no TTL), which is thematically adjacent as a design choice that reduces external dependencies for critical routing decisions.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` (Claim 4) — Discusses generalizing outages ("how could this happen in another way?") rather than patching specific failures. This incident's dual-encoding strategy (item ID + encrypted_content) is a direct application of that principle: "Codex doesn't send item IDs" was discovered during the initial fix, and the encrypted_content encoding provides coverage for that gap.

- **Novel**: This is the first source note covering:
  1. **Encrypted content affinity as a routing requirement** — the specific failure mode where cryptographically-bound API response items create a deployment affinity requirement that traditional session/user-level affinity mechanisms cannot satisfy.
  2. **Content-embedded routing metadata** — the pattern of encoding routing state (`model_id`) directly into response payload (item IDs and encrypted content body) with upstream-transparent restoration, eliminating the need for a separate affinity cache.
  3. **The streaming-vs-non-streaming wrapping gap** — the failure of the initial fix to cover the streaming path, and the specific code-level fix required.
  4. **Organization-bound encrypted content in LLM proxy routing** — the intersection of cryptographic key boundaries and multi-region load balancing, which is a new failure surface specific to the Responses API (not present in chat completions or embeddings).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — LLM gateway/proxy routing)**: Add a concrete failure pattern and routing design principle: "LLM gateway responses may contain content cryptographically bound to the creating deployment (e.g., OpenAI Responses API encrypted reasoning items). Traditional affinity mechanisms (session affinity, deployment affinity, `previous_response_id`-based routing) are often insufficient — design content-aware affinity that encodes routing metadata directly into the response payload for upstream-transparent decoding, with separate handling for streaming and non-streaming paths." Include the `encrypted_content_affinity` pattern as a reference implementation.

- **Chapter 05 (Rate limiting and capacity management)**: Add guidance on affinity-pinned rate-limit bypass: "When a request is inherently pinned to a specific deployment (due to encrypted content, signed payloads, or other cryptographic binding), the rate-limit check should account for this — rejecting a pinned request for pool-wide rate-limit exhaustion creates false failures. Design affinity-aware rate limiting."

- **Chapter 02 (Incident response — postmortem patterns)**: The streaming-fix gap (initial fix covered non-streaming only, follow-up fix needed for streaming) is a useful incident-anatomy case study showing how a single code path fix can miss a parallel implementation path, especially relevant for LLM gateways where streaming and non-streaming often use separate components.

- **Chapter 04 (Load balancing for LLM services)**: Add "Affinity for cryptographically-bound content" as a new axis of routing consideration, noting that `deployment_affinity` and `session_affinity` are blunt instruments that reduce effective multi-region benefits, and that content-embedded routing metadata is a surgical alternative.

## Extraction Notes

- Source read in full via WebFetch (HTML page). Complete article content extracted — no paywall, no truncation. The page includes two dated sections: the initial incident report (Feb 24, 2026) and the streaming follow-up fix (Mar 3, 2026), both captured.
- The page is a self-contained incident report with code-level descriptions (not full diffs, but detailed pseudocode and file references), a remediation table, before/after YAML configuration, and a timeline. GitHub file links are provided in the remediation table but were not followed (they point to source code lines, not narrative content).
- No contradiction issue filed: verified against CONTRADICTIONS.md (empty) and all existing source notes. The specific failure pattern (encrypted content cryptographic binding across multi-key load balancing) is genuinely novel in this corpus. No existing note claims that `deployment_affinity` or `session_affinity` handle encrypted content, nor that Responses API responses are interchangeable across deployments.
- The miner-related-notes.md candidates that are not cited above are dismissed because they do not address encrypted content affinity, Responses API routing, or organization-bound cryptographic content in LLM gateways:
  - `docs-langfuse-security-and-guardrails.md` — Security/guardrail patterns for LLM applications, unrelated to proxy routing affinity.
  - `docs-langfuse-mcp-server.md` — MCP server documentation access, unrelated.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO fundamentals, unrelated.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — Gaming/retail SRE, unrelated.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — AI agent spectrum, unrelated.
  - `blog-litellm-claude-fable-5-day-0.md` — Day 0 model support, unrelated.
  - `docs-google-sre-prodcast-05-06-ai-safety.md` — AI safety frameworks, unrelated.
  - `blog-litellm-observatory.md` — Long-running load tests, unrelated.
