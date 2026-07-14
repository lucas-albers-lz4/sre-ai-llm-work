# On-call and Toil

> Cutting repetitive on-call work with AI without inventing new pages or
> hiding risk.

## No Single Point of Failure in On-Call

Staff a primary and a deputy for every rotation, and page both in parallel for
every incident. The tooling must support this: parallel paging and quick
overrides are table-stakes requirements, not nice-to-haves
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 2]
[settled].

> "not having a single point of failure in terms of just one person getting
> paged." — and — "we always have a primary and a deputy, and they're both
> getting paged for every incident that we're taking."

The rationale is straightforward: the primary may be asleep, in a dead zone, or
already overwhelmed. The deputy provides a hot backup without waiting for
escalation timeouts. Tooling that only pages one person and escalates after N
minutes bakes latency into the response before the incident is even acknowledged.

**Rule**: Configure your paging tool to alert primary and deputy simultaneously.
If your tooling doesn't support parallel paging, fix that before adding any
other automation.

### Example

```
Rotation: primary + deputy, both paged for every incident.

- Primary: Alice (on-call this week)
- Deputy: Bob (also paged in parallel)
- Escalation: Charlie (paged if neither acknowledges within 5 minutes)

When the page fires, both Alice and Bob receive it simultaneously. If Alice
acknowledges, Bob sees the incident is claimed and stays available as backup.
If Alice's phone is on DND or she's already engaged, Bob acknowledges and
begins mitigation immediately — no escalation timeout, no delay.
```

## Start With the Tools You Already Have

Teams without dedicated incident-management budgets already have tools — they
just aren't calling them tools. Google Docs, Sheets, and Slack workflows have
supported effective incident response at large companies
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 7]
[settled].

> "you have tools. You're just not calling them tools. I have been amazed at
> big companies with amazing incident response who have done it with Google
> Docs or with a Google Sheet or with a Slack workflow."

The process matters more than the tool. A well-run incident in a shared Google
Doc beats a chaotic incident in an enterprise incident-management platform.
This also means the bar for "can AI help?" is low: if you're tracking state in
a spreadsheet, an agent that populates rows from chat context is immediately
useful without a platform migration.

**Rule**: Don't block incident-response improvements on a tooling purchase.
Process and discipline with a spreadsheet beat a platform nobody knows how to
use.

### Example

**Before**: "We can't improve incident response until we get budget for a
dedicated platform approved."

**After**: Team runs incidents with a shared Google Sheet (timestamp, action,
owner columns), a Slack #incident-response channel for engineering
coordination, and a Slack #incident-status channel for stakeholder updates.
When budget is approved, they know exactly which manual steps are the
bottlenecks and buy the tool that automates those — not the one with the
longest feature list.

## Drive Tooling Roadmaps From Postmortems

Google's internal incident-response tooling roadmap is driven by aggregating
many postmortems to find the common pain points, then streamlining those. The
target is the 80% majority of on-callers, with the remaining 20% handled
through extensibility points the team runs itself
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 5]
[emerging].

```
1. Run postmortems / retrospectives per incident.
2. Run a META-retrospective: aggregate many postmortems, find the
   common factors, streamline those.
   -> "that's really how we do a bunch of our roadmap planning for
       our internal tooling."
3. Build the core product for the 80% majority of on-callers / reviewers /
   customer-care. Delegate the remaining 20% (legitimate-but-different
   needs) to extensibility / custom extensions the team runs itself.
```

This method is reproducible without Google-scale resources: if you have
postmortems, you have enough data to identify the tooling gaps that would
actually reduce toil. The 80/20 split prevents roadmap paralysis from
conflicting stakeholder requirements.

**Rule**: The next tooling investment priority is the most common friction
point across your last 10–20 postmortems, not the loudest feature request.

---
*Sources for this chapter: docs-google-sre-prodcast-03-06-incident-response-tooling*
*Last updated: 2026-07-14*
