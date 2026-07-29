---
source_url: https://sre.google/static/pdf/CreatingProductionLaunchPlan.pdf
source_type: documentation
title: "Creating a Production Launch Plan — O'Reilly SRE Report (Google)"
author: Alec Warner, Vitaliy Shipitsyn, with Carmela Quinito (Google SRE)
date_published: 2019-11-13
date_extracted: 2026-07-29
last_checked: 2026-07-29
status: current
confidence_overall: settled
issue: "#639"
---

# Creating a Production Launch Plan — O'Reilly SRE Report

> A practical 45-page O'Reilly report from Google SRE practitioners (2019) providing a hands-on guide to writing and executing production launch plans. Includes a reusable launch plan template (staged checks, rollout schedules, monitoring tables, emergency rollback planning), a detailed Dauntless game launch case study (10X worst-case scaling exercise, load simulation, autoscaling mid-launch fixes, database sharding, login queue pattern), risk/mitigation table methodology, dark launch technique, and day-of-launch command center procedures. Provides the concrete launch plan *document* and *execution* practices that complement the SRE Book's organizational Launch Coordination Engineering (LCE) methodology.

## Source Context

- **Type**: documentation — standalone O'Reilly report (45 pages), published November 2019, hosted as a PDF on sre.google. Part of the Google-O'Reilly collaboration series.
- **Author credibility**: High credibility. Alec Warner is a senior SRE at Google since 2007, working on planet-scale storage systems and Customer Reliability Engineering (CRE). Vitaliy Shipitsyn is a staff software engineer in SRE at Google, specializing in production infrastructure resilience and production best-practice adoption, with several years of launch consulting experience. Carmela Quinito is an SRE technical writer at Google. All three are practitioner-authors with direct Google SRE launch experience. The report is published through O'Reilly Media's editorial pipeline as part of a collaboration with Google.
- **Scope**: Covers (a) launch plan definition and benefits (risk management, quick adjustments, communication, process improvement); (b) product analysis elements for launch readiness (architecture review, traffic projections, resource provisioning, SLO evaluation, resilience planning); (c) operational sustainability assessment (team capacity, technology alignment, technical debt); (d) business needs accommodation; (e) launch structure — stages (EAP/Alpha/Beta/GA), dark launches, checklists, action item properties, launch controls; (f) launch day procedures — command center, pre-to-post-launch transition, after-launch monitoring; (g) the Dauntless game launch case study with specific scaling session, load simulation, architecture review, and post-launch adaptation lessons; (h) a reusable launch plan template in the appendix. Does NOT cover AI/LLM workloads — the patterns are general SRE launch planning knowledge directly transferable to AI/LLM service and model deployments.

## Extracted Claims

### Claim 1: A launch plan is a document that communicates scope, timeline, contacts, mitigation, and records actual progression — preparing the product for the critical pre-to-post-launch transition
- **Evidence**: The "What Does a Launch Plan Look Like?" section defines the launch plan with specific functions. It is not a project plan; it is a focused operational document that captures points of contact, mitigation, and records what actually happened.
- **Confidence**: settled
- **Quote**: "The launch plan is a document that communicates the scope and timeline of all proposed changes in production, assembles all relevant points of contact and mitigation, and records the actual launch progression along with any follow-up actions after the launch. It prepares your product for the critical step of transitioning from pre- to post-launch."
- **Our assessment**: This functional definition distinguishes a launch plan from a general project plan or timeline. The emphasis on *recording actual progression* (not just planned actions) and the pre/post-launch transition as the critical step are specific differentiators. For AI/LLM services, this definition is directly applicable — model rollouts need a document that captures what actually happened (token usage, latency shifts, error rates during rollout), not just what was planned.

### Claim 2: Launch planning manages risk through scenario generation, mitigation strategy development, prioritization, and early resource allocation — "hope is not a strategy for launches"
- **Evidence**: The "Managing Risks Instead of Hoping for Luck" section enumerates four risk-management functions: generate risk scenarios, build mitigation strategies, prioritize the most impactful risks, and focus resources earlier in development rather than retrofitting closer to launch.
- **Confidence**: settled
- **Quote**: "Hope is not a strategy for launches; you might not have time for surprises once you initiate the launch, so don't count on luck getting you through!"
- **Our assessment**: The four-step risk management framework (generate → build → prioritize → focus early) is a direct, actionable methodology for AI launch planning. For LLM model rollouts, scenario generation would include: model quality regression, prompt injection vulnerability, cost explosion from unexpected usage, GPU capacity exhaustion, and API provider dependency failure. The emphasis on early resource allocation is especially relevant for AI where GPU capacity may have long lead times.

