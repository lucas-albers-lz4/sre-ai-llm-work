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

> A detailed practitioner post-mortem from PagerDuty Engineering tracing the
> architectural evolution of their SRE Agent from a single-agent monolith to a
> reactive multi-agent system. Documents specific failure modes (context rot,
> instruction overload), three execution model trade-offs, a custom reactive
> loop built on LangGraph interrupt/resume primitives, and the counterintuitive
> simplification from distributed to single-process architecture. Published
> June 2026 — 28-minute read with significant architectural depth.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three senior/staff/principal engineers at PagerDuty
  who built the system they describe. Viktor Vasylkovskyi (Senior SWE), Micah
  Mayo (Staff SWE, co-led SRE Agent from concept to GA), Ralph Bird (Principal
  ML Engineer focused on AI agents and LLM observability). This is first-hand
  production experience, not a thought-piece.
- **Scope**: Covers the full architectural journey — why a single agent failed,
  three execution models with trade-offs, the custom reactive loop built from
  first principles, and the simplification from distributed to single-process.
  Also covers identity conventions, event transport, the "build hard, ship
  simple" methodology, and comparison with framework-native async sub-agent
  support. Does NOT cover: evaluation/accuracy metrics, cost data, specific
  model choices, failure recovery from model hallucinations, or the companion
  article's productionization framework (Freitas, 2026).

## Extracted Claims

### Claim 1: AI-native products where AI is the system itself have fundamentally different failure modes than AI-assisted products where AI is a feature layer
- **Evidence**: The authors frame the entire article around this distinction,
  citing João Freitas's companion PagerDuty post. The distinction determines
  reliability requirements, engineering trade-offs, and failure modes throughout
  the architectural discussion.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of
  an existing system. In AI-native products, the AI is the system."
- **Our assessment**: This is a foundational framing that the authors
  demonstrate concretely throughout the article. The claim that failure modes
  differ materially is supported by specific examples (context rot, instruction
  overload) that are unique to AI-native architectures.

### Claim 2: Context rot creates a hard ceiling on single-agent incident investigation — beyond a certain threshold, more context degrades model performance
- **Evidence**: The Incident Context document grew to include JSON blobs of
  alerts, past incidents, change events, runbook content, service topology,
  dependency graphs, historical patterns, and remediation options. The authors
  cite Liu et al. (2023) "Lost in the Middle" research showing model performance
  degrades beyond certain context thresholds. Newer models are improving but
  cost and latency impacts remain.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows, not because the information isn't there but because the model
  struggles to weight it correctly."
- **Our assessment**: Well-established in the literature and widely observed.
  The authors' specific contribution is showing how this manifests in incident
  investigation, where context documents grow large and heterogeneous quickly.

### Claim 3: Instruction overload — an inverse relationship between instruction volume and output quality — imposes a hidden tax on monolithic agent feature accumulation
- **Evidence**: Every new feature meant more instructions, new tools, new
  guardrails, expanded system prompts. The authors cite Jaroslawicz et al.
  (2025) finding that as prompts get longer, the model's ability to follow any
  given instruction decreases. Agents that performed well at a certain feature
  set degraded as features accumulated because new capabilities competed with
  existing ones for model attention.
- **Confidence**: emerging
- **Quote**: "in a monolithic agent, adding a new capability competes with every
  existing capability for the model's attention"
- **Our assessment**: The research backing is cited and the production
  observation is specific. This has significant implications for teams building
  long-lived agent systems — feature work carries a hidden quality tax on
  existing capabilities. The mechanism (attention competition) is plausible.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency — one hypothesis at a time
- **Evidence**: A single root cause analysis chain — formulate hypothesis,
  search for evidence, evaluate — took several minutes. A moderately complex
  incident with 3-4 candidate causes could take 10+ minutes to diagnose. Each
  step involves LLM inference plus external API calls (log search, metrics
  query).
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible given the described architecture. The key insight
  is that this is an architectural problem (sequential execution of
  parallelizable work), not a model speed problem. This latency is unacceptable
  for live incident response where minutes matter.

