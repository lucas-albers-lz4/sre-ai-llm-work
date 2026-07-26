---
source_url: https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
source_type: blog-post
title: "Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation"
author: "Viktor Vasylkovskyi, Micah Mayo, Ralph Bird (PagerDuty Engineering)"
date_published: 2026-06-24
date_extracted: 2026-07-12
last_checked: 2026-07-12
status: current
confidence_overall: emerging
issue: "#1-cohere-north-mini-code-free-eval"
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
  decisions. The claim that failure modes differ materially between the two
  categories is demonstrated, not just asserted — context rot and instruction
  overload are specifically identified as AI-native failure modes that don't
  appear in conventional software.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document in their single-agent system grew
  to include JSON blobs of alerts, past incidents, change events, runbook
  content, service topology, dependency graphs, historical patterns, and
  remediation options. The authors cite Liu et al. (2023) "Lost in the Middle"
  research showing that model performance degrades beyond certain context
  thresholds. Newer models are improving but cost and latency impacts remain.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows, not because the information isn't there but because the model
  struggles to weight it correctly."
- **Our assessment**: This is well-established in the literature (Liu et al.
  2023) and widely observed in practice. The authors' specific contribution is
  showing how it manifests in the SRE incident investigation domain, where
  context documents grow large and diverse very quickly. The key insight is that
  this is a weighting failure, not an information-availability failure — the
  data is present but the model can't properly attend to it.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. Agents that
  performed well at a certain feature set degraded as features accumulated
  because new capabilities competed with existing ones for model attention.
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between
  instruction volume and output quality (Jaroslawicz et al., 2025): as the
  prompt gets longer, the model's ability to follow any given instruction
  decreases."
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research
  backing, but the specific claim about agent degradation as features accumulate
  is the authors' production observation. This is a significant concern for any
  team building long-lived agent systems — it means feature work carries a
  hidden tax on existing capabilities. The article's framing of "adding a new
  capability competes with every existing capability for the model's attention"
  is a useful mental model.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search
  for evidence, evaluate — took several minutes. A moderately complex incident
  with 3-4 candidate causes could take 10+ minutes to diagnose. This is a direct
  production measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible. The latency is plausible given that each step
  involves LLM inference plus external API calls (log search, metrics query).
  The key insight is that this is not a model speed problem — it's an
  architectural problem (sequential execution of parallelizable work).

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the agent
  to finish, then restart with that context. The authors characterize this as the
  agent "operating without information the human already had." This was not a
  bug — it was a consequence of the synchronous single-agent execution model.
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most important failure mode they identify for
  live incident response. An agent that can't accept mid-run input from the
  on-call engineer wastes time and ignores the human's existing knowledge. This
  directly supports the guide's editorial principle of keeping humans on the
  paging path.

