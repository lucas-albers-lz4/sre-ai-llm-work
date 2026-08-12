---
source_url: https://sre.google/workbook/reaching-beyond
source_type: documentation
title: "Google SRE: Reaching Beyond Your Walls — SRE Workbook Chapter 19"
author: "Dave Rensin, with Betsy Beyer, Niall Richard Murphy, and Liz Fong-Jones"
date_published: 2018
date_extracted: 2026-08-12
last_checked: 2026-08-12
status: current
confidence_overall: settled
issue: "#885"
---

# Google SRE: Reaching Beyond Your Walls — SRE Workbook Chapter 19

> The canonical statement of the platform-reliability *partnership*: for any
> API- or platform-bearing system, the reliability a tenant experiences is a
> joint product of platform and customer choices (peak-end rule; the
> 99.999% × 99% → 98.999% ceiling math), so the platform must "do SRE with your
> customers" via a concrete five-step engagement methodology — SLO/SLI
> alignment, monitoring audit + shared dashboards, measure-and-renegotiate
> ("five 9s" myth), design reviews ranked by error-budget consumption, and
> joint practice — plus explicit customer-selection frameworks
> (revenue/feature/workload coverage). Directly transferable to how an LLM
> inference-platform team runs reliability with downstream LLM-app tenants.

## Source Context