### Claim 5: Lack of mid-run interactivity meant the agent operated without information the human already had — a structural consequence of synchronous single-agent execution, not a missing feature
- **Evidence**: Users could not ask questions or add context while the agent was
  working. If the on-call engineer knew about a recent deployment, they had to
  wait for the agent to finish, then restart with that context. This was not a
  bug — it was inherent to the synchronous single-agent execution model.
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: The most operationally significant failure mode. For live
  incidents, an agent that can't accept mid-run input wastes the on-call's
  existing knowledge. This directly supports keeping humans in the loop during
  AI-assisted incident response — the agent should augment, not replace, the
  human's judgment.

### Claim 6: Three execution models exist for multi-agent investigation — sequential, parallel-wait-for-all, and parallel-fan-out-concurrent-fan-in — with only the third meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three with timeline
  diagrams. Sequential: total time is sum of sub-agent durations. Parallel-wait:
  total time equals slowest sub-agent but main agent is idle and can't report
  progress. Concurrent fan-in: dispatch all asynchronously, process each result
  as it arrives, treat user input as a first-class event alongside sub-agent
  results. The authors chose concurrent fan-in for the SRE Agent.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: The taxonomy is clearly reasoned and each model's
  trade-offs are well articulated. The contribution is mapping these abstract
  execution models to concrete SRE investigation requirements. The concurrent
  fan-in model directly addresses all three failure modes identified in Claims
  2-5.

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and blocks mid-run user input because control only returns after every tool in a batch resolves
- **Evidence**: The authors tried LangChain Deep Agents with sub-agents as
  tools. In LangGraph's BSP model, a parallel tool call is one superstep —
  control returns only after every tool in the batch resolves. The orchestrator
  cannot react to sub-agent 1's result at t=3min while sub-agents 2 and 3 still
  run. No external event — including user input — can reach the graph while
  blocked inside a parallel tool call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "A parallel tool call is one superstep, so control only returns to
  the orchestrator once every tool in that batch has resolved."
- **Our assessment**: This is a specific technical claim about LangGraph's
  execution model that matches its documented BSP superstep design. The
  implication that framework-managed parallelism is incompatible with real-time
  interactivity is a significant constraint. LangGraph has since added async
  sub-agent support, but the authors argue this still doesn't fully address
  their requirements (see Claim 15).

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph — a queue is required to buffer arrivals and serialize processing
- **Evidence**: When two sub-agents finished close together, the first
  completion resumed the graph and triggered the main agent's working loop.
  While processing, the second completion arrived and tried to resume the same
  graph. LangGraph either errored or started a fresh execution from scratch,
  losing state from the first arrival. The fix was a local queue — incoming
  results went into the queue and the main agent drained it one at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph execution model. The queue is the obvious
  fix but the fact that the naive approach fails under realistic timing (two
  sub-agents finishing within seconds) is a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, a window remained between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and call `Command(resume=...)` before the graph was genuinely
  paused — same race, different shape. The fix: the drain loop held a lock while
  resuming, and the graph signaled through a callback when it had actually
  re-interrupted, releasing the lock. This guaranteed the graph was never
  resumed twice in flight.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the kind of concurrency edge case easy to miss
  until it hits in production. The lock pattern is standard but the specific
  interaction with LangGraph's interrupt/resume lifecycle is a useful concrete
  example. The authors' willingness to document this level of detail adds
  credibility.

