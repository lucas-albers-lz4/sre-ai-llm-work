---
source_url: https://sre.google/workbook/on-call
source_type: documentation
title: "Google SRE: On-Call — SRE Workbook Chapter 8"
author: "Ollie Cook, Sara Smollett, Andrea Spadaccini, Cara Donnelly, Jian Ma, and Garrett Plasky (Evernote), with Stephen Thorne and Jessie Yang"
date_published: 2018
date_extracted: 2026-08-11
last_checked: 2026-08-11
status: current
confidence_overall: settled
issue: "#866"
---

# Google SRE: On-Call — SRE Workbook Chapter 8

> The canonical Google SRE workbook treatment of on-call operations: the
> two-incident pager budget and 50% project-work balance, the anatomy of pager
> load (three inputs: production bugs / alerting / human processes), response-
> time tiers, a full alert-introduction process (~1-week test window, trigger
> rate predicting pager-budget consumption, explicit team approval), playbook
> policy including the "deterministic command list → automate it" rule, the
> rigor-of-follow-up discipline with the 30-pages break-even heuristic,
> bug/alert data-quality practice (placeholder bug per paging alert, 21-day
> trailing average), staffing minimums (5/site multisite, 8/site single-site,
> +1 buffer), shift-length and scheduling-flexibility guidance, compensation,
> the Evernote outside-Google case study (P1/P2/P3 event classes, Sev1–3
> triage, CRE engagement), and team-dynamics practices. Foundational SRE
> practice knowledge for Ch04, with no AI/LLM content of its own.

## Source Context

- **Type**: documentation — SRE Workbook (O'Reilly, 2018) Chapter 8 "On-Call,"
  published at `sre.google/workbook/on-call/`. The workbook chapter is the
  companion to SRE Book Chapter 11 "Being On-Call"; it addresses "specific
  feedback and questions we received about that chapter" from smaller and
  non-Google organizations.
- **Author credibility**: Highest available. Six named authors including
  Ollie Cook, Sara Smollett, and Andrea Spadaccini (Google SRE) and Garrett
  Plasky (Evernote), with Stephen Thorne and Jessie Yang. First-party
  practitioner accounts: the Google Mountain View new-team bootstrap is a
  first-person narrative (Sara, Mike, four Nooglers), and the Evernote section
  is written by Evernote engineers describing their own cloud migration and
  on-call redesign. Google SRE data (pager-load inputs, staffing minimums,
  scheduling practice) is stated as Google norms.
- **Scope**: Covers (a) recap of the SRE Book's on-call principles (50/50
  balance, two-incident budget, psychological safety, compensation); (b) two
  real on-call setups — Google's Mountain View new-team bootstrap and Evernote's
  cloud-migration on-call redesign; (c) the anatomy of pager load — its three
  inputs, response-time expectations, a "team in overload" case study, alerting
  hygiene and the new-alert introduction process, rigor of follow-up, and data
  quality; (d) on-call flexibility — shift length, automated scheduling,
  short-term swaps, long-term breaks/staffing, part-time models; (e) on-call
  team dynamics (empower ops engineers, fun budget, co-location). Does NOT
  cover: AI/LLM operations, agent architectures, monitoring/SLO theory (other
  workbook chapters cover those). Pre-LLM-era (2018) source; its AI relevance is
  as operational context for where automation can absorb on-call toil.

## Extracted Claims

### Claim 1: Google SRE on-call strives for a balance — at least 50% of SRE time on project work — and a maximum of two incidents per 12-hour on-call shift, to ensure adequate follow-up time and prevent reliability from being bought at the cost of an on-call engineer's health
- **Evidence**: The chapter's recap of the SRE Book states the goal explicitly:
  coverage for critical services "while making sure that we never achieve
  reliability at the expense of an on-call engineer's health," the ≥50% project
  work requirement, and the two-incident pager budget (footnote 2 defines one
  incident as one problem, one shift as 12 hours). Pager-load reduction later in
  the chapter is framed against this budget.
- **Confidence**: settled
- **Quote**: "SRE work should be a healthy mix of duties: on-call and project
  work. Specifying that SREs spend at least 50% of their time on project work
  means that teams have time to tackle the projects required to strategically
  address any problems found in production." and "We target a maximum of two
  incidents per on-call shift, to ensure adequate time for follow-up. If the
  pager load gets too high, corrective action is warranted."
- **Our assessment**: The two-incident-per-shift budget is the concrete,
  citable number for "pager load as a budget" (corroborating the alerting
  Prodcast note) and the 50% project-work figure corroborates the eliminating-
  toil chapter's 50% operational-work cap. These two numbers are the load
  guardrails an AI first-responder agent would have to respect (an agent that
  pages must consume this budget, so agent-triggered paging inherits the same
  scarcity).

### Claim 2: Pager load — the number of paging incidents per shift — is influenced by three main factors: bugs in production, alerting, and human processes, each with several sub-inputs
- **Evidence**: The "Pager load inputs" section enumerates the three inputs and
  their sub-inputs: for production (number of existing bugs, introduction of new
  bugs, speed of bug identification, speed of mitigation/removal); for alerting
  (thresholds, introduction of new paging alerts, SLO alignment with dependent
  services); for human processes (rigor of fixes and follow-up, quality of data
  collected about pages, attention paid to pager-load trends, human-actuated
  changes to production). A footnote defines "bug" broadly: logic errors,
  incorrect configuration, incorrect capacity planning, misconfigured load
  balancers, and newly discovered vulnerabilities all count.
- **Confidence**: settled
- **Quote**: "Pager load is the number of paging incidents that an on-call
  engineer receives over a typical shift length (such as per day or per week).
  An incident may involve more than one page." and "Pager load is influenced by
  three main factors: bugs in production, alerting, and human processes."
