# On-call and Toil

> Structuring on-call work to protect cognitive flow — the three categories of
> operational load, why round-robin tickets destroy productivity, polarized time
> as the structural remedy, and the interrupt reduction project role that
> eliminates ticket root causes rather than passively cycling through them.

## The three categories of operational load

Not all operational work is the same. Google SRE classifies it into three types,
each with a different urgency profile and management strategy
[source: docs-google-sre-dealing-with-interrupts, Claim 1] [settled]:

| Category | Urgency | SLO | Examples |
|----------|---------|-----|----------|
| Pages (production alerts) | Immediate | Minutes | Monitoring-triggered incidents, production emergencies |
| Tickets | Hours to weeks | Hours, days, weeks | Customer requests, config reviews, capacity consultations |
| Ongoing responsibilities | Unpredictable | None (ad hoc) | Code/flag rollouts, ad hoc customer questions |

This taxonomy matters for AI-augmentation decisions: agents are best suited for
tickets (structured, time-flexible) and ongoing responsibilities (procedural),
least suited for pages (fluid, high-stakes, requiring judgment).

**Rule**: Classify every piece of operational work into pages, tickets, or
ongoing responsibilities. Automate tickets first — they are the highest-volume,
lowest-judgment category.

## Protecting cognitive flow

### The cost of an interruption

> A 20-minute interruption while working on a project entails two context
> switches. If you factor in the time to get back up to speed after being
> interrupted, it's a loss of a couple hours of truly productive work.
> [source: docs-google-sre-dealing-with-interrupts, Claim 4] [settled]

The 20-minute → hours-lost quantification is the productivity argument for every
structural decision in this chapter. Interrupt-driven scheduling doesn't just
cost the interrupt time — it costs the full context-switch recovery cycle.

### Primary on-call = no project work

> A person should never be expected to be on-call and also make progress on
> projects (or anything else with a high context switching cost). When an
> engineer is on-call for a week, that week should be written off as far as
> project work is concerned. If a project is too important to slip by a week,
> that person shouldn't be on-call.
> [source: docs-google-sre-dealing-with-interrupts, Claim 2] [settled]

If the pager is quiet, the primary on-call can work on tickets or
quickly-abandonable interrupt work, but not on project work with high
context-switch cost.

**Rule**: The primary on-caller's week belongs to on-call. Don't schedule
project deliverables against it. If the on-caller codes during a quiet
period, that's a bonus — not the plan.

### Stop round-robin ticket assignment

> If tickets are randomly assigned to team members, stop. This is extremely
> disrespectful of your team's time, and is completely counter to the idea of
> not being interruptible.
> [source: docs-google-sre-dealing-with-interrupts, Claim 3] [settled]

Round-robin ticket distribution is the most common anti-pattern in small SRE
teams. It fragments every team member's attention across project work and ticket
work, preventing any individual from achieving cognitive flow in either mode.

**Rule**: Centralize ticket handling onto one dedicated person. The rest of the
team works on projects uninterrupted. Rotate the ticket handler role, don't
spread the tickets.

## Polarized time

> Polarizing time means that each day, a person knows they're doing just project
> work or just interrupts. They concentrate for longer periods, and don't get
> stressed out because they're being roped into tasks that drag them away from
> the work they're supposed to be doing.
> [source: docs-google-sre-dealing-with-interrupts, Claim 5] [settled]

The ideal polarization period is a week (on-call week vs. project week), but a
day or even half-day can be the practical minimum. The structural requirement is
that the boundary is known in advance — a person starts their day knowing which
mode they're in.

**Rule**: Structure your team's week around polarized time blocks. Every team
member should know at the start of each day whether they're in project mode
(no interrupts) or interrupt mode (no project expectations).

### Two kinds of flow

Interrupt work itself can produce a state of flow — what Google SRE calls
"Angry Birds flow": repetitive, know-how-to-do-it work that is nonetheless
satisfying. The chapter notes that "people are ultimately happier with a balance
between these two types of work"
[source: docs-google-sre-dealing-with-interrupts, Claim 11] [settled].

**Rule**: The goal is not to eliminate all interrupt work — it's to isolate it
so that both project work and interrupt work can be done in flow. The problem
is the context switch, not the interrupt.

## The toil budget

Google SRE caps toil at ≤50% of total engineering time, with 60–70% as the
target for project work
[source: docs-google-sre-dealing-with-interrupts, Claim 6] [settled].

Tickets and interrupts are classified as toil. This means the ticket load alone
can consume nearly half the team's capacity before any project work happens.
Reducing toil is not a nice-to-have — it is the gate on the team's ability to
do engineering work.

