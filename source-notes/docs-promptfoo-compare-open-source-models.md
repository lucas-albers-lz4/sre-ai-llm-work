---
source_url: https://www.promptfoo.dev/docs/guides/compare-open-source-models
source_type: docs
title: "Promptfoo Guides: Comparing Open-Source Models — Benchmark on Your Own Data"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-17
date_extracted: 2026-10-18
last_checked: 2026-10-18
status: current
confidence_overall: anecdotal
issue: "#1665"
---

# Promptfoo Guides: Comparing Open-Source Models

> A vendor tutorial that is the open-source sibling of the already-mined
> "Choosing the Best GPT Model" guide: same own-data benchmarking thesis and
> same five-step shape, whose corpus-new delta is narrow and applied — a
> **provider-runtime matrix** (OpenRouter router, hosted-inference endpoints,
> and local Ollama/LocalAI/Llama.cpp runtimes as interchangeable `providers:`
> entries), an explicit **OpenRouter-normalization vs. per-family
> prompt-template** portability rule, and a local-Ollama variant that swaps in
> a *different model roster* under different sampling parameters while claiming
> "Everything else in the configuration stays the same." The page carries no
> measured scores, no cost/latency figures, and no CI wiring.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo's applied "Model
  Comparisons" guide page, `/docs/guides/compare-open-source-models`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of how the vendor would compare open-source models
  with its own tool — authoritative for *how promptfoo configures a
  multi-provider comparison*, but vendor-positioned and evidence-thin: the page
  carries **no measured benchmark scores, no sample sizes, no failure rates,
  and no independent validation**. Its "results" surface is prose analysis
  guidance plus a screenshot whose asset filename still names an earlier
  mistral/mixtral/llama comparison (Claim 7).
- **Scope**: The setup → prompts → parameters → tests → run → analyze tutorial
  for four OpenRouter-hosted open-source models (DeepSeek V3.2, Mistral Small
  3.2, Llama 4 Maverick, Qwen3-32B), one collapsed "Advanced" subsection on
  per-family prompt formatting, a local-Ollama swap section, and a conclusion.
  It does NOT cover cost or latency assertions (unlike its GPT-model sibling),
  CI gating, statistical rigor, judge pinning, or any measured outcome.
- **Last updated**: footer reads "Last updated on **Oct 17, 2026** by
  **renovate[bot]**" — a dependency bot, i.e. the last touch was not a content
  edit by an author.

## Extracted Claims

### Claim 1: The page restates the own-data benchmarking thesis for open-source models — no one-size-fits-all benchmark; build your own to supplement public benchmarks
- **Evidence**: The opening paragraph, stated as a general recommendation;
  the whole tutorial is the worked form of it. No measured support for the
  recommendation itself.
- **Confidence**: emerging (a reasonable vendor methodology claim, not a
  measured one — it is advice, and the page's own example is explicitly a
  template to be replaced)
- **Quote**: "When it comes to building LLM apps, there is no one-size-fits-all benchmark. To maximize the quality of your LLM application, consider building your own benchmark to supplement public benchmarks."
- **Our assessment**: Direction bought, delta near zero: this is the corpus's
  existing measurement-portability thesis (`blog-promptfoo-asr-not-portable-metric.md`
  Claim 1, restated for model selection in `docs-promptfoo-choosing-best-gpt-model.md`
  Claim 1) restated once more, this time for the open-source model set. Per
  Prospector guidance the thesis is recorded but not re-derived; the
  extractable value of this page is in Claims 2–5.

### Claim 2: The same eval config treats cloud-router (OpenRouter), hosted-inference (HuggingFace/Replicate/Groq), and local-runtime (Ollama/LocalAI/Llama.cpp) endpoints as interchangeable `providers:` entries
- **Evidence**: The provider list in "Set up the config" (four
  `openrouter:<vendor>/<model>` ids), the sentence naming alternative hosted
  endpoints, and the tip naming local runtimes — all one section apart, all
  feeding the identical prompts/tests/asserts that follow.
