---
source_url: https://sre.google/resources/practices-and-processes/incident-management-guide/
source_type: documentation
title: "Google SRE — Incident Management Guide"
author: "Adam Crume, Alex Cepoi, Chelsea Granados, Roxana Loza, Steve McGhee, Svetlana Gites, Trevor Mattson-Hamilton, and Vrai Stacey (Google SRE)"
date_published: undated (page on sre.google; references SRE Workbook and IMAG, contemporaneous with SRE Prodcast S1E08 / 2022–2026 range)
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: settled
issue: "#528"
---

# Google SRE — Incident Management Guide

> Google's official first-party written incident management guide, published on
> sre.google. Defines the end-to-end incident lifecycle — preparation (SLO-based
> symptom alerting, playbooks, Wheel of Misfortune), IMAG role structure with the
> three Cs (Coordinate, Communicate, Control), IRT escalation, and blameless
> postmortem culture. This is the canonical written framework that the SRE Prodcast
> incident-management episode (S1E08) covers in conversational form. The guide's
> framing of the three Cs and its introduction of the Operations Lead role are
> notable differences from the Prodcast treatment.

## Source Context

- **Type**: documentation — first-party Google SRE reference page, part of the
  "practices and processes" series on sre.google.
- **Author credibility**: Eight named authors from Google SRE/Cloud, including
  Steve McGhee (Google Reliability Advocate, regular Prodcast host) and Vrai
  Stacey (Staff Software Engineer, Google internal IR tooling — also guest on
  S3E06 of the SRE Prodcast). Published on the official sre.google domain. This
  is the canonical process definition, not a secondary or vendor account.
- **Scope**: Covers the end-to-end incident management lifecycle — preparation
  (alerting, oncall, playbooks, automation), response and management (IMAG/ICS,
  3Cs, IC/CL/OL roles, IRT escalation), and post-incident learning (blameless
  postmortems, action items, trend aggregation). Does NOT contain code examples,
  config files, metrics, or quantitative benchmarks. The page is a concise
  primer (~2,000 words) rather than a deep-dive — it serves as an authoritative
  overview that the SRE Workbook and SRE Book chapter 9 expand on.

## Extracted Claims

### Claim 1: Outages are inevitable in complex systems; a well-defined incident management process minimizes impact and enables learning
- **Evidence**: Opening statement of the guide; establishes the thesis for the
  entire page.
- **Confidence**: settled
- **Quote**: "Outages are inevitable in any sufficiently complex system."
- **Our assessment**: Settled, foundational SRE principle. Provides the framing
  for why incident management process matters. The guide cites the goal as
  minimizing impact and learning, which is consistent with the SRE Prodcast
  lifecycle framing (S1E08 Claim 3).

### Claim 2: A good alerting mechanism must meet four attributes — timely, cover all key user-facing functionality, symptom-based not cause-based, and actionable
- **Evidence**: Listed as four explicit bullet points in the "Prepare for
  Incidents" section.
- **Confidence**: settled
- **Quote**: "Alert in a timely manner: Minimize the user impact prior to
  incident response beginning." / "Cover all key user facing functionality" /
  "Alert based on symptoms, not causes" — alerts "should be based on end-to-end
  measures of customer/client experience." / "Be actionable: Alerts that cannot
  be acted upon by an on-caller generate noise."
- **Our assessment**: Settled, authoritative guidance from Google SRE. The
  symptom-based alerting principle is the critical one — it directly connects to
  SLO-based alerting (Claim 3) and is the foundation for meaningful alerting
  that AI agents can act on. The actionable requirement echoes Prodcast S1E03
  (alerting episode Claim 5: "a paging alert must be both urgent AND
  actionable").

### Claim 3: Alerting based on SLOs is the recommended method to achieve timely, comprehensive, symptom-based alerting; avoid alerting on internal system behavior except for preventive capacity-quota alerts
- **Evidence**: Explicit recommendation in the guide, with the exception noted
  for hard resource quota limits.
- **Confidence**: settled
- **Quote**: "Alerting based on SLOs (Service Level Objectives for particular
  functionality) is a good way to achieve the first three attributes." / "the
  general rule is to avoid alerting on a system's internal behavior" because
  such alerts "don't accurately map to user impact" and "are fragile due to
  being closely bound to a service's implementation."
