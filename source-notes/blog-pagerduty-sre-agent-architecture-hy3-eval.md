---
source_url: https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
source_type: blog-post
title: "Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation"
author: "Viktor Vasylkovskyi, Micah Mayo, Ralph Bird (PagerDuty Engineering)"
date_published: 2026-06-24
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: emerging
issue: "#1-hy3-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> A detailed practitioner writeup from PagerDuty Engineering describing the
> architectural evolution of their SRE Agent from a single-agent monolith to a
> reactive multi-agent system. Covers specific AI-native failure modes (context
> rot, instruction overload), three execution models with trade-offs, a custom
> reactive loop built on LangGraph interrupt/resume primitives, and the
> counterintuitive simplification from distributed to single-process architecture.
> Published June 2026 — very recent, with concrete production patterns.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three engineers at PagerDuty who built the system they
  describe — Viktor Vasylkovskyi (Senior SWE, Python/AWS/LangGraph), Micah Mayo
  (Staff SWE, co-led SRE Agent from concept to GA and shaped cross-team agentic
  patterns), Ralph Bird (Principal ML Engineer, AI agents and LLM observability,
  previously an astrophysics researcher at UCLA and a nuclear safety engineer at
  Rolls-Royce). This is first-hand production experience, not a thought-piece.
- **Scope**: Covers the full architectural journey — why a single agent failed,
  the three execution models evaluated, the custom reactive loop built from first
  principles (interrupt/resume, priority queue, lock-and-drain serialization),
  the three primitives surfaced (identity, transport, reactive loop), and the
  simplification that collapsed distributed machinery into a single process with
  a durable supervisor and stateless sub-agents. Also covers the A2A-inspired
  lifecycle, callback/dependency-injection decoupling, the "build hard, ship
  simple" methodology, and a balanced take on when native framework async support
  suffices. Does NOT cover: evaluation/accuracy metrics, cost data, specific
  model choices, or failure recovery from model hallucinations (the companion
  Freitas piece, `blog-pagerduty-production-ai-agent-gaps.md`, covers those).

## Extracted Claims

### Claim 1: The distinction between AI-native and AI-assisted products changes the failure modes, reliability requirements, and engineering trade-offs
- **Evidence**: The authors open with this as the foundational framing for the
  entire architecture discussion and cite João Freitas's companion PagerDuty post
  (Production AI Agents) as the fuller treatment. The article is structured as a
  case study in what the distinction means in practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an
  existing system. In AI-native products, the AI is the system"
- **Our assessment**: A useful framing the authors back with concrete examples
  throughout. It is a single-source claim, but the reasoning is sound and the
  distinction has practical consequences for architecture decisions (see Claims 2
  and 3, which are framed as AI-native-specific failure modes). The companion
  PagerDuty note (`blog-pagerduty-production-ai-agent-gaps.md`, Claim 1) opens
  from the same premise.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document in their single-agent system grew
  to include JSON blobs of alerts, past/related incidents, change events, runbook
  content, notes, service topology, dependency graphs, historical patterns, and
  remediation options. The authors cite Liu et al. (2023) "Lost in the Middle,"
  noting model performance degrades beyond a threshold "not because the
  information isn't there but because the model struggles to weight it correctly."
  Newer models improve but still cost latency and money.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows"
