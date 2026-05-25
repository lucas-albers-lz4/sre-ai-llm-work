---
source_url: https://github.github.com/gh-aw/reference/triggers
source_type: docs
title: "GitHub Agentic Workflows: Triggers Reference"
author: GitHub Agentic Workflows team (GitHub Next / Microsoft Research)
date_published: null
date_extracted: 2026-05-25
last_checked: 2026-05-25
status: current
confidence_overall: emerging
issue: "#418"
---

# GitHub Agentic Workflows: Triggers Reference

> The authoritative unified catalog of all gh-aw trigger types — documents 10 named
> trigger types (including `slash_command`, `label_command`, `repository_dispatch`,
> and `workflow_run`), cross-cutting filtering mechanisms (search query, role, bot,
> author association, and custom step filtering), the fuzzy schedule scattering model,
> pre-activation steps and dependencies, and advanced options (`stop-after:`,
> `manual-approval:`, `lock-for-agent:`) not fully documented in any pattern-specific
> note.

## Source Context

- **Type**: docs (official GitHub Agentic Workflows `reference/triggers` page — in
  the "Reference" section, parallel to `reference/concurrency`, `reference/permissions`,
  and `reference/artifacts`. Reference pages document the complete platform API; this
  one is the master trigger configuration reference.)
- **Author credibility**: First-party from GitHub Next / Microsoft Research (the same
  team behind Peli de Halleux's agent factory series and all other gh-aw documentation
  in the corpus). Trigger type enumeration, YAML field names, and filtering behavior
  are settled platform facts. Pattern guidance on when to prefer one trigger type over
  another carries the weight of first-party design intent but may not generalize to
  non-gh-aw agentic platforms.
- **Scope**: Covers the complete `on:` section configuration — all 10 named trigger
  types, all filtering mechanisms, and all supplementary options (reactions, status
  comments, token configuration, activation gates). Does NOT cover: Safe Outputs
  model (see `docs-ghaw-how-they-work.md`), concurrency configuration (see
  `docs-ghaw-concurrency-reference.md`), permissions beyond pre-activation scope
  (see `docs-ghaw-permissions-reference.md`), or pattern-specific workflow design
  guidance (see `docs-ghaw-dispatch-ops.md`, `docs-ghaw-labelops.md`,
  `docs-ghaw-chatops.md`, `docs-ghaw-issueops.md`).

## Extracted Claims

### Claim 1: gh-aw extends standard GitHub Actions `on:` syntax with reactions, cost control, and advanced filtering — the triggers reference is the master catalog of all 10 supported trigger types

- **Evidence**: The page opens with: "The `on:` section configures when workflows
  execute using GitHub Actions syntax. GitHub Agentic Workflows supports standard
  GitHub Actions triggers plus enhancements for reactions, cost control, and advanced
  filtering." Ten named trigger types are enumerated and documented.
- **Confidence**: settled (first-party reference; the enumeration is an authoritative
  platform specification)
- **Quote**: "GitHub Agentic Workflows supports standard GitHub Actions triggers plus
  enhancements for reactions, cost control, and advanced filtering."
- **Our assessment**: The framing as "standard GitHub Actions triggers plus enhancements"
  is architecturally important: gh-aw does not replace the GitHub Actions trigger model
  but extends it. Practitioners with existing Actions knowledge can apply that knowledge
  directly; the gh-aw-specific additions are layered on top. The "cost control" framing
  (via `stop-after:`, `skip-if-match:`) is novel — it positions trigger configuration
  as a lever for managing LLM spend, not just workflow scheduling. For Ch03 (Workflow
  Orchestration): this page is the single authoritative source for trigger selection
  — pattern-specific notes (dispatch-ops, labelops, chatops) each document one trigger
  type, but this reference documents all 10 in one place. Cross-reference it as the
  complete trigger menu.

### Claim 2: Fuzzy scheduling scatters execution times to avoid load spikes — human-readable expressions like `daily around 14:00` produce ±1 hour randomization windows

