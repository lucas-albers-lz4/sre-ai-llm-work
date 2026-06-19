---
source_url: https://claude.com/blog/artifacts-in-claude-code
source_type: blog-post
title: "Claude Code now supports artifacts"
author: Anthropic
date_published: 2026-06-18
date_extracted: 2026-06-19
last_checked: 2026-06-19
status: current
confidence_overall: emerging
issue: "#1221"
---

# Claude Code now supports artifacts

> Official Anthropic product announcement introducing artifacts in Claude Code — live, authenticated, version-tracked web pages generated from session context (codebase + connectors + conversation), with org-scoped sharing and admin controls, spanning nine documented role-based use cases from SRE incident response to legal audits and PR walkthroughs.

## Source Context

- **Type**: blog-post (official Anthropic claude.com blog, June 18, 2026; product announcement for a beta feature)
- **Author credibility**: First-party Anthropic product announcement. Maximum authority for what the feature does, how it is shared, and which practitioner patterns Anthropic intends. Beta status means the feature is available to Team and Enterprise orgs but behavior may change. No independent practitioner accounts accompany this announcement.
- **Scope**: Covers what artifacts are, how they are created (natural language invocation), how session context feeds into them, the live-update/versioning model, privacy and access controls (org-scoped, admin toggle, compliance API), a gallery for managing artifacts, nine role-based use case prompt examples, and plan availability. Does NOT cover: API or SDK parameters for artifact creation, how artifacts interact with multi-agent or dynamic workflow sessions, whether artifacts can be created from routines or headless sessions, cost model, or the relationship to Claude.ai's existing interactive artifacts feature.

## Extracted Claims

### Claim 1: Artifacts turn Claude Code session work into live, shareable visual pages that update as the session progresses

- **Evidence**: First-party feature description in the opening of the announcement, with four named artifact types enumerated.
- **Confidence**: emerging (first-party vendor feature description; beta status means behavior may change; no independent practitioner accounts yet)
- **Quote**: "Starting today, Claude Code can capture work progress as an artifact, which turn Claude Code's work into live, shareable visual pages— including PR walkthroughs, system explainers, dashboards, and release checklists—that update themselves as your session works."
- **Our assessment**: The "live" and "update themselves" properties distinguish Claude Code artifacts from static exports or shared transcripts. The page is not a frozen snapshot — it continues to reflect the session's ongoing work. This is the core enabling property for the team collaboration patterns (SRE incident response, PR walkthroughs) described in the post. The four named artifact types (PR walkthroughs, system explainers, dashboards, release checklists) are the primary templates Anthropic expects practitioners to reach for first.

### Claim 2: Artifacts use the full session context — codebase, connectors, and conversation — to generate their content without requiring separate data source setup

- **Evidence**: First-party architectural description of how artifacts are built, with explicit enumeration of the three context sources.
- **Confidence**: emerging (vendor architectural claim; mechanism described at a high level without implementation detail)
- **Quote**: "Claude Code builds an artifact using the full context of your session, including your codebase, your connectors, and the conversation itself."
- **Our assessment**: The three-part context model (codebase + connectors + conversation) is the key differentiator from a generic document tool. A practitioner does not need to manually copy findings into an artifact — the session context is implicit. The "connectors" element is particularly significant: connectors link Claude Code to external systems (Jira, Datadog, GitHub monitoring, Terraform, etc.); including connector context means an artifact can incorporate live data from those systems without the practitioner explicitly fetching it. This makes the SRE incident timeline pattern ("error spike from our monitoring") and FinOps resource mapping patterns feasible without separate data-wrangling steps.

### Claim 3: Artifacts render as interactive web pages — not plain text or files — with filterable dashboards and sortable views

