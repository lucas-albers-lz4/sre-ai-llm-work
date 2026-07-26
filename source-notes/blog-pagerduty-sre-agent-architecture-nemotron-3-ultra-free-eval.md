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
issue: "#1-nemotron-3-ultra-free-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation (Nemotron-3-Ultra-Free Eval)

> Nemotron-3-Ultra-Free evaluation extraction of the PagerDuty SRE Agent architecture post. Same source as the merged DeepSeek/Flash baseline; this note exists solely for quality comparison against `blog-pagerduty-sre-agent-architecture.md`.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three senior/staff/principal engineers at PagerDuty — Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from concept to GA), Ralph Bird (Principal ML Engineer, focused on AI agents and LLM observability). First-hand production experience.
- **Scope**: Full architectural journey — single-agent failure modes, three execution models evaluated, custom reactive loop on LangGraph interrupt/resume, identity convention, event transport, distributed-to-single-process simplification, "build hard ship simple" methodology. Does NOT cover eval/accuracy metrics, cost data, specific model choices, or hallucination recovery.

## Extracted Claims

### Claim 1: The distinction between AI-native and AI-assisted products determines failure modes and engineering trade-offs
- **Evidence**: Authoritative framing — authors cite João Freitas's earlier PagerDuty post on production AI agents. The entire article is structured as a case study in what this distinction means in practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an existing system. In AI-native products, the AI is the system."
- **Our assessment**: This is a useful framing backed by concrete examples throughout the article. The claim that failure modes differ materially between the two categories is demonstrated, not just asserted.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document included JSON blobs of alerts, past incidents, change events, runbook content, service topology, dependency graphs, historical patterns, and remediation options. Authors cite Liu et al. (2023) "Lost in the Middle" research showing model performance degrades beyond certain context thresholds. Newer models improve but cost and latency impacts remain.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the context grows."
- **Our assessment**: Well-established in literature (Liu et al. 2023) and widely observed in practice. The authors' contribution is showing how it manifests in SRE incident investigation where context documents grow large and diverse quickly.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Every new feature meant more instructions, tools, guardrails, system prompts. Authors cite Jaroslawicz et al. (2025) finding an inverse relationship between instruction volume and output quality. Agents that performed well at a certain feature set degraded as features accumulated because new capabilities competed with existing ones for model attention.
- **Confidence**: emerging
- **Quote**: "an inverse relationship between instruction volume and output quality"
- **Our assessment**: The Jaroslawicz et al. (2025) reference provides research backing, but the specific claim about agent degradation as features accumulate is the authors' production observation. Significant concern for teams building long-lived agent systems — feature work carries a hidden tax on existing capabilities.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: A single root cause analysis chain (formulate hypothesis, search for evidence, evaluate) took several minutes. A moderately complex incident with 3-4 candidate causes could take 10+ minutes to diagnose. Direct production measurement from their single-agent system.
- **Confidence**: emerging
- **Quote**: "A moderately complex incident with three or four candidate causes could take 10+ minutes to diagnose."
- **Our assessment**: Credible. The latency is plausible given each step involves LLM inference plus external API calls (log search, metrics query). Key insight: this is not a model speed problem — it's an architectural problem (sequential execution of parallelizable work).

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Users could not ask questions or add context mid-run. If the on-call engineer knew about a recent deployment, they had to wait for the agent to finish, then restart with that context included. Authors characterize this as the agent "operating without information the human already had." This was not a bug — it was a consequence of the synchronous single-agent execution model.
- **Confidence**: emerging
- **Quote**: "the agent was operating without information the human already had"
- **Our assessment**: This is the most important failure mode they identify for live incident response. An agent that can't accept mid-run input from the on-call engineer wastes time and ignores the human's existing knowledge. Directly supports the guide's editorial principle of keeping humans on the paging path.

### Claim 6: Three execution models exist for multi-agent investigation; only concurrent fan-in meets real-time visibility and mid-run steering requirements
- **Evidence**: Authors enumerate and evaluate all three:
  - **Sequential**: Total time = sum of all sub-agent durations. Simple but "a slow hypothesis in the middle blocks everything behind it."
  - **Parallel, wait for all**: Total time = slowest sub-agent. But the main agent is idle during execution, can't report progress, and "the graph is locked inside the parallel call until everything resolves."
  - **Parallel fan-out, concurrent fan-in**: Dispatch all asynchronously, process each result as it arrives, user input is "a first-class event alongside sub-agent results." The main agent is never idle, user always has visibility, new work can be injected at any point.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New work can be injected at any point."
