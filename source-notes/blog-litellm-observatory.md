---
source_url: https://docs.litellm.ai/blog/litellm-observatory
source_type: blog-post
title: "Improve Release Stability With Long-Running Load Tests — LiteLLM Observatory"
author: "Alexsander Hamir (Performance Engineer, LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-02-06
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: settled
issue: "#551"
---

# LiteLLM Observatory: Long-Running Release-Validation Load Testing for an LLM Gateway Proxy

> This blog post introduces LiteLLM Observatory, a long-running release-validation
> testing system for LiteLLM's LLM gateway proxy. It describes the system
> architecture (API-triggered tests, smart queueing, background execution, Slack
> notification), the specific `TestOAIAzureRelease` (3-hour duration, <1% pass/fail
> threshold, same-HTTP-client reuse across the run), concrete failure metrics from
> a v1.81.3 HTTP client lifecycle bug (40% → 0.001% failure rate), and how the
> Observatory complements unit tests by catching regressions that only surface
> under sustained real-world conditions.

## Source Context

- **Type**: blog-post (vendor engineering blog), tagged `testing`, `observability`,
  `reliability`, `releases`.
- **Author credibility**: High — authored by LiteLLM's Performance Engineer
  (Alexsander Hamir), CEO (Krrish Dholakia), and CTO (Ishaan Jaffer). The post
  describes a system built and operated by the LiteLLM team. System architecture
  is authoritative (vendor-authored for their own tooling). The bug metrics are
  specific, named, and independently plausible.
- **Scope**: Covers (1) architecture of the LiteLLM Observatory testing system
  — how it works, the test flow (start → smart queue → instant response →
  background execution → Slack notification), (2) the `TestOAIAzureRelease` test
  case with its 3-hour duration, <1% pass/fail threshold, and same-HTTP-client
  reuse, (3) the v1.81.3 HTTP client lifecycle bug that motivated the system,
  with before/after metrics, (4) use cases (pre-deploy, routine validation, issue
  investigation, long-running failure detection). Does NOT cover: configuration
  of the Observatory tool itself, deployment instructions, or integration with
  specific CI/CD platforms beyond Slack.

## Extracted Claims

### Claim 1: LiteLLM Observatory is a long-running release-validation testing system for LLM gateway proxies, triggered via API requests with results posted to Slack
- **Evidence**: Detailed system architecture description — the test flow starts
  with an API request specifying deployment URL/API key, test name (e.g.,
  `TestOAIAzureRelease`), and test settings; results are automatically posted to
  Slack upon completion.
- **Confidence**: settled
- **Quote**: "The LiteLLM Observatory is a testing service that runs long-running
  tests against LiteLLM deployments. Tests are triggered by sending API requests,
  and results are automatically sent to Slack when tests complete."
- **Our assessment**: A factual description of the system by the team that built
  it. The architecture is specific and internally consistent. We buy this as
  describing how the system works.

### Claim 2: The test flow uses smart queueing — duplicate tests are rejected to avoid wasted resources, and up to 5 tests run concurrently by default
- **Evidence**: Explicit description of the queueing mechanism under "Smart Queueing."
- **Confidence**: settled
- **Quote**: "The system checks whether the exact same test is being attempted more
  than once. If a duplicate test is already running or queued, an error is returned
  to avoid wasting resources. Otherwise, the test is added to a queue and runs when
  capacity is available (up to 5 tests concurrently by default)."
- **Our assessment**: A practical resource-management pattern. Deduplication at the
  API layer prevents redundant load on the deployment under test. The concurrent
  cap is a reasonable default. We buy this as the system's operational design.

### Claim 3: The API responds immediately (milliseconds) even though tests run for hours — tests execute asynchronously in the background
- **Evidence**: "Instant Response" section explicitly states the API returns in
  milliseconds while the test runs asynchronously.
- **Confidence**: settled
- **Quote**: "The API responds immediately — the request itself completes in
  milliseconds, even though tests may run for hours."
- **Our assessment**: Standard async request-acceptance pattern. The quick API
  response is a UX decision for integration into deployment pipelines. We buy this
  as the system's design.