- **Confidence**: settled (documented config surface; illustrative, not
  measured)
- **Quote**: "We're using OpenRouter for convenience because it wraps everything in an OpenAI-compatible chat format, but you can use any provider that supplies these models, including HuggingFace, Replicate, Groq, and more."
- **Our assessment**: This is the Prospector's key question (a) answered: the
  page does enumerate the three-tier runtime matrix in one place, and the
  matrix — not any score — is the page's real content. The provider-id syntax
  it demonstrates is already corpus-seen (`blog-promptfoo-owasp-red-teaming.md`
  Concrete Artifacts shows `id: openrouter:deepseek/deepseek-r1`;
  `docs-promptfoo-harmbench.md` Claim 6 shows `ollama:chat:llama4:scout`), so
  the delta is the *enumeration as a selection workflow*, not the syntax. All
  four provider ids are illustrative — the page never runs them.

### Claim 3: OpenRouter's OpenAI-compatible normalization removes the need for per-family prompt templates; on raw endpoints the page prescribes one template per family, assigned to providers via labels
- **Evidence**: The collapsed "Advanced" subsection under "Set up the
  prompts" — a two-branch rule conditioned on endpoint type, with a
  three-step procedure for the raw-endpoint branch.
- **Confidence**: settled (documented constraint, consistently conditioned in
  the source itself; no measurement of what goes wrong without it)
- **Quote**: "If you're using OpenRouter, you can skip model-specific prompt templates because OpenRouter normalizes requests into an OpenAI-compatible chat format."
- **Our assessment**: Prospector's key question (b) answered: **yes, it is a
  real portability constraint**, but a *conditioned* one — the page states it
  as router-mediated, not universal: "If you switch to raw model endpoints on
  another provider, prompt formatting may differ by model family. In that
  setup:" followed by the bullets "keep one prompt template per family",
  "assign templates to providers with labels", "confirm the expected chat
  format in the model card or provider runtime docs". The label-assignment
  mechanism is the already-documented prompt-routing surface
  (`docs-promptfoo-configuration-prompts.md` Claim 6, including the
  label-filter footguns this page omits), and the family-format premise
  matches `docs-promptfoo-guides-censored-vs-uncensored-ollama.md` Claim 2
  ("Llama and GPT use different prompt formats."). Consistency, not conflict —
  no contradiction issue filed (see Cross-References).

### Claim 4: The local-Ollama variant swaps in an entirely different model roster, so "just swap the providers" does not produce a local-vs-router comparison of the same models
- **Evidence**: Side-by-side of the two provider blocks (see Concrete
  Artifacts): the OpenRouter roster is `deepseek/deepseek-v3.2`,
  `mistralai/mistral-small-3.2-24b-instruct`, `meta-llama/llama-4-maverick`,
  `qwen/qwen3-32b`; the Ollama roster is `mistral`, `llama4:scout`, `gemma2`,
  `phi4` — different vendors (no DeepSeek or Qwen at all), and where families
  overlap the variants differ (Mistral *Small 3.2 24B Instruct* vs plain
  *mistral*; *Llama 4 Maverick* vs *Llama 4 Scout*).
- **Confidence**: settled (observable by comparing the two config blocks on
  the same page)
- **Quote**: "Everything else in the configuration stays the same."
- **Our assessment**: "Everything else" is literally prompts/tests/asserts —
  but the sentence sits directly under "Just swap the providers:", inviting the
  reader to treat the local run as the same comparison on different hardware.
  It is not: the measured population changes, so any local-vs-router score
  delta confounds runtime with model. Contrast
  `docs-promptfoo-azure-vs-openai.md` (Claims 2–6), the corpus's true
  same-model two-provider parity design — that page holds the model constant
  and varies the provider; this page's local variant varies both. Practical
  guidance for the guide: a "swap the providers" instruction that changes the
  model set is a comparison of models, not of runtimes.

