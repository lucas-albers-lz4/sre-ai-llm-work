---
source_url: https://sre.google/static/pdf/Anatomy_Of_An_Incident.epub
source_type: documentation
title: "Anatomy of an Incident — Google's Approach to Incident Management for Production Services"
author: "Ayelet Sachto & Adrienne Walcer, with Jessie Yang (Google SRE)"
date_published: 2022-01-20
date_extracted: 2026-07-27
last_checked: 2026-07-27
status: current
confidence_overall: settled
issue: "#589"
---

# Anatomy of an Incident — Google's Approach to Incident Management for Production Services

> Full-length Google SRE incident management book (O'Reilly, January 2022) by two Google SRE practitioners. Covers the incident lifecycle end-to-end — preparedness, response, mitigation/recovery, and postmortems — with the IMAG/ICS role structure, the hazard/trigger vocabulary, severity classification, and a detailed real-world case study (the "Mayan Apocalypse" network automation outage). **Heavy overlap with existing corpus** — the same IMAG framework, lifecycle model, responder topology, and blameless-postmortem culture are already extracted from the SRE Prodcast S1E08 (featuring same author Walcer) and the canonical written IMAG Guide. Novel elements include: Google's four-tier severity classification with litmus tests, the N+2 capacity principle, the "generic mitigations" concept, the Venn-diagram systems-analysis model, and the full Mayan Apocalypse case-study narrative. Published January 2022 — predates the December 2025 recency cutoff. Recorded here for completeness; the Assayer should evaluate whether this adds sufficient new material beyond the existing extracted corpus.

## Source Context

- **Type**: documentation (ebook) — full-length O'Reilly report (~60 pages), published on sre.google as a free EPUB download.
- **Author credibility**: Ayelet Sachto is a Google SRE on the GKE SRE team with 17 years of experience; Adrienne Walcer is a Technical Program Manager in Google SRE, program lead for Incident Management at Google, and the same author featured in Prodcast S1E08 (extracted as `docs-google-sre-prodcast-01-08-incident-management.md`). Both are primary-source Google SRE practitioners. Jessie Yang contributed as a writer/editor. Published on the official sre.google domain under O'Reilly Media.
- **Scope**: Covers the full incident management lifecycle: what constitutes an incident (Ch1), preparedness/disaster testing (Ch2), scaling incident management with component/SoS responders and IMAG structure (Ch3), mitigation and recovery (Ch4), postmortems and psychological safety (Ch5), a real-world case study (Ch6), and conclusions (Ch7). Does **not** contain AI/LLM content, code examples, configs, or quantitative benchmarks — it is a process-focused guide. Published in January 2022, predating the guide's December 2025 recency cutoff. The IMAG/incident-management content substantially overlaps with `docs-google-sre-prodcast-01-08-incident-management.md` (same author Walcer, conversational depth) and `docs-google-sre-incident-management-guide.md` (canonical written primer).

## Extracted Claims

### Claim 1: Incidents are defined by three criteria — escalated (too big for one person), immediate response required, and organized response required — which distinguishes them from alerts or tickets
- **Evidence**: Explicit definition in Chapter 1, distinguishing Google's incident definition from ITIL's broader definition.
- **Confidence**: settled
- **Quote**: "At Google, incidents are issues that: Are escalated (because they're too big to handle alone), Require an immediate response, Require an organized response."
- **Our assessment**: A more specific, operational definition than the IMAG Guide's "issues that have been escalated and require immediate, continuous, organized response" (S1E08 Claim 5). The three-criteria framing is a useful checklist for teams deciding whether to declare an incident. Consistent with the existing corpus.

### Claim 2: Monitoring alert outputs should be classified into three tiers — pages (immediate human action), alerts (action within hours), and metrics/logs (pull mode for analysis)
- **Evidence**: Explicit three-tier classification in Chapter 1 with action-timeframe mapping.
- **Confidence**: settled
- **Quote**: "If an immediate (human) action is necessary, you should send a page. If a human action is required in the next several hours, you should send an alert. If no action is needed — that is, the information is needed in pull mode, such as for analysis or troubleshooting — the information remains in the form of metrics or logs."
- **Our assessment**: A concrete actionability taxonomy more granular than the IMAG Guide's four-attribute alerting framework (timely, covers all functionality, symptom-based, actionable). The three-tier classification (page vs alert vs metric) maps directly to incident-decision workflows. The existing alerting note (S1E03) discusses actionable alerts and push vs pull but not this specific three-tier schema.

### Claim 3: Declaring an incident should be encouraged and rewarded — it is always better to declare and close than to open retroactively; measuring incident counts creates perverse incentives
- **Evidence**: Explicit guidance in Chapter 1 warning against measuring incident counts as a reliability metric.
- **Confidence**: settled
- **Quote**: "it's better to declare an incident and close it afterward than to open an incident retroactively." — and — "If you focus on the latter [measuring the number of declared incidents], people will hesitate to declare an incident for fear of being penalized. This can lead to late incident declarations."
- **Our assessment**: A concrete organizational anti-pattern warning. The existing corpus has the IMAG lifecycle but not this specific "measure reliability, not incident counts" framing. Relevant to Ch04 (on-call culture): measuring incident counts as a KPI is counterproductive.

### Claim 4: Once a human is involved in outage response, the outage will last at least 20 to 30 minutes — automation and self-healing are the primary levers to reduce this floor
- **Evidence**: Explicit heuristic stated in Chapter 4's "Calculating the Impact of Incidents" section.
- **Confidence**: settled (stated as a Google finding)
- **Quote**: "At Google, we found that once a human is involved, the outage will last at least 20 to 30 minutes."
- **Our assessment**: A striking operational heuristic — establishes a lower bound on human-involved TTR that automation aims to beat. This is the strongest quantitative argument for AI-assisted / automated incident response in the entire book. It quantifies the "human-expensive" claim from S1E08 Claim 10. This is new to the corpus.

### Claim 5: Generic mitigations (roll back, drain traffic, add capacity) should be the first action on impact — fix symptoms, not causes, to buy time
- **Evidence**: Chapter 4 defines "generic mitigations" as pre-prepared Band-Aids that stop or lessen user impact without requiring full understanding of the outage. Uses the roof-leak bucket metaphor.
- **Confidence**: settled
- **Quote**: "A generic mitigation is an action that you can take to reduce the impact of a wide variety of outages while you're figuring out what needs to be fixed." — and — "Your first priority should always be to stop or lessen the user impact, not to figure out what's causing the issue." — and — "These mitigations fix the symptoms of the outage rather than the causes."
- **Our assessment**: This concept is implicit in S1E08 Claim 4 ("determine user impact, apply Band-Aid") but the book provides the named framework ("generic mitigations"), the specific building blocks (rollback, drain traffic, add capacity), and the "symptoms not causes" rationale explicitly. This is a more complete treatment suitable for the guide's response-playbook material.

### Claim 6: Google uses four-tier severity classification for incidents — Huge, Major, Medium, and Minor (plus Negligible/Test) — each with a defined litmus test and brand/business impact criterion
- **Evidence**: Table 3-1 in Chapter 3 provides severity definitions with explicit litmus tests.
- **Confidence**: settled
- **Quote**: "Huge — A major user-facing outage that generates bad press OR that results in a massive impact on revenue for Google or identified customers. [...] Major — An outage that is visible to users but does not cause lasting damage to Google services or identified customers, OR a sizable loss in revenue for Google or its customers, OR 50% or more of Googlers significantly impacted. [...] Medium — Anywhere from a near miss to a huge/major outage. [...] Minor — External users may not have even noticed the outage. [...] Negligible, Trivial — The incident was not visible to users in any way and had little to no real impact on production, but valuable lessons were learned."
- **Our assessment**: This is a concrete severity-classification schema — new to the corpus. The existing notes (IMAG Guide, S1E08) mention incident severity in passing but do not provide Google's specific four-tier framework with litmus tests. The litmus test column linking each tier to brand/business risk is particularly useful for the guide's incident-grading material. The "Test, False alarm" category (named in the table) is also notable — it normalizes non-incidents as learning data, not noise.

### Claim 7: An incident should remain open with active incident management for no more than three days — beyond that, close the incident and move to long-term recovery work
- **Evidence**: Explicit recommendation in Chapter 3's "Managing Risk" section.
- **Confidence**: settled
- **Quote**: "The time from identifying to resolving an incident should be no more than three days." — and — "If you expect to spend that much time in fight-or-flight mode, it's natural to expect that this situation will eventually lead to continuous turnover on your team." — and — "Close your incident; move on to recovery."
- **Our assessment**: A concrete time-bound for incident duration that operationalizes the "do as little incident response as possible" principle (S1E08 Claim 10). The three-day maximum is new to the corpus. The fight-or-flight / cortisol / burnout framing provides the physiological justification for capping incident duration.

### Claim 8: The incident management lifecycle stages are preparedness → response → mitigation and recovery, and recovery actions circle back to preparedness — at scale, all phases may occur simultaneously
- **Evidence**: Chapter 1 section explicitly titled "The Incident Management Lifecycle" with a diagram.
- **Confidence**: settled
- **Quote**: "The process of dealing with such risks is called the incident management lifecycle. The incident management lifecycle encompasses all of the necessary activities to prepare for, respond to, recover from, and mitigate incidents. This is an ongoing cost of an operational service." — and — "Depending on the size of your stack, it's possible that all of these phases occur simultaneously."
- **Our assessment**: Consistent with S1E08 Claim 3 (plan/preparation → occurrence → response → mitigation → recovery). The book adds the explicit point that at large scale, phases can overlap simultaneously — a nuance not present in S1E08's linear presentation.

### Claim 9: Root cause and trigger work together to create an incident — the root cause is a system hazard (vulnerability), the trigger is the environmental shift; neither maps one-to-one to incident types
- **Evidence**: Chapter 5's "Root Cause Versus Trigger" section with multiple examples (house fire, ant infestation, OOM).
- **Confidence**: settled
- **Quote**: "Root cause(s) — The system hazards, or how the system was vulnerable. A hazard can exist in a system for an indefinite period of time — the system environment needs to shift somehow to turn that hazard into an outage." — and — "Trigger(s) — The circumstances that allowed the root cause(s) to turn into an incident." — and — "There isn't a one-to-one mapping of which root causes and triggers cause which types of incidents — complexity makes a whole range of outcomes possible."
- **Our assessment**: This expands S1E08 Claim 2 with the explicit "no one-to-one mapping" insight — acknowledging that complexity produces non-deterministic outcomes from the same root cause/trigger pair. The three worked examples (house fire, ant infestation, OOM) are concrete teaching tools. The OOM example is particularly illustrative for SRE: "the root cause might have been put in place years before the trigger conditions existed."

### Claim 10: Effective systems analysis after incidents maximizes the intersection of three circles — what you think the problem is × what it actually is × what you can fix (Venn diagram model)
- **Evidence**: Chapter 5's "Systems Analysis for Organizational Improvement" section, illustrated with a three-circle Venn diagram and worked analysis.
- **Confidence**: emerging (presented as analytic framework, not Google-wide process)
- **Quote**: "The overlap of 'What you THINK the problem is' and 'What you can fix' [...] is dangerous: these are solutions that you think will help in the long term but actually won't address the real issues." — and — "The key is to invest enough in systems analysis that you and your team can achieve a high probability of selecting the best possible engineering projects to improve system resilience. But there is a point of diminishing returns."
- **Our assessment**: A novel conceptual framework for post-incident analysis not present in the existing corpus. The three-circle model provides a structured way to think about postmortem depth — go deep enough to find the real problems, but not so deep that analysis paralysis sets in. The "danger zone" (what you think × what you can fix, minus what the problem actually is) is a memorable warning against solving the wrong problem. This is the book's most original contribution to the postmortem-analysis literature.

### Claim 11: N+2 resources is the minimum principle for achieving reliability in distributed systems — N for peak capacity, +2 for one unexpected failure and one planned upgrade
- **Evidence**: Explicit recommendation in Chapter 4's "Design with reliability in mind" section.
- **Confidence**: settled
- **Quote**: "Having N+2 resources is a minimum principle for achieving reliability in a distributed system. N+2 means you have N capacity to serve the requests at peak, and +2 instances to allow for one instance (of the complete system) to be unavailable due to unexpected failure and another instance to be unavailable due to planned upgrades."
- **Our assessment**: Concrete architectural guidance new to the corpus. The existing notes have capacity planning and redundancy concepts but not this specific N+2 framing with the explicit distinction between unexpected failure and planned upgrade. Useful for the guide's reliability-design material.

### Claim 12: The "Mayan Apocalypse" case study (June 2, 2019) demonstrates the full IMAG/IRT/component-responder architecture in action — a network automation mis-flag cascaded into a multi-region outage affecting half the globe
- **Evidence**: Chapter 6 provides a detailed 5-page narrative of a real Google outage involving Maya (network automation tool), component responders, Tech IRT escalation, IC role assumption, and post-incident learning.
- **Confidence**: settled (attributed to a real, well-documented Google outage — confirmed by public Google Cloud incident reports from June 2019)
- **Quote**: "For Google, the Mayan Apocalypse was not some New Age phenomenon that led to failure during the year 2012. Rather, the Mayan Apocalypse happened June 2, 2019, with a network automation tool named Maya." — and — "One hour into the outage, one component responder noted that the system-of-systems issues impacting our infrastructure were too pervasive, and coordinated communications surrounding the incident were turning into chaos and discord. At this point, more than 40 teammates had joined the incident response communication channel."
- **Our assessment**: A detailed, publishable case study illustrating all the concepts from earlier chapters. Key operational details: (1) the mis-flag in Maya's traffic-direction logic existed before the planned maintenance that triggered it; (2) more than 40 responders joined the channel before IRT was paged; (3) the IC had no prior experience with the affected networking component but used IRT training to subvert the degraded-internal-traffic flagging; (4) post-incident, the networking team restructured Maya to prevent the failure mode. This is the single largest novel artifact in the book, though the concepts it illustrates are already extracted.

## Concrete Artifacts

### Severity classification table (verbatim from source)

```
Severity    Definition                                         Litmus Test
Huge        A major user-facing outage that generates bad      Could or did damage the
            press OR that results in a massive impact on       Alphabet/Google brand and
            revenue for Google or identified customers.        business.
Major       An outage that is visible to users but does not    Recurring, unmitigated future
            cause lasting damage to Google services or         incidents of this nature could
            identified customers, OR a sizable loss in         or will damage the
            revenue for Google or its customers, OR 50% or     Alphabet/Google brand and
            more of Googlers significantly impacted.           business.
Medium      Anywhere from a near miss to a huge/major          Recurring, unmitigated future
            outage. A significant number of internal users     incidents of this nature will
            are significantly impacted. Workarounds existed    likely lead to increasing
            and were known to users (mitigating the impact).   instability over time and
                                                               greater costs in production
                                                               maintenance.
Minor       External users may not have even noticed the       Recurring, unmitigated future
            outage. Internal users were inconvenienced.        incidents of this nature are
            The result was unexpected sloshing of traffic      unlikely to lead to increasing
            between entities (network, data center,            instability over time but
            instances).                                        represent normal operating
                                                               conditions.
Negligible, The incident was not visible to users in any way   Recurring, unmitigated future
Trivial     and had little to no real impact on production,    incidents of this nature would
            but valuable lessons were learned and some         not be considered a process
            follow-up action items may need to be tracked      breakdown.
            at a low priority.
Test,       This wasn't even an incident. Go do a new thing.   (none)
False alarm
```
*Source: Table 3-1, "Anatomy of an Incident," Chapter 3, page 22.*

### Incident impact metrics equation (verbatim from source)

```
Impact = (TTD + TTR) × Frequency

Time to detect (TTD):   time from outage occurrence to human notification/alerting
Time to repair (TTR):   time from alert to mitigation (not code fix)
Time between failures:  time from incident start to next same-type incident start

"At Google, we found that once a human is involved, the outage will last at least
20 to 30 minutes. In general, automation and self-healing systems are a great
strategy, since both help reduce the time to detect and time to repair."
```
*Source: "Anatomy of an Incident," Chapter 4, pages 28–29.*

### Generic mitigations building blocks (verbatim from source)

```
"Some of the basic building blocks are the ability to:
- Roll back a binary
- Drain or relocate traffic
- Add capacity

These Band-Aids are intended to buy you and your service time so that you can
figure out a meaningful fix which can fully resolve the underlying issues. In
other words, they fix the symptoms of the outage rather than the causes."
```
*Source: "Anatomy of an Incident," Chapter 4, page 25.*

### The Venn diagram model for post-incident systems analysis (paraphrased from source)

```
Three circles:
1. What you THINK the problem is (your understanding during the incident)
2. What the problem actually is (the real system state)
3. What you can fix (system elements under your control)

The goal is to maximize the intersection (1 ∩ 2 ∩ 3) — your best work.
The danger zone is (1 ∩ 3) - (2) — solutions you think will help but don't
address the real issues.
Circle 2 (truth) and Circle 3 (fixable) are unmovable — only Circle 1
(your understanding) can expand through deeper systems analysis.
```
*Source: "Anatomy of an Incident," Chapter 5, pages 47–50 (Figures 5-2 through 5-5).*

### Root cause and trigger examples (verbatim from source)

```
House fire:
  Root cause: A gas leak
  Trigger: A sparking electrical plug near the leaky stove
  Incident: A house fire

Ant infestation:
  Root cause: A warm season comfortable for bugs
  Trigger: Sloppy eating habits leaving crumbs around
  Incident: An ant infestation

Out of Memory (OOM):
  Root cause: A config file change that introduces a memory leak
  Trigger: A surprisingly high volume of requests
  Incident: OOM
```
*Source: "Anatomy of an Incident," Chapter 5, page 51 (three worked examples).*

### N+2 capacity principle (verbatim from source)

```
"Having N+2 resources is a minimum principle for achieving reliability in a
distributed system. N+2 means you have N capacity to serve the requests at peak,
and +2 instances to allow for one instance (of the complete system) to be
unavailable due to unexpected failure and another instance to be unavailable
due to planned upgrades."
```
*Source: "Anatomy of an Incident," Chapter 4, page 36.*

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

The following candidates from `miner-related-notes.md` were evaluated:

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3000) — **Dismissed.** Discusses complexity theory and sociotechnical systems — the ebook touches on complexity (Claim 9's "no one-to-one mapping" between root cause/trigger and incident types) but does not engage deeply enough to substantiate a cross-reference. The ebook's complexity acknowledgment is one sentence; the Prodcast episode is a full treatment. No claims to corroborate or contradict.

2. **`docs-google-sre-prodcast.md`** (score 0.2500) — **Dismissed.** The Prodcast index note confirms Season 1 Episode 8 features Adrienne Walcer (same author) but adds no substantive cross-reference beyond what the S1E08 extraction provides.

3. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2250) — **Dismissed.** The ebook covers incident management process, not tooling. The Prodcast episode covers tools, meta-retrospectives, and channel separation — none of which the ebook addresses.

4. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2250) — **Dismissed.** Covers SRE concepts outside Google. The ebook describes Google-internal practice. No overlap.

5. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2250) — **Dismissed.** AI for SRE. The ebook has zero AI/LLM content.

6. **`docs-google-sre-prodcast-03-05-building-reliable-systems.md`** (score 0.2000) — **Dismissed.** Database reliability. The ebook's N+2 principle and design-for-reliability material (Claim 11) is general architectural guidance, not database-specific. No specific claims to corroborate.

7. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2000) — **Dismissed.** The ebook mentions SLOs/SLIs once at a primer level (Chapter 4) — the dedicated SLO Prodcast episode is far more comprehensive. The ebook adds nothing to the existing SLO corpus.

8. **`docs-google-sre-reliable-product-launches.md`** (score 0.2000) — **Dismissed.** Launch coordination, not incident management.

9. **`docs-google-sre-prodcast-04-09-ai-agents.md`** (score 0.2000) — **Dismissed.** AI agents. The ebook has zero AI/LLM content.

10. **`docs-google-sre-handling-overload.md`** (score 0.2000) — **Dismissed.** Load shedding and capacity management. The ebook's generic-mitigations material (drain traffic, add capacity) touches on the same operational actions but at a conceptual level, not the detailed technical treatment of the Handling Overload note. No claims to corroborate or contradict.

