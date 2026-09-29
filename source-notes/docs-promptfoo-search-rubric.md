---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/search-rubric
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Search Rubric"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-28
date_extracted: 2026-09-28
last_checked: 2026-09-28
status: current
confidence_overall: emerging
issue: "#1485"
---

# Promptfoo Configuration: Model-Graded — Search Rubric

> The per-type reference page for promptfoo's `search-rubric` assertion — the
> model-graded tier's only **live-web** grader, and the delta the hub note
> (#1305) explicitly left on the table when it summarized this page into a
> single Claim 12. This page contributes the corpus's **first and only
> documented instance of a score-inverting negation** — a negated result scores
> `1 - score`, clamped to `[0, 1]`, and the vendor's stated reason is
> *aggregation* rather than polarity (Claim 1) — the **fourth statement of the
> family's inverted-form fail-closed property** in wording that is otherwise
> character-identical to the g-eval and llm-rubric pages (Claim 2), the
> **verdict contract's preserve-don't-invert clause** placed in the *How it
> works* section rather than the negation section, which is what keeps the
> `1 - score` clamp from reading as a silent-pass on grader outage (Claim 3), a
> **pre-flight rubric type check** that rejects non-string rubrics *before* the
> grading provider is called (Claim 4), a **documented expected-failure
> semantics for SUT refusals** that makes a `search-rubric` gate partly a
> measurement of the SUT's web reachability rather than its answer quality
> (Claim 5), a **vendor-endorsed tolerance band** that is the false-red
> counterpart to the guide's existing false-green threshold table (Claim 6),
> and a **second, tool-carrying grader-pinning location** in a `grading:` block
> that the corpus had zero occurrences of (Claim 7). Net: this is the
> model-graded tier's only assert whose *ground truth is a live third-party
> corpus*, and every gate-design rule in Ch05 needs a "and can it go red for
> the wrong reason?" counterpart to sit beside its existing "can it go green
> for the wrong reason?" rule.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Search-Rubric"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`, sitting between
  `model-graded-closedqa` and `select-best` in the sidebar)
- **Author credibility**: Promptfoo, Inc. — the product's own maintainers.
  First-party and therefore authoritative for *what promptfoo does with a given
  config*, and every mechanism claim here is checkable against an installed
  CLI. It is **not** independent evidence: no measured gate-failure rate, no
  judge-agreement figure, no latency or flake measurement, and no practitioner
  report appears anywhere on the page. The cost list is the vendor's own and is
  dated "As of November 2025" (already extracted in #1305 Claim 12; deliberately
  not re-extracted here).
- **Scope**: the whole page — the `search-rubric` / `not-search-rubric` assert
  type, its verdict contract, rubric-input validation, the five web-search
  grading providers and their tool configs, threshold semantics, the vendor's
  expected-behavior table, and four troubleshooting entries.
  **Not covered, and not available anywhere in the corpus**: what the grader
  does with the *content* of the search results, how a search-rubric verdict
  interacts with `agent-rubric`, and any runtime/observability surface. The page
  contains **no `metadata` field of any kind** — see Claim 3's assessment.
- **Page currency**: footer reads "Last updated on **Sep 28, 2026** by
  **mldangelo-oai**". The page is undated (no publish date), so
  `date_published` carries the last-updated date, the same convention as the
  sibling notes (#1287/#1289/#1305/#1349/#1471/#1483/#1484). This is a
  user-maintained page (not a bot), and its model IDs are `gpt-5.1` /
  `claude-opus-4-6` / `gemini-3.1-pro-preview` / `grok-4.3` — the current
  generation, one step ahead of the `gpt-5` / `claude-sonnet-4-5` /
  `gemini-2.5-pro` roster in #1471 Claim 5.

## Extracted Claims

### Claim 1: `not-search-rubric` inverts the **score**, not just the boolean — a negated result scores `1 - score` clamped to `[0, 1]`, and the vendor's stated reason is that negation must aggregate correctly under `threshold` and weighted scoring, not merely flip a pass flag
- **Evidence**: the "Negation with `not-search-rubric`" section, immediately
  after the worked negated assert. The stated rationale is the load-bearing
  part: aggregation is named as the reason the score moves, not the polarity.
- **Confidence**: settled (documented product behavior)
- **Quote**: "`not-search-rubric` passes when the rubric criterion does **not**
  match. The score is inverted alongside `pass` — a negated result scores
  `1 - score`, clamped to `[0, 1]` — so negated assertions aggregate correctly
  under `threshold` and weighted scoring."
- **Our assessment**: This is the note's highest-value claim and it is new to
  the corpus — grep for `not-search-rubric` and for score-inversion semantics
  across all 200+ notes returns **zero hits**; the hub note records only that
  `search-rubric` exists and what it costs (#1305 Claim 12), and the family's
  other negation claims (#1305 Claim 4, #1349 Claim 5, #1471 Claim 7, #1483
  Claims 1/3) all describe inversion as a *polarity* flip plus a fail-closed
  guarantee, never as a *score* transform.

  Two consequences follow, and only the first is the vendor's.

  1. **(Vendor's stated reason.)** If inversion flipped only `pass`, a
     *strongly* satisfied "criterion NOT met" verdict (grader score 0.9) would
     enter an average as 0.9 — indistinguishable from a rubric the output
     almost met. The `1 - score` form is what makes a negated assert's
     contribution monotone in the correct direction under any weighted
     aggregation, which is the mechanism #1472 (`max-score`) Claims 3 and 4
     describe as `sum(score × weight) / sum(weights)` with weights keyed by
     assertion type. **The clamp is the part that matters for a gate**: an
     inverted score is bounded to `[0, 1]`, so a grader that returns an
     out-of-range score cannot leak a negative or >1 contribution into the
     aggregate. Nothing else in the family's negation documentation mentions a
     clamp.
  2. **(Our synthesis — flag for a resolver, not a vendor claim.)** The page
     documents the `1 - score` transform for the *score* and says nothing about
     the *threshold* on a negated assert. A per-assert `threshold` written
     against a positive rubric therefore does not obviously carry over: if
     `score ≥ 0.9` is the bar for "criterion met", the negated form's bar is
     `1 - score ≥ t`, i.e. `t' = 1 - t`. The page does **not** state whether
     promptfoo re-derives the threshold for the `not-` form or leaves the
     operator's number untouched, and I did not find it documented elsewhere
     in `source-notes/`. This is an open question, recorded here rather than
     guessed — but it is a real gate-design trap either way, because the
     *meaning* of the number inverts with the score. An operator reusing a
     calibrated `threshold: 0.9` on a `not-search-rubric` should re-derive it.

### Claim 2: `not-search-rubric` is fail-closed in both directions — the fourth statement of the family's inversion guarantee, in wording character-identical to the g-eval and llm-rubric pages except for one word, and still scoped to the inverted form only
- **Evidence**: the sentence following the negation paragraph on the same page.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Transport or parse failures from the grader are reported as
  failures in both directions — a grader error is not treated as evidence that
  the criterion was or was not met, so inversion never silently turns a failed
  search call into a pass."
- **Our assessment**: Corpus bookkeeping, precisely, because the counts matter
  for how confidently the guide can state a family rule. The long sentence
  appears **verbatim on three pages now**: `not-g-eval` (#1349 Claim 5),
  `not-llm-rubric` (#1471 Claim 7), and `not-search-rubric` here — the three
  differ only in the final noun phrase ("a failed grader call" →
  "a failed search call"). #1305 Claim 4 states the same *property* in
  different wording for `not-trajectory:goal-success`, so four pages state it
  and three share an identical string.

  What this does **not** do, and what I therefore do not claim: it does not
  resolve #1305 Claim 4's asymmetry finding. That finding is that the property
  is documented for the **inverted** form only. This page is again about the
  inverted form. The corpus's only statement covering the *positive*
  polarity is #1483 (`model-graded-closedqa`) Claim 3, which says grader errors
  and malformed responses "fail both forms with score `0`" — a claim about the
  score, on a different assert type. So the correct summary after four pages is
  still: **every `not-` section mined so far carries the sentence; the positive
  form is documented on exactly one page and nowhere else.** #1471 Claim 7's
  operational advice — treat a *missing* fail-closed sentence on a new assert
  type as a question for the vendor, not as an implied pass — is reinforced, and
  `search-rubric` is not an exception to it.

  The genuinely new part is the **search-specific consequence**, which is a real
  SRE surface rather than a wording data point: because the failure direction is
  failure, a judge's *search* failure (timeout, provider error, empty result
  set) presents as a **red gate**, not a pass. The correct direction, yes — but
  it converts the grader's network egress into a gate dependency. The flake
  rate of a `search-rubric` gate is a function of the judging provider's
  connectivity, not only of the system under test. That belongs next to #1471
  Claim 2's "fails loudly on the wrong shapes" finding and next to the guide's
  judge-trust rules as an availability consequence, not a correctness one.

### Claim 3: The verdict contract is lenient on **formatting** and strict on **absence** — and the `not-` form *preserves* grader failures rather than inverting them, stated in the "How it works" section rather than in the negation section
- **Evidence**: the fourth and fifth paragraphs of "How it works", plus the
  four-step procedure list immediately above them ("The grader must return a
  JSON object…", "Provider errors, empty responses, and responses without a
  valid verdict…"). The page's only sample grader contract.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The grader must return a JSON object with a boolean `pass` field.
  JSON inside Markdown or surrounding text is accepted. Provider errors, empty
  responses, and responses without a valid verdict fail with a score of `0`;
  `not-search-rubric` preserves these grader failures instead of inverting
  them."
- **Our assessment**: Read as a contract, this sentence is *lenient in the wrong
  place to be strict and strict in the right place*. Formatting tolerance
  ("JSON inside Markdown or surrounding text is accepted") is generous; the
  strictness is reserved for the case that actually matters for a gate — no
  verdict at all. Combined with Claim 1, the page is internally consistent in a
  way that is worth recording explicitly, because a reader working from the
  negation section alone would compute `1 - 0 = 1` and conclude that a grader
  outage **passes** a `not-search-rubric` "must not" gate. It does not: the
  How-it-works sentence forecloses exactly that reading, and the `[0, 1]` clamp
  in Claim 1 is what leaves `0` in range to be preserved rather than flipped.
  Two pages in this family make adjacent statements that a reader has to
  combine carefully (#1483 Claims 2/3 do the same for the `Y`/`N` suffix parse);
  this page is the cleaner case because it puts both halves in one sentence.

  The tolerant parse is also the mechanism behind a hazard the corpus already
  knows: #1305 Claim 5 records that scratchpad/thinking text "can score
  scratchpad sentences or attribution markers" when a judge emits reasoning
  before its verdict. Accepting JSON embedded in surrounding text is what keeps
  a reasoning-leaking judge *parseable* — and a judge that parses despite
  leaking reasoning is a judge whose verdict you cannot audit from the score
  column. Tolerance and misgrade are two faces of one design choice, and this
  page is the third place the family documents the tolerant parse (after
  #1305 Claim 5 and #1483 Claim 5's expected-scratchpad case).

  **Documented absence, and it matters operationally**: unlike `closedqa`
  (#1483 Claim 3, which records `metadata.graderError: true` as the
  discrimination signal), this page names **no** `metadata` field, and no
  grader-error marker of any kind. So on `search-rubric` a grader outage and a
  genuinely wrong answer are both score `0` with nothing to tell them apart in
  the report. I am **not** claiming promptfoo's implementation lacks such a
  marker — only that this page, which is the only documentation of this assert
  type, does not mention one, so a guide rule that says "read assertion metadata
  to separate a grader error from a model disagreement" is currently
  **unsupported for `search-rubric`**.

### Claim 4: The rubric `value` must render to a string and non-string types are rejected **before** the grading provider is called — a pre-flight validation that is the exact inverse of the interpolate-everything default the hub documents for the same input
- **Evidence**: the fifth paragraph of "How it works", the whole of the claim.
  Read together with the page's own examples, two of which use a YAML block
  scalar (`value: |`, in Concrete Artifacts).
- **Confidence**: settled (documented product behavior)
- **Quote**: "The rubric `value` must render to a string. Numbers, booleans,
  arrays, and objects are rejected before calling the grading provider."
- **Our assessment**: New to the corpus — no note in `source-notes/` records a
  rubric *type* validation. Its value is highest as a contrast, because the two
  rules sit on opposite sides of the same boundary and an operator will hit
  both. #1305 Claim 9 documents the permissive side: objects in `{{output}}` /
  `{{rubric}}` are JSON-stringified *for you* by default, and you have to set
  `PROMPTFOO_DISABLE_OBJECT_STRINGIFY=true` to opt out. So: an object that
  arrives **through interpolation** is silently stringified, while an object or
  number written **as `value:`** is rejected outright. Same input data,
  opposite handling, decided by which side of the boundary it came in on.

  Two operational consequences, both grounded in the page's own examples:

  - **A YAML list of rubric criteria is rejected.** The multi-criteria rubrics
    on this page are written as `value: |` block scalars precisely because a
    list of bullet criteria would be an *array* — one of the four rejected
    types. The block scalar is not a style choice; it is the only shape in
    these examples that renders to a string while reading as a structured
    rubric. (Cross-check: #1289 Claim 5 documents the opposite failure for a
    deterministic assert — `value: 0` on `contains` matches any output
    containing the character `0`. So a numeric `value` is a *silent
    match-anything* footgun on `contains` and a *loud rejection* here. Same
    config smell, opposite blast radius, which is exactly why Ch05's
    per-type-defaults rule has to stay per-type.)
  - **The rejection is free and loud; the verdict-level failures in Claim 3 are
    quiet and paid for.** A bad `value` type raises before any provider call —
    no tokens, no search fee, no false red to triage. A bad *grader response*
    costs a full web search and then reports as a score `0` indistinguishable
    from a refusal. That asymmetry is the useful design lesson for gate
    authors: push as much validation as possible to the config layer, because
    everything the config layer catches is free and everything the judge layer
    catches is expensive and ambiguous.

### Claim 5: Refusal is a documented **expected failure** — a `search-rubric` gate is a conjunction of "does the SUT have web access" and "is the answer right", the vendor grades the first conjunct Fail, and all three documented remedies change the SUT or the assert type rather than the rubric
- **Evidence**: the "Expected Behavior" table, the "Models without web search"
  subsection (including its blockquoted sample SUT response), and the
  "Test always fails with refusal" troubleshooting entry with its
  three-solution list.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `search-rubric` grader correctly flags this as a failure since
  no actual information was provided. This is the expected behavior—the
  assertion is verifying whether your system provides accurate current
  information, not whether it gracefully declines." and "If your SUT
  consistently refuses to answer real-time questions, this is expected
  behavior for models without web access. The `search-rubric` grader is
  correctly identifying that no factual answer was provided."
- **Our assessment**: Buy it hard, and note that this is the **false-red
  counterpart** to a chapter rule the corpus already owns. Ch05's
  `### A gate that cannot fail is not a gate` table (guide/05, :655) is
  entirely *green-while-verifying-nothing*: `threshold: 0` (#1287 Claim 3),
  `weight: 0` (#1287 Claim 4), a score-blind `llm-rubric` (#1305 Claim 10),
  bare `context-faithfulness` / `context-recall` at `threshold: 0`, `guardrails`
  on a response with no normalized signal, and the custom-JS
  `if (!context.trace) return true`. Every one of those is a config property,
  reviewable before the run. This claim is the other failure direction: a
  **red** that is also not evidence about response quality, and it is *not* a
  config property — the rubric can be perfect and the gate still be
  unconditionally red.

  The mechanism is a documented conjunction. The expected-behavior table grades
  "I don't have access to real-time data" as **Fail** / "No actual answer
  provided"; the page's own SUT sample — a `gpt-4o-mini` refusal, "I don't have
  access to real-time stock data. For current prices, please check a financial
  website." — is graded the same way. The grader is therefore checking two
  things at once, and only one of them is the SUT's answer quality. The second
  is the SUT's *tooling*, and the vendor documents the second conjunct as
  expected-to-fail for any model without web access.

  What makes this actionable rather than a vendor caveat: **none of the three
  documented remedies touches the rubric.** The page's solutions are (1) use a
  web-search-capable SUT, (2) accept that models without real-time access cannot
  answer these questions, (3) "Use `llm-rubric` instead if you only need to
  verify the response format." All three change the SUT or swap the assert type.
  So there is no configuration that makes a `search-rubric` gate tolerant of a
  no-web SUT — a permanent red is the documented steady state, and the only way
  to a green is to change what is being tested. Read as gate design, a red
  `search-rubric` on a non-search SUT is measuring infrastructure, and the
  correct operator response is to fix the environment, not to loosen the
  threshold.

  This is also the same axis as open contradiction **#1307** (promptfoo
  missing-trace semantics: built-in `trace-*` asserts *throw* when trace data is
  unavailable, while a custom-JS trace gate `return true`s and goes green). That
  contradiction is about the *green* direction on the same underlying question —
  is a red/green an instrumentation fact or a model fact? — and the built-in
  side of it (#1289 Claim 12: the trace/trajectory family "throw an error when
  traces are unavailable rather than failing") is the true structural analogue of
  this claim, because it is the same fail-loud-on-missing-signal design. Cited
  as same-axis evidence; **not** filed as a new contradiction, and no side is
  picked here.

### Claim 6: The score banding is coarse and bucket-based, while the page's own threshold examples read `threshold` as a percentage of accuracy — a page-internal ambiguity that makes a `search-rubric` threshold a bucket selector rather than a precision dial
- **Evidence**: the "Partial matches and scoring" bullet list, the
  "Threshold Support" section and its commented example, Best Practices item 2,
  and the "Inaccurate results" troubleshooting entry that recommends against
  `1.0`.
- **Confidence**: settled for the vendor's stated numbers and bands; the
  ambiguity between the two readings is *my* reading, and I grade the
  reconciliation as unresolved because the page does not attempt one
- **Quote**: "**0.7-0.9**: Matches most criteria, minor issues" and
  "**0.4-0.6**: Partial match, missing key information" and "**0.0-0.3**:
  Significant errors or refusal to answer" and "Higher thresholds for factual
  accuracy, lower for general correctness" and "Use appropriate thresholds
  (not 1.0) to allow for minor discrepancies"
- **Our assessment**: The vendor publishes four coarse buckets —
  `1.0` / `0.7-0.9` / `0.4-0.6` / `0.0-0.3` — and undefined edges between them.
  So `threshold: 0.7` on a `search-rubric` does not mean "70% of the rubric's
  criteria were satisfied" in any sense the page defines; it means *the judge
  placed this answer in the "matches most criteria" bucket or better*. A
  threshold on this assert is a **bucket selector**, and a team that treats it
  as a precision dial and starts tuning it at 0.72 vs 0.78 is tuning noise.

  That reading is in tension with the page's own use of the number. The
  Threshold Support example is `threshold: 0.9` with the trailing comment
  "Requires 90% accuracy for economic data" (verbatim in Concrete Artifacts) —
  a *fidelity* reading of the same parameter, on the same page, with no
  reconciliation offered. I record this as a page-internal ambiguity and
  **deliberately do not file it as a contradiction** under MINER.md §4a: the
  "90% accuracy" phrasing is a code comment on one example rather than a
  contract definition, so it does not rise to a competing claim, and no existing
  source note asserts either reading. The Assayer should know the ambiguity is
  *recorded*, not resolved.

  The vendor's explicit "not 1.0" advice is more interesting than the
  ambiguity, because it is the vendor conceding that this gate produces false
  reds for reasons that have nothing to do with the SUT. Two documented causes,
  both on the same page: the grader's ground truth is a live web corpus that is
  "occasionally wrong or ambiguous" (the vendor's own limit, already recorded in
  #1305 Claim 12 and not re-extracted here), and — by Claim 3's contract — a
  search call that returns nothing usable scores into the `0.0-0.3` bucket,
  which is the *same* bucket as "Significant errors or refusal to answer". So a
  tolerance band on a `search-rubric` gate is doing double duty: absorbing real
  quality noise *and* judge-side unreliability, and the two are not separable in
  the score. This is the exact mirror of the false-green finding the guide
  already owns (#1305 Claim 10: without a `threshold`, `llm-rubric` passes
  anything the judge does not explicitly flag). One note says "your gate will
  pass things it should not", the other says "your gate will fail things it
  should not", and both are the same parameter.

### Claim 7: The `grading:` block is a second, tool-carrying grader-pinning location that the corpus had zero occurrences of, the page names **no** default judge, and the `search-rubric` ≡ `llm-rubric` equivalence therefore does not hold as a bare-config equivalence
- **Evidence**: the "Grading Providers" section and its five sub-blocks
  (Anthropic, OpenAI, Perplexity, Gemini, xAI), the "Comparing to LLM-Rubric"
  equivalence block, and the "How it works" requirement sentence.
- **Confidence**: settled for the config surface and the absence of a named
  default; the composition argued in the assessment about the shorthand-`config`
  trap is the Miner's inference and is labelled as such
- **Quote**: "The `search-rubric` assertion requires a grading provider with web
  search capabilities" and "The `search-rubric` assertion behaves exactly like
  `llm-rubric`, but automatically uses a provider with web search capabilities:"
- **Our assessment**: Two distinct findings, one about pinning and one about
  the page's own central equivalence claim.

  **The pinning surface is new.** `providerOptions` returns **zero hits**
  across `source-notes/`; this page is the corpus's only source for the
  `grading:` / `providerOptions.config.tools` shape. The tool is not decoration
  — it is the entire capability. Anthropic needs
  `- type: web_search_20250305 / name: web_search / max_uses: 5`, OpenAI needs
  `- type: web_search_preview`, Gemini a bare `- googleSearch: {}`, and xAI
  `- type: web_search` on the Responses API; only Perplexity
  (`provider: perplexity:sonar`) needs no tool block at all because search is
  built in. So for four of five providers, *enabling the capability is
  configuring a nested object*, which puts the assert on a different
  configuration path from every other model-graded assert the corpus holds.

  **Every model ID on this page is an operator-written pin, and the page names
  no default.** The five blocks specify `anthropic:messages:claude-opus-4-6`,
  `openai:responses:gpt-5.1`, `google:gemini-3.1-pro-preview`, and
  `xai:responses:grok-4.3` — these are the *examples of a `grading:` block a
  user writes*, not a documented default. Read that way, #1305 Claim 1 (the
  model-graded judge is unpinned, selected from ambient credentials) applies to
  `search-rubric` unchanged: a bare `- type: search-rubric` gets the built-in
  provider. This note does **not** extend open contradiction #1352 (per-type
  *default* judge: `g-eval` pins `gpt-4.1-2025-04-14` vs the hub's ambient
  selection) — #1352 is about a page's stated *default*, and this page states
  none, which is the same "silent third state" the `pi` note recorded for a
  different reason. It is also worth recording that the drift here is
  *example-level only*: #1471 Claim 5's default roster is `gpt-5` /
  `claude-sonnet-4-5-20250929` / `gemini-2.5-pro`, one generation behind these
  examples, so the docs' **examples** have moved forward while the
  **defaults** stay unpinned and unnamed. That is a documentation-currency fact
  about the corpus's own model IDs, not a contradiction between sources.

  **The equivalence claim does not survive contact with the config rules**
  (this second half is my inference, flagged as such). The page asserts
  `search-rubric` behaves "exactly like `llm-rubric`" with a
  web-search-capable provider — and its own worked equivalence has to write the
  *full* object for the OpenAI side (`provider: openai:responses:gpt-5.1` plus
  a `providerOptions.config.tools` block, per the "Must configure web search
  tool" comment). The family's documented precedence rules are the obstacle:
  #1305 Claim 2 records that an assertion-level *shorthand* provider "quietly
  blocks inheritance of the global provider object's `config`", and #1471
  Claim 10 restates it — the full object must be repeated, "unless you also
  repeat the full object there". The four `config` keys the hub names are
  `apiBaseUrl`, `apiKey`, `temperature`, `showThinking`; `tools` is not among
  them. So a shorthand `provider:` string cannot carry a web-search tool, which
  is presumably why the page's equivalence example spells the object out. I
  have not verified promptfoo's implementation, and promptfoo's own hub
  precedence chain (`--grader` → `defaultTest.options.provider` →
  `assertion.provider`) does not name `grading:` at all — so whether
  `defaultTest.options.provider`'s `config` would carry `tools` down is
  **undocumented on both pages**. Recorded as an open question for the resolver
  and for the guide's pinning rule, not as a vendor claim.

### Claim 8: `search-rubric` fails at three distinct layers that go loud/silent, early/late, and free/expensive in opposite directions — and the loudest is the one nobody sees when a gate goes red
- **Evidence**: the troubleshooting section's "No provider with web search
  capabilities" entry, Claim 4's pre-flight rule, and Claim 3's verdict
  contract. Each of the three failure modes is a distinct documented sentence in
  a different part of the page.
- **Confidence**: settled for the three behaviors individually; the layered
  model is my synthesis and is labelled as such
- **Quote**: "Ensure your grading provider supports web search. Default
  providers without web search configuration will fail."
- **Our assessment**: The page scatters three failure modes across three
  sections and never names them as a set; collected, they are the most useful
  thing on the page for an operator triaging a red gate, because the three
  demand *different* responses and look nothing alike in the report:

  | Layer | Trigger | What you see | Cost to find out |
  |---|---|---|---|
  | Provider selection (claim: this one) | Grading provider has no web-search capability configured | A named error, `"No provider with web search capabilities"` — the page's own troubleshooting heading — before any verdict | Free: config-layer, no tokens, no search fee |
  | Rubric input (Claim 4) | `value:` renders to a number, boolean, array, or object | "rejected before calling the grading provider" | Free: pre-flight, no provider call |
  | Verdict (Claim 3) | Provider error, empty response, or no valid verdict from a working search | **Score `0`** — the same score a refusal or a genuinely wrong answer produces | Full: the search already ran and was billed; #1305 Claim 12's $10–45/1,000 tier applies to a call that produced nothing |

  The operational point is the third row. Both cheap layers fail **loudly, and
  before you spend anything**; the only failure that costs money is the one that
  fails **quietly, in the pass/fail column, with no metadata marker documented on
  this page**. That is the same shape as #1471 Claim 2 ("fails loudly on the
  wrong shapes") and #1483 Claim 2 (malformed responses graded as failures at
  score 0), and it is the direct operational answer to the triage's
  gate-trust question: `search-rubric` is *fail-closed by construction* — it has
  no silent-green path, because the negative form preserves grader failures
  rather than inverting them (Claim 3) and the inversion carries a `[0, 1]`
  clamp (Claim 1) — but it has exactly one silent-**red** path, and it is the
  expensive one.

  The corollary the vendor does not draw: because no metadata marker is
  documented here (Claim 3's assessment), a triage workflow for this assert has
  no in-report way to separate "the SUT was wrong" from "the judge's search
  broke" from "the judge refused to answer". Both Ch05 rules that touch this —
  "a gate that cannot fail is not a gate" and "read the assert's own defaults
  before trusting its verdict" — are about the *green* direction. The symmetric
  rule, which this page supplies the evidence for, is: **a `search-rubric` red
  is a fact about the SUT's web reachability and the judging provider's network,
  not only a fact about the answer.** No existing note states that.

## Concrete Artifacts

Verbatim from the page's `Basic Usage` / `Threshold Support` / `Negation` /
`Grading Providers` sections; YAML indentation reconstructed from the rendered
token markup exactly as it appears on the page.

The page's own equivalence demonstration, and the only place the corpus holds a
side-by-side positive/negated assert for this type:

```yaml
# These are equivalent:
assert:
  # Using llm-rubric with a web-search capable provider
  - type: llm-rubric
    value: 'Contains current stock price for Apple (AAPL) within $5'
    provider: openai:responses:gpt-5.1 # Must configure web search tool

  # Using search-rubric (automatically selects a web-search provider)
  - type: search-rubric
    value: 'Contains current stock price for Apple (AAPL) within $5'
```
*Extracted from: "Comparing to LLM-Rubric". Note the first branch's trailing
comment — the vendor's own acknowledgement that the equivalence requires
explicit tool configuration on the `llm-rubric` side (Claim 7).*

The two provider blocks that carry a nested tool configuration — the corpus's
only `providerOptions` occurrences, and the only model IDs on the page that are
current-generation rather than the `gpt-5` era:

```yaml
grading:
  provider: anthropic:messages:claude-opus-4-6
  providerOptions:
    config:
      tools:
        - type: web_search_20250305
          name: web_search
          max_uses: 5
```
```yaml
grading:
  provider: openai:responses:gpt-5.1
  providerOptions:
    config:
      tools:
        - type: web_search_preview
```
*Extracted from: "1. Anthropic Claude" and "2. OpenAI with Web Search". For
contrast, the two tool-less blocks on the same page are
`grading: provider: perplexity:sonar` (Perplexity, search built in) and:*

```yaml
grading:
  provider: google:gemini-3.1-pro-preview
  providerOptions:
    config:
      tools:
        - googleSearch: {}
```
*— note the different tool *shape*: Gemini takes a mapping with an empty value,
not a typed list entry. The fifth block, xAI, is
`provider: xai:responses:grok-4.3` with `- type: web_search` under
`config.tools`.*

The negated assert, verbatim and complete (the page carries no other
`not-search-rubric` config):

```yaml
assert:
  - type: not-search-rubric
    value: States a stock price that is more than 5% off the current market price
```
*Extracted from: "Negation with `not-search-rubric`".*

The threshold example whose trailing comment is the source of the
bucket-vs-percentage ambiguity in Claim 6:

```yaml
assert:
  - type: search-rubric
    value: 'Contains accurate information about current US inflation rate'
    threshold: 0.9 # Requires 90% accuracy for economic data
```
*Extracted from: "Threshold Support".*

The page's multi-line rubrics, both using a YAML block scalar — the only shape
among the page's own examples that renders to a string while reading as a
structured rubric, and therefore load-bearing evidence for Claim 4's type rule:

```yaml
prompts:
  - "What's the current stock price of {{ticker}}?"

assert:
  - type: search-rubric
    value: |
      Provides accurate stock price for {{ticker}} that:
      1. Is within 2% of current market price
      2. Includes currency (USD)
      3. Mentions if market is open or closed
    threshold: 0.8
```
```yaml
prompts:
  - "What's the weather like in Tokyo?"

assert:
  - type: search-rubric
    value: |
      Describes current Tokyo weather including:
      - Temperature (with units)
      - General conditions (sunny, rainy, etc.)
      - Humidity or precipitation if relevant
```
*Extracted from: "2. Real-time Price Checking" and "3. Weather Information".
Both carry a `{{var}}` inside the block scalar, so the vars-in-rubric
templating documented in #1305 Claim 9 works unchanged here; the page states no
new templating semantics and none is claimed.*

The vendor's expected-behavior table, as a flat transcription (the live page
renders it as a four-column table: SUT Response / Grader Verdict / Reason):

| SUT Response | Grader Verdict | Reason |
|---|---|---|
| "I don't have access to real-time data" | **Fail** | No actual answer provided |
| Stale price from training data | **Fail** | Value differs from current market |
| Correct current price | **Pass** | Matches web search results |
| Partially correct answer | **Partial** | Score reflects completeness |

*Extracted from: "Expected Behavior → What the grader catches". The first row
is Claim 5 in one line: a refusal is a Fail, not a Pass and not a Partial.*

The sample SUT refusal the page quotes, blockquoted in the source:

> "I don't have access to real-time stock data. For current prices, please check
> a financial website."

*Extracted from: "Models without web search", attributed there to
`gpt-4o-mini` "without web search enabled".*

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 4** — the
    inverted-form fail-closed asymmetry. This page is a fourth statement of the
    same property; consistent, and it does **not** resolve the asymmetry, since
    it is again scoped to the inverted form (Claim 2).
  - `docs-promptfoo-g-eval.md` (#1349) **Claim 5** — the identical
    fail-closed sentence on `not-g-eval`, differing only in the closing noun
    phrase (Claim 2).
  - `docs-promptfoo-llm-rubric.md` (#1471) **Claim 7** — the same sentence on
    `not-llm-rubric`, and the note that first asked whether three instances
    license a family law and correctly answered no (Claim 2).
  - `docs-promptfoo-model-graded-closedqa.md` (#1483) **Claim 3** — the
    corpus's only *both-polarities* fail-closed statement, and the
    contrast case for Claim 3: `closedqa` documents a `graderError` metadata
    marker, `search-rubric` documents none.
  - `docs-promptfoo-deterministic-metrics.md` (#1289) **Claim 5** — the
    opposite handling of a numeric `value` on a deterministic assert
    (`value: 0` on `contains` match-anything) versus Claim 4's loud rejection
    of a number as a model-graded rubric.
  - `docs-promptfoo-deterministic-metrics.md` (#1289) **Claim 12** — the trace
    family throws when trace data is unavailable, the structural analogue of
    Claim 5's fail-loud-on-missing-signal, and the built-in side of open
    contradiction #1307.
- **Contradicts**: **none.** No contradiction issue was filed under MINER.md
  §4a, and the three candidates are recorded with the reason each fails the
  bar, because "we found nothing" needs its own evidence here given the dense
  overlap:
  1. *Claim 1 (score inversion) vs. the family's polarity-only negation
     records* (#1305 C4, #1349 C5, #1471 C7, #1483 C1/C3). Those notes do not
     say the score is **not** inverted — they are silent on the score, because
     their pages are silent on it. Silence in a sibling page is not a competing
     claim. §4a's "when not to file" clause applies (one side does not rise to a
     real claim).
  2. *Claim 4 (rubric type rejection) vs. #1305 Claim 9 (objects in
     `{{rubric}}` are JSON-stringified by default).* Different inputs on
     opposite sides of the interpolation boundary — an object written as
     `value:` versus an object arriving through `{{rubric}}`. §4a's conditioning
     clause applies, and both are recorded in the same claim.
  3. *Claim 6's `threshold: 0.9` reading vs. the page's own four-bucket banding.*
     A genuine page-internal ambiguity (recorded in Claim 6's assessment and in
     Extraction Notes below), but a single example's code comment is not a
     contract definition, and no source note in the corpus takes the other
     side. Recorded, not filed.
  Duplicate check run against the nine open `contradiction`-labeled issues
  (#1486, #1462, #1461, #1408, #1352, #1338, #1322, #1307, #1150): only #1352
  (per-type default judge) and #1307 (missing-trace semantics) touch this
  assert family, #1307 is cited above as same-axis evidence, and #1352 is
  explicitly not extended because this page states no default judge.
  `CONTRADICTIONS.md` has no open `C-NNN` entries. No verdict is picked
  anywhere in this note.
- **Extends**:
  - `docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 12** — the hub's
    entire `search-rubric` coverage. This note is the per-type depth Claim 12
    explicitly did not take, and it separates the page into the five surfaces
    Claim 12 collapsed into prose (definition, roster, cost, caching) versus
    the eight it did not carry at all. The cost list and the caching/
    `--no-cache` finding are **deliberately not re-extracted** — they are
    Claim 12's, and the hub's "as of November 2025" qualifier carries forward
    to any reuse.
  - `docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 9** — the
    interpolate-everything / object-stringify default that Claim 4's type check
    is the mirror image of.
  - `docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 10** — the
    score-blind-pass false green. Claim 6 is the false-red half of the same
    `threshold` question.
  - `docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 5** — the
    scratchpad-misparse family; Claim 3's tolerant JSON-in-Markdown parse is
    the mechanism that keeps a reasoning-leaking judge parseable.
  - `docs-promptfoo-model-graded-metrics.md` (#1305) **Claims 1 and 2** — the
    unpinned ambient default and the shorthand-`config` inheritance trap, which
    Claim 7 layers a second, tool-carrying pinning location on top of.
  - `docs-promptfoo-max-score.md` (#1472) **Claims 3, 4, and 9** — the
    aggregation machinery (`method: average` / `sum`, type-keyed `weights`) that
    Claim 1's `1 - score` inversion exists to feed correctly, and Claim 9's
    documented absence of a `not-` form on `max-score` itself (so this page's
    aggregation claim is about per-assert and test-case `threshold`, and about
    the weights map only for whichever type key the negated assert lands under
    — which the page does not say).
  - `docs-promptfoo-configuration-caching.md` (#1275) **Claims 4 and 9** — the
    default-on cache, the 14-day TTL, and `--no-cache`. The freshness half of a
    live-search gate: a cached verdict is up to two weeks old, and a
    "current information" assert replaying a two-week-old search result is
    failing at the gate's stated purpose. **Not re-extracted here** — Claim 12
    already carries the caching line — but the interaction is the reason the
    vendor's cost advice ("Caching is enabled by default to reduce API calls",
    this page's "High costs" entry) and the guide's freshness advice point in
    opposite directions on the same assert.
  - `docs-promptfoo-assertions-metrics.md` (#1287) **Claims 1, 3, and 4** —
    the test-case weighted average that per-assert scores feed, and the two
    silent-green configs (`threshold: 0`, `weight: 0`) that Claim 5 is the
    exact directional mirror of.
  - `docs-promptfoo-pi-scorer.md` (#1484) **Claim 6** — the sibling that
    established "no `not-` negation section" as a *recorded absence* worth a
    note. `search-rubric` is the counterpart case: it has a negation section,
    and it is the only one in the corpus that documents a **score** transform
    there.
  - `docs-litellm-messages-to-responses-mapping.md` — cited by section rather
    than claim number for the cross-vendor half of the tool story: the one other
    corpus page naming `web_search_preview` is LiteLLM's `/v1/messages` →
    Responses mapping, whose web-search handling is a *type remap* at the
    gateway. Together the two pages bracket the operational risk: the tool
    name is not a stable identifier across the two shapes of the same
    capability, so a gateway in the path can rewrite the very block that
    enables the gate's search.
- **Novel**:
  - `not-search-rubric` itself — **zero hits** across all notes in
    `source-notes/` before this one.
  - **Score-inverting negation** with a `[0, 1]` clamp and an
    explicitly aggregation-motivated rationale (Claim 1) — no corpus note
    records that any model-graded `not-` form transforms the score.
  - The **`not-`-preserves-grader-failures** clause stated in the verdict
    contract rather than in the negation section (Claim 3) — the corpus's only
    occurrence of a per-type page keeping both halves in one sentence.
  - **Rubric type validation before the provider call** (Claim 4) — no corpus
    note records a `value:` type rule for any assert type.
  - The **`grading:` block and `providerOptions.config.tools`** (Claim 7) —
    zero corpus occurrences of `providerOptions`; this is the only source for
    how a model-graded assert's provider-level tool capability is configured.
  - **Refusal as a documented expected failure** (Claim 5) — the corpus's
    first documented *systematic false red* in the model-graded tier, and its
    first documented case of an assert whose remedies all change the SUT rather
    than the config.
  - The **three-layer failure model** with opposite loudness and cost
    (Claim 8) — no corpus note organises a single assert's failure modes this
    way.
  - The **absence of any documented `metadata` or grader-error marker** for
    this assert type (Claim 3's assessment) — a documented silence, recorded
    as such and not generalized.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — `### A gate that cannot fail is not a
  gate` (guide/05-llm-ops-reliability.md:655)**: this section's six-row table
  is a catalogue of ways a gate goes **green while verifying nothing**, and its
  closing rule is "Every score-producing assertion carries an explicit non-zero
  `threshold` … and every suite carries a negative control". Claim 5 supplies
  the missing symmetric row and it is not a config property: a bare
  `- type: search-rubric` against a SUT without web access is
  **unconditionally red by the vendor's own documented expectation**, and
  nothing in the rubric, the threshold, or the `threshold: 0` family changes
  that. Recommend adding a short companion subsection — "a gate that can only
  fail is not a gate either" — carrying: (a) the fail-closed-by-construction
  finding (Claims 1, 3, 8: no silent-green path on this assert, one
  silent-red path), (b) the fact that the documented remedies all change the SUT
  or swap the assert type, so a permanent red here is an environment defect
  wearing a quality metric, and (c) the triage table from Claim 8, which tells
  an operator that a red is *not* a grader error by inspection — it is only
  distinguishable by cost, because the two cheap failure layers never reach the
  report.
- **Chapter 05 — `### Read the assert's own defaults before trusting its
  verdict` (guide/05-llm-ops-reliability.md:443)**: this section's argument is
  that per-type defaults fail open in directions the assert name does not
  advertise (it uses `factuality`'s permissive A/B/C/E pass-set as its worked
  example). Add the type-check row: on `search-rubric` the rubric `value` must
  render to a string, and numbers, booleans, arrays, and objects are rejected
  *before* the provider is called (Claim 4) — which makes a multi-criteria
  rubric a mandatory YAML block scalar, and which is the deliberate inverse of
  the family default that stringifies objects arriving through `{{rubric}}`
  (#1305 Claim 9). Also add that this assert's threshold is a **four-bucket
  selector**, not a precision dial (Claim 6): tuning `search-rubric` thresholds
  at the second decimal place tunes judge noise, and the vendor's own advice is
  "not 1.0" — a tolerance band that also absorbs judge-side search unreliability
  (Claim 3), not only answer-quality noise.
- **Chapter 05 — `### The judge behind a model-graded assertion is unpinned by
  default` (guide/05-llm-ops-reliability.md:699)**: the section's rule is
  "Pin *every* model artifact behind a verdict, not just the text judge".
  Claim 7 adds that for `search-rubric` the *capability* is a pinned artifact
  too: the web-search tool lives in `providerOptions.config.tools` under a
  `grading:` block that the guide's documented precedence chain
  (`--grader` → `defaultTest.options.provider` → `assertion.provider`) does not
  mention, `tools` is not among the four `config` keys the hub names as
  inheritable, and the page's own equivalence example has to write the full
  object to carry a tool. Two of five providers need no tool block at all
  (Perplexity, and Gemini's mapping-shaped `- googleSearch: {}`). The pinning
  rule should therefore add: *on a web-search assert, the tool block is part of
  the pin, and "the provider looks right" is not evidence the tool is
  configured.*
- **Chapter 05 — `### Judge calibration before judge trust`
  (guide/05-llm-ops-reliability.md:410)**: calibration is usually framed as
  making the judge agree with a human. This page adds that on a live-search
  assert the judge's evidence is a **third-party corpus with no version to pin**
  and a documented history of being "occasionally wrong or ambiguous" — so
  part of the observed disagreement rate is not judge miscalibration and cannot
  be calibrated away. It must be excluded before the human-agreement number is
  read, or teams will chase a calibration problem that lives upstream of the
  judge.
- **Chapter 05 (new, narrow) — negated-assert threshold derivation**: Claim 1's
  open question deserves a rule once the vendor or an installed CLI settles it:
  the score inverts under `not-`, so a calibrated positive-form `threshold` does
  not carry over unchanged, and the page does not say what promptfoo does about
  it. Until answered, the guide should say: re-derive the threshold for a
  negated assert, and do not copy a calibrated number across the `not-` prefix.
- **Chapter 06 (Security and Trust) — `### A classifier gate's detector is a
  dependency with a lifecycle` (guide/06:423)**: that section's lesson is that
  the thing behind a security gate has supply-chain properties (an archived
  `protectai` detector, thresholds that do not survive a detector swap). Claim 7
  is the same shape with a worse ending: a `search-rubric` gate's ground truth
  is the judging provider's live web index — a dependency that cannot be pinned,
  diffed, or reproduced, whose contents change between two runs of the same
  suite. For a Ch06 "must not" gate built as `not-search-rubric` (the page's
  own suggested use: "useful for 'must not' criteria"), the vendor's fail-closed
  guarantee is genuinely reassuring — a broken judge cannot wave a must-not
  through — and the residual risk is the mirror: the *positive* evidence the
  judge cites is unreproducible, so a green cannot be re-derived later in an
  incident. The chapter's "shadow → suggest → act" and auditability sections
  both assume a verdict can be re-checked; this assert cannot be.
- **Chapter 02 (Observability) — `### One trace per request` (guide/02:9)**:
  the trace/telemetry chapter reasons about what a request record does and does
  not preserve. This page is a compact worked counterexample: a `search-rubric`
  verdict's inputs include a live third-party search result that the trace does
  not capture, and the eval cache can replay that verdict for up to 14 days
  (#1275 Claim 4) without re-running the search. A trace can show that a
  `search-rubric` assert ran and passed; it cannot show what the world said when
  it did. Ch02's trace-contents table should say so explicitly, because
  "replay the trace to explain the grade" is the reflex an on-call engineer will
  try first, and it will produce a confident, unfalsifiable answer.
- **Chapter 05 — triage vocabulary, minor**: Claim 8's three-layer table is
  worth carrying as a small block wherever the guide tells readers how to
  investigate a red eval, because the shape generalizes past this assert: config
  layers fail loud and free, the judge layer fails quiet and expensive, and no
  note in the corpus currently separates the two for a reader.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/search-rubric),
  then re-fetched as raw HTML to verify quotes and reconstruct all 14 code
  blocks from the page's Prism `token-line` markup (the plain-text fetch
  collapses YAML indentation; token content is unchanged, and the reconstructed
  blocks are what appear in Concrete Artifacts). Every quote above was checked
  character-for-character against the fetched rendered content, including the
  em-dash constructions (which use no surrounding spaces: "expected
  behavior—the", "scored `1 - score`, clamped to `[0, 1]` — so negated") and the
  `not-` bolding inside "passes when the rubric criterion does **not** match".
  Code-block attributions name the section each block appears in.
- **Page currency**: the footer reads "Last updated on **Sep 28, 2026** by
  **mldangelo-oai**" on today's fetch (2026-09-28). Both triage comments on the
  issue recorded "Sep 27, 2026"; that is a one-day difference between two reads
  of the same page, and I can distinguish neither an intra-day page edit from a
  cached render in one of the two fetches, so I record the two reads rather
  than asserting an edit. The content I quote was verified against today's
  render. The page is undated (no publish date), so `date_published` carries the
  last-updated date, matching the sibling notes (#1287/#1289/#1305/#1349/#1471/
  #1483/#1484). Note the authoring account differs from the model-graded hub's
  ("renovate[bot]", Sep 14, 2026) — this is a human-maintained per-type page.
- **Triage key-question resolutions** (all three Prospector comments read as
  UNTRUSTED input; every item re-verified against the page, and no comment's
  wording was carried into a quote):
  1. *"Extract the delta, not the page."* — Done, and the boundary was
     enforced. **Not re-extracted**, because #1305 Claim 12 already holds it:
     the `search-rubric` definition, the "behaves exactly like `llm-rubric`"
     equivalence, the five-grader roster, the "as of November 2025" cost list,
     the default-on caching / `--no-cache` best-practice line, and the
     "web search results … wrong or ambiguous" caveat. I restate the caveat's
     *role* inside Claim 6's assessment (as the reason a tolerance band is
     needed) with a pointer back to Claim 12, and I do **not** make it a claim
     of this note's own. Everything else on the page is extracted at claim
     depth: score inversion (C1), fail-closed inversion (C2), the verdict
     contract (C3), rubric type validation (C4), refusal-as-expected-failure
     (C5), banding and thresholds (C6), the `grading:` config (C7), and the
     layered failure model (C8).
  2. *"This is the third per-assert instance of the `not-` fail-closed
     property."* — **Refined, not accepted as stated.** I count **four** pages
     stating the property (#1305 `not-trajectory:goal-success`, #1349
     `not-g-eval`, #1471 `not-llm-rubric`, this page) and **three** carrying the
     character-identical long sentence (the g-eval and llm-rubric pages differ
     from this one only in "a failed grader call" → "a failed search call").
     The count matters because the triage also said "do not generalize beyond
     what the vendor states", and with four inverted-form instances and still
     exactly one both-polarities instance (#1483 Claim 3), the generalization
     still does not follow. Recorded as such in Claim 2; I did not overwrite or
     resolve #1305 Claim 4.
  3. *"Mine it as a tension/extension of #1305 Claim 4, not as a new standalone
     law."* — Followed. #1305 Claim 4's asymmetry finding is cited as
     corroborating, not overturned, and Claim 2 states explicitly what this page
     does not settle.
  4. *"Pair the grader-failure scoring with #1305 Claim 10's score-blind-pass
     footgun."* — Done, in Claim 6: Claim 10 is the false-green half of the
     `threshold` question and this page is the false-red half, and the vendor's
     own "not 1.0" advice is the concession that ties them.
  5. *"The two rules sit on opposite sides of the same boundary — stringify the
     interpolated object, reject a non-string rubric."* — Confirmed and
     extended with a consequence the triage did not name: the page's own
     multi-criteria rubrics are YAML block scalars (`value: |`), which is what
     makes Claim 4's type rule load-bearing rather than theoretical (Concrete
     Artifacts).
  6. *"Capture the model IDs and any drift against the hub note's `gpt-5`-era
     examples."* — Done in Claim 7, with the distinction the triage did not make
     explicit: these IDs are **operator-written example pins, not documented
     defaults**, so the drift is in the docs' *examples* while the *default*
     stays ambient and unnamed. That is why I did not extend #1352.
- **Amendment-vs-standalone-note decision**: the triage offered an amendment to
  #1305 as the fallback if the delta proved thinner than its items 1, 3, 4 and
  5. **Not** taken. All four of those items are substantive and materially
  larger than the "amendment" scale — a score-inverting negation that is the
  corpus's only instance of the mechanism, a pre-flight validation rule with zero
  corpus precedent, a verdict contract that resolves an internal consistency
  question, and a documented systematic false red. A fifth (the `grading:`
  pinning surface, `providerOptions` → zero hits) is new. The sibling convention
  (#1471, #1472, #1483, #1484) is a standalone per-type note at claim depth, and
  that is what this is.
- **Sub-pages NOT followed, and why**: this page has no outbound sub-page links
  — its only hyperlinks are the sidebar's sibling per-type pages (all already
  mined at claim depth or rejected: `g-eval` #1349, `pi` #1484,
  `conversation-relevance`, `context-faithfulness` / `-recall` / `-relevance`,
  `agent-rubric` (folded into #1305 Claim 11), `answer-relevance` #1319,
  `factuality`, `llm-rubric` #1471, `max-score` #1472, `model-graded-closedqa`
  #1483, `select-best`, and the three deterministic/classification parents) plus
  one in-page anchor (`#grading-providers`, self-referential) and one outbound
  vendor link inside the cost list ("see Perplexity or your proxy's pricing
  page"), which is a pricing pointer carrying no assert semantics. So the
  "follow up to 5 linked pages" budget found nothing substantive to follow here;
  the sibling notes were cross-referenced from their existing notes rather than
  re-read.
- **Open questions recorded, not guessed** (three, all flagged in the claim
  assessments): (a) whether promptfoo re-derives a per-assert `threshold` for
  the `not-` form or leaves the operator's number untouched (Claim 1) —
  undocumented on this page and, per the corpus, not recorded in any note;
  (b) whether `defaultTest.options.provider`'s `config` would carry
  `providerOptions.config.tools` down to a `search-rubric` assert, given that
  the hub's documented precedence chain never mentions `grading:` and the
  shorthand-`config` trap (#1305 Claim 2, #1471 Claim 10) does name the
  mechanism (Claim 7) — this composition is **my inference from two sources,
  not a vendor statement**; (c) whether a negated assert's type key lands as
  `not-search-rubric` or `search-rubric` in a `max-score` `weights` map
  (#1472 Claim 4 keys weights by assertion type) — undocumented here, and I
  did not guess. All three are consequences of MINER.md §1's "read deeply" over
  §2a's ban on fabricating detail, and none is asserted as product behavior.
- **Contradiction check outcome**: no contradiction issue filed, with the three
  candidates and the failing reason for each recorded under **Contradicts**
  above, and the duplicate check run against all nine open
  `contradiction`-labeled issues. This page is *rich* rather than internally
  inconsistent — the one page-internal ambiguity found (the `threshold: 0.9`
  "Requires 90% accuracy" comment versus the four-bucket banding) is recorded in
  Claim 6's assessment as an ambiguity and explicitly not filed, because a code
  comment on one example is not a competing claim and MINER.md §4a's
  "when not to file" clause covers it. I also checked the page against itself
  for the interaction between the `1 - score` inversion (Claim 1) and the
  preserve-don't-invert rule (Claim 3), which is the most likely
  self-contradiction on a page with a negation section: the two are
  **consistent**, because the `[0, 1]` clamp leaves a failed grader at `0` in
  range to be preserved rather than flipped to `1`, and the "How it works"
  sentence says so explicitly. That consistency is the substance of Claim 3.
  No `C-NNN` entry was added to `CONTRADICTIONS.md` and no verdict is picked in
  this note.
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; all 10 candidates cited or dismissed by name — candidates
  are suggestions only, and no corroboration was invented to use one):
  - `docs-promptfoo-pi-scorer.md` — **cited** (Extends Claim 6 of that note: the
    negation-section inventory gains a counterpart case with a score transform).
  - `docs-promptfoo-classifier-grading.md` — detector-scorer thresholds and the
    archived-detector recalibration hazard. Structurally the nearest analogue to
    this page's "the judge behind the gate is a dependency", and the reason the
    Ch06 Guide Impact cites `docs-promptfoo-classifier-grading.md`'s
    detector-lifecycle argument by name — but the candidate list surfaced it for
    **claim-level** corroboration and there is none: that note's thresholds
    (0.5 / 0.75 / 0.9) are HuggingFace classifier score cut-points, not rubric
    score bands, and the two are different scales. Deliberately **not** listed
    under Corroborates, to avoid implying a corroboration that does not exist;
    cited by name in the Guide Impact prose only.
  - `docs-promptfoo-llm-rubric.md` — **cited heavily** (Corroborates Claims 2
    and 7; Extends Claims 2, 7, and 10).
  - `docs-promptfoo-model-graded-closedqa.md` — **cited** (Corroborates Claims 2
    and 3).
  - `docs-promptfoo-factuality.md` — per-category pass-set semantics and a
    scorer-bound threshold; the lexical overlap is "threshold" and the shared
    Chapter 05 section (`Read the assert's own defaults`), but this page states
    no per-category override and no factuality cross-reference; **dismissed** as
    a claim-level cross-ref.
  - `docs-promptfoo-model-graded-metrics.md` — **cited heavily** (Corroborates
    Claims 2 and 5; Extends Claims 1, 2, 5, 9, 10, and 12). This is the note
    whose Source Context says `search-rubric` "was followed for their config
    semantics"; this note is the depth that summary did not take, and Claim 12's
    scope is the boundary I extracted against.
  - `blog-promptfoo-owasp-red-teaming.md` — OWASP red-team methodology, SDLC
    phases, and the step-zero objectives principle. Shares the word "gate" with
    my Chapter 06 impact but carries no eval-grader, verdict-contract, or
    threshold-provenance semantics; **dismissed**.
  - `blog-promptfoo-red-team-gemini.md` — per-model red-team plugin strategy
    (including its own reasoning-DoS latency assert). Uses rubric asserts as
    tools but supplies nothing about judge verdicts, negation, or search
    graders; **dismissed**.
  - `docs-litellm-batches-api.md` — LiteLLM batch rate-limit accounting; the
    lexical overlap is cost/limits against this page's cost list, and the note
    supplies no per-call web-search figure; **dismissed**.
  - `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge *alerting* for incident
    triage; no eval-assert config surface, no verdict contract, no negation
    semantics; **dismissed**.
  - Additionally found by searching `source-notes/` per MINER.md §4 (not in the
    candidate list as written) and all **cited**:
    `docs-promptfoo-model-graded-metrics.md`, `docs-promptfoo-max-score.md`,
    `docs-promptfoo-configuration-caching.md`,
    `docs-promptfoo-assertions-metrics.md`, and
    `docs-litellm-messages-to-responses-mapping.md` (cited by section/claim for
    the cross-vendor `web_search_preview` remap, per the guidance that
    non-claim material is cited by name rather than a fictional claim number).
- **Cross-ref verification (§4b)**: every cited claim number was located and
  read in the cited note before it was written, and its content checked against
  what it is cited for — #1305 Claims 1/2/4/5/9/10/12, #1349 Claim 5, #1471
  Claims 2/7/10, #1483 Claims 2/3, #1472 Claims 3/4/9, #1275 Claims 4/9, #1287
  Claims 1/3/4, #1289 Claims 5/12, #1484 Claim 6, and
  `docs-litellm-messages-to-responses-mapping.md` Claim 7. No claim numbers were
  invented and no quotes are attributed to any other note. Source-note issue
  numbers were read from each cited note's frontmatter `issue:` field, not
  inferred: #1287, #1289, #1305, #1349, #1471, #1472, #1275, #1483, #1484. The
  guide section line numbers cited in Guide Impact (Ch05 :410/:443/:655/:699,
  Ch06 :423, Ch02 :9) were read from the current `guide/` working tree. One
  explicit limit: `docs-promptfoo-classifier-grading.md` and
  `docs-promptfoo-factuality.md` were read **only** far enough to confirm the
  absence of claim-level overlap recorded above; neither is cited by claim
  number, so no unverified claim reference is carried from them.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1288, #1289, #1305, #1320, #1332, #1334, #1349, #1471, #1472,
  #1483, #1484): every mechanism, default, config-shape, and failure-direction
  claim is settled for *product behavior* and directly checkable against an
  installed CLI, but this is single-vendor reference documentation with no
  measured gate-failure rate, no judge-agreement figure, no flake measurement,
  no latency data, and no independent practitioner validation. Two of the eight
  claims (1 and 7) rest partly on *absence* — of a documented default judge and
  of a documented threshold re-derivation for the negated form — and one (6)
  records an unresolved page-internal ambiguity. Marked `emerging` on the
  strength of the body of evidence, not on the strength of the page's
  confidence in itself.
- `registry/sources.json` and `registry/claims-index.json` were **not** edited —
  they are derived indexes rebuilt by `scripts/build_registry.py` and
  `scripts/build_claims_index.py` after merge. `miner-related-notes.md` was
  read as required and is **not** committed.
