---
source_url: https://www.anthropic.com/engineering/building-effective-agents
source_type: blog-post
title: "Building effective agents"
author: "Erik S. and Barry Zhang (Anthropic Engineering)"
date_published: 2024-12-19
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: settled
issue: "#567"
---

# Building effective agents

> The canonical taxonomy of agentic-system architecture from Anthropic Engineering —
> defining the workflow-vs-agent distinction, cataloging five workflow patterns (prompt
> chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer),
> and providing concrete ACI (Agent-Computer Interface) tool design principles with
> simplicity-first design philosophy, based on experience with dozens of teams.

## Source Context

- **Type**: blog-post (practitioner writeup from model provider)
- **Author credibility**: Highest available for the subject matter — Anthropic Engineering,
  the creators of Claude, writing from direct experience working with "dozens of teams
  building LLM agents across industries." The authors (Erik S. and Barry Zhang) are
  Anthropic engineers who have built agents internally and consulted with customers.
  The post is primary-source architectural guidance from the model provider, not a
  vendor thought-piece — the claims are grounded in observed patterns across many
  implementations. Published Dec 19, 2024; the pattern taxonomy remains the dominant
  industry reference for agent architecture design as of July 2026.
- **Scope**: Covers (1) the workflow-vs-agent architectural distinction, (2) when to use
  agents vs simpler solutions, (3) framework selection advice, (4) the augmented LLM
  building block, (5) five workflow patterns with when-to-use guidance and examples,
  (6) agent design (autonomous loop, stopping conditions, human-in-the-loop), (7) ACI
  tool design principles with concrete examples, (8) two application case studies
  (customer support, coding agents). Does NOT cover: specific code implementations
  (links to a cookbook), quantitative benchmarks, failure rates, or operational metrics.

## Extracted Claims

### Claim 1: The most successful agent implementations use simple, composable patterns rather than complex frameworks
- **Evidence**: Direct observation from "dozens of teams building LLM agents across
  industries." The post states this as its opening thesis and the driving theme throughout.
- **Confidence**: settled
- **Quote**: "Over the past year, we've worked with dozens of teams building large language
  model (LLM) agents across industries. Consistently, the most successful implementations
  weren't using complex frameworks or specialized libraries. Instead, they were building
  with simple, composable patterns."
- **Our assessment**: This is the article's core thesis, stated as direct observation from
  Anthropic's customer work. It is consistent with the corpus's existing practitioner
  evidence (the PagerDuty SRE Agent articles also describe simplifying from distributed
  to single-process architectures). High authority — this is the model provider's
  synthesis of cross-industry patterns, not a single-team experience.

### Claim 2: There is an important architectural distinction between workflows (predefined code paths) and agents (LLMs dynamically directing their own process)
- **Evidence**: The post defines both terms explicitly and grounds the distinction in
  architectural control — whether the code path is predetermined or the LLM decides
  dynamically.
- **Confidence**: settled
- **Quote**: "Workflows are systems where LLMs and tools are orchestrated through predefined
  code paths. Agents, on the other hand, are systems where LLMs dynamically direct their
  own processes and tool usage, maintaining control over how they accomplish tasks."
- **Our assessment**: This is the foundational taxonomy of the entire post. It provides a
  clean, practical distinction that maps onto the Google SRE Prodcast's agent spectrum
  (static algorithm → LLM-augmented → full agent) from a different angle. The distinction
  is actionable: teams can decide upfront whether their use case fits a fixed-path workflow
  or needs open-ended agent autonomy.

### Claim 3: The simplest solution should always be tried first — often a single LLM call with retrieval and in-context examples is enough, and agentic systems should only be added when simpler solutions fall short
- **Evidence**: Stated as direct recommendation throughout the post, emphasized in the
  summary and the "When (and when not) to use agents" section.
- **Confidence**: settled
- **Quote**: "When building applications with LLMs, we recommend finding the simplest solution
  possible, and only increasing complexity when needed. This might mean not building agentic
  systems at all."
- **Quote**: "For many applications, however, optimizing single LLM calls with retrieval and
  in-context examples is usually enough."
- **Our assessment**: This simplicity-first principle is a recurring theme across multiple
  post sections and is the load-bearing framing for the entire workflow/agent taxonomy.
  Directly applicable to the guide's principles — it provides a crisp rule for deciding
  when agent complexity is justified.