- **Our assessment**: This is the diagnostic map for reducing pager load — it
  tells a team *where* to look (which input) rather than just "page load is too
  high." For the guide this is the causal model behind Ch04's pager-load
  management: alerting inputs are the fastest lever (and the one an agent that
  decides when to page directly affects), human-process inputs are the
  slowest/most cultural, and production-bug inputs are the same bug-reduction
  discipline the SRE Book prescribes.

### Claim 3: Response-time expectations are tiered by incident severity — a revenue-impacting network outage warrants 5 minutes, a stuck customer-order batch process 30 minutes, and failing backups of a pre-launch service a ticket — so not every page needs an immediate response
- **Evidence**: Table 8-1 ("Examples of realistic response times") gives three
  concrete tiers with their SRE impact (Table 8-1 shown in Concrete Artifacts):
  5 minutes with "SRE needs to be within arm's reach of a charged and
  authenticated laptop" and heavy coordination with the secondary; 30 minutes
  allowing a quick errand with no secondary coverage; ticket for non-critical
  work-hours issues. The chapter's guidance is to audit the paging setup against
  these expectations.
- **Confidence**: settled
- **Quote**: "Engineers shouldn't have to be at a computer and working on a
  problem within minutes of receiving a page unless there is a very good reason
  to do so." and "You may be paging for issues that would be better served by
  automated repair (as it's generally better for a computer to fix a problem
  than requiring a human to fix it) or a ticket (if it's not actually high
  priority)."
- **Our assessment**: The 5-min / 30-min / ticket ladder is a concrete
  classification scheme the guide can adopt for "what pages, what tickets, what
  gets auto-remediated." The "better served by automated repair" clause is
  significant: the chapter explicitly ranks computer-fix > human-fix > ticket as
  the desired resolution paths, which is the direct pre-agent statement of the
  Ch03 runbook-automation thesis. Settled.

### Claim 4: Alerting hygiene — every paging alert must be immediately actionable with a high signal-to-noise ratio; under SLO-based/symptom-based alerting, relaxing alert thresholds is rarely an appropriate response to being paged
- **Evidence**: The "Alerting" subsection reiterates the SRE Book's monitoring
  guidelines: all alerts immediately actionable (an action a human must take
  that the system cannot take itself), high signal-to-noise ratio to prevent
  alert fatigue, SLO-alignment across all teams in the service's dependency
  chain, playbook entry per alert, and the "relaxing thresholds is rarely
  appropriate" rule. It also notes the "negative psychological impact" of pages.
- **Confidence**: settled
- **Quote**: "All alerts should be immediately actionable. There should be an
  action we expect a human to take immediately after they receive the page that
  the system is unable to take itself. The signal-to-noise ratio should be high
  to ensure few false positives; a low signal-to-noise ratio raises the risk for
  on-call engineers to develop alert fatigue." and "If a team fully subscribes
  to SLO-based and symptom-based alerting, relaxing alert thresholds is rarely
  an appropriate response to being paged."
- **Our assessment**: Corroborates the "urgent AND actionable" page criterion
  from the S1E03 alerting note and the IMG note's alerting attributes, restated
  in the authoritative workbook. The anti-threshold-relaxation rule is a
  genuinely useful guardrail for on-call fatigue management and has a direct
  agent analog: an AI responder that "fixes" noisy pages by muting/relaxing
  alerts instead of addressing root cause is doing the same damage at higher
  speed.

### Claim 5: New paging alerts must be introduced through a gated process — reviewed by the whole team, tested in author-email mode for roughly a week under typical production conditions, with the test-period trigger rate used to predict pager-budget consumption and an explicit team approve/disallow decision
- **Evidence**: The "Alerting" subsection prescribes the full lifecycle: anyone
  can write an alert but the whole team reviews additions; test new alerts in
  production (e.g., email the author rather than paging) to vet false positives;
  run the test long enough to see typical periodic conditions — "A week of
  testing is probably about right"; then use the trigger rate to predict pager-
  budget consumption and approve or disallow as a team. It closes: "If
  introducing a new paging alert causes your service to exceed its paging
  budget, the stability of the system needs additional attention."
- **Confidence**: settled
- **Quote**: "Thoroughly test new alerts in production to vet false positives
  before they are upgraded to paging alerts. For example, you might email the
  alert's author when the alert fires, rather than paging the on-call engineer."
  and "Be sure to run the new alerts in test mode long enough to experience
  typical periodic production conditions, such as regular software rollouts,
  maintenance events by your Cloud provider, weekly load peaks, and so on. A
  week of testing is probably about right."
- **Our assessment**: This is a complete, citable change-management process for
  adding pages — the ~1-week email-first test window and the trigger-rate→budget
  prediction are the two concrete, adoptable mechanics. It is exactly the gate an
  AI agent's newly-introduced page (or self-escalation rule) should also pass:
  no agent should be able to add itself to the pager without the same
  test-then-approve cycle. Settled.

