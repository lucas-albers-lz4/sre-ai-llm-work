---
source_url: https://sre.google/workbook/incident-response
source_type: documentation
title: "Google SRE: Incident Response — SRE Workbook Chapter 9"
author: "Jennifer Mace, Jelena Oertel, Stephen Thorne, and Arup Chakrabarti (PagerDuty), with Jian Ma and Jessie Yang"
date_published: 2018
date_extracted: 2026-08-10
last_checked: 2026-08-10
status: current
confidence_overall: settled
issue: "#852"
---

# Google SRE: Incident Response — SRE Workbook Chapter 9

> The SRE Workbook's deep-dive companion to the Incident Management Guide: the
> ICS-derived role hierarchy (IC/CL/OL with delegation mechanics), the "three Cs"
> (Coordinate, Communicate, Control), the "declare incidents early and often"
> doctrine, four full incident case studies (Google Home, GKE CreateCluster, GCE
> Persistent Disk, PagerDuty NTP), the generic-mitigations concept, and a
> concrete pre-incident preparation checklist plus drill menu. The genuinely new
> slice for the corpus is **PagerDuty's ICS-derived Incident Response process**
> (IC rotation staffing, Failure Friday failure-injection drills, open-postmortem
> culture) — the existing PagerDuty notes are AI-agent focused, not the PD IR
> process itself — and the four case-study narratives as concrete evidence for
> the already-settled IMAG/declare-early framework.

## Source Context

