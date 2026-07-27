---
source_url: https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
source_type: blog-post
title: "Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation"
author: "Viktor Vasylkovskyi, Micah Mayo, Ralph Bird (PagerDuty Engineering)"
date_published: 2026-06-24
date_extracted: 2026-07-27
last_checked: 2026-07-27
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
  examples throughout the article. The distinction has practical consequences for
  architecture decisions. The claim that failure modes differ materially between
  the two categories is demonstrated, not just asserted.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document in their single-agent system grew
  to include JSON blobs of alerts, past incidents, change events, runbook
  content, service topology, dependency graphs, historical patterns, and
  remediation options. The authors cite Liu et al. (2023) "Lost in the Middle"
  research showing that model performance degrades beyond certain context
  thresholds.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows, not because the information isn't there but because the model
  struggles to weight it correctly."
- **Our assessment**: This is well-established in the literature (Liu et al.
  2023) and widely observed in practice. The authors' specific contribution is
  showing how it manifests in the SRE incident investigation domain, where
  context documents grow large and diverse very quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. Agents that
  performed well at a certain feature set degraded as features accumulated.
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between
  instruction volume and output quality"
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research
  backing, but the specific observation about agent degradation as features
  accumulate is the authors' production experience. This is a significant
  concern for teams building long-lived agent systems.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search
  for evidence, evaluate — took several minutes. A moderately complex incident
  with 3-4 candidate causes could take 10+ minutes to diagnose.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible. The key insight is that this is not a model speed
  problem — it's an architectural problem (sequential execution of parallelizable
  work).

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the agent
  to finish, then restart with that context.
- **Confidence**: emerging
- **Quote**: "they had to wait for the agent to finish, then restart with the new
  context included"
- **Our assessment**: This is the most important failure mode they identify for
  live incident response. An agent that can't accept mid-run input from the
  on-call engineer wastes time and ignores the human's existing knowledge.

### Claim 6: Three execution models exist for multi-agent investigation, with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three: sequential (additive
  latency), parallel-wait-for-all (blocking main agent), and parallel fan-out
  with concurrent fan-in (async, reactive, user input as first-class event).
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: This taxonomy is clearly reasoned and each model's
  trade-offs are well articulated. The contribution is mapping these models to
  the SRE investigation domain with concrete requirements.

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: The authors tried LangChain Deep Agents with sub-agents as
  tools. In LangGraph's BSP model, a parallel tool call is one superstep —
  control returns only after every tool in that batch resolves. The orchestrator
  cannot react to sub-agent 1's result while sub-agents 2 and 3 still run.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: This is a specific technical claim about LangGraph's
  execution model. The implication — that framework-managed parallelism is
  incompatible with real-time interactivity — is a significant constraint for
  anyone building interactive agent systems on LangGraph.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first completion
  resumed the graph and triggered the main agent's working loop. The second
  completion arrived and tried to resume the same graph. LangGraph either errored
  or started a fresh execution from scratch, losing state from the first arrival.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The race is real given LangGraph's single-thread-per-graph
  execution model. The queue is the obvious fix, but the fact that the naive
  approach fails under realistic timing is a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there remained a window between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and call resume before the graph was genuinely paused.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the kind of concurrency edge case that's easy to
  miss until it hits in production. The lock pattern is standard but the
  specific interaction with LangGraph's interrupt/resume lifecycle is useful.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the user's
  message would go in fourth. The fix: a two-level priority queue where user
  input is priority 0 and sub-agent results are priority 1.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean pattern. The priority queue is a simple primitive
  but the authors make a compelling case for why it's essential — without it,
  user input can arrive too late to matter.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries a
  `parent_task_id`. By making the LangGraph `thread_id` identical to the agent's
  `task_id`, when a sub-agent publishes a completion event carrying
  `parent_task_id`, the parent agent immediately knows which LangGraph thread
  to resume.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: This is an elegant convention that eliminates an entire
  class of infrastructure. It's the kind of simple design decision that only
  becomes obvious after building the complex version.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries, and splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed, then
  questioned the assumption. Investigation is overwhelmingly IO (call log API
  and wait, call metrics API and wait, hand text to model and wait), and a
  single team owns the whole sub-agent system.
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: This is the article's most counterintuitive and valuable
  insight. The reflex to treat a multi-agent system as a distributed system is
  strong, and the authors make a clear argument for why it's wrong for this
  workload class.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — state checkpointed for pause, resume,
  and recovery. Sub-agents are stateless — no checkpoints, re-spawned on failure.
  Each processing step is atomic and persisted before the next event is touched.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: This asymmetric durability model reduces the recovery
  problem from distributed consensus to single-writer checkpoint. The trade-off
  — re-running sub-agent work on failure — is acceptable when sub-agents are
  cheap IO-bound tasks.

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The earlier distributed design required webhook callbacks, PubSub
  broadcast, and a durable event store. Once everything shares a process, the
  answer is an in-process mailbox — an asyncio.Queue injected into each
  background task.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the natural consequence of the single-process
  decision and a dramatic simplification. Only works because sub-agents are
  guaranteed to live in the same process as their spawning supervisor.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents. The polling
  model means no push notification when a sub-agent finishes. More importantly,
  native support stops short of true mid-run steering and gradual emission of
  artifacts as each hypothesis resolves.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Framework evolution doesn't automatically solve the hard
  problems. The bigger gap is mid-run steering and progressive result emission,
  which frameworks don't address.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors explicitly frame the complex version as a deliberate
  step. It let them identify which parts were essential and which were accidents
  of assuming a distributed architecture.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: This is advice, not a falsifiable claim. It's a valuable
  engineering philosophy and the authors demonstrate it convincingly, but it's
  one team's methodology.

