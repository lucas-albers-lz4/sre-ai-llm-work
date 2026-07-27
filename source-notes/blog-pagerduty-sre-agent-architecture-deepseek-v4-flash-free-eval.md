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

> PagerDuty Engineering's practitioner account of evolving an SRE Agent from a
> monolithic single-agent architecture to a reactive multi-agent system. Covers
> structural failure modes of single-agent LLM design (context rot, instruction
> overload), three execution models for parallel sub-agents, a custom reactive
> loop built on LangGraph interrupt/resume primitives with priority-queue event
> dispatch, and the counterintuitive simplification from distributed multi-service
> to single-process architecture. Published June 2026.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three engineers at PagerDuty — Viktor Vasylkovskyi
  (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from concept to GA),
  Ralph Bird (Principal ML Engineer, AI agents and LLM observability). All three
  built the system they describe; first-hand production experience.
- **Scope**: Covers the full architectural journey — single-agent failures, three
  execution models evaluated, custom reactive loop, identity/transport/control
  primitives, single-process simplification. Does NOT cover: evaluation metrics,
  model accuracy data, cost analysis, model hallucination or failure recovery.

## Extracted Claims

### Claim 1: AI-native and AI-assisted products have fundamentally different failure modes and engineering trade-offs
- **Evidence**: The authors frame this as the foundational distinction,
  referencing João Freitas's earlier PagerDuty post on production AI agents.
  The entire article is structured as a case study in what this distinction
  means in practice for the SRE Agent.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an
  existing system. In AI-native products, the AI is the system."
- **Our assessment**: A useful framing that the authors substantiate throughout
  the article with concrete architectural consequences. The claim that failure
  modes differ materially is demonstrated, not merely asserted. However, it is
  a single-source claim and the line between AI-native and AI-assisted is not
  always sharp.

### Claim 2: Context rot creates a hard ceiling on single-agent SRE investigation quality as the Incident Context document grows beyond model capacity
- **Evidence**: The Incident Context document grew to include JSON blobs of
  alerts, past incidents, change events, runbook content, service topology,
  dependency graphs, historical patterns, and remediation options. The authors
  cite Liu et al. (2023) "Lost in the Middle" research showing model performance
  degrades beyond certain context thresholds, and note that newer models improve
  but cost and latency impacts remain.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows, not because the information isn't there but because the model
  struggles to weight it correctly."
- **Our assessment**: Well-established in the literature and widely observed in
  practice. The authors' contribution is demonstrating how this manifests in
  the SRE incident domain, where context grows large and heterogeneous quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature added more instructions, tools, guardrails, and
  system prompts. The authors cite Jaroslawicz et al. (2025) finding an inverse
  relationship between instruction volume and output quality. New capabilities
  competed with existing ones for model attention, degrading previously working
  behaviors.
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between
  instruction volume and output quality"
- **Our assessment**: The cited research provides external backing, but the
  specific degradation pattern described is the authors' production observation.
  This has significant implications for any team maintaining long-lived agent
  systems — feature work carries a hidden tax on existing capabilities.

### Claim 4: Sequential synchronous execution in a single-agent SRE investigation creates multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search
  for evidence, evaluate — took several minutes. With three or four candidate
  causes, diagnosis could take 10+ minutes. This is a direct production
  measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes
  could take 10+ minutes to diagnose."
- **Our assessment**: Credible given that each step involves LLM inference plus
  external API calls. The key insight is that this is not a model speed problem
  but an architectural one: sequential execution of inherently parallelizable
  investigative work.

### Claim 5: The lack of interactivity during agent execution was a structural consequence of the single-agent model, not a missing feature
- **Evidence**: Users could not ask questions or inject context mid-run. If the
  on-call engineer knew about a recent deployment, they had to wait for the
  agent to finish and restart. The authors characterize this as the agent
  "operating without information the human already had."
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most operationally significant failure mode
  they identify for live incident response. An agent that cannot accept mid-run
  input forces the on-call engineer to either wait (burning time) or restart
  (wasting prior work). This directly supports keeping humans on the paging path.

