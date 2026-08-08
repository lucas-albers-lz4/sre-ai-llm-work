---
source_url: https://sre.google/workbook/data-processing
source_type: docs
title: "Data Processing Pipelines — SRE Workbook Chapter 13"
author: "Rita Sodt and Igor Maravić (Spotify), with Gary Luo, Gary O'Connor, and Kate Ward"
date_published: 2018
date_extracted: 2026-08-08
last_checked: 2026-08-08
status: current
confidence_overall: settled
issue: "#817"
---

# Data Processing Pipelines — SRE Workbook Chapter 13

> The canonical Google SRE treatment of data-pipeline reliability: pipeline SLO
> formats (data freshness, golden-data correctness, data isolation), the
> end-to-end-vs-per-stage measurement trap, dependency-failure planning (DiRT
> regional-outage drills), a documented development lifecycle (dry runs,
> canarying with two-phase mutation, partial deployment), hotspotting and
> autoscaling, a five-dimension pipeline maturity matrix, delayed-vs-corrupt-data
> failure response, and two case studies — the Dressy ML recommender pipeline
> (with the >24h stale-model failure) and Spotify's event delivery system
> (timeliness/skewness/completeness SLOs on hourly buckets). This is the
> pipeline-design/ops companion to the 2021 "Reliable Data Processing with
> Minimal Toil" paper already in the corpus, and the first corpus source on the
> Dressy ML pipeline and Spotify event delivery.

## Source Context

- **Type**: docs — SRE Workbook (O'Reilly, 2018) Chapter 13 "Data Processing
  Pipelines," published at `sre.google/workbook/data-processing/`. Licensed
  CC BY-NC-ND 4.0. A distinct document from the 2021 paper
  `reliable_data_processing_with_minimal_toil.pdf` (Coucke & Sodt), which the
  existing note `docs-google-sre-reliable-data-processing-minimal-toil.md`
  explicitly flagged as NOT covering this chapter's content.
- **Author credibility**: Highest available. Rita Sodt (Google SRE) and Igor
  Maravić (Spotify, author of the Spotify case study), with Gary Luo, Gary
  O'Connor, and Kate Ward — first-party practitioner accounts of systems the
  authors built and operated (the Dressy recommender is a fictional worked
  example; the Spotify event delivery system is a real production system
  described by its own author).
- **Scope**: Covers (a) pipeline applications (ETL, analytics, ML); (b) pipeline
  SLOs — data freshness formats, data correctness via golden data,
  isolation/priority; (c) the end-to-end vs per-stage measurement trap; (d)
  dependency-failure planning incl. DiRT; (e) pipeline documentation (system
  diagrams, process docs, playbooks); (f) the development lifecycle (prototype,
  1% dry run, staging, canarying, partial deployment, production); (g) hotspotting
  mitigation, autoscaling and resource planning; (h) access control; (i) pipeline
  requirements/design — Table 13-1 recommended features, idempotent and two-phase
  mutations, checkpointing, code patterns; (j) the pipeline maturity matrix
  (Table 13-2); (k) failure prevention and response (delayed data, corrupt data,
  failure causes); (l) the Spotify event delivery case study. Does NOT cover the
  safety-levels framework (0-3), the Autopush/Staging/Production release stages,
  or the Batch Platform — those are the 2021 paper's scope and are NOT
  re-extracted here. Framed in 2018-era big-data terms (Hadoop/MapReduce-era
  examples), but the patterns are technology-neutral.

## Extracted Claims

### Claim 1: Pipeline data-freshness SLOs come in three standardized formats — "X% of data processed in Y", "the oldest data is no older than Y", or "the pipeline job has completed successfully within Y"
- **Evidence**: The "Data freshness" subsection enumerates the three formats
  with the time unit bracketed (seconds/days/minutes), then gives the Shave the
  Yak worked example (99% of score-impacting user actions reflected in the
  scoreboard within 30 minutes).
- **Confidence**: settled
- **Quote**: "Most pipeline data freshness SLOs are in one of the following formats: X% of data processed in Y [seconds, days, minutes]. The oldest data is no older than Y [seconds, days, minutes]. The pipeline job has completed successfully within Y [seconds, days, minutes]."
- **Our assessment**: This is the concrete health-signal vocabulary Ch02 needs
  for batch LLM data paths (eval-data refresh, embedding/index backfills, batch
  inference). All three are measurable from job metadata (completion time,
  event-time lag, per-batch watermarks) without instrumenting business logic.
  It operationalizes the 2021 paper's freshness-SLO definition (time since last
  successful completion) into deployable formats. Settled — a canonical taxonomy
  from an authoritative source.

### Claim 2: Data-correctness SLOs need a defined "correct" output, and when none exists you generate one — "golden data" from test accounts — then compare expected vs actual and alert on discrepancies; backward-looking correctness targets are an alternative
- **Evidence**: The "Data correctness" subsection: correctness errors in a
  billing pipeline could over/under-charge customers; "A correctness target can
  be difficult to measure, especially if there is no predefined correct output"
  and "you can generate it"; golden-data comparison enables threshold-based
  alerting as test data flows through production; backward-looking examples
  include "no more than 0.1% of your invoices are incorrect per quarter" and
  limiting hours/days of bad data served. "The notion of data correctness varies
  by product and application."
- **Confidence**: settled
- **Quote**: "If you don't have access to such data, you can generate it. For example, use test accounts to calculate the expected output. Once you have this \"golden data,\" you can compare expected and actual output."
- **Our assessment**: The golden-data mechanism is directly transferable to LLM
  eval pipelines: instrument a held-out eval set with known-answer labels flowing
  through the real production path, and alert on drift between expected and
  actual outputs. This is the data-path ancestor of Google's later Bronze/
  Silver/Gold eval-data tiering (see Cross-References). The backward-looking
  targets ("no more than 0.1% of invoices incorrect per quarter") give a
  batch-oriented correctness SLO form for periodic eval runs. Settled.

