# Incident Response

> Using AI/LLMs during pages and SEVs — what helps, what slows you down, how
> to keep the human accountable for blast radius, and how postmortems close
> the loop.

## The incident-response doctrine

Incident response splits into two activities — resolving the incident
(mitigating impact, restoring service) and managing it (coordinating
responders, ensuring communication flows)
[source: docs-google-sre-incident-response, Claim 1] [settled]. The basic
principles: maintain a clear line of command, designate clearly defined
roles, keep a working record as you go, and declare incidents early and
often [source: docs-google-sre-incident-response, Claim 2] [settled].

**Rule**: Split an AI incident responder the same way — one capability that
mitigates, one that coordinates. A responder that only "understands the
incident" and never drives communication is not an incident responder.

### Roles follow knowledge, not reporting chains

The IMAG role hierarchy is IC / CL / OL: the Incident Commander leads, and
the Communications Lead and Operations Lead report to the IC. "By default,
the IC assumes all roles that have not been delegated yet," and both CL and
OL may lead teams that "expand or contract as needed"; if the incident
becomes small enough, the CL role can be subsumed back into the IC
[source: docs-google-sre-incident-response, Claim 4] [settled]. Command is a
context-dependent role: the GKE CreateCluster case study shows the IC handing
command to a more experienced responder mid-incident, while the GCE
Persistent Disk case study shows the IC retaining it because their team had
the best visibility into customer impact [source:
docs-google-sre-incident-response, Claim 6] [settled].

**Rule**: An AI copilot should identify who is best positioned to lead and
support a role handoff, not assume the first responder stays IC.

### Declare early and often

Declaring an incident early makes it resolve faster: it prevents
miscommunication, speeds root-cause identification, and gets relevant teams
and external communications looped in earlier. The Google Home case study is
the counterfactual — the team never declared an incident, relied on repeated
quota increases and heroic weekend effort, and users "lost half of their
requests during the weekend of June 3, 2017" before resolution
[source: docs-google-sre-incident-response, Claim 5] [settled].

**Rule**: Default to declaring. The cost of an unnecessary declared incident
is small; the cost of a late-declared one is a prolonged heroic-effort
incident. An AI triage agent that declines to declare should justify that
decision explicitly.

### Mitigate first, understand later

First responders must prioritize mitigation above all else — "customers do
not care whether or not you fully understand what caused an outage. What
they want is to stop receiving errors." The active-incident sequence: assess
the impact, mitigate the impact, perform root-cause analysis, and after the
incident is over, fix what caused it and write a postmortem
[source: docs-google-sre-incident-response, Claim 8] [settled].

Generic mitigations — pre-prepared actions that stop user pain before the
root cause is understood — are crucial for fast recovery, and they must be
built before the incident, not during it. The GKE CreateCluster outage was
prolonged because the service had none: a generic mitigation after the
plausible cause was identified at 9:56 a.m. would have ended a 6h40m outage
by 10 a.m. [source: docs-google-sre-incident-response, Claim 7] [settled].

**Rule**: Give an AI responder a pre-built catalog of generic mitigations
(rollback, drain, scale-out) and order its behavior mitigate → diagnose →
root-cause. A responder that insists on understanding the root cause before
acting is a root-cause analyst, not a first responder.

### The three Cs

ICS-based incident response frameworks share the "three Cs" — Coordinate,
Communicate, and Control — and when incident response goes wrong, the culprit
is likely in one of these three areas [source: docs-google-sre-incident-response,
Claim 3] [settled].

**Rule**: Structure an AI incident assistant's outputs around the three Cs —
does it coordinate the response, keep communication flowing, and maintain
control?

### Prepare before the incident

Pre-incident preparation: pre-decide the communication channel ("no Incident
Commander wants to make this decision during an incident"), prepare a contact
list, establish incident criteria from past outages and known high-risk
areas, and keep ready-to-use communication templates [source:
docs-google-sre-incident-response, Claim 12] [settled].

Drills build response muscle memory and reveal gaps: DiRT company-wide
resilience testing, Wheel of Misfortune, inventing outages from postmortems,
and breaking the test environment to troubleshoot with real tools — "the most
valuable part of running a drill is examining their outcomes, which can
reveal a lot about any gaps in incident management" [source:
docs-google-sre-incident-response, Claim 13] [settled].

**Rule**: Pre-load the decision surface — channel, contact list, incident
criteria, comms templates — before the incident. For AI responders, reuse the
same drill catalog: postmortem-derived outages and a broken test environment
are the natural eval harnesses for an incident agent.

## Postmortems

### The mandatory contents

A postmortem is a written record of an incident that must include the actions
taken to mitigate impact, the separated stages, the impact itself, the root
causes (not just the symptoms), and the follow-up actions to prevent
recurrence [source: docs-google-sre-prodcast-01-09-postmortems, Claim 1]
[settled].

