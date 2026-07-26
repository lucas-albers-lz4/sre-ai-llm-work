---
source_url: https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
source_type: blog-post
title: Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation
author: PagerDuty Engineering
date_published: 2026-06-24
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: emerging
issue: "#1-nemotron-3-ultra-free-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> PagerDuty Engineering details the architectural evolution from a single-agent SRE investigator to a multi-agent system with parallel fan-out, concurrent fan-in, real-time user interactivity, and mid-run steering — built by implementing a reactive interrupt/resume loop on LangGraph with a priority queue, task identity conventions, and an event transport layer.

## Source Context

- **Type**: blog-post
- **Author credibility**: PagerDuty Engineering team blog, authored by engineers who built the production SRE Agent. First-party account of architecture decisions, failures, and iterations. Not peer-reviewed; reflects one company's production experience.
- **Scope**: Covers the architectural journey from single-agent to multi-agent SRE investigation system, including context rot, instruction overload, LangGraph BSP limitations, reactive loop implementation (interrupt/resume, priority queue, lock, drain loop), three infrastructure primitives (task identity, event queue/transport, reactive loop), and the simplification to single-process deployment. Does not cover evaluation metrics, production incident data, or comparison with other multi-agent frameworks beyond LangChain Deep Agents.

## Extracted Claims

### Claim 1: AI-native products have fundamentally different failure modes and engineering trade-offs than AI-assisted products
- **Evidence**: Author's architectural reasoning; cites João Freitas' "Production AI Agents: Closing the Gaps Between Idea and Reality" as framing
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an existing system. In AI-native products, the AI is the system, which means the failure modes, the reliability requirements, and the engineering trade-offs are all different."
- **Our assessment**: Plausible architectural distinction. The claim frames the motivation for the multi-agent architecture but is a design philosophy rather than an empirically validated claim. No quantitative evidence provided.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: Cites Liu et al. 2023 (arXiv:2307.03172 "Lost in the Middle: How Language Models Use Long Contexts"); describes practical symptoms: "Beyond a certain threshold, model performance degrades as the context grows, not because the information isn't there but because the model struggles to weight it correctly. More data, worse decisions."
- **Confidence**: emerging
- **Quote**: "Beyond a certain threshold, model performance degrades as the context grows, not because the information isn't there but because the model struggles to weight it correctly. More data, worse decisions."
- **Our assessment**: The context rot phenomenon is documented in LLM literature (Liu et al. 2023). The claim that it creates a "hard ceiling" for single-agent investigation is the author's extrapolation — plausible but not independently validated. Newer models may shift the threshold.

### Claim 3: Instruction overload creates an inverse relationship between feature count and output quality in monolithic agents
- **Evidence**: Cites Jaroslawicz et al. 2025 (arXiv:2507.11538); describes practical symptom: "agents that worked well at a certain feature set started degrading as we added to it"
- **Confidence**: emerging
- **Quote**: "Research suggests there's an inverse relationship between instruction volume and output quality: as the prompt gets longer, the model's ability to follow any given instruction decreases."
- **Our assessment**: The cited paper (2025) is very recent; claim is plausible but the "inverse relationship" framing may overstate what the paper shows. Practical observation aligns with known prompt engineering challenges.

### Claim 4: Sequential synchronous execution in single-agent SRE investigation causes multi-minute diagnosis latency
- **Evidence**: Author's first-hand experience: "A single root cause analysis: formulate a hypothesis, search for evidence, evaluate – chain these together, and it could take several minutes. Sequential hypothesis testing multiplied that. A moderately complex incident with three or four candidate causes could take 10+ minutes to diagnose."
- **Confidence**: anecdotal
- **Quote**: "A single root cause analysis: formulate a hypothesis, search for evidence, evaluate – chain these together, and it could take several minutes. Sequential hypothesis testing multiplied that. A moderately complex incident with three or four candidate causes could take 10+ minutes to diagnose."
- **Our assessment**: Credible first-hand account of latency characteristics. No comparative benchmarks or measurements provided. "10+ minutes" is a reasonable estimate for sequential LLM tool-use chains.

