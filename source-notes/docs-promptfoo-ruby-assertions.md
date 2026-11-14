---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/ruby
source_type: docs
title: "Promptfoo Configuration: Ruby Assertions"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-30
date_extracted: 2026-09-30
last_checked: 2026-09-30
status: current
confidence_overall: emerging
issue: "#1511"
---

# Promptfoo Configuration: Ruby Assertions

> The `ruby` / `not-ruby` binding for promptfoo's custom-assertion escape
> hatch, and the part of that contract where the *runtime* is a third language:
> promptfoo resolves a `ruby` executable from the shell and fails with
> `ruby: command not found` on any standard runner image that does not
> deliberately install one, plus a `::`-namespaced method-dispatch grammar for
> `file://` loading that neither of the other two bindings has, a fourth
> independent statement of the pre-inversion `threshold` rule, a third
> instance of the fail-open trace guard, a second instance of the silent
> exception contract — and a flagstone of copy-paste from the Python sibling
> (`pass_` for a Ruby keyword collision Ruby does not have, and a score example
> written in JavaScript).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Ruby assertions"
  reference page under `/docs/configuration/expected-outputs/`, the third
  language binding in a family whose JavaScript page is mined as
  `docs-promptfoo-javascript-assertions.md` (#1304) and Python page as
  `docs-promptfoo-python-assertions.md` (#1499))
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of the tool's own `ruby` assertion behavior —
  authoritative for what the config does with a given method, but
  vendor-positioned: no measured gate-failure rate, no false-pass rate for the
  trace guard, and no independent practitioner validation. Every clause below
  is directly checkable against an installed CLI.
- **Scope**: The deep-dive page behind the `ruby` row of the parent hub page
  (`configuration/expected-outputs`, mined as #1287): the injected `output`
  variable, the `bool` / `float` / `GradingResult` return contract, the
  `AssertionValueFunctionContext` / `TraceData` / `TraceSpan` hash "type
  definitions", multiline and external (`file://`) methods, the `get_assert`
  default entrypoint and `::`-namespaced class-method dispatch, the
  `GradingResult` hash and its snake_case → camelCase field mapping,
  trace-based assertions, the `PROMPTFOO_RUBY` binary override, and `not-ruby`
  negation. Does NOT cover the deterministic assertion catalog (#1289), the
  model-graded family, the classifier type (#1288), or the JavaScript/Python
  bindings.
- **Sub-page followed**: `/docs/configuration/reference/` (the "GradingResult"
  anchor the page links from the `GradingResult types` section), read for the
  `GradingResult` and `AssertionValueFunctionContext` type declarations.
  Claim 5 and Claim 11 draw on it and say so inline. The other two links are
  the parent hub page (already mined as #1287) and `/docs/tracing/`.
- **Last updated**: Sep 30, 2026 by renovate[bot] (page footer; the page is
  otherwise undated).

## Extracted Claims

### Claim 1: promptfoo resolves the Ruby interpreter by running `ruby` from the shell, and a missing binary surfaces as a literal `"ruby: command not found"` — overridable via `PROMPTFOO_RUBY` (absolute path or bare PATH executable) — so a runner image that does not deliberately install Ruby breaks every Ruby assertion at invocation, with an error that reads as a harness crash rather than a gate result
- **Evidence**: The "Overriding the Ruby binary" section, in full: the
  default-resolution sentence, the verbatim error string, and the env-var
  override. No other section of the page mentions the interpreter, the
  subprocess, or the runner environment.
- **Confidence**: settled (documented product behavior, with the exact error
  string given)
- **Quote**: "By default, promptfoo will run `ruby` in your shell. Make sure
  `ruby` points to the appropriate executable." and "If a `ruby` binary is not
  present, you will see a "ruby: command not found" error." and "To override
  the Ruby binary, set the `PROMPTFOO_RUBY` environment variable. You may set
  it to a path (such as `/path/to/ruby`) or just an executable in your PATH
  (such as `ruby`)."
- **Our assessment**: The single most operationally load-bearing line on the
  page, and structurally the same dependency the Python sibling records
  (`docs-promptfoo-python-assertions.md` Claim 1) — but materially more likely
  to bite. `python3` is present on essentially every CI image, so a Python
  assertion usually works if the operator forgets to pin
  `PROMPTFOO_PYTHON`; **Ruby is present on almost none of them**. A GitHub
  Actions `ubuntu-latest` image, a `node:20` image, or a distroless base has no
  `ruby` on `PATH`, so a `type: ruby` gate fails on *every* test case, at
  invocation, identically — and the error text is a shell message rather than
  a promptfoo message, which is easy to misread during incident triage as the
  runner dying rather than the gate failing. Two operational consequences: pin
  `PROMPTFOO_RUBY` in the CI environment as part of the gate's definition
  (the direct analogue of Ch05's "Test in the environment you ship",
  `guide/05-llm-ops-reliability.md:47`) so the interpreter version is an
  attested input rather than an ambient property of the image; and note that
  the page documents **no** timeout, resource cap, or sandbox for the
  subprocess it spawns, so an assertion that blocks holds the gate
  indefinitely (see Cross-References → Ch06).

### Claim 2: External Ruby assertions dispatch three ways — `file://path/script.rb` (default `get_assert`), `file://path/script.rb:custom_assert` (named method), and `file://path/script.rb:Validators::Format.check_length` (a class method on a class or module in the file) — and the `get_assert` default is a Ruby/Python convention with no JavaScript equivalent
- **Evidence**: The "External .rb" section in full: the three `file://` YAML
  forms, the "append it after a colon" sentence, the class-method sentence,
  the default-entrypoint sentence, the call-signature/return-contract
  sentence, and the worked `assert.rb`.
- **Confidence**: settled (documented product behavior, with a worked example
  per rule)
- **Quote**: "You can specify a particular method to use by appending it after
  a colon:" and "You can also specify a class method on some class or module in
  the file:" and "If no method is specified, it defaults to `get_assert`." and
  "This file will be called with an `output` string and an
  `AssertionValueFunctionContext` object (see above). It expects that either a
  `bool` (pass/fail), `float` (score), or `GradingResult` will be returned."
- **Our assessment**: The `::`-namespaced selector is a loading grammar new to
  the corpus — it lets one `.rb` file host several validators as
  `Module::Class.method`, which is the Ruby-native answer to the
  one-function-per-file shape the JavaScript binding is forced into
  (`module.exports` plus optional named exports,
  `docs-promptfoo-javascript-assertions.md` Claim 8) and an organizing
  improvement on Python's single `:function_name` selector
  (`docs-promptfoo-python-assertions.md` Claim 8). The `get_assert` default
  confirms that the entrypoint convention is shared between the two
  interpreter-backed bindings and differs from the in-process JavaScript one:
  migrating an existing `file://` assertion between `javascript` and `ruby`
  changes which name the runner looks for, and a file that exports no
  `get_assert` fails at load rather than at call. Note also that `require 'json'`
  opens the vendor's own `assert.rb` example — the page ships a file with an
  unused import, evidence that this documentation block was adapted from the
  Python sibling rather than written or executed for Ruby.

### Claim 3: The page's own "return a number, treated as a score" example is JavaScript — `value: Math.log10(output.length) * 10` inside a `type: ruby` assertion — an example that cannot execute in the language it is filed under, and one whose output is far outside the score range the framework documents
- **Evidence**: The second code block of the page, verbatim, next to the
  "You may also return a number" sentence that introduces it. The `Math.`
  namespace is the JavaScript global object; the Ruby spelling is `Math` (a
  `Float` method on a number) or `Math.log10` (a module function), neither of
  which is a method on `String`, and the page's inline `value:` is an
  expression evaluated against an output string.
- **Confidence**: settled that the example is not valid Ruby as written (the
  `Math.` prefix and the `output.length` receiver are both JS idioms carried
  over from the JavaScript sibling's own `Math.log10` example); the *runtime
  behavior* of a Ruby assertion whose expression raises is **not** established
  by this source — see Claim 6.
- **Quote**: "You may also return a number, which will be treated as a score:"
  and, in the block it introduces, `value: Math.log10(output.length) * 10`
- **Our assessment**: Second instance of a Python-page artifact in the Ruby
  binding — the Python sibling carries `math.log10(len(output)) * 10`
  (`docs-promptfoo-python-assertions.md` Claim 11), correct Python spelling but
  still an unbounded score. Two things matter for a gate owner. First, the
  example cannot work: a reader who copies the vendor's second example into a
  config gets an expression that raises on the first line, and — because the
  page never says what a raise does (Claim 6) — the resulting verdict is
  undefined rather than loudly red. Second, the intended output is numerically
  absurd as a score: for a 200-character output it evaluates to ~23, far
  outside any sane range. The config reference defines the field as a "finite
  score, usually between 0 and 1" and documents nothing about clamping or
  erroring on out-of-range values, so the two best-reading sources for this
  vendor disagree on the bound without either resolving it. The practical rule
  is the same as for the JavaScript sibling's broken async example
  (`docs-promptfoo-javascript-assertions.md` Claim 9): execute vendor
  assertion examples before adopting them in a gate, and normalize every
  custom score into `[0, 1]` yourself.

### Claim 4: The page's `GradingResult` type block hedges the `pass` field as "'Can also use `pass_` if `pass` conflicts with Ruby keywords'" — but `pass` is not a Ruby keyword, and the surrounding `GradingResult` is a plain Hash literal in which `'pass'` is already used as a key, so the hedge is text carried over verbatim from the Python page
- **Evidence**: The inline comment on the `'pass'` line of the "GradingResult
  types" hash, set against every other field in the same block (no `| nil` on
  `score`, `reason`, or `'pass'`, versus `| nil` on all three optional fields),
  against the worked `assert.rb` and nested-metrics examples that write
  `'pass' => true`, and against the "Snake case support" list directly below,
  whose parenthetical reads "(or just use `pass` as a hash key)".
- **Confidence**: settled (the comment is verbatim on the page; `pass` not being
  a Ruby keyword is a language fact, not an inference about promptfoo)
- **Quote**: "'pass' => Boolean, # Can also use 'pass_' if 'pass' conflicts with
  Ruby keywords" and, from the mapping list immediately below, "`pass_` →
  `pass` (or just use "pass" as a hash key)"
- **Our assessment**: Informative as documentation archaeology and harmless as
  configuration — the hedge is if anything a *sympathy* for readers arriving
  from the Python page, where the collision is real and forces the dataclass
  plus `asdict()` step (`docs-promptfoo-python-assertions.md` Claim 2). It
  matters for two reasons. First, it is direct evidence for the "these three
  pages share one template" thesis that Claim 5 and Claim 8 corroborate, which
  is what makes a claim in one binding safe to generalize across all of them.
  Second, a Ruby author who trusts the hedge will reach for `pass_` and rely on
  the snake_case → camelCase bridge to translate it (Claim 5), adding an
  invisible transformation to a value that needed none — the mapping is silent,
  so a typo produces no error, only a verdict computed from a field the harness
  dropped. The Ruby binding is the one binding where the documented escape
  hatch is unnecessary; the correct form is the plain `'pass'` key the page's
  own examples already use.

### Claim 5: The page defines an automatic, silent snake_case → camelCase bridge for the Ruby return value — `pass_` → `pass`, `named_scores` → `namedScores`, `named_score_weights` → `namedScoreWeights`, `component_results` → `componentResults`, `tokens_used` → `tokensUsed` — identical entry-for-entry to the Python page, and its `tokens_used` entry is broader than the same page's own type block but *is* a real field of `GradingResult` per the config reference
- **Evidence**: The "Snake case support" list, quoted in full in Concrete
  Artifacts; the "GradingResult types" hash immediately above it (which has no
  `tokens_used` / `tokensUsed` member); and, from the sub-page read per MINER.md
  §1, the reference page's own `interface GradingResult` declaration, whose
  comment glosses it as "tokens consumed by the test".
- **Confidence**: settled (documented product behavior, enumerated — plus the
  reference-page confirmation that the `tokensUsed` field exists)
- **Quote**: "Ruby snake_case fields are automatically mapped to camelCase:"
  and, from the sub-page `GradingResult` interface, `tokensUsed?: TokenUsage;`
  with the trailing comment `// tokens consumed by the test`
- **Our assessment**: This is the strongest evidence that the mapping is a
  general return-contract feature of the framework rather than a Python quirk —
  two independently authored binding pages listing the same five entries in the
  same order. It also *resolves* a hazard left open by the Python note, which
  flagged `tokens_used` as "documented as mappable but not in the type
  definition" and could not say whether the field was real. The reference page
  settles it: `tokensUsed?: TokenUsage` is an optional member of the canonical
  `GradingResult`, so the assertion pages' type blocks are simply *incomplete*
  (they omit `tokensUsed`, plus the reference's `assertion`, `comment`,
  `suggestions`, and `metadata` members), not wrong. The practical shape for a
  reviewer: the mapping table is the list of *recognised* spellings, the type
  block is a subset, and because the mapping is silent a misspelled key yields
  no error — a verdict computed from a dropped field is the fail-open shape one
  layer down in the return value. Assert on the rendered eval output (does the
  named metric appear in the UI?) rather than trusting that a returned key was
  consumed. The reference page also glosses `score` as a "finite score,
  usually between 0 and 1" — hedged with "usually", which is the vendor's only
  statement anywhere about score bounds and leaves Claim 3's out-of-range
  example unresolved.

### Claim 6: A third binding documents the same fail-open trace guard — `unless context['trace'] … return true` with the comment "Tracing not enabled, skip trace-based checks" — and the page's causal-ordering example adds a second, quieter fall-through to a bare `true` when either expected span is absent; unlike the Python form, the Ruby guard is a *correct* read of a Hash, so the defect here is policy only
- **Evidence**: The "Using trace data" reference function's guard and its final
  bare `true`, plus the example YAML's trailing bare `true` — the same two
  shapes as the JavaScript sibling's artifacts, transposed to Ruby syntax
  (`context['trace']['spans']`, `s.fetch('statusCode', 0)`, `s['name'].downcase`).
- **Confidence**: settled (both guards are verbatim on the page)
- **Quote**: "When tracing is enabled, OpenTelemetry trace data is available in
  the `context['trace']` object. This allows you to write assertions based on
  the execution flow:" and, inside the function body: "Tracing not enabled,
  skip trace-based checks" / "return true"
- **Our assessment**: Third independent statement of the footgun
  `docs-promptfoo-javascript-assertions.md` Claim 6 surfaced and filed as
  contradiction **#1307**, and the direction of the escalation reverses here:
  the Python form of the guard (`hasattr(context, 'trace')` against a declared
  `TypedDict`) is *type-invalid* as well as fail-open, so under the page's own
  declaration the gate body is unreachable in every state
  (`docs-promptfoo-python-assertions.md` Claim 4); the Ruby form is a plain
  Hash subscript, exactly the correct spelling for the type the page declares,
  so the guard is a deliberate *policy* choice — skip rather than fail — and the
  error-span, latency-budget, and API-call-count checks below it are reachable
  and will fire when tracing is on. That is a useful sharpening for whoever
  resolves #1307: the policy defect is universal across bindings, the type
  defect is not. The second fail-open path is the one worth flagging to a gate
  owner: the causal-ordering YAML only returns a comparison
  `if retrieval_span && generation_span`, so a suite that means to assert
  "retrieval preceded generation" silently passes when the spans are renamed,
  the provider stops emitting them, or tracing is off — three different causes,
  one green result, and no way to tell from the report which happened. Neither
  built-in `trace-*` assertion family appears anywhere on this page, so the
  Ruby evidence speaks only to the custom-gate side of #1307. No verdict picked
  here, per MINER.md §4a; evidence posted to #1307 as a comment.

### Claim 7: The page is silent on the error contract — there is no occurrence of "raise", "exception", "throw", "error", or "timeout" anywhere in its prose or code — so what a Ruby assertion that blows up does to the gate is undocumented, the second binding to leave this open
- **Evidence**: Absence, verified over the full rendered text and all fifteen
  code blocks, against the JavaScript sibling's explicit fail-closed statement
  (`docs-promptfoo-javascript-assertions.md` Claim 2: "If your function throws
  an error, the assertion will fail and the error message will be included in
  the reason for the failure") and the Python sibling's identical silence
  (`docs-promptfoo-python-assertions.md` Claim 6). The page *does* document the
  success contract precisely ("either a `bool` (pass/fail), `float` (score), or
  `GradingResult`").
- **Confidence**: emerging — the documentation gap is a verified fact about the
  page; the runtime behavior is **not** established by this source and is
  deliberately left open. Do not assume the JavaScript fail-closed semantics
  carry over; that assumption is itself unverified.
- **Quote**: "It expects that either a `bool` (pass/fail), `float` (score), or
  `GradingResult` will be returned." (the page's complete statement of the
  contract; there is no corresponding statement for failure)
- **Our assessment**: The gap compounds rather than merely sits there, because
  this page ships an example that raises (Claim 3's `Math.log10`), a context
  hash whose keys are `fetch`-ed with defaults that quietly absorb a wrong
  shape, and an interpreter dependency that raises at invocation (Claim 1) —
  three distinct paths into undefined behavior and none of them documented. The
  three plausible runtimes are the same as the Python note's: catch-and-fail
  (JavaScript semantics), propagate-and-abort, or swallow-and-pass; the third
  is the dangerous one and it is the same shape as the guard sitting twelve
  lines above it in the same file. Our assessment is that this   is the one thing
  a release-gate owner cannot resolve by reading the vendor docs, and it costs
  one scratch config to settle: deliberately raise inside a `ruby` assertion and
  record whether the assertion goes red or the run dies. The guide rule should
  be "verify the error contract by execution", stated for the binding family
  rather than asserted as a fact about one page.

### Claim 8: The nested-metrics artifact mixes both spelling conventions inside one hash literal (`'named_scores'` and `'named_score_weights'` needing the bridge, next to an already-camelCase `'componentResults'`) and omits `reason` entirely — a field the same page's type block declares non-optional and the config reference declares as a required `string`
- **Evidence**: The "You can also return nested metrics and assertions via a
  GradingResult object" block in full, against the `'reason' => String` line of
  the type block directly beneath it (no `| nil`, unlike all three genuinely
  optional fields), against the "Multiline functions" block which likewise
  returns `GradingResult`-shaped hashes with only `pass` and `score`, and
  against the sub-page's `reason: string; // plaintext reason for outcome`.
- **Confidence**: settled (both spellings and the omissions are verbatim on the
  page; the required/optional contrast is on the page too)
- **Quote**: "'reason' => String," (the `GradingResult` type block, no `| nil`)
  and, from the sub-page `GradingResult` interface, "reason: string; // plaintext
  reason for outcome"
- **Our assessment**: Two copy-then-review hazards in one artifact. The mixed
  spellings mean a reader copying the vendor's example must know, per field,
  which side of the bridge they are on — and since the bridge is silent
  (Claim 5), getting it wrong is invisible. The missing `reason` is the sharper
  one: the page defines the field as required and then omits it from two of its
  three `GradingResult` examples, so a gate whose failure reason is the only
  thing telling an on-call engineer *why* a case went red may render a blank
  reason for the entire Ruby assertion set — which is exactly the failure mode
  Ch05's gate-readability guidance exists to prevent. The reference page's
  gloss ("plaintext reason for outcome") confirms `reason` is not optional, so
  the examples, not the type, are the defect. Worth a one-line checklist item
  next to the existing config-vs-vars hygiene rule
  (`docs-promptfoo-javascript-assertions.md` Claim 7): when a custom assertion
  returns a failure, does it return *why*?

### Claim 9: `not-ruby` restates the pre-inversion threshold rule word-for-word for a third independently authored page, and its own example returns a bool, so the vendor's example does not exercise the threshold interaction the sentence warns about
- **Evidence**: The "Negation" section's single sentence and its lone example
  (`value: output.include?('error')`), verbatim.
- **Confidence**: settled (documented product behavior, and the third
  independent vendor page to state it)
- **Quote**: "Use `not-ruby` to invert the final pass/fail result while
  preserving the returned score. Numeric scores are still compared against
  `threshold` before the result is inverted:"
- **Our assessment**: The rule itself is already extracted twice — at
  `docs-promptfoo-javascript-assertions.md` Claim 3 and
  `docs-promptfoo-python-assertions.md` Claim 9. The value of this claim is the
  *third* independent statement, which moves it from a page-level observation to
  a framework-level property, so a guide rule can be scoped to "negated custom
  assertions" rather than to one assertion type. The same caveat the Python
  note recorded applies identically: the documented `not-ruby` value evaluates
  to a bool, so the `threshold` comparison the sentence warns about never fires
  in the vendor's own example — a copied example has not tested the subtlety.

### Claim 10: Unlike the Python page, this page reads the context **consistently** as a plain Hash by string subscript — `context['prompt']`, `context['vars']['topic']`, `context['config']`, `context['trace']['spans']` — so the access-style inconsistency the Python note found has no Ruby instance
- **Evidence**: All nine context-access expressions on the page: the
  `assert.rb` example's `context['prompt']` and `context['vars']['topic']`, the
  "Using test context" YAML's `context["vars"]["example"]`, the config-reader's
  `context.fetch('config', {}).fetch('outputLengthLimit', 0)`, and the two
  trace examples' `context['trace']` / `context['trace']['spans']`. Every one
  is a Hash read; the page declares the same nine fields the other bindings do.
- **Confidence**: settled (all access expressions are verbatim and mutually
  consistent, and consistent with the Hash "type definition" the same page
  prints)
- **Quote**: "For example, if the test case has a var `example`, access it in
  Ruby like this:" and, from the config-reader example,
  `output.length <= context.fetch('config', {}).fetch('outputLengthLimit', 0)`
- **Our assessment**: A negative finding, recorded deliberately so the corpus
  does not over-generalize. `docs-promptfoo-python-assertions.md` Claim 5
  documented three mutually inconsistent access styles on the Python page
  (subscript, `.get()`, attribute) against one declared `TypedDict`, and the
  Python trace guard is unusable as written as a direct consequence. The Ruby
  page has none of that: one spelling, start to finish, matching its own type
  block. Two consequences for synthesis: the fail-open guard here should be
  described as a *policy* defect specific to the guard's shape rather than as
  the third instance of a doc/type-mismatch family (Claim 6); and the
  assertion-scoped-`config` hygiene rule transfers cleanly
  (`context.fetch('config', {})` is the `context` analogue of the
  `context.config` pattern that
  `docs-promptfoo-javascript-assertions.md` Claim 7 recommends over test `vars`),
  so a team can share one parameter-passing convention across bindings — the
  one place the three pages genuinely agree.

### Claim 11: The authoritative config reference documents the custom-assertion context contract for "JavaScript or Python assertions" only — the string `ruby` appears zero times anywhere in that reference — so the Ruby binding exists solely as a leaf page with no entry in the type-level documentation
- **Evidence**: The reference page's `AssertionValueFunctionContext` section
  (read per MINER.md §1 as the "GradingResult" link target) and a
  case-insensitive count of `ruby` versus `python` occurrences across that
  page's full article body: 0 and 7 respectively. The reference also types the
  related `assertScoringFunction` field as a JavaScript/Python path. And the
  reference's `AssertionValueFunctionContext` declares **eight** fields
  (`prompt`, `vars`, `test`, `logProbs`, `config`, `provider`,
  `providerResponse`, `trace`) — it omits the `metadata` field that all three
  binding pages declare.
- **Confidence**: settled (verified by direct count over the fetched page and by
  comparing the two type blocks)
- **Quote**: "When using JavaScript or Python assertions, your function receives
  a context object with the following interface:" and, from the same reference,
  "// OpenTelemetry trace data when tracing is enabled and the assertion uses
  trace context"
- **Our assessment**: A documentation-topology finding with a direct operational
  cost. A team that treats the config reference as the source of truth for the
  assertion contract — reasonably, since it holds the canonical
  `AssertionValueFunctionContext` and `GradingResult` declarations that Claim 5
  and Claim 8 had to go to — will conclude from it that `ruby` assertions are
  not a supported surface, or will not learn that the Ruby context is a Hash
  with a different shape from the TypeScript interface documented there. The
  reference is not merely silent on Ruby, it is *narrower than the feature
  pages* in both directions: no Ruby, and no `metadata` (which the Ruby page
  glosses as "Optional shortcut to providerResponse metadata"). So neither page
  is a superset of the other and neither can be treated as canonical on its own
  — a concrete case of a vendor's per-feature reference page and its per-feature
  type reference disagreeing about the same contract. The three binding pages
  are not peers in the docs' own structure either: JavaScript and Python each
  have an integration-level page, while Ruby's entire documented existence is
  this one leaf under `expected-outputs`. The guide-relevant form of the
  finding is about *where to pin a contract*: a vendor's feature page and its
  type declaration can each be incomplete, so a release gate's contract should
  be pinned to the feature page it actually configures **plus** a round-trip
  test (assert against a known-bad output and confirm the harness reads a red),
  not to any single reference page.

## Concrete Artifacts

### Score example as published — JavaScript inside a `type: ruby` assertion (verbatim from the page opening)

```yaml
assert:
  - type: ruby
    value: Math.log10(output.length) * 10
```

### Inline boolean example (verbatim from the page opening)

```yaml
assert:
  - type: ruby
    value: output[5..9] == 'Hello'
```

### Multiline function (verbatim from "Multiline functions") — note the returned hashes omit `reason`

```yaml
assert:
  - type: ruby
    value: |
      # Insert your scoring logic here...
      if output == 'Expected output'
        return {
          'pass' => true,
          'score' => 0.5,
        }
      end
      return {
        'pass' => false,
        'score' => 0,
      }
```

### Context type definition as printed (verbatim from "Using test context")

```ruby
# TraceSpan
{
  'spanId' => String,
  'parentSpanId' => String | nil,
  'name' => String,
  'startTime' => Integer,  # Unix timestamp in milliseconds
  'endTime' => Integer | nil,  # Unix timestamp in milliseconds
  'attributes' => Hash | nil,
  'statusCode' => Integer | nil,
  'statusMessage' => String | nil
}

# TraceData
{
  'traceId' => String,
  'spans' => Array[TraceSpan]
}

# AssertionValueFunctionContext
{
  # Raw prompt sent to LLM
  'prompt' => String | nil,

  # Test case variables
  'vars' => Hash[String, String | Object],

  # The complete test case
  'test' => Hash,  # Contains keys like "vars", "assert", "options"

  # Log probabilities from the LLM response, if available
  'logProbs' => Array[Float] | nil,

  # Configuration passed to the assertion
  'config' => Hash | nil,

  # The provider that generated the response
  'provider' => Object | nil,  # ApiProvider type

  # The complete provider response
  'providerResponse' => Object | nil,  # ProviderResponse type

  # Optional shortcut to providerResponse metadata
  'metadata' => Hash | nil,

  # OpenTelemetry trace data (when tracing is enabled)
  'trace' => TraceData | nil
}
```

This is a documentation-style object of *type descriptions*, not runnable Ruby
(no assignments, no class body) — the same shape the Python sibling page prints
as a `TypedDict`, and the shape the config reference prints as a TypeScript
`interface`. The Ruby binding's declared context is a plain Hash, which is what
makes Claim 10's uniform subscript access correct.

### `GradingResult` hash and the snake_case → camelCase bridge (verbatim from "GradingResult types" / "Snake case support")

```ruby
# GradingResult
{
  'pass' => Boolean,  # Can also use 'pass_' if 'pass' conflicts with Ruby keywords
  'score' => Float,
  'reason' => String,
  'componentResults' => Array[GradingResult] | nil,  # Component results (optional)
  'namedScores' => Hash[String, Float] | nil,  # Appear as metrics in the UI (optional)
  'namedScoreWeights' => Hash[String, Float] | nil  # Total weight per named score (optional)
}
```

```
Ruby snake_case fields are automatically mapped to camelCase:

- `pass_` → `pass` (or just use `"pass"` as a hash key)
- `named_scores` → `namedScores`
- `named_score_weights` → `namedScoreWeights`
- `component_results` → `componentResults`
- `tokens_used` → `tokensUsed`
```

`pass` is not a Ruby keyword (see Claim 4), and `tokens_used` is absent from
the hash above even though it is a real member of the canonical `GradingResult`
in the config reference (see Claim 5).

### The three `file://` dispatch forms (verbatim from "External .rb")

```yaml
assert:
  - type: ruby
    value: file://relative/path/to/script.rb
    config:
      outputLengthLimit: 10
```

```yaml
assert:
  - type: ruby
    value: file://relative/path/to/script.rb:custom_assert
```

```yaml
assert:
  - type: ruby
    value: file://relative/path/to/script.rb:Validators::Format.check_length
```

### Worked `assert.rb` and the assertion-scoped `config` reader (verbatim from "External .rb")

```ruby
require 'json'

# Default function name
def get_assert(output, context)
  puts 'Prompt:', context['prompt']
  puts 'Vars', context['vars']['topic']

  # This return is an example GradingResult hash
  {
    'pass' => true,
    'score' => 0.6,
    'reason' => 'Looks good to me',
  }
end

# Custom function name
def custom_assert(output, context)
  output.length > 10
end
```

```ruby
def get_assert(output, context)
  output.length <= context.fetch('config', {}).fetch('outputLengthLimit', 0)
end
```

### Nested metrics and component results (verbatim from "External .rb") — mixed spellings

```ruby
{
  'pass' => true,
  'score' => 0.75,
  'reason' => 'Looks good to me',
  'named_scores' => {'quality' => 0.75},
  'named_score_weights' => {'quality' => 3},
  'componentResults' => [{
    'pass' => output.downcase.include?('bananas'),
    'score' => 0.5,
    'reason' => 'Contains banana',
  }, {
    'pass' => output.downcase.include?('yellow'),
    'score' => 0.5,
    'reason' => 'Contains yellow',
  }]
}
```

`'named_scores'` and `'named_score_weights'` are snake_case and rely on the
automatic mapping; `'componentResults'` is already camelCase. The page's
weight arithmetic for this artifact: "The `quality` metric contributes
`0.75 × 3 = 2.25` to its weighted total, with weight `3`, so it displays as
75%."

### Trace-based assertion function (verbatim from "Using trace data")

```ruby
def get_assert(output, context)
  # Check if trace data is available
  unless context['trace']
    # Tracing not enabled, skip trace-based checks
    return true
  end

  # Access trace spans
  spans = context['trace']['spans']

  # Example: Check for errors in any span
  error_spans = spans.select { |s| s.fetch('statusCode', 0) >= 400 }
  if error_spans.any?
    return {
      'pass' => false,
      'score' => 0,
      'reason' => "Found #{error_spans.length} error spans"
    }
  end

  # Example: Calculate total trace duration
  if spans.any?
    duration = spans.map { |s| s.fetch('endTime', 0) }.max - spans.map { |s| s['startTime'] }.min
    if duration > 5000  # 5 seconds
      return {
        'pass' => false,
        'score' => 0,
        'reason' => "Trace took too long: #{duration}ms"
      }
    end
  end

  # Example: Check for specific operations
  api_calls = spans.select { |s| s['name'].downcase.include?('http') }
  if api_calls.length > 10
    return {
      'pass' => false,
      'score' => 0,
      'reason' => "Too many API calls: #{api_calls.length}"
    }
  end

  true
end
```

This is the same gate the JavaScript sibling documents
(`docs-promptfoo-javascript-assertions.md` Claim 6 / Concrete Artifacts) with
the guard rewritten as `unless context['trace']` — a valid Hash read, unlike the
Python sibling's `hasattr` form. The trace *patterns* (error spans ≥400,
duration > 5000ms, >10 http calls) are not re-claimed as new here.

### Causal-ordering gate (verbatim from "Using trace data" example YAML) — second fail-open path in the trailing `true`

```yaml
tests:
  - vars:
      query: "What's the weather?"
    assert:
      - type: ruby
        value: |
          # Ensure retrieval happened before response generation
          if context['trace']
            spans = context['trace']['spans']
            retrieval_span = spans.find { |s| s['name'].include?('retrieval') }
            generation_span = spans.find { |s| s['name'].include?('generation') }

            if retrieval_span && generation_span
              return retrieval_span['startTime'] < generation_span['startTime']
            end
          end
          true
```

### Vars access example (verbatim from "Using test context")

```yaml
tests:
  - description: 'Test with context'
    vars:
      example: 'Example text'
    assert:
      - type: ruby
        value: 'output.include?(context["vars"]["example"])'
```

### `not-ruby` example (verbatim from "Negation")

```yaml
assert:
  - type: not-ruby
    value: output.include?('error')
```

### Canonical `GradingResult` fields the assertion page's type block omits (verbatim from the sub-page `/docs/configuration/reference/`)

```ts
interface GradingResult {
  pass: boolean; // did test pass?
  score: number; // finite score, usually between 0 and 1
  reason: string; // plaintext reason for outcome
  namedScores?: Record<string, number> | null; // labeled metrics attached to this result
  namedScoreWeights?: Record<string, number> | null; // weighted denominator for namedScores
  tokensUsed?: TokenUsage; // tokens consumed by the test
  componentResults?: GradingResult[] | null; // nested component results
  assertion?: Assertion; // source assertion
  comment?: string; // user comment
  suggestions?: ResultSuggestion[]; // suggested follow-up actions
  metadata?: {
    pluginId?: string;
    strategyId?: string;
    context?: string | string[];
    contextUnits?: string[];
    renderedAssertionValue?: string;
    renderedGradingPrompt?: string;
    graderError?: true;
    [key: string]: any;
  };
}
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/expected-outputs/ruby — sections as noted — plus the sub-page
https://www.promptfoo.dev/docs/configuration/reference/ for the last block. All
copied character-for-character from the rendered pages (code blocks re-flowed
only at the newline level to restore line breaks lost in HTML extraction,
consistent with the sibling notes #1304 and #1499). Inline comment lines inside
code blocks are part of the verbatim extracted code; inline `<code>` spans in
prose are rendered as backticks, also matching the sibling notes' convention.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-python-assertions.md` **Claim 3** (the
    snake_case → camelCase return-field bridge — `pass_` → `pass`,
    `named_scores` → `namedScores`, `named_score_weights` →
    `namedScoreWeights`, `component_results` → `componentResults`,
    `tokens_used` → `tokensUsed`) — the Ruby page lists the **same five entries
    in the same order**, so the mapping is a general return-contract feature of
    the framework rather than a Python quirk (Claim 5 here), and this page's
    `get_assert`-era parenthetical "(or just use `pass` as a hash key)" is
    character-identical to the Python list's parenthetical. This note also
    *resolves* the open hazard in that claim: `tokensUsed?: TokenUsage` is a
    real member of the canonical `GradingResult` per the config reference, so
    the assertion pages' type blocks are incomplete rather than the field
    fictitious. (Verified: Python note Claim 3, re-read in the note file; field
    verified against the reference page.)
  - `source-notes/docs-promptfoo-python-assertions.md` **Claim 6** (the Python
    page "never states what happens when a Python assertion raises — an
    undocumented contract") — the Ruby page is silent in the same way, and with
    more exposure: it also documents a raising example (Claim 3) and an
    interpreter that raises at invocation (Claim 1). Two independently authored
    pages, same gap, so "verify the error contract by execution" is a
    binding-family rule (Claim 7 here). (Verified: Python note Claim 6.)
  - `source-notes/docs-promptfoo-python-assertions.md` **Claim 8** (external
    `file://` loading, the `:function_name` selector, and the `get_assert`
    default entrypoint) — Ruby's forms are the same convention with one
    addition: the `::`-namespaced class-method dispatch, which Python does not
    document (Claim 2 here). Reading the two notes together establishes
    `get_assert` as the convention for both interpreter-backed bindings and
    `module.exports` as the in-process one. (Verified: Python note Claim 8.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 3**
    (`not-javascript` inverts the verdict "while preserving the returned
    score", with numeric scores compared against `threshold` *before*
    inversion) — restated word-for-word as `not-ruby` (Claim 9 here) and, per
    Python note Claim 9, already as `not-python`. Three independently authored
    pages state the same rule. (Verified: JS note Claim 3, re-read in the note
    file.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 5** (the
    `AssertionValueFunctionContext` surface — `prompt`, `vars`, `test`,
    `logProbs`, `config`, `provider`, `providerResponse`, `trace`, `metadata`,
    with `trace` present "only when tracing is enabled") — the Ruby page
    declares the same nine fields with the same tracing-conditional comment and
    the same `# Contains keys like "vars", "assert", "options"` gloss on `test`,
    so the context surface is shared across bindings even as its *runtime type*
    differs (Hash here, `TypedDict` in Python, `interface` in JavaScript).
    (Verified: JS note Claim 5.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 7**
    (prefer assertion-level `config` over test `vars`, which "are shared across
    all assertions and appear as report columns") — the Ruby config-reader
    example `context.fetch('config', {}).fetch('outputLengthLimit', 0)` is the
    same parameter-scoping pattern with a Ruby signature, and the one surface
    on which all three binding pages genuinely agree (Claim 10 here).
    (Verified: JS note Claim 7.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 6** (custom
    scoring via `assertScoringFunction`: "JS/Python `file://` functions
    returning `{pass, score, reason}`", with `namedScoreWeights` emitted for
    downstream reconstruction) — this page is the third custom-assertion route
    behind the same `file://` prefix, and its nested-metrics artifact exercises
    the `named_scores` / `named_score_weights` spelling that the hub's "named
    scores already normalized as a weighted average" rule depends on. Note the
    hub's own field list says "JS/Python", like the config reference (Claim 11).
    (Verified: #1287 Claim 6.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (every
    assertion type is negatable via a `not-` prefix) — `not-ruby` is the Ruby
    instance of that surface. (Verified: #1287 Claim 10.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 2**
    ("Deterministic" means no model judge, not no external dependency — scripts
    may "depend on external services") — the Ruby binding adds a fourth class
    of non-hermetic dependency: whether the runner image has a `ruby` on `PATH`
    at all (Claim 1). A `type: ruby` gate is not even hermetically *executable*
    until the image is amended. (Verified: #1289 Claim 2.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 14**
    (budget/precondition gates carry hidden requirements — `latency` needs
    `--no-cache`, `perplexity` needs provider `logprobs`) — the Ruby page adds
    the interpreter precondition as a third class of hidden requirement, and a
    sharper one than either of those, because unlike a missing API feature the
    failure happens before the model is ever called. (Verified: #1289
    Claim 14.)

- **Contradicts**:
  - **Contradiction issue #1307** (open; "promptfoo missing-trace semantics:
    built-in `trace-*` assertions throw ('could not be evaluated') vs custom-JS
    trace gate passes green when tracing is off"). This page does **not** create
    a new contradiction — it supplies a third instance of the fail-open guard
    (Claim 6) and sharpens the existing one in a way the resolver needs: the
    *policy* defect is universal across all three documented bindings, while
    the *type* defect found on the Python page (`hasattr` against a `TypedDict`,
    making the gate body unreachable) is **not** present here, because
    `unless context['trace']` is a correct Hash read. The Ruby page says
    nothing about the built-in `trace-*` family, so it speaks only to the
    custom-gate side. Evidence and the verbatim guards posted as a comment on
    #1307. No verdict picked here, per MINER.md §4a.
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 12** (the
    trace/trajectory family "throw[s] an error rather than failing, indicating
    that the assertion could not be evaluated" when trace data is unavailable)
    opposed by this page's custom-Ruby gate, which returns `true` on the same
    condition — and by its causal-ordering example, which additionally falls
    through to `true` when the *expected spans* are missing even with tracing
    on. Same tool, same missing-trace precondition, opposite verdicts; and the
    two error semantics are different in kind (a JS/Ruby throw means the
    property failed; a trace-* throw means the property could not be checked).
    This is the Ruby side of #1307; recorded at claim level so the Smith sees
    the full evidence set. (Verified: #1289 Claim 12.)
  - **Same-page documentation inconsistencies (recorded, not filed)**, per
    MINER.md §4a's context-dependence carve-out and the Prospector's explicit
    guidance: (a) a JavaScript score example inside a `type: ruby` assertion
    (Claim 3); (b) a `pass` / Ruby-keyword hedge where Ruby has no such keyword
    and the surrounding block already uses `'pass'` as a hash key (Claim 4);
    (c) `reason` declared non-optional and then omitted from two of the page's
    own `GradingResult` examples (Claim 8); (d) a type block narrower than the
    canonical `GradingResult` in the config reference (Claim 5). Each is a
    contract slip *within* the vendor's own docs with the same operational
    answer — execute the example, pin the contract in reviewed code, and settle
    the error contract by experiment — so filing four issues for documentation
    slips would bury the substantive one (#1307). This mirrors the judgment
    recorded in `docs-promptfoo-python-assertions.md`'s Contradicts section for
    the same class of defect on the sibling page.

- **Extends**:
  - `source-notes/docs-promptfoo-javascript-assertions.md` — this page is the
    Ruby binding of that note's contract, and supplies the one thing its
    in-process binding structurally cannot: an interpreter-resolution
    dependency on the runner image (Claim 1), plus `::`-namespaced method
    dispatch (Claim 2) and a documentation topology in which the Ruby binding
    has no entry in the type reference at all (Claim 11). Read the three
    binding notes as one contract with language-specific failure modes.
  - `source-notes/docs-promptfoo-python-assertions.md` — this page is the Ruby
    counterpart of that note and contributes: the sharper interpreter
    dependency (Ruby is absent from standard images where `python3` is not),
    the `::`-namespaced dispatch grammar, a *resolving* piece of evidence for
    its `tokens_used` hazard, the mixed-spelling and missing-`reason` details
    of its nested-metrics artifact, and the negative finding that the Ruby page
    has no access-style inconsistency (Claim 10) — which bounds the Python
    note's Claim 5 rather than confirming it.
  - `source-notes/docs-promptfoo-assertions-metrics.md` — the threshold and
    weighted-average machinery this page's return values feed into: #1287
    Claim 1's "combined weighted score ≥ threshold" is the `threshold` named in
    the `not-ruby` sentence, and is what makes an out-of-range score (Claim 3)
    or a silently-unmapped key (Claim 5) consequential rather than cosmetic.
  - `source-notes/docs-promptfoo-deterministic-metrics.md` — the
    "deterministic means judge-free, not hermetic" framing (#1289 Claim 2)
    gains its most extreme instance: for `type: ruby`, the gate's
    *executability* depends on the image.

- **Novel**: Nothing in the corpus covered the Ruby binding before this note;
  verified by grep — the strings `not-ruby`, `PROMPTFOO_RUBY`, and
  `expected-outputs/ruby` appear nowhere in `source-notes/` or `guide/`
  beforehand. New to the corpus:
  1. **Interpreter resolution for Ruby, with the verbatim `ruby: command not
     found`** (Claim 1) — `PROMPTFOO_RUBY`, and the observation that Ruby
     (unlike `python3`) is absent from essentially every CI image, so this
     dependency is the sharpest in the binding family.
  2. **`::`-namespaced class-method dispatch** (Claim 2) — a `file://` loading
     grammar new to the corpus; the only documented way to host several
     validators in one file.
  3. **A JavaScript score example published inside a `type: ruby` assertion**
     (Claim 3) — plus the vendor's own unbounded-score example, against the
     reference page's hedged "finite score, usually between 0 and 1".
  4. **The `pass_`-for-Ruby-keywords hedge and the shared five-entry mapping
     table** (Claims 4–5) — direct evidence that the three binding pages are
     written from one template, which is what licenses generalizing a
     documented rule across them.
  5. **Resolution of the `tokens_used` / `tokensUsed` question** (Claim 5) via
     the config reference, which the Python note could not close.
  6. **The fail-open trace guard with a *correct* guard type** (Claim 6) — the
     evidence that distinguishes the universal policy defect from the
     Python-only type defect, plus a second fail-open path in the trailing bare
     `true` of the causal-ordering example.
  7. **Uniform, consistent context access** (Claim 10) — a negative finding that
     bounds the Python page's three-access-style claim.
  8. **Ruby-binding omission from the authoritative config reference** (Claim
     11) — `ruby` appears zero times in the page that defines the canonical
     `AssertionValueFunctionContext` and `GradingResult` types, whose
     `AssertionValueFunctionContext` is also one field (`metadata`) narrower
     than the feature pages' own declarations.
  9. **The missing `reason` in the vendor's own `GradingResult` examples**
     (Claim 8) — a gate-readability defect, not merely a doc typo.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "Test in the environment you ship"
  (`guide/05-llm-ops-reliability.md:47`)**: add the Ruby case as the sharpest
  instance of the rule. A `type: ruby` gate adds an interpreter-resolution
  dependency to the runner image and the documented default resolves the bare
  command `ruby` (Claim 1), which unlike `python` (Python note Claim 1) is not
  on standard CI images — so the whole Ruby assertion set goes red at invocation
  with a shell error string that reads like a harness crash. The rule: the
  language a custom assertion runs in is a *pinned gate input*; set
  `PROMPTFOO_RUBY` (or `PROMPTFOO_PYTHON`) in the CI environment as part of the
  gate's definition, and add an interpreter-presence precondition to the same
  negative-control check the guide already asks for — one deliberately-wrong
  case that must fail. Pair it with the timeout/resilience note: the page
  documents no timeout or resource cap for the subprocess.
- **Chapter 05 — "A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: the table's last row currently reads
  "Custom-JS trace gate written with the vendor's own guard …
  [source: docs-promptfoo-javascript-assertions, Claim 6]". Generalize that row
  to the binding family and add two new rows, all three from this page:
  1. **Custom trace gate in any documented binding, written with the vendor's
     own guard** — `if (!context.trace) return true` /
     `unless context['trace'] … return true` / `if not hasattr(context,
     'trace') … return True`: three independently authored vendor pages ship
     this guard (Claim 6 here; JS note Claim 6; Python note Claim 4). Cite
     contradiction #1307, no verdict. Note for the Smith: the *policy* is
     universal, the *type* defect is Python-only, so the row should not imply
     the Ruby guard is broken in the same way.
  2. **Causal-ordering trace gate whose comparison is conditional** — the
     trailing bare `true` passes when either expected span is absent, which
     conflates "tracing off", "provider stopped emitting these spans", and
     "spans renamed" into one green result (Claim 6, Concrete Artifacts).
  3. **Custom assertion returning a score with no `reason`** — the vendor's own
     `GradingResult` type declares `reason` non-optional and then omits it from
     the page's examples (Claim 8); a Ruby gate can therefore report red with
     a blank cause. Add "every custom assertion that returns a failure returns
     *why*" to the suite checklist alongside the existing `config`-vs-`vars`
     hygiene rule (JS note Claim 7).
- **Chapter 05 — "Read the assert's own defaults before trusting its verdict"
  (`guide/05-llm-ops-reliability.md:443`)**: extend the Python note's proposed
  "a custom assertion's contract is four things you must read" (return shape,
  field spelling, context access, error contract) to a fifth and a sixth
  visible on this page: the **score range** (the vendor's own example evaluates
  to ~23 for a 200-char output, against the reference page's hedged "finite
  score, usually between 0 and 1" — Claim 3) and the **interpreter/runtime
  precondition** (Claim 1). Both are contract properties readable from the
  vendor's own pages and both change a verdict without touching the output.
- **Chapter 05 — negation**: `not-ruby` is the third independent statement of
  the pre-inversion threshold semantics (Claim 9; JS note Claim 3, Python note
  Claim 9), so restate the existing `not-javascript` guidance as applying to
  negated *custom* assertions generally rather than to one assertion type. Carry
  the caveat forward from the Python note: the vendor's own `not-ruby` example
  returns a bool, so the `threshold` interaction the sentence warns about is not
  exercised by the example a reader would copy.
- **Chapter 02 (Observability) — trace-coupled gates**: add the Ruby instance
  of the coupling rule. A trace-coupled Ruby eval suite's health is coupled to
  the tracing pipeline's health, and the documented guard converts "tracing is
  off" into green; the context is a Hash keyed by string (`context['trace']`,
  `s.fetch('statusCode', 0)`), so a trace gate here needs a negative control
  that runs with tracing disabled and *requires* a red — the only way to catch
  both the fail-open policy and the missing-span fall-through (Claim 6).
  Cross-ref contradiction #1307.
- **Chapter 06 (Security and Trust) — "Gating on LLM security scans"
  (`guide/06-security-and-trust.md:768`) and "Pin everything; verify releases"
  (`guide/06-security-and-trust.md:636`)**: a `file://` Ruby assertion is
  committed repo code executed by a subprocess with the runner's privileges,
  and this page documents no sandbox, timeout, or resource cap for it (Claims
  1, 2). The `::`-namespaced dispatch (Claim 2) makes multi-validator `.rb`
  files practical, which raises the number of entry points a review has to
  cover — review `file://*.rb` hooks with the same weight as pipeline code, and
  treat the runner image's Ruby installation as part of the pinned, attested
  artifact set, since `PROMPTFOO_RUBY` is now part of the gate's definition.
- **Chapter 05 — vendor contract provenance (new, small)**: the documentation
  topology finding (Claim 11) is worth one line in gate-review guidance: a
  vendor's per-feature reference page and its per-feature *type* reference can
  disagree   about whether a feature exists (promptfoo's config reference names
  only JavaScript and Python for the assertion context contract, the string
  `ruby` appears nowhere in it, and its context interface is one field
  narrower than the feature pages'). Pin a gate's contract to the feature page
  it actually configures plus a round-trip test, not to the type reference.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/ruby), plus
  one linked page read in full per MINER.md §1:
  https://www.promptfoo.dev/docs/configuration/reference/ (the `GradingResult`
  anchor target). Claims 5, 8, and 11 draw on it and mark it inline. The
  page's only other links are the parent hub page (`configuration/expected-
  outputs`, already mined as #1287) and `/docs/tracing/`, neither followed —
  the hub is already covered by #1287 and the tracing docs carry no
  assertion-contract content. Note there is **no** Ruby equivalent of the
  `/docs/integrations/python/` page that the Python note followed, so no
  pipeline-wide Ruby hooks exist to extract.
- Quotes verified character-for-character against the fetched rendered content
  before writing; the source HTML was parsed at the token level so code blocks
  are reproduced with their original line structure. Code blocks re-flowed only
  at the newline level, matching the convention of the sibling notes #1304 and
  #1499. Inline `<code>` spans inside prose are rendered as backticks, also
  matching those notes. Inline comment lines inside code blocks are part of the
  verbatim extracted code.
- Per the Prospector's guidance (two triage comments, consistent), this note
  extracts the **Ruby deltas** only. Not re-extracted, because already settled
  in `docs-promptfoo-javascript-assertions.md`: the injected-`output` variable
  and the bool/number/`GradingResult` return union (JS Claim 1), the
  `AssertionValueFunctionContext` field list (JS Claim 5), the trace-gate
  *patterns* — error spans ≥400, latency >5000ms, >10 http calls, span-hierarchy
  depth, retrieval-before-generation ordering (JS Claim 6) — the
  `config`-over-`vars` hygiene rule (JS Claim 7), the `file://` loading
  mechanics (JS Claim 8), and the `GradingResult` / `componentResults` shape
  (JS Claim 10). Those are cited, not re-claimed; the "third instance of the
  fail-open guard" is claimed only as a *pattern across bindings*, with the
  JS/Python claim numbers attached.
- **Claim 7's absence was verified mechanically**, not by impression: the
  rendered page text and all fifteen code blocks were searched for
  "raise", "exception", "throw", "rescue", and "timeout", each with **zero**
  occurrences. The seven occurrences of "error" are all unrelated to an
  exception contract — six are the trace example's error-*span* comments
  (`# Example: Check for errors in any span`, `error_spans`,
  `"Found #{error_spans.length} error spans"`), one is the interpreter section's
  `"ruby: command not found" error` (Claim 1), and one is the string literal
  `output.include?('error')` in the `not-ruby` example.
- **No contradiction filed** (MINER.md §4a). Checked `CONTRADICTIONS.md` and
  every open `contradiction`-labeled issue first: the only missing-trace
  contradiction is **#1307**, already open and already carrying the JavaScript
  and Python evidence, and this page says nothing about the built-in `trace-*`
  family, so there is no new pair of opposing claims. The page's four
  documentation slips (Claims 3, 4, 5, 8) are within-source inconsistencies of
  the same class the Python note judged not worth filing, each with the same
  operational answer. Evidence for #1307 was posted there as a comment instead.
- **Cross-ref verification (§4b)**: every claim citation verified by re-reading
  the cited note and locating the claim number in `source-notes/` — Python note
  Claims 3, 6, 8; JS note Claims 3, 5, 7; #1287 Claims 1, 6, 10; #1289 Claims 2,
  12, 14. No claim numbers guessed; quotes from cited notes paraphrased in
  Cross-References rather than presented as source-note quotes, so no fabricated
  quote risk.
- **Candidate handling** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — each cited or dismissed
  by name):
  - `docs-promptfoo-javascript-assertions.md` — **cited heavily** (Corroborates
    Claims 3/5/7, Contradicts via #1289 Claim 12, Extends): the direct sibling
    note and owner of the shared gate contract.
  - `docs-promptfoo-assertions-metrics.md` — **cited** (Corroborates Claims 6,
    10; Extends): the parent hub page.
  - `docs-promptfoo-classifier-grading.md` — sibling `classifier` assert-type
    note; shares the assertion-type surface but carries no custom-assertion
    contract or language-binding content; dismissed.
  - `docs-promptfoo-pi-scorer.md` — the `pi` grader; no custom-assertion
    contract and no binding-specific content; dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` — red-team methodology and SDLC
    phases; no custom-assertion contract; dismissed.
  - `blog-promptfoo-red-team-gemini.md` — per-model red-team plugin config; uses
    asserts as examples but carries no custom-assertion mechanics; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge incident triage; no
    assertion-contract surface; dismissed.
  - `docs-litellm-batches-api.md` — LiteLLM gateway batching docs; unrelated
    vendor and unrelated topic; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated vendor;
    dismissed.
  - `docs-google-sre-team-lifecycles.md` — Google SRE workbook chapter; no
    LLM-eval content; dismissed.
  - **Found by searching `source-notes/`** (per MINER.md §4, not in the
    candidate list): `docs-promptfoo-python-assertions.md` — the direct sibling
    and the single most important cross-reference on this page (Corroborates
    Claims 3/6/8, Extends, and the Novel items' resolution in Claim 5); and
    `docs-promptfoo-deterministic-metrics.md` (Contradicts Claim 12, Corroborates
    Claims 2 and 14). `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
    was considered and deliberately **not** cited: this page's trace *patterns*
    and span-naming assumptions are identical to JS note Claim 6's, so the OTel
    producer cross-reference already stands in that note — duplicating it would
    add nothing.
- `confidence_overall` is `emerging`, matching the three sibling promptfoo
  config notes (#1287, #1289, #1304, #1499): the documented claims are settled
  as product behavior and directly checkable against an installed CLI, but this
  is vendor documentation with no measured false-pass rate, no drift or cost
  figures, and no independent practitioner validation — and the gate-integrity
  findings (the shipped JavaScript example, the keyword hedge, the
  undocumented error contract, the missing `reason`, the fail-open guard) are
  Miner's analysis on top of documented behavior. Claims 3, 6, 7, and 8 each
  carry their own lower confidence rating where the runtime behavior is not
  established by the source.
- `date_published` uses the page footer's "Last updated on Sep 30, 2026 by
  renovate[bot]" date (undated page). Note the Prospector's triage comment
  read that footer as "Sep 29, 2026 by dawn" — the page was re-updated between
  triage and extraction; the content quoted here is the Sep 30 revision.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt after merge.
