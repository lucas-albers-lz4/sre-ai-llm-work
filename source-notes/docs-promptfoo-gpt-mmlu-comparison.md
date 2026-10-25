---
source_url: https://www.promptfoo.dev/docs/guides/gpt-mmlu-comparison
source_type: docs
title: "Promptfoo Guides: GPT Model Tiers — MMLU-Pro Benchmark Comparison"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-25
date_extracted: 2026-10-25
last_checked: 2026-10-25
status: current
confidence_overall: anecdotal
issue: "#1740"
---

# Promptfoo Guides: GPT Model Tiers — MMLU-Pro Benchmark Comparison

> A vendor tutorial for comparing OpenAI model *tiers* on a public MMLU-Pro
> dataset, whose reusable artifact is a two-part assertion stack — a literal
> answer-format `regex` plus a `javascript` letter extraction compared to
> `context.vars.answer` — optionally paired with a `latency` budget on the same
> `defaultTest`. Its substantive contribution to the guide is not a model
> ranking but a self-refuting measurement example: the tier verdict depends on a
> user-chosen `limit` over an unpinned live dataset, and the page publishes no
> scores while hedging its only outcome claim.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo's applied "Model
  Comparisons" guide page, `/docs/guides/gpt-mmlu-comparison`, titled "GPT Model
  Tiers: MMLU-Pro Benchmark Comparison")
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of how the vendor would run a public-benchmark tier
  comparison with its own tool — authoritative for *how the config is shaped*,
  but vendor-positioned and evidence-thin: the page publishes **no measured
  scores, no cost figures, no latency measurements, no sample-size
  justification, and no per-category breakdown**. Its models are the
  `gpt-5.4` line (`gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`).
- **Scope**: A four-step tutorial — basic setup with three providers and a
  `defaultTest` assertion pair over `TIGER-Lab/MMLU-Pro`, run/view, a
  chain-of-thought variant adding `max_completion_tokens: 1200` and a `latency`
  assertion, and a sample-size increase (`limit=20 → 100 → 200`) — plus a
  "Understanding Your Results" checklist and next steps. It does **not** cover
  CI wiring, statistical significance, revision pinning, or the `--no-cache`
  precondition the `latency` assertion requires.
- **Last updated**: footer reads "Last updated on **Oct 25, 2026** by
  **renovate\[bot\]**" — a bot-driven stamp on the day of extraction; the page
  carries no human publication date.

## Extracted Claims

### Claim 1: The vendor's stated rationale for MMLU-Pro is that current models are near saturation on classic MMLU and MMLU-Pro's up-to-10 answer options make tier ties less likely — an unquantified methodology assertion
- **Evidence**: The introductory prose only. No saturation numbers, no citation
  to the linked MMLU-Pro paper's results, and no measured per-tier scores on
  the page support the rationale.
- **Confidence**: emerging for the methodology direction (near-saturation on
  MMLU is a widely reported property); the specific claim that full/mini/nano
  are "less likely to tie at a perfect score" on MMLU-Pro is the vendor's
  assertion, not measured here.
- **Quote**: "MMLU-Pro covers a broad set of academic and professional subjects, and it is more useful than classic MMLU when current models are already near saturation on easier multiple-choice benchmarks."
- **Our assessment**: Record as a *reason to pick a harder benchmark*, not as
  evidence about any model. The same paragraph then makes the comparative leap:
  "Running your own MMLU-Pro eval lets you compare reasoning quality, latency,
  and cost on a benchmark where full-size, mini, and nano models are less likely
  to tie at a perfect score." That is a hypothesis the tutorial never tests —
  which is precisely the measurement-validity gap this note records.

### Claim 2: The comparison shape is three OpenAI tiers over one prompt template and one remote test source, with a single `defaultTest` assertion stack serving as the whole gate
- **Evidence**: The Step 1 config (`providers:` = `gpt-5.4`, `gpt-5.4-mini`,
  `gpt-5.4-nano`; one prompt template; one `huggingface://` `tests:` entry) and
  the `defaultTest.assert` block.