### Claim 5: Lack of interactivity during agent execution was a structural failure, not a missing feature
- **Evidence**: Author's architectural analysis: "Users couldn't ask questions or add context while the agent was working... For a live incident, this wasn't just inconvenient — it meant the agent was operating without information the human already had."
- **Confidence**: emerging
- **Quote**: "Users couldn't ask questions or add context while the agent was working. If the on-call engineer knew the service had been deployed 10 minutes before the alert, they couldn't inject that. They had to wait for the agent to finish, then restart with the new context included. For a live incident, this wasn't just inconvenient — it meant the agent was operating without information the human already had."
- **Our assessment**: Strong architectural claim. The distinction between "missing feature" and "structural failure" correctly identifies that interactivity requires a different execution model (async, interruptible), not just an API endpoint.

### Claim 6: LangGraph's Bulk Synchronous Parallel (BSP) execution model prevents per-result reactivity in multi-agent orchestration
- **Evidence**: Technical analysis of LangGraph internals: "LangGraph, on which Deep Agents is built, executes with a Bulk Synchronous Parallel (BSP) model: it advances in supersteps, running a batch of work and then stopping at a synchronization barrier before the next batch begins. A parallel tool call is one superstep, so control only returns to the orchestrator once every tool in that batch has resolved."
- **Confidence**: settled
- **Quote**: "LangGraph, on which Deep Agents is built, executes with a Bulk Synchronous Parallel (BSP) model: it advances in supersteps, running a batch of work and then stopping at a synchronization barrier before the next batch begins. A parallel tool call is one superstep, so control only returns to the orchestrator once every tool in that batch has resolved."
- **Our assessment**: Accurate technical description of LangGraph's execution model (verifiable in LangGraph docs/source). This is a structural limitation of the framework, not a bug.

### Claim 7: Naive concurrent fan-out with LangGraph interrupt/resume suffers from race conditions when multiple sub-agents complete simultaneously
- **Evidence**: Author's experimental failure: "The first completion resumed the graph and triggered the main agent working loop. While the main agent was still processing, the second completion arrived and tried to resume the same graph. LangGraph either errored or started a fresh execution from scratch, which was worse because now we'd lost the state from the first arrival."
- **Confidence**: anecdotal
- **Quote**: "The first completion resumed the graph and triggered the main agent working loop. While the main agent was still processing, the second completion arrived and tried to resume the same graph. LangGraph either errored or started a fresh execution from scratch, which was worse because now we'd lost the state from the first arrival."
- **Our assessment**: Credible first-hand account of a race condition in LangGraph's interrupt/resume mechanism. The description of "fresh execution from scratch" losing state aligns with how checkpoint-based resumption works.

### Claim 8: A queue + lock around the resume call serializes concurrent sub-agent completions and prevents state corruption
- **Evidence**: Author's implemented solution: "The fix was a lock around the resume call. The drain loop held the lock while resuming, and the graph signaled through a callback when it had actually re-interrupted, releasing the lock. Now the drain loop could never issue a second resume until the first one had fully cycled back to a paused state."
- **Confidence**: anecdotal
- **Quote**: "The fix was a lock around the resume call. The drain loop held the lock while resuming, and the graph signaled through a callback when it had actually re-interrupted, releasing the lock. Now the drain loop could never issue a second resume until the first one had fully cycled back to a paused state."
- **Our assessment**: Sound concurrency pattern. The callback-based lock release is necessary because the graph's interruption point is asynchronous. This is a practical implementation detail, not a general theorem.

### Claim 9: User input must be a priority-0 event in a priority queue to enable mid-run steering ahead of buffered sub-agent results
- **Evidence**: Author's implementation: "User messages carried the highest priority, so they always jumped ahead of any buffered sub-agent results... Whenever a user event was sitting in the queue, it jumped the line and got processed before any backlog of sub-agent completions."
- **Confidence**: anecdotal
- **Quote**: "User messages carried the highest priority, so they always jumped ahead of any buffered sub-agent results... Whenever a user event was sitting in the queue, it jumped the line and got processed before any backlog of sub-agent completions."
- **Our assessment**: Correct UX requirement for real-time incident response. Priority inversion (user input stuck behind sub-agent results) would defeat the purpose of interactivity.

### Claim 10: The convention `thread_id === task_id` and `parent_task_id` on sub-agent events is the single most important convention for cross-agent communication
- **Evidence**: Author's architectural reflection: "This sounds trivial, yet it was the single most important convention in the system. It meant that when a sub-agent published a completion event carrying parent_task_id: task-001, the parent agent immediately knew which LangGraph thread to resume. No lookup table. No correlation logic."
- **Confidence**: anecdotal
- **Quote**: "This sounds trivial, yet it was the single most important convention in the system. It meant that when a sub-agent published a completion event carrying parent_task_id: task-001, the parent agent immediately knew which LangGraph thread to resume. No lookup table. No correlation logic."
- **Our assessment**: Strong design principle. Using identifiers as direct routing keys eliminates coordination infrastructure. This is a known pattern in actor systems and distributed tracing.

