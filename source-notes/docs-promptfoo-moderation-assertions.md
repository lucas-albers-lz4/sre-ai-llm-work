---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/moderation
source_type: docs
title: "Promptfoo Configuration: Moderation Assertion"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-28
date_extracted: 2026-09-28
last_checked: 2026-09-28
status: current
confidence_overall: emerging
issue: "#1498"
---

# Promptfoo Configuration: Moderation Assertion

> The vendor reference for the `moderation` / `not-moderation` assert types —
> a safety gate that *runs* a third-party classifier (OpenAI / LlamaGuard on
> Replicate / Azure Content Safety) rather than reading a normalized signal,
> and whose backend is selected by **ambient environment variables** rather
> than declared config: a stray `AZURE_CONTENT_SAFETY_ENDPOINT` on a CI runner
> silently swaps the content-safety taxonomy your gate enforces. Also the
> corpus's first coverage of the `value:` category-narrowing surface, which is
> backend-bound and non-portable (`harassment/threatening` vs `S1`–`S14` vs
> `Hate`/`SelfHarm`/`Sexual`/`Violence`).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Moderation"
  assert-type reference page under `/docs/configuration/expected-outputs/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (per the site banner, now part of OpenAI). First-party documentation of the
  tool's own `moderation` behavior — authoritative for what promptfoo does with
  a given config, and the precedence chain is stated outright rather than
  inferred. But vendor-positioned in the two places it matters: the page
  carries no measured false-pass rate, cost, or latency, and its one
  comparative performance claim defers to a self-reported benchmark on a
  different model generation. Every provider-selection and verdict-semantics
  fact below is directly checkable against an installed CLI.
- **Scope**: A single self-contained reference page for the `moderation` assert
  family. Covers the three supported backends (OpenAI's moderation model,
  Meta's LlamaGuard 3 and 4 via Replicate, Azure Content Safety), the
  environment-variable-driven backend precedence, the full per-provider
  category tables, `value:` category narrowing, the `not-moderation` negation's
  effect on reported usage, the Azure-only `blocklistNames` /
  `haltOnBlocklistHit` provider-config surface, and the token-usage
  accounting rules. Does NOT cover the `guardrails` assert type (which does not
  run a classifier — see `docs-promptfoo-guardrails-assertions.md`), the
  `classifier` assert type (`docs-promptfoo-classifier-grading.md`), the
  deterministic and model-graded families, or eval-level scoring and thresholds
  (`docs-promptfoo-assertions-metrics.md`).
- **Linked pages followed** (per MINER.md §1, up to 5): OpenAI's moderation
  guide (the page's first linked backend) and Meta's PurpleLlama
  `Llama-Guard2/MODEL_CARD.md` (the page's "See benchmarks" target). Both
  change the reading of the page materially — see Claims 6, 11, 13, 14. The
  Replicate model page and the Azure Content Safety overview were listed but
  not needed for the extraction.
- **Last updated**: Page footer reads "Last updated on Sep 28, 2026 by
  renovate[bot]" — a bot bump, not a substantive revision, so treat the content
  as a snapshot of the current tree rather than a reviewed change.
- **Page self-description**: the page's meta description reads "Implement
  comprehensive content moderation using multiple APIs to detect and filter
  harmful, toxic, or policy-violating outputs" — note "and filter". The body
  only ever *detects*: a `moderation` assert grades the output and produces a
  verdict. Nothing on the page filters, blocks, or rewrites the model output.
  See Extraction Notes.

## Extracted Claims

### Claim 1: `moderation` is a gate that *runs* a third-party classifier, not one that reads a normalized signal — the exact counterpart to the sibling `guardrails` assertion
- **Evidence**: The page's opening definition and its enumeration of the three
  supported backends, plus three full provider sections each with their own
  credential setup. There is no `providerResponse.guardrails`-style field to
  read; the assert type calls out to OpenAI, Replicate, or Azure at eval time.
- **Confidence**: settled (documented product behavior, directly checkable)
- **Quote**: "Use the `moderation` assert type to ensure that LLM outputs are safe." and "Currently, this supports OpenAI's moderation model, Meta's LlamaGuard models (LlamaGuard 3 and 4) via Replicate, and Azure Content Safety API."
- **Our assessment**: This is the claim that closes the carve-out in
  `docs-promptfoo-guardrails-assertions.md`, whose Scope section states the page
  "Does NOT cover the `moderation` assert type (sibling page)". The distinction
  matters for gate design and is not symmetric. `guardrails` is a *reader*: it
  grades a decision the target already made, and its documented hazards are
  fail-open on a missing field. `moderation` is a *runner*: the classification
  happens inside your eval, so the hazards are the ones of an external
  dependency (which backend, which taxonomy, what it costs, what happens when
  the call errors) rather than a signal-shape mismatch. Note also that the page
  describes the assert as ensuring outputs "are safe" — a detection framing,
  not a filtering one, despite the meta description.

### Claim 2: The moderation backend is selected by ambient environment variables, not by declared config — a documented two-step precedence chain where `AZURE_CONTENT_SAFETY_ENDPOINT` silently overrides the OpenAI default
- **Evidence**: The OpenAI section's default-backend sentence and the Azure
  section's auto-selection sentence, which together state the full chain: no
  `provider:` → OpenAI if `OPENAI_API_KEY` is set; `AZURE_CONTENT_SAFETY_ENDPOINT`
  set → Azure instead; explicit `provider:` on the assert → overrides both.
  Stated outright, not inferred from code.
- **Confidence**: settled (documented precedence, directly checkable by
  unsetting one env var against an installed CLI)
- **Quote**: "By default, the `moderation` assertion uses OpenAI if an OpenAI API key is provided." and "If `AZURE_CONTENT_SAFETY_ENDPOINT` is set, PromptFoo will automatically use the Azure Content Safety service for moderation instead of OpenAI's moderation API."
- **Our assessment**: The highest-value claim on the page, and the one the
  triage flagged. A committed `promptfooconfig.yaml` containing only
  `- type: moderation` is not a complete specification of what the gate checks:
  which content-safety taxonomy runs is a function of the CI runner's
  environment. Adding one variable to a runner — or inheriting one from a
  shared job definition, a container image, or an org-level secret — changes
  the classifier, the category namespace, and the false-pass behavior of a
  security gate without touching the repo or producing a config diff. This is
  the eval-side instance of the guide's *declare, don't infer* rule
  (`guide/06-security-and-trust.md:603`), which the corpus currently supports
  only from the MCP-gateway side via
  `blog-litellm-july-stability-update.md` Claim 1 ("there was no single place
  that decided which credential to attach, and no error when the decision was
  ambiguous"). It is also the eval-gate sibling of open contradiction #1352
  (promptfoo's g-eval default judge pinned vs ambient-credential-selected).
  Unlike #1352, this page is not self-contradictory — it *documents* the
  precedence — which is arguably worse for a reader skimming for a default: the
  behavior looks intentional and is easy to miss. The actionable rule is to
  always write an explicit `provider:` on a safety assert, so the backend is
  part of the reviewed diff.

### Claim 3: The Azure auto-switch keys on the *endpoint* variable alone, and a dated API version is baked into a default
- **Evidence**: The Azure "Setup" section. The setup prose requires a resource
  key *and* endpoint, but the switch condition in Claim 2 names only the
  endpoint variable; `AZURE_CONTENT_SAFETY_API_VERSION` is a third, optional
  variable documented with a hardcoded default.
- **Confidence**: settled (documented variables and default, directly
  checkable)
- **Quote** (verbatim from the page's setup block):
  ```bash
  AZURE_CONTENT_SAFETY_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
  AZURE_CONTENT_SAFETY_API_KEY=your-api-key
  AZURE_CONTENT_SAFETY_API_VERSION=2024-09-01  # Optional, defaults to this version
  ```
  The setup instruction reads "First, set these environment variables:" and the
  required-resource sentence reads "You can use the Azure Content Safety API for moderation. To set it up, you need to create an Azure Content Safety resource and get the API key and endpoint."
- **Our assessment**: Two compounding details behind Claim 2. First, the
  trigger is a single variable whose name says "endpoint" — a value that looks
  inert (it names a host, holds no secret) and would not draw a reviewer's eye
  in a secrets-scan or a CI variable list, yet is sufficient to redirect a
  safety gate. The key is required to *use* Azure but is not part of the
  switch condition as documented, so the trigger is even weaker than "the
  Azure credentials are present". Second, the API version is a dated contract
  baked into a default: `2024-09-01` is what your gate speaks unless you pin
  otherwise, and Azure adds categories and blocklist behavior across versions.
  For a security control, "defaults to a version string chosen by the docs
  author" is the same unpinned-artifact problem the guide flags for judges and
  guardrail models — a default that moves under a config nobody edited.

### Claim 4: `value:` narrows the check to named categories, and the category vocabulary is provider-specific and non-portable across all three backends
- **Evidence**: Three separate "Check specific categories" subsections, each
  with its own worked example, plus three category tables with three disjoint
  naming schemes: OpenAI's 11 slash-namespaced names (`hate`,
  `harassment/threatening`, `self-harm/instructions`, `sexual/minors`,
  `violence/graphic`, …), LlamaGuard's opaque `S1`–`S14` codes, and Azure's
  four bare capitalized names.
- **Confidence**: settled (documented product behavior, three worked examples)
- **Quote**: The three sections share the sentence "The assertion value allows
  you to only enable moderation for specific categories" and the three
  `value:` lists are `harassment` / `harassment/threatening` / `sexual` /
  `sexual/minors` (OpenAI), `S1` / `S3` / `S4` (LlamaGuard), and `hate` /
  `sexual` (Azure). Azure's category table is introduced with "The Azure Content Safety API checks content for these categories:" and lists `Hate`, `SelfHarm`, `Sexual`, `Violence`; the OpenAI table with "OpenAI monitors the following categories:"; the LlamaGuard table with "LlamaGuard monitors the following categories:".
- **Our assessment**: This is the page's most reusable operational fact and the
  concrete form of "your gate is only as good as the vocabulary you wrote".
  Three backends, three namespaces, zero overlap: a category list transfers
  between none of them. The LlamaGuard codes are the worst case, because `S1`
  carries no semantics at all — the mapping lives in the page's third table
  column, so a reviewer reading a config sees only opaque integers. The
  OpenAI namespace is also finer-grained than the other two (13 sub-categories
  of the same four Azure concepts), so an OpenAI-tuned list is *stricter* than
  the Azure list it would be pasted onto — the same category name covers
  materially different scope depending on which provider you end up on. Worth
  noting that narrowing is documented as the way to "only enable moderation for
  specific categories" with no statement that an unlisted category is
  unchecked, so a narrow list is also a coverage reduction that no run output
  makes obvious.

### Claim 5: The page documents no behavior for a `value:` entry that does not match a category on the selected backend — the silent-no-op-vs-error question the triage raised is unanswered
- **Evidence**: Absence across all three "Check specific categories"
  subsections and both category tables. There is no validation section, no
  "unknown category" note, and no error contract anywhere on the page. The
  contrast is the sibling pages: `docs-promptfoo-javascript-assertions.md`
  Claim 2 documents the fail-closed contract for its own assertion family ("If
  the JS function throws, the assertion fails (fail-closed) and the error
  message is included in the failure reason").
- **Confidence**: emerging (this is a documentation gap, not a product claim —
  the actual behavior is unstated and needs an installed CLI to establish)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: I want to be precise that this claim is about the *page*,
  not about promptfoo's behavior, which I did not test. The gap is
  consequential precisely because of Claim 2: after an ambient backend swap
  (Azure endpoint present on a CI runner), a `value:` list written for OpenAI
  names categories the Azure backend does not have. The page tells you neither
  whether that raises an error (loud, safe) nor whether the unmatched entries
  are dropped while the assertion still reports a green verdict (silent, and
  indistinguishable from a clean pass). If it is the latter, the failure
  compounds with Claim 2 into a gate that enforces a narrower or different
  policy than the config appears to name, and — unlike the
  `threshold: 0` / `weight: 0` silent-green family in
  `docs-promptfoo-assertions-metrics.md` Claims 3 and 4 — this one is *not*
  reviewable from the config at all, because the missing category name and the
  selected backend are both invisible in the committed file. Anyone gating on
  moderation should establish the behavior once with a deliberately bogus
  category and record it; that is a candidate contradiction/clarification
  issue if it turns out to be a silent no-op, and a "declare the provider
  explicitly" rule either way.

### Claim 6: The LlamaGuard `S`-code vocabulary is not stable across model generations — the page's table and the benchmark the page links for its performance claim use different numbers for the same category names from `S5` onward
- **Evidence**: The page's LlamaGuard table (a third "Code" column mapping
  `S1`–`S14` to names) side by side with the PurpleLlama model card the page's
  "See benchmarks" link resolves to, whose "Harm Taxonomy and Policy" section
  enumerates its own `S1`–`S11`. The two agree on `S1`–`S4` and diverge from
  `S5` on: the page has `S5` Defamation / `S6` Specialized Advice /
  `S10` Hate / `S11` Self-Harm / `S12` Sexual Content, while the model card
  has `S5` Specialized Advice / `S6` Privacy / `S7` Intellectual Property /
  `S8` Indiscriminate Weapons / `S9` Hate / `S10` Suicide & Self-Harm /
  `S11` Sexual Content.
- **Confidence**: settled (both documents state their mappings outright; the
  page's is a table column, the card's is a bulleted list)
- **Quote**: The model card's framing sentence is "The model is trained to
  predict safety labels on the 11 categories shown below, based on the
  MLCommons taxonomy of hazards." and its list runs "S1: Violent Crimes /
  S2: Non-Violent Crimes / S3: Sex-Related Crimes / S4: Child Sexual
  Exploitation / S5: Specialized Advice / S6: Privacy / S7: Intellectual
  Property / S8: Indiscriminate Weapons / S9: Hate / S10: Suicide & Self-Harm /
  S11: Sexual Content". The page's table, by contrast, assigns "S5" to
  "Defamation", "S6" to "Specialized Advice" and "S11" to "Self-Harm".
- **Our assessment**: The mechanism is visible in the model card, which
  explains why the numbering shifts at all: it implements 11 of the 13
  MLCommons categories and says so — "Llama Guard 2 supports 11 out of the 13
  categories included in the MLCommons AI Safety taxonomy. The Election and
  Defamation categories are not addressed by Llama Guard 2" — so it renumbers
  and drops the two it skips, while the page's table is the 13-category (plus
  `S14`) scheme. The operational consequence is that an `S`-code list is a
  *model-generation-scoped* artifact: a config pinned to
  `meta/llama-guard-3-8b:<hash>` and a config on the unpinned
  `meta/llama-guard-4-12b` are already in the page's 13-category scheme, but a
  team reading the linked benchmark to decide *what* to put in `value:` would
  read a different numbering, and any future generation that renumbers again
  silently re-points a list of integers. This is the `value:`-list analogue of
  `blog-promptfoo-asr-not-portable-metric.md` Claim 1 (a metric that cannot be
  compared without its unit): a bare `S5` is not a category, it is a category
  *in one model's numbering*. One nuance in the page's favor: its own worked
  example uses `value: [S1, S3, S4]`, which is inside the range where the two
  schemes happen to coincide, so the drift is invisible unless you reach `S5`.
  Recommended practice: write the category *names* into the assertion (via
  `metric`/`reason` or a comment) and pin the model revision, so the config
  says what it checks rather than only which integers it checks.

### Claim 7: The recommended default backend is unpinned while the alternative in the same page is pinned to a content hash — a pin-everything counterexample inside a security control
- **Evidence**: The LlamaGuard section. The main Replicate example and the
  "For compatibility" fallback both pin a 64-hex content hash on
  `llama-guard-3-8b`; the tip's *recommended* LlamaGuard 4 provider string is a
  bare model name, and the tip states that same bare-named model is the
  Replicate default.
- **Confidence**: settled (documented product guidance, strings are literal)
- **Quote**: "LlamaGuard 4 is the default moderation provider on Replicate, featuring enhanced capabilities and an additional category (S14: Code Interpreter Abuse). You can explicitly specify it:" followed by
  `provider: 'replicate:moderation:meta/llama-guard-4-12b'`. The pinned form,
  given twice on the page, is
  `provider: 'replicate:moderation:meta/llama-guard-3-8b:146d1220d447cdcc639bc17c5f6137416042abee6ae153a2615e6ef5749205c8'`.
- **Our assessment**: The exact inversion the guide's pinning discipline is
  meant to prevent, inside a safety gate rather than a judge. The page
  demonstrates that promptfoo's Replicate integration *accepts* a content-hash
  pin — twice — and then recommends the unpinned name for the version it
  prefers. Because `llama-guard-4-12b` is also Replicate's mutable default, the
  documented "explicit" configuration is simultaneously a moving target: a
  Replicate-side update changes what your CI safety gate blocks, with no repo
  change and no eval diff. The page compounds this by presenting the new
  category as a feature — `S14` Code Interpreter Abuse exists only on
  LlamaGuard 4, per its own table row — so *accepting the default silently
  widens the gate*, and doing so is documented as an upgrade. Note also the
  provider grammar: `replicate:moderation:<model>:<revision>` means the
  revision slot is part of the same string, so pinning is a one-token edit, not
  a structural change. Recommendation for the guide: on any `moderation` gate,
  pin the revision hash, and treat "the vendor's recommended default" as a
  change request with a review, not a starting point.

### Claim 8: The page's first Replicate example is annotated as the latest LlamaGuard while pinning LlamaGuard 3 — the comment contradicts both the pinned model and the page's own default statement
- **Evidence**: The example immediately below the section heading carries an
  inline comment on the `provider:` line. The comment and the model string
  disagree, and the page's own tip (Claim 7) states which model is current.
- **Confidence**: settled (the strings are literal and adjacent)
- **Quote**: The example line is
  `provider: 'replicate:moderation:meta/llama-guard-3-8b:146d1220d447cdcc639bc17c5f6137416042abee6ae153a2615e6ef5749205c8'`
  preceded by the comment `# Use the latest Llama Guard on replicate`, and the
  section's setup sentence is "This example uses the LlamaGuard model hosted on Replicate. Be sure to set the `REPLICATE_API_KEY` environment variable:". The page separately states "LlamaGuard 4 is the default moderation provider on Replicate".
