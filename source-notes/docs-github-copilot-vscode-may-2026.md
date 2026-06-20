---
source_url: https://github.blog/changelog/2026-06-03-github-copilot-in-visual-studio-code-may-releases
source_type: docs
title: "GitHub Copilot in Visual Studio Code, May releases"
author: GitHub (official changelog)
date_published: 2026-06-03
date_extracted: 2026-06-06
last_checked: 2026-06-06
status: current
confidence_overall: settled
issue: "#1077"
---

# GitHub Copilot in Visual Studio Code, May Releases

> GitHub's May 2026 VS Code roundup (v1.120–v1.123) documents four clusters of new
> agentic capabilities: a dedicated Agents window surface for multi-project agent work;
> session persistence and cross-machine history via GitHub account sync and Chronicle;
> expanded BYOK reach including air-gapped environments; and terminal-level safety and
> efficiency improvements — including the first documented explicit guarantee that
> sensitive credentials are NOT shared with the LLM.

## Source Context

- **Type**: docs (GitHub official product changelog, June 3, 2026; covers VS Code releases
  v1.120 through v1.123 from May and early June 2026)
- **Author credibility**: GitHub engineering team announcing production features in VS Code
  Copilot. Authoritative for the existence of each feature, exact names of settings and
  commands, and behavioral descriptions. Not a credible source for: adoption metrics, how
  often features are used, whether specific quality improvements are user-validated, or how
  these features interact with third-party tools or plugins not mentioned.
- **Scope**: Roundup of all VS Code Copilot updates released in May 2026, organized into
  four clusters: Agents window, Language models and BYOK, Terminal safety and efficiency,
  and "Also new." Individual May feature announcements (e.g., May 18 remote control GA,
  May 20 auto model selection) have their own source notes; this roundup adds synthesis
  context and covers features not announced separately. Does NOT cover: CLI-specific
  features (see `docs-github-copilot-cli-rubber-duck-scheduling-voice.md`), CCA cloud
  agent features, or VS Code Insiders-only features.

## Extracted Claims

### Claim 1: The Agents window is now in Stable (preview) — a dedicated multi-project surface for agent-first work with faster navigation and change review

- **Evidence**: Official changelog describes the feature as landed in Stable. The description
  highlights its purpose as a structural UI shift: moving agent work to a first-class surface
  rather than embedding it in chat.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "Work agent-first across multiple projects with a dedicated surface for faster
  navigation and change review."
- **Our assessment**: The Agents window landing in Stable is an architectural milestone: GitHub
  is signaling that agent-first interaction patterns now warrant a top-level UI surface rather
  than living inside the chat panel. The "multiple projects" framing means practitioners can
  manage concurrent work across repositories from a single surface. For Ch02: the Agents window
  is the new primary harness interaction surface for VS Code — practitioners configuring agent
  workflows should treat it as the reference execution environment, not the Chat panel. For Ch04:
  the "faster navigation and change review" framing suggests the surface is designed for
  iterative review of agentic edits, not just task dispatch.

### Claim 2: Remote agents run on remote machines over SSH or Dev Tunnels, with sessions that continue even when the client disconnects

- **Evidence**: Official changelog describes this as a preview feature under the Agents window.
  The persistence-on-disconnect property distinguishes this from the May 18 remote control
  feature (which enables remote *monitoring* of local sessions).
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "Run sessions on remote machines over SSH or Dev Tunnels, with sessions continuing
  even when the client disconnects."
