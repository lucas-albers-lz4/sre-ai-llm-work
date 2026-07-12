---
source_url: https://www.pagerduty.com/eng/production-ai-agents-closing-the-gaps-between-idea-and-reality/
source_type: blog-post
title: "Production AI Agents: Closing the Gaps Between Idea and Reality"
author: "João Freitas (PagerDuty Engineering)"
date_published: 2026-06-11
date_extracted: 2026-07-12
last_checked: 2026-07-12
status: current
confidence_overall: emerging
issue: "#4"
---

# Production AI Agents: Closing the Gaps Between Idea and Reality

> A practitioner writeup from PagerDuty Engineering describing the systemic
> reliability gaps, security risks, and operational constraints encountered
> when moving AI agents from prototype to production. Covers a five-pillar
> framework, concrete evaluation pipeline design, guardrail architecture,
> observable metrics, and architectural lessons from shipping a multi-agent
> system at enterprise scale. Published June 2026 — recent, and the precursor
> framing article for the SRE Agent deep-dive that followed.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: João Freitas is a PagerDuty engineer with direct
  production experience building and shipping their multi-agent system. The
  article is published on PagerDuty's engineering blog and serves as the
  foundational framing piece later cited by the SRE Agent architecture
  deep-dive (Vasylkovskyi et al., also on the PagerDuty engineering blog).
  Claims are supported by citations to peer-reviewed research (Chang et al.
  2026, Ullah et al. 2024, Yong et al. 2023, Shen et al. 2024, Marx &
  Dunaiski 2026, and others).
- **Scope**: Covers the full productionization gap — why prototypes fail at
  scale, the five-pillar reliability framework, architectural evolution from
  single-agent to hierarchical, evaluation pipeline design (golden datasets,
  LLM-as-a-judge, CI gates), observable metrics, guardrail architecture,
  transparent UX, agent memory sharing (knowledge graphs vs. RAG), and
  cost/latency optimization. Does NOT cover: deep implementation details of
  the agent runtime (those are in the follow-up SRE Agent article), specific
  model choices, concrete latency/cost numbers, or code-level implementation.

## Extracted Claims

### Claim 1: The prototype-to-production gap for AI agents is large and structural — demos are easy, reliability is hard
- **Evidence**: Authoritative — the author describes this as PagerDuty's
  observed experience from a year of shipping a multi-agent system. The
  entire article is structured around bridging this gap. The claim is also
  supported by the Karpathy "March of 9s" concept cited later in the article.
- **Confidence**: emerging
- **Quote**: "Going from an idea to a prototype today takes hours or minutes."
- **Our assessment**: This is the central thesis of the article and sets the
  stage for everything that follows. The distinction between "works in a demo"
  and "works in production" is widely acknowledged across practitioner
  communities. The article's contribution is cataloging the specific failure
  modes that cause the gap, not just asserting it exists.

### Claim 2: LLM non-determinism persists even with temperature set to zero, making agent behavior inherently unpredictable
- **Evidence**: Cites the statistical nature of LLMs — they predict the next
  most likely token rather than evaluating abstract rules. References Ullah
  et al. (2024) for the claim that LLMs cannot reliably identify security
  vulnerabilities. Common mitigations referenced: neuro-symbolic approaches,
  RAG, strict constraints, deterministic execution, stepwise verification.
- **Confidence**: settled
- **Quote**: "the same input can produce different outputs, and you may still see hallucinations"
- **Our assessment**: This is well-established across the literature. Even
  with temperature=0, floating-point non-determinism and model-update
  variability produce different outputs. The article correctly identifies
  this as a foundational challenge that makes "deterministic software tests"
  inadequate. The cited mitigations (neuro-symbolic, constraints, stepwise
  verification) are standard approaches.

### Claim 3: Context fatigue causes early prompt instructions to lose weight as token count grows, degrading agent behavior in long-running tasks
- **Evidence**: Described as a direct operational observation — in longer
  tasks the model "forgets" upfront constraints as the context window fills.
  The article frames this as a consequence of how LLMs weight tokens
  probabilistically.