- **Our assessment**: Small, but it is a documented example that misdescribes
  itself, and it is the *first* LlamaGuard config a reader copies. A reader who
  trusts the comment believes they are on the current model while running a
  hash-pinned LlamaGuard 3 — which is a defensible choice (see Claim 6) but not
  the one they were told they made, and it means the "current coverage
  question" (does my gate check `S14`?) is answered wrong. Included because it
  is the kind of artifact-level detail that a docs page's own text contradicts,
  and because it is a live instance of the guide's Ch05 rule to "read that
  assert type's own page" — here, reading the page still leaves the model
  ambiguous, so the resolved value has to come from the config or the eval
  output, not the prose.

### Claim 9: Token accounting is a documented three-state contract — provider-reported usage is billed into assertion token metrics for clean, flagged, *and provider-error* results, and `not-moderation` changes the verdict without changing the bill
- **Evidence**: A single paragraph immediately under the page's opening
  definition, before any provider section. It is the only place the page
  discusses metrics, and it names three result classes and two accounting
  rules.
- **Confidence**: settled (documented product behavior, stated outright)
- **Quote**: "When a moderation provider reports token usage, Promptfoo includes it in assertion token metrics for clean, flagged, and provider-error results. `not-moderation` changes only the verdict; it preserves reported usage. Providers that omit usage do not produce synthetic token counts."
- **Our assessment**: Three consequences the guide's cost and observability
  rules need. (1) A `moderation` assert is a *metered external call in the gate
  path*, per row, on top of the generation call — the same accounting shape
  Ch05 already records for `g-eval`'s two grader calls. (2) Error-state calls
  are billed, which is correct accounting and useful signal: a suite that is
  erroring its safety gate is spending money and producing no safety
  evidence, and the token metric is where that shows up. (3) The important gap
  is the last sentence: on a provider that reports no usage, moderation spend
  is **zero in the eval's own metrics** — not small, zero. So switching
  backends (Claim 2) or vendors can make a safety gate's cost disappear from
  the cost dashboard without the gate becoming cheaper in dollars, and
  "moderation is cheap" measured from eval metrics may be an artifact of the
  backend that was selected. Combined with `not-moderation` preserving usage,
  the practical rule is: read moderation cost from provider billing, not from
  the eval's token totals, and treat a zero moderation token count as "usage
  unreported", not "no calls". `not-moderation` is a good companion to
  `docs-promptfoo-javascript-assertions.md` Claim 3 — there the negation
  preserves a score that can contradict the verdict; here it explicitly does
  *not* touch the reported usage, so cost accounting stays honest under
  inversion.

