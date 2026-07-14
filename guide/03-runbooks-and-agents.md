# Runbooks and Agents

> Encoding operational knowledge so agents can act safely — runbook structure,
> tool permissions, human approval gates, and harness patterns for ops.

## Avoid Clumsy Automation

"Clumsy automation" is automation that increases workload at high-cognitive-load
moments and reduces it at low-load moments. The aviation analogy: if you had to
do a bunch of extra work during takeoff and landing just to make cruising
easier, the automation is a net negative — because takeoff and landing are
exactly when cognitive load is highest
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 12]
[anecdotal].

```
clumsy automation = automation that increases workloads at a high workload
moment for the responder and decreases it at a low workload time.

Aviation analogy: if you had to do a bunch of stuff during takeoff and
landing that made cruising easier, it actually wasn't useful automation,
because takeoff and landing are these high cognitive workload times.
```
*Attributed to John Alspaugh & Richard Cook, "future of above the line tooling," relayed by Sarah Butt.*

For incident-response agents and runbooks, the acute phase of an incident is
the equivalent of takeoff/landing. Automation that demands responders fill in
fields, confirm dialogs, or triage agent output during the first 15 minutes of
a SEV is clumsy. Automation that silently drafts a timeline from chat logs
without asking for input is not.

**Rule**: Measure automation value by cognitive load at the moment it
intervenes, not by total steps removed. An automation that removes 10 steps
during routine work but demands 2 decisions during a SEV is a net loss.

## Build on a Foundation, Extend via APIs

Build-vs-buy for incident tooling is rarely binary. Buy a foundation that
provides good APIs, then build your organization's specific needs on top:

> "all I care about is giving me the best APIs possible. If you will give me
> an API, I will have my engineers build the other piece of it."

The same source describes the strategy as "buy a foundation and build our needs
on top of that versus just assuming it's going to come for us perfectly out of
the box"
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 6]
[anecdotal].

This applies directly to agent-harness tooling: prefer platforms that expose
APIs for creating incidents, attaching evidence, and updating status, so your
agents can integrate into existing workflows rather than replacing them.

**Rule**: When evaluating incident tooling, prioritize API surface area over
feature checklist. You will need to extend whatever you buy.

---
*Sources for this chapter: docs-google-sre-prodcast-03-06-incident-response-tooling*
*Last updated: 2026-07-14*