- **Confidence**: settled (documented, runnable config)
- **Quote**: "This guide compares full, mini, and nano OpenAI GPT model tiers on MMLU-Pro reasoning tasks using promptfoo."
- **Our assessment**: This is the tier-granularity variant of
  `docs-promptfoo-choosing-best-gpt-model.md` Claim 2's "one prompt + shared test
  set + candidate models" pattern. The delta is the comparison axis (full vs
  mini vs nano of one model line) and the test source (a public benchmark rather
  than own data). The tier comparison itself is not a validated routing method:
  all three providers see the same prompt and the same rows, so this measures
  benchmark accuracy/latency, not the production traffic the tier mapping would
  route.

### Claim 3: The format-compliance check and the correctness check are two distinct assertions — a literal `regex` for the answer sentence, then a `javascript` assertion that extracts the letter, uppercases it, and compares it to `context.vars.answer`
- **Evidence**: The `defaultTest.assert` block in Step 1 (and repeated in Step
  3); the JS body is shown in Concrete Artifacts.
- **Confidence**: settled (documented config; the regex and JS assertion
  primitives are separately documented)
- **Quote**: "Therefore, the answer is [A-J]"
- **Our assessment**: The composition is the genuinely reusable piece. The
  `regex` alone asserts only that the model *ended with the right sentence
  shape*; it would pass an output ending "Therefore, the answer is A" even when
  the correct answer is C. The `javascript` assertion supplies the
  correctness half by reading the benchmark's `answer` column through
  `context.vars`. That makes the pair a model-independent MCQ compliance +
  correctness gate — no judge model in the loop, so it is deterministic in
  promptfoo's sense (`docs-promptfoo-assertions-metrics.md` Claim 10). What the
  pair does *not* fix is input validity: the `answer` it compares against comes
  from the remote dataset row (Claim 6).

### Claim 4: Step 3 pairs the quality gate with an operational budget gate — `max_completion_tokens: 1200` per provider plus `- type: latency, threshold: 60000` on the same `defaultTest` — a quality-and-budget stack on one test case
- **Evidence**: The Step 3 `promptfooconfig.yaml`, which adds per-provider
  `config.max_completion_tokens: 1200` and prepends the `latency` assertion to
  the same `defaultTest.assert` list that carries the regex and JS checks.
- **Confidence**: settled for the config shape; the 60 s threshold is an
  unjustified placeholder (the page offers no measured latency and no rationale
  for 60 000 ms).
- **Quote**: "- type: latency\n      threshold: 60000"
- **Our assessment**: This is the most portable pattern on the page for Ch05's
  canary/model-rollout evaluation: correctness *and* latency on the same row, so
  a tier that is accurate but slow fails the gate. Two caveats the page does not
  state. (a) The `latency` assertion requires `--no-cache` to measure the target
  call at all (`docs-promptfoo-deterministic-metrics.md` Claim 14); this page,
  like the sibling `choosing-best-gpt-model` tutorial, ships the assertion with
  no cache note — a documentation gap, not a contradiction. (b) A reasoning
  prompt with `max_completion_tokens: 1200` plus a 60 s budget is a *coupled*
  gate: raising the token cap to improve accuracy can blow the latency budget,
  so the two thresholds have to be tuned together, and the page never says so.

### Claim 5: The sample-size ladder is a user-chosen `limit` (20 → 100 → 200) presented as "scale your eval", with no sample-size justification, no confidence interval, and no per-category results — so the tier verdict is a function of a knob the reader picks
- **Evidence**: Step 1 `limit=20`, Step 3 `limit=100`, Step 4 `limit=200`; the
  Next Steps bullet recommending larger random subsets; and the complete absence
  of measured accuracy numbers anywhere on the page.
- **Confidence**: settled for the config values; the consequence — that changing
  `limit` can change the verdict — is the Miner's reading of an unpinned random
  subset with no reported variance.
