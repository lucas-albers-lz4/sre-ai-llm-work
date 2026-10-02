---
source_url: https://www.promptfoo.dev/docs/configuration/rate-limits
source_type: docs
title: "Promptfoo Configuration: Rate Limits — AIMD Adaptive Concurrency, Two-Layer Retry, and the 429 Contract"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-01
date_extracted: 2026-10-02
last_checked: 2026-10-02
status: current
confidence_overall: emerging
issue: "#1545"
---

# Promptfoo Configuration: Rate Limits

> The vendor reference for how promptfoo's evaluator absorbs provider rate
> limiting with no configuration at all: an AIMD adaptive-concurrency
> scheduler (halve on a 429, +1 after sustained success, preemptive cut below
> 10% reported quota remaining) under a `maxConcurrency` that is a *ceiling*
> rather than a dial, two independent retry layers (scheduler 3 attempts /
> 1s base, HTTP 4 attempts / 5000ms base) unified by a single provider
> `maxRetries`, status-text-gated retries for 502/503/504/524, per-provider
> *and* per-API-key limit tracking, a six-event debug vocabulary, and a
> `maxConcurrency: 1` + `delay: 1000` recipe for determinism — with the
> critical caveat that the documented 429 contract is unconditional
> retry with no body-level discrimination (filed as #1548).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo configuration
  reference, "Evals > Runtime > Rate Limits" page)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team
  vendor. First-party documentation of the tool's own runtime behavior, so
  authoritative for the config surface (every YAML key, CLI flag, and env-var
  default here is directly checkable). But it is documentation, not
  measurement: the page publishes **no** convergence time, throughput, or
  cost figures for the adaptive scheduler, and the "let promptfoo find the
  optimal rate automatically" recommendation carries no evidence at all.
  Page footer: "Last updated on **Oct 1, 2026** by **mldangelo-oai**".
- **Scope**: Covers automatic rate-limit handling in the evaluator, supported
  per-provider rate-limit headers, transient 5xx retry rules, the AIMD
  adaptive-concurrency algorithm, the concurrency/delay/backoff config
  surface (YAML + CLI + env var), scheduler and HTTP-retry env-var defaults,
  provider-specific notes (OpenAI, Anthropic, custom providers), the debug
  log event vocabulary, four best practices, and the deterministic-run recipe.
  Does NOT cover the eval-result cache (`docs-promptfoo-configuration-caching.md`),
  provider-side prompt caching, gateway/proxy rate limiting, or red-team
  configuration.
- **Relationship to sibling pages**: this is the deep source behind the
  one-line retry mention in the caching page and the first corpus coverage of
  the scheduler at all.

## Extracted Claims

### Claim 1: promptfoo treats HTTP 429 as unconditionally transient — the documented contract is that 429 (or similar rate-limit errors) is automatically retried with exponential backoff, up to 3 times by default, with no body-level or `type`/`code` discrimination
- **Evidence**: Opening paragraph plus the first bullet of the "Automatic
  Handling" list, which frames the whole feature as zero-configuration.
- **Confidence**: settled (as the documented product contract; it is a
  statement about defaults on a vendor docs page, and the page is the vendor's
  own spec of its own behavior)
