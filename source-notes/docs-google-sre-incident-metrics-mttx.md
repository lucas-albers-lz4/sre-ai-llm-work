---
source_url: https://sre.google/static/pdf/IncidentMeticsInSre.pdf
source_type: docs
title: "Incident Metrics in SRE — Critically Evaluating MTTR and Friends"
author: "Štěpán Davidovič (Site Reliability Engineer, Google)"
date_published: 2021-03-19
date_extracted: 2026-07-30
last_checked: 2026-07-30
status: current
confidence_overall: settled
issue: "#662"
---

# Incident Metrics in SRE — Critically Evaluating MTTR and Friends

> A primary-source O'Reilly research report from a Google SRE that provides the rigorous
> statistical and empirical foundation for why MTTx metrics (MTTR, MTTM, etc.) are unfit
> for incident trend analysis or decision-making — incident durations follow a high-variance,
> positively skewed distribution, making summary statistics unreliable at typical incident
> volumes. Proposes alternative measurement approaches: tailoring metrics to specific
> questions, SLI/SLO-based direct reliability indicators, user studies on selected incident
> samples, and simulation-based validation of any chosen metric.

## Source Context

- **Type**: docs — O'Reilly research report (36 pages, PDF format), published in collaboration with
  Google SRE. First edition, March 2021. This is a primary research publication, not a blog post,
  vendor content, or secondary summary.
- **Author credibility**: Štěpán Davidovič is a Site Reliability Engineer at Google, working on
  internal infrastructure for automatic monitoring. Previous roles include developing the Canary
  Analysis Service and working on AdSense reliability and shared infrastructure projects. The
  report was reviewed by Kathy Meier-Hellstern, Ben Appleton, Michael Brundage, Scott Williams,
  and Cassie Kozyrkov — all statisticians or SRE practitioners at Google. Highest credibility
  for the statistical analysis claims.
- **Scope**: Statistical analysis of incident duration distributions across four data sets (three
  public companies' incident dashboards + Google internal incident data). Uses Monte Carlo
  simulation to demonstrate why MTTx fails for trend analysis and decision-making. Evaluates
  alternative statistics (median, geometric mean, percentiles). Explores the Google data set
  separately for scale effects. Proposes alternative measurement approaches. Does NOT cover:
  incident prevention, on-call practices, tooling design, AI/LLM operations, specific SLO
  implementation, or incident response process guidance. The analysis is purely at the aggregate
  statistics level.

## Extracted Claims

### Claim 1: Incident durations across four independent data sets follow a positively skewed, high-variance distribution (roughly log-normal), with most incidents resolving quickly while a long tail of complex events dominate the aggregate
- **Evidence**: Empirical incident data from three public company dashboards (Company A: N=798,
  Company B: N=350, Company C: N=2,186) and Google's internal data set (several times larger
  than any public set). All show positively skewed distributions with huge variance. Q-Q plots
  show distributions approach log-normal (or gamma). The standard deviations (5h 16m, 5h 1m,
  6h 53m) are roughly double the means (2h 26m, 2h 31m, 4h 31m).
- **Confidence**: settled
- **Quote**: "The key observation is that the incidents follow a positively skewed distribution in each case, with the majority of incidents resolving quickly."
- **Our assessment**: This is the foundational empirical claim on which the entire report rests. The data is solid — drawn from real incident dashboards plus Google internal data, with consistent patterns across four independent sources. The roughly 2:1 standard-deviation-to-mean ratio is particularly striking as a rule-of-thumb metric for practitioners assessing their own incident data.

### Claim 2: Monte Carlo simulation shows that MTTR cannot reliably detect a 10% reduction in incident durations at typical annual incident volumes — 38–40% of simulations show MTTR worsening even when incidents are actually shorter
- **Evidence**: 100,000-run Monte Carlo simulation. At 2019 incident counts (Company A: 173,
  Company B: 103, Company C: 609), even with an actual 10% shortening applied to every incident,
  38% of Company A simulations showed MTTR getting worse, 40% for Company B, and 20% for
  Company C — far exceeding the 10% false-positive tolerance threshold.
- **Confidence**: settled
- **Quote**: "Yikes! Even though in the simulation the improvement always worked, 38% of the simulations had the MTTR difference fall below zero for Company A, 40% for Company B, and 20% for Company C."
- **Our assessment**: Mathematically rigorous and reproducible. The simulation methodology is explicitly described (random sampling, 100,000 iterations, 50/50 split, 10% duration reduction) and could be replicated by any team with their own incident data. This is the strongest single claim in the report — it directly refutes the assumption that MTTR trends are a reliable signal.