### Claim 3: Launch planning requires "Plan B" and "Plan C" backup plans with explicit invocation conditions — e.g., whether to acquire more resources or throttle adoption when capacity is exceeded
- **Evidence**: The "Managing Risks" section discusses developing backup/fallback plans with explicit conditions. The report raises specific contingent questions: "if your product starts running out of resources, will you try to get more resources or start to throttle user adoption? And do you even have the option to do either? How quickly will you be able to throttle or completely disable the product if it starts degrading other systems?"
- **Confidence**: settled
- **Quote**: "This process might involve making a plan B—and sometimes a plan C."
- **Our assessment**: The contingent-question framework — what will you do (two alternatives), do you have the option, and how quickly can you act — is a structured method for AI launch backup planning. For an LLM service launch, "Plan B" might be switching to a smaller/cheaper model if costs exceed projections; "Plan C" might be disabling the AI feature entirely for a tier of users. The throttling/disabling question is especially pertinent: can an AI model inference pipeline be throttled mid-launch, or would that require code changes?

### Claim 4: Traffic estimation must cover four time horizons — launch day (24-48h), near-term (1 week), medium-term (1 month), long-term (6-12 months) — with accuracy most critical for short-term estimates
- **Evidence**: The "Get traffic projections" section provides specific time ranges with rationale. Underestimating launch-day traffic by 100% "can be disastrous" while the same error at 6 months is "insignificant." Estimation methods include customer surveys, small-user onboarding projections, and baselines from comparable rollouts.
- **Confidence**: settled
- **Quote**: "You will need traffic estimates for several key time ranges: the day of launch when the interest peaks (the first 24–48 hours), the near-term range while the newness still exists (1 week), the medium-term range that permits you to evaluate the growth slope (1 month), and a long-term range that targets any perceived macro conditions (6–12 months)."
- **Our assessment**: The four-horizon framework is directly transferable to AI model launches. For an LLM service launch, launch-day (24-48h) traffic could spike far above projections if the model announcement goes viral — paralleling the "15×" spike noted in the SRE Book. The estimation methods (customer surveys, small user projections) are applicable to AI beta programs. The "underestimating by 100% on launch day is disastrous" principle is critical for AI capacity planning where GPU procurement lead times are long.

### Claim 5: Architecture review should produce a "Risks and Mitigations" table — with risk area, description, failure mode, mitigation strategy, and status columns — that captures systemic issues to resolve before launch
- **Evidence**: The "Review the product's architecture" section describes the output as a Risks and Mitigations table. Table 1 provides a concrete example entry for "Self-inflicted DoS attack by own clients" — clients synchronizing polling or compound retries that can saturate networks — with mitigation: exponential backoff and jitter.
- **Confidence**: settled
- **Quote**: "The output of this process is a Risks and Mitigations table, which you give to the appropriate developer or operations teams to resolve before the launch date. These risks are systemic issues that code or configuration changes should eliminate, not action items for the launch day."
- **Our assessment**: The Table 1 format (risk area, description, failure mode, mitigation, status) is a directly usable artifact for AI launch readiness reviews. For LLM deployments, example entries would include: "Model quality regression — new model version produces lower-quality outputs for edge cases — mitigation: automated A/B evaluation pipeline with quality gates." The distinction between "systemic issues that code/config should eliminate" and "launch day action items" is an important design principle for AI launch checklists.

### Claim 6: SLO evaluation is part of launch planning — including whether dependencies provide adequate SLOs and whether sufficient monitoring metrics exist to measure compliance
- **Evidence**: The "Evaluate the user experience" section states: "Review whether SLOs have been well defined for the product's core features. Pay attention to the balance of the costs and value of SLO metrics." It also requires checking dependency SLO adequacy and whether monitoring metrics are sufficient.
- **Confidence**: settled
- **Quote**: "Achieving low latency or high availability gets more expensive quickly, but it may not be necessary in most cases."
- **Our assessment**: The inclusion of SLO evaluation as a launch planning requirement — not just a "nice to have" — is a key transferable pattern. For AI services, SLO evaluation before launch would include: defining appropriate latency SLOs for token generation (streaming vs. non-streaming), accuracy/quality SLOs (are outputs meeting correctness thresholds?), and cost-per-request SLOs. The dependency SLO check is critical: an AI service depending on a third-party LLM API must evaluate whether that API's SLO is sufficient for the product's combined SLO.

### Claim 7: Launch stages (EAP, Alpha, Beta, GA) provide progressive exposure with pauses for validation — and can be combined with gradual traffic diversion (1% → 2% → 5% → 10% → 100%)
- **Evidence**: The "Launch Stages" section describes both dimensions of launch breakdown: by feature set (EAP/Alpha have subset features; Beta/GA have full features but differ in maturity) and by traffic percentage. The specific progressive percentages (1%, 2%, 5%, 10%, 100%) are enumerated.
- **Confidence**: settled
- **Quote**: "Start by opening the product to a small proportion of your customers. As you monitor progression from 1% to 2%, 5%, and 10%, you are ready to pause and roll back in the case of any incident, or move toward 100%."
- **Our assessment**: The two-dimensional stage breakdown (feature scope + traffic percentage) is a practical framework for AI model rollouts. An AI launch could: (1) in Alpha, deploy the new model to a subset of traffic (1%) with only core inference features enabled; (2) in Beta, expand to 10% traffic and enable all features (guardrails, logging); (3) in GA, reach 100% with full production support. The explicit monitoring-for-rollback at each step is the key operational practice.