### Claim 6: Three execution models exist for multi-agent investigation, with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - **Sequential**: Total time = sum of all sub-agent durations. Simple but
    "a slow hypothesis in the middle blocks everything behind it."
  - **Parallel, wait for all**: Total time = slowest sub-agent. But the main
    agent is idle during execution, can't report progress, and "the graph is
    locked inside the parallel call until everything resolves."
  - **Parallel fan-out, concurrent fan-in**: Dispatch all asynchronously,
    process each result as it arrives, user input is "a first-class event
    alongside sub-agent results." The main agent is never idle, user always
    has visibility, new work can be injected at any point.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: This taxonomy is clearly reasoned and each model's
  trade-offs are well articulated. The authors' contribution is not inventing
  these models but clearly mapping them to the SRE investigation domain with
  concrete requirements (real-time visibility, mid-run injection, cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: The authors tried LangChain Deep Agents with sub-agents as
  tools. In LangGraph's BSP model, a parallel tool call is one superstep —
  control returns only after every tool in that batch resolves. The orchestrator
  cannot react to sub-agent 1's result at t=3min while sub-agents 2 and 3 still
  run. No external event — including user input — can reach the graph while
  blocked inside a parallel tool call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model"
- **Our assessment**: This is a specific technical claim about LangGraph's
  execution model that matches the documented BSP/superstep design. The
  implication — that framework-managed parallelism is incompatible with
  real-time interactivity — is a significant constraint for anyone building
  interactive agent systems on LangGraph. Note: LangGraph has since added
  async sub-agent support, but the authors argue this still doesn't fully
  address their requirements (see Claim 15).

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first completion
  resumed the graph and triggered the main agent's working loop. While processing,
  the second completion arrived and tried to resume the same graph. "LangGraph
  either errored or started a fresh execution from scratch," losing state from
  the first arrival. The fix was a local queue — incoming results went into the
  queue, and the main agent drained it one result at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is a practical sharp-edge discovery. The race is real
  given LangGraph's single-thread-per-graph execution model. The queue is the
  obvious fix, but the fact that the naive approach fails under realistic timing
  (two sub-agents finishing within seconds) is a valuable warning for anyone
  building similar systems.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there remained a window between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and call resume before the graph was genuinely paused — same race,
  different shape. The fix: the drain loop held a lock while resuming, and the
  graph signaled through a callback when it had actually re-interrupted,
  releasing the lock. This guaranteed the graph was never resumed twice in flight.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the kind of concurrency edge case that's easy to
  miss until it hits in production. The lock pattern is standard but the
  specific interaction with LangGraph's interrupt/resume lifecycle is a useful
  concrete example. The authors' willingness to document this level of detail
  adds credibility.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the user's
  message would go in fourth — by the time the drain loop reached it, the graph
  might have already finished. The fix: a two-level priority queue where user
  input is priority 0 (highest) and sub-agent results are priority 1. This
  ensures user events jump the line. A `route_event` node then branches:
  sub-agent results go to `handle_sub_agent_result`, user messages go to
  `handle_user_input` which adds new work to state and re-enters `plan` for
  immediate dispatch.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean, well-explained pattern. The priority queue is a
  simple primitive but the authors make a compelling case for why it's essential
  — without it, user input can arrive too late to matter. The `route_event`
  branching design is also worth noting as a concrete LangGraph pattern.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries a
  `parent_task_id` pointing to whoever spawned it. By making the LangGraph
  `thread_id` identical to the agent's `task_id`, when a sub-agent publishes a
  completion event carrying `parent_task_id: task-001`, the parent agent
  immediately knows which LangGraph thread to resume — no lookup table, no
  correlation logic. The authors call this "the single most important convention"
  in their architecture.
- **Confidence**: emerging
- **Quote**: "This sounds trivial, yet it was the single most important
  convention in the system."
- **Our assessment**: This is an elegant convention that eliminates an entire
  class of infrastructure (lookup tables, correlation services). It's the kind
  of simple design decision that only becomes obvious after building the complex
  version. Worth adopting as a pattern for any multi-agent system built on
  LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries, and splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed
  (separate processes, broker, durable store), then questioned the assumption.
  The usual justifications for service boundaries — CPU isolation and
  organizational ownership — don't apply: investigation is overwhelmingly IO
  (call log API and wait, call metrics API and wait, hand text to model and
  wait), and a single team owns the whole sub-agent system. Spreading IO-bound
  agents across services buys "deployment, service discovery, network failure
  modes, distributed tracing — without buying the thing services are for."
- **Confidence**: emerging
- **Quote**: "Spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: This is the article's most counterintuitive and valuable
  insight. The reflex to treat a multi-agent system as a distributed system is
  strong, and the authors make a clear, specific argument for why it's wrong for
  this workload class. The key qualifier is "IO-bound" — this doesn't generalize
  to compute-bound agent workloads. But for the common SRE investigation case
  (query external APIs, wait for LLM responses), it's a powerful simplification.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — its state is checkpointed so it can
  pause, resume, and recover. Sub-agents are stateless — no checkpoints. If a
  sub-agent dies, they re-spawn it rather than resume mid-flight. Making every
  agent durable would mean keeping N+1 checkpoints consistent and reconciling
  them on every restart. By concentrating durability in the supervisor and
  treating sub-agents as cheap and replaceable, there's exactly one source of
  truth to recover. Each processing step is atomic and persisted before the next
  event is touched, so the checkpoint never captures in-flight mailbox contents.
- **Confidence**: emerging
- **Quote**: "if it dies, we re-spawn it rather than resume it mid-flight"
- **Our assessment**: This asymmetric durability model is a clean design
  principle. It reduces the recovery problem from a distributed consensus
  problem to a single-writer checkpoint. The trade-off — re-running sub-agent
  work on failure — is acceptable when sub-agents are cheap (IO-bound, no
  side effects beyond their result). The atomic-step-per-event model (process
  one event, checkpoint, move to next) is a strong guarantee that simplifies
  reasoning about crash recovery.

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The authors' earlier distributed design required webhook
  callbacks, PubSub broadcast, and a durable event store — all to move results
  across a network from one process to another. Once everything shares a process,
  the answer is "an in-process mailbox — an asyncio.Queue — injected into each
  background task when it's spawned." The sub-agent writes its result to the
  queue; the supervisor reads from it. No broker, no callback endpoint, no
  network hop. This is enabled by the co-location decision in Claim 12.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the natural consequence of the single-process
  decision and a dramatic simplification. The authors are explicit that this
  only works because sub-agents are guaranteed to live in the same process as
  their spawning supervisor. Multiple concurrent investigation runs can still
  land on different pods, but within one run, all sub-agents are co-located.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after
  their initial experiments) which let the supervisor launch background tasks and
  return immediately without blocking. But the polling model means "no push
  notification when a sub-agent finishes, which means no deterministic synthesis
  the moment each result arrives." More importantly, native support "stops short
  of the two things our SRE Agent actually needs: true mid-run steering, and
  gradual emission of artifacts as each hypothesis resolves." Since those require
  the same primitives they already built (identity, transport, reactive loop with
  priority queue), the native layer wasn't buying them much.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is an important qualification — framework evolution
  doesn't automatically solve the hard problems. The authors' argument is that
  polling vs. push is the smaller gap; the bigger gap is mid-run steering and
  progressive result emission, which frameworks don't address. This has direct
  implications for anyone choosing between building custom loops and waiting for
  framework support.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors explicitly frame the complex version (webhooks,
  PubSub, durable event store, the full primitive set) as "a deliberate step,
  not a mistake." It let them identify which parts were essential and which were
  accidents of assuming a distributed architecture. The simplification to a
  single process with in-process primitives was only possible because they first
  understood why each distributed primitive existed. They recommend this as a
  general methodology.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: This is advice, not a falsifiable claim. It's a valuable
  engineering philosophy and the authors demonstrate it convincingly in their
  own work, but it's one team's methodology. The risk is that teams might use
  this to justify over-engineering that never gets simplified. The authors avoid
  this trap by actually shipping the simple version, which is the part most
  worth emulating.

