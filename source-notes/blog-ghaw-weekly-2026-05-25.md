---
source_url: https://github.github.com/gh-aw/blog/2026-05-25-weekly-update/
source_type: blog-post
title: "Weekly Update – May 25, 2026 (GitHub Agentic Workflows)"
author: GitHub Agentic Workflows team (gh-aw)
date_published: 2026-05-25
date_extracted: 2026-05-26
last_checked: 2026-05-26
status: current
confidence_overall: emerging
issue: "#912"
---

# Weekly Update – May 25, 2026 (GitHub Agentic Workflows)

> v0.75.4 ships four production-significant changes: explicit `engine.permission-mode`
> configuration replacing implicit bash-wildcard detection for Claude's permission mode;
> `OTEL_RESOURCE_ATTRIBUTES` inheritance giving child processes automatic trace context;
> Codex engine hardening with secret diagnostics, missing-key fast-fail, and `--json`
> streaming mode; and the `linter-miner` Agent of the Week — 39 turns, 10.8 minutes,
> over one million tokens, two failed attempts — as new evidence on the cost and
> resilience profile of code-analysis agents.

## Source Context

- **Type**: blog-post (weekly changelog/release update from the official GitHub Agentic
  Workflows blog; covers v0.75.4 released May 24, 2026 following six pre-releases from
  the stable v0.74.8 base; includes an "Agent of the Week" spotlight on `linter-miner`)
- **Author credibility**: The gh-aw blog is the official publication of GitHub's Agentic
  Workflows platform team (Don Syme, Peli de Halleux, Mara Kiefer — see
  `blog-gh-aw-operations-release-workflows.md` for author background). Releases report
  on shipped PRs with specific version numbers and metrics derived from instrumentation
  data in live repos. High credibility for first-party platform claims.
- **Scope**: One release (v0.75.4) with six pre-releases from v0.74.8. Covers Codex
  engine improvements (secret diagnostics, fast-fail, streaming), OTel resource
  attribute inheritance, Go 1.26 infrastructure migration, Gemini stream-json parsing
  fix, explicit Claude permission mode configuration, two bug fixes (GHE shorthand
  fallback, PR Sous Chef startup context), FAQ documentation compression, and an Agent
  of the Week spotlight on `linter-miner`. Does NOT cover: the full list of Codex secret
  diagnostic messages; the exact mechanism by which OTEL_RESOURCE_ATTRIBUTES propagates
  into child processes; whether Go 1.26 introduces breaking changes for workflow authors;
  or the precise heuristic previously used for bash-wildcard-based permission-mode
  derivation.

## Extracted Claims

### Claim 1: The Codex engine now includes secret diagnostics, missing-key fast-fail, and `--json` streaming mode, with `OPENAI_API_KEY` absence now producing a clear error instead of a silent failure

- **Evidence**: v0.75.4 release. The three Codex improvements are named together.
  The `OPENAI_API_KEY` case is called out specifically as a concrete symptom now
  surfaced by the fast-fail behavior. dev.md switched to Codex as part of this
  change, indicating first-party dogfooding.
- **Confidence**: emerging (features named and shipped; the full set of secret
  diagnostics covered, the output format of `--json` streaming mode, and the
  behavior on partial or malformed secrets are not described in the changelog)
- **Quote**: "The Codex engine now includes secret diagnostics, missing-key fast-fail,
  and `--json` streaming mode."
- **Our assessment**: Three distinct improvements bundled in one release. Secret
  diagnostics surfaces configuration errors that previously caused silent failures —
  the `OPENAI_API_KEY` case is the canonical example. Missing-key fast-fail stops
  execution immediately on a missing required key rather than proceeding and failing
  later with a less interpretable error. `--json` streaming mode enables structured
  output consumption from Codex during a run (vs. waiting for the full completion).
  Together these make Codex-engine workflows observably fail rather than silently
  fail. For Ch02 (Harness Engineering): Codex engine configuration should include
  validation that required secrets are present before workflow execution; the
  fast-fail behavior makes this explicit. For Ch04 (Operations): `--json` streaming
  mode enables real-time structured output capture from Codex agents, analogous to
  the `--json` streaming modes in other CLI tools.

