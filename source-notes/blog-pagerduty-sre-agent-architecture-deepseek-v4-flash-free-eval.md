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

> Practitioner writeup from PagerDuty Engineering documenting the evolution
> of their SRE Agent from a synchronous single-agent design to a reactive
> multi-agent system with concurrent fan-in. Covers specific failure modes
> of monolithic agents, LangGraph BSP limitations, a custom interrupt/resume
> loop with priority queue, and the counterintuitive simplification from
> distributed services to single-process architecture. Published June 2026.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three PagerDuty engineers — Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from concept to GA), Ralph Bird (Principal ML Engineer). All built the system they describe. First-hand production experience at a leading incident management company.
- **Scope**: Full architectural journey from single-agent through three execution models to production reactive loop. Covers identity conventions, transport, the simplification to single-process, and the "build hard, ship simple" methodology. Does NOT cover: evaluation metrics, cost data, specific model choices, or failure recovery from hallucinations.

## Extracted Claims

### Claim 1: AI-native products have fundamentally different failure modes and engineering constraints than AI-assisted ones
- **Evidence**: Authoritative framing from the authors, citing João Freitas's PagerDuty blog post. The entire article is structured as a case study of this distinction. The failure modes — context rot, instruction overload — do not appear in conventional software.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an existing system. In AI-native products, the AI is the system."
- **Our assessment**: Well-supported by the article's concrete examples. The distinction has practical consequences for architecture decisions and reliability requirements. The claim that failure modes differ materially between the two categories is demonstrated, not merely asserted.

### Claim 2: Context rot creates a hard ceiling on single-agent architectures for incident investigation — more context leads to worse decisions
- **Evidence**: The Incident Context document in the single-agent system grew to include JSON blobs of alerts, past incidents, change events, runbook content, service topology, dependency graphs, historical patterns, and remediation options. The authors cite Liu et al. (2023) "Lost in the Middle" showing model performance degrades beyond certain context thresholds.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the context grows, not because the information isn't there but because the model struggles to weight it correctly."
- **Our assessment**: Well-established in the literature (Liu et al. 2023) and widely observed. The authors' contribution is showing how this manifests in SRE incident investigation, where context documents grow large and diverse quickly. Newer models improve but the cost and latency impacts remain.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, and system prompts. The authors cite Jaroslawicz et al. (2025) finding "an inverse relationship between instruction volume and output quality." Adding a new capability competed with every existing capability for the model's attention.
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between instruction volume and output quality"
- **Our assessment**: Research-backed (Jaroslawicz et al. 2025). The production observation about agent degradation as features accumulate is significant — feature work carries a hidden tax on existing capabilities in monolithic agent designs.

### Claim 4: Sequential synchronous execution in a single-agent investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain — formulate hypothesis, search for evidence, evaluate — took several minutes. With 3-4 candidate causes, total time reached 10+ minutes. The authors describe this as a direct production measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes could take 10+ minutes to diagnose."
- **Our assessment**: Plausible given each step involves LLM inference plus external API calls (log search, metrics query). The key insight is this is an architectural problem (sequential execution of parallelizable work), not a model speed problem.

### Claim 5: Lack of mid-run interactivity was a structural failure of the single-agent design, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the on-call engineer knew about a recent deployment, they had to wait for the agent to finish and restart. The authors characterize this as the agent "operating without information the human already had."
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: The most impactful failure mode for live incident response. An agent that cannot accept mid-run input wastes time and ignores the human's existing situational knowledge. Directly supports keeping humans on the paging path.