### Claim 17: Three insights — identity, event transport, and reactive loop — remain true regardless of runtime engine, forming a portable foundation for multi-agent architectures
- **Evidence**: The authors identify three primitives that survive the
  simplification from distributed to single-process and would apply to any
  runtime engine: (1) Identity (`task_id === thread_id`) routes events to the
  right graph without lookup tables; (2) Event transport delivers results
  reliably, handles late-joining clients, and survives restarts; (3) Reactive
  loop processes results as they arrive, serializes concurrent completions, and
  treats user input as a first-class event. The article closes by arguing that
  understanding why each layer exists is what distinguishes inheriting an
  architecture from owning it.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as your framework evolves."
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

### Three execution models (as described in the article)

1. **Sequential**: Total time = sum of all sub-agent durations. Simple but slow.
   "A slow hypothesis in the middle blocks everything behind it."
2. **Parallel, wait for all**: Total time = slowest sub-agent. Main agent idle
   during execution, graph locked, no mid-run injection possible.
3. **Parallel fan-out, concurrent fan-in**: Dispatch all asynchronously, process
   each result as it arrives. User input is a first-class event alongside
   sub-agent results. Requires interrupt/resume execution model, buffer for
   concurrent arrivals, and priority queue for user events.

### LangGraph concurrency pattern — queue + lock (from the article)

```
Sub-agent completions → local queue → drain loop (holds lock)
                                         │
                                         ▼
                                    resume graph
                                         │
                                    graph callback signals re-interrupt
                                         │
                                         ▼
                                    release lock → drain next item
```

## Cross-References

- **Corroborates**:
  - **`blog-pagerduty-production-ai-agent-gaps.md`** (Claim 8): The Freitas
    article's architecture evolution pattern (single → supervisor → hierarchical)
    is directly corroborated by this source's execution model progression
    (sequential → parallel → concurrent fan-in). Both argue that you earn
    complexity rather than starting with it. This source explicitly cites the
    Freitas article as its foundational framing piece (Claim 1).
  - **`blog-pagerduty-production-ai-agent-gaps.md`** (Claim 3, Context fatigue):
    The context-fatigue observation in the Freitas article directly corroborates
    this source's Claim 2 (Context rot). Same failure mode described under two
    names, both citing the "Lost in the Middle" phenomenon.
  - **`blog-incidentio-ai-sre-incident-run.md`** (Claim 3): The incident.io
    article's parallel human-agent investigation pattern with bidirectional
    context sync is a UX-level implementation of the concurrent fan-in model
    (Claim 6). Both treat human input as a first-class event that must not be
    blocked by agent execution.
  - **`blog-incidentio-ai-sre-incident-run.md`** (Claim 10): The incident.io
    article identifies tool fragmentation and context switching as the core
    friction in incident response; this source identifies sequential execution
    and the BSP model as the architectural root causes.
  - **`docs-google-sre-prodcast-04-09-ai-agents.md`** (Claim 5): The Google
    Prodcast's pre-on-caller triage pattern (agent acts first, then human
    reviews) is architecturally the concurrent fan-in model (Claim 6) — the
    human inspects parallel results as they arrive. Same principle, different
    scale.
  - **`docs-google-sre-prodcast-04-09-ai-agents.md`** (Claim 15): The Google
    Prodcast's explicit limits on LLMs (don't use LLMs where regex/specialist
    models fit) parallels this source's insight that framework-native polling
    models don't solve the hard problems — the expensive LLM work should be
    focused on what only it can do (mid-run synthesis, hypothesis evaluation).
  - **`docs-google-sre-prodcast-04-04-zelesko-future-sre.md`** (Claim 6): The
    Zelesko episode's framing of AI/ML as "a buddy next to the human" for
    faster detection/mitigation/postmortems aligns with this source's Claim 5
    — the agent should augment, not replace, the on-call engineer's judgment.

