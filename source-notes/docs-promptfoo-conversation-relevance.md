---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/conversation-relevance/
source_type: docs
title: "Promptfoo Configuration: Model-graded conversation-relevance"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-15
date_extracted: 2026-09-15
last_checked: 2026-09-15
status: current
confidence_overall: emerging
issue: "#1334"
---

# Promptfoo Configuration: Model-graded conversation-relevance

> The vendor reference for the `conversation-relevance` assert type — a
> sliding-window judge that scores a dialogue as the *proportion of windows*
> in which the assistant turn was relevant, with a documented default
> `threshold: 0.5`, a literal (non-template-rendered) `_conversation` input
> contract, and a `rubricPrompt` whose output shape is `verdict`/`reason`
> rather than the pass/score mold of the hub's `llm-rubric`.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo per-type
  model-graded reference page under `/docs/configuration/expected-outputs/
  model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner, authored by `mldangelo-oai`).
  First-party documentation of the tool's own assert type — authoritative for
  what the config does with a given threshold/window. The vendor reports no
  measured gate quality, calibration, or cost figures; the scoring contract is
  directly checkable against an installed CLI.
- **Scope**: A single self-contained page for the `conversation-relevance`
  assert: the sliding-window scoring model (single-turn and multi-turn), basic
  usage, the `_conversation` variable, configuration options (`windowSize`,
  custom `rubricPrompt`), special considerations (vague inputs, short
  conversations), provider override, and worked examples. It does NOT cover
  the sibling model-graded types (answer-relevance, context-faithfulness,
  context-recall, context-relevance — separate pages) or the deterministic
  tier (sibling #1289). Code examples arrived as collapsed single lines after
  HTML extraction; line breaks were restored at YAML boundaries with no
  wording changes.
- **Last updated**: Sep 15, 2026 by mldangelo-oai.
- **Provenance**: "This implementation is adapted from DeepEval's Conversation
  Relevancy metric."

## Extracted Claims

### Claim 1: The `conversation-relevance` metric scores a dialogue as the proportion of sliding windows (default size 5) in which the assistant response was deemed relevant — a quantized `k/windows` score, not a smooth one
- **Evidence**: The "How it works" section listing single-turn vs multi-turn
  evaluation and the "Scoring" bullet, plus the `windowSize` config option
  ("Control how many conversation turns are considered in each sliding
  window").
- **Confidence**: settled (documented product behavior)
- **Quote**: "For conversations, it creates sliding windows of messages and evaluates if each assistant response is relevant within its conversational context" and "The final score is the proportion of windows where the response was deemed relevant"
- **Our assessment**: This is the third distinct aggregation shape after
  weighted-average (#1287) and cosine-similarity (answer-relevance, #1319): a
  windowed proportion whose granularity is set by `windowSize` (default 5).
  The score is discrete — `k` relevant windows out of `n` — so a threshold is
  meaningful only relative to the window size; `threshold: 0.8` with a
  5-window dialogue is not 80% in general but a specific step on the
  quantized scale. For gate calibration (Ch05), that means the effective
  score resolution is fixed by `windowSize`, not by the threshold.

### Claim 2: The page documents a non-zero default threshold for the first time in the family — `0.5` when omitted, with an explicit `0` "accept any score" escape hatch
- **Evidence**: The paragraph directly under "Basic usage".
- **Confidence**: settled (documented product behavior)
- **Quote**: "The threshold defaults to `0.5` when omitted. Set it explicitly to `0` to accept any score."
- **Our assessment**: The body of evidence now shows per-type default
  thresholds, not a single family default: answer-relevance never states one
  (#1319 Claim 3), context-faithfulness defaults to `0` (#1320 Claim 2), and
  conversation-relevance documents `0.5`. This closes the #1319 open question
  for this type — each page must be read on its own. The `threshold: 0`
  escape hatch is the vendor-sanctioned version of the `threshold: 0`
  silent-green footgun (#1287 Claim 3): passing `0` means "accept any score",
  i.e. the assert always passes unless the judge errors.

### Claim 3: Conversations shorter than `windowSize` are evaluated as a single window — a degenerate case where the "proportion of windows" score collapses to a binary 0 or 1
- **Evidence**: The "Short conversations" special-consideration note.
- **Confidence**: settled (documented product behavior)
- **Quote**: "If the conversation has fewer messages than the window size, the entire conversation is evaluated as a single window."
- **Our assessment**: A 2-3 turn dialogue (a common smoke-test shape, and the
  example the page itself shows) yields only a single judge verdict: score is
  exactly 0 or 1, and any threshold in (0, 1] reduces to "all-or-nothing".
  For SRE gate use this is a sharp edge: a drift check that catches
  out-of-context replies in production-length threads gives no graded signal
  on short test fixtures — the gate is effectively Boolean there. Window sizing
  and fixture length must be decided together.

### Claim 4: `_conversation` content is treated as literal runtime data and is NOT rendered as a Nunjucks template — template syntax like `{{ vars.value }}` or `{{ env.API_KEY }}` is preserved verbatim "for security"
- **Evidence**: The note callout attached to the "Using with conversations"
  section.
- **Confidence**: settled (documented product behavior)
- **Quote**: "`_conversation` message content is treated as literal runtime data and is not rendered as a Nunjucks template. Template syntax such as `{{ vars.value }}` or `{{ env.API_KEY }}` is preserved verbatim for security."
- **Our assessment**: A deliberate guard against template-injection/exfiltration:
  anything a conversation participant says that *looks* like `{{ env.* }}`
  stays inert instead of being interpolated at render time. This is the first
  explicit "don't render secrets embedded in a fixture" statement in the
  corpus and is novel relative to the `_conversation` type-signature and
  concurrency-1 surface in #1276. For test-harness security review (Ch06,
  "Red-teaming as a CI gate") it is the vendor's own acknowledgement that
  fixture content is untrusted input and must not reach the template
  interpreter.

### Claim 5: The custom `rubricPrompt` for `conversation-relevance` must output JSON with `verdict` (yes/no) and `reason` fields — a rubric contract that diverges from the pass/score shape of the hub's `llm-rubric`
- **Evidence**: The "Custom grading rubric" configuration example ending with
  the JSON field instruction.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Output JSON with 'verdict' (yes/no) and 'reason' fields."
- **Our assessment**: The rubric's output contract is verdict/yes-no plus
  reason, not a `pass`/`score` pair — so a team that swaps an `llm-rubric`
  prompt (pass/score, #1305 Claim 10) into a `conversation-relevance` assert
  copy-paste-misparses it. The verdict/reason contract also explains how the
  windowed score is counted: each window's binary verdict feeds the
  proportion in Claim 1. Worth one line in the per-type rubric-swap guidance
  (#1305 Claim 8) that rubrics are not freely portable across types.

## Concrete Artifacts

Basic usage and default-threshold note:

```yaml
assert:
  - type: conversation-relevance
    threshold: 0.8
