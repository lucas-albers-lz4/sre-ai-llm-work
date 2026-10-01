---
source_url: https://www.promptfoo.dev/docs/configuration/guide
source_type: docs
title: "Promptfoo Configuration: Overview — Transform Pipeline, Assertion Inheritance, and Env Resolution"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-30
date_extracted: 2026-09-30
last_checked: 2026-09-30
status: current
confidence_overall: emerging
issue: "#1513"
---

# Promptfoo Configuration: Overview

> The hub page every mined promptfoo subpage links back to — the first
> corpus source on the **order** in which promptfoo rewrites an output
> before an assertion sees it (provider `transformResponse` first, then
> test/`contextTransform`, then the assertion's own `transform`), on the
> **override-not-compose** rule for `defaultTest` transforms, on the
> per-test `options.disableDefaultAsserts` escape hatch that silently
> drops an inherited baseline assertion, and on `{{ env.* }}` being
> resolved at *config load time* with a vendor warning that
> `config.env` secrets "may appear in exported results."

## Source Context

- **Type**: docs (vendor product documentation — promptfoo's top-level
  "Configuration" guide page, the hub the whole `/docs/configuration/*`
  family links back to)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team
  vendor. First-party documentation of the tool's own config-organization
  and evaluation-order semantics — authoritative for promptfoo product
  behavior, and directly checkable against an installed CLI, but
  vendor-documented with **no measured evidence**: no trace of an eval, no
  pass/fail outcome, no reproduction of any ordering or inheritance rule
  in action. Every "trap" below is the Miner's reading of documented
  behavior, not an observed incident.
- **Scope**: Covers how the YAML config composes — assertions and their
  optionality, `providers`/`tests`/`vars` file+glob loading, scripted
  (dynamic) vars and PDF vars, `defaultTest` (assertions, vars, external
  file), `$ref`/`assertionTemplates`, cartesian expansion of array vars,
  Nunjucks templating (objects, escaping, composition, `env`), thinking
  output, the output-transform pipeline (`transformResponse`,
  `options.transform`, `contextTransform`, assertion-level `transform`,
  `transformVars`), multi-config runs, and CSV / Google Sheets / Azure
  Blob test sets. Does NOT cover what any assertion *type* means (each
  has its own mined note), caching (`/docs/configuration/caching/`,
  note #1275), or provider-side request options beyond the three
  `transformResponse` / thinking examples.
- **Last updated**: Sep 30, 2026 (Docusaurus page footer, by
  `mldangelo-oai`) — same day as extraction, so this is current
  documentation, and the page's own examples are on the `gpt-6-luna` /
  `claude-sonnet-5` model generation.
- **Hub page, not a spec**: the page deliberately restates basics
  ("Assertions are optional. Many people get value out of reviewing
  outputs manually, and the web UI helps facilitate this.") and delegates
  depth to linked pages. That is why the ordering rules it *does* state —
  which ~35 already-mined promptfoo subpages all assume but none state —
  are the load-bearing content here.

## Extracted Claims

### Claim 1: Transforms are a fixed three-stage pipeline — provider `transformResponse` runs first, test `options.transform` and `contextTransform` both receive that already-transformed output, and the assertion's own `transform` runs on the *test-transformed* value
- **Evidence**: The "Transforming outputs" section's "Transform execution
  order" bullet list on this page, plus its worked assertion-level example
  (`transform: output.category`). The three-stage order is completed by
  the linked Configuration Reference page, whose "Transformation Pipeline"
  section's "Key Points" list adds step 3 and whose RAG worked example
  annotates each stage inline ("Step 3: Assertion-level transform
  (applied after test transform)").
- **Confidence**: settled (documented product behavior; ordering is
  checkable by reading an eval trace)
- **Quote**: "Provider transforms (transformResponse) - Always applied
  first" / "Test transforms (options.transform) and Context transforms
  (contextTransform)" / "Both receive the output from the provider
  transform" / "Test transforms modify the output for assertions" /
  "Context transforms extract context for context-based assertions (e.g.,
  context-faithfulness)". (Linked Configuration Reference page, verbatim:
  "Assertion Transform: Applied to already-transformed output for specific
  assertions".)
- **Our assessment**: This is the highest-value line on the page and it
  is genuinely new to the corpus: **no existing note states the order.**
  `docs-promptfoo-guardrails-assertions.md` has a worked
  `transformResponse` example; the `context-recall`/`context-faithfulness`
  notes have `contextTransform` examples. Neither tells a reader what
  their assertion actually receives. The practical consequence: an
  assertion's input is *not* the model's raw output — it is
  `transformResponse` → `options.transform` → assertion `transform`, and
  a transform that throws, truncates, or coerces a field silently
  redefines what the gate measures while the config still reads as a
  check on model behavior. The two branch fields (`options.transform`
  for regular assertions vs `contextTransform` for context assertions)
  both starting from the provider-transformed output is the part teams get
  wrong: writing `transform: output.answer` and expecting
  `context-faithfulness` to see the same string.

### Claim 2: At the test-case level exactly one transform applies — `defaultTest`'s or the individual case's, never both; a per-case transform **overrides** the suite-level one rather than composing with it
- **Evidence**: The "Test transform hierarchy" subsection's two bullets
  plus its explicit `Note that`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Individual test case transforms (overrides defaultTest
  transform if present)" and "Note that only one transform is applied at
  the test case level - either from defaultTest or the individual test
  case, not both."
- **Our assessment**: Buy it, and flag it as the page's sharpest trap:
  **zero hits for this rule across the 215-file corpus.** The failure
  mode is silent and asymmetric. A suite-level `defaultTest.options.transform`
  (e.g. unwrap JSON, strip a known prefix) is the natural place to put
  shared output hygiene; the first engineer who needs something slightly
  different on one case adds `options.transform` there, and from that
  moment the suite-wide transform stops running for that case. Nothing
  errors. If the suite transform is load-bearing (e.g. it strips
  chain-of-thought before a `not-contains` guardrail check, or maps a
  provider envelope to the field under test), that case is now graded
  against a *different* input than every other case, and the eval
  report shows one verdict per case with no marker of the divergence.
  Note this is a **conditioning-variable** asymmetry, not a bug to file:
  the behavior is documented and deliberate. The guide's job is to say
  *if you need both, chain them inside one function*, because the
  override semantics mean the obvious composition silently doesn't
  happen.

### Claim 3: `options.transform` is a JS snippet (or external file) with a documented `(output, context)` signature and a closed context surface — `prompt.{id,raw,display}`, `vars`, `metadata` — and the same `transform` field on an assertion selects a sub-field out of JSON output
- **Evidence**: The "Transforms from separate files" and
  "It also works in assertions" subsections, the inline `transformFn`
  TypeScript signature block, and the `transform: output.category`
  example.
- **Confidence**: settled (documented product behavior, with a typed
  signature)
- **Quote**: "The TestCase.options.transform field is a Javascript
  snippet that modifies the LLM output before it is run through the test
  assertions." and "It is a function that takes a string output and a
  context object:"
- **Our assessment**: Useful as a *contract* claim. Three things worth
  keeping: (a) `prompt.raw` is documented as "Raw prompt as provided in
  the test case, without `{{variable}}` substitution" while
  `prompt.display` is "Prompt as sent to the LLM API and assertions" —
  so a transform that re-renders or re-substitutes a prompt cannot read
  the substituted form back, and a transform that *asserts on* the prompt
  is reading a different string than the model saw; (b) the transform
  receives `vars`, so it can be var-dependent (per-language
  normalization) — which interacts with Claim 2's override rule, since a
  var-dependent transform is exactly the kind of case that gets added
  per-case and silently unhooks the suite default; (c) assertion-level
  `transform` means two assertions on the same test case can read
  **different** values of the same response, so a passing suite is not
  evidence that one output satisfied all its checks in one form.
  The signature returns `void` yet the multiline example `return`s a
  value — a small documentation inconsistency worth noting rather than
  resolving.

### Claim 4: `transformVars` is a distinct *input-side* transform whose returned keys are merged into `vars` and can override existing keys, set suite-wide under `defaultTest.options` or per test case
- **Evidence**: The "Transforming input variables" section, its
  suite-wide example (adding `uppercase_topic`, `topic_length`,
  `processed_content` consumed by the prompt template) and its per-case
  example (`{ ...vars, image_markdown: ... }`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can also transform input variables before they are used
  in prompts using the transformVars option. This feature is useful when
  you need to pre-process data or load content from external sources." and
  "The transformVars function should return an object with the
  transformed variable names and values. These transformed variables are
  added to the vars object and can override existing keys."
- **Our assessment**: New to the corpus (`transformVars`: **zero hits**
  across all 215 source notes) and it is the input-side twin of the
  output transforms, so the guide's pipeline story is incomplete without
  it. The "can override existing keys" clause is the sharp edge: a
  `transformVars` that spreads `{ ...vars, ... }` and then recomputes a
  key the test case also set will silently win, and because the override
  happens before templating, the *prompt* changes — not just the grading
  input. Contrast with Claim 1/2: `transformVars` has **no documented
  override/hierarchy note at all** on this page (the hierarchy rule is
  stated only for output transforms), so whether a per-case
  `transformVars` overrides or merges with `defaultTest.options.transformVars`
  is undocumented here. Flagging that as an open question rather than
  asserting behavior.

### Claim 5: The documented `transformVars` error convention is *return an error object*, not throw — and the docs state no behavior for what the harness does with it
- **Evidence**: The `transformVars.js` worked example wraps its body in
  `try/catch`, logs, and returns `{ error: 'Failed to transform variables' }`;
  the dynamic-var examples on the same page document the parallel
  `// return { error: 'Something went wrong' };` convention.
- **Confidence**: emerging (the convention is documented; the *outcome*
  is not)
- **Quote**: (config block, verbatim from "Input transforms from
  separate files") "console.error('Error in transformVars:', error);" /
  "return {" / "  error: 'Failed to transform variables'," / "};"
- **Our assessment**: Do not buy any implied fail-closed semantics. The
  docs document a *return channel*, not an outcome: nothing on this page
  (nor on the linked Test Cases / Configuration Reference pages) says
  whether a returned `error` key fails the test case, fails the whole
  eval, becomes a zero-scored result, or is ignored — and an ignored key
  would leave the prompt with a missing variable (nunjucks renders
  undefined as empty), producing a degraded prompt that still grades.
  This is the same shape as open contradiction issue **#1307**
  ("custom-JS trace gate passes green when tracing is off"): a
  documented-in-code negative path with no documented harness reaction.
  The cheap, testable hypothesis for the Smith: assert on a suite whose
  `transformVars` deliberately throws, and record whether the gate goes
  red. Until that is measured, treat "a returned `{error}` fails the
  case" as unverified, and put it in the guide's *verify-before-you-trust*
  list rather than as a rule.

### Claim 6: `defaultTest.assert` inheritance has a documented per-test opt-out — `options.disableDefaultAsserts: true` drops the inherited assertions while `vars`, `metadata`, `threshold`, and `options` still apply
- **Evidence**: The "Default test cases" subsection's paragraph plus its
  worked config; the linked Configuration Reference's Test Case `options`
  table row for `disableDefaultAsserts`.
- **Confidence**: settled (documented product behavior; stated twice,
  prose plus reference table)
- **Quote**: "Set options.disableDefaultAsserts: true on a test case when
  that test should define its own assertions without inheriting
  defaultTest.assert. Other defaultTest fields, such as vars, metadata,
  threshold, and options, still apply:" (Linked Configuration Reference
  page, verbatim: "If true, this test case does not inherit assertions
  from defaultTest.assert; other defaultTest properties still apply".)
- **Our assessment**: The cleanest green-gate trap on the page, and new
  to the corpus (`disableDefaultAsserts`: **zero hits**). The mechanism
  is legitimate — a case with its own assertions shouldn't also inherit
  a suite rubric — but the *scoping* is per test case with no other
  guard, so the cases most likely to carry the flag are the ones an
  author found awkward, which are usually the nuanced ones. A suite whose
  `defaultTest.assert` holds the "does not describe self as an AI"
  rubric (this page's own example) silently loses that rubric on exactly
  the flagged cases, and the eval report shows those cases as fully
  asserted. The mitigating detail worth keeping in the guide: the opt-out
  is scoped to `assert` only, so `defaultTest.vars` still applies — which
  means a case in this state is *partially* baseline-governed, the
  hardest state to reason about when auditing a config by eye. Same
  class as `docs-promptfoo-guardrails-assertions.md` **Claim 7** (a
  `defaultTest` assertion applied to a mixed suite backfires) and
  `docs-promptfoo-assertions-metrics.md` **Claim 3** (a `threshold` of `0`
  makes a case unfailable) — three separate config values, one failure
  mode.

### Claim 7: `{{ env.X }}` is resolved at **config load time, not runtime**, can therefore control file paths and API keys, and the vendor explicitly warns that putting secrets in `config.env` "resolves the secret into the eval config object and may appear in exported results"
- **Evidence**: The "Accessing environment variables" subsection — a
  warning admonition and a remedy paragraph directly beneath it. The
  linked Configuration Reference corroborates that `env` is a first-class
  config key ("Envar overrides" in `TestSuiteConfiguration`).
- **Confidence**: settled (documented product behavior, vendor-flagged
  as a security matter)
- **Quote**: "Environment variables are resolved at config load time (not
  runtime) and can control file paths and API keys—only use them in
  trusted environments." and "Avoid copying secrets into config.env with
  templates like ANTHROPIC_API_KEY: '{{ env.ANTHROPIC_API_KEY }}'. This
  resolves the secret into the eval config object and may appear in
  exported results." and "If a secret is already present in your shell
  environment (or loaded via --env-file), prefer reading it directly from
  process env and keep config.env for non-sensitive flags."
- **Our assessment**: Strong, quotable, and the only Ch06-grade item in
  the corpus on this page (`config.env`: **zero hits**; "config load
  time": **zero hits**). Three operational consequences, all
  load-bearing for a CI gate: (1) `{{ env.X }}` is a **pre-processing
  step over the config file**, so a config that interpolates env vars is
  no longer a static artifact — the same YAML produces different
  providers, keys, and *prompt file paths* depending on who runs it,
  which undermines commit-the-config / run-the-gate reproducibility
  (the vendor's own guard is "only use them in trusted environments",
  i.e. the threat model is the config file, not the attacker); (2)
  `config.env` is a value in the parsed config object, so a secret copied
  there is no longer a reference to a secret — it *is* the secret, and it
  rides along with anything that serializes the config, which the vendor
  names as exported results; (3) the documented fix is asymmetric on
  purpose: read credentials from the process environment (or
  `--env-file`) and reserve `config.env` for non-sensitive flags. For
  the guide this belongs with credential *declaration* discipline, not
  with secret-scanning tooling: the finding is "don't put a value where
  a reference belongs*, and the export path is the leak surface, so
  *audit what your eval exports, not just your prompt* is the actionable
  form. One honest limit: the page says "may appear" — it does not
  enumerate which export formats carry the config object, so the specific
  leak channel needs a check against the CLI's output options before the
  guide names one.

### Claim 8: Thinking content is included in the response by default and reaches assertions; `showThinking: false` excludes it, and on Claude 5 models the reasoning knob is `thinking: {type: 'adaptive'}` + `effort`, which "replaces budget_tokens"
- **Evidence**: The "Thinking Output" and "Controlling Thinking Output"
  sections with the annotated Claude provider block.
- **Confidence**: settled (documented product behavior; model-generation-
  specific)
- **Quote**: "By default, thinking content is included in the response.
  You can hide it by setting showThinking to false." and "This is useful
  when you want better reasoning but don't want to expose the thinking
  process to your assertions." and (config comment, verbatim) "effort:
  high # Reasoning depth; replaces budget_tokens on Claude 5 models"
- **Our assessment**: Buy the mechanism, and note that this is the
  corpus's **third independent appearance** of the same judge-hygiene
  rule (`docs-promptfoo-model-graded-metrics.md` **Claim 5** /
  **Claim 6**, `docs-promptfoo-llm-rubric.md`), reached here from the
  opposite direction — the config page frames it as "don't expose
  thinking to *your assertions*, whereas the model-graded notes frame it
  as the grader misparsing reasoning left in `content`. Same fix, same
  field; this page's phrasing generalizes it beyond judges to *any*
  assertion (e.g. `contains`, `similar`, `javascript` on a thinking
  model), which is the useful widening. The `effort`-replaces-`budget_tokens`
  comment is the vendor-side confirmation of a supersede the corpus
  already suspected: `blog-promptfoo-red-team-claude.md` **Claim 5**
  documents the 2025-era `budget_tokens` red-team config and flags it as
  obsolete on adaptive-thinking models, and
  `blog-litellm-claude-fable-5-day-0.md` **Claim 8** documents that
  explicit budgets are *rejected with a 400* on Fable 5 while
  `reasoning_effort` maps to adaptive thinking. Three sources, one
  migration. Also worth keeping: `showThinking` is a **provider**-level
  config field, so it must be set on every provider in the matrix or the
  same assertion grades reasoning on one column and final content on
  another.

### Claim 9: `$ref` + `assertionTemplates` de-duplication is available here, with one net-new caveat — `tools`/`functions` values in provider config are **not** dereferenced
- **Evidence**: The "YAML references" section's `info` admonition
  following the `$ref` example.
- **Confidence**: settled (documented product behavior; the caveat is
  the vendor's own `info` note)
- **Quote**: "tools and functions values in providers config are not
  dereferenced. This is because they are standalone JSON schemas that may
  contain their own internal references."
- **Our assessment**: The reuse mechanism itself is **not** re-extracted
  here — `docs-promptfoo-assertions-metrics.md` **Claim 13** already owns
  `$ref`/`assertionTemplates`. Recording only the caveat, because it is a
  real partial-application trap: a team that factors its provider tool
  schemas into `$ref` templates will find the dereference silently
  skipped for exactly those two keys, with no error — the config loads
  and the tool schema arrives unresolved (or not at all). The stated
  reason (standalone JSON schemas with their own internal references) is
  plausible and self-consistent, and it also means `$ref` is
  asymmetric: reusable on assertions and vars, not on tool definitions.
  Note the caveat's phrasing is slightly loose — it does not say whether
  the reference is ignored, left literal, or resolved at call time — so
  the safe reading is "do not put `$ref` in provider `tools`/`functions`
  and expect it to work."

### Claim 10: Scripted vars are a documented API with fixed callback signatures — JS `(varName, prompt, otherVars, provider)` and Python `get_var(var_name, prompt, other_vars)`, each returning `{output}` or `{error}`
- **Evidence**: The "Javascript variables" and "Python variables"
  subsections with both full function bodies; the framing sentence about
  vector databases; the separate PDF path with its `pdf-parse`
  dependency note.
- **Confidence**: settled (documented product behavior — the signatures
  are a hard contract for anyone writing a generator)
- **Quote**: "The function receives varName, prompt, otherVars, and
  provider as arguments:" and "Define a get_var function that accepts
  var_name, prompt, and other_vars:" and "Scripted vars are useful when
  testing vector databases like Pinecone, Chroma, Milvus, etc. You can
  communicate directly with the database to fetch the context you need."
- **Our assessment**: Worth having as an API record, with one
  operational caution. The use case the vendor names — a var that fetches
  live context from a vector DB at eval time — means **the eval's input
  is not reproducible from the config**: the same suite can grade
  different retrieved context on different runs with no recorded input
  to diff against. That is the same evidence-integrity problem Ch05
  already raises for caching (a green eval that cannot name what it
  measured), arriving from the input side instead of the cache side, and
  it is *not* covered by the caching note. The `{error}` return channel
  (per Claim 5) is the documented negative path for these functions, with
  the same absence of documented harness behavior. Also note the vendor
  spells it `Javascript` (not JavaScript) in this page's prose — quoting
  preserved.

### Claim 11: Multiple `-c` / globbed configs are combined into a **single eval**, not reported separately
- **Evidence**: The "Config structure and organization" section — two
  single-config invocations, then the combining forms.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can run multiple configs at the same time, which will
  combine them into a single eval." and (CLI, verbatim) "promptfoo eval
  -c my_configs/*" / "promptfoo eval -c config1.yaml -c config2.yaml -c
  config3.yaml"
- **Our assessment**: Small claim, real CI consequence. The natural
  refactor of a growing suite is to split configs per use case, which
  invites `promptfoo eval -c configs/*` in CI. That produces **one
  aggregate verdict**: there is no per-config pass/fail to gate on, and
  a failure tells you a config failed but not which one without reading
  the report. The same page's escape is the two preceding invocations —
  run each config separately to get per-config gates — so the rule for
  the guide is a choice, not a default: combined = one gate over a
  union, separate = N gates with N exit codes. Worth stating because
  *we split our configs per team* and *we gate per team* are different
  claims and only one of them is true by default.

### Claim 12: Array-valued vars expand to the cartesian product of their values, and the escape hatch (`disableVarExpansion`) lives on `defaultTest.options`, not on the assertion
- **Evidence**: The "Multiple variables in a single test case" section
  ("Evaluates each language x input combination") and the linked Test
  Cases page's "Passing Arrays to Assertions" subsection with its
  `contains-any` config.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The vars map in the test also supports array values. If
  values are an array, the test case will run each combination of values."
  (Linked Test Cases page, verbatim: "By default, array variables expand
  into multiple test cases. To pass an array directly to assertions like
  contains-any, disable variable expansion:") (Linked Configuration
  Reference page, `options.disableVarExpansion` row, verbatim: "If true,
  arrays in vars are not expanded into multiple test cases".)
- **Our assessment**: Buy it, and read it as a **cost and
  coverage-accounting** property rather than a syntax note. The guide's
  worked example is 3 languages × 3 inputs = 9 cases *per prompt per
  provider*, so adding one array dimension silently multiplies the whole
  matrix — the kind of growth that shows up as an unexpectedly expensive
  eval run, or as a CI job that gets timed out and then gets disabled
  (which is its own green-gate failure). The two escape hatches sit in
  different places and are easy to conflate: `disableVarExpansion` is a
  suite-level `options` flag (so it changes *every* case in scope, not
  just the assertion that wanted an array), and it must be set before the
  assertion that needs the array, which is the opposite of per-assertion
  scoping. The glob expansion of `vars` into an array is the same
  mechanism reached from the filesystem, so a directory of fixtures
  becomes a combinatorial suite. Corpus check: no existing note covers
  cartesian expansion — `docs-promptfoo-assertions-metrics.md` **Claim
  1/2** covers how scores combine *within* a case, not how cases multiply
  across array dims.

## Concrete Artifacts

### Transform execution order, as documented (verbatim from the "Transforming outputs" section)

```
- Provider transforms (transformResponse) - Always applied first
- Test transforms (options.transform) and Context transforms (contextTransform)
  - Both receive the output from the provider transform
  - Test transforms modify the output for assertions
  - Context transforms extract context for context-based assertions (e.g., context-faithfulness)
```

### Test transform hierarchy (verbatim from "Test transform hierarchy")

```
- Default test transforms (if specified in defaultTest)
- Individual test case transforms (overrides defaultTest transform if present)
```

> Note that only one transform is applied at the test case level - either
> from defaultTest or the individual test case, not both.

### The `transformFn` context contract (verbatim from "Transform execution order")

```
transformFn: (output: string, context: {
  prompt: {
    // ID of the prompt, if assigned
    id?: string;
    // Raw prompt as provided in the test case, without {{variable}} substitution.
    raw?: string;
    // Prompt as sent to the LLM API and assertions.
    display?: string;
  };
  vars?: Record<string, any>;
  // Metadata returned in the provider response.
  metadata?: Record<string, any>;
}) => void;
```

### `disableDefaultAsserts` — a case that opts out of the inherited baseline (verbatim from "Default test cases")

```yaml
defaultTest:
  vars:
    audience: developer
  assert:
    - type: contains
      value: installation steps
tests:
  - vars:
      topic: API setup
    options:
      disableDefaultAsserts: true
    assert:
      - type: contains-json
```

### Env resolution and the secret warning (verbatim from "Accessing environment variables")

```yaml
prompts:
  - 'file://{{ env.PROMPT_DIR }}/prompt.txt'
tests:
  - vars:
      headline: 'Articles about {{ env.TOPIC }}'
```

> Environment variables are resolved at config load time (not runtime)
> and can control file paths and API keys—only use them in trusted
> environments.

> Avoid copying secrets into config.env with templates like
> ANTHROPIC_API_KEY: '{{ env.ANTHROPIC_API_KEY }}'. This resolves the
> secret into the eval config object and may appear in exported results.

> If a secret is already present in your shell environment (or loaded
> via --env-file), prefer reading it directly from process env and keep
> config.env for non-sensitive flags.

### Scripted-var callback contracts (verbatim from "Javascript variables" / "Python variables")

```javascript
// dynamicVarGenerator.js
module.exports = async function (varName, prompt, otherVars, provider) {
  // Access other variables from the test case
  const role = otherVars.role;
  // Return the dynamic value
  return { output: PROMPTS[role] };
  // Or return an error
  // return { error: 'Something went wrong' };
};
```

```python
# load_context.py
def get_var(var_name, prompt, other_vars):
    # Access other variables from the test case
    role = other_vars.get("role")
    # Return the dynamic value
    return {"output": PROMPTS[role]}
    # Or return an error
    # return {"error": "Something went wrong"}
```

### `transformVars` suite-wide example and its error-return channel (verbatim from "Transforming input variables")

```yaml
prompts:
  - 'Summarize the following text in {{topic_length}} words: {{processed_content}}'
defaultTest:
  options:
    transformVars: |
      return {
        uppercase_topic: vars.topic.toUpperCase(),
        topic_length: vars.topic.length,
        processed_content: vars.content.trim()
      };
tests:
  - vars:
      topic: 'climate change'
      content: '  This is some text about climate change that needs processing.  '
    assert:
      - type: contains
        value: '{{uppercase_topic}}'
```

```javascript
// transformVars.js — external file form, verbatim including the error branch
const fs = require('fs');
module.exports = {
  customTransformVars: (vars, context) => {
    try {
      return {
        uppercase_topic: vars.topic.toUpperCase(),
        topic_length: vars.topic.length,
        file_content: fs.readFileSync(vars.file_path, 'utf-8'),
      };
    } catch (error) {
      console.error('Error in transformVars:', error);
      return {
        error: 'Failed to transform variables',
      };
    }
  },
};
```

### Transform from an external file (verbatim from "Transforms from separate files")

```yaml
defaultTest:
  options:
    transform: file://transform.js:customTransform
```
```javascript
module.exports = {
  customTransform: (output, context) => {
    // context.vars, context.prompt
    return output.toUpperCase();
  },
};
```
> If no function name is specified for Python files, it defaults to
> get_transform.

### Thinking output config (verbatim from "Controlling Thinking Output")

```yaml
providers:
  - id: anthropic:messages:claude-sonnet-5
    config:
      thinking:
        type: 'adaptive'
      effort: high # Reasoning depth; replaces budget_tokens on Claude 5 models
      showThinking: false # Exclude thinking content from output
```

### `$ref` reuse, and the provider `tools`/`functions` exception (verbatim from "YAML references")

```yaml
tests:
  - vars:
      language: French
      input: Hello world
    assert:
      - $ref: '#/assertionTemplates/startsUpperCase'
  - vars:
      language: German
      input: How's it going?
    assert:
      - $ref: '#/assertionTemplates/noAIreference'
      - $ref: '#/assertionTemplates/startsUpperCase'

assertionTemplates:
    noAIreference:
      type: llm-rubric
      value: does not describe self as an AI, model, or chatbot
    startsUpperCase:
      type: javascript
      value: output[0] === output[0].toUpperCase()
```

### Multi-config composition (verbatim from "Config structure and organization")

```bash
promptfoo eval -c usecase1.yaml
promptfoo eval -c usecase2.yaml
```
```bash
promptfoo eval -c my_configs/*
```
```bash
promptfoo eval -c config1.yaml -c config2.yaml -c config3.yaml
```

### External test-set sources (verbatim from "Loading tests from CSV" and the Azure Blob section)

```yaml
tests: file://tests.csv
```
```yaml
tests: https://docs.google.com/spreadsheets/d/1eqFnv1vzkPvS7zG-mYsqNDwOzvSaiIAsKB3zKg9H18c/edit?usp=sharing
```
```yaml
tests: az://myaccount/evals/tests.json
```
> Test files can be defined in YAML/JSON, JSONL, CSV, and
> TypeScript/JavaScript. Promptfoo also supports external datasets from
> Google Sheets and Azure Blob Storage.

### Linked Configuration Reference — the full three-stage pipeline with a RAG worked example (verbatim from `/docs/configuration/reference`, "Transformation Pipeline" section, "Complete Example: RAG System Evaluation" subsection)

```yaml
providers:
  - id: 'http://localhost:3000/api/rag'
    config:
      # Step 1: Provider transform - normalize API response structure
      transformResponse: |
        // API returns: { status: "success", data: { answer: "...", sources: [...] } }
        // Transform to: { answer: "...", sources: [...] }
        json.data
tests:
  - vars:
      query: 'What is the refund policy?'
    options:
      # Step 2a: Test transform - extract answer for general assertions
      # Receives output from transformResponse: { answer: "...", sources: [...] }
      transform: 'output.answer'
    assert:
      # Regular assertion uses test-transformed output (just the answer string)
      - type: contains
        value: '30 days'
      # Context assertions use contextTransform
      - type: context-faithfulness
        # Step 2b: Context transform - extract sources
        # Also receives output from transformResponse: { answer: "...", sources: [...] }
        contextTransform: 'output.sources.map(s => s.content).join("\n")'
        threshold: 0.9
      # Another assertion can have its own transform
      - type: equals
        value: 'confident'
        # Step 3: Assertion-level transform (applied after test transform)
        # Receives: "30-day refund policy" (the test-transformed output)
        transform: |
          output.includes("30") ? "confident" : "uncertain"
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 5** ("Self-hosted OpenAI-compatible judges (vLLM, LocalAI, llamafile) need `showThinking: false` so promptfoo grades only the final `content`") — this page's "This is useful when you want better reasoning but don't want to expose the thinking process to your assertions" (Claim 8) states the same mechanism from the config side; the generalization here is that the field is provider-level and applies to *any* assertion type, not only model-graded judges. (Verified: #1305 Claim 5.)
  - `source-notes/blog-promptfoo-red-team-claude.md` **Claim 5** ("A bounded `budget_tokens` is part of the recommended thinking-model red-team config — extended thinking is enabled (type 'enabled') with an explicit budget cap") and `source-notes/blog-litellm-claude-fable-5-day-0.md` **Claim 8** ("`reasoning_effort` is mapped to adaptive thinking; explicit thinking budgets are rejected by the Anthropic API with a 400") — the config guide's inline comment "`effort: high # Reasoning depth; replaces budget_tokens on Claude 5 models`" is the vendor-side confirmation of the supersede the red-team note already flagged, and it is the third independent source on that migration. (Verified: #689 Claim 5 and #258 Claim 8.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 8** ("External scripts load via `file://path/script.js` with an optional `:functionName` selector") — the same loading convention as this page's `file://transform.js:customTransform` and `file://transformVars.js:customTransformVars`, which corroborates `file://path[:symbol]` as promptfoo's general external-code convention rather than a per-feature quirk. (Verified: #1304 Claim 8.)
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` **Claim 4** (`context` "can be extracted dynamically from the provider response via `contextTransform` (worked form: `contextTransform: 'output.context'`)") and `source-notes/docs-promptfoo-model-graded-context-recall.md` **Claim 5** (the same `contextTransform: 'output.context'` instance) — this page adds the missing *position*: `contextTransform` sits in the same stage as `options.transform` and consumes the provider-transformed output, so the two notes' per-type examples are pipeline stages, not standalone config sugar. (Verified: #1320 Claim 4 and #1332 Claim 5.)
  - `source-notes/docs-promptfoo-conversation-relevance.md` **Claim 4** ("`_conversation` content is treated as literal runtime data and is NOT rendered as a Nunjucks template — template syntax like `{{ vars.value }}` or `{{ env.API_KEY }}` is preserved verbatim for security") — a deliberate contrast with this page's Claim 7: prompt templates *are* rendered (and `{{ env.* }}` resolved at load time) while conversation *content* is not. Together they define promptfoo's actual env-templating boundary, which is narrower than a blanket claim that the config interpolates env vars. (Verified: #1334 Claim 4.)
  - `source-notes/docs-promptfoo-classifier-grading.md` **Claim 3** (a token-classification detector's endpoint is injected as `apiEndpoint: '{{env.HF_STARPII_ENDPOINT}}'`) — same templating mechanism, and this page supplies the semantics the classifier note treats as a given: load-time resolution, and the vendor's warning about putting secret *values* (as opposed to non-secret endpoint URLs) into `config.env`. Adjacent, not identical; not a conflict. (Verified: #1288 Claim 3.)

- **Contradicts**: None identified, and no contradiction issue filed. Verified against `CONTRADICTIONS.md` and all ten open `contradiction`-labeled issues (checked #1307 in particular, since it is the closest claim in the corpus). Nothing on this page *opposes* an existing note: Claim 2's override-not-compose rule, Claim 6's `disableDefaultAsserts`, and Claim 7's load-time env resolution are all first statements in the corpus rather than competing ones. Open contradiction **#1307** ("promptfoo missing-trace semantics: built-in trace-* assertions throw ('could not be evaluated') vs custom-JS trace gate passes green when tracing is off") is *adjacent* to Claim 5's `{error}` observation — same shape (documented negative path, undocumented harness reaction, green-gate exposure), different mechanism and different assert family. That is a research lead for the Smith, not a conflict, and it is recorded here rather than filed as a new contradiction.

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-caching.md` — the sibling hub-adjacent config page (#1275), which owns the *replay* causes of a green eval that is not evidence (Claims 1/4/8). This page supplies the **configuration-composition** causes: a transform that overrides instead of composing (Claim 2), an inherited assertion silently dropped (Claim 6), an input var fetched live at eval time (Claim 10), and array expansion that changes the case count underneath a gate (Claim 12). Read together: the caching note says a green result may be replayed; this note says a green result may also have been measured against the wrong input, or measured on a subset of the assertions. (Verified: #1275 Claims 1, 4, 8.)
  - `source-notes/docs-promptfoo-guardrails-assertions.md` **Claim 7** ("Applying `guardrails` as a `defaultTest` in a mixed suite backfires — promptfoo adds default assertions to `not-guardrails` attack cases too") and its Concrete Artifacts section "HTTP provider transform example" — that note holds a worked `transformResponse` and one `defaultTest` trap; this page states where `transformResponse` sits in the order and supplies the general inheritance rule (`disableDefaultAsserts`) that makes the trap escapable. (Verified: #1303 Claim 7 and the named Concrete Artifacts section.)
  - `source-notes/docs-promptfoo-llm-rubric.md` **Claim 10** ("The override precedence is stated as an exact three-level chain on this page — `assertion.provider` > `test.options.provider` > `defaultTest.options.provider`") — this page's hub-level statement of the same surfaces ("To choose the judge for model-graded assertions, set defaultTest.options.provider. Keep the models being tested in the top-level providers list:") is where the `defaultTest` tier's *purpose* is documented, and it is the same `defaultTest` block whose `assert` and `options` tiers are separately overridable per this page (Claims 2 and 6). (Verified: #1471 Claim 10.)
  - `source-notes/docs-promptfoo-chat-threads.md` **Claim 4** ("`storeOutputAs` records an LLM output as a variable usable in subsequent test cases, and `transform` can mutate it before storage") and **Claim 7** ("JSON prompt files auto-escape vars containing quotes/newlines, while non-JSON (Nunjucks) template files must use the built-in `dump` filter") — this page's Nunjucks and transform sections are the hub-level statement of the two mechanisms that note applies to conversation fixtures; the additions here are the pipeline *position* of `transform` (Claim 1) and the `transformVars` input-side twin (Claim 4). (Verified: #1276 Claims 4 and 7.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 3** ("A test-case `threshold` of `0` makes the case pass regardless of how many assertions fail") and **Claim 13** (`$ref`/`assertionTemplates`) — Claim 13 owns the reuse mechanism and is deliberately *not* re-extracted here (only the `tools`/`functions` non-dereference caveat, Claim 9, is new). Claim 3 is the same failure class as this page's Claim 6: a per-case config value that removes an assertion's ability to fail. (Verified: #1287 Claims 3 and 13.)

- **Novel**: New to the corpus (each verified by grep across all 215 source notes; the counts in parentheses are total corpus hits before this note):
  1. **The transform execution order and the `defaultTest` transform hierarchy** — provider-first, both stage-2 branches from the provider-transformed output, assertion-level last, and per-case transform overriding rather than composing (Claims 1–3; `transformVars`/`disableDefaultAsserts` = 0 hits, and no note states the order).
  2. **`options.disableDefaultAsserts`** — the per-test opt-out from inherited `defaultTest.assert`, with everything else in `defaultTest` still applying (Claim 6; 0 hits).
  3. **`transformVars` as an input-side transform with key-override semantics** (Claim 4; 0 hits) and **its `{ error: ... }` return channel with no documented harness reaction** (Claim 5).
  4. **Load-time `{{ env.* }}` resolution and the `config.env` secret-in-exported-results warning** — the corpus's only vendor-flagged credential-handling rule for eval configs (Claim 7; `config.env` = 0 hits).
  5. **The scripted-var callback signatures as an API contract** for JS and Python, including the live-vector-DB framing that makes eval inputs non-reproducible from the config (Claim 10).
  6. **Cartesian expansion of array vars** and the suite-level `disableVarExpansion` escape hatch (Claim 12; no note covers case-count multiplication).
  7. **Multi-config composition into a single eval** (Claim 11) and the `$ref` non-application to provider `tools`/`functions` (Claim 9).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**, section *"A green eval is not evidence until you can name what it measured"*: this source is the second, independent route to that section's conclusion, and a better one for the reader who has already read the caching note. Add the config-composition failure class there — the thing an assertion receives is `transformResponse` → `options.transform` → assertion `transform` (Claim 1), a per-case transform silently replaces the suite-wide one rather than composing with it (Claim 2), `options.disableDefaultAsserts: true` drops the inherited baseline assertion from exactly the cases an author found awkward (Claim 6), and a `transformVars`/scripted var can change the *prompt* before templating (Claims 4, 10). The concrete recommendation to add: **before trusting a green gate, enumerate what each assertion actually received** — provider transform present? test transform present at both `defaultTest` and case level (they cannot both apply)? `disableDefaultAsserts` set on any case? — because each of those is a documented, silent divergence between the config's appearance and its behavior. Cite alongside the existing caching paragraph rather than replacing it.
- **Chapter 05**, section *"A gate that cannot fail is not a gate"*: this source supplies two more named, documented instances for the same list — `disableDefaultAsserts` (removes the check from a case) and `defaultTest` transform override (changes what the check sees). The existing `threshold: 0` example is about score semantics; these are about *composition* semantics, and they are the ones a reviewer cannot see by reading one assertion block. Also worth one line here: array-valued vars multiply the case count (Claim 12), which is how a gate quietly becomes expensive enough to be skipped or timed out.
- **Chapter 06 (Security and Trust)**, section *"Gateway credential routing: declare, don't infer"*: the `config.env` rule belongs with credential *declaration* discipline, and it is a declaration failure of exactly the kind that section is about — a value placed where a reference belongs. Add: `{{ env.X }}` is resolved at **config load time**, so an interpolated config is not a static artifact and can redirect prompt file paths and API keys (Claim 7); and per the vendor's own warning, `config.env` holding a secret puts the secret *in* the eval config object, which "may appear in exported results." The actionable form for the guide is therefore *audit what the eval exports, not only what the prompt contains* — a secret that was never in the prompt is still in the exported artifact. Documented fix to carry verbatim: read credentials from the process environment (or `--env-file`) and keep `config.env` for non-sensitive flags. Honest limit to preserve: the page says "may appear" and does not enumerate which export formats carry the config object, so the guide should name the *class* of artifact to check (exported eval results / shared results), not a specific file path.
- **Chapter 06**, section *"Red-teaming as a CI gate"* → *"Reasoning models add a compute-DoS category"*: the config guide's `effort` / `showThinking: false` block (Claim 8) is the config-side companion to the corpus's two existing sources on thinking-model configuration (`blog-promptfoo-red-team-claude.md` Claim 5's now-obsolete `budget_tokens` form, and `blog-litellm-claude-fable-5-day-0.md` Claim 8's 400-on-explicit-budget finding). One line to add: on Claude 5 / adaptive-thinking models the reasoning knob is `effort` (which "replaces budget_tokens"), so a red-team config carried over from the Claude 4 era needs migrating before its bounded-reasoning-DoS cap means anything.
- **Chapter 05**, section *"Read the assert's own defaults before trusting its verdict"* (line 443): extend the checklist's framing from *assert-level* defaults to *config-level* ones. `showThinking` defaults to including reasoning in the asserted text (Claim 8), array vars expand by default (Claim 12), and `defaultTest.assert` is inherited unless a case opts out (Claim 6) — three defaults, none of which appear on the assertion block a reviewer is reading.

## Extraction Notes

- Source read in full via direct HTTP fetch of the rendered Docusaurus page (`https://www.promptfoo.dev/docs/configuration/guide`, 970 lines of extracted prose + code). Every quote in this note was verified character-for-character against the fetched HTML before writing, including the em dash in the env-resolution sentence ("API keys—only use them"), the hyphen in "only one transform is applied at the test case level - either from", and the inline config comments quoted as code (`# Reasoning depth; replaces budget_tokens on Claude 5 models`).
- Linked pages followed (3 of a permitted 5), all reached from this page: `/docs/configuration/reference` (**used and cited** — supplies the third pipeline stage, the `disableDefaultAsserts` and `disableVarExpansion` table rows, and the `env` config key), `/docs/configuration/test-cases` (**used and cited** for the array-expansion escape hatch and dynamic *test* generation, which is a distinct surface from this page's dynamic *vars*), and `/docs/configuration/prompts` (read, **nothing cited** — the page only covers `file://` prompt loading, already established corpus-wide). Not followed: the provider pages (Google/OpenAI/Anthropic/Bedrock — out of scope for a config-organization note) and the GitHub example links. Claims sourced from the two linked pages are labeled as such in-line and their artifacts are grouped at the end of Concrete Artifacts.
- Deliberately **not** re-extracted, per the Prospector triage and confirmed against the corpus: basic YAML shape (`prompts`/`providers`/`tests`/`assert`) and per-case assertions (established across `docs-promptfoo-assertions-metrics.md`, `docs-promptfoo-llm-rubric.md`, `docs-promptfoo-g-eval.md`); the `$ref`/`assertionTemplates` mechanism (owned by `docs-promptfoo-assertions-metrics.md` **Claim 13** — only the `tools`/`functions` non-dereference caveat is extracted, Claim 9); caching (owned by `docs-promptfoo-configuration-caching.md`, #1275 — this page contains no cache content); and the boilerplate example configs at the top of the page, which the triage rightly calls illustrative.
- **Contradiction handling**: no contradiction issue filed. Checked `CONTRADICTIONS.md` and all open `contradiction`-labeled issues first. The closest candidate is #1307 (custom-JS trace gate passes green when tracing is off); this page's Claim 5 (`transformVars` returns `{ error: ... }`, harness reaction undocumented) is the same *shape* of unverified negative path but a different mechanism and a different assert family, so per MINER.md §4a it is a lead recorded in Cross-References, not a conflict. Claim 2 (override, not compose) is likewise not a contradiction: it is a documented asymmetry, and the apparent reading that *both transforms should apply* is a reader assumption the page explicitly corrects.
- `date_published` uses the page's own `Last updated … Sep 30, 2026` footer date (Docusaurus pages are otherwise undated); the page was last modified the same day this note was extracted, so the `gpt-6-luna` / `claude-sonnet-5` / `effort` examples are current-generation and a future revision may change them.
- `confidence_overall` is `emerging`, not `settled`: this is first-party vendor documentation with **no measured evidence** — no eval run, no trace, no pass/fail outcome, and no reproduction of any ordering or inheritance claim in action. Individual *mechanism* claims (1, 2, 3, 6, 8, 9, 11, 12) are settled-for-product-behavior and directly checkable against an installed CLI; the operational *risk* framing layered on top of them (that an override silently unhooks a suite transform, that a returned `{error}` may not fail the case) is the Miner's synthesis and is flagged as such in each **Our assessment**. Claim 5 is `emerging` on its own terms: it documents an absence, not a behavior.
- Two documentation inconsistencies noticed and left unresolved rather than smoothed over: the inline `transformFn` type is declared `=> void` while the page's own multiline example `return`s a value (Claim 3), and the "Assertions are optional" framing at the top of the page sits uneasily beside a guide whose whole purpose is gating. Both preserved as observed.
- **Candidate disposition** (from `miner-related-notes.md`, read before writing Cross-References; each candidate cited or dismissed by name, none invented):
  - `docs-promptfoo-pi-scorer.md` — dismissed: a grader-*type* page (`pi` SDK credential, determinism, threshold). It does mention `defaultTest.options.provider` only as one of three override surfaces, already owned by `docs-promptfoo-llm-rubric.md` **Claim 10**; no transform, inheritance, or env content.
  - `blog-promptfoo-owasp-red-teaming.md` — dismissed: red-teaming methodology and CI placement; shares the vendor and the CI-gate theme but has no config-composition surface.
  - `docs-google-sre-team-lifecycles.md` — dismissed: Google SRE team-organization chapter; lexical overlap only.
  - `docs-litellm-batches-api.md` — dismissed: LiteLLM gateway rate-limiting for batch inference; different tool and layer.
  - `blog-pagerduty-sre-agent-triage.md` — dismissed: AI incident triage and skill encoding. Same Ch05 neighborhood (what an LLM-as-judge alert should do to a responder) but zero overlap with config semantics; noted for the Smith as chapter-adjacent only.
  - `blog-promptfoo-red-team-claude.md` — **cited** (Corroborates, Claim 8): the `budget_tokens` → `effort` supersede.
  - `docs-promptfoo-classifier-grading.md` — **cited** (Corroborates, Claim 7 context): its `{{env.HF_STARPII_ENDPOINT}}` endpoint contract versus this page's load-time resolution semantics and secret-value warning.
  - `docs-promptfoo-javascript-assertions.md` — **cited** (Corroborates, Claim 3): `file://path/script.js:functionName` as the shared external-code convention.
  - `docs-promptfoo-llm-rubric.md` — **cited** (Extends, Claim 8/Cross-References): the three-level `defaultTest.options.provider` grader precedence this page documents the purpose of.
  - `docs-langfuse-mcp-server.md` — dismissed: Langfuse's docs MCP server; unrelated vendor and no config content.
  - Additional cross-references found by searching `source-notes/` directly (beyond the candidate list), each re-read and verified per MINER.md §4b before citation: `docs-promptfoo-configuration-caching.md`, `docs-promptfoo-guardrails-assertions.md`, `docs-promptfoo-assertions-metrics.md`, `docs-promptfoo-model-graded-metrics.md`, `docs-promptfoo-model-graded-context-faithfulness.md`, `docs-promptfoo-model-graded-context-recall.md`, `docs-promptfoo-conversation-relevance.md`, `docs-promptfoo-chat-threads.md`, and `blog-litellm-claude-fable-5-day-0.md`.
- `miner-related-notes.md` was read for cross-reference candidates and is **not** committed (per MINER.md §4 and the issue instructions).