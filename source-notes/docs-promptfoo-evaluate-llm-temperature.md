---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-llm-temperature
source_type: docs
title: "Promptfoo Guides: Choosing the right temperature for your LLM — repeat stability, Wilson intervals, and silent provider-constraint drift"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-23
date_extracted: 2026-10-24
last_checked: 2026-10-24
status: current
confidence_overall: emerging
issue: "#1706"
---

# Promptfoo Guides: Choosing the right temperature for your LLM

> A guide to evaluating temperature in promptfoo that contributes concrete CI/measurement semantics (repeatStability JSON, Wilson 95% CIs with validity assumptions, per-repeat-index cache masking) and a silent provider-constraint drift warning (Claude Sonnet 5+/newer Opus/Fable drop `temperature`/`top_p`/`top_k` with a warning; `effort` controls reasoning depth not sampling).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo guides page "Choosing the right temperature for your LLM")
- **Author credibility**: Promptfoo, first-party documentation. Authoritative for promptfoo product behavior; no measured numbers/benchmarks given on this page.
- **Scope**: Covers rationale for temperature, how to run a temperature comparison eval, adding assertions (`llm-rubric` example), and evaluating randomness via `--repeat`. Does NOT cover general decoding theory beyond a short explanation; focuses on eval mechanics.
- **Last updated**: Oct 23, 2026 by promptfoobot[bot] (per page footer)

## Extracted Claims

### Claim 1: `results.repeatStability` is the JSON export summary grouped by test case, expanded variables, provider, and prompt; repeated groups with both pass and fail are flagged as "mixed pass/fail", pass rates exclude errors, and groups with no scored results have no pass rate
- **Evidence**: The "Evaluating randomness" section states the completion summary flags mixed groups and JSON exports include `results.repeatStability` with grouping and pass-rate rules.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The completion summary flags repeated groups that contain both passing and failing results. JSON exports include the full summary under `results.repeatStability`, grouped by test case, expanded variables, provider, and prompt. Pass rates exclude errors; groups with no scored results have no pass rate."
- **Our assessment**: Buy it. This is the concrete schema/aggregation contract for repeat-based variance measurement. It clarifies how mixed outcomes are surfaced and explicitly excludes errors from pass rates and omits pass rates when unscorable.

### Claim 2: For groups with scored results and no cached target or grader responses, the summary includes a Wilson 95% confidence interval; interpreting it as a model pass-rate estimate assumes independent runs with the same success probability, an assumption broken by shared conversation history or shifting external state even under `--no-cache`
- **Evidence**: "Evaluating randomness" section states Wilson 95% CI semantics and validity preconditions.
- **Confidence**: settled (documented product behavior; statistical method named)
- **Quote**: "For groups with scored results and no cached target or grader responses, the summary includes a Wilson 95% confidence interval. Interpreting it as a model pass-rate estimate assumes independent runs with the same success probability. Shared conversation history or changing external state can violate that assumption, even with `--no-cache`."
- **Our assessment**: Buy it. Important correctness note: the CI is only meaningful under i.i.d.-like assumptions; stateful runs (conversation history, external state) invalidate the interpretation even if cache is disabled. Pairs with caching guidance on reproducibility.

### Claim 3: By default each repeat index has its own cache entry, so re-running the same eval can replay repeat 0, repeat 1, and repeat 2 independently; to get fresh generations on every run while sampling temperature add `--no-cache` (per-repeat cache namespaces mean replay can mask real variance)
- **Evidence**: "Evaluating randomness" states per-repeat cache entries and remediation.
- **Confidence**: settled (documented product behavior)
- **Quote**: "By default, each repeat index has its own cache entry, so re-running the same eval can replay repeat 0, repeat 1, and repeat 2 independently. If you want fresh generations on every run while sampling temperature, add `--no-cache`."
- **Our assessment**: Sharpens existing caching guidance. While `docs-promptfoo-configuration-caching.md` covers per-repeat namespaces, this page explicitly frames the failure mode as masking real variance and ties it directly to temperature/variance measurement — a useful operational emphasis for eval design.

### Claim 4: Claude Sonnet 5 and newer Opus and Fable models do not support `temperature`, `top_p`, or `top_k`; promptfoo omits these parameters with a warning, and `effort` controls reasoning depth rather than sampling randomness
- **Evidence**: Note in "Evaluating" section.
- **Confidence**: settled (documented product behavior; model-generation-specific)
- **Quote**: "Claude Sonnet 5 and newer Opus and Fable models do not support `temperature`, `top_p`, or `top_k`; Promptfoo omits these parameters with a warning. Their `effort` setting controls reasoning depth, not sampling randomness. These examples use Claude Sonnet 4.6, which accepts temperature settings when thinking is disabled."
- **Our assessment**: Generalizes the silent-constraint drift risk. Configuration guide notes `effort` replaces `budget_tokens` on Claude 5; this page adds that sampling params are silently dropped with a warning — important for eval configs that sweep temperature across model families/generations.

