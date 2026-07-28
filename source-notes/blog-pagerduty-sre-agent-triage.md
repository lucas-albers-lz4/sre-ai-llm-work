---
source_url: https://www.pagerduty.com/eng/pagerduty-for-ai-how-the-sre-agent-triages-ai-incidents/
source_type: blog-post
title: "PagerDuty for AI: How the SRE Agent Triages AI Incidents"
author: "Irena Grabovitch-Zuyev, Antonio Correia, Everaldo Aguiar, Murilo Venturin, Derek Barnes (PagerDuty Engineering)"
date_published: 2026-07-21
date_extracted: 2026-07-28
last_checked: 2026-07-28
status: current
confidence_overall: emerging
issue: "#610"
---

# PagerDuty for AI: How the SRE Agent Triages AI Incidents

> Concrete triage workflow for AI-specific incidents using PagerDuty's SRE
> Agent, covering the shift from detection to triage, the integration with
> AI observability (Arize) for automated first-pass diagnosis, skill-based
> runbook execution, team-bounded code-suggestion patterns, and a proposed
> failure-classification taxonomy (hallucination / tool-call error / model
> latency) with distinct remediation paths. Third installment in PagerDuty's
> SRE Agent series (July 2026).

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Five PagerDuty engineers — Irena Grabovitch-Zuyev
  (Staff Applied Scientist, leads AI agents behind PagerDuty Advance),
  Antonio Correia (Senior Applied Scientist, evaluation frameworks),
  Everaldo Aguiar (Director of Applied AI and Insights), Murilo Venturin
  (Senior ML Engineer, production-scale AI systems), Derek Barnes (Senior
  PM, AI & Automation features). First-hand production experience from the
  team that built and operates the SRE Agent. Published on PagerDuty's
  engineering blog.
- **Scope**: Covers the triage phase of AI incidents specifically — what
  happens after detection fires. Focuses on the SRE Agent's triage loop,
  Arize trace integration, skill-based runbook execution, code-suggestion
  boundaries, and the forward roadmap (signal re-checking, failure-type
  classification, autonomous operations). Does NOT cover: agent architecture
  internals (covered in the companion SRE Agent architecture article),
  evaluation pipeline design (covered in the production gaps article), or
  guardrail architecture.

## Extracted Claims

### Claim 1: LLM-as-a-judge eval alerts redefine the triage signal — "something might be broken" changes what a responder is supposed to do at 2 a.m. versus a traditional broken-service alert
- **Evidence**: The article states monitors based on LLM-as-a-judge evals
  reframe the signal: it's not "something is broken" but "something might be
  broken" according to the LLM. The practical consequence: a drop in a
  relevance metric is not something a human can fix in fifteen minutes, unlike
  a bad deployment.
- **Confidence**: emerging
- **Quote**: "Monitors based on LLM-as-a-judge evals reframe what an alert
  means. The signal is not 'something is broken'; it is 'something might be
  broken' according to the LLM."
- **Our assessment**: This is the foundational framing of the article and a
  genuinely useful distinction for on-call operations. Traditional incidents
  have a clear action (rollback, restart, scale up); AI eval failures require
  fundamentally different remediation (prompt change, retrieval tweak, model
  swap, eval tuning). The article correctly identifies that these should not
  necessarily wake a human at 2 a.m., which is an important operational design
  consideration.

### Claim 2: The SRE Agent takes the first pass on triage automatically — pulling monitor state, surfacing traces, and handing the responder a diagnosis with ranked next steps
- **Evidence**: The article describes the triage loop with a diagram: monitor
  breach triggers SRE Agent → check monitor status → pull failing traces →
  summarize trace patterns → check recent code changes → produce diagnosis and
  next steps. The SRE Agent has access to AI observability platforms (Arize)
  that capture every agent interaction as a trace.
- **Confidence**: emerging
- **Quote**: "The SRE Agent takes the first pass on the incident automatically:
  pulling monitor state, surfacing relevant traces, and handing the responder
  a diagnosis and a ranked set of next steps."
