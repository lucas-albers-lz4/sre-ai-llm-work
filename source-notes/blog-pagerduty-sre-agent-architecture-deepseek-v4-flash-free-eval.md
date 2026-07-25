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
issue: "#1-deepseek-v4-flash-free-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> A detailed practitioner writeup from PagerDuty Engineering tracing the architectural evolution of their SRE Agent from a single-agent monolith to a reactive multi-agent system with concurrent fan-in. Covers structural failure modes of single-agent design (context rot, instruction overload, sequential blocking), three execution models with trade-offs, a custom reactive loop built on LangGraph interrupt/resume primitives with a priority queue and lock serialization, and the counterintuitive simplification from distributed multi-service architecture to single-process in-process primitives.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three senior/staff/principal engineers at PagerDuty who built the system they describe — first-hand production experience, not a thought-piece. Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from concept to GA), Ralph Bird (Principal ML Engineer, AI agents and LLM observability).
- **Scope**: Covers the full architectural journey — why a single agent failed, three execution models evaluated, custom reactive loop built from first principles, identity conventions, event transport, the simplification from distributed to single-process, and the "build hard, ship simple" methodology. Does NOT cover: evaluation/accuracy metrics, cost data, model choices, or hallucination recovery.

## Extracted Claims

### Claim 1: AI-native products have fundamentally different failure modes and engineering trade-offs from AI-assisted products
- **Evidence**: The authors frame the entire article around this distinction, citing João Freitas's earlier PagerDuty post. The article is a case study in what this distinction means in practice for architecture decisions.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an existing system. In AI-native products, the AI is the system."
- **Our assessment**: This framing has practical consequences the authors demonstrate throughout. The distinction changes reliability requirements and which failure modes matter.

### Claim 2: Context rot creates a hard ceiling on single-agent performance — beyond a threshold, more context degrades model decisions
- **Evidence**: The Incident Context document grew to include JSON blobs of alerts, past incidents, change events, runbook content, service topology, dependency graphs, historical patterns, and remediation options. The authors cite Liu et al. (2023) "Lost in the Middle" research.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the context grows."
- **Our assessment**: This is well-established in the literature and widely observed. The authors' contribution is showing how it concretely manifests in SRE incident investigation where context grows large and diverse quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and system prompts. The authors cite Jaroslawicz et al. (2025) finding this inverse relationship. Agents that performed well at a certain feature set degraded as features accumulated — new capabilities competed with existing ones for model attention.
- **Confidence**: emerging
- **Quote**: "an inverse relationship between instruction volume and output quality"
- **Our assessment**: The research citation provides backing, and the production observation is significant. Feature work on monolithic agents carries a hidden tax on existing capabilities.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency — 10+ minutes for moderately complex incidents
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search for evidence, evaluate — took several minutes. A moderately complex incident with 3-4 candidate causes could take 10+ minutes.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes could take 10+ minutes to diagnose."
- **Our assessment**: Credible direct measurement. The key insight is this is an architectural problem (sequential execution of parallelizable work), not a model speed problem.

### Claim 5: Lack of interactivity during agent execution was a structural failure of the single-agent model, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the on-call engineer knew about a recent deployment, they had to wait for the agent to finish then restart. The authors characterize this as the agent operating without information the human already had.
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most important failure mode for live incident response. An agent that can't accept mid-run input from the on-call engineer wastes time and ignores the human's existing knowledge.

### Claim 6: There are three execution models for multi-agent investigation, and only concurrent fan-in meets real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - **Sequential**: Total time = sum of all sub-agent durations. "A slow hypothesis in the middle blocks everything behind it."
  - **Parallel, wait for all**: Total time = slowest sub-agent. But the main agent is idle, can't report progress, and "the graph is locked inside the parallel call until everything resolves."
  - **Parallel fan-out, concurrent fan-in**: Dispatch all asynchronously, process each result as it arrives. User input is a first-class event alongside sub-agent results.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New work can be injected at any point."