- **Confidence**: settled
- **Quote**: "the early parts of your prompt start losing probabilistic weight as more tokens accumulate"
- **Our assessment**: Consistent with the "Lost in the Middle" literature
  (Liu et al. 2023) and corroborated by the companion PagerDuty SRE Agent
  article's "context rot" finding (blog-pagerduty-sre-agent-architecture,
  Claim 2). This is a well-observed failure mode that creates a hard ceiling
  for single-agent architectures handling long investigations.

### Claim 4: Errors compound multiplicatively across multi-step agent workflows rather than averaging out
- **Evidence**: Each component (LLM, tools, APIs, retrieval, memory, other
  agents) has independent reliability characteristics. When chained in a
  workflow, individual error rates compound. The article notes this intensifies
  in multi-agent systems as protocols like DNS-AID and A2A make integration
  easier.
- **Confidence**: emerging
- **Quote**: "the errors multiply rather than average out"
- **Our assessment**: This is a critically important insight for system design.
  If each step in a 5-step workflow has 95% reliability, the compound
  reliability is ~77% (0.95^5), not the 95% average. The article correctly
  identifies that multi-agent systems amplify this effect. The practical
  implication — that system design must account for multiplicative error
  propagation — is not widely discussed in the agent literature.

### Claim 5: AI agents are highly susceptible to prompt injection, with reported rates in the 80-90% range, and guardrails can be bypassed via low-resource languages
- **Evidence**: Cites Chang et al. (2026) for the 80-90% prompt injection
  susceptibility rate. Cites Yong et al. (2023), Shen et al. (2024), and
  Marx & Dunaiski (2026) for the low-resource language bypass finding. The
  article's own guardrail design (low-resource language blocking, two-layer
  enforcement) is a direct response to these findings.
- **Confidence**: settled
- **Quote**: "the majority of agents built today are susceptible to prompt injection, with reported rates in the 80-90% range"
- **Our assessment**: The 80-90% figure is cited from peer-reviewed research
  (Chang et al. 2026) and is consistent with broader security research. The
  low-resource language bypass is well-documented (multiple citations provided).
  This claim has strong evidence backing. The article's practical contribution
  is translating academic findings into concrete guardrail designs.

### Claim 6: Context poisoning — stale, corrupted, or contradictory data filling an agent's working memory — propagates errors across agents and systems
- **Evidence**: The article provides a concrete scenario: real enterprise data
  is "siloed, inconsistent, incomplete, and poorly structured." When this data
  enters an agent's context window, it poisons the working memory. Combined
  with long-context issues, corrupted data propagates to other agents through
  shared context. This is the article's original concept — it has a specific
  name and mechanism, not just "bad data."
- **Confidence**: emerging
- **Quote**: "real enterprise data is usually siloed, inconsistent, incomplete, and poorly structured"
- **Our assessment**: This is one of the article's novel contributions. The
  term "context poisoning" describes a specific failure mode distinct from
  hallucination or context fatigue — it's about bad ground-truth data
  corrupting the agent's reasoning base. The propagation risk in multi-agent
  systems is a significant concern. The article's knowledge graph discussion
  (Claim 13) is positioned as a partial mitigation.

### Claim 7: A five-pillar framework — Reliability, Control, Visibility, Integration, Economics — defines production readiness for AI agent systems
- **Evidence**: The author derives these five pillars from the Karpathy
  "March of 9s" concept, extending beyond raw reliability to encompass the
  operational concerns unique to agentic AI. Each pillar is tied to concrete
  engineering decisions described in the article. The article explicitly notes
  that trade-offs between pillars are possible (e.g., trading latency for
  groundedness via verification agents).
- **Confidence**: emerging
- **Quote**: "by missing one of these, you increase your production risk"
- **Our assessment**: This is a useful organizational framework, not a
  falsifiable claim. It's well-structured and each pillar maps to concrete
  engineering concerns. The framework is one team's taxonomy; it hasn't been
  independently validated by other organizations. Still, it covers the
  dimensions that consistently appear in production-agent postmortems.

### Claim 8: Agent architecture should evolve from single-agent → supervisor → hierarchical, earning complexity rather than starting with it
- **Evidence**: PagerDuty's direct experience: they started with a single agent
  calling tools, which accumulated responsibilities until it felt like an
  orchestrator. They factored out a supervisor routing to specialized
  sub-agents, then moved to a hierarchical pattern with domain-grouped agents.
  Network/peer-to-peer patterns were considered but rejected as substantially
  harder to test and change.
