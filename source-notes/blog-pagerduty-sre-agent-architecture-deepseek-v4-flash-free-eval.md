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

> A detailed practitioner writeup from PagerDuty Engineering tracing the
> architectural evolution of their SRE Agent from a single-agent monolith to a
> reactive multi-agent system. Covers specific failure modes (context rot,
> instruction overload), three execution models for sub-agent orchestration,
> the LangGraph BSP limitation, a custom reactive loop built from first
> principles, and the counterintuitive simplification from distributed to
> single-process architecture. Published June 2026.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three senior/staff/principal engineers at PagerDuty —
  Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from
  concept to GA), Ralph Bird (Principal ML Engineer, AI agents and LLM
  observability). All three built the system they describe; first-hand production
  experience, not a thought-piece.
- **Scope**: Covers the full architectural journey — why a single agent failed
  (context rot, instruction overload, sequential blocking, no interactivity),
  three execution models for N sub-agents (sequential, parallel-wait-all,
  concurrent fan-in), the custom reactive loop built on LangGraph
  interrupt/resume primitives with a priority queue and lock, the identity
  convention (`task_id === thread_id`), the event transport evolution (webhooks
  → PubSub → in-process mailbox), and the single-process simplification.
  Does NOT cover: evaluation metrics, cost data, specific LLM model choices,
  or failure recovery from model hallucinations.

## Extracted Claims

### Claim 1: AI-native products have fundamentally different failure modes and engineering trade-offs than AI-assisted products
- **Evidence**: The authors draw this as the foundational framing, citing João
  Freitas's companion PagerDuty post. The entire article is a case study in
  what this distinction means architecturally.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of
  an existing system. In AI-native products, the AI is the system."
- **Our assessment**: The distinction is clearly demonstrated throughout the
  article. Context rot and instruction overload are AI-native failure modes
  that would not appear in conventional software, and they shape every
  architectural decision that follows.

### Claim 2: Context rot creates a hard ceiling on single-agent architectures for incident investigation
- **Evidence**: The Incident Context document grew to include JSON blobs of
  alerts, past incidents, change events, runbook content, service topology,
  dependency graphs, historical patterns, and remediation options. The authors
  cite Liu et al. (2023) "Lost in the Middle" showing model performance degrades
  beyond certain context thresholds. Newer models improve but cost and latency
  remain considerations.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows, not because the information isn't there but because the model
  struggles to weight it correctly."
- **Our assessment**: Well-established in the literature and widely observed in
  practice. The specific contribution here is demonstrating how it manifests
  in SRE incident investigation, where context documents grow large and diverse.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. In a monolithic
  agent, adding a new capability competes with every existing capability for the
  model's attention.
- **Confidence**: emerging
- **Quote**: "In a monolithic agent, adding a new capability competes with every
  existing capability for the model's attention."
- **Our assessment**: The Jaroslawicz reference provides research backing, but
  the specific observation of agent degradation as features accumulate is the
  authors' production experience. A significant concern for teams building
  long-lived agent systems — feature work carries a hidden tax.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search
  for evidence, evaluate — took several minutes. A moderately complex incident
  with 3-4 candidate causes could take 10+ minutes to diagnose. This is a direct
  production measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible. The latency is plausible given each step involves
  LLM inference plus external API calls (log search, metrics query). The key
  insight: this is an architectural problem (sequential execution of parallelizable
  work), not a model speed problem.

### Claim 5: Lack of interactivity during agent execution was a structural failure of the monolithic design, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the agent
  to finish and restart with that context. The authors characterize this as the
  agent "operating without information the human already had."
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: The most impactful failure mode for live incident response.
  An agent that cannot accept mid-run input wastes the human's existing knowledge
  and delays resolution. Directly supports keeping humans on the paging path.

