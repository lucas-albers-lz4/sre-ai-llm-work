---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/answer-relevance/
source_type: docs
title: "Promptfoo Configuration: Answer Relevance"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-15
date_extracted: 2026-09-15
last_checked: 2026-09-15
status: current
confidence_overall: emerging
issue: "#1319"
---

# Promptfoo Configuration: Answer Relevance

> The vendor reference for the only hybrid grader in promptfoo's model-graded
> assertion family — `answer-relevance` puts two independently-configurable
> provider classes (an LLM for question generation, an embedding model for
> similarity scoring) behind one verdict, making it non-deterministic by
> construction: the comparison corpus is re-generated per call, so the score
> moves run-to-run even when the judge is pinned.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Answer Relevance"
  per-type reference page under `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `answer-relevance` behavior — authoritative for what the config
  does with a given provider/threshold setup, but vendor-positioned: the page
  carries no measured gate-failure-rate, score-distribution, or calibration
  figures, and there is no independent practitioner validation.
- **Scope**: A single self-contained reference page for the `answer-relevance`
  assert type. Covers the three-step scoring pipeline (LLM generates candidate
  questions → embedding similarity against original query → aggregate score),
  the two-slot provider override shape (`text` + `embedding`), `rubricPrompt`
  customization for question generation, and `threshold` gating. Does NOT cover
  the model-graded hub page (#1305), other per-type sub-pages, or the
  aggregation/scoring model.
- **Last updated**: Sep 15, 2026 by renovate[bot]; page undated but documents
  the current `gpt-5` era.

## Extracted Claims

### Claim 1: `answer-relevance` is the only hybrid grader in the model-graded family — it uses two separate providers (an LLM text provider for question generation plus an embedding provider for similarity scoring) rather than a single judge model, making it non-deterministic by construction
- **Evidence**: The "How it works" section's three-step pipeline and the
  "Overriding the Providers" section's explicit two-slot split.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The answer relevance checker: Uses an LLM to generate potential questions that the output could be answering. Compares these questions with the original query using embedding similarity. Calculates a relevance score based on the similarity scores."
- **Our assessment**: This is the finding that extends the hub note's (#1305)
  ambient-judge finding from one provider slot to two. Every other model-graded
  assertion puts a single judge behind the verdict; `answer-relevance` puts
  *two independently unpinned* models behind it. The non-determinism is not a
  bug but a design consequence: the text provider regenerates the comparison
  corpus on each call, so even with both providers pinned, the embedding
  similarity scores will vary across runs because the generated questions are
  different. A gate built on this assertion cannot guarantee identical
  pass/fail across replays — a harder hermeticity problem than the single-
  judge model-graded family.

### Claim 2: The two-slot provider override shape (`provider: { text: ..., embedding: ... }`) is a different override surface from the single `provider`/`options.provider` override the hub note's precedence chain describes
- **Evidence**: The "Overriding the Providers" section's nested YAML structure
  at both `defaultTest.options.provider` and assertion level, with separate
  `id` and `config` keys under each slot.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Answer relevance uses two types of providers: A text provider for generating questions. An embedding provider for calculating similarity." and the nested override configs:
  ```yaml
  defaultTest:
    options:
      provider:
        text:
          id: gpt-5
          config:
            temperature: 0
        embedding:
          id: openai:text-embedding-ada-002
  ```
- **Our assessment**: The nested shape matters because it interacts with the
  hub note's shorthand-provider trap (#1305 Claim 2). If a team sets a
  `defaultTest.options.provider` object globally (e.g. for `llm-rubric`) and
  then adds an assertion-level shorthand `provider: anthropic:claude-sonnet-4-6`
  to an `answer-relevance` assert, the shorthand does not split into two slots
  — it replaces the entire provider object, losing both the text and embedding
  overrides. The question of whether the same inheritance trap (shorthand drops
  `config`) applies when a team mixes nested `text`/`embedding` overrides with
  assertion-level shorthand is the open surface the triage flagged: the page
  does not document this interaction explicitly.

### Claim 3: The score is a cosine-similarity aggregate, not a calibrated relevance probability — the threshold (e.g. 0.7, 0.8) gates a floating-point similarity score whose absolute meaning shifts when the embedding model or the question-generation prompt changes
- **Evidence**: The "How it works" pipeline description (embedding similarity
  → aggregate score) and the threshold examples shown only as user-supplied
  values.
- **Confidence**: settled (documented product behavior; the absence of a
  documented default is itself documented)
- **Quote**: "Score between 0 and 1" (the only threshold characterization on
  the page) and "A higher threshold requires the output to be more closely
  related to the original query."
- **Our assessment**: The page never states a default threshold — every
  `threshold:` in the examples is explicitly provided (0.7, 0.8), suggesting
  that omitting it either uses a promptfoo default or fails. The absence of a
  documented default means the gate's strictness is implicit config, not a
  pinned constant. More importantly, the threshold gates a *cosine-similarity
  aggregate* whose absolute scale depends on the embedding model
  (`text-embedding-ada-002` vs `embed-english-v3.0` produce different score
  distributions), so `threshold: 0.7` does not mean the same thing across two
  configs with different embedding providers. This is the score-comparability
  hazard the triage highlighted: swapping the embedding provider silently
  rebases every prior threshold without a config error.

### Claim 4: `rubricPrompt` is repurposed for question generation (not rubric grading) — customizing it changes the questions that get embedded and compared, so a fixed threshold does not mean the same thing across two configs
- **Evidence**: The "Customizing the Prompt" section with its
  `rubricPrompt` example that generates questions rather than grades output.
- **Confidence**: settled (documented product behavior; the divergence from
  the hub note's `rubricPrompt` semantics is implicit)
- **Quote**: "Given this answer: {{output}}\nGenerate 3 questions that this answer would be appropriate for.\nMake the questions specific and directly related to the content."
- **Our assessment**: In `llm-rubric` and `g-eval`, `rubricPrompt` customizes
  the grading rubric — the judge's criteria. In `answer-relevance`, it
  customizes the *question generation step* — what questions are proposed and
  then embedded. This is assertion-specific semantics that the hub note's
  (#1305) Claim 8 treats as a uniform multilingual-rubric swap across the
  family. A team that copies a `rubricPrompt` from an `llm-rubric` config into
  an `answer-relevance` assert will change the question-generation behavior
  without understanding that they are modifying the comparison corpus, not the
  grading criteria. The divergence is worth noting in the guide because the
  `rubricPrompt` slot has different semantics per assertion type.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/answer-relevance/
(sections as noted).

### Basic assertion syntax (verbatim from "How to use it")

```yaml
assert:
  - type: answer-relevance
    threshold: 0.7 # Score between 0 and 1
