---
source_url: https://github.github.com/gh-aw/reference/faq
source_type: docs
title: "GitHub Agentic Workflows: Reference FAQ"
author: GitHub Agentic Workflows team (GitHub Next / Microsoft Research)
date_published: null
date_extracted: 2026-05-25
last_checked: 2026-05-25
status: current
confidence_overall: emerging
issue: "#393"
---

# GitHub Agentic Workflows: Reference FAQ

> The official practitioner-facing FAQ for GitHub Agentic Workflows — answers
> the most common mental-model questions about the platform's additive design,
> capability boundaries, guardrail implementation, and cost structure, providing
> concise Q&A framing not found in the architectural reference or configuration
> guides.

## Source Context

- **Type**: docs (official GitHub Agentic Workflows `reference/faq` page — in
  the "Reference" section alongside the sandbox, network, and permissions
  references. The FAQ format makes it distinct from the architectural or
  configuration reference pages: it addresses practitioner concerns rather than
  specifying platform internals.)
- **Author credibility**: First-party from GitHub Next / Microsoft Research —
  the same team behind Peli de Halleux's agent factory blog series and the
  `gh aw` CLI. Answers to capability questions, guardrail descriptions, and
  supported-engine lists are authoritative for the platform. Cost-per-run
  figures are approximations, not contractual SLAs.
- **Scope**: Practitioner mental-model questions across five domains —
  Determinism, Capabilities, Guardrails, Configuration & Setup, Workflow
  Design, and Costs & Usage. Does NOT cover: detailed configuration field
  schemas (see `docs-ghaw-sandbox-reference.md`, `docs-ghaw-network-reference.md`,
  `docs-ghaw-permissions-reference.md`), the compilation model in depth
  (`docs-ghaw-how-they-work.md`), or the Safe Outputs specification
  (`docs-ghaw-safe-outputs-specification.md`). The FAQ is the "what can it do
  and why is it safe" document; the reference pages are the "how to configure it"
  documents.

## Extracted Claims

### Claim 1: Agentic workflows are "100% additive" — the existing deterministic CI/CD pipeline is unchanged and agentic workflows form a separate automation layer

- **Evidence**: The Determinism FAQ section directly addresses the most common
  architectural concern: "Agentic workflows are **100% additive** — your
  deterministic build, test, and release pipelines stay unchanged." The platform
  is explicitly framed as a supplement to CI/CD, not a replacement.
- **Confidence**: settled (first-party documentation; describes the platform's
  architectural design principle)
- **Quote**: "Agentic workflows are **100% additive** — your deterministic build,
  test, and release pipelines stay unchanged."
- **Our assessment**: The "100% additive" claim is the FAQ's most important
  framing for practitioners hesitant about adopting the platform. It explicitly
  separates agentic workflows from CI/CD, positioning them as a "Continuous AI"
  layer (per `docs-ghaw-how-they-work.md` Claim 8) that runs alongside the
  deterministic build pipeline rather than replacing it. For Ch01 (Daily
  Workflows): this framing directly addresses team adoption friction — the pitch
  is "this doesn't touch your releases" rather than "replace your pipelines."
  For Ch02 (Harness Engineering): the additive design means agentic workflows
  can be introduced incrementally, with no changes to existing `.yml` workflows.

### Claim 2: The agent step's read-only default prevents secret access by the agent; only specific MCP tool steps — not the agent itself — can access configured secrets

- **Evidence**: The "Secrets Access" FAQ entry: "Not by default — the AI agent
  runs with read-only permissions. Some MCP tools may be configured with secrets,
  but those are accessible only to the specific tool steps, not the agent itself."
  This establishes a data-isolation boundary between the agent's context and the
  secrets accessible to tool steps.
- **Confidence**: settled (first-party documentation; describes a platform
  security guarantee)
- **Quote**: "Not by default — the AI agent runs with read-only permissions.
  Some MCP tools may be configured with secrets, but those are accessible only
  to the specific tool steps, not the agent itself."
