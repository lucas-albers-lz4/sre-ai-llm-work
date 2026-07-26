---
source_url: https://incident.io/blog/how-it-feels-to-run-an-incident-with-ai-sre
source_type: blog-post
title: "How it feels to run an incident with AI SRE"
author: "incident.io (uncredited first-person author; incident.io team member)"
date_published: 2026-04-23
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: anecdotal
issue: "#3-big-pickle-eval"
---

# How it feels to run an incident with AI SRE

> A first-person practitioner narrative from incident.io walking through an
> end-to-end AI-assisted incident response. Covers autonomous multi-source
> investigation, Claude Code fix authoring via an `/incident` CLI bridge,
> MCP-driven Slack updates from the terminal, and a reverification loop where
> the AI agent double-checks everything posted back to the channel. Published
> April 2026 — the product (Investigations) has not fully launched, making
> this a pre-release design validation, not production evidence.

## Source Context

- **Type**: blog-post (vendor practitioner writeup)
- **Author credibility**: Unnamed incident.io team member writing in first
  person, describing an incident on incident.io's own infrastructure using
  their own product (18 months of internal dogfooding). No named author
  reduces individual credibility slightly, but the concrete workflow with
  screenshots and a real incident ID (INC-19672) lends specificity. The
  author has "responded to hundreds of incidents" per their own account.
- **Scope**: One complete incident lifecycle — a frontend rendering crash
  caused by a type mismatch in a new escalation-path feature. Covers
  declaration, autonomous investigation, desktop app pinning, Claude Code
  integration via `/incident` command, fix authoring, MCP-driven PR and
  Slack channel update, reverification, deploy, wrap-up, and AI-generated
  debrief. Also covers UX philosophy ("better to be right than first") and
  acknowledges the product is not yet fully launched. Does NOT cover:
  internal agent architecture, model selection, evaluation metrics, failure
  cases where the AI was wrong, pricing, or security/auth details for MCP.

## Extracted Claims

### Claim 1: AI SRE (Investigations) autonomously begins multi-source investigation immediately upon incident declaration, checking deploys, telemetry, errors, past incidents, code, and Slack context in parallel
- **Evidence**: Described as built-in system behavior triggered by declaration;
  corroborated by screenshots showing investigation results in the incident
  channel. The author contrasts this with sequential human investigation.
- **Confidence**: emerging
- **Quote**: "All the kinds of things a human would do if they were responding
  to an incident themselves, but much faster and in parallel."
- **Our assessment**: The investigation surface (deploys, telemetry, past
  incidents, code, Slack) is exactly what a human responder would check. The
  "parallel" claim is asserted but not measured — no latency or coverage data.
  Credible as a capability description, unvalidated as a performance claim.

### Claim 2: The `/incident INC-NNN` command in Claude Code synchronizes AI SRE investigation context directly into the terminal session, eliminating manual context transfer
- **Evidence**: Screenshot showing the command executed in Claude Code;
  the author states this connected their session "directly back into the
  incident" with all investigation context synchronized.
- **Confidence**: emerging
- **Quote**: "connecting my Claude Code session directly back into the
  incident, and synchronizing all of the investigation from Investigations
  into the context"
- **Our assessment**: This is the most novel integration pattern in the source.
  A CLI command that bridges an autonomous agent's context into an interactive
  coding agent is a practical, concrete mechanism. The article does not
  describe the underlying protocol (MCP-based vs. custom). Worth tracking as
  a reusable agent-to-agent bridging pattern.

### Claim 3: Human responders and AI agents investigate independently in parallel, with automatic context synchronization keeping both aligned as new findings emerge
- **Evidence**: Designed system behavior. The author worked in Claude Code while
  AI SRE continued investigating in the background; findings automatically
  connected as new intel arrived.
- **Confidence**: emerging
- **Quote**: "it lets responders and Claude move ahead and investigate
  independently, exploring while Investigations continues in parallel behind
  the scenes. That means there's no waiting around; as new intel comes in, we
  automatically connect the dots, keeping both agents aligned on the state of
  the investigation"
