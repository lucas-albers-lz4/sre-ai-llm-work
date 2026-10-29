---
source_url: https://www.cncf.io/blog/2026/05/21/how-netease-games-achieved-30-second-llm-cold-starts-on-kubernetes
source_type: blog-post
title: "How NetEase Games achieved 30-second LLM cold starts on Kubernetes"
author: "Haifeng Liao (Senior Infrastructure Engineer, NetEase Games) and Xiang Zhang (Head of AI Infrastructure, NetEase Games)"
date_published: 2026-05-21
date_extracted: 2026-10-29
last_checked: 2026-10-29
status: current
confidence_overall: emerging
issue: "#1942"
---

# How NetEase Games achieved 30-second LLM cold starts on Kubernetes

> A CNCF end-user post from NetEase Games' Tmax AI platform arguing that
> serverless GPU autoscaling is capped by the model-weight data path, and
> reporting a self-measured cold-start reduction from 42 minutes (cross-region
> direct storage) to 14 minutes (conventional Alluxio cache) to 3 minutes
> (Fluid prefetch) and finally ~1 minute to under 30 seconds after production
> tuning, using prefetch-before-startup, cross-namespace shared base models,
> and a dataset/runtime abstraction over the cache runtime.

## Source Context

- **Type**: blog-post (CNCF End User Post; CNCF highlights Kubernetes).
- **Author credibility**: Haifeng Liao is a Senior Infrastructure Engineer at
  NetEase Games and Xiang Zhang is Head of AI Infrastructure there. They run
  the Tmax platform described, so they know the system they operate — but the
  post is also a Fluid adoption story, and Fluid is a CNCF incubating project
  that the CNCF blog is promoting. Treat the mechanisms as practitioner
  experience and the specific durations as self-reported production anecdotes.
- **Scope**: Covers the three coupled Day-2 problems on Tmax (heterogeneous
  GPU capacity, bursty traffic, model-loading-dominated cold starts); why the
  team chose Fluid over running Alluxio directly; the operational features
  that mattered (prefetch workflows, cache elasticity, data-aware scheduling,
  dataset-level isolation with cross-namespace sharing, CSI vs. sidecar
  access, post-deploy cache scale-down); and the 42 → 14 → 3 min → ~1 min /
  <30 s ladder. It does **not** publish methodology, hardware, model names,
  per-region numbers, cache hit rates, failure modes (stale weights after a
  version bump, cache invalidation, prefetch targeting a missing revision),
  or how cold start interacts with readiness probes and request admission.

## Extracted Claims

### Claim 1: Autoscaling value is capped by the data path — elastic GPU compute is only useful if model data can move just as fast
- **Evidence**: The authors' central thesis, stated as the hard lesson from
  running LLM inference in production; the rest of the post is the argument
  and the measured ladder that follows from it.