- **Our assessment**: The secrets-isolation claim is more specific than the
  general "no write access by default" principle. It says that even when MCP
  tools are configured with secrets, those secrets do not flow into the agent's
  context — the agent calls a tool, the tool uses its secret, and the result is
  returned to the agent. This limits prompt injection attack surface: a malicious
  prompt cannot cause the agent to exfiltrate secrets by reading them from the
  environment. For Ch03 (Safety and Verification): this is a concrete safety
  boundary to document — secrets are scoped to tool steps, not the agent's
  reasoning context. Practitioners building custom MCP servers should note that
  the `ANTHROPIC_API_KEY` or similar credentials set in the workflow are handled
  in the step environment, not surfaced to the AI in plain text.

### Claim 3: Safe output sanitization applies seven specific transforms before changes reach GitHub state: secret redaction, URL domain filtering, XML escaping, size limits, control character stripping, GitHub reference escaping, and HTTPS enforcement

- **Evidence**: The "Sanitization" FAQ entry: "All safe outputs are sanitized
  before being applied: secret redaction, URL domain filtering, XML escaping,
  size limits, control character stripping, GitHub reference escaping, and HTTPS
  enforcement."
- **Confidence**: settled (first-party documentation; describes the platform's
  output sanitization pipeline)
- **Quote**: "All safe outputs are sanitized before being applied: secret
  redaction, URL domain filtering, XML escaping, size limits, control character
  stripping, GitHub reference escaping, and HTTPS enforcement."
- **Our assessment**: This is the most specific sanitization inventory in the
  corpus. "GitHub reference escaping" is notable — it prevents the agent's
  output from inadvertently (or maliciously) creating cross-references to
  arbitrary issues or PRs. "URL domain filtering" corresponds to the network
  allowlist (Layer 4 in `docs-ghaw-how-they-work.md` Claim 3). "Secret
  redaction" closes the exfiltration path if a prompt injection trick causes the
  agent to include a secret in its output. For Ch03: cite this list when
  documenting the Safe Outputs sanitization guarantee. The seven transforms
  together implement the output sanitization layer (Layer 5 of the five-layer
  pipeline) in a concrete, auditable way.

### Claim 4: The FAQ frames the platform's guardrails as a four-layer defense model — read-only agent, safe outputs with separate scoped-token jobs, threat detection blocking prompt injection and malicious patches, and network allowlist

- **Evidence**: The "Constraints" FAQ entry: "gh-aw uses defense-in-depth with
  four layers: read-only agent by default, safe outputs for all writes, threat
  detection, and network allowlist." Each layer is described: (1) read-only agent
  by default; (2) safe outputs with "separate jobs and scoped write tokens"; (3)
  threat detection "before writes blocking prompt injection/secrets/malicious
  patches"; (4) "network allowlist blocking outbound traffic except to explicitly
  allowed domains."
- **Confidence**: settled (first-party documentation; practitioner-facing
  description of the security model)
- **Quote**: "gh-aw uses defense-in-depth with four layers: read-only agent by
  default, safe outputs for all writes, threat detection, and network allowlist."
- **Our assessment**: The FAQ's four-layer framing differs from the architectural
  five-layer model in `docs-ghaw-how-they-work.md` Claim 3 (which lists:
  compilation-time validation, runtime isolation, permission separation, network
  controls, output sanitization). The FAQ groups permission separation and Safe
  Outputs together and omits compilation-time validation and runtime isolation as
  separate layers, while adding threat detection explicitly. This is a different
  categorization scheme — the FAQ is describing operational guardrails from a
  practitioner perspective, while the how-they-work page describes the security
  pipeline architecture. Neither contradicts the other; they describe the same
  system at different levels of abstraction. For Ch03: both framings are
  useful — the architectural five-layer model for technical depth, the four-layer
  operational model for team communication and onboarding.

### Claim 5: External human approval for safe outputs is implemented via GitHub Environment protection rules applied to a custom safe output job — not a separate gh-aw mechanism

- **Evidence**: The "External Approval" FAQ entry: "Yes. Apply GitHub Environment
  protection rules to a custom safe output job." This routes the approval
  through the standard GitHub Actions environment approval gate.
- **Confidence**: settled (first-party; describes a specific configuration
  mechanism)
