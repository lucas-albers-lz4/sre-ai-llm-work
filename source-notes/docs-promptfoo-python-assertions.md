---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/python/
source_type: docs
title: "Promptfoo Configuration: Python Assertions"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-29
date_extracted: 2026-09-30
last_checked: 2026-09-30
status: current
confidence_overall: emerging
issue: "#1499"
---

# Promptfoo Configuration: Python Assertions

> The `python` / `not-python` binding for the custom-assertion escape hatch —
> and, unlike its JavaScript sibling, the part of that contract where the
> *runtime* is a second language: promptfoo resolves a `python` executable
> from the shell and fails with `python: command not found` when the CI image
> ships only `python3`, the return shape crosses a snake_case → camelCase
> bridge that exists because `pass` is a reserved keyword in Python, and the
> page's own flagship trace gate is fail-open in a way the JavaScript page's
> is not — a guard written with `hasattr` against a context the same page
> declares a `TypedDict`.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Python
  assertions" reference page under `/docs/configuration/expected-outputs/`,
  the language-binding sibling of the already-mined "Javascript assertions"
  page #1304)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of the tool's own `python` assertion behavior —
  authoritative for what the config does with a given function, but
  vendor-positioned: no measured gate-failure rate, no false-pass rate for the
  trace guard, and no independent practitioner validation. Every clause below
  is directly checkable against an installed CLI.
