---
source_url: https://github.github.com/gh-aw/experimental/correction-ops/
source_type: docs
title: "GitHub Agentic Workflows: CorrectionOps Pattern"
author: GitHub Agentic Workflows team (GitHub Next / Microsoft Research)
date_published: null
date_extracted: 2026-05-24
last_checked: 2026-05-24
status: current
confidence_overall: emerging
issue: "#468"
---

# GitHub Agentic Workflows: CorrectionOps Pattern

> An experimental gh-aw pattern that closes a human-feedback loop around an
> agentic workflow — capturing agent predictions, diffing them against later
> human corrections, and using that evidence to update instructions, thresholds,
> and rollout gates — without retraining the underlying model.

## Source Context

- **Type**: docs (official GitHub Agentic Workflows documentation, in the
  `experimental/` section — the URL was originally `patterns/correction-ops`
  and now redirects to `experimental/correction-ops/`, reflecting the pattern's
  explicitly experimental status. The page carries a warning that "the guidance
  and workflow shape on this page may change as the pattern is tested in more
  real-world workflows." First-party source from the same team behind the
  `gh aw` CLI, Peli de Halleux's Agent Factory series, and all GHAW `patterns/`
  documentation.)
- **Author credibility**: GitHub Next / Microsoft Research — authoritative for
  the `gh aw` platform. The CorrectionOps pattern is a first-party, named
  experimental pattern, not a community contribution. The experimental
  designation signals that specific implementation guidance may change but that
  the concept is intentionally documented and intended for practitioner use.
  Claims about the platform's Safe Outputs, staged mode, and cross-repository
  reads are settled; the pattern-level design choices (four workflow classes,
  contract definitions) are practitioner recommendations subject to revision.
- **Scope**: Covers the CorrectionOps pattern — definition, when to apply it,
  two-surface architecture, four workflow classes with their responsibilities,
  four stable contracts that must be defined before adding rollout logic, the
  deterministic/agentic split rule, and the rollout progression starting in
  staged mode. Does NOT cover: staged mode YAML syntax in detail (see Staged
  Mode reference), Safe Outputs configuration depth (see Safe Outputs Reference),
  or cross-repository read specifics (see GitHub Tools reference). Does not
  include a downloadable reference implementation — this is a pattern page, not
  a `githubnext/` repo with workflow files.

## Extracted Claims

### Claim 1: CorrectionOps is an explicitly experimental gh-aw pattern for improving the workflow around the model rather than retraining it — it captures predictions, compares them against later human corrections, and uses the evidence to update instructions and rollout choices

- **Evidence**: The page opens with both the definition and an experimental
  caution. The two sentences in the source are the core claim and the scope
  limiter that governs all downstream guidance.
- **Confidence**: emerging (first-party documentation with an explicit
  experimental caution — the concept is settled, the specific implementation
  guidance is subject to change)
- **Quote**: "CorrectionOps improves the workflow _around_ the model rather
  than retraining it."
- **Our assessment**: This single sentence is the decisive architectural
  commitment of the pattern. Every implementation detail follows from it: if
  you're not retraining the model, your improvement levers are the instruction
  text, the routing logic, and the rollout gates — all of which are
  deterministic configuration artifacts that can be updated without model
  infrastructure. The constraint that humans remain authoritative correctors
  (not the model) means the feedback signal is explicit human edits, not
  synthetic ratings. For Ch02 (agent design and iteration): CorrectionOps is
  the named pattern for instruction-level improvement using production
  corrections as signal — the concrete alternative to fine-tuning for
  instruction-following tasks.

### Claim 2: CorrectionOps applies when humans retain decision authority and workflows need iterative improvement — the listed use cases are labeling and classification, routing and prioritization, moderation and approvals, and summaries or recommendations that humans later correct

- **Evidence**: The "When to Use CorrectionOps" section provides both the
  abstract applicability condition and a concrete four-item use-case enumeration.
- **Confidence**: emerging (first-party; the enumeration is illustrative rather
  than exhaustive)
- **Quote**: "labeling and classification, routing and prioritization, moderation
  and approvals, and summaries or recommendations that humans later correct"