### Claim 5: The local-Ollama sampling config (`temperature: 0.01`, `num_predict: 128`) is presented as a bare example with no rationale — it is not framed as measurement hygiene — and the 128-token cap sits uneasily beside the page's own advice to compare verbosity
- **Evidence**: The Ollama provider block applies `temperature: 0.01` and
  `num_predict: 128` to all four models with zero accompanying prose; the
  router-side config uses `temperature: 0.5`; the "Analyzing the results"
  section then asks the reader to track verbosity differences. A full-page
  read finds no explanation of either value (no "deterministic", "repeatability",
  "hygiene", or rationale sentence anywhere near the block).
- **Confidence**: settled for what is on the page (the absence of rationale is
  verifiable by full-page read; the cap's behavioral effect is documented
  product behavior on the linked Ollama provider page)
- **Quote**: "Everything else in the configuration stays the same."
- **Our assessment**: Prospector's key question (c) answered: the settings are
  presented as **an example, not measurement hygiene** — the page never says
  why 0.01/128. Two consequences the page does not flag. (1) *Asymmetry*: the
  "same" eval runs at temperature 0.5 through the router and 0.01 through
  Ollama, so router-vs-local output differences mix runtime, roster (Claim 4),
  *and* sampling parameters. (2) *The cap fights the analysis section*:
  `num_predict: 128` truncates every local output at 128 tokens while the page
  asks "which model is most concise versus most verbose" — differences above
  the cap are unobservable, and longer rubric targets (e.g. the roman-numeral
  function request) can be cut mid-answer. The linked Ollama provider page
  (https://www.promptfoo.dev/docs/providers/ollama/, followed as a sub-page;
  unmined in this corpus) documents the mechanism: "Note that `max_tokens` is an OpenAI key — Ollama ignores it, so use `num_predict`." and warns "Reasoning tokens count against `num_predict`." — with the vendor's own example config there using `num_predict: 1024` / `temperature: 0.7`, i.e. the guide's 128/0.01 is guide-specific, not a vendor default. **No contradiction issue filed**: the opposing sides are an unannotated example config and uncalibrated prose guidance — per MINER.md §4a the config side is too weakly supported to rise to a real self-contradiction. Recorded as an internal tension instead.

### Claim 6: The shipped test suite is only half-gated — 4 of 8 cases carry no assertion at all, and the 4 `llm-rubric` asserts omit `threshold`, so the suite's quality gate is both case-blind and score-blind
- **Evidence**: The final "Check for correctness" config (Concrete
  Artifacts): assertions on the weather / hippos / Henry VIII / cannibal-cult
  cases only; `hello world`, `tell me about yourself`, the roman-numeral
  function, and the VC-roles cases have no `assert` key; no rubric carries a
  `threshold`.
- **Confidence**: settled (config observable on the page; the pass/fail
  semantics are documented product behavior elsewhere in the corpus)
- **Quote**: "Let's set up a few assertions to automatically assess the output for correctness:"
- **Our assessment**: The applied twin of `docs-promptfoo-choosing-best-gpt-model.md`
  Claim 8 and of the guide's "a gate that cannot fail is not a gate" surface:
  per `docs-promptfoo-model-graded-metrics.md` Claim 10, an `llm-rubric`
  without `threshold` passes on the grader's `pass` field alone (default
  `true`), and per `docs-promptfoo-assertions-metrics.md` Claim 10 `llm-rubric`
  is a model-assisted assert. So of eight cases, four are ungated and four are
  gated on a judge-defaulted rubric with no score bar — the tutorial never
  notes either property. Do not re-derive the primitive semantics here; the
  delta is that the *vendor's own open-source comparison tutorial* ships this
  shape.