### Claim 6: Three execution models exist for multi-agent investigation — sequential, parallel-wait-all, and concurrent fan-in — with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three: sequential (total
  time = sum of durations, "a slow hypothesis in the middle blocks everything
  behind it"), parallel-wait-all (time = slowest sub-agent but main agent idle,
  "the graph is locked inside the parallel call until everything resolves"), and
  concurrent fan-in (dispatch all asynchronously, process each result as it
  arrives, user input as first-class event).
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: A clear taxonomy with well-articulated trade-offs mapped to
  the SRE investigation domain. Not inventing new models but mapping them to
  concrete incident-response requirements.

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and blocks mid-run user input
- **Evidence**: The authors tried LangChain Deep Agents with sub-agents as tools.
  In LangGraph's BSP model, parallel tool calls are one superstep — control
  returns only after every tool resolves. The orchestrator cannot react to
  sub-agent 1's result while sub-agents 2 and 3 are still running. No external
  event — including user input — can reach the graph while blocked inside a
  parallel call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model: it advances in supersteps, running a batch
  of work and then stopping at a synchronization barrier before the next batch
  begins."
- **Our assessment**: Matches LangGraph's documented BSP/superstep design. The
  implication — framework-managed parallelism is incompatible with real-time
  interactivity — is a significant constraint for interactive agent systems on
  LangGraph. Note: async sub-agents were added later but the authors argue this
  still doesn't fully address their requirements (see Claim 15).

### Claim 8: Concurrent sub-agent completions cause a race condition in LangGraph's interrupt/resume pattern, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first completion
  resumed the graph and triggered the working loop. The second completion arrived
  while the main agent was still processing. "LangGraph either errored or started
  a fresh execution from scratch," losing state from the first arrival. The fix:
  a local queue drained one result at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph execution model. The queue is the obvious
  fix, but the fact that the naive approach fails under realistic timing is a
  valuable warning.

### Claim 9: A lock around the drain loop's resume call is needed because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, a window existed between "main agent
  completed" and "graph re-interrupts" where the drain loop could issue a resume
  before the graph was genuinely paused. The fix: the drain loop held a lock
  while resuming, and the graph signaled through a callback when it had actually
  re-interrupted, releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A subtle concurrency edge case. The lock pattern is
  standard but the specific interaction with LangGraph's interrupt/resume
  lifecycle is a useful concrete example. The authors' willingness to document
  this level of implementation detail adds credibility.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results via a priority queue to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the message went
  in fourth — by the time the drain loop reached it, the graph might have
  finished. The fix: a two-level priority queue with user input at priority 0
  (highest) and sub-agent results at priority 1. A `route_event` node branches
  based on event type.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean pattern. The priority queue is simple but essential
  — without it, user input can arrive too late to influence the investigation.
  The `route_event` branching design is a concrete LangGraph pattern worth noting.

### Claim 11: The identity convention `task_id === thread_id` routes events to the correct graph without lookup tables — the single most important convention in the system
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries a
  `parent_task_id` pointing to whoever spawned it. By making LangGraph's
  `thread_id` identical to the agent's `task_id`, when a sub-agent publishes a
  completion event carrying `parent_task_id: task-001`, the parent agent
  immediately knows which thread to resume. No lookup table, no correlation logic.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: An elegant convention that eliminates an entire class of
  infrastructure. The kind of simple design that only becomes obvious after
  building the complex version. Worth adopting as a pattern for LangGraph-based
  multi-agent systems.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed
  (separate processes, broker, durable store), then questioned the assumption.
  Investigation is overwhelmingly IO (call log API and wait, call metrics API,
  hand text to model and wait). A single team owns the sub-agent system.
  Spreading IO-bound agents across services buys "deployment, service discovery,
  network failure modes, distributed tracing — without buying the thing services
  are for."
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive insight. The reflex to
  treat multi-agent systems as distributed systems is strong, and the authors
  make a specific argument for why it is wrong for IO-bound workloads. The key
  qualifier is "IO-bound" — this does not generalize to compute-bound agent
  workloads, but for SRE investigation it is a powerful simplification.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable (checkpointed, can pause/resume/recover).
  Sub-agents are stateless (no checkpoints, re-spawned on failure rather than
  resumed mid-flight). Making every agent durable would mean keeping N+1
  checkpoints consistent and reconciling them on restart. Each processing step
  is atomic and persisted before the next event is touched, so the checkpoint
  never captures in-flight mailbox contents.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: Clean asymmetric durability. Reduces recovery from a
  distributed consensus problem to single-writer checkpoint. The trade-off —
  re-running sub-agent work on failure — is acceptable when sub-agents are cheap
  (IO-bound, no side effects beyond their result).

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The distributed design required webhook callbacks, PubSub
  broadcast, and a durable event store — all to move results across a network.
  Once everything shares a process, the answer is "an in-process mailbox — an
  asyncio.Queue — injected into each background task when it's spawned." The
  sub-agent writes to the queue; the supervisor reads from it. No broker, no
  callback endpoint, no network hop.
