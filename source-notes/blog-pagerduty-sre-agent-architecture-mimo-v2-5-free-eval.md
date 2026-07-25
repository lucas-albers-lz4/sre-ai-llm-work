---
source_url: https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
source_type: blog-post
title: "Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation"
author: "Viktor Vasylkovskyi, Micah Mayo, Ralph Bird (PagerDuty Engineering)"
date_published: 2026-06-24
date_extracted: 2026-07-25
last_checked: 2026-07-25
status: current
confidence_overall: emerging
issue: "#1-mimo-v2-5-free-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> PagerDuty engineers describe the architectural evolution of their SRE Agent
> from a single-agent monolith to a reactive multi-agent system — covering
> context rot, instruction overload, LangGraph BSP limitations, a custom
> reactive loop with priority queue and lock serialization, and the
> counterintuitive single-process simplification for IO-bound agent workloads.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three PagerDuty engineers — Viktor Vasylkovskyi
  (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from concept to GA),
  Ralph Bird (Principal ML Engineer, focused on AI agents and LLM observability).
  First-hand production experience building the system described.
- **Scope**: Full architectural journey — single-agent failure modes, three
  execution models evaluated, custom reactive loop built from first principles,
  and simplification from distributed to single-process architecture. Does NOT
  cover: evaluation/accuracy metrics, cost data, specific model choices, or
  hallucination recovery.

## Extracted Claims

### Claim 1: The distinction between AI-native and AI-assisted products determines failure modes and engineering trade-offs
- **Evidence**: Foundational framing for the entire architecture discussion,
  citing João Freitas's earlier PagerDuty post on production AI agents. The
  article is structured as a case study in what this distinction means in
  practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of
  an existing system. In AI-native products, the AI is the system."
- **Our assessment**: Useful framing backed by concrete examples throughout.
  Single-source claim but the reasoning is sound — failure modes differ
  materially between the two categories, and this distinction drives real
  architecture decisions.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: Their Incident Context document grew to include JSON blobs of
  alerts, past incidents, change events, runbook content, service topology,
  dependency graphs, historical patterns, and remediation options. Authors cite
  Liu et al. (2023) "Lost in the Middle" research showing model performance
  degrades beyond certain context thresholds.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows."
- **Our assessment**: Well-established in the literature and widely observed.
  The specific contribution is showing how it manifests in SRE incident
  investigation, where context documents grow large and diverse very quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails,
  and system prompts. Authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. Agents that
  performed well at a certain feature set degraded as features accumulated.
- **Confidence**: emerging
- **Quote**: "an inverse relationship between instruction volume and output
  quality"
- **Our assessment**: Jaroslawicz et al. (2025) provides research backing.
  Significant concern for teams building long-lived agent systems — feature
  work carries a hidden tax on existing capabilities.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis,
  search for evidence, evaluate — took several minutes. A moderately complex
  incident with 3-4 candidate causes could take 10+ minutes. Direct production
  measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Plausible given LLM inference plus external API calls at
  each step. Key insight: this is not a model speed problem — it's an
  architectural problem (sequential execution of parallelizable work).

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the
  agent to finish, then restart with that context. The authors characterize this
  as the agent operating without information the human already had.
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: Most important failure mode for live incident response.
  Directly supports the guide's editorial principle of keeping humans on the
  paging path.