### Claim 8: Dark launches expose new features to production traffic without rendering results to users — pushing the point of no return past most launch milestones
- **Evidence**: The "Launch Stages" section defines dark launches and their benefits. The technique involves making client requests to the product without displaying results, discarding results "as late as possible, perhaps in the frontend or even on the client." Allows slower rollout and canary testing over gradually increasing user percentages.
- **Confidence**: settled
- **Quote**: "To implement a dark launch, you could modify your public clients to make requests on your product without rendering the results to users. The product would throw away the results as late as possible, perhaps in the frontend or even on the client."
- **Our assessment**: Dark launches are directly applicable to AI/agent deployments where the new behavior should not be visible to users during validation. For example, a new LLM model version can be deployed to serve "shadow" requests — it processes live user traffic but the response is discarded in favor of the current model's response — allowing quality/performance comparison without user impact. The warning ("don't abuse user trust and computing resources") is relevant: shadow inference doubles compute cost and should be time-boxed.

### Claim 9: Each launch action item should have six properties — timing, owner (accountable), executor (different person), status, verification, and rollback — with owner/executor separation and rollback defined at planning time
- **Evidence**: The "Launch Actions and Status" section fully enumerates the six properties with rationale. Owner/executor separation "allows the executor to focus on the actions and the owner to focus on processes and verification." Rollback is "a responsible action, and capturing it at the time of defining actions is convenient."
- **Confidence**: settled
- **Quote**: "Having a rollback on hand is a responsible action, and capturing it at the time of defining actions is convenient."
- **Our assessment**: The six-property framework is a concrete design spec for launch action items in any system, including AI launch runbooks. The owner/executor separation is a specific operational pattern — the executor runs the command, the owner verifies it succeeded — that prevents the error of the same person both acting and signing off. The "rollback at planning time" rule is critical: for an AI model swap action item, the rollback (revert routing to previous model version, revert prompt template, revert guardrail configuration) must be specified before launch day, not discovered during an emergency.

### Claim 10: Launch controls should minimize production changes during launch — ideally self-contained configuration changes, not server restarts — with all code deployed and verified before launch day
- **Evidence**: The "Launch Controls" section states: "Minimizing the amount of change needed during the launch is important. Ideally, you only have to do simple production changes such as a self-contained runtime configuration change, and not a more complex change like restarting your application servers." All necessary code should be deployed and verified pre-launch.
- **Confidence**: settled
- **Quote**: "Before the launch, you already have deployed all necessary code to production and it is available for real live verification."
- **Our assessment**: This is a high-value deployment engineering principle for AI/LLM rollouts. The implication for AI model deployments: the new model version should already be deployed to inference servers (side-by-side with the current version) before launch day, with the launch action being a configuration change to route traffic to it — not a container rollout during launch. The preference for configuration changes over complex changes is particularly important for AI where model loading/unloading can take minutes and consume significant resources.

### Claim 11: A launch-day command center should assemble subject matter experts, on-call engineers, marketing, and executives — with documented communication channels, fallback mediums, and printed copies of the launch plan
- **Evidence**: The "Organizing a Command Center" section details the composition: "Subject matter experts—for the launching product and its main components," on-call engineers, members of "marketing and press," and "executives on hand for highly visible launches." It recommends documenting communication channels, fallback solutions (e.g., IRC if primary chat fails), and making "a PDF or even a hard copy of the launch plan to protect against any service outages at a critical time."
- **Confidence**: settled
- **Quote**: "A production crisis is not the time to be looking up who those people might be."
- **Our assessment**: The command center composition guidance is directly transferable to AI service launches. For an LLM model rollout, the command center would include: the inference platform SRE (model serving infrastructure), the ML engineer (model behavior), the product engineer (user-facing integration), the guardrail/security engineer (safety monitoring), marketing/PR (for public AI announcements), and executives (for high-visibility AI launches). The printed-copy-of-launch-plan recommendation is a practical resilience pattern — if the internal AI platform or monitoring dashboard is down, the launch team still has the action plan and contact list.