### Claim 4: Agentic systems trade latency and cost for better task performance — this tradeoff must be explicitly evaluated before choosing an agent architecture
- **Evidence**: Stated in the "When (and when not) to use agents" section as a direct
  cost-benefit observation.
- **Confidence**: settled
- **Quote**: "Agentic systems often trade latency and cost for better task performance, and
  you should consider when this tradeoff makes sense."
- **Our assessment**: A clear, quantified framing of the agent decision. The post does not
  provide specific latency/cost numbers but establishes the tradeoff principle. This
  directly supports the guide's economics/decision-framework material.

### Claim 5: Workflows offer predictability and consistency for well-defined tasks; agents are better when flexibility and model-driven decision-making are needed at scale
- **Evidence**: Stated as the decision criterion in the "When to use agents" section.
- **Confidence**: settled
- **Quote**: "When more complexity is warranted, workflows offer predictability and
  consistency for well-defined tasks, whereas agents are the better option when flexibility
  and model-driven decision-making are needed at scale."
- **Our assessment**: This pairs with Claim 3 to form a two-step decision framework: (1) try
  the simplest solution first, (2) if complexity is needed, choose workflows for
  predictability and agents for flexibility. This is the actionable decision rule.

### Claim 6: Start by using LLM APIs directly before adopting frameworks — many patterns can be implemented in a few lines of code, and frameworks often obscure the underlying prompts and responses
- **Evidence**: Direct recommendation. The post lists several frameworks (Claude Agent SDK,
  Strands Agents SDK, Rivet, Vellum) and gives specific caution about debugging difficulty.
- **Confidence**: settled
- **Quote**: "We suggest that developers start by using LLM APIs directly: many patterns can
  be implemented in a few lines of code. If you do use a framework, ensure you understand
  the underlying code. Incorrect assumptions about what's under the hood are a common
  source of customer error."
- **Our assessment**: This is directly actionable guidance from Anthropic's customer
  experience. It reframes the framework question from "which framework?" to "do you need
  one at all?" and cautions that framework abstraction layers trade debugability for
  convenience. Supports the LiteLLM LAP note's "harness over framework" finding from a
  different angle.

### Claim 7: The augmented LLM — an LLM enhanced with retrieval, tools, and memory — is the basic building block of all agentic systems
- **Evidence**: The post introduces this as the foundational building block before any
  workflow or agent pattern. It notes that current models "can actively use these
  capabilities — generating their own search queries, selecting appropriate tools, and
  determining what information to retain."
- **Confidence**: settled
- **Quote**: "The basic building block of agentic systems is an LLM enhanced with
  augmentations such as retrieval, tools, and memory."
- **Our assessment**: This frames augmentation not as an optional add-on but as the core
  abstraction. The post recommends focusing on tailoring these capabilities to the use
  case and ensuring a well-documented interface. The MCP protocol is cited as one
  implementation approach. This is the foundational layer that all workflow and agent
  patterns build on.

### Claim 8: Prompt chaining — decomposing a task into sequential steps where each LLM call processes the previous output — trades latency for accuracy by making each call an easier task
- **Evidence**: The post describes the pattern with a diagram, when-to-use guidance, and two
  concrete examples (marketing copy translation, outline-check-write workflow).
- **Confidence**: settled
- **Quote**: "Prompt chaining decomposes a task into a sequence of steps, where each LLM
  call processes the output of the previous one. You can add programmatic checks (see
  'gate' in the diagram below) on any intermediate steps to ensure that the process is
  still on track."
- **Our assessment**: This is the first of five workflow patterns. The key design element
  is the programmatic gate — deterministic checks between steps that can halt the workflow
  if intermediate criteria aren't met. This provides a clean boundary between "LLM work"
  and "programmatic guard."

### Claim 9: Routing classifies an input and directs it to a specialized followup task, enabling separation of concerns and more specialized prompts — without routing, optimizing for one input type can hurt others
- **Evidence**: The post describes routing with a diagram, when-to-use guidance, and two
  examples (customer service routing, model-size routing for cost optimization).
- **Confidence**: settled
- **Quote**: "Routing classifies an input and directs it to a specialized followup task.
  This workflow allows for separation of concerns, and building more specialized prompts.
  Without this workflow, optimizing for one kind of input can hurt performance on other
  inputs."