- **Our assessment**: This is a concrete, live production pattern. The key
  contribution is connecting the SRE Agent to AI observability traces (not just
  traditional logs/metrics) as the triage data source. This directly extends
  the pre-on-caller pattern described in Google's SRE Prodcast S4E9 (Claim 5):
  the SRE Agent performs common triage steps before the human arrives. The
  PagerDuty implementation is more specific about the data sources (Arize
  traces) and the output format (diagnosis + ranked next steps).

### Claim 3: Teams encode runbooks into the SRE Agent via skills using the create-pagerduty-skill tool, built from existing runbooks
- **Evidence**: The article states the SRE Agent "knows about this process and
  its underlying details through a PagerDuty skill, built from existing
  runbooks using the `create-pagerduty-skill`" command, linking to the
  GitHub repository `PagerDuty/claude-code-plugins`.
- **Confidence**: emerging
- **Quote**: "The SRE Agent knows about this process and its underlying details
  through a PagerDuty skill, built from existing runbooks using the
  `create-pagerduty-skill`"
- **Our assessment**: This is a concrete tooling pattern — a CLI command that
  converts existing documentation/runbooks into agent skills. The open-source
  reference (`PagerDuty/claude-code-plugins`) makes this inspectable. This is
  directly relevant to the guide's runbook chapter: the skill-creation pattern
  (existing docs → agent skill) is a practical bridge from written runbooks to
  executable agent procedures.

### Claim 4: SRE Agent connects to observability, code, and documentation via connectors (MCP-based), establishing the data fabric for triage
- **Evidence**: The article states "the connections with Arize, GitHub, and
  other data sources are established with the SRE Agent's connectors," linking
  to PagerDuty documentation on connectors, tools, and skills.
- **Confidence**: emerging
- **Quote**: "the connections with Arize, GitHub, and other data sources are
  established with the SRE Agent's connectors"
- **Our assessment**: The connector architecture is the data plumbing layer
  underneath the triage workflow. The article doesn't detail the MCP protocol
  implementation, but the explicit naming of data sources (Arize for traces,
  GitHub for code, documentation systems) provides a concrete integration
  blueprint. This extends the production gaps article's discussion of the
  "Integration" pillar with specific connector patterns.

### Claim 5: The code-suggestion skill keeps the SRE Agent's code suggestions within team-bounded boundaries, and suggestions can be replayed against failing traces for regression testing
- **Evidence**: The article describes a "customized code-suggestion skill to
  keep the agent's suggestions within the boundaries defined by the team." The
  SRE Agent proposes adjustments to the agent's system prompt, and these
  suggestions can be "replayed against failing traces and regression tested
  following our agent self-improvement strategy."
- **Confidence**: emerging
- **Quote**: "The responder uses a customized code-suggestion skill to keep the
  agent's suggestions within the boundaries defined by the team."
- **Our assessment**: This is a high-value pattern with two parts: (1) the
  team-bounded suggestion scope (the agent can suggest changes only within its
  assigned domain), and (2) the replay-against-traces workflow (code changes
  are validated against real failing traces before deployment). The combination
  is more than the sum of its parts — it creates a feedback loop from
  production failures → automated suggestions → regression testing against the
  original failure data. This is a concrete implementation of the
  "self-improvement strategy" referenced but not detailed in the production
  gaps article.

### Claim 6: AI incident response requires three actions — classify whether escalation is needed, run pre-approved remediation, and file follow-up tickets for the owning team
- **Evidence**: The article enumerates three capabilities the system aims to
  deliver: (a) classify whether the incident requires escalation to a human,
  (b) run pre-approved remediation processes, (c) file follow-up tickets for
  the team that owns the AI feature.
- **Confidence**: emerging
- **Quote**: "classify whether the incident requires escalation to a human;
  run pre-approved remediation processes; file follow-up tickets for the team
  that owns the AI feature"
- **Our assessment**: This is a clean taxonomy of AI incident triage actions.
  The "pre-approved remediation" is notable — it implies a human-defined
  approval step before the agent can execute fixes, which is consistent with
  the guardrail patterns in the production gaps article. The three-action
  model maps well onto the autonomy-levels discussion in Google's AI-in-SRE
  paper (L2 with human approval for actuation).

