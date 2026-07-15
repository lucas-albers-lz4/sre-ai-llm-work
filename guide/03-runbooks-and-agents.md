# Runbooks and Agents

> Encoding operational knowledge so agents can act safely — the agent
> spectrum, read-vs-write boundaries, pre-on-caller triage pattern, agent
> evaluation methodology, and the emerging multi-runtime agent control plane.

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
[source: docs-google-sre-prodcast-04-09-ai-agents, Claims 6-8 — evaluation
methodology] [settled].

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
[source: docs-google-sre-prodcast-04-09-ai-agents, Claims 9-10 — Generic
Mitigations] [settled].

**Rule**: Build a named, version-controlled catalog of allowed mitigations
before letting an agent recommend actions. An agent should never invent a
mitigation — it should select from the catalog and cite which precondition
triggered the match.

### Proactive change review

Beyond incident response, agents can review proposed production changes
(config pushes, binary rollouts) for risk signals before they land. The agent
checks: has this change pattern caused incidents before? Does the blast
radius exceed the error budget? Are the affected components currently
healthy? [source: docs-google-sre-prodcast-04-09-ai-agents, Claim 11-12]
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

---
*Sources for this chapter: docs-google-sre-prodcast-04-09-ai-agents,
blog-litellm-agents-are-the-new-llms, blog-promptfoo-ai-orchestrated-cyberattacks,
blog-promptfoo-ai-regulation-2025*
*Last updated: 2026-07-15*
