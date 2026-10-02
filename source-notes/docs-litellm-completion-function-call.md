---
source_url: https://docs.litellm.ai/docs/completion/function_call
source_type: docs
title: "Function Calling | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-10-02)
date_extracted: 2026-10-02
last_checked: 2026-10-02
status: current
confidence_overall: settled
issue: "#1481"
---

# Function Calling (LiteLLM Docs)

> The only LiteLLM page that documents *tool-calling capability discovery* and
> *non-native tool calling* — and reading it against the shipped release shows
> both features are weaker than the page implies: `supports_function_calling()`
> is a fail-closed lookup into a remote, reloadable cost map (with a live
> `POST /api/show` template-substring probe behind it for Ollama, and the
> page's own example assertions failing against that map), and
> `add_function_to_prompt = True` — the documented "general fallback for
> providers without function calling support" — is read only inside a branch
> gated on `custom_llm_provider == "ollama"`, so it is inert for every other
> provider (filed as contradiction **#1550**). What LiteLLM actually does when
> it does inject a schema is *worse* for Ch06 than the page suggests: the raw
> Python dict is interpolated un-delimited and un-escaped into the caller's
> own system message, mutating the caller's message list in place, with
> nothing on the response side and nothing parsing the model's reply back
> into `tool_calls`.

## Source Context

- **Type**: docs
- **Author credibility**: First-party LiteLLM SDK reference. Authoritative for
  *what the vendor says the software does*; it is a capability description, not
  a report of observed production behavior. There are no metrics, no latency or
  cost figures, no failure writeup, no version pinning, and no deprecation
  date. The page is undated. Current as of 2026-10-02.
- **Scope**: Covers the LiteLLM `completion()` tool-calling surface for models
  that *do* support it: two capability predicates, a parallel-tool-call
  walkthrough (OpenAI + Azure OpenAI), the deprecated `functions=` path,
  `litellm.utils.function_to_dict`, and the `add_function_to_prompt` fallback
  for providers without native support. Does **not** cover: the gateway/proxy
  request path (`/v1/chat/completions` routing, budgets, guardrails), response
  parsing of tool calls on the fallback path, the injected prompt's token
  cost, or any measured behavior.
- **Independent verification performed by the Miner**: every claim about
  LiteLLM's actual behavior was checked against the shipped implementation at
  tag **v1.103.2** (latest release, published 2026-10-01; retrieved
  2026-10-02) — `litellm/utils.py`, `litellm/main.py`,
  `litellm/litellm_core_utils/prompt_templates/factory.py`,
  `litellm/proxy/proxy_server.py`,
  `litellm/proxy/guardrails/guardrail_hooks/lakera_ai.py`,
  `litellm/llms/ollama/common_utils.py`, and the shipped
  `model_prices_and_context_window.json` (4320 model keys). Results are in
  "Implementation Verification" below. The page cites no version, so doc/code
  skew is possible and is flagged per claim rather than resolved.
- **Prose/code mismatch precedent in this corpus**: this page is the fourth
  LiteLLM page in a row where the documentation and the release disagree
  (#1514, `docs-litellm-completion-input-params.md` Claim 5,
  `docs-litellm-anthropic-advisor-tool.md` Claim 12). Treat the page's code
  blocks as illustrative.

## Extracted Claims

### Claim 1: The two capability predicates are independent lookups over two separate keys on the same model record — the page presents them as a matched pair, but nothing guarantees both keys are declared for a model
- **Evidence**: Both page sections are identical in form, one sentence plus a
  bare `assert` block, differing only in the helper name and the boolean
  literal. Code side: `supports_parallel_function_calling()` and
  `supports_function_calling()` are two one-line wrappers over
  `_supports_factory(..., key="supports_parallel_function_calling")` and
  `key="supports_function_calling"`. Each key is read independently, so a
  model entry may carry one and not the other — and in the shipped cost map
  `gpt-4` carries `supports_function_calling: true` with no
  `supports_parallel_function_calling` key at all.
- **Confidence**: settled
- **Quote**: "Use `litellm.supports_function_calling(model="")` -> returns `True` if model supports Function calling, `False` if not" / "Use `litellm.supports_parallel_function_calling(model="")` -> returns `True` if model supports parallel function calling, `False` if not"
- **Our assessment**: Buy it, and it matters more than it looks. The page
  reads as "check one thing, and there's a second stricter check". In the
  implementation they are two unrelated facts about a model, and the strict
  one is the one more likely to be missing from the map. An operator who
  builds a routing tier on `supports_function_calling()` and assumes
  parallel support follows is reading a guarantee the page never made and the
  data does not provide. The honest form of the advice is two independent
  gates, each fail-closed (Claim 2).

### Claim 2: The predicates are fail-closed: they return `True` only when some source declares `True`; an unknown model, a missing key, or *any* exception all resolve to `False`
- **Evidence**: `_supports_factory()` has exactly one affirmative exit —
  `if model_info.get(key, False) is True: return True` — followed by a
  bare-model-name fallback, then `_supports_provider_info_factory()` (which
  can return `True` or `None`, never `False`), then `return False`. The
  function body is wrapped in `try/except`, and the `except` branch also ends
  in `return False` after a `verbose_logger.debug` line.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment — the page
  states the two-valued return but says nothing about how unknown models are
  treated)
- **Our assessment**: This is the single most important fact for the
  question the Prospector asked, and the answer is *no — this is an inventory
  of **declared** capability, not of actual capability.* Every uncertain
  input collapses to the safe-looking `False`, so the failure mode of a
  capability gate built on it is silent under-admission, not over-admission.
  Verified end to end: the page's own `assert litellm.supports_function_calling(model="ollama/llama2") == False`
  passes not because Ollama lacks tool support (modern Ollama templates do
  support tools) but because the `ollama/llama2` entry in the shipped cost map
  simply omits the key. A team routing away from tool-capable models on this
  predicate gets no error, no log at default level, and no way to distinguish
  "declared unsupported" from "never declared".

### Claim 3: The capability matrix is *data*, not code — it is LiteLLM's model cost map, fetched from a URL overridable by environment variable and reloaded via the documented cost-map reload endpoint
- **Evidence**: `_get_model_info_helper()` resolves the model against
  `litellm.model_cost` via a six-step specificity ladder
  (`provider/model` → bare `model` → `split_model` →
  `combined_stripped_model_name` → `stripped_model_name` →
  `provider_prefixed_model_name`). `litellm/__init__.py` initializes
  `model_cost` from `LITELLM_MODEL_COST_MAP_URL`, defaulting to the raw
  GitHub URL of `model_prices_and_context_window.json` on `main`.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment — the page
  never mentions where the answer comes from)
- **Our assessment**: The page presents the predicates as a stable model
  property. They are not: they are a field in a **remote JSON artifact
  served from `main`**, refreshable by `POST /reload/model_cost_map`. So a
  capability answer can change under a running gateway with no deploy and no
  config edit, and `guide/05-llm-ops-reliability.md` §"Enablement via
  cost-map reload, not deploy" already documents that reload path *and* its
  failure mode (a reload that reports success while leaving derived
  in-memory state stale). That is the connection: the same artifact drives
  both pricing and routing eligibility, so a cost-map refresh is also a
  capability-change event, and the corpus's existing incident
  (`failure-litellm-wildcard-model-access-desync`) is the precedent for
  "reload log line is not evidence". Audit questions for the guide: what is
  my `LITELLM_MODEL_COST_MAP_URL` pinned to, and what is my policy for
  re-validating tool-capability answers after each refresh.