### Claim 11: An event transport layer requires both PubSub broadcast (for real-time delivery) and a durable event store indexed by task_id (for late-joining clients and crash recovery)
- **Evidence**: Author's architecture: "PubSub alone was fire-and-forget — it wouldn't reach clients who joined after an event was emitted. The store covered late-joining clients, catching up on an in-progress investigation. In production, this would need to be a fully durable store (thinking about Kafka persistence or a database) to survive pod restarts and handle crash recovery properly."
- **Confidence**: emerging
- **Quote**: "PubSub alone was fire-and-forget — it wouldn't reach clients who joined after an event was emitted. The store covered late-joining clients, catching up on an in-progress investigation. In production, this would need to be a fully durable store (thinking about Kafka persistence or a database) to survive pod restarts and handle crash recovery properly."
- **Our assessment**: Standard distributed systems pattern (dual-write to broadcast + log). The author correctly identifies production hardening needs (durability, crash recovery) beyond the prototype.

### Claim 12: Progress reporting via LangGraph callbacks injected through `configurable` dict keeps graph nodes decoupled from transport concerns
- **Evidence**: Author's implementation detail: "Progress reporting from graph nodes flowed through callbacks injected via LangGraph's configurable dict, keeping the graph nodes entirely decoupled from transport."
- **Confidence**: settled
- **Quote**: "Progress reporting from graph nodes flowed through callbacks injected via LangGraph's configurable dict, keeping the graph nodes entirely decoupled from transport."
- **Our assessment**: Accurate description of LangGraph's callback mechanism via `configurable`. Good separation of concerns.

### Claim 13: The multi-agent prototype required seven distinct infrastructure components: webhook callback path, PubSub broadcast, durable event store per agent, interrupt-and-resume graph, drain loop, lock, and priority queue
- **Evidence**: Author's retrospective: "To coordinate between supervisor and sub-agents in production, we would have to build multiple services: a webhook callback path, a PubSub broadcast, a durable event store for each agent, an interrupt-and-resume graph, a drain loop, a lock, and a priority queue."
- **Confidence**: anecdotal
- **Quote**: "To coordinate between supervisor and sub-agents in production, we would have to build multiple services: a webhook callback path, a PubSub broadcast, a durable event store for each agent, an interrupt-and-resume graph, a drain loop, a lock, and a priority queue."
- **Our assessment**: Accurate accounting of the prototype's complexity. The list reflects the distributed-systems assumptions (separate processes, webhooks, PubSub) that the author later questions.

### Claim 14: Sub-agents in SRE investigation are overwhelmingly I/O-bound (log API calls, metrics API calls, model inference), making distributed deployment unnecessary
- **Evidence**: Author's retrospective simplification: "Our sub-agents do almost none of that. An investigation is overwhelmingly IO — call a log API and wait, call a metrics API and wait, hand the text to the model and wait."
- **Confidence**: emerging
- **Quote**: "Our sub-agents do almost none of that. An investigation is overwhelmingly IO — call a log API and wait, call a metrics API and wait, hand the text to the model and wait."
- **Our assessment**: Strong architectural insight. I/O-bound workloads with shared external dependencies (APIs, model endpoints) gain little from process isolation. Single-process with async concurrency is simpler and lower-latency.

### Claim 15: Three execution models for sub-agents exist: sequential (sum of latencies), parallel wait-for-all (max latency, orchestrator idle), and parallel fan-out with concurrent fan-in (max latency, orchestrator active, per-result reactivity)
- **Evidence**: Author's taxonomy with timeline diagrams and trade-off analysis
- **Confidence**: settled
- **Quote**: "There are three obvious ways to run N sub-agents and combine their results, and each has a different cost." (followed by detailed descriptions of all three models)
- **Our assessment**: Clear, correct taxonomy of concurrency patterns. The third model (concurrent fan-in) is the correct target for interactive multi-agent systems.