### Claim 6: Three execution models exist for multi-agent investigation, with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: Authors enumerate and evaluate all three: (a) Sequential —
  total time = sum of all sub-agent durations, a slow hypothesis blocks
  everything behind it; (b) Parallel wait-all — total time = slowest sub-agent,
  but the main agent is idle during execution and "the graph is locked inside
  the parallel call until everything resolves"; (c) Parallel fan-out, concurrent
  fan-in — dispatch all asynchronously, process each result as it arrives, user
  input is "a first-class event alongside sub-agent results."
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: Taxonomy is clearly reasoned with well-articulated
  trade-offs. Contribution is mapping these models to the SRE investigation
  domain with concrete requirements (real-time visibility, mid-run injection,
  cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: Authors tried LangChain Deep Agents with sub-agents as tools. In
  LangGraph's BSP model, a parallel tool call is one superstep — control
  returns only after every tool in that batch resolves. The orchestrator cannot
  react to sub-agent 1's result at t=3min while sub-agents 2 and 3 still run.
  No external event — including user input — can reach the graph while blocked
  inside a parallel tool call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: Specific technical claim about LangGraph's execution model
  that matches the documented BSP/superstep design. Significant constraint for
  anyone building interactive agent systems on LangGraph.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first
  completion resumed the graph and triggered the main agent's working loop.
  While processing, the second completion arrived and tried to resume the same
  graph. LangGraph either errored or started a fresh execution from scratch,
  losing state from the first arrival. The fix was a local queue — incoming
  results went into the queue, and the main agent drained it one result at a
  time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph execution model. The fact that the naive
  approach fails under realistic timing (two sub-agents finishing within
  seconds) is a valuable warning for anyone building similar systems.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there remained a window between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and call resume before the graph was genuinely paused — same race,
  different shape. The fix: the drain loop held a lock while resuming, and the
  graph signaled through a callback when it had actually re-interrupted,
  releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Concurrency edge case easy to miss until it hits in
  production. The lock pattern is standard but the specific interaction with
  LangGraph's interrupt/resume lifecycle is a useful concrete example.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the user's
  message would go in fourth — by the time the drain loop reached it, the graph
  might have already finished. The fix: a two-level priority queue where user
  input is priority 0 (highest) and sub-agent results are priority 1. A
  `route_event` node branches: sub-agent results go to
  `handle_sub_agent_result`, user messages go to `handle_user_input` which adds
  new work to state and re-enters `plan` for immediate dispatch.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: Clean, well-explained pattern. The priority queue is a
  simple primitive but the authors make a compelling case for why it's essential.
  The `route_event` branching design is a concrete LangGraph pattern worth
  noting.

### Claim 11: The identity convention task_id === thread_id eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID task_id. Every sub-agent carries a
  parent_task_id pointing to whoever spawned it. By making the LangGraph
  thread_id identical to the agent's task_id, when a sub-agent publishes a
  completion event carrying parent_task_id: task-001, the parent agent
  immediately knows which LangGraph thread to resume — no lookup table, no
  correlation logic. Authors call this "the single most important convention"
  in their architecture.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: Elegant convention that eliminates an entire class of
  infrastructure (lookup tables, correlation services). The kind of simple
  design decision that only becomes obvious after building the complex version.
  Worth adopting for any multi-agent system on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries, and splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: Authors initially built as if agents were distributed (separate
  processes, broker, durable store), then questioned the assumption. The usual
  justifications for service boundaries — CPU isolation and organizational
  ownership — don't apply: investigation is overwhelmingly IO (call log API and
  wait, call metrics API and wait, hand text to model and wait), and a single
  team owns the whole sub-agent system.
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: Most counterintuitive and valuable insight in the article.
  The reflex to treat a multi-agent system as a distributed system is strong,
  and the authors make a clear, specific argument for why it's wrong for this
  workload class. Key qualifier is "IO-bound" — doesn't generalize to
  compute-bound workloads.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — its state is checkpointed so it can
  pause, resume, and recover. Sub-agents are stateless — no checkpoints. If a
  sub-agent dies, they re-spawn it rather than resume mid-flight. Making every
  agent durable would mean keeping N+1 checkpoints consistent and reconciling
  them on every restart.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: Clean asymmetric durability model. Reduces the recovery
  problem from a distributed consensus problem to a single-writer checkpoint.
  Trade-off — re-running sub-agent work on failure — is acceptable when
  sub-agents are cheap (IO-bound, no side effects beyond their result).

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: Earlier distributed design required webhook callbacks, PubSub
  broadcast, and a durable event store — all to move results across a network.
  Once everything shares a process, the answer is "an in-process mailbox — an
  asyncio.Queue — injected into each background task when it's spawned." The
  sub-agent writes its result to the queue; the supervisor reads from it. No
  broker, no callback endpoint, no network hop.
- **Confidence**: emerging
- **Quote**: "an in-process mailbox — an asyncio.Queue — injected into each
  background task when it's spawned"
- **Our assessment**: Natural consequence of the single-process decision and a
  dramatic simplification. Authors are explicit that this only works because
  sub-agents are guaranteed to live in the same process as their spawning
  supervisor.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: Authors evaluated LangGraph's async sub-agents which let the
  supervisor launch background tasks and return immediately without blocking.
  But the polling model means "no push notification when a sub-agent finishes,
  which means no deterministic synthesis the moment each result arrives."
  Native support "stops short of the two things our SRE Agent actually needs:
  true mid-run steering, and gradual emission of artifacts as each hypothesis
  resolves."
- **Confidence**: emerging
- **Quote**: "no push notification when a sub-agent finishes, which means no
  deterministic synthesis the moment each result arrives"
- **Our assessment**: Important qualification — framework evolution doesn't
  automatically solve the hard problems. The gap is mid-run steering and
  progressive result emission, which frameworks don't address. Direct
  implications for anyone choosing between building custom loops and waiting for
  framework support.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: Authors explicitly frame the complex version (webhooks, PubSub,
  durable event store, the full primitive set) as "a deliberate step, not a
  mistake." It let them identify which parts were essential and which were
  accidents of assuming a distributed architecture. The simplification to a
  single process with in-process primitives was only possible because they first
  understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: Advice, not a falsifiable claim. Valuable engineering
  philosophy demonstrated convincingly in their own work, but one team's
  methodology. Risk: teams might use this to justify over-engineering that
  never gets simplified. Authors avoid this trap by actually shipping the
  simple version.

