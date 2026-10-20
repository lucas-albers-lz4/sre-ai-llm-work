---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/context-relevance/
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Context Relevance"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-16
date_extracted: 2026-09-16
last_checked: 2026-09-16
status: current
confidence_overall: emerging
issue: "#1333"
---

# Promptfoo Configuration: Model-Graded — Context Relevance

> The per-type vendor reference page for promptfoo's `context-relevance`
> RAG assertion — the page that measures what fraction of retrieved context
> is minimally needed to answer a query ("Score = required sentences / total
> sentences"), with a `threshold` default of `0` (the fourth independently
> documented member of the fail-open family), a `query`+`context` required-field
> contract matching `context-faithfulness`, and two hazards new to the
> `context-*` family: an *inverted polarity* warning (a low score can mean
> good retrieval, making a threshold gate non-actionable) and a
> *formatting-dependent denominator* (prose vs. array chunks changes the score
> for identical content).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Context relevance"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `context-relevance` behavior — authoritative for *what promptfoo
  does* with a given config (the score formula, the threshold default, the
  required fields, the denominator heuristic), but vendor-positioned: the page
  carries no measured judge-agreement, false-negative-rate, or retrieval-quality
  figures and no independent practitioner validation. Everything below is
  checkable against an installed CLI.
- **Scope**: A thin, six-section reference page (intro+worked example,
  Configuration, Array context, Dynamic context extraction, Score interpretation,
  Limitations, Related metrics, Further reading). It is the deep-dive on the
  `context-relevance` member of the context-based RAG assertion class that
  `docs-promptfoo-model-graded-metrics.md` (#1305) catalogued at class level
  only — that note's Extraction Notes explicitly record
  "context-recall/relevance/faithfulness … were NOT followed." This page
  therefore carries the *delta* (the relevance-direction score formula, the
  inverted polarity hazard, the formatting-dependent denominator, the score
  interpretation bands), not a re-derivation of the model-graded framing. Does
  NOT cover the sibling `context-faithfulness` / `context-recall` pages
  (separate sources, per the one-note-per-sub-page convention), `query`/`context`
  plumbing beyond this page, or empty/fallback-context behavior — the page
  itself does not document that.
- **Last updated**: the page footer reads "Last updated on Sep 16, 2026 by
  Michael". `date_published` carries the last-updated date (same convention as
  the sibling notes).

## Extracted Claims

### Claim 1: `context-relevance` grades what fraction of retrieved context is minimally needed to answer the query — "Score = required sentences / total sentences" — demonstrated with a worked example where one required sentence out of three scores 0.33
- **Evidence**: The page's "How it works" statement and the inline "Example"
  block (`Query: "What is the capital of France?"` /
  `Context: "Paris is the capital. France has great wine. The Eiffel Tower is in Paris."` /
  `Score: 0.33 (only first sentence required)`).
- **Confidence**: settled (documented formula and worked arithmetic; verifiable
  against an installed CLI)
