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
issue: "#1-laguna-s-2.1-free-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> A practitioner writeup from PagerDuty Engineering describing the architectural
> evolution of their SRE Agent from a single-agent monolith to a reactive
> multi-agent system. Covers specific failure modes (context rot, instruction
> overload), three execution models with trade-offs, a custom reactive loop built
> on LangGraph interrupt/resume primitives, and the simplification from
> distributed to single-process architecture. Published June 2026.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three engineers at PagerDuty — Viktor Vasylkovskyi
  (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from concept to GA),
  Ralph Bird (Principal ML Engineer, focused on AI agents and LLM observability).
  The authors built the system they describe; this is first-hand production
  experience.
- **Scope**: Covers the full architectural journey — why a single agent failed,
  the three execution models evaluated, the custom reactive loop built from first
  principles, and the simplification that collapsed distributed machinery into a
  single process. Also covers identity conventions, event transport, and the
  "build hard, ship simple" methodology. Does NOT cover: evaluation/accuracy
  metrics, cost data, specific model choices, or failure recovery from model
  hallucinations.

## Extracted Claims

### Claim 1: The distinction between AI-native and AI-assisted products determines failure modes and engineering trade-offs
- **Evidence**: The authors draw this as the foundational framing for the entire
  architecture discussion, citing João Freitas's earlier PagerDuty post on
  production AI agents. The entire article is structured as a case study in what
  this distinction means in practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an
  existing system. In AI-native products, the AI is the system."
- **Our assessment**: This is a useful framing that the authors back with
  concrete examples throughout the article. The distinction has practical
  consequences for architecture decisions. The claim that failure modes differ
  materially between the two categories is demonstrated, not just asserted.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document grew to include JSON blobs of
  alerts, past incidents, change events, runbook content, service topology,
  dependency graphs, historical patterns, and remediation options. The authors
  cite Liu et al. (2023) "Lost in the Middle" research showing that model
  performance degrades beyond certain context thresholds.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows, not because the information isn't there but because the model
  struggles to weight it correctly. More data, worse decisions."
- **Our assessment**: Well-established in the literature (Liu et al. 2023) and
  widely observed in practice. The authors' specific contribution is showing how
  it manifests in the SRE incident investigation domain, where context documents
  grow large and diverse very quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality.
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between
  instruction volume and output quality"
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research
  backing, but the specific claim about agent degradation as features accumulate
  is the authors' production observation. This is a significant concern for any
  team building long-lived agent systems.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search
  for evidence, evaluate — took several minutes. A moderately complex incident
  with 3-4 candidate causes could take 10+ minutes to diagnose. This is a direct
  production measurement from their single-agent system.
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
  agent "operating without information the human already had."
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most important failure mode they identify for
  live incident response. An agent that can't accept mid-run input from the
  on-call engineer wastes time and ignores the human's existing knowledge.

