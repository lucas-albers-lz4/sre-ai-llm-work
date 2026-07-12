---
source_url: https://incident.io/blog/how-it-feels-to-run-an-incident-with-ai-sre
source_type: blog-post
title: "How it feels to run an incident with AI SRE"
author: "incident.io (uncredited author; first-person narrative by an incident.io team member who has responded to hundreds of incidents)"
date_published: 2026-04-23
date_extracted: 2026-07-12
last_checked: 2026-07-12
status: current
confidence_overall: anecdotal
issue: "#3"
---

# How it feels to run an incident with AI SRE

> A first-person practitioner narrative from incident.io describing an end-to-end
> AI-assisted incident response: from declaration through AI SRE investigation,
> Claude Code fix authoring, MCP-driven Slack updates, and AI-generated debrief
> write-ups. Documents concrete human-AI collaboration patterns (parallel
> investigation, reverification loop, multi-surface orchestration) with
> screenshots of each stage. Published April 2026 — the product described has
> not yet launched, making this a pre-release design validation rather than
> production evidence. Also draws on the linked `ai-sre-agent-definition` page
> (January 2026) for capability claims and implementation guidance.

## Source Context

- **Type**: blog-post (vendor practitioner writeup)
- **Author credibility**: The author is an incident.io team member who writes in
  first person, has "responded to hundreds of incidents" over their career, and
  has been building the incident.io platform for several years. They have
  first-hand experience with the AI SRE product they describe (18 months of
  development, internal dogfooding). However, the article does not credit a
  named author, and the product is pre-launch — the narrative describes an
  internal incident on incident.io's own infrastructure, not a customer
  incident. This is a vendor narrative with an inherent promotional angle.
- **Scope**: Covers one complete incident lifecycle — a frontend rendering crash
  caused by a type mismatch in a new escalation-path feature. Walks through
  declaration, AI SRE autonomous investigation, desktop app pinning, Claude Code
  integration via `/incident` command, fix authoring, MCP-driven PR and channel
  update, reverification, deploy, wrap-up, and AI-generated debrief. Also covers
  UX philosophy ("better to be right than first") and acknowledges the product
  is not yet launched. The linked `ai-sre-agent-definition` page (January 2026)
  adds capability taxonomy, implementation guidance, and cost-of-downtime
  citations. Does NOT cover: internal agent architecture, model selection,
  evaluation metrics, failure cases where AI SRE was wrong, pricing, or
  security/auth details for the MCP integration.

## Extracted Claims

### Claim 1: AI SRE autonomously begins multi-source investigation immediately upon incident declaration, checking deploys, telemetry, errors, past incidents, code, and Slack context in parallel
- **Evidence**: Described as built-in system behavior triggered by declaration;
  corroborated by screenshots showing investigation results in the incident
  channel. The author contrasts this with what a human would do sequentially.
- **Confidence**: emerging
- **Quote**: "All the kinds of things a human would do if they were responding
  to an incident themselves, but much faster and in parallel."
- **Our assessment**: The investigation surface is plausible — these are exactly
  the data sources a human responder would check. The "parallel" claim is
  asserted but not measured. No latency or coverage data provided. The claim
  is credible as a capability description but unvalidated as a performance
  claim.

### Claim 2: The `/incident INC-NNN` slash command in Claude Code synchronizes AI SRE investigation context directly into the terminal session, allowing the responder to pick up where the agent left off without manual context transfer
- **Evidence**: Screenshot showing the command being executed in Claude Code;
  the author states this connected their session "directly back into the
  incident" with all investigation context synchronized. The linked
  `ai-sre-agent-definition` page confirms Slack-native operation and tool
  integration as core design principles.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is one of the most concrete and novel patterns in
  the source. The context-bridging mechanism between an autonomous agent (AI
  SRE) and an interactive coding agent (Claude Code) via a simple CLI command
  is a practical integration pattern worth tracking. The article does not
  describe the underlying implementation (how context is serialized, what
  protocol is used, whether this is MCP-based or custom).

