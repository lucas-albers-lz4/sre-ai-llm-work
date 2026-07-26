---
source_url: https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
source_type: blog-post
title: "Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation"
author: "Viktor Vasylkovskyi, Micah Mayo, Ralph Bird (PagerDuty Engineering)"
date_published: 2026-06-24
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: emerging
issue: "#1-deepseek-v4-flash-free-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> A detailed practitioner writeup from PagerDuty Engineering describing the
> architectural evolution of their SRE Agent from a single-agent monolith to a
> reactive multi-agent system. Covers specific failure modes (context rot,
> instruction overload), three execution models with trade-offs, a custom
> reactive loop built on LangGraph interrupt/resume primitives, and the
> counterintuitive simplification from distributed to single-process architecture.
> Published June 2026 — very recent, with concrete production patterns.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three senior/staff/principal engineers at PagerDuty —
  Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from
  concept to GA), Ralph Bird (Principal ML Engineer, focused on AI agents and LLM
  observability). The authors built the system they describe; this is first-hand
  production experience, not a thought-piece.
- **Scope**: Covers the full architectural journey — why a single agent failed,
  the three execution models evaluated, the custom reactive loop built from first
  principles, and the simplification that collapsed distributed machinery into a
  single process. Also covers identity conventions, event transport, and the
  "build hard, ship simple" methodology. Does NOT cover: evaluation/accuracy
  metrics, cost data, specific model choices, or failure recovery from model
  hallucinations.

## Extracted Claims

### Claim 1: The distinction between AI-native and AI-assisted products determines failure modes and engineering trade-offs
- **Evidence**: Authoritative — the authors draw this as the foundational framing
  for the entire architecture discussion, citing João Freitas's earlier PagerDuty
  post on production AI agents. The entire article is structured as a case study
  in what this distinction means in practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an
  existing system. In AI-native products, the AI is the system."
- **Our assessment**: This is a useful framing that the authors back with concrete
  examples throughout the article. It's a single-source claim but the reasoning
  is sound and the distinction has practical consequences for architecture
  decisions.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document in their single-agent system grew
  to include JSON blobs of alerts, past incidents, change events, runbook
  content, service topology, dependency graphs, historical patterns, and
  remediation options. The authors cite Liu et al. (2023) "Lost in the Middle"
  research showing that model performance degrades beyond certain context
  thresholds.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows."
- **Our assessment**: Well-established in the literature and widely observed in
  practice. The authors' specific contribution is showing how it manifests in
  the SRE incident investigation domain, where context documents grow large
  and diverse very quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. Agents that
  performed well at a certain feature set degraded as features accumulated.
- **Confidence**: emerging
- **Quote**: "an inverse relationship between instruction volume and output quality"
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research
  backing. The authors' observation that feature work carries a hidden tax on
  existing capabilities is a significant concern for teams building long-lived
  agent systems.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search
  for evidence, evaluate — took several minutes. A moderately complex incident
  with 3-4 candidate causes could take 10+ minutes to diagnose.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible given that each step involves LLM inference plus
  external API calls. The key insight is that this is an architectural problem
  (sequential execution of parallelizable work), not a model speed problem.

### Claim 5: Lack of interactivity during agent execution was a structural failure of the single-agent model, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the
  agent to finish, then restart with that context. The agent was "operating
  without information the human already had."
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most important failure mode they identify for
  live incident response. An agent that cannot accept mid-run input wastes time
  and ignores the human's existing knowledge. Directly supports the guide's
  principle of keeping humans on the paging path.

### Claim 6: Three execution models exist for multi-agent investigation — only concurrent fan-in meets real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - Sequential: total time is sum of sub-agent durations, slow hypothesis blocks
    everything behind it
  - Parallel wait-for-all: total time is slowest sub-agent, but main agent idle,
    no progress reporting, graph locked until everything resolves
  - Parallel fan-out with concurrent fan-in: dispatch all asynchronously, process
    each result as it arrives, user input as first-class event
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: The taxonomy is clearly reasoned and each model's
  trade-offs are well articulated. The authors' contribution is mapping these
  models to SRE investigation requirements with concrete constraints.

