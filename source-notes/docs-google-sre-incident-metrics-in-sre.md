---
source_url: https://sre.google/static/pdf/IncidentMeticsInSre.epub
source_type: documentation
title: "Incident Metrics in SRE"
author: "Štěpán Davidovič (Google SRE)"
date_published: 2021-03-19
date_extracted: 2026-07-30
last_checked: 2026-07-30
status: current
confidence_overall: settled
issue: "#661"
---

# Incident Metrics in SRE

> O'Reilly report (~60 pages) by a Google SRE practitioner, published on sre.google. Uses Monte Carlo simulation on four empirical incident-duration data sets (three public companies + Google) to demonstrate that MTTx metrics (MTTR, MTTM) are structurally unreliable for decision-making or trend analysis given the heavy-tailed, high-variance distribution of incident durations. Proposes alternative approaches: tailoring metrics to specific questions, user studies on select incidents, and direct reliability indicators (SLIs/SLOs). Published March 2021 — predates the guide's December 2025 recency cutoff; the statistical methodology is timeless but the empirical data is from 2019 incidents and the source contains no AI/LLM-specific incident context.

## Source Context

- **Type**: documentation — O'Reilly report published as a free EPUB download on sre.google. Single chapter (~60 pages, 2019 data).
- **Author credibility**: Štěpán Davidovič is a Google SRE practitioner. The report is published on the official sre.google domain under O'Reilly Media, with editorial review (acknowledges Kathy Meier-Hellstern, Ben Appleton, Michael Brundage, Cassie Kozyrkov). This is a first-party statistical analysis backed by empirical data from Google's internal incident tracking plus three public incident-status dashboards.
- **Scope**: Covers the statistical critique of MTTx metrics (MTTR, MTTM, median TTR, geometric mean, sum, percentile) for incident-duration analysis. Provides Monte Carlo simulation methodology, analytical (z-test) alternatives, and proposes better measurement approaches. Does NOT cover incident management process, on-call practices, AI/LLM content, or specific tool recommendations. The source is a mathematical/statistical analysis, not a process guide.
- **Note on recency**: Published March 2021 — approximately 4.5 years before the guide's December 2025 recency cutoff. The Monte Carlo simulation methodology and conclusions about incident-duration distributions are foundational statistical analysis that does not depend on rapidly-changing tooling or AI patterns. However, the empirical data is from 2019 incidents, and the source contains no AI/LLM-specific incident context. The Assayer should evaluate whether this age is acceptable for inclusion given the timeless nature of the analysis.

## Extracted Claims

### Claim 1: Incident durations follow a positively skewed (log-normal-like) distribution with huge variance — the majority resolve quickly but a long tail of complex events and "black swan" disasters dominates the mean
- **Evidence**: Empirical incident duration data from three public companies (Company A: N=798; Company B: N=350; Company C: N=2,186) and Google's internal 2019 incident data set. Q-Q plots show the distributions approach lognormal (or gamma) distribution. All data sets show "huge variance in the incident durations."
- **Confidence**: settled
- **Quote**: "The key observation is that the incidents follow a positively skewed distribution in each case, with the majority of incidents resolving quickly. ... All data sets show a huge variance in the incident durations. This matches my experience: most incidents are resolved fairly quickly, but some are more complex and lingering events, and a handful are disastrous 'black swan events.'"
- **Our assessment**: Settled empirical finding. The log-normal-like, positively skewed distribution is the foundational observation that underpins every subsequent claim about metric unreliability. This distribution shape is consistent with the known behavior of many complex-system failure modes. The data spans companies of different sizes and business models, suggesting the distribution shape is a general property of production incidents rather than company-specific.

### Claim 2: Even with a guaranteed 10% reduction in every incident's duration, MTTR cannot reliably detect the improvement — 38–40% of simulations show MTTR worsening or no improvement at small sample sizes
- **Evidence**: Monte Carlo simulation (100k iterations, 2-sample 50/50 split, incidents from year 2019: N1+N2=173, 103, 609 for Companies A, B, C). With a guaranteed 10% shortening in one sample, "38% of the simulations had the MTTR difference fall below zero for Company A, 40% for Company B, and 20% for Company C."
- **Confidence**: settled
- **Quote**: "Even though in the simulation the improvement always worked, 38% of the simulations had the MTTR difference fall below zero for Company A, 40% for Company B, and 20% for Company C. Looking at the absolute change in MTTR, the probability of seeing at least a 15-minute improvement is only 49%, 50%, and 64%, respectively."
- **Our assessment**: The core quantitative finding of the report. A 38–40% false-negative rate means MTTR is essentially a coin-flip for detecting moderate improvements at practical sample sizes. This directly undermines any claim that MTTR improvement validates an intervention. The fact that even Company C (609 incidents/year, the largest public data set) still has a 20% false-negative rate shows that more incidents help but don't solve the problem at typical organizational scales.

