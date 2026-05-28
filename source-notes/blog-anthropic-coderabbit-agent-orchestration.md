---
source_url: https://claude.com/blog/how-coderabbit-used-claude-to-build-an-agent-orchestration-system
source_type: blog-post
title: "How CodeRabbit used Claude to build an agent orchestration system"
author: Anthropic (featuring David Loker, VP of AI at CodeRabbit)
date_published: 2026-05-27
date_extracted: 2026-05-28
last_checked: 2026-05-28
status: current
confidence_overall: emerging
issue: "#975"
---

# How CodeRabbit used Claude to build an agent orchestration system

> Practitioner case study documenting CodeRabbit's multi-model orchestration
> pipeline that inserts a structured planning layer *before* code generation —
> introducing planning quality as a first-class quality gate and an
> evaluation-harness-driven model routing pattern using all three tiers of
> the Claude family.

## Source Context

- **Type**: blog-post (Anthropic's claude.com blog, May 27, 2026; case study
  in Anthropic's "how customers built with Claude" series)
- **Author credibility**: David Loker is VP of AI at CodeRabbit, a
  production-scale code review platform (2 million PRs/week, 15,000+
  customers, founded 2023 by Harjot Gill). He is describing implementation
  decisions and hard-won lessons from a live production system, not a
  prototype. The source is Anthropic-published and therefore editorially
  curated for positive framing; treat workflow patterns and design rationale
  as practitioner evidence, treat the implicit "our approach works" framing
  as marketing context. No controlled performance metrics are reported —
  all claims are qualitative or directional.
- **Scope**: Covers the design and motivation of CodeRabbit's pre-code
  planning orchestration layer: the implicit knowledge gap problem, the
  PRD-as-quality-gate pattern, multi-model routing strategy across Opus/
  Sonnet/Haiku, the plan evaluation harness, and the abstraction level
  challenge. Does NOT cover API specifics, cost figures, latency data, or
  CodeRabbit's core PR review product. Does NOT include code examples or
  configuration artifacts.

## Extracted Claims

### Claim 1: Experienced developers make implicit assumptions AI agents do not share — the agent fills those gaps with whatever seems plausible, producing code that compiles and tests but misses the actual requirement

- **Evidence**: Direct quote from David Loker (VP of AI, CodeRabbit) with a
  concrete anecdote: a developer built a memory system that required users but
  never stated users needed a login page; the agent filled the gap and hours
  of work produced a product missing authentication.
- **Confidence**: anecdotal (single practitioner account, but the failure mode
  is structurally coherent and widely reported; Loker's framing as a general
  pattern, not a one-time mistake, adds weight)
- **Quote**: "As we gain experience as developers, we internalize knowledge.
  All those things are in our head, and we assume other developers know them
  too. But then we make that assumption of the AI system as well, that it
  also implicitly understands. We're not even aware that we're assuming those
  things."
- **Our assessment**: This names the specific failure mode responsible for
  the "code works but doesn't solve the problem" outcome. The framing — that
  developers do not know they are making implicit assumptions — is why simple
  prompting improvements (be more specific) are not sufficient alone. A
  structured process that externalizes assumptions is the only reliable fix.
  This is also the demand-side motivation for the entire planning-layer
  architecture; without this problem well-characterized, the solution looks
  like over-engineering.

### Claim 2: Late validation in AI workflows is especially expensive because generated code quickly accumulates on a misaligned foundation

- **Evidence**: Direct quote from David Loker with a mechanics explanation.
  The problem is not just discovering a bug late — it is that each AI-generated
  increment is built on top of earlier increments, so an assumption buried in
  the foundation compounds.
- **Confidence**: anecdotal (single practitioner framing; logically coherent)
- **Quote**: "What ends up happening is you build a lot more stuff on top of
  it, then much later you find there's a problem. In AI workflows, late
  validation can be very expensive."
- **Our assessment**: This is the economic argument for shifting validation
  upstream. The claim is stronger for AI workflows than for traditional
  development because AI code generation is fast — a developer who spends an
  hour going in the wrong direction might produce a day's equivalent of
  traditional code, all of which must be re-evaluated when the mismatch is
  discovered. The compounding effect is inherent to the speed advantage of
  AI-native coding.

### Claim 3: A planning layer that produces a structured PRD before code generation surfaces assumptions explicitly and allows stakeholders to validate requirements before any implementation begins

- **Evidence**: CodeRabbit's production implementation, described by Loker.
  The planning layer coordinates multiple Claude models to analyze requirements,
  surface assumptions, and produce a collaborative PRD that teams review before
  implementation starts.
- **Confidence**: emerging (production implementation at scale; single company;
  no comparative metric reported)
- **Quote**: "This planning system is not meant to replace Claude Code's Plan
  Mode. It's a higher level orchestration that happens before Claude Code, to
  point it in a really narrow and right direction where everything that needs
  to be explicit is made explicit, and we are aware of all assumptions that
  are being made."
- **Our assessment**: The "higher level orchestration that happens before
  Claude Code" framing is architecturally significant. The planning layer is
  not a replacement for Claude Code's built-in planning — it is a pre-step
  that scopes and constrains what Claude Code does. This nests multi-model
  orchestration and Claude Code as two distinct layers in a pipeline, neither
  replacing the other. The explicit goal — make implicit assumptions explicit —
  is directly responsive to Claim 1. This is the first corpus source to
  document a production implementation of a pre-code planning orchestration
  layer at this level of architectural specificity.

### Claim 4: The planning layer's output is a collaborative PRD — a shared team artifact that captures decisions and rationale, which Claude Code then uses to generate a fine-grained implementation plan

- **Evidence**: Description of the output format and its downstream use.
  The PRD facilitates team alignment and knowledge transfer for new engineers.
- **Confidence**: emerging (architectural description from practitioner; the
  team-artifact framing adds a collaboration dimension absent from most
  single-agent planning approaches)
- **Quote**: (no single direct quote; described as "a shared artifact that
  captures what was decided and why" in article narrative)
- **Our assessment**: The PRD-as-shared-artifact pattern transforms an AI
  planning output from an ephemeral prompt into a durable, reviewable document.
  This has two distinct values: (1) human stakeholders can validate before
  implementation begins (catching misalignments before code is written), and
  (2) the document becomes institutional memory for what was decided and why,
  useful for future engineers. The handoff to Claude Code (which then generates
  a fine-grained implementation plan from the PRD) is a clear two-stage
  orchestration pattern: strategic planning in the orchestration layer,
  tactical planning in Claude Code.

### Claim 5: Planning quality is a direct upstream determinant of code quality — high-quality plans produce substantially better code at the end of the pipeline

- **Evidence**: Direct quote from Loker stating the team's core empirical
  observation after building and operating the planning layer.
- **Confidence**: emerging (practitioner directional claim from production
  operation; no quantitative metric, but framed as an observed relationship
  rather than a theory)
- **Quote**: "What we've built, using the Claude ecosystem, is a team-wide
  planning system. The plan itself becomes a quality gate. If we can make
  sure the quality of that plan is really good upfront, the downstream effect
  is very pronounced. You end up with a lot better code at the end of it."
- **Our assessment**: "The downstream effect is very pronounced" is the key
  evidential claim. It positions planning quality, not code generation model
  quality, as the primary lever for output quality. If this holds, it has
  significant implications for where practitioners should invest optimization
  effort: improving the planning step may return more quality per dollar than
  switching to a more expensive code generation model. This would make eval
  harnesses for plan quality (Claim 8) a first-priority engineering investment.

### Claim 6: As code generation gets cheaper, the cost of moving in the wrong direction increases proportionally — making planning quality more economically valuable over time

- **Evidence**: Direct quote from the article framing the core economic thesis.
- **Confidence**: anecdotal (logical argument, not measured; but the direction
  of the argument is coherent and follows from Claim 2)
- **Quote**: "the cheaper code generation gets, the more expensive it becomes
  to move in the wrong direction"
- **Our assessment**: This is the most quotable claim in the article and the
  most important for the guide's framing of AI-native engineering economics.
  The implication is that planning infrastructure is an appreciating investment:
  as models improve and code generation accelerates, the relative cost of
  rework increases, making early-stage validation more valuable. Practitioners
  who defer building planning and validation infrastructure are making an
  economically irrational bet.

### Claim 7: CodeRabbit routes tasks across the Claude model family by task complexity — Opus for orchestration and strategic problem-understanding, Sonnet for sequencing, Haiku for narrowly-scoped operations like context distillation

- **Evidence**: Direct description from Loker of the three-tier routing
  strategy in production.
- **Confidence**: emerging (production routing strategy from a large-scale
  deployment; single company; no cost/quality trade-off data reported)
- **Quote**: (no single direct quote; routing described in article section
  "Routing Across the Claude Model Family" with Opus = orchestration loops
  and strategic problem-understanding, Sonnet = sequencing orchestration
  output into structured steps, Haiku = context distillation and targeted
  tool use)
- **Our assessment**: The notable architectural choice is Opus at the
  orchestration layer, not Haiku. This is the inverse of Spiral's assignment
  in `blog-anthropic-managed-agents-dreaming-outcomes.md` (Claim 8), where
  Haiku orchestrates and Opus generates. The difference is task type: Spiral's
  orchestration is routing and delegation (routing can be cheap); CodeRabbit's
  orchestration is strategic reasoning about requirements (reasoning requires
  Opus). The shared principle is the same — match model capability to task
  requirements — but the correct assignment depends on what orchestration
  actually involves in the specific pipeline.

### Claim 8: Model selection should be evaluation-harness-driven, not intuited — the team uses their plan quality eval to confirm which model assignment actually improves output

- **Evidence**: Direct quote from Loker on their decision process for model
  routing.
- **Confidence**: emerging (described as their explicit methodology; represents
  a more rigorous approach than most practitioners apply to model selection)
- **Quote**: "If Haiku does as well as Sonnet on a given task, we use Haiku.
  If the evaluation harness tells us the plan quality improves when we give
  Opus more room, we give it more room. We don't guess."
- **Our assessment**: "We don't guess" is the key phrase. This operationalizes
  model routing as an empirical question with a measurable answer (plan quality
  score) rather than a theoretical question about model capability. It also
  implies that the eval harness (Claim 9) is not just a monitoring tool — it
  is the feedback loop that drives architectural decisions about model
  assignments. This is a mature engineering posture: most practitioners make
  model routing decisions once at architecture time, based on intuition. Loker's
  team treats it as an ongoing empirically validated choice.

### Claim 9: Evaluating intermediate outputs (plan quality) requires purpose-built infrastructure — CodeRabbit built a library of LLM judges scoring specific plan dimensions, validated against downstream code outcomes

- **Evidence**: Description of their eval harness development process: "The
  system started with hand-tuned examples and manual inspection. The team
  developed a library of LLM judges that scored specific dimensions of plan
  quality." The team also measured code correctness, extra scope, and token
  consumption to correlate plan quality with downstream code outcomes.
- **Confidence**: emerging (production infrastructure description; no
  methodology details reported; the approach is concrete and specific enough
  to be credible)
- **Quote**: (no single direct quote spanning the full description; described
  across the "Building an Eval Harness for Plan Quality" section)
- **Our assessment**: Building eval infrastructure for intermediate pipeline
  outputs (plans, not final code) is architecturally distinct from evaluating
  final code outputs. Most practitioners evaluate at the end (does the code
  work?); CodeRabbit evaluates in the middle (is the plan good?). The LLM-
  judge-per-dimension approach is analogous to the plan quality rubric pattern
  in `blog-anthropic-harness-long-running.md` Claim 4 (sprint contracts for
  evaluators), but applied one stage earlier — at plan generation rather than
  code generation. The correlation measurement (run same task with/without
  planning step; compare code outcomes) is the methodologically strongest
  part of this claim: it provides causal evidence for planning's contribution
  rather than measuring plan quality in isolation.

### Claim 10: Finding the right plan abstraction level is a non-trivial challenge — plans too granular go stale when the codebase shifts; plans too high-level reintroduce the assumption-filling problem the planning layer was built to solve

- **Evidence**: Direct quote from Loker describing the team's iterative
  discovery of this trade-off through production experience.
- **Confidence**: emerging (first-person observation from production; the
  failure modes described are logically coherent and mutually exclusive)
- **Quote**: "We didn't realize what the right level of detail was going to
  be for that plan. Plans that were too granular went stale the moment the
  codebase shifted. Plans that were too high-level left room for the agent
  to fill in assumptions, which was the original problem the planning layer
  was meant to solve."
- **Our assessment**: This is the most operationally specific claim in the
  article and the most useful for practitioners implementing planning layers.
  The failure modes are symmetric and mutually opposing: increase granularity
  to reduce assumption-filling, but granularity creates staleness risk; reduce
  granularity to reduce staleness, but that re-enables assumption-filling.
  The right level must be empirically discovered for each codebase and team.
  No heuristic is given; the implication is that this requires iterative
  calibration using an eval harness (Claim 9) to detect which failure mode
  is dominating.

## Concrete Artifacts

### CodeRabbit's Multi-Model Pipeline Architecture

```
CodeRabbit Agent Orchestration Pipeline (David Loker, VP AI, 2026)
Source: Anthropic blog, May 27, 2026

LAYER 0: Developer provides requirements (implicit assumptions present)

LAYER 1: Pre-Code Planning Orchestration (multi-model)
  Purpose: surface implicit assumptions; create structured plan
  Models:
    Opus    → orchestration loops, strategic problem-understanding
    Sonnet  → sequencing orchestration output into structured steps
    Haiku   → context distillation, targeted narrowly-scoped tool use
  Output: collaborative PRD (product requirements document)
          - shared artifact capturing what was decided and why
          - reviewed by stakeholders before implementation
          - serves as knowledge transfer for new engineers

LAYER 2: Claude Code
  Input: PRD from Layer 1
  Action: generates fine-grained implementation plan from PRD
  Then: generates code from implementation plan

KEY PROPERTY: Layer 1 runs BEFORE Layer 2; it is not a replacement
for Claude Code's built-in Plan Mode but a higher-level pre-step.

Source: CodeRabbit case study, claude.com blog, 2026-05-27
```

### Plan Evaluation Harness (from post)

```
CodeRabbit Plan Quality Evaluation Infrastructure
Source: Anthropic blog, May 27, 2026

DEVELOPMENT APPROACH:
  Phase 1: Hand-tuned examples + manual inspection (bootstrap)
  Phase 2: Library of LLM judges, each scoring specific plan dimensions
  Phase 3: Correlation with downstream code outcomes

MEASUREMENTS:
  Plan quality:   LLM judges per dimension (dimensions not named)
  Code quality:   correctness, extra scope, token consumption

CAUSAL VALIDATION METHOD:
  Run same task with and without planning step
  → compare code outcomes to isolate planning's contribution

MODEL ROUTING USE:
  Eval results drive model assignment per task
  "If Haiku does as well as Sonnet on a given task, we use Haiku."
  "If the evaluation harness tells us the plan quality improves when
   we give Opus more room, we give it more room. We don't guess."

Source: CodeRabbit case study, claude.com blog, 2026-05-27
```

### Model Routing Strategy — CodeRabbit vs. Spiral (comparison)

```
Two production multi-model routing strategies (both Claude ecosystem):

CODERABBIT (code planning pipeline):
  Opus    → orchestration / strategic reasoning about requirements
  Sonnet  → sequencing / structuring steps
  Haiku   → context distillation / narrow tool use
  Principle: high reasoning tasks need Opus at the orchestration layer

SPIRAL BY EVERY (content drafting pipeline, per managed-agents-dreaming-outcomes):
  Haiku   → lead orchestrator (routing, follow-up questions)
  Opus    → specialist subagents (drafting, parallel)
  Principle: routing can be cheap; generation quality needs Opus

SHARED PRINCIPLE (both cases):
  Match model capability to actual task requirements
  Use eval to confirm assignments, not intuition

Implication: "Opus at orchestration" vs. "Haiku at orchestration" is
a conditioning variable on what orchestration actually involves —
strategic reasoning vs. simple routing.

Source: CodeRabbit (claude.com blog 2026-05-27) and
        Spiral (managed-agents announcement 2026-05-06)
```

## Cross-References

- **Corroborates**:
  - `blog-anthropic-harness-long-running.md` Claim 1: "agents tend to respond
    by confidently praising the work—even when, to a human observer, the
    quality is obviously mediocre" — CodeRabbit's Claim 9 (LLM judges for
    plan quality) is independently motivated by the same insight: the model
    generating output cannot reliably evaluate its own output. CodeRabbit
    applies this principle one stage earlier (plan evaluation, not code
    evaluation) but the architectural motivation is identical.
  - `blog-anthropic-harness-long-running.md` Claim 3: planner as the most
    stable component of the generator/evaluator architecture. CodeRabbit's
    planning layer is a practitioner independent validation: their planning
    step is also the component that shapes everything downstream and is the
    primary quality lever. Two independent production systems converge on
    "planning first" as the architectural insight.
  - `blog-anthropic-multi-agent-coordination-patterns.md` Claim 7: "For most
    use cases, we recommend starting with orchestrator-subagent. It handles
    the widest range of problems with the least coordination overhead."
    CodeRabbit's pipeline is a practitioner implementation of orchestrator-
    subagent for the planning stage, with Opus as the orchestrator and
    Sonnet/Haiku as bounded specialists.
  - `blog-anthropic-managed-agents-dreaming-outcomes.md` Claim 8: Spiral's
    Haiku (lead orchestrator) + Opus (specialists) pattern establishes that
    mixing models across orchestration levels is production-validated.
    CodeRabbit confirms the same principle with a different assignment —
    corroborating the general pattern while demonstrating that the correct
    assignment is task-dependent.

- **Contradicts**: None filed. The apparent reversal of model assignments
  (CodeRabbit: Opus at orchestration vs. Spiral: Haiku at orchestration) is
  a conditioning variable on orchestration task type (strategic reasoning vs.
  routing), not a factual contradiction about which model should be used.
  Both cases are consistent with the shared principle: match model capability
  to task requirements.

- **Extends**:
  - `blog-anthropic-harness-long-running.md` Claim 4 (sprint contracts —
    agree what "done" looks like before code is written): CodeRabbit's PRD
    pattern is a more upstream version of this same idea. Sprint contracts
    define done for a sprint; PRDs define done for a feature before any sprint
    begins. The planning-as-quality-gate pattern extends the sprint-contract
    pattern one stage earlier in the pipeline.
  - `blog-anthropic-harness-long-running.md` Claim 6 (evaluator quality
    requires intensive prompt tuning): CodeRabbit's plan eval harness (Claim 9
    in this note) independently arrived at the same finding — evaluation
    infrastructure for AI outputs requires purpose-built, carefully tuned
    machinery, not off-the-shelf prompting.
  - `blog-anthropic-multi-agent-coordination-patterns.md` Claim 7 (orchestrator-
    subagent as recommended default): CodeRabbit adds a concrete production
    implementation of this pattern specifically for the planning stage, with
    named model assignments per role and an eval-driven approach to confirming
    those assignments.

