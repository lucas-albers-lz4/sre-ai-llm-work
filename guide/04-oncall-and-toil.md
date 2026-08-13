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

## Running the on-call rotation

### The pager budget

Google SRE targets a maximum of two incidents per 12-hour on-call shift, to
ensure adequate follow-up time, and at least 50% of SRE time on project work,
so reliability is never bought at the cost of an on-call engineer's health
[source: docs-google-sre-on-call, Claim 1] [settled]. If introducing a new
paging alert would exceed the paging budget, "the stability of the system
needs additional attention" [source: docs-google-sre-on-call, Claim 5]
[settled].

**Rule**: Treat pager load as a budget with a hard number. An AI first
responder that pages must consume the same budget — agent-triggered pages are
not free.

### Pager-load anatomy and response tiers

Pager load has three main inputs: bugs in production, alerting, and human
processes [source: docs-google-sre-on-call, Claim 2] [settled]. The alerting
inputs (thresholds, new paging alerts, SLO alignment) are the fastest lever;
the human-process inputs (rigor of fixes, data quality, human changes to
production) are the slowest and most cultural. When load is high, diagnose
which input drives it — "relaxing alert thresholds is rarely an appropriate
response to being paged" [source: docs-google-sre-on-call, Claim 4]
[settled].

Not every page needs an immediate response: a revenue-impacting network
outage warrants 5 minutes, a stuck customer-order batch process 30 minutes,
and failing backups of a pre-launch service a ticket. "Engineers shouldn't
have to be at a computer and working on a problem within minutes of receiving
a page unless there is a very good reason to do so" [source:
docs-google-sre-on-call, Claim 3] [settled].

**Rule**: Classify every alert into a response tier (page-today, page-soon,
ticket) — the tier is also the automation surface, since "it's generally
better for a computer to fix a problem than requiring a human to fix it"
[source: docs-google-sre-on-call, Claim 3] [settled].

### Gated alert introduction

New paging alerts go through a gated process: whole-team review, a test
window of roughly a week in production in author-email mode to vet false
positives, with the test-period trigger rate used to predict pager-budget
consumption and an explicit team approve/disallow decision [source:
docs-google-sre-on-call, Claim 5] [settled].

**Rule**: No agent may add itself to the pager without the same
test-then-approve cycle.

### Follow-up rigor and data quality

Aim to identify the root cause of every page — "you should rarely conclude
that a page is triggered by 'cause unknown.'" Fixes sort into a ladder: point
fix vs. systemic fix vs. monitoring fix (the monitoring fix being a ticket
alert, not a page), and Google on-callers work on production bugs during
their shift rather than projects [source: docs-google-sre-on-call, Claim 7]
[settled]. The prioritization economics are citable: if a fix takes 3 working
weeks (120 hours) and a page costs 4 working hours to handle properly,
"there's a clear break-even point after 30 pages" [source:
docs-google-sre-on-call, Claim 8] [settled].

Pager-load management needs structured bug tracking: file a placeholder bug
per paging alert, link each alert to its root-cause bug, and monitor load
with a 21-day trailing average plus warning-level ticket alerts
[source: docs-google-sre-on-call, Claim 9] [settled].

**Rule**: Every page an agent triggers must trace to a bug link, or the agent
is generating unclassified noise. Justify each recurring page class with page
count × page cost.

### Staffing, shifts, and scheduling

Minimum staffing to sustain 24/7 on-call: five people per site in a multisite
configuration, eight in a single-site configuration, plus one buffer each —
six or nine per site. Practitioner recollections of Google's multisite
minimum run slightly higher (6–7 per site); treat 5–7 per site as the
defensible multisite range [source: docs-google-sre-on-call, Claim 11]
[settled]. Shift lengths should be capped at 12 hours — "24 hours of on-call
duty without reprieve isn't a sustainable setup" — with "3 days on, 4 days
off" as a shorter-shift alternative and out-of-hours work compensated
[source: docs-google-sre-on-call, Claim 12] [settled].

Scheduling should be automated with a tool that rearranges and rebalances
load, but "it must never change an already generated schedule" so engineers
can plan around their shifts; short-term swaps need a documented policy with
peer review [source: docs-google-sre-on-call, Claim 13] [settled]. During
long incidents, PagerDuty rotates on-call engineers and the Incident
Commander every four hours, to encourage rest and bring fresh ideas
[source: docs-google-sre-incident-response, Claim 9] [settled].

**Rule**: Set the staffing floor before adding agent help — an agent absorbs
pages, but the human rotation still needs minimum headcount for
sustainability. An automated scheduler that publishes and never mutates a
generated schedule is a good first agent for on-call ops.

### Bootstrapping a rotation

A new SRE team can reach on-call readiness in three months (vs. the normal
3–9 months for new hires) using a training checklist, lab drills, deep dives,
Wheel of Misfortune, and shadowing the outgoing team before becoming primary
with them as backup [source: docs-google-sre-on-call, Claim 16] [settled].

**Rule**: Use the same staged ramp for AI first responders — observe, then
act with human backup, then autonomous with escalation.

## Which services get on-call — and when

SRE capacity is scarce, so engagement is selective: "an SRE team must decide
where to focus their attention to achieve the best results"
[source: docs-google-sre-engagement-model, Claim 1] [settled]. The service
lifecycle governs when on-call investment happens — during Limited
Availability, operational and incident work should be shared between the
developer and SRE teams so the developer gains operational experience before
GA; at GA, the developer team "should continue to field a small part of all
operational and incident response work" and "might permanently include one
developer in the on-call rotation" [source: docs-google-sre-engagement-model,
Claim 6, Claim 7] [settled].

Customer break/fix work is the demand side of the toil budget: "whatever
energy you put into helping users past their difficult moments is energy you
can't invest in advancing your system" — and this "doubly applies" to
internal platform teams [source: docs-google-sre-reaching-beyond-walls,
Claim 5] [settled]. For a platform, only systems that meet "minimum viable
reliability requirements" should reach the pager-handoff point at all
[source: docs-google-sre-reaching-beyond-walls, Claim 6] [settled].

An engagement needn't be indefinite: consider handing a service back when it
has been optimized to no longer need ongoing SRE engagement, when its
importance has diminished, or when it is reaching end of life
[source: docs-google-sre-engagement-model, Claim 17] [settled].

**Rule**: Decide which services get on-call by lifecycle phase, keep
developers in a small permanent share of on-call work, and define the
hand-back conditions up front. An AI reliability team should apply the same
selection discipline to agentic services rather than attempting uniform
coverage.

---
*Sources for this chapter: docs-google-sre-eliminating-toil,
docs-google-sre-on-call, docs-google-sre-incident-response,
docs-google-sre-engagement-model, docs-google-sre-reaching-beyond-walls*
*Last updated: 2026-08-13*