- **Our assessment**: This is the canonical SRE symptom-alerting doctrine,
  directly applicable to the guide's Ch02 (SLO-based alerting) material. The
  "general rule" language with the resource-quota exception is a nuanced,
  practical stance — hard limits can cause instantaneous 0%→100% failure
  transitions that symptom alerts cannot catch in time. This nuance is absent
  from the S1E03 Prodcast alerting note.

### Claim 4: Oncall readiness requires up-to-date playbooks, playbook awareness, and regular "Wheel of Misfortune" practice exercises
- **Evidence**: Explicit recommendations in the "Prepare for Incidents" section.
- **Confidence**: settled
- **Quote**: "Having up to date playbooks with instructions on how to debug and
  mitigate issues can speed up incident response significantly." / "Wheel of
  Misfortune exercises keep knowledge fresh and provide an opportunity for less
  experienced oncallers to develop their skills in a safe environment."
- **Our assessment**: Standard SRE oncall preparation practice. The Wheel of
  Misfortune reference is a specific Google practice worth capturing — it's a
  concrete preparation mechanism for Ch04 (oncall readiness). The explicit
  requirement that oncallers must "be aware of the playbooks' existence" is a
  simple but often-overlooked operational detail.

### Claim 5: Automation of incident response elements — common tasks, impact analysis, root cause analysis, and intelligent mitigation suggestions — frees oncallers to focus on problem-solving
- **Evidence**: Explicit statement in the preparation section, enumerating the
  specific automation targets.
- **Confidence**: settled
- **Quote**: "automating elements of incident response will free the oncallers
  to focus on problem solving." / The guide lists "automation of common tasks,"
  automated "analysis of the incident's impact information," "root cause
  analysis," and "intelligent suggestion of mitigating actions."
- **Our assessment**: This is the guide's most directly AI-relevant passage. It
  specifies exactly which incident-response tasks are amenable to automation.
  The list maps cleanly onto the capabilities claimed by incident.io's AI SRE
  (multi-source investigation, impact analysis) and PagerDuty's SRE Agent
  (RCA, mitigation suggestions). The phrase "intelligent suggestion of
  mitigating actions" is notably more conservative than autonomous remediation
  — it implies human decision authority remains, consistent with the Prodcast
  S3E06 "human-in-the-loop" stance (Claim 9).

### Claim 6: Google's IMAG system is based on the Incident Command System (ICS) and centers on the three Cs: coordinate, communicate, and control
- **Evidence**: Named explicitly in the "Respond and Manage Incidents" section.
- **Confidence**: settled
- **Quote**: "Google's incident response system, known as IMAG, is based on the
  Incident Command System (ICS)." / The guide identifies "the 'three Cs' (3Cs)
  of incident management: coordinate, communicate, and control."
- **Our assessment**: This is the canonical written definition of Google's IMAG
  three Cs — and it differs from the Prodcast S1E08's framing ("Command,
  Control, Communications"). The guide's 3Cs (Coordinate, Communicate, Control)
  map to the three IMAG roles (IC, CL, OL) while the Prodcast's 3Cs (Command,
  Control, Communications) describe process functions. This is not a
  contradiction in practice but a different framing altitude — one is
  role-oriented, the other is function-oriented. The guide's framing is the
  more recent and structured treatment; see Cross-References for the full
  discussion.

### Claim 7: IMAG establishes a hierarchical structure with three main roles — Incident Commander (IC), Communications Lead (CL), and Operations Lead (OL) — based on knowledge and incident context, not reporting chains
- **Evidence**: Explicit role definitions in the response section.
- **Confidence**: settled
- **Quote**: "It organizes the incident response by establishing a hierarchical
  structure with clear roles, tasks, and communication channels." / "Incident
  Commander (IC), Communications Lead (CL), and Operations Lead (OL)." / "Roles
  do not follow reporting chains and instead are based on knowledge and incident
  context."
- **Our assessment**: The **Operations Lead (OL)** role is absent from the
  Prodcast S1E08 role set (which has IC, scribe, and communications). The OL
  is the role that focuses on mitigation while IC coordinates and CL handles
  communications. This three-role structure (IC/CL/OL) is more aligned with
  standard ICS than the Prodcast's IC/scribe/communications set — the scribe
  function is subsumed within CL and OL responsibilities. The "roles follow
  knowledge, not reporting chains" principle is critical for the guide's
  incident-command training material: it enables effective cross-team response
  without organizational friction.

