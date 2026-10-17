---
source_url: https://www.promptfoo.dev/docs/guides/hle-benchmark
source_type: docs
title: "Promptfoo Guide: Testing Humanity's Last Exam (HLE) with Promptfoo — Small-Sample Eval, LLM-as-Judge Grading, and Comparability Disclaimers"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-16
date_extracted: 2026-10-16
last_checked: 2026-10-16
status: current
confidence_overall: emerging
issue: "#1755"
---

# Promptfoo Guide: Testing Humanity's Last Exam (HLE) with Promptfoo

> A vendor-run demonstration of running Scale AI/CAIS's Humanity's Last Exam benchmark via promptfoo, explicitly documenting sampling fragility (50 of 3,000+ questions, single run), comparability limitations (harness numbers differ from the official leaderboard), measured cost/latency/tokens per model, LLM-as-judge grading via `llm-rubric`, multi-provider image formatting, and the unpriced judge-dependency in the reported numbers.

## Source Context

- **Type**: docs (vendor product guide — promptfoo `/docs/guides/hle-benchmark`, discovered from the registered `promptfoo-docs` site-crawl seed)
- **Author credibility**: Promptfoo (commercial LLM eval/red-team vendor). First-party documentation describing how to run the HLE example and sharing a single-run demonstration; the page explicitly presents the reported numbers as a demonstration and caveats their limitations rather than as a leaderboard submission. Footer: "Last updated on Oct 16, 2026 by renovate[bot]".
- **Scope**: Covers what HLE is (Scale AI/CAIS, 1000+ experts, benchmark saturation rationale), running the example (`npx promptfoo@latest init --example huggingface/hle` etc.), API keys (OpenAI/Anthropic/HF), the demo results for Claude 4 vs o4-mini on 50 questions each, prompt engineering for multimodal inputs (provider-specific image formatting), automated grading via `llm-rubric`, customization options (thinking tokens, max_tokens, sampling), explicit limitations, and implications. The page does not claim CI gating or present a full-corpus run; it positions itself as a "how to" with a concrete small-sample run. What the page documents **not at all** — CI exit-code/threshold configuration, retry/timeout/rate-limit handling, seed control, and cross-run variance — is enumerated in the **Limitations** section below.
- **Followed sub-pages**: None required beyond the main guide page. Outbound links (arXiv, HuggingFace dataset, Scale AI leaderboard, etc.) are references; the substantive measured content is on this page.

## Extracted Claims

### Claim 1: HLE is framed as a response to benchmark saturation — designed to be more challenging because models exceed 90% on MMLU, with characteristics including 100+ subjects, 14% multimodal questions, resistance to simple web search, and verifiable closed-ended problems
- **Evidence**: Introductory paragraphs naming Scale AI/CAIS, the benchmark-saturation rationale, and key characteristics.
- **Confidence**: settled (external benchmark provenance)
- **Quote**: "Humanity's Last Exam (HLE) is a challenging benchmark commissioned by Scale AI and the Center for AI Safety (CAIS), developed by 1,000+ subject experts from over 500 institutions across 50 countries."
- **Quote**: "Created to address benchmark saturation where current models achieve 90%+ accuracy on MMLU, HLE presents genuinely difficult expert-level questions that test AI capabilities at the frontier of human knowledge."
- **Our assessment**: This establishes the benchmark's purpose and design; it is vendor's framing of the external benchmark, not a measured claim. Useful as context, not a measurement claim.

### Claim 2: The page explicitly disclaims comparability to the official leaderboard — the demo numbers differ from official benchmarks due to prompting strategy, token budgets, question sampling
- **Evidence**: The Eval Results section states this disclaimer immediately before showing the demo results.
- **Confidence**: settled (first-party admission)
- **Quote**: "Note that our results differ from official benchmarks due to different prompting strategies, token budgets, and question sampling."
- **Our assessment**: A critical methodological disclaimer. This is the vendor documenting its own comparability weakness — the harness number ≠ leaderboard number. This generalizes to any eval-gated release and is directly citable as a caution.

