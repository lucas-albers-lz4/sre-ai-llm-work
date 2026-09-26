---
source_url: https://docs.litellm.ai/docs/completion/batching
source_type: docs
title: "Batching Completion() — LiteLLM Documentation (synchronous fan-out: batch_completion_models + proxy fastest_response)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: "unknown (living vendor docs; current as of 2026-09-26)"
date_extracted: 2026-09-26
last_checked: 2026-09-26
status: current
confidence_overall: emerging
issue: "#1467"
---

# Batching Completion() (LiteLLM Docs)

> LiteLLM's `/docs/completion/batching` page documents a *latency* primitive
> wearing a *batch* name: `batch_completion_models()` fans one prompt out to N
> providers in parallel, returns the first response, and "Cancels other LLM API
> calls" — while publishing a winning-response-only `usage` block, no billing
> semantics for the cancelled siblings, no rate-limit or retry accounting for
> the N concurrent calls, and no error contract for the all-fail case. For a
> platform team, the documented capability is solid and its governance is absent.

## Source Context

- **Type**: docs (official LiteLLM vendor documentation, living Docusaurus page
  under "Guides > Core Requests > Batching Completion()", the canonical page for
  the synchronous SDK fan-out helpers).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation —
  authoritative for the *surface* LiteLLM exposes (helper names, signatures,
  request/response shapes, the `fastest_response` flag, the sample outputs). The
  page carries no measurements, no benchmarks, and no billing, limit, or failure
  analysis, so nothing about cost or latency *effectiveness* is established here
  and none is inferred.
- **Scope**: Three synchronous helpers (`batch_completion`,
  `batch_completion_models`, `batch_completion_models_all_responses`), the proxy
  equivalent (comma-separated `model` string + `fastest_response: true`), a
  two-model `config.yaml`, and two sample output dumps. Followed to the one
  substantive linked page — the proxy's own "(BETA) Batch Completions" section
  on `/docs/proxy/user_keys` — plus the sibling "Streaming + Async" page to
  look for a documented concurrency model. Does **not** cover the asynchronous
  `/v1/files` + `/v1/batches` Batch API (that surface is
  `source-notes/docs-litellm-batches-api.md`, issue #1415, and the two must not
  be conflated — see Cross-References), router fallbacks, or cost tracking.

## Extracted Claims

### Claim 1: The page documents three *synchronous, in-process* fan-out helpers under one heading, and only the "return fastest" one has any stated behavior contract — the other two are code samples with no concurrency, error, or partial-failure semantics
- **Evidence**: The page's three-bullet opening list, the one-paragraph section
  for `batch_completion`, and the two sibling sections. `batch_completion` gets
  a single sentence of description plus one code sample; it does not state
  whether the sub-lists run serially or concurrently, what happens to the list
  if one sub-list raises, or whether the call is one upstream HTTP request or N
  of them (its description says "in a single API call", which is about the
  *helper*, not the provider).
- **Confidence**: settled (for what the page does and does not state)
- **Quote**: "LiteLLM allows you to:" / "Send many completion calls to 1
  model" / "Send 1 completion call to many models: Return Fastest Response" /
  "Send 1 completion call to many models: Return All Responses" / "In the
  `batch_completion` method, you provide a list of `messages` where each
  sub-list of messages is passed to `litellm.completion()`, allowing you to
  process multiple prompts efficiently in a single API call."
- **Our assessment**: The heading is the hazard. An operator who greps
  `source-notes/` and `guide/` for "batching" finds the async Batch API (which
  has a real, heavily-governed submission-time limit contract) and this page
  (which has none) behind the same word. Naming is the only thing these two
  surfaces share. A platform team should treat the two words as unrelated in
  runbooks, dashboards, and capacity models.

### Claim 2: `batch_completion_models` is a race whose documented purpose is latency, not throughput — "Use this to reduce latency" — and the race is won by whoever responds first, with the losers cancelled
- **Evidence**: The section's two-sentence description plus its Output section,
  which is the only place the cancellation behavior is stated anywhere on the
  page (one line, no elaboration, no provider matrix, no caveats).
- **Confidence**: settled (documented API-contract behavior)
- **Quote**: "This makes parallel calls to the specified `models` and returns
  the first response" / "Use this to reduce latency" / "Returns the first
  response in OpenAI format. Cancels other LLM API calls."
- **Our assessment**: This is the canonical SRE hedged-request pattern
  (see Cross-References → `docs-google-sre-address-cascading-failures.md` Claim
  8) with a very different cost profile than the RPC case it comes from: the
  "server" being cancelled is a *billed* third-party API call that has already
  consumed input tokens and may already be generating output tokens. The page
  says "Cancels other LLM API calls" and stops. We read that as a client-side
  abort of the local request/stream; the page does not say whether the abort
  propagates upstream to the provider, and it certainly does not say whether
  the provider bills a cancelled call. Per the Prospector's bounding and plain
  reading, we do **not** assert that losers are free — see Claim 4.

