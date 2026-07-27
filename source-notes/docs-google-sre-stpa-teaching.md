---
source_url: https://sre.google/stpa/teaching/
source_type: docs
title: "STPA (System Theoretic Process Analysis) — Teaching a new way to prevent outages at Google"
author: Garrett Holthaus, Technical Writer (Google)
date_published: 2026 (estimated; page carries no explicit publication date; training evolution described spans from 2021 to ongoing self-serve curriculum buildout)
date_extracted: 2026-07-27
last_checked: 2026-07-27
status: current
confidence_overall: settled
issue: "#586"
---

# Teaching STPA at Google

> A first-hand account of how Google built custom STPA training for software engineers — covering the evolution from a control-structures-only course through full workshops to a self-serve video curriculum, the key pedagogical insight that engineers neglect feedback paths, and the adoption challenges (attendance, follow-through) that drove each iteration. Complements the STPA methodology coverage in `docs-google-sre-prodcast-04-07-stpa.md` with the training/education angle that source does not address.

## Source Context

- **Type**: docs (Google SRE site blog-post / technical article, published on sre.google)
- **Author credibility**: High. Garrett Holthaus is a Technical Writer at Google who personally participated in building and delivering Google's internal STPA training program. He recounts first-hand decisions, challenges, and outcomes across multiple training iterations from 2021 onward. The page is published on the official sre.google domain under Google SRE's authority.
- **Scope**: Covers the full evolution of Google's STPA training program — initial motivation (physical-system examples failing for software audiences), the control-structures course, the full STPA workshop, the stepped approach (30/60-minute tutorials → workshop), and the latest self-serve video curriculum. Includes specific pedagogical insights (feedback-path neglect, control-structure abstraction level), a concrete 30-day delayed outage case study, a dataflow-vs-control-structure comparison with examples, and adoption metrics (50% workshop attendance, low post-workshop follow-through). Does NOT cover the STPA methodology itself in depth — it assumes familiarity with control-structure modeling and focuses on education challenges.

## Extracted Claims

### Claim 1: Physical-system STPA examples (Mars Polar Lander) failed to resonate with Google's pure-software audience, forcing creation of custom training grounded in real software examples
- **Evidence**: First-hand account of audience reaction to standard STPA training materials. Google hosted instructor-led training using existing materials, but audiences dismissed physical-system examples.
- **Confidence**: settled
- **Quote**: "However, when we presented these examples of physical systems (such as the Mars Polar Lander crash) to Google audiences, the response we got was, 'That's interesting, but I don't see how it applies to my pure software system.'"
- **Our assessment**: A clear, specific, first-hand observation. This is likely a universal problem for any organization teaching STPA to software engineers — the canonical examples are from aerospace/chemical engineering. Google's response (building software-specific examples from its own systems) is a replicable pattern the guide should recommend. We buy this as settled for Google's experience.

### Claim 2: Teaching the creation of useful control structures is very difficult over a limited time period; it requires sustained practice, expert guidance, and instructors cannot learn each trainee's system fast enough
- **Evidence**: The 2-day control-structures workshop faced three challenges: (a) teaching the right level of controller abstraction is hard, (b) skill requires "time, experience creating control structures, and guidance from experts," and (c) the 7 participants built models of 7 different software systems, overwhelming the instructors.
- **Confidence**: settled
- **Quote**: "we discovered that teaching people to create a useful control structure is very difficult to accomplish over a limited period of time."
- **Quote**: "it takes time, experience creating control structures, and guidance from experts to achieve skill in modeling a system with control feedback loops."
- **Our assessment**: The 7-participants-to-7-systems problem is a specific, vivid constraint that any STPA training program will face: domain expertise in every trainee's system is impractical. The guide should recommend that initial STPA training use a shared worked example (as Google later adopted with its real Google examples) rather than having each participant analyze their own system.