- **Quote**: "Use larger random subsets once your prompt and assertions are stable"
- **Our assessment**: This is the measurement-validity illustration the
  Prospector asked for, and it is stronger than a generic "sample size matters"
  note because the page itself instructs the reader to change the sample size
  *after* the gate is running without saying what result to compare against.
  With no accuracy figure at `limit=20`, `100`, or `200`, the guide cannot tell
  whether a difference between tiers is a capability difference or subset
  noise. The page's own hedge — "though the exact gaps depend on the sample" —
  concedes the point. Treat any MMLU-Pro tier conclusion drawn from this config
  as directional at best, and record the resolved `limit` alongside the result.

### Claim 6: The test source is a live third-party HuggingFace dataset with `split`, `config`, and `limit` set but no revision pin — the tier comparison's inputs can change under the same config
- **Evidence**: The `tests:` line
  `huggingface://datasets/TIGER-Lab/MMLU-Pro?split=test&config=default&limit=20`
  (and its `limit=100` / `limit=200` variants). A full read finds no `revision=`,
  `ref=`, commit, or version parameter anywhere, and the page never mentions
  dataset pinning or snapshotting.
- **Confidence**: settled (absence of a pin on this page, and the loader's
  documented knob surface has no revision slot — see Cross-References)
- **Quote**: "huggingface://datasets/TIGER-Lab/MMLU-Pro?split=test&config=default&limit=20"
- **Our assessment**: This is the concrete Ch05 hermeticity miss. The config
  looks complete and reproducible — `split`, `config`, and `limit` are all
  explicit — but the rows themselves are fetched from a dataset the gate does
  not control, and `limit` caps *how many*, not *which version*. Two runs of the
  same tutorial at different times can evaluate different inputs, so it is a
  cross-tier comparison over a moving reference. The loader mechanics are not
  re-derived here; they are owned by
  `docs-promptfoo-configuration-huggingface-datasets.md` Claims 2, 3, and 5.

### Claim 7: The page reports no results — its only outcome statement is hedged, its "What to Look For" bullets are expectations, and the screenshot is a static asset with no numbers — so it demonstrates the harness without producing evidence about GPT tiers
- **Evidence**: A full read finds no scores, tables, per-category pass rates,
  confidence intervals, or cost figures. The Step 2 prose is the only outcome
  claim and is hedged ("should see", "at least some", "depend on the sample");
  the "Understanding Your Results" section uses "may score higher"; the results
  screenshot is embedded with alt text "GPT benchmark results" and the page
  states only that it shows "side-by-side benchmark pass rates" — no values are
  reproduced in text.
- **Confidence**: settled (observable page content)
- **Quote**: "You should see the full-size GPT tier outperforming the smaller tiers on at least some MMLU-Pro categories, though the exact gaps depend on the sample."
- **Our assessment**: Confirms the Prospector's caveat: do **not** extract
  facts about GPT-5.4 tiers from this page. "You should see" is an expectation,
  not a measurement, and "at least some categories" is unfalsifiable without the
  per-category breakdown the page never gives. For the guide this is a clean
  example of a green-looking eval surface that has not answered the question it
  claims to answer — the accuracy-benchmark counterpart of
  `blog-promptfoo-asr-not-portable-metric.md`'s non-portability thesis.

### Claim 8: The Step 3 chain-of-thought "improvement" is not an isolated variable — it changes the prompt, adds `max_completion_tokens`, adds a latency gate, and doubles the sample size from 20 to 100 at once
- **Evidence**: Comparing the Step 1 and Step 3 configs: a new expert-taker
  prompt, per-provider `config.max_completion_tokens: 1200`, a new
  `latency: 60000` assertion, and `limit=20` → `limit=100`.
- **Confidence**: settled (diffable configs); the consequence — that no
  before/after attribution is possible — follows from the four simultaneous
  changes.
