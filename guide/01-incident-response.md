# Incident Response

> Using AI/LLMs during pages and SEVs — what helps, what slows you down, and
> how to keep the human accountable for blast radius.

## Process Before Tools

Tools assist a good process and remove manual work, but they cannot create a
working process where one doesn't exist. Obtuse tooling that only half the team
can use becomes a detriment — it adds friction during the moments that demand
the least friction
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 8]
[anecdotal].

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

## Communication Topology: Separate Engineering from Stakeholders

Keep the voice bridge focused on engineering mitigation — that's where the
highest-bandwidth communication must happen during an incident. Run a separate
Slack channel (or equivalent) for customer-support and stakeholder updates, so
the bridge airtime stays clear for the people fixing the problem
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 4]
[anecdotal].

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
automation intervenes.

**Rule**: Run two parallel channels during incidents — one for engineers
mitigating, one for everyone else asking "is it fixed yet?"

## Severity Is a Lever, Not a Verdict

Severity labels are an organizational construct — a model. What matters is the
outcome each level unlocks: the ability to page additional teams, escalate to
legal, authorize spend, or bypass change freezes. Declare SEV1 if you need
SEV1's mechanisms, not because you're certain the impact warrants it
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 10]
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 11]
[anecdotal].

> "severity is very much an organizational construct, and it's a model. All
> models are flawed, but some models are useful."

Don't burn mitigation time arguing the label. Severity serves the incident, not
the other way around. And as understanding improves, explicitly demote: "when
was the last time you demoted an incident? ... if it gets to SEV1, it's that
for life, which is a bummer because it can change"
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 11].

**Rule**: Pick the severity that unlocks the resources you need right now.
Reclassify as you learn more. Never let the label outlive its usefulness.

## Learn From Every Outage

> "an outage that you don't learn from is a failure."

The investment is already sunk — the incident already impacted customers and
burned responder hours. Postmortems and retrospectives are how you extract
return on that unplanned investment. The goal is to rebalance spending away
from slick mitigation and toward ensuring you never fall down the same hole
twice
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 14]
[anecdotal].

> "we need to re-balance somewhat the investments in general in incident
> response into let's not have the same incident happen twice."

**Rule**: Treat every incident as an unplanned investment whose payoff is the
postmortem. If you didn't learn something that prevents recurrence, the outage
failed.

---
*Sources for this chapter: docs-google-sre-prodcast-03-06-incident-response-tooling*
*Last updated: 2026-07-14*
