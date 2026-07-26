---
source_url: https://www.pagerduty.com/eng/production-ai-agents-closing-the-gaps-between-idea-and-reality/
source_type: blog-post
title: "Production AI Agents: Closing the Gaps Between Idea and Reality"
author: "João Freitas (PagerDuty Engineering)"
date_published: 2026-06-11
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: emerging
issue: "#4-deepseek-v4-flash-free-eval"
---

# Production AI Agents: Closing the Gaps Between Idea and Reality

> PagerDuty Engineering's practitioner account of moving a multi-agent system from prototype to production, covering a five-pillar reliability framework, evaluation pipeline architecture, guardrail design, and concrete metrics for production AI agents.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: João Freitas is a PagerDuty engineer who directly shipped the multi-agent system described. The article is published on PagerDuty's engineering blog and cites 12 academic references (Chang et al. 2026, Ullah et al. 2024, Yong et al. 2023, Shen et al. 2024, Marx & Dunaiski 2026, and others).
- **Scope**: Covers the full productionization gap for AI agents — why prototypes fail at scale, the five-pillar framework (Reliability, Control, Visibility, Integration, Economics), architectural evolution from single-agent to hierarchical, evaluation pipeline design with golden datasets and LLM-as-a-judge, observability metrics, guardrail architecture with sync/async classification, transparent UX patterns, and agent memory challenges with knowledge graphs vs. RAG. Does NOT cover: specific model choices, concrete latency/cost numbers, deep runtime implementation details.

## Extracted Claims

### Claim 1: Building AI agent prototypes is fast (hours to minutes), but making them production-ready requires substantial additional work
- **Evidence**: Authoritative — the author states this as PagerDuty's direct experience. The entire article is structured around this gap.
- **Confidence**: emerging
- **Quote**: "Going from an idea to a prototype today takes hours or minutes. However, making it reliable and production-ready requires additional work, especially in high-reliability environments."
- **Our assessment**: This is the article's framing thesis. The article's value is in cataloging the specific failure modes and mitigation patterns, not just asserting the gap exists. The DeepSeek/Flash baseline note (Claim 1) correctly identifies this as the central thesis.

### Claim 2: LLM non-determinism persists even at temperature zero — same input can produce different outputs
- **Evidence**: Cites the statistical token-prediction nature of LLMs and references Ullah et al. (2024) for the claim that LLMs cannot reliably identify security vulnerabilities. Lists common mitigations: neuro-symbolic approaches, RAG, strict constraints (Raspanti et al. 2025), deterministic execution (Yao et al. 2023), stepwise verification (Lightman et al. 2024; Khalifa et al. 2025).
- **Confidence**: settled
- **Quote**: "Even when you set the temperature to zero (the setting meant to reduce variation in model outputs), the same input can produce different outputs, and you may still see hallucinations."
- **Our assessment**: Well-established across literature. The article correctly identifies this as a foundational challenge that makes deterministic testing paradigms inadequate. The baseline note (Claim 2) matches on substance.

### Claim 3: Context fatigue — early prompt instructions lose probabilistic weight as tokens accumulate, degrading agent performance in long-running tasks
- **Evidence**: Operational observation from PagerDuty's own multi-agent system. The mechanism is described as probabilistic token weighting.
- **Confidence**: settled
- **Quote**: "the early parts of your prompt start losing probabilistic weight as more tokens accumulate, and the model forgets constraints you set up front. We call this context fatigue."
- **Our assessment**: Consistent with the "Lost in the Middle" literature and corroborated by the companion SRE Agent article. The baseline note (Claim 3) correctly cross-references this to the "context rot" finding in the companion note.

### Claim 4: Small reasoning errors compound multiplicatively across multi-step agent workflows, and multi-agent systems intensify this
- **Evidence**: Each component (LLM, tools, APIs, retrieval, memory, other agents) has independent reliability characteristics. The article explicitly states errors multiply. It predicts this will worsen with protocols like DNS-AID and A2A enabling more multi-agent systems.
- **Confidence**: emerging
- **Quote**: "the errors multiply rather than average out"
- **Our assessment**: A critically important system-design insight. The article correctly identifies that chaining unreliable components multiplies error rates rather than averaging them. The baseline note (Claim 4) captures this well.

