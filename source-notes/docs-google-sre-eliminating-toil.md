---
source_url: https://sre.google/workbook/eliminating-toil
source_type: documentation
title: "Google SRE: Eliminating Toil — SRE Workbook Chapter 6"
author: "David Challoner, Joanna Wijntjes, David Huska, Matthew Sartwell, Chris Coykendall, Chris Schrier, John Looney, and Vivek Rau (Google), with Betsy Beyer, Max Luebbe, Alex Perry, and Murali Suriar"
date_published: 2018
date_extracted: 2026-08-08
last_checked: 2026-08-08
status: current
confidence_overall: settled
issue: "#819"
---

# Google SRE: Eliminating Toil — SRE Workbook Chapter 6

> The canonical Google SRE toil playbook: six toil characteristics with worked
> examples, an objective measurement framework (units, continuous tracking,
> don't let measurement become toil), a six-category toil taxonomy, nine toil
> management strategies (engineer it out, reject it, SLO-bound it, human-backed
> interfaces, self-service, start small), automation-safety principles (risk
> assessment before every action, default to human operators, automation is not
> fire-and-forget), and two full case studies (Saturn→Jupiter datacenter network
> repair automation; Moira filer-backed home-directory decommissioning). This is
> the systematic treatment Ch04 needs for its "measuring toil reduction" and
> "auto-remediation candidates vs. always-manual classes" targets, and the
> "automatable runbook-as-pseudocode" framing is a direct basis for Ch03's
> AI-agent automation guidance.

## Source Context

- **Type**: documentation — SRE Workbook (O'Reilly, 2018) Chapter 6
  "Eliminating Toil," published at `sre.google/workbook/eliminating-toil/`, the
  canonical follow-on chapter to SRE Book Chapter 5 "Eliminating Toil." The
  workbook chapter is a distinct, deeper treatment than the SRE Book chapter:
  it adds the "Grows at least as fast as its source" characteristic, a six-part
  toil taxonomy, a measurement methodology, and two long case studies.
- **Author credibility**: Highest available. Written by nine Google SRE
  practitioners (including John Looney, a Production Engineering Manager who
  contributed the first-person "Manual Response to Toil" vignette, and
  Chris Coykendall / Chris Schrier of the network automation effort), edited by
  Betsy Beyer, Max Luebbe, Alex Perry, and Murali Suriar — the editors behind
  the SRE Book/Workbook series. First-party practitioner accounts of systems the
  authors built and operated (datacenter network repair automation, Corp Data
  Storage decommissioning).
- **Scope**: Covers (a) the definition of toil and its six characteristics, each
  with a concrete operational example; (b) how to measure toil objectively
  (units of human effort, continuous tracking, not letting measurement become
  toil); (c) a six-category toil taxonomy (Business Processes, Production
  Interrupts, Release Shepherding, Migrations, Cost Engineering/Capacity
  Planning, Troubleshooting for Opaque Architectures); (d) toil management
  strategies (engineer it out, reject the toil, SLOs, human-backed interfaces,
  self-service, management support, promote as a feature, start small, increase
  uniformity, risk assessment in automation, automate toil response, open-source
  reuse, feedback, legacy systems); (e) Case Study 1: Saturn→Jupiter datacenter
  network line-card repair automation; (f) Case Study 2: Moira decommissioning
  of NetApp filer-backed home directories. Does NOT cover LLM/agent-specific
  workloads directly — the toil taxonomy, measurement, and automation-safety
  principles are the guide's bridge to AI-agent toil reduction. The 50% cap on
  operational work is stated here but the deeper treatment of the 60–70% project
  work target already exists in the corpus (see Cross-References).

## Extracted Claims

### Claim 1: Toil is "the repetitive, predictable, constant stream of tasks related to maintaining a service," falling on a spectrum of six characteristics — Manual, Repetitive, Automatable, Nontactical/reactive, Lacks enduring value, and Grows at least as fast as its source — each demonstrated with a concrete operational example
- **Evidence**: The chapter defines toil and walks each characteristic with a
  worked example (e.g., "disk full" handling for Manual/Repetitive, tmp-directory
  cleanup for Automatable, alert storms for Nontactical/reactive, ticket closure
  that won't prevent recurrence for Lacks enduring value, hardware repairs scaling
  with fleet size for Grows at least as fast as its source). Note this chapter
  lists SIX characteristics, adding "Grows at least as fast as its source" to the
  SRE Book's canonical five.
- **Confidence**: settled
- **Quote**: "For the purposes of this chapter, we'll define toil as the repetitive, predictable, constant stream of tasks related to maintaining a service." — and — "Many classes of operational work grow as fast as (or faster than) the size of the underlying infrastructure."
- **Our assessment**: The six-characteristic spectrum is the checkable taxonomy
  Ch04's "moving beyond 'repetitive work' intuition" target needs. The "Grows at
  least as fast as its source" characteristic is the workbook's addition over the
  SRE Book and matters for agent planning: infra-linked toil will not shrink on
  its own. We buy this fully — it is canonical, first-party SRE doctrine.

### Claim 2: "Automatable" remediation documents — "log in to X, execute this command, check the output, restart Y if you see…" — are "essentially pseudocode to someone with software development skills," making runbook content itself the raw material for automation
- **Evidence**: The Automatable characteristic's worked example explicitly
  frames step-by-step remediation instructions as pseudocode and describes a
  three-stage automation ladder: partial automation of the human-run script →
  fully automated detection+remediation (no human runs the script) → submitting a
  patch so the software never breaks that way again.
- **Confidence**: settled
- **Quote**: "If your team has remediation documents with content like 'log in to X, execute this command, check the output, restart Y if you see…,' these instructions are essentially pseudocode to someone with software development skills!"
- **Our assessment**: The single strongest claim in this chapter for the
  AI-agent/runbook thesis: it asserts directly that the content of remediation
  runbooks is machine-executable spec. This is the corpus's clearest statement
  that runbook-driven automation (including LLM-driven execution of runbooks)
  is a legitimate automation target rather than a category error. We buy it,
  with the caveat (also in this chapter, Claim 12) that automation must not
  eliminate human understanding.

### Claim 3: Google caps SRE teams' operational work (toil and non-toil alike) at 50% of time; the exact target may not suit other orgs, but placing an upper bound on toil matters because identifying and quantifying it is the first step toward optimization
- **Evidence**: Stated in the chapter intro, pointing to SRE Book Chapter 5 for
  rationale. The wording frames the cap on *operational work* (including non-toil
  operational work), which is a slightly different framing than the "toil cap
  with 60–70% project-work target" already extracted from the Dealing with
  Interrupts companion paper (see Cross-References for the delta).
- **Confidence**: settled
- **Quote**: "Google limits the time SRE teams spend on operational work (including both toil- and non-toil-intensive work) at 50% (for more context on why, see Chapter 5 in our first book). While this target may not be appropriate for your organization, there's still an advantage to placing an upper bound on toil, as identifying and quantifying toil is the first step toward optimizing your team's time."
- **Our assessment**: The 50% figure is already in the corpus
  (`docs-google-sre-dealing-with-interrupts.md` Claim 6), so we flag rather than
  re-extract it. The delta: this chapter caps *operational work* (a superset of
  toil), while the interrupts paper caps *toil* specifically and adds the 60–70%
  project-work target. Both are consistent; the guide should state the workbook's
  operational-work framing when discussing the cap's scope. This is a
  conditioning-variable difference, not a contradiction.

### Claim 4: Toil identification should be a data-driven measurement exercise, not experience-and-intuition — choose an objective unit of human effort (minutes/hours, applied patch, completed ticket, manual production change, hardware operation), track it continuously before/during/after the reduction effort, and automate the measurement so collecting it doesn't itself become toil
- **Evidence**: The "Measuring Toil" section argues experience and intuition are
  "not repeatable, objective, or transferable," that team members "often arrive at
  different conclusions regarding the magnitude of engineering effort lost to
  toil," and that long-lived (quarters-to-years) reduction efforts need an
  objective measure to justify cost. Three-step method: identify it, select a
  unit, track continuously with tooling/scripts.
- **Confidence**: settled
- **Quote**: "Select an appropriate unit of measure that expresses the amount of human effort applied to this toil. Minutes and hours are a natural choice because they are objective and universally understood." — and — "Track these measurements continuously before, during, and after toil reduction efforts. Streamline the measurement process using tools or scripts so that collecting these measurements doesn't create additional toil!"
- **Our assessment**: This is the operational answer to Ch04's "measuring toil
  reduction" target. The "unit of human effort" list (tickets, manual production
  changes, patches) is directly countable by an agent/automation layer — it gives
  the guide a citable, non-elapsed-time metric for toil. The "don't let
  measurement become toil" instruction is a useful guardrail for AI-assisted
  measurement (an agent that generates toil while measuring toil is self-defeating).

### Claim 5: Toil falls into six common categories — Business Processes (ticket-driven), Production Interrupts, Release Shepherding, Migrations, Cost Engineering/Capacity Planning, and Troubleshooting for Opaque Architectures — a spectrum, not a binary classification
- **Evidence**: The "Toil Taxonomy" section enumerates all six categories with
  worked detail (ticketing systems as "the human interface to the machine,"
  interrupts as "time-sensitive janitorial tasks," release requests/rollbacks/
  emergency patches, migrations done manually "because, hopefully, you're only
  going to move from X to Y once," cost/capacity planning purchase orders and
  Reserved Instances, and troubleshooting ad hoc log queries on "opaque
  architectures"). The chapter explicitly says the list is not exhaustive.
- **Confidence**: settled
- **Quote**: "The categories in this section aren't exhaustive, but represent some common categories of toil. Many of these categories seem like 'normal' engineering work, and they are. It's helpful to think of toil as a spectrum rather than a binary classification."
- **Our assessment**: This taxonomy is Ch04's candidate "toil classes" map for
  deciding agent-appropriate vs always-manual work. Notable for the guide: the
  "Migrations" and "Release Shepherding" categories are where automation (and
  agents) have the most leverage, while "Troubleshooting for Opaque Architectures"
  explicitly warns against spending effort on recurring (automatable) failures
  instead of novel ones. We buy the taxonomy as a starting framework, not an
  exhaustive list.

### Claim 6: Ticket-driven business processes are insidious toil — they "accomplish their goal," so the toil accumulates quietly across the team without loudly calling for remediation; even without automation, process simplification/streamlining pays off because it makes the process easier to automate later
- **Evidence**: The Business Processes section describes teams as "the human
  interface to the machine," with tickets dispersed evenly across the team so the
  burden doesn't surface. The chapter recommends simplification/streamlining
  independent of automation as a de-risking step.
- **Confidence**: settled
- **Quote**: "Ticket toil is a bit insidious because ticket-driven business processes usually accomplish their goal. Users get what they want, and because the toil is typically dispersed evenly across the team, the toil doesn't loudly and obviously call for remediation."
- **Our assessment**: Explains why ticket toil persists despite being the most
  common toil source — a structural explanation Ch04 should carry. The
  "simplify before automating" advice corroborates the corpus's
  automate-the-process-not-the-hack stance and is a direct input to agent
  rollout sequencing (agents shouldn't automate a convoluted process).

### Claim 7: "Reject the toil" should be the first option considered — analyze the cost of responding versus not responding, and intentionally delay/batch toil so tasks accumulate for batch or parallelized processing, which reduces interrupts and reveals patterns to target for elimination
- **Evidence**: The "Reject the Toil" strategy states this explicitly as "the
  first option you consider," and recommends delaying toil so aggregates form.
  Cost-engineering framing (response vs non-response) parallels the SRE Book's
  error-budget logic.
- **Confidence**: settled
- **Quote**: "In our experience, while it may seem counterproductive, rejecting a toil-intensive task should be the first option you consider. For a given set of toil, analyze the cost of responding to the toil versus not doing so." — and — "Working with toil in larger aggregates reduces interrupts and helps you identify patterns of toil, which you can then target for elimination."
- **Our assessment**: A deliberate counterweight to the automation-heavy framing:
  the cheapest toil reduction is often simply deciding not to do the work. The
  batch-and-delay tactic is directly compatible with ticket-bucketing and
  agent-assisted triage (an agent can hold non-urgent toil for scheduled batch
  processing). Settled — stated as Google's experience.

### Claim 8: SLOs reduce toil by licensing inaction — engineers may ignore operational tasks that don't consume the error budget, and a service-health-focused SLO is more flexible and sustainable than per-device SLOs
- **Evidence**: The "Use SLOs to Reduce Toil" strategy ties to the workbook's
  Implementing SLOs chapter: a well-defined SLO lets engineers decide that a task
  is ignorable within budget, and health-of-service SLOs avoid the toil of
  per-device management.
- **Confidence**: settled
- **Quote**: "A well-defined SLO enables engineers to make informed decisions. For example, you might ignore certain operational tasks if doing so does not consume or exceed the service's error budget."
- **Our assessment**: This is the SLO-driven permission-to-skip mechanism: the
  error budget converts a value judgment into a budget check. Corroborates the
  error-budget-as-signal framing in the SLOs Prodcast note (see Cross-References).
  For the guide, this is how toil triage and error budgets compose: agent-driven
  toil triage can check budget burn before deciding whether to act.

### Claim 9: For complex business problems with many edge cases, use "human-backed interfaces" — a partially automated approach where the service receives structured data via a defined API but engineers still handle some operations — as an interim step toward full automation
- **Evidence**: The "Start with Human-Backed Interfaces" strategy defines the
  "engineer behind the curtain" approach, recommends using customer input to make
  data collection more uniform, and warns against overengineering a big-bang
  solution before the domain is mapped. Reinforced in Case Study 2: "Tickets can
  serve as a quick and dirty GUI for automation."
- **Confidence**: settled
- **Quote**: "In this approach, your service receives structured data—usually via a defined API—but engineers may still handle some of the resulting operations. Even if some manual effort remains, this 'engineer behind the curtain' approach allows you to incrementally move toward full automation."
- **Our assessment**: The strongest "semi-automation" pattern in the corpus and
  the direct antecedent of current human-in-the-loop agent patterns. For the
  guide's Ch03/Ch04, this is the recommended on-ramp for AI-agent handoff:
  typed interfaces first, human fallback kept, full automation later. We buy it
  as settled — it is the pattern both case studies converged on.

### Claim 10: After a typed interface exists, provide self-service methods (web form, script, API, or config-pull-request docs) that degrade gracefully to a ticket on failure — moving 80–90% of requests to self-service is still a huge workload reduction
- **Evidence**: The "Provide Self-Service Methods" strategy gives the VM
  provisioning example and the graceful-degradation design; footnote 4 quantifies
  the 80–90% target and acknowledges some one-off cases can't be self-served.
- **Confidence**: settled
- **Quote**: "Rather than asking engineers to file a ticket to provision a new virtual machine for their development work, give them a simple web form or script that triggers the provisioning. Allow the script to gracefully degrade to a ticket for specialized requests or if a failure occurs."
- **Our assessment**: The graceful-degradation-to-ticket design is the
  human-fallback mechanism an agent system needs: the automation is allowed to
  fail forward into human queue. The 80–90% target is a useful, citable
  planning number for agent-assisted ticket deflection (matches the Bigtable
  ticket funnel result in the Dealing with Interrupts note).

### Claim 11: Automation safety requires risk assessment before every action and safeguards equivalent to the indirect alerts a human would receive — even read operations can spike device load, and automation should default to human operators when it hits an unsafe condition
- **Evidence**: The "Assess Risk Within Automation" strategy lists: validate
  input defensively even from upstream systems; build in safeguards like command
  timeouts or current-outage checks; monitoring/alerting must be consumable by
  machines and humans; read operations can spike load and "as automation scales,
  these safety checks can eventually dominate workload"; "Automation should
  default to human operators if it runs into an unsafe condition." The Saturn
  case study implements this as automated drain-risk assessment plus a secondary
  defense-in-depth check (link/device impact limits that auto-open a tracking
  bug when exceeded).
- **Confidence**: settled
- **Quote**: "Every action should be assessed for its safety before execution. This includes changes that might reduce serving capacity or redundancy." — and — "Automation should default to human operators if it runs into an unsafe condition."
- **Our assessment**: A complete, copyable safety checklist for the guide's
  automation/agent execution guidance. The "read operations can spike load"
  warning is a non-obvious detail directly relevant to agent-driven
  observability queries hammering telemetry backends. This is the workbook's
  version of what the AI-in-SRE whitepaper formalizes as real-time risk
  evaluation and a safety control plane (see Cross-References).

### Claim 12: Don't literally transcribe human workflows into machine workflows — break the documented manual work into separable, composable components for reuse, and don't let automation eliminate human understanding of what's going wrong
- **Evidence**: The "Automate Toil Response" strategy: "You rarely want to
  literally transcribe a human workflow into a machine workflow," break manual
  work into "components that can be implemented separately and used to create a
  composable software library that other automation projects can reuse later,"
  and "automation shouldn't eliminate human understanding of what's going wrong."
  Corroborated by the Jupiter case study's lesson that automation "often provides
  the opportunity to reevaluate and simplify human workflows."
- **Confidence**: settled
- **Quote**: "Once your process is thoroughly documented, try to break down the manual work into components that can be implemented separately and used to create a composable software library that other automation projects can reuse later." — and — "You rarely want to literally transcribe a human workflow into a machine workflow. Also note that automation shouldn't eliminate human understanding of what's going wrong."
- **Our assessment**: Two durable principles for Ch03: (1) automation is a
  re-design opportunity, not transcription — the guide should warn against
  automating a process verbatim; (2) human understanding is a first-class output
  of automation design, which directly contradicts the naive "fully autonomous
  agent" goal and supports keeping humans informed even where agents act.
  Settled.

### Claim 13: "Sometimes imperfect automation is good enough" — skip verification for low-risk paths, and don't overthink the problem; Google spent three years (2012–2015) collecting data on 650+ memory-error incidents before concluding the diagnosis exercise was overkill
- **Evidence**: Two case-study lessons: (a) BERT link verification was skipped
  for network-management links because they carried no customer traffic ("We were
  comfortable bypassing verification because the links didn't carry customer
  traffic"); (b) the memory-error diagnosis effort — "We spent nearly three years
  (2012–2015) collecting data on over 650 discrete memory error problems before
  realizing this exercise was probably overkill" — and one quarter of data showed
  "most of the errors were transient—most switches recovered after being rebooted
  and reinstalled," so the delay was unnecessary. Jupiter treated memory errors
  like failed line cards by adding one symptom to a config file.
- **Confidence**: settled
- **Quote**: "We spent nearly three years (2012–2015) collecting data on over 650 discrete memory error problems before realizing this exercise was probably overkill, or at least shouldn't block our repair automation project."
- **Our assessment**: The "good enough / act now, measure later" principle is a
  direct antidote to automation analysis-paralysis — and a strong justification
  for starting small (Claim 15). The 650-incidents/3-years over-collection
  episode is a concrete, quotable failure of over-engineering. For agents, this
  supports instrumenting for a bounded pilot rather than waiting for perfect
  data. Settled as Google's own reported lesson.

### Claim 14: Automation is not fire-and-forget — it has a very long lifetime, needs project continuity as people join/leave, and inflexible automation makes systems brittle to change; policy-based automation (separating intent from a generic implementation engine) lets automation evolve more transparently
- **Evidence**: The "Repair automation is not fire and forget" lesson: Saturn
  fabrics outlived their end-of-life due to Jupiter parts shortages, requiring
  late improvements; "Once adopted, automation may become entrenched for a long
  time, with positive and negative consequences"; policy-based automation is
  recommended to separate intent from implementation. The "Get a failure budget
  and manager support" lesson adds: "Repair automation can sometimes fail,
  especially when first introduced" and "We recommend establishing an error
  budget for antitoil automation."
- **Confidence**: settled
- **Quote**: "Once adopted, automation may become entrenched for a long time, with positive and negative consequences. When possible, design your automation to evolve in a flexible way. Relying on inflexible automation makes systems brittle to change." — and — "We recommend establishing an error budget for antitoil automation."
- **Our assessment**: The automation-as-liability framing (long-lived, must be
  maintained, can fail) is exactly what the guide's toil-reduction section must
  balance against the "automation removes toil" enthusiasm. The "error budget for
  antitoil automation" is a concrete governance mechanism: automation itself can
  consume reliability budget when it breaks. Directly applicable to AI-agent
  automation, which adds a model-upgrade drift dimension on top of the software
  lifetime problem.

### Claim 15: Start small and improve — don't design the perfect toil-free system; automate a few high-priority items first, then reinvest the gained time and lessons
- **Evidence**: The "Start Small and Then Improve" strategy: "Don't try to design
  the perfect system that eliminates all toil. Automate a few high-priority items
  first, and then improve your solution using the time you gained by eliminating
  that toil," with clear metrics such as MTTR. Both case studies followed a
  phased, incremental path (Saturn before Jupiter; Moira's four phases over years).
- **Confidence**: settled
- **Quote**: "Automate a few high-priority items first, and then improve your solution using the time you gained by eliminating that toil, applying the lessons learned along the way."
- **Our assessment**: Consistent with the corpus's incremental-autonomy
  recommendation (assist → act → self-direct) and the workbook's own
  imperfect-automation lesson. The "pick clear metrics such as MTTR" ties toil
  reduction to measurable outcomes. Settled.

### Claim 16: Case Study 1 (Saturn→Jupiter datacenter network repair) shows automation can replace most human repair work when failure volumes outgrow the team — a software-enforced strike policy (first failure reboots/reinstalls, second triggers hardware replacement), automated drain-risk assessment, and a technician UI — with Jupiter automating switch-wide drain, config install/verify, and repair-verification before undrain
- **Evidence**: Problem dimensions: "We couldn't grow the team fast enough to
  keep up with the volume of failures," "Performing the same steps repeatedly and
  frequently introduced too many human errors," and no way to prioritize or
  handle transient failures. The Saturn design: repurposed alerting to trigger
  automated repair, "automated risk assessment to prevent accidental isolation of
  devices during a drain... This eliminated a huge source of human errors," and a
  strike policy tracked by software. Jupiter scale: "our next-generation
  datacenter fabric, Jupiter, was more than six times larger than any previous
  Google fabric. The volume of problems was also six times larger." Failures
  identified: technician UI state-sync problems, reliance on experienced
  technicians ("Experience is difficult to replicate" — a technician drained every
  line card concurrently, "resulting in network congestion and user-visible
  packet loss"), and under-testing with new technicians.
- **Confidence**: settled
- **Quote**: "We built in automated risk assessment to prevent accidental isolation of devices during a drain and to trigger safety mechanisms where required. This eliminated a huge source of human errors." — and — "the first failure (or strike) only rebooted the card and reinstalled the software. A second failure triggered card replacement and full return to the vendor."
- **Our assessment**: The strike policy is a concrete, citable remediation
  escalation design: try software recovery once, then escalate to hardware
  replacement — exactly the bounded-autonomy pattern agents need (attempt
  fix-forward once, escalate after recurrence). The "don't rely on human
  expertise" and "test with new technicians" lessons map directly to agent
  rollout: automation must not assume the operator knows the edge cases, and
  untested operators (human or automated) cause incidents. Settled — a documented,
  multi-year Google deployment.

### Claim 17: Case Study 2 (Moira — decommissioning NetApp filer-backed home directories) shows data-driven toil rejection at scale: Moonwalk (BigQuery analytics over 2.5 billion files) validated which use cases to retire; a self-service Flask portal handled user communication/migration as "low-touch as possible"; tickets served as a "quick and dirty GUI for automation" with a manual SRE fallback queue; "melt snowflakes" (retool or delete nonconforming shares) enabled near-zero-touch migration; the program reduced home directories from 65,000 to ~50
- **Evidence**: "Moonwalk stored the data about who was accessing what files and
  when in BigQuery... summarized access patterns across 2.5 billion files using
  300 terabytes of disk space. This data was owned by 60,000 POSIX users in 400
  disk volumes on 124 NAS appliances in 60 geographic sites." The portal
  requirements (landing page, FAQ, status/usage info, request/archive/delete/
  extend/reactivate options) and human-backed bug routing; "Automation craves
  conformity" for the snowflake-melting; "The program officially completed in
  2016. We've reduced home directories from 65,000 to around 50 at the time of
  writing." Also the strategic framing: primary business justification was
  Beyond Corp security, not toil reduction — "emphasizing the many security
  benefits of decommissioning filers made for a more compelling business case."
- **Confidence**: settled
- **Quote**: "Tickets can serve as a quick and dirty GUI for automation: they keep a log of work, update stakeholders, and provide a simple human fallback mechanism if automation goes awry." — and — "The program officially completed in 2016. We've reduced home directories from 65,000 to around 50 at the time of writing."
- **Our assessment**: The strongest real-world demonstration in the corpus of the
  human-backed-interface strategy at scale (engineer-behind-the-curtain plus
  ticket-as-fallback). The "couple toil reduction with a compelling business goal
  (security)" lesson is the "promote toil reduction as a feature" strategy in
  action. "Melt snowflakes" — changing reality to fit the code — is a contrarian
  but effective pattern worth flagging with its governance caveat. Settled.

### Claim 18: The legacy-system exit path has four stages — Avoidance, Encapsulation/augmentation, Replacement/refactoring, Retirement/custodial ownership — and decommissioning should start by slowing new adoption ("It's much more painful to take something away from users than never offer it in the first place")
- **Evidence**: The "Legacy Systems" section defines all four stages, with
  encapsulation "a bit like refinancing high-interest technical debt into
  low-interest technical debt," replacement best done incrementally behind a
  common interface with canarying/blue-green, and retirement aligning business
  incentives ("stragglers who haven't migrated can assume custodial ownership").
  Moira's phase-one targeting of least-usage users operationalizes the
  slow-adoption-start.
- **Confidence**: settled
- **Quote**: "Avoidance is effectively choosing to accept technical debt and to move away from SRE principles and toward system administration." — and — "It's much more painful to take something away from users than never offer it in the first place."
- **Our assessment**: A directly citable roadmap for the guide's migration
  guidance (e.g., legacy model-serving stacks). The "encapsulation = refinancing
  technical debt" framing is a useful economic metaphor, and the
  slow-new-adoption-first sequencing matches corpus guidance to reduce blast
  radius. Settled.

## Concrete Artifacts

### Artifact A — The six toil characteristics with their worked examples (verbatim, condensed from the chapter)

```
Manual        When the tmp directory on a web server reaches 95% utilization,
              engineer Anne logs in to the server and scours the filesystem for
              extraneous log files to delete.
Repetitive    A full tmp directory is unlikely to be a one-time event, so the
              task of fixing it is repetitive.
Automatable   "If your team has remediation documents with content like 'log in
              to X, execute this command, check the output, restart Y if you
              see…,' these instructions are essentially pseudocode to someone
              with software development skills!"
Nontactical/  Too many "disk full"/"server down" alerts distract engineers from
reactive      higher-value engineering and potentially mask higher-severity
              alerts; "the health of the service suffers."
Lacks         Closing an alert-generated ticket won't prevent the issue in the
enduring      future, "so the payback has a short duration."
value
Grows at      Hardware-repair time scales in lock-step with fleet size, but
least as      ancillary tasks (software/config changes) "doesn't necessarily
fast as its   have to."
source
```

### Artifact B — The three-step toil measurement method (verbatim-condensed from the chapter)

```
1. Identify it. "The people best positioned to identify toil depend upon your
   organization. Ideally, they will be stakeholders, including those who will
   perform the actual work."
2. Select an appropriate unit of measure that expresses the amount of human
   effort applied to this toil. "Minutes and hours are a natural choice because
   they are objective and universally understood. Be sure to account for the
   cost of context switching." Other examples: an applied patch, a completed
   ticket, a manual production change, a predictable email exchange, a hardware
   operation.
3. Track these measurements continuously before, during, and after toil
   reduction efforts. "Streamline the measurement process using tools or
   scripts so that collecting these measurements doesn't create additional
   toil!"
```

### Artifact C — The six-category toil taxonomy (verbatim-condensed)

```
1. Business Processes        "the most common source of toil"; ticket-driven,
                             your team is "the human interface to the machine."
2. Production Interrupts     "time-sensitive janitorial tasks that keep systems
                             running" (free disk, restart leaky apps, replace
                             hard drives, "kick" unresponsive systems).
3. Release Shepherding       Even with automated deploys and CI: "release
                             requests, rollbacks, emergency patches, and
                             repetitive or manual configuration changes, releases
                             may still generate toil."
4. Migrations                Done manually "because, hopefully, you're only going
                             to move from X to Y once" — but migration work can
                             still meet many criteria of toil.
5. Cost Engineering and      Purchase orders, AWS Reserved Instances, holiday
   Capacity Planning         launch prep, "spot"/"preemptable" resource
                             refactoring, oversubscribed-resource handling.
6. Troubleshooting for       "aim to focus your energy on novel failure modes—not
   Opaque Architectures      the same type of failure every week caused by brittle
                             system architecture." Four 9s + nine four-9s
                             dependencies = three 9s.
```

### Artifact D — The Saturn line-card repair workflow with automation (verbatim-condensed, Figure 6-4 narrative)

```
1. The problematic line card is detected and a symptom is added to a specific
   component in the database.
2. The repair service picks up the problem, performs a risk assessment to
   confirm no capacity will be isolated, then:
   a. Drains traffic from the entire switch.
   b. Shuts down the line card.
   c. First failure → reboot the card and undrain the switch (workflow done).
   d. Second failure → proceed to step 3.
3. The workflow manager sends the case to a pool of repair cases for a
   technician to claim.
4. The technician claims the case, sees a red "stop" in the UI (switch must be
   drained before repairs), then:
   a. Initiates the chassis drain via a "Prep component" button.
   b. Waits for the red "stop" to clear.
   c. Replaces the card and closes the case.
5. The automated repair system brings the line card up; after a pause for the
   card to initialize, traffic is restored and the repair case is closed.
```

### Artifact E — The four-stage legacy-system exit path (verbatim-condensed)

```
1. Avoidance: "accepting technical debt and to move away from SRE principles
   and toward system administration."
2. Encapsulation/augmentation: build a shell of abstracted APIs, automation,
   config management, monitoring, and testing around the legacy system;
   "refinancing high-interest technical debt into low-interest technical debt."
3. Replacement/refactoring: define a common interface in front of the legacy
   system; migrate "slowly and safely" using release-engineering techniques
   "like canarying or blue-green deployments"; build production-sized datasets
   of historical expected inputs/outputs to check for divergence.
4. Retirement/custodial ownership: "stragglers who haven't migrated can assume
   custodial ownership of remnants of the legacy system."
```

### Artifact F — Case Study 2 (Moira) key metrics and tooling (verbatim-condensed)

```
- Moonwalk dataset: "2.5 billion files using 300 terabytes of disk space...
  60,000 POSIX users in 400 disk volumes on 124 NAS appliances in 60 geographic
  sites around the world."
- Portal: Python/Flask, reading/writing Bigtable, background jobs + schedulers.
- Outcome: "We've reduced home directories from 65,000 to around 50 at the time
  of writing."
- Team: "averaging three CDS team members" over the life of the project.
- Sequenced sub-projects: Moira (home-dir decommissioning), Tekmor (long tail),
  Migra (Team Share decommissioning), Azog (infrastructure retirement).
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-dealing-with-interrupts.md` **Claim 6** (toil capped at
    maximum 50% of engineering time, with 60–70% expected on project work) —
    this chapter states the same 50% ceiling but framed as a cap on *operational
    work including non-toil* (Claim 3 here). The delta is framing, not substance;
    the interrupts note carries the stronger 60–70% project-work target that this
    chapter does not restate. Flagged rather than re-extracted per the triage
    guidance.
  - `docs-google-sre-dealing-with-interrupts.md` **Claim 8** (Bigtable ticket
    funnel cut ticket creation roughly in half, 30+ → 15+ per week) — the
    funnel/self-service deflection mechanism corroborates this chapter's
    self-service + graceful-degrade-to-ticket strategy (Claim 10 here) and the
    "ticket toil is insidious" diagnosis (Claim 6 here).
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` **Claim 7**
    (batch-job safety levels 0–3 with the toil↔blast-radius policy tradeoff;
    "Level 3 = no humans involved") — an independent Google source reaching the
    same conclusion as this chapter's "Assess Risk Within Automation" (Claim 11
    here): automation level is a risk-bounded decision, and higher automation
    levels are justified only where blast radius is controlled.
  - `docs-google-sre-ai-engineering-reliable-operations.md` **Claim 2** (Safety
    Trifecta — Real-time Risk Evaluation assesses every proposed action against
    production context) and **Claim 5** (Actus control plane: mandatory dry-runs,
    dynamic autonomy downgrade, default-to-human on unsafe conditions) — the
    whitepaper formalizes this chapter's 2018 risk-assessment-in-automation
    principle (Claim 11 here) into the named architecture for AI agents. Direct
    intellectual lineage; the workbook's "Automation should default to human
    operators if it runs into an unsafe condition" is the pre-agent statement of
    Actus's L3→L2 downgrade.
  - `docs-google-sre-twenty-years-lessons.md` **Claim 4** (every service
    dependency should have a Big Red Button identified before risky changes) —
    corroborates the case-study-1 defense-in-depth lesson and the
    "error budget for antitoil automation" recommendation (Claim 14 here);
    both sources independently prescribe emergency-stop mechanisms for
    automation.
  - `docs-google-sre-reliable-product-launches.md` **Claim 9** (all manual
    processes must be documented before launch — "to ensure that the information
    is translated from an engineer's mind onto paper while it is still fresh")
    — corroborates this chapter's "once your process is thoroughly documented,
    break down the manual work" automation precondition (Claim 12 here);
    documentation-before-automation is a shared Google SRE doctrine.
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` **Claim 2** (change-management
    systems minimize both false negatives and false positives, "enabling higher
    feature velocity with low toil") — corroborates that Release Shepherding
    (taxonomy category 3 here) is automatable toil; Treynor's safe-change systems
    are the serving-side instance of the automation this chapter describes.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` **Claim 12** (error
    budgets are the signal for *when to investigate* an infrastructure problem)
    — corroborates this chapter's "Use SLOs to Reduce Toil" (Claim 8 here): the
    error budget licenses which operational work to skip.
  - `docs-google-sre-handling-overload.md` **Claim 8** (denominate request costs
    in the scarcest resource; "If CPU is the scarcest thing in your system then
    use that to express all of your costs") — the same cost-analysis discipline
    as this chapter's "Reject the Toil" (Claim 7 here): decide whether to
    respond by costing the work. Both are Google's cost-engineering lens on
    operational decisions.

- **Contradicts**: None identified. All claims are consistent with existing
  source notes and with SRE canon. Specific checks: (a) the 50% cap framing
  delta (operational work vs toil; Claim 3 here vs `dealing-with-interrupts`
  Claim 6) is a conditioning-variable difference — the workbook explicitly
  includes non-toil operational work in the cap and says the exact target "may
  not be appropriate for your organization," so no real opposition; (b) this
  chapter's "reject the toil / delay toil" emphasis (Claim 7) vs the
  dealing-with-interrupts note's "interrupt reduction projects" (Claim 7 there)
  are complementary tactics, not opposed; (c) the "automatable runbook as
  pseudocode" claim (Claim 2 here) is stronger than anything in the corpus but
  contradicts nothing — the Prodcast/AI-in-SRE notes assume runbook automation
  is viable, this chapter provides the canonical authority. No contradiction
  issue filed.

- **Extends**:
  - `docs-google-sre-dealing-with-interrupts.md` — that note covers *interrupt
    management* (tickets/pages/ongoing responsibilities, polarized time). This
    chapter is the broader, systematic toil treatment: the interrupt categories
    map into this chapter's "Production Interrupts" taxonomy entry and the
    "Reject the Toil"/"Start with Human-Backed Interfaces" strategies are the
    operational mechanisms behind the interrupts note's ticket-funnel and
    interrupt-reduction-project patterns. Together they give Ch04 both the
    taxonomy (this note) and the load-management playbook (that note).
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` — that paper
    applies automation safety to batch jobs specifically (safety levels, dry
    runs, canarying). This chapter supplies the general toil-management
    framework (taxonomy, measurement, strategies) within which the batch safety
    levels sit. This note is the parent; that note is the batch specialization.
  - `docs-google-sre-ai-engineering-reliable-operations.md` — the whitepaper's
    Autonomy Levels (L0–L4) and Actus control plane are the agent-era
    implementation of this chapter's "human-backed interfaces" (Claim 9) and
    risk-assessment-in-automation (Claim 11). The workbook chapter is the
    2018 pre-agent grounding the Smith can cite for the lineage.
  - `docs-google-sre-twenty-years-lessons.md` — that note's Claim 9 (automate
    mitigations for clear failure signals to reduce MTTR) is the incident-side
    instance of this chapter's automate-toil-response doctrine; this note adds
    the toil-classification criteria for deciding *which* mitigation signals are
    safe to automate.

- **Novel**: Material new to the corpus:
  - **The six-characteristic toil definition with worked examples** (Claim 1),
    including the workbook's added "Grows at least as fast as its source"
    characteristic — no existing note enumerates the characteristics.
  - **The six-category toil taxonomy** (Claim 5) — Business Processes, Production
    Interrupts, Release Shepherding, Migrations, Cost Engineering/Capacity
    Planning, Troubleshooting for Opaque Architectures. Directly adoptable as
    Ch04's "toil classes" map for agent-vs-manual assignment.
  - **The objective toil-measurement methodology** (Claim 4) — units of human
    effort (patch/ticket/manual change), continuous before/during/after tracking,
    don't-let-measurement-become-toil.
  - **The "reject the toil / delay and batch toil" strategy** (Claim 7) — a
    non-automation lever not present elsewhere.
  - **Human-backed interfaces as a named partial-automation pattern** (Claim 9)
    with the ticket-as-GUI-for-automation mechanism (Artifact F) — the clearest
    statement of the semi-automation on-ramp in the corpus.
  - **The "automatable runbook is pseudocode" claim** (Claim 2) — canonical
    authority for Ch03's runbook-automation premise.
  - **The automation-safety checklist** (Claim 11) — risk assessment before every
    action, human-equivalent safeguards, read-ops-can-spike-load, default-to-human
    — and the "error budget for antitoil automation" governance idea (Claim 14).
  - **The Saturn/Jupiter datacenter repair case study** (Claim 16) with the
    strike policy (reboot-then-replace) and the three-years-of-data-collection
    overkill lesson (Claim 13).
  - **The Moira filer-decommissioning case study** (Claim 17) with Moonwalk's
    2.5-billion-file dataset and the 65,000→50 home-directory result.
  - **The four-stage legacy-system exit path** (Claim 18) — Avoidance →
    Encapsulation → Replacement → Retirement.

## Guide Impact

- **Chapter 04 (oncall-and-toil)**: The primary target, and both stated targets
  are currently unsourced stubs. (1) *Measuring toil reduction*: add Claim 4's
  objective-unit methodology (tickets, manual production changes, patches —
  countable by an agent layer), the 50% operational-work cap with the
  cross-referenced 60–70% project target (Claim 3), and Claim 13's
  act-now-measure-later caution. (2) *Auto-remediation candidates vs
  always-manual classes*: adopt Claim 5's six-category taxonomy as the
  classification map — Release Shepherding, Migrations, and ticket-driven
  Business Processes are the high-leverage agent classes; Troubleshooting for
  Opaque Architectures and novel-failure diagnosis are the always-manual /
  always-human classes (the chapter itself says to focus human energy on novel
  failure modes). (3) Add the toil-management strategy set (Claims 7–10, 15) as
  the chapter's playbook, especially "Reject the Toil" (a non-automation lever)
  and "Start with Human-Backed Interfaces" (the agent-handoff on-ramp).
- **Chapter 03 (runbooks-and-agents)**: Add Claim 2 ("automatable runbook is
  pseudocode") as the canonical authority for treating remediation runbooks as
  machine-executable spec — the premise the chapter's AI-runbook automation
  guidance rests on. Add Claim 12 (don't transcribe workflows; build composable
  components; preserve human understanding) as a design principle, and Claim 11's
  safety checklist (risk-assessment-before-action, default-to-human, read-ops
  can spike load) as the agent-safety baseline. Add Claim 14 (automation is not
  fire-and-forget; error budget for antitoil automation) as the maintenance/governance
  requirement for any agent-run automation.
- **Chapter 02 (observability)**: Add Claim 9's SLO-licenses-skipping pattern
  (ignore toil that doesn't consume the error budget) as the decision rule that
  ties toil triage to error-budget burn — the same budget-as-signal principle as
  the SLOs Prodcast note, now applied to toil triage. Add Claim 4's "measure with
  tooling so measurement doesn't become toil" as a design constraint for
  telemetry-dashboards-as-toil.
- **Chapter 05 (llm-ops-reliability)**: Add Claim 16's strike-policy escalation
  (attempt software recovery once, replace on recurrence) as the remediation-
  escalation pattern for model/inference component failures, and Claim 18's
  four-stage legacy-exit path as the roadmap for decommissioning legacy
  model-serving stacks (avoidance → encapsulation → replacement behind a common
  interface → retirement).

## Extraction Notes

- **Source read**: The workbook chapter at
  `https://sre.google/workbook/eliminating-toil/` was fetched and read
  end-to-end (full chapter text, both case studies, all "Lessons Learned"
  sections, conclusion, and footnotes). It is a single self-contained page; no
  linked sub-pages were needed. This is the canonical workbook treatment of toil
  (distinct from SRE Book Ch5, which is linked but not re-extracted here). Per
  the triage comments, the 50% cap overlap with
  `docs-google-sre-dealing-with-interrupts.md` Claim 6 was flagged (Claim 3) and
  the delta (operational-work vs toil framing) noted rather than re-extracted.
- **Quote verification**: All quotes were copied character-for-character from the
  fetched page text. Two characters to note for the Assayer: the Automatable
  characteristic quote uses the source's ellipsis character ("…") inside
  "restart Y if you see…," and quoted-within-quote passages use the source's
  single quotes. Verbatim fragments were kept contiguous per MINER.md §2a.
- **Related-notes candidates (`miner-related-notes.md`) — dispositions**:
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response, no toil taxonomy/measurement.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` —
    **Dismissed**; incident-response tooling, not toil management.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — **Dismissed**;
    org-scale economics of SRE (scale shock, replication norms).
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**;
    AI-for-SRE tagging/golden data, not toil.
  - `docs-google-sre-prodcast.md` — **Dismissed**; podcast index page.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
    **Dismissed**; DB reliability culture/burnout; its toil-adjacent claims
    (predict-failure, outage-driven work) are already cross-referenced via the
    dealing-with-interrupts and reliable-data-processing notes.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` — **Cited**
    (Corroborates, Claim 12).
  - `docs-google-sre-reliable-product-launches.md` — **Cited** (Corroborates,
    Claim 9).
  - `docs-google-sre-handling-overload.md` — **Cited** (Corroborates, Claim 8).
  - `blog-incidentio-ai-sre-incident-run.md` — **Dismissed**; AI incident-run
    experience, incident response not toil management.
- **Additional cross-references found by corpus search beyond the candidate
  list**: `docs-google-sre-dealing-with-interrupts.md` (Claims 6, 8 — flagged
  overlap + ticket-funnel corroboration), `docs-google-sre-reliable-data-processing-minimal-toil.md`
  (Claim 7), `docs-google-sre-ai-engineering-reliable-operations.md` (Claims 2,
  5), `docs-google-sre-twenty-years-lessons.md` (Claim 4),
  `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` (Claim 2). All cited claim
  numbers were verified against the actual `### Claim:` headings per MINER.md
  §4b.
- **Contradiction check**: No open `contradiction`-labeled issues exist
  (verified via `gh issue list --label contradiction --state open`), and no claim
  here opposes an existing source note. The 50%-cap framing delta and the
  reject-the-toil vs interrupt-reduction-project emphases are conditioning
  variables, not oppositions. Per MINER.md §4a, no contradiction issue was filed.
- **Issue #297 note**: The triage comments correctly note that closed issue #297
  had triaged the *landing page* URL (`/resources/book-update/eliminating-toil/`)
  and identified this workbook URL as the substantive content; no note was ever
  produced for it. This extraction covers the workbook chapter as the actionable
  path for that content. No duplication with any existing source note.
- **Confidence rationale**: `confidence_overall: settled` — official Google SRE
  Workbook chapter authored by Google SRE practitioners with two documented,
  multi-year case studies and quantified outcomes (65,000→50 home directories;
  six-times-larger fabric volume; 650 incidents / 3 years of over-collection).
  No claim required `anecdotal` grading; the two case-study lessons are stated as
  the teams' own retrospective findings.
