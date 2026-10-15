---
source_url: https://www.promptfoo.dev/docs/guides/factuality-eval
source_type: docs
title: "Promptfoo Guide: Evaluating Factuality"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-15
date_extracted: 2026-10-15
last_checked: 2026-10-15
status: current
confidence_overall: emerging
issue: "#1726"
---

# Promptfoo Guide: Evaluating Factuality

> The *guide* surface for promptfoo's `factuality` assert — the sibling of the
> per-type configuration reference (#1348), on a different URL
> (`/docs/guides/factuality-eval`). Where the reference page documents the
> gate mechanics and this page restates the same five-category taxonomy and
> permissive default pass-set, the guide page adds what the reference page
> lacks and what matters most for calibration: (1) a first-party
> **default-grader statement** — "By default, promptfoo uses `gpt-5` for
> grading" — which is in tension with the sibling reference page's silence on a
> default judge (#1348 Claim 4) and joins the open contradiction **#1352** as a
> third data point; (2) a reproducible **TruthfulQA quick-start** recipe and a
> `file://...:generate_tests` **external dataset-loader** authoring path; (3)
> the vendor's own **reference-answer authoring criteria** (clarity, precision,
> verifiability, completeness) and **scoring-weight hardening guidance**; and
> (4) an explicit **binary score→pass mapping** that spells out, for the first
> time in the corpus, the 1→pass / 0→fail reading #1348 could only infer.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo *guide* page
  `/docs/guides/factuality-eval`, distinct from the already-mined per-type
  reference page `/docs/configuration/expected-outputs/model-graded/factuality/`
  in #1348)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `factuality` assert behavior — authoritative for *what promptfoo
  does* with a given config (the taxonomy, the default pass-set, the
  default-grader claim, the override forms, the rubric contract), but
  vendor-positioned: the page carries no measured judge-agreement, pass-rate,
  or calibration figures, and its motivating statistics are unsourced
  illustrative framing (see Extraction Notes). Everything below is checkable
  against an installed CLI.
- **Scope**: A guide-style page (What is factuality / Quick Start / How it
  works + Key terminology / Creating a basic evaluation / Comparing Multiple
  Models / Evaluating On External Datasets / Crafting Effective Reference
  Answers / Customizing the Evaluation / Response Formats / Best Practices /
  See Also). It restates the five-category taxonomy and default pass-set the
  reference page (#1348) already documents in full — this note extracts only the
  **delta** (default-grader claim, TruthfulQA recipe, external dataset loader,
  reference-authoring criteria, explicit binary scoring, best-practices list),
  not a re-extraction of the taxonomy. It does NOT cover the per-type reference
  page (#1348, a separate source), the model-graded hub (#1305), the g-eval
  per-type page (#1349), the context-faithfulness sibling (#1320), or the
  assertions hub (#1287).
- **Last updated**: the page footer reads "Last updated on Oct 15, 2026 by
  renovate[bot]" (a dependency-bump edit) — current well after the Dec 2025
  cutoff, and matching the extraction date.

## Extracted Claims

### Claim 1: The page states a concrete default grading model — "By default, promptfoo uses `gpt-5` for grading" — the first promptfoo surface in the corpus to name a default judge for `factuality`, and a claim that sits in direct tension with the sibling reference page's silence on a default judge (#1348 Claim 4) and with the model-graded hub's family-wide ambient-judge claim (#1305 Claim 1)
- **Evidence**: The "Selecting the Grading Provider" subsection's opening
  sentence, followed by the three override forms (global `defaultTest`,
  per-assertion `provider:`, CLI `--grader`) — none of which contradicts the
  default sentence.
- **Confidence**: settled for the page text (documented product behavior); the
  consequence for the corpus contradiction is unresolved (see Cross-References —
  joins open **#1352**)
- **Quote**: "By default, promptfoo uses `gpt-5` for grading. To specify a different grading model:"
- **Our assessment**: This is the triage's key question answered verbatim from
  the vendor: on the *guide* surface for the factuality assert, the default
  grading model is `gpt-5`, not "whatever credentials are present." That mapping
  is stated as a default model *family*, not a dated pin (unlike g-eval's
  `gpt-4.1-2025-04-14` in #1349 Claim 2), and the page never reconciles it with
  the hub's ambient-credential mechanism (#1305 Claim 1). Two readings are both
  consistent with the text: `gpt-5` is the unconditioned default, or `gpt-5` is
  the *OpenAI-credential branch* of the ambient selection (the reconciliation
  #1352 asks for). This page cannot settle that; it widens #1352 with a
  factuality-surface data point that names a default where the factuality
  reference page names none. For the guide, the safe rule is unchanged: pin the
  grader explicitly (`provider:` / `--grader` / `defaultTest.options.provider`)
  and do not assume the default is stable across surfaces.

### Claim 2: The page's default scoring is explicitly binary and its pass semantics are spelled out — A/B/C/E score `1.0` (pass), D scores `0.0` (fail), and "A score of 0 means fail, while any positive score is considered passing" — which states the 1→pass / 0→fail mapping that the reference page (#1348 Claim 2) only let the Miner infer
- **Evidence**: The "Understanding the default scoring weights" subsection: the
  two bullets assigning the category scores and the closing pass-semantics
  sentence.
- **Confidence**: settled (documented product behavior)
- **Quote**: "By default, promptfoo uses a simple binary scoring system:" and "Categories A, B, C, and E are assigned a score of 1.0 (pass)" and "Category D (disagree) is assigned a score of 0.0 (fail)" and "A score of 0 means fail, while any positive score is considered passing. The score values can be used for ranking and comparing model outputs."
- **Our assessment**: High-value confirmation: #1348 Claim 2 explicitly flagged
  that "this page never spells [the 1→pass / 0→fail mapping] out" and that the
  mapping was the Miner's synthesis. This guide page supplies the vendor
  sentence that confirms it, and adds the stronger rule — *any positive score
  passes*, so a fractional customization (`0.8`, `0.7`) is still a pass, not a
  soft-fail. That matters for teams reading the worked example below: lowering
  `superset` to `0.8` does not make superset answers "usually fail"; it makes
  them pass with a lower *ranking* score. Only a `0.0` grade (or an explicit
  `threshold`/aggregation elsewhere) actually flips pass/fail.

### Claim 3: The page gives explicit scoring-weight hardening direction — lower `superset` if you fear models adding incorrect information, lower `differButFactual` if wording precision matters, lower `subset` if comprehensive answers are required — the vendor's own prescriptive confirmation that the per-category grade override (#1348 Claim 3) is the tightening lever
- **Evidence**: The "When to use custom weights:" bullets under the scoring
  example.
- **Confidence**: settled (documented product behavior / vendor guidance)
- **Quote**: "Decrease `superset` if you're concerned about models adding potentially incorrect information" and "Reduce `differButFactual` if precision in wording is important for your application" and "Adjust `subset` downward if comprehensive answers are required"
- **Our assessment**: This is the vendor telling operators to do exactly what
  #1348 Claim 3 recommended as the gate-tightening review: turn the permissive
  default pass-set into an explicit, application-specific one. It also names the
  three risk axes in plain terms — fabrication risk (`superset`), wording
  precision (`differButFactual`), and completeness (`subset`) — which is a
  ready-made review checklist for Ch05. Note this is *customization guidance*,
  not a default-value claim: the worked example's `0.8`/`0.7` are a
  customization choice, not the shipped defaults (which Claim 2 restates as
  1/1/1/0/1).

### Claim 4: Factuality cases can be authored programmatically through a JavaScript/TypeScript dataset loader referenced as `tests: file://your_dataset_loader.ts:generate_tests` — a third reference-answer supply path beyond the single-`value` assert and the CSV `factuality:` prefix (#1348 Claim 6)
- **Evidence**: The "Creating Your Own Dataset Integration" subsection's three
  numbered steps ("Create a dataset loader" / "Add factuality assertions" /
  "Reference in your config") and its one-line YAML.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Create a dataset loader: Use JavaScript/TypeScript to fetch and format your dataset" and "Add factuality assertions: Include a factuality assertion in each test case" and "`tests: file://your_dataset_loader.ts:generate_tests`"
- **Our assessment**: The loader hook is how factuality cases become
  *generated* rather than hand-authored — a scaling path the reference page's
  CSV route (#1348 Claim 6) does not offer. The consequence for the guide is a
  supply-chain one: if the reference answers are produced by a script, the
  ground truth's provenance is the script *and* its upstream dataset, so a
  loader that silently changes its upstream (or that maps the wrong label)
  changes what the gate tests with no diff to the promptfoo config. The actual
  TruthfulQA example (Concrete Artifacts) demonstrates this precisely: the
  loader picks the reference as `choices[label]` from a `label` index.

### Claim 5: The guide ships a reproducible end-to-end reference recipe — `npx promptfoo@latest init --example huggingface/dataset-factuality` → `cd` → `npx promptfoo eval` → `npx promptfoo view` — which runs factuality tests against the TruthfulQA dataset with built-in assertions and no hand-authored cases
- **Evidence**: The "Quick Start: Try it today" section's four-command bash
  block and the "What these commands do" and "This example:" bullets.
- **Confidence**: settled (documented product behavior; the example is a linked
  GitHub template)
- **Quote**: "The fastest way to get started with factuality evaluation is to use our pre-built TruthfulQA example:" and "Fetches the TruthfulQA dataset (designed to test model truthfulness)" and "Creates test cases with built-in factuality assertions"
- **Our assessment**: This is the corpus's first *runnable* factuality recipe —
  a concrete "start here" the guide can point readers at instead of describing
  the taxonomy abstractly. It is also the strongest confirmation that promptfoo
  treats reference-based factuality as a first-class quick-start, not a niche
  config. The recipe's reference answers come from TruthfulQA's `label` index
  (see Concrete Artifacts), so it is a *benchmark-anchored* gate, not a
  production-corpus gate — useful for smoke-testing the harness, not for
  validating a specific product's claims.

### Claim 6: The page defines first-party reference-answer authoring criteria — clarity (state the fact directly), precision (no extraneous detail), verifiability (authoritative sources), completeness (all essential parts) — with healthy and unhealthy examples for each
- **Evidence**: The "What makes a good reference answer?" subsection's four
  numbered criteria, each with Good/Avoid examples.
- **Confidence**: settled (vendor guidance)
- **Quote**: "Clarity: State the fact directly and unambiguously" and "Precision: Include necessary details without extraneous information" and "Verifiability: Ensure your reference is backed by authoritative sources" and "Completeness: Include all essential parts of the answer"
- **Our assessment**: This is the prescriptive operational content the
  reference page (#1348) lacks: it tells an operator how to write the ground
  truth the gate grades against. It is genuinely useful for Ch05's
  gate-review checklist because reference quality is the *unmovable* input to a
  factuality gate — if the reference is vague or subjective, the judge's verdict
  is meaningless no matter how well the grader is pinned. The criteria also
  reveal the gate's scope limit: it can only test facts a human can state
  plainly and cite.

### Claim 7: The page lists four reference-answer pitfalls — subjective statements, temporally dependent facts, ambiguous wording, unnecessary complexity — i.e. the reference-answer failure modes that make a factuality gate undecidable rather than wrong
- **Evidence**: The "Common pitfalls to avoid" subsection's four numbered
  items.
- **Confidence**: settled (vendor guidance)
- **Quote**: "Subjective statements: Avoid opinions or judgments in reference answers" and "Temporally dependent facts: Be careful with time-sensitive information" and "Ambiguous wording: Ensure there's only one way to interpret the statement" and "Unnecessary complexity: Keep references simple enough for clear evaluation"
- **Our assessment**: The "temporally dependent facts" pitfall is the
  operational link to the corpus's staleness theme: a reference answer that was
  true last quarter can silently invert a factuality gate, and the eval
  *passes the run* while testing a now-false ground truth. Combined with
  Claim 6, this is a compact "reference hygiene" rule for the guide: the
  reference set is a maintained asset, not a one-time CSV.

### Claim 8: The page's Best Practices list gives five setup rules — choose references carefully, test multiple providers, customize scoring weights, use a strong grader, validate with known examples — with the "strong grader" rule stated as a general expectation ("More capable models generally provide more reliable factuality assessments")
- **Evidence**: The closing "Best Practices" numbered list.
- **Confidence**: settled (vendor guidance)
- **Quote**: "Consider multiple providers: Different models may excel at different types of factual knowledge" and "Use a strong grader: More capable models generally provide more reliable factuality assessments" and "Test with known examples: Validate your setup with questions where you know the correct answers"
- **Our assessment**: "Test with known examples" is the vendor's own statement
  of the negative/known-answer control the corpus's gate-review rules require
  (#1348 Guide Impact item (b)): prove the gate discriminates before trusting
  it. "Use a strong grader" is a flat, unevidenced vendor assertion — no
  agreement data — and it interacts awkwardly with Claim 1's `gpt-5` default:
  the page tells you both that the default is already a strong grader and that
  you should choose one, without stating what "strong" means measurably.

### Claim 9: The page restates the five-category taxonomy with richer worked examples than the reference page, including the superset (B) example explicitly described as adding *accurate* information ("it adds accurate information while maintaining consistency") — framing superset as benign rather than as fabrication risk
- **Evidence**: The "Key terminology explained" five categories each with an
  italic example; the B example is the notable one.
- **Confidence**: settled (documented product behavior)
- **Quote**: "B: Output is a superset of the reference and is fully consistent with it" and "Example: If the reference is \"Paris is the capital of France,\" a superset would be \"Paris is the capital of France and home to the Eiffel Tower\" — it adds accurate information while maintaining consistency"
- **Our assessment**: The example is the vendor's own illustration of why B is
  a *passing* grade: when the addition is accurate, a superset is not a defect.
  But the judge does not verify the addition against the world — it judges only
  consistency with the reference — so the same category also admits a *fabricated*
  addition (the reference page's #1348 Claim 2 hazard). The guide page's benign
  example and the reference page's risk framing are complementary, not
  contradictory: the category is safe when extras are accurate and unsafe when
  they are invented, and only the operator (via the `superset` weight, Claim 3)
  can choose which stance the gate takes.

### Claim 10: The page documents the same family grader-override surface with the same three forms (global `defaultTest.options.provider`, per-assertion `provider:`, CLI `--grader`) but, unlike the reference page, pairs it with the `gpt-5` default claim
- **Evidence**: The "Selecting the Grading Provider" subsection's three code
  blocks.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can also override it per assertion:" and "Or via the command line:" with the verbatim forms `provider: openai:gpt-5`, `provider: anthropic:claude-sonnet-5`, and `promptfoo eval --grader openai:gpt-5`
- **Our assessment**: The override mechanics corroborate #1348 Claim 4's
  override surface, and the CLI/global/assertion precedence matches the hub's
  precedence model (#1305 Claim 2). The delta is context: on the reference page
  the same surface sits beside silence about the default; here it sits beside an
  affirmative default (Claim 1). For the guide, this is the concrete pinning
  recipe to cite on the factuality gate: set `provider:` on the assert (or
  `defaultTest.options.provider`) rather than trusting the ambient/`gpt-5`
  default.

### Claim 11: The page restates the `rubricPrompt` contract for factuality — the prompt must implement `{{input}}`, `{{ideal}}`, and `{{completion}}`, and the checker accepts two response formats, JSON (`{"category": "LETTER", "reason": "..."}`, primary/recommended) or a single-letter legacy form — consistent with the reference page's parse contract
- **Evidence**: The "Customizing the Evaluation Prompt" subsection's template
  bullets and the "Response Formats" section's two items.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You must implement the following template variables:" and "`{{input}}`: The original prompt/question" and "`{{ideal}}`: The reference answer (from the `value` field)" and "`{{completion}}`: The LLM's actual response (provided automatically by promptfoo)" and "The factuality checker supports two response formats:" and "JSON format (primary and recommended):" and "Single Letter (legacy format):"
- **Our assessment**: Corroborates #1348 Claim 5 (family-specific template
  variables + letter-or-JSON parse) and the hub's "assertion-specific prompts"
  constraint (#1305 Claim 8) — a custom rubric copied from `llm-rubric`
  (`{{output}}`/`{{rubric}}`) binds nothing here. The guide page's "JSON format
  (primary and recommended)" framing is a mild strengthening of the reference
  page, which presents the two formats more neutrally. The silent-gate hazard
  noted in #1348 Claim 5 (unparseable custom rubric has no documented failure
  behavior) still applies, since this page states no failure behavior either.

### Claim 12: The page frames factuality eval primarily as a *model-comparison* tool — "especially useful for comparing how different models perform on the same facts" — with a four-provider worked config that runs the same reference cases against `gpt-5-mini`, `gpt-5`, `claude-sonnet-5`, and `gemini-2.5-flash`
- **Evidence**: The "Comparing Multiple Models" section's intro sentence and
  its four-provider `promptfooconfig.yaml`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Factuality evaluation is especially useful for comparing how different models perform on the same facts:"
- **Our assessment**: This is the page's most SRE-relevant framing: factuality
  as a *model-selection* measurement, not only a release gate. The same
  reference set becomes a benchmark across candidates, which is exactly the
  "which model should we ship" decision the MVP's model-routing work
  (`docs/MODEL-ROUTING.md`) makes recurringly. The catch is that the comparison
  is only as valid as the reference set and the judge's stability across the
  compared runs — both of which Claims 1/6/7 put under pressure.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/guides/factuality-eval (sections as noted),
except the coding-platform example, which is copied from the page's linked
TruthfulQA GitHub example (attributed per sub-section).

### Quick-start TruthfulQA recipe (verbatim from "Quick Start: Try it today")

```bash
# Initialize the example - this command creates a new directory with all necessary files
npx promptfoo@latest init --example huggingface/dataset-factuality

# Change into the newly created directory
cd huggingface/dataset-factuality

# Run the evaluation - this executes the factuality tests using the models specified in the config
npx promptfoo eval

# View the results in an interactive web interface
npx promptfoo view
```

### Basic factuality config (verbatim from "Creating a basic factuality evaluation")

```yaml
providers:
  - openai:gpt-5-mini
prompts:
  - |
    Please answer the following question accurately:
    Question: What is the capital of {{location}}?
tests:
  - vars:
      location: California
    assert:
      - type: factuality
        value: The capital of California is Sacramento
```

### Multi-model comparison config (verbatim from "Comparing Multiple Models")

```yaml
providers:
  - openai:gpt-5-mini
  - openai:gpt-5
  - anthropic:claude-sonnet-5
  - google:gemini-2.5-flash
prompts:
  - |
    Question: What is the capital of {{location}}?
    Please answer accurately.
tests:
  - vars:
      location: California
    assert:
      - type: factuality
        value: The capital of California is Sacramento
  - vars:
      location: New York
    assert:
      - type: factuality
        value: Albany is the capital of New York
```

### External dataset loader reference (verbatim from "Creating Your Own Dataset Integration")

```yaml
tests: file://your_dataset_loader.ts:generate_tests
```

### Reference-answer criteria (verbatim from "What makes a good reference answer?")

```text
Clarity: State the fact directly and unambiguously
  Good: "The capital of France is Paris."
  Avoid: "As everyone knows, the beautiful city of Paris serves as the capital of the magnificent country of France."
Precision: Include necessary details without extraneous information
  Good: "Water freezes at 0 degrees Celsius at standard atmospheric pressure."
  Avoid: "Water, H2O, freezes at 0 degrees Celsius, which is also 32 degrees Fahrenheit, creating ice that floats."
Verifiability: Ensure your reference is backed by authoritative sources
  Good: "According to the World Health Organization, the COVID-19 pandemic was declared on March 11, 2020."
  Avoid: "The COVID pandemic started sometime in early 2020."
Completeness: Include all essential parts of the answer
  Good: "The three branches of the U.S. federal government are executive, legislative, and judicial."
  Avoid: "The U.S. government has three branches."
```

### Grader override forms (verbatim from "Selecting the Grading Provider")

```yaml
defaultTest:
  options:
    # Set the provider for grading factuality
    provider: openai:gpt-5
```

```yaml
assert:
  - type: factuality
    value: The capital of California is Sacramento
    provider: anthropic:claude-sonnet-5
```

```bash
promptfoo eval --grader openai:gpt-5
```

### Custom scoring weights example (verbatim from "Customizing Scoring Weights")

```yaml
defaultTest:
  options:
    factuality:
      subset: 1.0 # Category A: Output is a subset of reference
      superset: 0.8 # Category B: Output is a superset of reference
      agree: 1.0 # Category C: Output contains all the same details
      disagree: 0.0 # Category D: Output and reference disagree
      differButFactual: 0.7 # Category E: Differences don't affect factuality
```

### Custom rubric prompt (verbatim from "Customizing the Evaluation Prompt")

```yaml
defaultTest:
  options:
    rubricPrompt: |
      You are an expert factuality evaluator. Compare these two answers:

      Question: {{input}}
      Reference answer: {{ideal}}
      Submitted answer: {{completion}}

      Determine if the submitted answer is factually consistent with the reference answer.
      Choose one option:
      A: Submitted answer is a subset of reference (fully consistent)
      B: Submitted answer is a superset of reference (fully consistent)
      C: Submitted answer contains same details as reference
      D: Submitted answer disagrees with reference
      E: Answers differ but differences don't affect factuality

      Respond with JSON: {"category": "LETTER", "reason": "explanation"}
```

### Accepted response formats (verbatim from "Response Formats")

JSON format (primary and recommended):

```json
{
  "category": "A",
  "reason": "The submitted answer is a subset of the expert answer and is fully consistent with it."
}
```

Single Letter (legacy format):

```text
(A) The submitted answer is a subset of the expert answer and is fully consistent with it.
```

### TruthfulQA example `promptfooconfig.yaml` (verbatim from the linked GitHub example, `promptfoo/promptfoo/examples/huggingface/dataset-factuality/promptfooconfig.yaml`)

```yaml
description: 'TruthfulQA Factuality Evaluation'

prompts:
  - |
    Please answer the following question accurately and truthfully.

    Question: {{question}}

    Answer:

providers:
  - anthropic:messages:claude-sonnet-5
  # Uncomment to add more providers
  # - bedrock:us.meta.llama3-2-1b-instruct-v1:0
  # - openai:gpt-4.1-mini
  # - google:gemini-2.5-flash

defaultTest:
  options:
    # Uncomment one to change the grading provider.
    # provider: anthropic:messages:claude-sonnet-5
    # provider: bedrock:us.meta.llama3-2-1b-instruct-v1:0
    # provider: openai:gpt-4.1-mini
    # provider: google:gemini-2.5-flash

    # Optional: Custom scoring weights for different factuality categories
    factuality:
      # Scoring weights for different factuality categories
      subset: 1.0 # Score for category A (subset of correct answer)
      superset: 0.8 # Score for category B (superset of correct answer)
      agree: 1.0 # Score for category C (same details as correct answer)
      disagree: 0.0 # Score for category D (disagreement with correct answer)
      differButFactual: 0.7 # Score for category E (differences don't affect factuality)

# Grabs TruthfulQA dataset from HuggingFace and formats it for promptfoo
tests:
  path: file://dataset_loader.ts:generate_tests
  config:
    dataset: EleutherAI/truthful_qa_mc
    split: validation
```

The example's `dataset_loader.ts` fetches the dataset over the HuggingFace API
and builds each case's reference from the dataset's `label` index (verbatim
excerpt): `const { question, choices, label } = item.row;` / `const correct_answer = choices[label];` /
`assert: [ { type: 'factuality', value: correct_answer } ]`. Its documented
default row cap is `maxRows = 100`.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-factuality.md` **Claim 2** (the same permissive
    default pass-set: "By default, options A, B, C, and E are considered passing
    grades, while D is considered failing") — this guide page restates the
    pass-set verbatim ("By default, categories A, B, C, and E are considered
    passing (with customizable scores), while category D (disagreement) is
    considered failing"). (Verified: #1348 Claim 2.)
  - `source-notes/docs-promptfoo-factuality.md` **Claim 3** (the per-category
    score override is "the only documented lever for making the gate stricter")
    — this page both restates the override keys and adds vendor hardening
    guidance for them (Claim 3 here). (Verified: #1348 Claim 3.)
  - `source-notes/docs-promptfoo-factuality.md` **Claim 5** (the
    `{{input}}`/`{{ideal}}`/`{{completion}}` template set and the
    letter-or-JSON parse contract) — this page restates both (Claim 11 here).
    (Verified: #1348 Claim 5.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 8**
    ("`factuality` and `context-recall` require specific output formats and need
    assertion-specific prompts") — this page's rubric section is the
    assertion-specific prompt in full, with the family-specific variables.
    (Verified: #1305 Claim 8.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (the
    model-assisted boundary naming `factuality` as inheriting "every judge-bias
    problem") — this page supplies the config-level detail under that catalogue
    row (default grader, weights, reference-authoring) for the `factuality`
    member; its Concrete Artifacts assertion-syntax table carries the
    `factuality:reference` string form this page's pages use. (Verified: #1287
    Claim 10 and the `factuality:reference` row in that note's Concrete
    Artifacts.)

- **Contradicts**: **In tension with `source-notes/docs-promptfoo-factuality.md`
  (#1348) Claim 4 — and this is a third data point for the already-filed open
  contradiction #1352, so no new contradiction issue was filed.** #1348 Claim 4
  holds that the factuality assert names no default judge, so "the default
  grader remains the ambient credential-selected one from the model-graded hub
  (#1305 Claim 1)." This guide page, on the *same assert type*, states a
  concrete default — "By default, promptfoo uses `gpt-5` for grading" (Claim 1
  here) — which opposes the ambient reading for `factuality`. It equally opposes
  `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 1** (the
  family-wide "nothing is pinned by default" claim). The divergence is about
  *scope*, not wording: the reference page is silent on a default judge; this
  guide page asserts one. Per MINER.md §4a, a contradiction on this exact fork
  is **already filed** as open **#1352** ("promptfoo g-eval default judge:
  pinned `gpt-4.1-2025-04-14` vs ambient credential-selected (model-graded
  hub)"), which pits per-type/guide pages that name a default judge against the
  hub's ambient claim. Rather than open a duplicate, this note records the new
  evidence on #1352 (see Extraction Notes) and **does not pick a verdict** — the
  guide advice genuinely forks ("always pin your model-graded judge" vs "the
  factuality default is `gpt-5`; verify the pinned default is what you want"),
  and resolution is a human/`#1352` decision. Verified: #1348 Claim 4 and #1305
  Claim 1 read directly; #1352 status open with labels `contradiction` +
  `needs-resolution`.

- **Extends**:
  - `source-notes/docs-promptfoo-factuality.md` (#1348) — the **direct sibling
    and parent surface**: this note is the guide-page delta under that
    reference-page extraction (the default-grader claim, the TruthfulQA recipe,
    the external dataset loader, reference-authoring criteria, and the explicit
    binary score→pass mapping that #1348 Claim 2 could only infer). Together the
    two notes are the factuality surface: reference page = gate mechanics,
    guide page = calibration/authoring/comparison practice.
  - `source-notes/docs-promptfoo-configuration-huggingface-datasets.md` (#1526)
    **Claim 1** (`huggingface://datasets/<owner>/<repo>` as a complete `tests:`
    source with one case per row) — this page documents a *different* external
    case-authoring path (a JS `file://...:generate_tests` loader that fetches
    and formats a dataset itself), so the corpus now has both the declarative HF
    dataset route and the programmatic loader route; the TruthfulQA example
    (Concrete Artifacts) uses the loader route against `EleutherAI/truthful_qa_mc`.
    (Verified: #1526 Claim 1.)
  - `source-notes/docs-promptfoo-evaluate-rag.md` (#1725) **Claim 7** (the
    stage-keyed metric taxonomy lists "output-based (factuality/correctness,
    answer-relevance)" alongside "context-based (context-adherence/grounding/
    faithfulness...)") — this guide page is the factuality-specific deep-dive for
    that output-based taxonomy slot, giving the reference-authoring and
    default-grader detail behind the RAG guide's catalogue row. (Verified: #1725
    Claim 7.)

- **Novel**: The taxonomy and permissive default pass-set are **not** new (they
  are #1348 Claims 1-2). What is new here:
  1. **The `gpt-5` default-grader statement** (Claim 1) — the corpus's first
     promptfoo surface to name a default judge for `factuality`, and the third
     data point on the open #1352 fork.
  2. **A reproducible TruthfulQA recipe** (Claim 5) — the first runnable
     end-to-end factuality quick-start in the corpus.
  3. **The `file://...:generate_tests` external dataset-loader authoring path**
     (Claim 4) — a programmatic reference-answer supply route distinct from the
     CSV `factuality:` prefix (#1348 Claim 6) and the declarative HF dataset
     route (#1526 Claim 1).
  4. **First-party reference-answer authoring criteria + pitfalls** (Claims 6-7)
     and a **best-practices list** (Claim 8) — practitioner-facing guidance the
     reference page lacks.
  5. **Explicit binary score→pass semantics** (Claim 2) — the vendor sentence
     confirming the 1→pass / 0→fail mapping #1348 flagged as Miner inference,
     plus the "any positive score is passing" rule that changes how a fractional
     weight like `0.8`/`0.7` should be read.
  6. **The superset-benign worked example** (Claim 9) — the vendor's own
     illustration that an *accurate* superset is a passing grade, the
     counterpoint to the reference page's superset-as-fabrication-risk framing.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md`, the gate-review checklist built up from
  #1287/#1305/#1320/#1348)**: add the **factuality calibration + reference-hygiene
  rules**: (a) *pin the grader* — the factuality default is now documented as
  `gpt-5` on the guide page (Claim 1) but is silent/unpinned on the reference
  page (#1348 Claim 4), so a gate must set `provider:`/`--grader`/
  `defaultTest.options.provider` explicitly rather than rely on either surface's
  default (Claims 1, 10); flag this as joined to open contradiction #1352, not
  resolved. (b) *Tighten the per-category grades* — the vendor explicitly names
  the lever (Claim 3): raise/lower `superset` for fabrication risk,
  `differButFactual` for wording precision, `subset` for completeness, and
  remember any positive score passes (Claim 2), so only a `0.0` grade flips the
  verdict. (c) *Treat references as a maintained asset* — apply the clarity/
  precision/verifiability/completeness criteria and the four pitfalls, especially
  "temporally dependent facts" (Claims 6-7), and validate with known-answer
  controls (Claim 8), the negative control the corpus already requires.
- **Chapter 05 — factuality as a model-selection measurement** (Claim 12): the
  four-provider worked config turns one reference set into a cross-model
  factuality comparison, which the guide can cite for the "how do we choose a
  model for a factuality-critical surface" decision (cf. `docs/MODEL-ROUTING.md`).
  Caveat it with the reference-set and judge-stability dependencies (Claims
  1/6/7): a model "wins" a factuality comparison only on that reference set and
  that judge.
- **Chapter 06 (Security and Trust) — RAG/grounding gates**: document the
  reference-based factuality gate beside the existing RAG-triad material
  (`blog-promptfoo-owasp-red-teaming.md`), noting the two supply paths for
  ground truth — a curated reference (`value`/CSV, #1348 Claim 6) and a
  *programmatic loader* whose upstream dataset and label mapping are now part of
  the gate's provenance (Claim 4). A loader that changes upstream (or maps the
  wrong label) silently changes what the gate tests.
- **Chapter 02 / methodology — reproducible recipes**: cite the TruthfulQA
  quick-start (Claim 5) as the canonical "stand up a factuality harness" recipe,
  explicitly scoped as a *benchmark-anchored smoke test* rather than a
  production-corpus gate (its references come from TruthfulQA's label index, not
  the product's claims).

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/factuality-eval); all quotes and code
  blocks verified character-for-character against the fetched rendered HTML
  (default-grader sentence, binary-scoring bullets + pass-semantics sentence,
  hardening bullets, quick-start bash block, loader line, reference criteria,
  pitfalls, best-practices list, taxonomy/example text, override forms, scoring
  and rubric YAML, response formats). The page's linked TruthfulQA example
  (`https://github.com/promptfoo/promptfoo/tree/main/examples/huggingface/dataset-factuality`)
  was followed (one substantive sub-page) and its `promptfooconfig.yaml` and
  `dataset_loader.ts` read for the Concrete Artifacts section; those two
  artifacts are attributed to the GitHub example, not the doc page. No passages
  spliced across non-adjacent sentences.
- **Recency note**: the Prospector's triage recorded the footer as "Last updated
  on Oct 14, 2026"; the page footer at extraction reads "Last updated on Oct 15,
  2026 by renovate[bot]" (`<time datetime="2026-10-15T19:02:48Z">`). Recorded as
  Oct 15, 2026 (`last_checked` date).
- **Illustrative statistics deliberately not extracted as evidence** (per the
  triage's caution): the page's motivating figures — a support chatbot
  "fabricates non-existent troubleshooting steps 15% of the time" and a model
  with "30% better factual accuracy for technical documentation" — are
  illustrative and unsourced (no dataset, sample, or citation). They appear in
  the "What is factuality and why is it important?" section as rhetorical
  framing and are not treated as claims.
- **Doc-vs-example discrepancy recorded**: the doc page shows
  `tests: file://your_dataset_loader.ts:generate_tests` (Claim 4 artifact),
  while the linked TruthfulQA example actually uses `tests: path: file://dataset_loader.ts:generate_tests`
  with a `config: {dataset, split}` block (Concrete Artifacts). Both are quoted
  verbatim from their respective sources; the difference (`file://` directly vs
  `path:` + `config:`) is noted rather than smoothed over.
- **Confidence rationale**: `confidence_overall` is `emerging`, matching the
  sibling promptfoo notes (#1305, #1320, #1348, #1349): the individual claims
  (default grader, binary scoring, hardening guidance, loader path, authoring
  criteria, override/rubric contracts) are settled-for-product-behavior and
  directly checkable against an installed CLI, but this is vendor documentation
  with no measured judge-agreement or pass/failure-rate figures, and the
  operational framing (reference hygiene, comparison validity, contradiction
  join) is the Miner's synthesis on documented behavior. The default-grader
  claim (Claim 1) is settled as *page text* but its reconciliation with the
  hub's ambient mechanism is explicitly left unresolved under #1352.
- **Contradiction handling (§4a)**: this page's `gpt-5` default-grader statement
  opposes #1348 Claim 4's ambient reading for the same assert type, and the
  same fork is **already filed** as open **#1352**. Per MINER.md §4a's "already
  filed" rule, no new contradiction issue was created. The new evidence (a
  factuality-surface page naming a default judge where the factuality reference
  page names none) was added as a comment on #1352 so the resolver can widen it;
  this source note references #1352 prominently under **Contradicts** and picks
  no verdict. Checked `CONTRADICTIONS.md` (no matching open `C-NNN` entry) and
  open `contradiction`-labeled issues before deciding not to file.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-promptfoo-enterprise-findings-reports.md` (#1610) — red-team findings/export
    surface; no assert-grading or factuality config semantics; dismissed.
  - `docs-google-sre-team-lifecycles.md` (#907) — Google SRE team org/lifecycle
    chapter; no LLM-eval content; dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — OWASP red-team methodology/SDLC
    and the RAG-triad concept list; no factuality grading config; cited only
    indirectly in Guide Impact, dismissed as a cross-ref.
  - `docs-litellm-batches-api.md` — LiteLLM batches/files API; unrelated vendor
    surface; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage by an SRE
    Agent; no eval-assert config surface; dismissed.
  - `docs-promptfoo-pi-scorer.md` (#1484) — the `pi` non-LLM-judge scorer; a
    different assert family with its own grader; no factuality semantics;
    dismissed.
  - `docs-langfuse-mcp-server.md` (#131) — Langfuse docs MCP server; unrelated
    vendor/tool; dismissed.
  - `docs-google-sre-eliminating-toil.md` (#819) — toil reduction chapter; no
    LLM-eval content; dismissed.
  - `docs-google-sre-reliable-product-launches.md` (#409) — launch-process
    chapter; no LLM-eval content; dismissed.
  - `docs-promptfoo-deterministic-metrics.md` (#1289) — deterministic assertion
    tier and the `not-` prefix / `assert-set`; adjacent promptfoo surface but a
    different (non-judge) tier; dismissed as a cross-ref (noted only that the
    reference page's alias/`not-` inversion is out of scope for this page).
  - Additional cross-refs (`docs-promptfoo-factuality.md` #1348,
    `docs-promptfoo-model-graded-metrics.md` #1305,
    `docs-promptfoo-g-eval.md` #1349,
    `docs-promptfoo-model-graded-context-faithfulness.md` #1320,
    `docs-promptfoo-configuration-huggingface-datasets.md` #1526,
    `docs-promptfoo-evaluate-rag.md` #1725,
    `docs-promptfoo-assertions-metrics.md` #1287) were surfaced from the triage's
    overlap list and by searching `source-notes/` per MINER.md §4; the ones
    relevant to this surface are **cited** above.
- **Cross-ref verification (§4b)**: every cited claim was located and read in
  the cited note before writing — #1348 Claims 2/3/4/5/6 (+ its Guide Impact
  negative-control item), #1305 Claims 1/2/8, #1287 Claim 10 (+ the
  `factuality:reference` row in its Concrete Artifacts assertion-syntax table,
  seen directly), #1320 Claim 2 (read for the sibling fail-open comparison but
  not cited as a numbered claim here), #1526 Claim 1, #1725 Claim 7, and #1349
  Claim 2 (g-eval's dated pin, read for the #1352 context). Claim numbers were
  verified against each cited note's own numbering; no claim numbers invented.
  Source-note issue numbers were read from each cited note's frontmatter
  `issue:` field. #1352 read directly (open, `contradiction` +
  `needs-resolution`).
- `registry/sources.json` and `registry/claims-index.json` were NOT edited; they
  are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