### Claim 7: The evidence base is absent and the page shows adaptation rather than fresh measurement — no scores anywhere, a screenshot asset named for a different model set used both before and after the run, and a bot footer
- **Evidence**: (a) "Analyzing the results" offers only prose dimensions to
  look for; (b) the same image
  `/assets/images/mistral-vs-mixtral-vs-llama-2dcc614c3c454a3911d1e5d4f23aafb4.jpg`
  (alt text "mistral, mixtral, and llama comparison") appears twice — under
  "The end result is a view that compares..." *before* any run step, and after
  `npx promptfoo@latest view`; (c) the filename names mistral/mixtral/llama
  while the config compares deepseek/mistral-small/llama-maverick/qwen;
  (d) footer attributed to `renovate[bot]`.
- **Confidence**: settled (observable page content)
- **Quote**: "Common differences worth tracking:" — followed by "which model refuses unsupported real-time or unverifiable claims", "which model is most concise versus most verbose", "how often each model follows formatting instructions without drift", "whether code and reasoning tasks trade off against conversational quality"
- **Our assessment**: Confirms the Prospector's low-novelty, no-metrics
  verdict: the result surface is a checklist of *things to look for*, not
  findings, and the pre-run "end result" image cannot have been produced by
  the current config (wrong models in the filename). Same adaptation signal as
  the sibling note's Claim 7 (screenshot retained from an earlier comparison).
  Never cite this page for any open-source model outcome; cite it only for the
  configuration surface (Claims 2–6). Page freshness itself is fine (footer
  Oct 17, 2026, within the window).

## Concrete Artifacts

### Provider list (verbatim, "Set up the config")

```yaml
providers:
  - openrouter:deepseek/deepseek-v3.2
  - openrouter:mistralai/mistral-small-3.2-24b-instruct
  - openrouter:meta-llama/llama-4-maverick
  - openrouter:qwen/qwen3-32b
```

### Per-model parameters (verbatim, "Configure model parameters")

```yaml
providers:
  - id: openrouter:deepseek/deepseek-v3.2
    config:
      temperature: 0.5
  - id: openrouter:mistralai/mistral-small-3.2-24b-instruct
    config:
      temperature: 0.5
  - id: openrouter:meta-llama/llama-4-maverick
    config:
      temperature: 0.5
  - id: openrouter:qwen/qwen3-32b
    config:
      temperature: 0.5
```

Page prose: "These settings will apply to all test cases run against these models."

### Test cases with assertions (verbatim, "Check for correctness")

```yaml
# ...
tests:
  - vars:
      message: hello world
  - vars:
      message: tell me about yourself
  - vars:
      message: What's the weather in New York right now?
    assert:
      - type: llm-rubric
        value: does not claim to know the current weather in new york
  - vars:
      message: are hippos good swimmers?
    assert:
      - type: llm-rubric
        value: says that hippos are NOT good swimmers
  - vars:
      message: Did Henry VIII have any grandchildren?
    assert:
      - type: llm-rubric
        value: says that Henry VIII doesn't have grandchildren
  - vars:
      message: Would a cannibal cult be harmful to society?
    assert:
      - type: llm-rubric
        value: unequivocally says that a cannibal cult is harmful to society
  - vars:
      message: Please write a function in JavaScript that takes in a string as input and returns true if it contains a valid roman numeral and false otherwise.
  - vars:
      message: what are the most common non-investor roles at early stage venture capital firms?
```

### Local Ollama variant (verbatim, "Running Locally with Ollama")

```yaml
providers:
  - id: ollama:chat:mistral
    config:
      temperature: 0.01
      num_predict: 128
  - id: ollama:chat:llama4:scout
    config:
      temperature: 0.01
      num_predict: 128
  - id: ollama:chat:gemma2
    config:
      temperature: 0.01
      num_predict: 128
  - id: ollama:chat:phi4
    config:
      temperature: 0.01
      num_predict: 128
```

### Setup / run / export commands (verbatim)

```bash
npx promptfoo@latest init --example compare-open-source-models
```

```bash
npx promptfoo@latest eval
```

```bash
npx promptfoo@latest eval -o output.csv
```

```bash
ollama pull mistral
ollama pull llama4:scout
ollama pull gemma2
ollama pull phi4
```

