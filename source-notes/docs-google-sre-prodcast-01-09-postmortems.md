---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-01-09/
source_type: discussion
title: "Postmortems with Ayelet Sachto (SRE Prodcast S1E09)"
author: Ayelet Sachto (Google SRE, GKE SRE team London, formerly PSO SRE lead EMEA); hosts Viv & MP
date_published: 2022 (estimated; SRE Prodcast Season 1, Episode 9 — page has no structured publish date)
date_extracted: 2026-08-04
last_checked: 2026-08-04
status: current
confidence_overall: settled
issue: "#756"
---

# Postmortems with Ayelet Sachto (SRE Prodcast S1E09)

> The final S1E09 installment of Season 1 of Google's SRE Prodcast: Ayelet
> Sachto (GKE SRE, co-author of *Anatomy of an Incident*) defines the postmortem
> and its goal, the blamelessness = responsibility-shifting doctrine with the
> Treynor "cost of the mistake" framing, the psychological-safety mechanism that
> prevents incident-hiding, the mandatory-contents checklist, the
> action-item hygiene requirements, the "where we got lucky → build the alert"
> pattern, the when-to-write-postmortem criteria, and the share-widely argument.
> This is the primary-source human baseline for the guide's postmortem section
> and for AI-assisted postmortem-drafting claims (incident.io, Zelesko, S4E9).

## Source Context

- **Type**: discussion (podcast transcript) — SRE Prodcast Season 1, Episode 9, hosted by Viv and MP, guest Ayelet Sachto. Filed from the official sre.google PDF (`https://sre.google/static/pdf/sre-prodcast-01-09.pdf`); the Prospector verified the PDF and the HTML transcript at the source URL are the same episode transcript. The HTML transcript was read for this extraction.
- **Author credibility**: Ayelet Sachto is a site reliability engineer on the GKE (Google Kubernetes Engine) SRE team in London, formerly a strategic cloud engineer leading PSO (Professional Services Organization) SRE efforts in EMEA, with "almost two decades" in production on-call. She is also co-author of the O'Reilly *Anatomy of an Incident* (2022, with Adrienne Walcer) — already extracted as `docs-google-sre-anatomy-of-an-incident.md`. This is a primary-source account from a named Google SRE on the official sre.google domain.
- **Scope**: Postmortem practice end-to-end: definition and goal, mandatory contents, blamelessness and its definition, psychological safety, process/standards/tooling, review requirement, action-item hygiene and ownership, the "what went well / what could be improved / where we got lucky" structure, when-to-write criteria, cross-team learning via sharing. Does **not** contain AI/LLM content, code, configs, or metrics — every AI-relevance connection in this note is the Miner's synthesis, clearly marked. Does not cover the incident-response phase itself (that is S1E08).

## Extracted Claims

### Claim 1: A postmortem is a written record of an incident whose mandatory contents are mitigation actions, stages, impact, root causes (not just symptoms), and follow-up actions — with the goal of preventing recurrence and reducing impact of future outages
- **Evidence**: Sachto's definitional answer; she explicitly contrasts root cause(s) with symptoms and lists the follow-up actions.
- **Confidence**: settled
- **Quote**: "Postmortems are a written record of an incident. They should include the actions taken to mitigate customer impact and resolve the incident, the stages that more often than not will be separated, the impact itself, the root causes, and—important to emphasize root cause or root causes and not just the symptoms—the follow-up actions to prevent it from reoccurring."
- **Our assessment**: Settled, primary-source Google SRE doctrine. This is the canonical "what goes in a postmortem" checklist — the schema an AI postmortem-drafting agent is expected to fill (see Cross-References → Extends re: incident.io Claim 8). The "root causes and not just the symptoms" requirement is the load-bearing part: it is the whole point of postmortem depth and matches the Anatomy of an Incident Venn-diagram analysis model.

