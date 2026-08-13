---
source_url: https://sre.google/workbook/slo-engineering-case-studies
source_type: documentation
title: "SLO Engineering Case Studies — SRE Workbook Chapter 3"
author: "Ben McCormack (Evernote) and William Bonnell (The Home Depot), with Garrett Plasky, Alex Hidalgo, Betsy Beyer, and Dave Rensin"
date_published: 2018
date_extracted: 2026-08-13
last_checked: 2026-08-13
status: current
confidence_overall: settled
issue: "#906"
---

# SLO Engineering Case Studies — SRE Workbook Chapter 3

> Two practitioner case studies of SLO/error-budget adoption — Evernote (SLOs
> introduced after a move to GCP, a deliberately simple first uptime SLO, and a
> shared-SLO partnership that broke the customer/cloud-provider "SLO wall") and
> The Home Depot (a four-part culture change — vernacular, evangelism,
> automation, incentive — that took an SLO program from 0 to 800 services in
> less than a year via the VALET framework). Supplies concrete, enterprise-scale
> evidence for *how* SLO programs actually get adopted, complementing the
> Prodcast adoption-pattern notes (S5E2) and the SLO-skeptic critique (S1E4).

## Source Context

- **Type**: documentation — Chapter 3 "SLO Engineering Case Studies" of the
  Site Reliability Engineering Workbook (O'Reilly, 2018), published at
  `sre.google/workbook/slo-engineering-case-studies/`, licensed CC BY-NC-ND
  4.0. The chapter sits between Ch2 "Implementing SLOs" and Ch4 "Monitoring"
  and is the only case-study chapter in the workbook's Foundations section.
- **Author credibility**: Highest available for enterprise SLO adoption. Two
  named practitioner-authors from the case-study companies — Ben McCormack
  (Evernote) and William Bonnell (The Home Depot) — writing their own
  company's journey, with Garrett Plasky (Evernote), Alex Hidalgo (Google CRE,
  author of *Implementing Service Level Objectives*), Betsy Beyer, and Dave
  Rensin (Google SRE) as contributing editors. The Evernote half is
  first-party; the THD half is first-party; Alex Hidalgo and Dave Rensin also
  anchor two sibling corpus notes (S5E2 Prodcast; reaching-beyond-walls). This
  is the CRE (Customer Reliability Engineering) perspective that Google runs
  SLO engagements with cloud customers — the chapter explicitly opens with the
  CRE origin ("almost every customer interaction starts and ends with SLOs").
