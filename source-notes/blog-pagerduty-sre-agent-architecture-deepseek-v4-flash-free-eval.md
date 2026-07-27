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

### Claim 1: The AI-native vs. AI-assisted distinction determines failure modes and engineering trade-offs for agent products
- **Evidence**: Authoritative — the authors draw this as the foundational framing
  for the entire architecture discussion, citing Joao Freitas's earlier PagerDuty
  post on production AI agents. The article is structured as a case study in what
  this distinction means in practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an
  existing system. In AI-native products, the AI is the system."
- **Our assessment**: This is a useful framing that the authors back with concrete
  examples throughout the article. It's a single-source claim but the reasoning
  is sound and the distinction has practical consequences for architecture
  decisions.

### Claim 2: Context rot creates a hard ceiling for the amount of context a single-agent architecture can handle
- **Evidence**: The Incident Context document included JSON blobs of alerts, past
  incidents, change events, runbook content, service topology, dependency graphs,
  historical patterns, and remediation options. The authors cite Liu et al.
  (2023) "Lost in the Middle" research showing model performance degrades beyond
  certain context thresholds. Newer models improve but cost and latency impacts
  remain.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows, not because the information isn't there but because the model
  struggles to weight it correctly."
- **Our assessment**: This is well-established in the literature and widely
  observed in practice. The authors' specific contribution is showing how context
  rot manifests in the SRE incident investigation domain, where context documents
  grow large and diverse quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. Agents that worked
  well at a certain feature set degraded as features accumulated because new
  capabilities competed with existing ones for model attention.
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between
  instruction volume and output quality"
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research
  backing, but the specific claim about agent degradation as features accumulate
  is the authors' production observation. This is a significant concern for teams
  building long-lived agent systems — feature work carries a hidden tax on
  existing capabilities.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search
  for evidence, evaluate — took several minutes. A moderately complex incident
  with three or four candidate causes could take 10+ minutes to diagnose. This is
  a direct production measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible. The latency is plausible given that each step
  involves LLM inference plus external API calls. The key insight is that this is
  an architectural problem (sequential execution of parallelizable work), not a
  model speed problem.

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the agent
  to finish, then restart with that context. The authors characterize this as the
  agent "operating without information the human already had." This was a
  consequence of the synchronous single-agent execution model.
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most important failure mode for live incident
  response. An agent that cannot accept mid-run input from the on-call engineer
  wastes time and ignores existing human knowledge. Directly supports keeping
  humans on the paging path.