- **Our assessment**: Taxonomy is clearly reasoned and each model's trade-offs are well articulated. Authors' contribution is not inventing these models but clearly mapping them to the SRE investigation domain with concrete requirements (real-time visibility, mid-run injection, cancellation).

### Claim 7: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity and makes mid-run user input injection impossible
- **Evidence**: Authors tried LangChain Deep Agents with sub-agents as tools. In LangGraph's BSP model, a parallel tool call is one superstep — control returns only after every tool in that batch resolves. The orchestrator cannot react to sub-agent 1's result at t=3min while sub-agents 2 and 3 still run. No external event — including user input — can reach the graph while blocked inside a parallel tool call. The tool set is fixed at dispatch time.
- **Confidence**: emerging
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk Synchronous Parallel (BSP) model"
- **Our assessment**: Specific technical claim about LangGraph's execution model matching documented BSP/superstep design. Implication — framework-managed parallelism is incompatible with real-time interactivity — is the authors' conclusion.

### Claim 8: A custom reactive loop built from LangGraph interrupt/resume primitives enables per-result reactivity and mid-run user injection
- **Evidence**: Authors built a drain loop with a priority queue and lock around resume calls. The graph interrupts at `accept_event`; a result arrives in the queue; the drain loop acquires the lock, resumes the graph, lets it run until it interrupts again, then releases the lock. Concurrent arrivals serialized. User input enters the same priority queue at priority 0 (highest), sub-agent results at priority 1. The `route_event` node branches to `handle_sub_agent_result` or `handle_user_input`, which adds new work to state and re-enters `plan` for immediate dispatch.
- **Confidence**: settled
- **Quote**: "The drain loop was the spine of the whole architecture. The graph was interrupted. A result arrived in the queue. The drain loop acquired the lock, resumed the graph, let it run through until it interrupted again, then released the lock and went back to waiting on the queue."
- **Our assessment**: Concrete, reproducible pattern. The priority queue design (user input > sub-agent results) directly solves the mid-run steering requirement. The lock around resume/re-interrupt cycle prevents the race condition where a second resume fires before the graph has re-paused.

### Claim 9: The `task_id === thread_id` identity convention routes events to the correct LangGraph thread without lookup tables
- **Evidence**: Every agent run has a UUID `task_id`. Every sub-agent carries `parent_task_id` pointing to its spawner. Convention: LangGraph `thread_id` == agent's `task_id`. When sub-agent publishes completion with `parent_task_id: task-001`, the parent agent immediately knows which thread to resume. No lookup table, no correlation logic.
- **Confidence**: settled
- **Quote**: "It meant that when a sub-agent published a completion event carrying `parent_task_id: task-001`, the parent agent immediately knew which LangGraph thread to resume. No lookup table. No correlation logic. The identifier on the event was the identifier of the graph that needed to wake up."
- **Our assessment**: Elegant, practical convention. The insight is that the graph's existing thread mechanism *is* the routing table if you align identifiers. This is a directly applicable pattern for any LangGraph-based multi-agent system.

### Claim 10: A three-layer primitive stack emerged: task identity, event queue/transport, reactive loop
- **Evidence**: By the time the async model worked, three layers had accumulated:
  1. Task identity layer (`task_id`, `parent_task_id`, `thread_id` convention)
  2. Event queue and transport layer (webhook callbacks, PubSub broadcast, durable event store indexed by `task_id`)
  3. Reactive loop layer (interrupt/resume graph, priority queue, lock)
- **Confidence**: settled
- **Quote**: "By this point, we'd accumulated three layers of machinery, each solving a different problem: the task identity layer, event queue and transport layer, and reactive loop."
- **Our assessment**: Clear architectural decomposition. Each layer solves a distinct problem and the layers compose cleanly.