### Claim 3: With no actual change to incidents, there is a 19% chance of observing a ≥30-minute MTTR improvement purely by random sampling variation — making it impossible to distinguish real improvement from statistical noise
- **Evidence**: Same Monte Carlo simulation, but with both samples drawn from the same (unchanged) distribution (step 2 modified to `new_duration = old_duration`). "There's a 19% chance that there is a half-hour improvement (or better) of MTTR in Company A (and 23% for Company B, and 10% for Company C)…even though in this simulation, you did not change anything about the incidents."
- **Confidence**: settled
- **Quote**: "there's a 19% chance that there is a half-hour improvement (or better) of MTTR in Company A (and 23% for Company B, and 10% for Company C)…even though in this simulation, you did not change anything about the incidents."
- **Our assessment**: Even more damning than Claim 2 — this shows that an apparent improvement can arise from sampling variation alone, with no structural change. The author's cynical footnote about a "fake incident-shortening product" is darkly illustrative: a vendor could sell a product that does nothing, and 19% of customers would see an apparent MTTR improvement by chance. This is the strongest argument in the report for why MTTR should not be used for tooling/process evaluation.

### Claim 4: The 90% confidence interval for MTTR difference spans hours even at N=1,000 incidents — a 10% improvement falls well within the noise band
- **Evidence**: Table 2: For N1+N2=1,000 incidents (50/50 split), the 90% confidence interval for the MTTR difference is approximately ±33 minutes (Company A), ±31 minutes (Company B), ±43 minutes (Company C). The mean TTR values are 2h26m, 2h31m, and 4h31m respectively — a 10% improvement is ~15 minutes, well within the ~30–40 minute confidence interval.
- **Confidence**: settled
- **Quote**: "As the number of samples goes up, the standard deviation goes down, and that improves your ability to detect smaller and smaller changes as significant. In the original scenario, you were evaluating a product offering a 10% reduction in the incident duration; even at one thousand incidents, that would still fall into the 90% confidence interval. In no case do you get to a confident value even with a year's worth of data."
- **Our assessment**: This table is the most practically useful artifact in the report — it provides concrete sample-size requirements. Even at 1,000 incidents (far more than most organizations produce in a year), the confidence interval is wide enough to swallow a meaningful 10% improvement. The implication: only organizations with extremely high incident volumes (or extremely large improvement effects) can use MTTR reliably.

### Claim 5: Median TTR and geometric mean TTR perform only marginally better than arithmetic mean — the problem is not specific to "mean" in MTTR but applies to all aggregate statistics of high-variance, low-sample-size data
- **Evidence**: Tables 3 (median) and 5 (geometric mean). For median TTR at N=1,000: 90% CI is ±11min (Company A), ±9min (Company B), ±29min (Company C). For geometric mean at N=1,000: ±7.2min, ±8.5min, ±18min respectively. Higher percentiles (95th, Table 4) perform "much worse" — at N=100, 90% CI spans ±12h for Company A.
- **Confidence**: settled
- **Quote**: "The difficulty is not specific to the 'mean' in MTTR; median TTR isn't helping us either." — and — "The higher percentiles, such as 95th percentile, perform much worse. Intuitively, this makes sense. The higher percentile incident duration will be swayed by the worst incidents, which are also the rarest."
- **Our assessment**: This refutes a common objection ("just use median instead of mean"). The underlying problem is not the specific statistic but the high variance-to-sample-size ratio. The geometric mean, which is the natural summary for lognormal-like distributions, also fails to provide tight enough confidence intervals at practical sample sizes. This is a structural limitation of the data, not a choice of formula.