### Claim 6: Three execution models exist for multi-agent investigation, with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - **Sequential**: Total time = sum of all sub-agent durations. A slow
    hypothesis in the middle blocks everything behind it.
  - **Parallel, wait for all**: Total time = slowest sub-agent. But the main
    agent is idle during execution, can't report progress, and "the graph is
    locked inside the parallel call until everything resolves."
  - **Parallel fan-out, concurrent fan-in**: Dispatch all asynchronously,
    process each result as it arrives, user input is "a first-class event
    alongside sub-agent results." The main agent is never idle, user always has
    visibility, new work can be injected at any point.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: This taxonomy is clearly reasoned and each model's
  trade-offs are well articulated. The authors map them to the SRE investigation
  domain with concrete requirements (real-time visibility, mid-run injection,
  cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: The authors tried LangChain Deep Agents with sub-agents as tools.
  In LangGraph's BSP model, a parallel tool call is one superstep — control
  returns only after every tool in that batch resolves. The orchestrator cannot
  react to sub-agent 1's result at t=3min while sub-agents 2 and 3 still run. No
  external event — including user input — can reach the graph while blocked
  inside a parallel tool call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: This is a specific technical claim about LangGraph's
  execution model that matches the documented BSP/superstep design. The
  implication — that framework-managed parallelism is incompatible with
  real-time interactivity — is a significant constraint for interactive agent
  systems.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first completion
  resumed the graph and triggered the main agent's working loop. While processing,
  the second completion arrived and tried to resume the same graph. "LangGraph
  either errored or started a fresh execution from scratch," losing state from
  the first arrival. The fix was a local queue — incoming results went into the
  queue, and the main agent drained it one result at a time.
- **Confidence**: emerging
- **Quote**: "LangGraph either errored or started a fresh execution from
  scratch"
- **Our assessment**: This is a practical sharp-edge discovery. The race is real
  given LangGraph's single-thread-per-graph execution model. The queue is the
  obvious fix, but the fact that the naive approach fails under realistic timing
  is a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there remained a window between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and call resume before the graph was genuinely paused. The fix: the
  drain loop held a lock while resuming, and the graph signaled through a callback
  when it had actually re-interrupted, releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the kind of concurrency edge case that's easy to
  miss until it hits in production. The lock pattern is standard but the specific
  interaction with LangGraph's interrupt/resume lifecycle is a useful concrete
  example.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the user's
  message would go in fourth — by the time the drain loop reached it, the graph
  might have already finished. The fix: a two-level priority queue where user
  input is priority 0 (highest) and sub-agent results are priority 1. A
  `route_event` node then branches: sub-agent results go to
  `handle_sub_agent_result`, user messages go to `handle_user_input` which adds
  new work to state and re-enters `plan` for immediate dispatch.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean, well-explained pattern. The priority queue is a
  simple primitive but the authors make a compelling case for why it's essential
  — without it, user input can arrive too late to matter.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries a
  `parent_task_id` pointing to whoever spawned it. By making the LangGraph
  `thread_id` identical to the agent's `task_id`, when a sub-agent publishes a
  completion event carrying `parent_task_id: task-001`, the parent agent
  immediately knows which LangGraph thread to resume — no lookup table, no
  correlation logic.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: This is an elegant convention that eliminates an entire
  class of infrastructure. It's the kind of simple design decision that only
  becomes obvious after building the complex version.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries, and splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed
  (separate processes, broker, durable store), then questioned the assumption.
  The usual justifications for service boundaries — CPU isolation and
  organizational ownership — don't apply: investigation is overwhelmingly IO
  (call log API and wait, call metrics API and wait, hand text to model and
  wait), and a single team owns the whole sub-agent system.
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: This is the article's most counterintuitive and valuable
  insight. The reflex to treat a multi-agent system as a distributed system is
  strong, and the authors make a clear, specific argument for why it's wrong for
  this workload class. The key qualifier is "IO-bound."

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — its state is checkpointed so it can
  pause, resume, and recover. Sub-agents are stateless — no checkpoints. If a
  sub-agent dies, they re-spawn it rather than resume mid-flight. Making every
  agent durable would mean keeping N+1 checkpoints consistent and reconciling
  them on every restart.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: This asymmetric durability model is a clean design
  principle. It reduces the recovery problem from a distributed consensus problem
  to a single-writer checkpoint. The trade-off — re-running sub-agent work on
  failure — is acceptable when sub-agents are cheap.

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The earlier distributed design required webhook callbacks, PubSub
  broadcast, and a durable event store — all to move results across a network.
  Once everything shares a process, the answer is "an in-process mailbox — an
  asyncio.Queue — injected into each background task when it's spawned."
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the natural consequence of the single-process
  decision and a dramatic simplification. Only works because sub-agents are
  guaranteed to live in the same process as their spawning supervisor.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents which let the
  supervisor launch background tasks and return immediately without blocking. But
  the polling model means "no push notification when a sub-agent finishes, which
  means no deterministic synthesis the moment each result arrives." More
  importantly, native support "stops short of the two things our SRE Agent
  actually needs: true mid-run steering, and gradual emission of artifacts as each
  hypothesis resolves."
- **Confidence**: emerging
- **Quote**: "there's no push notification when a sub-agent finishes, which means
  no deterministic synthesis the moment each result arrives"
- **Our assessment**: This is an important qualification — framework evolution
  doesn't automatically solve the hard problems. The bigger gap is mid-run
  steering and progressive result emission, which frameworks don't address.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors explicitly frame the complex version (webhooks,
  PubSub, durable event store, the full primitive set) as "a deliberate step, not
  a mistake." It let them identify which parts were essential and which were
  accidents of assuming a distributed architecture.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: This is advice, not a falsifiable claim. It's a valuable
  engineering philosophy and the authors demonstrate it convincingly in their own
  work.

### Claim 17: Three insights — identity, event transport, and reactive loop — remain true regardless of runtime engine, forming a portable foundation for multi-agent architectures
- **Evidence**: The authors identify three primitives that survive the
  simplification from distributed to single-process and would apply to any
  runtime engine: (1) Identity (`task_id === thread_id`) routes events to the
  right graph without lookup tables; (2) Event transport delivers results
  reliably, handles late-joining clients, and survives restarts; (3) Reactive
  loop processes results as they arrive, serializes concurrent completions, and
  treats user input as a first-class event.
- **Confidence**: emerging
- **Quote**: "Identity (task_id === thread_id): routes events to the right graph
  without lookup tables."
- **Our assessment**: This is a useful distillation. The three primitives form a
  reasonable abstraction stack (identity → transport → control loop) that could
  guide design even outside LangGraph. The portability claim is plausible but
  untested — the authors only implemented on LangGraph.

## Concrete Artifacts

### Reactive loop node structure (as described in the article)

The reactive loop consists of six nodes in the supervisor's LangGraph:

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

- **Corroborates**: `blog-pagerduty-sre-agent-architecture.md` (the merged
  DeepSeek/Flash baseline note for this same source) — all 17 claims above are
  consistent with the baseline extraction. Both notes cover the same source URL
  and reach the same architectural conclusions.