- **Scope**: The deep-dive page behind the `python` row of the parent hub page
  (`configuration/expected-outputs`, mined as #1287): the injected `output`
  variable, the `bool | float | GradingResult` return contract, the
  `AssertionValueFunctionContext` / `TraceData` / `TraceSpan` type
  definitions, multiline and external (`file://`) functions, the
  `GradingResult` dataclass and its snake_case → camelCase field mapping,
  trace-based assertions, the `PROMPTFOO_PYTHON` binary override, and
  `not-python` negation. Does NOT cover the deterministic assertion catalog
  (#1289), the model-graded family, the classifier type (#1288), or the
  JavaScript binding (#1304).
- **Sub-page followed**: `/docs/integrations/python/` (the "Python Overview"
  link the page opens with), read in full — it establishes the execution model
  (a TypeScript/Node tool invoking Python for the whole eval pipeline), the
  `PYTHONPATH` / `LOG_LEVEL=debug` configuration knobs, and a per-provider
  `pythonExecutable` override that the assertions page never mentions. Claims
  1, 10, and 11 draw on it and say so inline.
- **Last updated**: Sep 29, 2026 by mldangelo-oai (footer of both pages; the
  pages are otherwise undated).

## Extracted Claims

### Claim 1: promptfoo resolves the Python interpreter by running `python` from the shell, and a missing binary surfaces as a literal `"python: command not found"` — overridable via `PROMPTFOO_PYTHON` (absolute path or bare PATH executable) — so a slim CI image that ships only `python3` breaks every Python assertion at invocation
- **Evidence**: The "Overriding the Python binary" section, in full: the
  default-resolution sentence, the verbatim error string, and the env-var
  override. Extended by the sub-page's per-provider `pythonExecutable` YAML
  override and its `export PROMPTFOO_PYTHON=/path/to/python3` example.
- **Confidence**: settled (documented product behavior, with the exact error
  string given)
- **Quote**: "By default, promptfoo will run `python` in your shell. Make sure
  `python` points to the appropriate executable." and "If a `python` binary is
  not present, you will see a "python: command not found" error." and "To
  override the Python binary, set the `PROMPTFOO_PYTHON` environment variable.
  You may set it to a path (such as `/path/to/python3.11`) or just an
  executable in your PATH (such as `python3.11`)."
- **Our assessment**: This is the single most operationally load-bearing line on
  the page, and it has no analogue in the JavaScript note (#1304): the JS
  binding runs in-process inside the already-running Node runner, so a
  JavaScript gate's environment is the gate's own environment. The Python
  binding adds an *interpreter resolution* dependency to the runner image, and
  the default is the unversioned, frequently-absent `python` rather than
  `python3`. The failure mode is a red gate that has nothing to do with the
  model: every case in a suite using `type: python` fails identically on an
  image that only ships `python3`, and the error text is a shell message rather
  than a promptfoo message, which makes it easy to misread as a harness crash
  during incident triage. This is a concrete instance of Ch05's "test in the
  environment you ship" rule (`guide/05-llm-ops-reliability.md:47`) with a
  config-level fix: set `PROMPTFOO_PYTHON` explicitly (or the per-provider
  `pythonExecutable`) in the CI environment rather than relying on the shell
  default, so the interpreter is part of the pinned gate definition. The
  sub-page's troubleshooting pointer names the same failure class — "for common
  issues like `Python not found`, module import errors, and timeout problems" —
  and adds two more: `PYTHONPATH` must include any directory holding imported
  assertion modules, and Python execution detail is only visible at
  `LOG_LEVEL=debug`.

### Claim 2: Because `pass` is a Python reserved keyword, the page's `GradingResult` is a **dataclass** with a `pass_` field, and the page instructs the author to convert it with `dataclasses.asdict()` before returning — a return-shape step the JavaScript contract does not have
- **Evidence**: The "GradingResult types" section: the `@dataclass` definition
  carrying the inline comment on `pass_`, plus the conversion instruction
  sentence immediately after it. The `asdict` import is in the same block.
- **Confidence**: settled (documented product behavior, stated explicitly)
- **Quote**: "# 'pass' is a reserved keyword in Python" (inline comment on the
  `pass_` field of the `GradingResult` dataclass) and "Convert dataclass
  instances to dictionaries with `asdict(result)` before returning them from an
  assertion."
- **Our assessment**: A return-shape footgun that exists purely because of the
  host language, and it is invisible from the JavaScript note. A
  `python`-language gate returns a `GradingResult` **instance** rather than a
  dict unless the author remembers the `asdict()` step; the page does not say
  what the harness does with a raw dataclass instance returned by mistake, so
  the shape is under-specified at exactly the point a reviewer would want the
  contract. The name-mapping table that follows (Claim 3) is the second half of
  the same problem: even a correctly-converted dict has to spell its fields
  correctly, and the page documents *both* spellings as acceptable. Combined,
  the Python gate has three independent places to get the return shape wrong
  (dataclass vs dict, `pass_` vs `pass`, snake vs camel) where the JavaScript
  binding has none — which makes the Python assertion the one that warrants a
  round-trip test (assert against a known-bad output and confirm the harness
  reads a red, not a green) before it is trusted in a release gate.

### Claim 3: The page defines a silent snake_case → camelCase field bridge for the Python return value — `pass_` → `pass`, `named_scores` → `namedScores`, `named_score_weights` → `namedScoreWeights`, `component_results` → `componentResults`, `tokens_used` → `tokensUsed` — the only place the Python return-contract spelling is specified
- **Evidence**: The "Snake case support" list, quoted in full in Concrete
  Artifacts, including the parenthetical escape hatch for the reserved keyword.
  Note that `tokens_used` appears **only** in this list — it is not a field on
  the `GradingResult` dataclass defined twenty lines above it on the same page.
- **Confidence**: settled (documented product behavior, enumerated)
- **Quote**: "Python snake_case fields are automatically mapped to camelCase:"
  and "`pass_` → `pass` (or just use `"pass"` as a dictionary key)"
- **Our assessment**: Two useful things and one hazard. Useful: writing
  `named_scores` in a Python gate is not a mistake, so the snake_case-native
  style a Python reviewer expects is also the supported style. Hazard: the
  mapping is *automatic and silent*, so a misspelled or unmapped key produces
  no error — it produces a verdict computed from a field the harness dropped,
  which is the fail-open shape Ch05's "a gate that cannot fail is not a gate"
  is about, one layer down in the return value. The `tokens_used` →
  `tokensUsed` entry is the concrete tell: it is documented as mappable but is
  not in the type definition, so the page's own list is broader than its own
  contract. And the vendor's nested-metrics example mixes conventions inside a
  single dict literal — `'named_scores'` (needs mapping) next to
  `'componentResults'` (already camel) — so a reader copying that artifact has
  to know, per field, which side of the bridge they are on. Our assessment:
  treat the mapping table as the authoritative list of *recognised* fields and
  assert on the rendered eval output (does the named metric appear in the UI?)
  rather than trusting that a returned key was consumed.

### Claim 4: The page's canonical trace gate guards with `hasattr(context, 'trace')` while declaring `context` to be a `TypedDict` — so, read against the page's own type definition, the guard returns `True` **unconditionally** and the entire trace-checking body below it is unreachable
- **Evidence**: The "Using trace data" reference function's first three lines
  (`if not hasattr(context, 'trace') or context.trace is None:` →
  `return True`), set against the `class AssertionValueFunctionContext(TypedDict)`
  definition in "Using test context" and against the page's own dict-method
  call `context.get('config', {})` in the external-file example. Compare the
  JavaScript sibling's guard, `if (!context.trace) { … return true; }`, where
  `context` is declared an `interface` and attribute access is coherent
  (#1304 Claim 6).
- **Confidence**: settled that the guard is fail-open under either reading
  (`hasattr` is `False` for every attribute of a plain dict, and `context.trace`
  is `None`/absent when tracing is off); emerging for the stronger claim that
  the body is *unreachable* — that follows from the page's `TypedDict`
  declaration plus its own `.get()` call, but we have not executed the
  assertion, and if the runner actually injects an attribute-bearing object
  rather than the declared dict then the body is reachable and the only defect
  is the doc/type mismatch. Recorded as an open contract question, not a
  measured fact.
- **Quote**: "When tracing is enabled, OpenTelemetry trace data is available in
  the `context.trace` object. This allows you to write assertions based on the
  execution flow:" (the section introducing the function) and, inside the
  function body: `if not hasattr(context, 'trace') or context.trace is None:`
  followed by `return True`
- **Our assessment**: The fail-open trace guard is the item the JavaScript note
  surfaced and filed as contradiction #1307, and this page shows the same
  footgun is **language-independent** — it is a documentation pattern, not a JS
  quirk — but the Python form is strictly worse. In JS, `if (!context.trace)`
  is a correct read of a correctly-typed object: the guard is *chosen*, and the
  only defect is the policy (skip rather than fail). In Python as written, the
  guard is not even a valid read of the type the same page declares: if
  `context` really is a `TypedDict` (a plain dict, as the page's own
  `context.get('config', {})` call implies), then `hasattr(context, 'trace')` is
  `False` for every possible state of the trace field, the `or` short-circuits,
  and the gate returns `True` even when trace data is present and the error-span
  / latency / API-count checks below it would have failed. The escalation is
  silent in the worst way: the suite is green, the assertion reports a pass, and
  the body that was supposed to be the gate never runs. Neither reading escapes
  the policy problem — with an attribute-bearing object the guard is correct
  code and still a fail-open policy — so the *policy* conclusion is settled
  either way, and only the *reachability* claim is conditional. This is an
  extension of contradiction #1307, not a new contradiction: the Python page is
  silent on what the built-in `trace-*` assertions do when tracing is off, so
  it only speaks to the custom-gate side. Evidence posted to #1307 as a
  cross-reference comment; no verdict picked here, per MINER.md §4a.

### Claim 5: The page documents three mutually inconsistent access styles for the same `AssertionValueFunctionContext` object — dict-subscript (`context["vars"]["example"]`), dict-method (`context.get('config', {})`), and attribute (`context.trace`, `if context.trace`) — in three different examples
- **Evidence**: The "Using test context" example's
  `value: 'context["vars"]["example"] in output'`; the external-file config
  example's `context.get('config', {}).get('outputLengthLimit', 0)`; and the two
  trace examples' attribute-style `context.trace` and `context.trace['spans']`,
  plus the YAML example's bare `if context.trace:` truthiness test. All three
  appear on one page, against the single `TypedDict` declaration.
- **Confidence**: settled (all five access expressions are verbatim on the
  page; the declared type and the subscript/method examples agree with each
  other and disagree with the attribute examples)
- **Quote**: "For example, if the test case has a var `example`, access it in
  Python like this:" (introducing the subscript form) and
  `return len(output) <= context.get('config', {}).get('outputLengthLimit', 0)`
- **Our assessment**: Two of the three styles are coherent with the declared
  type — subscript and `.get()` both work on a plain dict — and the attribute
  style does not. So a Python gate author has a working recipe for `vars` and
  `config` and a broken-looking recipe for `trace`, on the same page, with no
  statement about which is authoritative. The YAML example is the sharpest
  case: `if context.trace:` is a truthiness test that, on a dict, can never be
  `True` even for a populated trace, so that example fails open *silently and
  correctly* (no `AttributeError`, because Python evaluates `context.trace` and
  raises before the truthiness test can even run — but only if attribute access
  raises, which is the point in dispute). Either way the operator cannot tell
  from the docs which spelling to copy. This is precisely Ch05's "read the
  assert's own defaults before trusting its verdict" applied to a *type*
  contract: the fix is a one-line runtime check (`isinstance(context, dict)`)
  plus pinning the spelling in a reviewed helper module, so that the gate's
  view of the context is defined by tested code rather than by which example a
  developer copied.

### Claim 6: Unlike the JavaScript page, this page never states what happens when a Python assertion raises — an undocumented contract where the most likely exception (`AttributeError` from the attribute-style `context.trace` access in Claims 4–5) has undefined behavior
- **Evidence**: Absence of any exception/throw/error sentence anywhere in the
  page's "External .py", "GradingResult types", or "Using trace data" sections,
  against the JavaScript sibling's explicit fail-closed statement (#1304
  Claim 2, verified in that note). The page *does* document the return contract
  precisely ("It expects that either a `bool` (pass/fail), `float` (score), or
  `GradingResult` will be returned") while leaving the error contract entirely
  unstated.
- **Confidence**: emerging — the documentation gap is a verified fact about the
  page; the runtime behavior is **not** established by this source and is
  deliberately left open. Do not assume the JavaScript fail-closed semantics
  carry over; that assumption is itself unverified.
- **Quote**: "It expects that either a `bool` (pass/fail), `float` (score), or
  `GradingResult` will be returned."
- **Our assessment**: The gap is load-bearing precisely because of Claims 4–5.
  The JavaScript page's fail-closed rule is a useful default to reason from, and
  a reader who assumes it carries over will build a Python gate that *looks*
  fail-closed and has never been shown to be. There are three plausible runtime
  behaviors and this source cannot distinguish them: the harness catches the
  exception and fails the assertion (JavaScript semantics), it propagates and
  aborts the whole eval run, or it swallows the exception and scores the
  assertion as a pass. The third is the dangerous one and is exactly the shape
  of the guarded example above it, so a Python gate's error behavior is the
  one thing a release-gate owner cannot determine by reading this page. Our
  assessment: treat the error contract as an open question and *measure* it
  before adopting a Python gate — deliberately raise inside a `python`
  assertion on a scratch config and record whether the assertion goes red or
  the run dies. That experiment is cheap, and it is the only way to close the
  question; the guide should state the rule as "verify the error contract by
  execution" rather than asserting a behavior the vendor has not documented.

### Claim 7: The page's opening return-value prose still specifies the **JavaScript** boolean literals `true` / `false` for a Python function, and the multiline example returns a dict literal with bareword keys — contract slips copy-pasted from the sibling page
- **Evidence**: The opening paragraph's return instruction, verbatim, next to
  the immediately following Python expression example
  `output[5:10] == 'Hello'`; and the "Multiline functions" block returning
  `{'pass': True, ...}` / `{'pass': False, ...}` — correct Python for the
  values, with the JS-derived spelling of the surrounding prose.
- **Confidence**: settled (both statements are verbatim; the inconsistency
  between them is on the page)
- **Quote**: "A variable named `output` is injected into the context. The
  function should return `true` if the output passes the assertion, and
  `false` otherwise. If the function returns a number, it will be treated as a
  score."
- **Our assessment**: In Python, `true` and `false` are not literals — a
  function body written to the prose above raises `NameError` on the first
  line, and because the *inline* `value:` expression is evaluated as Python, an
  inline assertion written the way the page describes it fails the same way.
  The page's own example immediately after the prose uses a Python expression
  that returns a real bool, so the examples and the prose disagree about which
  language the reader is writing in. The practical read for a gate owner: the
  prose is unreliable, the examples are closer to correct, and the
  *error behavior* of a `NameError` here is the undocumented one from Claim 6 —
  so a language slip in a Python gate is a compounding risk (slip → exception →
  unknown verdict) rather than a loud syntax error the config validator would
  catch. Note the pattern, not the individual literal: this is the third
  contract slip on this page after the access-style inconsistency (Claim 5) and
  the `hasattr`-on-a-`TypedDict` guard (Claim 4), all in service of the same
  point — a custom assertion's verdict is only as trustworthy as the contract
  its author read, and this contract has to be checked against the runtime.

### Claim 8: External Python assertions load via `file://relative/path/script.py` with an optional `:function_name` selector and a **default entrypoint of `get_assert`**, are called as `(output, context)`, and read assertion-scoped `config` through `context.get('config', {})` — the same parameter-reuse pattern as the JavaScript route, with a different default-function convention
- **Evidence**: The "External .py" section in full: the `file://` YAML form with
  its `config:` block, the `:custom_assert` selector form, the default-name
  sentence, the call-signature sentence, and the two worked scripts (the
  `get_assert` / `custom_assert` pair and the `outputLengthLimit` config
  reader).
- **Confidence**: settled (documented product behavior, with a worked example
  per rule)
- **Quote**: "You can specify a particular function to use by appending it after
  a colon:" and "If no function is specified, it defaults to `get_assert`." and
  "This file will be called with an `output` string and an
  `AssertionValueFunctionContext` object (see above)."
- **Our assessment**: The `get_assert` default is a real migration hazard in the
  opposite direction from the obvious one: a team that already has
  `file://assertions/check.py` wired into a `javascript` assertion will find
  that renaming the assertion type to `python` requires also naming a
  `get_assert` function (JavaScript defaults to `module.exports`), and a file
  that exports no `get_assert` fails at load rather than at call — a different
  and louder failure mode than the return-shape mistakes in Claim 2. The
  `context.get('config', {})` read is the same assertion-scoped-parameter
  pattern the JavaScript note records (#1304 Claim 7, prefer `config` over test
  `vars` because vars leak into report columns), so that hygiene rule transfers
  directly to Python gates. Two operational notes the page adds: the referenced
  file is committed repo code executed by the eval runner, so it inherits the
  same review surface as the pipeline itself (Ch06's supply-chain boundary), and
  its imports must be resolvable on the runner image — which ties directly back
  to Claim 1's interpreter and `PYTHONPATH` dependency.

### Claim 9: `not-python` restates the pre-inversion threshold rule for the Python binding, independently corroborating that the negation semantics are a property of the assertion framework and not of the JavaScript page
- **Evidence**: The "Negation" section's one sentence and its lone example
  (`value: "'error' in output"`), verbatim.
- **Confidence**: settled (documented product behavior, and the second
  independent vendor page to state it)
- **Quote**: "Use `not-python` to invert the final pass/fail result while
  preserving the returned score. Numeric scores are still compared against
  `threshold` before the result is inverted:"
- **Our assessment**: The rule itself is already extracted at #1304 Claim 3
  (from the JavaScript page). The value of this claim is the *second
  independent statement* of it, in a different language binding, from a
  separately-authored page — which upgrades the negation-semantics finding from
  a single-page observation to a framework-level property. That matters for
  synthesis: a guide rule derived from "promptfoo's JavaScript negation does
  this" would be scoped to a code path; a rule derived from "both documented
  bindings do this" can be stated as applying to negated custom assertions
  generally. One caveat specific to this example: the documented
  `not-python` value is a *string expression* evaluating to a bool, not a
  numeric score, so the threshold interaction that the sentence warns about
  does not actually bite in the page's own example — the page states the rule
  without an example that exercises it. A reader who copies this example will
  not have tested the subtlety the sentence describes.

### Claim 10: The whole eval pipeline is Python-addressable through the same `file://` prefix — prompts, providers, test generators, and assertions — so a Python-based gate is not a single assertion but a multi-hook dependency on the runner's interpreter
- **Evidence**: The sub-page (`/docs/integrations/python/`): its opening
  statement of the execution model, the "Use Python for" list covering all
  four surfaces, the single combined `promptfoo.config.yaml` example wiring
  `file://prompts.py:create_prompt` / `file://provider.py` /
  `file://tests.py:generate_tests` / `file://assert.py:check` in one config, and
  the Configuration section's `PYTHONPATH` and `LOG_LEVEL=debug` knobs.
- **Confidence**: settled (documented product behavior, from the vendor's own
  integration page; not independently validated)
- **Quote**: "Promptfoo is written in TypeScript and runs via Node.js, but it
  has first-class Python support. You can use Python for any part of your eval
  pipeline without writing JavaScript." and "The `file://` prefix tells
  promptfoo to execute a Python function. Promptfoo automatically detects your
  Python installation."
- **Our assessment**: The framing that makes Claim 1 matter: `file://` is not
  an assertion-only convenience but a uniform hook into every stage of the
  pipeline, so a team that adopts one Python assertion has adopted an
  interpreter dependency for the gate, and a team that adopts Python prompts or
  providers has adopted it for the *measurement* side too — where a broken
  import or a missing interpreter corrupts the very outputs the assertions
  score. The Node-tool-invoking-Python architecture is the root of the
  operational asymmetry versus JavaScript: the runner is guaranteed to have
  Node (it is the Node tool) and not guaranteed to have `python`. Two
  configuration knobs matter for debugging a Python gate and neither is on the
  assertions page: `PYTHONPATH` for assertion modules that import from the repo,
  and `LOG_LEVEL=debug` as the only documented way to see Python execution
  detail — i.e. the default-visible failure surface for a Python gate is the
  shell-level error from Claim 1.

### Claim 11: The two pages disagree on how promptfoo finds Python — the assertions page says it runs `python` from your shell and warns about `command not found`, while the integration page says promptfoo "automatically detects your Python installation" — and the integration page adds a `0-1` range constraint on numeric returns that the assertions page omits
- **Evidence**: The assertions page's "Overriding the Python binary" section
  versus the sub-page's opening Configuration paragraph and its inline
  assertion comment. Also the sub-page's per-provider
  `pythonExecutable: ./venv/bin/python` override, which appears nowhere on the
  assertions page.
- **Confidence**: settled that both statements are verbatim; the conditional
  reading (auto-detection *of the installation* vs. resolution *of the
  command name* `python`) is a plausible reconciliation but is **not** stated by
  either page
- **Quote**: "Promptfoo automatically detects your Python installation."
  (sub-page, contrasting with the assertions page's "By default, promptfoo will
  run `python` in your shell. Make sure `python` points to the appropriate
  executable.") and, from the sub-page's inline-assertion example, the comment
  "# Inline expression (returns bool or float 0-1)"
- **Our assessment**: The reconciliation is obvious once seen — detecting *an
  installed interpreter* is not the same as resolving the command name `python`,
  and the assertions page's warning is about the latter — but an operator
  reading only the integration page will believe their `python3.13`-only image
  is handled, and the first thing they will learn otherwise is a failing gate.
  The `0-1` range note is the same class of gap as Claim 3: the assertions page
  says only "If the function returns a number, it will be treated as a score",
  while the integration page constrains the inline form to "float 0-1". Since a
  score outside `[0, 1]` is precisely the input that makes weighted aggregation
  (#1287 Claim 1) and display meaningless, a Python gate returning
  `math.log10(len(output)) * 10` — which is the assertions page's *own* second
  example — deserves a second look, and nothing on the page says the harness
  clamps, errors, or normalizes it. Recorded, not filed as a contradiction:
  the two pages are not making opposing claims about the same predicate, and
  the operational answer (pin the interpreter, keep scores in range) is the same
  under either reading.

## Concrete Artifacts

### `GradingResult` dataclass and the snake_case → camelCase bridge (verbatim from "GradingResult types")

```python
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

@dataclass
class GradingResult:
    pass_: bool  # 'pass' is a reserved keyword in Python
    score: float
    reason: str
    component_results: Optional[List['GradingResult']] = None
    named_scores: Optional[Dict[str, float]] = None  # Appear as metrics in the UI
    named_score_weights: Optional[Dict[str, float]] = None  # Total weight per named score
```

```
Python snake_case fields are automatically mapped to camelCase:

- `pass_` → `pass` (or just use `"pass"` as a dictionary key)
- `named_scores` → `namedScores`
- `named_score_weights` → `namedScoreWeights`
- `component_results` → `componentResults`
- `tokens_used` → `tokensUsed`
```

(`tokens_used` appears in this list but is not a field on the `GradingResult`
dataclass above — see Claim 3.)

### `AssertionValueFunctionContext` type definition (verbatim from "Using test context")

```python
from typing import Any, Dict, List, Optional, TypedDict, Union

class TraceSpan(TypedDict):
    spanId: str
    parentSpanId: Optional[str]
    name: str
    startTime: int  # Unix timestamp in milliseconds
    endTime: Optional[int]  # Unix timestamp in milliseconds
    attributes: Optional[Dict[str, Any]]
    statusCode: Optional[int]
    statusMessage: Optional[str]

class TraceData(TypedDict):
    traceId: str
    spans: List[TraceSpan]

class AssertionValueFunctionContext(TypedDict):
    # Raw prompt sent to LLM
    prompt: Optional[str]
    # Test case variables
    vars: Dict[str, Union[str, object]]
    # The complete test case
    test: Dict[str, Any]  # Contains keys like "vars", "assert", "options"
    # Log probabilities from the LLM response, if available
    logProbs: Optional[list[float]]
    # Configuration passed to the assertion
    config: Optional[Dict[str, Any]]
    # The provider that generated the response
    provider: Optional[Any]  # ApiProvider type
    # The complete provider response
    providerResponse: Optional[Any]  # ProviderResponse type
    # OpenTelemetry trace data (when tracing is enabled)
    trace: Optional[TraceData]
    # Optional shortcut to providerResponse.metadata
    metadata: Optional[Dict[str, Any]]
```

Note that `context` is declared a `TypedDict` — a plain dict at runtime —
while the "Using trace data" examples access it as `context.trace` (Claims 4
and 5).

### Trace-based assertion function (verbatim from "Using trace data")

```python
def get_assert(output: str, context) -> Union[bool, float, Dict[str, Any]]:
    # Check if trace data is available
    if not hasattr(context, 'trace') or context.trace is None:
        # Tracing not enabled, skip trace-based checks
        return True

    # Access trace spans
    spans = context.trace['spans']

    # Example: Check for errors in any span
    error_spans = [s for s in spans if s.get('statusCode', 0) >= 400]
    if error_spans:
        return {
            'pass': False,
            'score': 0,
            'reason': f"Found {len(error_spans)} error spans"
        }

    # Example: Calculate total trace duration
    if spans:
        duration = max(s.get('endTime', 0) for s in spans) - min(s['startTime'] for s in spans)
        if duration > 5000:  # 5 seconds
            return {
                'pass': False,
                'score': 0,
                'reason': f"Trace took too long: {duration}ms"
            }

    # Example: Check for specific operations
    api_calls = [s for s in spans if 'http' in s['name'].lower()]
    if len(api_calls) > 10:
        return {
            'pass': False,
            'score': 0,
            'reason': f"Too many API calls: {len(api_calls)}"
        }

    return True
```

This is the same gate the JavaScript sibling documents (#1304 Claim 6 /
Concrete Artifacts), with the guard rewritten as `hasattr(...) or
context.trace is None`. The trace *patterns* (error spans ≥400, duration
> 5000ms, >10 http calls) are not re-claimed as new here.

### Causal-ordering gate (verbatim from "Using trace data" example YAML)

```yaml
tests:
  - vars:
      query: "What's the weather?"
    assert:
      - type: python
        value: |
          # Ensure retrieval happened before response generation
          if context.trace:
              spans = context.trace['spans']
              retrieval_span = next((s for s in spans if 'retrieval' in s['name']), None)
              generation_span = next((s for s in spans if 'generation' in s['name']), None)
                          
          if retrieval_span and generation_span:
              return retrieval_span['startTime'] < generation_span['startTime']
          return True
```

### External `.py` loading, entrypoint convention, and assertion-scoped `config` (verbatim from "External .py")

```yaml
assert:
  - type: python
    value: file://relative/path/to/script.py
    config:
      outputLengthLimit: 10
```

```yaml
assert:
  - type: python
    value: file://relative/path/to/script.py:custom_assert
```

```python
from typing import Any, Dict, TypedDict, Union

# Default function name
def get_assert(output: str, context) -> Union[bool, float, Dict[str, Any]]:
    print('Prompt:', context['prompt'])
    print('Vars', context['vars']['topic'])
    # This return is an example GradingResult dict
    return {
      'pass': True,
      'score': 0.6,
      'reason': 'Looks good to me',
    }

# Custom function name
def custom_assert(output: str, context) -> Union[bool, float, Dict[str, Any]]:
    return len(output) > 10
```

```python
from typing import Any, Dict, Union

def get_assert(output: str, context) -> Union[bool, float, Dict[str, Any]]:
    return len(output) <= context.get('config', {}).get('outputLengthLimit', 0)
```

### Nested metrics and component results (verbatim from "External .py") — note the mixed spellings

```python
{
    'pass': True,
    'score': 0.75,
    'reason': 'Looks good to me',
    'named_scores': {'quality': 0.75},
    'named_score_weights': {'quality': 3},
    'componentResults': [{
        'pass': 'bananas' in output.lower(),
        'score': 0.5,
        'reason': 'Contains banana',
    }, {
        'pass': 'yellow' in output.lower(),
        'score': 0.5,
        'reason': 'Contains yellow',
    }]
}
```

`named_scores` and `named_score_weights` are snake_case and rely on the
automatic mapping; `componentResults` is already camelCase. The page's
weight arithmetic for this artifact: "The `quality` metric contributes
`0.75 × 3 = 2.25` to its weighted total, with weight `3`, so it displays as
75%."

### Inline expression forms (verbatim from the page opening)

```yaml
assert:
  - type: python
    value: output[5:10] == 'Hello'
```

```yaml
assert:
  - type: python
    value: math.log10(len(output)) * 10
```

### Multiline function (verbatim from "Multiline functions") — note the JS-derived prose in the surrounding text

```yaml
assert:
  - type: python
    value: |
      # Insert your scoring logic here...
      if output == 'Expected output':
          return {
            'pass': True,
            'score': 0.5,
          }
      return {
        'pass': False,
        'score': 0,
      }
```

### `not-python` example (verbatim from "Negation")

```yaml
assert:
  - type: not-python
    value: "'error' in output"
```

### Pipeline-wide Python hooks (verbatim from the sub-page `/docs/integrations/python/`)

```yaml
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
prompts:
  - file://prompts.py:create_prompt # Python generates the prompt
providers:
  - file://provider.py # Python calls the model
tests:
  - file://tests.py:generate_tests # Python generates test cases
defaultTest:
  assert:
    - type: python # Python validates the output
      value: file://assert.py:check
```

```bash
export PROMPTFOO_PYTHON=/path/to/python3
```

```yaml
providers:
  - id: file://provider.py
    config:
      pythonExecutable: ./venv/bin/python
```

```bash
export PYTHONPATH=/path/to/modules:$PYTHONPATH
```

```bash
LOG_LEVEL=debug npx promptfoo eval
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/expected-outputs/python/ — sections as noted — plus the sub-page https://www.promptfoo.dev/docs/integrations/python/ for the last block. All copied character-for-character from the rendered pages (code blocks re-flowed only at the newline level to restore line breaks lost in HTML extraction, consistent with the conventions of the sibling notes #1304 and #1289). Inline comment lines inside code blocks are part of the verbatim extracted code.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 3**
    (`not-javascript` "inverts the final pass/fail result while preserving the
    returned score", and numeric scores compared against `threshold` *before*
    inversion) — the Python page states the same rule word-for-word for
    `not-python` in a separately-authored page, so the semantics are a
    framework property rather than a JavaScript-page artifact (Claim 9 here).
    (Verified: #1304 Claim 3, re-read in the note file.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 5** (the
    `AssertionValueFunctionContext` field list, with `trace` "undefined unless
    tracing is enabled") — the Python page's `TypedDict` declares the identical
    nine fields with the same tracing-conditional comment, so the context
    surface is shared across bindings. (Verified: #1304 Claim 5.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 7**
    (prefer assertion-level `config` over test `vars`, which "are shared across
    all assertions and appear as report columns") — the Python `config` example
    reads `context.get('config', {}).get('outputLengthLimit', 0)`, the same
    parameter-scoping pattern with a Python signature (Claim 8 here).
    (Verified: #1304 Claim 7.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 6**
    (custom scoring functions are "JS/Python `file://` functions returning
    `{pass, score, reason}`", with named scores "already normalized as a
    weighted average") — this page is the Python half of that statement, and
    the nested-metrics artifact's own arithmetic ("`0.75 × 3 = 2.25` … so it
    displays as 75%") is the same normalization made concrete.
    (Verified: #1287 Claim 6.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (every
    assertion type is negatable via a `not-` prefix) — the `not-python` row is
    the Python instance of that surface. (Verified: #1287 Claim 10.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 14**
    (budget/precondition gates carry hidden requirements — `latency` needs
    `--no-cache`, `perplexity` needs provider `logprobs`) — the Python page
    adds a third class of hidden precondition: the interpreter must exist and
    be resolvable as `python` (Claim 1). (Verified: #1289 Claim 14.)

- **Contradicts**:
  - **Contradiction issue #1307** (open; "promptfoo missing-trace semantics:
    built-in trace-* assertions throw ('could not be evaluated') vs custom-JS
    trace gate passes green when tracing is off"). This page does not create a
    new contradiction — it **extends** the existing one, and extends it in the
    same direction: the fail-open guard is language-independent, and the Python
    form is strictly worse than the JS form because the guard is written with
    `hasattr` against a `TypedDict`, so under the page's own type declaration
    `hasattr(context, 'trace')` is `False` in every state and the guard returns
    `True` unconditionally (Claim 4, Concrete Artifacts). Evidence and the
    verbatim guard were posted as a comment on #1307 for the resolver. No
    verdict picked here, per MINER.md §4a.
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 12** (the
    built-in trace/trajectory family "throw[s] an error rather than failing,
    indicating that the assertion could not be evaluated" when trace data is
    unavailable) vs this page's custom-Python gate, which returns `True` on the
    same condition. Same tool, same missing-trace precondition, opposite
    verdicts — and, uniquely on this page, the gate body is not merely skipped
    but (under the declared types) unreachable. This is the Python side of
    #1307; the claim-level opposition is recorded here so the Smith sees the
    full evidence set.
  - **Same-page documentation inconsistencies (recorded, not filed)**, per the
    Prospector's explicit guidance and MINER.md §4a's context-dependence
    carve-out: (a) three context access styles against one `TypedDict`
    declaration (Claim 5); (b) JS `true`/`false` literals in a Python return
    contract (Claim 7); (c) "automatically detects your Python installation"
    (sub-page) vs "will run `python` in your shell" (this page) (Claim 11).
    These are contract slips *within* the vendor's own docs rather than two
    sources opposing each other on a topic, and each has the same operational
    answer (pin the interpreter, pin the context accessor in reviewed code,
    execute the example before deploying it), so filing three issues for
    documentation typos would bury the substantive one (#1307).

- **Extends**:
  - `source-notes/docs-promptfoo-javascript-assertions.md` — this page is the
    Python binding of that note's contract, and supplies the four things the JS
    page structurally cannot: interpreter resolution as a gate-environment
    dependency (Claim 1), the reserved-keyword/dataclass return-shape step and
    the snake_case → camelCase bridge (Claims 2–3), a trace guard that is
    fail-open *and* type-invalid (Claim 4), and the absence of any documented
    exception contract (Claim 6). Read the two notes as one contract with
    language-specific failure modes.
  - `source-notes/docs-promptfoo-assertions-metrics.md` — supplies the
    threshold/weighted-average machinery this page's return values feed into
    (#1287 Claim 1's "combined weighted score ≥ threshold" is what the
    `threshold` in the `not-python` sentence refers to, and what makes an
    out-of-range or unmapped-field return value consequential).
  - `source-notes/docs-promptfoo-deterministic-metrics.md` — the "deterministic
    means judge-free, not hermetic" framing (#1289 Claim 2) gains a third
    non-hermetic dependency: the runner image's Python installation, its version
    path, and its `PYTHONPATH` are all part of whether the gate can even
    execute (Claims 1, 10).
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` —
    not re-cited here: this page's trace *patterns* are identical to #1304
    Claim 6's and the span-naming contract is unchanged, so the OTel producer
    cross-reference stands as recorded in that note. Noted rather than
    duplicated.

- **Novel**: Nothing in the existing corpus covers the Python binding; verified
  by grep — the strings `not-python`, `PROMPTFOO_PYTHON`, and
  `expected-outputs/python` appear nowhere in `source-notes/` or `guide/`
  before this note. New to the corpus:
  1. **Interpreter resolution as a gate-environment footgun** (Claim 1) — the
     `python` default, the verbatim `python: command not found`, the
     `PROMPTFOO_PYTHON` / `pythonExecutable` / `PYTHONPATH` knobs. No JS
     analogue exists because the JS binding runs in-process.
  2. **The `pass_` reserved-keyword dataclass + `asdict()` requirement**
     (Claim 2) — a return-shape step unique to the language binding.
  3. **The snake_case → camelCase return-field bridge** (Claim 3) — the only
     statement of the Python return-contract spelling anywhere in the corpus,
     including a mapped field (`tokens_used`) absent from the page's own type
     definition.
  4. **The type-invalid fail-open trace guard** (Claim 4) — `hasattr` against a
     `TypedDict`, i.e. a guard that returns `True` in every state; the
     language-independent escalation of #1304 Claim 6 and new evidence on
     contradiction #1307.
  5. **Three inconsistent context access styles** (Claim 5) — the doc-level
     contract slip the guard bug is an instance of.
  6. **The undocumented Python exception contract** (Claim 6) — an *open*
     question where the JS sibling is explicit, and where the plausible
     fail-open behavior compounds Claim 4.
  7. **Pipeline-wide `file://` Python hooks** (Claim 10) — prompts, providers,
     test generators, and assertions behind one prefix, with
     `LOG_LEVEL=debug` as the only documented Python-execution visibility.
  8. **The auto-detect-vs-`python`-in-shell cross-page inconsistency and the
     undocumented `0-1` numeric range** (Claim 11).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: the table currently ends with a
  custom-JS trace-gate row citing
  `source-notes/docs-promptfoo-javascript-assertions` Claim 6. Add the Python
  row and, more importantly, reframe the entry: the fail-open trace guard is
  **not a JavaScript-specific default**, it is how the vendor documents trace
  gating in every language binding, so the guide's rule should be stated
  binding-agnostically — "a custom assertion that guards on missing trace data
  passes green" (Claim 9/4). Cross-ref open contradiction #1307; no verdict.
- **Chapter 05 — "Read the assert's own defaults before trusting its verdict"
  (`guide/05-llm-ops-reliability.md:443`)**: this page supplies two more
  "look at the assert's own contract" cases that are *not* threshold defaults
  and so do not fit the existing section's framing. Recommend a short
  subsection, "A custom assertion's contract is four things you must read",
  covering: the return shape (`bool | float | GradingResult`, Claims 2–3), the
  field-spelling bridge (Claim 3), the context access style (Claim 5), and the
  error contract (Claim 6). Each of the four is documented inconsistently or
  not at all on the vendor page, which is the section's actual thesis: the
  verdict is a property of the assertion's contract, not of the output.
- **Chapter 05 — "Test in the environment you ship"
  (`guide/05-llm-ops-reliability.md:47`)**: add the concrete version. A
  `type: python` gate adds an interpreter-resolution dependency to the runner
  image, and the documented default resolves the unversioned command `python`
  (Claim 1), so an image shipping only `python3` turns the entire Python
  assertion set red with a shell error string. The rule: pin
  `PROMPTFOO_PYTHON` (or the per-provider `pythonExecutable`) in the CI
  environment as part of the gate's definition, and set `PYTHONPATH` for
  repo-local assertion modules. This is the general form of Ch05's existing
  "a gate that fails for infrastructure reasons is indistinguishable from a
  model regression in the alert" problem — name the environment as a gate
  input.
- **Chapter 06 (Security and Trust) — "Gating on LLM security scans"
  (`guide/06-security-and-trust.md:768`) and "Pin everything; verify releases"
  (`guide/06-security-and-trust.md:636`)**: the Python binding widens the
  supply-chain surface of a `file://` assertion from "committed JS in the repo"
  to "committed Python in the repo, executed by a subprocess whose
  interpreter, version path, and import path are environment inputs"
  (Claims 1, 8, 10). A vendored or third-party `file://` assertion now brings
  its own dependency requirements with it. Concretely: review `file://*.py`
  hooks with the same weight as pipeline code, and treat the runner image's
  Python installation as part of the pinned, attested artifact set.
- **Chapter 02 (Observability) — trace-coupled gates**: the guard-shape finding
  (Claims 4, 5) is the Python-path instance of the rule already implied by the
  JS note: a trace-coupled eval suite's health is coupled to the tracing
  pipeline's health, and the coupling must be made to *fail* rather than
  *pass* when tracing is absent. Add that the coupling is asserted through a
  typed context object whose documented type and documented access style do not
  agree, so a trace gate needs its own negative control — run it once with
  tracing disabled and confirm it goes red, which is the only way to catch
  both the fail-open policy and the unreachable-body bug.
- **Chapter 05 — negation**: `not-python` independently confirms the
  pre-inversion threshold semantics (Claim 9), so the existing `not-javascript`
  guidance should be restated for negated *custom* assertions generally rather
  than for one assertion type. Add the caveat from Claim 9's assessment: the
  vendor's own `not-python` example does not exercise the numeric-threshold
  path it warns about, so a copied example has not tested the rule.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/python/),
  plus one linked sub-page read in full per MINER.md §1:
  https://www.promptfoo.dev/docs/integrations/python/ (the "Python Overview"
  link the page opens with). Claims 1, 10, and 11 draw on the sub-page and mark
  it inline. No other sub-pages followed: the parent hub page
  (`configuration/expected-outputs`) is already mined as #1287, the `javascript`
  and `ruby` siblings are separate notes/issues, and the remaining links
  (`/docs/tracing/`, `/docs/configuration/reference/`, provider and
  test-generation pages) are out of scope for this page's contract.
- Quotes verified character-for-character against the fetched rendered content
  before writing. Code blocks re-flowed only at the newline level to restore
  line breaks lost in HTML extraction (same convention as the sibling #1304
  and #1289 notes). Inline comments inside code blocks are part of the
  verbatim extracted code. Where a code region was too long to quote as a
  single `Quote` field, the fragment carrying the claim is quoted and the
  surrounding context left to Concrete Artifacts; no two non-adjacent
  sentences were spliced into one quote.
- Per the Prospector's guidance (three triage comments agree on the
  priorities), the note extracts the **Python deltas** only. The generic
  custom-function escape hatch, the `boolean | number | GradingResult` union,
  and the trace *patterns* (error spans ≥400, duration >5000ms, >10 http calls,
  retrieval-before-generation ordering) are already extracted at
  `docs-promptfoo-javascript-assertions.md` Claims 1, 3, and 6 and are cited
  rather than re-claimed. Where the Python page reuses them, that reuse is
  itself the finding (Claim 9's cross-language corroboration).
- **Claim confidence split**: Claims 1, 2, 3, 5, 7, 8, 9, 10, and 11 are
  verbatim document statements (settled as documented product behavior).
  Claim 4 splits deliberately — the fail-open *policy* is settled under either
  reading of the runtime, while the *unreachable body* claim is marked
  `emerging` because it depends on the page's `TypedDict` declaration being
  accurate, which was not verified by execution. Claim 6 is deliberately an
  open contract question, not a settled behavior: the JavaScript fail-closed
  rule (#1304 Claim 2) was **not** assumed to carry over to Python.
- **Contradiction handling (MINER.md §4a)**: no new contradiction issue filed.
  Checked `CONTRADICTIONS.md` (no open engine entries) and confirmed
  contradiction **#1307** is OPEN with the `contradiction` /
  `needs-resolution` labels on exactly this subject (promptfoo missing-trace
  semantics). The Python guard (Claim 4) is new evidence *for the side #1307
  already records* — the custom-gate-passes-green side — so per the
  Prospector's explicit instruction ("flag item 1 as an extension to
  contradiction #1307 rather than a fresh contradiction") it was posted as a
  comment on #1307 with the verbatim guard, and #1307 is referenced under
  `**Contradicts:**` above. No verdict was picked. The remaining
  doc-internal slips (Claims 5, 7, 11) are vendor typos within a single page
  or between two pages of the same vendor that do not change the guide's
  operational advice, so per §4a's context-dependence carve-out they are
  recorded rather than filed — a judgment call flagged here for the Assayer in
  case it reads §4a's same-source-disagreement trigger more strictly.
- **Cross-ref verification (§4b)**: every `Claim N` citation was verified by
  re-reading the cited note and locating the numbered heading —
  `docs-promptfoo-javascript-assertions.md` Claims 3, 5, 7 (and 1, 2, 6
  referenced in prose) and `docs-promptfoo-assertions-metrics.md` Claims 6, 10
  and `docs-promptfoo-deterministic-metrics.md` Claims 2, 12, 14, all confirmed
  against the files in `source-notes/` before writing. No claim numbers were
  guessed, and no quotation was reconstructed from a cited note. Guide
  line-number references (#5 line refs and #6 section names) checked against
  the current files in `guide/`.
- **Candidate handling** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — each cited or dismissed
  by name):
  - `docs-promptfoo-javascript-assertions.md` — **cited heavily** (Corroborates
    Claims 3/5/7; Extends; the direct language-binding sibling named by all
    three triage comments).
  - `docs-promptfoo-assertions-metrics.md` — **cited** (Corroborates Claims 6,
    10; Extends): the parent hub page that owns the weighted-score/threshold
    model the return contract feeds.
  - `docs-promptfoo-pi-scorer.md` — dismissed: a model-graded grader page; its
    Claim 5 notes `pi`'s default threshold `0.5` is documented on a second
    promptfoo page, but that is unrelated to the custom-assertion contract
    here.
  - `docs-promptfoo-classifier-grading.md` — dismissed: sibling assert-type
    page; shares the assertion-catalog surface but carries no custom-assertion
    contract content.
  - `blog-promptfoo-owasp-red-teaming.md` — dismissed: red-team
    methodology/SDLC phases; no assertion-contract content.
  - `blog-pagerduty-sre-agent-triage.md` — dismissed: LLM-as-judge incident
    triage; no assertion-contract surface.
  - `docs-litellm-batches-api.md` — dismissed: unrelated vendor and topic
    (batch rate-limit windows).
  - `docs-langfuse-mcp-server.md` — dismissed: Langfuse docs MCP server;
    unrelated vendor and concern.
  - `docs-google-sre-team-lifecycles.md` — dismissed: Google SRE Workbook
    team-structure chapter; no LLM-eval content.
  - `blog-promptfoo-red-team-gemini.md` — dismissed: per-model red-team plugin
    config; uses asserts as examples but carries no assertion mechanics.
  - `docs-promptfoo-deterministic-metrics.md` and
    `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` were **not** in
    the candidate list; both were found by searching `source-notes/` per
    MINER.md §4 and are cited (Corroborates/Contradicts/Extends as marked,
    with the Honeycomb note referenced in Extends for continuity only).
- **Freshness check before writing Cross-References**: grepped `source-notes/`
  and `guide/` for `not-python`, `PROMPTFOO_PYTHON`, and
  `expected-outputs/python` — zero hits, confirming no existing note or guide
  section covers this page (the Prospector made the same claim; verified
  independently). Also confirmed the adjacent `ruby` binding page
  (`/docs/configuration/expected-outputs/ruby/`) is likewise unmined, so this
  note is not a duplicate-by-proxy of an existing Ruby note.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1289, #1304): most claims are settled-for-product-behavior
  and directly checkable against an installed CLI, but this is vendor
  documentation with no measured failure rates and no independent practitioner
  validation, and the gate-integrity findings (unreachable trace-gate body,
  undocumented exception contract, contract slips) are the Miner's analysis on
  top of documented behavior rather than vendor statements.
- `date_published` uses the page footer's "Last updated on Sep 29, 2026 by
  mldangelo-oai" (both pages are otherwise undated).
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt after merge. `guide/` was not touched.