### Primary cross-references

- **Corroborates**:
  - `docs-google-sre-prodcast-01-08-incident-management.md` — This ebook and S1E08 share Adrienne Walcer as author/guest and cover the same IMAG framework. Directly corroborates Claims 2 (hazard/trigger distinction = Claim 9 here), Claim 3 (lifecycle phases = Claim 8 here), Claim 4 (user-impact-first/Band-Aid = Claim 5 here), Claim 5 (IMAG = IMAG naming and role structure), Claim 9 (component/SoS responder types = described in Ch3), and Claim 10 (prevention-first = Claim 7 and Ch7 conclusion here). The ebook is the full book-length treatment; S1E08 is the conversational summary. No contradictions.
  - `docs-google-sre-incident-management-guide.md` — Corroborates Claim 1 (alerting principles — the IMAG Guide's four-attribute alerting framework and the ebook's three-tier page/alert/metrics classification are complementary, not contradictory), Claim 6 (IMAG/3Cs/IC/CL/OL role structure — the ebook describes the same IMAG framework as the Guide though at less structured depth), Claim 11–12 (blameless postmortem culture). The ebook adds severity classification (Table 3-1) which the Guide lacks.
  - `docs-google-sre-prodcast-06-09-irt-incident-response.md` — The ebook's Mayan Apocalypse case study (Claim 12 here) illustrates the IRT engagement model described in S6E09 Claims 1–2 (threshold-based trigger, ~10-minute assembly, video-conference coordination, IC authority regardless of hierarchy). The case study provides a concrete narrative of Tech IRT activation that corroborates S6E09's operational description.