### Claim 16: LangChain Deep Agents' sub-agents feature (at the time of writing) lacked async sub-agents and operated within LangGraph's BSP model, preventing per-result reactivity
- **Evidence**: Author's evaluation: "At the time, there was no async-subagents feature in the package — that has since been added and bundled in. We considered whether async sub-agents would have solved our problem, too; more on that later." and "Within this framework-managed orchestration, there is no way to say 'do something each time a single tool finishes, before the others have.'"
- **Confidence**: settled
- **Quote**: "At the time, there was no async-subagents feature in the package — that has since been added and bundled in. We considered whether async sub-agents would have solved our problem, too; more on that later."
- **Our assessment**: Accurate historical claim about LangChain Deep Agents' capabilities at the time. The async-subagents feature was added later (per LangChain changelog). Even with async sub-agents, the BSP model would still batch completions at superstep boundaries unless the framework exposes per-tool callbacks.

### Claim 17: The A2A protocol inspired the agent lifecycle state machine (working → completed | failed | canceled)
- **Evidence**: Author's citation: "Each agent wrapped its logic in a simple lifecycle: working → completed | failed | canceled. Inspired by the A2A protocol."
- **Confidence**: anecdotal
- **Quote**: "Each agent wrapped its logic in a simple lifecycle: working → completed | failed | canceled. Inspired by the A2A protocol."
- **Our assessment**: Plausible. The A2A (Agent-to-Agent) protocol defines task states including working, completed, failed, canceled. The author adopted a compatible state machine.

## Concrete Artifacts

```
# Task identity convention (JavaScript/TypeScript-like pseudocode from source)
Main Agent (task_id: task-001, thread_id: task-001)
    │
    ├── Sub-Agent 1 (task_id: sub-1, parent_task_id: task-001)
    │     └→ completes → publishes event with parent_task_id: task-001
    │                  → parent agent resumes thread_id: task-001
    ├── Sub-Agent 2 (task_id: sub-2, parent_task_id: task-001)
    └── Sub-Agent 3 (task_id: sub-3, parent_task_id: task-001)
```

```
# Agent lifecycle states (inspired by A2A protocol)
working → completed | failed | canceled
```

```
# Priority queue event structure
User input event:     { priority: 0, type: "user_input", payload: {...} }
Sub-agent result:     { priority: 1, type: "sub_agent_result", payload: {...} }
```

```
# Reactive loop node structure (6 nodes in LangGraph)
accept_event → route_event → handle_sub_agent_result | handle_user_input → plan → spawn_sub_agent → accept_event (interrupt)
```

```
# Event transport dual-write pattern
# 1. PubSub broadcast (real-time)
pubsub.publish(channel, event)

# 2. Durable event store (indexed by task_id)
event_store.append(task_id, event)
```

## Cross-References

### Corroborates
- **source-notes/blog-pagerduty-production-ai-agent-gaps.md** (Claims 3, 5, 8) — João Freitas' precursor framing article, explicitly cited by name in Claim 1 of this note ("cites João Freitas' 'Production AI Agents: Closing the Gaps Between Idea and Reality' as framing"). Same company (PagerDuty), same domain (production multi-agent systems), and the source article itself describes this as the foundational piece. Specific overlaps: Claim 3 of the Freitas note (context fatigue — "the early parts of your prompt start losing probabilistic weight as more tokens accumulate") directly parallels this note's Claim 2 (context rot — "Beyond a certain threshold, model performance degrades as the context grows…More data, worse decisions") — the same failure mode under different names, both citing Liu et al. 2023. Claim 8 of the Freitas note (architecture evolution: single-agent → supervisor → hierarchical, "earn complexity rather than starting with it") parallels this note's full architectural journey from monolith to multi-agent and Claim 14's simplification argument. The two articles are companion pieces: Freitas covers evaluation, metrics, guardrails, and UX; Vasylkovskyi et al. cover implementation primitives (reactive loop, identity, transport, durability model).
- **source-notes/blog-pagerduty-sre-agent-architecture.md** (same source URL, production Miner extraction by Claude Opus) — This note is a `miner-eval` extraction using Nemotron 3 Ultra Free against the same source URL as the production Miner note. It serves as a model-comparison extraction for LLM evaluation purposes, not an independent source discovery or duplicate submission. The production Miner note may contain equivalent or more detailed extraction; this note represents what the Nemotron model produced independently.
- **source-notes/blog-incidentio-ai-sre-incident-run.md** (Claim 1, 3, 4) — Incident.io's AI SRE also demonstrates parallel multi-source investigation (deploys, telemetry, errors, past incidents, code, Slack), human-AI parallel investigation with context sync, and terminal integration via Claude Code. Corroborates the pattern of AI agents doing deep parallel investigation during live incidents with human-in-the-loop.

