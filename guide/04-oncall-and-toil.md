# On-call and Toil

> Cutting repetitive on-call work with AI without inventing new pages or
> hiding risk.

## Auto-remediation candidates vs. always-manual work

The toil-vs-safety tradeoff is a ladder, not a binary. Google classifies
batch-job changes by how much data a single run modifies — four safety levels
where "the lower the safety level, the more manual verifications we ask a
team to perform for a change" [source:
docs-google-sre-reliable-data-processing-minimal-toil, Claim 7] [settled]:

```
Level 0   The entire dataset is affected in a single run.
Level 1   Changes are canaried (manual or automated).
Level 2   Changes are gradually rolled out, first to less risky populations,
          then globally.
Level 3   Level 1 and 2 criteria are met and no humans are involved in the
          phased rollout.
```

Level 3 is the canonical auto-remediation candidate — automation that removes
the manual verification, and the framework is designed to incentivize teams
to climb to it [source: docs-google-sre-reliable-data-processing-minimal-toil,
Claim 7] [settled].

The always-manual class is what automation leaves behind: investigating false
positives from automated validation, and troubleshooting cascading rollouts
[source: docs-google-sre-reliable-data-processing-minimal-toil, Claim 11,
Claim 14] [settled].

**Rule**: For each remediation you'd automate, ask which safety level it
unlocks and what residual manual work it leaves behind. Budget for that
residual — it is the toil automation does not remove [editorial].

## The toil/on-call boundary for data pipelines

Freshness SLOs — "time since the last successful completion of the job" — are
operationalized with on-call readiness: alert on schedule overrun and mitigate
before the freshness SLO is violated; the paper's motto is "Hope is not a
strategy" [source: docs-google-sre-reliable-data-processing-minimal-toil,
Claim 15] [settled].

**Rule**: A silently stale pipeline (eval data, embeddings, indexes) is a
toil generator precisely because nobody pages on it. Give every batch job a
freshness SLO and an on-call rotation that pages before the SLO is violated
[source: docs-google-sre-reliable-data-processing-minimal-toil, Claim 15]
[settled].

## Action items: the follow-through loop

Postmortem data is the prioritization input for reliability investment —
"Postmortem is our tool to learn from our failures" — and learnings become
fixes only through action items that are concrete, assigned, and ideally
ETA'd [source: docs-google-sre-prodcast-01-09-postmortems, Claim 2, Claim 7]
[settled]. Ownership is flexible: an assignee may triage (create the bug, set
the meeting) rather than resolve everything, and "we don't know the owner" is
a valid item that starts a cross-team discussion [source:
docs-google-sre-prodcast-01-09-postmortems, Claim 8] [settled].

**Rule**: Unresolved action items are repeated incidents. Follow through to a
closed bug or an explicit "we don't know the owner" discussion — not a
forgotten document [source: docs-google-sre-prodcast-01-09-postmortems,
Claim 2, Claim 7, Claim 8] [settled].

## Open topics

Still unsourced targets for this chapter:

- Ticket / alert summarization for handoffs
- Measuring toil reduction (and review-time debt)
- Handoff quality when AI drafts the narrative

---
*Sources for this chapter: docs-google-sre-reliable-data-processing-minimal-toil,
docs-google-sre-prodcast-01-09-postmortems*
*Last updated: 2026-08-06*