### Claim 3: Human responders and AI agents can investigate independently in parallel, with automatic context synchronization keeping both aligned as new findings emerge
- **Evidence**: Described as designed system behavior. The author worked in
  Claude Code while AI SRE continued investigating in the background; "as new
  intel comes in, we automatically connect the dots, keeping both agents
  aligned." The linked `ai-sre-agent-definition` page frames this as reducing
  the "coordination tax" — the ~15 minutes of a median 48-minute MTTR spent on
  team assembly and context sharing.
- **Confidence**: emerging
- **Quote**: "let responders and Claude move ahead and investigate
  independently"
- **Our assessment**: This pattern — parallel independent investigation with
  automatic context sync — addresses a key failure mode identified in the
  PagerDuty SRE Agent architecture source note (see Cross-References). The
  PagerDuty team identified that single-agent sequential execution left the
  agent "operating without information the human already had." incident.io's
  approach inverts this: the human and agent each work independently, and
  context syncs bidirectionally. The claim is plausible but demonstrated only
  through a single ideal-run narrative.

### Claim 4: AI SRE implements a reverification loop — every Claude action posted back to the incident channel is rechecked, and the agent nudges the responder on mistakes or omissions
- **Evidence**: Described behavior; no specific example of a caught mistake is
  provided. The author frames this as a safety mechanism that removes the need
  to "blindly trust" the AI's output.
- **Confidence**: anecdotal
- **Quote**: "everything you do in Claude and post back to the channel gets
  reverified by AI SRE. If you've made a mistake or forgotten something, it'll
  nudge you about it."
- **Our assessment**: The reverification loop is a novel safety pattern — it
  treats the human-AI collaboration as adversarial enough to warrant double-
  checking, but cooperative enough to make the double-check automatic and
  non-blocking. However, without examples of actual caught mistakes, we can't
  assess the sensitivity or specificity of this mechanism. The article
  presents an ideal run where no mistakes were caught, which leaves the
  reverification's practical value unproven.

### Claim 5: Claude Code, via incident.io MCP integration, can open a GitHub PR and post a structured incident-channel update (findings, fix description, PR link) without the responder leaving the terminal
- **Evidence**: Screenshots of terminal output showing the PR creation prompt
  and the resulting Slack channel update. The author states they never opened
  GitHub or switched to Slack. The linked `ai-sre-agent-definition` page
  describes PR generation as a core AI SRE capability.
- **Confidence**: emerging
- **Quote**: "All of it happened from the same place I was writing the fix."
- **Our assessment**: This is the most concrete demonstration of MCP value in
  the source. The pattern — Claude Code authoring a fix, committing, opening a
  PR, and posting a Slack update via MCP, all within the terminal — represents
  a genuinely reduced-tool-switching workflow. However, no MCP server
  configuration, tool schema, or authentication details are provided, limiting
  reproducibility. The claim is credible as a capability demonstration but
  cannot be independently replicated from the article alone.

### Claim 6: The incident.io macOS desktop app uses the Mac notch as a persistent, live incident view that provides passive situational awareness without requiring the responder to actively check multiple tools
- **Evidence**: Screenshot showing the pinned incident in the desktop app
  integrated with the Mac notch. The author describes it as "pinging me with
  updates" and keeping them "always plugged into the latest context without
  having to go looking for it."
- **Confidence**: anecdotal
- **Quote**: "the incident.io desktop app is sitting there on my Mac, pinging
  me with updates"
- **Our assessment**: The "pin to notch" pattern is a UX innovation specific
  to macOS, but the underlying principle — a persistent, ambient incident
  awareness surface that doesn't require active polling — is generalizable.
  This addresses the context-switching overhead that the author identifies as
  the core friction of traditional incident response. The claim is novel but
  supported only by a single screenshot and self-reported experience.

