---
source_url: https://sre.google/resources/book-update/handling-overload/
source_type: documentation
title: "Google SRE: Handling Overload — SRE Book Update Hub (Workbook Ch11 + Load Shedding Blog)"
author: Google SRE / Google CRE (Cloud Reliability Engineering)
date_published: 2017-2021 (hub page undated; Workbook Ch11 references Pokémon GO 2016 launch; CRE blog published 2017-04-05)
date_extracted: 2026-07-20
last_checked: 2026-07-20
status: current
confidence_overall: settled
issue: "#368"
---

# Google SRE: Handling Overload — SRE Book Update Hub

> A Google SRE documentation hub pointing to three resources on handling
> overload: (1) SRE Workbook Chapter 11 "Managing Load" — covering load
> balancing (Maglev, GCLB, GFE), autoscaling patterns, capacity planning,
> and two case studies on load-shedding/load-balancer interaction failures;
> (2) the Google CRE (Cloud Reliability Engineering) blog post "Using load
> shedding to survive a success disaster" — a detailed treatment of load
> shedding methodology including priority buckets, cost modeling, soft/hard
> quotas, and optimistic vs pessimistic throttling; and (3) a USENIX SREcon17
> Europe talk on load-shedding methodologies. Provides the comprehensive
> overload-handling pattern set missing from the existing corpus.

## Source Context

- **Type**: documentation — a hub/index page on sre.google that aggregates
  SRE Book update resources. The page itself is a thin landing page with
  minimal body text; the substantive content lives in the three linked
  resources. Per MINER.md §1, those linked pages were followed:
  - **SRE Workbook Chapter 11 "Managing Load"** (workbook/managing-load/) —
    the chapter-length treatment (fully read, substantive)
  - **"Using load shedding to survive a success disaster"** (Google Cloud
    Blog, CRE Life Lessons series, 2017) — a detailed blog post with code
    examples and case studies (fully read, substantive)
  - **"Load-Shedding: Overview of Different Methodologies"** (USENIX
    SREcon17 Europe talk) — returned HTTP 403; content not accessible
- **Author credibility**: Highest-credibility for SRE practice. The Workbook
  is an official Google SRE publication, co-edited by Betsy Beyer, Niall
  Murphy, and others who shaped the SRE discipline. The CRE blog post is
  authored by Google's Cloud Reliability Engineering team — practitioner-
  authors with direct experience running Google Cloud infrastructure. Both
  sources are first-party Google SRE content on the official domain.
- **Scope**: Covers (a) load balancing architecture at Google scale (Anycast,
  Maglev, GSLB, GFE); (b) capacity planning and autoscaling patterns
  including constraints, kill switches, and dependency analysis; (c) load
  shedding methodology — when to shed, what to shed, priority buckets, cost
  models, soft/hard quotas; (d) optimistic vs pessimistic throttling; (e)
  case studies of overload-induced cascading failures and their remediation
  (Pokémon GO on GCLB, Dressy load-shedding miscommunication, mobile client
  retry storms, background-upload load shedding as defense-in-depth). Does
  NOT cover AI/LLM-specific workloads directly — the patterns are general
  SRE knowledge applicable to LLM inference serving.

## Extracted Claims

### Claim 1: Load shedding must signal overload to the load balancer — fast error responses are interpreted as "efficient processing" by latency-based LBs, attracting *more* traffic and creating a positive feedback loop
- **Evidence**: Case Study 2 (Dressy): servers returned errors when CPU hit a
  threshold. Errors were fast (low CPU cost to generate), so the LB perceived
  those servers as *more* efficient and routed *more* traffic to them. The
  perceived per-request CPU in the affected region was 10× lower than actual
  because errors were counted as cheap requests. Remediation: count each error
  as 120% CPU utilization.
