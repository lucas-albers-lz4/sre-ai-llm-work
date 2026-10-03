---
source_url: https://docs.litellm.ai/docs/completion/mock_requests
source_type: docs
title: "Mock Completion() Responses - Save Testing Costs 💰 — LiteLLM Documentation (with sibling pages Mock Completion Responses tutorial and Reliability - Retries, Fallbacks)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page front-matter last_updated 2026-10-02)
date_extracted: 2026-10-03
last_checked: 2026-10-03
status: current
confidence_overall: emerging
issue: "#1523"
---

# Mock Completion() Responses — Save Testing Costs 💰 (LiteLLM Docs)

> LiteLLM documents a one-parameter, SDK-level stub for LLM calls:
> `completion(..., mock_response="...")` returns a synthesized OpenAI-shaped
> completion without contacting any provider. This note's contribution to the
> guide is not that the parameter exists — it is the **shape of the synthesized
> response** (`model: "MockResponse"`, `usage.prompt_tokens` /
> `completion_tokens` / `total_tokens` all `null`, a 2023-era `created`
> timestamp, no `id`, no `object`) and therefore what a green mocked suite can
> and cannot attest to. The headline finding: the mock is a *spend* tool with a
> *coverage* blind spot, positioned inside the SDK **before** the gateway, so it
> exercises none of the routing, auth, retry, fallback, rate-limit, guardrail,
> latency, or spend-accounting code that an LLM-touching SRE system exists to
> keep working — and it silently returns `null` where an accounting assertion
> would need a number. No contradiction with any existing note; the page makes
> no claim about any of those paths.

## Source Context

- **Type**: docs (official LiteLLM / BerriAI vendor documentation — a living
  Docusaurus page, no byline, no publish date). The triage classified this as a
  thin page and was right: the primary page is **~35 words of prose, four code
  blocks, one JSON sample, and front matter**.
- **Author credibility**: First-party product documentation. Authoritative for
  the *surface* (parameter name, call shape, and the documented response object,
  which is the only published contract for what the stub returns). **Not**
  authoritative for *behavior*: there is no measured result, no failure
  writeup, no version note, no changelog entry, and no statement anywhere on
  the page about what the stub bypasses. The page's own framing is cost
  avoidance, not coverage.
- **Scope — primary page** (`/docs/completion/mock_requests`, front matter
  `last_updated: "2026-10-02"`): four sections — `## quick start`,
  `## streaming`, `## (Non-streaming) Mock Response Object`, and `## Building a
  pytest function using completion with mock_response` — plus a two-entry
  `related:` list. Does **not** cover: error/failure injection, how to make a
  mocked call return a 4xx/5xx, tool calls or function calling under
  `mock_response`, `logprobs`, structured-output/JSON-mode under
  `mock_response`, embedding or non-`/chat/completions` endpoints under
  `mock_response`, guardrails, or any interaction with a `litellm.Router`,
  proxy, or budget.
- **Scope — followed page 1** (`/docs/tutorials/mock_completion`, read per
  MINER.md §1; linked from the docs sidebar and carrying the same title minus
  the emoji, front matter `last_updated: "2026-10-02"`): a near-duplicate of
  the primary page with one material difference — its copy of the pytest
  example **prints `finish_reason` instead of asserting on content** (Claim 7).
  Also the source of the page's spend framing sentence (Claim 9).
- **Scope — followed page 2** (`/docs/completion/reliable_completions`, read per
  MINER.md §1; it is the primary page's `related:` entry and its "Next" nav
  link): the sibling retry/fallback page. Read to establish what a **real**
  call's response carries (`id`, `object`, populated `usage`,
  `x-litellm-attempted-fallbacks`) and what a real failure path looks like
  (`num_retries`/tenacity, the `[model] + fallbacks` attempt list,
  `All fallback attempts failed`) — i.e. to state the mock's negative space
  against the vendor's own documentation of the machinery the mock skips.
- **Not mined** (out of MINER.md §1 budget, and each is a separate source with
  its own `source_url`): `/docs/guides/reliability_testing_spend` (the section
  hub), `/docs/completion/json_mode`, `/docs/completion/stream`,
  `/docs/proxy/reliability`. Each belongs in its own note; none is quoted from
  here.

## Extracted Claims

### Claim 1: `mock_response` is a parameter on the SDK's `completion()` call itself, and the documented guarantee is that it returns a response object "without calling the LLM APIs" — so the stub sits *below* every gateway and provider mechanism
- **Evidence**: The page's entire prose is two sentences (quoted below),
  followed by four examples that all pass `mock_response` as a keyword argument
  to `litellm.completion`. Nothing on the page invokes a proxy, a
  `litellm.Router`, or a config file; there is no server-side counterpart to
  this parameter anywhere in the page.
- **Confidence**: settled (explicit vendor statement plus four consistent
  call shapes). The *consequence* — that gateway behavior is therefore
  unreachable — is an inference from the placement of the parameter, flagged as
  such in Our assessment.
- **Quote**: "For testing purposes, you can use `completion()` with `mock_response` to mock calling the completion endpoint." / "This will return a response object with a default response (works for streaming as well), without calling the LLM APIs."
- **Our assessment**: The placement is the whole story, and it is the part the
  page never draws. `mock_response` is an argument to the *client library*, so
  the request never leaves the process: no proxy hop, no virtual key, no model
  registry lookup, no deployment selection, no `success_callback`, no spend
  row, no Prometheus scrape. Compare the corpus's other two test knobs
  (Claim 10): `network_mock: true` keeps the entire gateway in the request path
  and removes only the provider, while `mock_testing_fallbacks` is a Router-level
  flag that the Proxy now strips. So this is the **cheapest and the most
  destructive** of the three, and an operator who reaches for it by name
  ("mock the LLM call") is unlikely to realize they have also mocked away the
  gateway they are usually trying to test. That inference is reasoned from the
  documented return path, not stated by the vendor — see Claim 9 and OQ-1.

### Claim 2: The documented non-streaming mock response carries `"model": "MockResponse"` and a `usage` object whose three token fields are **all `null`** — the single most consequential detail on the page for anything that asserts on cost or tokens
- **Evidence**: The `(Non-streaming) Mock Response Object` section, a complete
  JSON object reproduced verbatim in Concrete Artifacts below. `usage` is
  present as an object (not omitted) with `prompt_tokens`, `completion_tokens`,
  and `total_tokens` each `null`. `message.logprobs` is `null` as well. The
  sibling reliability page's real-response sample carries the same `usage` keys
  with integers (`16` / `46` / `62`).
- **Confidence**: settled for the documented object shape (it is a complete
  published sample, not an excerpt). The downstream consequences are this
  note's reading.