### Claim 17: Three insights — identity, event transport, and reactive loop — remain true regardless of runtime engine, forming a portable foundation for multi-agent architectures
- **Evidence**: Authors identify three primitives that survive the
  simplification from distributed to single-process and would apply to any
  runtime engine: (1) Identity (task_id === thread_id) routes events to the
  right graph without lookup tables; (2) Event transport delivers results
  reliably, handles late-joining clients, and survives restarts; (3) Reactive
  loop processes results as they arrive, serializes concurrent completions, and
  treats user input as a first-class event.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as your framework evolves."
- **Our assessment**: Useful distillation. Three primitives form a reasonable
  abstraction stack (identity → transport → control loop) that could guide
  design even outside LangGraph. Portability claim is plausible but untested —
  authors only implemented on LangGraph.

## Concrete Artifacts

### Reactive loop node structure (as described in the article)

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

Where:
- `accept_event`: The graph spends most of its life here, paused, waiting for
  the drain loop to deliver the next event from the priority queue.
- `route_event`: Inspects the event type and branches.
- `handle_sub_agent_result`: Processes a sub-agent's findings.
- `handle_user_input`: Adds new work to state, marks as pending spawn, re-enters
  `plan` so the new sub-agent gets dispatched immediately.
- `plan`: Formulates investigation strategy based on current state.
- `spawn_sub_agents`: Dispatches new sub-agent background tasks.

### Identity hierarchy (from the article)

```
Main Agent (task_id: task-001, thread_id: task-001)
    ├── Sub-Agent 1 (task_id: sub-1, parent_task_id: task-001)
    │     └→ completes → publishes event with parent_task_id: task-001
    │                  → parent agent resumes thread_id: task-001
    ├── Sub-Agent 2 (task_id: sub-2, parent_task_id: task-001)
    └── Sub-Agent 3 (task_id: sub-3, parent_task_id: task-001)
```

### Lifecycle states (A2A-protocol-inspired)

Each agent wraps its logic in a lifecycle: `working → completed | failed | canceled`

### Priority queue levels

```
Priority 0 (highest): User input — processed first, jumps the line
Priority 1:          Sub-agent results — processed in arrival order after any pending user input
```

### Single-process architecture (as described)