- **Our assessment**: The common thread across these use cases is that (1) the
  agent makes a *prediction* at one point in time and (2) a human makes the
  *actual decision* at a later point in time, creating a natural prediction/truth
  pair. This structure is not present in all agentic workflows — code generation
  and document drafting, for instance, do not have a clean "later human truth"
  event that can be diffed against the prediction. CorrectionOps requires a
  workflow shape where human corrections are observable, attributable, and
  distinguishable from other edits. For Ch04 (production patterns and feedback
  loops): document CorrectionOps' applicability condition as "workflows where
  humans make explicit post-hoc corrections to agent decisions" — this is the
  gating criterion.

### Claim 3: The two-surface architecture places production as the authoritative source and ops as the improvement hub — production starts read-only, with direct writes enabled only after promotion

- **Evidence**: The "How It Works" section describes the two-surface setup as
  the required architecture for "a clean CorrectionOps setup." The initial
  state (ops cannot write to production) and the terminal state (direct writes
  after promotion) are both specified.
- **Confidence**: emerging (first-party practitioner guidance; the qualifier
  "clean" signals this is a recommended shape, not a platform enforcement)
- **Quote**: "A clean CorrectionOps setup has two long-lived surfaces.
  Production stays authoritative. Ops hosts prediction, correction intake,
  reporting, instruction updates, and rollout control — initially without
  writing back to production, later with direct writes once promoted."
- **Our assessment**: The "two long-lived surfaces" framing is architecturally
  important: both repositories persist over the entire lifetime of the workflow,
  not just during rollout. The ops repository is not a temporary shadow target
  (cf. `docs-ghaw-safe-rollout.md` Claim 9, which requires shadow targets to
  remain thin and disposable) — it is a permanent improvement infrastructure
  alongside production. This is a distinct role from the shadow target in the
  safe rollout ladder: the ops repository in CorrectionOps persists predictions
  and corrections indefinitely, accumulating the evidence base for instruction
  updates. For Ch02: the production + ops two-surface pattern is the canonical
  CorrectionOps infrastructure shape — document it with the distinction that the
  ops repository is permanent, not a temporary rollout artifact.

### Claim 4: The relay workflow must be purely deterministic — it forwards stable facts and provenance from production to ops without inference, diffing, or correctness decisions

- **Evidence**: The first of the four workflow classes is defined with an
  explicit prohibition on what it must NOT do, making the determinism
  requirement concrete rather than abstract.
- **Confidence**: settled (first-party documentation; the prohibition is stated
  as a design rule, not a recommendation)
- **Quote**: "Forwards stable facts and provenance into ops — no diffs, no
  intent inference, no correctness decisions."
