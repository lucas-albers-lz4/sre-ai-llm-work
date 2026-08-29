# Runbooks and Agents

> Encoding operational knowledge so agents can act safely — the agent
> spectrum, read-vs-write boundaries, pre-on-caller triage pattern, agent
> evaluation methodology, and the emerging multi-runtime agent control plane.

## Runbooks as executable spec

Remediation runbooks are the raw material for automation: instructions like
"log in to X, execute this command, check the output, restart Y if you see…"
are "essentially pseudocode to someone with software development skills!"
[source: docs-google-sre-eliminating-toil, Claim 2] [settled].

Google's three-stage ladder runs from partially automating the human-run
script, to fully automated detection plus remediation (no human runs the
script), to submitting a patch so the software never breaks that way again.

**Rule**: Write runbooks that survive being read by an agent — exact commands,
named steps, explicit decision points. A runbook only a human can parse is not
an automation input.

## Skills are the packaging unit for runbook knowledge

Runbook knowledge reaches agents as skills — a self-contained directory with a
`SKILL.md` entrypoint describing general rules and a `references/` folder of
per-workflow docs filled with specific best practices
[source: docs-langfuse-agent-skill, Claim 3] [settled]. The open Agent Skills
standard has third-party implementations: Langfuse ships an open-source skill
for Claude Code, Cursor, and Windsurf [source: docs-langfuse-agent-skill,
Claim 1] [settled].

Vendors frame skills as conditioning — an agent with the skill installed is
"conditioned to follow best practices," which Langfuse asserts makes coding
agents "produce significantly better results" — an effectiveness claim with no
metrics attached, so take the mechanism, not the magnitude [source:
docs-langfuse-agent-skill, Claim 2] [emerging].

A skill loads progressively: the frontmatter is always in the agent's context
so it knows when the skill applies; the full instructions and reference docs
load only on demand, keeping context usage low [source: docs-langfuse-agent-skill,
Claim 4] [settled].

```
skills/langfuse/            # github.com/langfuse/skills (MIT)
├── SKILL.md                # frontmatter + core principles — always loaded
└── references/             # loaded on demand — one file per workflow
    ├── instrumentation.md
    ├── prompt-migration.md
    ├── setting-up-evals.md
    ├── judge-calibration.md
    ├── error-analysis.md
    ├── ci-cd.md
    └── ... (15 reference files total)
```
*Extracted from [source: docs-langfuse-agent-skill, Concrete Artifacts].*

Install is a directory operation — the npm skills CLI, a Cursor plugin, or a
manual clone + symlink:

```bash
npx skills add langfuse/skills --skill "langfuse"      # --agent <id> targets one agent
# or manual install:
git clone https://github.com/langfuse/skills.git /path/to/langfuse-skills
ln -s /path/to/langfuse-skills/skills/langfuse /path/to/<agent-skill-root>/skills/langfuse
```
*Extracted from [source: docs-langfuse-agent-skill, Concrete Artifacts].*

The prompts such skills enable are agent-run ops work — "Show me the last 10
traces with a score below 0.5", "Migrate the system prompt in src/agent.ts to
Langfuse prompt management" [source: docs-langfuse-agent-skill, Concrete
Artifacts] [settled].

**Rule**: Package operational knowledge as a skill — a frontmatter `SKILL.md`
plus per-workflow reference files — so the agent always knows when the
procedure applies and loads the details on demand. A skill is just a
directory: install by copy, symlink, or a skills CLI.

## Automation-safety baseline for agents

### Risk assessment before every action

Google requires that every action be assessed for its safety before execution —
including changes that reduce serving capacity or redundancy — and that
"automation should default to human operators if it runs into an unsafe
condition" [source: docs-google-sre-eliminating-toil, Claim 11] [settled].

The read-ops-can-spike-load warning is the non-obvious one for agents: an
agent hammering telemetry backends with ad hoc queries is itself a load
source.

**Rule**: Gate every agent action — reads included — through a risk check
before execution, and route to a human on anything the check cannot clear.

### Don't transcribe the human workflow

You rarely want to literally transcribe a human workflow into a machine
workflow — break the documented manual work into separable, composable
components that other automation can reuse, and don't let automation eliminate
human understanding of what's going wrong
[source: docs-google-sre-eliminating-toil, Claim 12] [settled].

**Rule**: Treat automation as a re-design opportunity, not transcription. If
an agent runbook is a verbatim copy of the human steps, decompose it into
reusable pieces first.