- **Our assessment**: The key insight is the negative consequence of *not* routing:
  optimizing for one input type degrades others. The model-size routing example (easy
  queries to Haiku, hard to Sonnet) is a concrete cost optimization pattern directly
  relevant to the guide's economics material.

### Claim 10: Parallelization has two key variations — sectioning (breaking a task into independent subtasks run in parallel) and voting (running the same task multiple times for diverse outputs)
- **Evidence**: The post describes both variations with when-to-use guidance and examples
  (sectioning: guardrails + core response separation, LLM evaluation automation; voting:
  code vulnerability review, content moderation with vote thresholds).
- **Confidence**: settled
- **Quote**: "LLMs can sometimes work simultaneously on a task and have their outputs
  aggregated programmatically. This workflow, parallelization, manifests in two key
  variations: Sectioning: Breaking a task into independent subtasks run in parallel.
  Voting: Running the same task multiple times to get diverse outputs."
- **Our assessment**: The sectioning-vs-voting distinction is practically important.
  Sectioning is for parallel independent subtasks; voting is for confidence through
  redundancy. The guardrails example (one model instance processes queries while another
  screens for inappropriate content) is a directly deployable pattern for safe agent design.

### Claim 11: The orchestrator-workers pattern — a central LLM dynamically breaks down tasks, delegates to worker LLMs, and synthesizes results — is best for complex tasks where subtasks can't be predicted in advance
- **Evidence**: The post describes the pattern with a diagram, when-to-use guidance, and
  two examples (coding products with multi-file changes, multi-source search tasks).
- **Confidence**: settled
- **Quote**: "In the orchestrator-workers workflow, a central LLM dynamically breaks down
  tasks, delegates them to worker LLMs, and synthesizes their results."
- **Our assessment**: The key distinction from parallelization is flexibility — subtasks
  are not predefined but determined by the orchestrator based on the specific input. This
  is the pattern that most directly maps to the PagerDuty SRE Agent architecture
  (supervisor routing to sub-agents), providing foundational justification for that design.

### Claim 12: The evaluator-optimizer pattern — one LLM generates a response while another evaluates and provides feedback in a loop — is effective when clear evaluation criteria exist and iterative refinement provides measurable value
- **Evidence**: The post describes the pattern with a diagram, when-to-use guidance, and
  two examples (literary translation, complex search with multiple rounds).
- **Confidence**: settled
- **Quote**: "In the evaluator-optimizer workflow, one LLM call generates a response while
  another provides evaluation and feedback in a loop."
- **Our assessment**: The post identifies two signs of good fit: (1) LLM responses can be
  demonstrably improved when a human articulates feedback, and (2) the LLM can provide
  such feedback. This maps directly onto the LLM-as-a-judge evaluation pattern from the
  PagerDuty production AI agent gaps article, linking workflow architecture to evaluation
  methodology.

### Claim 13: Agents are typically just LLMs using tools based on environmental feedback in a loop — their implementation is often straightforward despite handling sophisticated tasks
- **Evidence**: The post explicitly demystifies agents: "their implementation is often
  straightforward" and they are "typically just LLMs using tools based on environmental
  feedback in a loop."
- **Confidence**: settled
- **Quote**: "Agents can handle sophisticated tasks, but their implementation is often
  straightforward. They are typically just LLMs using tools based on environmental feedback
  in a loop."
- **Our assessment**: This is a deliberate demystification of agent complexity. The post
  emphasizes that the hard part is not the agent loop itself but the *tool design* (see
  Claim 16). This reframing is valuable for the guide's Ch03 — it separates "agent"
  (simple loop) from "good agent" (well-designed tools).

### Claim 14: Agents must plan and operate independently, but should pause for human feedback at checkpoints or when encountering blockers, and stopping conditions (like max iterations) are essential for control
- **Evidence**: The post describes the agent lifecycle: begin with human instruction, plan
  and operate independently, potentially return to human for input, terminate on completion
  or stopping condition.
- **Confidence**: settled
- **Quote**: "Once the task is clear, agents plan and operate independently, potentially
  returning to the human for further information or judgement. During execution, it's
  crucial for the agents to gain 'ground truth' from the environment at each step (such
  as tool call results or code execution) to assess its progress. Agents can then pause
  for human feedback at checkpoints or when encountering blockers. The task often terminates
  upon completion, but it's also common to include stopping conditions (such as a maximum
  number of iterations) to maintain control."
