---
source_url: https://docs.litellm.ai/docs/completion/stream
source_type: docs
title: "Streaming + Async | liteLLM (sync/async streaming, stream_chunk_builder, and the REPEATED_STREAMING_CHUNK_LIMIT runaway-stream guard)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: "unknown (living vendor docs; current as of 2026-10-05)"
date_extracted: 2026-10-05
last_checked: 2026-10-05
status: current
confidence_overall: emerging
issue: "#1585"
---

# Streaming + Async (LiteLLM Docs — `/docs/completion/stream`)

> LiteLLM's "Streaming + Async" page documents exactly one ops-relevant
> mechanism: a model that loops emitting the same chunk is detected by a
> consecutive-repetition counter and converted into
> `litellm.InternalServerError` "to allow retry logic to happen" — a bound
> that is **only** a bound (no timeout, no backoff, no retry wiring, and the
> check skips any chunk whose `delta.content` is `None` or ≤ 2 characters, so
> a loop of short deltas is unbounded). The remaining four sections are
> hello-world SDK usage, and the page's own `stream_chunk_builder` snippet does
> not run as printed.

## Source Context

- **Type**: docs (official LiteLLM vendor documentation, living Docusaurus page
  under "Guides > Core Requests > Streaming + Async"; the sibling page to
  `docs-litellm-completion-batching.md`'s `/docs/completion/batching`). Page
  title as published: "Streaming + Async".
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation —
  authoritative for the *surface* LiteLLM exposes (parameter names, config keys,
  exception type, sample code) and nothing more. The page carries no
  measurements, no benchmarks, no limits table, and no failure analysis. Its one
  substantive section is a **vendor surface description with no independent
  verification**, and the retry rationale it gives is an assertion about
  behavior the page never demonstrates.
- **Scope**: Five sections — "Streaming Responses" (`stream=True` +
  `part.choices[0].delta.content`), "Helper function"
  (`litellm.stream_chunk_builder`), "Async Completion" (`acompletion`),
  "Async Streaming" (`async for` over the object, described as an
  `__anext__()` implementation), and "Error Handling - Infinite Loops" (the
  guard). Also a three-row feature matrix (Streaming / Async / Async
  Streaming × LiteLLM SDK / LiteLLM Proxy). Followed the page's one substantive
  outbound link — GitHub issue
  [BerriAI/litellm#5158](https://github.com/BerriAI/litellm/issues/5158), the
  bug the guard was written to fix — and read it in full including all 14
  comments, because it is the only place the failure mode, its trigger, and
  the guard's design rationale are stated in prose. Additionally read the
  proxy page the feature matrix points the Proxy column at
  (`/docs/proxy/user_keys#streaming`), and resolved the guard's undocumented
  semantics against LiteLLM's own source and unit tests on `main` — see
  Extraction Notes for the exact files, line numbers, and the standing caveat
  that `main` is not a pinned release. Does **not** cover cost accounting,
  `stream_options`/`include_usage`, rate limits, or router fallbacks.
- **Extraction scope**: Per the Prospector's bounding, the first four sections
  are treated as boilerplate SDK usage and are **not** padded into claims; the
  note's claims come from the "Error Handling - Infinite Loops" section, the
  feature matrix, the linked issue, and the source verification. The
  `stream_chunk_builder` helper is captured briefly as requested.

## Extracted Claims

### Claim 1: The runaway-stream guard is the *only* bounded control documented on the page, and its entire stated job is to convert a hung stream into a retryable error — the page documents the failure, the trigger, and the exception type, and nothing about recovery
- **Evidence**: The "Error Handling - Infinite Loops" section, which opens by
  naming the failure, links the bug it came from, gives the setting, and states
  the outcome in one sentence. The section contains no timeout parameter, no
  backoff, no circuit-breaker language, no metric or log field, and no
  guidance on what the caller should do after the raise.
- **Confidence**: settled (for what the page does and does not state)
- **Quote**: "Sometimes a model might enter an infinite loop, and keep repeating the same chunks" / "LiteLLM provides error handling for this, by checking if a chunk is repeated 'n' times (Default is 100). If it exceeds that limit, it will raise a `litellm.InternalServerError`, to allow retry logic to happen."
- **Our assessment**: This is the load-bearing claim: on this page, and on
  the proxy streaming page it cross-links, an LLM stream that loops forever has
  **one** native bound and that bound is a repetition counter, not a time or
  cost limit. For an SRE writing a runbook, the practical consequence is that a
  hung stream is an *unbounded-spend-and-unbounded-connection* hazard whose
  only vendor-provided stop is content-shape-based — so the guide should pair
  this with a caller-side deadline and a spend cap rather than present the
  guard as "LiteLLM handles runaway streams".

### Claim 2: The default is 100, but the default's *rationale* exists only as an inline code comment — the prose states the number without ever explaining the false-positive trade-off
- **Evidence**: The prose sentence ("Default is 100") sits directly above a
  one-line code block whose trailing comment carries the reasoning. There is no
  dedicated prose paragraph on the default anywhere on the page, and the
  Feature / SDK / Proxy matrix has no row for the guard.
- **Confidence**: settled (the number and the comment are both explicit)
- **Quote**: `litellm.REPEATED_STREAMING_CHUNK_LIMIT = 100 # # catch if model starts looping the same chunk while streaming. Uses high default to prevent false positives.`
- **Our assessment**: "High default to prevent false positives" is a real and
  correct design statement — and it is also the whole risk disclosure. 100
  identical multi-character deltas is far past any plausible legitimate
  repetition, so the threshold is not aggressive; but the page never says what
  it costs to be wrong in the other direction (a loop that *is* caught late,
  after 99 duplicate chunks have already been delivered to the client and
  billed). An operator tuning this value should read the number as
  "how many duplicate tokens am I willing to pay for and ship before the
  gateway admits the stream is broken", not as a safety threshold.

### Claim 3: The failure mode is a documented *provider-side* bug with a concrete reproducer — Perplexity's `llama-3.1-sonar-large-128k-online` with a non-zero `frequency_penalty` and `stream=True` either truncates or repeats a word forever
- **Evidence**: The issue the section links to
  ([BerriAI/litellm#5158](https://github.com/BerriAI/litellm/issues/5158),
  "[Feature]: Perplexity streaming model enters loop -> catch and raise as
  InternalServerError", opened 2024-08-11, closed 2024-08-26), read in full
  with all 14 comments. Its body gives the request shape, and the
  maintainer's first reply states the provider scope. Two comments later in the
  thread record the same call succeeding on retry with no changes, which is
  the empirical basis for the "allow retry logic to happen" rationale.
- **Confidence**: settled (reported reproducer plus maintainer reproduction;
  the maintainer independently reproduced the raise on the same request)
- **Quote** (from the linked issue): "Perplexity streams break when the `frequency_penalty` parameter is set, example:" / "This seems to be only happening with Perplexity models." / "The same call with no changes @toniengelhardt works if you just retry -" / "this works for me as expected - i get an InternalServerError raised by litellm -"
- **Our assessment**: Two things the guide should carry. (1) The guard is a
  **provider-bug containment mechanism, not a client-bug detector** — the
  documented trigger is a specific upstream model emitting duplicate stream
  frames, so "we have the guard on" does not mean "our streams cannot loop".
  (2) The retry rationale is grounded in a real observation (the identical
  request succeeded on retry), which is why `InternalServerError` rather than
  a bespoke exception type is defensible here. It also explains why the guard
  is *content*-shaped: a provider that loops on a frame must be caught by
  frame comparison, since nothing in the request changes between the failing
  and succeeding attempt.

### Claim 4: Two configuration surfaces are documented — an SDK module global and a proxy `litellm_settings` key — and the page's own proxy guidance is to validate the proxy behavior by running the SDK snippet, i.e. it publishes no proxy-side verification
- **Evidence**: The section's "SDK" / "PROXY" tab pair: the one-line SDK global,
  then the `config.yaml` block, then a closing sentence that redirects
  validation to the SDK tab. There is no proxy curl example, no proxy log
  field, and no statement of how the proxy surfaces the raise to a client
  (status code, SSE error event, or truncated stream).
- **Confidence**: settled (both config keys are verbatim; the validation
  sentence is verbatim)
- **Quote**: "Define this on your config.yaml on the proxy." / `litellm_settings:    REPEATED_STREAMING_CHUNK_LIMIT: 100 # this overrides the litellm default` / "The proxy uses the litellm SDK. To validate this works, try the 'SDK' code snippet."
- **Our assessment**: "The proxy uses the litellm SDK" is doing real work and
  is the page's only justification for assuming the SDK knob transfers — it is
  an argument from implementation, not a documented proxy contract. The
  operational gap is what a proxy operator actually needs and cannot get here:
  **how does the raise reach the client through the proxy?** An SSE stream that
  has already emitted 200 and partial content cannot change its status code, so
  the client must be reading an error mid-stream, and this page does not say
  what that looks like on the wire. This is a concrete pre-rollout test item,
  not a defect claim — see our assessment on Claim 8 for what the source code
  says about *when* the raise happens relative to delivered chunks.

### Claim 5: What counts as "repeated" is `delta.content` equality between the **two most recent** chunks, and the counter is a *consecutive-run* counter — any single differing chunk resets it to zero, so a loop that varies even slightly never trips the guard
- **Evidence**: Verified in LiteLLM's own source rather than the page, because
  the page never defines the term. In
  `litellm/litellm_core_utils/streaming_handler.py` (main, fetched
  2026-10-05) the check `raise_on_model_repetition` (line 440) compares
  `self.chunks[-1].choices[0].delta.content` against
  `self.chunks[-2].choices[0].delta.content`, incrementing
  `self._repeated_messages_count` on equality and assigning `1` on inequality
  (lines 465–470), then raising when the count reaches the limit (line 472).
  The vendor's own parametrized unit test
  (`tests/unit/litellm_core_utils/test_streaming_handler.py`) pins this: a run
  of `LIMIT` identical chunks raises, `LIMIT - 1` does not, and inserting a
  single different chunk at the **start**, **middle**, or **end** of an
  otherwise-identical run yields `should_raise == False` under the test ids
  `first_chunk_different_no_raise`, `middle_chunk_different_no_raise`, and
  `last_chunk_different_no_raise`.
- **Confidence**: settled (source-verified and test-pinned; not asserted on the
  page)
- **Quote** (vendor source, `streaming_handler.py`): `last_content: Final = self.chunks[-1].choices[0].delta.content` / `second_to_last_content: Final = self.chunks[-2].choices[0].delta.content` / `if last_content == second_to_last_content:` / `if self._repeated_messages_count >= litellm.REPEATED_STREAMING_CHUNK_LIMIT:` / `raise litellm.InternalServerError(` / `message=f"The model is repeating the same chunk = {last_content}.",`
- **Our assessment**: **This is the answer to the question the docs decline to
  answer, and it narrows the guard's reach considerably.** It is a
  consecutive-duplicate detector, not a "the model is stuck" detector. A
  pathological stream that cycles a 3-token pattern (`"foo"`, `"bar"`,
  `"baz"`, forever) resets the counter on every chunk and runs unbounded, even
  though it is exactly as useless as the loop the guard exists to stop. Note
  also what the comparison ignores: only `delta.content` is compared — token
  identity, `finish_reason`, tool-call payloads, and multimodal delta fields
  are not. So the guard's blast radius is "identical visible text", full stop.
  The guide should describe it as a *duplicate-frame* tripwire with a known
  evasion (any variation resets it), not as runaway-stream protection.

### Claim 6: Chunks whose `delta.content` is `None`, non-string, or **2 characters or fewer** are exempt *and reset* the counter — so a loop emitting short deltas is unbounded, and the exemption exists because a user reported the guard misfiring on tool-call streams
- **Evidence**: Same function, lines 459–463: a chunk is skipped and the counter
  reset when `last_content is None or not isinstance(last_content, str) or
  len(last_content) <= 2`. The code's own trailing comment links the specific
  issue comment that motivated the exemption, and that comment is a *user*
  report, not a vendor statement: "would this be tripped if we make tool calls?
  I suspect this might be because the `delta`'s`content` would be empty for a
  long time (as the response isn't happening in `content`)". The maintainer's
  reply in the same thread states the rule in prose. The vendor's unit tests
  enshrine the boundary with `none_content_no_raise`,
  `empty_content_no_raise`, `short_content_1char_no_raise`,
  `short_content_2chars_no_raise`, and `short_content_2chars_ab_no_raise` — all
  `should_raise == False` at a full run of `LIMIT` chunks.
- **Confidence**: settled (source-verified, test-pinned, and traceable to the
  exact upstream report)
- **Quote** (vendor source): `last_content is None or not isinstance(last_content, str) or len(last_content) <= 2` / `# ignore empty content - https://github.com/BerriAI/litellm/issues/5158#issuecomment-2287156946` / (issue comment, KillianLucas, 2024-08-13) "would this be tripped if we make tool calls? I suspect this might be because the `delta`'s`content` would be empty for a long time (as the response isn't happening in `content`)" / (issue comment, maintainer, 2024-08-13) "Will ignore none chunks, empty chunks / anything less than 2 characters"
- **Our assessment**: A principled false-positive fix with a sharp edge. The
  exemption is *correct* — a tool-call stream legitimately emits many chunks
  with empty `delta.content`, and a naive counter would kill those streams — but
  it is implemented as a **reset**, not as a skip, so it converts "this stream
  is not the failure mode" into "this stream gets a fresh budget". An operator
  relying on the guard for tool-calling workloads should know that a degenerate
  loop of 1–2 character deltas (or of empty deltas) will never trip it. This
  is also the clearest evidence that the guard's contract lives in the code and
  not the docs: the page's "checking if a chunk is repeated 'n' times" is a
  summary that silently omits the carve-out that makes the feature usable at
  all.

### Claim 7: The counter is per-stream-wrapper state — per request, not per deployment, key, or model — and the limit is also readable from a `REPEATED_STREAMING_CHUNK_LIMIT` environment variable that the page never mentions
- **Evidence**: `self._repeated_messages_count = 1` is initialized in
  `CustomStreamWrapper.__init__` (`streaming_handler.py` line 279, class at
  line 207) alongside `self.chunks` (line 278); the check reads the module
  attribute `litellm.REPEATED_STREAMING_CHUNK_LIMIT` at stream time (line 472),
  and that attribute is defined in `litellm/constants.py` (lines 489–491) as
  `int(os.getenv("REPEATED_STREAMING_CHUNK_LIMIT", 100))` and re-exported in
  `litellm/__init__.py` (line 88). The page documents only the SDK global and
  the proxy `litellm_settings` key.
- **Confidence**: settled (source-verified)
- **Quote** (vendor source): `self.chunks: list = []  # keep track of the returned chunks - used for calculating the input/output tokens for stream options` / `self._repeated_messages_count = 1` / `REPEATED_STREAMING_CHUNK_LIMIT: Final = int(os.getenv("REPEATED_STREAMING_CHUNK_LIMIT", 100))`
- **Our assessment**: Two operational readings. (1) **Isolation is per-call**,
  which is the right default: one looping stream cannot trip the guard for
  concurrent traffic, and there is no cross-tenant state to reason about. It
  also means the guard cannot be used as an aggregate anomaly detector — it
  fires 100 times or 0 times per stuck request, with no shared signal. (2)
  **There is a third configuration surface the docs omit**: the environment
  variable. Since the env var is read once at import while the check reads the
  live module attribute, the documented post-import assignment (SDK global) and
  the proxy's `litellm_settings` both work, and the env var additionally works
  when set before process start. An operator who has "set it everywhere" via
  `litellm_settings` should confirm the value actually in force, because the
  env var and the config key are different surfaces and the page only
  documents one of the three.

### Claim 8: The raise happens *inside* the chunk iterator, after the already-repeated chunks have been yielded to the caller — so this is a mid-stream abort with partial output already delivered, not a pre-flight rejection
- **Evidence**: The check is invoked from `return_processed_chunk_logic` (line
  958, guarded by `if is_chunk_non_empty:`), which is called from
  `chunk_creator` (line 1518) whose `return result` (line 1523) is what the
  caller's `for chunk in response` / `async for` loop receives. The comparison
  uses `self.chunks[-1]` / `self.chunks[-2]`, i.e. chunks already appended on
  the way out (line 1064). Nothing in the path builds or validates the whole
  response before emitting.
- **Confidence**: settled (for the code fact — verified in
  `streaming_handler.py` on main, 2026-10-05)
- **Quote** (vendor source): `self.raise_on_model_repetition()` / `# expect to raise InternalServerError` (the page's own comment on the SDK validation snippet's loop body)
- **Our assessment**: The page's rationale — the exception exists "to allow
  retry logic to happen" — is weakest exactly here, and this is the finding the
  guide most needs. A `for chunk in response:` consumer has already rendered
  ~99 duplicate chunks to the user (or to a downstream agent's context) by the
  time the exception surfaces, and LiteLLM's own retry layer wraps the initial
  API call, not the iteration of an already-open stream — so "retry logic will
  happen" is a statement about the *exception type being retryable by whatever
  retry logic you have*, not a promise that LiteLLM re-issues the request. Any
  retry-on-error policy that counts this as a retryable upstream error must also
  handle **partially rendered duplicate output already in flight**, which is a
  client-side idempotency problem, not a gateway one. The page documents none
  of this.

### Claim 9: A `usage`-only or metadata-only chunk suspends detection rather than resetting it — the carve-out is explicitly motivated by Vertex Gemini with web search
- **Evidence**: `streaming_handler.py` lines 451–455: a comment naming the
  provider and the reason, followed by an early `return` when either of the two
  most recent chunks has no `choices`. Because this path returns *before* the
  comparison and before the counter assignment, the accumulated count survives
  an interleaved usage chunk.
- **Confidence**: settled (source-verified; the vendor states the reason inline)
- **Quote** (vendor source): `# Providers like Vertex Gemini (Flash / Flash Lite with web search) emit metadata-only / usage-only chunks with no choices. These get stored in self.chunks but carry no comparable content, so skip repetition detection.`
- **Our assessment**: Good engineering — the corpus's own streaming-usage
  finding (`docs-litellm-streaming-token-usage.md` Claim 2) establishes that
  empty-`choices` usage chunks are a real wire phenomenon, and a guard that
  counted them would misfire on exactly the providers documented as emitting
  them. Worth recording mainly because it is the one place in the guard where
  the implementation is *more* careful than the documentation, and because it
  marks a concrete third-party surface (Vertex + web search) where this guard
  has already needed a special case — i.e. the exemption list is not finished.

### Claim 10: The page's feature matrix has no row for the guard, and all three Proxy-column links point at a section that never mentions it — the runaway-stream guard is documented on exactly one page of the vendor docs
- **Evidence**: The matrix has three rows (Streaming, Async, Async Streaming),
  each with an SDK "start here" anchor on this page and a Proxy "start here"
  link to `/docs/proxy/user_keys#streaming`; there is no fourth row. The
  target page was fetched and searched in full (293 KB of HTML): zero
  occurrences of `REPEATED_STREAMING`, `repeated`, `infinite loop`,
  `stream_chunk_builder`, `include_usage`, or `always_include_stream_usage`. Its
  "Streaming" section does document proxy streaming (a `curl` with
  `"stream": true` and an OpenAI-SDK example).
- **Confidence**: settled (verified by full read of both pages)
- **Quote**: `| Async Streaming | ✅ [start here](#async-streaming) | ✅ [start here](/docs/proxy/user_keys#streaming) |` (this page's matrix) / "The proxy uses the litellm SDK." (this page, §4)
- **Our assessment**: Documentation reach, and it is a fair proxy for
  operational awareness: an operator who starts from the proxy streaming
  documentation — the natural entry point for a gateway deployment — will not
  find the guard, its config key, or the failure mode. The corpus has already
  recorded this class of gap as substantive rather than cosmetic
  (`docs-litellm-completion-output.md` Claim 9's conclusion that LiteLLM SDK
  samples should be treated as illustrative and guard logic verified against
  the prose and the library source). This note is a second instance, and it is
  stronger than a stale sample: the *entire mechanism* is missing from the
  page a proxy operator is likelier to read.

### Claim 11: `litellm.stream_chunk_builder(chunks, messages=messages)` is the documented way to rebuild a full response from accumulated chunks — and the page's snippet for it cannot run, because `chunks` is never initialized
- **Evidence**: The "Helper function" section's prose plus a five-line snippet
  that imports `completion`, iterates `for chunk in response:` and calls
  `chunks.append(chunk)` with no `chunks = []` anywhere in the block. In
  LiteLLM's source the function is `stream_chunk_builder(chunks: list, messages:
  Sequence | None = None, start_time=None, end_time=None, logging_obj=None,
  count_prompt_tokens: Callable[[], int] | None = None)` returning
  `ModelResponse | TextCompletionResponse | None`, returning `None` on an empty
  list and raising `litellm.APIError(status_code=500, ...)` if `chunks is None`
  — so the caller is expected to supply the list.
- **Confidence**: settled (the snippet defect is directly observable; the
  signature is source-verified)
- **Quote**: "LiteLLM also exposes a helper function to rebuild the complete streaming response from the list of chunks." / `for chunk in response:     chunks.append(chunk)print(litellm.stream_chunk_builder(chunks, messages=messages))`
- **Our assessment**: This is the corpus-relevant piece of the helper for a
  cost-accounting pipeline: it is the documented bridge from "I consumed a
  stream" to "I have a response object to log and price". Three caveats for the
  guide. (1) The snippet is broken as printed, so anyone following it
  verbatim gets a `NameError` — and the fix (initialize the list) is not in the
  docs. (2) `messages` is not decoration: it feeds prompt-token accounting when
  the stream carried no usage, so a reconstruction that omits it produces a
  rebuilt response with an incomplete picture — and the rebuilt object inherits
  whatever the stream reported, so a stream that never received its usage chunk
  (see Claim 12) reconstructs into a usage-less response. (3) The return type
  is a union with `None`, so `stream_chunk_builder([])` yields `None`, not an
  empty response — a real `AttributeError` path in an error handler.

### Claim 12: The guard's mid-stream abort means a tripped stream never delivers its usage chunk — so the corpus's streamed-cost accounting has an unmeasurable hole exactly on the requests that went wrong
- **Evidence**: Composition of Claim 8 with the corpus's established streaming
  wire contract: the usage totals arrive as a single extra chunk immediately
  before `data: [DONE]`
  (`docs-litellm-streaming-token-usage.md` Claims 1–2;
  `docs-litellm-completion-input-params.md` Claim 9). An exception raised inside
  the iterator terminates the stream, so no final usage chunk is ever produced
  for that request. The gateway-side remedy the corpus already documents,
  `general_settings: always_include_stream_usage: true`
  (`docs-litellm-completion-output.md` Claim 10), forces the flag on — it does
  not force a chunk to exist.
- **Confidence**: settled for the mechanism (both halves source-verified /
  documented); the accounting consequence is our assessment, not a vendor claim
- **Quote**: (no direct quote; see Our assessment — the two halves are quoted in
  the two corpus notes cited)
- **Our assessment**: Per the guide's existing rule, "pass
  `stream_options={"include_usage": True}` and read the final usage chunk"
  [source: docs-litellm-streaming-token-usage, Claim 1, Claim 2] — this note
  supplies the failure branch that rule does not cover: when a stream aborts,
  there is no final chunk, so a gateway that logs stream spend from that chunk
  logs **nothing at all** for precisely the requests that burned the most
  tokens. That is the same silent-zero shape the chapter already flags for
  `include_usage` opt-out, with a worse trigger. The operational recommendation
  is therefore not "also pass the flag" but "meter streamed requests from a
  source that survives an abort" — accumulate deltas client-side, or bound
  spend per stream independently of whether a usage chunk arrives. Consider
  also recording the *repetition abort* itself as a first-class error class,
  because `InternalServerError` from a stream mid-delivery is not
  distinguishable, client-side, from a provider 500 that arrived before any
  content.

### Claim 13: Both of the page's guard-related snippets do not run as printed, and the SDK validation snippet is itself internally odd — it repeats a chunk carrying `finish_reason: "stop"` 101 times and calls `time.time()` with no `import time`
- **Evidence**: Direct inspection of the page's code blocks. The SDK validation
  snippet imports `litellm` and `os` (with `os` unused), builds
  `chunks = [litellm.ModelResponse(**{...}, stream=True)] * loop_amount` with
  `loop_amount = litellm.REPEATED_STREAMING_CHUNK_LIMIT + 1`, and every
  repeated chunk is `"finish_reason": "stop"` — i.e. 101 copies of a
  terminal-chunk marker. The same snippet passes `time.time()` to
  `litellm.Logging(...)` while importing `time` nowhere, and drives the loop
  through the low-level `litellm.CustomStreamWrapper` / `ModelResponseListIterator`
  internals with `custom_llm_provider="cached_response"`. Its embedded
  `created` value is `1694268190` (2023-09-09).
- **Confidence**: settled (all four defects directly observable in the fetched
  page)
- **Quote**: `"created": 1694268190,` / `"finish_reason": "stop"` / `import litellm import os litellm.set_verbose = Falseloop_amount = litellm.REPEATED_STREAMING_CHUNK_LIMIT + 1` / `start_time=time.time(),` / `# expect to raise InternalServerError`
- **Our assessment**: Minor individually, but the aggregate is a signal worth
  one line in the guide's source-quality guidance, and it is a pattern the
  corpus has already recorded twice (the batching page's `print(result)` on an
  object assigned to `response`, and the mock-responses page's three-year-old
  `created` value). The consequential one is the `finish_reason: "stop"`
  repetition: it means the vendor's own validation exercises a stream that is
  *terminally finished* 101 times, which is not the failure mode the guard was
  written for (a live stream looping on content). An operator copying this
  snippet as a smoke test is validating the counter, not the production
  scenario — and will not notice if the guard is broken for the case that
  matters. Recommend a real-loop test against a provider (or a fixture with
  `finish_reason: None` on every chunk) rather than the vendor's snippet.

### Claim 14: The page's async surface is documented as `__anext__()`-backed iteration with a bare `except:` in the sample — the one ops-relevant detail is that the example swallows the guard's exception class along with everything else
- **Evidence**: The "Async Streaming" section's prose plus its sample, which
  wraps the whole async call in `try:` / `except:` with `print(f"error
  occurred: {traceback.format_exc()}")` / `pass`. The same shape appears for
  the guard: the page's error-handling section shows no `try`/`except` at all,
  and the validation snippet's loop body is a bare `continue`.
- **Confidence**: settled (verbatim from the page)
- **Quote**: "We've implemented an `__anext__()` function in the streaming object returned. This enables async iteration over the streaming object." / `except:        print(f"error occurred: {traceback.format_exc()}")        pass`
- **Our assessment**: The `__anext__()` detail itself is boilerplate and the
  Prospector asked for it only "where it differs from the synchronous
  section" — it does not, beyond the await points. The part worth recording is
  the interaction with Claim 8: the page's *only* async-streaming example
  catches everything and passes, so a service written from this page will
  classify a repetition abort as a generic logged-and-ignored condition rather
  than an error to surface. Under `async for`, the partial duplicate output is
  already delivered to the consumer before the exception propagates — so a
  swallow-and-continue handler produces a user-visible truncated stream of
  repeated text with no error surfaced anywhere but a log line. That is the
  concrete failure to write a runbook against, and it is assembled from the
  page's own two sections rather than stated anywhere.

## Concrete Artifacts

**The guard's SDK configuration line, verbatim as printed** (note the doubled
`#` and the rationale living in a trailing comment):

```python
litellm.REPEATED_STREAMING_CHUNK_LIMIT = 100 # # catch if model starts looping the same chunk while streaming. Uses high default to prevent false positives.
```

**The guard's proxy configuration, verbatim as printed:**

```yaml
litellm_settings:    REPEATED_STREAMING_CHUNK_LIMIT: 100 # this overrides the litellm default
```

**The page's SDK validation snippet, verbatim as printed** (line breaks and
indentation restored; `os` is imported and unused, `time` is used and never
imported, and all 101 chunks carry `finish_reason: "stop"`):

```python
import litellm
import os

litellm.set_verbose = False

loop_amount = litellm.REPEATED_STREAMING_CHUNK_LIMIT + 1

chunks = [
    litellm.ModelResponse(
        **{
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1694268190,
            "model": "gpt-5.6-luna",
            "system_fingerprint": "fp_44709d6fcb",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "How are you?"},
                    "finish_reason": "stop",
                }
            ],
        },
        stream=True,
    )
] * loop_amount

completion_stream = litellm.ModelResponseListIterator(model_responses=chunks)

response = litellm.CustomStreamWrapper(
    completion_stream=completion_stream,
    model="gpt-5.6-luna",
    custom_llm_provider="cached_response",
    logging_obj=litellm.Logging(
        model="gpt-5.6-luna",
        messages=[{"role": "user", "content": "Hey"}],
        stream=True,
        call_type="completion",
        start_time=time.time(),
        litellm_call_id="12345",
        function_id="1245",
    ),
)

for chunk in response:
    continue # expect to raise InternalServerError
```

**The `stream_chunk_builder` helper, verbatim as printed** (note: no `chunks`
initialization anywhere in the block — this snippet raises `NameError`):

```python
from litellm import completion

messages = [{"role": "user", "content": "Hey, how's it going?"}]

response = completion(model="gpt-5.6-luna", messages=messages, stream=True)

for chunk in response:
     chunks.append(chunk)

print(litellm.stream_chunk_builder(chunks, messages=messages))
```

**The async-streaming sample, verbatim as printed** (the bare `except:` that
swallows every error class, including the guard's):

```python
from litellm import acompletion
import asyncio, os, traceback

async def completion_call():
    try:
        print("test acompletion + streaming")
        response = await acompletion(
            model="gpt-5.6-luna",
            messages=[{"content": "Hello, how are you?", "role": "user"}],
            stream=True
        )
        print(f"response: {response}")
        async for chunk in response:
            print(chunk)
    except:
        print(f"error occurred: {traceback.format_exc()}")
        pass

asyncio.run(completion_call())
```

**The guard's actual implementation** (from
`litellm/litellm_core_utils/streaming_handler.py` on `main`, fetched
2026-10-05 — **not** a page artifact; included because the page does not define
what "repeated" means. Line numbers as fetched):

```python
def raise_on_model_repetition(self) -> None:          # line 440
    """
    Fixes - https://github.com/BerriAI/litellm/issues/5158

    if the model enters a loop and starts repeating the same chunk again, break out of loop and raise an internalservererror - allows for retries.

    Raises - InternalServerError, if LLM enters infinite loop while streaming
    """
    if len(self.chunks) < 2:
        return

    # Providers like Vertex Gemini (Flash / Flash Lite with web search) emit
    # metadata-only / usage-only chunks with no choices. These get stored in
    # self.chunks but carry no comparable content, so skip repetition detection.
    if not self.chunks[-1].choices or not self.chunks[-2].choices:   # line 454
        return

    last_content: Final = self.chunks[-1].choices[0].delta.content

    if (
        last_content is None or not isinstance(last_content, str) or len(last_content) <= 2
    ):  # ignore empty content - https://github.com/BerriAI/litellm/issues/5158#issuecomment-2287156946
        self._repeated_messages_count = 1
        return

    second_to_last_content: Final = self.chunks[-2].choices[0].delta.content

    if last_content == second_to_last_content:      # line 467
        self._repeated_messages_count += 1
    else:
        self._repeated_messages_count = 1

    if self._repeated_messages_count >= litellm.REPEATED_STREAMING_CHUNK_LIMIT:   # line 472
        # All last n chunks are identical
        raise litellm.InternalServerError(
            message=f"The model is repeating the same chunk = {last_content}.",
            model="",
            llm_provider="",
        )
```

**The limit's definition — a third, undocumented configuration surface**
(`litellm/constants.py`, lines 489–491, `main` @ 2026-10-05). The trailing
comment is character-identical to the page's inline comment, confirming the docs
comment is copied from the constant:

```python
#### RELIABILITY ####
REPEATED_STREAMING_CHUNK_LIMIT: Final = int(
    os.getenv("REPEATED_STREAMING_CHUNK_LIMIT", 100)
)  # catch if model starts looping the same chunk while streaming. Uses high default to prevent false positives.
```

**The per-request state that carries the counter**
(`streaming_handler.py`, lines 278–279, inside `CustomStreamWrapper.__init__`,
class at line 207):

```python
self.chunks: list = []  # keep track of the returned chunks - used for calculating the input/output tokens for stream options
self._repeated_messages_count = 1
```

**The upstream issue the guard fixes — the request that triggered it**
([BerriAI/litellm#5158](https://github.com/BerriAI/litellm/issues/5158), from
the issue body, verbatim):

```python
messages = [
    { 'role': 'system', 'content': 'You are a wise and all-knowing oracle.' },
    { 'role': 'user', 'content': 'What is the meaning of the Universe?\n\nDon\'t say 42.\n\nAnswer:' },
]

res = completion(
  'perplexity/llama-3.1-sonar-large-128k-online',
  messages=messages,
  api_key=PERPLEXITY_API_KEY,
  frequency_penalty=0.1,
  stream=True,
)
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path is cited or
dismissed):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: the
  asynchronous `/v1/files` + `/v1/batches` job API with a thorough
  submission-time metering contract. Its Claims 1 and 3 (limits charged at
  `POST /v1/batches`; `batch_enqueued_token_limit` as the remedy for per-minute
  windows) describe a surface with no streaming and no repetition detection.
  The only adjacency is vocabulary — "loop"-shaped unbounded work — and citing
  it would imply an answer about stream behavior it does not contain.
- `source-notes/docs-litellm-completion-input-params.md` — **cited**
  (Composes / Extends; Claims 5, 7, 13; this is the corpus's home for the
  request-side reliability contract). **Claim 5** ("The documented default client
  timeout is **600 seconds** — and the page's own signature declares `timeout:
  Optional[Union[float, int]] = None`, so the prose default and the code default
  on the same page disagree") is the corpus's only LiteLLM timeout evidence,
  and this page documents *no* timeout for a stream at all (Claim 1) — so the
  corpus now holds two mutually unreconciled statements about how long a LiteLLM
  call may run. **Claim 7** (JSON mode without an explicit instruction is a documented
  liveness failure — the model emits an unbounded whitespace stream until the
  token limit, which the vendor describes as a long-running, seemingly stuck
  request) is the *other* documented hung-stream mode, and
  its bound is `max_tokens` rather than a repetition count; the two hazards are
  complementary, not competing. **Claim 13** ("SDK-level `fallbacks` has no
  time budget, no loop and no cooldown — each entry is tried exactly once in
  order, total failure raises the last error suffixed `All fallback attempts
  failed`, and the successful response carries an `x-litellm-attempted-fallbacks`
  header") is the corpus's statement of what *does* exist for retries — and it
  establishes that retry/backoff is delegated to the Router, which is precisely
  what this page's "to allow retry logic to happen" leaves unspecified
  (Claim 8). Its **Claim 9** is the same streaming-usage wire contract cited in
  Claim 12.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: the Bedrock
  native `/invoke` passthrough; its claims are SigV4→bearer auth swapping and a
  per-provider support matrix. No streaming-loop content.
- `source-notes/docs-litellm-mock-requests.md` — **cited** (Corroborates, the
  staleness precedent; Claim 4, verified). Its **Claim 4** records the mock
  sample's `"created": 1694459929.4496052` as a ~3-year-stale example value; this
  page's guard snippet carries `"created": 1694268190` (2023-09-09) in the same
  style, so LiteLLM's *illustrative* code samples now have a documented
  cross-page pattern of carrying frozen 2023 timestamps. Its Claims 2 and 5
  (mock `usage` fields all `null`; the mock works with `stream=True` and is
  delivered as `delta` fragments) are adjacent to this page's streaming surface
  but make claims about mocking, not about repetition detection.
- `source-notes/docs-litellm-audio-transcription.md` — **dismissed**:
  per-request `fallbacks[]` on a non-chat endpoint plus the
  `model_info: mode: audio_transcription` registration requirement. Sequential
  failover on a different endpoint; nothing about stream frames.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **dismissed**: its
  nearest-sounding claim (its **Claim 4**, "Streaming contains a non-streaming
  hop — the advisor sub-inference does not stream, the executor's stream pauses
  while it runs") concerns a *pause*, not a repeat, and neither page says
  anything about the other's mechanism. Citing it would imply an interaction
  neither source documents.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: per-field
  ✅/❌ signature-stripping on A2A agent cards. Different protocol surface.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited** (Extends /
  contrast; Claims 3 and 4, verified). The corpus's only documented LiteLLM
  spend/call controls are `max_iterations` and `max_budget_per_session`, both
  **A2A-session-scoped**. Its **Claim 4** ("The budget control has asymmetric
  timing — spend is accumulated *after* each successful LLM call and checked
  *before* each call, so a single over-budget call reaches the provider and the
  excess is only rejected on the next call") is the same
  check-after-the-fact shape as this guard (Claim 8: the abort happens after ~99
  duplicate chunks are already delivered and billed) — a recurring LiteLLM
  pattern in which every documented control is enforced one step *behind* the
  spend it is meant to bound. Its **Claim 3** (a request over the cap receives
  a 429) is the other kind of control: rejection *before* the call, which is
  what the guard is not.
- `source-notes/docs-litellm-bedrock-converse.md` — **dismissed**: the Bedrock
  native `/converse` passthrough; adjacent only as another `/bedrock/...` route,
  with a support matrix and no streaming-failure content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: the toil
  taxonomy and the automate-the-measurement argument. One could argue a
  repetition abort is a codified toil trigger, but the chapter's six
  characteristics and its measurement method are not claims about gateway
  behavior, and stretching the citation would manufacture relevance.

**Additional cross-references found by searching `source-notes/` directly**
(beyond the candidate list):

- `source-notes/docs-litellm-completion-batching.md` — **cited** (Fills a gap
  this note closes; the triage-named neighbour). Its **Claim 9** ("Nothing on
  the page describes the concurrency mechanism, and nothing describes the
  rate-limit, retry, or fallback interaction of the N parallel calls") and its
  Extraction Notes both record that this page exists and documents the
  repeated-chunk guard, while extracting no claim about it — that is precisely
  the hole this note fills. Two of its claims now compose into live
  operational questions: its **Claim 10** (the page's only streaming example
  pairs `fastest_response: true` with `"stream": true` and never says how
  "first response" behaves on a stream) means a *hedged streaming* request can
  sit inside a repetition abort with the hedge-set question unanswered, and its
  **Claim 3** (winner-only `usage` on a documented latency path) compounds
  Claim 12 — on a hedged stream the loser calls are absent from `usage` *and*
  the winner may never deliver a usage chunk at all.
- `source-notes/docs-litellm-streaming-token-usage.md` — **cited**
  (Corroborates / Composes; Claims 1 and 2, verified). Its **Claim 1** ("A
  streaming completion does not report token usage unless the client opts in with
  `stream_options={"include_usage\": True}`") and **Claim 2** (the usage chunk
  is a single extra chunk before `data: [DONE]` with empty `choices`, all other
  chunks `usage: null`) are the precondition and the wire shape that Claim 12
  turns into a failure branch. Its own §Scope note flags sections 1–2 of the
  old `/stream` page as boilerplate; this page is the **diverged successor** to
  that `/stream` page (different URL, and no `stream_options`/`include_usage`
  content here at all — verified by full read), so the two notes are
  complementary rather than duplicative, and the corpus should stop citing
  "LiteLLM's streaming page" as a single thing.
- `source-notes/docs-litellm-completion-output.md` — **cited** (Corroborates /
  Extends; Claims 9 and 10, verified). Its **Claim 10** documents the
  gateway-side remedy `general_settings: always_include_stream_usage: true`,
  which force-injects `include_usage` into all streaming requests — this is the
  correct mitigation to pair with the guard, and its limit is the point of
  Claim 12 (the flag does not conjure a final chunk on an aborted stream). Its
  **Claim 9** ("All five code blocks on the page are published with their line
  breaks collapsed, so none of the page's four artifacts is copy-pasteable as
  rendered") is the corpus precedent for the same fetch/rendering defect on this
  page's seven blocks, and its conclusion — treat LiteLLM SDK samples as
  illustrative and verify guard logic against the prose and the library source —
  is exactly what Claims 5, 6 and 13 had to do.
- `source-notes/docs-litellm-completion-http-handler-config.md` — **cited**
  (Corroborates the "no bound is documented" finding; Claims 7 and 10,
  verified). Its **Claim 7** records three mutually inconsistent timeout/pool
  profiles on the sibling config page (dev `total=60`, main example `total=180`,
  "Production" `total=300`) with no stated derivation, and its **Claim 10**
  records that the page documents no verification step at all. With
  `docs-litellm-completion-input-params.md` Claim 5 (600s prose vs `None`
  code), the corpus now holds **four** unreconciled timeout figures across
  three adjacent LiteLLM pages and no stated stream-level deadline anywhere.
  That is a coverage gap in our own guidance as much as a vendor-documentation
  gap, and it is why this note's Claims 1 and 8 recommend a caller-side
  deadline rather than deferring to a vendor default.
- `blog-litellm-redis-circuit-breaker.md` — **cited** (Extends / tension;
  Claim 7, verified). Its **Claim 7** ("Retry logic still waits for each
  timeout (30s × retries). The circuit breaker cuts the connection immediately
  at 0ms after the failure threshold, preventing threadpool exhaustion across all
  pods simultaneously. Retries make slow-Redis worse; the circuit breaker
  contains it.") is the corpus's statement of the principle this guard's design
  depends on and does not enforce: retrying is only safe because the failure
  became *fast*. A repetition abort at chunk 100 is fast; a stream that loops
  emitting varying deltas (Claim 5's evasion) is not caught at all, and a
  caller that wraps such a stream in retry logic inherits precisely the
  amplification this post warns about.
- `failure-litellm-prisma-reconnect-event-loop-blocking.md` — **cited**
  (Corroborates, the corpus's other LiteLLM hang; Claims 1 and 2, verified).
  Its **Claim 1** ("A synchronous `subprocess.Popen.wait()` hidden inside
  `prisma-client-py`'s async `Engine.aclose()` could block the entire asyncio
  event loop, defeating any timeout mechanism that relies on `await` points") and
  **Claim 2** ("`asyncio.wait_for()` is not a safety net for synchronous blocking
  calls — it can only cancel at `await` points") are the corpus's precedent for
  a hang that a timeout *cannot* clear. A repeated-chunk loop is the opposite
  case and that contrast is the useful part: the event loop stays healthy and
  chunks keep arriving, so a caller's `wait_for`/deadline **can** fire, and the
  guard is an application-level bound layered on top of that. Both notes agree
  on the operational rule they imply — the caller-side deadline is the control
  that survives both failure shapes, and the vendor mechanism is a second,
  weaker layer.
- **Contradicts**: none found, and **no contradiction issue filed** per MINER.md
  §4a. Two candidates were considered and rejected as *conditioning variables*
  rather than contradictions, per §4a's "When NOT to file":
  (1) `docs-litellm-completion-output.md` **Claim 10** ("all streaming requests
  will automatically have `stream_options={"include_usage": True}` added") vs.
  Claim 12's finding that an aborted stream delivers no final usage chunk. Both
  are true simultaneously — the flag *is* added; the stream *does* abort — so
  this is a limit on a guarantee, not a disagreement about a fact, and the
  resolution belongs in this note's assessment (Claim 12), not in a
  contradiction issue.
  (2) `docs-litellm-completion-input-params.md` **Claim 5** (600s default client
  timeout) vs. this page's silence on any stream timeout. An omission is not an
  opposing claim. Grepped `source-notes/`, `guide/`, and `CONTRADICTIONS.md`
  before deciding: zero prior mentions of `REPEATED_STREAMING_CHUNK_LIMIT`,
  `stream_chunk_builder`, or `InternalServerError` anywhere in the corpus
  (the single pre-existing hit is the batching note's Extraction Notes mention),
  and no open `C-NNN` entry covers stream repetition.
- **Novel**: (1) The corpus's **only documented bound on a hung LLM stream**,
  and the first evidence that LiteLLM treats stream-frame duplication as a
  retryable server-side condition at all — every other LiteLLM note in the
  corpus documents selection, deferral, metering, caching, or security. (2) The
  precise **semantics the docs omit**: consecutive-duplicate `delta.content`
  comparison with a full reset on any variation (Claim 5), an exemption at ≤ 2
  characters that resets rather than skips (Claim 6), per-request state plus an
  undocumented env-var configuration surface (Claim 7), and an early return for
  usage-only chunks motivated by Vertex Gemini with web search (Claim 9) —
  resolved against source and the vendor's own parametrized unit tests, not
  guessed. (3) The **mid-stream** nature of the abort (Claim 8), which is what
  makes the page's "to allow retry logic to happen" rationale weakest exactly
  where an operator would rely on it. (4) The **usage hole on failed streams**
  (Claim 12): the requests that burned the most tokens are the ones a
  usage-chunk-based cost meter records as nothing. (5) A named, dated **upstream
  provider trigger** (Perplexity + `frequency_penalty`, issue #5158) making this
  a provider-bug containment control rather than a general safety net (Claim 3).

## Guide Impact

- **Chapter 05 — "LLM Ops Reliability"**, as a new subsection beside the
  existing "Streamed traffic is usage-blind by default" rule (~L1209-1242):
  that rule currently reads "Pass `stream_options={"include_usage": True}` on
  every streamed request the gateway meters, read totals from the final usage
  chunk rather than summing deltas." It is **incomplete on the failure branch**
  and should be amended, not restated: add that when a stream aborts mid-flight
  — for example on LiteLLM's repetition guard — the final usage chunk never
  arrives, so the meter records nothing for precisely the highest-token requests
  [source: docs-litellm-completion-stream, Claim 12; docs-litellm-streaming-token-usage,
  Claim 2] [settled for the mechanism, emerging for the recommendation]. Pair it
  with the gateway-side flag the corpus already documents
  (`general_settings: always_include_stream_usage: true`,
  `docs-litellm-completion-output.md` Claim 10) and state explicitly that the
  flag governs *availability of the flag*, not existence of the chunk.
- **Chapter 05**, same subsection, as a new bounded rule: **a looping stream is
  bounded by content-shape, not by time or money.** LiteLLM's
  `REPEATED_STREAMING_CHUNK_LIMIT` (default 100) compares only
  `delta.content` of the two most recent chunks, resets on any variation, and
  skips-and-resets any chunk with `None` or ≤ 2 characters of content — so the
  guide should say plainly that a stream cycling a short varying pattern, or
  emitting ≤ 2-character deltas, is **unbounded** by this control, and that the
  only reliable stop is a caller-side deadline plus a per-stream spend cap. This
  is the first time the guide can name what a specific knob does *not* cover
  [source: docs-litellm-completion-stream, Claims 1, 5, 6, 7] [settled].
- **Chapter 05**, retry/fallback guidance: correct the implicit reading of the
  page's "raise ... to allow retry logic to happen." The raise happens *inside*
  the chunk iterator after the duplicate content has already been delivered to
  the client, and LiteLLM's retry layer wraps the initial call rather than the
  iteration of an open stream — so treat the repetition abort as **partial
  output plus a retryable error**, handle the idempotency of already-emitted
  duplicate text client-side, and record it as its own error class (it is not
  distinguishable, mid-stream, from a provider 500 that arrived before any
  content). Cross-reference the existing Router-delegation rule
  (`docs-litellm-completion-input-params.md` Claim 13) so the chapter stops
  implying that a raised error implies a re-issued request
  [source: docs-litellm-completion-stream, Claim 8] [emerging].
- **Chapter 05**, timeout/deadline guidance: the corpus now holds four
  unreconciled LiteLLM timeout figures across three adjacent pages and **no
  stream-level deadline in any of them** (600s prose vs `None` code;
  `total=60/180/300`; this page's silence). Recommend the Smith add an explicit
  "do not rely on a vendor default for stream liveness" line and cite this page
  as the case where a *repeated* hang has no time bound at all, only a repetition
  bound [source: docs-litellm-completion-stream, Claims 1, 4;
  docs-litellm-completion-input-params, Claim 5;
  docs-litellm-completion-http-handler-config, Claim 7] [emerging].
- **Chapter 02 (Observability), secondary**: one sentence on why
  "LiteLLM's streaming page" should stop being cited as a single source — the
  corpus now has two diverged pages (`/stream` and `/docs/completion/stream`),
  and the guard is documented on only one of them, absent from the proxy
  streaming documentation the vendor's own feature matrix points proxy operators
  at [source: docs-litellm-completion-stream, Claim 10] [settled].
- **Chapter 05**, source-quality guidance: this note is a third instance (with
  `docs-litellm-completion-batching.md` Claim 12 and
  `docs-litellm-completion-output.md` Claim 9) of LiteLLM docs samples that do
  not run as printed. The one worth generalizing is Claim 13's: the vendor's own
  validation snippet repeats a `finish_reason: "stop"` chunk 101 times, so
  copying it as a smoke test validates the counter and not the production
  failure mode [source: docs-litellm-completion-stream, Claims 11, 13] [settled].

## Extraction Notes

- **Page read in full** (HTTP 200, no paywall, no truncation): title,
  breadcrumb path (`Guides → Core Requests → Streaming + Async`), the three-row
  feature matrix, all five sections, both config blocks, all seven code blocks,
  and the footer nav. Followed the page's one substantive outbound link —
  GitHub issue
  [BerriAI/litellm#5158](https://github.com/BerriAI/litellm/issues/5158) — and
  read the issue body plus all 14 comments, because the guard section is a
  summary of that bug and the issue is where the failure mode, the trigger, the
  false-positive report, and the retry rationale are stated in prose. Also
  fetched and searched in full the proxy page the matrix's Proxy column points
  at (`https://docs.litellm.ai/docs/proxy/user_keys`, 293 KB) to test whether
  the guard is documented there; it is not (Claim 10). Not followed: the
  Academy/Gateway-Quickstart links, the sidebar's unrelated pages, and the
  `docs/completion/usage` sibling (already mined as
  `docs-litellm-completion-output.md` Claim 10).
- **Source-code verification, with a standing caveat.** Five claims (5, 6, 7, 8,
  9) answer questions the page does not answer, so they are grounded in
  LiteLLM's own repository at `main`, fetched 2026-10-05 via
  `raw.githubusercontent.com`, at these paths and line numbers:
  `litellm/litellm_core_utils/streaming_handler.py` (guard at lines 440–479;
  call site 958; `chunk_creator` return 1518–1523; per-request state 207, 278–279),
  `litellm/constants.py` (489–491), `litellm/__init__.py` (88),
  `litellm/main.py` (`stream_chunk_builder`, 9006–9012), and
  `tests/unit/litellm_core_utils/test_streaming_handler.py` (the parametrized
  repetition cases). **Caveat for the Assayer and the Smith: `main` is a moving
  target, not a released version, so these claims describe current upstream
  behavior and may differ from whatever version a deployment pins.** They are
  marked `settled` as *source-verified facts about `main` on 2026-10-05*,
  separately from the page's own claims, and every one of them is quoted from
  the fetched file. The unit-test ids cited in Claim 5 are load-bearing: they
  are the vendor's own encoding of the boundary semantics, so if a future
  release changes the behavior the tests change first.
- **Quotes**: every `Quote` field and every quoted string in this note was
  copied character-for-character from its source. Quotes attributed to the page
  come from the fetched HTML/Markdown of
  `https://docs.litellm.ai/docs/completion/stream`; quotes attributed to the
  linked issue come from the GitHub REST API for issue #5158 (body and
  comments, including the specific comment at
  `issuecomment-2287156946` that the source code cites by URL — verified to be
  the third-party report, not the maintainer's reply, which is why Claim 6
  attributes the exemption to a *user report*); quotes marked "vendor source"
  come from the raw files listed above. Where a link sits inside a sentence I
  quoted only the contiguous prose on one side of it (e.g. "Sometimes a model
  might enter an infinite loop, and keep repeating the same chunks" stops before
  the inline link rather than splicing across it). Claims whose substance is our
  synthesis across sources carry `Quote: (no direct quote; see Our assessment)`
  — Claim 12 — rather than a reconstructed quotation.
- **Whitespace in code blocks**: as fetched, all seven code blocks on this page
  arrive with their line breaks collapsed (one unbroken run per block), which
  matches `docs-litellm-completion-output.md` Claim 9 for the sibling output
  page. In Concrete Artifacts the **line breaks and indentation have been
  restored**; no token inside a block was added, removed, or reordered, and the
  page's own defects (`chunks` never initialized in the
  `stream_chunk_builder` snippet; the doubled `#` in the guard comment; the
  unused `os` import and missing `import time` in the validation snippet;
  `for chunk in response:     chunks.append(chunk)`'s five-space indent) are
  reproduced as printed.
- **Bounding honored.** Per the Prospector's instruction not to pad the note with
  boilerplate, the three hello-world sections (`stream=True` iteration,
  `acompletion`, `async for` / `__anext__()`) yield exactly one claim — Claim 14,
  and only for the bare `except:` in the async sample, since the body of those
  sections carries no ops content. The note's substance is the "Error Handling -
  Infinite Loops" section, the linked issue, the feature matrix, the
  `stream_chunk_builder` snippet, and the source verification. This is a thin
  page; a note proportionate to it is the correct outcome, and `confidence_overall`
  is set to **emerging** rather than `settled` for that reason: the *documented
  surface* is settled, but it is one thin living vendor page whose one mechanism
  we verified against moving upstream source rather than a released version, and
  whose retry interaction (the page's own stated purpose) remains undocumented.
- **Not a duplicate.** Verified `source_url: https://docs.litellm.ai/docs/completion/stream`
  appears in no existing note, consistent with the Prospector's duplicate check.
  The nearest note, `docs-litellm-streaming-token-usage.md`, covers a different
  URL (`https://docs.litellm.ai/stream`) and a different mechanism; this page
  contains no `stream_options` or `include_usage` content at all. Grepped
  `source-notes/` and `guide/` for `REPEATED_STREAMING_CHUNK_LIMIT`,
  `stream_chunk_builder`, and `InternalServerError` before writing: the only
  pre-existing hit is one passing mention in
  `docs-litellm-completion-batching.md`'s Extraction Notes. No contradiction
  issue filed — reasoning in Cross-References → Contradicts.