### Claim 7: The complete AI-assisted incident lifecycle — declaration through investigation, fix, PR, deploy, wrap-up, and debrief — took "minutes, and most of that was waiting for the deploy"
- **Evidence**: Self-reported time estimate with no stopwatch data. The
  incident involved a frontend rendering crash (a `map` returning `undefined`
  for an unrecognized type) in a feature the author had "zero familiarity"
  with. The linked `ai-sre-agent-definition` page asserts that teams "can
  reduce incident MTTR by up to 80%" but provides no primary data for this
  figure.
- **Confidence**: anecdotal
- **Quote**: "The whole process here, from incident declaration to resolution,
  took minutes. And most of that was waiting for the deploy."
- **Our assessment**: This is the headline claim of the article and also the
  weakest evidentially. "Minutes" is imprecise; "most of that was waiting for
  the deploy" is unfalsifiable without actual timing. The incident was also a
  relatively simple bug (type mismatch causing a render crash) in the author's
  own company's product, with full tooling integration already in place. This
  does not generalize to complex multi-service incidents, incidents requiring
  infrastructure changes, or incidents in organizations without the same
  integration maturity. Treat as an existence proof, not a benchmark.

### Claim 8: AI SRE can generate a fully AI-written structured incident write-up that incorporates context from Slack, Zoom/Google Meet transcripts, and coding session activity, serving as a foundation for team debriefs
- **Evidence**: Screenshot of the generated write-up. The linked
  `ai-sre-agent-definition` page describes post-mortem drafting as a core
  capability, noting that Scribe records and transcribes incident calls in
  real time, capturing "key moments, important decisions, and next steps."
- **Confidence**: emerging
- **Quote**: "entirely AI-generated"
- **Our assessment**: Multi-source context incorporation (Slack + video
  transcripts + coding activity) into a single structured write-up is a
  non-trivial integration claim. The generated write-up is shown in a
  screenshot and appears coherent, but we cannot assess accuracy or
  completeness from a single example. The debrief framework page linked from
  the article (`a-seven-step-framework-for-running-incident-debriefs`, March
  2025) contains no reference to AI SRE integration, suggesting the AI
  write-up feature post-dates or exists separately from their human debrief
  methodology.

### Claim 9: Incident wrap-up is reduced to a one-liner Slack command (`@incident`) that triggers AI SRE to incorporate all incident context and close out the incident
- **Evidence**: Screenshot showing the `@incident` command and the agent's
  response. The author calls this "as simple as a one-liner."
- **Confidence**: emerging
- **Quote**: "as simple as a one-liner to ask @incident to take care of it"
- **Our assessment**: The one-liner wrap-up is a compelling simplicity claim,
  but it likely only works for incidents where all resolution steps have
  already been completed (PR merged, deploy shipped, re-test confirmed). The
  article's incident had a clean linear resolution; multi-responder incidents
  with partial resolutions, follow-up items, or disputed root causes may not
  reduce to a one-liner. This is a best-case demonstration.

### Claim 10: The traditional friction in incident response is tool fragmentation and context switching — "too many tools, too much context switching, too much time spent just figuring out what's going on before you can start fixing it" — and AI SRE addresses this by consolidating investigation, fix authoring, communication, and wrap-up into a unified flow
- **Evidence**: Author's stated experience from responding to "hundreds of
  incidents" over their career. The article demonstrates five tool surfaces
  (Slack, desktop app, Claude Code terminal, GitHub, incident.io) orchestrated
  into a flow where the responder only actively interacts with the desktop app
  and Claude Code terminal.
- **Confidence**: settled
- **Quote**: "too many tools, too much context switching, too much time spent
  just figuring out what's going on"
- **Our assessment**: The problem statement — tool fragmentation in incident
  response — is well-established and uncontroversial. The source's
  contribution is demonstrating a concrete integration pattern that addresses
  it, not identifying the problem itself. The five-surface orchestration
  (Slack → desktop → Claude Code → GitHub → Slack) is more surfaces than
  ideal, but the claim is that the responder only actively touches two of them
  (desktop app for awareness, Claude Code for action).

