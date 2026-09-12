---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/
source_type: docs
title: "Promptfoo Configuration: Assertions and Metrics"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-12
date_extracted: 2026-09-12
last_checked: 2026-09-12
status: current
confidence_overall: emerging
issue: "#1287"
---

# Promptfoo Configuration: Assertions and Metrics

> The vendor reference for how promptfoo turns a test case's assertions into a
> single pass/fail gate — the weighted-average score model, test-case
> `threshold` gating, and the two config values (`threshold: 0`, `weight: 0`)
> that make a gate report green while verifying nothing, plus `assert-set`
> partial-pass grouping, custom `assertScoringFunction`s, order-dependent
> `derivedMetrics` that silently default to 0, the trace/trajectory assertion
> family that consumes OTel-shaped agent telemetry, and the offline
> `--model-outputs` replay path for already-captured production outputs.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Assertions & metrics" configuration hub page)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own assertion/scoring behavior — authoritative for what promptfoo does
  with a given config, but vendor-positioned: the page reports no measured
  gate-failure-rate, drift, or cost figures, and there is no independent
  practitioner validation. Every default, threshold, and formula on the page is
  directly checkable against an installed CLI.
- **Scope**: This is the "Assertions & metrics" hub page under
  `/docs/configuration/expected-outputs/`. It covers the assertion properties
  table, `assert-set` grouping, the full assertion-type catalogue (deterministic
  and model-assisted families), weighted scoring and test-case thresholds, the
  `assertScoringFunction` escape hatch, external `file://`/CSV assertion
  loading, assertion string syntax, `assertionTemplates` reuse, named metrics
  and `derivedMetrics`, and post-hoc assertion of captured outputs. Two sibling
  sub-pages are carved out as their own source issues (#1288 classifier,
  #1289 deterministic metrics); this note extracts the hub-page aggregation and
  scoring semantics plus the assertion families the sub-pages do not carry
  (trace/trajectory, post-hoc replay, scoring composition). Does NOT cover the
  eval-result cache (sibling #1275), dataset generation (#1277), or the
  classifier/deterministic sub-page details.
- **Last updated**: Sep 12, 2026 by renovate[bot]; the page is undated but the
  documented examples describe the current `gpt-5` era.

## Extracted Claims

### Claim 1: A test case's final score is the weighted average of its assertions' scores (per-assertion `weight` defaults to 1), and — when a test-case `threshold` is set — pass/fail is "combined weighted score ≥ threshold"
- **Evidence**: The "Weighted assertions" section's scoring formula sentence and
  the "Setting a score requirement" section's pass/fail definition.
- **Confidence**: settled (documented product behavior, directly checkable)
- **Quote**: "The final score of the test case is calculated as the weighted average of the scores of all assertions, where the weights are the `weight` values of the assertions." and "If set, the pass/fail status of a test case is determined by whether the combined weighted score of all assertions is greater than or equal to the threshold value."
- **Our assessment**: This is the aggregation model the whole gate rests on:
  partial credit is possible and expected (each failing assertion still
  contributes its 0 to the weighted mean), and the gate is a threshold on that
  mean, not logical AND over assertions. For SRE reading, this is the concrete
  answer to "how many assertions must hold for this gate to pass" — it depends
  entirely on the weights and the threshold, which makes both quantities
  reviewable config rather than magic.

### Claim 2: The documented worked example shows the partial-credit model in numbers: `equals` (w=2) failing plus `contains` (w=1) passing scores 0.33, which fails a 0.5 threshold but would pass a 0.2 threshold
- **Evidence**: The "Weighted assertions" worked example ("If the LLM output is
  `Goodbye world`…") and the "Setting a score requirement" restatement with the
  two threshold variants.
- **Confidence**: settled (vendor-worked arithmetic: verified, 1 passing-of-3
  weight-units = 1/3 ≈ 0.33)
- **Quote**: "If the LLM output is `Goodbye world`, the `equals` assertion fails but the `contains` assertion passes, and the final score is 0.33 (1/3)." and "If the LLM output is `Goodbye world`, the `equals` assertion fails but the `contains` assertion passes and the final score is 0.33. Because this is below the 0.5 threshold, the test case fails. If the threshold were lowered to 0.2, the test case would succeed."
- **Our assessment**: Buy it as the canonical partial-credit arithmetic. The
  pair of quotes makes the threshold semantics concrete and testable in a review:
  a team wanting "exactly one of these two must hold" or "the important one must
  hold" gets a precise formula, not prose. It also exposes that a threshold
  change is the single dial that can flip the gate, which matters for CI
  post-mortems ("the gate went green after a config change, not after a model
  change").

### Claim 3: A test-case `threshold` of `0` makes the case pass regardless of how many assertions fail — a silent-green-gate configuration that collects scores but cannot fail
- **Evidence**: The "Setting a score requirement" note paragraph, which the
  vendor frames as an intentional score-collection feature.
- **Confidence**: settled (documented product behavior)
- **Quote**: "A `threshold` of `0` makes the test case pass regardless of individual assertion failures, since the combined score is always at least 0. Use it to collect assertion scores without letting any single failure fail the test. The same applies to an `assert-set` threshold."
- **Our assessment**: The highest-value trap on the page for the guide. It is a
  legitimate score-collection feature, but in a CI gate it is a gate that cannot
  fail — the exact same failure family as the eval-result cache
  (`docs-promptfoo-configuration-caching.md`): a green run that evidences
  nothing. Note the vendor's own framing is observability-first ("collect
  assertion scores"), not gating — which is precisely the mismatch with how most
  teams deploy it. "Can this gate fail?" is a checkable property of the config
  (grep for `threshold: 0`, and test with a deliberate failure), not of the run.

### Claim 4: An assertion `weight` of `0` makes that assertion automatically pass — a second config value that removes an assertion's check from the gate
- **Evidence**: The "Setting a score requirement" info note
  ("If weight is set to 0, the assertion automatically passes.").
- **Confidence**: settled (documented product behavior)
- **Quote**: "If weight is set to 0, the assertion automatically passes."
- **Our assessment**: Buy it as documented behavior; it is the second
  silent-pass trap after `threshold: 0`. Two consequences for gate accounting:
  (a) an assertion whose author set `weight: 0` is not a check — it contributes
  nothing and can never fail; (b) combined with the derived-metrics pattern
  (Claim 7), `weight: 0` assertions are a *documented idiom* for carrying
  metric-only signals (e.g., the F1 example's `true_positives`/`false_positives`
  rows) that must not gate. The trap is only a trap when the `weight: 0` is
  accidental rather than intentional — same provenance question as
  `threshold: 0`.

### Claim 5: `assert-set` groups assertions under one pass condition with its own `threshold` — all-pass by default, partial-pass when a threshold is set (e.g., 0.5 for 1-of-2, or 0.25 for 1-of-4 equal-weight assertions)
- **Evidence**: The "Grouping assertions via Assertion Sets" section with the
  "cheap and fast" (all-pass) and "cheap or fast" (threshold 0.5) examples, and
  the Assertion Set properties table's `threshold` row.
- **Confidence**: settled (documented product behavior)
- **Quote**: "In the above example if all assertions of the `assert-set` pass the entire `assert-set` passes." and "Success threshold for the assert-set. Ex. 1 out of 4 equal weights assertions need to pass. Threshold should be 0.25"
- **Our assessment**: This is the "gate on most assertions rather than all"
  mechanism the triage flagged — partial-pass gating expressed declaratively.
  The same `threshold: 0` silent-pass semantics that apply at test-case level
  apply to the set ("The same applies to an `assert-set` threshold.", Claim 3),
  so every assert-set threshold is also reviewable for the can-it-fail? property.
  Useful as the concrete config for "cheap OR fast" style compound gates.

### Claim 6: Custom scoring via `assertScoringFunction` replaces weighted averaging only when every assertion carries a `metric` name — JS/Python `file://` functions returning `{pass, score, reason}`, with weighted named scores pre-normalized and `namedScoreWeights` emitted for downstream reconstruction
- **Evidence**: The "Custom assertion scoring" section: the named-metrics
  prerequisite, the two-level configuration (`defaultTest` /
  per-test override), the `file://` and named-export reference syntax, the full
  `ScoringFunction` type definition, and the weighted-normalization /
  `namedScoreWeights` statement.
- **Confidence**: settled (documented product behavior with a full interface listing)
- **Quote**: "By default, test cases use weighted averaging to combine assertion scores. You can define custom scoring functions to implement more complex logic" and "Custom scoring functions require **named metrics**. Each assertion must have a `metric` field:" and "When assertions use `weight`, each named score passed into the scoring function is already normalized as a weighted average. Eval outputs also include `namedScoreWeights` so downstream consumers can recover the weighted denominator when needed."
- **Our assessment**: The experimental escape hatch, and one with a
  determinism/pinning answer that differs from the dataset-generation surface
  (`docs-promptfoo-dataset-generation.md` Claim 5): the scoring logic is local
  JS/Python sourced via `file://`, i.e., committed code that is naturally pinned
  and reviewable in the same repo as the config — unlike LLM-synthesized
  fixtures, which the vendor ships with no pinning story. The counterpart caveat:
  nothing on the page pins the judge models behind any model-graded assertions
  feeding the named scores, so the function is deterministic but its inputs may
  not be. The `namedScoreWeights` escape hatch is the right idea for
  reconstructing the denominator in post-hoc analysis of recorded evals.

### Claim 7: `derivedMetrics` are computed in order per prompt, missing metric names silently default to 0, and there is no circular-dependency protection — a typo corrupts the composite score without any failure signal beyond `LOG_LEVEL=debug`
- **Evidence**: The "Creating derived metrics" section's ordering sentence, its
  tip note ("Derived metrics are initialized to 0 and calculated per prompt.
  Errors are logged at debug level."), the Notes list ("Missing metrics default
  to 0", "No circular dependency protection - order your metrics carefully"),
  and the "Debug errors with" command.
- **Confidence**: settled (documented product behavior; the silent-0 default is
  the vendor's own bullet)
- **Quote**: "Metrics are calculated in order, so later metrics can reference earlier ones:" and "Missing metrics default to 0" and "No circular dependency protection - order your metrics carefully"
- **Our assessment**: A third silent-corruption trap in the same family as
  Claims 3/4. A typo'd metric name in a composite like the F1 example resolves to
  `0` rather than erroring, and the only error surface is `LOG_LEVEL=debug`.
  The failure is silent in the sense that matters most: the eval still completes,
  the gate still reports, and the arithmetic is just wrong. The degradation also
  interacts with Claim 6 — derived metrics consume the same named-metric
  namespace as custom scoring, so the reference must be exact. For the guide:
  derived-metric definitions deserve review like any graph computation
  (topological order, no names invented), and CI should run a derivation sanity
  check at debug log level before trusting the composite.

### Claim 8: `__count` provides the per-prompt-provider test count so derived metrics can express averages across test cases (e.g., MAPE), with each provider tracked independently
- **Evidence**: The "Calculating averages with `__count`" section: the built-in
  variable, the MAPE example, the per-provider note, and its availability in
  JavaScript function form.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `__count` variable contains the number of test evals for the current prompt-provider combination. With multiple providers, each provider gets its own separate metrics tracked independently."
- **Our assessment**: The normalization primitive that makes derived metrics
  legitimate averages rather than raw sums. Worth extracting because
  "average across a run" is exactly what an error-rate or divergence metric needs
  to be comparable across runs of different sizes; without `__count` an
  un-normalized sum would drift with test-set size — the metric-inflation
  cousin of the measurement-portability problems in
  `blog-promptfoo-asr-not-portable-metric.md`.

### Claim 9: Already-captured LLM outputs can be scored offline via `promptfoo eval --assertions asserts.yaml --model-outputs outputs.json` — a post-hoc replay path for running a gate over production traffic that was recorded, not generated at eval time
- **Evidence**: The "Running assertions directly on outputs" section: the
  standalone-assertions framing, the outputs/asserts examples, the eval command,
  and the optional per-output `tags` structure.
- **Confidence**: settled (documented product behavior)
- **Quote**: "If you already have LLM outputs and want to run assertions on them, the `eval` command supports standalone assertion files." and "promptfoo eval --assertions asserts.yaml --model-outputs outputs.json"
- **Our assessment**: The offline counterpart to Langfuse's always-on online
  scoring (`docs-langfuse-evaluate-production-traffic.md`): rather than
  instrumenting a live rule, this replays a captured JSON array through the gate.
  The `tags` field per output is the provenance hook (attach run ID, model
  version, timestamp) — which is precisely the reporting discipline the guide
  needs so a re-scored population is attributable. Note the constraints the
  mechanism implies: the assertion pass/fail is re-evaluated on recorded outputs,
  so the capture and the scoring can disagree if the rubric changed between
  capture and replay (the re-score-comparability question already surfaced in
  the dataset notes).

### Claim 10: The assertion-type surface splits into a deterministic family ("programmatic tests") and a model-assisted family ("rely on LLMs or other machine learning models"), with every type negatable via a `not-` prefix and `is-refusal` providing deterministic refusal detection
- **Evidence**: The two assertion-catalogue subsections' framing sentences, the
  `not-` tip note, and the `is-refusal` row.
- **Confidence**: settled (documented product behavior)
- **Quote**: "These metrics are programmatic tests that are run on LLM output." and "These metrics are model-assisted, and rely on LLMs or other machine learning models." and "Every test type can be negated by prepending `not-`. For example, `not-equals` or `not-regex`."
- **Our assessment**: This boundary is the guide's concrete answer to "what can
  be checked without a judge." Deterministic checks (exact match, JSON/SQL/XML
  validation, similarity thresholds like `rouge-n`/`bleu`/`gleu`/`meteor`/
  `levenshtein`, plus cost/latency/perplexity bounds) are free of judge variance;
  model-assisted checks (similarity, classifier, moderation, llm-rubric, g-eval,
  context-* families, factuality) inherit every judge-bias problem
  `blog-promptfoo-asr-not-portable-metric.md` documents. `is-refusal` is the
  deterministic safety-gate primitive (asserts the model refused), and the
  generic `not-` negation makes the catalog compositional.

### Claim 11: promptfoo can assert directly over agent telemetry — `trace-span-count`, `trace-span-duration` (percentile support), `trace-error-spans`, `skill-used`, the `trajectory:*` family (`tool-used`, `tool-args-match`, `tool-sequence`, `step-count`), and model-judged `trajectory:goal-success`, plus a `guardrails` assertion on normalized guardrail signal
- **Evidence**: The deterministic and model-assisted catalogue rows for the
  trace/trajectory/guardrails types (verbatim in the assertion-type tables), and
  the `skill-used` row.
- **Confidence**: settled (documented assertion semantics; directly checkable)
- **Quote**: "Count spans matching patterns with min/max thresholds" and "Check span durations with percentile support" and "Detect errors in traces by status codes, attributes, and messages" and "Ensure a traced agent trajectory used specific tools" and "Use an LLM judge to decide whether the traced agent run achieved its goal" and "Evaluate the target's normalized input or output guardrail signal"
- **Our assessment**: Novel surface for the corpus, and the strongest tie to the
  observability side. These assertions consume an OTel-shaped agent trace — the
  data shape `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
  prescribes (`gen_ai.agent.name` swim lanes, `<operation> <target>` span
  naming, `error.type` propagation) — meaning the eval gate and the observability
  pipeline share one schema. Concretely: `trajectory:tool-used` /
  `:tool-sequence` can only pass if spans are named and attributed in the way the
  integration bounded, so this page is the consumer-side contract for that
  producer-side instrumentation. `trajectory:goal-success` puts an LLM judge on
  the agent run's goal attainment — model-judged, so Claim 10's
  judge-variance caveat applies.

### Claim 12: Assertion string syntax (`type:value` / `type(threshold):value`, bare values default to `equals`, `not-` negation) and the CSV `__expected` contract (exactly one assertion per column, `__expected1..N` for multiple; a provided `__expected` switches summary statistics to expected-criteria mode) let assertions be expressed without YAML objects
- **Evidence**: The "Assertion string syntax" table and the "Load assertions
  from CSV" section, including the `tests.csv` example (`fn:`/`grade:` bodies).
- **Confidence**: settled (documented product behavior)
- **Quote**: "The general format is `type:value` or `type(threshold):value`. Values without a prefix default to `equals`." and "All assertion types can be used in `__expected`. The column supports exactly one assertion." and "When the `__expected` field is provided, the success and failure statistics in the evaluation summary will be based on whether the expected criteria are met."
- **Our assessment**: Two non-YAML surfaces with the same semantics as the
  object form — relevant to the corpus because the red-team/custom-test docs
  already in source-notes use exactly these idioms (`fn:output.includes('eval')`,
  `grade:…` rubric bodies, `contains-none`). The `__expected` summary-statistics
  switch is the subtle part: adding the column changes what the eval summary
  reports, so a CSV fixture with and without `__expected` is reporting different
  statistics even for identical outputs — a reporting trap worth a footnote in
  gate-reading guidance.

### Claim 13: `assertionTemplates` + `$ref` de-duplicate repeated assertion sets and `metric` tags aggregate related assertions into named metrics visible in the UI — the reuse/aggregation layer on top of per-case assertions
- **Evidence**: The "Reusing assertions with templates" section (with the
  `containsMentalHealth` example reused across test cases) and the "Defining
  named metrics" section (the `Tone`/`Consistency` example).
- **Confidence**: settled (documented product behavior)
- **Quote**: "If you have a set of common assertions that you want to apply to multiple test cases, you can create assertion templates and reuse them across your configuration." and "Each assertion supports a `metric` field that allows you to tag the result however you like. Use this feature to combine related assertions into aggregate metrics."
- **Our assessment**: The maintenance layer that keeps assertion policy from
  forking across dozens of test cases: a single `$ref`'d template is the single
  point of truth for a policy, and `metric` tags are the named-metric namespace
  that claims 6/7 operate on. Both are the "treat your gate config like code"
  primitives — templates live in the repo, $ref'd, reviewed like any other code
  change.

## Concrete Artifacts

### Weighted-assertion worked example (verbatim from "Weighted assertions")

```yaml
tests:
  assert:
    - type: equals
      value: 'Hello world'
      weight: 2
    - type: contains
      value: 'world'
      weight: 1
```

Documented outcome: if the LLM output is `Goodbye world`, `equals` fails,
`contains` passes, final score 0.33 (1/3).

### Score-requirement example (verbatim from "Setting a score requirement")

```yaml
tests:
  threshold: 0.5
  assert:
    - type: equals
      value: 'Hello world'
      weight: 2
    - type: contains
      value: 'world'
      weight: 1
```

Documented outcome: 0.33 < 0.5 → test case fails; a 0.2 threshold would pass.

### Assert-set examples (verbatim from "Grouping assertions via Assertion Sets")

```yaml
tests:
  - description: 'Test that the output is cheap and fast'
    vars:
      example: 'Hello, World!'
    assert:
      - type: assert-set
        assert:
          - type: cost
            threshold: 0.001
          - type: latency
            threshold: 200
```

```yaml
tests:
  - description: 'Test that the output is cheap or fast'
    vars:
      example: 'Hello, World!'
    assert:
      - type: assert-set
        threshold: 0.5
        assert:
          - type: cost
            threshold: 0.001
          - type: latency
            threshold: 200
```

### Custom assertion scoring interface (verbatim from "Custom assertion scoring")

Named-metrics prerequisite:

```yaml
assert:
  - type: equals
    value: 'Hello'
    metric: accuracy
  - type: contains
    value: 'world'
    metric: completeness
```

Configuration levels:

```yaml
defaultTest:
  assertScoringFunction: file://scoring.js # Global default

tests:
  - description: 'Custom scoring for this test'
    assertScoringFunction: file://custom.js # Test-specific override
```

Function interface:

```ts
type ScoringFunction = (
  namedScores: Record<string, number>, // Map of metric names to scores (0-1)
  context: {
    threshold?: number; // Test case threshold if set
    tokensUsed?: {      // Token usage if available
      total: number;
      prompt: number;
      completion: number;
    };
  },
) => {
  pass: boolean; // Whether the test case passes
  score: number; // Final score (0-1)
  reason: string; // Explanation of the score
};
```

### Derived-metrics F1 example (verbatim from "Creating derived metrics")

```yaml
defaultTest:
  assert:
    - type: javascript
      value: output.sentiment === 'positive' && context.vars.expected === 'positive' ? 1 : 0
      metric: true_positives
      weight: 0
    - type: javascript
      value: output.sentiment === 'positive' && context.vars.expected === 'negative' ? 1 : 0
      metric: false_positives
      weight: 0
    - type: javascript
      value: output.sentiment === 'negative' && context.vars.expected === 'positive' ? 1 : 0
      metric: false_negatives
      weight: 0
derivedMetrics:
  - name: precision
    value: 'true_positives / (true_positives + false_positives)'
  - name: recall
    value: 'true_positives / (true_positives + false_negatives)'
  - name: f1_score
    value: '2 * true_positives / (2 * true_positives + false_positives + false_negatives)'
```

Derived-metrics Notes list (verbatim from the "Notes" bullet section):

- Missing metrics default to 0
- The `__count` variable is per prompt-provider combination (number of test cases)
- Functions receive a copy of the context - return values, don't mutate
- To avoid division by zero: `value: 'numerator / (denominator + 0.0001)'`
- Debug errors with: `LOG_LEVEL=debug promptfoo eval`
- No circular dependency protection - order your metrics carefully

### Post-hoc assertion of captured outputs (verbatim from "Running assertions directly on outputs")

`output.json`:

```json
["Hello world", "Greetings, planet", "Salutations, Earth"]
```

`asserts.yaml`:

```yaml
- type: icontains
  value: hello
- type: javascript
  value: 1 / (output.length + 1) # prefer shorter outputs
- type: model-graded-closedqa
  value: ensure that the output contains a greeting
```

Command:

```
promptfoo eval --assertions asserts.yaml --model-outputs outputs.json
```

Optional per-output tagging form:

```json
[
  { "output": "Hello world", "tags": ["foo", "bar"] },
  { "output": "Greetings, planet", "tags": ["baz", "abc"] },
  { "output": "Salutations, Earth", "tags": ["def", "ghi"] }
]
```

### Assertion string syntax samples (verbatim from "Assertion string syntax")

| Syntax | Type | Example |
| --- | --- | --- |
| `value` | `equals` | `Paris` |
| `contains:value` | `contains` | `contains:Paris` |
| `similar(threshold):value` | `similar` | `similar(0.8):Hello world` |
| `llm-rubric:criteria` | `llm-rubric` | `llm-rubric:Is helpful and accurate` |
| `grade:criteria` | `llm-rubric` | `grade:Does not mention being an AI` |
| `factuality:reference` | `factuality` | `factuality:Paris is the capital of France` |
| `javascript:code` | `javascript` | `javascript:output.length < 100` |
| `fn:code` | `javascript` | `fn:output.includes('hello')` |
| `python:code` | `python` | `python:len(output) > 10` |
| `file://path` | External file | `file://assertions/custom.js` |
| `not-type:value` | Negated | `not-contains:error` |
| `levenshtein(N):value` | `levenshtein` | `levenshtein(5):expected text` |

### CSV tests contract (verbatim from "Load assertions from CSV")

`tests.csv`:

```csv
text
__expected
Hello, world!
Bonjour le monde
Goodbye, everyone!
fn:output.includes('Au revoir');
I am a pineapple
grade:doesn't reference any fruits besides pineapple
```

(The `__expected` column supports exactly one assertion; multiple assertions use
`__expected1`, `__expected2`, `__expected3`, etc.)

### Assertion-template reuse (verbatim from "Reusing assertions with templates")

```yaml
assertionTemplates:
  containsMentalHealth:
    type: javascript
    value: output.toLowerCase().includes('mental health')
prompts:
  - file://prompt1.txt
  - file://prompt2.txt
providers:
  - openai:gpt-5.5
  - localai:chat:vicuna
tests:
  - vars:
      input: Tell me about the benefits of exercise.
    assert:
      - $ref: '#/assertionTemplates/containsMentalHealth'
  - vars:
      input: How can I improve my well-being?
    assert:
      - $ref: '#/assertionTemplates/containsMentalHealth'
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/expected-outputs/ — sections as noted. All copied character-for-character from the rendered page (table rows and code blocks preserved as-is).

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 8** (a warm
    eval cache means `--no-cache` + `--repeat` is required before a run is fresh
    evidence) — the caching note's thesis is "a green run may evidence nothing";
    this page supplies the *scoring-side* twins of that thesis (`threshold: 0`,
    `weight: 0`, silent-0 derived metrics). Same failure class, different
    mechanism; the two notes must be read together for the Ch05 "can your gate
    actually fail?" checklist. (Verified: #1275 Claim 8.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` **Claim 9** (run a
    no-jailbreak baseline; if baseline "success" is already high you are
    measuring noise, not the property under test) — the baseline-discipline that
    makes Claim 3/4's trap detectable in practice: a gate configured with
    `threshold: 0` or `weight: 0` will *also* pass a deliberately-injected
    negative control the same way a no-attack baseline flags a broken rubric.
    (Verified: #261 Claim 9.)
  - `source-notes/blog-promptfoo-model-upgrades-break-agent-safety.md` **Claim 1**
    (a GPT-4o→GPT-4.1 upgrade dropped a customer's injection resistance from 94%
    to 71%) — the existence proof for *why* a gate's discriminating power
    matters: a weighted-average gate that cannot fail (Claims 3/4) would have
    reported green through that regression. (Verified: #482 Claim 1.)

- **Contradicts**: None identified, and no contradiction issue filed. This is a
  first-party config reference; it opposes no existing source-note claim.
  Checked against `CONTRADICTIONS.md` (only open entry is #1150, an unrelated
  LiteLLM-routing contradiction) and open `contradiction`-labeled issues. The
  closest surfaces are mechanism differences, not claim conflicts:
  `threshold: 0`/`weight: 0` sharpening (not opposing) the caching note's
  green-gate thesis; and the `assertScoringFunction` determinism contrast with
  `docs-promptfoo-dataset-generation.md` (pinnable committed scoring code vs
  unpinnable LLM-synthesized fixtures) — a feature difference between two
  surfaces of the same tool, captured as Extends below rather than a
  contradiction. The negative-control rule of thumb: for any config value on
  this page, "does removing/reconciling this value change the gate outcome?" —
  tested by injecting a guaranteed-fail case.

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-caching.md` — extends the
    "green gate is real?" thesis from the *runtime/cache* layer to the
    *scoring/aggregation* layer: #1275 answers "was this run actually fresh?"
    and this page answers "could this gate actually have failed?"; together they
    bound the two independent config questions a CI gate review must ask.
    (Verified: #1275 Claims 4, 8.)
  - `source-notes/docs-promptfoo-dataset-generation.md` — extends the dataset
    note's reproducibility analysis with the scoring side: #1277 found generated
    *fixtures* are unpinnable; this page's `assertScoringFunction` (`file://`
    JS/Python, Claim 6) is the pinnable, committable half of the eval pipeline,
    while the model-graded assertion inputs to it remain unpinned.
    (Verified: #1277 Claim 5.)
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
    **Claims 2, 12** (the three mandatory agent spans attributes; the
    `<operation> <target>` span-naming convention) — the trace data shape that
    this page's `trace-*`/`trajectory:*` assertions consume as their input
    contract: asserting `trajectory:tool-used` or `:tool-sequence` over a trace
    only works when spans carry the naming/attribution the Honeycomb note
    prescribes. The eval gate and the observability pipeline share one schema.
    (Verified: #2 Claims 2, 12.)
  - `source-notes/docs-langfuse-evaluate-production-traffic.md` **Claim 1** (the
    Rule primitive that scores incoming live observations) — this page's
    `promptfoo eval --assertions asserts.yaml --model-outputs outputs.json`
    (Claim 9) is the *offline* complement to Langfuse's always-on online Rule:
    both replay a gate over production traffic, one as an always-on scorer, one
    as a post-hoc batch over captured outputs. (Verified: #1185 Claim 1.)
  - `source-notes/docs-promptfoo-chat-threads.md`, `source-notes/blog-promptfoo-red-team-claude.md` (Claim 10: custom test cases with `llm-rubric`/`javascript`
    asserts) and `source-notes/blog-promptfoo-red-team-gpt.md` — siblings in the
    same vendor docs/blog family that already exercise this page's assertion
    surface (string syntax, `llm-rubric`, custom JS) in red-team contexts; this
    note adds the hub-page *aggregation semantics* underneath those recipes.

- **Novel**: First corpus coverage of assertion **aggregation/scoring
  semantics** for an eval harness (the guide previously had CI-gating material
  from the caching/dataset/code-scan notes but no scoring-model reference):
  1. **The weighted-average + test-case-threshold model** (Claims 1-2) with the
     worked 0.33 < 0.5 partial-credit example — the concrete answer to "how many
     assertions must hold."
  2. **The two silent-green-gate config values** — `threshold: 0` (Claim 3) and
     `weight: 0` (Claim 4) — plus the silent-0 derived-metric default (Claim 7):
     three reviewable config properties where a gate reports green while
     verifying nothing, the scoring-layer twin of the caching note's trap.
  3. **`assert-set` partial-pass gating** with its own threshold (Claim 5) —
     "gate on most assertions" expressed declaratively.
  4. **The `assertScoringFunction` interface** (Claim 6) with the
     `{pass, score, reason}` contract and `namedScoreWeights` — the first
     documented custom-scoring surface in the corpus, and the determinism
     contrast with the synthesized-fixture path.
  5. **`derivedMetrics` order-dependence** (Claims 7-8) — the F1 example and the
     `__count` normalization primitive as reproducible artifacts.
  6. **The trace/trajectory assertion family** (Claim 11) — an eval harness
     asserting directly over OTel-shaped agent telemetry; the eval-gate/
     observability schema-sharing contract, novel vs the Honeycomb producer-side
     note (#2).
  7. **The post-hoc `--model-outputs` replay path** (Claim 9) — the offline
     scoring complement to the always-on online-scoring corpus material.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md:261` "Evaluation and measurement
  methodology")**: Add a "can your gate actually fail?" config checklist beside
  the existing eval-gating material — currently the chapter builds the caching
  trap (from #1275) but has no scoring-config checklist. New items:
  (a) forbid-or-flag `threshold: 0` on test cases and assert-sets (Claim 3)
  unless deliberately collecting scores; (b) flag `weight: 0` assertions as
  non-checks (Claim 4), distinguishing the metric-carrier idiom (F1 example)
  from accidental removal; (c) treat test-case/assert-set thresholds and
  per-assertion weights as reviewed config (Claims 1-2, 5) since they are the
  *only* dials between "pass" and "fail"; (d) run a negative control — inject a
  deliberately-failing case and confirm the gate fails (echoing #261 Claim 9's
  baseline discipline); (e) for composite scores, review `derivedMetrics` order
  and names in a topological pass with `LOG_LEVEL=debug`, since missing names
  silently become 0 (Claim 7). This is the scoring-side completion of #1275's
  green-gate thesis and belongs beside it at `guide/05-llm-ops-reliability.md`.
- **Chapter 05 — model-upgrade test corridor**: extend the #482-derived upgrade
  prescription (re-run safety suites when a model bumps): a weighted-average
  gate must *also* be verified to still discriminate after the upgrade — the
  model that silently dropped 94%→71% injection resistance
  (#482 Claim 1) could pass a threshold:0/weight:0 gate while regressing.
  Concrete rule: after a provider/model change, re-check the gate's
  fail-discrimination with a negative control, not just its green rate.
- **Chapter 03 (Runbooks and Agents) — agent/runbook verification**: add the
  trace/trajectory assertion surface (Claim 11) as the eval-gate side of the
  agent observability layer built on the Honeycomb note (#2): asserting
  `trajectory:tool-used` / `:tool-sequence` / `trace-error-spans` requires the
  OTel-shape contract from #2 (span naming `<operation> <target>`, agent-name
  attributes) to hold, so the guide should state the integration contract as a
  joint producer/consumer requirement — the tracing setup and the eval gate must
  agree on span schema or the assertions silently match nothing. `trajectory:goal-success`
  is model-judged and inherits the judge-variance caveats of #261.
- **Chapter 02 (Observability) — eval-input provenance**: extend the
  production-traffic evaluation guidance to include the *offline* replay path
  (Claim 9): `--model-outputs` re-scoring of captured outputs is the
  post-hoc/batch complement to online scoring (#1185), and per-output `tags`
  should carry provenance (run ID / model / timestamp) so a re-score is
  attributable — "replay through the gate" and "score in production" are both
  admissible, but only with the capture metadata attached.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/). Single
  self-contained page; no sub-pages followed — the two sub-page families
  (deterministic metrics, model-graded) are carved out as sibling issues #1289
  and #1288 respectively, so this note extracts the hub-page aggregation/scoring
  semantics and the assertion families the sub-pages do not carry
  (trace/trajectory, post-hoc replay). Quotes verified against the fetched
  rendered content character-for-character before writing; table rows and code
  blocks copied verbatim.
- Per the Prospector's guidance (superseding comment), the note deliberately
  avoids a *full* re-enumeration of the deterministic/model-assisted catalogues —
  Claims 10/11 summarize the taxonomy boundary and the trace/trajectory family
  as this hub page's payload, deferring the per-type deep-dives to the sibling
  extraction issues.
- **Determinism/pinning finding (triage item 5)**: the custom scoring interface
  (`assertScoringFunction`, Claim 6) *differs* from the dataset-generation
  surface in exactly the way the Prospector asked to check — scoring logic is
  local `file://` JS/Python, i.e., committed, version-controllable code, unlike
  the LLM-synthesized fixtures of #1277 which ship with no pinning story. The
  residual unpinned inputs are the judge models behind model-graded assertions.
- **Cross-ref verification (§4b)**: every cross-reference below was verified by
  re-reading the cited note and locating the cited claim number. #1275 Claims 4/8,
  #1277 Claim 5, #261 Claims 9/11, #482 Claims 1/2, #2 Claims 2/12, #1185
  Claim 1 were all located and read in full before citation. No claim numbers
  were invented.
- **Candidate dismissal** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `blog-promptfoo-owasp-red-teaming.md` — OWASP red-team methodology/SDLC
    phases (its Claim 4 touches CI/CD red-team integration, adjacent to gating
    but no assertion-aggregation content); dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — AI-incident triage by an SRE Agent
    using LLM-as-judge eval alerts; no assertion-scoring surface; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated vendor;
    dismissed.
  - `docs-google-sre-reliable-product-launches.md`,
    `docs-google-sre-team-lifecycles.md`,
    `docs-google-sre-creating-production-launch-plan.md`,
    `docs-google-sre-eliminating-toil.md` — Google SRE book/workbook chapters;
    launch process / team org / toil; no LLM-eval content; dismissed.
  - `blog-promptfoo-red-team-gemini.md`, `blog-promptfoo-red-team-claude.md` —
    red-team plugin config and reasoning-DoS strategy; use latency/rubric
    asserts as examples but carry no scoring/aggregation semantics; dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent spectrum/guardrail
    taxonomy for agent design; no assertion-gate content; dismissed.
  - The relevant cross-refs (`docs-promptfoo-configuration-caching.md`,
    `blog-promptfoo-asr-not-portable-metric.md`,
    `blog-promptfoo-model-upgrades-break-agent-safety.md`,
    `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`,
    `docs-langfuse-evaluate-production-traffic.md`,
    `docs-promptfoo-dataset-generation.md`,
    `docs-promptfoo-chat-threads.md`, the two red-team blog notes) were found by
    searching `source-notes/`, per the Prospector's guidance.
- No contradiction issue filed: verified against `CONTRADICTIONS.md` (only open
  entry is #1150, unrelated LiteLLM routing) and open `contradiction`-labeled
  issues. The threshold:0/weight:0 findings oppose no existing source claim —
  they are the scoring-layer complement to #1275's caching-layer finding, both
  sides of the same "gate green ≠ evidence" thesis.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1275, #1277): individual mechanism/default claims (Claims 1-13) are
  settled-for-product-behavior and directly checkable against an installed CLI,
  but this is vendor documentation with no measured failure-rate, drift, or cost
  figures and no independent practitioner validation — the operational-consequence
  framing (gate-cannot-fail traps, composite-corruption risk) is the Miner's
  synthesis on top of documented behavior.
- `date_published` uses the page's "Last updated Sep 12, 2026" date (undated page).