### Claim 4: `TestOAIAzureRelease` runs continuously for 3 hours, cycling through specified models, with a pass/fail threshold of <1% failure rate
- **Evidence**: Explicitly documented test parameters under "The OpenAI / Azure
  Reliability Test" subsection — duration, behavior, pass/fail criteria.
- **Confidence**: settled
- **Quote**: "Duration: Runs continuously for 3 hours / Behavior: Cycles through
  specified models (such as gpt-4 and gpt-3.5-turbo), issuing requests continuously
  / Pass / Fail Criteria: The test passes if fewer than 1% of requests fail. If the
  failure rate exceeds 1%, the test fails and the team is notified in Slack."
- **Our assessment**: Clear, operational test specification. The 1% threshold is a
  specific reliability bar that can be used as a reference for other LLM gateway
  release-validation setups.

### Claim 5: The same HTTP client is reused for the entire 3-hour test run to detect lifecycle-related bugs that only appear under prolonged reuse
- **Evidence**: Explicit "Key Detail" callout within the `TestOAIAzureRelease` test
  description, with the motivation tied directly to the v1.81.3 bug.
- **Confidence**: settled
- **Quote**: "Key Detail: The same HTTP client is reused for the entire run,
  allowing detection of lifecycle-related bugs that only appear under prolonged reuse"
- **Our assessment**: A deliberate testing design choice that directly targets the
  failure class LiteLLM has encountered in production (HTTP client lifecycle bugs).
  The same-client-reuse pattern is specifically designed to reproduce the conditions
  under which the v1.81.3 bug manifested. This is a concrete, actionable testing
  technique for LLM gateway operators.

### Claim 6: The v1.81.3 HTTP client lifecycle bug — a cached httpx client with a 1-hour TTL was closed on cache expiry while a higher-level client still held a reference — caused a 40% failure rate
- **Evidence**: Before/after metrics table with exact provider-specific request
  counts. The mechanism is described: cached httpx client with 1-hour TTL; when
  cache expired, the connection was closed; a higher-level client still held a
  reference; subsequent requests failed.
- **Confidence**: settled
- **Quote**: "A cached httpx client was configured with a 1-hour TTL / When the
  cache expired, the underlying HTTP connection was closed as expected / A
  higher-level client continued to hold a reference to that connection / Subsequent
  requests failed with: 'Cannot send a request, as the client has been closed'"
- **Our assessment**: The failure mechanism is clearly described and the metrics
  (before: 40% failure rate with 288,000 failures out of 720,000 OpenAI requests;
  after: 0.001% with 12 failures out of 1,200,000) are specific and plausible. This
  is the same class of bug documented in the separate incident report
  `failure-litellm-httpx-cache-eviction.md` (Feb 2026), but appears to be an earlier
  manifestation. The post uses this bug as the primary motivation for building the
  Observatory.

### Claim 7: After the fix, the failure rate dropped from 40% to 0.001% for OpenAI and from 40% to 0.002% for Azure, with total request volumes more than doubling
- **Evidence**: Before/after comparison table directly in the source.
- **Confidence**: settled
- **Quote**: Before: "OpenAI — 720,000 requests, 432,000 success, 288,000 failures,
  40% fail / Azure — 692,000 requests, 415,200 success, 276,800 failures, 40% fail"
  After: "OpenAI — 1,200,000 requests, 1,199,988 success, 12 failures, 0.001% fail /
  Azure — 1,150,000 requests, 1,149,982 success, 18 failures, 0.002% fail"
- **Our assessment**: The absolute numbers are striking — from 288,000 failures down
  to 12, with request volume nearly doubling (720k → 1.2M). The 0.001% level is
  effectively zero. The request volume increase suggests the fix also removed a
  bottleneck that was throttling throughput. We buy these numbers as published by
  the vendor.

### Claim 8: Unit tests do not cover real provider behavior, long-lived network interactions, resource lifecycle edge cases, or time-dependent regressions — Observatory fills these gaps
- **Evidence**: Explicit enumeration in the "Complementing Unit Tests" section of
  what unit tests miss and what the Observatory covers.
- **Confidence**: settled
- **Quote**: "Unit tests remain foundational — they are fast and precise, but don't
  cover: Real provider behavior / Long-lived network interactions / Resource
  lifecycle edge cases / Time-dependent regressions"