- **Confidence**: emerging
- **Quote**: "the complexity of testing and changing a network or peer-to-peer system is substantially higher"
- **Our assessment**: The evolutionary pattern (single → supervisor →
  hierarchical) is corroborated by the companion SRE Agent article
  (blog-pagerduty-sre-agent-architecture, Claim 12 regarding the
  simplification argument). The advice to "earn complexity" is a recurring
  theme across both PagerDuty articles. The rejection of peer-to-peer for
  testability reasons is a practical constraint worth noting.

### Claim 9: Transparent UX — showing agent reasoning steps in real time — builds user trust and increases willingness to wait for agent responses
- **Evidence**: A concrete anecdote: an early prototype displayed everything
  the agent did in real time, while the production version only showed the
  final answer. A product manager saw the prototype and specifically requested
  that transparency be added to production. The article notes this is
  especially important in enterprise and regulated settings where trust makes
  the product usable. The team studied how large-scale AI players handle
  agentic experiences and adapted lessons for collaborative interfaces like
  Slack and Microsoft Teams.
- **Confidence**: anecdotal
- **Quote**: "Showing the agent's plans, steps, and reasoning as it runs is one of the simplest and most effective UX improvements"
- **Our assessment**: This is an anecdote, but a compelling one with direct
  product impact. The finding — that a silent spinner frustrates users while
  a visible reasoning process builds trust — is consistent with broader UX
  research on perceived performance and transparency. The application to
  enterprise/regulated settings is a useful contextualization.

### Claim 10: Automated evaluation pipelines using golden datasets + LLM-as-a-judge + CI gates are essential for production-grade agent systems
- **Evidence**: The article describes a specific workflow: golden test
  questions (with defined what/how/who dimensions) are fed simultaneously to
  the agent under test and an expected responder generator; an LLM-as-a-judge
  compares outputs; results flow to monitoring. This is integrated into CI
  gates for continuous offline re-evaluation on any model, prompt, or tool
  change. Builds out to scenario tests (multi-turn, noisy inputs, tool
  failures) and adversarial suites (prompt injections, tool confusion,
  hallucination traps).
- **Confidence**: emerging
- **Quote**: "An 'LLM-as-a-judge' is then used to compare the agent's actual output against the expected output"
- **Our assessment**: This is one of the article's highest-value contributions.
  It provides a concrete, reproducible evaluation architecture rather than
  vague advice to "test your agents." The what/how/who framework for golden
  dataset curation, the LLM-as-a-judge step, and the CI integration all
  provide actionable patterns. The adversarial testing suite is particularly
  notable — it tests for prompt injection and hallucination, not just task
  accuracy.

### Claim 11: Not everything in an agent needs to be probabilistic — deterministic code should replace LLM calls where possible for speed, cost, and reliability
- **Evidence**: The team found two issues in early versions: using very large
  models for simple problems, and using LLMs for tasks solvable with basic
  deterministic code. The article frames this as an optimization principle:
  build first, then identify and replace unnecessary LLM calls.
- **Confidence**: emerging
- **Quote**: "using a very large model to solve relatively simple problems"
- **Our assessment**: This is a practical and important observation. It
  connects to the companion SRE Agent article's discussion of IO-bound vs
  compute-bound workloads (blog-pagerduty-sre-agent-architecture, Claim 12).
  The principle is straightforward but easy to miss when building
  agent-first systems — the temptation to use LLMs for everything is real.

### Claim 12: A concrete metrics framework should track task success, groundedness, tool error rates, p95 latency, cost per successful task, safety violations, and human escalation rate
- **Evidence**: The article enumerates nine specific metrics PagerDuty found
  useful in production: task success rate, groundedness rate, tool
  success/timeout/error rates, loop and retry rate, plan length, p95 latency,
  cost per successful task, safety violation rate, and human escalation rate.
  These are operational metrics they track in their observability platform
  with LLMOps/AgentOps capabilities.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is a concrete, actionable set of metrics from
  production experience. The inclusion of "groundedness" (whether output
  reflects source data) and "cost per successful task" (not just cost per
  call) are particularly insightful — they measure quality and efficiency,
  not just throughput. The companion SRE Agent article explicitly says it
  doesn't cover this dimension, making this article's metrics coverage a
  valuable complement.