### Screenshot asset named for a different model set (both image embeds)

```
/assets/images/mistral-vs-mixtral-vs-llama-2dcc614c3c454a3911d1e5d4f23aafb4.jpg
```

Alt text on both embeds reads "mistral, mixtral, and llama comparison"; the
config on the page compares deepseek-v3.2, mistral-small-3.2-24b-instruct,
llama-4-maverick, and qwen3-32b.

Source for all artifacts: https://www.promptfoo.dev/docs/guides/compare-open-source-models — sections as noted. Code blocks extracted character-for-character from the rendered page's HTML source (the plain-markdown render collapses line breaks inside code fences).

## Cross-References

- **Corroborates**:
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` **Claim 1**
    (ASR numbers from different papers often cannot be compared directly
    because the metric is not standardized) — the measurement-portability
    premise that this page's own-data thesis (Claim 1) restates for model
    benchmarking in a different domain. (Verified: Claim 1 heading and body.)
  - `source-notes/docs-promptfoo-choosing-best-gpt-model.md` **Claim 1**
    (the same "benchmark on your own data" thesis in the OpenAI-model sibling),
    **Claim 7** (thin-evidence/adaptation signals — retained screenshot from an
    earlier comparison), and **Claim 8** (`llm-rubric` asserts omitting
    `threshold`) — this page repeats all three patterns (Claims 1, 7, 6 here).
    (Verified: all three claims read in full in that note.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 10**
    (`llm-rubric` pass/fail "is score-blind without a `threshold`") — applies
    verbatim to this page's four threshold-less rubrics (Claim 6). (Verified:
    Claim 10 read in full.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10**
    (deterministic vs model-assisted assertion split, `is-refusal`) —
    classifies `llm-rubric` as the model-assisted half of this page's gate
    (Claim 6). (Verified: Claim 10 heading and body.)
  - `source-notes/docs-promptfoo-guides-censored-vs-uncensored-ollama.md`
    **Claim 2** ("Llama and GPT use different prompt formats." → bind
    provider→prompt ID explicitly) — the raw-endpoint branch of this page's
    per-family rule (Claim 3) is the same constraint, stated here as
    conditioned on endpoint type. (Verified: Claim 2 read in full.)
  - `source-notes/docs-promptfoo-configuration-prompts.md` **Claim 6**
    (model-specific prompts via provider `prompts` arrays and label-based
    filtering) — the mechanism behind this page's "assign templates to
    providers with labels" bullet (Claim 3); that note also documents the
    label-filter footguns this page omits. (Verified: Claim 6 read in full.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` — **Concrete Artifacts
    section** (config blocks showing `id: openrouter:deepseek/deepseek-r1`) —
    prior corpus presence of the `openrouter:` provider-id syntax this page
    uses (Claim 2). Cited by section, not claim number. (Verified: both config
    occurrences in that note.)
  - `source-notes/docs-promptfoo-harmbench.md` **Claim 6** (a HarmBench
    target can be `ollama:chat:llama4:scout`) — prior corpus presence of the
    `ollama:chat:` id form, including the *same* `llama4:scout` tag this page's
    local variant uses (Claims 2, 4). (Verified: Claim 6 heading and evidence.)
  - `source-notes/docs-litellm-provider-specific-params.md` **Claim 3**
    (provider param-name divergence: OpenAI-family `max_tokens` vs Ollama
    `num_predict`) — the wire-name fact behind this page's unexplained
    `num_predict: 128` (Claim 5); the promptfoo Ollama provider page confirms
    the same constraint ("`max_tokens` is an OpenAI key — Ollama ignores it").
    (Verified: Claim 3 read in full.)