### Claim 3: The demo uses small-N single-run sampling — 50 questions per model (100 total), single run, from HLE's 3,000+ questions, and explicitly calls the results "preliminary" with arbitrary choices requiring validation
- **Evidence**: Eval Results section gives sample sizes; Limitations section restates fragility.
- **Confidence**: settled (explicit admission)
- **Quote**: "Keep in mind these results are preliminary - we only tested 50 questions per model in a single run. That's a pretty small sample from HLE's 3,000+ questions, and we didn't optimize our approach much (token budgets, prompts, etc. were chosen somewhat arbitrarily)."
- **Quote**: "o4-mini's 42% success rate stands out and requires validation through larger samples and multiple runs. Performance will likely vary considerably across different subjects and question formats."
- **Our assessment**: The strongest fragility admission. The vendor self-ratifies that small-N single-run evals are not conclusive — useful counter-example for gating criteria.

### Claim 4: The page forwards official leaderboard numbers (as of early 2026) as a pointer, not independently measured evidence — the table attributes numbers to Scale AI leaderboard
- **Evidence**: About section includes a table titled "Model performance as of early 2026. See the Scale AI leaderboard for current results:" followed by the table.
- **Confidence**: settled (attribution)
- **Quote**: "Model performance as of early 2026. See the [Scale AI leaderboard](https://scale.com/leaderboard/humanitys_last_exam) for current results:"
- **Our assessment**: The page correctly treats third-party leaderboard data as external reference, not as measurements from this run. This is good attribution hygiene.

### Claim 5: The demo reports concrete measured cost/latency/tokens for each model (50 questions each) and aggregate run metrics
- **Evidence**: Performance summary and per-model table in Eval Results.
- **Confidence**: emerging (single-run vendor measurements)
- **Quote**: "Performance summary (50 questions per model, 100 total test cases):\n- Combined pass rate: 28% (28 successes across both models)\n- Runtime: 9 minutes with 20 concurrent workers\n- Token usage: Approximately 237K tokens for 100 test cases"
- **Quote**: "| Model | Success Rate | Token Usage | Total Cost (50 questions) | Avg Latency |\n|---|---|---|---|---|\n| o4-mini | 42% (21/50) | 139,580 | $0.56 | 17.6s |\n| Claude 4 | 14% (7/50) | 97,552 | $1.26 | 28.8s |"
- **Our assessment**: Harvestable as an illustrative run shape (Ch05), **not** as an eval-budget baseline. These are measured run-shape figures (sample → tokens → cost → latency → concurrency) with a single-run provenance: the page flags them as preliminary, and — the load-bearing point — they are **variance-free**. The page reports exactly one run (Claim 3: "we only tested 50 questions per model in a single run"), so 9 minutes / 237K tokens / 17.6s / 28.8s carry no cross-run dispersion whatsoever; the page documents no repeat count, no per-run spread, and no seed control (see Limitations below). A reader must not generalise this run shape into a budget estimate without that caveat.
- **Naming reconciliation**: the results table names the evaluated Anthropic model "Claude 4", while the Customization Options section (Claim 6) names the linked example's model "Claude Sonnet 4.6"; the leaderboard table (Claim 4) separately lists "Claude Sonnet 4" (5.5%) and "Claude Opus 4.6 (Thinking Max)" (34.4%). The page never states that the demo's "Claude 4" row is the same model as the example's "Claude Sonnet 4.6" — treat them as one demo entry rather than two models, but note the page's naming is inconsistent across its own tables.

### Claim 6: Token budgets and reasoning configuration are documented as levers — example uses 3K thinking tokens for Claude Sonnet 4.6 and 4K max tokens total; also shows adaptive thinking with `effort: xhigh` and `max_tokens: 12000` for Claude Sonnet 5
- **Evidence**: Customization Options section.
- **Confidence**: settled (documented config)
- **Quote**: "- **3K thinking tokens (Claude)**: The linked example uses a 3,000-token thinking budget on Claude Sonnet 4.6\n- **4K max tokens**: The example's output budget, including Claude's thinking tokens"
- **Quote**: "For Claude Sonnet 5, use adaptive thinking with `effort`:\n```yaml\nproviders:\n  - id: anthropic:claude-sonnet-5\n    config:\n      thinking:\n        type: adaptive\n      effort: xhigh # For complex proofs\n      max_tokens: 12000\n```"
- **Our assessment**: Documents the levers and their config surface. The page also notes "token budget increases alone don't guarantee accuracy improvements" (Claim 10) — a falsifiable, extractable caution.