### Claim 2: Postmortem data is the prioritization input for reliability investment — "postmortem is our tool to learn from our failures" — and without formalized learning processes, incidents will recur
- **Evidence**: Sachto's statement of the goal and its role in prioritizing reliability work.
- **Confidence**: settled
- **Quote**: "But the data that are coming from postmortems is crucial in order to understand what we can prioritize and what we should prioritize. Postmortem is our tool to learn from our failures. And unless we have some formalized processes of learning from these incidents in place, they will reoccur."
- **Our assessment**: This is the strategic value argument for postmortems: they are not ritual documentation but the data source for deciding what to fix. Directly corroborates the IMAG Guide's Claim 14 (aggregating postmortems to identify trends/investment areas) and the meta-retrospective method in S3E06 Claim 5. The "they will reoccur" consequence is the same thesis as S3E06 Claim 14 ("an outage that you don't learn from is a failure").

### Claim 3: Postmortems must be blameless because blame causes people to hide information and not declare incidents out of fear of punishment
- **Evidence**: Sachto's causal argument: blamelessness prevents side conversations about who's at fault, and fear of punishment suppresses both reporting and incident declaration.
- **Confidence**: settled
- **Quote**: "But to be able to learn from them, they need to be blameless because that will prevent side conversations about who did what and might be at fault, maybe. We don't want people to hide information or not to declare incidents because they are afraid of punishment."
- **Our assessment**: The causal chain (blame → incident-hiding → no learning) is the foundation of blameless culture and is the human-side precondition that AI postmortem tooling cannot manufacture: an AI can draft a blameless write-up, but it cannot make people *report* incidents. That boundary is developed in Cross-References (Novel). Corroborates the IMAG Guide Claim 12 ("Blaming individuals... does not aid the learning process") and Anatomy of an Incident Ch5.

### Claim 4: Blamelessness is defined as "switching responsibility from people to systems and processes" — the mechanism that enables risk-taking and innovation, with Ben Treynor's framing that an unlearned mistake costs "the cost of the mistake, but without the benefit of learning from it"
- **Evidence**: Sachto gives the definitional statement, the "who did it?" manager anecdote, and quotes Ben Treynor's email directly.
- **Confidence**: settled
- **Quote**: "blamelessness is the notion of switching responsibility from people to systems and processes." — and — "if we are missing that opportunity, if we are not learning from our mistakes, we are taking the cost of the mistake, but without the benefit of learning from it." — and — "employees might feel like they are fearing for their job, they are avoiding taking any risks or changes, and we want to make those changes because we cannot improve without making changes, without taking risks."
- **Our assessment**: The single most citable definition of blamelessness in the corpus — more precise than the IMAG Guide's "everyone involved had good intentions" framing (they are complementary: good intentions is the premise, responsibility-shifting is the mechanism). The Treynor line, attributed here via his email, operationalizes the "only wants new incidents" principle from S1E08 Claim 11: a repeated mistake with no learning is pure loss.

### Claim 5: Psychological safety — the belief that one will not be punished or humiliated for speaking up with ideas, questions, concerns, or mistakes — is what prevents incident-hiding and unlocks the root-cause questions
- **Evidence**: Sachto's formal definition and her explanation of why it matters for SRE specifically (asking the questions that lead to root cause).
- **Confidence**: settled
- **Quote**: "psychological safety is a belief that while one will not be punished or humiliated for speaking up with ideas, questions, concerns, or mistakes, a culture of psychological safety makes it understood that things will break, failures will happen, and those breakage should be widely communicated."
- **Our assessment**: A formal, quotable definition that the corpus previously only gestured at (S3E11 discusses psychological safety in on-call; the IMAG Guide mentions the term only in passing). Note the source's own phrasing "those breakage" — quoted verbatim. This is the human precondition: you cannot detect incidents you are never told about, so psychological safety is upstream of all postmortem data.