### Claim 13: Basic RAG is insufficient for agent shared memory — knowledge graphs with time awareness and invalidation awareness are needed, but tooling is immature
- **Evidence**: A detailed scenario: Agent A posts that the database is the
  problem. Agent B builds on that hypothesis. Ten minutes later, Agent C (or
  a human) discovers the database is fine — a dependency service returning bad
  responses made it appear slow. The "fact" has been invalidated and everything
  built on it must be revisited. The article states RAG can't handle this
  because it lacks temporal/invalidation awareness and the ability to navigate
  relationships between facts.
- **Confidence**: emerging
- **Quote**: "basic RAG... starts falling short"
- **Our assessment**: This is a sophisticated analysis of a real multi-agent
  memory problem. The scenario is compelling and specific. The honest caveat
  about tooling immaturity adds credibility. This directly complements the
  companion SRE Agent article's discussion of shared context between agents
  but goes deeper on the memory representation layer. The knowledge graph
  recommendation is directionally important but the article correctly flags
  that current tools aren't enterprise-ready.

### Claim 14: Guardrails require defense-in-depth with synchronous and asynchronous checks, and must block low-resource languages as one of the most common bypass paths
- **Evidence**: PagerDuty enforces guardrails at two layers. Low-resource
  language blocking is a specific, named mitigation. The article explicitly
  discusses the latency trade-off: synchronous checks block the response
  until the check passes (safer, slower), asynchronous checks send the
  response first and catch problems after (faster, riskier). Non-critical
  checks use async to avoid latency penalties.
- **Confidence**: emerging
- **Quote**: "we do not allow our agents to operate in low-resource languages, since that was one of the most common bypass paths"
- **Our assessment**: The sync/async classification of guardrail checks is a
  practical design pattern applicable beyond PagerDuty. The low-resource
  language blocking is a specific, evidence-backed mitigation (supported by
  the cited research on multilingual jailbreaking). The two-layer enforcement
  provides defense-in-depth without prescribing a specific technology.

### Claim 15: Deterministic software tests are inadequate for evaluating natural-language agent systems where there is no single correct output
- **Evidence**: The article observes that test sets cover important use cases,
  but real users find unexpected input combinations via natural language
  prompting. More fundamentally, deterministic tests expect a single correct
  output — a paradigm that doesn't fit probabilistic, natural-language systems.
  This is the motivation for the LLM-as-a-judge evaluation approach.
- **Confidence**: settled
- **Quote**: "deterministic software tests do not work well with natural language systems, where there is no single correct output"
- **Our assessment**: This is fundamentally correct and widely acknowledged in
  the LLM evaluation literature. The article's contribution is connecting this
  observation to the specific evaluation pipeline they built (golden datasets
  → LLM-as-a-judge → CI gates), making it actionable rather than theoretical.

### Claim 16: The "March of 9s" applies to AI agents — prototype reliability at ~90% requires redundant system layers, validation pipelines, fallback logic, and runtime error containment to improve
- **Evidence**: The article attributes the "March of 9s" concept to Andrej
  Karpathy. Reaching additional 9s beyond prototype-level (~90%) requires
  systematic investment in redundant layers, extensive validation, complex
  fallback logic, and runtime error containment. The article uses this as
  the framing for its five-pillar approach.
- **Confidence**: emerging
- **Quote**: "Andrej Karpathy named the process of increasing the reliability of your system as the 'March of 9s'"
- **Our assessment**: The "March of 9s" is a useful concept for framing the
  reliability investment curve. Applied to agents, it correctly predicts that
  the jump from demo (~90%) to production (99%+) requires systematic
  investment, not incremental tweaks. The article uses this concept effectively
  to motivate its five-pillar framework. It's a frame rather than a verified
  law, but it's a useful one.

## Concrete Artifacts

### Five Pillars Framework (as described in the article)

1. **Reliability** — predictable outcomes from a non-deterministic system
2. **Control** — guardrails and permissions
3. **Visibility** — observability and evaluation
4. **Integration** — real workflow embedding
5. **Economics** — scalable cost and latency

The article states trade-offs between pillars are possible: e.g., if
groundedness matters more than latency, introduce a verification agent to
fact-check answers, increasing both reliability and latency.

### Evaluation Pipeline Design (from the article)