- **Evidence**: Feature description with specific output format examples, including "filter and sort" interactivity.
- **Confidence**: settled (first-party feature description of output format and interaction model)
- **Quote**: "Artifacts translate the work into a web page anyone can open and explore, like a pull request walkthrough, a dashboard you can filter and sort, or even a release checklist"
- **Our assessment**: "A dashboard you can filter and sort" implies rich client-side interactivity, not a static HTML page. This positions artifacts as presentation-layer output rather than formatted text. "Anyone can open and explore" applies only to authenticated org members (Claim 5 clarifies this), but the UX is browser-native — no Claude Code installation required to view. This matters for the team collaboration use cases: reviewers who are not Claude Code practitioners can still interact with artifacts shared by the session owner.

### Claim 4: Live updates flow to teammates immediately upon publish; each publish creates a new versioned entry at the same URL with full version history and restore capability

- **Evidence**: First-party feature description with two specific properties: immediate live update and versioned history with restore.
- **Confidence**: emerging (vendor feature description; versioning behavior and restore specifics are stated but implementation details not provided)
- **Quote**: "When Claude Code updates an artifact, the open page refreshes in place and teammates see the updates the moment they're published. Every publish is a new version at the same link, with version history so you can restore at any time"
- **Our assessment**: The same-URL versioning model (publish → new version at same URL → viewer sees update immediately) is the correct design for collaborative review of evolving work. Stakeholders do not need to track down a new link when the practitioner reruns the session — the URL they already have updates in place. The version history restore capability ensures a bad publish can be rolled back. This is the mechanism behind the SRE incident-to-postmortem pattern: the same artifact URL tracks the incident as it unfolds, visible to the whole team without re-sharing. The "refreshes in place" behavior means teammates viewing the artifact at time of republish see the update without reloading.

### Claim 5: A gallery lets practitioners browse and manage all artifacts they have created across sessions

- **Evidence**: First-party feature description of the gallery UI as an artifact lifecycle management surface.
- **Confidence**: settled (first-party feature description; gallery is named as a specific UI component)
- **Quote**: "a gallery lets you browse and manage all artifacts you've made"
- **Our assessment**: The gallery is the cross-session management surface for artifacts. Without it, artifacts created in different sessions would be discoverable only by recalling or reconstructing their links. The gallery provides artifact discoverability across the practitioner's full history, making past work reusable and auditable. "Manage" implies CRUD-like operations (view, organize, possibly delete or archive) beyond browsing. For organizations building recurring artifact patterns (weekly team summaries, monthly audit pages), the gallery is the operational hub for managing that content library.

### Claim 6: Every artifact is private to its author by default; sharing is scoped to authenticated org members only and cannot be made public

- **Evidence**: First-party policy description with explicit "cannot be made public" statement.
- **Confidence**: settled (first-party policy statement; access control is a specific, verifiable product property)
- **Quote**: "Every artifact is private to its author by default. When you're ready, share it with your teammates and your organization directly from the page. Artifacts are viewable only by authenticated members of your org and cannot be made public."
- **Our assessment**: The "cannot be made public" constraint is an explicit privacy design choice — Claude Code artifacts are enterprise-scoped, not web-public. This makes them appropriate for sensitive use cases (legal audits, security findings, financial data) without requiring additional access control configuration by the practitioner. The "share from the page header" mechanism keeps sharing within the artifact's UX, not in external systems. For enterprise practitioners, the default-private model means no accidental exposure, but it also means external stakeholders (customers, regulators, auditors) cannot access artifacts without org membership, which may require additional workflows for regulated sharing.

### Claim 7: Admins control artifact access via org-level toggle, role-based scoping, retention policies, and compliance API visibility

- **Evidence**: First-party admin controls description with specific control mechanisms enumerated.
- **Confidence**: emerging (vendor feature description; four specific control types are named, increasing credibility above generic "admin controls" language; implementation detail like role definitions not described)
- **Quote**: "Admins manage access with an org-level toggle and role-based scoping, set retention policies, and get org-wide visibility through the compliance API"
- **Our assessment**: The four admin controls cover the enterprise governance needs for a content creation feature: (1) org-level toggle — enable/disable for the organization without per-user configuration, (2) role-based scoping — granular who-can-see-what beyond org-wide sharing, (3) retention policies — legal hold and data lifecycle management, (4) compliance API visibility — integration with existing audit and oversight tooling. The compliance API connection is particularly significant: it links artifacts into the same governance surface organizations already use for conversation audit trails, not a separate tool. This makes artifacts appropriate for regulated industries (legal, financial, healthcare) that require documented oversight of AI-generated content.