### Claim 11: The distributed multi-process architecture (webhooks, PubSub, durable event store per agent) was over-engineered for IO-bound agent workloads
- **Evidence**: Authors stepped back and reasoned: sub-agents do almost no compute — investigation is overwhelmingly IO (call log API and wait, call metrics API and wait, hand text to model and wait). No compute hotspot to isolate. Single team owns the whole system, so no organizational boundary for service boundaries to mirror. Spreading IO-bound agents across services buys operational complexity (deployment, service discovery, network failure modes, distributed tracing) without buying what services are for.
- **Confidence**: emerging
- **Quote**: "Our sub-agents do almost none of that. An investigation is overwhelmingly IO — call a log API and wait, call a metrics API and wait, hand the text to the model and wait. There's no compute hotspot to isolate."
- **Our assessment**: Strong architectural reasoning. The "services for IO-bound work" anti-pattern is well-known in distributed systems; the authors correctly identify that agent workloads inherit the same property. This is a high-value insight for teams reaching for distributed frameworks prematurely.

### Claim 12: Durable supervisor / stateless sub-agent asymmetry concentrates durability in one place, avoiding N+1 checkpoint reconciliation
- **Evidence**: Supervisor is durable — its state is checkpointed, can pause/resume/recover. Message queue lives inside supervisor, covered by same checkpoint. Sub-agents are stateless — no checkpoints, run-produce-result-report-back, if they die re-spawn rather than resume mid-flight. Making every agent durable would mean keeping N+1 checkpoints consistent and reconciling on every restart.
- **Confidence**: settled
- **Quote**: "Making every agent durable would mean keeping N+1 checkpoints consistent and reconciling them on every restart. By concentrating durability in the supervisor and treating sub-agents as cheap and replaceable, there's exactly one source of truth to recover."
- **Our assessment**: Excellent pattern. The asymmetry is the point — it's not that sub-agents *can't* be durable, it's that making them so adds coordination cost with no benefit for IO-bound, short-lived tasks. This is a directly applicable architectural pattern.

### Claim 13: In the single-process design, the mailbox stays an in-process `asyncio.Queue` because the supervisor drains it atomically per checkpoint step
- **Evidence**: Supervisor drains mailbox one event at a time: pull event, run execution to next interrupt, checkpoint before touching next event. Each step atomic and persisted when applied. On restart, supervisor reloads last checkpoint with empty queue; any still-running sub-agents are re-spawned and results land in fresh mailbox. Nothing in queue needs to survive a crash because nothing durable ever lived there.
- **Confidence**: settled
- **Quote**: "Because each step is atomic and persisted the moment it's applied, the checkpoint never has to capture in-flight mailbox contents — every persisted step can start from an empty mailbox, since the supervisor is constantly draining it."
- **Our assessment**: Clever use of the checkpointing semantics. The mailbox doesn't need durability because the supervisor's constant draining means any in-flight event represents work that hasn't been checkpointed yet — and the sub-agent that produced it will be re-spawned. This is a subtle but important correctness argument.

### Claim 14: Native framework async sub-agent support (e.g., LangGraph async sub-agents) uses pull-based polling, leaving a gap for deterministic push-based synthesis and true mid-run steering
- **Evidence**: LangGraph's async sub-agents launch background tasks and return immediately; supervisor checks progress on its own schedule. No push notification when sub-agent finishes, so no deterministic synthesis the moment each result arrives. Polling cycle of a few seconds is often invisible for minute-scale sub-agents, but the native support stops short of true mid-run steering and gradual artifact emission as hypotheses resolve.
- **Confidence**: emerging
- **Quote**: "The pull-based polling model in these frameworks leaves a specific gap: there's no push notification when a sub-agent finishes, which means no deterministic synthesis the moment each result arrives."
- **Our assessment**: Fair assessment of the polling vs. push trade-off. For minute-scale sub-agents, polling latency is negligible, but the authors needed true mid-run steering (user input preemption) which polling doesn't natively provide. The assessment that you end up reimplementing the same primitives (identity, transport, reactive loop) is credible given their requirements.

### Claim 15: "Build the hard version to understand, ship the simple one" methodology — the distributed proof-of-concept was a deliberate step, not a mistake
- **Evidence**: Building the reactive loop the hard way (webhooks, PubSub, durable event store, full primitive set) let them see which parts were essential and which were accidents of assuming a distributed architecture. The shippable design was reached by taking complexity away: one process, durable supervisor, stateless sub-agents, in-process mailbox.
- **Confidence**: emerging
- **Quote**: "Build the hard version to understand the problem; ship the simple one."
- **Our assessment**: Honest and valuable engineering philosophy. The distributed PoC was expensive but necessary for the team to earn the simplification. This matches the "build to understand, ship simple" principle.