### Claim 3: The fastest-response payload reports `model` and `usage` for the winner only — the N-1 cancelled calls leave no field, header, or array in the response body, and the same page's all-responses variant proves the contrast
- **Evidence**: The two Output sections, side by side. The fastest path returns
  a single `chat.completion` object whose `usage` reports `prompt_tokens: 6`,
  `completion_tokens: 14`, `total_tokens: 20` — matching the winner
  (`command-nightly`, one of the three raced models) exactly, with no sibling
  entries. The all-responses path on the same page returns *three*
  `ModelResponse` objects, each with its own `usage`: `claude-sonnet-5` 14/9/23,
  `command-nightly` 6/14/20, `gpt-5.6-luna` 13/39/52 — 95 total tokens across
  three calls where the race would have reported 20 for one. Same page, same
  three models, same prompt; the flag is the only difference.
- **Confidence**: settled (explicit payload shape, verified against the page's
  own worked example)
- **Quote**: `"usage": { "prompt_tokens": 6, "completion_tokens": 14,
  "total_tokens": 20 }` on the fastest path — versus the all-responses
  example's three separate `"usage"` objects (`"model": "claude-sonnet-5"`,
  `"total_tokens": 23`; `"model": "command-nightly"`, `"total_tokens": 20`;
  `"model": "gpt-5.6-luna"`, `"total_tokens": 52"`)
- **Our assessment**: This is the claim the guide should carry. The failure is
  silent and it is *asymmetric in the dangerous direction*: a request the
  operator believes cost 20 tokens may have cost 95 across three providers, and
  the response is a 200 with a complete-looking `usage` object. Any spend
  dashboard, budget alert, or per-model cost report keyed on the response
  `usage` under-reports the hedge by a factor of N. Note also that the corpus's
  nearest neighbour (`docs-litellm-anthropic-advisor-tool.md` Claim 2) at least
  exposes its hidden sub-inference at `usage.iterations[]`; here there is no
  such array — the losing calls are not merely summarized away, they are absent.
  The correct operator mitigation is the one Ch05 already states: read the
  response `model` field, do not infer from the request — extended here to
  "and do not treat response `usage` as the request's total cost when the
  request was hedged."

### Claim 4: The page documents cancellation and publishes *no* billing semantics for the cancelled calls — no statement of whether providers charge for aborted requests, no partial-usage field, no "billed: false" marker
- **Evidence**: Full read of the page. The word "cancel" appears once, in the
  one-line Output description quoted in Claim 2. There is no cost section, no
  mention of pricing, no per-model rate-limit note, and no example containing a
  usage entry for a cancelled call. The fastest-path sample output contains
  exactly one `usage` object, for the winner.
- **Confidence**: emerging (the *absence* is verified by full read; the
  operational consequence is deliberately **not** asserted — the page does not
  establish either that losers are billed or that they are free)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The honest, high-value statement is the gap itself, not
  a guess in either direction. Cancellation-after-dispatch is not
  cancellation-before-billing: three of the four providers this page's own
  example races (OpenAI, Anthropic, Cohere) bill on tokens generated, and a
  client-side abort does not necessarily reach them. So an operator turning on
  `fastest_response` to cut p99 must assume **N× provider spend for one
  client-visible request** until they have measured otherwise, and must not
  budget from the response `usage`. This is the concrete form of the hazard the
  Prospector flagged, and it is recorded here as *unestablished by the vendor*,
  not as *established by us*. A guide rule should say "measure it on your
  providers before enabling" — not "losers are charged."

### Claim 5: The hedge set is expressed inside the `model` **data field**, not as a route, alias, or config key — a comma-separated string in the request body
- **Evidence**: The proxy curl example and the OpenAI-SDK example, both
  annotated inline by the vendor with a pointing-finger comment, plus the
  `config.yaml` that maps each name to a real deployment. The proxy's own page
  states the same scheme and confirms each name resolves to a model group in
  `config.yaml`.
- **Confidence**: settled (documented request schema)
- **Quote**: `"model": "gpt-5.6-terra, groq-llama", # 👈 Comma-separated
  models` / "Just pass a comma-separated string of model names and the flag
  `fastest_response=True`." / (proxy page) "Pass model as a string of comma
  separated value of models. Example `"model"="llama3,gpt-5.6-luna"`"
- **Our assessment**: A routing decision is carried in a data field that every
  other layer also reads as an opaque model identifier. Anything keyed on the
  request `model` — per-model cost maps, per-model SLOs, allowlists, cache
  keys, dashboards, eval routing — sees the compound string
  `"gpt-5.6-terra, groq-llama"`, not two models. This is the same class of
  hazard Ch05 already records for a substituted model, except substitution is
  detectable from the response `model` field and *hedge-set membership is not
  detectable at all* from the response. The page gives the operator no
  gateway-side way to name the hedge set (a route/alias) that would keep the
  request `model` field clean.

### Claim 6: The proxy's own canonical batch-completions section never mentions `fastest_response` — it documents only the list-returning form, and marks the feature BETA
- **Evidence**: Full read of the "Advanced → (BETA) Batch Completions - pass
  multiple models" section on `https://docs.litellm.ai/docs/proxy/user_keys`,
  which the batching page's info callout sends readers to. The section's
  description, both request examples, and both response examples are entirely
  about the multi-response shape; `fastest_response` does not appear. The
  inbound link from the batching page is also broken — it points at
  `#beta-batch-completions---pass-model-as-list` while the page's actual
  heading anchor is `#beta-batch-completions---pass-multiple-models`.