### Contradicts
- None identified. The PagerDuty architecture (multi-agent, reactive loop, single-process simplification) and incident.io's approach (Claude Code + MCP, parallel investigation) are complementary — different implementation strategies for similar capabilities.

### Extends
- **source-notes/docs-google-sre-prodcast-05-04-del-cid-ai-sre.md** (Claim 1, 2, 3) — Google's "AI for SRE" horizontal team builds shared tooling (early outage detection from support cases, incident analysis dashboards, incident similarity matching). PagerDuty's SRE Agent extends this pattern into a real-time, interactive, multi-agent investigation engine that runs during live incidents rather than as batch analysis.

### Novel
- The **reactive interrupt/resume loop with priority queue + lock** implemented on LangGraph for multi-agent orchestration — a concrete pattern for per-result reactivity in a BSP-based framework.
- The **task_id === thread_id convention** as a zero-coordination routing mechanism for parent/child agent communication.
- The **dual-write event transport** (PubSub + durable store) specifically for agent event streams with late-join support.
- The **architectural simplification argument**: SRE investigation sub-agents are I/O-bound, making distributed deployment (webhooks, PubSub, separate processes) unnecessary complexity — single-process async concurrency suffices.
- The **three-model taxonomy** (sequential / parallel-wait-all / parallel-fan-out-concurrent-fan-in) with explicit latency and interactivity trade-offs for multi-agent SRE investigation.

## Guide Impact

- **Chapter 02 (Harness Engineering / Agent Architectures)**: Add the parallel fan-out + concurrent fan-in pattern as a recommended architecture for interactive multi-agent investigation. Cite the reactive loop (interrupt/resume, priority queue, lock, drain loop) as a concrete implementation pattern for LangGraph-based systems. Note the task_id === thread_id convention as a design principle.
- **Chapter 02**: Add the "AI-native vs AI-assisted" framing as a design principle — when the agent *is* the system, reliability requirements change (interactivity, cancellation, observability become structural).
- **Chapter 03 (Reliability / Failure Modes)**: Cite context rot (Liu et al. 2023) and instruction overload (Jaroslawicz et al. 2025) as documented failure modes for monolithic LLM agents with growing context/instructions.
- **Chapter 04 (Human-AI Collaboration)**: Cite the priority-queue user-input pattern as a concrete mechanism for mid-run human steering of agent execution. The "structural failure, not missing feature" distinction belongs here.
- **Chapter 05 (Infrastructure / Deployment)**: Cite the single-process simplification argument — I/O-bound agent workloads don't need distributed deployment; the seven-component distributed prototype was over-engineered.

## Extraction Notes

- Source read in full (28-minute read per blog metadata). All claims extracted from the main article body; no sub-pages followed (the article is self-contained).
- The article includes architecture diagrams (referenced as images) that were not directly accessible; diagram descriptions in alt-text/captions were used for Claims 6, 7, 8, 9.
- Two academic citations (Liu et al. 2023, Jaroslawicz et al. 2025) were referenced but not verified — marked as "emerging" confidence where claims depend on them.
- The author notes LangChain Deep Agents has since added async-subagents; this evaluation reflects the architecture *at the time of writing*.
- The "production hardening" notes (durable event store, crash recovery) are explicitly marked by the author as future work — not yet validated in production.
- Cross-reference candidates from `miner-related-notes.md` were all evaluated (10 candidates total). The candidate file is not persisted to the repo; the numbering below reflects the file's order at extraction time: candidate 1 (`blog-pagerduty-sre-agent-architecture.md`, same source URL) cited; candidate 4 (`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`) noted as weakly extends; candidate 9 (`blog-incidentio-ai-sre-incident-run.md`) cited; candidates 2, 3, 5, 6, 7, 8, 10 dismissed — these had low lexical/domain overlap with the source (different companies or problem domains). Note: the automated candidates did NOT include `blog-pagerduty-production-ai-agent-gaps.md` (the João Freitas precursor article) — the Miner separately identified this connection via the explicit citation in Claim 1 of the source text and has added it as a manual cross-reference under Corroborates (see above).
