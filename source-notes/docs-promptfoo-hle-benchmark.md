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
- **Scope**: Covers what HLE is (Scale AI/CAIS, 1000+ experts, benchmark saturation rationale), running the example (`npx promptfoo@latest init --example huggingface/hle` etc.), API keys (OpenAI/Anthropic/HF), the demo results for Claude 4 vs o4-mini on 50 questions each, prompt engineering for multimodal inputs (provider-specific image formatting), automated grading via `llm-rubric`, customization options (thinking tokens, max_tokens, sampling), explicit limitations, and implications. The page does not claim CI gating or present a full-corpus run; it positions itself as a "how to" with a concrete small-sample run.
- **Followed sub-pages**: None required beyond the main guide page. Outbound links (arXiv, HuggingFace dataset, Scale AI leaderboard, etc.) are references; the substantive measured content is on this page.

## Extracted Claims

### Claim 1: HLE is framed as a response to benchmark saturation — designed to be more challenging because models exceed 90% on MMLU, with characteristics including 100+ subjects, 14% multimodal questions, resistance to simple web search, and verifiable closed-ended problems
- **Evidence**: Introductory paragraphs naming Scale AI/CAIS, the benchmark-saturation rationale, and key characteristics.
- **Confidence**: settled (external benchmark provenance)
- **Quote**: "Humanity's Last Exam (HLE) is a challenging benchmark commissioned by Scale AI and the Center for AI Safety (CAIS)... Created to address benchmark saturation where current models achieve 90%+ accuracy on MMLU, HLE presents genuinely difficult expert-level questions that test AI capabilities at the frontier of human knowledge."
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
- **Our assessment**: Harvestable for per-run eval budget estimation (Ch05). These are measured run-shape figures (sample → tokens → cost → latency → concurrency). Single-run provenance; page flags they are preliminary.

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
- **Quote**: (cost table as in Claim 5 shows only evaluated model costs)
- **Our assessment**: The page reports judge is used, but never states judge identity or its cost. This is a concrete gap: the per-model costs ($0.56, $1.26) are for generation only, not total eval cost. Worth recording as a caution.

### Claim 9: Multi-provider image formatting is handled via custom Python — OpenAI uses `image_url` format while Anthropic/Claude requires base64 `source` format; also uses `developer` role for o1/o3 reasoning models
- **Evidence**: Prompt Engineering for HLE section.
- **Confidence**: settled (documented implementation detail)
- **Quote**: "To handle images across different AI providers, we wrote a custom prompt function in Python. OpenAI uses `image_url` format while Anthropic/Claude requires base64 `source` format."
- **Quote**: "- **OpenAI models**: Uses `image_url` format for images, `developer` role for o1/o3 reasoning models\n- **Anthropic models**: Converts images to base64 `source` format for Claude compatibility"
- **Our assessment**: Documents portability cost of multi-provider eval harness — concrete operational detail.

### Claim 10: The page states "token budget increases alone don't guarantee accuracy improvements" as a falsifiable caution
- **Evidence**: Implications section (bullet list).
- **Confidence**: settled (stated finding/lesson)
- **Quote**: "- Token budget increases alone don't guarantee accuracy improvements"
- **Our assessment**: This is an extractable empirical caution tied to reasoning budgets; the page presents it as a key finding from the demo context.

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

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-harmbench.md` — same shape (vendor product docs for running a standardized benchmark via promptfoo plugin/config). Both emphasize config surface and limitations of what the page demonstrates (Harmbench notes static dataset limits; HLE notes sampling fragility/comparability).
  - `source-notes/docs-promptfoo-evaluate-osworld-with-inspect.md` — strong methodological parallel on denominator/hygiene: this page's "three states" vs the error-vs-failure/denominator discipline. Also both give concrete measured run-shape figures (tokens/cost/time/concurrency) and explicit caveats about generalizing numbers.

- **Extends**:
  - `source-notes/docs-promptfoo-llm-rubric.md` (and related model-graded notes) — extends the `llm-rubric` concept by applying it to a closed-ended public benchmark with a concrete 0.0-1.0 rubric tailored to mathematical/logical equivalence. (The rubric here is specific to HLE's grading needs.)

- **Contradicts**: None identified; no contradiction issue filed. The page's claims are self-consistent and include appropriate disclaimers.

- **Novel**:
  - The first source note covering promptfoo's HLE benchmark guide. No existing note covers HLE or the specific cost/latency breakdown for o4-mini vs Claude 4 on this example. The explicit first-party admission that small-N single-run results "require validation via larger samples and multiple runs" paired with concrete numbers is the key novel extraction.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add guidance about small-sample honesty — when reporting benchmark results, document sample size relative to full corpus (50/3000+), single vs multiple runs, and comparability to official leaderboards. Cite Claims 2, 3 as concrete examples of vendor self-disclosure. Also add that eval costs should account for judge (llm-rubric) cost which may not be itemized in per-model generation costs (Claim 8).
- **Chapter 05 (Cost, capacity, and fallback patterns)**: Incorporate the concrete run-shape numbers as an illustrative example (237K tokens for 100 cases, 9 min at 20 concurrent workers) to help teams estimate eval budgets, while noting they are preliminary and single-run (Claims 5, 3).
- **Chapter 03/05 (Evaluation methodology)**: The page's levers (thinking tokens, max_tokens, adaptive effort) and the caution that increasing token budget alone doesn't guarantee gains (Claims 6, 10) are useful additions to methodology guidance.

## Extraction Notes

- Source read in full from the live page (https://www.promptfoo.dev/docs/guides/hle-benchmark). Single page, no sub-pages followed.
- Quotes were copied verbatim where possible; the performance summary and tables are reproduced as-is in Concrete Artifacts.
- The Prospector's caution about treating accuracy table as pointer (not evidence) is reflected in Claim 4 and the note preserves that distinction.
- Judge dependency (unpriced) is called out as Claim 8 based on what's reported; page never states judge identity/cost.
- `date_published` uses the page's "Last updated Oct 16, 2026" footer.
- `confidence_overall` = `emerging`: concrete measured numbers exist but are explicitly presented as preliminary single-run demonstration; the methodological disclaimers are the strongest signal.
- Registry files (`sources.json`, `claims-index.json`) were not edited — they are derived after merge.