- **Our assessment**: Well-established in the literature (Liu et al. 2023) and
  widely observed. The authors' specific contribution is showing how it manifests
  in SRE incident investigation, where context documents grow large and diverse
  quickly. Corroborated by the companion PagerDuty note
  `blog-pagerduty-production-ai-agent-gaps.md` (Claim 3, "context fatigue" — same
  phenomenon, both citing Liu et al. 2023).

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. In a monolithic
  agent, "adding a new capability competes with every existing capability for the
  model's attention."
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between
  instruction volume and output quality"
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research
  backing. The specific claim about agent degradation as features accumulate is
  the authors' production observation. Significant for any team building long-lived
  agent systems: feature work carries a hidden tax on existing capabilities.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root-cause chain (formulate hypothesis → search for
  evidence → evaluate) took several minutes; sequential hypothesis testing
  multiplied that. A direct production measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible. The latency is architectural (sequential execution
  of parallelizable work), not a model-speed problem. Each step combines LLM
  inference with external API calls (log search, metrics query). The key insight
  for the guide: this latency class is unacceptable for live incidents.

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the agent
  to finish, then restart with that context. The authors characterize this as the
  agent "operating without information the human already had" — a consequence of
  the synchronous single-agent execution model, not a bug.
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: The most important failure mode for live incident response.
  An agent that cannot accept mid-run human input wastes time and ignores the
  human's existing knowledge. This directly supports keeping humans on the paging
  path. The incident.io note (`blog-incidentio-ai-sre-incident-run.md`,
  Cross-References → Corroborates) independently demonstrates a design response to
  exactly this failure mode.

### Claim 6: Three execution models exist for multi-agent investigation, with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - **Sequential**: Total time = sum of sub-agent durations. "A slow hypothesis in
    the middle blocks everything behind it."
  - **Parallel, wait for all**: Total time = slowest sub-agent, but the main agent
    is idle, cannot report progress, and "the graph is locked inside the parallel
    call until everything resolves"; one hung sub-agent blocks synthesis
    indefinitely.
  - **Parallel fan-out, concurrent fan-in**: Dispatch all asynchronously, process
    each result as it arrives; user input is "a first-class event alongside
    sub-agent results." The main agent is never idle, the user always has
    visibility, new work can be injected at any point. Hidden cost: implementation
    complexity (interrupt/resume, a buffer for concurrent arrivals, prioritization).
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: The taxonomy is clearly reasoned with concrete trade-offs
  mapped to SRE-investigation requirements (real-time visibility, mid-run
  injection, cancellation). The authors' contribution is not inventing these
  models but mapping them to the domain. The incident.io note
  (`blog-incidentio-ai-sre-incident-run.md`, Cross-References → Extends) shows a
  UX-level implementation of the concurrent-fan-in principle.

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: They tried LangChain Deep Agents with sub-agents as tools. In
  LangGraph's BSP model, a parallel tool call is one superstep — "running a batch
  of work and then stopping at a synchronization barrier before the next batch
  begins." Control returns only after every tool in that batch resolves.
  Consequences: the orchestrator cannot react to sub-agent 1's result at t=3min
  while 2 and 3 still run; no external event (including user input) can reach the
  graph while blocked inside a parallel call; the tool set is fixed at dispatch.
  This gap — "our desired properties are per-result reactivity" — is why they built
  the reactive loop themselves.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: A specific technical claim about LangGraph's execution model
  that matches the documented BSP/superstep design. The implication — that
  framework-managed parallelism is incompatible with real-time interactivity — is
  a significant constraint for anyone building interactive agent systems on
  LangGraph. The authors note an async-subagents feature has since been added and
  address it in Claim 15.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first completion
  resumed the graph and triggered the main agent's working loop; while it was
  still processing, the second completion arrived and tried to resume the same
  graph. "LangGraph either errored or started a fresh execution from scratch,"
  losing the state from the first arrival. The fix: a local queue — incoming
  results went into the queue, and the main agent drained it one result at a time,
  resuming only after the previous resume fully completed and the graph
  re-interrupted. In practice sub-agents finished minutes apart, so the queue was
  insurance for the edge case where two arrivals landed within seconds.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph execution model. The queue is the obvious
  fix, but the fact that the naive approach fails under realistic timing (two
  sub-agents finishing within seconds) is a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, a window remained between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the next
  item and call `Command(resume=...)` before the graph was genuinely paused — same
  race, different shape. The fix: the drain loop held a lock while resuming, and
  the graph signaled through a callback when it had actually re-interrupted,
  releasing the lock, so the graph was never resumed twice in flight.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The kind of concurrency edge case easy to miss until it hits
  production. The lock pattern is standard, but the specific interaction with
  LangGraph's interrupt/resume lifecycle is a useful concrete example. The authors
  call the drain loop "the spine of the whole architecture."

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a FIFO queue, if three sub-agent results were buffered and
  the user typed "also check the deployment logs from this morning," the user's
  message went in fourth — or by the time the drain loop reached it, the graph
  might have already finished and reached END, so the user's hypothesis would
  never spawn. The fix: a two-level priority queue — user input priority 0
  (highest), sub-agent results priority 1 — so a user event jumps the line. A
  `route_event` node then branches: sub-agent results → `handle_sub_agent_result`;
  user messages → `handle_user_input`, which adds the new work to state, marks it
  `pending_spawn`, and re-enters `plan` so the new sub-agent is dispatched
  immediately.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean, well-explained pattern. Without it, user input can
  arrive too late to matter. The `route_event` branching design is a concrete
  LangGraph pattern worth noting. The incident.io note
  (`blog-incidentio-ai-sre-incident-run.md`, Cross-References → Corroborates)
  independently treats human input as a first-class event that must not be blocked
  by agent execution.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID `task_id`; every sub-agent carries a
  `parent_task_id` pointing to whoever spawned it. By making the LangGraph
  `thread_id` identical to the agent's `task_id`, when a sub-agent publishes a
  completion event carrying `parent_task_id: task-001`, the parent immediately
  knows which LangGraph thread to resume — no lookup table, no correlation logic.
  The authors call this "the single most important convention in the system."