- **Our assessment**: This parallel-independent-with-auto-sync pattern addresses
  a failure mode the PagerDuty SRE Agent team identified: single-agent
  sequential execution leaving the agent "operating without information the
  human already had." incident.io's approach inverts this. Plausible but
  demonstrated only through one ideal-run narrative.

### Claim 4: AI SRE implements a reverification loop — everything posted back to the incident channel is rechecked, and the agent nudges on mistakes or omissions
- **Evidence**: Described behavior; no specific example of a caught mistake is
  provided. Framed as a safety mechanism removing the need to blindly trust
  AI output.
- **Confidence**: anecdotal
- **Quote**: "everything you do in Claude and post back to the channel gets
  reverified by Investigations. If you've made a mistake or forgotten
  something, it'll nudge you about it, but it'll also update its understanding
  and ensure anyone in the channel knows what you did and where we landed."
- **Our assessment**: A novel safety pattern — treating human-AI collaboration
  as warranting automated double-checks. The "also update its understanding"
  phrasing suggests the reverification feeds back into the agent's state, not
  just a binary pass/fail. However, without examples of caught mistakes, the
  sensitivity and specificity of this mechanism are unproven. The article
  presents an ideal run where no mistakes were caught.

### Claim 5: Claude Code, via incident.io MCP integration, opens a GitHub PR and posts a structured incident-channel update without the responder leaving the terminal
- **Evidence**: Screenshots of terminal output showing the PR creation and
  resulting Slack channel update. The author states they never opened GitHub
  or switched to Slack.
- **Confidence**: emerging
- **Quote**: "I didn't have to switch to Slack to type an update. I didn't
  open GitHub to create the PR. I didn't go back to incident.io to change
  the status. All of it happened from the same place I was writing the fix."
- **Our assessment**: This is the most concrete MCP value demonstration in the
  source. The pattern (Claude Code commits → opens PR → posts Slack update via
  MCP) represents a genuinely reduced-tool-switching workflow. No MCP server
  configuration, tool schema, or auth details provided, limiting
  reproducibility.

### Claim 6: The incident.io macOS desktop app uses the Mac notch as a persistent, live incident view providing passive situational awareness
- **Evidence**: Screenshot showing the pinned incident in the desktop app
  integrated with the Mac notch. The author describes it as "pinging me with
  updates" and keeping them "always plugged into the latest context without
  having to go looking for it."
- **Confidence**: anecdotal
- **Quote**: "the incident.io desktop app is sitting there on my Mac, pinging
  me with updates"
- **Our assessment**: The "pin to notch" pattern is macOS-specific, but the
  underlying principle — a persistent, ambient incident awareness surface that
  doesn't require active polling — is generalizable. Addresses the
  context-switching overhead the author identifies as core friction. Novel UX
  pattern, but supported only by a screenshot and self-reported experience.

### Claim 7: The complete AI-assisted incident lifecycle took "minutes, and most of that was waiting for the deploy"
- **Evidence**: Self-reported time estimate with no stopwatch data. The incident
  was a frontend rendering crash (type mismatch) in a feature the author had
  "zero familiarity" with, resolved within their own fully-integrated toolchain.
- **Confidence**: anecdotal
- **Quote**: "The whole process here, from incident declaration to resolution,
  took minutes. And most of that was waiting for the deploy."
- **Our assessment**: Headline claim and weakest evidentially. "Minutes" is
  imprecise; "most of that was waiting for the deploy" is unfalsifiable without
  actual timing. The incident was a relatively simple bug in the author's own
  product with full tooling integration. Does not generalize to complex
  multi-service incidents or organizations without the same maturity. Treat as
  an existence proof, not a benchmark.

### Claim 8: AI SRE generates a fully AI-written structured incident write-up incorporating Slack, Zoom/Google Meet transcripts, and coding session activity
- **Evidence**: Screenshot of the generated write-up. The article states it is
  "entirely AI-generated" and serves as "a much more accessible way for anyone
  revisiting this incident to understand what happened."