### Claim 3: Even with no actual change to incidents, MTTR can show large "improvements" purely by chance — a useless product would appear to deliver ≥30-minute MTTR improvement 19% of the time for a typical company
- **Evidence**: Identical Monte Carlo simulation but with NO duration change applied (the "product does nothing" condition). For Company A, 19% of simulations showed ≥30-minute apparent MTTR
  improvement; Company B: 23%; Company C: 10%.
- **Confidence**: settled
- **Quote**: "there's a 19% chance that there is a half-hour improvement (or better) of MTTR in Company A... even though in this simulation, you did not change anything about the incidents."
- **Our assessment**: Devastating for the use of MTTR as a decision metric. The author makes the
  point explicit with a memorable aside: "A cynical response to this finding would be to start
  selling a fake incident-shortening product." The practical implication is that even a randomly
  fluctuating MTTR can drive wrong purchasing decisions.

### Claim 4: Neither median, geometric mean, nor high percentiles (95th) rescue the problem — all summary statistics fail at typical incident volumes due to the fundamental variance-to-sample-size ratio
- **Evidence**: Tables 3 (median), 4 (95th percentile), and 5 (geometric mean) show 90% confidence intervals from 100,000 simulations at N=10, N=100, and N=1,000. At Company C (best data set), 90% CI for median at N=1,000 is ±29 minutes on a 2h 50m median. The 95th percentile performs worst:
  90% CI of ±12h 30m at N=100 on a 12h 59m baseline.
- **Confidence**: settled
- **Quote**: "The difficulty is not specific to the 'mean' in MTTR; median TTR isn't helping us either."
- **Our assessment**: Exhaustive and convincing. The author systematically checks every plausible
  alternative summary statistic and shows each fails. The 95th percentile failure is particularly
  striking — the metric most relevant to worst-case-incident analysis has the worst statistical
  performance. This closes the escape hatch of "just use median/percentile instead."

### Claim 5: Even at Google's massive incident volume (15× the largest public data set), MTTR can only detect a ~5.3% change after a full year of data — and the heterogeneity of incidents makes the result practically meaningless
- **Evidence**: Google internal data: for "all significant incidents" (15× the count of user-facing
  incidents), 90% CI after one year is ±5.3% of MTTR. For "most severe incidents" only: ±18%
  after one year. Incident types range from user-facing serving failures to corporate device
  software installations — the author notes "I have no practical development that would promise
  this level of incident duration reduction over such a wide gamut of incidents."
- **Confidence**: settled
- **Quote**: "The ability to confidently detect changes as 'small' as 5.3% in the mean after a year's worth of incidents is not strengthening MTTR's position as a practically useful incident statistic."
- **Our assessment**: This closes the "just get more data" escape hatch. Even Google — with
  vastly more incidents than any single team — cannot get useful signal from MTTR in less than
  a year. And a year's worth of heterogeneous incidents from a large company means the detected
  "improvement" can't be attributed to any specific change. The ±18% CI for severe incidents
  (the ones that matter most) is especially damning.

### Claim 6: Improving incident data quality (metadata accuracy, more stringent reporting) does not materially improve MTTx analysis — the problem is structural, not data-quality
- **Evidence**: Google-internal comparison of teams with more stringent incident-reporting
  expectations (SRE-supported, highest-availability services) showed no major improvement in
  analysis. All three public data sets show the same behavior regardless of how meticulously
  incidents were recorded. Author also validated by generating synthetic distributions.
- **Confidence**: settled
- **Quote**: "The challenge in aggregate incident analysis does not appear to be about incident metadata quality. The efforts to improve the accuracy of metadata collection are unlikely to cause any dramatic changes."
- **Our assessment**: Closes another escape hatch. A common response to MTTR critique is "our
  data is just poor quality — if we track it better, MTTR will work." This claim directly
  refutes that. The author's Google-internal access provides unique authority here: he can
  compare teams with different reporting rigor within the same company.

