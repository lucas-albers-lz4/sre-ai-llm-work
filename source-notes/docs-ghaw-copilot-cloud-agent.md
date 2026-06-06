---
source_url: https://github.github.com/gh-aw/reference/copilot-cloud-agent
source_type: docs
title: "GitHub Agentic Workflows: Copilot Cloud Agent Reference"
author: GitHub Agentic Workflows team (GitHub Next / Microsoft Research)
date_published: null
date_extracted: 2026-06-06
last_checked: 2026-06-06
status: current
confidence_overall: emerging
issue: "#1082"
---

# GitHub Agentic Workflows: Copilot Cloud Agent Reference

> The single authoritative reference for both Copilot-invocation safe outputs on the
> gh-aw platform — documents `create-agent-session` (spawn new Copilot work autonomously)
> and `assign-to-agent` (route existing issues/PRs to Copilot) with shared authentication
> requirements; the primary novel contribution is `create-agent-session`, which enables
> workflows to fan out new agent tasks without human issue-creation as an intermediary step.

## Source Context

- **Type**: docs (official GitHub Agentic Workflows `reference/copilot-cloud-agent` page —
  in the "Reference" section alongside `reference/assign-to-copilot`,
  `reference/safe-outputs-specification`, and `reference/cross-repository`. Reference pages
  document platform behavior and parameter schemas precisely, not conceptual overviews or
  patterns-section implementation guides. This page is the authoritative combined reference
  for the two Copilot-invocation safe output types.)
- **Author credibility**: First-party from the GitHub Agentic Workflows team (GitHub Next /
  Microsoft Research — the same team behind Peli de Halleux's "Agent Factory" blog series
  and the `gh aw` CLI). Parameter defaults, authentication requirements, and cross-repository
  constraint claims are settled platform facts for the `gh aw` platform.
- **Scope**: The `create-agent-session` safe output (full parameter schema, autonomous-spawn
  semantics, cross-repository constraints including the no-wildcard restriction) and the
  `assign-to-agent` safe output (consolidated here alongside `create-agent-session`), plus
  shared authentication requirements (fine-grained PAT requirement, GitHub App token
  exclusion, `GH_AW_AGENT_TOKEN` magic secret). Does NOT cover: the general Safe Outputs
  architecture and security invariants (see `docs-ghaw-safe-outputs-specification.md`), the
  broader cross-repository parameter surface (`docs-ghaw-cross-repository-reference.md`),
  orchestration primitives (`docs-ghaw-orchestration-patterns.md`), or the detailed
  `assign-to-agent` parameter schema already documented in `docs-ghaw-assign-to-copilot.md`.

## Extracted Claims

### Claim 1: This page is the single reference for both Copilot-invocation safe outputs — `create-agent-session` for spawning new work and `assign-to-agent` for routing existing issues or PRs

- **Evidence**: The page's introductory statement explicitly scopes it to both types.
- **Confidence**: settled (first-party reference documentation; this is the normative scope
  statement for the page)
- **Quote**: "This page covers two safe outputs for invoking the GitHub Copilot cloud agent
  from workflows"
- **Our assessment**: The consolidation of both Copilot-invocation safe outputs on a single
  reference page is architecturally deliberate — authentication requirements are shared
  (both require a fine-grained PAT) and the two types address complementary scenarios in the
  same domain (Copilot task dispatch). Practitioners choosing between the two should consult
  this page as the decision point. The existing `docs-ghaw-assign-to-copilot.md` covers the
  `/reference/assign-to-copilot` page (a separate reference URL); this page is a distinct
  consolidated reference. For Ch04 (Agent Patterns): document both safe output types together
  in the "Copilot dispatch" section so practitioners see the full surface in one place.

### Claim 2: `create-agent-session` enables a workflow to autonomously spawn follow-up Copilot work — it creates a new GitHub issue that triggers Copilot to implement the described task and open a pull request

- **Evidence**: The page provides a direct definition of the safe output's behavior and the
  mechanism by which the agent session manifests in GitHub.
- **Confidence**: settled (first-party reference documentation; this is the canonical
  definition of the operation type)