- **Quote**: "Score = required sentences / total sentences." and "Score: 0.33 (only first sentence required)"
- **Our assessment**: The metric's unit, stated explicitly — the one place the
  guide's "metrics without a unit are noise" rule gets its concrete anchor for
  RAG relevance: a three-sentence context where only one is essential scores
  exactly 0.33, not "somewhat relevant." The formula makes the score depend on
  the judge *classifying* each sentence as required or not; every misclassified
  sentence changes both numerator and denominator. Crucially, adding correct-
  but-supplementary context *lowers* the score — the worked example shows a
  context that *does* contain the answer but scores 0.33 because two of three
  sentences are supplementary. This is the opposite intuition from
  `context-faithfulness` (#1320 Claim 1), where more context gives the judge
  more to verify against; here, more context dilutes the signal. The worked
  example is a *good* retrieval (answer present, context relevant) that would
  fail a 0.5 threshold — the "a good retrieval can fail a relevance gate"
  anchor the triage flagged.

### Claim 2: The page documents `threshold` as "(default: 0)" — at default config a bare `context-relevance` assert is score-blind and passes at score 0, the fourth independently documented per-assert member of the fail-open family
- **Evidence**: The "Required fields" list entry: "`threshold` - Minimum score
  0-1 (default: 0)". The vendor states the default; the page never recommends a
  non-zero default, and the worked configs set explicit thresholds (`0.3`,
  `0.8`, `0.5`).
- **Confidence**: settled for the documented default; the pass-at-0 reading is
  Miner synthesis on documented behavior (the formula in Claim 1 + the default)
- **Quote**: "`threshold` - Minimum score 0-1 (default: 0)"
- **Our assessment**: Corroboration, not a novel finding — the family is now
  established across four per-assert data points: `context-faithfulness`
  documents `0` (#1320 Claim 2), `context-recall` documents `0` (#1332 Claim 2),
  and the hub's `llm-rubric` score-blind pass (#1305 Claim 10) plus the
  test-case level trap (#1287 Claim 3) complete the picture. Because the pass
  condition is `score >= threshold` (the hub's scoring model, #1287 Claim 1) and
  the default threshold is `0`, a bare `assert: - type: context-relevance`
  passes a score-0 run — a retrieval where the judge found zero required
  sentences — exactly the vacuous pass the gate exists to catch. This is
  inference from documented formula + default, not a vendor statement; the page
  never says "a bare assert passes everything." For Ch05 the rule is unchanged:
  every `context-relevance` assert must set an explicit non-zero threshold or
  it does not gate.

### Claim 3: The required-field contract is `query` ("User's question (in test vars)") and `context` ("Retrieved text (in vars or via `contextTransform`)"), plus `threshold` — the same two-slot field contract as `context-faithfulness`, but distinct from `context-recall`'s `value`+`context`
- **Evidence**: The "Required fields" list's three entries, matching #1320
  Claim 3's field set exactly.
- **Confidence**: settled (documented field contract)
- **Quote**: "`query` - User's question (in test vars)" and "`context` - Retrieved text (in vars or via `contextTransform`)" and "`threshold` - Minimum score 0-1 (default: 0)"
- **Our assessment**: The `query`+`context` contract makes this a retrieval-
  quality gate that grades *against the query*, not against a known-correct
  answer (that is `context-recall`'s job, #1332 Claim 3). An operator who
  swaps `context-relevance` for `context-recall` and keeps the old field set
  misconfigures silently: the missing `value` is not flagged while the gate
  degrades. Worth stating as a per-type-swap line in Ch05 alongside #1332
  Claim 3's mirror warning.

### Claim 4: The page's own warning states a low score can mean good retrieval — "A low score might mean good retrieval (found answer plus supporting context) or bad retrieval (lots of irrelevant content)" — making a threshold gate on `context-relevance` non-actionable without a human-defined band, because the failing signal has two opposite causes
- **Evidence**: The warning block in the page intro, verbatim.
- **Confidence**: settled (vendor-documented warning)
- **Quote**: "This metric finds the MINIMUM needed, not all relevant content. A low score might mean good retrieval (found answer plus supporting context) or bad retrieval (lots of irrelevant content)."
- **Our assessment**: This is the sharpest finding on the page and entirely new
  to the `context-*` family. For `context-faithfulness` (#1320) and
  `context-recall` (#1332), a low score is unambiguously bad — unsupported
  claims or missing statements are the only way to score low. For
  `context-relevance`, a low score has two opposite meanings: the retrieval
  found the answer in one sentence (good) *or* the retrieval returned a pile of
  noise (bad). A CI gate whose failing signal has two opposite causes cannot
  route an on-call response — the gate can tell you "something is off" but
  cannot tell you *what*. For Ch05: `context-relevance` should be treated as a
  *diagnostic* metric (score tracked over time, investigated manually) rather
  than a *gate* metric (threshold pass/fail), unless the team has independently
  validated that their use case falls in the "mostly noise" interpretation. The
  vendor's own score interpretation bands (Claim 6) partially address this by
  giving human-facing ranges, but a bare threshold gate does not distinguish the
  two causes.

### Claim 5: The denominator is formatting-dependent — "A single-paragraph (prose) context string is split into sentences on `.`/`!`/`?` boundaries; a context with two or more non-empty lines, or an array of chunks, is treated as already segmented and split by line/chunk" — so the same retrieved content scores differently depending on whether the provider formats it as prose or as structured chunks
- **Evidence**: The "Limitations" list's first bullet, verbatim.
- **Confidence**: settled (vendor-documented limitation)
- **Quote**: "A single-paragraph (prose) context string is split into sentences on `.`/`!`/`?` boundaries; a context with two or more non-empty lines, or an array of chunks, is treated as already segmented and split by line/chunk. Sentence splitting is a lightweight heuristic that does not handle every abbreviation or decimal edge case — provide an array of chunks for the most precise denominator."
- **Our assessment**: A concrete reproducibility problem for a CI gate. The same
  three facts, formatted as one prose paragraph vs. as three array elements, will
  produce different denominators (3 sentences via `.` splitting vs. 3 chunks via
  line splitting — possibly the same count, but the boundary logic differs). More
  consequentially, a provider that returns context as a single long sentence
  (no `.`/`!`/`?` boundaries) yields a denominator of 1, making every
  sentence either required (score 1.0) or irrelevant (score 0.0) with no middle
  ground. The vendor's own recommendation ("provide an array of chunks for the
  most precise denominator") is an admission that the prose heuristic is lossy.
  This is a *different* denominator mechanism from `context-faithfulness`'s
  "claims the judge fails to register drop out of the denominator" (#1320
  Claim 6) — here the denominator is set by *formatting*, not by judge
  capability. For Ch05: a `context-relevance` gate must document which
  denominator path (prose splitting vs. array chunks) its context takes,
  because the score is not comparable across paths.

### Claim 6: The page documents three interpretation bands — "0.8-1.0: Almost all content is essential (very focused or minimal retrieval)", "0.3-0.7: Mixed essential and supporting content (often ideal)", "0.0-0.3: Mostly non-essential content (may indicate poor retrieval)" — creating a vendor-internal tension with the "Full example" threshold of 0.8
- **Evidence**: The "Score interpretation" section's three bullets and the
  "Full example" config's `threshold: 0.8 # Most content should be essential`.
- **Confidence**: settled (both statements are on the page verbatim)
- **Quote**: "0.3-0.7: Mixed essential and supporting content (often ideal)" and
  "threshold: 0.8 # Most content should be essential"
- **Our assessment**: The triage flagged this as a "vendor-internal threshold
  tension," and it holds: the vendor's own score interpretation calls 0.3–0.7
  "often ideal," while the very next section's worked example sets `threshold:
  0.8` with the comment "Most content should be essential." An operator who
  copies the example into CI fails a score of 0.6 — a score the vendor
  describes as "often ideal." This is not a *contradiction* (the 0.8 example
  targets a different use case than the general "often ideal" band), but it is
  a concrete copy-the-example-into-CI trap: the example threshold *exceeds* the
  "ideal" band, so a team that copies it and sees failures may be rejecting
  good retrievals. The three bands are the vendor's own guidance; the example
  is a worked config. Neither is wrong, but they lead to different conclusions
  for an operator who treats the example as a template. No contradiction issue
  warranted — the tension is a conditioning variable (use-case specificity),
  not a claim disagreement.

### Claim 7: `contextTransform: 'output.context'` extraction with array-form support (`output.chunks`) is the per-type instance of the hub's context-based class contract — for RAG systems that return context alongside the response, the transform supplies the grading context dynamically
- **Evidence**: The "Dynamic context extraction" subsection's config examples
  (`contextTransform: 'output.context' # Extract context field` and
  `contextTransform: 'output.chunks' # Extract chunks array`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "For RAG systems that return context with their response:" and
  "`contextTransform: 'output.context' # Extract context field"` and
  "`contextTransform: 'output.chunks' # Extract chunks array`"
- **Our assessment**: The per-type instance of #1305 Claim 13's class-level
  contract. This page adds the array-form `output.chunks` extraction, which
  interacts with Claim 5's formatting-dependent denominator: extracting chunks
  via `contextTransform` pre-segments the context (line/chunk splitting), while
  extracting a prose string triggers the `.`-boundary heuristic. The two
  extraction forms are not just convenience variants — they produce different
  denominators for the same underlying content. The fallback-context concern
  from #1320 Claim 7 applies unchanged: a transform that degrades to a fallback
  string becomes the context the judge grades against, and nothing on this page
  makes that visible in the pass/fail report.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/context-relevance/
(sections as noted).

### Worked example (verbatim from the page intro "Example")

```
Query: "What is the capital of France?"
Context: "Paris is the capital. France has great wine. The Eiffel Tower is in Paris."
Score: 0.33 (only first sentence required)
```

### Configuration (verbatim from "Configuration" and "Required fields")

```yaml
assert:
  - type: context-relevance
    threshold: 0.3 # At least 30% should be essential
```

Required fields (verbatim from the list):

- `query` - User's question (in test vars)
- `context` - Retrieved text (in vars or via `contextTransform`)
- `threshold` - Minimum score 0-1 (default: 0)

### Full example (verbatim from "Full example")

```yaml
tests:
  - vars:
      query: 'What is the capital of France?'
      context: 'Paris is the capital of France.'
    assert:
      - type: context-relevance
        threshold: 0.8 # Most content should be essential
```

### Array context (verbatim from "Array context")

```yaml
tests:
  - vars:
      query: 'What are the benefits of RAG systems?'
      context:
        - 'RAG systems improve factual accuracy by incorporating external knowledge sources.'
        - 'They reduce hallucinations in large language models through grounded responses.'
        - 'RAG enables up-to-date information retrieval beyond training data cutoffs.'
        - 'The weather forecast shows rain this weekend.' # irrelevant chunk
    assert:
      - type: context-relevance
        threshold: 0.5 # Score: 3/4 = 0.75
```

### Dynamic context extraction (verbatim from "Dynamic context extraction")

```yaml
# Provider returns { answer: "...", context: "..." }
assert:
  - type: context-relevance
    contextTransform: 'output.context' # Extract context field
    threshold: 0.3
```

```yaml
assert:
  - type: context-relevance
    contextTransform: 'output.chunks' # Extract chunks array
    threshold: 0.5
```

### Score interpretation (verbatim from "Score interpretation")

- **0.8-1.0**: Almost all content is essential (very focused or minimal retrieval)
- **0.3-0.7**: Mixed essential and supporting content (often ideal)
- **0.0-0.3**: Mostly non-essential content (may indicate poor retrieval)

### Limitations (verbatim from "Limitations")

- Only identifies minimum sufficient content
- A single-paragraph (prose) context string is split into sentences on `.`/`!`/`?` boundaries; a context with two or more non-empty lines, or an array of chunks, is treated as already segmented and split by line/chunk. Sentence splitting is a lightweight heuristic that does not handle every abbreviation or decimal edge case — provide an array of chunks for the most precise denominator.
- Score interpretation varies by use case

Related metrics (verbatim from "Related metrics"): `context-faithfulness` - "Does output stay faithful to context?"; `context-recall` - "Does context support expected answer?"

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` **Claim 2**
    (its documented "`threshold` - Minimum score 0-1 (default: 0)" default) —
    this page's Claim 2 is the third per-type page in the context-based RAG
    family to document `0` (after #1320's `context-faithfulness` and #1332's
    `context-recall`), strengthening the class-wide reading of the fail-open
    family. (Verified: #1320 Claim 2.)
  - `source-notes/docs-promptfoo-model-graded-context-recall.md` **Claim 2**
    (its documented `threshold` default of `0`) — same corroboration from the
    recall-direction sibling; the family reading now has three independent
    per-type data points (#1320 Claim 2, #1332 Claim 2, this page's Claim 2).
    (Verified: #1332 Claim 2.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 13** (the
    context-based RAG class contract: `contextTransform` "**must return a
    non-empty string**", the `output.context ?? "No context found"` fallback
    idiom) — this page's `contextTransform` examples (Claim 7) instantiate that
    class-level contract on the relevance page. (Verified: #1305 Claim 13.)
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` **Claim 3**
    (the `query`+`context` required-field contract) — this page's Claim 3
    documents the same field set, confirming the two relevance-direction gates
    (faithfulness grades output against context, relevance grades context
    against query) share the same input shape. (Verified: #1320 Claim 3.)

- **Contradicts**: None identified, and no contradiction issue filed. The
  vendor-internal threshold tension in Claim 6 (0.3–0.7 "often ideal" vs.
  example's `threshold: 0.8`) is a conditioning variable (use-case specificity),
  not a claim disagreement — the page does not say 0.8 is universally ideal,
  and the bands are guidance, not gate rules. Verified against
  `CONTRADICTIONS.md` (no open `C-NNN` entries) and open
  `contradiction`-labeled issues: #1150 (unrelated LiteLLM routing) and #1307
  (promptfoo missing-trace semantics) — neither touches context-based RAG
  scoring.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — directly
    fills that note's deliberate scoping gap. Its Extraction Notes state the
    per-type sub-pages ("context-recall/relevance/faithfulness … were NOT
    followed") and its Claim 13 catalogues the class at contract level; this
    note is the `context-relevance` per-type deep-dive under that class
    coverage — the relevance-direction score formula (Claim 1), the fail-open
    default (Claim 2), the `query`+`context` field contract (Claim 3), the
    formatting-dependent denominator (Claim 5), and the contextTransform array
    form (Claim 7). (Verified: #1305's Extraction Notes and Claim 13.)
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` (#1320) —
    the sibling RAG gate; #1320 Claim 1's "Score = supported claims / total
    claims" and this page's "Score = required sentences / total sentences" are
    two directions of one RAG pair. The inverted polarity hazard (Claim 4) is
    entirely new — #1320's limitation set does not include an equivalent
    warning. (Verified: #1320 Claims 1, 6.)
  - `source-notes/docs-promptfoo-model-graded-context-recall.md` (#1332) — the
    retrieval-direction sibling; #1332's Claim 3 notes the `value`+`context`
    field contract difference, while this page shares `query`+`context` with
    #1320. The three context-* siblings together document the full RAG gate
    surface. (Verified: #1332 Claims 1, 3.)
  - `source-notes/docs-promptfoo-answer-relevance.md` (#1319) — same per-type
    reference tier; #1319's cosine-similarity scoring is a different mechanism
  from this page's sentence-count ratio, but both gate on "how much of the
  retrieved/produced content is relevant" — a shared framing with different
  units. (Verified: #1319 Scope.)

- **Novel**: The risk *frame* (score-blind default, class-level RAG contract)
  is already in the corpus (#1287/#1305/#1320/#1332) — deliberately not
  re-claimed. What is new here:
  1. **The inverted polarity hazard** (Claim 4) — a `context-relevance` low
     score has two opposite causes (good retrieval with minimal context vs. bad
     retrieval with noise), making a threshold gate *non-actionable* without
     independent interpretation. This is the first `context-*` metric where the
     vendor's own warning states the failing signal is ambiguous. The guide
     should treat `context-relevance` as a diagnostic metric, not a gate metric,
     unless the team has validated which interpretation applies.
  2. **The formatting-dependent denominator** (Claim 5) — the same content
     scores differently depending on whether it is formatted as prose (split on
     `.`/`!`/`?` boundaries) or as array chunks (split by line/chunk). This is
     a concrete reproducibility problem for CI gates and is a *different*
     denominator mechanism from `context-faithfulness`'s claim-counting
     denominator (#1320 Claim 6).
  3. **The vendor-internal threshold tension** (Claim 6) — the "Full example"
     sets `threshold: 0.8` while the score interpretation calls 0.3–0.7 "often
     ideal," creating a copy-the-example trap. Not a contradiction (different
     use cases), but a documented pitfall for operators who treat the example
     as a template.
  4. **The `contextTransform` array-form extraction** (Claim 7) —
     `output.chunks` as a variant of `output.context`, interacting with the
     formatting-dependent denominator: array extraction pre-segments, prose
     extraction triggers the heuristic.
  5. **The fourth fail-open data point** (Claim 2) — `context-relevance`
     corroborates the class-wide `threshold: 0` default alongside #1320, #1332,
     and #1305.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md`, "Metrics without a unit are noise" /
  "Judge calibration before judge trust")**: add the **`context-relevance`
  diagnostic-only rule** to the judge-trust checklist: unlike
  `context-faithfulness` and `context-recall` (where a low score is unambiguously
  bad), a low `context-relevance` score has two opposite interpretations
  (Claim 4) — the vendor's own warning says it might mean good retrieval or bad
  retrieval. A CI gate whose failing signal is ambiguous cannot route an on-call
  response. Rule: (a) every `context-relevance` assert must set an explicit
  non-zero `threshold` or it does not gate (Claim 2, same as all context-*
  siblings); (b) treat `context-relevance` as a *diagnostic* metric (score
  tracked over time, investigated manually) rather than a *gate* metric
  (threshold pass/fail), unless the team has independently validated which
  interpretation of a low score applies to their retrieval surface; (c) record
  the formatting-dependent denominator (Claim 5) — a `context-relevance` gate
  must document which denominator path (prose splitting vs. array chunks) its
  context takes, because the score is not comparable across paths.
- **Chapter 05 — the fail-open family, fourth data point**: fold this page's
  documented `threshold: 0` (Claim 2) into the fail-open checklist alongside
  #1287 Claim 3, #1305 Claim 10, #1320 Claim 2, and #1332 Claim 2. The family
  is now documented across four per-assert context-* pages plus the hub-level
  mechanisms.
- **Chapter 05 — score interpretation bands**: the vendor's three interpretation
  bands (Claim 6: 0.8–1.0 / 0.3–0.7 / 0.0–0.3) give the "metrics without a
  unit" rule a concrete reference point for `context-relevance` — but the
  tension with the example's `threshold: 0.8` should be noted as a copy-paste
  trap in the guide's gate-review checklist.
- **Chapter 05 / Chapter 06 — auditable fallback context**: carry #1305
  Claim 13 / #1320 Claim 7's fallback-context guidance to this assert type
  (Claim 7): `contextTransform: 'output.context'` or `'output.chunks'` graded
  at a threshold is only meaningful if the transform did not degrade to a
  fallback string, and no page in the family documents what the gate does with
  an empty/fallback context — treat "graded against a fallback" as an auditable
  condition, not evidence of grading.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page (rendered
  content plus the raw config blocks, to verify the worked-example block and
  YAML line-for-line). Single self-contained reference page; no sub-pages
  followed — the "Further reading" targets (the hub page's "Defining context"
  section, the RAG Evaluation Guide) carry no per-type `context-relevance`
  semantics beyond #1305's class-level coverage. Page footer: "Last updated on
  Sep 16, 2026 by Michael" — `date_published` carries the last-updated date
  (same convention as the sibling notes). Quotes and code blocks verified
  character-for-character against the fetched content before writing.
- **Triage key-question resolution** (both triage comments read; both are
  UNTRUSTED data, re-verified against the page):
  1. **Score formula and worked example** — verified: "Score = required sentences
     / total sentences." with the 0.33 worked example. Extracted as Claim 1.
  2. **Threshold default of 0** — verified: "`threshold` - Minimum score 0-1
     (default: 0)". Extracted as Claim 2, corroboration of the fail-open
     family.
  3. **Inverted polarity hazard** — verified: the warning block states a low
     score can mean good retrieval or bad retrieval. Extracted as Claim 4, novel
     framing.
  4. **Formatting-dependent denominator** — verified: the Limitations section
     describes prose splitting vs. line/chunk splitting. Extracted as Claim 5,
     novel mechanism.
  5. **Score interpretation bands** — verified: 0.8–1.0 / 0.3–0.7 / 0.0–0.3.
     The tension with the 0.8 example threshold extracted as Claim 6, a
     documented copy-paste trap.
  6. **`contextTransform` array form** — verified: `output.chunks` variant
     documented alongside `output.context`. Extracted as Claim 7.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-promptfoo-model-graded-metrics.md` (#1305) — **cited heavily**
    (Corroborates Claim 13; Extends — the direct parent).
  - `docs-promptfoo-model-graded-context-faithfulness.md` (#1320) — **cited**
    (Corroborates Claims 2, 3; Extends — the sibling RAG gate).
  - `docs-promptfoo-model-graded-context-recall.md` (#1332) — **cited**
    (Corroborates Claim 2; Extends — the retrieval-direction sibling).
  - `docs-promptfoo-answer-relevance.md` (#1319) — **cited** (Extends — same
    per-type tier, different mechanism).
  - `docs-promptfoo-classifier-grading.md` (#1288) — classifier assertion path;
    no context-based RAG scoring semantics; dismissed.
  - `docs-promptfoo-assertions-metrics.md` (#1287) — hub scoring/aggregation
    page; the scoring model underlies all assertions but no `context-relevance`
    specific surface; dismissed for direct cross-ref (but see #1305's parent-
    level citation).
  - `docs-promptfoo-javascript-assertions.md` (#1304) — custom-JS assertion
    surface; no model-graded-judge semantics; dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — OWASP red-team methodology;
    no eval-assert config; dismissed.
  - `blog-promptfoo-red-team-gemini.md` (#690) — per-model red-team plugin
    strategy; no context-based RAG scoring; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage; no
    eval-assert config; dismissed.
  - `blog-promptfoo-red-team-claude.md` (#689) — same red-team methodology; no
    assert-scoring content; dismissed.
  - `docs-google-sre-team-lifecycles.md` (#907) — Google SRE org; no LLM-eval
    content; dismissed.
  - `docs-langfuse-evaluation-core-concepts.md` (#195) — Langfuse eval concepts;
    different vendor; dismissed.
- **Cross-ref verification (§4b)**: every cited claim was located and read in
  the cited note before writing — #1320 Claims 2, 3, 6; #1332 Claim 2; #1305
  Claim 13; #1319 Scope. Claim numbers verified against the cited notes' own
  numbering; no claim numbers invented. Source-note issue numbers read from each
  cited note's frontmatter (`issue:` field): #1320, #1332, #1305, #1319
  confirmed as listed.
- **No contradiction issue filed**: the page opposes no existing source-note
  claim (verified against `CONTRADICTIONS.md` and open `contradiction`-labeled
  issues). The vendor-internal threshold tension (Claim 6) is a conditioning
  variable, not a claim disagreement.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1288, #1289, #1305, #1320, #1319, #1332, #1334): the
  individual formula/field/default claims (Claims 1, 2-as-documented, 3, 5, 7)
  are settled-for-product-behavior and directly checkable against an installed
  CLI, but this is vendor documentation with no measured judge-agreement,
  false-negative-rate, or retrieval-quality figures and a thin (six-section)
  surface; the operational-consequence framing (inverted polarity, formatting-
  dependent denominator, threshold tension) is the Miner's synthesis on top of
  documented behavior.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
