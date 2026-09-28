---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/pi/
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Pi Scorer"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-28
date_extracted: 2026-09-28
last_checked: 2026-09-28
status: current
confidence_overall: emerging
issue: "#1484"
---

# Promptfoo Configuration: Model-Graded — Pi Scorer

> The per-type reference page for promptfoo's `pi` assertion — the model's
> **first non-LLM-judge grader in the model-graded tier**, and the gap the hub
> note (#1305) explicitly left open ("the remaining per-type sub-pages
> (g-eval, pi, llm-rubric, ...) were not followed"). It contributes the
> corpus's **first grading topology that is neither an ambient-credential LLM
> judge nor an agent grader**: an externally-hosted dedicated scoring model
> reached through the `withpi` SDK and a separately-issued `WITHPI_API_KEY`
> (Claim 1, Claim 2), a **determinism claim with zero supporting evidence on
> the page** — "Pi always generates the same score, when given the same input"
> is stated flatly with no calibration data, no agreement figures, and no
> repeat-run example, and the substance is deferred to an off-site vendor
> document (Claim 3) — the **inverse auditability tradeoff**, since the score
> arrives explicitly "without providing detailed reasoning" (Claim 4), a
> **second, cross-page-corroborated `0.5` default threshold** (Claim 5), and
> the finding that **the family's judge-pinning and rubric-override levers
> have no documented surface here at all** (Claim 6) plus **no `not-`
> negation section** — so the guide's pin-the-judge rule is *unsatisfiable*
> for this assert type and a `not-pi` "must not leak PII" gate has no
> documented behavior on this page.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Pi Scorer"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `pi` behavior — authoritative for *what promptfoo does* with a
  given `pi` config (the `withpi` SDK call, the `WITHPI_API_KEY` prerequisite,
  the threshold contract, the input fields), but this page is thinner and more
  vendor-positioned than any sibling in the family: its two load-bearing
  performance claims ("highly accurate numeric scoring", "Pi always generates
  the same score, when given the same input") carry no measurement, no
  calibration data, and no worked repeat-run example, and the page routes the
  reader to Pi Labs' own off-site documentation for "more options,
  configuration, and calibration details". The page is also third-party
  integration content: its footer reads "Last updated on **Sep 28, 2026** by
  **Aniket Kumar**", a different author string from the promptfoo-engineer
  faceplates on the sibling pages (`mldangelo-oai` on `llm-rubric`,
  `jameshiester-oai` on `g-eval`), which is consistent with a partner-integration
  page rather than a core product page. Everything below is checkable against
  an installed CLI; the determinism and accuracy claims are not checkable from
  this page at all.
- **Scope**: An eight-section reference page (Alternative Approach,
  Prerequisites, How to use it, How it works, Threshold Support, Metrics
  Brainstorming, Example Configuration, See Also). It is the per-type
  deep-dive on the one member of the model-graded class that `pi`-class
  `docs-promptfoo-model-graded-metrics.md` (#1305) catalogued at claim level
  and explicitly did **not** follow — that note's Extraction Notes list "pi"
  among the unf followed sub-pages, and it separately flags `pi` as a
  "novel capability surface" only in the *navigation* (the sidebar's Pi Scorer
  entry). The page does **not** document a `provider:` grader override, a
  `rubricPrompt` slot, negation, a `not-` inversion, a score range statement
  beyond "greater than or equal to the threshold", a cost figure, a latency
  figure, a data-handling/retention statement, a self-hosted or on-prem
  option, or any failure semantics for an unreachable/rate-limited/absent-key
  Pi API. Those absences are load-bearing and are recorded as claims (Claim 6)
  or assessments, not invented.
- **Second vendor surface, also read**: the `### Pi` stub retained on
  https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/
  — the same assertion documented on a second promptfoo page, which
  corroborates the `0.5` default independently (Claim 5) and characterizes the
  grader differently ("Pi Labs' preference scoring model", Claim 4's
  assessment). This is **not** the note's `source_url`; it is cited by URL
  where used, and its code block is reproduced separately in Concrete
  Artifacts.
- **Outbound links**: `https://docs.withpi.ai` (the calibration/options
  pointer), `https://build.withpi.ai` (the Copilot and the API-key console),
  `https://build.withpi.ai/account/keys`, plus the in-corpus `llm-rubric` and
  model-graded-hub pages. **Both Pi Labs domains were unreachable from the
  mining runner** (DNS resolution failure for `docs.withpi.ai` and
  `build.withpi.ai`; the promptfoo host resolved normally), so the
  calibration material the page defers to could not be read. See Extraction
  Notes.

## Extracted Claims

### Claim 1: `pi` is the model-graded family's only non-LLM-judge grader — it delegates scoring to a dedicated, externally-hosted scoring model via the `withpi` SDK, grades an `llm_input`/`llm_output` pair against a criteria string, and needs no system prompt because the model is pretrained to score
- **Evidence**: The page's opening definition, the "Alternative Approach"
  bullet list, the "How it works" section's SDK sentence and its four-bullet
  "Compared to LLM as a judge" list (both reproduced verbatim in Concrete
  Artifacts).
- **Confidence**: settled (documented product behavior)
- **Quote**: "`pi` is an alternative approach to model grading that uses a dedicated scoring model instead of the \"LLM as a judge\" technique. It can evaluate input and output pairs against criteria." and "Under the hood, the `pi` assertion uses the `withpi` SDK to evaluate the output based on the criteria you provide." and "Pi does not need a system prompt, and is pretrained to score"
- **Our assessment**: This is the reason the page is worth a note, and it is a
  genuinely new *grading topology* for the corpus — not a new judge model. The
  two topologies the corpus already documents are (a) promptfoo's built-in
  grading provider, ambiently credential-selected (#1305 Claim 1) and (b) an
  agent runtime (`agent-rubric`, #1305 Claim 11). `pi` is neither: no LLM is
  prompted, so none of #1305's judge-prompt surface exists here — no rubric
  system prompt to tune, no `showThinking` scratchpad to misparse, no
  `provider:` to select. Three consequences follow, and they are the guide-
  relevant part. (a) **The "no system prompt" property removes an entire
  failure class and adds nothing**: the scratchpad-misparse family (#1305
  Claims 5-6) is structurally impossible when the grader emits no text. (b)
  **The criteria surface is a single natural-language string**, not a rubric
  template — so the multilingual `rubricPrompt` override that #1305 Claim 8
  documents does not reach this type even in principle (that claim's reach
  list is `llm-rubric`/`g-eval`/`model-graded-closedqa` only, and `pi` is not
  on it). A non-English `pi` gate must therefore express its criteria in the
  language the criterion is written in, with no documented override. (c) The
  corpus's #261 finding that *specific* rubrics make different judge models
  converge (Claim 11 there) cannot be applied by model-swapping here, because
  there is no model to swap and no other judge to converge with — rubric
  specificity still controls the score, but for one grader, not for a
  population of them. The net assessment: `pi` removes judge-prompt variance
  and judge-prompt attack surface, and pays for it with an audit trail
  (Claim 4) and a pinning surface that does not exist (Claim 6).

### Claim 2: `pi` requires a separately-issued third-party credential — a Pi Labs API key created at Pi Labs' own console and supplied as `WITHPI_API_KEY` — and the vendor names the difference from the family explicitly: unlike `llm-rubric`, it does not run on your existing providers
- **Evidence**: The `note` admonition directly under the page title (the page's
  only admonition), the two-step "Prerequisites" list, the `export` code block,
  and the config-file `env:` alternative (both in Concrete Artifacts).
- **Confidence**: settled (documented product behavior)
- **Quote**: "**Important**: Unlike `llm-rubric` which works with your existing providers, Pi requires a separate external API key from Pi Labs." and "To use Pi, you **must** first:" / "1. Create a Pi API key from [Pi Labs](https://build.withpi.ai/account/keys)" / "2. Set the `WITHPI_API_KEY` environment variable"
- **Our assessment**: Two effects that must be kept apart, because they point
  in opposite directions for the guide's judge-trust material. **On judge
  identity, this is an improvement over #1305 Claim 1** — the grader is no
  longer a function of which credentials happen to lie around on the runner;
  it is a function of which key you deliberately provisioned, so the
  "add one API key and the grader silently swaps" hazard does not apply to
  `pi`. **On pinning, it is a loss, and it is the more important half** — the
  key names a *vendor*, not a model. Nothing on this page (or on the
  promptfoo provider surface generally: `/docs/providers/withpi` returns
  HTTP 404 and the providers index carries no `withpi` entry) tells you which
  scoring model a given `WITHPI_API_KEY` resolves to, whether that model is
  versioned, or whether Pi Labs may change it server-side. So the guide's
  pinning rule is not merely unsatisfied here (Claim 6) — the artifact it asks
  you to pin **does not exist in the config surface at all**. The Ch05 rule
  needs a named third state between "ambient" and "pinned": *vendor-named,
  model-opaque*. **On data, this is a new egress destination**: the graded
  payload is the eval's own `llm_input` and `llm_output` (Claim 9) sent to a
  third-party scoring endpoint — not a summary, not a hash, the prompt and the
  completion. The difference from the ambient judge matters for a security
  review: an ambient judge is a provider you have already contracted, already
  pay, and can already route through your own gateway (per the g-eval
  note's documented LiteLLM grader-reuse pattern, #1349 Claim 8). `pi` has no
  documented self-hosted, proxy, or LiteLLM-reuse route — the *only*
  documented path is the vendor's SaaS key. The page documents no retention
  policy, no region, no redaction, and no training-use statement, and it
  defers the whole "configuration" question off-site. For Ch06 that is a
  concrete gap to record: a promptfoo gate can be made to ship production-
  shaped prompt/response pairs to a vendor that is not your model provider,
  and the page offers no way to audit or route that.

### Claim 3: The determinism claim is a flat vendor assertion with no evidence attached — the page states "always the same score" as a guarantee, gives no calibration data, no agreement figures, and no worked repeat-run example, and defers the substance of both accuracy and calibration to an off-site vendor document
- **Evidence**: The "How it works" bullet list (determinism stated as one of
  four bullets), the "Alternative Approach" bullet list (which states a
  *weaker* consistency property), and the "See Also" pointer. The page's
  entire "Metrics Brainstorming" section is about finding a threshold, not
  about validating the score.
- **Confidence**: anecdotal (as a property of the grader — it is a vendor
  design statement with zero supporting evidence on the page; the *surrounding*
  behavior claims in this note are settled)
- **Quote**: "Pi always generates the same score, when given the same input" and "Aims for consistency in scoring the same inputs" and "[Pi Documentation](https://docs.withpi.ai) for more options, configuration, and calibration details"
- **Our assessment**: This is the load-bearing claim of the page and the one a
  guide must not repeat as fact. Three problems, in increasing order of
  severity. (1) **The page states two different strengths of the same
  property with nothing between them**: the summary list says the approach
  "Aims for consistency in scoring the same inputs" (an aspiration) and the
  mechanism list says "Pi always generates the same score" (a guarantee).
  Nothing on the page connects them, and the guarantee is the one a reader
  will quote. (2) **"Same input" is doing unstated work.** The determinism is
  a claim about a *version* of the scoring model, and the page names no
  version. Whether the score is stable across changes to the criterion string,
  across Pi Labs model updates behind the same key, or across a change of the
  scoring system's internal composition is not addressed, and cannot be
  addressed from this page. A versioned guarantee with no version named is not
  a guarantee. (3) **Determinism and calibration are orthogonal, and only the
  first is claimed.** The corpus already knows this from the other direction:
  #261 Claim 8 shows that two judges with *identical* 80% accuracy produce a
  14-point ASR gap purely from differing TPR/FPR, so headline agreement does
  not predict verdict behavior; the page here claims the opposite axis (that
  the verdict does not move) and says nothing about whether it is *right*. A
  reproducible score is a reproducible *error*: a gate whose score is frozen
  and whose bias is constant fails the same rows on every run, forever, and
  that is precisely the "silently green" shape the guide's Ch05 table is built
  to catch. The operational rule this implies is not "avoid `pi`" but "a
  deterministic grader does not earn you a pass on the negative-control
  requirement": a `pi` gate still needs one deliberately-wrong case that must
  fail, and a `pi` threshold still needs a calibration population recorded
  (Claim 8), because a score that cannot move cannot tell you it is wrong.
  Practical note for the resolver and for future Miners: Pi Labs' own
  conference talk by David Karam (ai.engineer,
  `https://ai.engineer/talks/jxrGodnopHo-building-metrics-that-actually-work`)
  describes the determinism as architectural — a bidirectional encoder with a
  regression head rather than autoregressive generation of score tokens, and
  explicitly distinguishes it from the "generate a score, then generate a
  post-hoc justification" pattern. That is a *mechanism* explanation, not a
  measurement, and it is not part of the extracted source; it is recorded here
  as the likely reason the claim is plausible and as the place to look for
  calibration data. I did not verify it verbatim against the transcript and
  quote nothing from it.

### Claim 4: The determinism is purchased by giving up the rationale — the grader's product is a number and explicitly not an explanation, and the same bullet asserts "highly accurate" with the same absence of evidence
- **Evidence**: The second bullet of the "Alternative Approach" list,
  reproduced verbatim below. The page documents no reason field, no
  decomposition, and no metadata marker for `pi` anywhere (contrast the
  `renderedGradingPromptAudio` marker documented for `llm-rubric` audio
  grades, #1471 Claim 4).
- **Confidence**: settled for the no-reasoning property (it is stated);
  anecdotal for the "highly accurate" half of the same bullet (unevidenced on
  the page, same status as Claim 3)
- **Quote**: "Focuses on highly accurate numeric scoring without providing detailed reasoning"
- **Our assessment**: The exact inverse of the LLM judge, on both axes at
  once, and the guide should name it as a deliberate trade rather than an
  oversight. The whole failure taxonomy in #1305 Claims 5-6 is about reasoning
  text going *somewhere it should not* — a `thinking` block parsed as a
  verdict, a scratchpad number read as a winning index — and the fix there is
  `showThinking: false` plus positive markers. `pi` is the assert type where
  that whole class is impossible *and* where the debugging handle is gone by
  construction. Operationally this means the report for a `pi` row carries the
  score, the threshold, and the criterion string, and nothing that explains
  the score; a reviewer asking "why did this score 0.62?" has no artifact to
  ask. That is a real cost for a CI gate whose incident story is usually
  "explain the last red row", and it is the reason the guide's
  "can your gate tell wrong from a broken judge?" checklist needs a `pi`-shaped
  answer: for this type the honest answer is *the gate cannot explain itself*,
  so the compensating control is not a log field — it is the negative control
  (Claim 3) plus a threshold whose calibration set is recorded (Claim 8).
  Note also the second-page wording difference: the deterministic page's `pi`
  stub calls it "Pi Labs' preference scoring model", a mechanism-flavoured
  description that the model-graded page does not use. The two pages do not
  disagree, but only one of them tells a reader anything about *what kind* of
  model produces the number. I do not claim a `renderedGradingPrompt`-
  equivalent field does not exist in the eval report — only that this page
  documents none, which is a silence, not a prohibition.

### Claim 5: `pi` documents a non-zero default threshold of `0.5` — independently corroborated by a second promptfoo page that carries the same default in a config comment — making it the only default threshold in the family documented twice
- **Evidence**: The "Threshold Support" section's `info` callout and its
  worked `threshold: 0.8` config; plus the `### Pi` stub on the deterministic
  page, whose example carries the inline comment
  `# Optional, defaults to 0.5` (reproduced in Concrete Artifacts).
- **Confidence**: settled (documented product behavior, cross-page
  corroborated)
- **Quote**: "The default threshold is `0.5` if not specified." and "When specified, the output must achieve a score greater than or equal to the threshold to pass."
- **Our assessment**: This turns #1334 Claim 2's per-type-defaults doctrine from
  an observed pattern into a settled rule, and the inventory it produces is
  now large enough to state as a rule rather than a curiosity. Documented
  defaults across the family: `0` for `context-faithfulness` (#1320 Claim 2)
  and `context-recall` (#1332 Claim 2); `0.5` for `conversation-relevance`
  (#1334 Claim 2) and now `pi`; `0.7` for `g-eval` (#1349 Claim 3); none stated
  at all for `answer-relevance` (#1319 Claim 3), `max-score` (#1472 Claim 5),
  or `llm-rubric` (whose absence is the score-blind pass, #1305 Claim 10).
  Four different outcomes across the family — a fail-open `0`, two non-zero
  values, an unstated default, and a score-blind pass — is enough to make
  "model-graded asserts don't gate by default" unusable as a general rule and
  to make the per-type read mandatory. The operational consequence for `pi`
  specifically is the *good* one on this list: unlike the `0` members, a bare
  `assert: - type: pi` **can** fail at default config, so `pi` belongs on the
  "can this gate fail?" side of the guide's Ch05 table rather than in it. The
  review consequence is the *normal* one: the per-assert default is only half
  the gate, because a test-case or `assert-set` `threshold` below it, or an
  assertion `weight` of 0, still washes it out (#1287 Claims 1, 4, 5), and a
  `max-score` aggregate over `pi` scores inherits the same mixed-scale-average
  hazard as any other continuous scorer (#1472 Claim 3). Set the `pi`
  threshold explicitly and do not let the default stand in for a calibration
  decision (Claim 8).

### Claim 6: The page documents no `provider:` grader override, no `rubricPrompt`, and no `not-` negation — so the two levers the guide's model-graded rules are built on have no documented surface here, and `pi` is the first model-graded per-type page in the corpus with no negation section at all
- **Evidence**: The page's complete section list (Alternative Approach,
  Prerequisites, How to use it, How it works, Threshold Support, Metrics
  Brainstorming, Example Configuration, See Also), verified by full read: the
  strings `provider`, `rubricPrompt`, `not-`, and `negat` appear nowhere in
  the fetched rendered content, and the "See Also" list offers only LLM
  Rubric, Model-graded metrics, and the off-site Pi Documentation. (Note:
  `providers:` does appear once — in the Example Configuration, where it is
  the **target** under test; see Claim 10.)
- **Confidence**: settled **as page silence** — the absence of documentation is
  verified; this is explicitly **not** a claim that the underlying behavior is
  unsupported, and no CLI probe was run to test it
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the highest-value claim for the guide, because it
  makes an existing guide rule *wrong* as written rather than merely
  incomplete. Ch05's judge-pinning rule reads "Pin the judge explicitly
  (`--grader`, `defaultTest.options.provider`, or the assertion's own
  `provider:`)" — for `pi` none of those three levers is documented, so a
  reader who greps the config for a judge pin and finds `providers:
  openai:gpt-5` (Claim 10) will believe they pinned the grader. They pinned
  the target. The guide needs a named third state, not a silent omission:
  `pi`'s grader is **vendor-named and model-opaque** — a key plus a SaaS
  endpoint, with no config surface for the model behind it. The same applies
  to the multilingual-grading guidance: there is no `rubricPrompt` slot to
  reskin, so a non-English `pi` gate is stuck with the criterion as written.
  The **negation** half is a second, independent finding. #1287 Claim 10
  states "Every test type can be negated by prepending `not-`", and three
  per-type pages now carry a documented, symmetric, fail-closed inversion
  sentence: `not-trajectory:goal-success` (#1305 Claim 4), `not-g-eval`
  (#1349 Claim 5), and `not-llm-rubric` (#1471 Claim 7). The llm-rubric note
  drew the right operational inference from that pattern — treat the absence
  of that sentence on a *new* assert type as a question for the vendor, not
  as an implied pass. `pi` is that case, and it is the first page where the
  question is sharper, because #1471 Claim 9 notes the vendor's own steer that
  a grading capability which changes the trust boundary belongs in a
  *dedicated* assert type — and the `pi` page is such a type (external vendor,
  new credential, new egress) with no inversion semantics documented. So for
  the exact Ch06 shape the guide already uses — a `not-pi` "must not leak PII"
  gate — this page documents neither what a grader transport failure does to
  the verdict nor what inverting a 0-1 score would even mean. I follow the
  precedent set by #1472 Claim 9, which recorded the identical observation for
  `max-score` (hub blanket rule vs page silence) and also declined to file;
  consistency says record it as page silence, not as opposition. Two per-type
  pages now lack negation sections and three carry them, which strengthens the
  per-type-read doctrine rather than creating a conflict between sources.

### Claim 7: The vendor's own documented second path for the new third-party credential is to place it in the promptfoo config file, and the page presents no protection, templating, or secret-handling guidance for that file
- **Evidence**: The "Prerequisites" section's second code block, reproduced
  verbatim below, and the connective prose around it ("or set" … "in your
  promptfoo config").
- **Confidence**: settled (that the config-file placement is a documented
  option); the file's protection is **not documented** and is not claimed
- **Quote**: "or set" and "in your promptfoo config" (the intervening code
  block is reproduced verbatim in Concrete Artifacts)
- **Our assessment**: Small, concrete, and worth a Ch06 line plus one
  deliverables item. The vendor puts the env var first and the config file
  second, which is the right order, and a guide rule can simply keep that
  order and name the second path as documented-but-worse. What is worth
  recording is *why* it matters: promptfoo configs are normally checked-in
  YAML that teams review in PRs, so a newly documented path for a *new*
  vendor's key is a path by which a third-party credential lands in a diff.
  The page does not say the config is gitignored, does not say the value is
  templated, and does not say whether promptfoo warns on a plaintext key in
  `env:`. Two small, checkable follow-ups for a team adopting `pi`: add
  `WITHPI_API_KEY` to the secret-scanner list alongside every other
  provider key in the runner, and add it to the CI secret inventory — because
  unlike the ambient judge, this key has exactly one purpose and its absence
  is not something a credential swap will paper over. The absence-of-key
  behavior is itself undocumented (Claim 6's family): the page says you
  **must** set the variable and does not say what a `pi` assert does without
  it — fail the run, or score nothing.

### Claim 8: The only documented threshold-calibration procedure is an interactive loop in a separate web product — "Find the optimal threshold values for your use case" is done in the Pi Labs Copilot — and the page documents no API, export, or versioned artifact for it
- **Evidence**: The "Metrics Brainstorming" section: its one-sentence
  introduction, the `build.withpi.ai` link, and its three numbered items
  (reproduced verbatim below).
- **Confidence**: settled (that the documented calibration path is the
  interactive Copilot); the reproducibility properties of that process are
  **not** documented and are not claimed
- **Quote**: "You can use the [Pi Labs Copilot](https://build.withpi.ai) to interactively brainstorm representative metrics for your application." and "Find the optimal threshold values for your use case"
- **Our assessment**: The operations half of the determinism story, and the
  part that composes badly with Claim 3. A deterministic score is worth
  exactly as much as the threshold it is compared against, and the only
  procedure the page offers for choosing that threshold is a human in a
  browser, on a product that is not promptfoo and not in the config. So a
  `threshold: 0.8` in a checked-in config has **undocumented provenance**:
  nothing in the repo records the population it was chosen on, and nothing
  records that it *was* chosen rather than copied from the page's own example
  (the `0.8` in the Threshold Support block is the vendor's illustrative
  value, not a calibrated one — worth saying plainly, because it is the number
  a reader is most likely to copy). This is a **new class of
  non-reproducible artifact, and it is at the threshold layer rather than the
  judge layer** — the corpus already has a hermetic-replay rule for the judge
  layer (#1287/#1275 via #1305's Guide Impact) and a cost ladder for the
  grader. The two defects compose in the worst direction: a frozen score
  compared against a threshold whose provenance is a chat session produces a
  gate that is perfectly stable and completely unjustified. The rule to
  extract: treat a `pi` threshold as a **calibration artifact** — record the
  set it was chosen on next to it (a comment, a dataset ref), treat the
  Copilot session as the offline design step rather than the runtime, and
  re-calibrate on the same schedule the guide already requires for judge
  changes. Note the asymmetry with the family's own tooling: the
  `metrics-brainstorming` step is the one part of this workflow that is
  *designed* to be interactive, which makes it the most likely to be skipped
  in a CI-first team's setup — and skipping it is what produces a bare
  `threshold: 0.5` (Claim 5) nobody chose.

### Claim 9: The graded payload is the eval's own input/output pair — the page names the fields `llm_input` and `llm_output` and states they are the same as the LLM-judge case, with no context channel, no rendering, and no summarization
- **Evidence**: The first bullet of the "How it works" comparison list,
  reproduced verbatim in Concrete Artifacts.
- **Confidence**: settled (documented contract)
- **Quote**: "The inputs of the eval are the same: `llm_input` and `llm_output`"
- **Our assessment**: Two things, one checkable and one derived. The
  checkable half: the graded object is a **pair of strings**, the prompt and
  the completion, and the criterion is a single question about them. That has a
  concrete porting hazard, because the family's RAG asserts are the common
  case teams port to a new grader: `context-recall` requires a `context`
  field alongside `value` and grades the *retrieval* side of the pair
  (#1332 Claim 3), and `context-faithfulness` grades output fidelity against
  that same supplied context (#1320). A `pi` assert has no context slot, so a
  RAG gate ported to `pi` grades the completion **in isolation** — unless the
  retrieved context is inside the completion text, in which case `pi` is
  grading a concatenation and the criterion has to say so. That is a silent
  weakening of exactly the kind the guide's table is about: the gate still
  returns a score, the report still looks normal, and the property it can no
  longer see is grounding. A `pi` RAG gate should assert that its `value`
  criterion names the context, or should not be a `pi` gate. The derived
  half, flagged as mine: the field names are the vendor's own API field names
  rather than promptfoo's internal terminology, which is consistent with the
  graded payload being a plain request/response body that crosses a network
  hop to a hosted service. That is a reading of naming, not a statement from
  the page, and it does not add anything the page does not already say about
  the egress (Claim 2). What the page does **not** say — and this is the
  point — is anything about how those strings are handled after they arrive.

### Claim 10: The only complete config on the page pins the *target* under test and names no grader at all — `providers: - openai:gpt-5` sits in the same file as two `pi` asserts, which is precisely the shape a reader will mistake for a pinned judge
- **Evidence**: The "Example Configuration" block, reproduced verbatim below.
  The `providers:` key is promptfoo's target-provider key (the same key the
  g-eval note's LiteLLM-reuse example uses at the top level to declare the
  provider under test, #1349 Claim 8, and the same key the closedqa example
  uses, #1483 Claim 1), and no grader identity appears anywhere in the block.
- **Confidence**: settled (about the config's content and the key's meaning
  from the family-wide contract); the misreading consequence is Miner
  synthesis, flagged as such
- **Quote**: (no direct quote — the block is a YAML artifact, reproduced
  verbatim in Concrete Artifacts)
- **Our assessment**: The guard-worthy detail is that this is the *only*
  full config on the page, so it is the thing a reader copies, and it contains
  exactly one model ID in a `providers:` block that a reader applying Ch05's
  "pin every model artifact behind a verdict" rule will point at as the pinned
  judge. It is the target. This is the concrete failure mode behind Claim 6's
  "vendor-named, model-opaque" finding, and it is a config-reading trap rather
  than a behavior claim, which makes it cheap to check: in any `pi` config,
  every model ID in a `providers:` key is a target, and none of them is the
  grader. Two supporting observations from the same block and the second
  vendor page. First, the example encodes its two criteria as **two separate
  `pi` asserts** with independent thresholds (`0.7` and `0.8`) rather than one
  combined criterion, and the deterministic page's stub says the same thing in
  words — so per-criterion granularity is the documented shape, which is the
  right posture given #1349 Claim 4's array-averaging lesson: never let an
  aggregate stand in for per-criterion gates. Second, and the honest
  counterweight to every concern above: this config *does* set explicit
  thresholds on both asserts, which is the single thing the guide's Ch05
  "can this gate fail" rule asks for. So the vendor's own example is a
  non-decorative `pi` gate. It is the *judge* that it does not pin, because
  it cannot.

## Concrete Artifacts

All promptfoo artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/pi/
(section named per block). Code blocks were reconstructed from the page's
Prism `token-line` markup so that the site's YAML indentation is preserved
(the plain-text fetch collapses it); token content is unchanged.

### The admonition (verbatim from the note callout under the page title)

> **Important**: Unlike `llm-rubric` which works with your existing providers,
> Pi requires a separate external API key from Pi Labs.

### Prerequisites — environment variable (verbatim from "Prerequisites")

```bash
export WITHPI_API_KEY=your_api_key_here
```

### Prerequisites — config-file alternative (verbatim from "Prerequisites")

```yaml
env:
  WITHPI_API_KEY: your_api_key_here
```

### The vendor's characteristic list (verbatim from "Alternative Approach")

```
- Uses a dedicated scoring model rather than prompting an LLM to act as a judge
- Focuses on highly accurate numeric scoring without providing detailed reasoning
- Aims for consistency in scoring the same inputs
- Requires a separate API key and integration
```

Verbatim framing sentence: "Pi offers a different approach to evaluation with
some distinct characteristics:"

Verbatim closing sentence: "Each approach has different strengths, and you may
want to experiment with both to determine which best suits your specific
evaluation needs."

### Basic usage (verbatim from "How to use it")

```yaml
assert:
  - type: pi
    # Specify the criteria for grading the LLM output
    value: Is the response not apologetic and provides a clear, concise answer?
```

### The mechanism comparison list (verbatim from "How it works")

```
- The inputs of the eval are the same: `llm_input` and `llm_output`
- Pi does not need a system prompt, and is pretrained to score
- Pi always generates the same score, when given the same input
- Pi requires a separate API key (see Prerequisites section)
```

Verbatim framing: "Compared to LLM as a judge:"

### Threshold support (verbatim from "Threshold Support")

```yaml
assert:
  - type: pi
    value: Is not apologetic and provides a clear, concise answer
    threshold: 0.8 # Requires a score of 0.8 or higher to pass
```

Verbatim `info` callout: "The default threshold is `0.5` if not specified."

### Metrics Brainstorming — the documented calibration procedure (verbatim from "Metrics Brainstorming")

```
1. Generate effective evaluation criteria
2. Test metrics on example outputs before integration
3. Find the optimal threshold values for your use case
```

### The only complete config on the page (verbatim from "Example Configuration")

Note: the `providers:` block is the **target** under test, not the grader —
no grader identity appears in this config.

```yaml
prompts:
  - 'Explain {{concept}} in simple terms.'
providers:
  - openai:gpt-5
tests:
  - vars:
      concept: quantum computing
    assert:
      - type: pi
        value: Is the explanation easy to understand without technical jargon?
        threshold: 0.7
      - type: pi
        value: Does the response correctly explain the fundamental principles?
        threshold: 0.8
```

### Second vendor surface — the retained `### Pi` stub on the deterministic page

From https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/
— **not** this note's `source_url`. Reproduced because it is the independent
corroboration of the `0.5` default (Claim 5) and the second, differently-worded
characterization of the grader (Claim 4's assessment).

Verbatim prose:

> The `pi` assertion uses Pi Labs' preference scoring model as an alternative
> to LLM-as-a-judge for evaluation. It provides consistent numeric scores for
> the same inputs.

Verbatim note: "Requires `WITHPI_API_KEY` environment variable to be set."

Verbatim example (the `# Optional, defaults to 0.5` comment is the
cross-page corroboration of Claim 5):

```yaml
assert:
  - type: pi
    value: 'Is the response not apologetic and provides a clear, concise answer?'
    threshold: 0.8 # Optional, defaults to 0.5
```

Verbatim multi-criteria lead-in: "You can use multiple Pi assertions to
evaluate different aspects:"

Verbatim boundary sentence introducing that stub's whole section, which is
what places `pi` outside the deterministic tier despite the stub living on
that page: "These checks use an additional model or external inference service.
Their sections remain here for existing links:"

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` (#1289) **Claim 1**
    — the vendor's own deterministic/model-graded boundary, whose mini-table
    already lists `pi` with the requirement "A Pi Labs scorer" among the
    checks that "use an additional model or external inference service". This
    page is the per-type reference *under* that one catalogue row, and it
    confirms the row's shape: an external scorer, its own key, and no
    self-hosted route. That note's cross-page framing that "deterministic" in
    promptfoo's sense means no model judge rather than no external dependency
    (its Claim 2) is the exact distinction `pi` sits on: it is neither tier.
    (Verified: read Claim 1 and its quote in #1289 directly.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 1**
    — the family-wide unpinned-judge finding. This page is the required test
    of whether that finding still applies to a *non*-LLM-judge member, and
    the answer is **no, and the guide should say so explicitly**: `pi` names
    its vendor and its credential, so the ambient-credential *swap* hazard
    does not apply — but neither does the pin (Claim 2, Claim 6). The finding
    is not contradicted; it is bounded, and this page supplies the boundary.
    (Verified: read Claim 1 and its verbatim quote in #1305.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 5**
    (the cross-family scratchpad-misparse list) — `pi` is the confirming
    negative case on a different axis: it emits no grader text at all, so the
    whole class is structurally absent rather than merely mitigated
    (Claim 1(a), Claim 4). (Verified: read Claim 5 in #1305.)
  - `source-notes/docs-promptfoo-llm-rubric.md` (#1471) **Claim 5** — the
    per-credential default-judge roster with concrete model IDs. This page is
    the contrast case the vendor's own admonition names: `pi` has a roster of
    one, a *separate external key*, and no roster of models. The page's
    "Unlike `llm-rubric` which works with your existing providers" sentence
    is the vendor stating the difference between the two topologies in one
    line, which is stronger evidence than any Miner inference. (Verified:
    read Claim 5 and the roster artifact in #1471 directly.)
  - `source-notes/docs-promptfoo-llm-rubric.md` (#1471) **Claim 7** — the
    third instance of the symmetric fail-closed `not-` inversion sentence, and
    its assessment's operational inference: the convention holds across the
    per-type pages mined so far, so "treat its absence on a *new* assert type
    as a question for the vendor rather than as an implied pass." This page is
    that new assert type, and the absence is verified (Claim 6). Also
    **Claim 4** — the positive-marker rule for a graded channel the report
    does not render (`renderedGradingPromptAudio`), the control `pi` has no
    analogue for, since it has no rationale to render in the first place
    (Claim 4). (Verified: read Claims 4, 5 and 7 in #1471 directly.)
  - `source-notes/docs-promptfoo-conversation-relevance.md` (#1334) **Claim 2**
    — the `0.5` default and the per-type-defaults doctrine ("each page must
    be read on its own"). `pi` documents the same `0.5` and is the first
    default in the family documented on two pages, which turns the doctrine
    into a settled rule (Claim 5). (Verified: read Claim 2 and its quote in
    #1334 directly.)
  - `source-notes/docs-promptfoo-g-eval.md` (#1349) **Claim 3** — the
    non-zero `0.7` default, the strongest counter-member to the `0` family.
    `pi`'s `0.5` is a third value in the same inventory and confirms no family
    default exists. **Claim 8** — the documented LiteLLM grader-reuse pattern
    is the concrete answer to what `pi` does *not* have: a self-hosted or
    proxied grader route, with the target restricted in `tests[].providers`.
    `pi` has no equivalent, which is why the vendor named model opacity rather
    than a pinned judge as the trade (Claim 2). (Verified: read Claims 3 and 8
    and the LiteLLM-reuse artifact in #1349 directly.)
  - `source-notes/docs-promptfoo-classifier-grading.md` (#1288) **Claim 5** —
    thresholds are scorer-bound and non-portable: the worked values are
    "meaningful only for the specific model and label set, and switching
    detectors requires recalibration". This is the same property at the
    `pi` threshold layer, and it is *stronger* here, because the classifier's
    scorer is at least a model you can name and pin — a `pi` threshold is
    bound to a vendor-hosted scoring model the config cannot name at all
    (Claims 2, 6, 8). **Claim 4** — the flagship detector was archived and
    unmaintained, and switching required label validation plus recalibration:
    the same "your scorer can change under you" hazard, already documented for
    a pinned model, and unaddressable for `pi`. (Verified: read Claims 4 and 5
    and their quotes in #1288 directly.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) **Claim 1**
    (the weighted-average aggregation and test-case `threshold` semantics that
    sit above every per-assert default, including this one). (Verified: read
    Claim 1 in #1287 directly.)
  - `source-notes/docs-promptfoo-model-graded-closedqa.md` (#1483) **Claim 1**
    — the binary-verdict sibling, and the note that the family members
    carrying a *graded* surface are `g-eval` (0-1, default `0.7`) and
    `llm-rubric` (a `pass` field plus score). `pi` is a **third** graded-surface
    member with a different shape again: a continuous 0-1 score with a `0.5`
    default and *no* reason field, so it has neither a verdict letter to parse
    nor a rationale to read. That makes the closedqa parse-failure class
    (its Claim 2) structurally impossible here and replaces it with the
    opposite problem — nothing to parse *and* nothing to explain. (Verified:
    read Claims 1 and 2 in #1483 directly.)

- **Contradicts**: **None identified, and no contradiction issue filed.** Three
  candidates were examined and each fails the MINER.md §4a bar, for
  different reasons — recorded here so the Assayer and the resolver can see
  the checks rather than infer them:
  - **The determinism claim vs the corpus's measured judge variance**
    (`blog-promptfoo-asr-not-portable-metric.md` #261 Claim 8, 14-point ASR
    gap between two equally-accurate judges; Claim 11, rubric specificity as
    the variance control). This is *not* filed. #261's findings are about LLM
    judges; `pi` is explicitly not an LLM judge, and its determinism claim is
    about run-to-run stability, not about calibration. Per §4a's "claims
    differ only in *context*," these are different properties of different
    mechanisms, and the guide needs both, not either/or. The genuine tension
    is with the *guide's* framing rather than with a source claim, and it is
    recorded in Claim 3's assessment: a zero-variance score with an uncalibrated
    bias fails the same rows forever, so determinism buys replayability, not
    correctness. No verdict is needed because no two sources disagree.
  - **The absence of a `not-` section vs #1287 Claim 10** ("Every test type can
    be negated by prepending `not-`"). Not filed: this is **page silence**,
    not a documented refusal, and the identical observation was already
    recorded for `max-score` in `docs-promptfoo-max-score.md` (#1472) **Claim
    9**, which reached the same conclusion and also declined to file. Two
    per-type pages without a negation section, three with one, strengthens the
    per-type-read doctrine rather than creating a conflict. Recorded under
    Claim 6 and the Extends line for #1472.
  - **The absence of any grader pin vs #1305 Claim 1** (the family-wide
    "nothing is pinned by default"). Not filed, and this is the closest call.
    It fails the bar for the same reason the `factuality` page's silence did:
    a missing override surface is an *absence*, so it cannot "materially
    oppose" a claim about what a default *is* — and the *default* here is
    named (a Pi Labs scorer, per #1289 Claim 1's catalogue row and this page's
    Prerequisites). The tension is with the guide's *rule*, not with a
    source claim, and the fix is a guide edit (a third state: vendor-named,
    model-opaque), not a contradiction verdict. Filed as Guide Impact
    instead. Duplicate check re-run: `gh issue list --label contradiction
    --state open` returns #1486, #1462, #1461, #1408, #1352, #1338, #1322,
    #1307, #1150 — of the promptfoo-related ones, **#1352** (g-eval's dated
    default judge pin vs the hub's ambient claim) and **#1307** (missing-trace
    semantics) are the only ones on this page's subject matter, and neither
    covers `pi`. #1352 in particular is about whether a per-type page's stated
    default is a pin; `pi` states a vendor, not a model, and does not touch
    the built-in grading provider at all, so it neither extends nor resolves
    #1352. `CONTRADICTIONS.md` has no open `C-NNN` entries. No new issue.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — closes
    that note's explicitly-open "pi ... not followed" gap, carrying the delta
    (the non-LLM-judge topology, the separate credential, the determinism
    claim, the 0.5 default, the absent override/negation surfaces, the
    interactive calibration loop). The shared material (grader-override
    precedence, `rubricPrompt` reach, `showThinking`, temperature knobs) is
    cited above rather than re-extracted — and its *absence* here is itself
    the finding (Claim 6).
  - `source-notes/docs-promptfoo-max-score.md` (#1472) **Claim 9** — the
    precedent for handling a missing `not-` section as documented page silence
    rather than as opposition to the hub's blanket negation rule. `pi` is the
    second instance, and the sharper one (an external vendor changes the trust
    boundary, per #1471 Claim 9's own routing argument). **Claim 3** — the
    continuous 0-1 scorer inherits the mixed-scale-average hazard: `pi` scores
    are not binary, so a `max-score` or test-case aggregate over a `pi` assert
    blends them with binary siblings on one scale. (Verified: read Claims 3, 5
    and 9 in #1472 directly.)
  - `source-notes/docs-promptfoo-factuality.md` — **Claim 4** (cited by claim
    number; read and verified) records that the factuality page names *no*
    default judge model, which is the discriminator a #1352 resolver needs.
    This page supplies the third case in that taxonomy: a per-type page that
    names a *vendor* and a credential rather than a model — neither a pin
    (#1352 Side B shape) nor silence (factuality), and not on the built-in
    grading provider at all. (Verified: read Claim 4 in
    `docs-promptfoo-factuality.md` directly.)
  - `source-notes/docs-promptfoo-model-graded-context-recall.md` (#1332)
    **Claim 3** — the required-field contract `value` + `context`, and the
    silent-degradation risk when a config swaps one RAG assert type for
    another. This page is the swap *target*: `pi` has no `context` slot, so a
    ported RAG gate grades the completion in isolation and keeps reporting
    normal verdicts (Claim 9). **Claim 2** — the documented `0` default, one
    more entry for the per-type-defaults inventory (Claim 5). (Verified: read
    Claims 2 and 3 in #1332 directly.)
  - `source-notes/docs-promptfoo-model-graded-context-faithfulness.md` (#1320)
    **Claim 2** — the documented `threshold: 0` default; the third entry for
    the same inventory, and the one that shows what a `pi` gate does *not* need
    to worry about. (Verified: read Claim 2 in #1320 directly.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` (#261) **Claim 8**
    and **Claim 11** — the empirical frame this page's headline claim has to
    answer to. Claim 8 supplies the reason determinism is not calibration
    (14 points of ASR from TPR/FPR distribution alone, at identical accuracy);
    Claim 11's rubric-specificity finding is *unavailable* as a control here
    because there is no second judge for a rubric to converge across
    (Claim 1(c)). (Verified: read Claims 8 and 11 and their worked arithmetic
    in #261 directly.)
  - `source-notes/docs-promptfoo-answer-relevance.md` (#1319) **Claim 3** —
    from the family-defaults inventory cited in Claim 5: a per-type page that
    states *no* default at all, which is a third distinct outcome alongside
    `0`, `0.5`, and the score-blind pass. Cited for the inventory only; that
    claim was not re-read in this extraction, so treat it as carried from
    `docs-promptfoo-g-eval.md`'s and `docs-promptfoo-conversation-relevance.md`'s
    verified references to it rather than as re-verified here.

- **Novel**: What is new to the corpus, in rough order of value:
  1. **A third grading topology** (Claim 1) — neither the ambient
     credential-selected LLM judge (#1305 Claim 1) nor an agent grader (#1305
     Claim 11): a dedicated, externally-hosted, pretrained scoring model
     reached through a vendor SDK. The model's first non-LLM-judge member in
     the family, and the first assert type where the whole scratchpad-misparse
     failure class is structurally absent.
  2. **A determinism claim in a model-graded assert, stated flatly and with no
     evidence** (Claim 3) — the only assert in the corpus that promises a
     stable score, and the promise is a vendor design statement with no
     calibration data, no agreement figure, no repeat-run example, and no
     named model version, deferred to an off-site document.
  3. **Determinism traded for auditability, explicitly** (Claim 4) — "highly
     accurate numeric scoring without providing detailed reasoning", the first
     corpus statement that a gate score may arrive with no rationale by design.
  4. **A grader that is vendor-named and model-opaque** (Claims 2, 6) — a third
     state for the guide's pinning rule, between "ambient" (config does not
     choose it) and "pinned" (config names the model). Plus the egress fact
     that the full `llm_input`/`llm_output` pair crosses a network hop to a
     non-provider vendor with no documented self-hosted, proxy, retention, or
     redaction route.
  5. **The absence of `provider:`, `rubricPrompt`, and `not-` on a model-graded
     per-type page** (Claim 6) — the first per-type page with no negation
     section at all, verified by full read, which makes the guide's negation
     and multilingual-override rules unsatisfiable for this type.
  6. **Threshold calibration as an interactive, non-reproducible,
     off-platform step** (Claim 8) — a new class of non-reproducible eval
     artifact, at the *threshold* layer rather than the judge layer, which
     composes badly with the determinism claim: a frozen score against an
     unjustified threshold.
  7. **A second, cross-page-corroborated `0.5` default** (Claim 5) — the only
     default threshold in the family documented on two independent promptfoo
     pages, and the fourth distinct outcome in the per-type-defaults inventory.
  8. **A documented, vendor-endorsed config-file path for a third-party key**
     (Claim 7) — a concrete, small Ch06 item plus a secret-scanner
     deliverable (`WITHPI_API_KEY`).
  9. **The one config a reader will copy pins the target, not the grader**
     (Claim 10) — the concrete config-reading trap behind the pinning finding,
     with the counterweight that this example *does* set explicit thresholds on
     both asserts, so the vendor's own `pi` gate is a real gate.

## Guide Impact

- **Chapter 05 — "The judge behind a model-graded assertion is unpinned by
  default" / judge-pinning rule: add a third state, do not extend the rule
  silently.** The rule currently reads "Pin the judge explicitly (`--grader`,
  `defaultTest.options.provider`, or the assertion's own `provider:`) and grep
  every level for assertion-level shorthand overrides" [source:
  docs-promptfoo-model-graded-metrics, Claim 1/2], and the guide presents the
  ambient judge as a *sloppiness* to fix by pinning. `pi` breaks both halves:
  (a) it is not ambient — the grader is named by which `WITHPI_API_KEY` you
  provisioned, so the add-a-key-and-the-grader-swaps hazard does not apply; and
  (b) it is not pinnable — no `provider:` override is documented for this type,
  and no promptfoo surface (including `/docs/providers/withpi`, which 404s)
  names the scoring model the key resolves to [source:
  docs-promptfoo-pi-scorer, Claims 2, 6]. Recommend adding
  **"vendor-named, model-opaque"** as a named third state, with the per-assert
  read required, and with the concrete grep caveat: **in a `pi` config every
  model ID under a `providers:` key is the target, never the grader** [source:
  docs-promptfoo-pi-scorer, Claim 10]. If the guide's rule stays as written
  without the third state, a reader will believe the example config pins its
  judge.
- **Chapter 05 — "A gate that cannot fail is not a gate" / the negative-control
  rule: `pi` is on the *can-fail* side, so the note is a positive, not a new
  table row.** Unlike the `0`-default members, a bare `assert: - type: pi`
  gates at the documented `0.5` default [source: docs-promptfoo-pi-scorer,
  Claim 5], and the vendor's own only complete example sets explicit
  `threshold: 0.7` / `0.8` on both of its asserts [source:
  docs-promptfoo-pi-scorer, Claim 10]. What the table *should* gain is the
  inverse caveat: the same section's closing rule already requires a
  deliberately-wrong negative control, and for `pi` that control is the *only*
  mechanism that can detect a miscalibrated grader, because the score cannot
  move and nothing in the report explains it [source: docs-promptfoo-pi-scorer,
  Claims 3, 4]. Also extend the closing paragraph's per-type-defaults
  paragraph with the fourth inventory value — the defaults now read `0`
  (context-faithfulness #1320, context-recall #1332), `0.5`
  (conversation-relevance #1334, and `pi` on two pages), `0.7` (g-eval #1349),
  and unstated (answer-relevance #1319, max-score #1472, llm-rubric #1305) —
  and note that the `0.5` for `pi` is the only one corroborated on two
  independent vendor pages, which is evidence the per-type read is mandatory
  and not merely tidy.
- **Chapter 05 — judge-calibration / hermetic-replay material: add a
  threshold-layer reproducibility rule.** The guide's existing hermeticity
  rules cover the *judge* (ambient provider, live web-search graders). `pi`
  adds an artifact one layer down: the only documented procedure for choosing
  the threshold is an interactive loop in a separate web product — "Find the
  optimal threshold values for your use case" in the Pi Labs Copilot — with no
  documented API, export, or versioned output, so a `threshold: 0.8` in the
  config has no recorded provenance [source: docs-promptfoo-pi-scorer,
  Claim 8]. The `0.8` in the page's own Threshold Support block is an
  illustrative value, not a calibrated one, and it is the number a reader is
  most likely to copy. Recommend: **record the calibration set next to every
  `pi` threshold**, treat the Copilot session as an offline design step, and
  re-calibrate on the same schedule the guide already requires for judge
  changes. Frame the composition risk explicitly, because it is the part that
  surprises: a frozen score compared against an unjustified threshold is a gate
  that is perfectly stable and completely unfounded.
- **Chapter 05 — the "can your gate explain itself?" / audit-trail rule: name
  the `pi` tradeoff rather than leaving it implicit.** For every other
  model-graded type the guide can point at a rationale, a rendered prompt, or a
  positive channel marker (#1471 Claim 4's `renderedGradingPromptAudio`
  precedent). `pi` is documented to return a number "without providing
  detailed reasoning", and the page documents no metadata marker or
  decomposition for the type [source: docs-promptfoo-pi-scorer, Claim 4]. The
  compensating controls are therefore *process*, not telemetry: a negative
  control per gate, a recorded calibration set, and a re-calibration schedule.
  Do not let the guide imply the score is inspectable for this type, and do
  not carry the #1305 Claim 5/6 `showThinking` guidance into it — there is no
  thinking text to strip, and no `provider:` block to put it on.
- **Chapter 06 (Security and Trust) — the egress-boundary section: add `pi` as
  a second, structurally different kind of third party in the request path.**
  The section's existing rule is about a guardrail *inside* the request path and
  is minimization-first: enumerate the fields the third party needs, allowlist
  the rest [source: docs-litellm-generic-guardrail-api, Claims 6-7]. `pi` is
  the mirror case: the third party is *outside* the request path and receives
  the eval's full `llm_input` and `llm_output` — the prompt and the completion
  — with a single natural-language criterion, and the page documents no
  retention policy, no region, no redaction, and no self-hosted or proxied
  route [source: docs-promptfoo-pi-scorer, Claims 2, 9]. Unlike an ambient LLM
  judge, which is a provider the team already contracts with and *can* route
  through its own gateway (the documented LiteLLM grader-reuse pattern, #1349
  Claim 8), there is no documented way to keep `pi` traffic inside the
  perimeter. Recommend the section state the boundary and the two open
  questions a security review must answer before adopting it: what the vendor
  retains, and whether any part of it is used for training.
- **Chapter 06 — secret-management checklist: add `WITHPI_API_KEY` with a
  named constraint.** The page documents the env var *and* a config-file
  `env:` block as co-equal options, with no statement about the config file's
  protection or templating [source: docs-promptfoo-pi-scorer, Claim 7]. The
  rule to add: keep the env var (the page lists it first), treat the config
  file as documented-but-worse, and add `WITHPI_API_KEY` to the runner's
  secret-scanner list and the CI secret inventory — with the asymmetry noted
  that unlike an ambient judge key, this one has exactly one purpose, so its
  absence is not something a credential swap papers over (the page says you
  **must** set it and does not say what a `pi` assert does without it).
- **Chapter 06 — the "must not leak PII" negated-gate pattern: add a caveat
  rather than a new rule.** The guide's negated model-graded gates lean on the
  vendor's fail-closed inversion sentences (`not-trajectory:goal-success` #1305
  Claim 4, `not-g-eval` #1349 Claim 5, `not-llm-rubric` #1471 Claim 7). The
  `pi` page has no negation section and no failure semantics at all, so a
  `not-pi` gate has no documented verdict behavior for a transport failure —
  and no documented meaning for inverting a 0-1 score [source:
  docs-promptfoo-pi-scorer, Claim 6]. Recommend the guide's negation
  material gain one sentence: *per-type read, and treat a missing fail-closed
  sentence as a vendor question, not an implied pass* — the inference
  `docs-promptfoo-llm-rubric` already records, now with two per-type pages
  (max-score #1472 Claim 9, and `pi`) lacking the sentence.
- **Chapter 05 — cost/dependency tiering: no numbers available, so say so.**
  The guide's model-graded cost ladder (#1305 Guide Impact → cost tiering)
  reads "model-graded asserts consume an extra inference call per verdict."
  That framing is imprecise for `pi` in one direction (no prompt to send, per
  Claim 1) and incomplete in another (a hosted vendor call per verdict, whose
  price the page does not state and which is not covered by any provider
  contract the team already holds). Recommend adding `pi` to the tier list
  with an explicit "no documented cost figure" rather than inheriting the
  "extra inference call" wording, and noting that the vendor itself steers the
  decision with "you may want to experiment with both to determine which best
  suits your specific evaluation needs" — i.e. the vendor's position is that
  the topology choice is a per-suite experiment, which is a weaker guarantee
  than a documented cost or failure contract.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/pi/),
  then re-fetched as raw HTML to verify quotes and reconstruct the five code
  blocks from the page's Prism `token-line` markup (the plain-text fetch
  collapses YAML indentation; token content is unchanged, and the reconstructed
  blocks are what appear above). Footer reads "Last updated on **Sep 28, 2026**
  by **Aniket Kumar**" — page is undated, so `date_published` carries the
  last-updated date, the same convention as the sibling notes
  (#1287/#1289/#1305/#1349/#1471). Every quote above was checked
  character-for-character against the fetched rendered content. The
  `llm_input` / `llm_output` / `withpi` / `WITHPI_API_KEY` names are the page's
  inline code spans and are reproduced as such.
- **Second page read (in addition to the source_url)**: the `### Pi` stub on
  https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/,
  which is the retained pointer for the `pi` type from the deterministic page
  (the boundary sentence that introduces it is quoted in Concrete Artifacts).
  It corroborates the `0.5` default from a second page, characterizes the
  grader as a "preference scoring model" (a wording the model-graded page does
  not use), and says "You can use multiple Pi assertions to evaluate different
  aspects". Cited by URL throughout; not a separate source note.
- **Linked pages that could NOT be followed**: the page's three Pi Labs
  outbound targets — `https://docs.withpi.ai` (the "more options,
  configuration, and calibration details" pointer that carries the entire
  substance of the determinism and calibration claims), `https://build.withpi.ai`
  (the Copilot named in "Metrics Brainstorming"), and
  `https://build.withpi.ai/account/keys` (the key console named in
  "Prerequisites") — were unreachable from the mining runner: DNS resolution
  failed for both `docs.withpi.ai` and `build.withpi.ai` while the promptfoo
  host resolved normally, so this is an egress restriction on the runner, not
  evidence that those pages are down. Consequence stated plainly: **the
  determinism claim (Claim 3) and the accuracy claim (Claim 4) could not be
  corroborated or refuted from the vendor's own calibration material**, and
  they are graded `anecdotal` for that reason. The in-corpus links
  (`llm-rubric` #1471, the model-graded hub #1305) were not re-followed; both
  are already mined at claim level and are cross-referenced rather than
  re-extracted. `/docs/providers/withpi` was checked and returns HTTP 404, with
  no `withpi` entry on the providers index — recorded as a checked absence
  supporting Claim 6.
- **Triage key-question resolutions** (both Prospector comments read as
  UNTRUSTED input; every item re-verified against the page, and neither
  comment's wording was carried into a quote):
  1. *"Is the 'judge is ambient-credential-selected' finding still applicable,
     or inapplicable here?"* — **Neither cleanly.** The ambient *swap* hazard
     does not apply (the grader is tied to a deliberately provisioned
     `WITHPI_API_KEY`, Claim 2), and the *pin* is not available either (no
     `provider:` override documented, and the scoring model is named nowhere,
     Claim 6). Recorded as a third state, "vendor-named, model-opaque", and as
     a guide-impact change to the pinning rule. I did not extend or resolve
     #1352: that contradiction is about whether a per-type page's stated
     default is a pin on the *built-in grading provider*, and `pi` does not
     use the built-in grading provider.
  2. *"Extract whether the 0.5 default confirms the per-type-defaults pattern
     as a stable rule rather than an anomaly."* — **Yes**, and strengthened:
     with `pi` the inventory is four distinct outcomes across the family
     (`0`, `0.5` twice, `0.7`, unstated, plus the score-blind pass), and
     `pi`'s `0.5` is the only default documented on two independent vendor
     pages (Claim 5).
  3. *"Is 'always the same score' a measured property or a vendor design
     assertion?"* — **A vendor design assertion**, explicitly. No calibration
     data, no agreement figure, no worked repeat-run example, no model
     version, and the substance deferred to an unreachable off-site document.
     Recorded as Claim 3 at `anecdotal`, with the variance-vs-calibration
     distinction argued explicitly rather than assumed (Claim 3's assessment).
  4. *"What happens to the gate when the Pi API is unreachable,
     rate-limited, or the key is absent?"* — **Not documented anywhere on the
     page.** I did not infer an answer. The page says you **must** set the key
     and documents no behavior for its absence, no timeout, no retry, and no
     fail-closed or fail-open semantics for a transport failure — a notable
     contrast with the three family pages that *do* carry an explicit
     fail-closed inversion sentence (#1305 Claim 4, #1349 Claim 5, #1471
     Claim 7). Recorded as part of Claim 6's silence, not as a claim that the
     gate fails open.
  5. *"Extract the third-party dependency and secret surface."* — Claim 2
     (egress and credential lifecycle), Claim 7 (the config-file key path),
     Claim 9 (the exact payload that crosses the boundary), and the Guide
     Impact entries for Ch06.
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; all 10 candidates cited or dismissed by name — candidates
  are suggestions only, and no corroboration was invented to use one):
  - `docs-promptfoo-classifier-grading.md` — **cited** (Corroborates, Claims 4
    and 5: scorer-bound thresholds, and the archived-detector
    recalibration hazard).
  - `blog-promptfoo-owasp-red-teaming.md` — OWASP red-team methodology and CI
    integration of red-teaming; no eval-grader topology, credential, or
    threshold-calibration semantics; **dismissed**.
  - `docs-litellm-batches-api.md` — LiteLLM batch/rate-limit accounting; the
    only lexical overlap is "API key" and a cost/limits frame, and the note
    supplies no per-key cost or limit figure to use; **dismissed**.
  - `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge *alerting* for incident
    triage; no eval-assert config surface and no grader-credential
    lifecycle; **dismissed**.
  - `blog-promptfoo-red-team-claude.md` — per-model red-team plugin strategy;
    uses rubric asserts as tools but carries no judge-topology, pinning, or
    threshold-provenance semantics (and #1305 already sourced the rubric
    semantics from it, so re-citing would be circular); **dismissed**.
  - `docs-promptfoo-llm-rubric.md` — **cited heavily** (Corroborates, Claims 4,
    5, 7; the contrast case the page's own admonition names).
  - `docs-promptfoo-model-graded-closedqa.md` — **cited** (Corroborates, Claims
    1 and 2: the binary-verdict sibling and the third graded-surface member).
  - `docs-promptfoo-factuality.md` — **cited** (Extends, Claim 4: the
    silence-vs-named-default taxonomy a #1352 resolver needs, now with a third
    case).
  - `docs-google-sre-team-lifecycles.md` — Google SRE workbook chapter on team
    org design and SLO adoption; no LLM-eval content; **dismissed**.
  - `docs-promptfoo-assertions-metrics.md` — **cited** (Corroborates, Claim 1:
    the aggregation layer above every per-assert default, and the reason the
    `0.5` is not the whole gate).
  - Additionally found by searching `source-notes/` per MINER.md §4 (not in the
    candidate list as written) and all **cited**:
    `docs-promptfoo-model-graded-metrics.md` (Corroborates Claims 1 and 5;
    Extends — the hub's open "pi not followed" gap), `docs-promptfoo-g-eval.md`
    (Corroborates Claims 3 and 8), `docs-promptfoo-deterministic-metrics.md`
    (Corroborates Claim 1 — the only prior corpus mention of `pi` by name),
    `docs-promptfoo-conversation-relevance.md` (Corroborates Claim 2),
    `docs-promptfoo-max-score.md` (Extends Claims 3 and 9 — the
    missing-negation-section precedent),
    `docs-promptfoo-model-graded-context-recall.md` (Extends Claims 2 and 3),
    `docs-promptfoo-model-graded-context-faithfulness.md` (Extends Claim 2),
    `blog-promptfoo-asr-not-portable-metric.md` (Extends Claims 8 and 11), and
    `docs-promptfoo-answer-relevance.md` (Extends Claim 3, inventory only —
    see the re-verification caveat there).
- **Cross-ref verification (§4b)**: every cited claim number was located and
  read in the cited note before it was written, and its content checked
  against what it is cited for — #1289 Claim 1, #1305 Claims 1 and 5, #1471
  Claims 4/5/7, #1334 Claim 2, #1349 Claims 3 and 8, #1288 Claims 4 and 5,
  #1287 Claim 1, #1483 Claims 1 and 2, #1472 Claims 3/5/9, #1332 Claims 2 and
  3, #1320 Claim 2, #261 Claims 8 and 11, and
  `docs-promptfoo-factuality.md` Claim 4. No claim numbers were invented and no
  quotes are attributed to any other note. Source-note issue numbers were read
  from each cited note's frontmatter `issue:` field, not inferred: #1289,
  #1305, #1471, #1334, #1349, #1288, #1287, #1483, #1472, #1332, #1320, #261,
  #1319. One explicit limit: `docs-promptfoo-answer-relevance.md` **Claim 3**
  is cited from the family-defaults inventory and was **not re-read in this
  extraction** — it is carried from the verified references to it in the
  g-eval and conversation-relevance notes and should be treated as
  carried-over-and-consistent, not re-verified here. A web search was also
  run to look for public Pi Labs calibration material; the only hit of
  substance was a conference talk (David Karam, Pi Labs, ai.engineer), which
  is referenced in Claim 3's assessment for its *mechanism* claim and is
  explicitly **not** quoted, not part of the extracted source, and not
  verbatim-verified.
- **No contradiction issue filed**, per MINER.md §4a, with the three candidates
  and the reason each fails the bar recorded under **Contradicts** above. The
  duplicate check was re-run against open `contradiction`-labeled issues:
  #1486, #1462, #1461, #1408, #1352, #1338, #1322, #1307, #1150 — of these,
  only #1352 and #1307 are promptfoo-related and on this page's subject
  matter, and neither covers `pi`. `CONTRADICTIONS.md` has no open `C-NNN`
  entries. Note that this page is *thin* rather than internally inconsistent:
  the summary list and the mechanism list state different strengths of the
  determinism property (Claim 3), which is a wording gap I recorded rather
  than a self-contradiction, because the page never claims the two are
  equivalent and never claims either is measured.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1288, #1289, #1305, #1320, #1332, #1334, #1349, #1471, #1472,
  #1483): the mechanism, default, credential, and threshold claims are settled
  for product behavior and directly checkable against an installed CLI, but
  this is thin vendor documentation whose two performance claims carry no
  measurement, whose calibration material is off-site and unreachable, and
  whose most consequential findings are *absences* (no override, no negation,
  no failure semantics, no cost, no retention). Marked `emerging` on the
  strength of the body of evidence, not on the strength of the page's
  confidence in itself.
- `registry/sources.json` and `registry/claims-index.json` were **not**
  edited — they are derived indexes rebuilt by `scripts/build_registry.py` and
  `scripts/build_claims_index.py` after merge. `miner-related-notes.md` was
  read as required and is **not** committed.
