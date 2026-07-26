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

> A practitioner architecture post from PagerDuty Engineering describing the
> evolution of their SRE Agent from a single-agent monolith to a reactive
> multi-agent system with concurrent fan-in. Covers specific single-agent
> failure modes (context rot, instruction overload, sequential blocking,
> no interactivity), three execution models evaluated, the custom reactive
> loop built on LangGraph interrupt/resume, and the counterintuitive
> simplification from distributed services to a single-process architecture.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three current PagerDuty engineers who built the system:
  Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent
  from concept to GA), Ralph Bird (Principal ML Engineer, AI agents and LLM
  observability). First-hand production experience.
- **Scope**: Full architectural journey — single-agent failures, three execution
  models evaluated, custom reactive loop using LangGraph interrupt/resume,
  identity conventions, event transport design, single-process simplification,
  and durable-supervisor/stateless-sub-agents asymmetry. Does NOT cover:
  evaluation/accuracy metrics, cost data, specific model choices, or model
  hallucination recovery.

## Extracted Claims

### Claim 1: AI-native and AI-assisted products differ fundamentally in their reliability requirements and failure modes, with the SRE Agent being an AI-native system
- **Evidence**: The authors frame the entire article around this distinction,
  citing Freitas (2026) from the PagerDuty engineering blog. They state that
  in AI-native products "the AI *is* the system," which changes "the failure
  modes, the reliability requirements, and the engineering trade-offs."
- **Confidence**: emerging
- **Quote**: "In AI-native products, the AI *is* the system, which means the
  failure modes, the reliability requirements, and the engineering trade-offs
  are all different."
- **Our assessment**: This framing is used consistently throughout the article
  and directly shapes the engineering decisions described. The claim is backed
  by concrete architectural choices made in response to this distinction.

### Claim 2: Context rot creates a hard ceiling on how much context a single-agent can handle before model performance degrades
- **Evidence**: The Incident Context document in their single-agent system
  accumulated JSON blobs of alerts, past incidents, change events, runbook
  content, service topology, dependency graphs, historical patterns, and
  remediation options. The authors cite Liu et al. (2023) "Lost in the Middle"
  research showing model performance degrades beyond certain context thresholds.
- **Confidence**: settled
- **Quote**: "More data, worse decisions."
- **Our assessment**: This is well-established in LLM literature. The authors'
  contribution is demonstrating how this manifests in the SRE investigation
  domain, where context documents grow large rapidly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails,
  and system prompts in the single agent. The authors cite Jaroslawicz et al.
  (2025) finding an inverse relationship between instruction volume and output
  quality. They observed that "agents that worked well at a certain feature set
  started degrading as we added to it."
- **Confidence**: emerging
- **Quote**: "as the prompt gets longer, the model's ability to follow any given
  instruction decreases"
- **Our assessment**: The Jaroslawicz citation provides research backing, and
  the production observation adds practitioner weight. This is a structural
  problem for monolithic agents that scales with feature count.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency, making it impractical for incidents with multiple candidate causes
- **Evidence**: "A moderately complex incident with three or four candidate
  causes could take 10+ minutes to diagnose." Each root cause analysis step
  (formulate hypothesis, search for evidence, evaluate) takes several minutes
  because it chains LLM inference with external API calls.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible given the sequential nature of the single-agent
  design. The 10+ minute figure is the only concrete latency number in the
  article. The key insight is this is architectural, not a model speed problem.

### Claim 5: Lack of interactivity during agent execution was a structural failure of the single-agent design, not a missing UI feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the
  agent to finish and restart. The authors characterize this as "the agent was
  operating without information the human already had."
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is a critical failure mode for live incident
  response. The single-agent execution model structurally prevents the human
  from contributing their existing knowledge mid-run, making investigation
  slower and less informed than it should be.