- **Confidence**: settled (verified by full read of both pages)
- **Quote**: "Use this when you want to send 1 request to N Models" / "Get a
  list of responses when `model` is passed as a list" / "This same request will
  be sent to the following model groups on the [litellm proxy
  config.yaml](https://docs.litellm.ai/docs/proxy/configs)"
- **Our assessment**: The single most-documented page for proxy fan-out never
  mentions the flag that changes the response contract, while the page that
  does mention it points at a dead anchor. So the operator's authoritative
  reference for this feature is silent on it, and a reader who follows the
  callout lands on a section that describes a *different* return shape (Claim
  7). Record as documentation debt, not product behavior — the flag plainly
  works, the batching page's curl and OpenAI-SDK examples both use it.

### Claim 7: The same comma-separated `model` string yields two different JSON types depending on a flag — a **list** of `ChatCompletion` objects without `fastest_response`, a single `chat.completion` object with it
- **Evidence**: The proxy page's two "Expected Response Format" blocks
  (each a JSON array of two `ChatCompletion` objects, one per model) set against
  the batching page's Output block (one `chat.completion` object, `fastest_response`
  implied by the section). The request shape that produces them is
  materially the same — a comma-separated `model` — and differs only by the
  flag.
- **Confidence**: settled (both response shapes are worked examples on the two
  linked pages)
- **Quote**: (proxy page) "Get a list of responses when `model` is passed as a
  list" — versus (batching page) "Returns the first response in OpenAI format.
  Cancels other LLM API calls."
- **Our assessment**: A response *type* that changes with a request flag is a
  client-deserialization hazard, not just a cost one: any OpenAI-SDK-based
  caller that assumes `response.choices[0]` works against the list form and
  fails against the single form, and vice versa. Because the flag lives in
  `extra_body` (or a raw curl body) it is not visible in the typed client
  signature, so a flag flipped in one code path can break deserialization in
  another without a type error anywhere. Any migration between the two modes is
  a client-code change, not a config change — worth stating in a runbook.

### Claim 8: SDK-mode hedging puts a credential for every hedged provider in the client process; the proxy path instead resolves the same names as gateway-side model groups
- **Evidence**: The `batch_completion_models` sample sets three provider
  environment variables for three raced models; the proxy sample's
  `config.yaml` maps `model_name` aliases to real deployments and the client
  authenticates to the proxy only. The `command-nightly` model in the SDK
  example does not appear in the proxy `config.yaml` at all.
- **Confidence**: settled (both configurations shown verbatim on the page)
- **Quote**: `os.environ['ANTHROPIC_API_KEY'] = ""` /
  `os.environ['OPENAI_API_KEY'] = ""` / `os.environ['COHERE_API_KEY'] = ""` /
  (proxy page) "This same request will be sent to the following model groups
  on the [litellm proxy config.yaml]"
- **Our assessment**: The two paths have opposite trust footprints. In SDK
  mode the *client* holds N third-party credentials and the operator's hedge
  set is invisible to every gateway-side control — no virtual key, no budget,
  no per-team rate limit, no spend log. In proxy mode the client holds one
  proxy key and the hedge set is gateway configuration, so it *is* subject to
  those controls. The page presents the two as interchangeable tabs ("SDK" /
  "PROXY") with no statement that the operational exposure differs. An SRE
  reviewing a new service should ask which side the credentials and the hedge
  set live on before accepting the feature.

### Claim 9: Nothing on the page describes the concurrency mechanism, and nothing describes the rate-limit, retry, or fallback interaction of the N parallel calls
- **Evidence**: Full read of the page and of the sibling "Streaming + Async"
  page (`/docs/completion/stream`) that the sidebar pairs with it. The page
  states calls are "parallel" and no more: no `asyncio.gather` or thread-pool
  reference, no concurrency cap, no per-call retry/`num_retries` parameter, no
  statement of whether the N calls count as N requests against per-model TPM/RPM
  or as one, and no interaction with router fallbacks. The sibling page
  documents `acompletion` and async streaming but says nothing about the
  batching helpers.
- **Confidence**: settled (for the absence; the rate-limit consequence is
  explicitly not asserted)
- **Quote**: "This makes parallel calls to the specified `models` and returns
  the first response"
- **Our assessment**: Three unanswered questions a capacity owner must answer
  before enabling this, none of which the vendor addresses: (1) does the hedge
  multiply gateway-side RPM/TPM pressure by N, against the same per-minute
  windows the async Batch API already contests (see
  `docs-litellm-batches-api.md` Claims 1 and 3); (2) does the fastest-response
  flag compose with router fallbacks and `num_retries`, or replace them — i.e.
  is a hedged request also a retrying request, making worst-case fan-out N×M;
  (3) what is the client-visible error when *all* N fail. Given that the
  gateway meters and rate-limits spend as a first-class feature, "parallel" is
  the entire published contract, and a platform team should treat the
  rate-limit amplification as **unmeasured** rather than assume either way.

### Claim 10: The one streaming example on the page pairs `fastest_response: true` with `"stream": true` and says nothing about how "first response" behaves on a stream
- **Evidence**: The proxy curl example, which is the only example that sets
  `stream`, sets it alongside the flag. No section on the page discusses
  streaming behavior for either helper, and the all-responses helper's
  signature is shown with no `stream` argument at all.