### Claim 12: The 10X worst-case scaling exercise — imagining 10× expected demand — is a rule-of-thumb technique that exposes architectural pain points before they occur in production
- **Evidence**: The Dauntless case study's "Holding a Scaling Session" section describes the 10X exercise with an explicit footnote defining the rule of thumb. "If you expected a million players and 10 million showed up, what would happen? Would the game work? If not, what would break first in the game?" The team grouped risks by likelihood, with likely risks receiving mitigations/scaling plans.
- **Confidence**: settled
- **Quote**: "10X is a general rule of thumb based on Google's experience engineering software systems. In our experience, systems do not fare well when demand is 10 times higher than what the system was designed to handle. These systems typically require major engineering changes in order to service the heightened demand; this requirement is why this exercise is valuable, as it can deliver these pain points before the scenario occurs in production."
- **Our assessment**: The 10X exercise is directly applicable to AI service launch planning. For LLM inference, the 10X exercise would test: can the inference cluster handle 10× the expected tokens per second? Would the KV-cache allocation strategy sustain 10× concurrent users? Can the guardrail/rate-limiter pipeline process 10× the expected prompt volume? The risk-grouping-by-likelihood methodology (likely risks get mitigations; unlikely risks get lower priority) provides a cost-effective prioritization framework.

### Claim 13: The Dauntless load simulation discovered that the DoS detection component triggered against legitimate load simulation traffic, causing a partial production outage — providing practical experience with the component's behavior under real conditions
- **Evidence**: The Dauntless case study's "Load simulation" and "Denial of service" sections. The DoS mitigation component was triggered during load simulation, causing it to attempt to "mitigate" the simulation traffic, resulting in a partial production outage. The team learned that the DoS component did function, saw how the game operated when it was active, and gained "experience in configuring the component in a real incident."
- **Confidence**: emerging
- **Quote**: "This component was triggered during the load simulation, causing the component to attempt to 'mitigate' the load simulation. This attempt resulted in a partial production outage and halted the load simulation."
- **Our assessment**: This is a cautionary pattern for AI inference load testing: rate limiters, guardrails, or safety classifiers configured to detect "anomalous traffic" may trigger against legitimate load-test traffic. For LLM inference, a load test generating high token volumes or low-latency requests could trigger prompt-rate-limiting or abuse-detection systems. The key lesson is to run load tests early enough to discover and tune these interactions, and to treat the discovery as "practical experience" rather than a test failure.

### Claim 14: The Dauntless launch demonstrated that even identified mitigations may need mid-launch adaptation — the autoscaler, called out in the design review, had to be modified during launch due to unforeseen scaling behavior
- **Evidence**: The Dauntless case study's "Autoscaling" section. The design review had identified autoscaling as a required item before launch day. Despite being "appropriately staffed and deployed," an unforeseen scaling issue caused malfunction, requiring a new design "deployed quickly to mitigate the situation."
- **Confidence**: emerging
- **Quote**: "It turned out the autoscaler would have to be modified mid-launch in order to achieve its goals."
- **Our assessment**: This pattern — identified and deployed mitigations still needing mid-launch adaptation — is a realistic counterpoint to the "perfect planning" ideal. For AI model launches, this means even pre-tested autoscaling policies may fail under the unique traffic patterns of launch day. The lesson is to have the engineering team available during launch (part of the command center) and to design deployment systems that allow quick configuration changes rather than full redeployments. The Dauntless team's ability to "modify mid-launch" depended on their preparation beforehand.

### Claim 15: The Login Queue pattern — controlling admission speed to provide a consistent experience for already-connected users while communicating queue position to waiting users — manages uneven demand for online services
- **Evidence**: The Dauntless case study's "Login Queue" section. Phoenix Labs decided to "provide a smooth gameplay experience for a preset number of players instead of a degraded experience for all players." The queue can be enabled opportunistically "during periods of instability or unexpected player demand."
- **Confidence**: settled
- **Quote**: "The Login Queue is a feature that Phoenix Labs can enable to control the speed at which players are admitted into gameplay. This feature enables the company to offer a consistent playable experience for players who have already joined the game, while communicating to queued players when they might be able to play."
- **Our assessment**: The Login Queue pattern directly translates to AI service demand management. An LLM service can implement a request queue that admits tokens/conversations at a controlled rate during overload, providing consistent latency for admitted requests and communicating wait times to users. The key design choice — protecting in-flight quality over total throughput — is the same tradeoff Google's SRE patterns recommend. The "opportunistic enablement" (not always on, enabled during instability) is a useful operational nuance.

### Claim 16: The launch plan template (Appendix) provides a reusable structure with stage-specific checklists, rollout schedule, monitoring tables, emergency rollback plan, and product success metrics
- **Evidence**: The appendix contains the full launch plan template (pp. 35-39) with: status/signoff table (stakeholders with email and signoff); summary section; related documents; testing guidelines; checks for Trusted Tester stage; checks for Production stage (QA complete, final signoffs, support page, production readiness, monitoring/alerts, stakeholder notification); checks for Post-Launch stage; Rollout Schedule (Trusted Tester, Production 1%→5%→20%→100%); Launch Monitoring table per component; Plan for Emergency Rollback (decision makers, procedure, impact); Product Success Metrics.
- **Confidence**: settled
- **Quote**: (no direct quote; the template itself is the artifact — see Concrete Artifacts section)
- **Our assessment**: The template is the most directly reusable artifact in the report. For AI/LLM service launches, the template can be adapted with: AI-specific Production Stage checks (model quality evaluation gates, safety/guardrail validation, cost-per-request monitoring, GPU capacity verification); AI-specific Rollout Schedule steps (model version, prompt version, guardrail version tracking); AI-specific Emergency Rollback (model version rollback, prompt revert, cache invalidation); AI-specific success metrics (quality scores, token efficiency, user satisfaction, safety incident rate). The template's staged structure (Trusted Tester / Production / Post-Launch) maps naturally to AI deployment pipelines (shadow/canary/production).

