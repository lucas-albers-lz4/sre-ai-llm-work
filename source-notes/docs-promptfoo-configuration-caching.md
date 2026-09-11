---
source_url: https://www.promptfoo.dev/docs/configuration/caching/
source_type: docs
title: "Promptfoo Configuration: Caching — Runtime"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-11
date_extracted: 2026-09-11
last_checked: 2026-09-11
status: current
confidence_overall: emerging
issue: "#1275"
---

# Promptfoo Configuration: Caching

> The vendor reference for promptfoo's client-side eval-result response
> cache — the correctness trap that governs whether a green LLM regression
> gate is real: disk-based storage at `~/.promptfoo/cache`, provider-scoped
> composite cache keys whose formats are versioned implementation details,
> a 14-day default TTL (memory under `NODE_ENV=test`), errors and empty
> responses never cached, and per-repeat-index cache namespaces that make
> `--no-cache` + `--repeat` the only way to get every run fresh.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo configuration reference, "Runtime > Caching" page)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team
  vendor (now part of OpenAI per the site banner). First-party
  documentation of the tool's own caching behavior — authoritative for
  promptfoo product behavior, but vendor-positioned: the page reports no
  measured cache-hit-rate, latency, or cost figures, and there is no
  independent validation of the operational claims. The env-var defaults
  and config surface are directly checkable against an installed CLI.
- **Scope**: Covers how the eval-result cache works (composite cache keys,
  caching behavior with TTL/invalidation), the CLI and Node-package
  cache-disable surface, the CI/test-framework recommendation, the env-var
  configuration table, throttling/retry semantics alongside caching, and
  cache clearing/cache-busting. Does NOT cover the LiteLLM gateway/proxy
  cache layer, provider-side prompt caching, or red-team configuration
  (covered by other notes).
- **Last updated**: Sep 11, 2026 by renovate[bot]; page is undated, but the
  documented key-format examples describe the current `gpt-5` era.

## Extracted Claims

### Claim 1: promptfoo caches LLM provider API results by default on disk at `~/.promptfoo/cache`, managed by `cache-manager` with `keyv` and `keyv-file`
- **Evidence**: The page's opening paragraph and the "How Caching Works" intro describe the stack and default storage.
- **Confidence**: settled (documented product behavior; the default path and dependency stack are checkable)
- **Quote**: "promptfoo caches the results of API calls to LLM providers to help save time and cost." and "The cache is managed by `cache-manager` with `keyv` and `keyv-file` for disk-based storage. By default, promptfoo uses disk-based storage (`~/.promptfoo/cache`)."
- **Our assessment**: Buy it as a product fact. This is the base contract: caching is on by default and is a disk-backed client-side memoisation of eval results. The operational consequence (a "save time and cost" feature silently changing what a later eval run observes) is developed in the claims below.

### Claim 2: Cache entries are keyed by provider-scoped composite keys — provider identifier, a deterministic digest of prompt/request content, provider configuration, and context variables — and sensitive request payloads and headers are hashed rather than embedded
- **Evidence**: The "Cache Keys" section lists the four composite-key components and the hashing statement, then gives the two example key formats.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Cache entries are stored using provider-specific composite keys that include: Provider identifier; Prompt or request content, often represented as a deterministic digest; Provider configuration; Context variables (when applicable)"
- **Our assessment**: Buy it. The composite key is what makes the cache memoise at request granularity rather than prompt granularity — a config change or a different context variable changes the bucket. The hashing of sensitive payloads/headers is the security-relevant detail: request bodies do not get embedded verbatim into cache keys on disk.