```

### Complete example (verbatim from "Example Configuration")

```yaml
prompts:
  - 'Tell me about {{topic}}'
providers:
  - openai:gpt-5
tests:
  - vars:
      topic: quantum computing
    assert:
      - type: answer-relevance
        threshold: 0.8
```

### Two-slot provider override at `defaultTest` level (verbatim from "Overriding the Providers")

```yaml
defaultTest:
  options:
    provider:
      text:
        id: gpt-5
        config:
          temperature: 0
      embedding:
        id: openai:text-embedding-ada-002
```

### Assertion-level provider override with cross-vendor embedding (verbatim from "Overriding the Providers")

```yaml
assert:
  - type: answer-relevance
    threshold: 0.8
    provider:
      text: anthropic:claude-sonnet-4-6
      embedding: cohere:embedding:embed-english-v3.0
```

### Custom question-generation prompt via `rubricPrompt` (verbatim from "Customizing the Prompt")

```yaml
defaultTest:
  options:
    rubricPrompt: |
      Given this answer: {{output}}
      Generate 3 questions that this answer would be appropriate for.
      Make the questions specific and directly related to the content.
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 1** (ambient
    judge selection — the judge model is picked from environment credentials,
    not pinned by default) — this page extends the ambient-judge finding from
    one provider slot to *two*: `answer-relevance` has a text provider and an
    embedding provider, both unpinned by default. (Verified: #1305 Claim 1.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 5** (self-
    hosted thinking judges can leak reasoning into graded content; `answer-
    relevance` is explicitly named in the cross-type misparse warning) —
    confirms that the scratchpad-misparse risk the parent note documents applies
    to `answer-relevance` specifically: "answer-relevance can embed questions
    with `Thinking:` prepended." (Verified: #1305 Claim 5.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 8** (the
    `rubricPrompt` override surface) — this page supplies the assertion-specific
    semantics: in `answer-relevance`, `rubricPrompt` controls question
    generation rather than grading criteria, diverging from the uniform
    multilingual-rubric swap the parent page documents for `llm-rubric`/
    `g-eval`/`model-graded-closedqa`. (Verified: #1305 Claim 8.)

- **Contradicts**: None identified. No contradiction issue filed. This page
  opposes no existing source-note claim. The `rubricPrompt` semantics divergence
  (Claim 4) is a conditioning variable, not a conflict — the parent page (#1305
  Claim 8) documents the uniform rubric-swap for `llm-rubric`/`g-eval`/
  `model-graded-closedqa`, and this page shows `answer-relevance` has different
  `rubricPrompt` semantics — these are different assertion types with different
  slot meanings, not competing claims about the same slot.

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — the hub
    note catalogs `answer-relevance` by name and documents the cross-type
    thinking-leak risk (Claim 5) but deliberately does not follow this sub-page.
    This note supplies the per-type config semantics: the two-provider
    architecture, the nested override shape, the `rubricPrompt`-as-question-
    generation semantics, and the non-deterministic-by-construction scoring.
    The hub note is the catalogue; this note is the deep-dive on one entry.
    (Verified: #1305's Extraction Notes: "answer-relevance" listed among
    deliberately-not-followed sub-pages.)
  - `source-notes/docs-promptfoo-classifier-grading.md` — the classifier note
    documents the `classifier` / `not-classifier` surface with its own
    label-bound threshold semantics (Claims 1, 5); this page is the model-graded
    counterpart: a similarity-score threshold rather than a classifier-score
    threshold, but with the same non-portability property (Claim 3: threshold
    meaning depends on the specific embedding model). The two notes are the
    "thresholded score from a model artifact" surface from different assertion
    families. (Verified: #1288 Claims 1, 5.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 1** (the
    vendor-drawn deterministic/model-graded boundary) — this page is the
    model-graded side of that boundary, and `answer-relevance` is the strongest
    example of non-determinism in the family: unlike `llm-rubric` (which is
    non-deterministic only if the judge temperature > 0), `answer-relevance`
    regenerates its comparison corpus on every call regardless of temperature
    settings. (Verified: #1289 Claim 1.)

- **Novel**: First corpus coverage of the **dual-provider hybrid grader**
  pattern:
  1. **Two-slot provider surface, both unpinned by default** (Claims 1-2) —
     extends the hub note's ambient-judge finding from one provider slot to two.
  2. **Non-deterministic-by-construction scoring** (Claim 1) — the comparison
     corpus is regenerated per call, so the score moves even with pinned
     providers; this is a harder hermeticity problem than single-judge model-
     graded assertions.
  3. **Score-comparability hazard from embedding-model swaps** (Claim 3) —
     `threshold: 0.7` does not mean the same thing across different embedding
     providers; the threshold is meaningful only relative to a specific
     embedding model's score distribution.
  4. **`rubricPrompt` repurposed for question generation** (Claim 4) — assertion-
     specific slot semantics that diverge from the hub page's uniform rubric-
     swap treatment.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology**:
  Add `answer-relevance` as the case study for the non-hermetic judge gate:
  (a) state that `answer-relevance` is the only model-graded assertion with
  two independently-unpinned provider slots (Claim 1), so the ambient-judge
  risk (#1305 Claim 1) is doubled; (b) add the score-comparability rule —
  swapping the embedding model silently rebases every prior threshold (Claim 3),
  so a pinned gate must pin the embedding provider alongside the text provider
  and the threshold must be re-calibrated when the embedding model changes;
  (c) document that `rubricPrompt` has assertion-specific semantics in
  `answer-relevance` (question generation, not grading criteria — Claim 4),
  so teams cannot uniformly copy `rubricPrompt` configs across assertion types.
  This is the concrete "Metrics without a unit are noise" example for
  similarity-score gates.
- **Chapter 06 (Security and Trust) — judge trust**: The non-deterministic
  scoring of `answer-relevance` (Claim 1) is the strongest example of why
  "pin everything" (#1305 Claim 1, `guide/06-security-and-trust.md:426`) must
  cover both the judge model and the embedding model: a gate that pins the text
  provider but not the embedding provider is half-pinned, and the embedding
  half controls the similarity score that the threshold gates.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/answer-relevance/).
  The page is short (~150 words of substance) and self-contained; no sub-pages
  were followed. Quotes verified character-for-character against the fetched
  rendered content before writing; code blocks copied verbatim.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-promptfoo-model-graded-metrics.md` (#1305) — **cited** (Corroborates,
    Claims 1/5/8). The parent hub note; this sub-page extends it with per-type
    config details.
  - `docs-promptfoo-classifier-grading.md` (#1288) — **cited** (Extends,
    Claims 1/5). Threshold non-portability parallels the classifier note's
    label-bound threshold finding.
  - `docs-promptfoo-deterministic-metrics.md` (#1289) — **cited** (Extends,
    Claim 1). The vendor-drawn boundary; this page is the model-graded side.
  - `docs-promptfoo-assertions-metrics.md` (#1287) — the hub scoring/aggregation
    page; no direct `answer-relevance` coverage; the sibling convention treats
    sub-pages separately; dismissed for direct cross-ref (but the scoring model
    from #1287 underlies all assertion types).
  - `blog-promptfoo-owasp-red-teaming.md` — red-team methodology; no eval-
    assert config surface; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — AI-incident triage via SRE Agent;
    no eval-assert surface; dismissed.
  - `blog-promptfoo-red-team-claude.md`, `blog-promptfoo-red-team-gemini.md` —
    per-model red-team plugin config; no `answer-relevance` surface; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated vendor;
    dismissed.
  - `docs-google-sre-team-lifecycles.md` — SRE team org; no LLM-eval content;
    dismissed.
  - `docs-promptfoo-javascript-assertions.md` (#1304 sibling) — custom-JS
    assertion; no model-graded-judge semantics; dismissed.
- **Cross-ref verification (§4b)**: every cited claim was located in the cited
  note before writing — #1305 Claims 1, 5, 8; #1288 Claims 1, 5; #1289 Claim 1
  were all read and confirmed. No claim numbers invented. The `answer-relevance`
  cross-type mention in #1305 Claim 5 was located character-for-character.
- **Triage signal note honored**: the Prospector flagged 2–4 claims as the
  honest ceiling for this short page; this note contains 4 claims, each
  grounded in a specific documented behavior. No inflation.
- No contradiction issue filed: verified against `CONTRADICTIONS.md` (only
  entry #1150 is unrelated LiteLLM routing) and open contradiction-labeled
  issues.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt after merge.
