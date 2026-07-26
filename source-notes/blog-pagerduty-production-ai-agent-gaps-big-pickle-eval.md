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
issue: "#4-big-pickle-eval"
---

# Production AI Agents: Closing the Gaps Between Idea and Reality

> A PagerDuty Engineering practitioner writeup documenting the systemic
> reliability gaps, security vulnerabilities, and operational constraints
> encountered when moving AI agents from prototype to production. Introduces
> a five-pillar production-readiness framework, a concrete evaluation pipeline
> design, guardrail architecture, and a metrics framework — all grounded in
> experience shipping a multi-agent system at enterprise scale.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: João Freitas is a PagerDuty engineer with direct
  production experience building their multi-agent system. The article is
  published on PagerDuty's engineering blog and serves as the foundational
  framing piece cited by the companion SRE Agent deep-dive (Vasylkovskyi
  et al.). Claims are backed by citations to peer-reviewed research
  (Chang et al. 2026, Ullah et al. 2024, Yong et al. 2023, Shen et al.
  2024, Marx & Dunaiski 2026, Lightman et al. 2024, Khalifa et al. 2025,
  Raspanti et al. 2025, Colelough & Regli 2025, Yao et al. 2023).
- **Scope**: Covers the full productionization gap — why prototypes fail at
  scale, the five-pillar reliability framework, architectural evolution from
  single-agent to hierarchical, evaluation pipeline design, observable
  metrics, guardrail architecture, transparent UX, agent memory sharing
  (knowledge graphs vs. RAG), and cost/latency optimization. Does NOT cover:
  deep implementation details of the agent runtime (covered in the companion
  SRE Agent article), specific model choices, quantitative latency/cost
  numbers, or code-level implementation.

## Extracted Claims

### Claim 1: The prototype-to-production gap for AI agents is large and structural — demos are easy, reliability is hard
- **Evidence**: PagerDuty's direct experience from a year of shipping a
  multi-agent system. The article is structured around bridging this gap.
  Supported by the Karpathy "March of 9s" concept (Claim 16).
- **Confidence**: emerging
- **Quote**: "Going from an idea to a prototype today takes hours or minutes."
- **Our assessment**: This is the central thesis of the article. The
  distinction between "works in a demo" and "works in production" is widely
  acknowledged across practitioner communities. The article's contribution
  is cataloging the specific failure modes that cause the gap — non-
  determinism, context fatigue, compounding errors, prompt injection — not
  just asserting the gap exists.

### Claim 2: LLM non-determinism persists even with temperature set to zero, making agent behavior inherently unpredictable
- **Evidence**: Cites the statistical nature of LLMs — predicting the next
  most likely token rather than evaluating abstract rules. References Ullah
  et al. (2024) for LLMs' inability to reliably identify security
  vulnerabilities. Lists mitigations: neuro-symbolic approaches, RAG,
  strict constraints, deterministic execution, stepwise verification.
- **Confidence**: settled
- **Quote**: "the same input can produce different outputs, and you may still
  see hallucinations"
- **Our assessment**: Well-established across the literature. Even with
  temperature=0, floating-point non-determinism and model-update variability
  produce different outputs. The article correctly identifies this as a
  foundational challenge that makes deterministic software tests inadequate
  for agent evaluation.

### Claim 3: Context fatigue causes early prompt instructions to lose weight as token count grows, degrading agent behavior in long-running tasks
- **Evidence**: Described as a direct operational observation — in longer
  tasks the model "forgets" upfront constraints as the context window fills.
  Framed as a consequence of how LLMs weight tokens probabilistically.
- **Confidence**: settled
- **Quote**: "the early parts of your prompt start losing probabilistic weight
  as more tokens accumulate"
- **Our assessment**: Consistent with the "Lost in the Middle" literature
  (Liu et al. 2023) and corroborated by the companion PagerDuty SRE Agent
  article's "context rot" finding. This is a well-observed failure mode that
  creates a hard ceiling for single-agent architectures handling long
  investigations.

### Claim 4: Errors compound multiplicatively across multi-step agent workflows rather than averaging out
- **Evidence**: Each component (LLM, tools, APIs, retrieval, memory, other
  agents) has independent reliability characteristics. When chained, error
  rates multiply. Intensifies in multi-agent systems as integration protocols
  (DNS-AID, A2A) proliferate.
