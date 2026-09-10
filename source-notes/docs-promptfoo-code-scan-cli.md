---
source_url: https://www.promptfoo.dev/docs/code-scanning/cli/
source_type: docs
title: "Promptfoo Code Scanning — CLI Command"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-10
date_extracted: 2026-09-10
last_checked: 2026-09-10
status: current
confidence_overall: emerging
issue: "#1264"
---

# Promptfoo Code Scanning — CLI Command

> The CLI/command-surface reference for Promptfoo's LLM-security code scanner
> (`promptfoo code-scans run`). The primary contribution is the concrete
> operational interface: the full flag surface with defaults, the
> `.promptfoo-code-scan.yaml` config schema (severity threshold = CI-gating
> knob), the auth-precedence chain, and the JSON output schema with the
> `skipReason` empty-result gotcha and the `aiAgentPrompt` agent-remediation
> field — the operational complement to the scanner methodology in #292 and
> the CI wiring in #1265.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Code Scanning CLI Command page)
- **Author credibility**: Promptfoo, the commercial LLM-security scanner vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  `promptfoo code-scans` command's own interface — authoritative about the
  product's documented flag/config/output surface, but vendor-positioned: scan
  behavior claims (detection quality, runtime ranges) are not independently
  validated. The schema tables and defaults are directly checkable against the
  installed CLI and are the most citable content.
