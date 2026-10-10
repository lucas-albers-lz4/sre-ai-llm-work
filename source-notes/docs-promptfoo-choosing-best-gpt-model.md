---
source_url: https://www.promptfoo.dev/docs/guides/choosing-best-gpt-model
source_type: docs
title: "Promptfoo Guides: Choosing the Best GPT Model — Benchmark on Your Own Data"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-10
date_extracted: 2026-10-10
last_checked: 2026-10-10
status: current
confidence_overall: anecdotal
issue: "#1655"
---

# Promptfoo Guides: Choosing the Best GPT Model

> A vendor tutorial that applies promptfoo's assertion machinery to a
> named **own-data model-selection** decision — two candidate OpenAI models
> against one prompt template and a three-riddle test set, with `cost` and
> `latency` thresholds used as pre-rollout budget gates — whose genuinely
> corpus-new delta is narrow: the applied framing, plus a documented
> **omission** of the `--no-cache` precondition that `cost`/`latency`
> assertions require (contrast `docs-promptfoo-deterministic-metrics.md`
> Claims 6 and 14), which the page presents as a straightforward selection
> gate.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo's applied
  "Model Comparisons" guide page, `/docs/guides/choosing-best-gpt-model`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of how the vendor would run an own-data model
  comparison with its own tool — authoritative for *how promptfoo configures
  a comparison*, but vendor-positioned and, per the Prospector, evidence-thin:
  the page carries **no measured benchmark scores, no sample sizes, no
  failure rates, and no independent validation**. Its thresholds are
  placeholder budgets (0.001–0.002 USD; 3000–5000 ms) over three riddles, and
  the page itself calls the test set "limited".
- **Scope**: A five-step tutorial plus a cleanup step and a conclusion:
  setup (`providers`), a prompt template, three test cases, an
  `npx promptfoo@latest eval` run, per-test `cost`/`latency`/`contains`/
  `llm-rubric` assertions, and a `defaultTest` block hoisting global
  `cost`/`latency` limits. It does NOT cover CI wiring, statistical rigor,
  judge selection/pinning, or the cache preconditions the assertion types
  require. Model names on the page are `openai:gpt-5-mini` and
  `openai:gpt-5.2`; the screenshot asset is still named for an earlier
  gpt-4o-mini/gpt-4o comparison (see Claim 7), i.e. the page was adapted
  rather than freshly measured.
- **Last updated**: footer reads "Last updated on **Oct 10, 2026** by
  **mldangelo-oai**" — same day as extraction.

## Extracted Claims

### Claim 1: The page's stated methodology is that public leaderboard scores are inadequate for app decisions and teams should benchmark candidate models on their own data
- **Evidence**: The opening framing paragraph, stated as a general
  recommendation; the whole tutorial is the worked form of it. No measured
  support is offered for the recommendation itself.
- **Confidence**: emerging (a reasonable vendor methodology claim, not a
  measured one — it is advice, and the page's own example is explicitly
  illustrative)
- **Quote**: "New model releases often score well on benchmarks. But generic benchmarks are for generic use cases. If you're building an LLM app, you should evaluate these models on your own data and make an informed decision based on your specific needs."
- **Our assessment**: Buy the direction, keep the evidence grade low: this is
  a vendor restating the corpus's existing measurement-portability thesis
  (`blog-promptfoo-asr-not-portable-metric.md`) as a how-to. The contribution
  is the *applied* shape (a runnable comparison config), not the claim. The
  page supplies no gate-failure rate, no drift figure, and no data on whether
  the own-data test actually discriminated the two models.

### Claim 2: The model-selection pattern is "one prompt template + a small shared test set + candidate models", with assertions — not leaderboards — encoding the decision criteria
- **Evidence**: The Step 1–3 config blocks (two `providers`, one prompt
  `'Solve this riddle: {{riddle}}'`, one `{{riddle}}` var per test case) and
  the Step 5 framing sentence.