### Claim 7: MTTx is unsuitable for three common SRE purposes — measuring overall system reliability, detecting trends in incident-response practices, and evaluating the success of process/tooling changes
- **Evidence**: The "And That's Why MTTx Will Probably Mislead You" section enumerates three
  specific failures, each backed by the preceding simulation analysis. First: doubling incident
  count while keeping the same distribution worsens reliability but leaves MTTR unchanged
  (citing Hidalgo, *Implementing Service Level Objectives*). Second: simulations show the
  variance in observed MTTR masks any real trend. Third: the variance makes it impossible to
  distinguish improvement from noise, and MTTR can worsen even while incidents improve.
- **Confidence**: settled
- **Quote**: "It is a poor measure of the overall reliability of your system... It does not provide any useful insights into the trends in your incident-response practices... Improvements in incident management processes or tooling changes cannot have their success or failure evaluated on MTTx."
- **Our assessment**: Synthesizes the simulation results into actionable guidance. Each of the
  three failures is independently demonstrated by the simulation data. The first point (doubling
  incident count = worse reliability, but MTTR unchanged) is a particularly crisp argument for
  why MTTR is fundamentally the wrong axis.

### Claim 8: Two exceptions exist where MTTx analysis can work: (a) massive homogeneous quantities with lower variance (e.g., Backblaze's tens of thousands of disk drives) and (b) truly dramatic changes (~80% duration reduction) that would be detectable by many methods anyway
- **Evidence**: Author cites Backblaze's hard drive reliability statistics as an example where
  tens of thousands of units per model enable valid aggregate statistics. Notes that a dramatic
  80% reduction in incident duration would be confidently detectable — but would also be
  detectable by many other means, making MTTx unnecessary.
- **Confidence**: settled
- **Quote**: "One exception would be if you have quantities that enable aggregate MTTx analysis. A real example is a large-scale hardware purchase, such as hard disk drives."
- **Our assessment**: Important boundary condition that prevents over-generalization. The "catch
  with fire" exception confirms the rule: if the change is big enough to see via MTTR, you
  don't need MTTR to see it. The disk-drive counterexample is also instructive for
  differentiating component-level metrics (which can work with massive homogeneous N) from
  incident-level metrics (which cannot).

### Claim 9: The recommended alternative approach is to "tailor the metric to the question" — narrow the analysis to specific incident-lifecycle phases, use user studies on selected incident samples, and consider direct SLI/SLO-based reliability indicators
- **Evidence**: The "Better Analysis Options" section proposes: (a) identify the specific step
  of the incident lifecycle a change targets and measure only that step; (b) conduct user
  studies on a select sample of incidents for richer understanding than any aggregate can
  provide; (c) use SLIs/SLOs as direct reliability indicators rather than incident summary
  statistics. Author notes he found no "silver bullet" metric to replace MTTx.