### Automation is a long-lived liability

Automation is not fire-and-forget: once adopted it may become entrenched for a
long time, inflexible automation makes systems brittle to change, and Google
recommends "establishing an error budget for antitoil automation"
[source: docs-google-sre-eliminating-toil, Claim 14] [settled].

**Rule**: Maintain agent-run automation like software, with an error budget of
its own. An agent whose failures burn the service's reliability budget is
toil in disguise.

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

## Structured tool contracts over free-form interfaces

A maximally-flexible agent-facing interface — a generic key/value "bag," an
untyped dict, a free-text tool schema — looks simple but shifts the design
burden onto every client that must document and maintain the informal
contract. Google's case study of an abstract API vs structured types makes
the trade explicit: "Structured data types like Google's Protocol Buffers or
Apache Thrift might seem more complex than their abstract general-purpose
alternatives, but they result in simpler end-to-end solutions because they
force upfront design decisions and documentation"
[source: docs-google-sre-simplicity, Claim 7] [settled].

**Rule**: Define agent-facing tool and service contracts as structured,
typed schemas that force design decisions at definition time. A tool schema
that says "here's a dict, figure it out" transfers its complexity to every
agent that calls it.

### Failure class at the process boundary

Structured contracts extend to exit codes. Langfuse's CLI wraps the entire
Langfuse API — generated from the full OpenAPI spec so every endpoint is a
CLI command [source: docs-langfuse-cli, Claim 2] [settled] — and its failures
exit with a machine-readable code so agents "can tell what went wrong without
parsing stderr": usage (2), configuration (3), network (4), HTTP failure (5),
local errors (6) [source: docs-langfuse-cli, Claim 3] [settled].

```
2  usage error          4  network failure
3  configuration error  5  HTTP failure
6  local error
```

**Rule**: A CLI an agent or an automated runbook invokes should signal failure
*class* at the process boundary — usage vs config vs network vs HTTP vs local —
so automation branches on the exit code instead of scraping free-text stderr.

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

### Alerts that dispatch runbooks

An alert can also trigger a runbook directly, with no agent in the loop.
Langfuse automations pair a trigger (an alert severity change) with an
external action — a Slack message, an HMAC-signed webhook POST, or a GitHub
Actions `workflow_dispatch` event [source: docs-langfuse-alerts, Claim 7]
[settled]. A severity change firing `workflow_dispatch` is the alert→CI/CD
bridge: the runbook (a self-healing action, dataset refresh, experiment
re-run) starts on the alert, not on human reaction.

Notification plumbing needs a circuit breaker of its own: after five
consecutive delivery failures, Langfuse disables the automation's trigger and
requires manual re-enablement once the endpoint is restored [source:
docs-langfuse-alerts, Claim 8] [settled].

**Rule**: Wire high-signal alert classes to a CI/CD `workflow_dispatch`
runbook, and give every notification channel a delivery-failure circuit
breaker that stops retrying a dead endpoint and demands a human re-enable.

## The human incident-tooling baseline an agent populates

PagerDuty's incident-response tooling is a three-part topology an AI incident
agent should populate rather than replace [source:
docs-google-sre-incident-response, Claim 11] [settled]:

- **Source of truth**: "We store all of our on-call information, service
  ownership, postmortems, incident metadata, and the like, in PagerDuty. This
  allows us to rapidly assemble the right team when something goes wrong."
- **Scribe-led ledger**: a dedicated `#incident-war-room` channel "used mostly
  as an information ledger for the scribe, who captures actions, owners, and
  timestamps."
- **Decision bridge**: "We prefer that all coordination decisions are made in
  the conference call, and that decision outcomes are recorded in Slack" —
  with every call recorded so the timeline can be recreated.

**Rule**: An AI incident agent is most useful as the scribe and timeline
reconstructor of this topology — read the metadata source of truth, write the
action ledger, keep the decision record complete. Don't let the agent replace
the human decision bridge.

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

---
*Sources for this chapter: docs-google-sre-prodcast-04-09-ai-agents,
blog-litellm-agents-are-the-new-llms, blog-promptfoo-ai-orchestrated-cyberattacks,
blog-promptfoo-ai-regulation-2025, docs-google-sre-eliminating-toil,
docs-google-sre-incident-response, docs-google-sre-simplicity,
docs-langfuse-agent-skill, docs-langfuse-alerts, docs-langfuse-cli*
*Last updated: 2026-08-29*