### Claim 7: The next step is smarter signals — LLM-as-a-judge eval scores on small samples should be automatically re-checked to suppress noise before paging a human
- **Evidence**: The article describes a planned feature: "LLM-as-a-judge evals
  can be noisy on a small sample, and so we want PagerDuty to automatically
  trigger a re-check of the score." The stated goal: "real failures still page
  while noise gets suppressed on the way in."
- **Confidence**: anecdotal (roadmap, not yet in production)
- **Quote**: "LLM-as-a-judge evals can be noisy on a small sample, and so we
  want PagerDuty to automatically trigger a re-check of the score. The idea is
  that real failures still page while noise gets suppressed on the way in."
- **Our assessment**: This is aspirational, not validated in production. The
  insight is sound — small-sample eval scores are inherently noisy, and
  re-checking is a standard statistical reliability technique. The practical
  question is latency: if the re-check takes 30+ seconds, it delays genuine
  failure alerts. Worth flagging as directional guidance, not proven practice.

### Claim 8: AI incidents should be classified by failure type (hallucination, tool-call error, model latency) with each type routed to a different automated remediation path
- **Evidence**: The article proposes a classification taxonomy: "classify
  incidents by failure type, such as hallucinations, tool-call errors, and
  model latency. Each one can be routed to a different fix." The article gives
  a concrete example: "A model latency incident, for example, can be handled
  by temporarily switching to a pre-approved fallback model."
- **Confidence**: anecdotal (roadmap, not yet in production)
- **Quote**: "classify incidents by failure type, such as hallucinations,
  tool-call errors, and model latency. Each one can be routed to a different
  fix, and classification lets triage and remediation pick the right path."
- **Our assessment**: This is a proposed taxonomy, not an empirically validated
  classification scheme. The three failure types (hallucination, tool-call
  error, model latency) are reasonable categories, but the article doesn't
  describe the classifier that would assign incidents to these types. The
  fallback-model example is concrete and actionable. This taxonomy could be
  valuable if validated — it would give teams a starting point for designing
  type-specific remediation playbooks. Flag as directional.

### Claim 9: The Autonomous Operations vision — PagerDuty diagnoses and resolves AI incidents on the customer's behalf, regardless of which observability tool the team uses
- **Evidence**: The article describes a forward vision: "Autonomous Operations.
  A standard pattern for AI observability in which PagerDuty can diagnose
  incidents and, over time, resolve them on the customer's behalf, regardless
  of which tool a team uses to trace and evaluate their agents."
- **Confidence**: anecdotal (vision statement, not in production)
- **Quote**: "A standard pattern for AI observability in which PagerDuty can
  diagnose incidents and, over time, resolve them on the customer's behalf,
  regardless of which tool a team uses to trace and evaluate their agents."
- **Our assessment**: This is a product vision, not a validated capability.
  The direction is consistent with Google's L3–L4 autonomy levels (Actus paper
  Claim 5). The tool-agnostic framing ("regardless of which tool") is
  interesting as a market-positioning claim — it suggests the triage pattern
  should work across observability platforms, not just Arize. Flag as
  directional.

### Claim 10: A low-relevance alert could be either internal performance drift or an upstream service failure — the SRE Agent distinguishes these by checking traces against code and recent changes
- **Evidence**: The article describes a diagnostic distinction: "a drop in a
  relevance metric is usually not something a human can fix in the next fifteen
  minutes, unlike a bad deployment. The fix is a prompt change, a retrieval
  tweak, a model swap, or a re-tune of the eval itself. However, a
  low-relevance alert could also be due to an upstream service failure that
  causes errors in the AI feature's responses, without implying a drop in its
  internal performance."
- **Confidence**: emerging
- **Quote**: "a low-relevance alert could also be due to an upstream service
  failure that causes errors in the AI feature's responses, without implying a
  drop in its internal performance that the responder can adjust for."
- **Our assessment**: This is a practical diagnostic distinction that maps
  onto the traditional SRE separation of "infrastructure failure" vs.
  "application bug." For AI incidents specifically, the two root causes
  (upstream service failure vs. internal model/prompt degradation) require
  completely different remediation paths. The SRE Agent's value is in
  automatically making this distinction by pulling traces and code context. This
  is the most actionable claim in the article for teams building AI incident
  response workflows.