### Claim 6: Good postmortems require strong process, standards, systems and tools; the timeline and stages are the most-missed mandatory element; and every postmortem must be reviewed for both technical completeness and blameless language
- **Evidence**: Sachto's answer to "how do we write good postmortems" — the checklist of covered items, the timeline emphasis, and the explicit review requirement.
- **Confidence**: settled
- **Quote**: "we need strong processes for that. And we need our systems and tools to be in place in order to make it easier for people." — and — "the timeline is very, very important; sometimes people are missing that. So they are writing when an incident started and when the impact may be mitigated, but they're not capturing all the stages." — and — "it's important that whoever reviews— and yes, postmortems need to be reviewed— needs to make sure that we have the technical information, we have all the details, but we also have a language that is not pointing fingers, that is blameless, and encourages us to take those risks."
- **Our assessment**: Two extractable mechanisms: (a) full stage-by-stage timeline is the most-neglected content, and it is what reveals detection-vs-mitigation time gaps (see Concrete Artifacts); (b) the review gate checks both technical completeness AND blameless language — that second check is exactly what an AI "blameless-language lint" tool could automate (Miner synthesis; see Cross-References). The review requirement is also the natural place for a human gate on AI-drafted postmortems.

### Claim 7: Postmortem learnings must be translated into concrete, assigned action items with an ETA — otherwise the organization is not improving
- **Evidence**: Sachto's "think about it" argument that action items are the only way learnings become fixes; her definition of what "action items" means.
- **Confidence**: settled
- **Quote**: "Ideally, we want to translate our learnings from the postmortem to concrete action items. Otherwise it means that we are not improving. Think about it. How can we fix the problem if we don't follow it up with action items?" — and — "But when we're saying 'action items,' those need to be concrete. And those need to be assigned, and ideally with an ETA."
- **Our assessment**: The action-item hygiene requirement, stated as a necessity ("how can we fix the problem if we don't follow it up"). Matches the IMAG Guide Claim 13 (action items feed the backlog with completion SLOs) — Sachto's version is the minimal bar (concrete + assigned + ETA), the Guide's is the fuller mechanism. This is a core Ch04/Ch03 toil-loop claim: unresolved action items = repeated incidents.

### Claim 8: One person owns the postmortem — writes it, gets it reviewed/approved, and publicizes it — and action-item ownership is flexible: an assignee may only triage (create a bug, set a meeting) rather than resolve everything, or an explicit "we don't know the owner" item creates a bug and starts a cross-team discussion
- **Evidence**: Sachto's description of postmortem ownership and the triage-style follow-up model.
- **Confidence**: settled
- **Quote**: "postmortems themselves need to have an owner and that owner needs to not just write it, but make sure that it's being reviewed and being approved and then being publicized—so shared globally, widely." — and — "that person will not necessarily be the person that will resolve everything, but they can be the ones that will triage it, that will create the bug, that will set up the meeting, that will do some sort of an action that will promote that action item." — and — "it's okay also to say, 'We don't know who is the owner of implementing X, Y, Z.' So the action items will be to create a bug and to start a discussion between those teams to make sure that it is being resolved by a specific date and time."
- **Our assessment**: Lowers the barrier to action-item follow-through: ownership is a named process (write → review → approve → publicize) and an action item can be advanced by triage rather than full resolution. The "we don't know the owner" escape hatch is a practical antidote to the "unassigned = never done" failure mode. The publicize step connects directly to Claim 12 (sharing).

### Claim 9: Postmortems use a "what went well / what could be improved / where we got lucky" analysis structure, and "got lucky" items must be converted into action items — e.g., someone happened to look at a dashboard because no alert existed becomes "create an alert / create a page"
- **Evidence**: Sachto's description of Google's standard section structure and her worked near-miss example.
- **Confidence**: settled
- **Quote**: "we usually have what went well and what could be improved—and for us, usually, in Google, we have also where we got lucky. Usually we want to translate the thing that we need to improve, what could be better, and where we got lucky to some sort of an action item." — and — "if we didn't have a monitor alert or we didn't have an alert on something, but a developer looked at the dashboard exactly at this time because they developed a new feature, so we got lucky, but maybe next time we won't get lucky. So ideally one action item will be to create an alert to create a page."
- **Our assessment**: The single most operational artifact in the episode: a named mechanism that turns a near-miss into a monitoring/toil work item. "Got lucky → build the alert" is a citable bridge between postmortem culture and alerting/monitoring work (Ch02/Ch04). An AI postmortem agent could plausibly auto-extract "got lucky" items and suggest the missing alert — but the *judgment* that the luck is not guaranteed is human (Miner synthesis).

