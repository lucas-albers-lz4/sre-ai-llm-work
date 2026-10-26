---
source_url: https://docs.litellm.ai/docs/load_test_rpm
source_type: docs
title: "Multi-Instance TPM/RPM (litellm.Router) — LiteLLM AI Gateway Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page metadata last_updated 2026-10-24)
date_extracted: 2026-10-26
last_checked: 2026-10-26
status: current
confidence_overall: emerging
issue: "#1886"
---

# Multi-Instance TPM/RPM (litellm.Router)

> A vendor tutorial for testing whether per-deployment RPM limits stay global
> across two Router/proxy instances. Its real contribution is the deployment
> shape — per-deployment `rpm`, shared Redis, `enable_pre_call_checks`,
> `num_retries=0` — plus a cautionary example of a rate-limit test whose fake
> backend has the same limit as the gateway, so the observed 200 successes
> cannot be attributed to the gateway at all.

## Source Context

- **Type**: docs (official LiteLLM AI Gateway documentation, living Docusaurus
  page). Rendered page metadata reports `last_updated: 2026-10-24`; there is
  no byline or separate publication date.
- **Author credibility**: LiteLLM (BerriAI) first-party vendor documentation.
  Authoritative for *what LiteLLM says its configuration flags mean and what
  test shape it recommends*. Not authoritative as evidence that the test
  produces the claimed outcome: the page publishes no measured output, no
  assertion, and no run log.
- **Scope**: Covers two variants of one load test — (1) two `litellm.Router`
  objects in a single Python process, each pointed at the same two fake
  deployments and the same Redis; (2) two locally started proxy processes on
  ports 4000 and 4001 with the equivalent `router_settings`. Both variants
  offer 600 requests per iteration against a nominal 200 RPM aggregate budget
  (2 deployments × 100 RPM) and expect roughly 200 successes. Also includes a
  fake OpenAI server built with FastAPI + `slowapi` that is itself limited to
  `100/minute`. Does **not** cover: how Redis keys/counters are scoped,
  what happens without Redis, how TPM (as opposed to RPM) is exercised,
  provider-side quota behavior, multi-region deployments, or any measured
  result from the run. The linked `/docs/routing` page was followed for
  background on the same flags (see Extraction Notes), but all `Quote` fields
  below are from `load_test_rpm` itself.

## Extracted Claims

### Claim 1: The page's purpose is to check that configured TPM/RPM limits are respected across multiple Router instances, not just inside one process
- **Evidence**: The title and opening sentence state the cross-instance scope
  directly; the proxy section repeats the same objective for multiple proxy
  instances.
- **Confidence**: settled (explicit statement of intent)
- **Quote**: "Test if your defined tpm/rpm limits are respected across multiple instances of the Router object."
- **Our assessment**: This is the question worth asking. A per-process
  in-memory limiter would let each instance spend the full budget, so N
  instances multiply the effective cap. But the page only states the intent;
  it never shows a result or explains how to tell cross-instance enforcement
  apart from a coincidental success count (see Claims 9-11).

### Claim 2: The test is designed as a 3:1 overload — 100 RPM per deployment, 200 RPM aggregate over two deployments, and 600 requested per interval, with only ~200 expected to succeed
- **Evidence**: The three bullet points defining the test, repeated for the
  Router and proxy variants; the proxy section adds the explicit success
  expectation.
- **Confidence**: settled for the stated design; emerging for the actual
  behavior (no run output is published)
- **Quote**: "Max RPM per deployment is = 100 requests per minute" / "Max Throughput / min on router = 200 requests per minute (2 deployments)" / "Load we'll send through router = 600 requests per minute"
- **Our assessment**: The limit is attached to each *deployment*
  (`rpm: 100` under `litellm_params`), and the two deployments share one
  `model_name` alias. So the budget is a property of the deployment pool, not
  of a Router process. That is the right mental model for a gateway, but the
  page calls the sum "Max Throughput / min", conflating a configured limit
  with a measured throughput ceiling. It also never says how close to 200 is
  acceptable, so "respected" remains an eyeball judgment.

### Claim 3: Cross-instance enforcement is configured through shared Redis — both Router objects and the proxy config receive the same Redis host, port, and password
- **Evidence**: Both `Router(...)` constructors pass `redis_host`,
  `redis_port`, and `redis_password` from environment variables; the proxy
  YAML sets the same three under `router_settings`, with an inline warning.
- **Confidence**: emerging (the page presents Redis as required configuration
  but does not explain the counter mechanism or the failure mode without it)