### Claim 4: Provider-supplied model info **outranks** the static cost map, and for Ollama that means the capability answer is a live HTTP call plus a substring test on the model's chat template
- **Evidence**: In `_get_model_info_helper()`, the provider config's
  `get_model_info()` is called *before* the `litellm.model_cost` ladder and
  its result returned immediately (`if provider_model_info is not None: return
  provider_model_info`); only on exception does it log a warning and fall
  through to the map. Ollama's `get_model_info()` calls
  `get_runtime_model_info()`, which does
  `module_level_client.post(url=f"{api_base}/api/show", json={"name": model})`
  and derives the flag with a substring test on the returned template. This
  only happens for models *not* already baked into the map —
  `get_model_info()` returns `None` early for `self._is_static_ollama_model(model)`.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: So `supports_function_calling()` is not one mechanism
  but three, in precedence order: (1) a live provider probe where the
  provider offers one, (2) the remote cost map, (3) the bare-model-name
  fallback. Three consequences an operator cannot see from the page. (a) A
  function whose signature reads like a pure predicate can make a **blocking
  network call** to an Ollama server inside a routing loop. (b) The Ollama
  answer is a text heuristic — `"tools" in template.lower()` — so a template
  that names tools in prose reports `True` and one that wires tool support
  under another variable name reports `False`. (c) On probe failure Ollama
  returns a dict with **no** capability key at all, which feeds straight into
  the fail-closed `False` of Claim 2 — an unreachable Ollama server looks
  exactly like a model that does not support tools. Never call this in a
  hot routing path; read the cost map once at config time and cache it.

### Claim 5: The injection mechanism is a synthesized optional parameter, `functions_unsupported_model`, not the flag — and `tool_choice` is silently discarded on the path where it applies
- **Evidence**: `pre_process_optional_params()` pops `tools` (or `functions`)
  out of `non_default_params` and re-attaches it under the non-standard key
  `functions_unsupported_model`; `main.py` pops that key and calls
  `function_call_prompt()`. Separately, in the `tools` branch only,
  `tool_choice` is dropped with an inline rationale.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Worth knowing because it explains why the page says
  nothing about the injected text: the page documents the flag, and the flag
  is not what does the work. `functions_unsupported_model` is a private key
  that appears at only six sites in the whole v1.103.2 tree — three producer
  assignments in `pre_process_optional_params()` (two in the Ollama branch,
  one in the unreachable `elif`), one consumer in `main.py`, and one assertion
  in `tests/test_litellm/llms/ollama/test_ollama_chat_transformation.py:371`.
  The `tool_choice` drop is its own small finding and the page's
  examples are built on it — both the OpenAI and Azure examples pass
  `tool_choice="auto"`, and on the only provider where the fallback runs
  that parameter is thrown away, so the documented "auto is default, but
  we'll be explicit" intent never reaches the provider. Same operational
  shape as `docs-litellm-completion-input-params.md` Claim 1 (a
  hard-coded exemption/omission list outside the normal support matrix):
  one parameter takes a different path for one provider and the docs do not
  say so.

### Claim 6: On the Ollama path the flag is not a switch — the library **writes** the global as a side effect of handling a request, process-globally, and never resets it
- **Evidence**: `litellm/__init__.py:414` defines the default `False`. The
  Ollama branch of `pre_process_optional_params()` executes
  `litellm.add_function_to_prompt = True` as an assignment on every such
  request. Repo-wide search over v1.103.2 finds no `= False` assignment
  anywhere outside the default declaration, and the proxy's only writer is
  `if add_function_to_prompt is True:` — a one-way latch with no `else`.
- **Confidence**: settled
- **Quote**: "# IMPORTANT - Set this to TRUE to add the function to the prompt for Non OpenAI LLMs"
- **Our assessment**: This is the concrete form of the Prospector's "is
  that flag safe under a multi-tenant gateway" question, and the answer is
  worse than "global, not per-request". Setting it was never required for
  Ollama: **one Ollama request sets it for the whole process**, and it stays
  set. In a gateway serving many tenants, tenant A's request mutates a
  module global that tenant B's request path and the guardrail hooks read
  (Claim 8). Note also the *direction* of the page's advice is misleading
  for Ollama users: the flag is already on there, so turning it "on" is a
  no-op and the operator learns nothing about whether their configuration
  took effect. There is no per-request form of this flag in v1.103.2 —
  passing `add_function_to_prompt=` on a `completion()` call is not read
  here and lands in `**kwargs` as an unknown body field.

### Claim 7: The injected block is un-delimited and un-escaped: the raw Python dict is f-string-interpolated into the system message behind one fixed preamble, and it is appended to *every* message whose role contains the substring `"system"`
- **Evidence**: `function_call_prompt()` in
  `litellm/litellm_core_utils/prompt_templates/factory.py` builds one string
  from a literal preamble plus `f"""\n{function}\n"""` per function — a Python
  `str()` of the dict, so single-quoted, Python-formatted — then loops over
  the messages with `if "system" in message["role"]:` and appends.
- **Confidence**: settled
- **Quote**: "For Models/providers without function calling support, LiteLLM allows you to add the function to the prompt set: `litellm.add_function_to_prompt = True`"
- **Our assessment**: This answers the Prospector's second question directly:
  the page does not say how the injected block is delimited or escaped, and
  the answer is *it isn't*. There is no JSON serialization, no fenced code
  block, no XML-ish tag, no length or nonce delimiter. The preamble is the
  only separator, and it is followed immediately by a Python dict repr
  while instructing the model to "Produce JSON OUTPUT ONLY". Two concrete
  properties an operator should care about. (1) `{"type": "string", "enum":
  "['celsius', 'fahrenheit']"}` (see Claim 11) reaches the model with
  Python quoting inside a prompt that demands JSON, and a tool
  `description` is attacker- or author-controlled free text sitting in the
  same undelimited region — so the trust boundary for tool schemas and the
  trust boundary for model-visible content are the *same channel*, with
  nothing between them. That is the Ch06 framing: not prompt injection in
  the classic sense, but the absence of any structural separation between
  your authorization surface and your prompt surface. (2) The role test is a
  **substring** match, not `== "system"`, and it appends to *all* matching
  messages rather than the first — so a request with two system messages
  gets the whole schema twice, doubling the injected token cost for no
  reason.

### Claim 8: The injection mutates the caller's own message dicts and list in place — the opposite contract from LiteLLM's own message sanitization
- **Evidence**: `function_call_prompt()` writes with
  `message["content"] += f""" {function_prompt}"""` (or `.append(...)` on
  list-style content) directly on the passed-in dicts, and when no system
  message exists it calls `messages.append({"role": "system", ...})` on the
  caller's list, then returns that same list.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Contrast this with `docs-litellm-message-sanitization.md`
  Claim 10, where the vendor explicitly reassures callers that
  "sanitization creates a new list of messages. Your original messages
  remain unchanged." Two gateway transforms on the same request array, two
  opposite contracts, and only one of them is documented as mutating. The
  operational consequence is a class of bug that is hard to see: a caller
  that retries, logs, hashes, or caches its message array after a failed or
  retried call finds the tool schema already spliced into its own history,
  and will splice it again on the next attempt — so the schema count in the
  transcript grows with each retry while `prompt_tokens` grows with it. Any
  golden-transcript test or prompt-cache key computed from the caller's
  array is now wrong. This is a `*_unsupported_model`-path-only hazard, but
  it is the path the page tells you to use.

