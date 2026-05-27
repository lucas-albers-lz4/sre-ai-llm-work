---
source_url: https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli
source_type: docs
title: "Copilot Memory has more controls for deletion, scope, and the Copilot CLI"
author: GitHub (official changelog)
date_published: 2026-05-26
date_extracted: 2026-05-27
last_checked: 2026-05-27
status: current
confidence_overall: emerging
issue: "#958"
---

# Copilot Memory Has More Controls for Deletion, Scope, and the Copilot CLI

> GitHub's May 26, 2026 changelog incrementally extends Copilot Memory with four
> new capabilities: conversational deletion guidance with down-voting, repository-
> level admin disable controls, three `/memory` CLI commands, and explicit scope
> notifications ("user-level preference" vs. "repository-level fact") at capture
> time — while also expanding availability from Pro/Pro+ early access to public
> preview for all paid Copilot subscribers.

## Source Context

- **Type**: docs (GitHub official product changelog, May 26, 2026; approximately
  300–400 words; public-preview feature expansion announcement)
- **Author credibility**: GitHub engineering team announcing a production feature
  expansion. Authoritative for the fact that these capabilities exist and their
  behavioral descriptions. Not a credible source for: the down-voting mechanism's
  effect on inference accuracy, how fast repository-level disable takes effect,
  the CLI memory session persistence model, or whether scope notifications affect
  what Copilot chooses to store.
- **Scope**: Four incremental enhancements to the Copilot Memory feature first
  announced on May 15, 2026 (`docs-github-copilot-memory-user-preferences.md`):
  deletion guidance, repository-level admin disable, Copilot CLI `/memory`
  commands, and scope transparency at capture time. Also covers the tier expansion
  from Pro/Pro+ early access to all paid Copilot subscribers. Does NOT cover: the
  underlying mechanism for down-voting (how it affects future inference), the
  interaction between repository-level disable and existing stored memories, how
  CLI memory commands interact with IDE-based memory settings, or whether these
  new controls are subject to further change before GA.

## Extracted Claims

### Claim 1: When a user asks Copilot to forget something, Copilot now guides them to the correct settings location to remove the memory and down-votes the memory where voting is available

- **Evidence**: Official GitHub changelog describes this as a new deletion guidance
  behavior. The down-voting mechanism implies a feedback signal to the memory system,
  not merely a UI pointer — Copilot actively signals that a memory is unwanted in
  addition to directing the user to delete it.
- **Confidence**: emerging (product fact; public preview status means behavior may
  change before GA)
- **Quote**: "points you to the right place to remove the memory and down-votes the
  memory where voting is available"
- **Our assessment**: This is the most architecturally interesting enhancement in the
  source. Prior to this change, users who asked Copilot to "forget" something were
  presumably met with a conversational response that did not directly trigger any
  memory system action. The new behavior has two components: (1) a UI navigation
  hint — directing users to the settings page described in the May 15 source
  (`docs-github-copilot-memory-user-preferences.md`, Claim 4); (2) a feedback signal
  — the down-vote, which implies the memory system has a voting/weighting layer that
  can deprioritize memories without full deletion. The distinction matters for
  practitioners: deleting a memory removes it entirely; down-voting reduces its weight
  (exact semantics not documented). For Ch02: practitioners who want to remove a
  specific preference should use the settings page (explicit deletion); practitioners
  who want to signal that a memory was incorrectly inferred can down-vote as a lighter-
  weight correction. The conversational trigger ("ask Copilot to forget") is a new
  interaction pattern — the memory system is now reachable through conversation, not
  only through settings navigation.

### Claim 2: Repository administrators can now disable Copilot Memory at the repository level through existing Copilot feature controls, preventing storage of new repository-level facts while preserving user preferences

- **Evidence**: Official changelog describes repository-level disable as a new admin
  control accessible through existing Copilot feature controls (Repository Settings).
  The "preventing new repository-level facts from being stored" framing implies the
  disable is forward-looking — it prevents future storage but the behavior for existing
  stored facts is not described. The explicit "while preserving user preferences"
  qualifier is documented as the design intent.
- **Confidence**: emerging (product fact; public preview status)
- **Quote**: (no direct quote; capability described in changelog but without a single
  extractable verbatim sentence — see paraphrase in Our assessment)