- **Confidence**: emerging (practical recommendations, not empirically validated in the report)
- **Quote**: "Perhaps your question is, 'Is our reliability getting better or worse, as a company?' This is where the concept of availability comes in. In SRE practice, the familiar language for this would be service level indicators (SLIs) and service level objectives (SLOs)."
- **Our assessment**: These are sensible recommendations but less rigorously supported than the
  critique portion of the report. The "no silver bullet" honesty is refreshing and important —
  the author is not selling a replacement metric, he's advocating for critical thinking about
  metrics. The user-studies recommendation (citing Steve Krug's *Rocket Surgery Made Easy*) is
  notably concrete and low-cost.

### Claim 10: The same Monte Carlo simulation methodology can and should be applied to test any candidate incident metric before adoption — "whatever metric you choose to use, it is important to test that it can give you robust insights regardless of the shape of the incident duration distribution"
- **Evidence**: Concluding methodological recommendation: determine what level of change is
  meaningful, then use simulation (easily done with Python + CSV or SQL) to test whether the
  metric can confidently detect it. The report's simulation framework is fully described
  (five-step process, 100,000 iterations, two-sample split).
- **Confidence**: settled
- **Quote**: "The same tools that I've used to investigate MTTx can be used for another metric you might be considering. The process is much the same: determine what level of change is meaningful to you (this depends on the metric, but also on your business), and then analyze whether you can confidently see it in the data."
- **Our assessment**: The most actionable recommendation in the report for practitioners. The
  simulation framework is simple enough that any team with incident data and basic scripting
  skills can apply it. This is the constructive counterpart to the report's critical analysis.

## Concrete Artifacts

### Key data set statistics (verbatim from Tables 1 and accompanying text)

```
Table 1: Incident count, mean, and variance across the three public data sets.

                    Company A    Company B    Company C
Incidents (all)     779          348          2,157
Incidents (2019)    173          103          609
Mean TTR            2h 26m       2h 31m       4h 31m
Standard deviation  5h 16m       5h 1m        6h 53m
```
*Source: Davidovič, "Incident Metrics in SRE," Table 1, p. 9.*

### 90% confidence intervals for MTTR difference at N=10, N=100, N=1,000 (verbatim from Table 2)

```
90% CI for difference of two MTTRs (N1 = N2, 100,000 simulations):

                    Company A          Company B          Company C
N1+N2 = 10          [-5h41m; +5h42m]   [-5h25m; +5h18m]   [-7h4m; +7h15m]
N1+N2 = 100         [-1h44m; +1h44m]   [-1h39m; +1h39m]   [-2h16m; +2h16m]
N1+N2 = 1,000       [-33m; +33m]       [-31m; +31m]       [-43m; +43m]
```
*Source: Davidovič, "Incident Metrics in SRE," Table 2, p. 13.*

### 90% confidence intervals for median TTR at N=10, N=100, N=1,000 (verbatim from Table 3)

```
90% CI for difference of two median TTRs (N1 = N2, 100,000 simulations):

                    Company A          Company B          Company C
N1+N2 = 10          [-1h46m; +1h46m]   [-2h13m; +2h12m]   [-4h8m; +4h7m]
N1+N2 = 100         [-29m; +29m]       [-29m; +29m]       [-1h20m; +1h19m]
N1+N2 = 1,000       [-11m; +11m]       [-9m; +9m]         [-29m; +29m]
```
*Source: Davidovič, "Incident Metrics in SRE," Table 3, p. 15.*

### Google data set — 90% CI for MTTR and median at various time windows (verbatim from Table 7)

```
90% CI for difference of two MTTRs and median TTRs (N1 = N2, 100,000 simulations):

                    Most severe incidents    All significant incidents
                    (often user-facing)      (often not user-facing)
Mean TTR
  ¼ year             ±35% of MTTR             ±11% of MTTR
  ½ year             ±25% of MTTR             ±7.6% of MTTR
  1 year             ±18% of MTTR             ±5.3% of MTTR

Median TTR
  ¼ year             ±53% of median TTR       ±20% of median TTR
  ½ year             ±35% of median TTR       ±14% of median TTR
  1 year             ±25% of median TTR       ±10% of median TTR
```
*Source: Davidovič, "Incident Metrics in SRE," Table 7, p. 23.*

### 90% CI for total incident duration sum (verbatim from Table 6)

```
90% CI for difference of two incident duration sums (N1 = N2, 100,000 simulations):

                    Company A          Company B          Company C
N1+N2 = 100         [-87h; +87h]       [-82h; +82h]       [-113h; +113h]
N1+N2 = 1,000       [-275h; +274h]     [-260h; +259h]     [-359h; +357h]
```
*Source: Davidovič, "Incident Metrics in SRE," Table 6, p. 17.*

### The Monte Carlo simulation procedure (verbatim from source)

```
1. Randomly draw two samples, with size N1 and N2 (where N1 = N2 to get a
   perfect 50/50 split), from the empirical distribution of incident durations.
2. Modify the incident durations in one of the populations, in this case by
   shortening it by 10%.
3. Calculate MTTR for each of the groups, i.e., MTTR_modified and
   MTTR_unmodified.
4. Take the difference, observed improvement = MTTR_unmodified − MTTR_modified.
5. Repeat this process 100,000 times.
```
*Source: Davidovič, "Incident Metrics in SRE," p. 8–9. The author notes this can be done with "a Python script and a CSV file with the data or a sufficiently capable SQL engine."*

### The three failures of MTTx (verbatim from source)

```
"It is a poor measure of the overall reliability of your system."
  — if you doubled the incident count while the incidents follow roughly the
    same distribution, your reliability has worsened but your metric hasn't
    changed much.

"It does not provide any useful insights into the trends in your
 incident-response practices."
  — simulations showed the amount of change you can see even if nothing
    changed about the nature of your incidents.

"Improvements in incident management processes or tooling changes cannot
 have their success or failure evaluated on MTTx."
  — the variance makes it difficult to distinguish any such improvement, and
    the metric might worsen despite the promised improvement materializing.
```
*Source: Davidovič, "Incident Metrics in SRE," p. 25.*

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 15** — Butt states "as an industry, we're moving away from MTTR right now as the single be-all and end-all metric." Davidovič's report provides the rigorous statistical foundation that the Prodcast episode cites only as a trend signal. Direct corroboration of the directional claim, with the primary evidence the Prodcast note lacked.
  - `docs-google-sre-prodcast-06-01.md` **Claim 2** — Clint Byrum states "Stepan Davidovic killed it" and describes the Monte Carlo simulations secondhand (citing the same PDF mined in this note). This note IS the primary source that Prodcast S6E01 pointed to. The Prodcast note explicitly says "the Smith should cite Davidovic's actual paper for the math before treating the mechanism as settled" — this source note fulfills that deferred citation.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` **Claim 13** — Singer calls MTTR "a pretty poor proxy for the actual customer experience." Davidovič's report provides the statistical mechanics behind that judgment.
  - `docs-google-sre-prodcast-04-02-data-centers.md` **Claim 6** — Steve McGhee critiques MTTR/MTBF at fleet scale, noting failures are "novel and non-normal." Davidovič's distributional analysis (positively skewed, log-normal-approaching) provides the mathematical characterization of that non-normality. The data-centers note's caveat — "at the component layer MTTR/MTBF still earn their keep" — matches Davidovič's own Backblaze-disk-drive exception (Claim 8 in this note).
  - `docs-google-sre-twenty-years-lessons.md` **Claim 9** — Recommends automating mitigations "to reduce MTTR." This is not a contradiction (see below) but rather uses "reduce MTTR" in the colloquial sense of "shorten incident durations," which Davidovič's report does not dispute. Both sources agree shorter incidents are desirable; Davidovič shows MTTR is a poor tool for measuring whether you're achieving that.
  - `docs-google-sre-prodcast-05-07-crisis-engineering.md`, `docs-google-sre-prodcast-06-02-crisis-engineering.md` — Both critique simple metrics for crisis/incident response, consistent with Davidovič's statistical argument that aggregate measures mask meaningful variation.

- **Contradicts**: None filed. The apparent tensions are conditioning variables, not contradictions:
  - `discussion-google-sre-ben-treynor-interview.md` **Claim 13** (Treynor: availability = MTBF × MTTR, MTTR as component of reliability) vs. Davidovič's claim that MTTR is a poor reliability measure. These operate at different levels: Treynor uses MTTR at the *component/availability* level (a server either works or doesn't), while Davidovič attacks MTTR as an *aggregate/comparative* metric over heterogeneous incidents. The corpus already documents this split (data-centers Claim 6: "at the component layer MTTR/MTBF still earn their keep"). CONTRADICTIONS.md has no MTTR entry and no open `contradiction`-labeled issues exist, so no new contradiction issue is filed per MINER §4a ("When NOT to file": context difference already documented).
  - `blog-incidentio-ai-sre-incident-run.md` — Reports vendor claim of "up to 80% MTTR reduction" as a marketing assertion, not a statistical endorsement of MTTR's validity as a metric. The note itself assesses this as "anecdotal" and "provides no primary data." No genuine contradiction with Davidovič's mathematical analysis.

- **Extends**:
  - The multi-source MTTR-skeptic thread (`docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 15; `docs-google-sre-prodcast-06-01.md` Claims 2–4; `docs-google-sre-prodcast-04-02-data-centers.md` Claim 6; `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claim 13) — Davidovič's report is the *primary source* that all those notes point to or approximate secondhand. It provides the empirical data (four data sets), the simulation methodology (Monte Carlo framework), and the mathematical analysis (variance equations, CLT applicability limits) that the other notes reference but do not contain. This note is the analytical anchor for the entire MTTR-critique cluster in the corpus.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — Davidovič's recommendation to "tailor the metric to the question" (Claim 9 in this note) provides the positive prescription that complements the Prodcast episode's purely critical MTTR trend-claim (Claim 15).
  - `docs-google-sre-prodcast-06-01.md` — The Prodcast S6E01 note explicitly deferred to this PDF for the math. This note closes that citation gap.

- **Novel**: Material new to the corpus:
  - **The full Monte Carlo simulation framework** for testing incident metrics — a reproducible methodology any team can apply to their own data. No existing note provides this.
  - **The four-data-set empirical foundation** — Company A (N=798), Company B (N=350), Company C (N=2,186), and Google (15× larger). No existing note provides multi-company incident duration distributions with variance statistics.
  - **The quantitative failure of alternative statistics** — tables showing median, geometric mean, and 95th percentile 90% confidence intervals at N=10/100/1,000. No existing note has this data.
  - **Google-scale analysis** — showing even at 15× incident volume, only ~5.3% MTTR changes are detectable after a full year, and the heterogeneity makes it meaningless.
  - **Data quality refutation** — empirical evidence from Google that better incident reporting doesn't fix the statistical problem.
  - **The two exceptions** — Backblaze disk drives (massive homogeneous N) and dramatic changes (~80% reduction).
  - **The complete analytical approach section** — variance formulas, z-test derivation, CLT applicability limits for incident data, and the finding that CLT doesn't apply at fewer than ~3 months of incidents.
  - **The "three failures" framework** — a concise reference for why MTTx fails for three distinct SRE purposes.

## Guide Impact

- **Chapter 01 (Incident Response)**: Primary target. This report should anchor the guide's incident-metrics methodology section. Currently the guide has no rigorous treatment of why MTTx is misleading. Add: (a) the foundational distribution-of-incident-durations claim (Claim 1) with the multi-company evidence; (b) the Monte Carlo simulation framework as a reproducible methodology (Concrete Artifacts); (c) the "three failures" of MTTx (Claim 7) as the guide's reference for why teams should not default to MTTR; (d) the two exceptions (Claim 8) for nuance; (e) the alternative approaches (Claim 9), especially "tailor the metric to the question" and SLI/SLO-based indicators. Replace or augment any existing "MTTR as KPI" guidance with this source's evidence-based critique.

- **Chapter 02 (Observability / SLOs)**: Add the recommended alternative of SLI/SLO-based direct reliability indicators (Claim 9) as a better approach than incident summary statistics. The report's argument that "if you doubled incident count while keeping the same distribution, your reliability has clearly worsened but MTTR hasn't changed" is a crisp justification for SLO-based reliability measurement over incident-metric-based measurement.

- **Chapter 04 (On-call and Toil)**: Use the report's distributional analysis to inform on-call metric design: teams should not use MTTR/MTTM trends to evaluate on-call improvements. The simulation framework (Claim 10) provides a method for teams to test whatever metrics they do choose.

- **Chapter 05 (LLM Ops Reliability)**: The report's methodology is directly applicable to LLM incident analysis, where incidents may be even more heavy-tailed (long context windows, model idiosyncrasies, cascading failures from agent autonomy). The recommendation to "tailor the metric to the question" rather than defaulting to MTTR is especially relevant for evaluating LLM-specific incident-response tooling and automation investments.

## Extraction Notes

- The source is a 36-page O'Reilly PDF (5 MB). It was downloaded from the Google-hosted URL
  (https://static.googleusercontent.com/media/sre.google/en//static/pdf/IncidentMeticsInSre.pdf)
  and extracted to text using `pdftotext -layout`. The full extracted text (1,252 lines) was read
  end-to-end. Tables were verified against the layout-preserved text output and cross-checked
  against figure descriptions for numerical consistency.
- Table content was extracted as accurately as possible from the layout-preserved text. Column
  headers and row values were verified to match their visual presentation in the PDF. Some
  values listed as "obfuscated" in the Google data set (e.g., actual incident counts) are
  reported as relative sizes (15×, 1×) per the source's obfuscation.
- The Google data set amounts (Table 7) cannot be shared precisely as per the author's
  obfuscation. The note preserves the relative-comparison framing used in the source.
- `confidence_overall` is **settled**: the dominant claims are mathematical/statistical
  simulations confirmed across four independent data sets. The critique portion (Claims 1–8)
  is empirically demonstrated with reproducible methodology. The alternative recommendations
  (Claim 9) are labeled "emerging" at the individual claim level because they are practical
  proposals rather than tested prescriptions. The simulation methodology (Claim 10) is settled.
- The report is from March 2021 (pre-2025), but the underlying mathematical truths (log-normal
  distributions, variance of sample means, CLT applicability limits) are timeless. The specific
  data sets are historical but the distributional patterns are characteristic, not dated.
- No contradiction issue was filed. The apparent tension with Treynor's MTBF/MTTR framework is
  a conditioning variable (component-level vs. aggregate-level measurement), already documented
  as such in `docs-google-sre-prodcast-04-02-data-centers.md`. The tension with
  `blog-incidentio-ai-sre-incident-run.md` is a vendor marketing claim, not a competing
  statistical claim. CONTRADICTIONS.md has no MTTR entry, and no open `contradiction`-labeled
  issues exist on the topic.
