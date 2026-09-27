---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/model-graded-closedqa
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Model-Graded Closed QA"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-27
date_extracted: 2026-09-27
last_checked: 2026-09-27
status: current
confidence_overall: emerging
issue: "#1483"
---

# Promptfoo Configuration: Model-Graded — Model-Graded Closed QA

> The per-type reference page for `model-graded-closedqa`, the one
> model-graded assert in this family whose verdict is a **string-suffix
> parse** rather than a structured field or a score: "The assertion passes
> if the response ends with 'Y' and fails if it ends with 'N'", and anything
> ending in neither letter is a *malformed response* that "fail[s] both
> forms with score `0`". It contributes the corpus's first documented
> fail-closed statement covering the **positive** form of a model-graded
> assert (the three earlier instances — #1305 Claim 4, g-eval Claim 5,
> llm-rubric Claim 7 — are all scoped to the inverted form), the
> `{{input}}` / `{{criteria}}` / `{{completion}}` `rubricPrompt` variable
> set that makes the hub note's `{{ output }}` / `{{ rubric }}` multilingual
> recipe **non-portable** to this assert (contradiction **#1486**), the
> OpenAI-`evals`-inherited grader prompt, and a page-level silence on the
> default judge (a third data point for open contradiction **#1352**).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Model-graded
  Closed QA" per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `model-graded-closedqa` behavior — authoritative for *what
  promptfoo does* with a given config (the verdict parse, the inversion
  semantics, the `rubricPrompt` variable surface, the override surface), but
  vendor-positioned: the page carries no measured judge-agreement,
  gate-failure-rate, cost, or calibration figures, and no independent
  practitioner validation. Its sibling `llm-rubric` page's one comparative
  claim about this prompt ("It is similar to OpenAI's model-graded-closedqa
  prompt, but can be more effective and robust in certain cases") is
  asserted without evidence, so this page carries no comparative claim of its
  own. Everything below is checkable against an installed CLI — and, unusually
  for this family, most of it is also checkable against the vendor's
  published implementation (see Extraction Notes).
- **Scope**: A short, self-contained reference page (intro, How to use it,
  How it works, Example Configuration, Overriding the Grader, Customizing the
  Prompt, Further reading). It is the deep-dive on the
  closed-question-answering member of the model-graded class that
  `docs-promptfoo-model-graded-metrics.md` (#1305) catalogued at claim level
  and explicitly did **not** follow — that note's Extraction Notes list
  "model-graded-closedqa" among the un-followed per-type sub-pages, and its
  `Scope` section repeats the deferral. This note therefore carries the
  *delta* (the Y/N suffix-parse contract, the malformed-response clause, the
  fail-closed-both-forms sentence, the third `rubricPrompt` variable set, the
  OpenAI-evals provenance, the default-judge silence), not a re-extraction of
  the grader-override boilerplate that #1305 Claim 2 and the sibling per-type
  notes already hold. Does NOT cover the model-graded hub page (#1305), the
  aggregation/scoring model of the assertions hub (#1287), or the sibling
  sub-pages (one note per sub-page, per the corpus convention).
- **Last updated**: the page footer reads "Last updated on **Sep 27, 2026**
  by **mldangelo-oai**" — current (same day as this extraction).

## Extracted Claims

### Claim 1: The verdict is a string-suffix test on the grader's own response — pass iff the response ends with `Y`, fail iff it ends with `N`, and `not-model-graded-closedqa` inverts the polarity by requiring an `N` verdict — so the assert is binary (1 / 0) with no `threshold` anywhere in its contract
- **Evidence**: The "How it works" section: the two verdict bullets
  (`Y` / `N`), the single sentence stating the parse, and the page's
  Example Configuration (two asserts, each with its own `value:` criterion).
  Verified by full read that the string `threshold` does not appear anywhere
  on the page.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Under the hood, `model-graded-closedqa` uses OpenAI's closed QA evaluation prompt to analyze the output. The grader will return:" (then, verbatim bullets, "`Y` if the output meets the criterion" and "`N` if the output does not meet the criterion") and "The assertion passes if the response ends with 'Y' and fails if it ends with 'N'. Use `not-model-graded-closedqa` to require an 'N' verdict instead."
- **Our assessment**: This is a *parse* surface, not a *score* surface, and
  that is the whole operational content of the type: the gate's granularity
  is one bit, and the bit is read off the final character of a free-form
  judge response. Two consequences. First, no graded-quality property can be
  expressed here — a criterion like "quality 4/5" has nowhere to land,
  because the only values the assert can produce are 1 and 0; the family
  members that do carry a graded surface are `g-eval` (normalized 0–1 score,
  default `threshold: 0.7`) and `llm-rubric` (a `pass` field plus score).
  Second, criteria are per-assert and independent: the page's own Example
  Configuration encodes two criteria as two asserts, so an N-criterion
  closed-QA gate costs N judge verdicts, and each verdict is a separate
  call. Contrast `g-eval` Claim 6, where a *single* assert already costs two
  grader calls; the cost shape here is linear in criteria, not in asserts
  times two. The binary score still feeds the test-case weighted average
  (#1287 Claim 1), which is where the real weakening risk lives (Claim 7).

### Claim 2: A grader response that ends in neither `Y` nor `N` is neither a silent pass nor a clean fail — it is a *malformed response*, and malformed responses are graded as failures at score 0, so the suffix parse is strict in both directions and any trailing character after the verdict letter flips a passing case
- **Evidence**: The third sentence of the same "How it works" paragraph
  ("Grader errors and malformed responses fail both forms with score `0`"),
  read together with the page's own custom-prompt example, whose final line
  is an explicit output instruction. The "malformed responses" clause is new
  to the corpus: #1305 Claim 4, g-eval Claim 5 and llm-rubric Claim 7 all
  quote the *transport/parse-failure* wording, and none of the three covers a
  response that parses as neither verdict.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Grader errors and malformed responses fail both forms with score `0`."
- **Our assessment**: The fail direction is the load-bearing half and it is
  invisible in the report: a judge that answers "The response meets the
  criterion. Y." — a period after the letter, a closing sentence, a quoted
  letter — does not end in `Y`, so a *correct* grade is recorded as a failing
  assertion. Nothing on the page documents leniency (no punctuation
  stripping, no "last Y/N token", no regex), and the page's own example shows
  the vendor's own answer to this hazard: the custom prompt's last line is
  "Does this response meet the criterion? Answer Y or N." — the output
  instruction is not decoration, it is the parse contract restated in the
  prompt. Compare the sibling that documents its parse *positively*:
  factuality (#1348 Claim 5) lists the two formats its checker accepts (a bare
  letter, or `{"category", "reason"}` JSON), so a mis-formatted custom rubric
  there is at least predictable; this page documents only the negative
  contract
  only, which means a custom-prompt author has to infer the acceptable shape
  from the absence of a failure. The guide's rule this supports: when you
  override `rubricPrompt`, the override's *output format* is part of the gate
  and must be reviewed as carefully as the criterion text.

### Claim 3: This page states the fail-closed property for **both** polarities of a model-graded assert in one sentence — the first positive-form instance in the corpus, which narrows #1305 Claim 4's documented asymmetry, but the wording is narrower than the family sentence and must not be read as "fail-loud"
- **Evidence**: The same "How it works" sentence, which covers the assertion
  *and* its negation in one breath ("Use `not-model-graded-closedqa` to
  require an 'N' verdict instead. Grader errors and malformed responses fail
  both forms with score `0`."). Compare the three earlier instances' wording,
  quoted verbatim in the cited notes.
- **Confidence**: settled for the documented claim; the
  "fail-closed but not fail-loud" reading below is the Miner's
- **Quote**: "The assertion passes if the response ends with 'Y' and fails if it ends with 'N'. Use `not-model-graded-closedqa` to require an 'N' verdict instead. Grader errors and malformed responses fail both forms with score `0`."
- **Our assessment**: This is the note's highest-value item for the corpus's
  judge-trust thread, and it does change an existing note's answer. #1471
  (llm-rubric) Claim 7 asked whether three instances of the symmetric
  fail-closed sentence were enough to state it as a family property, and
  answered **no** — because all three were scoped to the *inverted* form and
  "no page documents the positive form". This page documents a fourth
  instance covering both polarities. It still does not license a family law
  (it is one assert type, and the other per-type pages are unchanged), so
  #1305 Claim 4's asymmetry finding stands as a per-page statement; what
  changes is that "the positive form is undocumented" is no longer true of
  the family. The nuance worth carrying into the guide is the wording
  difference the triage flagged: the other three instances say transport or
  parse failures "are reported as failures", while this one says they "fail
  both forms with score `0`". That is a claim about the **score**, and a
  score-0 assertion failure is a *failed assertion* in the report — so a
  broken grader here presents as model-red unless the operator goes looking.
  The implementation does mark these results (`metadata.graderError: true`,
  and the negation handler propagates a grader failure verbatim instead of
  flipping it), so the discrimination is available in assertion metadata but
  not in the pass column. Ch05's "can your gate tell wrong from a model
  break?" checklist should therefore say: fail-closed per assert type, and
  treat the score as *not* evidence about the output; read assertion metadata
  to separate a grader error from a model disagreement.

### Claim 4: The closedqa `rubricPrompt` binds `{{input}}`, `{{criteria}}`, and `{{completion}}` — a third distinct variable set in this family, and the page's own example binds neither `{{ output }}` nor `{{ rubric }}`, so a rubric prompt ported from `llm-rubric`/`g-eval` binds nothing and renders silently
- **Evidence**: The "Customizing the Prompt" section: its one prose sentence
  and the worked `rubricPrompt` YAML (Concrete Artifacts below, verbatim).
  The divergence from the hub's multilingual recipe is checkable on both
  pages; the vendor's own implementation confirms the context keys (see
  Extraction Notes).
- **Confidence**: settled (documented product behavior, and implementation-
  confirmed)
- **Quote**: "You can customize the evaluation prompt using the `rubricPrompt` property:" (followed, verbatim, by the config whose template variables are `Question: {{input}}`, `Criterion: {{criteria}}`, `Response: {{completion}}`)
- **Our assessment**: This is the note's main contribution and it holds, so
  it is filed as contradiction **#1486** rather than argued here. The
  practical form of the finding is the *silence*, not the mismatch: unlike
  factuality (#1348 Claim 5), which enumerates its three variables and its
  two accepted parse formats, this page documents one example and no
  compatibility statement — so a reader who wants to know whether the hub's
  `{{ output }}` / `{{ rubric }}` template also works here has nothing to read.
  The implementation answers it (the closedqa template context is the test
  vars plus `input` / `criteria` / `completion`; unbound Nunjucks variables
  render as empty strings rather than erroring, because grader prompts are
  rendered with `throwOnUndefined: false`), which produces the worst
  possible failure shape: a mis-ported rubric does not error, it renders with
  empty output and empty criterion, and the judge grades against nothing.
  One edge worth knowing, because it makes the failure suite-dependent: the
  context is built as the test vars *spread first*, so a test that happens to
  define a var named `output` or `rubric` would bind it — the same config
  can silently work in one test row and silently grade nothing in the next.
  The guide rule this supports is the one #1348 already states in its Guide
  Impact: `rubricPrompt` is per-assert, so grep the variable names when
  porting one, and do not treat "works with llm-rubric, g-eval, and
  model-graded-closedqa" as license to swap by rename.

### Claim 5: The grader prompt is inherited from OpenAI's public evals, and the vendor's default prompt asks the judge to reason step by step, then print a single `Y`/`N`, then **repeat the letter at the end** — which is what makes a suffix parse viable, and makes this assert the family's one surface where leading scratchpad is expected rather than a misparse hazard
- **Evidence**: The intro paragraph and the first sentence of "How it
  works" name the provenance twice (public evals prompt / closed QA
  evaluation prompt). The default prompt's shape — including the
  repeat-the-letter-at-the-end instruction — is *not* on the page; it is in
  the vendor's published implementation, quoted in Concrete Artifacts with
  its file path and permalink so the distinction is auditable.
- **Confidence**: settled for the provenance (stated on the page); the
  structural reading of *why* the parse is a suffix test is the Miner's, and
  the prompt text it rests on is implementation evidence rather than
  documented behavior
- **Quote**: "`model-graded-closedqa` is a criteria-checking evaluation that uses OpenAI's public evals prompt to determine if an LLM output meets specific requirements." and "Under the hood, `model-graded-closedqa` uses OpenAI's closed QA evaluation prompt to analyze the output."
- **Our assessment**: Two things to keep. (a) Provenance: this is the second
  corpus case of a judge prompt inherited from OpenAI-side evals tooling,
  after factuality's `fact.yaml` taxonomy (#1348 Claim 1) — a second data
  point for the guide's "where did this judge's rubric come from?" rule, and
  a reminder that the rubric text a team is debugging may live in another
  project's eval registry rather than in their config. (b) The parse shape
  is the interesting finding, and it inverts the hub's scratchpad-misparse
  family. #1305 Claims 5/6 describe the hazard where a self-hosted judge's
  reasoning text gets read *as* the verdict (JSON-first metrics parsing
  scratchpad JSON, `select-best` reading a scratchpad index), with
  `showThinking: false` as the remedy. Here the default prompt *asks* for
  step-by-step reasoning and then puts the verdict last, so the trailing
  character is the verdict by construction — this parse surface is
  structurally immune to the leading-scratchpad problem the rest of the
  family has. The flip side is the trailing-text fragility of Claim 2, and
  it is why the "repeat the letter again by itself on a new line"
  instruction is load-bearing: it is the only reason a
  reasoning-then-verdict response still ends in the verdict character. A
  custom prompt that asks for anything after the letter, or a judge that
  truncates before it, loses the property — and the page documents no
  handling for that at all.

### Claim 6: The grader-override surface is the family's usual three levels (CLI `--grader`, `defaultTest.options.provider`, assertion-level `provider`), and the page names **no** default judge anywhere — so a bare `model-graded-closedqa` assert is graded by the ambient credential-selected judge, and the page's own examples are pins while its default is undocumented
- **Evidence**: The "Overriding the Grader" section — its opening sentence
  and the three numbered forms (Concrete Artifacts, verbatim). The absence
  of any default-judge sentence was verified by full read of the page; the
  three examples all pin `openai:gpt-5-mini` or `openai:gpt-5`.
- **Confidence**: settled for the override surface (documented); the
  ambient-default consequence is #1305 Claim 1 applied to this page's silence
- **Quote**: "Like other model-graded assertions, you can override the default grader:"
- **Our assessment**: Deliberately not re-extracted as a new mechanism —
  #1305 Claim 2 holds the precedence chain and the shorthand-`config` trap,
  and the sibling per-type notes (llm-rubric Claim 10, factuality Claim 4)
  already record the same three forms. What is new is the *silence* as a
  third data point for open contradiction #1352: the llm-rubric page
  enumerates the ambient roster with concrete model IDs (#1471 Claim 5),
  g-eval names a dated default pin (#1349 Claim 2), factuality and this page
  name nothing. A reviewer working only from this page cannot learn which
  judge a bare assert uses at all — they have to go to the hub page for the
  ambient-credential mechanism — and the guide's pin-the-judge rule cannot be
  satisfied by copying a default from here because there isn't one. Note the
  documentation gap this exposes: the page's examples demonstrate a *pinned*
  judge while its default is unspecified, which reads as reassurance to a
  skimming reader and is the opposite of a guarantee.

### Claim 7: `value:` is the criterion and each assert is one independent yes/no check with no threshold and no intra-type aggregation — but the binary scores still feed the test-case weighted average, so a row's `threshold` is where a closedqa gate can be silently weakened
- **Evidence**: The "How to use it" config (with the `# Specify the criteria
  that the output must meet:` comment on the `value` line), the closing
  sentence of that section, and the Example Configuration's two-assert row.
  The absence of any `threshold` option is verified by full read.
- **Confidence**: settled for `value`-as-criterion and per-assert
  independence; the aggregation reading is the Miner's, on #1287's
  documented scoring model
- **Quote**: "# Specify the criteria that the output must meet:" and "This assertion will use a language model to evaluate whether the output meets the specified criterion, returning a simple yes/no response."
- **Our assessment**: The type is a boolean checklist, which makes it the
  cleanest possible instantiation of the corpus's "explicit, falsifiable
  pass/fail rubrics" rule (#261) — and the narrowest, because there is no
  gradient to calibrate. The gate's real fragility is one tier up: because a
  test case's score is the weighted average of its assertions' scores
  (#1287 Claim 1), a row carrying two closedqa asserts where one passes
  scores 0.5, and a test-case `threshold` below that converts a failed
  criterion into a green row. That is #1287 Claim 2's partial-credit shape
  one tier above the assertion, and it is reviewable only by reading the
  row's `threshold` — the closedqa page's silence on `threshold` invites
  exactly the misreading that the gate "has no threshold, so nothing to
  tune", when in fact the row-level threshold is doing the gating. Pair it
  with #1287 Claim 3 (`threshold: 0` = a gate that cannot fail) and the
  guide's row-level threshold belongs in the closedqa gate-review checklist
  for the same reason it belongs in every other gate's.

## Concrete Artifacts

### Basic usage (verbatim from "How to use it")

```yaml
assert:
  - type: model-graded-closedqa
    # Specify the criteria that the output must meet:
    value: Provides a clear answer without hedging or uncertainty
```

### The verdict contract (verbatim from "How it works")

> Under the hood, `model-graded-closedqa` uses OpenAI's closed QA evaluation
> prompt to analyze the output. The grader will return:
>
> - `Y` if the output meets the criterion
> - `N` if the output does not meet the criterion
>
> The assertion passes if the response ends with 'Y' and fails if it ends
> with 'N'. Use `not-model-graded-closedqa` to require an 'N' verdict
> instead. Grader errors and malformed responses fail both forms with score
> `0`.

(Reproduced as prose; the page renders the two `Y` / `N` items as a bulleted
list and the rest as a single paragraph.)

### Example configuration (verbatim from "Example Configuration")

```yaml
prompts:
  - 'What is {{topic}}?'
providers:
  - openai:gpt-5
tests:
  - vars:
      topic: quantum computing
    assert:
      - type: model-graded-closedqa
        value: Explains the concept without using technical jargon
      - type: model-graded-closedqa
        value: Includes a practical real-world example
```

### Grader override forms (verbatim from "Overriding the Grader")

```bash
promptfoo eval --grader openai:gpt-5-mini
```

```yaml
defaultTest:
  options:
    provider: openai:gpt-5-mini
```

```yaml
assert:
  - type: model-graded-closedqa
    value: Is concise and clear
    provider: openai:gpt-5-mini
```

### Custom rubric prompt (verbatim from "Customizing the Prompt")

```yaml
defaultTest:
  options:
    rubricPrompt: |
      Question: {{input}}
      Criterion: {{criteria}}
      Response: {{completion}}

      Does this response meet the criterion? Answer Y or N.
```

(The blank line before the instruction line is in the source block.)

### Miner verification against the vendor implementation (NOT from the docs page)

These are excerpts from the promptfoo repository, not from the URL in
`source_url`, recorded so the Assayer can check Claims 2–5 without an
installed CLI. All at `main` @
[`ca609b7`](https://github.com/promptfoo/promptfoo/tree/ca609b7dede818493f1d9aa9b39483f6f2c7e1fb).

`src/matchers/llmGrading.ts` — the template context and the parse
(https://github.com/promptfoo/promptfoo/blob/ca609b7dede818493f1d9aa9b39483f6f2c7e1fb/src/matchers/llmGrading.ts):

```ts
  const parsedOutput = tryParse(output);
  const templateVars = { ...(vars || {}), input, criteria: expected, completion: parsedOutput };

  const rubricPrompt = await loadRubricPrompt(grading?.rubricPrompt, OPENAI_CLOSED_QA_PROMPT);
  const prompt = await renderLlmRubricPrompt(rubricPrompt, templateVars);
```

```ts
  if (resp.error || !resp.output) {
    return graderFail(resp.error || 'No output', resp.tokenUsage);
  }
  ...
  try {
    const pass = resp.output.trimEnd().endsWith('Y');
    let reason;
    if (pass) {
      reason = `The submission meets the criterion:\n${resp.output}`;
    } else if (resp.output.trimEnd().endsWith('N')) {
      reason = `The submission does not meet the criterion:\n${resp.output}`;
    } else {
      return graderFail(
        `Model grader produced a malformed response:\n${resp.output}`,
        resp.tokenUsage,
      );
    }
    return {
      pass,
      score: pass ? 1 : 0,
      reason,
      tokensUsed: normalizeMatcherTokenUsage(resp.tokenUsage),
    };
```

`src/assertions/modelGradedClosedQa.ts` — the vendor's own note about the
variable set, and the inversion's grader-failure guard
(https://github.com/promptfoo/promptfoo/blob/ca609b7dede818493f1d9aa9b39483f6f2c7e1fb/src/assertions/modelGradedClosedQa.ts):

```ts
  // Note: rubricPrompt will be rendered later in matchesClosedQa with proper variables
  // (input, criteria, completion) available at that point
  ...
  // Grader failures must remain failures under negation.
  if (isGraderFailure(resp)) {
    return { ...resp, assertion };
  }
```

`src/matchers/shared.ts` — what a grader failure carries
(https://github.com/promptfoo/promptfoo/blob/ca609b7dede818493f1d9aa9b39483f6f2c7e1fb/src/matchers/shared.ts):

```ts
export function fail(
  reason: string,
  tokensUsed?: Partial<TokenUsage>,
): Omit<GradingResult, 'assertion'> {
  return {
    pass: false,
    reason,
    score: 0,
    ...
```

```ts
export function graderFail(
  reason: string,
  tokensUsed?: Partial<TokenUsage>,
): Omit<GradingResult, 'assertion'> {
  return {
    ...fail(reason, tokensUsed),
    metadata: { graderError: true },
  };
}
```

`src/matchers/rubric.ts` — grader prompts render unbound variables as empty
strings, not errors
(https://github.com/promptfoo/promptfoo/blob/ca609b7dede818493f1d9aa9b39483f6f2c7e1fb/src/matchers/rubric.ts):

```ts
const nunjucks = getNunjucksEngine(undefined, false, true);
```

(`getNunjucksEngine(filters, throwOnUndefined = false, isGrader = true)` —
so `throwOnUndefined` is off for grader prompts; see
`src/util/templates.ts` in the same commit.)

`src/prompts/grading.ts` — the default grader prompt, i.e. the
OpenAI-`evals`-inherited closed-QA prompt
(https://github.com/promptfoo/promptfoo/blob/ca609b7dede818493f1d9aa9b39483f6f2c7e1fb/src/prompts/grading.ts):

```ts
export const OPENAI_CLOSED_QA_PROMPT = JSON.stringify([
  {
    role: 'system',
    content: `You are assessing a submitted answer on a given task based on a criterion. Here is the data:
[BEGIN DATA]
***
[Task]: {{input}}
***
[Submission]: {{completion}}
***
[Criterion]: {{criteria}}
***
[END DATA]
Does the submission meet the criterion? First, write out in a step by step manner your reasoning about the criterion to be sure that your conclusion is correct. Avoid simply stating the correct answers at the outset. Then print only the single character "Y" or "N" (without quotes or punctuation) on its own line corresponding to the correct answer. At the end, repeat just the letter again by itself on a new line.

    Reasoning:`,
  },
]);
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 4** —
    the `not-` inversion fail-closed sentence and its asymmetry finding ("this
    fail-closed property is documented only for the inverted form, not as a
    general property of all model-graded assertions"). This page states the
    property for **both** polarities of one assert (Claim 3), so it
    corroborates the mechanism and narrows the "positive form is
    undocumented" half of the finding without contradicting it. (Verified:
    read Claim 4 and its quote in #1305.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 1** — the
    ambient, credential-selected judge. This page names no default judge
    (Claim 6), so it is a per-type instance of the same unpinned-default
    exposure. (Verified: read Claim 1 and its quote in #1305.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 2** — the
    three-level grader-override chain and the shorthand-`config` trap,
    restated here verbatim and deliberately not re-extracted as a claim
    (Claim 6). (Verified: read Claim 2 in #1305.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claims 5 and 6** —
    the cross-family scratchpad-misparse surface and the vLLM
    unfinished-`thinking` caveat. Claim 5 above is the structural inverse on
    one assert type: because the default closedqa prompt puts the verdict
    last by instruction, leading reasoning is expected rather than
    misparsed — while the trailing-text fragility in Claim 2 is the same
    class of hazard the family has elsewhere. (Verified: read Claims 5-6 in
    #1305.)
  - `source-notes/docs-promptfoo-llm-rubric.md` (#1471) **Claim 7** — the
    `not-` fail-closed sentence for `llm-rubric`, and its explicit finding
    that "no page documents the positive form". Claim 3 here is the
    positive-form instance that note's open question asked for, recorded as a
    fourth per-assert instance rather than as a family law — the same
    restraint that note applied. (Verified: read Claim 7 and its assessment
    in #1471.)
  - `source-notes/docs-promptfoo-llm-rubric.md` **Claim 5** — the
    per-credential default-judge roster. This page's silence on the default
    judge (Claim 6) is the discriminating data point for open contradiction
    #1352: a per-type page that enumerates the roster versus one that says
    nothing. (Verified: read Claim 5 in #1471.)
  - `source-notes/docs-promptfoo-g-eval.md` (#1349) **Claim 5** — the
    symmetric fail-closed inversion for `not-g-eval`, with the same "reported
    as failures in both directions" wording this page restates in its own
    terms. (Verified: read Claim 5 and its quote in #1349.)
  - `source-notes/docs-promptfoo-factuality.md` (#1348) **Claim 5** — the
    `{{input}}` / `{{ideal}}` / `{{completion}}` variable set and its
    "satisfies the reader but not the parser" failure mode. Claim 4 here is
    the third set in that series, and the same footgun: a ported
    `rubricPrompt` binds nothing, and this page additionally documents no
    accepted-output-format list, so the mis-port is silent. (Verified: read
    Claim 5 and its quotes in #1348.)
  - `source-notes/docs-promptfoo-factuality.md` **Claim 4** — the factuality
    page's default-grader silence and its placement on the ambient side of
    #1352. This page has the same silence, which makes the silence a pattern
    (two per-type pages) rather than an omission. (Verified: read Claim 4 in
    #1348.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) **Claim 1** —
    "the final score of the test case is calculated as the weighted average
    of the scores of all assertions" and the `threshold` pass rule. This is
    the tier that gives a 1/0 closedqa score its gate semantics (Claim 7),
    and **Claim 3** — "`threshold: 0` makes the test case pass regardless of
    individual assertion failures" — is the same tier's silent-green config,
    one level above the assert. (Verified: read Claims 1 and 3 and their
    quotes in #1287.)

- **Contradicts**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 8** —
    the vendor's portability sentence, quoted in that note: "This approach
    works with `llm-rubric`, `g-eval`, and `model-graded-closedqa`." The
    "approach" Claim 8 documents is a `defaultTest.options.rubricPrompt`
    whose bodies are `Ausgabe: {{ output }}` / `Kriterium: {{ rubric }}` and
    whose system message instructs a JSON verdict
    (`{"reason": …, "pass": …, "score": …}`). This page's parse contract
    (Claim 1) and variable set (Claim 4) cannot both accommodate that
    recipe: a JSON verdict does not end in `Y`, so on this assert it is a
    malformed response that fails at score 0, and the two template variables
    the recipe reads are not in the closedqa context. **Filed as
    contradiction #1486** (with the implementation evidence in its body) per
    MINER.md §4a. No verdict is picked here — #1305 Claim 8 is currently
    load-bearing for the guide's multilingual-rubric rule, so the resolver
    should decide whether the correct resolution is "the hub sentence is
    wrong about `model-graded-closedqa`" (a note correction plus possibly an
    upstream docs report) or something subtler.
  - `source-notes/docs-promptfoo-llm-rubric.md` (#1471) — its Extraction
    Notes quote the same portability sentence as it appears on the
    `llm-rubric` page ("Note: Option 1 works with llm-rubric, g-eval, and
    model-graded-closedqa." — quoted as transcribed in that note), so
    #1486's Side A has two page instances, not one. Noted for the resolver;
    same issue, no separate filing.
  - Open contradiction **#1352** (per-type pinned default judge vs the
    family-wide ambient-credential claim, #1305 Claim 1 vs g-eval's
    `gpt-4.1-2025-04-14` pin): this page names no default judge at all
    (Claim 6), so it sits on the *ambient* side — the same side as the
    factuality page (#1348 Claim 4) and opposite the g-eval page. Recorded
    for #1352's resolver as a third data point; **not** filed as a new
    contradiction (it is a silence, not an opposing claim, and MINER.md §4a
    excludes "one side is so weakly supported it doesn't rise to a real
    claim"), and no verdict is picked here.
  - Duplicate check for this filing: `gh issue list --label contradiction`
    returns eight open issues (#1462, #1461, #1408, #1352, #1338, #1322,
    #1307, #1150) and none closed. #1352 and #1307 are the promptfoo-scoped
    ones and cover different subjects (judge pin; missing-trace semantics), so
    neither duplicates #1486. `CONTRADICTIONS.md` carries no `C-NNN` entries
    yet.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — closes
    the "model-graded-closedqa … NOT followed" gap that note's Extraction
    Notes records, for the deltas above. The shared material (the
    grader-override surface, the `value`-as-criterion contract, the
    multilingual `rubricPrompt` guide) is cited above rather than
    re-extracted, per the note's own "what was not extracted" list.
  - `source-notes/docs-promptfoo-g-eval.md` (#1349) **Claim 3** — g-eval's
    non-zero default `threshold: 0.7` is the documented counter-case to the
    "model-graded asserts don't gate by default" generalization, and
    `model-graded-closedqa` is now a second instance of the *opposite* shape:
    no `threshold` on the page at all, because the assert is binary rather
    than scored. The per-type threshold picture therefore now spans "not
    documented" (closedqa), "documented as 0" (context-faithfulness Claim 2
    below), and "documented as 0.7" (g-eval) — and each page must be read on
    its own. (Verified: read Claim 3 and its quotes in #1349.)
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md`
    (#1320) **Claim 2** — `threshold` documented as "(default: 0)", i.e. a
    score-blind default pass. closedqa reaches the same "bare assert may not
    gate" neighborhood by a different route (no score to threshold, gating
    happens at the row level instead), which is a second illustration of
    that note's per-page-reading rule. (Verified: read Claim 2 and its quote
    in #1320.)
  - `source-notes/docs-promptfoo-max-score.md` (#1472) **Claim 5** — the
    vendor's `select-best` comparison table's objective-vs-judged split and
    the "no threshold at all" edge. Useful here only as a reminder that
    "no threshold" is not unique to closedqa; the mechanism (a binary assert
    score entering the aggregate) is #1287's, not max-score's. (Verified:
    read Claim 5's heading and content in #1472.)

- **Novel**:
  1. **A string-suffix parse as the gate contract** — "The assertion passes
     if the response ends with 'Y' and fails if it ends with 'N'" (Claim 1).
     Every other model-graded assert in the corpus is score-gated
     (`g-eval` 0.7, `llm-rubric` pass-field, `context-*` threshold 0,
     `factuality` per-category grades) or letter/JSON-parsed
     (`factuality` A–E). This is the family's first *trailing-character*
     parse, and the first whose correctness depends on the judge emitting
     nothing after its verdict.
  2. **The "malformed response" fail clause, for both polarities** (Claim 2)
     — new wording relative to the three transport/parse-failure sentences
     already in the corpus, and a distinct failure class: a *correct* grade
     recorded as a failing assertion because of a trailing character.
  3. **Positive-form fail-closed, documented** (Claim 3) — the fourth
     instance, and the first that covers the un-inverted assert; the
     fail-closed-but-score-0 framing (fail-closed, not fail-loud) is new
     too.
  4. **A third `rubricPrompt` variable set** — `{{input}}` / `{{criteria}}` /
     `{{completion}}` (Claim 4) — which falsifies the hub's uniform-swap
     claim for this assert and is filed as contradiction #1486.
  5. **OpenAI-`evals` provenance for a second judge prompt** (Claim 5) —
     after `fact.yaml` (#1348 Claim 1) — plus the structural finding that
     this parse is the one family surface where leading reasoning is
     expected rather than misparsed, and the "repeat the letter at the end"
     instruction that the parse contract depends on.
  6. **A per-type page with a documented override surface and no documented
     default judge** (Claim 6) — a third data point for #1352, and a
     documentation gap distinct from g-eval's pin (Claim 2 there) and
     `llm-rubric`'s roster (Claim 5 there).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — extend the gate-review checklist with
  the parse contract and its trailing-text failure mode.** For any
  `model-graded-closedqa` assert: (a) the verdict is a trailing-character
  test, so a custom `rubricPrompt` must state its output format as part of
  the gate (Claim 2), and a judge that appends anything after the letter
  turns passing cases red with a reason string that reads like a model
  disagreement; (b) the assert is binary with no `threshold` of its own, so
  the row-level `threshold` is doing the gating (Claim 7) — audit it with the
  same suspicion as #1287's `threshold: 0`; (c) treat the score as
  uninformative about the output: a score-0 row may be a grader error rather
  than a model failure, and the discrimination lives in assertion metadata,
  not the pass column (Claim 3). Add the per-assert `rubricPrompt` variable
  table to the checklist, now covering three sets — `{{output}}`/`{{rubric}}`
  (rubric family), `{{input}}`/`{{ideal}}`/`{{completion}}` (factuality),
  `{{input}}`/`{{criteria}}`/`{{completion}}` (closedqa) — with the rule
  "grep the variable names; the fact that the `rubricPrompt` slot is shared
  across assert types is not license to port a prompt by rename" (Claim 4,
  and see contradiction #1486, whose resolution is pending).
- **Chapter 05 — the "fail-closed" rule, restated per assert type.** The
  guide should now say: fail-closed on grader error is documented for both
  polarities of `model-graded-closedqa`, for the inverted forms of
  `g-eval` / `llm-rubric` / `trajectory:goal-success`, and *not* documented
  for the positive forms of the latter two — with the wording difference
  called out (transport/parse failure "reported as a failure" vs "fail …
  with score `0`"), because the second says the failure is a score, not an
  error class. That distinction is the operational content: a gate that is
  fail-closed but not fail-loud still needs the metadata check to separate
  infra-red from model-red (#1305's Contract).
- **Chapter 06 (Security and Trust) — refusal-style gates built on
  `not-model-graded-closedqa`.** The hub note's Concrete Artifacts use
  `type: model-graded-closedqa` with `value: Is not apologetic` — a
  positive-form safety-flavored gate. Two updates: that shape is now
  documented fail-closed on grader failure (so a broken judge cannot silently
  pass a "must not apologize" gate), and the same property holds for the
  `not-` form if the polarity is inverted. Also record that this judge's
  rubric is inherited from OpenAI's public evals rather than written by
  promptfoo (Claim 5), which matters for a security review: the criteria
  text a team believes it wrote may be a paraphrase of a prompt maintained
  elsewhere.
- **Chapter 05 / Ch03 (conditional) — "how many criteria can a closed-QA gate
  afford".** If a gate is built from N closedqa asserts, budget N judge
  verdicts per test case, each an unpinned judge call unless `provider:` is
  set (Claims 1 and 6). That is the cheapest way to make the cost and the
  judge surface of a criteria checklist explicit.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/model-graded-closedqa);
  the rendered text and all six code blocks were extracted from the raw HTML
  so that YAML indentation, the blank line inside the `rubricPrompt` block,
  and the inline-code spans survive verbatim. Footer reads "Last updated on
  **Sep 27, 2026** by **mldangelo-oai**" — page undated, so `date_published`
  carries the last-updated date (same convention as the sibling notes
  #1287/#1289/#1305/#1348/#1471). Every `Quote:` above was checked against
  the fetched text; code blocks copied verbatim.
- **Sub-pages followed: none, deliberately.** The page's only outbound link
  is "Further reading → model-graded metrics", which is the hub page already
  mined at #1305; the nav's sibling links are the per-type family, each its
  own source by corpus convention (#1305's own Extraction Notes enumerated
  them as separate surfaces, and three of them are now mined). MINER.md §1's
  "follow up to 5 linked pages" was applied and none qualified: the sibling
  pages were read as *notes* (not re-fetched) for the cross-reference work
  below.
- **Implementation verification (not the documented source).** Because this
  page's load-bearing claim is a parse contract, I checked the vendor's
  published implementation at `main` @ `ca609b7` rather than inferring
  behavior. Five files were read (`src/matchers/llmGrading.ts`,
  `src/prompts/grading.ts`, `src/matchers/shared.ts`,
  `src/assertions/modelGradedClosedQa.ts`, `src/matchers/rubric.ts`, plus
  the `getNunjucksEngine` signature in `src/util/templates.ts`); the
  excerpts and permalinks are in Concrete Artifacts, clearly separated from
  the page's own artifacts. This supports Claims 2–5 and is the evidence
  body of contradiction #1486. Caveat stated for the Assayer: this is
  `main`-branch code read on 2026-09-27, not a released-version check, and
  no CLI was run — a `npx promptfoo@<pinned>` run on a two-assert config
  (one with a hub-style JSON `rubricPrompt`, one with the page's own) would
  be the independent confirmation, and the guide should not present the
  implementation excerpts as vendor *documentation*.
- **Triage key-question resolutions.** (1) *`rubricPrompt` variable
  divergence* — confirmed, with a documented variable list and the full
  example extracted as a Concrete Artifact; filed as contradiction **#1486**,
  no verdict in this note. (2) *Positive-form fail-closed* — extracted as
  Claim 3, recorded as a fourth per-assert instance and an update to #1471
  Claim 7's "not family-level" answer, **not** as a family law; the
  score-0-vs-reported-as-error distinction is stated in the claim and
  carried into Guide Impact. (3) *Provenance* — extracted as Claim 5 (the
  page names the upstream twice); the default prompt's
  repeat-the-letter-at-the-end instruction is implementation evidence and is
  labeled as such. (4) *No default judge documented* — recorded under
  `**Contradicts:**` for #1352's resolver without a verdict, per the
  triage's instruction.
- **Scope discipline.** Deliberately **not** extracted as claims because
  #1305 and the sibling per-type notes already hold them verbatim: the
  three-level grader-override surface and the shorthand-`config` trap (#1305
  Claim 2; #1471 Claim 10; #1348 Claim 4), the `value`-is-the-criterion
  contract, and the multilingual `rubricPrompt` guide (#1305 Claim 8 — cited
  under `**Contradicts:**` rather than re-extracted, because this page
  contests its reach for this one assert type). Also not extracted: the
  "Further reading" pointer (carries nothing) and the page's relative
  positioning in the nav.
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — each cited or dismissed
  by name):
  - `docs-promptfoo-llm-rubric.md` — **cited heavily** (Corroborates Claims
    5 and 7; the Contradicts discussion picks up its quoted restatement of
    the portability sentence).
  - `docs-promptfoo-factuality.md` — **cited** (Corroborates Claims 4 and 5).
  - `docs-promptfoo-assertions-metrics.md` — **cited** (Corroborates Claims 1
    and 3, for the row-level scoring/threshold mechanics).
  - `docs-promptfoo-classifier-grading.md` — fixed-classifier rung with a
    label-bound threshold non-portability finding; a different tier of the
    same family and no closedqa/parse content; **dismissed**.
  - `docs-litellm-batches-api.md` — LiteLLM batch rate-limit accounting;
    unrelated vendor, unrelated surface; **dismissed**.
  - `blog-promptfoo-red-team-claude.md` — per-model red-team config whose
    `llm-rubric` grader semantics are already sourced from #1305; citing it
    again here would be circular, and it carries no closedqa material;
    **dismissed** (reasoning recorded, per the #1471 precedent).
  - `blog-promptfoo-owasp-red-teaming.md` — OWASP GenAI red-teaming
    methodology and SDLC/CI integration; no judge-grading config surface;
    **dismissed**.
  - `blog-promptfoo-red-team-gemini.md` — per-model red-team plugin config
    and reasoning-DoS plugins; no eval-grader parse surface; **dismissed**.
  - `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge *alerting* for
    incident triage; no eval-assert config surface; **dismissed**.
  - `docs-google-sre-team-lifecycles.md` — Google SRE workbook chapter on
    team lifecycles; no LLM-eval content; **dismissed**.
  - Found by searching `source-notes/` beyond the candidate list and **cited**:
    `docs-promptfoo-model-graded-metrics.md` (the hub; Corroborates Claims
    1/2/4/5/6, Contradicts Claim 8, Extends),
    `docs-promptfoo-g-eval.md` (Corroborates Claim 5; Extends Claim 3),
    `docs-promptfoo-model-graded-context-faithfulness.md` (Extends Claim 2),
    `docs-promptfoo-max-score.md` (Extends Claim 5).
- **Cross-ref verification (§4b)**: every `Claim N` cited above was located in
  the cited note and its content checked against what it is cited for —
  #1305 Claims 1/2/4/5/6/8 (read in the hub note, including the Claim 8
  quote and the Extraction Notes deferral list), #1471 Claims 5/7/10 plus its
  quoted "Option 1 works with …" restatement, #1348 Claims 4/5, #1287 Claims
  1/3 (quotes read), #1349 Claims 2/3/5 (read), #1320 Claim 2 (read), #1472
  Claim 5 (read). No claim numbers invented and no quotes attributed to other
  notes. Source-note issue numbers were read from each cited note's
  frontmatter `issue:` field, not inferred.
- **Contradiction issue #1486 filed** (open, `contradiction` + `needs-
  resolution` + `no-triage`) before this PR, per MINER.md §4a, with both
  sides' sources, claims, evidence and confidence, the "why this is a
  contradiction" argument, the implementation excerpts, an explicit statement
  that the residual open question is whether the hub sentence is a docs error
  or a compatibility shim, and a `accepted-B`-leaning filer recommendation
  that leaves the verdict to the resolver. This note picks **no** verdict, per
  MINER.md §4a.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1289, #1305, #1348, #1349, #1471, #1472): the individual
  mechanism and default claims are settled-for-product-behavior and directly
  checkable, and unusually for this family most were also verified against
  the vendor's published implementation — but this is vendor documentation
  with no measured judge-agreement, gate-failure, cost, or calibration
  figures and no independent practitioner validation, and the guide-level
  readings (partial-credit weakening at the row level, the
  fail-closed-not-fail-loud distinction, the mis-port failure shape) are the
  Miner's synthesis on top of documented behavior rather than vendor
  statements.
- `registry/sources.json` and `registry/claims-index.json` were **NOT** edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
