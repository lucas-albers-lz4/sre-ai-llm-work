---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/factuality/
source_type: docs
title: "Promptfoo Configuration: Factuality"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-17
date_extracted: 2026-09-17
last_checked: 2026-09-17
status: current
confidence_overall: emerging
issue: "#1348"
---

# Promptfoo Configuration: Factuality

> The per-type vendor reference page for promptfoo's `factuality` reference-based
> grading assert — the page that answers what a bare `type: factuality` gate
> actually admits. The judge maps output-vs-reference into a five-category
> taxonomy inherited from OpenAI's evals (`fact.yaml`), with a **hard-coded
> permissive default pass-set: A (subset), B (superset), C (agree), and E
> (differ-but-factual) pass by default, and only D (disagree) fails** — so an
> uncalibrated factuality gate passes an output that is consistent with the
> reference *and adds unverified claims* (B), and passes E on the judge's own
> qualitative judgment that the differences "don't matter". The only
> documented lever to make the gate stricter is changing per-category scores
> under `defaultTest.options.factuality`. This page is the deliberately-unmined
> `factuality` sub-page the model-graded hub note (#1305) explicitly recorded as
> not followed, and it supplements — not duplicates — the sibling
> context-faithfulness note (#1320).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Factuality"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own assert-type behavior — authoritative for *what promptfoo does*
  with a given `factuality` config (the judge taxonomy, the default pass-set,
  the category-score override surface, the `rubricPrompt` parse contract), but
  vendor-positioned: the page carries no measured judge-agreement,
  pass-rate, or calibration figures and no independent practitioner
  validation. Everything below is checkable against an installed CLI.
- **Scope**: A single self-contained reference page (intro, How to use it,
  How it works, Example Configuration, Customizing Score Thresholds, Overriding
  the Grader, Customizing the Prompt, Using Factuality with CSV, See Also).
  It is the deep-dive on the `factuality` member of the reference-based
  (non-retrieval) model-graded class that `docs-promptfoo-model-graded-metrics.md`
  (#1305) catalogued at claim level only — that note's Extraction Notes
  explicitly record "model-graded-closedqa, factuality, answer-relevance,
  conversation-relevance … were NOT followed." This page therefore carries the
  *delta* (the five-category taxonomy, the default pass-set, the category-score
  override surface, the `{{input}}`/`{{ideal}}`/`{{completion}}` rubric
  contract), not a re-extraction of the model-graded framing. Does NOT cover the
  sibling sub-pages (`context-faithfulness` #1320, `answer-relevance` #1319,
  etc. — separate sources per the one-note-per-sub-page convention), the
  model-graded hub page (#1305), or the aggregation/scoring model of the
  assertions hub (#1287).
- **Last updated**: the page footer reads "Last updated on Sep 17, 2026 by
  jameshiester-oai". Current, not stale.

## Extracted Claims

### Claim 1: `factuality` grades factual consistency of an LLM output against a reference answer via a five-category judge taxonomy — A (subset), B (superset), C (agree), D (disagree), E (differ-but-factual) — using a structured prompt that is "based on OpenAI's evals" (the `evals/registry/modelgraded/fact.yaml` model-graded definition), so the taxonomy is inherited, not a promptfoo invention
- **Evidence**: The page's intro paragraph naming OpenAI's evals with a direct
  link to `fact.yaml`, and the "How it works" section's five bullet categories
  with their (A)–(E) letters.
- **Confidence**: settled (documented product behavior; the provenance link is
  explicit on the page)
- **Quote**: "The `factuality` assertion evaluates the factual consistency between an LLM output and a reference answer. It uses a structured prompt based on OpenAI's evals to determine if the output is factually consistent with the reference." plus the category list, verbatim: "(A) Output is a subset of the reference and is fully consistent", "(B) Output is a superset of the reference and is fully consistent", "(C) Output contains all the same details as the reference", "(D) Output and reference disagree", "(E) Output and reference differ, but differences don't matter for factuality"
- **Our assessment**: The taxonomy's provenance matters for the guide's
  "calibrate the judge before trusting it" rule: the categories are a
  containment/agreement ladder, not a numeric scale — and two of the five
  categories (B, E) require the judge to make a *qualitative* call ("fully
  consistent", "differences don't matter"), which is exactly the judge-variance
  surface the corpus's measured-judge-gap material (#261) warns about. The
  `fact.yaml` inheritance means the same taxonomy appears in OpenAI-side evals
  tooling; it is not a promptfoo-specific contract, which teams auditing a
  custom `rubricPrompt` should know when they compare notes with OpenAI-based
  workflows.

### Claim 2: The default pass-set is permissive — options A (subset), B (superset), C (agree), and E (differ-but-factual) are passing by default and only D (disagree) fails — so a bare `type: factuality` assert passes an output that is consistent with the reference *and adds unverified claims* (the superset case) and passes E on the judge's own judgment that the differences "don't matter"
- **Evidence**: The "How it works" section's default statement.
- **Confidence**: settled (documented default)
- **Quote**: "By default, options A, B, C, and E are considered passing grades, while D is considered failing."
- **Our assessment**: The triage's key question resolves directly from the
  vendor's own sentence. The default pass-set is permissive in two directions
  at once, and both directions are silent: a **superset** output (B) passes, so
  the gate does not catch an answer that is consistent with the reference *and
  appends hallucinated or unverified content* — the exact RAG-fabrication
  failure a factuality gate exists to catch; and (E) passes whenever the judge
  decides the differences "don't matter for factuality," a subjective call the
  judge makes per verdict. Note that B and E are not containment checks: both
  require the judge to evaluate whether extra content is "fully consistent" or
  merely "doesn't matter" — so even the *passing* side of the taxonomy leans on
  qualitative judgment, and per #1305 Claim 1's ambient judge, that judge can
  change with the environment with no config edit. This is the reference-based
  sibling of the context-faithfulness default (#1320 Claim 2): there the gate is
  score-blind because the documented `threshold` default is `0`; here the gate
  is *admission-allowing by documented default grades* — different mechanism,
  same "the default config passes what the assert exists to catch" family.
  (The 1→pass / 0→fail mapping of the category scores is the Miner's reading of
  the documented defaults next to the documented pass-set; this page never
  spells the mapping out.)

### Claim 3: The pass-set is explicit config — per-category scores under `defaultTest.options.factuality.{subset, superset, agree, disagree, differButFactual}` with documented defaults `1, 1, 1, 0, 1` — and this per-category grade override is the only documented lever for making the gate stricter than the default pass-set
- **Evidence**: The "Customizing Score Thresholds" section: the heading sentence
  and the default-annotated YAML block.
- **Confidence**: settled (documented defaults and override surface)
- **Quote**: "You can customize which factuality categories are considered passing by setting scores in your test configuration:" with the verbatim defaults `subset: 1 # Score for category A (default: 1)`, `superset: 1 # Score for category B (default: 1)`, `agree: 1 # Score for category C (default: 1)`, `disagree: 0 # Score for category D (default: 0)`, `differButFactual: 1 # Score for category E (default: 1)`
- **Our assessment**: This is the calibration lever Ch05's "explicit,
  falsifiable pass/fail rubrics" rule wants — and notably, the lever is
  *category grades*, not a numeric `threshold`. A team that wants the gate to
  block unverified additions must explicitly change `superset` to `0`; a team
  that wants extension-only-passes-D-disagrees to fail must also flip
  `differButFactual` to `0`. Absent that, the defaults hard-code the permissive
  pass-set of Claim 2 with no score aggregation to override. The category-score
  surface is the honest place to put a "what does our factuality gate pass?"
  review: it is enumerable (five values), which is more modellable than a
  threshold on a judge's opaque score — but flipping grades only moves the
  boundary the *ambient judge* (Claim 4) draws.

### Claim 4: The factuality grader is overridable at three levels ("Like other model-graded assertions" — CLI `--grader`, `defaultTest.options.provider`, assertion-level `provider`), but — unlike the g-eval per-type page, which a sibling contradiction says pins `gpt-4.1-2025-04-14` — this page names no default judge model, so the default grader remains the ambient credential-selected one from the model-graded hub (#1305 Claim 1)
- **Evidence**: The "Overriding the Grader" section's three numbered override
  forms (`promptfoo eval --grader openai:gpt-5-mini`; `defaultTest: options: provider: anthropic:claude-sonnet-4-5-20250929`; assertion `provider: openai:gpt-5-mini`), plus the absence of any
  sentence naming a default judge anywhere on the page (verified by full read).
- **Confidence**: settled for the override surface (documented); the
  unpinned-default consequence is #1305 Claim 1 applied to this page's silence
- **Quote**: "Like other model-graded assertions, you can override the default grader:" and the three override forms, verbatim: "`promptfoo eval --grader openai:gpt-5-mini`", "`defaultTest: options: provider: anthropic:claude-sonnet-4-5-20250929`", "`assert: - type: factuality value: Sacramento is the capital of California provider: openai:gpt-5-mini`"
- **Our assessment**: The silence is itself a finding. The page documents the
  override path but never states what the *default* grader is, so per #1305
  Claim 1 the factuality verdict is drawn by whatever model promptfoo picks from
  ambient credentials — OpenAI, Anthropic, Gemini, etc. This places factuality
  on #1305's "nothing is pinned" side of the adjacent open contradiction #1352
  (g-eval's dated default pin vs the hub's family-wide ambient claim): the
  factuality page names no pin, so it neither joins nor resolves #1352, but if
  #1352's Side B wins for g-eval it would show per-type pages can pin defaults
  and underscore that this page's default is *unspecified*. For a CI gate, the
  grader should be pinned explicitly on every factuality assert (or globally via
  `defaultTest.options.provider`).

### Claim 5: The custom rubric contract uses a family-specific Nunjucks template set — `{{input}}` (original prompt/question), `{{ideal}}` (reference from `value`), `{{completion}}` (LLM response) — and the checker's parser accepts exactly two formats, a single letter `"A"` / `"(A)"` or a JSON object `{"category": "...", "reason": "..."}`, so a custom `rubricPrompt` whose output satisfies the reader but not the parser silently cannot gate correctly
- **Evidence**: The "Customizing the Prompt" section: the three template-variable
  bullets, the two accepted-output-format instructions, the worked custom-prompt
  YAML, and the trailing parse note.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can customize the evaluation prompt using the `rubricPrompt` property. The prompt has access to the following Nunjucks template variables:" with the verbatim variable lines "`{{input}}`: The original prompt/question", "`{{ideal}}`: The reference answer (from the `value` field)", "`{{completion}}`: The LLM's actual response (provided automatically by promptfoo)"; "Your custom prompt should instruct the model to either:"; and the parse contract, verbatim: "The factuality checker will parse either format:", "A single letter response like \"A\" or \"(A)\"", "A JSON object: `{\"category\": \"A\", \"reason\": \"Detailed explanation...\"}`"
- **Our assessment**: Two robustness gotchas for custom rubrics, both
  checkable. First, the variable names are assertion-family-specific: the
  reference in is `{{ideal}}`, not `{{rubric}}`/`{{output}}` — a rubric prompt
  copied from an `llm-rubric` config binds nothing here (the hub's #1305 Claim
  8 already flags factuality as needing "specific output formats … and
  assertion-specific prompts"). Second, the parse contract is a strict
  disjunction — bare letter *or* `{category, reason}` JSON. A custom prompt that
  returns, say, a JSON object with `score` but no `category`, or prose like
  "Category B", satisfies the reader but not the parser, and the page states no
  failure behavior for the unparseable case — so a malformed custom rubric is a
  silent-gate risk on top of the default pass-set.

### Claim 6: `factuality` cases can be authored in CSV form via the `factuality:` prefix in an `__expected` column — with the reference answer as the column value — the mass-case authoring path for reference-based grading
- **Evidence**: The "Using Factuality with CSV" section and its two-row
  `tests.csv` example.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Use the `factuality:` prefix in `__expected` columns:" with the verbatim example rows `"What does GPT stand for?","factuality:Generative Pre-trained Transformer"` and `"What is photosynthesis?","factuality:Plants convert sunlight into chemical energy"`
- **Our assessment**: This is the reference-answer supply path: because
  factuality grades against an externally-supplied reference (from `value` or
  this CSV prefix), the gate can only test claims a human wrote down. The CSV
  form is the same `factuality:` string-syntax family the assertions hub
  catalogues (`factuality:...` in #1287's Concrete Artifacts assertion-syntax
  table) — so the ground truth is a curated, reviewable test asset, unlike
  retrieval-anchored RAG asserts where the context comes from the pipeline. The
  practical consequence for SRE: factuality gates are only as strong as the
  reference corpus, and a large uncurated CSV of `factuality:` cases inherits
  the permissive default pass-set of Claim 2 unless every category grade is
  audited too.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/factuality/
(sections as noted).

### The five-category taxonomy (verbatim from "How it works")

```
(A) Output is a subset of the reference and is fully consistent
(B) Output is a superset of the reference and is fully consistent
(C) Output contains all the same details as the reference
(D) Output and reference disagree
(E) Output and reference differ, but differences don't matter for factuality
```

Default pass-set (verbatim): "By default, options A, B, C, and E are considered passing grades, while D is considered failing."

### Basic usage (verbatim from "How to use it")

```yaml
assert:
  - type: factuality
    # Specify the reference statement to check against:
    value: The Earth orbits around the Sun
```

### Example configuration (verbatim from "Example Configuration")

```yaml
prompts:
  - 'What is the capital of {{state}}?'
providers:
  - openai:gpt-5
  - anthropic:claude-sonnet-4-5-20250929
tests:
  - vars:
      state: California
    assert:
      - type: factuality
        value: Sacramento is the capital of California
  - vars:
      state: New York
    assert:
      - type: factuality
        value: Albany is the capital city of New York state
```

### Per-category score defaults (verbatim from "Customizing Score Thresholds")

```yaml
defaultTest:
  options:
    factuality:
      subset: 1 # Score for category A (default: 1)
      superset: 1 # Score for category B (default: 1)
      agree: 1 # Score for category C (default: 1)
      disagree: 0 # Score for category D (default: 0)
      differButFactual: 1 # Score for category E (default: 1)
```

### Grader override forms (verbatim from "Overriding the Grader")

```bash
promptfoo eval --grader openai:gpt-5-mini
```

```yaml
defaultTest:
  options:
    provider: anthropic:claude-sonnet-4-5-20250929
```

```yaml
assert:
  - type: factuality
    value: Sacramento is the capital of California
    provider: openai:gpt-5-mini
```

### Custom rubric prompt (verbatim from "Customizing the Prompt")

```yaml
defaultTest:
  options:
    rubricPrompt: |
      Input: {{input}}
      Reference: {{ideal}}
      Completion: {{completion}}
      Evaluate the factual consistency between the completion and reference.
      Choose the most appropriate option:
      (A) Completion is a subset of reference
      (B) Completion is a superset of reference
      (C) Completion and reference are equivalent
      (D) Completion and reference disagree
      (E) Completion and reference differ, but differences don't affect factuality
      Answer with a single letter (A/B/C/D/E).
```

Accepted parse formats (verbatim): "A single letter response like \"A\" or
\"(A)\"" and "A JSON object: `{\"category\": \"A\", \"reason\": \"Detailed
explanation...\"}`".

### CSV form (verbatim from "Using Factuality with CSV")

```
question,__expected
"What does GPT stand for?","factuality:Generative Pre-trained Transformer"
"What is photosynthesis?","factuality:Plants convert sunlight into chemical energy"
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 1** (the
    hub's ambient judge: "By default, model-graded asserts use promptfoo's
    built-in grading provider. Promptfoo chooses that provider from the
    credentials available in the environment…") — this page documents the
    "override the default grader" surface for factuality but names no default
    judge, so its verdict is drawn by an ambient, credential-selected model
    unless pinned; Claims 2 and 4 here are the per-type instance of the hub's
    unpinned-judge finding. (Verified: #1305 Claim 1.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 8** (the hub's
    multilingual note: "Other assertions like `factuality` and `context-recall`
    require specific output formats and need assertion-specific prompts") —
    this page's strict letter-or-JSON parse contract and its
    `{{input}}`/`{{ideal}}`/`{{completion}}` variable set (Claim 5) are that
    "specific output format" surface, now in concrete form. (Verified: #1305
    Claim 8.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (the
    deterministic/model-assisted boundary: "model-assisted checks (similarity,
    classifier, moderation, llm-rubric, g-eval, context-* families, factuality)
    inherit every judge-bias problem…") — this page is the config-level detail
    under that catalogue row for the `factuality` member: the judge-called
    categories B and E (Claims 1-2) are exactly where judge bias and variance
    land. (Verified: #1287 Claim 10.)
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` **Claim
    2** (the sibling's documented `threshold` default of `0` → a bare
    `context-faithfulness` assert is score-blind and passes a fully-unsupported
    response) — same fail-open family, different mechanism: context-faithfulness
    defaults to not-gating on score, while this page's factuality defaults to a
    permissive *pass-set* that admits supersets and judge-judged "differ but
    doesn't matter" outputs. Together they are two independently documented
    instances of "the default config passes what the assert exists to catch."
    (Verified: #1320 Claim 2.)

- **Contradicts**: None identified, and no contradiction issue filed. Checked
  `CONTRADICTIONS.md` (no open `C-NNN` entries for this surface) and open
  `contradiction`-labeled issues: #1150/#1338/#1322/#1307 are unrelated
  (LiteLLM routing/eval semantics, promptfoo missing-trace). **#1352 is
  adjacent context, not a conflict with this page**: it pits the g-eval
  per-type page's pinned default judge (`gpt-4.1-2025-04-14`) against the hub's
  family-wide ambient-judge claim (#1305 Claim 1). This page names no default
  judge at all, so it sits entirely on #1305's ambient side and neither joins
  nor resolves #1352 — but if #1352's Side B wins, it would establish that
  per-type pages *can* name a default, making this page's silence the notable
  contrast. No contradiction issue warranted.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — directly
    fills that note's deliberate scoping gap: its Scope and Extraction Notes
    explicitly record that "factuality … were NOT followed." This note is the
    per-type deep-dive under that carve-out: the taxonomy and default pass-set
    (Claims 1-2), the category-score override lever (Claim 3), the
    no-default-judge silence under the hub's ambient-judge framing (Claim 4),
    and the parse contract that concretizes the hub's "specific output formats"
    warning (Claim 5).
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) **Claim 10**
    (the model-assisted catalogue row naming factuality) **and its Concrete
    Artifacts assertion-syntax table** (`factuality:reference` /
    `factuality:Paris is the capital of France` string form) — this page adds
    the reference-level semantics and the CSV `factuality:` prefix (Claim 6)
    beneath that catalogue entry. (Verified: #1287 Claim 10 and the
    `factuality:reference` row in its assertion-syntax table.)

- **Novel**: The risk *frame* (fail-open / permissive defaults letting a gate
  pass what it exists to catch) is not new — it is already in the corpus as
  #1287's test-case `threshold: 0`/`weight: 0` traps and #1320's score-blind
  default. What is new here:
  1. **The five-category factuality taxonomy with its explicit default pass-set**
     (Claims 1-2) — a bare `type: factuality` becomes pass-all-except-disagree;
     the first per-type documentation of what a factuality verdict is, and the
     first corpus record that a *superset* output (reference-consistent plus
     unverified additions) passes by default.
  2. **The per-category grade override as the calibration lever** (Claim 3) —
     pass/fail configured as five enumerable category grades with documented
     defaults (1/1/1/0/1) rather than a numeric threshold; the "what does our
     gate pass?" review item is enumerable.
  3. **The strict letter-or-JSON parse contract with family-specific template
     variables** (Claim 5) — `{{input}}`/`{{ideal}}`/`{{completion}}` vs the
     `{{output}}`/`{{rubric}}` of the rubric family; custom rubrics must satisfy
     the parser, and unparseable responses have no documented failure behavior.
  4. **The provenance record** (Claim 1) — the taxonomy is inherited from
     OpenAI's `fact.yaml`, not a promptfoo invention.
  5. **The no-default-judge silence** (Claim 4) — vs the g-eval page's dated
     pin (the #1352 Side B claim), factuality documents no default judge; the
     contrast between two per-type pages in the same family is itself corpus
     value for the guide's judge-pinning rule.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md`, "Judge calibration before judge trust" /
  the gate-review checklist built up from #1287/#1305/#1320)**: add the
  **factuality pass-set rule** — a bare `assert: - type: factuality` admits
  superset outputs (unverified/hallucinated additions on top of a
  reference-consistent answer) and judge-judged "differences don't matter"
  outputs by default (Claims 1-2); it does **not** need a `threshold` edit to go
  permissive, the permissiveness is the documented default. Rule: (a) review the
  five category grades on every factuality assert — a gate that must block
  fabrication sets `superset: 0` (and, for disagreement-strictness,
  `differButFactual: 0`) explicitly (Claim 3); (b) run a D-category negative
  control to prove the gate discriminates, the same negative-control item the
  score-blind siblings (#1320) require; (c) pin the grader explicitly — this
  page names no default judge, so per #1305 Claim 1 the boundary is drawn by an
  ambient model unless `provider:`/`--grader`/`defaultTest.options.provider` is
  set (Claim 4); (d) validate any custom `rubricPrompt` against the parser — it
  must return a bare letter or `{category, reason}` JSON, and the unparseable
  case has no documented failure behavior (Claim 5).
- **Chapter 05 — rubric portability**: record the variable-set divergence —
  factuality binds `{{input}}`/`{{ideal}}`/`{{completion}}`, not the
  `{{output}}`/`{{rubric}}` used by `llm-rubric`/`g-eval` (Claim 5; extending
  #1305 Claim 8's "assertion-specific prompts"). Copying a rubricPrompt across
  assert types silently unbinds the variables — a review-greppable footgun.
- **Chapter 06 (Security and Trust) — RAG/grounding gates**: document the
  superset-pass exposure (Claim 2) next to the RAG-triat material
  (`blog-promptfoo-owasp-red-teaming.md` Claim 7): the RAG factuality gate, as
  shipped by default, will happily green an answer that pads a correct statement
  with fabricated detail — and unlike `context-faithfulness` (+context passes
  green at default score) the tell is not a low score but a *passing* category
  the operator must re-read.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/factuality/);
  quotes and code blocks verified character-for-character against the fetched
  rendered HTML before writing (verbatim categories, default-pass-set sentence,
  score defaults YAML, grader-override forms, rubric prompt, parse formats, CSV
  rows). Footnotes/markup noise (e.g. inline code emphasis) removed from quoted
  fragments only where a contiguous passage carried the meaning; no passages
  spliced across non-adjacent sentences.
- **Recency discrepancy with the triage**: the Prospector's triage noted "page
  last updated Sep 16, 2026 (today)". The page footer actually reads "Last
  updated on Sep 17, 2026 by jameshiester-oai" — the page was updated again
  today (Sep 17 2026 UTC, `last_checked` date). Recorded as Sep 17.
- **Confidence rationale**: `confidence_overall` is `emerging`, matching the
  sibling promptfoo config notes (#1305, #1320, #1332, #1319): the individual
  claims (taxonomy, default pass-set, category-score defaults, override
  surface, parse contract) are settled-for-product-behavior and directly
  checkable against an installed CLI, but this is vendor documentation with no
  measured judge-agreement or pass/failure-rate figures; the
  operational-consequence framing (superset admission, ambient-judge boundary,
  unparseable-rubric silence) is the Miner's synthesis on top of documented
  behavior. Claim 2's "1→pass / 0→fail" score mapping is flagged as synthesis —
  the page never spells it out; the vendor states the pass-set in prose and the
  scores as defaults.
- **Triage key-question resolution**: the Prospector's reading that "by
  default options A, B, C, E pass, D fails" is confirmed verbatim on the page.
  The claimed hazard — a superset output passes, so the gate misses
  reference-consistent-plus-unverified answers — holds as documented default
  behavior (Category B is a passing grade by default; no threshold or score
  aggregation is documented that would filter it). The interaction with the
  unpinned judge (#1305 Claim 1) holds via this page's silence on a default
  judge (Claim 4).
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-promptfoo-model-graded-metrics.md` (#1305) — **cited heavily**
    (Corroborates Claims 1/8; Extends — the direct parent).
  - `docs-promptfoo-assertions-metrics.md` (#1287) — **cited** (Corroborates
    Claim 10; Extends — plus its `factuality:reference` artifact row).
  - `docs-promptfoo-model-graded-context-faithfulness.md` (#1320) — not in the
    candidate list as written but surfaced in `source-notes/` per MINER.md §4
    and the triage's "sibling instance" pointer; **cited** (Corroborates Claim 2).
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — OWASP red-team
    methodology/SDLC and the RAG-triad concept list (Claim 7 names factuality as
    a triad dimension); no per-type grading/config semantics; cited only
    indirectly in Guide Impact guidance, dismissed as a cross-ref.
  - `blog-promptfoo-red-team-claude.md` (#689) and `blog-promptfoo-red-team-gemini.md`
    (#690) — per-model red-team plugin strategies and reasoning-DoS testing;
    no assert-scoring or judge-taxonomy semantics; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage by an SRE
    Agent using LLM-as-judge *alerts*; no eval-assert config surface; dismissed.
  - `docs-google-sre-team-lifecycles.md` (#907) — Google SRE team org/lifecycle
    chapter; no LLM-eval content; dismissed.
  - `docs-langfuse-mcp-server.md` (#131) — Langfuse docs MCP server; unrelated
    vendor/tool; dismissed.
  - `docs-promptfoo-classifier-grading.md` (#1288) — classifier-assert
    thresholds and HF-inference wiring; a different assert family, no
    model-graded taxonomy content; dismissed.
  - `docs-promptfoo-javascript-assertions.md` (#1304) — custom-JS assertion
    surface; its `context.trace` silent-pass guard (#1307 Side A) is a
    trace-data concern; no shared claims with reference-based grading; dismissed.
- **Cross-ref verification (§4b)**: every cited claim was located and read in
  the cited note before writing — #1305 Claims 1, 8 (+ its Scope/Extraction
  Notes sub-page-not-followed statements), #1320 Claim 2, #1287 Claim 10 (+ the
  `factuality:reference` row in its Concrete Artifacts assertion-syntax table).
  Claim numbers verified against the cited notes' own numbering; no claim
  numbers invented. Source-note issue numbers read from each cited note's
  frontmatter (`issue:` field): #1305, #1320, #1287 confirmed as listed.
- **No contradiction issue filed**: the page opposes no existing source-note
  claim (verified against `CONTRADICTIONS.md` — no open `C-NNN` entries — and
  the open `contradiction`-labeled issues #1150/#1307/#1322/#1338/#1352). The
  permissive default *joins* the corpus's existing fail-open family (#1287
  Claims 3/4, #1305 Claim 10, #1320 Claim 2) rather than conflicting with it;
  #1352 is adjacent per-type-page context (g-eval's pinned default) that this
  page neither joins nor resolves, noted in the Contradicts section.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.