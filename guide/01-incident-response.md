# Incident Response

> Using AI/LLMs during pages and SEVs — what helps, what slows you down, how
> to keep the human accountable for blast radius, and how postmortems close
> the loop.

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

## Open topics

Still unsourced targets for this chapter:

- Triage assistants vs. autonomous remediation
- Prompting with timeline, symptoms, and recent deploys
- When *not* to paste secrets / PII into a model
- Pairing AI hypotheses with graph/trace checks

---
*Sources for this chapter: docs-google-sre-prodcast-01-09-postmortems*
*Last updated: 2026-08-06*