### Claim 6: Three execution models exist for multi-agent investigation — sequential, parallel-wait-for-all, and concurrent fan-in — with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate all three models with diagrams and
  trade-offs. Sequential: total time = sum of all sub-agent durations, and "a
  slow hypothesis in the middle blocks everything behind it." Parallel wait:
  total time = slowest sub-agent, but the main agent is idle and can't report
  progress. Concurrent fan-in: all sub-agents dispatched asynchronously, each
  result processed as it arrives, user input is a "first-class event."
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: The taxonomy is well-reasoned and each model's trade-offs
  are clearly articulated. The authors' contribution is mapping these models
  to the specific requirements of SRE incident investigation.

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input impossible during parallel tool calls
- **Evidence**: LangGraph advances in supersteps — a parallel tool call is one
  superstep, so control returns only after every tool in the batch resolves.
  The orchestrator cannot react to individual sub-agent results as they arrive.
  No external event, including user input, can reach the graph while blocked
  inside a parallel call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model: it advances in *supersteps*, running a
  batch of work and then stopping at a synchronization barrier before the next
  batch begins."
- **Our assessment**: This is a specific technical claim about LangGraph's
  execution model that matches documented behavior. The implication —
  framework-managed parallelism is incompatible with real-time interactivity —
  is a significant constraint for interactive agent systems on LangGraph.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first
  completion resumed the graph and triggered the main agent's working loop.
  The second arrival tried to resume the same graph while still processing.
  "LangGraph either errored or started a fresh execution from scratch," losing
  state from the first arrival. The fix was a local queue that the drain loop
  processed one result at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical production sharp-edge. The queue serializes
  arrivals but alone is insufficient — a lock was also needed. This is valuable
  for anyone building similar systems on LangGraph.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there was a window between "main agent
  completed" and "graph re-interrupts" where the drain loop could call resume
  before the graph was genuinely paused. The fix: the drain loop held a lock
  while resuming, and the graph signaled through a callback when it had
  actually re-interrupted, releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A subtle concurrency edge case that's easy to miss until
  production. The lock pattern is standard but the specific interaction with
  LangGraph's interrupt/resume lifecycle is a useful concrete example.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering, requiring a priority queue
- **Evidence**: With a FIFO queue, if three sub-agent results were buffered and
  the user typed "also check the deployment logs," the user's message went in
  fourth. By the time the drain loop reached it, the graph might have finished.
  The fix: a two-level priority queue where user input is priority 0 (highest)
  and sub-agent results are priority 1. A `route_event` node branches based on
  event type.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean, well-explained pattern. Without the priority
  queue, user input can arrive too late to affect the investigation.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events to the correct LangGraph thread
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries a
  `parent_task_id` pointing to whoever spawned it. By making `thread_id` equal
  to `task_id`, when a sub-agent publishes a completion event with
  `parent_task_id: task-001`, the parent immediately knows which thread to
  resume. The authors call this "the single most important convention."
- **Confidence**: emerging
- **Quote**: "The identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: An elegant design convention that eliminates an entire
  class of infrastructure (lookup tables, correlation services). Worth adopting
  as a pattern for any multi-agent system on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed
  (separate processes, broker, durable store), then questioned the assumption.
  Investigation is overwhelmingly IO (call log API and wait, call metrics API
  and wait, hand text to model and wait). A single team owns the whole system.
  Spreading IO-bound agents across services buys "operational complexity —
  deployment, service discovery, network failure modes, distributed tracing —
  without buying the thing services are for."