- **Confidence**: emerging
- **Quote**: "the errors multiply rather than average out"
- **Our assessment**: Critically important for system design. A five-step
  workflow with 95% reliability per step yields ~77% compound reliability,
  not 95%. The practical implication — system design must account for
  multiplicative error propagation — is under-discussed in agent
  literature. The article correctly notes that multi-agent systems amplify
  this effect.

### Claim 5: AI agents are highly susceptible to prompt injection, with reported rates in the 80-90% range, and guardrails can be bypassed via low-resource languages
- **Evidence**: Cites Chang et al. (2026) for the 80-90% prompt injection
  susceptibility rate. Cites Yong et al. (2023), Shen et al. (2024), and
  Marx & Dunaiski (2026) for the low-resource language bypass finding.
  PagerDuty's guardrail design (low-resource language blocking, two-layer
  enforcement) is a direct response.
- **Confidence**: settled
- **Quote**: "the majority of agents built today are susceptible to prompt
  injection, with reported rates in the 80-90% range"
- **Our assessment**: Strong evidence backing — multiple peer-reviewed
  citations. The 80-90% figure is sobering but well-sourced. The low-
  resource language bypass is independently documented across multiple
  studies. PagerDuty's practical contribution is translating academic
  findings into concrete guardrail designs (two-layer enforcement, language
  blocking).

### Claim 6: Context poisoning — stale, corrupted, or contradictory data filling an agent's working memory — propagates errors across agents and systems
- **Evidence**: Enterprise data is "siloed, inconsistent, incomplete, and
  poorly structured." When this data enters an agent's context window, it
  poisons the working memory. Combined with long-context issues, corrupted
  data propagates to other agents through shared context. Original concept
  from the article with a specific name and mechanism.
- **Confidence**: emerging
- **Quote**: "real enterprise data is usually siloed, inconsistent,
  incomplete, and poorly structured"
- **Our assessment**: A novel contribution — "context poisoning" is a
  distinct failure mode from hallucination or context fatigue. It describes
  bad ground-truth data corrupting the agent's reasoning base, with
  propagation risk in multi-agent systems. The knowledge graph discussion
  (Claim 13) is positioned as a partial mitigation.

### Claim 7: A five-pillar framework — Reliability, Control, Visibility, Integration, Economics — defines production readiness for AI agent systems
- **Evidence**: Derived from the Karpathy "March of 9s" concept, extending
  beyond raw reliability to operational concerns unique to agentic AI. Each
  pillar maps to concrete engineering decisions. The article notes trade-offs
  between pillars are possible (e.g., trading latency for groundedness via
  verification agents).
- **Confidence**: emerging
- **Quote**: "by missing one of these, you increase your production risk"
- **Our assessment**: A useful organizational framework, not a falsifiable
  claim. Well-structured — each pillar maps to concrete engineering
  concerns. It's one team's taxonomy and hasn't been independently validated,
  but it covers the dimensions that consistently appear in production-agent
  postmortems.

### Claim 8: Agent architecture should evolve from single-agent → supervisor → hierarchical, earning complexity rather than starting with it
- **Evidence**: PagerDuty's direct architectural evolution: single agent
  calling tools → accumulated responsibilities felt like an orchestrator →
  factored out a supervisor routing to specialized sub-agents → hierarchical
  pattern with domain-grouped agents. Network/peer-to-peer patterns
  considered but rejected as substantially harder to test and change.
- **Confidence**: emerging
- **Quote**: "the complexity of testing and changing a network or peer-to-peer
  system is substantially higher"
- **Our assessment**: Corroborated by the companion SRE Agent article's
  architectural evolution discussion. The evolutionary pattern (single →
  supervisor → hierarchical) is the same in both articles. The "earn
  complexity" advice is a recurring theme. The rejection of peer-to-peer
  for testability reasons is a practical constraint worth noting.

### Claim 9: Transparent UX — showing agent reasoning steps in real time — builds user trust and increases willingness to wait for agent responses
- **Evidence**: Concrete anecdote: early prototype displayed everything the
  agent did in real time; production version showed only the final answer.
  A product manager saw the prototype and requested transparency be added
  to production. Especially important in enterprise/regulated settings where
  trust makes the product usable. The team studied how large-scale AI
  players handle agentic experiences and adapted lessons for collaborative
  interfaces (Slack, Microsoft Teams).
