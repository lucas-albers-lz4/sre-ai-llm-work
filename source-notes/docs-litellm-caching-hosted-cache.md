---
source_url: https://docs.litellm.ai/docs/caching/caching_api
source_type: docs
title: "Hosted Cache - api.litellm.ai | LiteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation (no byline or date)"
date_published: unknown (living vendor docs; current as of 2026-09-23)
date_extracted: 2026-09-23
last_checked: 2026-09-23
status: current
confidence_overall: emerging
issue: "#1432"
---

# LiteLLM Hosted Cache — `Cache(type="hosted")` via api.litellm.ai

> LiteLLM's vendor-hosted response-cache tier: `Cache(type="hosted")` backs
> `completion()` and `embedding()` caching with `api.litellm.ai` instead of a
> self-operated store — but the page is a three-snippet quick-start that
> documents no TTL, no invalidation, no residency/retention contract, and (on
> the streaming path) only an asynchronous cache write, not read-your-writes.

## Source Context

- **Type**: docs — LiteLLM SDK caching quick-start page (`/docs/caching/caching_api`), "Hosted Cache - api.litellm.ai", one page of the LiteLLM Python SDK configuration tree on `docs.litellm.ai`, rendered by Docusaurus. No byline, no publication date, no version pinning.
- **Author credibility**: First-party vendor documentation for LiteLLM (BerriAI), a widely used open-source LLM gateway/SDK. Authoritative on **that the hosted-cache mode exists and how the sample is written**, not on production behavior — the page reports no TTL, no hit-rate/latency/cost figures, no failure modes, and no data-handling or retention statement.
- **Scope**: Three headed sections, each a single code block: Quick Start (completion), Embedding(), and Caching with Streaming, plus an Enterprise upsell footer. Does NOT cover the cache configuration surface (backends matrix, init parameters, `semantic_cache_scope`, `supported_call_types`, TTL knobs) — that lives on the sibling page `/docs/caching/all_caches` (mined as `docs-litellm-caching-all-caches.md`, #1431). Does NOT cover provider-side prompt caching (linked out) or self-hosted semantic caching (`blog-litellm-valkey-semantic-caching.md`).

## Extracted Claims

### Claim 1: LiteLLM ships a vendor-hosted response-cache mode — `litellm.cache = Cache(type="hosted")` backs `completion()` and `embedding()` caching with `api.litellm.ai` rather than a store the operator operates
- **Evidence**: Page subtitle plus all three code blocks initialize the cache with `Cache(type="hosted")` and the inline comment naming the hosted service.
- **Confidence**: settled (documented vendor product behavior with a runnable snippet)
- **Quote**: "Use api.litellm.ai for caching `completion()` and `embedding()` responses"
- **Quote**: "litellm.cache = Cache(type=\"hosted\") # init cache to use api.litellm.ai"
- **Our assessment**: The placement fact is documented: the cache backend is the vendor's hosted service, so prompt and response bodies are stored by the vendor rather than in the operator's own Redis/in-memory store. What the page documents only [editorial] — it states *no* residency control, no opt-out, no retention, no encryption, and no tenancy statement, so the boundary/data-egress consequences are inferred from the architecture and must not be attributed to this page. For a team that chose self-hosted caching specifically to keep payloads in-boundary, this mode is a silent egress path the page documents by omission (see Claim 4).

### Claim 2: `caching=True` is a per-call opt-in on both `completion()` and `embedding()`, and an identical second call is returned from cache
- **Evidence**: Quick Start and Embedding sections both pass `caching=True` per call; the completion sample's trailing comment states the second call is a cache hit; the embedding sample times both calls.
- **Confidence**: settled (documented, reproducible)
- **Quote**: "# response1 == response2, response 1 is cached"
- **Our assessment**: Confirms the hosted tier follows the same per-call opt-in shape as LiteLLM's other cache backends — consistent with the `supported_call_types` allow-list on the all_caches page (`docs-litellm-caching-all-caches.md` Claim 2), which defaults to including completion and embedding. The embedding sample's timing instrumentation shows the intended cost/latency signal (cache hit is faster), but the page prints no measured values, so no numbers are extractable.

### Claim 3: Streamed responses are cacheable on the hosted tier, but the cache entry is written asynchronously after the stream — an immediately re-sent identical request may not hit
- **Evidence**: The "Caching with Streaming" section ("LiteLLM can cache your streamed responses for you") shows two identical `stream=True, caching=True` calls separated by `time.sleep(1)` with an inline comment stating the cache update is async.
- **Confidence**: settled (vendor-stated behavior with a runnable snippet; the async window itself is unquantified)
- **Quote**: "time.sleep(1) # cache is updated asynchronously"
- **Our assessment**: This is the read-your-writes gap on the streaming path: `caching=True` on a stream does not give write-then-immediately-read consistency, and an immediate re-read can miss and re-bill. It is a timing-dependence the corpus's other caching notes are not about — the eval-cache replay hazards (`docs-promptfoo-configuration-caching.md`) come from a *stale* entry persisting; this is a *write that has not landed yet*. A hit-rate or cost measurement taken right after the first streamed call measures the write race, not the cache — same family as the guide's "a flake rate computed on a warm cache measures replay" rule, but on the gateway response-cache side.

### Claim 4: The page documents no cache lifecycle or governance contract for the hosted tier — no TTL, no eviction/invalidation behavior, no failure semantics, no observability, and no statement about what the vendor retains
- **Evidence**: Full-page read: three `<h2>` sections, three code blocks, one enterprise upsell footer. Zero configuration parameters, zero prose sections, zero tables beyond the doc index.
- **Confidence**: settled (a factual statement about the page's content, checkable against the page)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The documented-absence is the operational point for the corpus: a vendor quick-start asserts `Cache(type="hosted")` "works" (and caches streams asynchronously) while defining no retention, no expiry, no invalidation, and no failure behavior. Every design decision about what the vendor keeps and for how long is therefore unreviewed by the source; guidance built on it must stay "verify with the vendor," not "the docs guarantee X." Note the sibling all_caches backend matrix (`docs-litellm-caching-all-caches.md` Claim 1) also does not list `hosted` among its nine backends — so the hosted tier's config surface is documented *nowhere* in the corpus to date.

## Concrete Artifacts

All three code blocks verbatim from the page (the entire technical surface; newlines restored at the statement level).

### Quick Start Usage - Completion (source: https://docs.litellm.ai/docs/caching/caching_api)

```python
import litellm
from litellm import completion
from litellm.caching.caching import Cache
litellm.cache = Cache(type="hosted") # init cache to use api.litellm.ai

# Make completion calls
response1 = completion(
    model="gpt-5.6-luna", 
    messages=[{"role": "user", "content": "Tell me a joke."}],
    caching=True
)

response2 = completion(
    model="gpt-5.6-luna", 
    messages=[{"role": "user", "content": "Tell me a joke."}],
    caching=True
)
# response1 == response2, response 1 is cached
```

### Usage - Embedding() (source: https://docs.litellm.ai/docs/caching/caching_api)

```python
import time
import litellm
from litellm import completion, embedding
from litellm.caching.caching import Cache
litellm.cache = Cache(type="hosted")

start_time = time.time()
embedding1 = embedding(model="text-embedding-ada-002", input=["hello from litellm"*5], caching=True)
end_time = time.time()
print(f"Embedding 1 response time: {end_time - start_time} seconds")

start_time = time.time()
embedding2 = embedding(model="text-embedding-ada-002", input=["hello from litellm"*5], caching=True)
end_time = time.time()
print(f"Embedding 2 response time: {end_time - start_time} seconds")
```

### Caching with Streaming → Usage (source: https://docs.litellm.ai/docs/caching/caching_api)

```python
import litellm
import time
from litellm import completion
from litellm.caching.caching import Cache

litellm.cache = Cache(type="hosted")

# Make completion calls
response1 = completion(
    model="gpt-5.6-luna", 
    messages=[{"role": "user", "content": "Tell me a joke."}], 
    stream=True,
    caching=True)
for chunk in response1:
    print(chunk)

time.sleep(1) # cache is updated asynchronously

response2 = completion(
    model="gpt-5.6-luna", 
    messages=[{"role": "user", "content": "Tell me a joke."}], 
    stream=True,
    caching=True)
for chunk in response2:
    print(chunk)
```

The surrounding prose is minimal: intro sentence "Use api.litellm.ai for caching `completion()` and `embedding()` responses"; streaming section intro "LiteLLM can cache your streamed responses for you"; footer is LiteLLM Enterprise SSO/SAML/spend-tracking marketing (no technical content).

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-caching-all-caches.md` **Claim 2** ("`Cache.__init__` restricts `type` to a literal enum defaulting to `local`, and `supported_call_types` is an allow-list defaulting to `[\"completion\", \"acompletion\", \"embedding\", ...]`") — this page's per-call `caching=True` on `completion()` and `embedding()` (Claim 2) is consistent with those call types sitting inside the all_caches allow-list; the two pages describe the same opt-in shape for the same call types. (Verified: #1431 Claim 2.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 8** (per-repeat cache namespaces make a flake rate on a warm cache measure replay rather than model variance) — the streaming async-write here (Claim 3) is the same "cache timing changes what a measurement means" hazard on the gateway response-cache side: an immediate post-stream measurement observes the write race, not the cache. (Verified: #1275 Claim 8.)

- **Contradicts**: None. Verified against `CONTRADICTIONS.md` (no open `C-NNN` entries) and all corpus notes. The hosted tier is additive placement, not a dispute: no existing note claims LiteLLM has no vendor-hosted cache option, and the async-streaming caveat opposes no existing cache behavior claim. No contradiction issue filed.

- **Extends**:
  - `source-notes/docs-litellm-caching-all-caches.md` **Claim 1** (the nine-backend response-cache matrix: `local`, `disk`, `redis`, `s3`, `gcs`, `azure-blob`, `redis-semantic`, `qdrant-semantic`, `valkey-semantic`) — `type="hosted"` is a backend absent from that matrix; this page adds the tenth placement (vendor-hosted) to the sibling's backend picture, and the two should be read as one cache-tier story. (Verified: #1431 Claim 1.)
  - `source-notes/blog-litellm-valkey-semantic-caching.md` **Claim 1** ("LiteLLM now supports semantic prompt caching on Valkey via a new `cache_params.type: valkey-semantic` backend") — the hosted tier is the other side of the placement decision the semantic-caching note opens: a store you operate (`valkey-semantic` on your Valkey/ElastiCache) vs a vendor-hosted service (`type="hosted"` at `api.litellm.ai`). Distinct mechanisms, same decision axis (where do cached payloads live). (Verified: #1176 Claim 1.)
  - `source-notes/failure-litellm-httpx-cache-eviction.md` **Claim 1** ("A cache-eviction cleanup method that indiscriminately closes cached objects can destroy shared references still in active use") — the corpus's other LiteLLM cache-reliability failure, but on the *client* cache (`LLMClientCache`, 200-entry/10-min TTL). This page's hosted response cache is a different object whose lifecycle/eviction contract is undocumented (Claim 4), so the incident's fixed eviction policy neither covers nor contradicts it. (Verified: #461 Claim 1.)
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 1** ("A gateway request-translation change that keeps payloads semantically equivalent can still silently destroy a provider's prefix-based prompt cache") — provider-side prompt caching, a third distinct tier; gateway response caching (this page) and provider prompt caching must stay distinct in the guide. Both cache types matter to cost, and both can be invisible to correctness checks. (Verified: #697 Claim 1.)
  - `source-notes/blog-litellm-save-claude-code-costs.md` **Claim 3** (LiteLLM auto-injects `cache_control` markers enabling Claude's provider prompt cache) — another caching tier whose data placement is not the operator's self-operated store; distinct from the hosted *response* cache (provider-prompt-cache vs vendor-hosted-response-cache). (Verified: #668 Claim 3.)

- **Novel** (new to the corpus):
  - **`Cache(type="hosted")` as a vendor-hosted response-cache placement** — the first corpus source naming a LiteLLM cache backend operated by the vendor (`api.litellm.ai`) rather than a self-operated or purely in-process store; `grep -rin "hosted" source-notes/ guide/` has no cache-related hit prior to this note.
  - **The asynchronous cache write on the streaming path** — a correctness limit on `caching=True` that is not stale-data or eviction but "the write has not landed yet"; an immediate repeated streamed request can miss and re-bill. No other note in the corpus frames a cache failure this way.
  - **The documented non-contract** — a vendor cache tier whose page defines no TTL/eviction/retention/residency surface (Claim 4), which the guide currently has no framework for treating as a governance decision.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: (a) In the "Semantic caching" section (~lines 1073-1107, sourced from `blog-litellm-valkey-semantic-caching` and `docs-litellm-caching-all-caches`), add the hosted tier as a *separate placement* from the self-operated Valkey/store semantic tier: `Cache(type="hosted")` = the vendor's api.litellm.ai service, documented with no TTL, no invalidation, and no residency contract. (b) Extend the "Cache is a cost control, not a correctness control" rule (~lines 597-599, from `docs-promptfoo-configuration-caching`): on LiteLLM's streaming path, `caching=True` does not even give read-your-writes — the entry is written asynchronously, so an immediate same-request re-read can miss and re-bill, and a hit-rate/cost sample taken right after a streamed call measures the write race. Recommend treating gateway cache-hit telemetry (e.g. `kwarg["cache_hit"]` from `docs-litellm-caching-all-caches` Claim 6) as time-valid only after the async write lands.

- **Chapter 06 (Security and Trust)**: Add "cache placement is an egress/residency decision" where the guide discusses where prompt/response payloads live: `Cache(type="hosted")` stores prompt and response bodies at `api.litellm.ai` (vendor-side). For a team that chose self-hosted caching to keep payloads in-boundary, switching the `Cache(...)` type is a silent egress path. Because the source states no residency, retention, encryption, or tenancy control, the guidance must be "verify data handling with the vendor," not "the docs guarantee X." Cite this note for the placement fact and its documented absence of a governance contract.

- **Chapter 02 (Observability)**: Where Ch02 treats cache hit/miss as a reliability signal, note that on LiteLLM's streaming path the hit condition is timing-dependent (async write) — record whether a hit was observed immediately post-stream or later; a hit-rate graph spanning a stream burst can be dominated by the write race rather than the cache.

## Extraction Notes

- Source read in full via direct HTTP fetch (39.6 KB HTML, 28.1 KB article); the page is three code blocks and three headings, plus the Enterprise footer, which was skipped per the site-crawl seed's scope (skip marketing/pricing). No substantive sub-pages are linked; the sibling config page (`/docs/caching/all_caches`) was not re-mined here (see below).
- Per the Prospector triage (#1432, three triage passes agreeing): keep extraction to (1) the hosted-cache mode as a placement/egress decision, (2) the async-write-on-streaming caveat, (3) the per-call opt-in shape, and (4) what the page does *not* document. Deliberately NOT mined: the cache configuration surface (`supported_call_types`, `semantic_cache_scope`, backends matrix, TTL knobs, `cache_hit` hook) — that lives on the sibling `/docs/caching/all_caches` page, already mined as `docs-litellm-caching-all-caches.md` (#1431, PR #1437 merged).
- `confidence_overall` is `emerging`: the extraction claims are documented product surface (settled individually), but the page is an undated, unversioned vendor quick-start with no TTL, no failure detail, no measured numbers, and no residency statement — it is not evidence about behavior under load or failure, and vendor-authored quick-starts can drift from shipped behavior. Code samples (`gpt-5.6-luna`, `text-embedding-ada-002`, `["hello from litellm"*5]`) are treated as illustrative only.
- All `Quote` fields verified character-for-character against the fetched raw HTML (quotes in the Concrete Artifacts section are the code blocks as rendered; newlines restored at the statement level only). Claim 4 has no quote because its content is a documented *absence*.
- **Candidate dismissal** (from `miner-related-notes.md`, read before Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `docs-litellm-batches-api.md` — batch input-file rate limiting; different subsystem, no response-cache surface; dismissed.
  - `docs-litellm-bedrock-invoke.md` / `docs-litellm-bedrock-converse.md` — native Bedrock passthrough routing/auth; no cache surface; dismissed.
  - `docs-litellm-a2a-iteration-budgets.md` / `docs-litellm-a2a-cost-tracking.md` — A2A agent-loop cost caps and per-agent cost attribution; no cache surface; dismissed.
  - `docs-litellm-audio-transcription.md` — transcription fallbacks/`mock_testing_fallbacks`; dismissed.
  - `docs-litellm-helicone-integration.md` — observability integration; its Claim 3 notes caching re-implemented at the Helicone vendor boundary, a different vendor boundary than the hosted cache here; tangential, dismissed.
  - `blog-litellm-auto-router-v2.md` — complexity/semantic/adaptive *routing*, not caching; distinct feature (same category-error caution as semantic routing vs semantic caching); dismissed.
  - `blog-litellm-save-claude-code-costs.md` — cited above (provider prompt-cache tier, distinct from the hosted response cache).
  - `blog-litellm-valkey-semantic-caching.md` — cited above (self-hosted semantic tier, the placement alternative to `type="hosted"`).
  - Additional cross-refs found by searching `source-notes/` per triage guidance: `docs-litellm-caching-all-caches.md` (primary sibling), `docs-promptfoo-configuration-caching.md`, `failure-litellm-httpx-cache-eviction.md`, `failure-litellm-bedrock-invoke-prompt-cache.md` — all re-read and verified per MINER.md §4b before citation.
- No contradiction issue filed: no claim here opposes an existing note, and `CONTRADICTIONS.md` has no open `C-NNN` entries. The closest surfaces (semantic tier in #1176/#1431, eval-cache replay in #1275, cache failures in #461/#697) are distinct mechanisms or placements, not disagreements.