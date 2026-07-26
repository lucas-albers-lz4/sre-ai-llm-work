---
source_url: https://incident.io/blog/how-it-feels-to-run-an-incident-with-ai-sre
source_type: blog-post
title: "How it feels to run an incident with AI SRE"
author: "incident.io (uncredited author; first-person narrative by an incident.io team member who has responded to hundreds of incidents)"
date_published: 2026-04-23
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: anecdotal
issue: "#3-deepseek-v4-flash-free-eval"
---

# How it feels to run an incident with AI SRE (eval: deepseek-v4-flash-free)

> A first-person practitioner narrative from incident.io documenting a
> single AI-assisted incident lifecycle. Describes parallel investigation
> between an autonomous AI SRE agent and a human responder in Claude Code,
> context bridging via a CLI command, MCP-driven tool orchestration, and
> AI-generated wrap-up. Published April 2026 as a pre-launch design
> validation.

## Source Context

- **Type**: blog-post (vendor practitioner writeup)
- **Author credibility**: Uncredited incident.io team member writing in first
  person, claims "hundreds of incidents" of experience and several years of
  building the platform. Has 18 months of direct involvement with the
  Investigations product. No named author reduces accountability. The
  narrative describes an internal incident on incident.io's own infrastructure,
  not a customer incident. The product is pre-launch, making this a dogfooding
  report rather than shipped-production evidence.
- **Scope**: Covers one incident lifecycle end-to-end: declaration, AI SRE
  autonomous investigation, desktop app pinning, Claude Code integration via
  `/incident`, fix authoring, MCP-based PR and Slack channel update,
  reverification, deploy, wrap-up, and AI-generated debrief. Includes UX
  philosophy and explicit pre-launch caveats. Does NOT cover: internal agent
  architecture, model selection, evaluation metrics, failure cases where the
  AI was wrong, pricing, or MCP configuration details.

## Extracted Claims

### Claim 1: AI SRE begins multi-source parallel investigation automatically upon incident declaration — checking deploys, telemetry, errors, past incidents, code, and Slack context
- **Evidence**: Described as system behavior with screenshots of investigation
  results in the incident channel. The author contrasts this with sequential
  human investigation.
- **Confidence**: emerging
- **Quote**: "All the kinds of things a human would do if they were responding
  to an incident themselves, but much faster and in parallel."
- **Our assessment**: The listed investigation surfaces (deploys, telemetry,
  past incidents, code, Slack) are exactly what a human responder would check.
  The parallel-execution claim is asserted without latency or coverage
  measurements. Plausible as a capability description; unvalidated as a
  performance claim.

### Claim 2: The `/incident INC-NNN` slash command in Claude Code synchronizes AI SRE investigation context into the terminal, eliminating manual context transfer between agents
- **Evidence**: Screenshot of the command in Claude Code. The author states
  this connected "my Claude Code session directly back into the incident, and
  synchronizing all of the investigation from Investigations into the context."
- **Confidence**: emerging
- **Quote**: "I jumped into Claude Code with the `/incident INC-19672` command,
  connecting my Claude Code session directly back into the incident, and
  synchronizing all of the investigation from Investigations into the context."
- **Our assessment**: This is a novel integration pattern between an autonomous
  investigation agent (AI SRE) and an interactive coding agent (Claude Code).
  The CLI-based context bridge is simple and practical. The article does not
  describe the underlying serialization protocol, whether this uses MCP, or
  how conflicts between agent contexts are resolved.

### Claim 3: Human responders and AI agents can investigate independently in parallel, with automatic context synchronization keeping both aligned as new findings emerge
- **Evidence**: Described as a designed system behavior. The author worked in
  Claude Code while AI SRE continued investigating in the background.
- **Confidence**: emerging
- **Quote**: "A subtle but important point in this flow is that it lets
  responders and Claude move ahead and investigate independently, exploring
  while Investigations continues in parallel behind the scenes."
- **Our assessment**: This addresses a key failure mode identified in the
  PagerDuty SRE Agent architecture — single-agent sequential execution where
  the agent "operates without information the human already had." The
  incident.io approach inverts this: human and agent work independently,
  context syncs bidirectionally. Plausible but demonstrated through a single
  ideal-run narrative with no reported conflicts.

### Claim 4: AI SRE implements a reverification loop — every Claude action posted to the incident channel is rechecked, and the agent nudges the responder on mistakes
- **Evidence**: Described as system behavior. No concrete example of a caught
  mistake is provided in the article.
