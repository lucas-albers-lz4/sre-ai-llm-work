---
source_url: https://sre.google/resources/practices-and-processes/infrastructure-change-management/
source_type: docs
title: "Case Studies in Infrastructure Change Management: How Google Rebuilds the Jet While Flying It"
author: "Wendy Look and Mark Dallman (Technical Program Managers, Google SRE)"
date_published: 2019-10-23
date_extracted: 2026-07-23
last_checked: 2026-07-23
status: current
confidence_overall: settled
issue: "#431"
---

# Case Studies in Infrastructure Change Management

> An authoritative practitioner account of two massive Google infrastructure
> migrations — GFS→Colossus ("Moonshot") and local disk→diskless compute —
> documenting the tools, processes, staffing, and communication patterns that
> succeeded and failed. Includes a reusable 10-item preflight checklist for
> large-scale infrastructure change. Extends the conceptual safe-change-management
> discussions from other Google SRE source notes with concrete post-hoc
> case-study evidence.

## Source Context

- **Type**: docs (O'Reilly report, free PDF, published on sre.google — part of the
  official Google SRE resource library)
- **Author credibility**: High. Both authors are Technical Program Managers in
  Google SRE, specializing in infrastructure change management. Wendy Look has
  been at Google since 2012; Mark Dallman specializes in infrastructure change
  and capacity management. The report was published by O'Reilly in collaboration
  with Google and reviewed by Niall Richard Murphy (co-author of the SRE Book)
  and Grace Petegorsky. The primary source (the PDF) was read in full; the
  sre.google landing page is a brief summary with a download link. This note
  extracts from the PDF.
- **Scope**: Two detailed case studies: (1) the GFS→Colossus migration
  ("Moonshot," ~2010–2012) and (2) the local disk→diskless compute transition
  ("Diskless," ~2012–2018). Covers the specific tools built, processes used,
  capacity planning (including the "Steamroller" resource-reclamation project),
  staffing challenges, communication breakdowns, and lessons learned. Does NOT
  cover AI/ML operations, agent architectures, or any post-2019 technology. The
  preflight checklist (10 items) is extracted as a reusable pattern.

## Extracted Claims