- **Evidence**: The page documents the fuzzy scheduling system with specific scatter
  windows for each syntax form. `daily` delegates to the compiler for time assignment;
  `daily around 14:00` scatters within ±1 hour (13:00-15:00); `daily between 9:00
  and 17:00` scatters within the stated range; `weekly on friday around 5pm` scatters
  day + time; `every 10 minutes` has a minimum of 5 minutes. Fixed times use standard
  cron with optional timezone and UTC offset support.
- **Confidence**: settled (first-party reference; scatter window specifications are
  platform specifications)
- **Quote**: (no direct quote for the complete system; see Concrete Artifacts for the
  schedule syntax examples)
- **Our assessment**: Fuzzy scheduling is a platform-level solution to the "thundering
  herd" problem for scheduled agent workflows. In a repository with many similar
  workflows (e.g., daily dependency checks across multiple repos), using `daily` rather
  than `cron: "0 9 * * *"` prevents all instances from hitting GitHub APIs, LLM
  endpoints, and external services simultaneously. The `between` variant (e.g.,
  `daily between 9:00 and 17:00`) is the right choice when workflows must run during
  business hours but don't need a specific time. The minimum 5-minute interval for
  `every N minutes` is a rate-limit safeguard. For Ch04 (Automation Patterns): recommend
  fuzzy scheduling as the default for any scheduled workflow, reserving fixed cron
  times only when exact timing is required (e.g., triggering after a known external
  batch process completes at 03:00 UTC sharp). Cross-reference
  `docs-ghaw-fuzzy-schedule-specification.md` for the formal ABNF specification and
  compilation model.

### Claim 3: `label_command` automatically removes the label after activation for re-triggering semantics — distinct from `names:` label filtering which monitors persistent label state