- **Quote**: "You are an expert test taker. Solve this step by step."
- **Our assessment**: Presented as an improvement step, it is actually a
  four-way change with no control arm. If Step 3 scores better than Step 1, the
  page cannot say whether the reasoning prompt, the token budget, the subset
  change, or simply the larger sample did it. This is the same experimental-
  design defect as Claim 5, made worse by the sample-size change being bundled
  with the prompt change. For a Ch05 canary the lesson is concrete: change one
  variable per tier comparison, or the result cannot be attributed to the model.

### Claim 9: The results screenshot is named for a `gpt-5` vs `gpt-5-mini` comparison while the page compares `gpt-5.4` tiers — evidence the page was adapted rather than freshly measured
- **Evidence**: The image embed path
  `/assets/images/gpt-5-vs-gpt-5-mini-mmlu-results-d5d686bdf14272980b3bb89bc8b6870e.jpg`
  against the page's `gpt-5.4` / `gpt-5.4-mini` / `gpt-5.4-nano` providers.
- **Confidence**: settled (observable page content); the inference that the
  screenshot predates the current model line is the Miner's reading of the
  filename.
- **Quote**: (no direct quote; see Our assessment)
- **Our assessment**: Same adaptation smell as
  `docs-promptfoo-choosing-best-gpt-model.md` Claim 7, where the screenshot
  asset still names an earlier model pair. Here the mismatch is `gpt-5` vs
  `gpt-5-mini` in the asset name versus `gpt-5.4` tiers in the config. It is
  not proof the image is wrong, but it is evidence the page's visual result was
  not regenerated for this model line — reinforcing Claim 7's conclusion that
  the page is a harness demo, not a current measurement.

## Concrete Artifacts

### Step 1 config (verbatim from "Step 1: Basic Setup")

```yaml
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
description: GPT model tiers MMLU-Pro comparison
prompts:
  - |
    Question: {{question}}
    {% for option in options -%}
    {{ "ABCDEFGHIJ"[loop.index0] }}) {{ option }}
    {% endfor %}
    End with: Therefore, the answer is <LETTER>.
providers:
  - openai:chat:gpt-5.4
  - openai:chat:gpt-5.4-mini
  - openai:chat:gpt-5.4-nano
defaultTest:
  assert:
    - type: regex
      value: 'Therefore, the answer is [A-J]'
    - type: javascript
      value: |
        const match = String(output).match(/Therefore,\s*the\s*answer\s*is\s*([A-J])/i);
        return match?.[1]?.toUpperCase() === String(context.vars.answer).trim().toUpperCase();
tests:
  - huggingface://datasets/TIGER-Lab/MMLU-Pro?split=test&config=default&limit=20
```

### Step 3 config (verbatim from "Step 3: Improve with Chain-of-Thought")

```yaml
prompts:
  - |
    You are an expert test taker. Solve this step by step.
    Question: {{question}}
    Options:
    {% for option in options -%}
    {{ "ABCDEFGHIJ"[loop.index0] }}) {{ option }}
    {% endfor %}
    Think through this step by step, then provide your final answer as "Therefore, the answer is A."
providers:
  - id: openai:chat:gpt-5.4
    config:
      max_completion_tokens: 1200
  - id: openai:chat:gpt-5.4-mini
    config:
      max_completion_tokens: 1200
  - id: openai:chat:gpt-5.4-nano
    config:
      max_completion_tokens: 1200
defaultTest:
  assert:
    - type: latency
      threshold: 60000
    - type: regex
      value: 'Therefore, the answer is [A-J]'
    - type: javascript
      value: |
        const match = String(output).match(/Therefore,\s*the\s*answer\s*is\s*([A-J])/i);
        return match?.[1]?.toUpperCase() === String(context.vars.answer).trim().toUpperCase();
tests:
  - huggingface://datasets/TIGER-Lab/MMLU-Pro?split=test&config=default&limit=100
```

### Step 4 scale-up (verbatim from "Step 4: Scale Your Eval")

```yaml
tests:
  - huggingface://datasets/TIGER-Lab/MMLU-Pro?split=test&config=default&limit=200
```

### Quick start and prerequisites (verbatim)

