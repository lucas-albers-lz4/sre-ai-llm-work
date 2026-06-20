---
source_url: https://github.blog/changelog/2026-06-04-larger-context-windows-and-configurable-reasoning-levels-for-github-copilot
source_type: docs
title: "Larger context windows and configurable reasoning levels for GitHub Copilot"
author: GitHub (official changelog)
date_published: 2026-06-04
date_extracted: 2026-06-07
last_checked: 2026-06-07
status: current
confidence_overall: settled
issue: "#1101"
---

# Larger Context Windows and Configurable Reasoning Levels for GitHub Copilot

> GitHub's June 4, 2026 changelog announcing one-million-token context windows and
> configurable reasoning levels (including extended thinking) in GitHub Copilot for
> VS Code, the Copilot CLI, and the GitHub Copilot app — the first platform-level
> documentation of 1M context capacity in Copilot and the first official practitioner
> guidance on when to trade speed for reasoning depth.

## Source Context

- **Type**: docs (GitHub official product changelog, June 4, 2026; a short changelog
  entry covering two feature areas: context window expansion and reasoning level
  configuration, with a usage recommendation and credit cost notice)
- **Author credibility**: GitHub engineering team announcing a production feature release.
  Authoritative for: the existence of 1M context windows, the availability of
  configurable reasoning levels, the surfaces where these are available (VS Code, Copilot
  CLI, GitHub Copilot app), the credit-cost implication, and the recommended usage
  guidance. Not a credible source for: which specific models support these features
  (models are described only as "supported models"), the exact number of distinct reasoning
  levels exposed in each surface's UI, how "extended thinking" differs technically from
  "higher reasoning" settings, whether the 1M context applies to all token types equally
  (input, output, context), or the specific credit cost per additional context increment.
- **Scope**: Platform-level announcement of two capability expansions in VS Code, Copilot
  CLI, and GitHub Copilot app. Covers: context window size increase to 1M tokens, configurable
  reasoning level controls, official guidance on default vs. extended usage, and credit cost
  warning. Does NOT cover: the specific models that support these features, the exact reasoning
  level options (names, count, increments), plan-tier availability restrictions,
  organizational admin governance requirements, or any benchmarks or quality evidence for the
  extended reasoning capability.

## Extracted Claims

### Claim 1: GitHub Copilot now supports one-million-token context windows in VS Code, the Copilot CLI, and the GitHub Copilot app

- **Evidence**: Official GitHub product changelog stating the 1M context window capability
  as a production release available in three named surfaces.
- **Confidence**: settled (product fact — stated in official changelog as a released feature)
- **Quote**: "work across larger codebases, longer documents, and complex multi-file projects
  without losing context"
- **Our assessment**: This is the first corpus documentation of a 1M token context window
  in GitHub Copilot itself (as distinct from Claude Code's 1M context window documented in
  `blog-anthropic-session-management-1m-context.md` Claim 12). The availability across VS Code,
  CLI, and the app (rather than just one surface) signals a platform-level architectural
  change rather than an IDE-specific feature. The stated user benefit — working across
  "larger codebases, longer documents, and complex multi-file projects without losing context"
  — maps directly to the failure mode of context loss in large code review and refactoring
  tasks. For Ch04 (Context Engineering): a 1M token context window fundamentally changes
  the session management calculus for Copilot users, just as it did for Claude Code users
  (see `blog-anthropic-session-management-1m-context.md` Claim 9 on proactive compaction
  becoming viable at 1M tokens).

### Claim 2: Configurable reasoning levels allow practitioners to adjust the balance between speed and reasoning depth

- **Evidence**: Official GitHub product changelog describing the configurable reasoning
  levels as a shipped feature with a specific user benefit framing.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "dial in the right balance of speed and depth"