- **Type**: documentation — SRE Workbook (O'Reilly, 2018) Chapter 9 "Incident
  Response," published at `sre.google/workbook/incident-response/`. First-party
  Google/PagerDuty reference material; the chapter has no AI/LLM content.
- **Author credibility**: Highest available. Four named authors — three Google
  SRE practitioners (Jennifer Mace, Jelena Oertel, Stephen Thorne) plus Arup
  Chakrabarti of PagerDuty writing the PagerDuty case study — with Jian Ma and
  Jessie Yang. The Google authors write about the Incident Management at Google
  (IMAG) process they operate; Chakrabarti describes PagerDuty's own ICS-derived
  process from the inside. This is the canonical first-party SRE Workbook, the
  same authority family as the already-extracted `docs-google-sre-eliminating-toil.md`
  (Workbook Chapter 6).
- **Scope**: Covers (a) the ICS origin and the "three Cs" of incident
  management; (b) the main incident-response roles (IC/CL/OL) and their
  delegation/expansion mechanics; (c) four full incident case studies — Google
  Home (late declaration), GKE CreateCluster (IC handoff + missing generic
  mitigations), GCE Persistent Disk (early declaration, well-managed), PagerDuty
  NTP (IC rotation during response); (d) PagerDuty's IR process, training
  (Failure Friday, simulation games), and tooling stack; (e) a "Putting Best
  Practices into Practice" preparation checklist and drill menu. Does NOT cover
  SLOs, monitoring, toil, on-call rotation *scheduling* design (that is Workbook
  Chapter 8 "On-Call"), or any AI/LLM content.

## Extracted Claims

### Claim 1: Incident response splits into two activities — resolving the incident (mitigating impact/restoring service) and managing it (coordinating responders and ensuring communication flows)
- **Evidence**: Opening definition of the chapter; the distinction frames the
  entire role structure that follows (IC/CL/OL).
- **Confidence**: settled
- **Quote**: "Resolving an incident means mitigating the impact and/or restoring the service to its previous condition. Managing an incident means coordinating the efforts of responding teams in an efficient manner and ensuring that communication flows both between the responders and to those interested in the incident's progress."
- **Our assessment**: The canonical resolve-vs-manage split, consistent with the
  IMAG Guide's role-oriented framing. Buy fully — first-party Google doctrine.

### Claim 2: The basic principles of incident response are: maintain a clear line of command, designate clearly defined roles, keep a working record as you go, and declare incidents early and often
- **Evidence**: Explicit bulleted list in the chapter introduction.
- **Confidence**: settled
- **Quote**: "The basic principles of incident response include the following: Maintain a clear line of command. Designate clearly defined roles. Keep a working record of debugging and mitigation as you go. Declare incidents early and often."
- **Our assessment**: The chapter's own four-principle summary. Consistent with
  the IMAG Guide and S1E08; the chapter's contribution is the worked case-study
  evidence behind each principle (especially declare-early).

### Claim 3: ICS-based incident response frameworks share the "three Cs" — Coordinate, Communicate, and Control — and when incident response goes wrong, the culprit is likely in one of these three areas
- **Evidence**: Explicit definition of the 3Cs; stated as the common goals of
  both PagerDuty's and Google's ICS-derived frameworks.
- **Confidence**: settled
- **Quote**: "Incident response frameworks have three common goals, also known as the "three Cs" (3Cs) of incident management: Coordinate response effort. Communicate between incident responders, within the organization, and to the outside world. Maintain control over the incident response."
- **Our assessment**: This chapter uses the SAME 3Cs framing as the Incident
  Management Guide (Coordinate/Communicate/Control) — not the Prodcast S1E08
  framing (Command/Control/Communications). That means two first-party written
  Google sources agree on the "coordinate, communicate, control" version,
  strengthening the Guide's framing over the conversational S1E08 version. This
  is the framing-difference already assessed as complementary in the IMAG Guide
  note, not a new contradiction.

### Claim 4: The IMAG role hierarchy is IC/CL/OL — the IC leads, the CL and OL report to the IC; by default the IC assumes all roles that have not been delegated yet, and the CL/OL teams expand or contract as needed
- **Evidence**: Explicit role definitions plus the delegation/expansion
  mechanics — the IC "assumes all roles that have not been delegated yet," the
  IC may hand off their role or assign the OL role, both CL and OL may lead
  teams that "expand or contract as needed," and the CL role can be subsumed
  back into the IC role when the incident becomes small.
- **Confidence**: settled
- **Quote**: "By default, the IC assumes all roles that have not been delegated yet." — and — "Both the CL and OL may lead a team of people to help manage their specific areas of incident response. These teams can expand or contract as needed. If the incident becomes small enough, the CL role can be subsumed back into the IC role."
- **Our assessment**: This is the delegation/expansion mechanics the IMAG Guide
  states at a higher level. The "IC assumes all undelegated roles by default"
  rule and the CL/OL expansion/contraction are the operational detail that makes
  the hierarchy work at scale — new specificity beyond the Guide note.

### Claim 5: Declaring an incident early makes incidents resolve faster — it prevents miscommunication, speeds root-cause identification, and gets relevant teams and external communications looped in earlier; the Google Home incident shows the cost of late declaration
- **Evidence**: The Google Home case study (Case Study 1) — a bug in Google
  Assistant 1.88 caused speaker recognition files to be fetched 50× more often
  than expected, exceeding quota; the team never declared an incident, relied on
  repeated quota increases and heroic weekend effort, and users "lost half of
  their requests during the weekend of June 3, 2017" before resolution. The
  chapter's review states the declare-early benefits explicitly.
- **Confidence**: settled
- **Quote**: "The team did not declare an incident, but continued to troubleshoot the issue via "normal" methods, using the bug tracking system for communication." — and — "Our experience shows that managed incidents are resolved faster. Declaring an incident early ensures that: Miscommunication between the client and server developers is prevented. Root-cause identification and incident resolution occur sooner. Relevant teams are looped in earlier, making external communications faster and smoother."
- **Our assessment**: This is the canonical "declare early and often" doctrine
  backed by a concrete counterfactual (late declaration prolonged a week-long
  incident that was mitigated three times but never root-caused until the end).
  Already settled in the corpus (IMAG Guide, Anatomy); the workbook adds the
  case-study evidence.

### Claim 6: Incident command should be handed off to whoever is best suited — the GKE CreateCluster case study shows the IC handing command to a more experienced responder mid-incident, and the GCE case study shows the IC retaining command because their team had the best customer-impact visibility
- **Evidence**: Case Study 2 (GKE CreateCluster): Zara, the London on-call who
  declared the incident, "decided to hand over incident command to Il-Seong
  before 10 a.m., since he had more experience with IMAG." Case Study 3 (GCE
  Persistent Disk): the Persistent Disk SRE on-call "retained the IC role, since
  that team had the best visibility into customer impact."
