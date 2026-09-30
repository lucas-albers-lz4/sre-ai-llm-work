---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/similar
source_type: docs
title: "Promptfoo Configuration: Similarity (embeddings) — the `similar` / `not-similar` assertion"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-30
date_extracted: 2026-09-30
last_checked: 2026-09-30
status: current
confidence_overall: emerging
issue: "#1512"
---

# Promptfoo Configuration: Similarity (embeddings) — the `similar` / `not-similar` assertion

> The primary source behind the corpus's one-line treatment of `similar` as "a
> gate that needs an embedding model": it names the default embedding provider
> and model, documents three metric variants whose threshold *directions* are
> not the same (euclidean is a maximum distance, not a minimum similarity),
> shows the two provider-override surfaces, and defines `not-similar`-over-an-
> array as the forbidden/canned-answer-list gate.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo reference page for
  the `similar` assertion under `/docs/configuration/expected-outputs/`, the
  sibling of the deterministic catalog (#1289) and of the model-graded
  `answer-relevance` page (#1319))
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own assertion behavior — authoritative for
  what each config value does, vendor-positioned on every evaluative claim
  ("This is the industry standard for embeddings"). The page reports no measured
  gate-failure rate, no score distribution, no drift data, and no independent
  practitioner validation. Every mechanism claim below is directly checkable
  against an installed CLI.
- **Scope**: A single assertion type's reference page: what `similar` computes,
  the three selectable metrics and their numeric ranges, the array and negation
  semantics of the expected value, and the two documented provider-override
  surfaces. It does NOT cover: a default threshold (the page documents none),
  whether the embedding call participates in promptfoo's response cache,
  how scores are reported in the Eval UI, calibration procedure, or any
  operational incident data.
- **Last updated**: Sep 30, 2026 by mldangelo-oai (page footer). Vendor docs
  are a moving target; re-check before citing the default model name.

## Extracted Claims

### Claim 1: The `similar` assertion is a model-assisted gate whose default embedding provider is OpenAI's `text-embedding-3-large` — an unpinned, remotely-hosted dependency in a suite that otherwise looks like string matching
- **Evidence**: The page's second paragraph, immediately after the definition,
  plus the "Overriding the provider" section's restatement ("By default
  `similar` will use OpenAI").
- **Confidence**: settled (documented product behavior)
- **Quote**: "By default, embeddings are computed via OpenAI's `text-embedding-3-large` model."
- **Our assessment**: This is the concrete instance behind
  `docs-promptfoo-deterministic-metrics.md` **Claim 1**'s requirement-column
  entry "An embedding model" for `similar`. Read as a CI-gate property it is
  the sharpest case in the family: an operator scanning a config sees
  `type: similar` / `threshold: 0.8` and reasonably files it under
  string-matching gates, but every run makes a network call whose result
  depends on a model the config never names. Nothing on the page states that
  the default is version-pinned, and the model name carries no version
  qualifier — so the gate's score distribution can rebase under an unchanged
  config for the same reason a generated dataset does
  (`docs-promptfoo-dataset-generation.md` **Claim 5**). Note the page is
  *silent* on whether the embedding call is subject to promptfoo's response
  cache; the corpus's caching note (#1275) documents that provider API results
  are cached by default, but neither page connects the two, so treat
  "is a `similar` gate subject to the 14-day eval cache?" as an open question
  rather than a documented property.

### Claim 2: One assertion name, three metrics — `similar`/`similar:cosine` (default), `similar:dot`, and `similar:euclidean` are selected by suffix in the type string, so the metric is invisible in a compact `similar(0.8):value` form
- **Evidence**: The "Similarity Metrics" section's opening sentence, plus the
  three per-metric subsections with their type suffixes in the examples.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can specify which metric to use by including it in the assertion type. The default is `similar` (cosine similarity)."
- **Our assessment**: The type string is the only place the metric is
  recorded. `docs-promptfoo-assertions-metrics.md` **Claim 12** documents the
  compact assertion form `similar(0.8):Hello world`, in which the metric is
  *not* expressible — a compact `similar(0.8):…` is always cosine, silently.
  Combined with Claim 3 below, "the same assertion type with a different
  suffix" is the config-portability hazard the triage flagged: a threshold that
  was calibrated for one suffix is meaningless under another, and the compact
  form gives a reader no way to see which metric they are looking at.

### Claim 3: The euclidean threshold is a **maximum distance**, not a minimum similarity — the docs state the inversion twice and in an "Important" callout, so the same threshold literal reads in the opposite direction under `similar:euclidean` than under cosine
- **Evidence**: The Euclidean Distance section's "When to use" sentence, the
  separate bolded "Important" callout immediately after it, and the inline
  comment in the section's own YAML example (`threshold: 0.5 # Maximum distance
  threshold`).
- **Confidence**: settled (documented product behavior; the vendor states the
  inversion twice, in prose and in a config comment)
- **Quote**: "Note that the threshold represents the *maximum* distance (not minimum similarity), so lower values are stricter." and "**Important:** For euclidean distance, the threshold semantics are inverted - it represents the *maximum* acceptable distance rather than minimum similarity."
- **Our assessment**: The rule is stated twice on the page, once in prose and
  once in an "Important" callout, which makes the threshold literal
  non-portable across metrics: the same number reads in *opposite* directions
  depending on the suffix. Under cosine, `threshold: 0.8` is a minimum
  similarity, so raising the number tightens the gate; under
  `similar:euclidean`, `threshold: 0.8` is a maximum distance, so raising the
  number *loosens* the gate and lowering it tightens the gate. A threshold
  calibrated under one suffix therefore carries no meaning under the other,
  and nothing in the config marks which direction is in force (the metric
  lives only in the type suffix — Claim 2). The vendor's own examples are the
  tell: the euclidean block uses `0.5` where every other example uses `0.8`
  (Claim 9), i.e. the authors re-chose the number when they changed the
  metric rather than carrying it over. What we are *not* claiming is a
  specific downstream verdict for a mis-set threshold: the page publishes no
  euclidean distance distribution for the default embedding model, so whether
  a given literal turns a real gate red or green depends on where that
  model's distances actually fall and cannot be read off the docs. The
  source-supported statement is the weaker one — the threshold's *direction*
  is part of the assertion's contract and differs by metric — and the
  score-distribution consequence is `emerging` at most.

### Claim 4: The inversion compounds under negation in a way the page never states — `not-similar` with an euclidean threshold passes when the distance is *above* the threshold, so a threshold tuned to catch a near-miss silently becomes a floor rather than a ceiling
- **Evidence**: The page's own two rules read together — the euclidean
  inversion (Claim 3) and the `not-similar` array semantics ("passes only when
  the output is dissimilar to **every** value"). The page documents no
  `not-similar` example at all, in any metric.
- **Confidence**: emerging (Miner synthesis from two documented rules; the page
  does not state the interaction, and no worked example exists to confirm it)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Under cosine, `not-similar` passes when similarity is
  *below* the threshold — a forbidden-answer gate with the threshold as a
  ceiling on similarity. Under `similar:euclidean` the same assertion passes
  when distance is *above* the threshold, so the same number becomes a floor
  on distance: the operator who writes `similar:euclidean` + `not-similar`
  + `threshold: 0.5` believing they have tightened a forbidden-list gate has
  in fact inverted it, and the direction of failure depends entirely on the
  embedding model's distance distribution. Because the page ships zero
  `not-similar` examples and never pairs negation with a metric suffix, this
  is the configuration surface most likely to be authored by analogy from a
  cosine example and least likely to be reviewed. Corpus precedent for taking
  negation semantics seriously rather than assuming they compose:
  `docs-promptfoo-javascript-assertions.md` **Claim 3** (score compared against
  `threshold` *before* inversion) and **Claim 2** (a throw is a hard fail).

### Claim 5: The three metrics do not share a numeric range — cosine is −1..1, dot product is unbounded, euclidean is 0..∞ — so a single threshold literal cannot be carried across metrics even in the "higher is stricter" cases
- **Evidence**: The one-line range characterization at the head of each of the
  three metric subsections.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Measures the cosine of the angle between two vectors. Range: -1 to 1 (higher is more similar), though text embeddings typically produce values between 0 and 1." and "Computes the dot product of two vectors. Range: unbounded, but typically 0 to 1 for normalized embeddings (higher is more similar)." and "Computes the straight-line distance between two vectors. Range: 0 to ∞ (lower is more similar)."
- **Our assessment**: The vendor's own hedges are the operational content:
  cosine is documented as −1..1 but "typically" 0..1, and dot as unbounded but
  "typically 0 to 1 **for normalized embeddings**". Both "typically"
  qualifications are unstated preconditions — a `similar:dot` gate over
  un-normalized embeddings can produce dot products well above 1, so a
  threshold written against the "typically 0 to 1" reading is not calibrated.
  The page never says whether promptfoo normalizes before computing, and never
  documents the observed score distribution for the default model. For a gate,
  the honest statement is: this threshold is model- and metric-specific and
  the docs supply no calibration reference point. This is the same
  score-rebasing hazard `docs-promptfoo-answer-relevance.md` **Claim 3**
  documents for a different assertion, and it composes with this page's
  unpinned default (Claim 1) rather than duplicating it.

### Claim 6: An array `value` makes `similar` an OR over acceptable answers, and `not-similar` over an array a NOR — the documented primitive for asserting an output does not resemble *any* item in a forbidden or canned-answer list
- **Evidence**: The array example immediately after the single-value example
  (with the "at least one" pass rule), and the following paragraph defining
  `not-similar`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "If you provide an array of values, the test will pass if it is similar to at least one of them:" and "The negated `not-similar` assertion is the logical inverse: with an array of values it passes only when the output is dissimilar to **every** value (and fails as soon as it is too similar to any one of them). This is the natural way to assert that an output does not resemble any item in a list of forbidden or canned answers."
- **Our assessment**: The vendor names the use case, and it is the most
  useful thing on the page: a "did the model parrot one of our three canned
  answers / refuse-and-echo-the-prompt" gate. Two operational properties worth
  carrying. First, the negation is a *universal* quantifier, so the failure
  mode of a `not-similar` array is driven by the single nearest forbidden
  answer — adding a long forbidden list monotonically loosens the gate, which
  is the opposite of the intuition that a longer blocklist is a stricter one.
  That is a gate whose strictness moves when someone appends to a fixture, and
  no config error occurs. Second, the page's own array example includes
  `- file://my_expected_output.txt` as one of the list entries, so the
  expected values can be loaded from files at eval time — a second mutable
  external input to the gate, in the same list as the embedding model.

### Claim 7: Two documented override surfaces, neither required, and both in the YAML-object form — suite-wide `test.options`/`defaultTest.options` → `provider.embedding.{id,config}` and per-assertion `assertion.provider` as a bare shorthand string
- **Evidence**: The "Overriding the provider" section's numbered list (1 =
  suite-wide, 2 = per-assertion) with its two YAML examples, and the section's
  opening sentence.
- **Confidence**: settled (documented product behavior)
- **Quote**: "By default `similar` will use OpenAI. To specify the model that creates the embeddings, do one of the following:" and "1. Use `test.options` or `defaultTest.options` to override the provider across the entire test suite. For example:" and "2. Set `assertion.provider` on a per-assertion basis. For example:"
- **Our assessment**: The suite-wide shape reuses the same `embedding` slot key
  that `docs-promptfoo-answer-relevance.md` **Claim 2** documents as part of
  that assertion's two-slot `provider: { text, embedding }` object — here it
  is the *only* slot, because `similar` has no text provider. That is
  convenient for a team that already sets `defaultTest.options.provider.embedding`
  for `answer-relevance`: the same override would silently also rebase every
  `similar` gate in the suite, including thresholds calibrated under a
  different model. The per-assertion form is a bare shorthand string, which is
  the inheritance hazard `docs-promptfoo-model-graded-metrics.md` documents for
  the judge family (a shorthand `provider:` does not split into slots or inherit
  the parent's `config`); the `similar` page gives no guidance on the
  interaction, and the corpus already has an open contradiction on a different
  promptfoo override interaction (#1486) showing this family of question is
  live. Flagging as an open surface, not a documented behavior.

### Claim 8: Both documented override examples pin a *named model version*, while the default is named without one — so the page's own "how to pin" path moves the gate onto an older, vendor-pinned model (`text-embedding-ada-002`, `sentence-transformers/all-MiniLM-L6-v2`) hosted somewhere else, and neither destination is local
- **Evidence**: The two YAML examples in the "Overriding the provider" section,
  each naming a specific model id and (in the Azure case) a `config.apiHost`
  the operator must supply.
- **Confidence**: settled (documented config values); the pinning comparison is
  Miner synthesis over those values
- **Quote**: "2. Set `assertion.provider` on a per-assertion basis. For example:" (followed by the example block below, `provider: huggingface:sentence-similarity:sentence-transformers/all-MiniLM-L6-v2`)
- **Our assessment**: Read the two examples against the default: the default
  is `text-embedding-3-large` (no version qualifier in the string); the
  documented overrides are `azureopenai:embedding:text-embedding-ada-002`
  (older OpenAI model, but on the operator's own Azure resource, with
  `apiHost` as a required config key) and
  `huggingface:sentence-similarity:sentence-transformers/all-MiniLM-L6-v2` (a
  hosted HuggingFace inference endpoint for a small sentence-transformer).
  So "pin the embedding model" is not a move toward hermeticity — every
  documented destination is still a remote inference call, and the two pinned
  options are an *older, weaker* model on infrastructure the team must also
  operate. The honest framing for the guide: the pinning lever exists, it is
  worth using for reproducibility, and none of its three documented settings
  makes the gate hermetic. The threshold must be re-calibrated at each move,
  because the score distributions of a 3-large embedding and a MiniLM sentence
  embedding are not on a common scale (Claim 5).

### Claim 9: The page documents no default `threshold` for `similar` in any metric — every example supplies one explicitly, and the euclidean example deliberately uses a different literal from the other four
- **Evidence**: All five YAML examples on the page carry an explicit
  `threshold` (0.8 in the single-value example, the array example, the
  explicit-cosine example, and the dot example; 0.5 in the euclidean
  example), and no prose on the page states a default.
- **Confidence**: settled (the absence is documented; the *consequence* of the
  absence is not stated by the vendor)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Two things follow, and they compound. (a) An operator
  who writes `type: similar` with no `threshold` is relying on a default the
  documentation never states — the same shape as the unpinned-judge finding at
  Ch05 §699. (b) The euclidean example's `0.5` is the clearest possible signal
  that the authors themselves did not treat the number as portable across
  metrics: they changed it when they changed the metric. Note the compact
  assertion form `similar(0.8):value` (#1287 **Claim 12**) hard-codes a
  threshold into a one-line form that cannot express the metric, so the
  compact syntax is cosine-and-0.8-only in practice.

### Claim 10: The docs tie the metric choice to production vector-database parity — dot product is recommended specifically to match the production index, and is declared near-equivalent to cosine *only for normalized embeddings*
- **Evidence**: The Dot Product section's "When to use" sentence.
- **Confidence**: settled (documented product behavior); the coupling
  consequence is Miner synthesis
- **Quote**: "**When to use:** Useful when you want to match the metric used in your production vector database (many use dot product for performance). For normalized embeddings, dot product is nearly equivalent to cosine similarity."
- **Our assessment**: This makes the eval's metric a *dependent* of the
  production retrieval configuration, which is a different and stronger
  coupling than "an unpinned external model": a production index migration
  from dot product to cosine (or a normalization change) silently invalidates
  the eval's metric choice, and the eval config carries no marker that it was
  written to track production. The guide's useful rule is that the similarity
  metric is not a free parameter of the test suite — it is a mirror of the
  production retrieval metric, and both must be named together in the eval
  config. Related corpus thread: `blog-litellm-valkey-semantic-caching.md`
  **Claim 6** (a semantic cache hit is itself a cosine-similarity decision
  gated by `similarity_threshold`) — same construction, but in the gateway's
  serving path rather than the eval gate.

## Concrete Artifacts

All blocks below are copied character-for-character from the source markdown
at https://github.com/promptfoo/promptfoo/blob/main/site/docs/configuration/expected-outputs/similar.md
and verified against the rendered page at
https://www.promptfoo.dev/docs/configuration/expected-outputs/similar. Line
breaks are the source's own (the Docusaurus page renders these same blocks
collapsed onto single lines; the upstream `.md` restores the YAML structure).

### Base `similar` gate (verbatim — the page's first example)

```yaml
assert:
  - type: similar
    value: 'The expected output'
    threshold: 0.8
```

### Array / OR-over-acceptable-answers form (verbatim — note the `file://` list entry)

```yaml
assert:
  - type: similar
    value:
      - The expected output
      - Expected output
      - file://my_expected_output.txt
    threshold: 0.8
```

### All three metric variants side by side (verbatim from the "Similarity Metrics" subsections)

```yaml
assert:
  # Default - uses cosine similarity
  - type: similar
    value: 'The expected output'
    threshold: 0.8

  # Explicit cosine
  - type: similar:cosine
    value: 'The expected output'
    threshold: 0.8
```

```yaml
assert:
  - type: similar:dot
    value: 'The expected output'
    threshold: 0.8
```

```yaml
assert:
  - type: similar:euclidean
    value: 'The expected output'
    threshold: 0.5 # Maximum distance threshold
```

### Suite-wide embedding-provider override (verbatim from "Overriding the provider", item 1)

```yaml
defaultTest:
  options:
    provider:
      embedding:
        id: azureopenai:embedding:text-embedding-ada-002
        config:
          apiHost: xxx.openai.azure.com
tests:
  assert:
    - type: similar
      value: Hello world
```

### Per-assertion embedding-provider override (verbatim from "Overriding the provider", item 2)

```yaml
tests:
  assert:
    - type: similar
      value: Hello world
      provider: huggingface:sentence-similarity:sentence-transformers/all-MiniLM-L6-v2
```

### Metric ranges and threshold directions (compiled by the Miner from the three subsection opening sentences — each cell is traceable to a verbatim quote)

| Assertion type | Range (as documented) | Higher score means | Threshold means | Example threshold on the page |
| --- | --- | --- | --- | --- |
| `similar` / `similar:cosine` (default) | −1 to 1, "though text embeddings typically produce values between 0 and 1" | more similar | minimum similarity | `0.8` |
| `similar:dot` | "unbounded, but typically 0 to 1 for normalized embeddings" | more similar | minimum similarity | `0.8` |
| `similar:euclidean` | 0 to ∞ | more similar (i.e. *less* distance) | **maximum acceptable distance** | `0.5` |

*Cells are the Miner's compilation of the page's own range sentences (Claim 5)
and its two inversion statements (Claim 3); the page publishes no table.*

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 1** — this
    page is the primary source behind that claim's requirement-column entry
    "An embedding model" for `similar`, and behind the same note's
    Concrete Artifacts weighted `assert-set` example, whose second member is
    `- type: similar`. #1289 states the boundary (no model dependency); this
    page supplies the dependency's name, model, and override config. (Verified:
    #1289 Claim 1; weighted `assert-set` block in #1289 Concrete Artifacts.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 2** — that
    note's "deterministic means no judge, not no external dependency" caveat
    (quoting "Configured scripts, webhooks, and grouped assertions may still
    depend on external services") is corroborated here for a *built-in* type:
    `similar` is not a configured script or webhook, yet its default path
    reaches an external inference service. (Verified: #1289 Claim 2.)
  - `source-notes/docs-promptfoo-answer-relevance.md` **Claim 3** — that note
    documents a cosine-similarity aggregate whose "absolute meaning shifts
    when the embedding model … changes"; this page documents the same
    score-rebasing hazard on the *base* assertion it consumes, and adds the
    variable that note does not have: three metrics with different threshold
    directions. (Verified: #1319 Claim 3.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` **Claim 12** ("if
    two papers pick different automation defaults, the leaderboard mostly
    measures those defaults") — the same measurement-variable argument applied
    to eval-harness defaults: the `similar` gate's verdict is a function of an
    unpinned default embedding model and an undocumented default threshold,
    neither of which appears in the config a reviewer reads. (Verified: #261
    Claim 12.)
  - `source-notes/docs-promptfoo-classifier-grading.md` **Claim 5** ("thresholds
    are label-bound and non-portable … switching detectors requires
    recalibration") and **Claim 10** (a `classifier` gate "is a dependency on a
    remotely-hosted, mutable model endpoint … the gate's verdict is not
    hermetic with the repo") — a second instance of the same two-part failure
    class: model-dependent score, non-portable threshold, remote endpoint. The
    difference is that `classifier` makes the dependency loud (you name a
    detector) while `similar` hides it behind a default. (Verified: #1288
    Claims 5, 10.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 3** — the
    corpus's precedent that negation semantics must be read per-assertion
    rather than assumed to compose (numeric score compared against `threshold`
    *before* inversion there). This page ships no `not-similar` example at all,
    so Claim 4's inversion-under-negation is undocumented surface rather than
    documented behavior. (Verified: #1304 Claim 3.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** (pre-deployment
    testing "must be integrated into CI/CD pipelines and run on a recurring
    schedule") — thematic corroboration only: this note's subject is a
    per-commit release gate, which is the placement #555 argues for. No
    assertion-semantics overlap. (Verified: #555 Claim 4.)

- **Contradicts**: None identified, and no contradiction issue filed. Checked
  `CONTRADICTIONS.md` (no `C-NNN` entries yet — the file still reads "No open
  contradictions at MVP bootstrap") and all ten open `contradiction`-labeled
  issues; the two promptfoo-side ones (#1486 `rubricPrompt` portability, #1352
  g-eval default judge) are different assertions and different override
  surfaces. The nearest tension is with
  `docs-promptfoo-answer-relevance.md` **Claim 3**, which characterizes the
  `answer-relevance` score as "a cosine-similarity aggregate" without
  qualification; this page shows that "cosine" is a *default* that two of the
  three documented metrics abandon, with an inverted threshold direction in one
  case. That is a completion of the sibling's framing, not an opposition —
  `answer-relevance` is not documented as metric-selectable, so no claim
  actually conflicts. The page is internally consistent: the inversion is
    stated twice, and the example threshold changes with the metric.

- **Extends**:
  - `source-notes/docs-promptfoo-answer-relevance.md` (#1319) — that note
    documented the two-slot `provider: { text, embedding }` override for an
    assertion that needs both a question generator and an embedder. This page
    documents the same `embedding` slot key used *alone*, which is the reason
    a suite-wide `defaultTest.options.provider.embedding` set for
    `answer-relevance` silently rebases every `similar` gate too — a
    cross-assertion coupling neither page documents.
  - `source-notes/docs-promptfoo-deterministic-metrics.md` (#1289) — carries
    that note's "excluded from the deterministic tier because it needs an
    embedding model" down to the specific model, the two override shapes, the
    metric variants, and the negation semantics.
  - `source-notes/docs-promptfoo-configuration-caching.md` (#1275) — extends the
    "a green gate may evidence nothing" thesis to a gate whose *input* is a
    remote embedding of the expected value; the page is silent on cache
    participation for the embedding call, which is the open question a guide
    section should flag rather than assume.
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) **Claim 10**
    (the model-assisted family includes "similarity") and the
    `similar(threshold):value` → `similar(0.8):Hello world` table row in that
    note's unnumbered "Concrete Artifacts → Assertion string syntax samples"
    section — this page supplies
    the per-type semantics behind both, and shows the compact row's implicit
    metric-and-threshold assumption.

- **Novel** — none of the following appears anywhere in the corpus before this
  note. Verified by searching `source-notes/`: `euclidean`,
  `text-embedding-3-large`, `dot product`, and `not-similar` return **zero**
  pre-existing matches, and no existing note documents a similarity-*metric*
  choice (`cosine` appears only as an incidental descriptor inside
  `answer-relevance`, `conversation-relevance`, `context-recall`, the LiteLLM
  cache/semantic-cache notes, and `blog-litellm-valkey-semantic-caching.md`):

  1. **The euclidean threshold inversion** (Claim 3) — a documented
     maximum-distance threshold on a gate whose two sibling metrics use
     minimum-similarity thresholds. First corpus appearance of the word
     "euclidean" and of this inversion.
  2. **The three-metric range table** (Claim 5) — cosine −1..1, dot unbounded,
     euclidean 0..∞, with the vendor's own "typically" hedges as unstated
     preconditions on normalization.
  3. **`not-similar`-over-array as a NOR / forbidden-canned-answer-list gate**
     (Claim 6) — first corpus appearance of the phrase and of the
     monotonic-loosening property (appending to a forbidden list makes the
     gate weaker).
  4. **The default embedding model as a named, unpinned, remotely-hosted
     dependency** (Claim 1, Claim 8) — first corpus appearance of
     `text-embedding-3-large` and of the comparison showing that both
     documented "pin it" paths relocate the dependency rather than remove it.
  5. **The inversion-under-negation interaction** (Claim 4) — no `not-similar`
     example exists on the page at all, so the corpus had no coverage of this
     assertion's negated form.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)** — primary landing site, two sections:
  - **§"A generated dataset is the mutable external reference"
    (`guide/05-llm-ops-reliability.md:216`)**: this page is a *second*
    documented case of the same hermeticity violation, and a quieter one. The
    generated dataset is visibly a generator step; a `similar` gate is a single
    config line whose dependency is off-page. Add the concrete anchor: "By
    default, embeddings are computed via OpenAI's `text-embedding-3-large`
    model" [settled, Claim 1]. Extend the section's rule from datasets to
    model-dependent assertions: *record the embedding model id alongside the
    threshold, the way the section already requires recording the synthesis
    model alongside a generated fixture.*
  - **§"The judge behind a model-graded assertion is unpinned by default"
    (`guide/05-llm-ops-reliability.md:699`)**: the section's ambient-credential
    finding is about judge providers; `similar` is a different, simpler case
    worth its own paragraph — the *stated* default model, and no documented
    default threshold at all (Claim 9). Extend the section's "three further
    pinning traps" list with: an assert's metric is chosen by a type suffix
    invisible in the compact `similar(0.8):value` form (#1287 Claim 12), and
    the two override surfaces have an undocumented interaction with a
    suite-wide `provider.embedding` set for `answer-relevance` (Claim 7).
  - **§"Read the assert's own defaults before trusting its verdict"
    (`guide/05-llm-ops-reliability.md:443`)**: this section is the natural home
    for the metric-inversion rule, as a "the threshold's *direction* is part of
    the assert's contract" item alongside the `factuality` per-category
    defaults already documented there. Concretely add: for
    `similar:euclidean`, `threshold` is a maximum distance and lower is
    stricter [settled, Claim 3]; the docs' own example uses a different
    literal (`0.5` vs `0.8`) for that reason [Claim 9]; and the inversion
    compounds under `not-similar`, where no example exists at all
    [emerging, Claim 4]. The review checklist item: *does every `similar*` gate
    in this repo name its metric suffix and have its threshold re-calibrated
    against that metric and that embedding model?*
  - **§"A gate that cannot fail is not a gate"**: the array-semantics finding
    (Claim 6) is a distinct failure class worth one line — appending to a
    `not-similar` forbidden-answer list monotonically *loosens* the gate with
    no config error, so fixture growth is a silent strictness regression.

- **Chapter 02 (Observability)** — minor, as the triage anticipated. The
  embedding-model-version drift case is the same shape as any silent
  signal-semantics change: a gate whose verdict depends on a remote artifact
  that is not in your telemetry. If Ch02 carries a "what version was this
  number computed against" discipline for dashboards and alerts, this is the
  eval-side instance — the run report should carry the embedding model id
  alongside the score, or a post-hoc threshold regression is
  un-investigable. Pair with the existing cross-vendor note that a
  similarity decision is a correctness knob on the serving side
  (`blog-litellm-valkey-semantic-caching.md` **Claim 6**) and the eval side
  has the same missing unit.

## Extraction Notes

- Source read in full via direct HTTP fetch of the rendered Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/similar),
  then cross-checked against the upstream source markdown
  (https://raw.githubusercontent.com/promptfoo/promptfoo/main/site/docs/configuration/expected-outputs/similar.md)
  to recover exact code-block line breaks and the un-italicized wording. Every
  quoted string was taken from one of those two and matched character-for-
  character; the two agree except for italic markers (`_maximum_` →
  `*maximum*`) and a single space loss in an `apiHost` value introduced by
  the HTML extraction (`xxx.openai.azure.comtests:`), which is why the code
  blocks above are cited to the upstream markdown.
- No sub-pages followed. The page is self-contained — it links only to the
  assertion-type index and its two siblings (`ruby/`, `classifier/`), neither
  of which carries additional `similar` semantics. Per MINER.md §1 the budget
  went into re-reading the metric subsections against each other instead, which
  is what surfaced Claim 4 (inversion under negation, undocumented on the
  page).
- Dedupe per the Prospector's guidance: this note is an **addendum** to
  `docs-promptfoo-deterministic-metrics.md` (#1289), not a re-extraction. The
  `similar(threshold):value` shorthand from #1287 Claim 12 was deliberately not
  re-extracted (referenced only in Cross-References), and the
  "requires an embedding model" boundary from #1289 Claim 1 was not re-argued
  — only resolved to a named model and documented override config. What is new
  is the five-item Novel list above.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1275, #1277, #1287, #1288, #1289, #1304, #1319): individual
  mechanism/default claims (1, 2, 3, 5, 6, 7, 9) are settled-for-product-behavior
  and checkable against an installed CLI, but this is vendor documentation with
  no measured failure rate, no score distributions, no drift data, and no
  independent practitioner validation. Claim 4 is explicitly Miner synthesis
  from two documented rules and is marked `emerging` for that reason; Claims 8
  and 10 carry Miner operational synthesis on top of documented config values.
- `date_published` uses the page footer's "Last updated on Sep 30, 2026 by
  mldangelo-oai" (the page is undated in-body). The Prospector triage comment
  recorded Sep 29, 2026; the footer read Sep 30, 2026 at extraction time —
  re-check before citing the default model name in the guide, since a vendor
  docs page can change its default without a revision note.
- **Candidate list handling** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — each cited or dismissed
  by name):
  - `blog-promptfoo-owasp-red-teaming.md` — **cited** (Corroborates, #555
    Claim 4) for the CI/CD release-gate placement only; explicitly flagged as
    thematic, with no assertion-semantics overlap.
  - `docs-litellm-batches-api.md` — **dismissed**: LiteLLM batch rate limiting
    (TPM/RPM windows, enqueued-token limits); no eval-assertion surface.
  - `blog-pagerduty-sre-agent-triage.md` — **dismissed**: LLM-as-judge
    alerting and incident triage; the retrieval score goes through an
    assertion the note does not cover, and there is no config-semantics
    overlap.
  - `docs-promptfoo-classifier-grading.md` — **cited** (Corroborates, #1288
    Claims 5, 10): same two-part failure class (model-dependent score,
    non-portable threshold, remote endpoint) on the sibling assertion.
  - `docs-promptfoo-javascript-assertions.md` — **cited** (Corroborates, #1304
    Claim 3): the corpus precedent for reading negation semantics per-assertion
    rather than assuming they compose, which is the basis for treating Claim 4
    as live surface.
  - `docs-promptfoo-pi-scorer.md` — **dismissed**: that note's Claim 6 records
    that the `pi` page documents *no* `provider:` grader override, which makes
    it a useful contrast but not corroboration; `similar` documents two
    overrides, `pi` documents none, and the page contents do not bear on
    `similar`'s threshold semantics.
  - `docs-langfuse-mcp-server.md` — **dismissed**: documentation-MCP transport
    and client config; unrelated vendor and layer.
  - `docs-google-sre-slo-engineering-case-studies.md` — **dismissed**: SLO
    case studies (Evernote, Google); no LLM-eval assertion content.
  - `docs-google-sre-team-lifecycles.md` — **dismissed**: SRE team formation and
    lifecycles; no LLM-eval assertion content.
  - `docs-promptfoo-assertions-metrics.md` — **cited** (Extends, #1287 Claim 10
    and the compact-syntax row in that note's "Concrete Artifacts → Assertion
    string syntax samples" section): the family split and the compact-syntax
    row that hides the metric.
  - Additional cross-refs found by searching `source-notes/` per MINER.md §4
    and the Prospector's overlap list: `docs-promptfoo-deterministic-metrics.md`
    (#1289), `docs-promptfoo-answer-relevance.md` (#1319),
    `blog-promptfoo-asr-not-portable-metric.md` (#261),
    `docs-promptfoo-configuration-caching.md` (#1275),
    `blog-litellm-valkey-semantic-caching.md` (#1176).
- Every `Claim N` citation above was verified by re-reading the cited note and
  locating the numbered heading in document order (MINER.md §4b). Three
  cross-references are cited by note rather than claim number because the
  material lives in a non-numbered section: the `defaultTest.options.provider.embedding`
  suite-wide coupling of Claim 7 refers to #1319's "Overriding the Providers"
  configuration examples (also reachable as #1319 Claim 2); the `similar`
  member of #1289's weighted `assert-set` example refers to that note's
  "Concrete Artifacts" section; and the `similar(0.8):Hello world` compact-syntax
  row refers to #1287's "Concrete Artifacts → Assertion string syntax samples"
  section (the underlying `type(threshold):value` syntax rule, which is what the
  `Claim N` citations to #1287 Claim 12 point at, is in that note's numbered
  Claim 12 — *not* Claim 13, which is `assertionTemplates`/`$ref`).
- No contradiction issue filed, per MINER.md §4a: the only candidate tension
  (the unqualified "cosine" framing in #1319 Claim 3 versus this page's
  three-metric default) is a completion, not an opposition, because
  `answer-relevance` is not documented as metric-selectable. `CONTRADICTIONS.md`
  has no entries and none of the ten open `contradiction` issues concern this
  assertion. The two genuinely open surfaces (shorthand-vs-object provider
  inheritance on this page, and inversion-under-negation) are recorded as
  `emerging` claims and in Extraction Notes rather than filed as
  contradictions, since the sources do not disagree with each other — they are
  silent.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