- **Confidence**: settled
- **Quote**: "Whenever CPU utilization reached a certain threshold, a server
  would return an error for any new requests ... the load balancer didn't know
  that the 'efficient' requests were errors because the load shedding and load
  balancing systems weren't communicating"
- **Our assessment**: A classic, well-documented SRE failure mode (fast-error
  response attracting LB traffic). Directly relevant to LLM inference serving:
  if an LLM API gateway returns fast "overloaded" errors, a latency-based LB
  might route *more* traffic to the shedding server. The 120% accounting trick
  is a concrete, adoptable fix. Directly corroborates Prodcast 03-05 Claim 16
  (error responses faster than valid data attract more traffic from latency LB)
  and Prodcast 03-08 Claim 5 (stampeding herd capacity cascade).

### Claim 2: Reserve spare capacity for both overload protection and redundancy — pre-launch load testing at 5× expected traffic was insufficient (actual was 50×)
- **Evidence**: Pokémon GO on GCLB case study. Pre-launch load testing
  targeted 5× the most optimistic traffic estimates; actual launch traffic was
  nearly 50× that estimate. After migrating to GCLB, traffic was 200% higher
  than previously observed. Recommendation: set minimum instances per location
  for failover spare capacity.
- **Confidence**: settled
- **Quote**: "reserve enough spare capacity for both overload protection and
  redundancy"
- **Our assessment**: A vivid quantification (5× tested vs 50× actual) of how
  badly capacity estimates can miss for a viral success. Direct translation to
  LLM API serving: if a new model goes viral (e.g., ChatGPT launch), capacity
  may need orders of magnitude above testing estimates. The minimum-instances-
  per-location pattern prevents cascading failover overload.

### Claim 3: Synchronized client retries without jitter and exponential backoff produce thundering herd spikes up to 20× normal peak RPS — fix with truncated exponential backoff + jitter
- **Evidence**: Pokémon GO case study. The app's retry strategy was "a single
  immediate retry, followed by constant backoff." During the overload, error
  responses synchronized client retries, producing spikes reaching "20× the
  previous global RPS peak." Fix: "Niantic introduced jitter and truncated
  exponential backoff to their clients."
- **Confidence**: settled
- **Quote**: "error responses served to effectively synchronize client
  retries, producing a 'thundering herd' problem"
- **Our assessment**: Settled, widely-known SRE pattern (retry amplification),
  but the 20× spike quantification is usefully specific. Directly applies to
  LLM API clients: LLM SDK retry logic without jitter can amplify overload
  during inference server degradation. Corroborates Prodcast 03-08 Claim 8
  (QPS rises during outage as users retry) and the broader retry-storm pattern
  described across the Prodcast corpus.

### Claim 4: Autoscaling should trigger before load shedding kicks in — set thresholds such that the system autoscales before reaching load-shedding thresholds
- **Evidence**: Dressy case study remediation: "set your thresholds such that
  your system autoscales before load shedding kicks in." The autoscaler should
  be configured "to keep your service far from key system bottlenecks (such as
  CPU)." Autoscalers are "intentionally more sensitive to jumps in traffic
  than to drops."
- **Confidence**: settled
- **Quote**: "We recommend configuring your autoscaler to keep your service
  far from key system bottlenecks (such as CPU)"
- **Our assessment**: A crisp layering principle (autoscale first, shed only
  when autoscaling is insufficient) that the guide can state directly. For LLM
  inference, this means: configure HPA/vPA based on inference-serving CPU/GPU
  utilization such that new replicas spin up *before* the API gateway starts
  shedding requests. The "more sensitive to jumps than drops" asymmetry is an
  important implementation detail.

### Claim 5: Graceful degradation via "lame duck" mode — backends fail health checks while continuing to respond to in-flight requests, enabling zero-disruption removal
- **Evidence**: GFE (Google Front End) uses lame duck mode: backends "fail
  health checks while continuing to respond to in-flight requests." This lets
  the load balancer "gracefully remove GFE backends from service without
  disrupting any user requests." Canarying is the deployment analogue:
  "deploying a new application to a very small number of servers, then
  gradually increasing traffic."