- **Our assessment**: This taxonomy is clearly reasoned and each model's trade-offs are well articulated. The contribution is mapping these models to SRE investigation with concrete requirements.

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: In LangGraph's BSP model, a parallel tool call is one superstep — control returns only after every tool in that batch resolves. The orchestrator cannot react to sub-agent 1's result while sub-agents 2 and 3 are still running. No external event — including user input — can reach the graph while blocked inside a parallel tool call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk Synchronous Parallel (BSP) model"
- **Our assessment**: This matches LangGraph's documented BSP/superstep design. The implication — that framework-managed parallelism is incompatible with real-time interactivity — is a significant constraint.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph — the first completion resumes the graph, and the second either errors or starts a fresh execution, losing state
- **Evidence**: When two sub-agents finished close together, the first resumed the graph. While the main agent was processing, the second arrival tried to resume the same graph. LangGraph "either errored or started a fresh execution from scratch," losing state from the first arrival. The fix was a local queue to buffer incoming results.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is a practical sharp-edge discovery. The race is real given LangGraph's single-thread-per-graph execution model. The queue is the obvious fix, but the fact that the naive approach fails under realistic timing is a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there remained a window between "main agent completed" and "graph re-interrupts" where the drain loop could call `Command(resume=...)` before the graph was genuinely paused. The fix: the drain loop held a lock while resuming, and the graph signaled through a callback when it had re-interrupted, releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the kind of concurrency edge case easy to miss until production. The lock pattern is standard but the specific interaction with LangGraph's interrupt/resume lifecycle is a useful concrete example.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results via a two-level priority queue to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were buffered and the user typed "also check the deployment logs," the user's message would go in fourth. By the time the drain loop reached it, the graph might have already finished. The fix: a two-level priority queue where user input is priority 0 (highest) and sub-agent results are priority 1. A `route_event` node branches: sub-agent results go to `handle_sub_agent_result`, user messages go to `handle_user_input`.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent results were priority 1."
- **Our assessment**: A clean, well-explained pattern. The priority queue is simple but essential — without it, user input can arrive too late to matter.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries a `parent_task_id`. By making the LangGraph `thread_id` identical to `task_id`, when a sub-agent's completion event carries `parent_task_id: task-001`, the parent agent immediately knows which LangGraph thread to resume. No lookup table, no correlation logic.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that needed to wake up"
- **Our assessment**: An elegant convention that eliminates an entire class of infrastructure. Worth adopting as a pattern for any multi-agent system built on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed (separate processes, broker, durable store), then questioned the assumption. The usual justifications for service boundaries — CPU isolation and organizational ownership — don't apply: investigation is overwhelmingly IO (call log API and wait, call metrics API and wait, hand text to model and wait), and a single team owns the whole sub-agent system.
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational complexity — deployment, service discovery, network failure modes, distributed tracing — without buying the thing services are for."
- **Our assessment**: This is the article's most counterintuitive and valuable insight. The reflex to treat multi-agent systems as distributed is strong. The key qualifier is "IO-bound" — this doesn't generalize to compute-bound workloads, but for common SRE investigation it's a powerful simplification.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable (checkpointed). Sub-agents are stateless (no checkpoints). If a sub-agent dies, they re-spawn it rather than resume mid-flight. Making every agent durable would mean keeping N+1 checkpoints consistent and reconciling on every restart.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: This asymmetric durability model reduces recovery from a distributed consensus problem to a single-writer checkpoint. The trade-off — re-running sub-agent work on failure — is acceptable when sub-agents are cheap (IO-bound, no side effects beyond their result).

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The distributed design required webhook callbacks, PubSub broadcast, and a durable event store. Once everything shares a process, the answer is "an asyncio.Queue — injected into each background task when it's spawned." Sub-agent writes its result to the queue; supervisor reads from it. No broker, no callback endpoint, no network hop.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The natural consequence of the single-process decision and a dramatic simplification. This only works because sub-agents are guaranteed to be co-located with their spawning supervisor within a single run.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after their initial experiments). The polling model means "no push notification when a sub-agent finishes, which means no deterministic synthesis the moment each result arrives." More importantly, native support "stops short of the two things our SRE Agent actually needs: true mid-run steering, and gradual emission of artifacts as each hypothesis resolves."
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: An important qualification. The authors' argument is that polling vs. push is the smaller gap; the bigger gap is mid-run steering and progressive result emission, which frameworks don't address.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors explicitly frame the complex version (webhooks, PubSub, durable event store) as "a deliberate step, not a mistake." It let them identify which parts were essential and which were accidents of assuming a distributed architecture. The simplification to single-process was only possible because they first understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple one."
- **Our assessment**: This is advice, not a falsifiable claim, but the authors demonstrate it convincingly. The risk is teams might use this to justify over-engineering that never gets simplified.