### Claim 8: Artifacts are invoked by natural language, not a special command or syntax

- **Evidence**: First-party feature description with explicit invocation description and informal alternative phrasing.
- **Confidence**: settled (first-party invocation description; the "just ask for something visual" alternative implies intent-based routing without keyword requirements)
- **Quote**: "Ask your session for an artifact — or just ask for something visual"
- **Our assessment**: The natural language invocation is the lowest-friction path to artifact creation. A practitioner does not need to learn a new command syntax — the same prompt interface that drives all Claude Code interaction also triggers artifact generation. The "or just ask for something visual" alternative framing suggests that even without the word "artifact," requests for visual output (a dashboard, a diagram, a checklist) may trigger the artifact output mode. This is consistent with Anthropic's broader design principle of intent-based invocation over command-based invocation across Claude Code features.

### Claim 9: Nine role-based use case prompt patterns cover legal, privacy, security, FinOps, engineering, design, architecture, SRE, and engineering management

- **Evidence**: Complete list of nine example prompts from the announcement, each scoped to a named role or function area.
- **Confidence**: emerging (Anthropic-documented patterns with verbatim example prompts; these represent use cases Anthropic tested or validated before including in the announcement)
- **Quote**: (see Concrete Artifacts section for all nine verbatim prompts)
- **Our assessment**: The nine patterns are the clearest signal of what Anthropic believes artifacts are well-suited for. They cluster around three task types: (1) compliance and audit work (legal, privacy, security, FinOps — all requiring connector data), (2) engineering collaboration and handoff (PR walkthroughs, architecture maps, incident response — codebase-grounded), and (3) team retrospectives and management status (engineering manager shipping summaries, design explorations). Patterns that do not require connectors (PR walkthroughs, code architecture maps) are likely the most accessible starting points for teams without extensive connector configuration.

### Claim 10: The SRE incident pattern exemplifies the live-update team collaboration workflow — a single artifact URL tracks an incident through resolution

- **Evidence**: Narrative scenario in the announcement describing a specific use case: an artifact shared at incident start, updated by Claude Code twice before standup.
- **Confidence**: emerging (vendor-described narrative scenario illustrating a specific feature behavior; not an independent practitioner case study)
- **Quote**: "she shares the link with her team from the page header. By the time standup begins, Claude has republished it twice as the investigation progressed"
- **Our assessment**: This is the clearest illustration of the live-update value proposition. The incident artifact is created during investigation, shared immediately via URL, and republished automatically as the session makes progress — all without the practitioner manually updating a document or re-sharing. The "By the time standup begins" timing makes the workflow concrete: the artifact is ready for team review at a predictable moment, not contingent on the practitioner manually preparing a status update. For on-call practitioners, this pattern replaces the "write up the incident doc" step that normally happens after resolution — the artifact evolves in real time during the investigation.

### Claim 11: Artifacts are available in beta to Claude Team and Enterprise orgs, accessible from Claude Code CLI and desktop app, with pages viewable in any browser

- **Evidence**: First-party availability statement from the announcement.
- **Confidence**: settled (first-party plan availability statement; beta is a formal designation with specific plan scope)
- **Quote**: "Artifacts is available in beta to Claude Team and Enterprise orgs, from the Claude Code CLI and desktop app, with pages viewable in any browser."
- **Our assessment**: Beta status means the feature is available but not API-stable. The "pages viewable in any browser" note is operationally important: while creation requires Claude Code (CLI or desktop app), consumption is browser-native. This means the entire team can benefit from artifacts as consumers even if only some members create them — a non-Claude-Code user can view a shared artifact without installing anything. The Pro and individual Max tiers are absent from the availability statement, making this a team/enterprise-first feature at launch.