- **Type**: documentation — SRE Workbook (O'Reilly, 2018) Chapter 19 "SRE:
  Reaching Beyond Your Walls," published at
  `sre.google/workbook/reaching-beyond/`. This is the sibling chapter to
  Workbook Ch18 "SRE Engagement Model": Ch18 covers how SRE engages
  *internal* dev/product teams; Ch19 covers how SRE engages *external
  customers/tenants* of a platform.
- **Author credibility**: Highest available. Lead author Dave Rensin (Google
  SRE), with Betsy Beyer, Niall Richard Murphy, and Liz Fong-Jones. The
  chapter's "Truths We Hold to Be Self-Evident" section is based on Rensin's
  SREcon17 Americas talk (linked from the page). First-party statement of
  Google's own platform-reliability practice, published on the official
  sre.google domain.
- **Scope**: Covers (a) six "self-evident" truths (reliability as the most
  important feature; users-not-monitoring decide reliability; platform
  reliability as a partnership; everything becomes a platform; customer break/
  fix as innovation-budget absorption; the need to practice SRE with
  customers); (b) the 5-step "How to: SRE with Your Customers" methodology;
  (c) customer-selection frameworks (revenue/feature/workload coverage). Does
  NOT cover LLM/agent-specific workloads directly — it is the general
  platform-tenant reliability framework the guide maps onto LLM inference
  platforms. Pre-LLM-era (2018) source; the AI transfer is the Miner's
  synthesis, flagged in Guide Impact.

## Extracted Claims

### Claim 1: Reliability is the most important feature of any system — because users won't trust (then won't use) an unreliable system, network effects make a userless system worthless, and "you are what you measure, so choose your metrics carefully"
- **Evidence**: The "Reliability Is the Most Important Feature" argument list:
  untrustworthy systems lose users, network effects amplify that loss, and the
  "you are what you measure" close links reliability to measurement choice. The
  author acknowledges "reliability" covers a wide area.
- **Confidence**: settled
- **Quote**: "If a system isn't reliable, users won't trust it. If users don't trust a system, when given a choice, they won't use it. Since all software systems are governed by network effects, if a system has no users, it's worth nothing. You are what you measure, so choose your metrics carefully."
- **Our assessment**: The chapter's axiomatic opening. The "you are what you
  measure" step is the load-bearing one for the guide: it justifies the whole
  five-step methodology (align the customer's measurements with their actual
  SLOs) and transfers directly to LLM platforms — a model provider that
  measures only p95 latency while tenants measure token-quality failures is
  measuring the wrong thing.

### Claim 2: Your users, not your monitoring, decide your reliability — the only reliability measure that matters is the user's experienced reliability; telling a worried user "our monitoring looks fine" doesn't change their perception (the peak-end rule), and monitoring/logs/alerting are valuable only insofar as they notice problems before customers do
- **Evidence**: The "Your Users, Not Your Monitoring, Decide Your Reliability"
  section; the "peak-end rule" (linked to Wikipedia) is invoked to explain why
  the user's remembered experience (peak + end) governs their choice between
  the platform and a competitor.
- **Confidence**: settled
- **Quote**: "If your user is worried that your platform is responsible for instability they're experiencing, then telling them "our monitoring looks fine; the problem must be on your end" won't make them any less grumpy." — and — "Your monitoring, logs, and alerting are valuable only insofar as they help you notice problems before your customers do."
- **Our assessment**: The chapter's sharpest principle and the direct rationale
  for the customer-SRE engagement program that follows. For LLM platforms this
  is decisive: a tenant's application can be failing on quality/latency in ways
  the provider's serving dashboards never see, and the tenant will blame the
  platform regardless of provider-side metrics — exactly the argument the
  corpus's AI-era Detectr note makes (see Cross-References).

### Claim 3: If you run a platform, reliability is a partnership — once you add an API, your users' experienced reliability is not limited to your choices; a customer system at 99% availability caps their best-case experience at 98.99901% even when the platform itself runs at 99.999%
- **Evidence**: The "If You Run a Platform, Then Reliability Is a Partnership"
  section, including the multiplication example (linked to a CACM piece, "The
  Calculus of Service Availability"). The UI-only case (real human beings only)
  keeps reliability almost entirely on the platform; the API case transfers
  part of it to the tenant.
- **Confidence**: settled
- **Quote**: "When your product acts as a platform, the reliability your users experience isn't limited to the choices you make. Reliability becomes a partnership." — and — "If your users build or operate a system on your platform that never achieves better than 99% availability—even if you're running your platform at 99.999% availability—then their best-case experience is 98.99901%."
- **Our assessment**: The central quantitative claim. The multiplication is
  simple (99.999% × 99% ≈ 98.999%), but the conclusion — the platform must
  engage the tenant's *own* reliability, not just its own — is the structural
  argument the guide's platform-reliability material needs. For an LLM
  inference provider: a downstream app's 99% wrapper/app reliability caps its
  users' experience regardless of how many 9s the model endpoint holds, so the
  provider's reliability ceiling is partly owned by tenants' systems.

### Claim 4: Everything important eventually becomes a platform — machine-consumable APIs are inevitable; if you never build an official API, someone will wrap your UI into one, and you'll have no control over the outcome
- **Evidence**: The "Everything Important Eventually Becomes a Platform"
  section: integration is "an inevitable step in your evolution"; the
  screen-scraping fallback is invoked for platforms that refuse an API.
- **Confidence**: settled
- **Quote**: "Even if you decide that you don't care about other user communities, and decide to never create a machine-consumable API, you still won't be able to avoid this future. Other people will simply wrap your UI into a machine API and consume it." — and — "Once your system becomes a gateway to a large collection of users, it becomes valuable. APIs—official or unofficial—will be a part of your future."
- **Our assessment**: A strategic claim that widens the chapter's audience from
  explicit platforms to anything popular: the reliability-partnership rules
  apply even to systems that never intended to be platforms. For the guide this
  argues that any widely-used LLM product (including agent UIs) should expect a
  machine-consumption surface and plan for the partnership model rather than
  treating API access as an opt-in afterthought.

### Claim 5: When customers have a hard time, you have to slow down — energy spent helping users through difficult moments is energy not invested in advancing your system; teams that let time be "slowly absorbed" by break/fix customer problems are "consumed by toil," and this applies doubly to internal platform teams
- **Evidence**: The "When Your Customers Have a Hard Time, You Have to Slow
  Down" section; it explicitly extends to internal platform teams ("this doubly
  applies to you!") and points to the Eliminating Toil workbook chapter for the
  way out ("Once in this state, it's hard to dig out… A better plan is to get
  ahead of the impending toil").
- **Confidence**: settled
- **Quote**: "Whatever energy you put into helping users past their difficult moments is energy you can't invest in advancing your system. We have seen many teams (and companies) allow their time to be slowly absorbed by break/fix customer problems—leaving an ever-diminishing innovation budget. These teams are consumed by toil."
- **Our assessment**: The toil-absorption mechanism that ties this chapter to
  Ch04's toil material: customer break/fix work is the *demand side* of the
  toil budget, and it silently shrinks the innovation budget before anyone
  measures it. The internal-team extension matters for LLM platforms, where
  tenant debugging of inference quality/latency is the modern break/fix sink.
  The "get ahead of the impending toil" directive is the stated motivation for
  the 5-step program — the 5-step program *is* the toil-avoidance investment.

### Claim 6: You will need to practice SRE with your customers — you must teach customers to design and operate reliable systems on your platform, and "do SRE" with at least a representative sample of users: undertake most of the work leading up to pager handoff (minimum viable reliability requirements) without necessarily taking the pagers
- **Evidence**: The "You Will Need to Practice SRE with Your Customers"
  section; one-to-many content (books, docs, diagrams) is insufficient because
  it goes stale, so "the best way to learn these lessons is to 'do SRE' with
  your customers."
- **Confidence**: settled
- **Quote**: "That doesn't necessarily mean you need to take the pagers for your customers' systems, but you do need to undertake most of the work that normally leads up to pager handoff (meaning the system has met certain minimum viable reliability requirements), with at least a representative sample of your users."
- **Our assessment**: The chapter's thesis. The "minimum viable reliability
  requirements before pager handoff" framing is a concrete gate: the platform
  team's engagement ends where tenant systems become independently operable.
  For the guide this is the boundary between platform-owned and tenant-owned
  reliability — and the "representative sample" qualifier is what makes the
  engagement scalable (see Claim 12).

### Claim 7: Step 1 — SLOs and SLIs are how you speak to customers: in the absence of a stated SLO, a customer will inevitably invent one and not tell you until you don't meet it; the fix is to sit down, explain SLOs/SLIs/error budgets, and help customers describe their critical applications in those terms
- **Evidence**: The "Step 1: SLOs and SLIs Are How You Speak" section, with the
  two worked conversation transcripts (a circular performance complaint without
  SLOs vs a budget-burn conversation with them). The SLO conversation "will
  happen only when the SLO is threatened, and… relies on mutually understood
  metrics (SLIs) and targets (SLOs)."
- **Confidence**: settled
- **Quote**: "Remember, in the absence of a stated SLO, your customer will inevitably invent one and not tell you until you don't meet it!"
- **Our assessment**: The "invented SLO" claim is the chapter's most quotable
  behavioral insight: customers will form reliability expectations regardless,
  so unstated expectations are worse than explicit ones because they surface as
  surprise escalations. For LLM platforms this maps directly to tenant
  expectations about model quality, latency, and availability — the provider
  should help tenants state them rather than leave them implicit.

### Claim 8: Step 2 — Audit the customer's monitoring and build shared dashboards: up to half of the things a customer measures (and alerts on) have zero impact on their SLOs; the remaining measurements are candidate SLIs, uncovered SLO dimensions need new measurements, and a shared SLO dashboard should make SLO-threatened conversations information-free
- **Evidence**: The "Step 2: Audit the Monitoring and Build Shared Dashboards"
  section. The half-of-measurements figure is stated as the authors' direct
  experience; the shared-dashboard goal is stated as the "no additional
  information swapping" test.
- **Confidence**: settled
- **Quote**: "In our experience, up to half of the things your customer is measuring (and alerting on) have zero impact on their SLOs." — and — "Your goal is that whenever your customer contacts you because their SLO seems threatened, you shouldn't have to swap much additional information. All of that information should be in the shared monitoring."
- **Our assessment**: A concrete, citable audit heuristic (≈half of tenant
  alerting is SLO-irrelevant — turning it off reduces pages for both parties)
  and a concrete deliverable (shared SLO dashboards as the interface that makes
  customer-platform communication self-service). For LLM platforms the audit
  analog is tenant telemetry for quality/latency/cost SLIs: much of what tenants
  alert on (token counts, generic p95) may not track their stated app SLOs.

### Claim 9: Step 3 — Measure and renegotiate: customers who believe they're operating at "five 9s" usually measure only 99.5%–99.9% against real SLOs; if users are happy and no evidence shows availability/performance gains would increase adoption, retention, or usage, the renegotiation is done
- **Evidence**: The "Step 3: Measure and Renegotiate" section: collect data for
  "a month or two," expect the rude awakening, then point out "their users
  aren't yelling all the time, so they probably never needed the five 9s they
  haven't really been getting." The "you're done" criterion is user
  satisfaction plus no adoption/retention/usage upside.
- **Confidence**: settled
- **Quote**: "The application they thought was operating at "five 9s" (99.999%; everybody thinks they're getting five 9s) is probably achieving only 99.5%–99.9% when measured against their shiny new SLOs." — and — "If their users are happy, and there's no evidence that improving performance or availability will increase user adoption/retention/usage, then you're done."
- **Our assessment**: Two claims in one: (a) the measured-vs-believed reliability
  gap is systematic ("everybody thinks they're getting five 9s"), and (b) the
  renegotiation criterion is *user satisfaction plus business evidence*, not an
  abstract availability target — the same "the target is a product question"
  doctrine the corpus already carries, now applied to the platform-customer
  relationship. For LLM tenants: model quality SLOs should be set against
  whether users stop using the app, not against a fixed "5 nines" of inference.

### Claim 10: Step 4 — Design reviews and risk analysis: audit the customer's application for hidden SPOFs and manual rollouts/rollbacks, rank the findings by error-budget consumption, and watch which fixes the customer chooses to "earn back the 9s" — the choices reveal how customers consume the platform
- **Evidence**: The "Step 4: Design Reviews and Risk Analysis" section. The
  review reveals how customers consume the platform, what reliability mistakes
  they make, and which tradeoffs they pick; it also "help[s] your customer set
  realistic expectations" so trust is earned.
- **Confidence**: settled
- **Quote**: "Next, rank the issues you find by how much of their error budget each item consumes." — and — "Pay attention to which items your customer chooses to fix in order to "earn back the 9s" they want (e.g., to move from 99.5% to 99.9%)."
- **Our assessment**: The error-budget-ranking method is the customer-facing
  analogue of the internal risk analysis the guide already covers (SPOF audit,
  manual-change detection); the "earn back the 9s" observation makes the
  customer's choices the diagnostic signal for how they consume the platform.
  For LLM platforms the analogous review is a tenant-app audit (prompt paths,
  single-region inference, no fallbacks) ranked by how much of the tenant's
  quality/availability budget each flaw consumes.

### Claim 11: Step 5 — Practice, practice, practice: run Wheel of Misfortune exercises, disaster-recovery tests, and paper game days with customers; build cross-team crisis-communication muscle memory (builds trust, lowers MTTR, surfaces edge cases to fold into platform features); and conduct joint postmortems rather than just sharing yours
- **Evidence**: The "Step 5: Practice, Practice, Practice" section, with links
  to the LISA15 disaster-recovery-testing talk and Google Cloud's shared-
  postmortem guidance. Joint postmortems "build trust and teach you some
  invaluable lessons."
- **Confidence**: settled
- **Quote**: "Practice simulated problems (Wheel of Misfortune exercises, disaster and recovery testing, paper game days, etc.)." — and — "When an incident does occur, don't just share your postmortems with your customer. Actually conduct some joint postmortems."
- **Our assessment**: The practice steps are the same incident-response
  machinery the corpus already sources for internal teams (Wheel of Misfortune,
  game days), now extended across the platform/tenant boundary. The "integrate
  edge cases as enhancements into your platform features" loop is the mechanism
  by which tenant pain becomes platform roadmap — high value for LLM platforms
  where tenant-side agent failures often trace to provider-side gaps.

### Claim 12: Be thoughtful and disciplined about customer selection — it becomes impossible to run these steps with more than a small percentage of customers; pick one coverage framework (revenue / feature / workload coverage) and stick to it, because mixing approaches confuses stakeholders and overwhelms the team
- **Evidence**: The "Be Thoughtful and Disciplined" section: three named
  selection approaches with their fit conditions (revenue-weighted large
  customers; feature coverage for diverse platforms; workload cohorts for
  usage-dominated platforms) and the explicit don't-mix warning.
- **Confidence**: settled
- **Quote**: "It will quickly become impossible to carry out these steps with more than a small percentage of your customers. Please don't try extending this model to everyone." — and — "Whatever approach you choose, stick to it. Mixing and matching will confuse your stakeholders and quickly overwhelm your team."
- **Our assessment**: The scarcity framing mirrors the sibling Ch18 engagement
  model (SRE capacity is limited, so engagement selection must be principled).
  The three frameworks are a concrete, citable selection menu; for an LLM
  inference platform, revenue coverage (largest tenant spend) or workload
  coverage (agent-traffic cohorts) are the natural analogues. The don't-mix
  warning is the operational guardrail.

## Concrete Artifacts

### Artifact A — The two conversation transcripts (verbatim, from Step 1)

```
WITHOUT SLOs (the circular, effort-consuming conversation):
  Customer: "API call X usually takes time T, but now it's taking time U. I
            think you are having a problem. Please look into it and get back
            to me immediately."
  You:      "That performance seems in line with what we expect, and everything
            looks fine on our end. Is it a problem if API call X takes this
            long?"
  Customer: "I don't know. It doesn't usually take this long, so obviously
            something has changed and we're worried about it."

WITH SLOs (the budget conversation):
  Customer: "We're burning through our SLO for application FOO too quickly and
            the application is in jeopardy. SLIs X and Y seem to have fallen
            off a cliff. They both depend on your API X."
  You:      "Okay. Let me look into how API X is performing in our system
            and/or how it's performing specific to you."
— SRE Workbook Ch19, "Step 1: SLOs and SLIs Are How You Speak"
```

### Artifact B — The 5-step customer-SRE journey (verbatim-condensed from the chapter)

```
Step 1  SLOs and SLIs are how you speak: explain SLOs/SLIs/error budgets and
        help customers describe their critical applications in those terms.
Step 2  Audit the monitoring and build shared dashboards: ~half of what the
        customer measures/alert-on has zero SLO impact; cover uncovered SLO
        dimensions; build shared SLO dashboards so "you shouldn't have to swap
        much additional information."
Step 3  Measure and renegotiate: collect data for "a month or two"; the
        "five 9s" claim usually measures 99.5%–99.9%; done when users are
        happy and there's no adoption/retention/usage upside.
Step 4  Design reviews and risk analysis: audit for hidden SPOFs and manual
        rollouts/rollbacks; "rank the issues you find by how much of their
        error budget each item consumes"; watch what customers choose to fix
        to "earn back the 9s."
Step 5  Practice, practice, practice: Wheel of Misfortune, disaster-recovery
        testing, paper game days; build crisis-communication muscle memory
        (trust, lower MTTR, platform-feature edge cases); conduct joint
        postmortems, don't just share yours.
```

### Artifact C — The reliability-partnership math (verbatim from the chapter)

```
Platform at 99.999% availability × customer system at 99% availability
  ⇒ customer's best-case experience is 98.99901%.
Reasoning: the customer's users hit the customer's system first; the platform
  only sees the requests that get there. The customer's choices (their own
  availability) set the ceiling on the experience they associate with your
  service.
```

### Artifact D — Customer-selection frameworks (verbatim-condensed from "Be Thoughtful and Disciplined")

```
Revenue coverage    Select the minimum number of customers to account for XX%
                    of your revenue. Right when revenue is heavily weighted to
                    a few large customers.
Feature coverage    Select the minimum number of customers to cover more than
                    XX% of your platform features. Right for highly diverse
                    platforms with a long tail of customers doing different
                    things.
Workload coverage   Sample one or two customers from each usage cohort
                    (distinct use cases/customer types), to get platform
                    coverage and discover operational differences between use
                    cases.

Rule: "Whatever approach you choose, stick to it. Mixing and matching will
confuse your stakeholders and quickly overwhelm your team."
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-eliminating-toil.md` **Claim 3** (Google caps SRE teams'
    operational work at 50%; identifying/quantifying toil is the first step
    toward optimization) — this chapter's break/fix absorption mechanism
    (Claim 5 here) is the demand-side input to that cap: customer support work
    is toil that must be budgeted like any other operational work, and "get
    ahead of the impending toil" is the chapter's own cross-reference to the
    eliminating-toil chapter. The two notes are explicitly linked in the
    source.
  - `discussion-google-sre-prodcast-customer-centric-monitoring.md` **Claim 11**
    ("we no longer assume that five 9s of availability represent the overall
    experience for all the customers") — Esparrachiari's long-tail evolution of
    Google observability corroborates Claim 9 here (the five-9s assumption is
    systematically wrong when you look at real customers). **Claim 3** (a broad
    availability number hides *who* is observing the errors) corroborates
    Claims 2 and 7 here (measure the way the customer experiences it; the
    customer's own SLIs, not aggregate provider metrics, are the unit of
    discussion).
  - `docs-google-sre-prodcast-01-04-rethinking-slos.md` **Claim 2** ("no one
    wants to be in the error budget… they're paying money for a service that
    they depend on") — Desai's B2B/paying-customer critique of canonical error
    budgets is the SLO-skeptic statement of why platform-tenant SLO alignment
    (Steps 1–3 here) must be done *with* the customer rather than imposed:
    tenants won't accept being silently inside the provider's budget. Both
    sources are conditioning-variable-compatible (platform/B2B context), not
    opposed (see Contradicts).
  - `docs-google-sre-ai-engineering-reliable-operations.md` **Claim 8** (Detectr
    — a Gemini-powered user-feedback outage-detection platform that catches
    novel issues traditional monitoring misses, adopted across Cloud/Ads/
    YouTube/Search) — Detectr is the AI-era implementation of Claim 2 here
    ("your users, not your monitoring, decide your reliability"): Google now
    literally reads user feedback to detect outages its dashboards miss. The
    whitepaper note is 2025; this 2018 chapter is the doctrinal ancestor.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 1**
    (incident-response tooling includes monitoring, observability, dashboards,
    and the customer-support interface) — corroborates Step 2's shared SLO
    dashboards (Claim 8 here) and Step 5's joint postmortems (Claim 11 here):
    the "customer-support interface" the tooling note names is exactly the
    shared-monitoring surface this chapter prescribes.

- **Contradicts**: None that meets the MINER.md §4a bar. One *conditioning
  variable* tension to surface: this chapter's Step 1 — SLOs/SLIs are how you
  speak with customers (Claim 7 here) — vs
  `docs-google-sre-prodcast-02-08-life-beyond-google.md` **Claim 5** ("Don't
  start a reliability program with SLOs — start with basics… or teams 'get mad
  about not knowing how their systems are performing'"). These are different
  populations: the Xoogler panel advises orgs that lack production hygiene and
  need basics first; this chapter advises platform teams whose customers are
  *already mid-stream* operating apps on the platform, where unstated tenant
  expectations are already being formed ("in the absence of a stated SLO, your
  customer will inevitably invent one"). Same doctrine as the sibling Ch18 note
  — the guide should present both with their maturity context. Per MINER.md §4a
  no contradiction issue is filed; this matches the corpus's prior handling of
  the same tension in `docs-google-sre-engagement-model.md` (Contradicts
  section). No `contradiction`-labeled issue or `C-NNN` entry covers this
  chapter's content.

- **Extends**:
  - `docs-google-sre-engagement-model.md` (Workbook Ch18) — the sibling note
    covers the *internal* dev/product engagement lifecycle (7-phase model, NYT
    shared-goals, ground rules, scaling, hand-back). This chapter is the
    *external/tenant* layer: same scarcity framing (Ch18 Claim 1 "must decide
    where to focus their attention" ↔ Claim 12 here "impossible to carry out
    these steps with more than a small percentage of your customers"), same
    SLO/error-budget machinery, but the engagement partner is the paying
    tenant rather than the internal developer. Together they give the guide the
    full engagement portfolio: internal engagement model + external
    customer-SRE program.
  - `docs-google-sre-prodcast-04-10-platform-engineering.md` **Claim 8**
    (deployment archetypes encode failure-domain understanding behind a simple
    "big or small" dropdown so users can't accidentally pick a
    single-failure-domain layout) — this chapter supplies the *why* behind
    that platform design: because a tenant's choices set the ceiling on their
    experienced reliability (Claim 3 here), the platform must encode
    reliability decisions into the consumption surface rather than leave them
    to tenant freedom. The archetype dropdown is the platform's side of the
    partnership; this chapter is the doctrine.
  - `docs-google-sre-ai-engineering-reliable-operations.md` — beyond Claim 8's
    direct corroboration, the whitepaper's whole safety-control-plane design
    (Claims 2–5) is the agent-era continuation of this chapter's "do SRE with
    your customers": the autonomy/risk machinery is what a modern LLM platform
    would run *with* its tenants rather than purely internally.
  - `docs-google-sre-prodcast-01-04-rethinking-slos.md` — Desai's stationarity/
    variance framing (Claims 15–16) extends this chapter's "measure the way the
    customer experiences it" (Claim 2 here) with a statistical model: a
    platform's tenant-facing reliability should be judged on a *stable
    distribution* of the tenant's experienced behavior, not a mean availability
    number — the measurement layer the 2018 chapter's SLO-alignment step
    anticipates but does not build.

- **Novel**: Material new to the corpus:
  - **The "your users, not your monitoring, decide your reliability" principle
    with the peak-end rule** (Claim 2) — no existing note states the peak-end
    rule or the "monitoring is valuable only insofar as it notices problems
    before customers do" framing.
  - **The platform-reliability-partnership math** (Claim 3) — the
    99.999% × 99% → 98.99901% ceiling argument and its conclusion that
    platform reliability is a joint product with tenants. No existing note
    carries the multiplication or the partnership framing.
  - **"Everything important eventually becomes a platform"** (Claim 4) — the
    API-inevitability argument including the UI-scraping fallback.
  - **The break/fix → innovation-budget → toil absorption mechanism**
    (Claim 5) — customer support work as a toil source, with the "doubly
    applies to internal platform teams" extension.
  - **"Do SRE with your customers" / minimum-viable-reliability-before-pager-
    handoff** (Claim 6) — the engagement-boundary concept (where platform work
    ends and tenant ownership begins).
  - **The "invented SLO" behavioral claim** (Claim 7) — "in the absence of a
    stated SLO, your customer will inevitably invent one and not tell you until
    you don't meet it."
  - **The "up to half of what customers measure/alert on has zero SLO impact"
    audit heuristic** and the **shared-SLO-dashboard deliverable** (Claim 8).
  - **The five-9s myth quantification** (99.5%–99.9% actual; Claim 9) and the
    **user-satisfaction-plus-adoption "you're done" renegotiation criterion**.
  - **The error-budget-ranking design-review method and the "earn back the 9s"
    diagnostic** (Claim 10).
  - **The three customer-selection frameworks** (revenue / feature / workload
    coverage) with the explicit don't-mix warning (Claim 12).

## Guide Impact

- **Chapter 00 (principles)**: Add the "your users, not your monitoring, decide
  your reliability" principle with the peak-end rule (Claim 2) as a founding
  reliability axiom — the guide's principles chapter currently has no statement
  of who the arbiter of reliability is. Add "reliability is the most important
  feature… you are what you measure" (Claim 1) and the platform-reliability-
  partnership doctrine (Claim 3) as the principled basis for the platform
  chapters' tenant coverage. Recommend the Smith weigh this against
  `docs-google-sre-prodcast-02-08-life-beyond-google.md` Claim 5 (don't start
  with SLOs) as a maturity-conditioned pair, not a conflict.

- **Chapter 02 (observability)**: Add the customer-SLO alignment step (Claim 7)
  and the monitoring-audit heuristic — "up to half of the things your customer
  is measuring (and alerting on) have zero impact on their SLOs" (Claim 8) —
  as the platform-side observability practice: audit tenant telemetry against
  tenant SLIs, turn off SLO-irrelevant alerting, and build shared SLO
  dashboards so customer-platform conversations are information-free. This is
  the direct template for an LLM platform's shared tenant dashboard (quality/
  latency/cost SLIs). Cross-reference the Detectr claim (ai-engineering Claim 8)
  as the AI-era user-feedback layer on top of shared dashboards.

- **Chapter 04 (oncall-and-toil)**: Add the break/fix absorption mechanism
  (Claim 5) — customer support time consuming the innovation budget and feeding
  toil, with the internal-platform-team extension — as a demand-side input to
  the toil budget, complementing the eliminating-toil note's 50% operational-
  work cap (its Claim 3). Add the "minimum viable reliability requirements
  before pager handoff" gate (Claim 6) as the boundary deciding when tenant
  systems may enter (or stay out of) the platform team's on-call scope — a
  concrete admission criterion the chapter's on-call coverage lacks.

- **Chapter 01 (incident response)**: Add the joint-practice and joint-
  postmortem requirements (Claim 11) — Wheel of Misfortune / disaster-recovery
  tests / paper game days run *across* the platform-tenant boundary, and joint
  postmortems instead of shared ones — as the incident-response layer of the
  platform partnership, with the "edge cases fold back into platform features"
  loop as the feedback mechanism. Corroborates the incident-tooling note's
  Claim 1 (the customer-support interface is part of the tooling surface).

- **Chapter 05 (llm-ops-reliability)**: The primary AI-transfer target. Frame
  the LLM inference platform as a reliability *partnership* with downstream
  LLM-app tenants using the multiplication math (Claim 3): a tenant's app-level
  99% caps their users' experience regardless of endpoint 9s, so the provider
  must "do SRE with its tenants." Adopt the 5-step customer-SRE methodology
  (Claims 7–11, Artifacts A–B) as the engagement program an LLM platform runs
  with tenant teams — SLO/SLI alignment on quality/latency/cost, tenant
  monitoring audit + shared dashboards, measure-and-renegotiate against the
  five-9s myth (Claim 9), design reviews ranked by error-budget consumption
  (Claim 10), and joint game days/postmortems (Claim 11). Adopt the
  customer-selection frameworks (Claim 12, Artifact D) — revenue or workload
  (agent-traffic cohort) coverage, never mixed — as the sizing rule for which
  tenants get the full engagement. Use the "invented SLO" claim (Claim 7) as
  the argument for proactively stating model-quality/latency/availability
  expectations to tenants.

## Extraction Notes

- **Source read**: The chapter at
  `https://sre.google/workbook/reaching-beyond` was fetched via WebFetch and
  read end-to-end (all six "Truths We Hold to Be Self-Evident" sections, all
  five steps of "How to: SRE with Your Customers," the "Be Thoughtful and
  Disciplined" selection section, and the conclusion). It is a single
  self-contained page. Per MINER.md §1 the linked pages (SREcon17 talk, CACM
  "Calculus of Service Availability," the GCP blog posts on shared postmortems
  and "know thy enemy," the LISA15 disaster-recovery talk, the O'Reilly SLO
  book, the Wikipedia peak-end rule) were evaluated: they are supporting
  references behind hyperlinks, not substantive sub-pages with additional
  methodology — the chapter's claims stand alone. No sub-pages were followed.
- **Quote verification**: All `Quote` fields and Artifact A/C/D passages were
  copied character-for-character from the fetched page text, contiguous
  fragments per MINER.md §2a. Note the source uses nested double quotes
  (e.g., 'telling them "our monitoring looks fine; the problem must be on your
  end"'), the "99.5%–99.9%" en dash, and the em-dash in "98.99901%" passage
  ("99% availability—even if you're running…"); these were preserved verbatim.
  The Claim 6 quote is one contiguous sentence from the pager-handoff passage.
- **Related-notes candidates (`miner-related-notes.md`) — dispositions**:
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response, no platform/tenant reliability
    partnership content.
  - `docs-google-sre-configuration-specifics.md` — **Dismissed**;
    configuration toil and DSLs, unrelated to platform-customer engagement.
  - `docs-google-sre-eliminating-toil.md` — **Cited** (Claim 3, operational-
    work cap); the source itself links to the eliminating-toil chapter — see
    Corroborates.
  - `docs-google-sre-on-call.md` — **Cited** (section-level): that note covers
    on-call rotation mechanics; this chapter supplies the *prerequisite* (the
    "minimum viable reliability requirements" work leading up to pager handoff,
    Claim 6 here) that decides which systems ever reach the on-call scope the
    Ch8 note assumes. No numbered-claim citation — the connection is
    cross-chapter framing, not a shared claim.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` — **Cited** (Claim
    5, don't-start-with-SLOs) as the conditioning-variable pair for Step 1 —
    see Contradicts.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
    **Dismissed**; databases and reliability culture, unrelated.
  - `docs-google-sre-data-processing-pipelines.md` — **Dismissed**; pipeline
    SLO formats and pipeline reliability, no platform-tenant engagement content.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — **Cited**
    (Claim 1, tooling breadth incl. customer-support interface) — see
    Corroborates.
  - `docs-google-sre-handling-overload.md` — **Dismissed**; load shedding and
    thundering herds, unrelated.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**;
    AI-for-SRE tooling (support-case early outage detection is adjacent to
    Claim 2 here, but the Detectr claim in
    `docs-google-sre-ai-engineering-reliable-operations.md` covers the
    user-feedback-detection thesis more directly and is cited instead).
- **Additional cross-refs beyond candidates**: `docs-google-sre-engagement-
  model.md` (sibling Ch18, internal engagement), `docs-google-sre-ai-engineering-
  reliable-operations.md` (Detectr, AI-era user-perception detection),
  `docs-google-sre-prodcast-04-10-platform-engineering.md` (deployment
  archetypes), `docs-google-sre-prodcast-01-04-rethinking-slos.md` (B2B error
  budgets, stationarity), and `discussion-google-sre-prodcast-customer-centric-
  monitoring.md` (five-9s assumption, broad-availability critique) — all
  verified claim-by-claim per MINER.md §4b before citation.
- **Contradiction analysis (per MINER.md §4a)**: No contradiction issue filed.
  The Step 1 SLO-first advice vs the life-beyond-Google "don't start with SLOs"
  advice is a maturity-conditioning-variable difference, handled the same way
  the sibling Ch18 note handled the identical tension. No existing
  `contradiction`-labeled issue or `C-NNN` entry in CONTRADICTIONS.md covers
  this chapter. `confidence_overall` is `settled`: the source is canonical
  first-party Google SRE documentation by named authors describing Google's own
  established practice; the quantitative claims (half-of-measurements, five-9s
  gap, 98.99901% ceiling) are stated as the authors' direct experience. All
  AI/LLM extensions in Guide Impact are the Miner's synthesis and should be
  reviewed by the Smith for fidelity.