- **Quote**: "redis_host: os.environ/REDIS_HOST ## IMPORTANT! Setup the proxy w/ redis"
- **Our assessment**: This is the mechanism the tutorial is really about:
  shared state is what makes two processes enforce one budget. The linked
  `/docs/routing` page is more explicit, describing Redis as the production
  usage tracker for TPM/RPM across deployments (async `redis.incr` /
  `redis.mget`). But `load_test_rpm` itself never states what happens if Redis
  is absent or partitioned, whether counters are per-key/team/deployment, or
  how counter reset windows are aligned. Those are exactly the questions an
  operator needs answered before trusting the pattern.

### Claim 4: Both variants enable `enable_pre_call_checks`, presented as part of the rate-limit test configuration
- **Evidence**: The direct-Router constructors pass
  `enable_pre_call_checks=True`; the proxy YAML sets
  `enable_pre_call_checks: true` under `router_settings`.
- **Confidence**: emerging (the flag is shown but not defined on this page)
- **Quote**: "enable_pre_call_checks: true"
- **Our assessment**: The name and the linked routing page's inline comment
  identify this as the switch that enables router rate limits for concurrent
  calls. The tutorial omits that explanation, its default, and whether the
  test fails if it is off. The guide should not present the flag as optional
  without documenting its default.

### Claim 5: Both variants set `num_retries` to zero, removing retries from the measurement
- **Evidence**: Both `Router(...)` constructors pass `num_retries=0`; the
  proxy YAML sets `num_retries: 0` under `router_settings`.
- **Confidence**: settled for the artifact; emerging for the rationale (the
  page does not state why)
- **Quote**: "num_retries: 0"
- **Our assessment**: This is a deliberate and necessary control. With
  retries enabled, a 429 could be retried and eventually succeed, inflating
  the success count and hiding whether the limit was enforced at the intended
  boundary. The page should say so; a reader who copies the config without
  understanding the line is likely to re-enable retries and misread the
  result.

### Claim 6: `simple-shuffle` is recommended for the test, with "best performance" as the only justification
- **Evidence**: The proxy YAML line carries the recommendation as an inline
  comment; the direct-Router constructors also choose
  `routing_strategy="simple-shuffle"`.
- **Confidence**: anecdotal (single-line vendor recommendation; no benchmark
  or comparison on this page)
- **Quote**: "routing_strategy: simple-shuffle # recommended for best performance"
- **Our assessment**: The linked routing page adds the missing context —
  `simple-shuffle` is the default and usage-based routing adds Redis latency.
  That makes the recommendation plausible, but it is a throughput preference,
  not a correctness requirement for a rate-limit test. The tutorial tests only
  one strategy; it does not show whether usage-based routing changes the
  success count or concentrates rejections on one deployment.

### Claim 7: The harness does not actually send 600 requests per minute — it fires 600 concurrent tasks, sleeps 10 seconds, and repeats 10 times, so the real offered rate depends on how long each batch takes
- **Evidence**: `loadtest_fn` creates 600 tasks per call; `parent_fn` calls it
  10 times with `asyncio.sleep(10)` between calls. There is no per-minute
  pacing inside `loadtest_fn`.
- **Confidence**: settled (the code is the artifact)
- **Quote**: "n = 600  # Number of concurrent tasks" / "await loadtest_fn()" / "await asyncio.sleep(10)"
- **Our assessment**: The prose says "Load we'll send through router = 600
  requests per minute", but the loop offers 600 requests per ~10 seconds plus
  completion time. If the mock answers quickly, the offered load is several
  thousand RPM, not 600; only if each batch takes roughly 50 seconds does the
  arithmetic land near 600 RPM. A test meant to demonstrate a 3:1 overload
  ratio should either pace requests uniformly or report the actual start/end
  timestamps and computed offered rate. This is a documentation/harness
  inconsistency, not a claim conflict with another source.

### Claim 8: The harness's success metric is "returned a response without raising" — every exception is collapsed to `None`, so a gateway 429, a backend 429, a timeout, and a connection error are indistinguishable
- **Evidence**: The completion helper catches `Exception` and returns `None`;
  the batch result keeps only non-`None` responses and prints their count.
- **Confidence**: settled (verbatim code)
- **Quote**: "successful_completions = [c for c in chat_completions if c is not None]"
- **Our assessment**: This is the most important methodological weakness. The
  test asks whether limits are respected, but the only observable is a count
  of non-exceptions. A result of ~200 is consistent with the gateway enforcing
  its budget, with the backend enforcing its own limit, or with a mix of both.
  To attribute rejections, the harness must record status codes and error
  bodies (or at least count HTTP 429 separately) rather than a boolean.

