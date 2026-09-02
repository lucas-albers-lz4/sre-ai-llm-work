---
source_url: https://docs.litellm.ai/blog/valkey_semantic_caching
source_type: blog-post
title: "Semantic Caching on Valkey and AWS ElastiCache"
author: "Yassin Kortam (Senior SWE, LiteLLM)"
date_published: 2026-06-17
date_extracted: 2026-09-02
last_checked: 2026-09-02
status: current
confidence_overall: emerging
issue: "#1176"
---

# Semantic Caching on Valkey and AWS ElastiCache

> LiteLLM's new `cache_params.type: valkey-semantic` backend enables embedding-based (semantic) prompt caching against a Valkey cluster running the valkey-search module — including AWS ElastiCache for Valkey — with no Redis Stack, RediSearch, RedisVL, or Qdrant in the path; it builds its own HNSW vector index plus a per-request tag field and returns a cache hit when cosine similarity clears a configurable threshold.

## Source Context

- **Type**: blog-post — LiteLLM vendor engineering/feature post on `docs.litellm.ai/blog`, tagged `caching`, `valkey`, `elasticache`, `semantic cache`. Published June 17, 2026. Identified via a one-post Docusaurus tag-index page (`/blog/tags/semantic-cache`) that resolves to this single article.
- **Author credibility**: Yassin Kortam is a Senior SWE at LiteLLM (BerriAI), the vendor behind the open-source LLM gateway/proxy described. Claims about how the `valkey-semantic` feature behaves are authoritative for LiteLLM product behavior. The config snippets are concrete and reproducible. The post is short, vendor-authored, and does not provide independent benchmarks or measured cache-hit-rate/latency/cost figures, so outcome claims are limited.
- **Scope**: Covers (1) the reason the semantic cache moved from RedisVL/RediSearch to a Valkey backend, (2) how the `valkey-semantic` backend works (vector index, tag field, KNN + threshold), (3) connection/env-var resolution, (4) a `config.yaml` example and docker test image. Does NOT cover: measured performance/cost data, cache invalidation/eviction behavior, failure modes, or comparison with exact-match (token/prefix) prompt caching in depth.

## Extracted Claims

### Claim 1: LiteLLM now supports semantic prompt caching on Valkey via a new `cache_params.type: valkey-semantic` backend, giving embedding-based cache hits without Redis Stack or a separate vector database
- **Evidence**: The opening statement introduces the backend and the direct configuration value.
- **Confidence**: settled (documented shipped feature with a concrete config surface)
- **Quote**: "LiteLLM now supports semantic prompt caching on Valkey. If you run a Valkey cluster with the valkey-search module, including AWS ElastiCache for Valkey, you can point LiteLLM at it with `type: valkey-semantic` and get embedding-based cache hits without standing up Redis Stack or a separate vector database."
- **Our assessment**: A concrete shipped feature with a named config type. The key operational value is removing the separate-vector-database requirement that previously accompanied semantic caching. Settled as a description of LiteLLM product behavior, verifiable from the config and open-source codebase.

### Claim 2: Semantic caching stores responses by prompt meaning rather than exact string match, so a reworded request can still hit the cache and skip a paid model call
- **Evidence**: The "Why this matters" section states the mechanism and its purpose directly.
- **Confidence**: settled (definitional statement of the caching model)
- **Quote**: "Semantic caching stores responses by the meaning of a prompt rather than an exact string match, so a reworded request can still hit the cache and skip a paid model call."
- **Our assessment**: A clean definition that distinguishes semantic (meaning-similarity) from exact/prefix-match caching. This is the correctness-relevant framing for the guide: a semantic hit is a *similarity* decision, not an identity one, which is exactly where scope/correctness risk lives.

### Claim 3: LiteLLM's previous semantic cache required RedisVL, which depends on RediSearch's `FT.*` vector API — unavailable on Redis OSS or ElastiCache for Redis OSS, forcing teams to stand up Redis Stack or Qdrant just for semantic caching
- **Evidence**: The "Why this matters" section describes the prior dependency chain and its availability limits.
- **Confidence**: settled (historical description of the prior RedisVL/RediSearch path)
- **Quote**: "Until now LiteLLM's semantic cache was built on RedisVL, which depends on RediSearch's `FT.*` vector API. RediSearch is not available on Redis OSS or on ElastiCache for Redis OSS, which left teams standing up Redis Stack or Qdrant just to get semantic caching."
- **Our assessment**: Explains the infrastructure burden of the prior approach — RediSearch availability forced a separate vector-capable store. This is the operational motivation for the new backend.