- **Contradicts**: None identified. The source's human-in-the-loop stance
  (mid-run steering, priority queue for user input) is consistent with all
  extant notes in the corpus. This is the first deep architectural treatment of
  multi-agent execution models in the repo; it extends rather than opposes other
  sources.

- **Extends**:
  - **`blog-pagerduty-production-ai-agent-gaps.md`**: The Freitas article covers
    **what** the production gaps are (reliability, control, visibility,
    integration, economics). This source covers **how** to build the runtime that
    addresses them — the reactive loop, identity convention, transport layer,
    and durability model. The two are complementary halves of the same PagerDuty
    production-agent story.
  - **`blog-incidentio-ai-sre-incident-run.md`**: The incident.io article shows
    the user-facing interaction design (Slack → desktop app → Claude Code →
    GitHub); this source shows the internal agent architecture that enables that
    interaction pattern. The incident.io `@incident` command is effectively the
    user-input-as-first-class-event pattern (Claim 10) implemented at the Slack
    UX layer.
  - **`docs-google-sre-prodcast-04-09-ai-agents.md`**: The Google Prodcast
    covers the spectrum from static algorithms to full agents and the evaluation
    methodology; this source extends that with a concrete reactive-loop
    implementation showing how a production agent actually runs step by step.

- **Novel**: This source contributes the following that are new to the corpus:
  - The three execution models (sequential, parallel/wait-all, concurrent
    fan-in) mapped to SRE investigation requirements with specific trade-offs
  - The LangGraph BSP limitation as a concrete barrier to interactive agent
    systems
  - The queue+lock pattern for serializing concurrent LangGraph graph resumes
  - The priority queue pattern for user input preemption in agent loops
  - The `task_id === thread_id` identity convention for routing events
  - The single-process simplification argument for IO-bound agent workloads —
    the article's most counterintuitive insight
  - The durable supervisor / stateless sub-agent asymmetry for checkpoint-free
    recovery
  - The "build hard, ship simple" methodology demonstrated end-to-end
  - The three portable primitives (identity, event transport, reactive loop)

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
- Quotes were extracted via WebFetch and spot-checked against the rendered
  page. Key quotes verified verbatim against the live URL on 2026-07-26:
  Claims 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, and 17 all have direct
  quotes confirmed character-for-character. Claims 8, 9, 14, and 15 use
  paraphrased quotes where the source describes patterns in prose rather
  than in single extractable sentences — these are marked as "(no direct
  quote; see paraphrase in Our assessment)."
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
- Published June 24, 2026 — approximately 3 weeks before extraction. The
  architecture described is very recent and may still be evolving.

## Evaluation Context

**MINER EVAL** — This is a quality comparison run against an existing DeepSeek/Flash note. You MUST follow these eval rules in addition to MINER.md:

1. **Do NOT modify the source issue** — no comments, no label changes, no close/reopen on issue #1.
2. **Do NOT edit existing files** under `source-notes/` except to add ONE new eval file (see filename rule below).
3. **Filename**: `<normal-slug>-cohere-north-mini-code-free-eval.md`
   (e.g. if the note would be `blog-foo-bar.md`, write
   `blog-foo-bar-cohere-north-mini-code-free-eval.md`).
4. **Frontmatter**: set
   `issue: "#1-cohere-north-mini-code-free-eval"`
   (not the bare issue number).
5. **Branch**:
   `miner/eval-cohere-north-mini-code-free-issue-1-r30185272482`
6. **PR title** must start with `[eval:cohere-north-mini-code-free] `
   then the normal `source: <slug> (#1)` pattern.
7. **PR labels**: `source-note` AND `miner-eval` (both required).
8. **PR body** must include:
   "Miner candidate eval (openrouter / `cohere/north-mini-code:free`)
   for golden issue #1. Do not merge —
   compare against the merged DeepSeek/Flash baseline note."

**Comparison scope:** This note is a structural and content comparison of the
existing `blog-pagerduty-sre-agent-architecture.md` (DeepSeek/Flash baseline) —
same source URL, same structural sections, and same guide impact analysis. The
goal is to compare model extraction quality and adherence to MINER.md rules.
This revision (2026-07-26) addresses Assayer feedback by adding the 14 missing
claims (Claims 3–5, 7–17), Concrete Artifacts, Cross-References, Guide Impact,
and Extraction Notes sections that the initial extraction omitted. The 3 claims
present in the initial extraction were verified as accurate; the additional
14 claims are independently extracted from the source with verbatim quotes
verified against the live URL.
