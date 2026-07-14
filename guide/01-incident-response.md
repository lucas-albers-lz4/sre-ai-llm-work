# Incident Response

> Using AI/LLMs during pages and SEVs — what helps, what slows you down, and
> how to keep the human accountable for blast radius.

## Process Before Tools

Tools assist a good process and remove manual work, but they cannot create a
working process where one doesn't exist. Obtuse tooling that only half the team
can use becomes a detriment — it adds friction during the moments that demand
the least friction
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 8]
[settled].

> "Tools can assist you in having a good process, and they can make it easier.
> They can remove a lot of the manual work, but tools can't give you a working
> process. You can have the best tooling in the world, if you're not using them
> properly, your incident response is not going to be good."

At Google, bolted-together Unix-style incident tooling "was taking months to
train people" — the complexity itself became the incident response bottleneck.
The same source notes that Google rebuilt toward tooling that is "powerful
enough to support your process but not so obtuse that only half your people can
actually use the thing properly"
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 8].

**Rule**: Designate and exercise the process first; select tools that remove
steps from that process, not tools that demand the process bend around them.

### Example

**Before (tool-first)**: Team purchases an enterprise incident-management
platform and spends two quarters configuring it. During the first SEV,
responders discover nobody knows how to declare an incident or hand off
command in the new tool. Mitigation stalls while they figure out the UI.

**After (process-first)**: Team runs tabletop exercises with a shared
Google Doc and a Slack channel. They identify the 3 manual steps that
cause the most friction during handoffs. Then they evaluate tools based
on which ones eliminate those specific steps without adding new ones.
The tool ships in one week because the process already works — the tool
just removes friction.

## Communication Topology: Separate Engineering from Stakeholders

Keep the voice bridge focused on engineering mitigation — that's where the
highest-bandwidth communication must happen during an incident. Run a separate
Slack channel (or equivalent) for customer-support and stakeholder updates, so
the bridge airtime stays clear for the people fixing the problem
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 4]
[settled].

```
Keep the voice bridge focused on engineering mitigation (highest-bandwidth
need at that time). Run a SEPARATE Slack channel (e.g., the CIC) to the
customer-support / customer-facing staff. Goal: "keeping ... the bridge
airtime clear for engineering and mitigation efforts."
```
*Communication-channel-separation pattern from Sarah Butt (Salesforce Centralized IR), SRE Prodcast S3E6.*

This topology also defines where AI assistance is safest to deploy first: the
stakeholder-facing channel, where summarization and status drafting reduce toil
without touching production. The engineering bridge needs higher trust before
automation intervenes. [editorial]

**Rule**: Run two parallel channels during incidents — one for engineers
mitigating, one for everyone else asking "is it fixed yet?"

## Severity Is a Lever, Not a Verdict

Severity labels are an organizational construct — a model. What matters is the
outcome each level unlocks: the ability to page additional teams, escalate to
legal, authorize spend, or bypass change freezes. Declare SEV1 if you need
SEV1's mechanisms, not because you're certain the impact warrants it
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 10]
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 11]
[settled].

> "severity is very much an organizational construct, and it's a model. All
> models are flawed, but some models are useful."

Don't burn mitigation time arguing the label. Severity serves the incident, not
the other way around. And as understanding improves, explicitly demote: "when
was the last time you demoted an incident? ... if it gets to SEV1, it's that
for life, which is a bummer because it can change"
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 11].

**Rule**: Pick the severity that unlocks the resources you need right now.
Reclassify as you learn more. Never let the label outlive its usefulness.

### Example

```
1. Alert fires — unknown scope. Declare SEV1 to unlock cross-team paging,
   legal escalation, and spend authorization.
2. Mitigation begins. Scope narrows: single-region impact, contained.
3. Demote to SEV2 at minute 45. Release SEV1-only mechanisms.
4. Postmortem confirms: declaring SEV1 at minute 0 was correct given the
   information available, and demoting at minute 45 was equally correct.
```

## Learn From Every Outage

> "an outage that you don't learn from is a failure."

The investment is already sunk — the incident already impacted customers and
burned responder hours. Postmortems and retrospectives are how you extract
return on that unplanned investment. The goal is to rebalance spending away
from slick mitigation and toward ensuring you never fall down the same hole
twice
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 14]
[settled].

> "we need to re-balance somewhat the investments in general in incident
> response into let's not have the same incident happen twice."

**Rule**: Treat every incident as an unplanned investment whose payoff is the
postmortem. If you didn't learn something that prevents recurrence, the outage
failed.

### Example

```
After every SEV:
1. Draft timeline within 24h — raw, from chat logs and alert timestamps.
2. Blameless review within 5 business days — what happened, not who.
3. Action items tracked to completion in the team's normal backlog.
4. Quarterly meta-retrospective: aggregate action items across incidents,
   find the recurring patterns, fund the top prevention investments.
```

---
*Sources for this chapter: docs-google-sre-prodcast-03-06-incident-response-tooling*
*Last updated: 2026-07-14*
