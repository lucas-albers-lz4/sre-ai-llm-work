---
source_url: https://docs.litellm.ai/docs/completion/drop_params
source_type: docs
title: "Drop Unsupported Params | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-27)
date_extracted: 2026-09-27
last_checked: 2026-09-27
status: current
confidence_overall: emerging
issue: "#1480"
---

# Drop Unsupported Params (LiteLLM Docs)

> The canonical reference for the gateway's parameter-support gate: LiteLLM
> **raises by default** when a request carries a parameter the target
> model/provider does not support, and a single knob (`drop_params`) flips that
> into a **silent omission** — the switch that decides whether
> guide/05-llm-ops-reliability.md's "may be silently ignored or explicitly
> rejected" lands on the silent branch or the loud branch. Ops-relevant content
> beyond the well-known `drop_params` flag: `additional_drop_params` accepts
> **JSONPath-like nested-field notation** (`tools[*].input_examples`,
> `parent.child`, `array[0]`, …) that rewrites the *outbound payload in flight*,
> with the page's own stated use case being "Remove `input_examples` from tool
> definitions (Claude Code + AWS Bedrock)"; `allowed_openai_params` is the
> documented inverse override that force-passes a param past the gate; the
> support matrix has an executable introspection form
> (`litellm.get_supported_openai_params("<model>")`); and the knob has **four
> documented placements with no stated precedence** and **no documented signal
> emitted on a drop**. Not marketing — knob tables, a syntax table, and eleven
> verbatim config/code examples are the evidence.

## Source Context

- **Type**: docs (single-page LiteLLM gateway parameter-handling reference at
  `/docs/completion/drop_params` — verified HTTP 200 this session, matching
  `source_url`). Site breadcrumb per the page's own JSON-LD:
  "Guides → Compatibility & Extensibility → Drop Unsupported Params". Sibling
  pages in the same nav section: `provider_specific_params` (Previous) and
  `model_alias` (Next); the site-crawl seed filed them separately as #1481 and
  #1482, so they were not followed.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented* knob surface: it gives the default
  polarity, four placement forms with runnable code, a nested-syntax table, a
  type contract, and a permalink into the implementing source
  (`litellm/utils.py#L3584`). This is vendor documentation of the product's own
  behavior — no independent validation, no metrics, no test output, and the
  page is undated.