### Claim 10: A priority queue where user input is priority 0 and sub-agent results are priority 1 enables mid-run steering by ensuring user events jump the line
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the user's
  message went in fourth — by the time the drain loop reached it, the graph
  might have already finished. The fix: a two-level priority queue where user
  input is priority 0 and sub-agent results are priority 1. A `route_event`
  node branches: sub-agent results go to `handle_sub_agent_result`, user
  messages go to `handle_user_input` which adds new work to state and re-enters
  `plan` for immediate dispatch.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean pattern with a compelling justification. Without
  prioritization, user input can arrive too late to matter. The `route_event`
  branching design is a concrete LangGraph pattern worth noting.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic — the single most important convention in the architecture
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries a
  `parent_task_id` pointing to whoever spawned it. By making the LangGraph
  `thread_id` identical to the agent's `task_id`, when a sub-agent publishes a
  completion event carrying `parent_task_id: task-001`, the parent agent
  immediately knows which LangGraph thread to resume. No lookup table, no
  correlation logic. The authors call this "the single most important
  convention."
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: An elegant convention that eliminates an entire class of
  infrastructure. Only becomes obvious after building the complex version. Worth
  adopting as a pattern for any multi-agent system on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed
  (separate processes, broker, durable store), then questioned the assumption.
  Usual justifications for service boundaries — CPU isolation and organizational
  ownership — don't apply here: investigation is overwhelmingly IO (call log API
  and wait, call metrics API and wait, hand text to model and wait), and a
  single team owns the whole sub-agent system. Spreading IO-bound agents across
  services buys deployment, service discovery, network failure modes, and
  distributed tracing without buying the thing services are for.
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive and valuable insight.
  The reflex to treat multi-agent systems as distributed systems is strong, and
  the authors make a clear, specific argument for why it's wrong for this
  workload class. The key qualifier is "IO-bound" — this does not generalize to
  compute-bound workloads. But for the common SRE investigation case, it is a
  powerful simplification.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — its state is checkpointed for
  pause/resume/recovery. Sub-agents are stateless with no checkpoints — if one
  dies, they re-spawn it rather than resume mid-flight. Making every agent
  durable would require keeping N+1 checkpoints consistent and reconciling them
  on every restart. By concentrating durability in the supervisor and treating
  sub-agents as cheap and replaceable, there is exactly one source of truth.
  Each processing step is atomic and persisted before the next event is touched,
  so the checkpoint never captures in-flight mailbox contents.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: The asymmetric durability model is a clean design
  principle. It reduces the recovery problem from a distributed consensus
  problem to a single-writer checkpoint. The trade-off of re-running sub-agent
  work on failure is acceptable when sub-agents are IO-bound and have no side
  effects beyond their result. The atomic-step-per-event model is a strong
  guarantee that simplifies reasoning about crash recovery.

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The earlier distributed design required webhook callbacks,
  PubSub broadcast, and a durable event store to move results across a network.
  Once everything shares a process, the answer is an in-process mailbox — an
  `asyncio.Queue` injected into each background task when spawned. The sub-agent
  writes its result to the queue; the supervisor reads from it. No broker, no
  callback endpoint, no network hop. This is enabled by the co-location decision
  in Claim 12.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The natural consequence of the single-process decision and
  a dramatic simplification. Multiple concurrent investigation runs can still
  land on different pods, but within one run all sub-agents are co-located with
  their spawning supervisor.

### Claim 15: Framework-native async sub-agent polling leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after
  their initial experiments) which let the supervisor launch background tasks
  and return immediately. But the polling model means no push notification when
  a sub-agent finishes, so no deterministic synthesis the moment each result
  arrives. More importantly, native support stops short of true mid-run steering
  and gradual emission of artifacts as each hypothesis resolves. Since those
  require the same primitives (identity, transport, reactive loop with priority
  queue), the native layer wasn't buying them much.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: An important qualification — framework evolution doesn't
  automatically solve the hard problems. Polling vs. push is the smaller gap;
  the bigger gap is mid-run steering and progressive result emission, which
  frameworks don't address. Direct implications for teams choosing between
  custom loops and waiting for framework support.