- **Our assessment**: This provides a concrete agent lifecycle model with specific control
  mechanisms (checkpoints, stopping conditions). The "ground truth from environment" emphasis
  is important — the agent must not rely on its internal state but must verify against real
  tool outputs. This directly supports the guide's human-in-the-loop guidance.

### Claim 15: Autonomous agents compound errors and increase costs — requiring extensive sandboxed testing, guardrails, and trust in the model's decision-making before production deployment
- **Evidence**: The post warns about the risks of autonomous agents in the "When to use
  agents" section.
- **Confidence**: settled
- **Quote**: "The autonomous nature of agents means higher costs, and the potential for
  compounding errors. We recommend extensive testing in sandboxed environments, along with
  the appropriate guardrails."
- **Our assessment**: This is a critical caution from the model provider. The compounding
  errors warning is consistent with the PagerDuty production AI agent gaps article
  (Claim 4: "errors multiply rather than average out"). The recommendation for sandboxed
  environments matches the Google SRE Prodcast's "production is not a sandbox" insight.

### Claim 16: Tool design (ACI — Agent-Computer Interface) requires as much prompt engineering attention as prompts themselves — the format, naming, and structure of tools directly determines agent success or failure
- **Evidence**: The post devotes an entire appendix to ACI tool design. It gives specific
  examples: diff vs full-file rewrite, absolute vs relative filepaths, JSON vs markdown
  formatting, and the principle of poka-yoke (mistake-proofing) tools.
- **Confidence**: settled
- **Quote**: "Tool definitions and specifications should be given just as much prompt
  engineering attention as your overall prompts."
- **Our assessment**: The ACI concept is the post's most actionable contribution for the
  guide's agent-building material. The specific recommendations are concrete and
  testable:
  - Give the model enough tokens to "think" before acting
  - Keep format close to what the model has seen naturally in text
  - Avoid formatting overhead (line counts, string escaping)
  - Invest in ACI as much as HCI
  - Include example usage in tool definitions
  - Poka-yoke: change arguments to make mistakes harder

### Claim 17: Absolute filepaths in tool definitions eliminated SWE-bench agent errors caused by relative paths — a concrete example of ACI optimization producing measurable improvement
- **Evidence**: The post states this as a direct observation from building their SWE-bench
  coding agent.
- **Confidence**: settled
- **Quote**: "For example, we found that the model would make mistakes with tools using
  relative filepaths after the agent had moved out of the root directory. To fix this,
  we changed the tool to always require absolute filepaths — and we found that the model
  used this method flawlessly."
- **Our assessment**: This is a specific, measurable ACI optimization. The post explicitly
  states they "spent more time optimizing our tools than the overall prompt" for their
  SWE-bench agent, underscoring the ACI principle. This is an exact parallel to the Google
  SRE Prodcast's timezone-wrapping fix (S4E9 Claim 11) — both are cases of normalizing tool
  input formats to eliminate agent confusion.

### Claim 18: Customer support and coding agents are the two most promising agent applications because they combine conversation and action, have clear success criteria, enable feedback loops, and integrate meaningful human oversight
- **Evidence**: The post dedicates Appendix 1 to both domains, describing why each is a
  natural fit for agent architectures and noting that customer support implementations
  use "usage-based pricing models that charge only for successful resolutions."
- **Confidence**: emerging
- **Quote**: "Our work with customers has revealed two particularly promising applications
  for AI agents that demonstrate the practical value of the patterns discussed above."
- **Our assessment**: The post's characterization of customer support (conversation +
  tool integration, clear success measurement) and coding (verifiable via tests,
  structured problem space) provides a framework for identifying other good agent
  candidates. The claim that both "require both conversation and action, have clear
  success criteria, enable feedback loops, and integrate meaningful human oversight"
  is a reusable heuristic.

### Claim 19: Adding complexity should only happen when it demonstrably improves outcomes — the key to success is measuring performance and iterating
- **Evidence**: Stated in the "Combining and customizing these patterns" section and
  reinforced in the summary.
- **Confidence**: settled
- **Quote**: "To repeat: you should consider adding complexity only when it demonstrably
  improves outcomes."