- **Our assessment**: A well-reasoned claim about the limits of unit testing for LLM
  gateway proxies. The four gaps are specific and grounded in real operational
  experience (the v1.81.3 bug exemplifies all four). This framework — that unit tests
  validate correctness while long-running tests validate *behavior over time* — is a
  useful testing taxonomy for LLM infrastructure.

### Claim 9: The Observatory is used in four distinct scenarios — before deployments, routine validation (daily or weekly), issue investigation, and long-running failure detection
- **Evidence**: Explicitly enumerated use cases under "When They Use It."
- **Confidence**: settled
- **Quote**: "Before Deployments: Tests are run before promoting a new LiteLLM
  version to production / Routine Validation: Regular runs (daily or weekly) catch
  regressions early / Issue Investigation: On-demand tests when a deployment issue
  is suspected / Long-Running Failure Detection: Identifies bugs that only appear
  under sustained load, beyond what short smoke tests can reveal"
- **Our assessment**: The four-scenario framework is a practical categorization of
  when long-running validation adds value. The distinction between "routine
  validation" (scheduled, proactive) and "issue investigation" (reactive, on-demand)
  is particularly useful. We buy this as how LiteLLM uses the system.

### Claim 10: The 3-hour test duration was specifically chosen because bugs like the v1.81.3 incident require sustained runtime to manifest
- **Evidence**: The "Why 3 Hours" callout explicitly connects the test duration
  to the v1.81.3 bug pattern.
- **Confidence**: settled
- **Quote**: "Why 3 Hours: Helps catch issues where HTTP clients degrade or fail
  after extended use (for example, a bug observed in LiteLLM v1.81.3)"
- **Our assessment**: The duration is not arbitrary — it's empirically chosen based
  on a real production bug. The 3-hour window was sufficient for the v1.81.3 failure
  pattern to surface (1-hour TTL + gradual connection degradation). This is a
  concrete reference point for other teams designing their own long-running tests.

## Concrete Artifacts

**Before/after failure metrics for the v1.81.3 HTTP client lifecycle bug (verbatim from source):**

```
Before (with bug):

| Provider | Requests | Success | Failures | Fail % |
|----------|----------|---------|----------|--------|
| OpenAI   | 720,000  | 432,000 | 288,000  | 40%    |
| Azure    | 692,000  | 415,200 | 276,800  | 40%    |

After (fixed):

| Provider | Requests | Success  | Failures | Fail %  |
|----------|----------|----------|----------|---------|
| OpenAI   | 1,200,000| 1,199,988| 12       | 0.001%  |
| Azure    | 1,150,000| 1,149,982| 18       | 0.002%  |
```

Attribution: https://docs.litellm.ai/blog/litellm-observatory, "A Real-World Lifecycle Edge Case" section.

**`TestOAIAzureRelease` test specification (verbatim from source):**

```
- Duration: Runs continuously for 3 hours
- Behavior: Cycles through specified models (such as gpt-4 and gpt-3.5-turbo),
  issuing requests continuously
- Why 3 Hours: Helps catch issues where HTTP clients degrade or fail after
  extended use (for example, a bug observed in LiteLLM v1.81.3)
- Pass / Fail Criteria: The test passes if fewer than 1% of requests fail.
  If the failure rate exceeds 1%, the test fails and the team is notified
  in Slack
- Key Detail: The same HTTP client is reused for the entire run, allowing
  detection of lifecycle-related bugs that only appear under prolonged reuse
```

Attribution: https://docs.litellm.ai/blog/litellm-observatory, "Example: The OpenAI / Azure Reliability Test" section.

**Test flow steps (verbatim from source):**

```
1. Start a Test: A request is sent to the Observatory API with:
   - Which LiteLLM deployment to test (URL and API key)
   - Which test to run (e.g., TestOAIAzureRelease)
   - Test settings (which models to test, how long to run, failure thresholds)

2. Smart Queueing:
   - The system checks whether the exact same test is being attempted more than once
   - If a duplicate test is already running or queued, an error is returned to
     avoid wasting resources
   - Otherwise, the test is added to a queue and runs when capacity is available
     (up to 5 tests concurrently by default)

3. Instant Response: The API responds immediately — the request itself completes
   in milliseconds, even though tests may run for hours.

4. Background Execution:
   - The test runs in the background, issuing requests against the LiteLLM deployment
   - It tracks request success and failure rates over time
   - When the test completes, results are automatically posted to a Slack channel
```