- **Confidence**: settled
- **Quote**: "gracefully remove GFE backends from service without disrupting
  any user requests"
- **Our assessment**: A concrete procedure for terminating backend instances
  without dropping in-flight inference requests. Directly applicable to LLM
  serving: when draining an inference pod (for rolling update or scale-in),
  implement a lame-duck / preStop hook that de-registers from the LB health
  check but completes active generation requests before shutting down.

### Claim 6: Autoscaling kill switches must be "easy, obvious, fast, and well documented" — a CPU-consuming bug or stuck dependency can cause unbounded quota consumption
- **Evidence**: Two failure scenarios: (1) a CPU-consuming bug causes
  autoscaler to "upsizing this job again and again until all available quota
  is wasted"; (2) a stuck dependency causes "Autoscaler will scale up the
  jobs, causing more and more traffic to get stuck." Recommendation: "Make
  sure your on-call engineers understand how to disable autoscaling and how to
  manually scale if necessary." Also recommend "adding automatic shutdown
  triggers if these systems are behaving wildly out of control."
- **Confidence**: settled
- **Quote**: "Make sure your on-call engineers understand how to disable
  autoscaling and how to manually scale if necessary"
- **Our assessment**: Concrete, actionable runbook guidance for the guide's
  on-call chapter. For LLM inference, a runaway autoscaler could burn GPU
  quota at enormous cost. The kill switch (and documented manual scaling
  procedure) is a must-have, not a nice-to-have. "Automatic shutdown triggers"
  is a stronger pattern worth recommending.

### Claim 7: Load shedding uses local measures (CPU, memory, queue length) to progressively drop traffic — from a configurable fraction of requests up to full rejection at hard limits
- **Evidence**: The CRE blog provides a complete Python implementation (see
  Concrete Artifacts). The method uses a soft quota (e.g., 25) and hard quota
  (e.g., 45), with a threshold that decreases linearly as load increases.
  Definition: "Load shedding is a technique that allows your system to serve
  nominal capacity, regardless of how much traffic is being sent to it, in
  order to maintain availability."
- **Confidence**: settled
- **Quote**: "Load shedding is a technique that allows your system to serve
  nominal capacity, regardless of how much traffic is being sent to it, in
  order to maintain availability. To do this, you'll need to throw away some
  requests and make clients retry."
- **Our assessment**: The definition and code are a complete, adoptable
  pattern. For LLM inference serving, the soft/hard quota approach maps
  directly to admission control on inference endpoints: progressive rejection
  as GPU utilization nears capacity, with a hard cap that prevents OOM. The
  linear threshold descent is simple enough to implement in an API gateway
  without a dedicated load-shedding framework.

### Claim 8: Every request has two costs — direct (CPU, RAM, bandwidth) and opportunity (cost of not doing the work) — denominate both in the scarcest resource and get organizational agreement on units
- **Evidence**: The CRE blog states this as a core framework. "In our
  experience, however, this most usually resolves to CPU, as RAM is often
  already over-provisioned relative to CPU." Two rules: (1) "Denominate your
  costs in terms of your scarcest resource" — at Google, sometimes engineering
  hours because "we perceive engineering time as more scarce than dollars."
  (2) "Get everyone to agree on the units before you start ranking request
  types."
- **Confidence**: settled
- **Quote**: "Denominate your costs in terms of your scarcest resource. If CPU
  is the scarcest thing in your system then use that to express all of your
  costs. If it's revenue or profit then use that."
- **Our assessment**: A decision framework directly applicable to LLM serving
  cost modeling: is the scarcest resource GPU compute (for self-hosted
  inference) or cost-per-token budget (for API-proxied inference)? The second
  rule (organizational agreement on units) is a pragmatic governance
  recommendation — different teams (infra, product, business) will have
  different views on what's costly to drop.