- **Confidence**: settled
- **Quote**: "Zara decided to hand over incident command to Il-Seong before 10 a.m., since he had more experience with IMAG." — and — "The Persistent Disk SRE's primary on-call retained the IC role, since that team had the best visibility into customer impact."
- **Our assessment**: Two worked illustrations of the "roles follow knowledge,
  not reporting chains" principle from the IMAG Guide. The handover pattern is
  concrete evidence that IC is a context-dependent role, not a fixed assignment.

### Claim 7: Generic mitigations — pre-prepared actions that stop user pain before the root cause is understood — are crucial for fast recovery; the GKE incident was prolonged because the service had none
- **Evidence**: Case Study 2 review defines generic mitigations (roll back a
  recent release correlated with the outage; reconfigure load balancers to avoid
  a region) and shows that a generic mitigation after the 9:56 a.m. plausible
  cause would have mitigated the 6h40m outage by 10 a.m.
- **Confidence**: settled
- **Quote**: "Generic mitigations are actions that first responders take to alleviate pain, even before the root cause is fully understood." — and — "To mitigate an incident, you don't have to fully understand the details—you only need to know the location of the root cause."
- **Our assessment**: The workbook's term for the same concept as the Anatomy
  ebook's "generic mitigations" (Claim 5 there). This case study adds the
  counterfactual timeline proving the value — and the statement that mitigation
  tools "should be created before an incident occurs" (from the chapter review)
  is a concrete Ch03/tooling argument.

### Claim 8: First responders must prioritize mitigation above all else — the active-incident sequence is assess impact, mitigate impact, perform root-cause analysis, then fix and write a postmortem
- **Evidence**: Case Study 2 review's explicit ordering and the "customers do
  not care whether or not you fully understand what caused an outage" line.
- **Confidence**: settled
- **Quote**: "It's important to remember that first responders must prioritize mitigation above all else, or time to resolution suffers." — and — "Ultimately, customers do not care whether or not you fully understand what caused an outage. What they want is to stop receiving errors." — and — "Assess the impact of the incident. Mitigate the impact. Perform a root-cause analysis of the incident. After the incident is over, fix what caused the incident and write a postmortem."
- **Our assessment**: The mitigation-first response doctrine, concretely ordered.
  Corroborates S1E08's "Band-Aid first" and the Anatomy ebook's "stop or lessen
  user impact first." The "customers only want errors to stop" line is a strong,
  quotable rationale for prioritizing mitigation over understanding.

### Claim 9: PagerDuty's major-incident response rotates the on-call engineers and the Incident Commander every four hours, to encourage rest and bring fresh ideas — demonstrated on a 10-hour NTP incident with minimal customer impact
- **Evidence**: Case Study 4 (PagerDuty NTP, October 6, 2017): internal NTP
  clock drift cascaded across software teams; the SRE on-call declared a major
  incident and alerted the IC on-call at 9:49 p.m.; the response team rotated
  engineers and IC every four hours for the eight-hour response.
- **Confidence**: settled
- **Quote**: "During this time, we rotated on-call engineers and the IC every four hours. Doing so encouraged engineers to get rest and brought new ideas into the response team." — and — "The incident occurred on October 6, 2017, and lasted more than 10 hours, but had very minimal customer impact."
- **Our assessment**: A concrete IC-rotation pattern for *long* incidents — the
  incident-time analog of on-call rotation freshness. New operational detail not
  in the existing corpus (which covers rotation *scheduling* design, not
  rotation *during* an incident).

### Claim 10: PagerDuty's ICS-derived Incident Response process is purposefully non-static and trained via Failure Friday failure-injection drills, time-bound simulation games, and open postmortem culture
- **Evidence**: Case Study 4 describes PagerDuty's process evolution (from a
  permanent company-wide IC to a rotation), Failure Friday (inspired by Netflix's
  Simian Army, manual failure injection, nominees act as a real IC with
  subject-matter experts using real processes and vernacular), the
  "Keep Talking and Nobody Explodes" simulation game, and open postmortems with
  recorded incident calls.
