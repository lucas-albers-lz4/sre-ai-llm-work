---
source_url: https://sre.google/workbook/postmortem-analysis
source_type: documentation
title: "Results of Postmortem Analysis — SRE Workbook Appendix C"
author: "Google SRE (Site Reliability Engineering Workbook, O'Reilly, 2018)"
date_published: 2018
date_extracted: 2026-08-12
last_checked: 2026-08-12
status: current
confidence_overall: settled
issue: "#882"
---

# Results of Postmortem Analysis — SRE Workbook Appendix C

> The empirical backbone for the guide's postmortem and change-management content: Google's standard postmortem template is what makes trend analysis possible, and the appendix's two aggregate tables (2010–2017) show that pushes trigger most outages (binary push 37%, configuration push 31%) while root causes are dominated by software (41.35%) and development process failure (20.23%). The first quantitative trigger/root-cause breakdown in the corpus, and the data behind the canarying note's qualitative "majority of incidents" claim.

## Source Context

- **Type**: documentation — Appendix C ("Results of Postmortem Analysis") of the Site Reliability Engineering Workbook (O'Reilly, 2018), hosted on sre.google, licensed CC BY-NC-ND 4.0.
- **Author credibility**: Highest credibility. Published through Google's official SRE channel; the appendix aggregates Google's own postmortem data ("a sample of thousands of postmortems"). It is the appendix that Chapter 16 (Canarying Releases) cites for the "majority of incidents are triggered by binary or configuration pushes" claim.
- **Scope**: Two quantitative tables only — (1) Table C-1, the top eight outage triggers 2010–2017, and (2) Table C-2, the top five root-cause categories — plus the one-sentence enabling mechanism: a standard postmortem template that consistently captures root cause and trigger, enabling trend analysis that targets systemic root-cause types. The standard template it links to (SRE Book Appendix D, Example Postmortem) was followed for context. It does **not** cover postmortem culture, blamelessness, or when-to-write criteria (those are SRE Prodcast S1E09, already extracted).

## Extracted Claims

### Claim 1: Google's standard postmortem template consistently captures the incident root cause and trigger, and this consistent capture is what enables trend analysis across postmortems
- **Evidence**: The appendix's opening sentence, stated as the purpose of the standard template.
- **Confidence**: settled
- **Quote**: "At Google, we have a standard postmortem template that allows us to consistently capture the incident root cause and trigger, which enables trend analysis."
- **Our assessment**: The enabling mechanism behind the appendix's data, and the transferable practice: the value of a postmortem program is not the individual documents but the consistent, machine-aggregatable schema (root cause + trigger as separate fields). This is the schema requirement an AI postmortem-drafting or incident-analysis tool must satisfy to feed trend analysis — consistent structured capture, not prose. It corroborates the S1E09 claim that a critical mass of postmortems enables pattern identification.

### Claim 2: Google uses the trend analysis to target improvements at systemic root-cause types, such as faulty software interface design or immature change deployment planning
- **Evidence**: The appendix's stated use of the aggregate data.
- **Confidence**: settled
- **Quote**: "We use this trend analysis to help us target improvements that address systemic root-cause types, such as faulty software interface design or immature change deployment planning."
- **Our assessment**: This is the "so what" of the whole appendix: the data is consumed as a targeting signal for systemic (process/design-level) fixes, not as a scorecard. For an LLM-ops context, "immature change deployment planning" as a named systemic type is a direct mandate for change-management discipline (canarying, gated rollouts) as the fix for the push-dominated trigger distribution.

### Claim 3: The trigger distribution covers thousands of postmortems over 2010–2017, so the percentages are historical and directional, not a current-state benchmark
- **Evidence**: The appendix's description of the sample underlying Table C-1.
- **Confidence**: settled
- **Quote**: "Table C-1 shows the breakdown of our top eight triggers for outages, based on a sample of thousands of postmortems over the last seven years."
- **Our assessment**: The honest framing the Prospector flagged: the data predates the LLM era (2010–2017) and is Google-specific. The claims it supports (pushes dominate triggers; software/development-process dominate root causes) are structural and evergreen, but any guide use must cite the percentages as directional, not as a current reliability benchmark.

### Claim 4: The top eight outage triggers are dominated by pushes — binary push 37%, configuration push 31%, user behavior change 9%, processing pipeline 6%, service provider change 5%, performance decay 5%, capacity management 5%, hardware 2% — i.e., binary + configuration pushes together account for 68% of the trigger distribution
- **Evidence**: Table C-1, verbatim figures.
- **Confidence**: settled
- **Quote**: "Table C-1. Top eight outage triggers, 2010–2017" with rows "Binary push 37%", "Configuration push 31%", "User behavior change 9%", "Processing pipeline 6%", "Service provider change 5%", "Performance decay 5%", "Capacity management 5%", "Hardware 2%".
- **Our assessment**: The quantitative version of the canarying note's qualitative claim (see Cross-References). The headline number for change-management investment is that 68% of the trigger distribution is push-driven (binary 37% + configuration 31%) — the strongest empirical argument the corpus has for gating, canarying, and automating change. "User behavior change" at 9% is a reminder that not all outages are change-driven.

### Claim 5: The top five root-cause categories are software 41.35%, development process failure 20.23%, complex system behaviors 16.90%, deployment planning 6.74%, and network failure 2.75% — so software plus the software-development process account for over 61% of root causes
- **Evidence**: Table C-2, verbatim figures.
- **Confidence**: settled
- **Quote**: "Table C-2. Top five root-cause categories for outages" with rows "Software 41.35%", "Development process failure 20.23%", "Complex system behaviors 16.90%", "Deployment planning 6.74%", "Network failure 2.75%".
- **Our assessment**: The root-cause taxonomy is the appendix's second novel contribution — it names the categories an incident-analysis pipeline should classify into. Software (41.35%) plus development process failure (20.23%) = 61.58%, meaning the dominant root-cause cluster is in the software delivery chain, not infrastructure/hardware (network failure is only 2.75%). For LLM ops, this supports treating model/prompt/gateway code as the primary root-cause surface for AI incidents.

### Claim 6: "Complex system behaviors" is Google's third-largest named root-cause category (16.90%), giving empirical, quantified weight to the complexity-reduces-reliability theme
- **Evidence**: Table C-2 row "Complex system behaviors 16.90%".
- **Confidence**: settled
- **Quote**: "Complex system behaviors 16.90%" (Table C-2).
- **Our assessment**: A citable datapoint for the guide's Ch00 complexity principle: complex systems are a first-class root-cause category in Google's own taxonomy, distinct from software bugs and from human process failure. Combined with the embracing-complexity corpus (Claims 14/16), this moves complexity from a philosophical theme to a measured category of failure — 16.90% of root causes in thousands of postmortems.

## Concrete Artifacts

### Artifact A — Table C-1: Top eight outage triggers, 2010–2017 (verbatim)

```
Binary push                    37%
Configuration push             31%
User behavior change            9%
Processing pipeline             6%
Service provider change         5%
Performance decay               5%
Capacity management             5%
Hardware                        2%
```
*Source: https://sre.google/workbook/postmortem-analysis — Table C-1, copied verbatim.*

### Artifact B — Table C-2: Top five root-cause categories for outages (verbatim)

```
Software                       41.35%
Development process failure    20.23%
Complex system behaviors       16.90%
Deployment planning             6.74%
Network failure                  2.75%
```
*Source: https://sre.google/workbook/postmortem-analysis — Table C-2, copied verbatim.*

### Artifact C — The standard postmortem template the appendix links to (SRE Book Appendix D, Example Postmortem)

The appendix's "standard postmortem template" links to the SRE Book's worked example (https://sre.google/sre-book/example-postmortem/). Its section structure — the consistent-capture schema that enables trend analysis:

```
Summary
Impact
Root Causes
Trigger
Resolution
Detection
Action Items
Lessons Learned (what went well / what went wrong / where we got lucky)
Timeline
```
*Source: followed link from the appendix intro; https://sre.google/sre-book/example-postmortem/ (Shakespeare Sonnet++ postmortem, incident #465).*

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3077) — **Corroborates** Claim 6 here (complex system behaviors as a root-cause category) with **Claim 16** (interesting large outages involve interactions between powerful, complex systems that had to be complex to handle heterogeneity — you can't predict or prevent these interactions) and **Claim 14** (complex systems fail in surprising, nonlinear ways; reductive linear cause-effect thinking makes you solve the wrong problem). The appendix quantifies (16.90%) what the Prodcast argues conceptually: complexity is a distinct, measurable root-cause type.

2. **`docs-google-sre-configuration-specifics.md`** (score 0.2821) — **Corroborates/Extends** via **Claim 13** (hermetic config evaluation; "configuration bugs may be discovered at runtime, which is too late"). Table C-1's "Configuration push 31%" is the incident-frequency justification for the config-as-code/hermeticity/DSL discipline the chapter prescribes — a 31% trigger share is exactly why configuration must be treated as code with evaluation-time validation.

3. **`docs-google-sre-eliminating-toil.md`** (score 0.2564) — **Dismissed.** Covers toil definition/measurement. No outage-trigger or root-cause-taxonomy claims to corroborate or contradict.

4. **`docs-google-sre-on-call.md`** (score 0.2564) — **Dismissed.** Covers pager load, response-time tiers, and alert hygiene. No trigger-distribution or root-cause content.

5. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2564) — **Dismissed.** AI-for-SRE tooling (outage detection, ticket analysis, golden data sets). No postmortem-data claims.

6. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2308) — **Dismissed.** SLOs as shared vernacular. No overlap with trigger/root-cause distributions.

