---
source_url: https://sre.google/workbook/team-lifecycles
source_type: documentation
title: "Google SRE: SRE Team Lifecycles — SRE Workbook Chapter 20"
author: "David Ferguson and Prashant Labhane, with Shylaja Nukala (Google); 'Transforming an Existing Team into an SRE Team' by Brian Balser (New York Times)"
date_published: 2018
date_extracted: 2026-08-13
last_checked: 2026-08-13
status: current
confidence_overall: settled
issue: "#907"
---

# Google SRE: SRE Team Lifecycles — SRE Workbook Chapter 20

> The canonical roadmap for building and scaling an SRE organization — from
> SRE practices without any SREs (Principle #1: SLOs with consequences), to
> hiring and placing the first SRE (five interview skill areas, three embedding
> options), to forming the first team through Tuckman's forming/storming/
> norming/performing stages with per-formation risk tables, to scaling to many
> teams (service-complexity splits, geographic splits, and Google's running-
> many-teams programs). This is the org-design substrate the guide's on-call,
> toil, and engagement playbooks assume, and it transfers directly to standing
> up AI/LLM reliability teams.

## Source Context

- **Type**: documentation — SRE Workbook (O'Reilly, 2018) Chapter 20 "SRE Team
  Lifecycles," published at `sre.google/workbook/team-lifecycles/`. The chapter
  is the companion to SRE Book Chapter 27 ("Reliable Product Launches") and the
  workbook's engagement chapter (Ch18); it operationalizes the enterprise
  roadmap linked from the chapter ("enterprise-roadmap-to-sre").
- **Author credibility**: Highest available. Written by David Ferguson and
  Prashant Labhane with Shylaja Nukala, all Google SRE authors published on the
  official sre.google domain; the "Transforming an Existing Team into an SRE
  Team" case study is a first-party account by Brian Balser of the New York
  Times' actual conversion of a service-config operations team. Published by
  O'Reilly under CC BY-NC-ND 4.0.
- **Scope**: Covers (a) the three SRE principles and the staged org-maturity
  roadmap (SRE practices without SREs → first SRE → first team → many teams);
  (b) first-SRE hiring criteria and the three embedding options with selection
  factors; (c) the three team-formation approaches (new team for a major
  project / horizontal SRE team / converting an existing team in place) with
  Tuckman staging and per-formation risk/mitigation tables; (d) the NYT
  in-place-conversion case study; (e) scaling to multiple teams — service-
  complexity splits, SRE rollout prioritization, geographic splits (timezone
  separation, parity, three-site failure); (f) Google's running-many-teams
  programs (Mission Control, SRE Exchange, SRE EDU, horizontal projects, SRE
  Mobility, LCE teams, Production Excellence) and the SRE:engineer staffing
  ratio (1:5–1:50, ~1:10). Does NOT cover AI/LLM-specific content — the org
  guidance is generic SRE and applies to AI/LLM reliability teams by analogy.

## Extracted Claims

### Claim 1: SRE practices can be adopted without a single SRE by using SLOs — Principle #1 "SRE needs SLOs with consequences" — where the error budget guides both tactical mitigation and longer-term reliability prioritization, and even SRE-less organizations should set SLOs because an implicit 100% SLO makes a team permanently reactive
- **Evidence**: The "SRE Practices Without SREs" section states Principle #1 and
  lists the four SRE-less practices (acknowledge you don't want 100% reliability;
  set a reasonable user-relevant SLO target; agree an error budget policy that
  guides tactical and long-term work; measure and commit with leadership
  agreement). It explicitly argues SLOs + an error budget policy are worthwhile
  with zero SRE staff.
- **Confidence**: settled
- **Quote**: "SRE needs SLOs with consequences." — and — "Even if an organization doesn't have SRE staff, we believe that it is worthwhile to set SLOs for critical customer applications and to implement an error budget policy, if only because an implicit 100% SLO means a team can only ever be reactive."
- **Our assessment**: The chapter's entry point is that SLOs-with-consequences is
  a prerequisite, not an output, of having an SRE team — consistent with the
  corpus's SLO-before-GA material (engagement-model note) and the workbook's
  Implementing SLOs chapter. For AI/LLM platforms: a reliability program for
  agents/models can start with error-budgeted SLOs before any dedicated
  reliability staff exists.

### Claim 2: The first SRE should be hired against five interview areas — operations, software engineering, monitoring systems, production automation, system architecture — and will occupy a difficult, ambiguous position between velocity and reliability
- **Evidence**: The "Finding Your First SRE" section enumerates the five areas,
  each with a one-line rationale (e.g., production automation: "Scaling
  operations requires automation"), and characterizes the first hire's position.
- **Confidence**: settled
- **Quote**: "Your first SRE will likely occupy a difficult and ambiguous position between velocity and reliability goals." — and — "Running applications in production gives invaluable insights that cannot be easily gained otherwise."
- **Our assessment**: A concrete hiring rubric that doubles as a skills checklist
  for the first AI/LLM reliability engineer: the five areas (ops, SWE, monitoring,
  automation, architecture) are exactly the breadth an AI-reliability hire needs.
  The ambiguity framing matches the corpus's first-SRE-in-small-org warnings.

### Claim 3: The first SRE can be embedded three ways — in a product development team, in an operations team, or in a horizontal consulting role across teams — selected on five factors (sphere of influence, immediate challenges, 12-month outlook, org-change plans, the person); experimentation is fine early, but stick with one stable model long-term
- **Evidence**: The "Placing Your First SRE" section lists the three options and
  the five evaluation factors, then warns against model instability.
- **Confidence**: settled
- **Quote**: "It might make sense to experiment with different models as you figure out which approach works best for you. However, we strongly recommend sticking with one stable and coherent model in the long term; otherwise, the instability will undermine the effectiveness of SRE."
- **Our assessment**: The three embedding options and the five-factor selection
  framework are a direct decision procedure for where to place a first AI/LLM
  reliability hire (in the ML platform team vs the infra/ops team vs a horizontal
  reliability function). The stability warning is the org-level complement of
  the engagement-model note's relationship-management guidance.

### Claim 4: The first SRE's initial mission is to get up to speed on the service — its problems, its required toil, and the engineering needed to stay within SLOs — which leads to Principle #2 "SREs must have time to make tomorrow better than today"; three warning signs mark a failing first-SRE role
- **Evidence**: The "Bootstrapping Your First SRE" section states Principle #2
  and its rationale (toil grows with service usage), gives starter project
  suggestions (monitoring, postmortem actions, automation of a specific toil
  element), and lists the three warning signs.
- **Confidence**: settled
- **Quote**: "SREs must have time to make tomorrow better than today." — and — "Without this principle, toil will only increase as service usage increases and the system becomes correspondingly larger and more complex." — and — "Their mix of work is indistinguishable from other engineering work."
- **Our assessment**: Principle #2 is the org-design statement of the 50%
  project-work rule already in the corpus (eliminating-toil note's operational
  cap; Treynor's 50% development-time rule). The warning signs — work
  indistinguishable from other engineering, SRE doing more than their fair share
  of ops, SLOs not taken seriously — are checkable failure signals for the
  guide's toil chapter.

### Claim 5: Organizations with distributed SREs (no discrete team) should build a community that advocates the SRE's distinctive role and drives consistent reliability change, because without a social grouping individual SREs feel isolated
- **Evidence**: The "Distributed SREs" section under "Starting an SRE Role."
- **Confidence**: settled
- **Quote**: "Without a social grouping, individual SREs may feel very isolated."
- **Our assessment**: A named mitigation for the "sprinkled SREs" problem the
  corpus already flags as an anti-pattern (life-beyond-google note): if SREs are
  scattered, give them a community. Directly applicable to organizations with a
  lone AI-reliability engineer.

### Claim 6: The first SRE team can be formed three ways, from least to most complex — a new team as part of a major project, a horizontal SRE team, or converting an existing team (e.g., operations) in place — with an explicit warning against renaming Ops→SRE without first applying SRE practices
- **Evidence**: The "Your First SRE Team" section lists the approaches and the
  "Converting a team in place" subsection carries the rename warning.
- **Confidence**: settled
- **Quote**: "Be careful to avoid renaming a team from \"Operations\" to \"SRE\" without first applying SRE practices and principles!"
- **Our assessment**: The rename warning is a high-value guardrail for the guide:
  retitling a toil-heavy ops team "AI SRE" without changing practice is the org-
  level version of the checkbox-SRE anti-pattern. The three-approach menu (new /
  horizontal / convert) is the decision framework for standing up an AI
  reliability team.

### Claim 7: Principle #3 "SRE teams have the ability to regulate their workload" is the most subtle and most organizationally difficult of the three principles, and most teams cannot embrace it from day one
- **Evidence**: The chapter intro to "Your First SRE Team" states the principle
  and its caveats before walking the Tuckman stages.
- **Confidence**: settled
- **Quote**: "Outside of a large SRE organization, a team likely can't embrace this concept from day one." — and — "It's also the most subtle of our three principles, and bears some unpacking."
- **Our assessment**: Principle #3 is workload self-determination, earned through
  maturity. The guide should present it as a performing-stage capability, not a
  formation-stage requirement — consistent with the norming/storming risk
  material (Claim 9-10).

### Claim 8: Team formation is staged with Tuckman's forming/storming/norming/performing model; forming requires a specific skill mix (app-software reliability changes, detection/mitigation + automation tooling, strong software practices, methodical operational changes, system architecture) and benefits from seeding with internal transfers
- **Evidence**: The "Forming" section lists the required combined expertise and
  recommends seeding; the Tuckman model is cited to the 1965 Psychological
  Bulletin paper in footnote 1.
- **Confidence**: settled
- **Quote**: "If possible, we recommend that you seed the team with internal transfers."
- **Our assessment**: The forming skill mix is an explicit staffing checklist for
  a new reliability team (including AI-reliability teams): it notably includes
  writing software to expedite detection/mitigation and automate manual processes
  — the exact competencies the guide's runbook/agent chapters assume. Seeding
  with transfers matches the corpus's barn-raise guidance (on-call note).

### Claim 9: For a team created as part of a major project, the storming phase carries six risks (spreading too thin, SLO-perfectionist introspection, not examining work, abandoning principles for product milestones, conflict with existing teams, insufficient skill breadth) with named mitigations — engage on a single service, engage at design stage, no day-one operational responsibility, and keep new hires below a third of the team
- **Evidence**: The "New team as part of a major project" risk/mitigation table:
  the six risks and their paired mitigations, including the page-desensitization
  example ("The team is paged 100 times a day") and the new-hire ratio rule.
- **Confidence**: settled
- **Quote**: "The team is paged 100 times a day. Since the pages don't indicate that immediate intervention is required, they ignore the pages." — and — "Continue to keep the number of new hires to less than a third of the team so that the training effort doesn't overwhelm existing team members."
- **Our assessment**: The 100-pages-a-day desensitization example is the toil-
  overflow failure mode for a new team, and the "no operational responsibility on
  day one" mitigation (responsibility initially stays with the product team) is a
  concrete, citable staffing pattern. The <1/3 new-hire ratio is a useful sizing
  rule for growing an AI reliability team.

### Claim 10: Horizontal SRE teams and converted-in-place teams have distinct storming risks — horizontal teams risk being perceived as a value-less "gating" org (mitigate: respected seeds, tools benefiting ≥2 teams, celebrating wins, "enablers, not gatekeepers"); converted teams risk job-loss fear, no slack, and missing automation skills (mitigate: leadership support, renegotiated slack, head-on job-loss communication, training, changed performance metrics, adding an experienced SRE)
- **Evidence**: The "Horizontal SRE team" and "A team converted in place"
  risk/mitigation tables; the job-loss communication guidance states that
  automation typically eliminates portions of work rather than whole jobs.
- **Confidence**: settled
- **Quote**: "Sees themselves as enablers, not gatekeepers. Focus on solutions, not just problems." — and — "Perceives that the conversion process is the start of a slow journey to job losses as automation replaces humans." — and — "In a lot of environments, automation eliminates portions of work, but not jobs as a whole; while this might be a step on the path to job losses, it does at least have the virtue of freeing up time to do something better (and more sellable to a future employer) than nonautomated toil."
- **Our assessment**: Two citable patterns. The horizontal-team mitigation list
  (tools with short-term benefit to ≥2 teams, celebrate wins, enablers-not-
  gatekeepers) is exactly the operating model a horizontal AI-for-SRE tools team
  needs — and the corpus already has a real Google instance (del Cid's team). The
  converted-team guidance is the human-change-management side of automation
  adoption the guide should carry when recommending agent-driven toil reduction.

### Claim 11: Case study (New York Times, Brian Balser): converting a ticket-driven, interrupt-flooded configuration-support team in place worked by inverting the responsibility model — embedding an SRE in the dev team, splitting config into team-based repos, moving to a GitHub-driven Drone CI/CD pipeline, and holding daily office hours to batch review interrupts — reaching >50% project work
- **Evidence**: The "Transforming an Existing Team into an SRE Team" section
  describes the four process stages, the office-hours interrupt batching, and the
  measured outcome. The prior state: a team "driven by tickets and production
  issues," "in a continuous reactive mode," with a looming bus factor.
- **Confidence**: settled
- **Quote**: "One guiding principle of our SRE organization is to remove ourselves from the critical path and to empower product development teams with self-service solutions." — and — "The SRE team is now meeting its initial goal of > 50% project work (versus support-related work)."
- **Our assessment**: A worked, first-party instance of the converting-in-place
  path (Claim 10's mitigations in action) and of Principle #2 measured as >50%
  project work. The four stages — embed an SRE, split config ownership, standard
  CI/CD, self-service onboarding — are a directly copyable playbook for an AI
  platform team absorbing a legacy operations/support team.

### Claim 12: The norming phase has explicit maturity criteria — SLOs/error budgets in place and exercised after incidents, sustainable compensated on-call with tooling/docs/training, toil documented/bounded/managed, established postmortem culture, most DevOps tenets, regular training exercises (Wheel of Misfortune, DiRT), the product team remaining in the on-call rotation, and regular stakeholder reports
- **Evidence**: The "Norming" section's maturity checklist plus the
  "Transforming an Existing Team" case study that sits within it.
- **Confidence**: settled
- **Quote**: "Toil is documented, bounded, and managed. As a result, SREs complete impactful projects that improve reliability and efficiency." — and — "On-call rotations are established and sustainable"
- **Our assessment**: This is the chapter's definition of a "working" SRE team —
  a concrete, checkable norming gate that links directly to the corpus's
  on-call (compensation, tooling) and postmortem notes. The product-team-in-
  rotation item corroborates the engagement-model note's developer-in-on-call
  doctrine from the team-formation side.

### Claim 13: At the performing stage, the SRE team partners on all architecture design and change and has complete workload self-determination — it chooses if/when to onboard a service, reduces toil by lowering the SLO or transferring operational work, and can hand a service back; without that self-regulation the team risks attrition that "can put production at risk"
- **Evidence**: The "Performing" section's two subsections (Partnering on
  architecture; Self-regulating workload), including the operational-overload
  levers and the hand-back condition, and the no-dev-partner tactics.
- **Confidence**: settled
- **Quote**: "The product development team should start to reach out to its partner SRE team for advice on all significant service changes." — and — "Otherwise, your team risks attrition as SREs move on to more interesting opportunities. The slow bleed from attrition can put production at risk." — and — "If the service does not conform to its SLO, stop feature-related project work in favor of reliability-focused project work."
- **Our assessment**: Principle #3's operating levers (choose to onboard, reduce
  the SLO, transfer work, hand back) are the concrete workload-regulation
  machinery — the same lever set the engagement-model note's hand-back conditions
  describe. For AI/LLM services this is the governance answer to "who can stop
  operating an unhealthy agent/model and hand it back." The attrition warning is
  a named failure mode for over-committed reliability teams.

### Claim 14: Forming more SRE teams is motivated by service complexity, SRE rollout success, or geographic split; the creation checklist is to read prior teams' postmortems, seed the new team from the existing one, standardize the team/onboarding framework, and change on-call responsibilities slowly (keep team members on-call for the old system transitionally; wait three to six months before splitting rotations)
- **Evidence**: The "Making More SRE Teams" section's four recommendations, the
  on-call-transition guidance, and the "SRE Rollout" prioritization subsection
  (prioritize high financial/reputational impact, protect the minimal viable set,
  don't prioritize a service merely because it's unreliable).
- **Confidence**: settled
- **Quote**: "Seed the new team with SREs from the existing team—some of your best SREs and highest-potential SREs who can rise to the challenge." — and — "After the teams split, wait three to six months to split the on-call rotations." — and — "A service should not be a priority for SRE simply because it's unreliable."
- **Our assessment**: Two concrete, citable practices: seeding a new team from an
  existing one (matching the corpus's culture-transfer/shard guidance), and the
  3–6-month on-call split lag with a transitional on-call period — an explicit
  safety rule for restructuring. The SRE-rollout prioritization (impact-driven,
  minimal-viable-set, not "because it's unreliable") mirrors the engagement-model
  note's where-to-focus selection.

### Claim 15: Splitting teams — service-complexity splits run along architectural, language, or location lines, with a designated responsible team plus a senior technical lead to prevent orphaned components; geographic splits work best 6–8 time zones apart, require active parity management to prevent a "night shift" office, and three-site splits are a known failure mode
- **Evidence**: The "Service Complexity" (Where to split / Pitfalls) and
  "Geographical Splits" sections, including the parity/vigilance guidance, the
  6–8-hour timezone recommendation, and the three-site failure analysis.
- **Confidence**: settled
- **Quote**: "Designate one team as responsible for everything not covered in the second team's charter." — and — "In our experience, staffing teams in time zones that are six to eight hours apart works well and avoids 12 a.m. to 6 a.m. on-call shifts." — and — "be vigilant to ensure that the team that is not colocated (\"Office 2\") doesn't become a night shift that has little contact with the product development team, takes more than its fair share of toil, or is assigned only the less interesting or impactful projects." — and — "If all on-call duties take place only during office hours, there's less of an incentive to automate low-level toil and low-value pages."
- **Our assessment**: High-value org-design detail for the guide: the explicit
  "night shift office" anti-pattern and its mitigation practices (balance on-call
  load and project allocation between offices, split projects to force
  interaction, similar team size/seniority) are directly applicable to
  distributed AI-platform teams. The three-site failure mode (no all-hands
  meeting, weaker parity, and — notably for automation — office-hours-only on-call
  removing the incentive to automate toil) is a concrete warning against
  follow-the-sun staffing past two sites.

### Claim 16: For running many SRE teams, Google uses named programs — Mission Control (six-month product-engineer embeds), SRE Exchange (one-week team swaps), SRE EDU training, horizontal project teams, SRE Mobility (free transfer), LCE teams for low-engagement services, and Production Excellence senior reviews — and funds SRE like product engineering, keeping the SRE-to-engineer ratio at roughly 1:5–1:50 (about 1:10 for most services)
- **Evidence**: The "Suggested Practices for Running Many Teams" section and the
  "SRE Funding and Hiring" section with the ratio ranges.
- **Confidence**: settled
- **Quote**: "senior SRE leaders review every SRE team, assessing them on a number of standard measures (e.g., pager load, error budget usage, project completion, bug closure rates)." — and — "At Google, the ratio of SREs to engineers on product development teams ranges from around 1:5 (e.g., low-level infrastructure services) to around 1:50 (e.g., consumer-facing applications with a large number of microservices built using standard frameworks). Many services fall in the middle of this range, at a ratio of around 1:10." — and — "In short, you should have fewer SREs than the organization would like, and only enough SREs to accomplish their specialized work."
- **Our assessment**: The ratio range (1:5–1:50, ~1:10 typical) is the more
  granular sibling of the engagement-model note's "<10%" figure — both should be
  cited together. The named programs (Mission Control, SRE Exchange, SRE EDU,
  Production Excellence, SRE Mobility) are concrete, adoptable mechanisms for
  an AI/LLM reliability org, and the horizontal-projects pattern is corroborated
  by del Cid's horizontal AI-for-SRE team.

## Concrete Artifacts

### Artifact A — The three SRE principles (verbatim-condensed from the chapter's note boxes and conclusion)

```
Principle #1: SRE needs SLOs with consequences.
              "The performance of your service relative to SLOs should guide
               your business decisions."
Principle #2: SREs must have time to make tomorrow better than today.
Principle #3: SRE teams have the ability to regulate their workload.
```

### Artifact B — First-SRE interview skill areas (verbatim, from "Finding Your First SRE")

```
Operations
- Running applications in production gives invaluable insights that cannot be
  easily gained otherwise.
Software engineering
- SREs need to understand the software they are supporting, and be empowered to
  improve it.
Monitoring systems
- SRE principles require SLOs that can be measured and accounted for.
Production automation
- Scaling operations requires automation.
System architecture
- Scaling the application requires good architecture.
```

### Artifact C — First-SRE embedding options and selection factors (verbatim-condensed from "Placing Your First SRE")

```
Three options:
  1. In a product development team
  2. In an operations team
  3. In a horizontal role, consulting across a number of teams

Selection factors:
  - "Your own role and sphere of influence."
  - "The immediate challenges that you face."
  - "The challenges you expect to face in the next 12 months."
  - "Your plan for how you want to change your organization."
  - "The person you have identified as your first SRE."
```

### Artifact D — Three team-formation approaches with their storming risks/mitigations (verbatim-condensed from "Your First SRE Team" and "Risks and mitigations")

```
Formation approaches (least to most complex):
  1. "Creating a new team as part of a major project"
  2. "Establishing a horizontal SRE team"
  3. "Converting an existing team (for example, an operations team)"

New-team-as-major-project risks: spreads too thin; too introspective (e.g.,
"consumed with developing the perfect SLO definition"); doesn't examine its work
("paged 100 times a day" and pages are ignored); abandons principles for product
milestones; conflict with existing teams; insufficient skill breadth.
Mitigations: "Engages initially on a single important service"; engage at the
design stage; "Has input into the design, with a particular focus on defining
SLOs"; "Is not expected to have operational responsibility on day one"; clear
onboarding conditions; "keep the number of new hires to less than a third of the
team."

Horizontal-team risks: perceived as a "gating" organization doing no real work.
Mitigations: seed with respected experts; deliver tools with "a short-term
beneficial impact on at least two other teams"; celebrate successes; "Sees
themselves as enablers, not gatekeepers."

Converted-team risks: job-loss fear; no support for the change; no slack; no
day-to-day benefit; systems that don't support scripting; missing software
engineering skills.
Mitigations: "Secures senior leadership support"; "Renegotiates responsibilities
to create the slack needed to effect change"; careful change communication;
deal with job-loss concern head on; training; "Changes how performance is
evaluated"; "Adds an experienced SRE or developer to the team"; freedom to
introduce monitoring/alerting systems; regular progress reviews.
```

### Artifact E — Workload self-regulation levers at the performing stage (verbatim-condensed from "Self-regulating workload")

```
With a product development partner:
  - "An SRE team chooses if and when to onboard a service"
  - In the event of operational overload, the team can reduce toil by:
      "Reducing the SLO"
      "Transferring operational work to another team (e.g., a product
       development team)"
  - "If it becomes impossible to operate a service at SLO within agreed toil
     constraints, the SRE team can hand back the service"
  - If all problems are solved: intentionally pick new reliability challenges or
    intentionally hand back the service — otherwise attrition risk.

Without a dev partner (team builds/runs the systems):
  - "If the service does not conform to its SLO, stop feature-related project
     work in favor of reliability-focused project work."
  - "reduce your SLOs—unless management provides more capacity (people or
     infrastructure) to deal with the situation."
```

### Artifact F — Scaling guidance: making more teams, splitting, and geographic placement (verbatim-condensed)

```
Creation checklist ("When you're creating a new SRE team"):
  - "Read any postmortems written after other teams were established."
  - "Seed the new team with SREs from the existing team—some of your best SREs
     and highest-potential SREs who can rise to the challenge."
  - "Standardize the framework for establishing teams and onboarding services."
  - On-call changes slowly: "keep team members on-call for their previous team's
     systems for a transitional period"; "After the teams split, wait three to
     six months to split the on-call rotations."

SRE rollout prioritization:
  - "Prioritize services for which reliability has a high financial or
     reputational impact."
  - "Define the minimal viable set of services that need to be up in order for
     the product to function."
  - "A service should not be a priority for SRE simply because it's unreliable."

Geographic splits:
  - Timezone separation: "six to eight hours apart works well and avoids 12 a.m.
     to 6 a.m. on-call shifts."
  - Parity: "be vigilant to ensure that the team that is not colocated
     ('Office 2') doesn't become a night shift."
  - Three-site splits fail: "It is impossible to have an interoffice production
     meeting that all SREs can attend"; office-hours-only on-call means "less of
     an incentive to automate low-level toil and low-value pages."
  - Travel: "Every SRE, product development manager, and technical lead in Site 1
     visit Site 2 annually (at a minimum), and vice versa"; "All SREs convene at
     least once a year."
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-engagement-model.md` **Claim 15** (Google's SRE-to-developer
    ratio is "< 10%") — this chapter's more granular ratio (Claim 16 here: 1:5–
    1:50, ~1:10) sits in the same scale; the two should be cited together. Also
    **Claim 16** (organize SRE teams by technology, prefer sharding) — this
    chapter's service-complexity/location split guidance and seeding-with-SREs
    practice (Claims 14-15 here) are the team-formation side of the same org-
    design doctrine. The engagement-model note is the *external* service-
    engagement lifecycle (Ch18); this note is the *internal* team lifecycle
    (Ch20) — complementary, not duplicative.
  - `discussion-google-sre-ben-treynor-interview.md` **Claim 2** (an SRE team
    must spend at least 50% of time on development) — Treynor's 50% rule is the
    interview-form statement of this chapter's Principle #2 "SREs must have time
    to make tomorrow better than today" (Claims 4, 11 here). Also **Claim 11**
    (SRE teams progress through chaotic/defined/optimizing maturity stages) — the
    interview's 3-stage maturity model and this chapter's Tuckman
    forming/storming/norming/performing roadmap (Claims 8-13 here) are two
    compatible stagings of the same "teams mature through stages" claim.
  - `docs-google-sre-eliminating-toil.md` **Claim 3** (Google caps SRE
    operational work at 50%) — the toil chapter's cap is the quantitative
    statement of Principle #2 here, and the chapter explicitly links the first
    SRE's bootstrapping mission to "its required toil (see Eliminating Toil)"
    (Claim 4 here). Also **Claim 1** (toil definition) is what the converted-team
    risk "no slack capacity" (Claim 10 here) implicitly references.
  - `docs-google-sre-on-call.md` **Claim 11** (staffing minimums — 5/site
    multisite, 8/site single-site) — this chapter's geographic-split rationale
    ("Splitting the pager rotation into 12-hour shifts allows proper breaks") and
    norming criterion ("On-call rotations are established and sustainable") assume
    the on-call staffing mechanics that note documents. Also **Claim 16** (the
    Mountain View 3-month bootstrap: two-dozen-item checklist, shadow-before-
    primary) — a worked instance of this chapter's forming/storming team-assembly
    guidance (Claim 8 here).
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` **Claim 1** (an "AI for
    SRE" effort at Google runs as a *horizontal* tools team across "tens of
    teams", not per-team embeds) — a real Google instance of this chapter's
    horizontal-team formation approach (Claims 6, 10, 16 here), and the strongest
    AI-ops angle on this chapter: the org shape the chapter recommends is exactly
    the shape del Cid's AI-for-SRE team uses.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` **Claim 6** (in large
    companies a central team responsible for the *practice* of SLOs works well as
    consultant/advisor/arbitrator, not creator) — corroborates this chapter's
    horizontal-consulting embedding option and LCE/horizontal-teams model (Claims
    3, 6, 16 here) from the SLO-practice side.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` **Claim 9** (SRE
    emerges from a small, motivated, empowered team with end-to-end
    responsibility) — corroborates this chapter's forming composition guidance
    (Claim 8 here) from practitioner experience.

- **Contradicts**: None identified. Specific checks against apparent tensions
  (per MINER.md §4a, none rise to a filed contradiction):
  - (a) This chapter's Principle #1 "SRE needs SLOs with consequences" (Claim 1
    here) vs `docs-google-sre-prodcast-02-08-life-beyond-google.md` **Claim 5**
    ("don't start a reliability program with SLOs") — a **conditioning-variable**
    difference, already analyzed in the engagement-model note's Contradicts
    section: the workbook chapter is written for orgs that can meaningfully
    measure reliability, while the Xoogler panel addresses orgs lacking
    production hygiene/monitoring. No contradiction issue filed.
  - (b) This chapter's embedding options put the first SRE *in* a product or ops
    team (Claim 3 here) vs `docs-google-sre-prodcast-02-08-life-beyond-google.md`
    **Claim 12** (the single-embedded-SRE-becomes-the-ops-person anti-pattern) —
    conditioning again: the chapter explicitly requires the SRE to have "a
    distinctive role" with projects that "benefit the whole team" and lists
    "doing more than their fair share of operational work" as a warning sign
    (Claim 4 here), which is precisely the setup the anti-pattern warns fails
    when the embedded SRE is isolated. The two sources agree once scope is
    specified; no contradiction.
  - (c) This chapter's ~1:10 typical ratio (Claim 16 here) vs the engagement-model
    note's "< 10%" (Claim 15 there) — the chapter's 1:10 figure and the
    engagement-model's <10% figure are consistent (1:10 ≈ 10%, and the chapter
    gives the 1:5–1:50 range); no opposition.

- **Extends**:
  - `docs-google-sre-engagement-model.md` — the engagement note covers how an SRE
    team manages the *external* service lifecycle and engagements; this chapter
    supplies the *internal* team lifecycle (formation, staging, scaling) that
    runs the engagements. Together they give Ch04/Ch05 the full org-design
    picture (team-building + engagement management). The engagement note's
    technology-grouping and sharding rules (Claim 16 there) are extended here by
    the service-complexity split axes, geographic-split placement, and
    postmortem-driven team-creation checklist (Claims 14-15 here).
  - `discussion-google-sre-ben-treynor-interview.md` — Treynor's maturity model
    (chaotic/defined/optimizing, Claim 11 there) is extended by this chapter's
    operational stage map: forming/storming/norming/performing with per-formation
    risk tables and the workload-regulation levers at performing.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — that note's
    anti-patterns (checkbox SRE, sprinkled SREs, single-embedded-SRE) are
    extended by this chapter's *positive* org-design machinery: the distributed-
    SRE community (Claim 5 here) is the remedy to sprinkled-SRE isolation, and
    the conversion-in-place path with guardrails (Claims 6, 10, 11 here) is the
    structured alternative to a bare Ops→SRE rename.
  - `docs-google-sre-eliminating-toil.md` — that note's toil-management strategies
    sit inside this chapter's team-lifecycle context: the bootstrapping mission
    (get up to speed on the service's required toil), the norming criterion (toil
    "documented, bounded, and managed"), and the converted-team mitigation
    (training + monitoring/alerting freedom) are where the toil strategies get
    staffed.

- **Novel**: Material new to the corpus:
  - **The three SRE principles as a named triad** (Claims 1, 4, 7; Artifact A) —
    "SLOs with consequences," "time to make tomorrow better than today,"
    "regulate their workload." Individual principles exist in the corpus
    (50% rule, SLO-licenses-inaction), but this is the first note presenting the
    canonical three-principle framing.
  - **The SRE-practices-without-SREs stage** (Claim 1) — the explicit claim that
    an error-budgeted SLO program can (and should) precede hiring any SRE.
  - **The five first-SRE interview skill areas** (Claim 2, Artifact B) and the
    **three embedding options with five selection factors** (Claim 3, Artifact C).
  - **The three team-formation approaches with the "don't rename Ops→SRE"
    warning** (Claims 6, 10; Artifact D) and the **per-formation risk/mitigation
    tables** — including the <1/3 new-hire ratio and the "no operational
    responsibility on day one" rule (Claim 9).
  - **The Tuckman forming/storming/norming/performing staging applied to SRE
    teams** (Claims 8, 12) with the norming maturity checklist.
  - **The NYT in-place-conversion case study** (Claim 11) — self-service
    inversion of the responsibility model reaching >50% project work.
  - **The workload self-regulation levers at performing** (Claim 13, Artifact E) —
    choose onboarding, reduce the SLO, transfer work, hand back; plus the
    no-dev-partner tactics.
  - **The scaling-to-many-teams checklist** (Claim 14): postmortem-driven team
    creation, seeding from the existing team, the 3–6-month on-call split lag,
    and SRE-rollout prioritization ("not simply because it's unreliable").
  - **Service-complexity split axes and the orphaned-component mitigations**
    (Claim 15): designated responsible team + senior technical lead.
  - **The geographic-split placement rules** (Claim 15): 6–8 time zones apart,
    the "night shift" office parity anti-pattern and its mitigation practices,
    and the three-site failure mode (incl. the office-hours-on-call incentive
    argument against automating toil).
  - **Google's running-many-teams programs** (Claim 16): Mission Control, SRE
    Exchange, SRE EDU, horizontal projects, SRE Mobility, LCE teams, Production
    Excellence — and the 1:5–1:50 (~1:10) staffing ratio.

## Guide Impact

- **Chapter 00 (principles)**: Add the canonical three-principle framing
  (Claim 1, 4, 7; Artifact A) as the org-design substrate for the guide's SLO/
  error-budget and toil chapters — particularly Principle #1's claim that SLOs
  with consequences precede having SRE staff, and Principle #3's workload
  self-regulation as a maturity-earned capability, not a day-one entitlement.
  Add Principle #2 as the team-level restatement of the 50% project-work rule,
  cross-referenced to the Treynor interview and eliminating-toil notes.

- **Chapter 04 (oncall-and-toil)**: Add the norming maturity checklist
  (Claim 12) — sustainable on-call with tooling/docs/training, toil
  "documented, bounded, and managed," postmortem culture — as the "what does a
  working reliability team look like" gate for the on-call material. Add the
  converting-in-place playbook (Claim 11: embed an SRE, split config ownership,
  CI/CD, self-service, office hours) as the Ch04 org-remediation pattern, and
  the converted-team mitigations (Claim 10: leadership support, renegotiated
  slack, head-on job-loss communication, training) as the human-change side of
  toil-reduction automation. Add the 3–6-month on-call split lag and
  transitional on-call period (Claim 14) to the rotation-change guidance, and
  the geographic-split parity rules and three-site failure mode (Claim 15) to
  any follow-the-sun on-call material.

- **Chapter 05 (llm-ops-reliability)**: The primary AI-transfer target, though
  the source contains no AI content itself. Use the five first-SRE skill areas
  (Claim 2) as the hiring rubric for a first AI/LLM reliability engineer, and
  the three embedding options + five selection factors (Claim 3) as the decision
  procedure for where to place them (ML platform team vs infra team vs
  horizontal). Use the three-formation menu and the "don't rename Ops→SRE"
  warning (Claims 6, 10) as the standing-up-an-AI-reliability-team playbook —
  including the warning against retitling a support team "AI SRE" without
  practice. Cite the horizontal-team mitigations (Claim 10) alongside del Cid's
  horizontal AI-for-SRE team (S5E4 note) as the recommended structure for an
  AI-reliability function. Add the staffing ratio (Claim 16: 1:5–1:50, ~1:10)
  and the workload-regulation levers (Claim 13) as the sizing/governance rules
  for AI platform reliability teams.

- **Chapter 03 (runbooks-and-agents)**: Add the forming skill mix (Claim 8 —
  including "writing software to... expedite the detection and mitigation of
  problems in production" and "automate manual processes") as the team
  competency baseline the runbook/agent chapters assume. Add the
  page-desensitization risk (Claim 9: paged 100 times a day → pages ignored) as
  the toil-overflow failure mode agent-run alerting must not recreate, and the
  office-hours-only-on-call incentive argument (Claim 15: "less of an incentive
  to automate low-level toil") as a structural argument for keeping on-call
  painful enough to drive automation.

## Extraction Notes

- **Source read**: The chapter at `https://sre.google/workbook/team-lifecycles`
  was fetched (raw HTML, ~74 KB) and read end-to-end: the intro and maturity-
  roadmap framing, SRE Practices Without SREs, Starting an SRE Role (Finding /
  Placing / Bootstrapping / Distributed SREs), Your First SRE Team (Forming,
  Storming with all three risk/mitigation tables, Norming incl. the NYT
  case study, Performing), Making More SRE Teams (Service Complexity, SRE
  Rollout, Geographical Splits incl. parity/placement/timing/finance/
  leadership), Suggested Practices for Running Many Teams (all nine subsections),
  the Conclusion, and both footnotes. Per MINER.md §1, linked pages (SRE Book
  Chapters 27/31/32, the enterprise roadmap, the On-Call training-roadmap anchor,
  the ACM Queue "Why SRE Documents Matter" reference) were evaluated: they are
  companion references already covered by existing corpus notes (on-call,
  engagement-model, reliable-product-launches) or outside this chapter's
  extraction scope, so no sub-pages were followed.
- **Quote verification**: All `Quote` fields and Concrete Artifact passages were
  copied character-for-character from the extracted page text (verified against
  the raw HTML text dump). Characters to note for the Assayer: the chapter uses
  curly apostrophes/curly quotes and em dashes — e.g., the Claim 6 quote uses
  curly quotes around "Operations"/"SRE", the Claim 15 quote uses curly quotes
  around "Office 2", and the Claim 14 / Artifact F quotes contain em dashes
  ("existing team—some of your best SREs", "reduce your SLOs—unless").
  Verbatim fragments were kept contiguous per MINER.md §2a. Claim count is 16 —
  one above the template's 5–15 aim, justified by the chapter's length (the full
  SRE-org lifecycle from pre-SRE to many-teams operations); each claim maps to a
  distinct section or named practice.
- **Related-notes candidates (`miner-related-notes.md`) — dispositions**:
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response, no team-lifecycle/org-formation
    content.
  - `docs-google-sre-eliminating-toil.md` — **Cited** (Claims 1, 3); see
    Corroborates — Principle #2 and the converted-team toil/slack material.
  - `docs-google-sre-on-call.md` — **Cited** (Claims 11, 16); see Corroborates —
    on-call staffing/bootstrap and the norming on-call criterion.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — **Dismissed**;
    incident-response tooling breadth, no org-design content.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — **Cited** (Claims 5,
    9, 12); see Corroborates and Contradicts — the small-empowered-team
    condition, the single-embedded-SRE anti-pattern (conditioning check), and
    the don't-start-with-SLOs claim (conditioning check).
  - `docs-google-sre-configuration-specifics.md` — **Dismissed**; configuration
    toil and DSLs (Workbook Ch15), unrelated to team lifecycle.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Cited** (Claim 1); see
    Corroborates — the horizontal AI-for-SRE team is the AI-era instance of this
    chapter's horizontal-team model.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — **Dismissed**;
    database reliability / DB culture, unrelated to team lifecycle.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` — **Cited** (Claim
    6); see Corroborates — the central SLO-practice consultant/arbitrator team
    corroborates the horizontal-consulting embedding option.
  - `docs-google-sre-data-processing-pipelines.md` — **Dismissed**; pipeline
    SLOs (Workbook Ch13), unrelated to team lifecycle.
- **Cross-reference verification (MINER.md §4b)**: Every `Claim N` citation was
  verified against the cited note: `docs-google-sre-engagement-model.md` Claims
  15, 16; `discussion-google-sre-ben-treynor-interview.md` Claims 2, 11;
  `docs-google-sre-eliminating-toil.md` Claims 1, 3; `docs-google-sre-on-call.md`
  Claims 11, 16; `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` Claim 1;
  `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claim 6;
  `docs-google-sre-prodcast-02-08-life-beyond-google.md` Claims 5, 9, 12. No
  fabricated claim numbers or reconstructed quotes.
- **Contradiction analysis (per MINER.md §4a)**: No contradiction issue filed.
  The three apparent tensions (SLOs-with-consequences vs don't-start-with-SLOs;
  embedding vs single-embedded-SRE anti-pattern; ~1:10 ratio vs <10%) were
  evaluated and are conditioning-variable or scale differences, documented under
  Contradicts. No existing `contradiction`-labeled issue or CONTRADICTIONS.md
  entry is affected.
- **Overlap with sibling chapters**: The triage flagged overlap with
  `discussion-google-sre-ben-treynor-interview.md` (team lifecycle / capability
  maturity). Per the triage, that interview's lifecycle treatment is brief and
  interview-form; this chapter is the canonical full treatment, so both notes
  stand and cross-reference (Treynor's 3-stage maturity model vs this chapter's
  Tuckman 4-stage roadmap are compatible stagings, noted under Corroborates).
- `date_published` is 2018 (SRE Workbook publication year); the page on sre.google
  carries no separate per-chapter date. `confidence_overall` is `settled`: the
  source is canonical first-party Google SRE / NYT SRE documentation describing
  the authors' own org-design practice, with a first-party case study. All
  claims are descriptive of documented practice, not speculative. No part of the
  source was paywalled.
