---
source_url: https://github.github.com/gh-aw/blog/2026-06-02-agent-of-the-day/
source_type: blog-post
title: "Agent of the Day – June 2, 2026: The Data Detective (Scout)"
author: GitHub Agentic Workflows team (gh-aw), bylined "By Copilot"
date_published: 2026-06-02
date_extracted: 2026-06-03
last_checked: 2026-06-03
status: current
confidence_overall: emerging
issue: "#1039"
---

# Agent of the Day – June 2, 2026: The Data Detective (Scout)

> Seventh entry in the "Agent of the Day" series — profiles Scout, an on-demand
> research agent (DispatchOps trigger, no pipeline integration, no writes) that
> diagnosed a token consumption doubling across gh-aw's 237+ workflow fleet by
> attributing root cause to a velocity problem (catalog growth outpacing optimization),
> not an efficiency problem; introduces the "seeing clearly" mission type for
> agents whose entire value is structured insight rather than action.

## Source Context

- **Type**: blog-post (seventh "Agent of the Day" entry from the official GitHub
  Agentic Workflows blog; bylined "By Copilot" — gh-aw convention for AI-authored
  posts. Each post profiles a single production agent with concrete run data. This
  entry is distinct from all six prior entries: it profiles an on-demand research
  agent triggered by a human dispatch (not a schedule, not an event) rather than
  any automated trigger. The post is subtitled "The Data Detective.")
- **Author credibility**: The gh-aw blog is the official publication of GitHub's
  Agentic Workflows platform team. Run #26709587451 (May 31, 2026) is a specific,
  independently verifiable GitHub Actions run URL. Metrics (8 turns, 8.1 minutes,
  37 tool types, 61 network requests, token consumption data) are instrumentation
  data from the live `github/gh-aw` repository, not marketing copy. The token
  consumption data covering April and May 2026 is drawn from the
  `agentic-token-audit` and `agentic-token-optimizer` workflows, which are
  production instrumentation for the gh-aw fleet. High credibility for first-party
  platform claims.
- **Scope**: Profiles one run of Scout (Run #26709587451, May 31, 2026) responding
  to a research prompt on issue #36100 about token usage trends across April and
  May. Covers: Scout's mission and operational boundaries, the key findings (token
  consumption trajectory, run-count flatness, per-run growth, top consumers, catalog
  growth, velocity/efficiency diagnosis), Scout's research mechanics (tool diversity,
  turn count, duration, network footprint), data quality caveats, and the "seeing
  clearly" value framing. Does NOT cover: Scout's full YAML workflow configuration;
  how it is invoked or who can invoke it; cost of Scout's own run (token count not
  stated); the specific ET metric vs. raw token count distinction; or how the
  `agentic-token-optimizer` selects optimization targets.

## Extracted Claims

### Claim 1: Scout is a seventh distinct agent archetype in the series — an on-demand research agent triggered by human dispatch, with no writes, no PR generation, and no pipeline integration

- **Evidence**: Explicit characterization of Scout's trigger and operational
  boundaries in the post's overview paragraph; contrasted with pipeline agents
  that file PRs or leave comments.
- **Confidence**: settled (first-party characterization; the run data confirms
  zero PRs opened and a research report as the sole output)
- **Quote**: "Scout is gh-aw's on-demand research agent — a workflow you invoke
  with a question and come back to with an answer."
- **Our assessment**: The six prior archetypes were: event-driven write-enabled
  moderation (AI Moderator, May 15), weekday-scheduled read-only audit with
  agent-driven skip (Architecture Guardian, May 20), weekly scheduled fleet
  meta-orchestration (Agent Performance Analyzer, May 27), daily-scheduled
  write-enabled codemod (Dead Code Removal Agent, May 28), hybrid-trigger
  label-and-report triage (Auto-Triage Issues, May 29), and nightly forensic
  security scanner (Daily Security Red Team Agent, June 1). Scout adds a seventh
  position: on-demand (human-dispatched), read-only, analysis-only. The trigger
  is a human decision about when to ask a question — not a schedule, not a
  repository event. For Ch02 (Harness Engineering): add on-demand research as
  a seventh named agent archetype, distinct from scheduled and event-driven agents.
  The key distinguishing features: human-timing trigger (DispatchOps), no pipeline
  integration, research report as the sole output.