- **Confidence**: emerging
- **Quote**: "The identifier on the event was the identifier of the graph that
  needed to wake up."
- **Our assessment**: An elegant convention that eliminates an entire class of
  infrastructure (lookup tables, correlation services). The kind of simple design
  decision that only becomes obvious after building the complex version. Worth
  adopting for any multi-agent system built on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries; splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: They initially built as if agents were distributed (separate
  processes, a broker, a durable store). The usual justifications for service
  boundaries don't apply: investigation is overwhelmingly IO (call a log API and
  wait, call a metrics API and wait, hand the text to the model and wait) — "no
  compute hotspot to isolate"; and a single team owns the whole sub-agent system,
  so there are no team boundaries for service boundaries to mirror. Spreading
  IO-bound agents across services buys "deployment, service discovery, network
  failure modes, distributed tracing — without buying the thing services are for."
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive and valuable insight.
  The reflex to treat a multi-agent system as a distributed system is strong; the
  authors make a clear, specific argument for why it is wrong for this workload
  class. The key qualifier is "IO-bound" — this does not generalize to
  compute-bound agent workloads. For the common SRE case (query external APIs, wait
  for LLM responses), it is a powerful simplification. The companion PagerDuty note
  (`blog-pagerduty-production-ai-agent-gaps.md`, Claim 11) makes the adjacent
  point that not everything needs to be probabilistic — build first, then replace
  unnecessary LLM calls with deterministic code.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — its state, including the in-process
  message queue, is checkpointed, so it can pause, resume, and recover; it is the
  long-running component, so failing mid-execution wastes minutes or hours.
  Sub-agents are stateless — no checkpoints; if one dies, they re-spawn it rather
  than resume it mid-flight. Making every agent durable would mean keeping N+1
  checkpoints consistent and reconciling them on every restart. With durability
  concentrated in the supervisor, there is exactly one source of truth. Each drain
  step is atomic and persisted before the next event is touched, so the checkpoint
  never captures in-flight mailbox contents; on restart the supervisor reloads its
  last checkpoint with an empty queue and re-spawns any still-running sub-agents.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: A clean asymmetric durability model that reduces the recovery
  problem from a distributed-consensus problem to a single-writer checkpoint. The
  trade-off — re-running sub-agent work on failure — is acceptable when sub-agents
  are cheap (IO-bound, no side effects beyond their result). The atomic-step-per-
  event guarantee simplifies crash-recovery reasoning.

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The earlier distributed design required webhook callbacks, a PubSub
  broadcast, and a durable event store — all to move results across a network.
  Once everything shares a process, the answer is "an in-process mailbox — an
  asyncio.Queue — injected into each background task when it's spawned." The
  sub-agent writes its result to the queue; the supervisor reads from it. No
  broker, no callback endpoint, no network hop. Dependency injection keeps the
  sub-agent ignorant of the transport: it is handed a queue to write to and knows
  nothing about who reads it. This is enabled by the co-location decision in Claim
  12.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A natural consequence of the single-process decision and a
  dramatic simplification. It only works because sub-agents are guaranteed to live
  in the same process as their spawning supervisor. Multiple concurrent
  investigation runs can still land on different pods, but within one run all
  sub-agents are co-located.