- **Contradicts**: None identified. The ebook is fully consistent with the existing IMAG/incident-management corpus — it describes the same Google SRE process at greater length but does not introduce any conflicting claims. No contradiction issue filed.

- **Extends**:
  - `docs-google-sre-prodcast-01-08-incident-management.md` — The ebook extends S1E08 in several dimensions: (1) **Severity classification** (Claim 6 here) — S1E08 does not provide Google's severity scale; the ebook's Table 3-1 adds the four-tier Huge/Major/Medium/Minor framework with litmus tests. (2) **Generic mitigations** (Claim 5 here) — S1E08's "Band-Aid" concept is extended with named building blocks (rollback, drain traffic, add capacity) and the "symptoms not causes" rationale. (3) **TTD/TTR/TBF metrics equation** and the **"20-30 minute human involvement" heuristic** (Claim 4 here) — S1E08 describes the impact measurement concept in passing; the ebook quantifies it. (4) **Root cause/trigger examples** — S1E08 has the gas-leak metaphor; the ebook adds three worked examples (house fire, ant infestation, OOM) with the "no one-to-one mapping" insight.
  - `docs-google-sre-incident-management-guide.md` — Extends the Guide with: (1) the severity classification schema (Table 3-1), (2) the detailed Mayan Apocalypse case study (Claim 12 here), (3) the three-tier alert classification (Claim 2 here) as a complement to the Guide's four-attribute framework, (4) the N+2 capacity principle (Claim 11 here).
  - `docs-google-sre-prodcast-06-09-irt-incident-response.md` — The ebook's Mayan Apocalypse narrative (Claim 12 here) extends S6E09's IRT engagement description with a full timeline-driven case study of IRT activation, IC handoff, and post-incident learning.