### Claim 2: Scout's operational posture is explicitly bounded — it reads, reasons, and reports; it does not file PRs or leave comments as part of a pipeline

- **Evidence**: Direct statement of Scout's operational boundaries in the post's
  Scout Overview section.
- **Confidence**: settled (first-party description; run data confirms no PR outputs)
- **Quote**: "It doesn't file PRs or leave comments as part of a pipeline. It
  reads, reasons, and reports, turning an open-ended research prompt into
  structured evidence a team can actually act on."
- **Our assessment**: "Reads, reasons, and reports" is the most succinct
  statement of the research-agent posture in the corpus. Prior read-only agents
  produce no pipeline outputs (Architecture Guardian calls `safeoutputs.noop`,
  Agent Performance Analyzer produces a fleet health report). Scout differs: it
  produces one structured research artifact, posted to the issue that triggered
  it, rather than interacting with the agent pipeline at all. For Ch02: distinguish
  the research-agent read-only posture from other read-only postures — research
  agents exit the pipeline model entirely. Their sole deliverable is a structured
  evidence document. "Structured evidence a team can actually act on" sets the
  quality bar: not raw data, not a narrative summary, but evidence with enough
  structure to drive decisions.

### Claim 3: Daily token consumption at the gh-aw fleet level nearly doubled over two months — from ~80.1M tokens/day in April to ~101.8M tokens/day in late May, peaking at 138 million on May 29

- **Evidence**: Specific instrumentation metrics from Scout's analysis of the
  `agentic-token-audit` and `agentic-token-optimizer` workflows across April and
  May 2026.
- **Confidence**: settled (first-party instrumentation data from the live gh-aw
  repository; the source describes this as the dataset Scout was given to analyze)
- **Quote**: "The headline: daily token consumption in gh-aw **nearly doubled**
  over two months, peaking at **138 million tokens on May 29**"
- **Our assessment**: The trajectory is:
  - April 2026 (21 days): ~80.1M tokens/day average, ~713 action-min/day
  - Early May (days 1–5): ~62.1M tokens/day average
  - Late May (days 20–29): ~101.8M tokens/day average, ~900 action-min/day
  - Peak: 138M tokens on May 29
  
  The early-May dip followed by a late-May surge suggests the trajectory is not
  monotone — there are structural changes occurring within the period. For Ch04
  (Operations) and Ch07 (Cost Management): this data provides a concrete calibration
  point for fleet-scale AI agent token consumption. A fleet of 237+ workflows
  consuming 80–138M tokens/day is a production-scale reference for practitioners
  planning fleet operations. Note the blind-spot window (May 6–19, see Claim 9)
  — the early-May vs late-May comparison has a 14-day gap.

### Claim 4: Run counts at fleet scale stayed nearly flat (capped near 100/day by the collector's limit) while token consumption grew — meaning per-run cost growth, not more runs, is the driver

- **Evidence**: Specific finding from Scout's analysis explicitly contrasting the
  run count trajectory with the token consumption trajectory.
- **Confidence**: settled (direct from Scout's multi-month analysis with specific
  constraint stated: the 100/day collector cap)
- **Quote**: "Run counts stayed nearly flat the whole time — capped near 100/day
  by the collector's limit." and "More runs weren't the culprit. The growth was
  coming from _within_ each run."