### Claim 3: Data isolation / load balancing — under resource constraints, higher-priority data must be processed before lower-priority data via separate queues or jobs, and work that fails on lower-provisioned workers can be retried on higher-provisioned ones
- **Evidence**: The "Data isolation/load balancing" subsection: tighter SLOs on
  high-priority data require it "processed before lower-priority data if your
  resources become constrained"; implementation "often manifests as different
  queues in task-based systems or different jobs"; "Pipeline workers can be
  configured to take the highest available priority task"; failed work on lower
  provisioned workers can retry on higher provisioned ones (memory/CPU/network
  tiers). When not all data can be processed quickly, "this separation allows
  you to preferentially process higher-priority items over lower ones."
- **Confidence**: settled
- **Quote**: "If you promise a tighter SLO on high-priority data, it's important to know that this data will be processed before lower-priority data if your resources become constrained."
- **Our assessment**: A pipeline-specific statement of the priority-bucket
  doctrine the corpus already carries for request admission (handling-overload).
  For LLM data paths this maps to: separate queues for eval-data refresh vs
  bulk backfills vs interactive batch inference, with capacity preemption so a
  heavy backfill cannot starve a tighter-SLO eval refresh. The retry-on-higher-
  provisioned-workers detail is a concrete resource-tiering mechanism. Settled.

### Claim 4: Per-stage SLO measurement misses end-to-end corruption — a field dropped at one stage that a downstream stage silently ignores leaves both stages "correct" per their own metrics while the user never sees the data
- **Evidence**: The "End-to-end measurement" subsection: measuring per-stage
  SLOs "doesn't capture your customer's experience or the end-to-end health of
  your system"; per-component SLOs force tighter per-component alerting that
  "could result in more alerts that don't model the user experience." The worked
  example: one stage introduces a field it expects a downstream job to process;
  the downstream job drops it; "Both jobs think they are correct, but the user
  doesn't see the data."
- **Confidence**: settled
- **Quote**: "Additionally, if you measure data correctness only per stage, you could miss end-to-end data corruption bugs. For example, each stage in your pipeline could report that all is well, but one stage introduces a field that it expects a downstream job to process. This upstream stage assumes that the extra data has been processed and used to serve requests to users. A downstream job doesn't expect the additional field, so it drops the data. Both jobs think they are correct, but the user doesn't see the data."
- **Our assessment**: This is the highest-value observability warning in the
  chapter. For LLM data pipelines it generalizes the "per-component correctness"
  trap to cross-stage corruption: an embedding/feature transform that drops a
  field or a tokenizer change that silently alters inputs can pass every
  per-stage check while degrading model outputs end-to-end. The guide's Ch02
  should state the rule: measure the end-to-end SLO (freshness AND correctness)
  on the user-visible output, not just per-stage health. Settled.

### Claim 5: Plan for dependency failure by designing for at least the largest failure in a dependency's advertised SLA — and Google stages DiRT regional-outage tests; an unplanned manual failover risks continuing to process stale data
- **Evidence**: The "Plan for Dependency Failure" subsection: confirm you "aren't
  overdepending on the SLOs/SLAs of other products that fail to meet their
  commitments"; "at a minimum, design for the largest failure accounted for in
  their advertised SLAs"; pipeline owners may replicate data across regions to
  get higher availability than the single-region guarantee. DiRT "frequently
  targets these systems, simulating a regional outage"; planned pipelines
  "automatically fail over to another region," others wait for manual failover;
  "In a worst-case scenario, processing jobs may have continued processing stale
  data, which introduces out-of-date or incorrect data in any downstream
  pipelines."
- **Confidence**: settled
- **Quote**: "Once you identify any third-party dependencies, at a minimum, design for the largest failure accounted for in their advertised SLAs." and "Our Disaster Recovery Testing (DiRT) frequently targets these systems, simulating a regional outage."
- **Our assessment**: The SLO-vs-advertised-SLA over-dependence trap is directly
  relevant to LLM-ops: an embedding/index job that promises tighter freshness
  than its storage dependency's region SLA must replicate across regions or
  loosen its SLO. DiRT-style planned outage drills are the "practice failover
  before you need it" mechanism — cheap relative to a first-time regional outage
  on an eval-data path. The manual-failover stale-data risk is a concrete warning
  that an unplanned regional failover of a batch pipeline can silently corrupt
  downstream outputs. Settled.

### Claim 6: Pipeline documentation has three categories — system diagrams with live per-stage status links, process documentation (document the task, then automate away any manual work), and a playbook entry linked in every alert
- **Evidence**: The "Create and Maintain Pipeline Documentation" subsection.
  System diagrams show each component and transformation, and "should contain
  quick links to other monitoring and debugging information at different pipeline
  stages" — "Ideally, these links should pull from live monitoring information,
  displaying the current status of each stage." Process documentation covers
  common tasks (releasing a pipeline version, changing the data format) and
  rare manual tasks (turnup/turndown in a new region): "Once your tasks are
  documented, investigate the possibility of automating away any manual work."
  Playbook entries: "Each alert condition in your system should have a
  corresponding playbook entry that describes the steps to recovery," linked in
  alert messages.
- **Confidence**: settled
- **Quote**: "It's important to document how to perform common tasks, such as releasing a new version of a pipeline or introducing a change to the data format." and "Once your tasks are documented, investigate the possibility of automating away any manual work."
- **Our assessment**: Directly supports Ch04's document-then-automate doctrine and
  Ch03's runbook-automation premise: process documentation is the raw material
  for automation, and the diagram-with-live-links is the on-call navigation
  artifact (a live-status diagram of eval-data refresh stages would be the single
  most useful operational artifact for an LLM data pipeline). The playbook-entry-
  linked-in-alert requirement is the same pattern the corpus already carries for
  serving alerts, applied to pipeline alerts. Settled.

