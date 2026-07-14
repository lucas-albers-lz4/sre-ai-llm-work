# LLM Ops Reliability

> Running LLM-powered products and internal agents as production systems —
> SLOs, evals, cost, drift, fallbacks, and capacity.

## AI in Incident Response: Assisted, Not Autonomous

AI is a tool like any other — it excels at removing on-call toil through
capturing, summarizing, and categorizing incident data. Simple automatic
rollbacks are within reach. But AI is "not creative, at least not at the
moment," and you should not trust crown-jewel production systems to it without
human oversight
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 9]
[emerging].

> "AI is a tool like anything else, and it's a tool that's making radical and
> great progress. And I think it can help remove a bunch of the toil from
> being on call, capturing, summarizing, categorization. It's great at that.
> Can it also help with very simple automatic rollbacks? Sure. But it's not
> creative, at least not at the moment."

> "are you going to trust your company's crown jewels, the thing that makes
> all your money, to a system that could just make things far worse without
> human oversight?"

The toil tasks AI is ready for today — summarization, categorization, timeline
drafting — are low-risk and high-volume. The tasks it is not ready for —
autonomous decision-making during novel incidents — are high-risk and
(hopefully) low-volume. Deploy AI where the risk profile matches. [editorial]

**Rule**: Deploy AI for incident toil (summaries, categorization, timeline
drafting) today. Keep a human in the loop for any action that mutates
production state. Shadow → suggest → act, never the reverse.

### Example

```
Phase 1 — Shadow (week 1-2): Agent drafts incident timelines and status
summaries. Human reviewer reads every output before it reaches stakeholders.
Agent output is never customer-facing without review.

Phase 2 — Suggest (week 3-4): Agent proposes rollback commands, restart
candidates, or config reverts. Human approves or rejects each suggestion.
Agent never executes without explicit approval.

Phase 3 — Act (earned, not calendar-driven): After 20+ consecutive correct
suggestions with zero false positives, agent is granted auto-approval for
a narrow action class (e.g., restart a known-flaky service during a
documented incident pattern). Human can revoke at any time.
```

## Destructive Actions Need Destructive Defaults

> "Don't have a system whose default behavior when you pass it an empty list
> is to just go on the rampage through your infrastructure."

A decommissioning automation at Google had a one-line bug: given a list of
machines to clean up, it worked correctly. Given an empty list, it interpreted
"empty" as "everything" and purged a huge chunk of the fleet. The team had to
manually reinstall to recover. The automation caused far more trouble than it
had ever prevented. This is a published SRE Workbook case study
[source: docs-google-sre-prodcast-03-06-incident-response-tooling, Claim 16]
[settled].

```
A decommissioning automation had a tiny one-line bug:
  - given a list of machines to clean up  -> it cleans them
  - given an EMPTY list                   -> "An empty list you say?
                                            Well, that means I'll just
                                            destroy everything."
It purged a huge chunk of the fleet; the team had to manually reinstall
huge chunks of the fleet to recover.
Lesson: "Don't have a system whose default behavior when you pass it an
empty list is to just go on the rampage through your infrastructure."
```

The same failure mode applies to AI agents with tool access: an agent told to
"clean up stale resources" that receives an empty or malformed list from an
upstream query could interpret it as "delete everything." Every destructive
action an agent can take needs a guard that treats empty, null, or unexpected
input as a no-op — never as "all." [editorial]

**Rule**: Every destructive action needs a kill switch and a default-deny on
bad input. If an empty list means "everything," the automation is a landmine.

---
*Sources for this chapter: docs-google-sre-prodcast-03-06-incident-response-tooling*
*Last updated: 2026-07-14*
