---
source_url: https://github.blog/changelog/2026-06-02-introducing-copilot-cli-and-agentic-capabilities-enhancements-in-jetbrains-ides
source_type: docs
title: "Introducing Copilot CLI and agentic capabilities enhancements in JetBrains IDEs"
author: GitHub (official changelog)
date_published: 2026-06-02
date_extracted: 2026-06-03
last_checked: 2026-06-03
status: current
confidence_overall: emerging
issue: "#1036"
---

# Introducing Copilot CLI and Agentic Capabilities Enhancements in JetBrains IDEs

> GitHub's June 2, 2026 JetBrains changelog adds seven substantive enhancements to the
> May 13 CLI agent foundation: an agent picker with explicit mode control, three new
> slash commands (/remote, /compact, /chronicle) for session management and self-improvement,
> a public-preview agent debug panel for sub-agent debugging, Cloud Agent integration into
> the unified sessions view, configurable thinking effort per request, and a centralized
> agent customizations editor — plus GA promotions for agent skills, hooks, prompt files,
> Anthropic Thinking, and BYOK.

## Source Context

- **Type**: docs (GitHub official product changelog, June 2, 2026; approximately 600 words
  covering seven new feature areas plus availability updates)
- **Author credibility**: GitHub engineering team announcing production feature releases in
  the JetBrains Copilot plugin. Authoritative for the existence and described behavior of each
  feature, exact settings paths and slash command syntax, and GA/preview status of each
  capability. Not authoritative for: performance characteristics of CLI agent vs. non-CLI agent
  modes, how thinking effort affects output quality or cost in practice, latency of the agent
  debug panel, or how /chronicle improve-generated instructions interact with existing
  workspace instructions.
- **Scope**: Seven new features in the June 2026 JetBrains Copilot update — agent picker for
  CLI sessions, /remote / /compact / /chronicle slash commands, agent debug panel (public
  preview), Cloud Agent in unified sessions view, configurable thinking effort, and agent
  customizations editor — plus availability updates (skills/hooks/prompt files/Anthropic
  Thinking reaching GA, BYOK removing preview flag, phased rollout of CLI agent as default).
  Does NOT cover: how the agent picker modes compare in token consumption, what happens when
  /chronicle improve-generated instructions conflict with existing project instructions, whether
  Cloud Agent sessions in the unified view expose the same status fields as local and CLI
  sessions, or cost differences between thinking effort levels.

## Extracted Claims

### Claim 1: Copilot CLI agent in JetBrains now includes an agent picker enabling explicit mode selection between Agent (default), Ask, Custom agents, and Plan mode

- **Evidence**: Official GitHub product changelog listing all four modes with descriptions.
  Agent mode is explicitly labeled as the default.
- **Confidence**: emerging (official claim; CLI agent is still in public preview as of June 2)
- **Quote**: "Copilot CLI agent now includes an agent picker that lets you flexibly choose
  between different operating modes to suit your workflow"
- **Our assessment**: The agent picker converts what was previously implicit (whatever mode
  the agent started in) into an explicit practitioner decision point. Plan mode's description
  is the most substantive addition: "Collaborate on planning before implementation, where
  Copilot analyzes your request and builds a structured implementation plan for your review."
  This formalizes a human review gate at the planning stage — the agent cannot proceed to
  execution until the practitioner approves the plan. For Ch02: the four modes map to
  four distinct risk/autonomy postures. Agent mode is highest autonomy; Ask mode is lowest;
  Plan mode inserts a mandatory human gate before execution; Custom agents apply
  project-specific instructions. Practitioners should establish team norms around which
  mode to use for which task class.

### Claim 2: The /remote slash command in JetBrains CLI sessions enables remote control from github.com or GitHub Mobile, enabled via a JetBrains settings path

- **Evidence**: Official changelog documents the command and its settings path: "Enable it
  from Settings > Tools > GitHub Copilot > Chat > Enable Copilot CLI Remote."
- **Confidence**: emerging (official claim; CLI agent still in public preview)
- **Quote**: "The /remote command lets you remotely control a Copilot CLI session from
  github.com or the GitHub Mobile app."