### Claim 7: Grading is LLM-as-judge via the built-in `llm-rubric` assertion with a 0.0–1.0 scale; it does not require exact string matches and accounts for equivalent formats
- **Evidence**: Automated Grading section with rubric text and assertion config.
- **Confidence**: settled (documented mechanism)
- **Quote**: "Promptfoo uses LLM-as-a-judge for automated grading with the built-in `llm-rubric` assertion. This approach evaluates model responses against the expected answers without requiring exact string matches."
- **Quote**: "Grade the response on accuracy (0.0 to 1.0 scale):\n- 1.0: Response matches the correct answer exactly or is mathematically/logically equivalent\n- 0.8-0.9: Response is mostly correct with minor differences that don't affect correctness\n- 0.5-0.7: Response is partially correct but has significant errors\n- 0.0-0.4: Response is incorrect or doesn't address the question"
- **Our assessment**: Explicitly identifies grading as LLM-as-judge (second model involved). The rubric shows continuous scoring. This is the judge dependency (unpriced) noted in Prospector triage.

### Claim 8: There is an unpriced judge dependency — grading uses LLM-as-judge (`llm-rubric`) but the reported cost/latency/tokens in the demo tables only cover the evaluated models (o4-mini and Claude 4), not the judge model's cost
- **Evidence**: Demo cost table lists "Total Cost (50 questions)" per evaluated model only; no judge cost shown. Grading is described as separate via `llm-rubric` assertion.
- **Confidence**: emerging (inference from reported scope; page does not itemize judge cost)
- **Quote**: none — this is an inference from the *absence* of a judge line item in the reported cost table (Claim 5); the page never states that judge cost is excluded, so there is no passage to quote. See `Our assessment` for the reasoning.
- **Our assessment**: The page reports judge is used, but never states judge identity or its cost. This is a concrete gap: the per-model costs ($0.56, $1.26) are for generation only, not total eval cost. Worth recording as a caution.

### Claim 9: Multi-provider image formatting is handled via custom Python — OpenAI uses `image_url` format while Anthropic/Claude requires base64 `source` format; also uses `developer` role for o1/o3 reasoning models
- **Evidence**: Prompt Engineering for HLE section.
- **Confidence**: settled (documented implementation detail)
- **Quote**: "To handle images across different AI providers, we wrote a custom prompt function in Python. OpenAI uses `image_url` format while Anthropic/Claude requires base64 `source` format."
- **Quote**: "- **OpenAI models**: Uses `image_url` format for images, `developer` role for o1/o3 reasoning models\n- **Anthropic models**: Converts images to base64 `source` format for Claude compatibility"
- **Our assessment**: Documents portability cost of multi-provider eval harness — concrete operational detail.

### Claim 10: The page states "token budget increases alone don't guarantee accuracy improvements" as a falsifiable caution
- **Evidence**: Implications section (bullet list), under "Key findings".
- **Confidence**: emerging (the sentence is stated plainly and verbatim on the page, but it is an empirical generalization drawn from one 50-question-per-model single run — the same run Claim 3 records the page flagging as "preliminary" and as requiring "validation through larger samples and multiple runs". The page offers no per-model token/accuracy comparison to support it.)
- **Quote**: "- Token budget increases alone don't guarantee accuracy improvements"
- **Our assessment**: Extractable as a caution tied to reasoning budgets, but graded `emerging` rather than `settled` precisely because its evidentiary base is the demo's own single small run: it is a stated lesson, not a demonstrated result. Use it in the guide as a hypothesis to test per model, not as a measured law.

### Claim 11: The demo is runnable via the shipped example; the page gives concrete config snippets including test selection and provider configuration
- **Evidence**: Running the Eval and Customization Options sections with commands and YAML.
- **Confidence**: settled (documented)
- **Quote**: "Set up your HLE eval with these commands:\n```\nnpx promptfoo@latest init --example huggingface/hle\ncd huggingface/hle\nnpx promptfoo@latest eval\n```"
- **Quote**: "Test more questions:\n```yaml\ntests:\n  - huggingface://datasets/cais/hle?split=test&limit=200\n```"
- **Our assessment**: Concrete runnable artifacts; confirms this is a product example, not just conceptual guidance.

## Concrete Artifacts