### Claim 9: The fake OpenAI server is itself limited to 100 requests per minute per deployment, which makes the expected ~200 successes attributable to the fake backends even if the gateway's RPM enforcement fails
- **Evidence**: The fake server applies `@limiter.limit("100/minute")` to the
  completion route and returns HTTP 429 with `{"detail": "Rate Limited!"}`.
  The two deployments point at two server ports, each carrying that limit.
- **Confidence**: emerging (inference from the published code; the page never
  runs the counterfactual)
- **Quote**: `@limiter.limit("100/minute")` / `content={"detail": "Rate Limited!"}`
- **Our assessment**: This is a confounded test design. If LiteLLM fails to
  enforce `rpm: 100`, it forwards the excess and each fake server independently
  admits only 100/minute, so the aggregate success count still lands near 200.
  The page even says "Let's setup a fake openai server with a RPM limit of
  100", i.e. the mock duplicates the exact budget under test. A valid
  gateway-limit test should make the backend's limit non-binding (remove it or
  set it far above the gateway cap) and then assert the gateway-produced 429s.
  This is high-value for the guide's testing methodology: don't let the test
  double enforce the thing you are trying to measure.

### Claim 10: Despite the title, the page never exercises TPM — every configuration sets only `rpm`, and the request payload is a short UUID message
- **Evidence**: Both the Router `model_list` and proxy `model_list` include
  `rpm: 100` and no `tpm` key; the request body is
  `{"role": "user", "content": f"This is a test: {uuid.uuid4()}"}`.
- **Confidence**: settled (absence in the published config and payload)
- **Quote**: "Test if your defined tpm/rpm limits are respected across multiple instances of the Router object."
- **Our assessment**: The title promises TPM/RPM coverage, but TPM enforcement
  is not tested at all. Short UUID prompts are nowhere near any plausible token
  budget, so even if a `tpm` limit were added, the test would not stress it.
  A real TPM test needs a `tpm` limit plus long prompts and token-accounting
  assertions. The corpus already documents token-based batch accounting
  (`docs-litellm-batches-api`); this page does not cover the real-time TPM
  analogue.

### Claim 11: The test has no pass/fail assertion — it prints `(request count, elapsed seconds, success count)` for a human to interpret
- **Evidence**: `loadtest_fn` ends with a `print(...)` and returns nothing;
  `parent_fn` discards the return value. There is no expected-count check,
  tolerance, or non-zero exit on failure.
- **Confidence**: settled (verbatim code)
- **Quote**: "print(n, time.time() - start, len(successful_completions))"
- **Our assessment**: Calling this a test overstates it; it is a demo harness.
  It cannot be wired into CI, and a regression that changes the success count
  from 200 to 400 or 0 produces no signal. Contrast the guide's existing
  "a gate that cannot fail is not a gate" rule: this harness is the same
  pattern at the load-test layer. Add an explicit expected-success range and
  fail outside it, then log the status-code distribution alongside it.

### Claim 12: The proxy is documented as reusing the Router's enforcement path, so the same test is claimed to work for either surface
- **Evidence**: The proxy section's framing sentence explicitly says the proxy
  uses the router underneath.
- **Confidence**: settled (vendor architectural statement)
- **Quote**: "so if you're using either of them, this test should work for you."
- **Our assessment**: This is useful because it means the proxy YAML's
  `router_settings` is not a parallel implementation — it is the same knobs
  surfaced through config. It also means a Router-level bug/behavior should
  reproduce on the proxy. The page does not verify that equivalence; the two
  variants are presented as alternatives rather than cross-checked against each
  other.

## Concrete Artifacts

### Proxy configuration under test (verbatim from the page)
```yaml
model_list:
- litellm_params:
    api_base: http://0.0.0.0:8080
    api_key: my-fake-key
    model: openai/my-fake-model
    rpm: 100
  model_name: fake-openai-endpoint
- litellm_params:
    api_base: http://0.0.0.0:8081
    api_key: my-fake-key
    model: openai/my-fake-model-2
    rpm: 100
  model_name: fake-openai-endpoint
router_settings:
  num_retries: 0
  enable_pre_call_checks: true
  redis_host: os.environ/REDIS_HOST ## IMPORTANT! Setup the proxy w/ redis
  redis_password: os.environ/REDIS_PASSWORD
  redis_port: os.environ/REDIS_PORT
  routing_strategy: simple-shuffle # recommended for best performance
```
Attribution: https://docs.litellm.ai/docs/load_test_rpm, "1. Setup config".