### Claim 7: The pipeline development lifecycle runs prototype → 1% dry run on production data → staging (A/B vs known-good output) → canary (skip production writes; two-phase mutation) → partial deployment by data subset (~1%/10%/50%/100%) → production with rollback and mark-bad-data
- **Evidence**: The "Map Your Development Lifecycle" subsection with Figure 13-3.
  Prototyping verifies business-logic expressibility. Dry run: "run your pipeline
  using an experimental set, or a 1% dry run of production data in a nonproduction
  environment." Staging should use "a full copy of production data or at least a
  representative subset," with A/B comparison of newly generated data to known
  good data. Canarying: "you may choose to process the same real production data
  as the live pipeline but skip writes to production storage; techniques such as
  two-phase mutation can help," and "Verifying your canary is a task that lends
  itself well to automation." Partial deployment: "Consider first processing your
  new features on one or two accounts, then gradually ramping up the amount of
  data (e.g., ~1%, ~10%, ~50%, and finally, 100% of your sample data)." Production
  entry: "be able to quickly restore from a known good state (e.g., roll back the
  binaries) and mark any potentially broken data as bad."
- **Confidence**: settled
- **Quote**: "For example, run your pipeline using an experimental set, or a 1% dry run of production data in a nonproduction environment." and "Verifying your canary is a task that lends itself well to automation."
- **Our assessment**: This is the lifecycle recipe for LLM dataset/model-promotion
  changes: dry-run an eval-data refresh on 1% of real data, stage against a full
  production copy with output-diffing, canary with two-phase mutation (plan
  mutations, validate, apply), then partial-deploy by account/tenant slice before
  full rollout. The ~1/10/50/100 ramp is a ready-made config ladder for Ch05's
  batch-data subsection, and the "verify the canary automatically" statement is a
  direct automation/agent target. Settled.

### Claim 8: The Dressy ML recommender pipeline is a canonical streaming-preprocess → train → accuracy-gated promotion → serve flow, and its >24h stale-model failure gives a three-question diagnostic for ML pipeline health
- **Evidence**: The "Machine Learning" subsection (Figure 13-1). Dressy streams
  product images through Cloud Dataflow to an image classification service,
  preprocesses purchase history from BigQuery, trains a TensorFlow model stored
  in GCS, gates promotion on "the model passes accuracy checks when evaluated
  against a test set of the preprocessed data used for model evaluation," and
  serves via Cloud ML online prediction. The failure: "occasionally a new model
  doesn't get published for over 24 hours, and the recommendations trigger
  intermittent errors," with the triage: "Is data stuck coming into the pipeline
  before it can be preprocessed to train the model? / Do we have a poor ML model
  caused by a software bug? Is there a lot of spam? Are the features used to
  train the model poorly chosen? / Has a new version of the ML model been recently
  generated, or is a stale version of the model running in production?"
- **Confidence**: settled
- **Quote**: "Dressy has noticed that occasionally a new model doesn't get published for over 24 hours, and the recommendations trigger intermittent errors." and "Has a new version of the ML model been recently generated, or is a stale version of the model running in production?"
- **Our assessment**: The stale-model-served-too-long failure mode is exactly the
  model-freshness problem Ch05's dressy references need: a serving-time SLO gap
  where model promotion stalls and the old model's outputs degrade. The
  three-question checklist (input stuck / poor model from a bug or bad features /
  stale model in production) is a ready-made runbook for LLM/embedding freshness
  incidents. The accuracy-checked promotion gate before production is a
  correctness SLO applied to model serving — the same pattern as golden-data
  validation (Claim 2). Settled.

### Claim 9: Two-phase mutations stage mutations in a temporary location, validate them in a separate verification step, and apply them only after validation passes — the canonical source of the pattern; exactly-once semantics are unneeded when work units are idempotent
- **Evidence**: The "Idempotent and Two-Phase Mutations" subsection (Figure 13-4):
  "With two-phase mutation, the mutations themselves are stored in a temporary
  location. A separate verification step (or pipeline) can run against these
  potential mutations to validate them for correctness. A follow-up pipeline step
  applies the verified mutations only after the mutations pass validation." An
  idempotent mutation "can be applied multiple times with the same result," and
  from Table 13-1: "you don't need \"exactly once\" semantics if your work units
  are idempotent and can be performed more than once for the same result."
- **Confidence**: settled
- **Quote**: "With two-phase mutation, the mutations themselves are stored in a temporary location. A separate verification step (or pipeline) can run against these potential mutations to validate them for correctness. A follow-up pipeline step applies the verified mutations only after the mutations pass validation."
- **Our assessment**: This chapter is the original canonical treatment of
  two-phase mutation that the 2021 paper (Claim 12) restates in batch terms — the
  existing note's claim number should be cross-cited here rather than treated as
  novel. For LLM dataset work, the pattern is: compute candidate mutations to an
  index/embedding store, validate in a separate step (spot-check, golden-data
  comparison, size sanity), then apply. The idempotency-eases-exactly-once note is
  a concrete cost/effort tradeoff for pipeline tech selection. Settled.

### Claim 10: Checkpointing lets long-running pipelines periodically save partial state and resume later — especially important for AI models where each iteration depends on previous calculations, and useful for preemption/rescheduling as well as failure
- **Evidence**: The "Checkpointing" subsection: "pipelines that are terminated
  early will lose their state, requiring the entire pipeline to be executed
  again. This is especially true for pipelines that create AI models, as each
  iteration of the model calculation relies on previous calculations." Also
  enables clean shutdown for preemption/rescheduling (changing CPU/RAM limits)
  and skipping expensive re-reads/recomputations.
- **Confidence**: settled
- **Quote**: "Checkpointing is a technique that enables long-running processes like pipelines to periodically save partial state to storage so that they can resume the process later."
- **Our assessment**: Directly relevant to long LLM batch jobs (embedding
  backfills over large corpora, eval-data reprocessing, model retraining): a
  crashed job without checkpoints restarts from scratch, multiplying outage
  impact. The preemption use case matters for spot/preemptible GPU fleets — a
  checkpointing job can be cleanly rescheduled. Note the chapter frames
  checkpointing primarily as failure/preemption recovery (not correctness), which
  is a useful scoping vs the 2021 paper's dry-run semantics. Settled.