- **Confidence**: emerging (well-supported systems framing, but asserted from
  one team's production experience rather than demonstrated generally)
- **Quote**: "At NetEase Games, we learned a hard lesson about large language model (LLM) inference in production: elastic compute is only useful if data can move just as fast."
- **Our assessment**: Buy the ordering of bottlenecks. This is the source's
  transferable claim and the reason it belongs in the guide: it reframes the
  cold-start problem from "scale the GPU pool" to "warm the data path where
  the pod will land." It is also a direct conditioning variable on the
  corpus's GPU-autoscaling material — the autoscaler decides *when* to add a
  replica, not whether that replica can load weights in time.

### Claim 2: The real bottleneck was loading model data, not scheduling containers — 70B-class models pull hundreds of gigabytes of weights and can take tens of minutes from remote storage
- **Evidence**: The authors' production observation across regions; they name
  the workload class (70B models) and the storage path (remote/cross-region)
  but publish no model names, hardware, or measurement method.
- **Confidence**: emerging (mechanism is plausible and widely observed;
  magnitudes are single-site and self-reported)
- **Quote**: "For 70B-class models, pulling hundreds of gigabytes of weights from remote storage into inference nodes could take tens of minutes. That erased the value of autoscaling."
- **Our assessment**: The mechanism is the durable part: weight bytes are
  large enough that remote fetch dominates startup, so the scheduler handing
  you a GPU quickly does not make the service ready quickly. Do not carry
  "tens of minutes" as a constant — it is a function of model size, storage
  locality, and bandwidth, none of which the post specifies.

### Claim 3: Three Day-2 problems were tightly coupled — scarce/heterogeneous GPUs, non-uniform traffic, and cold starts dominated by model loading
- **Evidence**: The Tmax problem statement enumerates the three and then says
  they became coupled as LLM usage grew across NPCs, content generation, and
  internal AI services.
- **Confidence**: emerging (problem framing from one platform; no fleet data)
- **Quote**: "First, GPU resources were scarce and heterogeneous. Different workloads require different card types, memory sizes, and scaling patterns. Keeping enough GPU capacity online for peak demand across every team was inefficient."
- **Quote**: "Second, inference traffic was not uniform. Some titles peaked in the evening, others during the day. Some workloads were latency-sensitive online inference; others were batch jobs or fine-tuning tasks."
- **Quote**: "Third, serverless cold starts were dominated by model loading. Even when computing resources became available quickly, the model’s data path remained slow."
- **Our assessment**: The useful reframing is that these are not three
  separate optimization projects. Elastic capacity without a fast data path
  produces an expensive system that still misses spikes ("The result was an
  expensive system that still could not respond to traffic spikes in time.").
  The guide should present capacity planning for LLM serving as at least two
  layers — replica/GPU elasticity and data locality — not one.

### Claim 4: The measured cold-start ladder was 42 minutes (cross-region direct storage) → 14 minutes (conventional Alluxio cache) → 3 minutes (Fluid prefetch) → ~1 minute, sometimes under 30 seconds, after production tuning
- **Evidence**: Two statements of the same progression: an intro "representative
  workload" and a production-results section describing an "earlier benchmark
  path" plus further tuning for two model inference services.
- **Confidence**: anecdotal (single-site, self-reported; no methodology,
  hardware, model names, cache hit rate, or baseline conditions)
- **Quote**: "In one representative workload, model load time was reduced from 42 minutes with cross-region direct storage access to 14 minutes with a traditional Alluxio-based cache and then to 3 minutes after we enabled Fluid’s prefetching workflow."
- **Quote**: "In an earlier benchmark path, model load time dropped from 42 minutes with cross-region direct access to 14 minutes with a conventional cache layer, and then to 3 minutes after enabling Fluid-based prefetching. After further tuning in production, the startup time for two model inference services was reduced to about one minute and, in some cases, even under 30 seconds."
- **Our assessment**: Record the ladder as a decomposition of where the time
  goes — remote access, local/distributed cache, prefetch — not as a benchmark
  result. The step sizes are informative in shape (cache cuts it by ~3x,
  prefetch cuts it by another ~5x, tuning cuts it by ~3x again), but the "30
  seconds" headline is a best case for two services, not an SLO. The guide
  should treat each rung as a distinct mechanism to adopt in order, not a
  guaranteed ratio.

### Claim 5: Prefetch *before* pod startup is the mechanism that removes the cold-start penalty from the request path, with scheduled, event-driven, and proactive warm-up tied to predictable traffic windows
- **Evidence**: The Fluid feature table's LLM-optimization row and the three
  "common patterns" bullets; the authors state pods then do not pay the full
  penalty at runtime.
- **Confidence**: emerging (the operational pattern is concrete and the
  authors report using it; no per-mode measurements)
- **Quote**: "Fluid provided prefetch workflows for scheduled, event-driven, and proactive warm-up. It also lets us optimize for framework-specific access behavior, including vLLM and SGLang-style model-loading patterns, and scale the cache down again after deployment when appropriate."
- **Quote**: "Prefetch before startup so inference Pods do not pay the full cold-start penalty at runtime."
- **Quote**: "Schedule scale-up and warm-up for workloads with predictable traffic windows."
- **Our assessment**: This is the operational core of the post and the
  complement to the corpus's scale-to-zero material. A passive cache still
  makes the first replica after a scale-up pay the full load; prefetch moves
  that cost off the request path and (for predictable windows) ahead of the
  burst. The claim is conditional on traffic being predictable enough to
  schedule warm-up — game titles peaking at known hours is exactly that case,
  and is not universal.

### Claim 6: Cross-namespace shared base models are a cache-memory and version-management control, not just a latency trick — warm a foundation model once and reference it from many services
- **Evidence**: The Fluid isolation/sharing row, the third "common pattern"
  bullet, and the explicit statement that this "mattered more than we expected."
- **Confidence**: emerging (operational reasoning from a multi-tenant
  platform; no memory or cost figures)
- **Quote**: "The last point mattered more than we expected. In a multi-tenant platform, repeated caching of the same model wastes memory and creates version-management overhead. Fluid lets us maintain shared models in a single namespace and expose them to application teams via references rather than duplicate runtime stacks."
- **Quote**: "Cross-namespace models share a common base; they do not have to be repeatedly cached by each team."
- **Our assessment**: High-value multi-tenant pattern: per-namespace
  duplicate caches of the same foundation model waste memory and create
  drift, so sharing is both a cost and a consistency control. The post does
  not address the failure mode sharing invites — a model version bump in the
  shared namespace, or a team that needs a pinned older revision — so the
  guide should pair this pattern with an explicit version-pinning rule rather
  than presenting it as free.

### Claim 7: The operational unit should be the dataset and runtime, not a cache cluster — that abstraction was the main reason the team chose Fluid over deploying Alluxio directly
- **Evidence**: The "Why we didn't just run Alluxio directly" section and the
  constrasting table row on Kubernetes integration.
- **Confidence**: emerging (architectural rationale from the adopting team;
  vendor-aligned because Fluid is the CNCF project the post promotes)
- **Quote**: "With Fluid, the operational unit is not just a cache cluster. It’s a dataset and runtime."
- **Quote**: "That higher-level abstraction was the main reason for choosing Fluid, a Cloud Native Computing Foundation (CNCF) incubating project."
- **Our assessment**: Buy the abstraction argument while flagging its
  provenance. Managing "a dataset and a runtime" maps to how platform teams
  actually think about model artifacts; managing "an Alluxio master and worker
  cluster" maps to operating a cache product. The vendor incentive is real,
  but the abstraction claim is testable against the alternative and the
  authors state the trade-off honestly (Claim 13).

### Claim 8: The dataset abstraction is decoupled from the cache runtime, so the team can keep one operating model and swap Alluxio, JindoCache, or JuiceFS over time
- **Evidence**: The "Data abstraction and runtime decoupling" table row; the
  authors name the candidate runtimes and frame the motive as long-term
  evolution rather than raw performance.
- **Confidence**: emerging (architectural hedge; no evidence of an actual
  runtime swap in production)
- **Quote**: "Fluid separated the dataset abstraction from the runtime layer. That allowed us to maintain a stable operational model while retaining the option to switch runtimes over time, such as Alluxio, JindoCache, or JuiceFS."
- **Our assessment**: This is a portability hedge, and the guide should
  grade it as such. The claim is not "the abstraction is faster"; it is "the
  abstraction reduces lock-in to one cache implementation." That is valuable
  but unexercised here — the post does not show a migration between runtimes,
  so do not treat runtime-swappability as demonstrated.

### Claim 9: Cache elasticity (HPA/KEDA) and data-aware scheduling align compute placement with cached data
- **Evidence**: The "Integration with Kubernetes" table row describing what
  Fluid added over separately managed Alluxio clusters.
- **Confidence**: emerging (feature statement from the adopting team; no
  scaling-latency or placement measurements)
- **Quote**: "Fluid automated runtime deployment and lifecycle management, supported cache elasticity through mechanisms such as HPA/KEDA, and made it easier to align compute placement with cached data through data-aware scheduling."
- **Our assessment**: This is the join to the corpus's GPU-autoscaling note:
  scaling up pods is only half the loop, because the cache must already be
  warm where the pod lands. The post asserts the alignment but gives no
  scheduler configuration, no evidence of how placement is constrained, and
  no measurement of the benefit — so record it as a design requirement
  ("schedule compute onto warm data"), not a validated capability.

### Claim 10: CSI-based and sidecar-based access with webhook-injected sidecars let the same model-loading path work across serverless and non-serverless environments
- **Evidence**: The "Support for heterogeneous compute environments" table
  row, which names both access patterns and the sidecar-injection mechanism.
- **Confidence**: emerging (feature statement; no comparison of the two
  access modes or their overhead)
- **Quote**: "Fluid supported both CSI- and Sidecar-based access patterns. Webhook-based Sidecar injection reduced the amount of application-side change needed to use the same model-loading path across environments."
- **Our assessment**: The operationally interesting part is uniformity:
  one model-loading path across environments means an application does not
  need a different weight-access implementation for serverless vs. ordinary
  pods. But the post does not discuss the cost of each mode (sidecar resource
  overhead, webhook failure modes) or when to choose CSI over sidecar. The
  guide should treat "one access path" as the goal and require the mode choice
  to be measured, not defaulted.

### Claim 11: The distributed cache absorbs startup bursts — when many inference pods launch together, backend storage no longer takes the full pressure
- **Evidence**: The production-results paragraph naming startup bursts as a
  distinct benefit from latency reduction.
- **Confidence**: emerging (mechanism is sound and consistent with how
  distributed caches work; no burst-size or backend-load numbers)
- **Quote**: "Just as important was the distributed cache that helped absorb startup bursts. When many inference Pods were launched together, the platform no longer pushed all of that pressure directly onto the backend storage path."
- **Our assessment**: This is a reliability argument, not just a latency one:
  a cold-start stampede can overload the object store that every replica is
  reading from, turning a scale-up into a correlated failure. The guide should
  call out the stampede explicitly — prefetch plus a distributed cache protects
  the origin, while N replicas fetching directly can amplify load exactly when
  the platform is trying to recover.

### Claim 12: The cache is scaled down again after deployment, so the memory saving exists only during warm-up — a cost/latency trade-off the post does not quantify
- **Evidence**: The LLM-optimization row's "scale the cache down again after
  deployment when appropriate" and the production section's statement that
  latency reduction let them scale GPUs more aggressively during quiet periods.
- **Confidence**: anecdotal (mechanism stated; no numbers on cache size,
  scale-down timing, or the latency risk of shrinking too early)
- **Quote**: "It also lets us optimize for framework-specific access behavior, including vLLM and SGLang-style model-loading patterns, and scale the cache down again after deployment when appropriate."
- **Quote**: "The significant reduction in latency led to a corresponding reduction in cost, allowing us to scale GPU resources more aggressively during quiet periods."
- **Our assessment**: Worth flagging as an unquantified trade. Shrinking the
  cache after launch recovers memory/cost, but a subsequent scale-up or node
  eviction may then pay the load again. The post gives no scale-down policy,
  no trigger, and no failure case where the cache was shrunk too early. Treat
  "scale down after deployment" as a cost lever that must be bounded by the
  next warm-up window.

### Claim 13: The authors' own decision rule is narrow problem vs. operational problem — direct Alluxio is enough for a cache in front of remote storage; the orchestration layer matters only once you need prefetch, sharing, autoscaling, and tenant controls
- **Evidence**: The closing "A useful way to frame the choice" section, which
  explicitly declines to frame the decision as "Fluid versus Alluxio".
- **Confidence**: emerging (a clear, honest decision criterion from the
  adopting team, but still vendor-aligned because Fluid is the higher layer)
- **Quote**: "For us, the comparison was not really “Fluid versus Alluxio” as competing products. It was a choice between solving a narrow problem and solving the operational one."
- **Quote**: "If the requirement is simply to put a cache in front of remote storage, running Alluxio directly may be enough. If the requirement is to operate LLM inference on Kubernetes over time — with prefetching, sharing, autoscaling, and multi-tenant controls — then the higher-level data orchestration model matters."
- **Our assessment**: Strongest guide-worthy artifact in the post because it
  gives the reader a way to decide *without* adopting the vendor's product.
  The guide should present it as a staged adoption rule: start with a cache if
  that is the whole problem; add an orchestration layer when the operational
  requirements (prefetch, sharing, elasticity, tenancy) accumulate. Note that
  the post does not price the higher layer, so "matters" is qualitative.

### Claim 14 (vendor-aligned): The latency reduction translated into cost reduction and allowed the team to scale GPU resources more aggressively during quiet periods
- **Evidence**: One sentence in the production-results section; no cost
  figures, utilization data, or comparison against the previous policy.
- **Confidence**: anecdotal (directionally plausible; entirely unquantified)
- **Quote**: "The significant reduction in latency led to a corresponding reduction in cost, allowing us to scale GPU resources more aggressively during quiet periods."
- **Our assessment**: Do not carry this as evidence of savings. The causal
  story is plausible — predictable cold starts make aggressive scale-down
  safer — but the post supplies no numbers, and the corpus's accelerator-power
  note (Kepler) already warns that GPU cost/energy telemetry is immature. Keep
  the claim as motivation and pair it with a measurement requirement.

### Claim 15 (scope caveat): This is a CNCF Member/End User Post promoting Fluid, a CNCF incubating project; the durations are self-reported and no benchmark methodology, hardware, model sizes, or cache-hit rates are published
- **Evidence**: The post's framing and "CNCF projects highlighted in this
  post" Kubernetes/Fluid promotion, plus the absence of any methodology
  section; the authors are the platform's own engineers.
- **Confidence**: settled (as a statement about the source's provenance and
  evidentiary limits)
- **Quote**: "CNCF projects highlighted in this post"
- **Our assessment**: The mechanisms are useful; the numbers are not
  transferable. Grade the architectural claims `emerging`, the specific
  durations `anecdotal`, and never present "<30 seconds" as a general SLO.
  This caveat is why the specific durations, not the mechanism-level claims,
  carry `confidence_overall: emerging` only at the mechanism level.

## Concrete Artifacts

### What Fluid added over running Alluxio directly (verbatim table cells)

```
Dimension: Integration with Kubernetes
  Challenge with Alluxio directly:
    "Alluxio master and worker clusters had to be deployed and managed separately, with limited alignment to Kubernetes-native lifecycle and scheduling behavior."
  What Fluid added:
    "Fluid automated runtime deployment and lifecycle management, supported cache elasticity through mechanisms such as HPA/KEDA, and made it easier to align compute placement with cached data through data-aware scheduling."

Dimension: LLM inference-specific optimization
  Challenge:
    "General-purpose caching improved access times, but loading large models still required custom warmup logic and additional operational work."
  What Fluid added:
    "Fluid provided prefetch workflows for scheduled, event-driven, and proactive warm-up. It also lets us optimize for framework-specific access behavior, including vLLM and SGLang-style model-loading patterns, and scale the cache down again after deployment when appropriate."

Dimension: Data abstraction and runtime decoupling
  Challenge:
    "A direct deployment model tied operations more closely to a single cache implementation, making long-term evolution harder."
  What Fluid added:
    "Fluid separated the dataset abstraction from the runtime layer. That allowed us to maintain a stable operational model while retaining the option to switch runtimes over time, such as Alluxio, JindoCache, or JuiceFS."

Dimension: Isolation and sharing across teams
  Challenge:
    "Multi-team sharing required more manual namespace, quota, and configuration design, especially when common base models had to be reused safely."
  What Fluid added:
    "Fluid supported dataset-level logical isolation and cross-namespace sharing, with access control aligned to native Kubernetes mechanisms."

Dimension: Support for heterogeneous compute environments
  Challenge:
    "Deploying and managing the same data access model across environments, such as serverless containers, was more difficult and usually required additional integration work."
  What Fluid added:
    "Fluid supported both CSI- and Sidecar-based access patterns. Webhook-based Sidecar injection reduced the amount of application-side change needed to use the same model-loading path across environments."
```

Attribution: https://www.cncf.io/blog/2026/05/21/how-netease-games-achieved-30-second-llm-cold-starts-on-kubernetes,
"Fluid: Adding operational control to Alluxio". Cell text transcribed verbatim;
the source renders this as a three-column table (`Dimension`,
`Challenges With Running Alluxio Directly`, `What Fluid Added`).

### The operational patterns the team named (verbatim bullets)

```
- Prefetch before startup so inference Pods do not pay the full cold-start penalty at runtime.
- Schedule scale-up and warm-up for workloads with predictable traffic windows.
- Cross-namespace models share a common base; they do not have to be repeatedly cached by each team.
```

Attribution: same page, immediately below the feature table.

### Cold-start ladder (verbatim)

```
In one representative workload, model load time was reduced from 42 minutes
with cross-region direct storage access to 14 minutes with a traditional
Alluxio-based cache and then to 3 minutes after we enabled Fluid’s prefetching
workflow.
```

```
In an earlier benchmark path, model load time dropped from 42 minutes with
cross-region direct access to 14 minutes with a conventional cache layer, and
then to 3 minutes after enabling Fluid-based prefetching. After further tuning
in production, the startup time for two model inference services was reduced
to about one minute and, in some cases, even under 30 seconds.
```

Attribution: same page, introduction and "What changed in production" respectively.

### Decision rule (verbatim)

```
If the requirement is simply to put a cache in front of remote storage, running
Alluxio directly may be enough. If the requirement is to operate LLM inference
on Kubernetes over time — with prefetching, sharing, autoscaling, and
multi-tenant controls — then the higher-level data orchestration model matters.
```

Attribution: same page, "A useful way to frame the choice".

## Cross-References

- **Extends**: `source-notes/blog-cncf-gpu-autoscaling-keda-external-scaler.md`
  — that note's **Claim 1** establishes that Kubernetes autoscaling is blind
  to the accelerator, **Claim 9** separates the scale-to-zero activation gate
  from the steady-state target, and **Claim 11** shows a `minReplicaCount: 0`
  vLLM workload scaling on GPU memory. Its own assessment of Claim 11 already
  flags that "scale-to-zero still pays the vLLM cold start." This source
  supplies the other half of that loop: the data path must be warm *where and
  when* the replica lands (Claims 1, 5, 9 here). The two together say that
  replica elasticity and data locality are separate control planes, and an
  autoscaler that ignores the second can scale into a multi-minute load
  (Claim 4). Do not merge them — cross-link.

- **Extends**: `source-notes/blog-cncf-running-self-hosted-llm-kubernetes-vllm.md`
  — that note's **Claim 3** (Hugging Face cache on a PVC) and **Claim 4**
  (scale-to-zero preserves the PVC and cached weights) solve the same
  "don't re-download on restart" problem at single-node/lab scale, and its
  **Claim 5** establishes a multi-minute cold start dominated by weight fetch
  plus engine init. This source extends that from a per-pod PVC to a
  fleet-scale distributed cache with prefetch and cross-namespace sharing
  (Claims 4–6, 11). Do not duplicate the PVC recommendation; the new content
  is locality *ahead of* scheduling and sharing across tenants.

- **Extends**: `source-notes/blog-cncf-kubernetes-health-checks-waking-services.md`
  — that note's **Claim 1** shows ordinary health-check traffic defeating
  scale-to-zero, and its **Claim 11** notes that GPU pods are a primary
  beneficiary because cold-start fear keeps expensive accelerators running.
  This source attacks the same trade-off from the other side: if cold start
  is reduced to ~1 minute (Claim 4) and warm-up can be scheduled (Claim 5),
  then keeping GPUs at zero becomes more tolerable. The two notes together
  define the scale-to-zero budget: probe hygiene on one side, warm-data
  startup latency on the other.

- **Extends**: `source-notes/blog-cncf-goodput-more-than-throughput-llm-serving.md`
  — that note's **Claim 1** defines goodput as completed requests that meet
  latency targets, and **Claim 7** scopes its measurements to after warm-up.
  Cold start is a distinct capacity dimension that goodput measurement will
  miss unless startup requests are counted: a request admitted during a cold
  start can blow TTFT/TPOT even though steady-state goodput looks healthy.
  Cross-link the two as "what to measure once warm" vs. "how to get warm."

- **Extends**: `source-notes/blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md`
  — that note's **Claim 9** (GPU time-slicing via DRA) and **Claim 10**
  (Cluster Autoscaler possibly provisioning GPU nodes) cover device
  allocation and node provisioning. This source is the layer between
  scheduling and serving: even a correctly allocated GPU cannot start
  inference until hundreds of GB of weights are local (Claim 2). Pair them as
  three distinct capacity layers — node provisioning, device allocation, and
  data locality — and note this post covers only the third.

- **Corroborates**: `source-notes/failure-cncf-kubeflow-cilium-60-idle-gpus.md`
  — that note's **Claim 4** treats GPU utilization as the observable signal
  for wasted accelerator spend ("In our lab, GPU utilization went from around 40% to around 85% the moment the group was co-located.")
  and **Claim 6** says GPU utilization plus pod-zone metrics exposed the
  problem in seconds. This source agrees on the underlying economic premise —
  idle or slow-starting accelerators are expensive — but its waste signal is
  cache memory and version drift (Claim 6), not GPU utilization. The two are
  complementary observability lenses on accelerator waste, not the same claim.

- **Extends**: `source-notes/blog-cncf-kepler-rearchitected-power-accuracy.md`
  — that note's **Claim 10** states GPU power monitoring exists only behind an
  experimental flag and explicitly seeks end-user validation. This source's
  cost claim (Claim 14) is likewise unquantified, so the guide should not
  present "faster cold start → lower cost" as measured. Pair the two when
  requiring cost evidence for accelerator decisions.

- **Contradicts**: None. No existing note claims a cold-start mechanism,
  prefetch, distributed model caching, or cross-namespace dataset sharing.
  The nearest notes differ in scale (single-node PVC) or layer (GPU
  autoscaling control loop, goodput after warm-up), so they are extensions,
  not disagreements. Verified against `CONTRADICTIONS.md` (no `C-NNN` entries
  yet) and open `contradiction`-labeled issues; no contradiction issue filed.

- **Novel**: First source note in the corpus on distributed model-weight
  caching and prefetch. Specifically new: (1) the cold-start decomposition
  42 min → 14 min → 3 min → ~1 min / <30 s; (2) prefetch-before-startup with
  scheduled/event-driven/proactive warm-up; (3) cross-namespace shared base
  models as a memory and version-management control; (4) the dataset/runtime
  abstraction decoupled from the cache runtime; (5) cache elasticity plus
  data-aware scheduling as the placement half of autoscaling; (6) the
  narrow-problem vs. operational-problem adoption rule.

## Guide Impact

- **Chapter 05 (Cost, capacity, and fallback patterns, guide/05-llm-ops-reliability.md:970)**:
  Add a subsection on cold starts for self-hosted/serverless GPU inference.
  State the bottleneck ordering first — scheduling is not the limit; model
  weight transfer is [Claim 1, Claim 2]. Present the ladder as one team's
  representative decomposition, not a benchmark [Claim 4], and label the
  <30 s figure anecdotal. Then give the operational pattern: prefetch before
  startup, schedule warm-up to known traffic windows [Claim 5], share base
  models across namespaces with explicit version pinning [Claim 6], and
  protect the origin with a distributed cache during launch bursts [Claim 11].
  Close with the staged adoption rule: a plain cache may be enough, and an
  orchestration layer only pays once prefetch, sharing, elasticity, and tenant
  controls are all needed [Claim 13]. Pair with the GPU-autoscaling note so
  the chapter presents replica elasticity and data locality as two control
  planes [source: blog-cncf-gpu-autoscaling-keda-external-scaler, Claims 1, 9, 11].

- **Chapter 02 (SLI measurement design / readiness, guide/02-observability.md:227)**:
  Add that startup latency for LLM inference is a data-path SLI, not a
  pod-scheduling SLI. Measure time from replica creation to weights-local /
  model-loaded, separately from container start, so a data-path regression is
  not mistaken for scheduler latency [Claim 2, Claim 4]. Cross-link the
  existing readiness-by-log-line material [source: blog-cncf-running-self-hosted-llm-kubernetes-vllm, Claim 5] and note that the post does not cover how
  cold-start latency interacts with readiness probes or request admission —
  worth an explicit "not covered" marker.

- **Chapter 04 (Oncall and toil, guide/04-oncall-and-toil.md)**:
  Add cache warm-up and per-namespace duplicate model caches to the toil
  inventory, with the shared-base-model pattern as the remediation [Claim 6].
  Add the cold-start stampede to the runbook: when many inference replicas
  launch together, verify the cache/origin path is absorbing the burst rather
  than saturating backend storage [Claim 11]. Include the scale-down-after-
  deploy lever as a policy that must be bounded by the next warm-up window
  [Claim 12].

## Extraction Notes

- Deep-read of the full CNCF End User Post (single page, no substantive
  linked sub-pages followed; the post links to Fluid's CNCF project page and
  two thenewstack.io background pieces, which were not needed for the claims).
  No paywall; fully readable. All quotes copied character-for-character from
  the rendered page, including the curly apostrophes in "Fluid’s" and "It’s".
- The feature table is an HTML/Markdown table; the artifact block transcribes
  cell text verbatim into a labelled form and preserves the three-column
  structure. Bold markers on the three pattern bullets were stripped (they are
  formatting, not content).
- `confidence_overall: emerging` — the mechanisms are sound and several are
  corroborated by adjacent notes (prefetch-before-startup, shared base models,
  cache/origin protection during launch bursts). But every quantitative claim
  rests on one self-reported production environment with no methodology,
  hardware, model names, cache-hit rates, or per-region figures, and the post
  is a Fluid adoption story published on the project's foundation blog. Those
  numbers are graded `anecdotal` (Claim 4, Claim 14, Claim 15); only the
  mechanism-level claims are `emerging`. The Prospector's caveat ("do not
  present the 30-second figure as a generalizable SLO") is carried into
  Claim 4 and Claim 15.
- The post's "three coupled problems" and the "Day 2" framing were extracted
  as Claim 3; the "Why we didn't just run Alluxio directly" material became
  Claims 7–10; the production-results section became Claims 4, 11, 12, 14.
  The intro's "representative workload" and the results section's "earlier
  benchmark path" are the same ladder stated twice; both quotes are recorded
  in Claim 4 so the Assayer can verify without chasing one wording.
- `miner-related-notes.md` candidates (10), each cited or explicitly dismissed
  per MINER.md §4:
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` —
    dismissed; gaming/retail SLO granularity, no infrastructure or data-path
    content.
  - `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` —
    dismissed; multi-agent security platform; its HPA mention is ordinary
    microservice scaling, not model loading.
  - `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
    dismissed; imperative vs. declarative change workflows.
  - `source-notes/docs-google-sre-prodcast-03-01.md` — dismissed; SRE
    methodology and organizational influence.
  - `source-notes/docs-litellm-completion-input-params.md` — dismissed;
    LiteLLM completion parameter gates.
  - `source-notes/docs-litellm-batches-api.md` — dismissed; LiteLLM batch
    rate limiting.
  - `source-notes/docs-litellm-bedrock-invoke.md` — dismissed; Bedrock
    Invoke passthrough routing.
  - `source-notes/docs-google-sre-eliminating-toil.md` — dismissed from
    Cross-References; toil taxonomy/measurement, not cache warm-up. Guide
    Impact nevertheless uses it as the natural home for warm-up toil (Ch04).
  - `source-notes/docs-google-sre-reliable-product-launches.md` — dismissed;
    launch coordination/checklists.
  - `source-notes/docs-litellm-anthropic-advisor-tool.md` — dismissed;
    within-request model composition.
- Additional cross-references were found by searching `source-notes/` directly:
  `blog-cncf-running-self-hosted-llm-kubernetes-vllm.md`,
  `blog-cncf-gpu-autoscaling-keda-external-scaler.md`,
  `blog-cncf-kubernetes-health-checks-waking-services.md`,
  `blog-cncf-goodput-more-than-throughput-llm-serving.md`,
  `blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md`,
  `failure-cncf-kubeflow-cilium-60-idle-gpus.md`, and
  `blog-cncf-kepler-rearchitected-power-accuracy.md`.
- Every cited claim number was re-read in its source note and verified before
  writing (MINER.md §4b): GPU-autoscaling Claims 1, 9, 11; self-hosted-vLLM
  Claims 3, 4, 5; health-checks Claims 1, 11; goodput Claims 1, 7; DRA
  Claims 9, 10; Kubeflow/Cilium failure Claim 4; Kepler Claim 10. No
  fabricated numbers or quotes. No contradiction found; no contradiction issue
  filed.
