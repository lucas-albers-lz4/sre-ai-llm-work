---
source_url: https://docs.litellm.ai/blog/bedrock-invoke-prompt-caching-incident
source_type: failure-report
platform: blog
title: "Incident Report: Prompt Cache Invalidation for Claude Code on Bedrock Invoke"
author: "Mateo Wang (AI Engineer, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-07-13
date_extracted: 2026-07-31
last_checked: 2026-07-31
status: current
confidence_overall: settled
issue: "#697"
---

# Failure Report: LiteLLM Bedrock Invoke translation invalidated Anthropic prompt caching for Claude Code

> A "compatibility" patch upstreamed from a customer workaround hoisted every `role: "system"` entry in `messages` into the top-level `system` field on the Bedrock **Invoke** path, silently destroying Anthropic's prefix-based prompt cache for Claude Code sessions: warm-session cache hit rates dropped from ~90% to 25-45% and team spend rose 2-3x while every request still returned a 200 with a correct completion. Shipped `v1.91.0` (Jul 4), fixed `v1.91.2` (Jul 10).

## Source Context

- **Platform**: Vendor engineering incident blog on `docs.litellm.ai/blog`, published July 13, 2026, authored by LiteLLM's AI Engineer (Mateo Wang), CEO (Krrish Dholakia), and CTO (Ishaan Jaffer). Follows the same incident-report format as LiteLLM's other postmortems (httpx cache eviction, wildcard desync, model cost map).
- **Author credibility**: High — vendor-authored, fully root-caused and remediated incident with PR-level code references, a dated timeline, measured impact metrics, and process-gap self-assessment (including admitting the fix's own regression tests had been single-turn only).
- **Scope**: A specific production regression in LiteLLM's Bedrock Invoke translation layer, plus two post-publication updates (July 21) covering the extended e2e coverage. Generalizes to a failure class: a gateway/translation layer altering a provider-specific caching contract while keeping request payloads semantically equivalent.

## What Was Attempted

- **Goal**: Restore working Claude Code sessions on Bedrock **Invoke** for models older than Opus 4.8. After May 28, 2026 these sessions failed with 400s mid-conversation whenever the model was pre-Opus-4.8 and served under an alias.
- **Tool/approach**: LiteLLM proxy. An enterprise customer's local patch — hoisting every `role: "system"` entry in `messages` into the top-level `system` field, mirroring Converse behavior — was upstreamed as PR #31364 and shipped in `v1.91.0` on July 4.
- **Setup**: Claude Code routed to Amazon Bedrock's Invoke API through the LiteLLM proxy. Prompt caching is prefix-based on Anthropic: the Bedrock provider checks whether any previous request was a truncated prefix of the current request and reads from cache only up to that point.

## What Went Wrong

- **Symptoms**: Warm-session cache hit rates dropped from roughly 90% to 25-45%; team daily spend rose 2-3x for identical usage. Requests kept returning 200s with correct completions — "the only symptoms were the cache miss rate and the bill."
- **Severity**: Medium (silent cost regression; no correctness impact), per the vendor's own rating.
- **Duration**: July 4 (shipped `v1.91.0`) → July 10 (`v1.91.2` fix); affected versions `v1.91.0` and `v1.91.1`.
- **Reproducibility**: Deterministic for any Claude Code session that wrote a new mid-conversation system message (measured at ~1 every 3 turns on average) — each hoist invalidated the entire `messages` cache past the tool definitions/system prompt.

### Symptom A: Cache hit rate collapse with zero correctness impact
- **Evidence**: Vendor's measured impact in the Summary; the 200s-with-correct-completions symptom is stated explicitly.
- **Quote**: "For the customers who reported it, warm-session cache hit rates dropped from roughly 90% to 25-45% and team daily spend rose 2-3x for the same usage. Requests kept returning 200s with correct completions; the only symptoms were the cache miss rate and the bill."
- **Confidence**: settled.

### Symptom B: 400s on pre-Opus-4.8 aliased models triggered the "fix" that caused the regression
- **Evidence**: "What went wrong" section ties the 400s to the alias-capability-detection path.
- **Quote**: "After May 28, Claude Code sessions on Bedrock Invoke began failing with 400s mid-session when two things were true: the model was older than Opus 4.8; the model is served under an alias"
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: PR #31364 moved every `role: "system"` entry in `messages` into the top-level `system` field on the Invoke path. Because Anthropic prompt caching is prefix-based, hoisting the system entries invalidates every cache breakpoint past the tool definitions and system prompt whenever a new mid-conversation system message is written. The hoist fixed the 400s but silently destroyed caching.
- **Our assessment**: Agree completely. This is the class of bug where a translation layer keeps the request *semantically equivalent* to the model but breaks the provider's *caching contract* — no error surfaces, and only cache-read token counts (which no CI or monitoring measured) and the bill revealed it. The severity framing (Medium: silent cost regression, no correctness impact) is appropriate but undersells it for cost-sensitive fleets: a 2-3x spend increase on Claude Code traffic is material.
- **Category**: genuine-bug in LiteLLM's Bedrock Invoke translation, but representative of a generic anti-pattern — a provider-specific caching contract silently altered by a request-translation change in a gateway.

### Root-cause detail A: Prefix-based caching makes the hoist doubly destructive
- **Evidence**: Background section explains the mechanism and the pricing ladder.
- **Quote**: "the pricing of tokens in increasing cost is: cache read (0.1x); normal write (1x); cache write (1.25x for 5m ttl, 2x for 1h ttl)"
- **Quote**: "when Claude Code makes a new request, the Bedrock provider checks if any previous request was a truncated prefix of the current request. If so, it reads from the cache only up to that point."
- **Confidence**: settled.

### Root-cause detail B: Mid-conversation system messages are brand-new and half-undocumented
- **Evidence**: Dated feature rollout; Claude Code changelog never mentioned it.
- **Quote**: "On May 28, 2026, Claude Opus 4.8 shipped as the first model accepting `role: "system"` entries inside `messages`"
- **Quote**: "Claude Code (`v2.1.154`) began emitting them on May 28, 2026, with no mention in its changelog."
- **Confidence**: settled.

### Root-cause detail C: Bedrock's two Anthropic APIs have different system-message rules
- **Evidence**: Background section distinguishes Converse (top-level only, hoisted by LiteLLM since December 2024, PR #7037) from Invoke (native Anthropic Messages format, pre-Opus-4.8 rejects mid-conversation system entries with a 400).
- **Quote**: "Converse requires all system content in a top-level field; LiteLLM has hoisted it there since December 2024 (#7037)."
- **Quote**: "Invoke takes the native Anthropic Messages format, where models older than Opus 4.8 reject mid-conversation system entries with a 400 and newer models accept them."
- **Confidence**: settled.

### Root-cause detail D: Alias-based capability detection is a provider-version-gating trap
- **Evidence**: Claude Code infers model capabilities from the model-name string.
- **Quote**: "Claude Code detects capabilities by looking for version substrings like `opus-4-7` or `sonnet-4-6` in the model name."
- **Quote**: "For example, an alias like `bedrock-claude` contains none, so Claude Code assumes the newest feature set and always emits mid-conversation system messages."
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: Three PRs, all released July 10 in `v1.91.2` after extensive end-to-end testing, with regression tests that fail on pre-fix code: #32578 disables mid-conversation system message hoisting on Invoke; #32831 re-enables hoisting on models below Opus 4.8; #32882 disables hoisting on Sonnet 5 and Fable 5 too.
- **Workaround / guidance to users**: "If you run Claude Code against Bedrock, route it through the Invoke path (`bedrock/invoke/<model>`)" — Converse still must hoist (it rejects system entries inside `messages` at any position), so Converse-routed sessions still lose cached prefix on every mid-conversation system message. The vendor is "raising the API constraint with AWS."
- **Unresolved at publication**: Converse limitation; Vertex AI and Azure parity. Both were closed post-publication (July 21 update): #33807 (merged July 20) confirmed Vertex AI and Azure enforce the same per-model contract as Bedrock Invoke and both paths now reuse the model-aware hoisting logic.

### Fix detail A: Regression tests fail on pre-fix code
- **Evidence**: Detection and response section lists all three fix PRs.
- **Quote**: "Three PRs fixed it, all released July 10 in `v1.91.2` after extensive end-to-end testing, with regression tests that fail on pre-fix code:"
- **Confidence**: settled.

### Fix detail B: Post-incident e2e coverage is multi-turn against real Bedrock
- **Evidence**: Remediation section plus July 21 update.
- **Quote**: "#32963 merged July 14 with live-Bedrock tests that fail whenever a mid-conversation system message costs a session its cached prefix; #33807 extends the same coverage to Vertex AI and Azure."
- **Confidence**: settled.

### Fix detail C: Weekly cost/perf regression load test
- **Evidence**: July 21 update for #34166.
- **Quote**: "CI now runs concurrent Claude Code-shaped sessions weekly against real Anthropic and Bedrock Invoke deployments and fails if error rate, warm-turn cache reads, cache write volume, p95 turn latency, or recorded spend leaves its baseline."
- **Confidence**: settled.

## Concrete Artifacts

**Incident metadata (verbatim from source):**
```
Date: July 4 to July 10, 2026
Affected versions: v1.91.0 and v1.91.1
Severity: Medium (silent cost regression; no correctness impact)
Status: Resolved in v1.91.2
Note: If you run Claude Code against Amazon Bedrock through LiteLLM on either v1.91.0 or v1.91.1, upgrade to v1.91.2 or higher.
```

**Timeline (verbatim from source):**
```
Date (2026) | Event
May 28      | Opus 4.8 ships; Claude Code starts emitting mid-conversation system messages
Jun 27      | Customer workaround upstreamed as #31364
Jul 4       | v1.91.0 ships with the regression
Jul 6       | Customer observes 2-3x spend and collapsed cache hit rates
Jul 8       | Regression reported; root cause identified; fix opened
Jul 10      | v1.91.2 ships with all three fixes and regression tests
Jul 13      | Customer confirms full recovery
```

**Fix PRs (verbatim from source):**
```
#32578 disables mid-conversation system message hoisting on Invoke.
#32831 re-enables hoisting on models below Opus 4.8.
#32882 disables hoisting on Sonnet 5 and Fable 5, too.
```

**Prefix-based cache pricing ladder (verbatim from source):**
```
cache read (0.1x) < normal write (1x) < cache write (1.25x for 5m ttl, 2x for 1h ttl)
```

**Post-incident process commitment (verbatim from source):**
```
Bug fixes now have a higher merge bar: validated means reproduced against the real client's traffic on their exact end-user application end-to-end and a complete understanding of the root cause; synthetic requests are not enough.
```

## Extracted Claims

### Claim 1: A gateway request-translation change that keeps payloads semantically equivalent can still silently destroy a provider's prefix-based prompt cache
- **Evidence**: PR #31364 hoisted every `role: "system"` entry in `messages` into the top-level `system` field on the Bedrock Invoke path; this invalidated every cache breakpoint past the tool definitions/system prompt. Requests remained semantically identical to the model yet the cache contract was broken.
- **Confidence**: settled
- **Quote**: "The cause: PR #31364 moved every `role: "system"` entry in `messages` into the top-level `system` field on the Invoke path, which invalidates every cache breakpoint past the tool definitions and system prompt."
- **Our assessment**: This is the core, novel claim of the report and the vendor's own root cause, corroborated by measured impact and a verified fix. It establishes a new failure class for the corpus: translation-layer changes that preserve model-facing semantics while altering a caching contract, invisible to correctness checks.

### Claim 2: The regression was silent — all requests returned 200s with correct completions, and only cache-read token counts and spend signaled it
- **Evidence**: Vendor's own monitoring gap: no CI or monitoring measured cache-read token counts.
- **Confidence**: settled
- **Quote**: "3. **Cost regressions are silent.** Every response was a 200 with a correct completion. The only signal was cache-read token counts, which nothing in our CI or monitoring measured."
- **Our assessment**: Directly actionable for Ch02 observability. A correctness-complete failure can be invisible to request/error metrics; cache-hit-rate and spend are the signals that catch it. This corroborates the "silent regression" theme already present in the LiteLLM corpus (see Cross-References).

### Claim 3: Measured impact — warm-session cache hit rate dropped ~90% → 25-45%, daily spend rose 2-3x
- **Evidence**: Vendor-reported customer metrics in the Summary.
- **Confidence**: settled
- **Quote**: "For the customers who reported it, warm-session cache hit rates dropped from roughly 90% to 25-45% and team daily spend rose 2-3x for the same usage."
- **Our assessment**: Concrete, quantified impact from the reporting customers. The magnitude (2-3x spend on identical usage) makes the "Medium severity, no correctness impact" framing understate the operational cost for cache-dependent fleets.

### Claim 4: Anthropic prompt caching is prefix-based, and a new mid-conversation system message written roughly every ~3 turns by Claude Code destroyed the cache each time
- **Evidence**: Background + "What went wrong" sections; "which we measured to happen every ~3 turns on average".
- **Confidence**: settled
- **Quote**: "The hoist fixed the 400s but by always hoisting the system entries in `messages`, that would invalidate the entire `messages` cache whenever a new mid-conversation system message was written by Claude Code, which we measured to happen every ~3 turns on average."
- **Our assessment**: The ~3-turns cadence explains the 2-3x spend amplification: the regression wasn't a rare edge case but a per-session, recurring event. Any prefix-cache design with a frequently-mutating early segment is exposed to this failure class.

### Claim 5: Mid-conversation system messages are a new (May 28, 2026) Anthropic feature that shipped with no Claude Code changelog entry
- **Evidence**: Dated rollout facts in the Background section.
- **Confidence**: settled
- **Quote**: "On May 28, 2026, Claude Opus 4.8 shipped as the first model accepting `role: "system"` entries inside `messages`"
- **Quote**: "Claude Code (`v2.1.154`) began emitting them on May 28, 2026, with no mention in its changelog."
- **Our assessment**: Undocumented client behavior is a provider-ecosystem reliability hazard: gateway vendors can't translate features they don't know exist. This motivates the vendor's "daily automated diffs of Anthropic's SDKs and docs" remediation.

### Claim 6: Bedrock's two Anthropic API surfaces have different system-message contracts — Converse requires top-level hoisting, Invoke accepts mid-conversation entries only on newer models
- **Evidence**: Background section, including the December 2024 hoist PR (#7037) for Converse.
- **Confidence**: settled
- **Quote**: "Converse requires all system content in a top-level field; LiteLLM has hoisted it there since December 2024 (#7037)."
- **Quote**: "Invoke takes the native Anthropic Messages format, where models older than Opus 4.8 reject mid-conversation system entries with a 400 and newer models accept them."
- **Our assessment**: The Converse/Invoke divergence is the backdrop of the whole incident and remains a live footgun (see Claim 12). A gateway cannot safely apply one translation rule across both paths.

### Claim 7: Alias-based model capability detection makes version-gating fail silently — an alias like `bedrock-claude` has no version substring, so Claude Code assumes the newest feature set
- **Evidence**: "What went wrong" section, item 1.
- **Confidence**: settled
- **Quote**: "For example, an alias like `bedrock-claude` contains none, so Claude Code assumes the newest feature set and always emits mid-conversation system messages."
- **Our assessment**: A genuine provider-version-gating trap beyond LiteLLM: any layer that abstracts model identities away from version substrings (aliases, logical names, wildcards) can cause clients to emit payloads the underlying model rejects. Routing and model metadata should carry version information.

### Claim 8: The 400-fix itself was upstreamed from a customer workaround and shipped without understanding its caching implications
- **Evidence**: "What went wrong" item 2 and "Why our process did not catch this" item 1.
- **Confidence**: settled
- **Quote**: "An enterprise customer worked around the 400s with a local patch that hoisted every system entry from `messages` into top-level `system`, mirroring the Converse behavior, and asked us to upstream it. We shipped it as #31364 in `v1.91.0` on July 4."
- **Quote**: "We validated it with single-turn `curl` requests showing a 400 become a 200 that we assumed was the shape that Claude Code would use. That was not the case."
- **Our assessment**: The process gap is textbook: a patch validated single-turn, on synthetic requests, without reproducing the real client's traffic shape, then merged with passing tests. The vendor's new merge bar (reproduce against the real client's exact end-user application end-to-end) is the direct, correct response.

### Claim 9: Review lacked the context to object — neither the human reviewer nor AI review bots connected the hoist to cache invalidation
- **Evidence**: "Why our process did not catch this" item 2.
- **Confidence**: settled
- **Quote**: "The human reviewer saw a small compatibility patch with passing tests and no explanation of why Claude Code started sending these kinds of mid-conversation system messages, and our AI review bots did not flag the caching implication either. Nobody in the loop had the info to connect the hoist to cache invalidation."
- **Our assessment**: A small, green patch with no context defeats both human and AI review. The fix is process-level (higher merge bar) plus automated doc/SDK diffs, not "review more carefully."

### Claim 10: Provider documentation was incomplete — as of July 13 the Claude API docs still described mid-conversation system messages as Opus 4.8-only and unavailable on Bedrock, contradicting the vendor's empirical measurements
- **Evidence**: "Why our process did not catch this" item 4; Bedrock documented support by June 9, 2026.
- **Confidence**: settled
- **Quote**: "The feature never appeared in the Claude Code changelog, and as of July 13 the Claude API docs still describe it as Opus 4.8 only (without mentioning Sonnet or Fable 5) and unavailable on Bedrock, which contradicts our empirical measurements."
- **Our assessment**: This is a provider-docs reliability claim, corroborated within the corpus by `blog-litellm-claude-opus-4-8-day-0.md` (which documented the feature as new) — but note the incident's empirical scope (Sonnet 5/Fable 5 also affected) is newer than the day-0 note's coverage.

### Claim 11: The regression-defense artifact is behavioral e2e tests that fail on pre-fix code, extended to multi-turn Claude Code sessions against real Bedrock (~250k tokens, cache reads must grow monotonically)
- **Evidence**: Remediation section and July 21 update.
- **Confidence**: settled
- **Quote**: "Our e2e suite will gain a scripted multi-turn Claude Code session growing to roughly 250k tokens of context against real Bedrock, asserting cache reads grow monotonically and never collapse (started in #32963)."
- **Quote**: "#32963 merged July 14 with live-Bedrock tests that fail whenever a mid-conversation system message costs a session its cached prefix; #33807 extends the same coverage to Vertex AI and Azure. The full 250k-token session is still in progress."
- **Our assessment**: This is the concrete "how to test for this" pattern: assert a cost-behavioral invariant (cache reads grow monotonically) under real client traffic shape, rather than asserting on payloads. High-value for the guide's regression-defense material.

### Claim 12: Converse-routed Claude Code still loses cached prefix on every mid-conversation system message — the known limitation is unfixed by design, with the fix being to route through Invoke
- **Evidence**: "Known limitations" section.
- **Confidence**: settled
- **Quote**: "Converse rejects system entries inside `messages` at any position, so on `bedrock_converse` we must still hoist, and Claude Code sessions routed through Converse still lose cached prefix on every mid-conversation system message. If you run Claude Code against Bedrock, route it through the Invoke path (`bedrock/invoke/<model>`)."
- **Our assessment**: An honest, actionable limitation statement: the caching hazard isn't fully resolved on Bedrock, it's route-dependent. Anyone running Claude Code against Bedrock should prefer `bedrock/invoke/<model>`.

### Claim 13: Vertex AI and Azure enforce the same per-model hoisting contract as Bedrock Invoke; model-aware hoisting now preserves the cache on both paths
- **Evidence**: July 21 update in "Known limitations".
- **Confidence**: settled
- **Quote**: "We verified live that both providers enforce the same per-model contract as Bedrock Invoke, so both paths now reuse the model-aware hoisting logic: older models return completions instead of 400s and newer models keep the cached prefix byte-identical."
- **Our assessment**: Confirms the failure class generalizes beyond Bedrock — any provider surface with per-model system-message contracts needs model-aware translation, not a single rule.

## Cross-References

- **Corroborates**:
  - `failure-litellm-model-cost-map-silent-fallback.md` (Lesson 3: cost tracking that fails silently erodes observability — failures invisible to request success metrics need separate health checks). This incident is a second, harder instance of the same principle: a pure cost regression invisible to correctness checks, surfaced only by cache-hit-rate/spend telemetry.
  - `failure-litellm-wildcard-model-access-desync.md` (Lesson 4: a successful reload can still silently break dependent behavior — reload success ≠ end-to-end health). Parallel detection theme: correctness-invisible LiteLLM regression with only an out-of-band signal (401s / cache misses).
  - `failure-litellm-httpx-cache-eviction.md` (Claim 4: e2e tests that assert a behavioral invariant catch this failure class regardless of implementation; Claim 5: ~6-day silent window before detection). This incident's "regression tests that fail on pre-fix code" and 6-day window (Jul 4 → Jul 10) match the same e2e-assertion and detection-latency pattern.

- **Extends**:
  - `blog-litellm-claude-opus-4-8-day-0.md` (Claim 2: the Messages API now accepts `system` entries inside `messages`, "so an agent can update its instructions, permissions, or token budget mid-run without breaking the prompt cache"). The day-0 note documented the feature as a cache-preserving benefit on the native Messages API; this incident shows the hazard appears when a translation layer rewrites those entries (hoisting to top-level `system`), and adds the pre-Opus-4.8 400 constraint the day-0 note does not mention. Consistent, not contradictory — the incident's own background confirms native Invoke path behavior matches the day-0 claim.
  - `blog-litellm-save-claude-code-costs.md` (Claim 3: auto-injecting `cache_control` markers to maximize prompt-cache hits). That note covers how to get cache hits; this incident covers what silently destroys them — two halves of the same cache-reliability story for Claude Code through a gateway.
  - `failure-litellm-httpx-cache-eviction.md` — same vendor's cache-related failure genre, but a different cache subsystem (LiteLLM's own client cache eviction vs. provider prompt caching); do not conflate the mechanisms.

- **Contradicts**: None. Verified against `CONTRADICTIONS.md` (no open `C-NNN` entries) and all corpus notes. No existing note claims gateway request translation is cache-safe, or that mid-conversation system messages preserve caching on Bedrock.

- **Novel**: First source note covering:
  1. **Provider caching semantics broken by gateway request-translation** — a translation change that preserves model-facing semantics while silently violating the provider's prefix-cache contract.
  2. **Alias-based capability detection as a version-gating trap** — alias names with no version substring cause clients to assume the newest feature set and emit unsupported payloads.
  3. **Prefix-based cache invalidation via a frequently-mutating early segment** — a ~3-turn system-message cadence amplifying a cost regression 2-3x.
  4. **Cost regression as a monitoring-signal class** — cache-read token counts and spend as the only detectors of a correctness-complete failure.
  5. **The multi-turn e2e regression-test pattern** — scripted Claude Code sessions against real Bedrock asserting cache reads grow monotonically, plus a weekly cost/perf load test.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add the failure class "gateway/translation layer alters a provider-specific caching contract while keeping payloads semantically equivalent." Use this incident as the case study: hoisting `role: "system"` into top-level `system` on Bedrock Invoke invalidated prefix-based prompt caching (hit rate ~90% → 25-45%, spend 2-3x, all 200s). Note the fix pattern (model-aware hoisting: disabled for newer models, enabled below Opus 4.8) and the persistent Converse limitation (route Claude Code via `bedrock/invoke/<model>`).

- **Chapter 02 (Observability)**: Add "correctness-complete failures need out-of-band signals": cache-hit-rate and spend regressions are invisible to request/error metrics; gateways should measure cache-read token counts and flag hit-rate/spend anomalies weekly (LiteLLM now does this via #34166). Cost regressions are a first-class monitoring signal, not a finance concern.

- **Chapter 01 (Incident Response)**: Use the incident anatomy as a case study in process gaps: a customer workaround upstreamed as a "small compatibility patch," validated single-turn with synthetic `curl` requests, merged on passing tests with no end-to-end reproduction of real client traffic. The vendor's response (reproduce against the real client's exact end-user application end-to-end before validating) is a reusable merge-bar rule for gateway changes.

- **Chapter 02 or Ch05 (model enablement / routing)**: Add the alias-capability-detection trap: abstracting model identities away from version substrings (aliases, logical names) can cause client capability detection to assume the newest feature set; version metadata should survive routing layers.

## Extraction Notes

- Source read in full via direct HTTP fetch from the Docusaurus blog page (~8 KB of extractable text, including two July 21 update blocks). No paywall, no truncation. No sub-pages followed — the linked PRs (#31364, #32578, #32831, #32882, #32963, #33807, #34166) are cited as identifiers only.
- All quotes copied character-for-character from the rendered page text, matching the punctuation/numbering in the source ("25-45%", "2-3x", "`v1.91.0`").
- `confidence_overall` is `settled`: vendor-authored postmortem with measured impact metrics, PR-level root cause, dated timeline, and a verified customer-confirmed fix; two post-publication updates confirm the extended coverage merged.
- No contradiction issue filed: the closest corpus claim (`blog-litellm-claude-opus-4-8-day-0.md` Claim 2 — system-inside-messages preserves prompt cache) is consistent with this incident, which concerns the hoisting translation, not the native Messages path. No opposing claim exists in the corpus.
- Candidates from `miner-related-notes.md` dismissed (lexical retrieval returned no gateway/caching-relevant notes; none address provider prompt caching, Bedrock Invoke translation, or silent cost regressions):
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — AI agent spectrum, not caching/gateway reliability.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — AI-for-SRE tooling team, not relevant.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` — SLO vernacular, not relevant.
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — complexity/whiteboard heuristic, not relevant.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — database reliability culture, not applicable.
  - `docs-google-sre-prodcast-04-03-underwood-ai.md` — AIOps effectiveness, not relevant.
  - `blog-pagerduty-sre-agent-triage.md` — agent triage patterns, not gateway caching.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — change-workflow paradigms, not applicable.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — incident tooling breadth, tangential only.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SRE, not applicable.