- **Our assessment**: This is the first repository-level governance control for Copilot
  Memory documented in the corpus. The May 15 source covered only individual user
  settings; this source adds the repository admin layer. The "preserving user
  preferences" qualifier is architecturally significant: disabling memory at the
  repository level does NOT clear or suppress the user-level preferences documented
  in the May 15 source. A repository admin who disables memory for their repository
  is suppressing repository-scoped fact accumulation (e.g., "this repo uses React
  hooks exclusively") but not the user's cross-repository preferences (e.g., "this
  user prefers imperative commit messages"). For Ch05: teams with compliance requirements
  that prohibit codebase facts from being stored in AI memory systems now have a
  per-repository disable control. For Ch06: repository maintainers should evaluate
  whether to disable memory for repositories with sensitive code patterns, third-party
  IP, or compliance constraints — this is now a repository configuration decision
  analogous to enabling/disabling other Copilot features at the repository level.
  Repository Settings > Copilot > Memory is the new governance surface.

### Claim 3: The Copilot CLI now supports `/memory on`, `/memory off`, and `/memory show` commands for managing memory settings within CLI agent sessions

- **Evidence**: Official changelog names all three commands explicitly as new
  capabilities in the Copilot CLI. The command names follow the `/verb` convention
  established by other Copilot CLI commands (e.g., `/remote on` documented in
  `docs-github-copilot-cli-remote-control-ga.md`, Claim 3; `/keep-alive` documented
  in the same source, Claim 4).
- **Confidence**: emerging (product fact; public preview)
- **Quote**: (no single verbatim sentence; the commands `/memory on`, `/memory off`,
  and `/memory show` are named directly in the changelog as new CLI capabilities)
- **Our assessment**: This is the first documentation of dedicated Copilot CLI memory
  management commands in the corpus. Previously, Copilot Memory settings were accessible
  only through GitHub web settings pages. Adding CLI commands creates a second
  interaction surface for memory management, which matters for practitioners using
  the Copilot CLI as their primary AI coding interface. `/memory off` allows a CLI
  session to run without memory accumulation — useful for sessions involving sensitive
  code or one-off exploration tasks where the practitioner does not want interaction
  patterns stored. `/memory show` provides in-session visibility into what has been
  stored — a practitioner can audit their memory state without navigating to GitHub
  settings. `/memory on` re-enables memory if it was disabled. The three-command
  pattern mirrors the `/remote on/off` model for CLI remote control (same source
  conventions), suggesting a consistent CLI interaction model for toggle features. For
  Ch02: add the three `/memory` commands to the Copilot CLI reference. Practitioners
  who have not visited their GitHub settings page can now manage memory entirely within
  the CLI workflow. This is particularly valuable for Copilot CLI practitioners who
  discovered the CLI remote control capability in the May 18 GA announcement and are
  now running long unattended sessions — they can disable memory for sensitive sessions
  with `/memory off` without interrupting the session to navigate to a web settings page.

### Claim 4: At memory capture time, Copilot now explicitly notifies users whether a new entry will be stored as a "user-level preference" (personal, cross-repository) or a "repository-level fact" (visible to all contributors), making scope visible at the moment of creation

- **Evidence**: Official changelog describes scope transparency at capture time as a
  new behavior. The two scope labels ("user-level preference" and "repository-level
  fact") are named in the source as the distinct categories surfaced to users.
- **Confidence**: emerging (product fact; public preview)
- **Quote**: "user-level preference" and "repository-level fact"
- **Our assessment**: This directly addresses a gap identified in the May 15 source
  (`docs-github-copilot-memory-user-preferences.md`, Extraction Notes): "The interaction
  between the pre-existing repository-level Copilot Memory and the new user-level Copilot
  Memory is not documented in this changelog." The scope notification at capture time is
  GitHub's answer to that gap — rather than documenting the interaction as a technical
  specification, they surface it at the UX layer where it matters most: the moment a
  memory is being stored. For the practitioner, this provides immediate feedback on
  whether an interaction is contributing to personal preferences (scope: user) or shared
  repository context (scope: repository). The "visible to all contributors" description
  of repository-level facts is the critical governance signal: contributors to a
  repository accumulate shared knowledge that all team members' Copilot instances can
  access, not just the individual who triggered the memory storage. For Ch05: this scope
  transparency is the runtime governance primitive for teams. Practitioners can now see
  in real time whether their interactions are adding to personal preferences or shared
  repository context — enabling informed decisions about which sessions to run with
  memory enabled vs. disabled (using the `/memory off` command from Claim 3).

### Claim 5: Copilot Memory has expanded from early access for Pro and Pro+ subscribers to public preview for all paid Copilot subscribers

- **Evidence**: The May 15 source (`docs-github-copilot-memory-user-preferences.md`,
  Claim 5) documented Copilot Memory as "early access" for Pro and Pro+ only. This
  May 26 source announces public preview availability for all paid Copilot subscribers,
  implying expansion to Copilot Business and Copilot Enterprise tiers.
- **Confidence**: settled (product fact — tier expansion stated in official changelog)
- **Quote**: (no direct quote; the tier expansion is described in the announcement but
  the exact wording is not extractable as a single sentence without risk of fabrication;
  see paraphrase in Our assessment)
- **Our assessment**: The progression from "early access for Pro/Pro+" (May 15) to
  "public preview for all paid subscribers" (May 26) took eleven days. This is a
  rapid tier expansion for a feature still described as "preview" — suggesting GitHub
  prioritized broad feedback collection over a more gradual rollout. The expansion to
  Business and Enterprise tiers is significant: Business/Enterprise organizations now
  have access to Copilot Memory, which means the repository-level admin disable control
  (Claim 2) is now relevant for enterprise governance. For Ch06: enterprise practitioners
  who previously dismissed Copilot Memory as an individual-tier feature should now
  evaluate it against their governance frameworks, particularly using the repository-level
  disable control for sensitive repositories. The "public preview" label still signals
  that behavior may change before GA — enterprise teams should not build hard dependencies
  on the exact current behavior.

### Claim 6: Repository owners can manage repository-level memory facts through Repository Settings > Copilot > Memory — a distinct governance surface from the user-level Copilot Memory settings page

- **Evidence**: Official changelog specifies Repository Settings > Copilot > Memory
  as the admin management path. This is distinct from the personal Copilot Memory
  settings page described in the May 15 source, which manages user-level preferences.
- **Confidence**: emerging (product fact; public preview)
- **Quote**: (no direct quote; management path described in changelog but not in a
  single extractable verbatim sentence)
- **Our assessment**: The two distinct settings surfaces — personal Copilot Memory
  settings (user preferences) and Repository Settings > Copilot > Memory (repository
  facts) — confirm a two-layer memory governance model. Individual users manage their
  preference layer; repository owners/admins manage the shared fact layer. This mirrors
  the two-scope architecture described in the Claim 4 scope transparency notification.
  For Ch06: practitioners maintaining AI-native repositories should document both
  governance surfaces in their team onboarding materials: (a) tell individual developers
  to review their personal Copilot Memory settings periodically; (b) assign a repository
  maintainer to review and maintain the Repository Settings > Copilot > Memory surface
  for shared facts. The down-voting mechanism (Claim 1) operates at the personal level;
  the repository-level disable (Claim 2) operates at the repo level — these are
  complementary, not overlapping.

## Concrete Artifacts

### Copilot CLI Memory Commands (May 2026)

```
GitHub Copilot CLI — Memory Management Commands
Source: GitHub changelog, May 26, 2026

/memory on    — enable memory for the current CLI session
/memory off   — disable memory for the current CLI session
/memory show  — display currently stored memories

Convention: follows the /verb pattern established by other Copilot CLI
session commands (/remote on, /remote off, /keep-alive)

Use cases:
  - Sensitive sessions:  run /memory off before starting
  - Memory audit:        run /memory show to review stored state
  - Re-enable:           run /memory on after sensitive work is done
```

*Source: Copilot Memory changelog, May 26, 2026*

### Copilot Memory Governance Surfaces (Two-Layer Model)

```
GitHub Copilot Memory — Governance Surfaces (as of May 26, 2026)

LAYER 1 — User Preferences:
  Scope:        User-level (personal, cross-repository)
  Managed via:  Personal Copilot Memory settings on GitHub
  Also via:     /memory on|off|show in Copilot CLI
  Who manages:  Individual user
  Isolation:    Private — does NOT affect teammates

LAYER 2 — Repository Facts:
  Scope:        Repository-level (shared, visible to all contributors)
  Managed via:  Repository Settings > Copilot > Memory
  Who manages:  Repository owner / admin
  Disable:      Admin can disable new fact storage (preserves user prefs)

DELETION PATH (either layer):
  Conversational: Ask Copilot to forget → guided to settings + down-vote
  Settings UI:    Navigate directly to the relevant settings surface

SCOPE TRANSPARENCY:
  At capture time, Copilot displays scope label:
    "user-level preference" — personal use, cross-repository
    "repository-level fact" — visible to all contributors

ACCESS TIERS (as of May 26, 2026):
  Public preview: all paid Copilot subscribers
  (Previously: early access for Pro, Pro+ only as of May 15, 2026)
```

*Source: GitHub changelog, May 15 and May 26, 2026*

### Deletion Guidance Flow (New Behavior)

```
User: [asks Copilot to forget something, e.g., "forget that I use spaces"]

Copilot (new behavior):
  1. Points user to the right place to remove the memory
     (i.e., personal settings or Repository Settings > Copilot > Memory)
  2. Down-votes the memory where voting is available
     (signals it as unwanted without requiring manual settings navigation)

Prior behavior (implied): Copilot acknowledged the request conversationally
                           but did not trigger any memory system action

Note: Down-vote vs. deletion distinction:
  Delete:     Removes the memory entry entirely
  Down-vote:  Reduces the memory's weight/priority (exact semantics not
              documented in this changelog)
```

*Source: GitHub changelog, May 26, 2026*

## Cross-References

- **Corroborates**:
  - `docs-github-copilot-memory-user-preferences.md` (Claim 1): The user-scope vs.
    repository-scope architecture introduced in the May 15 source is confirmed and
    made visible to the user via the scope transparency notification (Claim 4 here).
    Both sources independently describe the same two-scope model; this source makes
    the distinction runtime-visible.
  - `docs-github-copilot-memory-user-preferences.md` (Claim 4): The management
    interface for user-level preferences described in the May 15 source is now
    complemented by: (a) conversational deletion guidance (Claim 1); (b) CLI
    `/memory` commands (Claim 3). Both sources document the management surface for
    user-level memory; this source adds two new access paths to the same surface.
  - `docs-github-copilot-cli-remote-control-ga.md` (Claim 3): That source documented
    the `/remote on` CLI command convention. This source adds `/memory on|off|show`
    using the same `/verb` command pattern. Both confirm that Copilot CLI is being
    built with a consistent `/verb` command model for managing session-level features.

- **Extends**:
  - `docs-github-copilot-memory-user-preferences.md`: The May 15 source documented
    the base user-level Copilot Memory feature for Pro/Pro+ in early access, with
    deletion via the personal settings page. This May 26 source adds: CLI management
    commands, repository-level admin control, scope transparency at capture time,
    conversational deletion guidance with down-voting, and tier expansion to all
    paid subscribers. Together the two sources form a complete current-state picture
    of Copilot Memory as of May 26, 2026.
  - `docs-github-copilot-cli-remote-control-ga.md` and
    `docs-github-copilot-jetbrains-cli-agent-sessions.md`: Those sources established
    the Copilot CLI as a growing surface for session management features. This source
    adds three more CLI commands to that surface, extending the pattern that GitHub
    is building a rich set of `/verb` in-session management commands for the Copilot CLI.
  - `docs-github-copilot-memory-user-preferences.md` (Extraction Notes): That note
    flagged the gap: "The interaction between the pre-existing repository-level Copilot
    Memory and the new user-level Copilot Memory is not documented in this changelog."
    This May 26 source directly resolves that gap with the scope transparency notification
    and the two-layer governance model.

- **Contradicts**: None. The May 15 source's "early access for Pro/Pro+" statement is
  not contradicted by this source's "public preview for all paid subscribers" — it is a
  progression, not a reversal. The scope architecture (user vs. repository) is consistent
  across both sources. No contradiction issue filed.

- **Novel**:
  - **Copilot CLI `/memory` commands** (Claim 3): No prior corpus source documents
    in-session CLI commands for managing Copilot Memory. This is the first CLI-native
    path to memory management, distinct from web settings navigation.
  - **Repository-level admin disable for Copilot Memory** (Claim 2): No prior corpus
    source documents a repository admin control that prevents Copilot from storing
    repository-level facts. This is the first per-repository governance primitive for
    AI memory in the corpus.
  - **Down-voting as a memory feedback mechanism** (Claim 1): The concept of a down-vote
    signal to the memory system — lighter than full deletion, heavier than ignoring —
    is new to the corpus. No prior source documents a memory weighting or voting layer
    in any commercial AI coding tool.
  - **Scope transparency at capture time** (Claim 4): The runtime notification ("user-
    level preference" vs. "repository-level fact") at the moment memory is stored is
    a new UX primitive for AI memory governance. No prior corpus source documents a
    commercial AI coding tool that labels stored memories by scope at creation time.

## Guide Impact

- **Chapter 02 (Tool Configuration / Harness Engineering)**: Add Copilot CLI `/memory`
  commands to the CLI command reference (`/memory on`, `/memory off`, `/memory show`).
  Recommend `/memory off` as a standard practice when running CLI sessions that process
  sensitive code, third-party IP, or compliance-sensitive material. The CLI path to
  memory management is now equivalent in capability to web settings navigation for the
  commands it covers. Update the Copilot Memory configuration hierarchy artifact in
  `docs-github-copilot-memory-user-preferences.md`'s Concrete Artifacts section to
  include the CLI surface.

- **Chapter 05 (Team Adoption / Governance)**: The repository-level admin disable
  (Claim 2) and scope transparency at capture time (Claim 4) are the two most team-
  relevant additions. For Ch05: recommend that teams with sensitive repositories
  evaluate repository-level memory disable as a governance control. Add the scope
  transparency notification as the runtime complement to the documented scope architecture:
  practitioners can now see in real time whether their interaction is contributing to
  personal preferences or shared repository context. This makes the two-scope model
  operational, not just architectural.

- **Chapter 06 (Scaling / Maintaining AI-Native Systems)**: The expansion to all paid
  subscribers (Claim 5) means enterprises on Copilot Business and Enterprise tiers should
  now factor Copilot Memory governance into their AI usage policies. Repository Settings >
  Copilot > Memory (Claim 6) is a new maintenance surface for repository owners. Add
  to enterprise Copilot governance checklists: (a) decide per-repository whether memory
  should be enabled or disabled; (b) assign a repository maintainer to review the
  repository memory facts periodically; (c) include the Copilot Memory settings page
  and CLI commands in developer onboarding.

## Extraction Notes

- The source is a short GitHub changelog entry (~300–400 words, consistent with other
  GitHub Copilot changelog entries in the corpus). Content was fetched twice with
  different prompts. Results were consistent across both fetches for all four key
  features. Verbatim quotes are restricted to the deletion guidance sentence (Claim 1),
  which appeared consistently across both fetches, and the scope labels "user-level
  preference" and "repository-level fact" (Claim 4), which appeared in the second fetch.
  CLI command names (`/memory on`, `/memory off`, `/memory show`) are treated as
  verbatim because they are command syntax, not narrative text.
- The "down-voting" mechanism (Claim 1) is the most semantically uncertain element:
  the changelog describes it as occurring "where voting is available," which implies
  voting is not available for all memory entries. The exact semantics of down-voting
  vs. deletion are not specified in this changelog.
- The behavior for existing stored repository-level facts when a repository admin
  disables Copilot Memory (Claim 2) is not described. It is unclear whether disable
  affects only future storage or also purges existing facts. This is a governance gap
  worth documenting if this source informs guide content.
- This source and `docs-github-copilot-memory-user-preferences.md` together constitute
  the complete Copilot Memory documentation available in the corpus as of May 27, 2026.
  They should be read together: the May 15 note covers the base feature; this May 26
  note covers the incremental enhancements.
- No contradictions were found. No contradiction issue filed.