- **Novel** (content new to the corpus):
  - **The four-tier severity classification with litmus tests** (Table 3-1) — including the explicit brand/business-risk litmus for each tier and the "Test, False alarm" category. The existing corpus has incident-severity mentions (S1E08, IMAG Guide) but no classification schema with decision criteria.
  - **The "20-30 minute human floor" heuristic** (Claim 4) — "once a human is involved, the outage will last at least 20 to 30 minutes." This quantified assertion is new to the corpus.
  - **The three-tier alert classification** (Claim 2) — page (immediate), alert (hours), metrics/logs (pull mode). More granular than the existing S1E03 and IMAG Guide alerting material.
  - **The Venn diagram systems-analysis model** (Claim 10) — what you think × what it is × what you can fix. A novel conceptual framework for post-incident analysis depth.
  - **N+2 capacity principle** (Claim 11) — explicit N+2 minimum with the dual-failure allowance (unexpected failure + planned upgrade).
  - **The Mayan Apocalypse case study** (Claim 12 / Concrete Artifacts) — a detailed 5-page real-world outage narrative illustrating the full IMAG/IRT response architecture. The concepts are extracted; the specific narrative is new.
  - **The three-day incident duration cap** (Claim 7) — "time from identifying to resolving an incident should be no more than three days."
  - **The generic mitigations framework** (Claim 5) — named concept with specific building blocks and the "symptoms not causes" rationale, building on the simpler "Band-Aid" in S1E08.