- **Confidence**: anecdotal
- **Quote**: "It's worth calling out that everything you do in Claude and post
  back to the channel gets reverified by Investigations. If you've made a
  mistake or forgotten something, it'll nudge you about it, but it'll also
  update its understanding and ensure anyone in the channel knows what you did
  and where we landed."
- **Our assessment**: The reverification loop is a novel safety pattern that
  treats the human-AI collaboration as warranting automated double-checks.
  However, the article presents an incident where no mistakes were caught,
  so we cannot assess the mechanism's sensitivity, specificity, or practical
  value. This remains a design claim.

### Claim 5: Claude Code, via incident.io MCP integration, opens a GitHub PR and posts a structured incident-channel update (findings, fix, PR link) without the responder leaving the terminal
- **Evidence**: Screenshots of terminal output showing the PR creation and the
  resulting Slack channel update. The author states no tool switching occurred.
- **Confidence**: emerging
- **Quote**: "Most notably, I didn't have to switch to Slack to type an update.
  I didn't open GitHub to create the PR. I didn't go back to incident.io to
  change the status. All of it happened from the same place I was writing the
  fix."
- **Our assessment**: This is the strongest concrete demonstration of MCP value
  in the source. The pattern — fix authoring, commit, PR creation, and Slack
  update all from the terminal — represents genuine tool-switching reduction.
  No MCP server configuration, tool schema, or authentication details are
  provided, limiting reproducibility.

### Claim 6: The incident.io macOS desktop app uses the Mac notch as a persistent, live incident view providing passive situational awareness
- **Evidence**: Screenshot of the pinned incident in the desktop app. The
  author describes receiving automated updates.
- **Confidence**: anecdotal
- **Quote**: "the incident.io desktop app is sitting there on my Mac, pinging
  me with updates as things progress. So I'm always plugged into the latest
  context without having to go looking for it."
- **Our assessment**: The "pin to notch" pattern is a macOS-specific UX
  innovation, but the underlying principle — ambient incident awareness
  without active polling — is generalizable. This addresses the context-switch
  overhead identified as the core friction of traditional incident response.
  Single-screenshot evidence only.

### Claim 7: The complete AI-assisted incident lifecycle — declaration through fix, PR, deploy, wrap-up, and debrief — took "minutes, and most of that was waiting for the deploy"
- **Evidence**: Self-reported time estimate without stopwatch data or
  timestamps. The incident was a frontend rendering crash in the author's own
  company's product.
- **Confidence**: anecdotal
- **Quote**: "The whole process here, from incident declaration to resolution,
  took minutes. And most of that was waiting for the deploy."
- **Our assessment**: This is the article's headline claim and its weakest
  evidentially. "Minutes" is imprecise; "most of that was waiting for the
  deploy" is unfalsifiable. The incident was a simple type-mismatch bug in the
  author's own product with full integration. Does not generalize to complex
  multi-service incidents or organizations without equivalent tooling maturity.
  Treat as an existence proof, not a benchmark.

### Claim 8: AI SRE generates an entirely AI-written structured incident write-up incorporating Slack, Zoom/Google Meet transcripts, and coding session context
- **Evidence**: Screenshot of the generated write-up. The author calls it
  "entirely AI-generated" and "a much more accessible way for anyone revisiting
  this incident to understand what happened."
- **Confidence**: emerging
- **Quote**: "What you see here is entirely AI-generated"
- **Our assessment**: Multi-source context incorporation (Slack + video
  transcripts + coding activity) into a single structured write-up is a
  non-trivial integration claim. The generated write-up appears coherent in the
  screenshot, but we cannot assess accuracy, completeness, or hallucination
  risk from a single example.

### Claim 9: Incident wrap-up is reduced to a one-liner Slack command (`@incident`) that triggers AI SGE to incorporate all context and close out the incident
- **Evidence**: Screenshot of the `@incident` command and the agent's response.
- **Confidence**: emerging
- **Quote**: "The job of closing out and providing a final update is as simple
  as a one-liner to ask @incident to take care of it."
- **Our assessment**: The one-liner wrap-up is a compelling simplicity claim,
  but it likely only applies to incidents with clean linear resolutions (PR
  merged, deploy shipped, confirmed fixed). Multi-responder incidents with
  partial resolutions, dispute about root cause, or follow-up items may not
  reduce to a one-liner. This is a best-case demonstration.