### Claim 4: The migration driver is Redis moving to a source-available license — more teams are standing up Valkey instead, and ElastiCache for Valkey is a common managed target
- **Evidence**: The "Why this matters" section ties the new backend to the Redis licensing shift.
- **Confidence**: emerging (the licensing fact is settled; the "more teams" adoption claim is directional/inferred)
- **Quote**: "With Redis moving to a source-available license, more teams are standing up Valkey instead, and ElastiCache for Valkey is a common managed target."
- **Our assessment**: The licensing shift is a real, widely reported industry driver. The adoption claim ("more teams") is a reasonable inference by the vendor, not measured. This is a concrete instance of a cache-tier selection decision point driven by Redis licensing → Valkey movement.

### Claim 5: Valkey provides vector search through the valkey-search module, exposed by ElastiCache for Valkey, and the new backend talks to it directly over the Redis protocol — so semantic caching on ElastiCache for Valkey works without RediSearch, Redis Stack, or Qdrant in the path
- **Evidence**: The "Why this matters" section describes the module and the direct-protocol talk.
- **Confidence**: settled (feature-availability and protocol statements)
- **Quote**: "Valkey ships vector search through the valkey-search module, and ElastiCache for Valkey exposes it. LiteLLM's new backend talks to valkey-search directly over the Redis protocol, so semantic caching on ElastiCache for Valkey works without RediSearch, Redis Stack, or Qdrant in the path."
- **Our assessment**: The core architecture claim — a managed Valkey offering is sufficient for semantic caching with no auxiliary vector store. This is the main operational takeaway for teams on ElastiCache.

### Claim 6: The `valkey-semantic` backend builds its own vector index from valkey-search field types — a tag field that isolates each cache key's scope plus an HNSW vector field for the prompt embedding — then runs a KNN query at lookup time and returns the cached response when cosine similarity clears a configurable threshold
- **Evidence**: The "How it works" section describes the index construction and lookup mechanism.
- **Confidence**: emerging (mechanism described by the vendor; no code shown in the post to verify exact field construction)
- **Quote**: "The `valkey-semantic` backend builds its own vector index from the field types valkey-search supports, a tag field that isolates each cache key's scope and an HNSW vector field for the prompt embedding, then runs a KNN query at lookup time and returns the cached response when the cosine similarity clears your threshold."
- **Our assessment**: This is the mechanism detail the Prospector asked for. The tag field provides per-request scope isolation; the HNSW vector field holds the embedding; lookup is a KNN search gated on a cosine threshold. The correctness/poisoning risk lives in the threshold — a too-low threshold returns a semantically-neighboring but not-equal response. Emerging because the post states the mechanism without showing the code.

### Claim 7: Prompt extraction, embedding generation, and response handling are shared with the existing Redis semantic cache, so behavior matches the Redis path including per-request scope isolation
- **Evidence**: The "How it works" section states the shared pipeline explicitly.
- **Confidence**: emerging (vendor statement about shared behavior; no code diff shown)
- **Quote**: "Prompt extraction, embedding generation, and response handling are shared with the existing Redis semantic cache, so behavior matches the Redis path including per-request scope isolation."
- **Our assessment**: Means the semantic-cache correctness semantics (scope isolation, embedding behavior) are inherited from the established Redis backend rather than reimplemented — a reuse claim that reduces new-surface risk. Useful context but not independently verifiable from this short post.

### Claim 8: Connections resolve from `VALKEY_HOST`, `VALKEY_PORT`, and `VALKEY_PASSWORD`, falling back to the `REDIS_*` equivalents, and passwordless clusters are supported for IAM or no-auth setups
- **Evidence**: The "How it works" section enumerates the env-var resolution and the passwordless case.
- **Confidence**: settled (documented config behavior)
- **Quote**: "Connections resolve from `VALKEY_HOST`, `VALKEY_PORT`, and `VALKEY_PASSWORD`, falling back to the `REDIS_*` equivalents, and passwordless clusters are supported for IAM or no-auth setups."
- **Our assessment**: A concrete operational detail: the `REDIS_*` fallback means existing Redis configs keep working with a minimal rename, and IAM/auth-less ElastiCache endpoints are supported. Directly actionable for cache tier selection.