- **Confidence**: emerging
- **Quote**: "What you see here is entirely AI-generated, and it's a much more
  accessible way for anyone revisiting this incident to understand what
  happened."
- **Our assessment**: Multi-source context incorporation (Slack + video
  transcripts + coding activity) into a single structured write-up is
  non-trivial. The screenshot appears coherent but accuracy/completeness
  cannot be assessed from a single example. The linked debrief framework
  article (March 2025) contains no AI SRE integration, suggesting this feature
  post-dates or exists separately from incident.io's human debrief methodology.

### Claim 9: Incident wrap-up reduces to a one-liner Slack command (`@incident`) that triggers AI SRE to incorporate all incident context and close out
- **Evidence**: Screenshot showing the `@incident` command and agent response.
- **Confidence**: emerging
- **Quote**: "The job of closing out and providing a final update is as simple
  as a one-liner to ask @incident to take care of it."
- **Our assessment**: Compelling simplicity claim, but likely only works for
  incidents where all resolution steps are already complete (PR merged, deploy
  shipped, re-test confirmed). The article's incident had a clean linear
  resolution. Multi-responder incidents with partial resolutions, follow-up
  items, or disputed root causes may not reduce to a one-liner. Best-case
  demonstration.

### Claim 10: Tool fragmentation and context switching are the core friction in traditional incident response, and AI SRE addresses this by consolidating investigation, fix authoring, communication, and wrap-up
- **Evidence**: Author's stated experience from "hundreds of incidents" over
  their career. The article demonstrates five tool surfaces orchestrated into
  a flow where the responder only actively interacts with two (desktop app
  and Claude Code terminal).
- **Confidence**: settled
- **Quote**: "too many tools, too much context switching, too much time spent
  just figuring out what's going on before you can start fixing it"
- **Our assessment**: The problem statement is well-established and
  uncontroversial. The source's contribution is demonstrating a concrete
  integration pattern addressing it. The five-surface orchestration (Slack →
  desktop → Claude Code → GitHub → Slack) is more surfaces than ideal, but
  the author's claim is that only two require active interaction.

### Claim 11: The product is explicitly pre-launch, with the team prioritizing correctness and UX quality over speed to market
- **Evidence**: Explicit statements. 18 months of development, earlier UX
  described as "jarring and easy to move past," and the team is "right on the
  edge of nailing the whole flow."
- **Confidence**: settled
- **Quote**: "We've still got a little way to go (which is why we haven't
  fully launched yet!)"
- **Our assessment**: Rare candor from a vendor blog post. Materially affects
  how we weight all other claims: this is a design validation, not production
  evidence. The candor is credibility-enhancing but every claim should be read
  as aspirational until confirmed by post-launch evidence.

### Claim 12: Incident.io identifies a recurring cross-team type-mismatch pattern — one side introduces a type the other doesn't handle — surfaced by AI SRE during investigation
- **Evidence**: The author states AI SRE "even identified a recurring pattern
  from previous incidents where one side introduces a type that the other side
  doesn't handle – we're now looking into this!"
- **Confidence**: anecdotal
- **Quote**: "It even identified a recurring pattern from previous incidents
  where one side introduces a type that the other side doesn't handle – we're
  now looking into this!"
- **Our assessment**: This is a concrete example of cross-incident pattern
  detection — the AI finding a systemic issue beyond the immediate bug. It's
  the strongest evidence of AI SRE's analytical value beyond simple log
  searching. However, the pattern is described in a single sentence with no
  detail on how the detection works or how many incidents were matched.

### Claim 13: The AI SRE definition distinguishes itself from both traditional runbook automation (rigid scripts) and AIOps (recommendations without action)
- **Evidence**: From the linked `ai-sre-agent-definition` page (January 2026),
  which the article links to but does not directly quote. The page defines AI
  SRE agents as systems that "perceive their environment, reason, plan, and
  execute multi-step tasks" autonomously.
- **Confidence**: emerging
- **Quote**: (no direct quote from the main article; definition sourced from
  linked page)