- **Quote**: "Apply GitHub Environment protection rules to a custom safe output job."
- **Our assessment**: The implementation detail matters: human approval in gh-aw
  is not a custom gh-aw feature but a composition of the existing GitHub Actions
  environment protection mechanism with a custom safe output job. This means
  practitioners familiar with environment protection rules from CI/CD deployments
  already understand the approval mechanism. For Ch03: when recommending human
  approval gates, specify that the mechanism is GitHub Environment protection
  rules on a custom safe output job — not just "configure human approval." This
  directs practitioners to the correct documentation.

### Claim 6: Integrity filtering controls which GitHub content the agent sees by filtering by author trust and merge status, with the MCP gateway removing below-threshold content before the agent sees it

- **Evidence**: The "Integrity Filtering" FAQ entry: "Controls which GitHub
  content the agent sees, filtering by author trust and merge status. The MCP
  gateway removes content below the configured threshold before the agent sees it."
- **Confidence**: emerging (the FAQ describes the mechanism; detailed configuration
  is in the dedicated integrity reference page)
- **Quote**: "Controls which GitHub content the agent sees, filtering by author
  trust and merge status. The MCP gateway removes content below the configured
  threshold before the agent sees it."
- **Our assessment**: Integrity filtering operates as a pre-filter on agent inputs
  — before the AI reasons about GitHub content (issue bodies, PR descriptions,
  comments), the MCP gateway strips content from untrusted or unmerged sources.
  This is input-side sanitization complementing the output-side sanitization in
  Claim 3 — together they form a bidirectional safety layer. The "author trust
  and merge status" criteria suggest the filter is designed to prevent prompt
  injection via malicious issue comments or PR descriptions from external
  contributors. For Ch03: document integrity filtering as the input-side
  complement to Safe Output sanitization. Reference the dedicated integrity
  reference page (see `docs-ghaw-integrity-reference.md`) for configuration
  details.

### Claim 7: The markdown body (AI instructions) can be edited on GitHub.com and takes effect on the next run without recompiling; only the YAML frontmatter or structural changes require recompilation

- **Evidence**: The "Editing on GitHub.com" FAQ entry: "Yes, for the markdown
  body (AI instructions) — loaded at runtime, takes effect on the next run."
  The implicit corollary is that changes to the compiled structure (frontmatter,
  tool allowlists, triggers) require recompilation.
