---
source_url: https://docs.litellm.ai/docs/extras/creating_adapters
source_type: docs
title: "Call any LiteLLM model in your custom format | liteLLM (Custom Formats / Adapters)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-14)
date_extracted: 2026-10-14
last_checked: 2026-10-14
status: current
confidence_overall: emerging
issue: "#1705"
---

# Call any LiteLLM model in your custom format (LiteLLM Custom Adapters)

> LiteLLM's `CustomFormatter`/adapter API lets an operator register a
> process-global translation layer (`litellm.adapters = [{"id": ..., "adapter": ...}]`)
> that rewrites an arbitrary client request shape into OpenAI format before
> `.completion()` runs, and rewrites the `ModelResponse` back afterwards — it is a
> **format-translation** extension, not a new provider integration. The only
> ops-facing content is (a) the process-global registration, (b) a 3-method
> contract on a `CustomLogger` subclass whose streaming method returns a wrapper
> object, and (c) a single `general_settings.pass_through_endpoints` proxy wiring
> that maps a path to a Python module class. The page carries no error handling,
> retries, fallbacks, timeouts, rate limits, logging, cost tracking, or
> deployment guidance, and its snippets are illustrative rather than
> copy-paste-ready.

## Source Context

- **Type**: docs (official vendor documentation — single living Docusaurus page
  at `/docs/extras/creating_adapters`, verified HTTP 200 this session and
  matching `source_url`). Nav position per the page's own breadcrumb:
  AI Gateway → Create Custom Plugins → **Custom Formats (Adapters)**, sitting
  beside `call_hooks`, `agentic_loop_hook`, `rules`, and `worker_startup_hooks`
  as a "Create Custom Plugins" sibling.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented* surface of a shipped feature — the
  method names, the import paths, the registration list shape, the entry-point
  names, and the proxy config keys. It is **not** evidence of measured behavior:
  the page carries no metrics, no version range, no changelog entry, no tests,
  and no failure report, and it is undated. The three "Real Example" links point
  at the upstream implementation files but the page does not quote or explain
  them.
- **Scope**: How to author and register a custom bidirectional adapter so a
  proprietary request/response shape can be served by any LiteLLM-supported
  `.completion()` model: the `CustomLogger` base class, the three translation
  methods, the SDK registration, the sync/async/streaming entry points, a worked
  Anthropic example, and a `pass_through_endpoints` proxy wiring. Does **not**
  cover: any reliability or operational surface (error handling, retries,
  fallbacks, timeouts, rate limits, logging, cost tracking, deployment),
  versioning/compatibility, or how the proxy behaves when the adapter fails.
  The Prospector's secondary framing is confirmed below: this is a
  *format-translation* layer around OpenAI-format internals, not a way to add a
  new provider backend.
