---
source_url: https://www.promptfoo.dev/docs/configuration/tools
source_type: docs
title: "Promptfoo Configuration: Tool Calling — Per-Provider Schema Shapes, tool_choice Translation, and Strict-Mode Divergence"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-04
date_extracted: 2026-10-04
last_checked: 2026-10-04
status: current
confidence_overall: emerging
issue: "#1576"
---

# Promptfoo Configuration: Tool Calling

> The first corpus source on promptfoo's **tool-call contract layer**: that
> declaring a tool is a statement of *capability*, not of enforcement (the
> model "doesn't execute anything itself"); that five distinct native
> definition shapes exist and only the nested Chat Completions form is
> portable; that promptfoo **auto-detects** format and *fails open* —
> anything it cannot recognize "pass[es] through unchanged"; that `strict`
> schema enforcement is honored on OpenAI/Anthropic and **silently ignored on
> Bedrock Converse and Google**; and that the `tool_choice` translation is
> lossy in a way that changes test semantics — `'none'` is **omitted** for
> Bedrock, so a "model must not call tools" negative test is not actually
> enforced there.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo's "Configuration >
  Tool Calling" reference page, the `Tool Calling` entry in the
  `/docs/configuration/*` sidebar)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of promptfoo's own config surface and of the
  wire shapes promptfoo claims to emit — authoritative for product syntax,
  and the mapping tables are checkable against an installed CLI or the
  promptfoo source. But it is **vendor-documented with no measured evidence**:
  no eval run, no captured request body, no reproduction of any mapping, and
  no statement that the tables were generated from tests. Every "footgun"
  below is the Miner's reading of documented behavior, not an observed
  incident.
- **Scope**: Covers the tool-calling round trip, the `tools` definition
  surface (five native shapes, field table, JSON Schema in `parameters`,
  `strict` mode), `tool_choice` (four modes, four-provider translation
  matrix), cross-provider reuse via YAML anchors, `file://` tool loading, and
  the HTTP provider's `transformToolsFormat` escape hatch. Does NOT cover the
  *assertion* side of tool calls (`tool-call-f1`,
  `trajectory:tool-args-match` — mined separately as
  `docs-promptfoo-deterministic-metrics.md` Claims 10-12), promptfoo's
  execution of tools (it does not execute them — see Claim 1), or tool-call
  observability/tracing.
- **Last updated**: Oct 4, 2026 (Docusaurus page footer, by `Michael`) — the
  same day as extraction. The page's own examples are on the `gpt-6-sol` /
  `gpt-6-luna` / `claude-sonnet-5` / `gemini-2.5-flash` model generation, so
  the syntax is current-generation.
- **Hub-and-spoke with the HTTP provider page**: this page defers
  `transformToolsFormat` detail to `/docs/providers/http/`, and that page
  links back here for the tool formats. Extraction followed that link (§
  "HTTP Provider with Tools"); one sub-page's material is included below and
  attributed. Following it surfaced a live disagreement between the two pages
  — filed as contradiction **#1593**.

## Extracted Claims

### Claim 1: Tool calling is a four-step loop in which the model emits a name and arguments and executes nothing — the harness (or the application) is the thing that runs code
- **Evidence**: The "How It Works" numbered procedure plus the worked
  transcript artifact (`User: "What's the weather in San Francisco?"` →
  `{ tool: "get_weather", args: {...} }` → `getWeather("San Francisco")` →
  final natural-language response). The page attributes the mapping of name
  to real code to "your application".
- **Confidence**: settled (documented; this is the definitional part of the
  contract)
- **Quote**: "**Model requests a tool call** - The model outputs a function
  name and arguments. This name is an identifier that maps to a function in
  your code—the model doesn't execute anything itself" / "**Your code executes
  the function** - Your application matches the function name to real code
  and runs it with the provided arguments"
- **Our assessment**: Worth stating explicitly because it locates the trust
  boundary that Ch06 cares about. Declaring `get_weather` in a promptfoo
  config does not constrain, sandbox, or authorize anything — it tells the
  model a name exists. promptfoo is an eval harness; it does not run the tool
  either (the docs describe `transformResponse`/`transform` for responses and
  say nothing about executing `tool_calls`). The page is a *contract
  declaration* surface, and a reader must not infer an enforcement boundary
  from it. The corollary for guide writing: an eval that asserts on tool
  *calls* is asserting on the model's request for a capability, never on the
  capability's effect.

### Claim 2: Five distinct native tool-definition shapes exist across providers, and OpenAI/Azure alone has two of them (flat Responses vs nested Chat)
- **Evidence**: The "Tool definitions use different shapes depending on the
  provider and endpoint" table, reproduced in Concrete Artifacts. Only
  `type` and `name` are required; `description`, `parameters`, and `strict`
  are optional.
- **Confidence**: settled (explicit table + field table, documented syntax)
- **Quote**: "Tool definitions use different shapes depending on the provider
  and endpoint:" / "Use the flat Responses format for OpenAI Responses
  requests." / "`type` | string | Yes | Must be `'function'`" / "`name` |
  string | Yes | The function name (used by the model to call it)"
- **Our assessment**: The load-bearing detail is the OpenAI split: the *same
  vendor* has two incompatible shapes, and the docs are explicit that the
  flat `{type, name, parameters}` form is for the **Responses** endpoint. That
  makes "OpenAI tool format" an ambiguous phrase, which is exactly the kind
  of ambiguity that produces misconfigured evals. Note also the Bedrock
  shape's depth — `{ toolSpec: { name, inputSchema: { json } } }` nests the
  schema one level under a doubly-nested wrapper, so any hand-rolled
  Bedrock tool config is a three-level object to get right by eye.