### Claim 6: Playbook policy is a genuine tension (general entries vs step-by-step entries); the chapter's arbiters are (a) agree on minimal structured details, and (b) if a playbook is a deterministic list of commands run every time an alert fires, implement automation
- **Evidence**: The "Maintaining Playbooks" section describes both camps
  ("keep playbook entries general so they change slowly" vs "step-by-step
  playbooks to reduce human variability and drive down MTTR") and warns that
  conflicting views pull playbooks "in many directions." The recommendation:
  agree on minimal structured details, watch for accretion beyond them, and
  convert deterministic playbook steps into automation. The Mountain View
  section also establishes the playbook-entry-per-alert norm.
- **Confidence**: settled
- **Quote**: "If you agree on nothing else, at least decide with your team what
  minimal, structured details your playbooks must have, and try to notice when
  your playbooks have accumulated a lot of information beyond these structured
  details." and "If your playbooks are a deterministic list of commands that the
  on-call engineer runs every time a particular alert fires, we recommend
  implementing automation."
- **Our assessment**: The deterministic-list→automate rule is the core arbiter
  of which runbook actions become agent automation — it is the Ch03 bridge the
  triage flagged, and it directly corroborates the eliminating-toil note's
  "automatable runbook is essentially pseudocode" claim from the on-call side
  of the discipline. The general-vs-step-by-step tension is worth preserving in
  the guide as an open design tension rather than resolving it: step-by-step
  playbooks are what make automation (and agent execution) possible, but general
  playbooks are what stay accurate under daily-release drift. Settled.

### Claim 7: Follow-up rigor requires identifying the root cause of every page — rarely concluding "cause unknown" — fixing bugs in priority order (point fix vs systemic fix vs monitoring fix), and having on-call engineers work on production bugs rather than projects during shifts
- **Evidence**: The "Rigor of follow-up" section: root causes extend "out of the
  machine and into the team's processes" (a bug that a unit test would have
  caught is a process bug in code review); the point/systemic/monitoring fix
  ladder is worked with a failure-domain example; explaining a page away as
  "transient" invites recurrence; and Google on-callers "typically doesn't work
  on projects during their on-call shift. Instead, they work on bugs that
  improve the health of the system."
- **Confidence**: settled
- **Quote**: "Aim to identify the root cause of every page." and "You should
  rarely conclude that a page is triggered by 'cause unknown.'" and "a Google
  on-caller typically doesn't work on projects during their on-call shift.
  Instead, they work on bugs that improve the health of the system."
- **Our assessment**: The "point fix vs systemic fix vs monitoring fix" ladder
  (with the monitoring fix as a *ticket* alert, not a page) is a concrete
  classification for post-incident action that the guide can adopt for Ch04
  follow-up. The bugs-over-projects shift-time rule is the operational
  expression of the 50% project-work balance (Claim 1): the balance is preserved
  by making on-call time bug-fixing time, not toil time. Settled.

### Claim 8: A concrete toil-reduction prioritization heuristic — a fix that takes 3 working weeks (120 working hours) to implement pays for itself against 4-working-hour pages at the break-even point of 30 pages
- **Evidence**: The rigor-of-follow-up section's project-bug advice gives the
  arithmetic explicitly: "If your proposal will take 3 working weeks or 120
  working hours to implement, and a page costs on average 4 working hours to
  properly handle, there's a clear break-even point after 30 pages." The chapter
  recommends filing a project bug, gathering data on how many bugs/pages the
  project would remove, and advocating for prioritization with that data.
- **Confidence**: settled
- **Quote**: "If your proposal will take 3 working weeks or 120 working hours to
  implement, and a page costs on average 4 working hours to properly handle,
  there's a clear break-even point after 30 pages."
- **Our assessment**: A concrete, citable prioritization rule for Ch04's toil-
  reduction economics: page-count times average page cost is the value of a
  systemic fix. It gives the guide a simple formula (fix value ≈ pages prevented
  × 4h; invest if project cost < that) that can also be used to justify agent
  automation of a recurring failure class. The 4-hour "cost to properly handle"
  per page is the load-bearing assumption — includes follow-up, not just
  response. Settled.

### Claim 9: Data quality for pager-load management comes from structured bug tracking — file a placeholder bug per paging alert and link each alert to its root-cause bug, producing "which bugs cause the most pages" reports; monitor pager load with a 21-day trailing average and warning-level ticket alerts
- **Evidence**: The "Data quality" and "Vigilance" sections: monitoring load
  patterns by hand "doesn't scale"; the sustainable approach is a placeholder
  bug per paging alert plus on-call engineers linking alerts to the relevant bug
  as root causes surface. Reports then answer which bugs cause the most pages and
  which components page most. Vigilance techniques: discuss pager-load trends at
  production meetings ("We've found a 21-day trailing average to be useful"),
  ticket alerts to tech leads/managers when load crosses a pre-agreed warning
  threshold, and regular SRE/developer joint production meetings. The Connection
  team applied this: "adopted a strict policy requiring every outage to have a
  tracking bug," which let the TPM see root causes in aggregate and revealed
  "human error was the second most common cause of new bugs in production."
- **Confidence**: settled
- **Quote**: "it's far more sustainable to file a placeholder bug for each
  paging alert in your bug tracking system (e.g., Jira, IssueTracker), and for
  the on-call engineer to create a link between the paging alerts from your
  monitoring system and the relevant bug in the bug tracking system, as and when
  they realize that each alert is symptomatic of a preexisting issue." and
  "We've found a 21-day trailing average to be useful."
- **Our assessment**: The alert→bug link is the same telemetry-discipline the
  guide needs for agent-triggered pages (every agent page must trace to a bug
  link, or the agent is generating unclassified noise). The 21-day trailing
  average is a concrete, adoptable metric. The "human error second most common
  cause" data point (from the Connection team's tracking-bug policy) is evidence
  for the human-change risk that automation reduces (Claim 10). Settled.

### Claim 10: Because humans are error-prone, all changes to production systems should be made by automation informed by human-developed intent configuration — the Connection team's manual changes went wrong and caused pages, while automation could pre-check safety before a change entered production
- **Evidence**: The Connection team case study: manual changes "went wrong
  sometimes; the team introduced new bugs, which caused pages. Automated systems
  making the same changes would have determined that the changes were not safe
  before they entered production and became paging events." The aggregate
  tracking-bug data (Claim 9) "revealed that human error was the second most
  common cause of new bugs in production," and the TPM used the data to
  "convince them to prioritize automation projects."
- **Confidence**: settled
- **Quote**: "Because humans are error-prone, it's better if all changes made to
  production systems are made by automation informed by (human-developed) intent
  configuration. Before you make a change to production, automation can perform
  additional testing that humans cannot."