- **Quote**: "Creates a new Copilot coding agent session from workflow output, allowing a
  workflow to spawn follow-up work autonomously."
- **Our assessment**: `create-agent-session` closes a gap in the existing gh-aw Copilot
  dispatch surface: before this safe output, a workflow that wanted to dispatch new Copilot
  work had to either (a) create an issue via `create-issue` with `assignees: copilot`, or
  (b) use `assign-to-agent` on a pre-existing issue. `create-agent-session` provides a
  direct "spawn new session" primitive that skips the issue-creation step — the agent session
  appears as a GitHub issue internally, but the workflow declares the task directly. This
  is the mechanism that enables true workflow-initiated multi-agent fan-out: an orchestrator
  workflow can spawn N Copilot sessions in parallel, each working on a different sub-task,
  without the orchestrator needing to first create N GitHub issues and then assign each.
  For Ch04: document `create-agent-session` as the fan-out primitive for Copilot sub-agents
  in orchestrated workflows, positioned alongside `dispatch-workflow` and `call-workflow`
  from `docs-ghaw-orchestration-patterns.md` as the three fan-out mechanisms on gh-aw.

### Claim 3: The `create-agent-session` safe output is configured with a `base` branch, a `max` concurrent sessions cap, and optional cross-repository targeting via `target-repo` and `allowed-repos`

- **Evidence**: The page documents the parameter schema. The `base` parameter specifies
  "base branch for agent session PR" with a default of `"main"`. The `max` parameter
  specifies "max sessions (default: 1, maximum: 10)". `target-repo` and `allowed-repos`
  enable cross-repository session creation.
- **Confidence**: settled (parameter names and defaults stated in first-party reference
  documentation)
- **Quote**: `max: 1` with the comment "max sessions (default: 1, maximum: 10)"
- **Our assessment**: The `max` cap of 10 is the platform's guardrail against unbounded
  Copilot session spawning — unlike `assign-to-agent` which also defaults to `max: 1`
  (`docs-ghaw-assign-to-copilot.md` Claim 5), the explicit platform maximum of 10 for
  `create-agent-session` suggests this type is designed for modest fan-out scenarios, not
  bulk session creation. The `base` parameter is the session-creation analog to the
  `base-branch` parameter in `assign-to-agent` (`docs-ghaw-assign-to-copilot.md` Claim 10)
  — in both cases, the workflow author controls which branch the Copilot-generated PR
  targets. For Ch04: document the `max: 10` ceiling as an architectural constraint when
  designing orchestrators that use `create-agent-session` for fan-out — workflows requiring
  more than 10 parallel Copilot sessions must be redesigned (e.g., sequential batching or
  a queue-based WorkQueueOps approach).

### Claim 4: `create-agent-session` does not support wildcard repository targeting (`target-repo: "*"`) — explicit repository names must be provided via `target-repo` or `allowed-repos`

- **Evidence**: The page explicitly documents the restriction on dynamic targeting.
- **Confidence**: settled (first-party documentation; the exclusion is stated directly)
- **Quote**: "create-agent-session supports target-repo and allowed-repos for cross-repository
  use but does not support target-repo: '*' — use an explicit owner/repo value or
  allowed-repos instead."
- **Our assessment**: This restriction means that orchestrators cannot dynamically select
  the repository in which to spawn a Copilot session — the target repository must be
  statically declared in the workflow YAML. This is a critical architectural constraint for
  dynamic multi-agent systems: if a workflow needs to spawn Copilot sessions in repos
  determined at runtime (e.g., based on which repos contain failing tests), it cannot use
  `target-repo: "*"` as a catch-all — it must enumerate the allowed repos via `allowed-repos`
  and have the agent output the specific target. This corroborates
  `docs-ghaw-cross-repository-reference.md` Claim 4, which documents the same exclusion
  within the broader cross-repository reference context. For Ch04: explicitly warn that
  `create-agent-session` requires static repo targeting — orchestrators that route to
  dynamically-selected repos must declare all possible targets in `allowed-repos` or use
  a different dispatch mechanism.