- **Quote**: `"usage": { "prompt_tokens": null, "completion_tokens": null, "total_tokens": null }` and `"model": "MockResponse",` (both from the page's own JSON block, whitespace normalized; see Concrete Artifacts for the byte-exact object)
- **Our assessment**: This is why the page is worth a note despite being thin.
  The null-usage object is the **worst** of the three possible shapes for a
  test: it is not absent (so `response.get("usage")` truthiness checks pass
  and a consumer that guards on presence alone proceeds) and it is not zero (so
  a naive reducer that sums or multiplies it does not produce a plausible
  number either — it produces `None` propagation or a `TypeError`). A spend
  assertion written against `response["usage"]["total_tokens"]` fails loudly;
  a spend *accounting pipeline* written against it can pass a unit test, ship,
  and then silently record nothing in production. This is the LiteLLM-side
  instance of a pattern the corpus already has from promptfoo: a cost gate
  whose value source has nothing in it is not a gate
  (`docs-promptfoo-deterministic-metrics.md` **Claim 6** — "an unknown cost
  cannot be checked"). Two further consumers are blocked by the same object:
  `logprobs: null` rules out perplexity-style scoring (cf.
  `docs-promptfoo-deterministic-metrics.md` **Claim 14** on `logprobs`
  availability), and `"model": "MockResponse"` means any code that echoes or
  branches on the response `model` — which Ch05 treats as the primary
  substitution-detection signal — takes a branch no real provider can produce.
  Recommend the guide state the rule directly: **never let a cost, budget, or
  token assertion be satisfied by a mocked call; assert on a fixture instead.**

### Claim 3: The documented mock object omits `id` and `object`, both of which the vendor's own real-response example on the sibling page carries — so identity- and envelope-shape assertions are not portable between a mocked and a real call
- **Evidence**: Side-by-side comparison of the two published response samples.
  The mock object has exactly four top-level keys: `choices`, `created`,
  `model`, `usage`. The real-response sample on
  `/docs/completion/reliable_completions` has six: `id`, `object`, `created`,
  `model`, `choices`, `usage` — with `"id": "chatcmpl-7qTmVRuO3m3gIBg4aTmAumV1TmQhB"`
  and `"object": "chat.completion"`.
- **Confidence**: settled as a *documentation* observation (both objects are
  published in full, verbatim, on two pages by the same vendor, both
  `last_updated: 2026-10-02`). Whether the **implementation** adds `id` and
  `object` to mocked responses is not documented either way — recorded as OQ-2,
  not asserted.
- **Quote** (from `/docs/completion/reliable_completions`, "Output from calls"):
  `"id": "chatcmpl-7qTmVRuO3m3gIBg4aTmAumV1TmQhB",` / `"object": "chat.completion",`
- **Our assessment**: Note the *direction* of this failure, because it is the
  opposite of the null-usage hazard and it matters for how a team reacts to a
  red test. A test asserting `response["id"]` or `response["object"]` on a
  mocked call fails **loudly** — a `KeyError`, immediately, in CI. That is the
  benign direction: it is a false red that a developer will investigate. The
  dangerous directions are the ones that stay green (Claims 2, 4, 9). The
  practical guidance that falls out: prefer assertions that fail under a stub
  over assertions a stub silently satisfies, and when a mocked test fails on a
  missing envelope field, resist the urge to add `.get(...)` defaults — that
  conversion turns a loud false red into a quiet false green. The same applies
  to any code under test that branches on `object` or parses `id`.

### Claim 4: The mock sample's `created` value is `1694459929.4496052` — an epoch timestamp that resolves to **2023-09-11T19:18:49Z**, i.e. the page's own example response is ~3 years stale relative to its `last_updated` date, and no page states whether the field is live or frozen
- **Evidence**: The literal value in the page's JSON block, plus this Miner's
  own conversion of it (flagged as arithmetic, not a vendor statement). The
  same 2023-era value appears in the sibling page's real-response sample
  (`"created": 1692741891`, i.e. 2023-08-22), which suggests both samples were
  captured when the docs were first written and refreshed mechanically
  thereafter — an inference, not a documented fact.
- **Confidence**: settled for the literal value and its date. **Low** for any
  claim about runtime behavior: a plausible implementation stamps
  `time.time()`, in which case `created` *is* live and this is a
  documentation-staleness artifact only. Recorded as OQ-3. Do not treat the
  2023 date as an operational finding without an independent test.
- **Quote**: `"created": 1694459929.4496052,` (from the page's JSON block)
- **Our assessment**: The reason this is worth stating rather than skipping is
  that it is *checkable in one line* and it is the kind of field that quietly
  appears in application code: cache-age and freshness logic, "is this
  response stale?" assertions, timestamp-ordering checks, replay-window
  filters, and any dedup keyed on `(model, created)`. If the field is frozen,
  every one of those tests is testing a 2023 constant and will pass forever
  while proving nothing; if it is live, none of this applies. The
  cost-asymmetric move is to **not assert on `created` in a mocked test at
  all** and to pin the value in a fixture if the logic under test genuinely
  needs a timestamp — that is correct under either implementation, which is why
  it is the guidance rather than a finding about LiteLLM.

### Claim 5: The mock also works with `stream=True` and is delivered as `delta` fragments rather than one shot — the page's inline output comment shows a chunk whose `content` is the three-character fragment `'Thi'` with `finish_reason: None`
- **Evidence**: The `## streaming` section's code block and its trailing
  comment, reproduced byte-exact in Concrete Artifacts. The comment shows one
  chunk of a multi-chunk iteration: `print(chunk)` followed by accumulation of
  `chunk["choices"][0]["delta"]["content"]` into `complete_response`.
- **Confidence**: settled for the fragment *shape* (`delta`-keyed content
  chunks, `finish_reason: None` mid-stream). **Not** settled: how many chunks,
  where the boundaries fall, whether a terminal `finish_reason: "stop"` chunk
  is emitted, and whether a final usage chunk is ever sent (Claims 6 and 8).
- **Quote**: "# {'choices': [{'delta': {'role': 'assistant', 'content': 'Thi'}, 'finish_reason': None}]}"
- **Our assessment**: Real value here, and it is the one capability the page
  offers that has no substitute in the corpus: a **deterministic streaming
  completion with no provider**, which is what a streaming-handler unit test
  actually needs. The corollary is a constraint rather than a gap: because
  chunk boundaries are undocumented (Claim 6), a stream test must assert on the
  *reassembled* text, never on a chunk index, a chunk count, or a specific
  fragment. This is also where the mock's null usage meets the corpus's
  streaming-accounting hazard: a consumer that aggregates `usage` per chunk
  gets nothing at all from a mocked stream, and a consumer that indexes
  `chunk["choices"][0]` unconditionally will break on a terminal usage chunk if
  one is ever emitted — the exact failure
  `docs-litellm-streaming-token-usage.md` **Claim 2** documents for real
  streams ("all other chunks will also include a usage field, but with a null
  value"). Write the consumer to branch on `usage is not None` / non-empty
  `choices`, per that note.

### Claim 6: The streaming example is internally inconsistent — the `mock_response` string it passes is `"It's simple to use and easy to get started"`, but the fragment it documents is `'Thi'`, the first three characters of `"This is a mock request"`, which is also the sample object's `content` — so the documented chunk output appears carried over from an older default-response rendering of the page
- **Evidence**: Three artifacts compared within the same page: the
  `mock_response` value in the streaming example, the inline output comment on
  the following line, and the `content` value in the `(Non-streaming) Mock
  Response Object` sample. The prose supports the "default response" reading:
  "This will return a response object with a **default** response."
- **Confidence**: settled as a *documentation* inconsistency (all three
  strings are on the page, verbatim, and mutually inconsistent). The mechanism
  is inferred, not documented — flagged in Our assessment, and OQ-4.
- **Quote**: `response = completion(model=model, messages=messages, stream=True, mock_response="It's simple to use and easy to get started")` / `# {'choices': [{'delta': {'role': 'assistant', 'content': 'Thi'}, 'finish_reason': None}]}` / `"content": "This is a mock request",`
- **Our assessment**: The most useful thing on the page, precisely because it
  is a documentation defect rather than a product one. If the streamed chunks
  were derived from the passed `mock_response`, the first fragment would begin
  `"It"`, not `"Thi"`. So either (a) the mock streams a *fixed default*
  response regardless of `mock_response` and the parameter is honored only on
  the non-streaming path — which the pytest assertion in Claim 7 would then be
  the only evidence against — or (b) the inline comment is simply stale copy
  from a previous revision of the page. The corpus cannot distinguish these
  from documentation. This is exactly the kind of page where an SRE writing a
  stream test should spend five minutes in a REPL before trusting either
  behavior, and where the guide should say: **do not encode the vendor's
  example output as a fixture.**

### Claim 7: Non-streaming `mock_response` sets `choices[0].message.content` to the passed string **exactly** — established by the only executable assertion the vendor ships — and the near-duplicate tutorial page carries the same example with the assertion replaced by a `print`
- **Evidence**: The primary page's pytest block ends
  `assert(response['choices'][0]['message']['content'] == "LiteLLM is awesome")`;
  the tutorial page's block with the same function name (`test_completion_openai`),
  the same prompt, and the same `mock_response` value instead ends
  `print(response['choices'][0]['finish_reason'])`. Both retain the inline
  comment `# Add any assertions here to check the response`. Both pages carry
  front-matter `last_updated: "2026-10-02"`.
- **Confidence**: settled (two verbatim code blocks compared field by field).
- **Quote**: `assert(response['choices'][0]['message']['content'] == "LiteLLM is awesome")` (primary page) / `print(response['choices'][0]['finish_reason'])` (tutorial page)
- **Our assessment**: The assertion is the highest-value line on either page —
  it is the vendor's own statement of the non-streaming contract, and it is what
  resolves the ambiguity in Claim 6 for the non-streaming path. The tutorial
  divergence is worth recording as a small but real documentation-hygiene
  signal: the same example, under the same title, on two simultaneously
  `last_updated` pages, differs exactly in the one line that makes it a test.
  The tutorial's copy is a *smoke check* dressed as a test — it exercises the
  call, prints the envelope, and asserts nothing. A team copy-pasting from the
  tutorial gets a green test that verifies only that `mock_response` did not
  raise. Note also that both versions wrap the whole body in
  `try: … except Exception as e: pytest.fail(...)`, which is Claim 10's subject:
  the documented failure pattern is "any exception fails the test," with no way
  to distinguish an expected error path from a defect.

### Claim 8: The page's streaming example is not runnable as written — `complete_response` is read and appended to inside the loop but never initialized, so the documented example raises `NameError` on its first iteration
- **Evidence**: The `## streaming` code block verbatim (Concrete Artifacts
  below). The loop body is `print(chunk)`, a comment, then
  `complete_response += chunk["choices"][0]["delta"]["content"]`. No assignment
  to `complete_response` appears anywhere in the block, and the page's
  prose offers nothing else.
- **Confidence**: settled (verified against the byte-exact code block; the only
  streaming example on the page).
- **Quote**: `for chunk in response: ` / `    print(chunk) # {'choices': [{'delta': {'role': 'assistant', 'content': 'Thi'}, 'finish_reason': None}]}` / `    complete_response += chunk["choices"][0]["delta"]["content"]`
- **Our assessment**: Small, but it is the kind of detail that tells a reader
  how much the page has been exercised. The one streaming example the vendor
  publishes has never been run. Read together with Claim 6 (the inline output
  is stale relative to the input string) and Claim 5 (chunk boundaries
  undocumented), the conclusion for the guide is consistent and specific: **the
  streaming mock path is documented well enough to use, and not well enough to
  copy.** Use the parameter; write your own consumer; verify the reassembled
  text once in a REPL and pin that as a fixture. Do not transcribe the page's
  example, and do not treat its documented fragment as an expected value.

### Claim 9: The vendor's framing of `mock_response` is **cost, not coverage** — title, front-matter summary, and tutorial prose are all about avoiding spend, and the page never once states what the stub bypasses
- **Evidence**: Page title "Mock Completion() Responses - **Save Testing Costs 💰**";
  front-matter `summary` is the one-sentence cost-free description; the only
  prose is "without calling the LLM APIs"; the tutorial's version of the
  sentence ends by naming the benefit explicitly. A full read of both pages
  finds no "coverage", "bypass", "limitation", "caveat", or "does not test"
  statement, and no negative-space section of any kind.
- **Confidence**: settled for the framing (title and quotes are the page's
  own). The coverage gap itself is **this note's inference** from the documented
  return path (Claim 1) and from the machinery the sibling reliability page
  documents as bypassed — it is **not** the vendor's claim, and the page
  contains no measured false-confidence rate. Per the triage's explicit
  instruction, this claim is graded low-confidence inference and is **not**
  inflated into a contradiction.
- **Quote** (from `/docs/tutorials/mock_completion`): "Trying to test making LLM Completion calls without calling the LLM APIs ? Pass `mock_response` to `litellm.completion` and litellm will directly return the response without neededing the call the LLM API and spend $$" (the doubled "neededing" and the trailing "$$" are the source's own)
- **Our assessment**: The negative space, stated once so the guide can state it
  once. A mocked `completion()` cannot validate: **routing** (model aliases,
  deployment selection, `auto_router` tiers), **auth** (virtual keys, per-team
  spend limits), **retry** (`num_retries`/tenacity), **fallbacks** (the
  `[model] + fallbacks` attempt list, `context_window_fallback_dict`, and the
  `x-litellm-attempted-fallbacks` header the sibling page documents), **rate
  limits / 429**, **timeouts** (the documented default client timeout is 600
  seconds — `docs-litellm-completion-input-params.md` **Claim 5** — and a
  mocked call returns instantly, so no timeout path is touched), **spend and
  budget accounting** (usage is `null`; per-key budget windows and
  budget-driven fallback chains live in the gateway —
  `blog-litellm-save-claude-code-costs.md` **Claims 1–2**;
  `docs-litellm-a2a-iteration-budgets.md` **Claims 4–5**), **guardrails**, and
  **latency** (a stub has no latency, so any latency SLO or percentile assertion
  built on it is decorative by construction). The guide's rule should be
  one sentence: **`mock_response` replaces the provider call and nothing else;
  a green mocked suite is evidence about your parsing and branching, and is
  silent evidence about your gateway.** The corresponding corollary, from the
  corpus: the vendor's own documented remedy for the one path where a synthetic
  knob was removed is to **induce a real provider error in a non-production
  environment** (`docs-litellm-audio-transcription.md` **Claim 2**) — which is
  also the only documented way to cover the paths this page skips.

### Claim 10: The corpus now covers three test-only mocking knobs at three different layers, and this is the first note to place all three side by side — with the operational consequence that **no documented knob synthetically exercises gateway fallback logic**
- **Evidence**: The three mechanisms, each verified against its source:
  `mock_response` (this page) is an SDK `completion()` parameter that returns
  before the gateway; `mock_testing_fallbacks` is stripped from incoming Proxy
  requests as of v1.85.0 and survives only on direct `litellm.Router` calls; and
  `network_mock: true` is a proxy `litellm_settings` key that intercepts
  outbound requests at the httpx transport layer inside the gateway and returns
  canned responses. The two pre-existing rows are quoted verbatim from existing
  notes (both re-read this session per MINER.md §4b).
- **Confidence**: settled for each row's layer (two from verbatim quotes in
  existing notes, one from this page's own prose and examples).
- **Quote** (from `source-notes/docs-litellm-audio-transcription.md` **Claim 1**):
  "Starting in LiteLLM Proxy v1.85.0, `mock_testing_fallbacks` is stripped from incoming Proxy requests and has no effect. It remains supported only for direct `litellm.Router` calls in tests." / (from `source-notes/docs-litellm-benchmarks.md` **Claim 11**) "The fastest way to benchmark proxy overhead is using network_mock mode. This intercepts outbound requests at the httpx transport layer and returns canned responses, no need for setting up a mock provider."
- **Our assessment**: Only `network_mock` keeps the gateway's own logic in the
  test path — routing, auth, logging, and budget enforcement all still run; it
  is the right knob for "is my proxy healthy", and the benchmarks note already
  ships the runnable harness. `mock_response` is the right knob for "is my
  response parser and branching correct", and the wrong knob for anything the
  gateway does. `mock_testing_fallbacks` is now a Router-only test flag with no
  proxy path at all. So the layer table the triage asked for is not just
  taxonomy — it identifies a genuine hole: **fallback behavior has no synthetic
  test surface.** The corpus's evidence that this is a real operational
  constraint rather than a documentation quibble is
  `docs-litellm-audio-transcription.md` **Claim 2** (vendor-documented
  replacement is an induced real provider error in a non-production
  environment) and `docs-litellm-benchmarks.md` **Claim 4** (a gateway-side
  success metric cannot see failures that never reach the gateway — a mocked
  call is the extreme case, never reaching anything). Teams should treat
  "fallback logic is covered" as a staging-environment claim with an induced
  failure, and say so in the test's name or comment, because nothing in the
  request path will tell them otherwise.

### Claim 11: The page's only failure-handling construct is `except Exception as e: pytest.fail(f"Error occurred: {e}")` — there is no documented way to make a mocked `completion()` return an error, so the page offers no mechanism for testing LLM error paths at all
- **Evidence**: Complete absence, checked against the byte-exact full text of
  both pages. Neither page shows a mocked call returning a 4xx/5xx, raising a
  typed LiteLLM exception, returning malformed JSON, returning a tool call,
  returning a content-filter block, or returning an empty/`refusal` message.
  The only error handling in either page is the `try`/`except` wrapper around
  the two pytest examples.
- **Confidence**: settled (that the documentation is silent). This claim is
  about the documentation, not the implementation.
- **Quote**: `except Exception as e:` / `        pytest.fail(f"Error occurred: {e}")`
- **Our assessment**: The concrete consequence is that the most valuable tests
  for an LLM-touching SRE system — the ones that assert a 429 is retried, a
  fallback model is selected, a guardrail blocks, a malformed body surfaces as
  an alert, a budget overrun is refused — have **no documented stub path on this
  page at all**. The documented pattern actively works against writing them: a
  blanket `except Exception` that calls `pytest.fail` means an assertion about
  an *expected* error is indistinguishable from a crash, so the natural first
  instinct (wrap the call, assert on the outcome) produces a test that cannot
  express "this should have raised". Combined with `docs-litellm-a2a-iteration-budgets.md`
  **Claim 5** — an over-cap response is HTTP 429 with
  `"type": "budget_exceeded"`, a *cost* cap surfacing as the same status class
  as ordinary rate limiting — the guide's practical recipe is: inject failures
  at the layer you actually want to test (an HTTP fault-injecting proxy in
  front of a real LiteLLM, or a stub of *your own* client wrapper rather than
  of `litellm.completion`), and reserve `mock_response` for the
  parse-and-branch layer.

## Concrete Artifacts

All four code blocks and the JSON object below are byte-exact from
`https://docs.litellm.ai/docs/completion/mock_requests.md` (the page's own raw
markdown endpoint, which preserves exact line breaks, indentation, and trailing
whitespace; the *rendered* HTML fetch collapses newlines inside code blocks and
would have made these quotes inexact).

The `## quick start` block, verbatim:

```python
from litellm import completion 

model = "gpt-5.6-luna"
messages = [{"role":"user", "content":"This is a test request"}]

completion(model=model, messages=messages, mock_response="It's simple to use and easy to get started")
```

The `## streaming` block, verbatim — note the uninitialized `complete_response`
on the last line (Claim 8) and the `mock_response` value that does not match the
`content` in the inline output comment (Claim 6):

```python
from litellm import completion 
model = "gpt-5.6-luna"
messages = [{"role": "user", "content": "Hey, I'm a mock request"}]
response = completion(model=model, messages=messages, stream=True, mock_response="It's simple to use and easy to get started")
for chunk in response: 
    print(chunk) # {'choices': [{'delta': {'role': 'assistant', 'content': 'Thi'}, 'finish_reason': None}]}
    complete_response += chunk["choices"][0]["delta"]["content"]
```

The `(Non-streaming) Mock Response Object`, verbatim — the null-usage contract
(Claim 2), the `MockResponse` model name, the 2023-era `created` (Claim 4), and
the absence of `id` / `object` (Claim 3):

```json
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "This is a mock request",
        "role": "assistant",
        "logprobs": null
      }
    }
  ],
  "created": 1694459929.4496052,
  "model": "MockResponse",
  "usage": {
    "prompt_tokens": null,
    "completion_tokens": null,
    "total_tokens": null
  }
}
```

The `## Building a pytest function …` block, verbatim — the only executable
assertion on either page (Claim 7) and the blanket `except` (Claim 11):

```python
from litellm import completion
import pytest

def test_completion_openai():
    try:
        response = completion(
            model="gpt-5.6-luna",
            messages=[{"role":"user", "content":"Why is LiteLLM amazing?"}],
            mock_response="LiteLLM is awesome"
        )
        # Add any assertions here to check the response
        print(response)
        assert(response['choices'][0]['message']['content'] == "LiteLLM is awesome")
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
```

Full front matter of the primary page, verbatim — the `related:` list is the
route to the sibling reliability page mined below:

```yaml
title: "Mock Completion() Responses - Save Testing Costs"
url: "/docs/completion/mock_requests"
canonical_url: "https://docs.litellm.ai/docs/completion/mock_requests"
type: "docs"
last_updated: "2026-10-02"
summary: "For testing purposes, you can use completion() with mock_response to mock calling the completion endpoint."
related:
  - "/docs/guides/reliability_testing_spend"
  - "/docs/completion/reliable_completions"
```

From the followed tutorial page `https://docs.litellm.ai/docs/tutorials/mock_completion.md`
— the same pytest example with the assertion replaced by a print (Claim 7), and
the page's spend-framing prose (Claim 9), verbatim:

```python
        # Add any assertions here to check the response
        print(response)
        print(response['choices'][0]['finish_reason'])
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
```

```markdown
Trying to test making LLM Completion calls without calling the LLM APIs ? 
Pass `mock_response` to `litellm.completion` and litellm will directly return the response without neededing the call the LLM API and spend $$ 
```

```yaml
title: "Mock Completion Responses - Save Testing Costs"
url: "/docs/tutorials/mock_completion"
canonical_url: "https://docs.litellm.ai/docs/tutorials/mock_completion"
type: "docs"
last_updated: "2026-10-02"
summary: "Trying to test making LLM Completion calls without calling the LLM APIs ?"
related:
  - "/docs/tutorials/text_completion"
  - "/docs/tutorials/python_sdk"
```

From the followed sibling page `https://docs.litellm.ai/docs/completion/reliable_completions.md`
— a **real** call's output, for the envelope contrast in Claim 3 (note populated
`usage`, present `id` and `object`):

```
Completion with 'bad-model': got exception Unable to map your input to a model. Check your input - {'model': 'bad-model'

completion call gpt-5.6-luna
{
  "id": "chatcmpl-7qTmVRuO3m3gIBg4aTmAumV1TmQhB",
  "object": "chat.completion",
  "created": 1692741891,
  "model": "gpt-5.6-luna",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I apologize, but as an AI, I do not have the capability to provide real-time weather updates. However, you can easily check the current weather in San Francisco by using a search engine or checking a weather website or app."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 16,
    "completion_tokens": 46,
    "total_tokens": 62
  }
}
```

Also from that sibling page — the fallback attempt-list semantics and the
attempt-count header that a mocked call can never produce (Claim 9, Claim 10).
Quoted verbatim, two contiguous fragments:

```markdown
When you pass `fallbacks` to `completion`, LiteLLM builds the attempt list `[model] + fallbacks` and calls each entry once, in order. The first response that comes back is returned; a failing entry is logged and the next one is tried. There is no time budget, no repeated loop over the list and no cooldown: once every entry has failed, `completion` raises an exception carrying the last error, suffixed with `All fallback attempts failed`.
```

```markdown
The successful response carries the `x-litellm-attempted-fallbacks` header with the number of fallbacks that were attempted before it.
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path cited or
dismissed; the retrieval was lexical and returned generic LiteLLM
parameter-surface matches — only 2 of 10 candidates are genuinely adjacent to
this page, and the notes that matter most — `docs-litellm-streaming-token-usage.md`
and `docs-promptfoo-deterministic-metrics.md` — were absent from the list and
found by searching `source-notes/` directly):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch JSONL
  submission accounting (`batch_enqueued_token_limit`, per-record TPM
  reservations). Shares only the vocabulary of token accounting, and is the
  corpus's counterexample: there, LiteLLM *computes* token counts before
  forwarding; here, the documented mock returns `null`.
- `source-notes/docs-litellm-audio-transcription.md` — **cited** (Extends,
  and one row of the Claim 10 layer table): **Claim 1** for
  `mock_testing_fallbacks` being stripped at Proxy v1.85.0 and **Claim 2** for
  the vendor's documented replacement — induce a real provider error in a
  non-production environment. Both are load-bearing for Claim 10.
- `source-notes/docs-litellm-completion-input-params.md` — **cited** (Extends;
  the negative space): **Claim 4** documents the `fallbacks` /
  `context_window_fallback_dict` machinery a mocked call skips, and **Claim 5**
  documents the 600-second default client timeout a mocked call returns
  instantly beneath.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock native
  Invoke passthrough routing and bearer-token auth swap. Unrelated.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited** (cited as a
  contrast rather than corroboration, following the precedent in
  `docs-litellm-completion-message-trimming.md`): **Claim 4**'s
  accumulate-after / check-before ordering and **Claim 5**'s
  `"type": "budget_exceeded"` 429 are the *enforcing, observable* budget
  posture; the mock is the unobservable extreme of the same axis, since
  `usage: null` means nothing accumulates and nothing can ever be refused.
- `source-notes/docs-litellm-benchmarks.md` — **cited** (Extends; the third row
  of the Claim 10 layer table): **Claim 11** (`network_mock` at the httpx
  transport layer, verbatim re-read) and **Claim 4** (a gateway-side success
  metric cannot see failures that never reach the gateway — the general form of
  this note's blind spot).
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: routing
  strategy selection and debuggability. Routing is in this note's *negative*
  space (a mocked call never routes), so the note is adjacent by subject and
  contributes no shared claim.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **cited** (Extends, as a
  three-position contrast on where a cost figure comes from): **Claim 3** makes
  the flat per-query cost "a gateway-declared synthetic charge" with no linkage
  to measured token usage. The mock's `usage: null` is the third and worst
  position: not declared-synthetic, not measured — simply absent.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  telemetry integration paths (headers, `success_callback`). No shared claim;
  both subjects are telemetry, but the mechanisms and the failure modes are
  unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: the
  general toil-reduction principles. Its **Claim 2** (runbook content is
  "essentially pseudocode to someone with software development skills") is the
  closest thing in the corpus to a motivation for stubbing LLM calls in CI, but
  it makes no claim about stubs, tests, or providers, so citing it would be
  thematic rather than evidential. Noted for the Smith: Ch04 has no
  LLM-stubbing material and this page does not change that.

**Additional cross-references found by searching `source-notes/` and `guide/`:**

- `source-notes/docs-litellm-streaming-token-usage.md` — **cited**
  (Corroborates, Extends): **Claim 1** (streamed usage is opt-in via
  `stream_options={"include_usage": True}`, so a stream is usage-blind by
  default) and **Claim 2** (the usage chunk arrives before `data: [DONE]` with
  an empty `choices` array while "all other chunks will also include a usage
  field, but with a null value"). This is the corpus's existing precedent for
  *legitimate* null usage on the streaming path, and it is the right contrast
  for Claim 5: there, `usage: null` is documented and expected per-chunk; on
  the mock, all three token fields are null in the **final, only** response, so
  there is no chunk anywhere that carries a count.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — **cited**
  (Corroborates, and the corpus's prior art for this note's Guide Impact):
  **Claim 6** ("This requires the provider to return cost information; an
  unknown cost cannot be checked") is the same no-gate failure mode on a
  different product — a cost assertion whose value source is empty passes
  without gating. **Claim 14** (`latency` requires `--no-cache` to be measuring
  the target call at all) is the same class of error for latency, which a mocked
  call makes structurally impossible rather than merely misconfigured.
  **Claim 12** (trace/trajectory assertions throw when trace data is
  unavailable rather than passing) is the corpus's one *fail-closed* precedent —
  the behavior this page's mock lacks.
- `source-notes/docs-litellm-token-usage-helpers.md` — **cited**
  (Corroborates, Extends): **Claim 4** — `completion_cost` "combines
  token_counter and cost_per_token", re-tokenizing locally rather than reading
  provider-reported usage. That is the corpus's *recovery path* for Claim 2's
  hazard: a local estimator can still price a mocked call, so a test that needs
  a cost figure should compute it from `token_counter`/`cost_per_token` over
  known inputs rather than reading `usage` off the response. (That note's
  assessment also warns the local path silently yields a wrong or zero figure
  when the cost map lacks an entry — a hazard a mocked model name like
  `"MockResponse"` makes worse.)
- `source-notes/blog-litellm-save-claude-code-costs.md` — **cited** (Extends,
  negative space): **Claim 1** (stacked budget windows cap virtual-key spend
  within rolling periods) and **Claim 2** (a budget-driven fallback chain
  silently routes to a cheaper model when a per-model budget is exhausted). Both
  are gateway-enforced spend behaviors that a mocked call cannot reach and
  cannot alert on — the concrete Ch05 "Cost, capacity, and fallback patterns"
  content this note argues must not be covered by mocked tests.
- `source-notes/docs-litellm-completion-http-handler-config.md` — **cited by
  section name** (not by claim number, per MINER.md §4b: the material is in its
  Cross-References section, not a numbered claim): its "Extends / thematically
  adjacent" block cites `docs-litellm-benchmarks.md` **Claim 11** as establishing
  the *inbound* transport layer while that note covers the *outbound*
  connection pool. Useful here because it shows the corpus already reasons about
  mocking in terms of **which layer intercepts** — the same axis the Claim 10
  table extends with the SDK-level row.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-audio-transcription.md` **Claim 1** — the
    precedent this note extends: a test-only knob that a version gate turned
    into a no-op with no error, warning, or metric. `mock_response` is not
    version-gated away, but both share the corpus's recurring detectability
    failure — a test path that silently exercises nothing.
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 6** — "an
    unknown cost cannot be checked." The promptfoo cost gate is a no-gate when
    the provider reports no cost; the LiteLLM mock is a no-gate when the value
    source is the stub. Two products, one rule for Ch05.
  - `source-notes/docs-litellm-streaming-token-usage.md` **Claim 2** — null
    `usage` on non-terminal chunks, and the note's finding that the page's own
    SDK example would `IndexError` on the final usage chunk. Corroborates that
    LiteLLM's stream consumers need explicit `usage is not None` / non-empty
    `choices` guards, which a mock stream consumer needs even more.
  - `source-notes/docs-litellm-benchmarks.md` **Claim 4** — a gateway-side
    success metric cannot see failures that never reach the gateway. This note's
    blind spot is the same shape taken one layer further out: a mocked call
    never reaches anything, so neither the gateway nor the provider can observe
    it.
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claim 4** — the local
    cost path exists and is the documented way to get a number without a
    provider, which is what makes Claim 2's guidance actionable rather than
    merely cautionary.

- **Contradicts**:
  - **None. No contradiction issue filed**, per MINER.md §4a. Checked
    `CONTRADICTIONS.md` (no entries; "No open contradictions at MVP bootstrap")
    and the reasoning against the §4a "when NOT to file" criteria: (a) the
    mock's contract does not oppose any existing note's claim — the candidates
    that share vocabulary (`docs-litellm-batches-api.md` token accounting,
    `docs-litellm-audio-transcription.md` fallback testing) are complementary,
    not opposed; (b) the intra-page inconsistencies this note found (Claims 6
    and 8) are **defects in a vendor page about a testing helper**, not
    disagreements between two positions on the same operational question — the
    page takes no position on routing, fallback, retry, or coverage at all, so
    there is nothing for it to contradict; and (c) the coverage-gap claim
    (Claim 9) is an *absence* of a claim, which cannot be in conflict with
    another source's claim. Per the triage's explicit instruction ("do not
    inflate it into a new contradiction"), this was a deliberate outcome.

- **Extends**:
  - `source-notes/docs-litellm-audio-transcription.md` (#1401) — the primary
    sibling, and the note that made the layer distinction necessary. Extends it
    on three axes: (1) **layer** — that note's **Claim 1** establishes a
    Router-level flag with no proxy path; this note adds the SDK-level knob
    that never reaches the gateway at all, completing a three-layer picture
    (Claim 10). (2) **Remedy** — that note's **Claim 2** documents the vendor's
    substitute for lost synthetic fallback testing (induce a real provider
    error in a non-production environment); this note argues the same substitute
    is the *only* documented coverage path for everything `mock_response`
    skips, which upgrades a transcription-endpoint footnote into a general
    Ch05 rule. (3) **Detectability** — that note records "green tests that
    exercise nothing" for one flag; this note records the same outcome for the
    corpus's most-used mocking knob, plus the sharper version: green tests
    whose *accounting* reads `null`.
  - `source-notes/docs-litellm-benchmarks.md` (#1430) — **Claim 11** is the
    harness this note's Claim 10 recommends for gateway-level tests, and this
    corpus now has both sides of the layer pair documented with runnable
    configs. Extends it with the SDK-level knob and with the observation that
    `network_mock` is the only one of the three that preserves gateway logic in
    the request path — so the benchmarks page's harness, not `mock_response`,
    is the right starting point for any test that claims to cover the gateway.
  - `source-notes/docs-litellm-completion-input-params.md` — **Claim 4** and
    **Claim 5** supply the concrete list of what a mocked call skips
    (`fallbacks`, `context_window_fallback_dict`, and the 600-second default
    client timeout). This note is the negative-space companion to that
    parameter reference: that note says what each knob does, this one says a
    stubbed call does none of it.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Claims 4–5** as
    the enforcing/observable budget posture, and
    `blog-litellm-save-claude-code-costs.md` **Claims 1–2** as the gateway-side
    spend posture. Together with `docs-litellm-a2a-cost-tracking.md`
    **Claim 3** (declared-synthetic cost), the corpus now has four distinct
    positions on "where does a cost figure come from" — declared-synthetic,
    gateway-enforced-and-refused, provider-reconciled, and **null** — and this
    note adds the last, with the operational rule that a cost *assertion* over
    a null-usage response is not a gate.

- **Novel**: First corpus coverage of LiteLLM's **`mock_response` parameter**
  and of the **`MockResponse` synthetic model name** (grep-verified this
  session across `source-notes/` and `guide/`: zero prior matches for
  `mock_response` or `MockResponse`). Specifically new: the documented
  non-streaming mock envelope including the all-`null` `usage` triple and
  `logprobs: null`; the absence of `id` / `object` measured against the
  vendor's own real-response sample; the 2023-era `created` value in the sample;
  the delta-fragment streaming form with the `'Thi'` fragment; the
  `mock_response`-value / documented-fragment mismatch (Claim 6); the
  uninitialized `complete_response` in the vendor's only streaming example
  (Claim 8); the near-duplicate tutorial page whose copy of the pytest example
  prints instead of asserting (Claim 7); and the first three-layer table of the
  corpus's test-only knobs (`mock_response` / `mock_testing_fallbacks` /
  `network_mock`), including the finding that **fallback logic has no synthetic
  test surface** (Claim 10). Also, per the triage's own note: this is the
  corpus's **first note on stubbing or testing LLM-touching code at all**.

## Guide Impact

Verified before writing: `grep -niE "mock|pytest|stub"` over `guide/*.md`
returns **zero** matches — the guide documents no mocking or stubbing mechanism
of any kind. (`fixture` and `unit test` do appear, but only as committed
*eval-data* fixtures in Ch05 ~L234/626/653 and a CI/CD stage-isolation sentence
in Ch06 ~L709; neither stubs an LLM call.) The only hits for "deterministic"
are Ch03's static-vs-agentic algorithm rule and Ch05's promptfoo citations.
Nothing in `guide/` recommends `mock_response`, and no chapter discusses what a
mocked LLM call does or does not prove. So this is net-new chapter material, and
the triage's Ch02 and Ch06 suggestions are partially warranted (Ch02 for the
telemetry consequence, Ch06 for guardrails), with Ch05 as the primary home.

- **Chapter 05 (llm-ops-reliability) — add a "what a mocked LLM call does not
  test" subsection**, placed next to the existing `### Test in the environment
  you ship` rule. That rule currently says to gate on the built artifact "not a
  local dev environment that diverges from the runtime"; this note extends the
  same logic one level further, since a `mock_response` call diverges from the
  runtime not in environment but in *whether a provider call happens at all*.
  Lead with the one-sentence rule (Claim 9): **`mock_response` replaces the
  provider call and nothing else; a green mocked suite is evidence about your
  parsing and branching, and is silent evidence about your gateway.** Then the
  enumerated skip-list: routing, auth, retry, fallback, rate limits, timeouts,
  spend/budget accounting, guardrails, latency.
- **Chapter 05 — extend the existing `### A gate that cannot fail is not a
  gate` table with a new row class: the stubbed value source.** That table
  currently lists six *config* properties that make a gate incapable of failing,
  and its rule is "'Can this gate fail?' is a grep of the config." This note
  supplies the complementary case, where the config is fine and the *data* is
  synthetic: a cost or token assertion over a response with `usage: null`
  (Claim 2), a latency gate over a call that has no latency, a `logprobs`
  consumer over `logprobs: null`. Cite
  `docs-promptfoo-deterministic-metrics.md` **Claim 6** alongside it — the same
  no-gate failure mode from the other direction ("an unknown cost cannot be
  checked"). Suggested rule wording: *every gate names the source of every value
  it reads, and a gate that reads a stubbed or absent value is a gate.*
- **Chapter 05 — add the layer table** (`mock_response` / `mock_testing_fallbacks`
  / `network_mock`, Claim 10), because no existing chapter or note collects all
  three. Two payload conclusions for the guide: use `network_mock` when the
  claim under test is about the gateway (it is the only one of the three that
  keeps routing, auth, logging, and budgets in the request path, and the
  benchmarks note already ships the runnable harness), and state plainly that
  **fallback behavior has no synthetic test surface** — the vendor's own
  documented substitute is an induced real provider error in a non-production
  environment (`docs-litellm-audio-transcription.md` **Claim 2**), so teams
  should label such tests as staging-environment tests.
- **Chapter 05 (`## Cost, capacity, and fallback patterns`) — add the null-usage
  warning to the spend-accounting content.** Concretely: a mocked call returns
  `prompt_tokens` / `completion_tokens` / `total_tokens` as `null` and `model` as
  `"MockResponse"`, so any budget or chargeback code exercised against a stub
  sees no numbers and can pass its tests while recording nothing in production.
  Cross-reference `docs-litellm-a2a-cost-tracking.md` **Claim 3** (declared-
  synthetic charge), `blog-litellm-save-claude-code-costs.md` **Claims 1–2**
  (gateway-enforced budget windows and budget-driven silent fallback), and
  `docs-litellm-a2a-iteration-budgets.md` **Claims 4–5** (`"type":
  "budget_exceeded"` 429) so the chapter has all four cost-figure positions,
  ending with the recovery path from `docs-litellm-token-usage-helpers.md`
  **Claim 4**: compute a test's cost locally via `token_counter` /
  `cost_per_token` rather than reading `usage` off the response.
- **Chapter 05 (`### Test in the environment you ship`) — add the
  false-green caution about *stubbing the layer under test*.** Ch05 already
  warns about environment divergence; this note adds the sharper failure of
  mocking away the component whose behavior the test claims to cover, and the
  corollary for error paths (Claim 11): the page offers no way to make a mocked
  `completion()` return an error, and its shipped example wraps everything in
  `except Exception: pytest.fail(...)`, which cannot express "this should have
  raised." Recommend injecting failures at the layer actually under test.
- **Chapter 02 (observability) — add one line to the token/cost-telemetry
  content.** A mocked response carries `"model": "MockResponse"` and `usage`
  fields of `null`, so any trace, span attribute, or dashboard derived from a
  mocked call is populated with a synthetic model name and missing token counts.
  Relevant because Ch02 treats the response `model` as the substitution-detection
  signal, and `"MockResponse"` is a value no provider can produce — worth naming
  so it is not mistaken for a misconfiguration or a rogue model alias.
- **Chapter 06 (security-and-trust) — one caveat line, not a section.** The
  triage suggested Ch06 on the grounds that tests that bypass guardrails give a
  false green. That is true but is already implied by the Ch05 skip-list
  (guardrails are gateway-enforced and a mocked call never reaches them), and
  this source adds no guardrail content of its own. Recommend Ch06 point at the
  Ch05 subsection rather than restating it.
- **No `guide/` edit is proposed by this note.** Per repo rules this is Smith
  work; the impact above is advisory input only.

## Extraction Notes

- **Followed pages, disclosed.** The primary page is thin — verified against
  its byte-exact raw markdown: front matter, two sentences of prose, four code
  blocks, one JSON object, a two-entry `related:` list, and a two-entry footer.
  MINER.md §1 directs following substantive linked pages, and this page's
  front-matter `related:` points at `/docs/completion/reliable_completions`,
  which is also its "Next" nav link and is the vendor's own documentation of
  the retry/fallback machinery a mocked call skips. That page was read in full
  and supplies Claims 3, 9, and 10 plus the real-response artifact.
  `/docs/tutorials/mock_completion` — same title minus the emoji, same
  `last_updated`, reachable from the docs sidebar — was read in full because it
  is a near-duplicate whose divergence (Claim 7) is itself evidence. **Every
  quote and artifact from both is attributed inline** to its own URL;
  `source_url` in the front matter remains the primary page (the issue's
  source).
- **Verbatim sourcing method.** All three pages were read from their raw
  markdown endpoints (`…/mock_requests.md`, `…/tutorials/mock_completion.md`,
  `…/reliable_completions.md`). This was deliberate: the *rendered* HTML fetch
  collapses newlines inside code blocks, which would have made every code-block
  quote inexact — and code blocks are most of this page's content. All fenced
  blocks in Concrete Artifacts are byte-exact from those endpoints, including
  trailing whitespace after `from litellm import completion`, the unterminated
  `"$$ "` prose line, and the doubled "neededing" typo on the tutorial page.
- **Claims about the documentation vs the implementation.** Following the
  precedent set by `docs-litellm-completion-message-trimming.md` (#1510), this
  note separates the two explicitly. Claims 1, 2, 5, 6, 7, 8, 9, 10, and 11 are
  statements about what the vendor publishes and what follows from the
  documented return path. Claims 3, 4, and 6 involve runtime behavior that the
  documentation does not settle; those are flagged in-confidence and recorded
  as open questions rather than asserted as product defects. Nothing here claims
  LiteLLM's mock is broken — the specific, checkable statements are that the
  *documented* envelope omits `id`/`object` and carries null usage, and that
  the page's two streaming artifacts are inconsistent with each other.
- **No contradiction filed.** See the Contradicts block above: no opposition to
  any existing note's claim, and the intra-page findings are documentation
  defects rather than competing positions. Deliberate, per the triage.
- **Candidate-list handling.** All 10 paths in `miner-related-notes.md` were
  cited or explicitly dismissed above, per MINER.md §4. Two are load-bearing
  (`docs-litellm-audio-transcription.md`, `docs-litellm-benchmarks.md`), one is
  cited for negative space (`docs-litellm-completion-input-params.md`), and
  three more were found by searching `source-notes/` directly — most notably
  `docs-litellm-streaming-token-usage.md` and
  `docs-promptfoo-deterministic-metrics.md`, which the lexical retrieval missed
  entirely and which carry the two closest prior-art findings in the corpus.
  Every cited claim number was verified by re-reading the cited note this
  session (MINER.md §4b), and every quotation attributed to another note was
  copied from that note rather than reconstructed.
- **Open questions this source cannot answer** (recorded rather than guessed):
  - **OQ-1** — does `mock_response` short-circuit *before* or *after* client-side
    pre-call hooks (`success_callback`s, logging, budget tracking, pre-call
    hooks)? Nothing on the page says, and the answer determines whether a
    mocked call is truly invisible to telemetry or merely un-billed. Needs a
    read of the implementation or a black-box test.
  - **OQ-2** — does the mocked response object include `id` and `object` at
    runtime (Claim 3)? Testable in one line: `completion(..., mock_response="x").keys()`.
  - **OQ-3** — is `created` stamped live (`time.time()`) or frozen (Claim 4)?
    Same one-line test. Both OQ-2 and OQ-3 resolve with a single REPL session;
    they are recorded rather than answered because this note's evidence must
    come from the source, not from an unreported local experiment.
  - **OQ-4** — for `stream=True`, are the delta fragments derived from the
    `mock_response` string or from a fixed default (Claim 6)? And are chunk
    boundaries stable across runs and across string lengths? This is the
    highest-value open question on the page: it determines whether a streaming
    test can assert anything stronger than "the reassembled text equals the
    input."
  - **OQ-5** — is there any documented way to make a mocked call return an
    error status, a refusal, a malformed body, or a tool call (Claim 11)? No
    knob is documented on either page; the repository or release notes would
    have to be searched, which is outside this source.
- **Pages deliberately not mined.** `/docs/guides/reliability_testing_spend` (the
  section hub — an index page, no claims of its own),
  `/docs/completion/json_mode`, `/docs/completion/stream`, and
  `/docs/proxy/reliability` were read only as far as needed to confirm the
  section structure and nav. Each is a separate source with its own
  `source_url`. `/docs/proxy/reliability` in particular is the proxy-side
  counterpart to the reliability page mined here and is likely to be the
  highest-value next issue for the fallback-testability question this note
  raises.
- **Confidence rationale for `emerging`.** The documented surfaces are
  `settled` at the individual-claim level and are first-party vendor
  documentation: the parameter name, the call shapes, the published response
  object, and the delta-fragment form are all checkable by a second reader
  against the same URL. The note is `emerging` overall because: the headline
  finding (the coverage gap) is an **inference** from the documented return
  path and not a vendor statement, exactly as the triage required; the two
  sharpest technical observations (the fragment/value mismatch in Claim 6 and
  the frozen `created` in Claim 4) are unresolvable from documentation; the
  page ships **no metrics, no failure writeup, and no measured
  false-confidence rate**, so nothing here supports a quantitative claim about
  how often mocked suites mislead; and Claims 3, 4, and 6 concern a
  documentation sample whose fidelity to current implementation behavior is
  itself unverified. Consistent with how other single-page LiteLLM docs notes
  in this corpus are graded.