- **Scope**: Covers two complete SLO-adoption journeys: Evernote's move off
  physical datacenters to GCP, its deliberately simple first uptime SLO, its
  measurement design, its SLO-driven prioritization, and its shared-SLO
  partnership with GCP; THD's move to microservices with full-stack ownership,
  its four-part "SLO Culture Project" (vernacular, evangelism, automation,
  incentive), the VALET framework (Volume/Availability/Latency/Errors/Tickets),
  its BigQuery-based TPS Reports automation, the 0→800-service scaling, batch
  and chaos-testing applications, and future error-budget aspirations. Does NOT
  cover SLO statistics/math (that is Ch2 Implementing SLOs, a separate page),
  nor AI/LLM workloads directly (2018-era source; the LLM transfer is the
  Miner's synthesis, flagged in Guide Impact).

## Extracted Claims

### Claim 1: Evernote's SLO adoption was embedded in a wider technology revamp — stop running physical datacenters and move to a public cloud, revise the ops/dev working model for feature velocity, and revamp how SLAs are viewed — at a scale of 220M+ users, 12B+ stored items, and 750+ MySQL instances
- **Evidence**: The chapter's goals list for the revamp and the scale figures
  given in the opening paragraph. Evernote framed SLOs as part of the GCP
  migration ("Once the Evernote service was up and running on GCP and
  stabilized, we introduced SLOs"), not as a standalone metric program.
- **Confidence**: settled
- **Quote**: "With more than 220 million users worldwide, we store over 12 billion pieces of information—a mix of text-based notes, files, and attachments/images—within the platform. Behind the scenes, the Evernote service is supported by 750+ MySQL instances."
- **Also**: "Move engineering focus away from undifferentiated heavy lifting in datacenters and toward product engineering work that customers actually cared about. To that end, we stopped running our physical datacenters and moved to a public cloud."
- **Our assessment**: The "undifferentiated heavy lifting in datacenters" phrasing is a toil-reduction motivation (cf. the eliminating-toil note's "consume the innovation budget" framing) — SLOs were adopted as part of a migration-and-velocity program, not in isolation. The scale figures give the guide a citable "SLOs work at consumer scale" data point, though self-reported. Settled.

### Claim 2: Evernote failed at "You wrote it, you run it" and "You wrote it, we run it for you" before settling on SLO-centric SRE, which embraces rather than erases the ops/dev difference and gives both teams a common frame of reference — the error budget removes subjectivity so both teams make similar decisions from the same facts
- **Evidence**: The chapter recounts five-plus years of attempts to fix the
  traditional ops/dev split, the two named failed models, and then the
  SLO-centric model, with the mechanism stated explicitly.
- **Confidence**: settled
- **Quote**: "After trying out a "You wrote it, you run it" (development) model, and a "You wrote it, we run it for you" (operations) model, we moved toward an SLO-centric SRE approach."
- **Also**: "It does not try to transform operations engineers into application developers, or vice versa. Instead, it gives both a common frame of reference. In our experience, an error budget/SLO approach has led both teams to make similar decisions when presented with the same facts, as it removes a good deal of subjectivity from the conversation."
- **Our assessment**: A concrete, first-party account of the exact mechanism the corpus already claims abstractly: SLOs/error budgets as the *shared vernacular* that aligns dev and ops (S5E2 Claim 1) and as the resolution to the ops/dev chasm (Treynor's "throw it over the wall" problem). The empirical claim — both teams "make similar decisions when presented with the same facts" — is the strongest direct evidence in the corpus that the SLO mechanism works as designed outside Google. Settled as a documented case study.

### Claim 3: Evernote started SLO design from the customers' point of view and deliberately kept its first pass simple — one uptime SLO of 99.95% over a calendar-month window for "certain services and methods," written into a document that specified the definition, what/how to measure, and how to calculate the SLO from monitoring data
- **Evidence**: The "Introduction of SLOs" section walks the first SLO document
  bullet-by-bullet (definition; what to measure; how to measure; how to
  calculate from monitoring data). The calendar-month choice over a rolling
  window is explicitly motivated.
- **Confidence**: settled
- **Quote**: "We wanted to ensure we initially focused on the most important and common customer need: the availability of the Evernote service for users to access and sync their content across multiple clients. Our SLO journey started from that goal. We kept our first pass simple by focusing on uptime."
- **Also**: "This was an uptime measure: 99.95% uptime measured over a monthly window, set for certain services and methods." — and — "We deliberately chose to bind our SLOs to a calendar month versus a rolling period to keep us focused and organized when running service reviews."
- **Our assessment**: The calendar-month-vs-rolling decision is a concrete, citable design choice the corpus doesn't otherwise record (the error-budget-policy sibling appendix and THD both weigh the same axis; see Claim 15). The customer-first start ("what promises are you trying to uphold") corroborates the customer-centric monitoring note's user-goal-first thesis and the reaching-beyond-walls "SLOs are how you speak to customers" step. Settled.

### Claim 4: Evernote's SLO measurement used an external third-party prober (Pingdom) polling frontend nodes every minute from multiple probes across North America and Europe, with a node marked "down" only after two geographically separate probe failures — and maintenance windows were treated as downtime because uninformed users experience them as unexplained downtime
- **Evidence**: The "What to measure, and how to measure it" subsection details
  the prober location rationale, frequency, locations, the two-check down
  definition, and the maintenance-window accounting rule.
- **Confidence**: settled
- **Quote**: "We wanted that prober to be located completely outside of and independent from our environment so we could test all our components, including our load balancing stack."
- **Also**: "If a prober check fails, the node is marked as Unconfirmed Down and then a second geographically separate prober performs a check. If the second check fails, the node is marked down for SLO calculation purposes." — and — "we could not assume that all of our hundreds of millions of users knew about our published maintenance windows. Uninformed users would therefore experience these windows as generic and unexplained downtime, so our SLO calculations treated maintenance as downtime."
- **Our assessment**: Two durable SLI-measurement artifacts for the guide's Ch02 material: (1) the two-location-confirmation rule for declaring "down" (kills single-prober false positives while staying outside the measured environment), and (2) maintenance-as-downtime — measuring what *users* experience rather than what was operationally announced. The second is a precise instance of the corpus's "users, not your monitoring, decide your reliability" principle (reaching-beyond-walls Claim 2). Settled.

### Claim 5: Evernote used SLO/error budgets to allocate resources — missed-SLO last month prioritizes fixes at a monthly Evernote/Google SLO review with outage deep dives — and governed SLO evolution with the principle "Perfect is the enemy of good": two revisions in nine months, a six-month review cycle, and a 2017 compressed-release case where SLO quantification cut release windows from five to two
- **Evidence**: The "Once we defined our SLOs" section describes the monthly
  review and resource-allocation use; the "Introduction of SLOs" and "Current
  State" sections give the revision count, the review cycle, and the 2017
  release example.
- **Confidence**: settled
- **Quote**: "We use the SLO/error budget concept as a method to allocate resources going forward. For example, if we missed the SLO for last month, that behavior helps us prioritize relevant fixes, improvements, and bug fixes."
- **Also**: "Throughout this process, our guiding principle has been "Perfect is the enemy of good." Even when SLOs aren't perfect, they're good enough to guide improvements over time." — and — "we've settled on a six-month SLO review cycle, which strikes the right balance between changing SLOs too often and letting them become stale." — and — "By applying an SLO calculation to the problem and removing human subjectivity from the scenario, we were able to better quantify customer impact and reduce our release windows from five to two to minimize customer pain."
- **Our assessment**: The six-month review cycle is an independently-derived instance of the revisit-cadence pattern (S5E2 Claim 10 recommends quarterly/bi-annual), and "Perfect is the enemy of good" operationalizes Desai's "validate and iterate" (S1E4 Claim 8) — start coarse, revise on signal. The 2017 release-window example is the rare concrete *quantified outcome* of SLO-driven decision-making in the corpus (5 windows → 2). Settled.

### Claim 6: Evernote broke the "SLO wall" between customer and cloud provider: a provider's global SLO rollup can hide region-isolated outages for a small-footprint tenant (GCP's 99.95% Compute Engine SLO "lost" Evernote's regional outages in the global rollup), so Evernote shared real-time SLO performance and dashboards with the Google CRE team, received SLO-impact-quantified notifications, and treated high-SLO-impact incidents as mutual P1s on a shared conference bridge
- **Evidence**: The "Breaking Down the SLO Wall" section describes the rollup
  blind spot, the shared-dashboard practice, the example notification, and the
  P1-with-special-handling agreement.
- **Confidence**: settled
- **Quote**: "a given cloud provider probably runs hundreds of thousands of virtual machines globally, which they manage for uptime and availability. GCP promises 99.95% availability for Compute Engine (i.e., its virtual machines). Even when GCP SLO graphs are green (i.e., above 99.95%), Evernote's view of the same SLO might be very different: because our virtual machine footprint is only a small percentage of the global GCP number, outages isolated to our region (or isolated for other reasons) may be "lost" in the overall rollup to a global level."
- **Also**: "we share our SLO and real-time performance against SLO with Google. As a result, both the Google CRE team and Evernote work with same performance dashboards." — and — "in addition to a generic "GCP load balancing environment is running slow today," we'll also be informed that this issue is causing a 5% impact to Evernote's SLO." — and — "We have a common understanding that if the SLO impact is high enough, both parties will treat the issue as a P1 ticket with special handling."
- **Our assessment**: The single most novel and reusable artifact in the Evernote half: a worked demonstration of the platform-reliability partnership claim (reaching-beyond-walls Claim 3 — the tenant's experienced reliability is not limited to the provider's choices) and of the shared-dashboard engagement step (reaching-beyond-walls Claim 8). The "global rollup hides regional outages" mechanism is a precise failure mode of aggregate SLOs — the same averaging-away problem Desai critiques from the B2B angle (S1E4 Claim 3). Directly transferable to LLM inference platforms: a tenant with a small prompt/region footprint can be invisible in a provider's global model-quality SLO. Settled.

### Claim 7: THD moved from centralized support teams for monolithic software to small, independently operated microservice teams under a "freedom and responsibility culture" of full-stack ownership — developers free to push code but jointly responsible for operations — requiring SLOs as the common language; before the program, monitoring was scattered, the root service of an outage was unidentifiable, and support tickets were the closest thing to a customer-facing SLO
- **Evidence**: The chapter's opening THD sections give the pre-state
  disconnects, the microservices + full-stack-ownership move, and the role of
  SLOs in the joint-ownership model.
- **Confidence**: settled
- **Quote**: "Our move to microservices was complemented by a move to a new "freedom and responsibility culture" of full-stack ownership. This approach gives developers freedom to push code when they want, but also makes them jointly responsible for the operations of their service. For this model of joint ownership to work, operations and development teams need to speak a common language that promotes accountability and cuts across complexity: service level objectives."
- **Also**: "Monitoring tools and dashboards were plentiful, but were scattered everywhere and didn't track data over time. We weren't always able to pinpoint the service at the root of a given outage." — and — "The primary (and only) way we measured the reliability of the applications deployed to our stores was by tracking the number of support calls our internal support desk receives."
- **Our assessment**: THD is the corpus's best real-world instantiation of the "team that writes AND runs the code owns the SLOs" principle (S5E2 Claim 3) — full-stack ownership is the org design that makes it structurally true. The "support tickets as the closest metric to a customer-facing SLO" pre-state is a precise articulation of the tickets-as-reliability-proxy failure the eliminating-toil note documents (ticket toil as the human interface to the machine). Settled.

### Claim 8: THD's "SLO Culture Project" spanned four areas — common vernacular, evangelism, automation, incentive — grounded in an inventory of existing metrics that mapped to Google's Four Golden Signals (volume, latency, errors, utilization) but were "inconsistently monitored, were named differently, or had insufficient data"
- **Evidence**: The "SLO Culture Project" section enumerates the four areas,
  the Four Golden Signals mapping, and the metric-quality audit finding.
- **Confidence**: settled
- **Quote**: "Our efforts spanned four general areas: Common vernacular, Evangelism, Automation, Incentive."
- **Also**: "Every service monitored some form of its traffic volume, latency, errors, and utilization—metrics that map closely to Google SRE's Four Golden Signals." — and — "Unfortunately, across the board, all categories of metrics were inconsistently monitored, were named differently, or had insufficient data."
- **Our assessment**: The four-area frame (vernacular / evangelism / automation / incentive) is a complete, citable organizational-change checklist for standing up an SLO program — and it independently converges on the corpus's "name a champion + central practice team + revisit cadence" adoption patterns (S5E2 Claims 6-7, 10). The "inconsistently monitored, named differently, had insufficient data" audit is exactly the "you are what you measure, so choose your metrics carefully" (reaching-beyond-walls Claim 1) failure state that the reaching-beyond-walls Step-2 audit ("up to half of what you measure has zero impact on your SLOs") is designed to fix. Settled.

### Claim 9: THD's first SLOs were per-microservice availability and latency SLOs for internal API calls, published so dependents could consult them; THD explicitly declined utilization SLOs (users don't care about utilization if traffic is handled) and set traffic-volume SLOs sized to expected peak capacity for retailer peaks like Black Friday
- **Evidence**: The "Our First Set of SLOs" section walks the decision for each
  metric category (availability/latency for internal APIs, no utilization,
  traffic volume to peak).
- **Confidence**: settled
- **Quote**: "We decided that each microservice had to have availability and latency SLOs for its API calls that were called by other microservices."
- **Also**: "We decided against setting utilization SLOs for a few reasons. To begin with, microservices aren't overly concerned with this metric—your users don't really care about utilization as long as you can handle the traffic volume, your microservice is up, it's responding quickly, it's not throwing errors, and you're not in danger of running out of capacity." — and — "as a retailer we needed to size our service for peaks like Black Friday, so we set an SLO according to expected peak capacity."
- **Our assessment**: The published-SLOs-for-dependents pattern is the microservice instantiation of SLOs as a *cross-team contract* between producers and consumers — S5E2's "your users might be the team down the hall" (Claim 4) made concrete. The decline-of-utilization-SLOs rationale matches Furino's caveat that system-health/saturation SLIs have only a bounded role (S4E5 Claim 6) — THD reached the same boundary independently. The peak-capacity (Black Friday) SLO is a business-shaped SLO the guide can cite for capacity-gated SLOs. Settled.

### Claim 10: THD's latency SLOs required percentiles over arithmetic averages (minimum 90th percentile; user-facing services 95th and/or 99th) plus a black-box supplement to white-box monitoring; THD standardized errors on HTTP codes (no errors in 2xx bodies; 4xx = client, 5xx = service), tracked both 4xx and 5xx but set SLOs on 5xx only; the five categories were summed into the VALET acronym (Volume, Availability, Latency, Errors, Tickets)
- **Evidence**: The "Latency" and "Errors" subsections plus the VALET section.
  Tickets are described as a sixth dimension "analogous to something like
  'software operation level.'"
- **Confidence**: settled
- **Quote**: "We also decided that percentiles were more appropriate than arithmetic averages. At minimum, services needed to hit a 90th percentile target; user-facing services had a preferred target of 95th and/or 99th percentile."
- **Also**: "A service should not indicate an error in the body of a 2xx response; rather, it should throw either a 4xx or a 5xx." — and — "After much deliberation, we decided to track both 4xx and 5xx errors, but used 5xx errors only to set SLOs." — and — "You can consider this metric as analogous to something like "software operation level.""
- **Our assessment**: Concrete, adoption-ready SLI decisions: percentile-over-average latency (the guide's latency-SLO default; corroborates Desai's "take variance seriously" via the distribution framing), 5xx-only error SLOs with 4xx tracking (client errors excluded from the SLO but still tracked), and black-box supplementation. The VALET "Tickets" category formalizes what eliminating-toil documents as the ticket-driven toil class — reliability measured by manual intervention required. Settled.

### Claim 11: THD evangelized SLOs top-down — the education campaign started with senior leadership to secure executive backing, then moved team-by-team; a weekly SLO report in VALET format went to senior leadership with reliability commentary; workshops later became the FiRE Academy training program; and SLO implementation officially factored into annual performance reviews for development managers
- **Evidence**: The "Evangelizing SLOs" section describes the sequencing
  (leadership first), the weekly report, the marketing materials (internal
  WordPress blog, Tech Talks with a Google SRE guest, stickers and t-shirts),
  and the performance-review linkage.
- **Confidence**: settled
- **Quote**: "As we needed to secure executive backing for our move to SLOs, our education campaign started with senior leadership."
- **Also**: "we sent a weekly SLO report in VALET format, which we paired with commentary around general reliability concepts and lessons learned from internal events, to senior leadership." — and — "SLO implementation even began to officially factor into THD's annual performance reviews for development managers."
- **Our assessment**: The incentive lever (SLOs in annual reviews) and the executive-first sequencing are the strongest org-change-management evidence in the corpus for SLO adoption, and they map directly onto the S5E2 "SLO evangelist" role (Claim 7) and ownership ladder (Claim 8: higher-level journeys owned up the management chain). The weekly VALET report to leadership is a concrete instance of S5E2's "error budgets as an executive-communication instrument" (Claim 13). Settled.

### Claim 12: THD automated VALET data collection with TPS Reports (a BigQuery-based framework: all web-serving frontend logs fed to BigQuery, transformed into hourly VALET metrics, new services auto-registered, with a chatbot for in-chat VALET reporting) and built a VALET service/dashboard for trending at daily, weekly, and monthly granularity — deliberately decoupled from monitoring/alerting systems
- **Evidence**: The "Automating VALET Data Collection" section describes TPS
  Reports, the VALET service, and the dashboard; the decoupling tradeoff is
  stated explicitly.
- **Confidence**: settled
- **Quote**: "We built a framework to automatically capture VALET data for any service that was deployed to our new GCP environment. We called this framework TPS Reports, a play on the term we used for volume and performance testing (transactions per second)."
- **Also**: "The most interesting integration was a chatbot that let us directly report on the VALET of services in a commercial chat platform." — and — "Note that our SLOs are a trending tool that we can use for error budgets, but aren't directly connected to our monitoring systems." — and — "The downside of this setup is that alerting thresholds set in the monitoring systems aren't integrated with SLOs; however, we have the flexibility to change out monitoring systems as needed."
- **Our assessment**: Two important, citable design decisions. First, *automating SLI collection* (auto-registered services, hourly metrics) is what made 800 services tractable — the "SLI automation as the scale prerequisite" pattern the guide's Ch05 can adopt for many-model fleets. Second, *decoupling SLOs from alerting* (SLOs as a trending/error-budget tool, not a paging source) is a deliberate design that avoids the "page someone to death on every out-of-SLO state" failure Desai warns about (S1E4 Claim 10) — THD accepted the tradeoff (alert thresholds not integrated with SLOs) for flexibility. That tradeoff is itself worth surfacing in the guide. Settled.

### Claim 13: THD's SLO adoption scaled from ~50 services to 800 services in less than a year (~50 new services/month registered with VALET) — but automation was not a prerequisite: "there are benefits to just writing SLOs in the first place"
- **Evidence**: The "Proliferation of SLOs" section gives the 50→800 numbers,
  the registration rate, and the explicit "you don't need complex automation"
  caveat.
- **Confidence**: settled
- **Quote**: "After tracking SLOs for about 50 services at the beginning of the year, by the end of the year we were tracking SLOs for 800 services, with about 50 new services per month being registered with VALET."
- **Also**: "While automation provided THD extra benefits, there are benefits to just writing SLOs in the first place." — and — "we went from 0 to 800 SLO-supported services in less than a year."
- **Our assessment**: The 50→800-in-a-year curve is the corpus's strongest quantitative counter-example to "you need an elaborate SLO platform before you start" — and it conditions (not contradicts) Desai's proliferation warning (S1E4 Claim 9): THD scaled SLO *coverage* fast precisely because the SLOs were trending tools decoupled from paging, so the "always out of SLO → page someone to death" failure (S1E4 Claim 10) did not trigger. The "benefits to just writing SLOs" is a pragmatic de-risking note for teams without automation budget. Settled.

### Claim 14: THD adapted VALET beyond web services — batch applications map to records processed (Volume), percent-complete-by-time (Availability), job runtime (Latency), failed records (Errors), and manual fix/reprocess count (Tickets) — and used TPS Reports to run automated destructive (chaos) testing in staging with impact recorded against a service's VALET data
- **Evidence**: The "Applying VALET to Batch Applications" and "Using VALET in
  Testing" sections.
- **Confidence**: settled
- **Quote**: "How often (as a percentage) the job completed by a certain time" — and — "The number of times an operator has to manually fix data and reprocess a job"
- **Also**: "With the TPS Reports framework in place, we could automatically run destructive tests and record the impact (or hopefully lack of impact) to the service's VALET data."
- **Our assessment**: THD's batch-availability format ("how often the job completed by a certain time") is exactly the third pipeline-freshness SLO format the data-processing-pipelines chapter standardizes ("the pipeline job has completed successfully within Y") — an independent re-derivation of the same batch-SLO shape. The chaos-testing-with-VALET-measurement pattern (measure the impact of injected failures against SLOs) is a concrete, early example of SLO-driven chaos engineering the guide can cite. Settled.

### Claim 15: THD's stated future is an error-budget culture "similar to Google" (stop pushing non-reliability features when a service is out of SLO), it is "weighing the pros and cons of rolling windows versus fixed windows," and it wants SLOs set by the business owner based on criticality — with simplified business-facing VALET tiers (99.5% / 99.9% / 99.95% / 99.99%) and deployment-gating by automated VALET verification before rollout
- **Evidence**: The "Future Aspirations" section enumerates the error-budget
  culture, the window debate, business-owner-set SLOs with the simplified
  tiers, and the deployment-verification aspiration.
- **Confidence**: emerging (aspirations, not yet implemented at time of
  writing)
- **Quote**: "Our next step is an error budget culture similar to Google, whereby a team stops pushing new features (other than improvements to reliability) when a service is out of SLO."
- **Also**: "Like many companies adopting error budgets, we're weighing the pros and cons of rolling windows versus fixed windows." — and — "we strongly believe that the SLOs for a service should be set by the business owner of the service (often called a product manager) based on its criticality to the business." — and — "We'd like to extend VALET data to application deployments. Specifically, we'd like to use automation to verify that VALET is within tolerance before rolling out a change to the next server, zone, or region."
- **Our assessment**: Two conditioning variables worth capturing. (1) THD's *aspiration* to stop feature pushes when out of SLO is the canonical Treynor launch-freeze model (Treynor Claim 9) — but stated as a future goal with an immediate hedge ("we'll have to strive to find a good balance between the SLO reporting time frame (weekly or monthly) and the frequency of SLOs being breached"), which matches Hidalgo's retraction of the binary freeze framing outside Google-core (S5E2 Claim 14). As an aspiration, this is not a contradiction with either position. (2) The business-owner-set SLO tiers (99.5/99.9/99.95/99.99) operationalize Treynor's "the reliability target is a product question" (Treynor Claim 8) and Hidalgo's PM-ownership ladder (S5E2 Claim 8) with concrete, business-shaped numbers. The deployment-gating aspiration is the SLO-gated rollout that canarying mechanics (Ch16) formalize. Emerging.

### Claim 16: The chapter's conclusion: SLO culture is an ongoing process, not a one-time fix; THD's and Evernote's measurement styles, SLIs, SLOs, and implementation details are markedly different despite shared philosophical underpinnings; and SLO implementation "need not be Google-specific"
- **Evidence**: The closing "Conclusion" section.
- **Confidence**: settled
- **Quote**: "These two case studies highlight that SLO culture is an ongoing process and not a one-time fix or solution."
- **Also**: "Both stories complement Google's own take on SLOs by demonstrating that SLO implementation need not be Google-specific."
- **Our assessment**: The meta-claim the corpus can adopt directly: SLO adoption is *context-shaped* — the two companies chose different SLIs, different windows, different automation depth, and both succeeded. This supports presenting SLO adoption patterns as a menu conditioned on org context rather than a single prescribed playbook — exactly how the guide should present the S5E2/Furino/Desai material. Settled.

## Concrete Artifacts

### Evernote's first SLO document structure (verbatim from the source)

```
DEFINITION     "This was an uptime measure: 99.95% uptime measured over a
               monthly window, set for certain services and methods."
               (calendar month, not rolling — deliberately)
WHAT TO MEASURE "a status page built into our service that exercises most of
               our stack and returns a 200 status code if all is well"
HOW TO MEASURE  third-party prober (Pingdom), outside and independent of the
               environment, including the load balancing stack
CALCULATION     documented from raw Pingdom data; maintenance windows treated
               as downtime (uninformed users experience them as downtime)
— Ben McCormack, Evernote, SRE Workbook Ch3
```

### Evernote's prober configuration (verbatim)

```
- Frequency of probe:   "We poll our frontend nodes every minute."
- Location of probers:  "we currently use multiple probes in North America
                         and Europe"
- Definition of "down": "If a prober check fails, the node is marked as
                         Unconfirmed Down and then a second geographically
                         separate prober performs a check. If the second
                         check fails, the node is marked down for SLO
                         calculation purposes. The node will continue to be
                         marked as down as long as consecutive probe requests
                         register errors."
— Ben McCormack, Evernote, SRE Workbook Ch3
```

### The VALET framework (THD's five SLO categories)

```
VOLUME       "How much business volume can my service handle?"
AVAILABILITY "Is the service up when I need it?"
LATENCY      "Does the service respond fast when I use it?"
ERRORS       "Does the service throw an error when I use it?"
TICKETS      "Does the service require manual intervention to complete my
              request?"  ("analogous to something like 'software operation
              level'")
— William Bonnell, The Home Depot, SRE Workbook Ch3
```

### THD's simplified business-facing VALET tiers (for product managers)

```
99.5%   "Applications that are not used by store associates or an MVP of a
         new service"
99.9%   "Adequate for the majority of nonselling systems at THD"
99.95%  "Selling systems (or services that support selling systems)"
99.99%  "Shared infrastructure services"
— William Bonnell, The Home Depot, SRE Workbook Ch3
```

### VALET mapped to batch applications (THD)

```
Volume      The volume of records processed
Availability How often (as a percentage) the job completed by a certain time
Latency     The amount of time it takes for the job to run
Errors      The records that failed to process
Tickets     The number of times an operator has to manually fix data and
            reprocess a job
— William Bonnell, The Home Depot, SRE Workbook Ch3
```

### TPS Reports data flow (THD's SLI automation)

```
All web-serving frontend logs  →  BigQuery  →  TPS Reports transforms into
   hourly VALET metrics (queryable by anyone)
Newly created services         →  automatically registered → immediately
   queryable
Outputs                        →  automated reports, alerts, and a chatbot
   reporting VALET for the last hour / vs previous week / services out of
   SLO inside a commercial chat platform
— William Bonnell, The Home Depot, SRE Workbook Ch3
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` (issue #122) — the
    closest sibling in the corpus, and Alex Hidalgo is a co-author of both.
    Alignments (each verified against the cited note's claim):
    - **S5E2 Claim 1** (SLOs as the shared vernacular across teams/verticals) ⇄
      THD's "common vernacular" as the first of its four culture areas
      (Claim 8 here) and Evernote's "common frame of reference" that lets both
      teams "make similar decisions" (Claim 2 here).
    - **S5E2 Claim 3** (the team that writes AND runs the code should create and
      use the SLOs; imposed SLOs become a compliance exercise) ⇄ THD's
      full-stack-ownership "freedom and responsibility culture" where
      developers are "jointly responsible for the operations of their service"
      (Claim 7 here).
    - **S5E2 Claim 10** (consistent revisit dates for SLOs, quarterly or
      bi-annually) ⇄ Evernote's independently-chosen six-month review cycle
      (Claim 5 here) and THD's weekly/monthly SLO reviews (Claim 12 here).
    - **S5E2 Claim 8** (PM → director → VP ownership ladder for higher-level
      journeys) ⇄ THD's "SLOs for a service should be set by the business owner
      of the service (often called a product manager)" (Claim 15 here).
    - **S5E2 Claim 4** (say "user," not "customer" — internal teams are users
      too) ⇄ THD's published per-microservice API SLOs for dependent
      microservices ("the Inventory microservice published SLOs that the Cart
      microservice ... could consult," Claim 9 here).
  - `docs-google-sre-reaching-beyond-walls.md` (issue #885) — same workbook
    book; Dave Rensin is a co-author of both chapters:
    - **Reaching-beyond-walls Claim 7** (SLOs are how you speak to customers;
      in the absence of a stated SLO the customer invents one) ⇄ Evernote's
      SLO-wall breaking — sharing real-time SLO performance so Google
      understands "which performance characteristics were most important to us"
      (Claim 6 here). The chapter is the customer-side case study the
      platform-side Ch19 methodology describes.
    - **Reaching-beyond-walls Claim 3** (platform reliability is a partnership;
      99.999% × 99% caps a tenant at 98.999%) ⇄ Evernote's discovery that a
      global GCP rollup hides region-isolated outages for a small VM footprint
      (Claim 6 here) — both are aggregate-vs-tenant SLO visibility.
    - **Reaching-beyond-walls Claim 2** (users, not monitoring, decide
      reliability) ⇄ Evernote's maintenance-as-downtime decision (Claim 4
      here) — measuring what users experience, not what ops announced.
  - `docs-google-sre-eliminating-toil.md` (issue #819) — same workbook book:
    - **Eliminating-toil Claim 8** (a well-defined SLO enables engineers to
      ignore operational tasks that don't consume the error budget) ⇄
      Evernote's budget-driven resource allocation — a missed SLO "helps us
      prioritize relevant fixes" (Claim 5 here) — and THD's error-budget
      culture aspiration (Claim 15 here). The budget as the *permission to
      skip/prioritize* mechanism.
    - Evernote's motivation ("Move engineering focus away from undifferentiated
      heavy lifting in datacenters," Claim 1 here) is the toil-reduction driver
      Ch6 documents as the reason SLOs reduce operational work.
  - `docs-google-sre-data-processing-pipelines.md` (issue #817) — **Claim 1**
    (pipeline freshness SLOs come in three formats including "the pipeline job
    has completed successfully within Y") ⇄ THD's batch Availability SLO "How
    often (as a percentage) the job completed by a certain time" (Claim 14
    here) — an independent re-derivation of the same batch-SLO format.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` (issue #87) — Furino's
    **Claim 6** (saturation/system-health SLIs are a deliberate deviation from
    user-experience measurement, useful only for scaling) ⇄ THD's explicit
    decision *against* utilization SLOs (Claim 9 here) — both reach the
    user-centric-SLO boundary from opposite sides. Furino's **Claim 3**
    (accepting an error budget is what lets you make changes) ⇄ Evernote's
    SLO-quantified release-window reduction (Claim 5 here) — budget as the
    change-enabler.
  - `docs-google-sre-prodcast-01-04-rethinking-slos.md` (issue #37) —
    Desai's **Claim 10** ("if you're gonna page someone whenever you're out of
    SLO ... you will page someone to death") is *conditioned* by THD's design
    choice to keep SLOs as trending/error-budget tools decoupled from alerting
    (Claim 12 here) — THD scaled to 800 SLO-covered services without that
    failure mode precisely by not paging on out-of-SLO. Desai's **Claim 8**
    (validate and iterate) ⇄ Evernote's "Perfect is the enemy of good" +
    six-month review cycle (Claim 5 here).

- **Contradicts**: None that meets the MINER.md §4a bar — but two tensions are
  surfaced prominently, both resolved as conditioning variables consistent with
  the corpus's prior handling of the same axes:
  1. **Simple-first/blanket-ish SLOs (Evernote, THD) vs Hidalgo's
     "bespoke/artisanal, don't slap an SLO on every endpoint" (S5E2 Claim 2).**
     Evernote started with a single uptime SLO for "certain services and
     methods" and THD set availability+latency SLOs on every microservice's
     internal API calls. This could appear to oppose Hidalgo's bespoke-SLO
     rule. It does not: (a) Hidalgo's critique targets uniform targets across
     heterogeneous *code paths/backends* (her "every response in 200ms"
     example), while THD let each service define its own latency target,
     measurement point, and percentiles; (b) Evernote explicitly framed the
     coarse start as iterative ("Perfect is the enemy of good," six-month
     review cycle — Claim 5 here), which is Hidalgo's own "not a one and done"
     lifecycle. Same "start coarse, refine, don't mechanically blanket" rule
     from opposite directions — the conditioning variable is *whether the
     target is tuned per code path and re-examined*, which both case studies
     did. No contradiction filed.
  2. **THD's error-budget aspiration ("stop pushing new features when out of
     SLO") vs Hidalgo's retraction of the freeze framing (S5E2 Claim 14).**
     THD states the launch-freeze model (Treynor Claim 9) as a *future goal*
     and immediately hedges: "To protect the velocity demands of our business,
     we'll have to strive to find a good balance between the SLO reporting time
     frame (weekly or monthly) and the frequency of SLOs being breached." It is
     an aspiration about the model, not a defense of it, and the corpus has
     already classified the Treynor ↔ Hidalgo launch-freeze axis as a
     conditioning variable (Google-core-own-the-codebase vs multi-team) in both
     the S1E4 and S5E2 notes. No contradiction filed; CONTRADICTIONS.md has no
     open entries and no open `contradiction`-labeled issues cover this.

- **Extends**:
  - `docs-google-sre-reaching-beyond-walls.md` (issue #885) — that chapter
    prescribes *how a platform does SRE with customers* (Step 1 SLOs/SLIs,
    Step 2 shared dashboards, Step 4 design reviews ranked by error-budget
    consumption). The Evernote case study here is the worked customer-side
    instance of that methodology, written with Dave Rensin (Ch19's lead author)
    as co-editor.
  - `docs-google-sre-eliminating-toil.md` (issue #819) — Evernote's
    off-datacenters move and THD's full-stack-ownership model are documented
    *case studies of the toil-reduction motivations* the eliminating-toil
    chapter turns into taxonomy and strategy; this chapter supplies the
    real-company evidence behind Ch6's framework.
  - `docs-google-sre-canarying-releases.md` (issue #801) — THD's deployment
    aspiration (automated VALET verification "before rolling out a change to
    the next server, zone, or region," Claim 15 here) points toward the
    SLO-gated rollout that Ch16's canary mechanics formalize (**Claim 6**:
    error-budget impact is proportional to traffic exposed to defects; the
    SLO/eval check is what makes the staged rollout safe).
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` (issue #122) —
    the S5E2 note gives the *enterprise adoption org-patterns* (evangelist,
    central practice team, ownership ladder, revisit cadence); this chapter
    supplies two complete *worked journeys* those patterns describe, adding
    concrete numbers (99.95% first SLO, 5→2 release windows, 50→800 services,
    〜50/month registration) and the org-change mechanics (four culture areas,
    annual-review incentives, weekly leadership reports).

- **Novel** (new to the corpus from this source):
  - **Evernote's first-SLO document structure and measurement design** — the
    definition / what-to-measure / how-to-measure / how-to-calculate document,
    the external two-location prober "down" confirmation rule, and the
    maintenance-as-downtime accounting rule.
  - **The calendar-month-vs-rolling SLO window decision** as a documented
    choice (Evernote's rationale: keeping monthly service reviews organized)
    and THD's later "weighing the pros and cons of rolling windows versus fixed
    windows."
  - **The customer/cloud-provider shared-SLO partnership mechanics** — the
    global-rollup-hides-regional-outages failure mode, shared real-time SLO
    dashboards between customer and provider, SLO-impact-quantified
    notifications ("this issue is causing a 5% impact to Evernote's SLO"), and
    mutual-P1 incident handling.
  - **THD's four-part SLO Culture Project** (common vernacular, evangelism,
    automation, incentive) as an organizational change-management checklist,
    including the incentive lever (SLOs in annual performance reviews).
  - **The VALET framework** (Volume/Availability/Latency/Errors/Tickets) and
    its simplified business-facing tiers (99.5 / 99.9 / 99.95 / 99.99) for
    product-manager-owned SLO targets.
  - **TPS Reports / BigQuery-based automatic SLI collection** (auto-registered
    services, hourly metrics, chatbot reporting) as the scaling prerequisite,
    and the **deliberate decoupling of SLOs from alerting** (trending tool, not
    paging source) with its accepted tradeoff.
  - **The SLO-program scaling data points**: Evernote on v3 of its SLO practice
    after nine months; THD from 50 to 800 SLO-covered services in less than a
    year.
  - **VALET applied to batch applications and chaos/destructive testing in
    staging.**

## Guide Impact

- **Chapter 00 (Principles — SLOs / error budgets)**: Supplies the
  adoption-playbook evidence behind principle 5 ("LLM services need SLOs too")
  and principle 3 ("Encode ops knowledge outside the chat"). Concretely:
  1. Cite Evernote's dev/ops outcome (Claim 2 — "an error budget/SLO approach
     has led both teams to make similar decisions when presented with the same
     facts") as the strongest first-party evidence in the corpus that SLOs
     resolve the ops/dev conflict the guide's "Break the dev/SRE wall early"
     section already frames.
  2. Add the **six-month / weekly-monthly SLO review cadences** (Claims 5, 12)
     as concrete instances of the revisit obligation, complementing the S5E2
     quarterly/bi-annual recommendation and Desai's validate-and-iterate.
  3. Present the case studies as evidence that **SLO adoption is context-shaped,
     not Google-specific** (Claim 16) — the guide should present SLO patterns
     as an org-context-conditioned menu, not a single playbook.
- **Chapter 02 (observability)**: The most directly actionable chapter.
  1. Adopt Evernote's **SLI measurement design** (Claim 4) into the
     SLO-and-drill-down material: external black-box prober, two-location "down"
     confirmation, and maintenance-as-downtime — with the explicit rationale
     that the SLI must measure user-experienced reliability, not announced
     operational windows.
  2. Adopt THD's **SLI choice rules** (Claims 9-10): percentiles over averages
     (min P90, user-facing P95/P99), black-box supplement to white-box
     monitoring, 5xx-only error SLOs with 4xx tracking, and the deliberate
     exclusion of utilization from SLOs.
  3. Add the **global-rollup-hides-regional-outages** failure mode (Claim 6)
     to the SLO-signal-quality material — an aggregate SLO that looks green can
     mask a single-tenant/region failure; for LLM platforms, a global
     model-quality SLO can hide a region- or tenant-specific degradation.
- **Chapter 04 (oncall-and-toil)**: Add the error-budget-as-prioritization
  pattern (Claim 5 — missed-SLO-last-month drives fix prioritization) as the
  budget-driven resource allocation mechanism, and THD's support-tickets-as-
  reliability-proxy pre-state + Tickets-as-VALET-category (Claims 7, 10) as the
  bridge between ticket toil and SLO measurement. Evernote's "undifferentiated
  heavy lifting in datacenters" motivation (Claim 1) ties the SLO program to
  the toil-reduction drivers of Ch04.
- **Chapter 05 (LLM ops reliability)**: Transferable SLO-setting practice for
  AI services (Miner's synthesis; the source is pre-LLM):
  1. **Start simple and iterate for agent/model SLOs** (Claim 3, 5): begin with
     one coarse user-facing SLO (availability/uptime), document it, revise on a
     fixed cadence — the Evernote v1→v3 trajectory is the model for standing up
     an agent-reliability SLO program without analysis paralysis.
  2. **Automate SLI collection to make fleet-wide SLOs tractable** (Claim 12):
     the TPS Reports pattern — auto-registered services, hourly metrics,
     chatbot reporting — is directly applicable to many-model/agent fleets,
     where per-service SLO coverage only scales if SLIs are collected
     automatically.
  3. **Decouple SLO trending from alerting as a deliberate design** (Claim 12,
     with Desai's page-someone-to-death conditioning): SLOs as the error-budget/
     trending layer, symptom alerting separate — avoids alert sprawl while
     keeping budget-based prioritization.
  4. **Business-owner-set SLO tiers** (Claim 15): the simplified 99.5/99.9/
     99.95/99.99 ladder with criticality-based assignment is a ready-made
     template for product-manager-owned agent/model reliability targets,
     operationalizing Treynor's "reliability target is a product question."
  5. **SLO-gated rollout verification** (Claim 15): "verify that [reliability]
     is within tolerance before rolling out a change to the next server, zone,
     or region" is the deployment-gating step the guide's canary material
     already formalizes — cite THD's aspiration as the practitioner statement
     of the same principle.
  6. **Provider/customer shared SLOs for hosted LLM platforms** (Claim 6): a
     model-provider tenant relationship mirrors Evernote/GCP — share real-time
     SLO performance, quantify impact in tenant terms, and treat high-impact
     incidents as joint P1s.

## Extraction Notes

- **Source read**: The chapter at
  `https://sre.google/workbook/slo-engineering-case-studies/` was fetched and
  read end-to-end (intro, Evernote half, THD half, conclusion, and footnotes).
  It is a single self-contained page; no sub-pages were followed. The linked
  Evernote GCP-migration blog post and the FiRE Academy footnote are referenced
  but were not fetched (out of scope for this note). The sibling chapter
  "Implementing SLOs" (Ch2) is not yet mined in the corpus and is a candidate
  separate source.

- **`confidence_overall: settled`**: The dominant content is documented,
  first-party enterprise case studies published through Google's official SRE
  channel and co-edited by Alex Hidalgo and Dave Rensin. Adoption mechanics,
  SLI choices, and org-change details (Claims 1-14, 16) are settled practitioner
  accounts; only the explicitly-future aspirations (Claim 15) are marked
  emerging and do not pull the overall confidence down. The scale figures
  (220M users, 800 services) are self-reported by the companies and should be
  read as such.

- **Related-notes candidates (`miner-related-notes.md`) — dispositions** (all
  ten):
  - `docs-google-sre-eliminating-toil.md` — **Cited** (Corroborates Claim 8;
    Extends; Evernote's off-DC motivation).
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — **Dismissed**;
    complexity science for incident response; no SLO-adoption content.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` — **Cited**
    (Corroborates Claims 1, 3, 4, 8, 10; Extends; Hidalgo co-edits this
    chapter).
  - `docs-google-sre-data-processing-pipelines.md` — **Cited**
    (Corroborates Claim 1 — batch-freshness format matches THD's batch
    Availability).
  - `docs-google-sre-reliable-product-launches.md` — **Dismissed**; launch
    process mechanics, not SLO adoption.
  - `docs-google-sre-on-call.md` — **Dismissed**; on-call balancing.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` —
    **Dismissed**; incident-response tooling.
  - `docs-google-sre-configuration-specifics.md` — **Dismissed**; config
    language design.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**; AI-for-
    SRE tagging/golden data, not SLO adoption.
  - `docs-google-sre-reaching-beyond-walls.md` — **Cited** (Corroborates
    Claims 2, 3, 7; Extends; Rensin co-edits both chapters).
  Additional cross-refs beyond the candidate list, per the Prospector's
  overlap list: `docs-google-sre-prodcast-01-04-rethinking-slos.md` and
  `docs-google-sre-prodcast-04-05-furino-slos.md` (cited), and
  `docs-google-sre-canarying-releases.md` (Extends). All cited claim numbers
  were verified against the target notes per MINER.md §4b (S5E2 Claims 1, 3,
  4, 8, 10; reaching-beyond-walls Claims 2, 3, 7; eliminating-toil Claim 8;
  data-processing-pipelines Claim 1; furino Claims 3, 6; rethinking-slos
  Claims 8, 10; canarying Claim 6). The candidates file is not committed.

- **Quote verification**: All `Quote` and `Also` fields were copied
  character-for-character from the fetched page text. The source uses straight
  double quotes inside passages (e.g., "You wrote it, you run it") and footnote
  markers — footnote markers were trimmed from the end of quoted fragments
  (e.g., the FiRE Academy line), and the em-dash/nested-quote characters were
  preserved. Where a claim synthesizes across the two companies or across
  sections, the synthesis lives in "Our assessment," not in a quote (per
  MINER.md §2a). The Concrete Artifacts tables are the Miner's faithful
  structuring of the source's definitions and lists (verbatim where quoted);
  labeled as such. The Assayer should spot-check key quotes against the live
  URL.

- **Contradiction analysis (per MINER.md §4a)**: Two apparent tensions were
  evaluated and rejected as contradictions: (1) simple-first/per-service SLOs
  (Evernote, THD) vs Hidalgo's bespoke-SLO rule (S5E2 Claim 2) — resolves to
  the tuning-and-revisiting conditioning variable both case studies satisfy;
  (2) THD's launch-freeze error-budget aspiration vs Hidalgo's retraction
  (S5E2 Claim 14) and Treynor's freeze model (Treynor Claim 9) — an explicit
  future aspiration with an immediate hedge, and an axis the corpus has already
  classified as a conditioning variable in the S1E4 and S5E2 notes. No
  contradiction issue filed; CONTRADICTIONS.md has no open entries and no open
  `contradiction`-labeled issues were found at extraction time.

- **AI/LLM relevance**: None in the source itself (2018-era). The relevance is
  as transferable SLO-setting/measurement/org-adoption practice for AI
  services (Guide Impact, Ch05). The Ch05 extrapolations are the Miner's
  analytical synthesis and should be reviewed by the Smith for fidelity.