### Claim 15: Framework-native async sub-agents (polling-based) can meet many latency needs, but they do not address the two hard requirements — true mid-run steering and gradual artifact emission
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after
  their initial experiments), which let the supervisor launch background tasks and
  return immediately without blocking. The pull-based polling model means "no push
  notification when a sub-agent finishes, which means no deterministic synthesis
  the moment each result arrives" — but the article qualifies that "that gap often
  matters less than it first appears," since a few-second polling cycle is invisible
  for minute-long sub-agents, and explicitly advises: "Before building the custom
  reactive loop ... first verify that your latency requirements genuinely can't be
  met by polling." The deeper reason they still built custom: native support "stops
  short of the two things our SRE Agent actually needs: true mid-run steering, and
  gradual emission of artifacts as each hypothesis resolves." Since getting those
  requires reimplementing identity, transport, and the reactive loop with a
  priority queue anyway, "the native layer isn't buying us much. The hard
  part — the inter-agent communication — is still ours to build."
- **Confidence**: emerging
- **Quote**: "the native support stops short of the two things our SRE Agent
  actually needs: true mid-run steering, and gradual emission of artifacts as each
  hypothesis resolves."
- **Our assessment**: An important, balanced qualification. Framework evolution
  does not automatically solve the hard problems, but the authors are careful not
  to overstate the gap — polling-versus-push is the smaller issue; mid-run steering
  and progressive emission are what frameworks don't address, and they are exactly
  the pieces built by hand. This has direct implications for anyone choosing
  between building custom loops and waiting for framework support: build custom
  only if steering/streaming requirements truly fail polling.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors frame the complex version (webhooks, PubSub, durable
  event store, the full primitive set) as "a deliberate step, not a mistake." It
  let them see which parts were essential and which were "accidents of assuming a
  distributed architecture." The shippable design — one process, a durable
  supervisor, stateless sub-agents, an in-process mailbox — was reached by taking
  complexity away. They recommend this as a general methodology and note that
  building a proof of concept "is a proven way to get the actual feel of the
  trade-off, and ... the feel of what to throw away."
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: Advice, not a falsifiable claim. A valuable engineering
  philosophy the authors demonstrate convincingly — but it carries the risk that
  teams justify over-engineering that never gets simplified. The authors avoid this
  trap by actually shipping the simple version, which is the part most worth
  emulating. The incident.io note (`blog-incidentio-ai-sre-incident-run.md`,
  Cross-References → Extends) parallels this with its "better to be right than
  first" philosophy and 18-month dogfooding cycle.

### Claim 17: Three insights — identity, event transport, and reactive loop — remain true regardless of runtime engine, forming a portable foundation for multi-agent architectures
- **Evidence**: The authors identify three primitives that survive the
  simplification from distributed to single-process and would apply to any runtime
  engine: (1) Identity (`task_id === thread_id`) routes events to the right graph
  without lookup tables; (2) Event transport delivers results reliably, handles
  late-joining clients, and survives restarts; (3) Reactive loop processes results
  as they arrive, serializes concurrent completions, and treats user input as a
  first-class event. The article closes by arguing that "Understanding why each
  layer exists is what lets you extend or replace individual pieces as your
  framework evolves" — the difference between inheriting an architecture and owning
  it.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend it or
  replace individual pieces as your framework evolves."
- **Our assessment**: A useful distillation. The three primitives form a reasonable
  abstraction stack (identity → transport → control loop) that could guide design
  even outside LangGraph. The portability claim is plausible but untested — the
  authors only implemented on LangGraph.