### Claim 6: At Google-scale (15× the incidents of the next-largest data set), MTTx still fails to be practically useful — a year's worth of all-significant-incidents data can only detect changes of ≥5.3% of MTTR
- **Evidence**: Google 2019 data set (all significant incidents, ~15× the size of the largest public data set). Table 7: For all significant incidents at one year's data, the 90% CI is [−5.3%; +5.4% of MTTR]. For the most severe incidents only (often user-facing), the CI is [−18%; +18%] even at a full year.
- **Confidence**: settled
- **Quote**: "I have no practical development that would promise this level of incident duration reduction over such a wide gamut of incidents. The ability to confidently detect changes as 'small' as 5.3% in the mean after a year's worth of incidents is not strengthening MTTR's position as a practically useful incident statistic."
- **Our assessment**: Even Google — with vastly more incidents than a typical organization — cannot use MTTR reliably for the most severe incidents (the ones that matter most). The all-incidents data set gets tighter confidence intervals, but includes everything from "long-standing processing pipeline problems" to "corporate device software installations" — a heterogeneous mix where a uniform improvement is implausible. This is the "quantity has a quality all its own" argument turned on its head: even with Google's incident volume, the metric is not practically useful.

### Claim 7: The problem is structural to the incident domain (high variance + low sample size) and cannot be fixed by better metadata quality
- **Evidence**: The author examined Google-internal incident metadata and "found no major improvement in the incident duration analysis for teams with more stringent incident-reporting expectations." Additionally, the three public data sets (varying business models, reporting practices) all "show roughly similar behavior."
- **Confidence**: settled
- **Quote**: "The challenge in aggregate incident analysis does not appear to be about incident metadata quality. The efforts to improve the accuracy of metadata collection are unlikely to cause any dramatic changes."
- **Our assessment**: An important corrective. The natural response to "MTTR is noisy" is "let's improve our data quality." This claim argues that won't help — the problem is not measurement error (metadata quality) but fundamental variance in the phenomenon. This makes the problem structural rather than operational.

### Claim 8: The default position should be to reject MTTx metrics for evaluating reliability trends, tooling/process improvements, or overall system reliability — with two exceptions (high-volume hardware and truly dramatic changes)
- **Evidence**: The author lists three specific failures of MTTx: (a) poor measure of overall reliability (doubling incidents without changing their distribution worsens reliability but doesn't change MTTR); (b) no useful insight into trends in incident-response practices; (c) improvements in process/tooling cannot have their success or failure evaluated on MTTx. Two exceptions: high-volume hardware purchases (Backblaze's hard drive reliability data, tens of thousands of devices per model, with lower variance) and truly dramatic changes (cutting incident duration to 20% of baseline).
- **Confidence**: settled
- **Quote**: "This means that MTTx is a bad fit for typical practical analysis to evaluate the impact of a typical change on TTx: ... It is a poor measure of the overall reliability of your system. ... It does not provide any useful insights into the trends in your incident-response practices. ... Improvements in incident management processes or tooling changes cannot have their success or failure evaluated on MTTx."
- **Our assessment**: The report's primary actionable conclusion. The three failure modes are clearly named, and the two exceptions are narrow enough that most organizations will fall into the default "reject MTTx" category. The Backblaze exception is particularly instructive: high-volume hardware is an exception precisely because it has both high N (tens of thousands) and lower variance (hard drives of the same model are more similar than incidents).

### Claim 9: The recommended alternative is to tailor metrics to specific questions — what aspect of the incident lifecycle is being improved? — and use user studies on select incidents rather than aggregate statistics
- **Evidence**: The author argues that a product or process change improves specific sub-steps of an incident (e.g., communication, automated hypothesis generation), not "incident duration" as a monolithic thing. "If you are improving one step of the journey, including all other steps in the aggregate makes your ability to understand the impact of the change worse." Recommended approach: user studies on a select sample, focused on the specific aspect being improved, with expert advice if possible.
- **Confidence**: emerging (presented as reasoned opinion, not empirically validated)
- **Quote**: "Trying to analyze the individual behavior of each and every incident is likely not practical. ... Instead, a practical solution can be user studies on a select sample of incidents. These studies can be constructed to focus on just the aspects of the incident you are interested in and can surface richer understanding than an aggregate statistic can ever hope to."
- **Our assessment**: The weakest section of the report — the alternatives are sketched at a high level and lack the rigorous simulation-based evidence of the critique. The "user studies on select incidents" recommendation is reasonable but vague; it does not provide a practical methodology that a team could implement. The author acknowledges this limitation ("Constructing these studies correctly is not always trivial"). This is more of a research direction than a replacement framework.