### Running the eval (verbatim)
```bash
npx promptfoo@latest init --example huggingface/hle
cd huggingface/hle
npx promptfoo@latest eval
```

### API keys
- `OPENAI_API_KEY` - for o4-mini and GPT models
- `ANTHROPIC_API_KEY` - for Claude 4 with thinking mode
- `HF_TOKEN` - get yours from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Performance summary (verbatim)
```
Performance summary (50 questions per model, 100 total test cases):
- Combined pass rate: 28% (28 successes across both models)
- Runtime: 9 minutes with 20 concurrent workers
- Token usage: Approximately 237K tokens for 100 test cases
```

### Per-model table (verbatim)
| Model | Success Rate | Token Usage | Total Cost (50 questions) | Avg Latency |
|---|---|---|---|---|
| o4-mini | 42% (21/50) | 139,580 | $0.56 | 17.6s |
| Claude 4 | 14% (7/50) | 97,552 | $1.26 | 28.8s |

### llm-rubric grading (verbatim excerpt)
```yaml
defaultTest:
  assert:
    - type: llm-rubric
      value: |
        Evaluate whether the response correctly answers the question.
        Question: {{ question }}
        Model Response: {{ output }}
        Correct Answer: {{ answer }}
        Grade the response on accuracy (0.0 to 1.0 scale):
        - 1.0: Response matches the correct answer exactly or is mathematically/logically equivalent
        - 0.8-0.9: Response is mostly correct with minor differences that don't affect correctness
        - 0.5-0.7: Response is partially correct but has significant errors
        - 0.0-0.4: Response is incorrect or doesn't address the question
        The response should pass if it demonstrates correct understanding and provides the right answer, even if the explanation differs from the expected format.
```

### Thinking/token budget example (verbatim)
```yaml
providers:
  - id: anthropic:claude-sonnet-5
    config:
      thinking:
        type: adaptive
      effort: xhigh # For complex proofs
      max_tokens: 12000
```

### Provider config with DeepSeek thinking (verbatim)
```yaml
providers:
  - anthropic:claude-sonnet-5
  - openai:o4-mini
  - id: deepseek:deepseek-flash
    config:
      max_tokens: 8192
      passthrough:
        thinking:
          type: enabled
```

### System/user prompt structure (verbatim)
```yaml
- role: system
  content: |
    Your response should be in the following format:
    Explanation: {your explanation for your answer choice}
    Answer: {your chosen answer}
    Confidence: {your confidence score between 0% and 100% for your answer}
- role: user
  content: |
    Which condition of Arrhenius's sixth impossibility theorem do critical views violate?

    Options:
    A) Weak Non-Anti-Egalitarianism
    B) Non-Sadism
    C) Transitivity
    D) Completeness
```

## Limitations — What This Page Does Not Cover

The Prospector's triage explicitly required that this page not be citable as a
CI-gating recipe. A full read of the page confirms the following absences; each
is a *verified absence* (a full-page read with no matching content), not merely
an unquoted passage:

- **No CI exit-code or threshold configuration.** The only run commands on the
  page are `npx promptfoo@latest init --example huggingface/hle`,
  `npx promptfoo@latest eval`, and `npx promptfoo@latest view` (Claim 11). No
  pass/fail threshold, no exit-code semantics, and no CI wiring appear anywhere.
  A pass rate is *reported* (Claim 5) but never *gated* on — there is no
  documented way on this page to fail a build on HLE results.
- **No retry, timeout, or rate-limit handling.** The page's entire statement on
  execution behavior is "Promptfoo handles dataset loading, parallel execution,
  cost tracking, and results analysis automatically." Concurrency appears only
  as a reported run-shape fact ("9 minutes with 20 concurrent workers", Claim 5)
  — nothing on the page documents a concurrency ceiling, a retry policy, backoff
  behavior, or a request timeout. This is the gap the rate-limits cross-reference
  below fills from the vendor's sibling page.
- **No seed control.** No `seed`, determinism, temperature, or repeat setting
  appears in the page's body content.
- **No cross-run variance.** Every reported figure comes from a **single run**
  (Claim 3). There is no repeat count, no per-run spread, no run-to-run p50/p95
  — Claims 3 and 5 hand the reader a run shape (sample size, token usage, cost,
  latency, concurrency) with no dispersion data behind it at all. The Claim 5
  run shape is therefore labelled variance-free throughout this note.