### Claim 9: For ElastiCache with encryption in transit, you pass a `rediss://` URL through `cache_params.redis_url` instead of host and port
- **Evidence**: The "Get started" section states the TLS-encrypted connection path.
- **Confidence**: settled (documented config behavior)
- **Quote**: "For ElastiCache with encryption in transit, pass a `rediss://` URL through `cache_params.redis_url` instead of host and port."
- **Our assessment**: A specific operational requirement — transit-encrypted ElastiCache connections use the `rediss://` (TLS) scheme via `redis_url`. Captures a real constraint for managed Valkey deployments where encryption-in-transit is on by default.

### Claim 10: To try valkey-search locally, the bundled Docker image with the module ready is `valkey/valkey-bundle:8.1`
- **Evidence**: The "Get started" section provides the docker run command.
- **Confidence**: settled (stated image reference)
- **Quote**: "To try valkey-search locally, the bundled image has the module ready: `docker run -d -p 6379:6379 valkey/valkey-bundle:8.1`"
- **Our assessment**: A reproducible local-testing entry point. The image tag (`valkey-bundle:8.1`) is the concrete artifact an operator needs to evaluate the feature before standing up ElastiCache.

## Concrete Artifacts

### `valkey-semantic` cache config (verbatim from the article's "Get started" section)

```yaml
litellm_settings:
  cache: True
  cache_params:
    type: valkey-semantic
    host: os.environ/VALKEY_HOST
    port: os.environ/VALKEY_PORT
    valkey_semantic_cache_embedding_model: openai-embedding
    similarity_threshold: 0.8
```

### Local valkey-search test image (verbatim from the article's "Get started" section)

```bash
docker run -d -p 6379:6379 valkey/valkey-bundle:8.1
```

Source for both artifacts: https://docs.litellm.ai/blog/valkey_semantic_caching — "Get started" section.

## Cross-References

- **Corroborates**:
  - `blog-litellm-redis-circuit-breaker.md` **Claim 1** — Redis sits in the LiteLLM gateway hot path for cache lookups and spend tracking. This source adds a new cache-backend type that still routes through the same Redis-protocol key/value store family (Valkey), so the hot-path dependency framing holds for Valkey-managed caching too. Not a direct corroboration of the same claim, but shared infrastructure context.
  - `blog-litellm-save-claude-code-costs.md` — That note covers cost-reduction levers including proxy-side prompt caching; this source is a different cache mechanism (semantic meaning-match response cache on Valkey) aimed at the same goal of skipping paid model calls. Consistent cost-reduction theme, distinct mechanism.

- **Contradicts**: None identified. Verified against all existing source notes and `CONTRADICTIONS.md` (no open `C-NNN` entries). No existing note claims semantic caching is impossible without RedisVL/Redis Stack/Qdrant, or that Valkey is unsupported for LiteLLM caching. The overlap with `blog-litellm-auto-router-v2.md` (LiteLLM *semantic routing*) is a distinct feature — this post is about *semantic caching*, and the Prospector explicitly noted not to conflate the two, which would not be a contradiction but a category error. No contradiction issue filed.

- **Extends**:
  - `blog-litellm-redis-circuit-breaker.md` — Extends LiteLLM's Redis-dependency coverage (resilience under Redis degradation) into a second dimension: choosing the Redis-protocol store (Valkey vs. Redis vs. ElastiCache) for a specific caching purpose (semantic). The circuit-breaker note covers keeping the gateway up when the store degrades; this note covers which store to point it at and how.
  - `failure-litellm-bedrock-invoke-prompt-cache.md` — That incident covers a *provider-side* prompt-cache being silently destroyed; this source covers LiteLLM's own response-cache backend options. Both concern prompt/caching reliability through LiteLLM but on different layers (provider cache vs. gateway cache), so this note extends the caching-reliability theme without overlapping the failure mechanism.
  - `failure-litellm-httpx-cache-eviction.md` — Both concern LiteLLM's caching layer. The failure note covers a cache-eviction lifecycle bug in LiteLLM's own client cache; this source covers a cache *backend selection* for semantic responses. The Prospector flagged this as a cross-check; the mechanisms do not overlap (client-cache eviction vs. response-cache backend), so this is thematic adjacency, not coverage of the same behavior.