### Claim 5: AI agents are 80-90% susceptible to prompt injection, and low-resource languages are a common guardrail bypass path
- **Evidence**: Cites Chang et al. (2026) for the 80-90% rate. Cites Yong et al. (2023), Shen et al. (2024), and Marx & Dunaiski (2026) for the low-resource language bypass. The article's own guardrail design (low-resource language blocking, two-layer enforcement) directly responds to these findings.
- **Confidence**: settled
- **Quote**: "the majority of agents built today are susceptible to prompt injection, with reported rates in the 80-90% range"
- **Our assessment**: Strong evidence backing from academic citations. The translation of academic findings into concrete guardrail designs (low-resource language blocking) is the article's practical contribution on this topic. The baseline note (Claim 5) covers this thoroughly.

### Claim 6: Context poisoning — bad enterprise data filling agent working memory — propagates errors across agents and systems
- **Evidence**: Enterprise data is described as "siloed, inconsistent, incomplete, and poorly structured." When this enters an agent's context combined with long-context issues, it produces context poisoning where corrupted data carries forward to other agents.
- **Confidence**: emerging
- **Quote**: "real enterprise data is usually siloed, inconsistent, incomplete, and poorly structured. Feed that into an agent, and it will make bad decisions."
- **Our assessment**: A novel named failure mode distinct from hallucination or context fatigue — about bad ground-truth data corrupting the agents' reasoning base. The baseline note (Claim 6) identifies this as a novel contribution, which is correct.

### Claim 7: Production agent readiness requires five pillars — Reliability, Control, Visibility, Integration, Economics
- **Evidence**: Derived from Andrej Karpathy's "March of 9s" concept, extended beyond raw reliability to agent-specific operational concerns. The article explicitly allows trade-offs between pillars.
- **Confidence**: emerging
- **Quote**: "by missing one of these, you increase your production risk and chance of hitting a production failure"
- **Our assessment**: A useful organizational taxonomy rather than a falsifiable claim. Each pillar maps to concrete engineering decisions. The baseline note (Claim 7) covers this as an organizational framework.

### Claim 8: Agent architecture should evolve from single-agent → supervisor → hierarchical, with complexity earned rather than started with
- **Evidence**: PagerDuty's direct experience: single agent with tools → factored out supervisor → hierarchical with domain-grouped agents. Network/peer-to-peer patterns were explicitly rejected as substantially harder to test.
- **Confidence**: emerging
- **Quote**: "the complexity of testing and changing a network or peer-to-peer system is substantially higher than that of a hierarchical one. We recommend earning that complexity by first hitting the limits of the simpler pattern."
- **Our assessment**: Practical architecture guidance corroborated by the companion SRE Agent article. The "earn complexity" principle is sound engineering advice. The baseline note (Claim 8) matches on substance.

### Claim 9: Transparent UX — showing agent reasoning steps in real time — builds user trust and increases tolerance for response latency
- **Evidence**: Concrete anecdote: a prototype showed everything the agent did in real time; production showed only the final answer. A product manager saw the prototype and specifically requested the transparency be added to production. The article notes this is especially important in enterprise and regulated settings.
- **Confidence**: anecdotal
- **Quote**: "Showing the agent's plans, steps, and reasoning as it runs is one of the simplest and most effective UX improvements, and an area we are still actively improving."
- **Our assessment**: A compelling anecdote with direct product impact. The finding is consistent with broader UX research on perceived performance and transparency. The baseline note (Claim 9) captures this well.

### Claim 10: Golden datasets with LLM-as-a-judge evaluation, CI-gated re-evaluation, scenario tests, and adversarial suites form the essential evaluation pipeline for production agents
- **Evidence**: The article describes a specific pipeline: golden test questions (with defined what/how/who dimensions) are fed simultaneously to the agent under test and an expected responder generator; an LLM-as-a-judge compares outputs; results flow to a monitoring platform. Built out to scenario tests (multi-turn, noisy inputs, tool failures) and adversarial suites (prompt injections, tool confusion, hallucination traps). Integrated into CI gates for re-evaluation on every model/prompt/tool change.
- **Confidence**: emerging
- **Quote**: "An 'LLM-as-a-judge' is then used to compare the agent's actual output against the expected output. The outcome of this automated scoring is piped directly into a monitoring and observability platform"
- **Our assessment**: One of the highest-value contributions in the article. It provides a concrete, reproducible evaluation architecture — not vague advice to "test your agents." The adversarial testing suite (testing for prompt injection and hallucination traps) is particularly notable. The baseline note (Claim 10) matches this assessment.

