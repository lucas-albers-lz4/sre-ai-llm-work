---
source_url: https://sre.google/sre-book/addressing-cascading-failures/
source_type: documentation
title: "Addressing Cascading Failures — SRE Book Chapter 22"
author: Mike Ulrich (Google SRE)
date_published: 2017
date_extracted: 2026-07-21
last_checked: 2026-07-21
status: current
confidence_overall: settled
issue: "#389"
---

# Addressing Cascading Failures — SRE Book Chapter 22

> The canonical SRE treatment of cascading failure mechanisms: positive feedback loops, resource exhaustion taxonomy (CPU/memory/threads/file descriptors), hysteresis in crash-loop recovery, retry amplification across service layers, bimodal latency thread-exhaustion, deadline/cancellation propagation, cold-caching startup vulnerability, and the "always go downward in the stack" design rule. Provides the systematic failure-propagation framework that the load-management patterns in the handling-overload note fit into.

## Source Context

- **Type**: documentation — Chapter 22 of the Site Reliability Engineering book (O'Reilly, 2017), written by Mike Ulrich, hosted on sre.google as part of the book-update series.
- **Author credibility**: Highest credibility. The SRE Book is the foundational text of the SRE discipline, published by Google and O'Reilly. Mike Ulrich is a named Google SRE practitioner-author. The chapter has been peer-reviewed through Google's internal SRE review process and the O'Reilly publication pipeline. The content is hosted on the official sre.google domain under a CC BY-NC-ND 4.0 license.
- **Scope**: Systematically covers (a) definition and mechanisms of cascading failures via positive feedback; (b) server overload as the most common trigger; (c) resource exhaustion taxonomy (CPU, memory, threads/goroutines, file descriptors) with inter-dependency chains; (d) crash-loop dynamics and the hysteresis asymmetry (load must drop far below the breaking point to recover); (e) prevention strategies — queue management, load shedding, graceful degradation, retry policies; (f) latency and deadline management including propagation and cancellation; (g) cold-caching startup vulnerability; (h) the intra-layer communication anti-pattern; (i) triggering conditions taxonomy; (j) testing methodology; (k) immediate-mitigation steps; (l) the Shakespeare case study. Does NOT cover AI/LLM workloads directly — the patterns are general SRE knowledge directly applicable to LLM inference serving (GPU OOM cascades, KV-cache memory pressure, inference request queue saturation, streaming deadline propagation).

## Extracted Claims

### Claim 1: A cascading failure is defined as a failure that grows over time as a result of positive feedback — each component failure increases the probability of additional failures, creating a domino effect

- **Evidence**: Chapter opening definition. The running example is the Shakespeare search service: when one cluster fails, its traffic shifts to remaining clusters, which then exceed capacity and also fail, spreading the failure.
- **Confidence**: settled
- **Quote**: "A cascading failure is a failure that grows over time as a result of positive feedback. When a portion of a system fails, the probability of other portions of the system failing increases substantially."
- **Our assessment**: The foundational definition of the topic. Settled SRE knowledge — this is the canonical framing used across the SRE discipline. Directly applicable to LLM inference serving: if one GPU node exhausts memory (OOM) and requests are retried onto other nodes, their cumulative KV-cache pressure can trigger a cascade of OOM failures.

### Claim 2: Resource exhaustion comes in four primary modes (CPU, memory, threads, file descriptors) that feed into each other — the causal chain is so complex it is "unlikely" to be fully diagnosed during an outage

- **Evidence**: The chapter enumerates each resource type with specific secondary effects. CPU exhaustion causes increased in-flight requests, queue buildup, thread starvation (health checks fail), and missed RPC deadlines. Memory exhaustion triggers the "GC death spiral" in Java systems: "less CPU → slower requests → increased RAM → more GC → even lower CPU availability." The chapter provides a 9-step dependency chain: poor GC tuning → CPU exhaustion → slower requests → more RAM → less cache → lower hit rate → more backend requests → backend CPU exhaustion → health check failures → full cascade.
- **Confidence**: settled
- **Quote**: "In situations as complex as the preceding scenario, it's unlikely that the causal chain will be fully diagnosed during an outage."
- **Our assessment**: The multi-resource taxonomy and the 9-step chain are critical for understanding why cascading failures are so hard to resolve mid-incident. For LLM inference: memory (KV-cache) and compute (GPU utilization) are the primary exhaustion modes, with thread/connection exhaustion affecting the inference gateway and request queue. The "GC death spiral" has direct analogs in GPU memory fragmentation and garbage-collection-like memory management in inference frameworks.

### Claim 3: Crash-loop recovery exhibits hysteresis — returning load to pre-crash levels is insufficient; load must drop far below the original breaking point, with recovery requiring traffic reduction of roughly 10:1

- **Evidence**: The chapter uses a concrete numerical example. A system handling 10,000 QPS begins failing at 11,000 QPS. Dropping back to 9,000 QPS does not stabilize the system because remaining servers are still overloaded. The quantified recovery condition: if 10% of servers are healthy, load must drop to ~1,000 QPS.
- **Confidence**: settled
- **Quote**: "If 10% of the servers are healthy enough to handle requests, the request rate would need to drop to about 1,000 QPS."
- **Our assessment**: This is the most actionable quantified pattern in the chapter and entirely new to the corpus. The hysteresis asymmetry means that during a crash-looping cascade, mild traffic reduction (e.g., 10-20% via load shedding) will not stabilize the system — operators must drop traffic aggressively (e.g., to 1% of normal) before gradually ramping back up. For LLM inference: when GPU nodes are crash-looping from OOM, reducing request rate by 10% won't help; traffic must be dropped to a tiny fraction until nodes stabilize, then gradually increased.

### Claim 4: Retry amplification across service layers follows a product, not a sum — a 3-layer system with 4 attempts per layer produces 4³ = 64 database attempts per single user action

- **Evidence**: The chapter explicitly calculates the multi-level retry product under "Think about the service holistically." The example: frontend, backend, and JavaScript layers each retry 3 times (4 total attempts), producing 64 database-level attempts per user action.
- **Confidence**: settled
- **Quote**: "a single request at the highest layer may produce a number of attempts as large as the product of the number of attempts at each layer to the lowest layer."
- **Our assessment**: The product formulation (not sum) is the critical insight. Existing corpus notes on retry amplification (handling-overload Claim 3, Prodcast 03-05 Claim 16) describe the symptom but not the mathematics. For LLM agent systems: an agent call → LLM API retry → Gateway retry → inference node retry can produce multiplicative load on the underlying GPU cluster. This directly informs Ch05's retry policy guidance: each layer must limit retries independently and communicate retry counts down the stack.

### Claim 5: Retry policies must use randomized exponential backoff, bound per-request retry counts, employ server-wide retry budgets, and never retry permanent errors — these are the four core guidelines

- **Evidence**: The chapter enumerates concrete retry rules. Randomized exponential backoff prevents synchronized retry storms. Per-request limits prevent indefinite retry loops. Server-wide retry budgets (e.g., 60 retries/minute/process) cap total retry load. Clear response codes distinguish retriable vs. non-retriable errors.
- **Confidence**: settled
- **Quote**: "Always use randomized exponential backoff when scheduling retries."
- **Quote**: "Don't retry permanent errors or malformed requests."
- **Our assessment**: All four guidelines are settled SRE knowledge. The server-wide retry budget is the most novel for LLM systems — an API gateway should track total retries per minute and begin shedding once the budget is exhausted, even if individual requests haven't exceeded their per-request limit. The "don't retry permanent errors" rule has a sharp AI analog: don't retry on 400 errors (content filter rejections, malformed prompts) — only retry on 429/503/5xx.

### Claim 6: Bimodal latency from a small fraction of slow requests can exhaust thread pools — 5% of requests with a 100-second deadline consume 5,000 threads in a system with only 1,000 total threads, producing an 80.4% error rate instead of 5%

- **Evidence**: The chapter provides a worked example: 10 frontend servers with 100 threads each (1,000 total). Normal operation: 1,000 QPS at 100ms latency (100 threads occupied). If 5% of requests have a 100-second deadline and never complete (e.g., unavailable Bigtable ranges), those 50 QPS consume 5,000 threads — 5× the total thread pool. The remaining 95% of requests get only ~195 threads, resulting in an 80.4% error rate.
- **Confidence**: settled
- **Quote**: "5% of requests would consume 5,000 threads (50 QPS × 100 seconds)."
- **Our assessment**: A striking quantified example of how tail-latency amplification works. For LLM inference: if 5% of generation requests have an overly long timeout (e.g., 120 seconds for streaming) and get stuck on a degraded GPU node, they can consume connection pool or batching slot capacity, starving the healthy 95% of requests. The recommendation to use fail-fast options and limit in-flight requests per keyspace/client maps directly to per-model or per-tenant connection limits in LLM API gateways.

### Claim 7: Deadlines must be propagated downward through the call stack with arithmetic — each layer subtracts its elapsed time and forwards the remainder; servers must check remaining deadline before each processing stage

- **Evidence**: The chapter explains the propagation mechanism: server A sets a 30-second deadline, spends 7 seconds, and passes 23 seconds to B. B spends 4 seconds and passes 19 seconds to C. Without this, a downstream server might use a hardcoded 20-second deadline for a call when only 2 seconds remain, producing useless work. Setting upper bounds on outgoing deadlines is recommended.
- **Confidence**: settled
- **Quote**: "you don't get credit for late assignments with RPCs."
- **Our assessment**: Deadline propagation is well-understood in distributed systems but rarely applied in LLM inference stacks. For LLM agent systems: if the top-level agent call has a 60-second timeout, and the orchestrator uses 20 seconds planning, the downstream LLM call should have a 40-second deadline — not a hardcoded 60-second inference timeout. The "no credit for late assignments" rule means an inference response that arrives after the client deadline expired should be discarded, not processed.

### Claim 8: Cancellation propagation and hedged requests require propagating "stop work" signals through the entire stack — for hedged requests, send to multiple servers and cancel all outstanding work once one responds

- **Evidence**: The chapter recommends cancellations propagate throughout the stack so downstream servers learn their efforts are unnecessary. The hedged request pattern is described: identical RPCs sent to multiple servers; once the first responds, the rest are cancelled.
- **Confidence**: settled
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: For LLM inference, cancellation propagation has high practical value. If an LLM gateway sends a generation request and the client disconnects (timeout, navigation), the cancellation should propagate to the GPU inference node to free its compute. Similarly, if the gateway sends a hedged request to two inference nodes (for latency optimization), the first response should cancel the second generation immediately. The current state of many LLM API gateways does not propagate cancellations to GPU compute, wasting inference capacity.

### Claim 9: Cold caches create a startup vulnerability — newly started servers underperform until warmed up, and the distinction between "latency caches" (service handles load without them) and "capacity caches" (service cannot) determines whether restarts trigger a cascade

- **Evidence**: The chapter addresses cold caching under "Slow Startup and Cold Caching." Processes are slower after starting due to initialization and runtime optimizations (JIT, hotspot optimization, deferred class loading). Cold caches make all requests expensive. The recommendation for capacity caches: "consider moving caching from a server to a separate binary like memcache." The strategy distinction: overprovision for latency caches vs. use general cascade prevention for capacity caches. Gradual load introduction is recommended.
- **Confidence**: settled
- **Quote**: "consider moving caching from a server to a separate binary like memcache."
- **Our assessment**: The latency vs. capacity cache distinction is crucial for LLM inference. KV-cache in LLM serving is a capacity cache — without it, the model cannot generate efficiently and latencies spike dramatically (linear-time generation instead of sublinear). Restarting an inference node during high load (e.g., during a rolling update) with a cold KV-cache will produce significantly degraded throughput and may cascade. The recommendation to separate the cache (e.g., prefix-caching infrastructure, external KV-cache store) is directly applicable. The "slowly increase load" rule translates to: when bringing a new inference node online, gradually ramp its request rate rather than sending full traffic immediately.

### Claim 10: Intra-layer communication is prohibited — "always go downward in the stack"; backends should not proxy to each other because it creates cycles that cause distributed deadlock, active rebalancing under load, and bootstrapping complexity

- **Evidence**: The chapter lists three specific problems with intra-layer communication: (1) distributed deadlock from thread pool saturation when backends wait on each other; (2) active rebalancing under load increases intra-layer requests precisely when the system is already overloaded; (3) bootstrapping complexity makes recovery harder. The recommended pattern is to "have the client do the communication" — if a frontend talks to the wrong backend, the backend should tell the frontend to retry rather than proxying.
- **Confidence**: settled
- **Quote**: "have the client do the communication."
- **Our assessment**: For LLM inference architectures, this rule applies directly to inference routing. If an API gateway sends a request to an inference node that doesn't have the model cached, the node should reject with a redirect (or the gateway should retry) rather than the node proxying to another node that has the model warm. The proxy approach creates intra-layer cycles, thread pool exhaustion on the proxy node, and complicates recovery. For agent systems: agent A should not proxy to agent B which proxies back to agent A — the client (orchestrator) should communicate directly.

### Claim 11: Load shedding and graceful degradation must be engineered in advance and their rarely-exercised code paths must be monitored — "the code path you never use is the code path that (often) doesn't work"

- **Evidence**: The chapter warns that complex load shedding and graceful degradation can cause problems themselves. Recommendations: (1) monitor and alert when too many servers enter degraded mode; (2) design a way to quickly disable or tune parameters; (3) change queue discipline from FIFO to LIFO or use CoDel to "remove requests that are unlikely to be worth processing"; (4) "When overloaded at either the frontend or backend layers, fail early and cheaply."
- **Confidence**: settled
- **Quote**: "When overloaded at either the frontend or backend layers, fail early and cheaply."
- **Our assessment**: The rarely-exercised-code-path warning is high-value. For LLM inference, load-shedding code paths (HTTP 503 responses, queue-depth checks, priority-based rejection) may not be exercised in normal operation and are likely to have bugs. Regular load testing that exercises shedding paths is essential. The LIFO/CoDel recommendation is directly applicable to LLM request queues: a request that has been queued for 10+ seconds for GPU compute is unlikely to produce a useful response — drop it early rather than processing it when the user has already abandoned.

### Claim 12: Triggering conditions for cascading failures include six categories — process death, process updates, new rollouts, organic growth, planned changes, and request profile changes — any of which can tip a system already near its breaking point

- **Evidence**: The chapter enumerates each category with specific mechanisms. Process death (Query of Death, assertion failures) is the most acute. Process updates push new binaries/configs simultaneously. New rollouts alter request profiles or resource usage. Organic growth exceeds capacity gradually. Planned changes (drains, turndowns, traffic shifts) redistribute load. Request profile changes (payload cost changes, data growth) occur silently.
- **Confidence**: settled
- **Quote**: "During a cascading failure, it's usually wise to check for recent changes and consider reverting them."
- **Our assessment**: A practical checklist for incident response. For LLM inference: triggering conditions include model rollouts (new model versions with different compute profiles), GPU hardware failures (process death), organic growth in inference traffic, and request profile changes (longer prompts → more KV-cache pressure). The "check recent changes and revert" recommendation is especially relevant: if an LLM serving rollout triggered a cascade, reverting to the previous model version or scaling configuration should be the first response.

### Claim 13: Testing for cascading failures requires understanding behavior under heavy load, testing both impulse and gradual load patterns, testing each component independently, testing popular clients, and testing noncritical backends' blackholing behavior

- **Evidence**: The chapter's "Test Until Failure and Beyond" section: understanding behavior under heavy load is "perhaps the most important first step." A well-designed component "should ideally start serving errors or degraded results in response to additional load, but not significantly reduce the rate at which it successfully handles requests." Both gradual and impulse load patterns must be tested due to caching effects. Components must be tested for self-recovery (can degraded mode exit without intervention? how much must load drop to stabilize?). Noncritical backends that blackhole (never respond) can cause frontend resource exhaustion even though they are "noncritical."
- **Confidence**: settled
- **Quote**: "Understanding the behavior of the service under heavy load is perhaps the most important first step in avoiding cascading failures."
- **Quote**: "the component should ideally start serving errors or degraded results in response to additional load, but not significantly reduce the rate at which it successfully handles requests."
- **Our assessment**: The testing methodology is comprehensive and directly applicable to LLM inference. Testing "impulse load" (sudden traffic spikes from viral events or coordinated retries) is particularly relevant for LLM APIs. Testing each component independently applies to the inference stack: test the gateway independently (can it shed load?), test the inference node independently (does it crash or return errors under GPU overload?). Testing noncritical backends (e.g., logging, monitoring, content filtering) for blackholing behavior is critical — if the content filter's response time degrades, it can block the entire inference gateway thread pool.

### Claim 14: The immediate mitigation hierarchy for active cascading failures is: increase resources → stop health check failures/deaths → restart servers → drop traffic → enter degraded modes → eliminate batch/bad traffic — with aggressive traffic reduction (e.g., to 1%) as the most reliable escape from a death spiral

- **Evidence**: The chapter provides ordered mitigation steps. "Drop traffic" is called "a big hammer for true cascading failures" with a specific procedure: (1) address the triggering condition, (2) reduce load aggressively (e.g., to 1% of traffic), (3) let servers become healthy, (4) gradually ramp up load. Stopping health check failures/deaths can let the system stabilize temporarily. Entering degraded modes requires advance engineering.
- **Confidence**: settled
- **Quote**: "Once a service passes its breaking point, it is better to allow some user-visible errors or lower-quality results to slip through than try to fully serve every request."
- **Our assessment**: The mitigation hierarchy is actionable runbook material. The "aggressive traffic reduction to 1%" protocol directly operationalizes Claim 3's hysteresis insight. For LLM inference: this means the runbook should include a documented "emergency traffic shed" step that immediately drops inference traffic to a minimal level (e.g., using a feature flag or GSLB rule) before operators investigate root cause. The distinction between "process health checking" (cluster scheduler) and "service health checking" (load balancer) is critical — disabling service health checks can stop the crash-loop without removing the task from the scheduler.

### Claim 15: Well-intentioned patterns for steady-state health (retries, load shifting, killing unhealthy servers, adding caches) increase cascading failure risk — changes must be evaluated to ensure one outage is not being traded for another

- **Evidence**: The chapter's closing remarks warn that the very mechanisms engineering teams use to improve reliability can, under overload conditions, accelerate cascading failures. Retries amplify load. Load shifting creates new hotspots. Killing unhealthy servers concentrates traffic. Adding caches creates cold-cache vulnerability.
- **Confidence**: settled
- **Quote**: "Be careful when evaluating changes to ensure that one outage is not being traded for another."
- **Our assessment**: A meta-warning that is especially relevant for AI/LLM systems. Common "reliability improvements" in LLM serving — add client-side retries (amplifies GPU OOM cascades), add cross-region failover (creates cold-cache vulnerability in the failover region), kill unresponsive inference nodes (concentrates KV-cache pressure on remaining nodes) — all increase cascade risk. The chapter's closing warning should be a design review checklist item for any LLM serving architecture change.

## Concrete Artifacts

### Retry amplification product formula (SRE Book Ch22, verbatim)

```
If the database can't service requests due to overload, and the backend,
frontend, and JavaScript layers all issue 3 retries (4 attempts), then a single
user action may create 64 attempts (4^3) on the database.
```

### The 9-step resource exhaustion chain (SRE Book Ch22, reconstructed from narrative)

```
1. A Java frontend has poorly tuned garbage collection
2. → CPU exhaustion from excessive GC cycles
3. → Requests complete more slowly
4. → More RAM consumed by in-flight requests
5. → Less RAM available for caching
6. → Lower cache hit rate
7. → More backend requests generated
8. → Backend CPU and thread exhaustion
9. → Backend health checks fail → cascading failure
```

### Bimodal latency worked example (SRE Book Ch22, reconstructed from narrative)

```
System:   10 frontend servers × 100 threads = 1,000 total threads
Normal:   1,000 QPS × 100ms latency = 100 threads occupied, 0% errors
Degraded: 5% of requests (50 QPS) have 100-second deadline and never complete
          50 QPS × 100 seconds = 5,000 threads consumed
          Remaining 950 QPS only get ~195 threads = ~80.4% error rate
```

### Immediate crash-loop recovery procedure (SRE Book Ch22, reconstructed from narrative)

```
1. Address the triggering condition (revert recent changes)
2. Reduce load aggressively (e.g., to 1% of traffic)
3. Let servers become healthy and warm caches
4. Gradually ramp up load, monitoring for re-entry into overload
```

### Episode epigraphs (verbatim, SRE Book Ch22)

```
Dan Sandler, Google Software Engineer:
    "If at first you don't succeed, back off exponentially."

Ade Oshineye, Google Developer Advocate:
    "Why do people always forget that you need to add a little jitter?"
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-handling-overload.md` — This note covers the *load-management* side of the same coin (how to prevent overload). The two notes are complementary: handling-overload covers what to do when load approaches capacity (load shedding, autoscaling, priority buckets, throttling); this chapter covers what happens *after* the breaking point is passed (cascade propagation, crash-loop hysteresis, resource exhaustion chains).
    - **Claim 1** (handling-overload: fast-error attracting LB traffic) — the positive feedback loop this chapter describes as the core cascade mechanism. The Dressy case study is a real-world instance of the server overload dynamic this chapter models theoretically.
    - **Claim 3** (handling-overload: synchronized retries, 20× RPS spike) — this chapter's Claim 4 (retry product formula) provides the mathematical model: retry amplification is multiplicative across layers, not additive.
    - **Claims 7, 11** (handling-overload: optimistic throttling, soft/hard quotas) — this chapter's Claim 11 (load shedding and graceful degradation) covers the *what*; the handling-overload note covers the *how* with concrete implementation patterns.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` —
    - **Claim 14** (Murphy: client-side load shedding beats server-side) — this chapter's load shedding section corroborates the principle with the "fail early and cheaply" recommendation (Claim 11 here).
    - **Claim 16** (fast-error attracting traffic from latency LB) — this chapter's server overload dynamics (Claim 2 here) describe the same positive feedback loop at the theoretical level.
    - **Claim 12** (internal self-DoS dynamics) — this chapter's resource exhaustion taxonomy (Claim 2) and triggering conditions (Claim 12) explain *why* self-DoS happens and what resource chains are involved.
  - `docs-google-sre-prodcast-03-08-public-dns.md` —
    - **Claim 5** (stampeding herd capacity cascade) — this chapter's hysteresis quantification (Claim 3) explains the *mechanism* behind the stampeding herd: losing a bit of capacity pushes remaining nodes past their breaking point, and recovery requires load to drop far below pre-incident levels.
    - **Claim 8** (QPS rises during outages as users retry) — this chapter's retry amplification analysis (Claims 4-5) provides the mathematical model for why retry-induced QPS increase happens.
  - `docs-google-sre-prodcast-02-08-life-beyond-google.md` —
    - **Claim 8** (Nolan: cascading-failure insight as the core SRE intuition) — this chapter is the canonical deep treatment of that insight. Nolan's "vicious cycle of load that causes retries that causes more load" is an informal description of the positive feedback loop this chapter formalizes.
  - `docs-google-sre-nalsd-classroom.md` — The NALSD design methodology is the companion *design* framework; this chapter covers the *failure dynamics* that NALSD's capacity planning, component isolation, and graceful degradation patterns are intended to prevent. The two chapters together (SRE Book Ch22 + Workbook Ch12) form a complete design-against-failure methodology.

- **Contradicts**: None identified. All claims are foundational SRE knowledge consistent with existing corpus claims. The one potential tension — this chapter's recommendation to "fail early and cheaply" via fast error responses (Claim 11) vs. the handling-overload note's Dressy case study showing fast errors attracting LB traffic (Claim 1 there) — is not a contradiction: the Dressy case study documents a *miscommunication* between load shedding and load balancing, not a flaw in the fail-early principle itself. The chapter's recommendation assumes the load balancer and load-shedding system are properly coordinated (exactly the fix the Dressy case study applies with the 120% CPU accounting trick). No contradiction issue filed.

- **Extends**:
  - The handling-overload note covers load management (how to avoid overload with shedding, throttling, autoscaling). This chapter covers how failures *propagate* once they start — the positive-feedback mechanisms, resource-exhaustion chains, and recovery dynamics. Together they form a complete overload-and-cascade framework for the guide.
  - The Prodcast corpus covers retry storms and cascading failures as *incident anecdotes* within broader conversations. This chapter provides the systematic taxonomy and quantification that turns those anecdotes into generalizable patterns.
  - The Prodcast 03-05 note's client-side load shedding recommendation (Claim 14) and this chapter's deadline propagation framework (Claim 7) are complementary: shedding + propagation means both "don't send the work" and "tell downstream they can stop working."

- **Novel**: Entirely new to the corpus:
  - **Hysteresis quantification** (Claim 3) — the specific 11,000 QPS trigger / ~1,000 QPS recovery asymmetry. No existing note quantifies crash-loop recovery requirements.
  - **Resource exhaustion taxonomy** with the 9-step inter-dependency chain (Claim 2) — not systematically extracted anywhere.
  - **Multi-level retry product formula** (Claim 4) — 4³ = 64, not just "retry amplification." Formalizes what existing notes describe qualitatively.
  - **Bimodal latency thread-exhaustion quantified example** (Claim 6) — 5% of slow requests → 5,000 thread consumption → 80.4% error rate. Concrete scenario with numbers.
  - **Deadline propagation arithmetic** (Claim 7) — with subtraction at each layer and the "no credit for late assignments" rule.
  - **Cancellation propagation and hedged requests** (Claim 8) — the pattern for propagating "stop work" through the stack is absent from existing notes.
  - **Intra-layer communication prohibition** (Claim 10) — "always go downward in the stack" as a design rule, with three specific failure modes (distributed deadlock, rebalancing under load, bootstrapping complexity).
  - **Cold caching taxonomy** (Claim 9) — latency caches vs. capacity caches, with the recommendation to externalize capacity caches.
  - **Immediate mitigation hierarchy** (Claim 14) — the specific procedure (address trigger → reduce to ~1% → stabilize → ramp up) operationalizes the hysteresis insight.
  - **Triggering conditions taxonomy** (Claim 12) — six categories as a structured incident-response checklist.

## Guide Impact

- **Chapter 02 (Reliability fundamentals)**: This is the most impacted chapter. Add a dedicated "Cascading Failures" subsection with: (a) the definition and positive-feedback mechanism (Claim 1); (b) the resource exhaustion taxonomy (Claim 2) mapped to LLM inference resources (GPU memory/KV-cache, GPU compute/streaming multiprocessors, inference thread pools, GPU interconnect bandwidth); (c) the hysteresis / crash-loop asymmetry (Claim 3) with the specific quantification — a key insight for Ch02's reliability fundamentals that no existing source provides. Currently Ch02 has zero mentions of "cascading" — this would be the first systematic treatment.

- **Chapter 04 (Incident management / Oncall)**: Add the triggering conditions checklist (Claim 12) to the incident-response runbook template — "check recent changes, check process updates, check organic growth, check request profile changes." Add the immediate mitigation hierarchy (Claim 14) as the primary runbook procedure for active cascading failures, with the "drop traffic to ~1%" protocol. The distinction between process health checking and service health checking (Claim 14) is directly actionable for on-call runbooks.

- **Chapter 05 (LLM Ops Reliability)**: Multiple specific additions:
  - Retry policy (Claims 4-5): the multi-level retry product formula (4³ = 64) as the mathematical basis for LLM SDK retry limits. The server-wide retry budget pattern (60 retries/minute/process). The "don't retry permanent errors" rule mapped to HTTP 400 / content-filter rejections.
  - Bimodal latency pattern (Claim 6): the 5%-slow-requests → 80.4%-error-rate worked example as a warning against long inference timeouts. Connection pool limits per model/tenant to prevent tail-latency amplification.
  - Deadline propagation (Claim 7): propagating agent-call timeouts to downstream LLM inference calls with elapsed-time subtraction. The "no credit for late assignments" rule for streaming responses that arrive after client disconnect.
  - Cancellation propagation (Claim 8): propagating client disconnects to GPU inference nodes to free compute. Implementing hedged requests with cancellation for latency-sensitive LLM calls.
  - Cold KV-cache vulnerability (Claim 9): the latency-cache vs. capacity-cache distinction applied to KV-cache. Slow-ramp load introduction for new inference nodes. Externalizing KV-cache to a separate service.
  - Intra-layer communication prohibition (Claim 10): inference routing must not proxy between nodes; use client-directed retries (redirect) instead.

- **Chapter 03 (Runbooks and agents)**: Add the "always go downward in the stack" rule (Claim 10) as an architectural principle for agent systems: agents at the same layer should not proxy to each other — cycles in the request path cause distributed deadlock, load amplification under stress, and recovery complexity.

- **Chapter 00 (Principles)**: Add the closing warning (Claim 15) as a guiding principle: "One outage should not be traded for another." Reliability improvements (retries, failover, caches, unhealthy-server killing) must be evaluated for their cascade-risk contribution, not assumed to be purely beneficial. This pairs with the already-sourced "rate-limit code is there for a reason" lesson from Prodcast 03-08.

## Extraction Notes

- The source URL in the issue body (https://sre.google/resources/book-update/addressing-cascading-failures/) is a thin hub page that points to the actual chapter at https://sre.google/sre-book/addressing-cascading-failures/. Per MINER.md §1, the actual chapter was fetched and read deeply. The workbook link on the hub page (Ch12 NALSD) was NOT followed per the Prospector's guidance — it is fully covered by `docs-google-sre-nalsd-classroom.md`.
- Quotes were gathered from two rounds of WebFetch against the actual chapter URL. The fast-model WebFetch returns a structured summary rather than raw HTML; quotes attributed in quotation marks were confirmed by re-fetching targeted passages. Spot-check any quote against the live URL above.
- `date_published` is approximate. The SRE Book was published by O'Reilly in 2017. The chapter page on sre.google carries no specific publication date separate from the book's publication. The exact date is less material than the content quality: cascading failure mechanisms are foundational, time-invariant SRE knowledge that has not meaningfully changed since publication.
- Confidence is `settled` overall: the source is the canonical SRE Book, authored by a named Google SRE practitioner, published through Google's official and O'Reilly's peer-reviewed channels. The claims are well-evidenced with case studies, worked examples, and quantified scenarios. The material is foundational SRE knowledge that the broader industry has validated through two decades of practice since the book's concepts were developed.
- No contradictions were found against existing source notes. The one potential tension — fast-error response attracting LB traffic (handling-overload Claim 1) vs. this chapter's "fail early and cheaply" recommendation — is a coordination problem, not a contradiction (the chapter assumes load-shedding and load-balancing systems are communicating properly, which is exactly the Dressy case study's fix). No contradiction issue filed.