- **Confidence**: emerging
- **Quote**: "Spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive insight. The reflex
  to treat multi-agent as distributed is strong. The key qualifier is
  "IO-bound" — this does not generalize to compute-bound workloads. For the
  common SRE investigation case, it is a powerful simplification.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable with checkpointed state so it can
  pause, resume, and recover. Sub-agents are stateless with no checkpoints.
  If a sub-agent dies, "we re-spawn it rather than resume it mid-flight."
  Making every agent durable would require keeping N+1 checkpoints consistent.
  By concentrating durability in the supervisor, there is exactly one source
  of truth. Each processing step is atomic and persisted before the next event.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: A clean design principle that reduces recovery from a
  distributed consensus problem to a single-writer checkpoint. The trade-off —
  re-running sub-agent work on failure — is acceptable when sub-agents are
  cheap (IO-bound, no side effects beyond their result).

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The earlier distributed design required webhook callbacks,
  PubSub broadcast, and a durable event store to move results across a network.
  Once everything shares a process, the answer is "an in-process mailbox — an
  asyncio.Queue — injected into each background task when it's spawned." The
  sub-agent writes to the queue; the supervisor reads from it. No broker, no
  callback endpoint, no network hop.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The natural consequence of the single-process decision
  and a dramatic simplification. Only works because sub-agents are guaranteed
  to live in the same process as their spawning supervisor.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission that still requires the same custom primitives
- **Evidence**: LangGraph's async sub-agents let the supervisor launch
  background tasks and return immediately without blocking. But the polling
  model means "no push notification when a sub-agent finishes, which means no
  deterministic synthesis the moment each result arrives." Native support
  "stops short of the two things our SRE Agent actually needs: true mid-run
  steering, and gradual emission of artifacts as each hypothesis resolves."
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: An important qualification. Polling vs. push is the
  smaller gap; the bigger gap is mid-run steering and progressive result
  emission, which frameworks don't address.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives are essential before simplifying for production
- **Evidence**: The authors explicitly frame the complex version (webhooks,
  PubSub, durable event store) as "a deliberate step, not a mistake." It let
  them identify which parts were essential and which were accidents of assuming
  a distributed architecture. They recommend this as a general methodology.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: This is advice, not a falsifiable claim. It is a valuable
  engineering philosophy demonstrated convincingly in their own work. The risk
  is teams might use this to justify over-engineering without the follow-through
  simplification.

### Claim 17: Three primitives — identity, event transport, and reactive loop — form a portable foundation for multi-agent architectures regardless of runtime engine
- **Evidence**: The authors identify three primitives: (1) Identity
  (`task_id === thread_id`) routes events to the right graph without lookup
  tables; (2) Event transport delivers results reliably and survives restarts;
  (3) Reactive loop processes results as they arrive, serializes concurrent
  completions, and treats user input as a first-class event. These survive the
  simplification from distributed to single-process and would apply to any
  runtime.
- **Confidence**: emerging
- **Quote**: "Understanding *why* each layer exists is what lets you extend it
  or replace individual pieces as your framework evolves."
- **Our assessment**: A useful distillation of the architecture into three
  portable primitives. The portability claim is plausible but untested beyond
  LangGraph.

## Concrete Artifacts

### Reactive loop node structure (from the article)

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

### Identity hierarchy (from the article)

```
Main Agent (task_id: task-001, thread_id: task-001)
    ├── Sub-Agent 1 (task_id: sub-1, parent_task_id: task-001)
    │     └→ completes → publishes event with parent_task_id: task-001
    │                  → parent agent resumes thread_id: task-001
    ├── Sub-Agent 2 (task_id: sub-2, parent_task_id: task-001)
    └── Sub-Agent 3 (task_id: sub-3, parent_task_id: task-001)
```

### Priority queue levels (from the article)

```
Priority 0 (highest): User input — processed first, jumps the line
Priority 1:          Sub-agent results — processed in arrival order after any pending user input
```

### Single-process architecture (from the article)