### Claim 6: Three execution models exist for multi-agent investigation — sequential, parallel-wait-for-all, and concurrent fan-in — with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - Sequential: total time is sum of all sub-agent durations. "A slow hypothesis
    in the middle blocks everything behind it."
  - Parallel, wait for all: total time is slowest sub-agent. But the main agent
    is idle, cannot report progress, and "the graph is locked inside the parallel
    call until everything resolves."
  - Parallel fan-out, concurrent fan-in: dispatch all asynchronously, process
    each result as it arrives, user input is a first-class event alongside
    sub-agent results.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: This taxonomy is clearly reasoned with well-articulated
  trade-offs. The authors' contribution is mapping these models to SRE
  investigation domain requirements (real-time visibility, mid-run injection,
  cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: In LangGraph's BSP model, a parallel tool call is one superstep —
  control returns only after every tool in that batch resolves. The orchestrator
  cannot react to sub-agent 1's result while sub-agents 2 and 3 still run. No
  external event, including user input, can reach the graph while blocked inside
  a parallel tool call. Tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: This matches LangGraph's documented BSP/superstep design.
  The implication — framework-managed parallelism is incompatible with real-time
  interactivity — is a significant constraint for building interactive agent
  systems on LangGraph.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first completion
  resumed the graph. While processing, the second completion arrived and tried to
  resume the same graph. LangGraph either errored or started a fresh execution
  from scratch, losing state from the first arrival. The fix was a local queue
  where incoming results went and the main agent drained it one at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph execution model. The queue is the obvious
  fix, but the fact that the naive approach fails under realistic timing (two
  sub-agents finishing within seconds) is a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, a window remained between "main agent
  completed" and "graph re-interrupts" where the drain loop could call resume
  before the graph was genuinely paused. Fix: drain loop held a lock while
  resuming, graph signaled through a callback when it had re-interrupted,
  releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This concurrency edge case is easy to miss until production.
  The lock pattern is standard but the specific interaction with LangGraph's
  interrupt/resume lifecycle is a useful concrete example.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results via a two-level priority queue to enable mid-run steering
- **Evidence**: With a FIFO queue, if three sub-agent results were buffered and
  the user typed "also check the deployment logs," the user's message would go
  in fourth. By the time the drain loop reached it, the graph might have already
  finished. Fix: priority queue where user input is priority 0 (highest) and
  sub-agent results are priority 1. A route_event node branches: sub-agent
  results go to handle_sub_agent_result, user messages go to handle_user_input.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean, well-explained pattern. The priority queue is a
  simple primitive but essential — without it, user input can arrive too late to
  matter. The route_event branching design is a concrete LangGraph pattern worth
  adopting.

### Claim 11: The identity convention task_id === thread_id eliminates lookup tables and correlation logic for routing events to correct graphs
- **Evidence**: Every agent run gets a UUID task_id. Every sub-agent carries a
  parent_task_id pointing to whoever spawned it. By making LangGraph thread_id
  identical to task_id, when a sub-agent publishes a completion event carrying
  parent_task_id, the parent agent immediately knows which LangGraph thread to
  resume — no lookup table, no correlation logic.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: This is an elegant convention that eliminates an entire
  class of infrastructure. It is the kind of simple design decision that only
  becomes obvious after building the complex version.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed
  (separate processes, broker, durable store). Investigation is overwhelmingly
  IO-bound (call log API and wait, call metrics API and wait, hand text to model
  and wait). A single team owns the whole sub-agent system. Service boundaries
  would buy deployment complexity, service discovery, network failure modes, and
  distributed tracing without the benefits of CPU isolation or organizational
  ownership.
- **Confidence**: emerging
- **Quote**: "Spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive and valuable insight.
  The reflex to treat multi-agent systems as distributed is strong, and the
  authors make a clear argument for why it is wrong for IO-bound workloads.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable (checkpointed for pause/resume/recover).
  Sub-agents are stateless — no checkpoints. If a sub-agent dies, they re-spawn
  it rather than resume mid-flight. Making every agent durable would mean keeping
  N+1 checkpoints consistent. There is exactly one source of truth to recover.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: This asymmetric durability model reduces the recovery
  problem from distributed consensus to single-writer checkpoint. The trade-off
  — re-running sub-agent work on failure — is acceptable when sub-agents are
  cheap (IO-bound, no side effects beyond their result).

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The earlier distributed design required webhook callbacks, PubSub
  broadcast, and a durable event store — all to move results across a network.
  Once everything shares a process, the answer is an in-process mailbox — an
  asyncio.Queue — injected into each background task when spawned. Sub-agent
  writes its result to the queue; supervisor reads from it.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The natural consequence of the single-process decision and
  a dramatic simplification. Only works because sub-agents are guaranteed to live
  in the same process as their spawning supervisor.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: LangGraph's async sub-agents let the supervisor launch background
  tasks and return immediately without blocking. But polling means no push
  notification when a sub-agent finishes, so no deterministic synthesis the
  moment each result arrives. Native support stops short of true mid-run steering
  and gradual emission of artifacts as hypotheses resolve.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Framework evolution does not automatically solve the hard
  problems. The polling vs. push gap is smaller than the mid-run steering and
  progressive result emission gaps, which frameworks do not address.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives are essential before simplifying for production
- **Evidence**: The authors explicitly frame the complex version (webhooks,
  PubSub, durable event store) as a deliberate step, not a mistake. It let them
  identify which parts were essential and which were accidents of assuming a
  distributed architecture. The simplification to single process was only
  possible because they understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: This is advice, not a falsifiable claim. It is a valuable
  engineering philosophy demonstrated convincingly. The risk is teams using this
  to justify over-engineering that never gets simplified.

### Claim 17: Three insights — identity, event transport, and reactive loop — form a portable foundation for multi-agent architectures regardless of runtime engine
- **Evidence**: The authors identify three primitives that survive simplification
  from distributed to single-process: (1) Identity (task_id === thread_id) routes
  events without lookup tables; (2) Event transport delivers results reliably and
  handles late-joining clients; (3) Reactive loop processes results as they
  arrive, serializes concurrent completions, and treats user input as a
  first-class event.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as frameworks evolve."
- **Our assessment**: A useful distillation forming a reasonable abstraction
  stack (identity → transport → control loop). The portability claim is
  plausible but untested outside LangGraph.

## Concrete Artifacts

### Reactive loop node structure (as described in the article)

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

Where:
- `accept_event`: graph spends most of its life here, paused, waiting for drain loop
- `route_event`: inspects event type and branches
- `handle_sub_agent_result`: processes a sub-agent's findings
- `handle_user_input`: adds new work to state, marks as pending spawn
- `plan`: formulates investigation strategy based on current state
- `spawn_sub_agents`: dispatches new sub-agent background tasks

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
Priority 1:          Sub-agent results — processed in arrival order
```

### Single-process architecture summary

- Supervisor and all sub-agents share one process
- Mailbox: ordinary asyncio.Queue (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Multiple concurrent investigation runs can land on different pods
- Within one run, all sub-agents are co-located with their spawning supervisor

## Cross-References

- **Corroborates**: The merged baseline note
  ([blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md))
  corroborates all 17 claims in this eval note. Claims 1-17 map directly to the
  same numbered claims in the baseline, with identical extracted content and
  matching quotes. This is expected — both notes reference the same source URL.
  The complementary PagerDuty article
  ([blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md))
  corroborates Claim 2 (context rot) via its Claim 3 (context fatigue — the same
  failure mode under a different name). It also corroborates Claim 1
  (AI-native framing) as the foundational framing article.

- **Contradicts**: None identified. Both notes represent the same source material
  and agree across all claims.

- **Extends**: The baseline note extends this eval note as the authoritative
  merged reference. The complementary PagerDuty article extends Claims 1
  (AI-native framing), 12 (single-process simplification), and 16
  (build-to-understand methodology) with additional context from the companion
  production-gaps perspective.

- **Novel**: This eval note does not contribute novel claims beyond the baseline.
  It is an eval quality-comparison artifact re-extracting the same source with a
  different model (opencode/deepseek-v4-flash-free via OpenCode Action, Zen free
  chat-completions backend).

- **Related candidates dismissed**:
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md`: Dismissed —
    covers SRE in retail/gaming, not incident investigation agent architecture.
  - `source-notes/docs-google-sre-prodcast-04-05-furino-slos.md`: Dismissed —
    covers SLO construction, not agent systems.
  - `source-notes/docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`: Dismissed —
    covers Google horizontal AI-for-SRE tooling, not multi-agent architecture.
  - `source-notes/docs-google-sre-prodcast-03-06-incident-response-tooling.md`: Dismissed —
    covers incident response tooling broadly, not agent architecture.
  - `source-notes/docs-google-sre-prodcast-03-11-embracing-complexity.md`: Dismissed —
    covers sociotechnical complexity theory, not agent implementation.
  - `source-notes/docs-google-sre-prodcast-03-05-building-reliable-systems.md`: Dismissed —
    covers database reliability, not agent systems.
  - `source-notes/docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md`: Dismissed —
    covers ML training infrastructure, not incident investigation agents.
  - `source-notes/blog-incidentio-ai-sre-incident-run.md`: Dismissed —
    covers incident.io's AI SRE product experience, not PagerDuty's architecture.
  - `source-notes/docs-google-sre-prodcast-01-05-client-transparent-migrations.md`: Dismissed —
    covers migration client transparency, not agent architecture.

## Guide Impact

- **Chapter 00 (Principles)**: Provides evidence for "Design for AI-native failure
  modes" — context rot and instruction overload are structural, not incidental.
  Also supports "build to understand, ship simple" as an engineering principle.

- **Chapter 01 (Incident Response)**: Concrete architecture for AI-assisted
  incident investigation. Key claims: (a) real-time visibility is a hard
  requirement for live incidents; (b) mid-run human steering must be a first-class
  event; (c) sequential hypothesis testing creates unacceptable latency.

- **Chapter 03 (Runbooks and Agents)**: Patterns for multi-agent ops architecture:
  (a) three execution models and when to use each; (b) reactive loop pattern;
  (c) task_id === thread_id identity convention; (d) durable supervisor / stateless
  sub-agent asymmetry; (e) single-process simplification for IO-bound workloads.

- **Chapter 04 (Oncall and Toil)**: Investigation workflow (formulate hypotheses
  → spawn sub-agents → query logs/metrics → report findings → synthesize root
  cause) is a reusable pattern. Priority queue pattern (user input > sub-agent
  results) applies to any interactive on-call agent.

## Extraction Notes

- This is an eval-quality comparison note for issue #1
  (deepseek-v4-flash-free via OpenCode Action / Zen free chat-completions).
  Do not merge — compare against the merged DeepSeek/Flash baseline note
  (blog-pagerduty-sre-agent-architecture.md).
- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. No sub-pages were followed — the article is self-contained.
- Quotes were extracted via WebFetch and verified against the rendered page.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol). These were not independently fetched.
- The source is light on quantitative metrics; the only concrete number is
  "10+ minutes" for sequential diagnosis of a moderately complex incident.
- No part of the source was paywalled. Published June 24, 2026.
- The baseline merged note (PR #5) was used as cross-reference verification.