- **Quote**: "Promptfoo automatically handles rate limits from LLM providers. When a provider returns HTTP 429 or similar rate limit errors, requests are automatically retried with exponential backoff." / "Failed requests are retried up to 3 times with exponential backoff by default (overridable per provider via `maxRetries`, including `0` to disable retries)"
- **Our assessment**: Buy it as a description of the documented default, and
  flag it hard as an operational hazard. The page's *only* documented
  discrimination between transient and permanent failures is status-**text**
  matching on 5xx codes (Claim 5) — nothing in it inspects a 429 body. The
  custom-provider trigger is a bare substring test (Claim 7). So an operator
  who points this harness at any OpenAI-compatible gateway inherits a client
  that retries every 429 it receives, including 429s that encode a permanent
  condition. That is materially opposed to the corpus's existing position
  (see **Contradicts** below, filed as #1548); do not adopt "429 is
  transient" as a guide-level rule on the strength of this page. Note also
  that the shipped scheduler code is *stricter* than this page advertises —
  see Extraction Notes.

### Claim 2: There are two independent retry layers with different defaults — a scheduler layer that retries `callApi()` with 1-second base backoff up to 3 times, and an HTTP layer that defaults to 4 retries — and one provider `maxRetries` propagates into both, with explicit per-call overrides still winning
- **Evidence**: The "Backoff Configuration" section's numbered list of the two
  layers followed by the propagation sentence. The layer defaults match the
  rest of the page (3 attempts in "Automatic Handling" and in the transient
  section) except that the HTTP layer defaults to 4.
- **Confidence**: settled (documented product behavior, internally consistent
  between prose and the env-var table)
- **Quote**: "Promptfoo has two retry layers: 1. **Provider-level retry** (scheduler): Retries `callApi()` with 1-second base backoff, up to 3 times by default. If a provider config sets `maxRetries`, the scheduler uses that value (including `0` to disable scheduler retries entirely). 2. **HTTP-level retry**: Retries failed HTTP requests. Defaults to 4 retries, or the provider's `maxRetries` when set." / "When a provider config includes `maxRetries`, promptfoo propagates that value to both layers. Explicit per-call overrides (e.g. a provider that passes a specific `maxRetries` to `fetchWithRetries`) still take precedence. For direct `fetchWithProxy` calls, transient retries (502/503/504/524) are disabled when the provider sets `maxRetries: 0`."
- **Our assessment**: Buy it, and treat it as the single most important
  operational fact on the page: the propagation rule means **`maxRetries` is
  the only knob that governs both layers**, so it is the one dial to reach for
  when sizing CI retry budget. The documented `maxRetries: 0` fail-fast
  switch is genuinely total ("including `0` to disable scheduler retries
  entirely" + transient retries disabled for direct `fetchWithProxy` calls) —
  that is the right default for a gate that must fail fast rather than burn a
  provider quota proving a limit exists. The arithmetic nobody states: with
  both layers at their defaults, one logical request can become 4 `callApi()`
  attempts × 5 HTTP attempts = **up to 20 wire attempts**, and the page never
  publishes a combined bound. That is the retry-amplification product the
  Google SRE corpus warns about (see **Corroborates**), and it is also the
  mechanism by which a rate-limited run silently multiplies provider spend
  before it reports failure. The two layers also use different backoff bases
  (1s scheduler vs 5000ms HTTP, Claim 11) and the page never reconciles the
  "1s, 2s, 4s" in the transient section with the 5000ms HTTP default.

### Claim 3: The concurrency controller is AIMD with three documented rules — cut concurrency by 50% when a rate limit is hit, add 1 after sustained successful requests, and proactively reduce when header-reported remaining quota drops below 10%
- **Evidence**: The "How Adaptive Concurrency Works" section's three-item list
  under the AIMD label.
- **Confidence**: settled (documented algorithm; the constants are specific
  and checkable)
- **Quote**: "The scheduler uses AIMD (Additive Increase, Multiplicative Decrease) to optimize throughput: 1. When a rate limit is hit, concurrency is reduced by 50% 2. After sustained successful requests, concurrency increases by 1 3. When remaining quota drops below 10% (from headers), concurrency is proactively reduced"
- **Our assessment**: Buy the mechanism — this is the corpus's first
  documented instance of a named AIMD control loop, and it is the right shape
  for an unknown provider quota (multiplicative decrease because the limit is
  discovered by hitting it; additive increase because the safe direction is
  slow). Two things an operator should carry away beyond the docs: (a) the
  loop is **per-run and client-side** — nothing coordinates it across
  concurrent eval runners, so N runners on one key each pay the same
  discovery cost independently (Claim 6); and (b) rule 3 is the only
  *predictive* element, and it depends entirely on the provider volunteering
  quota headers — a provider that omits them reduces rule 3 to dead code and
  leaves only reactive halving.

### Claim 4: The page's headline recommendation — set `maxConcurrency` high and let the scheduler find the rate for you — is an unevidenced vendor claim, published with no convergence time, no throughput measurement, and no cost comparison
- **Evidence**: The sentence immediately after the AIMD list, restated as
  "Best Practices" item 1 with the inline example comment
  `maxConcurrency: 20 # Scheduler will adapt down if needed`. No measurement,
  trace, or benchmark appears anywhere on the page.
- **Confidence**: anecdotal (vendor recommendation, no supporting data)
- **Quote**: "This allows you to set a higher `maxConcurrency` and let promptfoo find the optimal rate automatically." / "**Start with higher concurrency** - Set `maxConcurrency` to your desired throughput; the scheduler will adapt down if needed"
- **Our assessment**: Do not buy it as validated practice, and say so in the
  guide if it is cited at all. The recommendation is *unfalsifiable as
  written* — "your desired throughput" is set to a value the scheduler is then
  expected to discover it cannot reach, so the config reads like a throughput
  dial while behaving as a ceiling (Claim 5). What is genuinely true and worth
  stating is the weaker version: a high `maxConcurrency` is a cheap probe —
  when quota is generous the scheduler sits at the configured value and the
  discovery cost is zero, and when it is tight the run degrades to a halved
  rate instead of a hard 429 wall. That is a defensible default; "it finds
  the optimal rate automatically" is not. Note that best-practice item 2 (use
  caching) is the only one on the list that reduces provider request volume
  or cost — items 1, 3, and 4 only change how the run reacts.

### Claim 5: `maxConcurrency` is a ceiling, not a setting — the adaptive scheduler may reduce it but "cannot exceed your configured maximum", so realized concurrency is state-dependent and per-provider
- **Evidence**: The "Concurrency" section's closing sentence.
- **Confidence**: settled (documented contract)
- **Quote**: "The adaptive scheduler will reduce this if rate limits are encountered, but cannot exceed your configured maximum."
- **Our assessment**: Buy it, and read it as an operational constraint
  rather than a reassurance. If the ceiling is one-sided, then eval
  wall-clock is not derivable from config: the same `maxConcurrency: 10` run
  is 10-wide on a fresh key and 1-wide after three 429s, and the difference is
  only visible in debug logs (Claim 10). For CI this means a suite that
  usually takes 12 minutes can take an hour after a provider-side limit
  change, with no config diff to explain it. The corollary sharpens an
  existing corpus claim: `docs-promptfoo-chat-threads.md` Claim 1 records
  that a suite referencing `_conversation` runs at concurrency 1 — which is
  exactly the scheduler's documented floor (`PROMPTFOO_MIN_CONCURRENCY`
  default 1), so for multi-turn suites AIMD has **nothing to adapt** and the
  entire rate-limit control surface is inert.

### Claim 6: Transient-error retries are gated on HTTP **status text**, not status code — 502/503/504/524 are retried only when the status text matches, precisely so permanent failures wearing those codes are not retried
- **Evidence**: The "Transient Error Handling" table maps each code to a
  required status-text substring, and the sentence after it states the
  rationale. (The rationale sentence is quoted in the Quote field; the
  code→text mapping is reproduced verbatim in Concrete Artifacts.)
- **Confidence**: settled (documented product behavior with a stated design
  rationale)