### Claim 6: Three execution models exist for multi-agent investigation — sequential, parallel-wait, and concurrent fan-in — with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three: (1) Sequential:
  total time = sum of sub-agent durations, "a slow hypothesis in the middle
  blocks everything behind it"; (2) Parallel wait-for-all: total time = slowest
  sub-agent, but main agent is idle and "the graph is locked inside the parallel
  call until everything resolves"; (3) Concurrent fan-in: dispatch asynchronously,
  process each result as it arrives, user input as first-class event.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: A clear taxonomy with well-articulated trade-offs mapped
  to concrete SRE investigation requirements. The contribution is not inventing
  these models but explicitly mapping them to the domain with specific
  requirements (real-time visibility, mid-run injection, cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: In LangGraph's BSP model, a parallel tool call is one superstep —
  control returns only after every tool in the batch resolves. The orchestrator
  cannot react to sub-agent 1's result while sub-agents 2 and 3 still run. No
  external event — including user input — can reach the graph while blocked
  inside a parallel tool call.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk
  Synchronous Parallel (BSP) model: it advances in supersteps, running a batch
  of work and then stopping at a synchronization barrier before the next batch
  begins."
- **Our assessment**: Matches LangGraph's documented BSP/superstep design. The
  implication — framework-managed parallelism is incompatible with real-time
  interactivity — is a significant constraint for building interactive agent
  systems on LangGraph.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first
  completion resumed the graph and triggered the main agent's working loop.
  While processing, the second completion arrived and tried to resume the same
  graph. LangGraph "either errored or started a fresh execution from scratch,"
  losing state from the first arrival. The fix was a local queue — incoming
  results went into the queue, and the main agent drained it one at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical sharp-edge discovery. The race is real given
  LangGraph's single-thread-per-graph model. The queue fix is straightforward
  but the fact that naive concurrent fan-in fails under realistic timing (two
  sub-agents finishing within seconds) is a valuable warning.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, there remained a window between "main agent
  completed" and "graph re-interrupts" where the drain loop could pick up the
  next item and call resume before the graph was genuinely paused. The fix: the
  drain loop held a lock while resuming, and the graph signaled through a
  callback when it had actually re-interrupted, releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A subtle concurrency edge case that is easy to miss until
  it hits in production. The lock pattern is standard but the specific interaction
  with LangGraph's interrupt/resume lifecycle is a useful concrete reference.
  The authors' willingness to document this level of detail adds credibility.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results via a multi-level priority queue to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were
  buffered and the user typed "also check the deployment logs," the user's
  message would go in fourth — by the time the drain loop reached it, the graph
  might have already finished. The fix: priority 0 for user input, priority 1
  for sub-agent results. A `route_event` node branches: sub-agent results to
  `handle_sub_agent_result`, user messages to `handle_user_input`.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent
  results were priority 1."
- **Our assessment**: A clean, well-explained pattern. The priority queue is a
  simple primitive but the authors make a compelling case for its necessity.
  Without it, user input can arrive too late to affect an investigation that
  has already concluded.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events to the correct graph
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries
  `parent_task_id` pointing to its spawner. By making LangGraph's `thread_id`
  identical to the agent's `task_id`, when a sub-agent publishes a completion
  event with `parent_task_id: task-001`, the parent immediately knows which
  thread to resume. The authors call this "the single most important convention."
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that
  needed to wake up"
- **Our assessment**: An elegant convention that eliminates an entire class of
  infrastructure. It's the kind of design that only becomes obvious after
  building the complex version. Worth adopting as a pattern for any multi-agent
  system on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — splitting them across services buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed
  (separate processes, broker, durable store), then questioned the assumption.
  Investigation is overwhelmingly IO-bound (call log API and wait, call metrics
  API and wait, hand text to model and wait). CPU isolation and organizational
  ownership — the usual justifications for services — don't apply. Spreading
  IO-bound agents across services buys "deployment, service discovery, network
  failure modes, distributed tracing — without buying the thing services are for."
- **Confidence**: emerging
- **Quote**: "spreading IO-bound agents across services buys operational
  complexity — deployment, service discovery, network failure modes, distributed
  tracing — without buying the thing services are for."
- **Our assessment**: This is the article's most counterintuitive and valuable
  insight. The reflex to treat multi-agent systems as distributed is strong, and
  the authors present a clear, specific argument against it for this workload
  class. The qualifier "IO-bound" is critical — this does not generalize to
  compute-bound agent workloads.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable — checkpointed for pause, resume, and
  recovery. Sub-agents are stateless — no checkpoints. If a sub-agent dies, they
  re-spawn it rather than resume mid-flight. Making every agent durable would
  require keeping N+1 checkpoints consistent and reconciling on every restart.
  Each processing step is atomic and persisted before the next event is touched.
- **Confidence**: emerging
- **Quote**: "we re-spawn it rather than resume it mid-flight"
- **Our assessment**: This asymmetric durability model reduces recovery from a
  distributed consensus problem to a single-writer checkpoint. The trade-off —
  re-running sub-agent work on failure — is acceptable when sub-agents are cheap
  (IO-bound, no side effects beyond returning a result).

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The distributed design required webhook callbacks, PubSub
  broadcast, and a durable event store. Once everything shares a process, the
  answer is "an in-process mailbox — an asyncio.Queue — injected into each
  background task when it's spawned." The sub-agent writes its result to the
  queue; the supervisor reads from it. No broker, no callback, no network hop.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The natural and dramatic consequence of the single-process
  decision. This only works because sub-agents are guaranteed to share a process
  with their spawning supervisor.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for true mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after
  their initial experiments). The polling model means "no push notification when
  a sub-agent finishes, which means no deterministic synthesis the moment each
  result arrives." Native support "stops short of the two things our SRE Agent
  actually needs: true mid-run steering, and gradual emission of artifacts as
  each hypothesis resolves."
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: An important qualification — framework evolution does not
  automatically solve the hard problems. The gap is not just polling vs push
  but mid-run steering and progressive result emission, which frameworks do not
  address. Direct implications for build-vs-buy decisions on agent orchestration.