- **Our assessment**: This closes the loop on the simplicity-first theme. The post frames
  complexity not as a design choice but as an earned outcome validated by measurement.
  This principle directly supports the guide's "measure before you automate" stance.

### Claim 20: Three core principles for building agents — maintain simplicity in design, prioritize transparency by explicitly showing the agent's planning steps, and carefully craft the ACI through thorough tool documentation and testing
- **Evidence**: The post's summary distillation of everything preceding it.
- **Confidence**: settled
- **Quote**: "When implementing agents, we try to follow three core principles: 1. Maintain
  simplicity in your agent's design. 2. Prioritize transparency by explicitly showing the
  agent's planning steps. 3. Carefully craft your agent-computer interface (ACI) through
  thorough tool documentation and testing."
- **Our assessment**: These three principles form a concise, memorable checklist. The
  transparency principle (showing planning steps) corroborates the PagerDuty production
  AI agent gaps article's transparent UX finding (Claim 9). The ACI principle is this
  post's unique contribution. The simplicity principle ties back to Claim 1.

## Concrete Artifacts

### Workflow pattern decision tree (reconstructed from the article's categorizations)

```
Start: What's the simplest solution?
  └─ Is a single LLM call + retrieval/in-context examples enough?
       ├─ YES → Stop. Don't build an agentic system.
       └─ NO → Do you need complexity?
                 ├─ For well-defined, predictable tasks:
                 │   Choose one or more workflow patterns:
                 │   ├─ Prompt chaining — sequential steps with programmatic gates
                 │   ├─ Routing — classify input, direct to specialized handler
                 │   ├─ Parallelization — sectioning (independent subtasks)
                 │   │                     or voting (multiple attempts)
                 │   ├─ Orchestrator-workers — dynamic task decomposition
                 │   └─ Evaluator-optimizer — generate → evaluate → iterate
                 │
                 └─ For open-ended, flexible, scale tasks:
                     Use agents — LLM uses tools in a loop with:
                     ├─ Stopping conditions (max iterations, completion)
                     ├─ Human checkpoints for feedback
                     └─ Ground truth verification at each step
```

### ACI tool design principles (verbatim from the article)

```
General format guidance:
  - Give the model enough tokens to "think" before acting
  - Keep format close to what the model has seen naturally occurring in text
  - Avoid formatting overhead (line counts, string escaping)

ACI-specific guidance:
  - Put yourself in the model's shoes — is the tool obvious to use?
  - A good tool definition includes example usage, edge cases,
    input format requirements, and clear boundaries from other tools
  - Change parameter names or descriptions to make things obvious
  - Treat it as "writing a great docstring for a junior developer"
  - Test how the model uses your tools in the workbench
  - Poka-yoke your tools — change args to make mistakes harder

Concrete example (SWE-bench):
  - Problem: model made mistakes with relative filepaths after
    moving out of root directory
  - Fix: require absolute filepaths → "the model used this
    method flawlessly"
  - Key: "We actually spent more time optimizing our tools than
    the overall prompt."
```

### Agent lifecycle (from the article)

```
1. Human provides command or interactive discussion
2. Agent plans and operates independently
3. At each step: agent gains "ground truth" from environment
   (tool call results, code execution)
4. Agent pauses at checkpoints or blockers for human feedback
5. Task terminates on:
   a. Completion (success)
   b. Stopping condition reached (max iterations, etc.)
   c. Human intervention
```

### Three core principles (verbatim from the article)

```
1. Maintain simplicity in your agent's design.
2. Prioritize transparency by explicitly showing the agent's planning steps.
3. Carefully craft your agent-computer interface (ACI) through thorough
   tool documentation and testing.
```

### Augmented LLM building block (reconstructed from the article's diagram)