### Claim 10: The traditional friction in incident response is tool fragmentation and context switching — AI SRE addresses this by consolidating investigation, fix, communication, and wrap-up into a unified flow
- **Evidence**: Author's stated experience from "hundreds of incidents." The
  article demonstrates orchestration across five tool surfaces (Slack, desktop
  app, Claude Code terminal, GitHub, incident.io) where the responder only
  actively interacts with two.
- **Confidence**: settled
- **Quote**: "the friction has always been the same: too many tools, too much
  context switching, too much time spent just figuring out what's going on
  before you can start fixing it"
- **Our assessment**: The problem statement is well-established and
  uncontroversial. The source's contribution is a concrete integration pattern
  addressing it. The flow orchestrates five surfaces but the responder only
  touches two (desktop app for awareness, Claude Code for action), which is
  the key claim.

### Claim 11: The product is pre-launch with acknowledged UX immaturity, and the team prioritizes correctness and UX quality over speed to market
- **Evidence**: Explicit statements. The author describes the build process,
  notes earlier UX iterations felt "jarring," and states the team is "right on
  the edge of nailing the whole flow."
- **Confidence**: settled
- **Quote**: "We've still got a little way to go (which is why we haven't fully
  launched yet!), but I have incredibly high conviction that this isn't just a
  small improvement, but a markedly better way to run incidents."
- **Our assessment**: This candor about pre-launch status is rare for a vendor
  blog and credibility-enhancing. It materially affects how all other claims
  should be weighted — this is design validation from internal dogfooding, not
  production evidence. Every operational claim should be treated as aspirational
  until confirmed by post-launch evidence.

## Concrete Artifacts

### End-to-end incident workflow (from the article)

```
1. TRIGGER:       Testing new feature → full page crash → blank error screen
2. DECLARATION:   Author reports as incident
3. INVESTIGATION: AI SRE kicks off parallel investigation:
                   - Recent deploys
                   - Telemetry and errors
                   - Past incidents
                   - Code (smoking guns)
                   - Slack context
4. DESKTOP PIN:   Slack nudge → pin incident to macOS desktop app → Mac notch
                   becomes live incident view
5. CLAUDE SYNC:   `/incident INC-19672` in Claude Code → investigation context
                   synced into terminal
6. FINDINGS:      AI SRE identifies frontend crash: `map` returning `undefined`
                   for unrecognized type; recurring cross-team pattern
7. VALIDATION:    Claude validates finding against OpenAPI spec
8. FIX:           Claude proposes graceful skip instead of crash
9. PR + UPDATE:   Claude commits, opens PR, uses incident.io MCP to post
                   channel update (findings + fix + PR link)
10. REVERIFY:     AI SRE rechecks everything Claude posted
11. DEPLOY:       PR merged → fix deployed
12. RE-TEST:      Engineer messages → confirmed fixed
13. WRAP-UP:      `@incident` in Slack → AI SRE closes incident with all
                   context incorporated
14. DEBRIEF:      AI SRE generates structured write-up (entirely AI-generated)
```

### CLI commands (from the article)

```
/incident INC-19672    — Sync AI SRE investigation context into Claude Code

@incident              — One-liner incident wrap-up in Slack
```

### Parallel investigation flow (from the article)

- AI SRE runs autonomously on declaration: deploys, telemetry, code, Slack
- Human works independently in Claude Code
- Context syncs automatically between both agents
- AI SRE reverifies everything Claude posts back to the channel

### Tool orchestration surfaces (from the article)

| Surface | Role |
|---------|------|
| Slack | Incident declaration, AI SRE investigation output, wrap-up command |
| macOS Desktop App | Persistent ambient awareness (notch pin) |
| Claude Code (terminal) | Fix authoring, PR creation, MCP-based Slack update |
| GitHub (via MCP) | PR created without browser |
| incident.io (via MCP) | Status update, wrap-up |

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 5): PagerDuty identifies
    that "lack of interactivity during agent execution was a structural failure"
    — the agent operating without human knowledge. The incident.io parallel
    investigation pattern is a design response to this same failure mode.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 10): PagerDuty's priority
    queue (user input = priority 0, sub-agent results = priority 1) and
    incident.io's parallel investigation pattern both treat human input as a
    first-class concern that must not be blocked by agent execution.
  - `blog-pagerduty-production-ai-agent-gaps.md` (Claim 9): The transparent UX
    finding — showing agent reasoning builds user trust — is demonstrated by
    the AI SRE investigation output visible throughout the incident channel.

