---
source_url: https://www.promptfoo.dev/docs/guides/deepseek-benchmark
source_type: docs
title: "Promptfoo Guides: DeepSeek vs GPT vs O3 vs Llama — Run a Custom Benchmark"
author: "Promptfoo (vendor documentation)"
date_published: unknown (living docs page; last updated 2026-10-19 by renovate[bot])
date_extracted: 2026-10-19
last_checked: 2026-10-19
status: current
confidence_overall: anecdotal
issue: "#1666"
---

# Promptfoo Guides: DeepSeek vs GPT vs O3 vs Llama

> A vendor how-to for a four-model, cross-vendor promptfoo comparison whose
> corpus-new content is **configuration shape only** — a single providers block
> mixing first-party `openai:*` with `openrouter:*` routes, selective
> per-provider parameters with no stated rationale, and a duplicate-`providers:`
> YAML artifact — plus an explicitly `Unknown`-heavy model-comparison table and
> no measured results, so nothing here should be cited as model-quality,
> latency, or cost evidence.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo's applied "Model
  Comparisons" guide page, `/docs/guides/deepseek-benchmark`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of how the vendor would set up a cross-vendor
  comparison with its own tool — authoritative for *how promptfoo configures
  the run*, but vendor-positioned and evidence-thin: the page carries **no
  measured benchmark scores, no latency figures, no cost figures, no sample
  sizes, and no failure traces**. The comparison table's parameter column is
  `Unknown` for all four models, and the page hedges its own conclusion.
- **Scope**: A four-step tutorial — project setup, a duplicate `providers:`
  config block with optional per-model parameters, four test cases
  (`llm-rubric`, `contains`, and inline-schema `is-json`), and
  `npx promptfoo@latest eval` / `view` — followed by a qualitative model
  comparison table, generic selection considerations, and a conclusion. It does
  NOT declare a `prompts:` block, does NOT use `cost` or `latency` assertions,
  and does NOT cover CI gating, regression/drift, statistical rigor, or judge
  selection. The four models are `openai:gpt-5`, `openai:o3-mini`,
  `openrouter:meta-llama/llama-4-maverick`, and
  `openrouter:deepseek/deepseek-v3.2`.
- **Last updated**: footer reads "Last updated on **Oct 19, 2026** by
  **renovate[bot]**" — a dependency bot, i.e. the last touch was not necessarily
  a content edit by an author.

## Extracted Claims

### Claim 1: The page's stated methodology is that generic benchmarks fall short of app-specific requirements, so teams should build a tailored benchmark for their use case
- **Evidence**: The opening paragraph, stated as a general recommendation; the
  entire tutorial is the worked form of it. No measured support is offered for
  the recommendation itself.