### Claim 10: The Monte Carlo simulation methodology (2-sample split, 100k iterations) is a reproducible, flexible technique that can be applied to evaluate any candidate incident metric
- **Evidence**: The author provides the complete 5-step simulation process, including the specific details (50/50 split gives strongest analysis; z-test analytical alternative; simulation preferred for flexibility — e.g., modeling 95th percentile requires only "a one-line change"). The method can be implemented with "a Python script and a CSV file with the data or a sufficiently capable SQL engine."
- **Confidence**: settled
- **Quote**: "The simulation process is simple: (1) Randomly draw two samples, with size N1 and N2 (where N1 = N2 to get a perfect 50/50 split), from the empirical distribution of incident durations. (2) Modify the incident durations in one of the populations, in this case by shortening it by 10%. (3) Calculate MTTR for each of the groups. (4) Take the difference. (5) Repeat this process 100,000 times."
- **Our assessment**: The most practically useful positive contribution of the report — a concrete, reproducible methodology that any team can apply to test their chosen metric. The author correctly notes that this applies "not just to MTTR" but to any candidate metric. The 50/50 split insight (demonstrated via the variance equation) is a useful technical detail. This methodology is the report's primary reusable artifact for the guide.

### Claim 11: Incident counts are as erratic as incident durations — multiyear trends may be detectable but single-year or quarterly fluctuations are dominated by external confounding factors
- **Evidence**: Figure 8 shows incidents per year as a proportion of total for the three public companies. Values "jump around wildly" even at whole-year aggregation, and "at the resolution of months or quarters, it is even worse." The author speculates that observed trends may be artifacts of usage pattern changes, product portfolio changes, or changes in incident reporting policies.
- **Confidence**: emerging (limited analysis; the author explicitly says "I will not attempt a deeper analysis here")
- **Quote**: "The incident count is just as erratic as incident durations. Even aggregated to whole years ... the values jump around wildly. At the resolution of months or quarters, it is even worse."
- **Our assessment**: A secondary observation that reinforces the overall theme: incident data is structurally high-variance. This is consistent with the existing source note on counting incidents (`docs-google-sre-anatomy-of-an-incident.md` Claim 3 warns against measuring incident counts). The author's speculation about confounding factors (usage patterns, product changes, reporting changes) is a useful caution but is not empirically substantiated in this report.

## Concrete Artifacts

### Monte Carlo simulation process (verbatim from source)

```
Step 1: Randomly draw two samples, with size N1 and N2 (where N1 = N2 to get
        a perfect 50/50 split), from the empirical distribution of incident
        durations.
Step 2: Modify the incident durations in one of the populations, in this case
        by shortening it by 10%.
Step 3: Calculate MTTR for each of the groups, i.e., MTTR(modified) and
        MTTR(unmodified).
Step 4: Take the difference, observed improvement = MTTR(unmodified) -
        MTTR(modified).
Step 5: Repeat this process 100,000 times.
```

*Source: "Incident Metrics in SRE," "Simulating MTTR in Parallel Universes" section.*

### Incident duration empirical statistics (Table 1, verbatim from source)

```
                        Company A   Company B   Company C
Incidents (all)         779         348         2157
Incidents (2019)        173         103         609
Mean TTR                2h 26m      2h 31m      4h 31m
Standard deviation      5h 16m      5h 1m       6h 53m
```

*Source: "Incident Metrics in SRE," Table 1.*

### 90% confidence intervals for MTTR difference (Table 2, verbatim from source)

```
N1+N2 = 10:   Company A [-5h41m; +5h42m]   B [-5h25m; +5h18m]   C [-7h4m; +7h15m]
N1+N2 = 100:  Company A [-1h44m; +1h44m]   B [-1h39m; +1h39m]   C [-2h16m; +2h16m]
N1+N2 = 1000: Company A [-33m; +33m]       B [-31m; +31m]       C [-43m; +43m]
```

*Source: "Incident Metrics in SRE," Table 2.*

### 90% confidence intervals for median TTR difference (Table 3, verbatim from source)

```
Median TTR:   Company A 42m    Company B 1h 7m    Company C 2h 50m

N1+N2 = 100:  Company A [-29m; +29m]   B [-29m; +29m]   C [-1h20m; +1h19m]
N1+N2 = 1000: Company A [-11m; +11m]   B [-9m; +9m]     C [-29m; +29m]
```

*Source: "Incident Metrics in SRE," Table 3.*

### 90% confidence intervals for 95th percentile TTR difference (Table 4, verbatim from source)

```
95th %ile TTR: Company A 10h 45m   Company B 8h 48m   Company C 12h 59m

N1+N2 = 100:  Company A [-12h19m; +12h22m]   B [-8h34m; +8h36m]   C [-12h29m; +12h30m]
N1+N2 = 1000: Company A [-5h23m; +5h25m]     B [-3h18m; +3h17m]   C [-3h33m; +3h32m]
```

*Source: "Incident Metrics in SRE," Table 4.*