- **Scope**: Covers the CLI usage (`promptfoo code-scans run [repo-path] [options]`),
  the full options table with defaults, `.promptfoo-code-scan.yaml` config schema,
  custom guidance invocation, authentication precedence, JSON output schema, and
  SARIF export. Does NOT cover the scanner's code-analysis methodology
  (far-tracing, call-graph, custom-guidance design rationale — see
  `blog-promptfoo-building-security-scanner-llm-apps.md`, #292) or the GitHub
  Action CI wiring / supply-chain hardening / SARIF publishing path
  (see `docs-promptfoo-code-scan-github-action.md`, #1265).
- **Vendor caveat**: Scans run against the Promptfoo-hosted API
  (`--api-host` default `https://api.promptfoo.app`) and a bare CLI install
  requires authentication with a Promptfoo account. Treat documented runtime
  ranges and behavior as vendor guidance to verify, not independently
  established practice; the flag/config/schema surface is vendor-documented
  product behavior.

## Extracted Claims

### Claim 1: The `promptfoo code-scans` command scans code changes for LLM-specific security vulnerabilities (prompt injection, jailbreaks, PII exposure) before they reach production
- **Evidence**: The page's opening description of the command, backed by the
  Quick Start (install globally, authenticate, `promptfoo code-scans run`).
- **Confidence**: settled (documented product behavior — the command's stated purpose)
- **Quote**: "The `promptfoo code-scans` command scans code changes for LLM-related security vulnerabilities, helping you identify prompt injection risks, jailbreaks, PII exposure, and other security issues before they reach production."
- **Our assessment**: Buy it as a product fact. This page is the operational
  interface to the scanner whose detection methodology (#292: far-tracing,
  call-graph, custom guidance) is already in the corpus. The command is
  usable inline (local dev) and programmatically (CI), which is what makes it
  the wiring surface the triage flagged. The vulnerability categories named
  (injection, jailbreaks, PII) are the scanner's declared scope, not a
  validated prevalence ranking.

### Claim 2: A bare CLI scan runs against the Promptfoo-hosted API and requires Promptfoo account authentication — the scanner is SaaS-dependent, not standalone
- **Evidence**: The `--api-host` option defaults to `https://api.promptfoo.app`
  and the Quick Start requires `promptfoo auth login` before `promptfoo code-scans run`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Authenticate with your promptfoo account:"
- **Our assessment**: Buy it as a vendor-positioned fact. Interesting for the
  guide: teams cannot run Promptfoo Code Scanning air-gapped without Enterprise
  on-prem (per the sibling #1265 note's vendor caveat). The `--api-host`
  override exists, but the default path ships code off to the vendor — a
  data-governance consideration for LLM-app teams, and a distinction from
  open-source alternatives (e.g. `blog-promptfoo-open-sourcing-modelaudit.md`,
  #553). Matches the #1265
  note's vendor caveat that scans run against `https://api.promptfoo.app`.

### Claim 3: A typical PR scan runs 3–10 minutes, with a minute-or-two floor and 20+ minute ceiling for large codebases
- **Evidence**: The Running Time section states the range and the typical case.
- **Confidence**: anecdotal (vendor-reported runtime envelope, no independent measurement)
- **Quote**: "Depending on the size of your PR and codebase, the scan can take anywhere from a minute or two to 20 minutes or more. That said, most PRs take between 3 and 10 minutes."
- **Our assessment**: Plausible and consistent with #292's claim that far-tracing
  is "incredibly slow and expensive" (Claim 6) — a full-repo-exploration default
  at 3–10 min per PR is a real CI cost. This is the number to use for CI timeout
  budgeting and for deciding scan placement (per-PR gate vs nightly). The 20+
  minute ceiling is exactly when `--diffs-only` (Claim 5) becomes the control
  lever. Treat the specific numbers as vendor-sourced, directionally correct.

### Claim 4: The CLI's diff base auto-detects `main`/`master` and the scan target defaults to `HEAD`, making bare `promptfoo code-scans run` a compare-against-branch scan
- **Evidence**: The Options table: `--base <ref>` default "Auto-detects either
  main or master" and `--compare <ref>` default "HEAD". The Examples section
  shows bare usage, `--compare feature/new-llm-integration`, and the
  two-commit form `--base ffa1b2d3 --compare a9c7e5b6`.
- **Confidence**: settled (documented defaults, directly checkable)
- **Quote**: "Auto-detects either main or master"
- **Our assessment**: Buy it. The comparison model (base vs commit) mirrors
  branch-diff semantics a CI gate needs. The defaults mean a freshly-installed
  CLI does the right thing with no required arguments — low-friction local use
  and trivial inclusion in a CI step. The two-commit form is the citable
  primitive for scanning an arbitrary diff range.

### Claim 5: `--diffs-only` (default false = full-repo exploration) is the documented cost/coverage tradeoff control
- **Evidence**: The Options table: `--diffs-only` → "Scan only PR diffs, don't
  explore full repo", default `false`; the config file comment repeats the
  semantics: "Scan only PR diffs without filesystem exploration (default: false
  = explore full repo)".
- **Confidence**: settled (documented default behavior)
- **Quote**: "Scan only PR diffs, don't explore full repo"
- **Our assessment**: Buy it. This is the concrete cost lever behind #292's
  Claim 6 (far tracing is "incredibly slow and expensive"). Default full-repo
  exploration is the thorough-but-slow mode;
  `--diffs-only` trades coverage for runtime — the PR-gate vs nightly distinction.
  The option exists on both flags and config (`diffsOnly`), which is the
  operationalization the guide can cite for "where to place the scan in the
  pipeline."

### Claim 6: The `.promptfoo-code-scan.yaml` config schema exposes `minSeverity` (both spellings accepted), `diffsOnly`, `guidance`/`guidanceFile`, and `apiHost`, with the severity threshold as the alert-fatigue/CI-gating knob
- **Evidence**: The Configuration File section's schema sample: `minSeverity: medium`
  with the comment "Both minSeverity and minimumSeverity are supported", and the
  commented `guidanceFile` / `apiHost` keys.
- **Confidence**: settled (documented schema, directly checkable)
- **Quote**: "# Both minSeverity and minimumSeverity are supported"
- **Our assessment**: Buy it. The severity threshold is the operational
  implementation of the #292 Claim 9/10 alert-fatigue tradeoff ("alert fatigue
  makes developers ignore legitimate findings") — teams set
  `minSeverity: high` to block on critical/high findings only. `guidance` as a
  block scalar in config is the same mechanism #292 Claim 10 demonstrated as the
  defense-in-depth YAML; this page adds the file-based `guidanceFile` variant
  ("path relative to config file"). The config file name
  (`.promptfoo-code-scan.yaml`) is coordinated with the GitHub Action's
  `config-path` auto-detect (#1265).

### Claim 7: Authentication is resolved by a documented precedence chain — `--api-key` → `PROMPTFOO_API_KEY` env → `promptfoo auth login` → GitHub OIDC (GitHub Action only)
- **Evidence**: The Authentication section lists the methods "checked in order",
  ending with GitHub OIDC "(when used in the Promptfoo GitHub Action): Automatic".
- **Confidence**: settled (documented product behavior)
- **Quote**: "The code scanner supports multiple authentication methods (checked in order):"
- **Our assessment**: Buy it. The precedence chain is the concrete CI-credential
  pattern: secret-first CLI/env overrides, interactive login for humans, and a
  keyless OIDC path only inside the GitHub Action. The #1265 note carries the
  action-side of this model (GitHub App OIDC vs manual API key); this page adds
  the CLI-side precedence. The practical rule for CI: pass `--api-key` or set
  `PROMPTFOO_API_KEY` from a secret so resolution never falls through to an
  interactive login or a shared default.

### Claim 8: `--json` output follows a documented schema — a response object `{success, review, comments[], commentsPosted, skipReason, error}` with per-finding `Comment` objects `{file, line, startLine, finding, fix, severity, aiAgentPrompt}`
- **Evidence**: The JSON Output Schema section's two field tables (Response
  Object, Comment Object) and an example response.
- **Confidence**: settled (documented schema, directly checkable)
- **Quote**: "Prompt for AI coding agents to fix the issue"
- **Our assessment**: Buy it. The machine-consumable schema is what makes the
  scanner wireable into arbitrary tooling (not just GitHub). Two fields matter
  for operations: `skipReason` (Claim 9) and `aiAgentPrompt` (Claim 10). The
  `severity` enum is `critical|high|medium|low|none` — a `none` value
  complicates naive threshold logic (a JSON-driven gate must treat `none` as
  non-reportable, not as an error).

### Claim 9: `skipReason` is set when a scan is intentionally skipped (e.g. fork PR awaiting maintainer approval), in which case `comments` is empty — an empty result is not a clean result
- **Evidence**: Response Object table: `skipReason` — "Set when the scan was
  intentionally skipped (e.g. fork PR awaiting maintainer approval); `comments`
  will be empty".
- **Confidence**: settled (documented schema semantics)
- **Quote**: "Set when the scan was intentionally skipped (e.g. fork PR awaiting maintainer approval); `comments` will be empty"
- **Our assessment**: Buy it, and it's an operational gotcha worth calling out:
  an empty `comments` array is ambiguous between "no findings" (clean) and
  "didn't scan" (skip). Any downstream gating (CI pass/fail, SARIF ingestion)
  must check `success`/`skipReason` before treating empty comments as a pass —
  the JSON-side analogue of the #1265 Claim 5 SARIF conditional-upload rule
  ("Intentionally skipped scans do not publish a clean Code Scanning result").
  This is the same skip-vs-clean distinction seen from the CLI side.

### Claim 10: Each finding ships an `aiAgentPrompt` — a machine-consumable fix prompt for AI coding agents
- **Evidence**: Comment Object table: `aiAgentPrompt` — "Prompt for AI coding
  agents to fix the issue"; the example shows concrete prompts per finding
  (e.g. the prompt to sanitize input at `src/chat/handler.ts`).
- **Confidence**: evolving (documented product behavior; the "agent-ready
  remediation" framing as a generalizable pattern is new to our corpus)
- **Quote**: "Prompt for AI coding agents to fix the issue"
- **Our assessment**: Buy it. The schema guarantees every finding carries an
  agent-consumable prompt, which is the concrete mechanism behind "scanner
  emits agent-ready remediation" — a feedback loop the guide's agent-runbook
  chapter (Ch03) will want: scan → finding → `aiAgentPrompt` → coding agent
  opens a fix PR → re-scan. It is vendor-documented (no independent proof the
  prompts actually drive agent fixes well), so confidence stays emerging.

### Claim 11: `--format sarif` emits location-backed findings that GitHub Code Scanning can display — the reuse route for the existing security toolchain
- **Evidence**: The Examples section shows the redirect form
  `promptfoo code-scans run --format sarif > promptfoo-code-scan.sarif`, with
  "SARIF output includes location-backed findings that GitHub Code Scanning can
  display."
- **Confidence**: settled (documented behavior; SARIF as a format is standard)
- **Quote**: "SARIF output includes location-backed findings that GitHub Code Scanning can display."
- **Our assessment**: Buy it. The file-redirect form is the standalone-CLI
  analogue of the GitHub Action's conditional upload (#1265 Claim 5) — a team
  not using the Action can still pipe the scan into GitHub Code Scanning. The
  location-backed wording matters: findings carry file/line positions
  (matching the `Comment` object's `file`/`line`/`startLine` fields), which is
  what a SARIF consumer needs. Keep the *publishing* path on #1265; this claim
  is only the CLI export surface.

## Concrete Artifacts

### Quick Start (verbatim from Quick Start section)

```bash
npm install -g promptfoo
promptfoo auth login
promptfoo code-scans run
```

### Options table (verbatim rows)

| Option | Description | Default |
|--------|-------------|---------|
| `repo-path` | Path to repository | Current directory (`.`) |
| `--api-key <key>` | Promptfoo API key | From `promptfoo auth` or `PROMPTFOO_API_KEY` env var |
| `--base <ref>` | Base branch/commit to compare against | Auto-detects either main or master |
| `--compare <ref>` | Branch/commit to scan | `HEAD` |
| `--config <path>` | Path to config file | `.promptfoo-code-scan.yaml` |
| `--guidance <text>` | Custom guidance to tailor the scan | None |
| `--guidance-file <path>` | Load guidance from a file | None |
| `--api-host <url>` | Promptfoo API host URL | `https://api.promptfoo.app` |
| `--diffs-only` | Scan only PR diffs, don't explore full repo | false |
| `--json` | Output results as JSON (see schema) | false |
| `-f, --format <format>` | Output format (`text`, `json`, or `sarif`) | `text` |
| `--github-pr <owner/repo#number>` | Post comments to GitHub PR (used with Promptfoo GitHub Action) | None |

Source: promptfoo docs, "Options" section. Verbatim.

### Diff examples (verbatim from Examples section)

```bash
promptfoo code-scans run
promptfoo code-scans run --compare feature/new-llm-integration
promptfoo code-scans run --base ffa1b2d3 --compare a9c7e5b6
promptfoo code-scans run --config custom-scan-config.yaml
promptfoo code-scans run --json
promptfoo code-scans run --format sarif > promptfoo-code-scan.sarif
```

### Config file schema (verbatim from Configuration File section)

```yaml
# Minimum severity level to report (low|medium|high|critical)
# Both minSeverity and minimumSeverity are supported
minSeverity: medium

# Scan only PR diffs without filesystem exploration (default: false = explore full repo)
diffsOnly: false

# Optional: Custom guidance to tailor the scan to your needs
guidance: |
  Focus on authentication and authorization vulnerabilities.
  Treat any PII exposure as high severity.

# Or load guidance from a file (path relative to config file)
# guidanceFile: ./scan-guidance.md

# Optional: Promptfoo API host URL
# apiHost: https://api.promptfoo.dev
```

### JSON output schema field tables (verbatim from JSON Output Schema section)

Response Object:

| Field | Type | Description |
|-------|------|-------------|
| `success` | `boolean` | Whether the scan completed successfully |
| `review` | `string` | Overall review summary of the scan |
| `comments` | `Comment[]` | Array of findings (see below) |
| `commentsPosted` | `boolean` | Whether comments were posted to a PR |
| `skipReason` | `string` | Set when the scan was intentionally skipped (e.g. fork PR awaiting maintainer approval); `comments` will be empty |
| `error` | `string` | Error message if the scan failed |

Comment Object:

| Field | Type | Description |
|-------|------|-------------|
| `file` | `string` | File path where the issue was found, or null |
| `line` | `number` | Line number of the finding, or null |
| `startLine` | `number` | Start line for multi-line findings, or null |
| `finding` | `string` | Description of the security issue |
| `fix` | `string` | Suggested fix for the issue |
| `severity` | `string` | `critical`, `high`, `medium`, `low`, or `none` |
| `aiAgentPrompt` | `string` | Prompt for AI coding agents to fix the issue |

### Example response (verbatim from Example section)

```json
{
  "success": true,
  "review": "The PR introduces an LLM-powered support chat feature. The main security concerns are around prompt injection via user messages and insufficient output validation.",
  "comments": [
    {
      "file": "src/chat/handler.ts",
      "line": 42,
      "startLine": 40,
      "finding": "User input is passed directly to the LLM prompt without sanitization, allowing prompt injection attacks.",
      "fix": "Sanitize user input and use a system prompt that instructs the model to ignore injected instructions.",
      "severity": "critical",
      "aiAgentPrompt": "In src/chat/handler.ts around line 42, add input sanitization before passing user messages to the LLM. Use a system prompt with injection-resistant instructions."
    },
    {
      "file": "src/chat/handler.ts",
      "line": 87,
      "startLine": null,
      "finding": "LLM responses are rendered as raw HTML without escaping, which could allow cross-site scripting if the model is manipulated.",
      "fix": "Escape or sanitize LLM output before rendering it in the UI.",
      "severity": "high",
      "aiAgentPrompt": "In src/chat/handler.ts at line 87, escape the LLM response output before inserting it into the DOM to prevent XSS."
    }
  ]
}
```

## Cross-References

- **Corroborates**:
  - `blog-promptfoo-building-security-scanner-llm-apps.md` **Claim 6** (far
    tracing "is incredibly slow and expensive") — this page's runtime envelope
    (Claim 3: 3–10 min typical, 20+ min ceiling, full-repo exploration by
    default) is the documented cost that methodology claim predicts.
  - `blog-promptfoo-open-sourcing-modelaudit.md` **Claim 12** ("ModelAudit
    supports SARIF output, SBOM generation, secret scanning, and license
    detection") — SARIF export is a capability shared across Promptfoo's
    scanners; this page documents the CLI mechanism (`--format sarif`) for the
    same capability, for the Code Scanning product rather than ModelAudit.
- **Contradicts**: None identified. This page is a first-party CLI reference for
  the same product whose methodology (#292) and GitHub Action wiring (#1265) are
  already mined; the surfaces are complementary layers of one tool, and no claim
  here opposes an existing note's claim. No contradiction issue is required
  (open contradiction issues are unrelated: #1150 is a LiteLLM routing topic).
- **Extends**:
  - `blog-promptfoo-building-security-scanner-llm-apps.md` **Claim 10** (custom
    guidance as a config-level strictness-tuning mechanism) — this page
    operationalizes the guidance from the blog as the file-based config surface
    (`guidance:` block scalar + `guidanceFile:` in `.promptfoo-code-scan.yaml`,
    Claim 6), providing the concrete deployment artifact for the design pattern.
  - `docs-promptfoo-code-scan-github-action.md` (**#1265**) — the two pages are
    sibling surfaces of the same product. This page extends #1265's Claim 7
    (`min-severity` action input) with the CLI/config-side severity knob
    (`minSeverity`/`minimumSeverity`, Claim 6), and #1265's Claim 6 (two-auth
    trust model) with the full CLI-side precedence chain (Claim 7).
  - `docs-promptfoo-code-scan-github-action.md` **Claim 5** (SARIF published
    only on completed scans; "Intentionally skipped scans do not publish a clean
    Code Scanning result") — this page's `skipReason` semantics (Claim 9) are
    the CLI-side statement of the same skip-vs-clean distinction.
- **Novel**:
  1. **The full CLI/flag surface with defaults** for `promptfoo code-scans run` —
     the first complete command reference in the corpus (option table, artifact).
  2. **The auth precedence chain for a scanning CLI** — `--api-key` →
     `PROMPTFOO_API_KEY` → `promptfoo auth login` → GitHub OIDC, as an ordered
     credential-resolution pattern.
  3. **The `skipReason` JSON-semantics gotcha** — empty `comments` on an
     intentionally-skipped scan must not be treated as a clean pass (from the
     CLI schema side).
  4. **`aiAgentPrompt` per finding** — a documented schema field that turns each
     scanner finding into a machine-consumable fix prompt for an AI coding agent
     ("scanner emits agent-ready remediation").
  5. **The `--diffs-only` cost/coverage knob** as an explicit, defaulted option
     (full-repo exploration by default) — the concrete tradeoff control for scan
     placement and runtime.
  6. **The SaaS-dependency data point** — default scans run against
     `https://api.promptfoo.app` (Claim 2), a governance consideration not
     previously documented in the corpus for this product.

## Guide Impact

- **Chapter 06 (Security and Trust)**, section "Red-teaming as a CI gate" /
  CI-gating LLM vulnerability scanning: This page provides the concrete vendor
  mechanism the chapter's existing CI-gate concept was missing — the
  `.promptfoo-code-scan.yaml` `minSeverity` threshold as the merge-gating knob
  (Claim 6), the `--diffs-only` full-repo vs PR-diff tradeoff (Claim 5), and the
  runtime budget of 3–10 min typical / 20+ min ceiling for scan placement (Claim
  3). **Recommendation**: cite this page (and the sibling #1265 note) as the
  worked example for "how a team actually wires LLM code scanning into a PR
  gate," including the `skipReason` empty-result gotcha (Claim 9) in the
  "downstream gating must not mistake 'skipped' for 'clean'" callout.
- **Chapter 06**, security-tooling section: the auth-precedence chain (Claim 7)
  is a citable CI-credential pattern — explicit secret-passed credentials
  (`--api-key` / env) over interactive or OIDC fallbacks. Also note the
  SaaS-dependency consideration (Claim 2): scans ship code to the vendor by
  default.
- **Chapter 03 (Runbooks and Agents)**, CI/CD gating / agent remediation: the
  `aiAgentPrompt` field (Claim 10) is the concrete "scanner emits
  agent-ready remediation" mechanism — recommend documenting the
  scan → finding → `aiAgentPrompt` → coding agent fix PR → re-scan loop as a
  pattern for agent-driven vulnerability remediation in CI.
- **Chapter 05 (LLM ops reliability)** if present, or the CI-gate material: the
  runtime envelope and `--diffs-only` knob (Claims 3, 5) are the numbers to cite
  for CI timeout budgeting and for deciding per-PR vs nightly scan placement.

## Extraction Notes

- Source read in full: https://www.promptfoo.dev/docs/code-scanning/cli/
  (fetched via direct HTTP, HTML + rendered markdown). Single self-contained
  docs page; "Last updated on Sep 10, 2026" by mldangelo-oai. No sub-pages were
  required beyond the schema/example sections already on the page (the Custom
  Guidance section links to the code-scanning overview page for what guidance
  "can do"; #292 already covers the guidance mechanism at depth).
- Coordination with sibling #1265 (`docs-promptfoo-code-scan-github-action.md`):
  per that note's Extraction Notes, the CLI note carries the CLI interface
  surface and #1265 carries the GitHub Code Scanning publishing path. This note
  keeps SARIF coverage to the CLI export flag (Claim 11) and the
  `skipReason`/empty-comments gotcha (Claim 9); the conditional-upload
  SARIF publishing detail lives in #1265 and is not duplicated here.
- The Prospector triage (three concurrent runs) plus #1265's extraction notes
  explicitly recommended extracting ONLY the net-new operational artifacts and
  NOT re-deriving the far-tracing/custom-guidance methodology from #292. This
  note follows that guidance.
- Cross-reference candidates file (`miner-related-notes.md`) read per MINER.md
  §4 before writing Cross-References. All 10 candidates dismissed as
  non-overlapping: `docs-langfuse-mcp-server.md` (docs MCP server), `blog-pagerduty-sre-agent-triage.md` (AI incident triage), `blog-promptfoo-red-team-claude.md` (runtime model red-teaming, no code-scanning interface content),
  `docs-google-sre-reliable-product-launches.md` (launch process),
  `docs-google-sre-eliminating-toil.md` (toil), `docs-google-sre-team-lifecycles.md`
  (team org), `docs-google-sre-prodcast-04-05-furino-slos.md` (SLO construction),
  `blog-promptfoo-owasp-red-teaming.md` (runtime attack simulation in CI/CD; same
  thematic CI-security-testing arena but no evidential overlap with the CLI
  command surface — consistent with the #1265 note's dismissal),
  `blog-incidentio-ai-sre-incident-run.md` (incident runs), and
  `docs-datadog-llm-observability.md` (LLM observability, not security scanning).
  The real cross-references (`blog-promptfoo-building-security-scanner-llm-apps.md`,
  `docs-promptfoo-code-scan-github-action.md`, `blog-promptfoo-open-sourcing-modelaudit.md`)
  were discovered by searching `source-notes/`. Each cited claim was re-read and
  its number verified per MINER.md §4b before citation.
- All quoted passages and schema artifacts were copied character-for-character
  from the fetched source HTML (the YAML config block, option tables, JSON
  schema tables, and example response were extracted from the rendered page,
  not reconstructed from memory).
- Vendor caveat: the page is Promptfoo's vendor documentation; flag defaults and
  schema are documented product behavior (directly checkable against the
  installed CLI) while runtime ranges and detection behavior are vendor-reported.
  confidence_overall is `emerging`, consistent with the sibling #1265 note and
  lower than the settled-confidence schema items individually.