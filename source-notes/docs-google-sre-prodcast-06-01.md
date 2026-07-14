---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-06-01/
source_type: docs
title: "This Is Fine! with Colette Alexander and Clint Byrum (SRE Prodcast S6E01)"
author: "Google SRE (Prodcast host Steve McGhee); guests Colette Alexander (co-host, 'This Is Fine!' podcast; president, Resilience in Software Foundation) and Clint Byrum (co-host, 'This Is Fine!' podcast; SRE)"
date_published: 2026 (estimated; recorded live at SREcon Americas 2026 in Seattle — exact air date not published on the transcript page)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#190"
---

# This Is Fine! with Colette Alexander and Clint Byrum (SRE Prodcast S6E01)

> A short (~9-minute), conversational Season-6 "Prodcast Live!" recording from SREcon
> Americas 2026 in which two resilience-engineering podcast hosts push back on the
> resurgence of MTTR as an incident metric — citing Stepan Davidovic's Monte Carlo
> simulations and the omission of business impact — and briefly surface CAST as a
> root-cause-analysis alternative and the Resilience in Software Foundation community.
> **Contains no AI/LLM content**; its value to the guide is the MTTR-critique and
> resilience-engineering framing, both of which the corpus already carries elsewhere.

## Source Context

- **Type**: docs (podcast transcript — SRE Prodcast Season 6, Episode 1, "Prodcast Live!" recorded at SREcon).
- **Author credibility**: Google SRE oral history (host Steve McGhee, a Google SRE Reliability Advocate). Guests are credible practitioner voices: Colette Alexander is president of the Resilience in Software Foundation and co-hosts "This Is Fine!", a resilience-engineering podcast; Clint Byrum is an SRE and co-host of the same podcast. The MTTR critique is opinion/practice-based, not a primary research write-up, but the guests cite named secondary work (Davidovic's paper, Forsgren's *Accelerate*).
- **Scope**: A casual, recorded-live chat. The load-bearing content is (a) a critique of MTTR as a metric — its statistical weakness (Davidovic Monte Carlo) and its omission of business impact — and (b) two community/methodology pointers: CAST as a root-cause-analysis alternative, and the Resilience in Software Foundation. It does **not** cover AI/LLM operations, code, configs, or measurements. The MTTR segment is the mining-worthy signal the triage flagged.
- **No AI/LLM content**: Confirmed — no mention of AI in SRE, LLM operations, or automation of SRE tasks. This note's only AI relevance is the Miner's cross-reference synthesis (clearly marked), not a claim from the source.

## Extracted Claims

