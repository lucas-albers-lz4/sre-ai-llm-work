---
source_url: https://sre.google/static/pdf/reliable_data_processing_with_minimal_toil.pdf
source_type: docs
title: "Reliable Data Processing with Minimal Toil"
author: "Pieter Coucke and Rita Sodt (Google), with Julia Lee (Slack), Rich Feit (Google), Athena Vawda (Google), Betsy Beyer (Google), and John Lunney (Google)"
date_published: 2021-10-12
date_extracted: 2026-08-02
last_checked: 2026-08-02
status: current
confidence_overall: settled
issue: "#725"
---

# Reliable Data Processing with Minimal Toil

> An official Google SRE paper (Oct 2021) that defines a safety-levels framework
> (0–3) for batch data-processing jobs, a three-stage release pipeline
> (Autopush/Staging/Production) with dry-run semantics, automated validation
> techniques (counter validation, data validation, A/B testing, two-phase
> mutation), and population-based canarying — the concrete mechanism by which
> automation removes manual verification toil from batch-job changes. Includes
> case studies of Google's internal Batch Platform (450+ teams) and Slack's
> async compute (criticality buckets, Job Registry). The first corpus source on
> batch/data-pipeline reliability.

## Source Context

- **Type**: docs — official Google SRE paper ("Google SRE - Reliable batch
  processing with minimal toil"), distributed as a static PDF on sre.google.
  Also presented at SREcon21 (Coucke & Lee). Licensed CC BY-NC-ND 4.0.
- **Author credibility**: Highest available. Pieter Coucke (Technical Program
  Manager, Google SRE Zürich, Google Workspace) and Rita Sodt (Google SRE),
  with contributors from Google and Slack (Julia Lee leads Slack's asynchronous
  compute services; Athena Vawda is Google Batch Platform Lead; Betsy Beyer is
  a founding editor of the SRE Book/Workbook). First-party practitioner account
  of systems the authors built and operate at Google Workspace scale.
- **Scope**: Covers (a) why batch jobs become "haunted graveyards"; (b) batch-job
  economics and risk profile; (c) correctness vs. freshness SLOs; (d) the four
  safety levels (0–3) and their attached manual-verification policies; (e) the
  Batch Platform standardization effort; (f) the three-stage release pipeline
  (Autopush/Staging/Production) with dry-run semantics; (g) automated validation
  techniques — start-up tests, process exit codes, counter validation, data
  validation, A/B testing, resource-overload detection, soak time, cascading
  rollouts; (h) canarying batch jobs via segmented/target populations; (i)
  freshness-SLO operations (on-call, alerting on schedule overrun); (j)
  batch vs. event-based processing tradeoffs; (k) the Slack async-compute case
  study. Does NOT cover streaming-pipeline specifics (points to SRE Workbook
  Ch13 for that), monitoring/alerting implementation detail, or LLM/ML serving
  directly — though the batch patterns transfer to ML/LLM data pipelines.

## Extracted Claims

### Claim 1: Batch jobs that run reliably for years tend to be forgotten and become unsafe "haunted graveyards" — lacking the monitoring, alerting, and rollout framework that user-facing services enjoy
- **Evidence**: Practitioner observation from Google Workspace: batch jobs run
  "reliably for several years," so teams neglect them; changes are "largely
  manual and time-consuming," and unlike user-facing services, batch-job teams
  "were left to set up most of this infrastructure themselves" (monitoring,
  alerting, rollouts) and lacked basic canarying capabilities. Term coined by
  John Reese in "No Haunted Graveyards."
- **Confidence**: settled
- **Quote**: "Batch jobs typically do one thing well and run reliably for several years. As a consequence, people tend to forget about batch jobs, and they become unsafe \"haunted graveyards\": places where you don't really care to venture, where ugly surprises are likely to bite you in the back."
- **Our assessment**: This is the motivational frame for the whole paper and
  matches the SRE Book's toil thesis. Directly transferable to LLM-ops: eval-data
  refresh jobs, embedding/index backfills, and training-data preprocessing are
  exactly the kind of "runs reliably, so nobody touches it" jobs that accumulate
  this neglect. The claim is settled — it is Google's stated operational
  experience and matches the corpus's toil-reduction doctrine.

### Claim 2: Freezing all batch-job rollouts backfired — a blanket change stop caused a different outage because dependencies (e.g., deprecated API versions) broke over time and the failures were hard to detect since nothing was deployed
- **Evidence**: Google Workspace declared "an emergency stop on rolling out
  changes to batch jobs"; dependencies "tended to break after some period of
  time," and detection was especially hard "since nothing was actually
  deployed."
- **Confidence**: settled
- **Quote**: "When we realized that our batch jobs were problematic, we temporarily declared an emergency stop on rolling out changes to batch jobs. This stop led to yet another outage: dependencies (for example, a dependency on a deprecated API version) tended to break after some period of time."
- **Our assessment**: A valuable nuance against the naive "freeze all changes"
  response to batch-job risk. It parallels Treynor's error-budget launch-freeze
  doctrine (see Cross-References) but shows a freeze on *unattended batch jobs*
  creates its own failure mode (rot). The paper's answer is not "stop changing
  batch jobs" but "make changing them safe and cheap" — the core toil-reduction
  insight. We buy this; it's a documented causal chain.

### Claim 3: A batch job is defined as a job that performs a finite amount of work then terminates; it can be scheduled, one-off (e.g., data-corruption repair), or triggered by another process
- **Evidence**: Paper's "What is a Batch Job?" section gives the definition plus
  the Drive-trash example (a nightly job scanning all users and deleting trash
  files after 30 days).
- **Confidence**: settled
- **Quote**: "We define a batch job as a job that performs some finite amount of work (typically by scanning over data or storage), then terminates."
- **Our assessment**: A crisp operational definition that the guide can use to
  classify LLM data work: periodic backfills, batch inference, report generation,
  index rebuilds, correctness checks, and bulk imports all fit. Settled — it's
  an explicit definition from an authoritative source.

### Claim 4: Batch jobs are compute- and cost-efficient — they run off-peak on unused or preemptible resources, making them well-suited for simple transformations like pre-processing a machine learning model
- **Evidence**: Paper lists benefits: "compute- and often cost-efficient,"
  run "during off-peak hours on unused resources" and are "essentially free
  given a large enough deployment of compute power," or on "cheaper preemptible
  instances"; use cases include "pre-processing a machine learning model,"
  report generation, indexing, correctness checks, and bulk imports.
- **Confidence**: settled
- **Quote**: "As a result, batch jobs are well-suited for analysis and for performing simple transformations of data like pre-processing a machine learning model."
- **Our assessment**: The paper explicitly names ML preprocessing as a canonical
  batch-job use case — the direct bridge to Ch05 (LLM-ops reliability). This is
  settled economics, though the "essentially free" claim is conditioned on
  large-scale compute deployment.

### Claim 5: Batch jobs carry a distinctive risk profile — large blast radius, data corruption, downstream delay propagation, staleness, and overloaded downstream services — and corrupt or delayed output from one job propagates rapidly through dependent systems
- **Evidence**: The "Challenges" section enumerates these failure modes; the
  downstream-delay case is explicit: batch-job output is often input to another
  batch job and may feed "user-facing serving jobs."
- **Confidence**: settled
- **Quote**: "The output (for example, the modified storage) of a batch job may also be used by user-facing serving jobs. Corrupt or delayed data from a single job can rapidly propagate through a system, which makes repairs difficult and time-intensive."
- **Our assessment**: The blast-radius framing is the risk lens the rest of the
  paper builds on. For LLM-ops this maps to: a bad embedding backfill or a stale
  training dataset propagates into model-serving quality. The "a job that removes
  data from an inactive account after 60 days has the potential to remove data
  for every user if the selection criteria has a wrong value" example is a
  concrete blast-radius illustration.

### Claim 6: Data processing is reliable when well-reasoned SLOs are met — with two distinct kinds: the freshness SLO ("Did the job complete in time?") and the correctness SLO ("Did the job produce the correct results?"), and a job meeting freshness is not necessarily safe
- **Evidence**: The paper defines reliability via SLOs and explicitly separates
  the two; footnote 6 states jobs meeting a freshness SLO "aren't necessarily
  safe— in other words, they might not meet the correctness SLO." Example: making
  Google Analytics data available to a webmaster within an hour.
- **Confidence**: settled
- **Quote**: "To apply an SRE approach, we can declare data processing to be reliable if well-reasoned SLOs are met."
- **Our assessment**: The correctness-vs-freshness distinction is a durable
  contribution: freshness is easy to measure (time since last successful
  completion) while correctness may have "no predefined correct output" — the
  paper later suggests generating "golden data" to measure it. For LLM eval
  pipelines this is the exact freshness/correctness split the guide needs (did
  the eval batch complete on time vs. did it produce correct labels).

### Claim 7: Safety levels (0–3) classify how risky a batch-job change is by how much data a single run modifies — Level 0 modifies the entire dataset, Level 3 is a fully automated phased rollout with no humans involved — and each level's policy sets how much manual verification (toil) is required per change
- **Evidence**: Table 1 defines the four levels: Level 0 = entire dataset in a
  single run; Level 1 = canaried (manual or automated); Level 2 = gradually
  rolled out first to less risky populations then globally; Level 3 = Levels 1
  and 2 met plus "no humans are involved in the phased rollout." The paper
  states the tradeoff directly.
- **Confidence**: settled
- **Quote**: "A higher (and thus safer) level indicates that a rollout has a smaller blast radius."
- **Quote**: "This system incentivizes teams to modify their jobs to comply with the highest safety level, since doing so reduces their toil and increases release velocity by removing obstacles."
- **Quote**: "The lower the safety level, the more manual verifications we ask a team to perform for a change."
- **Our assessment**: This is the highest-value claim in the paper for the
  corpus's Ch04 toil chapter. It is an explicit toil↔safety tradeoff: automation
  (Level 3) directly removes manual verification work, and the framework
  incentivizes teams to climb to Level 3. This is precisely the "auto-remediation
  candidates vs. always-manual classes" distinction the Ch04 stub targets — the
  four levels are a citable mechanism for deciding what can be automated. The
  adoption approach (identify risky changes up front, ban whole-dataset jobs,
  prioritize the riskiest user-impacting jobs, then build conformance tooling)
  is operationalizable.

### Claim 8: Standardizing on a common platform (the Batch Platform) removes duplicated production-setup work — following "convention over configuration" — and is already serving over 450 teams at Google
- **Evidence**: Athena Vawda (Batch Platform Lead) authored section: individual
  teams "often end up duplicating work that has already been done by others";
  the platform provides "sensible defaults," scales expertise, increases
  productivity, eases incident response, and exposes structured job data. Metric:
  "making life easier for over 450 teams across the company."
- **Confidence**: settled
- **Quote**: "the platform configures all of the infrastructure needed to accomplish that goal, following the principle of convention over configuration so that the user can benefit from sensible defaults rather than specifying every last detail of their setup."
- **Quote**: "The Batch Platform is much newer, but we're already making life easier for over 450 teams across the company."
- **Our assessment**: A platform-with-defaults pattern is how Google scales the
  safety-level policy without per-team rework — "saving individual product teams
  from having to develop their own solutions to this problem." For the guide this
  supports a "platform not policy-pamphlet" recommendation: encode rollout,
  canary, and validation defaults into a shared batch platform rather than asking
  each LLM data team to reinvent them.

### Claim 9: Batch-job releases go through three release-pipeline stages — Autopush, Staging, Production — promoted on a fixed schedule when release certifications pass, and the code-deployment schedule is deliberately decoupled from the job-run schedule
- **Evidence**: Table 2 details the stages: Autopush (dry run; every two hours
  checks "Does this compile, pass tests, and run?" on a Test dataset), Staging
  (dry run; runs new and old versions in an A/B test of output/counters; versions
  typically stay for "days or a week"), Production (supports multiple arbitrary
  canary stages). The deployment-vs-run schedule split is stated explicitly.
- **Confidence**: settled
- **Quote**: "We typically define three release stages, detailed in Table 2: Autopush, Staging, and Production. The release is promoted to the next stage on a fixed schedule when release certifications at that stage pass."
- **Quote**: "The code deployment schedule is completely different from the job run schedule. For example, it is common in production to have a daily run but only a weekly release."
- **Our assessment**: Applies standard service release engineering to batch
  jobs — the paper's whole point is that batch jobs were under-served here. The
  Autopush→Staging→Production ladder maps directly onto LLM data-pipeline
  changes (eval-data refresh, embedding backfill) and to model promotion. The
  deploy-schedule ≠ run-schedule observation is a concrete operational detail:
  a daily-running job can still ship weekly.

### Claim 10: A dry run (job skips its writing phase) contains failures to a single binary — configurable via a script parameter, or via writing to a temp location enforced with dataset permissions
- **Evidence**: The paper defines dry-run semantics and both enforcement options
  (a start-script parameter, or writing to a "temp location not consumed by any
  other process... enforce this setup with permissions").
- **Confidence**: settled
- **Quote**: "A dry run means the job skips the writing phase and does not produce any changes that affect other parts of the system. This ensures that an error stays limited to a particular binary."
- **Our assessment**: A concrete, copyable mechanism. For LLM-ops this is the
  read-only preview of a dataset mutation before it touches production storage —
  the same idea as the mandatory `dry_run=true` API mode in the AI-in-SRE note
  (see Cross-References), applied to batch jobs.

### Claim 11: Promotion stability checks should be automated, and validation design must minimize false positives — counter anomalies, range/percentage (not exact) counter comparisons, read-only data validation, and A/B testing on identical input
- **Evidence**: Section "Removing Manual Checks with Automated Validations":
  start-up tests validate preconditions before reading/writing; exit code 0/other
  is a basic signal; "We've found evidence that looking for counter anomalies...
  could have prevented major issues"; exact comparisons are "sometimes too
  noisy" so use ranges or percentages; data-validation jobs should run read-only
  under least privilege; A/B run new version in dry-run mode on "the exact same
  input" and compare counters or data.
- **Confidence**: settled
- **Quote**: "You should aim to minimize false positives (meaning that a job is incorrectly labeled as unstable), as they require manual intervention to investigate and therefore introduce rollout delays."
- **Quote**: "Exact number comparisons are sometimes too noisy. A different approach is to use ranges (for example, the value should fall between X and Y) or percentages (for example, records processed must be between 10% and 20% of the total dataset)."
- **Quote**: "Run the new version in dry-run mode (so that you don't write to any storage) on the exact same input as the previous version (ideally also running in dry-run mode) and compare the counters. Or, even better, compare the data itself."
- **Our assessment**: This is the paper's most directly reusable engineering
  detail. The false-positive-minimization principle matters for LLM eval gates:
  an over-sensitive validation (e.g., exact-match eval-score comparison) produces
  manual investigation toil — exactly the toil the framework is meant to remove.
  Counter-validation with ranges/percentages is a concrete pattern for
  "did the embedding backfill process the expected share of the corpus." Settled
  — evidenced by the paper's Google Workspace experience.

### Claim 12: The two-phase mutation design pattern stages mutations in a temporary location, validates them separately, and applies them only after validation passes — enabling dry-runs, validations, and A/B testing without making actual changes
- **Evidence**: The pattern is defined in "Idempotent and Two-Phase Mutations":
  store candidates (like IDs), perform API calls "in a separate process," then
  apply verified mutations only after validation. Privacy caution: unique
  identifiers may encode private user information and must be protected "even
  between different phases of the mutation." Can also run continuously in
  production as a health monitor.
- **Confidence**: settled
- **Quote**: "This approach entails storing candidates (like IDs) somewhere, and then performing API calls with these IDs in a separate process. This split allows validations, dry-runs, and A/B testing on the list of IDs without making actual changes."
- **Our assessment**: The two-phase mutation pattern is the strongest
  "concrete artifact" here for the guide: it is the safe-mutation primitive for
  dataset backfills and index rebuilds (plan changes in a staging store, validate,
  then apply). The privacy caution (IDs may encode PII) is a security-relevant
  detail the guide's data-path chapters should carry. Settled.

### Claim 13: Canarying a batch process must be based on segmented populations (users/customers/any logical object in the data model), not traffic segmentation — implemented via a startup parameter like hash(userid) mod 10 == 0, and idempotent jobs make canary-vs-production comparison possible
- **Evidence**: The paper contrasts serving-canary traffic segmentation (which
  "doesn't map to a batch process") with population segmentation; gives the
  `hash(userid) mod 10 == 0` example for a "10% prod" canary; describes target
  populations (canary-for-developers-team → canary-for-employees →
  canary-production-1%-free-users) driven by a single config flag; and a reusable
  targeting library "for typical user and customer selection criteria."
- **Confidence**: settled
- **Quote**: "canarying for batch processes needs to happen based on segmented populations— this is typically users or customers, but can more generally be any logical objects in the data model."
- **Quote**: "For the canary, this parameter might be defined as \"10% prod\" and implemented as a filter to process only records where hash(userid) mod 10 == 0 to run on 10% of production users."
- **Quote**: "Having idempotent jobs is especially useful when you want to compare the outcome of the canary run with the production run."
- **Our assessment**: A key conceptual adaptation of canarying for data work and
  directly portable to LLM-ops: canary an embedding backfill on a hash-defined
  slice of the corpus, or a new eval dataset on a subset of tenants before full
  promotion. The target-population ladder (internal → employees → free users) is
  the same staged-population pattern Google uses for user-facing changes. Settled.

### Claim 14: Soak time and cascading rollouts manage the time cost of gated batch releases — enough verification window for worst-case runtime, or dynamic start times (next run starts after the previous succeeds) to speed promotions at the cost of more complex troubleshooting
- **Evidence**: Fixed-schedule jobs need "sufficient time for the worst-case
  runtime... plus some additional verification time"; a weekly job requiring two
  successful runs "equates to six weeks in a four stage setup"; cascading
  rollouts make start time "dynamic instead of fixed in a crontab," but "make
  troubleshooting and monitoring more complicated."
- **Confidence**: settled
- **Quote**: "This means the start time becomes dynamic instead of fixed in a crontab. After a successful run and some verification time, the next run starts. This strategy can significantly lower the total time to get a release into production."
- **Our assessment**: A concrete velocity-versus-complexity tradeoff. For LLM
  data pipelines the "weekend peak coverage" argument (run a full week of jobs
  before promoting) is directly relevant to eval-data refresh cadence. The
  cascade's monitoring cost is a real operational price to weigh. Settled.

### Claim 15: Freshness SLOs are operationalized with on-call readiness ("Hope is not a strategy"), alerting on schedule overruns, and staggering job start times to avoid resource crunches
- **Evidence**: Freshness measures "time since the last successful completion of
  the job"; jobs can overrun (a "daily run might actually take two days");
  mitigations are more resources, realigned requirements, or splitting the job;
  an on-call rotation should mitigate "before the freshness SLO is violated";
  choosing midnight as a universal start time "can lead to a resource crunch if
  many jobs launch at the same time."
- **Confidence**: settled
- **Quote**: "The freshness SLO of a batch measures time since the last successful completion of the job."
- **Quote**: "It is tempting to choose midnight as the starting time for a batch job. Doing so can lead to a resource crunch if many jobs launch at the same time."
- **Our assessment**: The freshness SLO gives Ch02 (observability) a concrete
  batch-pipeline health signal ("time since last successful completion") and an
  alerting trigger (schedule overrun). The midnight-start warning is a practical,
  non-obvious detail for scheduling LLM batch work (eval runs, backfills) — the
  "define a time period instead of specifying an exact start time" suggestion
  lets a scheduler optimize launches. The "Hope is not a strategy" motto is a
  quotable on-call rationale.

### Claim 16: Event-based processing produces fresher results but makes correctness harder — and a queue introduces an external dependency that affects your SLO
- **Evidence**: The paper lists event-based downsides: non-critical work can
  block critical work, explicit dry-run setup needed, loss of precomputation,
  always-on processing cost, corruption detection "spread over several systems,"
  a "global shutdown emergency button" requirement, and "A queue introduces an
  external dependency that affects your SLO."
- **Confidence**: settled
- **Quote**: "The need for fresher results and less coupling, combined with a trend towards microservices and serverless, has accelerated the adoption of event-based processing across the industry."
- **Quote**: "A queue introduces an external dependency that affects your SLO. (When targeting five 9s of availability, every dependency counts.)"
- **Our assessment**: A balanced batch-vs-streaming tradeoff that conditions the
  guide's "when is batch appropriate" advice rather than picking a winner. The
  five-9s-every-dependency-counts line supports counting every external dependency
  toward the error budget. Settled as a tradeoff statement.

### Claim 17: Slack's async compute — over 60% of Slack application code — improves reliability through criticality-bucketed routing (kindergarten/tier1/tier0) with isolated processing pipelines, delay tolerance, dogfood deploy stages, and a Job Registry for operational control
- **Evidence**: Julia Lee's case study: "Async compute accounts for over 60% of
  compute for Slack application code"; jobs are routed to executor pools via the
  Job Registry; new job types start in kindergarten and are promoted to tier1
  then tier0, with kindergarten "completely isolated"; jobs get delay tolerance
  (immediate/soon/besteffort) to prioritize delay-sensitive work; changes deploy
  to dogfood (Slack's internal workspaces) first; the Job Registry supports
  re-routing/pausing, rate-limiting, and error-routing to job owners.
- **Confidence**: settled
- **Quote**: "Async compute accounts for over 60% of compute for Slack application code—from fetching a preview of a URL to importing and exporting large amounts of data to and from files— so high reliability is essential."
- **Quote**: "Jobs are bucketed and routed based on criticality (kindergarten, tier1, tier0), each of which has its own isolated processing pipeline and pool of executors."
- **Our assessment**: The criticality-bucket pattern with a registry-driven
  control plane is directly applicable to LLM batch/async work (eval jobs vs.
  interactive serving). It mirrors the corpus's priority-bucket guidance for load
  shedding (see Cross-References) but applied to *scheduling isolation* rather
  than admission control. The kindergarten → tier1 → tier0 promotion (and the
  ability to move a changed workload back to kindergarten for safer rollout) is a
  concrete version of the paper's Level 1/2 safety-level spirit. Settled.

## Concrete Artifacts

### Table 1 — The four safety levels (verbatim from the paper)

```
Table 1: Four safety levels for changes

Level 0   The entire dataset is affected in a single run of the job.
Level 1   Changes are canaried and don't affect the entire dataset.
          The canary can be manual or automated.
Level 2   Changes are gradually rolled out, first to less risky populations
          (such as internal, beta, or freemium user populations), then globally.
Level 3   Level 1 and 2 criteria are met and no humans are involved in the
          phased rollout.
```

### Table 2 — Release stages (condensed from the paper)

```
Release stage | Dry run? | Purpose
Autopush      | Yes      | Every two hours checks "Does this compile, pass
              |          | tests, and run?" — builds/deploys a fresh release
              |          | from the latest CI-passing revision. Runs on a
              |          | Test dataset.
Staging       | Yes      | Ensures the actual mutations between versions are
              |          | expected and equivalent before writing data. Launches
              |          | new and old versions for an A/B test of output or
              |          | counters. Versions typically stay days to a week.
Production    | No       | Release progresses after all previous stages pass.
              |          | Supports multiple arbitrary canary stages.
```

### Canary subsetting and targeting parameters (verbatim examples from the paper)

```
Startup parameter:  --subset=alpha-users
Canary filter:      process only records where hash(userid) mod 10 == 0
                    ("10% prod")
Production filter:  hash(userid) mod 10 != 0  (if the two runs should not
                    overlap), or ignore the parameter entirely if the jobs
                    are idempotent
Target population ladder:
  canary-for-developers-team → canary-for-employees → canary-production-1%-free-users
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-reliable-product-launches.md` **Claim 10** (gradual
    rollouts with canary testing + automatic rollback are the standard deployment
    pattern) — the paper applies the same canary/gated-release doctrine to *batch
    jobs*, where it "was under-utilized"; and **Claim 14** (standardization via
    "better platform APIs... and greater standardization across production
    services" as the fix for operational churn) — the Batch Platform's
    convention-over-configuration (Claim 8 here) is a concrete instance of that
    recommendation.
  - `docs-google-sre-twenty-years-lessons.md` **Claim 3** (canary all changes
    with progressive rollout — YouTube config change hobbled the service for 13
    minutes) — corroborates the paper's canary mandate for batch changes from an
    independent Google retrospective.
  - `docs-google-sre-handling-overload.md` **Claim 6** (autoscaling kill
    switches needed because a CPU-consuming bug or stuck dependency can cause
    unbounded quota consumption) — parallels the paper's Slack autoscaler
    workarounds (limit max instances, restrict daemon CPU, throttle on no-useful-
    work); and **Claim 9** (classify batch operations as "non-critical
    retryable" priority buckets) — the same criticality-tiering idea Slack's
    kindergarten/tier1/tier0 implements (Claim 17 here).
- **Contradicts**: None. No existing note opposes the paper's claims. Potential
  tensions are conditioning variables, not contradictions: (a) the paper's
  batch-vs-event-based tradeoffs (Claim 16 here) vs. the industry trend toward
  event-based processing — the paper itself recommends event-based for freshness
  and only flags correctness costs; (b) the paper's batch change-freeze failure
  (Claim 2 here) vs. Treynor's launch-freeze doctrine
  (`discussion-google-sre-ben-treynor-interview.md` Claim 9 — "the only reliable
  recovery mechanism is a launch freeze") — Treynor's freeze applies to
  *serving-service* launches under error-budget exhaustion, while the paper's
  freeze applied to *unattended batch jobs* that continue to rot; different
  scopes, so not a contradiction.
- **Extends**:
  - `docs-google-sre-infrastructure-change-management.md` **Claim 15** (the
    10-item preflight checklist, esp. item 6 "Push the migration out in phases"
    and item 7 "Automate as much of the manual, repeatable process as possible")
    — this paper supplies the *batch-job-specific mechanism* for phased rollout
    and automation: safety levels, staged release pipeline, automated
    validations, and population-based canarying.
  - `docs-google-sre-ai-engineering-reliable-operations.md` **Claim 7** (tiered
    Bronze/Silver/Gold evaluation data pipeline with calibrated confidence) and
    **Claim 15** (Adaptive Progressive Rollouts with "continuous production
    validation" at machine speed) — eval-data pipelines and progressive-rollout
    automation are precisely the batch-job class this paper's safety levels and
    automated validations govern; the paper is the batch-layer complement to
    Google's AI-in-SRE rollout patterns. Also extends that note's **Claim 4**
    (mandatory dry-run support for every API) with the batch dry-run mechanism
    (Claim 10 here).
- **Novel**: Material new to the corpus:
  - **Batch-job safety levels (0–3)** with the toil↔blast-radius policy tradeoff
    (Claim 7) — the explicit "Level 3 = no humans involved" automation bar.
  - **Batch release-pipeline stages** Autopush/Staging/Production with dry-run
    semantics (Claims 9–10) — no existing note covers batch release stages.
  - **Population-based batch canarying** via hash-subset startup parameters and
    target-population ladders (Claim 13).
  - **Counter validation with range/percentage comparisons** and the
    false-positive-minimization principle for automated gates (Claim 11).
  - **Two-phase mutation design pattern** for safe dataset mutations (Claim 12).
  - **The "haunted graveyard" concept** for neglected batch jobs (Claim 1).
  - **Slack async-compute case study** — kindergarten/tier1/tier0 criticality
    buckets, delay tolerance, Job Registry (Claim 17).
  - **Google Batch Platform** standardization with the 450+-teams metric
    (Claim 8).

## Guide Impact

- **Chapter 04 (oncall-and-toil)** — the primary target, and the chapter is an
  empty stub whose stated targets are "auto-remediation candidates vs.
  always-manual classes" and "measuring toil reduction." Add the four safety
  levels (Claim 7) as the citable mechanism: Level 3 (fully automated phased
  rollout, no humans) is the canonical auto-remediation candidate; the residual
  manual work the paper identifies — investigating false positives (Claim 11),
  troubleshooting cascading rollouts (Claim 14), manual canary approvals — is
  the always-manual class. Use the "lower the safety level, the more manual
  verifications" policy (Claim 7) to frame toil reduction as a function of
  automation level, and "Hope is not a strategy" + on-call-before-SLO-violation
  (Claim 15) for the toil/on-call boundary.

- **Chapter 05 (llm-ops-reliability)** — add a "batch data pipelines" subsection:
  classify LLM batch work (eval-data refresh, embedding/index backfills, batch
  inference, training-data preprocessing — the paper explicitly names ML
  preprocessing, Claim 4) as batch jobs needing the safety-level framework; apply
  the three-stage release pipeline with dry-runs (Claims 9–10) to dataset and
  model-promotion changes; use population-based canarying via hash-subset
  startup parameters (Claim 13) for embedding/index rebuilds and eval-dataset
  refresh; use correctness-vs-freshness SLOs (Claim 6) for "did the eval batch
  complete on time" vs. "did it produce correct labels," with counter-validation
  ranges (Claim 11) as the automated gate. The Dressy-style model-freshness
  failure (stale model served >24h) maps to the paper's freshness-SLO + schedule-
  overrun alerting (Claim 15).

- **Chapter 02 (observability)** — add batch-pipeline health signals: freshness
  SLO defined as "time since the last successful completion of the job"
  (Claim 15) and alerting when a job overruns its schedule; the two-phase
  mutation pattern run continuously in production as a health monitor
  (Claim 12).

- **Chapter 03 (runbooks-and-agents)** — the dry-run, counter-validation, and
  two-phase-mutation mechanics (Claims 10–12) are directly codifiable as
  automated-validation agent steps in a batch-job release runbook; the
  Job-Registry-style control (re-route/pause/rate-limit by job type, Claim 17)
  is a runbook/agent control-plane pattern.

## Extraction Notes

- **Source identification discrepancy (important for the Assayer)**: the issue
  body and the Prospector's *final* triage comment identify this PDF as SRE
  Workbook Ch13 "Data Processing Pipelines" and suggest extracting from
  `/workbook/data-processing/`. That is **incorrect**. I downloaded
  `https://sre.google/static/pdf/reliable_data_processing_with_minimal_toil.pdf`
  directly: PDF title metadata reads "Reliable Data Processing with Minimal
  Toil," it is 8 physical pages (15 pypdf pages incl. layout splits), and its
  content (safety levels, Autopush/Staging/Production, Google Batch Platform,
  Slack async compute) matches the earlier two Prospector comments (13:11:27,
  13:11:32), not Workbook Ch13. The two *earlier* triage comments correctly
  identified the 2021 paper (Coucke & Sodt, Oct 12, 2021). The Workbook Ch13
  content (Dressy ML pipeline, Spotify event delivery) is a different document
  and was NOT extracted here. The HTML landing page
  (`sre.google/resources/practices-and-processes/reliable-data-processing-with-minimal-toil/`)
  contains only the abstract; the full text is the PDF. Note the triage claim
  that the PDF has "CID/Type0 fonts with no ToUnicode CMap" is also wrong —
  pypdf extracted the text cleanly (it has ToUnicode CMaps). Assayer should
  verify quotes against the PDF itself.

- Quotes were taken from the pypdf-extracted PDF text and are word-for-word from
  the source. PDF text extraction glues adjacent words in places (e.g.,
  "well-reasonedSLOsare met"); quotes here restore the natural word spacing the
  PDF displays. Ligature glyphs (ﬁ/ﬀ/ﬂ) were normalized to their letters. The
  Assayer is asked to flag any residual character-level discrepancy.

- Per MINER.md §4, the related-notes candidates file
  (`miner-related-notes.md`) was read. Dispositions for the 10 candidates:
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response, not batch release engineering.
  - `docs-google-sre-prodcast.md` — **Dismissed**; podcast index page.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
    **Dismissed**; DB reliability culture/burnout, no batch canarying.
  - `docs-google-sre-reliable-product-launches.md` — **Cited** (Corroborates
    Claims 10 and 14).
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — **Dismissed**; agent
    capability/guardrail discussion.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**; AI-for-
    SRE tagging, golden-data eval for agent labels (different context from
    pipeline correctness).
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` —
    **Dismissed**; incident tooling, not batch pipelines.
  - `docs-google-sre-handling-overload.md` — **Cited** (Corroborates Claims 6
    and 9).
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — **Dismissed**;
    org-scale economics of SRE.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` — **Dismissed**;
    SLOs-as-vernacular / bespoke SLO design; the paper's SLO content (correctness
    vs. freshness) is orthogonal.

- The two notes flagged in the first Prospector comment were also checked:
  `docs-google-sre-prodcast-04-04-zelesko-future-sre.md` and
  `discussion-google-sre-ben-treynor-interview.md` — both touch toil/SLO
  fundamentals (Zelesko Claim 3 production principles; Treynor Claim 9 launch
  freeze) but neither covers batch-pipeline safety or canarying; Treynor Claim 9
  is referenced in the Contradicts discussion as a conditioning-variable nuance,
  not a contradiction.

- No contradiction issue was filed: no existing source note opposes this paper,
  and the two apparent tensions (batch vs. event-based; batch change-freeze vs.
  serving launch-freeze) are conditioning variables per MINER.md §4a.

- The PDF contains no code blocks beyond the startup-parameter examples; the
  two tables (safety levels, release stages) and the canary-subsetting examples
  are extracted as Concrete Artifacts. No follow-up linked pages were needed —
  the PDF is self-contained (footnotes reference the SRE Book/Workbook already
  mined elsewhere in the corpus).

- Confidence is `settled` overall: official Google SRE first-party publication
  describing systems the authors operate, with named components (Batch Platform,
  Job Registry, safety levels), a company-wide adoption metric (450+ teams), and
  case studies (Slack). Claim 11's "could have prevented major issues" and
  Claim 8's 450-teams figure are the only soft spots, noted per-claim.