### Claim 9: Establish priority/criticality buckets for request types — determined as early and cheaply as possible — using one of five methods (explicit field, hostname, URL path, user ID, operation type)
- **Evidence**: The CRE blog describes five methods for determining request
  criticality: (1) explicit field in the request; (2) hostname bucketing with
  DNS-based black-holing ("a big hammer, but occasionally life-saving because
  it can stop requests from reaching your overloaded service in the first
  place"); (3) URL path; (4) user ID with tiers (paying > logged-in >
  logged-out > known robot); (5) operation type — "At Google, we often
  classify batch operations (for example, background photo uploads) as
  'non-critical retryable.'"
- **Confidence**: settled
- **Quote**: "you should establish a few criticality buckets or classes for
  your known request types. This way you can more easily classify each request
  into one of the buckets and use that to stack-rank their priorities."
- **Our assessment**: The five-method taxonomy is directly applicable to LLM
  API request prioritization. An LLM serving gateway can classify requests by:
  user tier (paying API customers vs free-tier vs batch), operation type
  (interactive chat vs batch summarization vs background embedding), or URL
  path (completions vs embeddings). The hostname-based DNS black-hole method
  is the most drastic but also the fastest — relevant for catastrophic
  overload scenarios (e.g., a compromised API key sending abusive traffic).

### Claim 10: Opportunity cost is time-varying — request priority should change as deadlines pass; requests exceeding their response deadlines become the cheapest to shed
- **Evidence**: The CRE blog's front page example: a request to load the front
  page is high-value from 0.0–1.9 seconds (user is waiting); after 2.0 seconds
  the user has likely abandoned, so the remaining work is lowest priority and
  "you might as well drop it to the lowest bucket (or cancel it altogether)."
  General principle: "a great source of load that you can shed cheaply is
  requests that are exceeding their response deadlines."
- **Confidence**: settled
- **Quote**: "At first, the request to load your front page is very valuable
  because it's serving important content (perhaps ads) to your user. After a
  certain amount of waiting, say 2 seconds, the user will probably abandon the
  slow page and go someplace else."
- **Our assessment**: A powerful, specific pattern for LLM inference: if a
  generation request has exceeded its response deadline (e.g., streaming
  timeout), cancel it and free the GPU compute rather than continuing to
  generate tokens nobody will see. This is the time-aware version of priority
  shedding — directly applicable to streaming LLM responses where the value
  drops sharply after the user has stopped waiting.

### Claim 11: Prefer optimistic throttling for most systems — don't shed until global capacity is reached, then work from lowest priority upward; pessimistic throttling is costlier and never fully utilizes capacity
- **Evidence**: The CRE blog compares both approaches. Optimistic: "you don't
  start dropping traffic until you reach global capacity" then work up from
  lowest priority. "The advantage to this approach is that it's pretty easy to
  implement and relatively computationally 'cheap'." "this is our recommended
  approach for a majority of systems." Pessimistic: "assumes that you may not
  exceed your global maximum under any circumstance" — "more difficult and
  costlier to implement and maintain" and "you never quite serve up to your
  global capacity."
- **Confidence**: settled
- **Quote**: "this is our recommended approach for a majority of systems"
- **Our assessment**: A clear recommendation with rationale. For LLM inference
  serving: optimistic throttling (allow bursts up to capacity, shed only when
  saturated) is the right default. The risk — "your active load shedding may
  break due to a coding error... and you may not notice it for several weeks"
  — is a real concern for LLM gateways where load-shedding code paths may not
  be exercised regularly. Stress-testing the shedding path should be part of
  the deployment checklist.