- **Our assessment**: This is the JetBrains-specific implementation of the remote control
  capability that reached GA across all platforms on May 18 (`docs-github-copilot-cli-remote-
  control-ga.md`, Claim 1). The May 18 source documented the VS Code path
  (`github.copilot.chat.cli.remote.enabled` setting + `/remote on` in Chat view); this June 2
  source adds the JetBrains settings path (Settings > Tools > GitHub Copilot > Chat > Enable
  Copilot CLI Remote). The capability is the same: monitor and steer CLI sessions from
  github.com or mobile. For harness engineering: the JetBrains path is now documented;
  practitioners who use JetBrains as their primary IDE now have a native /remote entry point
  without needing the terminal `/remote on` command.

### Claim 3: The /compact slash command lets practitioners manually compress Copilot CLI session context at any time, keeping long-running sessions manageable

- **Evidence**: Official changelog documents the command with an explicit use case: managing
  long-running sessions. No configuration required; invoked mid-session.
- **Confidence**: emerging (official claim; CLI agent still in public preview)
- **Quote**: "The /compact command lets you manually compress the Copilot CLI session context
  at any time, keeping long-running sessions more manageable."
- **Our assessment**: This is a novel operational primitive not previously documented in our
  corpus. Prior sources discuss context limits as a constraint practitioners must plan around
  (e.g., via compact AGENTS.md, summarization tools); this is the first documented on-demand
  compression command that the practitioner can invoke mid-session without losing the session.
  For Ch01 (daily workflows): document /compact alongside /keep-alive as a required operational
  primitive for long-running CLI sessions. A session that accumulates many tool calls, file
  reads, and sub-agent exchanges over hours will hit context limits without /compact. The
  on-demand nature means practitioners control when compression happens — not the agent
  autonomously deciding to drop context.

### Claim 4: The /chronicle command enables four modes of session analysis and self-improvement: standup reports, personalized tips, pattern-based custom instruction generation, and session search

- **Evidence**: Official changelog enumerates all four subcommands with descriptions. The
  /chronicle improve subcommand is the most substantive: it analyzes session history to
  generate custom instructions.
- **Confidence**: emerging (official claim; feature specifics not independently verified)
- **Quote**: "/chronicle improve: Analyzes your session history to identify patterns where
  Copilot may have misunderstood your intent or where there was a lot of back-and-forth. It
  uses this analysis to generate custom instructions to help Copilot better understand you
  in the future."
- **Our assessment**: /chronicle is the most novel capability in this update. Its four modes
  serve distinct purposes: /chronicle standup produces a work summary ("Generates a short
  report summarizing what you worked on in your recent CLI sessions") useful for async
  team communication; /chronicle tips provides personalized guidance; /chronicle improve
  closes a self-optimization loop — it turns session history into custom instructions, which
  then inform future sessions; /chronicle search enables retrospective retrieval. The
  /chronicle improve pattern is particularly significant for harness engineering: it is a
  documented self-improvement loop where the agent's failures (misunderstandings,
  back-and-forth) are automatically converted into corrective instructions. This is the
  first corpus evidence of an IDE-integrated self-improving instruction layer. For Ch02:
  document /chronicle improve as a path to iterative harness refinement — run it periodically
  to let the CLI agent calibrate its instructions to the practitioner's actual working patterns.
  The generated instructions should be reviewed before application (they're AI-generated
  suggestions, not authoritative configuration).

### Claim 5: The Agent Debug Panel (public preview) shows a chronological event log of agent interactions during CLI sessions, intended for debugging custom agents and sub-agent workflows

- **Evidence**: Official changelog describes the panel's content and primary use case.
  Setup requires selecting Copilot CLI from the agent picker, then accessing the panel via
  settings icon. File-based logging requires a separate settings toggle.
- **Confidence**: emerging (official claim; explicitly labeled public preview)
- **Quote**: "The Agent Debug Log panel shows a chronological event log of agent interactions
  during a Copilot CLI session, making it especially useful when debugging custom agents and
  orchestrated sub-agent workflows."
