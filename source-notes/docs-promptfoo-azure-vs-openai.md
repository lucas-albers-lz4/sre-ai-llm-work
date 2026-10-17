---
source_url: https://www.promptfoo.dev/docs/guides/azure-vs-openai
source_type: docs
title: "OpenAI vs Azure: How to benchmark (promptfoo)"
author: "Promptfoo (vendor documentation)"
date_published: unknown (living docs page; last updated 2026-10-16 by renovate[bot])
date_extracted: 2026-10-17
last_checked: 2026-10-17
status: current
confidence_overall: anecdotal
issue: "#1642"
---

# OpenAI vs Azure: How to benchmark (promptfoo)

> A four-step promptfoo tutorial for benchmarking the same GPT model served by
> OpenAI direct vs Azure OpenAI. Its durable contributions are small but real:
> the provider-identity asymmetry in config (model slug vs Azure deployment
> name + `apiHost`), the vendor's own statement that outputs may differ between
> providers under identical configuration, the Azure model-cadence-lag and
> region-variation caveats, and the `--no-cache` timing-integrity rule for
> latency measurements. Its single quantitative datapoint (n=25, ~556 ms vs
> ~552 ms) is illustration, not a benchmark.

## Source Context

- **Type**: docs (promptfoo vendor documentation — "Model Comparisons" guide,
  page title "OpenAI vs Azure: How to benchmark").
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (site banner: now part of OpenAI). First-party tutorial documentation.
  The config surface and CLI flags are checkable product facts; the
  qualitative divergence claims (cadence lag, regional variation) are
  vendor prose with no supporting evidence on the page, and the single
  timing figure is the vendor's own illustrative run.
- **Scope**: Covers scaffolding a two-provider comparison (env vars, init
  example, provider YAML, prompt/tests, `eval --no-cache`, viewer review) and
  a short list of "key differences" axes. Does NOT cover API versions,
  throttling/quota or 429 behavior, error-handling differences, retries,
  timeouts, fallbacks, version pinning, or failure modes — the production
  concerns are entirely absent. The framing differences (speed, cost,
  compliance) are listed as prose, not measured.
- **Last updated**: Oct 16, 2026 by renovate[bot]; the page itself is undated.

## Extracted Claims

### Claim 1: Provider identity is asymmetric in config — OpenAI is referenced by model slug, Azure by deployment name plus a required `apiHost`, with separate API-key env vars
- **Evidence**: The page's provider YAML shows `openai:chat:gpt-5-mini` (a
  model slug) beside `azure:chat:my-gpt-5-mini-deployment` (an operator-chosen
  deployment name) with `config.apiHost`; prerequisites list `OPENAI_API_KEY`
  and `AZURE_API_KEY` as separate env vars.