- **Our assessment**: The relay workflow is the boundary between production and
  ops — and the rule that it must be purely deterministic is the load-bearing
  constraint that keeps the ops improvement loop from corrupting production
  data. "No intent inference" is the strongest prohibition: the relay must not
  make any judgment about what the event means; it only records what happened
  (source/object identity, event type, actor facts, timestamps). This connects
  directly to `docs-ghaw-deterministic-agentic-patterns.md` Claim 1 (the
  three-stage hybrid pipeline's first stage is deterministic) — the relay is
  the deterministic pre-processor that feeds the prediction workflow. For Ch02:
  the relay's determinism is the first design rule for any CorrectionOps
  implementation — teams that add inference to the relay will corrupt the
  feedback signal.

### Claim 5: The prediction workflow applies current instructions to normalized inputs and persists a durable prediction snapshot that records both the prediction and the instruction version that produced it

- **Evidence**: The prediction workflow description and the corresponding
  contract definition in the "Stable Contracts To Define First" section both
  specify the snapshot structure.
- **Confidence**: settled (first-party; the snapshot requirement is specified
  in both the workflow class description and the contract definition — two
  independent points of consistency)
- **Quote**: "applies the current instructions to normalized inputs and persists
  a durable prediction snapshot" / "durable record of the prediction and the
  instruction version that produced it"
- **Our assessment**: The instruction version field in the prediction snapshot
  is architecturally critical: it enables the review/compare workflow to
  attribute later corrections not just to "the agent was wrong" but to "the
  agent was wrong under instruction version X." Without the version field, you
  cannot determine whether a correction is evidence that the instructions need
  updating or evidence that the model is making random errors under stable
  instructions. The "durable" qualifier connects to `docs-ghaw-safe-rollout.md`
  Claim 7 ("persist what the workflow predicted at decision time — do not
  reconstruct predictions from logs") — CorrectionOps operationalizes this
  design rule as a required workflow component. For Ch04: the prediction
  snapshot with instruction version is the standard artifact for any workflow
  that intends to use human corrections as improvement signal.

### Claim 6: The review/compare/decide workflow builds deterministic diffs from predictions and later human truth, then invokes the agent for semantic judgment — pattern summarization and instruction-update proposals

- **Evidence**: The third workflow class description specifies both the
  deterministic diffing step and the agentic semantic judgment step in a
  single workflow, showing where the deterministic/agentic boundary falls
  within this workflow.
- **Confidence**: settled (first-party documentation; the division is explicit)
- **Quote**: "builds deterministic diffs from predictions and later human truth,
  then asks the agent to summarize patterns or propose instruction updates"
- **Our assessment**: This workflow class is where the actual improvement
  happens — and the design choice to split it into deterministic diffing first
  and then agentic summarization is the key architectural commitment. The agent
  is not asked to diff anything (that would introduce interpretation bias into
  the comparison); it is asked to make sense of a deterministically computed
  diff. This constrains the agent's input to "here is a precise record of what
  you predicted vs. what humans decided — identify patterns." For Ch04
  (production patterns and feedback loops): this is the workflow that closes
  the loop. The input is a deterministic diff artifact; the output is either
  a narrative summary or a proposed instruction update — both are safe-output
  candidates that humans review before applying.

### Claim 7: The optional collector workflow handles truth-feedback triggers that need their own trigger, permissions, or write path — separating the correction-collection boundary from the prediction and review workflows

- **Evidence**: The fourth workflow class is explicitly marked "optional" with
  a specific condition for when to add it.
- **Confidence**: settled (first-party documentation; the condition is stated
  precisely)
- **Quote**: "Add a separate collector when the later-truth boundary needs its
  own trigger, permissions, or write path."
- **Our assessment**: The optional collector handles the case where the
  "later human truth" signal cannot be captured by the existing workflows. For
  example, if human corrections happen in a different system (an external issue
  tracker, a moderation dashboard) that requires different OAuth scopes, the
  collector provides the bridge without contaminating the relay or prediction
  workflows with those permissions. The "trigger" condition covers the case
  where corrections arrive asynchronously — a batch of label corrections might
  be exported nightly rather than triggered per-edit. For Ch02: document the
  optional collector as the escape valve for correction-collection patterns
  that don't fit cleanly into the relay trigger model.

### Claim 8: All four stable contracts — relay payload, prediction snapshot, correction review input, and rollout gate contract — must be defined before adding rollout logic

- **Evidence**: The "Stable Contracts To Define First" section names all four
  contracts and provides a definition for each, with the explicit guidance
  that these must precede rollout logic.
- **Confidence**: settled (first-party; the four contracts are each specified
  with their required fields or properties)
- **Quote (relay payload)**: "minimal source/object identity, event type, actor
  facts, and timestamps forwarded into ops"
- **Quote (prediction snapshot)**: "durable record of the prediction and the
  instruction version that produced it"
- **Quote (correction review input)**: "deterministic diff artifact consumed by
  reporting and adaptation"
- **Quote (rollout gate contract)**: "evidence or approvals required before
  direct production writes are enabled"
- **Our assessment**: The contract-first requirement is an important sequencing
  rule: rollout logic (what triggers a promotion from staged to production
  writes) depends on the shape of the evidence you're collecting, which depends
  on the snapshot and correction review input contracts. Teams that add rollout
  gates before defining these contracts will build evaluation logic around
  ambiguous evidence. The rollout gate contract's "evidence or approvals"
  language is notable: the gate can be quantitative (N corrections without
  disagreement) or qualitative (maintainer approval). For Ch04: the four
  contracts are the design-time checklist before implementing CorrectionOps —
  all four must be stable before the pattern can be iterated on safely.

### Claim 9: The deterministic/agentic split rule requires relays, diffing, and grouping to be deterministic — only semantic judgment is delegated to the agent

- **Evidence**: The page states this as a key design principle in the "How It
  Works" section, applicable across all four workflow classes.
- **Confidence**: settled (first-party; stated as a design rule, not a
  recommendation)
- **Quote**: "Keep relays, diffing, and grouping deterministic; use the agent
  for semantic judgment only."
- **Our assessment**: This rule is the most important operational constraint
  in the pattern. It defines the agent's role in the feedback loop as
  interpretation only — not collection, not comparison, not routing. The agent
  answers "what patterns do these diffs show?" and "what should the instructions
  say instead?" — never "what is the diff?" or "which corrections should be
  grouped?". Grouping is explicitly deterministic: corrections are clustered by
  an objective criterion (e.g., same label, same actor type, same time window)
  before the agent sees them. This extends `docs-ghaw-deterministic-agentic-patterns.md`
  Claim 1 (three-stage hybrid pipeline) to the correction-processing domain:
  the correction intake and diffing are Stage 1 (deterministic), the pattern
  summarization and instruction-proposal are Stage 2 (agentic). For Ch02:
  the deterministic/agentic split rule should be stated alongside the four
  workflow classes as the first design principle of CorrectionOps.

### Claim 10: CorrectionOps is explicitly distinguished from RLHF — it adjusts instructions, thresholds, and safe-output routing rather than model weights, and requires no separate evaluation repository

- **Evidence**: The source's "Key Distinction" section provides a direct
  contrast with RLHF, specifying both what CorrectionOps changes (instructions,
  thresholds, routing) and what it avoids (model weight changes, separate
  evaluation repository).
- **Confidence**: settled (first-party; a named contrast with a specific
  alternative approach)
- **Quote**: (no direct quote available for the full comparison; key elements
  are: "unlike RLHF approaches that modify model weights," "adjusts
  instructions, thresholds, and safe-output routing," and "no separate
  evaluation repository required")
- **Our assessment**: The RLHF comparison is strategically important for
  practitioners: it positions CorrectionOps as a lightweight alternative for
  teams that cannot run fine-tuning infrastructure. The three levers
  (instructions, thresholds, routing) map to specific gh-aw configuration
  artifacts — instruction markdown files (updatable via PR), rollout gate
  thresholds (evidence counts, approval requirements), and staged-mode routing
  (which outputs go through safe-output review). None of these require model
  access. For Ch04: CorrectionOps should be presented as the instruction-level
  improvement path — accessible to any team with a gh-aw deployment, requiring
  no ML infrastructure investment.

### Claim 11: CorrectionOps deployments start in staged mode before promoting to direct production writes — the rollout progression follows the gh-aw safe rollout ladder

- **Evidence**: The page's "When to Apply It" section specifies staged mode as
  the starting point, and the related documentation links to the Staged Mode
  reference as the rollout companion guide.
- **Confidence**: settled (first-party; staged mode is specified as the starting
  point, and the related links confirm Staged Mode as the companion reference)
- **Quote**: (no direct quote; the page states the pattern "works best with
  gradual rollouts starting in staged mode before promoting to direct production
  writes")
- **Our assessment**: This connects CorrectionOps directly to
  `docs-ghaw-safe-rollout.md` — the safe rollout ladder applies to CorrectionOps
  as the trust-promotion framework. The rollout gate contract (Claim 8, fourth
  contract) is the CorrectionOps-specific specification for what "enough evidence"
  means before promoting from staged to production writes. The integration is
  clean: staged mode provides the safety mechanism (no production writes during
  evaluation); the correction evidence accumulated in ops provides the signal
  for promotion. For Ch04: CorrectionOps should be presented with the staged
  mode starting point as a required first step — teams that skip staged mode
  and deploy directly to production writes cannot collect the correction evidence
  needed to improve the workflow.

## Concrete Artifacts

### CorrectionOps Page Warning (verbatim)

```
"CorrectionOps is an experimental pattern. The guidance and workflow shape
on this page may change as the pattern is tested in more real-world workflows."
```

*Source: experimental status warning at top of `github.github.com/gh-aw/experimental/correction-ops/`*

### Two-Surface Architecture (from source)

```
Production repository: authoritative events, later human truth
Ops repository: prediction, correction intake, reporting,
                instruction updates, rollout control

Initial state: Ops cannot write to production
Terminal state: Direct writes enabled after promotion through
                staged mode and evidence thresholds
```

*Source: "How It Works" section — `github.github.com/gh-aw/experimental/correction-ops/`*

### Four Workflow Classes (from source, verbatim descriptions)

```
1. Relay Workflow (production repo)
   "Forwards stable facts and provenance into ops — no diffs, no intent
   inference, no correctness decisions."
   Relay payload contract: "minimal source/object identity, event type,
   actor facts, and timestamps forwarded into ops"

2. Prediction Workflow (ops repo)
   "applies the current instructions to normalized inputs and persists a
   durable prediction snapshot"
   Prediction snapshot contract: "durable record of the prediction and
   the instruction version that produced it"

3. Compare, Report, And Decide Workflow (ops repo)
   "builds deterministic diffs from predictions and later human truth,
   then asks the agent to summarize patterns or propose instruction updates"
   Correction review input contract: "deterministic diff artifact consumed
   by reporting and adaptation"

4. Optional Deterministic Collector (ops repo)
   "Add a separate collector when the later-truth boundary needs its own
   trigger, permissions, or write path."
```

*Source: example section (issue labeling example) — `github.github.com/gh-aw/experimental/correction-ops/`*

### Stable Contracts (from source, verbatim)

```
Four contracts to define before adding rollout logic:

1. Relay payload:         "minimal source/object identity, event type,
                           actor facts, and timestamps forwarded into ops"

2. Prediction snapshot:   "durable record of the prediction and the
                           instruction version that produced it"

3. Correction review      "deterministic diff artifact consumed by
   input:                  reporting and adaptation"

4. Rollout gate contract: "evidence or approvals required before direct
                           production writes are enabled"
```

*Source: "Stable Contracts To Define First" section — `github.github.com/gh-aw/experimental/correction-ops/`*

### Core Design Rule (from source, verbatim)

```
"Keep relays, diffing, and grouping deterministic; use the agent for
semantic judgment only."
```

*Source: "How It Works" section — `github.github.com/gh-aw/experimental/correction-ops/`*

### Related Documentation Links (from source)

```
- Staged Mode (/gh-aw/reference/staged-mode/)
  "safe-write rollout guidance for CorrectionOps"

- Safe Outputs Reference (/gh-aw/reference/safe-outputs/)
  "controlling write targets and protections"

- GitHub Tools (/gh-aw/reference/github-tools/)
  "cross-repository reads"
```

*Source: "Related Documentation" section — `github.github.com/gh-aw/experimental/correction-ops/`*

## Cross-References

- **Corroborates**:
  - `docs-ghaw-safe-rollout.md` Claim 6 ("Do not let the evaluation surface
    become the new source of truth. Production events and later trusted human
    actions should remain authoritative."): CorrectionOps's "Production stays
    authoritative" two-surface architecture directly implements this design
    rule. The safe rollout guide provides the abstract principle; CorrectionOps
    provides the concrete workflow shape that upholds it.
  - `docs-ghaw-safe-rollout.md` Claim 7 ("If later comparison matters, persist
    what the workflow predicted at decision time. Do not reconstruct predictions
    from logs."): CorrectionOps's prediction snapshot contract ("durable record
    of the prediction and the instruction version that produced it") is the
    concrete implementation of this design rule. The two sources independently
    specify the same requirement: explicit persisted snapshots are mandatory for
    any workflow that intends to compare predictions against human corrections.
  - `docs-ghaw-safe-rollout.md` Claim 8 ("Not every later edit should count as
    trustworthy truth. Record provenance such as actor type, manual versus
    automated source, trust status, and origin repository role."): The relay
    payload contract in CorrectionOps ("actor facts, and timestamps forwarded
    into ops") implements the provenance requirement. The safe rollout guide
    specifies what provenance fields are needed; CorrectionOps builds those
    fields into the relay payload as a required contract.
  - `blog-langchain-human-judgment-improvement-loop.md` Claim 5 ("teams get
    more leverage when humans help design and calibrate automated evaluators,
    rather than manually reviewing large volumes of agent outputs"): Both
    sources address the same fundamental problem — human review doesn't scale —
    and both resolve it by making human corrections the input to a systematic
    improvement mechanism. CorrectionOps uses corrections to update instructions
    directly; the LangChain post uses corrections to calibrate evaluators. The
    two approaches are complementary: CorrectionOps is the right tool when you
    want to improve the workflow's instruction text; the LangChain evaluator
    approach is the right tool when you want to build an automated quality gate.
  - `blog-langchain-human-judgment-improvement-loop.md` Claim 11 ("After launch,
    you gain access to a much better source of test cases: real production data."
    ): CorrectionOps treats real production corrections as the primary
    improvement signal — a concrete implementation of the same principle. The
    LangChain post describes it as a general principle; CorrectionOps is the
    gh-aw-native workflow pattern that operationalizes it.

- **Extends**:
  - `docs-ghaw-deterministic-agentic-patterns.md` Claim 1 (three-stage hybrid
    pipeline as the named GHAW architecture for combining deterministic
    computation with AI reasoning): CorrectionOps applies this architecture to
    the feedback-loop domain. The relay and diffing are deterministic Stage 1;
    the semantic summarization and instruction proposal are agentic Stage 2;
    the instruction update and rollout gate change are safe-output Stage 3.
    CorrectionOps is the named specialization of the three-stage pipeline for
    the correction-loop use case.
  - `docs-ghaw-safe-rollout.md` Claim 2 (four-rung rollout ladder: report-only
    → staged → shadow → production writes): CorrectionOps uses this ladder and
    adds the rollout gate contract as the CorrectionOps-specific specification
    for what evidence is required at each rung transition. The safe rollout
    guide provides the ladder; CorrectionOps provides the feedback loop that
    accumulates the evidence needed to climb it.
  - `docs-ghaw-safe-rollout.md` Claim 10 (three-repository shape: production,
    ops, shadow): CorrectionOps's two-surface shape (production + ops) is a
    subset of this three-repository shape, without the shadow repository. The
    key difference is that CorrectionOps's ops repository is permanent (not
    disposable like a shadow target) — it accumulates correction history and
    serves as the long-lived improvement infrastructure. For teams progressing
    through the rollout ladder, a shadow repository could be added during the
    shadow evaluation phase, making the full three-repository shape relevant.

- **Contradicts**: None identified. CorrectionOps is additive to the existing
  corpus — it provides a named pattern for the feedback loop use case that no
  existing source note documents. The ops repository's permanence (Claim 3) vs.
  the safe rollout guide's disposable shadow target (Claim 9 in
  `docs-ghaw-safe-rollout.md`) is NOT a contradiction: they serve different
  roles. The ops repository in CorrectionOps is a permanent improvement
  infrastructure; the shadow target in safe rollout is a temporary write
  validation surface. No contradiction issue filed.

- **Novel**:
  - **CorrectionOps as the named gh-aw pattern for instruction-level improvement
    via human corrections** (Claim 1): No existing source note documents a
    named, structured workflow pattern for capturing human corrections and using
    them to update workflow instructions without model retraining. This is the
    first corpus entry describing the instruction-improvement loop as a deployable
    workflow architecture.
  - **The four workflow class taxonomy** (Claims 4–7): No existing source note
    enumerates relay, prediction, review/compare/decide, and optional collector
    as the four named components of a correction-driven improvement system. The
    taxonomy provides a concrete decomposition for practitioners implementing
    their own feedback loops.
  - **The four stable contracts requirement** (Claim 8): The explicit requirement
    to define relay payload, prediction snapshot, correction review input, and
    rollout gate contract before adding rollout logic is new to the corpus. This
    is the first source to specify a contract-first design requirement for an
    agentic workflow pattern.
  - **The deterministic/agentic split rule for correction processing** (Claim 9):
    The specific rule — keep relays, diffing, and grouping deterministic; use
    the agent for semantic judgment only — applied to correction-loop workflows
    is new. While `docs-ghaw-deterministic-agentic-patterns.md` documents the
    general three-stage hybrid pipeline, it does not specify this rule for
    correction-loop workflows specifically.
  - **The instruction version field in prediction snapshots** (Claim 5): The
    requirement to persist not just the prediction but the instruction version
    that produced it is not documented in any existing source note. This is a
    data quality requirement specific to iterative instruction improvement.

## Guide Impact

- **Chapter 02 (Agent Design and Iteration)**:
  - Add CorrectionOps as the named gh-aw pattern for iterative instruction
    improvement. Position it as: when your agentic workflow makes predictions
    that humans later correct (labeling, routing, moderation, summarization),
    CorrectionOps is the structured approach to turning those corrections into
    instruction updates. Distinguish it from fine-tuning: CorrectionOps changes
    the workflow's instruction text, not the model.
  - Document the deterministic/agentic split rule ("keep relays, diffing, and
    grouping deterministic; use the agent for semantic judgment only") as the
    first design principle for correction-loop workflows. This is the same
    principle as the three-stage hybrid pipeline from
    `docs-ghaw-deterministic-agentic-patterns.md` applied to the feedback-loop
    domain.
  - Add the two-surface architecture (production + permanent ops) as the
    canonical CorrectionOps infrastructure shape. Emphasize the permanence of
    the ops repository — it is not a temporary shadow target but the long-lived
    home for prediction history and correction evidence.
  - Document the four stable contracts as the design-time checklist before
    implementing CorrectionOps: relay payload (what facts flow to ops), prediction
    snapshot (what the workflow predicted and under which instruction version),
    correction review input (the deterministic diff artifact), and rollout gate
    contract (what evidence triggers promotion).

- **Chapter 04 (Production Patterns and Feedback Loops)**:
  - Add CorrectionOps as the production feedback loop pattern for gh-aw
    workflows. The chapter should describe the full loop: production events →
    relay → prediction workflow (ops) → human corrections → optional collector
    → review/compare/decide workflow → instruction update proposal → staged
    review → instruction update applied → next prediction cycle improved.
  - Document the applicability condition explicitly: CorrectionOps applies when
    workflows make predictions that humans later correct in observable, attributable
    events. The feedback loop requires a clean prediction/truth pair — workflows
    that don't produce a distinct "later human truth" event cannot use this
    pattern.
  - Add the staged mode starting point as a required first step: CorrectionOps
    deployments begin in staged mode, accumulate correction evidence, and promote
    to direct production writes only when the rollout gate contract is satisfied.
    This integrates with the safe rollout ladder from `docs-ghaw-safe-rollout.md`.
  - Cross-reference the RLHF distinction (Claim 10): CorrectionOps adjusts
    instructions, thresholds, and safe-output routing — not model weights. Teams
    that want instruction-level improvement without ML infrastructure should
    reach for CorrectionOps; teams that need model behavior changes require
    fine-tuning or RLHF infrastructure.

## Extraction Notes

1. **URL redirect**: The source URL in the issue (`github.github.com/gh-aw/patterns/correction-ops`)
   redirects to `github.github.com/gh-aw/experimental/correction-ops/`. The
   redirect confirms the pattern was moved from `patterns/` to `experimental/`,
   consistent with its explicitly experimental status. The `source_url` in this
   note reflects the actual location.

2. **WebFetch returns AI-processed content**: The `github.github.com/gh-aw`
   site renders through an AI model before returning content. Three independent
   WebFetch passes were made. Verbatim quotes were validated by checking
   consistency across all three passes; quotes that appeared in consistent form
   across multiple passes are cited as direct quotes. The key verbatim passages
   (two-surface architecture description, relay workflow prohibition,
   deterministic/agentic split rule, four stable contracts) were consistent
   across passes.

3. **No reference implementation**: Unlike `docs-ghaw-agentic-ops.md` which has
   a `githubnext/agentic-ops` repository with workflow files to examine, the
   CorrectionOps page is a pattern description only — no repository of workflow
   YAML files was referenced. All concrete artifacts are from the pattern page
   itself.

4. **Experimental designation noted**: The pattern carries an explicit experimental
   warning that "the guidance and workflow shape on this page may change as the
   pattern is tested in more real-world workflows." This was captured in Claim 1
   and in the Concrete Artifacts section. Consumers of this note should verify
   current guidance at the source URL before implementing the pattern.

5. **No contradictions filed**: Reviewed all four design rules in
   `docs-ghaw-safe-rollout.md` against CorrectionOps claims — CorrectionOps
   implements all four rules rather than contradicting any of them. The ops
   repository permanence vs. shadow target disposability is not a contradiction
   because they serve different roles. No contradiction issue required.