### Claim 18: Each agent wraps its logic in an A2A-protocol-inspired lifecycle (working → completed | failed | canceled)
- **Evidence**: "Each agent wrapped its logic in a simple lifecycle: working →
  completed | failed | canceled. Inspired by the A2A protocol." Progress events
  flowed into a shared event queue; parent agents subscribed to the same channel to
  pick up sub-agent completions and resume graphs. The lifecycle is what lets a
  parent "stop a sub-agent" and "propagate the event correctly," and supports
  post-mortem analysis when an agent fails.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A small but concrete pattern. Adopting a standard lifecycle
  state machine (rather than ad-hoc status strings) gives cancellation propagation
  and failure handling a clean contract. Worth noting for any multi-agent system
  that needs reliable cancellation — a stated requirement ("user cancellation") for
  the SRE Agent.

### Claim 19: Transport decoupling via callback injection (and later dependency injection) keeps graph nodes ignorant of queues, task IDs, and transport
- **Evidence**: Progress reporting from graph nodes flowed through callbacks
  injected via LangGraph's `configurable` dict, "keeping the graph nodes entirely
  decoupled from transport. A node would invoke a callback it received through
  configuration without knowing anything about queues or task IDs — the transport
  concerns stayed at the agent runner level." Later, in the single-process design,
  dependency injection hands each sub-agent a queue to write to, "knows nothing
  about who reads it — exactly the decoupling the callback-injection layer gave
  us, now without the network."
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A clean separation-of-concerns pattern. Keeping transport at
  the agent-runner layer (not baked into node logic) is what makes the later
  collapse from distributed transport to an in-process queue a local change rather
  than a rewrite. This is the kind of coupling lesson that generalizes beyond
  LangGraph.

### Claim 20: The failure modes compound — context rot and instruction overload push toward multi-agent; parallelism pushes toward async; IO-bound work lets that fit in a single process
- **Evidence**: The authors' closing "Key Takeaways" state the pattern explicitly:
  "context rot and instruction overload push you toward multi-agent architectures;
  multi-agent parallelism pushes you toward async execution; and because the work
  is IO-bound rather than compute-bound, that async execution fits in a single
  process with a durable supervisor and stateless sub-agents — which is what lets
  the queue, lock, and priority pattern stay simple in-process primitives instead
  of distributed machinery you'd have to reconcile across services."
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A strong synthesizing insight that ties the whole article
  together. It is a design-derivation chain: each failure mode dictates the next
  architectural move, and the final single-process simplification is a consequence
  of the workload being IO-bound, not an assumption. Useful as a rationale when
  teaching the architecture end-to-end.

## Concrete Artifacts

### Reactive loop node structure (verbatim from the article)

The reactive loop is six LangGraph nodes. `accept_event` is where the graph spends
most of its life — paused, waiting for the drain loop to deliver the next event
from the priority queue.

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

- `accept_event`: graph paused, waiting for the next event from the priority queue.
- `route_event`: inspects the event type and branches.
- `handle_sub_agent_result`: processes a sub-agent's findings.
- `handle_user_input`: adds new work to state, marks `pending_spawn`, re-enters
  `plan` so the new sub-agent is dispatched immediately.
- `plan`: formulates investigation strategy from current state.
- `spawn_sub_agents`: dispatches new sub-agent background tasks.

### Identity hierarchy (verbatim from the article)

```
Main Agent (task_id: task-001, thread_id: task-001)
│
├── Sub-Agent 1 (task_id: sub-1, parent_task_id: task-001)
│ └→ completes → publishes event with parent_task_id: task-001
│ → parent agent resumes thread_id: task-001
├── Sub-Agent 2 (task_id: sub-2, parent_task_id: task-001)
└── Sub-Agent 3 (task_id: sub-3, parent_task_id: task-001)
```

"`task_id` was what was running. `parent_task_id` was what spawned it."

### Lifecycle states (A2A-protocol-inspired, verbatim)

```
working → completed | failed | canceled
```

### Priority queue levels (verbatim)

