---
source_url: https://sre.google/workbook/engagement-model
source_type: documentation
title: "Google SRE: SRE Engagement Model — SRE Workbook Chapter 18"
author: "Michael Wildpaner, Gráinne Sheerin, Daniel Rogers, and Surya Prashanth Sanagavarapu (New York Times), with Adrian Hilton and Shylaja Nukala"
date_published: 2018
date_extracted: 2026-08-09
last_checked: 2026-08-09
status: current
confidence_overall: settled
issue: "#835"
---

# Google SRE: SRE Engagement Model — SRE Workbook Chapter 18

> The canonical written statement of how an SRE team allocates scarce
> reliability capacity across a large production landscape and structures
> engagement with developer/product teams: the 7-phase service-lifecycle
> engagement model (Architecture/Design → Active Development → Limited
> Availability → GA → Deprecation → Abandoned → Unsupported) with the
> concrete SRE action at each phase (early engagement, productionalization,
> SLO-before-GA, shared operational work, developer permanently in the GA
> on-call rotation); the relationship-setting tactics ("we will support you
> in releasing as quickly as is safe" = within error budget, joint
> SRE+product-leadership meetings, quarterly state-of-production talks); the
> New York Times shared-goals engagement model (full-time embed vs brief
> constrained projects, jointly-written milestone goals, kickoff/planning/
> sprint/retro cadence, point-in-time maturity assessments); scaling
> structure (SRE-to-developer ratio < 10%, group by technology not PA
> reporting); and when/how to end an engagement (Ares and Data Analysis
> Pipeline case studies). This is the authoritative baseline the corpus's
> engagement-prioritization podcast claims reference.

## Source Context