### Claim 5: Both `create-agent-session` and `assign-to-agent` require a fine-grained Personal Access Token (PAT); the default `GITHUB_TOKEN` is insufficient and GitHub App tokens are explicitly not supported

- **Evidence**: The page explicitly states this shared authentication requirement for both
  safe output types.
- **Confidence**: settled (stated directly in first-party reference documentation as an
  authentication requirement; GitHub App token exclusion explicitly called out)
- **Quote**: "Both safe outputs require a fine-grained PAT. The default GITHUB_TOKEN lacks
  the necessary permissions."
- **Quote**: "GitHub App tokens are not supported for Copilot assignment"
- **Our assessment**: The shared PAT requirement across both safe output types confirms that
  Copilot dispatch is a privileged operation on the gh-aw platform — it cannot be performed
  with the automatic credentials that most GitHub Actions workflows use. The GitHub App token
  exclusion is operationally significant: organizations that standardize on GitHub App tokens
  for workflow automation (a common enterprise pattern for credential management and
  auditability) must make an explicit exception for any workflow using Copilot-invocation safe
  outputs. This is the same constraint documented for `assign-to-agent` alone in
  `docs-ghaw-assign-to-copilot.md` Claim 7, now confirmed to apply equally to
  `create-agent-session`. For Ch05 (Team Adoption): document the PAT requirement as a
  deployment prerequisite with lead time implications — PAT provisioning may require GitHub
  organization admin coordination, particularly in enterprises with PAT governance policies.

### Claim 6: The `GH_AW_AGENT_TOKEN` magic secret provides a platform-recognized fallback for PAT authentication across both Copilot-invocation safe outputs, set via `gh aw secrets set`

- **Evidence**: The page documents the magic secret convention and the CLI command to
  configure it.
- **Confidence**: emerging (magic secret name and CLI command provided; exact wording
  confirmed across two independent fetches)
- **Quote**: "Alternatively, you can set the magic secret GH_AW_AGENT_TOKEN to a suitable PAT"
- **Our assessment**: The `GH_AW_AGENT_TOKEN` convention extends the pattern documented in
  `docs-ghaw-assign-to-copilot.md` Claim 8 — that note documented the secret for
  `assign-to-agent` alone. This reference page confirms it applies to both Copilot-invocation
  safe outputs. The naming convention (`GH_AW_*` prefix) is consistent with
  `GH_AW_GITHUB_MCP_SERVER_TOKEN` (documented in `docs-ghaw-multi-repo-ops.md` for
  cross-repo MCP reads) — there is a broader gh-aw pattern of magic secrets for elevated
  permissions beyond `GITHUB_TOKEN`. For Ch02 (Harness Engineering): document
  `GH_AW_AGENT_TOKEN` as the standard deployment pattern — configure it once at the
  repository or organization level and it satisfies the PAT requirement for all
  `create-agent-session` and `assign-to-agent` safe outputs in that scope.

### Claim 7: The two safe output types represent fundamentally different Copilot invocation modes: `create-agent-session` spawns new work; `assign-to-agent` routes existing work

- **Evidence**: The page defines both types and their distinct use cases.
- **Confidence**: settled (first-party definitions of both safe output types; the
  contrast between new-work and existing-work is the defining architectural distinction)
- **Quote**: `assign-to-agent` "Programmatically assigns the GitHub Copilot coding agent to
  existing issues or pull requests."
- **Our assessment**: The architectural distinction is fundamental to choosing between the two
  patterns. `create-agent-session` is the right choice when the workflow itself generates
  the work — e.g., an orchestrator that identifies failing tests, extracts N sub-tasks, and
  spawns N Copilot sessions to fix them. `assign-to-agent` is the right choice when the
  issue or PR already exists and the workflow is responsible only for routing it to Copilot
  — e.g., a label-triggered workflow that detects a `ready-for-copilot` label and dispatches
  the issue. This distinction maps directly to the `create-issue` + `assignees: copilot`
  vs. `assign-to-agent` two-pattern split documented in `docs-ghaw-assign-to-copilot.md`
  Claim 2, but `create-agent-session` adds a third option that bypasses the issue-creation
  step entirely. For Ch04: present all three Copilot dispatch options as a decision table
  (new issue needed → `create-issue` + `assignees: copilot`; existing issue → `assign-to-
  agent`; direct session spawn, no issue needed → `create-agent-session`).