Attribution: https://docs.litellm.ai/blog/litellm-observatory, "How the Observatory Works" section.

**Use cases for the Observatory (verbatim from source):**

```
- Before Deployments: Tests are run before promoting a new LiteLLM version to
  production
- Routine Validation: Regular runs (daily or weekly) catch regressions early
- Issue Investigation: On-demand tests when a deployment issue is suspected
- Long-Running Failure Detection: Identifies bugs that only appear under
  sustained load, beyond what short smoke tests can reveal
```

Attribution: https://docs.litellm.ai/blog/litellm-observatory, "When They Use It" section.

**Error message from the v1.81.3 bug (verbatim from source):**

```
Cannot send a request, as the client has been closed
```

Attribution: https://docs.litellm.ai/blog/litellm-observatory, "A Real-World Lifecycle Edge Case" section.

## Cross-References

- **Corroborates**:
  - `failure-litellm-httpx-cache-eviction.md` — Both sources document the same
    recurring failure class: httpx client lifecycle bugs in LiteLLM where a cached
    client is closed/destroyed while still referenced and actively used by other
    subsystems. The v1.81.3 bug (this note) and the Feb 2026 incident (the failure
    report) are distinct events but share the same underlying mechanism: HTTP client
    shutdown while references remain in use, causing connection errors. Together
    they demonstrate that this is not a one-off bug but a recurring failure class
    for LLM gateway proxies. The metrics are different (this note: 40% failure rate
    on 720k requests; failure report: undisclosed failure rate), confirming separate
    incidents.
  - `blog-litellm-june-townhall-updates.md` **Claim 10** (Guardrail resource leaks
    eliminated by avoiding per-request re-initialization) — shares the broader theme
    of lifecycle/resource management bugs in LiteLLM that only surface under
    sustained runtime, which is exactly what the Observatory is designed to catch.
  - `docs-google-sre-reliable-product-launches.md` **Claim 1** (Google SRE created a
    dedicated Launch Coordination Engineering team for release validation) — both
    sources describe release validation systems with gatekeeping criteria (Google:
    launch checklist pass; LiteLLM: <1% failure rate on a 3-hour test). Different
    implementation, same pattern: automated validation before production promotion.

- **Contradicts**: None. No contradiction issue filed. The v1.81.3 bug described in
  this blog post is an earlier manifestation of the same httpx client lifecycle
  failure class documented in `failure-litellm-httpx-cache-eviction.md`, but the
  two incidents are temporally distinct and both support the same claim (that
  HTTP client lifecycle bugs are a recurring failure class). No existing note
  claims that unit tests are sufficient for catching such bugs, or that the
  Observatory's approach is ineffective.

- **Extends**:
  - `failure-litellm-httpx-cache-eviction.md` — That incident report ends with
    "The lesson extends beyond LiteLLM to any cache that stores both exclusive and
    shared resources." This blog post extends that lesson by describing the testing
    system LiteLLM built as a direct response: the Observatory's same-HTTP-client-
    for-3-hours test pattern is designed to catch the very class of bug documented
    in the failure report. The two notes together form a before/after: failure →
    motivation → testing system.
  - `blog-litellm-april-townhall-updates.md` **Claim 4** (Staging-gated main-branch
    protection with CI/CD testing) — The April townhall describes CI/CD-level
    release validation (staging PRs must pass CircleCI LLM API testing). The
    Observatory adds an additional layer: long-running load tests before deployment.
    Together they show LiteLLm's layered release validation approach (CI tests
    → long-running load tests → production).
  - `docs-google-sre-reliable-product-launches.md` **Claim 5** (The launch checklist
    can drive convergence on common infrastructure) — LiteLLM's Observatory achieves
    a similar convergence goal: a standardized long-running test that every release
    must pass, replacing ad-hoc manual validation. Google's checklist and LiteLLM's
    Observatory are different implementations of the same principle: codify release
    validation in a repeatable, automated process.