- **No full-corpus run and no leaderboard comparability.** Sampling is 50 of
  HLE's 3,000+ questions per model, and the page explicitly disclaims
  comparability to official benchmarks (Claim 2). The leaderboard table is
  forwarded third-party data, not a measurement from this run (Claim 4).

**Consequence:** this note records what a small-sample vendor demonstration
reported. It is not a gating recipe and not an eval-budget baseline, and the
Smith should not synthesize it as either.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-harmbench.md` — same shape (vendor product docs for running a standardized benchmark via promptfoo plugin/config). Both emphasize config surface and limitations of what the page demonstrates (Harmbench notes static dataset limits; HLE notes sampling fragility/comparability).
  - `source-notes/docs-litellm-benchmarks.md` — **Claim 6** and **Claim 9**, the same methodological shape as this note's Claim 2 comparability disclaimer and its concurrency-dependent latency figures. Claim 6 is the sibling non-universality disclaimer (its quote: "The in-process mock model excludes provider latency. These results measure gateway capacity for this specific traffic shape and should not be treated as universal production sizing guidance.") — the same move this page makes with "our results differ from official benchmarks due to different prompting strategies, token budgets, and question sampling" (this note's Claim 2). Claim 9 supplies the missing interpretation rule for this note's Claim 5 latencies measured at concurrency 20: latency tracks in-flight concurrency rather than being an independent property of the model, and (its quote) "Latency and concurrency are not independent, and neither number means anything without the other." So the 17.6s / 28.8s average latencies in this note's Claim 5 table are not model-level latency properties — they are properties of a run with 20 concurrent workers, and the LiteLLM note is the corpus's explicit statement of that rule. Both are vendor self-benchmarks whose own pages defuse the obvious misuse. (Verified: read the note's Claims 6 and 9 in full.)
  - `source-notes/docs-promptfoo-choosing-best-gpt-model.md` — **Claim 1** and **Claim 7**, the direct sibling of this note's Claim 3 fragility point from the same vendor-docs family. Claim 1 holds that public leaderboard scores are inadequate for app decisions (its quote: "New model releases often score well on benchmarks. But generic benchmarks are for generic use cases."), the general form of what this page does concretely: it forwards the Scale AI leaderboard as a pointer (this note's Claim 4) while disclaiming that its own harness numbers are comparable to it (this note's Claim 2). Claim 7 documents the thin-evidence disclaimer pattern (small test set, placeholder thresholds, its quote: "Of course, this is a limited example test set.") — the mirror of this note's Claim 3, where the vendor calls its own 50-question single run "preliminary" and says the 42% figure "requires validation through larger samples and multiple runs". Two promptfoo guide pages in the corpus independently self-flag thin evidence; that convergence is itself citable. (Verified: read the note's Claims 1 and 7 in full.)
  - `source-notes/docs-promptfoo-evaluate-osworld-with-inspect.md` — strong methodological parallel on denominator/hygiene. The three-state result model is *that* note's, not this page's: its Claim 3 documents the provider's `score >= 1.0` / `score < 1.0` / provider `error` taxonomy, and its Claim 4 the rule that collapsing provider errors into failures corrupts the score. This page has no such state model; what it shares is the "the number you publish is not the number a leaderboard publishes" discipline (its Claim 2 disclaimer vs that note's Claims 5/6 publication rule). Also both give concrete measured run-shape figures (tokens/cost/time/concurrency — that note's Claim 9) and explicit caveats about generalizing numbers. (Verified: read OSWorld Claims 3, 4, 5, 6 and 9.)

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-rate-limits.md` — **Claim 5's run shape depends on this note, and this note is where the "no retry/timeout/rate-limit handling" gap lands.** This page reports "9 minutes with 20 concurrent workers" (Claim 5) as a bare run-shape fact and documents nothing about how that concurrency is governed. That note documents the mechanism: `maxConcurrency` is a *ceiling*, not a setting — its **Claim 5** states (its quote) "The adaptive scheduler will reduce this if rate limits are encountered, but cannot exceed your configured maximum.", so realized concurrency is state-dependent and per-provider, and eval wall-clock is not derivable from the configured number. Its **Claim 3** documents the AIMD controller that produces that variance (halve concurrency on a rate-limit hit, +1 after sustained success, proactive cut below 10% remaining quota). Consequence for this note's Claim 5 figures: "9 minutes at 20 concurrent workers" is the *observed* concurrency of one run, not a configured rate — the same config can run narrower and slower on a throttled day, so the runtime figure is as variance-free as the accuracy figures (see Limitations). That note also carries the retry/timeout surface this page entirely omits (its two retry layers and its 300-second scheduler queue timeout, Claim 11), which is the documented answer to the "no retry/timeout/rate-limit handling" absence recorded here. (Verified: read the note's Claims 3 and 5 in full, plus its Claim 11 for the queue timeout.)
  - `source-notes/docs-promptfoo-llm-rubric.md` (and related model-graded notes) — extends the `llm-rubric` concept by applying it to a closed-ended public benchmark with a concrete 0.0-1.0 rubric tailored to mathematical/logical equivalence. (The rubric here is specific to HLE's grading needs.)
  - `source-notes/docs-promptfoo-configuration-huggingface-datasets.md` — **Claim 11's runnable artifact depends on this note.** The "Test more questions" snippet (`tests: - huggingface://datasets/cais/hle?split=test&limit=200`, Claim 11) is a `huggingface://datasets/` test source, so the 200 HLE questions are fetched live from `cais/hle` at eval time. That note's Claim 2 establishes the prefix's whole knob surface is `split`/`config`/`limit` with **no revision or commit pin at either layer**, which means the HLE example's inputs are non-hermetic and not even pinnable in place — a fifth failure mode for this note's small-sample fragility point (Claims 3, 5): not only are 50 questions a small sample, the 200-question "scale up" is a mutable third-party reference. Two further properties from that note attach to this snippet: its Claim 3 documents that rows arrive 100 per request over the dataset-viewer `/rows` API (so `limit=200` is a two-page remote fetch), and its Claim 5 that a wrong or absent `split`/`config` yields **zero** test cases with no error. (Verified: read huggingface-datasets Claims 2, 3 and 5.)
  - `source-notes/docs-promptfoo-model-graded-closedqa.md` — a related grading alternative for the closed-ended shape this note describes. This note's Claim 1 records HLE's "verifiable, closed-ended problems", and its Claim 7 documents the page's chosen grader: `llm-rubric` on a continuous 0.0–1.0 scale. That note's Claim 1 documents the opposite granularity available in the same assert family — `model-graded-closedqa` returns `Y`/`N` by string-suffix parse with no `threshold` of its own, and its Claim 7 notes the per-assert `value:` is one binary criterion, with gating pushed up to the row-level `threshold`. For HLE-style closed-ended items that is a cheaper (one bit, one judge call) alternative to this page's rubric, and the trade is the graded-partial-credit scale vs the binary parse. (Verified: read model-graded-closedqa Claims 1 and 7.)

- **Contradicts**: None identified; no contradiction issue filed. The page's claims are self-consistent and include appropriate disclaimers.

- **Novel**:
  - The first source note covering promptfoo's HLE benchmark guide. No existing note covers HLE or the specific cost/latency breakdown for o4-mini vs Claude 4 on this example. The explicit first-party admission that small-N single-run results "require validation via larger samples and multiple runs" paired with concrete numbers is the key novel extraction.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add guidance about small-sample honesty — when reporting benchmark results, document sample size relative to full corpus (50/3000+), single vs multiple runs, and comparability to official leaderboards. Cite Claims 2, 3 as concrete examples of vendor self-disclosure. Also add that eval costs should account for judge (llm-rubric) cost which may not be itemized in per-model generation costs (Claim 8).
- **Chapter 05 — do not cite this page as a CI-gating recipe.** Add as a counter-example: a vendor guide that publishes a pass rate (28% combined, Claim 5) with **no** threshold, exit-code semantics, or CI wiring anywhere on the page, and with no retry/timeout/rate-limit handling, no seed control, and no cross-run variance (see Limitations). Use it to make the rule concrete that "reported" is not "gated" and "single run" is not "measured baseline".
- **Chapter 05 (Cost, capacity, and fallback patterns)**: Incorporate the concrete run-shape numbers as an illustrative example (237K tokens for 100 cases, 9 min at 20 concurrent workers), **explicitly labelled variance-free and single-run** (Claims 5, 3; see Limitations) — the Smith must not present them as an eval-budget baseline, because the page reports one run with no repeat count, no spread, and no seed control, and the observed concurrency of that run is itself the state-dependent output of the scheduler documented in `docs-promptfoo-configuration-rate-limits.md` Claim 5, not a configured rate. One line of hardening belongs with the runnable artifact: the example's test selection is a live `huggingface://datasets/cais/hle` fetch with no revision pin (Claim 11; see `docs-promptfoo-configuration-huggingface-datasets.md` Claim 2), so a team scaling this up should materialize and commit the sampled questions rather than inherit an unpinnable third-party input.
- **Chapter 03/05 (Evaluation methodology)**: The page's levers (thinking tokens, max_tokens, adaptive effort) and the caution that increasing token budget alone doesn't guarantee gains (Claims 6, 10) are useful additions to methodology guidance.

## Extraction Notes

- Source read in full from the live page (https://www.promptfoo.dev/docs/guides/hle-benchmark). Single page, no sub-pages followed.
- Quotes were copied verbatim where possible; the performance summary and tables are reproduced as-is in Concrete Artifacts.
- The Prospector's caution about treating accuracy table as pointer (not evidence) is reflected in Claim 4 and the note preserves that distinction.
- Judge dependency (unpriced) is called out as Claim 8 based on what's reported; page never states judge identity/cost.
- `date_published` uses the page's "Last updated Oct 16, 2026" footer.
- `confidence_overall` = `emerging`: concrete measured numbers exist but are explicitly presented as preliminary single-run demonstration; the methodological disclaimers are the strongest signal.
- Registry files (`sources.json`, `claims-index.json`) were not edited — they are derived after merge.
- **Rework after Assayer review**: the page was re-fetched (raw HTML, rendered to text) and every `Quote:` field re-checked against it. Changes made: Claim 1's quote was split into its two contiguous source sentences (it had elided the sentence naming the 1,000+ experts behind an ellipsis); Claim 10 was downgraded `settled` → `emerging` because it is an empirical generalization from the single preliminary run Claim 3 describes, not a demonstrated result; Claim 8's Quote field was relabelled as an inference from absence rather than a pointer that reads like a quote; the OSWorld corroboration was corrected so the three-state result model is attributed to that note (its Claim 3) rather than to this page; and the two missed cross-references (the `huggingface://datasets/` prefix note behind Claim 11's snippet, and `model-graded-closedqa` as the binary alternative to this page's rubric) were added after re-reading both notes to verify the cited claim numbers.
- **Second rework, after the round-1 Assayer review**: the page was re-fetched and re-read in full. Changes made: (a) the three Prospector-named overlapping notes that were missing from Cross-References were added — `docs-promptfoo-configuration-rate-limits.md` (Claims 3/5, under Extends: the concurrency controller behind the Claim 5 run shape, and the retry/timeout surface this page omits), `docs-litellm-benchmarks.md` (Claims 6/9, under Corroborates: the sibling non-universality disclaimer and the latency-depends-on-concurrency rule), and `docs-promptfoo-choosing-best-gpt-model.md` (Claims 1/7, under Corroborates: leaderboard inadequacy and the thin-evidence disclaimer), with every cited claim number re-read in its note before writing (MINER.md §4b) and quoted fragments copied from those notes rather than reconstructed; (b) a new **Limitations — What This Page Does Not Cover** section records the enumerated absences extraction target #4 required (no CI exit-code/threshold config, no retry/timeout/rate-limit handling, no seed control, no cross-run variance), each verified as an absence by full-page read, and the same caveat is carried into Guide Impact so the note cannot be synthesized as a CI-gating recipe or an eval-budget baseline; (c) Claim 5's run shape is now explicitly labelled single-run and variance-free, and notes that its observed 20-way concurrency is the scheduler's state-dependent output rather than a configured rate; (d) the optional Claim 5/Claim 6 naming inconsistency is reconciled in-line ("Claude 4" in the results table vs "Claude Sonnet 4.6" in the Customization Options section), with the page's separate leaderboard entries for "Claude Sonnet 4" and "Claude Opus 4.6 (Thinking Max)" noted. No quote fields were changed this round — every `Quote:` in the note was re-verified character-for-character against the re-fetched page and all matched.
