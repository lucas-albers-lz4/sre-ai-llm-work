# Runbooks and Agents

> Encoding operational knowledge so agents can act safely — the agent
> spectrum, read-vs-write boundaries, pre-on-caller triage pattern, agent
> evaluation methodology, and the emerging multi-runtime agent control plane.
> Anthropic's workflow-vs-agent taxonomy and five workflow patterns provide the
> architectural vocabulary; Google's Safety Trifecta and L0–L4 autonomy levels
> govern how far an agent may act; Agent Skills package procedural knowledge
> for reuse.

## The workflow-agent architectural distinction

### Workflows vs. agents

There is an important architectural distinction between workflows (systems where
LLMs and tools are orchestrated through predefined code paths) and agents
(systems where LLMs dynamically direct their own processes and tool usage)
[source: blog-anthropic-building-effective-agents, Claim 2] [settled].

Workflows offer predictability and consistency for well-defined tasks; agents
are better when flexibility and model-driven decision-making are needed at scale
[source: blog-anthropic-building-effective-agents, Claim 5] [settled].

**Rule**: Before choosing an architecture, ask whether the task needs
predetermined code paths (workflow) or open-ended LLM-directed control (agent).
Most production systems today are workflows with bounded LLM augmentation.

### The augmented LLM building block

All agentic systems build on a single foundation: an LLM enhanced with
retrieval, tools, and memory. The model actively uses these capabilities —
generating its own search queries, selecting appropriate tools, and determining
what to retain [source: blog-anthropic-building-effective-agents, Claim 7]
[settled].

**Rule**: Start by tailoring the three augmentations (retrieval, tools, memory)
to your use case. The augmented LLM is the composable building block that every
workflow and agent pattern layers on top of.

### Five workflow patterns

Anthropic's pattern taxonomy, distilled from dozens of teams building LLM agents,
catalogs five reusable workflow patterns
[source: blog-anthropic-building-effective-agents, Claims 8-12] [settled]:

1. **Prompt chaining** — decompose a task into sequential steps where each LLM
   call processes the previous output. Add programmatic gates between steps to
   halt if intermediate criteria aren't met. Trades latency for accuracy.

2. **Routing** — classify input and direct it to a specialized handler. Without
   routing, optimizing for one input type degrades others. Example: easy queries
   to a fast model, hard queries to a stronger one.

3. **Parallelization** — two variants: *sectioning* (break a task into
   independent subtasks run in parallel) and *voting* (run the same task
   multiple times for diverse outputs, aggregate).

4. **Orchestrator-workers** — a central LLM dynamically breaks down tasks,
   delegates to worker LLMs, and synthesizes results. Best for complex tasks
   where subtasks can't be predicted in advance.

5. **Evaluator-optimizer** — one LLM generates, another evaluates and provides
   feedback in a loop. Effective when clear evaluation criteria exist and
   iterative refinement provides measurable value.

**Rule**: Choose the workflow pattern by the shape of the task: sequential
steps with gates → chaining; heterogeneous inputs → routing; independent
subtasks → parallelization; unpredictable decomposition → orchestrator-workers;
iterable output → evaluator-optimizer.

### Simplicity-first: earn complexity

> When building applications with LLMs, we recommend finding the simplest solution
> possible, and only increasing complexity when needed. This might mean not
> building agentic systems at all.
> [source: blog-anthropic-building-effective-agents, Claim 3] [settled]

The most successful agent implementations use simple, composable patterns rather
than complex frameworks [source: blog-anthropic-building-effective-agents,
Claim 1] [settled]. A single LLM call with retrieval and in-context examples is
often enough — agentic complexity should only be added when it demonstrably
improves outcomes [source: blog-anthropic-building-effective-agents, Claim 19]
[settled].

**Rule**: Start with a single LLM call + retrieval. Only add workflow/agent
patterns when measurement shows simpler approaches fall short. Complexity is
earned, not chosen.

### ACI: Tool design is as important as prompt design

Tool definitions deserve as much engineering attention as prompts. The format,
naming, and structure of tools directly determines whether an agent succeeds or
fails [source: blog-anthropic-building-effective-agents, Claim 16] [settled].

Concrete ACI principles:
- Give the model enough tokens to "think" before acting
- Keep format close to what the model has seen naturally in text
- Avoid formatting overhead (line counts, string escaping)
- Include example usage in tool definitions
- Poka-yoke: change arguments to make mistakes harder