### Claim 12: Soft quotas should not throttle when the system has remaining capacity (work conservation); hard quotas exist to protect infrastructure and cannot be exceeded
- **Evidence**: The CRE blog distinguishes the two: "clients who have exceeded
  their quotas should not be throttled if the system has remaining capacity."
  Soft quotas manage resources "equitably"; hard quotas are "a limitation that
  cannot ever be exceeded under any circumstances." Fairness rule: "When the
  system runs out of capacity then the clients who are most over their quotas
  should be the first to be throttled."
- **Confidence**: settled
- **Quote**: "clients who have exceeded their quotas should not be throttled
  if the system has remaining capacity"
- **Our assessment**: A critical distinction for LLM API rate limiting. "Work
  conservation" means: if the inference cluster has idle GPU capacity, allow
  bursts even from users above their soft quota. Hard quotas (absolute per-
  user or per-tenant caps) protect against runaway usage. The fairness rule
  (most-over-quota-first) prevents the pattern where a moderate user gets
  throttled while a heavy consumer saturates the cluster.

### Claim 13: When evaluating throttling impact, measure in user experience and revenue terms — not raw capacity; non-interactive retryable throttling is often working as intended
- **Evidence**: The CRE blog's decision framework: "Are real users seeing
  errors or service degradation as a result? If so, what fraction of active
  users are affected? How many revenue-related requests are being throttled?"
  Cautions against overreacting: "if the system is only throttling non-
  interactive retryable requests, then your system is probably working as
  intended." Exception: "if your service is throttling traffic for 12 hours
  every day, it may be time to do something about its capacity."
- **Confidence**: settled
- **Quote**: "In many cases, if the system is only throttling non-interactive
  retryable requests, then your system is probably working as intended. As
  long as the throttling period is not prolonged and the retries are
  completing within your processing SLO there's no real reason to spend more
  money to serve them more promptly."
- **Our assessment**: A nuanced, business-aware recommendation for interpreting
  throttling signals. For LLM inference: throttling batch/async requests
  (e.g., background summarization embeddings) is acceptable; throttling
  interactive chat requests is not. This pairs with Claim 9's priority buckets
  — if batch work has a separate lower-priority bucket, its throttling is by
  design, not a capacity emergency.

### Claim 14: Load shedding provides defense-in-depth against irreversible coding bugs — a real-world case study showed dropping ~half of background upload requests saved the service from complete overload
- **Evidence**: The CRE blog's mobile client case study: a bug caused all
  clients to re-upload data simultaneously. The service had priority-tagged
  requests (critical user-facing to non-critical background) and was set to
  shed from lowest priority upward. "Load shedding saved it from becoming
  overloaded by dropping nearly half of all background upload requests, while
  the remaining clients patiently backed off and retried again later."
- **Confidence**: settled
- **Quote**: "Load shedding saved it from becoming overloaded by dropping
  nearly half of all background upload requests, while the remaining clients
  patiently backed off and retried again later."
- **Our assessment**: A concrete, quantified demonstration of load shedding as
  safety net, not just capacity management. For LLM serving: if an SDK bug
  causes all clients to resend pending requests simultaneously, priority-aware
  shedding (dropping batch/low-priority work first) can keep interactive chat
  alive. The "defense-in-depth" framing positions load shedding as an
  insurance policy for the LLM API, not just a performance optimization.

### Claim 15: Perform dependency analysis on backend services before deploying autoscalers — a microservice scaling in response to traffic spikes may consume shared quota, starving other services
- **Evidence**: The Workbook chapter recommends to "perform a detailed
  dependency analysis on your backend services before deploying your
  autoscaler" because "If a microservice scales up in response to a traffic
  spike, it might use most of the quota." Suggests separate quotas per
  microservice to prevent starvation. Also warns that "no amount of load
  shedding, autoscaling, or throttling will save our services when they all
  fail in sync."
- **Confidence**: settled
- **Quote**: "perform a detailed dependency analysis on your backend services
  before deploying your autoscaler"