- **Novel**:
  - **Planning layer as a distinct pipeline stage before Claude Code**: No
    prior corpus source documents a production pre-code planning orchestration
    layer that takes developer requirements and outputs a stakeholder-reviewed
    PRD as Claude Code's input. The architectural pattern — multi-model
    planning → PRD → Claude Code → implementation plan → code — is new to
    the corpus.
  - **Evaluation of intermediate outputs (plan quality) as a first-class
    engineering investment**: Prior corpus sources evaluate final code outputs.
    CodeRabbit's approach of building LLM judges for plan quality, then
    correlating with code outcomes, is a new pattern for the corpus.
  - **"We don't guess" as an explicit methodology for model routing**: The
    principle of using eval-harness feedback to drive model assignments
    (rather than intuiting from model capability descriptions) is a
    methodological standard not previously stated explicitly in the corpus.
  - **The abstraction level trade-off for plans**: The specific failure mode
    pair — too granular goes stale, too high-level reintroduces assumption-
    filling — is new to the corpus and directly actionable for practitioners
    building planning layers.
  - **Planning quality as economically appreciating**: The claim that cheaper
    code generation makes planning investment *more* valuable (because the
    cost of wrong-direction work scales with generation speed) is a novel
    economic framing not found in prior corpus sources.

## Guide Impact