## Concrete Artifacts

### `create-agent-session` Safe Output — Parameter Schema

```yaml
# create-agent-session safe output — parameter schema
# Source: github.github.com/gh-aw/reference/copilot-cloud-agent

safe-outputs:
  create-agent-session:
    base: "main"            # base branch for agent session PR (required)
    max: 1                  # max sessions (default: 1, maximum: 10)
    target-repo: null       # cross-repository target (explicit owner/repo; "*" not supported)
    allowed-repos: []       # additional allowed repositories for cross-repo sessions
    github-token: null      # fine-grained PAT (falls back to GH_AW_AGENT_TOKEN)
```

*Parameter names and defaults extracted from first-party reference documentation.
Verify against source URL before production use, as defaults may change.*

### Authentication Setup Command

```bash
# Register the PAT as the platform-recognized magic secret
# Source: github.github.com/gh-aw/reference/copilot-cloud-agent

gh aw secrets set GH_AW_AGENT_TOKEN --value "YOUR_AGENT_PAT"
```

*Required PAT permissions: Actions, Contents, Issues, and Pull requests (Write access).*

### Copilot Dispatch Decision Table

```
Scenario                                     | Safe output to use
---------------------------------------------|--------------------------------------------
Workflow creates a new issue for a task AND  | create-issue safe output with
immediately needs Copilot to work on it      | assignees: copilot (single atomic step)
                                             |
Existing issue already in GitHub; workflow   | assign-to-agent safe output
needs to route it to Copilot                 | (existing-issue assignment)
                                             |
Workflow generates work directly (no issue   | create-agent-session safe output
needed as an artifact); orchestrator wants   | (direct Copilot session spawn;
to spawn a Copilot coding session            | agent session appears as issue internally)

Authentication requirement for all Copilot invocation safe outputs:
  GITHUB_TOKEN:      ❌ Insufficient
  GitHub App token:  ❌ Not supported
  Fine-grained PAT:  ✅ Required
  Recommended:       Set GH_AW_AGENT_TOKEN at repo or org level
```

### Cross-Repository Constraint for `create-agent-session`

```
create-agent-session cross-repository support:
  target-repo: "org/specific-repo"  ✅ Supported — explicit repo name
  allowed-repos: ["org/repo1", ...]  ✅ Supported — additional allowed repos
  target-repo: "*"                   ❌ NOT supported — wildcard excluded

Contrast with other cross-repo safe outputs (create-issue, add-comment, etc.):
  target-repo: "*"                   ✅ Supported by most other types

Source: github.github.com/gh-aw/reference/copilot-cloud-agent
        Also: docs-ghaw-cross-repository-reference.md Claim 4
```

## Cross-References

- **Corroborates**:
  - `docs-ghaw-assign-to-copilot.md` Claims 7–8 (PAT authentication requirement and
    `GH_AW_AGENT_TOKEN` magic secret): The new source confirms that both requirements
    apply equally to `create-agent-session` — the PAT requirement and magic secret convention
    are shared across both Copilot-invocation safe output types. Claim 5 above extends Claim
    7 of the assign-to-copilot note from `assign-to-agent`-specific to platform-wide.
  - `docs-ghaw-cross-repository-reference.md` Claim 4 (five safe-output types excluded from
    wildcard `target-repo: "*"` including `create-agent-session`): The new source's direct
    statement of the `create-agent-session` wildcard exclusion (Claim 4 above) is corroborated
    by the cross-repository reference, which lists `create-agent-session` among the five
    excluded types from a different reference page angle.
  - `docs-ghaw-multi-repo-ops.md` Claim 1 (`target-repo` supported on `create-agent-session`
    among eight safe output types): The new source explicitly confirms `target-repo` and
    `allowed-repos` parameters on `create-agent-session`, consistent with the multi-repo ops
    safe-output support matrix.