### Claim 17: Post-launch monitoring must cover full demand cycles (day-night-day, weekday-weekend), and permanent sustainable solutions must replace temporary launch-day mitigations
- **Evidence**: The "After the Launch" section states: "Status should be actively or at least occasionally monitored until a reasonable demand cycle has completed." The report explicitly notes that launch abnormalities need permanent fixes: "Any abnormalities identified and mitigated during the launch need sustainable, permanent solutions." Demand cycles include day-night-day (24h), weekday-weekend, and special events (flash sales).
- **Confidence**: settled
- **Quote**: "Any abnormalities identified and mitigated during the launch need sustainable, permanent solutions."
- **Our assessment**: The launch-is-not-over-on-launch-day principle and the specific demand-cycle framework are directly applicable to AI service launches. For an LLM service, demand cycles might show different inference patterns during business hours (high query volume) vs nights (batch processing), and weekdays (corporate users) vs weekends (consumer users). The requirement to replace temporary launch-day mitigations with permanent solutions is critical — a quick-fix rate limit or model routing change applied during launch should not become permanent technical debt.

### Claim 18: Operational sustainability assessment must evaluate whether the team has capacity to absorb the new product, whether technology aligns with existing practices, and how technical debt impacts future launches
- **Evidence**: The "Evaluate Operational Sustainability" section provides a framework with three dimensions: (1) team operating capacity — a team at 80% capacity can absorb 5-10% operational increase but not 40-80% from different technologies; (2) technology alignment — "a product that doubles the team's resource footprint might increase toil by only 5-10%" if using same technologies vs "40-80%" if different; (3) technical debt — "technical debt diminishes the capacity of the operations teams to support future launches."
- **Confidence**: settled
- **Quote**: "Does adding this product dilute or improve the operating efficiency? Poor alignment will increase the cognitive load on the team while reducing the reuse of the production expertise and hands-on skills. The difference can be drastic!"
- **Our assessment**: The quantified operational impact ranges (5-10% vs 40-80%) provide concrete decision-making guidelines for AI platform teams evaluating whether to onboard new AI products. For an AI infrastructure team supporting multiple inference frameworks (e.g., vLLM, TensorRT-LLM, TGI), adding a product that uses a different framework could increase toil by 40-80%, while one using the already-supported framework adds only 5-10%. The technical debt assessment is especially relevant: AI/ML teams under launch pressure often accumulate technical debt (hardcoded model configs, manual prompt management, ad-hoc evaluation scripts) that diminishes future launch capacity.

## Concrete Artifacts

### Artifact A — Risks and Mitigations table format (Table 1, p. 9, verbatim)

| Risk area | Risk description | Failure mode | Mitigation strategy | Status |
|-----------|------------------|-------------|-------------------|-------|
| Self-inflicted DoS attack by own clients | Clients that synchronize polling or compound retries can saturate networks. | Product becomes unavailable to other users. | Clients must add exponential backoff and jitter wherever polling or retries are used. | Low launch risk—DONE |

### Artifact B — Dauntless design review findings (Table 2, pp. 28-29, extracted verbatim)

| Area | Risk | Notes | Mitigation |
|------|------|-------|-----------|
| Game APIs did not have autoscaling enabled. | High | Large surges in player count are expected, and the game APIs should be able to scale up and down automatically without human intervention. This will enable automated operation of game APIs, instead of 24/7 human operation. | Team agrees that autoscaling should be enabled before launch day; will determine what blockers are necessary to be resolved prior. |
| The Content Delivery Network (CDN) might go down, taking the game offline. | Low | Dauntless's CDN vendor has pretty good uptime, historically speaking. | Mitigation (e.g., paying for two separate CDN vendors) tends to be expensive and operationally complex. CDN failure is rare. We accept this risk; no recommended actions. |
| Database: has the team executed a successful restore from a database replica? | Medium | Possible in theory to restore database state from a backup/replica, but this has never been done in production. | Action: try it and confirm we can do it. Document the process. |
| Database: concern that writes might overwhelm the throughput of the datastore without a sharding strategy. | High | Sharding the database can provide greater total throughput for the database layer. | Action: the Dauntless team committed to sharding some of the databases in order to sustain gaming performance. |