### Claim 1: Google's Infrastructure Change Management (ICM) program uses a four-phase lifecycle — Concept, Backlog, Planning, Execution — driven by a dedicated team of TPMs who centrally drive migrations, deprecations, and other large-scale infrastructure changes
- **Evidence**: Authoritative (Google's official SRE documentation). The ICM
  lifecycle is described in detail with each phase's activities.
- **Confidence**: settled
- **Quote**: "The ICM program at Google, consisting of a dedicated team of
  technical program managers (TPMs), does just that: centrally driving migrations,
  deprecations, and other large-scale changes to infrastructure."
- **Our assessment**: A concrete, named organizational structure (ICM) with a
  defined lifecycle. This is useful as an organizational pattern the guide can
  reference: rather than treating large infrastructure changes as ad-hoc projects,
  institutionalize a dedicated change-management function with a standardized
  lifecycle. The four-phase model (Concept → Backlog → Planning → Execution) is
  simple enough to be replicable.

### Claim 2: The MapReduce→Flume deprecation (driven by ICM) achieved over 99% C++ and Java pipeline migration with only 12 engineers staffing the support rotation, demonstrating ICM's effectiveness at managing large-scale deprecations
- **Evidence**: Quantitative metrics from the report: 50% of 30-day active build
  targets migrated in the first year (2018); by September 2019, over 45% of the
  remaining active targets were migrated; Flume reached over 99% C++ and Java
  pipeline adoption; support rotation staffed with 12 engineers.
- **Confidence**: settled
- **Quote**: "During 2018, 50% of 30-day active build targets migrated off
  MapReduce and, by September 2019, over 45% of the remaining active targets were
  off MapReduce. As of 2019, Flume was rolled out to over 99% of C++ and Java
  pipelines, and the Flume support rotation was staffed with 12 engineers."
- **Our assessment**: The MapReduce→Flume migration is presented as a successful
  example of ICM-driven change. The metrics are concrete and credible. For the
  guide, this shows ICM's model in practice and provides a baseline for what
  "successful" infrastructure change management looks like at Google scale — a
  useful benchmark, though the staffing (12 engineers for the support rotation)
  is specific to Google's size and tooling.

### Claim 3: The Moonshot project (GFS→Colossus migration) was initially communicated as a 1-year project but actually took 2 years — the initial communication "completely undersold the effort, complexity, and difficulty"
- **Evidence**: The report states the initial mandate was to complete migration
  "by the end of 2011" but then states "it took a full two years to migrate all
  of Google's services from GFS to Colossus." The internal newsletter quote
  shows the optimistic tone.
- **Confidence**: settled
- **Quote**: "The initial communication completely undersold the effort,
  complexity, and difficulty of this project."
- **Our assessment**: A candid admission of planning failure at the outset of one
  of Google's largest migrations. For the guide, this is a concrete warning about
  underestimating infrastructure change timelines. The 2× factor (1 year stated,
  2 years actual) is a useful heuristic: infrastructure changes at Google scale
  took roughly twice the initial estimate. This corroborates the general
  software-engineering wisdom about estimation bias but grounds it in a
  high-stakes Google case.

### Claim 4: GFS had six specific architectural limitations that necessitated the migration to Colossus — including that the GFS Master was a single-machine single-process bottleneck with a 10–30 minute restart time and no persistent index of chunk locations
- **Evidence**: The report lists six concrete GFS limitations: (1) clusters grew
  past thousands of machines; (2) user-facing systems like Gmail used GFS as
  backend and minute-long failures were unacceptable; (3) RAM stored chunk
  locations (limited by physical memory); (4) no persistent index so restarting
  the Master took 10–30 minutes to recompute chunk maps; (5) Master was a single
  machine / single process (shadow masters were read-only); (6) Master software
  was partially single-threaded and couldn't use SMP hardware fully.
- **Confidence**: settled
- **Quote**: "The GFS Master software couldn't take full advantage of SMP
  hardware because portions of the GFS Master software were single threaded."
- **Our assessment**: The six limitations provide a concrete, technically detailed
  rationale for why GFS needed replacement. The single-master bottleneck and 10–30
  minute restart are especially relevant as failure-mode documentation. For the
  guide, this is useful as a real example of how architectural constraints drive
  infrastructure change — not abstract "technical debt" but specific,
  measurement-backed limitations.

### Claim 5: Google built five custom migration tools for the Moonshot project — a quota dashboard, quota move service, migration planning/scheduling tool, migration tracking tool, and bulk data migration service — that automated "a non-trivial amount of work" and "minimized human error"
- **Evidence**: The report describes each tool in detail with its function. The
  tools were custom-built by Google SREs specifically for this migration.
- **Confidence**: settled
- **Quote**: "These tools automated a non-trivial amount of work, and helped the
  team manage and track the migration, as well as the quota, so that team members
  would not have to do so manually themselves. The tools made the migration less
  troublesome and minimized human error."
- **Our assessment**: The five-tool catalog is a concrete artifact: specific,
  named systems with documented functions. For the guide, this provides a
  template for what tooling an infrastructure change requires: visibility into
  current usage (dashboard), automated resource reallocation (quota move),
  scheduling with disruption awareness, tracking/progress communication, and
  bulk data movement. The "minimized human error" claim is acknowledged but not
  measured — treat as assertion, not metric.

### Claim 6: The Steamroller project — a prerequisite capacity-reclamation effort for Moonshot — used a 90-day usage window to set 100th-percentile RAM and 99th-percentile CPU limits, causing Borg to kill tasks that exceeded new memory limits even by small amounts, causing "localized service disruptions and latency"
- **Evidence**: The report describes the Steamroller methodology and its negative
  consequences with specific examples.
- **Confidence**: settled
- **Quote**: "The Steamroller team used a 90-day usage period to identify the
  100th percentile for RAM and 99th percentile for CPU. The team used this as the
  new baseline measurement for each Borg job to be applied after restarting the
  jobs but did not take into account the small spikes in RAM usage. Therefore, if
  any tasks went over their new memory limits, even by a small amount, Borg killed
  them immediately, causing localized service disruptions and latency."
- **Our assessment**: A concrete example of how a well-intentioned capacity-planning
  metric choice (90-day window, 100th-percentile RAM) caused production pain. The
  root cause is not the metric itself but the failure to account for spikes outside
  the measurement window. For the guide, this is a cautionary tale about capacity
  reclamation: the measurement/aggregation methodology matters as much as the
  limits themselves. The lesson about using absolute percentiles without headroom
  is transferable to AI/LLM capacity planning (e.g., GPU memory limits).

### Claim 7: The Steamroller project was understaffed — received only 2 of 4 requested TPMs — and management made explicit trade-offs: "delay communication of the project, limit automation effort, and reduce the scope of the project"
- **Evidence**: The report states "the Steamroller project failed to get the
  initial staffing request of at least four full-time TPMs, and only received two
  TPMs" and that this led to specific management decisions.
- **Confidence**: settled
- **Quote**: "If the project had more TPMs, they could have engaged more with
  service owners during the initial service notification, exception review
  process, and the manual effort put in to overcome the lack of robust self-service
  tools. Management recognized the shortfall in staffing at the time and made
  decisions to delay communication of the project, limit automation effort, and
  reduce the scope of the project."
- **Our assessment**: A clear causal chain: understaffing → delayed communication
  → limited automation → reduced scope. This is a pattern the guide should flag:
  understaffing infrastructure change projects cascades into communication
  failures and tooling shortfalls. The explicit management acknowledgment ("we
  know we're understaffed, so we will communicate later, automate less, and do
  less") is unusually candid for a post-hoc case study.

### Claim 8: The forced-mandate approach of Moonshot created resentment — engineers felt "they had no choice" — and a better approach would have been to "collaborate closely with the teams supporting complex services and allow smaller teams more time in the background to migrate"
- **Evidence**: The report quotes engineers' reactions: "Some resented the
  'mandate from above,' feeling that they 'had no choice.'" Sabrina Farmer
  (VP of Engineering) noted the project "achieved several other very important
  but unstated goals."
- **Confidence**: settled
- **Quote**: "People felt they had no choice with this declared mandate. The team
  asked service owners to 'swap out a known and tested storage system for one that
  was incomplete and had a comparatively low number of "road miles."' Rather than
  forcing all teams to migrate by a target deadline, it would have been better to
  collaborate closely with the teams supporting complex services and allow smaller
  teams more time in the background to migrate."
- **Our assessment**: A documented negative outcome of the top-down mandate
  approach. Sabrina Farmer's observation — that focusing only on "missed"
  advertised goals causes us to miss other benefits — is a useful framing device.
  For the guide, this supports a phased, collaborative approach to infrastructure
  change over a hard-deadline mandate, especially for complex services. The "road
  miles" quote captures the trust gap between a proven old system and an unproven
  new one.

### Claim 9: The Moonshot core team was initially composed of 20%-time volunteers, which added complexity due to distributed time zones and competing priorities — management eventually recognized this and pulled them to 100%
- **Evidence**: The report describes the team composition and the eventual shift
  to full-time dedication.
- **Confidence**: settled
- **Quote**: "The migration team consisted of a handful of SREs, SWEs, PMs, and
  TPMs from various teams, who volunteered to work 20% of their time to make the
  migration happen. Such a distributed team meant they had both broad and deep
  levels of domain knowledge... However, the fact that they were 20%ers and based
  in different offices in varying time zones added more complexity to the project."
- **Our assessment**: A concrete staffing lesson: 20%-time allocations are
  insufficient for migration projects of this scale. The report's recommendation
  — "it would have helped to have had a core migration team from the start" — is
  directly actionable. The "Develop for the team you have, not the one you're
  promised" quote (from an engineer on Steamroller, Claim 6) captures the
  pragmatic response to understaffing.

### Claim 10: The Diskless migration (2012–2018) was motivated by six factors including that 25–30% of production task deaths were attributable to disk failure and that disk performance grew slower than CPU/SSD/network
- **Evidence**: The report lists six specific motivations with quantitative
  backing for at least one (disk-attributable task deaths).
- **Confidence**: settled
- **Quote**: "25%–30% of production task deaths were attributable to disk
  failure."
- **Our assessment**: The 25–30% figure is a striking quantitative motivation for
  removing local disk. For the guide, this is a concrete example of using
  production data (task death attribution) to justify a multi-year infrastructure
  change. The six motivations span performance, reliability, TCO, and
  operational simplicity — a model for how to frame an infrastructure-change
  business case.

### Claim 11: The Diskless team suffered from a "fan-in" support crisis — 4 core team members fielding "multiple user support questions a day (sometimes dozens)" — that was "not sustainable" because support scaled linearly with users and "you can't just spin up team members like VMs"
- **Evidence**: Direct quote from a Diskless team member describing the
  unsustainable support load.
- **Confidence**: settled
- **Quote**: "[over the next year] we were getting multiple user support questions
  a day for migration (sometimes dozens). The fan-in situation wasn't sustainable.
  Because everyone waited until a few specific quarters to migrate, [the rush
  arrived] and when that rush comes, you can't just spin up team members like
  VMs."
- **Our assessment**: A candid account of support scalability failure. The root
  cause was that all users deferred migration until the last feasible window,
  creating a demand spike that the small core team could not handle. For the
  guide, this illustrates why phased migration with capacity for support is
  essential — and why "you can't just spin up team members like VMs" is a
  memorable warning against understaffing the support side of migrations. This
  directly corroborates the linear-scaling-failure principle (anything that
  scales headcount linearly with service size will fail) from
  discussion-google-sre-ben-treynor-interview (Claim 12).

### Claim 12: Most Diskless migration tooling, docs, and dashboards were built in 2016 — only after the program "ran into trouble" — by which time the timeline was "getting too protracted" and core teams were "burning out"
- **Evidence**: The report explicitly states tooling was built reactively, after
  the crisis had begun.
- **Confidence**: settled
- **Quote**: "Once built, the tooling and processes worked well. Unfortunately,
  tooling, docs, and dashboards were built mostly in 2016, only after the program
  ran into trouble. By then, the timeline was getting too protracted, and core
  engineering teams were burning out."
- **Our assessment**: A clear failure pattern: tooling built reactively rather
  than proactively. The "once built, they worked well" qualifier shows the tools
  themselves were effective — the failure was timing, not quality. For the guide,
  this supports investing in migration tooling *before* the migration wave hits,
  not after. This is a concrete instance of the "automate as much manual process
  as possible" preflight checklist item (Claim 17), but shows what happens when
  that principle is violated.

### Claim 13: The core Diskless team "did not thoroughly collect requirements on some critical user journeys (such as debug logging)," resulting in a solution "with different features and behaviors than those of the local disk" — some changes were wins, others led to "regressions and new challenges for SREs operating and debugging the services"
- **Evidence**: The report describes the RDLs issue: logs were garbage-collected
  as soon as a job completed, so users missed logs if not timed well. The
  engineering effort and ongoing cost was not "deeply considered or accounted for
  during initial design decisions."
- **Confidence**: settled
- **Quote**: "The core Diskless team did not thoroughly collect requirements on
  some critical user journeys (such as debug logging), which resulted in a
  solution with different features and behaviors than those of the local disk.
  Some of these—easy task searching and filtering, new debugging, and analysis
  capabilities that were not previously possible—were wins but others led to
  regressions and new challenges for SREs operating and debugging the services."
- **Our assessment**: A classic requirements-gathering failure with mixed outcomes
  (some wins, some regressions). The root cause is that the team assumed the
  replacement would naturally cover all use cases without specifically tracing
  each critical user journey. For the guide, this directly supports the preflight
  checklist item "Understand your customer requirements" (Claim 17, item 4) and
  provides a concrete case study of the consequences of skipping that step. The
  RDLs cost-not-considered failure is a particularly clear warning about
  cost/benefit analysis for replacement features.

### Claim 14: Google's engineering culture — where every engineer "regardless of their position" has "local incentives and a strong sense of shared values" — made top-down project management "extremely difficult" unless the change was "universally urgent"
- **Evidence**: The report describes the cultural resistance to the Diskless
  hard-deadline approach directly.
- **Confidence**: settled
- **Quote**: "Google's culture empowered every engineer, regardless of their
  position, to have local incentives and a strong sense of shared values in
  engineering. This made managing a project from the top down (unless it was
  universally urgent) extremely difficult. People resisted supporting the change
  because top-down project management was not Google culture."
- **Our assessment**: An important cultural observation that conditions how
  infrastructure change management must be done at organizations with
  empowered/autonomous engineering cultures. The finding that hard deadlines only
  worked when the urgency was universally accepted (the "deadline was deadly
  serious") explains why the aggressive mandate approach of Moonshot and Diskless
  encountered resistance. For the guide, this suggests that infrastructure change
  in AI/LLM teams — which often have similar autonomy — requires bottom-up buy-in,
  not just top-down mandate.

### Claim 15: The 10-item Preflight Checklist is a synthesized pattern from both case studies providing guidelines for large-scale infrastructure change
- **Evidence**: The report presents the checklist as the concluding artifact
  drawn from both migrations. Each item is supported by specific lessons from
  the case studies.
- **Confidence**: settled
- **Quote**: "The lessons learned here are specific to each of the case studies
  examined, but may be modified to fit your individual needs. We've also listed
  10 general guidelines to keep in mind when implementing a large-scale
  infrastructure change at your organization."
- **Our assessment**: The preflight checklist is the single highest-value artifact
  in this source for the guide. It synthesizes the lessons from both case studies
  into actionable guidelines. Each item maps to specific failures or successes
  documented in the case studies. For the guide's AI/LLM infrastructure
  operations chapters, this checklist can be adapted as a pre-migration review
  template for any large AI infrastructure change (e.g., model deployment
  migration, training cluster reconfiguration, inference infrastructure swap).
  See Concrete Artifacts for the full checklist.

## Concrete Artifacts

### 10-Item Preflight Checklist (verbatim from the report, Chapter 4)

```
1.  Establish a core team (if it doesn't yet exist) to manage the
    infrastructure change in the company
    Staff the effort with the right people from the beginning to ensure
    projects smoothly launch and land. At a minimum, there should be
    full-time engineers (to build code for the migration tools and assist with
    answering questions), technical project managers (who facilitate
    communication, tracking, and meeting deadlines), and an executive sponsor
    (who helps push this change at the top, to ensure it gets prioritized).

2.  Pilot with the more technically savvy, low-risk customers first
    These customers are more aware of what features they need and can provide
    useful feedback to improve the migration before a large rollout. In
    addition, try to select the customers that are considered to be low risk
    (i.e., unexpected issues would not stop operations for them).

3.  Understand trade-offs up front as much as possible
    While establishing a core team is critical, it's not always possible to
    have dedicated people working on the migration project or, perhaps, the
    program complexity was not well understood at the outset. Clarify at the
    start the lost opportunity costs in the project, such as delivery delays,
    low quality project communication, or unmanaged migration risks for
    critical services. By doing such clarification up front, the team can
    identify and proactively accept the risks brought in due to these
    constraints.

4.  Understand your customer requirements
    Before the change project starts, gather user requirements to see what
    specifically they want in a system and for what purpose. Even if their use
    cases will not be built in the same way in the new system, it helps to
    ensure you're building the right tools for the right audience, to ensure
    a smooth migration.

5.  Publish your plan of record
    A plan of record confirms the project plan and key decisions, as agreed on
    by the project stakeholders. This includes, at a minimum, a glossary of
    key vocabulary, project goals, project timeline, and key milestones, with
    assigned owners.

6.  Push the migration out in phases
    The migration itself is a disruption to service operations. Even with a
    plan in place, significant risks still exist. Staging the migration in
    phases relevant to the scale of your organization is an effective way of
    implementing the change. As issues emerge during earlier phases, you have
    time to update tools, techniques, and processes before the risks impact
    more services in later phases.

7.  Automate as much of the manual, repeatable process as possible
    Depending on how large the infrastructure change is and how many people it
    affects, automating relevant processes saves time for engineers, so they
    can focus on more complex issues, and avoids burdening users with manual
    and toilsome work.

8.  Test early and often
    Having a testing environment setup for users, to test whether their
    service functions on the new infrastructure, is critical for uncovering
    and mitigating technical risks. Testing should simulate, as closely as
    possible, the behavior that the production environment offers, when
    services are migrated.

9.  Communicate early and often
    For a large-scale infrastructure change, issues may crop up at any time.
    Those leading the implementation of the change must continually
    communicate early and often about this change and through the right
    channels.

10. Create appropriate escalation and exception procedures
    It's not uncommon for a service to need an exception or extension to a
    large-scale infrastructure project. This occurs because a change may not
    have the features a team needs, because there are conflicting and
    committed project deadlines, or for other valid reasons.
```

### Moonshot (GFS→Colossus) custom tools catalog (from Chapter 2)

```
1. Quota and storage usage dashboard
   Custom-built dashboard identifying how much quota each team historically
   used, showing trending resource usage across machines, teams, and PAs.
   Became a widely accessed, supported tool for viewing resource utilization
   across the machine fleet.

2. Quota move service
   Custom-built service to periodically free up quota from a source cell to a
   minimum threshold and add freed quota to the destination cell. Enabled
   automatic, fine-grained moves of quota from GFS to D (Colossus-backed
   storage).

3. Migration planning and scheduling tool
   Custom-built tool providing a free quota loan on migration, creating a
   scheduled migration window at a time least disruptive to the service.
   Analyzed file directory structure, determined data chunking, generated
   namespace mapping files, and generated bulk data migration commands.

4. Migration tracking tool
   Custom-built frontend webserver to keep track of all GFS to D migrations,
   create/update migrations for users, and identify available datacenter
   capacity for migration needs. Used for execution, monitoring, and
   stakeholder communication.

5. Bulk data migration service
   Internally built service for bulk copying files from GFS/Colossus to
   another destination in production. Still used as of the report date for
   data copies of arbitrary sizes.
```

### GFS architectural limitations (from Chapter 2)

```
1. Google production clusters held more than just thousands of machines.
2. User-facing systems (Gmail) used GFS as backend — minute-long failures
   caused unacceptable outages.
3. Chunk locations stored in RAM, limited by physical memory per machine.
4. No persistent index of chunk locations — GFS Master restart took 10–30
   minutes to recompute the full chunk-location map.
5. GFS Master ran on a single machine as a single process (shadow masters
   were read-only).
6. GFS Master software was partially single-threaded and couldn't fully
   use SMP hardware.
```

### Diskless migration motivations (from Chapter 3)

```
1. Spinning disk performance grew slower than CPU, SSD, or networking.
2. Network-attached storage enabled compute migration across machines
   without losing storage and accelerated physical maintenance.
3. Separating compute and storage improved tail latency ("best of three"
   parallel reads).
4. Independent provisioning of compute and storage on different cycles
   improved TCO and scalability.
5. 25–30% of production task deaths were attributable to disk failure.
6. Removing local disk simplified provisioning and configuration.
```

### Steamroller project — staffing and communication failures (from Chapter 2)

```
Staffing shortfall: 4 TPMs requested, 2 received.
Consequences of understaffing:
  - Delayed communication of the project to affected teams
  - Limited automation effort
  - Reduced project scope
Metric methodology failure:
  - 90-day usage window for baselines
  - 100th-percentile RAM (no headroom for spikes)
  - 99th-percentile CPU
  - Result: Borg killed tasks exceeding new limits → localized disruptions
Communication failure:
  - "engineers felt that they received notice of the upcoming change too
    late, and had limited information apart from the email"
  - Aggressive timeline caused by overly optimistic initial schedule
```

### Diskless — unsustainable fan-in support pattern (from Chapter 3)

```
Team: 4 core members
Support load: "multiple user support questions a day (sometimes dozens)"
Root cause: all users deferred migration to last feasible quarters
Outcome: team burnout, unsustainable support model
Key quote: "you can't just spin up team members like VMs"
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` (Claims 1-2): Treynor's
    thesis that most production problems come from change, and that
    Sisyphus/annealing are Google's safe-change-management systems. This source
    provides the *post-hoc case-study evidence* for the same claim — two concrete
    large-scale changes at Google, documenting what worked and what didn't.
    Treynor's false-negative/false-positive framing (Claim 2) is visible in the
    Steamroller project's metric choice failure (100th-percentile RAM without
    headroom = false positives from legitimate spikes).
  - `docs-google-sre-prodcast-04-04-zelesko-future-sre.md` (Claim 3): Zelesko's
    "safe change management" as one of four production principles. This source
    documents the concrete practice of safe change management through the ICM
    program, Moonshot, and Diskless — principle → practice evidence chain.
  - `discussion-google-sre-ben-treynor-interview.md` (Claim 12): The
    linear-scaling-failure principle ("anything that scales headcount linearly
    with the size of the service will fail"). The Diskless fan-in support crisis
    (Claim 11 in this note) is a direct instance: support load scaled linearly
    with number of migrating users, and the 4-person core team couldn't scale to
    match it.

- **Contradicts**: None identified. This source is a post-hoc practitioner case
  study that complements the conceptual/principle-level discussions in existing
  Google SRE source notes. No claim in this source opposes any claim in the
  existing notes. The forced-mandate failures documented here (Moonshot
  resentment, Diskless cultural resistance) might appear to contradict the
  "mandate from above" effectiveness claim in the Steamroller example, but this
  is an internal tension within the source (top-down mandates were necessary for
  Steamroller's prerequisites but caused resentment for Moonshot's migration) —
  this is a conditioning variable (mandates work for resource-reclamation but not
  for migration work), not a contradiction requiring a filing.

- **Extends**:
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` (Claims 1-2): Extends
    Treynor's *conceptual* safe-change-management framing with *concrete*
    case-study evidence of two large-scale changes, showing how the principles
    (and their absence) played out in practice. The preflight checklist (Claim 15)
    is an operationalization of Treynor's "safe change management" thesis into
    actionable guidelines.
  - `discussion-google-sre-ben-treynor-interview.md` (Claim 5, PRR): Extends the
    Production Readiness Review concept with a post-hoc analysis pattern: the
    preflight checklist and lessons-learned process here can be seen as PRRs
    applied *during* a migration, not just before taking on a new service.
  - `docs-google-sre-prodcast-04-04-zelesko-future-sre.md` (Claim 10, design-doc
    AI review): Extends Zelesko's earlier-cycle risk-assessment theme by providing
    specific checkpoints where risk management failed in real migrations (lack of
    customer requirements gathering, steamroller metric methodology, delayed
    tooling builds).

- **Novel**: Material new to the corpus:
  - The **ICM program** as a named organizational structure with a four-phase
    lifecycle (Claim 1) — no existing note documents a dedicated infrastructure
    change management function.
  - The **five custom Moonshot tools** catalog (Claim 5) — a concrete, named
    tooling pattern for large-scale migrations.
  - The **Steamroller project** as a case study in capacity-reclamation methodology
    failure (Claim 6) — including the specific metric-choice error (100th-percentile
    RAM, 90-day window).
  - The **explicit staff-to-consequences chain** (Claim 7) — management
    acknowledging that understaffing caused delayed communication, limited
    automation, and reduced scope.
  - **Diskless fan-in support crisis** (Claim 11) with the "you can't just spin
    up team members like VMs" quote.
  - **Google's cultural resistance to top-down project management** (Claim 14) —
    a documented organizational constraint.
  - The **10-item Preflight Checklist** (Claim 15) — a complete, reusable artifact
    for pre-migration planning.
  - **Quantified motivations** for infrastructure change (25–30% task deaths from
    disk failure, Claim 10; six GFS limitations, Claim 4).

## Guide Impact

- **Chapter 02 (Automation & Toil / Change management)**: Add the Preflight
  Checklist (Claim 15) as the canonical template for planning large AI/LLM
  infrastructure changes (model deployment migration, training cluster
  reconfiguration, inference infrastructure swap). Each checklist item maps to
  specific failures from the case studies. Pair it with Treynor's safe-change-management
  conceptual framing (Sisyphus/annealing from `docs-google-sre-prodcast-03-03-treynor-ai-ml.md`)
  so the chapter presents both the *principle* and the *practice* of safe change
  management. Use the Moonshot custom-tools catalog (Claim 5) as an example of
  what dedicated migration tooling looks like at scale — recommend that any
  AI-infrastructure migration invest in equivalent tooling (usage dashboards,
  automated quota/limit management, scheduling, tracking, bulk operations).

- **Chapter 02 (Capacity planning for AI/LLM)**: Use the Steamroller metric-choice
  failure (Claim 6 — 100th-percentile RAM, 90-day window, no headroom for spikes)
  as a cautionary tale for GPU/RAM capacity planning in AI training and inference
  clusters. The specific error — using absolute percentiles without accounting for
  workload spikes and causing production disruption — is directly transferable.
  Recommend that capacity limits for AI workloads include headroom for gradient
  checkpointing, batch-size variation, and memory fragmentation spikes.

- **Chapter 04 (Incident response) / Chapter 02 (Change management)**: Use the
  Diskless fan-in support crisis (Claim 11) and the staffing-to-consequences chain
  (Claim 7) to argue that migration support capacity must be provisioned for peak
  demand, not average demand. The "you can't just spin up team members like VMs"
  quote is a memorable warning for managers planning AI-infrastructure migrations.
  The pattern — deferred migration creates a demand spike that overwhelms a fixed
  support team — applies directly to model-upgrade rollouts across large fleets.

- **Chapter — Organizational design / adoption**: Use the Google cultural
  resistance finding (Claim 14 — empowered engineers resist top-down project
  management unless the urgency is universally accepted) to condition how the
  guide recommends infrastructure change governance for AI/LLM teams. Hard
  deadlines and mandates are less effective in autonomous engineering cultures;
  phased, collaborative approaches with bottom-up buy-in (as recommended in the
  Preflight Checklist items 2, 6, 9) are more likely to succeed.

- **Chapter — Service reliability fundamentals**: Use GFS's six architectural
  limitations (Claim 4, Concrete Artifacts) as a real example of how
  single-master bottlenecks, lack of persistent state, and single-threaded
  architecture create failure modes that drive infrastructure change. The
  10–30 minute GFS Master restart time is a concrete SLO violation scenario. For
  AI/LLM systems, this argues for avoiding analogous single-point-of-failure
  architectures in AI infrastructure (single inference-api endpoint, single
  embedding service, single vector-store indexer).

- **Chapter — Pre-migration planning**: Extract the Preflight Checklist (Concrete
  Artifacts) as a complete, ready-to-adapt artifact for the guide. Each item
  should be annotated with the specific case-study evidence that supports it
  (e.g., item 4 "Understand your customer requirements" → Diskless RDLs failure
  in Claim 13; item 7 "Automate manual process" → Moonshot tooling success in
  Claim 5 vs Diskless late-tooling failure in Claim 12; item 9 "Communicate early
  and often" → Steamroller communication failure in Claim 6-7).

## Extraction Notes

- The source is a 40-page O'Reilly PDF (Copyright 2019, First Edition published
  2019-10-23), downloaded from sre.google/static/pdf/CaseStudiesInfrastructureChangeManagement.pdf.
  The sre.google landing page at the issue URL is a brief summary page with a
  download link — the PDF is the substantive source. The full PDF text was
  extracted via PyMuPDF and read end-to-end (all 40 pages, including frontmatter
  and acknowledgments).

- Quotes were copied character-for-character from the extracted PDF text. The
  Assayer should verify key quotes against the PDF (available for free download at
  the source URL). Due to PDF text-extraction artifacts (line-break hyphens,
  spacing), a small number of character-level deviations may occur — the Assayer
  is asked to flag any discrepancies found.

- The PDF contains no code examples, terminal transcripts, or workflow diagrams
  beyond the simple lifecycle diagram described in the text. The "Concrete
  Artifacts" section synthesizes the checklists, tool catalogs, and limitation
  lists that appear as bulleted/ordered lists in the PDF.

- Confidence is `settled` overall: this is a published, peer-reviewed O'Reilly
  report on official Google SRE documentation, documenting real completed
  projects with specific names, dates, metrics, and quotes. The claims are
  post-hoc descriptions of what happened, not aspirational or predictive.
  Individual claims marked with "asserted, not measured" caveats are noted per-claim
  where metrics are absent, but the factual accuracy of the case-study
  descriptions is not in question.

- No contradiction was identified with any existing source note. The forced-mandate
  tension within the source (Steamroller required top-down mandates for resource
  reclamation; Moonshot's forced migration caused resentment) is a conditioning
  variable — not a contradiction — and is documented internally in the note.

- The report explicitly cross-references the SRE Book and SRE Workbook; these are
  already referenced by existing source notes in the corpus (e.g.,
  discussion-google-sre-ben-treynor-interview.md).