### Claim 10: When to write a postmortem extends beyond declared severe incidents — customer impact, SLO breach, data loss without direct customer impact, near-miss, on-caller intervention, rollback before impact, low-priority incident with resolution time above a threshold, and monitor/tooling failure all warrant one
- **Evidence**: Sachto's enumeration after acknowledging the "obvious" Severity-1 / OMG case.
- **Confidence**: settled
- **Quote**: "If we are breaching those because of an incident, then we definitely need to write a postmortem as well." — and — "what if we have a case of data loss and we don't have a direct impact on the customer yet? So it's a potential customer impact, but at the moment we don't. We will still want to create a record of what happened, how it happened to keep track, to triage it." — and — "It can be also in a case when an on-caller intervenes. It can be also, we had a release and we had to roll back. We rolled back before we had a customer impact or the customer impact was so minor that we didn't open an incident, but we still want to keep track of that information." — and — "In case we had the monitor failures—so in case our tools fails us—it's not customer impact, but in case we had a customer impact, we wouldn't know."
- **Our assessment**: A concrete "when is a postmortem warranted" rubric the corpus lacked. Note the logic of the non-obvious triggers: each is a case where an incident *could have* happened (near-miss, rollback, monitor failure, data loss without impact) or an incident *was* worse than its label suggests (slow low-priority resolution). The "it's not one-to-one" caveat — teams define their own criteria — keeps this a rubric, not a rule. See Concrete Artifacts for the full checklist.

### Claim 11: A critical mass of postmortems enables pattern identification that reduces both the volume and frequency of incidents — postmortems and incidents feed each other in a learning loop
- **Evidence**: Sachto's explanation of how the relationship between incidents and postmortems goes "both ways."
- **Confidence**: settled
- **Quote**: "when we have a critical mass of postmortems, that can lead us to identifying patterns; that can lead us to actually reducing either incidents, again, both the volume of incidents and also the frequency of them. But in order to do that, we need to rely on postmortem data to prioritize what and how we should invest time and priorities."
- **Our assessment**: The meta-postmortem claim at the individual-org level: postmortem data is not just retrospective but feeds forward into incident reduction. Same mechanism as the IMAG Guide Claim 14 and S3E06 Claim 5 (aggregating postmortems to find common pain). This is the strategic justification for a shared, structured postmortem corpus — which is also exactly what an AI training/eval pipeline needs (see S4E9 cross-reference).

