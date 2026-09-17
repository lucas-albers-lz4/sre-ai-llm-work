---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/g-eval/
source_type: docs
title: "Promptfoo Configuration: Model-Graded — G-Eval"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-16
date_extracted: 2026-09-17
last_checked: 2026-09-17
status: current
confidence_overall: emerging
issue: "#1349"
---

# Promptfoo Configuration: Model-Graded — G-Eval

> The per-type vendor reference page for promptfoo's G-Eval assertion — the
> chain-of-thought (CoT) LLM judge that closes the #1305 hub note's explicit
> "g-eval not followed" gap. It documents a **dated default judge pin**
> (`gpt-4.1-2025-04-14` — the surface tension with the hub note's Claim 1 that
> "nothing is pinned by default," now filed as contradiction #1352), a
> **non-fail-open default** (`threshold: 0.7`, the per-type counter-case to the
> context-sibling family's documented `0` defaults), a **two-judge-call
> structure** per assertion (one to generate evaluation steps, one to score —
> a 2x grader-call cost multiplier vs single-call `llm-rubric`), array-value
> criteria that are graded independently and **averaged** before threshold
> comparison (with an **empty array failing closed** as a config error), and
> a **symmetric fail-closed `not-g-eval` inversion** (grader transport/parse
> failures report as failures in *both* directions — never silently passing a
> failed grader call).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "G-Eval" per-type
  model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `g-eval` assert-type behavior — authoritative for *what promptfoo
  does* with a given g-eval config (the default judge, the default threshold,
  the two-call CoT structure, the array-averaging rule, the `not-` inversion
  semantics, the grader-override path), but vendor-positioned: the page carries
  no measured judge-agreement, gate-failure-rate, cost-per-assertion, or
  calibration figures and no independent practitioner validation. Everything
  below is checkable against an installed CLI.
- **Scope**: A six-section reference page (How to use it, How it works,
  Negation with `not-g-eval`, Customizing the evaluator — including the
  LiteLLM grader-reuse subsection, Example, Further reading). It is the
  per-type deep-dive on the `g-eval` member of the rubric-based model-graded
  assertion class that `docs-promptfoo-model-graded-metrics.md` (#1305)
  catalogued at claim level only — that note's Extraction Notes explicitly
  record "g-eval" among the sub-pages "NOT followed." This page therefore
  carries the *delta* (the default judge pin, the default threshold, the
  two-call CoT structure, the array-averaging semantics, the symmetric
  fail-closed inversion), not a re-extraction of the model-graded framing.
  Does NOT cover the sibling `llm-rubric`, `pi`, `model-graded-closedqa`, or
  RAG/context pages (separate sources), or any measured property of the judge.
  Non-English evaluation is delegated to the hub page's multilingual guide
  (a single link line, no per-type content).
- **Last updated**: the page footer reads "Last updated on **Sep 16, 2026** by
  **jameshiester-oai**" — within the recency window; the faceplates describe
  the current `gpt-5` era while pinning the default grader to `gpt-4.1`.
- **Attribution note**: the page's worked examples use `openai:gpt-5-mini` /
  `openai:gpt-5` as the *example overrides*, which are NOT the default judge —
  the default is the `gpt-4.1-2025-04-14` pin stated in "How it works."

## Extracted Claims

### Claim 1: G-Eval is a chain-of-thought LLM judge based on the G-Eval paper (Liu et al., Microsoft) — it grades an output against a plain-text criterion and returns a normalized 0–1 score, with no measurement or calibration evidence on the page
- **Evidence**: The page intro ("framework that uses LLMs with
  chain-of-thoughts (CoT) to evaluate LLM outputs based on custom criteria")
  with the paper citation, and the "How it works" three-step process
  (criteria → CoT analyze → normalized score).
- **Confidence**: settled (documented product behavior — what `g-eval` asserts;
  the CoT mechanism is a design statement, not a measured property)
- **Quote**: "G-Eval is a framework that uses LLMs with chain-of-thoughts (CoT) to evaluate LLM outputs based on custom criteria. It's based on the paper \"G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment\" (Liu et al., Microsoft)." and "1. Takes your evaluation criteria" / "2. Uses chain-of-thought prompting to analyze the output" / "3. Returns a normalized score between 0 and 1"
- **Our assessment**: This positions g-eval inside the rubric-based model-graded
  family (with `llm-rubric`, per #1305 Claim 8 and #1320's assessment) but with
  a distinctive structure the other rubric types do not document: the CoT
  evaluation steps are generated *as part of grading*, which is the mechanism
  behind Claim 6's two-call cost shape. The paper grounding is the vendor's
  provenance claim, nothing more — the page asserts no agreement or calibration
  property of the judge.

### Claim 2: The page pins g-eval's default evaluator to a specific dated model ID — `gpt-4.1-2025-04-14` — the page's concrete default that sits in direct tension with the hub note's (#1305) finding that model-graded judges are ambient/unpinned by default
- **Evidence**: The "How it works" opening sentence, verbatim.
- **Confidence**: settled (documented product behavior — the exact model ID is
  stated on the page; the reconciliation with #1305 Claim 1 is *not* stated on
  either page)
- **Quote**: "G-Eval uses `gpt-4.1-2025-04-14` by default to evaluate outputs based on your specified criteria."
- **Our assessment**: This is the Prospector's single highest-value item and the
  reason I filed **contradiction #1352**. #1305 Claim 1 states every model-graded
  assertion's judge is *unpinned / selected from ambient credentials* (OpenAI,
  Anthropic, Gemini, *etc.* can each "activate a different default"); this page
  names a *dated model ID* as g-eval's default. My reading of the two pages is
  that the pin is real for the *model* (a fixed OpenAI ID) — but I do not
  resolve the contradiction here; the open reconciliation question is whether
  that pin is absolute (g-eval always routes `gpt-4.1-2025-04-14`, requiring
  OpenAI credentials) or whether it is the OpenAI*credential-branch* default
  within the ambient-selection mechanism #1305 describes, with a fallback to
  other families when OpenAI credentials are absent. Neither page states which,
  and no CLI probe was run in this trial. See the **Contradicts:** line below
  and issue #1352.

### Claim 3: g-eval has a non-zero default threshold — `0.7` — and passes when `score >= threshold`; a bare `g-eval` assert therefore gates by default, unlike the context-based siblings whose documented default is `0`
- **Evidence**: The usage config (`threshold: 0.7 # Optional, defaults to 0.7`)
  and the "How it works" pass-condition sentence.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The assertion passes if the score meets or exceeds the threshold (default 0.7)." and "threshold: 0.7 # Optional, defaults to 0.7"
- **Our assessment**: The per-type threshold-defaults picture (#1334 Claim 2:
  "each page must be read on its own") gains its strongest counter-member.
  `context-faithfulness` (#1320 Claim 2) and `context-recall` (#1332 Claim 2)
  document `0`; `conversation-relevance` documents `0.5` (#1334 Claim 2); g-eval
  documents `0.7`. So g-eval is *not* a member of the score-blind fail-open
  family (#1305 Claim 10's `llm-rubric` pass-field semantics; #1287 Claim 3's
  test-case `threshold: 0`): a bare g-eval assert is a real gate at 0.7. That is
  the documented-behavior counter-case teams should cite against the "model-graded
  asserts don't gate by default" generalization — though the *judge* (Claim 2)
  remains the contradiction-filed question.

### Claim 4: Array-valued `value` criteria are graded independently and the scores are averaged — the averaged score alone is compared against the threshold (a semantic flattening that can mask a failing criterion); an empty array is a configuration error that fails with a clear reason (fails closed, not silently green)
- **Evidence**: The "How it works" array sentence, verbatim.
- **Confidence**: settled (documented product behavior)
- **Quote**: "When `value` is an array, each criterion is graded independently and the scores are averaged; the averaged score is compared against the threshold. An empty array is a configuration error and fails with a clear reason."
- **Our assessment**: Two gate-design implications for Ch05. First, the
  *average* is the only number that meets the threshold: a single criterion
  scoring 0.0 against `threshold: 0.7` fails visibly, but the same criterion
  at 0.0 averaged with three criteria at 1.0 yields 0.75 and *passes* — the
  array form trades single-criterion strictness for aggregate tolerance, and
  nothing on the page surfaces per-criterion scores in the pass/fail verdict.
  Teams that want "every criterion must pass" must use one `g-eval` assert per
  criterion rather than an array. Second, the empty-array behavior is the
  page's own fail-closed instance: it is a hard config error with a clear
  failure reason, the inverse of the silent-green `threshold: 0` footguns
  (#1287 Claims 3/4) — worth recording as the vendor's config-error policy for
  this type.

### Claim 5: `not-g-eval` inverts the gate to "passes when the grader score is *below* the threshold", and grader transport/parse failures are reported as failures in **both** directions — an inverted g-eval can never be silently passed by a broken grader
- **Evidence**: The "Negation with `not-g-eval`" section, verbatim.
- **Confidence**: settled (documented product behavior)
- **Quote**: "`not-g-eval` passes when the grader score is **below** the threshold. Transport or parse failures from the grader are reported as failures in both directions — a grader error is not treated as evidence that the criterion was or was not met, so inversion never silently turns a failed grader call into a pass."
- **Our assessment**: The Prospector's fail-closed question resolves *for
  g-eval*: the inversion is fail-closed symmetrically — a positive g-eval and a
  `not-g-eval` both report grader transport/parse failure as failure, so the
  inverted "must not leak PII" gate cannot be waved through by a broken judge.
  The contrast with #1305 Claim 4 is real and I record it as a per-type
  *difference in documentation*, not a contradiction: #1305 documented the
  fail-closed property only for the *inverted* `trajectory:goal-success` form
  (its asymmetry finding); g-eval is documented for *both* directions on its own
  page. Whether that symmetry is family-wide is still unanswered — the
  trajectory page has no equivalent sentence — so the guide should not
  generalize beyond what each per-type page states.

### Claim 6: A `g-eval` assertion makes **two grader calls** — one to generate evaluation steps, one to score the output — a 2x judge-call cost/latency multiplier per assertion relative to a single-call rubric judge
- **Evidence**: The LiteLLM subsection's premise sentence, verbatim.
- **Confidence**: settled (documented product behavior — the call count is a
  structural fact; the page gives no measured cost/latency figures)
- **Quote**: "G-Eval makes one grader call to generate evaluation steps and another to score the output."
- **Our assessment**: For Ch05 gate costing this is the first concrete
  per-assertion call-count data point in the rubric family: each g-eval assert
  burns two judge round-trips (plus the outputs being graded), versus `llm-rubric`'s
  single call. With multi-criterion arrays (Claim 4) the question of whether the
  steps-generation call is per-assertion or per-criterion is not stated on the
  page — I do not invent the accounting. The two-call structure is exactly why
  the LiteLLM reuse pattern (Claim 8) exists: routing both calls through one
  configured grader endpoint keeps the judge self-consistent across the
  generate-then-score pair.

### Claim 7: The grader override follows the family mechanics — `provider:` on the assertion or `defaultTest.options.provider` replaces the default evaluator, and pinning grader parameters (e.g., `temperature: 0`) for repeatability requires expanding the shorthand provider into an `id` + `config` block
- **Evidence**: The "Customizing the evaluator" section's two override forms and
  the `id`+`config` expansion example.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Like other model-graded assertions, you can override the default evaluator:" and "To set grader parameters such as `temperature` for repeatability, expand the shorthand into an `id` + `config` block:"
- **Our assessment**: Redundant with the hub note's override mechanics (#1305
  Claims 2, and the shorthand-provider `config`-inheritance warning), which is
  the expected redundancy for a per-type page. The repeatability route is the
  page's concrete answer to judge variance: expand to `id`+`config` to set
  `temperature: 0`. Two caveats carried from the hub: per #1305 Claim 7 the
  built-in OpenAI grader already runs at `temperature=0` (so for the pinned
  default the knob is moot), while a custom override provider that would
  otherwise inherit a non-zero default does need the explicit set; and GPT-5-series
  reasoning models ignore `temperature` entirely — neither caveat is restated on
  this page, both are the hub's.

### Claim 8: The documented LiteLLM grader-reuse pattern — reference a configured `litellm:*` provider ID on the assertion *and* restrict the test target via `tests[].providers` so the graded target is not also the grader
- **Evidence**: The "Using LiteLLM as the G-Eval grader" subsection's config.
- **Confidence**: settled (documented product behavior)
- **Quote**: "To reuse a configured LiteLLM provider for both calls, reference its ID on the assertion and restrict the test target to the provider being evaluated:"
- **Our assessment**: The self-hosting/proxy workaround the triage flagged: with
  both grader calls going to a configured `litellm:gemini-pro` endpoint (see the
  artifact below), the *target* under test stays restricted to `openai:gpt-5` in
  `tests[].providers`. This is the concrete pattern for a self-hosted/proxied
  judge: the grader is a configured endpoint, the evaluated target is a separate
  provider restricted at the `tests[]` level — preventing the graded target from
  double-serving as its own judge. Ties into the LiteLLM provider surface
  already in `source-notes/` at the routing level only; no existing note
  documents this grader-reuse shape.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/g-eval/
(sections as noted).

### Basic usage (verbatim from "How to use it")

```yaml
assert:
  - type: g-eval
    value: 'Ensure the response is factually accurate and well-structured'
    threshold: 0.7 # Optional, defaults to 0.7
```

### Multiple criteria as an array (verbatim from "How to use it")

```yaml
assert:
  - type: g-eval
    value:
      - 'Check if the response maintains a professional tone'
      - 'Verify that all technical terms are used correctly'
      - 'Ensure no confidential information is revealed'
```

### `not-g-eval` inversion (verbatim from "Negation with `not-g-eval`")

```yaml
assert:
  - type: not-g-eval
    value: 'The response leaks personally identifiable information'
    threshold: 0.7
```

### Assertion-level grader override (verbatim from "Customizing the evaluator")

```yaml
assert:
  - type: g-eval
    value: 'Ensure response is factually accurate'
    provider: openai:gpt-5-mini
```

### Global grade via test options (verbatim from "Customizing the evaluator")

```yaml
defaultTest:
  options:
    provider: openai:gpt-5-mini
```

### Repeatable judge via `id` + `config` (verbatim from "Customizing the evaluator")

```yaml
assert:
  - type: g-eval
    value: 'Ensure response is factually accurate'
    provider:
      id: openai:gpt-5-mini
      config:
        temperature: 0
```

### LiteLLM grader reuse (verbatim from "Using LiteLLM as the G-Eval grader")

```yaml
providers:
  - id: openai:gpt-5
  - id: litellm:gemini-pro
    config:
      apiBaseUrl: http://localhost:4000
      temperature: 0
tests:
  - providers:
      - openai:gpt-5
    assert:
      - type: g-eval
        value: 'Check whether the answer is grounded and complete'
        provider: litellm:gemini-pro
```

### Complete example (verbatim from "Example")

```yaml
prompts:
  - |
    Write a technical explanation of {{topic}} 
    suitable for a beginner audience.
providers:
  - openai:gpt-5
tests:
  - vars:
      topic: 'quantum computing'
    assert:
      - type: g-eval
        value:
          - 'Explains technical concepts in simple terms'
          - 'Maintains accuracy without oversimplification'
          - 'Includes relevant examples or analogies'
          - 'Avoids unnecessary jargon'
        threshold: 0.8
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 8** (the hub's
    `rubricPrompt`-swap rule: "This approach works with `llm-rubric`, `g-eval`,
    and `model-graded-closedqa`") — this page confirms g-eval's rubric-member
    position: its `value` field *is* the criterion text, and the grader override
    surface (`provider:`/`defaultTest.options.provider`) matches the family
    mechanics. (Verified: #1305 Claim 8.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (the
    model-assisted catalogue, which names `g-eval` among "model-assisted, and
    rely on LLMs or other machine learning models" checks) — this page is the
    per-type reference under that catalogue row, with no deterministic claim
    about the assert. (Verified: `docs-promptfoo-assertions-metrics.md` Claim 10,
    its catalogue enumeration lists g-eval beside llm-rubric and the context-*
    families.)
  - `source-notes/docs-promptfoo-conversation-relevance.md` **Claim 2** ("The
    threshold defaults to `0.5` when omitted" — the per-type-defaults doctrine,
    "each page must be read on its own") — g-eval's documented `0.7` default is
    a new member of that per-type-defaults family, consistent with the doctrine
    rather than altering it. (Verified: #1334 Claim 2.)

- **Contradicts**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 1** (the hub's
    family-wide finding that a model-graded assert's judge is *unpinned / chosen
    from ambient credentials* — "nothing is pinned by default") vs this page's
    dated default judge pin (`gpt-4.1-2025-04-14`, Claim 2 above). Material
    opposition on the same topic (what a model-graded assert pins by default)
    with forking guide advice: #1305's Ch05 rule reads "the judge is ambient —
    pin it yourself," while g-eval's page states a concrete pinned default.
    **Filed as contradiction issue #1352** per MINER.md §4a; I do not pick a
    verdict in this note. The reconciliation question (absolute pin requiring
    OpenAI credentials, vs OpenAI-credential-branch of the ambient-selection
    mechanism) is left for the resolver. (Verified: #1305 Claim 1 quote, and the
    g-eval page wording cited in Claim 2.)
  - Explicitly *not* a contradiction: g-eval's symmetric fail-closed inversion
    (Claim 5) vs #1305 Claim 4's finding that fail-closed was documented only
    for the *inverted* `trajectory:goal-success` form. Different assertion
    types; #1305 said "documented *only for the inverted form*" about trajectory,
    not "inversion is never fail-closed family-wide." g-eval is a second,
    independently documented case with *stronger* wording (both directions).
    Recorded as a documentation-difference extension, not an opposition (no new
    contradiction issue beyond #1352).

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — directly
    fills that note's deliberate scoping gap. Its Scope/Extraction Notes list
    "g-eval" among the per-type sub-pages explicitly NOT followed; this note
    supplies the per-type delta (the dated judge pin, the 0.7 default, the
    two-call CoT structure, the array-averaging rule, the symmetric fail-closed
    inversion). Claim 8 of the hub ("swap rubricPrompt uniformly for
    llm-rubric/g-eval/model-graded-closedqa") is now backed by the per-type
    page's `value`-as-criterion contract.
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` (#1320)
    **Claim 2** and `source-notes/docs-promptfoo-model-graded-context-recall.md`
    (#1332) **Claim 2** (the documented `threshold: 0` defaults) — g-eval's
    documented `0.7` default is the rubric-based counter-case in the per-type
    default-threshold family: two context-based pages document `0`, one
    conversation page documents `0.5`, g-eval documents `0.7`. The "model-graded
    asserts are score-blind by default" reading does not hold for g-eval.
    (Verified: #1320 Claim 2, #1332 Claim 2.)
  - `source-notes/docs-promptfoo-answer-relevance.md` (#1319) **Claim 4** (the
    `rubricPrompt` slot-divergence finding: in `answer-relevance` it controls
    question generation, whereas in `llm-rubric` and `g-eval` it customizes the
    grading rubric) — this page confirms the g-eval side of that claim's
    semantics via `value`-as-criteria and the grader-override surface. (Verified:
    #1319 Claim 4.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) — the hub's
    scoring/aggregation model underlies the averaged-array pass semantics
    (Claim 4); #1287 Claim 3's test-case `threshold: 0` silent-green footgun is
    the config-level contrast to g-eval's empty-array fail-closed config error.
    (Verified: #1287 Claims 3/4 framing as referenced by #1305's Cross-References.)

- **Novel**: The risk *frame* is already in the corpus (judge pinning and
  fail-open vs fail-closed semantics from #1305/#1320/#1332). What is new here:
  1. **A dated default judge pin on a model-graded page** (Claim 2) — the first
     corpus instance of a *specific model-ID default* in this family; the source
     of the filed contradiction #1352.
  2. **The two-grader-call CoT structure** (Claim 6) — the first documented
     per-assertion judge-call *count* in the rubric family (2 calls/assert), a
     structural cost input the hub note lacked.
  3. **The array-averaging semantic** (Claim 4) — independent per-criterion
     grading flattened to one averaged score for the threshold; the first
     multi-criterion aggregation shape documented for a rubric assert on a
     per-type page, with the failing-criterion-masking consequence.
  4. **Empty-array config error, fail-closed** (Claim 4) — a documented
     config-error path with a clear failure reason, distinct from the silent-green
     config footguns (#1287 Claims 3/4).
  5. **Symmetric fail-closed `not-g-eval`** (Claim 5) — the first corpus
     documentation of an inverted model-graded assert that is fail-closed in
     *both* directions, extending (not contradicting) #1305 Claim 4's
     inverted-form-only finding for `trajectory:goal-success`.
  6. **The LiteLLM grader-reuse pattern** (Claim 8 / artifact) — a configured
     `litellm:*` provider as the judge for both calls with the target restricted
     in `tests[].providers`; no existing note documents this shape.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology /
  judge pinning**: do NOT update the guide's judge-pinning rule from this page
  alone — g-eval's dated default pin (Claim 2) is in open contradiction (#1352)
  with #1305 Claim 1's ambient-judge finding, and the reconciliation requires
  resolving that issue first. When resolved: if the pin holds, Ch05 should state
  that g-eval is the model-graded exception (a pinned default judge) and that
  other model-graded asserts still follow the ambient rule; if it does not hold,
  the `gpt-4.1-2025-04-14` sentence is the OpenAI-credential-branch default and
  the pin-everything rule stands for g-eval too. Either way the guide should not
  keep asserting an unpinned blanket rule as if g-eval's dated pin did not exist.
- **Chapter 05 — gate cost modeling**: add the two-grader-call factor (Claim 6)
  to the model-graded cost tier: each g-eval assert is 2 judge calls per
  assertion (steps-generation + scoring), so a g-eval gate is ≥2x the judge-call
  budget of a single-call `llm-rubric` gate over the same row count — and the
  array form does not reduce the count per the page (per-criterion accounting
  is not documented; do not assume it).
- **Chapter 05 — gate-design checklist**: add the averaged-array hazard (Claim
  4): an array-valued `g-eval` gates on the *average* of independently graded
  criteria, so a failing criterion can be masked by passing siblings (worked
  consequence: one criterion at 0.0 averaged with three at 1.0 = 0.75, passing a
  0.7 threshold) — for "every criterion must pass" semantics, use one `g-eval`
  assert per criterion. Also log the empty-array hard-fail as a positive
  (vendor-documented config error that fails closed, not green).
- **Chapter 05 / Chapter 06 — security "must not" gates**: record the symmetric
  fail-closed inversion (Claim 5) for the `not-g-eval` "must not reveal PII"
  pattern (#1349's Ch06 read): a grader transport/parse failure reports as a
  failure in both directions, so the inverted gate cannot be silently passed by
  a broken judge — but label it as g-eval-documented, and do not generalize it to
  `not-trajectory:goal-success` or other inverted types beyond what their own
  pages state (#1305 Claim 4).
- **Chapter 05 — repeatable judges**: the `id`+`config` expansion for
  `temperature: 0` (Claim 7, with the #1305 Claim 7 caveat that the built-in
  OpenAI grader already runs at `temperature=0` and GPT-5-series ignores
  `temperature`) is the documented self-hosted/proxied judge pattern, including
  the LiteLLM reuse shape (Claim 8) — add to the "how to pin a judge"
  configuration examples.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/g-eval/).
  Page footer: "Last updated on **Sep 16, 2026** by **jameshiester-oai**" —
  matches the triage window; `date_published` carries the last-updated date
  (same convention as the sibling notes). Quotes and code blocks verified
  character-for-character against the fetched rendered content before writing.
  No sub-pages followed: the "Further reading" targets are the hub page (already
  mined as #1305) and the external G-Eval paper (not promptfoo config); the
  llm-rubric grader-override link is cross-referenced, not re-followed, per the
  one-note-per-sub-page convention.
- **Triage key-question resolutions** (all three Prospector comments read as
  UNTRUSTED input, each item re-verified against the page):
  1. **Default judge pin** — confirmed the page states "gpt-4.1-2025-04-14 by
     default," and that this tensions #1305 Claim 1. Refused to pick a winner;
     filed **contradiction #1352** and referenced it under **Contradicts:**
     (MINER.md §4a). The open reconciliation question (absolute pin vs
     OpenAI-branch default) is recorded in Claim 2 without a verdict.
  2. **Two grader calls per assertion** — confirmed the sentence "makes one
     grader call to generate evaluation steps and another to score the output"
     (Claim 6); cost accounting beyond the call count is not stated and was not
     invented.
  3. **Array averaging + empty-array contract** — confirmed both in one sentence
     (Claim 4); the masking consequence is my synthesis from the documented
     arithmetic, flagged as such.
  4. **`not-g-eval` failure symmetry** — confirmed "in both directions"
     (Claim 5); checked that #1305 Claim 4's finding (fail-closed documented only
     for the inverted trajectory form) is about the trajectory page, not a
     family-wide exclusion — recorded as extension, no contradiction issue beyond
     #1352.
  5. **Repeatability override** — confirmed the `id`+`config` expansion guidance
     (Claim 7).
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `docs-promptfoo-classifier-grading.md` (#1288) — classifier assert path
    (HF classifiers, label-bound thresholds); no g-eval/CoT-rubric semantics;
    dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — OWASP red-team methodology/
    SDLC phases; no eval-assert config surface; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage by an SRE
    Agent; no eval-assert config; dismissed.
  - `blog-promptfoo-red-team-claude.md` (#689) — red-team plugin strategy for
    Claude; rubric/latency asserts used as tools, no g-eval grading semantics;
    dismissed.
  - `docs-google-sre-team-lifecycles.md` (#907) — Google SRE org/lifecycle
    chapter; no LLM-eval content; dismissed.
  - `docs-promptfoo-assertions-metrics.md` (#1287) — **cited** (Corroborates
    Claim 10; Extends, the aggregation hub).
  - `blog-promptfoo-red-team-gemini.md` (#690) — per-model red-team plugin
    strategy; no g-eval config semantics; dismissed.
  - `docs-promptfoo-javascript-assertions.md` (#1304) — custom-JS assertion
    surface; no model-graded-rubric semantics; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated vendor;
    dismissed.
  - `docs-promptfoo-model-graded-context-recall.md` (#1332) — **cited** (Extends
    Claim 2, the documented `0` default counter-member to g-eval's `0.7`).
  - Additional cross-refs from searching `source-notes/` per MINER.md §4 (not in
    the candidate file): `docs-promptfoo-model-graded-metrics.md` (#1305 — cited
    heavily, Corroborates/Contradicts/Extends), `docs-promptfoo-model-graded-context-faithfulness.md`
    (#1320 — cited Claim 2), `docs-promptfoo-conversation-relevance.md` (#1334 —
    cited Claim 2), `docs-promptfoo-answer-relevance.md` (#1319 — cited Claim 4).
- **Cross-ref verification (§4b)**: every cited claim was located and read in the
  cited note before writing — #1305 Claims 1 (headline + quote), 7, 8;
  `docs-promptfoo-assertions-metrics.md` Claim 10 (catalogue line naming g-eval);
  #1320 Claim 2; #1332 Claim 2; #1334 Claim 2 (quote); #1319 Claim 4. Claim
  numbers verified against the cited notes' own numbering; no claim numbers
  invented. Source-note issue numbers read from each cited note's frontmatter:
  #1305, #1287 (assertions-metrics), #1320, #1332, #1334, #1319.
- **Contradiction filed**: **#1352** (g-eval default judge pin vs #1305 Claim 1),
  created from `.github/ISSUE_TEMPLATE/contradiction.yml` fields before this PR,
  referenced in the **Contradicts:** line and Claim 2. No verdict assigned here;
  the fail-closed-vs-fail-open surface was explicitly assessed and *not* filed
  (complementary mechanisms / per-type documentation difference, per MINER.md
  §4a "when NOT to file").
- `confidence_overall` is `emerging`, matching the sibling promptfoo config notes
  (#1305, #1320, #1332, #1319, #1334): the individual behavior/default claims
  (Claims 1, 3-8) are settled-for-product-behavior and directly checkable against
  an installed CLI, but this is thin vendor documentation with no measured
  judge-agreement, gate-cost, or calibration figures, and the headline question
  (Claim 2) is an open contradiction awaiting resolution — marked `emerging` on
  the strength of the body of evidence, consistent with the family convention.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited; they
  are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.