### Claim 1: A "return of MTTR" at SREcon frustrated practitioners who believed the metric had been retired, and was seen as backsliding into an expo-hall/keynote artifact
- **Evidence**: Colette and Clint react to MTTR resurfacing in conference talks. Colette says she was "really upset" to see it return; Clint says he thought it had been "contained to the expo hall" and was surprised to see it in a keynote.
- **Confidence**: anecdotal (their personal reaction to a conference trend)
- **Quote**: "I was really upset at the return of MTTR. What the heck, man? I thought we got rid of it, and it came back." — and — "I thought we had contained that to the expo hall."
- **Our assessment**: Anecdotal, but a genuine "MTTR fatigue" signal that matches the directional claim in `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 15 ("the field is moving away from MTTR as the single be-all metric"). Useful as field-sentiment evidence, not as a prescription.

### Claim 2: Stepan Davidovic's work discredited MTTR (and Accelerate-era metrics) via Monte Carlo simulations showing incident durations are not statistically correlated enough to matter
- **Evidence**: Clint states Davidovic "killed it" and describes the mechanism: Davidovic's "very free paper" explains the math via Monte Carlo simulations demonstrating that "the times in incidents are not related to each other enough to statistically matter" — "You can't move it enough to make it matter statistically." Clint says he sends the paper/link to executives and engineers.
- **Confidence**: emerging (secondhand, colloquial account of Davidovic's analysis; not verified against the primary paper in this note)
- **Quote**: "Stepan Davidovic killed it, and yet the zombie rises again." — and — "the times in incidents are not related to each other enough to statistically matter. And I link to Stepan Davidovic's very free paper where it explains the math. And he did these Monte Carlo simulations that-- I think if anybody goes and reads those and has the time, which I know many executives do not-- if you have the time to think about it, it presents itself very clearly. You can't move it enough to make it matter statistically."
- **Our assessment**: This is the load-bearing, **novel** attribution in the episode: a named primary analysis (Davidovic's Monte Carlo) behind the MTTR-skeptic position. It is the specific empirical backing the other MTTR-skeptic notes in our corpus lack (they cite Courtney Nash's void report and Google data-center fleet experience). Caveat: we rely on the speakers' summary; the Smith should cite Davidovic's actual paper for the math before treating the mechanism as settled.

### Claim 3: Dr. Nicole Forsgren's Accelerate was seminal for modern SRE/DevOps metrics, but some of its conclusions fall to the wayside as new research (e.g., Davidovic's) is done
- **Evidence**: Clint credits Forsgren's work for bringing him "into a modern history perspective" and calls *Accelerate* "important and still is important," then immediately qualifies it: "just like all good science, some of it falls to the wayside as new research is done, like Stepan Davidovic killed it."
- **Confidence**: emerging
- **Quote**: "Dr. Forsgren's work was like seminal in bringing me into a modern-- history perspective. I think a lot of people would say Accelerate was important and still is important. But that part, just like all good science, some of it falls to the wayside as new research is done, like Stepan Davidovic killed it, and yet the zombie rises again."
- **Our assessment**: Noteworthy historically: it frames MTTR not just as a weak metric but as a DORA/*Accelerate*-era metric being revised by newer research. Plausible and relevant to the guide's metrics framing, but the claim is an opinion about a research lineage, so confidence is emerging.

### Claim 4: MTTR omits business impact — a long incident can have low business impact and a short incident can be severe, so time-to-recover is a poor proxy for what matters
- **Evidence**: Colette's hallway explanation: "you've had an incident that's lasted three hours, three days, three weeks that might not have impacted your business very much. And you've had an incident that's lasted 10 minutes, I bet, that has-- really sucked for your business." She then states the gap directly: "the other piece that MTTR leaves out is what is the business impact?"
- **Confidence**: settled (intuitive and directly corroborated by an existing corpus claim)
- **Quote**: "you've had an incident that's lasted three hours, three days, three weeks that might not have impacted your business very much. And you've had an incident that's lasted 10 minutes, I bet, that has-- really sucked for your business." — and — "And so the other piece that MTTR leaves out is what is the business impact? What are the other elements, besides time, of an incident that actually do materially matter to you?"
- **Our assessment**: The single most actionable critique for the guide. It moves the argument from "MTTR is statistically weak" (Claim 2) to "MTTR is the wrong axis" — time ≠ customer/business impact. Directly corroborated by `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claim 13 (Singer: MTTR "is a pretty poor proxy for the actual customer experience"). This is the bridge the guide's incident-metrics section should use.

### Claim 5: CAST (a system-theoretic method) is being proposed as an alternative more attuned to replacing root-cause analysis
- **Evidence**: Clint mentions seeing "a talk on CAST" at the conference and describes it as "an interesting adjustment, more attuned to replacing root-cause analysis"; he says he "didn't know much about CAST before" and has "now got some books to read."
- **Confidence**: anecdotal (he just encountered it; explicitly pre-learning)
- **Quote**: "I did see there was a talk on CAST, which is an interesting adjustment, more attuned to replacing root-cause analysis. I didn't know much about CAST before. I've now got some books to read. So that's an exciting-- like, OK, here's a new model."
- **Our assessment**: A light, secondhand pointer. CAST = *System-Theoretic Accident Model and Processes* (Nancy Leveson), the sibling of STPA. This overlaps `docs-google-sre-prodcast-04-07-stpa.md` (the dedicated STPA methodology note); both are Leveson system-theoretic safety analyses positioned as alternatives to root-cause analysis. S6E01 adds only a named pointer, no methodology — so it Extends the STPA note rather than contributing new substance.

### Claim 6: The Resilience in Software Foundation is a practitioner community (Slack, events, FRAM training, merch) for resilience engineering
- **Evidence**: Colette (its president) describes it as "a bunch of nerds that hang out and talk about resilience engineering in the software domain," points to resilienceinsoftware.org for membership (Slack + free events), notes an upcoming "FRAM training," and shows an "Anti Complexity Complexity Club" hoodie.
- **Confidence**: settled (factual description of an organization)
- **Quote**: "We're a bunch of nerds that hang out and talk about resilience engineering in the software domain, mostly, although there are some folks who are not of the software domain who grace us with their-- really, an awesome presence." — and — "we have a Slack, and you can go to resilienceinsoftware.org to become a member. And becoming a member gets you access to that Slack and free access to all of our events."
- **Our assessment**: A community-resource pointer, not a technical claim. Useful as a "where to go deeper" citation for the resilience-engineering framing the guide touches (and which Claim 7 reinforces). Not AI/LLM-specific.