- **Scope**: The unsupported-parameter gate only: the default-raise rule, the
  `drop_params` switch and its four placements, `additional_drop_params`
  (including nested-field removal), `allowed_openai_params`, and the
  supported-params introspection helper. Does NOT cover: *which* params each
  provider/model supports (the matrix is a separate, larger surface referenced
  but not reproduced here), the translation-layer parameter mapping for
  `/v1/messages` (that is `docs-litellm-messages-to-responses-mapping.md`,
  #1390), the `context_management` polyfill's own opt-out semantics
  (`docs-litellm-claude-code-context-management.md`, #1445), or any logging /
  metrics surface for drops.
- **Redundancy**: Three existing notes cite this knob family *second-hand* and
  none owns it. `docs-litellm-claude-code-context-management.md` Claim 10
  treats `drop_params` as a disable switch and gets the negation right from a
  *different* page; `docs-litellm-messages-to-responses-mapping.md` Claim 4
  names `drop_params` as a proxy-hop escape valve; `blog-litellm-auto-router-v2.md`
  Claim 9 uses it as the worked example of alias-level `litellm_params` that
  used to vanish on routed requests. This page is the grounding reference all
  three lean on; per the Prospector's instruction it grounds and extends them
  rather than re-deriving them.

## Extracted Claims

### Claim 1: The default is a hard exception — LiteLLM raises when a request carries a parameter the target model does not support, and `drop_params=True` converts that raise into a silent drop of the parameter
- **Evidence**: The "Default Behavior" section states the default and the flip
  in consecutive sentences, with a concrete `temperature` example.
- **Confidence**: settled (explicit vendor statement of both polarities; the
  example is a specific parameter/model mismatch)
- **Quote**: "By default, LiteLLM raises an exception if you send a parameter to a model that doesn't support it." / "For example, if you send `temperature=0.2` to a model that doesn't support the `temperature` parameter, LiteLLM will raise an exception." / "When `drop_params=True` is set, LiteLLM will drop the unsupported parameter instead of raising an exception. This lets your code work across different providers without having to customize parameters for each one."
- **Our assessment**: This is the polarity the corpus has been missing, and it
  inverts the common "gateways silently strip" folk assumption. The guide's
  Ch05 rule ("Parameters valid on earlier models may be silently ignored or
  explicitly rejected", guide/05-llm-ops-reliability.md ~L338-341) describes
  both branches but does not say *who chooses*. This page says the answer is a
  **config flag, not a provider property**: a LiteLLM deployment in its
  documented default state *loudly* rejects unsupported params, and a single
  operator-set boolean converts that fleet-wide to silent. The same client code
  therefore produces 500-class gateway errors on one proxy and quiet
  behavior-divergence on another with an unchanged request. The "This lets
  your code work across different providers" sentence is the vendor selling the
  silent branch as the portability feature — which is exactly why the
  observability cost (Claim 9) is worth stating.

### Claim 2: The support matrix is keyed on provider *and* model (not provider), and the page ships an executable introspection call as its source of truth — `litellm.get_supported_openai_params("<model>")`
- **Evidence**: The sentence following the Quick Start code block, with its
  worked provider/model asymmetry and a permalink into the implementing source.
- **Confidence**: settled (explicit vendor statement plus a linked source
  location)
- **Quote**: "LiteLLM maps all supported openai params by provider + model (e.g. function calling is supported by anthropic on bedrock but not titan)." / "See `litellm.get_supported_openai_params("command-r")`"
- **Our assessment**: Two operational consequences. (1) The gate is
  *per-model*, not per-provider, so "Cohere supports X" is not a usable
  precondition — the same provider's other model can differ, exactly as the
  page's bedrock-anthropic-vs-titan example shows. An operator auditing a
  migration cannot answer with a provider capability table. (2) The page hands
  over the executable form of the audit, which is the single most reusable
  item here: it is the pre-migration check Ch05's "audit existing request
  parameters against the model's supported set" rule has been asking for, and
  it is a single function call that can be run per candidate model *before*
  traffic is routed. The "If a provider/model doesn't support a particular
  param, you can drop it." sentence directly ties the two. Note the page links
  a line anchor (`litellm/utils.py#L3584`) in the LiteLLM repo — a line number
  in a moving file, so the citation is version-sensitive.

### Claim 3: `drop_params` is documented in four placements with **no stated precedence or composition** between them — SDK module global (`litellm.drop_params = True`), proxy-global config (`litellm_settings.drop_params: true`), per-request kwarg (`completion(..., drop_params=True)`), and per-deployment (`litellm_params.drop_params: true`)
- **Evidence**: Four separate code blocks across the Quick Start, "OpenAI
  Proxy Usage", and "Pass drop_params in completion(..)" sections, each with a
  `👈 KEY CHANGE` marker on the drop line. No precedence, override, or
  interaction statement appears anywhere on the page.
- **Confidence**: settled for the four documented placements; the
  **absence** of a precedence statement is the claim and is itself verified —
  no section of the page discusses interaction or which placement wins
- **Quote**: "litellm.drop_params = True # 👈 KEY CHANGE" / "litellm_settings:
  drop_params: true" / "Just drop_params when calling specific models"
- **Our assessment**: The precedence gap is the finding, and it is a real
  config-drift surface for a fleet: four places to set one boolean, silently
  different blast radii, and a documentation page that never says how they
  compose. The two *global* placements are process- and proxy-wide, so setting
  them once to fix one broken call route changes the failure polarity for every
  other model the proxy serves — including models that *do* support the
  parameter, where "drop it" is now a silent narrowing of an explicit caller
  request. The safe reading for the guide (flagged as the Miner's inference,
  not a documented rule): a per-deployment or per-request placement is the
  auditable one, because its blast radius is legible in `config.yaml`; a
  `litellm_settings` or module-global flip is a *fleet-wide silent-omission
  switch* and should be treated as a change requiring the same review as a
  routing change. This is the same "config-layers drift" hazard Ch05 treats for
  routing, applied to a safety-relevant boolean.

### Claim 4: `additional_drop_params` is a *wider* gate than `drop_params` — an explicit list of params to strip on the way to the model regardless of whether the target supports them, typed as "List or null", and settable per-request or per-deployment
- **Evidence**: The "Specify params to drop" section's SDK and PROXY examples
  (both using `["response_format"]`), plus the type-contract line.
- **Confidence**: settled (explicit definition sentence with a type contract and
  two placement examples)
- **Quote**: "To drop specific params when calling a provider (E.g. 'logit_bias' for vllm)" / "**additional_drop_params**: List or null - Is a list of openai params you want to drop when making a call to the model."
- **Our assessment**: The semantic difference from `drop_params` is the
  load-bearing part and the page does not spell it out: `drop_params` is
  *reactive* (LiteLLM drops what the support matrix says is unsupported),
  while `additional_drop_params` is *proactive* (the operator names what to
  strip, support matrix notwithstanding). That makes it the right tool for a
  provider whose support matrix is wrong or unknown, and the wrong tool to
  reach for casually — listing a param the target *does* support silently
  discards a caller's explicit request, with the same absence of signal as
  Claim 1's silent branch. The page's own parenthetical use case
  (`'logit_bias' for vllm`) is the same shape as the corpus's existing
  vLLM-parameter-divergence incident
  (`failure-litellm-vllm-embeddings-encoding-format.md`, Claims 1-4), where the
  fix was filter-to-omit at the shared boundary; `additional_drop_params` is
  the declarative, config-level equivalent of that Python filter, and it
  generalizes it from one parameter to a list.

### Claim 5: `additional_drop_params` accepts **JSONPath-like nested-field notation** — six documented syntax forms — so a nested field inside a complex object is removed from the outbound request, not just a top-level parameter
- **Evidence**: The "Nested Field Removal" section's SDK and PROXY examples
  (targeting a field inside a `tools[]` element) plus the six-item "Supported
  syntax" list.
- **Confidence**: settled (explicit syntax table plus two runnable examples)
- **Quote**: "Drop nested fields within complex objects using JSONPath-like notation:" / "`field` - Top-level field" / "`parent.child` - Nested object field" / "`array[*]` - All array elements" / "`array[0]` - Specific array index" / "`tools[*].input_examples` - Field in all array elements" / "`tools[0].metadata.field` - Specific index + nested field"
- **Our assessment**: This is the genuinely new mechanism in the corpus —
  a *payload rewriter*, not a parameter filter. The documented syntax ladder
  (`field` → `parent.child` → `array[*]` → `array[0]` → wildcard-plus-nested →
  index-plus-nested) is a bounded subset of JSONPath, and the page's own
  warning-free list means the operator gets no error for a path that matches
  nothing: a typo in the path degrades to "nothing was removed", silently, on
  a surface where the whole point is that the client is unmodified. The
  operational significance is that it moves payload surgery from every client
  to one proxy config — a single `config.yaml` line fixes a whole fleet of
  clients, and equally a single `config.yaml` line silently rewrites a whole
  fleet's tool definitions. There is no client-visible or response-visible
  marker (see Claim 9). Note also that this is the first corpus occurrence of
  a *drop-path* wildcard syntax; the `[*]` patterns elsewhere in the corpus are
  response-field mappings, a different mechanism.

### Claim 6: The page's own named use case for nested removal is stripping `input_examples` from tool definitions on the Claude Code + AWS Bedrock path — a gateway-side workaround for a nested tool-schema field the downstream rejects, with no client change
- **Evidence**: The SDK and PROXY examples under "Nested Field Removal" both
  target `tools[*].input_examples` on `bedrock/us.anthropic.claude-sonnet-5`,
  and the first bullet of the "Example use cases" list names the scenario.
- **Confidence**: settled for the documented pattern; the motivating upstream
  failure (Bedrock rejecting the field) is the page's framing, not an
  independently reported error
- **Quote**: "Remove `input_examples` from tool definitions (Claude Code + AWS Bedrock)" / "Drop provider-specific fields from nested structures" / "Clean up nested parameters before sending to LLM"
- **Our assessment**: This is the pattern's load-bearing example and it sits
  exactly where the corpus's Claude Code work already is. Claude Code emits
  richer tool definitions than the Bedrock tool schema accepts, and this is
  the documented remedy that does not require patching the client — a
  materially different posture from the cost/playbook levers in
  `blog-litellm-save-claude-code-costs.md` (which the operators also apply at
  the proxy, but as additive context, not as a schema rewrite). Two cautions
  the page does not give the operator. (1) The strip is unconditional for that
  deployment: every tool definition routed to that `model_name` loses
  `input_examples`, including from clients that would have been fine. (2)
  Because the page documents no signal on removal (Claim 9), the operator
  cannot tell from the response whether the rewrite fired — the only
  verification is inspecting the outbound provider payload, the same
  "verify after routing" conclusion
  `docs-litellm-messages-to-responses-mapping.md` Claim 1 reaches for the
  translation layer. The page also does not say what happens if the path is
  valid but the field is absent, nor whether the same syntax reaches fields
  under `input_schema` itself (the docs only show `input_examples`, a sibling
  of `input_schema`, not a child of it).

### Claim 7: `allowed_openai_params` is the documented inverse override — the stated remedy for `litellm.UnsupportedParamsError`, passing the param through as-is, with SDK, per-request proxy, and per-model config placements
- **Evidence**: The "Specify allowed openai params in a request" section's
  opening sentence, plus three examples (SDK `acompletion`, OpenAI-SDK
  `extra_body`, `config.yaml`).
- **Confidence**: settled (explicit vendor statement of purpose and behavior
  with three placements)
- **Quote**: "Tell litellm to allow specific openai params in a request. Use this if you get a `litellm.UnsupportedParamsError` and want to allow a param. LiteLLM will pass the param as is to the model." / "When using litellm proxy you can pass `allowed_openai_params` in two ways:"
- **Our assessment**: The knob that makes the gate *auditable from the error
  side*: the raise from Claim 1 is actionable, and this is the documented
  answer. It also completes a pair the corpus has only ever seen one half of —
  `blog-litellm-gpt-5-5-day-0.md` Claim 4 documents LiteLLM's *local*
  enforcement of reasoning-effort caps via `UnsupportedParamsError` and notes
  that the error surface shifted from upstream 400s to gateway errors; that
  note has the error with no remedy, and this page supplies the remedy. The
  important asymmetry for operators: `allowed_openai_params` and `drop_params`
  are opposite overrides on the same gate, so a deployment can be configured
  to both strip params it knows are unsupported and force-passthrough params it
  believes are supported — with the effective behavior for any single param
  decided by which of the two fires first, which the page does **not** state.
  The page is also silent on the risk direction: force-passing a param the
  downstream genuinely rejects converts a local, attributable gateway error into
  an upstream provider error with a different status and monitoring path — the
  mirror image of the drop-branch's silent-wrong-outcome. That is the Miner's
  reading of the two documented behaviors, not a documented warning.

### Claim 8: Set on `config.yaml`, `allowed_openai_params` applies to **every request to that deployment** — a blanket, model-scoped bypass of the support check, not a per-request exception
- **Evidence**: The "Set allowed_openai_params on config.yaml" section's
  one-sentence scope statement and its `model_list` example.
- **Confidence**: settled (explicit scope sentence)
- **Quote**: "You can also set `allowed_openai_params` on the config.yaml file for a specific model. This means that all requests to this deployment are allowed to pass in the `tools` param."
- **Our assessment**: The scope sentence is short and load-bearing: "for a
  specific model" / "all requests to this deployment". That is the right
  granularity (per `model_name`, not proxy-global, unlike `litellm_settings`),
  and it is the only one of the four `drop_params` placements plus this one
  whose blast radius is stated in prose. But note the residual gap: the
  allowlist is unconditional per deployment, so a new client that sends `tools`
  in a shape the deployment's downstream model actually rejects now fails
  upstream instead of at the gateway — the operator has traded a local,
  well-attributed error class for an upstream one across every caller on that
  deployment, and nothing on the page warns about that trade. Pair with the
  `config.yaml` example's own scope: the force-passthrough is visible in
  `config.yaml` only if the operator looks for it, because a request that
  succeeds carries no marker that the check was bypassed (Claim 9).

### Claim 9: The page documents **no observable signal for a drop** — no log line, metric, response field, or header is stated for either branch, so the only difference a caller or monitor can detect between "param honored" and "param silently stripped" is the absence of the raise
- **Evidence**: Verified by full-page read: the page's ten sections cover
  Default Behavior, Quick Start, OpenAI Proxy Usage, per-request `drop_params`,
  `additional_drop_params`, Nested Field Removal, and the three
  `allowed_openai_params` placements. None of them mentions logging, metrics,
  callbacks, response fields, or headers. The only verb used for the drop
  action is "drop" / "will be removed" — and the `allowed_openai_params`
  section is the only place the error class is named
  (`litellm.UnsupportedParamsError`).
- **Confidence**: settled as an **absence** claim (the page is fully read and
  short; the omission is checkable by re-reading it). It is an absence in
  *documentation*, not a claim that LiteLLM emits nothing — the page is a knob
  reference, and gateway logging is documented elsewhere. Recorded per the
  Prospector's explicit instruction to confirm rather than assume.
- **Quote**: (no direct quote; the page contains no sentence describing a drop
  signal — see the section inventory and paraphrase in Our assessment)
- **Our assessment**: If the docs are complete on this point, then flipping
  `drop_params` buys cross-provider portability by deleting the request's own
  error surface, and the operator's only evidence of a dropped parameter is a
  downstream behavior change with no attributed cause. That is exactly the
  observability hole Ch02 cares about, and it is *asymmetric*: the loud branch
  leaves a stack-trace-class error, the silent branch leaves nothing. The
  practical consequence for the guide is a monitoring rule rather than a
  feature: a proxy fleet running `drop_params` (or any
  `additional_drop_params` entry, or any nested-path rewrite) has an
  unmonitored parameter surface, and the only auditable checks are
  (a) enumerate the config, and (b) diff the outbound provider payload. Given
  the body of evidence — a `config.yaml` where the knob can be set at four
  layers, a wildcard path syntax, and a per-deployment force-passthrough — the
  Miner rates the *absence* of a documented signal as the most consequential
  gap on this page, and flags that verifying it against the gateway's actual
  logging surface (rather than this page) is the open follow-up.

### Claim 10: The page's four proxy config snippets are formatted inconsistently — the per-model `drop_params` and `additional_drop_params` examples are bare list fragments with `litellm_params` first and no `model_list:` wrapper, while the nested-field and `allowed_openai_params` per-model examples include `model_list:` and list `model_name` first; all four are valid YAML and parse to the same structure
- **Evidence**: Verbatim line-by-line extraction of the four proxy config code
  blocks, plus a parse check of the reproduced artifacts. The `drop_params`
  per-model block renders as five lines: `- litellm_params:` at column 0,
  `api_base` / `model` / `drop_params` at column 4, and `model_name: my-model`
  at column 2 *after* them; the `additional_drop_params` block has the
  identical shape. By contrast the nested-field and `allowed_openai_params`
  per-model blocks both begin `model_list:` and list `model_name` first.
  Parsing the two fragments (`yaml.safe_load`) yields
  `[{"litellm_params": {...}, "model_name": "my-model"}]` — a well-formed
  one-element list whose item has `litellm_params` and `model_name` as
  **sibling** keys; wrapping the same fragment under `model_list:` parses to
  the structurally identical mapping.
- **Confidence**: settled (a directly re-checkable property of the reproduced
  blocks, verified by parsing them; the rendered text is reproduced verbatim
  in Concrete Artifacts)
- **Quote**: (no prose quote — the difference is in the code blocks themselves;
  reproduced verbatim in Concrete Artifacts → "Per-model proxy config snippets
  (verbatim, as published)")
- **Our assessment**: Cosmetic, and the correction it forces is on us rather
  than on the page. The two fragments are **valid YAML**, not defective
  config: because YAML mappings are unordered and `model_name` sits at column
  2 alongside `litellm_params`, the two keys compose into one well-formed list
  item, and the only real differences from the page's other two per-model
  snippets are key order and the elided `model_list:` wrapper. That is a
  documentation-style inconsistency, not something an operator would hit after
  pasting. Two small operational notes survive. (1) The elided wrapper means
  the fragment is not a standalone `config.yaml`: pasted on its own it is a
  bare sequence where LiteLLM expects a top-level `model_list` key, so the
  operator has to supply the surrounding shape. (2) Because key order varies
  across the page's own snippets, a diff of two per-model blocks can look like
  a substantive change when it is a reordering. Neither warrants a warning in
  the guide; the well-formed `model_list:` form is in
  `docs-litellm-claude-code-context-management.md`'s per-model
  `additional_drop_params` artifact. This claim is a formatting observation,
  not a claim about LiteLLM behavior and not a documentation defect.

## Concrete Artifacts

All artifacts verbatim from
https://docs.litellm.ai/docs/completion/drop_params (line structure preserved
from the rendered code blocks; trailing whitespace inside code lines is as
published).

### Default behavior (verbatim prose)

> **By default, LiteLLM raises an exception** if you send a parameter to a
> model that doesn't support it.

### Supported nested-drop syntax (verbatim list)

> **Supported syntax:**
>
> - `field` - Top-level field
> - `parent.child` - Nested object field
> - `array[*]` - All array elements
> - `array[0]` - Specific array index
> - `tools[*].input_examples` - Field in all array elements
> - `tools[0].metadata.field` - Specific index + nested field

### Example use cases (verbatim list)

> - Remove `input_examples` from tool definitions (Claude Code + AWS Bedrock)
> - Drop provider-specific fields from nested structures
> - Clean up nested parameters before sending to LLM

### Quick Start — SDK module global (verbatim)

```python
import litellm 
import os 

# set keys 
os.environ["COHERE_API_KEY"] = "co-.."

litellm.drop_params = True # 👈 KEY CHANGE

response = litellm.completion(
                model="command-r",
                messages=[{"role": "user", "content": "Hey, how's it going?"}],
                response_format={"key": "value"},
            )
```

### OpenAI Proxy Usage — proxy-global (verbatim)

```yaml
litellm_settings:
    drop_params: true
```

### Per-request — SDK (verbatim)

```python
import litellm 
import os 

# set keys 
os.environ["COHERE_API_KEY"] = "co-.."

response = litellm.completion(
                model="command-r",
                messages=[{"role": "user", "content": "Hey, how's it going?"}],
                response_format={"key": "value"},
                drop_params=True
            )
```

### Per-model `additional_drop_params` — SDK (verbatim)

```python
import litellm 
import os 

# set keys 
os.environ["COHERE_API_KEY"] = "co-.."

response = litellm.completion(
                model="command-r",
                messages=[{"role": "user", "content": "Hey, how's it going?"}],
                response_format={"key": "value"},
                additional_drop_params=["response_format"]
            )
```

### Nested field removal — SDK (verbatim)

```python
import litellm

response = litellm.completion(
    model="bedrock/us.anthropic.claude-sonnet-5",
    messages=[{"role": "user", "content": "Hello"}],
    tools=[{
        "name": "search",
        "description": "Search files",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
        "input_examples": [{"query": "test"}]  # Will be removed
    }],
    additional_drop_params=["tools[*].input_examples"]  # Remove from all tools
)
```

### Nested field removal — PROXY, well-formed `model_list:` form (verbatim)

```yaml
model_list:
  - model_name: my-bedrock-model
    litellm_params:
      model: bedrock/us.anthropic.claude-sonnet-5
      additional_drop_params: ["tools[*].input_examples"]  # Remove from all tools
```

### `allowed_openai_params` — LiteLLM Python SDK (verbatim)

```python
await litellm.acompletion(
    model="azure/o_series/<my-deployment-name>",
    api_key="xxxxx",
    api_base=api_base,
    messages=[{"role": "user", "content": "Hello! return a json object"}],
    tools=[{"type": "function", "function": {"name": "get_current_time", "description": "Get the current time in a given location.", "parameters": {"type": "object", "properties": {"location": {"type": "string", "description": "The city name, e.g. San Francisco"}}, "required": ["location"]}}}],
    allowed_openai_params=["tools"],
)
```

### `allowed_openai_params` — proxy, dynamic per-request via the OpenAI SDK (verbatim)

```python
import openai
from openai import AsyncAzureOpenAI

import openai
client = openai.OpenAI(
    api_key="anything",
    base_url="http://0.0.0.0:4000"
)

response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages = [
        {
            "role": "user",
            "content": "this is a test request, write a short poem"
        }
    ],
    extra_body={ 
        "allowed_openai_params": ["tools"]
    }
)
```

### `allowed_openai_params` — `config.yaml`, per-deployment (verbatim)

```yaml
model_list:
  - model_name: azure-o1-preview
    litellm_params:
      model: azure/o_series/<my-deployment-name>
      api_key: xxxxx
      api_base: https://openai-prod-test.openai.azure.com/openai/deployments/o1/chat/completions?api-version=2025-01-01-preview
      allowed_openai_params: ["tools"]
```

### Per-model proxy config snippets (verbatim, as published)

The two per-model `drop_params` / `additional_drop_params` blocks are published
in this shape (see Claim 10) — bare list fragments with the `model_list:`
wrapper elided and the keys ordered `litellm_params` first. This is valid YAML
(it parses to a one-element list whose item has `litellm_params` and
`model_name` as sibling keys). Column alignment is exactly as rendered:

```yaml
- litellm_params:
    api_base: my-base
    model: openai/my-model
    drop_params: true # 👈 KEY CHANGE
  model_name: my-model
```

```yaml
- litellm_params:
    api_base: my-base
    model: openai/my-model
    additional_drop_params: ["response_format"] # 👈 KEY CHANGE
  model_name: my-model
```

### `additional_drop_params` type contract (verbatim inline definition)

> **additional_drop_params**: List or null - Is a list of openai params you
> want to drop when making a call to the model.

### Introspection helper (verbatim, with the page's source permalink)

> See `litellm.get_supported_openai_params("command-r")`
> [**Code**](https://github.com/BerriAI/litellm/blob/main/litellm/utils.py#L3584)

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/blog-litellm-auto-router-v2.md` — **Cited** (Extends /
  Corroborates, see below): **Claim 9** is the corpus's other `drop_params`
  claim, and it uses the knob as its worked example of alias-level
  `litellm_params` that used to vanish on routed requests.
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **Cited**
  (Extends + layer reconciliation, see below): **Claim 1** (silent
  `stop_sequences` / `top_k` drops) and **Claim 4** (`drop_params` named as the
  proxy-hop escape valve) both describe consequences of the gate this page
  documents.
- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch
  input-file rate limiting, per-record token charging, and
  `batch_enqueued_token_limit`; no request-parameter support gate.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  audio-transcription endpoint config, `mode: audio_transcription` registration,
  and mock-testing fallbacks; no supported-params gate.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed** as a
  cross-reference, but noted as surface adjacency: that note is the *native
  Bedrock Invoke passthrough* route (`POST /bedrock/model/<model_name>/invoke`),
  whereas this page's flagship nested-drop example is the standard
  `bedrock/us.anthropic.claude-sonnet-5` chat-completions model string. Two
  different Bedrock routes; no claim overlap. (The Claude Code + Bedrock
  *client* constraint on this surface is in
  `docs-litellm-claude-code-compatibility.md` Claim 8, cited below.)
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session `max_iterations` / `max_budget_per_session` caps keyed on
  `x-litellm-trace-id`; no parameter drop path.
- `source-notes/docs-litellm-a2a-agent-card.md` — **Dismissed**: agent-card
  field passthrough matrix; unrelated to request-parameter support.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Dismissed**:
  the advisor tool's within-request model composition, `usage.iterations[]`
  advisor-token accounting, and `AdvisorOrchestrationHandler`; no param
  validation surface.
- `source-notes/docs-litellm-gateway-auth-reference.md` — **Dismissed**:
  MCP/A2A outbound `auth_type` and header-parsing conventions; unrelated.
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **Dismissed**:
  `cache_params.type: valkey-semantic` backend selection; unrelated.

**Additional cross-references found by searching `source-notes/` and
`guide/`** (the candidates file was not exhaustive):

- **Corroborates**:
  - `source-notes/docs-litellm-claude-code-context-management.md` **Claim 10**
    — that note's load-bearing sentence is "`drop_params: true` does not disable
    the polyfill. `context_management` is a LiteLLM-supported parameter (native
    on Anthropic, polyfilled elsewhere), and `drop_params` only drops genuinely
    unsupported parameters." This page is the grounding reference for the
    clause that grounds the negation: `drop_params` is gated on the
    provider+model support matrix (Claim 2 here), so a parameter LiteLLM
    *supports* (by polyfilling it) is never a drop candidate — the only opt-out
    is the explicit `additional_drop_params` list, which this page documents as
    the operator-named, support-matrix-independent gate (Claim 4 here). The
    two notes are consistent and mutually completing: that note found the
    negation empirically on a different page, this page supplies the mechanism.
  - `source-notes/blog-litellm-gpt-5-5-day-0.md` **Claim 4** — "LiteLLM
    enforces these caps locally — passing an unsupported value (e.g. `minimal`)
    raises an `UnsupportedParamsError` instead of round-tripping to OpenAI for
    a 400." This page documents the same default-raise polarity as the
    framework's *documented* behavior (Claim 1 here) and names
    `litellm.UnsupportedParamsError` as the error class operators hit — which
    upgrades that note's "the error surface shifts from OpenAI API errors to
    LiteLLM errors" observation from a GPT-5.5-specific enforcement note to a
    general property of the gateway. No conflict.
  - `source-notes/blog-litellm-auto-router-v2.md` **Claim 9** — the fixed bug
    ("`drop_params`, `cache_control_injection_points`, and any other
    `litellm_params` set on the auto router alias itself used to vanish when
    the router picked a tier. They now merge into the outbound request, without
    overriding anything the caller passed explicitly (#32974).") is the
    *placement* half of this page's story: that note establishes that a
    `drop_params` set on a routing alias used to be routed-conditionally
    ignored, and this page establishes what the knob does when it does apply,
    and that its placements have undocumented precedence (Claim 3 here).
- **Contradicts**: None filed, and no self-contradiction in the source. The
  nearest tension is with `docs-litellm-messages-to-responses-mapping.md`
  **Claim 1** ("`stop_sequences` and `top_k` are silently dropped — a caller
  setting them gets a 200 with no error and no telemetry that the constraint
  was ignored") versus this page's default-raise (Claim 1 here). Per MINER
  §4a "when NOT to file," this is a **layer difference, not a claim conflict**:
  the mapping note describes a *wire-format translation adapter* that does not
  map those two fields, while this page describes a *supported-params
  validation gate* keyed on a per-provider-and-model matrix — different
  mechanisms, both true, and the page does not claim the two paths share a
  gate. No contradiction issue filed; the reconciliation and the open
  sub-question are recorded in Extraction Notes. Verified no open
  `contradiction`-labeled issue covers this surface (#1150, #1307, #1322,
  #1338, #1352, #1408, #1461, #1462, #1486 — all routing, A2A, `thinking.summary`,
  advisor-tool, or promptfoo topics) and `CONTRADICTIONS.md` has no `C-NNN`
  entries.
- **Extends**:
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` **Claim 4**
    — that note states the chained-proxy case "would reject it unless
    `drop_params` is set there" without saying what `drop_params` does. This
    page supplies the reference: setting it there is what converts a would-be
    upstream rejection into a silent omission (Claims 1 + 9 here), which is why
    the topology change that adds a proxy hop costs prompt-cache affinity with
    no error surface at all — the two claims compose into a complete story
    about why a topology change is also a cache-behavior change.
  - `source-notes/failure-litellm-vllm-embeddings-encoding-format.md`
    **Claim 4** — that note's remediation is a Python
    `{k: v for k, v in optional_params.items() if v not in (None, '')}`
    filter-to-omit at the shared forwarding boundary, applied specifically in
    the OpenAI-like embedding handler. This page documents the declarative,
    config-level generalization of the same remedy: `additional_drop_params`
    is a named list of params to omit, and its nested syntax reaches *inside*
    objects, so the vLLM-style per-parameter exclusion ("Drop provider-specific
    fields from nested structures", page's own words) becomes one
    `config.yaml` line instead of a code change per handler. **Claim 5** here
    also confirms that note's Chapter-05 framing: the chapter's
    "Provider parity in the shared forwarding path" section
    (guide/05-llm-ops-reliability.md ~L343-374) currently prescribes
    filter-to-omit in Python; this page is the config-level equivalent worth
    recording alongside it.
  - `source-notes/docs-litellm-claude-code-compatibility.md` **Claim 8** —
    that note documents that "Claude Code's Bedrock mode speaks only the
    InvokeModel wire (`/model/{id}/invoke-with-response-stream`) and has no
    Converse-wire client," i.e. the client constrains the gateway surface on
    the Bedrock route. This page's flagship example (Claim 6) is the other half
    of that coupling: the gateway can now *rewrite the client's tool
    definitions in flight* (`tools[*].input_examples`) to fit that route, with
    no client change — so the Claude Code + Bedrock pairing has both a
    documented client-side constraint and a documented gateway-side repair, and
    operators should reach for the latter before patching the client. (Cited
    by section-topic, not as corroboration: that note does not mention
    `input_examples`.)
  - `source-notes/docs-litellm-claude-code-context-management.md` — also the
    source of the **correct** per-model config form. Its Concrete Artifacts
    show a well-formed `model_list:` / `- model_name:` / `litellm_params:` /
    `additional_drop_params: ["context_management"]` block, which is the fuller
    shape to use in place of the page's two wrapper-less snippet fragments
    (Claim 10).
- **Novel**: First corpus coverage of the **parameter-support gate itself** —
  nothing in `source-notes/` or `guide/` documents the gate; the three
  LiteLLM notes that mention `drop_params` do so as an incidental escape valve
  in another claim, and re-verified this session that `allowed_openai_params`
  and `get_supported_openai_params` appear **nowhere** in the corpus. Specifically
  new: the default-raise polarity and its inversion by one boolean; the
  **four documented placements with no stated precedence**; the
  proactive-vs-reactive distinction between `additional_drop_params` and
  `drop_params`; the **JSONPath-like nested-field drop syntax** (six documented
  forms, `tools[*].input_examples`) and its Claude Code + Bedrock use case;
  `allowed_openai_params` as the inverse override and the documented
  `UnsupportedParamsError` remedy, including its per-deployment scope; the
  **absent drop signal** (no documented log/metric/response field); the
  per-provider-**and**-model support-matrix keying with an executable
  introspection call; and the page's inconsistent formatting of its four
  per-model proxy snippets (Claim 10 — recorded as a formatting observation,
  not a corpus-novel fact).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Parameter migration hazards"
  (guide/05-llm-ops-reliability.md ~L327-341)**: The chapter's Rule currently
  says "Parameters valid on earlier models may be silently ignored or
  explicitly rejected" and leaves the branch undetermined. Add the
  determination: on LiteLLM the branch is a **config flag, not a provider
  property** — the documented default is a hard exception, and
  `drop_params` (SDK global, `litellm_settings`, per-request, or per-deployment
  `litellm_params`) flips the whole fleet to silent omission
  [Claim 1] [settled]. Add the concrete pre-migration check the rule has been
  asking for: the support matrix is keyed on provider **and** model, and
  `litellm.get_supported_openai_params("<model>")` is the executable audit
  [Claim 2] [settled] — a single call per candidate model, run *before*
  traffic is routed, instead of inferring support from a provider capability
  table. Add the config-drift rule from Claim 3 [settled]: one boolean, four
  documented placements, no documented precedence, and the two global
  placements (`litellm.drop_params` module attribute, `litellm_settings:
  drop_params: true`) change the failure polarity for *every* model the proxy
  serves — so a global flip should get change-review like a routing change,
  and the auditable placements are the per-deployment and per-request ones.
- **Chapter 05, "Provider parity in the shared forwarding path"
  (~L343-374)**: The section prescribes filter-to-omit **in Python** at the
  shared boundary. Add the declarative counterpart: `additional_drop_params`
  is the config-level form of the same remedy, and its nested syntax
  (`parent.child`, `array[*]`, `array[0]`) reaches fields *inside* objects
  rather than only top-level parameters [Claims 4, 5] [settled] — so a
  provider-specific field that appears in a nested structure is now a
  `config.yaml` line instead of a per-handler code change. Note the corollary
  hazard: a path that matches nothing degrades to "nothing was removed", with
  no error [Claim 5] — the declarative surface inherits the shared-path
  fragility it was meant to remove.
- **Chapter 02 (Observability)**: Add the **absent-signal rule** as a first-class
  entry [Claim 9] [settled-as-documented-absence]: a proxy running
  `drop_params`, any `additional_drop_params` entry, or any nested-path
  rewrite has an *unmonitored parameter surface* — the page documents no log
  line, metric, or response field for a drop, so a caller cannot distinguish
  "param honored" from "param silently stripped," and the two failure branches
  are asymmetric (the loud branch leaves an error, the silent branch leaves
  nothing). The only auditable checks are (a) enumerate the knob across all
  four placements in `config.yaml`, and (b) diff the outbound provider payload.
  This is the same detection conclusion
  `docs-litellm-messages-to-responses-mapping.md` Claim 1 reaches for the
  translation layer — worth stating once, as a rule, for both layers. Flag for
  the Smith that the absence is verified against *this page*; confirming
  whether the gateway emits any drop signal at all is an open follow-up
  against the gateway's logging documentation.
- **Chapter 03 (Runbooks and agents)**: Add the Claude Code + Bedrock
  tool-definition workaround as a runbook step [Claim 6] [settled]: route
  Claude Code at Bedrock and strip `input_examples` with
  `additional_drop_params: ["tools[*].input_examples"]` on the
  `model_name`, using the well-formed `model_list:` form (see the
  snippet-format note below) — no client change required. Two
  preconditions for the runbook, both from the page's silence: the strip is
  unconditional for that deployment (all clients lose the field), and
  verification requires inspecting the outbound provider payload because the
  response carries no marker.
- **Chapter 05, error-surface and monitoring attribution** (pairs with the
  chapter's existing work on silent fallback breaking attribution, ~L972-985):
  add the inverse knob so the `UnsupportedParamsError` class is actionable
  rather than terminal [Claim 7] [settled] — `allowed_openai_params` is the
  documented remedy (`allowed_openai_params=["tools"]` per request via SDK
  `extra_body`, or per-deployment in `config.yaml`), completing
  `blog-litellm-gpt-5-5-day-0.md` Claim 4, which documents the error with no
  remedy. Record the trade honestly: force-passthrough moves a local,
  attributable gateway error to an upstream provider error for every caller on
  that deployment [Claim 8] [settled-scope / Miner-read consequence], so the
  remedy changes *which* monitoring path must be covered, not whether
  monitoring is required.
- **Chapter 05 / any runbook that instructs on `config.yaml`** (minor, no
  action required): when reproducing the per-model `drop_params` /
  `additional_drop_params` forms, use the full `model_list:` shape rather than
  copying the page's fragments verbatim [Claim 10] [settled-cosmetic]. The
  page's two per-model `drop_params` / `additional_drop_params` snippets elide
  the `model_list:` wrapper and order `litellm_params` before `model_name`,
  unlike its nested-field and `allowed_openai_params` snippets. **The blocks
  are valid YAML either way** — this is not a correctness warning and the
  guide needs no change to accommodate it; it is only a note that the
  fragments are not standalone `config.yaml` files.

## Extraction Notes

- Source read in full via WebFetch (markdown) **and** re-fetched with `curl` to
  recover exact code-block line structure, since the markdown pass flattened
  newlines inside fenced blocks. Canonical URL
  `https://docs.litellm.ai/docs/completion/drop_params`, HTTP 200, no
  paywall, no auth. All eleven code blocks and all prose sections were
  extracted; nothing was skipped. No sub-pages followed: the only outbound
  links are the nav siblings `provider_specific_params` and `model_alias`
  (both filed separately as #1481 / #1482 by the same site crawl) and the
  one external permalink into `litellm/utils.py#L3584`, which was **not**
  fetched — this runner has no access to the repository file, so nothing in
  this note is asserted from source code. Claims 3 and 9 are explicitly
  scoped to what the page does and does not say; Claim 10 is scoped to the
  rendered shape of the page's own code blocks.
- All `Quote` fields are character-for-character contiguous fragments from the
  fetched page prose or list items; inner double quotes are escaped as they
  render. No splicing across non-adjacent sentences. Interpreted consequences
  are in `Our assessment`. Claim 9 (absent signal) and Claim 10 (snippet
  formatting) carry `Quote: (no direct quote …)` markers and reproduce the
  evidence verbatim in Concrete Artifacts instead, because their evidence is
  respectively an absence and a code-block shape rather than a sentence.
- **Quote fidelity re-verified this session, including by parsing.** The
  source was re-fetched from `source_url` (HTTP 200) and every `Quote` field in
  the note — all of Claims 1-8 — was checked programmatically against the
  fetched page text: each is present as a contiguous, character-for-character
  fragment (the only normalization needed was accounting for inline `<code>`
  spans, which is how the page renders the backticked tokens in those quotes).
  No quote is spliced across non-adjacent sentences. Separately, the two bare
  list fragments reproduced in Concrete Artifacts were run through a YAML
  parser: both load to a one-element list whose item has `litellm_params` and
  `model_name` as sibling keys, which is why Claim 10 states the snippets are
  valid YAML and the difference between the page's four proxy snippets is
  formatting (key order, elided `model_list:` wrapper) rather than validity.
  The `litellm/utils.py#L3584` permalink remains the one outbound reference
  **not** fetched, and nothing in this note is asserted from source code.
- **Claim 10's confidence grade was re-derived, not carried over.** The claim
  no longer rests on an asserted mechanical defect; it now rests on the
  re-checkable formatting difference between the page's four proxy snippets,
  plus a parse result that is reproducible from the note's own verbatim
  artifacts. It is `settled` for that narrow observation and deliberately
  makes no claim about LiteLLM behavior or config correctness.
- **Layer reconciliation performed, no contradiction filed** (MINER §4a
  when-NOT-to-file): `docs-litellm-messages-to-responses-mapping.md` Claim 1
  documents `stop_sequences` / `top_k` as "❌ Not mapped / Dropped silently" on
  the `/v1/messages`→OpenAI/Azure **translation adapter**; this page
  documents a **supported-params validation gate** that raises by default
  (Claim 1 here). These are two different mechanisms on the request path and
  both can be true simultaneously, so per §4a (claims differ by
  layer/condition) no contradiction issue was filed. **Open sub-question,
  recorded not resolved:** the page does not state whether
  `stop_sequences` / `top_k` on that path are subject to the drop gate at all,
  or whether setting `drop_params` there changes anything — so whether a
  `/v1/messages`→Responses caller can expect a raise or a silent drop is
  genuinely undetermined across the two notes. That is a question for the Smith
  or a future `/provider_specific_params` / `model_alias` source, not a
  contradiction between two claims. Checked all nine open `contradiction`
  issues and `CONTRADICTIONS.md` (no `C-NNN` entries) before deciding.
- **Claim 3 (precedence) and Claim 9 (absent signal) are absence claims and
  were verified by full-page read**, not inferred. Claim 3: the page documents
  four placements across four separate sections and never uses the words
  precedence, override, or "takes priority" in relation to them.
  `blog-litellm-auto-router-v2.md` Claim 9 documents that caller-explicit
  params win over alias-level `litellm_params` for the *merge* it fixed, which
  is adjacent but is not a precedence statement about these four placements —
  not used to fill the gap. Claim 9: the page's ten sections are inventoried in
  the claim; no logging/metrics/response-field mechanism appears.
- Cross-reference verification (MINER §4b): re-read the cited notes and
  confirmed the numbered claims match the cited content —
  `docs-litellm-claude-code-context-management.md` Claim 10 (drop_params
  negation + per-model `additional_drop_params` opt-out) and its per-model
  config artifact; `docs-litellm-messages-to-responses-mapping.md` Claims 1 and
  4; `blog-litellm-auto-router-v2.md` Claims 9 and 10; `blog-litellm-gpt-5-5-day-0.md`
  Claim 4 (`UnsupportedParamsError` local enforcement);
  `failure-litellm-vllm-embeddings-encoding-format.md` Claim 4
  (filter-to-omit remedy) and Claims 1-2 (the incident);
  `docs-litellm-claude-code-compatibility.md` Claim 8 (Claude Code Bedrock
  InvokeModel-only client constraint). All ten `miner-related-notes.md`
  candidates are cited or explicitly dismissed above. No claim numbers
  invented, and the two notes cited by *section topic* rather than claim number
  (`docs-litellm-claude-code-compatibility.md` does not mention
  `input_examples`) are marked as such.
- `confidence_overall` set to `emerging`: the mechanical facts (default
  polarity, the four placements, the syntax table, the three
  `allowed_openai_params` placements, the type contract, the per-model snippet
  formatting) are settled first-party documentation and were verified against
  the rendered page, and the two absence claims were verified by full read. It
  is not `settled` because the whole surface is vendor-documented with no
  independent validation, the page is undated and living, the cited source
  location is a line anchor in a moving file, and three of the highest-value
  conclusions (fleet-wide blast radius of the global placements, the
  `allowed_openai_params` / `drop_params` interaction order, the unreachability
  of verifying a drop signal from this page) are the Miner's readings of
  documented mechanics rather than documented behavior. Consistent with the
  sibling LiteLLM docs notes (#1286, #1359, #1382, #1390, #1445).
- `date_published` unknown (undated living docs page; the page references
  `bedrock/us.anthropic.claude-sonnet-5` and `gpt-5.6-luna`, so it is current
  past the Dec-2025 freshness bar); `date_extracted` and `last_checked` both
  2026-09-27 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain; `miner-related-notes.md` read for candidates and
  left uncommitted.