### Claim 2: `OTEL_RESOURCE_ATTRIBUTES` are now injected into gh-aw workflows so child processes using the OpenTelemetry SDK automatically inherit trace context

- **Evidence**: v0.75.4 release. Described as enabling "improved distributed tracing"
  by propagating resource attributes to child processes automatically.
- **Confidence**: emerging (feature shipped; whether all child process invocation
  patterns are covered, and whether the inheritance applies to MCP tool subprocesses
  as well as direct process invocations, is not specified)
- **Quote**: "OTEL_RESOURCE_ATTRIBUTES are now injected into gh-aw workflows, so child
  processes using the OpenTelemetry SDK automatically inherit trace context"
- **Our assessment**: This fills a propagation gap in the gh-aw distributed tracing
  story. Prior OTel additions added spans for workflow jobs and cross-job trace
  hierarchy (April 6 + April 13 releases) and then finish reasons and synthetic
  exception events (May 11). Those additions all operated at the gh-aw-runtime level.
  This change operates at the environment variable level: `OTEL_RESOURCE_ATTRIBUTES`
  is a standard OTel environment variable that child processes can read without any
  gh-aw-specific instrumentation. A subprocess using the standard OTel SDK will
  automatically emit traces tagged with the parent workflow's resource attributes —
  enabling trace correlation without modifying the child process. For Ch04
  (Operations): any subprocess or MCP tool that uses the standard OTel SDK now
  participates in the distributed trace automatically; no gh-aw-specific API calls
  are required for basic trace correlation.

### Claim 3: The Codex default model is set to `gpt-5.3-codex` to prevent empty-string fallback crashes when `engine.model` is unset

- **Evidence**: v0.75.4 release. Named as a defensive default to prevent a specific
  failure mode: empty-string fallback crashes when `engine.model` is unset.
- **Confidence**: settled (specific version, specific model name, specific failure
  mode prevented)
- **Quote**: (no direct quote; post describes the Codex default model as set to
  `gpt-5.3-codex` to prevent empty-string fallback crashes when `engine.model` is
  unset)
- **Our assessment**: A missing `engine.model` previously caused a crash via
  empty-string fallback rather than a clear error. Setting a named default
  (`gpt-5.3-codex`) makes the behavior predictable: unset `engine.model` now
  produces a defined outcome rather than a crash. This pairs with the missing-key
  fast-fail in Claim 1: fast-fail catches missing secrets; the default model catches
  missing model configuration. Together they harden the Codex engine startup path.
  For Ch02 (Harness Engineering): Codex workflows should declare `engine.model`
  explicitly to make model selection auditable, even though the default now prevents
  crashes; an explicit declaration avoids behavior changes when the default model
  changes in a future release.

### Claim 4: Go 1.26 infrastructure migration completed in v0.75.4

- **Evidence**: v0.75.4 release. Listed as a completed infrastructure update.
- **Confidence**: settled (stated as completed in the release)
- **Quote**: (no direct quote; post lists Go 1.26 migration as a completed
  infrastructure update in v0.75.4)
- **Our assessment**: Platform-level infrastructure upgrade. No direct
  practitioner impact from this change alone, but Go version updates in the gh-aw
  runtime can affect subprocess environment compatibility. Low actionable content
  for guide recommendations but worth noting as context for any unexplained
  behavior changes after v0.75.4 upgrade.

### Claim 5: Gemini stream-json fragmented chunk responses were causing detection verdicts to appear missing; the parsing fix resolves this

- **Evidence**: v0.75.4 release. Described as Gemini's stream-json producing
  fragmented chunk responses that caused detection verdicts to appear missing until
  the fix.