### Artifact C — Launch action item properties (p. 18-19, extracted verbatim)

Each action item has at least these properties:

- **Timing**: When the action item is needed and how long it is expected to take.
- **Owner**: The contact accountable for this action item and responsible for managing and verifying it.
- **Executor**: Who will actually perform the action item. If possible, assign someone different from the owner. This separation of responsibilities allows the executor to focus on the actions and the owner to focus on processes and verification.
- **Actions**: One or two actions to perform, simple enough not to need further breakdown of ownership, communication, or verification.
- **Status**: Whether this action item has been started, blocked, completed, verified, and so on. This property gives all observers the same situational awareness—the launch at any moment is in a clearly defined and clearly communicated state.
- **Verification**: How to determine that the actions occurred completely and successfully.
- **Rollback**: How to undo the actions if needed. Having a rollback on hand is a responsible action, and capturing it at the time of defining actions is convenient.

### Artifact D — Launch plan template structure (Appendix, pp. 35-39, extracted)

The template in the appendix organizes these sections:

1. **Status** — Stakeholder table with role, email, signoff (Marketing, Security, SRE, Product Manager, Technical Program Manager)
2. **Summary** — Scope, changes list, what is not in scope
3. **Related Documents** — Privacy document, design document, test plan, rollout plan
4. **Testing Guidelines** — Environment, whitelisting, what to test, test signals, bug triage
5. **Checks for Trusted Tester Stage** — Dev code/test complete, QA complete, UX/PM signoff, permissions
6. **Checks for Production Stage** — QA complete, final signoffs (legal/marketing/security/privacy), support page, EAP/TTP process, engineering partner signoff, production readiness, monitoring/alerts, metrics verified, stakeholder email
7. **Checks for Post-Launch Stage** — QA automation in regression suite, experiment cleanup
8. **Rollout Schedule** — Trusted tester (5+ days), Production 1% (~1 day, "Get SRE approval before each bump"), 5%, 20%, 100%, experiment cleanup
9. **Launch Monitoring** — Per component dashboards and metrics to monitor
10. **Plan for Emergency Rollback** — Decision makers, how to roll back, impact of rollback
11. **Product Success Metrics** — Logging to measure success/failure

### Artifact E — Dauntless case study: lessons learned (pp. 26-31, extracted)

**Scaling Session / 10X Exercise**: "If you expected a million players and 10 million showed up, what would happen? Would the game work? If not, what would break first in the game?"

**Load Simulation**: Team ran production-scale load test simulating thousands of players. Key learnings:
- DoS detection component triggered against legitimate load test traffic, causing a partial production outage
- Database replication not tested (replication disabled during load testing to save costs), leading to replica lag issues in production
- Load simulation "is not free from capital cost as well as operational costs" — developers built testing infrastructure instead of working on the game

**Post-Launch Autoscaling Fix**: "It turned out the autoscaler would have to be modified mid-launch in order to achieve its goals."

**Database Sharding**: "The team migrated these tables into a different storage system that could sustain that rate."

**Login Queue**: "Controlling the speed is often better than providing an unstable gaming experience for all players."

## Cross-References

- **Corroborates**:
  - `docs-google-sre-reliable-product-launches.md` — This is the most significant overlap. The existing note covers the SRE Book Ch27 (2017) LCE role, checklist methodology, and organizational process. This report (2019) provides the complementary *practical how-to*: the launch plan document template, day-of-execution procedures, and case study. **Claim 2** (launch stages/rollout schedule) in this note corroborates **Claim 10** (gradual rollouts) of the existing note — the template's 1%→5%→20%→100% schedule is a concrete instance of the canary pattern described there. **Claim 5** (Risks and Mitigations table) corroborates **Claim 4** (checklist questions substantiated by disaster) — both sources emphasize concrete, evidence-based risk capture. **Claim 7** (launch stages) corroborates the existing note's multiple references to staged rollouts. The sources are complementary: the LCE note provides the *who/process* framework, this report provides the *what/template* artifact.
  - `docs-google-sre-handling-overload.md` **Claim 2** (5× tested vs 50× actual — under-estimation of traffic) — the 10X worst-case exercise (Claim 12 here) corroborates the same pattern of systematic demand underestimation in launch planning. **Claim 4** (autoscaling before load shedding) — the Dauntless case study's autoscaling requirement (called out in design review, Claim 14 here) directly corroborates the principle that autoscaling must be functional before launch. **Claim 1** (load shedding must signal overload) — the Login Queue pattern (Claim 15 here) is a concrete instance of controlled demand management, corroborating the same principle from a pre-launch planning perspective.
  - `docs-google-sre-address-cascading-failures.md` — The Dauntless cold-cache scenario (resource consumption on cold cache after launch) traces to the same cascading-failure dynamics described in that note. The report's section on "Evaluate lifecycle expectations for the product's dependencies" (deprecated system risk) aligns with the cascading-failure trigger taxonomy.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` **Claim 1** (SLOs as shared vernacular) and **Claim 3** (team that writes code should create SLOs) — the source's SLO evaluation section (Claim 6) corroborates the importance of SLOs being defined and owned by product teams as part of launch readiness.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 1** (IR tooling is broader than chat/paging) — the command center section (Claim 11) corroborates the principle that launch-day operations require a multi-channel coordination system including the monitoring/observability/dashboard tooling mentioned in the Prodcast.