### Claim 17: Three primitives — identity, event transport, and reactive loop — form a portable foundation for multi-agent architectures regardless of runtime engine
- **Evidence**: The three primitives that survive the simplification: (1) Identity (`task_id === thread_id`) routes events without lookup tables; (2) Event transport delivers results reliably and handles late-joining clients; (3) Reactive loop processes results as they arrive, serializes concurrent completions, and treats user input as a first-class event.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or replace individual pieces as frameworks evolve."
- **Our assessment**: A useful distillation forming a reasonable abstraction stack (identity → transport → control loop) that could guide design even outside LangGraph.

## Concrete Artifacts

### Reactive loop node structure (six nodes in supervisor's LangGraph)

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

- `accept_event`: Graph spends most of its life here, paused, waiting for drain loop to deliver next event from priority queue.
- `route_event`: Inspects event type and branches.
- `handle_sub_agent_result`: Processes a sub-agent's findings.
- `handle_user_input`: Adds new work to state, marks as pending_spawn, re-enters plan.
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
Priority 1:          Sub-agent results — processed in arrival order after any pending user input
```

### Single-process architecture properties

- Supervisor and all sub-agents share one process
- Mailbox: ordinary `asyncio.Queue` (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Multiple concurrent investigation runs can land on different pods/processes
- Within one run, all sub-agents are co-located with their spawning supervisor

## Cross-References

- **Corroborates**: The companion PagerDuty framing article ([blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)) corroborates the AI-native vs. AI-assisted distinction (Claim 1 of this note, Claim 1 of that note), and corroborates that context fatigue is a hard ceiling (Claim 2 of this note, Claim 3 of that note) and that architecture should evolve from single-agent to supervisor-based (Claim 6 of this note, Claim 8 of that note).
- **Contradicts**: None identified.
- **Extends**: The companion PagerDuty production AI agents article ([blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)) establishes the five-pillar framework and evaluation pipeline; this note extends it with concrete implementation primitives (reactive loop, identity, transport, durability model).
- **Novel**: Everything in this source is largely new to the corpus. Specific novel contributions:
  - The three execution models mapped to SRE investigation requirements
  - The LangGraph BSP limitation for interactive agent systems
  - The queue+lock pattern for serializing concurrent graph resumes
  - The priority queue pattern for user input preemption in agent loops
  - The `task_id === thread_id` identity convention
  - The single-process simplification argument for IO-bound agent workloads
  - The durable supervisor / stateless sub-agent asymmetry
  - The "build hard, ship simple" methodology demonstrated end-to-end

## Guide Impact

- **Chapter 00 (Principles)**: Supports a new principle: "Design for AI-native failure modes" — context rot and instruction overload are structural, not incidental. Also supports "build to understand, ship simple" as an engineering principle.

- **Chapter 01 (Incident Response)**: Provides concrete architecture for AI-assisted incident investigation. Key claims: (a) real-time visibility into agent reasoning is a hard requirement for live incidents; (b) mid-run human steering must be a first-class event; (c) sequential hypothesis testing creates unacceptable latency; (d) the agent should never operate without information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Provides patterns for multi-agent ops architecture: (a) three execution models and when to use each; (b) the reactive loop pattern (interrupt/resume, priority queue, lock serialization); (c) the `task_id === thread_id` identity convention; (d) durable supervisor / stateless sub-agent asymmetry; (e) single-process simplification argument for IO-bound workloads.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate hypotheses → spawn sub-agents → query logs/metrics → report findings → synthesize root cause) is a directly reusable pattern. The priority queue pattern (user input > sub-agent results) applies to any interactive on-call agent.

## Extraction Notes

- The source is a single long-form blog post (~28 minute read) on PagerDuty's engineering blog. All architectural detail is self-contained inline.
- This is an eval note produced by the Miner using `opencode/deepseek-v4-flash-free` (OpenCode Action, OpenCode Zen free chat-completions backend) for comparison against the baseline note extracted via DeepSeek/Flash.
- The baseline note for this source is at `blog-pagerduty-sre-agent-architecture.md` (merged via PR #5).
- Quotes were extracted from the rendered WebFetch output. All direct quotes are short (≤125 chars) and are verbatim from the source as returned by the extraction tool. The Assayer should verify key quotes against the live URL.
- No part of the source was paywalled. The article is publicly accessible.
- Published June 24, 2026 — approximately 4 weeks before extraction.
