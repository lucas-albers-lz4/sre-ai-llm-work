---
source_url: https://github.github.com/gh-aw/reference/audit
source_type: docs
title: "GitHub Agentic Workflows: Audit Command Reference"
author: GitHub Agentic Workflows team (GitHub Next / Microsoft Research)
date_published: null
date_extracted: 2026-05-26
last_checked: 2026-05-26
status: current
confidence_overall: emerging
issue: "#450"
---

# GitHub Agentic Workflows: Audit Command Reference

> The authoritative reference for the `gh aw audit` and `gh aw logs` CLI commands —
> documents the full flag surface, five accepted input formats (including GitHub Enterprise
> URLs), single-vs-multi-run output modes, the eight named single-run report sections,
> the `ambient_context` token metrics object, the explicit output stability contract, and
> the `gh aw logs` cross-run aggregate report. Complements `docs-ghaw-audit-with-agents.md`
> (patterns for consuming audit output in workflows) by providing the command-level
> technical specification those workflow patterns depend on.

## Source Context

- **Type**: docs (official GitHub Agentic Workflows `reference/audit` page — in the
  `reference/` section, the same tier as `reference/triggering-ci`, `reference/artifacts`,
  and `reference/repo-memory`. Reference pages document the complete CLI surface with
  flags, defaults, and output schemas authoritatively, distinct from `guides/` how-to
  pages and `patterns/` design-pattern pages.)
- **Author credibility**: First-party from GitHub Next / Microsoft Research — the same
  team behind Peli de Halleux's agent factory blog series and the `gh aw` CLI platform.
  Flag names, defaults, input format specifications, and the output stability contract are
  authoritative for the `gh aw` platform. Claims do not automatically generalize to other
  audit CLI tools.