### Claim 16: The "build the hard version to understand, ship the simple one" methodology was deliberate — the complex distributed prototype was necessary to identify which primitives were essential
- **Evidence**: The authors explicitly frame the complex version (webhooks,
  PubSub, durable event store, the full primitive set) as a deliberate step,
  not a mistake. It let them identify which parts were essential and which were
  accidents of assuming a distributed architecture. The simplification to a
  single process with in-process primitives was only possible because they
  first understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: This is engineering philosophy, not a falsifiable claim.
  It is convincingly demonstrated in the article but carries a risk that teams
  might use it to justify over-engineering that never gets simplified. The
  authors avoid this trap by actually shipping the simple version, which is the
  part most worth emulating.

### Claim 17: Three insights — identity, event transport, and reactive loop — form a portable foundation for multi-agent architectures regardless of runtime engine
- **Evidence**: The authors identify three primitives that survive the
  simplification from distributed to single-process and would apply to any
  runtime engine: (1) Identity (`task_id === thread_id`) routes events without
  lookup tables; (2) Event transport delivers results reliably and survives
  restarts; (3) Reactive loop processes results as they arrive, serializes
  concurrent completions, and treats user input as a first-class event.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as frameworks evolve."
- **Our assessment**: A useful distillation into three primitives (identity →
  transport → control loop) that could guide design even outside LangGraph.
  The portability claim is plausible but untested — the authors only implemented
  on LangGraph.

## Concrete Artifacts

### Reactive loop node structure

The supervisor's LangGraph reactive loop consists of six nodes:

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

- `accept_event`: Graph spends most of its life here, paused, waiting for the
  drain loop to deliver the next event from the priority queue.
- `route_event`: Inspects event type and branches.
- `handle_sub_agent_result`: Processes a sub-agent's findings.
- `handle_user_input`: Adds new work to state, marks as pending spawn, re-enters
  `plan` so the new sub-agent gets dispatched immediately.
- `plan`: Formulates investigation strategy based on current state.
- `spawn_sub_agents`: Dispatches new sub-agent background tasks.

### Identity hierarchy

```
Main Agent (task_id: task-001, thread_id: task-001)
    ├── Sub-Agent 1 (task_id: sub-1, parent_task_id: task-001)
    │     └→ completes → publishes event with parent_task_id: task-001
    │                  → parent resumes thread_id: task-001
    ├── Sub-Agent 2 (task_id: sub-2, parent_task_id: task-001)
    └── Sub-Agent 3 (task_id: sub-3, parent_task_id: task-001)
```

### Agent lifecycle (A2A-protocol-inspired)

Each agent wraps its logic in: `working → completed | failed | canceled`

### Priority queue levels

```
Priority 0 (highest): User input — processed first, jumps the line
Priority 1:          Sub-agent results — processed in arrival order after user input
```

### Single-process architecture properties

- Supervisor and all sub-agents share one process
- Mailbox: ordinary `asyncio.Queue` (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Multiple concurrent investigation runs can land on different pods/processes
- Within one run, all sub-agents are co-located with their spawning supervisor

## Cross-References

- **Corroborates**:
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    (baseline DeepSeek/Flash note for the same URL, Claim 1): Corroborates
    Claim 1 (AI-native vs AI-assisted distinction) — both notes extract this
    as the foundational framing.
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    (Claim 2): Corroborates Claim 2 (context rot) — same failure mode, same
    Liu et al. 2023 citation.
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    (Claim 3): Corroborates Claim 3 (instruction overload) — same Jaroslawicz
    et al. 2025 citation and production observation.
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    (Claim 4): Corroborates Claim 4 (sequential synchronous latency and the
    10+ minute diagnosis figure).
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    (Claims 6-10): Corroborates Claims 6-10 (three execution models, BSP
    limitation, queue+lock, priority queue, task_id=thread_id) — each claim
    matches the baseline extraction.
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    (Claims 12-17): Corroborates Claims 12-17 (single-process simplification,
    asymmetric durability, transport collapse, framework gap, build-hard-ship-
    simple methodology, three portable primitives).
  - [blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)
    (Claim 3): Corroborates Claim 2 (context rot/fatigue) — the companion
    article describes the same failure mode under the name "context fatigue"
    and likewise cites the "Lost in the Middle" phenomenon.
  - [blog-incidentio-ai-sre-incident-run.md](blog-incidentio-ai-sre-incident-run.md)
    (Claim 3): Corroborates the requirement for parallel human-agent
    investigation — incident.io's design allows human and agent to investigate
    independently with automatic context sync, which is the inverse of the
    PagerDuty article's finding that single-agent architectures lack
    interactivity.
  - [docs-google-sre-prodcast-04-09-ai-agents.md](docs-google-sre-prodcast-04-09-ai-agents.md)
    (Claim 2, read/write capability split): Corroborates the architectural
    principle that agent capabilities must be classified by safety impact —
    the PagerDuty article's durable supervisor / stateless sub-agents design
    mirrors the read/write split.
  - [docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md](docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md)
    (Claim 5, investigation vs mitigation autonomy boundary): Corroborates
    the architectural separation of concerns — Zelesko argues investigation is
    AI-safe while mitigation needs human-in-the-loop, consistent with the
    PagerDuty article's design that keeps sub-agents read-only (log/metric
    queries) while the supervisor manages synthesis.