- **Our assessment**: Useful taxonomy for situating the source. The runbook-
  vs-AIOps-vs-AI-agent three-tier framing is analytically sound, though the
  boundaries blur in practice (many AIOps tools now include action execution).
  Vendor-authored and serves product positioning.

## Concrete Artifacts

### End-to-end incident workflow (from the article)

```
1. TRIGGER:       Feature test → full page crash → blank error screen
2. DECLARATION:   Author declares incident ("declare early, declare often")
3. INVESTIGATION: AI SRE (Investigations) autonomously kicks off parallel
                  investigation: recent deploys, telemetry and errors,
                  past incidents, code, Slack context
4. DESKTOP PIN:   Slack nudge → pin incident to macOS desktop app
                  → Mac notch becomes live incident view
5. CLAUDE SYNC:   `/incident INC-19672` in Claude Code
                  → investigation context synced into terminal session
6. FINDINGS:      AI SRE identifies: frontend crash, map returning undefined
                  for unrecognized type; recurring cross-team type-mismatch
                  pattern surfaced
7. VALIDATION:    Claude validates finding against OpenAPI spec in codebase
8. FIX:           Claude proposes graceful skip instead of crash
9. PR + UPDATE:   Claude commits, opens PR, uses incident.io MCP to post
                  channel update (findings + fix + PR link)
10. REVERIFY:     AI SRE rechecks everything Claude posted; nudges if needed
11. DEPLOY:       PR merged → fix deployed
12. RE-TEST:      Engineer messages author to re-test → confirmed fixed
13. WRAP-UP:      @incident one-liner in Slack → AI SRE closes incident,
                  incorporating Slack + Zoom/Meet + coding session context
14. DEBRIEF:      AI SRE generates structured write-up (entirely AI-generated)
```

### CLI command: Incident context sync into Claude Code

```
/incident INC-19672
```

Connects the Claude Code session to the specified incident, synchronizing
all AI SRE investigation context. Shown in a screenshot.

### Slack command: Incident wrap-up

```
@incident
```

One-liner that triggers AI SRE to incorporate all incident context (Slack,
Zoom/Google Meet transcripts, coding session activity) and close out the
incident. Shown in a screenshot.

### AI SRE autonomous investigation checklist (from the article)

- Recent deploys
- Telemetry and error logs
- Past incidents (similarity/pattern matching)
- Code changes (smoking guns)
- Slack context (relevant channel discussions)

### MCP integration point (described, not configured)

Claude Code used "the incident.io MCP to post an update into the incident
channel, including what was found, what the fix is, and a link to the PR."
No MCP server configuration, tool schema, endpoint, or authentication
details are provided.

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 5): PagerDuty identifies
    that "lack of interactivity during agent execution was a structural
    failure" — the agent operating without information the human already had.
    The incident.io article demonstrates a design response: human and AI
    investigate in parallel with bidirectional context sync.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 10): PagerDuty's
    priority queue pattern (user input = priority 0) and the incident.io
    parallel investigation pattern both treat human input as a first-class
    event that must not be blocked by agent execution.
  - `miner-related-notes.md` candidate 1 (`blog-incidentio-ai-sre-incident-run.md`):
    This is the merged baseline DeepSeek/Flash source note for the same URL.
    Cites the same source with 12 claims. Cross-referenced and compared
    throughout; see Extraction Notes for differences.

- **Contradicts**: None identified. The PagerDuty source covers internal agent
  architecture; the incident.io source covers user-facing interaction design.
  They operate at different layers and are complementary.

- **Extends**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 6, three execution
    models): PagerDuty argues concurrent fan-in is required for real-time
    visibility. The incident.io article demonstrates a UX-level implementation
    of concurrent operation: AI SRE and Claude Code working in parallel with
    automatic context sync.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 16, "build hard, ship
    simple"): The incident.io team's 18-month development cycle with pre-launch
    dogfooding parallels PagerDuty's methodology of building the complex
    version first.

