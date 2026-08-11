# Incident Response

> Using AI/LLMs during pages and SEVs — what helps, what slows you down, and
> how to keep the human accountable for blast radius.

## Why MTTR lies to you

Incident durations follow a positively skewed (log-normal-like) distribution
with huge variance — most resolve quickly but a long tail of complex events
dominates the mean. Standard deviations are roughly double the means across
four independent data sets (three public companies + Google)
[source: docs-google-sre-incident-metrics-in-sre, Claim 1] [settled].

Monte Carlo simulation (100k iterations, 2-sample 50/50 split) shows that
even with a guaranteed 10% reduction in every incident's duration, MTTR
cannot reliably detect the improvement: 38–40% of simulations show MTTR
worsening at typical annual incident volumes
[source: docs-google-sre-incident-metrics-in-sre, Claim 2] [settled].

Worse: with no actual change to incidents, there is a 19% chance of
observing a ≥30-minute MTTR improvement purely by random sampling variation
[source: docs-google-sre-incident-metrics-in-sre, Claim 3] [settled].

```
                    Company A    Company B    Company C
Incidents (2019)     173          103          609
Mean TTR             2h 26m       2h 31m       4h 31m
Standard deviation   5h 16m       5h 1m        6h 53m

90% CI for MTTR diff at N=1000: ±33m (A), ±31m (B), ±43m (C)
```
*Data from [source: docs-google-sre-incident-metrics-mttx, Concrete Artifacts].*

Even at Google's incident volume (15× the largest public data set), MTTR can
only detect changes of ≥5.3% after a full year — and for the most severe
(user-facing) incidents, the 90% CI is ±18% after one year
[source: docs-google-sre-incident-metrics-in-sre, Claim 6] [settled].

Neither median, geometric mean, nor high percentiles rescue the problem. The
difficulty is structural (high variance + low sample size), not specific to
the arithmetic mean [source: docs-google-sre-incident-metrics-mttx, Claim 4]
[settled]. Improving incident metadata quality doesn't help either — the
problem is the phenomenon itself, not measurement error
[source: docs-google-sre-incident-metrics-in-sre, Claim 7] [settled].

**Rule**: Reject MTTx for evaluating incident-response process improvements,
tooling changes, or overall system reliability. The metric cannot distinguish
real improvement from noise at typical organizational incident volumes.

### Two narrow exceptions

MTTx can work for (a) massive homogeneous quantities with lower variance
(e.g., Backblaze's tens of thousands of disk drives) and (b) truly dramatic
changes (~80% duration reduction) that would be detectable by many methods
anyway [source: docs-google-sre-incident-metrics-in-sre, Claim 8] [settled].

### What to do instead

Tailor the metric to the specific question — measure the specific
incident-lifecycle phase a change targets rather than aggregate duration. Use
user studies on selected incident samples. Use SLIs/SLOs as direct reliability
indicators rather than incident summary statistics
[source: docs-google-sre-incident-metrics-in-sre, Claim 9] [emerging].

The same Monte Carlo methodology (2-sample 50/50 split, 100k iterations) can
test any candidate incident metric before adoption
[source: docs-google-sre-incident-metrics-mttx, Claim 10] [settled]:

```
1. Randomly draw two samples (N1 = N2) from your incident duration data
2. Apply the expected improvement to one sample
3. Calculate your metric for both groups
4. Take the difference
5. Repeat 100,000 times
```
*From [source: docs-google-sre-incident-metrics-mttx, Concrete Artifacts].*

**Rule**: Before adopting any incident metric, run the Monte Carlo simulation
on your own data. If the 90% confidence interval at your annual incident
volume is wider than the improvement you're targeting, the metric cannot
support the decision you want to make.

## Supply-chain incident response

When an LLM gateway or SDK package is compromised, the response follows an
ordered playbook: quarantine → credential rotation → external forensics →
release freeze → hardened rebuild → signed artifacts → safe-version audit
[source: failure-litellm-supply-chain-compromise-march-2026, Lesson 5]
[settled].

Impact scoping must be deployment-path-aware. In LiteLLM's March 2026
supply-chain incident, pinned-Docker/source/Cloud installs were safe, while
pip installs without pinned versions — including transitive/unpinned deps via
AI agent frameworks and MCP servers — were exposed
[source: failure-litellm-supply-chain-compromise-march-2026, Lesson 4]
[settled].

Post-incident trust restoration uses artifact signing (cosign pinned to a
commit hash) plus a reproducible safe-version audit: SHA-256 digest + IoC
scan + Git-commit match
[source: failure-litellm-supply-chain-compromise-march-2026, Lesson 6] [settled]:

```
cosign verify \
--key https://raw.githubusercontent.com/<org>/<repo>/<commit>/cosign.pub \
ghcr.io/<org>/<image>:<release-tag>
```
*From [source: failure-litellm-supply-chain-incident-march-2026, Concrete
Artifacts].*

**Rule**: Pin LLM gateway and SDK dependencies to verified versions. Treat
transitive, unpinned dependencies as first-class exposure — agent frameworks
and MCP servers that pull in gateway packages expand the blast radius of any
package compromise. Verify release artifacts against an immutable signing key;
repo integrity is not release integrity.

---
*Sources for this chapter: docs-google-sre-incident-metrics-in-sre,
docs-google-sre-incident-metrics-mttx,
failure-litellm-supply-chain-compromise-march-2026,
failure-litellm-supply-chain-incident-march-2026*
*Last updated: 2026-08-01*