- **Our assessment**: The "automation informed by intent configuration" principle
  is the chapter's clearest statement of the human-in-the-loop automation model —
  humans express intent, automation performs the change with pre-flight safety
  checks. This is the direct pre-agent lineage of the "AI-assisted, not AI-native"
  position: the same logic that justifies automation here (error-prone humans,
  pre-execution safety testing) applies to AI agents, with the addition that the
  agent's *own* change intent is also subject to validation. Settled.

### Claim 11: Minimum staffing for sustainable on-call is five people per site in a multisite 24/7 configuration and eight in a single-site 24/7 configuration, with one extra engineer per site as buffer — six per site (multisite) or nine per site (single-site)
- **Evidence**: The "Plan for long-term breaks" section states the minimums
  directly as "our experience" for sustaining on-call when a member temporarily
  leaves the rotation. The +1 buffer brings the figures to 6/site multisite and
  9/site single-site.
- **Confidence**: settled
- **Quote**: "In our experience, you need a bare minimum of five people per site
  to sustain on-call in a multisite, 24/7 configuration, and eight people in a
  single-site, 24/7 configuration. Therefore, it is safe to assume each site
  will need one extra engineer as protection against staff reduction, bringing
  the minimum staffing to six engineers per site (multisite) or nine per site
  (single-site)."
- **Our assessment**: This is a citable sizing floor for Ch04 — and it differs
  numerically from the on-call-rotations Prodcast note's ~12–14-person dual-site
  minimum (~6–7 per site). The two are from the same source family (workbook vs
  practitioner recollection) and are in the same order of magnitude, but the
  workbook's 5–6/site (multisite) vs APW's 6–7/site is a real numeric gap worth
  surfacing rather than merging: the workbook is the authoritative published
  number and adds the single-site case APW does not cover. Per MINER.md §4a this
  is a numerics discrepancy within the same scale, not a material opposition
  leading to different guide advice, so no contradiction issue is filed — the
  note below the claim records the discrepancy for the Smith.

### Claim 12: Shift lengths should be capped at 12 hours — 24 hours of on-call without reprieve is unsustainable — with "3 days on, 4 days off" as a shorter-shift alternative; out-of-hours on-call work should be compensated (time-off-in-lieu or cash, capped)
- **Evidence**: The "Shift Length" section: "we recommend limiting shift lengths
  to 12 hours"; 12-hour shifts work in a single location (split a week between a
  day person and an overnight person); "24 hours of on-call duty without reprieve
  isn't a sustainable setup"; "3 days on, 4 days off" is offered as an
  alternative. Compensation is in the recap: Google offers time-off-in-lieu or
  cash "capped at some proportion of the overall salary."
- **Confidence**: settled
- **Quote**: "In our experience, 24 hours of on-call duty without reprieve
  isn't a sustainable setup. While not ideal, occasional overnight 12-hour shifts
  at least ensure breaks for your engineers. Another option is to shorten shifts
  to last less than a week—something like 3 days on, 4 days off." and "While
  different companies may choose to handle this in different ways, Google offers
  time-off-in-lieu or cash compensation, capped at some proportion of the overall
  salary."
- **Our assessment**: The ≤12h cap and the 3-on/4-off variant corroborate the
  rotation-shape menu in the on-call-rotations note (12/12 dual-homed) from the
  authoritative workbook. The compensation cap ("ensures that engineers do not
  take on too many on-call shifts for economic reasons") is a useful governance
  detail the guide can cite. For AI augmentation the implication is structural:
  shift caps exist to protect human cognition, which is the scarce resource an
  agent-on-call design must preserve rather than work around. Settled.

### Claim 13: On-call scheduling should be automated with a tool that rearranges shifts for changing needs, rebalances load, factors in personal preferences and historical load — and never changes an already generated schedule; short-term swaps need a documented policy, and peer review of changes balances safety and flexibility
- **Evidence**: The "On-Call Flexibility" section specifies the tool's
  characteristics (rearrange, rebalance, fairness via preferences + history,
  and — critically — "it must never change an already generated schedule" so
  engineers can plan around shifts). For swaps: give team members the ability to
  update the rotation, document a swap policy, and "instituting peer review of
  changes provides a good tradeoff between safety and flexibility." Part-time
  work is compatible if the scheduler never assigns the part-time engineer
  outside their working days, or splits shift hours (9 a.m.–3 p.m. example).
- **Confidence**: settled
- **Quote**: "So that on-call engineers can plan around their on-call shifts, it
  must never change an already generated schedule." and "In our experience,
  instituting peer review of changes provides a good tradeoff between safety and
  flexibility."
- **Our assessment**: The "never change an already generated schedule" invariant
  is the key stability rule — predictability beats micro-optimization when humans
  are planning their lives around the pager. The peer-review-of-swaps mechanism
  is a concrete, adoptable governance pattern. For the guide's AI bridge: an
  automated scheduler is a bounded, low-risk automation target (a constrained
  optimization with a hard no-change-after-publish rule) — a good first agent
  use case for on-call operations. Settled.

### Claim 14: Evernote's outside-Google model — three event classes (P1 pages the on-call, P2 next business day, P3 informational), Sev1–3 incident triage with a paged incident manager and assembled incident team, SLO-based reframing of paging, CRE paged alongside for SLO-impacting events, and on-call explicitly freed from project work
- **Evidence**: The Evernote section (written by Evernote authors) describes the
  full redesign after moving to GCP: SLOs written down as "explicit SLOs"
  reframed what to alert on; events classified P1 (immediately actionable,
  pages on-call, SLO-impacting) / P2 (next business day, email + event stream) /
  P3 (informational, dashboards); Sev 1 incidents assemble an incident team
  (incident manager paged, scribe and communications lead, communication
  channels) with automatic postmortems, while Sev 2/3 are handled by the on-call
  responder with an abbreviated postmortem; monthly service-review meetings track
  on-call burden as a team-health barometer; and CRE was paged "alongside our own
  engineers for SLO-impacting events," reducing MTTR.
- **Confidence**: settled
- **Quote**: "We classify any event generated by our metrics or monitoring
  infrastructure into three categories:" (the P1/P2/P3 classification itself is
  reproduced verbatim in Concrete Artifacts) and "One of the benefits of keeping
  our process lightweight is that we can explicitly free the on-call from any
  expectations of project work."