### Claim 9: Nothing parses the model's reply back into `tool_calls` — the caller receives free text and must parse it itself
- **Evidence**: Repo-wide search: `function_call_prompt` has exactly two
  references outside its own definition — the import at `main.py:184` and the
  single call at `main.py:5514`. No code anywhere reads
  `functions_unsupported_model` on the response path, and the injected
  preamble is the only specification of the reply format.
- **Confidence**: settled
- **Quote**: "Produce JSON OUTPUT ONLY! Adhere to this format {"name": "function_name", "arguments":{"argument_name": "argument_value"}} The following functions are available to you:"
  (verbatim from `function_call_prompt()` in the shipped release; **not**
  present on the page — the page never shows the injected text at all)
- **Our assessment**: The page never says this, and the omission is the
  operational trap. Because `tools`/`functions` is popped out of the
  outbound params (Claim 5), the provider never sees a tool definition, so
  the response has no `tool_calls` array and `finish_reason` will not be
  `tool_calls` — it will be ordinary text completion. A caller written
  against the OpenAI contract (`response.choices[0].message.tool_calls`,
  exactly as the page's own examples do) gets `None`/absent and must
  re-implement JSON extraction from `content`, including the page's own
  warning about validity: "# Note: the JSON response may not always be valid;
  be sure to handle errors". Two guide-relevant consequences: the fallback
  path is *strictly harder* to evaluate than the native path (an eval that
  asserts on `tool_calls` silently measures nothing), and it does not show
  up in any tool-call metric or cost attribution derived from `tool_calls`
  usage.

### Claim 10: The same global flag changes what a guardrail sends — the Lakera hook omits the flattened tool-call arguments from its system-role payload when the flag is set
- **Evidence**: `litellm/proxy/guardrails/guardrail_hooks/lakera_ai.py:186`
  reads the same module global and gates the flattening of tool-call
  `arguments` into the system message it submits for scanning. An in-code
  comment states the reasoning ("they are in system already").
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the finding that makes the flag a **Ch06**
  subject rather than a Ch05 one, and it is entirely undocumented. The
  premise — "the function schemas are already in the system message, so the
  guardrail need not see them separately" — is only true for the Ollama path
  where injection actually happens (Claim 6, and contradiction **#1550**).
  Everywhere else the flag is inert for injection but *still* live for the
  guardrail: setting it disables the Lakera hook's inclusion of tool-call
  arguments in the scanned payload. Combined with Claim 6's one-way latch —
  a single Ollama request can flip it process-wide — a gateway can silently
  change what its prompt-injection scanner inspects without any config edit,
  any log line at default level, and any deployment restart. Pair with
  `guide/06-security-and-trust.md` §"A guardrail gate reads a signal — it
  does not run a guardrail" and §"A guardrail is an egress boundary —
  configure what crosses it": the thing to configure here is not the
  guardrail's threshold but *which content reaches it at all*. Also note the
  hook keys off the raw module global rather than the request, so the
  scanned content is a function of gateway-wide mutable state rather than of
  the request under inspection.

### Claim 11: `function_to_dict`'s documented output is a live defect, not a rendering artifact — `enum` is emitted as a **string** containing a Python list repr, and its member order is not deterministic
- **Evidence**: The page prints the output of `function_to_dict()` verbatim,
  including `'enum': "['fahrenheit', 'celsius']"`. The shipped
  implementation at `litellm/utils.py` produces exactly that:
  `param_enum = str(list(literal_eval(param_type)))` — `str()` of a Python
  list — and the docstring branch that reaches it is keyed on the numpydoc
  type field containing `{`. The **next** property filter keeps only
  `isinstance(v, str)` values, so the malformed `enum` is precisely the
  value that survives. The `str(list(...))` originates from
  `literal_eval` of a docstring **set** literal (`unit : {'celsius',
  'fahrenheit'}`), whose iteration order is hash-seed dependent.
- **Confidence**: settled for the type defect; emerging for the ordering
  consequence (reasoned from CPython semantics, not measured here)
- **Quote**: `'unit': {'type': 'string', 'description': 'Temperature unit', 'enum': "['fahrenheit', 'celsius']"}`
- **Our assessment**: The page is telling the truth, which is what makes it
  valuable — an operator copying that output into their own schema builder
  will emit `"enum": "['fahrenheit', 'celsius']"`, a string where the JSON
  Schema (and OpenAI's tool schema) requires an array. Strict validators
  reject it; permissive ones ignore the constraint, so the model is free to
  return a unit outside the set the developer believed it was restricted to.
  That is a correctness bug in a security-adjacent field — enum constraints
  are how you keep a tool argument inside an allowed set. The ordering half
  is a smaller, distinct problem: because the enum members come from a Python
  set, the emitted schema text can differ between processes, which perturbs
  prompt-cache keys and makes byte-exact golden-prompt comparisons flaky
  across worker restarts. Practical advice for the guide: hand-write tool
  schemas for anything with an enum; use `function_to_dict` only for
  docstring-only functions with no constrained parameters.

### Claim 12: `function_to_dict` also silently drops any parameter it cannot type as a string, and infers `required` from the Python signature rather than from the docstring
- **Evidence**: The page's documented output shows `'required':
  ['location', 'unit']` for a function whose `unit` parameter has no default.
  In the implementation, `required_params` is built from
  `param.default == param.empty`, and each property dict is filtered to
  `isinstance(v, str)` — so a parameter with no annotation *and* no docstring
  entry (type `None`, description `None`, enum `None`) is removed from
  `properties` entirely rather than defaulting to `{"type": "string"}`.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment — the page
  shows the output but does not describe the derivation rules)
- **Our assessment**: Included because it changes what the helper is safe
  for. `required` comes from the *signature*, not the docstring, so marking
  a parameter required in the docstring's `Parameters` section does nothing
  and a parameter with a Python default is never required even if the
  docstring says it must be. Combined with the drop-if-not-a-string filter,
  the helper silently produces a *different* schema than the function it
  describes whenever a parameter is unannotated — no error, no warning. Same
  family as the corpus's established pattern of silent gateway-side
  narrowing (`docs-litellm-drop-params.md` Claim 9: no observable signal for
  a drop).

### Claim 13: The deprecated `functions=` path is labeled deprecated with no removal date, no replacement statement, and no documented behavior when `functions` and `tools` are passed together
- **Evidence**: A single section heading marks the path deprecated; the body
  is one code block and one sentence of prose. The page contains no
  deprecation timeline, no version, and no statement of what LiteLLM does if
  both parameters are supplied.
- **Confidence**: settled
- **Quote**: "Deprecated - Function Calling with `completion(functions=functions)`"
- **Our assessment**: For a corpus whose whole Ch05 premise is "audit
  parameters before routing production traffic", this is a gap worth naming
  rather than a finding worth resolving. Two specifics the page leaves open
  that the code does not answer cleanly: the ordering between `tools` and
  `functions` is *observable in the implementation* — on the Ollama path the
  `tools` branch is taken first and also discards `tool_choice`, so passing
  `tools` wins and passing both is not an error — and the deprecated
  `function_call=` parameter is never popped by the fallback path at all, so
  on the injection path it rides along as an unknown field. The
  `guide/05-llm-ops-reliability.md` §"Parameter migration hazards" rule is
  directly applicable and the page supplies the raw material: a deprecated
  parameter with no removal date is a parameter that will be in someone's
  request body on the day it stops working.

### Claim 14: The page's own section headings, code blocks, and example assertions are mutually inconsistent — the "gpt-3.5-turbo-1106" quick start calls `gpt-5.6-luna`, and the capability assertions do not hold against the shipped cost map
- **Evidence**: Read directly off the page: the section heading is "Quick
  Start - gpt-3.5-turbo-1106" and its explanation repeats "Parallel
  function calling with `gpt-3.5-turbo-1106`", while every model string in
  every block on the page is `gpt-5.6-luna` (and the Azure block pins
  `AZURE_API_VERSION = "2023-07-01-preview"` with
  `model="azure/chatgpt-functioncalling"`). Separately, running the page's
  five capability assertions against v1.103.2's shipped
  `model_prices_and_context_window.json`: `gpt-5.6-luna` ✓ (`true`),
  `azure/gpt-5.6-terra` ✓ (`true`), `palm/chat-bison` ✓ (`false` — but the
  map entry *omits* the key rather than declaring `false`, and `palm` is a
  retired provider), `ollama/llama2` ✓ (`false`, same omission),
  **`xai/grok-2-latest` ✗ (`False`)** — the key is absent from all 4320 map
  entries and the `xai` provider config declares no capability, so
  `_supports_factory` reaches `return False`. And
  `assert litellm.supports_parallel_function_calling(model="gpt-4") == False`
  is `False` for the same omission reason, not by declaration.
- **Confidence**: settled
- **Quote**: "Quick Start - gpt-3.5-turbo-1106" / "Below is an explanation of what is happening in the code snippet above for Parallel function calling with `gpt-3.5-turbo-1106`"
- **Our assessment**: Two lessons, and the guide should carry both. (1)
  **Never copy an assertion from vendor docs as a capability fixture.** One
  of the page's five asserts evaluates `False` today, and it fails *closed*,
  so it will fail silently in whatever script adopts it rather than raising.
  A page's example code is not a test. (2) The heading/model-string drift is
  the same pattern #1514 and
  `docs-litellm-anthropic-advisor-tool.md` Claim 12 recorded. Taken
  together — four LiteLLM pages in a row where prose, model IDs, and code
  blocks disagree with the release — the corpus now has enough evidence for
  a standing editorial rule: **LiteLLM documentation code blocks are
  illustrative, not transcribed**, and the shipped source plus the shipped
  cost map are the behavior of record. Recommend the Smith state that rule
  once, in Ch05, rather than re-deriving it per note.

### Claim 15: On the fallback path the entire tool schema is re-sent on every request as system-message text — the page gives no token accounting for it
- **Evidence**: `function_call_prompt()` appends the preamble plus every
  function repr to the system message that is sent with each request; there
  is no caching, no `cache_control` handling, and no conditional on request
  content anywhere in the function. The page documents nothing about token
  cost, caching, or spend.
- **Confidence**: emerging — reasoned from the code path and the standard
  prompt-caching semantics; **not measured**, and no figure appears anywhere
  on the page
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Flagged as inference, not evidence, per the corpus's
  treatment of unmeasured cost claims. Two consequences worth stating
  qualitatively: the injected block is inside the system message, so it is
  part of the cached prefix on providers that support prompt caching — which
  is good for cost but means **any change to a tool description busts the
  cache for every conversation using that tool**, a real footgun for agent
  loops that mutate descriptions at runtime; and when no system message
  exists, LiteLLM *creates* one, which changes the prompt's role structure
  for providers where that matters (compare
  `docs-litellm-message-sanitization.md` Claim 7: same Claude model,
  different treatment by transport). An operator who needs a number should
  measure `prompt_tokens` with and without `tools` on one request rather
  than trust any estimate.

## Concrete Artifacts

### The page's two capability sections, as rendered

Page source: https://docs.litellm.ai/docs/completion/function_call,
"Checking if a model supports function calling" and "…parallel function
calling". Newlines in the page's code blocks are published collapsed (a
pattern already recorded in `docs-litellm-completion-output.md` Claim 9),
so the asserts read as one run-on line:

```
assert litellm.supports_function_calling(model="gpt-5.6-luna") == Trueassert litellm.supports_function_calling(model="azure/gpt-5.6-terra") == Trueassert litellm.supports_function_calling(model="palm/chat-bison") == Falseassert litellm.supports_function_calling(model="xai/grok-2-latest") == Trueassert litellm.supports_function_calling(model="ollama/llama2") == False
```

```
assert litellm.supports_parallel_function_calling(model="gpt-5.6-terra") == Trueassert litellm.supports_parallel_function_calling(model="gpt-4") == False
```

Verdict against v1.103.2's shipped cost map (Claim 14):

```
gpt-5.6-luna:      present   supports_function_calling=True   supports_parallel_function_calling=True    litellm_provider=openai
azure/gpt-5.6-terra: present supports_function_calling=True   supports_parallel_function_calling=True    litellm_provider=azure
gpt-4:             present   supports_function_calling=True   supports_parallel_function_calling=<KEY ABSENT>  litellm_provider=openai
ollama/llama2:     present   supports_function_calling=<KEY ABSENT>  supports_parallel_function_calling=<KEY ABSENT>  litellm_provider=ollama
palm/chat-bison:   present   supports_function_calling=<KEY ABSENT>  supports_parallel_function_calling=<KEY ABSENT>  litellm_provider=palm
xai/grok-2-latest: ABSENT FROM MAP (4320 keys checked)         provider config declares no capability      -> predicate returns False
claude-2:          ABSENT FROM MAP                             -> the page's own add_function_to_prompt example model
```

### `function_to_dict` output as the page prints it (page, "Output from function_to_dict")

```
{    'name': 'get_current_weather',     'description': 'Get the current weather in a given location',     'parameters': {        'type': 'object',         'properties': {            'location': {'type': 'string', 'description': 'The city and state, e.g. San Francisco, CA'},             'unit': {'type': 'string', 'description': 'Temperature unit', 'enum': "['fahrenheit', 'celsius']"}        },         'required': ['location', 'unit']    }}
```

Note `'enum'` is a quoted string holding a Python list repr — reproduced
here as printed. See Claim 11.

### The `add_function_to_prompt` usage block (page, "Usage")

```
import os, litellmfrom litellm import completion# IMPORTANT - Set this to TRUE to add the function to the prompt for Non OpenAI LLMslitellm.add_function_to_prompt = True # set add_function_to_prompt for Non OpenAI LLMsos.environ['ANTHROPIC_API_KEY'] = ""messages = [    {"role": "user", "content": "What is the weather like in Boston?"}]
```

The example that cannot work as documented: `claude-2` is
`custom_llm_provider == "anthropic"`, and the flag is read only inside an
`== "ollama"` branch (Claim 6, contradiction **#1550**).

### The page's response expectation (page, "Expected output", first block)

```
ModelResponse(  id='chatcmpl-8MHBKZ9t6bXuhBvUMzoKsfmmlv7xq',   choices=[    Choices(finish_reason='tool_calls',     index=0,     message=Message(content=None, role='assistant',       tool_calls=[
```

Consistent with `docs-litellm-completion-output.md` Claim 4's
five-value `finish_reason` normalization — but only on the *native* path.
On the `add_function_to_prompt` path there is no `tool_calls` and no
`finish_reason='tool_calls'` at all (Claim 9).

### Implementation Verification (Miner, not the page)

Source: `litellm` at tag **v1.103.2** (latest release, published 2026-10-01;
retrieved 2026-10-02), file tarball, plus the shipped
`model_prices_and_context_window.json` from the same tag. The page is undated
and cites no version, so every check below is a point-in-time read of the
release, not a claim about what any given version shipped.

**Where the flag is read, and where it is not (Claim 6, contradiction #1550).**
`litellm/utils.py:4223` `pre_process_optional_params()` — the whole block,
including the flag's only read site, sits behind `custom_llm_provider ==
"ollama"`:

```python
    ## raise exception if function calling passed in for a provider that doesn't support it
    if "functions" in non_default_params or "function_call" in non_default_params or "tools" in non_default_params:
        if (
            custom_llm_provider == "ollama"
            and custom_llm_provider != "text-completion-openai"
            ...
        ):
            if custom_llm_provider == "ollama":
                # ollama actually supports json output
                optional_params["format"] = "json"
                litellm.add_function_to_prompt = True  # so that main.py adds the function call to the prompt
                if "tools" in non_default_params:
                    optional_params["functions_unsupported_model"] = non_default_params.pop("tools")
                    non_default_params.pop("tool_choice", None)  # causes ollama requests to hang
                elif "functions" in non_default_params:
                    optional_params["functions_unsupported_model"] = non_default_params.pop("functions")
            elif litellm.add_function_to_prompt:  # if user opts to add it to prompt instead
                optional_params["functions_unsupported_model"] = non_default_params.pop(
                    "tools", non_default_params.pop("functions", None)
                )
            else:
                raise UnsupportedParamsError(
                    status_code=500,
                    message=f"Function calling is not supported by {custom_llm_provider}.",
                )
```

The `elif` is unreachable, and so is the `raise`. The provider exclusion is a
chain of `!=` comparisons nested under the `==` conjunct — the author appears
to have meant those comparisons to *be* the filter. Note the inline
comment still claims `main.py` does the injection; `main.py` only pops a
key.

Repo-wide search over the v1.103.2 tree for `add_function_to_prompt`
(definition, forced assignment, one read in `utils.py`, two consumers, one
guardrail hook, no `= False` anywhere outside the default):

```
./litellm/__init__.py:414                            add_function_to_prompt: bool = (False  # if function calling not supported by api, append function call details to system prompt)
./litellm/utils.py:4282                                  litellm.add_function_to_prompt = True  # so that main.py adds the function call to the prompt
./litellm/utils.py:4288                              elif litellm.add_function_to_prompt:  # if user opts to add it to prompt instead
./litellm/main.py:5510                               if litellm.add_function_to_prompt and optional_params.get(
./litellm/proxy/guardrails/guardrail_hooks/lakera_ai.py:186    if not litellm.add_function_to_prompt:
./litellm/proxy/proxy_server.py:8652                   add_function_to_prompt=True,          # initialize() signature default
./litellm/proxy/proxy_server.py:8765-8767              if add_function_to_prompt is True: ... litellm.add_function_to_prompt = True / dynamic_config["general"]["add_function_to_prompt"] = True
./litellm/proxy/proxy_cli.py:743                       "--add_function_to_prompt",  is_flag=True,  help="If function passed but unsupported, pass it as prompt",
```

**The injection itself (Claims 7, 8, 9).**
`litellm/litellm_core_utils/prompt_templates/factory.py:5168`:

```python
def function_call_prompt(messages: list, functions: list):
    function_prompt = """Produce JSON OUTPUT ONLY! Adhere to this format {"name": "function_name", "arguments":{"argument_name": "argument_value"}} The following functions are available to you:"""
    for function in functions:
        function_prompt += f"""\n{function}\n"""

    function_added_to_prompt = False
    for message in messages:
        if "system" in message["role"]:
            if isinstance(message["content"], str):
                message["content"] += f""" {function_prompt}"""
            else:
                message["content"].append({"type": "text", "text": f""" {function_prompt}"""})
            function_added_to_prompt = True

    if function_added_to_prompt is False:
        messages.append({"role": "system", "content": f"""{function_prompt}"""})

    return messages
```

Five properties, all visible in these lines: a fixed preamble; each function
interpolated as a **Python dict repr** (`str()`, not `json.dumps`); a
substring role test (`"system" in message["role"]`); mutation of the
caller's dicts via `+=` / `.append`; and, when no system message exists, a
new `role: "system"` message appended **to the caller's list**. Note also
the emitted format (`{"name": ..., "arguments": {...}}`) does not match the
OpenAI `tool_calls` shape the page's own examples consume.

**The consumer (Claim 5).** `litellm/main.py:5510`:

```python
        if litellm.add_function_to_prompt and optional_params.get(
            "functions_unsupported_model", None
        ):  # if user opts to add it to prompt, when API doesn't support function calling
            functions_unsupported_model: Final = optional_params.pop("functions_unsupported_model")
            messages = function_call_prompt(messages=messages, functions=functions_unsupported_model)
```

`base_model` is not re-derived for the provider dispatch here (its uses in
this function are model-info lookup, logging, and Azure model-type
detection), so the provider resolution that put `functions_unsupported_model`
in `optional_params` still holds: Ollama only.

**The guardrail coupling (Claim 10).**
`litellm/proxy/guardrails/guardrail_hooks/lakera_ai.py:180-197`:

```python
            # For models where function calling is not supported, these messages by nature can't exist, as an exception would be thrown ahead of here.
            # Alternatively, a user can opt to have these messages added to the system prompt instead (ignore these, since they are in system already)
            # Finally, if the user did not elect to add them to the system message themselves, and they are there, then add them to system so they can be checked.
            # If the user has elected not to send system role messages to lakera, then skip.

            if system_message is not None:
                if not litellm.add_function_to_prompt:
                    content = system_message.get("content")
                    function_input: Final = []
                    for tool_call in tool_call_messages:
                        if "function" in tool_call:
                            function_input.append(tool_call["function"]["arguments"])

                    if len(function_input) > 0:
                        content += " Function Input: " + " ".join(function_input)
```

The in-code premise ("an exception would be thrown ahead of here") is the
documented `UnsupportedParamsError` from the unreachable `else` above — so
the comment describes behavior the release no longer implements, and the
`if not litellm.add_function_to_prompt:` branch that decides what gets
scanned is keyed on the global.

**Capability resolution order (Claims 2, 3, 4).**
`litellm/utils.py:2656` `_supports_factory()`:

```python
        model_info: Final = _get_model_info_helper(model=model, custom_llm_provider=custom_llm_provider)

        if model_info.get(key, False) is True:
            return True
        elif model_info.get(key) is None:  # don't check if 'False' explicitly set
            bare_model_key: Final = _get_model_cost_key(model)
            if bare_model_key is not None:
                bare_entry: Final = litellm.model_cost.get(bare_model_key) or {}
                if bare_entry.get(key, False) is True:
                    return True

            supported_by_provider = _supports_provider_info_factory(model, custom_llm_provider, key)
            if supported_by_provider is not None:
                return supported_by_provider

        return False
    except Exception as e:
        verbose_logger.debug(
            "Model not found or error in checking %s support. You passed model=%s, custom_llm_provider=%s. Error: %s",
            ...
        )
        supported_by_provider = _supports_provider_info_factory(model, custom_llm_provider, key)
        if supported_by_provider is not None:
            return supported_by_provider

        return False
```

`_supports_provider_info_factory()` returns `Literal[True] | None` — it can
upgrade an answer to `True` but never to `False`. One affirmative exit; every
other path lands on `return False`.

Provider info outranks the map, in `_get_model_info_helper()`
(`litellm/utils.py:5796-5814`):

```python
        if provider_config is not None:
            provider_get_model_info: Final = getattr(provider_config, "get_model_info", None)
            if callable(provider_get_model_info):
                try:
                    provider_model_info: Final = provider_get_model_info(
                        model=model,
                        api_base=api_base,
                        api_key=api_key,
                    )
                    if provider_model_info is not None:
                        return provider_model_info
                except Exception as e:
                    verbose_proxy_logger.warning(
                        "Could not get dynamic model info for model=%s, provider=%s; "
                        "falling back to the static cost map: %s",
                        ...
                    )
```

**Ollama's live probe and its template heuristic (Claim 4).**
`litellm/llms/ollama/common_utils.py:156-226`:

```python
    @staticmethod
    def _supports_function_calling(ollama_model_info: dict) -> bool:
        _template: Final[str] = str(ollama_model_info.get("template", "") or "")
        return "tools" in _template.lower()
```

```python
            response: Final = module_level_client.post(
                url=f"{api_base}/api/show",
                json={"name": model},
                headers=headers,
            )
            response.raise_for_status()
        except Exception:
            verbose_logger.debug("OllamaError: Could not get model info.")
            return {
                "key": model,
                "litellm_provider": "ollama",
                "mode": "chat",
                "input_cost_per_token": 0.0,
                "output_cost_per_token": 0.0,
                "max_tokens": None,
                "max_input_tokens": None,
                "max_output_tokens": None,
            }
```

The success branch adds `"supports_function_calling":
self._supports_function_calling(model_info)`; the failure branch does not —
so an unreachable Ollama server produces a record with no capability key and
therefore `False`. And the probe is skipped for models already in the cost
map:

```python
    def get_model_info(
        self,
        model: str,
        api_base: str | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any] | None:
        if self._is_static_ollama_model(model):
            return None
        return self.get_runtime_model_info(model=model, api_base=api_base, api_key=api_key)
```

**The enum defect (Claim 11).** `litellm/utils.py`, `function_to_dict()`:

```python
                    elif "{" in param_type:
                        # may represent a set of acceptable values
                        # translating as enum for function calling
                        try:
                            param_enum = str(list(literal_eval(param_type)))
                            param_type = "string"
                        except Exception:
                            pass
```

```python
        parameters[param_name] = {k: v for k, v in param_dict.items() if isinstance(v, str)}
```

`str(list(...))` is where the string-typed `enum` comes from; the
`isinstance(v, str)` filter is why the malformed value is the one that
survives into the schema.

**The capability data is remote (Claim 3).** `litellm/__init__.py:417-421`:

```python
model_cost_map_url: str = os.getenv(
    "LITELLM_MODEL_COST_MAP_URL",
    "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json",
)
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-completion-input-params.md` — **Claim 3** is
    the mechanism behind Claim 13's open question: any parameter LiteLLM does
    not classify as an OpenAI param "is assumed provider specific and passes
    it in as a kwarg in the request body", which is exactly where `functions`
    lands on providers where the fallback never runs (contradiction #1550) and
    where the deprecated `function_call=` rides along on the Ollama path.
    **Claim 1** corroborates the *shape* of Claim 5: a hard-coded list
    (`stream_options`, `extra_headers`, `max_retries`) that bypasses the
    support matrix, the mirror image of `tool_choice` being popped outside it.
    **Claim 12** corroborates the trust-boundary reading of Claim 7 from the
    other direction — `tools[].type` may already be `"mcp"`, so a world-mutating
    capability rides the ordinary `/chat/completions` surface; this note shows
    the same surface degraded to prompt text for non-native providers.
  - `source-notes/docs-litellm-completion-output.md` — **Claim 4** corroborates
    the `finish_reason` value this page's expected output relies on: all
    provider-specific values are normalized into a fixed five-value OpenAI set
    including `tool_calls`. That is what the *native* path returns; Claim 9
    shows the `add_function_to_prompt` path returns neither `tool_calls` nor
    that `finish_reason`, and that page's **Claim 1** records that the output
    page never documents `tool_calls` at all — this page is the corpus's only
    place the field appears in an example.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — **Claim 1**
    corroborates the observability half of Claim 9: a gateway that changes the
    request's semantics without telemetry. Its `stop_sequences`/`top_k` case
    ("a caller setting them gets a 200 with no error and no telemetry") and
    this page's silent tool-schema injection are the same class. **Claim 4**'s
    topology hazard — behavior that changes with which provider the gateway
    resolved — is the same shape as Claim 6's one-way global latch changing
    behavior across tenants from one Ollama request.
  - `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Claim 9**
    corroborates Claim 7's core mechanism on the same Anthropic pipeline:
    the gateway edits conversation history in flight to keep the provider
    happy. Two features, one underlying behavior — LiteLLM rewrites what the
    model sees, and the page's own code examples do not tell you.
  - `source-notes/docs-litellm-drop-params.md` — **Claim 1** corroborates the
    silent-narrowing family: `drop_params` converts a raise into a silent
    drop, and here the *documented* raise never fires at all. **Claim 9**
    corroborates the detection gap in Claims 6, 9, and 10 — the corpus now has
    three LiteLLM knobs whose behavior changes are announced by nothing.
  - `source-notes/blog-litellm-auto-router-v2.md` — **Claim 3** corroborates
    the routing question from the design side, and this note supplies the
    counterweight. That note's rationale is that "a fixed, versioned
    capability→model mapping is what makes 'why did this response cost 4x
    today' answerable after the fact" — an explicitly versioned mapping.
    Claims 3 and 4 show the *other* capability surface in LiteLLM is neither
    fixed nor versioned: it is a remote JSON artifact plus, for some
    providers, a live network probe with a template-substring heuristic. If
    you want answerability, prefer a mapping your config declares.

- **Contradicts**:
  - **The page contradicts its own implementation on the scope of
    `add_function_to_prompt`.** Side A (page): "For Models/providers without
    function calling support, LiteLLM allows you to add the function to the
    prompt set: `litellm.add_function_to_prompt = True`", demonstrated with
    `ANTHROPIC_API_KEY` and `completion(model="claude-2", ...)`. Side B
    (v1.103.2 `litellm/utils.py:4249-4295`): the flag's only read site is an
    `elif` inside a block whose first conjunct is `custom_llm_provider ==
    "ollama"`, so for `anthropic/` and every other non-Ollama provider the
    flag is inert, no prompt injection occurs, and the documented
    `UnsupportedParamsError` is unreachable too. Filed as contradiction issue
    **#1550**. **No verdict is taken here.**
  - Not filed separately, recorded for the resolver: the page's example
    assertions also fail against the shipped cost map
    (`supports_function_calling(model="xai/grok-2-latest")` is `False`,
    Claim 14). Same page, staleness rather than control-flow conflict; the
    logic for keeping it inside #1550 rather than opening a third issue is in
    that issue's notes.

- **Extends**:
  - `source-notes/docs-litellm-message-sanitization.md` — the closest sibling
    in the corpus and the right pairing for any gateway-mutation discussion.
    Its **Claim 1** establishes the `modify_params` precedent (a global-only
    gate on three outbound-message mutations); its **Claim 10** establishes
    that *that* transform returns a new list and leaves the caller's messages
    alone — which Claim 8 of this note shows the `add_function_to_prompt`
    path does not. Its **Claim 2** (a fabricated tool result) and **Claim 7**
    (transport-scoped mutation) bracket this note's Claims 7 and 10: LiteLLM
    has at least four documented or shipped ways to change what a model sees,
    and only one of them is a caller-visible response field. Its **Claim 8**
    (debug-only logging for a content mutation) is the same detection gap
    Claims 6, 9, and 10 extend.
  - `source-notes/docs-litellm-completion-input-params.md` — the parameter
    and message-shape boundary for `/chat/completions`; this note is the
    tool-calling capability layer above it.
  - `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Claim 3**'s
    practitioner rule ("The default guardrail is to deny agents any
    world-mutating action and require explicit human permission before any
    write") is the standard Claims 7 and 10 should be measured against: a
    tool schema that has been flattened into prompt text is no longer a
    structurally separate authorization surface, so the guide's Ch06
    function-calling authorization checklist needs a gateway-side step
    ("what did the gateway put in my prompt that I did not authorize?") that
    this independent source argues for on general grounds.

- **Novel**:
  - **A capability-prediction API whose failure mode is silent
    under-admission** (Claims 1–4), where the matrix is a remote reloadable
    JSON artifact and the fallback for one provider is a live HTTP probe with
    a substring heuristic over a prompt template. Nothing in the corpus
    treats `supports_function_calling()` as an ops surface at all.
  - **The page's own example assertions failing against the release's data**
    (Claim 14) — one of five, failing closed, in vendor docs presented as
    runnable checks.
  - **A documented feature that is inert on every provider except the one it
    was not written for** (Claim 6, contradiction #1550), with the documented
    example (`claude-2`) unable to exercise it.
  - **A module global that the library writes on the request path and never
    resets** (Claim 6) — one Ollama request changes process state that other
    tenants' requests and a guardrail hook read.
  - **The injected tool schema is un-delimited, un-escaped Python-repr text
    appended in place to the caller's own system message** (Claim 7), with no
    response-side signal (Claim 9) — the trust-boundary instance Ch06 needs
    and the page's framing ("LiteLLM allows you to add the function to the
    prompt") does not convey.
  - **A guardrail's scanned payload decided by an unrelated module global**
    (Claim 10) — new to the corpus and the highest-consequence claim here.
  - **A live schema generator that emits `enum` as a Python-list string**
    (Claim 11), i.e. a released, documented, copy-pasteable defect in a field
    that is how you constrain tool arguments.
  - **A documented escaping change to the caller's message list** (Claim 8),
    the opposite contract from the same vendor's message sanitizer.

- **Dismissed from the pre-computed candidate list** (`miner-related-notes.md`,
  10 candidates), per MINER.md §4b — each was opened and checked against the
  claim it suggested, and none is cited above because none bears on this
  page: `docs-litellm-batches-api.md` (rate limits and batch accounting —
  no tool-calling or capability content), `docs-litellm-bedrock-invoke.md`
  (Bedrock passthrough auth and route shape — nothing about `tools` or the
  capability matrix), `docs-litellm-a2a-iteration-budgets.md` (agent session
  iteration and spend caps — no tool surface), `docs-litellm-audio-transcription.md`
  (non-chat endpoint mode registration — different endpoint family),
  `docs-litellm-message-sanitization.md` and
  `docs-litellm-anthropic-advisor-tool.md` (both cited above under
  Corroborates/Extends, not dismissed),
  `docs-google-sre-prodcast-04-09-ai-agents.md` (cited above under Extends),
  `blog-litellm-auto-router-v2.md` and `docs-litellm-completion-output.md`
  (both cited above under Corroborates). Candidates
  `docs-litellm-completion-input-params.md` and
  `docs-litellm-messages-to-responses-mapping.md` are cited above. Every
  `Claim N` cited above was re-read in the cited note and the number
  confirmed against that claim's content, not approximated.

## Guide Impact

- **Chapter 06, §"Function-calling authorization" (~L265)**: the section's
  runtime counterpart already prescribes a gateway guardrail "handed both the
  tool schemas and the model's actual invocations — `tools` (what is
  *available*) and `tool_calls` (what is *being called*)". Add the failure
  mode this source documents: **on a provider without native tool calling,
  LiteLLM can collapse that separation** — the schema is concatenated into the
  system message as Python-repr text, un-delimited and un-escaped, with a
  preamble that merely *asks* for JSON, and nothing parses the reply back
  into `tool_calls` (Claims 7, 9). So the authorization surface an operator
  thinks they are gating is, on that path, prompt text. Add the
  gateway-side probe the guide currently lacks: *what did the gateway put into
  my prompt that I did not write?* And add the one configuration fact that
  can change a guardrail's input without a deploy: `add_function_to_prompt`
  is read by the Lakera hook, and one Ollama request sets it process-wide
  (Claims 6, 10). Recommend the section state the trust-boundary property
  explicitly rather than implying tool schemas stay structured.
- **Chapter 06, §"A guardrail is an egress boundary — configure what crosses
  it" (~L547)**: one sentence, high value. The boundary is not only *which
  roles* cross it but *which content* the guardrail is handed, and here a
  mutable module global — written on the request path, never reset, readable
  by a guardrail hook — decides part of that content. Cite Claim 10 and
  Claim 6.
- **Chapter 05, §"Parameter migration hazards" (~L327)**: the section's rule
  is to audit parameters against the model's supported set before routing
  production traffic. Add the capability-discovery half, which the corpus does
  not cover: `supports_function_calling()` and
  `supports_parallel_function_calling()` are two independent, **fail-closed**
  keys in a **remote, reloadable** cost map, with a live provider probe
  (Ollama: a `POST /api/show` plus a `"tools" in template` substring test)
  taking precedence for some providers (Claims 1–4). Practical rule: gate
  routing on the cost map read once at config time, never on a live call; and
  treat a capability answer as *stale after every cost-map reload*, which
  makes this section's existing reload material the natural home for the
  re-validation step. Add the `functions=` case with its absent removal date
  (Claim 13) and the `function_to_dict` enum defect as two items on the audit
  checklist (Claim 11) — the second is worth listing because it produces a
  schema that *looks* valid and silently drops the constraint.
- **Chapter 05, §"Provider parity in the shared forwarding path" (~L343)**:
  a clean instance of the section's thesis with an unusual polarity — the
  gateway's tool-calling fallback applies to exactly **one** provider while
  the documentation describes it as general, and the same flag changes a
  guardrail's payload on every provider (Claims 6, 10, contradiction #1550).
  Cite with the version boundary stated, per #1514's precedent.
- **Chapter 05, §"A green eval is not evidence until you can name what it
  measured" (~L567)**: add the tool-eval precondition. On the fallback path
  there is no `tool_calls` in the response, so an eval or assertion written
  against `response.choices[0].message.tool_calls` — the exact shape the
  page's own examples use — measures nothing and passes or fails for reasons
  unrelated to the tool (Claim 9). Also add: the injected schema lands in the
  system message, so a tool description mutated at runtime busts the prompt
  cache for every conversation using that tool, and the caller's message list
  is mutated in place, so golden-transcript comparisons and prompt-cache keys
  computed from it are wrong after a retry (Claims 8, 15).
- **Chapter 02, §"The observability model for LLM applications" (~L7)**: add
  a named gap alongside the existing ones. A capability predicate that
  fail-closes logs only at `verbose_logger.debug` and only on the exception
  path; the prompt injection that changes what the model sees emits no log,
  no header, and no response field; and the guardrail payload change emits
  nothing at all (Claims 2, 9, 10). Same family as
  `docs-litellm-drop-params.md` Claim 9 and
  `docs-litellm-message-sanitization.md` Claim 8 — this is now four LiteLLM
  surfaces where the behavior change is invisible, which is itself the
  finding worth stating once in the chapter.
- **A standing editorial rule the Smith should state once, in Ch05**: four
  LiteLLM documentation pages in this corpus (this one, #1514's
  `modify_params`, `docs-litellm-completion-input-params.md` Claim 5,
  `docs-litellm-anthropic-advisor-tool.md` Claim 12) disagree with the
  shipped release, and this page additionally contradicts its own section
  headings and contains a non-running assertion (Claim 14). Recommend a
  standing rule: **LiteLLM documentation code blocks are illustrative, not
  transcribed — cite the shipped source and the shipped cost map as the
  behavior of record, and state the release checked.** Individual notes
  should stop re-deriving this.
- **Do not** carry Claim 15's token-cost reasoning into the guide as a
  figure. It is inference from the code path with no measurement anywhere in
  the corpus; if the Smith wants the cost consequence, it needs a measurement
  first.

## Extraction Notes

- Full read of the page, including both capability sections, the parallel
  function-calling definition, the "Quick Start - gpt-3.5-turbo-1106"
  section with its full-code block and three-step walkthrough (Step 1, Step 2,
  Step 3, each with an expected-output block), the Azure OpenAI variant, the
  deprecated `functions=` section, both `function_to_dict` sections (usage +
  output + the second worked example), and the
  "Function calling for Models w/out function-calling support" section.
  **No linked sub-page was followed, deliberately.** The nav's Tool Calling
  siblings (`/docs/completion/web_search`, `/docs/completion/web_fetch`,
  `/docs/completion/computer_use`, `/docs/completion/message_sanitization`,
  `/docs/guides/tools_integrations`, `/docs/guides/code_interpreter`) are
  separately-registered pages that are already covered or queued —
  `docs-litellm-message-sanitization.md` exists in the corpus — and following
  them would re-mine material this repo already owns rather than deepen this
  page. Depth on this page came from reading the implementation instead, per
  the precedent set by `docs-litellm-message-sanitization.md`.
- **The Prospector's triage comment scoped this tightly and was followed.**
  Its four key questions map to Claims 1–4 (is the capability helper an
  ops-usable routing primitive), Claims 7/8/10 (trust-boundary behavior of
  `add_function_to_prompt`, including "how is the injected function block
  delimited or escaped" — answered: it is not), Claim 11 (is the `enum`
  string a live defect or a rendering artifact — answered: live defect,
  `str(list(...))` at `litellm/utils.py`), and Claim 13 (the
  deprecated/current split with no removal date). The weather examples, the
  Azure redeploy variant, and OpenAI-cookbook content were skipped as
  instructed, with one exception worth flagging: the *Azure* block was read
  (not extracted for its Azure content) because it is the second place the
  `tool_choice="auto"` parameter appears, which is load-bearing for Claim 5.
  The triage comment's own claim that "no hits for
  `supports_function_calling`, `add_function_to_prompt`, or `function_to_dict`
  in `source-notes/` or `guide/`" was re-verified this session and holds.
- **Implementation verification was performed by the Miner and is not part of
  the source.** All implementation claims (1–6, 8–15) were checked against
  `litellm` **v1.103.2** (latest release, published 2026-10-01, retrieved
  2026-10-02) via the release tarball — `litellm/utils.py`,
  `litellm/main.py`, `litellm/litellm_core_utils/prompt_templates/factory.py`,
  `litellm/proxy/proxy_server.py`, `litellm/proxy/proxy_cli.py`,
  `litellm/proxy/guardrails/guardrail_hooks/lakera_ai.py`,
  `litellm/llms/ollama/common_utils.py` — plus a repo-wide search for
  `add_function_to_prompt` and `functions_unsupported_model`, and a lookup of
  the page's five example models against the shipped
  `model_prices_and_context_window.json` (4320 keys) from the same tag. The
  page is **undated** and cites no version, so this is a point-in-time check
  rather than a claim about what every release shipped. Both sides of each
  discrepancy are quoted so a resolver can judge without re-running it. One
  caveat recorded honestly: the `xai/grok-2-latest` verdict in Claim 14 rests
  on absence from the shipped map plus an absence of capability declarations
  in the `xai` provider config, which together force the fail-closed `False`;
  it was not executed against a live install, since installing the package
  was out of scope for a headless Miner run.
- **A contradiction issue was filed** for the `add_function_to_prompt` scope
  conflict (page vs v1.103.2 `pre_process_optional_params()`), as **#1550**,
  with a recommended verdict of `unresolved` on the grounds that a version
  boundary needs establishing before a winner is picked — the same posture as
  #1514. No verdict is taken in this note, per MINER.md §4a. Pre-existing open
  contradiction issues were checked first (#1548, #1534, #1517, #1514, #1486,
  #1462, #1461, #1408, #1352, #1338, #1322, #1307, #1150) — none covers
  `add_function_to_prompt`, `function_to_dict`, or
  `supports_function_calling`. #1514 is the closest sibling and concerns a
  different flag, so it was cited as precedent rather than duplicated.
- **Provenance**: the page was auto-filed from the already-registered
  `litellm-docs` site-crawl seed by `scripts/scan-sites.py`, so no new
  registry entry is warranted and `registry/sources.json` and
  `registry/claims-index.json` are left untouched, per AGENTS.md hard rule 2.
- **On the page's code blocks**: the page publishes its code blocks with
  newlines collapsed, so the assertions and imports read as run-on lines. All
  quotes above are verbatim *as rendered*, and none should be treated as
  copy-pasteable Python — the same defect
  `docs-litellm-completion-output.md` Claim 9 records for the output page.
- **Thinness, stated plainly**: the prose content of this page is genuinely
  thin, as the Prospector warned — roughly a dozen sentences plus four
  OpenAI-cookbook code blocks. Fifteen claims were extractable only because
  the implementation was read; a docs-only extraction would have yielded four
  claims (the two predicates, `function_to_dict`, and the `functions=`
  deprecation) and three of them would have been wrong or misleading. This is
  recorded for the Assayer's benefit: the depth here is code-verified, not
  page-verified, and every code-derived claim is reproducible from the tag
  and file:line references given.