7. **`docs-google-sre-data-processing-pipelines.md`** (score 0.2308) — **Dismissed.** Pipeline data-freshness/correctness SLOs. The appendix's "Processing pipeline" trigger (6%) shares only the word "pipeline."

8. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2308) — **Corroborates** Claim 2 here (trend analysis targeting systemic root-cause types) with **Claim 5** (tooling roadmap should come from a meta-retrospective — aggregating many postmortems to find common pain, targeting the 80% majority). Same learning-loop thesis: aggregate postmortems to find systemic patterns; the appendix is Google's aggregate-output example of that method at full scale.

9. **`docs-google-sre-handling-overload.md`** (score 0.2308) — **Dismissed.** Load shedding, capacity reserves, retries. No overlap with outage-trigger taxonomy.

10. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2308) — **Dismissed.** SRE concepts outside Google / scale shock. No overlap.

### Primary cross-references (from the Prospector's triage and manual search)

- **Corroborates**:
  - `docs-google-sre-canarying-releases.md` **Claim 4** ("In Google's experience, a majority of incidents are triggered by binary or configuration pushes (see Results of Postmortem Analysis)") — this appendix is the source cited by that claim. This note mines the data behind it (68% push-driven trigger share, Claim 4 here) without restating the qualitative claim as new; per the triage, the two notes are complementary rather than a duplicate.
  - `docs-google-sre-prodcast-01-09-postmortems.md` **Claim 2** (postmortem data is the prioritization input for reliability investment — "postmortem is our tool to learn from our failures") and **Claim 11** (a critical mass of postmortems enables pattern identification). The appendix is Google's concrete realization of both: thousands of postmortems aggregated into a targeting signal for reliability investment. This appendix supplies the quantified aggregate that S1E09 describes as the mechanism.
  - `docs-google-sre-anatomy-of-an-incident.md` **Claim 9** (root cause vs. trigger distinction — the system hazard vs. the environmental shift that turns it into an incident). The appendix's template captures root cause and trigger as separate, consistently-coded fields — the operational implementation of that conceptual distinction, and the reason the two tables exist separately.
  - `docs-google-sre-incident-management-guide.md` **Claim 14** (aggregating structured data across many postmortems in larger organizations enables identification of trends and areas needing larger investment). The appendix is Google's public aggregate-output example of exactly this practice.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 5** — see Candidates list above.