- **Contradicts**: None identified. The PagerDuty sources cover internal
  architecture (reactive loops, LangGraph primitives, evaluation pipelines);
  this source covers user-facing interaction design and multi-surface
  orchestration. They are complementary, not contradictory.

- **Extends**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 6, three execution
    models): PagerDuty theorizes concurrent fan-in for real-time visibility.
    This source demonstrates a UX-level implementation of concurrent operation.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 16, "build hard, ship
    simple"): incident.io's 18-month development cycle with pre-launch
    dogfooding parallels the PagerDuty team's methodology.

- **Novel** (compared to the existing baseline note):
  - Multi-surface orchestration: Slack → desktop → Claude Code CLI → GitHub PR
    → Slack, all without tool switching by the responder.
  - The reverification loop: AI SRE double-checking every human-AI collaboration
    output posted to the channel.
  - The `/incident` CLI context-sync command bridging autonomous and interactive
    agents.
  - The "pin to notch" ambient awareness pattern for passive incident visibility.
  - One-liner `@incident` wrap-up reducing incident closeout to a single command.

- **Baseline comparison**: The existing merged note for this source
  (`blog-incidentio-ai-sre-incident-run.md`, issue #3) covers the same source
  with similar claim structure. This eval note was independently extracted
  using `opencode/deepseek-v4-flash-free` via OpenCode Action (Zen free
  chat-completions backend). See that note for the DeepSeek/Flash baseline
  extraction.

## Guide Impact

- **Chapter 01 (Incident Response)**: This source provides evidence for a
  specific AI-assisted incident response pattern: parallel human-agent
  investigation with bidirectional context sync. Key additions: (a) the "first
  responder" role shifting from investigator to verifier as AI SRE runs
  autonomous investigation; (b) the reverification loop as a safety mechanism;
  (c) the end-to-end timing claim (minutes) as an aspirational benchmark,
  caveated with pre-launch status.

- **Chapter 03 (Runbooks and Agents)**: This source provides concrete
  integration patterns: (a) the `/incident` CLI command as a context-bridging
  mechanism between autonomous and interactive agents; (b) MCP-based channel
  updates from within Claude Code as terminal-to-Slack integration without
  context switching; (c) multi-surface orchestration (Slack → desktop →
  terminal → GitHub → Slack) as a zero-switch workflow pattern.

- **Chapter 04 (On-call and Toil)**: This source provides evidence for: (a) the
  ambient awareness pattern (desktop app with passive updates) reducing
  cognitive overhead of actively monitoring multiple tools during incidents;
  (b) the one-liner wrap-up pattern as toil reduction for incident closeout;
  (c) AI-generated debrief write-ups reducing post-incident administrative
  overhead. All claims caveated with pre-launch status.

## Extraction Notes

- The primary source is a single blog post on incident.io's blog. Per MINER.md
  §1, linked pages were checked against what was available in the baseline note:
  the `ai-sre-agent-definition` page (January 2026) was cited but not
  independently fetched for this eval — the existing baseline note's coverage
  of that page (Claim 12, Concrete Artifacts four-step implementation path) is
  referenced instead.

- The article credits no named author. The first-person perspective and "we"
  references suggest a senior team member or co-founder. The article's value is
  in its concrete workflow description and screenshots, not individual authority.

- All quotes are verbatim from the source content fetched via WebFetch of the
  article URL. The Assayer should verify key quotes against the live URL.

- The source is rich in screenshots (10 images) but provides no raw code, no
  MCP configuration, no quantitative metrics, and no failure cases. The
  article presents exactly one incident — a successful linear resolution of a
  relatively simple frontend bug. Generalizability is limited.

- The product is explicitly pre-launch. All claims should be read as design
  validation from internal dogfooding, not production evidence.

- This is an eval mode extraction using `opencode/deepseek-v4-flash-free` via
  OpenCode Action (Zen free chat-completions backend). It is a candidate
  comparison against the merged DeepSeek/Flash baseline at
  `blog-incidentio-ai-sre-incident-run.md`. The extraction methodology follows
  MINER.md precisely; the only variations are the model used and the eval-mode
  filename/frontmatter conventions.