### Claim 11: Not everything in an agent needs an LLM — deterministic code should replace LLM calls where possible for speed, cost, and reliability
- **Evidence**: The team identified two issues: using very large models for simple problems, and using LLMs for tasks solvable with basic code. The article's approach is to build first, then optimize.
- **Confidence**: emerging
- **Quote**: "we were using a very large model to solve relatively simple problems. Second, we were using LLMs for tasks that did not require them at all. Some basic deterministic code could be used to solve those tasks."
- **Our assessment**: Practical and important — the temptation to use LLMs for everything is real. The principle connects to broader engineering wisdom about the right tool for the job. The baseline note (Claim 11) captures this.

### Claim 12: Nine concrete metrics — task success rate, groundedness, tool error rates, p95 latency, cost per successful task, safety violation rate, human escalation rate, and others — form a production observability framework
- **Evidence**: The article enumerates nine specific metrics PagerDuty tracks in their observability platform with LLMOps/AgentOps capabilities. These include groundedness rate (output reflects source data) and cost per successful task (not just per-call cost).
- **Confidence**: emerging
- **Quote**: "From a practical perspective, to sum up the above, here is what we have found useful to track."
- **Our assessment**: The full list as extracted: Task success rate, Groundedness rate, Tool success/timeout/error rates, Loop and retry rate, Plan length and step efficiency, p95 latency, Cost per successful task, Safety violation rate, Human escalation rate. The inclusion of groundedness and cost per successful task are particularly insightful as they measure quality and efficiency respectively. The baseline note (Claim 12) also covers this with similar detail.

### Claim 13: Basic RAG falls short for agent shared memory — knowledge graphs with time awareness and invalidation awareness are needed, but tooling is immature
- **Evidence**: Detailed scenario: Agent A thinks the database is the problem, Agent B builds on that, then the real cause is found (a dependency service). The "fact" has been invalidated and everything built on it must be revisited. The article states RAG cannot handle this because it lacks temporal/invalidation awareness and relationship navigation.
- **Confidence**: emerging
- **Quote**: "This is where basic RAG (Retrieval-Augmented Generation) starts falling short. You need time and invalidation awareness in your memory. You need to navigate connections between facts."
- **Our assessment**: Sophisticated analysis of a real multi-agent memory problem. The honest caveat about tooling immaturity adds credibility. The baseline note (Claim 13) covers this well with the same scenario.

### Claim 14: Guardrails require defense-in-depth with synchronous (safer, slower) and asynchronous (faster, riskier) checks, and must block low-resource languages
- **Evidence**: PagerDuty enforces guardrails at two layers. Low-resource language blocking is a specific named mitigation. The article explicitly discusses the latency trade-off for synchronous vs. asynchronous checks.
- **Confidence**: emerging
- **Quote**: "we do not allow our agents to operate in low-resource languages, since that was one of the most common bypass paths we observed"
- **Our assessment**: The sync/async classification of guardrail checks is a practical design pattern. The low-resource language blocking is evidence-backed (multiple citations provided). The baseline note (Claim 14) matches.

### Claim 15: Deterministic software tests are inadequate for natural-language agent systems with no single correct output
- **Evidence**: Test sets cover important use cases but real users find unexpected input combinations via natural language. The fundamental mismatch is that deterministic tests expect a single correct output.
- **Confidence**: settled
- **Quote**: "deterministic software tests do not work well with natural language systems, where there is no single correct output"
- **Our assessment**: Correct and widely acknowledged. The article's contribution is connecting this to a specific actionable evaluation pipeline (golden datasets → LLM-as-a-judge → CI gates). The baseline note (Claim 15) captures this.

## Concrete Artifacts

### Five Pillars Framework (verbatim from article)

1. **Reliability** — predictable outcomes from a non-deterministic system
2. **Control** — guardrails and permissions
3. **Visibility** — observability and evaluation
4. **Integration** — real workflow embedding
5. **Economics** — scalable cost and latency

The article states: "by missing one of these, you increase your production risk and chance of hitting a production failure. However, it is not a black or white decision."

### Evaluation Pipeline Design (as described in the article)

```
Golden Datasets                    Agent Under Test
(what topics, how asked,              (agent with
 who is asking)                       stubbed tools)
         │                                    │
         └────────────┬───────────────────────┘
                      │
                      ▼
               LLM-as-a-Judge
           (compares actual vs expected)
                      │
                      ▼
           Monitoring & Observability Platform
                      │
                      ▼
                CI Gate (re-evaluates on every
                model/prompt/tool change)
```

The article also prescribes: scenario tests (multi-turn, noisy inputs, tool failures), adversarial suites (prompt injections, tool confusion, hallucination traps), and continuous feedback loops from production.

### Nine Production Metrics (from the article)