- **Confidence**: settled (first-party documentation; describes the compilation
  model's runtime loading behavior)
- **Quote**: "Yes, for the markdown body (AI instructions) — loaded at runtime,
  takes effect on the next run."
- **Our assessment**: This runtime-loading characteristic has important
  implications for the harness design model. The YAML frontmatter (constraints,
  tools, triggers) is compiled and pinned in the `.lock.yml`; the markdown body
  (instructions) is loaded fresh at every run. This means the AI's instructions
  can be updated without going through the compile → commit → CI cycle, but the
  security envelope (what tools the agent can call, what permissions it has)
  remains anchored to the compiled artifact. For Ch02 (Harness Engineering):
  this is a useful design property to document — fast iteration on instructions
  (edit the `.md` directly) vs. deliberate change management for capabilities
  (requires recompile). For Ch03: the compiled security envelope is immutable
  without recompilation, which is a positive property — a quick markdown edit
  cannot accidentally expand the agent's permissions.

### Claim 8: Any external system that can make an HTTP request can trigger an agentic workflow via `repository_dispatch`, with runtime parameters available in the agent's context

- **Evidence**: The "External System Trigger" FAQ entry: "Any system that can
  make an HTTP request — Jira, PagerDuty, Slack, custom APIs — can trigger a
  workflow via the `repository_dispatch` API." The Workflow Design section adds
  that the agent has the triggering content (e.g., a Jira issue body) in context,
  so "no extra integration is needed."
- **Confidence**: settled (first-party documentation; `repository_dispatch` is
  a standard GitHub Actions feature; the FAQ confirms agentic workflows use the
  same API)
- **Quote**: "Any system that can make an HTTP request — Jira, PagerDuty, Slack,
  custom APIs — can trigger a workflow via the `repository_dispatch` API."
- **Our assessment**: The `repository_dispatch` trigger is the standard GitHub
  Actions mechanism for external system integration; the FAQ confirms it works
  for agentic workflows without modification. This is significant because it means
  any existing webhook-capable system (issue trackers, incident management, Slack
  bots) can dispatch agentic workflows without a custom integration layer. For
  Ch01 (Daily Workflows): document `repository_dispatch` as the standard trigger
  for external-system-driven agentic automation. Teams using Jira, PagerDuty, or
  similar tools can connect them to agentic workflows via standard webhooks.

### Claim 9: TrialOps provides isolated testing of agentic workflows in trial repositories, preventing any real issues, PRs, or comments from being created during testing

- **Evidence**: The "Testing Without Side Effects" FAQ entry: "Use TrialOps to
  run workflows in isolated trial repositories without creating real issues, PRs,
  or comments."
- **Confidence**: settled (first-party documentation; TrialOps is referenced
  elsewhere in the platform documentation)
- **Quote**: "Use TrialOps to run workflows in isolated trial repositories without
  creating real issues, PRs, or comments."
- **Our assessment**: TrialOps is the platform's answer to the "how do I test
  without side effects" question — a fundamental concern when the agent can
  create PRs, post comments, and apply labels. An isolated trial repository
  provides a safe sandbox for testing workflow behavior before enabling in
  production. For Ch02 (Harness Engineering): TrialOps should be recommended as
  the standard pre-production testing environment for any workflow that produces
  Safe Outputs. The alternative (testing directly in a production repository with
  limited permissions) is more error-prone and riskier. Reference the dedicated
  TrialOps documentation (`docs-ghaw-trial-ops.md`) for setup instructions.

### Claim 10: gh-aw has no automatic retries — each trigger produces exactly one run, and retry cost accumulation is not a concern

- **Evidence**: The "Retries and Costs" FAQ entry: "gh-aw has no automatic
  retries — each trigger produces exactly one run."
- **Confidence**: settled (first-party documentation; describes a platform design
  decision)
- **Quote**: "gh-aw has no automatic retries — each trigger produces exactly one
  run."
- **Our assessment**: The no-retry policy is a deliberate design choice that
  simplifies cost reasoning. Unlike some AI pipeline frameworks that implement
  automatic retry on failure (potentially multiplying cost by 2-5x on flaky
  tasks), gh-aw produces exactly one run per trigger. This is consistent with
  the deterministic CI/CD framing — CI/CD pipelines also don't automatically
  retry on logic failures; retries are explicit and deliberate. For Ch02
  (Harness Engineering): document the no-retry policy when discussing cost
  management. Teams building on gh-aw should not expect automatic recovery from
  transient failures; if retry logic is needed, it must be implemented via a
  re-trigger mechanism (e.g., a separate workflow responding to a failure event).

### Claim 11: The Claude engine requires `ANTHROPIC_API_KEY` as a GitHub Actions secret and does not support `CLAUDE_CODE_OAUTH_TOKEN`

- **Evidence**: The "CLAUDE_CODE_OAUTH_TOKEN" FAQ entry: "No. The Claude engine
  only supports `ANTHROPIC_API_KEY` as a GitHub Actions secret."
- **Confidence**: settled (first-party documentation; specific API key
  requirement for the Claude engine)
- **Quote**: "No. The Claude engine only supports `ANTHROPIC_API_KEY` as a
  GitHub Actions secret."
- **Our assessment**: This is a practitioner gotcha worth documenting. Users
  familiar with Claude Code's `CLAUDE_CODE_OAUTH_TOKEN` (the OAuth flow for
  personal use) might assume it works in gh-aw agentic workflows; it does not.
  Only the API key (`ANTHROPIC_API_KEY`) is supported. For Ch02: include this
  in any "Getting Started with Claude Engine" documentation. The `ANTHROPIC_API_KEY`
  should be set as a repository or organization secret following standard GitHub
  Actions secret management practices.

### Claim 12: macOS runners are not supported because agentic workflows require container jobs for the Agent Workflow Firewall sandbox, which macOS runners do not support

- **Evidence**: The "macOS Runners" FAQ entry: "macOS runners (`macos-*`) don't
  support container jobs, which agentic workflows require for the Agent Workflow
  Firewall sandbox."
