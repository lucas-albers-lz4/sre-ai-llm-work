---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/select-best
source_type: docs
title: "Promptfoo Configuration: Model-Graded — Select Best"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-29
date_extracted: 2026-09-29
last_checked: 2026-09-29
status: current
confidence_overall: emerging
issue: "#1497"
---

# Promptfoo Configuration: Model-Graded — Select Best

> The per-type vendor reference for promptfoo's `select-best` assertion — the
> page that closes the explicit "`select-best` was not followed" gap left by
> both the model-graded hub note (#1305) and the sibling `max-score` note
> (#1472), and that gives the corpus its **primary-source contract** for the
> judged member of the comparison-assert pair. Its load-bearing findings: the
> assertion's pass column is a **ranking, not a verdict** ("Returns `pass=true`
> for the winning output and `pass=false` for others" — so in the page's own
> three-prompt example two of three outputs are red *by construction*); it
> documents **no `threshold`, weight, or aggregation dial at all**, so unlike
> `max-score` there is no setting that converts it into a quality bar; its
> multi-candidate precondition is stated in prose but **not enforced**, leaving
> the single-candidate case undocumented; the judge's expected response is a
> **bare integer index** ("responding with its index (0 to
> `{{ outputs | length - 1 }}`)"), which is the mechanism behind the hub's
> already-recorded "`select-best` can read a scratchpad number as the winning
> index" (#1305 Claim 5) and a fourth distinct `rubricPrompt` variable
> vocabulary in this family (data point for contradiction **#1486**); and — new
> to the corpus — the page documents a **grader-restore failure mode under
> resume**: "Resuming with redacted grader credentials requires a matching
> provider ID and nonsecret configuration."

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Select Best"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `select-best` behavior — authoritative for *what promptfoo does*
  with a given config (the checker's four-step sequence, the per-output pass
  flags, the multi-candidate precondition, the grader-override surfaces, the
  `rubricPrompt` variable set and verdict encoding), but vendor-positioned:
  the page carries **no** measured gate-failure rate, judge-agreement figure,
  cost figure, latency figure, or calibration data, and there is no independent
  practitioner validation. Everything below is checkable against an installed
  CLI. The hazards (Claim 1, Claim 3) are recorded as **documented product
  behavior**, not as measured failure rates. Per the sibling note's caveat
  (#1472), this is authoritative for *what the tool does*, never for *whether
  the pattern works in production*.
- **Scope**: A single self-contained reference page — intro paragraph, How to
  use it, How it works (the four-step checker sequence), Example Configuration,
  Overriding the Grader, Customizing the Prompt, Further reading. It is the
  per-type deep-dive on the `select-best` member of the comparison-assert
  family that `docs-promptfoo-model-graded-metrics.md` (#1305) catalogued at
  claim level only and that `docs-promptfoo-max-score.md` (#1472) explicitly
  recorded as *not followed*. This page therefore carries the *delta* (pass
  semantics, precondition, `rubricPrompt` index contract, resume caveat), not
  a re-extraction of the model-graded framing. Does **NOT** cover the
  `max-score` page, any measured property of judge accuracy, or what the page
  never documents (the single-candidate case, tie-breaking, cost, and the
  `not-` negated form — recorded as open questions in Extraction Notes).
- **Last updated**: the page footer reads "Last updated on **Sep 29, 2026** by
  **dawn**" — same-day as extraction. As the triage noted, a Docusaurus
  footer stamp is a build/render date and is *not* evidence of a content
  change; the page carries no dated material of its own, so `date_published`
  follows the sibling per-type convention (#1349/#1319/#1320/#1332/#1334/
  #1472/#1483) of carrying the last-updated stamp.
- **Taxonomy note**: like `max-score`, this page is filed under "Model-graded
  metrics" in the sidebar and genuinely does make a judge call, so unlike its
  sibling there is **no** nav-grouping artifact here. `select-best` is on the
  judged side of the vendor's own deterministic/judged line in both the nav and
  the prose.

## Extracted Claims

### Claim 1: The `select-best` pass column is a ranking, not a verdict — "Returns `pass=true` for the winning output and `pass=false` for others" means every non-winner is red **by construction**, so a 3-prompt row is 1 green / 2 red regardless of whether any output was actually good
- **Evidence**: The "How it works" numbered sequence (step 4), read together
  with the "Example Configuration" block, which supplies exactly three prompt
  variations against a single provider.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Returns pass=true for the winning output and pass=false for
  others" (step 4 of the "How it works" list, quoted from
  https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/select-best)
- **Our assessment**: The single most consequential sentence on the page, and
  it is nearly **character-identical** to the sibling `max-score` page's step
  ("Returns pass=true for the highest scoring output, pass=false for
  others"). Two vendor pages, same comparison-assert family, same pass-column
  shape, one line apart — that is now strong enough to state as a *family
  pattern* rather than two coincidences: **promptfoo's selector asserts emit a
  ranking in the pass column.** The arithmetic is worth writing out, because it
  is the thing a CI reviewer will get wrong. In the page's own example
  (`prompts:` × 3, `providers:` × 1, two test cases), each test case produces
  three candidate outputs; one gets `pass=true`, the other two get
  `pass=false`. A reader who greps the results table for red rows finds a
  **67% failure rate on a suite that is entirely green by design**, and a
  reader who counts "how many outputs passed" is counting an argmax, not a
  quality verdict. Worse, and unlike the deterministic traps already in the
  corpus, this asymmetry is **not** a config value that could have been set
  differently — it is the assertion's semantics. `select-best`'s `pass` column
  answers "which of these won?", and no config change can make it answer "was
  any of these good?" (see Claim 3). Cross-output comparability is the *point*
  of the assert ("This is useful for comparing different prompt or model
  variations to determine which produces the best result"), so the honest
  reading is: this is a **selector with a ranking printed into the pass
  column**, and the guide's rule should be the same one #1472 derived for
  `max-score` — *a selector's green is a ranking, never evidence that an output
  was good* — now with two documented instances instead of one.

### Claim 2: The page's precondition is stated in prose and **not enforced** — "This assertion requires multiple prompts or providers to generate different outputs to compare" — and the page documents no error, warning, or degenerate-case behavior when only one candidate exists
- **Evidence**: The one-sentence note immediately under the "How to use it"
  config block; contrasted with the sibling `max-score` page's documented
  fail-closed config error (see Cross-References → Corroborates, #1472 Claim 9).
  The page contains no "Edge cases" section at all — `max-score` has four
  bullets, `select-best` has none.
- **Confidence**: settled (the requirement is stated); the single-candidate
  behavior is **page silence**, recorded as an open question rather than
  inferred
- **Quote**: "Note: This assertion requires multiple prompts or providers to
  generate different outputs to compare."
- **Our assessment**: The most SRE-relevant sentence on the page, and the
  triage asked for exactly this. What the vendor states is the *requirement*;
  what the page never states is the *consequence of violating it* — so the
  failure mode is undocumented, and undocumented preconditions in a CI gate are
  where silent-green lives. The failure shape is fully determined by Claim 1:
  with one candidate, the argmax has exactly one possible answer, so **every
  row is `pass=true` by construction** — a gate that reports 100% green
  forever, on a suite the vendor simultaneously says cannot work. I am *not*
  asserting promptfoo actually behaves this way (that needs a CLI probe; see
  Extraction Notes); what is documented is that the page promises nothing here
  and ships no guard. The asymmetry with the sibling is the finding: `max-score`
  states a structurally similar requirement as a hard error — "No other
  assertions: Error - max-score requires at least one assertion to aggregate"
  (#1472 Claim 9) — while `select-best` states its structurally similar
  requirement as a prose note, in a page with no edge-case list at all. **Same
  comparison family, same class of precondition, opposite enforcement.** A
  guide rule that has to say "read *this* assert type's own page for its
  precondition and check it yourself" is exactly the per-type-read doctrine
  #1349 established; this page is a fresh instance of why.

### Claim 3: `select-best` documents **no** `threshold`, weight, method, or any other dial — `value:` is the criterion string and nothing else, so unlike `max-score` there is no configuration that turns the selector into a quality bar
- **Evidence**: The "How to use it" config (`value:` is a criterion sentence,
  not a number), the "Customizing the Prompt" section (the only other knob,
  and it changes the prompt, not the verdict), and the **absence** of any
  `threshold` / `weights` / `method` field anywhere on the page. Contrast the
  sibling's documented schema: `method: average | sum`, `threshold: 0.7`,
  and a type-keyed `weights` map (#1472 Claims 3/4/5, all reproduced in that
  note's Concrete Artifacts).
- **Confidence**: settled (documented product behavior); this is a
  *page-absence* finding recorded from the full page read, not an inference
  about undocumented behavior
- **Quote**: (no direct quote; see paraphrase in Our assessment — the page
  contains no `threshold`, `weight`, `method`, or `weights` string; the
  only two configurable surfaces on the page are the criterion `value:` and
  `rubricPrompt`, both quoted verbatim in Concrete Artifacts below)
- **Our assessment**: This is what turns Claim 1 from "a ranking you must not
  misread" into "a gate with no off switch," and it is the finding that should
  change guide text. `max-score` at least has a documented dial: set a
  `threshold` and the assert starts failing on quality (with the mix-scale
  caveats #1472 documents). `select-best` has **nothing** — no threshold, no
  aggregation, no minimum margin between winner and runner-up. There is no
  version of this config where "the winner was mediocre" turns a row red. The
  only way to gate quality on `select-best` is to put a *second* assert
  alongside it (the `max-score`+`llm-rubric` composition, or a deterministic
  assert) and treat `select-best`'s column as an annotation. Combined with
  Claim 1 and Claim 2, the full picture is a three-part statement the guide can
  make in one line: **`select-best` cannot fail on quality, has no dial to
  make it able to, and states no behavior for the configuration where its
  precondition is unmet.** That belongs in Ch05's "A gate that cannot fail is
  not a gate" table — with the important structural difference from the other
  rows there, which the Smith must preserve: the six existing rows are *config
  values* that disable a check, and this is an *assert type* that is a selector
  with no bar. The fix is "do not read its pass column as a verdict" plus
  "gate on a different assert," not "change this value."

### Claim 4: The judge's expected response is a **bare integer index** — "Choose the best output by responding with its index (0 to `{{ outputs | length - 1 }}`)" — which is the missing causal mechanism behind the hub's "`select-best` can read a scratchpad number as the winning index", and makes this assert the family's narrowest, most collision-prone verdict encoding
- **Evidence**: The `rubricPrompt` block in "Customizing the Prompt"
  (reproduced verbatim in Concrete Artifacts), read against the hub's
  already-recorded scratchpad-misparse list (#1305 Claim 5, verified at
  `source-notes/docs-promptfoo-model-graded-metrics.md:137`).
- **Confidence**: settled (the encoding is stated verbatim in the vendor's own
  default prompt); the collision reasoning is the Miner's
- **Quote**: "Choose the best output by responding with its index (0 to
  {{ outputs | length - 1 }})."
- **Our assessment**: This confirms, from the primary source, the causality the
  hub note could only assert second-hand. The hub warned that "`select-best`
  can read a scratchpad number as the winning index" but did not say *why* —
  and the why is that **the expected verdict is itself a number**. Compare the
  encodings across this family as the corpus has now documented them:
  `llm-rubric` expects JSON `{"reason", "pass", "score"}`; `closedqa` expects a
  `Y`/`N` **suffix** and fails a response ending in neither (#1483 Claims 1-2);
  `factuality` accepts a bare letter `"A"`/`"(A)"` **or** a JSON object (#1348
  Claim 5); `conversation-relevance` expects JSON with `verdict`/`reason`;
  `select-best` expects **a bare integer, positionally**. That last one is the
  most fragile shape in the set, for a reason specific to thinking models: the
  set of *wrong* strings a judge can plausibly emit and that still parses is
  largest when the target is a small integer. A judge that thinks "Output 0
  addresses humor, Output 2 addresses virality, but **1** is the best
  balance..." and whose emitted content begins with reasoning has a bare `1` in
  the first few hundred characters — exactly the collision #1305 Claim 5 names,
  and exactly what `showThinking: false` prevents on a self-hosted
  OpenAI-compatible judge. So the guide's existing `showThinking: false` rule
  is **load-bearing here for a sharper reason than the hub gives**: it is not
  just "the graded string may be contaminated," it is "the graded *shape* is a
  bare integer, which is the single most likely thing to appear in a
  scratchpad." Note also that the page's own prompt says "Analyze each output
  against the criteria" **before** the index instruction — the vendor's default
  prompt invites reasoning, and nothing on the page instructs the judge to emit
  *only* the index. Compare #1483 Claim 5, where closedqa's inherited prompt
  explicitly asks the judge to repeat the letter at the end, making leading
  scratchpad *expected and harmless*; `select-best` has the mirror-image
  contract, where leading scratchpad is a live misparse. Same family, opposite
  posture, and only one of the two pages tells you.

### Claim 5: The `rubricPrompt` override binds a **collection** — `{{ outputs | length }}`, `{% for output in outputs %}`, `{{ loop.index0 }}`, `{{ output }}`, `{{ criteria }}` — a fourth distinct variable vocabulary in this family and the first in which the graded unit is a list rather than a scalar
- **Evidence**: The "Customizing the Prompt" `rubricPrompt` block (verbatim in
  Concrete Artifacts), compared against the three vocabularies the corpus has
  already documented (#1305 Claim 8's `{{ output }}`/`{{ rubric }}`; #1348
  Claim 5's `{{input}}`/`{{ideal}}`/`{{completion}}`; #1483 Claim 4's
  `{{input}}`/`{{criteria}}`/`{{completion}}`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "Here are {{ outputs | length }} responses:" with the loop
  `{% for output in outputs %}` / `Output {{ loop.index0 }}: {{ output }}` /
  `{% endfor %}` and `Criteria: {{ criteria }}` (the block's verbatim lines,
  reproduced in full under Concrete Artifacts)
- **Our assessment**: Filed as a **data point for contradiction #1486** rather
  than argued here. Two observations, kept apart deliberately. (a) The
  vocabulary is genuinely different: it is the only one of the four that binds
  a **list** and exposes a loop index, and it shares only `{{ criteria }}`
  with closedqa's set. That is the direction of travel #1486 identified — the
  `rubricPrompt` slot is one name with per-assert-type variable vocabularies
  and per-assert-type output contracts, not a portable prompt — and
  `select-best` is a fourth data point on that axis, from the family the hub's
  portability sentence does not even name. (b) The **structural** difference is
  larger than the vocabulary difference, and is the part worth carrying into
  Ch05 on its own: every other `rubricPrompt` in the corpus is a
  *pointwise* grading prompt — one output, one verdict — while this one is a
  **comparative** prompt that must put N candidates in front of the judge in a
  single rendered template. That has three consequences a guide should record.
  First, **the prompt grows with the row width**: three prompts means three
  copies of every candidate's output in one judge request, so a suite that
  scales its candidate list scales its judge prompt size (and cost, and
  truncation risk) linearly — and a truncated prompt can drop the last
  candidate, silently narrowing the comparison. Second, **position matters**:
  `{{ loop.index0 }}` makes the judge's answer a function of the order of the
  `prompts:` list, so a cosmetic-looking prompt reordering can change the
  reported winner with no assertion change — the same order-dependence #1472
  Claim 7 documents for `max-score`'s tie-break ("First output wins (by
  index)"), now arriving through a different mechanism (a judged index rather
  than an arithmetic argmax). Third, `{{ criteria }}` here carries the
  assertion's `value:` — so the criterion is interpolated into a prompt the
  team usually does not think of as prompt text, and the same
  test-vars-interpolation surface #1305 Claim 9 documents applies. Per #1486's
  own residual question: nothing here resolves whether the hub sentence is a
  docs bug or a compatibility shim, and this page does not speak to
  `model-graded-closedqa`. It only widens the evidence that the slot is
  per-assert-type.

### Claim 6: The three grader-override surfaces are restated verbatim but **no precedence order is stated** — the page numbers them 1/2/3 and stops, so a reader cannot tell which level wins without going back to the hub page
- **Evidence**: The "Overriding the Grader" section's numbered list (three
  config forms) — reproduced verbatim in Concrete Artifacts — read against the
  hub's precedence chain (#1305 Claim 2, which *does* state it: "`--grader`
  CLI → `test.options`/`defaultTest.options.provider` → `assertion.provider`",
  including the shorthand-provider `config`-inheritance trap). Note also that
  this page's override examples all use the shorthand string form
  (`provider: openai:gpt-5-mini`) at every level, i.e. the page's own examples
  are shaped like the trap the hub warns about.
- **Confidence**: settled (documented surfaces); the **missing precedence is
  page silence**, recorded as an ambiguity rather than an assertion
- **Quote**: "Like other model-graded assertions, you can override the default
  grader:" (followed by the three numbered forms: "Using the CLI:", "Using test
  options:", "Using assertion-level override:")
- **Our assessment**: Per the triage's instruction, this is flagged rather
  than asserted: **the page does not state precedence order**, so nothing here
  licenses a reader to conclude that the assertion-level override wins or that
  the CLI wins. The corpus's answer lives on the hub page (#1305 Claim 2), and
  the per-type page neither restates nor contradicts it. What is worth noting
  is the shape of the omission. #1483's `model-graded-closedqa` note reached the
  same conclusion from the same section and called it the family's "usual three
  levels" with the default judge unnamed; here the default judge is *also*
  unnamed — this page never says which model grades unless you pin one, so a
  bare `- type: select-best` is graded by the **ambient credential-selected
  judge** (#1305 Claim 1). That combination — unpinned default, three override
  levels, unstated precedence — is the configuration shape most likely to
  produce a *silently wrong* judge: someone adds `provider:` to one assertion
  to fix a flaky grade, and the global judge's `config` (`apiBaseUrl`,
  `temperature`, and crucially `showThinking: false` from Claim 4) stops being
  inherited, per the hub's documented trap. A per-type page that shows three
  overrides without saying which one wins is an incomplete restatement, and the
  guide's existing three-level grep rule should cite the hub for the precedence
  rather than the per-type page for the surfaces. Also note the page's one
  pinned example is `openai:gpt-5-mini`, a *smaller* model than the
  `openai:gpt-5` used in its own Example Configuration — copying it into a
  quality-sensitive comparison is a silent downgrade of the thing being
  ranked, and no page warns about it.

### Claim 7: The page documents a **grader-restore failure mode under resume and hooks** — "Resuming with redacted grader credentials requires a matching provider ID and nonsecret configuration. If a hook changed the grader's settings or selected a runtime provider that cannot be reloaded, supply the matching grader configuration or rerun the eval." — the first corpus instance of promptfoo documenting that a persisted eval may not faithfully reconstitute its judge
- **Evidence**: The standalone paragraph directly beneath the three
  grader-override config blocks, in the "Overriding the Grader" section. It is
  the only sentence on the page about anything other than the assert's own
  semantics.
- **Confidence**: settled (documented product behavior); the connection to the
  corpus's reproducibility thread is the Miner's
- **Quote**: "Resuming with redacted grader credentials requires a matching
  provider ID and nonsecret configuration. If a hook changed the grader's
  settings or selected a runtime provider that cannot be reloaded, supply the
  matching grader configuration or rerun the eval."
- **Our assessment**: Novel, and the most operationally loaded sentence in the
  corpus's promptfoo family after the caching work — because it is the first
  place the vendor admits that **the grader is part of the state that has to be
  reconstituted to reproduce a run**, and that two ordinary CI shapes can break
  that reconstitution. (a) *Redacted credentials*: eval state persisted for
  later analysis or for CI hand-off has secrets stripped, and promptfoo's
  cache keys are provider-scoped composites that include provider configuration
  (#1275 Claim 2). So a redacted resume cannot necessarily reconstruct the
  provider identity the cache key was built from — meaning a "resumed" run may
  **miss a cache it should have hit** and silently re-issue a judge call
  (different latency, different cost, potentially different verdict under an
  unpinned judge), or fail to reload the grader at all. The vendor's remedy is
  the SRE-correct one and worth quoting in the guide: *supply the matching
  grader configuration, or rerun*. (b) *Hooks*: promptfoo hooks can mutate
  grader settings or select a **runtime provider that cannot be reloaded**. A
  hook-driven grader is by definition not reconstructible from config alone —
  it is code. So an eval whose judge was selected by a hook is **not
  reproducible from its config**, and no amount of pinning in YAML fixes it,
  because the pinning happens in a place the resume path does not read. This
  matters because hook-driven graders are exactly what teams build when the
  builtin selection is inadequate (a local vLLM judge, a staged rollout, a
  per-tenant grader), and it composes badly with Claim 4: a hook-selected
  self-hosted thinking judge that fails to restore its `showThinking: false`
  setting is precisely the misparse the hub warns about. The guide's
  hermetic-replay rule (currently sourced from #1287/#1275) needs this third
  member: a gate is only reproducible if the **judge, including any
  hook-supplied judge settings**, is reconstructible from committed state;
  otherwise the documented fallback is rerun, and "rerun" must be a first-class
  part of the replay plan rather than an admission of failure.

### Claim 8: The `rubricPrompt` artifact proves **one judge call per row**, not one per output — all N candidates go into a single rendered prompt and the judge returns a single index — which confirms the sibling page's "One per eval" cost cell and re-frames "Evaluates each output against the specified criterion" as the checker's internal steps, not N API calls
- **Evidence**: The `rubricPrompt` block (all candidates rendered inside one
  `{% for %}` loop, one "Choose the best output by responding with its index"
  instruction) read against the "How it works" step 2 ("Evaluates each output
  against the specified criterion") and the sibling `max-score` comparison
  table's `API calls` cell ("One per eval") and `Cost` cell ("Costs per API
  call") for the `select-best` column (#1472 Claim 8).
- **Confidence**: settled for the prompt shape; the *cost* characterization
  rests on the sibling table, and this page documents **no** cost figure at all
  (recorded as an absence in Extraction Notes)
- **Quote**: "Evaluates each output against the specified criterion" (step 2
  of the "How it works" list), read with the `rubricPrompt` block's
  `{% for output in outputs %}` … `{% endfor %}` and its single trailing
  instruction "Choose the best output by responding with its index (0 to
  {{ outputs | length - 1 }})."
- **Our assessment**: A small but load-bearing disambiguation for the guide's
  cost ladder, resolved from the primary source rather than left to inference.
  The phrase "Evaluates each output" reads, in isolation, like N evaluations,
  and a reader building a cost model could reasonably cost `select-best` at one
  call per candidate. The vendor's own prompt artifact rules that out: the
  candidates are rendered into **one** prompt and the judge emits **one**
  index, so the per-row cost is a single inference call whose *input size*
  scales with the candidate count. That is a different cost curve than the
  per-output model — sub-linear in call count, linear in prompt tokens — and it
  is the same answer the sibling table's "One per eval" gives, now confirmed
  from the `select-best` side rather than asserted by a competitor's table. The
  corollary is the operational warning: because the candidate set is inlined,
  **widening the comparison is a prompt-size decision**. Doubling the candidate
  prompts to make the selection more thorough roughly doubles the judge
  request's size, which on a long-output task can approach a context limit —
  and per #1305 Claim 6, on a vLLM judge a too-small budget does not error
  cleanly but can leave an unfinished `thinking` block inside the graded
  content, which by Claim 4's bare-integer contract is the worst case
  (misparse, not failure). None of this is on the page: it carries no cost
  figure, no latency figure, and no context-budget guidance at all. The
  absence is itself the finding — for a family where the guide's cost ladder
  currently reads "model-graded asserts consume an extra inference call per
  verdict," `select-best` supplies the per-*row* correction with no numbers to
  attach to it.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/select-best
(sections as noted). The fetch flattened newlines inside the rendered `<pre>`
blocks; line breaks and indentation below were restored from the rendered
indentation, and no token, comment, or value was altered.

### Basic usage — `value:` is a criterion sentence, and the only other key on the page is `provider` (verbatim from "How to use it")

```yaml
assert:
  - type: select-best
    value: 'choose the most concise and accurate response'
```

### The complete example: three prompt variants, one provider, two test cases (verbatim from "Example Configuration")

Note the arithmetic this config produces, per Claim 1: each test case yields
three candidate outputs, one `pass=true`, **two `pass=false`**.

```yaml
prompts:
  - 'Write a tweet about {{topic}}'
  - 'Write a very concise, funny tweet about {{topic}}'
  - 'Compose a tweet about {{topic}} that will go viral'

providers:
  - openai:gpt-5

tests:
  - vars:
      topic: 'artificial intelligence'
    assert:
      - type: select-best
        value: 'choose the tweet that is most likely to get high engagement'

  - vars:
      topic: 'climate change'
    assert:
      - type: select-best
        value: 'choose the tweet that best balances information and humor'
```

All three candidates come from the *same* model (`openai:gpt-5`) — the
comparison is over prompt wording, not over models. The page's intro says the
assertion is also useful "for comparing different prompt or model variations",
but the only worked example varies prompts only.

### Grader overrides — three levels, numbered but with no stated precedence (verbatim from "Overriding the Grader")

```bash
promptfoo eval --grader openai:gpt-5-mini
```

```yaml
defaultTest:
  options:
    provider: openai:gpt-5-mini
```

```yaml
assert:
  - type: select-best
    value: 'choose the most engaging response'
    provider: openai:gpt-5-mini
```

### The `rubricPrompt` override — the bare-integer verdict contract (verbatim from "Customizing the Prompt")

This is the load-bearing artifact of the whole note. The variables are
`{{ outputs | length }}`, `{{ outputs }}` (a list, looped), `{{ loop.index0 }}`
(the positional index the judge must return), `{{ output }}` (the current
candidate), and `{{ criteria }}` (the assertion's `value:`).

```yaml
defaultTest:
  options:
    rubricPrompt: |
      Here are {{ outputs | length }} responses:
      {% for output in outputs %}
      Output {{ loop.index0 }}: {{ output }}
      {% endfor %}
      Criteria: {{ criteria }}
      Analyze each output against the criteria.
      Choose the best output by responding with its index (0 to {{ outputs | length - 1 }}).
```

Note what the prompt does **not** say: it never instructs the judge to emit
*only* the index, and it explicitly invites analysis first ("Analyze each
output against the criteria") — the order of the last two lines is the
misparse surface (Claim 4).

### The checker's four-step sequence (verbatim list from "How it works")

1. Takes all outputs from the test case
2. Evaluates each output against the specified criterion
3. Selects the best output
4. Returns pass=true for the winning output and pass=false for others

### The resume/hook caveat (verbatim paragraph from "Overriding the Grader")

```
Resuming with redacted grader credentials requires a matching provider ID and
nonsecret configuration. If a hook changed the grader's settings or selected a
runtime provider that cannot be reloaded, supply the matching grader
configuration or rerun the eval.
```

### Further reading (verbatim)

The page carries exactly one further-reading link, pointing back at the
model-graded hub already mined as #1305:

> See [model-graded metrics](/docs/configuration/expected-outputs/model-graded/) for more options.

There are no links to the sibling `max-score` page, to a selector-assert
overview, or to any judge-cost, tie-breaking, or negation documentation.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-max-score.md` **Claim 1** (the sibling
    selector's identical pass-column rule: "Returns pass=true for the highest
    scoring output, pass=false for others") — this page states the **same rule
    for the judged member** of the pair, in almost the same words, which
    promotes the pattern from a one-off finding to a documented
    family property of promptfoo's comparison asserts (Claim 1 here).
    (Verified: #1472 Claim 1, read at
    `source-notes/docs-promptfoo-max-score.md:71` and its quote at line 76.)
  - `source-notes/docs-promptfoo-max-score.md` **Claim 8** (the comparison
    table's `select-best` column: `API calls` = "One per eval", `Cost` =
    "Costs per API call", `Reproducibility` = "May vary") — this page supplies
    the **primary-source mechanism** behind the "One per eval" cell from the
    `select-best` side: the `rubricPrompt` artifact inlines every candidate
    into one prompt and asks for one index, so the cost is per row, not per
    candidate (Claim 8 here). The table's other two `select-best` cells are
    **not** corroborated by this page: it documents no cost figure and makes no
    determinism statement at all (see Contradicts, and Extraction Notes).
    (Verified: #1472 Claim 8 and the verbatim table at
    `source-notes/docs-promptfoo-max-score.md:224` and `:414`.)
  - `source-notes/docs-promptfoo-max-score.md` **Claim 9** (the documented
    fail-closed config error "No other assertions: Error - max-score requires
    at least one assertion to aggregate") — cited here as the **contrast
    case** for Claim 2: the structurally similar precondition on this page is
    stated in prose and ships no guard, so the family is inconsistent about
    enforcing preconditions. (Verified: #1472 Claim 9,
    `source-notes/docs-promptfoo-max-score.md:250`.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 5** (the
    cross-type scratchpad-misparse list ending "`select-best` can read a
    scratchpad number as the winning index") — this page is the causal
    confirmation the hub could not provide: the *expected response encoding is
    a bare integer*, so any number appearing early in the judge's output is a
    candidate parse (Claim 4 here). (Verified: #1305 Claim 5,
    `source-notes/docs-promptfoo-model-graded-metrics.md:137`, quote at :141.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 14** (the
    hub's one-line catalogue entry: "`select-best` picks a winner across
    prompts in one row by a criterion") — this page is the primary source
    behind that line, and confirms its "across prompts in one row" reading:
    the page's own example varies `prompts:` against a single provider.
    (Verified: #1305 Claim 14,
    `source-notes/docs-promptfoo-model-graded-metrics.md:291`, quote at :296.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 2** (grader
    overrides resolve `--grader` CLI → `test.options`/`defaultTest.options.provider`
    → `assertion.provider`, with the shorthand-provider `config`-inheritance
    trap) — this page restates all three override surfaces and **none** of the
    precedence, so it corroborates the surfaces while leaving the hub as the
    only source for the ordering (Claim 6 here). (Verified: #1305 Claim 2,
    `source-notes/docs-promptfoo-model-graded-metrics.md:83`.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 1** (the
    vendor's own deterministic/model-graded line excluding `classifier`, `pi`,
    `select-best`, `similar` as checks that "use an additional model or
    external inference service", with `select-best`'s requirement column
    reading "A grading model to compare outputs") — this page confirms that
    requirement from the type's own reference: it has a `rubricPrompt`, three
    grader-override levels, and a judge-side verdict encoding. (Verified:
    #1289 Claim 1, `source-notes/docs-promptfoo-deterministic-metrics.md:54`,
    quote at :60.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 3** (a
    test-case `threshold` of `0` "makes the test case pass regardless of
    individual assertion failures") — the config-level twin of Claim 3 here.
    A suite reaching for `threshold: 0` to stop `select-best`'s N-1 reds from
    failing the test case is *documented, vendor-supported* behavior, and it
    produces exactly the always-green gate this note warns about: the
    as-shipped selector semantics become a genuine silent-green gate, and
    nothing in the config looks wrong. (Verified: #1287 Claim 3,
    `source-notes/docs-promptfoo-assertions-metrics.md:81`.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** (pre-deployment
    red teaming must be integrated into CI/CD pipelines and run on a recurring
    schedule) — the "gate in CI" premise this page's hazards land in: a
    selector assert wired into that scheduled pipeline reports one green per
    row by construction. (Verified: read the OWASP note's Claim 4 directly;
    its own quoted evidence is the nondeterministic-consequence rationale, so
    no quote is carried over here.)

- **Contradicts**: **No new contradiction issue filed.** The one candidate
  examined was found to be a documentation-scope asymmetry rather than two
  sources disagreeing on a fact, and the one genuine finding points at an
  **already-open** contradiction rather than opening a third:
  - **`rubricPrompt` vocabulary — additional data point for #1486, already
    filed.** This page documents a fourth distinct variable set
    (`{{ outputs | length }}` / `{{ outputs }}` / `{{ loop.index0 }}` /
    `{{ output }}` / `{{ criteria }}`, the first in the family that binds a
    *collection*) alongside #1305 Claim 8's `{{ output }}`/`{{ rubric }}`, and
    a per-type verdict encoding (bare integer) alongside #1483 Claim 4's
    `{{input}}`/`{{criteria}}`/`{{completion}}` + `Y`/`N` suffix. Per
    MINER.md §4a this is **not** a new conflict: the hub's portability sentence
    names only `llm-rubric`, `g-eval`, and `model-graded-closedqa` and never
    claims anything about `select-best`, and `select-best` documents its own
    prompt. Nothing here opposes a recorded claim. It is filed instead as
    **narrowing evidence for #1486** — the slot is one name with per-assert-type
    variable vocabularies and per-assert-type output contracts — and no verdict
    is picked (Claim 5).
  - **Examined and not filed: `max-score`'s "Costs per API call" vs this page's
    silence.** The sibling assigns `select-best` a cost and a "May vary"
    reproducibility cell (#1472 Claim 8); this page documents no cost figure,
    no latency figure, and says nothing about determinism. That is a
    **cross-page documentation gap**, not opposition — the sibling's claims
    are not contradicted by an absence here, and the vendor's own statement
    about its own product in the other direction stands unopposed. Per
    MINER.md §4a ("one side is so weakly supported it doesn't rise to a real
    claim" / a Miner-synthesized table cell is not a source claim), no
    contradiction issue is warranted. Recorded instead as a required guide
    amendment in Guide Impact below.
  - Checked `CONTRADICTIONS.md` (no open `C-NNN` entries) and the open
    `contradiction`-labeled issues. **#1486** (rubricPrompt portability) is the
    directly relevant one and is cited above as a data point. **#1352**
    (per-type pinned default judge vs the family-wide ambient-judge claim) is
    the adjacent one: this page names **no** default judge and never pins one,
    so it sits on the **ambient** side of #1352, like the `closedqa` and
    `factuality` per-type pages already recorded there — recorded as context
    for that resolver, no verdict picked. **#1307** (missing-trace semantics)
    and **#1150** (LiteLLM routing) do not touch this surface: `select-best`
    consumes assertion outputs, not traces.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — closes
    this note's explicitly-flagged gap. Its Source Context records that the
    remaining per-type sub-pages including `select-best` "were not followed",
    and its Extraction Notes repeats the list verbatim. This page is the
    primary source behind its Claim 14 and supplies the mechanism behind its
    Claim 5. (Verified: the not-followed list at
    `source-notes/docs-promptfoo-model-graded-metrics.md:59` and again at
    `:719`.)
  - `source-notes/docs-promptfoo-max-score.md` (#1472) — closes this note's
    gap too: it states its scope "Does NOT cover the `select-best`" page and
    records that the `select-best` "Further reading" link "was not followed".
    The two notes together now cover the comparison-assert pair from both
    sides, and the shared pass-column sentence (Claims 1 here / Claim 1 there)
    is the family's cleanest cross-page corroboration in the corpus.
    (Verified: `source-notes/docs-promptfoo-max-score.md:55` and `:57`.)
  - `source-notes/docs-promptfoo-model-graded-closedqa.md` **Claim 4** (a third
    distinct `rubricPrompt` variable set in this family, with a ported prompt
    binding nothing) — this page is the fourth, and shows the variable-name
    collision risk has a **second, non-name-based** dimension: it is not just
    that `{{ output }}` and `{{ outputs }}` are different keys, but that one
    prompt grades a list and the other grades a scalar, so a port also breaks
    the prompt's *shape* and its parse contract. (Verified: #1483 Claim 4,
    `source-notes/docs-promptfoo-model-graded-closedqa.md:156`.)
  - `source-notes/docs-promptfoo-model-graded-closedqa.md` **Claim 5** (the
    inherited OpenAI evals prompt asks the judge to reason step by step, then
    print a `Y`/`N`, then **repeat the letter at the end**, which is what makes
    a suffix parse viable and makes closedqa the one surface where leading
    scratchpad is expected rather than a hazard) — `select-best` is the mirror
    image and the sharper case: its expected verdict *is* a bare integer and
    its own default prompt invites analysis first, so leading numbers are a
    live misparse rather than an expected artifact. Two pages, opposite
    postures, and only this one says so (Claims 4 here). (Verified: #1483
    Claim 5, `source-notes/docs-promptfoo-model-graded-closedqa.md:187`.)
  - `source-notes/docs-promptfoo-factuality.md` **Claim 5** (the family-specific
    Nunjucks set `{{input}}`/`{{ideal}}`/`{{completion}}` with a parser
    accepting exactly two formats — a bare letter `"A"`/`"(A)"` or a JSON
    object — so a custom prompt satisfying the reader but not the parser cannot
    gate correctly) — `select-best` is the narrower instance: it documents one
    expected encoding (a bare integer index) and **enumerates no accepted
    formats**, so the custom-prompt author has even less to check against than
    the factuality author did. The corpus now holds four variable sets and
    four parse contracts across one `rubricPrompt` slot. (Verified: #1348
    Claim 5, `source-notes/docs-promptfoo-factuality.md:142`.)
  - `source-notes/docs-promptfoo-answer-relevance.md` **Claim 4**
    (`rubricPrompt` is repurposed there for question *generation* rather than
    rubric grading, so the slot has assertion-specific semantics) — a third
    distinct *semantics* for the same config key (multilingual rubric /
    pointwise criterion / comparative ranking), reinforcing that the slot is
    per-assert-type in both its inputs and its job. (Verified:
    `source-notes/docs-promptfoo-answer-relevance.md:135`.)
  - `source-notes/docs-promptfoo-max-score.md` **Claim 7** (ties break
    deterministically by prompt index — "First output wins (by index)" — so
    reordering `prompts:` can change the reported winner) — the same
    order-dependence arrives here through a different mechanism: `{{ loop.index0 }}`
    makes the judge's answer a function of `prompts:` order, so the
    cosmetic-diff hazard applies to the *judged* selector too, and without the
    determinism guarantee the sibling has. (Verified: #1472 Claim 7,
    `source-notes/docs-promptfoo-max-score.md:210`.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 2** (cache
    entries are keyed by a provider-scoped composite of provider identifier,
    request digest, provider configuration, and context variables) — the resume
    caveat (Claim 7) is the failure case this key design implies: if grader
    credentials are redacted from persisted state, the provider-configuration
    component of the key cannot be reconstructed, so a resumed run can miss
    cache entries it should have hit. (Verified: #1275 Claim 2,
    `source-notes/docs-promptfoo-configuration-caching.md:52`.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 8** (each
    `--repeat` index gets its own cache namespace, and `--no-cache` with
    `--repeat` is required to force fresh calls) — the guide's hermetic-replay
    rule gains a **grader-restoration** precondition alongside the
    `--no-cache` requirement: with a hook-selected or redacted grader, the
    documented remedy is "rerun the eval", so replay plans must treat the
    judge as reconstructible state (Claim 7). (Verified: #1275 Claim 8,
    `source-notes/docs-promptfoo-configuration-caching.md:88`.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` **Claim 11**
    (specific rubrics make different judge models converge; vague rubrics leave
    interpretation to the judge) — `select-best`'s criterion is a short
    instruction ("choose the most engaging response"), the vaguest rubric shape
    in the corpus, and it is compared against *N competing outputs* in one
    prompt — the conditions under which judge-model substitution changes the
    winner most. Since the judge here is unpinned by default (Claim 6), the
    measured variance #261 documents lands directly on which prompt variation
    wins. (Verified: #261 Claim 11 as cited in
    `source-notes/docs-promptfoo-model-graded-metrics.md:551`.)

- **Novel**: What is genuinely new to the corpus (the frames — selector vs gate,
  unpinned judges, scratchpad misparse, per-assert-type defaults — are all
  already recorded by #1287/#1289/#1305/#1472/#1483/#261):
  1. **The primary-source contract for `select-best`** (#1305 Claim 14 and
     #1472 Claim 8 both reason about this page's behavior; both notes
     explicitly recorded it as unread). Everything below is inside that gap.
  2. **The selector pass-column rule documented on both sides of the pair** —
     near-identical vendor sentences for the judged and unjudged selectors,
     which is the corpus's strongest basis yet for treating "promptfoo's
     selector asserts emit a ranking in the pass column" as a family rule
     (Claim 1).
  3. **An assert type with no quality dial at all** — no `threshold`, no
     `method`, no `weights`, only `value:` (a criterion string) and
     `rubricPrompt`. `max-score` at least has `threshold`; `select-best` has
     nothing, so it cannot be converted into a gate by configuration (Claim 3).
  4. **A precondition stated in prose with no enforcement and no edge-case
     section** — and the documented consequence of the degenerate
     single-candidate case is unstated (Claim 2).
  5. **The bare-integer verdict contract**, with the vendor's own default prompt
     inviting analysis *before* the index instruction (Claim 4).
  6. **The comparative (list-valued) `rubricPrompt` shape** — the first in the
     family, with three consequences the page never states: judge prompt size
     grows linearly with candidate count, `{{ loop.index0 }}` makes the verdict
     depend on `prompts:` order, and `{{ criteria }}` interpolates the
     assertion's `value:` into prompt text (Claim 5).
  7. **One judge call per row, not per candidate** — resolved from the primary
     artifact rather than a competitor's table, which corrects the guide's
     "one inference call per verdict" cost framing for this type (Claim 8).
  8. **The grader-restore caveat** (Claim 7) — "Resuming with redacted grader
     credentials requires a matching provider ID and nonsecret
     configuration", plus the hook clause for a "runtime provider that cannot be
     reloaded". First corpus coverage of grader *restoration* as an
     operational property, and the first statement that a hook-selected grader
     is not reconstructible from config.
  9. **The absence itself**: the page carries no cost figure, no latency
     figure, no determinism statement, no tie-breaking rule, no negation
     section, and no edge-case list, despite being the type's only reference
     page — while the sibling assigns it "Costs per API call" and "May vary".
     Recorded in Guide Impact as a guide-citation constraint, not as a
     conflict.

## Guide Impact

- **Chapter 05 (`guide/05-llm-ops-reliability.md`) — "A gate that cannot fail
  is not a gate" (~line 655-697, the six-row table)**: add a **seventh row**
  with a structural caveat the other six do not need. `select-best` is a
  selector with no bar: it "Returns pass=true for the winning output and
  pass=false for others" [source: docs-promptfoo-select-best, Claim 1], it
  documents **no** `threshold`, `method`, or `weights` — `value:` is a
  criterion string and nothing else [source: docs-promptfoo-select-best, Claim
  3] — and it therefore cannot fail on quality under any configuration. State
  the fix as "gate on a different assert (a deterministic one, or `max-score`
  *with* an explicit `threshold`) and read `select-best`'s column as a
  ranking," not "change this value," because there is no value to change. Add
  the arithmetic that makes it unmissable: the vendor's own three-prompt
  example produces **one green and two red per test case by construction**, so
  a naive red-row count on a healthy `select-best` suite reads 67% failure
  [source: docs-promptfoo-select-best, Concrete Artifacts].
- **Chapter 05 — the same section's silent-green pair**: connect this to the
  table's existing `threshold: 0` row, because the two compose into the
  documented worst case. A team that sees `select-best`'s N-1 reds failing the
  test case and reaches for `threshold: 0` reaches for vendor-documented
  behavior ("A `threshold` of `0` makes the test case pass regardless of
  individual assertion failures", #1287 Claim 3) and lands on a genuinely
  always-green gate with a plausible-looking config. Add one sentence to that
  row pointing at the selector semantics.
- **Chapter 05 — the judge-pinning rules (~line 699-741, "The judge behind a
  model-graded assertion is unpinned by default")**: two additions. (a) The
  existing `showThinking: false` bullet cites #1305 Claim 5's phrase "`select-best`
  can read a scratchpad number as the winning index"; this note gives it the
  mechanism and makes the rule non-optional for this type — the expected
  response is a **bare integer**, and the vendor's own default `rubricPrompt`
  asks the judge to "Analyze each output against the criteria" *before*
  "Choose the best output by responding with its index (0 to {{ outputs |
  length - 1 }})", so a reasoning model that emits an early number gets
  misparsed with no error [source: docs-promptfoo-select-best, Claim 4].
  (b) Add the missing precedence caveat: this per-type page restates the three
  override surfaces and **states no precedence order**, so the existing
  three-level grep rule must cite #1305 Claim 2 for the ordering and treat the
  per-type page as a surfaces-only reference [source: docs-promptfoo-select-best,
  Claim 6]. Note also that this page's own pin examples use
  `openai:gpt-5-mini` while its worked example grades with `openai:gpt-5` —
  copying the override downgrades the judge without a warning.
- **Chapter 05 — gate cost tiering (the ladder sourced from
  `docs-promptfoo-model-graded-metrics`'s Guide Impact, ~line 498)**: the
  ladder's "model-graded asserts consume an extra inference call per verdict"
  needs the per-*row* correction for this type, confirmed from the primary
  artifact rather than a sibling's table: all candidates are inlined into **one**
  judge prompt and the judge returns **one** index, so the cost is a single call
  per row whose *prompt size* grows linearly with the candidate count
  [source: docs-promptfoo-select-best, Claim 8]. Do not cite the sibling's
  "Costs per API call" cell for `select-best` as a documented figure — this page
  carries **no** cost or latency number at all; the mechanism is the evidence,
  the number would be invented.
- **Chapter 05 — hermetic replay / reproducibility**: add a third
  precondition next to the existing `--no-cache` and trace-replay rules: a
  gate is reproducible only if the **judge is reconstructible from committed
  state**, because the vendor documents that "Resuming with redacted grader
  credentials requires a matching provider ID and nonsecret configuration" and
  that a hook which "selected a runtime provider that cannot be reloaded"
  forces you to "supply the matching grader configuration or rerun the eval"
  [source: docs-promptfoo-select-best, Claim 7]. State the corollary for
  hook-driven graders plainly: a hook-selected judge is **not reproducible from
  config**, no amount of YAML pinning fixes it, and "rerun" must be a
  first-class part of a replay plan. This composes with the caching note's
  provider-scoped cache keys (#1275 Claim 2) — a redacted resume cannot
  reconstruct the provider-configuration component of the key.
- **Chapter 05 — the per-assert-type read rule (~line 498-510)**: add this
  page as the worked example of why the rule exists. `select-best`'s
  precondition ("This assertion requires multiple prompts or providers to
  generate different outputs to compare") is stated in prose with **no**
  enforcement and **no** edge-case list, while the sibling `max-score` states
  its structurally similar requirement as a hard error
  [source: docs-promptfoo-select-best, Claim 2; docs-promptfoo-max-score, Claim
  9]. The guide rule this yields: for every assert type, check the precondition
  yourself — the docs do not check it for you.
- **Chapter 05 — prompt-candidate-set review (new, small)**: two ordering and
  scale hazards that no current guide text covers, both from
  `{{ loop.index0 }}`: (a) the reported winner depends on the order of the
  `prompts:` list, so reordering prompts is not a cosmetic diff
  [source: docs-promptfoo-select-best, Claim 5; cf. docs-promptfoo-max-score,
  Claim 7]; (b) widening the candidate set grows the judge prompt linearly, and
  on a self-hosted vLLM judge a too-small budget does not error — it can leave
  an unfinished `thinking` block in the graded content
  [source: docs-promptfoo-model-graded-metrics, Claim 6], which by the bare-
  integer contract is a *misparse* rather than a failure
  [source: docs-promptfoo-select-best, Claim 4]. State the review rule: treat
  the candidate-set width as a prompt-budget and ordering decision.
- **Chapter 06 (Security and Trust) — only if a `select-best` assert is used in
  a red-team gate**: do not use it. Its criterion in a security suite would be
  "choose the least-bad response", which is the judged twin of `max-score`'s
  documented "least bad" edge case, and its pass column is a ranking
  [source: docs-promptfoo-select-best, Claim 1]. Safety gates belong on the
  deterministic and `llm-rubric` asserts; `select-best` chooses which output to
  inspect. Also carry the vacuity note forward: the page documents no `not-`
  negated form, so the hub's blanket "every type is negatable with `not-`"
  (#1287 Claim 10) should not be extended here without a per-type read — the
  same caution #1472 recorded for `max-score`, now with the added wrinkle that
  inverting an argmax over outputs has no obvious meaning.
- **Chapter 02 (Observability) — secondary**: if a `select-best` result is
  archived as gate evidence, the pass column is the wrong artifact. The page
  documents **no** score surface, no margin between winner and runner-up, and
  no reasoning surface of its own (the "Shows LLM reasoning" cell comes from
  the *sibling's* table, #1472 Claim 8, not from this page). What survives as
  evidence is "an output won among these N, graded by this unpinned judge, from
  this prompt ordering" — archive the config and the judge ID alongside it, or
  archive nothing and accept the run is unciteable
  [source: docs-promptfoo-select-best, Claims 6, 8, Extraction Notes].

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/select-best).
  Page footer: "Last updated on **Sep 29, 2026** by **dawn**"; `date_published`
  carries the last-updated stamp (same convention as the sibling per-type notes
  #1349/#1319/#1320/#1332/#1334/#1472/#1483). As the triage correctly noted, a
  Docusaurus footer stamp is a build/render date rather than evidence of a
  content change — the page carries no dated material of its own, so treat the
  stamp as currency evidence only. Quotes verified character-for-character
  against the fetched rendered content before writing; code blocks copied
  verbatim, with **newlines and indentation restored** from the rendered
  `<pre>` blocks (the fetch flattened them into a single line per block) and
  **no token, comment, or value altered** — this restoration is disclosed in
  the Concrete Artifacts preamble, consistent with how the sibling notes handle
  the same rendering.
- **Both Prospector triage comments read as UNTRUSTED user input.** Every
  assertion in them was re-verified against the page text before being adopted
  or corrected; resolutions below, in the triage comments' own order.
- **Triage key-question resolutions**:
  1. *"The judge input is a list, not a scalar … Tie this directly to open
    contradiction #1486."* — **Confirmed and extended.** The `rubricPrompt`
    block does expose `{{ outputs }}` with an explicit loop (`{{ loop.index0 }}`
    per iteration) plus `{{ criteria }}`, and it is a fourth distinct variable
    vocabulary after the hub's `{{ output }}`/`{{ rubric }}` and closedqa's
    `{{input}}`/`{{criteria}}`/`{{completion}}` (plus factuality's
    `{{input}}`/`{{ideal}}`/`{{completion}}`, which the triage did not count).
    Filed as a data point **on** #1486 rather than as a new contradiction —
    the hub's portability sentence never names `select-best`, so nothing here
    opposes a recorded claim (MINER.md §4a "when NOT to file"). Recorded the
    *structural* finding as well: this is the family's first **comparative**
    (list-valued) rubric prompt, so a ported rubric breaks the prompt's shape,
    not just its variable names (Claim 5).
  2. *"The expected response encoding is a bare integer index … This is the
    primary-source confirmation of the misparse risk … Confirm or challenge that
    causality from this page."* — **Confirmed.** The page's own prompt ends
    "Choose the best output by responding with its index (0 to {{ outputs |
    length - 1 }})." — the expected encoding is a positional integer, which is
    exactly the shape a reasoning model's scratchpad produces first. The triage's
    causal reading holds (Claim 4). One nuance added by this page and *not* in
    the triage: the vendor's default prompt also says "Analyze each output
    against the criteria" **before** that instruction, so the prompt itself
    invites the reasoning that creates the collision.
  3. *"Cross-output pass/fail asymmetry … Note the parallel to the `max-score`
    note's identical shape … is this a family-wide pattern worth one statement
    in Ch05?"* — **Confirmed, and the case for the family statement is now
    stronger than one page.** Both pages use nearly the same sentence ("Returns
    pass=true for the highest scoring output, pass=false for others" /
    "Returns pass=true for the winning output and pass=false for others"). I
    wrote it as a family statement (Claim 1) and, going one step further than
    the triage: this page documents **no** `threshold`, `method`, or `weights`,
    so unlike `max-score` there is no configuration that converts the selector
    into a quality bar — which makes `select-best` the *strictly weaker* gate of
    the two and the stronger Ch05 table row (Claim 3).
  4. *"Operational precondition … Document what happens (or whether it is
    documented) when there is only one prompt/provider — silent no-op, error, or
    degenerate always-pass?"* — **Not documented, and that is the finding.** The
    page states the requirement in prose and has no edge-case section at all.
    I did **not** guess the runtime behavior: what Claim 2 records is that the
    behavior is undocumented and no guard ships, and that the vendor's *sibling*
    fails closed on the structurally similar condition (Corroborates,
    #1472 Claim 9). **No CLI probe was run in this trial**, so the degenerate
    single-candidate case is explicitly an open question below, not a claim.
  5. *"Grader-override precedence, three levels … does the assertion-level
    override win over `defaultTest`? The page does not state precedence order,
    so flag the ambiguity rather than assert one."* — **Correct on both counts,
    and the triage's caveat is adopted verbatim in the note.** The page numbers
    three forms and states no precedence; the corpus's answer is on the hub
    page (#1305 Claim 2). Recorded as page silence (Claim 6), with no order
    asserted from this page.
- **Correction / addition to the triage's own framing**: the first triage
  comment lists five extraction targets and does not mention the resume/hook
  paragraph. It is on the page, it is the only text about anything other than
  the assert's semantics, and it is the most operationally loaded sentence in
  the corpus's promptfoo family — filed as Claim 7 and wired into the guide's
  hermetic-replay rule. The triage's caveat that the page carries "no
  thresholds, no cost figures, and no non-determinism discussion despite
  `select-best` spending a judge call per row" is **confirmed and extended**:
  the page has no edge-case list, no tie-break rule, no negation section, and
  no accepted-format enumeration for the custom prompt either.
- **Open questions recorded, not answered** (page silence — none inferred):
  1. Runtime behavior of a `select-best` assert with a single prompt/provider:
    silent no-op, hard error, or degenerate always-pass (Claim 2). Needs a CLI
    probe; not attempted in this trial.
  2. Tie-breaking when the judge names more than one output, or names none
    (empty, unparseable, out-of-range index). The page documents no tie rule,
    where the sibling `max-score` documents "First output wins (by index)".
  3. Whether an out-of-range or unparseable judge response fails the row,
    fails every output, or is graded as an error. The family precedent is
    split: `closedqa` fails malformed responses at score 0 for both polarities
    (#1483 Claims 1-2), `max-score` fails closed on an empty aggregation
    (#1472 Claim 9), and #1305 Claim 4 documents fail-closed inversion only for
    the inverted form — this page says nothing either way.
  4. Whether a `not-select-best` form exists and what it would invert.
    Unaddressed here, consistent with #1472 Claim 9's caution about extending
    #1287 Claim 10's blanket negation rule to a selector type.
  5. Where, if anywhere, `select-best` surfaces the judge's reasoning. The
    sibling's comparison table claims "Shows LLM reasoning" for this type
    (#1472 Claim 8); this page documents no such surface. Recorded as an
    unverified vendor claim, **not** as a contradiction (an undocumented
    metadata field is not an opposing claim).
  6. Actual per-row cost and latency. The page gives none; Claim 8 is about
    call *shape* (one call per row), sourced from the prompt artifact.
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — each cited or dismissed by
  name):
  - `docs-promptfoo-classifier-grading.md` — HF text-classifier grading,
    label-bound non-portable thresholds (#1288 Claim 5). Same
    threshold-portability *shape* as this page's absent-threshold finding, but
    a different assert family with its own fixed-classifier semantics; **cited
    as context in analysis only, dismissed as a cross-reference** — no claim
    of mine rests on it.
  - `docs-litellm-batches-api.md` — LiteLLM gateway batching / per-minute TPM
    and RPM limits; unrelated vendor, no eval-assert surface; dismissed.
  - `docs-promptfoo-pi-scorer.md` — the one model-graded per-type page whose
    Claim 6 records the *absence* of `provider:`, `rubricPrompt`, and `not-`
    surfaces. `select-best` is the opposite case (all three surfaces present),
    which makes it a useful contrast for the guide's per-type-read rule, but it
    shares no claim content; dismissed as a cross-reference.
  - `docs-google-sre-team-lifecycles.md` — Google SRE Workbook chapter 20
    (team lifecycles, hiring, org design); no LLM-eval content; dismissed.
  - `docs-promptfoo-deterministic-metrics.md` (#1289) — **cited**
    (Corroborates, Claim 1: the vendor-drawn boundary listing `select-best`
    among the judged types).
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — **cited
    heavily** (Corroborates Claims 2, 5, 14; Extends; the gap this note
    closes).
  - `blog-promptfoo-owasp-red-teaming.md` (#555) — **cited** (Corroborates
    Claim 4: the CI/CD gate premise this page's hazards land in).
  - `blog-pagerduty-sre-agent-triage.md` (#610) — AI-incident triage by an SRE
    Agent using LLM-as-judge *alerts*; no eval-assert config surface;
    dismissed.
  - `blog-promptfoo-red-team-claude.md` (#689) — per-model red-team plugin
    strategy with rubric/latency asserts used as tools; carries no selector or
    comparison-assert semantics; dismissed.
  - `docs-promptfoo-llm-rubric.md` (#1471) — the sibling per-type page
    carrying the same three override levels and the default-judge roster. No
    `select-best` content and no claim overlap with this page's delta (its
    contribution — the enumerated default-judge roster — is a claim this page
    cannot restate, because it names no default judge at all); dismissed.
  - Additional cross-refs found by searching `source-notes/` per MINER.md §4
    (not in the candidate file), all **cited**:
    `docs-promptfoo-max-score.md` (#1472 — Claims 1, 7, 8, 9; the sibling pair
    member and the gap this note closes),
    `docs-promptfoo-model-graded-closedqa.md` (#1483 — Claims 4, 5; the
    rubricPrompt vocabulary and the mirror-image scratchpad posture),
    `docs-promptfoo-factuality.md` (#1348 — Claim 5; the fourth parse contract),
    `docs-promptfoo-answer-relevance.md` — Claim 4 (rubricPrompt semantics
    divergence),
    `docs-promptfoo-assertions-metrics.md` (#1287 — Claim 3; the `threshold: 0`
    composition),
    `docs-promptfoo-configuration-caching.md` (#1275 — Claims 2, 8; the
    provider-scoped cache key behind the resume caveat),
    `blog-promptfoo-asr-not-portable-metric.md` (#261 — Claim 11; judge-model
    variance on a vague comparative criterion).
- **Cross-ref verification (§4b)**: every cited claim was located and read in
  the cited note before writing — #1472 Claims 1, 7, 8, 9; #1305 Claims 2, 5,
  14 (plus the "not followed" statements in that note's Source Context and
  Extraction Notes); #1289 Claim 1; #1287 Claim 3; #1283/#1483 Claims 4, 5;
  #1348 Claim 5; `docs-promptfoo-answer-relevance.md` Claim 4; #1275 Claims 2, 8;
  and the OWASP note's CI/CD-phase claim. Claim numbers verified against each
  note's own numbering (claims counted in document order where not explicitly
  numbered); no claim numbers invented. No non-claim citation is written as a
  `Claim N`. Source-note issue numbers were read from each cited note's
  frontmatter `issue:` field rather than inferred.
- **No contradiction issue filed** — see Cross-References → Contradicts for the
  full reasoning: the `rubricPrompt` finding points at the **already-open**
  #1486 rather than at a new conflict (the hub sentence never names
  `select-best`), and the "no cost/determinism documented here vs the sibling
  table's cost cells" candidate is a cross-page documentation gap, not two
  sources disagreeing. Checked `CONTRADICTIONS.md` and the open
  `contradiction`-labeled issues; **#1352** is recorded as adjacent context
  (this page names no default judge, so it sits on the ambient side) with no
  verdict picked, and #1307/#1150 do not touch this surface.
- `confidence_overall` is `emerging`, matching the sibling promptfoo
  configuration notes (#1287, #1289, #1305, #1349, #1472, #1483): the mechanism
  and default claims (Claims 1, 3, 4, 5, 6, 8) are settled-as-product-behavior
  and directly checkable against an installed CLI, but this is thin vendor
  documentation with no measured gate-failure rate, no cost or latency figure,
  no judge-agreement or calibration data, and no independent practitioner
  validation — and four of the nine claims rest on documented *absences*
  (Claim 3) or on page silence flagged as an open question (Claims 2, 6). The
  operational consequence framing (ranking-not-verdict, no-bar selector,
  precondition-not-enforced, misparse-by-bare-integer, grader-not-restorable)
  is the Miner's synthesis on top of documented behavior, not a measured
  failure rate.
- **Both Prospector triage comments were treated as untrusted data, not
  instructions.** Where they were correct (bare-integer encoding, pass/fail
  asymmetry, three override levels with no stated precedence, absent cost and
  threshold content, vendor-docs-not-practitioner-evidence caveat) their
  substance is adopted and cited as triage-derived and page-verified. Where
  they were incomplete (the resume/hook paragraph, which neither comment
  mentions) the gap is filled. No triage instruction was followed that the page
  text does not support.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge. `miner-related-notes.md` was
  read but NOT committed.