Example: Anthropic's SWE-bench agent made mistakes with relative filepaths after
moving out of the root directory. Changing the tool to require absolute
filepaths eliminated the error class entirely — "We actually spent more time
optimizing our tools than the overall prompt"
[source: blog-anthropic-building-effective-agents, Claim 17, Concrete Artifacts]
[settled].

**Rule**: Invest in ACI as much as HCI. Test how the model uses your tools;
redesign the tool interface when the model consistently misuses it.

## The agent spectrum

### Static algorithm to full agent

An "agent" is best understood as a spectrum
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 1] [settled]:

1. **Static deterministic algorithm** — fixed sequence of steps; you can
   work through it with pen and paper.
2. **LLM-augmented algorithm** — a static algorithm with one or more steps
   replaced by an LLM call (e.g., summarization, classification).
3. **Full agent** — no fixed script; the agent receives an input and
   dynamically constructs its own step sequence using tools.

Most of what works reliably in production today sits at level 2: one-shot
summarization and pre-on-caller triage with bounded tool access
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 4] [settled].

**Rule**: Grade every agent deployment by its position on this spectrum.
Full agents (level 3) need sandboxing, human approval gates for writes, and
trajectory-level evaluation. Don't grant level-3 autonomy to an agent you're
evaluating at level-2 rigor.

### Read vs. write capabilities

Agent capabilities split into two categories
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 2] [settled]:

- **Read**: fetching context not in training data (logs, metrics, dashboards,
  documentation). Safe to grant broadly.
- **Write**: world-modification with side effects (triggering rollouts,
  modifying configs, executing commands). Hard to predict when and how the
  agent will invoke these.

> The tools and the capabilities that you give to the agent, you need to
> know what you are giving it because knowing or predicting how and when
> they are going to be called is not that trivial.

**Rule**: Default-deny all write capabilities. Every write action requires
explicit human approval. Run writes in a sandbox; actions that escape the
sandbox need a second permission check.

## The pre-on-caller triage pattern

### Agent as first responder

When an alert fires, an agent steps in before the human reaches their desk.
In the ~3–4 minutes before the on-caller arrives, the agent runs the common
triage steps: release check, error-rate diff, log correlation. By the time
the human arrives, the agent has either found the root cause or ruled out a
set of mitigations — but the human still makes the call and applies changes
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 5] [settled].

> So when the alert gets triggered, we have some use cases where the agent
> steps in first. By the time the human gets to their desk, which is
> typically three or four minutes… the agent has already done a lot of the
> common steps that the on-caller would have done.

**Rule**: Deploy agents as pre-on-callers that triage and recommend before
the human arrives — not as autonomous responders that act without review.
The agent's job is to compress the time-to-clue, not to remove the human
from the decision path.

### One-shot summarization works today

One-shot alert summarization — feeding the agent logs, metrics, and error
traces and asking it to summarize the situation — works reliably well in
production. The LLM weeds signal from noise across thousands of log lines and
can surface a hidden error via large-context "needle in a haystack" search
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 4] [settled].

**Rule**: Start with summarization. It is the lowest-risk, highest-payoff
AI integration for on-call — the agent reads, summarizes, and recommends;
the human decides and acts.

## Agent evaluation in production

### Golden labels from historical incidents

Google evaluates production agents by replaying historical incident
trajectories and comparing the agent's actions to what the on-caller actually
did. The key challenge: historical incident data is retained for limited
windows, so evaluation coverage degrades over time unless data is
deliberately preserved for eval
[source: docs-google-sre-prodcast-04-09-ai-agents, Claims 7, 8, 10] [settled].

> Production has no sandbox. You cannot roll back an agent action in
> production the way you can roll back a bad deploy. So you must evaluate
> the agent's trajectory before it acts.

**Rule**: Preserve incident trajectories (alert → human actions → resolution)
as evaluation datasets. Replay them against agent changes before deployment.
The eval gold standard is "did the agent take the same actions the on-caller
took, and if not, would its alternative actions have been safe?"

### Generic mitigations taxonomy

Agents should have a catalog of safe, pre-audited mitigations they can
recommend or apply: restart, rollback, scale-up, drain-traffic, fail-over.
Each mitigation carries preconditions (what must be true before it's
applicable) and a blast-radius estimate
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 12] [settled].

**Rule**: Build a named, version-controlled catalog of allowed mitigations
before letting an agent recommend actions. An agent should never invent a
mitigation — it should select from the catalog and cite which precondition
triggered the match.

### Proactive change review

Beyond incident response, agents can review proposed production changes
(config pushes, binary rollouts) for risk signals before they land. The agent
checks: has this change pattern caused incidents before? Does the blast
radius exceed the error budget? Are the affected components currently
healthy? [source: docs-google-sre-prodcast-04-09-ai-agents, Claim 14]
[settled].