- **Novel**: New to the corpus beyond existing PagerDuty source notes:
  - **Multi-surface orchestration**: Slack → desktop app → Claude Code CLI →
    GitHub PR → Slack channel update, all within a single incident flow.
  - **The reverification loop**: AI SRE rechecking everything posted back to
    the incident channel and nudging on mistakes — a safety pattern treating
    human-AI collaboration as warranting automated double-checks.
  - **Ambient awareness pattern**: Persistent desktop surface for incident
    context providing passive updates without active polling.
  - **`/incident` context-sync command**: A CLI command bridging an autonomous
    investigation agent's context into an interactive coding agent.
  - **One-liner incident wrap-up**: Reducing incident closeout to a single
    Slack command with AI handling context incorporation and write-up.
  - **Cross-incident pattern detection**: AI SRE identifying a recurring
    type-mismatch pattern across previous incidents (Claim 12) — concrete
    evidence of analytical value beyond log searching.

## Guide Impact

- **Chapter 01 (Incident Response)**: Add the parallel human-agent
  investigation pattern with bidirectional context sync. Specifically:
  (a) the pattern of declaring an incident and having AI begin autonomous
  investigation immediately — changes the "first responder" role from
  investigator to verifier; (b) the reverification loop as a safety mechanism;
  (c) end-to-end lifecycle timing claim (minutes) as an aspirational benchmark
  with pre-launch caveat.

- **Chapter 03 (Runbooks and Agents)**: Add concrete agent-to-agent and
  agent-to-tool integration patterns: (a) the `/incident` CLI command as a
  context-bridging mechanism between autonomous and interactive agents; (b)
  MCP-based channel updates from within Claude Code as a terminal-to-Slack
  integration without context switching.

- **Chapter 04 (On-call and Toil)**: Add: (a) ambient awareness pattern
  (desktop app with passive updates) as cognitive overhead reduction; (b)
  one-liner wrap-up as toil reduction for incident closeout; (c) cross-incident
  pattern detection (Claim 12) as evidence that AI SRE provides value beyond
  single-incident resolution. All claims caveated with pre-launch status.

## Extraction Notes

- The primary source is a single long-form blog post on incident.io's blog.
  The linked `ai-sre-agent-definition` page (January 2026) was followed and
  contributed Claim 13. Two other linked pages (`declare-early-declare-often`
  and `a-seven-step-framework-for-running-incident-debriefs`) were checked
  but contained no AI-specific claims worth extracting.

- The article has no named author. The first-person narrative and "we" (the
  incident.io product team) suggest a senior team member or co-founder. Lack
  of attribution reduces individual authority, but the article's value is in
  concrete workflow descriptions and screenshots.

- Quotes were extracted from the WebFetch of the live URL on 2026-07-26.
  Short quotes are likely verbatim; the Assayer should verify against the
  live URL. Longer passages are attributed as paraphrases per MINER.md §2a.5.

- The source is rich in screenshots (10 images) but provides no raw code, no
  MCP configuration, no quantitative metrics, and no failure cases. The
  article presents exactly one incident — a successful, linear resolution of
  a simple frontend bug. This limits generalizability.

- The product is explicitly pre-launch. All claims should be read as design
  validation from internal dogfooding, not production evidence. The
  confidence_overall of "anecdotal" reflects both the vendor source and the
  pre-launch status.

- Cross-reference with `miner-related-notes.md` candidates: Candidate 1 is
  the merged baseline note for this same URL (cited above). Candidates 2-10
  are unrelated SRE Prodcast transcripts and other source notes that do not
  overlap with this source's claims about AI-assisted incident response UX.
  Dismissed as not relevant.

- Comparison with baseline note (`blog-incidentio-ai-sre-incident-run.md`):
  Both notes extract the same source. The baseline has 12 claims; this eval
  note has 13 (added Claim 12 on cross-incident pattern detection, which the
  baseline did not extract). Both notes cite the same cross-references and
  arrive at similar assessments. Key difference: this note adds the cross-
  incident pattern detection claim (sourced from the article's single sentence
  about recurring type-mismatch patterns) and provides slightly more detail on
  the reverification loop's feedback mechanism.