- **Confidence**: settled
- **Quote**: "Our Incident Response processes are purposefully not static; they change and evolve just as our business does." — and — "PagerDuty drew inspiration from Netflix's Simian Army to create this program." — and — "We also record all of the phone calls involved in a major incident so we can learn from the real-time communication feed."
- **Our assessment**: This is the genuinely novel slice of the chapter for the
  corpus — a real non-Google, ICS-derived incident-response framework. The
  existing PagerDuty notes are AI-agent focused (SRE Agent architecture, triage,
  production gaps), not the PD IR process itself. Failure Friday as a named
  failure-injection drill program and the open-postmortem-with-recorded-calls
  culture are new.

### Claim 11: PagerDuty's incident-response tooling stack pairs a source-of-truth metadata tool with a dedicated scribe-led war-room channel and a static conference call where coordination decisions are made and recorded
- **Evidence**: The "Tools used for incident response" section enumerates three
  tools: PagerDuty (on-call info, service ownership, postmortems, incident
  metadata — "allows us to rapidly assemble the right team"), a dedicated
  `#incident-war-room` Slack channel "used mostly as an information ledger for
  the scribe, who captures actions, owners, and timestamps," and a static
  conference call where "all coordination decisions are made," with every call
  recorded so the timeline can be recreated.
- **Confidence**: settled
- **Quote**: "We maintain a dedicated channel (#incident-war-room) as a gathering place for all subject-matter experts and Incident Commanders. The channel is used mostly as an information ledger for the scribe, who captures actions, owners, and timestamps." — and — "We prefer that all coordination decisions are made in the conference call, and that decision outcomes are recorded in Slack. We found this was the fastest way to make decisions."
- **Our assessment**: A concrete, human incident-tooling baseline relevant to
  Ch03 (runbook/agent tooling). The metadata-sources-of-truth + scribe-led
  ledger + decision bridge pattern is exactly the topology an AI incident agent
  would populate (role-aware summaries, timeline reconstruction). Corroborates
  the channel-separation pattern from S3E06 and the war-room centralization from
  the IMAG Guide.

### Claim 12: Incident-response preparation should be done before an incident — pre-decide the communication channel, prepare a contact list, establish incident criteria from past outages/high-risk areas, and keep ready-to-use communication templates
- **Evidence**: The "Putting Best Practices into Practice" section's "Prepare
  Beforehand" tips: "no Incident Commander wants to make this decision during an
  incident" (comms channel), prepared contact list (the GKE Comms Lead's "all
  hands on deck" email used pre-prepared lists), incident criteria "by looking
  at past outages, taking known high-risk areas into consideration," and "two or
  three ready-to-use templates" for public communications.
- **Confidence**: settled
- **Quote**: "Decide and agree on a communication channel (Slack, a phone bridge, IRC, HipChat, etc.) beforehand—no Incident Commander wants to make this decision during an incident." — and — "Also, prepare two or three ready-to-use templates for sharing information, making sure the on-call knows how to send them."
- **Our assessment**: A concrete, actionable preparation checklist. The
  "establish criteria for an incident" item is the operational version of the
  Anatomy ebook's three-criteria incident definition, and the pre-made comms
  templates connect to the CL role's public-facing duties.

### Claim 13: Incident-response drills — DiRT company-wide resilience testing, Wheel of Misfortune, inventing outages from postmortems, and breaking the test environment — build response muscle memory and reveal gaps
- **Evidence**: The "Drills" section lists Google's Disaster Recovery Testing
  (DiRT, company-wide controlled emergencies), Wheel of Misfortune, treating
  minor problems as major ones for low-stakes practice, inventing outages (also
  "create outages from postmortems, which contain plenty of ideas"), and breaking
  the test environment to troubleshoot with real tools. Drills should be
  periodic and followed by a report on what went well/wrong.
