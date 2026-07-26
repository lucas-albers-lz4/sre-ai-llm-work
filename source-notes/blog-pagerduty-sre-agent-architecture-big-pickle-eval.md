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
issue: "#1-big-pickle-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> PagerDuty Engineering describes the architectural evolution of their SRE
> Agent from a single-agent monolith to a reactive multi-agent system built on
> LangGraph. Covers the specific failure modes of single-agent incident
> investigation (context rot, instruction overload, sequential latency, no
> interactivity), the three execution models evaluated, the custom reactive
> loop built from first principles (interrupt/resume, priority queue, lock
> serialization), the counterintuitive simplification from distributed to
> single-process architecture for IO-bound agent workloads, and the durable
> supervisor / stateless sub-agent asymmetry. Published June 2026.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three senior/staff/principal engineers at PagerDuty —
  Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent
  from concept to GA), Ralph Bird (Principal ML Engineer, focused on AI agents
  and LLM observability). All three authors built the system described. This is
  first-hand production experience, not a thought-piece.
- **Scope**: Covers the full architectural journey — why a single agent failed,
  the three execution models, the custom reactive loop built from first
  principles, and the simplification from distributed machinery to a single
  process with in-process primitives. Also covers identity conventions, event
  transport, and the "build hard, ship simple" methodology. Does NOT cover:
  evaluation/accuracy metrics, cost data, model choices, or failure recovery
  from model hallucinations.

## Extracted Claims

### Claim 1: The distinction between AI-native and AI-assisted products determines failure modes and engineering trade-offs
- **Evidence**: The authors draw this as the foundational framing for the
  entire architecture discussion, citing João Freitas's earlier PagerDuty post.
  The entire article is structured as a case study in what this distinction
  means in practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of
  an existing system. In AI-native products, the AI is the system."
- **Our assessment**: A useful framing backed by concrete examples throughout
  the article. The claim that failure modes differ materially between the two
  categories is demonstrated, not just asserted. The distinction has practical
  consequences for architecture decisions.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document grew to include JSON blobs of
  alerts, past incidents, change events, runbook content, service topology,
  dependency graphs, historical patterns, and remediation options. The authors
  cite Liu et al. (2023) "Lost in the Middle" research showing performance
  degradation beyond certain context thresholds. Newer models are improving but
  cost and latency impacts remain.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows."
- **Our assessment**: Well-established in the literature and widely observed in
  practice. The specific contribution here is showing how it manifests in the
  SRE incident investigation domain, where context documents grow large and
  diverse very quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails,
  and system prompts. The authors cite Jaroslawicz et al. (2025) finding an
  inverse relationship between instruction volume and output quality. Agents
  that performed well at a certain feature set degraded as features accumulated.
- **Confidence**: emerging
- **Quote**: "an inverse relationship between instruction volume and output
  quality"
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research
  backing, but the specific claim about agent degradation as features accumulate
  is the authors' production observation. This is a significant concern for any
  team building long-lived agent systems — feature work carries a hidden tax on
  existing capabilities.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis,
  search for evidence, evaluate — took several minutes. A moderately complex
  incident with 3-4 candidate causes could take 10+ minutes to diagnose. This
  is a direct production measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible. The latency is plausible given that each step
  involves LLM inference plus external API calls. The key insight is that this
  is not a model speed problem — it's an architectural problem (sequential
  execution of parallelizable work).

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the
  agent to finish, then restart with that context. The authors characterize this
  as the agent "operating without information the human already had."
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most important failure mode they identify for
  live incident response. An agent that can't accept mid-run input from the
  on-call engineer wastes time and ignores the human's existing knowledge. This
  directly supports the guide's editorial principle of keeping humans on the
  paging path.