- **Our assessment**: Directly relevant to LLM inference architectures, where
  multiple inference services may share a GPU quota pool. If a popular model's
  endpoint autoscales, it can consume GPU quota needed by other model
  endpoints. Separate quotas per model/endpoint is the mitigation. The
  "all-fail-in-sync" warning is a reminder that load management is a delaying
  tactic, not a cure for fundamental capacity shortage.

## Concrete Artifacts

### Artifact A — Load shedding Python implementation (Google CRE blog, verbatim)

```python
def addRequest(self, r):
    HARD_QUOTA = 45
    SOFT_QUOTA = 25
    STEPS = 10
    divisor = (HARD_QUOTA - SOFT_QUOTA) / STEPS
    self.received += 1
    self.req_modulus = (self.req_modulus + 1) % STEPS
    # Are we overloaded?
    load = self.getLoad()
    # Become progressively more likely to reject requests
    # once load > soft quota; reject everything once load
    # hits hard limit.
    threshold = int((HARD_QUOTA - load) / divisor)
    if self.req_modulus < threshold:
        # We're not too loaded
        self.active_requests.append(r)
        self.accepted += 1
    else:
        self.rejected += 1
```

### Artifact B — Dressy case study: load-shedding miscommunication (Workbook Ch11, verbatim)

```
The failure cascade:
1. Servers in region A hit CPU threshold → returned errors for new requests.
2. Errors were fast (low CPU cost to generate).
3. Load balancer saw region A servers as "efficient" (low per-request CPU)
   → routed MORE traffic to region A.
4. Perceived CPU in region A was 10× lower than actual (errors counted as
   cheap requests).
5. Region A: steady state 90 RPS → spiked to 400 RPS while B/C served 40.
6. Remediation: count each error request as 120% CPU utilization
   ("any number over 100 will work").

Key insight: "the load balancer didn't know that the 'efficient' requests
were errors because the load shedding and load balancing systems weren't
communicating."
```

### Artifact C — Five methods for determining request criticality (CRE blog, verbatim)

```
1. Explicit field in the request specifying the bucket.
2. Hostname bucketing → DNS to point to sacrificial server.
   "This is a big hammer, but occasionally life-saving because it can stop
    requests from reaching your overloaded service in the first place."
3. URL path — fairly cheap to check.
4. User ID / group: 'paying customers' (highest) > 'logged in users'
   (medium-high) > 'logged-out users' (medium-low) > 'known robot accounts'
   (lowest). "Allows the most precise bucketing, but is more expensive."
5. Operation type: batch operations classified as 'non-critical retryable.'
   Signals "the user generally doesn't mind if the handling is delayed
   several minutes, or even an hour."
```

### Artifact D — Autoscaling failure scenarios requiring kill switches (Workbook Ch11, verbatim)