### Claim 11: Hotspotting mitigation — block fine-grained records so the rest of the pipeline can progress, let the framework dynamically rebalance, and build an emergency-shutdown flag into client logic to skip problematic input
- **Evidence**: The "Reduce Hotspotting and Workload Patterns" subsection:
  "Hotspotting happens when a resource becomes overloaded from excessive access,
  resulting in an operation failure"; "you can also block fine-grained data such
  as individual records. If that data is blocked, the rest of the pipeline can
  progress"; framework can "dynamically rebalance by breaking the work into
  smaller pieces"; "it's still best to build an emergency shutdown into your
  client logic... you should be able to quickly set a flag or push a config that
  allows you to skip input data that matches a certain pattern or problematic
  user." Other strategies: spread load evenly, statically allocate data, reduce
  lock granularity.
- **Confidence**: settled
- **Quote**: "To combat hotspotting, you can also block fine-grained data such as individual records. If that data is blocked, the rest of the pipeline can progress."
- **Our assessment**: The record-level blocking and emergency-shutdown flag are
  concrete, copyable controls for LLM data pipelines: a pathological input
  (abusive text, a pathological user's data, an oversized record) must be
  blockable without stalling the whole backfill. The emergency-shutdown flag
  (skip-by-pattern) is the pipeline version of the kill-switch doctrine the
  corpus carries for autoscaling and overload. The example is presciently
  user-centric — the "problematic user" skip is directly the kind of control an
  eval-data or content-ingest pipeline needs. Settled.

### Claim 12: Autoscaling and resource planning — don't provision for peak load, do measure end-to-end SLOs but per-stage efficiency/resource usage, and account for cross-region storage/network costs and unused-data pruning
- **Evidence**: The "Implement Autoscaling and Resource Planning" subsection:
  "By using autoscaling, you don't have to provision for peak load 100% of the
  time"; "Autoscaling turns down idle workers so you won't pay for resources you
  don't need. This strategy is particularly important for streaming pipelines
  and workloads that are variable." Cost scope: "you may also be paying the data
  storage and network bandwidth costs for replicating data across regions or
  cross-region writes and reads"; "periodically examining your data set and
  pruning unused content" drives down costs. Measurement split: "the pipeline
  efficiency and resource usage should be measured at each individual stage"
  even though effectiveness is measured end-to-end.
- **Confidence**: settled
- **Quote**: "Autoscaling turns down idle workers so you won't pay for resources you don't need. This strategy is particularly important for streaming pipelines and workloads that are variable."
- **Our assessment**: Two durable rules for LLM data ops: (1) effectiveness
  (SLOs) is end-to-end, but efficiency (resource/cost) is per-stage — so a
  BigQuery/GPU cost spike after a release is attributable to the responsible job;
  (2) total pipeline cost includes cross-region storage/network, not just compute
  — directly relevant to embedding stores replicated across regions for the
  dependency-failure planning of Claim 5. The prune-unused-data advice is a
  concrete cost lever for growing vector stores. Settled.

### Claim 13: The pipeline maturity matrix scores five characteristics (failure tolerance, scalability, monitoring and debugging, transparency/ease of implementation, unit and integration testing) on a 1-5 scale from "Chaotic" to "Continuous improvement" — a PRR-style rubric for evaluating pipeline technology
- **Evidence**: The "Pipeline Maturity Matrix" subsection (Table 13-2): "Each
  characteristic is measured on a scale of 1 to 5, where 1 represents \"Chaotic\"
  (unplanned, ad hoc, risky, fully manual) and 5 represents \"Continuous
  improvement.\"" If multiple milestones apply, "use the score in the middle
  (i.e., 2 or 4)." The matrix "represents the collective knowledge of many
  pipeline experts at Google" and is used "when consulting on the choice or
  design of a pipeline technology," in the same spirit as a PRR. "We recommend
  that you spend the time to make improvements in any weak areas identified by
  the matrix."
- **Confidence**: settled
- **Quote**: "Each characteristic is measured on a scale of 1 to 5, where 1 represents \"Chaotic\" (unplanned, ad hoc, risky, fully manual) and 5 represents \"Continuous improvement.\""
- **Our assessment**: A concrete, actionable rubric the guide can adapt verbatim
  as a readiness checklist for LLM pipeline tech (embedding/indexing platforms,
  eval-data refresh stacks): score failure tolerance (failover, hot/hot/hot
  global scheduling), scalability (autoscaling, dynamic resharding, load
  shedding), monitoring/debugging, transparency, and testing. The matrix is
  technology-neutral despite its 2018 framing. This is the strongest candidate
  for a guide-adopted artifact. Settled.

### Claim 14: For delayed data, "stale data is almost always better than incorrect data" — a pipeline should stall and wait for data rather than process incomplete/corrupt input, since errors propagate downstream; batch stages wait for predecessors while streaming event-time processing can start partial work
- **Evidence**: The "Delayed data" subsection: "a downstream job may start running
  even though it doesn't have the necessary data"; "Stale data is almost always
  better than incorrect data. If your pipeline processes incomplete or corrupt
  data, errors will propagate downstream." "Creating data dependencies that are
  respected by all stages is important." Batch vs streaming: "In batch processing
  pipelines, each stage waits for its predecessor to finish before it begins";
  streaming via event-time processing "a downstream stage can start a portion of
  work as soon as the corresponding upstream portion completes."
- **Confidence**: settled
- **Quote**: "Stale data is almost always better than incorrect data. If your pipeline processes incomplete or corrupt data, errors will propagate downstream. Restoring or reprocessing bad data takes time and can prolong an outage. Instead, if your pipeline stalls, waits for data, and then resumes once the data becomes available, the data remains high quality."
- **Our assessment**: The stale-is-better-than-incorrect rule is a crisp failure-
  response principle for LLM data paths: an embedding backfill that sees a
  partial upstream export should stall rather than silently index incomplete
  data. It also conditions the freshness-vs-correctness tension — when the two
  conflict, correctness wins by waiting. The batch-waits vs streaming-partial-work
  distinction is the technology-neutral version of the 2021 paper's
  batch-vs-event-based tradeoff (Claim 16 there). Settled.

### Claim 15: Corrupt-data recovery has two steps — mitigate (prevent further corrupt data entering) then restore from a known-good version or reprocess; selective reprocessing and checkpoints reduce the cost, and the common failure causes are pipeline dependencies, application/config bugs, unexpected resource growth, and region-level outages
- **Evidence**: The "Corrupt data" and "Potential Causes" subsections. "There are
  two main steps involved in fixing corrupt data: 1. Mitigate the impact by
  preventing further corrupt data from entering the system. 2. Restore your data
  from a previously known good version, or reprocess to repair the data." To cut
  reprocessing cost: "consider selective reprocessing—read in and process only
  the user or account information impacted by the data corruption" or "persist
  some intermediate data that can serve as a checkpoint." Failure causes: pipeline
  dependencies (throttling, refusing writes, hotspot ranges, storage bugs),
  application/config bugs ("the most common causes of outages"), unexpected
  resource growth (need emergency resources, prioritize data classes), and
  region-level outage (single-homed pipelines stop; multihomed can drain the
  affected region).
- **Confidence**: settled
- **Quote**: "There are two main steps involved in fixing corrupt data: 1. Mitigate the impact by preventing further corrupt data from entering the system. 2. Restore your data from a previously known good version, or reprocess to repair the data."
- **Our assessment**: The two-step recovery and the selective-reprocessing cost
  control are concrete runbook material for LLM data corruption incidents (a bad
  embedding write, a poisoned eval split): stop the bleed, then restore/reprocess
  only the affected slice. The failure-cause taxonomy is the pipeline analogue of
  the corpus's incident-response cause categories. "Application or configuration
  errors... are the most common causes of outages" justifies the development-
  lifecycle investment of Claim 7. Settled.

### Claim 16: Spotify's event delivery system measures health with three SLO types on hourly buckets — timeliness, skewness, completeness — computed from server-side timestamps, with full event-type isolation and deliberately no data-quality SLO (the "postal service" model)
- **Evidence**: The "Event Delivery" and "Event Delivery System Operation"
  sections (Figures 13-5 through 13-9): events partition into delivered hourly
  buckets per event type; SLOs are "timeliness, completeness, and skewness."
  Timeliness = "the maximum delay of delivering an hourly bucket of data"
  (split into high/normal/low priority tiers); skewness = "the maximal
  percentage of data that can be misplaced on a daily basis"; completeness =
  "the percentage of events that are delivered after they are successfully
  published to the system." Buckets are assigned "at the time they were received
  at our servers, not when they were produced on the clients" (offline buffering
  up to 30 days, system-time manipulation). "To ensure that separate event types
  don't impact each other, the system has full event type isolation." No quality
  SLOs: "we use the analogy that event delivery should behave like a postal
  service: your mail should be delivered on time, intact, and unopened."