- **Confidence**: emerging (a reasonable vendor methodology claim, not a
  measured one — it is advice, and the page's own example is a template)
- **Quote**: "When evaluating LLMs for your application, generic benchmarks often fall short of capturing the specific requirements of your use case."
- **Our assessment**: Direction bought, delta near zero: this is the same
  own-data thesis restated by the already-mined siblings
  (`docs-promptfoo-choosing-best-gpt-model.md` Claim 1;
  `docs-promptfoo-compare-open-source-models.md` Claim 1). Record it at
  corroborate-only weight and do not re-derive it. The page's contribution, if
  any, is the cross-vendor config shape in Claims 2–4, not the thesis.

### Claim 2: One `promptfooconfig.yaml` mixes first-party `openai:*` providers with `openrouter:*` routes for the open-weight candidates, under one prompt/test harness
- **Evidence**: The Step 2 provider list (see Concrete Artifacts) contains two
  `openai:` ids and two `openrouter:` ids; the Requirements section assigns
  separate credentials per route: OpenAI for GPT-5/o3-mini, OpenRouter for
  DeepSeek/Llama.
- **Confidence**: settled (documented, runnable config shape); illustrative,
  not measured — the page never reports a run
- **Quote**: "OpenRouter API access for DeepSeek and Llama (set `OPENROUTER_API_KEY`)"
- **Our assessment**: This is the Prospector's key question (a): the page does
  demonstrate a **mixed first-party + router** provider set. The syntax is
  already corpus-seen — `openrouter:` ids in
  `blog-promptfoo-owasp-red-teaming.md` (Concrete Artifacts) and the all-router
  matrix in `docs-promptfoo-compare-open-source-models.md` Claim 2 — so the
  delta is the *mix* in one tutorial, not the provider-id form. Note the
  confound the page does not discuss: OpenRouter and OpenAI-direct are
  different serving stacks, so any output difference across the four providers
  mixes model, route, and provider configuration. The corpus's parity rule
  (`docs-promptfoo-azure-vs-openai.md` Claim 2: outputs may differ between
  providers under identical configuration) applies, and this page never
  acknowledges it.

### Claim 3: Per-provider `config` blocks set `temperature: 0.7` for GPT-5 and Llama 4 Maverick but omit `temperature` for o3-mini and DeepSeek V3.2, with `max_tokens: 1000` on all four — and the page gives no rationale for the asymmetry
- **Evidence**: The "# Optional: Configure model parameters" block in Step 2
  (see Concrete Artifacts). A full-page read finds no prose explaining why
  temperature is set on two models and omitted on the other two; the only
  annotation is the inline comment "# Optional: Configure model parameters".
- **Confidence**: settled for the config as written; anecdotal for any implied
  convention — the page never states the reasoning-model rule
- **Quote**: "# Optional: Configure model parameters"
- **Our assessment**: The Prospector asked whether this is the "temperature
  omitted for reasoning models" convention. It is *consistent with* that
  convention but **not documented as such**: nothing on the page says o3-mini
  or DeepSeek are reasoning models or that temperature is intentionally
  omitted. Worse for the convention reading, GPT-5 is also a reasoning-family
  model and the page still sets `temperature: 0.7` on it — while the corpus
  documents that "GPT-5 series reasoning models ignore temperature and do not
  need it set" (`docs-promptfoo-llm-rubric.md` Claim 10;
  `docs-promptfoo-model-graded-metrics.md` Claim 7). So the block reads as an
  unexplained partial override, not a principled per-model parameter policy.
  No contradiction issue: the page never claims GPT-5 honors temperature; it
  merely sets a no-op knob.

### Claim 4: Step 2's fenced `promptfooconfig.yaml` contains two top-level `providers:` keys in one document — a duplicate mapping key, not an additive "optional" overlay
- **Evidence**: The fenced block reproduces a complete four-item `providers:`
  list, then "# Optional: Configure model parameters" and a **second**
  `providers:` key with `id`/`config` objects (see Concrete Artifacts). The
  page introduces it with "Edit your `promptfooconfig.yaml` to include the four
  models:" and never says to replace the first block.
- **Confidence**: settled (the duplication is observable in the page's code
  block); the parse consequence is standard YAML behavior
- **Quote**: (no direct quote; see the duplicated block in Concrete Artifacts)
- **Our assessment**: YAML has no merge semantics for repeated mapping keys:
  standard parsers reject the document as a duplicate key (permissive loaders
  may take the last value, silently discarding the first list). A reader who
  pastes both blocks does not get "the same providers with optional params" —
  they get either a config-load error or a replacement, depending on the
  loader. This is an applied-config quality defect the tutorial does not flag;
  the correct instruction is to replace the first `providers:` block with the
  second. Worth recording as an example of a vendor how-to shipping a
  copy-paste-invalid config.

### Claim 5: The test suite is four single-case "dimensions" — reasoning, code generation, math, and structured output — with exactly one case per dimension
- **Evidence**: The Step 3 `tests:` block (see Concrete Artifacts): one
  quantum-cryptography reasoning case, one merge-sort code case, one calculus
  case, one JSON-output case. Every case has at least one assertion.
- **Confidence**: settled (documented config); the sufficiency of one case per
  dimension is not claimed by the vendor
- **Quote**: "Let's create a comprehensive test suite that evaluates the models across different dimensions:"
- **Our assessment**: The page calls this "comprehensive", but n=1 per
  dimension means the suite cannot distinguish a model's capability from
  per-case variance — and it never repeats runs, so there is no within-model
  variance estimate at all. This is the same applied-suite thinness the
  siblings exhibit (`docs-promptfoo-choosing-best-gpt-model.md` Claim 7 uses
  three riddles; `docs-promptfoo-compare-open-source-models.md` Claim 7 uses
  eight mostly-ungated cases), here compressed to one case per named
  dimension. Useful to the guide only as an illustration of *why* "a green eval
  is not evidence until you can name what it measured" applies at the test-set
  level.