- **Novel**: First source note in the corpus covering:
  1. **Long-running release-validation load testing** for an LLM gateway proxy as
     a dedicated system — no existing note describes automated multi-hour load
     testing integrated into a release pipeline for AI infrastructure.
  2. **Smart test queueing with deduplication** — the pattern of rejecting duplicate
     test runs to avoid wasting resources on concurrent identical executions.
  3. **Same-HTTP-client-reuse testing pattern** — the specific technique of reusing
     a single HTTP client across a multi-hour test to surface lifecycle bugs,
     explicitly named as a detection strategy.
  4. **Concrete <1% pass/fail threshold** for long-running LLM gateway validation
     — a specific, measurable reliability bar that current notes lack.
  5. **The v1.81.3 HTTP client lifecycle bug metrics** — 40% → 0.001% failure rate
     reduction with provider-specific request counts (720k OpenAI, 692k Azure) —
     the first dataset in the corpus quantifying the impact of an HTTP client
     lifecycle bug in an LLM gateway.
  6. **Four-scenario use-case taxonomy** for long-running tests (pre-deploy, routine
     validation, issue investigation, long-running failure detection) as a
     practitioner framework.

## Guide Impact

- **Chapter 02 (Production Deployments — Release Validation/Testing)**: Add the
  LiteLLM Observatory pattern as a reference architecture for release-validation
  load testing of LLM gateways. Specific content:
  - The four-scenario use-case taxonomy (pre-deploy, routine, investigative,
    long-running failure detection) as a framework for when to run long tests.
  - The `TestOAIAzureRelease` specification (3-hour duration, <1% threshold, same
    HTTP client across run) as a concrete test design pattern for catching HTTP
    client lifecycle bugs.
  - The smart queueing with deduplication as an operational pattern for teams that
    run long tests in shared CI infrastructure.
  - The "unit tests vs long-running tests" gap analysis (real provider behavior,
    long-lived network interactions, resource lifecycle edge cases, time-dependent
    regressions) as a testing taxonomy for LLM infrastructure.

- **Chapter 03 (Resilience & Reliability Patterns)**: Add the v1.81.3 HTTP client
  lifecycle bug (40% → 0.001% failure rate) as a case study demonstrating that
  lifecycle interactions in cached HTTP clients can cause catastrophic failure in
  LLM gateways, and that such bugs are invisible to short-duration tests. Connect
  to the existing case study in `failure-litellm-httpx-cache-eviction.md` to show
  this is a recurring failure class, not a one-off.

- **Chapter 05 (LLM Ops Reliability)**: Add the Observatory's release-validation
  workflow (smart queueing → instant-response API → background execution →
  Slack notification) as a reference pattern for automated reliability gates in
  an LLM gateway release pipeline. The <1% failure threshold is a specific
  reliability bar that can serve as a starting point for similar systems.

## Extraction Notes

- Source read in full via WebFetch from the published blog post URL. The page is a
  standard Docusaurus blog post, self-contained, no paywall. All quoted passages
  were verified character-for-character from the rendered page text.
- The blog post links to a GitHub repository
  (https://github.com/BerriAI/litellm-observatory) but the URL is mentioned as the
  project location, not as substantive content to extract. No sub-pages were
  followed (the associated GitHub repo would contain configuration/installation
  details that the blog post itself doesn't reference as part of the narrative).
- The v1.81.3 bug metrics are the most significant concrete artifact — the exact
  provider-specific request counts (720k OpenAI, 692k Azure) and the 40% → 0.001%
  reduction provide the strongest evidence for the recurring httpx lifecycle
  failure class documented in `failure-litellm-httpx-cache-eviction.md`.
- `confidence_overall` set to `settled`: the system architecture is described by
  the team that built it; the bug metrics are published as specific, verifiable
  numbers; the test specification is factual. This contrasts with LiteLLM townhall
  updates (rated `emerging`) which are more forward-looking and aspirational. The
  Observatory post describes a completed, operational system with measurable
  results.
- No contradiction issue filed: verified against all existing source notes. The
  v1.81.3 bug in this post and the Feb 2026 incident in
  `failure-litellm-httpx-cache-eviction.md` are distinct events with the same
  failure class — not a contradiction. All adjacent notes (LiteLLM townhalls,
  Google SRE launch practices) corroborate or extend rather than oppose.
