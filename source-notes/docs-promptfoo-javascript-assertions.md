---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/javascript/
source_type: docs
title: "Promptfoo Configuration: Javascript Assertions"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-13
date_extracted: 2026-09-13
last_checked: 2026-09-13
status: current
confidence_overall: emerging
issue: "#1304"
---

# Promptfoo Configuration: Javascript Assertions

> The vendor reference for the `javascript` / `not-javascript` assertion
> escape hatch — the `boolean | number | GradingResult` return contract under
> which a gate's semantics are redefined in user code, the full
> `AssertionValueFunctionContext` surface (including OpenTelemetry
> `context.trace` span data), the trace-based gates that assert *how* a
> response was produced (causal ordering, latency budget, error spans, span
> depth, API-call count), the `not-javascript` pre-inversion threshold
> subtlety, the config-vs-vars report-pollution rule, and the page's own
> footguns: a fail-open trace guard that passes green when tracing is off,
> conflicting output-shape statements, and a vendor example that throws.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Javascript
  assertions" reference page under `/docs/configuration/expected-outputs/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `javascript` assertion behavior — authoritative for what the
  config does with a given function, but vendor-positioned: no measured
  gate-failure-rate, drift, or cost figures, and no independent practitioner
  validation. Every clause below is directly checkable against an installed
  CLI.
