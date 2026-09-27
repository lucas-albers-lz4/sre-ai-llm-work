---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/max-score
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Max Score"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-26
date_extracted: 2026-09-26
last_checked: 2026-09-26
status: current
confidence_overall: emerging
issue: "#1472"
---

# Promptfoo Configuration: Model-Graded — Max Score

> The per-type vendor reference for promptfoo's `max-score` assertion — the
> page that closes the #1305 hub note's explicit "max-score was not
> followed" gap.
> It documents an assertion that is filed under **Model-graded metrics** in the
> nav but makes **no LLM call at all**: it collects the scores the other
> assertions in the row already produced and picks a winner arithmetically
> (`sum(score × weight) / sum(weights)` by default, `sum(score × weight)` under
> `method: sum`). The load-bearing finding for gate design is its **pass
> semantics**: exactly one output per row reports `pass=true` — the highest
> scorer, even when *"All outputs fail: Still selects the highest scorer
> ('least bad')"* — so a `max-score` gate is a **ranker, not a quality bar**,
> and its weights are keyed by *assertion type* ("Weights apply to all
> assertions of that type"), so individual assertions cannot be weighted.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Max Score"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `max-score` behavior — authoritative for *what promptfoo does*
  with a given config (the aggregation formulas, the weight-map granularity, the
  per-output pass flags, the edge cases, the tie-break), but vendor-positioned:
  the page carries no measured gate-failure-rate, cost, drift, or calibration
  figures and there is no independent practitioner validation. Everything below
  is checkable against an installed CLI. The headline hazard (Claim 2) is
  recorded as **documented product behavior**, not as a measured failure rate.
- **Scope**: A single self-contained reference page — When to use max-score, How
  it works, Basic usage, Configuration options (Aggregation method, Weighted
  scoring / How weights work, Minimum threshold), Scoring details, three
  Examples, the Comparison-with-`select-best` table, Edge cases, Tips, Further
  reading. It is the per-type deep-dive on the `max-score` member of the
  comparison-assert family that `docs-promptfoo-model-graded-metrics.md` (#1305)
  catalogued at claim level only; that note's Extraction Notes explicitly
  record `max-score` among the sub-pages that were not followed. This page
  therefore
  carries the *delta* (the `method`/`weights`/`threshold` schema, the
  per-output pass flags, the four edge cases, the `select-best` table), not a
  re-extraction of the model-graded framing. Does NOT cover the `select-best`
  page itself, nor any measured property of the aggregated scores' provenance.
  The "Further reading" links (hub page, `select-best`, assertions) were
  cross-referenced against existing notes, not re-followed, per the
  one-note-per-sub-page convention.
- **Last updated**: the page footer reads "Last updated on **Sep 26, 2026** by
  **mldangelo-oai**" — same-day as extraction; the examples describe the current
  `gpt-5` / `claude-haiku-4-5` era.
- **Taxonomy note**: the sidebar files this page under "Model-graded metrics",
  but the page's own opening sentence and its comparison table place the
  assertion on the **objective, no-judge** side of the vendor's own
  deterministic/judged split. This is a nav-grouping artifact, not a claim
  conflict — see Cross-References → Contradicts.

## Extracted Claims

### Claim 1: `max-score` makes no LLM call — it selects the highest-scoring output from the scores the other assertions in the row already produced, and reports exactly one pass per row: "Returns pass=true for the highest scoring output, pass=false for others"
- **Evidence**: The page's opening paragraph, the 5-step "How it works"
  sequence, and the "Comparison with select-best" table rows for API calls,
  Reproducibility, Transparency, and Cost.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `max-score` assertion selects the output with the highest aggregate score from other assertions. Unlike `select-best` which uses LLM judgment, `max-score` provides objective, deterministic selection based on quantitative scores from other assertions." and "Returns pass=true for the highest scoring output, pass=false for others"
- **Our assessment**: This is the whole page in two sentences, and it is the
  item the triage ranked first. Two consequences. (a) **Cost/placement**: an
  assertion in the model-graded nav family that costs nothing per verdict is
  the documented carve-out to any blanket "model-graded asserts consume an
  extra inference call" rule (see Guide Impact). (b) **Verdict shape**: because
  step 4 is an argmax, the per-output `pass` flags are a *ranking*, not a set of
  quality verdicts. In a multi-prompt row every non-winner reports
  `pass=false` **even if it individually satisfied every underlying
  criterion** — so a single `max-score` assert produces exactly one green per
  row by construction, and any CI reader counting "N outputs passed" is
  misreading a selector as N quality verdicts. The page's own "Tips" section
  proposes the mitigation ("Debug with scores: The output shows aggregate
  scores for transparency"), i.e. the numbers are the evidence and the flags
  are not.

### Claim 2: The documented "least bad" edge case makes a `max-score` gate go green when every output failed every underlying assertion — a false green that no config review of the underlying asserts will surface
- **Evidence**: The "Edge cases" list, verbatim, read together with Claim 1's
  per-output pass rule.
- **Confidence**: settled (documented product behavior — the vendor states the
  selection happens even when all candidates fail; no failure-rate measurement
  is offered, and none is claimed here)
- **Quote**: "All outputs fail: Still selects the highest scorer (\"least bad\")"
- **Our assessment**: The single highest-value sentence on the page for Ch05's
  gate-trust checklist. Combined with Claim 1 it defines a green that means
  only "some output scored highest", never "some output was good": if the
  `python` correctness assert and the `llm-rubric` both fail on all three
  prompts, the row still emits one `pass=true`. Nothing in the pass/fail column
  distinguishes that from a real win, so the negative-control discipline
  (#1287 Claim 2/3's "can this gate fail?" property) has to be applied to
  `max-score` explicitly: a `max-score`-only gate cannot fail on quality at
  all, and one that carries an aggregate `threshold` (Claim 5) fails only on
  the aggregate, never per-output. This is documented product behavior,
  checkable against an installed CLI — treat it as such, not as a measured
  gate-failure statistic. I do not resolve *why* the vendor chose it (a
  selector must return something); the guide-relevant part is that a selector's
  green is not a quality signal and must not be read as one.

### Claim 3: Aggregation is chosen at the assert (`value.method`, `average` by default or `sum`) with both formulas documented — and the silent `average` default blends a binary 1.0 and a judge 0.5 on one scale
- **Evidence**: The "Aggregation method" subsection, the "How weights work"
  formula bullets, and the page's own worked arithmetic.
- **Confidence**: settled (documented product behavior; the worked arithmetic
  checks out)
- **Quote**: "For `method: average`, the final score is: `sum(score × weight) / sum(weights)`" and "For `method: sum`, the final score is: `sum(score × weight)`"
- **Our assessment**: The default is the trap surface. Under `average`, a
  passing binary assert contributes a hard `1.0` on the same scale as an
  `llm-rubric`'s partial score, so the cheap deterministic checkouts inflate
  the aggregate relative to the judged ones — the vendor's own worked example
  shows exactly this: with `python=1.0` and `contains=1.0` both at full credit
  and a `llm-rubric` at 0.5, the aggregate is **0.9**, which clears a
  `threshold: 0.7` while the quality criterion is failing. `method: sum`
  removes the normalization (score = unbounded weighted sum), so a `threshold`
  means something numerically different under the two methods — the page never
  states a default for `threshold` (see Claim 5), and switching `method`
  without re-deriving `threshold` is an unreviewed config change. The page's
  "average by default" is documented in the step list ("Calculates an
  aggregate score for each output (average by default)") and in the code
  comment, so nothing about it is hidden — but nothing warns that the *default*
  is the one that mixes scales.

### Claim 4: `value.weights` is keyed by **assertion type** and "Weights apply to all assertions of that type" — individual assertions cannot be weighted at the `max-score` level, and adding a second assertion of an already-weighted type silently changes that type's share of the aggregate
- **Evidence**: The "Weighted scoring" subsection's framing sentence, the
  "How weights work" bullet list, and the two `weights` examples (`python: 3 /
  llm-rubric: 1` and the four-type map in Example 3) — including Example 1, which
  declares **two** `llm-rubric` asserts under a single `llm-rubric: 1` entry.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Give different importance to different assertions by specifying weights per assertion type:" and "Weights apply to all assertions of that type"
- **Our assessment**: This is a different surface from the per-assertion
  `weight` the aggregation hub documents (#1287 Claim 1: per-assertion `weight`
  defaults to 1) and a different surface again from the named-`metric` mapping
  `assertScoringFunction` requires (#1287 Claim 6). The guide needs the three
  kept straight: `weight` = per-assertion weight in the *test-case* average;
  `max-score`'s `weights` = per-assertion-*type* multiplier inside one assert's
  aggregate; `metric` = the name a custom scoring function aggregates by. The
  operational cost of the type-keyed map is granularity: a config that wants
  "correctness 3x, and docstrings matter more than efficiency" has to split the
  judged criteria across **types** or accept a single weight for all of them —
  the page offers no per-assertion escape hatch, and unlike #1287's
  `weight: 0` auto-pass (Claim 4) the page documents **no** `weights: {x: 0}`
   behavior at all, so do not assume a zero weight is a supported way to
  exclude a type from the aggregate. Example 1 also shows the multiplicity
  consequence: two `llm-rubric` asserts under one `llm-rubric: 1` entry means
  the judged-quality family enters the aggregate twice. The page's worked
  example has exactly one assertion per type, so it does **not** disambiguate
  whether the `sum(weights)` denominator counts each assertion separately or
  each type once — recorded as an open question in Extraction Notes rather than
  resolved by guesswork.

### Claim 5: `value.threshold` changes the *outcome shape* rather than the per-output flags: it gates **selection** ("Only select if average score >= 0.7"; "Below threshold: No output selected if threshold is specified and not met") — and a bare `- type: max-score` has no threshold at all, so the documented default configuration cannot fail on quality
- **Evidence**: The "Minimum threshold" subsection, its code comment, and the
  fourth "Edge cases" bullet; contrasted with the "Basic usage" example, which
  ends in a bare `- type: max-score` with no `value` block.
- **Confidence**: settled (documented config surface); the *verdict* mapping for
  the below-threshold case is **not stated on the page** — see Our assessment
  and Extraction Notes
- **Quote**: "Require a minimum score for selection:" and "Below threshold: No output selected if threshold is specified and not met"
- **Our assessment**: The threshold is the only dial that makes a `max-score`
  assert behave like a quality gate, and the page's own "Basic usage" example
  — the first thing a reader copies — leaves it unset. So the copied config
  ranks three prompts and reports one winner, with no bar on the winner. Note
  also what the page does *not* say: "No output selected" describes the
  selection, not the pass/fail report. Whether a below-threshold row then
  reports every output as `pass=false` (the natural reading, and the only one
  consistent with Claim 1) or something else is not documented, and I have not
  assumed it. The practical review rule this yields: a `max-score` gate is only
  a gate if it carries an explicit non-zero `threshold`, and that threshold is
  measured on a blend that mixes hard binary 1.0s with judge scores (Claim 3),
  so it is a *composition-dependent* number, not a portable quality bar — the
  same portability argument #1288 documents for classifier thresholds (Claim 5
  there: thresholds are label-bound and non-portable) applies to a composite
  `max-score` threshold with even less warning from the page.

### Claim 6: The scoring unit contract is "binary = 1.0/0.0, scored = its numeric score (typically 0-1), default weight 1.0" — a *typical*, not enforced, range, which is what makes the mixed-scale average possible
- **Evidence**: The "Scoring details" bullet list, and Example 3's `latency`
  assert (`threshold: 1000`) entering the same `weights` map as `is-json` and
  `llm-rubric`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Binary assertions (pass/fail): Score as 1.0 or 0.0" and "Scored
  assertions: Use the numeric score (typically 0-1 range)" and "Default
  weights: 1.0 for all assertions"
- **Our assessment**: The unit contract is the precondition for Claim 3's
  dilution finding: a hard `1.0` from `contains` and a soft 0.5 from
  `llm-rubric` are averaged as if commensurable, and the page only says scored
  assertions are "typically 0-1" — it states no clamping, so an assertion type
  that emits a score outside 0-1 (a raw cost, a token count, or a JS assert
  returning an arbitrary number per #1304 Claim 1's number-as-score contract)
  would enter the average unchecked. The page also does not document how a
  **lower-is-better** assertion such as `latency` maps onto that 0-1 scale, even
  though Example 3 weights `latency: 1` alongside `is-json: 2` in the same
  aggregate; I have not invented a mapping. Both are recorded as open
  questions. The vendor's default weight of 1.0 also means an unmentioned
  assertion type is *not* excluded from the aggregate — it is averaged in at
  full weight, the opposite of an exclusion idiom.

### Claim 7: Ties break deterministically by prompt index — "Tie scores: First output wins (by index)" / "Tie breaking: First output wins (deterministic)" — reproducible but decided by config order
- **Evidence**: The "Scoring details" bullet and the second "Edge cases" bullet,
  which state the same rule twice.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Tie scores: First output wins (by index)" and "Tie breaking: First output wins (deterministic)"
- **Our assessment**: Determinism without fairness: the run is reproducible,
  which is what makes the green comparable across runs, but *which* output wins
  a tie is a function of position in the `prompts:` list. Reordering prompts —
  a cosmetic-looking diff — can therefore change the reported winner with no
  change to any assertion, and two outputs with identical scores are
  indistinguishable in the report except by index. Combined with Claim 1, a
  tie is also the case where a `max-score` gate most obviously reports an
  arbitrary green.

### Claim 8: The vendor's own `select-best` comparison table is the corpus's cleanest statement of the objective-vs-judged selection split — and the split is about the *selection step only*, because the scores `max-score` aggregates are typically produced by judged asserts
- **Evidence**: The "Comparison with select-best" table (reproduced verbatim in
  Concrete Artifacts).
- **Confidence**: settled (the table is the vendor's documented contrast; the
  inheritance point is synthesis, flagged as such)
- **Quote**: "Aggregate scores from assertions" and "None (uses existing
  scores)" and "One per eval" and "Deterministic" and "May vary" and "Shows exact
  scores" and "Shows LLM reasoning" and "Free (no API calls)" and "Costs per
  API call" (individual cell values from the Comparison table's `max-score` and
  `select-best` columns; the table is reproduced verbatim under Concrete
  Artifacts)
- **Our assessment**: The table is worth quoting as-is because it is the
  vendor's framing of *why* both types exist, and it lines up exactly with the
  deterministic/judged boundary the corpus already draws (#1289 Claim 1, whose
  mini-table lists `select-best` — "A grading model to compare outputs" — among
  the types that "use an additional model or external inference service";
  `max-score` is not among them). The operational caveat the page does not
  make: the "Free (no API calls)" row is true of the selection step only. Every
  example on the page except one aggregates an `llm-rubric`, so in practice the
  judge cost, the judge variance, and the unpinned-judge hazard are *inherited
  through the inputs*, not avoided. The page's own examples make this visible —
  Basic usage weights `python: 3` against an `llm-rubric` — but the table
  invites a reader to conclude `max-score` removes judge risk from the gate.
  It removes the *selection* judge's risk, which for `select-best` was real, and
  nothing else. That distinction is the carve-out Ch05's cost ladder needs.

### Claim 9: `max-score` fails closed on an empty aggregation — "No other assertions: Error - max-score requires at least one assertion to aggregate" — and the page documents no `not-` negated form
- **Evidence**: The first "Edge cases" bullet; the absence of any negation
  section on the page (contrast `g-eval`, which has a dedicated "Negation with
  `not-g-eval`" section, #1349).
- **Confidence**: settled (documented product behavior) for the error; the
  negation point is recorded as **page silence**, not as a claim that
  `not-max-score` is unsupported
- **Quote**: "No other assertions: Error - max-score requires at least one
  assertion to aggregate"
- **Our assessment**: The error is the vendor's fail-closed config-error policy
  showing up again, and it is the good news on this page: unlike the silent-green
  `threshold: 0` / `weight: 0` footguns (#1287 Claims 3/4) and the silent-0
  derived metrics (Claim 7 there), a misconfigured `max-score` says so. It also
  means the "least bad" green of Claim 2 cannot arise from a *typo* — a
  misspelled sibling assertion type that silently produces no score is a
  different failure mode, and the page does not say whether a type that matched
  nothing contributes 0 to the aggregate or is ignored. Noted as an open
  question. On negation: #1287 Claim 10 states every assertion type is negatable
  with a `not-` prefix, and this page documents no negated form and no
  inversion semantics for one. I make no claim either way — but the guide
  should not infer "therefore `not-max-score` is safe" from the hub's blanket
  rule, since what "invert" would even mean for an argmax (invert *which*
  output? the loser?) is not addressed. That is worth a per-type read, in the
  spirit of #1349's per-type-defaults doctrine — each page has to be read on
  its own.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/max-score
(sections as noted).

### Basic usage — note the bare `- type: max-score` with no `threshold` (verbatim from "Basic usage")

```yaml
prompts:
  - 'Write a function to {{task}}'
  - 'Write an efficient function to {{task}}'
  - 'Write a well-documented function to {{task}}'

providers:
  - openai:gpt-5

tests:
  - vars:
      task: 'calculate fibonacci numbers'
    assert:
      # Regular assertions that score each output
      - type: python
        value: 'assert fibonacci(10) == 55'
      - type: llm-rubric
        value: 'Code is efficient'
      - type: contains
        value: 'def fibonacci'
      # Max-score selects the output with highest average score
      - type: max-score
```

### Aggregation method and minimum threshold (verbatim from "Aggregation method" and "Minimum threshold")

```yaml
assert:
  - type: max-score
    value:
      method: average # Default: average | sum
```

```yaml
assert:
  - type: max-score
    value:
      threshold: 0.7 # Only select if average score >= 0.7
```

### Per-assertion-type weights (verbatim from "Weighted scoring")

```yaml
assert:
  - type: python # Test correctness
  - type: llm-rubric # Test quality
    value: 'Well documented'
  - type: max-score
    value:
      weights:
        python: 3 # Correctness is 3x more important
        llm-rubric: 1 # Documentation is 1x weight
```

### The vendor's worked weighted average (verbatim from "How weights work")

```
Output A: python=1.0, llm-rubric=0.5, contains=1.0
Weights:  python=3,   llm-rubric=1,   contains=1 (default)

Score = (1.0×3 + 0.5×1 + 1.0×1) / (3 + 1 + 1)
      = (3.0 + 0.5 + 1.0) / 5
      = 0.9
```

### Example 1: Multi-criteria code selection — two `llm-rubric` asserts under one `llm-rubric: 1` weight (verbatim from "Example 1")

```yaml
prompts:
  - 'Write a Python function to {{task}}'
  - 'Write an optimized Python function to {{task}}'
  - 'Write a documented Python function to {{task}}'

providers:
  - openai:gpt-5-mini

tests:
  - vars:
      task: 'merge two sorted lists'
    assert:
      - type: python
        value: |
          list1 = [1, 3, 5]
          list2 = [2, 4, 6]
          result = merge_lists(list1, list2)
          assert result == [1, 2, 3, 4, 5, 6]

      - type: llm-rubric
        value: 'Code has O(n+m) time complexity'

      - type: llm-rubric
        value: 'Code is well documented with docstring'

      - type: max-score
        value:
          weights:
            python: 3 # Correctness most important
            llm-rubric: 1 # Each quality metric has weight 1
```

### Example 3: API response selection — `latency` weighted in the same map as judged and JSON asserts (verbatim from "Example 3")

```yaml
tests:
  - vars:
      query: 'weather in Paris'
    assert:
      - type: is-json

      - type: contains-json
        value:
          required: ['temperature', 'humidity', 'conditions']

      - type: llm-rubric
        value: 'Response includes all requested weather data'

      - type: latency
        threshold: 1000 # Under 1 second

      - type: max-score
        value:
          weights:
            is-json: 2 # Must be valid JSON
            contains-json: 2 # Must have required fields
            llm-rubric: 1 # Quality check
            latency: 1 # Performance matters
```

### Comparison with `select-best` (verbatim table from "Comparison with select-best")

| Feature | max-score | select-best |
|---|---|---|
| Selection method | Aggregate scores from assertions | LLM judgment |
| API calls | None (uses existing scores) | One per eval |
| Reproducibility | Deterministic | May vary |
| Best for | Objective criteria | Subjective criteria |
| Transparency | Shows exact scores | Shows LLM reasoning |
| Cost | Free (no API calls) | Costs per API call |

### Edge cases (verbatim list from "Edge cases")

- **No other assertions**: Error - max-score requires at least one assertion to aggregate
- **Tie scores**: First output wins (by index)
- **All outputs fail**: Still selects the highest scorer ("least bad")
- **Below threshold**: No output selected if threshold is specified and not met

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 14** (the
    hub's comparison-types finding that `select-best` picks a winner across
    prompts in one row by a criterion, and `max-score` aggregates other
    assertions' scores via `method`/`threshold`) — this page supplies the
    schema, formulas, per-output pass semantics, and four edge cases behind
    that one-line summary, and confirms the hub's "aggregate gate" reading.
    (Verified: #1305 Claim 14, read directly at
    `source-notes/docs-promptfoo-model-graded-metrics.md:291`.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 5** (the
    scratchpad-misparse list: "`select-best` can read a scratchpad number as
    the winning index") — this page is the confirming negative case the triage
    asked for: `max-score` is **not** in that list because it makes no judge
    call, so there is no scratchpad to misparse. (Verified: #1305 Claim 5.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 1** (the
    vendor's own deterministic/model-graded line: `classifier`, `pi`,
    `select-best`, and `similar` "use an additional model or external
    inference service", with `select-best`'s requirement reading "A grading
    model to compare outputs") — this page is the other side of that same
    boundary: `max-score` is absent from the excluded set, and its comparison
    table states the same split from the `max-score` side ("None (uses
    existing scores)" vs "One per eval"). Two vendor surfaces agreeing on
    where the judged step lives. (Verified: #1289 Claim 1, read directly at
    `source-notes/docs-promptfoo-deterministic-metrics.md:54`.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 4** ("If weight
    is set to 0, the assertion automatically passes" — a config value that
    removes an assertion's check from the gate) — this page documents **no**
    equivalent behavior for a `weights:` map entry, and states only
    "Each assertion type can have a custom weight (default: 1.0)". Two
    different weight surfaces with different documented extremes: the
    test-case-level `weight: 0` is a documented auto-pass, the
    `max-score`-level `weights` map has no documented zero. Corroborates the
    hub note's framing that gate-removing values are the reviewable surface
    while flagging that they are **per surface**. (Verified: #1287 Claim 4.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** (pre-deployment
    red teaming must be integrated into CI/CD pipelines and run on a recurring
    schedule) — the "gate in CI" premise this page's hazard lands in: a selector
    assert wired into that pipeline is the shape of gate that reports green on
    schedule while the underlying criteria regress. (Verified: read the OWASP
    note's Claim 4 directly; the claim's own quoted evidence is the
    nondeterministic-consequence rationale, so no quote is carried over here.)

- **Contradicts**: **None identified, and no contradiction issue filed** — the
  one real tension was examined and found to be a taxonomy/emphasis artifact
  plus an internal generalization, not two sources disagreeing on a fact:
  - **Nav grouping vs the page's own self-description.** The sidebar files
    `max-score` under "Model-graded metrics", yet the page states it makes no
    LLM call (Claim 1, Claim 8). This is a navigation artifact, not a claim
    conflict: the vendor's own deterministic/judged split (#1289 Claim 1) puts
    `max-score` on the no-judge side, and #1305 Claim 14's assessment already
    records that it "assumes the scores already exist and aggregates them
    arithmetically."
  - **The one place a generalization is now too broad**: `docs-promptfoo-model-graded-metrics.md`
    **Guide Impact → "Chapter 05 — cost tiering"** (cited by section name, not
    by claim number per MINER.md §4b — that section is not a numbered claim)
    states the cost ladder as "deterministic asserts are free to rerun (#1289);
    model-graded asserts consume an extra inference call per verdict".
    `max-score` is a model-graded-family assert that consumes **zero** inference
    calls for its own verdict. Not filed as a contradiction because (a) that
    sentence is the Miner's own guide-impact synthesis, not an extracted vendor
    claim, so no *source* is contradicting another source; (b) the same note's
    Claim 14 body already carries the carve-out; and (c) the two statements
    differ in context (judge-involving asserts vs an aggregation assert) — the
    MINER.md §4a "when NOT to file" case. Recorded instead as a required guide
    amendment in Guide Impact below, so the Smith can fix the over-broad cost
    rule rather than leaving it to chance.
  - Checked `CONTRADICTIONS.md` (no open `C-NNN` entries) and open
    `contradiction`-labeled issues (#1150, #1307, #1322, #1338, #1352, #1408,
    #1461, #1462). **#1352** (g-eval's dated `gpt-4.1-2025-04-14` judge pin vs
    #1305's ambient-judge finding) is the closest neighbor: it is about *which
    model judges*, this page is about an assert that has **no** judge, so the
    two cannot conflict. **#1307** (missing-trace semantics) does not touch
    this surface — `max-score` consumes assertion scores, not traces.

- **Extends**:
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) — the
    assert-level expression of that note's test-case-level weighted average.
    Claim 1 there ("The final score of the test case is calculated as the
    weighted average of the scores of all assertions, where the weights are
    the `weight` values of the assertions") is the *test-case* model; this
    page's `sum(score × weight) / sum(weights)` is the same arithmetic scoped
    to one assert, with type-keyed weights instead of per-assertion ones. The
    guide needs the two levels drawn explicitly, because `max-score` re-weights
    scores the test-case average will weight again. (Verified: #1287 Claim 1,
    `source-notes/docs-promptfoo-assertions-metrics.md:53`.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 3** — the hub's
    "A `threshold` of `0` makes the test case pass regardless of individual
    assertion failures" is the *other* half of this page's Claim 5: a
    `max-score` assert with no `threshold` is a ranker, and a test-case
    `threshold: 0` is a suite that cannot fail. Both are config-reviewable
    "can this gate fail?" properties. (Verified: #1287 Claim 3.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 6** — the
    `assertScoringFunction` path requires **named metrics** (per-assertion
    `metric:` names) and a `{pass, score, reason}` return; `max-score`'s
    `weights` map is keyed by *assertion type* with no naming step and no
    custom logic, so the two mechanisms do not compose — a suite that wants
    custom composite scoring uses `assertScoringFunction`, and a suite that
    wants type-weighted selection uses `max-score`. Worth stating so a reader
    does not try to `metric:`-tag asserts expecting `max-score` to honor it.
    (Verified: #1287 Claim 6.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 1** ("If the
    function returns a number, it will be treated as a score") — the
    custom-JS numeric return is one of the *unbounded* score sources Claim 6
    flags as undistinguished once it enters a `max-score` aggregate: a JS
    assert returning a raw value is "scored" on the same blend as `llm-rubric`.
    (Verified: #1304 Claim 1, `source-notes/docs-promptfoo-javascript-assertions.md:52`.)
  - `source-notes/docs-promptfoo-g-eval.md` (#1349) — the sibling
    per-type-sub-page convention this note follows, plus two content
    extensions: g-eval's empty-array **config error that fails closed** (its
    Claim 4) is the same vendor policy as this page's "requires at least one
    assertion to aggregate" (Claim 9), and g-eval's array-averaging masking
    finding (0.0 averaged with three 1.0s = 0.75 clearing a 0.7 threshold) is
    the *within-assert* twin of this page's mixed-binary/judge-scale average
    (Claim 3). The guide's aggregate-masking checklist now has two documented
    members. (Verified: #1349 Claims 4 and its Concrete Artifacts.)
  - `source-notes/docs-promptfoo-classifier-grading.md` **Claim 5** (thresholds
    are label-bound and non-portable — the worked thresholds
    0.5 / 0.75 / 0.9 are meaningful only for the specific model and label set)
    — the same portability argument at a different granularity: a
    `max-score` `threshold: 0.7` is meaningful only for the *composition* of
    assertion types and weights that produced it, and the page gives no
    calibration guidance for changing that composition. (Verified: #1288
    Claim 5, `source-notes/docs-promptfoo-classifier-grading.md:114`.)

- **Novel**: What is new to the corpus (the general *frames* — weighted
  aggregation, silent-green configs, judge variance — are already covered by
  #1287/#1289/#1305/#261/#482):
  1. **A model-graded-family assertion with no judge call** (Claims 1, 8) — the
     documented carve-out to the cost ladder: the Comparison table's `API
     calls` row reads "None (uses existing scores)" and its `Cost` row reads
     "Free (no API calls)", against "One per eval" and "Costs per API call" for
     `select-best`.
  2. **The argmax-only pass semantics** (Claim 1) — exactly one `pass=true`
     per row by construction, and every non-winner is `pass=false` even when it
     met every criterion. No existing note documents a pass/fail surface that
     is a ranking.
  3. **The "least bad" false green** (Claim 2) — a documented edge case in
     which the gate reports green when every output failed every underlying
     assertion. This is the first corpus instance of a vendor-documented
     *always-green-by-construction* gate, and it belongs in Ch05's "a gate that
     cannot fail is not a gate" table.
  4. **The type-keyed `weights` map and its granularity limit** (Claim 4) —
     weights apply to *all* assertions of a type; individual assertions cannot
     be weighted at this level, and the page documents no `weights: {x: 0}`
     behavior. First corpus coverage of this third weight surface (after
     per-assertion `weight` and `metric`).
  5. **The `method: average` | `sum` switch with both formulas** (Claim 3) and
     the vendor's own 0.9 worked average that clears 0.7 while the judged
     criterion scores 0.5 — a documented, reproducible instance of aggregate
     dilution by passing binaries.
  6. **Index-order tie-breaking** (Claim 7) — deterministic by prompt index, so
     a `prompts:` reordering can change the reported winner.
  7. **Fail-closed empty aggregation** (Claim 9) — "Error - max-score requires
     at least one assertion to aggregate", the vendor's config-error policy on
     this type.

## Guide Impact

- **Chapter 05 (`guide/05-llm-ops-reliability.md`) — "A gate that cannot fail is
  not a gate" (the six-row table at ~line 656-673)**: add a seventh row. `max-score`
  with no `threshold` is a ranker, not a gate — it "Returns pass=true for the
  highest scoring output, pass=false for others" and, per the documented edge
  case, "All outputs fail: Still selects the highest scorer (\"least bad\")", so
  a row in which every output failed every underlying assertion still reports
  one green [source: docs-promptfoo-max-score, Claim 2]. This row is
  categorically different from the other six (which are *config* values that
  disable a check): here the assert type is a **selector**, so the fix is
  "do not read its `pass` column as a quality verdict" plus "set an explicit
  non-zero `threshold`", not "change this value". State the rule as: *a
  selector's green is a ranking, never evidence that an output was good.*
- **Chapter 05 — evaluation and measurement methodology (the per-assert-type
  read rule at ~line 498-510)**: extend the existing "read that assert type's
  own page" rule with this type's two documented defaults: `method` defaults to
  `average` (the mix-scale blend, Claim 3) and **no `threshold` is set by
  default** — the page's own "Basic usage" example ends in a bare
  `- type: max-score`, so the copied config ranks and reports a winner with no
  bar on it (Claim 5). Add the `weights`-map granularity to the same rule: the
  page weights by **assertion type** and "Weights apply to all assertions of
  that type", so a config needing per-criterion importance must express it
  across types, not within one (Claim 4).
- **Chapter 05 — gate cost tiering (currently sourced from the
  `docs-promptfoo-model-graded-metrics` note's Guide Impact, and at ~line 498)**:
  the ladder statement "model-graded asserts consume an extra inference call
  per verdict" is **too broad as written** and needs the carve-out this page
  supplies: `max-score` consumes **zero** inference calls for its own verdict
  (the Comparison table's `API calls` row reads "None (uses existing scores)";
  the `Cost` row reads "Free (no API calls)"). Add
  it as the free rung of the ladder alongside deterministic asserts — with the
  qualification the page does not state and the guide must: the *selection* is
  free, and the scores it aggregates are usually produced by judged asserts
  (an `llm-rubric` appears in all four of the page's worked configurations),
  so the judge cost,
  variance, and unpinned-judge hazard are inherited through the inputs, not
  avoided (Claim 8). Cite the model-graded family as "judge-involving asserts"
  rather than all model-graded asserts.
- **Chapter 05 — the aggregate-masking checklist**: the `g-eval` section (~line
  476-497) already documents that averaged criteria can mask a failing one
  (0.0 + 1.0 + 1.0 + 1.0 = 0.75 clearing a 0.7 threshold). This page supplies
  the *cross-type* instance: the vendor's own worked average lands 0.9 with the
  judged criterion at 0.5, because two passing binary asserts carry it — so
  "the bar was cleared" and "the judged criterion passed" are different
  statements, and a `max-score` threshold is a composition-dependent number, not
  a portable quality bar (Claims 3, 5).
- **Chapter 06 (Security and Trust) — only if a `max-score` assert is used as a
  safety/red-team gate**: record that this assert type is **not** a safety
  signal. Selecting the "least bad" of three jailbreak-triggering outputs is
  the documented behavior, so a red-team suite that gates on `max-score` gates
  on ranking among failures; safety gates belong on the underlying
  `llm-rubric`/deterministic asserts, with `max-score` used only to choose
  which output to inspect (Claim 2). Also note the page documents no `not-`
  negated form and no inversion semantics, so the hub's blanket
  "every type is negatable with `not-`" (#1287 Claim 10) should not be
  extended to this type without a per-type read (Claim 9).
- **Chapter 02 (Observability) — secondary**: the vendor's transparency hook
  here is the aggregate score itself ("Debug with scores: The output shows
  aggregate scores for transparency"), and `select-best`'s contrast column is
  "Shows LLM reasoning". If a team records gate evidence, the per-output
  aggregate score is the artifact to archive — the pass/fail column is not
  (Claim 8).

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/max-score).
  Page footer: "Last updated on **Sep 26, 2026** by **mldangelo-oai**";
  `date_published` carries the last-updated date (same convention as the sibling
  per-type notes #1349/#1319/#1320/#1332/#1334). Quotes and code blocks
  verified character-for-character against the fetched rendered content
  (prose from the article body, code blocks recovered line-by-line from the
  `<pre>` blocks) before writing; the comparison table and edge-case list were
  copied as rendered. No sub-pages followed: the "Further reading" links are the
  hub page (already mined as #1305), `select-best`, and the assertions hub
  (#1287) — cross-referenced, not re-extracted, per the one-note-per-sub-page
  convention. The three "Example" sections and all eight code blocks were read
  in full and are reproduced or cited above.
- **Triage key-question resolutions** (all three Prospector comments read as
  UNTRUSTED input; every item re-verified against the page text, and the
  first-listed triage assertion corrected where the page says otherwise):
  1. **`method` + formulas + worked example** — confirmed. `average` is the
     default (documented in the step list and the code comment), both formulas
     are given verbatim, and the worked 0.9 example reproduces exactly
     (Claim 3). The worked example also confirms the dilution mechanism the
     triage predicted.
  2. **`weights` is per-assertion-type and "applies to all assertions of that
     type"** — confirmed verbatim (Claim 4), and the page documents **no**
     `weights: {type: 0}` behavior, so unlike the per-assertion `weight: 0`
     auto-pass of #1287 Claim 4 the zero case here is **not** documented. I
     did not extend the #1287 behavior to this surface.
  3. **Pass semantics are a ranking** — confirmed: step 5 of "How it works" is
     "Returns pass=true for the highest scoring output, pass=false for others"
     (Claim 1), and the "All outputs fail: Still selects the highest scorer
     (\"least bad\")" edge case is present verbatim (Claim 2).
  4. **Determinism / cost boundary vs `select-best`** — confirmed by the
     comparison table (Claim 8) plus "Tie scores: First output wins (by index)"
     (Claim 7). Confirmed *negative*: `max-score` does **not** appear in #1305
     Claim 5's scratchpad-misparse list, consistent with it making no judge
     call (cited under Corroborates).
  5. **Scoring details** — confirmed verbatim (Claim 6), including the hedged
     "typically 0-1 range" for scored assertions.
  6. **Correction to a triage assertion**: the triage reported that the page
     "is silent on the all-below-threshold case". The page is **not** silent —
     the "Edge cases" list carries "Below threshold: No output selected if
     threshold is specified and not met". What the page does not state is the
     *verdict* mapping in that case (whether the row then reports all
     `pass=false`); recorded as an open question in Claim 5 rather than
     answered. Same for the second triage comment's "only select if average
     score >= 0.7" framing: that string is the code comment on the
     `threshold: 0.7` example, not prose.
  7. **Determinism carve-out vs #1305's cost ladder** — confirmed and recorded
     as a guide amendment rather than a contradiction filing; reasoning in
     Cross-References → Contradicts, which cites that statement by section name
     (it lives in a Guide Impact paragraph, not a numbered claim, so a
     `Claim N` citation would be fabricated per MINER.md §4b).
- **Open questions recorded, not answered** (page silence — none of these were
  inferred):
  1. Whether the `sum(weights)` denominator counts each *assertion* separately
     or each *type* once when a type has multiple asserts. The page's worked
     example has one assert per type, and Example 1 has two `llm-rubric`
     asserts under one `llm-rubric: 1` entry, so the page's own examples
     straddle the question. No CLI probe was run in this trial.
  2. The pass/fail verdict reported when `threshold` is set and no output
     clears it (Claim 5).
  3. How a lower-is-better assertion such as `latency` maps onto the
     "typically 0-1" score scale, despite Example 3 weighting `latency: 1` in
     the same map (Claim 6), and whether scores outside 0-1 are clamped (the
     page documents no clamping).
  4. Whether an assertion that matched nothing (e.g. a misspelled sibling
     type) contributes 0 to the aggregate or is dropped — the only documented
     behavior is the "no other assertions at all" error (Claim 9).
  5. Whether a `not-max-score` form exists and what it would invert, given the
     hub's blanket negation rule (#1287 Claim 10) and this page's silence
     (Claim 9).
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — each cited or dismissed
  by name):
  - `docs-promptfoo-deterministic-metrics.md` (#1289) — **cited** (Corroborates
    Claim 1, the vendor-drawn boundary that excludes `select-best` and not
    `max-score`).
  - `docs-promptfoo-model-graded-metrics.md` (#1305) — **cited heavily**
    (Corroborates Claims 5 and 14; Extends; and the source of the cost-ladder
    generalization flagged in Contradicts).
  - `docs-promptfoo-assertions-metrics.md` (#1287) — **cited heavily**
    (Corroborates Claims 3/4; Extends Claims 1, 3, 6).
  - `docs-promptfoo-classifier-grading.md` (#1288) — **cited** (Extends Claim 5,
    threshold portability at a different granularity).
  - `docs-litellm-batches-api.md` — LiteLLM gateway batching/rate-limit docs;
    unrelated vendor and no eval-assert surface; dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — **cited** (Corroborates
    Claim 4, the CI/CD red-team integration premise this page's hazard lands
    in).
  - `blog-promptfoo-red-team-gemini.md` (#690) — per-model red-team plugin
    strategy with a latency assert used as a tool; carries no `max-score`
    semantics; dismissed.
  - `blog-promptfoo-red-team-claude.md` (#689) — red-team plugin strategy for
    Claude, rubric/latency asserts as tools, no selection-assert semantics;
    dismissed.
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage by an SRE
    Agent using LLM-as-judge *alerts*; no eval-assert config surface; dismissed.
  - `docs-promptfoo-javascript-assertions.md` (#1304) — **cited** (Extends
    Claim 1, the number-as-score contract as an unbounded aggregate input).
  - Additional cross-refs found by searching `source-notes/` per MINER.md §4
    (not in the candidate file): `docs-promptfoo-g-eval.md` (#1349, **cited** —
    the sibling per-type convention and the aggregate-masking precedent),
    `docs-promptfoo-model-graded-metrics.md`'s cost-ladder Guide Impact
    paragraph (**flagged**, not filed).
- **Cross-ref verification (§4b)**: every cited claim was located and read in
  the cited note before writing — #1305 Claims 5 and 14;
  `docs-promptfoo-deterministic-metrics.md` Claim 1;
  `docs-promptfoo-assertions-metrics.md` Claims 1, 3, 4, 6;
  `docs-promptfoo-classifier-grading.md` Claim 5;
  `docs-promptfoo-javascript-assertions.md` Claim 1;
  `docs-promptfoo-g-eval.md` Claim 4; and the OWASP note's CI/CD phase claim.
  Claim numbers verified against each note's own numbering; no claim numbers
  invented. The one non-claim citation (#1305's cost-ladder statement) is cited
  **by section name** because it lives in a Guide Impact paragraph, not a
  numbered claim. Source-note issue numbers were read from each cited note's
  frontmatter `issue:` field rather than inferred.
- **No contradiction issue filed** — see Cross-References → Contradicts for the
  full reasoning (taxonomy/nav artifact plus a Miner-synthesized guide-impact
  generalization, not a source-vs-source claim conflict; context-scoped
  difference per MINER.md §4a "when NOT to file"). Checked `CONTRADICTIONS.md`
  and all eight open `contradiction`-labeled issues; #1352 (g-eval judge pin)
  and #1307 (missing-trace semantics) are adjacent surfaces, not conflicts.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1289, #1305, #1349): the individual mechanism/default claims
  (Claims 1, 3-9) are settled-for-product-behavior and directly checkable
  against an installed CLI, but this is thin vendor documentation with no
  measured gate-failure rate, cost figure, drift measurement, or calibration
  data, and no independent practitioner validation — the operational
  consequence framing (false-green selector, mixed-scale dilution, threshold
  non-portability) is the Miner's synthesis on top of documented behavior.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
