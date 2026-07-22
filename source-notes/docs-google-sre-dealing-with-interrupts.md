---
source_url: https://sre.google/resources/book-update/dealing-with-interrupts/
source_type: documentation
title: "Google SRE: Dealing with Interrupts — SRE Book Chapter 29 + Interrupt Reduction Projects Paper"
author: "Dave O'Connor (Chapter 29); Betsy Beyer, John Tobin, Liz Fong-Jones (Interrupt Reduction Projects, USENIX ;login: Winter 2016)"
date_published: 2016
date_extracted: 2026-07-22
last_checked: 2026-07-22
status: current
confidence_overall: settled
issue: "#411"
---

# Google SRE: Dealing with Interrupts — SRE Book Chapter 29 + Interrupt Reduction Projects

> A collection of interrupt-handling patterns from Google SRE: the three categories of
> operational load (pages, tickets, ongoing responsibilities), the primacy of cognitive
> flow state in engineering productivity, polarized time as the structural remedy for
> context-switch overhead, centralized ticket handling (not round-robin), and a
> dedicated "interrupt reduction project" role that actively reduces the ticket burden
> rather than passively cycling through it. Includes the Bigtable SRE ticket funnel
> case study (50% ticket reduction). Well-established SRE practice with no AI/LLM
> angle — foundational background for Ch04 (Oncall and Toil).

## Source Context

- **Type**: documentation — the landing page at `/resources/book-update/dealing-with-interrupts/`
  is a thin index page pointing to two substantive resources. Per MINER.md §1, both
  were followed and read deeply:
  1. **SRE Book Chapter 29 "Dealing with Interrupts"** (`/sre-book/dealing-with-interrupts/`)
     — the full book chapter (~12,000 words), read end-to-end.
  2. **"Interrupt Reduction Projects" by Betsy Beyer, John Tobin, Liz Fong-Jones**
     (USENICE ;login: Winter 2016, Vol. 41, No. 4, pp 57–62) — a companion paper
     available as PDF at `research.google.com/pubs/archive/45764.pdf`, read end-to-end.
- **Author credibility**: Highest-credibility for SRE practice. Dave O'Connor is a
  Google SRE and co-author of the SRE book. Betsy Beyer is a Technical Writer for
  Google SRE (editor of the SRE book series). John Tobin is an SRE manager at Google
  Dublin (Bigtable, Cloud Bigtable). Liz Fong-Jones is a Senior SRE Manager at Google
  (storage systems). The chapter is part of the official Google SRE Book (O'Reilly,
  2016), the canonical text on the discipline.
- **Scope**: Covers interrupt-handling patterns for on-call SRE teams: classification
  of operational load, management strategies for each load type (pages → primary/secondary
  on-call, tickets → dedicated rotation, ongoing responsibilities → role formalization),
  cognitive flow state theory, polarized time as the structural solution to context-switch
  overhead, ticket centralization vs round-robin assignment, the "interrupt reduction
  project" role as separate from ticket duty, the Bigtable ticket funnel case study,
  and policy-as-tool for managing interrupt burden. Does NOT cover AI/LLM-specific
  workloads, agent architectures, or any post-2016 automation patterns.

## Extracted Claims

### Claim 1: Operational load falls into three categories — pages (urgent, minutes), tickets (days to weeks), and ongoing operational responsibilities (unpredictable) — each with different urgency and SLO profiles
- **Evidence**: The chapter defines and categorizes all three. Pages carry expected response
  time SLOs measured in minutes; tickets have SLOs measured in hours/days/weeks; ongoing
  responsibilities (rollouts, flag flips, ad hoc questions) lack defined SLOs but can still
  interrupt. The companion paper uses the same three-way classification with identical
  urgency ranges.
- **Confidence**: settled
- **Quote**: "Pages... carry with them an expected response time, which is sometimes measured
  in minutes." — and — "Tickets may have SLOs, but they are more likely measured in hours,
  days, or weeks."
- **Our assessment**: A foundational taxonomy for organizing Ch04's on-call work types. The
  three categories map naturally to different automation strategies: AI agents are best
  suited for tickets (structured, time-flexible) and ongoing responsibilities (procedural),
  least suited for pages (fluid, high-stakes, requiring judgment).

