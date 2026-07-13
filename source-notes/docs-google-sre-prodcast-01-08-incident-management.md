---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-01-08/
source_type: discussion
title: "Incident management process with Adrienne Walcer (SRE Prodcast S1E08)"
author: Adrienne Walcer (Google SRE, program lead for Incident Management); hosts Viv & MP
date_published: 2022 (estimated; SRE Prodcast Season 1, Episode 8 — page has no structured publish date)
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: settled
issue: "#41"
---

# Incident management process with Adrienne Walcer (SRE Prodcast S1E08)

> Authoritative Google-side description of the human incident-management lifecycle, the
> hazard/trigger vocabulary, the three C's (Command/Control/Communications), and the IMAG
> role structure — the human baseline that AI incident-response agents are built to automate.

## Source Context

- **Type**: discussion (podcast transcript) — SRE Prodcast Season 1, Episode 8, hosted by Viv and MP, guest Adrienne Walcer.
- **Author credibility**: Adrienne Walcer is a Technical Program Manager in Google SRE and the **program lead for Incident Management at Google**; author of *Anatomy of an Incident* (O'Reilly). This is a primary-source account of the process she owns, not a secondary summary. The page is published on the official sre.google domain.
- **Scope**: How to organize and manage incidents throughout the *production lifecycle* — from engineering-time root-cause insertion, through detection/response/mitigation/recovery, to post-incident learning. Covers role structure (IMAG), responder types, accountability, and the "three C's." It does **not** contain AI/LLM content, code, configs, metrics, or failure-data — it is general SRE incident-management practice in conversational form.
- **Note on AI relevance**: This source has zero AI/LLM content. Every connection drawn below to AI-assisted incident response (incident.io, PagerDuty agent notes) is the Miner's analytical synthesis, clearly marked, not a claim from the source.

## Extracted Claims

### Claim 1: Incident management is a continuous lifecycle practice, not a single point-in-time event
- **Evidence**: Walcer contrasts two "schools of thought" and states her firm belief in the second; she says you manage the incident from the moment the root cause is written into the stack.
- **Confidence**: settled
- **Quote**: "I've noticed that there are two primary schools of thought around incident management. The first school of thought is that you manage an incident and then it's over; you move on. ... The second school of thought is that incident management is a practice that you do every single day with every single piece of engineering that you touch. Incident management is a continuous cycle that will exist throughout the lifecycle of your system." — and — "I am a firm believer in number two. So even though your pager is going off at one moment, I believe pretty firmly that you are managing the incident from the second that you wrote the root cause into your technical stack."
- **Our assessment**: Settled, authoritative, and the spine of the whole episode. Directly useful as the framing for Ch01: incident response is a lifecycle owned from engineering time, not a pager-triggered afterthought.

### Claim 2: Hazards and triggers are distinct — a hazard is a latent vulnerability; a trigger is the environmental shift that turns it into an incident (root cause ≈ hazard)
- **Evidence**: Walcer borrows systems-engineering vocabulary; uses the gas-leak metaphor (gas leak persists; an electrical switch is the trigger).
- **Confidence**: settled
- **Quote**: "a hazard can exist in a system for an indefinite period of time. The system environment needs to shift somehow to turn that hazard into an outage. And essentially 'root cause' kind of equals the 'hazard.'" — and — "A gas leak in a house can go on for hours, but it's not until an electrical switch flips or a burner lights up before that gas leak turns into an outage or a problem, or an incident scenario. ... And this environmental shift, usually we refer to that as the trigger."
- **Our assessment**: A useful, citable piece of vocabulary the corpus previously lacked. The hazard/trigger split is a clean way to talk about prevention levers: harden the hazard *or* harden the trigger conditions. Note this is a conditioning-variable framing, not a contradiction of simpler "root cause" language elsewhere.

### Claim 3: The incident lifecycle phases are planning/preparation → occurrence → response → mitigation → recovery, and recovery actions double as preparation
- **Evidence**: Walcer describes the cycle explicitly; recovery/stabilization work is the same work that prepares the team for the next incident.
- **Confidence**: settled
- **Quote**: "we move through these phases of planning and preparation of incident occurrence, of response, of mitigation, and of recovery."
- **Our assessment**: Standard, well-established phase model. Worth capturing as the canonical Google phase list for Ch01 so the guide can map AI-agent activities (investigate/fix/write-up) onto specific phases.

### Claim 4: On a page, first determine user impact immediately, then apply a "Band-Aid" mitigation to buy time to diagnose
- **Evidence**: Walcer's "two things I love for people to think about" when the pager goes off; prioritizes a stabilizing mitigation when user impact is immediate.
- **Confidence**: settled
- **Quote**: "Number one is figure out immediately, or as quickly as possible, if you're having any user impact." — and — "if you see immediate user impact, like I love to prioritize having some kind of Band-Aid to bring about a little bit of stability, such that you have time in order to figure out what's really happening within your system."
- **Our assessment**: Concrete, actionable first-responder guidance. This is the human analog of what AI agents automate — note the ordering: stabilize user impact *before* deep diagnosis, which is a useful check on AI "investigate first" framing (see Cross-References re: incident.io Claim 1).

### Claim 5: IMAG (Incident Management at Google) is Google's variant of the FEMA incident management system; incidents need immediate, continuous, organized response
- **Evidence**: Walcer names IMAG explicitly and defines what qualifies as an incident.
- **Confidence**: settled
- **Quote**: "here at Google, we use a cool variant on the FEMA incident management system. We call it IMAG: Incident Management at Google. And we believe that incidents are an issue that have been escalated and require kind of immediate, continuous, organized response to address it."
- **Our assessment**: Names the actual Google framework (adapted from FEMA ICS). High-value concrete artifact for the guide — previously the corpus had Google SRE *fundamentals* (Ben Treynor) and Google SRE *alerting*, but not the named incident-command framework.

### Claim 6: Pre-determining accountability/ownership buys critical time; "deer-in-headlights" indecision multiplies across the team into hours or days lost
- **Evidence**: Walcer argues that figuring out who is accountable in advance avoids a multiplied paralysis; whoever's pager goes off is accountable.
- **Confidence**: settled
- **Quote**: "When pagers go off, it's really simple. Whoever's pager is going off is somehow responsible or accountable for that incident." — and — "that deer-in-headlights response of, 'Oh gosh, who does the thing?' When you multiply that by the number of people on your team, the number of people having that same response, what initially starts out as seconds in figuring out who's accountable can turn into minutes, can turn into hours, can sometimes turn into days of figuring out what subteam or what person is accountable for resolving an incident or an issue."
- **Our assessment**: Strong organizational argument for pre-assigned on-call ownership and clear escalation paths. Directly relevant to Ch04 (on-call/toil): undefined accountability is a measurable velocity tax.

### Claim 7: The three C's of incident management are Command, Control, and Communications
- **Evidence**: Walcer defines each C; says Google's protocol is a version of FEMA ICS with defined roles (incident commander, scribe, communications).
- **Confidence**: settled
- **Quote**: "we think about the three C's of managing incidents, which is: Command— so making decisions and keeping the team or subteam focused on the same goals; Control— know what is going on, coordinate people, be continuously aware; and Communications— so taking notes, being clear and ensuring that everybody has the same context."
- **Our assessment**: The single most extractable concrete artifact. These three C's are the template AI incident agents fill — see Cross-References. Command↔decisions, Control↔investigation/coordination, Communications↔scribe/notes/write-up.

### Claim 8: A shared, clearly-defined incident protocol builds positive habits — active state, clear chain of command, lower stress — and role titles are self-explanatory
- **Evidence**: Walcer argues a common protocol means you don't re-explain roles; everyone knows where to go and how to hand off.
- **Confidence**: settled
- **Quote**: "by using a shared and clearly defined process, we build really positive emergency response habits, including maintaining active state, a clear chain of command, and just overall reduction of stress. Everyone understands who to go to in an incident and how to hand off." — and — "the version of the FEMA incident command system, it has defined roles like incident commander, scribe, communications."
- **Our assessment**: The case for *standardization* of incident process. This is exactly what AI agents presuppose (a stable role/schema to slot into). Relevant to Ch01 as the "why standardize" argument.

### Claim 9: Google uses two responder types — component responders (one component) and systems-of-systems responders (span multiple components / "when it gets messy")
- **Evidence**: Walcer describes both types and how differentiating them lets you scale incident response to a large, messy technical stack; gives the Ads team as the example.
- **Confidence**: settled
- **Quote**: "we have essentially two types of incident responders at Google. We have component responders, and these are incident responders on-call for one component or system within Google's overall technical infrastructure. And then we'll also have systems of systems responders. And these are folks that are on-call to support incidents that fall between system boundaries. Or sometimes they're just the folks around when anything gets messy."
- **Our assessment**: A scalable responder topology. The "systems-of-systems" responder is the human analog of a supervisor/orchestrator over sub-agents — a clean bridge to the PagerDuty multi-agent architecture note (see Cross-References).

### Claim 10: Incident response is human-expensive; the takeaway is "do as little incident response as possible" — focus on prevention, preparedness, reliability from the ground up, avoid burnout
- **Evidence**: Walcer's stated number-one takeaway; argues response is exhausting and should be used sparingly.
- **Confidence**: settled
- **Quote**: "incident response is a really human-expensive activity. ... So I guess my number one takeaway is: do as little incident response as possible. Focus on great engineering— building really sound products that can handle a wide variety of user behaviors. Build in reliability from the ground up, use [incident response] sparingly, avoid burning out your team"
- **Our assessment**: The prevention-first thesis. Aligns with the SRE anti-toil / no-heroism philosophy and strengthens the toil-reduction argument in Ch04. It is *also* the strategic justification for AI-assisted response (offload the human-expensive activity) — but that conclusion is the Miner's, not Walcer's.

### Claim 11: Ben Treynor's principle — he "only wants new incidents"; don't repeat incidents
- **Evidence**: Walcer attributes the principle directly to Google SRE VP Ben Treynor as repeated guidance.
- **Confidence**: settled (as an attributed claim; the principle itself is Treynor's)
- **Quote**: "Something that our SRE vice president Ben Treynor has said on numerous occasions is that he only wants new incidents. You know, if we've seen something before, we don't wanna see it again."
- **Our assessment**: A named principle echoed across Google SRE literature. Note: this specific "only wants new incidents" line is **not** extracted as a numbered claim in `discussion-google-sre-ben-treynor-interview.md` (that note covers SRE fundamentals — error budgets, monitoring categories, the 50% rule — not incident-management specifics), so it is referenced thematically rather than by claim number. It reinforces the postmortem/learning loop in the lifecycle (Claim 3).

### Claim 12: Cross-team / multi-pager incidents are coordinated via the common protocol; Log4Shell showed Google mobilizing across product areas in hours
- **Evidence**: Walcer uses the 2021 Log4Shell vulnerability as a concrete example of rapid mobilization enabled by pre-established accountability, not heroics.
- **Confidence**: emerging (single anecdotal example, but illustrative of the accountability/IC-protocol claim)
- **Quote**: "During a couple really recent big blowups— you think of the Log4Shell vulnerability in JavaScript where, you know, you just get a little bit of remote code execution, it's cool, we all do it. A major security vulnerability, like threatening the whole internet. One of the cool things that Google was able to do was we were able to mobilize really quickly. It took a matter of hours before we had some teams on pretty much every product area working to address these issues and bring things to closure."
- **Our assessment**: Anecdotal but useful evidence that the accountability/protocol investment pays off at scale. The mechanism (pre-known ownership → fast mobilization) is the load-bearing claim; the Log4Shell story is the illustration.

### Claim 13: Internalize best practices as habits so responders don't rely on looking up a playbook
- **Evidence**: Walcer argues habits beat playbook-lookup in the moment.
- **Confidence**: settled
- **Quote**: "if you can take some of these best practices and turn them into habits, you won't be relying upon looking up a playbook to figure out how to resolve something. You'll have that internal, intuitive understanding of what those next steps should be and how we can communicate and work together to resolve an incident."
- **Our assessment**: Cultural claim about drilled practice. Relevant to Ch04 on-call readiness: the "first step forward" (even a sloppy one) matters more than perfect playbook recall. For AI, this is the counterpoint — agents *do* look up/execute playbooks, which is both their weakness (no intuition) and strength (no deer-in-headlights).

## Concrete Artifacts

### The three C's (verbatim from source)

```
Command — making decisions and keeping the team or subteam focused on the same goals
Control  — know what is going on, coordinate people, be continuously aware
Communications — taking notes, being clear and ensuring that everybody has the same context
```
*Source: Adrienne Walcer, SRE Prodcast S1E08 transcript (three C's of managing incidents).*

### IMAG / FEMA-derived role structure (verbatim from source)

```
IMAG: Incident Management at Google — Google's variant on the FEMA incident command system.
Incidents = an issue that has been escalated and requires immediate, continuous, organized response.
Defined roles (from FEMA ICS): incident commander, scribe, communications.
```
*Source: Adrienne Walcer, SRE Prodcast S1E08 transcript.*

### Two responder types (verbatim from source)

```
Component responders        — on-call for one component or system within Google's technical infrastructure.
Systems-of-systems responders — on-call to support incidents spanning multiple component systems,
                                incidents that fall between system boundaries, or "just the folks around
                                when anything gets messy."
```
*Source: Adrienne Walcer, SRE Prodcast S1E08 transcript (example: Google Ads component teams + overarching Ads incident response team).*

### Incident lifecycle phases (verbatim from source)

```
planning and preparation → occurrence → response → mitigation → recovery
(recovery/stabilization actions are the same work that prepares the team for the next incident)
```
*Source: Adrienne Walcer, SRE Prodcast S1E08 transcript.*

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-01-03-alerting.md` — Claim 1 ("alerting is synchronous (push): timing matters and you must be told when something is actionable") and Claim 5 ("a paging alert must be both urgent AND actionable by the responder"). This transcript treats the page/alert as the entry signal to incident management and states "whoever's pager is going off is somehow responsible or accountable" (Claim 6 here), which is consistent with the alerting note's actionable-by-responder requirement. The two notes agree the page is the actionable trigger.
  - `discussion-google-sre-ben-treynor-interview.md` — general SRE primary-source philosophy. Walcer's "do as little incident response as possible / avoid burning out your team" (Claim 10) and "I normally don't condone any kind of heroism" align with the anti-toil / no-heroism SRE thesis and with that note's Claim 1 (SRE "automate rather than perform manual labor"). The "only wants new incidents" line (Claim 11 here) is Walcer's attribution to Treynor but is **not** a numbered claim in the Ben Treynor note, so it is referenced thematically only.

- **Extends**:
  - `blog-incidentio-ai-sre-incident-run.md` — this transcript is the authoritative *human* incident-management process that incident.io's AI SRE is built to automate. The mapping is direct: incident.io Claim 1 (multi-source investigation on declaration) ≈ this note's **Control** C; incident.io Claim 8 (AI-written structured write-up from Slack/Meet/code context) ≈ this note's **Communications** C (scribe/notes); incident.io Claim 3 (human + AI investigate in parallel) ≈ this note's "bring in more people" principle (Claim 8/Claim 10). The guide can present the three C's as the schema AI agents fill.
  - `blog-pagerduty-sre-agent-architecture.md` — the "systems-of-systems responder" (Claim 9 here) is the human analog of the supervisor/orchestrator role; PagerDuty's Claim 8 (evolve single-agent → supervisor → hierarchical) describes the AI equivalent of scaling from component to systems-of-systems coverage.

- **Novel**:
  - **Hazard/trigger (root-cause-matrix) vocabulary** and the named **IMAG / three-C's / IC-scribe-communications role structure** as a concretely citable Google process. The corpus had Google SRE *fundamentals* (Ben Treynor) and Google SRE *alerting*, but not the named incident-command framework or the hazard/trigger lexicon. This fills that gap for Ch01.
  - **Analytical bridge (Miner synthesis, not from source):** this transcript's emphasis on **Communications** — "taking notes, being clear and ensuring that everybody has the same context" (Claim 7) and "everyone understands … how to hand off" (Claim 8) — is precisely the capability AI incident agents currently struggle with. `blog-pagerduty-production-ai-agent-gaps.md` Claim 3 (context fatigue) and Claim 6 (context poisoning) show that maintaining shared, correct context across a long incident is where agents degrade. So the human Communications/scribe role is the function an AI incident agent must emulate but, per the gaps note, fails at today. This is a novel connection the guide can use to scope what AI can and cannot yet take over in incident response.

- **Contradicts**: None identified. No contradiction issue filed. The source is the human baseline; the AI incident-response notes (incident.io, PagerDuty) describe automating *within* this process, not opposing it. The only tension — AI agents "investigate first" (incident.io Claim 1) vs. Walcer's "stabilize user impact first" (Claim 4) — is a conditioning-variable difference (diagnosis vs. stabilization are parallel workstreams in both framings), not a true contradiction.

## Guide Impact

- **Chapter 01 (Incident Response)**: Add a foundational "human incident command" subsection built on this note: the lifecycle (preparation → occurrence → response → mitigation → recovery, Claim 3), the three C's (Claim 7), and the IMAG role structure (IC / scribe / communications, Claims 5 & 8). The chapter currently leans on AI-specific sources (incident.io, PagerDuty); this note supplies the authoritative human baseline those agents augment, letting the guide explicitly separate "what humans do in incident command" from "what AI agents automate within it" (map per Cross-References → Extends). Also add the hazard/trigger vocabulary (Claim 2) as a prevention-framing tool.
- **Chapter 04 (On-call and Toil)**: Use Claim 6 (pre-determined accountability avoids multiplied "deer-in-headlights" lost time) and Claim 9 (component vs systems-of-systems responder scaling) to inform on-call ownership and escalation design. Use Claim 10 ("do as little incident response as possible," prevention-first, avoid burnout) to reinforce the toil-reduction thesis already implicit in the chapter.
- **Cross-chapter (Ch01 ↔ Ch04)**: The Novel analytical bridge (human Communications/scribe role ≈ the AI capability that degrades per PagerDuty gaps Claims 3 & 6) can anchor a "what AI cannot yet do in incident response" callout, scoping realistic automation boundaries.

## Extraction Notes

- Full transcript read end-to-end (313 lines of extracted text from the 80 KB HTML page; title confirmed "Incident management process with Adrienne Walcer"). No sub-pages were followed — the only external reference is Walcer's O'Reilly book *Anatomy of an Incident*, which is a book, not a web page, so it was not fetched.
- The page carries no structured publish date; the year is estimated as 2022 from SRE Prodcast Season 1 / the *Anatomy of an Incident* (2022) reference and the Log4Shell (2021) anecdote. Recorded as "2022 (estimated)" in frontmatter.
- All quotes are copied character-for-character from the extracted transcript text, including the transcript's own bracketed annotation `[incident response]` in Claim 10. The only AI/LLM content in this note is the Miner's synthesis in Cross-References (Novel) and Guide Impact, clearly marked as such.