### Claim 10: A provider error is a recognized result class for metrics but has no documented pass/fail semantics — the fail-open question is answered on the sibling page and left open here
- **Evidence**: The token paragraph in Claim 9 enumerates "provider-error
  results" as a distinct class, which establishes that the state exists in the
  result model. The page then documents nothing further about it: no verdict
  table (contrast the `guardrails` sibling page's four-row verdict table), no
  "if the provider errors" paragraph, and no fail-closed guidance. The
  `guardrails` page, by contrast, states the behavior outright in the same
  position.
- **Confidence**: emerging (documentation gap — the state is documented, its
  verdict is not)
- **Quote**: (no direct quote for the verdict behavior; the existence of the
  state is established by "clean, flagged, and provider-error results" in the
  Quote field of Claim 9, and the contrast quote below is from the sibling
  `guardrails` page, not this one)
- **Our assessment**: The triage asked specifically whether a provider error
  fails or passes the assert, and the honest answer is that this page does not
  say. I am not going to guess. What makes the gap high-value rather than
  pedantic is the asymmetry with the documented sibling: on the `guardrails`
  page, a provider `error` "skips assertions" (recorded in
  `docs-promptfoo-guardrails-assertions.md` Claim 11), and that page separately
  fails *open* when the `guardrails` field is missing (its Claim 3, score 1).
  So this vendor's documented posture on the reader side of the same
  assert family is permissive in the error direction. If `moderation` behaves
  the same way — an unreachable Replicate or a throttled Azure returns a
  result that the assertion grades as unflagged — then a CI safety gate fails
  open on exactly the transient conditions (network blip, provider rate limit,
  expired credential) most likely to occur during an incident. And the upstream
  APIs confirm the state is real rather than theoretical: OpenAI's own guide
  says "If a moderation step can't complete, the corresponding input or output
  moderation field can contain an error instead of moderation scores." The
  checklist item that follows from all of this is concrete: before trusting a
  `moderation` gate, run it once against a deliberately unreachable provider
  and confirm the suite goes red. If it goes green, that is a
  contradiction-grade finding against the guide's fail-closed posture and
  belongs in `CONTRADICTIONS.md`.

### Claim 11: The vendor's comparative performance claim carries no number on the page, and its only evidence is a self-reported, policy-aligned internal benchmark for a *different* model generation
- **Evidence**: One sentence on the page, linking out to Meta's PurpleLlama
  model card. Reading that card supplies the numbers, the internal-test-set
  caveat, the policy-alignment caveat, and the model-generation mismatch.
- **Confidence**: emerging (first-party vendor claim, self-reported benchmark,
  model generation mismatch)
- **Quote**: "In general, we encourage the use of Meta's LlamaGuard as it substantially outperforms OpenAI's moderation API as well as GPT-4." The linked card's Table 1
  ("Comparison of performance of various approaches measured on our internal
  test set") reports, on F1 / AUPRC / False Positive Rate: Llama Guard 2
  **0.915 / 0.974 / 0.040**; Llama Guard 0.665 / 0.854 / 0.027; GPT4 0.796 /
  N/A / 0.151; OpenAI Moderation API 0.347 / 0.669 / 0.030; Azure Content
  Safety API 0.519 / N/A / 0.245; Perspective API 0.265 / 0.586 / 0.046. Its
  own caveat reads "comparing model performance is not straightforward as each
  model is built on its own policy and is expected to perform better on an
  evaluation dataset with a policy aligned to the model."
- **Our assessment**: The claim is *directionally* supported and *unqualified*
  on the page, and the qualifications matter more than the number. Three
  things to record. (1) The benchmark is Meta's own, on Meta's own internal
  test set, with a decision threshold it chose: "For obtaining a binary
  classification decision from the score, we use a threshold of 0.5." It is
  first-party evidence for a third-party model's superiority over a
  competitor's API — and the card itself says the comparison is not
  straightforward because each model is built on its own policy and is
  evaluated on a policy-aligned set. (2) "Substantially outperforms" is true
  on F1 (0.915 vs 0.347 for OpenAI Moderation) and false on the *other*
  direction that matters for a user-facing gate: Llama Guard 2's false
  positive rate is 0.040 against OpenAI Moderation's 0.030, and GPT-4's is
  0.151 with the card noting "GPT-4 achieves high recall on all of the sets but
  at the cost of very high FPR (9-25%)". Over-moderation is a real cost in
  production, so the recommendation trades recall for precision and the
  one-line page summary hides which. The card's category-level breakdown makes
  the same point: Hate FNR 0.190, Specialized Advice 0.192, Sexual Content
  0.229, Indiscriminate Weapons 0.263, Child Exploitation 0.267, Sex Crimes
  0.275, Self-Harm 0.277. (3) The generation mismatch: the card is titled for
  **Llama Guard 2**, an "8B parameter Llama 3-based" model with 11 categories
  (Claim 6), while the page recommends **LlamaGuard 4** (`llama-guard-4-12b`,
  Claim 7) and its primary example pins **LlamaGuard 3**. So the numbers
  backing the recommendation are for a model two generations back, with a
  different taxonomy numbering, from a self-evaluated set. This corroborates
  `blog-promptfoo-asr-not-portable-metric.md` Claim 1 (a metric that cannot be
  compared without its unit) and Claim 8 (measurement artifacts reshuffling
  rankings): here the artifact is the evaluation set, not the judge. Guide
  treatment: record the recommendation as emerging, cite the benchmark with its
  caveats, and never report it as a settled capability comparison.

### Claim 12: Azure carries a provider-config surface no other backend has — custom blocklists that can halt the gate outside the four named categories
- **Evidence**: The closing subsection of the Azure section, which
  introduces a `provider:` given as an object with a `config:` block rather
  than a string id, carrying two options.
- **Confidence**: settled (documented product behavior, worked example)
- **Quote**: "You can also set blocklist names and halt on blocklist hit in the provider config:" followed by
  ```yaml
  provider:
    id: azure:moderation
    config:
      blocklistNames: ['my-custom-blocklist', 'industry-terms']
      haltOnBlocklistHit: true
  ```
- **Our assessment**: A coverage-accounting hazard, and the reason the `value:`
  list alone is not a description of the gate. Azure's four documented
  categories (Hate, SelfHarm, Sexual, Violence) are the *taxonomy*; the
  blocklist is an orthogonal, org-specific list, and `haltOnBlocklistHit: true`
  is the one documented control in this entire page that *blocks* rather than
  grades. Two consequences: a `value:` list that names two of the four
  categories still permits a blocklist hit on `industry-terms` to fail the
  assert, so the effective policy is `value ∪ blocklist`; and switching to
  Azure silently drops the blocklist surface entirely if you only ported a
  `value:` list from OpenAI, so the gate *narrows* on a backend swap while
  looking more capable (four categories, a custom list, a halt option) than
  the one it replaced. Also note the shape change: `provider:` accepts either a
  string id or an object with `config`, so a mechanical find-and-replace of
  `provider: 'azure:moderation'` across a config set will drop any
  `blocklistNames` you had configured. Neither LlamaGuard nor OpenAI documents
  an equivalent, so this surface exists on exactly one of three backends.

### Claim 13: The OpenAI category vocabulary promptfoo documents is smaller than the one OpenAI's own API returns — the page's table omits `illicit` and `illicit/violent`
- **Evidence**: Counting the page's OpenAI table gives 11 rows. OpenAI's
  current moderation guide documents 13 categories for the
  `omni-moderation-latest` model, with a worked JSON response whose
  `categories` and `category_scores` objects include the two names the
  promptfoo table does not list.
- **Confidence**: settled (both documents enumerate their categories; the
  omission is a direct comparison of two lists)
- **Quote**: The promptfoo page's table is introduced with "OpenAI monitors
  the following categories:" and lists 11 names ending at `violence/graphic`.
  OpenAI's guide adds, from its supported-categories table, "`illicit`" —
  "Content that gives advice or instruction on how to commit illicit acts. A
  phrase like \"how to shoplift\" would fit this category." — and
  "`illicit/violent`" — "The same types of content flagged by the `illicit`
  category, but also includes references to violence or procuring a weapon."
  OpenAI's worked response body lists them as `"illicit": false` and
  `"illicit/violent": false`.
- **Our assessment**: The gate's documented vocabulary is a subset of the
  provider's actual vocabulary, so a `value:` list that "looks complete"
  against the promptfoo page is silently incomplete against the API. The
  missing pair is the illicit-behavior branch — advice on committing crimes
  and weapon procurement — which is not a subset of anything in the promptfoo
  table, so it is not covered by any listed category and cannot be narrowed
  *to* by name. The practical read: promptfoo's table is a documentation
  snapshot that lags the provider, which is the same drift pattern as
  `docs-promptfoo-classifier-grading.md` Claim 4 (a documented flagship
  detector archived and unmaintained) and Claim 5 (thresholds are label-bound
  and non-portable) — here the *labels* drift rather than the detector. OpenAI
  warns about the same instability on the score side: "We plan to continuously
  upgrade the moderation endpoint's underlying model. Therefore, custom
  policies that rely on `category_scores` may need recalibration over time."
  Note for the guide: the promptfoo `moderation` assert takes no score
  threshold on the page — there is no documented `threshold:` for this type —
  so promptfoo is gating on the provider's boolean `flagged`/`category` hit,
  which is at least less exposed to score drift than a calibrated threshold
  would be. The exposure that remains is the *label* drift above.

### Claim 14: The upstream provider frames moderation as a signal, not a blocking decision — the vendor's own API documentation argues against treating one moderation assert as a CI hard gate
- **Evidence**: Two sentences in OpenAI's moderation guide, fetched as a
  linked sub-page. Neither is a promptfoo statement, and both are first-party
  statements from the classifier's own vendor about how to use its output.
- **Confidence**: settled (upstream vendor's explicit stated position)
- **Quote**: "Treat moderation scores as signals for your application's policy, not as an automatic blocking decision." and "Check the moderation result type before you read scores if your application needs to handle moderation failures. If a moderation step can't complete, the corresponding input or output moderation field can contain an error instead of moderation scores."
- **Our assessment**: The strongest single counterweight to reading this
  promptfoo page as a green-light for a blocking CI gate, and it comes from
  upstream rather than from a critic. Both sentences land on Claims 1 and 10:
  the first says a classifier verdict is an input to *your* policy, not the
  policy — so one `moderation` assert per category, wired straight to a
  required CI check, inverts what the classifier's own vendor recommends; the
  second confirms the error state is a designed part of the response contract,
  not an edge case, which is exactly the state Claim 10 finds undocumented in
  promptfoo's own verdict semantics. The same guide also bounds the input
  surface: "The `omni-moderation-latest` model accepts text and image inputs.
  It doesn't classify audio." — so a gate built on this backend is
  text-and-image only, and any audio path in the product under test is outside
  the taxonomy entirely. Guide treatment: a moderation assert is one signal in
  a defense-in-depth stack whose pass set you choose; pair it with a
  negative control and a documented error path, and do not let a single
  provider boolean stand as the merge gate.

## Concrete Artifacts

### Backend precedence, as documented (the three states)

Attributed to the moderation page, OpenAI section:

> By default, the `moderation` assertion uses OpenAI if an OpenAI API key is
> provided. Just make sure that the `OPENAI_API_KEY` environment variable is
> set

```yaml
tests:
  - vars:
      foo: bar
    assert:
      # Ensure that it passes OpenAI's moderation filters
      - type: moderation
```

Attributed to the moderation page, Azure section — the override that fires
without any config change:

> If `AZURE_CONTENT_SAFETY_ENDPOINT` is set, PromptFoo will automatically use
> the Azure Content Safety service for moderation instead of OpenAI's
> moderation API.

```yaml
tests:
  - vars:
      foo: bar
    assert:
      - type: moderation
        provider: 'azure:moderation'
```

### The three category vocabularies (verbatim tables, abridged to the name/code column)

OpenAI, introduced with "OpenAI monitors the following categories:" — 11 rows:

| Category               |
| ---------------------- |
| hate                   |
| hate/threatening       |
| harassment             |
| harassment/threatening |
| self-harm              |
| self-harm/intent       |
| self-harm/instructions |
| sexual                 |
| sexual/minors          |
| violence               |
| violence/graphic       |

LlamaGuard, introduced with "LlamaGuard monitors the following categories:" —
14 rows, note the third column is the only place the `S`-code meaning is
written down anywhere on the page:

| Category               | Code |
| ---------------------- | ---- |
| Violent Crimes         | S1   |
| Non-Violent Crimes     | S2   |
| Sex Crimes             | S3   |
| Child Exploitation     | S4   |
| Defamation             | S5   |
| Specialized Advice     | S6   |
| Privacy                | S7   |
| Intellectual Property  | S8   |
| Indiscriminate Weapons | S9   |
| Hate                   | S10  |
| Self-Harm              | S11  |
| Sexual Content         | S12  |
| Elections              | S13  |
| Code Interpreter Abuse | S14  |

The `S14` row's description cell ends "- LlamaGuard 4 only", which is the
table's only statement that the taxonomy is version-scoped.

Azure, introduced with "The Azure Content Safety API checks content for these
categories:" — 4 rows:

| Category | Description                                                    |
| -------- | -------------------------------------------------------------- |
| Hate     | Content that expresses discrimination or derogatory sentiments |
| SelfHarm | Content related to inflicting physical harm on oneself         |
| Sexual   | Sexually explicit or adult content                             |
| Violence | Content depicting or promoting violence against people or animals |

### Category narrowing on each backend (the three `value:` examples, verbatim)

```yaml
# OpenAI — "The assertion value allows you to only enable moderation for specific categories:"
tests:
  - vars:
      foo: bar
    assert:
      - type: moderation
        value:
          - harassment
          - harassment/threatening
          - sexual
          - sexual/minors
```

```yaml
# Meta LlamaGuard — same section heading, repeated per provider
tests:
  - vars:
      foo: bar
    assert:
      - type: moderation
        provider: 'replicate:moderation:meta/llama-guard-3-8b:146d1220d447cdcc639bc17c5f6137416042abee6ae153a2615e6ef5749205c8'
        value:
          - S1
          - S3
          - S4
```

```yaml
# Azure — the page's third and final "Check specific categories" example
tests:
  - vars:
      foo: bar
    assert:
      - type: moderation
        provider: 'azure:moderation'
        value:
          - hate
          - sexual
```

Note the Azure example's lowercase `hate` / `sexual` against the same section's
capitalized `Hate` / `Sexual` category table. The page does not state whether
the backend matches case-insensitively, and states nothing about unmatched
names at all (Claim 5) — so the one narrowing example on the Azure path is
written in a vocabulary the page does not otherwise document.

### The recommended vs pinned Replicate provider strings (verbatim, from the tip)

```yaml
# recommended, unpinned — "LlamaGuard 4 is the default moderation provider on Replicate"
provider: 'replicate:moderation:meta/llama-guard-4-12b'

# compatibility, pinned to a content hash — "For compatibility or specific use cases"
provider: 'replicate:moderation:meta/llama-guard-3-8b:146d1220d447cdcc639bc17c5f6137416042abee6ae153a2615e6ef5749205c8'
```

### The linked benchmark's Table 1 (attributed to Meta's PurpleLlama model card, not to the promptfoo page)

Decision rule: "For obtaining a binary classification decision from the score,
we use a threshold of 0.5." Measured "on our internal test set":

| Model                     | F1 ↑      | AUPRC ↑   | False Positive Rate ↓ |
| ------------------------- | --------- | --------- | --------------------- |
| Llama Guard               | 0.665     | 0.854     | 0.027                 |
| Llama Guard 2             | **0.915** | **0.974** | 0.040                 |
| GPT4                      | 0.796     | N/A       | 0.151                 |
| OpenAI Moderation API     | 0.347     | 0.669     | 0.030                 |
| Azure Content Safety API  | 0.519     | N/A       | 0.245                 |
| Perspective API           | 0.265     | 0.586     | 0.046                 |

Category-level false-negative rates for Llama Guard 2, same source, worst
first: Self-Harm 0.277, Sex Crimes 0.275, Child Exploitation 0.267,
Indiscriminate Weapons 0.263, Sexual Content 0.229, Specialized Advice 0.192,
Hate 0.190.

### Upstream OpenAI response shape (attributed to OpenAI's moderation guide)

Fields in a moderation result: `flagged`, `categories` (per-category violation
flags), `category_scores` (per-category confidence, "The value is between 0
and 1, where higher values denote higher confidence"), and
`category_applied_input_types`. The card the model card's own comparison rests
on warns: "We plan to continuously upgrade the moderation endpoint's underlying model. Therefore, custom policies that rely on `category_scores` may need recalibration over time."

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-llm-rubric.md` **Claim 5** (the default
    `llm-rubric` judge is selected per ambient credential, with a roster of
    concrete model IDs and the env vars that activate them) — the strongest
    existing precedent for Claim 2, and the same failure shape one assert
    family over: a security/quality gate's backend is a function of the
    runner's environment, not the committed config. promptfoo documents the
    credential→provider mapping in both cases; the corpus's finding is that
    *documenting the inference chain does not make the gate hermetic*.
    (Verified: #1305 Claim 5 = ambient-credential default judge, model-ID
    roster.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` **Claim 1** (ASR
    numbers cannot be compared across papers because the metric is not
    standardized), **Claim 8** (judge error reshuffles rankings — two systems
    with identical true vulnerability and identical 80% judge accuracy can
    differ by 14 ASR points), and **Claim 12** (automation defaults become the
    measured variable: "If two papers pick different automation defaults, the
    leaderboard mostly measures those defaults") — the metric-portability
    family, at assert granularity. Claim 12 is the exact structural match for
    Claim 2: the `moderation` gate's measured safety is a function of which
    default the environment selected. Claim 11's internal-test-set benchmark
    is a case study in Claim 8 — an evaluation artifact (Meta's own set, its
    own policy, its own threshold) reshuffling the comparison.
    (Verified: #261 Claim 1 = ASR not standardized, 50-pp shift; Claim 8 =
    judge-error 14-point gap; Claim 12 = automation defaults are the
    measurement.)
  - `source-notes/docs-promptfoo-classifier-grading.md` **Claim 5** (thresholds
    are label-bound and non-portable; switching detectors requires validating
    labels and recalibrating scores on your own data) — `moderation`'s
    `value:` list is the same class of artifact: a vocabulary-bound parameter
    that silently changes meaning when the detector changes. Claim 13's
    omitted `illicit` / `illicit/violent` is label drift of exactly the kind
    Claim 5 warns about, arriving from the provider side rather than through a
    detector swap. **Claim 10** (a `classifier` gate is a dependency on a
    remotely-hosted, mutable model endpoint, so the verdict is not hermetic
    with the repo) is the generic form of Claims 2, 7, and 11 here.
    (Verified: #1288 Claim 5 = label-bound non-portable thresholds; Claim 10 =
    detector-as-dependency synthesis.)
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 1** (the MCP
    gateway inferred which credential to attach from whichever fields happened
    to be set — "there was no single place that decided which credential to
    attach, and no error when the decision was ambiguous") and **Claim 3** (the
    fix was an explicit user-declared auth mode dispatched through a typed,
    exhaustively-matched resolver) — the guide's *declare, don't infer* rule
    (`guide/06-security-and-trust.md:603`) has one documented instance in the
    corpus, on the gateway side. Claim 2 is the eval-gate instance, and the
    remedy is the same shape: an explicit `provider:` on the assert, so
    selection has a single declared decision point and no precedence order.
    (Verified: Claim 1 = no single decision point, no error on ambiguity;
    Claim 3 = typed exhaustive-match resolver.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 2** (an
    unhandled throw in a custom assertion is a hard fail, fail-closed, with the
    error in the reason) — the documented fail-closed contrast for Claim 10.
    Across this vendor's assertion family, the *programmable* assert is
    fail-closed and the safety asserts are the ones with permissive or
    undocumented error handling. (Verified: #1304 Claim 2 = throw fails the
    assertion, fail-closed.)

- **Contradicts**: None identified, and **no contradiction issue filed** — the
  judgment call is recorded here so the Assayer can push back on it. Two
  candidates were considered and rejected against MINER.md §4a's "when NOT to
  file" criteria:
  1. **The `S`-code drift between this page's table and the linked PurpleLlama
     model card (Claim 6).** These look like a flat contradiction — the same
     identifiers meaning different categories — but the model card states the
     mechanism ("Llama Guard 2 supports 11 out of the 13 categories included
     in the MLCommons AI Safety taxonomy. The Election and Defamation
     categories are not addressed by Llama Guard 2"), which makes this a
     conditioning variable on model generation rather than a disagreement
     between two sources making competing claims about the same system. Under
     §4a that is captured in the note as a portability hazard, not escalated.
  2. **This page's comparative performance claim (Claim 11) vs the corpus's
     existing positions on non-portable metrics.** The page says LlamaGuard
     "substantially outperforms" the OpenAI moderation API; the linked
     benchmark's own card says cross-model comparison is "not
     straightforward". But the page makes no *measured* claim — it states no
     number — and its own linked evidence carries the caveat. An unquantified
     vendor recommendation hedged by the very source it cites is thin, not
     contradictory: it does not "rise to a real claim" (§4a) that would lead
     to different guide advice, because the guide's advice is already "record
     it as emerging and cite the caveats".
  Also checked and clear: `CONTRADICTIONS.md` has no entries at MVP bootstrap,
  and the open `contradiction`-labeled issues (#1150, #1307, #1322, #1338,
  #1352, #1408, #1461, #1462, #1486) are all unrelated surfaces. Issue **#1352**
  (promptfoo g-eval default judge: pinned vs ambient-credential-selected) is
  the *closest* open item and remains open on its own facts; this note adds a
  second, independent instance of the same pattern and does not change its
  sides, so I did not comment on it or file a duplicate. It is referenced in
  Claims 2 and 11 as adjacent evidence only.

- **Extends**:
  - `source-notes/docs-promptfoo-guardrails-assertions.md` — this note closes
    the gap that note's Scope section declares: "Does NOT cover the
    `moderation` assert type (sibling page)". The two notes together give the
    corpus the runner/reader distinction for safety gates, and the
    error-direction contrast is the payoff. That note's **Claim 1** (the
    `guardrails` assertion "does not run a guardrail or inspect the text") is
    the negative case for Claim 1 here. Its **Claim 3** (missing `guardrails`
    field is treated as `flagged: false`, so the assert passes with score 1 —
    a silent false pass) and **Claim 11** (a provider `error` skips
    assertions) are the documented verdict behavior that Claim 10 finds absent
    for `moderation`. Its **Claim 6** (detect-only guardrails set a signal
    while still delivering the unsafe output, so a force-pass reports
    `success: true`) is the mirror image of Claim 1 here: `moderation` does
    inspect the text, but it still only *reports*. Read together: a green
    moderation assert means a classifier looked and did not flag, which is a
    stronger statement than a green `guardrails` assert and a weaker one than
    a block. (Verified: #1303 Claim 1 = verdict reader not runner; Claim 3 =
    fail-open, score 1; Claim 6 = detect-only force-pass; Claim 11 = provider
    error skips assertions; Scope carve-out line as quoted.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` — the hub page's
    taxonomy (**Claim 10**: the assertion surface splits into a deterministic
    and a model-assisted family, "These metrics are model-assisted, and rely
    on LLMs or other machine learning models", and every type is negatable
    with a `not-` prefix) catalogs `moderation` as a model-assisted type; this
    note documents its parameter surface (`value:`, `provider:`, the Azure
    `config:` block, `not-moderation`) and its cost/verdict consequences. Its
    **Claims 3 and 4** (`threshold: 0` and `weight: 0` as silent-green-gate
    config values) are the precedent for treating Claim 5 as a candidate
    seventh member of that family — with the difference that the other six are
    greppable from the config and this one is not. Its **Claim 9** (offline
    replay via `--assertions asserts.yaml --model-outputs outputs.json`) is
    the natural mitigation for reproducing a moderation gate's behavior after
    the environment has moved. (Verified: #1287 Claim 3 = `threshold: 0`;
    Claim 4 = `weight: 0`; Claim 9 = offline replay; Claim 10 = family split
    and `not-` prefix, `moderation` in the model-assisted list.)
  - `source-notes/docs-promptfoo-classifier-grading.md` — the nearest sibling
    by mechanism. Both asserts run a third-party detector inside the eval, but
    the `classifier` page demands you bring a hosted endpoint and calibrate a
    threshold (its Claims 2, 5, 8) while this page supplies three managed
    backends, no documented threshold, and an environment-selected default
    (Claims 2, 13). The contrast is the useful part: `classifier` fails loudly
    on detector availability, `moderation` fails silently on backend
    availability. (Verified as cited above.)
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 3**
    (`not-javascript` inverts the verdict while preserving the returned score,
    and the threshold comparison runs *before* inversion, so score and verdict
    can diverge) — `not-moderation` is the cleaner sibling: the page states
    outright that it "changes only the verdict; it preserves reported usage".
    Together they show the `not-` family is not uniform in what it preserves,
    so a negation is per-type documentation, not a general convention.
    (Verified: #1304 Claim 3 = `not-javascript` threshold-before-inversion.)

- **Novel**: First corpus coverage of the **`moderation` / `not-moderation`
  assert type** — the sibling assert page that
  `docs-promptfoo-guardrails-assertions.md` and
  `docs-promptfoo-classifier-grading.md` both explicitly carve out. Specifically
  new to the corpus: (1) the two-step environment-variable backend precedence
  (Claim 2) as a *security*-gate concern, extending the unpinned-default-judge
  family from model-graded metrics to safety classification; (2) the `value:`
  category-narrowing surface and its three disjoint namespaces (Claim 4); (3)
  the `S`-code instability across LlamaGuard generations, established against
  the benchmark the page itself links (Claim 6); (4) the documented
  three-state token-accounting contract including "Providers that omit usage do
  not produce synthetic token counts" (Claim 9) — the first corpus evidence
  that a safety gate's cost can be *structurally invisible* in eval metrics; (5)
  the Azure-only `blocklistNames` / `haltOnBlocklistHit` surface, the one
  blocking control documented on the page (Claim 12); (6) the gap that a
  provider-error result class is documented for metrics while its verdict is
  not (Claim 10), which is a new *kind* of finding for this corpus — a
  documented state with undocumented semantics, rather than a documented
  fail-open.

## Guide Impact

- **Chapter 06 — "A guardrail gate reads a signal — it does not run a guardrail"
  (`guide/06-security-and-trust.md:387-421`)**: this section currently reads
  as though promptfoo's safety asserts are all signal readers. It needs a
  sibling subsection immediately after it: **"A moderation gate runs a
  classifier — so name the classifier."** The addition is not cosmetic. The
  existing section's whole argument is that a green `guardrails` assert proves
  a decision was *read*, and the rules that follow (export the result, confirm
  `guardrails.flagged` is present and true, never for detect-only
  integrations) are all response-shape checks. A `moderation` assert breaks
  that frame: it makes an outbound, metered, taxonomy-dependent call. The new
  rules should be (a) always set an explicit `provider:` on a safety assert so
  the backend is in the reviewed diff; (b) pin the Replicate revision hash,
  since the page demonstrates the pin syntax and then declines to use it for
  its own recommendation; (c) name the categories in config, not just the
  `S`-codes; (d) add `blocklistNames` to the audit if Azure is the backend,
  since it is outside the `value:` list. Recommend the existing section's
  title be qualified rather than replaced — "reads a signal" is still exactly
  right for `guardrails`.

- **Chapter 06 — "Gateway credential routing: declare, don't infer"
  (`guide/06-security-and-trust.md:603`)**: the rule is currently evidenced
  entirely by the LiteLLM MCP gateway postmortem and reads as a *gateway*
  concern. Add a second instance on the eval side and generalize the heading's
  scope to "credential routing" rather than "gateway credential routing." The
  sentence to add: an assert type that picks its backend from ambient
  environment variables has the same defect as a gateway that infers its auth
  mode from whichever fields are set — no single declared decision point, no
  error on the ambiguous case, and a green run that verifies something other
  than what the config names. This also strengthens the guide's standing
  against open contradiction #1352 (ambient-credential-selected eval judge) by
  showing the pattern is a vendor-wide design habit in this tool, not a
  one-page slip. Because #1352 is unresolved, the Smith should cite this note
  as a *second instance*, not as a resolution.

- **Chapter 06 — "A classifier gate's detector is a dependency with a
  lifecycle" (`guide/06-security-and-trust.md:423-436`)**: currently built
  entirely on `docs-promptfoo-classifier-grading.md` (archived flagship
  detector; label-bound thresholds). Add the moderation-side lifecycle facts:
  the *selected* model can change without a config change (backend precedence),
  the *label set* can change without a config change (OpenAI's `illicit` pair
  absent from the documented table), and the *taxonomy numbering* can change
  without a config change (`S`-code drift across LlamaGuard generations). The
  section's existing rule — "pin the detector like any other dependency" —
  should be extended with the sharper corollary for this page: pinning the
  *provider name* is not pinning the detector, because on the recommended path
  the provider name is a mutable upstream default. Add the negative-control
  step: run the moderation gate once against an unreachable provider and
  confirm the suite goes red, since the page documents a provider-error result
  class without documenting its verdict.

- **Chapter 05 — "A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:656-680`)**: the table there lists six
  config values that make a suite report green while verifying nothing, and
  all six are greppable from the config. Add a seventh row for the
  non-greppable case, and say plainly why it is different: a `value:` category
  list whose entries name categories the *selected* backend does not have.
  Unlike `threshold: 0`, nothing in the committed file reveals it, because the
  missing category name and the effective backend both live in the runner's
  environment. The row's "what makes it incapable of failing" cell should be
  the page's own admission that it documents no unmatched-category behavior.
  I have not verified the underlying product behavior, so the Smith should
  phrase this as "undocumented, verify locally" rather than as a confirmed
  silent pass — the finding is that the docs do not tell you, which is itself
  the reason it cannot be reviewed.

- **Chapter 05 — "The judge behind a model-graded assertion is unpinned by
  default" (`guide/05-llm-ops-reliability.md:699-738`)**: add a paragraph for
  the safety-assert analogue, with the page as the evidence: promptfoo
  documents a two-step precedence chain (OpenAI by default, Azure
  automatically if `AZURE_CONTENT_SAFETY_ENDPOINT` is set) and then recommends
  the unpinned Replicate default (`meta/llama-guard-4-12b`) while pinning the
  alternative twice. This is the same rule with a sharper edge, because a
  model-graded judge change degrades eval quality while a moderation-backend
  change alters what a security gate blocks. The Ch05 rule at
  `guide/05-llm-ops-reliability.md:736-738` (pin the judge explicitly and pin
  every model artifact) should gain "pin the revision, not the name."

- **Chapter 05 — gate cost accounting (near
  `guide/05-llm-ops-reliability.md:498-508`, the per-type gate-cost note)**:
  add the moderation line and, more importantly, the accounting caveat. A
  `moderation` assert is a metered external call per row; provider-reported
  usage is folded into assertion token metrics for clean, flagged *and*
  provider-error results; `not-moderation` preserves the usage; and "Providers
  that omit usage do not produce synthetic token counts" — so on such a
  provider moderation cost is **zero** in the eval's own totals while being
  non-zero on the invoice. Rule to add: treat a zero moderation token count as
  "usage unreported", and read safety-gate spend from provider billing rather
  than from eval metrics. This is the observability half of the same
  backend-selection problem: the switch changes semantics (Claim 2) and
  visibility (Claim 9) at once.

- **Chapter 05 — "Before trusting a model-graded gate, read that assert type's
  own page" (`guide/05-llm-ops-reliability.md:503-508`)**: this note is a
  strong supporting exhibit for that rule and one warning about it. The page
  does document its own precedence chain, so reading it works for Claim 2 — but
  it is silent on the two things that most affect a gate's trustworthiness
  (unmatched-category behavior, provider-error verdict), and its first worked
  example misdescribes its own model (Claim 8). Recommend the rule's wording
  gain "and check that the page's examples agree with its own prose" —
  specifically, verify the resolved provider and model from the eval output
  rather than from the docs, since a `moderation` gate's effective
  configuration is not fully reconstructable from the committed config.

- **Chapter 02 — no change recommended.** Token accounting belongs in Ch05's
  cost section, which is where the guide already puts per-assert-type gate cost
  (`guide/05-llm-ops-reliability.md:498`); adding a token-metric row in Ch02
  would split the argument. The observability-relevant fact for Ch02 is not
  "moderation emits tokens" but "this call path can report zero tokens", which
  is an eval-observability problem.

## Extraction Notes

- **Deep-read, not skimmed.** The rendered page was read in full, then
  cross-checked against the page's own markdown source
  (`site/docs/configuration/expected-outputs/moderation.md` in
  `promptfoo/promptfoo`) to confirm every quoted string and, importantly, the
  LlamaGuard table's column structure. That check mattered: the rendered HTML
  table is a 3-column `Category | Description | Code` table whose visual
  rendering pairs each code with the *following* row's label, which makes
  `S14` look like an empty row. The source markdown confirms `S14` is
  correctly `Code Interpreter Abuse` and that the page is internally consistent
  between its table and its tip. Anyone re-checking these tables from the
  rendered page should be aware of that rendering artifact.
- **Two linked sub-pages followed** (of the five budgeted): OpenAI's
  moderation guide and Meta's PurpleLlama `Llama-Guard2/MODEL_CARD.md`. Both
  changed the extraction — OpenAI's supplied Claims 13 and 14 and the
  `illicit` / `illicit/violent` gap; the model card supplied Claims 6 and 11
  and the FPR direction. The Replicate model page and the Azure Content Safety
  overview were listed on the page but not needed; I did not read them, so
  nothing here depends on them.
- **Two claims are documentation gaps, not product findings, and are marked
  as such.** Claims 5 and 10 assert what the page does *not* say, and both
  carry `Quote: (no direct quote; see paraphrase in Our assessment)`. I did not
  install promptfoo or execute an eval, so I have not established promptfoo's
  actual behavior for an unmatched `value:` category or for a provider error.
  Both are stated as "the page does not document this", which is checkable by
  reading the page, and both carry a concrete local test to resolve them
  (bogus category name; unreachable provider). Neither should be promoted to
  `settled` without that test, and neither should be written into the guide as
  a confirmed silent pass — the Smith should mark them as undocumented and
  actionable.
- **A meta-description / body mismatch worth recording but not claiming.** The
  page's meta description reads "Implement comprehensive content moderation
  using multiple APIs to detect and filter harmful, toxic, or policy-violating
  outputs". The body only detects: a `moderation` assert grades the output and
  yields a verdict, and the single blocking control on the entire page is
  Azure's `haltOnBlocklistHit`. I folded this into Claim 1's assessment and
  Claim 12 rather than giving it its own claim, because the meta description
  is marketing copy rather than a documented behavior. Flagging it here so
  nobody cites the meta description as a capability claim.
- **No contradiction issue filed**, and that was a deliberate call with two
  rejected candidates written out in Cross-References (the `S`-code drift and
  the comparative-performance claim). Both were judged to be conditioning
  variables or thin claims under MINER.md §4a's "when NOT to file" list. The
  `S`-code drift is the one I would most expect the Assayer to disagree with,
  so the reasoning is spelled out in the note rather than left implicit. If
  anyone reads the drift as a same-system disagreement, that reassessment
  belongs with the contradiction-resolver, not inside a source note.
- **No behavior executed.** Everything asserted as `settled` is a documented
  string, table, or precedence statement read from the page or its two linked
  sub-pages — all directly re-checkable at the source URL. The `S`-code
  mapping, the provider strings, the env-var block, the three category tables,
  and the three `value:` examples are quoted verbatim so the Assayer can
  diff them against the live page.
- **Candidate dispositions** (from `miner-related-notes.md`, read before
  writing Cross-References; all ten candidates addressed):
  `blog-promptfoo-owasp-red-teaming.md` — **dismissed**: OWASP red-teaming
  methodology (objectives, threat categories, SDLC phases), not
  assert-level provider selection; no claim on this page bears on it.
  `docs-litellm-batches-api.md` — **dismissed**: batch rate-limit and
  token-reservation accounting; shares only the word "metrics" and the subject
  of rate limits, not gate semantics.
  `blog-pagerduty-sre-agent-triage.md` — **dismissed**: LLM-as-judge alert
  triage and connectors; its Claim 1 (eval alerts redefine the triage signal)
  is thematically adjacent but makes no claim about assertion configuration.
  `docs-promptfoo-classifier-grading.md` — **cited** (Corroborates Claims 5
  and 10; Extends), as the nearest mechanism sibling.
  `docs-promptfoo-javascript-assertions.md` — **cited** (Corroborates Claim 2
  for the fail-closed contrast; Extends Claim 3 for `not-` semantics).
  `docs-promptfoo-llm-rubric.md` — **cited** (Corroborates Claim 5): the
  ambient-credential default-judge precedent, found by me in the candidate file
  rather than in the issue's triage comment.
  `docs-langfuse-mcp-server.md` — **dismissed**: documentation-MCP transport
  and client config; unrelated surface.
  `docs-google-sre-team-lifecycles.md` — **dismissed**: SRE org design and
  hiring; no overlap.
  `docs-promptfoo-assertions-metrics.md` — **cited** (Extends Claims 3, 4, 9,
  10): the hub taxonomy, the silent-green-gate family, and offline replay.
  `blog-promptfoo-red-team-gemini.md` — **dismissed**: Gemini-specific attack
  surface (context length, multimodal injection, thinking-mode DoS); its
  `thinkingConfig` pinning advice is a model-config concern, not a moderation
  assert concern.
  Additional cross-references found by searching `source-notes/` beyond the
  candidate list and not in the file:
  `source-notes/docs-promptfoo-guardrails-assertions.md`,
  `source-notes/blog-promptfoo-asr-not-portable-metric.md`, and
  `source-notes/blog-litellm-july-stability-update.md` — all cited above.
- **`miner-related-notes.md` was not committed.** Per MINER.md §4 it is a
  retrieval aid only; it remains untracked in the working tree.
- **`registry/sources.json` and `registry/claims-index.json` were not
  touched** — both are derived indexes rebuilt post-merge by
  `registry-rebuild.yml`.
- **Confidence**: `emerging` overall. Single first-party vendor page for its
  own product (authoritative for the precedence chain and the literal
  strings, weak for comparative performance and silent on two verdict
  questions), no independent practitioner validation, and no measured
  false-pass rate, cost, or latency for the moderation path. Consistent with
  the sibling promptfoo config notes.