- **Confidence**: settled
- **Quote**: "Our timeliness SLO is defined as the maximum delay of delivering an hourly bucket of data." and "We define completeness as the percentage of events that are delivered after they are successfully published to the system."
- **Our assessment**: A production-grade pipeline-health SLO suite: timeliness
  (freshness of the bucket), completeness (event loss), skewness (misplacement
  between time buckets) — all measurable per time-partition and reported daily
  from an independent auditing system. The server-side-timestamp choice is a
  specific anti-corruption design (client clock/offline manipulation) that maps
  directly to data-quality hygiene in LLM telemetry. The postal-service boundary
  (delivery reliability yes, content quality no) is a clean responsibility split
  for pipeline platforms vs the teams that own business logic. Settled.

### Claim 17: Spotify's GCE Autoscaler can scale indefinitely on CPU usage that doesn't correlate with work — fixed with max-instance limits, restricted daemon CPU, and aggressive throttling of no-useful-work CPU; capacity planning keeps a 50% peak-CPU safety margin
- **Evidence**: The "Capacity planning" subsection: "we provision each component
  to have 50% of CPU usage during peak hours. This provision acts as a safety
  margin that allows our system to handle unexpected bursts of traffic." The
  autoscaler failure: "Autoscaler depends on a strong correlation between CPU
  usage and the amount of work performed... If the relationship is broken—
  either through the addition of CPU-hungry daemons to each component instance
  or due to component instances extensively burning CPU without doing any work—
  Autoscaler will start far too many instances"; "it will scale indefinitely
  until it uses all of the resources it can find." Workarounds: "We limit the
  maximum number of instances Autoscaler can use. We heavily restrict the CPU
  usage of all daemons running on an instance. We aggressively throttle a
  component's CPU usage as soon as we detect that no useful work is being done."
- **Confidence**: settled
- **Quote**: "When Autoscaler is presented with constantly increasing CPU usage that has no correlation with the amount of work performed, it will scale indefinitely until it uses all of the resources it can find."
- **Our assessment**: A real production instance of the autoscaling-kill-switch
  failure class the corpus already carries (handling-overload Claim 6): a
  CPU-based autoscaler whose signal decouples from work (daemons, busy-spin) will
  burn quota without bound. The three workarounds are directly copyable for
  autoscaling GPU/CPU worker pools for batch LLM jobs. The 50% peak-CPU safety
  margin is a concrete capacity-planning rule (vs the "static resources → waste"
  baseline). Settled.

### Claim 18: Spotify ships via conservative staged deployments with manual approval gates and a testing pyramid, and incident handling forbids new changes mid-incident except rolling back recently deployed code
- **Evidence**: The "Development process" and "Incident handling" subsections:
  CI/CD with tests on a shared server and peer review; "we decided to take a more
  conservative approach to deployments and deploy each change in stages. We
  require a manual approval before a deployment can move from one stage to
  another"; stages are staging (mirrored production traffic) then canaries then
  full production. Incident handling: "our first priority is to mitigate the
  damage and return the system to a stable previous state"; "we refrain from
  deploying any major changes to our components during an incident. The
  exception to this rule is if we conclude that the incident was caused by
  recently deployed new code. In such cases, we immediately roll the system back
  to a previous working version." Recovery from SLO breaches: "To deal with
  incompleteness, events need to be redelivered from the last checkpoint known to
  be good" and "To deal with excessive skewness, already delivered events are
  reshuffled and assigned to their correct hourly buckets," both done manually,
  with customers advised to reprocess.