```
Priority 0 (highest): User input — processed first, jumps the line
Priority 1:          Sub-agent results — processed in arrival order after any pending user input
```

### Single-process architecture (as described in the article)

- Supervisor and all sub-agents share one process (co-located).
- Mailbox: ordinary `asyncio.Queue` (in-process), injected into each background
  task at spawn.
- Only the supervisor reaches out to a durable store; the queue/checkpoint lives
  inside the supervisor and survives a crash because the supervisor's state does.
- Sub-agents: stateless, no checkpoints, re-spawned on failure.
- Multiple concurrent investigation runs can still land on different pods/processes
  (cross-process primitives remain at the supervisor boundary: durable store,
  broker, or webhook for outside work).
- The drain loop: acquire lock → resume graph → run until it re-interrupts →
  release lock → wait on queue. Each step atomic and checkpointed before the next
  event is touched, so the checkpoint never holds in-flight mailbox contents.

### Key Takeaways — the compounding design rationale (verbatim excerpt)

```
context rot and instruction overload push you toward multi-agent architectures;
multi-agent parallelism pushes you toward async execution; and because the work
is IO-bound rather than compute-bound, that async execution fits in a single
process with a durable supervisor and stateless sub-agents — which is what lets
the queue, lock, and priority pattern stay simple in-process primitives instead
of distributed machinery you'd have to reconcile across services.
```

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-production-ai-agent-gaps.md` (Claim 3, "context fatigue"):
    the companion PagerDuty piece describes the same phenomenon — early prompt
    instructions losing probabilistic weight as tokens accumulate — under a
    different name, and both cite Liu et al. (2023). Its Claim 8 (architecture
    evolution single → supervisor → hierarchical, "earn complexity") and Claim 11
    (replace unnecessary LLM calls with deterministic code) parallel this source's
    "build hard, ship simple" and IO-bound-simplification arguments. The companion
    piece is the foundational framing article this source cites for the AI-native
    vs. AI-assisted distinction (Claim 1).
  - `blog-incidentio-ai-sre-incident-run.md` (Cross-References → Corroborates):
    that note independently corroborates this source's Claim 5 (lack of
    interactivity as a structural failure — it demonstrates a design response where
    human and AI investigate in parallel with bidirectional context sync) and
    Claim 10 (human input as a first-class, non-blockable event). It also Extends
    Claim 6 (concurrent fan-in) with a UX-level implementation, and Claim 16
    ("build hard, ship simple") with its "better to be right than first" philosophy.

- **Contradicts**: None identified. The PagerDuty "production AI agent gaps" note
  operates at a different layer (evaluation, metrics, guardrails, UX) and is
  explicitly the framing precursor this source cites; the incident.io note covers
  user-facing interaction design and multi-surface orchestration. All three are
  complementary.

- **Extends**: This source provides the "how" (reactive loop, identity, transport,
  durability model) that the companion PagerDuty note's "what to evaluate/measure"
  implicitly assumes. Together they are the two halves of PagerDuty's production
  agent picture.

- **Novel**: Relative to the rest of the corpus, this source is the first to
  provide: the three execution models mapped to SRE-investigation requirements; the
  LangGraph BSP limitation for interactive agent systems; the queue+lock pattern
  for serializing concurrent graph resumes; the priority-queue pattern for user-
  input preemption; the `task_id === thread_id` identity convention; the single-
  process simplification argument for IO-bound agent workloads; the durable
  supervisor / stateless sub-agent asymmetry; the A2A-inspired lifecycle; and the
  callback/dependency-injection transport-decoupling pattern.

  **Note on the DeepSeek baseline**: the merged note
  `blog-pagerduty-sre-agent-architecture.md` (issue #1, PR #5) extracts the *same*
  source. This Hy3-eval note is an independent reproduction for model-quality
  comparison. It reproduces the baseline's 17 claims faithfully (all direct quotes
  in this note were checked character-for-character against the live source and
  match the baseline's), and adds three claims the baseline did not separate out
  (Claim 18 A2A lifecycle, Claim 19 transport decoupling via injection, Claim 20
  the compounding design rationale). It also corrects the baseline's
  Cross-References section, which said "Corroborates: None" — at extraction time
  the companion PagerDuty note and the incident.io note already existed and
  genuinely corroborate/extend several claims (see above).

## Guide Impact

- **Chapter 00 (Principles)**: Evidence for two principles — (a) "design for
  AI-native failure modes": context rot and instruction overload are structural,
  not incidental, and distinguishing AI-native from AI-assisted changes reliability
  requirements (Claim 1-3, 20); (b) "build to understand, ship simple" as an
  engineering methodology for agent systems (Claim 16).

- **Chapter 01 (Incident Response)**: A concrete architecture for AI-assisted
  incident investigation. Incorporate: (a) real-time visibility into agent
  reasoning is a hard requirement for live incidents, not a nice-to-have (Claim
  5-6); (b) mid-run human steering must be a first-class event, not an afterthought
  (Claim 5, 10); (c) sequential hypothesis testing creates unacceptable latency for
  incidents with multiple candidate causes (Claim 4, 6); (d) the agent should never
  operate without information the human already has (Claim 5).

- **Chapter 03 (Runbooks and Agents)**: Multi-agent ops architecture patterns —
  (a) the three execution models and when to use each (Claim 6); (b) the reactive
  loop pattern (interrupt/resume, priority queue, lock serialization) for
  interactive agent systems (Claim 8-10); (c) the `task_id === thread_id` identity
  convention for routing events (Claim 11); (d) the durable supervisor / stateless
  sub-agent asymmetry for reliability without distributed complexity (Claim 13);
  (e) the single-process simplification argument — IO-bound agent workloads don't
  need service boundaries (Claim 12, 14, 20); (f) the A2A-inspired lifecycle for
  cancellation propagation (Claim 18); (g) transport decoupling via injection
  (Claim 19).

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate
  hypotheses → spawn sub-agents → query logs/metrics → report findings → synthesize
  root cause) is a reusable pattern for on-call tooling. The priority-queue pattern
  (user input > sub-agent results) applies to any interactive on-call agent (Claim
  10). Also: before building a custom reactive loop, verify polling-based framework
  async support can't meet latency needs (Claim 15) — a guardrail against
  over-engineering.

## Extraction Notes

- The source is a single long-form blog post (28-minute read) on PagerDuty's
  engineering blog. Self-contained; no sub-pages were required — all architectural
  detail is inline. Fetched as HTML (HTTP 200) and converted to text; the full
  article was read end-to-end, not skimmed.
- All quotes marked direct in this note were copied character-for-character from
  the rendered source text. Quotes were kept short (≤140 chars). The Assayer should
  spot-check them against the live URL, particularly the longer fragments (Claim 1,
  6, 7, 11, 12, 15, 17) and the Concrete Artifacts excerpts, which are verbatim.
- Three claims (8, 9, 14, 18, 19) are marked "no direct quote" because the source
  states the mechanism in prose rather than a single quotable sentence; the meaning
  is captured in `Our assessment` instead of fabricating a quote. Claim 20's
  rationale is quoted verbatim in the Concrete Artifacts "Key Takeaways" excerpt,
  so no inline quote is needed.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025, LangChain
  Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023, Google A2A
  protocol). These were not independently fetched — cited here as they appear in the
  source.
- The source is rich in architectural detail but light on quantitative metrics — no
  latency distributions, accuracy/eval numbers, or cost data. The one concrete
  number is "10+ minutes" for sequential diagnosis of a moderately complex incident
  (Claim 4).
- No part was paywalled; publicly accessible on the PagerDuty Engineering Blog.
  Published June 24, 2026 — about three weeks before extraction. The architecture
  described is very recent and may still be evolving (notably the LangGraph
  async-subagents feature the authors address in Claim 15).
- EVAL CONTEXT: This note is a Hy3-model replay of the golden issue #1, written to
  compare against the merged DeepSeek baseline `blog-pagerduty-sre-agent-
  architecture.md`. It does not edit that baseline or any other file under
  `source-notes/` except its own `-hy3-eval.md` file. It does not modify issue #1.