- **Novel** (new to the corpus):
  - **Semantic caching as a response-cache tier** — embedding-based (meaning-similarity) cache hits on a gateway, distinct from the exact/prefix-match and token/context caching already covered (prompt caching in `blog-litellm-save-claude-code-costs.md` Claim 3, prefix-cache incident in `failure-litellm-bedrock-invoke-prompt-cache.md`). No existing note covers semantic response caching.
  - **The `valkey-semantic` backend specifically** — `cache_params.type: valkey-semantic` with `similarity_threshold`, `valkey_semantic_cache_embedding_model`, and the `VALKEY_*`/`REDIS_*` env fallback.
  - **Valkey and ElastiCache for Valkey as a managed cache tier** — first corpus mention of Valkey as a Redis-protocol store for LLM caching, including the `rediss://` TLS requirement for transit-encrypted ElastiCache and the `valkey-search` module path. The Redis-licensing → Valkey driver (Claim 4) is also new to the corpus.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — caching / cost-latency)**: Add a **semantic caching** pattern distinct from prompt caching: an embedding-similarity response cache (LiteLLM `cache_params.type: valkey-semantic`) that returns a cached response when cosine similarity clears a threshold (default `0.8`), enabling reworded requests to skip paid model calls. Add the `similarity_threshold` as the key correctness/poisoning risk knob — a lower threshold trades hit rate against the risk of returning a semantically-neighboring-but-not-equal response (per-request scope isolation via the tag field is the mitigation the vendor describes). Add the cache-tier selection decision: the Redis-licensing → Valkey driver and the fact that Valkey + `valkey-search` (incl. ElastiCache for Valkey) removes the need for Redis Stack/Qdrant for semantic caching; note the `rediss://` TLS requirement for transit-encrypted ElastiCache and the `VALKEY_*`/`REDIS_*` env fallback for config reuse.

- **Chapter 05 (LLM Ops Reliability — resilience/dependency patterns)**: Extend the existing Redis hot-path dependency guidance (already citing the circuit-breaker note) to note that a Valkey-managed cache (ElastiCache for Valkey) is a supported drop-in for LiteLLM's caching and carries the same hot-path dependency concerns — the circuit-breaker resilience framing applies equally to a Valkey-backed cache tier.

## Extraction Notes

- Source read in full via HTTP (Docusaurus blog page). The submitted issue URL (`/blog/tags/semantic-cache`) is a one-post tag index; per the Prospector triage, extraction was done from the underlying article `https://docs.litellm.ai/blog/valkey_semantic_caching`, confirmed as the single post the tag page resolves to. All quotes and config artifacts copied character-for-character from the rendered article.
- `confidence_overall` is `emerging`: the config surface, env-var resolution, `rediss://` requirement, and docker image (Claims 1, 3, 5, 8, 9, 10) are settled documented product behavior verifiable against the open-source codebase. The mechanism claims (Claims 6, 7) are vendor-described without code shown in this post. The license/adoption driver (Claim 4) is partially inferred. The post reports **no measured cache-hit-rate, latency, or cost figures**, so there are no operational outcome numbers to extract — the Prospector noted to capture any such figures, but the article provides none.
- The post is short (~4 paragraphs plus config). That is the full extent of the source; the adjacent caching-docs link (`/docs/proxy/caching`) was not followed because it is a general docs page, not a sub-page of this feature post, and the tag page contains exactly one post.
- **Candidate dismissal** (from `miner-related-notes.md`): all 10 lexical candidates were reviewed; the two relevant-to-this-topic LiteLLM candidates are cited above (`blog-litellm-redis-circuit-breaker.md`, `blog-litellm-save-claude-code-costs.md`). The remainder are dismissed as unrelated: `blog-litellm-auto-router-v2.md` (semantic *routing* — distinct feature, do not conflate; see Contradicts), `docs-google-sre-prodcast-04-09-ai-agents.md` (agent spectrum/guardrails), `docs-langfuse-mcp-server.md` (unrelated vendor), `docs-google-sre-eliminating-toil.md` (toil measurement), `docs-datadog-llm-observability.md` (LLM observability), `docs-langfuse-security-and-guardrails.md` (scanning), `docs-google-sre-data-processing-pipelines.md` (pipeline SLOs), `docs-google-sre-reliable-product-launches.md` (launch process), `docs-google-sre-prodcast-04-05-furino-slos.md` (SLOs). In addition, the Prospector's triage named `failure-litellm-bedrock-invoke-prompt-cache.md` and `failure-litellm-httpx-cache-eviction.md`, both read in full and cited above as Extends / thematic adjacency.
- No contradiction issue filed: no existing source note opposes any claim here, and `CONTRADICTIONS.md` has no relevant open entries. The semantic-routing vs. semantic-caching distinction flagged by the Prospector is a category difference, not a contradiction.