- **Confidence**: settled
- **Quote**: "Google runs company-wide resilience testing (called Disaster Recovery Testing, or DiRT), in which we create a controlled emergency that doesn't actually impact customers. Teams respond to the controlled emergency as if it were a real emergency." — and — "You can also create outages from postmortems, which contain plenty of ideas for incident management drills. Use real tools as much as possible to manage the incident. Consider breaking your test environment so the team can perform real troubleshooting using existing tools." — and — "The most valuable part of running a drill is examining their outcomes, which can reveal a lot about any gaps in incident management."
- **Our assessment**: A catalog of drill mechanisms with the "learn from the
  outcome, not the exercise" framing. Extends the existing corpus's Wheel of
  Misfortune mentions (Treynor interview, S1E07) with the DiRT and
  break-the-test-environment patterns. Directly relevant to Ch04 preparation
  and to agent-based incident-simulation tooling.

## Concrete Artifacts

### The four basic principles of incident response (verbatim from source)

```
- Maintain a clear line of command.
- Designate clearly defined roles.
- Keep a working record of debugging and mitigation as you go.
- Declare incidents early and often.
```
*Source: SRE Workbook Chapter 9, chapter introduction.*

### The three Cs (verbatim from source)

```
- Coordinate response effort.
- Communicate between incident responders, within the organization, and to the outside world.
- Maintain control over the incident response.
```
*Source: SRE Workbook Chapter 9, "Incident Command System" section.*

### The active-incident sequence (verbatim from source)

```
1. Assess the impact of the incident.
2. Mitigate the impact.
3. Perform a root-cause analysis of the incident.
4. After the incident is over, fix what caused the incident and write a postmortem.
```
*Source: SRE Workbook Chapter 9, Case Study 2 review.*

### GKE CreateCluster error message (verbatim from source)

```
error: failed to run Kubelet: cannot create certificate signing request: Post
https://192.0.2.53/apis/certificates.k8s.io/v1beta1/certificatesigningrequests
```
*Source: SRE Workbook Chapter 9, Case Study 2 incident narrative.*

### GKE CreateCluster incident metrics (verbatim from source)

```
"CreateCluster had failed in Europe for 6 hours and 40 minutes before it was
fixed. In IRC, 41 unique users appeared throughout the incident, and IRC logs
stretched to 26,000 words. The effort spun up seven IMAG task forces at various
times, and as many as four worked simultaneously at any given time. On-calls
were summoned from six teams, not including those from the "all hands on deck"
call. The postmortem contained 28 action items."
```
*Source: SRE Workbook Chapter 9, Case Study 2.*

### PagerDuty's incident tooling stack (verbatim from source)

```
- PagerDuty: "We store all of our on-call information, service ownership,
  postmortems, incident metadata, and the like, in PagerDuty. This allows us to
  rapidly assemble the right team when something goes wrong."
- Slack: "We maintain a dedicated channel (#incident-war-room) as a gathering
  place for all subject-matter experts and Incident Commanders. The channel is
  used mostly as an information ledger for the scribe, who captures actions,
  owners, and timestamps."
- Conference calls: "We prefer that all coordination decisions are made in the
  conference call, and that decision outcomes are recorded in Slack. We found
  this was the fastest way to make decisions. We also record every call to make
  sure that we can recreate any timeline in case the scribe misses important
  details."
```
*Source: SRE Workbook Chapter 9, Case Study 4 "Tools used for incident response."*

### The preparation checklist (structured from the "Prepare Beforehand" section)

```
1. Decide and agree on a communication channel beforehand.
2. Keep the audience informed with regular status updates; call off the
   response explicitly once mitigated/resolved.
3. Prepare a list of people to email or page beforehand.
4. Establish criteria for what counts as an incident (from past outages and
   known high-risk areas).
5. Prepare two or three ready-to-use communication templates (with PR-team
   review path at Google).
6. Encourage a mitigation-first response; define IC/CL/OL roles and let
   on-calls know they can delegate and escalate.
```
*Source: SRE Workbook Chapter 9, "Putting Best Practices into Practice" section (paraphrase of the section's tips; direct quotes in Claims 12–13).*

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3243) — **Extends (thematic).** Claim 4 there ("no single person's mental model of a large system is ever complete... multiple diverse perspectives are required for incident response") is directly illustrated by this chapter's Case Study 2, whose framing premise is "a system with so many interactions that no single person can grasp all the details" and whose resolution required 41 responders across seven task forces. The workbook supplies the concrete incident narrative for the complexity claim; not a corroboration of a specific assertion so much as a case-study instance of it.

