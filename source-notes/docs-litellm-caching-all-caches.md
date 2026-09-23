---
source_url: https://docs.litellm.ai/docs/caching/all_caches
source_type: docs
title: "Caching — In-Memory, Redis, s3, gcs, Redis Semantic Cache, Disk | liteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-23)
date_extracted: 2026-09-23
last_checked: 2026-09-23
status: current
confidence_overall: emerging
issue: "#1431"
---

# LiteLLM SDK Caching Reference (In-Memory, Redis, s3, gcs, Semantic, Disk)

> The consolidated SDK reference for LiteLLM response caching: the full nine-backend matrix (local in-memory, disk, redis, s3, gcs, azure-blob, plus three semantic backends), the `Cache.__init__` control surface (`type`, `supported_call_types`, `semantic_cache_scope`, layered TTL knobs, `namespace`, `redis_flush_size`), the four per-call cache-controls (`no-cache` / `no-store` / `ttl` / `s-maxage`) for runtime bypass, the custom cache-key override, the `kwarg["cache_hit"]` observability hook, and hard deployment constraints for `valkey-semantic` (ElastiCache Serverless / cluster-mode limits).

## Source Context

- **Type**: docs — LiteLLM SDK configuration reference page (`/docs/caching/all_caches`), one page of the LiteLLM Python SDK configuration tree on `docs.litellm.ai`, rendered by Docusaurus.
- **Author credibility**: First-party vendor documentation for LiteLLM (BerriAI), a widely used open-source LLM gateway/SDK. Authoritative on **what the config surface is** (signatures, parameter defaults, documented behaviors). Not authoritative on how caching behaves in production — the page reports no benchmarks, no hit-rate/latency/cost figures, and no failure behaviour for the remote backends; provider-side OpenAI/Anthropic prompt caching is explicitly linked out to a separate page.
- **Scope**: Covers SDK-level response caching only: backend matrix and per-backend setup code, the per-call cache-control kwarg, the cache context manager, custom cache keys/add-get overrides, the `Cache.__init__` parameter surface, and the cache-hit logging hook. Does NOT cover the proxy-tier caching page (`/docs/proxy/caching`, sibling issue #1432), provider prompt caching (linked out), or cache eviction/invalidation semantics for remote backends. The Redis/Qdrant/Valkey semantic-cache walkthrough sections substantially restate `blog-litellm-valkey-semantic-caching.md` and are treated as covered; only their new parameter and constraint surfaces are extracted here.

## Extracted Claims

### Claim 1: LiteLLM's SDK response cache supports nine documented backends spanning two sharing classes — per-process stores (`local`, `disk`) and shared stores (`redis`, `s3`, `gcs`, `azure-blob`, plus semantic stores `redis-semantic`, `qdrant-semantic`, `valkey-semantic`)
- **Evidence**: The "Initialize Cache" section enumerates the backends as a tab list with a code example for each; no measured performance data accompanies any of them.
- **Confidence**: settled (documented backend enum with concrete setup code)
- **Quote**: "Initialize Cache - In Memory, Redis, s3 Bucket, gcs Bucket, Redis Semantic, Disk Cache, Qdrant Semantic"
- **Our assessment**: The matrix is the page's core value — one consolidated enumeration of every storage class LiteLLM will write responses to. The per-process vs shared split (`local`/`disk` are local to a Python process and do not share hits across replicas; `redis`/`s3`/`gcs`/`azure-blob` and the semantic stores do) is the capacity-planning question the Prospector flagged; that operational inference is ours, not stated on the page, which is why the sharing-class half stays emerging in flavour while the enum itself is settled.

### Claim 2: `Cache.__init__` restricts `type` to a literal enum defaulting to `local`, and `supported_call_types` is an allow-list defaulting to `["completion", "acompletion", "embedding", "aembedding", "atranscription", "transcription"]` — caching silently does not apply to call types outside the list
- **Evidence**: The `Cache.__init__` signature and the identical `enable_cache`/`update_cache` signatures list both defaults.
- **Confidence**: settled (documented signature facts, checkable against the open-source codebase)
- **Quote**: "    supported_call_types: Optional[\n        List[Literal[\"completion\", \"acompletion\", \"embedding\", \"aembedding\", \"atranscription\", \"transcription\"]]\n    ] = [\"completion\", \"acompletion\", \"embedding\", \"aembedding\", \"atranscription\", \"transcription\"],"
- **Our assessment**: This is the "why is my cache not hitting" answer that no existing note states: the default `type="local"` is a per-process in-memory cache, and call types outside the supported list are never cached. Operators assuming a Redis cache is active because they set `litellm.cache` will be wrong unless `type="redis"` (or a shared backend) is explicit. Note that the signature's `Literal` omits `azure-blob` and `qdrant-semantic` even though the page documents those backends with code — the shorthand `type=` enum appears to lag the documented backend surface.

### Claim 3: `semantic_cache_scope` (default `"key"`) is the semantic-cache tenant-scope control — `key` scopes hits to key/team/org, `end_user` additionally scopes per end user
- **Evidence**: The `Cache.__init__` signature documents the parameter and default inline.
- **Confidence**: settled (documented signature fact)
- **Quote**: "    # semantic cache tenant scope: \"key\" (key/team/org) or \"end_user\" (also per end user)\n    semantic_cache_scope: str = \"key\","
- **Our assessment**: This is the shipped control surface that Ch05 currently reaches for only as an `[editorial]` hedge. Because a semantic hit is a similarity decision rather than an identity one, this knob is what prevents one tenant's prompt from being answered with another tenant's cached response: the default separates at key/team/org granularity but not below it, and `end_user` opts into per-end-user separation. Behave like a config fact; production isolation properties would need incident data to move past that.

### Claim 4: Four per-call cache-controls on the `cache={...}` kwarg provide a runtime bypass and expiry contract — `no-cache` (do not return a cached response), `no-store` (do not write to cache), `ttl` (per-request expiry in seconds), `s-maxage` (accept only cached responses younger than N seconds)
- **Evidence**: The "Switch Cache On / Off Per LiteLLM Call" section defines all four controls and shows a code example for each.
- **Confidence**: settled (documented, checkable semantics)
- **Quote**: "`no-cache`: *Optional(bool)* When `True`, Will not return a cached response, but instead call the actual endpoint."
- **Quote**: "`no-store`: *Optional(bool)* When `True`, Will not cache the response."
- **Quote**: "`s-maxage`: *Optional(int)* Will only accept cached responses that are within user-defined range (in seconds)."
- **Our assessment**: The no-cache/no-store distinction is the easy operational mistake: `no-cache` still lets the cache be written (a future request can resurrect the entry), `no-store` never writes. Per-request controls give the documented mitigation for a poisoned or stale entry without a redeploy — `{"no-cache": True}` forces a live call, and the code example URLs the semantics concretely. This is the "opt out of a stale entry" contract the Prospector asked for.

### Claim 5: Cache-key derivation is an operator extension point — `cache.get_cache_key = fn` replaces the key function, and the docs' own example key composes `model + messages + temperature + logit_bias`, with no user/tenant identity in it
- **Evidence**: The "Custom Cache Keys" section shows the key function, the assignment, and the note that nothing outside the composed fields is part of the key.
- **Confidence**: settled (documented example, verbatim)
- **Quote**: "    key = kwargs.get(\"model\", \"\") + str(kwargs.get(\"messages\", \"\")) + str(kwargs.get(\"temperature\", \"\")) + str(kwargs.get(\"logit_bias\", \"\"))"
- **Our assessment**: The page documents the *override* mechanism but not what the built-in default key derives, so the Prospector's framing — "no user/tenant identity in the default key" — is only directly supportable for the documented example, not for the shipped default. What is checkable: anything a custom key omits is invisible to the cache, so a team that copies this example verbatim gets a cross-tenant response-reuse hazard (requests differing only in user identity collide). The rule to state in the guide: cache keys used across tenants must include the tenant scope explicitly. Correctness surface, filed for Ch06.

### Claim 6: Cache hits are surfaced per-request in success events as `kwarg["cache_hit"]`, reachable through a `CustomLogger` success callback
- **Evidence**: The "Logging" section shows the callback reading the key and the exact accessor spelling.
- **Confidence**: settled (documented code surface)
- **Quote**: "Cache hits are logged in success events as `kwarg[\"cache_hit\"]`."
- **Our assessment**: The only per-request cache observability surface on the page, and the concrete hook for hit-rate telemetry and for proving a canary's traffic actually replayed from cache. Pairs directly with Ch02's existing point that a warm cache can make a green run meaningless — here is where the signal lives on the LiteLLM path. Note the page's spelling is the singular `kwarg`, not `kwargs`, which is itself a trap for code written from memory.

### Claim 7: `REDIS_*` environment variables map onto Redis client kwargs and "may fail during Redis client initialization" for non-string parameters — integers, booleans, and complex objects must be passed as `Cache()` kwargs instead
- **Evidence**: The page carries an explicit `warning` admonition distinguishing string env config from non-string kwargs.
- **Confidence**: settled (vendor warning, verbatim)
- **Quote**: "If you need to pass non-string Redis parameters (integers, booleans, complex objects), avoid `REDIS_*` environment variables as they may fail during Redis client initialization. Instead, pass them directly as kwargs to the `Cache()` constructor."
- **Our assessment**: A deployment-class footgun: env vars are strings, so `REDIS_SSL="False"` (shown in the page's own GCP IAM example!) or a boolean/integer param travels as a string and can fail client init — or worse, type-coerce wrong. The page recommends `REDIS_*` env vars as the primary mechanism but brackets them to string-valued params. Cheap to record, and the guide's deployment-chapter config rules should carry the string-vs-nonstring split.

### Claim 8: The `valkey-semantic` backend has hard deployment constraints — the valkey-search module must be loaded, ElastiCache Serverless does not support vector search, and cluster-mode multi-shard endpoints are unsupported because the async client cannot route `FT.*` across shards
- **Evidence**: The `valkey-semantic` "Requirements" paragraph states all three constraints plus the scaling direction.
- **Confidence**: settled (vendor-declared requirements)
- **Quote**: "The `valkey-search` module must be loaded on the server (run `MODULE LIST` and look for `search`, or `FT._LIST`)."
- **Quote**: "ElastiCache **Serverless does not support vector search**, so a serverless endpoint will not work here. Multi-shard (cluster-mode-enabled) endpoints are not supported by this backend, since the async client cannot route the `FT.*` search commands across shards; scale vertically instead."
- **Our assessment**: The most concretely actionable part of the page, and new relative to the blog note: the blog established that ElastiCache for Valkey (node-based) works, but this page's pre-flight list adds what *doesn't* — Serverless, and horizontal sharding — forcing a vertical-scaling capacity plan. Generalizes beyond LiteLLM: any vector-search cache has a serverless/sharding story, and `MODULE LIST`/`FT._LIST` is the two-command verification.

### Claim 9: The signature carries three distinct TTL knobs — `ttl`, `default_in_memory_ttl`, `default_in_redis_ttl` — plus `namespace` and `redis_flush_size`, but the page documents no precedence or eviction semantics for any of them
- **Evidence**: The `Cache.__init__` signature lists the knobs; the page body has no section defining their interaction.
- **Confidence**: emerging (parameter existence is settled; precedence/behavior is undocumented on this page)
- **Quote**: "    ttl: Optional[float] = None,\n    default_in_memory_ttl: Optional[float] = None,\n    # redis cache params\n    host: Optional[str] = None,\n    port: Optional[str] = None,\n    password: Optional[str] = None,\n    namespace: Optional[str] = None,\n    default_in_redis_ttl: Optional[float] = None,\n    redis_flush_size=None,"
- **Our assessment**: Existence of a layered-TTL model is checkable — per-cache `ttl` plus per-tier defaults `default_in_memory_ttl`/`default_in_redis_ttl` implies tiers can expire at different rates (an in-memory tier and a Redis tier serving different staleness windows from the same logical cache). But the page gives no precedence rule or eviction semantics, so any claim about which knob wins is not supportable from this source — that is exactly the gap `failure-litellm-httpx-cache-eviction.md` covers for the *client* cache (a different cache object with its own 10-minute TTL). `redis_flush_size` exists as a batching control but its semantics are also undocumented here.

### Claim 10: The page documents shared-cache auth and indexing params absent from every existing note — GCP Memorystore IAM Redis auth (`gcp_service_account`, `ssl`, `ssl_cert_reqs`, `ssl_check_hostname` on a `RedisClusterCache`), and Qdrant `qdrant_quantization_config` (one of `binary`/`product`/`scalar`)
- **Evidence**: The GCP IAM section shows the `RedisClusterCache` auth example and `REDIS_*` env-var equivalents; the Qdrant section shows `qdrant_quantization_config`.
- **Confidence**: settled (documented config surface)
- **Quote**: "    gcp_service_account=\"projects/-/serviceAccounts/your-sa@project.iam.gserviceaccount.com\",\n    ssl=True,\n    ssl_cert_reqs=None,\n    ssl_check_hostname=False,"
- **Quote**: "    qdrant_quantization_config =\"binary\", # can be one of 'binary', 'product' or 'scalar' quantizations that is supported by qdrant"
- **Our assessment**: Both are net-new backend-matrix parameters the Prospector targeted: IAM-authenticated Memorystore Redis is a managed-GCP pattern that needs `ssl_cert_reqs=None` + `ssl_check_hostname=False` (i.e., TLS connection with certificate verification disabled — a policy decision teams should see named), and Qdrant quantization is a storage-vs-recall index tradeoff surfaced as a one-line enum. Azure Blob (`azure_account_url`, `azure_blob_container`) is likewise absent from the corpus and appears on this page as a first-class backend.

## Concrete Artifacts

### Per-call cache-controls (verbatim from "Switch Cache On / Off Per LiteLLM Call", one snippet per control)

```python
response = litellm.completion(
        model="gpt-5.6-luna",
        messages=[
            {
                "role": "user",
                "content": "hello who are you"
            }
        ],
        cache={"no-cache": True},
    )
```

```python
        cache={"no-store": True},
```

```python
        cache={"ttl": 10},
```

```python
        cache={"s-maxage": 60},
```

Source: https://docs.litellm.ai/docs/caching/all_caches — "Example usage" blocks (the fourth example hardcodes `s-maxage = 60` meaning "only accept cached responses for 60 seconds").

### Custom cache-key override (verbatim from "Custom Cache Keys")

```python
def custom_get_cache_key(*args, **kwargs):
    # return key to use for your cache:
    key = kwargs.get("model", "") + str(kwargs.get("messages", "")) + str(kwargs.get("temperature", "")) + str(kwargs.get("logit_bias", ""))
    print("key for cache", key)
    return key
```

```python
cache.get_cache_key = custom_get_cache_key # set get_cache_key function for your cache
```

Source: https://docs.litellm.ai/docs/caching/all_caches — "Custom Cache Keys" section.

### GCP Memorystore IAM Redis auth (verbatim from "GCP IAM Redis Authentication")

```python
litellm.cache = RedisClusterCache(
    startup_nodes=[
        {"host": "10.128.0.2", "port": 6379},
        {"host": "10.128.0.2", "port": 11008},
    ],
    gcp_service_account="projects/-/serviceAccounts/your-sa@project.iam.gserviceaccount.com",
    ssl=True,
    ssl_cert_reqs=None,
    ssl_check_hostname=False,
)
```

Source: https://docs.litellm.ai/docs/caching/all_caches — "GCP IAM Redis Authentication".

### Cache-hit logging hook (verbatim from "Logging")

```python
class MyCustomHandler(CustomLogger):
  async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
       print(f"On Success")
      print(f"Value of Cache hit: {kwargs['cache_hit']}")
```

Source: https://docs.litellm.ai/docs/caching/all_caches — "Logging" section.

### Valkey-search pre-flight constraints (verbatim from valkey-semantic Requirements)

```
The `valkey-search` module must be loaded on the server (run `MODULE LIST` and look for `search`, or `FT._LIST`). On AWS ElastiCache, vector search is available on node-based Valkey 8.2+ clusters; a cluster-mode-disabled node group is supported and is the recommended target, and a primary with read replicas is fine since only horizontal sharding is unsupported. ElastiCache Serverless does not support vector search, so a serverless endpoint will not work here. Multi-shard (cluster-mode-enabled) endpoints are not supported by this backend, since the async client cannot route the `FT.*` search commands across shards; scale vertically instead.
```

Source: https://docs.litellm.ai/docs/caching/all_caches — valkey-semantic "Requirements" callout.

## Cross-References

- **Corroborates**:
  - `source-notes/blog-litellm-valkey-semantic-caching.md` **Claim 6** ("tag field that isolates each cache key's scope plus an HNSW vector field for the prompt embedding ... returns the cached response when cosine similarity clears a configurable threshold"). The blog's per-request scope isolation is formalized here as the `semantic_cache_scope` parameter (Claim 3) — same isolation concept, now with named config. (Verified: #1176 Claim 6.)
  - `source-notes/blog-litellm-redis-circuit-breaker.md` **Claim 1** ("Redis is a critical dependency in the AI Gateway hot path ... cache lookups, spend tracking"). This page's `redis` / `redis-semantic` backends are the cache-lookup surface that hot path refers to; consistent shared infrastructure context. (Verified: #647 Claim 1.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 4** (14-day TTL replay default on the eval-harness cache) — same "cache is a cost control, not a correctness control" theme, opposite side: promptfoo memoises eval results client-side; LiteLLM response caching memoises gateway responses. (Verified: #1275 Claim 4.)

- **Extends**:
  - `source-notes/blog-litellm-valkey-semantic-caching.md` — extends the blog's semantic-cache coverage (backend existence, mechanism, ElastiCache-node support) with the SDK-level parameter surface the blog lacks: `semantic_cache_scope`, `supported_call_types`, the `Cache.__init__` type enum, and the hard deployment constraints Claim 8 (Serverless / cluster-mode limits are new — the blog only says node-based ElastiCache for Valkey works).
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 9** (single `PROMPTFOO_CACHE_TTL` env knob) — the layered `ttl` / `default_in_memory_ttl` / `default_in_redis_ttl` model here (Claim 9) is the general case of promptfoo's single TTL: two cache tiers that can expire at different rates. (Verified: #1275 Claim 9.)
  - `source-notes/failure-litellm-httpx-cache-eviction.md` **Claim 1** (eviction cleanup destroying shared references) — the incident's eviction policy lived in `LLMClientCache` (the *client* cache, 200-entry / 10-min TTL), a different object from the response `Cache()` this page documents; the page's TTL knobs are therefore not the incident's driver, and the two must stay distinct in the guide. (Verified: #461 Claim 1.)
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 1** (gateway translation destroying a provider prompt cache) — provider-prompt-caching layer, which this page explicitly links out to; gateway response caching (this page) and provider prompt caching are distinct tiers and should not be conflated. (Verified: #697 Claim 1.)
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 3** (auto-injected `cache_control` markers for Claude prompt caching) — the provider-side prompt-caching mechanism on the same LiteLLM stack; different tier from the response cache here. (Verified: #668 Claim 3.)

- **Contradicts**: None. Verified against `CONTRADICTIONS.md` (no open `C-NNN` entries) and all corpus notes. The surface overlaps are consistent: the blog note's per-request scope isolation (Claim 6) and this page's `semantic_cache_scope` agree; the `failure-litellm-httpx-cache-eviction.md` TTL/eviction story is for a different cache object, not a disagreement over this one. No contradiction issue filed.

- **Novel** (new to the corpus):
  - **The consolidated nine-backend matrix** with the per-process vs shared sharing split (Claim 1).
  - **`supported_call_types` allow-list default** — the documented reason caching silently skips call types outside the literal set (Claim 2).
  - **`semantic_cache_scope`** as a named, defaulted tenant-scope control for semantic caching — upgrades an `[editorial]` hedge in Ch05 to a config fact (Claim 3).
  - **The four per-call cache-controls** as a runtime bypass contract for stale/poisoned entries (Claim 4).
  - **The `kwarg["cache_hit"]` success-event observability hook** (Claim 6) — the guide's Ch02 cache-hit-signal point gains its concrete LiteLLM accessor.
  - **The `REDIS_*` string-only env-var footgun** (Claim 7) and the GCP Memorystore IAM Redis auth pattern / Qdrant quantization config / azure-blob backend (Claim 10).
  - **The valkey-semantic hard constraints** — Serverless unsupported, cluster-mode multi-shard unsupported, `MODULE LIST`/`FT._LIST` verification (Claim 8).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — semantic caching, ~lines 1073-1107)**: The section currently hedges per-cache-key scope isolation as `[editorial]` citing the blog note ("Per-cache-key scope isolation is the mitigation the vendor describes ... [emerging]"). Replace/extend that hedge with the shipped control surfaced here: `semantic_cache_scope` (default `"key"` = key/team/org; `"end_user"` also per end user) is the vendor's documented isolation knob for semantic caches. Also add: (a) the per-call cache-control contract — `{"no-cache": True}` forces a live call past a stale/poisoned entry, `{"no-store": True}` stops writes, `ttl`/`s-maxage` bound freshness — as the documented no-redeploy mitigation; (b) the `supported_call_types` default allow-list as the "why is my cache not hitting" answer for non-completion/embedding call types; (c) the valkey-semantic deployment pre-flight (module load check via `MODULE LIST`/`FT._LIST`, no ElastiCache Serverless, no cluster-mode multi-shard — scale vertically).

- **Chapter 05 (capacity planning)**: Add the per-process vs shared backend framing — `type="local"` (the `Cache()` default) is per-process and shares no hits across replicas; shared hit-sharing only starts with `redis`/`s3`/`gcs`/`azure-blob` and the semantic stores. Capture the `REDIS_*` env vars are string-only / "may fail during Redis client initialization" for non-string params as a config guideline.

- **Chapter 02 (Observability)**: Add `kwarg["cache_hit"]` on LiteLLM success events as the concrete hook for hit-rate telemetry and for confirming a canary/replay actually replayed from cache — the operational counterpart to the existing "warm cache can make a green run meaningless" point (`cache_hit` proves a call was served from cache before its result is trusted as fresh model output).

- **Chapter 06 (Security and Trust — tenant isolation)**: Add cache-key derivations as a correctness surface: an operator-supplied `cache.get_cache_key` that omits tenant identity (as the page's own example does — `model + messages + temperature + logit_bias`) creates cross-tenant response reuse; state the rule that multi-tenant cache keys must include the tenant scope, and that `semantic_cache_scope="end_user"` is the per-user option for similarity-based hits.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page. Single self-contained page; the three semantic-cache walkthroughs repeat content covered by `blog-litellm-valkey-semantic-caching.md` (#1176), so per the Prospector triage I did not re-extract them; only their new params/constraints (Claims 8, 10) were taken. No sub-pages followed: the linked proxy-caching page is sibling issue #1432's source; prompt-caching is linked out and covered elsewhere.
- `confidence_overall` is `emerging`: per the triage note, signature/config facts (Claims 1, 2, 3, 4, 6, 7, 8, 10) are settled for vendor-product behavior — authoritative on the config surface. The sharing-class inference in Claim 1, the layered-TTL precedence in Claim 9, and the default-key/tenant-identity analysis in Claim 5 are operational synthesis on undocumented behaviour — hence the page overall, which contains no measured results, stays `emerging` rather than `settled`.
- On Claim 5 I deliberately scoped the tenant-identity hazard to the *documented example* key: the page documents the override mechanism and that example, not the built-in default key derivation, so I did not assert the default omits tenant identity (that would overread the source). Quote verbatim from the code block; the page's only claim about keys is the composable example.
- The `kwarg["cache_hit"]` accessor in Claim 6 is copied with the page's singular spelling — it is not a typo for `kwargs`; the page literally shows `kwarg["cache_hit"]` and `print(f"Value of Cache hit: {kwargs['cache_hit']}")` (mixed spellings in the same snippet).
- No contradiction issue filed: verified against `CONTRADICTIONS.md` and all corpus notes; no claim here opposes an existing note (see Cross-References).
- **Candidate dismissal** (from `miner-related-notes.md`, read before Cross-References; cited or dismissed by name):
  - `docs-litellm-batches-api.md` — batch input-file rate limiting; different subsystem, no response-cache surface; dismissed.
  - `docs-litellm-bedrock-invoke.md` / `docs-litellm-bedrock-converse.md` — native Bedrock passthrough routing/auth; no cache surface; dismissed.
  - `docs-litellm-audio-transcription.md` — transcription fallbacks/`mock_testing_fallbacks`; dismissed.
  - `blog-litellm-auto-router-v2.md` — complexity/semantic/adaptive *routing*, not caching; distinct feature; dismissed.
  - `docs-litellm-a2a-iteration-budgets.md` — A2A agent-loop cost caps; dismissed.
  - `docs-litellm-helicone-integration.md` — observability integration; caching only re-implemented at the vendor boundary in its Claim 3; tangential; dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent spectrum/guardrails; dismissed.
  - `blog-litellm-save-claude-code-costs.md` — cited above (provider-prompt-cache layer, distinct tier).
  - `blog-litellm-valkey-semantic-caching.md` — cited above (primary overlap, Extends/Corroborates).
  - Additional cross-refs found by searching `source-notes/` per triage guidance: `failure-litellm-httpx-cache-eviction.md`, `failure-litellm-bedrock-invoke-prompt-cache.md`, `docs-promptfoo-configuration-caching.md`, `blog-litellm-redis-circuit-breaker.md` — all verified per MINER.md §4b before citation.