- **Confidence**: anecdotal
- **Quote**: "Showing the agent's plans, steps, and reasoning as it runs is
  one of the simplest and most effective UX improvements"
- **Our assessment**: A compelling anecdote with direct product impact. The
  finding — a silent spinner frustrates users while a visible reasoning
  process builds trust — is consistent with broader UX research on
  perceived performance and transparency. The application to
  enterprise/regulated settings is a useful contextualization.

### Claim 10: Automated evaluation pipelines using golden datasets + LLM-as-a-judge + CI gates are essential for production-grade agent systems
- **Evidence**: Specific workflow: golden test questions (what/how/who
  dimensions) fed simultaneously to the agent under test and an expected
  responder generator; an LLM-as-a-judge compares outputs; results flow to
  monitoring. CI gates re-evaluate on every model/prompt/tool change. Builds
  out to scenario tests (multi-turn, noisy inputs, tool failures) and
  adversarial suites (prompt injections, tool confusion, hallucination traps).
  Initial golden sets cover ~95% of cases; feedback loops continuously update.
- **Confidence**: emerging
- **Quote**: "An 'LLM-as-a-judge' is then used to compare the agent's actual
  output against the expected output"
- **Our assessment**: One of the article's highest-value contributions. The
  what/how/who framework for golden dataset curation, the LLM-as-a-judge
  step, and CI integration provide actionable patterns. The adversarial
  testing suite is particularly notable — testing for prompt injection and
  hallucination, not just task accuracy. The ~95% initial coverage claim
  is notable but lacks the methodology details to assess independently.

### Claim 11: Not everything in an agent needs to be probabilistic — deterministic code should replace LLM calls where possible for speed, cost, and reliability
- **Evidence**: Two issues found in early versions: using very large models
  for simple problems, and using LLMs for tasks solvable with basic
  deterministic code. Framed as an optimization principle: build first,
  then identify and replace unnecessary LLM calls.
- **Confidence**: emerging
- **Quote**: "using a very large model to solve relatively simple problems"
- **Our assessment**: Practical and important observation. Connects to the
  companion SRE Agent article's discussion of IO-bound vs compute-bound
  workloads. The principle is straightforward but easy to miss when building
  agent-first systems — the temptation to use LLMs for everything is real.
  The "build first, then optimize" ordering is sensible given that model
  trends are rapidly changing.

### Claim 12: A concrete metrics framework should track task success, groundedness, tool error rates, p95 latency, cost per successful task, safety violations, and human escalation rate
- **Evidence**: Nine specific metrics enumerated: task success rate,
  groundedness rate, tool success/timeout/error rates, loop and retry rate,
  plan length, p95 latency, cost per successful task, safety violation rate,
  human escalation rate. Tracked in observability platform with
  LLMOps/AgentOps capabilities.
- **Confidence**: emerging
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Concrete, actionable set of metrics from production
  experience. The inclusion of "groundedness" (output reflects source data)
  and "cost per successful task" (not just cost per call) are particularly
  insightful — they measure quality and efficiency, not just throughput.
  The companion SRE Agent article explicitly says it doesn't cover metrics,
  making this article's coverage a valuable complement.

### Claim 13: Basic RAG is insufficient for agent shared memory — knowledge graphs with time awareness and invalidation awareness are needed, but tooling is immature
- **Evidence**: Concrete scenario: Agent A posts that the database is the
  problem. Agent B builds on that hypothesis. Ten minutes later, Agent C (or
  a human) discovers the database is fine — a dependency service returning
  bad responses made it appear slow. The "fact" has been invalidated and
  everything built on it must be revisited. RAG can't handle this because it
  lacks temporal/invalidation awareness and the ability to navigate
  relationships between facts.
- **Confidence**: emerging
- **Quote**: "basic RAG... starts falling short"
- **Our assessment**: Sophisticated analysis of a real multi-agent memory
  problem. The scenario is compelling and specific. The honest caveat about
  tooling immaturity adds credibility. Directly complements the companion
  SRE Agent article's discussion of shared context but goes deeper on the
  memory representation layer. The knowledge graph recommendation is
  directionally important but the article correctly flags that current
  tools aren't enterprise-ready.