- **Our assessment**: This fills a gap identified in the May 13 note (Claim 5, unified sessions
  view): while the sessions view shows status and elapsed time for running sessions, it provides
  no visibility into the sequence of events within a session. The debug panel adds that
  intra-session observability — particularly for practitioners building multi-layer agent
  workflows where understanding the event sequence is essential for diagnosing failures. For
  Ch04 (agentic workflows): document the Agent Debug Panel as the primary debugging surface
  for custom agents and sub-agent orchestrations. The "Enable Agent debug File Logging" toggle
  is notable — persistent file logging enables post-session analysis, not just real-time
  observation. Business/Enterprise users require the "Editor preview features" policy to be
  enabled by an administrator.

### Claim 6: Cloud Agent sessions are now integrated into the unified sessions view alongside local and CLI sessions, with filtering by agent type or status

- **Evidence**: Official changelog documents the integration as an explicit new feature with
  the same filtering capability already available for other session types. Settings path to
  enable Cloud Agent: "Settings > Tools > GitHub Copilot > Chat > Enable Coding Agent."
- **Confidence**: emerging (official claim; Business/Enterprise admin-gated)
- **Quote**: "Cloud agent sessions are now surfaced directly in the unified sessions view in
  the chat panel. This makes it easier to manage and monitor all your agent sessions from
  one place, whether they're local, CLI, or cloud."
- **Our assessment**: The May 13 source (Claim 5) introduced the unified sessions view for
  local and CLI agent sessions. This June 2 update extends it to cover Cloud Agent as well,
  completing the trifecta: local, CLI, and cloud. A practitioner who delegates one task to
  the local CLI agent, another to a cloud agent, and a third to a local agent mode session
  now has a single view for all three. This is the operational dashboard pattern for
  multi-agent concurrent work that Ch04 should document. The filter by agent type enables
  "show me only cloud sessions" — relevant for practitioners who run a mix of local and cloud
  agents and want to assess cloud session cost or progress separately.

### Claim 7: Practitioners can now configure thinking effort level per request directly from the JetBrains model picker, using higher effort for complex tasks and lower for straightforward ones

- **Evidence**: Official changelog documents the model picker integration, the effort level
  options, and the reasoning for each level. Non-reasoning models (e.g., GPT-4o) do not
  show the submenu.
- **Confidence**: emerging (official claim; feature availability depends on model support)
- **Quote**: "For reasoning models that support configurable thinking effort, you can now
  control how much reasoning the model applies to each request, directly from the model picker."
- **Our assessment**: This is the JetBrains-specific rollout of thinking effort configuration,
  introduced on the same date for Eclipse in `docs-github-copilot-eclipse-byok-skills-chat.md`
  (Claim 8). Both IDE updates publish the same day (June 2, 2026), indicating GitHub rolled
  out thinking effort control across IDEs simultaneously. The changelog provides explicit
  guidance on effort levels: "Use a higher effort level for complex tasks like architectural
  decisions or multi-step debugging, and a lower level for straightforward code generation
  or simple questions." For Ch04: add thinking effort as a practitioner-configurable quality/
  latency tradeoff. The per-request nature (not a global setting) means practitioners can
  apply high effort selectively without a blanket overhead increase. The task-to-effort
  mapping (architecture → high, syntax lookup → low) should be documented as a calibration
  heuristic. Note that Anthropic Thinking (which underlies this for Anthropic models) reaches
  GA in this same update (Claim 9).

### Claim 8: The Agent Customizations editor provides a centralized UI for creating and managing custom agents, skills, instructions, and prompts at workspace or personal scope

- **Evidence**: Official changelog describes the editor's scope and the two configuration
  levels (workspace = team; personal = across projects). Access via settings icon in Copilot
  Chat panel → Customizations.
- **Confidence**: settled (product fact — centralized editor with documented scope)
- **Quote**: "The Agent Customizations editor provides a centralized UI for creating and
  managing all your agent customizations in one place. You can configure workspace
  customizations for the entire team, or create personal ones that follow you across projects."