- **Our assessment**: This is a critical diagnostic split. The two variables that
  drive total token consumption — run count and per-run cost — can move independently.
  Scout's finding establishes that at gh-aw scale, the run count was artificially
  capped (the collector's rate-limit ceiling), so the only variable that could
  explain growing total consumption was per-run cost. This matters for intervention:
  rate-limiting runs would not have addressed the growth; per-run optimization
  is required. For Ch04 and Ch07: when investigating a token cost spike, always
  decompose "run count" vs. "per-run cost." The two respond to different
  interventions — rate limiting reduces runs; prompt optimization, turn-count
  reduction, and context trimming reduce per-run cost. A monitoring dashboard that
  shows only total consumption masks which lever to pull.

### Claim 5: The root cause of the token consumption growth is a velocity problem — new workflows arriving faster than optimizations land — not an efficiency problem

- **Evidence**: Explicit root-cause attribution in Scout's research report; the
  specific framing of "velocity" vs. "efficiency" as two competing diagnostic
  hypotheses.
- **Confidence**: emerging (Scout's attribution; the velocity interpretation is
  supported by the catalog growth data — 111 new .md files — but the post does
  not provide a per-workflow efficiency trend to rule out efficiency decay independently)
- **Quote**: "new workflows are arriving faster than optimizations land, so the
  net curve still bends upward."
- **Our assessment**: The velocity/efficiency diagnostic framework is the core
  analytical contribution of this source. Two hypotheses can explain a growing
  token bill: (1) efficiency problem — existing workflows are consuming more per
  run (prompt bloat, turn count drift, unoptimized patterns); (2) velocity problem
  — new workflows are being added faster than existing ones are optimized. Scout
  diagnoses type (2): the `agentic-token-optimizer` IS working (see Claim 6), but
  catalog growth (111 new .md files, per Claim 8) outpaces it. The interventions
  differ: efficiency problems require per-workflow prompt/turn optimization; velocity
  problems require catalog governance (per-workflow budgeting, token caps for new
  workflows, optimization gates before launch). For Ch07 (Cost Management): the
  velocity/efficiency diagnostic is a named root-cause framework for fleet cost
  spikes. Present both hypotheses before attributing; interventions are fundamentally
  different.

### Claim 6: Closed-loop accountability is visible at the fleet level — the agentic-token-optimizer is flagging concrete savings targets, confirming the optimization feedback loop is functional, though not keeping pace with catalog growth

- **Evidence**: Specific acknowledgment in Scout's report of the optimizer's
  functioning; the silver lining framing implies both that the optimizer is working
  and that it is insufficient alone.
- **Confidence**: anecdotal (one analysis period; the optimizer's effectiveness
  across multiple periods and its conversion rate from flag to implemented savings
  is not specified in this post)
- **Quote**: "There's a silver lining. The `agentic-token-optimizer` workflow is
  doing its job — flagging concrete savings targets."
- **Our assessment**: The optimizer is a closed-loop component of the fleet's
  cost management system. Without Scout's analysis, practitioners would not know
  whether the optimizer is keeping pace with catalog growth or being overwhelmed
  by it. This demonstrates the layered compound-agent pattern: optimizer (flags
  targets) + scout (measures whether optimization pace is sufficient). Either agent
  without the other is less effective — the optimizer without Scout is "working
  but invisible"; Scout without the optimizer is "analysis without a countermeasure."
  The post's "without that, optimization work is guesswork" quote captures this:
  Scout's fleet-level view is what makes the optimizer's work legible. For Ch04:
  deploy analysis agents alongside optimization agents to measure optimization pace
  against growth. Optimization without fleet-level visibility into whether it is
  keeping up is a feedback loop without closure.

### Claim 7: Scout executed its research in 8 turns over 8.1 minutes using 37 distinct tool types, drawing on Tavily's research suite — with 61 network requests and zero firewall blocks

- **Evidence**: Specific run metrics from Run #26709587451 (May 31, 2026).
- **Confidence**: settled (first-party instrumentation data for the specific run)
- **Quote**: "It used **37 distinct tool types** across 8 turns, drawing on
  Tavily's research suite"
- **Our assessment**: 37 distinct tool types is the highest tool diversity cited
  in the Agent of the Day series. Comparison with other entries:
  - Architecture Guardian (May 20): small number of file-check tools, 3 reasoning
    turns, 123k tokens
  - Agent Performance Analyzer (May 27): specialized fleet-scoring toolset, 10.7
    minutes, 12.2M effective tokens
  - Daily Security Red Team Agent (June 1): 37 bash calls, 12,465 commits unshallowed,
    1,076,688 tokens
  - Scout: 37 distinct tool types, 8 turns, 8.1 minutes — not described as a
    high-token run (no token count stated)
  
  The tool diversity is explained by the research mandate: Scout needed search
  (find relevant data), crawl (extract from data sources), extract (parse structured
  data from pages), map (navigate data structures), and research synthesis tools —
  alongside standard GitHub tools. Zero firewall blocks on 61 requests distinguishes
  Scout from pipeline agents (Architecture Guardian: 38% block rate; Agent Performance
  Analyzer: 27% block rate). Data-detective agents with purely read-only research
  posture appear to have a cleaner network profile, with no out-of-scope resource
  attempts. For Ch02: research agents require a broader, more heterogeneous toolset
  than task-execution agents. For Ch04: zero firewall blocks on a research agent
  is a useful baseline — if a research-only agent begins generating blocks, it may
  be drifting from its intended read-only scope.

### Claim 8: The primary output of an on-demand research agent is a structured research report posted directly to the issue that triggered the investigation, complete with a data table

- **Evidence**: Direct description of Scout's output format and delivery mechanism.
- **Confidence**: settled (stated explicitly; consistent with the DispatchOps
  pattern in which the investigation originates in a specific issue)
- **Quote**: "The result was a structured research report posted directly to [issue
  #36100], complete with a data table."
- **Our assessment**: Issue-targeted reporting is the correct output pattern for
  a DispatchOps-triggered research agent. The investigation started with a research
  prompt on issue #36100; the findings land in issue #36100. This creates a
  self-contained audit trail: question and answer in the same thread, with the
  data table making findings machine-readable for downstream agents or humans. The
  alternative — a separate report repository, a Slack message, or a new issue —
  severs the connection between the question context and the answer context. For
  Ch02: on-demand research agents should always deliver output to the requesting
  context (the issue, PR, or discussion that triggered the investigation), not to
  a separate reporting channel. Structure matters: a data table enables specific
  rows to be cited in subsequent decisions or passed to action agents.

### Claim 9: Data quality gaps in agentic observability data must be surfaced explicitly in research agent outputs — Scout documents the May 6-19 blind-spot window caused by API rate-limit failures

- **Evidence**: Explicit caveat in Scout's report about the 14-day gap in the
  analysis dataset.
- **Confidence**: settled (the gap is directly acknowledged in the source)
- **Quote**: "caveats about data quality during the blind-spot window (May 6–19)"
- **Our assessment**: May 6-19 represents approximately 24% of the 56-day analysis
  period (April 1 – May 29). This gap was caused by API rate-limit failures in
  the data collection pipeline — a failure mode of the observability infrastructure
  itself, not of the workflows being observed. Scout's explicit documentation of
  this gap is a methodological requirement: any analysis that presents trends
  across a period containing a large data gap without acknowledging it is
  misleading. The early-May (~62.1M/day average) figure in Claim 3 is based on
  only 5 days; the comparison between April average and late-May average is more
  reliable than an April-to-early-May comparison. For Ch02 and Ch04: research
  agents MUST document data quality caveats as a first-class component of their
  output. A finding without a confidence qualification is an incomplete output.
  Blind-spot windows caused by observability infrastructure failures should be
  named with dates, root cause (if known), and impact on the analysis.

### Claim 10: "Seeing clearly" is a legitimate standalone mission type for agents — reading, reasoning, and reporting without taking action is described as some of the highest-leverage work in a complex system

- **Evidence**: Explicit framing in the article's conclusion; stated as a design
  principle about what makes an agent valuable.
- **Confidence**: emerging (author framing and design philosophy; no measurement
  of relative leverage of analysis-only vs. action-taking agents is provided)
- **Quote**: "Scout is a good reminder that not every agent needs to _do_ something
  to be valuable. Some of the highest-leverage work in a complex system is the
  work of _seeing clearly_"
- **Our assessment**: This is the most direct statement in the series corpus of
  pure analysis as a first-class mission type. Prior Agent of the Day entries
  frame agent value in terms of outputs that change state: PRs (Dead Code Removal),
  labeled issues (Auto-Triage Issues), a fleet health report with automated issue
  filing (Agent Performance Analyzer), security clean bill of health (Daily
  Security Red Team). Scout's value is the analysis itself — the structured insight
  that makes the fleet's cost trajectory legible and attributable. "Without that,
  optimization work is guesswork" makes the leverage argument explicit: the
  optimizer exists, is working, but without Scout's analysis practitioners would
  not know whether optimization is keeping pace with catalog growth. This parallels
  `blog-ghaw-agent-of-the-day-2026-05-27.md` Claim 10 ("The value of a
  meta-orchestrator is not that it prevents incidents. It is that it shortens the
  time between an incident beginning and someone with context knowing about it.")
  — both articulate value as the compression of visibility lag rather than
  prevention of the underlying condition. For Ch02 (Harness Engineering): add
  "observability and business intelligence" as a named mission type for agents
  whose sole deliverable is structured insight. For Ch05 (Team Adoption): "seeing
  clearly" is a stakeholder-accessible framing for the value of research agents
  to non-technical audiences — finance and leadership can understand "we deployed
  an agent to explain why our AI bill doubled" more readily than a technical
  explanation of optimization meta-agents.

## Concrete Artifacts

### Scout: Run Profile (May 31, 2026)

```
Agent:            Scout ("gh-aw's on-demand research agent")
Role:             On-demand research — investigates open-ended prompts and
                  returns structured evidence; no PR generation, no pipeline
                  integration
Subtitle:         "The Data Detective"
Run ID:           26709587451
Date:             2026-05-31
Research prompt:  Issue #36100 — investigate token usage trends from the
                  agentic-token-audit and agentic-token-optimizer workflows
                  across April and May

Execution:
  Agentic turns:        8
  Duration:             8.1 minutes
  Tool types used:      37 distinct types
    — including Tavily's research suite (search, crawl, extract, map, research)
  Network requests:     61
  Firewall blocks:      0

Output:
  Structured research report posted to issue #36100, complete with a data table
```

*Source: GitHub Agentic Workflows blog, "Agent of the Day – June 2, 2026"*

### Token Consumption Profile: April–May 2026 (from Scout's analysis)

```
Period                    Daily avg (tokens)  Daily avg (action-min)  Notes
------------------------  ------------------  ----------------------  ------
April 2026 (21 days)          ~80.1M                ~713              Full month sample
Early May (days 1–5)          ~62.1M               (not stated)       Only 5 days; pre-gap
[Blind spot: May 6–19]          —                    —                API rate-limit failure
Late May (days 20–29)         ~101.8M               ~900              10-day sample
Peak (single day):            138M tokens on May 29

Run count (all periods):   Capped near 100/day by collector's limit — stayed
                           nearly flat throughout
Growth driver:             Per-run cost growth ("coming from within each run"),
                           not run count growth
Root cause:                Velocity problem — new workflows arriving faster than
                           optimizations land
```

*Source: GitHub Agentic Workflows blog, "Agent of the Day – June 2, 2026"*

### Top Token Consumers (May 29, 2026 — peak day)

```
Workflow                   Tokens        Runs    Turns/run (avg)
-------------------------  ----------    -----   ---------------
PR Sous Chef               15.7M         5       ~186
Safe Output Health Monitor  8.7M         1       (not stated)
Go Logger Enhancement       8.5M         1       (not stated)

Catalog metrics:
  New .md files added (April → May):   ~111 new agentic workflow .md files
  Total fleet size:                    237+ workflows
```

*Source: GitHub Agentic Workflows blog, "Agent of the Day – June 2, 2026"*

### Velocity vs. Efficiency Root-Cause Diagnostic (from Scout's report)

```
Hypothesis A: Efficiency problem
  — Existing workflows consuming more tokens per run (prompt bloat, turn drift)
  — Evidence: agentic-token-optimizer IS working, flagging concrete savings targets
  — Verdict: Partially true, but not the primary driver

Hypothesis B: Velocity problem
  — New workflows added faster than existing workflows are optimized
  — Evidence: ~111 new .md files added April → May; total fleet now 237+
  — Verdict: Primary driver — "new workflows are arriving faster than optimizations
    land, so the net curve still bends upward."

Closed-loop status: The agentic-token-optimizer is functional (silver lining),
but insufficient alone to offset catalog growth at current velocity.

Intervention implications:
  Efficiency problem → per-workflow prompt/turn optimization
  Velocity problem   → catalog governance: per-workflow token budgets, caps
                       for new workflows, or optimization gates before launch
```

*Source: GitHub Agentic Workflows blog, "Agent of the Day – June 2, 2026"*

## Cross-References

- **Corroborates**:
  - `blog-ghaw-agent-of-the-day-2026-05-27.md` Claim 10 ("The value of a
    meta-orchestrator is not that it prevents incidents. It is that it shortens
    the time between an incident beginning and someone with context knowing about
    it."): Scout's "seeing clearly" mission (Claim 10 here) is the same insight
    applied to cost intelligence. Both the May 27 Agent Performance Analyzer and
    Scout derive their value from compressing visibility lag — the meta-orchestrator
    shortens incident detection time; Scout makes a two-month cost trajectory
    legible and attributable. Neither agent prevents the underlying condition;
    both make it visible faster than unaided observation would.
  - `docs-ghaw-cost-management.md` (the Agentic Cost Optimization meta-agent
    pattern, "introduces the Agentic Cost Optimization pattern — a meta-agent
    that uses the `agentic-workflows` MCP tool to automatically propose
    cost-reducing frontmatter changes"): The `agentic-token-optimizer` mentioned
    in Scout's findings (Claim 6 here) appears to be the production instantiation
    of this meta-agent pattern. Scout provides the fleet-level analysis layer that
    measures whether the optimizer is keeping pace with growth — the two together
    implement the full cost-management feedback loop: detect (optimizer), measure
    pace (Scout).

- **Extends**:
  - `blog-ghaw-agent-of-the-day-2026-05-15.md` through
    `blog-ghaw-agent-of-the-day-2026-06-01.md` (the prior six Agent of the Day
    entries): Scout adds a seventh archetype to the series taxonomy. The seven
    archetypes now span: trigger (event / weekday-schedule / weekly-schedule /
    daily-schedule / hybrid / nightly-cron / on-demand-dispatch) × posture
    (write-enabled / read-only / strict-mode / analysis-only). The on-demand
    dispatch position is entirely new — all prior archetypes use automated
    triggers; Scout is the first to use a human-timing trigger.
  - `docs-ghaw-dispatch-ops.md` (the DispatchOps pattern reference, which
    documents `workflow_dispatch` as "a human-timing-judgment primitive"): Scout
    uses the DispatchOps pattern as its trigger mechanism. The dispatch-ops
    reference establishes `gh aw run --wait` as the synchronous CLI invocation
    primitive; Scout's research runs embody this: a human decides when to invoke
    it, with what question, rather than an automated trigger. The dispatch-ops
    pattern + research-agent posture combination is documented here for the first
    time in the Agent of the Day series.
  - `docs-ghaw-effective-tokens-specification.md` (the Effective Tokens metric
    specification, which "explicitly carries no dependency on billing or pricing
    systems by design"): Scout's analysis uses raw token counts from the
    `agentic-token-audit` workflow, not the weighted ET metric. The ET spec
    separates token accounting from cost context; Scout's analysis is exactly
    the cost-context layer that ET deliberately does not provide. The two
    sources are complementary: ET is the normalized accounting metric; Scout's
    fleet trend analysis is the business intelligence layer that makes ET data
    actionable.
  - `blog-ghaw-agent-of-the-day-2026-05-27.md` Claim 9 ("Meta-orchestrating a
    fleet of 236 workflows requires processing at a fundamentally different token
    scale — 12.2 million effective tokens in 10.7 minutes for a single analysis
    run"): Scout investigated a similar fleet-level question in 8 turns / 8.1
    minutes with no token count stated — likely substantially less than 12.2M
    effective tokens. This confirms that the two agents occupy different cost
    tiers: the Agent Performance Analyzer fans out across the entire fleet,
    scoring each workflow group; Scout synthesizes fleet-level trends from a
    targeted data audit. Research agents are not necessarily in the same token
    cost tier as fleet meta-orchestrators even when asking fleet-level questions.

- **Contradicts**: None identified. The Prospector's triage notes flagged that
  `docs-ghaw-agent-factory-status.md` mentions Scout as a tool but not as a
  production observability agent — this is an extension, not a contradiction.
  The Agent Performance Analyzer (May 27) and Scout both perform fleet-level
  observability, but the Agent Performance Analyzer is scheduled and scores
  quality/effectiveness/ecosystem health, while Scout is on-demand and investigates
  cost trends. They are complementary observability agents, not redundant ones.
  No contradiction issue warranted.

- **Novel**:
  - **On-demand (DispatchOps) trigger as a seventh agent archetype** (Claim 1):
    All six prior Agent of the Day entries use automated triggers (event, schedule,
    nightly cron, hybrid). Scout is the first profiled agent using a human-dispatch
    trigger — the human decides when to ask, with what question.
  - **"Reads, reasons, reports" as the named three-verb posture for research
    agents** (Claim 2): The formulation is new to the corpus. Prior read-only
    posture descriptions use domain-specific framing (skip-when-idle for
    Architecture Guardian; fleet-scoring for Agent Performance Analyzer). "Reads,
    reasons, reports" is a generic three-verb description of the research-agent
    posture applicable across domains.
  - **Velocity vs efficiency as a named root-cause diagnostic framework for cost
    spikes** (Claim 5): No prior corpus source names these two competing hypotheses
    or their different intervention implications. The diagnostic framework — decompose
    "run count" vs "per-run cost" → attribute to velocity (catalog growth) or
    efficiency (per-run degradation) → intervene accordingly — is new.
  - **Run-count vs per-run-cost decomposition as a cost investigation method**
    (Claim 4): Prior cost sources (docs-ghaw-cost-management.md, docs-ghaw-effective-
    tokens-specification.md) document how costs are computed; this is the first
    source to explicitly name run-count vs per-run-cost as two distinct diagnostic
    dimensions during cost investigation.
  - **"Seeing clearly" as a named, standalone mission type** (Claim 10): The
    explicit argument that analysis without action is high-leverage work — and the
    naming of this as a legitimate first-class agent mission — is new to the corpus.
    Prior sources treat analysis as a precursor to action; this source names it as
    sufficient on its own.
  - **Zero firewall blocks on a research-only agent** (Claim 7): The Agent of the
    Day series has now documented: 38% block rate (Architecture Guardian, single
    scheduled run), 27% block rate (Agent Performance Analyzer, fleet-level),
    and 0% block rate (Scout, on-demand research). The correlation — read-only
    data-detective agents show clean network profiles — is a new pattern.
  - **Data quality gap documentation as a required component of research output**
    (Claim 9): Prior agents produce outputs (health scores, filed issues, PRs) that
    don't require confidence qualifications. Scout is the first profiled agent that
    explicitly documents blind-spot windows with dates and root cause in its output.
    This names a quality requirement for analysis-output agents that does not apply
    to action-output agents.
  - **Issue-targeted structured reporting as the output delivery pattern for
    on-demand research agents** (Claim 8): Posting findings to the same issue
    that hosted the research prompt is the natural pattern for DispatchOps-triggered
    agents; this is the first source to explicitly describe and demonstrate it.

## Guide Impact

- **Chapter 02 (Harness Engineering)**:
  - Add on-demand research as a seventh named agent archetype (Claim 1): trigger =
    human dispatch (DispatchOps), posture = reads-reasons-reports, output = one
    structured research report. Distinguish from scheduled observability agents
    (Agent Performance Analyzer) and event-driven agents. The defining feature:
    a human decides when to ask; the question drives the scope.
  - Add "observability and business intelligence" as a named agent mission type
    (Claim 10): alongside write-enabled (codemod, PR), read-only-with-skip (audit),
    meta-orchestration (fleet health), and strict-mode (security scanning), add
    analysis-only (research report) as a first-class mission type where the sole
    deliverable is structured insight.
  - Add tool diversity as a research-agent harness requirement (Claim 7): research
    agents require a broader, more heterogeneous toolset than task-execution agents.
    Scout used 37 distinct tool types including external research suites (Tavily)
    to synthesize fleet-wide trends from unstructured data. Budget for wider MCP
    and tool grants when configuring research agents.
  - Add issue-targeted reporting as the output delivery pattern for DispatchOps-
    triggered research agents (Claim 8): findings should be posted to the issue
    that hosted the research prompt, as a structured report with data tables. Avoid
    separate reporting channels that sever the question-context from the answer-context.

- **Chapter 04 (Operations)**:
  - Add run-count vs per-run-cost decomposition as a first step in cost spike
    investigation (Claim 4): monitor both separately. A fleet with a capped run
    count and growing total consumption has a per-run problem; rate-limiting runs
    does not address it. Recommend tracking both dimensions in operational dashboards
    alongside total consumption.
  - Add "optimization without fleet-level visibility is guesswork" as a design
    principle for deploying cost optimization meta-agents (Claim 6): pair every
    optimization agent with an analysis agent that measures whether optimization
    pace is keeping up with catalog growth. The feedback loop is incomplete if the
    optimization output cannot be measured against a fleet-level growth signal.
  - Add data quality gap documentation as an operational requirement for research
    agent outputs (Claim 9): agents deployed for fleet observability must
    explicitly surface blind-spot windows — periods where the data collection
    infrastructure failed — with dates, root cause, and impact on analysis validity.

- **Chapter 05 (Team Adoption)**:
  - Add "seeing clearly" as a stakeholder-accessible framing for the value of
    analysis agents (Claim 10): non-technical stakeholders (finance, leadership)
    can understand "we deployed an agent to diagnose why our AI bill doubled" more
    readily than a technical description of cost optimization meta-agents. Frame
    adoption of research agents around the "visibility as leverage" argument:
    optimization without visibility into whether it is working is guesswork.

- **Chapter 07 (Cost Management)**:
  - Add Scout's fleet cost data as a calibration point (Claim 3): 237+ workflows
    consuming 80–138M tokens/day is a production-scale reference. The late-May
    average of ~101.8M tokens/day with ~900 action-min/day provides planning
    benchmarks for practitioners building fleets approaching gh-aw's scale.
  - Add the velocity/efficiency root-cause framework as the primary diagnostic for
    fleet cost spikes (Claim 5): when total token consumption grows, decompose
    into run-count growth vs per-run growth, then attribute per-run growth to
    velocity (new workflows, catalog expansion) or efficiency (per-workflow
    degradation). Interventions differ: velocity → catalog governance, token
    budgets per workflow category; efficiency → per-workflow optimization campaigns.
  - Reference PR Sous Chef (15.7M tokens, ~186 turns/run across 5 runs on May 29)
    and Safe Output Health Monitor (8.7M tokens, single run) as per-workflow cost
    outlier data points. High per-run cost at 186 turns/run indicates a
    high-turn-count workflow as a cost concentration risk; single-run workflows
    at 8.7M tokens indicate deep single-session analysis as another cost pattern.

## Extraction Notes

1. **Seventh "Agent of the Day" entry**: The series has now profiled seven distinct
   archetypes: event-driven moderation (May 15, AI Moderator), scheduled audit
   with skip logic (May 20, Architecture Guardian), scheduled meta-orchestration
   (May 27, Agent Performance Analyzer), scheduled write-enabled codemod (May 28,
   Dead Code Removal Agent), hybrid-trigger issue triage (May 29, Auto-Triage Issues),
   nightly forensic security scanner (June 1, Daily Security Red Team Agent), and
   on-demand research (June 2, Scout). The taxonomy now spans all four trigger types:
   event, schedule (daily/weekly/nightly), hybrid, and human-dispatch.

2. **Scout's own token cost not stated**: Unlike all prior Agent of the Day entries,
   this post does not state Scout's token consumption for the run. The May 27 entry
   documented 12.2M effective tokens; the June 1 entry documented 1,076,688 tokens.
   Scout's cost is conspicuous by its absence — it may be modest given the 8-turn
   / 8.1-minute profile, but this cannot be confirmed from the source.

3. **Verbatim quotes via multiple targeted WebFetch passes**: Four separate WebFetch
   calls were made with different prompts targeting different sections of the article.
   Quotes returned consistently with identical or highly consistent wording across
   at least two calls are included. The Assayer should spot-check key quotes —
   particularly Claims 1, 2, 4, 5, and 10 — against the source URL, as WebFetch
   returns are processed by a language model and may not be character-for-character
   accurate despite consistent returns.

4. **No sub-pages followed**: The post does not appear to link to substantive
   sub-pages beyond the GitHub repository reference. The source is self-contained.

5. **No contradictions filed**: Reviewed `blog-ghaw-agent-of-the-day-2026-05-27.md`
   (Agent Performance Analyzer), `docs-ghaw-effective-tokens-specification.md`,
   `docs-ghaw-cost-management.md`, `docs-ghaw-dispatch-ops.md`, and CONTRADICTIONS.md.
   The Agent Performance Analyzer and Scout both observe fleet-level metrics but
   focus on different dimensions (quality/ecosystem health vs. token cost trends)
   and use different triggers (scheduled vs. on-demand). No material opposition to
   any existing claim. No contradiction issue warranted.

6. **PR Sous Chef at 186 turns/run**: The 186-turn average per run for PR Sous Chef
   is the highest turn count per agent run cited in the entire corpus. For context:
   the AI Moderator (May 15) used 16 turns; the Architecture Guardian (May 20) used
   3 turns for a skip decision; the Agent Performance Analyzer (May 27) used turns
   across an entire fleet analysis run. A single PR Sous Chef run at ~186 turns
   suggests either extremely complex PRs being reviewed, extensive back-and-forth
   in a multi-step pipeline, or possible turn-count drift that the agentic-token-
   optimizer would correctly flag as an optimization target.