```
┌─────────────────────────────────────────────────────┐
│                  Augmented LLM                       │
│  ┌──────────────────────────────────────────────┐   │
│  │              LLM (core model)                 │   │
│  │  Generates search queries, selects tools,     │   │
│  │  determines what information to retain        │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                     │
│    ┌────────────┴────────────┐                        │
│    │       Augmentations      │                        │
│    ├──────────────────────────┤                        │
│    │ Retrieval  │  Tools  │  Memory  │                │
│    └──────────────────────────┘                        │
└─────────────────────────────────────────────────────┘
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-04-09-ai-agents.md` **Claim 1** (agent spectrum: static algorithm → LLM-augmented → full agent). Anthropic's workflow-vs-agent distinction maps onto the same spectrum; workflows correspond to the middle "LLM-augmented" range and agents to the "full agent" end. **Claim 2** (read/write capability split). Anthropic's "ground truth from environment" emphasis at each step corroborates the Google SRE podcast's requirement for explicit verification before writes. **Claim 3** (human-in-the-loop guardrails). Anthropic's checkpoint/pause pattern for human feedback matches the Google SRE "human permission before writes" design. **Claim 15** (don't insulate humans from learning). Anthropic's transparency principle (show planning steps) and simplicity-first principle align with the Google SRE podcast's "don't remove humans from the learning loop" (Ironies of Automation).
  - `blog-pagerduty-production-ai-agent-gaps.md` **Claim 11** (deterministic code should replace LLM calls where possible) corroborates Anthropic's simplicity-first principle (optimize single LLM calls before adding agent complexity). **Claim 9** (transparent UX — showing agent reasoning steps builds user trust) corroborates Anthropic's second core principle (prioritize transparency by showing planning steps). **Claim 4** (errors compound multiplicatively) corroborates Anthropic's warning about "potential for compounding errors" in autonomous agents (Claim 15).
  - `blog-pagerduty-sre-agent-architecture.md` **Claim 6** (three execution models for multi-agent investigation) corroborates Anthropic's orchestrator-workers pattern and parallelization pattern. Both describe the same architectural choice: how to decompose work across multiple LLM calls. **Claim 12** (IO-bound agents don't benefit from service boundaries) is consistent with the spirit of Anthropic's "simplicity in design" principle.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` — Anthropic's augmented LLM design principle (tailor tools/retrieval/memory to the use case, ensure easy interface) corroborates the Honeycomb note's argument that agent observability must span tools and retrieval, not just LLM calls.
  - `blog-promptfoo-model-upgrades-break-agent-safety.md` **Claim 2** (model upgrades must be treated as security changes). Anthropic's framework caution (start with direct API calls, understand underlying code) reinforces the same principle: abstraction layers hide model behavior changes.

- **Contradicts**: None — this post is the foundational taxonomy that is widely cited, not contradicted, by later sources in the corpus.

- **Extends**:
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — The Google SRE Prodcast S4E9 provides the SRE practitioner's perspective on what agents *do* in production (pre-on-caller triage, golden-label evaluation, postmortem trajectory matching). This Anthropic article provides the model provider's perspective on *how to architect* the agents themselves (the five workflow patterns, ACI tool design). Together they form a complete picture: this article says "what patterns to build," the Prodcast says "how to operate and evaluate them."
  - `blog-pagerduty-production-ai-agent-gaps.md` — The PagerDuty article's five-pillar framework and evaluation pipeline are *operational* concerns for productionizing agents. This Anthropic article provides the *architectural* foundation those pillars sit on — the workflow/agent patterns and ACI principles that determine what needs to be evaluated and guarded.
  - `blog-pagerduty-sre-agent-architecture.md` — The PagerDuty SRE Agent article describes a specific instantiation of the orchestrator-workers pattern. This Anthropic article provides the general pattern taxonomy that justifies and contextualizes that architecture. Post's Claim 11 (orchestrator-workers) is the general case; the PagerDuty reactive loop is a specific implementation.

- **Novel**: To the corpus, this source introduces:
  - The **workflow-vs-agent architectural distinction** — a formal decision rule for choosing between predetermined code paths and LLM-directed control
  - The **five workflow pattern taxonomy** (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) — a complete catalog of agentic system patterns
  - The **ACI (Agent-Computer Interface) design discipline** — tool design as a first-class engineering concern requiring the same rigor as HCI
  - The **augmented LLM building block** concept — tools + retrieval + memory as a composable foundation for all agentic systems
  - The **simplicity-first decision framework** — start simple, earn complexity
  - The **three core principles** (simplicity, transparency, ACI) as a concise checklist
  - Concrete **poka-yoke tool design examples** (absolute filepaths, format selection)
  - The **clarity on frameworks**: start with direct API calls, understand underlying code before adopting frameworks

## Guide Impact