```
Golden Datasets                    Agent Under Test
(what topics, how asked,              (LLM agent with
 who is asking)                       stubbed tools/seeds)
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

Additionally, the article prescribes:
- **Scenario tests**: multi-turn interactions, noisy inputs, tool failures
- **Adversarial suites**: prompt injections, tool confusion, hallucination traps
- **Feedback loops**: continuously update test sets from production data;
  "Each iteration builds on the last, failures shrink, the test suite grows"

### Production Metrics (from the article)

```
Task success rate (exact or graded)
Groundedness rate (output reflects source data vs. fabricated)
Tool success, timeout, and error rates
Loop and retry rate (agent repeating itself or retrying)
Plan length and step efficiency (reasoning steps or tool calls per answer)
p95 latency
Cost per successful task
Safety violation rate
Human escalation rate
```

### Guardrail Architecture (from the article)

```
Layer 1: Guardrail check ──sync or async──► Response
Layer 2: Guardrail check ──sync or async──► Response

Synchronous:  blocks response until check passes (safer, slower)
Asynchronous: sends response first, catches problems after (faster, riskier)

Concrete mitigation:
  - Block low-resource language prompts (most common bypass path)
  - Two-layer enforcement for defense-in-depth
  - Kill switch required from day one
```

### Architecture Evolution (from the article)

```
Single Agent (tools) ──► Supervisor + Sub-agents ──► Hierarchical
                                                      │
                                          ┌───────────┴───────────┐
                                     Domain Agent A         Domain Agent B
                                   (own tools+prompts)    (own tools+prompts)