- **Type**: documentation — SRE Workbook (O'Reilly, 2018) Chapter 18 "SRE
  Engagement Model," published at `sre.google/workbook/engagement-model/`. The
  chapter builds on SRE Book Chapter 32 ("Evolving the SRE Engagement Model,"
  linked from this page), which covers Production Readiness Reviews, early
  engagement, and continuous improvement at a technical level; this workbook
  chapter adds the organizational/relationship layer.
- **Author credibility**: Highest available. Four named Google SRE authors
  (Michael Wildpaner, Gráinne Sheerin, Daniel Rogers, Surya Prashanth
  Sanagavarapu) with Adrian Hilton and Shylaja Nukala. Sanagavarapu is the
  primary author of the New York Times shared-goals section and describes the
  NYT SRE team's actual practice first-hand; the Ares and Data Analysis
  Pipeline case studies are first-party accounts of Google SRE engagements
  the authors ran. Edited by Betsy Beyer et al. and published on the official
  sre.google domain.
- **Scope**: Covers (a) the 7-phase service-lifecycle engagement model with
  the recommended SRE action at each phase; (b) relationship setup —
  communicating priorities, identifying risks, aligning dev/SRE incentives,
  the NYT shared-goals model (engagement types, shared goals, sprints/
  communication, impact measurement); (c) setting ground rules (Google SRE's
  two major goals, cooperation principles); (d) planning and executing
  (roadmaps); (e) sustaining the relationship (regular meetings, service
  reviews, reassessing slipping ground rules, error-budget-driven
  prioritization, handling mistakes); (f) scaling SRE (single-team scaling,
  multi-team structure, adaptation, distributed teams); (g) ending the
  relationship (two case studies: Ares and a data analysis pipeline). Does NOT
  cover LLM/agent-specific workloads directly — the engagement framework is
  general SRE org design that the guide maps onto AI/LLM reliability teams.

## Extracted Claims

### Claim 1: Given a large production landscape, an SRE team cannot cover every service and must decide where to focus its attention to achieve the best results; the microservices movement makes this scarcity acute
- **Evidence**: Chapter intro states the two-fold SRE goal (velocity + reliability),
  the limit on what an SRE team can accomplish, and that "a small company can
  easily have more microservices than a single SRE team can handle." Product
  development and SRE teams are to collaborate on the focus decision.
- **Confidence**: settled
- **Quote**: "Given a large production landscape, and with the knowledge that they can't cover every service, an SRE team must decide where to focus their attention to achieve the best results."
- **Our assessment**: This is the framing claim that makes the rest of the
  chapter's machinery (lifecycle phases, prioritization tactics) necessary. It
  is the written-state baseline for the corpus's practitioner
  engagement-prioritization claims (Zelesko's "engagements chosen for maximum
  impact," Damion Yates's two-axis ranking). Fully canonical; we buy it as
  settled. The microservices-scarcity point transfers directly to LLM
  reliability teams facing hundreds of agentic services.

### Claim 2: The SRE model is less effective when the domain is too large and overly complex, so engagement focus must be actively managed rather than assumed
- **Evidence**: Chapter intro: "But there's a limit to how much even the best SRE
  team can accomplish, and the SRE model is less effective when the domain is
  too large and overly complex."
- **Confidence**: settled
- **Quote**: "But there's a limit to how much even the best SRE team can accomplish, and the SRE model is less effective when the domain is too large and overly complex."
- **Our assessment**: A candid limit on the SRE model itself — relevant to the
  guide's Ch00 framing of when SRE-style engagement applies vs when it breaks
  down. For AI/LLM platforms, this argues for explicit engagement-selection
  rather than attempting uniform coverage of every agent/service.

### Claim 3: During Phase 1 (Architecture and Design), SRE can influence design five ways (best practices, infrastructure dos/don'ts, early-engagement consulting, joining the dev team, codesigning) because fixing architectural mistakes becomes more difficult later in the development cycle
- **Evidence**: The Phase 1 section enumerates the five mechanisms and states
  the cost-of-late-fix rationale.
- **Confidence**: settled
- **Quote**: "Fixing architectural mistakes becomes more difficult later in the development cycle. Early SRE engagement can help avoid costly redesigns that become necessary when systems interact with real-world users and need to scale in response to service growth."
- **Our assessment**: The canonical shift-left rationale for SRE engagement,
  stated with a concrete cost mechanism (costly redesigns under real-world
  scale). This is the positive statement of what the corpus's ~10%
  SRE-engaged-from-start gap (retail-gaming note) shows is frequently missed.
  Maps to LLM services: engage reliability at agent architecture/design, not
  after the inference stack is frozen.

### Claim 4: During Phase 2 (Active Development), SRE productionalizes the service — capacity planning, redundancy, spike/overload handling, load balancing, and sustainable operational practices (monitoring, alerting, performance tuning)
- **Evidence**: Phase 2 section enumerates the productionalization work items.
- **Confidence**: settled
- **Quote**: "Productionalization typically includes capacity planning, setting up extra resources for redundancy, planning for spike and overload handling, implementing load balancing, and putting in place sustainable operational practices like monitoring, alerting, and performance tuning."
- **Our assessment**: A concrete, itemized list of what "getting a service in
  shape to be released into production" means — directly usable as a checklist
  for AI/LLM service productionization (capacity = GPU/inference capacity,
  redundancy = replica/multi-region, spike handling = token-load surges).
  Settled as canonical SRE practice.

### Claim 5: SRE strongly recommends defining SLOs before General Availability so service teams have an objective reliability measure, with the product team retaining the option to withdraw a product that can't meet target reliability
- **Evidence**: Phase 3 (Limited Availability) section.
- **Confidence**: settled
- **Quote**: "We strongly recommend defining SLOs before general availability (GA) so that the service teams have an objective measure of how reliable the service is. The product team still has the option to withdraw a product that can't meet its target reliability."
- **Our assessment**: The SLO-before-GA recommendation is the chapter's concrete
  pre-GA gate. Note the conditioning: this is about a service heading to GA in a
  mature org, not the "don't start with SLOs" immature-org advice from the
  Life-Beyond-Google note — complementary, not contradictory (see
  Cross-References). For LLM services, this supports setting availability,
  quality, and cost SLOs before a model/agent reaches GA.

### Claim 6: During Phase 3 (Limited Availability), operational and incident work should be shared between developer and SRE teams so the developer team gains operational experience with the service before GA
- **Evidence**: Phase 3 section: because usage is still changing, incident/
  operational load is higher while teams learn the service's failure modes;
  sharing the work gives devs operational experience that informs pre-GA
  changes.
- **Confidence**: settled
- **Quote**: "We recommend sharing this work between the developer and SRE teams. That way, the developer team gains operational experience with the service and the SREs gain experience with the service in general."
- **Our assessment**: The shared-operational-work pattern is the pre-GA analogue
  of the corpus's co-on-call guidance (on-call-rotations note) — devs learn the
  failure modes before they own the service. High value for the guide's
  dev/SRE boundary material (Ch00 "break the dev/SRE wall early").

### Claim 7: During Phase 4 (GA), the developer team should continue to field a small part of all operational and incident work so it doesn't lose perspective, and might permanently include one developer in the on-call rotation
- **Evidence**: Phase 4 section: while SRE typically performs the majority of
  operational work at GA, devs keep a small share; the permanent developer in
  the rotation "helps the developers keep track of operational load."
- **Confidence**: settled
- **Quote**: "the developer team should continue to field a small part of all operational and incident response work so they don't lose perspective on these aspects of the service. They might permanently include one developer in the on-call rotation to help the developers keep track of operational load."
- **Our assessment**: This is the strongest written statement in the corpus of
  the "keep developers in a small share of on-call/incident work" doctrine. It
  corroborates APW's co-on-call argument (on-call-rotations Claim 2) from the
  Workbook side and directly answers Ch04's dev/SRE on-call-sharing question.
  Settled.

### Claim 8: The incentives-alignment mechanism is the explicit pledge "We will support you in releasing as quickly as is safe" — where "safe" generally means staying within error budget — balanced by the developer team's commitment of a reasonable percentage of engineering time to reliability work
- **Evidence**: The "Aligning Goals" section: SRE favors long-term service
  viability while devs favor launch velocity; the pledge and the countervailing
  developer commitment (fixing/preventing reliability breakage, paying down
  technical debt, including SREs in feature design early) strike the balance.
- **Confidence**: settled
- **Quote**: "SREs can have an explicit goal to support the developer team's release velocity and ensure the success of all approved launches. For example, SRE might state, 'We will support you in releasing as quickly as is safe,' where 'safe' generally implies staying within error budget."
- **Our assessment**: The canonical "as quickly as is safe" framing — it
  operationalizes the velocity/reliability trade-off as an explicit joint
  pledge with the error budget as the safety definition. This connects to the
  sibling error-budget-policy appendix (#836) and to the corpus's
  SLO/error-budget-as-signal material. The paired developer commitment
  (dedicate engineering time to reliability) is the symmetric obligation the
  guide should carry.

### Claim 9: The New York Times shared-goals model offers two engagement types — a full-time embed of an SRE in a product development team, or part-time engagement on fairly brief and constrained projects — chosen based on SRE bandwidth
- **Evidence**: Sanagavarapu's NYT section: SRE resources are in high demand
  (cloud migrations, production ramp-ups, containerization), so engagement type
  is defined by SRE team bandwidth; long-term engagements prioritize
  applications that fit company strategy.
- **Confidence**: settled
- **Quote**: "For full-time engagements, we prefer to embed an SRE in a product development team. This helps provide focus and time to relieve some burden from the product engineering teams."
- **Our assessment**: A named, replicable engagement menu (embed vs brief
  constrained project) with an explicit selection criterion (bandwidth +
  company strategy). This is the organizational pattern an AI/LLM reliability
  team can adopt for engaging product teams. Settled as a first-party
  description of NYT practice.

### Claim 10: NYT shared-goal principles: application owners (not SREs) are directly responsible for application changes; new automation/tooling must benefit the whole company (no one-off scripts); SREs are not traditional operations engineers and do not do manual support work
- **Evidence**: The "Setting Shared Goals and Expectations" bullet list; the
  third principle is the "shared goals" thesis — application owners stay
  accountable; SRE engagement is for company-wide benefit; ARR/PRR change
  proposals are prioritized jointly by developers and SREs.
- **Confidence**: settled
- **Quote**: "We emphasize that the application owners, not SREs, are directly responsible for making changes to an application." — and — "SREs are not traditional operations engineers. They do not support manual work such as running a job for deployment."
- **Our assessment**: Two high-value guardrails. The owner-accountability
  principle is the same mechanism that prevents the corpus's "checkbox SRE"
  anti-pattern (permanent consultants without ownership); the
  SREs-aren't-ops-engineers principle is the toil-avoidance doctrine applied
  to the engagement itself. Directly relevant to Ch04/Ch00.

### Claim 11: NYT engagements begin with a kickoff and planning meeting, define shared goals jointly with milestones (epics/stories), run development cycles and retrospectives, and require a defined feedback loop (e.g., biweekly retrospective or manager check-in) outside Agile sprint reviews
- **Evidence**: The "Sprints and Communication" section enumerates the roadmap
  (architecture review, define goals, kickoff/planning, development cycles,
  retrospectives, PRRs, launches) and requires teams to agree on a feedback
  method and frequency; teams should not shy away from planning for
  disengagement if the engagement isn't working.
- **Confidence**: settled
- **Quote**: "Any engagement with product development teams begins with a kickoff and planning meeting."
- **Our assessment**: The shared-goals cadence is a concrete, copyable
  engagement operating model (kickoff → milestones → sprints → retros →
  PRRs → launches) plus the explicit feedback-loop requirement. For the guide,
  this is the "how to structure shared ownership with product teams" recipe an
  LLM reliability team needs.

### Claim 12: The NYT measures engagement impact with a point-in-time maturity assessment (walking a maturity matrix across axes like observability, capacity planning, change management, incident response) before and after the engagement, to verify SREs are doing high-value work
- **Evidence**: The "Measuring Impact" section: NYT adopted a point-in-time
  assessment from Google's Customer Reliability Engineering (CRE) team — agree
  on scores before starting, re-assess after the engagement ends, and measure
  against a maturity model if one exists.
- **Confidence**: settled
- **Quote**: "We have found it important to measure the impact of the engagement to make sure that SREs are doing high-value work."
- **Our assessment**: A concrete, measurable engagement-ROI mechanism: score the
  partner team's maturity on SRE axes before and after, and compare. This
  generalizes beyond NYT and gives the guide an evaluation method for AI
  reliability-team engagements. Settled as described NYT practice.

### Claim 13: Every Google SRE team has two major goals — short-term (operationally stable, available, scaling service) and long-term (optimize operations until ongoing human work is no longer needed, so the team can move on to the next high-value engagement) — supported by agreed cooperation principles (hard limit on operational work, measured SLO, quarterly error budget, developer involvement in daily operations)
- **Evidence**: The "Setting Ground Rules" section states the two goals and the
  principles; it also warns that without an SLO from the beginning of the
  relationship, teams "have to backtrack to this step later."
- **Confidence**: settled
- **Quote**: "Optimize service operations to a level where ongoing human work is no longer needed, so the SRE team can move on to work on the next high-value engagement."
- **Our assessment**: The long-term goal is the engagement-level statement of the
  toil-elimination doctrine: SRE's objective is to make itself unnecessary for a
  service and redeploy. The four cooperation principles (hard limit on
  operational work, measured SLO, quarterly error budget, developer involvement
  in daily ops) are the ground rules an AI/LLM reliability team can adopt
  directly. Consistent with the 50% operational-work cap in the eliminating-toil
  note.

### Claim 14: If a service is in danger of missing its SLO or has exhausted its error budget, both teams work with high priority on tactical and strategic fixes; if a service is well within SLO with ample error budget, the spare budget should be used to increase feature velocity rather than spent on overproportional service improvements
- **Evidence**: The "Adjusting Priorities According to Your SLOs and Error
  Budget" section.
- **Confidence**: settled
- **Quote**: "If a service is well within SLO and has ample error budget left, we recommend using the spare error budget to increase feature velocity rather than spending overproportional efforts on service improvements."
- **Our assessment**: The error budget as a bidirectional prioritization lever:
  it licenses both urgency (when exhausted) and restraint (when ample). This
  directly connects to the sibling error-budget-policy appendix (#836) and the
  eliminating-toil SLO-licenses-skipping claim. For LLM services with cost
  budgets, the same logic applies to spend vs reliability work.

### Claim 15: Google generally maintains an SRE-to-developer ratio of < 10%, so one SRE team commonly works with multiple developer teams in its product area; limited SRE resources can scale to many services if the services share a single product, similar tech stacks, and the same (or few) developer teams
- **Evidence**: The "Supporting Multiple Services with a Single SRE Team"
  section states the ratio and the three characteristics that make a service
  cluster scalable with one SRE team.
- **Confidence**: settled
- **Quote**: "Google generally maintains an SRE-to-developer ratio of < 10%."
- **Our assessment**: A concrete, citable staffing ratio with the three scaling
  conditions (single product / similar stacks / same few dev teams). For AI/LLM
  platforms, this is the sizing argument for a reliability team that engages
  many agentic services without per-service embedding. Settled as Google's
  stated practice.

### Claim 16: With multiple SRE teams, organize SRE teams by technology rather than by developer PA reporting structure to prevent churn during developer reorgs; and when a team has too many services, prefer sharding the existing team over building new teams from scratch
- **Evidence**: The "Structuring a Multiple SRE Team Environment" and "Adapting
  SRE Team Structures" sections; the storage-system grouping example and the
  culture-transfer rationale for sharding.
- **Confidence**: settled
- **Quote**: "To prevent churn in SRE teams during developer reorgs, we recommend organizing SRE teams according to technology rather than developer PA reporting structure."
- **Our assessment**: Two org-design rules with direct transfer to AI platforms:
  align SRE teams to the technology stack (inference platform, training infra,
  serving) rather than to product org-charts, and shard existing teams to
  preserve culture. The shard-vs-build rationale ("transfer culture and grow
  existing leadership") is the sort of concrete mechanism the guide's
  org-design material can cite.

### Claim 17: SRE engagements aren't necessarily indefinite — consider handing a service back when it has been optimized to no longer need ongoing SRE engagement, when its importance has diminished, or when it is reaching end of life
- **Evidence**: The "Ending the Relationship" section lists the three
  hand-back conditions and notes individual SREs will move away from toil-heavy
  teams toward more interesting engineering work.
- **Confidence**: settled
- **Quote**: "If a service has been optimized to a level where ongoing SRE engagement is no longer necessary"
- **Our assessment**: The hand-back conditions give the guide an explicit exit
  criterion for SRE engagement — the positive counterpart to the "when the value
  proposition goes away" disengagement discussion. Settled as stated.

### Claim 18: Case Study 2 (Data Analysis Pipeline): when the value of an SRE relationship declines, disbanding the SRE team and giving the developer team full control over old and new system work resolved a decade-long tension — but a communication breakdown between the SRE team maintaining the old system and the dev team building the replacement was the proximate cause of the disconnect
- **Evidence**: The case study describes the pivot (resources shifted to the new
  system), the communication breakdown, and the decommission (removing the
  organizational barrier). It notes the extra operational load on the dev team
  was offset by owners having greater knowledge of service internals, and that
  with a healthier relationship SRE would have handed production work back
  temporarily and reassumed it after restabilization.
- **Confidence**: settled
- **Quote**: "Ultimately, the simplest solution was to remove the organizational barrier and give the developer team full control over prioritizing work on old and new systems."
- **Our assessment**: A nuanced ending-relationship pattern: full disbandment
  was the last resort after the SRE/dev split created an organizational
  barrier during a migration. The chapter's preferred alternative (temporary
  hand-back, then reassume) is the more actionable guidance. High value for the
  guide's migration/ownership material.

### Claim 19: The conclusion ties engagement management to reliability outcomes: "investing in aligning team goals and understanding each other's objectives is as important as defending SLOs"
- **Evidence**: Chapter conclusion: shared sense of purpose with regular and
  open communication is key; relationship management scales; aligning goals is
  as important as defending SLOs.
- **Confidence**: settled
- **Quote**: "For sustaining the long-term success of an engagement, investing in aligning team goals and understanding each other's objectives is as important as defending SLOs."
- **Our assessment**: The chapter's thesis statement — reliability outcomes
  depend on the engagement relationship, not just SLO mechanics. This is a
  useful Ch00/Ch04 principle and a natural anchor for the guide's org-design
  and shared-ownership sections.

## Concrete Artifacts

### Artifact A — The 7-phase service-lifecycle engagement model (verbatim-condensed from the chapter's "The Service Lifecycle" section)

```
Phase 1 Architecture/Design   SRE influences design: best practices (resilience
                              to single points of failure), documented infra
                              dos/don'ts, early-engagement consulting with
                              targeted prototypes, joining the dev team,
                              codesigning part of the service.
Phase 2 Active Development    Productionalization: capacity planning, extra
                              resources for redundancy, spike/overload planning,
                              load balancing, sustainable operational practices
                              (monitoring, alerting, performance tuning).
Phase 3 Limited Availability  Measure/evaluate reliability; "strongly
                              recommend defining SLOs before general availability
                              (GA)"; capacity model, resource acquisition,
                              automating turnups/resizing; SHARE operational and
                              incident work between developer and SRE teams.
Phase 4 GA                    Service passes the Production Readiness Review;
                              SRE does the majority of operational work, but the
                              developer team "should continue to field a small
                              part of all operational and incident response work"
                              and "might permanently include one developer in
                              the on-call rotation."
Phase 5 Deprecation           Closed to new users; SRE operates the existing
                              system mostly without dev involvement and supports
                              the transition; "SRE is effectively supporting two
                              full systems. Headcount and staffing should be
                              adjusted accordingly."
Phase 6 Abandoned             Developer team typically resumes operational
                              support; SRE supports incidents on a best-effort
                              basis; SRE hands over service management to
                              remaining internal users.
Phase 7 Unsupported           Service shut down; "SRE helps to delete references
                              to the service in production configurations and in
                              documentation."
```

### Artifact B — The NYT shared-goals engagement roadmap (verbatim-condensed from "Sprints and Communication")

```
1. Review the application architecture.
2. Define shared goals.
3. Hold the kickoff and planning session.
4. Implement development cycles to reach milestones.
5. Set up retrospectives to solicit engagement feedback.
6. Conduct Production Readiness Reviews.
7. Implement development cycles to reach milestones.
8. Plan and execute launches.

Feedback requirement: "We require that the teams define a feedback method and
agree on its frequency" — e.g., "setting up a biweekly retrospective or check-in
with team managers." If an engagement isn't working, "we expect teams to not shy
away from planning for disengagement."
```

### Artifact C — NYT shared-goals example (verbatim-condensed from "Setting Shared Goals and Expectations")

```
Scope example 1: "In the next quarter, I want all members of my team to handle
GKE/GAE deployments, become comfortable with production environments, and be
able to handle a production outage."
Scope example 2: "In the next quarter, I want SRE to work with the dev team to
stabilize the app in terms of scaling and monitoring, and to develop runbooks
and automation for outages."
Success story example: "After the engagement, the product development team can
handle our service outages in Google Kubernetes Engine without escalation."
```

### Artifact D — Ground rules for cooperation (verbatim-condensed from "Setting Ground Rules")

```
Google SRE team goals:
  Short term:  "Fulfill the product's business needs by providing an
               operationally stable system that is available and scales with
               demand, with an eye on maintainability."
  Long term:   "Optimize service operations to a level where ongoing human work
               is no longer needed, so the SRE team can move on to work on the
               next high-value engagement."

Agreed cooperation principles:
  - "Definitions of (and a hard limit on) operational work."
  - "An agreed-upon and measured SLO for the service that is used to prioritize
     engineering work for both the developer and SRE teams."
  - "An agreed-upon quarterly error budget that determines release velocity and
     other safety parameters, such as excess service capacity to handle
     unexpected usage growth."
  - "Developer involvement in daily operations to ensure that ongoing issues
     are visible, and that fixing their root causes is prioritized."
```

### Artifact E — SRE scaling rules (verbatim-condensed from "Scaling SRE to Larger Environments")

```
Single SRE team → many services, if services are:
  - "part of a single product" (end-to-end ownership of the user experience)
  - "built on similar tech stacks" (minimizes cognitive load, enables skill reuse)
  - "built by the same developer team or a small number of related developer
     teams" (minimizes relationships, aligns priorities)
Ratio: "Google generally maintains an SRE-to-developer ratio of < 10%."
Multi-team structure: "Group the teams within a product" OR "Group the teams
within a technology stack (e.g., 'storage' or 'networking')." Prefer
technology grouping: "organizing SRE teams according to technology rather than
developer PA reporting structure."
Adaptation: create, split (shard), merge, and dissolve SRE teams based on
service needs — "we prefer to shard the existing team into multiple teams to
transfer culture and grow existing leadership."
Distributed teams: aim for a "two-location arrangement" minimum; singleton
teams are "generally less effective and more vulnerable to the effects of
reorgs outside the team"; gather the whole team "at an org-wide summit every
12-18 months."
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-04-04-zelesko-future-sre.md` **Claim 12** (SRE
    does not support every product — "we choose engagements and we engage where
    SRE is going to have the most value and the most impact") — Zelesko's
    strategic statement is the practitioner echo of this chapter's
    where-to-focus-attention framing (Claim 1 here). The chapter is the
    canonical written baseline that Zelesko's "maximum impact" engagement
    selection refines.
  - `docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` **Claim 6**
    (two-axis SRE-engagement prioritization: leadership-declared importance ×
    the requesting team's own reliability effort) — Damion's DeepMind ranking
    operationalizes this chapter's "must decide where to focus their attention"
    (Claim 1 here) and the NYT prioritization factors (backlog reduction
    contribution; Claim 9 here). Also **Claim 13** (Damion's team supports but
    does not operate Gemini serving) is an instance of the chapter's
    engagement-scoping discipline (what SRE does/doesn't own per service).
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` **Claim 14** (~10% of
    engagements have SRE as an active party from the start) — Chernev's
    observed shift-left gap is the failure-mode counterpart of this chapter's
    Phase-1 early-engagement recommendation (Claim 3 here); the chapter
    supplies the why (costly late redesigns).
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` **Claim 1** (SRE
    on-call is selective by design — the "overwhelming majority of...
    microservices at Google do not have SRE on-call") and **Claim 2**
    (developers co-on-call so they "feel the pain of the service") — APW's
    rotation-level selectivity and co-on-call corroborate this chapter's
    selective-engagement premise (Claim 1 here) and the Phase-3/4
    shared-operational-work + developer-permanently-in-the-rotation
    recommendations (Claims 6-7 here).
  - `docs-google-sre-eliminating-toil.md` **Claim 3** (Google caps SRE teams'
    operational work at 50%) — the "Definitions of (and a hard limit on)
    operational work" ground rule (Claim 13 here, Artifact D) is the
    engagement-level restatement of the toil chapter's cap; the chapter's
    long-term goal (optimize until no ongoing human work needed) is the
    toil-elimination doctrine applied to engagement exit.
  - `docs-google-sre-reliable-product-launches.md` **Claim 1** (LCE consulting
    team for launch readiness) and **Claim 9** (document all manual processes
    before launch) — the NYT roadmap's "Plan and execute launches" step and
    the PRR-as-GA-gate (Claim 5, Artifact B here) sit inside the same
    launch-coordination doctrine; the workbook chapter supplies the
    engagement-structure layer that the LCE launch-process layer builds on.

- **Contradicts**: None identified. Specific checks against apparent tensions:
  (a) this chapter's "define SLOs before GA" (Claim 5) vs
  `docs-google-sre-prodcast-02-08-life-beyond-google.md` Claim 5 ("don't start
  a reliability program with SLOs") — a **conditioning variable**, not a
  contradiction: the chapter addresses a service heading to GA within an
  established SRE relationship, while the Xoogler panel addresses immature orgs
  lacking production hygiene/monitoring. Per MINER.md §4a, no contradiction
  issue filed; the guide should present both with their maturity context.
  (b) this chapter's full-time SRE embed model vs
  `docs-google-sre-prodcast-02-08-life-beyond-google.md` Claim 12 (the
  single-embedded-SRE-becomes-ops anti-pattern) — the NYT model (Claim 9 here)
  embeds an SRE as one member of a real SRE team, with owner-accountability
  guardrails (Claim 10 here), which is precisely the setup the anti-pattern
  note says is broken when the embedded SRE is isolated. The two sources agree
  once scope is specified; no contradiction.
  (c) this chapter's Phase-4 recommendation that developers stay in a small
  share of on-call vs any note recommending devs be fully off-hook — no such
  note exists in the corpus; the co-on-call notes agree.

- **Extends**:
  - `docs-google-sre-prodcast-04-04-zelesko-future-sre.md` — Zelesko's Claim
    12 (engagement selection for maximum impact) is stated at the strategic
    level; this chapter supplies the full operating machinery (7-phase model,
    relationship tactics, ground rules, scaling rules, exit criteria) that
    makes that selection concrete.
  - `docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` — Damion's
    two-axis prioritization (Claim 6) and researcher-time-as-metric (Claim 5)
    are the AI-lab refinements of this chapter's generic engagement model; the
    chapter is the authoritative written baseline those practitioner
    observations refine ("mine it as the authoritative baseline, not a
    replacement," per the Prospector triage).
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` — that note covers
    rotation mechanics (sizing, shapes, training); this chapter adds the
    engagement-lifecycle context that decides WHICH services get those
    rotations (Phase 3 shared work → Phase 4 dev-in-rotation), extending the
    on-call material with the engagement-timing dimension.
  - `docs-google-sre-creating-production-launch-plan.md` — the launch-plan
    report covers the PRR/launch-readiness mechanics (the NYT roadmap step 6
    and the Phase-4 GA gate); this chapter supplies the relationship-structure
    within which those PRRs are jointly prioritized ("Proposed changes from ARR
    and PRR must be prioritized jointly by the developers and the SREs").

- **Novel**: Material new to the corpus:
  - **The 7-phase service-lifecycle engagement model** (Claim 3-7, Artifact A)
    — the full phase-by-phase SRE action map (Architecture/Design → Unsupported)
    with per-phase practices; no existing note enumerates the lifecycle.
  - **The "as quickly as is safe" = within-error-budget pledge** (Claim 8) —
    the explicit incentives-alignment mechanism between dev and SRE, with the
    paired developer-engineering-time commitment.
  - **The New York Times shared-goals engagement model** (Claims 9-12,
    Artifacts B-C) — the two engagement types (full-time embed vs brief
    constrained projects), joint milestone goals, the kickoff/planning/sprint/
    retro cadence, and the point-in-time maturity-assessment ROI method.
  - **The ground-rules set** (Claim 13, Artifact D) — the two Google SRE team
    goals (short-term stable service, long-term no-ongoing-human-work) plus
    the four cooperation principles (hard operational-work limit, measured
    SLO, quarterly error budget, developer involvement in daily ops).
  - **The SRE-to-developer ratio of < 10%** and the three service-cluster
    scaling conditions (Claim 15, Artifact E).
  - **The technology-vs-PA-reporting team-structure rule and the shard-to-
    transfer-culture principle** (Claim 16).
  - **The explicit engagement hand-back / ending conditions** (Claim 17) and
    the two ending case studies — Ares (Claim 18's positive disengagement
    pattern: standing up an in-house infra team to transfer production
    knowledge) and the Data Analysis Pipeline disbandment.

## Guide Impact

- **Chapter 04 (oncall-and-toil)**: Add the engagement-lifecycle model (Claims
  3-7, Artifact A) as the framework for deciding which services get on-call/
  operational investment and when. Add the Phase-3 shared-operational-work and
  Phase-4 developer-in-on-call-rotation recommendations (Claims 6-7) to the
  on-call-sharing section — these are the canonical written statements of the
  "keep developers in a small share of on-call" doctrine the chapter needs,
  corroborating the on-call-rotations note. Add the ground rules (Claim 13,
  Artifact D) — hard limit on operational work, measured SLO, quarterly error
  budget, developer involvement in daily ops — as the engagement-level
  complement to the toil chapter's 50% cap. Add the hand-back conditions
  (Claim 17) as the exit criteria for SRE engagement on a service.

- **Chapter 00 (principles)**: Add the "we will support you in releasing as
  quickly as is safe" pledge with error-budget-as-safety (Claim 8) as the
  canonical statement of dev/SRE incentives alignment — the positive mechanism
  behind the chapter's "break the dev/SRE wall early" guidance, with the
  symmetric developer commitment (dedicate engineering time to reliability).
  Add the owner-accountability guardrail (Claim 10) — application owners, not
  SREs, are directly responsible for changes — as the remedy to the
  throw-over-the-wall anti-pattern. Add the engagement-end thesis (Claim 19):
  aligning team goals is as important as defending SLOs.

- **Chapter 02 (incident-response)**: Add the PRR-as-GA-gate (Claim 5) and the
  joint-prioritization of ARR/PRR changes (Claim 11) to the launch-readiness
  material, linking to the creating-production-launch-plan note. Add the
  error-budget-prioritization lever (Claim 14) — urgent fixes when budget is
  exhausted, feature velocity when budget is ample — as the prioritization
  rule for incident-follow-up vs feature work.

- **Chapter 05 (llm-ops-reliability)**: The primary AI-transfer target. Use
  the engagement model (Claims 1-2) to frame how an AI/LLM reliability team
  decides WHICH agentic services/agents to engage with given scarce capacity —
  the same selection problem the chapter opens with. Adopt the NYT shared-goals
  model (Claims 9-12) as the recommended structure for AI reliability teams
  engaging product/ML teams (embed vs brief constrained projects, joint
  milestone goals, kickoff/planning/sprint/retro cadence, pre/post maturity
  assessment). Adopt the scaling rules (Claims 15-16): < 10% reliability-to-
  developer ratio, group by technology stack (inference platform, training
  infra) rather than product org, shard to transfer culture. Use the Ares case
  study (Claim 18) as the pattern for disengaging cleanly from an AI service —
  stand up in-house reliability owners rather than indefinite consulting.

## Extraction Notes

- **Source read**: The chapter at `https://sre.google/workbook/engagement-model/`
  was fetched and read end-to-end via WebFetch (full chapter text, all seven
  lifecycle phases, the NYT section, ground rules, sustaining-relationship
  tactics, scaling sections, both ending case studies, and conclusion). It is a
  single self-contained page; per MINER.md §1 the linked pages (SRE Book
  Chapter 32, reliable-product-launches, enterprise-roadmap, the Waze case
  study link in organizational-change) were evaluated: they are companion
  references already covered by existing corpus notes or outside this
  chapter's extraction scope (Ch32/PRR mechanics are referenced via the
  creating-production-launch-plan and reliable-product-launches notes), so no
  sub-pages were followed.
- **Quote verification**: All quotes were copied character-for-character from
  the fetched page text; contiguous fragments only per MINER.md §2a. Note the
  Claim 8 quote uses the source's own nested single quotes inside the double-
  quoted pledge ("We will support you in releasing as quickly as is safe").
  The Claim 7 quote begins mid-sentence ("the developer team should continue
  to field...") because it follows the source's opening clause "While SRE
  typically performs the majority of operational work," which was excluded for
  brevity — the fragment is contiguous.
- **Sibling cross-link**: Sibling issue #836 covers the Workbook's Appendix B
  "Example Error Budget Policy" (`/workbook/error-budget-policy`). This chapter
  references the error budget as the definition of "safe" (Claim 8) and as a
  ground-rule item (Claim 13, Artifact D) and a prioritization lever (Claim
  14); the error-budget artifact itself is mined independently in #836. The
  two notes are cross-referential, not overlapping. #836 currently carries a
  `rejected` label; if that rejection stands, the error-budget references here
  remain valid as forward pointers to the SRE Book/Workbook canon.
- **Related-notes candidates (`miner-related-notes.md`) — dispositions**:
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response, no engagement/organization model
    content.
  - `docs-google-sre-data-processing-pipelines.md` — **Dismissed**; data
    pipeline SLO formats and pipeline reliability, unrelated to engagement
    structure.
  - `docs-google-sre-eliminating-toil.md` — **Cited** (Claim 3, operational
    work cap); see Corroborates.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` —
    **Dismissed**; incident-response tooling breadth and on-call staffing, not
    engagement models.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — **Cited** (Claim
    10, "checkbox SRE" anti-pattern) and **used** for the conditioning-variable
    check on SLOs-first (Claim 5 there); see Contradicts and Corroborates.
  - `docs-google-sre-configuration-specifics.md` — **Dismissed**;
    configuration toil and DSLs, unrelated.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**;
    AI-for-SRE tooling (tagging, golden data), not engagement structure.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
    **Dismissed**; databases and reliability culture, unrelated to the
    engagement model.
  - `docs-google-sre-reliable-product-launches.md` — **Cited** (Claims 1, 9,
    launch/LCE doctrine); see Corroborates.
  - `blog-pagerduty-sre-agent-triage.md` — **Dismissed**; LLM incident triage
    tooling, unrelated to engagement/organization models.
- **Contradiction analysis (per MINER.md §4a)**: No contradiction issue filed.
  The two apparent tensions (SLO-before-GA vs don't-start-with-SLOs;
  full-time-embed vs single-embedded-SRE anti-pattern) were evaluated and are
  conditioning-variable differences, documented under Contradicts. No existing
  `contradiction`-labeled issue or CONTRADICTIONS.md entry is affected.
- `date_published` is 2018 (SRE Workbook publication year); the page on
  sre.google carries no separate per-chapter date. `confidence_overall` is
  `settled`: the source is canonical first-party Google SRE / NYT SRE
  documentation describing the authors' own established practice, with two
  first-party case studies. All claims are descriptive of documented practice,
  not speculative.