### Claim 11: The product has not launched and the UX is still being refined, with the team explicitly prioritizing correctness and UX quality over speed to market
- **Evidence**: Explicit statements in the article. The author acknowledges 18
  months of development, describes the UX as having been "jarring and easy to
  move past" in earlier iterations, and says they are "right on the edge of
  nailing the whole flow."
- **Confidence**: settled
- **Quote**: "We've still got a little way to go (which is why we haven't
  fully launched yet!)"
- **Our assessment**: This is a rare instance of a vendor blog post explicitly
  stating the product is pre-launch. It materially affects how we should weigh
  all other claims: this is a design validation, not production evidence. The
  candor is credibility-enhancing but also means every claim should be
  treated as aspirational until confirmed by post-launch evidence.

### Claim 12: Defining an AI SRE agent requires distinguishing it from both traditional runbook automation (which follows rigid scripts) and AIOps (which stops at recommendations without taking action)
- **Evidence**: From the linked `ai-sre-agent-definition` page (January 2026).
  The page defines AI SRE agents as systems that "perceive their environment,
  reason, plan, and execute multi-step tasks" autonomously, contrasting with
  runbook automation that "waits for a trigger and follows rigid scripts" and
  AIOps that provides "recommendations and insights but stops short of
  action."
- **Confidence**: emerging
- **Quote**: "An AI SRE agent is a software system that combines observability
  data, reasoning capabilities, and action execution to autonomously manage
  reliability tasks."
- **Our assessment**: This definition is useful for situating the source in
  the broader taxonomy of reliability automation. The runbook-vs-AIOps-vs-AI-
  agent distinction is a reasonable three-tier framing, though the boundaries
  are blurry in practice (many AIOps tools now include action execution). The
  definition is vendor-authored and serves the product's positioning, but the
  distinctions are analytically sound.

## Concrete Artifacts

### End-to-end incident workflow (as described and screenshot'd in the article)

```
1. TRIGGER:       Feature test → full page crash → blank error screen
2. DECLARATION:   Author declares incident (per "declare early, declare often")
3. INVESTIGATION: AI SRE autonomously kicks off parallel investigation:
                  - Recent deploys
                  - Telemetry and errors
                  - Past incidents (pattern matching)
                  - Code (smoking guns)
                  - Slack context
4. DESKTOP PIN:   Slack nudge → pin incident to macOS desktop app
                  → Mac notch becomes live incident view
5. CLAUDE SYNC:   `/incident INC-19672` in Claude Code
                  → investigation context synced into terminal session
6. FINDINGS:      AI SRE identifies: frontend crash, `map` returning
                  `undefined` for unrecognized type; recurring cross-team
                  type-mismatch pattern surfaced
7. VALIDATION:    Claude validates finding against OpenAPI spec in codebase
8. FIX:           Claude proposes graceful skip instead of crash
9. PR + UPDATE:   Claude commits, opens PR, uses incident.io MCP to post
                  channel update (findings + fix + PR link)
10. REVERIFY:     AI SRE rechecks everything Claude posted; nudges if needed
11. DEPLOY:       PR merged → fix deployed
12. RE-TEST:      Engineer messages author to re-test → confirmed fixed
13. WRAP-UP:      `@incident` one-liner in Slack → AI SRE closes incident,
                  incorporating Slack + Zoom/Meet + coding session context
14. DEBRIEF:      AI SRE generates structured write-up (entirely AI-generated)
```

### CLI command: Incident context sync into Claude Code

```
/incident INC-19672
```

Connects the Claude Code session to the specified incident, synchronizing
all AI SRE investigation context. Described in the article with an
accompanying screenshot of the Claude Code terminal.

### Slack command: Incident wrap-up