- **Confidence**: settled
- **Quote**: "For this reason, we decided to take a more conservative approach to deployments and deploy each change in stages. We require a manual approval before a deployment can move from one stage to another."
- **Our assessment**: The manual-gate staged deployment is the serving-side
  counterpart to the pipeline canary lifecycle (Claim 7), and the 
  no-changes-during-incident-except-rollback posture is standard SRE incident
  discipline applied to a data platform. The redeliver-from-last-known-good /
  reshuffle-to-correct-bucket recovery pair operationalizes Claim 10's checkpoint
  and Claim 15's reprocessing for the event-type-isolated case. Settled.

## Concrete Artifacts

### Table 13-1 — Recommended data pipeline features (condensed from the chapter)

```
Feature                    | Recommendation
Latency                    | Use an API that supports streaming, batch, or both;
                           | an interchangeable API reduces migration cost later.
Data correctness           | Exactly-once semantics globally, or make work units
                           | idempotent ("you don't need 'exactly once' semantics
                           | if your work units are idempotent"); two-phase
                           | mutations; windowing functions (fixed time, session,
                           | sliding); black-box monitoring; gate jobs until
                           | dependencies complete.
High availability          | Multihoming; autoscaling.
MTTR                       | Tie code changes to a release for fast rollbacks;
                           | tested backup/restore; easily drain a region;
                           | monitoring quick to identify why a pipeline is
                           | delayed and/or data is corrupt; use data
                           | checkpointing.
MTTD                       | SLO monitoring in place; alert on the symptom
                           | rather than the cause.
Development lifecycle      | Run changes in a canary environment before
                           | production.
Resource/cost              | Resource accounting dashboard incl. storage and
                           | network; a metric to correlate/predict growth.
Ease of development        | Language fit; simple API for transformations;
                           | reuse base libraries, metrics, reporting.
Ease of operation          | Use existing automation/tools; automate operational
                           | tasks; invest in automation for complex infrequent
                           | tasks (e.g., region-to-region migration + turndown).
```

### Table 13-2 — Pipeline maturity matrix (structure verbatim from the chapter)

```
Five characteristics: failure tolerance, scalability, monitoring and debugging,
transparency/ease of implementation, unit and integration testing.

Score: 1 "Chaotic" (unplanned, ad hoc, risky, fully manual) → 5 "Continuous
improvement." If more than one milestone applies, score the middle (2 or 4).

Example milestones (beginning → functional → advanced):
  Failover:              no support → some work-unit retries (even manual)
                         → multihomed with automatic failover
  Global work scheduling: none → hot/hot/hot (process same work in all three
                         regions) → effective warm/warm/warm (distribute work,
                         store centrally)
  Failed task management: no support → automatic retries → automatic quarantine
  Autoscaling:           no autoscaling, manual → autoscaling w/ manual tools
                         → built-in autoscaling; + dynamic subsharding;
                         + built-in load shedding; workers understand
                         preemption notification
  Debugging:             no logs → identify a failed work unit and extract logs
                         → access logs from the failed work unit → auto-quarantine
                         and replay
  Dashboards:            none → work-unit counts + latency/aging per stage
                         → fine-grained execution-map visualization with delays,
                         throttling rationale, resource limiting factors,
                         failing/stuck/slow work units, preserved historical runs
  Discoverability:       none → some, manual setup → global data registry
  Code:                  significant setup → reusable components → base
                         frameworks, minimum code; machine-readable config;
                         zero config; semantics like other pipeline solutions
  Documentation:         sparse/outdated → minimal per-component setup docs
                         → comprehensive + training examples
  Unit testing:          no framework → fast tests, easy data-source switching,
                         sanitizers, minimal dependency graph, code coverage,
                         no external deps, built-in test data generation
  Integration testing:   in-house tools required → minimal docs/examples
                         → built-in scaled-down input, output diffing,
                         configurable monitoring, ample docs
```

### Dressy stale-model diagnostic checklist (verbatim from the chapter)

```
If you start to notice that decisions, classifications, or recommendations
either aren't being surfaced or are stale or incorrect, ask yourself:
- Is data stuck coming into the pipeline before it can be preprocessed to train
  the model?
- Do we have a poor ML model caused by a software bug? Is there a lot of spam?
  Are the features used to train the model poorly chosen?
- Has a new version of the ML model been recently generated, or is a stale
  version of the model running in production?
```

### Data-freshness SLO formats (verbatim from the chapter)

```
Most pipeline data freshness SLOs are in one of the following formats:
- X% of data processed in Y [seconds, days, minutes].
- The oldest data is no older than Y [seconds, days, minutes].
- The pipeline job has completed successfully within Y [seconds, days, minutes].
```

### Spotify event-type enablement config example (verbatim from the chapter)

```
events:
    -CollectionUpdate
    -AddedToCollection
    -RemovedFromCollection
```

### Spotify autoscaler-runaway workarounds (verbatim from the chapter)

```
To prevent Autoscaler from using up all of our quota, we implemented some
workarounds:
- We limit the maximum number of instances Autoscaler can use.
- We heavily restrict the CPU usage of all daemons running on an instance.
- We aggressively throttle a component's CPU usage as soon as we detect that no
  useful work is being done.
```

### Corrupt-data recovery two-step (verbatim from the chapter)

