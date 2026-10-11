---
source_url: https://www.promptfoo.dev/docs/guides/evaling-with-harmbench
source_type: docs
title: "Promptfoo Docs — Evaluating LLM Safety with HarmBench (Standardized-Benchmark Red-Team Plugin)"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-11
date_extracted: 2026-10-11
last_checked: 2026-10-11
status: current
confidence_overall: emerging
issue: "#1667"
---

# Promptfoo Docs — Evaluating LLM Safety with HarmBench (Standardized-Benchmark Red-Team Plugin)

> The vendor recipe for driving a *standardized public* red-team benchmark
> (HarmBench, 400 behaviors) through promptfoo's `harmbench` plugin: the
> `config.categories` (semantic) vs `config.functionalCategories` (functional)
> filter taxonomy and their documented **intersection** semantics, the
> app-context-vs-vanilla-base-model target comparison, and a caution — the page
> documents a config surface, not a scoring formula or CI threshold.

## Source Context

- **Type**: docs (vendor product guide — Promptfoo "Evaluating LLM safety with
  HarmBench", under Red teaming → Guides; auto-discovered from the registered
  `promptfoo-docs` site-crawl seed).
- **Author credibility**: Promptfoo, the commercial LLM eval / red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  product's own `harmbench` redteam plugin and config surface — authoritative
  for the documented syntax and mechanism, but vendor-positioned: the page
  reports no scoring formula, no threshold, no pass-rate, and no independent
  validation. Page footer: "Last updated on **Oct 11, 2026** by
  **renovate[bot]**".
- **Scope**: Covers (1) what HarmBench is (400-behavior dataset from UC
  Berkeley, Google DeepMind, and the Center for AI Safety); (2) the base
  `promptfooconfig.yaml` (`targets`, `redteam.plugins[0].id: harmbench`,
  `numTests`); (3) category filtering — semantic `config.categories` and
  functional `config.functionalCategories`, with documented **intersection**
  behavior when both are set; (4) the `redteam run` → `view` workflow; (5)
  alternate targets — Ollama, and an app behind the HTTP / JS / Python
  providers; (6) a static-vs-dynamic "combine with other plugins" closing note.
  Does NOT cover: a scoring formula, any pass/fail threshold, observed
  pass-rates, per-category result breakdowns, or a CI-gating recipe.
- **Followed sub-page**: the directly-linked plugin reference
  `https://www.promptfoo.dev/docs/red-team/plugins/harmbench/` (same footer
  date) was read to confirm the canonical slug list, the default `numTests: 5`,
  alias normalization, and the static-dataset caveat. Quotes below are
  attributed to the page they come from.

## Extracted Claims

### Claim 1: HarmBench is a standardized public evaluation framework holding 400 harmful-behavior test cases, created by UC Berkeley, Google DeepMind, and the Center for AI Safety
- **Evidence**: The page's framing section names the creating institutions and
  the size, and lists the six prose behavior classes (chemical/biological,
  illegal activities, misinformation/conspiracy, harassment/hate speech,
  cybercrime, copyright). The plugin sub-page repeats the 400-behavior framing
  and adds "General harmful requests".
- **Confidence**: settled (external benchmark provenance; the HarmBench paper
  and GitHub repo are linked)
- **Quote**: "To help define a systematic way to assess potential risks and vulnerabilities in LLM systems, researchers at UC Berkeley, Google DeepMind, and the Center for AI Safety created HarmBench, a standardized evaluation framework for automated red teaming of Large Language Models (LLMs)."
- **Our assessment**: This is the page's one piece of externally verifiable
  substance: a named, citable public benchmark (arXiv 2402.04249) rather than a
  vendor-generated prompt set. That provenance is what gives the page any
  corpus value — the mechanism below is vendor config, but the *dataset* is
  third-party. We buy the provenance claim; we do not buy any implied
  detection-quality claim (the page makes none with evidence).