```bash
npx promptfoo@latest init --example compare-gpt-model-tiers-mmlu-pro
```

```bash
cd compare-gpt-model-tiers-mmlu-pro
```

```bash
export HF_TOKEN=your_token_here
```

```bash
npx promptfoo@latest eval
```

```bash
npx promptfoo@latest view
```

### Results screenshot asset (from the Step 2 embed)

```
/assets/images/gpt-5-vs-gpt-5-mini-mmlu-results-d5d686bdf14272980b3bb89bc8b6870e.jpg
```

Source for all artifacts:
https://www.promptfoo.dev/docs/guides/gpt-mmlu-comparison — sections as noted.
YAML and shell blocks copied from the rendered page; line breaks lost in HTML
extraction were restored at YAML/shell boundaries with no wording changes.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-configuration-huggingface-datasets.md`
    **Claim 2** (the loader's complete knob surface is `split` / `config` /
    `limit` with **no revision pin**) and **Claim 3** (`limit` is the only
    volume cap; rows arrive over a live `/rows` fetch) — this page is a worked
    instance of both: it sets `split=test&config=default&limit=20` and has no
    pin, so the dataset is a mutable reference (Claim 6 here). **Claim 5**
    (`split`/`config` defaults can yield an empty suite) is the loader-side
    fail-open trap this page avoids by setting both explicitly — cited to show
    the config here is *more* explicit than the loader default, not to repeat
    the trap. (Verified: #1526 Claims 2, 3, 5.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 14**
    ("Note that `latency` requires that the [cache is disabled](/docs/configuration/caching/) with `promptfoo eval --no-cache` or an equivalent option.")
    — the Step 3 latency gate needs this precondition, and the
    page omits it, exactly as the sibling `choosing-best-gpt-model` tutorial
    omits it for `cost`/`latency` (its Claim 6). This note records the omission
    as a documentation gap, not a contradiction. (Verified: #1289 Claim 14.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (the
    assertion surface splits into a deterministic/programmatic family and a
    model-assisted family) — the regex + `javascript` pair is entirely in the
    deterministic family, so the *assertions* are replayable even though the
    *inputs* are not (Claim 6 here). (Verified: #1287 Claim 10.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 1** (the JS
    assertion's return semantics) and **Claim 5** (`context.vars` is part of the
    injected assertion context) — the letter-match assertion is a plain JS
    assertion returning a boolean and reading the benchmark answer from
    `context.vars.answer`; both are documented primitive behavior, not new here.
    (Verified: #1304 Claims 1 and 5.)

- **Contradicts**: None identified; no contradiction issue filed. The closest
  surface is `docs-promptfoo-choosing-best-gpt-model.md` **Claim 1**
  ("public leaderboard scores are inadequate for app decisions … evaluate these
  models on your own data"). This page instead runs a *public benchmark*.
  That is a conditioning difference, not a contradiction: both pages tell the
  reader to run their own eval, and this one's benchmark is a self-run eval over
  MMLU-Pro rather than a consumed leaderboard. Per MINER.md §4a (context
  differences are not contradictions) no issue was filed. Checked
  `CONTRADICTIONS.md` and the open `contradiction`-labeled issues before
  concluding.

- **Extends**:
  - `source-notes/docs-promptfoo-choosing-best-gpt-model.md` **Claim 2** (the
    "candidate models × one prompt × shared test set, assertions encode the
    decision" pattern) and **Claim 7** (thin/adapted evidence — placeholder
    thresholds, no measured scores, screenshot named for an earlier model pair).
    This page is the same tutorial shape with two deltas: the comparison axis is
    model *tier* (full/mini/nano) and the test source is a public benchmark
    rather than own data. Its Claim 7 evidence smell recurs here (Claim 9).
    (Verified: #1655 Claims 2, 7.)
  - `source-notes/docs-promptfoo-configuration-huggingface-datasets.md` — the
    loader reference this page assumes. The extension is the *applied* use:
    a benchmark tier gate over HF rows, with the sample-size ladder as the
    coverage knob. No loader mechanics are re-extracted (Claim 6 here defers to
    Claims 2/3/5 there).
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** and
    `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 1** — the
    assertion types are documented there; the MCQ format-compliance + correctness
    *composition* is the delta here.