- **Evidence**: The page states for `label_command`: "Fires when specific label
  applied, then automatically removes the label for re-triggering." The `remove_label:
  false` option preserves the label after activation. The page also documents `names:`
  filtering separately for labels that should remain after execution, making the
  command-vs-state distinction explicit at the YAML level.
- **Confidence**: settled (first-party reference; field-level behavior is
  authoritatively specified)
- **Quote**: "Fires when specific label applied, then automatically removes the label
  for re-triggering."
- **Our assessment**: The auto-removal design solves a key UX problem: if label
  application is a command signal (e.g., "run deployment"), the label must be removed
  after execution so the same command can be issued again by re-applying the label.
  Without auto-removal, a user would have to manually remove and re-apply the label
  each time — defeating the one-click trigger experience. The `remove_label: false`
  escape hatch enables the label as a persistent state signal pattern (e.g., "marked
  for X" that stays until explicitly cleared). This creates a clean conceptual split:
  `label_command` = transient command signal; `names:` filtering = persistent state
  monitoring. For Ch03 and Ch04: this distinction should be the primary design
  heuristic for label-driven workflow trigger selection. Corroborates
  `docs-ghaw-labelops.md`'s coverage of `label_command` mechanics.

### Claim 4: `workflow_run:` requires a non-empty `workflows:` list as a security measure and supports `conclusion:` filtering for downstream conditional execution

- **Evidence**: The page states for `workflow_run:`: "Requires: `workflows:` with
  non-empty entries (required for security)" and "Supports `conclusion:` filtering
  (success, failure, cancelled, skipped, timed_out, action_required, neutral, stale)."
  The security rationale is stated explicitly: the non-empty list requirement exists
  to prevent security risks from cross-repository and fork-triggered runs.
- **Confidence**: settled (first-party reference; the security requirement and
  conclusion values are specified)
- **Quote**: "Requires: `workflows:` with non-empty entries (required for security)"
- **Our assessment**: The security requirement on `workflows:` is not obvious from
  standard GitHub Actions documentation — the gh-aw reference makes it explicit that
  this field is required (not optional) for security reasons, not just for filtering.
  An empty `workflows:` list would allow any workflow run to trigger the downstream
  workflow, including from forks or untrusted sources. The `conclusion:` filtering
  enables sophisticated chaining patterns: e.g., a notification workflow that fires
  only on `failure`, or a cleanup workflow that fires on any terminal state. For Ch03:
  when documenting workflow chaining patterns, flag the `workflows:` security
  requirement prominently — it prevents a class of privilege-escalation attacks where
  an untrusted workflow run triggers a more-privileged downstream workflow.

### Claim 5: `on.steps:` pre-activation steps run deterministically before the agent and save one workflow job vs. a separate filter job — each step with an `id` auto-produces a `<id>_result` output

- **Evidence**: The page documents `on.steps:` as "Inject deterministic pre-activation
  steps that save one workflow job. Each step with `id` automatically generates
  `<id>_result` output (success/failure based on exit code)." The auto-wiring of
  step outputs to workflow gating via `needs.pre_activation.outputs.<id>_result` is
  shown explicitly.
- **Confidence**: settled (first-party reference; the auto-output generation mechanism
  is specified)
- **Quote**: "Inject deterministic pre-activation steps that save one workflow job."
- **Our assessment**: The "saves one workflow job" claim is the key operational benefit:
  without `on.steps:`, conditional activation requires a separate filter job (with
  its own billing and latency). `on.steps:` collapses the filter into the pre-activation
  job that gh-aw already runs, reducing cost and latency for common conditional patterns
  (e.g., "only run this workflow if the issue has a specific label" checked via a grep).
  The auto-generated `<id>_result` output is the automatic integration with the
  workflow's `if:` condition — no manual output declaration needed for simple pass/fail
  filtering. For complex filter logic with explicit values, the note specifies using
  step output with manual re-exposure via `jobs.pre-activation.outputs`. For Ch02
  (Harness Engineering): `on.steps:` is the first-choice pattern for lightweight
  conditional activation; only escalate to a separate custom filter job (`jobs:`)
  when the filter requires heavy tooling (checkout, compiled tools, multiple runners).

### Claim 6: Search query filtering (`skip-if-match:`/`skip-if-no-match:`) enables org-wide state-based conditional activation — workflows can be skipped or gated on live GitHub search results

- **Evidence**: The page documents two search query filter options: `skip-if-match:`
  (skip if search query has matches, default `max: 1`) and `skip-if-no-match:` (skip
  if search query has fewer than minimum matches, default `min: 1`). Both support
  standard GitHub search qualifiers. Setting `scope: none` enables org-wide searches:
  `skip-if-no-match: { query: "org:myorg label:ops:in-progress is:issue is:open",
  scope: none }`.
- **Confidence**: settled (first-party reference; field names and behavior are
  specified)
- **Quote**: `skip-if-no-match: { query: "org:myorg label:ops:in-progress is:issue is:open", scope: none }`
- **Our assessment**: Search query filtering is the gh-aw mechanism for global state
  awareness at the trigger layer. A workflow that should not fire when another instance
  is already running can use `skip-if-match: { query: "label:ops:in-progress is:issue" }`
  to check for the in-progress signal before activation. This moves idempotency logic
  from within the workflow to the activation decision itself — much cheaper than running
  an agent to check state. The `scope: none` org-wide search is significant: it enables
  singleton-style patterns where only one instance of a workflow runs across an entire
  GitHub organization. For Ch04 (Automation Patterns): document search query filtering
  as the cost-control primitive for avoiding redundant agent runs — it consumes a
  GitHub search API call rather than an LLM invocation.

### Claim 7: The `forks:` field on PR triggers provides fine-grained fork access control — from `["*"]` (all forks) to specific org or repo patterns

- **Evidence**: The page documents the `forks:` field with three documented values:
  `["*"]` (allow all forks), `["owner/*"]` (allow forks from specific organization),
  `["owner/repo"]` (allow specific repository). Omitting the field defaults to
  same-repository-only behavior.
- **Confidence**: settled (first-party reference; field values are specified)
- **Quote**: (no direct prose quote; see Concrete Artifacts for the fork filter values)
- **Our assessment**: The default omit-means-same-repo behavior is the safe default for
  public repositories — forks cannot trigger PR-based workflows without explicit
  allowlisting. The `["owner/*"]` pattern is designed for organizations running monorepo
  forks or trusted partner forks. The `["*"]` pattern enables fully open contribution
  flows where fork PRs can trigger agentic workflows (e.g., automated dependency checks
  or code quality reviews on fork contributions). For Ch03 (Workflow Orchestration) and
  security-conscious deployments: the `forks:` field is the PR-specific complement to
  `workflow_dispatch`'s inherent fork protection (documented in
  `docs-ghaw-dispatch-ops.md` Claim 6). PR triggers require explicit configuration;
  dispatch triggers are fork-safe by design.

### Claim 8: `repository_dispatch` allows external systems to trigger workflows via authenticated API POST with arbitrary `client_payload` data accessible as `${{ github.event.client_payload.field }}`

- **Evidence**: The page documents `repository_dispatch` as: "External systems trigger
  workflows via authenticated API POST to `/repos/<owner>/<repo>/dispatches`. Accepts
  `event_type` and `client_payload` fields. Access payload data using
  `${{ github.event.client_payload.field }}`."
- **Confidence**: settled (first-party reference; API endpoint and payload access
  syntax are specified)
- **Quote**: "External systems trigger workflows via authenticated API POST to
  `/repos/<owner>/<repo>/dispatches`."
- **Our assessment**: `repository_dispatch` is the bridge between gh-aw and external
  systems (CI/CD pipelines, monitoring services, deployment tools). Unlike
  `workflow_dispatch` (human-triggered via UI or CLI), `repository_dispatch` is
  designed for machine-to-machine invocation. The `client_payload` mechanism allows
  arbitrary structured data to flow from the external system into the workflow — for
  example, a monitoring alert that includes severity level, affected service, and
  incident ID. For Ch03 (Workflow Orchestration): `repository_dispatch` is the
  integration trigger for non-GitHub systems that need to initiate agentic workflows.
  It is the gh-aw equivalent of a webhook receiver, but with GitHub authentication
  as the security model.

### Claim 9: `stop-after:` disables workflow triggering after a deadline calculated from compilation time — minimum granularity is hours, not minutes

- **Evidence**: The page documents `stop-after:` as: "Disable triggering after
  deadline: `'+25h'`, `'+7d'`, `'2025-12-31'`. Calculated from compilation time;
  minimum granularity is hours."
- **Confidence**: settled (first-party reference; field behavior and granularity
  are specified)
- **Quote**: "Calculated from compilation time; minimum granularity is hours."
- **Our assessment**: `stop-after:` is the cost-control mechanism for time-limited
  agent workflows — for example, a PR review workflow that should stop triggering
  24 hours after the PR is opened, or an experiment workflow that should expire
  after 7 days. The compilation-time calculation is important: `+25h` means 25 hours
  after the workflow was last compiled (deployed), not 25 hours after the first trigger.
  Teams must re-compile to reset the deadline. The hourly minimum granularity means
  this is not suitable for short-lived workflows (minutes-scale). For Ch04 (Automation
  Patterns): recommend `stop-after:` as a budget guardrail for any workflow with
  unbounded event-driven triggers (e.g., comment-driven agents on long-lived PRs or
  issues that could receive hundreds of triggering events).

### Claim 10: Comment-based triggers cover three distinct comment types and note that `issue_comment` fires for both issue and PR comments

- **Evidence**: The page documents three comment trigger types: `issue_comment:`,
  `pull_request_review_comment:`, and `discussion_comment:`. A notable edge: "Note:
  `issue_comment` events also fire for PR comments." Issue comment locking is available
  via `lock-for-agent: true`.
- **Confidence**: settled (first-party reference; this is a known GitHub Actions
  behavior documented here explicitly)
- **Quote**: "`issue_comment` events also fire for PR comments."
- **Our assessment**: The `issue_comment` fires-for-PR-comments behavior is a known
  GitHub Actions footgun. A workflow designed to handle issue comments that uses
  `issue_comment:` as its trigger will also fire on PR comments — potentially triggering
  issue-specific logic in a PR context. The reference documents this explicitly, which
  means gh-aw practitioners are expected to be aware of it and handle it (e.g., via
  `if:` conditions that check `github.event.issue.pull_request` to distinguish issue
  comments from PR comments). The `lock-for-agent: true` option for `issue_comment`
  prevents concurrent workflow runs from simultaneously modifying the same issue thread.
  For Ch03: flag the `issue_comment` / PR-comment overlap as a design consideration
  when building comment-triggered workflows.

### Claim 11: `on.needs:` and `on.permissions:` extend the pre-activation job to support secret-manager workflows and additional token scopes before agent execution

- **Evidence**: The page documents `on.needs:` as: "Add custom jobs that both
  pre_activation and activation depend on. Useful for secret-manager workflows
  providing app credentials." And `on.permissions:` as: "Grant additional token
  scopes to pre-activation job" listing 11 named scopes (actions, checks, contents,
  deployments, discussions, issues, packages, pages, pull-requests,
  repository-projects, security-events, statuses).
- **Confidence**: settled (first-party reference; field names and scope list are
  specified)
- **Quote**: "Useful for secret-manager workflows providing app credentials."
- **Our assessment**: `on.needs:` and `on.permissions:` together enable a pattern not
  covered by any existing corpus note: a pre-activation dependency that fetches
  credentials from a secret manager (e.g., HashiCorp Vault, AWS Secrets Manager) and
  makes them available to both the pre-activation job and the main activation job. This
  is more secure than embedding long-lived secrets in repository secrets: the
  pre-activation job requests short-lived credentials on demand. The 11-scope
  `on.permissions:` list matches the standard GitHub Actions token permission scopes,
  applied specifically to the pre-activation job. For Ch02 (Harness Engineering): this
  combination (`on.needs:` + `on.permissions:`) is the correct pattern for workflows
  that need dynamic credentials or elevated pre-activation permissions without granting
  those permissions to the main agent execution.

### Claim 12: Bot and author association filtering provides granular control over automated versus human actor workflows

- **Evidence**: The page documents four bot/actor filtering mechanisms: `bots:` (allow
  specific bot accounts like `dependabot[bot]`, `renovate[bot]`), `skip-bots:` (exclude
  specific bots like `github-actions`, `copilot`), `skip-author-associations:` (skip by
  GitHub author association: first_time_contributor, contributor, none), with
  per-trigger-type granularity for `skip-author-associations:`. The matching note:
  "Flexible matching handles bot names with/without `[bot]` suffix."
- **Confidence**: settled (first-party reference; field names and association values
  are specified)
- **Quote**: "Flexible matching handles bot names with/without `[bot]` suffix."
- **Our assessment**: The combination of `bots:` and `skip-bots:` creates an allow/deny
  model for automated actors, while `skip-author-associations:` provides trust-level
  filtering for human actors. The per-trigger-type granularity of `skip-author-associations:`
  (e.g., skip `first_time_contributor` for `issue_comment` but not for `pull_request_review_comment`) enables nuanced policies: for example, allow first-time
  contributors to open issues (triggering IssueOps) but not post comments (protecting
  against spam). For Ch04 (Automation Patterns): document bot/actor filtering as the
  trust boundary mechanism for comment-driven workflows in public repositories — the
  platform provides the filtering primitives, but teams must configure them explicitly
  for their trust model.

## Concrete Artifacts

### Fuzzy Schedule Syntax Forms

```
# Human-friendly fuzzy scheduling (from "Scheduled Triggers" section):
daily                               # Compiler assigns scattered time
daily around 14:00                  # Scattered within ±1 hour (13:00-15:00)
daily between 9:00 and 17:00        # Scattered within range
weekly on friday around 5pm         # Day + time with scatter
every 10 minutes                    # Minimum 5 minutes