## Concrete Artifacts

### Nine Role-Based Artifact Prompt Examples

```
Claude Code Artifacts: Role-Based Prompt Patterns
(Anthropic, "Claude Code now supports artifacts," June 18, 2026)
Source: https://claude.com/blog/artifacts-in-claude-code

LEGAL / OPEN SOURCE:
  "Build an artifact listing every third-party dependency and its license,
   flagging anything copyleft."
  Context needed: codebase (dependency files)
  Value: license audit without manual dependency inventory

PRIVACY:
  "Trace where we touch personal data across the codebase into an artifact
   for the privacy review."
  Context needed: codebase
  Value: data flow map for compliance reviews, codebase-grounded

SECURITY:
  "Build an artifact of the auth findings from this review, each linked
   to the code."
  Context needed: codebase + prior session conversation
  Value: finding report linked to specific code locations

FINOPS / PLATFORM FINANCE:
  "Map our cloud resources from the Terraform into an artifact, grouped
   by service, with the big cost drivers."
  Context needed: codebase (IaC) + connectors (cloud cost data)
  Value: infrastructure cost map from source; requires connector

SOFTWARE ENGINEERS:
  "Make an artifact walking through this PR — the diff, the reasoning,
   and what I tested."
  Context needed: codebase + conversation
  Value: PR walkthrough for review without inline comment spray

DESIGNERS & FRONTEND:
  "Give me an artifact with 5 UX variations of this signup form, built
   from our component library."
  Context needed: codebase (components)
  Value: design exploration grounded in real component code

STAFF ENGINEERS & ARCHITECTS:
  "Map how the payments service fits together into an artifact, from the code."
  Context needed: codebase
  Value: architecture map derived from actual code, not from memory

SRE & ON-CALL:
  "Turn this incident into an artifact — timeline, suspect commits,
   error spike from our monitoring."
  Context needed: codebase + connectors (monitoring, git history)
  Value: incident timeline auto-built from live data; URL the team
         follows in real time; republished as investigation progresses

ENGINEERING MANAGERS:
  "Build an artifact of what merged on my team this week from the PRs,
   grouped by project."
  Context needed: connectors (GitHub/version control)
  Value: shipping summary from PR history; no manual status notes needed
```

### Artifact Feature Reference

```
Claude Code Artifacts — Beta Feature Summary
(Anthropic, June 18, 2026)
Source: https://claude.com/blog/artifacts-in-claude-code

CREATION:
  Invocation:   "Ask your session for an artifact — or just ask for
                 something visual"
  Context:      Full session context (codebase + connectors + conversation)
  Entry point:  Claude Code CLI and desktop app

OUTPUT FORMAT:
  Type:         Interactive web page (dashboard, checklist, walkthrough)
  Examples:     "PR walkthroughs, system explainers, dashboards,
                 and release checklists"
  Interactivity: "a dashboard you can filter and sort"

SHARING & VERSIONING:
  Default:      Private to author
  Sharing:      "Share it with your teammates and your organization
                 directly from the page"
  Public:       "cannot be made public"
  Viewer auth:  "Artifacts are viewable only by authenticated members
                 of your org"
  Updates:      "the open page refreshes in place"
  Versioning:   "Every publish is a new version at the same link"
  History:      "with version history so you can restore at any time"
  Consumption:  "pages viewable in any browser" (no tool install required)

MANAGEMENT:
  Gallery:      "a gallery lets you browse and manage all artifacts
                 you've made"

ADMIN / COMPLIANCE:
  Toggle:       "org-level toggle"
  Scoping:      "role-based scoping"
  Retention:    "set retention policies"
  Audit:        "org-wide visibility through the compliance API"

AVAILABILITY:
  Status:       Beta
  Plans:        Claude Team and Enterprise
  Not yet:      Pro, individual Max
```