### Claim 16: Three AI-native failure modes specific to SRE agents: context rot, instruction overload, and blocking-on-slowest-sub-agent
- **Evidence**: Context rot (Claim 2) and instruction overload (Claim 3) are the single-agent failure modes. The multi-agent failure mode is "blocking-on-slowest-sub-agent" — in the parallel-wait-for-all model, one slow/hanging sub-agent blocks synthesis indefinitely. The authors don't name a third distinct failure mode explicitly; the triad in the triage comment may be summarizing the three execution model failures rather than three AI-native failure modes per se.
- **Confidence**: anecdotal
- **Quote**: (No single quote captures all three as a named triad)
- **Our assessment**: The triage comment's "three AI-native failure modes" framing may over-structure what the article presents. The article clearly identifies context rot and instruction overload as AI-native single-agent failure modes. The "blocking-on-slowest" is an architectural failure mode of the parallel-wait-all model, not inherently AI-native. Worth noting the distinction.

### Claim 17: The investigation workflow (formulate hypotheses → spawn sub-agents → query logs/metrics → report findings → synthesize root cause) is a directly reusable pattern for on-call tooling
- **Evidence**: The article describes this workflow explicitly and the sub-agent dispatch pattern implements it directly. Each sub-agent receives focused context for one hypothesis, queries relevant data sources, returns evidence for/against, supervisor synthesizes.
- **Confidence**: settled
- **Quote**: "formulate a few candidate root causes... and spawns a sub-agent for each one. Each sub-agent goes off, queries logs, looks at metrics, and reports back with evidence either supporting or disproving its hypothesis. The SRE Agent synthesizes across all the findings and surfaces the strongest root cause candidate to the engineer."
- **Our assessment**: Directly extractable pattern. The priority queue pattern (user input > sub-agent results) applies to any interactive on-call agent.

## Concrete Artifacts

### Code: Task Identity Convention
```javascript
Main Agent (task_id: task-001, thread_id: task-001)
    │
    ├── Sub-Agent 1 (task_id: sub-1, parent_task_id: task-001)
    │     └→ completes → publishes event with parent_task_id: task-001
    │                  → parent agent resumes thread_id: task-001
    ├── Sub-Agent 2 (task_id: sub-2, parent_task_id: task-001)
    └── Sub-Agent 3 (task_id: sub-3, parent_task_id: task-001)
```

### Code: Reactive Loop Drain Pattern (pseudocode)
```
while True:
    event = await priority_queue.get()
    async with lock:
        await graph.resume(event)
        # graph runs until it interrupts at `accept_event`
        # lock released via callback when graph re-interrupts
```

### Code: Priority Queue Event Structure
```python
# User input: priority 0 (highest)
# Sub-agent results: priority 1
event = {
    "type": "user_input" | "sub_agent_result",
    "priority": 0 | 1,
    "payload": {...}
}
```

### Diagram Descriptions (from source images)
- **Sequential timeline**: Sum of durations, slow middle blocks all
- **Parallel wait-for-all timeline**: Max duration, main agent idle, graph locked
- **Concurrent fan-in timeline**: Main agent active throughout, results processed as they arrive, user input injected mid-run
- **Naive concurrent fan-out LangGraph**: Race condition on concurrent resume
- **Queue + lock LangGraph**: Serializes resumes, lock held until graph re-interrupts
- **Full reactive loop**: 6-node graph with `accept_event` → `route_event` → `handle_sub_agent_result` / `handle_user_input` → `plan` → `spawn_sub_agents` → `accept_event`
- **Event transport layer**: PubSub broadcast + durable event store indexed by `task_id`
- **Single-process architecture**: Supervisor + sub-agents in one process, only supervisor writes to durable checkpoint store, mailbox = `asyncio.Queue`
- **Distributed architecture (discarded)**: N agents = N durable stores + message broker + cross-process state reconciliation
- **LangGraph async sub-agents**: Supervisor launches background tasks, polls progress, concurrency complexity in framework

## Cross-References