# UTC offset support:
daily around 3pm utc-5

# Fixed cron with optional timezone:
cron: "30 9 * * 1-5"
timezone: "America/New_York"
```

### Fork Filtering for PR Triggers

```yaml
# From "Pull Request Triggers" section:
on:
  pull_request:
    forks:
      - "*"               # Allow all forks
      # or:
      - "owner/*"         # Allow forks from specific organization
      # or:
      - "owner/repo"      # Allow specific repository
# Omit forks: field for same-repository-only (default)
```

### Pre-Activation Steps (`on.steps:`) with Auto-Generated Outputs

```yaml
# From "Custom Steps Filtering" section:
on:
  issues:
    types: [opened]
  steps:
    - id: check
      run: echo "$LABELS" | grep -q '"bug"'

# Generated output: needs.pre_activation.outputs.check_result == 'success'
# Use in workflow if: condition:
if: needs.pre_activation.outputs.check_result == 'success'
```

### Search Query Conditional Activation

```yaml
# Skip if search has matches (default max: 1):
skip-if-match:
  query: "label:ops:in-progress is:issue is:open"

# Skip if search has fewer than minimum matches (default min: 1):
skip-if-no-match:
  query: "org:myorg label:ops:in-progress is:issue is:open"
  scope: none   # org-wide search (not scoped to current repo)