- **Novel**:
  1. **The MCQ format-compliance + correctness assertion pair** (Claim 3) — a
     literal answer-sentence `regex` plus a `javascript` letter extraction
     compared to `context.vars.answer`. This is a distinct deterministic
     composition, not a rerun of the free-text `llm-rubric` / `contains`
     patterns already in the corpus.
  2. **Quality + operational budget stacked on one `defaultTest`** (Claim 4) —
     accuracy assertions and a `latency` threshold on the same row, as a
     CI-shaped tier-rollout gate.
  3. **A public-benchmark-as-tier-gate shape** (Claims 1–2) — comparing model
     tiers on a third-party benchmark rather than own data.
  4. **A self-refuting measurement example** (Claims 5–8) — a tutorial whose
     verdict depends on a user-chosen `limit` over an unpinned dataset, which
     bundles a sample-size change with a prompt change, and which publishes no
     numbers while hedging its only outcome claim. This is the accuracy-
     benchmark counterpart of the ASR non-portability argument.

## Guide Impact

- **Chapter 05 — §"Metrics without a unit are noise"
  (`guide/05-llm-ops-reliability.md:388`)**: Add the public-benchmark tier
  comparison as a second unit-less metric alongside ASR. A tier verdict read
  off a `limit=20/100/200` random subset of an unpinned dataset has no
  uncertainty attached and no fixed input version, so "tier X beats tier Y"
  is not a portable result. Recommend the guide state: **a benchmark-derived
  model-tier comparison must report the resolved sample size, the dataset
  revision (or a committed fixture), and per-category results before it can
  inform a routing decision** [source: docs-promptfoo-gpt-mmlu-comparison,
  Claims 5–7].
- **Chapter 05 — §"A generated dataset is the mutable external reference"
  (`guide/05-llm-ops-reliability.md:216`)**: The remote-import case is already
  carried by `docs-promptfoo-configuration-huggingface-datasets.md`; add this
  page only as the *worked benchmark example*: even an explicit
  `split=test&config=default&limit=20` is not a pin, so the fixture discipline
  (`file://`) applies to public benchmark gates too [source:
  docs-promptfoo-gpt-mmlu-comparison, Claim 6].
- **Chapter 05 — §"Read the assert's own defaults before trusting its verdict"
  (`guide/05-llm-ops-reliability.md:443`)**: The `latency` assertion in Step 3
  is shipped without the `--no-cache` precondition it requires
  [source: docs-promptfoo-gpt-mmlu-comparison, Claim 4], another vendor
  tutorial in this family to do so. Extend the existing cache note rather than
  adding a new rule: budget assertions measure fresh inference only with
  `--no-cache`.
- **Chapter 05 — §"Routing decisions are cost decisions"
  (`guide/05-llm-ops-reliability.md:1028`)**: This page is *not* evidence for a
  capability-class → tier mapping. It supplies a config shape for testing a
  mapping (deterministic correctness + latency on one row), not a validated
  mapping. Recommend citing it only for the gate skeleton, explicitly not for
  the `gpt-5.4` tier outcome [source: docs-promptfoo-gpt-mmlu-comparison,
  Claims 2–4, 7].

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/gpt-mmlu-comparison). Single
  self-contained tutorial page; no sub-pages followed — every linked page
  (HuggingFace `TIGER-Lab/MMLU-Pro`, `/docs/providers/openai/`,
  `/docs/guides/gpt-vs-claude-vs-gemini/`, the MMLU-Pro arXiv paper) is already
  covered in the corpus or is a dataset/paper reference, and the tutorial
  introduces no new mechanism on them.
