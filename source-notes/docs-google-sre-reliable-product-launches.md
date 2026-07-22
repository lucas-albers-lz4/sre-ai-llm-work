---
source_url: https://sre.google/sre-book/reliable-product-launches/
source_type: documentation
title: "Reliable Product Launches at Scale — SRE Book Chapter 27"
author: Rhandeev Singh and Sebastian Kirsch with Vivek Rau (Google SRE)
date_published: 2017
date_extracted: 2026-07-22
last_checked: 2026-07-22
status: current
confidence_overall: settled
issue: "#409"
---

# Reliable Product Launches at Scale — SRE Book Chapter 27

> The canonical Google SRE treatment of launch coordination engineering: the Launch Coordination Engineer (LCE) role, the launch checklist methodology, checklist theme taxonomy (architecture, capacity, failure modes, client behavior, processes, rollout), gradual/staged rollout patterns, feature flag frameworks, and the evolution of LCE at Google. Provides the launch-process framework that the guide's AI/LLM deployment patterns can reference for release engineering, canary testing, and pre-launch readiness reviews for AI/agent rollouts.

## Source Context

- **Type**: documentation — Chapter 27 of the Site Reliability Engineering book (O'Reilly, 2017), authored by Rhandeev Singh and Sebastian Kirsch with Vivek Rau, edited by Betsy Beyer. Hosted on sre.google.
- **Author credibility**: Highest credibility. The SRE Book is the foundational text of the SRE discipline, published by Google and O'Reilly. The authors are named Google SRE practitioner-authors with direct experience running the Launch Coordination Engineering team. The chapter has been peer-reviewed through Google's internal SRE review process and the O'Reilly publication pipeline. The content is hosted on the official sre.google domain under a CC BY-NC-ND 4.0 license.
- **Scope**: Covers (a) Launch Coordination Engineering (LCE) as a role, team structure, and consulting methodology; (b) launch checklist design principles and curation guidelines; (c) the nine checklist themes — Architecture & Dependencies, Integration, Capacity Planning, Failure Modes, Client Behavior, Processes & Automation, Development Process, External Dependencies, Rollout Planning — each with example questions and action items; (d) gradual and staged rollout patterns including canary testing; (e) feature flag framework design requirements; (f) client behavior management (backoff, jitter, server-side config control); (g) overload behavior and load testing; (h) the historical evolution of LCE at Google from 2004 onward with specific metrics (350 launches per LCE in 3.5 years, 30% low-risk by 2008); (i) three problems LCE didn't solve (scalability changes, growing operational load, infrastructure churn). Does NOT cover AI/LLM workloads directly — the patterns are general SRE launch process knowledge directly applicable to LLM model rollouts, AI agent deployments, and AI feature releases.

## Extracted Claims

### Claim 1: SRE created a dedicated Launch Coordination Engineering (LCE) consulting team to enable rapid launches without compromising site stability — the team audited products, acted as liaison, drove technical aspects, gatekept launches, and educated developers
- **Evidence**: Authoritative SRE Book chapter description of the LCE role and its functions. The role was created because engineers coding new products "may be unfamiliar with the challenges and pitfalls of launching a product to millions of users." The LCE team sits within SRE and is staffed by software and systems engineers with "strong communication and leadership skills."
- **Confidence**: settled
- **Quote**: "to enable a rapid pace of change without compromising stability of the site"
- **Our assessment**: The LCE role pattern is directly transferable to AI/LLM operations. A dedicated launch review function for AI model rollouts — responsible for auditing compliance, coordinating across infra/ML/research teams, gating releases, and educating researchers/producers on production requirements — would address a gap the guide's Ch03 and Ch05 identify (ad-hoc AI release processes without formal readiness review). The three advantages cited (breadth of experience across product areas, cross-functional perspective, objectivity as a nonpartisan advisor) apply equally to AI/LLM release engineering.

### Claim 2: Google defines a "launch" as any externally visible code change and performs up to 70 launches per week — this pace both necessitates and enables a streamlined launch process
- **Evidence**: The chapter's "Launching at Internet Scale" section provides the definition and pace metric. Internet companies iterate rapidly because features roll out server-side, unlike traditional firms that launch slowly. A firm launching once every three years does not need a launch process and has no data to refine it.
- **Confidence**: settled
- **Quote**: "any new code that introduces an externally visible change to an application"
- **Our assessment**: The definition is broad enough to cover AI/LLM deployments (new model version, new agent behavior, changed prompt, updated guardrail) and the 70/week pace contextualizes why process investment pays off. For AI/LLM systems where model updates can happen weekly or daily, the same logic applies: a launch process that feels burdensome at 1 launch/year is essential at 50+ launches/year. The mention of "server-side" rollouts is prescient for AI — most LLM feature changes are server-side (prompt changes, model swaps, parameter tuning) and invisible to clients, which is the exact scenario that enables rapid iteration without app-store updates.

### Claim 3: A good launch process must meet five sometimes-conflicting criteria — lightweight, robust, thorough, scalable, adaptable — requiring continuous balancing
- **Evidence**: The chapter enumerates these five criteria explicitly with one-line definitions. "Some of these requirements are at odds" — the conflict between lightweight and thorough requires active management through simplicity, high-touch customization by experienced engineers, and fast common paths for repeated patterns.
- **Confidence**: settled
- **Quote**: "Easy on developers"
- **Quote**: "Catches obvious errors"
- **Quote**: "Addresses important details consistently and reproducibly"
- **Our assessment**: These criteria form a design brief for any AI/LLM launch process. The lightweight requirement is especially salient: if the launch process for a model update is too heavy, "engineers are likely to sidestep processes that they consider too burdensome" — meaning the process must be tuned to the launch cadence. For AI systems where teams may be iterating daily, the process should default to simple (fast common paths) with escalation to thorough for high-risk launches (new model architecture, first production deployment, public-facing agent).

### Claim 4: Every launch checklist question must be substantiated by a previous launch disaster, and every instruction must be concrete and practical — enforced by VP-level approval for new questions
- **Evidence**: The chapter describes these curation rules. Google at one point required "adding new questions to Google's launch checklist required approval from a vice president" to keep the checklist from growing unbounded. The two guidelines are stated explicitly. The checklist needs "continuous attention" as recommendations, systems, and concerns change, with LCEs making small updates continuously and reviewing the entire checklist once or twice a year.
- **Confidence**: settled
- **Quote**: "Every question's importance must be substantiated, ideally by a previous launch disaster."
- **Quote**: "Every instruction must be concrete, practical, and reasonable for developers to accomplish."
- **Our assessment**: This is one of the highest-value transferable patterns in the chapter. For AI/LLM launch checklists, the "substantiated by disaster" rule prevents speculative questions about unlikely failure modes from bloating the checklist. Every readiness review question for an AI model launch should cite a real incident (e.g., "request deadline required — an LLM inference node without request deadlines previously caused thread pool exhaustion under load"). The VP-level approval gate is a mechanism the guide could recommend for AI launch checklist governance.

### Claim 5: The launch checklist can drive convergence on common infrastructure — replacing long sections on custom solutions with single-line recommendations to use hardened internal platforms
- **Evidence**: The chapter's "Driving Convergence and Simplification" section. Engineers without guidance "are likely to re-implement existing solutions." LCEs, having broad visibility, can recommend standard infrastructure — for example, replacing "a long section on rate limiting" with a single recommendation to "Implement rate limiting using system X." LCEs witness stumbling blocks firsthand and can streamline processes.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: A powerful pattern for LLM infrastructure. Instead of each model team building custom rate limiting, custom guardrails, and custom monitoring, the LCE-equivalent role can mandate standard infrastructure (e.g., "Use the shared LLM gateway for rate limiting and admission control" instead of each team writing their own). This is particularly relevant for organizations where multiple AI product teams each build bespoke inference stacks — a common anti-pattern this claim directly addresses.

### Claim 6: Architecture review should map request flow from user to backend, identify request types with different latency requirements, and validate request volume assumptions — one page view can turn into many requests
- **Evidence**: Chapter's "Architecture and Dependencies" section. The action items are explicit: "Isolate user-facing requests from non user–facing requests" and "Validate request volume assumptions. One page view can turn into many requests."
- **Confidence**: settled
- **Quote**: "Isolate user-facing requests from non user–facing requests"
- **Our assessment**: The "one page view can turn into many requests" warning applies strongly to LLM-powered applications. A single user prompt to an AI agent may generate: one chat completion call, one embedding call, one content-filter call, two retrieval calls, and one summarization call. The architecture review must model the full fan-out from a single user action. The isolation principle applies to separating interactive chat traffic from batch/background AI processing.

### Claim 7: Capacity planning must account for spikes up to 15× higher than estimates from publicity — "public interest is notoriously hard to predict" — and redundancy requires 4-5 deployments for 3 needed
- **Evidence**: The chapter's "Capacity Planning" section. "Some Google products saw spikes up to 15× higher than estimated." Launch region-by-region to build confidence. If three deployments are needed for peak traffic, four or five are needed to handle maintenance and failures. Resources often have long lead times.
- **Confidence**: settled
- **Quote**: "Public interest is notoriously hard to predict"
- **Our assessment**: The 15× figure is a concrete benchmark for LLM capacity planning. An AI model that goes viral (e.g., a new model release generating sudden interest) can produce traffic far exceeding estimates. The N+2 redundancy guidance (3 needed → 4-5 provisioned) is directly applicable to inference clusters. The region-by-region rollout pattern is especially important for LLM services with multi-region deployment — launching one region at a time builds confidence before global expansion.

### Claim 8: Client behavior patterns change fundamentally with auto-initiated actions — phone syncing, auto-refresh, and heartbeats replace human click rates as the traffic driver
- **Evidence**: Chapter's "Client Behavior" section. "On traditional websites, request rates are limited by user click speed." Auto-initiated changes this. Action items: "Make sure that your client backs off exponentially on failure" and "Make sure that you jitter automatic requests."
- **Confidence**: settled
- **Quote**: "Make sure that your client backs off exponentially on failure"
- **Our assessment**: For LLM API clients (SDKs, agent frameworks, chat apps), this claim is directly applicable. An LLM SDK with auto-retry on failure without exponential backoff can generate orders of magnitude more load than a human clicking refresh. The jitter requirement applies to scheduled inference workloads (e.g., batch evaluation jobs all firing at the top of the hour). This is a settled SRE pattern, but the chapter's placement in a launch checklist context ensures it is considered during pre-launch review rather than discovered post-mortem.

### Claim 9: All manual processes must be documented before launch — "to ensure that the information is translated from an engineer's mind onto paper while it is still fresh" — and documentation must be sufficient for any team member to execute in an emergency
- **Evidence**: Chapter's "Processes and Automation" section. The chapter notes not everything can be automated, and remaining processes need documentation. Example action items: "Document all manual processes," "Document the process for moving your service to a new datacenter," "Automate the process for building and releasing a new version."
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: For AI/LLM services, the pre-launch documentation requirement is particularly valuable because model behavior and failure modes may be less well-understood than traditional services. Documenting manual inference-serving processes (model reload procedure, GPU node replacement, fallback model activation) before launch ensures the information is captured while the deploying engineer's knowledge is current. The "any team member can execute in an emergency" standard is a concrete rubric: if the documentation for reloading a model requires the original MLE's notebook access, it fails the test.

### Claim 10: Gradual rollouts with canary testing are the standard deployment pattern — install on a few machines, observe, scale to full datacenter, observe, then global — with automatic rollback when validation fails
- **Evidence**: Chapter's "Gradual and Staged Rollouts" section. "Very few launches at Google are of the 'push-button' variety." Canary servers "detect dangerous effects from the behavior of the new software under real user traffic." Internal tools "observe the newly started server for a while" and "if the change doesn't pass the validation period, it's automatically rolled back."
- **Confidence**: settled
- **Quote**: "if the change doesn't pass the validation period, it's automatically rolled back"
- **Our assessment**: The canary pattern is standard in traditional SRE but must be adapted for AI/LLM deployments. An LLM model canary requires: (1) routing a percent of inference traffic to the new model version, (2) automated quality/performance metrics (not just latency/error-rate), (3) model-specific health signals (perplexity shift, output distribution drift, refusal rate change). The automatic rollback on validation failure is a critical design requirement for AI/LLM canary systems — a new model that degrades quality should be rolled back without human intervention. The chapter's description of gradual rollouts for non-server software (Android app updates to a subset of users) is a precedent for AI agent behavioral canaries (enabling a new agent behavior for a subset of users/traffic).

### Claim 11: Feature flag frameworks require six capabilities — parallel rollout, gradual increase (1-10%), traffic routing by user/session/location, automatic failure handling, immediate independent reversion, and user-experience measurement — and "can pay for its engineering investment"
- **Evidence**: Chapter's "Feature Flag Frameworks" section enumerates the six requirements. The ROI statement is explicit. Two classes of frameworks exist: those for UI improvements and those supporting server-side/business logic changes. The simplest UI framework is an HTTP payload rewriter at frontend servers for a subset of cookies.
- **Confidence**: settled
- **Quote**: "Automatically handle failure of the new code paths by design, without affecting users"
- **Quote**: "Independently revert each such change immediately in the event of serious bugs or side effects"
- **Our assessment**: Feature flags are even more important for AI/LLM systems than for traditional services because model behavior changes are harder to predict from unit tests. The six requirements map to AI feature flags: parallel rollout (A/B test model versions), gradual increase (ramp traffic to new model), routing by user/session (enterprise vs free tier), automatic failure handling (fall back to previous model if quality degrades), immediate reversion (rollback without redeploy), and UX measurement (track per-model quality metrics). The "pays for its engineering investment" claim is supported by the chapter's evidence but should be verified for AI-specific contexts where model API costs may reduce the ROI.

### Claim 12: Overload behavior is hard to predict from first principles — a real example showed logging debugging info on backend errors was more expensive than handling the normal case, creating a self-reinforcing slowdown
- **Evidence**: Chapter's "Overload Behavior and Load Tests" section. A concrete example: "it turned out that logging debugging information was more expensive than handling the backend response in a normal case." As the service became overloaded and timed out, it spent more CPU on logging, timing out more requests until it ground to a halt. The JVM equivalent is"GC thrashing" where memory management consumes most CPU. Because overload behavior is hard to predict, "load tests are invaluable and required for most launches."
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The logging-debugging example has a direct LLM analog: verbose token-level logging or full prompt/response audit logging that becomes more expensive under load, creating the same positive feedback loop. Under overload, an LLM gateway that logs full prompt/response pairs for debugging will consume more CPU/memory, further slowing inference throughput. The lesson: audit pre-launch what code paths become more expensive under load. The "load tests are required for most launches" standard is a concrete recommendation the guide can adopt for AI model launches.

### Claim 13: LCE at Google processed over 1,500 launches in 3.5 years with an average team of 5 engineers — 30% of launches qualified as low-risk by 2008 and faced a simplified checklist
- **Evidence**: Chapter's "Evolution of the LCE Checklist" section. "One LCE ran 350 launches through the LCE Checklist" in 3.5 years. With "the team averaging five engineers," this is "over 1,500 launches in 3.5 years." A new LCE hire needs "about six months of training." Low-risk categories were identified — launches with no new server executables and under 10% traffic increase faced a trivial checklist. By 2008, "30% of reviews were considered low-risk."
- **Confidence**: settled
- **Quote**: "over 1,500 launches in 3.5 years"
- **Quote**: "30% of reviews were considered low-risk"
- **Our assessment**: These metrics provide concrete sizing guidance for launching an LCE-equivalent team for AI/LLM operations. The 350 launches per LCE in 3.5 years (~100/year per engineer) establishes a baseline throughput. The low-risk categorization pattern — identifying launches that change no server code and increase traffic under 10% — is directly transferable to AI model rollouts: a prompt-only change with no model swap could qualify as low-risk. The six-month ramp time for new LCEs is notable: it suggests that building domain expertise in launch processes takes significant time, and organizations should plan for this ramp when staffing AI launch engineering roles.

### Claim 14: Three structural problems LCE didn't solve — scalability changes (products exceeding estimates by 100×+), growing operational load (manual work compounding without control), and infrastructure churn ("running fast just to stay in the same place")
- **Evidence**: Chapter's "Problems LCE Didn't Solve" section enumerates each. Scalability changes: when products "exceed initial estimates by more than two orders of magnitude," a complete rearchitecture is needed. Operational load: "Noisiness of automated notifications, complexity of deployment procedures, and the overhead of manual maintenance work tend to increase over time." SRE aims to keep operational work below 50% (Ch5 reference). Infrastructure churn: as features are deprecated, "service owners must continually modify their configurations and rebuild their executables" — "running fast just to stay in the same place." Solutions require company-wide efforts — "better platform APIs, continuous build/test automation, and greater standardization across production services."
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The three unsolved problems are a reality check for any LCE-equivalent program. For AI/LLM operations: scalability changes apply when an AI service goes from pilot (100 users) to production (1M+ users), requiring inference architecture redesign. Operational load applies to AI-specific manual work: model fine-tuning pipelines, manual prompt engineering, ad-hoc evaluation runs. Infrastructure churn applies most acutely: AI infrastructure (model serving frameworks, GPU orchestration, prompt management, guardrail systems) is evolving rapidly, meaning AI platform teams will spend significant effort "running fast just to stay in the same place." The chapter's honesty about what LCE didn't solve is valuable for setting expectations — a launch coordination function for AI is necessary but not sufficient; it must be paired with platform investment.

### Claim 15: The LCE model is most valuable for companies planning to "double its product developers every one or two years," scale to hundreds of millions of users, and maintain reliability despite rapid change — achieving "safety without impeding change"
- **Evidence**: Chapter's conclusion. The LCE team was Google's solution to "the problem of achieving safety without impeding change." The chapter expresses hope that "our approach will help inspire others facing similar challenges." The specific conditions for LCE applicability are stated: rapid developer growth, massive user scale, and reliability as a priority despite high change velocity.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: These conditions map well to the AI/LLM industry context (2026): organizations are rapidly hiring ML/LLM engineers, AI services are scaling to millions of users, and reliability is increasingly prioritized after high-profile AI outages. The "safety without impeding change" framing is the core design goal for AI release engineering — a launch process that is *perceived* as a gating bottleneck will be circumvented. The chapter's 10+ year evolution (from volunteer Launch Engineers in 2002 to full LCE team in 2004 to 30% low-risk streamlined process by 2008) provides a realistic timeline for organizations building their own AI launch coordination function.

### Claim 16: External dependencies require proactive identification and mitigation — third-party code, services, data, and events that the launch depends on, including partners who need notification and vendor deadline contingencies
- **Evidence**: Chapter's "External Dependencies" section. Example questions: "What third-party code, data, services, or events does the service or the launch depend upon?" "Do any partners depend on your service?" "What happens if you or the vendor can't meet a hard launch deadline?" Google has used "filtering/rewriting proxies, data transcoding pipelines, and caches to mitigate risks" from external dependencies.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: For AI/LLM services, external dependencies are especially critical and often underappreciated at launch. Dependencies include: third-party LLM APIs (OpenAI, Anthropic, Google), embedding model APIs, vector database providers, content filter/guardrail services, model registry services, and data providers. The "vendor can't meet a hard launch deadline" question is directly relevant: if a model launch is timed to a product launch and the third-party model provider has an outage, what's the contingency? The mitigation techniques (filtering/rewriting proxies, caches) translate to: an AI gateway that can fail over between model providers, cached responses for fallback, and prompt-level content filtering as a secondary guardrail.

### Claim 17: Client retry behavior must be controlled server-side via config files that enable/disable features and set sync frequency — "releasing a new version becomes much easier if we don't need to maintain parallel release tracks"
- **Evidence**: Chapter's "Dealing with Abusive Client Behavior" section. An app can "periodically download a config file enabling or disabling features or setting parameters like sync frequency." Client configuration may enable "dormant functionality." Benefits include easier versioning (no parallel release tracks) and easier launch abortion (switch feature off, iterate, release update).
- **Confidence**: settled
- **Quote**: "releasing a new version becomes much easier if we don't need to maintain parallel release tracks"
- **Our assessment**: The server-side config pattern directly applies to AI/LLM client SDKs and agent frameworks. An AI SDK can download a config file specifying: which model endpoints are active, retry parameters, timeout values, fallback model IDs, feature flags for beta capabilities. This enables the "dormant functionality" pattern for AI: a new agent behavior can be deployed to the client SDK but disabled by default, activated server-side when ready, and deactivated if issues arise — without requiring a client update. The "no parallel release tracks" benefit is significant for AI where client SDKs are often versioned independently.

## Concrete Artifacts

### Artifact A — NORAD Tracks Santa case study (Chapter opening, verbatim)

The Keyhole service normally serves "thousands of satellite images per second." On Christmas Eve 2011, it received 25× its normal peak — "over a million requests per second" — from the NORAD Santa-tracking website. "Never underestimate the power of millions of kids anxious for presents." Kill switches were nicknamed "Make-children-cry switches" to remind engineers of the human impact of failure.

### Artifact B — The launch checklist theme taxonomy (Chapter "Developing a Launch Checklist" section)

```
1. Architecture and Dependencies
   - "What is your request flow from user to frontend to backend?"
   - "Isolate user-facing requests from non user–facing requests."
   - "Validate request volume assumptions. One page view can turn into many requests."

2. Integration
   - "Set up a new DNS name for your service."
   - "Set up load balancers to talk to your service."
   - "Set up monitoring for your new service."

3. Capacity Planning
   - "Is this launch tied to a press release, advertisement, blog post, or other form of promotion?"
   - "How much traffic and rate of growth do you expect during and after the launch?"
   - "Have you obtained all the compute resources needed to support your traffic?"

4. Failure Modes
   - "Do you have any single points of failure in your design?"
   - "How do you mitigate unavailability of your dependencies?"
   - "Implement request deadlines to avoid running out of resources for long-running requests."
   - "Implement load shedding to reject new requests early in overload situations."

5. Client Behavior
   - "Do you have auto-save/auto-complete/heartbeat functionality?"
   - "Make sure that your client backs off exponentially on failure."
   - "Make sure that you jitter automatic requests."

6. Processes and Automation
   - "Are there any manual processes required to keep the service running?"
   - "Document all manual processes."
   - "Document the process for moving your service to a new datacenter."
   - "Automate the process for building and releasing a new version."

7. Development Process
   - "Check all code and configuration files into the version control system."
   - "Cut each release on a new release branch."

8. External Dependencies
   - "What third-party code, data, services, or events does the service or the launch depend upon?"
   - "Do any partners depend on your service? If so, do they need to be notified of your launch?"
   - "What happens if you or the vendor can't meet a hard launch deadline?"

9. Rollout Planning
   - "Set up a launch plan that identifies actions to take to launch the service. Identify who is responsible for each item."
   - "Identify risk in the individual launch steps and implement contingency measures."
```

### Artifact C — Feature flag framework requirements (Chapter "Feature Flag Frameworks" section, verbatim)

```
- "Roll out many changes in parallel, each to a few servers, users, entities, or datacenters"
- "Gradually increase to a larger but limited group of users, usually between 1 and 10 percent"
- "Direct traffic through different servers depending on users, sessions, objects, and/or locations"
- "Automatically handle failure of the new code paths by design, without affecting users"
- "Independently revert each such change immediately in the event of serious bugs or side effects"
- "Measure the extent to which each change improves the user experience"
```

### Artifact D — LCE historical metrics (Chapter "Development of LCE" section)

```
Year   | Event
-------|-------
~2002  | Small band of experienced engineers ("Launch Engineers") volunteer as consulting team
2004   | SRE staffs a small full-time LCE team
~2008  | 30% of reviews considered low-risk → simplified checklist for low-risk launches
3.5yr  | One LCE ran 350 launches; team of 5 → "over 1,500 launches in 3.5 years"
       | New LCE hire needs ~6 months training
```

### Artifact E — Overload feedback loop example (Chapter "Overload Behavior and Load Tests" section)

A service logged debugging information on backend errors. "It turned out that logging debugging information was more expensive than handling the backend response in a normal case." As the service became overloaded and timed out, it spent more CPU logging, timing out even more requests until it ground to a halt. In JVM systems, a similar effect is "GC (garbage collection) thrashing" where memory management consumes most CPU.

### Artifact F — LCE responsibilities (Chapter "Launch Coordination Engineering" section, verbatim)

```
- "Auditing products and services for compliance with Google's reliability standards and best practices"
- "Acting as a liaison between the multiple teams involved in a launch"
- "Driving the technical aspects of a launch by making sure that tasks maintain momentum"
- "Acting as gatekeepers and signing off on launches determined to be 'safe'"
- "Educating developers on best practices and on how to integrate with Google's services"
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-handling-overload.md` **Claim 2** (capacity gaps — 5× tested vs 50× actual in Pokémon GO) — the launch chapter's claim that capacity spikes can reach 15× higher than estimates (Claim 7 here) corroborates the same pattern with a different quantified example. Both sources agree that launch traffic estimates are systematically underestimates, with the launch chapter attributing the gap to "public interest is notoriously hard to predict."
  - `docs-google-sre-handling-overload.md` **Claim 3** (synchronized retries without jitter, 20× RPS spike) — the launch chapter's Client Behavior checklist (Claim 8 here) recommends exponential backoff and jitter, corroborating the same client-behavior pattern from a checklist/prevention perspective rather than a post-mortem perspective.
  - `docs-google-sre-handling-overload.md` **Claim 7** (progressive load shedding) — the launch chapter's Failure Modes checklist recommends "Implement load shedding to reject new requests early in overload situations" (Claim 7 here), corroborating the same principle from the pre-launch checklist perspective.
  - `docs-google-sre-address-cascading-failures.md` **Claim 14** (immediate mitigation hierarchy — drop traffic aggressively as first response) — the launch chapter's rollout planning checklist (Claim 16 here) including "identify risk in the individual launch steps and implement contingency measures" is the pre-launch planning side of the same practice.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` **Claim 16** (fast-error attracting traffic from latency LB) — the launch chapter's overload example (Claim 12 here) demonstrates the same positive feedback loop via a different mechanism (logging cost > normal processing cost).
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — the Prodcast episode covers AI agents in production and their reliability gaps; the launch chapter provides the formal launch process framework that such agents need before production deployment.
  - `docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md` — Zelesko's vision of agentic SRE aligns with the automated aspects of the launch checklist (automated canary validation, automatic rollback on validation failure).

- **Contradicts**: None identified. This chapter covers launch process design, which is complementary to the overload-handling and cascading-failure patterns in existing notes. The three "problems LCE didn't solve" (Claim 14) are presented as honest limitations of the approach, not contradictions with other sources. The chapter's explicit acknowledgement that "engineers are likely to sidestep processes that they consider too burdensome" is consistent with the existing corpus's emphasis on lightweight, engineer-friendly tooling. No contradiction issue filed.

- **Extends**:
  - The existing Google SRE source notes cover specific reliability domains — overload handling (`docs-google-sre-handling-overload.md`), cascading failures (`docs-google-sre-address-cascading-failures.md`), and the Prodcast corpus covers SRE culture and practices. This note provides the *launch process framework* that these domains fit into: load shedding, capacity planning, and failure mode analysis are not standalone practices but checklist items in a coordinated launch process. The chapter's checklist taxonomy (Artifact B) organizes the existing corpus's scattered checklist references into a comprehensive pre-launch review.
  - `docs-google-sre-prodcast-01-07-on-call-rotations.md` — the Prodcast's discussion of on-call readiness is extended by the launch chapter's Processes and Automation checklist (Claim 9): documenting manual processes before launch ensures on-call engineers can execute procedures in an emergency.
  - `docs-google-sre-nalsd-classroom.md` — the NALSD design methodology is the *architecture* framework for building reliable systems; this chapter provides the *launch* framework for deploying them. Together they cover the build-and-deploy lifecycle.

- **Novel**: Entirely new to the corpus:
  - **Launch Coordination Engineering (LCE) role** (Claims 1, 13, 15) — the concept of a dedicated launch-process role within SRE, its responsibilities, organizational positioning, and staffing model. No existing note describes this function.
  - **Launch checklist curation guidelines** (Claim 4) — the "substantiated by disaster" and "concrete instructions" rules with VP-level approval governance. A process-design principle not present elsewhere.
  - **Checklist theme taxonomy** (Artifact B) — the complete 9-theme architecture (Architecture, Integration, Capacity, Failure Modes, Client Behavior, Processes, Development, External Dependencies, Rollout Planning). While individual themes appear across existing notes, no source provides this comprehensive launch checklist structure.
  - **Feature flag framework requirements** (Claim 11, Artifact C) — the six specific requirements (parallel rollout, gradual increase, traffic routing, automatic failure handling, immediate reversion, UX measurement). The existing corpus mentions feature flags in passing (Ch03) but lacks the design specification.
  - **LCE historical evolution and metrics** (Claim 13, Artifact D) — the specific throughput data (350 launches/LCE, 1,500 launches in 3.5 years, 30% low-risk by 2008). Provides sizing guidance for an AI launch engineering function.
  - **LCE's three unsolved problems** (Claim 14) — scalability changes, operational load growth, infrastructure churn. A candid limitation analysis that sets expectations for what launch process can and cannot solve, absent from existing notes.
  - **Overload feedback loop via expensive logging** (Claim 12, Artifact E) — the specific dynamic where error-path logging costs more than normal processing, creating a self-reinforcing slowdown. Related to but distinct from the fast-error-attracting-LB-traffic pattern already in the corpus.
  - **NORAD Tracks Santa case study** (Artifact A) — the 25× traffic spike with human-impact framing (kill switches as "Make-children-cry switches"). A vivid launch-risk illustration.
  - **Server-side client config control** (Claim 17) — the pattern of controlling client behavior (sync frequency, feature toggles, retry parameters) via downloadable config files rather than client releases, enabling "dormant functionality."

## Guide Impact

- **Chapter 05 (LLM Ops Reliability / Release Engineering)**: The most impacted chapter. Add a dedicated "Launch Engineering for AI Services" subsection with: (a) the LCE role definition and responsibilities (Claim 1, Artifact F) as a recommended function for AI release engineering — a designated engineer or team responsible for launch readiness reviews for model/agent deployments; (b) the 9-theme launch checklist (Artifact B) adapted for AI launches, with LLM-specific questions under each theme (e.g., under Failure Modes: "Is there a fallback model if the primary model is unavailable? What is the token-level OOM behavior?"); (c) the checklist curation guidelines (Claim 4) as governance for AI launch process evolution — every AI launch question must be substantiated by a real incident; (d) the feature flag framework requirements (Claim 11, Artifact C) as a design spec for AI feature flag systems — canary model deployments require automatic rollback on quality metric degradation; (e) gradual rollout patterns (Claim 10) with canary testing as the standard for AI model rollouts; (f) the overload logging example (Claim 12, Artifact E) as a pattern for AI inference: verbose token-level logging becomes more expensive under load, creating the same feedback loop. Currently Ch05 has a high-level "release management" section referencing earlier SRE Book chapters but no dedicated launch process framework. This note provides the complete framework.

- **Chapter 03 (Runbooks and Agents)**: Add the server-side client config pattern (Claim 17) as a design principle for AI agent SDKs — agent behavior should be controllable via server-side configuration to enable "dormant functionality" and avoid parallel release tracks. Add the LCE gatekeeping function (Claim 1) as a pattern for agent deployment governance — an SRE function that reviews agent rollouts for compliance with reliability standards. Add the automated canary/rollback pattern (Claim 10) to the agent deployment runbook.

- **Chapter 02 (Incident Response and Reliability Fundamentals)**: Add the capacity planning spike delta (Claim 7 — up to 15×) and the NORAD Tracks Santa case study (Artifact A) to the capacity management fundamentals. Add the overload logging feedback loop (Claim 12) as a failure mode example — error-path code can be more expensive than normal-path code, directly relevant to LLM inference logging. Add the LCE's three unsolved problems (Claim 14) to the limitations section — launch process alone is insufficient; investment in platform infrastructure and operational load reduction is required.

- **Chapter 00 (Principles)**: Add the "safety without impeding change" framing (Claim 15) as a guiding design principle for all AI/LLM operational processes. Add the "substantiated by disaster" curation rule (Claim 4) as a governance principle for AI checklist evolution.

- **Chapter 04 (Oncall and Toil)**: Add the pre-launch documentation requirement (Claim 9) — all manual AI inference processes must be documented before launch, and the documentation must be sufficient for "any team member to execute in an emergency." This directly informs the on-call runbook template.

## Extraction Notes

- The source URL in the issue body (https://sre.google/resources/book-update/reliable-product-launches-at-scale/) is a thin hub page that points to the actual chapter at https://sre.google/sre-book/reliable-product-launches/. Per MINER.md §1, the actual chapter was fetched and read deeply. The hub page also links to a USENIX SREcon17 Asia talk (Kirsch) which was NOT followed per the Prospector's guidance — the chapter itself is the substantive source.
- Quotes were gathered from two rounds of WebFetch against the actual chapter URL. The fast-model WebFetch returns a structured summary rather than raw HTML; quotes attributed in quotation marks were confirmed by targeted re-fetching of specific passages. Spot-check any quote against the live URL above.
- `date_published` is approximate. The SRE Book was published by O'Reilly in 2017. The chapter page on sre.google carries no specific publication date separate from the book's publication. The content is time-invariant SRE process knowledge that remains fully applicable in 2026.
- Confidence is `settled` overall: the source is the canonical SRE Book, authored by named Google SRE practitioners, published through Google's official and O'Reilly's peer-reviewed channels. The claims are well-evidenced with case studies, quantified metrics, and explicit process descriptions. Individual claims marked `settled` where backed by chapter description.
- No contradictions were found against existing source notes. The chapter covers launch process design, a domain absent from existing notes. The three "unsolved problems" are presented as honest limitations rather than contradictions of the approach. No contradiction issue filed.
- The chapter predates the AI/LLM era (published 2017), so all claims about AI applicability in Our assessment are manual transfer patterns, not sourced from the chapter itself. The Prospector's guidance in the triage comments identified this AI-transfer opportunity explicitly.