- **Confidence**: settled (documented, checkable config surface)
- **Quote**: "Make sure to replace the above with the actual host and deployment name for your Azure OpenAI instances."
- **Our assessment**: Buy it. This is the page's most operationally citable
  artifact: the "same model" comparison already diverges at the config-identity
  layer — the Azure side names a *deployment*, not a model, so what is under
  test on the Azure side is whatever that deployment happens to point at
  (version pinning is the operator's job, and this page does not mention it).
  The asymmetry is real and worth recording; the page underplays its
  implication (see Claim 2).

### Claim 2: Outputs may differ between providers even with identical configurations, so accuracy and relevance must be validated per provider rather than assumed portable
- **Evidence**: Stated as the page's own finding in the results-analysis
  section, with the comparison viewer recommended as the checking tool.
- **Confidence**: anecdotal (vendor assertion with no measurement, no
  failure example, and no mechanism given on this page)
- **Quote**: "Interestingly, the outputs may differ between providers even with identical configurations."
- **Our assessment**: Buy the claim's direction — it is the standard
  non-determinism-plus-serving-stack reality, and the corpus has stronger
  evidence for provider divergence elsewhere (see Cross-References). But on
  this page it is a one-line aside with zero supporting data. Worth one rule
  in the guide ("validate assertions per provider; identical config does not
  imply identical outputs") backed by the corpus's stronger sources, not a
  standalone finding from this page.

### Claim 3: Azure tends to ship model updates more slowly than OpenAI direct, creating version gaps between the two providers
- **Evidence**: One bullet in the "key differences" list. No dates, no
  version numbers, no example of a lagging model on the page.
- **Confidence**: anecdotal (unevidenced vendor prose)
- **Quote**: "Frequency of model updates (Azure tends to move more slowly here) and therefore variation between models"
- **Our assessment directionally buy it — Azure OpenAI launch lag is a
  well-known industry pattern, and our corpus independently documents both
  faces of it (a prior GPT generation that was OpenAI-direct-only at launch,
  and a later generation that shipped with Azure at day zero). This page's
  value is as a *config-level* reminder that a parity comparison silently
  compares different model *versions* when the Azure deployment lags; the
  claim itself is weakly supported here.

### Claim 4: Latency varies between Azure regions, so a timing measured on one deployment is not a property of "Azure"
- **Evidence**: One bullet in the "key differences" list. No regional data
  on the page.
- **Confidence**: anecdotal (unevidenced vendor prose)
- **Quote**: "Variation in performance between Azure regions"
- **Our assessment**: Directionally buy — regional variation is expected for
  any hyperscaler — but this page supplies no numbers and its own benchmark
  (Claim 6) uses a single region, which undercuts any generalization. The
  operational rule the bullet implies (pin and report the region with any
  Azure latency figure) is the citable takeaway, not the bullet itself.

### Claim 5: When latency is the thing under test, the eval must run with `--no-cache` — cached results would invalidate timing data
- **Evidence**: The eval invocation in Step 3 carries `--no-cache`, with an
  explicit rationale sentence.
- **Confidence**: settled (documented vendor guidance, consistent with the
  promptfoo cache semantics documented elsewhere in the corpus)
- **Quote**: "We've added the `--no-cache` directive because we care about timings (in order to see which provider is faster), so we don't want any cached results."
- **Our assessment**: Buy it fully. This is a timing-integrity rule: a warm
  cache replays stored responses and their recorded latencies, so any
  latency-bearing eval run must opt out of the cache. The corpus already
  documents the cache mechanism in depth (default-on disk cache, `--no-cache`
  as the force-miss switch); this page is a clean worked instance of the
  measurement-hygiene consequence — citable as evidence that the vendor
  itself applies the rule when measuring speed.

### Claim 6: The page's only quantitative result — ~556 ms OpenAI vs ~552 ms Azure average over 25 examples ("negligible difference") — is a single illustrative run, not a benchmark
- **Evidence**: One worked example: 3 test-case prompts (weather, Mars
  news, sea poem) run across two providers; the viewer screenshot shows the
  averages. No repeats, no percentiles, no warmup policy, no statistical
  treatment, no disclosure of concurrency.
- **Confidence**: settled that the page reports this; anecdotal as a latency
  finding (n=25, single run)
- **Quote**: "In this particular test run over 25 examples, it shows that there is negligible difference in speed of inference - OpenAI and Azure take 556 ms and 552 ms on average, respectively."
- **Our assessment**: Do not carry this number forward as a latency finding —
  the Prospector's triage caveat applies (anecdote, not benchmark). Its only
  legitimate use is as an illustration of what the comparison view surfaces,
  and as a negative example of incomplete timing methodology (no percentile,
  no repeat count, no region named) against which the guide's
  measurement-hygiene rules can be stated. Note also the mild tension on the
  page itself: the intro promises "key differences" in inference speed, and
  the only measured result is "negligible difference."

## Concrete Artifacts

### Provider configuration (verbatim from Step 1)

```yaml
providers:
  - id: openai:chat:gpt-5-mini
  - id: azure:chat:my-gpt-5-mini-deployment
    config:
      apiHost: myazurehost.openai.azure.com
```

### Environment variables (verbatim from Prerequisites; line breaks restored from the rendered page)

```
export OPENAI_API_KEY='...'
export AZURE_API_KEY='...'
```

### Scaffold and run commands (verbatim from Steps 1 and 3)

```
npx promptfoo@latest init --example openai-azure-comparison
cd openai-azure-comparison
```

```
npx promptfoo@latest eval --no-cache
```

### Prompts and test cases (verbatim from Step 2)

```yaml
prompts:
  - 'Answer the following concisely: {{message}}'
tests:
  - vars:
      message: "What's the weather like in Paris today?"
  - vars:
      message: 'Summarize the latest news on Mars exploration.'
  - vars:
      message: 'Write a poem about the sea.'
```

### The "key differences" list (verbatim from the page intro)

- Speed of inference
- Frequency of model updates (Azure tends to move more slowly here) and therefore variation between models
- Variation in performance between Azure regions
- Cost
- Ease of integration
- Compliance with data regulations

Source for all artifacts: https://www.promptfoo.dev/docs/guides/azure-vs-openai — sections as noted. Code blocks re-flowed only at the newline level (the HTML extraction collapses line breaks); no wording changes.

## Cross-References

**Candidates from `miner-related-notes.md` (cited/dismissed):**
- `source-notes/docs-promptfoo-evaluate-coding-agents.md` — **Cited** (Corroborates, Claim 2): "The same underlying model behaves differently at each tier" — an eval-scoping taxonomy in which the serving surface, not just the model, is part of what is under test. This page is the provider-dimension instance of the same principle (same model slug-era GPT, two serving providers, outputs may differ). Different mechanism (capability tier vs provider parity) but the same guide-relevant rule: pin the surface, validate per surface.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — dismissed: assertion-type taxonomy (deterministic vs model-graded line); no provider-parity or latency content.
- `source-notes/docs-promptfoo-llm-rubric.md` — dismissed for cross-ref purposes: mentions Azure only as one entry in the default-judge provider roster; no parity or benchmarking surface.
- `source-notes/docs-promptfoo-enterprise-guardrails.md`, `docs-promptfoo-enterprise-findings-reports.md`, `docs-promptfoo-pi-scorer.md` — dismissed: enterprise red-team surfaces, unrelated to provider comparison.
- `source-notes/docs-litellm-batches-api.md` — dismissed: batch rate-limit accounting at the gateway; unrelated.
- `source-notes/docs-google-sre-team-lifecycles.md` — dismissed: SRE org/workflow chapter; unrelated.
- `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — dismissed: Python agent SDK tracing bridge; unrelated.
- `source-notes/blog-pagerduty-sre-agent-triage.md` — dismissed: AI incident triage; unrelated.

**Additional cross-references (searched `source-notes/` and via Prospector triage):**
- **Corroborates**:
  - `source-notes/blog-litellm-gpt-5-6-sol-terra-luna-day-0.md` **Claim 3** — the LiteLLM GPT-5.6 day-0 post documents that the *previous* generation (GPT-5.5) was "OpenAI direct only" at launch while GPT-5.6 shipped with Azure availability on day zero. This is independent corpus evidence for the Azure cadence lag this page asserts in prose (Claim 3) — including the counter-case that the lag is not constant. (Verified: Claim 3 quote "Azure availability: not yet — this post covers OpenAI direct only" re GPT-5.5.)
  - `source-notes/docs-promptfoo-configuration-rate-limits.md` **Claim 7** — rate-limit tracking is "header-driven and per-provider *and* per-API-key, with a documented header table for OpenAI, Anthropic, Azure OpenAI, and a generic fallback" — an independent, substantive instance of Azure-vs-OpenAI operational asymmetry in the same tool. (Verified: Claim 7 heading.)
- **Extends**:
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 9** (the `--no-cache` / `PROMPTFOO_CACHE_ENABLED` disable surface) and **Claim 11** ("You can force a cache miss in two ways: Pass `--no-cache` to the CLI...") — that note is the vendor reference for the cache mechanism; this page is a worked instance of the measurement-hygiene *consequence*: a latency-bearing comparison must disable the cache, because replayed responses carry replayed timings. Same tool, applied-use layer. (Verified: Claims 9 and 11.)
  - `source-notes/docs-litellm-provider-specific-params.md` **Claim 3** — provider parameter-name divergence (`max_tokens` vs `num_predict` vs ...) across providers behind a common gateway. This page adds the eval-harness-level analog: the *provider identity itself* is expressed differently (model slug vs deployment name + host), so "the same model on two providers" is never a config-copy operation. (Verified: Claim 3.)
  - `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` **Claim 1** — the guide's Ch05 "Provider parity in the shared forwarding path" section is built on that failure: a gateway normalization validated against OpenAI's SDK broke the stricter vLLM sibling. This page is the benign face of the same family (an eval tutorial comparing two providers), and its Claim 2 ("outputs may differ... even with identical configurations") is the vendor-level statement of the hazard that failure proves at the wire level. Complementary, not competing. (Verified: Claim 1.)
- **Novel**: First corpus source on **provider-parity benchmarking itself** — the pattern "run the same model through two providers side-by-side in an eval harness" as a deliberate measurement design, plus two first-in-corpus details: (a) the promptfoo config-shape asymmetry for Azure (deployment name + required `apiHost` rather than a model slug, Claim 1 / Concrete Artifacts), and (b) the `--no-cache`-for-latency timing-integrity rule stated by the vendor as rationale (Claim 5). No existing note covers this page's subject; the overlapping promptfoo notes cover caching, rate limits, scenarios, and outputs as separate config surfaces.

**Contradicts**: None identified. Claim 2 (outputs may differ across providers) is consistent with — and materially weaker than — the corpus's existing provider-divergence evidence (the vLLM embedding failure); no existing note claims the opposite (that identical config implies portable outputs). Claim 6's "negligible difference" result does not contradict any corpus latency claim: no other note asserts an OpenAI-vs-Azure latency gap. Verified against `CONTRADICTIONS.md` and existing notes; no contradiction issue filed.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — §Provider parity in the shared forwarding path**: That section currently frames provider parity as a wire-level hazard through a gateway (the vLLM embedding failure). Add a short companion rule from the eval side: when the same model is served by two providers (e.g., OpenAI direct vs Azure OpenAI), **identical configuration does not imply identical outputs** — validate accuracy/relevance assertions per provider (Claim 2, corroborated by the stronger vLLM case), and remember the Azure side is pinned to a *deployment name* that may lag the OpenAI-side model version (Claims 1, 3). Do not cite this page's timing numbers.
- **Chapter 05 — §Evaluation and measurement methodology**: Add the timing-integrity rule: **latency-bearing eval runs must disable the cache** (`promptfoo eval --no-cache`), because cached replays invalidate timing data (Claim 5), with the cache-mechanism detail delegated to the caching note. Optionally note the negative example: the page's own n=25 single-region, single-run average (Claim 6) lacks percentiles, repeats, and region disclosure — the absence list the guide's latency-measurement guidance should mandate.
- **Chapter 02 (Observability) — measurement hygiene (secondary)**: The "metrics without a unit are noise" discipline gains a provider dimension: a latency figure should carry provider, region, and cache state, not just a number — motivated by Claims 4-6 (region variation is a listed difference axis; the page's own run names none of these dimensions).

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page (single
  self-contained tutorial; no substantive sub-pages followed — the "Next
  steps" link points to the assertions docs, covered by other corpus notes,
  and the sibling model-comparison guides are separate leaf pages filed as
  their own issues). Quotes verified character-for-character against the
  fetched rendered content; code blocks re-flowed only at newline level (the
  HTML extraction collapses line breaks) — no wording changes.
- Per Prospector triage (three runs, all agreeing the page is thin): the
  single 25-example timing datapoint was extracted **as an anecdote and
  explicitly fenced off** from use as a latency finding (Claim 6); the
  "key differences" list is treated as framing, with only the Azure-cadence
  and region-variation bullets carried as claims, both marked anecdotal.
  No API versions, rate limits, retry/timeout/fallback guidance, or failure
  modes exist on the page — their absence is recorded in Scope rather than
  inferred.
- `confidence_overall` is `anecdotal`: the two durable, checkable artifacts
  (config identity asymmetry, Claim 1; `--no-cache` timing rule, Claim 5)
  are settled for vendor product surface, but the page's distinctive
  substantive claims (output divergence, cadence lag, region variation,
  Claims 2-4) are unevidenced vendor prose and its only number is an n=25
  illustrative run. The page's body of evidence does not rise to `emerging`.
- `date_published` uses the page's "Last updated on Oct 16, 2026" footer
  (page is undated; renovate[bot] bumps are content-neutral).
- Duplicate check: parent hub page `https://www.promptfoo.dev/docs/guides`
  was rejected as issue #1641 (link directory); this is a distinct leaf URL.
  No existing source note covers Azure-vs-OpenAI benchmarking (searched
  `source-notes/` for azure/parity/deployment-name patterns).
- No contradiction issue filed (see Cross-References). I did NOT edit
  `registry/sources.json` or `registry/claims-index.json` (derived indexes,
  rebuilt after merge).
