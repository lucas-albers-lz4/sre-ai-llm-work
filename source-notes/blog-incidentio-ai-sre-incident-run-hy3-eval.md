---
source_url: https://incident.io/blog/how-it-feels-to-run-an-incident-with-ai-sre
source_type: blog-post
title: "How it feels to run an incident with AI SRE"
author: "Chris Evans (Co-Founder & Field CTO, incident.io)"
date_published: 2026-04-23
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: anecdotal
issue: "#3-hy3-eval"
---

# How it feels to run an incident with AI SRE

> A first-person practitioner narrative from incident.io co-founder/Field CTO Chris
> Evans walking through a complete, real incident resolved with AI SRE: declaration →
> autonomous parallel investigation → Claude Code fix authoring via `/incident` →
> MCP-driven PR + Slack update → AI reverification → deploy → one-liner `@incident`
> wrap-up → AI-generated debrief. Documents concrete human-AI collaboration patterns
> (parallel investigation, reverification loop, multi-surface orchestration) with
> explicit acknowledgment that the product is pre-launch and the UX "hasn't clicked"
> until this run.

## Source Context

- **Type**: blog-post (vendor practitioner writeup, first-person)
- **Author credibility**: Named author — **Chris Evans**, "Co-Founder & Field CTO"
  at incident.io (per the article's author bio block: "I'm one of the co-founders,
  and Field CTO here at incident.io."). He states he has "responded to hundreds of
  incidents over the years" and that the team has "been building the broader
  incident.io platform for several years now" with "a lot of effort into this over
  the last 5 years" on UX. He has direct product involvement: "For the last 18
  months, we've been building AI SRE." The narrative is internal dogfooding — the
  incident occurred on incident.io's own in-development feature ("delay nodes in
  escalation paths," enabled only on demo accounts). This is a vendor narrative with
  a promotional angle, but it is unusually concrete (named incident ID INC-19672,
  specific commands, screenshots) and candid about pre-launch status.
- **Scope**: Covers one complete incident lifecycle — a frontend rendering crash
  from a type mismatch in a new escalation-path feature — from declaration through
  AI SRE autonomous investigation, Mac desktop "pin to notch," Claude Code
  integration via `/incident`, fix authoring, MCP-driven PR and channel update,
  reverification, deploy, one-liner wrap-up, and AI-generated debrief. Also states a
  UX philosophy ("better to be right than first") and explicitly acknowledges the
  product has not fully launched. Does NOT cover: agent internal architecture, model
  selection, evaluation metrics, failure cases where AI SRE was wrong, pricing, or
  MCP auth details. The article links to an "AI SRE explained" capability page for
  the broader vision but that page is not the focus of the walkthrough.

## Extracted Claims

### Claim 1: The author is a credible practitioner source — incident.io co-founder/Field CTO who has run hundreds of incidents and spent 18 months building AI SRE
- **Evidence**: Author bio block in the article: "I'm one of the co-founders, and
  Field CTO here at incident.io." Body states "I've responded to hundreds of
  incidents over the years" and "For the last 18 months, we've been building AI
  SRE." The incident described is on the author's own company infrastructure.
- **Confidence**: settled
- **Quote**: "I'm one of the co-founders, and Field CTO here at incident.io."
- **Our assessment**: Unlike an anonymous vendor post, this carries a named author
  with direct authority over the product. The first-person "we've been building AI
  SRE" plus the hundreds-of-incidents experience gives the UX claims weight. The
  vendor interest is real but the detail level (named incident, real commands) makes
  it more than marketing.

### Claim 2: The product's UX had not "clicked" until this run — the team struggled for 18 months to make the agent experience feel natural, describing earlier UX as "jarring and easy to move past"
- **Evidence**: Explicit self-critical statements in the intro. The author says the
  investigation "brain" improved but "we've been struggling to get the UX to click
  in a way that feels as natural as the rest of the product" and that "An agent that
  does impressive things behind the scenes doesn't count for much if the experience
  of using it feels jarring and easy to move past."
- **Confidence**: settled
- **Quote**: "An agent that does impressive things behind the scenes doesn't count
  for much if the experience of using it feels jarring and easy to move past, both of
  which are things we've felt as we've been building it."
- **Our assessment**: This is a high-value, candid admission rare in vendor blogs.
  It directly counters the usual "AI agent magically solves incidents" framing and
  establishes that UX/ergonomics — not raw capability — is the hard part of
  human-AI incident collaboration. It should temper how we read every downstream
  success claim.

### Claim 3: AI SRE autonomously begins multi-source investigation the moment an incident is declared, mirroring human responder actions but "much faster and in parallel"
- **Evidence**: Described as triggered by declaration. The article lists the
  investigation surface: recent deploys, telemetry/errors, past incidents, code
  "smoking guns," and Slack context. The author framed this as the contrast with
  sequential human work.
- **Confidence**: emerging
- **Quote**: "All the kinds of things a human would do if they were responding to an
  incident themselves, but much faster and in parallel."
- **Our assessment**: The data sources are exactly what a human would check, so the
  capability description is plausible. The "parallel" and "much faster" claims are
  asserted, not measured — no latency or coverage numbers. Credible as a capability
  description, unvalidated as a performance claim.

### Claim 4: The incident.io macOS desktop app's "pin to notch" turns the Mac notch into a live, interactive incident view and a jump-off point into Claude/Cursor/agentic coding tools
- **Evidence**: Described behavior + screenshot. Pinning an incident in the desktop
  app makes the Mac notch "a live and interactive view of the incident." The author
  also notes this is a recently shipped surface ("it's beautiful!").
- **Confidence**: anecdotal
- **Quote**: "pinning an incident turns the notch on your Mac into a live and
  interactive view of the incident, and an easy way to jump straight into Claude,
  Cursor, or your agentic coding platform of choice."
- **Our assessment**: The ambient/passive-awareness principle (a persistent incident
  surface that doesn't require active polling) is generalizable even though the
  macOS-notch implementation is platform-specific. It targets the context-switching
  overhead the author later names as the core incident friction.

### Claim 5: The `/incident INC-NNN` slash command in Claude Code synchronizes AI SRE's investigation context into the terminal session, letting the responder pick up where the agent left off without manual context transfer
- **Evidence**: Named command with incident ID `INC-19672`, shown in a screenshot.
  The author states it "connect[ed] my Claude Code session directly back into the
  incident, and synchroniz[ed] all of the investigation from AI SRE's investigation
  into the context."
- **Confidence**: emerging
- **Quote**: "I jumped into Claude Code with the /incident INC-19672 command,
  connecting my Claude Code session directly back into the incident, and
  synchronizing all of the investigation from AI SRE's investigation into the
  context."
- **Our assessment**: One of the most concrete and novel patterns: a CLI command that
  bridges an autonomous investigation agent's context into an interactive coding
  agent. No implementation detail is given (how context is serialized, what protocol,
  MCP or custom), so it's a design pattern, not a recipe.

### Claim 6: AI SRE pinpointed the root cause as a frontend rendering crash — a `map` returning `undefined` for a type the frontend didn't recognize — and surfaced a recurring cross-team type-mismatch pattern
- **Evidence**: Stated as the result of the first investigation pass. The author had
  "zero familiarity with this part of the platform" yet received enough to proceed.
  The recurring pattern ("one side introduces a type that the other side doesn't
  handle") is flagged as a follow-up the team is now investigating.
- **Confidence**: emerging
- **Quote**: "had narrowed down the cause to a frontend rendering crash: a map
  returning undefined for a type the frontend didn't recognize. It even identified a
  recurring pattern from previous incidents where one side introduces a type that the
  other side doesn't handle"
- **Our assessment**: The root-cause finding is specific and checkable (it was
  validated against the OpenAPI spec, see Claim 7). The "recurring pattern" claim is
  a value-add from historical incident matching — plausible but asserted from one
  example. Note the author stresses he did not have to "dig through logs, check
  Grafana, or read through code" — the investigation did it for him.

### Claim 7: Claude (not the human) validated the AI SRE finding against the codebase, checking the OpenAPI spec and confirming the problem
- **Evidence**: The author describes the Claude/AI SRE combo "validating it against
  the codebase" and explicitly "checked the OpenAPI spec and found the problem." This
  is presented as the non-blind-trust step.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment — the article
  narrates "it checked the OpenAPI spec and found the problem" alongside a
  screenshot rather than a standalone sentence suitable for verbatim citation)
- **Our assessment**: The claim is that validation is performed by the coding agent
  against the repo's own spec, not by the human. This is a concrete example of the
  "no need to blindly trust it" principle (Claim 8) in action. Credible as a
  demonstrated step, but shown via a single screenshot.

### Claim 8: The design explicitly rejects blind trust — responders and the AI investigate in parallel, and as new intel arrives the system auto-connects the dots to keep both agents aligned
- **Evidence**: Stated design principle. "There's no need to blindly trust it" and
  the parallel-investigation passage. The author notes he had "zero familiarity" with
  the code yet could "verify the conclusion as plausible and proceed."
- **Confidence**: emerging
- **Quote**: "it lets responders and Claude move ahead and investigate independently,
  exploring while AI SRE continues in parallel behind the scenes. That means there's
  no waiting around; as new intel comes in, we automatically connect the dots,
  keeping both agents aligned on the state of the investigation."
- **Our assessment**: This is the central collaboration pattern and it directly
  answers a known failure mode in the PagerDuty SRE Agent architecture note (see
  Cross-References). Instead of a single agent running synchronously while the human
  waits, the human and agent each work independently and context syncs
  bidirectionally. Demonstrated through one ideal run; no measurement of sync
  latency or conflict rate.

### Claim 9: Claude proposed the fix (gracefully skip rendering the item instead of crashing the page) and the human approved committing and opening a PR
- **Evidence**: The author quotes the proposed fix and his own approval. The fix is a
  defensive-rendering change, not a root-cause architectural fix.
- **Confidence**: emerging
- **Quote**: "Claude proposed the fix: gracefully skipping rendering an item instead
  of crashing the whole page. 'Want me to commit this and open a PR?' Yes. Yes, I do."
- **Our assessment**: The fix is a shallow, defensive patch (skip-on-unknown-type)
  rather than eliminating the type mismatch at its source. Worth noting for the guide:
  AI-assisted incident fixes may trend toward "make it not crash" rather than
  "fix the contract" — a toil-reduction pattern that can leave latent debt. The
  human approval gate is present, consistent with human-in-the-loop expectations.

### Claim 10: Claude, via incident.io MCP, opened the PR and posted a structured incident-channel update (findings, fix, PR link) — all without the responder leaving the terminal or switching to Slack/GitHub/incident.io
- **Evidence**: Described with screenshots. The author emphasizes he "didn't have to
  switch to Slack," "didn't open GitHub," "didn't go back to incident.io" — "All of
  it happened from the same place I was writing the fix."
- **Confidence**: emerging
- **Quote**: "Claude opened the PR, then used the incident.io MCP to post an update
  into the incident channel, including what was found, what the fix is, and a link to
  the PR."
- **Our assessment**: The strongest concrete demonstration of MCP value in the
  source: terminal → GitHub PR → Slack update with zero tool-switching. No MCP server
  config, tool schema, or auth detail is given, so it's not independently
  reproducible from the article. Credible as a capability demo.

### Claim 11: Every Claude action posted back to the channel is reverified by AI SRE, which nudges on mistakes/omissions and updates its own understanding and the channel
- **Evidence**: Stated as a built-in safety behavior. The author frames it as
  removing the need to "blindly trust" AI output. Notably, the article presents an
  ideal run where no mistake was actually caught — so the mechanism is described but
  not demonstrated catching an error.
- **Confidence**: anecdotal
- **Quote**: "everything you do in Claude and post back to the channel gets
  reverified by AI SRE. If you've made a mistake or forgotten something, it'll nudge
  you about it, but it'll also update its understanding and ensure anyone in the
  channel knows what you did and where we landed."
- **Our assessment**: A novel safety pattern — it treats human-AI collaboration as
  warranting automated double-checks, but makes them non-blocking. Without an example
  of a caught mistake, sensitivity/specificity are unknown. Valuable to track as a
  design pattern; unproven in practice here.

### Claim 12: The desktop app provides passive, ambient awareness — "pinging me with updates" so the responder stays plugged into context without actively checking
- **Evidence**: Described as a side effect of the desktop surface during the flow.
- **Confidence**: anecdotal
- **Quote**: "the incident.io desktop app is sitting there on my Mac, pinging me with
  updates as things progress. So I'm always plugged into the latest context without
  having to go looking for it."
- **Our assessment**: Reinforces Claim 4's ambient-awareness principle from the
  awareness (vs action) side: the responder receives progress passively while doing
  other work. Generalizable principle; macOS-specific delivery.

### Claim 13: Incident wrap-up reduces to a one-liner — `@incident` — that incorporates Slack, Zoom/Google Meet, and coding-session context and closes out the incident
- **Evidence**: Stated as a one-liner command with the AI incorporating all context.
  The author calls it "as simple as a one-liner to ask @incident to take care of it."
- **Confidence**: emerging
- **Quote**: "The job of closing out and providing a final update is as simple as a
  one-liner to ask @incident to take care of it."
- **Our assessment**: Compelling simplicity claim, but almost certainly a best case:
  it works because every resolution step (PR merged, deploy shipped, re-test
  confirmed) was already complete. Multi-responder incidents with partial
  resolutions, follow-ups, or disputed root causes won't reduce to a one-liner. Best-
  case demonstration.

### Claim 14: AI SRE turns the accumulated incident context into a fully AI-generated, structured write-up that serves as a foundation for team debriefs
- **Evidence**: Screenshot of the generated write-up. The author says "What you see
  here is entirely AI-generated" and that it's "a much more accessible way for anyone
  revisiting this incident to understand what happened."
- **Confidence**: emerging
- **Quote**: "What you see here is entirely AI-generated, and it's a much more
  accessible way for anyone revisiting this incident to understand what happened."
- **Our assessment**: Multi-source context incorporation (Slack + video transcripts +
  coding activity) into one structured write-up is a non-trivial integration claim.
  Shown via one coherent example; accuracy/completeness cannot be assessed from a
  screenshot alone.

### Claim 15: The core friction of incident response is tool fragmentation and context-switching, and AI SRE's unified flow attacks it — "too many tools, too much context switching, too much time spent just figuring out what's going on"
- **Evidence**: The author's experience across "hundreds of incidents": the friction
  "has always been the same." The article demonstrates five surfaces (Slack, desktop
  app, Claude Code terminal, GitHub, incident.io) orchestrated so the responder
  actively touches only the desktop app (awareness) and Claude Code (action).
- **Confidence**: settled
- **Quote**: "too many tools, too much context switching, too much time spent just
  figuring out what's going on before you can start fixing it"
- **Our assessment**: The problem statement is well-established and uncontroversial.
  The source's contribution is a concrete integration pattern that addresses it, not
  the identification of the problem. The five-surface orchestration is still more
  surfaces than ideal, but the claim is that the responder only actively drives two.

### Claim 16: The end-to-end lifecycle (declaration → resolution) took "minutes, and most of that was waiting for the deploy," and the team is pre-launch but has "incredibly high conviction" the approach is "markedly better" — guided by "better to be right than first"
- **Evidence**: Self-reported timing with no stopwatch; the incident was a simple
  frontend type-mismatch bug in the author's own product with full tooling already
  integrated. Explicit pre-launch statement and philosophy.
- **Confidence**: anecdotal
- **Quote**: "The whole process here, from incident declaration to resolution, took
  minutes. And most of that was waiting for the deploy. We've still got a little way
  to go (which is why we haven't fully launched yet!), but I have incredibly high
  conviction that this isn't just a small improvement, but a markedly better way to
  run incidents."
- **Our assessment**: The headline claim and the weakest evidentially. "Minutes" is
  imprecise and "most of that was waiting for the deploy" is unfalsifiable without
  timing. The incident is a relatively simple, linear bug in a fully-integrated
  environment — it does not generalize to complex multi-service incidents,
  infrastructure changes, or orgs without the same integration maturity. The "better
  to be right than first" line is a credible, maturity-signaling philosophy (cf.
  PagerDuty's "build hard, ship simple," Cross-References). Treat as an existence
  proof, not a benchmark.

## Concrete Artifacts

### End-to-end incident workflow (as described and screenshot'd in the article)

```
1. TRIGGER:       Testing "delay nodes in escalation paths" feature
                  → escalation details page crashes → blank error screen
2. DECLARATION:   Author declares incident (per "declare early, declare often")
3. INVESTIGATION: AI SRE autonomously kicks off parallel investigation:
                  - Recent deploys
                  - Telemetry and errors
                  - Past incidents (pattern matching)
                  - Code (smoking guns)
                  - Slack context
4. DESKTOP PIN:   Slack nudge → pin incident in incident.io macOS desktop app
                  → Mac notch becomes live, interactive incident view
5. CLAUDE SYNC:   /incident INC-19672 in Claude Code
                  → AI SRE investigation context synced into terminal session
6. FINDINGS:      AI SRE: frontend rendering crash, map returning undefined
                  for an unrecognized type; recurring cross-team type-mismatch
                  pattern surfaced
7. VALIDATION:    Claude validates finding against OpenAPI spec in codebase
8. FIX:           Claude proposes graceful skip instead of crash
                  → human approves: "Want me to commit this and open a PR?"
9. PR + UPDATE:   Claude commits, opens PR, uses incident.io MCP to post
                  channel update (findings + fix + PR link)
10. REVERIFY:     AI SRE rechecks everything Claude posted; nudges if needed
11. DEPLOY:       PR merged → fix deployed
12. RE-TEST:      Engineer messages author to re-test → confirmed fixed
13. WRAP-UP:      @incident one-liner in Slack → AI SRE closes incident,
                  incorporating Slack + Zoom/Meet + coding-session context
14. DEBRIEF:      AI SRE generates structured write-up (entirely AI-generated)
```

### CLI command: Incident context sync into Claude Code

```
/incident INC-19672
```

Connects the Claude Code session to the specified incident, synchronizing all AI
SRE investigation context. Verbatim from the article ("I jumped into Claude Code
with the /incident INC-19672 command…"); shown with a Claude Code terminal
screenshot.

### Slack command: Incident wrap-up

```
@incident
```

One-liner Slack command that triggers AI SRE to incorporate all incident context
(Slack, Zoom/Google Meet transcripts, coding-session activity) and close out the
incident. Verbatim from the article.

### AI SRE autonomous investigation checklist (from the article)

As described, AI SRE checks these data sources upon incident declaration:

- Recent deploys
- Telemetry and errors
- Past incidents (similarity / pattern matching)
- Code changes (smoking guns)
- Slack context (relevant channel discussions)

### MCP integration point (described but not configured)

Claude Code "used the incident.io MCP to post an update into the incident channel,
including what was found, what the fix is, and a link to the PR." No MCP server
configuration, tool schema, endpoint, or authentication details are provided in
the article.

### Four-step AI SRE adoption path (from the linked "AI SRE explained" capability page, cited in the article)

The article links its broader vision to an "AI SRE explained" page. That page (per
the deeper MINER read in the merged DeepSeek baseline note
`blog-incidentio-ai-sre-incident-run.md`) lays out a staged adoption path:

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
   → Safe runbooks first: restart containers, scale clusters, roll back deploys
```

This is included as a corroborating artifact; the Hy3 read focused on the main
walkthrough and did not independently fetch the linked page.

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 5): PagerDuty identifies that
    "lack of interactivity during agent execution was a structural failure" — the
    agent "operating without information the human already had." The incident.io
    article demonstrates a design response: the human and AI investigate in parallel
    (Claim 8), context syncs bidirectionally, and AI SRE's reverification loop
    (Claim 11) double-checks the human/agent output. Same problem, different layer of
    solution (user-facing interaction vs internal architecture).
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 6): PagerDuty's concurrent
    fan-in model requires that "the user always has visibility. New work can be
    injected at any point." incident.io's parallel-investigation + auto-connect-the-
    dots pattern (Claim 8) is a UX-level realization of that principle: human input
    is a first-class, non-blocking event.
  - `blog-pagerduty-production-ai-agent-gaps.md` (Claim 9): PagerDuty argues
    transparent UX (showing agent reasoning in real time) "builds user trust and
    increases willingness to wait." incident.io's ambient desktop updates (Claims 4,
    12) and reverification transparency (Claim 11) are concrete implementations of
    that trust-building UX advice.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 16, "build hard, ship simple"):
    incident.io's explicit "better to be right than first" philosophy (Claim 16) and
    18-month pre-launch dogfooding (Claim 2) parallel PagerDuty's methodology of
    building the complex version first to learn the primitives before simplifying.

- **Contradicts**: None identified. The PagerDuty notes operate at the internal
  agent-architecture layer (multi-agent loops, LangGraph primitives, context rot);
  the incident.io source operates at the user-facing collaboration/UX layer. They are
  complementary, not opposed. (Note: the production-gaps note's Claim 1 — "the
  prototype-to-production gap … demos are easy, reliability is hard" — is consistent
  with, not contradicted by, incident.io's own pre-launch admission in Claim 2/16.)

- **Extends**:
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 6, concurrent fan-in): PagerDuty
    argues concurrent fan-in is required for real-time visibility in investigation.
    incident.io demonstrates a product-level interaction implementing concurrent
    operation — AI SRE and Claude Code working in parallel with automatic context
    sync (Claim 8) — extending the architectural principle into a concrete UX pattern.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (Claim 5, "tool calls
    are where most agentic failures live"): incident.io's reverification loop (Claim
    11) is a human-AI-facing safety mechanism that re-checks exactly those tool-call
    outputs (PR creation, channel posts) Honeycomb says are failure-prone. The
     incident.io pattern is a product behavior; Honeycomb's is an observability
     prescription — they point at the same risk from different angles.

- **Novel**: The following patterns are new to the corpus (not covered by the existing
  PagerDuty or Honeycomb notes):
  - **The `/incident` context-sync CLI command** (Claim 5): a command that bridges an
    autonomous investigation agent's context into an interactive coding agent. A
    specific agent-to-agent integration pattern.
  - **MCP-based terminal → Slack channel update without context switching** (Claim 10):
    Claude Code posting findings + PR link to Slack via incident.io MCP from inside
    the terminal. A concrete demonstration of MCP's value proposition.
  - **The reverification loop** (Claim 11): AI SRE re-checks everything Claude posts
    back to the channel and nudges on mistakes — a safety pattern treating human-AI
    collaboration as warranting automated double-checks.
  - **The "pin to notch" ambient awareness pattern** (Claims 4, 12): a persistent
    desktop surface (macOS notch) for passive incident awareness without active
    polling. macOS-specific delivery; generalizable principle.
  - **One-liner incident wrap-up** (Claim 13): reducing closeout + debrief prep to a
    single `@incident` Slack command with AI incorporating all context.

## Guide Impact

- **Chapter 01 (Incident Response)**: Provides evidence for a specific AI-assisted
  response pattern — parallel human-agent investigation with bidirectional context
  sync (Claim 8). Recommend the guide add: (a) declaring an incident and having AI
  begin autonomous investigation immediately (Claim 3) — this shifts the first
  responder's role from investigator to verifier; (b) the reverification loop (Claim
  11) as a safety mechanism — AI double-checking human-AI collaboration output; (c)
  the end-to-end "minutes, mostly waiting for deploy" timing (Claim 16) as an
  aspirational benchmark, explicitly caveated by the source's pre-launch status and
  the simplicity of the incident (a single frontend type-mismatch bug).

- **Chapter 03 (Runbooks and Agents)**: Provides concrete agent-to-agent and
  agent-to-tool integration patterns: (a) the `/incident` CLI command (Claim 5) as a
  context-bridging mechanism between autonomous and interactive agents — worth
  recommending for any multi-agent incident toolchain; (b) MCP-based channel updates
  from within Claude Code (Claim 10) as terminal-to-Slack integration without context
  switching; (c) the staged adoption path (service catalog → tool integration →
  human-in-the-loop → gradual automation) as a pragmatic rollout sequence.

- **Chapter 04 (On-call and Toil)**: Provides evidence for: (a) tool-fragmentation /
  context-switching as the core incident friction (Claim 15) — a quantifiable target
  for AI-assisted reduction (the source gives no hard MTTR numbers, so pair with the
  PagerDuty coordination-tax framing rather than citing a figure); (b) the ambient
  awareness pattern (Claims 4, 12) as a way to cut the cognitive overhead of actively
  monitoring multiple tools; (c) the one-liner wrap-up (Claim 13) as toil reduction
  for closeout and debrief prep. All claims should carry the pre-launch caveat
  (Claims 2, 16).

## Extraction Notes

- The primary source is a single long-form blog post on incident.io's blog, authored
  by Chris Evans (identified in the page's author bio block and JSON-LD
  `BlogPosting` metadata: `"author":[{"@type":"Person","name":"Chris Evans"}]`,
  `datePublished":"2026-04-23"`). Full article text was extracted from the page's
  Next.js RSC payload (all `self.__next_f.push` chunks) and read end-to-end; every
  `Quote` above is copied character-for-character from that extracted text, including
  the em-dashes and curly apostrophes present in the source.
- This is an **eval replay** of the merged DeepSeek baseline note
  (`blog-incidentio-ai-sre-incident-run.md`, issue #3). The Hy3 read was performed
  independently from the raw source, not by copying the baseline. Where the two agree
  (e.g., the five novel patterns, the PagerDuty corroboration), that is convergence
  from the same source, not derivation. Differences worth noting for the Assayer:
  - The Hy3 read names the author (Chris Evans, Co-Founder & Field CTO) from the
    page metadata; the baseline left the author "uncredited."
  - The Hy3 read flags a nuance the baseline under-weighted: the proposed fix (Claim
    9) is a defensive "skip rendering" patch, not a root-cause contract fix — a
    toil-reduction pattern that can leave latent debt.
  - The Hy3 read grounds the coordination-tax / toil discussion in the article's own
    verbatim "too many tools, too much context switching" quote (Claim 15) rather
    than leaning on the linked definition page's MTTR figure, since that figure is
    not in the main article text.
- Only the main walkthrough was deeply read. The linked "AI SRE explained" capability
  page was not independently fetched for this eval; the four-step adoption path in
  Concrete Artifacts is included as a corroborating artifact sourced from the merged
  baseline's deeper read, and is flagged as such.
- The article is rich in screenshots (incident channel, Claude Code terminal, desktop
  app, generated debrief) but provides no raw code, no MCP configuration, no
  quantitative metrics, and no failure cases where AI SRE was wrong. It presents
  exactly one incident — a successful, linear resolution of a relatively simple
  frontend bug. This limits generalizability.
- The product is explicitly pre-launch; all claims should be read as design
  validation from internal dogfooding, not production evidence. `confidence_overall`
  of "anecdotal" reflects both the vendor source and the pre-launch status.
- No part of the source was paywalled. The page is publicly accessible.