```

### Label Name Filtering (`names:`)

```yaml
# From "Label Filtering" section:
on:
  issues:
    types: [labeled, unlabeled]
    names: [bug, critical, security]

# Shorthand form:
# on: issue labeled bug, enhancement
```

### Role and Bot Filtering

```yaml
# From "Repository Access Role Filtering" and "Bot Filtering" sections:

# Allow specific roles (default: [admin, maintainer, write]):
roles: [admin, maintainer, write, triage, read, all]

# Skip specific roles:
skip-roles: [read]

# Allow specific bots:
bots: [dependabot[bot], renovate[bot]]

# Skip specific bots:
skip-bots: [github-actions, copilot]
```

### Author Association Filtering

```yaml
# From "Author Association Filtering" section:
skip-author-associations:
  issue_comment: contributor
  pull_request_review_comment: [first_time_contributor, none]
```

### `stop-after:` Deadline Configuration

```yaml
# From "Stop After Configuration" section:
# Relative duration from compilation time:
stop-after: "+25h"    # 25 hours
stop-after: "+7d"     # 7 days

# Absolute date:
stop-after: "2025-12-31"

# Minimum granularity: hours (not minutes)
```

### Pre-Activation Dependencies and Permissions

```yaml
# From "Pre-Activation Dependencies" and "Pre-Activation Permissions" sections:
on:
  issues:
    types: [opened]
  needs: [fetch-credentials]    # Custom job both pre_activation and activation depend on
  permissions:
    issues: write
    pull-requests: read
    # Available scopes: actions, checks, contents, deployments, discussions,
    # issues, packages, pages, pull-requests, repository-projects,
    # security-events, statuses