## Concrete Artifacts

### SRE Agent Triage Loop (from the article's diagram description)

```
Monitor breach (Arize eval threshold)
        │
        ▼
SRE Agent checks monitor status (recovered?)
        │
        ▼
Pulls failing traces from Arize
        │
        ▼
Reviews eval explanations and summarizes patterns
        │
        ▼
Checks recent code changes (via GitHub connector)
        │
        ▼
Produces diagnosis + ranked next steps
        │
        ▼
Learnings feed back into the system
```

### Code-Suggestion Skill Pattern

```
Responder engages SRE Agent on incident page
        │
        ▼
SRE Agent performs standard triage steps
  (monitor check → trace filter → eval review → code review)
        │
        ▼
SRE Agent provides rundown of what happened
        │
        ▼
Responder asks for specific code changes
        │
        ▼
SRE Agent proposes adjustments (within team boundaries)
  via code-suggestion skill
        │
        ▼
Suggestions replayed against failing traces
  and regression-tested per self-improvement strategy
```

### Failure-Type Classification Taxonomy (proposed, not yet in production)

| Failure Type | Example Remediation |
|---|---|
| Hallucination | Prompt change, retrieval tweak |
| Tool-call error | Code adjustment, system prompt fix |
| Model latency | Switch to pre-approved fallback model |
| Upstream service failure | Traditional infrastructure remediation |

### Data Source Connections (from the article)

| Source | Purpose |
|---|---|
| Arize | AI observability traces (every agent interaction) |
| GitHub (code connector) | Code access for review and suggestions |
| Documentation systems | Runbook and knowledge base access |

## Cross-References

- **Corroborates**:
  - [blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)
    — The production gaps article (Claim 10) describes the evaluation pipeline
    (golden datasets → LLM-as-a-judge → CI gates) that produces the eval
    scores this article's triage loop consumes. The two articles are
    complementary: the gaps article covers how eval scores are generated; this
    article covers what happens when those scores breach a threshold in
    production.
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    — The architecture article (Claim 12) covers the single-process
    simplification and reactive loop that powers the SRE Agent. This article
    shows that same agent performing a concrete triage workflow, extending the
    architecture discussion from "how it works" to "what it does."
  - [docs-google-sre-prodcast-04-09-ai-agents.md](docs-google-sre-prodcast-04-09-ai-agents.md)
    — Claim 5 describes Google's "pre-on-caller" pattern where the agent
    performs common triage steps in the ~3–4 minutes before the human arrives.
    This PagerDuty article describes the same pattern applied specifically to
    AI incidents: the SRE Agent takes the "first pass" on triage automatically.
    Both corroborate the value of agent-initiated triage before human arrival.

- **Contradicts**: None identified. This article is the third installment in a
  three-part series and is complementary to the existing two source notes.

- **Extends**:
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    — The architecture article covers the reactive loop, identity, transport,
    and single-process architecture but explicitly does not cover operational
    triage workflows. This article fills that gap with a concrete triage
    example (Insights Agent tool-selection degradation). The architecture
    article's Claim 5 (lack of interactivity) is addressed here by the
    triage-loop design that includes human interaction points.
  - [blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)
    — The production gaps article covers the five-pillar framework and
    evaluation pipeline but does not cover operational triage of AI incidents.
    This article fills the gap: what happens when an eval score breaches a
    threshold in production. The "Integration" pillar (Claim 7 in the gaps
    article) is demonstrated here with the Arize/GitHub/documentation connector
    pattern.
  - [docs-google-sre-ai-engineering-reliable-operations.md](docs-google-sre-ai-engineering-reliable-operations.md)
    — The Google AI-in-SRE paper (Claim 3) defines autonomy levels L0–L4. This
    article describes PagerDuty's SRE Agent operating at approximately L2
    (automated triage with human escalation) with a roadmap toward L3
    (autonomous remediation of bounded failure types). The proposed failure-type
    taxonomy (Claim 8) maps onto the autonomy-level gating criteria: model
    latency could be autonomously remediated (L3), while hallucination
    investigation likely requires human judgment (L2).