### Claim 14: Guardrails require defense-in-depth with synchronous and asynchronous checks, and must block low-resource languages as one of the most common bypass paths
- **Evidence**: PagerDuty enforces guardrails at two layers. Low-resource
  language blocking is a specific, named mitigation. The article discusses
  the latency trade-off: synchronous checks block the response until the
  check passes (safer, slower), asynchronous checks send the response first
  and catch problems after (faster, riskier). Non-critical checks use async
  to avoid latency penalties.
- **Confidence**: emerging
- **Quote**: "we do not allow our agents to operate in low-resource
  languages, since that was one of the most common bypass paths we observed"
- **Our assessment**: The sync/async classification of guardrail checks is a
  practical design pattern applicable beyond PagerDuty. The low-resource
  language blocking is a specific, evidence-backed mitigation. The two-layer
  enforcement provides defense-in-depth without prescribing specific
  technology. The latency trade-off discussion is particularly useful for
  practitioners making real architecture decisions.

### Claim 15: Deterministic software tests are inadequate for evaluating natural-language agent systems where there is no single correct output
- **Evidence**: Test sets cover important use cases, but real users find
  unexpected input combinations via natural language prompting. More
  fundamentally, deterministic tests expect a single correct output — a
  paradigm that doesn't fit probabilistic, natural-language systems. This is
  the motivation for the LLM-as-a-judge evaluation approach.
- **Confidence**: settled
- **Quote**: "deterministic software tests do not work well with natural
  language systems, where there is no single correct output"
- **Our assessment**: Fundamentally correct and widely acknowledged in the
  LLM evaluation literature. The article's contribution is connecting this
  observation to the specific evaluation pipeline they built, making it
  actionable rather than theoretical.

### Claim 16: The "March of 9s" applies to AI agents — prototype reliability at ~90% requires redundant system layers, validation pipelines, fallback logic, and runtime error containment to improve
- **Evidence**: Attributes the concept to Andrej Karpathy. Reaching
  additional 9s beyond prototype-level (~90%) requires systematic investment
  in redundant layers, extensive validation, complex fallback logic, and
  runtime error containment. Used as framing for the five-pillar approach.
- **Confidence**: emerging
- **Quote**: "Andrej Karpathy named the process of increasing the reliability
  of your system as the 'March of 9s'"
- **Our assessment**: A useful framing concept rather than a verified law.
  Applied to agents, it correctly predicts that the jump from demo (~90%)
  to production (99%+) requires systematic investment, not incremental
  tweaks. The five-pillar framework is positioned as the operationalization
  of this concept.

## Concrete Artifacts

### Five Pillars Framework

```
Reliability  — predictable outcomes from a non-deterministic system
Control      — guardrails and permissions
Visibility   — observability and evaluation
Integration  — real workflow embedding
Economics    — scalable cost and latency
```

Trade-offs between pillars are possible: e.g., if groundedness matters more
than latency, introduce a verification agent to fact-check answers, increasing
both reliability and latency.

### Evaluation Pipeline Design

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

Additional testing layers:
- Scenario tests: multi-turn interactions, noisy inputs, tool failures
- Adversarial suites: prompt injections, tool confusion, hallucination traps
- Feedback loops: continuously update test sets from production data

### Production Metrics

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

### Guardrail Architecture

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

### Architecture Evolution

```
Single Agent (tools) ──► Supervisor + Sub-agents ──► Hierarchical
                                                      │
                                          ┌───────────┴───────────┐
                                     Domain Agent A         Domain Agent B
                                   (own tools+prompts)    (own tools+prompts)

Network/peer-to-peer: considered but rejected as substantially harder
to test and change compared to hierarchical.
```

### Minimum Reference Architecture

- **Gateway**: authentication, authorization, rate limits, policies, routing
- **Tools & Memory Layer**: APIs, databases, vector stores, key-value stores
- **Observability**: traces, logs, metrics
- **Constraining knobs**: temperature, tool constraints, input/system prompts

## Cross-References