```
Scenario 1 — CPU-consuming bug:
  Autoscaler "upsizing this job again and again until all available quota
  is wasted."

Scenario 2 — Stuck dependency:
  "Autoscaler will scale up the jobs, causing more and more traffic to
  get stuck."

Mitigations:
  - "Set a minimum and maximum bound for scaling, making sure that you have
    enough quota to scale."
  - "Make sure your on-call engineers understand how to disable autoscaling
    and how to manually scale if necessary."
  - "consider adding automatic shutdown triggers if these systems are
    behaving wildly out of control."
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` **Claim 14**
    (client-side load shedding beats server-side) — the Workbook's retry/jitter
    recommendation (Claim 3 here) and the CRE blog's client-isolation methods
    (Claim 9 here) corroborate client-side shedding as the recommended pattern.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` **Claim 16**
    (error responses faster than valid data attract more traffic from latency LB)
    — this claim is directly and independently re-derived from the Dressy case study
    (Claim 1 here), with the 10× CPU-perception asymmetry and the 120% accounting
    fix. Strong mutual corroboration from completely independent sources (Prodcast
    interview vs. Workbook case study).
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` **Claim 14** (circuit-
    breaking and throttling as first technical interventions) — this note provides
    the comprehensive framework (priority buckets, cost models, throttling types)
    that circuit-breaking fits into as one tool in the overload-management toolkit.
  - `docs-google-sre-prodcast-03-08-public-dns.md` **Claim 5** (stampeding herd
    capacity cascade) and **Claim 10** ("just add capacity" is wrong at scale) —
    the Workbook's Dressy case study (Claim 1 here) and the capacity-planning
    warnings (Claim 15 here) are the same class of cascading-overload dynamic,
    analyzed from the load-management perspective rather than the DNS perspective.
  - `docs-google-sre-prodcast-03-08-public-dns.md` **Claim 14** (don't rip out
    rate-limit code; "almost all of those lines are there for a really good reason")
    — corroborates this note's Claim 1 (load-shedding code is doing real work even
    when it looks like "errors"; removing it without understanding the LB interaction
    will cause worse failures).
  - `docs-google-sre-prodcast-04-06-fletcher-vibe-coding.md` **Claim 5** (SRE SaaS
    should modify code to add load shedding/multiregion, not just monitor) — Fletcher's
    "you weren't doing load shedding, I got it, I turned it on" wish-list aligns with
    the concrete load-shedding patterns cataloged here. This note provides the
    patterns Fletcher's hypothetical tool would implement.

- **Contradicts**: None identified. All claims here are foundational SRE knowledge
  consistent with existing corpus claims. The one potential tension — this source's
  recommendation for optimistic throttling (Claim 11) vs Prodcast 03-05's emphasis on
  client-side load shedding — is complementary, not contradictory: optimistic
  throttling is a *server-side admission strategy* (which layer of the server sheds
  first), while client-side shedding is a *where-to-shed* decision (stop sending vs
  receive-and-drop). Both are valid and layered in production systems. No
  contradiction issue filed.