### Claim 7: You can only fight complexity with complexity, due to the law of requisite variety (attributed to David Woods / Ashby, 1956)
- **Evidence**: Colette states the law; Clint attributes it to "David Woods" and calls him "the master of complexity." The same law is the central anchor of `docs-google-sre-prodcast-03-11-embracing-complexity.md` (quoting Maguire: "if your problems are all highly variable and very dynamic and changing, then your responses to those problems have to be similarly so" — Ashby, 1956).
- **Confidence**: settled (established systems-engineering principle, correctly attributed)
- **Quote**: "But you can only fight complexity with complexity due to the law of requisite variety." — and (Clint) — "There must-- Dr. Woods must have written it, David Woods. Right? ... He's the master of complexity, for sure."
- **Our assessment**: Direct, independent corroboration of the embracing-complexity note's central anchor (requisite variety / Ashby 1956), here invoked by named practitioners at SREcon. Strengthens the complexity/adaptive-response thesis for Ch02. Novel only as an independent echo; the principle itself is covered in the STPA/complexity notes.

## Concrete Artifacts

### Davidovic's MTTR critique (verbatim from source)

```
"the times in incidents are not related to each other enough to statistically matter.
 And I link to Stepan Davidovic's very free paper where it explains the math. And he
 did these Monte Carlo simulations that-- ... You can't move it enough to make it
 matter statistically."
*Source: Clint Byrum, SRE Prodcast S6E01 transcript (MTTR segment, ~[00:06:22]).*
```

### Business-impact gap in MTTR (verbatim from source)

```
"you've had an incident that's lasted three hours, three days, three weeks that might
 not have impacted your business very much. And you've had an incident that's lasted
 10 minutes, I bet, that has-- really sucked for your business."
"And so the other piece that MTTR leaves out is what is the business impact?"
*Source: Colette Alexander, SRE Prodcast S6E01 transcript (hallway explanation, ~[00:07:00]).*
```

### Resilience in Software Foundation resources (verbatim from source)

```
resilienceinsoftware.org  — membership => Slack access + free access to all events
Upcoming: FRAM training ("we have a FRAM training coming up next month")
Merch: "Anti Complexity Complexity Club" hoodie (law of requisite variety tie-in)
*Source: Colette Alexander, SRE Prodcast S6E01 transcript (~[00:02:04]–[00:03:08]).*
```

### CAST as RCA alternative (verbatim from source)

```
"a talk on CAST, which is an interesting adjustment, more attuned to replacing
 root-cause analysis."
*Source: Clint Byrum, SRE Prodcast S6E01 transcript (~[00:06:00]). CAST = System-Theoretic
 Accident Model and Processes (Nancy Leveson) — sibling method to STPA (see Cross-References).*
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 15** — "The field is moving away from MTTR as the single be-all metric, toward richer insights (Sarah cites Courtney Nash's 'void report')." S6E01's MTTR backlash (Claim 1) and Davidovic Monte Carlo (Claim 2) are the same field shift, stated at a different conference a season later. Direct match.
  - `docs-google-sre-prodcast-04-02-data-centers.md` **Claim 6** — "MTTR/MTBF are weak at fleet scale because failures are novel and non-normal." That note explicitly says its critique "corroborates `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 15"; S6E01's Davidovic Monte Carlo is the *statistical-mechanics* backing for that same shift, and the data-centers note's "at the component layer MTTR/MTBF still earn their keep" nuance is exactly the conditioning variable S6E01 operates within (see Contradicts).
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` **Claim 13** — "Error budgets beat incident counts / MTTR for communicating SRE value… MTTR is a pretty poor proxy for the actual customer experience." S6E01 Claim 4 (business impact omitted by MTTR) is the intuitive, practitioner version of Singer's same point. Direct match.
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` (requisite-variety anchor) — S6E01 Claim 7 cites the same law of requisite variety (David Woods / Ashby 1956) that anchors the complexity note (Maguire: "if your problems are all highly variable… your responses… have to be similarly so"). Independent corroboration by named practitioners.
  - `docs-google-sre-prodcast.md` (master index) — confirms S6E01 is a Season-6 "Prodcast Live!" episode recorded at SREcon; the index lists S6 AI episodes (S6E4, S6E8) but not this one, so S6E01 has no prior transcript-level note (novel at episode level).

- **Contradicts**: None filed. The only apparent tension — S6E01's anti-MTTR stance vs. `discussion-google-sre-ben-treynor-interview.md` **Claim 13** (Treynor: availability = MTBF × MTTR, "mean time to repair — once it stops working, how long does it take until you fix it") — is a **conditioning variable, not a contradiction**. Treynor uses MTTR at the *component/availability* level; S6E01 attacks MTTR as an *aggregate/comparative incident metric* and its omission of business impact. The corpus already documents this split without contradiction: incident-response-tooling Claim 15 notes "MTTR remains a useful coarse metric even as richer ones emerge," and data-centers Claim 6 notes "at the component layer MTTR/MTBF still earn their keep." CONTRADICTIONS.md has no MTTR entry and there are no open `contradiction`-labeled issues, so no new contradiction issue is filed. Per MINER §4a ("When NOT to file": context difference; already captured), this is correctly treated as a conditioning variable.