### Claim 6: The quality gate is weak by construction — the two `llm-rubric` assertions omit `threshold`, and the math case's extra `contains` checks are word-presence checks that a wrong answer can satisfy
- **Evidence**: The math case asserts `contains: derivative` and `contains:
  product rule` in addition to a correctness rubric with no threshold; the
  reasoning case also uses a threshold-less `llm-rubric`. The code and JSON
  cases use `contains: def merge_sort` and schema-valid `is-json` respectively.
- **Confidence**: settled (documented config); consequence documented in other
  corpus notes
- **Quote**: "Response should show clear mathematical steps, use proper calculus notation, and arrive at the correct answer: 3x^2*ln(x) + x^2"
- **Our assessment**: Two known failure modes recur here. (1) Per
  `docs-promptfoo-model-graded-metrics.md` Claim 10, an `llm-rubric` without
  `threshold` is score-blind — PASS depends on the grader's `pass` field,
  defaulting to `true` — so the correctness rubric has no quality bar. (2) The
  `contains` word checks gate vocabulary, not correctness: an answer that says
  "I would use the derivative and the product rule" passes both while solving
  nothing. The split is a literal instance of the deterministic/model-assisted
  taxonomy in `docs-promptfoo-assertions-metrics.md` Claim 10. The tutorial
  never notes either property; per the sibling notes, do not re-derive the
  primitive semantics, only record that the vendor's own benchmark ships this
  shape.

### Claim 7: The structured-output case uses `is-json` with an inline JSON Schema (`object`, required `name`/`age`/`email`, age 0–150, email format) inside the benchmark run
- **Evidence**: The fourth test case's `assert` (see Concrete Artifacts). This
  is the Prospector's key question (c).