- **Our assessment**: Prior to this editor, custom agent configuration required editing
  `.agent.md` files directly (documented in the May 13 source, Claim 8: `~/.copilot/agents`
  for user scope; `.github/agents/` for project scope). The Agent Customizations editor adds
  a UI layer above those files — it is a discovery and editing surface, not a new configuration
  model. The workspace/personal scope distinction maps to the project-scope vs. user-scope
  agent config model. For Ch02: the editor reduces the friction of discovering existing
  customizations and making changes without file navigation. Teams onboarding new practitioners
  can point to the editor as the starting point for understanding what agents and skills are
  configured. Important: the editor modifies the same underlying files — understanding the
  file locations remains necessary for version control and code review of agent configuration.

### Claim 9: Agent skills, agent hooks, prompt files, and Anthropic Thinking all reach general availability in the June 2026 JetBrains update

- **Evidence**: Official changelog "Availability updates" section lists each capability
  with its new status. All four are stated as "generally available" in the same release.
- **Confidence**: settled (GA status stated definitively in official changelog)
- **Quote**: "Agent skills are generally available" / "Agent hooks are generally available" /
  "Prompt files are generally available" / "Anthropic Thinking is generally available"
- **Our assessment**: This is a significant maturation signal. Four capabilities that were
  previously in preview or experimental status across JetBrains have simultaneously graduated
  to GA. For the guide: any caveat language around JetBrains agent skills, hooks, prompt
  files, or Anthropic Thinking being "in preview" should be removed as of June 2026. The
  simultaneous GA promotion of these four features suggests GitHub views the May-to-June
  period as the JetBrains agentic capabilities graduation milestone. Agent skills GA is
  particularly relevant to `docs-github-copilot-agent-skills-cli.md` (Claim 1), which
  established the Copilot CLI as the primary surface for new agent feature development — those
  skills are now stable in JetBrains.

### Claim 10: BYOK (Bring Your Own Key) is now available without the Editor Preview feature flag in JetBrains, with Business and Enterprise availability controlled by GitHub policy

- **Evidence**: Official changelog "Availability updates" section explicitly removes the
  preview flag requirement. Policy link: "github.com/settings/copilot/features" (for
  B&E plan admins).
- **Confidence**: settled (flag removal stated definitively in official changelog)
- **Quote**: "BYOK is available without the `Editor Preview` feature flag, and availability
  for Copilot Business and Enterprise is controlled by GitHub policy"
- **Our assessment**: This update removes a friction point for JetBrains BYOK adoption.
  Prior to this update, accessing BYOK in JetBrains required enabling the Editor Preview
  features policy — a coarse bundled gate. After this update, BYOK has its own dedicated
  policy control for Business/Enterprise users, enabling admins to enable BYOK specifically
  without also enabling other preview features. The shift from preview flag to dedicated
  policy is a governance maturation: admins get surgical control over BYOK separately from
  other experimental features.

### Claim 11: GitHub is beginning a phased rollout to make Copilot CLI agent the default experience in JetBrains, offering isolation modes, live session progress, and tool call visibility as differentiators

- **Evidence**: Official changelog states the phased rollout explicitly and enumerates the
  three differentiating capabilities that justify the default promotion.
- **Confidence**: emerging (phased rollout = not yet fully deployed; "in public preview" still
  applies to CLI agent)
- **Quote**: "We're rolling out a phased transition to make Copilot CLI agent (currently in
  public preview) the default. It offers a more powerful and consistent agentic experience,
  with support for multiple isolation modes, live session progress, and tool call visibility."
- **Our assessment**: This is the strongest signal yet that GitHub intends the Copilot CLI
  agent to supersede earlier agent modes as the primary agentic execution layer in JetBrains.
  The three differentiators — isolation modes, live session progress, tool call visibility —
  directly address the core practitioner concerns for long-running agent work: safety (isolation),
  observability (live progress), and auditability (tool call visibility). Note: Business and
  Enterprise subscribers still need administrator enablement of the editor preview features
  policy to use CLI agent. The default promotion may arrive before all teams have that policy
  enabled, creating a potential gap where the "default" experience requires admin action.
  For the guide: language around CLI agent being an "optional" or "preview" feature should
  be updated to reflect its trajectory as the intended primary mode.

