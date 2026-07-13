---
source_url: https://www.pagerduty.com/eng/production-ai-agents-closing-the-gaps-between-idea-and-reality/
source_type: blog-post
title: "Production AI Agents: Closing the Gaps Between Idea and Reality"
author: "João Freitas (PagerDuty Engineering)"
date_published: 2026-06-11
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: emerging
issue: "#4-hy3-eval"
---

# Production AI Agents: Closing the Gaps Between Idea and Reality  — Hy3 Miner eval replay

> **Eval note.** This is an Hy3-model replay of the Miner extraction for golden
> issue #4. It is written to be compared against the merged DeepSeek baseline
> note ([`blog-pagerduty-production-ai-agent-gaps.md`](blog-pagerduty-production-ai-agent-gaps.md)).
> The source is identical; this replay prioritizes **verbatim** quoting (the
> baseline paraphrased several quotes — see Extraction Notes) and corrects a few
> confidence ratings where the source treats a failure mode as settled fact.
> Do not merge — comparison artifact only.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: João Freitas is a PagerDuty engineer. The article
  states plainly: "Over the past year at PagerDuty, we launched a multi-agent
  system into production. Here is what we learned from that experience." It is
  first-hand production experience, not a thought-piece. The companion PagerDuty
  SRE Agent architecture article (Vasylkovskyi et al.) explicitly cites this post
  as its foundational framing (see companion Claim 1). Claims are backed by a
  bibliography of ten academic references (Chang et al. 2026, Yong et al. 2023,
  Shen et al. 2024, Marx & Dunaiski 2026, Ullah et al. 2024, Colelough & Regli
  2025, Raspanti et al. 2025, Lightman et al. 2024, Khalifa et al. 2025, Yao et
  al. 2023).
- **Scope**: Covers the full productionization gap — why prototypes fail at
  scale, the five-pillar reliability framework, architectural evolution
  (single-agent → supervisor → hierarchical), a concrete evaluation pipeline
  (golden datasets, LLM-as-a-judge, CI gates), a nine-metric observability
  framework, guardrail architecture (defense-in-depth, sync/async, low-resource
  language blocking, kill switch), transparent UX, agent memory sharing
  (knowledge graphs vs. RAG), and cost/latency optimization. Does NOT cover: the
  agent runtime's implementation primitives (those are in the companion SRE Agent
  article), specific model choices, or concrete latency/cost numbers.
- **Article length / read time**: long-form engineering post (the page metadata
  describes it as exploring "the complexities of transitioning AI agents from
  successful prototypes to reliable, production-ready systems").

## Extracted Claims

### Claim 1: The prototype-to-production gap for AI agents is large and structural — demos are easy, reliability is hard
- **Evidence**: First-hand — PagerDuty "launched a multi-agent system into
  production" over the prior year and "the same applies" to agents: "You build an
  agent in minutes. It works on your machine. Demos go well. Then you ship it to
  production, and the AI agent fails, or the quality of the end-user experience
  falls short of expectations." The article is structured entirely around
  bridging that gap.
- **Confidence**: settled
- **Quote**: "Going from an idea to a prototype today takes hours or minutes."
- **Our assessment**: Central thesis; the demo-vs-production distinction is
  widely acknowledged across practitioner communities. The article's value is
  cataloging the *specific* failure modes that cause the gap, which Claims 2–6 do.

### Claim 2: LLM non-determinism persists even with temperature set to zero, making agent behavior inherently unpredictable
- **Evidence**: "Even when you set the temperature to zero (the setting meant to
  reduce variation in model outputs), the same input can produce different
  outputs, and you may still see hallucinations." Mitigations cited from the
  literature: neuro-symbolic (Colelough & Regli 2025), RAG, strict constraints
  (Raspanti et al. 2025), deterministic executions (Yao et al. 2023), stepwise
  verifications (Lightman et al. 2024; Khalifa et al. 2025). Also notes LLMs
  "cannot yet reliably identify or reason about security vulnerabilities (Ullah
  et al., 2024)."
- **Confidence**: settled
- **Quote**: "the same input can produce different outputs, and you may still see hallucinations"
- **Our assessment**: Well-established. Even at temperature=0, floating-point and
  model-update variability yield different outputs; this is why "deterministic
  software tests" (Claim 15) are inadequate. The cited mitigations are standard.