Network/peer-to-peer: considered but rejected as substantially harder
to test and change compared to hierarchical.
```

### Minimum Reference Architecture (from the article)

Components:
- **Gateway**: authentication, authorization, rate limits, policies, routing
- **Tools & Memory Layer**: APIs, databases, vector stores, key-value stores
- **Observability**: traces, logs, metrics
- **Constraining knobs**: temperature, tool constraints, input/system prompts

### Agent Routing and Permissions (from the article)

The article describes domain-grouped agents with explicit permissions:
agents are scoped so that only authorized teams can use specific agents.
Example: during a security incident, an agent must not respond to queries
from someone outside the security team. Permissions are treated with the
same investment level as evaluation.

## Cross-References

- **Corroborates**: The companion PagerDuty SRE Agent architecture article
  ([blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md))
  corroborates several claims:
  - **Claim 3 (Context fatigue)** ↔ Existing note's Claim 2 (Context rot as
    a hard ceiling for single-agent architectures). Same failure mode under
    a different name; both cite the "Lost in the Middle" phenomenon.
  - **Claim 4 (Compounding errors)** ↔ Existing note's Claim 3 (Instruction
    overload creating inverse relationship between features and quality).
    Both describe the same structural problem: as agents accumulate more
    context/instructions/capabilities, output quality degrades.
  - **Claim 8 (Architecture evolution)** ↔ Existing note's Claim 6 (Three
    execution models), Claim 12 (Single-process simplification), and Claim
    16 (Build hard, ship simple). Both articles describe the single-agent →
    supervisor → hierarchical path. Both emphasize earning complexity.
  - **The companion article explicitly cites this article** (see existing
    note's Claim 1) as foundational framing for the AI-native vs.
    AI-assisted distinction.

- **Contradicts**: None identified. These two PagerDuty articles are
  complementary — the present article covers evaluation, metrics, guardrails,
  and UX (areas the companion article explicitly says it doesn't cover),
  while the companion covers implementation primitives (reactive loop,
  identity, transport, durability model).

- **Extends**: The companion SRE Agent architecture article
  ([blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md))
  in multiple dimensions:
  - The companion covers **how** to build the reactive loop, transport, and
    identity primitives. This article covers **what** to evaluate, **what**
    to measure, and **what** guardrails to enforce — the missing half of the
    production picture.
  - The companion explicitly notes it doesn't cover evaluation/accuracy
    metrics or cost data. This article fills both gaps with concrete metrics
    and a cost-per-successful-task framework.
  - This article adds the UX dimension (transparent reasoning) and memory
    architecture (knowledge graphs vs. RAG) that the companion doesn't
    address.

- **Novel**: Several contributions are new to the corpus:
  - **Five-pillar production readiness framework** (Reliability, Control,
    Visibility, Integration, Economics) — a taxonomy for evaluating agent
    system maturity not present in the companion article.
  - **Evaluation pipeline design** — golden datasets with what/how/who
    dimensions, LLM-as-a-judge automated scoring, CI-gated re-evaluation on
    every change, adversarial test suites.
  - **Context poisoning concept** — a named failure mode distinct from
    context fatigue or hallucination, describing how bad enterprise data
    propagates through agent working memory.
  - **Concrete metrics framework** — nine specific metrics including
    groundedness rate, cost per successful task, and human escalation rate.
  - **Prompt injection susceptibility data** — the 80-90% figure (Chang et
    al. 2026) and low-resource language bypass evidence.
  - **Guardrail classification** (sync vs. async) — a design pattern for
    trading off safety and latency.
  - **Knowledge graph vs. RAG argument** — for invalidation-aware,
    temporally-aware agent shared memory.
  - **Transparent UX finding** — showing reasoning steps builds trust and
    tolerance for latency.

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: This source provides the evaluation,
  metrics, and guardrail framework missing from the companion architecture
  article. Specific additions:
  - The five-pillar framework (Reliability, Control, Visibility, Integration,
    Economics) as a production-readiness checklist for agent systems.
  - The architecture evolution pattern (single → supervisor → hierarchical)
    as a recommended path, with the explicit warning not to start with
    peer-to-peer.
  - The deterministic-vs-probabilistic principle: audit agent code for LLM
    calls that could be replaced with deterministic code.
  - The domain-grouped agent pattern with explicit permissions.

- **Chapter 05 (LLM Ops Reliability)**: This source provides the strongest
  material for this chapter:
  - The evaluation pipeline design (golden datasets → LLM-as-a-judge → CI
    gates) as a recommended pattern for agent quality assurance.
  - The nine-metric framework (task success, groundedness, tool errors, p95
    latency, cost, safety violations, human escalation) as recommended
    observability metrics.
  - The guardrail architecture: defense-in-depth, sync/async classification,
    low-resource language blocking, kill switch requirement.
  - The context poisoning concept as a specific monitoring/alerting concern.
  - The "March of 9s" framing for reliability investment planning.
  - The transparent UX principle: agents should expose their reasoning
    to build trust, and observability platforms should capture traces of
    model input, reasoning path, tool choices, and sub-agent responses.

- **Chapter 00 (Principles)**: This source supports a new principle around
  "test what the user actually does" — deterministic tests don't work for
  natural-language systems; evaluation must be structural (golden datasets,
  LLM-as-a-judge) and continuous (CI-gated re-evaluation).

## Extraction Notes

- The source is a long-form blog post (~16 minute read) on PagerDuty's
  engineering blog. The companion article on end-to-end observability
  ("Building end-to-end observability for AI agents in production") linked
  within the article returned HTTP 404 at extraction time.
- No other sub-pages were followed. The article is self-contained and
  references academic papers as supporting evidence rather than as linked
  content to explore.
- Quotes were extracted via targeted WebFetch calls with explicit
  instruction to return verbatim text from the source. All quotes marked
  as direct are ≤125 characters and were confirmed as verbatim by the
  extraction tool. The Assayer should spot-check key quotes against the
  live URL.
- The article cites twelve academic references (Chang et al. 2026, Colelough
  & Regli 2025, Khalifa et al. 2025, Lightman et al. 2024, Marx & Dunaiski
  2026, Raspanti et al. 2025, Shen et al. 2024, Ullah et al. 2024, Yao et
  al. 2023, Yong et al. 2023). These were not independently fetched — they
  are cited here as they appear in the source bibliography.
- The source is rich in frameworks, patterns, and design guidance but does
  not provide quantitative production metrics (specific latency numbers,
  specific cost figures, accuracy percentages for their evaluation pipeline).
- The author (João Freitas) is the same author cited as foundational framing
  in the companion PagerDuty SRE Agent article (Vasylkovskyi et al.).
- No part of the source was paywalled. The article is publicly accessible on
  the PagerDuty Engineering Blog.
- Published June 11, 2026 — approximately one month before extraction. The
  patterns described are very recent and represent the current state of
  production agent thinking at PagerDuty.