- Supervisor and all sub-agents share one process
- Mailbox: ordinary asyncio.Queue (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Multiple concurrent runs can land on different pods
- Within one run, all sub-agents are co-located with their spawning supervisor

### A2A-inspired lifecycle states

```
working → completed | failed | canceled
```

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-production-ai-agent-gaps.md` (issue #4): Claim 3 (Context
    fatigue) corroborates this note's Claim 2 (Context rot) — same failure mode,
    different terminology. Claim 8 (Architecture evolution: single → supervisor
    → hierarchical) corroborates this note's Claim 6 (Three execution models)
    and Claim 16 (Build hard, ship simple). The companion article is cited as
    foundational framing in this note's Claim 1.

- **Contradicts**: None identified.

- **Extends**: None — this is the primary architecture deep-dive. The companion
  article (`blog-pagerduty-production-ai-agent-gaps.md`) covers evaluation,
  metrics, and guardrails that this article explicitly excludes.

- **Novel**: All claims are novel to the corpus at the time of publication. Key
  novel contributions:
  - The three execution models mapped to SRE investigation requirements
  - The LangGraph BSP limitation for interactive agent systems
  - The queue+lock pattern for serializing concurrent graph resumes
  - The priority queue pattern for user input preemption in agent loops
  - The `task_id === thread_id` identity convention
  - The single-process simplification argument for IO-bound agent workloads
  - The durable supervisor / stateless sub-agent asymmetry
  - The "build hard, ship simple" methodology demonstrated end-to-end

### Candidate file dismissals (from miner-related-notes.md)

The following candidates from `miner-related-notes.md` were reviewed and
dismissed as non-overlapping with this source:
- `docs-google-sre-prodcast-03-07-retail-gaming.md` — gaming/retail SRE focus;
  no agent architecture overlap
- `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO theory; no architecture
  overlap
- `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — Google AI-for-SRE tools;
  different domain (ticket/incident analysis vs. custom agent architecture)
- `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — incident
  response tooling generally; no agent architecture overlap
- `docs-google-sre-prodcast-03-11-embracing-complexity.md` — sociotechnical
  complexity theory; no agent architecture overlap
- `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — database
  reliability; no agent architecture overlap
- `docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` — ML training
  infrastructure; no agent architecture overlap
- `blog-incidentio-ai-sre-incident-run.md` — AI SRE user experience (incident.io);
  different angle (UX/practical use vs. architecture deep-dive)
- `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` — client
  transparency during migrations; no agent architecture overlap

## Guide Impact

- **Chapter 00 (Principles)**: Supports a new principle distinguishing AI-native
  from AI-assisted product engineering. Context rot and instruction overload are
  structural failure modes specific to AI-native systems. The "build hard, ship
  simple" methodology is directly extractable as engineering guidance.

- **Chapter 01 (Incident Response)**: Concrete architecture evidence that
  AI-assisted incident investigation requires: (a) real-time visibility into
  agent reasoning, (b) mid-run human steering as a first-class event, (c) parallel
  hypothesis testing (not sequential), (d) the agent must never operate without
  information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Direct patterns for multi-agent ops
  architecture: the three execution models and their trade-offs, the reactive
  loop (interrupt/resume, priority queue, lock), the `task_id === thread_id`
  identity convention, durable supervisor / stateless sub-agent asymmetry, and
  the single-process simplification for IO-bound workloads.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate
  hypotheses → spawn sub-agents → query logs/metrics → report → synthesize) is
  a directly reusable pattern for on-call tooling. The priority queue pattern
  (user input > sub-agent results) applies to any interactive on-call agent.

## Extraction Notes

- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. No sub-pages were followed — the article is self-contained.
- Quotes were extracted by reading the full rendered page via WebFetch. All
  quotes are verbatim. The Assayer should spot-check key quotes against the
  live URL.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol). These were not independently fetched.
- The source is rich in architectural detail but light on quantitative metrics.
  The one concrete number is "10+ minutes" for sequential diagnosis.
- Published June 24, 2026 — approximately 1 month before extraction.
- This eval note was produced by `opencode/deepseek-v4-flash-free` via OpenCode
  Action (zen-free backend) as a candidate model comparison against the baseline
  DeepSeek/Flash note at `blog-pagerduty-sre-agent-architecture.md`.
- Extracted 17 claims matching the baseline note's scope. The model's extraction
  is comparable in depth to the baseline, with similar claim structure and
  quote accuracy.