2. **`docs-google-sre-eliminating-toil.md`** (score 0.2703) — **Dismissed.** Workbook Chapter 6 covers the toil taxonomy and measurement framework. No overlap with incident-response process or case studies; no claims to corroborate or contradict.

3. **`docs-google-sre-configuration-specifics.md`** (score 0.2703) — **Dismissed.** Workbook Chapter 15 covers configuration toil and DSL design. Different domain.

4. **`docs-google-sre-data-processing-pipelines.md`** (score 0.2432) — **Dismissed.** Workbook Chapter 13 covers pipeline SLOs and data correctness. Different domain.

5. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2432) — **Extends.** This chapter's PagerDuty tooling stack (Claim 11 here) is the concrete instantiation of S3E06's channel-separation pattern (Claim 4 there: engineering voice bridge vs customer-support channel) and its scribe-led ledger concept. S3E06 Claim 16 (the empty-list-purge destructive automation) is confirmed by the S3E06 host as an SRE Workbook case study — a tie-back to this same workbook series. Also, Claim 12 here (mitigation tools built *before* incidents) dovetails with S3E06's postmortem-driven tooling roadmap (Claim 5).

6. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2432) — **Dismissed.** Scale shock and concept-transferability for SREs outside Google. No incident-response overlap.

7. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2432) — **Dismissed.** AI for SRE tooling (early outage detection from support cases). The workbook chapter has zero AI content; the connection is only that incident response is what the AI tooling assists. No claims to corroborate.

8. **`docs-google-sre-prodcast.md`** (score 0.2432) — **Dismissed.** Prodcast index note. No substantive overlap.

9. **`docs-google-sre-prodcast-03-05-building-reliable-systems.md`** (score 0.2162) — **Dismissed.** Database reliability and managed databases. Different domain.

10. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2162) — **Dismissed.** SLOs as shared vernacular / bespoke per-service. The workbook chapter does not engage SLO theory.

### Primary cross-references (from the Prospector's triage and manual search)