- **Extends**:
  - The existing Prodcast corpus covers load shedding and circuit-breaking as
    *mentions* within broader conversations. This note provides the **comprehensive
    taxonomy**: load balancing strategies (Maglev, GCLB, GFE, Anycast), admission
    control (soft/hard quotas), priority scheduling (criticality buckets), graceful
    degradation (lame duck mode, client isolation, DNS black-hole), capacity planning
    (spare capacity, dependency analysis, autoscaling constraints), and client-side
    patterns (jitter/backoff, deadlines). This fills the gap the Prospector identified
    — no existing note covers the full handling-overload pattern set.
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` — the GFE
    lame duck mode (Claim 5 here) is a concrete implementation of the client-
    transparent removal pattern that note describes at the architectural level.

- **Novel**: Material new to the corpus:
  - **Dressy case study** — the load-shedding/LB miscommunication pattern with
    the 120% CPU accounting fix (Claim 1). Completely novel; no existing note
    describes this specific feedback loop.
  - **Priority bucket framework** with five determination methods (Claim 9) and
    **two-cost model** for request valuation (Claim 8) — a decision framework
    for prioritizing LLM API requests, not present elsewhere.
  - **Soft vs hard quotas** with work conservation principle (Claim 12) —
    critical for LLM API rate limit design.
  - **Optimistic vs pessimistic throttling** comparison (Claim 11) with
    Google's recommendation for the majority of systems.
  - **Time-varying opportunity cost** (Claim 10) — shedding requests that have
    exceeded their deadlines, directly applicable to streaming LLM responses.
  - **Lame duck mode** for graceful backend removal (Claim 5) — relevant to
    inference pod lifecycle management.
  - **Autoscaling kill switch** requirements and **dependency analysis**
    recommendation (Claims 6, 15).
  - **Complete Python load-shedding implementation** (Artifact A) — a citable
    reference implementation for the guide.
  - **Pokémon GO 5×-tested vs 50×-actual capacity gap** (Claim 2) and **20×
    synchronized retry spike** (Claim 3) — quantified overload case study data.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: The most impacted chapter. Add a
  dedicated "Handling Overload" subsection with: (a) the priority bucket framework
  (Claims 8–10) for classifying LLM API requests by criticality (interactive chat,
  batch summarization, background embeddings); (b) the soft/hard quota distinction
  (Claim 12) for inference endpoint rate limiting; (c) optimistic throttling as the
  recommended approach for LLM gateways (Claim 11); (d) the Dressy miscommunication
  pattern (Claim 1) as a warning for latency-based LLM routing; (e) progressive load
  shedding with the Python reference implementation (Artifact A) as a template for
  inference admission control; (f) time-varying opportunity cost (Claim 10) for
  cancelling streaming responses that have exceeded their timeout. Currently Ch05
  covers rate limiting only at a high level (citing Prodcast 03-05). This note
  provides the concrete patterns the chapter needs.

- **Chapter 02 (Observability / Reliability fundamentals)**: Add the capacity-planning
  quantification (Claim 2 — 5× tested vs 50× actual) to the capacity management
  fundamentals section. Add the retry amplification pattern (Claim 3) as a design
  consideration for any LLM API client library. Add the load management systems
  interaction warning (Claim 1: load shedding, load balancing, and autoscaling are
  not independent) to the reliability fundamentals chapter. Currently Ch02 cites
  Prodcast sources on client-side load shedding but lacks the comprehensive taxonomy.

- **Chapter 04 (Oncall and Toil)**: Add autoscaling kill switch requirements
  (Claim 6) and dependency analysis guidance (Claim 15) to the on-call runbook
  material. Add lame duck mode (Claim 5) as the recommended pattern for graceful
  inference pod shutdown during deployments. Add the "throttling as a signal"
  decision framework (Claim 13) — when to escalate vs accept throttling as working
  as intended.

- **Chapter 00 (Principles)**: Add Claim 14's "load shedding as defense-in-depth"
  framing as a guiding principle: load shedding is not just for capacity management
  but is an insurance policy against bugs and unexpected traffic patterns.

## Extraction Notes

- The hub page at `https://sre.google/resources/book-update/handling-overload/` is
  thin — its body text is only "21. Handling Overload" and "Read Handling Overload
  from the SRE Book." Per MINER.md §1, the two substantive linked resources were
  followed and read deeply:
  1. **SRE Workbook Ch11 "Managing Load"** (`/workbook/managing-load/`) — ~130 lines
     of substantive extracted content including two case studies, load-balancer
     architecture descriptions, autoscaling patterns, and metrics.
  2. **Google CRE Blog "Using load shedding to survive a success disaster"**
     (`cloud.google.com/blog/...`) — a detailed blog post with complete Python code
     example, priority framework, cost model, and multiple case studies. Fully read
     and extracted.
  3. **USENIX SREcon17 Europe talk** (`usenix.org/conference/...`) — returned HTTP
     403; content not accessible. Noted but not extracted.
- Quotes were copied character-for-character from the fetched page content. Spot-
  check against the live URLs for verification.
- `date_published` is approximate for the hub page (it carries no publication date).
  The Workbook chapter references the Pokémon GO launch (July 2016) and the
  Dressy case study; the CRE blog post is dated 2017-04-05 in its URL structure.
  The `date_published` field reflects the range.
- Confidence is `settled` overall: both sources are first-party Google SRE
  publications on the official domain, the claims are well-evidenced with case
  studies and code, and the patterns are established SRE knowledge. Individual
  claims marked `settled` where backed by case study evidence or authoritative
  recommendation. No claims required `anecdotal` grading.
- No contradiction surfaces against existing notes. The CRE blog's "optimistic
  throttling for most systems" (Claim 11) and Prodcast 03-05's "client-side load
  shedding" (Claim 14 there) address different layers of the stack and are
  complementary, not contradictory. No contradiction issue filed.