```
@incident
```

One-liner Slack command that triggers AI SRE to incorporate all incident
context (Slack, Zoom/Google Meet transcripts, coding session activity) and
close out the incident. Shown in a screenshot.

### AI SRE autonomous investigation checklist (from the article)

As described, AI SRE checks these data sources upon incident declaration:

- Recent deploys
- Telemetry and error logs
- Past incidents (similarity/pattern matching)
- Code changes (smoking guns)
- Slack context (relevant channel discussions)

### MCP integration point (described but not configured)

Claude Code used "the incident.io MCP to post an update into the incident
channel, including what was found, what the fix is, and a link to the PR."
No MCP server configuration, tool schema, endpoint, or authentication
details are provided in the article.

### Four-step AI SRE implementation path (from linked `ai-sre-agent-definition` page, January 2026)

```
1. Centralize data via a service catalog
   → Capture ownership, dependencies, runbook locations, recent deploys
   → Connect to GitHub, Jira, monitoring tools

2. Integrate existing tools
   → Observability: Datadog, Prometheus, New Relic
   → CI/CD: GitHub, Jenkins
   → Communication: Slack, Microsoft Teams

3. Start with human-in-the-loop
   → Approval required for self-healing actions
   → All automated steps logged and reversible

4. Gradually expand automation
   → Safe runbooks first: restart containers on resource issues,
     scale clusters on saturation, roll back deploys on error rate spikes
```

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 5): PagerDuty identifies
    that "lack of interactivity during agent execution was a structural
    failure" — the agent operating without information the human already had.
    The incident.io article demonstrates a design response to this failure
    mode: the human and AI investigate in parallel, context syncs
    bidirectionally, and the AI SRE's reverification loop catches human
    mistakes. Same problem, different design solution.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 10): PagerDuty's
    priority queue pattern (user input = priority 0, sub-agent results =
    priority 1) and the incident.io parallel investigation pattern both treat
    human input as a first-class event that must not be blocked by agent
    execution. Different implementations, same principle.

- **Contradicts**: None identified. The PagerDuty source covers internal agent
  architecture (multi-agent, reactive loops, LangGraph primitives); the
  incident.io source covers user-facing interaction design and multi-surface
  orchestration. They operate at different layers of the stack and are
  complementary.

- **Extends**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 6, the three execution
    models): The PagerDuty article argues that concurrent fan-in is required
    for real-time visibility in incident investigation. The incident.io
    article demonstrates a UX-level implementation of concurrent operation:
    AI SRE and Claude Code working in parallel with automatic context sync.
    This extends the architectural principle into a concrete product
    interaction pattern.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 16, "build hard, ship
    simple"): The incident.io article's explicit "better to be right than
    first" philosophy and 18-month development cycle (with pre-launch
    dogfooding) parallel the PagerDuty team's methodology of building the
    complex version first to understand essential primitives.

- **Novel**: The following patterns are new to the corpus and not covered by
  the existing PagerDuty source note:
  - **Multi-surface orchestration**: Slack → desktop app → Claude Code CLI →
    GitHub PR → Slack channel update, all within a single incident flow without
    the responder switching tools. This is a concrete demonstration of MCP's
    value proposition (Claude Code posting to Slack via incident.io MCP).
  - **The reverification loop**: AI SRE rechecking everything Claude posts
    back to the incident channel and nudging on mistakes. A safety pattern
    that treats human-AI collaboration as warranting automated double-checks.
  - **The "pin to notch" ambient awareness pattern**: A persistent desktop
    surface for incident context that provides passive updates without active
    polling. The macOS-specific implementation is not generalizable, but the
    principle (ambient incident awareness) is.
  - **The `/incident` context-sync command**: A CLI command that bridges an
    autonomous investigation agent's context into an interactive coding agent.
    This is a specific integration pattern between two different AI agents
    (AI SRE and Claude Code).
  - **One-liner incident wrap-up**: Reducing incident closeout to a single
    Slack command with AI handling all context incorporation and write-up
    generation.