- **Chapter 02 (Harness Engineering)**: Add CodeRabbit's pipeline architecture
  (Concrete Artifacts → Architecture section) as a named pattern: pre-code
  planning orchestration. The guide currently documents generator/evaluator
  and orchestrator-subagent as the primary patterns; pre-code planning is a
  third pattern that complements both. The PRD-as-shared-artifact dimension
  adds a team-coordination benefit not present in the single-developer
  generator/evaluator pattern.

- **Chapter 02 (Harness Engineering)**: Add the "intermediate output evaluation"
  pattern (Claim 9) alongside code evaluation. The guide's harness engineering
  content currently focuses on evaluating final outputs. CodeRabbit's approach
  of evaluating plan quality (with LLM judges, hand-tuned examples, and
  downstream correlation) should be documented as an alternative evaluation
  target for pipelines with explicit planning stages.

- **Chapter 04 (Multi-Agent Orchestration)**: Add the eval-driven model
  routing methodology (Claim 8) as a best practice. The guide currently
  describes model routing patterns (from `blog-anthropic-managed-agents-
  dreaming-outcomes.md` and `blog-anthropic-multi-agent-coordination-patterns.md`);
  it should add the explicit principle: use an evaluation harness to confirm
  model assignments rather than deriving them from model capability descriptions
  alone.