- **Confidence**: settled (first-party documentation; this is a GitHub
  infrastructure constraint, not a gh-aw design choice)
- **Quote**: "macOS runners (`macos-*`) don't support container jobs, which
  agentic workflows require for the Agent Workflow Firewall sandbox."
- **Our assessment**: The macOS limitation follows directly from the AWF
  sandbox design: the Agent Workflow Firewall runs as a Docker container process,
  which requires container job support. GitHub-hosted macOS runners use a
  different virtualization stack that does not support Docker container jobs.
  This is a hard constraint — teams with macOS-specific workflows cannot use
  gh-aw natively. For Ch02: document Linux-only as a hard constraint. Teams with
  macOS-specific build steps should run those steps in a separate standard
  GitHub Actions job and pass outputs to the agentic job.

### Claim 13: PRs created by agentic workflows using the default `GITHUB_TOKEN` do not trigger pull_request CI workflows — a deliberate GitHub Actions security feature

- **Evidence**: The "CI Checks Not Triggered" FAQ entry explains: "PRs created
  with the default `GITHUB_TOKEN` don't trigger `pull_request` workflows — a
  GitHub Actions security feature." This is presented as a platform constraint,
  not a bug.
- **Confidence**: settled (this is a documented GitHub Actions security
  constraint; the FAQ confirms it applies equally to agentic workflows)
- **Quote**: "PRs created with the default `GITHUB_TOKEN` don't trigger
  `pull_request` workflows — a GitHub Actions security feature."
- **Our assessment**: This constraint has practical implications for any gh-aw
  workflow that creates PRs and expects CI to run automatically. Teams relying
  on CI checks to validate AI-generated code changes will need to use a non-
  default token (PAT or GitHub App token) or manually trigger CI. For Ch03
  (Safety and Verification): this is a critical caveat — if the validation
  strategy depends on CI checks running automatically on agent-created PRs,
  the default token will silently break that assumption. Recommend documenting
  that agentic workflows creating PRs must use a PAT or App token if CI
  auto-run is required.

### Claim 14: GitHub Actions minutes are charged for every agentic workflow run in addition to AI inference costs; Copilot CLI typically consumes 1-2 premium requests per run

- **Evidence**: The "Costs" FAQ section: "Yes — every run consumes Actions
  minutes (free for public repos, metered for private) alongside AI inference."
  Copilot CLI: "Copilot CLI typically uses 1-2 premium requests per run."
- **Confidence**: emerging (costs described as "typical" — actual costs vary by
  workflow complexity, model selection, and execution time)
- **Quote**: "Yes — every run consumes Actions minutes (free for public repos,
  metered for private) alongside AI inference."
- **Our assessment**: The dual-cost model (Actions minutes + AI inference) is
  important for budget planning. A workflow that triggers frequently on `push`
  events could accumulate both Actions minutes and AI inference costs rapidly.
  The 1-2 premium request estimate for Copilot CLI is useful as a baseline but
  should be validated against specific workflow complexity. For Ch01 (Daily
  Workflows): when recommending high-frequency event triggers (e.g., `on: push`
  on every commit), note that both cost dimensions scale with trigger frequency.
  Teams should use the fuzzy schedule trigger for lower-frequency tasks and
  scoped event filters for push/PR triggers to control cost.

## Concrete Artifacts

### Four-Layer Defense Model (FAQ Framing)

```
Defense-in-depth layers (practitioner perspective from the FAQ):

Layer 1: Read-only agent by default
  → AI agent step runs with no write permissions

Layer 2: Safe outputs with separate scoped-token jobs
  → Writes require explicit safe output declarations
  → Write operations execute in separate jobs with scoped write tokens
  → Sanitized before application (see sanitization list below)

Layer 3: Threat detection before writes
  → Runs before safe output jobs apply changes
  → Blocks: prompt injection, secrets in output, malicious patches

Layer 4: Network allowlist
  → Agent Workflow Firewall blocks outbound by default
  → Only explicitly declared domains are reachable
```

*Source: docs-ghaw-faq "How are agent actions constrained?" answer*

### Safe Output Sanitization Transforms (Complete List)