### Claim 2: The `harmbench` plugin is invoked as a first-class redteam plugin — `redteam.plugins[0].id: harmbench` with a `numTests` count — and running the full 400-behavior dataset is a config setting
- **Evidence**: The base config sets `numTests: 400` (the full benchmark); the
  filtered variant sets `numTests: 50`. The plugin sub-page documents the
  default as `numTests: 5` and notes the parameter "controls the number of test
  cases."
- **Confidence**: settled (documented config, directly checkable)
- **Quote**: (config block; see Concrete Artifacts → HarmBench evaluation of OpenAI GPT-5-mini) "- id: harmbench" and "numTests: 400"
- **Our assessment**: The operative fact is that a standardized external
  benchmark is exposed as a single plugin id — the same call shape as the
  vendor's own `harmful`/`pii` plugins. The `numTests` knob is a sample-size
  control, not a coverage control: setting `numTests: 50` samples the dataset,
  it does not define *which* behaviors are tested (that is the category filters,
  Claim 3). Teams often confuse sample count with coverage; the guide should
  state the distinction.

### Claim 3: HarmBench filtering has two orthogonal axes — 7 canonical **semantic** categories and 3 **functional** categories — and when both are set, Promptfoo uses their **intersection**
- **Evidence**: The page states the canonical semantic slugs
  (`chemical_biological`, `copyright`, `cybercrime_intrusion`,
  `harassment_bullying`, `harmful`, `illegal`,
  `misinformation_disinformation`), the functional slugs (`standard`,
  `contextual`, `copyright`), and the intersection rule explicitly. The plugin
  sub-page repeats the rule and adds that common aliases (e.g. `cybercrime`,
  `misinformation`) are normalized to the canonical values.
- **Confidence**: settled (documented behavior)
- **Quote**: "The semantic categories are `chemical_biological`, `copyright`, `cybercrime_intrusion`, `harassment_bullying`, `harmful`, `illegal`, and `misinformation_disinformation`. The functional categories are `standard`, `contextual`, and `copyright`. When you set both filters, Promptfoo uses their intersection."
- **Our assessment**: The single most reusable extraction here — the two-axis
  taxonomy plus intersection semantics is a concrete, reproducible filter
  contract. It also exposes a documentation wrinkle worth flagging: the page's
  own filtered example uses the *aliases* `cybercrime` and `misinformation`,
  but the terminology sentence lists only canonical slugs; without the plugin
  sub-page's alias-normalization note, a reader would have to guess whether
  `cybercrime` is a valid value. The guide should cite the canonical values and
  note aliases are accepted.

### Claim 4: The plugin tests the target *within the application's context* (prompt engineering, safety guardrails, processing layers), not the base model in isolation
- **Evidence**: The page's central scope statement, contrasted with "testing
  base models in isolation".
- **Confidence**: emerging (a scope/test-design claim, not a measured result)
- **Quote**: "Unlike testing base models in isolation, Promptfoo enables you to evaluate the actual behavior of LLMs within your application's context - including your prompt engineering, safety guardrails, and any additional processing layers."
- **Our assessment**: This is the page's genuine analytical content and its
  best link to the corpus: it argues the benchmark should be run against *your
  app*, so the result measures application defenses rather than the underlying
  model. It is a test-design assertion, not evidence — no run is shown to prove
  the app context changes the score. Still, it is the right framing for Ch06's
  baseline discipline (run a no-jailbreak baseline before jailbreaks): the
  "baseline" that matters is the deployed app, not the model card.

### Claim 5: The page asserts an app can beat its own vanilla base model — its internal sample app (powered by `gpt-5-mini`) "resist[s] attacks that the vanilla model is not able to" — but publishes no numbers
- **Evidence**: The results section: providing application context to OpenAI,
  the internal app is observed to resist attacks the vanilla model does not;
  the page points at an example eval and a "Show failures only" filter. No
  scores, rates, or sample sizes are given for the comparison.