### Claim 6: Three execution models exist for multi-agent investigation, with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three: Sequential (total
  time = sum of all durations; slow hypothesis blocks everything), Parallel
  wait-for-all (total time = slowest; main agent idle, can't react to early
  results), and Parallel fan-out/concurrent fan-in (main agent never idle, user
  always has visibility, new work injected at any point).
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: This taxonomy is clearly reasoned and each model's
  trade-offs are well articulated. The contribution is not inventing these
  models but clearly mapping them to the SRE investigation domain with concrete
  requirements (real-time visibility, mid-run injection, cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: In LangGraph's BSP model, a parallel tool call is one
  superstep — control returns only after every tool in that batch resolves. The
  orchestrator cannot react to sub-agent 1's result while sub-agents 2 and 3
  still run. No external event — including user input — can reach the graph
  while blocked inside a parallel tool call.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: A specific technical claim about LangGraph's execution
  model that matches the documented BSP/superstep design. The implication —
  that framework-managed parallelism is incompatible with real-time
  interactivity — is a significant constraint for anyone building interactive
  agent systems on LangGraph.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph
- **Evidence**: When two sub-agents finished close together, the first
  completion resumed the graph and triggered the main agent's working loop.
  While processing, the second completion arrived and tried to resume the same
  graph. "LangGraph either errored or started a fresh execution from scratch,"
  losing state from the first arrival.
- **Confidence**: emerging
- **Quote**: "LangGraph either errored or started a fresh execution from
  scratch"
- **Our assessment**: A practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph execution model. The queue is the
  obvious fix, but the fact that the naive approach fails under realistic timing
  is a valuable warning for anyone building similar systems.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there remained a window between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and call resume before the graph was genuinely paused. The fix: the
  drain loop held a lock while resuming, and the graph signaled through a
  callback when it had actually re-interrupted, releasing the lock.
- **Confidence**: emerging
- **Quote**: "Concurrent arrivals were serialized. The graph was never resumed
  twice in flight."
- **Our assessment**: This is the kind of concurrency edge case that's easy to
  miss until it hits in production. The lock pattern is standard but the
  specific interaction with LangGraph's interrupt/resume lifecycle is a useful
  concrete example. The callback-on-re-interrupt mechanism is a specific
  implementation detail worth noting.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the user's
  message would go in fourth — by the time the drain loop reached it, the graph
  might have already finished. The fix: a two-level priority queue where user
  input is priority 0 (highest) and sub-agent results are priority 1.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean, well-explained pattern. The priority queue is a
  simple primitive but the authors make a compelling case for why it's essential
  — without it, user input can arrive too late to matter.

### Claim 11: The identity convention task_id === thread_id eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID task_id. Every sub-agent carries a
  parent_task_id pointing to whoever spawned it. By making the LangGraph
  thread_id identical to the agent's task_id, when a sub-agent publishes a
  completion event carrying parent_task_id: task-001, the parent agent
  immediately knows which LangGraph thread to resume — no lookup table, no
  correlation logic.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: An elegant convention that eliminates an entire class of
  infrastructure. It's the kind of simple design decision that only becomes
  obvious after building the complex version. Worth adopting as a pattern for
  any multi-agent system built on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries
- **Evidence**: The usual justifications for service boundaries — CPU isolation
  and organizational ownership — don't apply: investigation is overwhelmingly
  IO (call log API and wait, call metrics API and wait, hand text to model and
  wait), and a single team owns the whole sub-agent system.
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive and valuable insight.
  The reflex to treat a multi-agent system as a distributed system is strong,
  and the authors make a clear, specific argument for why it's wrong for this
  workload class. The key qualifier is "IO-bound" — this doesn't generalize to
  compute-bound agent workloads.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — checkpointed so it can pause, resume,
  and recover. Sub-agents are stateless — no checkpoints. If a sub-agent dies,
  they re-spawn it rather than resume it mid-flight. Making every agent durable
  would mean keeping N+1 checkpoints consistent and reconciling them on every
  restart.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: An asymmetric durability model that reduces the recovery
  problem from a distributed consensus problem to a single-writer checkpoint.
  The trade-off — re-running sub-agent work on failure — is acceptable when
  sub-agents are cheap (IO-bound, no side effects beyond their result).

### Claim 14: Each processing step is atomic and checkpointed before the next event is touched, so the checkpoint never captures in-flight mailbox contents
- **Evidence**: The supervisor drains the mailbox one event at a time: it pulls
  an event, runs the execution forwards to the next interrupt, and that single
  step is checkpointed before it touches the next event. On restart, the
  supervisor reloads its last checkpoint with an empty queue; any sub-agents
  that were still running are simply re-spawned.
- **Confidence**: emerging
- **Quote**: "each step is atomic and persisted the moment it's applied, the
  checkpoint never has to capture in-flight mailbox contents"
- **Our assessment**: This is the critical invariant that makes the
  in-process mailbox safe despite being non-durable. It guarantees the
  checkpoint is always consistent (never mid-mailbox-processing) and that
  restart is simple (reload checkpoint, re-spawn running sub-agents, fresh
  mailbox). This is a more precise statement than "just checkpoint the
  supervisor" — the atomic-step-per-event model is what makes it work.

### Claim 15: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The earlier distributed design required webhook callbacks,
  PubSub broadcast, and a durable event store — all to move results across a
  network from one process to another. Once everything shares a process, the
  answer is "an in-process mailbox — an asyncio.Queue — injected into each
  background task when it's spawned."
- **Confidence**: emerging
- **Quote**: "No broker to run, no callback endpoint to expose, no network hop
  to fail."
- **Our assessment**: The natural consequence of the single-process decision
  and a dramatic simplification. The authors are explicit that this only works
  because sub-agents are guaranteed to live in the same process as their
  spawning supervisor. The dependency injection pattern (sub-agent handed a
  queue, knows nothing about the reader) maintains the decoupling that the
  original webhook design had.

### Claim 16: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after
  their initial experiments). The polling model means "no push notification when
  a sub-agent finishes, which means no deterministic synthesis the moment each
  result arrives." More importantly, native support "stops short of the two
  things our SRE Agent actually needs: true mid-run steering, and gradual
  emission of artifacts as each hypothesis resolves."