- **Confidence**: settled (documented, runnable config); the *sufficiency* of
  a three-case set is not claimed by the vendor
- **Quote**: "In this case, we're especially interested in `cost` and `latency` assertions given the tradeoffs between the two models:"
- **Our assessment**: This is the applied model-selection-as-eval-pipeline
  pattern the Prospector flagged. It is a genuine corpus delta in *form*
  (the config), but every building block is already documented:
  `contains`/`llm-rubric`/`cost`/`latency` primitives
  (`docs-promptfoo-deterministic-metrics.md`), the scoring/aggregation model
  (`docs-promptfoo-assertions-metrics.md`), and `defaultTest` inheritance
  (`docs-promptfoo-configuration-guide.md`). Extract the pattern; do not
  re-derive the primitives.

### Claim 3: Per-test `cost` and `latency` thresholds are used as the selection gate, with model-specific budget caps that differ across the three riddle cases
- **Evidence**: The Step 5 assertion config: case 1 `cost: 0.001` /
  `latency: 5000`; case 2 `cost: 0.002` / `latency: 3000`; case 3
  `cost: 0.0015` / `latency: 4000` (see Concrete Artifacts).
- **Confidence**: settled (documented config); thresholds are arbitrary
  placeholders with no justification on the page
- **Quote**: "Make sure the LLM output contains this word" and
  "# Inference should always cost less than this (USD)" and
  "# Inference should always be faster than this (milliseconds)" (the config
  comments attached to the `contains`, `cost`, and `latency` assertions)
- **Our assessment**: Buy the mechanism — a per-test cost/latency cap is a
  real budget gate, the deterministic-tier primitive documented at
  `docs-promptfoo-deterministic-metrics.md` Claim 6 (cost) and Claim 14
  (latency). But the page presents it as a straightforward selection gate
  **without the `--no-cache` precondition** those claims require (this note's
  Claim 6), and without justifying any threshold value — so it is an
  illustration, not a calibration.

### Claim 4: `defaultTest` is used to hoist global `cost`/`latency` limits so they apply to every test case, replacing the per-case caps
- **Evidence**: The "Cleanup" step prose and the final `promptfooconfig.yaml`
  (see Concrete Artifacts): a `defaultTest.assert` block with `cost: 0.001`
  and `latency: 3000`, while the per-test `cost`/`latency` assertions are
  removed and only `contains`/`llm-rubric` remain per case.
- **Confidence**: settled (documented config behavior — `defaultTest.assert`
  is inherited by every case)
- **Quote**: "Finally, we'll use `defaultTest` to clean things up a bit and apply global `latency` and `cost` requirements."
- **Our assessment**: The cleanup is a legitimate use of `defaultTest.assert`
  inheritance, but note *what changed*: the final config gates **every** case
  at the tighter 3000 ms / 0.001 USD global cap, and the per-case caps from
  Step 5 are gone. The defaultTest inheritance mechanism itself is already
  documented at `docs-promptfoo-configuration-guide.md` Claim 6 (a case
  inherits `defaultTest.assert` unless it sets
  `options.disableDefaultAsserts`), and its global-override-not-compose
  semantics for transforms are Claim 1/2 there. The tutorial adds no new
  inheritance semantics.

### Claim 5: In the vendor's own result, output quality did not separate the models — the `cost`/`latency` gate did: identical answers, GPT-5.2 over the latency cap and more expensive
- **Evidence**: The Conclusion section, which describes the outcome in prose
  (no numeric scores or per-case table are given; both images point at the
  same asset filename).
- **Confidence**: anecdotal (illustrative vendor narrative over a three-riddle
  set; no measurements, sample sizes, or reproducibility data)