### Claim 8: Good incident response is user-centric — communicating consistently and with appropriate detail builds trust and transparency as important as technical mitigations
- **Evidence**: Explicit statement in the response section.
- **Confidence**: settled
- **Quote**: "Communicating consistently and with an appropriate level of detail
  for the reader builds trust and transparency." / "Fixing the problem is only
  part of what's needed" — updating stakeholders about what's affected, severity,
  workarounds, and ETA is equally important.
- **Our assessment**: Establishes the communications dimension as a first-class
  concern alongside technical mitigation. This directly supports the CL role's
  purpose and aligns with the Prodcast S3E06's channel-separation pattern
  (Claim 4: engineering voice bridge vs customer-support Slack channel). For
  AI agents, this means automated stakeholder comms must match the appropriate
  level of detail per audience — not just broadcast raw technical data.

### Claim 9: Google maintains Incident Response Teams (IRTs) that can be activated for major incidents, providing coordination, hands-on assistance, and escalation services
- **Evidence**: Mentioned in the response section as an additional resource for
  major incidents.
- **Confidence**: settled
- **Quote**: "Google maintains various Incident Response Teams (IRTs) that can
  be activated when an incident requires additional support." / Their services
  "may include coordinating multiple team-level efforts, providing hands-on
  assistance," identifying involved teams, gathering resources, assisting
  escalations, activating other IRTs, and "handling broad communications."
- **Our assessment**: This is a brief mention — the canonical IRT operational
  detail is in S6E09 (IRT episode). The guide's value here is confirming IRT as
  a standard Google escalation tier, not a special exception. The guide does not
  describe IRT assembly mechanics, trigger thresholds, or psychological safety
  patterns (those are in S6E09 Claims 1–7).

### Claim 10: Effective incident response requires treating the incident as a project — planning ahead, deciding who needs involvement, documenting actions — because "chaos will naturally prevail unless it is actively managed"
- **Evidence**: Explicit statement at the end of the response section.
- **Confidence**: settled
- **Quote**: "Effective response means treating it as a project in its own
  right." / "Chaos will naturally prevail unless it is actively managed."
- **Our assessment**: A concise, memorable principle. The "treat as a project"
  framing is the operational counterpart to the Prodcast's lifecycle framing
  (S1E08 Claim 1: incident management is a continuous practice). The "chaos
  unless actively managed" line is a quotable artifact for the guide's
  incident-command training material.

### Claim 11: A core SRE tenet is learning from outages and improving systems to prevent recurrence; the most effective tool is open and blameless postmortem writing
- **Evidence**: Opening of the "Remediate and Learn from Incidents" section.
- **Confidence**: settled
- **Quote**: "One core SRE tenet is to learn from outages and improve our
  systems to prevent similar incidents from happening in the future. Where
  prevention is not possible, the goal is to minimize the duration and impact
  of unavoidable/unanticipated outages." / Without this, outages "tend to
  regularly resurface and accumulate over time," increasing toil, consuming
  error budgets, eroding user trust, and impacting revenue. / The most effective
  tool: "open and blameless postmortem writing."