- **Our assessment**: This is architecturally distinct from the May 18 remote control GA
  (`docs-github-copilot-cli-remote-control-ga.md`): that feature runs the agent locally and
  monitors it remotely; this feature runs the agent on a *remote machine* and disconnects the
  local client entirely. For long-running tasks, running on a persistent remote machine removes
  the dependency on the developer's laptop staying alive. For Ch04: document two distinct
  patterns: (1) local agent with remote monitoring (remote control GA, issue #805); (2) remote
  agent execution with client disconnect tolerance (this feature). The second pattern is closer
  to CCA's cloud execution model but uses the developer's own remote machine.

### Claim 3: The Agent Host Protocol (AHP) is an open protocol for synchronizing agent session state across multiple clients

- **Evidence**: Official changelog announces "continued investment" in AHP — framing it as an
  ongoing open protocol effort, not a single feature release.
- **Confidence**: emerging (the existence and intent of AHP is stated in the official changelog;
  the specific protocol details, adoption by non-GitHub clients, and maturity level are not
  documented here)
- **Quote**: "Continued investment in an open protocol for synchronizing agent session state
  across multiple clients."
- **Our assessment**: AHP is the first documented open protocol from GitHub for cross-client
  agent session synchronization in this corpus. If adopted by other tool vendors, AHP could
  become the interoperability layer enabling a single agent session to be visible and steerable
  from VS Code, the CLI, mobile, and third-party clients simultaneously. The "open protocol"
  framing is significant: it signals GitHub is not trying to own this as a proprietary surface
  but establish an interoperability standard. For Ch02: track AHP as a potential successor to
  ad-hoc multi-client agent management patterns. The guide should note its current "continued
  investment" (pre-GA) status.

### Claim 4: Session preferences persist across new agent sessions — including agent harness and isolation mode choices

- **Evidence**: Official changelog describes this as a quality-of-life improvement reducing
  per-session reconfiguration friction.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "New sessions keep your recent choices, including agent harness and isolation mode."
- **Our assessment**: Harness and isolation mode persistence is operationally meaningful:
  practitioners who have configured a specific agent harness (e.g., a project-specific skill
  set or MCP configuration) no longer need to reselect it each session. Isolation mode
  persistence matters for practitioners who routinely run agents in sandbox isolation. For
  Ch02: when documenting VS Code agent harness configuration, note that harness selection
  persists by default — practitioners who switch harnesses frequently should be aware that
  their previous choice carries forward.

### Claim 5: Chat sessions now sync automatically to the user's GitHub account, providing a searchable history across machines and workspaces

- **Evidence**: Official changelog describes this as a new feature under Session sync, linked
  to GitHub account authentication.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "Chat sessions now sync automatically to your GitHub account, giving you a
  searchable history of your work across machines and workspaces."
- **Our assessment**: Session sync transforms agent history from an ephemeral, local artifact
  to a persistent, cross-machine record. For practitioners who work across multiple machines
  (desktop + laptop, or developer machines + CI agents), session sync means they can pick up
  agentic work sessions from any machine without context loss. The "searchable history" framing
  also implies retrospective review — practitioners can search past sessions to recall what an
  agent did, what decisions were made, and how issues were resolved. For Ch04: document session
  sync as a new form of AI work history that complements but does not replace git history —
  sessions capture the interactive process; git captures the output.

### Claim 6: Chronicle enables querying past sessions, generating standup reports, and getting personalized productivity tips via `/chronicle` commands

- **Evidence**: Official changelog describes Chronicle as a capability accessed via `/chronicle`
  commands within VS Code, building on the session sync history.
- **Confidence**: settled (product fact — feature name and commands stated in official changelog)
- **Quote**: "Use `/chronicle` commands to query past sessions, generate standup reports, and
  get personalized productivity tips."
- **Our assessment**: Chronicle is the first AI coding tool feature in this corpus that uses
  accumulated session history to produce *meta-work outputs* (standup reports, productivity
  insights) rather than direct code artifacts. This is a significant category expansion: the
  agent's work history becomes an input to work-process reflection. The standup report
  generation capability specifically is high-value for teams that do daily standups — instead
  of manually recalling "what did I do yesterday?", practitioners can generate a summary from
  their actual session history. For Ch04: document Chronicle as a productivity meta-tooling
  pattern — an agent that supervises other agents' sessions and synthesizes the record. For
  Ch07: standup report generation from session history has implications for AI work
  observability and team transparency about AI-assisted work.

### Claim 7: Multiple agent sessions can run concurrently side-by-side within the Agents window

- **Evidence**: Official changelog describes this as an explicit Agents window capability.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "Open more than one agent session at the same time in the Agents window."
- **Our assessment**: Concurrent sessions within a single IDE surface enables a workflow
  previously only documented for multi-agent orchestration frameworks: running parallel
  workstreams and comparing outputs without switching between windows. For Ch04: document
  side-by-side sessions as a first-class VS Code pattern for multi-agent workflows, particularly
  useful for: (1) running an implementation session and a review/test session in parallel, and
  (2) comparing two approaches to the same problem by running them concurrently.

### Claim 8: Air-gapped BYOK allows bring-your-own-key models to run in isolated environments without GitHub authentication

- **Evidence**: Official changelog describes this as a new capability under "Language models
  and BYOK" — extending the April 22 BYOK GA announcement.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "Bring-your-own-key models can run in isolated environments without GitHub
  authentication."
- **Our assessment**: This extends the April 22 BYOK announcement (`docs-github-copilot-byok-vscode.md`,
  Claim 7), which stated that local BYOK models "still require the Copilot service" and noted
  "You need to be online" — with a "currently" qualifier that implied future change. Air-gapped
  BYOK appears to be that change: BYOK model calls can now route directly to the API provider
  without going through GitHub's Copilot service. For enterprises operating in restricted network
  environments (where GitHub authentication traffic is not permitted but direct API calls to
  specific providers are), this removes a prior architectural barrier to BYOK adoption. For Ch02:
  update BYOK guidance to note air-gapped operation is now available for provider keys that can
  be reached from the network segment; the April "requires Copilot service" caveat no longer
  applies to all BYOK scenarios.

### Claim 9: Configurable utility models allow choosing which models handle titles, summaries, rename suggestions, commit messages, and intent detection separately from the main chat model

- **Evidence**: Official changelog describes this as a new BYOK/model configuration capability.
  The feature name "Configurable utility models" is explicit.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "Choose which models handle titles, summaries, rename suggestions, commit messages,
  and intent detection."
- **Our assessment**: This is the first documented multi-model configuration in any VS Code
  Copilot surface — separating "utility" model slots from the primary chat model. Prior model
  selection sources (auto model selection, BYOK) discussed a single active model for chat;
  this introduces a model routing topology where different low-stakes tasks (naming, summary,
  intent) can be delegated to cheaper or faster models independently of the main chat model.
  For Ch04 (cost management): configurable utility models enable a cost optimization strategy:
  route lightweight utility tasks (commit message generation, rename suggestions) to inexpensive
  models while reserving the primary chat model budget for substantive coding work. For Ch02:
  document this as a new configuration surface in the VS Code harness — teams should consider
  which utility tasks they want to optimize vs. default.

### Claim 10: Reasoning effort controls are configurable directly from the model picker to balance quality, latency, and cost

- **Evidence**: Official changelog describes reasoning effort controls under the language model
  configuration section.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "Configure thinking effort directly from the model picker to balance quality,
  latency, and cost."
- **Our assessment**: Reasoning effort controls make a previously hidden model parameter
  (thinking budget / chain-of-thought depth) accessible as a first-class slider in the VS Code
  UI. Practitioners who want fast responses for low-complexity tasks (lower reasoning effort)
  and deep analysis for complex tasks (higher reasoning effort) can now configure this without
  changing the underlying model. For Ch04: document reasoning effort as a cost/quality tuning
  knob complementary to model selection — the same model at lower reasoning effort may
  outperform a cheaper model at maximum effort for many tasks.

### Claim 11: Sensitive prompts — passwords, passphrases, PINs, and verification codes — are entered directly in the terminal and are not shared with the LLM

- **Evidence**: Official changelog describes this under "Terminal safety and efficiency" as a
  new protection for credential handling.
- **Confidence**: settled (product fact — stated in official changelog with explicit enumeration
  of credential types)
- **Quote**: "Passwords, passphrases, PINs, and verification codes are entered directly in the
  terminal and are not shared with the LLM."
- **Our assessment**: This is the first explicit, documented guarantee in the corpus that a
  specific AI coding tool intercepts terminal-captured credentials to prevent them from
  entering the LLM context. Prior terminal-in-agent discussions treat terminal output as
  uniformly captured by the model. This claim establishes a safety boundary that practitioners
  can rely on: agents operating in VS Code terminals will not see credentials entered in
  interactive prompts. For Ch02: document this as a VS Code security property when describing
  terminal-integrated agentic workflows — credentials in interactive terminal prompts are
  isolated from the LLM context. For Ch05 (enterprise governance): this addresses a common
  security concern about agents reading terminal sessions where authentication tokens or
  database passwords appear.

### Claim 12: Terminal command confirmations include AI-generated risk levels and short safety explanations (experimental)

- **Evidence**: Official changelog describes "Command risk assessment" as an experimental
  feature under Terminal safety.
- **Confidence**: emerging (feature exists; marked experimental, meaning behavior may change;
  effectiveness of risk assessment not validated in this source)
- **Quote**: "Terminal confirmations include AI-generated risk levels and short safety
  explanations."
- **Our assessment**: Command risk assessment introduces a meta-reasoning layer before command
  execution: the AI evaluates the command's risk before the user approves it. This is complementary
  to the human-approval gates documented across other agentic systems — instead of just "approve
  yes/no?", the practitioner sees an AI-generated risk analysis to inform their decision. For
  Ch04: when documenting permission/approval gate design, note that VS Code's experimental
  command risk assessment adds an AI-informed safety context layer to the confirmation UI — a
  pattern likely to become standard as agentic execution matures.

### Claim 13: The `VSCODE_AGENT` environment variable lets CLIs detect and adapt behavior for agent-initiated commands

- **Evidence**: Official changelog describes this under "Agent-aware terminal commands."
- **Confidence**: settled (product fact — environment variable name stated in official changelog)
- **Quote**: "The `VSCODE_AGENT` environment variable lets CLIs adapt behavior for
  agent-initiated commands."
- **Our assessment**: `VSCODE_AGENT` is a surface-detection primitive: any CLI tool invoked
  within a VS Code agent terminal session can check this variable to determine whether it is
  running in an agent context versus a human-interactive context. This enables CLIs to suppress
  interactive prompts, output machine-parseable formats, or avoid human-oriented progress bars
  when invoked by an agent — reducing the disambiguation work agents must do when tools behave
  differently under agent vs. human use. For Ch02: document `VSCODE_AGENT` as a harness
  configuration primitive that CLI tools can integrate to improve agent compatibility. Teams
  building custom CLI tools used by agents should check this variable to disable interactive
  modes automatically.

### Claim 14: Expanded terminal output compression covers more verbose output patterns from tests, builds, linters, Docker, and package managers to reduce model context consumption

- **Evidence**: Official changelog describes the expansion of output compression coverage
  under Terminal safety and efficiency.
- **Confidence**: settled (product fact — categories explicitly listed in official changelog)
- **Quote**: "More verbose output patterns from tests, builds, linters, Docker, and package
  managers are compressed before reaching the model."
- **Our assessment**: Context-window management via terminal output compression is now a
  production-level capability in VS Code Copilot — the tool actively manages what reaches the
  model rather than passing through all terminal output verbatim. The explicit enumeration of
  compressed output categories (tests, builds, linters, Docker, package managers) shows GitHub
  has built pattern-specific compression logic, not generic truncation. For Ch02: document
  terminal output compression as a harness-level context-management mechanism practitioners
  can rely on for standard build/test workflows — they do not need to manually truncate or
  filter verbose build outputs before they reach the model context.

### Claim 15: Sessions and Git flow now pull base branch updates before agent edits and refresh Git state automatically after commits and syncs

- **Evidence**: Official changelog describes this under "Sessions and Git flow improvements"
  as multiple operational improvements.
- **Confidence**: settled (product fact — stated in official changelog)
- **Quote**: "New sessions can pull base branch updates before the agent starts edits, the
  Agents window refreshes Git state automatically after commits, syncs, and related operations,
  and agents can trigger tasks on remote machines."
- **Our assessment**: These Git flow improvements address a common failure mode in agentic
  workflows: the agent starts editing against a stale base branch, creating merge conflicts
  with work committed by teammates during the session. Auto-pulling the base before edits
  begin reduces divergence risk. Automatic Git state refresh after commits ensures the
  Agents window always shows current state without manual refresh. For Ch04: document
  pre-edit base branch pull as a default Git safety behavior in VS Code agent sessions —
  this reduces merge conflict rates in team environments where multiple agents or human
  developers may be committing to the same branch simultaneously.

## Concrete Artifacts

### Agents Window Feature Set (VS Code, May 2026)

```
GitHub Copilot Agents Window — May 2026 Capabilities (v1.120–v1.123)

SURFACE:
  Agents window in Stable (preview)
  "Work agent-first across multiple projects with a dedicated surface for
   faster navigation and change review."

EXECUTION MODES:
  Local agent       — runs on developer's machine (prior behavior)
  Remote agent      — runs on remote machine via SSH or Dev Tunnels
                       "sessions continuing even when the client disconnects"

INTEROPERABILITY:
  Agent Host Protocol (AHP) — "open protocol for synchronizing agent session
                               state across multiple clients"

SESSION MANAGEMENT:
  Session preferences   — "New sessions keep your recent choices, including
                           agent harness and isolation mode."
  Session sync          — "Chat sessions now sync automatically to your GitHub
                           account, giving you a searchable history of your
                           work across machines and workspaces."
  Multiple side-by-side — "Open more than one agent session at the same time
                           in the Agents window."

HISTORY & REFLECTION:
  Chronicle — "/chronicle commands to query past sessions, generate standup
               reports, and get personalized productivity tips"

GIT FLOW:
  Pre-edit base pull    — "New sessions can pull base branch updates before
                           the agent starts edits"
  Auto Git refresh      — Agents window refreshes state after commits, syncs
  Remote task trigger   — Agents can trigger tasks on remote machines

NETWORK:
  Network retry         — "Terminal commands that require network access are
                           automatically retried with broader network permissions."
```

### Language Model Configuration (VS Code, May 2026)

```
GitHub Copilot VS Code — Language Model Features (May 2026)

BYOK EXPANSION:
  Air-gapped BYOK       — "Bring-your-own-key models can run in isolated
                           environments without GitHub authentication."
  Custom Endpoint       — "Add endpoints compatible with chat completions,
                           responses, or messages from one provider flow."
  BYOK token visibility — "The context window now reports real token usage
                           for bring-your-own-key models."
  Model picker by provider — "Find and switch models more easily in
                               multi-provider environments."

MODEL CONFIGURATION:
  Configurable utility  — "Choose which models handle titles, summaries,
  models                   rename suggestions, commit messages, and intent
                           detection."
  Reasoning effort      — "Configure thinking effort directly from the model
  controls                 picker to balance quality, latency, and cost."
```

### Terminal Safety Properties (VS Code, May 2026)

```
GitHub Copilot VS Code — Terminal Safety (May 2026)

CREDENTIAL PROTECTION (GA):
  "Passwords, passphrases, PINs, and verification codes are entered directly
   in the terminal and are not shared with the LLM."
  → Intercepted before entering LLM context; not a workaround but an
    explicit architectural guarantee.

COMMAND RISK ASSESSMENT (experimental):
  "Terminal confirmations include AI-generated risk levels and short safety
   explanations."
  → AI evaluates command risk; shown to user at confirmation prompt.

AGENT DETECTION:
  VSCODE_AGENT env var — "The VSCODE_AGENT environment variable lets CLIs
                          adapt behavior for agent-initiated commands."
  → CLIs can suppress interactive prompts and use machine-parseable output.

OUTPUT COMPRESSION (expanded):
  "More verbose output patterns from tests, builds, linters, Docker, and
   package managers are compressed before reaching the model."
```

## Cross-References

- **Corroborates** `docs-github-copilot-cli-remote-control-ga.md` (issue #805, Claim 1):
  That source documented GA remote control for Copilot CLI sessions (May 18). This roundup
  adds a related but architecturally distinct pattern: remote *agent execution* over SSH/Dev
  Tunnels (Claim 2 here), where the agent runs on the remote machine rather than being
  monitored remotely. Together the two sources show GitHub building complementary remote
  execution patterns: remote monitoring of local agents (GA) and remote execution with client
  disconnect tolerance (preview). Practitioners choosing between patterns should consider
  whether they want the agent running locally (remote control model) or on an always-on
  remote host (remote agents model).

- **Extends** `docs-github-copilot-byok-vscode.md` (issue #346, Claim 7): That source's
  Claim 7 stated that local BYOK models "still require the Copilot service" with an explicit
  "currently" qualifier. Claim 8 in this note (air-gapped BYOK) appears to fulfill that
  qualifier: BYOK models can now run without GitHub authentication, indicating the Copilot
  service dependency has been relaxed for BYOK scenarios. For Ch02: the April BYOK guidance
  ("requires Copilot service + internet") should be updated with the May caveat that air-gapped
  environments are now supported.

- **Extends** `docs-github-copilot-vscode-auto-model-selection.md` (issue #844): That source
  documented auto model selection as the primary routing mechanism. This roundup adds two new
  model configuration surfaces on top of auto routing: configurable utility models (Claim 9)
  and reasoning effort controls (Claim 10). Together, the three sources show a VS Code model
  configuration hierarchy: (1) auto routing for main tasks, (2) reasoning effort controls
  to tune quality/cost within the selected model, (3) configurable utility models to delegate
  lightweight tasks to cheaper models independently.

- **Extends** `docs-github-copilot-memory-user-preferences.md` (issue #786): That source
  documented Copilot Memory for cross-session user preference persistence. This roundup adds
  session sync (Claim 5) and Chronicle (Claim 6) as complementary cross-session capabilities:
  Memory stores preferences; session sync stores the full session record; Chronicle queries
  the record. Together these form a three-layer personal AI work history: preferences (what
  you like), sessions (what you did), and Chronicle (reflection on what you did).

- **Extends** `docs-github-copilot-vs-april-2026.md` (issue #475, Claim 7): That source
  documented the VS IDE's cloud agent launch from the agent picker as a "dispatch and
  continue" pattern. The VS Code Agents window (Claim 1, this note) provides the VS Code
  equivalent: a first-class multi-project surface for agent work. Together the two sources
  show both major Microsoft IDEs (Visual Studio and VS Code) adopting dedicated agent-first
  UI surfaces in the same two-month window (April–May 2026).

- **Corroborates** `docs-github-copilot-cli-rubber-duck-scheduling-voice.md` (issue #1067):
  That source (June 2 CLI changelog) documented prompt scheduling, voice input, and rubber
  duck review as CLI-side productivity expansions. This roundup documents the VS Code-side
  expansions from the same period (Chronicle for standup reports, multiple side-by-side
  sessions). Together they evidence a May–June 2026 push to expand agent interaction modalities
  beyond single-session synchronous text — across both the CLI and VS Code surfaces.

- **Novel**:
  - First corpus source to document an explicit, guaranteed credential isolation guarantee:
    passwords, passphrases, PINs, and verification codes are intercepted and NOT shared with
    the LLM (Claim 11). Prior sources treat terminal output as uniformly model-visible.
  - First documented multi-model utility configuration in VS Code: separate model slots for
    title generation, summaries, rename suggestions, commit messages, and intent detection
    (Claim 9) — splitting the model routing topology beyond a single chat model.
  - First documentation of the `VSCODE_AGENT` environment variable as a agent-detection
    primitive for CLI tools (Claim 13).
  - First documentation of Chronicle as an AI-powered meta-reflection tool for past agent
    sessions (Claim 6) — agent history as an input to standup reports and productivity
    analysis.
  - First documentation of Agent Host Protocol (AHP) as an open cross-client session
    synchronization protocol (Claim 3).
  - Air-gapped BYOK (Claim 8) is the first documented removal of the GitHub authentication
    requirement for BYOK model usage.

## Guide Impact

### Chapter 02: Harness Engineering — IDE Configuration and Safety

- **Agents window as primary VS Code execution surface**: Update guidance to treat the
  Agents window (now in Stable preview) as the authoritative surface for VS Code agent
  workflows. Practitioners configuring VS Code agent harnesses should use the Agents window
  rather than Chat panel for multi-session, multi-project agentic work.
- **Terminal credential isolation guarantee**: Add an explicit security note that VS Code
  Copilot intercepts passwords, passphrases, PINs, and verification codes before they reach
  the LLM. Teams worried about credentials appearing in terminal sessions can rely on this
  as a documented VS Code safety property, not a workaround.
- **`VSCODE_AGENT` env var for CLI tool authors**: Teams building CLI tools used by agents
  should add a `VSCODE_AGENT` check to disable interactive prompts and switch to
  machine-readable output modes.
- **Update BYOK guidance**: The April 2026 caveat that BYOK requires Copilot service + internet
  is no longer fully accurate — air-gapped BYOK is now available. Update Ch02 BYOK notes.
- **Harness and isolation mode persistence**: Note that VS Code now persists the last-used
  agent harness and isolation mode into new sessions — practitioners who switch configurations
  should explicitly reset their preferences.

### Chapter 04: Agentic Workflows — Multi-Session and Cost Optimization

- **Multi-model utility optimization pattern**: Document the configurable utility models
  capability as a cost optimization strategy: route lightweight utility tasks (commit
  message generation, rename suggestions, title generation) to inexpensive models while
  preserving primary model capacity for substantive coding work.
- **Reasoning effort controls as a cost/quality dial**: Add reasoning effort to the model
  selection section — it provides a within-model quality/cost tradeoff that complements
  model selection.
- **Chronicle for AI work transparency**: Document Chronicle's standup report generation
  as a mechanism for making AI-assisted work visible and summarizable for team communication.
  Teams doing daily standups can generate session-history summaries rather than manually
  reconstructing their AI-assisted work.
- **Remote agent pattern**: Document the remote agent (SSH/Dev Tunnels) pattern as an
  alternative to CCA for long-running tasks where the developer wants to run on a
  persistent remote machine they control, rather than GitHub's cloud infrastructure.
- **Pre-edit base branch pull as Git safety default**: Note that VS Code Agents window
  now pulls base branch updates before agent edits begin — this reduces merge conflict risk
  in team environments without requiring practitioners to manually pull before starting
  agentic sessions.

### Chapter 05: Team Adoption — Enterprise Governance and Safety

- **Command risk assessment (experimental)**: Flag this as an emerging pattern for agent
  safety UX — AI-generated risk levels at command confirmation are likely to become standard.
  Teams evaluating VS Code Copilot for production use should test this feature as part of
  their agentic execution governance review.
- **Session sync and Chronicle as AI work history**: Teams concerned about AI work
  auditability now have a GitHub-native history surface — session sync creates a record
  of what Copilot was asked to do and (via Chronicle) provides query access to that record.
  This is an emerging form of AI work auditability that governance policies should account for.

## Extraction Notes

1. **Roundup format — significant features covered in one or two lines each**: Each feature
   in the source is described in one bullet point. Individual features with major guide impact
   (air-gapped BYOK, remote agents) are extracted with additional context derived from
   cross-referencing against existing source notes. Verbatim quotes are preserved exactly as
   they appear in the changelog.
2. **Some features extend individual May announcements already in the corpus**: Remote control
   (May 18, issue #805) and auto model selection (May 20, issue #844) have individual source
   notes. This roundup's extraction focuses on features not covered by those individual notes
   or synthesis context not present in individual announcements.
3. **Air-gapped BYOK vs. April BYOK note**: The April BYOK note (issue #346) explicitly stated
   local model BYOK required Copilot service + internet with a "currently" qualifier. The May
   air-gapped BYOK claim extends but does not cleanly contradict this — "air-gapped" likely
   refers to removing the GitHub authentication dependency, not necessarily full offline
   operation. The April claim's "currently" qualifier was deliberately hedged; no contradiction
   issue is required.
4. **AHP protocol details not yet disclosed**: AHP is described as "continued investment" —
   this is pre-GA and may not yet have public protocol documentation. Claim 3 is accordingly
   rated "emerging."
5. **Also new section provides minimal signal**: Browser, HTML preview, Markdown improvements
   are IDE UX features with no extractable AI-native engineering patterns; not extracted per
   triage guidance.