- **Confidence**: anecdotal (unquantified vendor observation)
- **Quote**: "By providing some additional context to OpenAI (from our application), you can observe how our internal application is able to resist attacks that the vanilla model is not able to."
- **Our assessment**: Directionally the same "prompt engineering + guardrails
  matter" point as Claim 4, but this is where the page is weakest: a comparative
  claim with zero supporting figures. Per the corpus's ASR discipline
  (`blog-promptfoo-asr-not-portable-metric.md`), an unquantified
  app-vs-model comparison is not reportable evidence. Treat as a hypothesis the
  guide should test, not a finding to cite.

### Claim 6: A HarmBench target is any promptfoo target — a base model (`openai:...`), an Ollama model, a JS/Python provider, or a generic HTTP app whose request body maps `myPrompt: '{{prompt}}'`
- **Evidence**: The "Testing different targets" section documents
  `ollama:chat:llama4:scout` and a generic `https` provider whose body is
  `myPrompt: '{{prompt}}'`.
- **Confidence**: settled (documented config)
- **Quote**: (config block; see Concrete Artifacts → Generic HTTP application target) "myPrompt: '{{prompt}}'"
- **Our assessment**: The target-agnosticism is what makes the benchmark usable
  against a black-box app (Claim 4). Note the overlap with the corpus's sibling
  black-box recipe: this page's one-line HTTP body template is the minimal form
  of the two-layer `transformRequest`/`transformResponse` contract documented in
  `docs-promptfoo-chatbase-redteam.md` Claim 5. The guide should not re-extract
  the HTTP-provider plumbing from this page — it is thinner here; cite the
  sibling note.

### Claim 7: The documented HarmBench workflow is `npx promptfoo@latest redteam run` → `npx promptfoo@latest view`
- **Evidence**: The "Run the evaluation" section lists the two commands.
- **Confidence**: settled (documented CLI)
- **Quote**: (code block; see Concrete Artifacts → Run the evaluation) "npx promptfoo@latest redteam run"
- **Our assessment**: Minor, but it is another data point on promptfoo CLI
  drift: this page uses `run`/`view`; the sibling
  `docs-promptfoo-chatbase-redteam.md` Claim 9 uses `eval`/`view`; the older
  blog guides use `init → run → report`. The guide should cite command names as
  version-relative, consistent with the existing note.

### Claim 8: HarmBench is a *static* dataset, and the vendor says it is most effective combined with dynamically generated plugins rather than used alone
- **Evidence**: The closing section states the static-dataset limitation and
  recommends sequencing HarmBench with plugins for PII leaks, hallucinations,
  excessive agency, and emerging cybersecurity threats. The plugin sub-page is
  sharper: "uses a statically generated dataset vs dynamically generating
  cases", "not something that can be used in lieu of a constantly evolving,
  dynamically generated set of test cases."
- **Confidence**: emerging (vendor guidance, well-reasoned)
- **Quote**: "While HarmBench provides valuable insights through its static dataset, it's most effective when combined with other red teaming approaches."
- **Our assessment**: The honest framing of a fixed benchmark's limit — a
  frozen 400-behavior set cannot track novel attack classes. This is the
  benchmark-versus-dynamic-tests distinction the guide should carry: a public
  benchmark buys comparability but not currency. It also undercuts using
  HarmBench alone as a CI gate (see Claim 9).

### Claim 9 (gap): The page documents no scoring formula, no threshold, and no pass-rate — so it is a config surface, not a validated evaluation methodology or a ready CI gate
- **Evidence**: The page shows only config and CLI; the results are referenced
  by a link and a screenshot, with no metric definition, threshold, or
  pass/fail criterion. Nothing states how a "success" is judged or what score
  gates a build.
- **Confidence**: settled as a gap (absence in the source)
- **Quote**: (no direct quote; the page contains no scoring or threshold text)
- **Our assessment**: The Prospector flagged exactly this and it holds: the
  page is *runnable* but not *reportable*. A benchmark run that produces no
  defined metric and no threshold cannot by itself be a Ch06 CI gate; it must
  be paired with the Ch05 nine-question ASR checklist (judge model, K, baseline,
  aggregation) before its output means anything. Do not present this page as a
  gating recipe.