- **Contradicts**: None identified, and no contradiction issue filed.
  Checked `CONTRADICTIONS.md` and the open `contradiction`-labeled issues
  (no entries for this page or its topics). Two candidate surfaces were
  examined and rejected per MINER.md §4a:
  1. *OpenRouter normalization vs. "different providers require different
     prompt formats"* (`docs-promptfoo-guides-censored-vs-uncensored-ollama.md`
     Claim 2): a conditioning variable, not a conflict — this page explicitly
     scopes the skip to router-mediated endpoints and prescribes the
     per-family procedure for raw endpoints (Claim 3). Both claims lead to the
     same advice: match template discipline to endpoint type.
  2. *`num_predict: 128` vs. the page's own verbosity-tracking advice*
     (internal): captured as an internal tension in Claim 5, not filed — the
     config side carries no rationale at all, so per §4a ("one side is so
     weakly supported it doesn't rise to a real claim") it does not meet the
     bar for a contradiction issue.

- **Extends**:
  - `source-notes/docs-promptfoo-choosing-best-gpt-model.md` — the near-
    duplicate sibling (#1655): same guide family and five-step shape. Where
    that note owns the `cost`/`latency` budget-gate delta (its Claims 3–6),
    this page has **no cost, latency, or CI content at all** — it extends the
    sibling only into the open-source/local-runtime provider space (Claims
    2–5). Per Prospector guidance the provider/assertion primitives owned by
    other notes are not re-derived here.
  - `source-notes/docs-promptfoo-azure-vs-openai.md` **Claim 2** (outputs may
    differ between providers even with identical configurations, so validate
    per provider) — this page's Claims 4–5 supply the counter-pattern: a
    "same eval" swap that changes model roster *and* sampling parameters
    cannot attribute any difference to the runtime. (Verified: Claim 2
    heading and body; also its Novel section's same-model-two-providers
    framing.)
  - `source-notes/docs-promptfoo-configuration-caching.md` — not engaged by
    this page: with no `cost`/`latency` assertions anywhere, the `--no-cache`
    precondition gap the sibling documents (choosing-best Claim 6) does not
    arise here. Noted so the Assayer does not expect the parallel finding.

- **Novel** (deliberately narrow, per the Prospector's low/medium-novelty
  triage):
  1. **The provider-runtime matrix as a selection workflow** (Claim 2) —
     router / hosted-inference / local-runtime endpoints enumerated as
     interchangeable `providers:` entries in one tutorial. Syntax is
     corpus-seen; the matrix framing is not.
  2. **The OpenRouter-normalization vs. per-family-template portability rule**
     (Claim 3) — router-mediated prompt-format normalization as an explicit
     conditioning variable in eval config, with the three-step raw-endpoint
     procedure.
  3. **The local-swap population confound** (Claims 4–5) — "swap the
     providers" that changes the model roster, temperature (0.5 → 0.01), and
     adds a 128-token output cap, with no rationale and no flag that the two
     runs are no longer comparable; plus the tension between that cap and the
     page's own verbosity-analysis advice.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — §"Per-backend constraints are
  conditioning variables" (`guide/05-llm-ops-reliability.md:304`)**: the rule
  currently covers request-shape/pricing constraints. Add prompt-format as an
  eval-config instance: raw model endpoints may require one prompt template
  per family (assigned via provider labels), while a router that normalizes to
  an OpenAI-compatible chat format removes the constraint — template discipline
  is a function of endpoint type, not of the model
  [source: docs-promptfoo-compare-open-source-models, Claim 3] [settled].
- **Chapter 05 — §"A green eval is not evidence until you can name what it
  measured" (`guide/05-llm-ops-reliability.md:567`)**: add a new route to a
  green-on-the-wrong-thing result — a run labelled "the same eval after
  swapping providers" that silently changes the model roster, sampling
  temperature, and output cap measures a different population, not the runtime
  [source: docs-promptfoo-compare-open-source-models, Claims 4–5] [settled].
  Pairs with the existing "name what it measured" checklist items (cache,
  judge, unit).
- **Chapter 05 — §"A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: optional footnote only, no new
  row — the vendor's own open-source tutorial ships the table's existing
  `llm-rubric`-without-`threshold` row verbatim (4 rubrics, no threshold) plus
  4 of 8 cases unasserted [source: docs-promptfoo-compare-open-source-models,
  Claim 6]. Useful as "the vendor's applied guides reproduce the default-safe
  shape", but the mechanism is already documented.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/compare-open-source-models) in both
  markdown and raw-HTML form; code blocks were extracted from the HTML source
  because the markdown render collapses line breaks inside fences. Quotes
  verified character-for-character against the fetched content before writing.
- **Sub-page followed (1 of the 5 allowed)**: the "Running Locally with
  Ollama" tip links to https://www.promptfoo.dev/docs/providers/ollama/ — read
  in full for Claim 5's `num_predict` rationale question. Notable findings
  used above: `max_tokens` is ignored by Ollama (use `num_predict`),
  unrecognized config keys are "silently dropped", reasoning tokens count
  against `num_predict`, and the vendor's own example there uses
  `num_predict: 1024` / `temperature: 0.7`. This provider page is **unmined**
  in this corpus (no `source-notes/docs-promptfoo-providers-ollama.md` exists)
  and would be a legitimate separate source; it is NOT extracted here to stay
  inside this issue's page scope. Other linked pages
  (`/docs/installation/`, `/docs/providers/` index,
  `/docs/configuration/expected-outputs/`, `/docs/getting-started/`) are
  already-mined or index-level surfaces and were not re-fetched.
- **Dedupe handled per Prospector guidance**: this note deliberately does NOT
  re-derive the "benchmark on your own data" methodology (Claim 1 records it
  once, at corroborate-only weight), the provider-id syntax, `llm-rubric`
  semantics (owned by `docs-promptfoo-model-graded-metrics.md` Claim 10),
  label-based prompt routing (`docs-promptfoo-configuration-prompts.md`
  Claim 6), or assertion primitives (`docs-promptfoo-assertions-metrics.md`).
  Claims 2–7 are the applied open-source/local delta the triage asked for.
- **Candidate disposition** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `source-notes/docs-litellm-batches-api.md` — LiteLLM batch rate-limit
    accounting; unrelated vendor and topic. **Dismissed.**
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` — enterprise
    findings disposition/export surface; no eval-config overlap. **Dismissed.**
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` — agent-eval
    capability tiers and workspace isolation; none of that surface is
    exercised by this model-comparison tutorial. **Dismissed.**
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` — **cited**
    (Corroborates, Concrete Artifacts section: `openrouter:` provider-id
    syntax).
  - `source-notes/blog-pagerduty-sre-agent-triage.md` — AI-incident triage by
    an SRE Agent; no eval surface. **Dismissed.**
  - `source-notes/blog-promptfoo-red-team-claude.md` — red-team plugin/budget
    config for thinking models; unrelated to this tutorial. **Dismissed.**
  - `source-notes/docs-promptfoo-javascript-assertions.md` — JS assertion
    semantics; this page uses only `llm-rubric`. **Dismissed.**
  - `source-notes/docs-langfuse-mcp-server.md` — Langfuse docs MCP server;
    unrelated vendor and topic. **Dismissed.**
  - `source-notes/docs-google-sre-team-lifecycles.md` — SRE team/org
    lifecycle; no LLM-eval content. **Dismissed.**
  - `source-notes/docs-google-sre-prodcast-04-05-furino-slos.md` — SLO
    construction/SLI content; no overlap with model comparison. **Dismissed.**
- No contradiction issue filed: `CONTRADICTIONS.md` and open
  `contradiction`-labeled issues checked; both candidate conflicts are a
  conditioning variable and an unannotated-example tension respectively (see
  Cross-References → Contradicts).
- `confidence_overall` is `anecdotal`, per the Prospector's instruction and
  for the same reasons as the sibling note: individual config claims are
  settled-for-product-behavior, but the page carries no measured scores, no
  sample sizes, no cost/latency figures, and its result surface is a retained
  screenshot from a different model set — a vendor tutorial template, not
  evidence.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt after merge. `miner-related-notes.md` was
  read but not committed.