## Concrete Artifacts

### Agent Picker Modes (Copilot CLI in JetBrains, June 2026)

```
Copilot CLI Agent Picker — JetBrains (June 2, 2026)

Modes:
  AGENT (default)   Full agentic experience with autonomous task execution.
  ASK               Get quick answers and assistance.
  CUSTOM AGENTS     Use personalized agents tailored to your specific needs.
  PLAN              Collaborate on planning before implementation; Copilot
                    analyzes your request and builds a structured implementation
                    plan for your review before proceeding.

Admin requirement for B/E:
  All modes: requires "Editor preview features" policy to be enabled by admin.
```

*Source: Introducing Copilot CLI and agentic capabilities enhancements in JetBrains IDEs, June 2, 2026*

### New Slash Commands for Copilot CLI Sessions

```
/remote
  Enables remote control of a Copilot CLI session from github.com or GitHub Mobile.
  Enable via: Settings > Tools > GitHub Copilot > Chat > Enable Copilot CLI Remote

/compact
  Manually compresses the CLI session context to keep long-running sessions manageable.
  No configuration required; invoke mid-session.

/chronicle [subcommand]
  standup   — Short report summarizing recent CLI session work
  tips      — Personalized tips for using Copilot CLI more effectively
  improve   — Analyzes session history for misunderstandings/back-and-forth patterns;
               generates custom instructions to improve future sessions
  search    — Search sessions for ones matching a query
```

*Source: Introducing Copilot CLI and agentic capabilities enhancements in JetBrains IDEs, June 2, 2026*

### Agent Debug Panel Setup

```
Agent Debug Panel (Public Preview — JetBrains, June 2026)

Step 1: Select "Copilot CLI" from the agent picker in Copilot Chat panel
Step 2: Click the settings icon (top-right) → select "Agent Debug Panel"
        → Shows chronological event log of agent interactions

Step 3 (optional, for persistent logging):
  Settings > Tools > GitHub Copilot > Chat > Enable Agent debug File Logging
  → Logs persist to file for post-session analysis

Admin requirement:
  Copilot Business/Enterprise: requires "Editor preview features" policy enabled by admin.
```

*Source: Introducing Copilot CLI and agentic capabilities enhancements in JetBrains IDEs, June 2, 2026*

### Thinking Effort Configuration

```
Thinking Effort — JetBrains Copilot (June 2, 2026)

Access: Open model picker in chat input field
        → Select a reasoning model
        → Select effort level from "Thinking Effort" submenu

Effort levels (guidance from changelog):
  Higher effort: complex tasks — architectural decisions, multi-step debugging
  Lower effort:  straightforward tasks — code generation, simple questions

Note: Only reasoning models show the Thinking Effort submenu.
      Non-reasoning models (e.g., GPT-4o) do not display this option.
```

*Source: Introducing Copilot CLI and agentic capabilities enhancements in JetBrains IDEs, June 2, 2026*

### Availability Promotions (June 2, 2026 — JetBrains)

```
Capability                  New Status
──────────────────────────────────────────────────────────────
Agent skills                Generally available
Agent hooks                 Generally available
Prompt files                Generally available
Anthropic Thinking          Generally available
BYOK                        Available without Editor Preview flag
                            (B/E availability controlled by GitHub policy)
Copilot CLI agent           Phased rollout as default (still public preview)
```

*Source: Introducing Copilot CLI and agentic capabilities enhancements in JetBrains IDEs, June 2, 2026*

## Cross-References