- **Extends**:
  - The MTTR-skeptic thread (`docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 15; `docs-google-sre-prodcast-04-02-data-centers.md` Claim 6) — S6E01 adds the specific, *named* primary analysis (Stepan Davidovic's Monte Carlo paper) that those notes cite around (Nash's void report; Google fleet experience) but do not themselves supply. This is the citable empirical anchor for the "MTTR is statistically weak" position.
  - `docs-google-sre-prodcast-04-07-stpa.md` (STPA methodology note) — S6E01's CAST mention (Claim 5) is the same Leveson system-theoretic family (CAST = System-Theoretic Accident Model and Processes; STPA = Systems Theoretic Process Analysis), both positioned as alternatives to root-cause analysis. S6E01 only names CAST; the STPA note carries the actual methodology. The guide can treat them as one "system-theoretic RCA alternatives" family.

- **Novel**:
  - **The Stepan Davidovic Monte Carlo attribution** as the specific empirical backing for the MTTR critique — absent from all other corpus notes, which lean on Nash's void report or Google fleet data. This is the episode's unique, citable contribution.
  - **The business-impact intuition as a first-person practitioner articulation** of why MTTR is the wrong axis (mirrors, but independently states, the SLOs Claim 13 customer-experience point).
  - **Resilience in Software Foundation** as a concrete community pointer (resilienceinsoftware.org, Slack, FRAM training) — a resource citation the corpus previously lacked.
  - **CAST** named as a root-cause-analysis alternative alongside the already-mined STPA — extends the system-theoretic-RCA family.

## Guide Impact

- **Chapter 02 (SRE Fundamentals / metrics)**: Add the MTTR critique with its two prongs — (a) Davidovic's Monte Carlo showing incident durations are not statistically correlated enough to matter (S6E01 Claim 2; cite Davidovic's paper as the primary source), and (b) MTTR omits business impact (S6E01 Claim 4). Cite S6E01 alongside `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 15, `docs-google-sre-prodcast-04-02-data-centers.md` Claim 6, and `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claim 13. Preserve the Treynor conditioning variable (`discussion-google-sre-ben-treynor-interview.md` Claim 13): MTTR is weak as an *aggregate/comparative* metric but still earns its keep at the *component/availability* level. Also surface the law of requisite variety (S6E01 Claim 7) as corroboration of the resilience/complexity framing already in `docs-google-sre-prodcast-03-11-embracing-complexity.md`.
- **Chapter 04 (Incident Management / incident metrics)**: Use the "incident-metrics debate" to recommend richer metrics than MTTR — error budgets (SLOs Claim 13) and the void-report-style richer insights (incident-response-tooling Claim 15) — grounded in S6E01's business-impact argument (Claim 4). Note CAST (S6E01 Claim 5) as a named root-cause-analysis alternative that belongs to the same system-theoretic family as the STPA material already mined (`docs-google-sre-prodcast-04-07-stpa.md`), for the post-incident-analysis section.
- **No AI/LLM change**: This episode has zero AI/LLM content. It should inform the guide's *human* SRE-fundamentals and incident-metrics sections only; do not cite it for any AI/LLM operational claim.

## Extraction Notes

- Full transcript read end-to-end (extracted from the 59 KB HTML page via `curl`; the live WebFetch model was unavailable, so the page was fetched and stripped of scripts/styles, then re-read in full). The episode is ~9 minutes of conversational audio; the MTTR segment (~[00:04:05]–[00:07:54]) is the substantive, mining-worthy signal the triage flagged.
- All quotes marked direct were copied character-for-character from the extracted transcript text, including the transcript's own bracketed annotation `[LAUGHTER]` context and mid-word em-dashes (e.g., "modern-- history perspective", "has-- really sucked"). Speaker attributions (Colette Alexander, Clint Byrum, Steve McGhee) were mapped from the transcript's turn structure.
- No part of the source was paywalled; the transcript is publicly accessible on sre.google.
- `date_published` is estimated as 2026: the transcript identifies the recording as "SREcon Americas 2026" in Seattle (Season 6 "Prodcast Live!") but the page carries no explicit air date. The master index note (`docs-google-sre-prodcast.md`) confirms S6 is the conference-recorded season.
- No contradiction issue was filed: the only apparent conflict (anti-MTTR vs. Treynor's MTBF×MTTR) is a conditioning variable already documented as such across incident-response-tooling Claim 15 and data-centers Claim 6, and CONTRADICTIONS.md / open `contradiction` issues contain no MTTR entry.
