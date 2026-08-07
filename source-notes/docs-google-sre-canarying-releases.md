---
source_url: https://sre.google/workbook/canarying-releases/
source_type: documentation
title: "Canarying Releases — SRE Workbook Chapter 16"
author: "Alec Warner and Štěpán Davidovič, with Alex Hidalgo, Betsy Beyer, Kyle Smith, and Matt Duftler (Google SRE)"
date_published: 2018
date_extracted: 2026-08-07
last_checked: 2026-08-07
status: current
confidence_overall: settled
issue: "#801"
---

# Canarying Releases — SRE Workbook Chapter 16

> The canonical Google SRE treatment of canary *mechanics*: the formal definition of canarying as a partial, time-limited A/B deployment, the error-budget sizing model (impact proportional to traffic exposed), canary population/duration selection, metric-selection and monitoring-data prerequisites, noninteractive-system canarying, and the worked App Engine example. Provides the release-engineering process depth that the guide's canary mentions in other notes lack, directly transferable to model/prompt/agent-config rollouts.

## Source Context

- **Type**: documentation — Chapter 16 of the Site Reliability Engineering Workbook (O'Reilly, 2018), hosted on sre.google, licensed CC BY-NC-ND 4.0.
- **Author credibility**: Highest credibility. Named Google SRE practitioner-authors (Alec Warner and Štěpán Davidovič, with Alex Hidalgo, Betsy Beyer, Kyle Smith, and Matt Duftler) writing through Google's official SRE publication channel. The Workbook is the companion volume to the SRE Book and treats practice-level implementation rather than principles. Chapter links to sibling Workbook chapters (Implementing SLOs, Data Processing Pipelines, Postmortem Analysis) for cross-references.
- **Scope**: Covers (a) release engineering principles (reproducible/automated builds, automated tests/deployments, small deployments); (b) the formal definition of canarying as a partial, time-limited deployment plus its evaluation (canary vs. control, A/B framing); (c) why canaries catch defects that unit/load testing miss under real production traffic; (d) the error-budget sizing model with explicit assumptions; (e) choosing canary population and duration (cadence coupling, one-canary-at-a-time rule, representativeness dimensions); (f) metric selection and evaluation (SLIs as the starting point, stack-ranking, excluding 400-level codes + black-box checks, attribution, before/after risk); (g) gradual multi-stage canaries; (h) dependencies and imperfect isolation; (i) canarying noninteractive/batch systems; (j) requirements on monitoring data (canary-vs-control breakdowns, aggregation interval ≤ canary duration); (k) related techniques — blue/green, artificial load, traffic teeing. Does NOT cover feature-flag framework design (covered in the SRE Book's launch chapter) or statistics for canary evaluation beyond the stated "avoid a deep dive into statistics."

## Extracted Claims

### Claim 1: Canarying is a partial and time-limited deployment of a change to a service plus its evaluation, where the changed portion ("the canary") is compared against the rest ("the control") to decide whether to proceed — effectively an A/B testing process
- **Evidence**: The chapter's formal definition, stated before any mechanics. The canary typically receives a much smaller subset of production traffic than the control.
- **Confidence**: settled
- **Quote**: "We define canarying as a partial and time-limited deployment of a change in a service and its evaluation. This evaluation helps us decide whether or not to proceed with the rollout. The part of the service that receives the change is "the canary," and the remainder of the service is "the control."" and "Canarying is effectively an A/B testing process."
- **Our assessment**: The definition is the transferable core for the guide: a canary is *not* merely "deploy to a subset" — it is deploy-to-a-subset **plus** an explicit evaluation loop plus integration of that evaluation into the release process (see Claim on requirements). This is the framing the guide's model/agent rollout content should use, since it makes the go/no-go decision a first-class part of the release pipeline rather than an afterthought.

### Claim 2: Canarying requires three capabilities — a way to deploy the change to a subset of the service population, an evaluation process that judges the canary "good" or "bad," and integration of that evaluation into the release process
- **Evidence**: The "Requirements of a Canary Process" section enumerates these three capabilities explicitly.
- **Confidence**: settled
- **Quote**: "A method to deploy the canary change to a subset of the population of the service." / "An evaluation process to evaluate if the canaried change is "good" or "bad."" / "Integration of the canary evaluations into the release process."
- **Our assessment**: A useful checklist for the guide's AI release tier: an LLM model canary that routes 5% of traffic but has no automated evaluation or no release-pipeline integration is only one-third of a canary process. The chapter also sets the value bar — "the canary process demonstrates value when canaries detect bad release candidates with high confidence, and identify good releases without false positives."

### Claim 3: Canaries exist because test environments are never identical to production — canarying exposes changes to real production traffic that unit/load testing miss, enabling defect detection with the smallest possible impact
- **Evidence**: The "What Is Canarying?" and "Release Engineering and Canarying" sections. The chapter notes some defects will always reach production because tests don't cover all scenarios, and "if a release deploys instantly everywhere, any defects will deploy in the same way."
- **Confidence**: settled
- **Quote**: "your test environments aren't 100% identical to production, and your tests probably don't cover 100% of possible scenarios." and "Introducing the change to actual production traffic also enables us to identify problems that might not be visible in testing frameworks like unit testing or load testing, which are often more artificial."
- **Our assessment**: The fundamental justification for canarying, and especially strong for LLM workloads where offline evals (the "test environment") systematically under-represent production input distributions. This corroborates the corpus's existing canary mandates and gives the model-canary argument a first-party authoritative basis.

### Claim 4: In Google's experience a majority of incidents are triggered by binary or configuration pushes — so instead of avoiding change, measure its reliability impact using SLOs and error budgets
- **Evidence**: The "Balancing Release Velocity and Reliability" section. Shipping and reliability are treated as reconcilable: "ship software as quickly as possible while meeting the reliability targets your users expect." The chapter also enumerates change types — underlying component behavior, dependency behavior (e.g., an API), and configuration like DNS.
- **Confidence**: settled
- **Quote**: "In Google's experience, a majority of incidents are triggered by binary or configuration pushes (see Results of Postmortem Analysis)."
- **Our assessment**: This is the safe-change-management evidence the Prospector flagged for Ch00/Ch02. For LLM ops, the implication is that model swaps, prompt changes, and gateway config pushes are exactly the "binary or configuration" changes that dominate incidents — and that error-budget measurement is the way to make them safe rather than freezing change.

### Claim 5: A deployment that cannot roll back forces the team to patch and redeploy during the outage, prolonging user impact — a canary with an error-rate evaluation enables pausing and rolling back a "bad" deployment instead
- **Evidence**: The worked comparison in "A Roll Forward Deployment Versus a Simple Canary Deployment." The naive deployment has "no option to roll back," so the fix is "to find defects in the production version, patch them, and deploy a new version during the outage." With a canary, "If the error rate of the canary metric is too far from the control error rate, this signals the canary deployment is "bad." In response, we should pause and roll back the deployment, or perhaps contact a human to help troubleshoot the issue."
- **Confidence**: settled
- **Quote**: "This course of action will almost certainly prolong the user impact of the bug." and "In response, we should pause and roll back the deployment, or perhaps contact a human to help troubleshoot the issue."
- **Our assessment**: The roll-forward vs. rollback trade is the core of the Prospector's key question. The chapter's position is that canarying exists to *make rollback the available option*; roll-forward (patch-during-outage) is the fallback when rollback infrastructure doesn't exist. For the guide's four-tier release taxonomy, this argues that a model/agent release tier without a rollback path is implicitly choosing the "prolong user impact" recovery.

### Claim 6: Error-budget impact is directly proportional to the traffic exposed to defects — a 5% canary at a 20% error rate yields a 1% overall error rate, conserving the error budget while learning about the new version
- **Evidence**: The "Minimizing Risk to SLOs and the Error Budget" section works the example. The model carries explicit assumptions: uniform load, entire remaining error budget available to canaries, 100% failure rate as a worst case, and system availability allowed to dip below SLO for the canary duration.
- **Confidence**: settled
- **Quote**: "If we instead use a canary population of 5%, we serve 20% errors for 5% of traffic, resulting in a 1% overall error rate" and "impact on the budget is directly proportional to the amount of traffic exposed to defects."
- **Our assessment**: The reusable sizing model for the guide. For LLM rollouts the same arithmetic applies: a new model version with a 20% failure (e.g., refusal-spike) canaried to 5% of traffic costs 1% overall error budget. The assumptions list matters — the model is a worst-case ceiling, not a precise predictor, and data leaks/incident impacts beyond availability are explicitly out of scope.

### Claim 7: Use the simplest error-budget model that meets your objectives — over-investing in model correctness leads to "incessant model tuning for no real benefit"
- **Evidence**: The chapter concedes "This model has clear flaws, but is a solid starting point that you can adjust to match business needs," then recommends simplicity. High-complexity services with overly complex models suffer endless tuning.
- **Confidence**: settled
- **Quote**: "We recommend using the simplest model that meets your technical and business objectives. In our experience, focusing on making the model as technically correct as possible often leads to overinvestment in modeling."
- **Our assessment**: Guidance against canary-methodology bikeshedding. For AI teams this is a caution against building statistically elaborate canary-evaluation models before the basic error-rate comparison is in place — start with the proportional model and add sophistication only when the business case demands it.

### Claim 8: Canary duration should track release cadence, and only one canary deployment should run at a time — overlapping canaries risk signal contamination and add mental effort to track system state
- **Evidence**: The "Choosing a Canary Population and Duration" section. Daily releases can't afford week-long canaries; continuous deployers need significantly shorter durations. Simultaneous canaries "adds significant mental effort to track system state" and "increases the risk of signal contamination."
- **Confidence**: settled
- **Quote**: "If you deploy continuously (for example, 20 times in a day), your canary duration must be significantly shorter." and "Running simultaneous canaries also increases the risk of signal contamination if the canaries overlap. We strongly advise running only one canary deployment at a time."
- **Our assessment**: A concrete, load-bearing rule for LLM release pipelines that ship frequently. For AI teams running multiple model/prompt promotions in parallel, the one-canary-at-a-time rule is a direct constraint on release cadence and a rationale for serializing promotions — and it flags a real failure mode (two overlapping model canaries whose error signals can't be attributed to either).

### Claim 9: A canary population must be representative across size/duration, traffic volume, time of day, and metrics — requirements that are "mutually at odds" — so tune parameters from historical canary failure rates rather than hypothetical worst cases
- **Evidence**: The representativeness dimensions enumerated in "Choosing a Canary Population and Duration": size and duration (a handful of queries gives no signal for diverse-query systems), traffic volume (homogeneous requests need less), time of day (performance defects manifest under heavy load), and metrics (queue depth needs more time/population than query success).
- **Confidence**: settled
- **Quote**: "Terminating a canary deployment after receiving just a handful of queries doesn't provide a useful signal for systems characterized by diverse queries with varied functionality." and "Canarying is a balancing act, informed both by cold analysis of worst-case scenarios and the past realistic track record of a system."
- **Our assessment**: The practical knob-setting guidance. For LLM canaries, "time of day" maps directly onto peak-inference-load windows (a model canary run only in off-peak hours would miss load-sensitive defects), and "diverse queries" maps onto prompt-distribution diversity — a canary fed only a narrow traffic slice is unrepresentative of the full prompt mix.

### Claim 10: For canary metric selection, start with SLIs, stack-rank candidate metrics by how well they indicate user-perceivable problems, and keep no more than ~a dozen — too many metrics bring diminishing returns and erode trust if unmaintained
- **Evidence**: The "Metrics Should Indicate Problems" section. SLIs already measured for SLO compliance can be reused. Each metric needs a defined acceptable-behavior threshold: too strict causes false positives, too loose lets bad canaries through, and "you need to reevaluate expectations on a regular basis."
- **Confidence**: settled
- **Quote**: "We typically recommend using SLIs as a place to start thinking about canary metrics. Good SLIs tend to have strong attribution to service health. If SLIs are already being measured to drive SLO compliance, we can reuse that work." and "Select the top few metrics to use in canary evaluations (perhaps no more than a dozen)."
- **Our assessment**: Directly portable to LLM rollouts: start from the LLM service's SLIs (latency, error rate) and add model-specific signals (refusal rate, eval regression, cost per request) as the stack-ranked top dozen. The false-positive/false-negative trade on thresholds is the same calibration problem the guide's LLM-ops content already grapples with for quality gates.

### Claim 11: Exclude 400-level HTTP codes from canary evaluation and add black-box URL-presence checks to isolate canary metrics from odd user behavior
- **Evidence**: The HTTP-return-code discussion in "Metrics Should Indicate Problems." 404s can come from broken shared URLs (user-driven) rather than the canaried change; the workaround is to exclude 400-level codes and add black-box monitoring for URL presence, folding that data into canary analysis.
- **Confidence**: settled
- **Quote**: "Often we can work around problems like this by excluding 400-level codes from our canary evaluation and adding black-box monitoring to test for the presence of a particular URL."
- **Our assessment**: A concrete metric-hygiene prescription with an LLM analog: exclude client-driven signals (e.g., user-input validation rejections) from model-canary evaluation and add black-box checks on key surfaces (e.g., the model actually responds to a canary-routed health probe). Prevents "odd user behavior" from flagging a good release as bad.

### Claim 12: Canary metrics must be attributable to the canaried change and isolated from shared-infrastructure noise — a noisy or flaky canary gets "disabled or ignored by operators, which can defeat the point of having a canary process"
- **Evidence**: The "Metrics Should Be Representative and Attributable" section. Whole-system CPU is a poor metric because other processes (database load, log rotation) drive it; a better metric is per-process CPU over the scheduled window. Outliers (oversubscribed machines, different kernels, overloaded network segments) make the canary-vs-control difference as much a function of infrastructure as of the change.
- **Confidence**: settled
- **Quote**: "A dramatic increase in CPU usage of the system as a whole would make for a poor metric, as other processes in the system (database load, log rotation, etc.) might be causing that increase." and "This can result in the canary process being disabled or ignored by operators, which can defeat the point of having a canary process in the first place."
- **Our assessment**: The attribution requirement is the highest-value metric lesson for LLM gateways, where many processes share one node: gateway-level aggregate metrics conflate the canaried model's behavior with tenant noise, autoscaler churn, and GPU contention. For the guide, this justifies per-model-version telemetry attribution as a canary prerequisite, not an enhancement.

### Claim 13: Before/after (time-segmented) canary evaluation is risky because time is one of the biggest sources of change in observed metrics — it cannot separate the change's degradation from organic variation such as weekday-vs-weekend usage
- **Evidence**: The "Before/After Evaluation Is Risky" section. A Monday release compared against a weekend baseline mixes business-day vs. weekend usage differences into the evaluation. The section also asks whether a big error spike from full replacement is better than a small-but-longer error rate from a small canary.
- **Confidence**: settled
- **Quote**: "Because time is one of the biggest sources of change in observed metrics, it is difficult to assess degradation of performance with before/after evaluation."
- **Our assessment**: The guide should distinguish before/after (full-replacement, time-comparison) canaries from true A/B (concurrent canary-vs-control) canaries, and prefer concurrent comparison for LLM rollouts. Note that the chapter itself classifies blue/green as "effectively performing a before/after canary" (see Related Concepts) — a limitation worth carrying into the guide's blue/green discussion.

### Claim 14: Use a gradual multi-stage canary — a small first stage evaluated on the clearest failure signals (application crashes, request failures), then progressively larger stages to build confidence
- **Evidence**: The "Use a Gradual Canary for Better Metric Selection" section. Early stages have no confidence in the release, so they use small populations and the clearest failure indicators; later stages carry larger populations and more nuanced metric analysis.
- **Confidence**: settled
- **Quote**: "In a small canary, we prefer metrics that are the clearest indication of a problem—application crashes, request failures, and the like. Once this stage passes successfully, the next stage will have a larger canary population to increase confidence in our analysis of the impact of the changes."
- **Our assessment**: The multi-stage pattern is the textbook basis for the guide's staged model-promotion tiers: stage 1 (tiny traffic, crash/refusal/error metrics only), stage N (larger traffic, full metric set). Matches and generalizes the concrete ramps in `docs-google-sre-prodcast-01-05` and the launch-plan notes.

### Claim 15: Canary and control populations share infrastructure imperfectly — including cross-request client state — so use absolute measures (e.g., defined SLOs) alongside the canary/control comparison, and don't assume the canary is at fault when evaluation flags a problem
- **Evidence**: The "Dependencies and Isolation" section. Two consecutive requests from one client can straddle the canary and control, with the canary's response altering the control's next request. A canary flag can reflect a shared-infrastructure issue rather than the canaried change.
- **Confidence**: settled
- **Quote**: "It is important to also use absolute measures, such as defined SLOs, to ensure the system is operating correctly." and "The first request may be handled by the canary deployment. The response by the canary may change the content of the second request, which may land on the control, altering the control's behavior."
- **Our assessment**: The "both A and B can change in tandem" warning is important for LLM canaries where a shared gateway, cache, or rate limiter sits in front of both model versions. Absolute SLO checks as a guard against misattributing shared-infrastructure faults to the canary is a concrete practice the guide should add to model-canary runbooks.

### Claim 16: Canarying noninteractive (batch/pipeline) systems requires three adaptations — canary duration must span at least one work unit, workers for a unit must come from a single pool (canary or control), and metrics cover end-to-end processing time plus application-specific output quality
- **Evidence**: The "Canarying in Noninteractive Systems" section. Work units in rendering/video pipelines can take far longer than interactive requests, so duration must span "the duration of a single work unit." In multistage pipelines a unit can be re-pooled between stages, so worker-pool isolation prevents "signals get increasingly mixed."
- **Confidence**: settled
- **Quote**: "Accordingly, make sure the canary duration at minimum spans the duration of a single work unit." and "It is helpful for canary analysis to ensure that the workers processing a particular unit of work are always pulled from the same pool of workers—either the canary pool or the control pool."
- **Our assessment**: Directly extends the batch-canarying treatment in `docs-google-sre-reliable-data-processing-minimal-toil` (population segmentation) with the missing duration and worker-isolation mechanics. For LLM batch work (embedding backfills, offline evals, scheduled agent jobs), this is the rule that a canary must run at least one full job end-to-end and must not let stages straddle pools.

### Claim 17: Monitoring data must support canary-vs-control breakdowns — whole-service aggregates hide a small canary — and metric aggregation intervals must be the same as or less than the canary duration
- **Evidence**: The "Requirements on Monitoring Data" section. A 5% canary at 20% errors is only a 1% overall error rate "indistinguishable from other sources of errors" at aggregate level; per-version breakdowns make it visible. The errors-per-hour example shows an hourly metric misfiring on a 30-minute canary.
- **Confidence**: settled
- **Quote**: "When collecting monitoring data, it is important to be able to perform fine-grained breakdowns that enable you to differentiate metrics between the canary and control populations." and "When using metrics to evaluate canary success, make sure the intervals of your metrics are either the same as or less than your canary duration."
- **Our assessment**: The observability prerequisite for trustworthy canaries, and the one most often missing in LLM stacks where dashboards aggregate across model versions and tenants. For the guide, this is a hard requirement to state before any model-canary guidance: if the gateway cannot break metrics down per model version, a 5% model canary is invisible. The aggregation-interval rule also directly bounds how short a canary may be given existing metric granularity.

### Claim 18: Blue/green, artificial load generation, and traffic teeing are related to canarying but are not canaries — synthetic load maximizes code coverage but not state coverage, and teeing is complicated in stateful systems
- **Evidence**: The "Related Concepts" section. Blue/green doubles resources and is "effectively performing a before/after canary"; artificial load "does a good job of maximizing code coverage, but doesn't provide good state coverage" and is dangerous on mutable systems like billing (could charge customers); traffic teeing "doesn't adequately identify risk in stateful systems" (a shared cache can inflate hit rates and invalidate performance measurements).
- **Confidence**: settled
- **Quote**: "Testing with synthetic load does a good job of maximizing code coverage, but doesn't provide good state coverage." and "One downside is that this setup uses twice as many resources as a more "traditional" deployment. In this setup, you are effectively performing a before/after canary (discussed earlier)."
- **Our assessment**: Useful boundary definitions for the guide's deployment-technique taxonomy. For LLM ops: shadow-mode (teeing) of a new model is explicitly not a canary and is unreliable for stateful services; load-testing an LLM gateway improves code coverage but won't surface prompt-distribution state coverage gaps that real-traffic canaries catch. Billing-risk caution applies to agent workloads that make external side-effectful calls.

## Concrete Artifacts

### Artifact A — Release engineering principles (Chapter opening, verbatim)

```
Reproducible builds
- The build system should be able to take the build inputs (source code, assets, and so on) and produce repeatable artifacts.
Automated builds
- Once code is checked in, automation should produce build artifacts and upload them to a storage system.
Automated tests
- Once the automated build system builds artifacts, a test suite of some kind should ensure they function.
Automated deployments
- Deployments should be performed by computers, not humans.
Small deployments
- Build artifacts should contain small, self-contained changes.
```

### Artifact B — The error-budget sizing model and its assumptions (section "Minimizing Risk to SLOs and the Error Budget")

```
Worked example: 5% canary × 20% error rate → 1% overall error rate.
"Impact on the budget is directly proportional to the amount of traffic exposed to defects."

Explicit model assumptions:
- "This is a very simple model that assumes uniform load."
- Assumes the entire error budget (beyond the organic measurement of current availability) can be spent on canaries.
- Considers only unavailability introduced by new releases, "rather than actual availability."
- "Our model also assumes a 100% failure rate because this is a worst-case scenario."
- "We also allow overall system availability to go below SLO for the duration of the canary deployment."
- Out of scope: incidents such as a data leak ("This analysis obviously does not cover the impact of incidents, such as a data leak.")

Recommendation: "We recommend using the simplest model that meets your technical and business objectives."
```

### Artifact C — The errors-per-hour monitoring timeline (section "Requirements on Monitoring Data", verbatim steps)

```
1. "An unrelated event causes some errors to occur."
2. "A canary is deployed to 5% of the population; the canary duration is 30 minutes."
3. "The canary system starts to watch the errors-per-hour metric to see if the deployment is good or bad."
4. "The deployment is detected as bad because the errors-per-hour metric is significantly different from the errors per hour of the control population."
5. "This scenario is a result of using a metric that is computed hourly to evaluate a deployment that is only 30 minutes long."
```

### Artifact D — Worked App Engine example setup and traffic-splitting methods (sections "Our Example Setup" / "A Roll Forward Deployment Versus a Simple Canary Deployment")

The example application exposes an HTTP API over product-price data, with tunable parameters "to simulate various production symptoms, to be evaluated by the canary process" — e.g., "we can make the application return errors for 20% of requests, or we can stipulate that 5% of requests take at least two seconds." Two versions exist: "live" (currently in production) and "release candidate" (newly built). The canary "splits traffic between specific labeled versions of our application." Traffic-splitting options:

```
"You can split traffic using App Engine, or any number of other methods, such as
backend weights on a load balancer, proxy configurations, or round-robin DNS records."
```

Evaluation: "We can now tune our deployment to automatically react based on the HTTP error rate by App Engine version. If the error rate of the canary metric is too far from the control error rate, this signals the canary deployment is 'bad.'"

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

The following candidates from `miner-related-notes.md` were evaluated:

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3077) — **Dismissed.** Covers sociotechnical complexity and incomplete mental models. The canary chapter is release-process mechanics with no complexity-theory claims to corroborate or contradict.

2. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2308) — **Dismissed.** Covers incident-response tooling breadth and on-call collaboration. No canary/release claims.

3. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2308) — **Dismissed.** Covers SRE concepts outside Google and scale shock. No canary mechanics.

4. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2308) — **Dismissed.** Covers AI-for-SRE tooling (outage detection, ticket analysis). No canary content.

5. **`docs-google-sre-prodcast.md`** (score 0.2308) — **Dismissed.** Prodcast index with episode listings; no substantive claims to cross-reference.

6. **`docs-google-sre-prodcast-03-05-building-reliable-systems.md`** (score 0.2051) — **Dismissed.** Covers database reliability culture and "predict failure" planning. No canary mechanics that this chapter corroborates or contradicts.

7. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2051) — **Corroborates** Claim 1 (SLOs as a shared vernacular for reliability communication). The canary chapter's error-budget model (Claim 6 here) operates on the premise that SLO/error-budget infrastructure exists and is the shared framework for reliability decisions; S5E2's Claim 1 is the same premise stated as a communication principle. Both treat SLOs as the language in which release decisions (including canary go/no-go) are denominated. The link is premise-level, not mechanical — the two sources do not overlap on canary procedure.

8. **`docs-google-sre-reliable-product-launches.md`** (score 0.2051) — **Corroborates/Extends.** Claim 10 (gradual rollouts with canary testing are the standard deployment pattern, automatic rollback on validation failure). The SRE Book launch chapter states the pattern; this Workbook chapter is the deep treatment of the same pattern's mechanics (error-budget sizing, metric selection, monitoring prerequisites, noninteractive canarying). See Cross-References → Corroborates/Extends for the specific claim mapping.