```

> The threshold defaults to `0.5` when omitted. Set it explicitly to `0` to
> accept any score.

Worked example with `_conversation` (vague-input acceptance example — a
greeting is considered acceptable):

```yaml
tests:
  - vars:
      _conversation:
        - input: 'Hi there!'
          output: 'Hello! How can I help you today?'
        - input: 'How are you?'
          output: "I'm doing well, thank you! How are you?"
    assert:
      - type: conversation-relevance
        threshold: 0.8
```

`windowSize` and custom `rubricPrompt`:

```yaml
assert:
  - type: conversation-relevance
    threshold: 0.8
    config:
      windowSize: 3 # Default is 5
```

```yaml
assert:
  - type: conversation-relevance
    threshold: 0.8
    rubricPrompt: |
      Evaluate if the assistant's response is relevant to the user's query.
      Consider the conversation context when making your judgment.
      Output JSON with 'verdict' (yes/no) and 'reason' fields.
```

Short-conversation degenerate case ("If the conversation has fewer messages
than the window size, the entire conversation is evaluated as a single
window") and single-window example:

```yaml
tests:
  - vars:
      _conversation:
        - input: 'What is 2+2?'
          output: '2+2 equals 4.'
        - input: 'What about 3+3?'
          output: 'The capital of France is Paris.' # Irrelevant response
        - input: 'Can you solve 5+5?'
          output: '5+5 equals 10.'
    assert:
      - type: conversation-relevance
        threshold: 0.8
        config:
          windowSize: 2