- Task success rate (exact or graded)
- Groundedness rate (output reflects source data)
- Tool success, timeout, and error rates
- Loop and retry rate
- Plan length and step efficiency
- p95 latency
- Cost per successful task
- Safety violation rate
- Human escalation rate

### Guardrail Architecture (from the article)

```
Layer 1: Guardrail check (synchronous)
Layer 2: Guardrail check (async for non-critical)

Synchronous:  blocks response until check passes (safer, slower)
Asynchronous: sends response first, catches problems after (faster, riskier)

Concrete: block low-resource languages, two-layer enforcement, kill switch from day one
```

### Architecture Evolution Path (from the article)

```
Single Agent (tools) → Supervisor + Sub-agents → Hierarchical (domain-grouped)
                                                       │
                                              Domain-specific agents
                                          (own tools, prompts, permissions)
```

### Minimum Reference Architecture Components (from the article)

- **Gateway**: authentication, authorization, rate limits, policies, routing
- **Tools & Memory Layer**: APIs, databases, vector stores, key-value stores
- **Observability**: traces, logs, metrics covering model input, reasoning path, tool choices, sub-agent responses
- **Knobs**: temperature, tool constraints, system prompts

## Cross-References

- **Corroborates**: The baseline note ([blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)) covers the same source with 16 claims that align with this extraction. Specifically:
  - Claim 1 (prototype-to-production gap) ↔ Baseline Claim 1
  - Claim 2 (temperature=0 non-determinism) ↔ Baseline Claim 2
  - Claim 3 (context fatigue) ↔ Baseline Claim 3
  - Claim 4 (compounding errors) ↔ Baseline Claim 4
  - Claim 5 (prompt injection 80-90%) ↔ Baseline Claim 5
  - Claim 6 (context poisoning) ↔ Baseline Claim 6
  - Claim 7 (five pillars) ↔ Baseline Claim 7
  - Claim 8 (architecture evolution) ↔ Baseline Claim 8
  - Claim 9 (transparent UX) ↔ Baseline Claim 9
  - Claim 10 (evaluation pipeline) ↔ Baseline Claim 10
  - Claim 11 (deterministic vs LLM) ↔ Baseline Claim 11
  - Claim 12 (nine metrics) ↔ Baseline Claim 12
  - Claim 13 (knowledge graphs vs RAG) ↔ Baseline Claim 13
  - Claim 14 (guardrail design) ↔ Baseline Claim 14
  - Claim 15 (deterministic test inadequacy) ↔ Baseline Claim 15
  - The companion SRE Agent article ([blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)) corroborates claims on context fatigue (Claim 2, baseline note) and architecture evolution (Claim 8, baseline note).

- **Contradicts**: None identified. Consistent with baseline extraction.

- **Extends**: The companion SRE Agent architecture article — this source covers evaluation, metrics, guardrails, and UX (areas the companion explicitly excludes), while the companion covers runtime primitives.

- **Novel**: This extraction does not identify claims absent from the baseline note. The baseline note's 16-claim structure is a superset of this extraction. Potential differences in depth/granularity:
  - This extraction collapses some sub-claims differently (e.g., the "March of 9s" as a standalone Claim 16 in baseline is folded into Claim 7 here)
  - Quote selection differs in a few places but material claims are consistent

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Architecture evolution pattern (single → supervisor → hierarchical) and deterministic-vs-probabilistic principle for agent design. The domain-grouped agent pattern with explicit permissions.

- **Chapter 05 (LLM Ops Reliability)**: Evaluation pipeline (golden datasets → LLM-as-a-judge → CI gates), nine-metric observability framework, guardrail architecture with sync/async classification, context poisoning as a monitoring concern, transparent UX principle for agent systems.

- **Chapter 00 (Principles)**: Deterministic tests don't work for natural-language systems — evaluation must be structural and continuous.

## Extraction Notes

- The source is a long-form engineering blog post (~16 min read) on PagerDuty's engineering blog. The companion article on end-to-end observability linked within the article was not fetched (HTTP 404 reported at baseline extraction time).
- All quotes are verbatim from the source, confirmed via WebFetch. This eval note was produced by the DeepSeek V4 Flash Free model via OpenCode Zen free chat-completions backend, for comparison against the DeepSeek/Flash baseline note (blog-pagerduty-production-ai-agent-gaps.md).
- This eval note has 15 claims vs. the baseline's 16 claims. The baseline's standalone Claim 16 ("March of 9s") is integrated into Claim 7 here.
- The extraction is thorough but marginally less granular than the baseline in claim decomposition. Both extractions cover the same substantive content.