**Rule**: Treat "root causes, not just symptoms" as the core requirement — it
is the whole point of postmortem depth. This is the schema an AI postmortem
drafter should be prompted to fill [source:
docs-google-sre-prodcast-01-09-postmortems, Claim 1] [settled].

### When to write one

Beyond declared severe incidents, a postmortem is warranted for any of these
triggers [source: docs-google-sre-prodcast-01-09-postmortems, Claim 10,
Concrete Artifacts] [settled]:

```
- Incident with customer impact
- SLO breach
- Data loss with no direct customer impact yet
- On-caller intervention
- Release rolled back before customer impact
- Traffic routed / mitigated during the release window
- Lower-priority incident with resolution time above a threshold
- Monitor / tooling failure
```

Each team defines its own criteria — the list is a rubric, not a rule
[source: docs-google-sre-prodcast-01-09-postmortems, Concrete Artifacts]
[settled].

**Rule**: If an incident *could* have happened (near-miss, rollback, monitor
failure) or was worse than its label suggests (slow low-priority resolution),
write the record [source: docs-google-sre-prodcast-01-09-postmortems,
Claim 10] [settled].

### The three-section structure

Google postmortems analyze "what went well / what could be improved / where we
got lucky," and every "got lucky" item is converted into an action item — a
developer who happened to look at a dashboard because no alert existed becomes
"create an alert / create a page" [source:
docs-google-sre-prodcast-01-09-postmortems, Claim 9] [settled].

```
what went well
what could be improved
where we got lucky    ← each "got lucky" item becomes an action item
```

**Rule**: A near-miss that only luck prevented must produce a monitoring or
automation work item. An AI can flag the lucky item; the judgment that the
luck is not guaranteed is human [editorial].

### Blamelessness is the reporting precondition

Postmortems must be blameless because blame makes people hide information and
stop declaring incidents out of fear of punishment [source:
docs-google-sre-prodcast-01-09-postmortems, Claim 3] [settled]. Blamelessness
is "switching responsibility from people to systems and processes" [source:
docs-google-sre-prodcast-01-09-postmortems, Claim 4] [settled], and it is a
cultural transformation that is "more complicated than a checklist" — start
simple and iterate [source: docs-google-sre-prodcast-01-09-postmortems,
Claim 13] [settled].

**Rule**: The reporting half cannot be automated. An AI drafts a blameless
write-up; it cannot make people report incidents [editorial].

### The review gate and action-item follow-through

Every postmortem must be reviewed for both technical completeness and
blameless language, and one person owns it through write → review → approve →
publicize [source: docs-google-sre-prodcast-01-09-postmortems, Claim 6,
Claim 8] [settled]. Learnings become fixes only through action items that are
concrete, assigned, and ideally ETA'd — an assignee may triage (create the
bug, set the meeting) rather than resolve, and "we don't know the owner" is a
valid item that starts a cross-team discussion [source:
docs-google-sre-prodcast-01-09-postmortems, Claim 7, Claim 8] [settled].
Publicize as widely as possible — orgs write postmortems and then fail to
share them, and a shared postmortem is what lets one team prevent an incident
another already hit; redact customer data, but don't let redaction be a
blocker [source: docs-google-sre-prodcast-01-09-postmortems, Claim 12]
[settled].

**Rule**: The review gate — completeness AND blameless language — is the
natural human checkpoint for AI-drafted postmortems. Keep it mandatory
[editorial].

### Trend analysis: the point of the corpus

A standard postmortem template that consistently captures the incident's root
cause and trigger is what makes trend analysis possible, and the value of a
postmortem program is the consistent, machine-aggregatable schema, not the
individual documents [source: docs-google-sre-postmortem-analysis, Claim 1]
[settled]. Google uses the resulting trend analysis to target improvements at
systemic root-cause types, "such as faulty software interface design or
immature change deployment planning" [source:
docs-google-sre-postmortem-analysis, Claim 2] [settled]. The taxonomy it
aggregates into: software (41.35%), development process failure (20.23%),
complex system behaviors (16.90%), deployment planning (6.74%), and network
failure (2.75%) — software plus the software-development process account for
over 61% of root causes [source: docs-google-sre-postmortem-analysis,
Claim 5] [settled].

**Rule**: Prompt an AI postmortem drafter to fill root cause and trigger as
distinct structured fields, and classify incidents into the taxonomy above.
Consistent capture is the prerequisite for the meta-retrospective that
targets systemic fixes.

## Open topics

Still unsourced targets for this chapter:

- Triage assistants vs. autonomous remediation
- Prompting with timeline, symptoms, and recent deploys
- When *not* to paste secrets / PII into a model
- Pairing AI hypotheses with graph/trace checks

---
*Sources for this chapter: docs-google-sre-prodcast-01-09-postmortems,
docs-google-sre-incident-response, docs-google-sre-postmortem-analysis*
*Last updated: 2026-08-13*