## Guide Impact

- **Chapter 01 (Incident Response)**: Limited impact — the lifecycle model, IMAG framework, IC/CL/OL roles, and incident definition are already captured from S1E08 and the IMAG Guide. Two additions: (a) the three-tier alert classification (Claim 2) as a complement to the IMAG Guide's four-attribute framework, (b) the three-criteria incident definition (Claim 1) as a concrete checklist for incident declaration decisions. The severity classification (Claim 6 / Table 3-1) could replace or supplement the current severity-grading material if the chapter has any.

- **Chapter 04 (On-call and Toil)**: Add: (a) the "20-30 minute human floor" heuristic (Claim 4) as the quantitative argument for automation — every incident involving a human has a ~25-minute floor on TTR regardless of skill; (b) the three-day incident duration cap (Claim 7) as a burnout-prevention policy — if you're managing an incident for more than three days, close it and switch to recovery project work; (c) the "measure reliability, not incident counts" anti-pattern (Claim 3) as an organizational metric warning.

- **Chapter 03 (Postmortems and Learning)**: Add: (a) the Venn diagram systems-analysis model (Claim 10) as a framework for postmortem analysis depth — "deep enough to find the real problem, not so deep that analysis costs exceed incident costs"; (b) the root cause/trigger worked examples (Claim 9 / Concrete Artifacts) as teaching tools for postmortem training.