### 90% confidence intervals for geometric mean TTR difference (Table 5, verbatim from source)

```
Geometric mean TTR: Company A 54m   Company B 1h 9m   Company C 2h 24m

N1+N2 = 100:  Company A [-24m; +25m]   B [-27m; +27m]   C [-56m; +56m]
N1+N2 = 1000: Company A [-7.2m; +7.2m] B [-8.5m; +8.7m] C [-18m; +17m]
```

*Source: "Incident Metrics in SRE," Table 5.*

### Google MTTR/median confidence intervals (Table 7, verbatim from source)

```
                          Most severe incidents   All significant incidents
                          (often, not always,      (often not user facing)
                           user facing)

Incidents in 2019         X                       15 × X
(approximate relative size)

Mean TTR, ¼ year data     90% CI [−35%; +35%]     90% CI [−11%; +11%]
Mean TTR, ½ year data     90% CI [−25%; +25%]     90% CI [−7.6%; +7.6%]
Mean TTR, 1 year data     90% CI [−18%; +18%]     90% CI [−5.3%; +5.4%]

Median TTR, ¼ year data   90% CI [−53%; +52%]     90% CI [−20%; +20%]
Median TTR, ½ year data   90% CI [−35%; +35%]     90% CI [−14%; +14%]
Median TTR, 1 year data   90% CI [−25%; +25%]     90% CI [−10%; +10%]
```

*Source: "Incident Metrics in SRE," Table 7.*

### Variance of the sample mean difference equation (verbatim from source)

```
σ²(sample mean difference) = (2/N) × σ²(incidents)

z = ΔMTTR / sqrt((2/N) × σ²)

±ΔMTTR = ±z × sqrt((2/N) × σ²)
```

*Source: "Incident Metrics in SRE," "Analytical Approach" section.*

### Incident timeline model (verbatim from source)

```
First product impact: The first moment of severe impact to the product
Detection:            When the system's operator becomes aware of the ongoing
                      problem
Mitigation:           When there is no longer severe product impact but the
                      system might still be degraded in some way
Recovery:             When the system has been fully recovered into normal
                      operation; recovery and mitigation are often the same
                      stage, but sometimes they differ
```

*Source: "Incident Metrics in SRE," "Incident Life Cycle and Timing" section.*

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

The following candidates from `miner-related-notes.md` were evaluated:

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3000) — **Dismissed.** Discusses sociotechnical complexity and incomplete mental models during incidents. The current source is a statistical analysis of incident duration distributions, not a discussion of complexity or cognitive factors. No claims to corroborate or contradict.

2. **`docs-google-sre-prodcast.md`** (score 0.2500) — **Dismissed.** The Prodcast index note lists season/episode metadata. No substantive claims about incident metrics or statistical analysis. No cross-reference needed.

3. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2250) — **Corroborates.** Claim 15 ("The field is moving away from MTTR as the single be-all metric, toward richer insights (Sarah cites Courtney Nash's 'void report')") is the trend-level claim that this source's statistical evidence supports. The Prodcast note states the sentiment (industry direction); this source provides the simulation-based evidence for why that direction is justified. The Prodcast claim is labeled `emerging` (trend claim); this source raises it to `settled` with quantitative evidence.

4. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2250) — **Dismissed.** Covers SRE concepts outside Google (scale shock, replication norms). No incident metrics or statistical analysis overlap.

5. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2250) — **Dismissed.** AI for SRE (early outage detection, ticket analysis). The current source has zero AI/LLM content. No cross-reference.

6. **`docs-google-sre-prodcast-03-05-building-reliable-systems.md`** (score 0.2000) — **Dismissed.** Database reliability, managed services, heroism culture. No incident metrics overlap.

7. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2000) — **Corroborates.** Claim 13 ("Error budgets beat incident counts / MTTR for communicating SRE value and ROI to leadership — MTTR is 'a pretty poor proxy for the actual customer experience'"). Singer's claim that MTTR is a poor proxy for customer experience corroborates the current source's recommendation to reject MTTx for reliability evaluation, approaching from the business-impact/customer angle rather than the statistical-reliability angle. The two angles are complementary: the current source provides the statistical evidence (Monte Carlo), while Singer provides the business/customer-experience argument.

8. **`docs-google-sre-reliable-product-launches.md`** (score 0.2000) — **Dismissed.** Launch coordination engineering (LCE). Pre-launch phase, not incident metrics. No overlap.

9. **`docs-google-sre-prodcast-04-09-ai-agents.md`** (score 0.2000) — **Dismissed.** AI agents for incident response (agent spectrum, guardrails, alert summarization). The current source has no AI content. No cross-reference.

