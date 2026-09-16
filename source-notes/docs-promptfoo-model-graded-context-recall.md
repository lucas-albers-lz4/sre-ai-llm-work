---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/context-recall/
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Context Recall"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-16
date_extracted: 2026-09-16
last_checked: 2026-09-16
status: current
confidence_overall: emerging
issue: "#1332"
---

# Promptfoo Configuration: Model-Graded — Context Recall

> The per-type vendor reference page for promptfoo's retrieval-side RAG
> assertion — the deliberately-deferred deep-dive (#1305 recorded
> "context-recall/relevance/faithfulness … were NOT followed") that supplies
> the *mirror direction* of the mined `context-faithfulness` sibling (#1320):
> `context-recall` grades whether the retrieved context *contains* the
> statements of a known-correct expected answer ("Score = attributable
> statements / total statements"), gates on a `value`+`context` field contract
> (not `query`+`context`), documents the `threshold` default of `0` (a third
> score-blind pass point in the fail-open family, after #1287 Claim 3, #1305
> Claim 10, #1320 Claim 2), carries a "Binary attribution (no partial credit)"
> limitation that the page's own fractional worked example (`Score: 0.5`)
> shows must mean *per-statement*, not per-score — and bounds itself with
> "Requires known correct answers", a hard applicability limit the faithfulness
> page's limitation set does not have.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Context recall"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own assert-type behavior — authoritative for *what promptfoo does*
  with a given `context-recall` config (the score formula, the threshold
  default, the required fields, the `contextTransform` surface), but
  vendor-positioned: the page carries no measured judge-agreement,
  false-negative-rate, or retrieval-failure data and no independent
  practitioner validation. Everything below is checkable against an installed
  CLI.
- **Scope**: A thin, five-section reference page (intro+worked example,
  Configuration, Limitations, Related metrics, Further reading). It is the
  deep-dive on the `context-recall` member of the context-based RAG assertion
  class that `docs-promptfoo-model-graded-metrics.md` (#1305) catalogued at
  class level only — that note's Extraction Notes explicitly record
  "context-recall/relevance/faithfulness … were NOT followed." This page
  therefore carries the *delta* (recall-direction score contract, the
  `value`+`context` field contract, the recall-specific limitation set), not a
  re-derivation of the model-graded framing. Does NOT cover the sibling
  `context-faithfulness` / `context-relevance` pages (separate sources, per the
  one-note-per-sub-page convention), `query`/`context` plumbing beyond this
  page, or empty/fallback-context behavior — the page itself does not document
  that (see Claim 2's boundary note and Extraction Notes).
- **Last updated**: the page footer reads "Last updated on Sep 16, 2026 by
  Haokai Ding". The triage comment (written 2026-09-15) noted the update landed
  via `renovate[bot]`; the current footer names a contributor, so the page was
  touched again on the extraction day. `date_published` carries the last-updated
  date (same convention as the sibling notes).

## Extracted Claims

### Claim 1: `context-recall` grades the *retrieval* side of a RAG pair — it breaks the expected answer into statements and checks whether each can be attributed to the retrieved context, scoring by "attributable statements / total statements", demonstrated with a worked 0.5 partial example
- **Evidence**: The page's intro ("Checks if your retrieved context contains
  the information needed to generate a known correct answer."), the "How it
  works" sentence, and the inline "Example" block
  (`Expected: "Python was created by Guido van Rossum in 1991"` /
  `Context: "Python was released in 1991"` / `Score: 0.5 (year ✓, creator ✗)`).
- **Confidence**: settled (documented formula and worked arithmetic; verifiable
  against an installed CLI)
- **Quote**: "Checks if your retrieved context contains the information needed to generate a known correct answer." and "Breaks the expected answer into statements and checks if each can be attributed to the context. Score = attributable statements / total statements." and "Score: 0.5 (year ✓, creator ✗)"
- **Our assessment**: The unit is *statement-attributability*: a ground-truth
  answer with two statements, one attributable to the context, scores exactly
  0.5 — the recall-side concrete anchor for the guide's "metrics without a
  unit" rule. Note the reference corpus for this metric is the *expected
  answer*, not the model output (unlike faithfulness, #1320 Claim 1): the gate
  measures what portion of the truth the retrieval actually surfaced. That is
  the retrieval-side failure class — the context does not contain the
  information a correct answer needs — and it is a *different* failure from
  faithfulness's (output strayed beyond the context). The how-it-works quote
  also silently shows the two-arg grammar the whole RAG tier shares with the
  faithfulness sibling (claims extracted from a reference text, verified
  against a context).

### Claim 2: The page documents `threshold` as "(default: 0)" — at default config a bare `context-recall` assert is score-blind and passes at score 0, the third independently documented per-assert member of the fail-open family (after `llm-rubric`'s score-blind pass and `context-faithfulness`'s documented 0 default)
- **Evidence**: The "Required fields" list entry: "`threshold` - Minimum score
  0-1 (default: 0)". The vendor states the default; the page never recommends a
  non-zero one, and both worked configs set an explicit threshold
  (`threshold: 1.0 # Context must support entire answer` and `0.8` on the
  `contextTransform` example).
- **Confidence**: settled for the documented default; the pass-at-0 reading is
  Miner synthesis on documented behavior (the formula in Claim 1 + the default)
- **Quote**: "`threshold` - Minimum score 0-1 (default: 0)"
- **Our assessment**: Corroboration, *not* a novel finding — the Prospector
  flagged this as "the third independently documented member of the fail-open
  family" (#1287 Claim 3 test-case level, #1305 Claim 10 `llm-rubric`, #1320
  Claim 2 `context-faithfulness`), and the body of evidence now supports
  class-wide reading: every context-based RAG assert page that documents a
  default at all documents `0` (this page, #1320), while the conversational
  sibling documents `0.5` (#1334 Claim 2). Because the pass condition is
  `score >= threshold` (the hub's scoring model, #1287 Claim 1), a bare
  `assert: - type: context-recall` passes a score-0 run — a retrieval that
  surfaced none of the expected-answer's statements — exactly the vacuous-pass
  the gate exists to catch. This is inference from documented formula +
  default, not a vendor statement; the page never says "a bare assert passes
  everything." For Ch05 the rule is unchanged from #1320: every
  `context-recall` assert must set an explicit non-zero threshold or it does
  not gate.

### Claim 3: The required-field contract is `value` (Expected answer/ground truth) + `context` — *not* `query`+`context` as on the `context-faithfulness` sibling — so a config swapping one RAG assert type for the other silently loses the other's required field
- **Evidence**: The "Required fields" list's three entries (`value`, `context`,
  `threshold`) versus the faithfulness page's `query`+`context`+`threshold`
  list (#1320 Claim 3). The "Full example" also wires a `query` var — but the
  required-fields list does not include it.
- **Confidence**: settled (documented field contract, difference verifiable by
  comparing the two pages)
- **Quote**: "`value` - Expected answer/ground truth" and "`context` - Retrieved text (in vars or via `contextTransform`)"
- **Our assessment**: The config-surface delta between the two RAG siblings.
  `context-faithfulness` grades the response against context and needs the
  user's `query`; `context-recall` grades the context against a known-correct
  answer and needs that answer as `value`. Both take `context`. An operator who
  swaps one assert for the other (say, to add the mirrored check) and keeps the
  old field set misconfigures silently: the missing `value`/`query` is not
  flagged while the gate degrades to judging against the wrong reference. Note
  the "Full example" still supplies `query: 'Who created Python?'` in `vars` —
  a real fixture will carry it anyway, but the gate reads only `value`+`context`.
  Worth stating as a per-type-swap line in Ch05 next to #1305 Claim 8's
  "assertion-specific prompts" note.

### Claim 4: The gate direction is the *mirror* of `context-faithfulness` — recall asks "does the context contain what a correct answer needs?" (retrieval completeness) while faithfulness asks "does the output stay within the context?" (output fidelity); two different failures, two different assertions
- **Evidence**: The "Use when" sentence and the "Related metrics" one-liners
  that position `context-faithfulness` as "Does output stay faithful to
  context?" against this page's own "Checks if your retrieved context contains
  the information needed to generate a known correct answer" intro.
- **Confidence**: settled (directions stated on the two sibling pages; the
  mirror relationship is the Prospector-confirmed reading, verifiable by the
  two score formulas)
- **Quote**: "**Use when**: You have ground truth answers and want to verify your retrieval finds supporting evidence." and "`context-faithfulness` - Does output stay faithful to context?"
- **Our assessment**: The retrieval-completeness gate has *zero* prior coverage
  in the guide — the Prospector confirmed no "recall"/"RAG"/"retriev" hits in
  `guide/05-llm-ops-reliability.md`. The two gates catch disjoint failure
  classes even when configured over the same retrieval: a retrieval that drops
  a needed fact fails `context-recall` while the output — faithfully limited to
  whatever was retrieved — passes `context-faithfulness`. Teams running only
  the faithfulness gate cannot distinguish "the model hallucinated beyond the
  context" from "the retrieval never fetched the ground truth"; the recall gate
  is the missing check. For Ch05 this is the "run the pair, not one of them"
  rule.

### Claim 5: `contextTransform: 'output.context'` extraction with a `0.8` threshold is the per-type instance of the hub's context-based class contract — for RAG systems that return context alongside the response, the transform supplies the grading context dynamically
- **Evidence**: The "Dynamic context extraction" subsection's config example
  (`# Provider returns { answer: "...", context: "..." }` with
  `contextTransform: 'output.context' # Extract context field`, `threshold: 0.8`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "For RAG systems that return context with their response:" and "`contextTransform: 'output.context'` # Extract context field"
- **Our assessment**: The per-type instance of #1305 Claim 13's class-level
  contract ("`contextTransform` … **must return a non-empty string**"). This
  page adds no new plumbing beyond the worked form; the fallback guidance
  (`output.context ?? "No context found"`) and the empty-context question live
  on the hub page (#1305 Claim 13) and in the faithfulness note's still-open
  record (#1320 Claim 7) — this page neither states fallback behavior nor
  contradicts the hub's non-empty mandate. With a threshold set (0.8 here) the
  fallback-context concern from #1320 Claim 7 applies unchanged: a transform
  that degrades to a fallback string becomes the context the judge grades
  against, and nothing on this page makes that visible in the pass/fail report.
  The threshold blend here (0.8, vs 1.0 in the static example) also shows a
  team tuning recall tolerance for dynamic extraction rather than the vendor
  prescribing one.

### Claim 6: The page contains a genuine ambiguity — the Limitations list's "Binary attribution (no partial credit)" reads as if scores are all-or-nothing while the same page's worked example scores 0.5; the reconciliation the vendor never spells out is that attribution is binary *per statement* while the aggregate score is the fraction of attributable statements
- **Evidence**: The first Limitations bullet ("Binary attribution (no partial
  credit)") vs the intro "Example" block (`Score: 0.5 (year ✓, creator ✗)`),
  where each statement is individually ✓ or ✗ and the score is their fraction.
- **Confidence**: settled that the ambiguity is real (both texts are on the
  page verbatim); the reconciliation reading is Miner synthesis on the worked
  example
- **Quote**: "Binary attribution (no partial credit)"
- **Our assessment**: The Prospector's sharpest line, resolved as a
  level-of-analysis ambiguity rather than a contradiction. The example is the
  page's own definitions: two expected-answer statements are each attributed or
  not (year ✓, creator ✗ — no statement is "half supported"), and the score is
  the ratio 1/2 = 0.5. "No partial credit" therefore operates at the statement
  level — a statement is fully attributable or not — while the *aggregate* is
  fractional because it is a count ratio. The limitation bullet's prose is
  shorthand for that statement-level rule and is misleadingly placed at score
  level; the vendor nowhere reconciles the two phrasings. Recorded as an
  unresolved documentation ambiguity (the vendor's intended meaning at the
  score level, if different, is not stated), *not* settled as a contradiction —
  the worked example resolves the operational meaning, and the guide advice
  (per-statement binary attribution, aggregate fraction) does not fork. Note
  the contrast: `conversation-relevance` (#1334 Claim 1) also aggregates binary
  window verdicts into a proportion, so the "binary verdicts → fractional
  aggregate" shape is a family-wide scoring pattern, and per-*statement* binary
  attribution is what makes `context-recall`'s 0.5 a *partial-failure* signal a
  thresholded gate can act on.

### Claim 7: The recall-specific Limitations set — "Works best with factual statements" and "Requires known correct answers" — the latter a hard applicability bound: no ground truth, no gate; both are absent from the faithfulness sibling's limitation set
- **Evidence**: The Limitations list's second and third bullets, versus #1320
  Claim 6's faithfulness limitations ("Depends on judge LLM quality", "May miss
  implicit claims", "Performance degrades with very long contexts").
- **Confidence**: settled (vendor-documented limitations; the complementarity
  reading is the Miner's)
- **Quote**: "Works best with factual statements" and "Requires known correct answers"
- **Our assessment**: The two pages' limitation sets overlap only at the
  implicit "works best with facts" hedges: faithfulness worries about the
  *judge* and long contexts; recall worries about the *reference material*.
  "Requires known correct answers" is the sharpest line on this page: for any
  retrieval surface without a ground-truth answer per test case, `context-recall`
  is unusable — it is the one limitation that is a hard exclusion, not a
  quality gradient. That makes the metric a *supervised* RAG check (you must
  hand the judge the answer you expect retrieval to support), which is exactly
  why it complements rather than substitutes for `context-faithfulness`
  (unsupervised: only needs the response and context). No contradiction with
  #1320 — the sets constrain different inputs (reference answer vs judge),
  which is a conditioning variable, not a disagreement.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/context-recall/.

### Worked example (verbatim from the page intro "Example")

```
Expected: "Python was created by Guido van Rossum in 1991"
Context: "Python was released in 1991"
Score: 0.5 (year ✓, creator ✗)
```

### Configuration (verbatim from "Configuration" and "Required fields")

```yaml
assert:
  - type: context-recall
    value: 'Python was created by Guido van Rossum in 1991'
    threshold: 1.0 # Context must support entire answer
```

Required fields (verbatim from the list):

- `value` - Expected answer/ground truth
- `context` - Retrieved text (in vars or via `contextTransform`)
- `threshold` - Minimum score 0-1 (default: 0)

### Full example (verbatim from "Full example")

```yaml
tests:
  - vars:
      query: 'Who created Python?'
      context: 'Guido van Rossum created Python in 1991.'
    assert:
      - type: context-recall
        value: 'Python was created by Guido van Rossum in 1991'
        threshold: 1.0
```

### Dynamic context extraction (verbatim from "Dynamic context extraction")

```yaml
# Provider returns { answer: "...", context: "..." }
assert:
  - type: context-recall
    value: 'Expected answer here'
    contextTransform: 'output.context' # Extract context field
    threshold: 0.8
```

### Limitations (verbatim from "Limitations")

- Binary attribution (no partial credit)
- Works best with factual statements
- Requires known correct answers

Related metrics (verbatim from "Related metrics"): `context-relevance` - "Is
retrieved context relevant?"; `context-faithfulness` - "Does output stay
faithful to context?"

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` **Claim 2**
    (its documented "`threshold` - Minimum score 0-1 (default: 0)" default) —
    this page's Claim 2 is the mirror-page instance of the identical
    score-blind default: two independent per-type pages in the same RAG tier
    document `0`. (Verified: #1320 Claim 2.) The family reading in this note's
    Claim 2 — per-assert score-blind defaults on both context-based gates — is
    now established by two pages, not one.
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 10** (the
    `llm-rubric` score-blind pass: "Without threshold: PASS depends only on the
    grader's `pass` field…" with a `{"pass": true, "score": 0}` example) and
    `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 3** (a
    test-case `threshold` of `0` "makes the case pass regardless of how many
    assertions fail") — the two other members of the fail-open family this
    page's Claim 2 corroborates; together the three establish a class-level
    pattern (test-case level, `llm-rubric`, and two context-based per-asset
    pages). (Verified: #1305 Claim 10, #1287 Claim 3.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 13** (the
    context-based RAG class contract: `contextTransform` "**must return a
    non-empty string**", the `output.context ?? "No context found"` fallback
    idiom) — this page's `contextTransform: 'output.context'` example (Claim 5)
    instantiates that class-level contract on the recall page, consistent with
    (not re-extending beyond) the hub. (Verified: #1305 Claim 13.)
  - `source-notes/docs-promptfoo-conversation-relevance.md` **Claim 2** (the
    per-type threshold family: "conversation-relevance documents `0.5`" vs
    "context-faithfulness defaults to `0`" — "each page must be read on its
    own") — this page adds `context-recall` to the documented-default side of
    that family (0, like faithfulness) and does not change the "read each page"
    doctrine. (Verified: #1334 Claim 2.)
  - `source-notes/docs-promptfoo-conversation-relevance.md` **Claim 1** (binary
    window verdicts aggregated into a fractional proportion — "The final score
    is the proportion of windows where the response was deemed relevant") — the
    family-wide "binary per-unit verdicts → fractional aggregate" scoring shape
    that reconciles this page's Claim 6. (Verified: #1334 Claim 1.)

- **Contradicts**: None identified, and no contradiction issue filed. The one
  intra-page tension (Claim 6 — "Binary attribution (no partial credit)" vs the
  `Score: 0.5` worked example) was evaluated against MINER.md §4a: it is a
  level-of-analysis ambiguity the page's own example resolves (per-statement
  binary, aggregate fractional), so no contradiction issue was warranted — the
  two phrasings do not produce forking guide advice, and the vendor's meaning
  at score level is simply not stated. Checked `CONTRADICTIONS.md` (no open
  `C-NNN` entries) and open `contradiction`-labeled issues: #1150 (unrelated
  LiteLLM routing) and #1307 (promptfoo missing-trace semantics) — neither
  touches context-based RAG scoring. The limitation-set difference versus #1320
  (Claim 7 here) is a conditioning variable (reference-answer bound vs
  judge/context bound), not disagreement. Specifically dismissed as a
  contradiction: #1334 Claim 2's documented `0.5` conversational default vs
  this page's `0` recall default — different assert types, same "read each page
  on its own" family doctrine, no opposition.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — directly
    fills that note's deliberate scoping gap. Its Extraction Notes state the
    per-type sub-pages ("context-recall/relevance/faithfulness … were NOT
    followed") and its Claim 13 catalogues the class at contract level; this
    note is the `context-recall` per-type deep-dive under that class coverage —
    the recall-direction score formula (Claim 1), the fail-open default (Claim
    2), the `value`+`context` field contract (Claim 3), and the recall-specific
    limitations (Claim 7). Its Claim 8's constraint that `context-recall`
    "require[s] assertion-specific prompts and specific output formats" is the
    hub-side echo of this page's supervised, ground-truth-bound shape.
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` (#1320) —
    the mirrored sibling: #1320 Claim 1's "Score = supported claims / total
    claims" and this page's "Score = attributable statements / total
    statements" are the two directions of one RAG pair; #1320 Claim 3's
    `query`+`context` contract and this page's `value`+`context` are the
    config-surface counterparts. The two notes together let Ch05 describe the
    full context-based RAG gate pair, not one half of it.
  - `source-notes/docs-promptfoo-answer-relevance.md` (#1319) and
    `source-notes/docs-promptfoo-conversation-relevance.md` (#1334) — same
    per-type reference tier, different metrics/aggregation shapes (cosine
    similarity; windowed binary verdicts). This page adds the count-ratio member
    to the family's documented aggregation shapes.

- **Novel**: The risk *frame* (score-blind default, class-level RAG contract) is
  already in the corpus (#1287/#1305/#1320/#1334) — deliberately not
  re-claimed. What is new here:
  1. **The retrieval-completeness gate contract** (Claims 1, 4) — the exact
     "attributable statements / total statements" formula with the worked 0.5
     example, and the mirror-direction framing vs faithfulness. The guide has
     zero coverage of recall-as-a-gate (Prospector-confirmed: no recall/RAG/
     retriev hits in `guide/05-llm-ops-reliability.md`); this note supplies the
     reference-level definition and the "run the pair" rule.
  2. **The `value`+`context` field contract** (Claim 3) — distinct from #1320's
     `query`+`context`; the config-surface delta that makes the two RAG
     siblings' misconfiguration modes differ.
  3. **The reconciliation of the binary-attribution ambiguity** (Claim 6) — a
     precise record of a page-level ambiguity and its resolution via the worked
     example, in the spirit of #1320 Claim 7's "a precise record of an
     unresolved question is itself corpus value."
  4. **The supervised-hard-bound limitation** (Claim 7) — "Requires known
     correct answers" as a hard applicability exclusion, distinct from every
     limitation the faithfulness sibling documents; the supervised-vs-
     unsupervised RAG-check split.
  5. **The third documentation point for the fail-open family at per-assert
     level** (Claim 2) — `context-recall` and `context-faithfulness` both
     document a `0` per-assert default, versus `llm-rubric`'s omitted-threshold
     pass and #1287's test-case-level trap — strengthening the class-wide claim
     the Prospector explicitly asked not to over-claim as novel.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md`, "Metrics without a unit are noise" /
  "Judge calibration before judge trust")**: add the **RAG gate-pair rule**:
  retrieval completeness and output fidelity are two disjoint failure classes
  caught by two distinct gates — `context-recall` (Claims 1, 4: does the
  *context* contain the expected answer's statements?) and
  `context-faithfulness` (#1320 Claim 1: does the *output* stay within the
  context?); a retriever that drops needed facts passes a faithfulness-only
  suite because the model has nothing to be unfaithful to. Guide teams to run
  the pair over the same eval and treat "green faithfulness + green recall" as
  the only claim that retrieval+generation held together. Where the gate-review
  checklist already demands explicit thresholds (#1320's rule), state it
  class-wide: every `context-recall` assert must set a non-zero `threshold` or
  it passes at score 0 (Claim 2), and `context-recall` additionally requires a
  per-case ground-truth `value` to exist at all (Claim 7's hard bound) — that
  bound, plus the score formula, is the "unit" for the metric: statement-
  attribution ratio over a known-correct answer.
- **Chapter 05 — assert swap-safety**: extend #1305 Claim 8's per-type guidance
  with the config-surface delta (Claim 3): swapping `context-faithfulness`
  (`query`+`context`) for `context-recall` (`value`+`context`) or vice versa
  loses a required field silently — the two required-field contracts must be
  captured per assert type in any RAG gate template so a swap does not
  misconfigure the grader against the wrong reference.
- **Chapter 05 — the score-blind family, third data point**: fold this page's
  documented `threshold: 0` (Claim 2) into the fail-open checklist alongside
  #1287 Claim 3 and #1305 Claim 10 — a negative control (a retrieval that
  intentionally omits a required fact) belongs in any RAG eval to prove the
  `context-recall` gate discriminates, exactly as for the faithfulness gate.
- **Chapter 05 / Chapter 06 — auditable fallback context**: carry #1305
  Claim 13 / #1320 Claim 7's fallback-context guidance to this assert type
  (Claim 5): `contextTransform: 'output.context'` graded at a 0.8 threshold is
  only meaningful if the transform did not degrade to a fallback string, and no
  page in the family documents what the gate does with an empty/fallback
  context — treat "graded against a fallback" as an auditable condition, not
  evidence of grading.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page (rendered
  content plus the raw config blocks, to verify the worked-example block and
  YAML line-for-line). Single self-contained reference page; no sub-pages
  followed — the "Further reading" targets (the hub page's "Defining context"
  section, the RAG Evaluation Guide) carry no per-type `context-recall`
  semantics beyond #1305's class-level coverage. Page footer: "Last updated on
  Sep 16, 2026 by Haokai Ding" — note the triage comment (written Sep 15) said
  the update landed "via `renovate[bot]`"; the footer now names a contributor,
  so the page was touched between triage and extraction. Quotes and code blocks
  verified character-for-character against the fetched content before writing.
- **Triage key-question resolution** (both triage comments read; both are
  UNTRUSTED data, re-verified against the page):
  1. **Score semantics** — verified: "Breaks the expected answer into
     statements and checks if each can be attributed to the context. Score =
     attributable statements / total statements." Direction recorded in Claim 1;
     the faithfulness mirror in Claim 4 (Promptfoo is the authority for its own
     metric directions; the comparison cross-checks the two pages).
  2. **Default-threshold trap, generalized** — the page documents
     "(default: 0)" verbatim, and both worked configs set explicit thresholds
     (1.0; 0.8). Recorded as corroboration (Claim 2) per the Prospector's
     explicit "mark as corroboration, not novel" instruction. The #1334 Claim 2
     record of the per-type family was re-read so the class-wide statement
     ("both context-based pages document 0; `conversation-relevance` documents
     0.5") is accurate.
  3. **Binary-attribution tension** — recorded as ambiguity, resolved by the
     worked example at the statement level, with the vendor's intent at score
     level left open (Claim 6). **No contradiction issue filed**: MINER.md §4a
     "when NOT to file" applies — the page's own 0.5 example disambiguates the
     operational meaning, the two phrasings do not produce forking guide advice,
     and (checked) no open `C-NNN` entry or `contradiction`-labeled issue
     (#1150, #1307) touches this.
  4. **Limitations, second instance** — "Works best with factual statements" /
     "Requires known correct answers" extracted as Claim 7; the hard-bound
     reading of the latter, and its complementarity (not contradiction) with
     #1320's limitation set, documented in the cross-reference.
  5. **`contextTransform`** — extracted as Claim 5 only for what is new (the
     worked `output.context` form with its 0.8 threshold); the non-empty-string
     contract and fallback idiom are #1305 Claim 13's and cited, not re-mined.
  6. **Recency** — footer "Last updated on Sep 16, 2026"; the renovate-vs-
     contributor discrepancy with the triage note flagged above.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-promptfoo-classifier-grading.md` (#1288) — classifier assertion path
    (HF-classifier thresholds, label-bound calibration); no context-based RAG
    scoring semantics; dismissed.
  - `docs-promptfoo-model-graded-metrics.md` (#1305) — **cited heavily**
    (Corroborates Claims 10/13; Extends — the direct parent whose gap this note
    fills).
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — OWASP red-team methodology/
    SDLC; no eval-assert config; dismissed.
  - `blog-promptfoo-red-team-gemini.md` (#690) — per-model red-team plugin
    strategy; no context-based RAG scoring; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage by an SRE
    Agent; no eval-assert config; dismissed.
  - `blog-promptfoo-red-team-claude.md` (#689) — same red-team methodology, no
    assert-scoring content; dismissed.
  - `docs-promptfoo-javascript-assertions.md` (#1304) — custom-JS assertion
    surface; its `context.trace` silent-pass guard (#1307 Side A) is a
    trace-data concern, not a context-based RAG scoring concern; dismissed.
  - `docs-google-sre-team-lifecycles.md` (#907) — Google SRE org/lifecycle
    chapter; no LLM-eval content; dismissed.
  - `docs-promptfoo-assertions-metrics.md` (#1287) — **cited** (Corroborates
    Claim 3, test-case-level fail-open member).
  - `docs-langfuse-evaluation-core-concepts.md` (#195) — Langfuse eval concepts;
    different vendor/harness; no promptfoo assert-config; dismissed.
  - Additional candidates found by searching `source-notes/` per MINER.md §4
    (not in the candidate file): `docs-promptfoo-model-graded-context-faithfulness.md`
    (#1320) — **cited heavily** (the mirrored sibling); `docs-promptfoo-conversation-relevance.md`
    (#1334) — **cited** (Corroborates Claims 1-2, the per-type threshold family);
    `docs-promptfoo-answer-relevance.md` (#1319) — **cited** (Extends, same
    per-type tier).
- **Cross-ref verification (§4b)**: every cited claim was located and read in
  the cited note before writing — #1320 Claims 1, 2, 3, 6, 7; #1305 Claims 8,
  10, 13 (+ Extraction Notes sub-page-following statement); #1287 Claim 3;
  #1334 Claims 1, 2; #1319 (Scope/summary — cited only at note level, no claim
  number attached). Claim numbers verified against the cited notes' own
  numbering; no claim numbers invented. Source-note issue numbers read from
  each cited note's frontmatter (`issue:` field): #1320, #1305, #1287, #1334,
  #1319 confirmed as listed.
- **No contradiction issue filed** (see Claim 6 / Contradicts): the page opposes
  no existing source-note claim, and the intra-page ambiguity is resolved by the
  page's own example. Verified against `CONTRADICTIONS.md` (no open `C-NNN`
  entries) and open `contradiction`-labeled issues (#1150 unrelated; #1307
  trace-data, cross-surface only). The `0` vs `0.5` per-type defaults are a
  documented family pattern (#1334 Claim 2), not a contradiction.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1288, #1305, #1320, #1319, #1334): the individual formula/
  field/default claims (Claims 1, 2-as-documented, 3, 5) are settled-for-product-
  behavior and directly checkable against an installed CLI, but this is vendor
  documentation with no measured judge-agreement or failure data and a thin
  (five-section) surface; the operational-consequence framing (score-blind
  default, mirror-direction rule, ambiguity resolution, hard-bound limitation)
  is the Miner's synthesis on top of documented behavior.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.