### Claim 5: Temperature affects token selection by scaling logits before softmax (lower temperature sharpens distribution toward high scores, higher temperature flattens it) — explanatory framing for why sampling changes creativity/predictability
- **Evidence**: "How does temperature work?" section explains logit scaling before softmax.
- **Confidence**: settled (general ML explanation; vendor states it)
- **Quote**: "The `temperature` parameter affects each output token by scaling the logits (the raw output scores from the model) before they are passed through the softmax function that turns them into probabilities. Lower temperatures sharpen the distinction between high and low scores, making the high scores more dominant, while higher temperatures flatten this distinction, giving lower-scoring words a better chance of being chosen."
- **Our assessment**: Textbook background; included for completeness but not novel to corpus. Skimmed per triage guidance to focus on eval/measurement and constraint details.

## Concrete Artifacts

### Example config: temperature sweep on same model with labels
```yaml
prompts:
  - 'Respond to the following instruction: {{message}}'

providers:
  - id: anthropic:claude-sonnet-4-6
    label: claude-sonnet-lowtemp
    config:
      temperature: 0.2
  - id: anthropic:claude-sonnet-4-6
    label: claude-sonnet-hightemp
    config:
      temperature: 0.9

tests:
  - vars:
      message: What's the capital of France?
  - vars:
      message: Write a poem about the sea.
  - vars:
      message: Generate a list of potential risks for a space mission.
  - vars:
      message: Did Henry VIII have any grandchildren?
```

### Automated check example (llm-rubric)
```yaml
tests:
  - description: 'Check for hallucination on Henry VIII grandchildren question'
    vars:
      message: Did Henry VIII have any grandchildren?
    assert:
      - type: llm-rubric
        value: Henry VIII didn't have any grandchildren
```

### Assertion example (deterministic)
```yaml
tests:
  vars:
    message: Generate a list of potential risks for a space mission.
  assert:
    - type: icontains-all
      value:
        - 'radiation'
        - 'isolation'
        - 'environment'
```

### Commands
```bash
npx promptfoo@latest eval
npx promptfoo@latest view
promptfoo eval --repeat 3
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-configuration-caching.md` (Claim 8) — per-repeat cache namespaces; this page adds emphasis on masking real variance and ties to temperature measurement. Also aligns with Claims 1,4,9 on cache controls.
  - `source-notes/docs-promptfoo-configuration-guide.md` (Claim 8) — `effort` replaces `budget_tokens` on Claude 5/adaptive thinking models; this page extends to silent dropping of `temperature`/`top_p`/`top_k` with warning.
  - `source-notes/docs-promptfoo-select-best.md` — mentions dropping temperature for thinking models; this page generalizes to a silent-constraint drift risk across newer Opus/Fable/Sonnet 5 families.
  - `source-notes/docs-promptfoo-test-agent-skills.md` (Claim 11), `source-notes/docs-promptfoo-evaluate-coding-agents.md` (Claim 10) — use of `--repeat`/`--no-cache` for variance/flake measurement.
  - `source-notes/docs-promptfoo-deterministic-metrics.md`, `source-notes/docs-promptfoo-assertions-metrics.md` — assertion patterns (`llm-rubric`, deterministic checks).

- **Contradicts**: (none found)

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-caching.md` — adds `results.repeatStability` schema details (grouping, mixed pass/fail flag, pass-rate rules excluding errors/no-scored-results), Wilson 95% CI semantics with independence assumptions, and explicit "mask real variance" framing for per-repeat cache entries.
  - `source-notes/docs-promptfoo-configuration-guide.md` — adds concrete warning behavior for dropped sampling params on newer Claude models.

- **Novel**: `results.repeatStability` export structure and rules; Wilson interval validity caveats (shared conversation history/external state break independence even with `--no-cache`); explicit variance-masking effect of per-repeat cache entries in temperature evaluation context; silent omission with warning of `temperature`/`top_p`/`top_k` on Claude Sonnet 5+/newer Opus/Fable with `effort` as reasoning-depth control.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add concrete measurement details for repeat-based evals. Specifically: document `results.repeatStability` grouping (test case + expanded vars + provider + prompt), mixed pass/fail flagging, pass-rate rules (exclude errors, no rate if unscored), Wilson 95% CI interpretation requirements (independence assumption; broken by shared history/external state even with `--no-cache`), and the variance-masking gotcha where per-repeat cache entries replay independently across reruns — requiring `--no-cache` when measuring model variance. Also add a note on provider-constraint drift: newer Claude models (Sonnet 5+, newer Opus/Fable) silently drop `temperature`/`top_p`/`top_k` with warnings and use `effort` for reasoning depth (not sampling) — eval sweeps must account for this.

## Extraction Notes

- Read the full page via webfetch; followed triage guidance to focus on items 1-4 (repeatStability, Wilson intervals/assumptions, per-repeat cache masking, Claude Sonnet 5+ silent drops) and skipped tutorial framing (logit/softmax explanation treated as background).
- Cross-referenced against existing promptfoo notes (caching, configuration-guide, select-best, test-agent-skills, evaluate-coding-agents). Verified `repeatStability` and Wilson CI details are not present in existing notes; per-repeat caching is present but this page adds explicit "mask real variance" framing.
- No contradictions found. No paywall/dead content issues.