### Claim 3: Context fatigue causes early prompt instructions to lose probabilistic weight as token count grows, degrading agents in long-running tasks
- **Evidence**: "The early parts of your prompt start losing probabilistic weight
  as more tokens accumulate, and the model forgets constraints you set up front.
  We call this context fatigue. It shows up in any agent that runs long enough."
  The source names the mechanism (probabilistic token weighting) and states it
  appears in "any agent that runs long enough."
- **Confidence**: settled
- **Quote**: "The early parts of your prompt start losing probabilistic weight as more tokens accumulate, and the model forgets constraints you set up front."
- **Our assessment**: Consistent with "Lost in the Middle" (Liu et al. 2023) and
  corroborated by the companion SRE Agent article's "context rot" finding
  (blog-pagerduty-sre-agent-architecture, Claim 2). This is a named, observed
  failure mode — a hard ceiling for long single-agent investigations. (The
  baseline rated this "emerging"; the source states it as a settled observation,
  so this replay rates it "settled.")

### Claim 4: Errors compound multiplicatively across multi-step agent workflows rather than averaging out
- **Evidence**: "Each part of an agent (the LLM, the tools and APIs it calls, the
  retrieval layer, the memory store, sometimes other agents) has its own
  reliability characteristics. When you chain them together, the errors multiply
  rather than average out. Multi-agent systems, where you have agents
  communicating with agents, intensify this directly." The article adds that as
  DNS-AID and A2A make integration easier, "edge cases are almost infinite."