- **Our assessment**: Foundational SRE doctrine, consistent with the Prodcast
  S1E08 lifecycle framing (Claim 10: "do as little incident response as
  possible" via prevention) and the Prodcast S3E06 Claim 14 ("an outage that
  you don't learn from is a failure"). The guide explicitly names the
  consequences of not learning: resurfacing outages, toil accumulation, error
  budget consumption, trust erosion, revenue impact.

### Claim 12: Postmortems must be blameless — everyone involved had good intentions; focus on improving systems, procedures, and training, not blaming individuals
- **Evidence**: Explicit section on postmortem culture.
- **Confidence**: settled
- **Quote**: "One of the core tenets of SRE's culture is that postmortems should
  be blameless." / "It's important to remember that everyone involved in the
  incident had good intentions." / "Blaming individuals for unintended
  consequences during the response, does not aid the learning process."
- **Our assessment**: The canonical blameless postmortem doctrine, stated
  plainly and authoritatively. The "good intentions" framing is the cultural
  foundation that enables honest postmortems — without it, responders hide
  mistakes. This is well-established SRE practice but worth capturing as the
  first-party source for the guide's Ch03 postmortem section.

### Claim 13: Corrective action items from postmortems feed into the team's backlog with agreed SLOs for completion, balanced against feature work based on reliability priorities
- **Evidence**: Explicit process description in the learning section.
- **Confidence**: settled
- **Quote**: "An honest and timely postmortem write-up" shared broadly "is key
  to identifying the most effective corrective action items." / Once SLOs for
  action items are agreed upon, "these feed back into the team's backlog." /
  Teams "balance these action items against feature work."
- **Our assessment**: Concrete operational guidance for postmortem follow-through
  — it's not enough to identify action items; they need completion SLOs, backlog
  entry, and explicit prioritization against feature work. This is more specific
  than the Prodcast S1E08's lifecycle framing, which just notes that recovery
  actions "double as preparation" for the next incident.

### Claim 14: Aggregating structured data across many postmortems in larger organizations enables identification of trends and organizational areas needing larger investments
- **Evidence**: Final paragraph of the learning section.
- **Confidence**: emerging
- **Quote**: "aggregating structured data collected across a large number of
  postmortems to identify trends and organizational areas needing larger
  investments" presents "a great opportunity in a larger organization."
- **Our assessment**: This is the meta-postmortem pattern also described in the
  Prodcast S3E06 Claim 5 (postmortem-driven 80/20 tooling roadmap via
  meta-retrospective). The guide frames it at the organizational investment
  level rather than the tooling-roadmap level. Emerging because it's presented
  as opportunity rather than established practice, but consistent with the
  Prodcast's more concrete method. Worth capturing as the strategic justification
  for postmortem data programs.

## Concrete Artifacts

### IMAG role structure (verbatim from source)

```
Incident Commander (IC):  coordinates the overall incident response.
Communications Lead (CL): provides regular updates to stakeholders and acts as
                           a point of contact for incoming communications.
Operations Lead (OL):     focuses on mitigating the issue and resolving the
                           problem. (Allows the OL to focus while IC and CL
                           handle coordination and communication.)

"Roles do not follow reporting chains and instead are based on knowledge and
incident context."
```
*Source: Google SRE Incident Management Guide, "Respond and Manage Incidents" section.*

### Four attributes of good alerting (verbatim from source)

```
1. Alert in a timely manner: Minimize the user impact prior to incident
   response beginning.
2. Cover all key user facing functionality.
3. Alert based on symptoms, not causes: Alerts should be based on end-to-end
   measures of customer/client experience, not based on a system's internal
   behavior.
4. Be actionable: Alerts that cannot be acted upon by an on-caller generate
   noise.
```
*Source: Google SRE Incident Management Guide, "Prepare for Incidents" section.*

### Incident response automation targets (verbatim from source)

```
The page recommends automating:
- Common tasks
- Analysis of the incident's impact information (severity, scope, affected users)
- Root cause analysis
- Intelligent suggestion of mitigating actions

"automating elements of incident response will free the oncallers to focus on
problem solving."
```
*Source: Google SRE Incident Management Guide, "Prepare for Incidents" section.*

### The three Cs (verbatim from source)

```
"the 'three Cs' (3Cs) of incident management: coordinate, communicate, and
control"
```
*Source: Google SRE Incident Management Guide, "Respond and Manage Incidents" section.*
*Note: This differs from the Prodcast S1E08's framing of "Command, Control, Communications" — see Cross-References.*

### Prevent/learn cycle (verbatim from source)

```
"One core SRE tenet is to learn from outages and improve our systems to prevent
similar incidents from happening in the future. Where prevention is not
possible, the goal is to minimize the duration and impact of
unavoidable/unanticipated outages."

"One of the core tenets of SRE's culture is that postmortems should be
blameless."

"Blaming individuals for unintended consequences during the response, does not
aid the learning process."
```
*Source: Google SRE Incident Management Guide, "Remediate and Learn from Incidents" section.*

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

The following candidates from `miner-related-notes.md` were evaluated:

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.2927) — **Dismissed.** Discusses complexity, sociotechnical systems, and incomplete mental models during incidents. Not directly relevant to the IMAG/3Cs/incident-lifecycle framework this guide defines. No claims to corroborate or contradict.