### Claim 3: Software engineers design control paths carefully but systematically neglect feedback paths — this insight became Google's primary messaging hook for STPA adoption
- **Evidence**: Repeated observation across many training sessions and STPA projects at Google. The feedback-path framing was the "powerful theme" that consistently resonated with audiences and caused a "shift in thinking."
- **Confidence**: settled
- **Quote**: "While most software developers do a thoughtful job of designing the control path–even without knowledge of control theory–they spend less time (if any!) designing the feedback path."
- **Our assessment**: This is the article's most important pedagogical contribution. It is a specific, testable claim about software engineering culture that the guide can adopt as a design-review heuristic: when reviewing any system, start by asking "where is the feedback?" We buy this as a settled observation about developer behavior, not just an STPA-specific claim — it generalizes to any control-loop design pattern (Kubernetes operators, CI/CD pipelines, AI agents).

### Claim 4: A concrete Google outage involved bad feedback between software components AND missing feedback from software to humans, with the unsafe condition persisting unmonitored for 30 days
- **Evidence**: Specific case study from Google STPA work. Two feedback failures in one outage: (a) one software component passed bad feedback to another, causing an unsafe control action, and (b) no humans were monitoring the indicators that the unsafe action would occur. The condition existed for 30 days.
- **Confidence**: anecdotal
- **Quote**: "In one particular case at Google, a software controller–acting on bad feedback from another software system–determined that it should issue an unsafe control action scheduled for 30 days later."
- **Quote**: "no software engineers–humans–were actually monitoring the indicators."
- **Quote**: "the unsafe condition existed for 30 days"
- **Our assessment**: A high-value concrete example of the feedback-path failure pattern. It illustrates both types of feedback failure (inter-component and human-in-the-loop) in a single incident. Marked anecdotal because it is one case study without postmortem-level details (specific system, root cause, fix). The 30-day latency is striking and should be cited as a vivid illustration of why missing feedback to humans is dangerous.

### Claim 5: The feedback-path framing caused a documented "shift in thinking" in how Google engineers approach system design — leading them to question assumptions about neighboring systems
- **Evidence**: Repeated feedback from training participants reported in the first person. Engineers began asking explicit questions about information quality from adjacent systems.
- **Confidence**: settled
- **Quote**: "Over and over, we would hear from other Googlers that these examples had caused a shift in thinking about how they approached system design."
- **Quote**: "Instead of assuming that a neighboring system would always behave perfectly, people started asking, 'what if that system passes me bad or incomplete information, or doesn't get the information to my system at the right time?'"
- **Our assessment**: The "shift in thinking" claim is well-supported by the article's consistent reporting across multiple training cohorts. The explicit question ("what if that system passes me bad or incomplete information") is a concrete, teachable challenge that any engineer can apply in a design review. We buy this as a genuine and replicable effect of STPA training.

### Claim 6: Control structures enable analysis at an abstraction level that dataflow diagrams cannot — a 33-box dataflow diagram compresses to a 10–15 box control structure, and meaningful analysis is possible with even fewer
- **Evidence**: Side-by-side comparison of a dataflow diagram (33 boxes, "spider web of arrows") and a control structure (4 boxes in the example, from an actual Google STPA). The article argues dataflow diagrams "do not indicate whether data is control or feedback" and do not establish control hierarchy.
- **Confidence**: settled
- **Quote**: "dataflow diagrams do not indicate whether data is control or feedback"
- **Quote**: "A typical control structure for a Google system has 10–15 boxes, and meaningful analysis can be done with even fewer boxes."
- **Our assessment**: A concrete, quantitative comparison that the guide can reference to motivate STPA adoption for teams that currently rely on dataflow/architecture diagrams. The compression ratio (33 → 4 boxes) is particularly compelling. We buy this as a valid methodological claim — control structures deliberately omit implementation detail in favor of control relationships, which is exactly the abstraction level needed for hazard analysis.

### Claim 7: STPA narrows the search space from "millions of lines of code to a few hundred lines" by identifying the specific code locations where decisions that lead to unsafe behavior occur
- **Evidence**: The article states this as a key message that resonated in training. The mechanism: scenarios pointing to unsafe control actions "literally point to the lines of code responsible for a possible outage."
- **Confidence**: settled
- **Quote**: "In the process of applying STPA, you are effectively narrowing down the search for issues from millions of lines of code to a few hundred lines."
- **Our assessment**: A striking and memorable claim. The mechanism is plausible — STPA identifies specific control decisions and the code that implements them — but the "few hundred lines" figure is a rule-of-thumb, not a measured outcome. Still, the directional claim (STPA drastically focuses analysis effort) is well-supported by the methodology and by the 20%-Pareto findings reported in `docs-google-sre-prodcast-04-07-stpa.md` (Claim 8).