- **Contradicts**: None identified. The sources this report overlaps with are complementary rather than contradictory. Where both cover launch planning, the existing LCE note focuses on organizational process (who, governance) while this report focuses on the document artifact and execution (what, how). No contradiction issue filed.

- **Extends**:
  - `docs-google-sre-reliable-product-launches.md` — This report extends the existing LCE methodology with: (1) a concrete launch plan template (Appendix) with stage-specific checklists, rollout schedule, and emergency rollback plan; (2) the Dauntless case study showing launch planning in practice with specific failure-mode discoveries; (3) the 10X worst-case exercise methodology; (4) dark launch technique; (5) command center organization; (6) action item property framework (timing/owner/executor/status/verification/rollback); (7) post-launch monitoring requirements through full demand cycles. The existing note's Claims 1-17 are organizational process; this report provides the document templates and execution procedures that those processes would produce.
  - `docs-google-sre-handling-overload.md` — The Dauntless autoscaling mid-launch modification story extends this note's autoscaling claims with a real-world example of autoscaling deployment and adaptation during a launch event.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — The report's operational sustainability assessment (technology alignment, team capacity, technical debt) extends that note's discussion of operations team health with a pre-launch assessment framework.

- **Novel**: What here is entirely new to the corpus:
  - **Launch plan template** (Claim 16, Artifact D) — a complete reusable template with staged checks, rollout schedule, monitoring tables, emergency rollback plan. No existing source provides this artifact.
  - **Risks and Mitigations table format** (Claim 5, Artifact A) — the specific five-column table structure (risk area, description, failure mode, mitigation, status) as a launch planning tool.
  - **Dauntless game launch case study** (Claims 12-15, Artifact E) — the first game launch case study in the corpus, with specific patterns: 10X scaling exercise, DoS-during-load-test, autoscaling mid-launch adaptation, database replication gap from cost-savings, Login Queue pattern.
  - **10X worst-case exercise methodology** (Claim 12) — a specific scaling review technique with risk-grouping-by-likelihood. Not present in existing notes.
  - **Dark launch technique** (Claim 8) — the pattern of deploying features to production without user-visible results for canary validation.
  - **Launch action item properties** (Claim 9, Artifact C) — the six-property framework (timing, owner, executor, status, verification, rollback) with owner/executor separation principle.
  - **Command center organization** (Claim 11) — launch-day command center composition with cross-functional roles (SMEs, on-call, marketing, executives), communication fallback planning, and paper-backup recommendation.
  - **Four-horizon traffic estimation** (Claim 4) — specific time ranges for demand projection with accuracy-weighting guidance.
  - **Operational sustainability quantification** (Claim 18) — the 5-10% vs 40-80% operational cost ranges for technology-aligned vs non-aligned products. No existing source quantifies this tradeoff.
  - **Post-launch demand cycle monitoring** (Claim 17) — the requirement to monitor through full demand cycles and replace temporary mitigations with permanent solutions, with cycle taxonomy (day-night, weekday-weekend, flash events).
  - **Launch plan "point of no return" concept** (Claim 3) — the notion that some launch commitments become irreversible, requiring Plan B/C backup plans with explicit invocation conditions.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability / Release Engineering)**: The most impacted chapter. Add a dedicated "Launch Planning for AI Services" subsection with: (a) the launch plan template (Artifact D) adapted for AI/LLM model rollouts — add AI-specific Production Stage checks (model quality gate, guardrail validation, cost-per-request monitoring, GPU capacity), AI-specific rollout schedule (canary model version, prompt version tracking), and AI-specific rollback plan (model version revert, prompt revert, cache invalidation); (b) the 10X worst-case exercise methodology (Claim 12) as a scaling review standard for AI inference — test 10× expected tokens/sec, 10× concurrent users, 10× prompt volume; (c) the Login Queue pattern (Claim 15) as a demand management technique for AI services — admit requests at controlled rate during overload with user-visible queue position; (d) the dark launch technique (Claim 8) for shadow-deploying new AI models — serve responses but discard in frontend, enabling quality comparison without user exposure; (e) the action item property framework (Claim 9, Artifact C) as a template for AI launch runbook entries — each AI deployment step must define rollback upfront; (f) the four-horizon traffic estimation (Claim 4) for AI capacity planning — GPU/TPU provisioning must account for launch-day spikes separately from steady-state growth. Currently Ch05 has no launch planning subsection; this report provides the complete practical framework.