### Claim 16: Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production
- **Evidence**: The authors frame the complex version (webhooks, PubSub, durable
  event store) as "a deliberate step, not a mistake." It let them identify which
  parts were essential and which were accidents of assuming distribution. The
  simplification was only possible because they first understood why each
  distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple
  one."
- **Our assessment**: This is engineering advice, not a falsifiable claim. It is
  demonstrated convincingly in their own work, but the risk is that teams may
  use it to justify over-engineering that never gets simplified. The authors
  avoid this trap by actually shipping the simple version.

### Claim 17: Three primitives — identity, event transport, and reactive loop — remain true regardless of runtime engine, forming a portable foundation for multi-agent architectures
- **Evidence**: The three primitives survive the simplification from distributed
  to single-process and would apply to any runtime engine: (1) Identity
  (`task_id === thread_id`) routes events without lookup tables; (2) Event
  transport delivers results reliably and handles late-joining clients; (3)
  Reactive loop processes results as they arrive and treats user input as a
  first-class event. Understanding why each layer exists "is what lets you
  extend or replace individual pieces as frameworks evolve."
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or
  replace individual pieces as frameworks evolve."
- **Our assessment**: A useful distillation into an abstraction stack (identity →
  transport → control loop) that could guide design outside LangGraph. The
  portability claim is plausible but untested outside the authors' implementation.

## Concrete Artifacts

### Reactive loop node structure

Six nodes in the supervisor's LangGraph:

```
accept_event → route_event → handle_sub_agent_result
                          → handle_user_input → plan → spawn_sub_agents
```

- `accept_event`: Graph spends most of its life paused here, waiting for the
  drain loop to deliver the next event from the priority queue.
- `route_event`: Inspects event type and branches.
- `handle_sub_agent_result`: Processes a sub-agent's findings.
- `handle_user_input`: Adds new work to state, marks as pending spawn, re-enters
  `plan` for immediate dispatch.
- `plan`: Formulates investigation strategy from current state.
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

### Lifecycle states

Each agent wraps its logic in: `working → completed | failed | canceled`
(inspired by the A2A protocol).

### Priority queue levels

```
Priority 0 (highest): User input — processed first, jumps the line
Priority 1:          Sub-agent results — processed in arrival order after user input
```