**Rule**: Run the same agent that triages incidents against proposed changes
before they ship. A change that the agent flags as matching a known-incident
pattern should require explicit overrule, not silent proceed.

## Where NOT to use LLMs

Google's SRE agent teams explicitly limit LLM use
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 15] [settled]:

- Don't use an LLM where a regex, static rule, or specialist model fits.
  If the problem is "parse this structured log line for an error code," a
  regex is faster, cheaper, and deterministic.
- Don't use an LLM where it could insulate a human from learning. An agent
  that silently handles an incident class removes the on-caller's opportunity
  to build the mental model needed for the next novel incident (Ironies of
  Automation).

**Rule**: An LLM is the right tool when the input is unstructured and the
output requires synthesis across sources. For structured-input/structured-output
tasks, use deterministic tooling. For tasks where human learning is the
goal, AI should surface questions, not answers.

## The emerging agent control plane

### Multi-runtime fragmentation is real

Agent infrastructure is separating into layers — models, harnesses (Claude
Code, Codex, OpenCode), and runtimes (Claude Managed Agents, Bedrock
AgentCore) — and teams will not consolidate on a single runtime
[source: blog-litellm-agents-are-the-new-llms, Claim 1, Claim 2] [emerging].

Coding agents may run on Bedrock AgentCore; data agents inside Databricks or
Snowflake; internal workflow agents on custom infrastructure. This means
"which runtime owns this agent?" is becoming an operational concern.

> Agent runtimes expose similar primitives — agents, sessions, events, tools —
> but they do not expose them through the same APIs. Anyone can build a list
> of agents. The harder problem is invocation.

**Rule**: Don't assume a single runtime for your agent fleet. Plan for a
registry that tracks which runtime each agent lives on, and design agent
invocation interfaces that abstract over runtime-specific APIs.

### The control plane's four verbs

The proposed agent control plane must manage agents across runtimes with four
capabilities: register, invoke, observe, and govern
[source: blog-litellm-agents-are-the-new-llms, Claim 4, Claim 9] [emerging].

This is the agent-stack mirror of the LLM-gateway pattern: just as gateways
standardized model-call access, a control plane would standardize agent-session
access — with the critical difference that agent sessions are stateful,
long-running, and tool-heavy, making the control plane a harder problem
than a model gateway
[source: blog-litellm-agents-are-the-new-llms, Claim 5] [emerging].

**Rule**: Your agent observability and governance surface must span runtimes.
The same four verbs an LLM gateway applies to model calls (route, log,
track spend, enforce auth) should apply to agent sessions (register, invoke,
observe, govern). But the cross-runtime agent API layer is explicitly unsolved —
plan for fragmentation, not turnkey unification
[source: blog-litellm-agents-are-the-new-llms, Claim 8] [emerging].

### The "harnesses" layer

Between raw models and deployed runtimes sits a distinct layer of agent
frameworks/CLIs: Claude Code, Codex, OpenCode, Hermes, DeepAgents
[source: blog-litellm-agents-are-the-new-llms, Claim 7, Concrete Artifacts]
[emerging].

These harnesses are where tool definitions, safety parameters, and
permission models are configured — the same concerns a control plane would
govern at the fleet level.

**Rule**: Standardize harness configuration (tool allowlists, permission
models, sandbox boundaries) across your agent fleet. A harness with
unrestricted tool access is the attacker's playbook entry point — see the
five-phase Claude Code extortion campaign
[source: blog-promptfoo-ai-orchestrated-cyberattacks, Claim 4] [emerging].

### Rollback-behavior testing

Agentic systems that can take actions (modify records, execute code, trigger
rollouts) must be tested for rollback behavior — if the agent takes a wrong
action, can it undo it?
[source: blog-promptfoo-ai-regulation-2025, Claim 13] [emerging].

Test tool selection, error handling, and rollback under adversarial
conditions, not just cooperative ones
[source: blog-promptfoo-ai-regulation-2025, Claim 12] [emerging]:

- If your agent uses retrieval, test retrieval quality.
- If it uses tools, test tool selection and error handling.
- If it maintains state across turns, test behavior at different context lengths.
- If it reads untrusted input, test adversarial conditions, not just cooperative ones.

**Rule**: For every tool the agent can invoke, test what happens when the
tool returns an error, a partial result, or a maliciously crafted response.
An agent that handles cooperative tool calls but fails on adversarial ones is
not production-ready.

## Agent governance and safety architecture