- **Confidence**: emerging
- **Quote**: "stops short of the two things our SRE Agent actually needs: true
  mid-run steering, and gradual emission of artifacts as each hypothesis
  resolves"
- **Our assessment**: An important qualification — framework evolution doesn't
  automatically solve the hard problems. The bigger gap is mid-run steering and
  progressive result emission, which frameworks don't address. This has direct
  implications for anyone choosing between building custom loops and waiting for
  framework support.

### Claim 17: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors explicitly frame the complex version (webhooks,
  PubSub, durable event store, the full primitive set) as "a deliberate step,
  not a mistake." The simplification to a single process was only possible
  because they first understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: Advice, not a falsifiable claim. It's a valuable
  engineering philosophy demonstrated convincingly in their own work, but it's
  one team's methodology. The risk is that teams might use this to justify
  over-engineering that never gets simplified. The authors avoid this trap by
  actually shipping the simple version.

### Claim 18: Three insights — identity, event transport, and reactive loop — remain true regardless of runtime engine, forming a portable foundation for multi-agent architectures
- **Evidence**: The authors identify three primitives that survive the
  simplification from distributed to single-process and would apply to any
  runtime engine: (1) Identity (task_id === thread_id) routes events to the
  right graph; (2) Event transport delivers results reliably, handles
  late-joining clients, and survives restarts; (3) Reactive loop processes
  results as they arrive, serializes concurrent completions, and treats user
  input as a first-class event.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as frameworks evolve."
- **Our assessment**: A useful distillation. The three primitives form a
  reasonable abstraction stack (identity → transport → control loop) that could
  guide design even outside LangGraph. The portability claim is plausible but
  untested — the authors only implemented on LangGraph.

## Concrete Artifacts

### Reactive loop node structure (from the article)

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

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

### Priority queue levels

```
Priority 0 (highest): User input — processed first, jumps the line
Priority 1:          Sub-agent results — processed in arrival order after any pending user input
```

### Single-process architecture (from the article)

- Supervisor and all sub-agents share one process
- Mailbox: ordinary `asyncio.Queue` (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Each processing step is atomic and checkpointed before the next event is touched
- On restart: supervisor reloads last checkpoint with empty queue; sub-agents re-spawned

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (same URL — the merged
    DeepSeek/Flash baseline note for this source). Baseline Claim 2 (context
    rot as hard ceiling) and Claim 3 (instruction overload) match this note's
    Claims 2 and 3. Both cite Liu et al. 2023 and Jaroslawicz et al. 2025
    respectively. The baseline provides the same quotes for these claims.
  - `blog-pagerduty-production-ai-agent-gaps.md` (companion PagerDuty article
    by João Freitas). Its Claim 3 ("context fatigue" causing early prompt
    instructions to lose weight) corroborates this note's Claim 2 (context
    rot). Same failure mode, different name, both cite "Lost in the Middle."
    Its Claim 8 (architecture evolution: single → supervisor → hierarchical)
    corroborates this note's Claim 12 (single-process simplification) and
    Claim 17 (build hard, ship simple).

- **Contradicts**: None identified.