- **Chapter 00 (Principles)**: Add the simplicity-first principle (Claim 3, Claim 19) — build the simplest solution, add complexity only when it demonstrably improves outcomes. Add the tradeoff awareness (Claim 4): agentic systems trade latency and cost for task performance. Add the three core principles (Claim 20) as a concise agent-building checklist. The framework caution (Claim 6) should be a principle: "start with direct API calls; know what's under your abstractions."

- **Chapter 03 (Runbooks and Agents)**: This source provides the primary architectural framework for the entire chapter:
  - Add the workflow-vs-agent distinction (Claim 2) as the foundational decision point — is the task a predefined path (workflow) or open-ended (agent)?
  - Add the five workflow patterns (Claims 8-12) as a pattern catalog with when-to-use guidance. Each pattern should become a subsection with its decision criteria and examples.
  - Add the augmented LLM (Claim 7) as the basic building block — all agentic systems begin with tools + retrieval + memory.
  - Add the agent lifecycle model (Claim 14) — plan, operate, verify ground truth, checkpoint for human feedback, terminate.
  - Add the ACI tool design principles (Claim 16, Claim 17) — tool definition quality determines agent success. Include the poka-yoke examples and the absolute-filepath fix.
  - Add the two-step decision framework (Claims 3+5): try the simplest solution → if complexity is needed, choose workflows for predictability or agents for flexibility.

- **Chapter 04 (On-Call Tooling)**: Add the agent lifecycle model's human-in-the-loop pattern (Claim 14) — agents must pause for human feedback at checkpoints or blockers, and stopping conditions (max iterations) are control mechanisms. The ACI principles (Claim 16) apply directly to on-call tool design — tools used by agents in incident response must be poka-yoked with clear input formats.

## Extraction Notes

- Source was read in full via WebFetch (markdown extraction from the rendered Anthropic Engineering blog page). The post is self-contained with two appendices (Agents in Practice, Prompt Engineering Your Tools) — both were read in full. No sub-pages were followed beyond the main article; the post links to a cookbook (external platform page) and the MCP announcement, which were not followed per MINER.md §1's "up to 5 linked pages" guidance — the post is architecturally complete without them.
- All quoted passages were copied character-for-character from the fetched markdown output. The Assayer should spot-check key quotes against the live URL (https://www.anthropic.com/engineering/building-effective-agents).
- Published December 19, 2024 — outside the Dec 2025 freshness cutoff. However, as the triage notes confirm, the pattern vocabulary remains the dominant industry reference as of July 2026 and no existing source note covers this content. The advice is evergreen architectural guidance, not a time-sensitive technology update.
- `confidence_overall` set to `settled`: this is primary-source architectural guidance from the model provider (Anthropic Engineering) based on experience with dozens of teams, and the pattern taxonomy has been validated through widespread industry adoption over the subsequent 18+ months.
- Miner-related-notes candidates processed:
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — **Cited** (Corroborates). Strongest cross-reference in the corpus.
  - `docs-google-sre-prodcast-05-06-ai-safety.md` — **Dismissed**. Covers production AI safety, not agent architecture patterns.
  - `blog-promptfoo-model-upgrades-break-agent-safety.md` — **Cited** (Corroborates peripherally through Claim 6's framework/shared-control principle).
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**. Covers sociotechnical complexity, not agent architecture.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — **Dismissed**. Covers database reliability, not agent architecture.
  - `blog-pagerduty-sre-agent-architecture.md` — **Cited** (Extends). Specific orchestrator-workers implementation corroborates Claim 11.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — **Dismissed**. Covers config change workflows, not agent architecture.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — **Dismissed**. Covers incident tooling, not agent architecture.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — **Dismissed**. Covers retail/gaming SRE, unrelated.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — **Dismissed**. Covers SLOs, unrelated.
- Additional source-notes cross-references searched manually:
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` — not directly relevant; covers summarization and AI-assisted SRE
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` — **Cited** (Corroborates through augmented LLM principle)
  - `blog-promptfoo-ai-regulation-2025.md` — **Dismissed**. Regulatory angle, not architecture.
  - `blog-litellm-lap-internal-agent-30-percent.md` — **Dismissed**. Covers specific implementation (brain/sandbox split), not foundational architecture.
- No contradiction issue filed: this source's claims are fully consistent with all existing notes. The simplicity-first principle and ACI discipline complement rather than oppose any existing corpus claims.