- **Confidence**: settled (specific symptom described and fix shipped)
- **Quote**: (no direct quote; post describes fragmented chunk responses from
  Gemini's stream-json causing detection verdicts to appear missing, now resolved)
- **Our assessment**: Fragmented streaming responses from Gemini's stream-json
  interface were being parsed as incomplete — detection verdicts that arrived in
  multiple chunks appeared missing when the parser expected a single chunk. This
  is a client-side parsing bug, not a Gemini API issue per se: the stream-json
  protocol allows chunked delivery, and the gh-aw Gemini client was not reassembling
  chunks correctly before parsing. For Ch03 (Safety and Verification): threat
  detection workflows using Gemini should be validated after upgrading to v0.75.4
  to confirm verdicts are now correctly parsed. Pre-v0.75.4 Gemini-based detection
  may have silently missed threats due to this parsing gap.

### Claim 6: Claude's `engine.permission-mode` is now explicitly configurable in workflow frontmatter, replacing the prior implicit derivation from bash wildcard detection

- **Evidence**: v0.75.4 release, described under "Security & Control." The prior
  behavior (implicit derivation from bash wildcard detection) is named explicitly,
  establishing a clear before/after.
- **Confidence**: emerging (feature shipped; the full set of valid values for
  `engine.permission-mode` beyond the two named values, and the migration path for
  existing workflows, are not described in the changelog)
- **Quote**: "Claude's permission mode (`acceptEdits` vs `bypassPermissions`) was
  previously derived implicitly from bash wildcard detection"
- **Our assessment**: This is the third step in a three-step progressive hardening
  of Claude's permission model in gh-aw. Step 1 (April 27, `blog-ghaw-weekly-2026-
  04-27.md` Claim 2): `bypassPermissions` deprecated, replaced by `acceptEdits`,
  with missing MCP server entries added to `--allowed-tools`. Step 2 (May 11,
  `blog-ghaw-weekly-2026-05-11.md` Claim 2 context): inline sub-agents going
  default-on in the same time window. Step 3 (May 25): the permission mode itself
  is made explicit — workflows can now state `engine.permission-mode: acceptEdits`
  or `engine.permission-mode: bypassPermissions` rather than relying on implicit
  inference from bash wildcard patterns.

  The implicit derivation from "bash wildcard detection" is significant: it means
  that prior to v0.75.4, a workflow's Claude permission mode was inferred from
  whether its `run:` blocks contained glob patterns (`*`, `**`) — a heuristic that
  could misclassify workflows with legitimately complex bash patterns as needing
  elevated permissions. Explicit `engine.permission-mode` removes this heuristic and
  makes the security boundary auditable at the configuration layer. For Ch02 (Harness
  Engineering): all workflows invoking Claude should add an explicit
  `engine.permission-mode:` field after upgrading to v0.75.4 to remove reliance on
  the implicit heuristic. For Ch03 (Safety and Verification): auditing Claude
  permission boundaries in gh-aw workflows now requires reading the
  `engine.permission-mode` field (explicit) rather than inferring from bash patterns
  (implicit). This is a security-posture improvement: explicit is auditable,
  implicit is not.

### Claim 7: GHE shorthand resolver now falls back to github.com for org-less specifications, fixing a resolution failure for GitHub Enterprise environments

- **Evidence**: v0.75.4 release bug fix. Described as a fallback addition for the
  GHE shorthand resolver.
- **Confidence**: settled (specific fix, specific scenario described)
- **Quote**: (no direct quote; post describes GHE shorthand resolver now falling back
  to github.com for org-less specifications)
- **Our assessment**: For GitHub Enterprise deployments where workflows reference
  shared configurations or resources without an org prefix, the prior shorthand
  resolver would fail rather than fall back to github.com. This fix enables
  cross-environment workflow portability for teams that maintain both GHE and
  github.com resources. Low impact for cloud-only deployments; meaningful for
  enterprises with hybrid GHE/cloud configurations.

### Claim 8: PR Sous Chef startup failures now display proper context including stdout/stderr instead of undefined references

- **Evidence**: v0.75.4 release bug fix. Described as fixing startup failure
  diagnostics to show proper context rather than `undefined stdout/stderr`.
- **Confidence**: settled (specific symptom named: `undefined stdout/stderr` in
  startup failure messages)
- **Quote**: (no direct quote; post describes PR Sous Chef startup failures now
  displaying proper context instead of undefined stdout/stderr)
- **Our assessment**: `undefined stdout/stderr` in error messages is a common
  JavaScript/TypeScript bug where error capture assumes a non-null stream handle
  that may be uninitialized at startup. The fix ensures that startup failures
  (where the process has not yet established its output streams) are diagnosed
  with available context rather than propagating undefined references. For
  practitioners debugging PR Sous Chef startup failures: pre-v0.75.4, startup
  errors yielded `undefined` in the diagnostic output; v0.75.4 and later yield
  actual stdout/stderr content, enabling root-cause identification.

### Claim 9: The `linter-miner` workflow — a code-analysis agent that creates new linters — required 39 turns, 10.8 minutes, and over one million tokens, with two failed attempts before success

- **Evidence**: "Agent of the Week" spotlight for May 25, 2026. The workflow
  analyzed the gh-aw codebase, identified `fmt.Fprintln(w, fmt.Sprintf(...))` as a
  redundant pattern, and created a new `fprintlnsprintf` linter. Metrics are explicit
  in the spotlight section.
- **Confidence**: anecdotal (single-run data from the Agent of the Week spotlight;
  sample size and conditions not specified)
- **Quote**: "It took 39 turns and 10.8 minutes, burning through over a million
  tokens."
- **Our assessment**: The `linter-miner` spotlight provides a qualitatively
  different data point from the `auto-triage-issues` longitudinal series. Where
  `auto-triage-issues` is a high-frequency, bounded-scope triage task that has been
  optimized to under-40-second runs (May 11: 9 API requests, ~270K cached tokens),
  `linter-miner` is a research-and-create task: it must search a codebase, identify
  a pattern, understand existing linter infrastructure, and author a new linter that
  passes review. That task profile justifies a much higher token budget and longer
  turn count.

  The two failed attempts before success on the third run establish an important
  benchmark: code-analysis agents that create new artifacts (linters, tests, scripts)
  should be expected to fail on first attempt. The agent's resilience — trying
  again and succeeding — is operationally significant. This argues for designing
  retry loops into code-creation workflows rather than treating first-attempt failure
  as a workflow termination condition. For Ch02 (Harness Engineering): code-creation
  agents require retry budgets; a single-attempt design underestimates the
  distribution of attempts needed. For Ch04 (Operations): over-one-million-token
  runs on code-analysis tasks are within the production range for gh-aw; budget
  planning for such workflows should use the `gh aw forecast` command (Claim 4 from
  `blog-ghaw-weekly-2026-05-11.md`) before committing to wide deployment.

### Claim 10: The FAQ was condensed by approximately 21% with tighter, more scannable responses

- **Evidence**: v0.75.4 documentation change. The compression percentage is stated
  explicitly.
- **Confidence**: anecdotal (percentage is stated; the methodology — character count,
  word count, or section count — is not specified)
- **Quote**: (no direct quote; post describes FAQ condensed by approximately 21%
  with tighter, more scannable responses)
- **Our assessment**: Documentation quality improvements in the official FAQ affect
  the discoverability of platform guidance. A 21% reduction while maintaining
  coverage suggests a meaningful rewrite, not minor trimming. For the guide: if any
  chapters cite gh-aw FAQ content verbatim, the relevant passages may have changed
  in v0.75.4 and should be re-verified against the current FAQ.

## Concrete Artifacts

### Version Summary: v0.75.4 (released May 24, 2026, from stable v0.74.8)

```
v0.75.4 — May 24, 2026

What's New:
  - Codex engine: secret diagnostics, missing-key fast-fail, --json streaming mode
    (clear error when OPENAI_API_KEY absent; dev.md switched to Codex)
  - OTel: OTEL_RESOURCE_ATTRIBUTES injected into workflows; child processes
    using OpenTelemetry SDK automatically inherit trace context
  - Infrastructure: Go 1.26 migration completed
  - Codex default model: gpt-5.3-codex (prevents empty-string fallback crashes
    when engine.model is unset)

Security & Control:
  - New: engine.permission-mode explicitly configurable in workflow frontmatter
    (acceptEdits | bypassPermissions)
    Previously: derived implicitly from bash wildcard detection
    Now: explicit field in workflow frontmatter

Bug Fixes:
  - Gemini stream-json: fragmented chunk responses no longer cause missing
    detection verdicts
  - GHE shorthand resolver: falls back to github.com for org-less specifications
  - PR Sous Chef: startup failures now display proper stdout/stderr context
    (previously showed "undefined")

Documentation:
  - FAQ condensed by approximately 21% — tighter, more scannable responses
```

### Explicit `engine.permission-mode` Configuration (v0.75.4)

```yaml
# Before v0.75.4: permission mode inferred from bash wildcard detection
# (heuristic — not auditable from configuration alone)

# After v0.75.4: explicit in workflow frontmatter
engine:
  permission-mode: acceptEdits    # or bypassPermissions
  # ...other engine configuration...
```

### Agent of the Week: `linter-miner` — May 25, 2026 Data

```
Agent:           linter-miner
Task type:       Code-analysis + linter creation (research-and-create)
Codebase:        gh-aw repository
Task:            Identify redundant patterns → author new linter

Pattern found:   fmt.Fprintln(w, fmt.Sprintf(...))  — redundant (use fmt.Fprintf directly)
Linter created:  fprintlnsprintf

Metrics:
  Turns:         39
  Wall time:     10.8 minutes
  Tokens:        over one million
  Attempts:      3 (2 failed, 1 successful)

Contrast with auto-triage-issues (May 11, 2026):
  Turns:         9 API requests (approx. 9 turns)
  Wall time:     < 40 seconds
  Tokens:        ~270K (from cache)
  Attempts:      1 (successful)

Implication: Research-and-create tasks require ~4x turns, ~10x tokens, and retry
budgets vs. bounded triage tasks. Agent budget planning must distinguish task types.
```

### Codex Engine Hardening: Startup Path (v0.75.4)

```
Failure mode before v0.75.4:
  Missing OPENAI_API_KEY → silent crash or unintelligible error
  Missing engine.model  → empty-string fallback crash

Behavior after v0.75.4:
  Missing OPENAI_API_KEY → clear diagnostic error (secret diagnostics)
  Missing engine.model  → gpt-5.3-codex default (no crash)
  Codex output format   → --json streaming mode available

Design principle: Codex engine startup failures now surface at configuration
validation time, not mid-run. Analogous to the Gemini verdict parsing fix:
both are "fail-visible" hardening over "fail-silent" prior behavior.
```

## Cross-References

- **Corroborates**:
  - `blog-ghaw-weekly-2026-04-27.md` Claim 2 (`bypassPermissions` → `acceptEdits`
    migration): The May 25 explicit `engine.permission-mode` field (Claim 6 here)
    is the natural extension of the April 27 flag rename. April 27 established the
    correct flag names; May 25 makes the selection explicit rather than inferred.
    Both changes are steps in the same security-hardening trajectory for Claude
    permission surfaces in gh-aw.
  - `blog-ghaw-weekly-2026-05-11.md` Claims 10–11 (OTel `gen_ai.response.finish_reasons`
    + synthetic exception events for silent failures): The May 25 `OTEL_RESOURCE_ATTRIBUTES`
    inheritance (Claim 2 here) continues the progressive OTel completion story. Each
    release adds a distinct OTel dimension: May 11 added model response metadata and
    silent-failure events; May 25 adds resource-attribute inheritance for child
    processes. The distributed tracing story is additive across releases.
  - `blog-ghaw-weekly-2026-04-06.md` Claim 1 (OTLP distributed tracing via
    `observability.otlp` frontmatter): The `OTEL_RESOURCE_ATTRIBUTES` injection
    (Claim 2 here) builds on the same OTLP framework established in April 6. April 6
    delivered the framework for gh-aw job spans; May 25 extends it to environment-level
    propagation for child processes. Child processes previously had no gh-aw trace
    context unless they explicitly implemented gh-aw-specific instrumentation.
  - `blog-ghaw-fault-investigation.md` (if applicable — fault investigation workflows):
    The Gemini stream-json fragmented-chunk fix (Claim 5 here) is consistent with the
    broader pattern of detection/verification workflows requiring careful streaming
    output handling; fragmented responses are a known failure mode for long-running
    stream-json consumers.

- **Extends**:
  - `blog-ghaw-weekly-2026-05-11.md` Claim 4 (`gh aw forecast` for pre-run token
    projection): The `linter-miner` data (Claim 9 here — >1M tokens, 39 turns,
    10.8 minutes, 2 failed attempts) is precisely the type of expensive workflow
    that `gh aw forecast` is designed for. The May 11 forecast command enables
    budget-before-you-run; the May 25 linter-miner data gives the first concrete
    example of why such forecasting matters for code-creation agents.
  - `blog-ghaw-weekly-2026-04-27.md` Claim 2 (`bypassPermissions` → `acceptEdits`
    migration): Claim 6 here (explicit `engine.permission-mode`) extends the April
    27 finding. The three-step progression: (1) April 27: deprecated `bypassPermissions`,
    introduced `acceptEdits`; (2) May 25: made permission mode configuration explicit
    rather than heuristic. Together they document the complete permission-model
    hardening arc for Claude in gh-aw.
  - `blog-ghaw-weekly-2026-05-11.md` Claim 12 (`auto-triage-issues` as a
    high-frequency, cache-optimized triage agent): The `linter-miner` data (Claim 9
    here) extends the Agent of the Week corpus with a qualitatively different task
    type. `auto-triage-issues` represents bounded-scope, high-frequency, cache-warm
    efficiency. `linter-miner` represents open-ended research-and-create, expensive,
    single-run-unreliable. The corpus now has both profiles with concrete metrics.

- **Contradicts**: None filed. No existing source note claims that `OTEL_RESOURCE_ATTRIBUTES`
  inheritance is handled by gh-aw for child processes (prior OTel notes are all
  at the job-span or attribute level, not environment-level propagation). No
  contradiction between the explicit `engine.permission-mode` field and prior
  permission-related notes — this is additive. No existing note claims code-analysis
  agents should succeed on first attempt; the two-failed-attempt data from
  `linter-miner` is novel, not contradictory. No contradiction issue warranted.

- **Novel**:
  - **Explicit `engine.permission-mode` frontmatter field** (Claim 6): First corpus
    source to document the transition from implicit (bash-wildcard-heuristic) to
    explicit (frontmatter field) Claude permission mode selection in gh-aw workflows.
    Prior notes documented the flag names (`acceptEdits` vs `bypassPermissions`) but
    not the configuration surface for selecting between them.
  - **`OTEL_RESOURCE_ATTRIBUTES` environment-level propagation** (Claim 2): First
    corpus source to document OTel inheritance at the environment variable level for
    child processes. All prior OTel additions operated at the gh-aw runtime span level;
    this is the first environment-level propagation mechanism.
  - **Codex engine secret diagnostics and fast-fail** (Claim 1): First corpus source
    to document Codex engine startup hardening for missing secrets and missing model
    configuration.
  - **`linter-miner` as a code-creation agent type with retry profile** (Claim 9):
    First Agent of the Week spotlight on a research-and-create agent (vs. triage
    or analysis agents in prior weeks). The two-failed-attempt data is the first
    corpus evidence that code-creation agents should budget for retry attempts as a
    baseline expectation, not an exception.
  - **`gpt-5.3-codex` as the Codex default model in gh-aw** (Claim 3): First corpus
    source to name the Codex default model for gh-aw and document why it was set
    (empty-string fallback prevention).

## Guide Impact

- **Chapter 02 (Harness Engineering)**:
  - Add explicit `engine.permission-mode:` as a required field in Claude-invoking
    gh-aw workflows after v0.75.4 (Claim 6). Implicit derivation from bash wildcard
    patterns is no longer the mechanism; explicit configuration is auditable and
    safer. Pair with the April 27 `acceptEdits` migration note.
  - Add Codex engine configuration pattern: declare `engine.model` explicitly to
    avoid reliance on the `gpt-5.3-codex` default (Claim 3); validate that
    `OPENAI_API_KEY` is present using the new secret diagnostics / fast-fail rather
    than relying on mid-run failures (Claim 1).
  - Add retry budget as a design requirement for code-creation agents (Claim 9):
    `linter-miner`'s two-failed-attempt data suggests first-attempt success is not
    the baseline for research-and-create agents. Workflow configuration should
    include explicit retry counts for such agent types.

- **Chapter 03 (Safety and Verification)**:
  - Update Claude permission-mode guidance: `engine.permission-mode:` is now the
    canonical configuration surface for selecting `acceptEdits` vs. `bypassPermissions`
    (Claim 6). Chapter content that describes permission selection should reference
    this frontmatter field rather than describing implicit behavior. Explicit
    configuration makes the security boundary auditable at review time.
  - Add Gemini stream-json detection verification step (Claim 5): workflows using
    Gemini for threat detection that were running pre-v0.75.4 should be validated
    after upgrade; detection verdicts may have been silently missing due to the
    fragmented-chunk parsing bug. The fix is in v0.75.4; any findings missed by
    pre-v0.75.4 Gemini detection runs are a known gap.

- **Chapter 04 (Operations)**:
  - Update OTel distributed tracing guidance (Claim 2): subprocesses and MCP tools
    using the standard OpenTelemetry SDK now automatically participate in distributed
    traces via `OTEL_RESOURCE_ATTRIBUTES` inheritance. No gh-aw-specific
    instrumentation required; child-process trace correlation is now the default
    behavior. Add this as a note to the distributed tracing configuration guidance.
  - Add `linter-miner` benchmarks to the agent budget planning section (Claim 9):
    the >1M token, 39-turn, 10.8-minute profile with 2 failed attempts is a
    concrete reference for code-analysis agents in production. Contrast with
    `auto-triage-issues` (<40 seconds, ~270K cached tokens) to illustrate the
    full range of gh-aw agent token budgets by task type. Recommend `gh aw forecast`
    before deploying code-creation agents at scale.

## Extraction Notes

1. **Source depth**: The weekly update is a changelog post covering one release
   (v0.75.4) and an Agent of the Week spotlight. Ten claims were extracted across
   new features, security improvements, bug fixes, documentation, and the agent
   spotlight. The source is a moderately concise changelog post; depth comes from
   the specificity of the feature descriptions and the Agent of the Week metrics.

2. **WebFetch extraction**: Source content was obtained via two WebFetch calls to
   ensure completeness. The first call returned a structured summary; the second
   call requested near-verbatim text. Verbatim quotes confirmed across both calls:
   "The Codex engine now includes secret diagnostics, missing-key fast-fail, and
   `--json` streaming mode." / "OTEL_RESOURCE_ATTRIBUTES are now injected into
   gh-aw workflows, so child processes using the OpenTelemetry SDK automatically
   inherit trace context" / "Claude's permission mode (`acceptEdits` vs
   `bypassPermissions`) was previously derived implicitly from bash wildcard
   detection" / "It took 39 turns and 10.8 minutes, burning through over a million
   tokens." Other descriptions are WebFetch model summaries; claims marked "(no
   direct quote; see paraphrase in Our assessment)" reflect descriptions that could
   not be verified character-for-character.

3. **No contradictions filed**: Reviewed all existing source notes, particularly
   `blog-ghaw-weekly-2026-04-27.md` (permission flag migration), `blog-ghaw-weekly-
   2026-05-11.md` (OTel additions), `docs-ghaw-permissions-reference.md` (permissions
   model), and `docs-ghaw-inline-sub-agents.md` (sub-agent model defaults). No claim
   in this source materially opposes any existing corpus claim. The explicit
   `engine.permission-mode` is additive to the April 27 flag-rename (not contradictory).
   The OTel resource attribute inheritance is additive to prior OTel span additions.
   No contradiction issue warranted.

4. **Version gap**: The May 11 note covered v0.71.5–v0.72.1. The May 25 note covers
   v0.75.4 (from stable v0.74.8 via six pre-releases). This implies approximately
   three minor version bumps (v0.72 → v0.73 → v0.74 → v0.75) between the two weekly
   posts, consistent with rapid weekly release cadence. No source notes cover the
   intervening v0.73.x or v0.74.x releases; the claims in this note represent the
   state as of v0.75.4 without full visibility into what changed in intermediate
   versions.

5. **`linter-miner` is a different agent than prior Agent of the Week subjects**:
   All previous Agent of the Week spotlights in the corpus featured `auto-triage-issues`.
   `linter-miner` is the first spotlight on a code-creation agent. The longitudinal
   `auto-triage-issues` series and this new `linter-miner` data point are not
   directly comparable (different task types), but together they expand the corpus's
   coverage of agent benchmark profiles.
