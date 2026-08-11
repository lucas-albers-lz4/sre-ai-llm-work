# Principles

> Mental models for using AI/LLMs in SRE work — and for treating LLM systems
> as production dependencies that need reliability engineering.

## Working principles

1. **Verification over generation.** AI can draft hypotheses faster than you
   can validate them against dashboards, traces, and blast radius. The scarce
   resource is confirmation, not text. `[editorial]`

2. **Keep humans on the paging path until trust is earned.** Shadow → suggest →
   act, never the reverse. Google's production AI agents default-deny
   world-mutating actions and require explicit human permission before writes
   [source: docs-google-sre-prodcast-04-09-ai-agents, Claim 3] [settled].
   `[editorial + sourced]`

3. **Encode ops knowledge outside the chat.** Runbooks, SLOs, and service
   catalogs beat prompt folklore. `[editorial]`

4. **Toil reduction must not create silent failure modes.** If an agent
   "fixes" something, the change must be observable and reversible. Rollback
   behavior must be tested — if the agent takes a wrong action, can it undo
   it? [source: blog-promptfoo-ai-regulation-2025, Claim 13] [emerging].
   `[editorial + sourced]`

5. **LLM services need SLOs too.** Latency, error rate, eval drift, and cost
   are first-class reliability signals. `[editorial]`

6. **Change is the dominant incident source — make it safe, don't freeze it.**
   "In Google's experience, a majority of incidents are triggered by binary
   or configuration pushes," and the answer is SLOs, error budgets, and
   canarying — measuring change's reliability impact rather than avoiding
   change [source: docs-google-sre-canarying-releases, Claim 4] [settled].
   `[editorial + sourced]`

## SRE is engineering, not ops

SRE is not an operational function at its core — it is about what engineering
you bring to your products and what you do for your users
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 10] [settled].

The operational work exists, but the value is the engineering: automation,
resilience patterns, risk reduction, and shared reliability tooling. AI
agents in SRE are engineering artifacts whose job is to raise the engineering
content of the role, not to absorb toil silently.

**Rule**: When evaluating an AI-agent deployment for SRE, ask: does this
raise the engineering content of the team's work (better instrumentation,
deeper system knowledge, faster root-cause analysis), or does it just hide
toil behind a model call?

## Feasibility study before scale

Before building a big plan or pushing a new process to a large audience, run
a feasibility study: prototype the idea in a bounded context, map "what would
have to be true," and confirm teams are ready *before* scaling
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 3] [settled].

> How can we discover whether or not that's going to be feasible? And you
> can do a small prototype. How would this work in different contexts?
> Because you want to do that research before you get something really far
> along.

A feasibility study is distinct from an MVP — the MVP asks "can we do this
thing," while the feasibility study asks "can we do this thing at scale, can
we do it now, and are people and infrastructure ready?"
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 4] [settled].

**Rule**: Before deploying an AI agent broadly, pilot it end-to-end on one
service in one domain. Work out the tool failures, permission boundaries, and
eval gaps in that single context. Only generalize when the pilot proves the
agent delivers value and the team is ready to own it.

## Prove end-to-end in one domain before generalizing

Google SRE's convergence effort found that doing a full end-to-end
proof-of-concept in a single domain and then generalizing realizes the
vision much quicker — even though it feels counterintuitive to teams
pushing for broad adoption
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 6] [settled].

The counterexample: a tool pushed broadly right away "took a lot longer to
take hold across the fleet" than the one scoped and proven first.

**Rule**: Resist the pressure to generalize an AI tool before it works
end-to-end in one domain. A tool that works nowhere yet but is "available
everywhere" is less valuable than one that demonstrably works in one place.

## Not every solution should be generalized

Product areas have different pressures and outcomes. Scoping a solution to
the local domain is sometimes the correct answer. A leader's job includes
the judgment of timing: a good idea with wrong timing should be paused and
revisited, not fought for a year
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 7] [settled].

**Rule**: After proving an AI agent in one domain, evaluate whether
generalization is the right next step. If the target domain has materially
different failure modes, pressure profiles, or tool surfaces, scope locally
rather than forcing a fit.

## Break the dev/SRE wall early

Bring SRE into the design phase — own resilience and reliability targets
up front, not after the system is built. SREs "coming in late" historically
doesn't work
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 2] [settled].

> There was a wall between the teams. And I think the first thing I do when
> I engage with a new product is I find out how high that wall is and I just
> start knocking it down.

**Rule**: For AI systems, this means SRE/reliability engineers must be in
the room when the agent architecture is designed — not called in when it
breaks. The tool inventory, permission model, and rollback path are
reliability decisions that get frozen at design time.

## Publish decision criteria so teams can self-steer

Leaders should publish *how* they make decisions — strategy plus guardrail
ranges (e.g., "we're working between A and D") — so teams understand
unpopular decisions ahead of time and can operate within the band without
asking permission
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 8] [settled].

**Rule**: For AI-agent governance, publish the decision criteria for when an
agent acts autonomously vs. escalates. Responders should know the guardrail
range without asking. An agent that operates within a published band is
auditable; an agent that operates within an undocumented one is not.

## "What would have to be true for the system to self recover?"

The future of SRE is to question standing policies and ask what would have to
be true for systems to understand and circumvent their own failure modes —
rather than layering workarounds on top
[source: docs-google-sre-prodcast-02-07-sabrina-farmer, Claim 11] [emerging].

This is the pre-AI articulation of the self-healing goal that later AI-agent
work pursues as a mechanism. The goal (self-recovering systems) is
aspirational; AI agents are the tooling toward it, not the guarantee of it.

**Rule**: Frame AI agents as one mechanism toward self-healing operations,
not the arrival at it. An agent that recovers from a known failure class is
progress; an agent that claims to understand and circumvent novel failure
modes is overclaiming.

---
*Sources for this chapter: docs-google-sre-prodcast-02-07-sabrina-farmer,
docs-google-sre-prodcast-04-09-ai-agents, blog-promptfoo-ai-regulation-2025,
docs-google-sre-prodcast-03-04-observability-spectrum,
docs-google-sre-canarying-releases*
*Last updated: 2026-08-08*