```

Provider override — per-assert and global (unpinned default judge):

```yaml
assert:
  - type: conversation-relevance
    threshold: 0.8
    provider: openai:gpt-5-mini
```

```yaml
defaultTest:
  options:
    provider: anthropic:claude-sonnet-4-6
```

> Like other model-graded assertions, you can override the default grading provider

## Cross-References

- **Corroborates**: #1305 Claims 1-2 (model-graded asserts use an ambient,
  overridable judge at the provider level; the "like other model-graded
  assertions" phrasing and the `defaultTest.options.provider` pattern confirm
  the shared rule surface), #1287 Claim 3 (a `threshold: 0` gate is a
  silent-green pass — the page now documents that surface as "accept any
  score"), #1276 Claims 1-2 (the `_conversation` array shape and its
  concurrency-1 implication are reiterated here), #1289 Claim 1
  (conversation-relevance sits on the model-graded side of the
  deterministic/model-graded boundary).
- **Contradicts**: none — the documented `0.5` default is a per-type scope
  qualifier, not an opposing claim to #1319 Claim 3 (which records that the
  *answer-relevance* page states no default) or #1305 Claim 10 (scoped to
  `llm-rubric`).
- **Extends**: #1305 (the hub's per-type family; here a concrete third
  aggregation shape and rubric contract), #1319 (sibling answer-relevance;
  both judge conversational relevance but answer-relevance is single-output
  cosine similarity while conversation-relevance is windowed verdicts),
  #1320 (per-type default thresholds now span `0` and `0.5`), #1289 (the
  model-graded side of the boundary in concrete).
- **Novel**: window-proportion (quantized `k/windows`) scoring as a third
  aggregation shape; the first documented non-zero default threshold in the
  family; the literal (non-Nunjucks-rendered) `_conversation` fixture
  contract as an explicit exfiltration guard; the verdict/reason rubric JSON
  contract distinct from pass/score.

## Guide Impact

- **Chapter 05 (`guide/05-llm-ops-reliability.md`)**: at the "Metrics without
  a unit are noise" line (:263), add that judge-produced conversational scores
  are discrete when windowed — resolution is set by `windowSize`/fixture
  length, so a "0.8 conversation relevance" on a 3-window fixture can only
  mean 2/3 or 3/3; and at the "Judge calibration before judge trust" line
  (:285), add the per-type default-quirk: `threshold` defaults differ by assert
  type (`0`, `0.5`, or unspecified), which is a copy-paste footgun when on
  shared prompts.
- **Chapter 06 (`guide/06-security-and-trust.md`)**: at the "Red-teaming as a
  CI gate" line (:98), cite the `_conversation`/Nunjucks note as the vendor's
  explicit "fixture content is not rendered" policy — a test fixtures must be
  treated as untrusted input even in first-party tools.

## Extraction Notes

- Candidates from `miner-related-notes.md` dismissed after reading/verifying
  (relationship too thin to cite): `docs-promptfoo-classifier-grading.md`
  (#1288, threshold calibration is model/label-bound, a different mechanism
  from window-relative thresholds), `blog-promptfoo-owasp-red-teaming.md`
  (#555) and `blog-promptfoo-red-team-claude.md` / `-gemini.md` (#689, #690,
  methodology-level, not per-type config), `blog-pagerduty-sre-agent-triage.md`
  (#610, incident triage), `docs-google-sre-team-lifecycles.md` and
  `docs-google-sre-reliable-product-launches.md` (org/process, not gate
  tooling), `docs-promptfoo-javascript-assertions.md` (#1304, custom-JS
  surface), `docs-langfuse-mcp-server.md` (unrelated integration).
- Cited and verified directly: #1305 (Claims 1-2, 8, 10, 13), #1319
  (Claims 3-4), #1320 (Claim 2), #1287 (Claim 3), #1276 (Claims 1-2),
  #1289 (Claim 1 — deterministic/model-graded boundary), #261 (portability
  thread on thresholds/rubrics).
- Do-Not-Merge guardrails: this note must land as a `source-note` PR (not
  `miner-eval`); the source issue #1334 stays open until the Assayer verdict;
  no `guide/` or `registry/` edits were made in this extraction.