- **Chapter 05 (AI-assisted SRE)**: The "20-30 minute human floor" (Claim 4) is the strongest single quantitative justification for AI-assisted incident response in the entire corpus — it defines the ceiling AI agents aim to beat. Worth citing as the "why automate" framing.

- **Overall assessment**: The ebook adds several novel concrete artifacts (severity table, N+2 principle, Venn model, three-tier alerting, the Mayan Apocalypse narrative) and one powerful quantitative heuristic (the human floor). However, the process framework (lifecycle, IMAG, responder types, postmortem culture) is already extracted from higher-credibility, more date-appropriate sources (the IMAG Guide is undated but on the current sre.google site; S1E08 covers the same material in a more accessible format with the same author). The Assayer should weigh whether the novel elements justify updating the guide over and above the existing source notes.

## Extraction Notes

- The source URL (`https://sre.google/static/pdf/Anatomy_Of_An_Incident.epub`) is an EPUB ebook file, not a web page. It was downloaded (3.6 MB), unzipped, and read as raw XHTML text across 61 split files. The EPUB was produced by calibre (5.37.0) from the O'Reilly source. All quotes are copied character-for-character from the extracted XHTML text.

- **Publication date concern**: The EPUB metadata (`content.opf`) records `dc:date` as `2022-01-20T21:16:37+00:00` and the copyright page states "January 2022: First Edition." This predates the guide's December 2025 recency cutoff by approximately four years. The content is classic Google SRE incident management — a topic that is largely evergreen — but the source contains zero AI/LLM content, AI-generated patterns, or references to post-2022 tooling/process changes. The Assayer should evaluate whether a January 2022 source on a well-covered topic warrants integration into a guide focused on SRE AI/LLM practices. See the Prospector's triage comments for the full recency-cutoff analysis.

- **Heavy content overlap**: The IMAG framework, lifecycle model, responder topology, hazard/trigger vocabulary, 3Cs, IC/CL/OL roles, and blameless-postmortem culture in this ebook are already extracted from:
  - `docs-google-sre-prodcast-01-08-incident-management.md` (same author, conversational depth)
  - `docs-google-sre-incident-management-guide.md` (canonical written primer)
  This extraction focuses on what is novel or notably more detailed than the existing corpus. The claims above intentionally omit the well-covered overlap material (lifecycle phases, IMAG structure, responder types, postmortem culture) and instead emphasize the new artifacts and assertions.

- The ebook contains figures and diagrams (severity table, lifecycle diagram, outage-lifecycle diagram, organizational-architecture pyramid, Venn diagrams) which are described in the text but could not be directly extracted as images. The severity table (Table 3-1) and Venn diagram model are faithfully reproduced from the text descriptions.

- No contradiction issue was filed. The ebook is fully consistent with the existing IMAG/incident-management corpus — same framework, same Google SRE source, same authors (Walcer). The ebook provides more detail but does not introduce any conflicting claims.

- `confidence_overall` is `settled` for the dominant claims (severity classification, generic mitigations, root cause/trigger analysis, N+2 principle) — these are authoritative first-party Google SRE doctrine. Claim 10 (Venn diagram model) is flagged `emerging` because it is presented as an analytic framework rather than established Google-wide practice.