- **Contradicts**: None identified.

- **Extends**:
  - [blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)
    (baseline): This eval note is not an extension — it is an alternative
    extraction of the same source for comparison purposes. The claims align
    closely with the baseline, differing primarily in phrasing, ordering, and
    quote selection.
  - [blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md):
    The source article cites Freitas (2026) as foundational framing. This note
    extends that companion article by providing the implementation-level
    architecture details (reactive loop, identity, transport, durability model)
    that the companion article explicitly says it does not cover.
  - [docs-google-sre-prodcast-04-09-ai-agents.md](docs-google-sre-prodcast-04-09-ai-agents.md):
    That note covers Google's agent-building practices at the evaluation and
    safety-boundary level. This note provides a concrete multi-agent
    architecture implementation that realizes the principles described there.

- **Novel**: Same source as the baseline note — no content is new to the corpus
  from this extraction. The novelty evaluation is for the Assayer to assess the
  extraction quality difference between this note and the baseline.

## Guide Impact

- **Chapter 00 (Principles)**: Supports a principle of "design for AI-native
  failure modes" and "build to understand, ship simple" as an engineering
  methodology for agent systems.

- **Chapter 01 (Incident Response)**: Provides concrete architecture
  requirements for AI-assisted incident investigation: real-time visibility,
  mid-run human steering, parallel hypothesis testing, and the principle that
  the agent should never operate without information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Provides specific patterns for
  multi-agent ops architecture — three execution models with trade-offs,
  reactive loop (interrupt/resume + priority queue + lock), identity convention,
  asymmetric durability, single-process simplification for IO-bound workloads.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate
  hypotheses → spawn sub-agents → query logs/metrics → report findings →
  synthesize root cause) is directly reusable for on-call tooling design.

## Extraction Notes

- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. The article is self-contained with all architectural detail
  inline. No sub-pages were followed.
- All quotes were captured from the rendered page via WebFetch and verified as
  verbatim. Longer architectural descriptions that the source provided as
  narrative rather than quotable claims are summarized in Our assessment rather
  than quoted.
- The source cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol). These were not independently fetched.
- The article is rich in architectural detail but light on quantitative metrics
  (no latency distributions, accuracy/eval numbers, or cost data). The one
  concrete number is "10+ minutes" for sequential diagnosis.
- This is an eval extraction produced by the `opencode/deepseek-v4-flash-free`
  model via OpenCode Zen free chat-completions. It is intended for comparison
  against the merged DeepSeek/Flash baseline
  (`blog-pagerduty-sre-agent-architecture.md`). The Assayer should evaluate
  claim accuracy, quote fidelity, and cross-reference thoroughness relative to
  the baseline.
- Published June 24, 2026. The source URL is publicly accessible.