## Cross-References

- **Corroborates** `blog-anthropic-agent-view-claude-code.md` (Claim 7): That note documents "dashboard updaters" as a looping job pattern in agent view — sessions that update outputs over time, with their next run time surfaced in the agent view row list. Claude Code artifacts are the named output surface that such sessions update in real time: the session produces the artifact, republishes on update, and teammates see the change at the same URL. The two features compose cleanly: agent view manages the looping session's lifecycle and monitoring; the artifact captures and distributes its output. The SRE-standup scenario described in this source ("Claude has republished it twice as the investigation progressed") is a concrete instance of the "dashboard updater" pattern documented in agent view.

- **Extends** `blog-anthropic-claude-code-routines.md` (Claim 9): The routines note documents six use case patterns (backlog management, docs drift, deploy verification, alert triage, library porting, PR review). Artifacts provide a natural output surface for routines: a nightly docs-drift routine could publish its findings as an artifact at a stable URL; an alert triage routine could produce an artifact page with linked findings. This source introduces a shareable, live-updating output layer that complements the scheduling/triggering layer routines provide. Together: routines determine *when* work runs; artifacts determine *how* the output is shared with the team.

- **Extends** `blog-anthropic-claude-code-skills-lessons.md` (Claim 2, Business Process skill category): The skills note describes Business Process skills (standup-post, weekly-recap) that automate recurring coordination tasks, with Slack as the implied output channel. Claude Code artifacts provide an alternative output surface: instead of posting to Slack, a skill invocation could generate an artifact page that teams visit on their own schedule. The Engineering Manager prompt ("Build an artifact of what merged on my team this week from the PRs, grouped by project") is the artifact-output version of the weekly-recap skill pattern from that note.

- **Corroborates** `blog-anthropic-compliance-api-security-partners.md`: The compliance API is referenced here as the admin governance surface for artifacts ("get org-wide visibility through the compliance API"). This corroborates the compliance API's role as a cross-feature organizational oversight mechanism — it covers not only conversation monitoring but also AI-generated output pages. The prior compliance API note covers the conversation-level use; this source extends the governed surface to artifact content.

- **Contradicts**: None found. A terminology collision exists between "Claude Code artifacts" (live web pages from session context, this source) and "GHAW artifacts" (`docs-ghaw-artifacts-reference.md`: workflow build output files produced by GitHub Agentic Workflow runs). These are structurally different concepts that share a name — not a factual contradiction. No contradiction issue required, but the guide should distinguish these explicitly.

- **Novel**:
  - **Live-updating, URL-stable web pages as a Claude Code output primitive**: No prior corpus source describes a persistent, URL-stable, live-updating output surface for Claude Code sessions. Prior session output patterns are static (files written to disk, PRs opened, Slack messages posted). Artifacts introduce a fourth output category: live collaborative web pages that evolve with the session.
  - **Session context (codebase + connectors + conversation) as the implicit input to shareable output**: The integration of connector data into artifact content (monitoring data for SRE timelines, Terraform for FinOps maps) without explicit data-fetching steps is a novel pattern. Prior sources treat connectors as in-session context only; this is the first to surface connector data as externally shareable output.
  - **Nine-role artifact prompt library**: No prior corpus source provides a named role-based taxonomy of output-sharing patterns with verbatim prompt examples. These nine patterns constitute the first practitioner reference for artifact-driven workflows.
  - **Version history + gallery for artifact lifecycle management**: No prior source describes a versioned artifact history at a stable URL, or a gallery for cross-session artifact management. Artifact lifecycle management is a new harness engineering concern introduced here.
  - **Compliance API extended to cover AI-generated output pages**: Prior compliance API coverage in the corpus addresses conversation-level governance. This is the first source establishing artifacts as a distinct content type with compliance API integration.
  - **Browser-viewable team output without tool installation**: The "pages viewable in any browser" property enables non-practitioners (stakeholders, reviewers, managers) to consume session output without having Claude Code installed. Prior output surfaces (code changes, PRs) require repository access; artifacts require only a browser and org authentication.