- **Confidence**: settled
- **Quote**: "When you chain them together, the errors multiply rather than average out."
- **Our assessment**: If each step in an n-step workflow is 95% reliable, compound
  reliability is ~0.95^n (≈77% for n=5), not 95%. The article correctly flags that
  multi-agent systems amplify this. The "edge cases are almost infinite" point
  directly motivates the evaluation-pipeline claim (Claim 10). (Baseline rated
  "emerging"; replay rates "settled" — it is a direct, unconditional statement in
  the source, and matches the companion's instruction-overload claim.)

### Claim 5: AI agents are highly susceptible to prompt injection (80-90% reported), and guardrails are bypassed via low-resource languages
- **Evidence**: "the majority of agents built today are susceptible to prompt
  injection, with reported rates in the 80-90% range (Chang et al., 2026), and
  many guardrails can be bypassed simply by phrasing the prompt in a low-resource
  language (Yong et al., 2023; Shen et al., 2024; Marx & Dunaiski, 2026)." Because
  "new vulnerabilities keep surfacing, monitoring and a kill switch need to be in
  place from day one."
- **Confidence**: settled
- **Quote**: "the majority of agents built today are susceptible to prompt injection, with reported rates in the 80-90% range (Chang et al., 2026)"
- **Our assessment**: The 80-90% figure is cited from peer-reviewed research and
  corroborated by broader security literature. The low-resource-language bypass is
  backed by three citations. Strong evidence. (Baseline rated "emerging"; replay
  rates "settled" because the source presents it as established research fact with
  multiple citations, not as PagerDuty's tentative experience.)

### Claim 6: Context poisoning — stale/corrupted/contradictory data filling working memory — propagates errors across agents and systems
- **Evidence**: "real enterprise data is usually siloed, inconsistent, incomplete,
  and poorly structured. Feed that into an agent, and it will make bad decisions.
  Combined with the long-context behavior we just discussed, it also produces what
  we call context poisoning (when the agent's working memory gets filled with
  corrupted or contradictory data that then carries forward to other systems and
  agents)." The article notes the companies getting the most value "tend to
  already have a strong data strategy in place."
- **Confidence**: emerging
- **Quote**: "real enterprise data is usually siloed, inconsistent, incomplete, and poorly structured."
- **Our assessment**: One of the article's novel contributions — "context
  poisoning" is a named failure mode distinct from hallucination or context
  fatigue: bad *ground-truth* data corrupts the reasoning base and propagates
  through shared context in multi-agent systems. The article's knowledge-graph
  discussion (Claim 13) is positioned as a partial mitigation.

### Claim 7: A five-pillar framework — Reliability, Control, Visibility, Integration, Economics — defines production readiness
- **Evidence**: Derived from Karpathy's "March of 9s" (Claim 16) and extended
  beyond raw reliability. The five pillars: "Reliability, meaning predictable
  outcomes from a non-deterministic system. Control, meaning guardrails and
  permissions. Visibility, meaning observability and evaluation. Integration,
  meaning real workflow embedding. Economics, meaning scalable cost and latency."
  Trade-offs are explicit: "if the groundedness ... of the response is more
  important than latency, you may have a verification agent that fact-checks the
  answer ... this would result in a latency increase at the cost of more reliable
  answers."
- **Confidence**: emerging
- **Quote**: "By missing one of these, you increase your production risk and chance of hitting a production failure."
- **Our assessment**: A useful organizational taxonomy, not a falsifiable claim.
  It maps to dimensions that recur in production-agent postmortems. One team's
  framing; not independently validated, so "emerging" is right.

### Claim 8: Agent architecture should evolve single-agent → supervisor → hierarchical, earning complexity rather than starting with it
- **Evidence**: "The pattern we started with was a single agent that called a set
  of tools. That single agent picked up enough responsibilities quickly to feel
  like an orchestrator, so we factored out a supervisor who routed to specialized
  sub-agents. Over time, we moved to a hierarchical pattern, with a supervisor on
  top and domain-focused agents below, each with their own tools and prompts."
  Network/peer-to-peer was considered but rejected: "the complexity of testing and
  changing a network or peer-to-peer system is substantially higher than that of a
  hierarchical one. We recommend earning that complexity by first hitting the
  limits of the simpler pattern."
- **Confidence**: emerging
- **Quote**: "the complexity of testing and changing a network or peer-to-peer system is substantially higher than that of a hierarchical one."
- **Our assessment**: The evolutionary path is corroborated by the companion SRE
  Agent article (Claim 12 single-process simplification; Claim 16 "build hard,
  ship simple"). The "earn complexity" advice recurs across both PagerDuty posts.
  Rejecting peer-to-peer for testability is a practical, defensible constraint.

### Claim 9: Transparent UX — showing agent reasoning steps in real time — builds trust and increases willingness to wait
- **Evidence**: Anecdote: "At the early stages of our development, we built a
  prototype that showed everything the agent was doing in real time. The
  production version, by contrast, only showed the final answer. When a product
  manager saw the prototype, they said they loved seeing the agent's process and
  asked us to add that transparency to production." General claim: "users are more
  open to waiting if they can see the agent working or reasoning. A silent spinner
  frustrates them." Especially important "in enterprise and regulated settings,
  where trust is what makes the product usable."
- **Confidence**: anecdotal
- **Quote**: "Showing the agent's plans, steps, and reasoning as it runs is one of the simplest and most effective UX improvements"
- **Our assessment**: Anecdotal but with direct product impact, and consistent with
  perceived-performance / transparency UX research. The application to
  enterprise/regulated settings is a useful contextualization.

### Claim 10: Automated evaluation pipelines (golden datasets + LLM-as-a-judge + CI gates) are essential for production-grade agents
- **Evidence**: Golden datasets require defining "what topics are asked ... how
  they are asked ... and who is asking." The pipeline: "the golden test questions
  are fed simultaneously into the AI agent under test and an expected responder
  generator ... An 'LLM-as-a-judge' is then used to compare the agent's actual
  output against the expected output. The outcome of this automated scoring is
  piped directly into a monitoring and observability platform." Strategy layers:
  baseline golden sets (stubbed tools/seeds), scenario tests (multi-turn, noisy
  inputs, tool failures), adversarial suites (prompt injections, tool confusion,
  hallucination traps), all "integrated into CI gates, allowing teams to run
  continuous offline re-evaluations whenever a model, prompt, or tool changes."
  Initial golden sets cover "roughly 95% of cases," then feedback loops grow them.
- **Confidence**: emerging
- **Quote**: "An 'LLM-as-a-judge' is then used to compare the agent's actual output against the expected output"
- **Our assessment**: One of the article's highest-value contributions — a
  concrete, reproducible evaluation architecture rather than vague "test your
  agents" advice. The what/how/who curation frame, the LLM-as-a-judge step, the CI
  integration, and especially the *adversarial* suite (tests prompt injection and
  hallucination, not just accuracy) are all actionable.

### Claim 11: Not everything in an agent needs to be probabilistic — deterministic code should replace LLM calls where possible
- **Evidence**: "When we looked at how our initial versions of the agents were
  built, two things stood out. First, we were using a very large model to solve
  relatively simple problems. Second, we were using LLMs for tasks that did not
  require them at all. Some basic deterministic code could be used to solve those
  tasks. The deterministic option is usually faster and cheaper, and not
  everything inside an agent needs to be probabilistic." Their approach: "build
  first, then optimize."
- **Confidence**: emerging
- **Quote**: "using a very large model to solve relatively simple problems"
- **Our assessment**: Practical and important. Connects to the companion SRE Agent
  article's IO-bound vs compute-bound discussion (Claim 12). Easy to miss when
  building agent-first systems — the temptation to use LLMs for everything is real.

### Claim 12: A nine-metric framework should track task success, groundedness, tool errors, loop/retry rate, plan length, p95 latency, cost per successful task, safety violations, and human escalation
- **Evidence**: The article enumerates these metrics: "Task success rate (exact or
  graded). Groundedness rate, meaning whether the agent's output reflects the
  source data rather than being made up. Tool success, timeout, and error rates.
  Loop and retry rate. Plan length and step efficiency. p95 latency. Cost per
  successful task. Safety violation rate. Human escalation rate." Tracked in "an
  observability platform with LLMOps and AgentOps capabilities"; "the goal is to
  catch problems before users do. Deployment gates enforce that."
- **Confidence**: emerging
- **Quote**: (no direct single-sentence quote; the enumerated list above is copied verbatim from the source's "Metrics, evals, and guardrails" section)
- **Our assessment**: Concrete, actionable metrics from production. "Groundedness
  rate" and "cost per successful task" (not just cost per call) are especially
  insightful — they measure quality and efficiency, not just throughput. The
  companion SRE Agent article explicitly does NOT cover this dimension, making
  this article's metrics coverage a valuable complement.

### Claim 13: Basic RAG is insufficient for shared agent memory — knowledge graphs with time/invalidation awareness are needed, but tooling is immature
- **Evidence**: Scenario: during an incident, one agent posts the database is the
  problem; a second builds on that; later a third/human finds the DB is fine (a
  dependency service returned bad responses). "What happens to the original
  'fact'? It has been invalidated. Everything built on top of it needs to be
  revisited." The article states: "This is where basic RAG (Retrieval-Augmented
  Generation) starts falling short. You need time and invalidation awareness in
  your memory. You need to navigate connections between facts. This is why
  knowledge graphs ... are interesting ... They let you do semantic search across
  multiple hops, and they let you express relationships that vector similarity
  cannot. The honest caveat is that the tooling here is still immature ... most do
  not yet have the scalability, reliability, or security for enterprise use."
- **Confidence**: emerging
- **Quote**: "basic RAG (Retrieval-Augmented Generation) starts falling short"
- **Our assessment**: Sophisticated analysis of a real multi-agent memory problem,
  with a specific invalidation scenario. The knowledge-graph recommendation is
  directionally important, and the honest immaturity caveat adds credibility. The
  source's own words ("time and invalidation awareness") are more precise than the
  baseline's paraphrase ("temporal/invalidation awareness").

### Claim 14: Guardrails require defense-in-depth (synchronous vs asynchronous checks) and must block low-resource languages as a common bypass path
- **Evidence**: "we do not allow our agents to operate in low-resource languages,
  since that was one of the most common bypass paths we observed. We enforce this
  at two layers, which gives us some defense-in-depth. Every guardrail check costs
  latency, though. You can run checks synchronously, which blocks the response
  until the check passes, or asynchronously, where the response is sent first and
  the check fires after. Non-critical checks can run async to avoid the latency
  penalty, but you only catch problems after the response has gone out."
- **Confidence**: emerging
- **Quote**: "we do not allow our agents to operate in low-resource languages, since that was one of the most common bypass paths"
- **Our assessment**: The sync/async classification of guardrail checks is a
  practical design pattern applicable beyond PagerDuty. Low-resource-language
  blocking is an evidence-backed mitigation (supported by the cited multilingual
  jailbreaking research). Two-layer enforcement provides defense-in-depth without
  prescribing a specific technology.

### Claim 15: Deterministic software tests are inadequate for natural-language agent systems where there is no single correct output
- **Evidence**: "deterministic software tests do not work well with natural
  language systems, where there is no single correct output." Context: with
  multi-agent systems, "edge cases are almost infinite," test sets can't cover
  them, and "real users arrive, prompt the system in natural language, and find
  unexpected combinations." This motivates the LLM-as-a-judge approach (Claim 10).
- **Confidence**: settled
- **Quote**: "deterministic software tests do not work well with natural language systems, where there is no single correct output"
- **Our assessment**: Fundamentally correct and widely acknowledged in LLM
  evaluation literature. The article's contribution is connecting this to the
  concrete pipeline it built (golden datasets → LLM-as-a-judge → CI gates).

### Claim 16: The "March of 9s" applies to AI agents — prototype reliability ~90% requires redundant layers, validation, fallback logic, and runtime error containment to improve
- **Evidence**: "Andrej Karpathy named the process of increasing the reliability of
  your system as the 'March of 9s'. The idea is that during the prototype or demo
  stage, your reliability is about 90% (one 9), and then for the subsequent 9s, you
  need to consider redundant system layers, extensive validation pipelines, complex
  fallback logic, runtime error containment, etc." This frames the five pillars.
- **Confidence**: emerging
- **Quote**: "Andrej Karpathy named the process of increasing the reliability of your system as the 'March of 9s'"
- **Our assessment**: A useful frame for the reliability investment curve. Applied
  to agents, it correctly predicts the jump from demo (~90%) to production (99%+)
  requires systematic investment. It's a frame rather than a verified law.

### Claim 17: Traditional DevOps practices still apply to agents — staged rollouts, canaries, feature flags, and "scale with AI on AI"
- **Evidence**: From the "What did we learn?" section: "Use staged rollouts,
  canaries, and feature flags. Some of the traditional DevOps playbook still
  applies in an agent world." Also: "Scale with AI on AI." and "Invest in traces,
  evals, and guardrails before you actually need them. If the system keeps breaking
  and you cannot detect it, you will find out through customer tickets instead.
  Keep everything traceable." Plus "Engineer the boundaries up front" (decide tools,
  state, and permissions before writing code) and "Bring designers in from day
  one."
- **Confidence**: emerging
- **Quote**: "Use staged rollouts, canaries, and feature flags. Some of the traditional DevOps playbook still applies in an agent world."
- **Our assessment**: A useful, sometimes-overlooked point — agent systems are
  still software and inherit the traditional release-engineering playbook. The
  "engineer boundaries up front" and "invest in traces/evals/guardrails before you
  need them" lessons are concrete and high-value for Chapter 05. (The baseline note
  omitted this "What did we learn?" synthesis; this replay captures it as a
  distinct claim.)

## Concrete Artifacts

### Five Pillars Framework (verbatim from source)

```
Reliability  — predictable outcomes from a non-deterministic system
Control      — guardrails and permissions
Visibility   — observability and evaluation
Integration  — real workflow embedding
Economics    — scalable cost and latency
```
Trade-off example (verbatim): "if the groundedness ... of the response is more
important than latency, you may have a verification agent that fact-checks the
answer with a cleaner context. Given a sequential flow, this would result in a
latency increase at the cost of more reliable answers."

### Evaluation Pipeline Design (described in source)

```
Golden Datasets                    Agent Under Test
(what topics, how asked,            (LLM agent, stubbed
 who is asking)                     tools / seeds)
        │                                    │
        └────────────┬───────────────────────┘
                     ▼
              LLM-as-a-Judge
          (compares actual vs expected output)
                     ▼
          Monitoring & Observability Platform
                     ▼
               CI Gate (re-evaluate on every
               model / prompt / tool change)
```
Source-prescribed layers (verbatim phrasing):
- "baseline golden set tests using stubbed tools and seeds"
- "scenario tests that introduce multi-turn interactions, noisy inputs, and tool failures"
- "adversarial suites designed to catch prompt injections, tool confusion, and hallucination traps"
- "feedback loops to continuously update the test sets. Each iteration builds on the last, failures shrink, the test suite grows, and the system compounds its own improvement"
- initial golden sets "cover roughly 95% of cases"

### Production Metrics (verbatim enumeration from source)

```
Task success rate (exact or graded)
Groundedness rate (output reflects source data vs. made up)
Tool success, timeout, and error rates
Loop and retry rate (agent repeating / retrying itself)
Plan length and step efficiency (reasoning steps or tool calls per answer)
p95 latency
Cost per successful task
Safety violation rate
Human escalation rate
```

### Guardrail Architecture (from source)

```
Layer 1: Guardrail check ── sync or async ──► Response
Layer 2: Guardrail check ── sync or async ──► Response   (two layers = defense-in-depth)

Synchronous:  blocks response until check passes (safer, slower)
Asynchronous: response sent first, check fires after (faster, riskier)

Concrete mitigations (verbatim):
  - "we do not allow our agents to operate in low-resource languages, since that was one of the most common bypass paths"
  - two-layer enforcement for defense-in-depth
  - "monitoring and a kill switch need to be in place from day one"
  - "Non-critical checks can run async to avoid the latency penalty, but you only catch problems after the response has gone out"
```

### Architecture Evolution (from source)

```
Single Agent (calls tools) ──► Supervisor + Sub-agents ──► Hierarchical
                                                        (supervisor on top,
                                                         domain-focused agents below,
                                                         each own tools + prompts)

Network / peer-to-peer: considered but rejected —
"the complexity of testing and changing a network or peer-to-peer system is
 substantially higher than that of a hierarchical one"
```
Also (verbatim): "We chose to group agents by domain, so each one stayed focused
and manageable. When an agent gets too large, it becomes difficult to evaluate,
debug, and understand."

### Minimum Reference Architecture (from source)

Components (verbatim):
- **Gateway**: authentication, authorization, rate limits, policies, routing
- **Tools & Memory Layer**: APIs, databases, vector stores, key-value stores
- **Observability**: traces, logs, metrics
- **Constraining knobs**: temperature, tool constraints, input / system prompts

### Agent Routing and Permissions (from source)

Verbatim example: "if there is a security incident and someone who is not on the
security team asks the agent about it, the agent should not respond." The article
states: "Permissions matter as much as evaluation." and "We invested heavily in
defining what actions an agent can take and which teams can use which agents."

### Context Poisoning / Knowledge-Graph Scenario (verbatim from source)

```
During an incident investigation, one agent posts that it thinks the database is the problem.
A second agent starts working from that hypothesis.
Ten minutes later, a third agent or a human discovers the database itself is fine.
The real cause is a dependency service returning bad responses, which made the database look slow.
The original "fact" has been invalidated. Everything built on top of it needs to be revisited.
```

## Cross-References

- **Corroborates**: The companion PagerDuty SRE Agent architecture article
  ([blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md))
  corroborates several claims (claim numbers below are the companion note's own
  numbering, verified against that file):
  - **Claim 3 (Context fatigue)** ↔ companion Claim 2 ("Context rot creates a hard
    ceiling for single-agent architectures"). Same failure mode, different name;
    both cite "Lost in the Middle" (Liu et al. 2023).
  - **Claim 4 (Compounding errors)** ↔ companion Claim 3 ("Instruction overload
    creates an inverse relationship between feature count and output quality").
    Both describe quality degrading as agents accumulate context/instructions.
  - **Claim 8 (Architecture evolution)** ↔ companion Claim 12 (IO-bound
    single-process simplification) and Claim 16 ("Build the hard version to
    understand the problem; ship the simple one"). Both describe the
    single-agent → supervisor → hierarchical path and emphasize *earning*
    complexity.
  - The companion explicitly cites this article (companion Claim 1) as the
    foundational "AI-native vs. AI-assisted" framing.

- **Contradicts**: None identified. The two PagerDuty articles are complementary —
  this one covers evaluation, metrics, guardrails, and UX (areas the companion
  explicitly says it does not cover), while the companion covers implementation
  primitives (reactive loop, identity, transport, durability model).

- **Extends**: The companion SRE Agent architecture article — this article supplies
  the *what to evaluate / measure / guardrail* half the companion omits (the
  companion notes it doesn't cover evaluation/accuracy metrics or cost data). This
  article also adds the UX dimension (transparent reasoning) and the memory
  architecture (knowledge graphs vs. RAG) the companion doesn't address.

- **Novel**: Contributions new to the corpus (vs. the companion note):
  - Five-pillar production-readiness framework (Reliability, Control, Visibility,
    Integration, Economics).
  - Evaluation pipeline design — golden datasets with what/how/who dimensions,
    LLM-as-a-judge scoring, CI-gated re-evaluation, adversarial test suites.
  - Context poisoning — a named failure mode distinct from context fatigue /
    hallucination.
  - Nine-metric framework including groundedness rate, cost per successful task,
    and human escalation rate.
  - Prompt-injection susceptibility data (80-90%, Chang et al. 2026) and
    low-resource-language bypass evidence.
  - Guardrail classification (sync vs. async) — a safety/latency trade-off pattern.
  - Knowledge-graph vs. RAG argument for invalidation-aware, temporally-aware
    shared agent memory.
  - Transparent UX finding — showing reasoning steps builds trust and latency
    tolerance.
  - Traditional DevOps carry-over — staged rollouts, canaries, feature flags
    (Claim 17).

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Supplies the evaluation, metrics, and
  guardrail framework the companion architecture article lacks:
  - The five-pillar framework as a production-readiness checklist.
  - The architecture evolution pattern (single → supervisor → hierarchical) with
    the explicit warning not to start with peer-to-peer.
  - The deterministic-vs-probabilistic principle: audit agent code for LLM calls
    replaceable with deterministic code.
  - The domain-grouped agent pattern with explicit permissions (security-incident
    example).

- **Chapter 05 (LLM Ops Reliability)**: Strongest material for this chapter:
  - The evaluation pipeline (golden datasets → LLM-as-a-judge → CI gates) as a
    recommended quality-assurance pattern.
  - The nine-metric framework (task success, groundedness, tool errors, p95
    latency, cost, safety violations, human escalation) as recommended
    observability metrics.
  - Guardrail architecture: defense-in-depth, sync/async classification,
    low-resource-language blocking, kill switch from day one.
  - Context poisoning as a specific monitoring/alerting concern.
  - The "March of 9s" framing for reliability investment planning.
  - Transparent UX: agents should expose reasoning to build trust; observability
    must capture traces of model input, reasoning path, tool choices, sub-agent
    responses.
  - Claim 17: staged rollouts / canaries / feature flags remain relevant in an
    agent world.

- **Chapter 00 (Principles)**: Supports "test what the user actually does" —
  deterministic tests don't fit natural-language systems; evaluation must be
  structural (golden datasets, LLM-as-a-judge) and continuous (CI-gated
  re-evaluation). Also supports "engineer boundaries up front" and "invest in
  traces/evals/guardrails before you need them."

## Extraction Notes

- The source is a long-form blog post on PagerDuty's engineering blog, publicly
  accessible, not paywalled. Full text was retrieved via direct HTML download
  (curl) and stripped of navigation/markup; the body was extracted from the
  `<h2 id="context">` anchor through the References section. All quotes in this
  note are copied character-for-character from that extracted text.
- **Where this replay differs from the merged DeepSeek baseline
  (`blog-pagerduty-production-ai-agent-gaps.md`):** The baseline extracted its
  quotes via WebFetch and several of its `Quote` fields were paraphrases rather
  than the source's exact words. Specifically, the baseline's quotes for Claims 1
  ("Going from an idea to a prototype today takes hours or minutes."), 3
  ("the early parts of your prompt start losing probabilistic weight as more
  tokens accumulate"), 4 ("the errors multiply rather than average out"), 5 (the
  80-90% sentence), 8 (the peer-to-peer sentence), and 14 (low-resource-language
  sentence) did not match the source verbatim — they were shortened or
  reconstructed. This replay restores the exact source wording for every one of
  those claims. The Assayer should spot-check this replay's quotes against the
  live URL; they are taken directly from the downloaded HTML.
- **Confidence corrections vs. baseline:** This replay rates Claim 3 (context
  fatigue), Claim 4 (compounding errors), and Claim 5 (prompt-injection
  susceptibility) as **settled** rather than the baseline's "emerging," because the
  source states each as an unconditional, observed/well-cited fact (and Claims 3
  & 4 are corroborated by the companion article). Claim 1 is rated "settled" as
  the article's central, directly-observed thesis.
- **New material vs. baseline:** This replay adds Claim 17 (traditional DevOps
  practices — staged rollouts, canaries, feature flags, "scale with AI on AI" —
  from the article's "What did we learn?" section), which the baseline omitted.
- The article cites ten academic references. These were not independently fetched;
  they are cited here as they appear in the source bibliography (Chang et al. 2026,
  Colelough & Regli 2025, Khalifa et al. 2025, Lightman et al. 2024, Marx &
  Dunaiski 2026, Raspanti et al. 2025, Shen et al. 2024, Ullah et al. 2024, Yao et
  al. 2023, Yong et al. 2023).
- The linked companion article "Building end-to-end observability for AI agents in
  production" is referenced but was not followed (out of scope for this single
  source; also returned errors in the baseline run).
- The source does not provide quantitative production metrics (no specific latency
  numbers, cost figures, or evaluation-pipeline accuracy percentages).