- **Quote**: "These errors are retried up to 3 times with exponential backoff (1s, 2s, 4s). The status text check ensures that permanent failures (like authentication errors that happen to use 502) are not retried."
- **Our assessment**: Buy this one outright — it is the most transferable
  idea on the page and the part most worth lifting into the guide as a
  vendor-independent pattern. Retrying on a status *code* is unsafe precisely
  because the same code carries both meanings: an auth failure behind a 502
  will never succeed, and retrying it three times multiplies load on an
  already-failing dependency for nothing. Gating on a second, independent
  signal (here the status text) is a cheap way to keep a code-class retry
  policy from looping on a permanent fault. Note the asymmetry that makes this
  a partial fix rather than a general one: promptfoo applies this
  discrimination to 5xx codes and applies **none** to 429 (Claim 1), even
  though the permanent-failure-wearing-a-transient-code problem is at its
  worst for 429 in the LLM-gateway world — `budget_exceeded`, exhausted
  quota, and org-level caps all arrive as 429 (#1548). Also note the 524 row
  is annotated "Cloudflare-specific", and its "timeout" substring is the
  loosest of the four.

### Claim 7: Rate-limit tracking is header-driven and per-provider *and* per-API-key, with a documented header table for OpenAI, Anthropic, Azure OpenAI, and a generic fallback
- **Evidence**: The "Supported Headers" table plus the "Header-aware delays"
  and "Per-provider isolation" bullets. The table is reproduced verbatim in
  Concrete Artifacts.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Respects `retry-after` headers from providers" / "Each provider and API key has separate rate limit tracking" / "Promptfoo parses rate limit headers from major providers:"
- **Our assessment**: Buy it, with the operational reading that the isolation
  is a *learning* boundary, not a coordination mechanism. Keying on provider
  **and API key** is correct — two keys on the same provider really do have
  separate limits, and a shared bucket would throttle the wrong workload. But
  because the learned state is per-process-per-run, ten eval runners sharing
  one key each rediscover the same limit from scratch, and the "proactively
  reduce below 10% remaining" rule (Claim 3) fires ten times independently
  against one shared window. The cost of client-side rate-limit discovery is
  therefore paid per runner, per run, and the page's own best-practice #2
  (caching) is the only listed mitigation for request volume. Also worth
  capturing for the guide: the table is the concrete list of headers an
  operator should expect to see, and a provider absent from it (or one that
  renamed its headers) silently falls back to reactive 429-only adaptation.

### Claim 8: Custom providers trigger automatic retry by substring match on the error text — `"429"`, `"rate limit"`, or `"too many requests"` — and supply their own retry timing through `metadata.headers['retry-after']`
- **Evidence**: The "Custom Providers" section's trigger list plus the
  JavaScript metadata snippet (reproduced verbatim in Concrete Artifacts).
- **Confidence**: settled (documented contract; the string matching is
  checkable in the shipped code)
- **Quote**: "Custom providers trigger automatic retry when errors contain: - \"429\" - \"rate limit\" - \"too many requests\"" / "To provide retry timing, include headers in your response metadata:"
- **Our assessment**: Buy the contract, dislike the mechanism, and say both.
  It is the only extensibility contract promptfoo offers a custom provider for
  retry timing, and returning a `retry-after` in metadata is the right shape
  (it lets the server's own timing win). But a **substring match on an error
  message** is a fragile trigger in both directions: a custom provider whose
  errors are structured JSON will not match unless the serialized body happens
  to contain one of those three strings (so it gets *no* retry), while a
  provider whose unrelated error text happens to contain "429" gets a full
  retry storm. Neither failure is detectable from the config. This is the
  concrete mechanism behind #1548: the vendor's own extension point for
  deciding what counts as a rate limit is textual, and it has no room for a
  structured signal that a given 429 is permanent, even if a custom
  provider wanted to supply one.

### Claim 9: The documented way to get deterministic eval behavior is to starve the scheduler of concurrency — `maxConcurrency: 1` plus `delay: 1000` — while the scheduler itself is described as always on
- **Evidence**: The "Disabling Automatic Handling" section (notably, it does
  not describe disabling it) plus its closing sentence. The values are
  identical to the scheduler's own documented floor and the fixed-delay
  example respectively.
- **Confidence**: settled (documented recipe)
- **Quote**: "The scheduler is always active but has minimal overhead. For fully deterministic behavior (e.g., in tests), use:" / "This ensures sequential execution with fixed delays between requests."
- **Our assessment**: Buy the recipe, and note the shape of it: the section
  is titled "Disabling Automatic Handling" but the documented remedy disables
  nothing — it pins concurrency to the value the scheduler would decay *to*.
  Determinism is bought by removing the controller's degrees of freedom, not
  by turning it off, and the one true off-switch
  (`PROMPTFOO_DISABLE_ADAPTIVE_SCHEDULER`) freezes concurrency at the
  configured value while leaving both retry layers live. That matters for CI
  budgeting: a `maxConcurrency: 1` gate is fully deterministic in *ordering*
  and still pays up to 20 wire attempts per failing case (Claim 2), so
  "deterministic" and "cheap" are independent properties here. The unstated
  cost: at concurrency 1 the suite's floor is `cases × delay` (1s per case in
  the documented recipe), which for a few hundred cases is hours of wall clock
  — the determinism recipe is a small-suite tool, and the page presents it as
  a general one.

### Claim 10: The only documented observability surface is six named debug-log events under `LOG_LEVEL=debug`, which together trace the control loop's state transitions
- **Evidence**: The "Debugging" section's command and the "Events logged"
  list (reproduced verbatim in Concrete Artifacts), plus best-practice #3,
  which tells an operator to count `ratelimit:hit` when a run is slow.
- **Confidence**: settled (documented surface)
- **Quote**: "To see rate limit events, enable debug logging:" / "`ratelimit:hit` - Rate limit encountered" / "`concurrency:decreased` / `concurrency:increased` - Adaptive concurrency changes" / "**Monitor debug logs** - If evaluations are slow, check for frequent `ratelimit:hit` events"
- **Our assessment**: Buy it — a named event vocabulary is unusually good
  practice for an eval harness, because it converts an unattributed slow run into a
  decidable question: count `ratelimit:hit` (throughput-bound) versus count
  `concurrency:decreased` without hits (something else is the bottleneck).
  The three limits to carry into the guide: (a) these are **debug-log
  strings, not telemetry** — the page documents no metric, no structured
  sink, and no way to export them, so the signal is only available to someone
  reading a local run's logs; (b) the vocabulary does not name *which* status
  was hit, so a `ratelimit:hit` from a 502-status-text retry and one from a
  genuine 429 are indistinguishable in the documented surface — which is the
  same blind spot as Claim 1; and (c) it does not cover the one failure mode
  with its own knob and its own default (the 300s queue timeout, Claim 11),
  so a run that silently times out queued requests has no event to grep for.

### Claim 11: The documented env-var surface splits cleanly by layer, and the scheduler queue timeout is a hard 5-minute wall-clock bound on waiting that no other section mentions
- **Evidence**: The two env-var tables ("Environment variables for the
  scheduler" and "Environment variables for HTTP-level retry"), reproduced
  verbatim in Concrete Artifacts.
- **Confidence**: settled (documented defaults, directly checkable)
- **Quote**: "`PROMPTFOO_SCHEDULER_QUEUE_TIMEOUT_MS` | Timeout for queued requests (0 to disable) | 300000ms" / "`PROMPTFOO_REQUEST_BACKOFF_MS` | Base delay for HTTP retry backoff | 5000ms"
- **Our assessment**: Buy the table, and pull out the item the page does not
  discuss: `PROMPTFOO_SCHEDULER_QUEUE_TIMEOUT_MS` defaults to **300000ms**
  (5 minutes) with 0 to disable. Under sustained rate limiting, the AIMD
  loop keeps lowering concurrency while requests sit in the scheduler's
  queue — so the queue is exactly where a throttled run accumulates, and
  requests that wait longer than 5 minutes are dropped by a timeout that
  appears in **no** section of this page, in **none** of the six debug events
  (Claim 10), and in neither retry layer (a queued request that never reaches
  the provider is not a failed HTTP request). This is a third, undocumented-
  elsewhere failure mode distinct from retry exhaustion, and it is bounded by
  a knob whose only documentation is a table cell. For a CI gate the useful
  rule is: when an eval run fails with missing or short results under
  rate limiting, check this timeout before blaming the provider. Also note the
  two layers' backoff bases are 10× apart (1s vs 5000ms) and the page never
  states which layer owns the "1s, 2s, 4s" figures quoted for 5xx retries.

### Claim 12: OpenAI's request and token limits are tracked separately, but the page's entire control surface is a *concurrency* count — there is no documented token-rate or request-rate control
- **Evidence**: The "OpenAI" provider note, its inline example comment, and
  the "Anthropic" note. The configuration sections offer only `maxConcurrency`
  and `delay` as rate-shaping knobs.
- **Confidence**: settled (documented tracking behavior; the *absence* of a
  token-rate knob is stated as absence, per the convention used elsewhere in
  this corpus)
- **Quote**: "OpenAI has separate rate limits for requests and tokens. The scheduler tracks both. For high-volume evaluations:" / "maxConcurrency: 20 # Scheduler will adapt down if needed" / "Anthropic rate limits are typically per-minute. The scheduler respects `retry-after` headers from the API."
- **Our assessment**: Buy the tracking claim; flag the gap in the control
  surface. Because the only lever is a count of in-flight requests, the
  harness's request rate is a function of request *latency* as well as
  concurrency — a suite whose prompts get longer (more tokens per request) or
  whose provider gets slower pushes token-per-minute over the limit while
  `maxConcurrency` still reads 20 and the config diff shows nothing. The AIMD
  loop will then halve concurrency repeatedly and the run will crawl rather
  than fail cleanly, because there is no documented way to state a token-rate
  budget. That is a real gap for a token-billed system where the scarce
  resource is tokens, not in-flight requests, and it is not something the
  start-with-higher-concurrency advice (Claim 4) accounts for. Anthropic's
  per-minute window plus `retry-after` respect is the documented mitigation
  for that provider.

### Claim 13: The page's framing is that rate-limit handling "requires no configuration" — and the configuration it then documents is exclusively *reactive* (retry, backoff, adaptive concurrency), with no static per-provider rate cap anywhere in its surface
- **Evidence**: The "Automatic Handling" section's lead sentence, read against
  the full config/env-var surface: `maxConcurrency`, `delay`, `maxRetries`, and
  five `PROMPTFOO_*` variables, none of which caps a request rate.
- **Confidence**: settled (the sentence and the absence are both on the page;
  the comparison to a sibling page's static cap is in Our assessment and
  Cross-References)
- **Quote**: "Rate limit handling is built into the evaluator and requires no configuration:"
- **Our assessment**: Buy the sentence as the vendor's framing, and treat the
  surface it enumerates as the real finding: every documented control here
  reacts *after* a limit is discovered, and none of them states a rate the
  harness will not exceed. That is a defensible design for an unknown-quota
  client, but it means an operator who *does* know the quota has no
  first-class way to say so on this page — and a sibling promptfoo page does
  document a static per-provider cap that this page never mentions (see
  **Extends**: `docs-promptfoo-modular-configs.md` Claim 3,
  `requestsPerMinute: 100` / `50`). The guide should present these as two
  distinct surfaces with different failure modes: a static cap fails fast and
  visibly when mistyped-unsupported, an adaptive loop degrades quietly. I am
  not filing this as a contradiction — this page's sentence is scoped to
  *automatic handling* (retry/backoff/adaptation), not to rate caps, so the
  two claims are about different things; it is a cross-page documentation gap
  and the resolver/Assayer should see it as one.

### Claim 14: `delay` is additive to rate-limit backoff and is reachable three ways — YAML `evaluateOptions.delay`, CLI `--delay`, and env var `PROMPTFOO_DELAY_MS` — making it a hard floor on run time rather than a throttle
- **Evidence**: The "Fixed Delay" section, with its three configuration routes
  and the parenthetical that fixes its relationship to backoff.
- **Confidence**: settled (documented semantics and config routes)
- **Quote**: "Add a fixed delay between requests (in addition to any rate limit backoff):" / "PROMPTFOO_DELAY_MS=1000 promptfoo eval"
- **Our assessment**: Buy it, and read the parenthetical as the load-bearing
  part: delay *stacks* with backoff rather than replacing it, so it is not a
  rate-limiter you can trade off against the adaptive loop — it is a floor
  added to whatever the loop is already doing. The practical consequence is
  a lower bound on wall clock of roughly `cases × delay / realized
  concurrency`, which is exactly the cost the determinism recipe (Claim 9)
  pays. This is also the only knob on the page with an env-var route that the
  tables do not list, which is worth knowing when a CI job needs to slow an
  eval down without a config change: `PROMPTFOO_DELAY_MS` is settable in the
  job environment where `evaluateOptions` is not.

## Concrete Artifacts

### Supported rate-limit headers (verbatim from the "Supported Headers" table)

| Provider     | Headers                                                                                                          |
| ------------ | ---------------------------------------------------------------------------------------------------------------- |
| OpenAI       | `x-ratelimit-remaining-requests`, `x-ratelimit-limit-requests`, `x-ratelimit-remaining-tokens`, `retry-after-ms` |
| Anthropic    | `anthropic-ratelimit-requests-remaining`, `anthropic-ratelimit-tokens-remaining`, `retry-after`                  |
| Azure OpenAI | `x-ratelimit-remaining-requests`, `retry-after-ms`, `retry-after`                                                |
| Generic      | `retry-after`, `ratelimit-remaining`, `ratelimit-reset`                                                          |

*(Attribution: promptfoo docs "Rate Limits > Automatic Handling > Supported Headers".)*

### Transient-error retry table (verbatim from the "Transient Error Handling" table)

| Status Code | Description         | Retry Condition                                      |
| ----------- | ------------------- | ---------------------------------------------------- |
| 502         | Bad Gateway         | Status text contains "bad gateway"                   |
| 503         | Service Unavailable | Status text contains "service unavailable"           |
| 504         | Gateway Timeout     | Status text contains "gateway timeout"               |
| 524         | A Timeout Occurred  | Status text contains "timeout" (Cloudflare-specific) |

*(Attribution: promptfoo docs "Rate Limits > Automatic Handling > Transient Error Handling".)*

### Scheduler env-var table (verbatim)

| Environment Variable                   | Description                                | Default  |
| -------------------------------------- | ------------------------------------------ | -------- |
| `PROMPTFOO_DISABLE_ADAPTIVE_SCHEDULER` | Disable adaptive concurrency (use fixed)   | false    |
| `PROMPTFOO_MIN_CONCURRENCY`            | Minimum concurrency (floor for adaptive)   | 1        |
| `PROMPTFOO_SCHEDULER_QUEUE_TIMEOUT_MS` | Timeout for queued requests (0 to disable) | 300000ms |

*(Attribution: promptfoo docs "Rate Limits > Configuration > Backoff Configuration".)*

### HTTP-level retry env-var table (verbatim)

| Environment Variable           | Description                       | Default |
| ------------------------------ | --------------------------------- | ------- |
| `PROMPTFOO_REQUEST_BACKOFF_MS` | Base delay for HTTP retry backoff | 5000ms  |
| `PROMPTFOO_RETRY_5XX`          | Retry on HTTP 500 errors          | false   |

*(Attribution: promptfoo docs "Rate Limits > Configuration > Backoff Configuration".)*

### Concurrency control (verbatim from "Configuration > Concurrency")

```yaml
evaluateOptions:
  maxConcurrency: 10
```

```bash
promptfoo eval --max-concurrency 10
```

### Fixed delay (verbatim from "Configuration > Fixed Delay")

```yaml
evaluateOptions:
  delay: 1000 # milliseconds
```

```bash
promptfoo eval --delay 1000
```

```bash
PROMPTFOO_DELAY_MS=1000 promptfoo eval
```

### Fail-fast: disable retries for one provider (verbatim from "Backoff Configuration")

```yaml
providers:
  - id: openai:chat:gpt-4.1-mini
    config:
      maxRetries: 0
```

*(Doc caption, verbatim: "Example — disable retries for a provider to fail fast on rate limits:")*

### HTTP-level retry tuning (verbatim from "Backoff Configuration")

```bash
PROMPTFOO_REQUEST_BACKOFF_MS=10000 PROMPTFOO_RETRY_5XX=true promptfoo eval
```

### High-volume evaluation (verbatim from "Provider-Specific Notes > OpenAI")

```yaml
evaluateOptions:
  maxConcurrency: 20 # Scheduler will adapt down if needed
```

### Custom provider retry timing (verbatim from "Provider-Specific Notes > Custom Providers")

```javascript
return {
  output: 'response',
  metadata: {
    headers: {
      'retry-after': '60', // seconds
    },
  },
};
```

### Debug event vocabulary (verbatim from "Debugging")

```bash
LOG_LEVEL=debug promptfoo eval -c config.yaml
```

- `ratelimit:hit` - Rate limit encountered
- `ratelimit:learned` - Provider limits discovered from headers
- `ratelimit:warning` - Approaching rate limit threshold
- `concurrency:decreased` / `concurrency:increased` - Adaptive concurrency changes
- `request:retrying` - Retry in progress

### Deterministic run (verbatim from "Disabling Automatic Handling")

```yaml
evaluateOptions:
  maxConcurrency: 1
  delay: 1000
```

*(Doc caption, verbatim: "The scheduler is always active but has minimal overhead. For fully deterministic behavior (e.g., in tests), use:")*

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/rate-limits — sections as noted. Code blocks and tables are copied from the page's own markdown source (`site/docs/configuration/rate-limits.md`), which was diffed against the rendered page; line breaks inside YAML/JS blocks are as authored upstream.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-google-sre-address-cascading-failures.md` **Claim 4**
    ("Retry amplification across service layers follows a product, not a sum — a
    3-layer system with 4 attempts per layer produces 4³ = 64 database
    attempts per single user action") — this page documents that product
    *inside one harness*: two retry layers (Claim 2) whose defaults multiply
    to up to 20 wire attempts per logical request. The Google SRE chapter
    supplies the general law; promptfoo is a live, config-checkable instance
    of it, and the guide's per-layer retry-budget rule has a concrete
    counterexample to point at. (Verified: Claim 4 heading and the 4³ worked
    example.)
  - `source-notes/docs-google-sre-address-cascading-failures.md` **Claim 5**
    ("Retry policies must use randomized exponential backoff, bound
    per-request retry counts, employ server-wide retry budgets, and never
    retry permanent errors") — Claim 6 is the vendor independently
    implementing the fourth guideline (never retry permanent errors) with a
    second-signal check, and the two-layer design is a per-request retry bound
    (Claim 2). The one guideline this page's *documented contract* does not
    honor is the first: the page specifies fixed intervals ("1s, 2s, 4s")
    and never mentions jitter, and the guide's "randomized" requirement has no
    documented counterpart here. (Verified: Claim 5 heading and quote
    "Always use randomized exponential backoff when scheduling retries.")
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 7**
    ("Rate limit responses (HTTP 429) are handled automatically with
    exponential backoff; HTTP 500 responses are retried only when
    `PROMPTFOO_RETRY_5XX=true` — retry behavior sits directly beside caching in
    the same pipeline") — this page is the authoritative source behind that
    claim: it supplies the layer architecture, the `PROMPTFOO_RETRY_5XX`
    default (`false`), the env-var table, and the fact that 502/503/504/524
    are retried on a *different* rule from 500. Note the correction to the
    sibling's framing: 500 is not the only 5xx the harness retries by default,
    and the 5xx retry that *is* on by default is the status-text-gated one
    (Claim 6). (Verified: #1275 Claim 7.)
  - `source-notes/docs-promptfoo-configuration-outputs.md` **Claim 3**
    ("`failure` is reserved for failed assertions and `error` for
    provider/runtime errors, explicitly so CI can tell incorrect model behavior
    apart from an execution fault") — the retry contract decides which of
    those two a rate-limited gate goes red through: a case that exhausts both
    retry layers surfaces as a provider/runtime error, not an assertion
    failure, so the JUnit split is the mechanism by which "the provider was
    rate-limiting us" stays distinguishable from "the model regressed" in CI
    output. (Verified: Claim 3 heading and quote.)

- **Contradicts**:
  - **#1548** — HTTP 429 retryability. `source-notes/docs-litellm-a2a-iteration-budgets.md`
    **Claim 5** ("Over-cap responses are HTTP 429 with `"type":
    "budget_exceeded"` ... a *cost* cap surfaces as the same status class as
    ordinary rate limiting and cannot be distinguished by status code alone")
    holds that a caller must inspect the error body before retrying a 429.
    This page documents the opposite default for a client: 429 →
    auto-retry with exponential backoff, with no body-level discrimination
    anywhere in its surface and a substring-only trigger for custom
    providers (Claim 8). The two cannot both be the guide's prescription for
    the same status code, and the composition case is live — promptfoo targets
    OpenAI-compatible endpoints, so a LiteLLM gateway enforcing a session
    budget can sit on the other end of this contract. Filed as
    [#1548](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1548);
    per MINER.md §4a **no verdict is picked here** — the guide-side resolution
    is the resolver's call. (Verified: #1331 Claim 5.)
  - `source-notes/docs-litellm-batches-api.md` **Claim 1** / **Claim 3** add a
    third non-transient 429 producer to the same family (batch admission
    returns 429 before forwarding; `batch_enqueued_token_limit` overage is
    also a 429) rather than opposing this page; noted in #1548 so the
    resolver sees the whole 429-status family. (Verified: Claim 1 and Claim 3
    headings.)

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-caching.md` — extends the
    caching note's single retry bullet (#1275 Claim 7) into the full control
    architecture: the two layers, the propagation rule, the AIMD scheduler,
    the env-var defaults, and the debug event vocabulary. The caching note
    also supplies the reason the request-volume lever matters more than the
    concurrency lever (its Claims 4 and 8: a 14-day TTL and per-repeat
    namespaces mean a warm-cache run needs no rate-limit budget at all), which
    is why this page's own best practice #2 is the load-bearing one.
  - `source-notes/docs-promptfoo-chat-threads.md` **Claim 1** ("When a prompt
    references `_conversation` as a Nunjucks variable, the eval runs
    single-threaded (concurrency of 1) — a silent parallelism loss with no
    config knob to restore it") — this page is the complementary side: it
    documents what the scheduler does with concurrency when it is *not*
    pinned. The sharp finding is the collision — concurrency 1 is also the
    scheduler's documented floor (`PROMPTFOO_MIN_CONCURRENCY` default 1), so
    for `_conversation` suites the entire adaptive surface is inert and
    `maxConcurrency` cannot help. (Verified: Claim 1 heading.)
  - `source-notes/docs-promptfoo-modular-configs.md` **Claim 3** ("Rate-limit
    policy is expressed *in the environment's provider file*, not in the test
    suite — the documented per-provider caps (`requestsPerMinute: 100` for the
    OpenAI provider, `50` for the Anthropic provider) sit in
    `configs/providers-prod.yaml`") — a **second, non-overlapping rate-limit
    surface in the same product**: a static per-provider cap on a sibling
    page that this page never mentions. Together the two notes give the guide
    both modes (static cap vs adaptive loop) and the two distinct failure
    modes that follow from them. This page's contribution is that its own
    surface is entirely reactive (Claim 13). (Verified: Claim 3 heading and
    the `requestsPerMinute` values.)
  - `source-notes/docs-google-sre-handling-overload.md` **Claim 3**
    ("Synchronized client retries without jitter and exponential backoff
    produce thundering herd spikes up to 20× normal peak RPS — fix with
    truncated exponential backoff + jitter") and **Claim 12** ("Soft quotas
    should not throttle when the system has remaining capacity (work
    conservation); hard quotas exist to protect infrastructure and cannot be
    exceeded") — general backoff/overload theory that this page implements
    concretely on the *client* side, and inverts on one point: promptfoo's
    AIMD loop is a per-run, per-process controller with no shared state, so
    there is no work conservation across runners — every runner throttles
    itself against the same window independently, which is the client-side
    analogue of (and a partial answer to) the thundering-herd problem, and no
    answer at all to the fairness rule in Claim 12. (Verified: Claim 3 and
    Claim 12 headings and quotes.)
  - `source-notes/docs-promptfoo-configuration-huggingface-datasets.md`
    **Claim 9** ("Hermeticity is restored only *after* the first fetch, and
    only for a saved run ... nothing on this page documents retry, backoff, or
    timeout for the fetch that gets them") — this page is the answer to that
    note's stated gap for the *provider* hop: provider calls get two retry
    layers, an adaptive scheduler, header awareness, and a 5-minute queue
    timeout. The asymmetry that note flagged is therefore sharper than it
    looked — input acquisition from HuggingFace has no documented policy
    while provider calls have a thoroughly documented one. (Verified: Claim 9
    heading.)

- **Novel**: This is the first corpus source on **eval-harness-side rate-limit
  control**, and every one of the following is net-new material:
  1. **The AIMD concurrency contract** (Claims 3–5) — halve / +1 / preemptive
     sub-10% cut, and the `maxConcurrency`-is-a-ceiling asymmetry. The corpus
     had backoff and overload *theory* (Google SRE notes) and gateway-side
     quota *enforcement* (LiteLLM notes) but no documented client-side
     controller.
  2. **The two-layer retry taxonomy and its propagation rule** (Claim 2) —
     including the arithmetic nobody publishes (up to 20 wire attempts per
     logical request at defaults) and `maxRetries: 0` as the one total
     fail-fast switch.
  3. **Status-text-gated 5xx retry with the stated rationale** (Claim 6) — a
     vendor-independent pattern the guide can lift on its own merits.
  4. **The 300-second scheduler queue timeout** (Claim 11) as a third failure
     mode, invisible in the debug event vocabulary.
  5. **The absence of any token-rate or request-rate control** (Claim 12) on a
     page whose only lever is a concurrency count, in a product billed per
     token.
  6. **The six-event debug vocabulary** (Claim 10) as the corpus's only
     documented run-level observability surface for a rate-limit control loop.
  The guide currently has **no** coverage of eval-harness rate-limit
  *control*: `maxConcurrency` appears in no chapter file, and the only
  rate-limit material in Ch05 is the 429 disambiguation (the
  `budget_exceeded` alert rule, `guide/05-llm-ops-reliability.md:1204`) plus
  the rolling-window framing. Ch05 does cover LiteLLM's *adaptive router*, but
  that is a gateway-side quality/cost bandit, not a client-side concurrency
  controller — different layer, different failure modes. So the AIMD contract
  and the two-layer retry taxonomy are entirely new.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — new section: rate-limit control belongs
  to the harness, and it is a control loop, not a dial.** Add the AIMD
  contract as a named pattern with its three rules and its one-sided ceiling
  (Claims 3–5), and state the operational consequence the vendor does not:
  realized concurrency is state-dependent and per-run, so eval wall-clock is
  not derivable from config and a slow run is diagnosed from the debug event
  counts (`ratelimit:hit` vs `concurrency:decreased` without hits), not from
  the config diff (Claim 10). The rule to state: set `maxConcurrency` as a
  cheap probe, never as a throughput commitment, and do not adopt "set it high
  and the scheduler finds the optimal rate" as validated practice — it is
  published with no measurements (Claim 4).
- **Chapter 05 — retry policy for eval and agent traffic: budget the product,
  not the layer.** Add promptfoo's two-layer taxonomy (scheduler 3/1s vs HTTP
  4/5000ms, unified by one `maxRetries`) as the concrete worked example for
  the per-layer retry-budget rule already implied by
  `docs-google-sre-address-cascading-failures.md` Claim 4, with the derived
  worst case of up to 20 wire attempts per logical request and the explicit
  `maxRetries: 0` fail-fast switch for gates that must not burn quota proving
  a limit exists (Claim 2). Pair it with the status-text-gating pattern
  (Claim 6) as a vendor-independent rule for any retry policy keyed on a
  status class, and note that the guide's randomized-backoff requirement has
  no documented counterpart in this page's contract.
- **Chapter 05 — the 429 status-code collision, cross-linked to #1548.** The
  existing text already warns that callers treating 429 as transient-retryable
  will retry an unsatisfiable session. This page documents a mainstream eval
  harness whose *documented* default does exactly that, with no body-level
  discrimination (Claims 1, 7). Until #1548 is resolved the guide should carry
  both claims as a `**Debated:**` pair and state the practical rule that is
  safe under either: check the error body before retrying a 429, and do not
  rely on a harness default that treats every 429 as transient.
- **Chapter 05 — the concurrency floor collision with multi-turn suites.**
  Add the cross-reference the chat-threads note's Claim 1 needs: a
  `_conversation` suite already runs at concurrency 1, which equals the
  scheduler's documented floor, so the whole adaptive surface is inert there
  and the only remaining rate tools are `delay`, `maxRetries`, and caching
  (Claim 5, Claim 14).
- **Chapter 05 — three distinct eval-throughput failure modes, not one.** Add
  the taxonomy: retry exhaustion (both layers), scheduler queue timeout at
  300s with no debug event (Claim 11), and cache-cold request volume
  (`docs-promptfoo-configuration-caching.md` Claims 4/8). A CI run that is
  slow or returns short results under rate limiting has three different root
  causes with three different knobs, and the documented log surface only
  names the first.
- **Chapter 02 (Observability) — debug events as a control-loop trace.** Add
  the six named events (Claim 10) as the pattern for making an adaptive
  controller observable, with the honest limits stated: debug-log strings
  rather than exported metrics, no per-status discrimination, and no event for
  the queue timeout. If the guide wants a rate-limit *signal*, this is the
  vocabulary to standardize on and the gap to instrument.
- **Chapter 05 — a second rate-limit surface, and its different failure mode.**
  Cross-link `docs-promptfoo-modular-configs.md` Claim 3's static
  `requestsPerMinute` cap against this page's entirely reactive surface
  (Claims 13, 14): a static cap states a rate the harness will not exceed and
  fails visibly if unsupported; an adaptive loop degrades quietly. A guide
  rule that follows: if you know the quota, say so statically; if you don't,
  expect discovery cost per run per runner.
- **Chapter 03 (Runbooks and Agents) — CI gate determinism vs cost.** Document
  the `maxConcurrency: 1` + `delay: 1000` recipe and what it actually buys
  (ordering determinism at roughly `cases × delay` of wall clock, with both
  retry layers still live) versus what it does not (a cheaper run, or a
  disabled scheduler) (Claims 9, 14). Also add `PROMPTFOO_DELAY_MS` as the
  env-var-only throttle for jobs that cannot change config (Claim 14).

## Extraction Notes

- Source read in full via direct fetch of the rendered page
  (https://www.promptfoo.dev/docs/configuration/rate-limits), then diffed
  against the page's own markdown source
  (`site/docs/configuration/rate-limits.md` in promptfoo/promptfoo @ main
  `94119b67`, retrieved 2026-10-02) so that every quote and every code block
  is character-for-character as authored upstream rather than as re-rendered
  by HTML extraction. The two agree; no content is present in one and absent
  from the other. Single self-contained page; the two links out (the caching
  page and the OpenAI provider troubleshooting page) were not followed as
  extraction targets — the caching page is already covered by
  `docs-promptfoo-configuration-caching.md` (#1275), and the OpenAI
  troubleshooting anchor is a provider reference rather than a rate-limit
  contract.
- **Implementation cross-check (not a claim source).** Because this page is a
  vendor's description of its own code, I checked the shipped implementation
  in `promptfoo/promptfoo` @ main `94119b67` (2026-10-02) to calibrate
  confidence. The code confirms most of the page and exposes three gaps that
  belong in the guide's framing rather than in the claims (claims and quotes
  above are strictly page-sourced):
  1. `src/scheduler/adaptiveConcurrency.ts` implements the *decrease* and
     *proactive* rules as documented (`BACKOFF_FACTOR = 0.5`, and a
     linear-scaling proactive cut — at 10% remaining it keeps 60% of current,
     at 5% 40%, at 1% ~24%, which the page does not publish) but implements
     the *increase* as `RECOVERY_FACTOR = 1.5` (×1.5, ceiling) after 5
     consecutive successes, **not** the "+1" the page documents. The page's
     additive-increase description is therefore not what ships, which is
     further reason not to treat Claim 3's "settled" as "this controller has
     been measured."
  2. `src/scheduler/retryPolicy.ts` sets `DEFAULT_RETRY_POLICY` to 3 retries /
     1000ms base — matching the page's scheduler layer and its "1s, 2s, 4s" —
     but also applies a **0.2 jitter factor** and a 60000ms cap. The page
     never mentions jitter or the cap, so the guide's "randomized exponential
     backoff" requirement is in fact met by the implementation and absent from
     the documentation; the reverse of the usual vendor-doc gap.
  3. `src/scheduler/retryPolicy.ts` `shouldRetry()` returns `false` **before**
     the rate-limit path when the error is a rate-limit error whose structured
     `kind` is `quota`, with the comment: "Hard quotas (insufficient_quota,
     billing_hard_limit_reached, …) won't resolve on retry — retrying just
     amplifies load against an exhausted account. The transport already fails
     fast, but isRateLimited may still be true via substring match, so check
     the structured signal before the rate-limit retry path." So the shipped
     scheduler *does* implement the body-level discrimination Claim 1's
     documentation lacks — which is the substance of Side B in #1548, and the
     reason that issue's verdict is `debated` rather than a clean win for one
     side. Two things remain open there: whether the transport maps a
     LiteLLM-style `type: budget_exceeded` body onto that `kind: 'quota'`
     signal, and the fact that the documented custom-provider trigger
     (Claim 8) is substring-only.
  4. `src/util/fetch/index.ts` confirms the HTTP layer exactly as documented
     (`maxRetries ?? contextMaxRetries ?? 4`, `PROMPTFOO_REQUEST_BACKOFF_MS`
     default 5000, `isTransientError()` matching 502/503/504/524 on lowercased
     `statusText`, transient retries suppressed via the retry context when a
     provider sets `maxRetries: 0`) — with one wording mismatch: the
     `PROMPTFOO_RETRY_5XX` gate fires on the whole `status >= 500 &&
     status < 600` range, while the page's table describes it as "Retry on
     HTTP 500 errors."
  5. `src/scheduler/rateLimitKey.ts` shows the isolation key is the provider id
     plus a SHA-256 digest (12 hex chars) of `apiKey` **last four characters**,
     `apiBaseUrl`, `region`, and `organization` — confirming the page's
     per-provider/per-key claim and adding an operational wrinkle worth a
     guide line: two keys sharing a last-four suffix and base URL share a rate
     limit bucket in the scheduler.
- **Config-schema cross-check.** The machine-readable schema
  (`site/static/config-schema.json` @ `94119b67`) **does** type this page's
  two knobs — `evaluateOptions.maxConcurrency` is an integer with
  `exclusiveMinimum: 0` and `evaluateOptions.delay` an integer defaulting to
  0 — so a typo in either is caught by schema validation. It contains **zero**
  occurrences of `requestsPerMinute`, independently re-confirming the gap
  recorded in `docs-promptfoo-modular-configs.md` Claim 3's assessment. The
  guide can therefore distinguish the two rate-limit surfaces by whether a
  typo fails loudly or silently.
- `confidence_overall` is `emerging`, per the triage caveat. The config
  surface, env-var defaults, and retry/status-text rules (Claims 2, 5–14
  mechanism-level) are settled *as documented product behavior* and are
  independently checkable — most of them I confirmed against the shipped
  source. Two things hold the overall grade at `emerging`: the page publishes
  **no measurements** for the scheduler (no convergence time, no throughput,
  no cost), so Claims 3–4 carry an unvalidated control loop; and Claim 1's
  documented contract is contradicted by the shipped implementation, which
  means the documentation cannot be treated as a complete spec even where it
  is the vendor's own.
- **Candidate handling** (from `miner-related-notes.md`, read before
  Cross-References; each candidate cited or dismissed by name):
  - `docs-litellm-batches-api.md` — **cited** under Contradicts (Claim 1 and
    Claim 3 as further non-transient 429 producers in the same family as
    #1548). Its other claims (per-record token reservation, 8-day reservation
    expiry) are gateway-side accounting and do not intersect this page.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent spectrum and
    write-guardrail guidance; no rate-limit or retry surface; dismissed.
  - `docs-promptfoo-deterministic-metrics.md` — assertion-type taxonomy
    (deterministic vs model-graded); unrelated to request scheduling;
    dismissed.
  - `docs-promptfoo-pi-scorer.md` — model-graded scorer determinism; a
    grading-layer claim, not a request-layer one; dismissed.
  - `docs-google-sre-team-lifecycles.md` — SRE org/lifecycle chapters;
    dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` — red-team methodology and CI/CD
    placement; same vendor, no rate-limit surface; dismissed.
  - `docs-promptfoo-configuration-outputs.md` — **cited** under Corroborates
    (Claim 3: the `failure` vs `error` JUnit split is how a rate-limited gate
    stays distinguishable from a model regression). Its other four claims
    (JUnit structure, lossy export, redaction) are output-format concerns;
    dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge alert triage and SRE
    Agent connectors; the closest thing here is the "judge alert is not a
    broken-service alert" framing, which is a signal-design point about
    alerting, not about harness rate limits; dismissed.
  - `docs-promptfoo-classifier-grading.md` — HF classifier thresholds and
    detector portability; dismissed.
  - `docs-promptfoo-javascript-assertions.md` — assertion failure semantics
    (Claim 2, fail-closed on throw) sit one layer above this page's request
    layer; nothing here changes them; dismissed.
  - Additional cross-references found by searching `source-notes/` myself
    (per MINER.md §4): `docs-promptfoo-configuration-caching.md`,
    `docs-promptfoo-chat-threads.md`, `docs-promptfoo-modular-configs.md`,
    `docs-promptfoo-configuration-huggingface-datasets.md`,
    `docs-google-sre-address-cascading-failures.md`,
    `docs-google-sre-handling-overload.md`, and
    `docs-litellm-a2a-iteration-budgets.md`. Every `Claim N` cited above was
    re-read and confirmed to resolve to a real numbered claim in the correct
    document order (MINER.md §4b), and every quoted passage from another note
    was copied from that note rather than reconstructed.
- One contradiction filed: **#1548**, before this PR, per MINER.md §4a. No
  verdict is asserted here; the source note points at the issue and the
  resolver assigns the `C-NNN` entry. I checked the open `contradiction`-labeled
  issues first — #1534, #1517, #1514, #1486, #1462, #1461, #1408, #1352, #1338,
  #1322, #1307, #1150 — and none covers 429 retryability, so this is not a
  duplicate. `CONTRADICTIONS.md` has no `C-NNN` entries yet.
- I deliberately did **not** file a second contradiction for the two judgment
  calls this extraction surfaced, and record the reasoning so the Assayer can
  overrule: (a) the `requestsPerMinute` gap (Claim 13) — this page's
  "requires no configuration" is scoped to *automatic handling*, so the
  sibling page's static cap is a different claim, not an opposing one; (b) the
  "+1 vs ×1.5" increase-rule gap — that is a documentation-versus-
  implementation mismatch within one vendor, not a conflict between two
  corpus claims, so it belongs in this note's implementation cross-check and
  not in `CONTRADICTIONS.md`.