- **Corroborates**:
  - `docs-google-sre-incident-management-guide.md` — The closest overlap. Claim 6 there (the 3Cs are "coordinate, communicate, and control") is confirmed verbatim by this workbook chapter's 3Cs (Claim 3 here) — two first-party written Google sources now agree on this framing, against the Prodcast S1E08 "Command, Control, Communications." Claim 7 there (IC/CL/OL hierarchy, "roles do not follow reporting chains") is corroborated and given operational mechanics by Claim 4 here (IC assumes all undelegated roles; CL/OL teams expand/contract; CL subsumed back into IC) and by the two role-assignment case-study instances (Claim 6 here).
  - `docs-google-sre-anatomy-of-an-incident.md` — Claim 5 there (generic mitigations: roll back, drain traffic, add capacity, "fix symptoms not causes") is corroborated and evidenced by Claim 7 here (the GKE counterfactual timeline). Claim 3 there (declare and close rather than open retroactively; late declaration is an anti-pattern) is corroborated by the Google Home case study (Claim 5 here). Claim 6 there (severity classification) has no counterpart in this chapter — the chapter does not classify severity.
  - `docs-google-sre-prodcast-01-08-incident-management.md` — Claim 5 there (IMAG is Google's variant of the FEMA incident management system) is corroborated by this chapter's IMAG treatment; Claim 4 there ("figure out user impact immediately, then apply a Band-Aid") is corroborated by the mitigation-first sequence (Claim 8 here) and generic mitigations (Claim 7 here). The 3Cs differ in wording (S1E08: Command/Control/Communications vs this chapter + IMAG Guide: Coordinate/Communicate/Control) — the known complementary framing difference, not a contradiction.
  - `docs-google-sre-prodcast-06-09-irt-incident-response.md` — Claim 1 there (Tech IRT is a threshold-triggered escalation tier) is not contradicted by this chapter (which predates IRT detail); the chapter's escalation descriptions (GKE paging infra/network/compute teams; PagerDuty alerting the IC on-call) are the single-team escalation precursor the IRT system formalizes. Referenced as background, not a numbered-claim corroboration.
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` — Claim 4 there (keep on-duty work separate so it doesn't drain the on-caller) connects to the PagerDuty 4-hour IC rotation (Claim 9 here): both are freshness-protection patterns, one at rotation-design time, one at incident time. Also, the "rollouts during business days" lesson in the Google Home review (Claim 5 here) corroborates the operational cadence norms discussed in S1E07.

- **Contradicts**: None identified. No contradiction issue was filed. The only
  cross-source tension is the 3Cs wording (this chapter + IMAG Guide =
  Coordinate/Communicate/Control; S1E08 = Command/Control/Communications),
  which the IMAG Guide note already assessed as complementary framings of the
  same system (role-oriented vs function-oriented). This chapter strengthens the
  Coordinate/Communicate/Control side with a second first-party written source;
  it does not assert S1E08 is wrong.

- **Extends**:
  - `docs-google-sre-incident-management-guide.md` — Extends the Guide with (1) the delegation/expansion mechanics of the role hierarchy (IC assumes all undelegated roles; CL/OL expand/contract; CL subsumed back into IC), (2) the four full case-study narratives as concrete evidence for the declare-early / role-handoff / mitigation-first doctrines, and (3) the preparation checklist + drill menu.
  - `docs-google-sre-prodcast-01-08-incident-management.md` — Extends S1E08's Band-Aid concept with the named "generic mitigations" framework and a counterfactual timeline proving its value (Claim 7 here).
  - `docs-google-sre-anatomy-of-an-incident.md` — Extends the Anatomy ebook's generic-mitigations concept with a full case-study proof (Claim 7 here).
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — Extends S3E06's channel-separation and meta-retrospective tooling claims with PagerDuty's concrete three-tool stack (Claim 11 here).
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` — Extends the on-call freshness principle with the incident-time IC rotation pattern (Claim 9 here).

- **Novel** (content new to the corpus):
  - **PagerDuty's ICS-derived Incident Response process** (Claims 9–11) — IC-rotation staffing during long incidents, Failure Friday failure-injection drills (Netflix Simian Army lineage), the "Keep Talking and Nobody Explodes" time-bound simulation game, open-postmortem culture with recorded incident calls, and the three-tool stack (metadata source of truth + scribe-led `#incident-war-room` + recorded static conference call). Existing PagerDuty notes are all AI-agent focused; none describe the PD IR process itself.
  - **The four case-study narratives** (Google Home, GKE CreateCluster, GCE Persistent Disk, PagerDuty NTP) — concrete incident-response evidence with named individuals, timelines, and metrics (41 IRC users, 26,000-word logs, 7 task forces, 28 action items, 6h40m duration, 0.000001% data loss, 10-hour NTP incident).
  - **The IMAG delegation/expansion mechanics** — "IC assumes all roles not yet delegated by default," CL/OL teams expand/contract, CL subsumed back into IC when small.
  - **The "mitigation tools should be built before incidents occur" argument** — "The right time to create general-purpose mitigation tools is before an incident occurs, not when you are responding to an emergency."

## Guide Impact

- **Chapter 01 (Incident Response)**: Add: (a) the IMAG delegation mechanics (Claim 4) — IC-assumes-undelegated-roles default, CL/OL expansion/contraction, CL subsumption — as the operational detail beneath the IC/CL/OL role set; (b) the four case studies as concrete evidence for the declare-early doctrine (Claim 5) and role-handoff-by-knowledge (Claim 6); (c) the generic-mitigations concept with its counterfactual timeline (Claim 7) and the mitigation-first active-incident sequence (Claim 8). Present the 3Cs as "Coordinate, Communicate, Control" citing this chapter AND the IMAG Guide (two first-party written sources) with the S1E08 "Command, Control, Communications" noted as the complementary conversational framing.

- **Chapter 03 (Runbooks and Agents)**: Use PagerDuty's three-tool stack (Claim 11) as the human tooling baseline an AI incident agent populates — metadata source of truth, scribe-led war-room ledger, decision bridge with recorded timeline. Add the "build mitigation/general-purpose tools before the incident" argument (Claim 7's review section) as justification for pre-built runbook/rollback tooling, and the "mitigation over understanding" framing (Claim 8) as a design constraint on agent behavior (stabilize before deep-diagnose).