- **Confidence**: emerging (the pairing is verbatim; the interaction is
  undocumented, so no behavior is claimed)
- **Quote**: `"stream": true,` / `"fastest_response": true # 👈 FLAG`
- **Our assessment**: "First response" is ambiguous under streaming, and the
  ambiguity is load-bearing: first *headers*, first *token*, or first
  *completed* response. A proxy that returns on first token will surface a
  stream that later errors, and a platform team that adopts the vendor's own
  example gets a stream whose `finish_reason` and error semantics are
  unspecified. This composes badly with the corpus's existing streaming finding
  (`docs-litellm-streaming-token-usage.md` Claim 1: a streamed completion is
  usage-blind by default unless `stream_options={"include_usage": True}`) — a
  *hedged streaming* request is doubly unaccounted, since the losers are
  missing (Claim 3) and the winner may not report usage either. Flag as a
  must-test before rollout item, not as a defect claim.

### Claim 11: The all-fail case has no documented error contract, and the fastest-response sample snippet does not run as printed
- **Evidence**: The page documents no error behavior for the fastest path
  (no exception name, no HTTP status, no partial-failure signal, no
  "returns the first *successful* response" qualifier — "first response" is
  unqualified). Separately, the `batch_completion_models` sample assigns to
  `response` and then prints `result`.
- **Confidence**: settled (for both the absence and the snippet)
- **Quote**: `response = batch_completion_models(...)` / `print(result)` /
  "This makes parallel calls to the specified `models` and returns the first
  response"
- **Our assessment**: "Returns the first response" does not say "first
  *successful* response" — if a fast 429 or 500 from one hedged model wins the
  race, the helper may hand a caller an error as a successful-looking
  response, and the N-1 healthy calls are then cancelled. The page gives no
  way to tell that case apart from a real answer. Combined with the missing
  partial-failure signal this is the reliability half of the feature's
  governance gap: a platform team should assume a hedged request can return a
  loser's error and must handle it explicitly. The `print(result)` snippet
  defect is minor but worth recording — it means the page's headline example
  was not executed as printed, which lowers (slightly) the evidentiary weight
  of the samples generally.

### Claim 12: The sample outputs are stale and internally inconsistent, and the page's outbound link to the proxy section is a dead anchor
- **Evidence**: The fastest-path output reports `"created": 1695154628.2076092`
  (a September-2023 Unix timestamp, and a *float*, where OpenAI-style responses
  carry an integer), and its assistant content is "I'm an AI assistant created
  by Anthropic to be helpful, harmless, and honest." while the same response
  reports `"model": "command-nightly"` (a Cohere model). The all-responses
  output's third entry is a bare `OpenAIObject` while the other two are
  `ModelResponse`. The info callout's link fragment does not match the target
  page's heading (Claim 6).
- **Confidence**: settled (all three are directly observable in the fetched
  page)
- **Quote**: `"created": 1695154628.2076092,` / `"content": " I'm doing well,
  thanks for asking! I'm an AI assistant created by Anthropic to be helpful,
  harmless, and honest.",` / `"model": "command-nightly",` / "Trying to do batch
  completion on LiteLLM Proxy ? Go here:
  https://docs.litellm.ai/docs/proxy/user_keys#beta-batch-completions---pass-model-as-list"
- **Our assessment**: Two lessons for the guide, both narrow. (1) Do not infer
  which model served from the model's *self-description* in the content — the
  vendor's own sample pairs an Anthropic self-identification with
  `model: "command-nightly"`; the response `model` field is the only field to
  trust, which is exactly Ch05's existing rule, now with a vendor-sample
  demonstration of why. (2) The samples are illustrative, not evidence: 2023
  timestamps and mixed response classes in the same dump mean the operator
  should not treat the example payloads as a wire-format contract, and the
  dead anchor means the documented cross-reference to the proxy surface does
  not resolve.

## Concrete Artifacts

**The three-way fan-out, as the page's own opening list states it**
("LiteLLM allows you to:"):

```
- Send many completion calls to 1 model
- Send 1 completion call to many models: Return Fastest Response
- Send 1 completion call to many models: Return All Responses
```