### Claim 7: LangGraph's Bulk Synchronous Parallel execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: In LangGraph's BSP model, a parallel tool call is one superstep —
  control returns only after every tool in that batch resolves. The orchestrator
  cannot react to sub-agent 1's result while sub-agents 2 and 3 still run. No
  external event can reach the graph while blocked inside a parallel tool call.
  The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: Matches LangGraph's documented BSP/superstep design. The
  implication — that framework-managed parallelism is incompatible with
  real-time interactivity — is a significant constraint. Note: LangGraph has
  since added async sub-agent support, but authors argue it still doesn't fully
  address requirements.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first resumed the
  graph and triggered the main agent's working loop. While processing, the second
  arrived and tried to resume the same graph — LangGraph either errored or started
  fresh execution, losing state. Fix: local queue, drained one result at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph model. The queue is the obvious fix, but
  the fact that naive approaches fail when sub-agents finish within seconds is
  a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary — a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, a window existed between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and resume before the graph was genuinely paused. Fix: lock held
  while resuming, graph signals via callback when re-interrupted, releasing lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A subtle concurrency edge case easy to miss until
  production. The specific interaction with LangGraph's interrupt/resume
  lifecycle is a useful concrete example.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a FIFO queue, buffered sub-agent results could delay user
  input until the graph finished. Fix: two-level priority queue (user = priority
  0, sub-agent results = priority 1). `route_event` node branches: sub-agent
  results to `handle_sub_agent_result`, user messages to `handle_user_input`
  which adds work and re-enters `plan` for immediate dispatch.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: Clean, well-explained pattern. The priority queue is simple
  but essential — without it, user input can arrive too late to matter.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables for routing events to the correct graph
- **Evidence**: Every agent gets a UUID `task_id`. Every sub-agent carries
  `parent_task_id`. By making the LangGraph `thread_id` identical to `task_id`,
  a sub-agent completion event carrying `parent_task_id` directly identifies the
  graph thread to resume. The authors call this "the single most important
  convention" in their architecture.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: An elegant convention that eliminates an entire class of
  infrastructure (lookup tables, correlation services). Worth adopting as a
  pattern for any LangGraph multi-agent system.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — splitting them across services buys complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed, then
  questioned the assumption. Justifications for service boundaries (CPU
  isolation, organizational ownership) don't apply: investigation is
  overwhelmingly IO-bound (call log API and wait, call metrics API and wait,
  hand text to model and wait), and a single team owns the sub-agent system.
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive and valuable insight.
  The reflex to treat multi-agent systems as distributed systems is strong, and
  the authors make a clear, specific argument for why it is wrong for this
  workload class.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: Supervisor is checkpointed for pause/resume/recovery. Sub-agents
  have no checkpoints — if one dies, they re-spawn rather than resume mid-flight.
  Making every agent durable would mean keeping N+1 checkpoints consistent.
  Each processing step is atomic and persisted before touching the next event.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: A clean design principle reducing recovery from distributed
  consensus to single-writer checkpoint. The trade-off (re-running sub-agent work
  on failure) is acceptable when sub-agents are cheap and IO-bound.

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The distributed design required webhooks, PubSub, and durable
  event store. In a single process, the answer is "an in-process mailbox — an
  asyncio.Queue — injected into each background task." Sub-agent writes to the
  queue; supervisor reads from it. No broker, no callback endpoint, no network
  hop.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Natural consequence of the single-process decision and a
  dramatic simplification. Only works because sub-agents are co-located with
  their spawning supervisor within one investigation run.

### Claim 15: Framework-native async sub-agent support leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: LangGraph's async sub-agents let the supervisor launch background
  tasks without blocking, but the polling model provides "no push notification
  when a sub-agent finishes, which means no deterministic synthesis the moment
  each result arrives." Native support stops short of true mid-run steering and
  gradual artifact emission — these still require custom identity, transport,
  and reactive loop primitives.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Important qualification — framework evolution does not
  automatically solve the hard problems. Polling vs. push is the smaller gap;
  mid-run steering and progressive result emission are the larger gaps that
  frameworks do not address.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors frame the complex version (webhooks, PubSub, durable
  event store) as "a deliberate step, not a mistake." It let them identify which
  parts were essential and which were accidents of a distributed assumption. The
  simplification to a single process was only possible because they first
  understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: Valuable engineering philosophy, demonstrated convincingly
  in their own work. Risk: teams might use this to justify over-engineering that
  never gets simplified. The authors avoid this by actually shipping the simple
  version.