- **Chapter 04 (On-call and Toil)**: Add the incident-time IC/responder rotation pattern (Claim 9) as freshness protection for long incidents, complementing rotation-scheduling design from S1E07; add the drill menu (Claim 13) — DiRT, Wheel of Misfortune, invented/postmortem-derived outages, break-the-test-environment — as the preparation/practice standard; add the preparation checklist (Claim 12) as the pre-incident baseline. Note the Google Home lesson that incident response "shouldn't rely on heroic efforts of individuals" (Claim 5's review) and that rollouts should happen on business days.

- **Chapter 05 (AI-assisted SRE)**: The Failure Friday drill pattern (Claim 10) and the break-the-test-environment technique (Claim 13) are the natural harnesses for evaluating AI incident agents against realistic scenarios; PagerDuty's recorded-call timeline reconstruction (Claim 11) is the human capability an agent's timeline/scribe function automates. These are the Miner's analytical bridges — the source itself contains no AI content.

## Extraction Notes

- The source is a single public page on sre.google
  (https://sre.google/workbook/incident-response), fetched and read end-to-end
  (the full chapter text). No sub-pages were followed per MINER.md §1 — the
  chapter is self-contained; the linked `response.pagerduty.com/about` page is
  the vendor site already described inside the chapter and not needed for the
  claims here.

- All `Quote` fields are copied character-for-character from the fetched chapter
  text, verified line-by-line against the saved fetch. Multi-fragment quotes are
  joined with "— and —"; each fragment is a contiguous passage from the source
  (trimmed only at sentence boundaries). The GKE error message and the incident
  metrics in Concrete Artifacts are verbatim, including the line break in the
  error message.

- **Triage-note discrepancy**: one Prospector triage comment references an
  "on-call rotation design section" in this chapter and maps it to Ch04. This
  chapter (Incident Response, Workbook Ch 9) contains no on-call rotation
  *scheduling* design — that is Workbook Chapter 8 "On-Call" (a separate page,
  not fetched here). What this chapter does contain is the incident-time IC
  rotation in the PagerDuty NTP case study (Claim 9), which I extracted as such.
  The Ch04 mapping still applies via the incident-time rotation pattern and the
  drill/preparation content, not via rotation-scheduling design.

- `date_published` is 2018 (SRE Workbook, O'Reilly, first edition; page footer
  confirms "Copyright © 2018 Google, Inc."). This predates the Dec-2025 recency
  cutoff, but as canonical first-party reference material it is consistent with
  the other workbook/book chapters already in the corpus (eliminating-toil,
  anatomy-of-an-incident). The chapter is undated evergreen practice.

- `confidence_overall` is `settled`: the dominant claims (resolve-vs-manage
  split, 3Cs, IC/CL/OL hierarchy, declare-early, mitigation-first, preparation
  checklist, drills) are canonical first-party SRE doctrine established over
  decades. The four case studies are first-person accounts of real, documented
  incidents (Google Home 2017, GKE CreateCluster, GCE Belgium 2015, PagerDuty
  NTP 2017). No claim here is speculative or forward-looking.

- **Contradiction check**: No contradiction issue filed. The only cross-source
  tension — 3Cs wording vs S1E08 — is the complementary-framing difference
  already assessed in `docs-google-sre-incident-management-guide.md`; this
  chapter adds a second first-party written source to the
  Coordinate/Communicate/Control side. No intra-source disagreement found.

- The source has no AI/LLM content. All AI/agent relevance (Chapter 03/05
  impact, the PagerDuty-IR-process novelty framing) is the Miner's analytical
  synthesis, clearly marked, to be reviewed by the Smith for fidelity.