- **Our assessment**: This is the first platform-level reasoning configuration documented
  in the GitHub Copilot corpus. The Eclipse IDE note (`docs-github-copilot-eclipse-byok-skills-chat.md`
  Claim 8) documented IDE-specific thinking effort selection in Eclipse as of June 2, 2026;
  this June 4 source documents the same capability type (speed/depth tradeoff via reasoning
  level control) as available across VS Code, CLI, and the Copilot app — a wider surface
  footprint. The "dial in" phrasing implies a continuous or multi-level control, though the
  specific level options (names or count) are not specified in this source. For Ch04
  (Context Engineering): reasoning level selection is a new quality/latency tradeoff dimension
  for Copilot users, distinct from model selection. A practitioner can use the same model
  at different reasoning depths.

### Claim 3: Extended thinking is available for "hardest architectural and debugging challenges" as a named use-case mode within the reasoning level system

- **Evidence**: Official GitHub product changelog naming "extended thinking" as a distinct
  capability enabled by higher reasoning levels.
- **Confidence**: settled (feature and use-case guidance stated in official changelog)
- **Quote**: "unlock extended thinking for your hardest architectural and debugging challenges"
- **Our assessment**: The phrase "unlock extended thinking" positions extended thinking as
  a gated capability accessed via higher reasoning levels — not always-on, but available to
  practitioners who select a higher reasoning tier. The named use cases (architectural challenges,
  debugging challenges) are the same two categories identified by the Eclipse note's thinking
  effort guidance ("Dial the reasoning depth up for complex problems or keep it light for
  quick tasks"). This is consistent with the extended thinking pattern documented in Claude
  Code quality contexts (`blog-anthropic-claudecode-quality-postmortem.md`), where thinking
  blocks provide a reasoning audit trail. For Ch04: document "extended thinking" as the
  high-reasoning-level mode in Copilot, analogous to extended thinking in Claude Code but
  accessed via a reasoning level control rather than a model flag.

### Claim 4: GitHub recommends default context window and reasoning level for everyday tasks, extended features only for complex multi-file problems

- **Evidence**: Official GitHub product changelog providing direct practitioner guidance on
  when to use the extended capabilities.
- **Confidence**: settled (explicit recommendation stated in official changelog)
- **Quote**: "We recommend using the default context window and reasoning level for everyday
  tasks, and reaching for extended context or higher reasoning when you're tackling complex,
  multi-file problems."
- **Our assessment**: This is the first GitHub-authored recommendation in the corpus on when
  to activate vs. not activate extended Copilot capabilities. The guidance follows the same
  logic as the CCA model selection heuristic from `docs-github-copilot-cca-cost-efficient-models.md`
  Claim 3 ("pick the right model for the job: a smaller, quicker model for straightforward
  changes, or a more capable model for complex work"), but applied to context window size and
  reasoning depth rather than model tier. The two-mode recommendation is clear:
  everyday tasks → default settings; complex multi-file work → extended context and/or
  higher reasoning. Practitioners should treat this as the canonical GitHub guidance until
  superseded by more granular recommendations. For Ch01 (Daily Workflows): this guidance
  should inform default Copilot configuration for practitioners who have access to these features.
  For Ch04 (Context Engineering): document as the primary use-case trigger for activating extended
  context in Copilot.

### Claim 5: Both larger context windows and higher reasoning levels consume more AI credits per interaction

- **Evidence**: Official GitHub product changelog explicitly stating the credit cost increase
  as a direct consequence of using these features.
- **Confidence**: settled (credit cost implication stated in official changelog)
- **Quote**: "Choosing a larger context window or higher reasoning level will consume more AI
  credits per interaction."
- **Our assessment**: The credit cost framing is significant for practitioners and teams
  managing Copilot credit consumption. The CCA model selection note (`docs-github-copilot-cca-cost-efficient-models.md`
  Claim 2) established explicit multipliers (0.33x for budget-tier models) — this source
  is less precise, stating only that extended features "consume more AI credits" without
  specifying a multiplier. The two features (larger context, higher reasoning) are listed
  as independent cost levers, meaning practitioners can use extended context without
  extended reasoning, or combine both at higher total cost. For Ch04: document that extended
  context and reasoning are not free upgrades — they should be treated as cost-quality
  tradeoffs comparable to model tier selection, and the same task-complexity heuristic
  (Claim 4) should govern when to incur the cost.

### Claim 6: These features are accessed by selecting supported models in VS Code, Copilot CLI, and GitHub Copilot app

- **Evidence**: Official GitHub product changelog specifying both the access method (model
  selection) and the surfaces where the feature is available.
- **Confidence**: settled (access mechanism and surface list stated in official changelog)
- **Quote**: (no direct quote on access mechanism; see paraphrase in Our assessment)
- **Our assessment**: The access path via "selecting supported models" establishes a dependency:
  not all models in the Copilot model picker support 1M context or configurable reasoning.
  Which specific models qualify as "supported models" is not stated in this source. This creates
  a documentation gap: practitioners must navigate the model picker to discover which models
  unlock these capabilities. The three named surfaces (VS Code, Copilot CLI, GitHub Copilot
  app) are notable for what they exclude: as of this announcement, these features were not
  yet available in JetBrains, Eclipse, Visual Studio, or the GitHub web interface — though
  the source indicates expansion is planned. For Ch02 (Harness Engineering): document VS Code,
  CLI, and app as the current surfaces for extended context/reasoning access; practitioners
  on other surfaces cannot currently access these capabilities.

### Claim 7: Expansion of these features to additional surfaces is planned

- **Evidence**: Official GitHub product changelog indicating planned expansion beyond the
  three surfaces named at launch.
- **Confidence**: settled (expansion stated as planned in official changelog, though no
  timeline is given)
- **Quote**: (no direct quote confirming the exact expansion language; per extraction notes,
  "expanding to more surfaces soon" appears in the source but verbatim wording was not
  confirmed character-for-character across both WebFetch passes)
- **Our assessment**: The planned expansion is directionally significant: the fact that VS Code,
  CLI, and app are explicitly named alongside a statement of planned expansion implies that
  other surfaces (Eclipse, JetBrains, web) are in the pipeline. For Ch02: note that the
  surface list for these capabilities is a snapshot as of June 4, 2026; practitioners on
  other surfaces should check the changelog for updates. The Eclipse IDE note's thinking effort
  selector (June 2, 2026) may be an early surface-specific instance of the same platform
  capability now being formalized.

## Concrete Artifacts

### Source Content — Key Feature Summary (from two WebFetch calls, June 7, 2026)

Two independent WebFetch calls to the source URL returned consistent content. The
following captures the substantive content as retrieved. All direct quotes in the
Extracted Claims above are drawn from this content.

```
Title: Larger context windows and configurable reasoning levels for GitHub Copilot
Published: 2026-06-04 (Release)
Source: https://github.blog/changelog/2026-06-04-larger-context-windows-and-configurable-reasoning-levels-for-github-copilot

FEATURE 1: One-Million-Token Context Windows
  Benefit: "work across larger codebases, longer documents, and complex multi-file
           projects without losing context"
  Surfaces: VS Code, Copilot CLI, GitHub Copilot app

FEATURE 2: Configurable Reasoning Levels
  Benefit: "dial in the right balance of speed and depth"
  Use case: "unlock extended thinking for your hardest architectural and debugging
            challenges"
  Surfaces: VS Code, Copilot CLI, GitHub Copilot app

CREDIT COST:
  "Choosing a larger context window or higher reasoning level will consume more AI
   credits per interaction."

USAGE RECOMMENDATION:
  "We recommend using the default context window and reasoning level for everyday
   tasks, and reaching for extended context or higher reasoning when you're tackling
   complex, multi-file problems."

ACCESS:
  By selecting supported models in the named surfaces.
  Expansion to more surfaces planned.
```

Source: https://github.blog/changelog/2026-06-04-larger-context-windows-and-configurable-reasoning-levels-for-github-copilot
Retrieved: 2026-06-07 via two independent WebFetch calls; content consistent across both passes.

### Capability Decision Matrix (synthesized from source guidance)

```
GitHub Copilot — Context Window and Reasoning Level Selection (as of June 4, 2026)

RECOMMENDED DEFAULTS:
  Task type:          Everyday tasks (single-file, routine, well-bounded)
  Context window:     Default
  Reasoning level:    Default
  Credit cost:        Standard

EXTENDED MODE (opt-in):
  Task type:          Complex, multi-file problems; architectural challenges; debugging
  Context window:     Extended (1M tokens)
  Reasoning level:    Higher / Extended thinking
  Credit cost:        More AI credits per interaction

ACCESS METHOD:
  Select a "supported model" in:
    - VS Code
    - Copilot CLI
    - GitHub Copilot app
  (Expansion to additional surfaces planned)

OFFICIAL GUIDANCE SOURCE:
  "We recommend using the default context window and reasoning level for everyday
  tasks, and reaching for extended context or higher reasoning when you're tackling
  complex, multi-file problems."
  — GitHub Copilot changelog, June 4, 2026
```

## Cross-References

- **Extends** `docs-github-copilot-eclipse-byok-skills-chat.md` (Claims 7 and 8, issue #1034):
  The Eclipse note (June 2, 2026) documented IDE-specific thinking blocks and selectable
  thinking effort level in Eclipse Copilot: "You can now choose the thinking effort level
  for supported models. Dial the reasoning depth up for complex problems or keep it light
  for quick tasks." This June 4 source documents configurable reasoning levels at platform
  level for VS Code, CLI, and app — a broader surface footprint. The Eclipse note's thinking
  effort selector is likely the same underlying capability that this source formalizes as
  "configurable reasoning levels." Together, the two June 2026 notes establish reasoning level
  configuration as a cross-surface Copilot capability: Eclipse (IDE-specific, June 2) +
  VS Code/CLI/app (platform-level, June 4). The Eclipse note's Extraction Note 4 flagged
  that "thinking effort levels not enumerated" — this June 4 source also does not enumerate
  the levels, confirming that the level options remain undocumented across both announcements.

- **Corroborates** `blog-anthropic-session-management-1m-context.md` (Claim 12, issue #316):
  That source confirmed Claude Code's 1M context window ("Claude Code has a context window
  of one million tokens") and documented how the 1M window changes session management strategy —
  more runway before compaction fires, proactive /compact viable. This June 4 Copilot source
  extends the 1M context paradigm to GitHub Copilot in VS Code, CLI, and app. The benefit
  framing is similar: in Claude Code, 1M enables proactive session management; in Copilot,
  1M enables "work across larger codebases, longer documents, and complex multi-file projects
  without losing context." Both sources confirm that 1M tokens is the current high-end
  context ceiling in the Anthropic/GitHub AI tooling ecosystem as of mid-2026.

- **Extends** `docs-github-copilot-cca-cost-efficient-models.md` (Claim 3, issue #818):
  That source documented GitHub's first explicit task-complexity-aware model selection
  guidance for CCA: "pick the right model for the job: a smaller, quicker model for
  straightforward changes, or a more capable model for complex work." This source adds
  two new complexity-aware selection dimensions beyond model tier: context window size and
  reasoning level. The same task-complexity logic now applies to three independent controls
  (model tier, context window, reasoning level), each with its own credit cost implication.
  For Ch04: document the three-dimensional model-context-reasoning selection framework
  as the full GitHub Copilot quality/cost configuration surface.

- **Extends** `docs-github-copilot-agent-model-selection.md` (Claim 7, issue #171):
  That source noted "the changelog implies model tier choice matters for task quality, but
  provides no guidance." This June 4 source fills that guidance gap not just for model
  selection but for the broader capability configuration space — it provides explicit
  official guidance on when to use extended context and reasoning. Combined, these two sources
  show the evolution of GitHub's practitioner guidance: April 2026 (no guidance on when to
  use higher-capability options) → June 2026 (explicit "default for everyday, extended for
  complex multi-file" recommendation).

- **Extends** `docs-github-copilot-web-model-consolidation.md` (Claim 6, issue #845):
  That source (May 20, 2026) documented GitHub's forward strategy for the web surface as
  "a more limited set of new model rollouts." This June 4 source's availability in VS Code,
  CLI, and app — but not the web surface — is consistent with that strategy: the web surface
  is being managed for reliability/consistency, while VS Code and CLI are receiving advanced
  capability expansions. The two sources together clarify the emerging surface differentiation:
  web = curated, consistency-optimized; VS Code/CLI/app = capability-advancing,
  frontier-feature-forward.

- **Novel**:
  - **1M token context window in GitHub Copilot (platform-level)**: No prior corpus source
    documents a 1M context window capacity in GitHub Copilot itself. The Eclipse note documented
    a context window "donut indicator" UI but did not state a maximum size. This is the first
    corpus documentation that Copilot's context capacity has reached 1M tokens across VS Code,
    CLI, and app surfaces.
  - **"Extended thinking" as a named Copilot product capability**: The Eclipse note referenced
    thinking blocks and thinking effort levels; this source uses the explicit phrase "extended
    thinking" as a named product mode unlocked by higher reasoning levels. The relationship between
    Eclipse's "thinking effort" UI and Copilot's "extended thinking" label is not clarified in
    either source, but both likely refer to the same underlying reasoning model capability.
  - **Official GitHub guidance: default for everyday, extended for complex multi-file**: No prior
    corpus source provides GitHub's own recommendation for when to use extended context or reasoning
    capabilities. This is the first authoritative usage guidance for these features.
  - **Credit cost for context window and reasoning level as independent cost levers**: No prior
    corpus source documents context window size as a credit-consuming variable distinct from model
    tier in Copilot. Prior credit cost documentation focused on model tier (0.33x vs. 1x vs. >1x
    per `docs-github-copilot-cca-cost-efficient-models.md`). This source adds context window and
    reasoning level as additional credit levers.

## Guide Impact

### Chapter 04: Context Engineering

- **1M context window changes Copilot session management strategy**: Parallel to the Claude
  Code guidance in `blog-anthropic-session-management-1m-context.md`, the 1M context window
  for Copilot changes when context limits become a constraint. Practitioners who previously
  pruned context aggressively to stay within smaller context limits now have substantially more
  runway for large-codebase tasks. Document the "default for everyday, extended for complex
  multi-file" recommendation (Claim 4) as the primary guidance for context window selection.
- **Reasoning level as a new quality/latency/cost dimension**: Add configurable reasoning levels
  to the context engineering framework as a practitioner-controlled quality knob, alongside model
  selection and context window size. For complex tasks requiring deep architectural reasoning or
  difficult debugging: enable higher reasoning / extended thinking. For routine tasks: use default
  reasoning to save credits and time. Document this as a three-dimensional selection space:
  model tier × context window × reasoning level.
- **Three-dimensional configuration framework**: The guide's model selection guidance should be
  updated to reflect that GitHub Copilot's capability and cost are now governed by three
  independently selectable parameters: (1) model tier (from
  `docs-github-copilot-cca-cost-efficient-models.md`), (2) context window size (this source),
  (3) reasoning level (this source). Each parameter affects both output quality and credit cost.

### Chapter 01: Daily Workflows

- **When to invoke extended context**: Add a decision point to the Copilot daily workflow:
  for tasks spanning multiple files, large codebases, or long documents, switch to an extended
  context window ("supported model" in VS Code, CLI, or app). For single-file, bounded, or
  routine tasks, stay with default. The official guidance (Claim 4) provides the baseline
  heuristic.
- **When to invoke extended reasoning**: For architectural decisions, complex multi-step
  debugging, or any task where the correctness of the reasoning path matters more than speed,
  enable higher reasoning / extended thinking. Document that thinking blocks (visible in Eclipse
  per `docs-github-copilot-eclipse-byok-skills-chat.md` Claim 7) can accompany extended thinking
  and provide a reasoning audit trail.

### Chapter 02: Harness Engineering

- **Surface availability matrix**: Document that as of June 4, 2026, 1M context and configurable
  reasoning are available in VS Code, Copilot CLI, and GitHub Copilot app, but not yet in web,
  Eclipse, JetBrains, or Visual Studio. Teams whose practitioners use multiple Copilot surfaces
  should account for this capability gap. Update when new surfaces are announced.
- **Model selection requirement**: Document that accessing these features requires selecting a
  "supported model" in the model picker — not all Copilot models enable extended context or
  reasoning. Teams configuring recommended model presets for their practitioners should identify
  which models support these features (to be determined from direct product observation; not
  specified in this source).
- **Credit cost governance**: Teams with credit budgets should document when practitioners
  are expected to use extended context/reasoning (complex work) vs. default (everyday tasks),
  following the official guidance. Extended features cost more credits; ungoverned use may
  exhaust credit allocations faster than expected.

### Chapter 03: Evaluation and Quality

- **Extended thinking as a verification tool**: The Eclipse note documented thinking blocks as
  an in-context verification mechanism — practitioners can inspect whether the model's reasoning
  path was sound before accepting output. This June 4 source confirms "extended thinking" is
  available more broadly. Add to the quality playbook: for high-stakes tasks (architecture
  decisions, security-adjacent changes), enable extended reasoning and inspect the reasoning
  trace (where thinking blocks are visible in supported surfaces) to verify correctness before
  accepting output.

## Extraction Notes

1. **Source is a short changelog entry**: Two independent WebFetch calls returned consistent
   content. The announcement is brief (~200 words estimated) covering two feature areas. All
   seven claims exhaust the substantive content. No sub-pages were followed, as the changelog
   does not appear to link to detailed documentation for these specific features.

2. **Verbatim quotes verified across both fetches**: Five direct quotes are used in this note.
   Four (Claims 1, 2, 3, 4 intro, and 5) were returned within quotation marks in both WebFetch
   passes with consistent wording. Claim 4's full recommendation quote was surfaced explicitly
   by both passes. Claim 7 (expansion announcement) was described by both passes but the exact
   verbatim phrase could not be confirmed character-for-character; that claim uses "(no direct
   quote)" accordingly.

3. **Reasoning levels not enumerated**: Neither WebFetch pass surfaced specific level names
   (e.g., "low / medium / high" or equivalent). The announcement describes the capability
   conceptually ("dial in the right balance") without naming the specific options. This is
   consistent with the Eclipse note's Extraction Note 4 ("thinking effort levels not enumerated").

4. **Supported models not named**: The announcement gates access behind "supported models" without
   naming them. Which models in the VS Code/CLI/app pickers qualify is not determinable from this
   source. Practitioners must discover this via the model picker UI.

5. **Two sources same date**: This announcement (June 4, 2026) shares a publication date with
   `docs-github-copilot-chat-pr-richer-context.md` (issue #1078). Both are changelog entries
   from the same day. The content is distinct — this source covers context/reasoning capabilities;
   that source covers PR chat workflows. No overlap.

6. **No contradictions to file**: The 1M context claim extends Claude Code's documented 1M window
   (consistent, not contradictory). The reasoning level guidance is consistent with the Eclipse
   thinking effort guidance (extends to broader surfaces). No existing corpus source makes a
   claim that this source would refute. No contradiction issue required.