- **Our assessment**: The P1/P2/P3 taxonomy is a clean, citable event-class scheme
  (distinct from the SRE Book's alerts/tickets/logs taxonomy — Evernote adds an
  SLO-impacting test and a "next business day" tier). The Sev1 escalation path
  (paged incident manager, scribe, comms lead) corroborates the IMAG role
  structure in the incident-management note, from a non-Google practitioner
  perspective. "Free the on-call from project work" is the small-team version of
  the 50% balance (Claim 1). Settled.

### Claim 15: On-call team dynamics are a first-class design concern — "empower your ops engineers" (give ops real ownership of reliability, not just a retitle) and a "fun budget" with co-location strengthen relationships so teammates protect each other from mistakes
- **Evidence**: The "On-Call Team Dynamics" section's two proposals: (1) remodel
  ops into SRE with real responsibility ("SREs own the site operation... driving
  the full resolution of issues, maintaining monitoring rules") and code-level
  involvement ("SREs are encouraged to dive into the code to make the changes
  themselves"); (2) strengthen bonds via a designated "fun budget" for offsites
  and co-location ("making all members of the on-call rotation sit together,
  regardless of job title and function area"). The motivating "survive the week"
  scenario includes a noisy alerting anti-pattern (paging by error rate rather
  than error ratio) and an engineer who ignores duplicate pages.
- **Confidence**: settled
- **Quote**: "Google designates a 'fun budget' specifically for organizing
  offsite activities to strengthen team bonds." and "We've also found that making
  all members of the on-call rotation sit together, regardless of job title and
  function area, helps improve team relations tremendously."
- **Our assessment**: The "empower ops" proposal is the workbook's answer to the
  ops-vs-developer ownership tension — and it lands on the same conclusion as the
  SRE Book: ownership and code access, not retitling, are what fix the dynamic.
  The "I protect my colleagues" mechanism (feeling worse about a 3 a.m. page you
  caused for a teammate you know) is a psychological-safety argument that has an
  agent implication: an agent that pages people it has no relationship with may
  not inherit any of these protective dynamics, so agent-page governance needs
  explicit cultural guardrails. Settled.

### Claim 16: A new SRE team can bootstrap itself to on-call readiness within three months (vs the normal 3–9 months for new hires) using a two-dozen-item training checklist, starter projects, impromptu teaching sessions, lab drills, deep dives, Wheel of Misfortune, and shadowing the outgoing team before becoming primary with them as backup
- **Evidence**: The Mountain View case study: seven people (one tech lead, one
  experienced SRE, one transfer, four Nooglers) needed on-call in three months.
  Sara and Mike compiled "a checklist of two dozen focus areas," Nooglers learned
  from codelabs/starter projects, impromptu sessions covered relevant topics, lab
  sessions built "muscle memory," deep dives explored services from first
  principles, and Wheel of Misfortune role-played recent incidents. After two
  months, "Sara, Mike, and the SRE transfer shadowed the on-call shifts of the
  outgoing Kirkland SRE team. At three months, they became the primary on-call,
  with the Kirkland SREs as backup." The team then automated release rollouts
  with canarying and "lowering machine costs by 40%."
- **Confidence**: settled
- **Quote**: "Sara, Mike, and the SRE transfer shadowed the on-call shifts of the
  outgoing Kirkland SRE team. At three months, they became the primary on-call,
  with the Kirkland SREs as backup. That way, they could easily escalate to the
  Kirkland SREs if needed. Next, the Nooglers shadowed the more experienced,
  local SREs and joined the rotation."
- **Our assessment**: The shadow-before-primary sequence is the concrete
  knowledge-transfer pattern the triage flagged, and it corroborates the
  barn-raising recipe in the on-call-rotations note (seed with experienced SREs,
  shadow, then primary) from a fully worked case study. The key transferable
  mechanism is staged exposure: shadow → primary-with-backup → independent, which
  is also exactly the right ramp for an AI first-responder agent (shadow
  (observe) → act-with-human-backup → autonomous-with-escalation). Settled.

## Concrete Artifacts

### Table 8-1 — Examples of realistic response times (verbatim-condensed from the chapter)

```
Incident description                      Response time  SRE impact
Revenue-impacting network outage          5 minutes      SRE needs to be within arm's
                                                         reach of a charged and
                                                         authenticated laptop with
                                                         network access at all times;
                                                         cannot travel; must heavily
                                                         coordinate with secondary at
                                                         all times
Customer order batch processing system    30 minutes     SRE can leave their home for
stuck                                                     a quick errand or short
                                                         commute; secondary does not
                                                         need to provide coverage
                                                         during this time
Backups of a database for a pre-launch     Ticket         None
service are failing                        (response
                                           during work
                                           hours)
```

### Pager-load inputs (verbatim list from the chapter)

```
For production:
  - The number of existing bugs in production
  - The introduction of new bugs into production
  - The speed with which newly introduced bugs are identified
  - The speed with which bugs are mitigated and removed from production

For alerting:
  - The alerting thresholds that trigger a paging alert
  - The introduction of new paging alerts
  - The alignment of a service's SLO with the SLOs of the services upon
    which it depends

For human processes:
  - The rigor of fixes and follow-up on bugs
  - The quality of data collected about paging alerts
  - The attention paid to pager load trends
  - Human-actuated changes to production
```

### Point fix vs systemic fix vs monitoring fix — the failure-domain example (verbatim-condensed)

```
Scenario: too many servers on the same failure domain (e.g., a switch),
causing regular multiple simultaneous failures.

Point fix:      "Rebalance your current footprint across more failure domains
                and stop there."
Systemic fix:   Use automation to ensure this type of server, and all other
                similar servers, are always spread across sufficient failure
                domains, and rebalance automatically when necessary.
Monitoring fix: Alert preemptively when failure-domain diversity is below the
                expected level but not yet service-impacting — "Ideally, the
                alert would be a ticket alert, not a page."
```

### Evernote P1/P2/P3 event classification (verbatim)

```
P1: Deal with immediately
    - Should be immediately actionable
    - Pages the on-call
    - Leads to event triage
    - Is SLO-impacting
P2: Deal with the next business day
    - Generally is not customer-facing, or is very limited in scope
    - Sends an email to team and notifies event stream channel
P3: Event is informational only
    - Information is gathered in dashboards, passive email, and the like
    - Includes capacity planning-related information
```

### Automated on-call scheduling tool — required characteristics (verbatim-condensed)

```
- "It should rearrange on-call shifts to accommodate the changing needs of
  team members."
- "It should automatically rebalance on-call load in response to any changes."
- "It should do its best to ensure fairness by factoring in personal
  preferences such as 'no primary during weekends in April,' as well as
  historical information such as recent on-call load per engineer."
- "So that on-call engineers can plan around their on-call shifts, it must
  never change an already generated schedule."
```

### Mountain View new-team training checklist (excerpt of the two dozen focus areas, verbatim)

```
- Administering production jobs
- Understanding debugging info
- "Draining" traffic away from a cluster
- Rolling back a bad software push
- Blocking or rate-limiting unwanted traffic
- Bringing up additional serving capacity
- Using the monitoring systems (for alerting and dashboards)
- Describing the architecture, various components, and dependencies of the
  services
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` — **Claim 3** (the
    fatigue limit: if incident follow-through volume exceeds a threshold, adjust
    SLA/rotation sizing) is corroborated by this chapter's two-incident-per-shift
    pager budget (Claim 1 here). **Claim 8** (Google's internal minimum is ~6–7
    people on each of two sites, 12–14 total) is the *sibling* claim to this
    chapter's staffing minimums (Claim 11 here) and the two differ numerically —
    see the discrepancy note under Claim 11. **Claim 9** (dominant rotation shape
    is dual-homed 12/12) is corroborated by this chapter's 12-hour shift cap and
    24-hour-unsustainable guidance (Claim 12 here). **Claim 12** (Wheel of
    Misfortune mechanics) is corroborated by this chapter's use of Wheel of
    Misfortune in both the Mountain View bootstrap (Claim 16 here) and the
    identification-delay guidance ("Practice emergency response"). **Claim 10**
    (barn-raise a new rotation by seeding with experienced SREs) is corroborated
    by the Mountain View shadow-before-primary case study (Claim 16 here).
    **Claim 2** ("feel the pain of the service" — keep developers co-on-call) is
    the rotation-culture counterpart to this chapter's team-dynamics material
    (Claim 15 here).
  - `docs-google-sre-eliminating-toil.md` — **Claim 3** (Google caps SRE
    operational work at 50%) is directly corroborated by this chapter's "at least
    50% of their time on project work" (Claim 1 here). **Claim 2** ("automatable
    runbook is essentially pseudocode") is corroborated by this chapter's
    deterministic-playbook→automate rule (Claim 6 here) — the same doctrine
    stated from the on-call side. **Claim 4** (objective toil measurement) shares
    this chapter's data-quality thesis (placeholder bug per paging alert, Claim 9
    here): both insist toil/pager-load management be data-driven, not anecdotal.
  - `docs-google-sre-prodcast-01-03-alerting.md` — **Claim 7** (pager load is a
    budget; don't add preemptive pages to a high-load rotation) is corroborated
    by this chapter's two-incident budget and by the "If introducing a new paging
    alert causes your service to exceed its paging budget, the stability of the
    system needs additional attention" rule (Claims 1, 5 here). **Claim 5** (a
    paging alert must be urgent AND actionable) is corroborated by this chapter's
    "All alerts should be immediately actionable" (Claim 4 here).
  - `docs-google-sre-incident-management-guide.md` — **Claim 2** (alerting
    attributes including "Be actionable") is corroborated by this chapter's
    actionable-alert requirement (Claim 4 here). **Claim 4** (oncall readiness
    requires playbooks and regular Wheel of Misfortune) is corroborated by this
    chapter's playbook-entry-per-alert norm and Wheel of Misfortune practice
    (Claims 6, 16 here). The Evernote Sev1 escalation (paged incident manager,
    scribe, communications lead) corroborates the IMAG role structure that note
    documents (Claim 14 here).
  - `docs-google-sre-canarying-releases.md` — **Claim 5** (a deployment that
    cannot roll back forces patching during the outage, prolonging user impact)
    corroborates this chapter's mitigation-delay doctrine — "roll back, fix, and
    roll forward" rather than "roll forward, fix, and roll forward again," and
    "avoid changes that can't be rolled back" (Claim 7 here, follow-up section) —
    and the chapter itself cites canarying as a new-bug-detection technique.

- **Contradicts**: None identified. One *numeric discrepancy* to surface rather
  than merge (not filed as a contradiction issue per MINER.md §4a — same scale,
  same source family, and no different guide advice):
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` **Claim 8** states
    Google's internal minimum as "six or maybe seven people on each of two sides
    of an ocean... cumulatively 12 to 14 people" for an SRE-funded dual-site
    rotation. This chapter (Claim 11 here) states "a bare minimum of five people
    per site to sustain on-call in a multisite, 24/7 configuration" (+1 buffer →
    6/site). The workbook's multisite per-site figure (5–6) is lower than APW's
    recollection (6–7), and only the workbook gives a single-site figure (8–9).
    Both are Google norms in the same order of magnitude; the workbook is the
    authoritative published number and APW explicitly hedges ("I've lost track").
    The Smith should cite the workbook figure for single-site and present the
    multisite figure as "5–7 per site across sources."

- **Extends**:
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` — that note covers
    rotation *design and culture* (who's on-call, rotation shapes, fatigue
    limits) from an interview. This chapter extends it with the *pager-load
    management* layer: the three-input anatomy (Claim 2 here), the response-time
    tiers (Claim 3), the gated alert-introduction process (Claim 5), follow-up
    rigor and data quality (Claims 7–9), and the scheduling-flexibility machinery
    (Claims 12–13) — none of which the episode transcript covers. Together they
    give Ch04 both the rotation-culture (that note) and the pager-load-mechanics
    (this note) layers.
  - `docs-google-sre-eliminating-toil.md` — that note is the toil taxonomy and
    reduction strategy chapter. This chapter is the *on-call operations* chapter
    in the same workbook: the toil-reduction economics (30-pages break-even,
    Claim 8 here) and the data-quality discipline (Claim 9 here) operationalize
    the eliminating-toil measurement framework inside the on-call rotation.
  - `docs-google-sre-incident-management-guide.md` — the Evernote case study
    (Claim 14 here) is the only source in the corpus that describes a
    non-Google incident-escalation path (P1/P2/P3 + Sev1–3) in the same
    lifecycle the IMG note defines; this chapter extends the corpus's incident
    coverage into the small-team / non-Google context.

- **Novel** (new to the corpus from this source):
  - The **two-incident-per-12-hour-shift pager budget** with its footnote
    definition of "incident" and "shift" (Claim 1) — the alerting note said
    "pager load is a budget" qualitatively; this is the numeric budget.
  - The **three-input anatomy of pager load** (production bugs / alerting /
    human processes) with sub-inputs (Claim 2) — a diagnostic model absent
    elsewhere in the corpus.
  - The **response-time tiers** (5 min / 30 min / ticket, Table 8-1) (Claim 3).
  - The **gated alert-introduction process** — whole-team review, ~1-week
    email-to-author test window, trigger-rate→pager-budget prediction, explicit
    approve/disallow (Claim 5).
  - The **deterministic-playbook→automate rule** as a named arbiter for runbook
    automation (Claim 6).
  - The **30-pages break-even heuristic** (3 weeks / 120h vs 4h per page)
    (Claim 8).
  - The **placeholder-bug-per-paging-alert + alert→bug link** data-quality
    mechanism and the **21-day trailing average** for pager-load vigilance
    (Claim 9) — and the Connection-team data point that **human error was the
    second most common cause of new production bugs** (Claim 10).
  - The **staffing minimums** (5/site multisite, 8/site single-site, +1 buffer
    → 6/9) (Claim 11).
  - The **automated-scheduling invariant** — "it must never change an already
    generated schedule" — and peer-reviewed swaps (Claim 13).
  - The **Evernote P1/P2/P3 event taxonomy** and Sev1–3 triage with CRE
    engagement (Claim 14).
  - The **"empower your ops engineers" + fun-budget** team-dynamics proposals
    (Claim 15).
  - The **Mountain View 3-month bootstrap roadmap** (two-dozen-item checklist,
    deep dives, shadow-before-primary) (Claim 16).

## Guide Impact

- **Chapter 04 (oncall-and-toil)**: Primary target. Add, all citable to this
  note:
  1. **Pager budget**: the two-incident-per-shift budget as the load guardrail
     (Claim 1) — and the rule that introducing a new paging alert which exceeds
     the budget signals a stability problem (Claim 5).
  2. **Pager-load anatomy**: the three-input diagnostic model (bugs / alerting /
     human processes) as the chapter's "reduce pager load" framework (Claim 2).
  3. **Response tiers**: the 5-min / 30-min / ticket ladder (Claim 3, Table 8-1)
     for classifying page-vs-ticket — complementing the alerting note's 48-hour
     heuristic with the "how fast must I respond" tier.
  4. **Alert introduction**: the gated process — whole-team review, ~1-week
     email-to-author test, trigger-rate budget prediction, explicit approval
     (Claim 5).
  5. **Playbook policy**: present the general-vs-step-by-step tension as an open
     design decision and adopt the "deterministic command list → automate"
     arbiter (Claim 6) — the direct runbook→agent bridge.
  6. **Follow-up rigor**: the point/systemic/monitoring fix ladder and
     root-cause-every-page discipline (Claim 7), plus the 30-pages break-even
     heuristic for prioritizing systemic fixes (Claim 8).
  7. **Data quality**: placeholder-bug-per-page, alert→bug links, 21-day
     trailing average (Claim 9).
  8. **Staffing & scheduling**: the 5/8 +1 staffing floor (Claim 11 — cite with
     the Prodcast discrepancy noted), ≤12h shift cap with 3-on/4-off variant
     (Claim 12), and the automated-scheduling invariant + peer-reviewed swaps
     (Claim 13).
  9. **Team dynamics**: the "empower ops" + fun-budget proposals (Claim 15) and
     the Mountain View bootstrap roadmap (training checklist, shadow-before-
     primary; Claim 16) as the new-rotation onboarding pattern.

- **Chapter 03 (runbooks-and-agents)**: Add Claim 6's deterministic-playbook→
  automate rule as the on-call-side statement of the "runbooks are executable
  spec" premise (already sourced from the eliminating-toil chapter's pseudocode
  claim). Add Claim 10's "automation informed by human-developed intent
  configuration" as the human-in-the-loop automation principle — the pre-agent
  authority for "humans set intent, automation executes with pre-flight safety
  checks." Add Claim 5's gated alert-introduction process as the test-then-
  approve gate any agent-added page must pass.

- **Chapter 01 (incident-response)**: Use the Evernote Sev1 escalation path
  (paged incident manager, scribe, communications lead — Claim 14) as a
  non-Google corroboration of the IMAG role structure already sourced from the
  incident-management note, and the response-time tiers (Claim 3) as the "when
  does this become an incident needing immediate action" decision rule.

- **AI/LLM relevance (measured)**: The source is pre-LLM-era (2018) with no
  AI content. The Smith should treat it as prerequisite practice knowledge for
  Ch04. The durable AI bridges, drawn by the Miner for review: (a) an AI
  first-responder agent operates under the same pager budget — agent-triggered
  pages consume the two-incident budget and must pass the same gated alert
  introduction (Claim 5); (b) the shadow→primary-with-backup bootstrap sequence
  (Claim 16) is the natural ramp for an agent (observe → act-with-human-backup →
  autonomous-with-escalation); (c) the data-quality discipline (alert→bug links,
  21-day average, Claim 9) is the governance every agent-triggered page needs;
  (d) the "automation informed by intent configuration" principle (Claim 10) is
  the lineage of the guide's "AI-assisted, not AI-native" position.

## Extraction Notes

- **Source read**: The workbook chapter at `https://sre.google/workbook/on-call`
  was fetched via `curl` (91 KB HTML), scripts/styles stripped, and converted to
  plain text (711 lines), then read end-to-end including the recap, both case
  studies, all sub-sections (Pager Load / On-Call Flexibility / On-Call Team
  Dynamics), the conclusion, and footnotes 1–5. It is a single self-contained
  page; no sub-pages needed. Per MINER.md §1 the linked SRE Book chapters
  (Being On-Call, Monitoring Distributed Systems) were not re-fetched — they are
  predecessor chapters, not substantive linked pages.
- **Quote verification**: All `Quote` fields and Concrete Artifact passages were
  copied character-for-character from the extracted page text. Two characters to
  note for the Assayer: the chapter uses em dashes in several passages
  ("24/7 follow-the-sun model" section uses "—"), and the "3 days on, 4 days
  off" quote contains an em dash ("less than a week—something like"). Verbatim
  fragments were kept contiguous per MINER.md §2a; the "point fix / systemic fix
  / monitoring fix" ladder is presented as attributed synthesis in Concrete
  Artifacts, with only the two quoted fragments verbatim.
- **Related-notes candidates (`miner-related-notes.md`) — dispositions**:
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response, no on-call rotation mechanics.
  - `docs-google-sre-configuration-specifics.md` — **Dismissed**; configuration
    toil (Workbook Ch15), not on-call.
  - `docs-google-sre-eliminating-toil.md` — **Cited** (see Cross-References):
    the 50% operational-work cap and runbook-automation claims corroborate
    Claims 1 and 6 here.
  - `docs-google-sre-prodcast.md` — **Dismissed**; podcast index page (structural
    S1E7→Ch11 map only; the substantive episode mining lives in
    `docs-google-sre-prodcast-01-07-on-call-rotations.md`, which is cited).
  - `docs-google-sre-data-processing-pipelines.md` — **Dismissed**; pipeline
    data-freshness SLOs, no on-call content.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` —
    **Dismissed**; incident-response tooling (primary+deputy parallel paging is
    a tooling design point, not rotation mechanics; the workbook's secondary-
    coordination mention in Table 8-1 is a response-time constraint, not the
    same claim).
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
    **Dismissed**; database reliability / overload economics.
  - `docs-google-sre-reliable-product-launches.md` — **Dismissed**; launch
    coordination, not on-call.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — **Dismissed**;
    org-scale economics of SRE.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**;
    AI-for-SRE tooling, not on-call practice.
- **Cross-reference verification**: All Claim numbers cited from
  `docs-google-sre-prodcast-01-07-on-call-rotations.md` (Claims 2, 3, 8, 9, 10,
  12), `docs-google-sre-eliminating-toil.md` (Claims 2, 3, 4),
  `docs-google-sre-prodcast-01-03-alerting.md` (Claims 5, 7),
  `docs-google-sre-incident-management-guide.md` (Claims 2, 4), and
  `docs-google-sre-canarying-releases.md` (Claim 5) were re-read and confirmed
  against those notes before citation, per MINER.md §4b.
- **Staffing discrepancy — no contradiction issue filed**: Per MINER.md §4a, the
  staffing-minimums gap between this chapter (5/site multisite, 8/site single-
  site, +1 buffer → 6/9) and the on-call-rotations note's ~12–14 dual-site
  minimum is a numerics discrepancy within the same scale from the same source
  family (authoritative workbook vs practitioner recollection that APW himself
  hedges as "I've lost track"), and both support the same order-of-magnitude
  guide advice. It is surfaced prominently under Claim 11 and in Cross-References
  rather than filed as a contradiction. No other opposition to existing notes was
  found.
- **Confidence rationale**: `confidence_overall: settled` — first-party Google
  SRE (and Evernote) published documentation of canonical on-call practice,
  consistent with the SRE Book and the rest of the corpus. No claims warranted
  `emerging` or `anecdotal`; the only nuance (staffing-minimums discrepancy) is
  handled above rather than graded down.
- The source predates the LLM era and contains no AI/LLM content; all AI/LLM
  applications in Guide Impact are the Miner's analytical bridge, to be reviewed
  by the Smith for fidelity.