- **Extends**:
  - `docs-ghaw-assign-to-copilot.md` (covers the `/reference/assign-to-copilot` page which
    documents `assign-to-agent` in detail): This new note covers the broader
    `/reference/copilot-cloud-agent` page that consolidates both Copilot-invocation types.
    The `assign-to-agent` coverage in this note is intentionally thin — the detailed schema
    for that safe output already lives in `docs-ghaw-assign-to-copilot.md`. The primary
    extension here is `create-agent-session` coverage and the shared-authentication
    confirmation.
  - `docs-ghaw-orchestration-patterns.md` (covers `dispatch-workflow` and `call-workflow`
    as the two orchestrator fan-out primitives): `create-agent-session` is the third fan-out
    option — it dispatches Copilot coding sessions rather than sub-workflows. Together,
    `dispatch-workflow` + `call-workflow` + `create-agent-session` form the complete
    fan-out surface for orchestrators on gh-aw.
  - `docs-ghaw-safe-outputs-specification.md` (Safe Outputs MCP Gateway Specification): The
    authentication model documented here (fine-grained PAT required, privilege separation)
    is an instance of the security invariant AR1 from the spec (Agents MUST execute without
    write permissions). `create-agent-session` follows the same Safe Outputs architecture
    as all other safe output types; this reference page documents its type-specific schema.

- **Contradicts**: None. The PAT authentication requirement and GitHub App token exclusion
  stated on this page are fully consistent with `docs-ghaw-assign-to-copilot.md` Claim 7.
  The `create-agent-session` wildcard exclusion is corroborated (not contradicted) by
  `docs-ghaw-cross-repository-reference.md` Claim 4. No contradiction issue filed.

- **Novel** (what this note adds to the corpus that no prior source covers):
  - **`create-agent-session` as a named safe output type with its own schema** (Claim 2–4):
    No prior corpus note dedicates coverage to `create-agent-session`. Prior notes mention it
    only in passing (as one item in lists of safe output types that support `target-repo`, or
    in the wildcard exclusion list). This is the first note to document its semantics, use
    case, and parameter schema.
  - **Direct workflow-to-Copilot session dispatch without an intermediate issue step**
    (Claim 2): The pattern of spawning a Copilot session directly from a workflow output
    (bypassing explicit issue creation as an artifact) is not documented in the corpus.
    Prior coverage of Copilot dispatch (`docs-ghaw-assign-to-copilot.md`, IssueOps patterns)
    always involves an issue as the coordination artifact. `create-agent-session` breaks this
    dependency.
  - **Three-option Copilot dispatch taxonomy** (Claim 7): The complete three-way decision
    structure (new issue → `create-issue` + `assignees: copilot`; existing issue →
    `assign-to-agent`; direct session spawn → `create-agent-session`) has not been assembled
    anywhere in the corpus. Individual options are covered separately; the decision table
    is new.
  - **`max: 10` ceiling on `create-agent-session`** (Claim 3): The platform maximum of 10
    concurrent sessions is not documented in any prior corpus note. This is an architectural
    constraint for fan-out orchestrators.
  - **PAT requirement confirmed shared across both Copilot-invocation safe outputs** (Claim 5):
    The existing `docs-ghaw-assign-to-copilot.md` documents the PAT requirement for
    `assign-to-agent` specifically. This note confirms the requirement is shared with
    `create-agent-session`, elevating it from a type-specific quirk to a platform-wide policy
    for all Copilot dispatch operations.

## Guide Impact

### Chapter 04: Agent Patterns / Orchestration

- **Add `create-agent-session` as the third Copilot dispatch option** (Claims 2, 7):
  The guide's coverage of Copilot dispatch currently documents two approaches
  (`create-issue` + `assignees: copilot` and `assign-to-agent`). `create-agent-session`
  adds a third option specifically for orchestrators that generate sub-tasks programmatically
  and want to dispatch them to Copilot without creating GitHub issues as artifacts.
  Present all three in a decision table keyed on whether an issue artifact is needed and
  whether the target issue pre-exists.