2. **`docs-google-sre-prodcast.md`** (score 0.2927) — **Dismissed.** This is the Prodcast index note (season/episode listing). It confirms the Prodcast S1E08 exists as the incident-management episode but adds no substantive cross-reference beyond what the individual episode notes provide.

3. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2439) — **Dismissed.** Covers SRE concepts outside Google. The guide is an internal Google process definition; the life-beyond-Google note is about transferability of concepts, not incident management structure.

4. **`docs-google-sre-prodcast-03-05-building-reliable-systems.md`** (score 0.2195) — **Dismissed.** Covers database reliability and managed services. No overlap with incident management framework.

5. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2195) — **Corroborates** at a general level — both sources recommend SLO-based symptom alerting. The guide presents SLO-based alerting as the method to achieve timely, comprehensive, symptom-based alerting (Claim 3); the S5E02 note treats SLOs as a shared communication vernacular (Claim 1) and stresses that SLOs must be "bespoke / artisanally crafted per service" (Claim 2). Together they supply both the **why** (SLOs as reliability language) and the **how** (SLO-based alerting for symptom detection). Not a contradiction — the guide is about alerting mechanics, the S5E02 note is about SLO as communication tool.

6. **`docs-google-sre-reliable-product-launches.md`** (score 0.2195) — **Dismissed.** Covers launch coordination engineering, not incident management. Different lifecycle phase (pre-launch vs incident response).

7. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2195) — **Extends.** The guide's Claim 14 (aggregating postmortems to identify organizational trends) is the strategic-level fram ing of the tooling-roadmap method described in S3E06 Claim 5 (meta-retrospective → 80/20 tooling prioritization). The guide sets the goal (identify investment areas); the Prodcast provides the concrete method (aggregate postmortems, find common factors, focus on the 80%). Also, the guide's automation targets (Claim 5) align with S3E06 Claim 9 (AI as toil-reduction tool for capturing, summarizing, categorizing) — both frame automation as freeing humans for higher-level problem-solving, with human oversight retained.

8. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2195) — **Dismissed.** Covers AI tooling for SRE (early outage detection, ticket analysis). Not relevant to incident management framework definition.

9. **`docs-google-sre-handling-overload.md`** (score 0.1951) — **Dismissed.** Covers load shedding, autoscaling, and thundering herd prevention. Different domain.

10. **`docs-google-sre-prodcast-03-03-treynor-ai-ml.md`** (score 0.1951) — **Dismissed.** Covers production change management and AI/ML. Not directly relevant to incident management framework.

### Primary cross-references (from the Prospector's triage and manual search)

- **Corroborates**:
  - `docs-google-sre-prodcast-01-08-incident-management.md` — This guide and the S1E08 Prodcast cover the same IMAG/incident-management topic in complementary formats (written canonical primer vs conversational podcast). Both describe the lifecycle (the guide's prepare→respond→remediate maps to S1E08's planning→occurrence→response→mitigation→recovery in Claim 3). Both identify alerting/oncall preparation as the prerequisite (Claim 2 here; S1E08 Claim 4). Both affirm blameless postmortem culture (Claim 12 here; S1E08 Claim 8). Both reference IRT as an escalation tier (Claim 9 here; S1E08 notes the "systems-of-systems" responder model as the closest analog in Claim 9). **No claim in this guide contradicts S1E08 substantively** — the 3Cs difference (see below) is a framing shift, not a contradiction.
  - `docs-google-sre-prodcast-06-09-irt-incident-response.md` — The guide's brief IRT mention (Claim 9) is corroborated in detail by S6E09, which describes the IRT engagement model (Claim 1: threshold-based trigger, Claim 2: ~10-minute assembly), psychological safety patterns (Claims 3–6), and adaptive capacity framing (Claim 7). The guide's sentence-level treatment and the Prodcast's deep operational coverage are consistent — the guide confirms IRT as standard Google practice.
  - `blog-pagerduty-production-ai-agent-gaps.md` — Claim 14 (guardrails: "kill switch required from day one"). The guide's conservative framing of automation as "intelligent suggestion of mitigating actions" (Claim 5 here) rather than autonomous remediation is consistent with PagerDuty's guardrail requirement — the guide implicitly retains human decision authority for mitigation actions.