### Direct-Router construction (verbatim from the page)
```python
router_1 = Router(model_list=model_list, num_retries=0, enable_pre_call_checks=True, routing_strategy="simple-shuffle", redis_host=os.getenv("REDIS_HOST"), redis_port=os.getenv("REDIS_PORT"), redis_password=os.getenv("REDIS_PASSWORD"))
router_2 = Router(model_list=model_list, num_retries=0, routing_strategy="simple-shuffle", enable_pre_call_checks=True, redis_host=os.getenv("REDIS_HOST"), redis_port=os.getenv("REDIS_PORT"), redis_password=os.getenv("REDIS_PASSWORD"))
```
Attribution: https://docs.litellm.ai/docs/load_test_rpm, "Code".

### Load loop and success counting (verbatim, direct-Router variant)
```python
async def loadtest_fn():
    start = time.time()
    n = 600  # Number of concurrent tasks
    tasks = [router_completion_non_streaming() for _ in range(n)]
    chat_completions = await asyncio.gather(*tasks)
    successful_completions = [c for c in chat_completions if c is not None]
    print(n, time.time() - start, len(successful_completions))
```
```python
async def parent_fn():
  for _ in range(10):
    dt = get_utc_datetime()
    current_minute = dt.strftime("%H-%M")
    print(f"triggered new batch - {current_minute}")
    await loadtest_fn()
    await asyncio.sleep(10)
```
Attribution: https://docs.litellm.ai/docs/load_test_rpm, "Code". The proxy variant
uses the same loop against two `AsyncOpenAI` clients instead of two Routers.

### Exception collapsing (verbatim, direct-Router variant)
```python
async def router_completion_non_streaming():
  try:
    client: Router = random.sample([router_1, router_2], 1)[0] # randomly pick b/w clients
    # print(f"client={client}")
    response = await client.acompletion(
              model="fake-openai-endpoint", # [CHANGE THIS] (if you call it something else on your proxy)
              messages=[{"role": "user", "content": f"This is a test: {uuid.uuid4()}"}],
          )
    return response
  except Exception as e:
    # print(e)
    return None
```
Attribution: https://docs.litellm.ai/docs/load_test_rpm, "Code".

### Fake backend's rate limit (verbatim excerpt)
```python
@app.post("/chat/completions")
@app.post("/v1/chat/completions")
@limiter.limit("100/minute")
async def completion(request: Request):
    # raise HTTPException(status_code=429, detail="Rate Limited!")
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        ...
    }
```
```python
@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429,
                        content={"detail": "Rate Limited!"})
```
Attribution: https://docs.litellm.ai/docs/load_test_rpm, "Extra - Setup Fake
OpenAI Server". The `...` inside the JSON response is elision of the fixed
sample completion body, not source text.

## Cross-References

- **Corroborates**: `docs-litellm-load-test-advanced`, Claim 3 — rate-limit
  capacity tests are expected to show failures, and an operator must
  distinguish quota rejections from gateway breakage. This page adds the
  missing multi-instance/RPM case: here the expected rejections are intended
  to be gateway-enforced (though Claim 9 shows the fake backend can produce
  them too). Its Claim 4 also supplies the concrete expected-count style that
  this page lacks.
- **Corroborates**: `docs-litellm-completion-input-params`, Claim 2 — the real
  retry knob in these code paths is `num_retries` (the docs elsewhere say
  `max_retries`). Both Router constructors and the proxy `router_settings` here
  use `num_retries`, which is consistent with that note's naming finding.
- **Extends**: `docs-litellm-batches-api`, Claim 3 and Claim 4 — that note
  documents the per-minute TPM/RPM window and the separate batch input-file
  limiter that bypasses it. This page supplies a real-time RPM example of the
  same per-minute budget, plus the shared-Redis/multi-instance dimension the
  batch note does not cover. No contradiction: batch and real-time traffic are
  explicitly different limiters.
- **Extends**: `docs-litellm-benchmarks`, Claim 4 and Claim 14 — Claim 4's rule
  is that gateway-side success metrics are blind to client-visible failures.
  This page is a client-side harness, so it can see failures, but it discards
  their type (Claim 8) and therefore cannot attribute them. Claim 14 notes the
  benchmark environment omitted Redis; this page is the multi-instance
  Redis-backed case that benchmark did not measure. The two are complementary,
  not contradictory.
- **Contradicts**: none filed. The apparent tensions are conditioning
  variables, not real contradictions: (a) `docs-litellm-benchmarks` Claim 14
  says "no Redis used" for a single-instance benchmark, while this page
  requires Redis for multi-instance limits; (b) `docs-litellm-batches-api`
  Claim 3 says batch submissions bypass per-minute TPM/RPM windows, while this
  page exercises real-time per-minute RPM. Neither pair leads to opposing guide
  advice on the same configuration.