- **Document `create-agent-session` as the Copilot fan-out primitive for orchestrators**
  (Claim 2): Position `create-agent-session` alongside `dispatch-workflow` and `call-workflow`
  as the three fan-out mechanisms for gh-aw orchestrators. The distinction: `dispatch-workflow`
  and `call-workflow` fan out to sub-workflows; `create-agent-session` fans out to Copilot
  coding sessions. An orchestrator that identifies N sub-tasks can spawn N Copilot sessions
  via N `create-agent-session` safe outputs (up to the `max: 10` ceiling).

- **Document the `max: 10` fan-out ceiling as an architectural constraint** (Claim 3):
  Workflows requiring more than 10 parallel Copilot sessions must use a sequential batching
  pattern (multiple workflow runs) or queue-based WorkQueueOps dispatch. This ceiling shapes
  the design space for high-parallelism orchestrators.

- **Add cross-repository constraint for `create-agent-session`** (Claim 4): Orchestrators
  that route work to dynamically-selected repositories cannot use `create-agent-session`
  with `target-repo: "*"`. The architecture must either statically enumerate repos via
  `allowed-repos`, or use a different dispatch mechanism for dynamic targeting. This should
  be called out explicitly alongside the orchestration patterns so practitioners don't design
  a dynamic routing system and discover the constraint at deployment time.

### Chapter 02: Harness Engineering

- **Document `GH_AW_AGENT_TOKEN` as the deployment standard for all Copilot dispatch**
  (Claim 6): Set `GH_AW_AGENT_TOKEN` at the repository or organization level once, and all
  `create-agent-session` and `assign-to-agent` safe outputs in scope will use it without
  per-workflow `github-token` configuration. Include the CLI setup command in the
  deployment checklist: `gh aw secrets set GH_AW_AGENT_TOKEN --value "YOUR_AGENT_PAT"`.

- **Extend the PAT-requirement warning to cover `create-agent-session`** (Claim 5): The
  guide may currently call out the PAT requirement only in the context of `assign-to-agent`.
  This source confirms the requirement applies to all Copilot-invocation safe outputs.
  Update the harness configuration checklist to cover `create-agent-session` as well.

### Chapter 05: Team Adoption / Enterprise Governance

- **Flag the GitHub App token exclusion as an enterprise deployment blocker** (Claim 5):
  Organizations that standardize on GitHub App tokens for workflow automation must provision
  a fine-grained PAT as an explicit exception for Copilot dispatch workflows. Surface this
  dependency in the enterprise adoption section alongside PAT lifecycle management guidance
  (creation, scoping, rotation, secret storage).

## Extraction Notes

1. **Reference page with two safe output types**: The source covers both `create-agent-session`
   and `assign-to-agent`. This note focuses on `create-agent-session` (the novel contribution)
   and the shared authentication context. Detailed `assign-to-agent` schema coverage is
   intentionally deferred to `docs-ghaw-assign-to-copilot.md`.

2. **Verbatim quotes from WebFetch**: Three independent WebFetch calls were made. The
   WebFetch AI layer declined to reproduce the full page verbatim on copyright grounds.
   Four distinct verbatim quotes were obtained (used in Claims 1, 2, 4, 5, and 6) and
   confirmed across two or more independent fetches. All other claims are based on
   consistent summaries across multiple fetches and are marked with appropriate confidence
   levels. Parameter names and defaults are treated as settled given consistency across
   three fetch passes.

3. **`base` parameter default**: The first fetch summary reported `base: "main"` as the
   parameter comment "base branch for agent session PR". This is treated as the default
   but should be verified against the live source before citing in the guide, as defaults
   may change.

4. **No publication date**: The reference page does not carry an explicit publication date.
   `date_published` is left null. Content is consistent with gh-aw platform state as of
   2026-06-06.

5. **No contradiction filed**: Reviewed all existing source notes in the corpus. The
   PAT authentication requirement and wildcard exclusion are corroborated by existing notes.
   No existing note makes a materially opposing claim.