### Claim 3: The nested Chat Completions shape is the documented portable authoring form — promptfoo converts it for Responses, Anthropic, Bedrock, and Google — and cross-provider reuse is done with YAML anchors/aliases, not `$ref`
- **Evidence**: The prose under the native-format table, the "Reusing tools
  between providers" subsection with a three-provider anchor/alias example
  (`&tools` on `openai:gpt-6-luna`, `*tools` aliased on
  `anthropic:claude-sonnet-5` and `google:gemini-2.5-flash`), and the
  YAML-anchors spec the page links.
- **Confidence**: settled (documented syntax; the conversion is asserted, not
  demonstrated)
- **Quote**: "For tools shared across providers, Promptfoo accepts the nested
  Chat Completions format and converts it for Responses, Anthropic, Bedrock,
  and Google." / "An anchor (`&tools`) saves a value, and an alias (`*tools`)
  references it elsewhere:"
- **Our assessment**: Two things worth carrying into the guide. First, the
  *authoring* dialect is a deliberate choice with a documented safe default
  — nested Chat — which is what makes a multi-provider eval matrix possible
  from one tool block. Second, the reuse mechanism is specifically YAML
  anchors, and that matters because the corpus already records that `$ref`
  is **not** dereferenced for provider `tools`/`functions`
  (`docs-promptfoo-configuration-guide.md` Claim 9). So there are two
  different `$ref` layers here and they behave oppositely: config-level
  `$ref` is silently skipped for tool definitions, while JSON-Schema-level
  `$ref`/`$defs` *inside* `parameters` is the page's own documented
  factoring mechanism (Claim 10). A team that reaches for `$ref` out of habit
  at the config layer will get an unresolved schema with no error.

### Claim 4: `strict` schema enforcement is honored on OpenAI, requires Anthropic's *native* tool format, and is **silently ignored** on Bedrock Converse and Google — the same `strict` flag produces different argument-validation behavior per provider column
- **Evidence**: The "Native strict mode support" table under "Strict Mode",
  and — independently, and more bluntly — the `function.strict` row of the
  "Tool Definition Mappings" table, which lists `*(ignored)*` for Anthropic,
  Bedrock Converse, *and* Google on the conversion path.
- **Confidence**: settled as documented behavior (vendor states the
  asymmetry explicitly in two places); the *operational consequence* is the
  Miner's inference, not something the page measures
- **Quote**: "OpenAI | Full support — function arguments match the schema" /
  "Anthropic | Set `strict` in Anthropic's native tool format" / "Bedrock
  Converse/Google | Ignored (not supported)" / "`function.strict` |
  *(ignored)* | *(ignored)* | *(ignored)*"
- **Our assessment**: This is the highest-value claim on the page and the one
  most likely to be load-bearing for Ch05. The divergence is **silent and
  per-column**: the same tool schema, unchanged in the config, is
  schema-enforced when the eval runs against OpenAI and merely
  advisory when it runs against Bedrock or Google. Nothing in the run output
  distinguishes the two. Concretely: a matrix eval whose Bedrock/Google
  columns report green on malformed arguments is not measuring the same
  property as its OpenAI column, and `additionalProperties: false` (required
  for strict mode) buys no enforcement at all on those two backends. The
  Anthropic cell is a second trap inside the trap: it says to set `strict` in
  Anthropic's *native* format, while the Tool Definition Mappings table says
  `function.strict` is *ignored* on the conversion path — i.e. the flag may
  only survive if you hand-write the native shape instead of letting
  promptfoo convert. Both readings cannot be satisfied by one config, and the
  page does not reconcile them; treat `strict` portability as unverified and
  assert argument conformance explicitly (e.g. with a schema-validating
  assertion) rather than trusting the flag to carry it across columns.

### Claim 5: `strict` also flips a default — Responses normalizes schemas into strict mode unless `strict: false` is set explicitly, and `additionalProperties: false` is a hard precondition for strict mode
- **Evidence**: The prose directly under the "Defining Tools" example, the
  inline comment `strict: false # Keep unit optional` in that example, and
  the comment `additionalProperties: false # Required for strict mode` in
  the Strict Mode example. The prose links out to OpenAI's own function-calling
  strict-mode guide for the normalization rule.
- **Confidence**: settled (documented, with the underlying rule delegated to
  the OpenAI docs)
- **Quote**: "The `strict: false` setting preserves optional fields instead
  of letting Responses" / "normalize the schema into strict mode" /
  "`additionalProperties: false # Required for strict mode`"
- **Our assessment**: An *inverted* default is a schema-portability hazard
  that the page states but does not flag: on the Responses endpoint, omitting
  `strict` does not mean "unvalidated" — it means "normalized into strict
  mode", which can change optional fields into required ones. So a tool
  schema authored once and pointed at two OpenAI/Azure endpoints with
  different endpoint types (Responses vs Chat) can change required-ness
  without a config edit. Combined with Claim 4, the practical rule is: pin
  `strict` explicitly on every tool definition, and never rely on its absence
  meaning anything.

### Claim 6: `tool_choice` has four documented modes, and three of the four are *test-design levers* — `none` is documented as an A/B-testing control and the two forcing modes as assertions that the model picked the right function
- **Evidence**: The "Tool Choice > Modes" table plus the `tool_choice`
  examples block (`auto` / `required` / `{type: function, name: get_weather}`
  / `none`) and the framing sentence under the "Tool Choice" heading. The
  config-level default is stated: `auto`.