- **Contradicts**: None identified, and no contradiction issue filed. The appendix is a data table and a mechanism statement; it agrees with every corpus claim it touches. Checked and resolved as conditioning rather than contradiction: the 68% push-driven trigger figure coexists with the "user behavior change 9%" and "performance decay 5%" rows — i.e., "majority of incidents are push-triggered" (canarying Claim 4) is a statement about the *distribution*, not an assertion that all incidents are change-driven.

- **Extends**:
  - `docs-google-sre-incident-metrics-in-sre.md` **Claim 8** (reject MTTx for evaluating reliability trends; tailor metrics to specific questions). The appendix's category-based percentage breakdown is an instance of the recommended alternative — it evaluates *what kind* of incident, rather than averaging durations of high-variance aggregates. The appendix shows the categorical analysis the MTTx note argues for.
  - `docs-google-sre-canarying-releases.md` **Claim 4** — adds the actual percentages behind the canarying note's qualitative citation.

- **Novel**:
  - **The full Table C-1/C-2 quantitative breakdowns** (Claims 4–5, Artifacts A–B) — no existing source note carries the actual trigger/root-cause percentages; the canarying note cites the appendix without the data.
  - **The standard-template → trend-analysis mechanism** (Claims 1–2) — the requirement that root cause and trigger be captured as consistent structured fields so the corpus can be aggregated; the schema requirement for AI postmortem/incident-analysis tooling.
  - **"Complex system behaviors" as a named, measured root-cause category** (Claim 6) — the quantified complexity datapoint for the guide's Ch00 complexity principle.
  - **The root-cause category taxonomy** (Claim 5) — software / development process failure / complex system behaviors / deployment planning / network failure as a classification schema for an incident-analysis pipeline.