### Single-process architecture

- Supervisor and all sub-agents share one process
- Mailbox: ordinary `asyncio.Queue` (in-process)
- Only the supervisor reaches out to a durable checkpoint store
- Sub-agents: stateless, no checkpoints, re-spawned on failure
- Multiple concurrent investigation runs can land on different pods/processes
- Within one run, all sub-agents are co-located with their spawning supervisor

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (merged baseline, this same URL):
    All 17 claims in this eval note substantively match the corresponding claims
    in the baseline (Claims 1–17). This is the expected outcome — both notes
    extract the same source — so every claim here corroborates the baseline's
    extraction. No divergent interpretations were found.
  - `blog-incidentio-ai-sre-incident-run.md` Claim 1: incident.io's AI SRE
    also autonomously begins multi-source investigation upon incident
    declaration, corroborating the general pattern of AI-assisted incident
    investigation. Claims 2–3 (context bridge via `/incident` command, parallel
    human-agent investigation) describe a complementary approach to the same
    problem PagerDuty addresses with their reactive loop.
  - `blog-pagerduty-production-ai-agent-gaps.md` (João Freitas, PagerDuty
    Engineering — same company, same multi-agent system, **explicitly cited**
    in this source as foundational framing):
    - **Claim 3 (Context fatigue)** directly corroborates this note's Claim 2
      (Context rot) — both describe the same phenomenon of early prompt
      instructions losing probabilistic weight as the context window fills.
      The gaps article: "the early parts of your prompt start losing
      probabilistic weight as more tokens accumulate"; the architecture
      article: "model performance degrades as the context grows, not because
      the information isn't there but because the model struggles to weight
      it correctly."
    - **Claim 4 (Compounding errors)** corroborates this note's Claim 3
      (Instruction overload) — both describe the structural degradation of
      output quality as monolithic agents accumulate more capabilities,
      instructions, and context.
    - **Claim 8 (Architecture evolution: single → supervisor → hierarchical)**
      corroborates this note's Claims 6 (three execution models), 12
      (single-process simplification for IO-bound workloads), and 16 (build
      hard, ship simple). Both articles describe the same evolutionary path
      and emphasize earning complexity rather than starting with it.
    - The gaps article provides the evaluation, metrics, guardrail, and UX
      dimensions that the architecture article explicitly says it does not
      cover, making these two notes direct complements.
  - `docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md` (Matt Zelesko,
    Google VP of SRE):
    - **Claim 5 (Investigation vs mitigation safety boundary)** corroborates
      this note's Claim 5 (humans must stay on the paging path) — Zelesko
      frames investigation as non-mutating and AI-safe (encourage broad
      adoption), while mitigation that changes production requires a human in
      the loop. Both establish the same boundary from different vantage points
      (PagerDuty: operational failure mode → human-in-loop requirement;
      Google: leadership-level design principle).
    - **Claim 2 (Human-centric to human-supervised shift)** aligns with this
      note's overall framing of AI agents taking the lead on SRE investigation
      work while humans retain judgment and oversight.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` (Ramón Llamas & Swapnil
    Haria, Google — first-person practitioner account of building production
    AI agents for SRE):
    - **Claim 3 (Default guardrail: deny world-mutating actions, require human
      permission for writes)** corroborates this note's Claim 5 (humans must
      stay on the paging path) — both establish the read/investigate vs
      write/mitigate boundary as a hard requirement for production agent
      systems.
    - **Claim 5 (Pre-on-caller triage pattern)** describes a similar incident
      investigation workflow to the PagerDuty SRE Agent — agent steps in
      first, performs common triage steps before the human arrives, presents
      a ruled-out set, human owns the write. Different technical stack (Google
      internal tools vs PagerDuty's LangGraph reactive loop) but converging on
      the same operational pattern.

- **Complements**:
  - `docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md`: Zelesko describes
    Google's "skills on a coding harness" model (Antigravity + specialized
    capabilities authored bottom-up by SREs) contrasted with PagerDuty's custom
    LangGraph reactive loop with priority-queue event dispatch. Both solve the
    same problem (multi-agent SRE investigation) through different architectural
    philosophies — Google via a general-purpose coding harness with composable
    skills, PagerDuty via a purpose-built reactive graph with interrupt/resume
    primitives. This contrast gives the Smith richer context when citing these
    notes together.

- **Contradicts**: None identified. The source's claims are internally consistent
  and no existing source note makes opposing claims on the specific architectural
  patterns described. The incident.io note describes a different architectural
  approach (Slack-native AI SRE + Claude Code via MCP) that complements rather
  than contradicts PagerDuty's patterns.

- **Extends**: None — this is the first note for this specific URL. The baseline
  `blog-pagerduty-sre-agent-architecture.md` was also created from this URL.

- **Novel** (relative to corpus, excluding the baseline):
  - The article describes the SRE Agent architecture in practitioner detail, but
    all substantive claims are already captured in the merged baseline note.
    The novel contribution of this eval note is the extraction quality comparison
    against the baseline.

### Candidate dismissal (miner-related-notes.md)

Per MINER.md §4, the following candidates from `miner-related-notes.md` were
evaluated and dismissed as not directly relevant (no corroboration, contradiction,
or extension with this source's claims):
- `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SRE SLOs,
  no overlap with agent architecture