```
All safe outputs are sanitized before being applied:
  1. Secret redaction             — removes secrets from output content
  2. URL domain filtering         — restricts URLs to allowed domains
  3. XML escaping                 — prevents XML/HTML injection
  4. Size limits                  — caps output length
  5. Control character stripping  — removes non-printable control chars
  6. GitHub reference escaping    — prevents unintended issue/PR cross-references
  7. HTTPS enforcement            — rewrites HTTP to HTTPS
```

*Source: docs-ghaw-faq "What sanitization is done on AI outputs before applying changes?" answer*

### Secrets Access Isolation Model

```
Agent context:          NO access to secrets
                        (reads repository content, tool outputs only)

MCP tool step:          CAN be configured with secrets
                        (secret is accessible in the tool step's environment)

Data flow:
  Secret → MCP Tool Step → Tool Output → Agent Context
                    ↑                        ↑
                 secret here              no secret here
                 (tool step env)          (only tool result)
```

*Source: docs-ghaw-faq "Can they access my repository secrets?" answer*

### Supported AI Engines (as of extraction date)

```
Supported engines:
  - GitHub Copilot (default, uses Copilot CLI)
  - Claude by Anthropic (requires ANTHROPIC_API_KEY; NOT CLAUDE_CODE_OAUTH_TOKEN)
  - Codex
  - Gemini by Google
  - Crush

Auth requirements:
  - Copilot CLI: Personal Access Token with 'Copilot Requests' permission
  - Claude: ANTHROPIC_API_KEY as GitHub Actions secret
```

*Source: docs-ghaw-faq "Configuration & Setup" section*

### External System Integration via repository_dispatch

```
Trigger pattern:
  External system (Jira, PagerDuty, Slack, custom API)
    → HTTP POST to GitHub repository_dispatch API
      → Agentic workflow receives event payload
        → Agent has triggering content in context (no extra integration needed)

Trigger type in workflow frontmatter:
  on:
    repository_dispatch:
      types: [jira-issue-created]
```

*Source: docs-ghaw-faq "Can I trigger an agentic workflow from an external system?" answer*

### Lock File Contents (FAQ Summary)

```
.lock.yml (compiled artifact from gh aw compile) contains:
  - SHA-pinned action references
  - Resolved imports (embedded at compile time for GHES compatibility)
  - Permissions declarations
  - Guardrail hardening

GHES compatibility: set `inlined-imports: true` on the platform workflow (callee)
  to embed imports at compile time instead of resolving them at runtime
```

*Source: docs-ghaw-faq "What is a workflow lock file?" and "GHES compatibility" answers*

## Cross-References