- **Scope**: Complete reference for the `gh aw audit` and `gh aw logs` CLI commands —
  input formats, flag surface, single-vs-multi-run output behavior, named report sections,
  token metrics fields, and the output stability contract. Also covers four workflow
  integration examples at a high level. Does NOT cover: how to consume audit output in
  autonomous workflows (see `docs-ghaw-audit-with-agents.md` issue #294), the artifact
  files produced during a run (see `docs-ghaw-artifacts-reference.md` issue #449), or the
  underlying firewall and network configuration (see `docs-ghaw-network-reference.md`).

## Extracted Claims

### Claim 1: `gh aw audit` accepts five distinct input formats — numeric run ID, full run URL, job URL with optional step anchor, short URL variants, and GitHub Enterprise URLs — enabling flexible invocation across development environments

- **Evidence**: The "Input Formats Accepted" subsection enumerates all five formats
  explicitly with examples for each. GitHub Enterprise URL support is called out as a
  distinct format rather than a flag.
- **Confidence**: settled (first-party reference documentation; the format list is
  explicit and enumerated)
- **Quote**: "Numeric run ID: `1234567890`" and "GitHub Enterprise URLs" appear as
  distinct listed formats in the Input Formats Accepted section.
- **Our assessment**: The variety of accepted input formats matters for harness design:
  practitioners can wire audit invocations from GitHub Actions event payloads
  (`github.event.workflow_run.id` is numeric), from CI/CD UI copy-paste (full run URL),
  or from GitHub Enterprise instances — without format conversion. The step-anchor
  variant (`job URL with optional step anchor`) enables audit scoping to a specific job
  step, which is useful for debugging a single tool call within a multi-step agent run.
  For Ch02 (Harness Engineering): document that `gh aw audit` accepts both numeric IDs
  and URLs interchangeably — practitioners do not need a URL-to-ID lookup step.

### Claim 2: Passing multiple run IDs or URLs to `gh aw audit` switches the command from individual reports to a comparative diff report, using the first argument as the baseline

- **Evidence**: The purpose description is explicit: "Single runs produce detailed
  Markdown reports; two or more runs generate comparative diff reports using the first
  as the baseline."
- **Confidence**: settled (first-party reference documentation; the mode switch is stated
  unambiguously)
- **Quote**: "Single runs produce detailed Markdown reports; two or more runs generate
  comparative diff reports using the first as the baseline."
- **Our assessment**: This is a meaningful CLI design decision: the same command handles
  both point-in-time audit and regression-detection diff, with the number of arguments
  selecting the mode. For practitioners building harness workflows, this means the
  regression detection workflow (`docs-ghaw-audit-with-agents.md` Claim 9) passes two
  run IDs to trigger the diff mode — not a separate subcommand. The baseline-first
  argument convention is important: accidentally reversing argument order would produce
  a diff measured in the wrong direction. For Ch02: document the multi-argument mode
  as the mechanism for `audit diff`, and note the argument order convention.

### Claim 3: The `--parse` flag runs JavaScript parsers on agent and firewall logs to populate `behavior_fingerprint` and `agentic_assessments` fields — opt-in semantic enrichment beyond the base output schema

- **Evidence**: The flag table lists `--parse` as "Run JavaScript parsers on agent/firewall
  logs" with default `off`. The report sections describe `behavior_fingerprint` and
  `agentic_assessments` as named sections that appear in single-run reports.
- **Confidence**: settled (first-party reference documentation; the mechanism — JavaScript
  parsers on log files — is specified, not just the effect)
- **Quote**: "Run JavaScript parsers on agent/firewall logs"
- **Our assessment**: The JavaScript parsers on log files is a technical implementation
  detail not documented in `docs-ghaw-audit-with-agents.md` Claim 12 (which only notes the
  effect on output fields). The mechanism matters: `--parse` is post-processing of artifact
  log files, not a different audit mode. This means the enrichment is available for any
  completed run — it is not a real-time analysis option. The output fields it populates
  (`behavior_fingerprint`, `agentic_assessments`) appear as named sections in the
  single-run report, confirming they are structured report sections rather than embedded
  prose. For Ch02: when building audit-consumer workflows that require behavioral
  classification, `--parse` must be included in the `gh aw audit` invocation.

### Claim 4: The `ambient_context` metrics object captures the first LLM inference footprint with input tokens, cached tokens, and effective tokens — enabling measurement of the initial prompt context cost

- **Evidence**: The Metrics section states: "Metrics Include: `ambient_context` object
  capturing first LLM inference footprint, Input tokens, cached tokens, and effective tokens."
- **Confidence**: settled (first-party reference documentation; the object name and its
  three sub-fields are explicitly named)
- **Quote**: "`ambient_context` object capturing first LLM inference footprint"
- **Our assessment**: The `ambient_context` object is a new concept not present in any
  other corpus source note. "First LLM inference footprint" refers to the initial context
  load — the tokens consumed when the model first processes the workflow's instructions
  and context before any tool calls. Separating this from total run tokens is significant:
  cached tokens and effective tokens within `ambient_context` allow practitioners to
  measure how much of the context overhead is absorbed by prompt caching. For Ch02
  (Harness Engineering): the `ambient_context` metric is the per-run baseline for context
  engineering overhead — high `ambient_context` token counts signal a large initial
  prompt (e.g., a long CLAUDE.md or large tool corpus). For cost optimization, cached
  tokens within `ambient_context` indicate how effectively the harness reuses context
  across invocations.

### Claim 5: A single-run `gh aw audit` report contains at least eight named sections — Overview, Behavior Fingerprint, Agentic Assessments, Metrics, Key Findings, MCP Server Health, Tool Usage, and Firewall Analysis

- **Evidence**: The "Single-Run Report Sections" field in the command description lists
  these explicitly: "Overview, Behavior Fingerprint, Agentic Assessments, Metrics, Key
  Findings, MCP Server Health, Tool Usage, Firewall Analysis, and more."
- **Confidence**: settled (first-party documentation; the section names are enumerated as
  the canonical structure of the report)
- **Quote**: "Overview, Behavior Fingerprint, Agentic Assessments, Metrics, Key Findings,
  MCP Server Health, Tool Usage, Firewall Analysis, and more."
- **Our assessment**: The "and more" qualifier indicates this is a non-exhaustive list,
  but these eight sections are the named, stable report structure. The presence of
  "Behavior Fingerprint" and "Agentic Assessments" as named top-level sections (not
  just fields) signals they are first-class report components, not annotations — but
  they only appear with `--parse` (Claim 3). "MCP Server Health" as a named section
  confirms that MCP tool reliability monitoring is a first-class audit output. For Ch03
  (Safety and Verification): document these eight sections as the canonical post-run
  audit report structure; practitioners building review workflows should understand which
  sections exist before building consumers that parse specific report content.

### Claim 6: `gh aw logs` generates cross-run aggregate security and performance reports across a configurable recent-run window, with output including domain inventory, metrics trends, MCP server health, per-run breakdown, and cross-run anomaly detection

- **Evidence**: The command description and report contents list specify these as the
  contents of `gh aw logs` output. The `-c/--count` flag (default 10) sets the window.
- **Confidence**: settled (first-party reference documentation; the report content list
  is explicit)
- **Quote**: "Report Contents: Executive summary, domain inventory, metrics trends,
  MCP server health, per-run breakdown, and cross-run anomaly detection."
- **Our assessment**: `gh aw logs` is distinct from `gh aw audit` in scope: where `audit`
  analyzes a specific run (or compares two runs), `logs` aggregates across the N most
  recent runs. The cross-run anomaly detection output is the key differentiator — it
  surfaces behavioral patterns that only emerge across runs (e.g., a domain that is
  intermittently blocked, an MCP tool whose error rate is trending upward). The default
  window of 10 runs matches the weekly digest workflow in `docs-ghaw-audit-with-agents.md`
  Claim 11, confirming 10 is the practitioner-validated starting point. For Ch02: document
  `gh aw logs` as the aggregate health-check command and `gh aw audit` as the per-run
  inspection command — they serve different monitoring purposes.

### Claim 7: The output stability contract explicitly distinguishes stable top-level fields from extensible nested sub-fields — providing a durable API contract for consumer workflow authors

- **Evidence**: The "Output Stability" section states this directly: "Top-level fields
  (`key_findings`, `recommendations`, `metrics`, `firewall_analysis`, `mcp_tool_usage`)
  are stable; nested sub-fields may be extended but are not removed without deprecation."
- **Confidence**: settled (first-party documentation; the stability contract language is
  explicit and lists the specific stable field names)
- **Quote**: "Top-level fields (`key_findings`, `recommendations`, `metrics`,
  `firewall_analysis`, `mcp_tool_usage`) are stable; nested sub-fields may be extended
  but are not removed without deprecation."
- **Our assessment**: This is the authoritative source for the stability contract that
  `docs-ghaw-audit-with-agents.md` Claim 3 documents from the consumer-workflow perspective.
  The reference page states it explicitly as a contract, not just an observed pattern. The
  five named stable fields match exactly those documented in the guide note's JSON field
  schema. The "extended but not removed without deprecation" policy on nested sub-fields
  gives consumer workflow authors a clear rule: build branching logic on top-level fields;
  treat nested sub-field presence as optional rather than required. For Ch03 (Safety and
  Verification): this is the canonical citation for the stability contract — practitioners
  should reference this page when deciding which fields to depend on in automated workflows.

### Claim 8: The `--stdin` flag enables reading run IDs and URLs from stdin rather than command arguments — supporting pipeline-style invocation patterns

- **Evidence**: The flag table lists `--stdin` with default `off` and purpose "Read
  IDs/URLs from stdin instead of arguments."
- **Confidence**: settled (first-party reference documentation; the flag purpose is
  explicit)
- **Quote**: "Read IDs/URLs from stdin instead of arguments"
- **Our assessment**: The `--stdin` flag enables shell pipeline composition: a command
  that lists recent run IDs (e.g., `gh run list --json databaseId`) can be piped to
  `gh aw audit --stdin` without intermediate variable assignment. This is particularly
  useful for batch audit scripts that process a dynamically generated list of runs.
  For Ch02: document `--stdin` as the scripting-friendly invocation path for audit
  batch operations.

### Claim 9: The `--format` flag on `gh aw audit` controls diff report output format with `pretty` (default for terminal viewing) and `markdown` (for programmatic use in PR comments and issue bodies)

- **Evidence**: The flag table lists `--format` as "Diff format: `pretty` or `markdown`"
  with default `pretty`. The workflow integration example "PR Comment with Findings"
  implies markdown-formatted output for posting to PR comments.
- **Confidence**: settled (first-party reference documentation; the two format values
  are named explicitly)
- **Quote**: "Diff format: `pretty` or `markdown`"
- **Our assessment**: The `--format` flag closes the loop between the audit command and
  the PR-comment posting workflow: the agent calls `gh aw audit --format markdown` and
  posts the result to a PR comment verbatim. The `pretty` format is for local terminal
  inspection; `markdown` is for automated workflows that embed audit output in GitHub
  UI. This is a small but important harness design detail — a PR comment consumer that
  forgets `--format markdown` will post ANSI escape sequences or terminal formatting to
  the PR comment. For Ch02: when building audit-consumer workflows that post to GitHub
  UI, always specify `--format markdown`.

### Claim 10: The `--repo` flag specifies the repository context for bare numeric run IDs — required when the run ID lacks the URL context needed to identify the repository

- **Evidence**: The flag table lists `--repo` with default `auto` and purpose "Repository
  specification for bare numeric IDs."
- **Confidence**: settled (first-party reference documentation; the flag purpose is
  explicit)
- **Quote**: "Repository specification for bare numeric IDs"
- **Our assessment**: The `auto` default attempts repository detection from the current
  working directory context (likely via the `gh` CLI's standard repository detection).
  The `--repo` flag is required when the audit command is invoked outside a repository
  context — for example, in a centralized audit script that audits runs from multiple
  repositories. For Ch02: document `--repo` as the required flag for cross-repository
  audit scripts; it is unnecessary for workflows invoked within the repository they audit.

## Concrete Artifacts

### `gh aw audit` Command Flags Reference

```
gh aw audit <run-id-or-url> [<run-id-or-url>...]

Input Formats Accepted:
  - Numeric run ID:              1234567890
  - Run URL:                     https://github.com/owner/repo/actions/runs/1234567890
  - Job URL with optional step anchor
  - Short run URL variants
  - GitHub Enterprise URLs

Flags:
  -o, --output   ./logs    Output directory for artifacts and reports
  --json         off       Output as JSON to stdout
  --parse        off       Run JavaScript parsers on agent/firewall logs
  --repo         auto      Repository specification for bare numeric IDs
  --stdin        off       Read IDs/URLs from stdin instead of arguments
  --format       pretty    Diff format: pretty or markdown

Single-Run Report Sections:
  Overview, Behavior Fingerprint, Agentic Assessments, Metrics,
  Key Findings, MCP Server Health, Tool Usage, Firewall Analysis, and more

Metrics Include:
  ambient_context object:
    - first LLM inference footprint
    - input tokens
    - cached tokens
    - effective tokens
```
(Source: https://github.github.com/gh-aw/reference/audit — Core Commands section)

### `gh aw logs` Command Flags Reference

```
gh aw logs --format <fmt>

Parameters:
  [workflow]   all        Filter by workflow name
  -c, --count  10         Number of recent runs
  --format     —          Output format: markdown or pretty
  --json       off        JSON output mode
  -o, --output ./logs     Artifact directory

Report Contents:
  Executive summary, domain inventory, metrics trends, MCP server health,
  per-run breakdown, and cross-run anomaly detection
```
(Source: https://github.github.com/gh-aw/reference/audit — Core Commands section)

### Output Stability Contract

```
Stable top-level fields:
  key_findings
  recommendations
  metrics
  firewall_analysis
  mcp_tool_usage

Nested sub-fields policy:
  "may be extended but are not removed without deprecation"

Fields populated only with --parse (not stable):
  behavior_fingerprint    → agent behavior pattern classification
  agentic_assessments     → AI-generated assessment
```
(Source: https://github.github.com/gh-aw/reference/audit — Output Stability section)

### Workflow Integration Examples (High-Level)

```
1. PR Comment with Findings
   - Post audit summaries as PR comments
   - Highlight high-severity issues and blocked domains

2. Regression Detection
   - Compare two runs (multi-run diff mode)
   - Flag: new blocked domains, elevated MCP error rates,
     cost increase > 20%, token usage spike > 50%

3. Issue Filing
   - Create GitHub issues for high-severity audit findings
   - Include impact descriptions and remediation recommendations

4. Weekly Monitoring Agent
   - Generate weekly digests tracking cost spikes, domain changes,
     MCP server reliability, and historical trends
   - Uses cached baseline data for trend comparison
```
(Source: https://github.github.com/gh-aw/reference/audit — Workflow Integration Examples section)

## Cross-References

- **Corroborates**:
  - `docs-ghaw-audit-with-agents.md` Claim 3: that note documents the stable top-level
    fields from the consumer-workflow perspective as an implied stability contract; this
    reference page states the same contract explicitly with identical field names
    (`key_findings`, `recommendations`, `metrics`, `firewall_analysis`, `mcp_tool_usage`).
    The reference page is the authoritative citation for Claim 3's stability contract.
  - `docs-ghaw-audit-with-agents.md` Claim 12: the `--parse` flag populating
    `behavior_fingerprint` and `agentic_assessments` fields. This reference adds
    the mechanism (JavaScript parsers on agent/firewall logs) and confirms both fields
    appear as named report sections, not just JSON fields.
  - `docs-ghaw-audit-with-agents.md` Claim 4 regression thresholds (cost >20%,
    tokens >50%): the Workflow Integration Examples section on this reference page
    lists the same thresholds ("cost increase > 20%, or token usage spikes surpassing 50%"),
    independently corroborating the values documented in the guide note.

- **Extends**:
  - `docs-ghaw-audit-with-agents.md` — that guide documents how to *consume* audit
    output in workflows (patterns, thresholds, workflow specs). This reference documents
    the *command itself* — the flag surface, input formats, and output structure the
    workflow patterns depend on. Together they form a complete audit system reference.
  - `docs-ghaw-artifacts-reference.md` — the artifacts reference documents what files
    `gh aw audit` downloads to the output directory (`./logs`). This reference documents
    what the command produces as report output (Markdown and JSON) — complementary views
    of the same command's outputs.

- **Contradicts**: None. All claims align with existing source notes. The `ambient_context`
  object (Claim 4) and the `--stdin` / `--repo` flags (Claims 8, 10) are new to the corpus
  but do not conflict with any existing claims.

- **Novel**:
  - **`ambient_context` metrics object** (Claim 4): the "first LLM inference footprint"
    concept with input/cached/effective tokens is not described in any existing source note.
    This is the first per-run context cost measurement mechanism in the corpus.
  - **Five enumerated input formats including GitHub Enterprise URL support** (Claim 1):
    no existing note documents the full input format surface for `gh aw audit`. GHE URL
    support is particularly notable for enterprise practitioners.
  - **Named single-run report sections** (Claim 5): the eight named sections (Overview,
    Behavior Fingerprint, Agentic Assessments, Metrics, Key Findings, MCP Server Health,
    Tool Usage, Firewall Analysis) are not enumerated as a list in any existing note —
    `docs-ghaw-audit-with-agents.md` references individual field names but not the
    report's section structure.
  - **`--stdin` pipeline flag** (Claim 8): not documented in any existing corpus note.
    Enables batch audit scripting patterns.
  - **`--format markdown` distinction from `--format pretty`** (Claim 9): the two-mode
    format flag and its implications for PR comment posting are not documented in any
    existing note.
  - **Explicit output stability contract text** (Claim 7): while `docs-ghaw-audit-with-agents.md`
    implies the contract, this page states it verbatim. This is the canonical citation.

## Guide Impact

- **Chapter 02 (Harness Engineering)**:
  - Add `gh aw audit` input format surface as a reference note: practitioners do not
    need URL-to-ID conversion before invoking the command. The five accepted formats
    cover all practical invocation contexts (Actions payload, UI copy-paste, GHE).
  - Document the single-vs-multi-run mode switch: two arguments = diff mode, first
    argument = baseline. This is the mechanism behind regression detection workflows.
  - Document `--format markdown` as required for any audit consumer that posts to GitHub
    UI (PR comments, issue bodies). Missing this flag produces terminal-formatted output
    in a GitHub comment.
  - Document `--stdin` as the pipeline invocation flag for batch audit scripts.
  - Add `ambient_context` to the metrics discussion: it is the per-run baseline for
    context engineering overhead. High `ambient_context` counts signal large initial
    prompts; high cached-token fractions signal effective prompt caching.
  - Document `gh aw logs` as the aggregate health-check command (N recent runs) and
    `gh aw audit` as the per-run inspection command — they are complementary, not
    redundant.

- **Chapter 03 (Safety and Verification)**:
  - Use this reference page as the canonical citation for the output stability contract
    (currently, `docs-ghaw-audit-with-agents.md` Claim 3 is the only corpus source —
    this reference page is the authoritative source and should be cited alongside it).
  - Document the eight named report sections as the canonical post-run audit structure,
    so practitioners know what to expect from a `gh aw audit` invocation and which
    sections contain the verification signals (Key Findings, MCP Server Health, Firewall
    Analysis).
  - Note that `--parse` is required to populate Behavior Fingerprint and Agentic
    Assessments — verification workflows that need behavioral classification must include
    this flag.

## Extraction Notes

1. **Reference page is complementary to, not overlapping with, `docs-ghaw-audit-with-agents.md`**:
   The existing guide note (issue #294) covers workflow patterns for consuming audit output.
   This reference covers the command technical surface. The Prospector's triage comment
   accurately characterizes the relationship: "complementary, not duplicate."

2. **Workflow integration examples on the reference page are summaries, not full specs**:
   The four workflow integration examples listed on the reference page are high-level
   one-to-two-sentence descriptions, not the full YAML workflow specs found in the guide
   note. Full specs are in `docs-ghaw-audit-with-agents.md`.

3. **`ambient_context` sub-fields not further specified**: The reference page names the
   three sub-fields (input tokens, cached tokens, effective tokens) but does not document
   their JSON field names, types, or units. The field names likely match the broader
   metrics convention in the platform but are not confirmed in this source.

4. **"And more" in report sections**: The single-run report sections list ends with "and
   more," indicating the eight named sections are not exhaustive. The reference page does
   not enumerate all sections.

5. **No contradictions found**: Reviewed `docs-ghaw-audit-with-agents.md` (issue #294),
   `docs-ghaw-artifacts-reference.md` (issue #449), `docs-ghaw-how-they-work.md`
   (issue #254), and `blog-ghaw-agent-observability.md`. No claims in this source oppose
   existing notes. The `ambient_context` object and input format enumeration are entirely
   new to the corpus.