- **Confidence**: settled (documented behavior)
- **Quote**: "Tool choice controls *when* and *how* the model uses the tools
  you've defined. By default, the model decides on its own whether a tool
  call is appropriate (`auto`)." / "`none` | Model cannot call any tools, even
  if they are defined — useful for A/B testing tool use vs. plain text
  responses" / "`required` | Model must call at least one tool — useful when
  you always expect a structured tool response" / "`{ type: function, name:
  get_weather }` | Model must call the specified tool — useful for testing a
  particular function"
- **Our assessment**: The page frames `tool_choice` as a harness dial, and
  that framing is worth borrowing — but with a methodological caveat the page
  does not state. `tool_choice: {type: function, name: get_weather}` makes
  "did the model call `get_weather`" a **tautology**: the provider is
  instructed to emit that name, so any name-set assertion over it
  (`tool-call-f1`, which per `docs-promptfoo-deterministic-metrics.md`
  Claim 10 does unordered set comparison of tool names) becomes a test that
  cannot fail. Forcing modes belong on *plumbing* checks (is the tool
  reachable, is the schema accepted, does the argument round-trip); tool
  *selection* judgment belongs on `auto`, which is also what the guide already
  prescribes for authorization probes in Ch06 ("Test with the model's
  tool-calling mode set to `auto`"). This source corroborates that Ch06
  choice with the vendor's own framing of `auto` as the default and of the
  forcing modes as "testing a particular function".

### Claim 7: The `tool_choice` translation is lossy and asymmetric — `'required'` becomes Anthropic `{ type: 'any' }` and Bedrock `{ any: {} }`, but `'none'` is **omitted entirely** for Bedrock
- **Evidence**: The "Tool Choice Mappings" table (reproduced in Concrete
  Artifacts), whose `none` row carries an explicit `*(omitted)*` cell for
  Bedrock Converse while the `auto` and `required` rows carry real Bedrock
  values in the same column.
- **Confidence**: settled (explicit table)
- **Quote**: "`'auto'` | `{ type: 'auto' }` | `{ auto: {} }` |
  `{ functionCallingConfig: { mode: 'AUTO' } }`" / "`'none'` |
  `{ type: 'none' }` | *(omitted)* |
  `{ functionCallingConfig: { mode: 'NONE' } }`" / "`'required'` |
  `{ type: 'any' }` | `{ any: {} }` |
  `{ functionCallingConfig: { mode: 'ANY' } }`"
- **Our assessment**: The `required` row is a rename with a semantic edge:
  OpenAI's `required` means "at least one call", Anthropic's `any` is the
  closest equivalent, so the translation is faithful-ish but the operator's
  config vocabulary is not what reaches the provider. The `none` row is the
  real finding. **Omission is not a value** — and this is precisely the
  failure class Ch05 already publishes a rule for under "Provider parity in
  the shared forwarding path": "Present-but-null and omitted are not
  equivalent across 'OpenAI-compatible' backends — how a parameter's absence
  is expressed is a compatibility surface, not an implementation detail." If
  `tool_choice: 'none'` is dropped for Bedrock, the request carries no
  tool-choice directive and the provider applies *its* default, which the
  same page documents as `auto`. So a Bedrock column asserting "the model
  does not call tools" is not testing that at all — it is testing unforced
  behavior under `auto`, and the only way to make the gate fail is to remove
  the tools from the config. Also note the named-function row:
  `{ function: { name } }` becomes `{ tool: { name } }` for Bedrock — i.e. the
  OpenAI wrapper key `function` is renamed to `tool` for Anthropic, which is
  the kind of one-word divergence that a hand-written "just use the native
  shape" config will get wrong in the other direction.

### Claim 8: Format auto-detection gates all translation, and it fails **open** — anything promptfoo does not recognize as OpenAI format "pass[es] through unchanged", with no error
- **Evidence**: The closing sentence of the "Other Provider Formats"
  section, which states both the recognition condition and the fallback. The
  recognition condition is narrow: `type: 'function'` **with** `function.name`.
- **Confidence**: settled (documented; the fail-open behavior is stated as
  design, not as a warning)
- **Quote**: "Promptfoo auto-detects the format. If tools are in OpenAI
  format (`type: 'function'` with `function.name`), they can be transformed.
  Otherwise, they pass through unchanged."
- **Our assessment**: Fail-open is the right default for a pass-through
  provider adapter and the wrong default for a CI gate. Concretely: the flat
  Responses shape `{ type: 'function', name, parameters }` (Claim 2) does
  **not** satisfy the stated recognition condition — it has `name` at the top
  level, not `function.name` — yet the same page documents the flat form as
  the way to define tools. So a flat-Responses tool block aimed at an
  Anthropic built-in provider is, by the page's own stated rule, in the
  "cannot be transformed" branch. The page never says what happens then: no
  error is documented, no warning is documented. The guide-facing rule is
  therefore narrow and mechanical: **author nested Chat Completions for
  anything that is not an OpenAI Responses request**, because nested is the
  one shape both the auto-detector and the documented cross-provider
  conversion path accept. Treat any other shape as a hypothesis to verify
  against a captured request body, not as a supported configuration.

### Claim 9: `transformToolsFormat` is the HTTP provider's escape hatch and it converts **both** `tools` and `tool_choice`; omitting it means pass-through, which is the documented route to a custom or non-standard tool shape
- **Evidence**: Three subsections on the tools page ("OpenAI-Compatible
  Endpoints", "Anthropic-Compatible Endpoints", "Native Format Pass-Through")
  plus the HTTP provider page's "Tool Calling" section, which is where the
  per-provider format table, the `{{ tools }}` / `{{ tool_choice }}` template
  variables, and the guardrails-specific guidance live. The accepted values
  are enumerated as exactly four: `openai`, `anthropic`, `bedrock`, `google`.
- **Confidence**: settled (documented config surface; the emitted wire format
  is asserted, not shown)
- **Quote**: "For custom HTTP endpoints, use the `transformToolsFormat` option
  to automatically convert OpenAI-format tools to the format your endpoint
  expects." / "The `transformToolsFormat` option accepts: `openai`,
  `anthropic`, `bedrock`, or `google`. The `{{ tools }}` and `{{ tool_choice }}`
  template variables are automatically serialized as JSON when injected into
  the request body." / "This is useful when your endpoint expects a custom or
  non-standard tool format."
- **Our assessment**: The escape hatch is correctly scoped — it exists
  precisely for endpoints outside the four built-in dialects — but two
  operational details are easy to miss. First, `transformToolsFormat` mutates
  **`tool_choice` as well as `tools`**, so it is a semantics-changing switch,
  not a serialization switch; the translation it applies is the lossy
  `required`→`any` / `none`-omitted matrix of Claim 7, which means a custom
  gateway can silently inherit the same gap. Second, `{{ tools }}` and
  `{{ tool_choice }}` are *serialized as JSON when injected* — so the body
  template must not quote them, and a body that writes `tools: '{{ tools }}'`
  inside a stringified payload is a double-encoding bug. The HTTP page adds
  the security-relevant detail: format correctness matters when the HTTP
  provider is aimed at a **guardrails** provider, because that is where
  managed tool calls must be parsed correctly by the target — i.e. a tool
  dialect mismatch here degrades into a guardrail that cannot see the calls
  it is supposed to police.

### Claim 10: Tool schemas may live in an external `file://` JSON file, and JSON Schema support inside `parameters` is explicitly provider- and model-dependent with no compatibility table
- **Evidence**: The "Loading Tools from Files" section (config line
  `tools: file://tools/my-tools.json` plus the JSON file body), and the "Full
  JSON Schema Support" section, whose prose states the dependency and then
  demonstrates factoring with `$defs` + `$ref` inside `parameters`.
- **Confidence**: settled for the `file://` mechanism; emerging for schema
  portability (the page states the dependency and then declines to quantify
  it)
- **Quote**: "Tools can be loaded from external files. Use the format
  expected by your endpoint:" / "The `parameters` field contains a JSON
  Schema. Supported keywords depend on the provider and model; this example
  uses a reusable object definition:"
- **Our assessment**: Two Ch05-relevant consequences. (a) `file://` makes the
  tool schema a *separately versioned artifact* shared between the application
  and the eval — good for drift control (the corpus already argues for
  version-pinning eval inputs rather than floating references; see
  `docs-promptfoo-configuration-prompts.md` Claim 3 on why floating labels
  break reproducible gates), and it means a schema change is now a diff
  against the app's contract rather than an inline edit. (b) "Supported
  keywords depend on the provider and model" with no table is an
  unquantified portability dependency: a schema using `$defs`/`$ref` may
  validate on one eval column and be rejected or silently loosened on another.
  The corpus already records the analogous asymmetry for assertion-side
  schema validation (`docs-promptfoo-classifier-grading.md` Claim 5:
  thresholds are label-bound and non-portable). The guide should say the same
  about tool schemas: pin the schema and verify per backend family, and treat
  the eval's schema-validation guarantee as a property of the column, not of
  the suite.

### Claim 11: Model capability gates the tool surface independently of the schema — GPT-6 Sol and Luna require `reasoning_effort: none` for Chat function calls, and Responses is the recommended path for reasoning plus tools
- **Evidence**: The single sentence in the "OpenAI-Compatible Endpoints"
  subsection, immediately above the worked `http://.../v1/chat/completions`
  example, in which `reasoning_effort: none` appears in the body alongside
  `tools: '{{ tools }}'`.
- **Confidence**: settled as documented (vendor states it as a hard
  requirement); anecdotal as an operational rule, since the page gives no
  error message, no observed failure, and no link to a capability table
- **Quote**: "This example targets Chat Completions, so it uses nested
  function definitions. GPT-6 Sol and Luna require `reasoning_effort: none`
  for Chat function calls; use Responses for tool calls with reasoning."
- **Our assessment**: A small claim with a large blast radius, because it
  means the tool schema is not the only thing that decides whether a tool
  call works. A team that switches a working tool-calling eval from Responses
  to Chat Completions — a very natural move when introducing a
  Chat-shaped self-hosted gateway — inherits a hard requirement to also pin
  `reasoning_effort: none`, and the page documents no failure mode for
  forgetting it (no error text, no timeout). The asymmetry it recommends
  (Responses for reasoning + tools, Chat only with reasoning disabled) is the
  kind of thing a guide should state as an explicit constraint table rather
  than leave to per-provider docs. Flagged as anecdotal-leaning because a
  single sentence with no supporting evidence is thin grounding for a hard
  requirement; the guide should attribute it to promptfoo's docs and mark it
  as vendor-asserted, not independently verified.

### Claim 12: Tool-definition field requirements are asymmetric between the flat and nested forms — `type` must be `'function'` and `name` is required, while `description`, `parameters`, and `strict` are all optional
- **Evidence**: The "Fields" table under "Defining Tools", reproduced in
  Concrete Artifacts.
- **Confidence**: settled (documented field contract)
- **Quote**: "`description` | string | No | Description of what the function
  does" / "`parameters` | object | No | JSON Schema defining the function's
  parameters" / "`strict` | boolean | No | Enable strict schema validation"
- **Our assessment**: Small but load-bearing for the Ch03 "structured tool
  contracts" rule. `parameters` being optional means a tool can be declared
  with a name and nothing else — an untyped, argument-free capability that
  still enters the model's action space and still gets a name in the
  `tool_calls` output. That is exactly the "here's a name, figure it out"
  pattern Ch03 argues against for agent-facing interfaces ("A tool schema
  that says 'here's a dict, figure it out' transfers its complexity to every
  agent that calls it"). The vendor's own field table permits it; the guide
  should require `parameters` for any tool an agent may invoke, and note that
  promptfoo will not enforce that for you.

## Concrete Artifacts

### Provider native tool-definition formats
```
Provider                  Native Format
OpenAI/Azure Responses    { type: 'function', name, parameters }
OpenAI/Azure Chat, Groq, Ollama
                           { type: 'function', function: { name, parameters } }
Anthropic                 { name, input_schema }
AWS Bedrock Converse      { toolSpec: { name, inputSchema: { json } } }
Google                    { functionDeclarations: [{ name, parameters }] }
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Configuration"
section table, transcribed as a code block from the rendered table.)*

### Tool definition field contract
```
Field        Type     Required   Description
type         string   Yes        Must be 'function'
name         string   Yes        The function name (used by the model to call it)
description  string   No         Description of what the function does
parameters   object   No         JSON Schema defining the function's parameters
strict       boolean  No         Enable strict schema validation
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Fields".)*

### Cross-provider reuse via YAML anchors and aliases
```yaml
providers:
  - id: openai:gpt-6-luna
    config:
      tools: &tools # Anchor: define tools once
        - type: function
          function:
            name: get_weather
            description: Get current weather for a location
            parameters:
              type: object
              properties:
                location: { type: string }
              required: [location]
  - id: anthropic:claude-sonnet-5
    config:
      tools: *tools # Alias: reuse the same tools
  - id: google:gemini-2.5-flash
    config:
      tools: *tools # Alias: works here too
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Reusing tools
between providers" — reproduced with line breaks and indentation restored
from the page's single-line code block.)*

### Strict mode, and the required `additionalProperties: false`
```yaml
tools:
  - type: function
    name: get_weather
    strict: true # Require function arguments to match the schema
    parameters:
      type: object
      properties:
        location:
          type: string
      required: [location]
      additionalProperties: false # Required for strict mode
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Strict Mode".)*

### JSON Schema factoring with `$defs` / `$ref` inside `parameters`
```yaml
tools:
  - type: function
    name: complex_function
    strict: false # Keep tags optional
    parameters:
      type: object
      properties:
        coordinates:
          $ref: '#/$defs/coordinate'
        tags:
          type: array
          items:
            type: string
          minItems: 1
      required: [coordinates]
      $defs:
        coordinate:
          type: object
          properties:
            lat:
              type: number
              minimum: -90
              maximum: 90
            lon:
              type: number
              minimum: -180
              maximum: 180
          required: [lat, lon]
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Full JSON Schema
Support". Note this is JSON-Schema-level `$ref`, inside `parameters` — not
the config-level `$ref` that `docs-promptfoo-configuration-guide.md` Claim 9
records as not dereferenced for `tools`/`functions`.)*

### `tool_choice` modes
```
Value                                 Description
auto                                  Model decides whether to call a tool based on the prompt (default)
none                                  Model cannot call any tools, even if they are defined — useful for
                                      A/B testing tool use vs. plain text responses
required                              Model must call at least one tool — useful when you always expect a
                                      structured tool response
{ type: function, name: get_weather }  Model must call the specified tool — useful for testing a particular function
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Tool Choice > Modes".)*

### `tool_choice` examples
```yaml
# Let the model decide
tool_choice: auto

# Force the model to use tools
tool_choice: required

# Force a specific tool
tool_choice:
  type: function
  name: get_weather

# Disable tools for this request
tool_choice: none
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Tool Choice >
Examples".)*

### Chat Completions → provider tool-definition mapping (built-in providers)
```
Chat Completions Field    Anthropic        Bedrock Converse              Google
function.name             name             toolSpec.name                  functionDeclarations[].name
function.description      description      toolSpec.description           functionDeclarations[].description
function.parameters       input_schema     toolSpec.inputSchema.json      functionDeclarations[].parameters
function.strict           (ignored)        (ignored)                      (ignored)
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Provider
Transformations > Tool Definition Mappings".)*

### Chat Completions → provider `tool_choice` mapping (built-in providers)
```
Chat Completions                       Anthropic             Bedrock Converse                        Google
'auto'                                { type: 'auto' }       { auto: {} }                            { functionCallingConfig: { mode: 'AUTO' } }
'none'                                { type: 'none' }       (omitted)                              { functionCallingConfig: { mode: 'NONE' } }
'required'                            { type: 'any' }        { any: {} }                             { functionCallingConfig: { mode: 'ANY' } }
{ type: 'function', function: { name } }  { type: 'tool', name }  { tool: { name } }                   { functionCallingConfig: { mode: 'ANY', allowedFunctionNames: [...] } }
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Tool Choice
Mappings". NOTE: the HTTP provider page's parallel table shows `—` instead of
`{ type: 'none' }` for Anthropic on the `'none'` row — filed as
contradiction **#1593**.)*

### Native-format pass-through (no conversion, no auto-detection)
```yaml
providers:
  - id: http://localhost:8080/v1/messages
    config:
      method: POST
      headers:
        Content-Type: application/json
        # No transformToolsFormat - tools pass through as-is
      body:
        model: claude-sonnet-5
        messages: '{{ prompt }}'
        tools: '{{ tools }}'
      tools:
        # Native Anthropic format with input_schema
        - name: get_weather
          description: Get weather for a location
          input_schema:
            type: object
            properties:
              location:
                type: string
            required:
              - location
```
*(Attribution: promptfoo docs /docs/configuration/tools, "HTTP Provider with
Tools > Native Format Pass-Through".)*

### HTTP provider, OpenAI-compatible endpoint with `transformToolsFormat`
```yaml
providers:
  - id: http://localhost:8080/v1/chat/completions
    config:
      method: POST
      headers:
        Content-Type: application/json
      transformToolsFormat: openai # Tools already in OpenAI format, pass through
      body:
        model: gpt-6-sol
        reasoning_effort: none
        messages: '{{ prompt }}'
        tools: '{{ tools }}'
        tool_choice: '{{ tool_choice }}'
      tools:
        - type: function
          function:
            name: get_weather
            description: Get weather for a location
            parameters:
              type: object
              properties:
                location: { type: string }
      tool_choice: required
```
*(Attribution: promptfoo docs /docs/configuration/tools, "HTTP Provider with
Tools > OpenAI-Compatible Endpoints".)*

### Tools loaded from an external file
```yaml
providers:
  - id: openai:gpt-6-sol
    config:
      tools: file://tools/my-tools.json
```
```json
[
  {
    "type": "function",
    "name": "get_weather",
    "description": "Get current weather",
    "parameters": {
      "type": "object",
      "properties": {
        "location": { "type": "string" }
      }
    }
  }
]
```
*(Attribution: promptfoo docs /docs/configuration/tools, "Loading Tools from
Files".)*

### From the linked sub-page: `transformToolsFormat` target per provider
```
Anthropic → anthropic        Google AI Studio → google
AWS Bedrock → bedrock        Google Vertex AI → google
Azure OpenAI → openai        Groq → openai
Cerebras → openai            Ollama → openai
DeepSeek → openai            OpenAI → openai
Fireworks AI → openai        OpenRouter → openai
Perplexity → openai          Together AI → openai
xAI (Grok) → openai
```
*(Attribution: promptfoo docs /docs/providers/http/, "Tool Calling >
transformToolsFormat", 16-provider table, extracted per MINER.md §1
sub-page following. Companion prose: "Use `openai` or omit for
OpenAI-compatible APIs where no conversion is needed.")*

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-configuration-guide.md` **Claim 9** — config-level `$ref`
    is not dereferenced for provider `tools`/`functions` ("tools and
    functions values in providers config are not dereferenced. This is because
    they are standalone JSON schemas that may contain their own internal
    references."). This note supplies the other half of that distinction:
    JSON-Schema-level `$ref`/`$defs` *inside* `parameters` is the page's own
    documented factoring mechanism (Claim 3, Claim 10), so the two `$ref`
    layers behave oppositely and a team must not generalize from one to the
    other.
  - `docs-promptfoo-configuration-guide.md` **Claim 1** and **Claim 3** —
    the transform vocabulary (`transformResponse` as a provider-stage
    rewrite) generalizes: `transformToolsFormat` is the request-side
    counterpart, and both are provider-stage transforms that run before an
    assertion ever sees the value.
  - `docs-litellm-messages-to-responses-mapping.md` **Claim 7** — the
    comparison baseline the triage named, and the mirror image of Claim 7
    here: LiteLLM's Anthropic→OpenAI direction remaps `tool_choice: "any"` to
    `{"type": "required"}`, while promptfoo's OpenAI→Anthropic direction maps
    `required` to `{ type: 'any' }`. Same vocabulary, different direction,
    and in both cases the translation is a semantic rewrite rather than a
    rename — corroborating this note's assessment that `tool_choice` is a
    semantics-changing surface, not a formatting one.
  - `docs-promptfoo-configuration-prompts.md` **Claim 3** — the corpus's
    established rule that eval inputs must be pinned to explicit versions for
    CI gates to be reproducible (floating external-registry labels break the
    green/red signal). This note extends it to the tool-definition surface,
    where `file://tools/my-tools.json` makes the schema a separately
    versioned artifact (Claim 10).
  - `docs-promptfoo-deterministic-metrics.md` **Claim 10** — `tool-call-f1`
    scores unordered tool-name sets only. Read together with Claim 6, this is
    the basis for the tautology warning: forcing `tool_choice` to a named
    function and then asserting on the tool-name set tests the harness, not
    the model. Claim 12 of that note (trace-family assertions *throw* when
    trace data is absent) is the complementary fail-loud precedent against
    which this page's fail-open format detection (Claim 8) reads as the
    outlier.
  - `docs-litellm-completion-function-call.md` **Claim 5** — LiteLLM's
    `tool_choice` is silently discarded on the path where its function-call
    fallback applies, with the docs not saying so. promptfoo's ignored
    `function.strict` on the conversion path (Claim 4) and omitted `'none'`
    for Bedrock (Claim 7) are the same class: a tool parameter that reaches
    some backends and not others, invisibly.
- **Contradicts**:
  - **#1593** (filed with this PR, via `.github/ISSUE_TEMPLATE/contradiction.yml`)
    — **promptfoo contradicts itself across two pages on `tool_choice:
    'none'` → Anthropic.** Side A: this page's "Tool Choice Mappings" table
    maps `'none'` to `{ type: 'none' }` for Anthropic and marks Bedrock
    `*(omitted)*`. Side B: the linked sub-page
    (https://www.promptfoo.dev/docs/providers/http/, "Why tool_choice needs
    transformation") shows `—` for both Anthropic and Bedrock on the `"none"`
    row, i.e. no Anthropic representation at all. Both tables claim to be the
    authoritative translation matrix, and the two pages link to each other.
    Verdict is deliberately **not** picked here; see #1593 and
    CONTRADICTIONS.md. Guide-facing consequence until resolved: treat
    `tool_choice: 'none'` against an Anthropic endpoint as **unverified in
    both directions** — do not write it into a gate until the wire format is
    confirmed from a captured request body or the promptfoo source.
  - No conflict with an existing *source note* in the corpus. Related but not
    contradictory: `docs-litellm-drop-params.md` and
    `docs-litellm-completion-input-params.md` record LiteLLM-side omission
    and exemption lists on the same parameter family; those concern LiteLLM's
    gateway, not promptfoo's harness.
- **Extends**:
  - `docs-promptfoo-configuration-guide.md` (#1513) — the hub page that links
    to this one and defers the tool-calling surface entirely; this note fills
    the tool-definition/`tool_choice` slice the hub never states, and gives
    Claim 9's `$ref`-not-dereferenced caveat its positive counterpart.
  - `docs-promptfoo-deterministic-metrics.md` — owns the *assertion* side of
    tool calls; this note owns the *declaration/export* side. Together they
    are the full tool-call contract in promptfoo (declare → choose → call →
    assert), and the gap between them is where Claim 6's tautology lives.
  - `docs-promptfoo-configuration-prompts.md` (#1544) — sibling page in the
    same config family, same vendor-credibility caveat, and the same
    pattern of a documented surface that hides an operational trap (there,
    `exec:` script permissions; here, fail-open format detection).
  - `docs-litellm-messages-to-responses-mapping.md` — gateway-side
    translation baseline; the two notes now cover both directions of the
    same translation problem (gateway-side and harness-side).
- **Novel**:
  - The first corpus source on promptfoo's tool/function-calling
    configuration at all — no prior note covers `tools:`, `tool_choice:`,
    `strict`, or `transformToolsFormat` for promptfoo (the triage comment
    confirms this, and a corpus-wide search for `tool_choice|toolSpec|
    input_schema|functionDeclarations|transformToolsFormat` returns only
    LiteLLM/Langfuse notes).
  - The **`strict`-mode support asymmetry** (honored on OpenAI, requires
    Anthropic's native shape, silently ignored on Bedrock Converse and
    Google) and the **`function.strict` → `*(ignored)*` row** on the
    conversion path. Nothing in the corpus records schema-enforcement
    portability as a per-provider axis of an eval harness.
  - The **fail-open auto-detection rule** ("If tools are in OpenAI format
    (`type: 'function'` with `function.name`), they can be transformed.
    Otherwise, they pass through unchanged") and the resulting gap that the
    flat Responses shape does not satisfy the stated recognition condition.
  - The **`'none'` → `*(omitted)*`** translation for Bedrock Converse, i.e.
    a documented case where promptfoo expresses a parameter's absence
    differently per provider — the exact failure class Ch05 publishes a rule
    for, now evidenced on the harness side.
  - The `transformToolsFormat`-must-also-be-set-for-guardrails-providers note
    from the linked sub-page, which makes a tool-dialect mismatch a
    *guardrail-visibility* problem rather than a cosmetic one.

## Guide Impact

- **Chapter 05 (llm-ops-reliability) — §Provider parity in the shared
  forwarding path**: add promptfoo as a second, harness-side instance of the
  rule already published from the vLLM embedding failure. The chapter's
  existing sentence — "Present-but-null and omitted are not equivalent across
  'OpenAI-compatible' backends" — generalizes directly to promptfoo's
  `tool_choice` matrix: `'none'` → `{ type: 'none' }` for Anthropic but
  **omitted** for Bedrock (Claim 7). Recommend a concrete addition: a
  negative tool test (`tool_choice: none`) is only enforced on backends whose
  native form expresses it; on Bedrock the request carries no directive and
  the provider applies the default the same page documents as `auto`, so the
  gate must instead remove the tool from the config to make it fail.
- **Chapter 05 — §Evaluation and measurement methodology**: two additions.
  (a) Under "read the assert's own defaults"/gate design, record that
  `strict` is a **per-column** property, not a suite property: the same tool
  schema is argument-enforced on OpenAI and advisory on Bedrock/Google with
  no signal in the run output (Claim 4), so a green multi-provider matrix does
  not mean the same thing in every column — assert argument conformance
  explicitly instead. (b) Note that forcing `tool_choice` to a named function
  and then asserting on the tool-name set is a test that cannot fail
  (Claim 6 + `docs-promptfoo-deterministic-metrics.md` Claim 10's unordered
  name-set comparison); forcing modes belong on plumbing checks, and tool
  *selection* judgment must be measured under `auto`.
- **Chapter 05 — §Test in the environment you ship / parameter migration
  hazards**: add the `reasoning_effort: none` requirement for GPT-6 Sol/Luna
  Chat function calls (Claim 11) to the parameter-migration hazard list —
  switching a tool-calling eval from Responses to a Chat-shaped gateway also
  requires pinning reasoning off, and promptfoo documents no failure mode for
  forgetting it. Attribute as vendor-asserted.
- **Chapter 03 (runbooks-and-agents) — §Structured tool contracts over
  free-form interfaces**: the promptfoo field table makes `parameters`
  optional (Claim 12), so a tool can be declared as a bare name and still
  enter the model's action space. Recommend the guide require `parameters` on
  any tool an agent may invoke, and note explicitly that promptfoo enforces
  nothing here. Also add the Ch03-adjacent Ch06 framing from Claim 1: a
  declared tool is a capability advertisement; the harness (not promptfoo) is
  what executes it, so schema declaration is not an authorization control.
- **Chapter 06 (security-and-trust) — §Function-calling authorization**: this
  source corroborates the chapter's existing "set tool-calling mode to `auto`"
  instruction with the vendor's own framing — `auto` is the documented
  default, and the forcing modes are documented as "testing a particular
  function" (Claim 6). Add the sub-page's guardrails note (Claim 9): when the
  HTTP provider targets a guardrails endpoint, `transformToolsFormat` governs
  whether managed tool calls are parseable at all, so a dialect mismatch
  degrades into a guardrail that cannot see the calls it is meant to police —
  a silent monitoring gap, not a config error.
- **New material worth a guide-level rule, all from this source**: author
  tools in the nested Chat Completions shape for anything that is not an
  OpenAI Responses request (Claims 2, 3, 8), because nested is the only shape
  the auto-detector and the documented cross-provider conversion both accept,
  and unrecognized shapes fail *open* ("pass through unchanged") with no
  error (Claim 8).

## Extraction Notes

- Read https://www.promptfoo.dev/docs/configuration/tools in full on
  2026-10-04 (no paywall, no truncation; page footer: "Last updated on
  Oct 4, 2026"). Followed the page's own outbound link to
  https://www.promptfoo.dev/docs/providers/http/ per MINER.md §1 sub-page
  rule — it is where `transformToolsFormat`'s per-provider format table, the
  `{{ tools }}` / `{{ tool_choice }}` template-variable contract, and the
  guardrails note live. Material from that sub-page is attributed inline and
  in Concrete Artifacts; it is the source of Claim 9's second half and of the
  "From the linked sub-page" artifact. Did not follow the other four
  provider-specific links (`/docs/providers/openai/`, `/anthropic/`,
  `/aws-bedrock/`, `/google/`, `/custom-api/`) — they are provider
  documentation, not this page's claim surface, and the mapping tables here
  are what the guide needs.
- **Contradiction filed**: #1593, opened before this PR per MINER.md §4a,
  using `.github/ISSUE_TEMPLATE/contradiction.yml`, labeled `contradiction`
  + `needs-resolution`. Verified it is not already covered: no open
  `contradiction`-labeled issue concerns promptfoo `tool_choice`, and
  CONTRADICTIONS.md has no entries. No verdict is picked in this note.
- **Quote hygiene** (MINER.md §2a): every `Quote` is copied from the page.
  Two provenance notes for the Assayer's spot-check. (a) Two claims (5 and 8
  and the Claim 4 quotes) quote table cells / code comments, which are
  verbatim but were rendered as markdown tables and code blocks — the
  transcription into Concrete Artifacts preserves the cell content and
  re-wraps it. (b) In Claim 5 the sentence "The `strict: false` setting
  preserves optional fields instead of letting Responses normalize the schema
  into strict mode." is broken by an inline hyperlink on the words "normalize
  the schema into strict mode" in the source. The two adjacent fragments are
  quoted separately rather than spliced, per §2a rule 3; the rendered page
  reads as one continuous sentence.
- **Candidates file** (`miner-related-notes.md`, present at repo root; not
  committed): 10 candidates retrieved. Cited: #6
  `docs-promptfoo-configuration-guide.md` (Corroborates Claim 9 / Extends).
  Dismissed with reason: #1 `docs-google-sre-team-lifecycles.md` (SRE org
  design and hiring — no tool-contract content), #2
  `docs-promptfoo-pi-scorer.md` (model-graded scorer surface, unrelated to
  tool declaration), #3 `docs-langfuse-mcp-server.md` (docs-MCP transport and
  client config), #4 `docs-google-sre-prodcast-04-09-ai-agents.md`
  (agent-capability concepts; conceptually adjacent to Claim 1's
  read/write boundary but already mined and cited on its own terms, and its
  claims are about granting capabilities to agents rather than declaring a
  schema), #5 `blog-promptfoo-owasp-red-teaming.md` (red-team process; no
  tool-call contract), #7 `docs-litellm-batches-api.md` (batch rate limiting),
  #8 `blog-pagerduty-sre-agent-triage.md` (SRE triage workflow), #9
  `docs-promptfoo-classifier-grading.md` (its Claim 5 non-portable-threshold
  *principle* is analogous and is referenced in Claim 10's assessment, but it
  is a different surface — assertion thresholds, not tool schemas — so it is
  deliberately not listed under Cross-References as corroboration), #10
  `docs-promptfoo-javascript-assertions.md` (custom-JS gate semantics;
  fail-closed behavior there contrasts with this page's fail-open detection,
  but that contrast is drawn in Claim 8's assessment via
  `docs-promptfoo-deterministic-metrics.md` Claim 12, which is the closer
  precedent).
- Beyond the candidates file, a corpus-wide search for
  `tool_choice|toolSpec|input_schema|functionDeclarations|transformToolsFormat`
  over `source-notes/` was run to check the "no prior note covers promptfoo
  tools" claim; every hit is LiteLLM- or Langfuse-side, confirming Novel.
- Credibility caveat applied per the triage instruction: vendor documentation
  only — no measured evidence, no eval traces, no incident data. Syntax and
  mapping claims marked `settled` as documented intent; the strict-mode
  divergence, the `'none'` omission, the fail-open detection, and the
  `reasoning_effort` requirement are all marked with their evidentiary status
  in-line and flagged as vendor-asserted where no supporting measurement
  exists. `confidence_overall: emerging`, matching the sibling promptfoo
  configuration notes.