- **Confidence**: settled (documented product behavior and config)
- **Quote**: "- type: is-json"
- **Our assessment**: No material delta over the corpus. Inline-schema `is-json`
  is already documented at `docs-promptfoo-deterministic-metrics.md` Claim 7
  ("You may optionally set a `value` as a JSON schema in order to validate the
  JSON contents") and applied with an inline schema at
  `docs-promptfoo-evaluate-crewai.md` Claim 4. The only detail this page adds
  is the particular field contract (`age` bounds, `format: email`), which is
  example content, not new mechanism. Record the applied usage; do not promote
  inline-schema validation as a delta.

### Claim 8: The "Model Comparison" table is qualitative and self-admittedly unmeasured — all four `Parameters` values are `Unknown`, "Key Strengths" are unsourced assertions, and the page hedges that results may differ
- **Evidence**: The comparison table (see Concrete Artifacts) and the
  sentence immediately after it. The table is introduced as "based on public
  benchmarks" but cites no benchmark, no score, no version, and no date. The
  conclusion repeats the same qualitative claims.
- **Confidence**: settled (observable page content); anecdotal as any kind of
  model-quality evidence
- **Quote**: "However, your custom benchmark results may differ significantly based on your specific use case."
- **Our assessment**: Confirms the Prospector's evidence-thinness warning in
  the strongest terms: the vendor's own cross-model comparison page supplies a
  table whose quantitative columns are entirely `Unknown` and whose "strengths"
  column has no citation. The only honest reading is that the page is a
  how-to scaffold plus product demonstration. Do **not** cite it for any
  model-quality, parameter-count, latency, or cost claim. It is useful in the
  guide as an example of *unmeasured* model-comparison content, not as
  evidence for a selection decision.

### Claim 9: The "Considerations for Model Selection" section asserts model strengths and resource traits without evidence, and compares DeepSeek to an unspecified set of "smaller open models"
- **Evidence**: Four bullets — task specificity ("DeepSeek excels in
  mathematical and coding tasks"), resource requirements ("DeepSeek V3.2 is more
  resource-intensive than smaller open models, for example."), API
  availability, and cost structure. None carries a number, source, or method.
- **Confidence**: anecdotal (unsourced vendor prose)
- **Quote**: "DeepSeek excels in mathematical and coding tasks"
- **Our assessment**: These are generic selection heuristics, and the one
  comparative claim ("more resource-intensive than smaller open models") is a
  category error as written — it compares a large MoE model to unnamed smaller
  models rather than to the other candidates in the tutorial. The API
  availability bullet is also internally odd: it says GPT "requires internet
  access", which is true of every hosted provider in the comparison. Record as
  evidence-free guidance; no guide recommendation should rest on it.

### Claim 10: The page drifts from `o3-mini` in the config and table to `o3` in the conclusion — an internal model-identity inconsistency
- **Evidence**: Step 2 uses `openai:o3-mini`; the comparison table row is
  `o3-mini`; the conclusion says "o3 with strong reasoning performance".
- **Confidence**: settled (observable page content)
- **Quote**: "o3 with strong reasoning performance"
- **Our assessment**: Small but telling: the prose summary is not tied to the
  model actually configured, so a reader cannot tell which model the
  conclusion's "strong reasoning performance" refers to. It reinforces Claim 8's
  verdict that the comparison text was not generated from, or checked against,
  a measured run. Not a §4a contradiction — both statements point the same
  direction and the page provides no opposing claims, only naming drift.

### Claim 11: The tutorial never declares a `prompts:` block, so the prompt under test is implicit and unstated
- **Evidence**: A full-page read finds no `prompts:` key and no prompt
  template; the four test cases supply only `vars.input` strings. Both sibling
  guides declare a `prompts:` block
  (`docs-promptfoo-choosing-best-gpt-model.md` Concrete Artifacts shows a
  riddle template; `docs-promptfoo-azure-vs-openai.md` Concrete Artifacts shows
  a prompt list).
- **Confidence**: settled for the omission (verifiable by full-page read); the
  runtime consequence is not documented on this page
- **Quote**: (no direct quote; see the `tests:` artifact — all cases use `input` vars and no `prompts:` key exists on the page)
- **Our assessment**: For a page whose thesis is "build a benchmark that
  matters for your application", omitting the prompt template is a real gap:
  the reader cannot see the instruction being evaluated, so even a successful
  run would not be reproducible as a comparison. Whether promptfoo falls back
  to an implicit `{{input}}` prompt or errors is not stated here; either way,
  the applied config is incomplete as a benchmark template. Pair this with
  Claim 5 (n=1 per dimension) and Claim 4 (duplicate key) as copy-paste
  hazards.

## Concrete Artifacts

### Provider config — two `providers:` keys in one fenced block (verbatim from Step 2)

```yaml
providers:
  - 'openai:gpt-5'
  - 'openai:o3-mini'
  - 'openrouter:meta-llama/llama-4-maverick'
  - 'openrouter:deepseek/deepseek-v3.2'

# Optional: Configure model parameters
providers:
  - id: openai:gpt-5
    config:
      temperature: 0.7
      max_tokens: 1000
  - id: openai:o3-mini
    config:
      max_tokens: 1000
  - id: openrouter:meta-llama/llama-4-maverick
    config:
      temperature: 0.7
      max_tokens: 1000
  - id: openrouter:deepseek/deepseek-v3.2
    config:
      max_tokens: 1000
```

### Requirements (verbatim)

```text
- Node.js `>=22.22.0`
- OpenRouter API access for DeepSeek and Llama (set `OPENROUTER_API_KEY`)
- OpenAI API access for GPT-5 and o3-mini (set `OPENAI_API_KEY`)
```

```bash
export OPENROUTER_API_KEY=your_openrouter_api_key
export OPENAI_API_KEY=your_openai_api_key
```

### Test suite with assertions (verbatim from Step 3)

```yaml
tests:
  # Complex reasoning tasks
  - vars:
      input: 'What are the implications of quantum computing on current cryptography systems?'
    assert:
      - type: llm-rubric
        value: 'Response should discuss both the threats to current encryption and potential solutions'

  # Code generation
  - vars:
      input: 'Write a Python function to implement merge sort'
    assert:
      - type: contains
        value: 'def merge_sort'

  # Mathematical problem solving
  - vars:
      input: 'Solve this calculus problem: Find the derivative of f(x) = x^3 * ln(x)'
    assert:
      - type: llm-rubric
        value: 'Response should show clear mathematical steps, use proper calculus notation, and arrive at the correct answer: 3x^2*ln(x) + x^2'
      - type: contains
        value: 'derivative'
      - type: contains
        value: 'product rule'

  # Structured output
  - vars:
      input: 'Output a JSON object with the following fields: name, age, and email'
    assert:
      - type: is-json
        value:
          required:
            - name
            - age
            - email
          type: object
          properties:
            name:
              type: string
            age:
              type: number
              minimum: 0
              maximum: 150
            email:
              type: string
              format: email
```

### Run commands (verbatim from Steps 1 and 4)

```bash
mkdir deepseek-benchmark
cd deepseek-benchmark
```

```bash
npx promptfoo@latest eval
```

```bash
npx promptfoo@latest view
```

### Model comparison table (contents as published; introduced as "based on public benchmarks")

| Model | Architecture | Parameters | Key Strengths |
|---|---|---|---|
| DeepSeek-V3.2 | Sparse/MoE | Unknown | Strong reasoning, tool use, and code tasks |
| GPT-5 | Unknown | Unknown | Consistent performance across tasks |
| o3-mini | Unknown | Unknown | Reasoning and code tasks |
| Llama 4 Maverick | MoE | Unknown | Strong open-weight general model |

Immediately followed on the page by: "However, your custom benchmark results may differ significantly based on your specific use case."

Source for all artifacts: https://www.promptfoo.dev/docs/guides/deepseek-benchmark — sections as noted. Code blocks extracted character-for-character from the rendered page's HTML source (the plain-markdown render collapses line breaks inside fences); the two `providers:` keys and all indentation/comments are as published.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-choosing-best-gpt-model.md` — **Claim 1**
    (same own-data thesis; this page restates it in Claim 1), **Claim 7**
    (thin-evidence/adaptation signals on the same guide family), and
    **Claim 8** (`llm-rubric` asserts omitting `threshold`; this page repeats
    that shape in Claim 6). Closest sibling: same guide family, same
    five-step pattern. (Verified: all three claims read in full.)
  - `source-notes/docs-promptfoo-compare-open-source-models.md` — **Claim 2**
    (router/hosted/local provider entries as one selection workflow; this page
    is the mixed first-party + router variant in Claim 2) and **Claim 7**
    (the same guide family ships no measured outcomes; this page's Claim 8 is
    even thinner — an `Unknown`-heavy table rather than a prose analysis
    checklist). (Verified: both claims read in full.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` — **Claim 7**
    (`is-json` optionally validates an inline or `file://` JSON Schema;
    this page's Claim 7 is an applied inline-schema instance, not a new
    mechanism). (Verified: Claim 7 read in full.)
  - `source-notes/docs-promptfoo-evaluate-crewai.md` — **Claim 4**
    (`is-json` plus an inline JSON Schema used as a structural invariant;
    the strongest corpus precedent for this page's structured-output case).
    (Verified: Claim 4 read in full.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` — **Claim 10**
    (`llm-rubric` without `threshold` is score-blind; applies to this page's
    two rubrics in Claim 6) and **Claim 7** ("GPT-5 series reasoning models
    ignore `temperature` entirely"; relevant to this page setting
    `temperature: 0.7` on `openai:gpt-5` in Claim 3). (Verified: both claims
    read in full.)
  - `source-notes/docs-promptfoo-llm-rubric.md` — **Claim 10** (the grader
    section's "GPT-5 series reasoning models ignore `temperature` and do not
    need it set"; the corpus statement the page's GPT-5 temperature setting in
    Claim 3 is consistent with only as a no-op). (Verified: Claim 10 heading
    and quote.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` — **Claim 10**
    (deterministic vs model-assisted assertion split; classifies this page's
    `contains`/`is-json` and `llm-rubric` mix in Claim 6). (Verified: Claim 10
    heading and body.)
  - `source-notes/docs-promptfoo-azure-vs-openai.md` — **Claim 2** ("the
    outputs may differ between providers even with identical configurations")
    is the reason this page's four-provider, two-route comparison in Claim 2
    cannot attribute a difference to the model alone. (Verified: Claim 2 read
    in full.)

- **Contradicts**: None identified, and no contradiction issue filed. Checked
  `CONTRADICTIONS.md` and the open `contradiction`-labeled issues. Two
  internal-inconsistency surfaces were examined and rejected per MINER.md §4a:
  1. `o3-mini` in config/table vs `o3` in the conclusion (Claim 10) — naming
     drift, not two opposing claims that would lead to different guide advice.
  2. `temperature: 0.7` on GPT-5 (Claim 3) vs the corpus statement that GPT-5
     reasoning models ignore temperature — the page never claims the knob has
     an effect, so this is an unexplained/no-op setting, not a contradiction.
  The duplicate `providers:` key (Claim 4) is a config defect, not a conflict
  with a recorded claim.

- **Extends**:
  - `source-notes/docs-promptfoo-choosing-best-gpt-model.md` — **Claims 2–4**
    (the applied own-data selection config). That note owns the `cost`/`latency`
    budget-gate delta and the `--no-cache` omission (its Claim 6); this page has
    **no cost or latency assertions at all**, so that precondition gap does not
    arise here. This page extends the family only into the mixed
    first-party/router provider set (Claim 2). (Verified: sibling Claims 2–4
    and 6 read.)
  - `source-notes/docs-promptfoo-compare-open-source-models.md` — **Claims 2–5**
    (the provider-runtime matrix and local-swap confound). This page is the
    cross-vendor/mixed-route complement: one OpenAI-direct route beside two
    OpenRouter routes, with selective per-provider parameters (Claim 3)
    instead of an explicit per-model temperature policy. (Verified: sibling
    Claims 2–5 read.)

- **Novel** (deliberately narrow, per the Prospector's low-novelty triage):
  1. **The mixed first-party + router provider set in one tutorial** (Claim 2)
     — `openai:*` beside `openrouter:*` in the same `providers:` block. Syntax
     is corpus-seen; the mix is the small delta.
  2. **Selective per-provider parameter omission without a stated rule**
     (Claim 3) — `temperature` on two models, omitted on the other two, with
     GPT-5 (also a reasoning-family model) still carrying `temperature: 0.7`.
     Not the principled "omit for reasoning models" convention the triage
     hypothesized; an unexplained partial override.
  3. **Copy-paste config hazards as applied-guide quality signals** — the
     duplicate top-level `providers:` key (Claim 4) and the missing `prompts:`
     block (Claim 11), neither flagged by the page.
  4. **An `Unknown`-heavy vendor comparison table** (Claim 8) as the corpus's
     clearest example of unmeasured model-comparison content — useful as
     counter-example, never as evidence.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — §Evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md:386`)**: optional one-line addition that a
  cross-vendor comparison can be expressed as one config with first-party and
  router provider ids, but that mixing serving routes means any difference is
  model + route + provider, not model alone [source:
  docs-promptfoo-deepseek-benchmark, Claim 2] [emerging]. No new methodology
  recommendation; the own-data thesis is already citable from the siblings.
- **Chapter 05 — §"A green eval is not evidence until you can name what it
  measured" (`guide/05-llm-ops-reliability.md:567`)**: add two routes from this
  page to a green-but-unmeasured result: (1) one test case per named
  "dimension" with no repeats (Claim 5), and (2) a tutorial with no `prompts:`
  block and a model-name drift between config and conclusion (Claims 10–11)
  [source: docs-promptfoo-deepseek-benchmark, Claims 5, 10–11] [settled for the
  config observations]. The existing cache/judge/unit checklist is the right
  home; this is a test-set-and-reproducibility instance, not a caching one.
- **Chapter 05 — §"A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: optional footnote only, no new
  table row — the vendor's own cross-vendor benchmark ships the existing
  `llm-rubric`-without-`threshold` row plus `contains` word-presence checks on
  a math case (Claim 6), i.e. a "correctness" gate that a wrong answer
  mentioning "derivative" and "product rule" can pass
  [source: docs-promptfoo-deepseek-benchmark, Claim 6]. The mechanism is
  already documented via `docs-promptfoo-model-graded-metrics.md` Claim 10;
  cite this page only as an applied instance.
- **Chapter 05 — do NOT use for model selection**: explicitly record that this
  page's comparison table is `Unknown`-heavy and its conclusion is hedged
  (Claim 8) and that its selection bullets are unsourced (Claim 9), so it must
  not be cited for DeepSeek/GPT/o3/Llama quality, parameter counts, latency, or
  cost.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/deepseek-benchmark) in rendered
  markdown and raw HTML. Code blocks were extracted from the HTML source
  (converting `<br>` line markers to newlines) because the plain-markdown render
  collapses line breaks inside fences; all quotes were verified
  character-for-character against the fetched content before writing.
- **No sub-pages followed**: the page's requirements name providers but do not
  link substantive sub-pages that are not already-mined corpus surfaces; there
  was no linked mechanism needed to interpret the config. The only external
  dependency named is an OpenRouter/OpenAI key, not a documentation page.
- **Dedupe handled per Prospector guidance**: this note deliberately does NOT
  re-derive the own-data methodology (Claim 1, corroborate-only), `is-json`
  schema semantics (owned by `docs-promptfoo-deterministic-metrics.md` Claim 7
  and applied by `docs-promptfoo-evaluate-crewai.md` Claim 4), `llm-rubric`
  threshold semantics (owned by `docs-promptfoo-model-graded-metrics.md`
  Claim 10), the deterministic/model-assisted split
  (`docs-promptfoo-assertions-metrics.md` Claim 10), or promptfoo
  provider-id syntax (`blog-promptfoo-owasp-red-teaming.md` Concrete
  Artifacts; `docs-promptfoo-compare-open-source-models.md` Claim 2). Claims
  2–11 are the applied/cross-vendor delta the triage asked for.
- **Candidate disposition** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `source-notes/docs-promptfoo-deterministic-metrics.md` — **cited**
    (Corroborates, Claim 7: inline `is-json` schema).
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` — **dismissed**:
    agent capability tiers, workspace isolation, and sandbox limits are not
    exercised by this model-comparison tutorial.
  - `source-notes/docs-promptfoo-pi-scorer.md` — **dismissed**: third-party Pi
    scoring model; this page uses only built-in `llm-rubric`/`contains`/
    `is-json`.
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` —
    **dismissed**: enterprise findings disposition/export surface; no eval
    config overlap.
  - `source-notes/docs-litellm-batches-api.md` — **dismissed**: LiteLLM batch
    rate-limit accounting; unrelated vendor and topic.
  - `source-notes/blog-pagerduty-sre-agent-triage.md` — **dismissed**:
    AI-incident triage; no eval-selection surface.
  - `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: documentation
    MCP server; unrelated vendor and topic.
  - `source-notes/docs-google-sre-team-lifecycles.md` — **dismissed**: SRE
    team/org lifecycle; no LLM-eval content.
  - `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
    measurement; no LLM-eval content.
  - `source-notes/docs-google-sre-reliable-product-launches.md` —
    **dismissed**: launch process; no LLM-eval content.
- Additional cross-references were found by searching `source-notes/` beyond
  the candidate list: `docs-promptfoo-choosing-best-gpt-model.md`,
  `docs-promptfoo-compare-open-source-models.md`,
  `docs-promptfoo-model-graded-metrics.md`, `docs-promptfoo-llm-rubric.md`,
  `docs-promptfoo-azure-vs-openai.md`,
  `docs-promptfoo-evaluate-crewai.md`, `docs-promptfoo-assertions-metrics.md`,
  and `blog-promptfoo-owasp-red-teaming.md`. Every `Claim N` citation above
  was verified by re-reading the cited note and locating the numbered heading
  before writing it.
- No contradiction issue filed: `CONTRADICTIONS.md` and the open
  `contradiction`-labeled issues were checked. The o3-mini/o3 naming drift and
  the no-op GPT-5 temperature setting are internal inconsistencies that do not
  oppose a recorded claim or produce different guide advice, so per MINER.md
  §4a they are recorded in the claims, not filed as contradictions.
- `confidence_overall` is `anecdotal`, matching the sibling promptfoo
  model-comparison notes: individual config claims are settled-for-product-
  behavior, but the page carries no measured scores, no sample sizes, no
  cost/latency figures, and its comparison table is `Unknown`-heavy — a vendor
  tutorial template, not evidence.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt after merge. `miner-related-notes.md` was
  read but not committed.