- **Chapter 02 (Incident Response and Reliability Fundamentals)**: Add the 10X worst-case exercise (Claim 12) to reliability fundamentals — the rule of thumb that systems fail under 10× designed demand. Add the Dauntless DoS-during-load-test pattern (Claim 13) as a cautionary example: monitoring/detection systems may trigger against legitimate load tests. Add the cold-cache resource consumption scenario (resource section) as a failure mode example relevant to AI inference cache warmup. Add the "point of no return" concept (Claim 3) to incident response fundamentals — some launch commitments become irreversible, requiring pre-planned contingency.

- **Chapter 03 (Runbooks and Agents)**: Add the launch action item property framework (Claim 9, Artifact C) as a template for AI agent deployment runbooks — each agent deployment step should specify timing, owner, executor, status, verification, and rollback. Add the command center composition (Claim 11) as guidance for AI launch coordination — an AI model launch command center must include ML engineers, inference platform SRE, safety/guardrail engineers, product managers, and communications staff.

- **Chapter 00 (Principles)**: Add the "hope is not a strategy for launches" principle (Claim 2) and the "Plan B, Plan C" backup planning principle (Claim 3) to the reliability philosophy section. Add the operational sustainability quantification principle (Claim 18) — technology alignment decisions produce measurable operational cost differences (5-10% vs 40-80%) that should inform AI platform investment priorities.

- **Chapter 04 (Oncall and Toil)**: Add the operational sustainability assessment framework (Claim 18) to the toil management section — teams evaluating new AI products should assess whether the product's technology stack aligns with existing practices, using the quantified ranges as decision support. Add the post-launch demand-cycle monitoring requirement (Claim 17) — post-AI-launch monitoring must cover full demand cycles before declaring stability.

## Extraction Notes

- The source URL in the issue body (`https://sre.google/static/pdf/CreatingProductionLaunchPlan.pdf`) redirects to `https://static.googleusercontent.com/media/sre.google/en//static/pdf/CreatingProductionLaunchPlan.pdf`. The actual PDF was fetched and read fully (45 pages, 1,639 lines extracted via pdftotext). The PDF was confirmed as a valid document via `file` identification (PDF v1.7, zip deflate encoded).
- This is the same PDF referenced in the triage comments as a "standalone O'Reilly report (45 pages, 2020)" — the publication date in the colophon is November 2019 (First Edition, 2019-11-13). The triage comments are close enough (2020 vs 2019); the actual publisher date is used in the frontmatter.
- The report explicitly references Chapter 27 of the SRE Book ("Reliable Product Launches at Scale") as a further-reading companion — confirming the complementary relationship identified by the Prospector. The report covers the concrete "how" (launch plan document, template, day-of procedures) while Ch27 covers the organizational "who/process" (LCE role, checklist governance).
- The Dauntless game launch case study (pp. 26-31) is the report's most concrete pattern source. The case study covers Google Cloud + Phoenix Labs collaboration on the free-to-play RPG launched publicly in May 2019, with planning beginning in mid-2018 (~1 year lead time). Key patterns extracted in Claims 12-15.
- Quotes were extracted directly from the PDF text (pdftotext -layout output). The PDF text extraction preserved paragraph content accurately. All quotes in quotation marks were verified against the extracted text. Spot-check any quote against the original PDF if higher fidelity is needed.
- One candidate from `miner-related-notes.md` — `docs-google-sre-prodcast-03-11-embracing-complexity.md` (score 0.30) — has the highest lexical overlap but addresses complexity of sociotechnical systems, not launch planning methodology. Low direct relevance to this source. Dismissed after reading its claims.
- `docs-google-sre-prodcast.md` (score 0.25) — SRE Prodcast index page, no launch-specific content. Dismissed.
- `docs-google-sre-prodcast-02-08-life-beyond-google.md` (score 0.225) — SRE concepts transferability, not launch planning. Dismissed.
- `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` (score 0.225) — AI for SRE tools. Dismissed.
- `docs-google-sre-prodcast-03-05-building-reliable-systems.md` (score 0.20) — databases and reliability culture. Low direct relevance. Dismissed.
- `docs-google-sre-prodcast-04-09-ai-agents.md` (score 0.20) — AI agents in production. Low direct relevance. Dismissed.
- `docs-google-sre-nalsd-classroom.md` — NALSD design methodology. Tangential relevance (architecture design for reliability, which feeds into launch planning). Not a direct cross-reference. Dismissed.
- No contradictions were found against existing source notes. The report's claims about launch planning methodology, risk management, and the Dauntless case study are complementary to existing sources. In particular, the relationship with the existing LCE note (`docs-google-sre-reliable-product-launches.md`) is explicitly complementary rather than contradictory — as the report itself cites Chapter 27 as further reading. No contradiction issue filed.