## Guide Impact

- **Chapter 01 (Incident Response) — Postmortems section**: The section currently covers contents, when-to-write, structure, blamelessness, review, and sharing, but has no trend-analysis content. Add: (a) the standard-template requirement — postmortems must capture root cause and trigger as consistent, structured fields so the corpus can be aggregated (Claim 1), which is the schema an AI postmortem drafter should be prompted to fill; (b) the trend-analysis loop — aggregate the corpus to target systemic root-cause types (Claim 2), matching the S3E06 meta-retrospective method already referenced; (c) the root-cause category taxonomy (Claim 5) as the classification vocabulary for AI-assisted incident analysis.

- **Chapter 00 (Principles)**: Add to rule 6 (change is the dominant incident source, citing canarying Claim 4) the actual figures behind it — binary push 37% + configuration push 31% = 68% of the trigger distribution (Claim 4). Add "complex system behaviors" at 16.90% (Claim 6) as the quantified complexity-reduces-reliability datapoint, distinct from software and process root causes.

- **Chapter 05 (LLM Ops Reliability / Change Management)**: Use the 68% push-driven figure (Claim 4) and "immature change deployment planning" as a systemic root-cause type (Claim 2) as the investment rationale for gated, canaried model/prompt/gateway change — the LLM-era instantiation of the push-driven distribution.

- **Chapter 02 (Observability / Trend analysis)**: Add the structured-postmortem-data → trend-analysis pattern (Claims 1–2) and the category taxonomy (Claim 5) as the analysis model for aggregated incident data — the appendix is the canonical example of category-based (not MTTx-based) incident analytics.

## Extraction Notes

- The source is a deliberately thin page — a two-table appendix with one mechanism paragraph. Extraction therefore concentrates the claims on the enabling mechanism (Claims 1–3), the trigger distribution (Claim 4), the root-cause distribution (Claim 5), and the complexity datapoint (Claim 6), plus the two tables as verbatim concrete artifacts. Depth was not diluted into paraphrase; every quantitative claim is traceable to a specific table row.
- The appendix's "standard postmortem template" link (SRE Book Appendix D, Example Postmortem) was followed per MINER.md; its section structure is captured as Artifact C. No other sub-pages were followed — the appendix has no other substantive links.
- All `Quote` fields are copied character-for-character from the fetched appendix text. Table rows are quoted as their exact "label percentage" strings; the table headers ("Table C-1. Top eight outage triggers, 2010–2017", "Table C-2. Top five root-cause categories for outages") are quoted verbatim. The SRE Book example postmortem page is a different document (different site section) and is used only for the template structure in Artifact C, with clear attribution.
- `confidence_overall` is `settled`: the source is the canonical Google SRE Workbook appendix, first-party data ("a sample of thousands of postmortems"), hosted on sre.google. The 2018 publication date is treated as evergreen per the established `sre-workbook` seed precedent (same handling as `docs-google-sre-configuration-specifics`, `docs-google-sre-canarying-releases`), with the data itself explicitly framed as historical/directional (Claim 3).
- No contradiction issue was filed (see Cross-References → Contradicts).