### Claim 3: Cache key formats are versioned implementation details that may change between versions, so a key-format bump silently invalidates prior cached entries
- **Evidence**: The "Cache Keys" section caveat directly precedes the example key formats (`openai:gpt-5:<request-digest>`, `fetch:v3:<request-digest>`).
- **Confidence**: settled (documented product behavior — the vendor's own caveat)
- **Quote**: "Cache key formats are implementation details and may change between versions."
- **Our assessment**: Buy it, and it is an important reliability caveat: cache reuse is explicitly **not** a stable contract. A promptfoo upgrade that changes the key format silently empties the cache (a cost spike, not a correctness break) — and conversely, teams should not assume a warm cache from one version is evidencing anything in the next. The versioned `fetch:v3` format prefix shows this is a designed-for pattern, not an accident.

### Claim 4: Cached entries expire by TTL (default 14 days) or manual clearing only — cached responses can be replayed for up to two weeks after a provider silently changes model behavior
- **Evidence**: The "Cache Behavior" bullets state successful responses are cached with complete response data, TTL expiry default is 14 days, and invalidation happens only on TTL expiry or manual clearing.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Successful API responses are cached with their complete response data" and "Cache is automatically invalidated when: TTL expires (default: 14 days); Cache is manually cleared"
- **Our assessment**: This is the core operational hazard for the guide. Because invalidation is TTL- or manual-only, an eval run inside the TTL window after a provider silently ships a new model version will replay pre-upgrade responses. That is a direct tension with `blog-promptfoo-model-upgrades-break-agent-safety.md` (#482), which establishes that model upgrades silently change behavior: the vendor documents that risk, yet the default config can serve stale responses for two weeks. Confidence in the mechanism is settled (documented); the severity framing is our synthesis.

### Claim 5: Error responses and empty responses are not cached — so retries and nondeterminism concentrate exactly on failing cases
- **Evidence**: The "Cache Behavior" section ("Error responses are not cached to allow for retry attempts") and the "Additional Cache Details" bullets ("Empty responses are not cached").
- **Confidence**: settled (documented product behavior)
- **Quote**: "Error responses are not cached to allow for retry attempts" and "Empty responses are not cached"
- **Our assessment**: Buy it. This defines the negative path: failed evals always re-hit the provider, so retry cost and nondeterminism land on exactly the cases that already failed. For CI-gate accounting this matters — a green run can be fully memoisable while the flaky failing cases are the ones paying full price on every retry. The retry-availability framing (a 429/500 is retryable precisely because it was not cached) connects to Claim 7.

### Claim 6: Memory storage is used automatically when `NODE_ENV=test`, with the default `PROMPTFOO_CACHE_TYPE` being `memory` under test and `disk` otherwise
- **Evidence**: The "Cache Behavior" section ("Memory storage is used automatically when `NODE_ENV=test`") and the env-var table (`PROMPTFOO_CACHE_TYPE` default "`memory` if `NODE_ENV` is `test`, otherwise `disk`").
- **Confidence**: settled (documented default behavior)
- **Quote**: "Memory storage is used automatically when `NODE_ENV=test`"
- **Our assessment**: Buy it. The memory default under test is a two-edged behavior for CI: it avoids polluting a shared disk cache during test runs, but it also means responses survive only for the lifetime of the test process. Combined with Claim 4's TTL, this is why the docs' own CI guidance (Claim 8) tells test-framework users to set disk explicitly — the "correct" cache layer for a test runner is a deliberate choice, not the default.

### Claim 7: Rate limit responses (HTTP 429) are handled automatically with exponential backoff; HTTP 500 responses are retried only when `PROMPTFOO_RETRY_5XX=true` — retry behavior sits directly beside caching in the same pipeline
- **Evidence**: The "Additional Cache Details" bullets list 429 backoff, 500 retry gating, and empty-response non-caching together.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Rate limit responses (HTTP 429) are automatically handled with exponential backoff" and "HTTP 500 responses can be retried by setting `PROMPTFOO_RETRY_5XX=true`"
- **Our assessment**: Buy it. The co-location of these rules with the cache rules matters: the negative path (429/500/empty) is the only path that both hits the provider and engages retry logic, so backoff and retry budget are effectively reserved for failing cases. `PROMPTFOO_RETRY_5XX=true` is the explicit opt-in for a flake-tolerance/flake-rate tradeoff in CI — default-off means a 500 is a hard failure unless a team deliberately buys into retry.

### Claim 8: For `--repeat` / `evaluateOptions.repeat` greater than 1, each repeat index gets a separate cache namespace — re-running an eval replays the per-repeat cached responses, and `--no-cache` combined with `--repeat` is required for every run to make fresh LLM calls
- **Evidence**: The "Cache Behavior" bullet on repeat namespacing and the CLI section's explicit guidance.
- **Confidence**: settled (documented product behavior)
- **Quote**: "When `evaluateOptions.repeat` or `--repeat` is greater than 1, each repeat index uses a separate cache namespace. Re-running the same eval can reuse those per-repeat cached responses, while preserving distinct outputs between repeat 0, repeat 1, etc." and "Use `--no-cache` with `--repeat` when you want every run to make fresh LLM calls instead of replaying each repeat index from cache."
- **Our assessment**: Buy it, and this is *the* reproducibility hazard the Prospector flagged. The per-repeat namespacing means a variance/flake measurement is not necessarily measuring model variance — on a warm cache it measures replay of distinct cached outputs per index, which is exactly why the vendor's own guidance pairs `--no-cache` with `--repeat`. Combined with the 14-day TTL, a CI regression gate can pass against cached responses from a prior model/prompt version unless the gate explicitly opts out of cache.

### Claim 9: The env-var control surface is `PROMPTFOO_CACHE_ENABLED` (default true), `PROMPTFOO_CACHE_TYPE` (disk/memory), `PROMPTFOO_CACHE_PATH` (default `~/.promptfoo/cache`), and `PROMPTFOO_CACHE_TTL` (default 14 days); the cache can also be disabled via CLI `--no-cache` / Node `evaluateOptions.cache: false`
- **Evidence**: The "Configuration" env-var table and the Command Line / Node package sections.
- **Confidence**: settled (documented defaults, directly checkable)
- **Quote**: "The cache is configurable through environment variables: Environment Variable | Description | Default Value / PROMPTFOO\_CACHE\_ENABLED | Enable or disable the cache | true / PROMPTFOO\_CACHE\_TYPE | `disk` or `memory` | `memory` if `NODE_ENV` is `test`, otherwise `disk` / PROMPTFOO\_CACHE\_PATH | Path to the cache directory | `~/.promptfoo/cache` / PROMPTFOO\_CACHE\_TTL | Time to live for cache entries in seconds | 14 days"
- **Our assessment**: Buy it. This is the concrete toggles surface a CI gate needs: `PROMPTFOO_CACHE_ENABLED=false` for a true cold gate, `PROMPTFOO_CACHE_PATH` to make the cache runner-local/reproducible, and `PROMPTFOO_CACHE_TTL` to shorten the stale-response window below 14 days. Whether a gate is real or satisfied from a warm cache is a pipeline design decision made through exactly these four variables.

### Claim 10: For jest/vitest/mocha and other external-framework integrations, promptfoo's own CI recommendation is `PROMPTFOO_CACHE_TYPE=disk` with an explicit `PROMPTFOO_CACHE_PATH` — making the eval cache an explicit, deliberately-placed pipeline decision
- **Evidence**: The "Tests" section's pairing of the caveat with the recommended config.
- **Confidence**: settled (documented vendor guidance for a named use case)
- **Quote**: "If you're integrating with jest or vitest, mocha, or any other external framework, you'll probably want to set the following for CI: `PROMPTFOO_CACHE_TYPE=disk` / `PROMPTFOO_CACHE_PATH=...`"
- **Our assessment**: Buy it as vendor guidance. The instruction's own logic: test runs default to an automatically-created disk cache, so "you'll probably want" an explicit path means making cache placement and lifecycle explicit rather than implicit. Note what the guidance does *not* say — it does not recommend disabling the cache for tests; it recommends placing a disk cache deliberately. Consistent with the eval-harness being designed to be cacheable, with the caveat that a shared default cache path across CI jobs is the footgun the explicit `PROMPTFOO_CACHE_PATH` exists to prevent.

### Claim 11: The cache can be cleared via `promptfoo cache clear`, `promptfoo.cache.clearCache()` in the Node API, or `rm -rf ~/.promptfoo/cache`, and a cache miss can be forced with `--no-cache` or a `true` last-argument to `fetchWithCache`
- **Evidence**: The "Clearing the Cache" three options and the "Cache Busting" two options.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can clear the cache in several ways: Using the CLI command: `promptfoo cache clear`; Through the Node.js API: `const promptfoo = require('promptfoo'); await promptfoo.cache.clearCache();`; Manually delete the cache directory: `rm -rf ~/.promptfoo/cache`" and "You can force a cache miss in two ways: Pass `--no-cache` to the CLI: `promptfoo eval --no-cache`; Set cache busting in code: `const result = await fetchWithCache(url, options, timeout, 'json', true); // Last param forces cache miss`"
- **Our assessment**: Buy it. The invalidation surface is the operational complement to Claim 4: in addition to TTL, a full invalidation is one command away (`promptfoo cache clear`), and a single-request force-miss is available in code (`fetchWithCache(..., true)`). For an incident-hit cache (suspected stale responses after a provider change), the clearing path is the emergency response; the `--no-cache` flag is the per-run escape hatch a CI gate should use for correctness-critical jobs.

## Concrete Artifacts

### Cache key formats (verbatim from "Cache Keys" section)

```
// Provider-specific scope plus a digest of request material
const providerCacheKey = `openai:gpt-5:<request-digest>`;

// HTTP fetch cache entries include URL, method, headers, options, and body identity
const fetchCacheKey = `fetch:v3:<request-digest>`;
```

### Cache behavior rules (verbatim from "Cache Behavior" section)

- Successful API responses are cached with their complete response data
- Error responses are not cached to allow for retry attempts
- When `evaluateOptions.repeat` or `--repeat` is greater than 1, each repeat index uses a separate cache namespace. Re-running the same eval can reuse those per-repeat cached responses, while preserving distinct outputs between repeat 0, repeat 1, etc.
- Cache is automatically invalidated when:
  - TTL expires (default: 14 days)
  - Cache is manually cleared
- Memory storage is used automatically when `NODE_ENV=test`

### Env-var configuration table (verbatim from "Configuration" section)

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| PROMPTFOO_CACHE_ENABLED | Enable or disable the cache | true |
| PROMPTFOO_CACHE_TYPE | `disk` or `memory` | `memory` if `NODE_ENV` is `test`, otherwise `disk` |
| PROMPTFOO_CACHE_PATH | Path to the cache directory | `~/.promptfoo/cache` |
| PROMPTFOO_CACHE_TTL | Time to live for cache entries in seconds | 14 days |

### Additional cache details (verbatim from "Additional Cache Details" section)

- Rate limit responses (HTTP 429) are automatically handled with exponential backoff
- Empty responses are not cached
- HTTP 500 responses can be retried by setting `PROMPTFOO_RETRY_5XX=true`

### Clearing the cache (verbatim from "Clearing the Cache" section)

```
promptfoo cache clear
```

```
const promptfoo = require('promptfoo');
await promptfoo.cache.clearCache();
```

```
rm -rf ~/.promptfoo/cache
```

### Cache busting (verbatim from "Cache Busting" section)

```
promptfoo eval --no-cache
```

```
const result = await fetchWithCache(url, options, timeout, 'json', true); // Last param forces cache miss
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/caching/ — sections as noted. All copied character-for-character from the rendered page (code blocks re-flowed only at the newline level to restore line breaks lost in extraction).

## Cross-References

- **Corroborates**:
  - `source-notes/blog-promptfoo-model-upgrades-break-agent-safety.md` **Claim 1** ("Upgrading from GPT-4o to GPT-4.1 caused a customer's agent to drop from 94% to 71% prompt-injection resistance") — this page's 14-day silent-replay default (Claim 4) is the enabling condition for that note's masked-regression scenario: a provider silently shipping a new model behavior is precisely what the cached eval result can hide within the TTL window. (Verified: #482 Claim 1.) The two notes do not contradict; #482 prescribes re-running safety suites on upgrade, and this page shows why the cache must be cleared/disabled for that re-run to be evidence.
  - `source-notes/blog-litellm-valkey-semantic-caching.md` **Claim 1** ("LiteLLM now supports semantic prompt caching on Valkey via a new `cache_params.type: valkey-semantic` backend") — both documents describe a response/prompt cache that can serve stale or similarity-based responses instead of live model output. Different layer (gateway/proxy vs eval-harness client) but the same reliability concern: "who owns the cached entry and when is it invalidated." (Verified: #1176 Claim 1.)

- **Contradicts**: None identified. This page is a first-party config reference for the eval-harness cache; verified against all existing source notes and `CONTRADICTIONS.md` (no open `C-NNN` entries). The tension with `blog-promptfoo-model-upgrades-break-agent-safety.md` (#482) flagged above is a risk relationship, not an opposing claim — #482 never claims the eval cache is safe. The cached-outputs-can-be-replayed property is distinct from the semantic-cache similarity mechanism in `blog-litellm-valkey-semantic-caching.md` (that note's cache keys are embedding/meaning-based; this page's are exact composite digests) — a mechanism difference, not a contradiction.

- **Extends**:
  - `source-notes/blog-litellm-valkey-semantic-caching.md` — extends the corpus's caching coverage from the gateway/proxy layer (server-side semantic response cache for live traffic, #1176) to the **eval-harness layer** (per-eval client-side response memoisation). The Prospector explicitly flagged distinguishing these two so the guide does not conflate "cache the proxy" with "cache the eval"; this note draws that boundary.
  - `source-notes/failure-litellm-httpx-cache-eviction.md` **Claim 1** ("A cache-eviction cleanup method that indiscriminately closes cached objects can destroy shared references still in active use") and `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 1** ("A gateway request-translation change that keeps payloads semantically equivalent can still silently destroy a provider's prefix-based prompt cache") — these two failure notes answer the "who owns / what invalidates a cache entry" question for the proxy and provider layers respectively; this page documents the eval-harness layer's answer (TTL + manual clear, errors never cached) as the client-side counterpart. Same question, one layer down from each incident's layer. (Verified: #461 Claim 1 and #697 Claim 1.)
  - `source-notes/docs-promptfoo-code-scan-cli.md` and `source-notes/docs-promptfoo-code-scan-github-action.md` — siblings in the same vendor docs family with the same CI-gating framing (#1264/#1265); this page adds the eval-result cache semantics behind an eval-driven CI gate, complementing (not restating) the scanner surface.

- **Novel**: This is the first source note covering **the eval harness's own response cache** — the corpus previously covered caching only at the gateway/proxy layer (LiteLLM, #1176/#461/#697) and provider prompt caching (Bedrock invoke, #697). Specifically new to the corpus:
  1. **The eval-result cache contract** — composite provider-scoped keys (Claim 2), the "key formats are implementation details" versioned-reuse caveat (Claim 3), and the 14-day TTL replay window (Claim 4).
  2. **The per-repeat-index cache namespace** interplay with `--repeat` (Claim 8) — the first documented instance of "a regression/variance measurement can be cache replay rather than model variance," and the specific `--no-cache` + `--repeat` remediation.
  3. **The negative-path rule** — errors and empty responses are never cached (Claims 5, 7), concentrating retry cost and nondeterminism on failing cases; `PROMPTFOO_RETRY_5XX=true` as the explicit 500 retry gate.
  4. **The test-framework CI guidance** — `PROMPTFOO_CACHE_TYPE=disk` + explicit `PROMPTFOO_CACHE_PATH` for jest/vitest/mocha (Claim 10). The guide currently has **zero** coverage of caching (no chapter file matches "cach"), so every one of these is net-new material.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation/measurement methodology and CI gating**: Add the eval-result cache as a new section: default disk cache at `~/.promptfoo/cache` with a 14-day TTL (Claims 1, 4); the exact-composite-key bucketing and versioned key formats (Claims 2, 3); and the reproducibility rule — a variance/flake or regression run must use `--no-cache` with `--repeat` and `PROMPTFOO_CACHE_TTL`/`PROMPTFOO_CACHE_ENABLED=false` for correctness-critical gates (Claims 8, 9). Add the negative-path accounting rule: because errors and empty responses are never cached (Claim 5), a green run can be fully cached while the failing cases pay full retry cost every run; budget CI accordingly and treat `PROMPTFOO_RETRY_5XX=true` as an explicit flake-tolerance decision (Claim 7).
- **Chapter 05 — the model-upgrade test corridor**: Cross-reference `blog-promptfoo-model-upgrades-break-agent-safety.md` (#482): before re-running that note's post-upgrade safety suites, the cache from the *previous* model version must be invalidated (`promptfoo cache clear` or `--no-cache`), because within the 14-day TTL the default config replays pre-upgrade responses (Claim 4). This ties the existing upgrade-checklist material to a concrete cache control.
- **Chapter 03 (Runbooks and Agents) — CI gate placement / eval pipelines**: Document the runner-local cache decision surface for CI: `PROMPTFOO_CACHE_TYPE=disk` with an explicit `PROMPTFOO_CACHE_PATH` for test-framework runs (Claim 10), the memory-under-test default (Claim 6), and the full env-var control surface (Claim 9). The rule to state: whether a gate passes against live model behavior or a warm cache is a pipeline design decision controlled by `PROMPTFOO_CACHE_*` — never leave it at the implicit default.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page (https://www.promptfoo.dev/docs/configuration/caching/). Single self-contained page; no sub-pages followed (the linked `jest`/`mocha` integration pages are covered by other integration docs and add no cache surface beyond the `PROMPTFOO_CACHE_TYPE=disk`/`_PATH` recommendation already on this page).
- The issue was auto-filed from the `promptfoo-docs` site-crawl seed; no human deep-read preceded this extraction. There is no separate confirmation link in the source; quotes were verified against the fetched rendered content character-for-character before writing. Code blocks in the source arrive as single lines after HTML extraction; I restored the line breaks at comment/statement boundaries only (no wording changes). Sensitive-payload hashing (Claim 2) is stated as "hashed where possible" — the docs do not guarantee hashing in all cases; the claim and quote preserve that qualifier.
- Per the Prospector triage (which ran several times, all agreeing): this page is the first corpus source on the **client-side eval-harness cache**, and must be cross-referenced — not conflated — with the proxy-layer semantic cache (#1176) and the proxy/provider cache failures (#461, #697). The sibling auto-filed pages #1276 (`configuration chat`) and #1277 (`configuration datasets`) are adjacent config pages, not duplicates; they were not mined here and are not cross-referenced as claims.
- `confidence_overall` is `emerging`: per the triage caveat, this is vendor product documentation, so claims are authoritative for promptfoo product behavior but there are **no measured cost/latency/cache-hit-rate figures and no independent validation**. Individual mechanism/default claims (Claims 1–9, 11) would score settled-for-product-behavior; the operational risk framing (the model-upgrade replay hazard, Claim 4, and the CI-gate correctness trap, Claims 8/10) is the Miner's synthesis on top of documented behavior, which is why the overall confidence is emerging rather than settled. `date_published` uses the page's "Last updated Sep 11, 2026" date (undated page).
- **Candidate dismissal** (from `miner-related-notes.md`, read before Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `docs-google-sre-team-lifecycles.md`, `docs-google-sre-eliminating-toil.md`, `docs-google-sre-reliable-product-launches.md` — Google SRE workflow/organization chapters; unrelated to eval caching; dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` — red-team methodology and CI/CD placement; same vendor and CI-gate theme but no caching surface; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — AI incident triage, no eval-cache content; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP; unrelated vendor; dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent spectrum/guardrails; no caching; dismissed.
  - `blog-promptfoo-red-team-claude.md` — model red-team plugin config; dismissed.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO construction from SRE Prodcast; dismissed.
  - `blog-litellm-valkey-semantic-caching.md` — **the relevant caching-layer candidate; cited** (Corroborates/Extends). The remaining relevant cross-refs (`blog-promptfoo-model-upgrades-break-agent-safety.md`, `failure-litellm-httpx-cache-eviction.md`, `failure-litellm-bedrock-invoke-prompt-cache.md`, the two `docs-promptfoo-code-scan-*` siblings) were found by searching `source-notes/` per the Prospector's guidance; each cited claim was re-read and verified per MINER.md §4b before citation.
- No contradiction issue filed: verified against `CONTRADICTIONS.md` (no open `C-NNN` entries) and all corpus notes. The closest surface — the 14-day replay default enabling masked model-upgrade regressions — is consistent with (and materially supports) #482's upgrade-testing prescription; it is a risk relationship, not a claim conflict.