- **Dedupe followed per the Prospector's three triage comments**: this note does
  NOT re-extract the HF loader (`split`/`config`/`limit`, `/rows` pagination,
  no revision pin — owned by `docs-promptfoo-configuration-huggingface-datasets.md`),
  the `regex`/`javascript`/`latency` primitive semantics (owned by
  `docs-promptfoo-deterministic-metrics.md` and
  `docs-promptfoo-javascript-assertions.md`), or the tier-comparison tutorial
  shape and thin-evidence pattern (owned by
  `docs-promptfoo-choosing-best-gpt-model.md`). The intended delta is the
  applied gate composition and the measurement-validity illustration.
- **No GPT tier facts extracted.** Per the triage caveat, Claims 1 and 7
  deliberately record the vendor's comparative statements as hedged expectations
  and publish no ranking. The page has no scores, cost figures, or latency
  measurements.
- Quotes were checked character-for-character against the fetched rendered
  content; YAML/shell blocks are the page's own artifacts with line breaks
  restored at config boundaries. Claim 4's quote is the contiguous
  `type: latency` / `threshold: 60000` pair from the Step 3 config.
- **Contradiction handling**: no contradiction issue filed. The only candidate
  (public benchmark here vs own-data in `choosing-best-gpt-model` Claim 1) is a
  conditioning difference, which MINER.md §4a excludes. Verified against
  `CONTRADICTIONS.md` and the open `contradiction`-labeled issues.
- **Cross-reference verification (MINER.md §4b)**: every `Claim N` above was
  re-read in the cited note before writing — #1526 Claims 2, 3, 5; #1289
  Claim 14; #1287 Claim 10; #1655 Claims 2, 7; and #1304 Claims 1 and 5.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; all ten lexical candidates are suggestions only):
  - `docs-litellm-evals-api.md` — LiteLLM server-side eval CRUD; different
    vendor and object (stored completions), no benchmark/HF-loader overlap;
    dismissed.
  - `docs-promptfoo-enterprise-findings-reports.md` — red-team findings export
    and disposition; no eval-methodology overlap; dismissed.
  - `docs-promptfoo-llm-rubric.md` — model-graded rubric (incl. audio); this
    page uses no judge at all; dismissed.
  - `docs-google-sre-reliable-product-launches.md` — Google launch-process
    chapter; no LLM-eval content; dismissed.
  - `docs-promptfoo-model-graded-metrics.md` — judge selection/precedence; the
    MCQ gate here is judge-free; dismissed.
  - `docs-promptfoo-enterprise-guardrails.md` — runtime guardrail enforcement;
    no eval-harness overlap; dismissed.
  - `docs-promptfoo-evaluate-openai-agents-python.md` — agent tracing/trajectory
    bridge; different eval surface; dismissed.
  - `docs-litellm-batches-api.md` — batch rate-limit accounting; unrelated
    vendor and topic; dismissed.
  - `docs-promptfoo-agent-skill.md` — agent-authored config taxonomy; mentions
    deterministic-first but carries no MMLU/tier-gate content; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — AI incident triage; no eval-harness
    overlap; dismissed.
  - The strongest cross-refs (`docs-promptfoo-configuration-huggingface-datasets.md`,
    `docs-promptfoo-choosing-best-gpt-model.md`,
    `docs-promptfoo-deterministic-metrics.md`,
    `docs-promptfoo-assertions-metrics.md`,
    `docs-promptfoo-javascript-assertions.md`) were found by searching
    `source-notes/` and the Prospector's overlap list, not by the lexical
    retrieval file.
- `confidence_overall` is `anecdotal`: the config claims (2–4, 6, 8–9) are
  settled documented behavior, but the page's substantive content — the tier
  comparison and its outcome — has no measurements, no sample-size
  justification, an unpinned input, and a hedged conclusion. This matches the
  sibling `docs-promptfoo-choosing-best-gpt-model.md` grade.
- `date_published` uses the page's "Last updated on Oct 25, 2026 by
  renovate\[bot\]" footer (the prose page carries no publication date);
  `date_extracted` and `last_checked` are today's UTC date.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited; they
  are derived indexes rebuilt after merge.