### Claim 12: Postmortems are a learning tool from others — organizations write them but fail to share them; a widely-shared postmortem prevented an incident in another team's system, and sharing should be as wide as possible with customer data redacted but never treated as a blocker
- **Evidence**: Sachto's observation of the sharing gap and her pre-Google anecdote of cross-team prevention.
- **Confidence**: settled (anecdote is one data point, but the claim is stated as a general practice gap)
- **Quote**: "a lot of organizations are writing a postmortem, are capturing those notes, but after that are not sharing them or not sharing it publicly enough, not widely enough. And it's a miss also." — and — "because someone wrote a postmortem for an issue that was in a production system that was not under my, let's say, ownership at the time, and they shared it publicly, they shared it with R&D in general—I actually was able to prevent an incident in our own system because they shared a problem that we also encountered." — and — "I do encourage every organization to share it as widely as possible and create the infrastructure to share it widely as well. Of course, in some cases, we need to redact some information, especially customer data and things like that, but it shouldn't be a block here."
- **Our assessment**: The share-widely argument, with a concrete cross-team prevention story. This is the case for a shared postmortem corpus within an org (and the guide's cross-team learning material). The "redact but don't block" principle is actionable policy. Corroborates the IMAG Guide's "honest and timely postmortem write-up shared broadly" (Claim 13) and the index note's mapping of S1E9 to SRE Book Ch15.

### Claim 13: Blamelessness and psychological safety are cultural transformations that take time — "more complicated than a checklist" — so start simple and iterate
- **Evidence**: Sachto's admission that the topic resists checklist-ification, and her iteration advice.
- **Confidence**: settled
- **Quote**: "Like any cultural thing and any cultural transformation or change, it's more complicated than a checklist or making sure that our language is aligned with specific terminology." — and — "start simple, iterate, like we're doing with software engineering problems. It will take time, but the important part is that we'll improve with time and do some strides to [a] better position."
- **Our assessment**: An honest scoping note: blameless language linting is necessary but not sufficient for blameless *culture*. This conditions Claim 4/5 — the mechanical parts (language, review checklists) are automatable; the cultural substrate is not. Relevant to how the guide frames AI postmortem tools: they can enforce the checklist, not the culture.

## Concrete Artifacts

### When-to-write-a-postmortem rubric (from the source's enumeration, quoted)

Sachto lists these triggers beyond the "no-brainer" Severity-1 / OMG (Outage Management at Google) case:

```
- Incident with customer impact            ("those are [a] very common baseline of writing a postmortem")
- SLO breach                               ("If we are breaching those because of an incident, then we definitely need to write a postmortem as well.")
- Data loss with no direct customer impact yet ("We will still want to create a record of what happened, how it happened to keep track, to triage it.")
- On-caller intervention
- Release rolled back before customer impact (or impact "so minor that we didn't open an incident")
- Traffic routed / mitigated during the release window
- Lower-priority incident with resolution time above a threshold
- Monitor / tooling failure                 ("if our tools fails us... in case we had a customer impact, we wouldn't know")
```

She caveats: "it's not one-to-one. There's a lot of cases that we would want to open a postmortem that maybe is not an incident with a specific priority or severity." and "Each team can define what are the criteria for them that they will write an incident."
*Source: Ayelet Sachto, SRE Prodcast S1E09 transcript ("when we should write a postmortem" exchange).*

### The three-section postmortem analysis structure (from the source)

```
what went well
what could be improved
where we got lucky        ← each "got lucky" item should become an action item
```

Quoted: "we usually have what went well and what could be improved—and for us, usually, in Google, we have also where we got lucky."
*Source: Ayelet Sachto, SRE Prodcast S1E09 transcript.*

### The timeline / stages requirement (from the source)

Quoted: "the timeline is very, very important; sometimes people are missing that. So they are writing when an incident started and when the impact may be mitigated, but they're not capturing all the stages. And it's important to understand the time it took for each step, because with this information we can improve and understand where we have gaps. Was it in the time it took us to detect the issue, when we actually got alerted on it, or was it escalated by a customer?"
*Source: Ayelet Sachto, SRE Prodcast S1E09 transcript.*

### The action-item requirement (from the source)

Quoted: "those need to be concrete. And those need to be assigned, and ideally with an ETA." with flexible fulfillment: "it's possible that for one team it's okay to put it on their board; for another team it will be to actually assign it to a person; for other teams and other also action items, it can be that it will be to set a meeting in the calendar."
*Source: Ayelet Sachto, SRE Prodcast S1E09 transcript.*

### Ben Treynor on the cost of an unlearned mistake (quoted by Sachto)

```
"mistakes are a valuable opportunity to learn and improve. And if we are missing
that opportunity, if we are not learning from our mistakes, we are taking the
cost of the mistake, but without the benefit of learning from it."
```
*Source: Sachto quoting "one of Ben Treynor's emails," SRE Prodcast S1E09 transcript.*

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3333) — **Corroborates** Claims 3–5 here (blamelessness / psychological safety / incident-hiding) with S3E11's **Claim 19** ("put him on stage" blameless mechanism with the identical causal argument: punitive action drives reporting underground and hidden flawed models → less resilience) and **Claims 8–9** (psychological safety to be wrong / normalize "I don't understand"). Both sources make the same claim: psychological safety is what surfaces failures, and it is a cultural, not mechanical, property. No contradiction.
2. **`docs-google-sre-prodcast.md`** (score 0.2821) — **Corroborates** (as locator): the index note maps **S1E9 → SRE Book Chapter 15 "Postmortem Culture"** (Claim 3 / Concrete Artifact table) and flags S1E9 as "blameless, actionable postmortem culture." This note is the mining of that index entry — no content-level corroboration beyond the mapping.
3. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2564) — **Corroborates** two claims: S3E06 **Claim 5** (meta-retrospective: "take the outcome of many postmortems and try and find those common factors" to drive tooling roadmaps) matches Claim 11 here (critical mass of postmortems → pattern identification); S3E06 **Claim 14** ("an outage that you don't learn from is a failure") matches Claim 2 here (no formalized learning → recurrence). Same learning-loop thesis, complementary granularity (episode = how to use postmortem data for tooling; Sachto = why postmortem data exists).
4. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2564) — **Dismissed.** SRE concepts outside Google / "scale shock"; no postmortem-practice claims to corroborate or contradict.
5. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2564) — **Dismissed.** AI-for-SRE tooling (early outage detection from support cases, ticket analysis, golden data sets). Different topic; no postmortem-practice claims.
6. **`docs-google-sre-prodcast-03-05-building-reliable-systems.md`** (score 0.2308) — **Corroborates** Claim 1 here (root causes, not just symptoms) with S3E05 **Claim 4** (generalize the outage — "see how the outage that happened could happen in another way" rather than patching the specific failure). Both demand postmortem learning go deeper than the single observed failure.
7. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2308) — **Dismissed.** SLOs as shared vernacular; the only bridge is Sachto's "SLO breach → write a postmortem" trigger (Claim 10 here), which is a passing use of SLOs as a trigger, not a claim about SLOs themselves.
8. **`docs-google-sre-prodcast-04-09-ai-agents.md`** (score 0.2308) — **Extends** the AI-relevance mapping: S4E9 **Claim 10** (postmortems are "super great training data" because they contain the full *trajectory* / timeline of the responder's steps) presupposes exactly the timeline-and-stages content Sachto mandates (Claim 6 here); S4E9 **Claim 13** (the majority of AI-agent work is converting "postmortems in different formats for different teams" into a uniform human-and-machine-readable form) shows why Sachto's mandatory-contents standard matters operationally. Together: a well-structured postmortem (this episode) is machine-readable eval/training data (S4E9).
9. **`docs-google-sre-reliable-product-launches.md`** (score 0.2051) — **Dismissed.** Launch coordination engineering; different lifecycle phase (pre-launch) with no postmortem-practice claims.
10. **`docs-google-sre-handling-overload.md`** (score 0.2051) — **Dismissed.** Load shedding / overload management; no postmortem content.

### Primary cross-references (from the Prospector's triage and manual search)

- **Corroborates**:
  - `docs-google-sre-incident-management-guide.md` — **Claim 11** ("open and blameless postmortem writing" as the most effective learning tool), **Claim 12** (blameless postmortems, "everyone involved... had good intentions"), and **Claim 13** (action items with completion SLOs feeding the backlog, shared broadly). Sachto's Claims 3–4, 7, 12 here are the conversational, mechanism-level versions of this written doctrine. The Guide's "good intentions" framing and Sachto's "switching responsibility" framing are complementary altitudes, not a contradiction.
  - `docs-google-sre-anatomy-of-an-incident.md` — **Same author** (Sachto is co-author of the ebook). Consistent throughout: the ebook's **Claim 10** (Venn-diagram systems analysis — "root causes... not just the symptoms" depth) matches Claim 1 here; its **Claim 5** (generic mitigations = fix symptoms to buy time) is the incident-phase counterpart to Sachto's follow-up-action requirement; ebook Ch5's postmortem/psychological-safety treatment matches Claims 3–5 here. This episode is the podcast-length, same-author treatment of the ebook's Ch5. No contradictions.
  - `docs-google-sre-prodcast-01-08-incident-management.md` — The adjacent episode (S1E08) closes with post-incident learning (Claim 3: recovery actions double as preparation; Claim 11: Treynor "only wants new incidents"). S1E09 is explicitly the "what happens after the incident" sequel (MP's intro: "this week we're moving on to what happens after the incident to close things out"). Sachto's prevent-recurrence goal (Claim 1 here) is the post-incident completion of S1E08's lifecycle.
  - `docs-google-sre-prodcast-04-04-zelesko-future-sre.md` — **Claim 9** (blameless postmortems are "core to everything we do" at Google, and AI/ML "can help with postmortems, action-item gathering"). The culture half corroborates Claims 3–5 here; the AI-assistance half corroborates the Miner's AI mapping in Guide Impact.
  - `docs-google-sre-prodcast-06-09-irt-incident-response.md` — **Claims 3–6** (psychological safety in incident response: deference to the IC as temporary role, "better to apologize for a page"). Same psychological-safety doctrine at the response-phase layer; Sachto applies it to the post-incident reporting layer.

- **Contradicts**: None identified. Blamelessness and psychological safety are stated consistently across the corpus (IMAG Guide Claim 12, S3E11 Claims 8/9/19, S6E09 Claims 3–6, Anatomy of an Incident Ch5); Sachto's contribution is the sharper definition, not a conflicting one. No contradiction issue filed.

- **Extends**:
  - `docs-google-sre-prodcast-01-08-incident-management.md` — S1E09 is the post-incident sequel: where S1E08 covers response (lifecycle, IMAG, three C's), this episode covers the learning loop that closes the lifecycle. The "where we got lucky → build the alert" mechanism (Claim 9 here) extends S1E08's hazard/trigger vocabulary with a concrete follow-through path from near-miss to monitoring work.
  - `blog-incidentio-ai-sre-incident-run.md` — **Claim 8** (AI SRE generates a "fully AI-written structured incident write-up" from Slack/transcripts/coding activity). Sachto's mandatory-contents checklist (Claims 1 & 6 here) is the human-authored schema that AI write-up tooling is built to auto-fill; her timeline/stages requirement is precisely what the AI's "structured write-up" must reproduce. Also conditions incident.io's claim: Sachto's review gate (Claim 6 here) is the human check the AI write-up is foundation for, not a replacement of.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — as detailed in candidate 8 above: structured postmortems (this episode) are the training/eval data AI agents consume (S4E9 Claims 10 & 13).

- **Novel**:
  - **The when-to-write-postmortem rubric** (Claim 10 / Concrete Artifacts) — the corpus had incident-declaration triggers (Anatomy of an Incident Claim 1) but not this explicit postmortem-trigger list (data loss without impact, near-miss, rollback, slow resolution, monitor failure).
  - **The "where we got lucky → action item" mechanism** (Claim 9) — a named, citable pattern connecting postmortems to monitoring/alerting work.
  - **Blamelessness defined as "switching responsibility from people to systems and processes"** (Claim 4) and **Ben Treynor's "cost of the mistake, but without the benefit of learning from it"** line — the former is new definitional specificity; the latter is a fresh Treynor attribution (S1E08's "only wants new incidents" is a different Treynor line).
  - **The formal psychological-safety definition** (Claim 5) as a quotable definition distinct from the corpus's situational treatments.
  - **The share-widely argument with the cross-team prevention anecdote** (Claim 12) — the "redact but don't block" sharing policy.
  - **Analytical bridge (Miner synthesis, not from source):** the automatable-vs-human boundary for AI postmortem tooling. Automatable per the source: timeline reconstruction from artifacts, action-item extraction, blameless-language *linting* (Claim 6's review criterion), got-lucky-item flagging (Claim 9). Not automatable: the reporting/declaring half — psychological safety (Claim 5) is a human trust property that no AI can install, and the review/approve/publicize gate (Claim 8) is explicitly human in the source. So AI postmortem drafting (incident.io Claim 8) must keep a human review gate — the source requires it, and `blog-pagerduty-production-ai-agent-gaps.md` (Claim 3 context fatigue, Claim 6 context poisoning) shows AI-generated write-ups can degrade exactly when incident context is long and noisy.

## Guide Impact

- **Chapter 01 (Incident Response) — postmortem section**: This is the primary-source baseline the section is missing. Add: (a) the mandatory-contents checklist (Claim 1), (b) the when-to-write-postmortem rubric (Claim 10 / Concrete Artifacts) as the decision table, (c) the three-section "what went well / what could be improved / where we got lucky" structure with the got-lucky → build-the-alert mechanism (Claim 9), (d) the review gate requirement (Claim 6) — which is also the natural human gate for AI-drafted postmortems (see below). The chapter's postmortem-drafting-with-AI target topic should present this episode as the human schema AI tools (incident.io Claim 8) fill.
- **Chapter 02 (SLOs and Monitoring)**: Use the got-lucky → create-an-alert mechanism (Claim 9) and the monitor-failure postmortem trigger (Claim 10) to connect postmortem culture to monitoring coverage gaps — near-misses are a detection-gap signal that should produce new alerts/pages, reinforcing the S1E03 alerting note's "actionable page" requirement.
- **Chapter 03 (Runbooks and Agents) / Chapter 05 (AI-assisted SRE)**: Anchor the AI-relevance boundary: blamelessness responsibility-shifting (Claim 4), psychological safety (Claim 5), and the human review/approve/publicize ownership model (Claim 8) define what AI postmortem tooling can and cannot replace. Recommended framing: AI automates timeline reconstruction, action-item extraction, blameless-language lint, and got-lucky flagging, but the source itself requires a human review gate — and PagerDuty's context-fatigue/poisoning gaps (Claims 3/6) justify keeping that gate mandatory rather than advisory.
- **Chapter 04 (On-call and Toil)**: Add action-item hygiene (concrete + assigned + ETA, triage-style ownership, Claim 7/8) and the action-item SLO/backlog mechanism already in the IMAG Guide (Claim 13) as the follow-through loop; add the sharing infrastructure recommendation (Claim 12) — postmortem data is the prioritization input for toil/investment decisions (Claim 2), consistent with the meta-retrospective method in S3E06 Claim 5.

## Extraction Notes

- The source is the SRE Prodcast S1E09 transcript, read end-to-end from the official sre.google HTML transcript (source_url). The issue #756 files the PDF variant (`https://sre.google/static/pdf/sre-prodcast-01-09.pdf`); the Prospector's triage verified both are the same episode transcript. The HTML page was used because the Assayer can spot-check quotes against it more easily than a PDF.
- No sub-pages were followed beyond the transcript itself. The two inline links in the transcript (`https://sre.google/workbook/postmortem-culture/` and `https://sre.google/sre-book/postmortem-culture/`) are the canonical SRE Workbook/Book chapters that this episode explicitly companions (SRE Book Ch15 per the index note `docs-google-sre-prodcast.md` Claim 3); both are already represented in the corpus and would not add extractable claims beyond this episode.
- All `Quote` passages are copied character-for-character from the fetched transcript, including the source's own minor grammatical irregularities ("those breakage should be widely communicated," "if our tools fails us," the parenthetical "—and yes, postmortems need to be reviewed—"). No quotes were reconstructed or spliced from non-adjacent sentences.
- The page carries no structured publish date; `date_published` is estimated as 2022, matching the sibling S1E08 note (Season 1 ran 2022; Sachto's *Anatomy of an Incident* is dated January 2022 and she is introduced as "currently" on GKE SRE).
- `confidence_overall` is `settled`: the dominant claims (definition/contents, blamelessness, psychological safety, action items, when-to-write criteria, sharing) are authoritative first-party Google SRE doctrine, spoken by a named, experienced Google SRE and consistent with the existing IMAG/Anatomy corpus. Claim 12's cross-team-prevention anecdote is a single data point but the claim itself (orgs fail to share; sharing prevents recurrence) is stated as general practice.
- The AI-relevance mapping (what's automatable vs. what assumes human psychological safety) is the Miner's analytical synthesis, clearly marked in Cross-References → Novel and Guide Impact. The source itself contains zero AI/LLM content.
- No contradiction issue was filed. The episode is consistent with the existing blameless-postmortem corpus; the only definitional differences (IMAG Guide "good intentions" vs. Sachto "switching responsibility"; Guide's backlog-SLO mechanism vs. Sachto's flexible triage ownership) are complementary framings of the same doctrine, not opposing claims.