- **Confidence**: emerging
- **Quote**: "an in-process mailbox — an asyncio.Queue — injected into each
  background task when it's spawned"
- **Our assessment**: Natural consequence of the single-process decision. The
  authors are explicit this only works because sub-agents are guaranteed to live
  in the same process as their spawning supervisor. Multiple concurrent
  investigation runs can still land on different pods.

### Claim 15: Framework-native async sub-agent support (polling-based) stops short of true mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after
  their initial experiments) which let the supervisor launch background tasks
  and return immediately without blocking. But the polling model means "no push
  notification when a sub-agent finishes, which means no deterministic synthesis
  the moment each result arrives." Native support "stops short of the two things
  our SRE Agent actually needs: true mid-run steering, and gradual emission of
  artifacts." Those require the same primitives they already built.
- **Confidence**: emerging
- **Quote**: "the native support stops short of the two things our SRE Agent
  actually needs: true mid-run steering, and gradual emission of artifacts as
  each hypothesis resolves."
- **Our assessment**: An important qualification — framework evolution does not
  automatically solve the hard problems. Polling vs. push is the smaller gap;
  the bigger gap is mid-run steering and progressive result emission, which
  frameworks do not address.

### Claim 16: "Build the hard version first" was a deliberate methodology — the complex distributed prototype revealed which primitives were essential before simplifying for production
- **Evidence**: The complex version (webhooks, PubSub, durable event store, full
  primitive set) was "a deliberate step, not a mistake." It let the authors see
  which parts were essential and which were accidents of assuming distributed
  architecture. The simplification to single-process was only possible because
  they first understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: Advice rather than a falsifiable claim, but demonstrated
  convincingly. The authors actually shipped the simple version, which is the
  part most worth emulating. Risk: teams might over-engineer without ever
  simplifying.

### Claim 17: Three primitives — identity, event transport, reactive loop — form a portable foundation for multi-agent architectures regardless of runtime engine
- **Evidence**: The authors identify three primitives that survive the
  simplification from distributed to single-process: (1) Identity
  (`task_id === thread_id`) routes events without lookup tables; (2) Event
  transport delivers results reliably; (3) Reactive loop processes results
  as they arrive and treats user input as a first-class event. Understanding
  why each layer exists is what distinguishes inheriting an architecture from
  owning it.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as your framework evolves."
- **Our assessment**: A useful distillation into three abstraction layers
  (identity → transport → control loop). The portability claim is plausible
  but only tested on LangGraph in this article.

## Concrete Artifacts

### Reactive loop node structure

The supervisor's LangGraph reactive loop consists of six nodes:

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

- `accept_event`: Graph spends most of its life paused here, waiting for the
  drain loop to deliver the next event from the priority queue.
- `route_event`: Inspects event type and branches.
- `handle_sub_agent_result`: Processes a sub-agent's findings.
- `handle_user_input`: Adds new work to state, marks as pending spawn,
  re-enters `plan` for immediate dispatch.
- `plan`: Formulates investigation strategy.
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

### Agent lifecycle (A2A-protocol-inspired)

`working → completed | failed | canceled`

### Priority queue levels

```
Priority 0 (highest): User input — processed first, jumps the line
Priority 1:          Sub-agent results — processed in arrival order after pending user input
```

### Single-process architecture properties