### Claim 17: Three insights — identity, event transport, and reactive loop — remain true regardless of runtime engine, forming a portable foundation for multi-agent architectures
- **Evidence**: The authors identify three primitives that survive the
  simplification: (1) Identity routes events without lookup tables; (2) Event
  transport delivers results reliably; (3) Reactive loop processes results as
  they arrive and treats user input as first-class.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as frameworks evolve."
- **Our assessment**: The three primitives form a reasonable abstraction stack
  that could guide design even outside LangGraph. The portability claim is
  plausible but untested.

## Concrete Artifacts

### Reactive loop node structure (as described in the article)

The reactive loop consists of six nodes in the supervisor's LangGraph:

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

Where:
- `accept_event`: Graph spends most of its life here, paused, waiting for the
  drain loop to deliver the next event from the priority queue.
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
  - `blog-pagerduty-production-ai-agent-gaps.md` (Claim 3, context fatigue):
    Both articles identify the same context-window degradation problem in
    long-running agent tasks. The present article calls it "context rot" and
    cites Liu et al. (2023); the companion article calls it "context fatigue."
    Same failure mode, same root cause.
  - `blog-pagerduty-production-ai-agent-gaps.md` (Claim 8, architecture
    evolution): Both articles describe the single-agent → supervisor →
    hierarchical evolution path. The "earn complexity" principle is consistent
    across both PagerDuty sources.
  - `blog-incidentio-ai-sre-incident-run.md` (Claim 3, parallel human-agent
    investigation): The incident.io article demonstrates a UX response to the
    same problem PagerDuty identifies — agents operating without human input.
    Both sources treat human input as a first-class event.

- **Contradicts**: None identified.

- **Extends**:
  - `blog-pagerduty-production-ai-agent-gaps.md`: The companion article
    provides the evaluation, metrics, and guardrail framework. The present
    article provides the implementation primitives (reactive loop, identity,
    transport, durability model). Together they form a complete picture:
    one covers what to measure, the other covers how to build.

- **Novel**: The following are specific novel contributions new to the corpus
  (already captured in the baseline note at
  `blog-pagerduty-sre-agent-architecture.md`):
  - The three execution models mapped to SRE investigation requirements
  - The LangGraph BSP limitation for interactive agent systems
  - The queue+lock pattern for serializing concurrent graph resumes
  - The priority queue pattern for user input preemption
  - The `task_id === thread_id` identity convention
  - The single-process simplification argument for IO-bound workloads
  - The durable supervisor / stateless sub-agent asymmetry
  - The "build hard, ship simple" methodology

## Guide Impact

- **Chapter 00 (Principles)**: Supports a new principle: "Design for AI-native
  failure modes" — context rot and instruction overload are structural, not
  incidental, and distinguishing AI-native from AI-assisted changes reliability
  requirements.

- **Chapter 01 (Incident Response)**: Provides concrete architecture for
  AI-assisted incident investigation. Key claims: (a) real-time visibility into
  agent reasoning is a hard requirement for live incidents; (b) mid-run human
  steering must be a first-class event; (c) sequential hypothesis testing
  creates unacceptable latency; (d) the agent should never operate without
  information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Provides patterns for multi-agent ops
  architecture: (a) the three execution models and when to use each; (b) the
  reactive loop pattern; (c) the `task_id === thread_id` identity convention;
  (d) the durable supervisor / stateless sub-agent asymmetry; (e) the
  single-process simplification argument.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate
  hypotheses → spawn sub-agents → query logs/metrics → report findings →
  synthesize root cause) is a directly reusable pattern for on-call tooling.

## Extraction Notes

- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. No sub-pages were followed — the article is self-contained
  with all architectural detail inline.
- Quotes were extracted via WebFetch and spot-checked against the rendered page.
  All quotes marked as direct were returned as verbatim by the extraction tool.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol). These were not independently fetched.
- The source is rich in architectural detail but light on quantitative metrics
  (no latency distributions, no accuracy/eval numbers, no cost data).
- Published June 24, 2026 — approximately one month before extraction.
- This is an eval note comparing against the baseline
  `blog-pagerduty-sre-agent-architecture.md` (merged via PR #5). The same source
  URL was extracted independently by the `opencode/deepseek-v4-flash-free` model
  to evaluate candidate quality.
- The `miner-related-notes.md` candidates file listed 10 candidates. All 10 were
  reviewed: candidate 1 (`blog-pagerduty-sre-agent-architecture.md`) is the
  baseline note for this same URL and is cited throughout Cross-References.
  Candidates 2-10 are not directly related to the PagerDuty SRE agent
  architecture (they cover SLOs, retail/gaming SRE, AI for SRE at Google,
  incident response tooling, complexity, databases, ML training SRE, incident.io
  AI SRE, and client-transparent migrations). The incident.io candidate
  (#9, `blog-incidentio-ai-sre-incident-run.md`) is cited as a corroborating
  source for the parallel human-agent investigation pattern.