- **Scope**: This is the deep-dive page behind the `javascript` row of the
  parent hub page (`configuration/expected-outputs`): the injected `output`
  variable, the return-type contract, the `GradingResult` / `componentResults`
  surface, multiline and external (`file://`) functions, linear and inline
  forms, the full `AssertionValueFunctionContext` object (including the
  `context.trace` OpenTelemetry span data), trace-based assertions, ES-module
  packaging, and `not-javascript` negation. Does NOT cover the deterministic
  assertion catalog (sibling #1289), the model-graded family (#1305 sibling),
  or the classifier type (#1288).
- **Last updated**: Sep 13, 2026 by renovate[bot]; the page is undated but
  documents the current tracing-enabled eval era.

## Extracted Claims

### Claim 1: The `javascript` assertion lets an operator provide a custom JS function against the LLM output — the gate accepts `true`/`false`, a number treated as a score, or a `GradingResult`, so the gate's pass/fail semantics are redefined in user code
- **Evidence**: The page's opening paragraphs and the "Return type" section's
  type union, with the bare-number-as-score rule.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `javascript` assertion allows you to provide a custom JavaScript function to validate the LLM output." and "A variable named `output` is injected into the context. The function should return `true` if the output passes the assertion, and `false` otherwise. If the function returns a number, it will be treated as a score." and "The return value of your Javascript function can be a boolean, number, or a `GradingResult`:"
- **Our assessment**: This is the extension point where a gate's semantics
  stop being declarative and become whatever the function says they are. The
  number-as-score contract means a function that returns a raw numeric value
  (e.g., a parsed response body) is interpreted as a score compared against
  `threshold`, and a value that is neither boolean, number, nor `GradingResult`
  falls outside the documented contract — the first thing a reviewer should
  check on any `javascript` assertion is which of the three shapes it
  actually returns.

### Claim 2: If the JS function throws, the assertion fails (fail-closed) and the error message is included in the failure reason — an unhandled exception in a custom assertion is a hard red, not a skip
- **Evidence**: The throw-behavior paragraph immediately after the score
  examples, with the worked "errorCase" example returning a `GradingResult`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "If your function throws an error, the assertion will fail and the error message will be included in the reason for the failure."
- **Our assessment**: Fail-closed on throw is the right default for a gate,
  but it makes *any* bug in the assertion function look like a model failure.
  Combined with the page's own broken example (Claim 9), this is the
  strongest argument for executing (not just reading) vendor example code
  before deploying it in a gate — a `ReferenceError` you introduced turns
  every output red until you notice the assertion itself is what threw.
  The contrast with the built-in trace-* family, which throws to signal
  "could not be evaluated" rather than a property violation, is filed as a
  contradiction (#1307) — see Cross-References.

### Claim 3: `not-javascript` inverts the final pass/fail result while preserving the returned score, and numeric scores are compared against `threshold` BEFORE inversion — so the score that lands in the report and the pass/fail verdict can diverge under negation
- **Evidence**: The "Negation" section's definition and its lone example.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Use `not-javascript` to invert the final pass/fail result while preserving the returned score. Numeric scores are still compared against `threshold` before the result is inverted:"
- **Our assessment**: The highest-value claim on the page and the one absent
  from every existing promptfoo note. A `not-javascript` gate is not a plain
  boolean NOT: the threshold comparison runs on the un-inverted score, so a
  function that returns `0.9` against a `threshold: 0.5` first *passes* on
  the raw score, then inverts to fail — while the `0.9` that "preserved" into
  the report/weighted aggregate describes the opposite of the verdict. A
  weighted score built from a negated assertion can therefore point the
  opposite direction from its own pass/fail row. For gate reading: never
  reconstruct a negated assertion's score from the report's weighted average
  without applying the inversion logic yourself.

### Claim 4: The page makes two conflicting statements about the injected `output` variable's type — YAML-config "Handling objects" says a JSON-object output is already parsed as an object, while "Inline assertions" says "Output will always be a string" and prescribes `JSON.parse(output)` — so a JS assertion written against the wrong assumption throws, and per Claim 2 a throw is a hard fail
- **Evidence**: The "Handling objects" section's one sentence versus the
  inline-assertions section's "Output will always be a string" guidance, in
  the same page.
- **Confidence**: settled (both statements are verbatim on the page; the
  conditioning variable — config path vs inline JS-package path — is only
  implied by section context)
- **Quote**: "If the LLM outputs a JSON object (such as in the case of tool/function calls), then `output` will already be parsed as an object:" and "Output will always be a string, so if your custom response parser returned an object, you can use `JSON.parse(output)` to convert it back to an object."
- **Our assessment**: The page never states the conditioning variable
  explicitly, but the section contexts point to it: in YAML `assert:` blocks
  a JSON-object output arrives pre-parsed, while in the inline
  JS-package form "Output will always be a string". The Prospector flagged
  this as a contradiction-in-page; we treat it as a documented ambiguity with
  a path-dependent resolution rather than filing it — but the operational
  consequence is real: `output.includes(...)` on an object, or
  `JSON.parse(output)` on an already-parsed object, both throw, and a throw
  is a hard fail (Claim 2). A reused assertion function should detect the
  shape it receives instead of assuming one.

### Claim 5: The full `AssertionValueFunctionContext` surface is `prompt`, `vars`, `test`, `logProbs`, `config`, `provider`, `providerResponse`, `trace`, and `metadata` — with `logProbs` available only when the provider emits them and `trace` `undefined` unless tracing is enabled
- **Evidence**: The typed `TraceSpan` / `TraceData` /
  `AssertionValueFunctionContext` interface block in the "Using test context"
  section, and the page's own guard pattern for `context.trace`.
- **Confidence**: settled (documented product behavior — the only page in the
  docs family that enumerates this contract fully)
- **Quote**: "The `context` variable contains information about the test case and execution environment:" and "// OpenTelemetry trace data (when tracing is enabled) trace?: TraceData;"
- **Our assessment**: Two fields carry dependency preconditions that a gate
  builder must treat as configuration risk. `logProbs` is provider-dependent
  — the same precondition the deterministic note records for `perplexity`
  (#1289 Claim 14: logprobs support "only more recent versions of OpenAI GPT
  and Azure OpenAI GPT APIs"); a function that assumes it will be present
  breaks on other providers. `trace` is *tracing-dependent*, and the page's
  own examples handle its absence by *returning true* (Claim 6) — i.e. the
  most trace-aware field on the surface is also the one whose documented
  handling is a silent pass.

### Claim 6: Custom JS over `context.trace` asserts the *execution flow* — error spans (`statusCode >= 400`), wall-clock latency budget, per-trace API-call count, span-hierarchy depth cap, and causal span ordering (retrieval must start before generation) — the "gate on agent behaviour, not just output" pattern, and the page's canonical example fails open when tracing is off
- **Evidence**: The "Using trace data" reference function (error spans, total
  duration `> 5000` → fail, http API-call count `> 10` → fail), the
  ordering YAML (`retrievalSpan.startTime < generationSpan.startTime`), the
  span-hierarchy-depth example, and the guard `if (!context.trace) { … return true; }`.
- **Confidence**: settled (documented patterns, verbatim)
- **Quote**: "When tracing is enabled, OpenTelemetry trace data is available in the `context.trace` object." and "This allows you to write assertions based on the execution flow:" and "// Tracing not enabled, skip trace-based checks" and "return true;"
- **Our assessment**: The ordering predicate is the concrete analogue of
  Ch06's "test the action path, not just the text output": no text-matching
  assertion can express "retrieval happened before generation". But the
  page's own guaranteed-pass trace guard is the trap: as written, the
  reference example returns `true` when tracing is off, so a suite that
  *intends* to gate on trace data passes green and verifies nothing until
  someone notices tracing was never enabled. The built-in `trace-*` family
  instead throws ("could not be evaluated") on the same condition — that
  divergence, and which route a release gate should use, is filed as
  contradiction #1307.

### Claim 7: For reusing one script with different parameters, the page recommends assertion-level `config` over test `vars` — vars are shared across all assertions and surface as report columns, while `config` stays attached to one assertion and arrives as `context.config`
- **Evidence**: The "Passing assertion-specific parameters" section's
  preference sentence and the two-`minLength` reuse example.
- **Confidence**: settled (documented product behavior)
- **Quote**: "If you want to reuse the same JavaScript assertion with different parameters in a single test case, prefer assertion-level `config` over test `vars`. Test vars are shared across all assertions and appear as report columns, while `config` stays attached to one assertion and is available as `context.config`."
- **Our assessment**: A config-blast-radius rule for eval suites: every `var`
  used for assertion tuning leaks into every other assertion *and* the eval
  report surface as a column, so parameterizing via `vars` couples assertions
  to each other and pollutes observability. Assertion-local `config` keeps the
  parameter scoped to the one check it tunes — the same "locals over globals"
  hygiene the hub note's weighted-model review deserves. Whether a team's
  report columns come from intentional metrics or from advisory `vars` is a
  reviewable property of the config.

### Claim 8: External scripts load via `file://path/script.js` with an optional `:functionName` selector, must `module.exports` an assertion function (or a named export), and ES modules must be `.mjs` — committed repo code that executes inside the eval runner
- **Evidence**: The "External script" section's `file://` forms, the default/
  named export examples, and the ES-modules note.
- **Confidence**: settled (documented product behavior)
- **Quote**: "To reference an external file, use the `file://` prefix:" and "You can specify a particular function to use by appending it after a colon:" and "The JavaScript file must export an assertion function." and "ES modules are supported, but must have a `.mjs` file extension. Alternatively, if you are transpiling Javascript or Typescript, we recommend pointing promptfoo to the transpiled plain Javascript output."
- **Our assessment**: The review/supply-chain surface: a `file://` assertion
  is repo-committed code that the eval runner executes, so it deserves the
  same review gates as the pipeline code itself — and its line coverage is
  never exercised unless the suite actually runs it. The `.mjs` /
  transpiled-output packaging rules are the CI footguns (a `.js` ES module
  throws at load; pointing at TS source loads the wrong file). This page
  documents the *loading mechanics*; the hermeticity caveat for these
  scripts is already covered in #1289 Claim 2 (a `javascript` assertion is
  deterministic-by-taxonomy yet can make external calls).

### Claim 9: The vendor's own async external-validation example is broken — it logs an undefined `testResult` (a `ReferenceError`, which per Claim 2 fails the assertion) and returns the parsed response body as a raw value interpreted as a score rather than a `{pass, score, reason}` verdict — an official example that violates the page's own return contract
- **Evidence**: The "more complex example that uses an async function to hit
  an external validation service" block, in full.
- **Confidence**: settled (the `ReferenceError` is provable from the code;
  the return-shape violation follows from Claim 1's documented contract)
- **Quote**: "console.log(`success: ${testResult}`);" and "return success;" and "const VALIDATION_ENDPOINT = 'https://example.com/api/validate';"
- **Our assessment**: The strongest single piece of evidence for the standing
  rule "don't paste vendor assertion examples into a gate without executing
  them." As published, the snippet would throw on `testResult` the moment it
  runs — converting every output into a hard fail (Claim 2) — and even
  `testResult` fixed, it returns `success` (the parsed response document) as
  a non-boolean number-like value that the harness treats as a score. Two
  further operational notes: an async `fetch()` puts a network endpoint
  inside the CI gate with no timeout documented on this page (an endpoint
  outage converts to a failed gate), and this is the concrete example behind
  #1289 Claim 2's deterministic-but-not-hermetic caveat.

### Claim 10: `GradingResult` supports nested `componentResults` that render as an assertion-details table in the Eval view modal, plus `namedScores` in the worked example — nested sub-results are inspectable rather than opaque
- **Evidence**: The return-type section's `componentResults` sentence and the
  "entire grading result" example's nested `componentResults`/`namedScores`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "If `componentResults` is set, a table of assertion details will be shown in the test output modal in the Eval view." and "pass: boolean; score: number; reason: string; componentResults?: GradingResult[];"
- **Our assessment**: The custom-JS counterpart of `assert-set`
  partial-pass grouping (#1287 Claim 5): one `javascript` assertion can
  carry a set of sub-verdicts that stay individually inspectable in the eval
  UI. For gate reading this matters — a red top-level `pass` with nested
  component results tells you *which* sub-check failed, which is what makes
  a composite custom assertion debuggable instead of a single opaque `0`.

## Concrete Artifacts

### Return-type contract (verbatim from "Return type")

```ts
type JavascriptAssertionResult = boolean | number | GradingResult;
// Used for more complex results
interface GradingResult {
  pass: boolean;
  score: number;
  reason: string;
  componentResults?: GradingResult[];
}
```

### Assertion context surface (verbatim from "Using test context")

```ts
interface TraceSpan {
  spanId: string;
  parentSpanId?: string;
  name: string;
  startTime: number; // Unix timestamp in milliseconds
  endTime?: number; // Unix timestamp in milliseconds
  attributes?: Record<string, any>;
  statusCode?: number;
  statusMessage?: string;
}
interface TraceData {
  traceId: string;
  spans: TraceSpan[];
}
interface AssertionValueFunctionContext {
  // Raw prompt sent to LLM
  prompt: string | undefined;
  // Test case variables
  vars: Record<string, string | object>;
  // The complete test case
  test: AtomicTestCase;
  // Log probabilities from the LLM response, if available
  logProbs: number[] | undefined;
  // Configuration passed to the assertion
  config?: Record<string, any>;
  // The provider that generated the response
  provider: ApiProvider | undefined;
  // The complete provider response
  providerResponse: ProviderResponse | undefined;
  // OpenTelemetry trace data (when tracing is enabled)
  trace?: TraceData;
  // Shortcut to providerResponse?.metadata (provider-specific fields)
  metadata?: Record<string, any>;
}
```

### Trace-based assertion function (verbatim from "Using trace data")

```js
module.exports = (output, context) => {
  // Check if trace data is available
  if (!context.trace) {
    // Tracing not enabled, skip trace-based checks
    return true;
  }
  const { spans } = context.trace;
  // Example: Check for errors in any span
  const errorSpans = spans.filter((s) => s.statusCode >= 400);
  if (errorSpans.length > 0) {
    return {
      pass: false,
      score: 0,
      reason: `Found ${errorSpans.length} error spans`,
    };
  }
  // Example: Calculate total trace duration
  if (spans.length > 0) {
    const duration =
      Math.max(...spans.map((s) => s.endTime || 0)) - Math.min(...spans.map((s) => s.startTime));
    if (duration > 5000) {
      // 5 seconds
      return {
        pass: false,
        score: 0,
        reason: `Trace took too long: ${duration}ms`,
      };
    }
  }
  // Example: Check for specific operations
  const apiCalls = spans.filter((s) => s.name.toLowerCase().includes('http'));
  if (apiCalls.length > 10) {
    return {
      pass: false,
      score: 0,
      reason: `Too many API calls: ${apiCalls.length}`,
    };
  }
  return true;
};
```

### Causal-ordering gate over trace spans (verbatim from "Using trace data" example YAML)

```yaml
tests:
  - vars:
      query: "What's the weather?"
    assert:
      - type: javascript
        value: |
          // Ensure retrieval happened before response generation
          if (context.trace) {
            const retrievalSpan = context.trace.spans.find(s => s.name.includes('retrieval'));
            const generationSpan = context.trace.spans.find(s => s.name.includes('generation'));
            
            if (retrievalSpan && generationSpan) {
              return retrievalSpan.startTime < generationSpan.startTime;
            }
          }
          return true;
```

### Span-hierarchy-depth cap (verbatim from "Additional examples")

```js
// Check span hierarchy depth
const MAX_ALLOWED_DEPTH = 1000;
const maxDepth = (spans, parentId = null, depth = 0) => {
  if (depth > MAX_ALLOWED_DEPTH) {
    throw new Error('Span hierarchy too deep');
  }
  const children = spans.filter((s) => s.parentSpanId === parentId);
  if (children.length === 0) return depth;
  return Math.max(...children.map((c) => maxDepth(spans, c.spanId, depth + 1)));
};
if (context.trace && maxDepth(context.trace.spans) > 5) {
  return {
    pass: false,
    score: 0,
    reason: 'Call stack too deep',
  };
}
```

### Assertion-scoped `config` reuse (verbatim from "Passing assertion-specific parameters")

```yaml
tests:
  - description: 'Reuse one assertion script with two thresholds'
    vars:
      topic: 'bananas'
    assert:
      - type: javascript
        value: file://assertions/min-length.js
        config:
          minLength: 5
      - type: javascript
        value: file://assertions/min-length.js
        config:
          minLength: 20
```

```js
module.exports = (output, context) => {
  return output.length >= context.config.minLength;
};
```

### External-file and named-export loading (verbatim from "External script")

```yaml
assert:
  - type: javascript
    value: file://relative/path/to/script.js
    config:
      maximumOutputSize: 10
```

```yaml
assert:
  - type: javascript
    value: file://relative/path/to/script.js:customFunction
```

```js
// Default export
module.exports = (output, context) => {
  return output.length > 10;
};
```

```js
// Named exports
module.exports.customFunction = (output, context) => {
  return output.includes('specific text');
};
```

### The broken async external-validation example (verbatim from "External script"; the sequence `console.log(\`success: ${testResult}\`)` references an undefined variable)

```js
const VALIDATION_ENDPOINT = 'https://example.com/api/validate';
async function evaluate(modelResponse) {
  try {
    const response = await fetch(VALIDATION_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/plain',
      },
      body: modelResponse,
    });
    const data = await response.json();
    return data;
  } catch (error) {
    throw error;
  }
}
async function main(output, context) {
  const success = await evaluate(output);
  console.log(`success: ${testResult}`);
  return success;
}
module.exports = main;
```

### Inline (JS-package) form (verbatim from "Inline assertions")

```js
{
  type:"javascript",
  value: (output, context) => {
    return output.includes("specific text");
  }
}
```

### `not-javascript` example (verbatim from "Negation")

```yaml
assert:
  - type: not-javascript
    value: output.includes('error')
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/expected-outputs/javascript/ — sections as noted. All copied character-for-character from the rendered page (code blocks re-flowed only at the newline level to restore line breaks lost in HTML extraction).

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (every
    assertion type negatable via a `not-` prefix) — the generic negation
    surface underneath this page's `not-javascript` row; this note adds the
    scoring semantics of the negated form that #1287 never states.
    (Verified: #1287 Claim 10.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 12** (the
    string forms `javascript:code`, `fn:code`, `file://path`) and **Claim 6**
    (`assertScoringFunction` loaded via `file://` JS returning
    `{pass, score, reason}`) — corroborate this page's accepted string/`file://`
    loading forms and the `GradingResult` shape (Claim 1/8/10 here).
    (Verified: #1287 Claims 6, 12.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 11** (the
    built-in trace/trajectory assertion family) — the built-in counterpart to
    this page's custom-JS access to the same `context.trace` span data; both
    assert over OTel-shaped agent telemetry. (Verified: #1287 Claim 11.)
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
    **Claim 2** (three mandatory agent-span attributes) and **Claim 12** (the
    strict `<operation> <target>` span-naming convention) — the span shape
    this page's `context.trace` contract exposes; `spans.find(s =>
    s.name.includes('retrieval'))` only matches if spans are named per the
    Honeycomb prescription. (Verified: #2 Claims 2, 12.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 2**
    ("Configured scripts, webhooks, and grouped assertions may still depend
    on external services") — corroborates the hermeticity reading of Claim 9
    here: a `javascript` assertion is deterministic-by-taxonomy yet may fetch
    a remote endpoint. (Verified: #1289 Claim 2.)

- **Contradicts**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 12** (the
    trace/trajectory family "throw[s] an error rather than failing ... the
    assertion could not be evaluated" when trace data is unavailable) opposed
    by this page's canonical JS trace gate, which *passes* green under the
    same condition via `if (!context.trace) { … return true; }`. Same tool,
    same missing-trace condition, opposite verdicts — loud "not evaluated"
    (built-in) vs silent green pass (custom JS). Each family also assigns a
    different meaning to an error: a JS throw means the property failed
    (Claim 2 here), a trace-* throw means the property could not be checked.
    **Filed as contradiction issue #1307**; no verdict chosen here, per
    MINER.md §4a.
  - Same-page divergence (not filed): the "Handling objects" statement that a
    JSON-object output is already parsed as an object vs the "Inline
    assertions" statement that "Output will always be a string" — conflicting
    descriptions of the injected `output` variable when the page never states
    the config-path conditioning variable explicitly (Claim 4).

- **Extends**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` — the JS-contract
    counterpart of that note's batched-vs-sequential example (its Concrete
    Artifacts → "Batched-vs-sequential tool-call assertion" already reads
    `context.trace.spans` in a `javascript` assertion) and of its
    `trajectory:*` family (Claim 11): this page is the full
    `AssertionValueFunctionContext` / `GradingResult` contract those snippets
    invoke, plus the latency-budget/error-span/span-depth/count gates its
    Claim 12-13 family covers declaratively. (Verified: #1289 Claim 11,
    Concrete Artifacts section.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` — the deep-dive behind
    that hub page's one-line `javascript` row (#1287 Claim 12's
    `javascript:code` / `fn:code` / `file://` string forms): the typed context
    object, component results, negation scoring, and trace gates the hub page
    does not detail.
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` —
    the consumer-side contract for that producer-side instrumentation: the
    eval gate reads the same span attributes/naming (#2 Claims 2, 12) that
    the observability pipeline emits, so the gate and the instrumentation
    share one schema.

- **Novel**: First corpus coverage of the **custom-JS assertion contract**:
  1. **`not-javascript` pre-inversion threshold semantics** (Claim 3) — score
     vs verdict divergence under negation; absent from #1287's `not-` surface
     claims and from #1289's negation claims.
  2. **The `AssertionValueFunctionContext` / `TraceSpan` / `TraceData` typed
     surface** (Claim 5) — the only enumeration of `prompt`, `vars`, `test`,
     `logProbs`, `config`, `provider`, `providerResponse`, `trace`,
     `metadata`, with the provider/tracing-dependency preconditions.
  3. **The fail-open trace guard** (Claim 6) — `if (!context.trace) return true`
     on the vendor's own flagship example, the silent-pass opposite of the
     built-in throw; surfaced to the corpus via contradiction #1307.
  4. **Trace-based gates over execution flow** (Claim 6) — causal ordering,
     latency budget, error-spans, span-depth, API-call count: "test the
     action path" assertions none of the existing notes carry.
  5. **The output-shape string-vs-object ambiguity** (Claim 4) — conflicting
     statements about the injected `output` within one page.
  6. **The broken vendor async example** (Claim 9) — undefined-`testResult`
     `ReferenceError` plus non-contract return shape; the concrete case for
     "execute vendor example code before adopting it in a gate."
  7. **`config`-vs-`vars` isolation rule** (Claim 7) — assertion-scoped
     parameters vs report-column-polluting shared vars.
  8. **`GradingResult` `componentResults`/`namedScores`** (Claim 10) — nested
     sub-verdicts rendered as an inspectable detail table, the custom-JS
     analogue of `assert-set` partial-pass grouping.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement
  methodology (`guide/05-llm-ops-reliability.md:261`)**: beside the "can your
  gate actually fail?" checklist from #1287, add three custom-assertion rules:
  (a) when a release gate uses `not-javascript`, the reported/weighted score
  is the *un-inverted* score — do not read score and verdict as agreeing
  (Claim 3); (b) a `javascript` gate that throws is failing on the assertion
  function, not necessarily the model — budget unit-testing/review of the JS
  itself, and execute vendor example code before adopting it (Claims 2, 9);
  (c) the output-shape ambiguity (Claim 4) means a reused function should
  detect object-vs-string `output` rather than assume, because a shape
  mismatch throws and a throw is a hard fail.
- **Chapter 05 — trace-coupled gate health**: extend the #1289-derived rule
  that trace-based gates throw loudly when tracing is disabled, with this
  page's counter-example: the custom-JS route as documented *passes green*
  when tracing is off (Claim 6), so the guide should state the family
  explicitly — built-in `trace-*` assertions fail loud on missing trace data;
  a custom-JS gate must be written to do the same, and a release trace gate
  must not use the `if (!context.trace) return true` guard. Cross-ref the
  open contradiction #1307.
- **Chapter 02 (Observability) — trace/span attributes as assertion inputs**:
  add the eval-gate / observability contract this page documents: custom
  assertions consume the same span naming/attributes Ch02 instruments
  (`s.name.includes('retrieval')`, `statusCode`, `parentSpanId` per the
  TraceSpan shape, corroborating #2 Claims 2/12), and trace fields on
  `context` are `undefined` unless tracing is enabled (Claim 5) — so a
  trace-coupled eval suite must itself be monitored for tracing liveness.
- **Chapter 03 (Runbooks and Agents) — agent verification**: add the
  causal-ordering pattern as the concrete "did the agent do the right steps
  in the right order" gate: `retrievalSpan.startTime <
  generationSpan.startTime`, span-depth caps, latency budgets, error-span
  counts (Claim 6, Concrete Artifacts) — the action-path assertions distinct
  from output text checks.
- **Chapter 06 (Security and Trust) — red-teaming as a CI gate**: add the
  code-execution/review boundary for `file://` / inline JS (Claim 8): a
  custom assertion is committed code executed inside the eval runner (a
  supply-chain/review surface), and an async validation `fetch` puts a
  network endpoint inside the gate with no documented timeout (Claim 9).

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/javascript/).
  Single self-contained page; no sub-pages followed — the siblings
  (deterministic #1289, classifier #1288, model-graded #1305) are carved out
  as their own issues, and the page's only internal links are the hub page
  (`expected-outputs`, already mined as #1287) and the tracing docs.
- Quotes verified character-for-character against the fetched rendered
  content before writing; code blocks re-flowed only at the newline level to
  restore line breaks lost in HTML extraction (consistent with the sibling
  #1289 note's convention). Inline comment lines inside code blocks are part
  of the verbatim extracted code.
- Per the Prospector's guidance (superseding comment), the note prioritizes
  the novel, quotable, gate-integrity items: `not-javascript` pre-inversion
  scoring (Claim 3), the throw-means-fail vs throw-means-not-evaluated
  divergence (Claims 2/6, contradiction #1307), and the output string-vs-object
  ambiguity (Claim 4). The `AssertionValueFunctionContext` surface, config-vs-
  vars rule, loading/packaging mechanics, `GradingResult`/componentResults,
  and the broken async example are carried as the remaining substantive
  claims; the rest of the page's mechanics (multiline blocks, inline form
  availability) live in Concrete Artifacts.
- The determinism/hermeticity angle was NOT re-extracted: #1289 Claim 2
  already records "`javascript` with an external fetch is not deterministic
  (judge-free doesn't mean hermetic)". This note only cites that claim and
  contributes the broken-example details new to it.
- **Contradiction filed (MINER.md §4a)**: issue #1307 — this page's
  fail-open trace guard (`if (!context.trace) return true`, Claim 6) and
  throw-means-fail rule (Claim 2) vs #1289 Claim 12's throw-means-not-
  evaluated built-in behavior. Filed BEFORE this PR per the workflow, and
  referenced under **Contradicts:**. No verdict picked. Checked
  `CONTRADICTIONS.md` (only open engine entry is #1150, unrelated LiteLLM
  routing) and open `contradiction`-labeled issues before filing; newly filed
  #1307 is the only one on missing-trace semantics. The output-shape
  ambiguity within the page (Claim 4) was evaluated per the contradiction
  template's context-dependence guidance and treated as a path-dependent
  documentation gap (config vs inline paths), not filed.
- **Cross-ref verification (§4b)**: every claim citation verified by
  re-reading the cited note and locating the claim number: #1287 Claims 6,
  10, 11, 12 and #1289 Claims 2, 11, 12 verified against the note files in
  `source-notes/` before writing; #2 Claims 2/12 verified the same way. No
  claim numbers invented. Quotes from cited notes copied verbatim from those
  notes.
- **Candidate dismissal** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-promptfoo-assertions-metrics.md` — **cited heavily**
    (Corroborates/Extends, Claims 6/10/11/12): the parent hub page of the
    `javascript` assertion.
  - `docs-promptfoo-classifier-grading.md` — sibling `classifier` assert-type
    note; shares the assertion-type surface but no custom-JS contract content;
    dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` — red-team methodology/SDLC phases;
    no custom-assertion contract; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge incident triage; no
    assertion-contract surface; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated
    vendor; dismissed.
  - `docs-google-sre-team-lifecycles.md`,
    `docs-google-sre-creating-production-launch-plan.md`,
    `docs-google-sre-reliable-product-launches.md` — Google SRE book/workbook
    chapters; no LLM-eval content; dismissed.
  - `blog-promptfoo-red-team-gemini.md`, `blog-promptfoo-red-team-claude.md` —
    per-model red-team plugin config; use asserts as examples but carry no
    custom-JS mechanics; dismissed.
  - The cross-refs `docs-promptfoo-deterministic-metrics.md`,
    `docs-promptfoo-chat-threads.md`, and
    `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` were found by
    searching `source-notes/` (the Prospector's overlap list), per MINER.md
    §4. `docs-promptfoo-chat-threads.md` uses `javascript` assertions in a
    multi-turn recipe but adds no contract detail overlapping this page;
    noted, not cited.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1289, #1288): Claims 1-10 are settled-for-product-behavior
  and directly checkable against an installed CLI, but this is vendor
  documentation with no measured failure-rate, drift, or cost figures and no
  independent practitioner validation — the gate-integrity framing (score/
  verdict divergence under negation, fail-open trace guard, broken vendor
  example, output-shape ambiguity) is the Miner's analysis on top of
  documented behavior.
- `date_published` uses the page's "Last updated Sep 13, 2026" date (undated page).
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt after merge.