- **Prospector triage**: three triage comments were filed on #1705. Two score it
  `medium` (novelty medium / docs / Ch05 gateway extensibility; the code-heavy
  tutorial with a reproducible config) and one scores it `low` (the page is a
  developer-extension how-to outside the seed's "routing, rate limits, spend,
  fallbacks, production deploy" scope). This note follows the shared instruction
  across all three: **extract only the ops-facing facts (registration shape,
  method contract, proxy wiring, upstream provenance) and do not pad**; mark the
  rest as developer-facing extension API with no ops claim. The "low" triage's
  two specific questions (is `pass_through_endpoints` a real gateway knob worth
  Ch05; is `CustomLogger` shared with the observability callback path) are
  answered in Claims 2, 8, and 9.

## Extracted Claims

### Claim 1: Adapters are a bidirectional **format-translation** layer around LiteLLM's OpenAI-format internals — the request is translated into OpenAI format, processed by any supported model, then translated back; it is not a new provider integration
- **Evidence**: The "How it works" section's one-line pipeline diagram and the
  page intro. The `translate_completion_input_params` docstring says "Convert
  your format → OpenAI format" and `translate_completion_output_params` says
  "Convert OpenAI format → your format".
- **Confidence**: settled (the page's own framing of its mechanism)
- **Quote**: "Your request → Adapter translates to OpenAI format → LiteLLM processes it → Adapter translates response back → Your response"
- **Our assessment**: This is the framing the note must preserve so it is not
  confused with provider-add work (per the Prospector's explicit instruction).
  The adapter never reaches a new backend: it sits on both sides of the
  existing OpenAI-format pipeline that `.completion()` already speaks. The
  operational consequence is that an adapter adds two Python translation hops
  to every request and every chunk of a stream, in the same process as the
  gateway — which is why the *silence* of the page on errors/latency matters
  (Claim 10). The corpus already records a built-in instance of this exact
  shape: the `/v1/messages`→Responses translation is implemented as a set of
  adapters in the same source tree (Claim 9).

### Claim 2: The adapter base class is `litellm.integrations.custom_logger.CustomLogger` — the **same** class used for logging/observability callbacks — but adapter registration uses a distinct module-level list (`litellm.adapters`) keyed by `id`, separate from the `litellm.callbacks` registry
- **Evidence**: The adapter snippet's import
  (`from litellm.integrations.custom_logger import CustomLogger`) and the
  registration snippet (`litellm.adapters = [{"id": "my_provider", "adapter": my_adapter}]`).
  The corpus confirms `CustomLogger` is the observability callback base
  (`docs-litellm-caching-all-caches.md` Claim 6 uses a `CustomLogger` success
  callback to read `kwarg["cache_hit"]`; `blog-litellm-swap-openai-code-interpreter.md`
  registers handlers via the separate `litellm.callbacks = [...]` list).
- **Confidence**: settled for the import path and the `litellm.adapters` list
  shape; emerging for the "same class, different registry" reading (the page
  names the class and the list; it does not discuss the relationship to
  `litellm.callbacks`)
- **Quote**: "Inherit from `CustomLogger` and implement 3 methods:" / "litellm.adapters = [{\"id\": \"my_provider\", \"adapter\": my_adapter}]"
- **Our assessment**: This answers the "low" triage's second question, and the
  answer is a caution rather than a reassurance: the *base class* is shared
  with the observability callback path, but the *registry* is not. An operator
  who greps for `CustomLogger` and assumes adapters and logging callbacks are
  configured the same way will look in the wrong list. The guide's Ch02
  callback material should record that `litellm.adapters` is a second,
  id-keyed registry that happens to reuse the same base class — do not
  conflate the two. No existing corpus note records `litellm.adapters`.

### Claim 3: Adapter registration is process-global mutable state — `litellm.adapters = [...]` is a module-level assignment, not a per-request or per-route setting, so it is not part of the model-cost-map reload path and an adapter swap implies a process restart
- **Evidence**: The registration snippet is a bare module-level assignment
  (`litellm.adapters = [{"id": ..., "adapter": ...}]`), mirroring the
  module-scoped assignment pattern the corpus documents as restart-scoped for
  the HTTP handler (`docs-litellm-completion-http-handler-config.md` Claim 2).
  The page has no reload, hot-swap, or per-route registration variant.
- **Confidence**: emerging (the *global assignment* is directly readable from
  the snippet; the "swap requires a restart rather than a reload, unlike the
  cost-map path" consequence is the Miner's inference from the assignment
  shape, not a statement the page makes)
- **Quote**: "litellm.adapters = [{\"id\": \"my_provider\", \"adapter\": my_adapter}]"
- **Our assessment**: The sharpest ops-facing point on the page, and it must be
  labeled as **inference**, not vendor statement. Contrast the guide's
  cost-map rule (`guide/05-llm-ops-reliability.md:271-284`, "Enablement via
  cost-map reload, not deploy"): model enablement is documented as live
  reload. Adapter registration is a Python assignment in the gateway process,
  so the analysis method is the same one Ch05 already prescribes — "know
  whether the enablement path is live reload or image upgrade"
  (`guide/05-llm-ops-reliability.md:282-284`) — and here the answer falls on
  the **restart** side, not the reload side. This is the kind of change that
  the Ch05 "Reload success ≠ model reachability" rule
  (`guide/05-llm-ops-reliability.md:286-302`) cannot cover, because there is no
  reload to observe. Verification of the exact reload semantics would require
  the upstream implementation file (not reachable from this runner), so this
  is recorded `emerging`.

### Claim 4: The adapter contract is a three-method trio with fixed signatures and types — `translate_completion_input_params(self, kwargs) -> ChatCompletionRequest`, `translate_completion_output_params(self, response: ModelResponse)`, and `translate_completion_output_params_streaming(self, completion_stream)`; the streaming method returns a **wrapper object**, not a transformed response
- **Evidence**: The "Create an Adapter" snippet's three method definitions and
  their type annotations (`ChatCompletionRequest`, `ModelResponse` imports),
  and the streaming return in that same snippet (`return MyStreamWrapper(completion_stream)`).
- **Confidence**: settled (explicit, typed method signatures)
- **Quote**: "def translate_completion_input_params(self, kwargs) -> ChatCompletionRequest:" / "def translate_completion_output_params(self, response: ModelResponse):" / "def translate_completion_output_params_streaming(self, completion_stream):" / "return MyStreamWrapper(completion_stream)"
- **Our assessment**: The streaming method is the one with operational weight:
  the non-streaming adapter returns a serializable response object, but the
  streaming adapter returns an *iterator-like wrapper* that decides chunk
  emission — so streaming correctness lives entirely in user code
  (Claims 7 and 11). Note the page's own streaming method is later redefined
  with a *different signature* in the Anthropic example (Claim 11): the
  contract above takes `completion_stream`, the worked example takes
  `(stream, model)`. That inconsistency is real and is flagged rather than
  presented as a working interface.

### Claim 5: Invocation is via dedicated entry points named `adapter_completion` / `aadapter_completion`, keyed by `adapter_id=`, kept separate from `litellm.completion` / `litellm.acompletion`
- **Evidence**: The "Use it" / "Async" snippets import and call
  `adapter_completion` and `aadapter_completion` with an `adapter_id="my_provider"`
  argument and a normal `model=` argument.
- **Confidence**: settled (explicit call signatures and import paths)
- **Quote**: "from litellm import adapter_completion" / "response = adapter_completion(" / "adapter_id=\"my_provider\","
- **Our assessment**: The `adapter_id` indirection is what ties the call to the
  global `litellm.adapters` list (Claim 3): the id string in the call must
  match an entry registered in that list, and the page documents no error
  behavior for a missing/mismatched id — the failure mode of a typo'd
  `adapter_id` is simply not specified here, consistent with the page's
  general silence on error handling (Claim 10). A client has to know to call
  `adapter_completion` (not `completion`) to reach the adapter; the proxy path
  in Claim 8 is the only place this is abstracted away behind a URL.

### Claim 6: The worked Anthropic example does the minimal bidirectional mapping — on input it moves the top-level `system` kwarg into a `system` message inserted at index 0 when present; on output it maps usage `prompt_tokens`→`input_tokens` and `completion_tokens`→`output_tokens`
- **Evidence**: The "Example: Anthropic Adapter" section's input-translation
  snippet (the `if "system" in kwargs:` block with
  `openai_messages.insert(0, {...})`) and its output-translation snippet
  (`usage={...}`).
- **Confidence**: settled for the documented example; anecdotal as a model of
  "correct" Anthropic translation (the page presents it as illustrative, and
  the full adapter lives in the linked upstream files)
- **Quote**: "if \"system\" in kwargs:" / "openai_messages.insert(0, {" / "\"input_tokens\": response.usage.prompt_tokens," / "\"output_tokens\": response.usage.completion_tokens"
- **Our assessment**: The example only handles the `user` role in the input
  loop and only inserts one system block; it is a teaching sketch, not a
  complete Anthropic mapping. Do not treat it as the reference for
  `/v1/messages` semantics — the corpus already documents the real, shipped
  translation in `docs-litellm-messages-to-responses-mapping.md` (a completely
  different and far more detailed mapping). The value here is the *pattern*
  (hoist top-level scalars into messages; rename usage fields), not the
  correctness of the Anthropic mapping itself.

### Claim 7: The streaming worked example emits Anthropic SSE event types in a fixed order via an `AdapterCompletionStreamWrapper` subclass — `message_start` first (guarded by a `first_chunk` flag), then `content_block_delta`, then `message_stop`
- **Evidence**: The "Streaming" section of the Anthropic example: a class
  `AnthropicStreamWrapper(AdapterCompletionStreamWrapper)` with `self.first_chunk = True`
  and an `__anext__` that returns `{"type": "message_start", ...}` on the first
  call, then `{"type": "content_block_delta", ...}`, then `{"type": "message_stop"}`.
- **Confidence**: emerging (the event order and the `first_chunk` guard are
  explicitly written; but the snippet's control flow is broken — see Claim 11 —
  so the *intended* sequence is clear while the *runnable* code is not)
- **Quote**: "class AnthropicStreamWrapper(AdapterCompletionStreamWrapper):" / "self.first_chunk = True" / "return {\"type\": \"message_start\", \"message\": {...}}" / "return {\"type\": \"content_block_delta\"," / "return {\"type\": \"message_stop\"}"
- **Our assessment**: The wrapper is where streaming reliability lives, and the
  page shows exactly the surface the guide's pass-through rule cares about:
  whether an adapter-driven route streams or buffers is decided by *this*
  user-supplied iterator, not by the gateway. The page does not state this
  connection, but it follows from Claim 1's pipeline plus Claim 8's
  `pass_through_endpoints` wiring. It also re-opens the Ch05 pass-through
  memory question (Cross-References → `blog-litellm-july-stability-update`).

### Claim 8: The only proxy wiring documented is `general_settings.pass_through_endpoints` mapping a path to a Python module class — `path: "/v1/messages"` / `target: "my_module.MyAdapter"` — exercised with a `Bearer` token against the proxy; the page states no caveats about auth or path handling
- **Evidence**: The "Use with Proxy" YAML block under `general_settings` and
  the follow-up curl using `Authorization: Bearer $LITELLM_API_KEY`.
- **Confidence**: settled for the config shape (explicit keys); emerging for
  any operational consequence (the page states none)
- **Quote**: "general_settings:" / "pass_through_endpoints:" / "- path: \"/v1/messages\"" / "target: \"my_module.MyAdapter\"" / "curl http://localhost:4000/v1/messages" / "-H \"Authorization: Bearer $LITELLM_API_KEY\""
- **Our assessment**: This is the one production-deploy-facing snippet on the
  page and the hook back to the guide's existing pass-through material
  (`guide/05-llm-ops-reliability.md:1124-1146`). Two things worth flagging
  precisely. (1) **Registry-vs-config mismatch**: the proxy `target` names a
  *class* (`my_module.MyAdapter`), while the SDK example registers an *instance*
  with an `id` (Claims 2-3). The page never reconciles how a `target` class
  relates to the `litellm.adapters` list or how the proxy instantiates/keys
  it. (2) **Auth surface**: the route is served with a normal LiteLLM `Bearer`
  virtual key, and the page gives no pass-through-specific auth guidance —
  which matters because the corpus has a dedicated "knob honored on one
  dispatch path and inert on a sibling" pattern
  (`docs-litellm-completion-http-handler-config.md` Claim 1) and a
  route-resolution auth-bypass incident
  (`failure-litellm-host-header-auth-bypass.md`). Whether `pass_through_endpoints`
  routes go through the standard auth dependency is **not documented here** and
  must not be assumed; recorded as an open question (Guide Impact, Ch06).

### Claim 9: The page names the real upstream Anthropic adapter files it is abstracting — `transformation.py`, `handler.py`, `streaming_iterator.py` under `litellm/llms/anthropic/experimental_pass_through/adapters/` — placing user-authored adapters in the same source tree as the built-in `responses_adapters/` translation
- **Evidence**: The "Real Example" link list and the corpus's
  `docs-litellm-messages-to-responses-mapping.md`, whose Source Context names
  the sibling directory
  `litellm/llms/anthropic/experimental_pass_through/responses_adapters/transformation.py`.
- **Confidence**: settled for the link targets (verbatim paths); emerging for
  the "same tree, sibling mechanism" synthesis
- **Quote**: "[transformation.py](https://github.com/BerriAI/litellm/blob/main/litellm/llms/anthropic/experimental_pass_through/adapters/transformation.py)" / "[handler.py](" / "[streaming\_iterator.py]("
- **Our assessment**: Provenance is the page's strongest claim and the one the
  corpus can act on: it tells the reader that the *documented adapter authoring
  API* and the *built-in `/v1/messages` translation* are not two unrelated
  features but the same mechanism at two levels. The corpus already has the
  built-in side (`docs-litellm-messages-to-responses-mapping.md`); this note
  supplies the authoring side, and the cross-link (Cross-References → Extends)
  is the reason to keep the note despite its thin ops content.

### Claim 10: The page documents **no** reliability or operational surface — no error handling, retries, fallbacks, timeouts, rate limits, logging, cost tracking, or deployment guidance — so it is a developer-extension tutorial, not gateway-ops documentation
- **Evidence**: Absence across all sections ("How it works", "Create an
  Adapter", "Register it", "Use it", "Example: Anthropic Adapter", "Use with
  Proxy", "Real Example", "That's it"). The page's own closing summary is four
  implementation steps with no operational step.
- **Confidence**: settled (an absence, directly verifiable on the page)
- **Quote**: (no direct quote; see Our assessment)
- **Our assessment**: This bounds the note's reliability value and is exactly
  what the "medium" triage asked to be recorded. An adapter sits in the hot
  path of every request (Claim 1) and its streaming behavior is user code
  (Claim 7), yet the page says nothing about what happens when that code
  raises, times out, or emits a malformed chunk. The guide must not present
  this page as evidence for any reliability property; it can only support the
  *shape* of the registration/config surface.

### Claim 11: The snippets are illustrative, not copy-paste-ready — the class-body indentation is inconsistent and the streaming example mixes a synchronous translation method with an `async def __anext__`, redeclaring the streaming-method signature with an extra `model` parameter
- **Evidence**: Direct reading of the fetched code blocks. In the first block
  the three methods are dedented to the same level as the class statement
  rather than nested; in the Anthropic streaming block `async def __anext__(self):`
  sits at 8-space indent (nested inside `__init__`) while the base contract's
  streaming method (Claim 4) took `completion_stream` and this example's
  `translate_completion_output_params_streaming` takes `(self, stream, model)`.
- **Confidence**: settled (directly observable in the page's own code)
- **Quote**: "async def __anext__(self):" / "def translate_completion_output_params_streaming(self, stream, model):"
- **Our assessment**: We do **not** present these as verified working code. The
  value is the *shape* of the contract (three methods, wrapper-returning
  streaming); the indentation and the signature drift mean an operator cannot
  lift the snippet as-is. This matches the Prospector's explicit instruction
  ("Treat the snippets as illustrative … Flag that rather than presenting them
  as verified working code"). Contrast the corpus's convention of quoting
  runnable config verbatim — here the note must label every code artifact as a
  documentation sketch.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(`https://docs.litellm.ai/docs/extras/creating_adapters`, markdown render),
unless noted. **Code blocks are documentation sketches — see Claim 11; do not
treat them as working code.** The first team block's line breaks were collapsed
by the markdown renderer (see Extraction Notes); they are re-flowed here for
readability only.

**How it works (verbatim pipeline line)**

```
Your request → Adapter translates to OpenAI format → LiteLLM processes it → Adapter translates response back → Your response
```

**Create an Adapter (verbatim; newlines re-flowed, see Extraction Notes)**

```python
from litellm.integrations.custom_logger import CustomLogger
from litellm.types.llms.openai import ChatCompletionRequest
from litellm.types.utils import ModelResponse

class MyAdapter(CustomLogger):
    def translate_completion_input_params(self, kwargs) -> ChatCompletionRequest:
        """Convert your format → OpenAI format"""
        # Example: Anthropic to OpenAI
        return {
            "model": kwargs["model"],
            "messages": self._convert_messages(kwargs["messages"]),
            "max_tokens": kwargs.get("max_tokens"),
        }

    def translate_completion_output_params(self, response: ModelResponse):
        """Convert OpenAI format → your format"""
        # Return your provider's response format
        return MyProviderResponse(
            id=response.id,
            content=response.choices[0].message.content,
            usage=response.usage,
        )

    def translate_completion_output_params_streaming(self, completion_stream):
        """Handle streaming responses"""
        return MyStreamWrapper(completion_stream)
```

**Register it (verbatim)**

```python
import litellm

my_adapter = MyAdapter()
litellm.adapters = [{"id": "my_provider", "adapter": my_adapter}]
```

**Use it / Streaming / Async (verbatim)**

```python
from litellm import adapter_completion

# Now you can use your provider's format with any LiteLLM model
response = adapter_completion(
    adapter_id="my_provider",
    model="gpt-5.6-terra",  # or any LiteLLM model
    messages=[{"role": "user", "content": "hello"}],
    max_tokens=100
)
```

```python
stream = adapter_completion(
    adapter_id="my_provider",
    model="gpt-5.6-terra",
    messages=[{"role": "user", "content": "hello"}],
    stream=True
)

for chunk in stream:
    print(chunk)
```

```python
from litellm import aadapter_completion

response = await aadapter_completion(
    adapter_id="my_provider",
    model="gpt-5.6-terra",
    messages=[{"role": "user", "content": "hello"}]
)
```

**Anthropic example — input translation (verbatim)**

```python
def translate_completion_input_params(self, kwargs):
    model = kwargs.pop("model")
    messages = kwargs.pop("messages")

    # Convert Anthropic messages to OpenAI format
    openai_messages = []
    for msg in messages:
        if msg["role"] == "user":
            openai_messages.append({
                "role": "user",
                "content": msg["content"]
            })

    # Handle system message
    if "system" in kwargs:
        openai_messages.insert(0, {
            "role": "system",
            "content": kwargs.pop("system")
        })

    return {
        "model": model,
        "messages": openai_messages,
        **kwargs  # pass through other params
    }
```

**Anthropic example — output translation (verbatim)**

```python
def translate_completion_output_params(self, response):
    return AnthropicResponse(
        id=response.id,
        type="message",
        role="assistant",
        content=[{
            "type": "text",
            "text": response.choices[0].message.content
        }],
        usage={
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens
        }
    )
```

**Anthropic example — streaming wrapper (verbatim; note the indentation and
signature issues flagged in Claim 11)**

```python
from litellm.types.utils import AdapterCompletionStreamWrapper

class AnthropicStreamWrapper(AdapterCompletionStreamWrapper):
    def __init__(self, completion_stream, model):
        super().__init__(completion_stream)
        self.model = model
        self.first_chunk = True

        async def __anext__(self):
            # First chunk
            if self.first_chunk:
                self.first_chunk = False
                return {"type": "message_start", "message": {...}}

            # Stream chunks
            async for chunk in self.completion_stream:
                return {
                    "type": "content_block_delta",
                    "delta": {"text": chunk.choices[0].delta.content}
                }

            # Last chunk
            return {"type": "message_stop"}

def translate_completion_output_params_streaming(self, stream, model):
    return AnthropicStreamWrapper(stream, model)
```

**Use with Proxy (verbatim)**

```yaml
general_settings:
  pass_through_endpoints:
    - path: "/v1/messages"
      target: "my_module.MyAdapter"
```

```bash
curl http://localhost:4000/v1/messages \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -d '{"model": "gpt-5.6-terra", "messages": [...]}'
```

**Real Example links (verbatim targets)**

```
transformation.py   → https://github.com/BerriAI/litellm/blob/main/litellm/llms/anthropic/experimental_pass_through/adapters/transformation.py
handler.py          → https://github.com/BerriAI/litellm/blob/main/litellm/llms/anthropic/experimental_pass_through/adapters/handler.py
streaming_iterator.py → https://github.com/BerriAI/litellm/blob/main/litellm/llms/anthropic/experimental_pass_through/adapters/streaming_iterator.py
```

**"That's it" summary (verbatim)**

```
1. Create a class that inherits `CustomLogger`
2. Implement the 3 translation methods
3. Register with `litellm.adapters = [{"id": "...", "adapter": ...}]`
4. Call with `adapter_completion(adapter_id="...")`
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path cited or
dismissed; the lexical retrieval is dominated by shared LiteLLM/proxy
vocabulary and returns no adapter-authoring match):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch
  TPM/RPM accounting and enqueued-token reservations; rate-limit arithmetic,
  no adapter/translation content.
- `source-notes/docs-litellm-completion-web-search.md` — **Dismissed**: the
  provider-native web-search tool surface; no request/response adapter layer.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: the Bedrock
  native Invoke passthrough is a *fixed* route family that swaps SigV4 for a
  bearer token; it is a different route mechanism from the user-authored
  `pass_through_endpoints` target here (Claim 8). The one adjacency is the word
  "passthrough," which is a route, not a translation layer.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  `mode: audio_transcription` routing and per-request fallbacks; no adapter
  content.
- `source-notes/docs-litellm-completion-input-params.md` — **Dismissed**: the
  supported-params gate and OpenRouter param handling; like all LiteLLM
  params, it is a *different* default on the OpenAI-format path this adapter
  feeds into, but the note contains no adapter material.
- `source-notes/docs-litellm-completion-web-fetch.md` — **Dismissed**:
  Anthropic `web_fetch_20250910` server tool; no adapter content.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session iteration/budget caps keyed on `x-litellm-trace-id`; "session"
  there is an agent conversation, not a translation layer.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Dismissed**: the
  advisor tool's within-request model composition; no adapter registration or
  translation method.
- `source-notes/blog-litellm-auto-router-v2.md` — **Dismissed**: complexity/
  semantic/adaptive routing strategy selection; routing chooses a model, an
  adapter rewrites the request/response *shape* (Claim 1). No shared subject
  matter.
- `source-notes/docs-litellm-exception-mapping.md` — **Dismissed**: the
  provider-error→exception→HTTP-status taxonomy. It is *relevant to the
  omission* in Claim 10 (LiteLLM has a documented error taxonomy; this page
  says nothing about which errors an adapter can surface), but it contains no
  adapter content to cite. Noted here rather than cited.

**Primary cross-references** (found by searching `source-notes/` and `guide/`
myself; every `Claim N` verified by re-reading the cited note, per MINER §4b):

- **Corroborates / Extends**:
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — **the
    note's most important cross-reference**. That note documents the
    *built-in, shipped* `/v1/messages`→Responses translation implemented under
    `litellm/llms/anthropic/experimental_pass_through/responses_adapters/`
    (its Source Context names
    `responses_adapters/transformation.py`; its Claim 1 documents the silent
    drops on that path). This page supplies the *user-authored authoring API*
    in the sibling `.../adapters/` directory (Claim 9 here). Together they
    establish that the corpus now has both levels of the same mechanism.
    **No contradiction**: that note is about a specific translation's
    semantics; this is about how an operator writes their own.
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 1** — "`/v1/messages`
    is a unified Anthropic-messages-format endpoint across all LiteLLM-supported
    providers" (`docs-litellm-anthropic-unified.md:67`). The page here is the
    authoring-side counterpart to that shipped endpoint; its Claim 6/8
    (Anthropic request/response shape on the unified route) is the *target
    format* an adapter author is trying to reproduce. Cross-link so the two
    notes are read together; no conflict.
  - `source-notes/docs-litellm-completion-http-handler-config.md` **Claim 2** —
    "Setting `litellm.base_llm_aiohttp_handler` creates a new attribute on the
    `litellm` package that nothing reads, and the custom session is silently
    ignored" (`docs-litellm-completion-http-handler-config.md:99-101`). That
    note's module-scoped-assignment and no-read-back lessons are the same class
    as Claim 3 here (`litellm.adapters` is a module-level assignment) and its
    Extraction Notes' "configured from Python process code, not `config.yaml`"
    scope limit applies to adapter registration too. The difference worth
    recording: the HTTP handler's wrong *attribute name* silently no-ops,
    whereas the adapter's registration list here is a documented name — the
    open question instead is whether the proxy's `target` class (Claim 8) reads
    that same list.
  - `source-notes/docs-litellm-caching-all-caches.md` **Claim 6** — the
    `CustomLogger` success callback used to read `kwarg["cache_hit"]`
    (`docs-litellm-caching-all-caches.md:58`) is the *same base class* the
    adapter inherits (Claim 2 here). Corroborates "CustomLogger is the
    observability callback base" while distinguishing the registries
    (`litellm.callbacks` vs `litellm.adapters`).
- **Contradicts**: **None found; no contradiction issue filed.** Reasoning in
  Extraction Notes. The one apparent tension — `docs-litellm-provider-specific-params.md`
  **Claim 6** documents a proxy example using an `adapter_base` litellm_param
  and a request field `"adapater_id"` (`docs-litellm-provider-specific-params.md:78-79`),
  which *looks* like the same "adapter" concept — is a **terminology
  collision, not opposition**: provider-specific params are arbitrary
  kwargs passed to the provider, and the page there uses the word "adapter" for
  a base-URL-style provider param. Neither note claims the other's mechanism is
  invalid, and both can be true. Recorded in Guide Impact so the Smith does not
  merge the two "adapter" meanings.
- **Extends / thematically adjacent** (guide thread):
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 4** — "Large
    non-JSON pass-through downloads (batch-result files, binary/octet-stream)
    were previously buffered whole in memory before being forwarded; the fix
    streams responses chunk-by-chunk" (`blog-litellm-july-stability-update.md:89`).
    The guide's pass-through rule built on that claim
    (`guide/05-llm-ops-reliability.md:1124-1146`) is the section the
    `pass_through_endpoints` adapter wiring (Claim 8) plugs into. **Open
    question this source raises**: whether an adapter-driven
    `pass_through_endpoints` route streams by default or buffers, and whether
    the adapter's `translate_completion_output_params_streaming` wrapper
    (Claim 7) is what determines it — the page does not say. Flag for Ch05,
    do not assert.
  - `source-notes/docs-litellm-gateway-auth-reference.md` — the corpus's auth
    reference; its Claim 1 records an auth dependency that is honored on one
    dispatch path and inert on a sibling (`/mcp` vs `/mcp-rest`). Whether
    `pass_through_endpoints` routes (Claim 8) go through the standard auth
    dependency is not documented by this page, and that note does not cover
    them. Cite as the *reason* the Ch06 open question exists, not as
    corroboration.
- **Novel**: First corpus coverage of the **custom adapter authoring API** —
  grep-verified zero prior matches in `source-notes/` for
  `creating_adapters`, `AdapterCompletionStreamWrapper`,
  `translate_completion_input_params`, `translate_completion_output_params`,
  `adapter_completion`, or `litellm.adapters`. Specifically new: the
  `CustomLogger`-subclass + 3-method contract (Claim 4); the process-global
  `litellm.adapters` registration list (Claim 3); the `adapter_completion`/
  `aadapter_completion` entry points (Claim 5); and the
  `general_settings.pass_through_endpoints` → Python-module proxy wiring
  (Claim 8). The upstream file provenance (Claim 9) links the note into the
  existing `experimental_pass_through/` thread.

## Guide Impact

- **Chapter 05 (§"Bound pass-through memory; skip work nobody consumes",
  `guide/05-llm-ops-reliability.md:1124-1146`)**: The existing rule — "pick the
  stream/buffer split by whether anything downstream reads the body" — assumes
  the gateway controls buffering. This source adds a pass-through route whose
  body handling is delegated to **user-supplied Python**
  (`pass_through_endpoints` → `target` adapter, Claim 8; the streaming wrapper,
  Claim 7). Recommend adding one sentence: for adapter-backed
  `pass_through_endpoints` routes, the stream/buffer decision is not purely a
  gateway config — it is the adapter's `translate_completion_output_params_streaming`
  return value — and the page documents **no** guarantee that a
  non-streaming adapter on a large body will not materialize it. Mark the
  streaming/buffering behavior as **undocumented here** (open question); do not
  cite this page as evidence either way. [Claim 8] [settled for the config
  keys; emerging for the consequence].
- **Chapter 05 (§"Enablement via cost-map reload, not deploy" /
  §"Reload success ≠ model reachability", `guide/05-llm-ops-reliability.md:266-302`)**:
  Add a second enablement path next to the cost-map reload: **process-global
  registration**. `litellm.adapters = [...]` is a Python module assignment
  (Claim 3), so — per the section's own "know whether the enablement path is
  live reload vs image upgrade" rule (`:282-284`) — an adapter change falls on
  the **restart** side, not the reload side, and the "reload success ≠
  reachability" verification (`:286-302`) has no reload to observe. Flag as
  **inference** (`emerging`), not a vendor statement; the page does not
  discuss reload semantics at all. [Claim 3].
- **Chapter 02 (Observability)**: Record the registry distinction so the two
  `CustomLogger` uses are not conflated: the adapter base class is the same
  `litellm.integrations.custom_logger.CustomLogger` used for logging callbacks
  (cf. `docs-litellm-caching-all-caches.md` Claim 6), but adapters register in
  the id-keyed `litellm.adapters` list, **not** `litellm.callbacks`
  (Claim 2). Do **not** cite this page for observability capability — it ships
  no logging/hook surface (Claim 10). [Claim 2] [settled for the shape].
- **Chapter 06 (Security and Trust)**: Add one open question, stated as a
  question and not a finding: `pass_through_endpoints` routes are documented
  only as a path→module mapping exercised with a `Bearer` virtual key
  (Claim 8); the page does **not** state whether they pass through the standard
  auth dependency or how client-supplied credentials are handled on the route.
  Given the corpus's existing "honored on one dispatch path, inert on a
  sibling" auth pattern (`docs-litellm-gateway-auth-reference.md` Claim 1) and
  its host-header route-resolution auth-bypass incident
  (`failure-litellm-host-header-auth-bypass.md`), operators wiring a custom
  pass-through route should verify auth coverage explicitly rather than assume
  it. Do not record a vulnerability — the source reports none. [Claim 8]
  [emerging].
- **Chapter 05 / cross-note disambiguation**: Note for the Smith — the word
  "adapter" in `docs-litellm-provider-specific-params.md` Claim 6
  (`adapter_base`, `adapater_id`) is a **provider-specific param base**, not
  this page's translation adapter (Cross-References → Contradicts). Keep the
  two meanings separate in any synthesized text.

## Extraction Notes

- Source read in full via WebFetch as markdown on the canonical URL
  (`https://docs.litellm.ai/docs/extras/creating_adapters`, HTTP 200, no
  paywall). The page is short (~a dozen prose lines plus code); there is no
  deeper body to read, and the Prospector's "do not pad" instruction is
  followed — the note is deliberately narrow. No sub-pages were followed
  (MINER §1 allows up to 5): the only outbound links are nav siblings
  (`worker_startup_hooks`, `memory`, the Enterprise footer) and the three
  upstream GitHub implementation files. The GitHub files were **not** fetched
  — this runner cannot be assumed to have network access to github.com, and the
  page does not quote them, so their contents are out of scope; they are cited
  only as provenance (Claim 9). The Prospector's instruction to "not re-extract
  the adapter-authoring tutorial end to end" is honored: the note captures the
  contract and the ops-facing facts, and treats the example bodies as
  illustrative artifacts, not as an extraction target.
- **Markdown-renderer artifact**: WebFetch's markdown render collapsed the
  newlines inside the first Python code block ("Create an Adapter"), running the
  imports, class body, and methods onto one line. The Concrete Artifacts
  reproduction re-flows those newlines for readability; the method signatures,
  identifiers, and strings are transcribed character-for-character from the
  rendered text. The Anthropic-example blocks rendered with newlines intact and
  are transcribed as-is (including the indentation/signature inconsistencies
  recorded in Claim 11). All `Quote` fields are contiguous fragments from the
  fetched page text; no quote is spliced across non-adjacent sentences. The
  arrow pipeline line (Claim 1) is quoted as a single contiguous line.
- **Cross-reference verification (MINER §4b)**: `miner-related-notes.md` was
  read before writing Cross-References; all ten candidate paths are cited or
  dismissed above. Every `Claim N` cited was re-read in its source note before
  being written: `docs-litellm-messages-to-responses-mapping.md` Source Context
  (the `responses_adapters/transformation.py` path; not a numbered claim, cited
  by section/name), `docs-litellm-anthropic-unified.md` Claim 1,
  `docs-litellm-completion-http-handler-config.md` Claim 2,
  `docs-litellm-caching-all-caches.md` Claim 6,
  `docs-litellm-provider-specific-params.md` Claim 6,
  `blog-litellm-july-stability-update.md` Claim 4, and
  `docs-litellm-gateway-auth-reference.md` Claim 1. The directly quoted
  passages from other notes were copied from those files, not reconstructed.
  No claim numbers invented; non-numbered material is cited by section name.
- **Contradiction decision (no issue filed, per MINER §4a "when NOT to
  file")**: the only apparent conflict is the "adapter" terminology collision
  with `docs-litellm-provider-specific-params.md` Claim 6, which is a shared
  word for two unrelated mechanisms, not two opposing claims about one
  mechanism. Per §4a's "claims differ only in context / one side is not a real
  claim," no contradiction issue was filed. Checked the open
  `contradiction`-labeled issues and `CONTRADICTIONS.md`: none covers custom
  adapters, `litellm.adapters`, or `pass_through_endpoints`.
- `confidence_overall` set to **`emerging`**, matching the sibling LiteLLM docs
  notes (`docs-litellm-messages-to-responses-mapping.md`,
  `docs-litellm-provider-specific-params.md`,
  `docs-litellm-completion-http-handler-config.md`): the API-surface claims
  (method names, import paths, registration list, entry points, proxy config
  keys) are `settled` as statements about *documented product behavior*, but
  the note's guide value is in inferences the page does not state (restart vs
  reload, streaming/buffering consequence, auth coverage), all marked
  `emerging` and several flagged as open questions. No measured behavior, no
  independent validation, no version range, no deployment experience.
- `date_published` unknown (undated living vendor docs page); `date_extracted`
  and `last_checked` both 2026-10-14 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain.