- **Notable differences from (not a contradiction)**:
  - **vs `docs-google-sre-prodcast-01-08-incident-management.md`** — The guide names the three Cs as **"coordinate, communicate, and control"** (Claim 6), while S1E08 names them **"Command, Control, Communications"** (Claim 7). These are different framings of the same IMAG system, at different altitudes: the guide's 3Cs are role-oriented principles (coordinate → IC, communicate → CL, control → OL), while the Prodcast's 3Cs are process functions (Command → decisions, Control → coordination/awareness, Communications → scribe/context). Additionally, the guide introduces an **Operations Lead (OL)** role that is absent from S1E08's role set (IC, scribe, communications). The guide's structure is: IC coordinates, CL communicates, OL controls (mitigates). S1E08's structure is: IC commands (decides), Control coordinates, Communications takes notes. These are complementary framings of the same underlying process, not contradictory — the guide describes the *role* layer, while the Prodcast describes the *function* layer. Both are authoritative Google sources; the guide's framing appears to be a later, structured evolution. No contradiction issue was filed because both describe the same system at different levels of granularity, and the guide does not assert that S1E08's framing is incorrect.

- **Extends**:
  - `docs-google-sre-prodcast-01-08-incident-management.md` — The guide extends S1E08 in three directions: (1) **Alerting doctrine** (Claims 2–3): S1E08 treats alerting as the entry signal; the guide adds the specific SLO-based symptom-alerting recommendation and the four-attribute framework, giving concrete evaluation criteria. (2) **Automation targets** (Claim 5): S1E08 focuses on human process (role structure, lifecycle, hazard/trigger vocabulary); the guide adds explicit automation guidance (common tasks, impact analysis, RCA, mitigation suggestions) that S1E08 lacks. (3) **Action-item follow-through** (Claim 13): S1E08's lifecycle notes that recovery actions "double as preparation" (Claim 3); the guide adds the specific mechanism — SLOs for action items, backlog integration, balance against feature work.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — As noted in the candidate evaluation above: the guide's organizational-trend aggregation (Claim 14) extends S3E06's meta-retrospective tooling method; the guide's automation targets (Claim 5) extend S3E06's toil-reduction framing.
  - `docs-google-sre-prodcast-06-09-irt-incident-response.md` — The guide confirms IRT as a standard escalation tier, which S6E09 extends with full operational mechanics.

- **Novel** (content new to the corpus):
  - **The three Cs as "coordinate, communicate, control"** — a different framing from the existing corpus (which has "Command, Control, Communications" from S1E08). This is not a contradiction but the corpus now has both framings, which is useful for the guide to present as complementary altitude models.
  - **The Operations Lead (OL) role** — absent from the existing IMAG role descriptions in the corpus (S1E08 has IC, scribe, communications). The OL is the role that focuses purely on mitigation while IC coordinates and CL communicates. This fills out the three-role IMAG structure more completely.
  - **The four-attribute alerting framework** — symptom-based, timely, covers all functionality, actionable — as a concrete evaluation rubric for alert quality. The existing corpus has alerting principles from S1E03 (actionable, urgent, push-based) but not this integrated framework.
  - **SLO-based symptom alerting with the resource-quota exception** — the explicit guidance to alert on symptoms with the hard-limit exception is new specificity.
  - **The explicit automation target list** (common tasks, impact analysis, RCA, mitigation suggestions) — the existing corpus has AI capability descriptions (incident.io, PagerDuty) but not the canonical Google-written list of *what* to automate in incident response.
  - **Action-item SLOs with backlog integration** — the concrete process for closing the postmortem loop beyond "do action items."

## Guide Impact

- **Chapter 01 (Incident Response)**: Primary target. This guide should serve as the canonical process backbone for the chapter's incident-response section. Add: (a) the end-to-end lifecycle framing (prepare → respond → remediate, Claim 1), (b) the IMAG role structure with the three Cs (Claim 6) and the IC/CL/OL role definitions (Claim 7) — **note the 3Cs are "coordinate, communicate, control" here vs "Command, Control, Communications" in the S1E08 source; present both framings as complementary** (role-oriented vs function-oriented), (c) the Operations Lead role (Claim 7) as the missing role from the current corpus-based role set, (d) the "treat as a project" and "chaos unless managed" principles (Claim 10), (e) the IRT escalation tier (Claim 9) linking to the detailed S6E09 extraction. The chapter currently leans on AI-specific sources (incident.io, PagerDuty) for incident-process descriptions — this guide supplies the authoritative human baseline.