**`batch_completion` — N prompts to one model** (page: "Send multiple
completion calls to 1 model"):

```python
import litellm
import os
from litellm import batch_completion

os.environ['ANTHROPIC_API_KEY'] = ""

responses = batch_completion(
    model="claude-sonnet-5",
    messages = [
        [
            {
                "role": "user",
                "content": "good morning? "
            }
        ],
        [
            {
                "role": "user",
                "content": "what's the time? "
            }
        ]
    ]
)
```

**`batch_completion_models` — the race, one credential per hedged provider**
(page: "Send 1 completion call to many models: Return Fastest Response"; note
the `print(result)` on an object assigned to `response`, verbatim as printed):

```python
import litellm
import os
from litellm import batch_completion_models

os.environ['ANTHROPIC_API_KEY'] = ""
os.environ['OPENAI_API_KEY'] = ""
os.environ['COHERE_API_KEY'] = ""

response = batch_completion_models(
    models=["gpt-5.6-luna", "claude-sonnet-5", "command-nightly"],
    messages=[{"role": "user", "content": "Hey, how's it going"}]
)
print(result)
```

**The fastest-response output — winner-only `model` and `usage`** (page
"Output" section, reproduced verbatim; `Cancels other LLM API calls.` is the
section's own one-line description):

```
Returns the first response in OpenAI format. Cancels other LLM API calls.

{
  "object": "chat.completion",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": " I'm doing well, thanks for asking! I'm an AI assistant created by Anthropic to be helpful, harmless, and honest.",
        "role": "assistant",
        "logprobs": null
      }
    }
  ],
  "id": "chatcmpl-23273eed-e351-41be-a492-bafcf5cf3274",
  "created": 1695154628.2076092,
  "model": "command-nightly",
  "usage": {
    "prompt_tokens": 6,
    "completion_tokens": 14,
    "total_tokens": 20
  }
}
```

**The proxy equivalent — hedge set inside the `model` field, paired with
`stream: true`** (page, "PROXY" tab, reproduced verbatim including the vendor's
inline comments):

```
curl -X POST 'http://localhost:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H "Authorization: Bearer $LITELLM_API_KEY" \
-D '{
    "model": "gpt-5.6-terra, groq-llama", # 👈 Comma-separated models
    "messages": [
      {
        "role": "user",
        "content": "What'\''s the weather like in Boston today?"
      }
    ],
    "stream": true,
    "fastest_response": true # 👈 FLAG
}'
```

**OpenAI-SDK form of the same request** (page, "OpenAI SDK" tab, verbatim) —
the flag arrives out-of-band in `extra_body`, invisible to the typed signature:

```python
import openai

client = openai.OpenAI(
    api_key="anything",
    base_url="http://0.0.0.0:4000"
)

# request sent to model set on litellm proxy, `litellm --model`
response = client.chat.completions.create(
    model="gpt-5.6-terra, groq-llama", # 👈 Comma-separated models
    messages = [
        {
            "role": "user",
            "content": "this is a test request, write a short poem"
        }
    ],
    extra_body={"fastest_response": true} # 👈 FLAG
)
print(response)
```

**The proxy `config.yaml` the hedge names resolve against** (page, "Example
Setup:", verbatim):

```yaml
model_list:
- model_name: groq-llama
  litellm_params:
    model: groq/llama3-8b-8192
    api_key: os.environ/GROQ_API_KEY

- model_name: gpt-5.6-terra
  litellm_params:
    model: gpt-5.6-terra
    api_key: os.environ/OPENAI_API_KEY
```

```
litellm --config /path/to/config.yaml
# RUNNING on http://0.0.0.0:4000
```

**`batch_completion_models_all_responses` — the contrast case, three
`usage` objects for the same three models** (page, "Output" section, verbatim
abridged only in the `JSON:` renderings; the `model` and `total_tokens` values
are the load-bearing part and are unaltered):

```
[<ModelResponse chat.completion id=chatcmpl-e673ec8e-4e8f-4c9e-bf26-bf9fa7ee52b9 at 0x103a62160> JSON: {
  "object": "chat.completion",
  "choices": [ { "finish_reason": "stop_sequence", "index": 0, "message": {
    "content": " It's going well, thank you for asking! How about you?", ... } } ],
  "id": "chatcmpl-e673ec8e-4e8f-4c9e-bf26-bf9fa7ee52b9",
  "created": 1695222060.917964,
  "model": "claude-sonnet-5",
  "usage": { "prompt_tokens": 14, "completion_tokens": 9, "total_tokens": 23 }
}, <ModelResponse chat.completion id=chatcmpl-ab6c5bd3-b5d9-4711-9697-e28d9fb8a53c at 0x103a62b60> JSON: {
  ...
  "model": "command-nightly",
  "usage": { "prompt_tokens": 6, "completion_tokens": 14, "total_tokens": 20 }
}, <OpenAIObject chat.completion id=chatcmpl-80szFnKHzCxObW0RqCMw1hWW1Icrq at 0x102dd6430> JSON: {
  "id": "chatcmpl-80szFnKHzCxObW0RqCMw1hWW1Icrq",
  "object": "chat.completion",
  "created": 1695222061,
  "model": "gpt-5.6-luna",
  ...
  "usage": { "prompt_tokens": 13, "completion_tokens": 39, "total_tokens": 52 }
}]
```

**The proxy's own BETA section for the same comma-separated request — note
there is no `fastest_response` anywhere in it, and the response is a *list***
(from `https://docs.litellm.ai/docs/proxy/user_keys`, "Advanced → (BETA) Batch
Completions - pass multiple models", verbatim):

```python
import openai

client = openai.OpenAI(
    api_key="sk-<your-litellm-api-key>",
    base_url="http://localhost:4000"
)
response = client.chat.completions.create(
    model="gpt-5.6-luna,llama3",
    messages=[
        {"role": "user", "content": "this is a test request, write a short poem"}
    ],
)
print(response)
```

```
Get a list of responses when `model` is passed as a list

[
  {
    "id": "chatcmpl-3dbd5dd8-7c82-4ca3-bf1f-7c26f497cf2b",
    "choices": [ { "finish_reason": "length", "index": 0, "message": {
      "content": "The Elder Scrolls IV: Oblivion!\n\nReleased", ... } } ],
    "created": 1715459876,
    "model": "groq/llama3-8b-8192",
    "object": "chat.completion",
    "system_fingerprint": "fp_179b0f92c9",
    "usage": { "completion_tokens": 10, "prompt_tokens": 12, "total_tokens": 22 }
  },
  {
    "id": "chatcmpl-9NnldUfFLmVquFHSX4yAtjCw8PGei",
    "choices": [ { "finish_reason": "length", "index": 0, "message": {
      "content": "TES4 could refer to The Elder Scrolls IV:", ... } } ],
    "created": 1715459877,
    "model": "gpt-5.6-luna",
    "object": "chat.completion",
    "system_fingerprint": null,
    "usage": { "completion_tokens": 10, "prompt_tokens": 9, "total_tokens": 19 }
  }
]
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path is cited or
dismissed):

- `source-notes/docs-litellm-batches-api.md` — **cited** (Extends / naming
  hazard, Claims 1, 9). This is the note the word "batching" will collide with
  in every search. Its **Claim 1** ("Batch TPM/RPM limits are charged when the
  client calls `POST /v1/batches`, not when the input file is uploaded —
  LiteLLM downloads the referenced JSONL, evaluates the complete file against
  every applicable limit, and returns 429 before forwarding anything to the
  provider") and **Claim 3** (per-minute TPM/RPM windows fit batch work poorly,
  the whole file charged to a single minute, remedied by
  `batch_enqueued_token_limit`) describe a surface with a *thoroughly
  documented* limit contract. This page documents none (Claim 9). A reader who
  carries the `/docs/batches` governance model over to `/docs/completion/batching`
  will assume metering that does not exist. Distinct execution models
  (asynchronous provider-side jobs vs. synchronous in-process fan-out); do not
  conflate.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: a Bedrock
  native passthrough page (`/invoke`) whose claims are about SigV4→bearer auth
  swapping and a provider support matrix. No overlap with the fan-out helpers;
  its per-provider matrix has no bearing on a cross-provider race.
- `source-notes/docs-litellm-audio-transcription.md` — **dismissed**: its
  claims concern per-request `fallbacks[]` on `/v1/audio/transcriptions` and
  the `model_info: mode: audio_transcription` registration requirement. The
  closest-sounding claim (its Claim 3, fallbacks as an auto-retry with a
  different model) is about *sequential* failover on a non-chat endpoint, not
  parallel racing, and this page documents no fallback interaction at all
  (Claim 9) — so citing it would imply an answer the source does not contain.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited** (Extends /
  contrast, Claims 3, 4, 9). This is the corpus's only documented LiteLLM
  spend-cap control: its **Claim 1** (`max_iterations` hard cap on LLM calls
  per session and `max_budget_per_session` dollar cap, both keyed on
  `x-litellm-trace-id`) and **Claim 4** (spend accumulated after each successful
  call, checked before the next, so one over-budget call still reaches the
  provider). Those caps are **A2A-session-scoped**. The hedge path here is on
  `/chat/completions`, carries no cap of any kind, fans out across *providers*
  (so a per-agent session key does not apply to the N-1 siblings), and its
  N-1 cancelled calls are outside the response `usage` an operator would meter
  (Claim 3). The corpus's existing cost-control surface does not reach this
  feature; recorded as a coverage gap in our own guidance, not a vendor claim.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  an SRE podcast transcript on agent capability spectra and human-in-the-loop
  approval. No claim about gateways, fan-out, or cost attribution.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **cited**
  (Corroborates, Claim 3; the corpus's nearest neighbour). Its **Claim 2**
  ("Advisor spend is split out of the top-level `usage` object — advisor calls
  are a separate sub-inference billed at the advisor model's rates, top-level
  `usage` reflects **executor tokens only**, and advisor tokens are reachable
  only via `usage.iterations[]` entries carrying `type: "advisor_message"`") is
  the same accounting shape — one client-visible response, two billable
  sub-inferences, one `usage` object — and its **Claim 7** ("On the
  non-Anthropic orchestration path the client receives a clean response with no
  advisor blocks at all, so the advisor's contribution is not observable by the
  client") is the observability half. This page is the *worse* variant: the
  losing calls are not summarized at `usage.iterations[]`, they are absent, and
  the hedge set itself is not recoverable from the response. Three independent
  LiteLLM surfaces (advisor tool, prompt-manager substitution, hedge) now show
  the same pattern — the top-level response describes one inference, not the
  work performed.
- `source-notes/blog-litellm-auto-router-v2.md` — **cited** (Extends /
  tension, Claims 3, 5). Its **Claim 3** ("The operational rationale is
  'predictable beats clever for debuggability' — a fixed, versioned
  capability→model mapping is what makes 'why did this response cost 4x today'
  answerable after the fact") and **Claim 8** (a per-request decision log line
  with a `cause=` marker, plus tier, score/signals, and routed model) are the
  corpus's standard for *routing* decisions: one decision, one model, one
  greppable line. The hedge path has no equivalent line, and its
  `fastest_response: true` flag is not in any decision log the page names. Its
  **Claim 11** (roadmap: escalation ceilings with cooldown on fallback chains,
  quoted "a bad upstream cannot cascade into a bill") is the aspiration this
  shipped primitive inverts: the race is an *intentional* N× bill on the request
  path. Not filed as a contradiction — a roadmap item and an unrelated shipped
  feature are not opposing claims about the same thing.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: per-field
  ✅/❌ signature-stripping on A2A agent cards. Different protocol surface, no
  overlap.
- `source-notes/docs-litellm-bedrock-converse.md` — **dismissed**: a Bedrock
  native Converse passthrough, adjacent only in the sense of another
  `/bedrock/...` route. Its support-matrix claims (Cost Tracking ✅, Logging ✅)
  say nothing about `fastest_response` accounting, and the page here makes no
  matrix claims to compare.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **cited** (Extends /
  tension, Claim 4). Its **Claim 4** ("Configured agent cost lands in the
  gateway request log (Logs cost column) and is attributed to the API key that
  made the request — the chargeback axis is per-team / per-project (the caller
  pays), not attribution to the agent's own backend spend") is the corpus's
  statement of how LiteLLM chargeback works: per calling key. A hedged request
  billed from response `usage` alone (Claim 3) charges the key for one
  inference while N providers may have been paid for N — so per-key chargeback
  is exactly the axis that breaks first, and its **Claim 3** (a configured
  per-query cost is a gateway-declared synthetic figure with no documented
  linkage to measured token usage) is the mechanism an operator would reach for
  as a workaround, with its own accuracy caveat.

**Additional cross-references found by searching `source-notes/` directly**
(beyond the candidate list):

- `source-notes/docs-google-sre-address-cascading-failures.md` — **cited**
  (Corroborates / Extends, Claims 2, 4). **Claim 8** ("Cancellation propagation
  and hedged requests require propagating 'stop work' signals through the
  entire stack — for hedged requests, send to multiple servers and cancel all
  outstanding work once one responds") is the canonical SRE statement of the
  pattern `batch_completion_models` implements, and its own assessment names
  LLM gateways ("if the gateway sends a hedged request to two inference nodes
  (for latency optimization), the first response should cancel the second
  generation immediately"). What the SRE chapter does not price is what this
  page leaves unpriced: in the RPC case the cancelled work is *your own*
  capacity, so cancellation is a pure win. In the LLM case the cancelled work
  is a *third party's* metered API call, so the same pattern carries a
  provider-spend consequence the cancellation signal does not cancel. This
  note supplies the missing half of Claim 8.
- `source-notes/docs-litellm-streaming-token-usage.md` — **cited**
  (Composes, Claim 10). **Claim 1** ("A streaming completion does not report
  token usage unless the client opts in with
  `stream_options={\"include_usage\": True}` — the account of a streamed request
  is usage-blind by default") turns this page's one streaming example into a
  compounded blind spot: the losing hedged calls are absent from `usage`
  (Claim 3) *and* the winning stream may carry `usage: null` unless the caller
  opts in. A cost report built on hedged streaming traffic can be wrong by an
  unbounded factor with no field to detect it.
- `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — **cited**
  (same-class precedent, Claim 4; cited by section, not claim number, since
  this note uses the failure-report structure). Its "What Went Wrong → Symptom
  2" section ("Cost tracking silently missing for newer models only") and
  "Extracted Lessons → Lesson 3" ("Cost tracking (or any non-request-path
  function) that fails silently erodes observability") are the corpus's
  precedent for *silently wrong* cost data on a healthy 200. Here the cost data
  is not wrong because of a bug but because the request was hedged and the
  payload is winner-only by design — the same operational outcome (spend
  dashboards quietly under-reporting) with a different root cause. Its "Symptom
  3" ("The failure was invisible to request-level success metrics") is the
  reusable diagnostic: check the cost ledger against a metric the feature
  cannot affect.
- **Contradicts**: none found. Checked against the whole corpus
  (`grep -rn "cancel"` over `source-notes/` and `guide/`): no existing note or
  guide rule claims that cancelled hedged calls are free, unbilled, or
  cost-neutral, and nothing in this page opposes an existing claim. The
  advisor-tool and auto-router notes are *tensions of emphasis*, not
  disagreements of fact, and both are recorded above as such. No contradiction
  issue filed per MINER.md §4a.
- **Novel**: (1) The first documented LiteLLM primitive whose *stated purpose*
  is to replicate a request N ways rather than to select, route, or batch it —
  the corpus had selection (routers) and deferral (async Batch API) but not
  replication. (2) The **winner-only `usage` payload on a documented
  latency path** (Claim 3), the corpus's sharpest instance of a response that
  reports one inference's cost for work that cost N. (3) The hedge set
  expressed as a compound string in the `model` request field (Claim 5) — a
  routing decision carried in a data field, invisible to per-model accounting
  that keys on the request. (4) A response *type* that changes with a request
  flag (Claim 7). (5) The operational asymmetry between SDK mode and proxy mode
  for the same feature — N third-party credentials in the client versus gateway
  model groups (Claim 8).

## Guide Impact

- **Chapter 05 — "Cost, capacity, and fallback patterns"** → subsection
  *"Silent model fallback breaks attribution"*: the existing rule ("Surface the
  `model` field from the response metadata in observability dashboards — do not
  infer it from the request") **does not extend** to hedged requests as
  written, and should be amended rather than restated. Recommend adding: a
  request fanned out to N models reports `model` and `usage` for the winner
  only, so per-key and per-model cost attribution from response `usage`
  under-reports the request by up to N×; the hedge *set* is not recoverable
  from the response at all, and on the proxy it is carried as a comma-separated
  string inside the request `model` field, which additionally breaks anything
  keyed on the request `model` (cost maps, SLOs, allowlists, cache keys). This
  source is the first evidence for the hedging case; the advisor-tool note
  supplies the sub-inference case, and the prompt-management note the
  substitution case. One rule, three mechanisms, currently written for one.
  Recommend a hedged-request rule stated as a *pre-rollout measurement
  requirement*, not as a vendor claim: LiteLLM documents that losers are
  cancelled and is silent on whether providers bill them, so the guide should
  say "assume N× and measure" rather than assert either way [source:
  docs-litellm-completion-batching, Claim 4] [emerging].
- **Chapter 05** → same subsection: recommend one sentence on the
  *governance gap as a pattern*, not a LiteLLM fact — a latency-optimizing
  replication primitive with no documented rate-limit accounting, no retry/
  fallback composition statement, and no all-fail error contract is a feature to
  gate on a runbook, not to enable because the vendor documents a `curl`
  snippet. Pair it with the existing `/docs/batches` rule in
  `docs-litellm-batches-api` so the two "batching" surfaces stop sharing
  vocabulary [source: docs-litellm-completion-batching, Claims 1, 9, 11]
  [emerging].
- **Chapter 02 (secondary) — observability / cost ledger**: recommend the
  hedge be treated as a *span fan-out*, not a request, and that the ledger
  record the hedge set from the **request** (where it lives) while recording
  the winner from the **response** — the two facts come from different places
  and neither is sufficient alone. Also worth a line: do not infer the serving
  model from response *content*; this page's own sample output pairs an
  Anthropic self-identification with `"model": "command-nightly"` [source:
  docs-litellm-completion-batching, Claims 3, 5, 12] [settled].
- **Chapter 05** → capacity section: if the Smith wants a "cost you cannot
  attribute" list, this source adds a second instance with a different carrier
  (replication rather than substitution), and the streaming interaction adds a
  third compounding one — a hedged *streaming* request is unaccounted even for
  the winner unless the caller opts into `include_usage` [source:
  docs-litellm-completion-batching, Claim 10; docs-litellm-streaming-token-usage,
  Claim 1] [emerging].

## Extraction Notes

- Followed the page's one substantive outbound link — the info callout to the
  proxy's "(BETA) Batch Completions - pass multiple models" section on
  `https://docs.litellm.ai/docs/proxy/user_keys` — and read that section in
  full, because it is the operator's authoritative reference for the comma-
  separated `model` form and because it is the only other place the response
  shapes are shown. That section is quoted in Claims 6 and 7 and in Concrete
  Artifacts; claims sourced from it are labeled with the page they come from.
  Also read the paired sibling page `/docs/completion/stream` in full to look
  for a documented concurrency model for the helpers — it documents
  `acompletion`, async streaming, and the repeated-chunk guard
  (`REPEATED_STREAMING_CHUNK_LIMIT`), and says nothing about the batching
  helpers, which is the basis for Claim 9's "not documented" statement.
  Not followed: the Colab cookbook notebook for `batch_completion` (a copy of
  the page's own sample) and the adjacent `json_mode` page (unrelated).
- **Source is thin, and deliberately so.** Three code samples, one
  `config.yaml`, two output dumps, and exactly one sentence about cancellation
  — no limits table, no cost discussion, no failure modes, no benchmarks, no
  changelog entry. The value extracted is therefore the *shape of the
  governance gap*, with the gap itself stated as verified-by-full-read and
  every consequence marked `emerging`. Consistent with the Prospector's
  bounding, nothing about whether cancelled calls are billed, whether the fan-out
  multiplies rate-limit consumption, or whether the hedge composes with
  fallbacks is asserted; each appears as an unanswered question with a
  must-measure recommendation.
- **Quotes**: every `Quote` and every quoted string above was copied from the
  fetched page(s) character-for-character. The fetch pipeline collapses
  whitespace inside the page's code blocks (newlines arrive as none), so code
  in Concrete Artifacts has had its **line breaks and indentation restored**;
  no token inside a code block was added, removed, or reordered, and the two
  deliberate page defects — `print(result)` on an object assigned to
  `response` (Claim 11) and the mismatched anchor in the proxy link (Claims 6,
  12) — are reproduced as printed. Two JSON dumps are marked "abridged only in
  the `JSON:` renderings"; the abridgement replaces `choices`/`message` bodies
  with `...` and nothing else, and the `model` / `usage` values quoted in the
  claims are unaltered from the page.
- **Not a duplicate of** `source-notes/docs-litellm-batches-api.md` (issue
  #1415), per the Prospector's bounding. That note's surface is the
  asynchronous `/v1/files` + `/v1/batches` job API with submission-time
  metering; this page is synchronous in-process fan-out with no metering
  documented. Verified distinct: no claim in either note is restated by the
  other, and the shared vocabulary is the word "batching" only.
- Grepped `source-notes/` and `guide/` for `fastest_response` and
  `batch_completion` before writing: zero hits, confirming this surface is
  unturned in the corpus. Grepped for `cancel` across both trees to test for an
  existing billing claim to contradict — none found, so no contradiction issue
  was filed (MINER.md §4a).