### Claim 8: Only ~50% of registrants attended the 3-day STPA workshop, attributed to the difficulty of budgeting three days for training — solved via a stepped approach with 30 and 60-minute tutorials that let participants self-select
- **Evidence**: Concrete metric from the first full STPA workshop offering. Registration filled quickly, but attendance was roughly half. The proposed solution: offer short tutorials (30 and 60 minutes) first, then invite interested attendees to register for the full workshop.
- **Confidence**: anecdotal
- **Quote**: "only about half the registrants showed up"
- **Quote**: "This can probably be attributed to the difficulty in budgeting three days of time for training."
- **Our assessment**: The 50% attendance figure is a single data point but reported as a first-hand observation. The self-selection solution (tutorials → workshop) is a straightforward and sensible approach that any organization can replicate. We recommend the guide present this pattern: use short, high-impact orientation sessions to let engineers self-select before committing to multi-day training.

### Claim 9: Even workshop attendees who expressed continuing interest "didn't actually try running STPA on their own system" after training — leading to the latest phase of self-serve video curriculum with templates and homework
- **Evidence**: First-hand observation of low post-training application, even among self-selected, motivated attendees. This directly motivated the self-serve curriculum.
- **Confidence**: anecdotal
- **Quote**: "for the most part, they didn't actually try running STPA on their own system"
- **Our assessment**: This is the critical adoption failure mode that any STPA training program must address. Classroom training produces interest but not independent practice. Google's solution — incremental homework with templates as part of a recorded video curriculum — is a credible mitigation that addresses the "intimidation" factor. We recommend the guide capture this as a key lesson: STPA training is not complete until participants have run at least a partial STPA on their own system.

### Claim 10: Google's latest training approach is a self-serve internal workshop with short recordings and homework templates where participants incrementally apply STPA to their own system, also serving as a pipeline to identify future STPA champions
- **Evidence**: Described as the current/latest phase of STPA training development. Builds incrementally so the barrier to starting is lower, and completion yields a strong starting analysis for each participant's system.
- **Confidence**: emerging
- **Quote**: "we are building a self-serve internal version of our workshop, with a series of short recordings, including homework assignments"
- **Quote**: "working incrementally and doing each part of STPA right after watching the corresponding training video will be less intimidating"
- **Our assessment**: This is the most mature form of the training evolution and the one most applicable outside Google. The self-serve, incremental, template-driven model addresses both the time-commitment barrier (Claim 8) and the follow-through gap (Claim 9). The additional goal — identifying "early adopters who will help scale STPA at Google by championing it to their individual teams" — creates a virtuous cycle. Confidence is emerging because this phase was still in development at the time of writing and its effectiveness is not yet measured.

## Concrete Artifacts

### The 30-day delayed outage case study (verbatim, from the article)

```
"In one particular case at Google, a software controller–acting on bad feedback from
another software system–determined that it should issue an unsafe control action
scheduled for 30 days later. Even though there were indicators that this unsafe action
was going to occur, no software engineers–humans–were actually monitoring the indicators."

[...] "the unsafe condition existed for 30 days" [...] "this one outage, there were two
feedback issues–bad feedback from one piece of software to another, and missing feedback
from the software to the engineers"
```

### Dataflow vs control structure comparison (verbatim description from the article)

```
Dataflow diagram:
  33 boxes with a "spider web of arrows" connecting them
  "dataflow diagrams do not indicate whether data is control or feedback"
  Do not show "control hierarchy –which pieces of software control the state of
  other pieces of software"
  "can be fiendishly complex" for millions-of-lines-of-code systems

Control structure:
  "A typical control structure for a Google system has 10–15 boxes"
  "meaningful analysis can be done with even fewer boxes"
  Example shown in article: 4 boxes from an actual Google STPA
  Each arrow labeled with control actions or feedback
  Makes clear "the goal of each software controller, what other pieces of
  software it controls, and where it gets feedback"
  "immediately noticed missing feedback from controller C to controller B"
```