**Rule**: Track toil as a percentage of total engineering time. If tickets +
pages + ongoing responsibilities > 50%, the team is an ops team, not an SRE
team — and the next hire should be a toil-reduction engineer, not another
on-caller.

## The interrupt reduction project role

The most effective structural pattern from Google's Bigtable SRE team: create a
**dedicated interrupt reduction project role** separate from ticket handling
[source: docs-google-sre-dealing-with-interrupts, Claim 7] [settled]:

> We explicitly allocated this job, which we'll refer to as "interrupt reduction
> project on duty," as a separate role from ticket work. It hits the sweet spot
> of undertaking small to medium-sized projects to reduce operational load —
> projects that require more than 30 minutes of attention, but are too small to
> account for on a quarterly planning cycle.

The model: one person handles all tickets (centralized), another person works on
20–30 hour projects that eliminate the root causes of those tickets. The team
completes "approximately three of these small strategic interrupt reduction
projects every four weeks."

```
1. Centralize your ticket load — one dedicated ticket handler
2. Track ideas for small interrupt reduction projects that will reduce toil
3. Reserve time for small (20–30 hours) proactive projects
4. Treat tickets and small proactive interrupt reduction projects as separate
   rotations, distributed among team members and sites on a regular basis
```
*Four-component interrupt-handling strategy from [source: docs-google-sre-dealing-with-interrupts, Concrete Artifacts].*

**Rule**: Staff a dedicated interrupt reduction project rotation. Don't ask
on-callers to "fix the root cause when you have time." A 20–30 hour project
needs a protected block, not a quiet-pager gap.

### Where AI fits

The interrupt reduction project role is the natural home for AI assistance in
on-call work. An AI agent can analyze ticket metadata for common patterns
("which ticket categories consume the most engineering hours?"), suggest
documentation improvements, and generate initial automation for recurring ticket
types. The human owns the 20–30 hour project; the AI compresses the
investigation and drafting phases.

## The ticket funnel pattern

Bigtable SRE built a simple web decision tree that routed customers to
self-service automation or documentation before allowing them to file a ticket.
Result: ticket creation dropped from 30+ to 15+ per week — a ~50% reduction
from a two-week project
[source: docs-google-sre-dealing-with-interrupts, Claim 8] [settled].

> Building a simple ticket funnel system to guide customers to appropriate
> automation or documentation was a natural choice for our first interrupt
> reduction project.

The modern LLM equivalent: an AI-powered support chatbot that answers common
questions and performs guided troubleshooting before escalating to a ticket.
The key design principle from the Bigtable case study: the funnel must redirect
to self-service *before* the ticket is created, not after.

**Rule**: Build a ticket funnel that deflects common requests to self-service
before they become tickets. An LLM-powered chatbot is the modern implementation
of the Bigtable decision tree. Measure ticket creation rate before and after —
the Bigtable benchmark is 50% reduction from a two-week investment.

## Regular ticket scrubs

> Lots of teams conduct on-call handoffs and page reviews. Very few teams do the
> same for tickets.
> [source: docs-google-sre-dealing-with-interrupts, Claim 9] [settled]

The asymmetry is real: pages get immediate postmortem attention, tickets get
triaged and forgotten. The chapter recommends periodic ticket scrubs to identify
root causes and "silence the interrupts until the root cause is expected to be
fixed."

The companion paper's approach: add metadata (cause, impact, time to fix) to
tickets so recurring issues are visible in aggregate. Without metadata,
individual tickets feel unique and the pattern is invisible.

**Rule**: Run a monthly ticket scrub. Add cause/impact/time-to-fix metadata to
every ticket at resolution time. The metadata is what makes the aggregate
pattern visible — without it, you're optimizing one ticket at a time.

## Policy as a toil-reduction tool

> Policy can be as powerful a tool as code. Your team sets the level of service
> provided by your service. It's OK to push back some of the effort onto your
> customers.
> [source: docs-google-sre-dealing-with-interrupts, Claim 10] [settled]

Not every interrupt needs an engineering solution. A policy change — deprecating
an under-resourced component, requiring customers to execute preparatory steps
before filing a ticket, giving back the pager for a flaky dependency — can
eliminate more toil than any automation project.

**Rule**: Before automating a recurring interrupt, ask: could a policy change
eliminate it entirely? Automation that sustains a fundamentally broken workflow
is worse than a policy change that removes the workflow.

---
*Sources for this chapter: docs-google-sre-dealing-with-interrupts*
*Last updated: 2026-07-23*