- **Chapter 02 (SLOs and Monitoring)**: Add the four-attribute alerting framework (Claim 2) and SLO-based symptom alerting doctrine with the resource-quota exception (Claim 3) as the canonical alerting-evaluation rubric. The existing Ch02 material cites Prodcast S1E03 on alerting principles; this guide adds the framework structure and the SLO-based alerting recommendation.

- **Chapter 03 (Runbooks and Agents) / Chapter 05 (AI-assisted SRE)**: Use the automation target list (Claim 5) — common tasks, impact analysis, RCA, mitigation suggestions — as the canonical human-side catalog of what incident-response automation should address. The "intelligent suggestion" framing (rather than autonomous action) supports the human-in-the-loop / "AI-assisted, not autonomous (yet)" stance that recurs across the corpus (Prodcast S3E06 Claim 9, PagerDuty gaps Claim 14).

- **Chapter 04 (On-call and Toil)**: Add: (a) the oncall-readiness requirements (playbooks, playbook awareness, Wheel of Misfortune exercises, Claim 4), (b) the postmortem-action-item lifecycle (SLOs for actions, backlog integration, balance against features, Claim 13), (c) the meta-postmortem trend aggregation as organizational-level toil reduction (Claim 14), (d) the blameless postmortem doctrine with the "good intentions" framing (Claim 12).

## Extraction Notes

- The source is a single public page on sre.google
  (https://sre.google/resources/practices-and-processes/incident-management-guide/).
  The page is a concise primer (~2,000 words across four sections). No sub-pages
  were followed per MINER.md §1 — the page is self-contained and the "Further
  Reading" links (SRE Book Chapter 9, ProdEx video, Lowe's case study, etc.)
  are supplementary references already covered by existing corpus notes or
  outside the scope of this extraction (SRE Book Chapter 9 is referenced by the
  SRE Workbook crawl seed; ProdEx is a video; Lowe's case study is a separate
  Google Cloud blog).

- The page carries no structured publication date. The SRE Prodcast S1E08
  (covering the same topic in conversation form) is estimated 2022. The guide
  references IMAG and IRT (also covered in S6E09, 2026) and is published on the
  current sre.google site. The author list includes Steve McGhee and Vrai
  Stacey, both active in 2024–2026 Prodcast episodes. `date_published` is set
  to "undated (page on sre.google; references SRE Workbook and IMAG,
  contemporaneous with SRE Prodcast S1E08 / 2022–2026 range)" — this should be
  refined if an exact publication date is discovered.

- All `Quote` field passages are copied character-for-character from two
  independent WebFetch extractions of the same URL, verified for consistency.
  Short quotes (≤125 characters per the fetch proxy) are exact. Longer
  descriptive text in Concrete Artifacts is attributed with section references
  so the Assayer can spot-check against the live URL.

- No part of the source was paywalled. The page also provides a PDF download
  link which was not fetched — the HTML version was complete and sufficient.

- `confidence_overall` is `settled`: the dominant claims (alerting principles,
  IMAG/3Cs/role structure, lifecycle, blameless postmortems) are authoritative,
  first-party Google SRE doctrine established over decades. The only element
  flagged `emerging` is Claim 14 (meta-postmortem trend aggregation as
  organizational opportunity), which is presented as aspirational guidance
  rather than established practice.

- No contradiction issue was filed. The guide and the Prodcast S1E08 use
  different framings for the three Cs (Coordinate/Communicate/Control vs
  Command/Control/Communications) and the guide introduces the OL role, but
  these are complementary framings of the same IMAG system at different
  altitudes (role-oriented vs function-oriented), not contradictory claims.
  The guide does not assert that the Prodcast's framing is incorrect, and both
  are authoritative Google sources. The difference is captured prominently in
  Cross-References and Guide Impact for the Smith and the guide editor to
  reconcile when synthesizing.