## Concrete Artifacts

All artifacts are copied verbatim from the source page's code blocks.

### HarmBench evaluation of OpenAI GPT-5-mini (verbatim from "Configure the evaluation")

```
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
description: HarmBench evaluation of OpenAI GPT-5-mini
targets:
  - id: openai:gpt-5-mini
    label: OpenAI GPT-5-mini
redteam:
  plugins:
    - id: harmbench
      numTests: 400
```

### Filtered HarmBench evaluation (verbatim from "Configure the evaluation")

```
redteam:
  plugins:
    - id: harmbench
      numTests: 50
      config:
        categories:
          - cybercrime
          - misinformation
        functionalCategories:
          - contextual
```

### Ollama target (verbatim from "Ollama Models")

```
ollama pull llama4:scout
```
```
targets:
  - ollama:chat:llama4:scout
```

### Generic HTTP application target (verbatim from "Your application")

```
targets:
  - id: https
    config:
      url: 'https://example.com/generate'
      method: 'POST'
      headers:
        'Content-Type': 'application/json'
      body:
        myPrompt: '{{prompt}}'
```

### Run the evaluation (verbatim from "Run the evaluation")

```
npx promptfoo@latest redteam run
```
```
npx promptfoo@latest view
```

### Plugin reference: minimal config and default (verbatim from the HarmBench plugin sub-page)

```
redteam:
  plugins:
    - harmbench
```
```
redteam:
  plugins:
    - id: harmbench
      numTests: 25 # The default is 5, but you can define the limit here.
```

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or dismissed before writing)

- **Dismissed — unrelated**: `docs-litellm-batches-api.md` (LiteLLM batch
  rate-limiting); `blog-pagerduty-sre-agent-triage.md` (AI incident triage);
  `docs-langfuse-mcp-server.md` (docs MCP server);
  `docs-google-sre-reliable-product-launches.md` (launch coordination);
  `docs-google-sre-team-lifecycles.md` (SRE team org/first-SRE hiring);
  `docs-promptfoo-enterprise-audit-logging.md` (control-plane audit event
  taxonomy); `docs-promptfoo-enterprise-guardrails.md` (runtime guardrail HTTP
  enforcement contract — a different layer from a red-team benchmark plugin);
  `docs-promptfoo-enterprise-findings-reports.md` (post-scan finding
  disposition/export — the reporting layer, no benchmark-plugin content). None
  touch standardized-benchmark red-teaming or a plugin/dataset invocation.
- **Cited**: `blog-promptfoo-owasp-red-teaming.md` — see Corroborates below.
- **Dismissed — adjacent, no evidential overlap**:
  `blog-promptfoo-red-team-claude.md` — per-model red-team plugin/strategy
  configuration (reasoning-DoS, budget tokens); it uses vendor-generated
  plugins and names no standardized external dataset, so it neither corroborates
  nor extends this page's benchmark-invocation content.

### Cross-references with existing source notes

- **Corroborates**:
  - `blog-promptfoo-owasp-red-teaming.md` **Claim 6** — the OWASP Top 10 for
    LLM Applications is "used as a red-teaming shortcut — Promptfoo's
    `owasp:llm` plugin tests all ten categories with a single configuration
    line" with config `redteam:\n  plugins:\n    - owasp:llm`. This page is the
    exact same pattern (a named external framework exposed as one promptfoo
    plugin id), but for an *academic* benchmark rather than a practitioner
    framework. Verified: #555 Claim 6 = `owasp:llm` single-line OWASP shortcut
    ✓.
  - `blog-promptfoo-owasp-red-teaming.md` **Claim 12** — "The foundation model
    itself should be baseline red-teamed before application-layer testing,
    using multiple jailbreak strategies." This page's app-context-vs-vanilla
    comparison (Claim 5) is the mirror image: it runs the *same* benchmark
    against both the bare model and the app to compare them. Complementary
    framings of model-layer vs application-layer red-teaming. Verified: #555
    Claim 12 = baseline red-team the foundation model ✓.