- Supervisor and all sub-agents share one process
- Mailbox: ordinary `asyncio.Queue` (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Multiple concurrent investigation runs can land on different pods/processes
- Within one run, all sub-agents are co-located with their spawning supervisor

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (baseline, same URL, issue #1):
    Both notes extract the same 17 claims from the same source — the reactive
    loop structure, the identity convention (task_id === thread_id), the
    single-process simplification argument, and the durable supervisor /
    stateless sub-agent asymmetry. Two independent models (DeepSeek/Flash and
    mimo-v2.5-free) arrived at the same extraction, increasing confidence in
    the claims.
  - `blog-pagerduty-production-ai-agent-gaps.md` (Freitas, issue #4): The
    precursor framing article that this note's Claim 1 explicitly cites. Claim 3
    (context fatigue) corroborates this note's Claim 2 (context rot as a hard
    ceiling for single-agent architectures) — same failure mode under a
    different name, both citing the "Lost in the Middle" phenomenon. Claim 4
    (compounding errors across multi-step agent workflows) corroborates this
    note's Claim 3 (instruction overload creating an inverse relationship
    between feature count and output quality). Claim 8 (architecture evolution
    single-agent → supervisor → hierarchical) corroborates this note's Claims 6
    (three execution models), 12 (single-process simplification), and 16 (build
    hard, ship simple). The gaps article covers evaluation, metrics, guardrails,
    and UX — areas this note explicitly says it does not cover — making the two
    notes complementary.
  - `blog-incidentio-ai-sre-incident-run.md` (issue #3): Independent production
    experience from incident.io corroborating the parallel investigation
    pattern and real-time visibility requirement. This note's Claim 5 (agent
    operating without information the human already had) is the structural
    failure mode that incident.io's bidirectional context sync and parallel
    human-agent investigation pattern addresses. This note's Claim 10 (user
    input as first-class event) parallels incident.io's design where human and
    AI investigate independently in parallel.
  - `docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md` (Zelesko, issue
    #247): Google VP of SRE corroborating at the leadership level: the
    investigation-vs-mitigation safety boundary (non-mutating investigation is
    AI-safe; mitigation requires human in the loop) aligns with this note's
    architectural emphasis on keeping human oversight for production changes.
    The shift from "human-centric" to "human-supervised" work parallels this
    note's framing of the agent as an active participant requiring mid-run
    human steering. The "build to understand" philosophy (Zelesko S6E4, Claims
    6–8: discover skills bottom-up) parallels this note's Claim 16 ("build
    hard, ship simple").
  - `docs-google-sre-prodcast-04-09-ai-agents.md` (Llamas & Haria, issue #105):
    Google SRE practitioners corroborating: the pre-on-caller triage pattern
    (agent investigates in parallel before the human arrives) maps to this
    note's concurrent fan-in execution model (Claim 6). The read-vs-write
    capability split and human-permission-before-write guardrail align with this
    note's emphasis on keeping humans in control of production-state mutations.
    The "production has no sandbox" evaluation difficulty parallels this note's
    context-rot argument — both describe structural ceilings created by
    production's inherent complexity.

- **Contradicts**: None identified. This note's architectural claims are
  consistent with all related notes in the corpus. PagerDuty, incident.io, and
  Google sources independently converge on the same principles: parallel
  investigation, human-in-the-loop for writes, and transparent agent reasoning.

- **Extends**: This note is a re-extraction of the same URL as the baseline
  `blog-pagerduty-sre-agent-architecture.md` (issue #1). It does not extend the
  baseline with new content — both notes extract the same 17 claims, the same
  concrete artifacts, and the same architectural patterns. The eval note adds
  an "Our assessment" field per claim (not present in the baseline template),
  providing independent model judgment of each claim's credibility. The two
  independent extractions corroborate each other and increase confidence in the
  extracted claims by confirming that different models arrive at the same
  substantive conclusions when given the same source.

- **Novel**: No substantively new claims relative to the baseline — both notes
  cover the same source. The value of this note is as an independent
  re-extraction that (a) confirms the baseline's 17 claims via a different
  model (mimo-v2.5-free), (b) adds "Our assessment" evaluations per claim
  providing a second opinion on credibility, and (c) provides a comparison
  point for model quality assessment (mimo-v2.5-free vs DeepSeek/Flash) as
  part of the miner-eval pipeline. The cross-references to three additional
  related notes (`blog-pagerduty-production-ai-agent-gaps.md`,
  `blog-incidentio-ai-sre-incident-run.md`, and the Google Prodcast notes on AI
  agents and agentic SRE) are new in this extraction and contextualize the
  claims within the broader corpus.

## Guide Impact

- **Chapter 00 (Principles)**: Source provides evidence for a new principle:
  "Design for AI-native failure modes" — context rot and instruction overload are
  structural, not incidental, and distinguishing AI-native from AI-assisted
  products changes reliability requirements. Also supports "build to understand,
  ship simple" as an engineering principle for agent systems.

- **Chapter 01 (Incident Response)**: Source provides a concrete architecture
  for AI-assisted incident investigation. Key claims to incorporate: (a)
  real-time visibility into agent reasoning is a hard requirement for live
  incidents, not a nice-to-have; (b) mid-run human steering (injecting
  hypotheses, redirecting investigation) must be a first-class event, not an
  afterthought; (c) sequential hypothesis testing creates unacceptable latency
  for incidents with multiple candidate causes; (d) the agent should never
  operate without information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Source provides patterns for multi-agent
  ops architecture: (a) the three execution models and when to use each; (b)
  the reactive loop pattern (interrupt/resume, priority queue, lock
  serialization) for interactive agent systems; (c) the task_id === thread_id
  identity convention for routing events; (d) the durable supervisor /
  stateless sub-agent asymmetry for reliability without distributed complexity;
  (e) the single-process simplification argument — IO-bound agent workloads
  don't need service boundaries.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate
  hypotheses → spawn sub-agents → query logs/metrics → report findings →
  synthesize root cause) is a directly reusable pattern for on-call tooling.
  The priority queue pattern (user input > sub-agent results) applies to any
  interactive on-call agent.

## Extraction Notes

- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. No sub-pages were followed — the article is self-contained
  with all architectural detail inline.
- Quotes were extracted via WebFetch and verified against the rendered page. All
  quotes marked as direct are verbatim from the source.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol). These were not independently fetched — they are cited
  here as they appear in the source.
- The source is rich in architectural detail but light on quantitative metrics
  (no latency distributions, no accuracy/eval numbers, no cost data). The one
  concrete number cited is "10+ minutes" for sequential diagnosis of a moderately
  complex incident.
- No part of the source was paywalled. The article is publicly accessible on
  the PagerDuty Engineering Blog.
- Published June 24, 2026 — approximately 5 weeks before extraction. The
  architecture described is very recent and may still be evolving.
- This is an eval candidate note (zen-free / mimo-v2.5-free via OpenCode
  Action). Compare against the merged DeepSeek/Flash baseline note
  `blog-pagerduty-sre-agent-architecture.md` for quality assessment.