### The Safety Trifecta

Google SRE's governance model for AI-in-production rests on three pillars
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 2] [settled]:

1. **Transparency** — AI actions and decisions must be observable and
   understandable. Agents must log their chain of thought: signals used,
   hypotheses considered, reasons for action choice, and confidence level.

2. **Real-time Risk Evaluation** — every proposed agent action must be assessed
   against current production context: ongoing deployments, error budget status,
   active incidents, and time of day. An action that is low-risk under normal
   conditions may be high-risk during a regional peak.

3. **Progressive Authorization** — agents are not granted full production access
   on day one. They are released at lower autonomy levels (human-approved) and
   scaled up based on demonstrated reliability.

**Rule**: Adopt the Safety Trifecta as your governance checklist. If you can't
say "yes" to all three pillars for a given agent deployment, the agent is not
ready for production.

### SRE AI Autonomy Levels (L0–L4)

Google defines a five-level maturity model across five operational dimensions
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 3] [settled]:

```
Level    Monitor    Investigate   Mitigate    Actuate     Self-Direct
L0       Auto       Human         Human       Human       Human
L1       Auto       Auto          Human       Human       Human
L2       Auto       Auto          Human       Auto        Human
L3       Auto       Auto          Auto        Auto        Human
L4       Auto       Auto          Auto        Auto        Auto
```

Gating criteria between levels:
- L0→L1: adoption of monitoring/investigation automation tools
- L1→L2: confidence in reliable identification of correct actions
- L2→L3: trust and robust safety controls — rigor "substantially higher,
  proportional to the risk of unsupervised actions"
- L3→L4: ability to perform multi-step resolution for complex, dynamic situations

Google's own AI Operator currently operates at L2–L3: autonomous for minor
incidents, human-approval-required for critical operations
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 12] [settled].

**Rule**: Grade your agent deployments on L0–L4. Most teams should target L1
first (assisted investigation) and only advance to L2+ after proven reliability.
The jump from L2 to L3 is the hardest — it requires the Safety Trifecta to be
fully operational.

### The Actus pattern: decouple reasoning from execution

Google's Actus is a dedicated actuation control plane that sits between AI
reasoning and production mutation
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 5] [settled]:

```
Phase 1 — Plan: Agent submits an EvaluateAction request. Actus hydrates
  parameters and translates LLM intent into a concrete, verifiable execution plan.
Phase 2 — Safety Gate: Mandatory dry-runs, justification verification (action
  targets an open incident), concurrent action checks. If Actus detects elevated
  risk, it auto-downgrades from L3 to L2, routing to a human for approval.
Phase 3 — Guard: Maintains long-running operation state, polling infrastructure
  for success/failure. A centralized Red Button lets SREs instantly pause all
  in-flight agentic actions or globally revoke L3 permissions.
```

The key architectural insight: "By decoupling the reasoning engine from the
execution engine, no matter how rapidly AI models evolve, their ability to
mutate production remains strictly governed by deterministic, human-controlled
safety boundaries."

**Rule**: Never let an agent directly execute production mutations. Place a
deterministic, auditable control plane (like Actus) between the LLM's reasoning
and the production action. The control plane must support mandatory dry-runs,
risk-scored autonomy, and an emergency stop.

### Four architectural guardrails

Google's production agent architecture requires four concrete controls
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 4] [settled]:

1. **No ambient access** — agent identities must be distinct from humans,
   strongly authenticated, with on-demand access. "Agentic systems must not
   operate with standing human-like credentials — a single errant prompt
   bringing down global serving infrastructure is a severe risk."
2. **Agentic circuit breakers** — strict, agent-specific rate limits and
   automated circuit breakers. Actions must be highly interruptible.
3. **Mandatory dry-run support** — every API an agent can call must support a
   declarative `dry_run=true` mode.
4. **Zero-trust actuation** — agents must only interface with tooling that
   possesses intrinsic, deterministic safety mechanisms.

**Rule**: Audit your agent's tool inventory against all four guardrails before
production deployment. A tool that lacks dry-run support or can't be
interrupted is not safe for agentic invocation.

### AI Operator: autonomous mitigation at L2–L3

Google's AI Operator is the first responder to production alerts, operating
across thousands of incidents
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 12] [settled].
Key design decisions:

- **Token budget management** — uses the minimum set of tokens per step because
  chain-of-thought can have a long horizon and "strict token management prevents
  the LLM from losing context or hallucinating over time."
- **Structured mitigation catalog** — selects from a catalog of enrichers,
  specialized skills, and few-shot prompts encoded as text protos, not
  free-form reasoning.