- **Corroborates**:
  - `docs-ghaw-how-they-work.md` Claim 4 (no write access by default): The FAQ
    Claim 2 ("agent runs with read-only permissions") and Claim 4 (read-only as
    Layer 1 of defense) independently restate the same design principle from the
    architectural documentation, confirming it from the practitioner-facing FAQ
    perspective.
  - `docs-ghaw-how-they-work.md` Claim 5 (Safe Outputs as pre-approved actions):
    FAQ Claim 4 (safe outputs as Layer 2 of defense, with separate scoped-token
    jobs) corroborates the architectural description of the Safe Outputs mechanism.
    The FAQ adds the specific detail that write operations execute in separate jobs
    with scoped write tokens.
  - `docs-ghaw-threat-detection.md` Claim 1 (threat detection as dedicated
    pipeline stage between agentic job and safe output execution): FAQ Claim 4
    (threat detection as Layer 3, blocking "prompt injection/secrets/malicious
    patches" before writes) corroborates the threat detection pipeline position.
    The FAQ adds the three specific threat categories blocked.
  - `docs-ghaw-sandbox-reference.md` Claim 2 (AWF as the default coding agent
    sandbox providing network egress control): FAQ Claim 12 (macOS not supported
    because container jobs required for AWF sandbox) corroborates that AWF is
    container-based and depends on GitHub Actions container job support.
  - `docs-ghaw-network-reference.md` Claim 1 (network defaults to infrastructure
    only, blocks undeclared domains): FAQ Claim 4 (Layer 4: "network allowlist
    blocking outbound traffic except to explicitly allowed domains") corroborates
    the default-deny network policy from the practitioner perspective.

- **Extends**:
  - `docs-ghaw-how-they-work.md` Claim 3 (five-layer defense-in-depth
    architecture): The FAQ's four-layer operational framing (Claim 4) is a
    complementary description of the same security system. The FAQ is not a
    contradiction — it uses a different categorization scheme aimed at
    practitioners rather than architects. Together, both framings are useful:
    the five-layer model for technical depth, the four-layer model for team
    communication.
  - `docs-ghaw-how-they-work.md` Claim 7 (compilation model, `.md` → `.lock.yml`):
    FAQ Claim 7 extends this by adding the runtime-loading behavior of the
    markdown body — the instructions are loaded fresh at each run, not compiled
    into the lock file. This is the first source in the corpus to document this
    distinction explicitly.
  - `docs-ghaw-mcps.md` Claim 1 (read-only MCP policy stated but not
    protocol-enforced): FAQ Claim 2 extends the MCP secrets picture — even when
    tools are configured with secrets, those secrets are scoped to the tool step
    environment, not surfaced to the AI agent. This adds a second isolation
    boundary at the agent context level, beyond the read-only tool behavior.

- **Contradicts**: None identified. The four-layer defense framing in the FAQ
  differs structurally from the five-layer architectural model in
  `docs-ghaw-how-they-work.md`, but both describe the same security system at
  different abstraction levels — this is a categorization difference, not a
  material conflict. No contradiction issue filed.

- **Novel** (findings not in any existing source note):
  - **Secret isolation at the agent-context boundary** (Claim 2): The specific
    claim that secrets configured in MCP tool steps are not surfaced to the AI
    agent's reasoning context is new to the corpus. Prior notes document "no
    write access by default" and "read-only MCP policy" but not the agent-level
    secret isolation boundary.
  - **Safe output sanitization as an enumerated seven-transform list** (Claim 3):
    The specific list of seven sanitization operations (secret redaction, URL
    domain filtering, XML escaping, size limits, control character stripping,
    GitHub reference escaping, HTTPS enforcement) is not documented in any
    existing source note.
  - **Integrity filtering via MCP gateway** (Claim 6): The claim that the MCP
    gateway pre-filters agent inputs by author trust and merge status is new to
    the corpus. The dedicated integrity reference (`docs-ghaw-integrity-reference.md`)
    has been filed, but the FAQ provides the concise framing for this mechanism.
  - **Runtime markdown loading without recompile** (Claim 7): The behavior that
    the markdown body is loaded at runtime (not compiled into the lock file) is
    new to the corpus. Prior notes document the compilation model for the
    frontmatter but do not specify the runtime-loading behavior of the markdown
    body.
  - **TrialOps for isolated testing** (Claim 9): The FAQ is the first source in
    the corpus to describe TrialOps as the recommended testing mechanism. The
    dedicated TrialOps documentation (`docs-ghaw-trial-ops.md`) exists but
    the FAQ's concise framing is useful for Ch02.
  - **No automatic retries** (Claim 10): The claim that each trigger produces
    exactly one run (no automatic retries) is new to the corpus.
  - **CI checks not triggered on default-token PRs** (Claim 13): The GitHub
    Actions security constraint that prevents CI from auto-triggering on PRs
    created with `GITHUB_TOKEN` is new to the corpus in the context of agentic
    workflows. This is a critical operational gotcha.
  - **`ANTHROPIC_API_KEY` requirement for Claude engine** (Claim 11): The
    explicit statement that `CLAUDE_CODE_OAUTH_TOKEN` is not supported (only
    `ANTHROPIC_API_KEY`) is new to the corpus.

## Guide Impact

### Chapter 01: Daily Workflows

- **"100% additive" framing for adoption** (Claim 1): Add this framing to the
  guide's pitch for agentic workflows. Teams can adopt gh-aw without touching
  their existing CI/CD pipelines — the entry point is a new `.md` workflow file,
  not a modification to existing `.yml` workflows. This removes the principal
  adoption blocker ("what if it breaks our releases?").

- **External system triggering via `repository_dispatch`** (Claim 8): Document
  `repository_dispatch` as the standard integration mechanism for connecting
  external systems (Jira, PagerDuty, Slack, custom APIs) to agentic workflows.
  Teams with existing issue trackers can connect them without custom integration
  code — just a webhook POST.

- **Dual cost model** (Claim 14): When recommending trigger frequency, note that
  both Actions minutes and AI inference costs scale with trigger frequency. Fuzzy
  schedule triggers and scoped event filters are the recommended cost controls.

### Chapter 02: Harness Engineering

- **Runtime markdown loading vs. compiled frontmatter** (Claim 7): Document the
  distinction between the markdown body (loaded at runtime — fast iteration) and
  the frontmatter (compiled into the lock file — requires recompile for changes).
  This is the correct mental model for the `.md` → `.lock.yml` compilation model.

- **TrialOps as standard pre-production testing** (Claim 9): Recommend TrialOps
  as the standard testing environment for any workflow that produces Safe Outputs.
  Reference `docs-ghaw-trial-ops.md` for setup instructions.

- **No automatic retries** (Claim 10): Document the no-retry policy when
  discussing fault tolerance. Teams that need retry logic must implement it via
  re-trigger (e.g., a separate monitoring workflow that re-dispatches failed runs).

- **Claude engine auth** (Claim 11): Document `ANTHROPIC_API_KEY` (not
  `CLAUDE_CODE_OAUTH_TOKEN`) as the required secret for the Claude engine. Pair
  with standard GitHub Actions secret management guidance.

- **Linux-only constraint** (Claim 12): Document as a hard constraint. Teams with
  macOS-specific build steps should isolate them in a separate standard Actions
  job and pass results to the agentic job.

### Chapter 03: Safety and Verification

- **Secret isolation boundary** (Claim 2): Add to the safety model: secrets
  are scoped to MCP tool step environments and do not flow into the agent's
  reasoning context. This limits prompt injection attack surface.

- **Seven-transform sanitization list** (Claim 3): Cite this list as the concrete
  Safe Output sanitization guarantee. "GitHub reference escaping" is particularly
  notable — it prevents agent output from creating unintended cross-repository
  references.

- **Human approval via Environment protection rules** (Claim 5): Specify the
  mechanism precisely: GitHub Environment protection rules on a custom safe output
  job. This directs practitioners to the correct GitHub Actions documentation.

- **Integrity filtering as input-side safety** (Claim 6): Document as the
  input-side complement to output sanitization. The MCP gateway filters agent
  inputs by author trust and merge status; Safe Output sanitization processes
  agent outputs. Together they form a bidirectional safety layer.

- **CI not triggered on default-token PRs** (Claim 13): Document as a critical
  caveat. If CI validation of agent-created PRs is part of the safety strategy,
  a PAT or GitHub App token is required for PR creation.

- **Four-layer operational model** (Claim 4): The FAQ's framing is useful for
  team communication — simpler than the architectural five-layer model and
  focused on "what can the agent do that might be dangerous?" rather than the
  full security pipeline.

## Extraction Notes

1. **Source format**: The FAQ is structured as Q&A sections under five headings
   (Determinism, Capabilities, Guardrails, Configuration & Setup, Workflow Design,
   Costs & Usage). Questions were extracted across multiple WebFetch passes to
   maximize coverage. The rendering is an Astro/Starlight SPA; WebFetch returns
   summarized AI-processed text, not raw HTML. Verbatim quotes were extracted
   from targeted fetches of specific sections.

2. **Question count**: The page contains approximately 50 FAQ questions. The 14
   claims extracted here prioritize novel findings not covered in existing source
   notes. Questions that simply restate content already documented in
   `docs-ghaw-how-they-work.md`, `docs-ghaw-mcps.md`, or other reference pages
   were noted but not re-extracted.

3. **No publication date**: The documentation page does not carry an explicit
   publication date. `date_published` is left null.

4. **Prior Miner PR**: A prior Miner PR (#645) for this issue was closed without
   merge. This extraction is a fresh pass from the source.

5. **No contradictions filed**: The four-layer FAQ framing and the five-layer
   architectural framing describe the same security system at different abstraction
   levels. After review of all existing source notes, no material contradiction
   was identified that would lead to different guide advice.