- **Chapter 04 (Multi-Agent Orchestration)**: Add the model assignment
  conditioning variable (Concrete Artifacts → Comparison section) when
  discussing Opus-at-orchestration vs. Haiku-at-orchestration. Both are
  production-validated; the correct assignment depends on what orchestration
  involves (strategic reasoning vs. routing). The guide should prevent the
  prescriptive error of recommending one assignment as universal.

- **Chapter 06 (Evaluation & Measurement)**: Add the abstraction level
  trade-off for plans (Claim 10) as a calibration challenge for practitioners
  building planning layers. The guide should note that the right abstraction
  level must be empirically discovered per codebase/team — it cannot be
  derived from first principles.

- **Chapter 01 (AI-Native Engineering Economics)** or equivalent: Add Claim 6
  ("the cheaper code generation gets, the more expensive it becomes to move
  in the wrong direction") as a framing device for why validation and planning
  investment is economically rational and increasingly so as models improve.

## Extraction Notes

- The source does not include code examples, configuration artifacts, or
  specific API/SDK details. All artifacts in the Concrete Artifacts section
  are reconstructed from the prose description, clearly attributed to the
  source.
- The article's promotional framing (Anthropic case study) means all positive
  outcomes are reported without baseline comparisons or controlled metrics.
  Treat "very pronounced downstream effect" (Claim 5) and all directional
  quality claims as practitioner-observed direction, not measured performance.
- David Loker is the sole named source for all claims. No CodeRabbit
  engineering team members, no customer quotes, no external validators.
- The source was read fully. The article is self-contained with no linked
  sub-pages. Reading time on page is stated as 5 minutes; the extraction
  reflects the full article depth.
- The model routing comparison (Concrete Artifacts → Comparison) cites
  `blog-anthropic-managed-agents-dreaming-outcomes.md` Claim 8 for the
  Spiral/Haiku+Opus pattern. This cross-reference was verified against
  that note before writing.