### Claim 2: The primary on-call engineer should focus solely on on-call work — that week should be written off for project work; a person should never be expected to be on-call and also make progress on projects
- **Evidence**: The chapter states this as an emphatic directive. If the pager is quiet, the
  primary on-call can work on tickets or quickly-abandonable interrupt work, but not on
  project work with high context-switch cost. If a project is too important to slip by a
  week, that person shouldn't be on-call.
- **Confidence**: settled
- **Quote**: "A person should never be expected to be on-call and also make progress on
  projects (or anything else with a high context switching cost)." — and — "When an
  engineer is on-call for a week, that week should be written off as far as project work
  is concerned. If a project is too important to slip by a week, that person shouldn't
  be on-call."
- **Our assessment**: A clear, citable directive that directly supports the on-call vs
  on-duty split from the Prodcast 01-07 on-call rotations note (Claim 4). For the guide,
  this is the principle behind "AI handles the toil so the human can do the project work"
  — if the human on-caller can't do projects anyway, the question is whether AI reduces
  the on-call burden enough to change this calculus.

### Claim 3: Randomly distributing tickets across the team ("round-robin assignment") must stop — it is "extremely disrespectful of your team's time" and prevents cognitive flow
- **Evidence**: The chapter calls out this pattern explicitly and labels it harmful. The
  companion paper elaborates: it prevents engineers from entering cognitive flow for
  project work, while conversely, engineers engaged in heads-down project work miss
  ticket response expectations.
- **Confidence**: settled
- **Quote**: "if tickets are randomly assigned to team members, stop. This is extremely
  disrespectful of your team's time, and is completely counter to the idea of not being
  interruptible." — and (companion paper) — "spreading ticket load across an entire team
  causes context switches that impact valuable flow time"
- **Our assessment**: A strong, prescriptive anti-pattern for Ch04. The round-robin ticket
  model is common in small SRE teams. The chapter's recommendation — centralize onto a
  dedicated ticket handler — is the pattern to recommend in the guide. The strength of
  the language ("stop," "extremely disrespectful") makes this a quotable directive.

