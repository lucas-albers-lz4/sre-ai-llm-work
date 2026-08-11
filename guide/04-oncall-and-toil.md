# On-call and Toil

> Cutting repetitive on-call work with AI without inventing new pages or
> hiding risk. Google's toil playbook supplies the taxonomy, the objective
> measurement methodology, and the strategy set that agent-driven toil
> reduction must operate under.

## What counts as toil

Toil is "the repetitive, predictable, constant stream of tasks related to
maintaining a service," falling on a spectrum of six characteristics — Manual,
Repetitive, Automatable, Nontactical/reactive, Lacks enduring value, and Grows
at least as fast as its source — each demonstrated with a concrete operational
example [source: docs-google-sre-eliminating-toil, Claim 1] [settled].

The sixth characteristic is the one that defeats backlog-clearing plans:
many classes of operational work grow as fast as (or faster than) the size of
the underlying infrastructure, so infra-linked toil will not shrink on its
own.

**Rule**: Classify candidate work against the six characteristics before
calling it toil. Automatable, infra-linked work is the highest-leverage
reduction target.

## Measuring toil reduction

Toil identification should be data-driven, not experiential: choose an
objective unit of human effort — minutes/hours, an applied patch, a completed
ticket, a manual production change, a hardware operation — track it
continuously before, during, and after the reduction effort, and automate the
measurement so collecting it doesn't itself become toil
[source: docs-google-sre-eliminating-toil, Claim 4] [settled].

The countable units are exactly what an agent layer can tally: tickets, manual
production changes, and patches can be counted with no new instrumentation,
only a ledger.

**Rule**: Pick an objective unit of human effort per toil class and track it
continuously. If collecting the measurement is itself manual work, automate
it or you have swapped toil for meta-toil.

Google caps SRE teams' operational work (toil and non-toil alike) at 50% of
time; the exact target may not suit other orgs, but placing an upper bound on
toil matters because identifying and quantifying it is the first step toward
optimization [source: docs-google-sre-eliminating-toil, Claim 3] [settled].

**Rule**: Set an explicit toil ceiling for the team. Any plan that grows the
toil share of on-call time is a regression even if total work falls.

## Agent-appropriate vs always-manual work

Toil falls into six common categories — Business Processes (ticket-driven),
Production Interrupts, Release Shepherding, Migrations, Cost Engineering /
Capacity Planning, and Troubleshooting for Opaque Architectures — a spectrum,
not a binary classification [source: docs-google-sre-eliminating-toil,
Claim 5] [settled].

Ticket-driven business processes are insidious: they usually accomplish their
goal, and because the toil is dispersed evenly across the team it "doesn't
loudly and obviously call for remediation"
[source: docs-google-sre-eliminating-toil, Claim 6] [settled].

**Rule**: Map your toil classes onto the six categories before assigning
agents. Release Shepherding, Migrations, and ticket-driven Business Processes
are the high-leverage agent classes; the taxonomy itself warns against
spending effort on recurring (automatable) failures instead of novel ones, so
novel-failure troubleshooting stays a human class
[source: docs-google-sre-eliminating-toil, Claim 5] [settled].

## The toil-management playbook

### Reject the toil first

Analyzing the cost of responding versus not responding should be the first
option you consider — working with toil in larger aggregates reduces interrupts
and reveals patterns to target for elimination
[source: docs-google-sre-eliminating-toil, Claim 7] [settled].

**Rule**: Before automating a task, ask whether it should be done at all.
Batching non-urgent toil into scheduled aggregates is cheaper than automation
and exposes the pattern to eliminate.

### Human-backed interfaces are the agent on-ramp

For complex problems with many edge cases, use human-backed interfaces — a
partially automated approach where the service receives structured data via a
defined API but engineers still handle some operations — as an interim step
toward full automation [source: docs-google-sre-eliminating-toil, Claim 9]
[settled].

**Rule**: Stand up the typed interface with a human fallback before full
automation. This is the predecessor of the human-in-the-loop agent pattern:
the engineer stays behind the curtain until the domain is mapped.

### Self-service that degrades to a ticket

After a typed interface exists, provide self-service methods (web form,
script, API) that degrade gracefully to a ticket on failure — moving 80–90% of
requests to self-service is still a huge workload reduction
[source: docs-google-sre-eliminating-toil, Claim 10] [settled].

**Rule**: Agent ticket deflection needs the same graceful-degradation design:
when the automation cannot handle a request, fail forward into the human queue
rather than erroring.

### Start small and improve

Don't design the perfect toil-free system — automate a few high-priority items
first, then improve using the time you gained, with clear metrics
[source: docs-google-sre-eliminating-toil, Claim 15] [settled].

**Rule**: Scope the first toil-reduction pass to a few high-priority classes
with a defined metric. Both of Google's toil case studies followed phased,
incremental paths rather than big-bang redesigns.

---
*Sources for this chapter: docs-google-sre-eliminating-toil*
*Last updated: 2026-08-08*