```
There are two main steps involved in fixing corrupt data:
1. Mitigate the impact by preventing further corrupt data from entering the
   system.
2. Restore your data from a previously known good version, or reprocess to
   repair the data.
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` **Claim 6**
    (correctness-vs-freshness SLO split) — Ch13's freshness formats (Claim 1 here)
    and golden-data correctness (Claim 2 here) corroborate and operationalize the
    paper's distinction; the chapter also warns that a job can be on-time yet
    incorrect (per-stage trap, Claim 4 here). **Claim 12** (two-phase mutation) —
    Ch13 is the original canonical source of the pattern (Claim 9 here); the two
    notes describe the identical mechanism. **Claim 10** (dry run skips the
    writing phase) — Ch13's 1% dry run and canary-skip-writes corroborate the
    same safe-preview mechanism for pipelines.
  - `docs-google-sre-eliminating-toil.md` **Claim 2** (automatable remediation
    documents are "essentially pseudocode") and **Claim 12** (document thoroughly,
    then break manual work into composable components) — Ch13's "Once your tasks
    are documented, investigate the possibility of automating away any manual
    work" (Claim 6 here) is the same document-then-automate doctrine applied to
    pipeline operations.
  - `docs-google-sre-canarying-releases.md` **Claim 16** (canarying noninteractive
    systems: duration spans one work unit, workers from a single pool,
    end-to-end + output-quality metrics) — Ch13's pipeline canarying (Claim 7
    here: skip production writes, two-phase mutation, wait for the full processing
    cycle) corroborates and adds the mutation-planning mechanics for the batch
    case.
  - `docs-google-sre-handling-overload.md` **Claim 6** (autoscaling kill switches
    — a CPU-consuming bug or stuck dependency causes unbounded quota consumption)
    — Spotify's autoscaler-runaway workarounds (Claim 17 here) are a named
    production instance of the same failure class, with the same mitigation shape
    (bounds + no-useful-work throttling). **Claim 4** (autoscale before load
    shedding) is consistent with Ch13's autoscaling-first resource posture
    (Claim 12 here).
  - `docs-google-sre-address-cascading-failures.md` **Claim 14** (mitigation
    hierarchy incl. "eliminate batch/bad traffic") — Ch13's corrupt-data response
    (mitigate-then-restore, drain region, block bad data, selective reprocessing;
    Claim 15 here) is the pipeline-flavored instance of the same stop-the-bleed
    hierarchy.
  - `docs-google-sre-reliable-product-launches.md` **Claim 9** (document all
    manual processes before launch) — corroborates Ch13's document-then-automate
    process-documentation requirement (Claim 6 here); **Claim 10** (gradual
    rollouts with canary testing as the standard deployment pattern) — Ch13's
    partial-deployment data ramp (~1/10/50/100%, Claim 7 here) is the batch-data
    analogue of the traffic ramp.
  - `docs-google-sre-ai-engineering-reliable-operations.md` **Claim 7**
    (Bronze/Silver/Gold evaluation data pipeline with golden data calibrating
    lower tiers) — Ch13's golden-data correctness validation for pipeline output
    (Claim 2 here) is the earlier data-path statement of the same golden-data
    principle Google later applies to eval-data quality tiers.

- **Contradicts**: None. Verified per MINER.md §4a: no existing note opposes a
  Ch13 claim such that different guide advice would result. Potential tensions
  checked and resolved as conditioning variables, not contradictions:
  (a) Ch13's "stale data is almost always better than incorrect data" (Claim 14)
  vs the 2021 paper's freshness-SLO emphasis (Claim 6 there) — different failure
  modes (delayed input vs on-time-but-wrong output); both agree correctness
  matters, Ch13 adds the wait-don't-process-incomplete rule. (b) Ch13's
  per-stage efficiency measurement (Claim 12 here) vs its own end-to-end SLO
  mandate (Claim 4) — explicitly reconciled in the source: effectiveness is
  measured end-to-end, efficiency per-stage. (c) Ch13's streaming Dataflow
  recommendation vs the 2021 paper's batch economics (Claim 4/16 there) — the
  sources address different pipeline shapes; the 2021 paper itself says event
  processing is preferred for freshness. No contradiction issue filed.