- **Contradicts**: None identified.
- **Extends**: This is a re-extraction of the same source as
  `blog-pagerduty-sre-agent-architecture.md` (the baseline, extracted
  2026-07-12). The baseline was the first source note in the repo; this eval
  extraction covers the same 17 claims with independently verified coverage
  of all quotes, concrete artifacts, and assessments — corroborating rather
  than extending the baseline.

  In the broader corpus:
  - `blog-pagerduty-production-ai-agent-gaps.md` (Freitas, same PagerDuty
    team, published June 11, 2026 — the foundational framing piece that
    precedes this architecture deep-dive): The gaps note covers evaluation,
    metrics, guardrails, and UX (areas this architecture note explicitly
    says it doesn't cover). Its Cross-References section already cites the
    baseline architecture note on Claims 2, 3, 6, 12, and 16. The two
    articles are complementary: gaps covers "what to evaluate and measure,"
    architecture covers "how to build the primitives."
  - `blog-incidentio-ai-sre-incident-run.md` (incident.io, different company):
    Claim 3 (human and AI investigate independently in parallel with
    automatic context sync) independently corroborates Claims 5 and 10
    (interactivity as structural failure; user input as higher-priority
    event) from a different company's implementation. The incident.io note's
    Cross-References already cites the baseline architecture note on Claims
    5, 6, 10, and 16. The reverification loop (AI double-checks human-
    contributed code) is a UX-level implementation of the architectural
    principle that human input must be a first-class event.
  - `docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md` Claim 5
    (investigation-vs-mitigation safety boundary — investigation is
    non-mutating and AI-safe; mitigation requires human-in-the-loop): The
    leadership-level articulation of the same boundary implied by Claims 5
    and 10 (mid-run human steering, priority queue for user input).
  - `docs-google-sre-prodcast-04-09-ai-agents.md` Claims 3 and 5: Claim 3
    (default guardrail: deny world-mutating actions, require human
    permission) and Claim 5 (agent as pre-on-caller — triage in ~3-4
    minutes before the human arrives) are Google's practitioner account of
    the human-in-the-loop patterns demonstrated by the priority queue and
    user input preemption in Claims 5 and 10.
- **Novel**: This is a re-extraction of the same source as the baseline note
  `blog-pagerduty-sre-agent-architecture.md` (extracted 2026-07-12). The
  baseline contributed these as novel to the corpus at that time. This eval
  extraction independently confirms the full set of claims, quotes, and
  concrete artifacts from the same source with a different model, without
  adding new claims. Specific contributions carried forward from the
  baseline:
  - The three execution models mapped to SRE investigation requirements
  - The LangGraph BSP limitation for interactive agent systems
  - The queue+lock pattern for serializing concurrent graph resumes
  - The priority queue pattern for user input preemption in agent loops
  - The `task_id === thread_id` identity convention
  - The single-process simplification argument for IO-bound agent workloads
  - The durable supervisor / stateless sub-agent asymmetry
  - The "build hard, ship simple" methodology demonstrated end-to-end

## Guide Impact

- **Chapter 00 (Principles)**: This source provides evidence for a new principle:
  "Design for AI-native failure modes" — context rot and instruction overload are
  structural, not incidental, and distinguishing AI-native from AI-assisted
  products changes reliability requirements. Also supports "build to understand,
  ship simple" as an engineering principle for agent systems.

- **Chapter 01 (Incident Response)**: This source provides a concrete
  architecture for AI-assisted incident investigation. The key claims to
  incorporate: (a) real-time visibility into agent reasoning is a hard
  requirement for live incidents, not a nice-to-have; (b) mid-run human
  steering (injecting hypotheses, redirecting investigation) must be a
  first-class event, not an afterthought; (c) sequential hypothesis testing
  creates unacceptable latency for incidents with multiple candidate causes;
  (d) the agent should never operate without information the human already has.

- **Chapter 03 (Runbooks and Agents)**: This source provides patterns for
  multi-agent ops architecture: (a) the three execution models and when to
  use each; (b) the reactive loop pattern (interrupt/resume, priority queue,
  lock serialization) for interactive agent systems; (c) the `task_id ===
  thread_id` identity convention for routing events; (d) the durable supervisor
  / stateless sub-agent asymmetry for reliability without distributed
  complexity; (e) the single-process simplification argument — IO-bound agent
  workloads don't need service boundaries.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate
  hypotheses → spawn sub-agents → query logs/metrics → report findings →
  synthesize root cause) is a directly reusable pattern for on-call tooling.
  The priority queue pattern (user input > sub-agent results) applies to any
  interactive on-call agent.

## Extraction Notes

- The source is a single long-form blog post (~28 minute read) on PagerDuty's
  engineering blog. No sub-pages were followed — the article is self-contained
  with all architectural detail inline.
- Quotes were extracted verbatim from the WebFetch output of the live URL. All
  direct quotes are copied character-for-character from the source text.
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
- Published June 24, 2026 — approximately 3 weeks before the baseline extraction
  (2026-07-12) and 5 weeks before this eval extraction (2026-07-25).