- Supervisor and all sub-agents share one process
- Mailbox: ordinary `asyncio.Queue` (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Within one run, all sub-agents co-located with their spawning supervisor
- Multiple concurrent investigation runs land on different pods/processes

## Cross-References

The following candidates were provided via `miner-related-notes.md`. Each is
cited or dismissed:

- **`source-notes/blog-pagerduty-sre-agent-architecture.md`** (same URL) —
  Baseline note for this source. The merged DeepSeek/Flash extraction against
  which this eval note should be compared. Covers the identical source with
  a different model backend.
- **`source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md`** —
  Dismissed: different domain (retail/gaming SRE), not about agent architecture.
- **`source-notes/docs-google-sre-prodcast-04-05-furino-slos.md`** —
  Dismissed: SLOs, not agent architecture.
- **`source-notes/docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** —
  Dismissed: AI for SRE at Google via horizontal tools team, different focus
  (ticket/incident analysis dashboards vs. agent architecture deep-dive).
- **`source-notes/docs-google-sre-prodcast-03-06-incident-response-tooling.md`** —
  Dismissed: broader IR tooling (monitoring, dashboards, alerting), not
  agent-specific.
- **`source-notes/docs-google-sre-prodcast-03-11-embracing-complexity.md`** —
  Dismissed: sociotechnical complexity, not agent architecture.
- **`source-notes/docs-google-sre-prodcast-03-05-building-reliable-systems.md`** —
  Dismissed: database reliability, not agent architecture.
- **`source-notes/docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md`** —
  Dismissed: ML training infrastructure SRE, not agent architecture.
- **`source-notes/blog-incidentio-ai-sre-incident-run.md`** —
  **Corroborates**: Both describe AI SRE agents for incident investigation.
  incident.io Claim 1 ("AI SRE autonomously begins multi-source investigation
  immediately upon incident declaration") corroborates the PagerDuty pattern
  of parallel investigation. PagerDuty contributes the deep architecture while
  incident.io provides the user-experience counterpart.
- **`source-notes/docs-google-sre-prodcast-01-05-client-transparent-migrations.md`** —
  Dismissed: client migration transparency, not agent architecture.
- **`source-notes/docs-google-sre-prodcast-04-09-ai-agents.md`** (S4E9) —
  **Corroborates**: S4E9's framework distinguishes deterministic agents from
  full dynamic agents (agent spectrum). PagerDuty's bounded stateless sub-agents
  with fixed scope align with the "algorithm with LLM-augmented steps" tier.
  S4E9 Claim 1 on capability boundaries is demonstrated in PagerDuty's design.
- **`source-notes/docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md`** (S6E4) —
  **Corroborates**: Zelesko's "human-supervised" SRE evolution matches
  PagerDuty's mid-run human steering design. Zelesko Claim 2 ("SRE work is
  moving from human-centric to human-supervised") is directly instantiated by
  PagerDuty's priority queue giving user input precedence over sub-agent results.
- **`source-notes/blog-pagerduty-production-ai-agent-gaps.md`** (Freitas, 2026) —
  **Corroborates**: This source is the direct companion framing piece cited in
  the SRE Agent article. Freitas's Claim 1 (the prototype-to-production gap
  is large and structural — demos are easy, reliability is hard) frames the
  production reliability problem that motivates the SRE Agent's architectural
  journey. The SRE Agent article introduces the AI-native vs AI-assisted
  distinction as its own framing (Claim 1), building on — but distinct from —
  Freitas's reliability framework. Freitas also contributes the five-pillar
  production-readiness framework (Claim 7), the architecture evolution pattern
  from single-agent to hierarchical (Claim 8), and the transparent UX finding
  (Claim 9), all of which the SRE Agent architecture instantiates in concrete
  implementation details.

- **`source-notes/blog-anthropic-building-effective-agents.md`** (Anthropic, 2024) —
  **Corroborates**: This is the canonical taxonomy of agentic-system
  architecture and provides framework-level endorsement of several PagerDuty
  design choices. Anthropic's Claim 11 (orchestrator-workers pattern: "a
  central LLM dynamically breaks down tasks, delegates to worker LLMs, and
  synthesizes results") directly corroborates PagerDuty's supervisor/sub-agent
  architecture (Claims 6, 11–14) — both describe the same fundamental pattern
  of dynamic task decomposition and parallel result synthesis. Anthropic's
  Claim 14 (human checkpointing: "Agents can then pause for human feedback at
  checkpoints or when encountering blockers") corroborates PagerDuty's mid-run
  human steering design (Claims 5, 10) — both treat human input as a
  first-class event in the agent execution lifecycle. Anthropic's Claim 2
  (workflows-vs-agents distinction: predetermined code paths vs. LLM-directed
  control) is a parallel framing to PagerDuty's Claim 1 (AI-native vs
  AI-assisted distinction) — both describe the same architectural spectrum
  from different angles (Anthropic: implementation patterns; PagerDuty:
  product philosophy). Anthropic's simplicity-first principle (Claims 1, 3)
  also aligns with PagerDuty's "build hard, ship simple" methodology
  (Claim 16). **Contrasts**: Anthropic's post is pattern-agnostic about
  deployment architecture (single-process vs distributed), while PagerDuty
  makes a specific argument (Claim 12) that IO-bound agent workloads should
  be single-process — a deployment-level recommendation outside Anthropic's
  scope.
- **Corroborates — additional**: None of the remaining existing source notes
  discuss SRE agent architecture. All other notes cover SLOs, incident response
  tooling, database reliability, ML training observability, or platform
  engineering without direct connection to multi-agent orchestration patterns.
- **Contradicts**: None identified.
- **Novel**: This is the sole practitioner architecture deep-dive in the corpus
  on a production multi-agent SRE investigation system. Specific novel
  contributions: the three execution models mapped to SRE incident requirements,
  the LangGraph BSP limitation for interactive agents, the queue+lock+priority
  queue reactive loop pattern, the `task_id === thread_id` convention, the
  single-process simplification argument for IO-bound agents, and the durable
  supervisor / stateless sub-agent asymmetry.

## Guide Impact

- **Chapter 00 (Principles)**: Provides evidence that AI-native failure modes
  (context rot, instruction overload) are structurally different from
  conventional software failures. Supports a principle: "Design for AI-native
  failure modes from the start." The "build hard, ship simple" methodology is
  also a candidate principle.

- **Chapter 01 (Incident Response)**: Concrete architecture requirements for
  AI-assisted incident investigation: (a) real-time visibility into agent
  reasoning is a hard requirement, (b) mid-run human steering must be a
  first-class event, (c) sequential hypothesis testing creates unacceptable
  latency for multi-cause incidents, (d) the agent must never operate without
  information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Specific patterns for multi-agent ops
  architecture: (a) the three execution models and their trade-offs, (b) the
  reactive loop pattern with interrupt/resume, priority queue, and lock
  serialization, (c) the `task_id === thread_id` identity convention,
  (d) durable supervisor / stateless sub-agent asymmetry, (e) single-process
  simplification for IO-bound agent workloads.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (hypothesis
  formulation → parallel sub-agent dispatch → findings synthesis → root cause)
  is a directly reusable pattern. The priority queue user-input-preemption
  pattern applies to any interactive on-call agent.

## Extraction Notes

- The source is a single long-form blog post (~28 min read) on PagerDuty's
  engineering blog. No sub-pages were followed; the article is self-contained.
- All quotes are verbatim from the rendered page fetched via web fetch and
  spot-checked against the source. Longer section paraphrases are in "Our
  assessment" where no direct quote captured the meaning.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025,
  LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023,
  Google A2A protocol). These were not independently fetched.
- The source is rich in architectural detail but light on quantitative metrics
  (no latency distributions, no accuracy/eval numbers, no cost data). The one
  concrete number is "10+ minutes" for sequential diagnosis.
- No paywall. Article publicly accessible.
- Published June 24, 2026 — approximately one month before this extraction.
- This is an eval note comparing the deepseek-v4-flash-free model against the
  baseline DeepSeek/Flash note (`blog-pagerduty-sre-agent-architecture.md`).
  Claims and structure mirror the same source but are independently extracted
  by this model.