- **Extends**:
  - `blog-incidentio-ai-sre-incident-run.md` describes AI SRE running
    parallel investigation with reverification loops. PagerDuty's reactive
    loop pattern (Claims 6, 9, 10) provides the architectural foundation for
    what incident.io describes from the user's perspective. PagerDuty goes
    deeper on WHY parallel concurrent fan-in is needed; incident.io shows HOW
    it feels in practice.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` describes Google's
    horizontal AI-for-SRE tools team. PagerDuty's claim that IO-bound agent
    workloads don't need service boundaries (Claim 12) directly challenges the
    "horizontal tools team" organizational model — if agents are co-located in
    one process, the service boundary question becomes moot, but the
    organizational question of who owns the single process remains.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` covers the
    human baseline of incident response tooling. PagerDuty's finding that
    mid-run interactivity was a structural failure (Claim 5) corroborates the
    human-centered tooling thesis — agents that can't accept human input mid-run
    are structurally limited for live incidents.
  - `blog-anthropic-building-effective-agents.md` — Anthropic's Claim 11
    (orchestrator-workers pattern: central LLM dynamically breaks down tasks,
    delegates to workers, synthesizes results) maps directly to this note's
    Claim 6 (concurrent fan-in execution model) — PagerDuty's reactive loop is
    a specific production instantiation of that general pattern. Anthropic's
    Claim 1 (most successful agent implementations use simple, composable
    patterns rather than complex frameworks) corroborates this note's Claim 17
    (build hard, ship simple) and Claim 18 (three portable primitives that
    remain true regardless of runtime engine, so you can "extend or replace
    individual pieces as frameworks evolve").

- **Novel**: Several contributions are new to the corpus beyond the merged
  baseline:
  - **BSP superstep limitation** in LangGraph — specific mechanism (parallel
    tool call = one superstep, control returns only after all resolve) explaining
    WHY framework-level orchestration fails for interactive agents.
  - **Queue + lock concurrency pattern** — the specific failure modes (queue
    alone isn't enough, need callback-on-re-interrupt to close the race window)
    and the six-node reactive loop structure.
  - **Distributed → single-process simplification** — the explicit argument
    that IO-bound agent workloads don't earn service boundaries, with the
    specific qualifier that this doesn't generalize to compute-bound workloads.
  - **Atomic checkpointing invariant** — each processing step is checkpointed
    before the next event is touched, guaranteeing the checkpoint never captures
    in-flight mailbox contents. This is the critical safety property that makes
    the in-process non-durable mailbox work.
  - **Durable supervisor / stateless sub-agent asymmetry** — concentrating
    durability in one component to eliminate N+1 checkpoint reconciliation.
  - **Webhooks → asyncio.Queue transport collapse** — the dramatic
    simplification when everything shares a process, with the dependency
    injection pattern preserving decoupling.
  - **LangGraph async sub-agents gap** — specific quote identifying that
    mid-run steering and gradual artifact emission remain unsolved by framework
    native support.

## Guide Impact

- **Chapter 00 (Principles)**: Supports "Design for AI-native failure modes" —
  context rot and instruction overload are structural, not incidental. Also
  supports "build to understand, ship simple" as an engineering principle for
  agent systems.

- **Chapter 01 (Incident Response)**: Provides concrete architecture for
  AI-assisted incident investigation: (a) real-time visibility into agent
  reasoning is a hard requirement for live incidents, not a nice-to-have;
  (b) mid-run human steering must be a first-class event; (c) sequential
  hypothesis testing creates unacceptable latency; (d) the agent should never
  operate without information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Provides patterns for multi-agent ops
  architecture: (a) three execution models and when to use each; (b) the
  reactive loop pattern (interrupt/resume, priority queue, lock serialization);
  (c) the task_id === thread_id identity convention; (d) durable supervisor /
  stateless sub-agent asymmetry; (e) single-process simplification for
  IO-bound workloads; (f) the three portable primitives (identity, transport,
  reactive loop).

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate
  hypotheses → spawn sub-agents → query logs/metrics → report findings →
  synthesize root cause) is a directly reusable pattern for on-call tooling.

## Extraction Notes

- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. No sub-pages were followed — the article is self-contained
  with all architectural detail inline.
- Quotes were extracted from the WebFetch output of the live page. All quotes
  marked as direct were confirmed as verbatim from the fetched content. The
  Assayer should spot-check key quotes against the live URL, particularly
  longer passages.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol). These were not independently fetched — they are cited
  here as they appear in the source.
- The source is rich in architectural detail but light on quantitative metrics
  (no latency distributions, no accuracy/eval numbers, no cost data). The one
  concrete number cited is "10+ minutes" for sequential diagnosis of a
  moderately complex incident.
- The merged DeepSeek/Flash baseline note (`blog-pagerduty-sre-agent-architecture.md`)
  covers the same source URL. This eval note was produced independently and
  cross-references the baseline in Cross-References above. Key differences in
  this eval: (a) includes the atomic checkpointing invariant (Claim 14), which
  the baseline mentions but does not extract as a standalone claim; (b) quotes
  the LangGraph async sub-agents gap more precisely (Claim 16); (c) provides
  a more structured cross-reference section with specific claim-number
  citations to the baseline.