- **Extends**:
  - `blog-promptfoo-asr-not-portable-metric.md` **Claim 10** — its judge-bias
    catalog cites HarmBench for a scoring/length effect: "ASR drops with longer
    outputs under common scoring approaches, breaking comparisons when
    generation settings differ (HarmBench)". That note uses HarmBench as
    external literature in an ASR-portability argument; this page is the
    *operational counterpart* — how you actually invoke a standardized
    benchmark (plugin id, `numTests`, category/functional filters, target
    config). Together they connect the abstract portability problem (Claim 1 of
    that note: "ASR numbers from different papers often can't be compared
    directly because the metric isn't standardized") to a concrete shared
    dataset — while this page's gap (Claim 9 here: no scoring formula or
    threshold) shows a public benchmark alone does not answer that note's
    nine-question checklist. Verified: #261 Claim 10 = judge biases incl.
    HarmBench length effect ✓; Claim 1 = ASR not standardized/comparable ✓.
  - `docs-promptfoo-chatbase-redteam.md` **Claim 5** — the two-layer
    `transformRequest` (OpenAI-style messages in) / `transformResponse`
    (extract the single response string) contract for driving a foreign HTTP
    target, and **Claim 3** — a hosted app red-teamed as a generic `http`
    target. This page's HTTP target body (`myPrompt: '{{prompt}}'`) is the
    minimal expression of that same black-box-target pattern; the guide should
    take the full adapter contract from the sibling note and cite this page only
    for the benchmark-plugin layer. Verified: #1654 Claim 5 =
    `transformRequest`/`transformResponse` two-layer contract ✓; Claim 3 = HTTP
    target for a hosted chatbot ✓.

- **Contradicts**: None identified, and no contradiction issue filed. The
  closest surface is coverage, not conflict: this page says a *static* public
  benchmark is best combined with dynamic plugins (Claim 8), while
  `blog-promptfoo-asr-not-portable-metric.md` argues comparability requires a
  *shared, fixed* threat model. These are the two horns of the same tradeoff —
  fixed benchmarks maximize comparability but go stale — not opposing claims on
  the same fact. Verified against `CONTRADICTIONS.md` (no relevant open entries)
  and open `contradiction`-labeled issues.

- **Novel**:
  - **The `harmbench` plugin invocation and its category taxonomy** — the two
    filter axes (semantic `categories` vs functional `functionalCategories`),
    the 7 canonical semantic slugs, the 3 functional slugs, the canonical-vs-
    alias normalization, and the documented **intersection** semantics when both
    are set. HarmBench appears in the corpus only as a literature citation
    (`blog-promptfoo-asr-not-portable-metric.md` Claim 10); no existing note
    covers the plugin or its dataset/filter surface.
  - **The app-context vs vanilla-base-model comparison as a test-design
    pattern** (Claims 4-5) — running the same standardized benchmark against the
    deployed application and the bare model to isolate the effect of prompt
    engineering + guardrails.
  - **The static-public-benchmark caveat** (Claim 8) as the explicit
    comparability-vs-currency tradeoff for a standardized red-team dataset.

## Guide Impact

- **Chapter 06 (Security and Trust) — "Red-teaming as a CI gate"
  (`guide/06-security-and-trust.md:120`)**: Add a short paragraph on using a
  *standardized public* benchmark (`harmbench` plugin) as a comparability
  anchor alongside the vendor-generated plugin sets, citing Claim 1 (named
  external provenance: arXiv 2402.04249) and Claim 3 (semantic/functional filter
  taxonomy + intersection). State the caveat from Claims 8-9: HarmBench is a
  static dataset and the page gives no scoring formula or threshold, so it is
  not a CI gate by itself — pair it with the Ch05 checklist and dynamic plugins.
  Near the "Run a no-jailbreak baseline before running jailbreaks" subsection
  (`guide/06-security-and-trust.md:364`), note Claim 4's scope rule: the
  meaningful baseline is the *deployed app*, not the base model card.