- **Corroborates**: The companion PagerDuty SRE Agent architecture article
  ([blog-pagerduty-sre-agent-architecture.md](blog-pagerduty-sre-agent-architecture.md)):
  - **Claim 3 (Context fatigue)** ↔ Existing note's Claim 2 (Context rot as a
    hard ceiling for single-agent architectures). Same failure mode under
    different names; both cite the "Lost in the Middle" phenomenon.
  - **Claim 8 (Architecture evolution)** ↔ Existing note's Claim 6 (Three
    execution models), Claim 12 (Single-process simplification), and Claim
    16 (Build hard, ship simple). Both describe the single-agent →
    supervisor → hierarchical path and emphasize earning complexity.
  - **Claim 10 (Evaluation pipeline)** ↔ Existing note's explicit statement
    that it doesn't cover evaluation/accuracy metrics — this article fills
    that gap.
  - The companion article explicitly cites this article (see existing
    note's Claim 1) as foundational framing for the AI-native vs.
    AI-assisted distinction.

- **Extends**: The companion SRE Agent architecture article — this article
  covers **what** to evaluate, **what** to measure, and **what** guardrails
  to enforce, while the companion covers **how** to build the reactive loop,
  transport, and identity primitives. Together they form the complete
  production picture.

- **Contradicts**: None identified. The two PagerDuty articles are
  complementary — this article covers evaluation, metrics, guardrails, and
  UX (areas the companion explicitly doesn't cover), while the companion
  covers implementation primitives.

- **Related notes (from miner-related-notes.md):**
  - `source-notes/blog-pagerduty-sre-agent-architecture.md`: Cited above as
    the companion article (Corroborates/Extends). Both are from PagerDuty
    Engineering on the same multi-agent production experience.
  - `source-notes/blog-anthropic-building-effective-agents.md`: Anthropic's
    taxonomy of agent architecture patterns. Its Claim 3 (simplicity-first
    principle) parallels this article's Claim 11 (deterministic over LLM
    where possible). Both argue for minimizing agent complexity. The
    Anthropic post covers workflow vs. agent distinction (Claim 2) while
    this article covers production failure modes — complementary perspectives.
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md`: SRE
    Prodcast on retail/gaming — not directly relevant to AI agent
    productionization patterns. Different domain, different concerns.
  - `source-notes/docs-google-sre-prodcast-04-05-furino-slos.md`: SRE
    Prodcast on SLOs/error budgets — tangentially relevant (agent
    reliability investment parallels SLO thinking) but not directly
    overlapping.
  - `source-notes/docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`: Google
    SRE Prodcast on AI for SRE — uses golden datasets for validation
    (Claim 4), similar to this article's evaluation pipeline design. Both
    emphasize golden data for measuring LLM accuracy in SRE contexts.

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

- **Chapter 05 (LLM Ops Reliability)**: Strongest material for this chapter:
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
    to build trust.

- **Chapter 00 (Principles)**: Supports a new principle around
  "test what the user actually does" — deterministic tests don't work for
  natural-language systems; evaluation must be structural (golden datasets,
  LLM-as-a-judge) and continuous (CI-gated re-evaluation).

## Extraction Notes

- The source is a long-form blog post (~16 minute read) on PagerDuty's
  engineering blog. The companion article on end-to-end observability
  ("Building end-to-end observability for AI agents in production") linked
  within the article returned HTTP 404 at extraction time.
- No sub-pages were followed. The article is self-contained and references
  academic papers as supporting evidence rather than as linked content to
  explore.
- All quotes were extracted via direct reading of the fetched source text.
  Quotes marked as direct were verified against the source. The Assayer
  should spot-check key quotes against the live URL.
- The article cites twelve academic references (Chang et al. 2026, Colelough
  & Regli 2025, Khalifa et al. 2025, Lightman et al. 2024, Marx & Dunaiski
  2026, Raspanti et al. 2025, Shen et al. 2024, Ullah et al. 2024, Yao et
  al. 2023, Yong et al. 2023). These were not independently fetched — they
  are cited as they appear in the source bibliography.
- The source is rich in frameworks, patterns, and design guidance but does
  not provide quantitative production metrics (specific latency numbers,
  specific cost figures, accuracy percentages for the evaluation pipeline).
- Published June 11, 2026 — approximately six weeks before extraction.
  The patterns described are very recent.
- Baseline note `blog-pagerduty-production-ai-agent-gaps.md` was read and
  compared during extraction. This eval note was written independently
  before reviewing the baseline in detail, then cross-checked for claim
  coverage.