## Guide Impact

- **Chapter 01 (Incident Response)**: This source provides evidence for a
  specific AI-assisted incident response pattern: parallel human-agent
  investigation with bidirectional context sync. Current guide content (if
  any) should consider adding: (a) the pattern of declaring an incident and
  having AI begin autonomous investigation immediately — this changes the
  "first responder" role from investigator to verifier; (b) the reverification
  loop as a safety mechanism — AI double-checking human-AI collaboration
  output; (c) the end-to-end lifecycle timing claim (minutes, not hours) as an
  aspirational benchmark, with the caveat that the product is pre-launch.

- **Chapter 03 (Runbooks and Agents)**: This source provides concrete patterns
  for agent-to-agent and agent-to-tool integration: (a) the `/incident` CLI
  command as a context-bridging mechanism between autonomous and interactive
  agents — a pattern worth recommending for any multi-agent incident toolchain;
  (b) MCP-based channel updates from within Claude Code as a demonstration of
  terminal-to-Slack integration without context switching; (c) the four-step
  implementation path from the linked definition page (service catalog →
  tool integration → human-in-the-loop → gradual automation) as a pragmatic
  adoption sequence.

- **Chapter 04 (On-call and Toil)**: This source provides evidence for: (a)
  the "coordination tax" concept — the ~15 minutes of a 48-minute median MTTR
  spent on team assembly and context sharing — as a quantifiable target for
  AI-assisted reduction; (b) the ambient awareness pattern (desktop app with
  passive updates) as a way to reduce the cognitive overhead of actively
  monitoring multiple tools during an incident; (c) the one-liner wrap-up
  pattern as toil reduction for incident closeout and debrief preparation.
  All claims should be caveated with the source's pre-launch status.

## Extraction Notes

- The primary source is a single long-form blog post on incident.io's blog.
  Three linked pages were followed per MINER.md §1:
  1. `ai-sre-agent-definition` (January 2026) — substantive; contributed
     Claims 12 and the four-step implementation path in Concrete Artifacts.
  2. `declare-early-declare-often` (June 2022) — pre-AI, lightweight; not
     substantively extracted (the "declare early" principle is referenced
     in the main article but adds no new AI-specific claims).
  3. `a-seven-step-framework-for-running-incident-debriefs` (March 2025) —
     contains no AI SRE integration references; not extracted. The disconnect
     between this framework article (no AI) and the main article's claim of
     AI-generated debriefs is noted in Claim 8's Our assessment.
  Two additional linked pages (`introducing-ai-sre`, July 2025; `what-is-ai-
  sre-complete-guide-2026`) were not fetched — the definition page plus the
  main article provided sufficient coverage.

- The article credits no named author. The first-person narrative and
  references to "we" (the incident.io product team) suggest the author is a
  senior team member or co-founder with direct product involvement. The lack
  of attribution reduces author credibility slightly but the article's value
  is in its concrete workflow description and screenshots, not the author's
  individual authority.

- Quotes were extracted via WebFetch and spot-checked for consistency across
  two independent fetches of the same URL. Short quotes (≤125 characters) are
  likely verbatim; the Assayer should verify any quotes used in guide chapters
  against the live URL. Longer descriptive passages are attributed as
  paraphrases per MINER.md §2a.5.

- The source is rich in screenshots (10 images) but provides no raw code,
  no MCP configuration, no quantitative metrics, and no failure cases. The
  article presents exactly one incident — a successful, linear resolution of
  a relatively simple frontend bug. This limits generalizability.

- The product is explicitly pre-launch. All claims should be read as design
  validation from internal dogfooding, not as production evidence. The
  confidence_overall of "anecdotal" reflects both the vendor source and the
  pre-launch status.

- No part of the source was paywalled. All linked pages are publicly
  accessible on the incident.io blog.
