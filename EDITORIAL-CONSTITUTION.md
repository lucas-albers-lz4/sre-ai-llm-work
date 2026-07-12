# Editorial Constitution

This document defines the editorial standards for the SRE AI LLM Work guide.
Every agent in the pipeline — discovery, extraction, review, synthesis — is
bound by these rules.

## Mission

Produce the fastest path from "I want AI/LLMs to help with SRE work" to
"I am using them effectively on-call, in incidents, and in production ops"
for working SREs and platform engineers.

Not a survey. Not a taxonomy. Not an overview. A field guide that tells you
what to do, what not to do, and shows you exactly what it looks like.

Scope includes:

- Using AI/LLMs *as an SRE* (incidents, on-call, runbooks, observability, toil)
- Running LLM-powered systems *reliably* (SLOs, failure modes, evals, cost, safety)
- Practitioner configs, postmortems, failure reports, and ops agent harnesses

Out of scope unless it directly serves those goals: AI coding-agent product
reviews, CLAUDE.md-as-lifestyle content, and vendor marketing.

## Editorial Tenets

### 1. Concrete beats abstract
Every recommendation must be actionable in a real ops context — an incident,
an on-call shift, a runbook change, or a production LLM service. Show the
example. Always.

### 2. Cite everything
No unsourced claims. Every recommendation links to its source note.
Every source note links to the original material. The reader can always
trace a claim back to its origin and judge for themselves.

### 3. Evidence grades are mandatory
Every claim carries a confidence tag: `[settled]`, `[emerging]`, `[anecdotal]`,
`[editorial]`, or `[stale]`. The reader deserves to know how much weight
to put on a recommendation.

### 4. Show the counter-evidence
If sources disagree, say so. Suppressing contradictions is editorial malpractice.

### 5. Prescriptive over descriptive
Don't say "there are several approaches." Say "do X. Here's why. If your
situation is Y, do Z instead."

### 6. Point-in-time honesty
Tools and models change monthly. Date your claims. Flag staleness.

### 7. Failure reports are first-class sources
"I tried X on-call and it made the incident worse" is as valuable as a success
story — often more.

### 8. Practitioner ops over vendor decks
A real runbook, pager playbook, or postmortem beats ten pages of product
marketing. Vendor docs say what's possible. Practitioner artifacts show what
survived production.

### 9. Small teams count
A two-person platform team's AI on-call notes are as valid as a Fortune 500's.
Filter by: did they use this under real load or real pages?

### 10. Deterministic tools for deterministic work
If a monitor, alert, CI check, or policy engine can enforce a rule, it should
not be "AI advice." LLMs are for judgment under uncertainty, not replacing
SLOs or paging policies.

## Anti-Patterns (in our own writing)

### Survey-itis
"There are several popular AI ops tools including..." — NO. Name the tool when
relevant. Skip the panorama.

### Prompt cargo cults
"Always include 'think step by step' in your incident prompt" — NO. Cite
evidence or don't include it.

### Terminal fanfiction
Invented incident transcripts that never happened. If you're showing an
interaction, link to the source or mark it as a constructed example.

### Grandiose framing
"AI is transforming the very fabric of reliability engineering" — NO.
Practical guide, not a keynote.

### Stale confidence
Presenting 6-month-old claims as current truth without a `[stale]` flag.

### Unsourced prescriptions
Every "should" needs a citation or an explicit `[editorial]` tag.

### AI tells (LLM-isms)
Same rules as the upstream hitchhiker constitution: cut filler, metaphor spam,
contrast clichés, and em-dash pile-ups. Read it aloud; if it sounds like a
press release, rewrite it plainer.

## Inclusion Bar

A source or claim earns inclusion if it meets ANY of:
- Concrete, reproducible ops/LLM pattern with evidence (config, metrics, postmortem)
- Credible failure report with enough detail to learn from
- Contradiction of an existing guide recommendation
- Novel pattern not covered by existing source notes

## Exclusion Bar

Reject if ANY of:
- Pure opinion with no supporting evidence or experience report
- Vendor marketing disguised as guidance
- Duplicate of an existing source note
- Theoretical/speculative — "this should work" with no evidence anyone tried it
- Older than 2025-12-01 (pre-agentic-era landscape was too different)
- Pure AI *coding-agent* content with no SRE/ops/reliability angle

## Report Shape

The guide is organized by **practitioner need**, not by tool or vendor:

1. How should I think about AI in SRE? (principles)
2. How do I use AI in incidents? (incident response)
3. How do I use AI with observability data? (observability)
4. How do I encode ops knowledge for agents? (runbooks and agents)
5. How do I cut on-call toil without creating new risk? (on-call and toil)
6. How do I run LLM systems reliably? (LLM ops reliability)
7. What can go wrong, and how do I trust the system? (security and trust)

Each chapter follows the pattern:
- Lead with the recommendation
- Show a concrete example (config, runbook, workflow, or metric)
- Cite the source(s)
- Note the confidence level
- Acknowledge counter-evidence if it exists