- **Sub-agent spawning** — creates specialized sub-agents for deeper analysis
  of specific signals.
- **CoT UI with human comments** — chain of thought is surfaced in a centralized
  UI with per-step commenting, enabling human oversight without blocking the
  agent.
- **Automatic bug filing** — when the evaluation loop detects a failure, it
  auto-generates a critique and files a bug with a concrete implementation plan.
- **Escalation with full history** — if the agent cannot identify root cause or
  the scenario falls outside safe boundaries, it immediately escalates to a
  human with synthesized investigation history.

**Rule**: An autonomous mitigation agent needs five things: token budget
management, a structured (not free-form) action catalog, human-visible CoT,
clear escalation triggers, and an automated evaluation feedback loop.

## Packaging procedural knowledge for agents

### Agent Skills: reusable, discoverable, progressive

Anthropic's Agent Skills are filesystem folders containing instructions,
scripts, and resources that agents can discover and load dynamically
[source: blog-anthropic-agent-skills, Claim 1] [settled].

A skill is a directory with a `SKILL.md` file containing YAML frontmatter
(required: `name` and `description`) and a body with instructions. Additional
files (reference docs, Python scripts) can be linked from SKILL.md
[source: blog-anthropic-agent-skills, Claim 2] [settled].

### Progressive disclosure: three levels

Skills load in three levels to conserve context window
[source: blog-anthropic-agent-skills, Claims 3-4] [settled]:

```
Level 1 (startup): name + description of every installed skill
  → Agent decides: "is this skill relevant?"

Level 2 (on demand): full SKILL.md body
  → Core instructions, references to linked files

Level 3+ (on demand): linked files within the skill directory
  → Agent reads only what the specific sub-task needs
```

This means the total context bundled into a skill is "effectively unbounded" —
the agent reads only what's needed, when it's needed.

**Rule**: Structure agent instructions as skills with progressive disclosure.
Put only the name and description in the system prompt; load detailed
instructions on demand. Separate mutually exclusive contexts into different
files to reduce token usage [source: blog-anthropic-agent-skills, Claim 7]
[emerging].

### Code-as-tool in skills

Skills can include pre-written Python scripts for the agent to execute.
Deterministic code is cheaper, more reliable, and more consistent than LLM
token generation for operations like sorting, parsing, or form-field extraction
[source: blog-anthropic-agent-skills, Claim 5] [settled].

**Rule**: When a skill requires a deterministic, repeatable operation (parsing,
sorting, data extraction), embed it as a Python script in the skill directory.
Let the LLM decide *when* to use the script, but let code perform the action.

### Skills complement MCP

Skills teach agents *how* to accomplish tasks using tools, while MCP provides
the tools themselves — skills are the procedural knowledge layer above the tool
layer [source: blog-anthropic-agent-skills, Claim 11] [emerging].

**Rule**: Use MCP for tool provisioning (what the agent can call); use skills
for workflow knowledge (how to combine those tools to accomplish a task).

### Skill authorship: start with evaluation

Build skills incrementally based on observed gaps, not upfront specification
[source: blog-anthropic-agent-skills, Claim 6] [emerging]:

1. Run agents on representative tasks and observe where they struggle.
2. Capture successful approaches and common mistakes into reusable skills.
3. Monitor how agents use the skill and iterate — pay special attention to the
   name and description, since these determine when the agent triggers the
   skill [source: blog-anthropic-agent-skills, Claim 8] [emerging].
4. If an agent goes off track using a skill, ask it to self-reflect on what
   went wrong [source: blog-anthropic-agent-skills, Claim 9] [emerging].

PagerDuty's SRE Agent implements a similar pattern: teams encode runbooks into
skills using a `create-pagerduty-skill` CLI tool that converts existing
documentation into executable agent procedures
[source: blog-pagerduty-sre-agent-triage, Claim 3] [emerging].

**Rule**: Don't pre-build skills speculatively. Identify real gaps empirically,
build skills to close them, and iterate based on observed agent behavior. The
skill's name and description are the critical trigger signals.

---
*Sources for this chapter: docs-google-sre-prodcast-04-09-ai-agents,
docs-google-sre-ai-engineering-reliable-operations,
blog-anthropic-building-effective-agents, blog-anthropic-agent-skills,
blog-litellm-agents-are-the-new-llms,
blog-pagerduty-sre-agent-triage, blog-promptfoo-ai-orchestrated-cyberattacks,
blog-promptfoo-ai-regulation-2025*
*Last updated: 2026-08-11*