### Claim 6: Three execution models exist for multi-agent investigation — only concurrent fan-in meets real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - Sequential: total time = sum of sub-agent durations. "A slow hypothesis in the middle blocks everything behind it."
  - Parallel, wait for all: total time = slowest sub-agent. Main agent is idle, "the graph is locked inside the parallel call until everything resolves."
  - Parallel fan-out, concurrent fan-in: dispatch all asynchronously, process each result as it arrives. "The main agent is never idle. The user always has visibility. New work can be injected at any point."
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New work can be injected at any point."
- **Our assessment**: Clearly reasoned taxonomy with well-articulated trade-offs mapped to the SRE investigation domain. The contribution is mapping these models to concrete requirements (real-time visibility, mid-run injection, cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: The authors tried LangChain Deep Agents with sub-agents as tools. In LangGraph's BSP model, a parallel tool call is one superstep — control returns only after every tool in that batch resolves. The orchestrator cannot react to sub-agent 1's result while sub-agents 2 and 3 still run. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk Synchronous Parallel (BSP) model: it advances in supersteps, running a batch of work and then stopping at a synchronization barrier before the next batch begins."
- **Our assessment**: Matches LangGraph's documented BSP/superstep design. The implication — framework-managed parallelism is incompatible with real-time interactivity — is a significant constraint. LangGraph has since added async sub-agent support, but the authors argue this still doesn't fully address their requirements.

### Claim 8: Concurrent sub-agent completions cause a race condition when resuming a LangGraph graph, requiring a queue to buffer arrivals
- **Evidence**: When two sub-agents finished close together, the first completion resumed the graph and triggered the working loop. While processing, the second completion tried to resume the same graph. LangGraph either errored or started fresh execution from scratch, losing state from the first arrival. The fix was a local queue — incoming results went in, and the main agent drained it one at a time.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A practical sharp-edge discovery. The race is real given LangGraph's single-thread-per-graph execution model. The queue is obvious in retrospect, but the naive approach fails under realistic timing.

### Claim 9: A lock around the drain loop's resume call is necessary because a queue alone leaves a race window between graph completion and re-interruption
- **Evidence**: Even with the queue, a window remained between "main agent completed" and "graph re-interrupts" where the drain loop could call resume before the graph was genuinely paused. The fix: the drain loop held a lock while resuming, and the graph signaled through a callback when it had re-interrupted, releasing the lock.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A concurrency edge case easy to miss until production. The lock pattern is standard but the specific interaction with LangGraph's interrupt/resume lifecycle is a useful concrete example demonstrating that queue-only serialization is insufficient.

### Claim 10: User input must be treated as a higher-priority event than sub-agent results to enable mid-run steering
- **Evidence**: With a regular FIFO queue, if three sub-agent results were buffered and the user typed "also check the deployment logs," the message went in fourth — by the time the drain loop reached it, the graph might have finished. The fix: a two-level priority queue where user input is priority 0 (highest) and sub-agent results are priority 1.
- **Confidence**: emerging
- **Quote**: "User input was priority 0 — highest, processed first. Sub-agent results were priority 1."
- **Our assessment**: Clean, well-explained pattern. The priority queue is a simple primitive but the authors make a compelling case for why it's essential — without it, user input arrives too late. The `route_event` branching design is a concrete LangGraph pattern worth adopting.

### Claim 11: The identity convention `task_id === thread_id` eliminates lookup tables and correlation logic for routing events
- **Evidence**: Every agent run gets a UUID `task_id`. Every sub-agent carries `parent_task_id` pointing to whoever spawned it. Making the LangGraph `thread_id` identical to the agent's `task_id` means when a sub-agent publishes a completion event with `parent_task_id: task-001`, the parent immediately knows which LangGraph thread to resume — no lookup table. The authors call this "the single most important convention" in the system.
- **Confidence**: emerging
- **Quote**: "the identifier on the event was the identifier of the graph that needed to wake up"
- **Our assessment**: Elegant convention that eliminates an entire class of infrastructure. Only becomes obvious after building the complex version. Worth adopting for any multi-agent system on LangGraph.

### Claim 12: IO-bound agentic workloads do not benefit from service boundaries — distributing them buys operational complexity without the benefits services exist for
- **Evidence**: The authors initially built as if agents were distributed (separate processes, broker, durable store), then questioned the assumption. Investigation is overwhelmingly IO (call API and wait, hand text to model and wait). A single team owns the whole sub-agent system. Spreading IO-bound agents across services buys "deployment, service discovery, network failure modes, distributed tracing" without buying isolation or independent scaling.
- **Confidence**: emerging
- **Quote**: "Spreading IO-bound agents across services buys operational complexity — deployment, service discovery, network failure modes, distributed tracing — without buying the thing services are for."
- **Our assessment**: The article's most counterintuitive insight. The reflex to treat multi-agent systems as distributed systems is strong, and the authors make a clear argument for why it is wrong for this workload class. The key qualifier is "IO-bound" — this does not generalize to compute-bound workloads but is powerful for the common SRE investigation case.

### Claim 13: Concentrating durability in the supervisor while keeping sub-agents stateless creates a single source of truth and eliminates N+1 checkpoint reconciliation
- **Evidence**: The supervisor is durable (checkpointed for pause, resume, recovery). Sub-agents are stateless (no checkpoints — if one dies, re-spawn rather than resume mid-flight). Making every agent durable would require keeping N+1 checkpoints consistent and reconciling on every restart. With one source of truth, each processing step is atomic and persisted before the next event is touched.
- **Confidence**: emerging
- **Quote**: "If it dies, we re-spawn it rather than resume it mid-flight."
- **Our assessment**: Clean design principle reducing recovery from distributed consensus to single-writer checkpoint. Trade-off (re-running sub-agent work on failure) is acceptable when sub-agents are cheap and IO-bound. The atomic-step-per-event model is a strong guarantee for crash recovery reasoning.

### Claim 14: When all agents share a single process, the transport layer collapses from webhooks/PubSub/durable event store to an in-process asyncio.Queue
- **Evidence**: The distributed design required webhook callbacks, PubSub broadcast, and a durable event store to move results between processes. In a single process, the answer is "an in-process mailbox — an asyncio.Queue — injected into each background task when it's spawned." The sub-agent writes to the queue; the supervisor reads from it. No broker, no callback endpoint, no network hop.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Natural consequence of the single-process decision. The authors are explicit this only works because sub-agents are guaranteed to live in the same process as their spawning supervisor. Multiple concurrent runs can still land on different pods, but within one run all sub-agents are co-located.

### Claim 15: Framework-native async sub-agent support (polling-based) leaves a gap for mid-run steering and gradual artifact emission — the hard parts remain custom
- **Evidence**: The authors evaluated LangGraph's async sub-agents (added after their initial experiments) which let the supervisor launch background tasks and return immediately. But the polling model means "no push notification when a sub-agent finishes, which means no deterministic synthesis the moment each result arrives." Native support "stops short of the two things our SRE Agent actually needs: true mid-run steering, and gradual emission of artifacts as each hypothesis resolves."
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Important qualification — framework evolution does not automatically solve the hard problems. Polling vs. push is the smaller gap; the bigger gap is mid-run steering and progressive result emission, which frameworks do not address.

### Claim 16: Building the complex distributed version first was a deliberate methodology — "build the hard version to understand the problem; ship the simple one"
- **Evidence**: The authors explicitly frame the complex version (webhooks, PubSub, durable event store) as "a deliberate step, not a mistake." It let them identify essential vs. accidental complexity. The simplification was only possible because they first understood why each distributed primitive existed.
- **Confidence**: anecdotal
- **Quote**: "Build the hard version to understand the problem; ship the simple one."
- **Our assessment**: Valuable engineering philosophy demonstrated convincingly in the authors' own work. Risk: teams might use this to justify over-engineering that never gets simplified. The authors avoid this trap by actually shipping the simple version.

### Claim 17: Three primitives — identity, event transport, and reactive loop — form a portable foundation for multi-agent architectures regardless of runtime engine
- **Evidence**: The authors identify three primitives that survive the simplification from distributed to single-process and would apply to any runtime: (1) Identity (task_id === thread_id) routes events without lookup tables; (2) Event transport delivers results reliably and handles late-joining clients; (3) Reactive loop processes results as they arrive, serializes concurrent completions, and treats user input as a first-class event.
- **Confidence**: emerging
- **Quote**: "Understanding why each layer exists is what lets you extend or replace individual pieces as frameworks evolve."
- **Our assessment**: Useful distillation forming a reasonable abstraction stack (identity -> transport -> control loop). Portability claim is plausible but untested — the authors only implemented on LangGraph. The layered understanding is valuable for teams evaluating framework choices.

## Concrete Artifacts

### Reactive loop node structure

The supervisor's LangGraph reactive loop consists of six nodes:

```
accept_event -> route_event -> handle_sub_agent_result
                          -> handle_user_input -> plan -> spawn_sub_agents
```

- `accept_event`: Graph spends most of its life paused here, waiting for the drain loop to deliver the next event from the priority queue.
- `route_event`: Inspects event type and branches.
- `handle_sub_agent_result`: Processes a sub-agent's findings.
- `handle_user_input`: Adds new work to state, marks as pending spawn, re-enters `plan`.
- `plan`: Formulates investigation strategy based on current state.
- `spawn_sub_agents`: Dispatches new sub-agent background tasks.

### Identity hierarchy

```
Main Agent (task_id: task-001, thread_id: task-001)
    |
    +-- Sub-Agent 1 (task_id: sub-1, parent_task_id: task-001)
    |     +-> completes -> publishes event with parent_task_id: task-001
    |                  -> parent agent resumes thread_id: task-001
    +-- Sub-Agent 2 (task_id: sub-2, parent_task_id: task-001)
    +-- Sub-Agent 3 (task_id: sub-3, parent_task_id: task-001)
```

### Lifecycle states (A2A-protocol-inspired)

Each agent wraps its logic in `working -> completed | failed | canceled`

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
- Multiple concurrent investigation runs can land on different pods
- Within one run, all sub-agents are co-located with their spawning supervisor

### Drain loop with lock pattern

The drain loop holds a lock while `Command(resume=...)` is called. The graph signals through a callback when it has actually re-interrupted, releasing the lock. This guarantees the graph is never resumed twice in flight.

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-sre-agent-architecture.md` (baseline for this URL, PR #5) — All 17 claims in this eval note are independent extractions of the same source that corroborate the baseline's claims. Specifically: Claim 1 ~ baseline Claim 1 (AI-native vs AI-assisted), Claim 2 ~ baseline Claim 2 (context rot), Claim 3 ~ baseline Claim 3 (instruction overload), Claim 4 ~ baseline Claim 4 (sequential latency), Claim 5 ~ baseline Claim 5 (lack of interactivity), Claim 6 ~ baseline Claim 6 (three execution models), Claim 7 ~ baseline Claim 7 (LangGraph BSP), Claim 8 ~ baseline Claim 8 (concurrent resume race), Claim 9 ~ baseline Claim 9 (lock serialization), Claim 10 ~ baseline Claim 10 (priority queue), Claim 11 ~ baseline Claim 11 (task_id === thread_id), Claim 12 ~ baseline Claim 12 (single-process simplification), Claim 13 ~ baseline Claim 13 (durable supervisor), Claim 14 ~ baseline Claim 14 (in-process transport), Claim 15 ~ baseline Claim 15 (framework async gaps), Claim 16 ~ baseline Claim 16 (build hard methodology), Claim 17 ~ baseline Claim 17 (three primitives).
  - `blog-incidentio-ai-sre-incident-run.md` — Claim 1 (parallel multi-source investigation) corroborates Claim 6's concurrent fan-in model; both describe autonomous parallel investigation by AI SRE tools.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — Claim 9 (AI is "a tool like anything else" — good at removing toil but needs human oversight) corroborates Claim 5's assertion that lack of interactivity is a structural failure; both emphasize human-in-the-loop requirements for incident response tooling.

- **Contradicts**: None identified. The claims are architectural descriptions from a practitioner, not normative positions that contradict existing notes.

- **Extends**:
  - `blog-pagerduty-production-ai-agent-gaps.md` (Freitas, 2026) — This source is the direct follow-up to Freitas's framing article. Freitas's Claim 1 (prototype-to-production gap is structural) is the foundation for this source's entire architectural evolution story. This source extends the AI-native vs AI-assisted distinction (Freitas's core framing) with concrete implementation patterns.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — Claim 2 (horizontal AI tools team builds shared tooling) superficially touches on AI-for-SRE architecture, but the PagerDuty article provides far deeper architectural detail. The connection is weak — different organizational contexts (horizontal team vs dedicated SRE agent).

- **Novel**: Everything in this source was already novel in the baseline extraction. Key contributions (identical to baseline):
  - The three execution models mapped to SRE investigation requirements
  - The LangGraph BSP limitation for interactive agent systems
  - The queue+lock pattern for serializing concurrent graph resumes
  - The priority queue pattern for user input preemption
  - The `task_id === thread_id` identity convention
  - The single-process simplification for IO-bound agent workloads
  - The durable supervisor / stateless sub-agent asymmetry
  - The "build hard, ship simple" methodology

## Guide Impact

- **Chapter 00 (Principles)**: Supports "Design for AI-native failure modes" — context rot and instruction overload are structural, not incidental. Also supports "build to understand, ship simple" as an engineering principle for agent systems.

- **Chapter 01 (Incident Response)**: Provides concrete architecture for AI-assisted incident investigation. Key claims: (a) real-time visibility into agent reasoning is a hard requirement for live incidents; (b) mid-run human steering must be a first-class event; (c) sequential hypothesis testing creates unacceptable latency; (d) the agent should never operate without information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Provides patterns for multi-agent ops architecture: (a) three execution models and their trade-offs; (b) reactive loop pattern (interrupt/resume, priority queue, lock serialization); (c) `task_id === thread_id` identity convention; (d) durable supervisor / stateless sub-agent asymmetry; (e) single-process simplification for IO-bound workloads.

- **Chapter 04 (Oncall and Toil)**: The investigation workflow (formulate hypotheses -> spawn sub-agents -> query logs/metrics -> report findings -> synthesize root cause) is a directly reusable pattern. The priority queue pattern applies to any interactive on-call agent.

## Extraction Notes

- EVAL NOTE: This is a candidate model evaluation run comparing DeepSeek V4 Flash Free (via OpenCode Zen free chat-completions) against the merged DeepSeek/Flash baseline (PR #5).
- The source is the same single long-form blog post (~28 min read) on PagerDuty's engineering blog. Same URL as the baseline.
- Quotes were extracted via WebFetch and verified against the rendered page. All direct quotes appear verbatim in the source.
- The article cites six references (Freitas 2026, Jaroslawicz et al. 2025, LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023, Google A2A protocol). These were not independently fetched.
- No quantitative metrics beyond the "10+ minutes" latency figure. Rich in architectural detail but light on eval numbers.
- The source is publicly accessible, no paywall.
- Baseline cross-reference candidate `docs-google-sre-prodcast-03-07-retail-gaming.md` dismissed (retail/gaming SRE, no agent architecture overlap). `docs-google-sre-prodcast-04-05-furino-slos.md` dismissed (SLOs, no overlap). `docs-google-sre-prodcast-03-11-embracing-complexity.md` dismissed (complexity/sociotechnical, not agent architecture). `docs-google-sre-prodcast-03-05-building-reliable-systems.md` dismissed (database reliability). `docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` dismissed (ML training infra). `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` dismissed (migrations, not agent architecture).