10. **`docs-google-sre-handling-overload.md`** (score 0.2000) — **Dismissed.** Load shedding, autoscaling, thundering herd prevention. Different domain from incident duration metrics.

### Primary cross-references

- **Corroborates**:
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 15 (moving away from MTTR as the single be-all metric). This source provides the statistical evidence that the Prodcast notes as a trend claim. The Prodcast cites Courtney Nash's "void report" qualitatively; this source provides Monte Carlo simulation evidence from four data sets. See the candidate evaluation above for details.
  - `docs-google-sre-anatomy-of-an-incident.md` Claim 3 (measuring incident counts creates perverse incentives — "it's better to declare an incident and close it afterward"). This source's Claim 11 (incident counts are "just as erratic as incident durations") and its citation of Branson's "Stop Counting Production Incidents" align with the Anatomy source's warning. Both argue that raw incident counts are unreliable metrics for reliability evaluation.
  - `docs-google-sre-anatomy-of-an-incident.md` Claim 4 (the "20-30 minute human floor" heuristic — "once a human is involved, the outage will last at least 20 to 30 minutes"). This source does not address the human floor directly, but its argument that MTTR should be rejected for process evaluation complements the Anatomy source's implicit argument: if there's a ~25-minute floor regardless of intervention quality, then improvements within that band are invisible to MTTR.
  - `docs-google-sre-prodcast-04-02-data-centers.md` Claim 6 (MTTR/MTBF are weak at fleet scale because "failures are novel and non-normal... it's not a normal distribution"). Steve McGhee's observation that MTTR/MTBF fail at fleet scale because failures are "novel and non-normal" provides independent evidence from Google's physical-infrastructure domain supporting Claim 7 (the problem is structural to the incident domain — high variance + non-normal distribution). McGhee's critique comes from Google's data-center fleet experience, while the current source's critique comes from software-incident data sets; both converge on the same conclusion from different domains.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claim 13 (MTTR is "a pretty poor proxy for the actual customer experience"; error budgets beat incident counts/MTTR for communicating SRE value and ROI to leadership). Singer's claim that MTTR is a poor proxy for customer experience corroborates the current source's recommendation to reject MTTx for reliability evaluation, approaching from the business-impact/customer angle rather than the statistical-reliability angle. The two angles are complementary: the current source provides the statistical evidence (Monte Carlo simulation), while Singer provides the business/customer-experience argument.
  - `docs-google-sre-prodcast-06-01.md` Claim 2 (Stepan Davidovic's work discredited MTTR via Monte Carlo simulations showing "the times in incidents are not related to each other enough to statistically matter... You can't move it enough to make it matter statistically"). This is the highest-value corroboration: the S6E1 episode *directly and explicitly discusses the Stepan Davidovic Monte Carlo paper* that this source note IS. Clint Byrum states Davidovic "killed it" and describes sending the paper to executives and engineers as the canonical reference for why MTTR is statistically unreliable. The S6E1 episode provides independent practitioner endorsement — recorded live at SREcon Americas 2026 — confirming the Davidovic paper's real-world dissemination and impact at industry conferences.

- **Contradicts**:
  - `blog-incidentio-ai-sre-incident-run.md` Claim 7 ("can reduce incident MTTR by up to 80%"). This source argues that MTTR is structurally unreliable for evaluating any incident-response improvement, which would make the 80% MTTR reduction claim unverifiable through the metric it uses. **However**, this is a tension in framing rather than a direct contradiction: the incident.io claim is a vendor performance claim (the reported MTTR reduction may be real, but whether MTTR reduction is the right way to measure it is the question), while this source is a statistical critique of the metric itself. The two can coexist if incident.io's claimed improvement is large enough to be detectable by MTTR (Claim 8's second exception: "truly dramatic changes, such as cutting the incident duration to just 20% of what it used to be"). The existing Prodcast-03-06 source note (Extends section) evaluated this same tension and classified it as a conditioning variable rather than a contradiction. This source does not change that assessment — it provides the statistical evidence for the existing tension. **No contradiction issue filed.** See the Prodcast-03-06 Extends discussion and the note below.
  - *Note on the MTTR tension*: The Prodcast-03-06 source note (Claim 15 vs incident.io Claim 7) already identified the tension between "moving away from MTTR" as an industry trend and the vendor claim of "80% MTTR reduction." That note classified it as a conditioning variable, not a contradiction (coarse metric still useful as richer ones emerge). This source adds quantitative evidence to the MTTR-skeptic side of that tension but does not change its fundamental nature. No new contradiction issue is warranted.