### Training evolution timeline (synthesized from the article narrative)

```
2021              → Initial class for 40 Googlers using existing materials
                     (physical-system examples — poor fit)
Early post-2021   → Control-structures-only course (2-day workshop)
                     (7 participants, 7 different systems — overwhelming for instructors)
Post-controls     → Full STPA workshop (3-day, all STPA steps, built around a
                     real Google example)
                     (~50% attendance rate; low post-workshop follow-through)
Next iteration    → Stepped approach: two short tutorials (30 min, 60 min) with
                     real Google examples → self-selected workshop registration
Latest phase      → Self-serve internal video curriculum with homework templates;
                     participants apply STPA to their own systems incrementally;
                     also identifies future STPA champions
```

### Key quotes from training participant (verbatim from the article)

```
"The class itself is very well structured. I've heard about STPA in past years,
but this was the first time I saw it explained with concrete examples. The Google
example at the end was also really helpful."
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-04-07-stpa.md` — **Claim 12** (broken feedback mechanisms and missing/implicit goals are the two most common STPA findings in practice): This source independently and directly corroborates that claim — the entire training program's messaging hook was that engineers neglect feedback paths, and the article identifies bad feedback and missing feedback to humans as the central failure pattern. The 30-day outage case study is a concrete instantiation of Claim 12's abstract finding. **Claim 8** (20% STPA Pareto adaptation): This source shows the same pragmatic scaling via the stepped training approach and the "narrowing down the search from millions of lines to a few hundred" framing — independently describing the same streamlining philosophy from the training side. **Claim 6** (worked example of diff-based road-closure pipeline): The new source's 30-day outage case study is a separate, complementary concrete example from a different system, strengthening the evidence base.
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` — **Claim 15** (Google has worked with MIT / Nancy Leveson on STPA for "several years," building tooling to make it far less manual): This source confirms and extends Claim 15 — it shows that the training program is a real operational effort (not just research), describes the multi-year evolution, and documents the practical scaling challenges that the tooling mentioned by Treynor aims to address. No contradiction; fully complementary.

- **Extends**:
  - `docs-google-sre-prodcast.md` — **Concrete Artifacts → Prodcast Season/Episode Index** (line 317: "S4E7 STPA (Theo Klein, Jeffrey Snover) — System Theoretic Process Analysis"): This source note provides the training/education angle that neither the Prodcast index entry nor the S4E7 podcast transcript covers. Together, `docs-google-sre-prodcast-04-07-stpa.md` (methodology + worked example) and this note (training + adoption challenges) provide a complete picture of Google's STPA practice.

- **Novel**: Material new to the corpus:
  - The full training evolution arc from 2021 onward (control-structures course → full workshop → stepped tutorials → self-serve video curriculum), with documented rationale for each iteration.
  - The specific pedagogical insight that feedback-path neglect is the most effective messaging hook for STPA adoption among software engineers.
  - The 30-day delayed outage case study — a concrete Google outage with two feedback failures (inter-component bad feedback + missing human feedback).
  - The explicit dataflow-diagram-vs-control-structure comparison (33 boxes vs 10–15 boxes) with concrete numbers.
  - The adoption failure data (50% workshop attendance, low post-training application) and Google's mitigation strategies.
  - The self-serve video + template + homework model as an STPA scaling approach.
  - The role of STPA training as a pipeline for identifying future STPA champions ("early adopters who will help scale STPA at Google by championing it to their individual teams").

- **Contradicts**: None. No claim in this source opposes any existing source note. The training claims are complementary to the methodology claims in `docs-google-sre-prodcast-04-07-stpa.md` and the strategic STPA mention in `docs-google-sre-prodcast-03-03-treynor-ai-ml.md`. No internal contradictions. No contradiction issue is filed.

## Guide Impact

- **Chapter 02 (Risk Assessment)**: Add the pedagogical insight from Claim 3 (engineers neglect feedback paths) as a design-review heuristic for any chapter covering control-loop or automation design. Include the training evolution pattern (Claims 8–10) as a recommendation for how teams should structure STPA adoption: start with short (30–60 min) orientation sessions using real software examples, then offer workshop-level training to self-selected participants, and follow up with template-driven incremental practice on participants' own systems.

- **Chapter 04 (Incident Management)**: Use the 30-day delayed outage case study (Claim 4) as a concrete illustration of missing feedback to humans — specifically, the finding that an unsafe condition can persist for weeks without anyone noticing. The "two feedback failures in one outage" framing (bad feedback between components + missing feedback to humans) is a specific diagnostic lens the guide should recommend for post-incident analysis: always check both inter-component feedback AND human-in-the-loop feedback.

- **Chapter 05 (Automation & Safety)**: Use the dataflow-vs-control-structure comparison (Claim 6) and the search-space narrowing claim (Claim 7) to motivate why teams should invest in STPA training for automated system design. The concrete numbers (33-box dataflow → 4-box control structure analysis) provide a quantitative rationale. The training challenges (Claims 8–9) should inform any "adopting STPA" recommendations — make clear that classroom training alone is insufficient and must be paired with structured practice on real systems.

- **Chapter — SRE Training / Adoption (emerging chapter)**: This is the primary impact. The full training evolution arc provides a replicable, phased model for any organization adopting STPA. Specific recommendations: (1) start with software-specific examples, not physical-system cases; (2) use a shared worked example rather than asking each participant to model their own system; (3) lead with the feedback-path framing as the motivational hook; (4) offer short orientation sessions before multi-day workshops to self-select for commitment; (5) pair training with template-driven homework so participants apply STPA to their own systems; (6) use the training pipeline as a vehicle to identify future STPA champions. The self-serve video model (Claim 10) is the most mature form and should be the recommended target state.

## Extraction Notes

- Source read in full (the complete HTML article at https://sre.google/stpa/teaching/, fetched and read end-to-end 2026-07-27). No sub-pages were followed — the article is self-contained. No paywall; the page is public.
- All `Quote` fields were copied character-for-character from the fetched page content. Where the source uses `&ndash;` for em-dashes or `&gt;` for special characters, these were transcribed to their rendered equivalents in the output so quotes remain readable; no words were added, removed, or reordered within a quoted passage. Quotes were verified against the raw HTML.
- `date_published` is approximate — the page carries no explicit publication date. Training began in 2021; the narrative describes multi-year evolution ending with the self-serve curriculum as "the latest phase." Estimated 2026 based on site activity (nav references to "Ask an SRE at Next '26") and the maturity of the training program described.
- The 10 candidate paths from `miner-related-notes.md` (pre-computed lexical retrieval) were read and vetted. All candidates with score < 0.22 are explicitly dismissed as not intersecting with STPA training methodology: `docs-google-sre-prodcast-03-06-incident-response-tooling.md` (incident response tooling), `docs-google-sre-prodcast-02-08-life-beyond-google.md` (Google vs non-Google SRE), `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` (AI for SRE), `docs-google-sre-prodcast-03-05-building-reliable-systems.md` (database reliability), `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` (SLOs), `docs-google-sre-handling-overload.md` (load shedding), `docs-google-sre-prodcast-03-11-embracing-complexity.md` (human factors/complexity — adjacent systems thinking but does not mention STPA, training, or control structures), and `docs-google-sre-reliable-product-launches.md` (launch coordination). Three candidates were cited as cross-references: `docs-google-sre-prodcast-04-07-stpa.md` (the existing STPA methodology note — direct overlap), `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` (STPA Claim 15), and `docs-google-sre-prodcast.md` (index listing S4E7).
- The existing STPA note (`docs-google-sre-prodcast-04-07-stpa.md`) was re-read and every cross-reference claim number verified per MINER.md §4b: Claim 12 (broken feedback mechanisms) confirmed at line 114; Claim 8 (20% STPA) confirmed at line 91; Claim 6 (road-closures example) confirmed at lines 76–78.
- `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` Claim 15 was re-read and verified at lines 269–290.
- No contradiction surfaces against any existing source note. No contradiction issue is filed.