- **Novel**: the concrete multi-instance deployment shape (two instances, two
  deployments sharing one alias, per-deployment `rpm`, shared Redis,
  `enable_pre_call_checks`, `num_retries=0`); the `simple-shuffle` performance
  recommendation; and the test-validity trap in Claim 9 (fake backend
  duplicates the gateway's limit, making the success count unable to attribute
  enforcement to the gateway).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — "Cost, capacity, and fallback
  patterns")**: add a rule that a per-deployment RPM/TPM budget is only a
  *global* budget when every Router/proxy instance shares the same Redis
  counters and has pre-call checks enabled. Without shared state, N instances
  each enforce the full budget, so the effective cap is N × the configured
  value. Cite this note's Claims 2-4, not the page's unverified "~200 succeed"
  expectation.
- **Chapter 02 (Observability — "Break error rates down by provider and
  operation" / "SLI measurement design")**: add the client-side attribution
  rule this page violates: a load test that counts only "non-exception
  responses" cannot distinguish gateway rate limiting from backend rate
  limiting, timeouts, or connection errors. Require status-code / error-body
  counts, and cite Claims 8-9 as the worked failure case.
- **Chapter 05 (Evaluation and measurement methodology — "A gate that cannot
  fail is not a gate")**: extend the existing rule with the load-test case:
  a harness that `print`s a success count and never asserts an expected range
  provides no regression signal. Cite Claim 11 and pair it with
  `docs-litellm-benchmarks` Claim 4 on vantage-point metrics.
- **Chapter 05 (capacity testing)**: do not import the page's "600 requests
  per minute" label without recomputing offered load from the loop. The code
  fires 600 concurrent tasks every ~10 seconds plus completion time, so the
  actual offered rate is not the stated 600 RPM (Claim 7).

## Extraction Notes

- The rendered HTML flattens code blocks (the Python snippets appear as one
  line). I extracted the verbatim code from the page's markdown alternate,
  `https://docs.litellm.ai/docs/load_test_rpm.md`, which reports
  `last_updated: "2026-10-24"` and matches the rendered page's content. All
  `Quote` fields are copied from that markdown text.
- Followed one linked page, `/docs/routing` (the page links it as "router"),
  to interpret `enable_pre_call_checks`, Redis usage tracking, and the
  `simple-shuffle` recommendation. Those linked-page details are paraphrased
  only in `Our assessment`; no quote in this note is sourced from the linked
  page, so every `Quote` remains checkable against `load_test_rpm`.
- The page publishes no run output, latency numbers, or observed success
  count, so confidence is `emerging` overall. The "expected 200" is a design
  statement, not a measurement.
- The "600 per minute" prose vs 600-concurrent-per-10s code is recorded as a
  harness/documentation inconsistency in Claim 7, not filed as a contradiction
  issue: it is an internal tutorial defect about offered-load accounting, not
  two opposing positions on how operators should run gateways.
- Candidate disposition (from `miner-related-notes.md`):
  - `docs-litellm-batches-api.md` — cited (Extends; real-time RPM vs batch
    limiter).
  - `docs-litellm-completion-web-search.md` — dismissed: web-search request
    surface, no rate-limit or multi-instance content.
  - `docs-litellm-evals-api.md` — dismissed: evaluations CRUD, unrelated.
  - `docs-litellm-generate-content.md` — dismissed: Google-native passthrough,
    unrelated.
  - `docs-litellm-bedrock-invoke.md` — dismissed: Bedrock Invoke passthrough,
    unrelated.
  - `docs-litellm-enterprise.md` — dismissed: its rate-limit mention is a
    governance feature list (Claim 6); no multi-instance enforcement or Redis
    detail.
  - `docs-litellm-files-endpoints.md` — dismissed: file API routing, unrelated.
  - `docs-litellm-audio-transcription.md` — dismissed: audio endpoint and
    fallback config, unrelated.
  - `docs-litellm-benchmarks.md` — cited (Extends; client-visible metrics and
    Redis omission).
  - `docs-litellm-completion-input-params.md` — cited (Corroborates;
    `num_retries` naming).
- The page is thin relative to most docs sources (a tutorial, not a reference),
  but it is not a duplicate of `docs-litellm-load-test-advanced` or
  `docs-litellm-benchmarks`: neither of those covers multi-instance shared
  Redis enforcement, and neither contains this page's fake-backend confound.