## Guide Impact

- **Chapter 01 (Daily Workflows)**: Add a "Sharing session output with artifacts" section documenting the nine role-based patterns. Artifacts are the recommended path for sharing findings from Claude Code sessions with teammates who are not in the same session — replacing the "screenshot and paste into Slack" workflow. The SRE incident pattern is the strongest illustration of live-update value: one URL, auto-updating, visible to the whole team without re-sharing. Note the "session context as input" property: a practitioner does not need to manually compile information — codebase and connector data feed the artifact automatically.

- **Chapter 01 (Daily Workflows)**: Add the artifact gallery as a session-output management primitive. For practitioners running multiple sessions across projects, the gallery is how prior session outputs are rediscovered and reused. This is the first corpus-documented mechanism for finding past Claude Code session outputs without searching through terminal history.

- **Chapter 02 (Harness Engineering)**: Document artifacts as the output layer in a complete session stack: context engineering (CLAUDE.md + skills) → session execution (auto mode + agent view) → output (artifacts). Prior sources covered the first two layers; artifacts complete the picture with a first-class output surface. The harness designer's decision is now: which Claude Code session output type fits the task — file writes (code changes), PRs (code review), or artifacts (human-readable deliverables for team sharing)?

- **Chapter 02 (Harness Engineering) — Enterprise governance**: The admin controls (org toggle, role scoping, retention, compliance API) add a governance layer to the artifact output surface. For organizations deploying Claude Code to regulated teams (legal, finance, security), artifact governance should be planned alongside session permission governance (auto mode) and connector governance (data source access). Add to the enterprise deployment checklist: configure artifact retention policy and compliance API access before enabling artifacts for regulated teams.

- **Chapter 04 (Team Collaboration)**: The artifact-as-team-handoff pattern (create artifact → share URL → team reviews async → session republishes as work progresses) is the primary team collaboration workflow this feature enables. The SRE standup example should anchor this section. Contrast with prior "share a file" patterns: artifacts provide URL-stable, live-updating content that teams return to without re-sharing, while files require re-distribution on every update.

- **Chapter 02 (Harness Engineering) — Terminology clarification**: Add a note distinguishing Claude Code artifacts (live web pages from session context, this source) from GHAW artifacts (workflow build output files, `docs-ghaw-artifacts-reference.md`). These share a name but are structurally different: Claude Code artifacts are browser-viewable pages, not downloadable build products. Practitioners familiar with GitHub Actions artifacts may have incorrect expectations.

## Extraction Notes

- The source is a product announcement blog post (June 18, 2026). The WebFetch tool would not reproduce the full verbatim article text; all quotes were gathered via targeted WebFetch requests for specific sections, with explicit verbatim quotation marks requested. The Assayer should spot-check all quotes against the live URL at https://claude.com/blog/artifacts-in-claude-code.
- The nine use case prompts were confirmed by two separate WebFetch requests with consistent results. They appear to be verbatim prompts embedded in the article as examples. They are reproduced verbatim in the Concrete Artifacts section.
- The SRE standup narrative quote ("she shares the link with her team from the page header. By the time standup begins, Claude has republished it twice as the investigation progressed") comes from a story-format section of the article. Spot-check its verbatim accuracy against the live URL.
- The blog post does not mention how Claude Code artifacts relate to Claude.ai's existing interactive artifacts feature. One WebFetch request explicitly confirmed this omission. This is a scope gap, not a factual conflict — no contradiction issue filed.
- No contradiction with existing corpus notes was found. The GHAW artifacts naming collision (`docs-ghaw-artifacts-reference.md`) is a terminology note, not a factual contradiction.
- Confidence set to `emerging`: first-party Anthropic product announcement for a shipping beta feature. High authority for what the feature does; beta status means specific behaviors (versioning details, gallery operations, admin control specifics) may change before general availability.