9. **`docs-google-sre-handling-overload.md`** (score 0.2051) — **Dismissed.** Covers load shedding, capacity reserves, and retry behavior under overload. The canary chapter does not address overload handling; the load-shedding claims neither corroborate nor contradict canary mechanics.

10. **`blog-incidentio-ai-sre-incident-run.md`** (score 0.2051) — **Dismissed.** Covers an AI SRE agent running incident response via Claude Code/incident.io. No canary or release-engineering claims.

### Primary cross-references (from the Prospector's triage and manual search)

- **Corroborates**:
  - `docs-google-sre-twenty-years-lessons.md` **Claim 3** (canary all changes with progressive rollout — a YouTube config change "pretty sure" to be safe "fully hobbled the service for 13 minutes"). The workbook's Claim 4 (majority of incidents from binary/config pushes) and Claim 3 (canaries detect defects before full impact) provide the mechanism and justification for the lessons' canary mandate; the lessons note supplies the quantified cost of skipping a canary. Mutual reinforcement.
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` **Claim 13** (batch canarying via segmented populations — `hash(userid) mod 10 == 0`). This chapter's Claim 16 (noninteractive canarying: work-unit-spanning duration, worker-pool isolation, end-to-end + quality metrics) corroborates the same doctrine for batch work and adds the mechanics that note does not cover. No contradiction: the data-processing note's population segmentation is the *how* for selecting the canary set; this chapter's duration/isolation rules are the *how* for evaluating it.
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` **Claim 15** (gradual rollout specifics — start ≤0.001%, below the error budget, hold a week, accelerate after 5%, cap each step at ≤15%) and **Claim 16** (random traffic selection). The Prodcast's concrete ramp is an implementation of this chapter's principles: population tied to cadence, gradual multi-stage canaries (Claim 14 here), and start-below-error-budget matching the error-budget sizing model (Claim 6 here). The workbook provides the textbook rationale for Pavan's numbers.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` **Claim 8** (progressive rollout/canary is a strategy above IaC, achievable declaratively or imperatively). This chapter's Claim 1 (canarying is a process: deploy-to-subset + evaluation + integration) and Claim 2 (three requirements including evaluation integration) corroborate the same decoupling — canary is not a deployment-mechanism property; the App Engine/LB/DNS traffic-split methods (Artifact D) are the "vehicles" Dominic refers to.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` **Claim 12** (weighted-DNS canary 0%→1%→5%+ via weighted CNAMEs when no blue/green infra exists). The weighted-DNS mechanism is a concrete instance of the traffic-splitting options this chapter enumerates ("backend weights on a load balancer, proxy configurations, or round-robin DNS records," Artifact D), and the "start tiny, ramp on confidence, accept bounded blast radius" structure matches the chapter's gradual-canary and error-budget guidance.
  - `docs-google-sre-creating-production-launch-plan.md` **Claim 7** (launch stages EAP/Alpha/Beta/GA with gradual traffic diversion 1%→2%→5%→10%→100%) and **Claim 8** (dark launches expose production traffic without rendering results, enabling canary testing). The launch-plan note's staged diversions are instances of this chapter's gradual multi-stage canary (Claim 14); the chapter's "traffic teeing" discussion (Claim 18) is the mechanics behind the dark-launch concept.
  - `blog-promptfoo-model-upgrades-break-agent-safety.md` **Claim 2** (model upgrades are security changes — pin and canary: "Pin model IDs and safety settings — do not ship 'latest'", canary in staging with sampled production traffic) and **Concrete Artifacts → Model Upgrade Checklist** (step 1 "Pin and canary"). This is the LLM-domain instantiation of the workbook's canary process: the promptfoo checklist's pin-and-canary step implements the deploy-to-subset + evaluation loop, and its "re-run safety suites / compare behavioral deltas" steps are the metric-selection prescription (Claims 10-12 here) applied to model swaps. The workbook chapter gives the AI-domain practice its release-engineering basis.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` **Claim 1** — see Candidates list above.