```

### Reactions and Status Comments Configuration

```yaml
# From "Reactions" and "Status Comments" sections:
reaction: "+1"          # Emoji on trigger: +1, -1, laugh, confused, heart, hooray, rocket, eyes
reaction: none          # Disable reaction

# Selective status comment targeting:
status-comment:
  issues: true
  pull-requests: false
  discussions: false
```

### Trigger Shorthand Examples

```yaml
# Natural-language shorthands (auto-include workflow_dispatch):
on: push to main
on: push tags v*
on: pull_request merged
on: pull_request affecting src/**
on: issue opened
on: issue labeled bug
on: discussion created
on: manual                          # workflow_dispatch only
on: workflow completed ci-test
on: comment created
on: dependabot pull request
on: api dispatch custom-event
on: "deployment failed"
```

### `slash_command` Centralized Strategy

```yaml
# From "Command Triggers" section:
on:
  slash_command:
    events: [issues, issue_comment]   # Restrict to specific contexts
    strategy: centralized             # Route via generated central trigger
```

### Activation Token Configuration

```yaml
# GitHub App token minting (from "Activation Token Configuration" section):
github-app:
  client-id: ${{ vars.APP_CLIENT_ID }}
  private-key: ${{ secrets.APP_PRIVATE_KEY }}
```

## Cross-References

- **Corroborates**:
  - `docs-ghaw-dispatch-ops.md` Claims 1–9: The triggers reference confirms and
    unifies what dispatch-ops documents in depth — `workflow_dispatch` typed inputs
    (Claim 2 in dispatch-ops), fork protection (Claim 6), `roles:` and `bots:` security
    model (Claim 5), and `manual-approval:` environment gates (Claim 7). The triggers
    reference is the master catalog; dispatch-ops is the practitioner guide for the
    `workflow_dispatch` trigger specifically.
  - `docs-ghaw-labelops.md`: The triggers reference confirms `label_command` auto-removal
    behavior and the `names:` filtering distinction (Claim 3 here). LabelOps provides
    the pattern-level guidance; this reference provides the canonical field specification.
  - `docs-ghaw-chatops.md`: The triggers reference confirms `slash_command` event
    restriction and the `strategy: centralized` option. ChatOps documents the design
    pattern; this reference documents the trigger configuration API.
  - `docs-ghaw-concurrency-reference.md` Claim 2 (trigger-type concurrency groups):
    The concurrency reference documents how each trigger type gets a different default
    concurrency group. This triggers reference documents what each trigger type *is* —
    the two are complementary: triggers reference = "what fires when"; concurrency
    reference = "how concurrent runs of that trigger are managed."
  - `docs-ghaw-fuzzy-schedule-specification.md`: That source provides the formal ABNF
    specification and FNV-1a hash-based scattering model; this triggers reference
    documents the human-readable syntax forms that compile to that specification
    (Claim 2 here). Together they describe the complete schedule system: syntax
    (this reference) + compilation model (fuzzy-schedule-specification).

- **Extends**:
  - `docs-ghaw-orchestration-patterns.md` Claim 5 (compile-time validation for
    dispatch targets): The triggers reference establishes that `workflow_run:` requires
    a non-empty `workflows:` list for security (Claim 4 here). Both claims are
    instances of the same compile-time/activation-time validation principle —
    orchestration patterns applies it to `dispatch-workflow`/`call-workflow` targets;
    the triggers reference applies it to `workflow_run:` security.
  - `docs-ghaw-permissions-reference.md` (read permissions model): The triggers
    reference's `on.permissions:` field (Claim 11 here) extends the main permissions
    model by showing that the pre-activation job can receive additional scopes
    independent of the main agent job. The permissions reference covers the full
    `permissions:` frontmatter section; this claim covers a pre-activation-specific
    subset.
  - `docs-ghaw-issueops.md`: The triggers reference documents `lock-for-agent: true`
    for `issues:` and `issue_comment:` triggers (Claim 10 here), which prevents
    concurrent modification during workflow execution. IssueOps documents the
    pattern; this reference provides the locking mechanism.

- **Contradicts**: None identified. All trigger behavior described in pattern-specific
  notes (dispatch-ops, labelops, chatops, issueops) is consistent with the unified
  reference documentation here. No existing source note makes claims about gh-aw
  trigger configuration that this reference opposes. No contradiction issue required.

- **Novel** (what this note adds that no prior source covers):
  - **`workflow_run:` trigger with `conclusion:` filtering and security requirement**
    (Claim 4): No prior corpus note documents this trigger type or its non-empty
    `workflows:` security requirement.
  - **`on.steps:` pre-activation cost saving and auto-output mechanism** (Claim 5):
    The "saves one workflow job" cost benefit and the `<id>_result` auto-generation
    are not documented in any existing source note.
  - **Search query conditional activation** (`skip-if-match:`, `skip-if-no-match:`)
    (Claim 6): No prior note documents these search query filtering mechanisms or the
    org-wide `scope: none` pattern.
  - **`stop-after:` deadline configuration** (Claim 9): The compilation-time deadline
    mechanism and hourly granularity minimum are new to the corpus.
  - **`on.needs:` + `on.permissions:` pre-activation extension** (Claim 11): The
    secret-manager dependency pattern and per-scope pre-activation permissions are
    not documented in any existing note.
  - **`repository_dispatch` with `client_payload` access** (Claim 8): No prior note
    documents this external integration trigger type.
  - **`forks:` PR trigger field** (Claim 7): The three fork filter patterns
    (`["*"]`, `["owner/*"]`, `["owner/repo"]`) are new to the corpus.
  - **Author association filtering** (Claim 12): The `skip-author-associations:`
    field and per-trigger-type granularity are new to the corpus.
  - **Trigger shorthands catalog**: The complete list of natural-language shorthand
    forms (Concrete Artifacts) is not documented in any existing source note.

## Guide Impact

### Chapter 03: Workflow Orchestration

- **Add triggers reference as the master trigger type menu** (Claim 1): Ch03 should
  cite this reference as the authoritative catalog of all 10 trigger types. Pattern-
  specific notes (dispatch-ops, labelops, chatops, issueops) provide design guidance;
  this reference provides the complete configuration API. A decision tree for trigger
  selection should link here.

- **Add `workflow_run:` with non-empty `workflows:` security requirement** (Claim 4):
  Document as the workflow chaining trigger, with the security constraint prominently:
  empty `workflows:` list is a security vulnerability, not just a misconfiguration.
  The `conclusion:` filtering enables conditional downstream chaining (fire only on
  failure, fire on any terminal state, etc.).

- **Add `forks:` PR trigger field** (Claim 7): When documenting PR-triggered
  agentic workflows for public repositories, the `forks:` field controls the trust
  boundary. Default (omit) = same-repo only; `["*"]` = all forks permitted.
  Cross-reference `docs-ghaw-dispatch-ops.md` Claim 6 (dispatch triggers are fork-safe
  by design; PR triggers require explicit configuration).

### Chapter 04: Automation Patterns

- **Add search query filtering as the cost-control activation primitive** (Claim 6):
  For automation workflows that might fire redundantly (e.g., when another instance
  is already running), `skip-if-match:` with a GitHub search query is the cheapest
  idempotency check — one API call vs. one LLM invocation. Document alongside
  `stop-after:` as budget guardrails for event-driven workflows.

- **Add `stop-after:` for time-bounded automation** (Claim 9): PRs, issues, and
  other long-lived GitHub entities can generate unbounded triggering events over
  their lifetime. `stop-after:` is the platform mechanism to cap agent exposure.
  Note: deadline is calculated from compilation time, not first trigger.

- **Add label-as-command vs. label-as-state design distinction** (Claim 3):
  `label_command` (auto-remove) = command signal; `names:` filtering (label persists)
  = state signal. This is a fundamental design decision for any label-driven automation
  pattern. Cross-reference `docs-ghaw-labelops.md` for full pattern guidance.

- **Add author association filtering for public repo safety** (Claim 12):
  `skip-author-associations:` is the trust-level mechanism for comment-driven
  workflows in public repositories. Recommended default for comment triggers:
  skip `first_time_contributor` and `none` until trust is established.

### Chapter 02: Harness Engineering

- **Add `on.steps:` as the lightweight conditional activation pattern** (Claim 5):
  For simple state checks before activation (label presence, file existence), `on.steps:`
  is cheaper than a separate filter job — same pre-activation slot, no extra billing.
  Escalate to `jobs:` filtering only when the check requires checkout, compiled tools,
  or multiple runners.

- **Add `on.needs:` + `on.permissions:` for credential-fetching pre-activation**
  (Claim 11): The pattern for dynamic credentials is: `on.needs:` → custom credential-
  fetching job → `on.permissions:` grants the pre-activation job the scopes needed to
  consume those credentials. This is more secure than long-lived repository secrets
  for sensitive workflows.

## Extraction Notes

1. **Source is the unified reference for a fragmented topic**: Trigger configuration
   is documented in multiple pattern-specific notes (dispatch-ops, labelops, chatops,
   issueops) plus this reference. The reference page is the authoritative master; the
   pattern pages are practitioner guides. Both are needed — this note focuses on what
   the reference adds beyond what the pattern notes already cover.

2. **Fuzzy scheduling cross-reference**: The `docs-ghaw-fuzzy-schedule-specification.md`
   note covers the formal specification for fuzzy scheduling. This reference covers the
   syntax forms; that specification covers the compilation model. Claims here about
   scatter windows are from the triggers reference; the formal ABNF and FNV-1a hash
   behavior belong to the specification note.

3. **Verbatim quote caution**: Source content was fetched via WebFetch, which processes
   HTML through an AI model. Technical strings (field names, YAML keys, specific values
   like reaction names and scope lists) are quoted as returned; they are unlikely to
   have been altered in processing. Prose passages that lack a clear direct quote are
   marked "(no direct quote; see paraphrase in Our assessment)."

4. **No publication date**: The page does not carry an explicit publication date.
   `date_published` is left null, consistent with other gh-aw reference pages.

5. **No contradictions filed**: All trigger behaviors are consistent with claims in
   existing pattern-specific source notes. The reference provides the canonical
   specification that pattern notes are consistent with — no opposing claims found.

6. **`slash_command` shorthand**: The page documents `on: "label-command deploy"` as
   shorthand for `label_command`. The shorthand generates `issues`, `pull_request`, and
   `discussion` events plus `workflow_dispatch` for testing — a useful detail for
   practitioners using the shorthand without understanding its expansion.