- **Corroborates**:
  - `docs-github-copilot-jetbrains-cli-agent-sessions.md` (Claims 5, 6): The May 13 source
    introduced the unified sessions view covering local and CLI sessions. Claim 6 in the
    present note extends that view to cover Cloud Agent sessions as well — corroborating the
    unified sessions view as GitHub's chosen observability primitive for multi-agent JetBrains
    work while adding the third session type.
  - `docs-github-copilot-cli-remote-control-ga.md` (Claims 1, 3, 7): The remote control GA
    source established the feature as available across mobile, github.com, VS Code, and
    JetBrains. The present note's Claim 2 adds the JetBrains-specific settings path (Settings
    > Tools > GitHub Copilot > Chat > Enable Copilot CLI Remote), corroborating that JetBrains
    is a supported remote control platform with its own integration path. The admin policy
    gate (Claim 7 in remote control GA: requires admin enablement for B/E) applies here as well.
  - `docs-github-copilot-eclipse-byok-skills-chat.md` (Claim 8): The Eclipse June 2 note
    documented selectable thinking effort as its "first documented user-facing thinking effort
    control in corpus." The present note's Claim 7 documents the same capability introduced on
    the same date for JetBrains — corroborating that thinking effort configuration was a
    simultaneous cross-IDE rollout on June 2, 2026.

- **Extends**:
  - `docs-github-copilot-jetbrains-cli-agent-sessions.md` (all claims): This note is the
    direct follow-up to the May 13 CLI agent introduction. Every new feature in the present
    note builds on the May 13 foundation: the agent picker extends the isolation mode choice
    (Claims 2, 3 in May 13); the /remote command extends the CLI session remote control already
    enabled (but without a JetBrains settings path); the unified sessions view extends to cover
    cloud agents; the debug panel extends session observability beyond status fields. For the
    guide: the May 13 note should be cross-referenced as the prerequisite reading before this note.
  - `docs-github-copilot-cli-remote-control-ga.md` (Claim 5): The remote control GA source
    documented the VS Code remote control setup path (`github.copilot.chat.cli.remote.enabled`
    setting + `/remote on` in Chat view). The present note's Claim 2 adds the parallel JetBrains
    path (Settings > Tools > GitHub Copilot > Chat > Enable Copilot CLI Remote). Together these
    two sources document the complete per-IDE remote control setup for VS Code and JetBrains.
  - `docs-github-copilot-agent-skills-cli.md` (Claim 1): That source documented agent skills
    as a growing capability surface on the Copilot CLI. The present note's Claim 9 confirms
    skills have reached GA in JetBrains, marking the maturation milestone for what that source
    introduced as an emerging capability.
  - `docs-github-copilot-byok-vscode.md` (Claim 1): The VS Code BYOK note documented BYOK
    availability for B/E users. The present note's Claim 10 documents that JetBrains BYOK
    has shed its preview flag, moving closer to the mature status documented for VS Code.

- **Contradicts**: None identified. The Eclipse note (Claim 8 in
  `docs-github-copilot-eclipse-byok-skills-chat.md`) describes thinking effort as "the first
  documented user-facing thinking effort control in corpus" — but the JetBrains note introduces
  the same feature on the same date. This is not a conceptual contradiction; both notes
  describe distinct IDE releases from the same June 2 batch. The Eclipse note's "first in
  corpus" framing applies only to Eclipse being mined first; no contradiction issue filed.

- **Novel**:
  - **/chronicle commands as a session self-improvement loop** (Claim 4): No prior source in
    corpus documents a capability for an AI coding tool to analyze its own session history
    and generate corrective custom instructions from patterns of misunderstanding. The
    /chronicle improve subcommand is the first evidence of an IDE-integrated feedback loop
    that converts agent failures into future configuration improvements.
  - **/compact as an on-demand context compression primitive** (Claim 3): Prior corpus sources
    discuss context limits as constraints to engineer around proactively. /compact is the first
    documented mid-session command that lets practitioners compress context without ending the
    session.
  - **Agent Debug Panel for sub-agent orchestration debugging** (Claim 5): No prior corpus
    source documents a purpose-built event log UI for debugging multi-layer agent workflows.
    Prior sources treat sub-agent debugging as a terminal/log-file concern; the debug panel
    makes it a first-class IDE feature.
  - **Thinking effort as a per-request JetBrains IDE control** (Claim 7): Confirms the
    cross-IDE simultaneous rollout of thinking effort configuration (Eclipse and JetBrains,
    same date). The per-request granularity (not a session-level setting) is documented here
    for JetBrains specifically.

