---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/context-faithfulness/
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Context Faithfulness"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-14
date_extracted: 2026-09-14
last_checked: 2026-09-14
status: current
confidence_overall: emerging
issue: "#1320"
---

# Promptfoo Configuration: Model-Graded — Context Faithfulness

> The per-type vendor reference page for promptfoo's `context-faithfulness`
> RAG assertion — the page that answers the model-graded hub note's (#1305)
> deliberately-unmined `context-*` sub-pages with the score contract
> (`Score = supported claims / total claims`), the **`threshold` default of
> `0`** (a bare `context-faithfulness` assert is score-blind: it passes a
> fully-unsupported response at score 0 — the second independently documented
> instance of the same fail-open family as `llm-rubric`'s score-blind pass
> and the hub's `threshold: 0` trap), the `query`+`context` required-field
> contract, array-valued and `contextTransform`-extracted contexts, the
> per-assert judge override (`provider: gpt-5`), and the vendor's three
> documented limitations — of which "May miss implicit claims" is a
> *false-negative* bound on the gate (unfaithful claims the judge cannot see
> are silently excluded from scoring).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Context
  faithfulness" per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own assert-type behavior — authoritative for *what promptfoo does*
  with a given `context-faithfulness` config (the score formula, the threshold
  default, the required fields, the override surface), but vendor-positioned:
  the page carries no measured judge-agreement, false-negative-rate, or
  calibration figures and no independent practitioner validation. Everything
  below is checkable against an installed CLI.
- **Scope**: A thin, five-section reference page (intro+worked example,
  Configuration, Limitations, Related metrics, Further reading). It is the
  deep-dive on the `context-faithfulness` member of the context-based RAG
  assertion class that `docs-promptfoo-model-graded-metrics.md` (#1305)
  catalogued at claim level only — that note explicitly records
  "context-recall/relevance/faithfulness … were NOT followed." This page
  therefore carries the *delta* (score formula, default threshold, field
  contract, array context, per-type override), not a re-extraction of the
  model-graded framing. Does NOT cover the sibling `context-recall` /
  `context-relevance` pages (separate sources, per the one-note-per-sub-page
  convention), `query`/`context` plumbing beyond this page, or the
  empty/fallback-context behavior — the page itself does not document that.
- **Last updated**: the page footer reads "Last updated on Sep 14, 2026 by
  renovate[bot]"; the worked examples describe the current `gpt-5` era.

## Extracted Claims

### Claim 1: `context-faithfulness` grades a response by claim-support ratio against the provided context — "Score = supported claims / total claims" — demonstrated with a worked example where only the capital claim is supported, scoring 0.5
- **Evidence**: The page's "How it works" statement and the inline "Example"
  block (`Context: "Paris is the capital of France."` / `Response: "Paris,
  with 2.2 million residents, is France's capital."` / `Score: 0.5 (capital ✓,
  population ✗)`).
- **Confidence**: settled (documented formula and worked arithmetic; verifiable
  against an installed CLI)
- **Quote**: "Extracts factual claims from the response, then verifies each against the context. Score = supported claims / total claims." and "Score: 0.5 (capital ✓, population ✗)"
- **Our assessment**: The metric's unit, stated explicitly — the one place the
  guide's "metrics without a unit are noise" rule gets its concrete anchor for
  RAG faithfulness: a response with two claims, one supported, scores exactly
  0.5, not "somewhat faithful." Operationally the formula makes the score
  depend on the judge *counting* claims correctly; every missing or extra claim
  the judge registers changes both numerator and denominator (see Claim 5).
  The worked example is a passing-sounding answer (plausible, capital correct)
  that fails a 0.9 threshold — the "a plausible answer is not a passing answer"
  anchor the triage flagged.

### Claim 2: The page documents `threshold` with "(default: 0)" — at default config a `context-faithfulness` assert is score-blind and passes a response with zero supported claims (score 0 ≥ threshold 0)
- **Evidence**: The "Required fields" list entry: "`threshold` - Minimum score 0-1 (default: 0)". The vendor states the default; the page nowhere recommends a non-zero threshold, and every example that actually gates sets an explicit `threshold: 0.9`/`0.8`.
- **Confidence**: settled for the documented default; the pass-at-0 reading is
  Miner synthesis on documented behavior (the formula in Claim 1 + the default)
- **Quote**: "`threshold` - Minimum score 0-1 (default: 0)"
- **Our assessment**: The triage's key question resolves *as suspected, but with
  a boundary the vendors never spell out*: because the pass condition is
  `score >= threshold` (the hub's scoring model, #1287 Claim 1) and the default
  threshold is `0`, a faithful-historical answer scores `0`, `0 >= 0` holds, and
  the assert passes — a fully-unsupported response that the gate exists to catch.
  This is inference from the documented formula and default, not a vendor
  statement — the page never says "a bare assert passes everything." Whether the
  judge *also* consults a `pass` field (the `llm-rubric` mechanism, #1305
  Claim 10) is not stated on this page; the score-blind failure is established
  by the default alone. For Ch05: a bare `assert: - type: context-faithfulness`
  is decorative unless a threshold is explicitly set.

### Claim 3: The assert takes two required inputs — `query` ("User's question (in test vars)") and `context` ("Reference text (in vars or via `contextTransform`)") — making it a RAG-specific gate that grades the response against retrieved context, not against a rubric
- **Evidence**: The "Required fields" list's first two entries, plus the "Full example" config wiring both into `tests.vars`.
- **Confidence**: settled (documented field contract)
- **Quote**: "`query` - User's question (in test vars)" and "`context` - Reference text (in vars or via `contextTransform`)"
- **Our assessment**: Both-required is the distinguishing contract versus the
  rubric-based model-graded asserts (`llm-rubric`, `g-eval`): the faithfulness
  verdict is *grounded by construction* — there is no rubric to iterate, the
  ground truth is the retrieved context. That is the property the assert
  family exists to check (no information beyond what was retrieved), and it
  makes the *context* the whole security-relevant input: whatever lands in
  `context` (see Claim 5 and the `contextTransform` fallback question in
  Extraction Notes) is what claims are verified against.

### Claim 4: `context` can be an array of documents, and can be extracted dynamically from the provider response via `contextTransform` (worked form: `contextTransform: 'output.context'`) — the RAG plumbing this page contributes to the parent note's class-level coverage
- **Evidence**: The "Array context" subsection (three-document France example
  with `threshold: 0.8`) and the "Dynamic context extraction" subsection
  ("For RAG systems that return context with their response:" with
  `# Provider returns { answer: "...", context: "..." }` and
  `contextTransform: 'output.context' # Extract context field`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "Context can also be an array:" and "For RAG systems that return context with their response:" and "`contextTransform: 'output.context'` # Extract context field"
- **Our assessment**: Two concrete forms the parent note (#1305) described only
  abstractly. The array form matters for chunked retrieval — the judge verifies
  against a document set, not one string, which changes how an operator audits
  "what was the context" after a green run. The `contextTransform` form is the
  per-type instance of #1305 Claim 13's "must return a non-empty string"
  contract, and it inherits that note's fallback warning: a transform emitting a
  fallback string (the `output.context ?? "No context found"` idiom) is still
  the context the judge grades against, and after a green pass nothing on this
  page or the parent's marks that it was a fallback.

### Claim 5: The per-assertion judge can be overridden inline via `provider: gpt-5`, so the faithfulness judge is a config-swappable model — and, per the parent note, an *unpinned* one when the override is absent
- **Evidence**: The "Custom grading" subsection: "Override the default grader:"
  with `type: context-faithfulness`, `provider: gpt-5 # Use a different model for grading`, `threshold: 0.9`.
- **Confidence**: settled for the override mechanism (documented); the unpinned-default consequence is the parent note's #1305 Claim 1 finding applied here
- **Quote**: "Override the default grader:" and "`provider: gpt-5` # Use a different model for grading"
- **Our assessment**: The page documents the override surface but says nothing
  about what the *default* grader is; #1305 Claim 1 supplies that — promptfoo's
  built-in grading provider picks its model from whatever credentials are in the
  environment. So a `context-faithfulness` gate is judged by an ambient,
  unpinned model unless `provider:` (or the parent's global override chain) is
  set — the judge half of the gate is as non-hermetic as every other model-graded
  assert. Note the override here is the shorthand form (`gpt-5`); per #1305
  Claim 2 the shorthand blocks inheritance of a global provider object's
  `config` — relevant only if a team configures a full provider object globally.

### Claim 6: The vendor documents three limitations — "Depends on judge LLM quality", "May miss implicit claims", "Performance degrades with very long contexts" — the middle of which is a false-negative bound on the gate
- **Evidence**: The "Limitations" list (three bullets, no elaboration).
- **Confidence**: settled (vendor-documented limitations); the false-negative framing is the Miner's reading
- **Quote**: "Depends on judge LLM quality" and "May miss implicit claims" and "Performance degrades with very long contexts"
- **Our assessment**: The honest reliability bound for a CI gate, and the
  sharpest line on the page. "May miss implicit claims" means a fabricated claim
  the judge does not register *as a claim* drops out of the denominator, so the
  score says the response is fully supported when it actually introduces an
  unsupported fact the judge couldn't see — an unfaithful output that passes
  *silently*, with nothing in the pass/fail report to distinguish it from a
  genuinely-faithful green. That is exactly the RAG case this assert type was
  added for, which is why "green faithfulness" cannot be read as "faithful."
  The long-context bullet is the operational sibling of the self-hosted-judge
  capacity warnings on the parent page: graders that lose claim-extraction
  fidelity on long input are another silent-quality gradient, not a crash.

### Claim 7: The page states no behavior for an empty or fallback context — the parent note's open question is subsumed at default config (score-blind per Claim 2) but remains unanswered for any explicitly-thresholded gate
- **Evidence**: Search of the page for empty/fallback/null/`contextTransform`
  behavior: the only `contextTransform` reference is the `output.context`
  extraction example (Claim 4); no sentence anywhere describes what the judge
  does with an empty context or a fallback string. "Further reading" links only
  to the parent page's "Defining context" section and the RAG guide.
- **Confidence**: settled that the documentation is absent (verifiable by
  reading the page); the moot-at-default reasoning is the Miner's synthesis
- **Quote**: (no direct quote; see paraphrase in Our assessment — the absence
  is the finding)
- **Our assessment**: #1305 Claim 13 left standing the question "the page does
  not state what `context-faithfulness` does with an empty or fallback context."
  This page still does not state it — the question is *partially* resolved, not
  literally answered. What is newly established is Claim 2's documented default:
  at default config the gate never gates on score, so the empty-context
  vacuous-pass scenario the hub note worried about is moot — a bare assert
  passes a score-0 response whether the context was real or a fallback string.
  But once an operator sets a threshold (which Claim 2 makes necessary for the
  gate to be meaningful), the empty/fallback-context behavior is *still*
  undocumented. Record as partially-open rather than closed, and do not invent
  the vendor's answer.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/context-faithfulness/.

### Worked example (verbatim from the page intro "Example")

```
Context: "Paris is the capital of France."
Response: "Paris, with 2.2 million residents, is France's capital."
Score: 0.5 (capital ✓, population ✗)
```

### Configuration (verbatim from "Configuration" and "Required fields")

```yaml
assert:
  - type: context-faithfulness
    threshold: 0.9 # Require 90% of claims to be supported
```

Required fields (verbatim from the list):

- `query` - User's question (in test vars)
- `context` - Reference text (in vars or via `contextTransform`)
- `threshold` - Minimum score 0-1 (default: 0)

### Full example (verbatim from "Full example")

```yaml
tests:
  - vars:
      query: 'What is the capital of France?'
      context: 'Paris is the capital and largest city of France.'
    assert:
      - type: context-faithfulness
        threshold: 0.9
```

### Array context (verbatim from "Array context")

```yaml
tests:
  - vars:
      query: 'Tell me about France'
      context:
        - 'Paris is the capital and largest city of France.'
        - 'France is located in Western Europe.'
        - 'The country has a rich cultural heritage.'
    assert:
      - type: context-faithfulness
        threshold: 0.8
```

### Dynamic context extraction (verbatim from "Dynamic context extraction")

```yaml
# Provider returns { answer: "...", context: "..." }
assert:
  - type: context-faithfulness
    contextTransform: 'output.context' # Extract context field
    threshold: 0.9
```

### Custom grading (verbatim from "Custom grading")

```yaml
assert:
  - type: context-faithfulness
    provider: gpt-5 # Use a different model for grading
    threshold: 0.9
```

### Limitations (verbatim from "Limitations")

- Depends on judge LLM quality
- May miss implicit claims
- Performance degrades with very long contexts

Related metrics (verbatim from "Related metrics"): `context-relevance` - "Is
retrieved context relevant?"; `context-recall` - "Does context support the
expected answer?"

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 10** (the
    llm-rubric result `{"pass": true, "score": 0}` passes without a threshold —
    "Without threshold: PASS depends only on the grader's `pass` field (defaults
    to `true` if omitted)") — this page's documented `threshold: 0` default
    (Claim 2) is the *same score-blind failure family* on a different assert
    type, now with a vendor-documented default rather than an omitted-value
    default. The two pages together establish the family, not a one-off.
    (Verified: #1305 Claim 10.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 3** (a test-case
    `threshold` of `0` makes the case pass regardless of individual assertion
    failures) — the config-level member of the same family; this page extends
    the pattern from the test-case aggregation level (#1287) to the
    per-assertion level (promptfoo's own nomenclature, "Required fields" lists
    `threshold` per assert). (Verified: #1287 Claim 3.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 13** (the
    context-based RAG class: `contextTransform` "must return a non-empty string",
    the `output.context ?? "No context found"` fallback idiom, the
    `JSON.stringify` debug form) — this page's array-context form and
    `contextTransform: 'output.context'` extraction example (Claim 4) instantiate
    that class-level contract on the per-type page. (Verified: #1305 Claim 13.)
  - `source-notes/docs-promptfoo-classifier-grading.md` **Claim 9** ("model-graded
    evals are also a good choice for some of these evaluations, especially if you
    want to quickly tune the eval to your use case") — the tune-vs-fixed choice
    the classifier note positions; the `provider: gpt-5` override (Claim 5) is
    the per-assert tuning surface for RAG faithfulness that note's framing
    implies. (Verified: #1288 Claim 9.)

- **Contradicts**: None identified, and no contradiction issue filed. Checked
  `CONTRADICTIONS.md` (no open `C-NNN` entries) and open
  `contradiction`-labeled issues: #1150 (unrelated LiteLLM routing) and #1307
  (promptfoo missing-trace semantics: built-in `trace-*` throwing vs custom-JS
  silent-pass). **#1307 is related-vendor context, not a conflict with this
  page** — it pits two assert families on the trace data axis; `context-faithfulness`
  consumes *context*, not traces, and opposes no claim on either side of #1307.
  The score-blind default (Claim 2) complements, rather than opposes, the
  fail-open traps already in the corpus (#1287 Claims 3/4, #1305 Claim 10); this
  page does not disagree with any existing source-note claim.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — directly
    fills that note's deliberate scoping gap. Its Extraction Notes state the
    per-type sub-pages ("context-recall/relevance/faithfulness … were NOT
    followed"), and its Claim 13 raises the empty-context question this page now
    bounds (Claim 7). This note is the per-type deep-dive under Claim 13's
    class-level coverage: score formula (Claim 1), the `threshold: 0` default
    (Claim 2), the required-field contract (Claim 3), the array/
    `contextTransform` forms (Claim 4), and the per-assert judge override
    (Claim 5). The `llm-rubric` score-blind mechanism (#1305 Claim 10) and this
    page's threshold-default mechanism are now two documented members of one
    family.
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 1** (the
    vendor's own deterministic/model-graded boundary — `select-best` etc. "use an
    additional model or external inference service") — this page sits firmly on
    the model-graded side of that line (claim-verification is performed by a
    judge LLM, Claim 1/5), the RAG counterpart to that note's "free to rerun"
    deterministic tier. (Verified: #1289 Claim 1.)

- **Novel**: The risk *frame* (score-blind / silent-green gates) is not new —
  it is already in the corpus as the hub's `threshold: 0`/`weight: 0` traps
  (#1287 Claims 3/4) and `llm-rubric`'s score-blind pass (#1305 Claim 10). What
  is new here:
  1. **The `context-faithfulness` score contract in full** (Claim 1) — the
     exact `supported claims / total claims` formula with the worked 0.5
     example; the per-type reference-level unit definition the guide's
     "metrics without a unit" rule wants for RAG faithfulness.
  2. **The second, independently documented instance of the fail-open family**
     (Claim 2) — `threshold` sets **to `0` by default** for a *score* metric,
     so at default config the assert passes score 0. Not an omitted-field
     default (`llm-rubric`) and not a test-case-level value (#1287) — a native
     per-assert default on this type.
  3. **The both-required `query`+`context` contract** (Claim 3) and the
     **array-context form** (Claim 4) — the RAG grounding surface, absent from
     the parent note.
  4. **The documented false-negative limitation** (Claim 6) — "May miss implicit
     claims" as a vendor-stated bound that silently passes unfaithful output; the
     first explicitly-*negative* reliability bound the corpus has for a
     model-graded RAG gate.
  5. **The status of the #1305 Claim 13 open question** (Claim 7) — the page
     still does not document empty/fallback-context grading; the vacant question
     is *partially* closed only in the score-blind-at-default sense, with the
     thresholded case still open. A precise record of an unresolved question is
     itself corpus value (the Assayer can verify the absence).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md`, "Metrics without a unit are noise" /
  "Judge calibration before judge trust")**: add the **RAG-faithfulness gate
  rule** to the judge-trust checklist (extending the #1287/#1305 fail-open
  material): a bare `assert: - type: context-faithfulness` is *decorative* —
  the documented `threshold` default is `0`, so the gate passes every response
  including a fully-unsupported one at score 0 (Claims 1-2). Rule:
  (a) every `context-faithfulness` assert must set an explicit non-zero
  `threshold`, or it does not gate; (b) "can this gate fail?" is now a
  per-assert review item exactly as it was for test-case thresholds in #1287
  Claim 3 — and a negative control (an intentionally unsupported answer) should
  appear in the eval to prove the gate discriminates; (c) record the
  false-negative bound from Claim 6 — "May miss implicit claims" means a green
  faithfulness run evidences only that the judge *found no unsupported claims it
  could register*, not that the response is faithful — downgrading what a green
  RAG gate may be claimed to prove. This page also gives the concrete "unit" for
  Judge Calibration: the score maps to claim-count ratio, so a calibrated judge
  is one whose claim extraction agrees with human extraction.
- **Chapter 05 — RAG observability / Ch02 gate semantics**: carry #1305
  Claim 13's auditable-condition guidance forward with this page's per-type
  form: `contextTransform: 'output.context'` returning a fallback string (the
  `?? "No context found"` idiom) becomes the grading context, and — because the
  page still documents nothing for empty/fallback contexts (Claim 7) — a team
  cannot distinguish "graded against real retrieval" from "graded against a
  fallback" in the pass/fail report. Treat a fallback/empty context as an
  auditable condition (log the transformed context, surface it in the report),
  not as evidence of grading; at default threshold the gate passes regardless
  (Claim 2).

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page (both the
  rendered markdown and the raw HTML, to verify the worked-example code block
  line-for-line). Single self-contained reference page; no sub-pages followed —
  the "Further reading" targets (parent page's "Defining context", the RAG
  Evaluation Guide) carry no per-type semantics not already in #1305. "Last
  updated on Sep 14, 2026 by renovate[bot]" — page undated, so `date_published`
  carries the last-updated date (same convention as the sibling notes). Quotes
  and code blocks verified character-for-character against the fetched HTML
  before writing.
- **Triage key-question resolution**: the triage's fail-open reading of the
  `threshold: 0` default **holds** — the page lists "`threshold` - Minimum score
  0-1 (default: 0)" under Required fields and never recommends a non-zero
  default. The pass-at-score-0 consequence is flagged in Claim 2 as synthesis on
  the documented formula + default (the vendor never states the consequence —
  per the triage, "the fail-open reading is our synthesis from the documented `0`
  default, not a vendor claim"). I did not take the Prospector's three divergent
  verdicts as established; each was re-verified against the page independently.
  Note the triage conflict on the empty-context question: comments disagree
  ("keep open as still-open" vs "the empty-context case is moot"). Resolution
  recorded in Claim 7: the *documented silence* is unchanged (still-open for any
  thresholded gate), while the *vacuous-pass concern* is moot at default config
  because Claim 2's score-blind pass subsumes it. Both half-truths preserved,
  neither invented.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `docs-promptfoo-model-graded-metrics.md` (#1305) — **cited heavily**
    (Corroborates Claims 10/13; Extends — the direct parent).
  - `docs-promptfoo-assertions-metrics.md` (#1287) — **cited** (Corroborates
    Claim 3).
  - `docs-promptfoo-classifier-grading.md` (#1288) — **cited** (Corroborates
    Claim 9).
  - `blog-promptfoo-red-team-gemini.md` (#690) — per-model red-team plugin
    strategy and reasoning-DoS testing; uses rubric/latency asserts as tools but
    carries no model-graded scoring semantics; dismissed.
  - `blog-promptfoo-red-team-claude.md` (#689) — same red-team plugin
    methodology; no assert-scoring content; dismissed.
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — OWASP red-team
    methodology/SDLC; no scoring semantics; dismissed.
  - `docs-promptfoo-javascript-assertions.md` (#1304) — custom-JS assertion
    surface; its `context.trace` silent-pass guard (#1307 Side A) is a
    trace-data concern, not a model-graded scoring concern; no shared claims;
    dismissed.
  - `docs-google-sre-team-lifecycles.md` (#907) — Google SRE org/lifecycle
    chapter; no LLM-eval content; dismissed.
  - `docs-langfuse-evaluation-core-concepts.md` (#195) — Langfuse eval concepts;
    different vendor/harness; no promptfoo assert-config; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage by an SRE
    Agent using LLM-as-judge *alerts*; no eval-assert config; dismissed.
  - `docs-promptfoo-deterministic-metrics.md` (#1289) — not in the candidate
    list as written but surfaced in `source-notes/` per MINER.md §4; **cited**
    (Extends, Claim 1).
- **Cross-ref verification (§4b)**: every cited claim was located and read in
  the cited note before writing — #1305 Claims 1, 2, 10, 13 (+ Extraction Notes
  sub-page-following statement), #1287 Claims 1, 3, #1288 Claim 9, #1289
  Claim 1. Claim numbers verified against the cited notes' own numbering; no
  claim numbers invented. Source-note issue numbers read from each cited note's
  frontmatter (`issue:` field): #1305, #1287, #1288, #1289 confirmed as listed.
- **No contradiction issue filed**: the page opposes no existing source-note
  claim (verified against `CONTRADICTIONS.md` — no open `C-NNN` entries — and
  open `contradiction`-labeled issues #1150/#1307). The score-blind default
  *joins* the corpus's existing fail-open family rather than conflicting with
  it; #1307 is cross-surface vendor context (trace data), not opposition.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1288, #1289, #1305): the individual default/formula claims
  (Claims 1, 3-5) are settled-for-product-behavior and directly checkable
  against an installed CLI, but this is vendor documentation with no measured
  judge-agreement or false-negative figures and a thin (five-section) surface;
  the operational-consequence framing (score-blind default, false-negative
  bound, partial-open empty-context record) is the Miner's synthesis on top of
  documented behavior.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.