### Claim 4: Cognitive flow state ("the zone") is the primary productivity mechanism for engineering work; interruptions cause context-switch costs far exceeding the interrupt duration — a 20-minute interruption can cost hours of productive work
- **Evidence**: The chapter explains flow psychology (citing Wikipedia's Flow article),
  describes how being "in the zone" increases productivity and creativity, and quantifies
  the context-switch cost: "A 20-minute interruption while working on a project entails
  two context switches" — realistically "a loss of a couple hours of truly productive work."
- **Confidence**: settled
- **Quote**: "You want to maximize the amount of time spent in this state." — and —
  "A 20-minute interruption while working on a project entails two context switches. If
  you factor in the time to get back up to speed after being interrupted, it's a loss
  of a couple hours of truly productive work."
- **Our assessment**: The quantitative framing (20-min interrupt → hours lost) is the key
  actionable insight here. This gives on-call rotation designers a concrete cost to assign
  to interrupt-driven scheduling. The guide should cite this as the productivity argument
  for polarized time (Claim 5) and centralized ticket handling (Claims 3, 7).

### Claim 5: Polarized time — strictly separating project work and interrupt work into discrete time periods (ideally a week, minimally half a day) — is the structural solution to protect cognitive flow
- **Evidence**: The chapter recommends that teams polarize time: a person knows each day
  they're doing "just project work or just interrupts." The ideal period is a week, but
  a day or even half-day may be more practical. This aligns with the "make time" concept
  cited from Gra09.
- **Confidence**: settled
- **Quote**: "Polarizing time means that each day, a person knows they're doing just
  project work or just interrupts. They concentrate for longer periods, and don't get
  stressed out because they're being roped into tasks that drag them away from the work
  they're supposed to be doing."
- **Our assessment**: The practical mechanism behind Claim 2. The companion paper's
  interrupt reduction project role (Claim 7) is an implementation of polarized time at
  the rotation level. For the guide, polarized time is the structuring principle that
  both human and AI-augmented rotations should adopt.

### Claim 6: Google caps toil at ≤50% of total engineering time, with 60–70% as the target for project work
- **Evidence**: The companion paper states this as a formal guideline for Google SRE teams.
  The paper also notes that tickets/interrupts are classified as toil, and that reducing
  toil is essential for teams to expand scope and undertake more interesting project work.
- **Confidence**: settled
- **Quote**: "We cap toil at a maximum of 50% of a team's total engineering time, with the
  expectation that most teams will instead spend 60–70% of their time on project work."
- **Our assessment**: This is a more specific toil cap than the "50% cap" commonly cited
  from the SRE Book. The companion paper draws a direct line between ticket/interrupt
  load and the toil cap, making interrupts a primary target for toil reduction. Directly
  relevant to Ch04's toil measurement framework.

### Claim 7: The effective model is (a) one dedicated ticket handler plus (b) a separate "interrupt reduction project on duty" role — the latter works on small-to-medium projects (20–30 hours) that eliminate root causes of tickets
- **Evidence**: The companion paper describes this as Bigtable SRE's implemented model.
  Key results: "most of the time, one dedicated ticket handler can resolve all tickets,
  which frees up one person's time for interrupt reduction projects"; "we complete
  approximately three of these small strategic interrupt reduction projects every four weeks."
  The chapter also emphasizes formalizing handoff processes for these roles.
- **Confidence**: settled
- **Quote**: "we explicitly allocated this job, which we'll refer to as 'interrupt reduction
  project on duty,' as a separate role from ticket work." — and — "It hits the sweet spot
  of undertaking small to medium-sized projects to reduce operational load — projects that
  require more than 30 minutes of attention, but are too small to account for on a
  quarterly planning cycle."
- **Our assessment**: The companion paper's key structural contribution: not just centralizing
  tickets, but creating a *second* dedicated role for eliminating tickets at their root.
  The 3-projects-per-4-weeks velocity is a measurable baseline. For the guide, this is the
  strongest pattern for the "AI reduces toil" framing: the interrupt reduction project role
  is exactly the kind of work that AI agents could assist with (analyzing ticket patterns,
  suggesting automatable root causes, drafting documentation).

### Claim 8: Bigtable SRE's ticket funnel — a simple web decision tree guiding customers to self-service automation or documentation — cut ticket creation rate by roughly half (from 30+ to 15+ per week)
- **Evidence**: The companion paper's case study. A two-week project built a web interface
  with a decision tree. Non-leaf nodes ask questions; leaf nodes either link to
  automation/documentation or generate a ticket. Results: ticket creation dropped from
  30+ to 15+ per week; customer satisfaction surveys improved; fewer easily-resolvable
  tickets were filed.
- **Confidence**: settled
- **Quote**: "Building a simple ticket funnel system to guide customers to appropriate
  automation or documentation was a natural choice for our first interrupt reduction
  project." — and — "Figure 4 shows that the ticket creation rate dropped by roughly
  half after we implemented the ticket funnel, from 30+ to 15+ per week."
- **Our assessment**: A concrete, quantified case study of interrupt reduction through
  automation. The specific mechanism — redirecting customers to self-service before they
  can file a ticket — is directly applicable to LLM API support: a similarly structured
  funnel for common inference issues (timeouts, rate limits, model selection) could
  reduce support tickets. The "two weeks to build" timescale makes it an achievable
  reference project for Ch04.

### Claim 9: Teams should conduct regular scrubs of tickets and pages to identify root causes — if fixable in reasonable time, silence the interrupts until the root cause is fixed
- **Evidence**: The chapter explicitly recommends this as a proactive interrupt-reduction
  practice. It contrasts the common pattern of on-call handoffs and page reviews with
  the infrequent practice of ticket scrubs. The companion paper reinforces this: "it's
  much easier to handle a ticket if the process is documented, and documentation is a
  good first step towards automating a process."
- **Confidence**: settled
- **Quote**: "Lots of teams conduct on-call handoffs and page reviews. Very few teams do
  the same for tickets." — and — "silence the interrupts until the root cause is expected
  to be fixed"
- **Our assessment**: The asymmetry the chapter identifies (tickets get less analysis than
  pages) is a practical observation that the guide can use to recommend structured ticket
  reviews. The companion paper's approach — using metadata (cause, impact, time to fix)
  to identify recurring issues — is the concrete implementation.

### Claim 10: Policy can be as powerful a tool as code for managing interrupt load; teams set the level of service and can push effort back to customers through policy
- **Evidence**: The chapter argues that policy decisions (temporary or permanent) can make
  workload more manageable. Concrete examples: giving back the pager for a flaky component,
  deprecating it, or requiring customers to execute preparatory steps before submitting a
  ticket. "if the customer wants a certain task to be accomplished, they should be prepared
  to spend some effort getting what they want."
- **Confidence**: settled
- **Quote**: "Policy can be as powerful a tool as code." — and — "Your team sets the level
  of service provided by your service. It's OK to push back some of the effort onto your
  customers."
- **Our assessment**: A counterpoint to the guide's automation-heavy framing. Sometimes the
  best solution to interrupt overload is a policy change (deprecating an under-resourced
  component, raising the bar for ticket eligibility) rather than a technical fix. The
  "policy as tool" framing broadens the interrupt-reduction toolkit beyond AI/automation.

### Claim 11: Engineers can achieve cognitive flow in both "creative/engaged" project mode and "Angry Birds" interrupt-handling mode; a balance between the two types of work makes people happier
- **Evidence**: The chapter describes two flow modalities: creative flow (losing track of
  time working on a difficult problem) and "Angry Birds" flow (repetitive, know-how-to-do-it
  work that is nonetheless satisfying — e.g., chasing down on-call problems). When someone
  concentrates full-time on interrupts, "interrupts stop being interrupts."
- **Confidence**: settled
- **Quote**: "many people in SRE-type roles spend much of their time either trying and
  failing to get into this mode and getting frustrated when they cannot, or never even
  attempting to reach this mode, instead languishing in the interrupted state." — and —
  "people are ultimately happier with a balance between these two types of work"
- **Our assessment**: A nuanced claim that recognizes interrupt work can itself be a source
  of flow and satisfaction. This tempers the guide's anti-toil framing: not all interrupt
  work is bad, and the goal is balance, not elimination. The "Angry Birds flow" framing
  is a useful vocabulary item for Ch04.

### Claim 12: Four concrete components for an interrupt-handling strategy: (1) centralize ticket load, (2) track interrupt reduction project ideas, (3) reserve time for small proactive projects (20–30 hours), (4) treat tickets and interrupt reduction as separate rotations
- **Evidence**: The companion paper summarizes these four components as the lessons
  "implemented by multiple storage-related services at Google." The chapter similarly
  provides piecemeal-implementable components: dedicated ticket handler, push manager
  role, formalized handoffs, regular scrubs.
- **Confidence**: settled
- **Quote**: "Our recommendations for approaching tickets/interrupts, which have been
  implemented by multiple storage-related services at Google, include four concrete
  components: Centralize your ticket load... Track ideas for small interrupt reduction
  projects... Put a framework in place that reserves time for small (20–30 hours)
  proactive projects... Treat tickets and small proactive interrupt reduction projects as
  separate rotations, distributed among team members and sites on a regular basis."
- **Our assessment**: A directly actionable, numbered strategy that Ch04 can present as
  the canonical interrupt-reduction playbook. The four components are implementation
  independent (they apply to human-only, AI-assisted, and AI-led rotations equally).
  The 20–30 hour sizing for interrupt reduction projects is a usefully specific estimate.

## Concrete Artifacts

### Artifact A — The three categories of operational load (SRE Book Ch29)

```
Category                    Urgency              SLO                  Examples
──────────────────────────────────────────────────────────────────────────────────
Pages (production alerts)   Immediate           Minutes               Production emergencies,
                                                                      monitoring-triggered incidents
Tickets                     Hours to weeks      Hours, days, weeks    Customer requests, config reviews,
                                                                      capacity plan consultations
Ongoing responsibilities    Unpredictable       None (ad hoc)         Code/flag rollouts, ad hoc
                                                                      time-sensitive customer questions
```

### Artifact B — Bigtable SRE Ticket Funnel case study metrics (companion paper, verbatim)

```
- Tickets per week (mid-2015):      20+ (increasing to 30+ over previous year)
- Tickets per week (post-funnel):   15+ (roughly half the pre-funnel rate)
- Project duration:                 ~2 weeks (though discussed for 2 years prior)
- Mechanism:                        Web interface decision tree → self-service or ticket
- Customer impact:                  Quarterly satisfaction surveys showed happier customers;
                                    fewer tickets resolvable by pointing at automation/docs
```

*Source: Beyer, Tobin, Fong-Jones, "Interrupt Reduction Projects," USENIX ;login: Winter 2016, pp 60–61 (case study section).*

### Artifact C — Interrupt reduction project tactics (companion paper, verbatim)

```
Project ideas come from two main sources:
  - Current/past ticket handlers who file annoyances into a bug hotlist
  - Technical Leads (TLs) who have a high-level view of the service

Project assignment:
  - TL sorts ideas by impact (more ideas than engineering time)
  - Let people choose from the top 10 (preserve autonomy)
  - Bleed-over from last week gets finished first

Handling excess ticket load:
  - Option 1: Task interrupt reduction person with tickets 1 day/week
  - Option 2: Relax ticket response expectations until the work pays off
```

*Source: Beyer, Tobin, Fong-Jones, "Interrupt Reduction Projects," USENIX ;login: Winter 2016, p 60 (Implementation Details section).*

### Artifact D — The four-component interrupt-handling strategy (companion paper, verbatim)

```
1. Centralize your ticket load, either onto engineers who are already expecting
   interruptions (e.g., primary or secondary on-call) or to a dedicated ticket
   duty rotation.
2. Track ideas for small interrupt reduction projects that will reduce toil.
3. Put a framework in place that reserves time for small (20–30 hours) proactive
   projects.
4. Treat tickets and small proactive interrupt reduction projects as separate
   rotations, distributed among team members and sites on a regular basis.
```

*Source: Beyer, Tobin, Fong-Jones, "Interrupt Reduction Projects," USENIX ;login: Winter 2016, p 62 (Takeaways section).*

### Artifact E — Suggested interrupt reduction projects (companion paper, verbatim)

```
1. Identify the Sources of Your Toil
   Consider adding metadata (e.g., cause, impact, time to fix) to tickets to
   help determine recurring issues and your biggest time sinks.

2. Improve Your Documentation
   "It's much easier to handle a ticket if the process is documented, and
   documentation is a good first step towards automating a process."
   Provide a standard template to overcome the "blank page effect."

3. Pick the 10 Most Annoying Small Bugs and Fix Them
   "Your team should be creating lists of bugs for the rough edges,
   shortcomings, and difficulties encountered in the course of everyday
   work — otherwise those problems will never be fixed."
   Choose commonly encountered bugs related to one or two systems so that
   progress is noticeable.
```

*Source: Beyer, Tobin, Fong-Jones, "Interrupt Reduction Projects," USENIX ;login: Winter 2016, p 62 (Suggested Interrupt Reduction Projects section).*

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` **Claim 4** (on-call vs on-duty
    split — the on-caller should not also do ticket/support "crank turning") — this note's
    Claim 2 (primary on-call focuses solely on on-call work) and Claim 5 (polarized time)
    directly corroborate APW's on-call/on-duty distinction. Where APW recommends it,
    this source provides the cognitive-flow rationale and the quantitative context-switch
    cost (20-min interrupt → hours lost).
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` **Claim 5** (prefer a single
    primary + secondary, not two co-primaries) — the chapter's recommendation for a
    single primary on-call who handles pages (Claim 2 here) with a secondary backup aligns
    with APW's primary/secondary model and the "avoid bystander effect" rationale.
  - `docs-google-sre-handling-overload.md` **Claim 6** (autoscaling kill switches must be
    easy, obvious, fast, and well-documented — a CPU-consuming bug can waste all quota) —
    this note's companion paper similarly identifies ticket volume as something that
    "spiral[s] out of control" if not proactively reduced; both sources warn of
    uncontrolled growth consuming engineering capacity.
  - `docs-google-sre-prodcast-01-08-incident-management.md` **Claim 10** (prevention-first:
    "do as little incident response as possible") — the companion paper's interrupt
    reduction projects (Claim 7 here) are the ticket-equivalent of prevention-first:
    actively eliminating ticket root causes rather than passively cycling through them.

- **Contradicts**: None identified. All claims are consistent with existing source notes
  and with established SRE canon. One potential tension — the chapter states primary
  on-call should do zero project work (Claim 2), while APW (on-call rotations note,
  Claim 4) says he "personally prefers coding while on-call" — is not a contradiction:
  APW explicitly frames this as his personal preference, not a recommendation, and the
  chapter's guidance is about team structure and role design, not individual working
  style. The two are compatible: a primary on-caller *may* code during quiet periods
  (as the chapter acknowledges with "if the pager is quiet, tickets or other quickly-
  abandonable interrupt work can be part of duties"), but the team should not *expect*
  project progress from the on-caller. No contradiction issue filed.

- **Extends**:
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` — that note covers on-call
    rotation *design* (who is on-call, shift models, fatigue limits). This note provides
    the *interrupt handling* counterpart: what on-call engineers actually do with their
    on-call time (pages, tickets, ongoing responsibilities) and how to structure ticket
    work to preserve cognitive flow. Together the two notes give Ch04 a complete on-call
    practice picture.
  - `docs-google-sre-handling-overload.md` — that note covers overload *at the system
    level* (load shedding, autoscaling, capacity planning). This note covers overload
    *at the human level* (interrupt management, cognitive flow, ticket reduction). The
    two are complementary: system-level overload and human-level interrupt overload are
    distinct failure modes that Ch04 should address separately.
  - `docs-google-sre-prodcast-06-03-handling-burnout.md` — that note's "treat yourself
    as a reliable system" metaphor (Claim 2) is the personal-scale analog of this note's
    organizational-scale interrupt management. The interrupt reduction projects (Claim 7
    here) and regular ticket scrubs (Claim 9) are organizational mechanisms that prevent
    the burn-out conditions described in the burnout note.

- **Novel**: Material new to the corpus:
  - **The complete three-category operational load taxonomy** with urgency/SLO profiles
    (Claim 1) — no existing note defines pages/tickets/ongoing-responsibilities as a
    unified framework.
  - **The "primary on-call = no project work" directive** (Claim 2) — a citable, quotable
    prescription for role design.
  - **The quantitative context-switch cost** (20-min interrupt → hours lost, Claim 4) —
    a specific, teachable metric for arguing against interrupt-driven scheduling.
  - **Polarized time as a structural pattern** (Claim 5) — the language for separating
    project and interrupt work into discrete blocks.
  - **The 50% toil cap with 60–70% project target** (Claim 6) — a more specific and
    citable version of the general SRE toil cap.
  - **The interrupt reduction project role** (Claim 7) — a named, dedicated rotation for
    eliminating ticket root causes, distinct from ticket handling. The 3-projects-per-
    4-weeks velocity is a measurable baseline.
  - **Bigtable ticket funnel case study** (Claim 8) — quantified evidence (50% ticket
    reduction from a 2-week project) for self-service ticket deflection.
  - **The "ticket scrubs are rare, page reviews are common" asymmetry** (Claim 9) —
    a specific gap the guide can recommend filling.
  - **Policy-as-tool for interrupt management** (Claim 10) — a non-automation lever for
    interrupt reduction.
  - **"Angry Birds flow"** (Claim 11) — the vocabulary for describing how interrupt work
    can itself be a source of satisfaction, tempering the anti-toil framing.
  - **Four-component interrupt-handling strategy** (Claim 12) — an actionable, numbered
    playbook for Ch04.
  - **The three concrete suggested interrupt reduction projects** (Artifact E: identify
    toil sources, improve documentation, fix 10 most annoying small bugs).

## Guide Impact

- **Chapter 04 (Oncall and Toil)**: The most impacted chapter. Currently Ch04 is a stub
  with no sourced claims. This note supplies the chapter's first foundational material:
  1. **Operational load taxonomy** (Claim 1) — structure the chapter around the three
     categories (pages, tickets, ongoing responsibilities), each with its own management
     strategy and AI-augmentation potential.
  2. **Primary on-call = no project work** (Claim 2) — add as a design principle for
     on-call role definition. This is the human-side complement to the on-call/on-duty
     split from the on-call rotations note (Claim 4 there).
  3. **Stop round-robin tickets** (Claim 3) — add as an anti-pattern with the strong
     "extremely disrespectful" language for emphasis.
  4. **Polarized time** (Claim 5) — add as the recommended structuring principle for
     the team's week: separate interrupt blocks from project blocks, ideally at day
     granularity.
  5. **Toil cap + project target** (Claim 6) — add to the toil measurement section as
     a specific, citable target.
  6. **Interrupt reduction project role** (Claim 7) — this is the strongest pattern
     for Ch04's "AI reduces toil" framing. Recommend that teams staff a dedicated
     rotation for eliminating ticket root causes. The 3-projects-per-4-weeks velocity
     from the case study gives teams a benchmark. AI agents could assist by: analyzing
     ticket metadata for common patterns, suggesting documentation improvements, and
     generating initial automation for recurring ticket types.
  7. **Ticket funnel pattern** (Claim 8) — add the Bigtable case study as a reference
     implementation for ticket deflection via self-service. Note the AI/LLM translation:
     an LLM-powered support chatbot that answers common questions before they become
     tickets is the modern version of this funnel.
  8. **Regular ticket scrubs** (Claim 9) — add as a recommended practice, paired with
     the "silence interrupts until root cause fixed" guidance.
  9. **Policy-as-tool** (Claim 10) — add as a non-automation lever in the interrupt
     reduction toolkit, broadening beyond the AI/automation focus.
  10. **Four-component strategy** (Claim 12) — present as the chapter's interrupt-
      reduction playbook.
  11. **Suggested interrupt reduction projects** (Artifact E) — add as a concrete,
      copyable list for teams to adapt.

- **Chapter 00 (Principles)**: Add Claim 11's "Angry Birds flow" and "balance between
  work types" as a nuance to the SRE principles: the goal is balanced work, not the
  elimination of all interrupt work. Add the "policy as tool" principle (Claim 10) to
  the principles chapter's tooling section.

## Extraction Notes

- **Dual-source structure**: The landing page at `https://sre.google/resources/book-update/dealing-with-interrupts/`
  is thin (only the heading "29. Dealing with Interrupts" and a link to the full chapter
  plus the companion paper). Per MINER.md §1, both substantive linked resources were
  followed and read deeply:
  1. **SRE Book Chapter 29** (`/sre-book/dealing-with-interrupts/`) — the full chapter,
     read end-to-end. All quotes from the chapter are character-for-character from the
     fetched page content.
  2. **"Interrupt Reduction Projects"** (USENIX ;login: Winter 2016) — the 6-page PDF
     at `research.google.com/pubs/archive/45764.pdf`, downloaded and read end-to-end.
     All quotes from the paper are character-for-character from the PDF text extraction.
- **No AI/LLM content**: Both sources predate the LLM era. AI/LLM applications in Guide
  Impact (ticket funnel → LLM support chatbot, interrupt reduction projects → AI-assisted
  analysis) are the Miner's analytical bridge, to be reviewed by the Smith for fidelity.
- **Confidence rationale**: `confidence_overall: settled` — both are official Google SRE
  publications (SRE Book chapter and USENIX paper by Google SRE authors), claims are
  well-evidenced with case studies and metrics, and the patterns are established SRE
  knowledge. No claims required `anecdotal` grading.
- **No contradiction filed**: No claim in either source opposes any existing source note.
  The primary-on-call vs coding recommendation tension noted in Cross-References is a
  conditioning-variable difference (personal preference vs team structure), not a true
  contradiction. Per MINER.md §4a, no contradiction issue is warranted.
- **Cross-reference verification**: Claim numbers cited from `docs-google-sre-prodcast-01-07-on-call-rotations.md`
  (Claims 4, 5), `docs-google-sre-handling-overload.md` (Claim 6),
  `docs-google-sre-prodcast-01-08-incident-management.md` (Claim 10), and
  `docs-google-sre-prodcast-06-03-handling-burnout.md` (Claim 2) were re-read and verified
  before citation. All remaining cross-references reference the cited note thematically
  rather than by claim number, clearly identified as such.