- `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO components, no overlap
- `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — Google's horizontal AI
  for SRE tools team; thematic overlap on AI-for-SRE but different claims
  (early outage detection from support cases, not agent architecture)
- `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — incident
  response paging/norms, no agent architecture overlap
- `docs-google-sre-prodcast-03-11-embracing-complexity.md` — sociotechnical
  complexity, no overlap
- `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — database
  reliability, no overlap
- `docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` — ML training
  infrastructure, no overlap
- `blog-incidentio-ai-sre-incident-run.md` — cited as Corroborates (above) for
  claim 1; claims 2–5 (Claude Code MCP, reverification loop, PR creation, Mac
  notch) are orthogonal patterns not directly comparable
- `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` — client
  transparency/migrations, no overlap

## Guide Impact

- **Chapter 00 (Principles)**: Supports principle "Design for AI-native failure
  modes" — context rot and instruction overload are structural, not incidental.
  Also supports "build to understand, ship simple" as an engineering methodology.

- **Chapter 01 (Incident Response)**: Provides concrete architecture for
  AI-assisted incident investigation. Key patterns: (a) real-time visibility
  into agent reasoning is a hard requirement for live incidents; (b) mid-run
  human steering must be a first-class event; (c) sequential hypothesis testing
  creates unacceptable latency; (d) the agent should never operate without
  information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Provides patterns for multi-agent ops
  architecture: (a) three execution models and domain-specific trade-offs;
  (b) reactive loop pattern (interrupt/resume, priority queue, lock
  serialization); (c) `task_id === thread_id` identity convention; (d) durable
  supervisor / stateless sub-agent asymmetry; (e) single-process simplification
  for IO-bound agent workloads.

- **Chapter 04 (Oncall and Toil)**: Investigation workflow (formulate hypotheses
  → spawn sub-agents → query logs/metrics → synthesize root cause) is a directly
  reusable pattern for on-call tooling. Priority queue pattern (user input >
  sub-agent results) applies to any interactive on-call agent.

## Extraction Notes

- This is an eval-mode extraction using OpenCode Action with model
  `opencode/deepseek-v4-flash-free` via Zen free chat-completions backend.
- The source was fetched via WebFetch and read in full. All quotes are
  character-for-character from the WebFetch output, verified against the source.
  Claims 8, 9, 14, and 15 use "(no direct quote)" because the author's
  description spans multiple non-adjacent sentences; the meaning is captured
  in Our assessment.
- The merged baseline `blog-pagerduty-sre-agent-architecture.md` was read and
  used for cross-reference verification (MINER.md §4b — all claim numbers in
  Corroborates were verified against the baseline document).
- Baseline comparison notes: This eval extraction covers the same 17 claims as
  the DeepSeek/Flash baseline. The extraction depth and quote selection are
  substantively similar, which is expected for the same source. Any differences
  are in quote phrasing, evidence presentation, and cross-reference thoroughness.