- **Contradicts**: None identified, and no contradiction issue filed. The chapter is a process/mechanics treatment and agrees with every canary-related claim already in the corpus. Potential tensions checked and resolved as conditioning variables rather than contradictions: (a) the chapter's "we strongly advise running only one canary deployment at a time" (Claim 8) vs. the cascading-rollouts scheduling in `docs-google-sre-reliable-data-processing-minimal-toil.md` Claim 14 — those are *sequential* gated releases with dynamic start times, not overlapping canaries of different changes, so no conflict; (b) the error-budget model's premise that canaries may consume budget vs. the S5E2 retraction of "error budget → ship features" (`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claim 14) — the workbook is quantifying *how much* budget a canary costs, not asserting how budget should be spent, so no contradiction; (c) before/after evaluation being risky (Claim 13 here) vs. blue/green usage in `docs-google-sre-prodcast-03-07-retail-gaming.md` Claim 12 — the retail-gaming note explicitly frames weighted-DNS as a substitute *because* blue/green infra is absent, consistent with the workbook's classification of blue/green as an effective before/after canary.

- **Extends**:
  - `docs-google-sre-reliable-product-launches.md` **Claim 10** — the SRE Book launch chapter states the gradual-rollout pattern at a high level; this chapter is the full mechanics (error-budget sizing, population/duration selection, metric selection, monitoring requirements) that the launch chapter assumes. Also extends that note's Claim 11 (feature-flag requirements) indirectly: the workbook's "Separating Components That Change at Different Rates" section (feature flags/experiment frameworks like Gertrude, Feature, PlanOut to separate feature launches from binary releases) corroborates the flag-driven rollout principle from the deployment side.
  - `docs-google-sre-creating-production-launch-plan.md` **Claim 7** — the launch plan's gradual traffic diversion schedule now has its evaluation methodology (what to compare, what monitoring must exist, how long to hold) from this chapter.
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` **Claim 15** — Pavan's ramp schedule (0.001%→5%→15%, < error budget, hold a week) is now grounded in the textbook rationale for *why* each knob is set as it is.
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` **Claim 13** — adds the missing duration/isolation mechanics (work-unit-spanning canary duration, single-pool worker assignment) to the population-based batch canarying treatment.
  - `docs-google-sre-infrastructure-change-management.md` **Claim 15** (the 10-item Preflight Checklist synthesized from Google's large-scale migration case studies) — the ICM note covers the *planning* discipline for large infrastructure change; this chapter covers the *deployment-time* discipline (canary evaluation, rollback decisions) that preflight-checked changes run under. Complementary: preflight planning (ICM) then canary validation (this chapter).
  - `docs-google-sre-incident-metrics-in-sre.md` — **Dismissed as a cross-reference.** The note concerns statistical evaluation of incident-response improvement via MTTx (high-variance aggregate statistics). It shares only a surface theme ("metric quality matters") with this chapter's metric-selection and monitoring-data sections; the claims do not overlap on canary mechanics, so it is not cited as corroboration. Included here so the Prospector's overlap mention is explicitly accounted for.

- **Novel**: Content new to the corpus:
  - **The formal canary definition and three-process requirement** (Claims 1-2) — deploy-to-subset + evaluation + release-process integration as a definitional checklist. Existing notes treat canarying as "deploy to a fraction and observe"; none state the evaluation-integration requirement explicitly.
  - **The error-budget sizing model** (Claims 6-7, Artifact B) — impact-proportional-to-exposed-traffic arithmetic (5%×20%→1%) with the explicit assumptions list and "simplest model" guidance. The most concrete transferable knob for the guide's release-maturity tiers.
  - **Canary-vs-control monitoring data requirements** (Claim 17, Artifact C) — per-population metric breakdowns and the aggregation-interval ≤ canary-duration rule, with the errors-per-hour worked timeline. An observability prerequisite no existing note states.
  - **Canary metric-selection guidance** (Claims 10-12) — SLI starting point, stack-ranking with a ~dozen cap, 400-level-code exclusion + black-box URL checks, attribution to the canaried change, and the noisy-metric-→-operator-distrust failure mode.
  - **Noninteractive canarying mechanics** (Claim 16) — work-unit-spanning duration and worker-pool isolation, extending the batch-canarying note with the missing evaluation rules.
  - **Before/after evaluation risk** (Claim 13) and the **one-canary-at-a-time rule** (Claim 8) — time-segmentation noise and signal-contamination constraints absent from prior notes.
  - **Related-techniques taxonomy** (Claim 18) — the explicit blue/green ("effectively a before/after canary"), artificial-load ("maximizes code coverage, but doesn't provide good state coverage"), and traffic-teeing distinctions, including the stateful-system hazards (shared cache invalidating teed measurements, billing risk of synthetic load).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability / Release Engineering)**: The most impacted chapter. This is the canonical mechanics reference the guide's release-engineering tiers should cite. Add: (a) the three-requirement canary definition (Claim 2) as the checklist for model/agent canary processes — every release tier must specify the deploy-to-subset method, the evaluation, and the pipeline integration; (b) the error-budget sizing model (Claims 6-7) as the exposure-sizing rule for model promotion — a model swap's error-budget cost equals its failure rate × exposed traffic fraction, sized with the simplest model that meets objectives; (c) metric-selection guidance for model canaries (Claims 10-12) — start from LLM SLIs (latency, error rate) plus model-specific signals (refusal rate, eval regression, cost/request), stack-ranked to ≤ a dozen, excluding client-driven signals and adding black-box model-response checks; (d) the monitoring-data prerequisites (Claim 17) as a hard gate before model canarying is allowed — per-model-version telemetry breakdowns and aggregation granularity finer than the canary window (gateway-wide aggregates hide a 5% model canary); (e) the gradual multi-stage canary (Claim 14) as the structure for the four-tier release taxonomy (tiny stage on crash/refusal metrics → larger stages); (f) rollback-vs-roll-forward decision guidance (Claim 5) — a release tier without a rollback path is implicitly choosing the "patch-during-outage" recovery; (g) the one-canary-at-a-time rule (Claim 8) for teams promoting multiple model/prompt/agent changes in parallel.

- **Chapter 02 (SLOs / Error Budgets)**: Add the error-budget sizing model (Claims 6-7) as the canonical worked example of how canaries interact with error budgets, and the monitoring-data requirements (Claim 17, Artifact C) as SLO-measurement prerequisites — if a service can't break metrics down per canary-vs-control population, its SLO data is too coarse to trust for release decisions. Add the before/after-evaluation risk (Claim 13) as a caution on time-segmented comparisons anywhere in SLO analysis.

- **Chapter 03 (Agents / Runbooks)**: Add the canary go/no-go criteria and the pause-and-rollback decision (Claim 5) to the runbooks for agents that trigger rollouts, and the error-rate-diff triage pattern (canary vs. control deviation → pause/rollback vs. proceed, from Artifact D). Add the attribution requirement (Claim 12) to agent-release telemetry design. Add the noninteractive canarying rules (Claim 16) to the runbook for batch agent jobs (embedding backfills, scheduled evals) — canary must span a full work unit and must not straddle worker pools.

- **Chapter 04 (Automation & Toil)**: Add the release-engineering principles (Artifact A) as the automation prerequisite for canarying — reproducible builds, automated tests/deployments, and small self-contained changes are what make canaries cheap enough to run on every change, and the "virtuous cycle of CI/CD" (more releases → smaller changes → cheaper rollbacks) as the toil-reduction rationale.

- **Chapter 00 (Principles)**: Add Claim 4 (a majority of incidents are triggered by binary or configuration pushes) as the safe-change-management evidence, and the framing that change itself is not the enemy — SLOs/error budgets plus canarying are how change is made safe. Add the canary-definition principle (Claim 1) — a canary without an evaluation loop and pipeline integration is not a canary — as a definitional standard for all guide deployment content.

## Extraction Notes

- The full chapter at https://sre.google/workbook/canarying-releases/ was fetched and read end-to-end in a single WebFetch. The chapter's linked sibling pages (Implementing SLOs, Data Processing Pipelines, Postmortem Analysis, SRE Book release engineering) were not followed per the Prospector's guidance — the chapter itself is the substantive source and its cross-links are covered by existing source notes already in the corpus.
- All quotes were copied verbatim from the fetched chapter text. Where a sentence carried a trailing parenthetical reference to a figure or footnote, the quote was trimmed to the contiguous fragment carrying the meaning (e.g., Claim 6's "resulting in a 1% overall error rate" without the "(as seen earlier in Figure 16-3)" suffix). No two non-adjacent sentences were spliced into a single quoted passage.
- `date_published` is the Workbook's 2018 publication year (O'Reilly, April 2018). Per the Prospector's third triage comment, this 2018-era source is deliberately treated as evergreen canonical SRE practice via the `sre-workbook` site-crawl seed; the pre-Dec-2025 rejection rule does not apply to this curation, and the claims are timeless release-engineering practice, mined at `settled` confidence.
- `confidence_overall` is `settled`: the source is the canonical Google SRE Workbook, authored by named Google SRE practitioners, hosted on the official sre.google domain, and the claims are explicit process prescriptions with a worked example and quantified model. No AI-landscape staleness concerns apply.
- No contradiction issue was filed (see Cross-References → Contradicts for the three tension points checked and resolved as conditioning variables).
- One WebFetch caveat: the fast-model WebFetch of the sre.google page returned the chapter's full text in structured form. Spot-check any high-value quotes (especially Claims 1, 6, 14, 17) against the live URL if the Assayer wants extra confidence.