- **Quote**: "In this particular eval, the models performed very similarly in terms of answers, but it looks like GPT-5.2 exceeded our maximum latency. Notably, GPT-5.2 was more expensive compared to GPT-5-mini."
- **Our assessment**: This is the one operationally interesting observation:
  the binding constraint on an upgrade was a **budget assertion**, not a
  quality difference. It is exactly the "a cost/latency assertion is the
  binding constraint on a model upgrade" case the Prospector asked to
  capture — but it must be labelled illustrative, not benchmarking evidence:
  the tests are three riddles, "the models performed very similarly in terms
  of answers" is asserted without a single score, and the page's own
  `llm-rubric`/`contains` asserts are the only quality checks.

### Claim 6: The tutorial presents `cost`/`latency` thresholds as a straightforward selection gate but omits the `--no-cache` precondition that both assertion types require — a cross-page documentation gap
- **Evidence**: A full read of the page finds **no mention of `--no-cache`,
  caching, or fresh-inference measurement** anywhere. The requirement is
  documented elsewhere in the corpus: `docs-promptfoo-deterministic-metrics.md`
  Claim 6 ("Use `--no-cache` when comparing fresh inference costs") and
  Claim 14 ("`latency` requires that the cache is disabled … with
  `promptfoo eval --no-cache`").
- **Confidence**: settled (the omission is verifiable by full-page read; the
  requirement it omits is documented product behavior)
- **Quote**: (no direct quote; see Our assessment — the page contains no
  `--no-cache`, `cache`, or "fresh" string)
- **Our assessment**: This is the only durable *delta* the Prospector's third
  triage comment asked the Miner to confirm, and it is confirmed: the tutorial
  teaches `cost`/`latency` gating **without** the cache opt-out those
  assertions need to measure the target call at all. A reader who copies the
  config verbatim and runs `npx promptfoo@latest eval` over a warm 14-day
  cache is gating on replayed figures, not on the candidate models' fresh
  cost/latency — the very failure class `docs-promptfoo-configuration-caching.md`
  Claim 8 and `docs-promptfoo-deterministic-metrics.md` Claims 6/14 document.
  This is a **documentation gap, not a contradiction**: the vendor's own
  reference page states the requirement, and this guide page is silent on it.
  Per MINER.md §4a no contradiction issue is filed (an omission does not
  oppose a recorded claim).

### Claim 7: The evidence base is thin and the page shows signs of adaptation rather than fresh measurement — three-riddle test set, placeholder thresholds, a "limited example" disclaimer, and a screenshot asset still named for a gpt-4o-mini/gpt-4o comparison
- **Evidence**: The three riddle test cases; the arbitrary budget values
  (0.001/0.0015/0.002 USD, 3000/4000/5000 ms); the explicit conclusion
  disclaimer; and the screenshot path
  `/assets/images/gpt-4o-mini-vs-gpt-4o-9306cf27978e297122c6bcf25ab881c0.png`
  (alt text reads "gpt-5-mini vs gpt-5.2") used for both the pre-run and
  post-run image.
- **Confidence**: settled (observable page content)
- **Quote**: "Of course, this is a limited example test set. The tradeoff between cost, latency, and accuracy is going to be tailored for each application. That's why it's important to run your own eval."
- **Our assessment**: Confirms the Prospector's low-novelty verdict. The asset
  filename retains an earlier gpt-4o-mini/gpt-4o comparison, so the images a
  reader sees were not generated by the current gpt-5.2/gpt-5-mini run — the
  page was adapted, not re-measured. Treat every number here as a
  placeholder, and do not cite the page for GPT-5.2-vs-GPT-5-mini outcomes.

### Claim 8: The tutorial mixes a deterministic `contains` check with a model-graded `llm-rubric` on the same test case, and the `llm-rubric` assertions omit an explicit threshold
- **Evidence**: The Step 5 config: case 1 has `contains: echo` plus
  `llm-rubric: Do not apologize`; case 2 has `llm-rubric: explains that the
  people are below deck`; both with no `threshold`.
- **Confidence**: settled (documented config); the consequence is documented in
  another note
- **Quote**: "# Use model-graded assertions to enforce free-form instructions"
- **Our assessment**: A clean illustration of the deterministic/model-graded
  split (`docs-promptfoo-assertions-metrics.md` Claim 10) and of a footgun the
  page does not flag: an `llm-rubric` with no explicit `threshold` is
  score-blind — PASS depends only on the grader's `pass` field, defaulting to
  true when omitted (`docs-promptfoo-model-graded-metrics.md` Claim 10). So
  half of this "selection gate" is a budget cap (deterministic) and half is a
  judge-defaulted rubric with no quality bar. The tutorial never notes either
  property.

## Concrete Artifacts

### Per-test assertion config (verbatim from Step 5, "Automatic evaluation")

```yaml
tests:
  - vars:
      riddle: 'I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?'
    assert:
      # Make sure the LLM output contains this word
      - type: contains
        value: echo
      # Inference should always cost less than this (USD)
      - type: cost
        threshold: 0.001
      # Inference should always be faster than this (milliseconds)
      - type: latency
        threshold: 5000
      # Use model-graded assertions to enforce free-form instructions
      - type: llm-rubric
        value: Do not apologize
  - vars:
      riddle: 'You see a boat filled with people. It has not sunk, but when you look again you don’t see a single person on the boat. Why?'
    assert:
      - type: cost
        threshold: 0.002
      - type: latency
        threshold: 3000
      - type: llm-rubric
        value: explains that the people are below deck
  - vars:
      riddle: 'The more of this there is, the less you see. What is it?'
    assert:
      - type: contains
        value: darkness
      - type: cost
        threshold: 0.0015
      - type: latency
        threshold: 4000
```

### Final config after "Cleanup" (verbatim) — global `defaultTest` cost/latency limits

```yaml
providers:
  - openai:gpt-5-mini
  - openai:gpt-5.2
prompts:
  - 'Solve this riddle: {{riddle}}'
defaultTest:
  assert:
    # Inference should always cost less than this (USD)
    - type: cost
      threshold: 0.001
    # Inference should always be faster than this (milliseconds)
    - type: latency
      threshold: 3000
tests:
  - vars:
      riddle: "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?"
    assert:
      - type: contains
        value: echo
  - vars:
      riddle: "You see a boat filled with people. It has not sunk, but when you look again you don’t see a single person on the boat. Why?"
    assert:
      - type: llm-rubric
        value: explains that the people are below deck
  - vars:
      riddle: "The more of this there is, the less you see. What is it?"
    assert:
      - type: contains
        value: darkness
```

### Setup and run commands (verbatim)

```bash
mkdir gpt-comparison
cd gpt-comparison
```

```bash
npx promptfoo@latest eval
```

```bash
npx promptfoo@latest view
```

### Screenshot asset still named for the previous comparison (from both image embeds)

```
/assets/images/gpt-4o-mini-vs-gpt-4o-9306cf27978e297122c6bcf25ab881c0.png
```

Alt text on both embeds reads "gpt-5-mini vs gpt-5.2"; the filename references
the earlier gpt-4o-mini/gpt-4o pairing.

Source for all artifacts: https://www.promptfoo.dev/docs/guides/choosing-best-gpt-model — sections as noted. Copied character-for-character from the rendered page, including the config comments.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 6** (the
    `cost` assertion "requires the provider to return cost information" and
    "Use `--no-cache` when comparing fresh inference costs") and **Claim 14**
    (`latency` "requires that the cache is disabled … with `promptfoo eval
    --no-cache`") — these are the primitive semantics this tutorial uses. The
    tutorial *uses* the assertions without restating the precondition, which
    is this note's Claim 6 (documentation gap). (Verified: #1289 Claims 6, 14,
    read in full.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (the
    deterministic vs model-assisted assertion split, incl. the `not-`
    negation and `is-refusal` framing) — the tutorial's mix of `contains` +
    `llm-rubric` on one case is a literal instance of that split. (Verified:
    #1287 Claim 10.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 10**
    (`llm-rubric` pass/fail "is score-blind without a `threshold`" — PASS
    depends only on the grader's `pass` field, defaulting to true) — the
    tutorial's two `llm-rubric` asserts omit `threshold`, so the behavior that
    claim documents applies to them. (Verified: #1305 Claim 10.)

- **Contradicts**: None identified, and no contradiction issue filed. This is a
  first-party tutorial; it opposes no existing source-note claim. Checked
  `CONTRADICTIONS.md` and the open `contradiction`-labeled issues. The closest
  surface is the `--no-cache` omission (Claim 6), which is a **documentation
  gap**, not a conflict: `docs-promptfoo-deterministic-metrics.md` Claims 6/14
  state the requirement, and this page is merely silent on it — an omission
  does not oppose a recorded claim, so per MINER.md §4a no issue is warranted.

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 6**
    (`defaultTest.assert` is inherited by every test case unless a case sets
    `options.disableDefaultAsserts`) — the tutorial's Cleanup step depends on
    exactly this inheritance to hoist global cost/latency limits onto all
    cases (Claim 4 here). The config guide supplies the semantics; this page is
    the applied usage. (Verified: #1513 Claim 6.)
  - `source-notes/docs-promptfoo-select-best.md` **Claim 3** (`select-best`
    documents no `threshold`/`method`/`weights`, only a criterion `value:`) and
    `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 14**
    (comparison types: "`select-best` picks a winner across prompts in one row
    by a criterion") — the tutorial is the corpus's model-selection
    *counter-example*: it selects between **candidate models** using
    cost/latency assertions rather than using promptfoo's own comparison
    assertion. Useful for the guide to distinguish "compare models with budget
    gates" from "rank outputs with `select-best`". (Verified: #1497 Claim 3;
    #1305 Claim 14.)

- **Novel**: Deliberately small, as the Prospector anticipated. New to the
  corpus:
  1. **The applied own-data model-selection pattern** as a runnable config —
     two candidate models, one prompt template, a shared test set, and
     `cost`/`latency` thresholds as the selection gate (Claims 2–5). The
     primitives already exist in the corpus; the *worked selection config* does
     not.
  2. **The confirmed `--no-cache` omission** (Claim 6) — the one durable
     finding: the vendor's applied guide teaches budget gating without the
     cache precondition its own reference page requires. Recorded as a
     cross-page documentation gap, not a contradiction.
  3. **A concrete "the budget gate, not quality, drove the upgrade" anecdote**
     (Claim 5), explicitly flagged as illustrative — do not extract the
     GPT-5.2-vs-mini outcome as benchmarking evidence.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — §Evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md:386`)**: the own-data model-selection
  framing (Claim 1) is a citable restatement of the section's existing thesis,
  not a new recommendation. Optional one-line addition: an own-data eval is the
  documented way to make a model-swap decision, and the page's worked pattern
  is candidate models × one prompt × a small test set with budget asserts
  [source: docs-promptfoo-choosing-best-gpt-model, Claims 2–4].
- **Chapter 05 — §"A green eval is not evidence until you can name what it
  measured" (`guide/05-llm-ops-reliability.md:567`)**: add the
  `cost`/`latency` budget-gate cache coupling to the existing caching
  paragraph. The section already cites `--no-cache`/`--repeat` for variance
  runs (from `docs-promptfoo-configuration-caching.md` Claim 8); extend it
  with "budget asserts (`cost`, `latency`) require `--no-cache` to measure the
  target call at all — a vendor model-selection tutorial ships those asserts
  with no cache note [source: docs-promptfoo-choosing-best-gpt-model, Claim 6]."
  This is the section's third documented route to a green result measured on
  the wrong thing.
- **Chapter 05 — §"A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: optional footnote. The tutorial's
  `llm-rubric` asserts carry no `threshold` (Claim 8), so half the "selection
  gate" is governed by the judge-pass default already listed in the table's
  `llm-rubric` row [source: docs-promptfoo-choosing-best-gpt-model, Claim 8].
  No new row needed.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/choosing-best-gpt-model). Single
  self-contained tutorial page; no sub-pages followed — every linked page
  (`/docs/installation/`, `/docs/providers/openai/`,
  `/docs/configuration/expected-outputs/`, `/docs/configuration/guide/`,
  `/docs/getting-started/`) is an already-mined corpus surface, and the
  tutorial introduces no new mechanism on them.
- **Dedupe handled per Prospector guidance**: this note deliberately does NOT
  re-extract the `cost`/`latency`/`contains`/`llm-rubric` primitives (owned by
  `docs-promptfoo-deterministic-metrics.md` and `docs-promptfoo-model-graded-metrics.md`),
  the `defaultTest` inheritance semantics (owned by
  `docs-promptfoo-configuration-guide.md`), or the comparison-assert family
  (`docs-promptfoo-select-best.md`). Claims 2–4/8 are the *applied usage*; the
  only durable delta is Claim 6 (the `--no-cache` omission).
- **`--no-cache` gap confirmed by re-reading both pages**: the tutorial page
  contains no `--no-cache`/`cache` string; the deterministic-metrics note
  documents the requirement for both `cost` (Claim 6) and `latency`
  (Claim 14). Recorded as a documentation gap (Claim 6), not a contradiction.
- Quotes verified character-for-character against the fetched rendered
  content before writing; the two YAML blocks and the shell commands are the
  page's own artifacts, copied verbatim including inline config comments.
  Curly apostrophes in the riddle text (e.g. "don't") are preserved as they
  appear on the page.
- **Candidate dismissal** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-promptfoo-deterministic-metrics.md` — **cited** (Corroborates,
    Claims 6/14) for the `cost`/`latency` `--no-cache` preconditions this
    tutorial omits.
  - `docs-promptfoo-llm-rubric.md` — the per-type reference for the
    `llm-rubric` assert used here; its audio/default-judge material is not
    exercised by this page; **cited indirectly** via
    `docs-promptfoo-model-graded-metrics.md` Claim 10 (which owns the
    no-threshold pass default). Dismissed as a direct citation only because
    the tutorial's rubrics invoke none of that note's delta surfaces.
  - `blog-promptfoo-red-team-claude.md` — red-team plugin config; uses
    latency/threshold asserts as a tool but carries no selection/gating
    semantics; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — AI-incident triage by an SRE
    Agent; no eval-selection surface; dismissed.
  - `docs-litellm-batches-api.md`, `docs-litellm-completion-function-call.md`
    — LiteLLM batch rate-limit and function-call docs; unrelated vendor and
    topic; dismissed.
  - `docs-google-sre-team-lifecycles.md`, `docs-google-sre-reliable-product-launches.md`
    — Google SRE book/workbook chapters (team org, launch process); no
    LLM-eval content; dismissed.
  - `docs-promptfoo-enterprise-findings-reports.md`, `docs-promptfoo-pi-scorer.md`
    — enterprise findings export and the third-party Pi scorer; no overlap with
    this tutorial's own-data selection pattern; dismissed.
- No contradiction issue filed: verified against `CONTRADICTIONS.md` and the
  open `contradiction`-labeled issues. The `--no-cache` finding is an omission
  (documentation gap), which per MINER.md §4a does not rise to a contradiction.
- `confidence_overall` is `anecdotal`, lower than the sibling promptfoo config
  notes' `emerging`: the individual config claims are settled-for-product-
  behavior, but the page's substantive content (which model to pick, what the
  result shows) rests on a three-riddle illustrative set with placeholder
  thresholds, no measured scores, and an adapted screenshot — a vendor tutorial
  example, not a reference catalog.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt after merge.