- **Extends**:
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 15 — as described above, this source provides the statistical backbone for the Prodcast's trend-level claim. The Prodcast note labels Claim 15 `emerging` because it is a trend observation; this source would raise the overall confidence for the MTTR-skeptic position to `settled`.
  - `docs-google-sre-incident-management-guide.md` Claim 5 (automation of incident response elements — common tasks, impact analysis, RCA, mitigation suggestions — frees oncallers to focus on problem-solving). This source is orthogonal to the Guide's automation targets but provides the measurement-context for why evaluating those automation targets should not rely on MTTR. The Guide's automation list can be cited as "what to automate," while this source provides "how NOT to measure if automation succeeded."
  - `docs-google-sre-prodcast-06-01.md` (S6E1 "Prodcast Live!") — as described above, the S6E1 episode provides a secondhand summary of the Davidovic Monte Carlo paper from a SREcon Americas 2026 live recording. The current source IS the primary reference that S6E1 cites. This source provides the full simulation methodology, empirical data sets, and confidence interval tables that S6E1 only describes colloquially ("You can't move it enough to make it matter statistically"). **S6E1 should also be updated to cross-reference this source as the canonical primary source for the Davidovic Monte Carlo analysis**, replacing the current "cite Davidovic's paper as the primary source" placeholder in its Guide Impact section with a citation to this source note.

- **Novel** (content new to the corpus):
  - **Monte Carlo simulation of incident metric reliability** — the specific 5-step methodology (2-sample 50/50 split, 100k iterations, testing both improvement and no-change scenarios) is entirely new to the corpus and is a reproducible technique the guide could reference.
  - **Empirical incident-duration distributions from four data sets** — the specific numbers (mean TTR, standard deviation, median, geometric mean) for three public companies and Google. These distributions characterize the "shape" of incident durations in a way no existing source note does.
  - **The "no improvement" detection failure case** (Claim 3) — the demonstration that apparent MTTR improvement arises purely from sampling variation (19–23% chance of ≥30-minute improvement in Company A/B with no change). This is a stronger argument than Claim 2 (can't detect real improvement) and is new to the corpus.
  - **Confidence interval tables** (Tables 2–7) — concrete numbers showing required sample sizes for reliable MTTR/median/percentile detection. These are actionable reference tables for teams evaluating their own metrics.
  - **The analytical (z-test) derivation** — the variance equation and z-test expansion that provides mathematical backing for the simulation results, plus the insight that a 50/50 split minimizes variance of the difference.

- **Corroborates (additional, beyond candidate list)**:
  - `docs-google-sre-anatomy-of-an-incident.md` — The incident timeline model used in this source (First product impact → Detection → Mitigation → Recovery) is a simplified version of the same lifecycle described in Anatomy. The source cites Allspaw's "Moving Past Shallow Incident Data" and acknowledges "shallow incident data" as an existing problem, which the Anatomy source also discusses (Claim 10's "what you think vs what it actually is" Venn diagram). No claim-level contradiction with the incident timeline model in Anatomy (the two models serve different purposes: one for measurement analysis, one for process guidance).

## Guide Impact

- **Chapter 02 (Incidents), Ch04 (Observability/Measurement)**: Primary target. This source provides the statistical evidence for a critical position the guide currently lacks: **MTTx metrics are structurally unreliable for evaluating incident-response improvements.** The guide currently has no coverage of incident metrics at all. Recommend adding a section that:
  (a) Presents the incident-duration distribution finding (Claim 1) as the empirical context — most incidents are short but a heavy tail dominates the mean.
  (b) States the default position: reject MTTx for evaluating process/tooling changes (Claim 8), with the two exceptions (high-volume hardware, dramatic changes).
  (c) Cites the confidence interval tables (Tables 2–7) as evidence for why typical organizational incident volumes are insufficient for reliable MTTR-based decisions.
  (d) Recommends the Monte Carlo simulation methodology (Claim 10) as a reproducible technique for testing any candidate metric — "Run this on your own incident data before trusting any aggregate statistic."
  (e) Recommends the alternatives (tailoring metrics to specific questions, user studies) from Claim 9, with the caveat that these are high-level sketches rather than mature frameworks.
  (f) Note the recency concern: this is a March 2021 source with 2019 data and no AI/LLM incident context. The statistical methodology is timeless, but the empirical data should be presented with its date context.