### Corroborates: `source-notes/blog-pagerduty-sre-agent-architecture.md` (baseline DeepSeek/Flash note)
- All 15 claims above are corroborated by the baseline note's Claims 1-7, 12-17 (numbering differs slightly). The baseline note covers the same architectural journey with identical quotes and evidence. Key overlapping extractions:
  - Context rot (Claim 2 in both)
  - Instruction overload (Claim 3 in both)
  - Sequential latency (Claim 4 in both)
  - No interactivity (Claim 5 in both)
  - Three execution models (Claim 6 in both)
  - LangGraph BSP limitation (Claim 7 in both)
  - Reactive loop with priority queue + lock (Claim 8 in both)
  - `task_id === thread_id` (Claim 9 in both)
  - Three primitives (Claim 10 in both)
  - Single-process simplification (Claim 11 in both)
  - Durable supervisor / stateless sub-agent (Claim 12 in both)
  - In-process mailbox atomic drain (Claim 13 in both)
  - Native async sub-agent polling gap (Claim 14 in both)
  - Build-hard-ship-simple (Claim 15 in both)

### Contradicts: None
- No contradictions found between this extraction and the baseline note. Both extract the same claims with the same evidence.

### Extends: `source-notes/blog-pagerduty-production-ai-agent-gaps.md` (PagerDuty's earlier "Production AI Agents: Closing the Gaps" post by João Freitas)
- The baseline note cites Freitas (2026) as the foundational framing for AI-native vs AI-assisted. The Freitas note (if extracted) would provide the earlier PagerDuty perspective that this article builds on. Claim 1 here explicitly references it.

### Novel: This extraction adds Claim 16 (three AI-native failure modes framing) and Claim 17 (explicit workflow pattern extraction) which are synthesized assessments rather than direct source claims. The baseline note does not separate these as distinct claims.

## Guide Impact

- **Chapter 00 (Principles)**: Evidence for new principle: "Design for AI-native failure modes" — context rot and instruction overload are structural, not incidental. Distinguishing AI-native from AI-assisted products changes reliability requirements. Also supports "build to understand, ship simple" as an engineering principle for agent systems.

- **Chapter 01 (Incident Response)**: Concrete architecture for AI-assisted incident investigation. Key claims to incorporate: (a) real-time visibility into agent reasoning is a hard requirement for live incidents; (b) mid-run human steering (injecting hypotheses, redirecting investigation) must be a first-class event; (c) sequential hypothesis testing creates unacceptable latency for incidents with multiple candidate causes; (d) the agent should never operate without information the human already has.

- **Chapter 03 (Runbooks and Agents)**: Multi-agent ops architecture patterns: (a) three execution models and when to use each; (b) reactive loop pattern (interrupt/resume, priority queue, lock serialization) for interactive agent systems; (c) `task_id === thread_id` identity convention for routing events; (d) durable supervisor / stateless sub-agent asymmetry for reliability without distributed complexity; (e) single-process simplification argument — IO-bound agent workloads don't need service boundaries.

- **Chapter 04 (Oncall and Toil)**: Investigation workflow (formulate hypotheses → spawn sub-agents → query logs/metrics → report findings → synthesize root cause) is a directly reusable pattern for on-call tooling. Priority queue pattern (user input > sub-agent results) applies to any interactive on-call agent.

## Extraction Notes

- Source is a single long-form blog post (~28 minute read) on PagerDuty's engineering blog. No sub-pages followed — article is self-contained with all architectural detail inline.
- Quotes extracted via WebFetch and spot-checked against rendered page. Key quotes are short (≤125 chars) and verified verbatim.
- Article cites six references (Freitas 2026, Jaroslawicz et al. 2025, LangChain Deep Agents, LangGraph async sub-agents docs, Liu et al. 2023, Google A2A protocol). Not independently fetched — cited here as they appear in source.
- Rich in architectural detail but light on quantitative metrics (no latency distributions, no accuracy/eval numbers, no cost data). One concrete number: "10+ minutes" for sequential diagnosis of moderately complex incident.
- No part of source was paywalled. Publicly accessible on PagerDuty Engineering Blog.
- Published June 24, 2026 — approximately 1 month before extraction. Architecture described is very recent and may still be evolving.
- This evaluation extraction was produced by Nemotron-3-Ultra-Free via OpenCode GitHub Action for quality comparison against the merged DeepSeek/Flash baseline (`blog-pagerduty-sre-agent-architecture.md`, issue #1). Do not merge — compare against baseline.