## Guide Impact

- **Chapter 02 (Harness Engineering — Agent Configuration)**:
  - Update the worktree/workspace isolation mode section (from May 13 note) to reflect the
    agent picker as the user-facing control for mode selection. The picker (Agent/Ask/Plan/Custom)
    is now the recommended entry point for mode selection rather than configuration files alone.
  - Add /chronicle improve as a harness calibration technique: practitioners should run it
    periodically and review generated custom instructions before adopting them. Document the
    file locations where generated instructions land so teams can version-control them.
  - Add thinking effort configuration guidance: high effort for architectural/debugging tasks,
    low effort for routine code generation. Note that Anthropic Thinking is now GA (not preview).
  - Update BYOK guidance to note that JetBrains BYOK no longer requires the Editor Preview flag.

- **Chapter 04 (Agentic Workflows — Observability and Debugging)**:
  - Add Cloud Agent integration into the unified sessions view as completing the "trifecta"
    pattern: local + CLI + cloud sessions now visible in one place. Document the filter-by-type
    capability for practitioners managing concurrent multi-mode agent work.
  - Add the Agent Debug Panel as the primary debugging surface for custom agent and sub-agent
    workflow issues. Document the two-step setup (agent picker selection + settings icon) and
    the file logging option for post-session analysis.
  - Add /compact to the operational primitive list alongside /keep-alive
    (`docs-github-copilot-cli-remote-control-ga.md`, Claim 4). Any session expected to run
    longer than a few hundred exchanges should use /compact proactively before hitting limits.

- **Chapter 02 (Harness Engineering — Session Management Patterns)**:
  - Add /chronicle standup as an async team communication pattern: practitioners who do deep
    CLI agent work can generate standup summaries without manually reconstructing what they
    delegated. Reduces the overhead of daily standups for agent-heavy workflows.
  - Add /chronicle improve as a periodic maintenance recommendation: run weekly or after
    completing a large feature to calibrate the agent's custom instructions to the practitioner's
    actual working style.

- **Chapter 04 (Agentic Workflows — Status Updates)**:
  - Update any language describing agent skills, hooks, or prompt files as "in preview" for
    JetBrains — all three reached GA on June 2, 2026.
  - Update language describing Copilot CLI agent as "optional" or "experimental" — GitHub is
    actively rolling it out as the default, and the three differentiators (isolation modes, live
    session progress, tool call visibility) justify the transition to primary mode.

## Extraction Notes

1. **Source is a changelog (~600 words)**: All substantive engineering-relevant claims are
   captured in the eleven claims above. User experience improvements (smooth NES experience,
   session persistence, UI freeze handling stability) and sign-in options (Google/Apple
   authentication) were noted but not extracted as harness engineering signal.
2. **Two WebFetch calls made**: The first call returned a summarized extraction; the second
   returned the full verbatim text of the article. All quotes in this note are taken from the
   second fetch's verbatim output. Quote locations cross-checked against the full article
   structure (sections: New features, UX/reliability improvements, Availability updates, Try
   it out, Share your feedback).
3. **Relationship to May 13 source**: This note intentionally does not re-extract features
   already documented in `docs-github-copilot-jetbrains-cli-agent-sessions.md` (worktree/
   workspace isolation, unified sessions view basics, Ask question tool, global .agent.md path,
   plan agent behavioral change, Edit mode removal). All eleven claims here are additive or
   update the GA status of previously-preview features.
4. **Phased rollout caveat**: CLI agent is simultaneously "being rolled out as default" and
   "still in public preview." This creates ambiguity for practitioners: the feature is becoming
   the default but is not yet GA. Guide language should reflect this transitional state rather
   than treating it as either fully stable or fully experimental.
5. **No contradictions to file**: The Eclipse note's "first in corpus" framing for thinking
   effort (Claim 8 in `docs-github-copilot-eclipse-byok-skills-chat.md`) is about corpus
   extraction order, not a factual claim that conflicts with JetBrains introducing the same
   capability on the same date. No contradiction issue filed.