- **Extends**:
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` — the 2021 paper
    explicitly flagged that "The Workbook Ch13 content (Dressy ML pipeline, Spotify
    event delivery) is a different document and was NOT extracted here." This note
    is exactly that missing document: the paper covers batch safety levels and
    release stages; Ch13 supplies the pipeline-design/ops companion material
    (SLO taxonomy, maturity matrix, failure recovery, hotspotting, the two case
    studies).
  - `docs-google-sre-canarying-releases.md` — extends Claim 16 (batch/pipeline
    canary adaptations) with Ch13's pipeline-canary mechanics: dry-run/two-phase-
    mutation planning, waiting for a full processing cycle, and the ~1/10/50/100
    partial-deployment ramp.
  - `docs-google-sre-ai-engineering-reliable-operations.md` — extends the
    eval-data-pipeline content (Claim 7) with the batch-pipeline machinery needed
    to refresh eval data and embedding indexes reliably: freshness SLO formats,
    golden-data validation, checkpointing, and the maturity matrix.
  - `docs-google-sre-eliminating-toil.md` — Ch13's process documentation and
    "automate away any manual work" is a pipeline-scoped instance of the toil
    chapter's broader document-then-automate doctrine.

- **Novel**: Material new to the corpus:
  - **Dressy ML recommender pipeline** with the streaming-preprocess → train →
    accuracy-gated promotion → serve flow and the >24h stale-model failure
    (Claim 8). Note: Dressy appears elsewhere in the corpus only as the Ch11
    load-shedding miscommunication case study (`docs-google-sre-handling-overload`
    Claim 1) — a different case study from this chapter's ML recommender example.
  - **Pipeline SLO taxonomy** — the three freshness formats, golden-data
    correctness with backward-looking targets, and data-isolation/priority
    (Claims 1-3).
  - **The end-to-end vs per-stage measurement trap** with the dropped-field
    example (Claim 4).
  - **Dependency-failure planning** — SLO-vs-advertised-SLA over-dependence and
    DiRT regional-outage drills (Claim 5).
  - **The pipeline maturity matrix** (Table 13-2, five dimensions scored 1-5)
    as a PRR-style rubric (Claim 13).
  - **Failure-response rules** — "stale data is almost always better than
    incorrect data," the mitigate-then-restore/reprocess two-step, selective
    reprocessing, hotspotting record-blocking + emergency-shutdown flag (Claims
    11, 14-15).
  - **The Spotify event-delivery case study** — hourly-bucket timeliness/skewness/
    completeness SLOs, server-side timestamps, event-type isolation, the postal-
    service no-quality-SLO boundary, the autoscaler-runaway workarounds, and
    staged deployments with manual gates (Claims 16-18).

## Guide Impact

- **Chapter 05 (llm-ops-reliability)**: Add the Dressy ML pipeline (Claim 8) as
  the canonical ML-pipeline case study for the batch-data-pipelines subsection:
  streaming preprocessing → training → accuracy-checked promotion → serving, with
  the >24h stale-model failure as the concrete model-freshness failure mode and
  its three-question diagnostic (stuck input / poor model / stale model in
  production) as runbook material. Add the freshness SLO formats (Claim 1) and
  golden-data correctness (Claim 2) as the SLO vocabulary for eval-data refresh,
  embedding/index backfills, and batch inference. Add the ~1/10/50/100 partial-
  deployment ramp and canary-with-two-phase-mutation lifecycle (Claims 7, 9) for
  dataset/model-promotion changes, checkpointing (Claim 10) for long backfills,
  and the maturity matrix (Claim 13) as the tech-selection rubric. The Prospector
  identified Ch05's dressy reference as needing this chapter's model-freshness
  failure — it is supplied here.

- **Chapter 02 (observability)**: Add pipeline health signals: the three
  freshness formats (Claim 1), golden-data-based correctness monitoring (Claim 2),
  and — prominently — the end-to-end vs per-stage measurement trap (Claim 4):
  telemetry must measure the user-visible end-to-end output, not just per-stage
  health, or cross-stage corruption (a field dropped at one stage, silently
  ignored downstream) goes undetected. The system-diagram-with-live-stage-status
  pattern (Claim 6) is a concrete observability artifact for pipeline on-call.

- **Chapter 04 (oncall-and-toil)**: Add the document-then-automate process
  requirement (Claim 6), playbook entries linked in pipeline alerts (Claim 6),
  and the escalation-path rule that a machine/zonal failure should never trigger
  an SLO page on its own (from the Plan Escalation Paths section) — automated
  mitigation must exhaust before paging. DiRT-style planned-outage drills (Claim
  5) and the corrupt-data two-step recovery with selective reprocessing (Claim
  15) are runbook material for pipeline incidents.

- **Chapter 03 (runbooks-and-agents)**: Add "Verifying your canary is a task that
  lends itself well to automation" (Claim 7) as a direct automation target, the
  system-diagram-with-live-status-links as the navigation artifact (Claim 6), and
  the maturity matrix (Claim 13) as a readiness checklist agents/automation can
  score pipelines against. The emergency-shutdown flag for hotspotting (Claim 11)
  is a codifiable control-plane pattern.

## Extraction Notes

- **Source read**: The full chapter at
  `https://sre.google/workbook/data-processing/` was fetched and read end-to-end
  (all sections through the Conclusion, both figures' captions, and footnotes).
  No linked sub-pages were followed — the chapter is self-contained and its
  outbound links (SRE Book chapters, Workbook Ch16 canarying, cloud docs) are
  already represented in the corpus. The page was confirmed, per the Prospector's
  triage, to be SRE Workbook **Chapter 13**, a document distinct from the 2021
  paper `reliable_data_processing_with_minimal_toil.pdf` already mined as
  `docs-google-sre-reliable-data-processing-minimal-toil.md`. Per the Prospector,
  overlapping content (two-phase mutation, canary via dry-run/1%, freshness/
  correctness SLOs) is cross-referenced rather than re-claimed as novel.
- **Quote verification**: All quotes were copied character-for-character from the
  fetched page text and verified against the tool-output copy of the fetch. The
  Dressy and SLO quotes use the source's curly apostrophes (don't, it's) exactly
  as they appear. Quotes-within-quotes ("golden data," "Chaotic," "Continuous
  improvement," "exactly once") use the source's typographic double quotes.
  Contiguous fragments only, per MINER.md §2a.
- **Related-notes candidates (`miner-related-notes.md`) — dispositions**:
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response, no pipeline reliability content.
  - `docs-google-sre-eliminating-toil.md` — **Cited** (Corroborates Claims 2 and
    12).
  - `docs-google-sre-configuration-specifics.md` — **Dismissed**; config-language
    mechanics, not data pipelines.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**; AI-for-SRE
    tagging/golden-data classification, not pipeline design.
  - `docs-google-sre-prodcast.md` — **Dismissed**; podcast index page.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
    **Dismissed**; DB reliability culture/backup, no pipeline SLOs.
  - `docs-google-sre-reliable-product-launches.md` — **Cited** (Corroborates
    Claims 9 and 10).
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` —
    **Dismissed**; incident-response tooling, not data pipelines.
  - `docs-google-sre-handling-overload.md` — **Cited** (Corroborates Claims 4 and
    6).
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — **Dismissed**;
    org-scale economics of SRE (scale shock, replication norms).
- Additional cross-references beyond the candidate list (per the Prospector's
  triage comments and my own search) were verified per MINER.md §4b against the
  actual claim headings in
  `docs-google-sre-reliable-data-processing-minimal-toil.md` (Claims 6, 10, 12),
  `docs-google-sre-canarying-releases.md` (Claim 16),
  `docs-google-sre-address-cascading-failures.md` (Claim 14), and
  `docs-google-sre-ai-engineering-reliable-operations.md` (Claim 7) — each was
  re-read before citing.
- **No contradiction issue was filed**: no existing source note opposes any Ch13
  claim; the three apparent tensions (stale-vs-incorrect, per-stage-vs-end-to-end
  measurement, batch-vs-streaming) are each resolved within the source or are
  conditioning variables per MINER.md §4a. No open `contradiction`-labeled issues
  exist that this chapter bears on.
- `confidence_overall` is `settled`: official Google SRE Workbook chapter,
  first-party authors (including the Spotify case-study author writing about his
  own system), concrete named systems and tables (DiRT, Datamon, Table 13-1/13-2),
  and production metrics. No claim needed `anecdotal` grading; the Dressy example
  is a fictional worked case, which is disclosed in Source Context.