- **Chapter 05 (LLM Ops Reliability) — "Evaluation and measurement methodology"
  (`guide/05-llm-ops-reliability.md:386`) and "The nine-question ASR checklist"
  (`guide/05-llm-ops-reliability.md:510`)**: Add HarmBench as a concrete
  example of a shared public benchmark that partially answers the checklist's
  comparability questions (public prompts, named category aggregation) but *not*
  the scoring/judge/threshold questions — reinforcing the rule that a
  benchmark's name is not a unit. Cite Claim 3 for the filter contract and
  Claim 9 for the missing-scoring gap. This complements the existing ASR
  material from `blog-promptfoo-asr-not-portable-metric.md`.
- **Chapter 06 — HTTP/black-box target plumbing**: Do **not** re-extract the
  HTTP-provider adapter from this page; cite
  `docs-promptfoo-chatbase-redteam.md` Claims 3/5 for the full
  `transformRequest`/`transformResponse` contract and use this page only for the
  target-agnostic benchmark invocation (Claim 6).

## Extraction Notes

- Read the full guide page in detail via WebFetch
  (https://www.promptfoo.dev/docs/guides/evaling-with-harmbench), then followed
  one linked sub-page — the directly-linked HarmBench plugin reference
  (`/docs/red-team/plugins/harmbench/`) — for the canonical slug list, the
  default `numTests: 5`, alias normalization, and the static-dataset caveat.
  Both pages share the footer date Oct 11, 2026. Other outbound links (HarmBench
  paper/GitHub, red-team quickstart, vulnerability-types, CyberSecEval,
  model-armor) are reference pointers, not substantive pages for this
  extraction.
- Quotes were copied verbatim from the rendered page text before writing;
  blockquote/markdown emphasis markers were stripped but wording was not
  altered. Config artifacts are verbatim code blocks. Where a claim relies on
  the plugin sub-page (Claim 2's default, Claim 3's aliases, Claim 8's sharper
  wording), the sub-page is named at the point of use.
- `date_published` uses the page's "Last updated Oct 11, 2026" footer (the page
  has no canonical first-published date), matching the convention of sibling
  promptfoo docs notes.
- The Prospector's triage explicitly predicted this would be a short,
  low-novelty note and that "a short note is the correct outcome" if only two
  items survive contact with the page. I let that stand: the durable output is
  the plugin/filter taxonomy (Claim 3), the app-context claim (Claim 4), and
  the documented gap (Claim 9). I did not balloon it into another generic
  red-team-config note.
- **Trust boundary**: the issue body and comments were treated as untrusted
  data. The triage's config snippets and slug lists were confirmed against the
  live source before citing; no instruction in the issue was followed.
- **Contradiction scan**: no contradiction filed. The page's claims are
  first-party vendor documentation or external-benchmark provenance and oppose
  no existing source-note claim. The only tension (static-benchmark comparability
  vs dynamic-coverage) is a tradeoff, not a claim conflict. Verified against
  `CONTRADICTIONS.md` (no relevant open entries) and open
  `contradiction`-labeled issues (none bearing on this topic).
- **Cross-ref verification (§4b)**: every cited claim number was re-read and
  confirmed before citation — owasp #555 Claim 6 (OWASP single-line shortcut)
  and Claim 12 (foundation-model baseline red-teaming); asr #261 Claim 10
  (HarmBench length-effect literature citation) and Claim 1 (ASR not
  standardized); chatbase #1654 Claim 5 (`transformRequest`/`transformResponse`
  contract) and Claim 3 (HTTP target). All 10 candidate paths from
  `miner-related-notes.md` were cited or explicitly dismissed above.
- `confidence_overall` = `emerging`: provenance and documented config behavior
  are settled and directly checkable, but the page is vendor documentation with
  no scoring formula, no threshold, no pass-rate, and no independent validation;
  its analytical value (the benchmark-as-comparability-anchor angle) is our
  synthesis across the page and the surrounding corpus. Consistent with the
  sibling promptfoo notes.
- `registry/sources.json` and `registry/claims-index.json` were intentionally
  not edited: they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