### Claim 17: Three portable primitives — identity, event transport, and reactive loop — remain true regardless of runtime engine
- **Evidence**: The authors identify three primitives surviving the distributed
  to single-process simplification: (1) Identity (`task_id === thread_id`)
  routes events without lookup tables; (2) Event transport delivers results
  reliably for late-joining clients and restarts; (3) Reactive loop processes
  results as they arrive, serializes concurrent completions, and treats user
  input as a first-class event.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as frameworks evolve."
- **Our assessment**: Useful distillation forming a reasonable abstraction stack
  (identity → transport → control loop). Portability claim is plausible but
  untested outside LangGraph.

## Concrete Artifacts

### Reactive loop node structure

The reactive loop consists of six nodes in the supervisor's LangGraph:

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

Where:
- `accept_event`: Graph spends most of its life here, paused, waiting for the
  drain loop to deliver the next event from the priority queue.
- `route_event`: Inspects event type and branches.
- `handle_sub_agent_result`: Processes a sub-agent's findings.
- `handle_user_input`: Adds new work to state, marks as pending spawn, re-enters
  `plan` for immediate dispatch.
- `plan`: Formulates investigation strategy based on current state.
- `spawn_sub_agents`: Dispatches new sub-agent background tasks.

### Identity hierarchy

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
Priority 1:          Sub-agent results — processed in arrival order after pending user input
```

### Single-process architecture

- Supervisor and all sub-agents share one process
- Mailbox: ordinary `asyncio.Queue` (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Multiple concurrent investigation runs can land on different pods/processes
- Within one run, all sub-agents are co-located with their spawning supervisor

## Cross-References

- **Corroborates**: The companion PagerDuty article on production AI agent gaps
  ([blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md))
  corroborates the single-agent failure modes (context fatigue / context rot)
  and the architecture evolution pattern (single → supervisor → hierarchical).
- **Contradicts**: None identified.
- **Extends**: Nothing yet — this remains one of the earliest practitioner
  source notes.
- **Novel**: Everything in this source is new to the corpus as the first
  production SRE agent architecture deep-dive. Baseline note:
  [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
  (merged via PR #5) covers the same material. This eval note should be compared
  against that baseline for extraction quality, claim depth, and quote fidelity.

## Guide Impact

- **Chapter 00 (Principles)**: Supports a principle for "Design for AI-native
  failure modes" — context rot and instruction overload are structural, not
  incidental. Also supports "build to understand, ship simple" as an engineering
  principle.

- **Chapter 01 (Incident Response)**: Concrete architecture for AI-assisted
  incident investigation: real-time visibility into agent reasoning is a hard
  requirement; mid-run human steering must be a first-class event; sequential
  hypothesis testing creates unacceptable latency for multi-cause incidents.

- **Chapter 03 (Runbooks and Agents)**: Patterns for multi-agent ops architecture:
  three execution models and when to use each; reactive loop pattern
  (interrupt/resume, priority queue, lock serialization); `task_id === thread_id`
  identity convention; durable supervisor / stateless sub-agent asymmetry;
  single-process simplification argument for IO-bound agent workloads.

- **Chapter 04 (Oncall and Toil)**: Investigation workflow (formulate hypotheses
  → spawn sub-agents → query logs/metrics → report findings → synthesize root
  cause) is a directly reusable pattern. Priority queue pattern (user input >
  sub-agent results) applies to any interactive on-call agent.

## Extraction Notes

- This is an eval note for the deepseek-v4-flash-free model via OpenCode Zen
  free chat-completions. Compare against the baseline extraction in
  `blog-pagerduty-sre-agent-architecture.md` (merged via PR #5).
- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. No sub-pages were followed.
- Quotes were verified against the source page. Short quotes (≤125 chars) are
  verbatim. Longer passages without direct quotes are paraphrased in Our
  assessment as specified by the extraction rules.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol) — not independently fetched.
- Light on quantitative metrics (only "10+ minutes" cited for sequential
  diagnosis latency). No cost data, accuracy numbers, or latency distributions.
- No part of the source was paywalled. Published June 24, 2026.