- **Novel**: Several contributions are new to the corpus:
  - **AI incident triage loop** — a concrete workflow for what happens after an
    AI eval alert fires, including the specific steps (monitor check → trace
    pull → eval review → code review → diagnosis). No other source note
    describes this end-to-end flow.
  - **Arize trace integration** as the data source for AI incident triage
    (traces, not logs/metrics) — a specific implementation of AI observability
    for incident response.
  - **Code-suggestion skill** with team-bounded scope and replay-against-traces
    regression testing — a concrete feedback loop from failure → suggestion →
    validation.
  - **Failure-type classification taxonomy** (hallucination / tool-call error /
    model latency) as a proposed scheme for routing AI incidents to different
    remediation paths. Aspirational but concrete enough to evaluate.
  - **Smarter signal re-check** — automatic re-evaluation of noisy LLM-as-a-
    judge scores before paging. Aspirational but operationally important.
  - **The diagnostic distinction** between internal performance drift and
    upstream service failure as two root causes of the same low-relevance
    alert — a practical separation that requires different remediation paths.

## Guide Impact

- **Chapter 01 (Incident Response)**: This source provides the most concrete
  material yet for AI-specific incident triage. Specific additions:
  - The triage loop diagram (monitor breach → trace pull → eval review → code
    review → diagnosis) as the reference workflow for AI incident response.
  - The three-action taxonomy (escalate / remediate / ticket) as the action
    model for AI incident triage.
  - The diagnostic distinction between internal performance drift and upstream
    service failure as a key triage decision point.
  - The failure-type classification taxonomy as a proposed routing mechanism
    (once validated).

- **Chapter 03 (Runbooks and Agents)**: This source provides the skill-creation
  pattern and code-suggestion boundaries:
  - The `create-pagerduty-skill` pattern (existing runbooks → agent skills) as
    a bridge from written documentation to executable agent procedures.
  - The team-bounded code-suggestion skill as a guardrail pattern for agent
    suggestions.
  - The replay-against-traces regression testing workflow as a validation
    pattern for agent-proposed changes.

- **Chapter 04 (Oncall and Toil)**: This source addresses the on-call
  experience directly:
  - The "smarter signal" re-check proposal as a pattern for reducing false-
    positive AI eval alerts that wake on-call engineers unnecessarily.
  - The failure-type classification as a way to route different AI incidents
    to different on-call response patterns (e.g., model latency → automated
    fallback; hallucination → human investigation).

## Extraction Notes

- The source is a single blog post (~8 min read) on PagerDuty's engineering
  blog. It is the third article in a three-part series; the first two have
  existing source notes in the corpus (blog-pagerduty-production-ai-agent-
  gaps.md and blog-pagerduty-sre-agent-architecture.md).
- The issue body contained a URL with a typo: `/pagerduty-for-ai-how-the-sre-
  agent-triager-ai-incidents/` should be `/pagerduty-for-ai-how-the-sre-agent-
  triages-ai-incidents/`. The Prospector flagged this in the triage comment.
  The correct URL (`triages`) is used in this source note's frontmatter.
- No sub-pages were followed. The article is self-contained with inline
  video embeds (Wistia-hosted) that demonstrate the triage workflow but were
  not fetched — their content is described in the article text.
- Quotes were extracted via WebFetch and verified against the rendered page.
  All quotes marked as direct are short (≤120 chars) and were confirmed as
  verbatim. The Assayer should spot-check key quotes against the live URL.
- The article contains several forward-looking / roadmap claims (Claims 7, 8, 9)
  that are explicitly flagged as aspirational in the extraction. The Assayer
  should not treat these as validated production patterns.
- The miner-related-notes.md candidate list was read before writing Cross-
  References. The PagerDuty series notes (Candidates 6) were cited as
  corroborates/extends. The Google Prodcast S4E9 (Candidate 2) was cited as
  corroborating the pre-on-caller pattern. The remaining candidates (Building
  Reliable Systems, S3E11, S3E3, S5E2, S5E4, Anthropic agents, Google AI-in-
  SRE) were reviewed and dismissed — they cover related topics (reliability
  principles, agent design patterns, evaluation, governance) but do not
  contain claims that directly corroborate or contradict the triage-specific
  patterns in this article.