- **Cross-reference to `docs-google-sre-prodcast-03-06-incident-response-tooling.md`**: The Prodcast source's Claim 15 ("moving away from MTTR") is currently `emerging` as a trend claim. This source provides the evidence that makes that trend position `settled` — recommend updating the Prodcast note's cross-reference to cite this source as the statistical backing.

- **Cross-reference to `docs-google-sre-prodcast-06-01.md`**: The S6E1 "Prodcast Live!" source note's Claim 2 cites the Davidovic Monte Carlo paper as the canonical reference for why MTTR is statistically unreliable, and its Guide Impact section contains a placeholder recommending to "cite Davidovic's paper as the primary source." With this source note now in the corpus, that placeholder can be resolved: **S6E1 should be updated to cross-reference this source as the canonical primary source for the Davidovic Monte Carlo analysis.** This closes a bidirectional cross-reference loop — S6E1 cites the paper, and this source IS the paper, providing the full simulation methodology, empirical data, and confidence interval tables that S6E1 only describes colloquially.

- **Cross-reference to `blog-incidentio-ai-sre-incident-run.md`**: The tension between incident.io's "80% MTTR reduction" claim (Claim 7) and this source's evidence that MTTR cannot reliably detect improvements should be explicitly noted in the guide. The guide should present both: incident.io's claim as a vendor-reported outcome (from pre-launch dogfooding), and this source's critique as the statistical reason to treat such claims skeptically. This is a conditioning variable discussion, not a "pick one" — the guide should recommend that readers evaluate vendor MTTR claims against their own incident volumes using the Monte Carlo methodology.

- **Chapter 05 (AI-assisted SRE) / AI SRE measurement**: This source provides a framework for thinking about how to measure AI agent effectiveness in incident response — a critical gap in the current guide. Instead of relying on MTTR reduction (the most commonly cited AI SRE metric), the guide should recommend: (a) measure specific sub-steps (time to detection, time to hypothesis generation, time to first mitigation attempt) rather than aggregate incident duration; (b) use user studies comparing AI-assisted vs human-only response on matched incidents; (c) test chosen metrics via simulation before trusting them for go/no-go decisions.

## Extraction Notes

- The source is a single EPUB file (`IncidentMeticsInSre.epub`, 6 MB, 1 chapter) downloaded from https://sre.google/static/pdf/IncidentMeticsInSre.epub. It was extracted by unzipping the EPUB and reading the XHTML content (`OEBPS/ch01.html`) end-to-end. No sub-pages were followed — the report is self-contained in one chapter.
- **Publication date**: The copyright page lists "March 2021: First Edition" with a revision history entry "2021-03-19: First Release." This is set as `date_published: 2021-03-19` in frontmatter.
- **Post-2025 cutoff concern**: The source predates the guide's December 2025 recency cutoff by ~4.5 years. The Monte Carlo simulation methodology and statistical conclusions are foundational and do not age. However, the empirical data is from 2019 incidents and the source contains zero AI/LLM content. The Assayer should weigh whether the value of the simulation methodology and confidence-interval tables outweighs the age concern. A note flags this in the Source Context and Guide Impact.
- **Outlier handling**: The author excluded incidents <3 minutes and >3 days from the public data sets (~1-2% of each set), noting that these outliers are valid but could "cast avoidable doubt on the analysis." Google data had more >3-day incidents, and the author tested both a 3-day cutoff and a top-5% exclusion with "only slight" differences in results. This is documented for reproducibility.
- **Author's identity**: The author is Štěpán Davidovič (acknowledgments name Google colleagues; published on sre.google). The frontmatter metadata labels this as an O'Reilly report. The author's specific role/team within Google SRE is not stated beyond the "Google SRE" attribution on the copyright page.
- `confidence_overall` is `settled`: the dominant claims (MTTx unreliability demonstrated by simulation, the distribution shape of incident durations, the confidence interval tables, the analytical derivation) are backed by reproducible empirical data and simulation methodology. Claim 9 (user study alternatives) and Claim 11 (incident count erraticism) are emerging/secondary and are flagged per-claim.
- All quotes are copied character-for-character from the extracted XHTML. Tables are reproduced from the HTML table elements in the source. The figures (images) could not be extracted directly and are described from the surrounding text and figure captions.
- No contradiction issue was filed. The tension with incident.io's "80% MTTR reduction" claim is the same conditioning-variable tension already identified in the Prodcast-03-06 source note's cross-references. This source provides the quantitative evidence for the MTTR-skeptic position but does not change the nature of that tension. See the Cross-References → Contradicts section for the full analysis.
