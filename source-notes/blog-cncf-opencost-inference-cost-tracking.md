---
source_url: https://www.cncf.io/blog/2026/08/05/opencost-1-121-0-first-of-a-kind-kubernetes-inference-cost-tracking
source_type: blog-post
title: "OpenCost 1.121.0: First-of-a-kind Kubernetes inference cost tracking"
author: "Sima Nadler (Senior Program Manager, IBM Research) and Alex Meijer (OpenCost Maintainer)"
date_published: 2026-08-05
date_extracted: 2026-10-31
last_checked: 2026-10-31
status: current
confidence_overall: emerging
issue: "#1955"
---

# OpenCost 1.121.0: First-of-a-kind Kubernetes inference cost tracking

> A CNCF project post announcing OpenCost's integration with llm-d, whose
> transferable content is a **two-cost model for self-hosted inference**:
> *usage-based* cost per million tokens (active compute only) is stable across
> load, while *allocation-based* cost per million tokens (GPU reservation, idle
> weights, shared gateway/KV-cache infra) rises as utilization falls — so
> build-vs-buy must compare allocation-based cost, not usage-based, against the
> external API price. It supplies concrete metrics (`llm_total_hourly_cost`,
> `llm_cost_per_million_tokens`), labels, and a 2×2 cost diagnostic, validated
> only by the authors' own 109-GPU PoC.

## Source Context

- **Type**: blog-post (CNCF Project Post; CNCF highlights OpenCost and llm-d).
  The authors are an IBM Research senior program manager and an OpenCost
  maintainer, so this is project-engineering writing rather than generic vendor
  marketing — but it announces the authors' own feature and supplies no raw
  dataset or independent replication.
- **Author credibility**: Sima Nadler (Senior Program Manager, IBM Research) and
  Alex Meijer (OpenCost Maintainer). They understand the cost-allocation engine
  and the llm-d/vLLM metric sources they describe. The evidence is a PoC they
  ran and "validated" on a 109-GPU cluster with 30 models; the article does not
  publish the validation method, the underlying data, or a reproduction harness.
- **Scope**: Covers the inference-cost gap, the usage-vs-allocation cost model
  and utilization identity, the build-vs-buy trap, the metric/label surface,
  input/output (prefill/decode) cost splitting, KV-cache and llm-d component
  accounting via `SharedLabels`, a 2×2 diagnosis matrix, and the feature's
  status in OpenCost 1.121.0. Does NOT cover per-request pricing, multi-tenant
  fairness policy, actual dollar measurements beyond illustrative examples,
  the OpenCost UI integration (still future work), or the promised idle-GPU
  detection/optimization-savings estimation (also future work).

## Extracted Claims

### Claim 1: Platform teams can see infrastructure spend and token throughput but not the connection between them, so per-model and per-token cost is unknown and every AI infrastructure decision is a guess
- **Evidence**: The article's problem framing, followed by three concrete unanswerable questions (self-hosting vs SaaS, cost-efficient model, team consumption).
- **Confidence**: emerging (widely observed operational gap; asserted here, not measured)
- **Quote**: "Platform teams today operate in a fog regarding AI inference costs—they see infrastructure spend and track token throughput, but the connection between those numbers is invisible."
- **Our assessment**: Buy the framing. It is the cost-attribution instance of the corpus's existing observability rule that pre-aggregated metrics answer only questions you anticipated: a GPU bill and a token counter are two aggregates with no join key. The guide should treat "what does each token cost?" as an attribution problem (model + namespace + basis), not a billing-report problem.

### Claim 2: Cost is not price — a SaaS provider may price below or above its own cost — so when comparing self-hosting to SaaS, the enterprise's cost for SaaS inference is the provider's price
- **Evidence**: An explicit call-out box in the introduction; no data supplied.
- **Confidence**: settled (definitional/accounting distinction)
- **Quote**: "SaaS providers may price below cost to gain market share or well above cost for premium models. When comparing self-hosting costs to SaaS, keep this distinction in mind. An enterprise’s cost for SaaS inference is the provider’s price."
- **Our assessment**: Important guardrail for any build-vs-buy guide advice. The comparison is not "our cost vs their cost"; it is "our allocation-based cost vs their price." That asymmetry is also why a provider's below-cost pricing can make the API rational even when self-hosting looks efficient on compute — and why the guide should not treat a low API price as evidence about the provider's true cost.

### Claim 3: A loaded model that is idle still burns GPU budget because its weights occupy VRAM, and low-traffic models can spend ~95% of their time in this warm-but-idle state
- **Evidence**: The GPU-economics paragraph, with the 95% figure given as an example rather than a measured distribution.
- **Confidence**: emerging (mechanism is settled; the 95% figure is illustrative/anecdotal)
- **Quote**: "A GPU sitting idle with a model loaded but no requests arriving is equally expensive, because the model’s weights occupy VRAM whether or not inference is happening. For example, a low-traffic model might spend 95% of its time in this “warm but idle” state, burning through your budget while contributing zero productive tokens."
- **Our assessment**: The "warm but idle" failure mode is the operational heart of the post and maps directly onto the corpus's scale-to-zero/cold-start trade-off: keeping weights resident buys latency and pays for it continuously. The 95% number is an example, not a measured benchmark; carry the mechanism, not the percentage, into the guide.

### Claim 4: Allocation-based cost per model includes weights reservation, active-inference compute, and a share of shared gateway/KV-cache infrastructure; it reconciles with the infrastructure bill and answers "what is this model costing us?"
- **Evidence**: The explicit definition contrasting the two cost bases, followed by the reconciliation and question it answers.
- **Confidence**: emerging (definitional model implemented in the PoC; not independently validated)
- **Quote**: "GPU memory reserved for its weights, compute consumed during active inference, and a share of common infrastructure components such as gateway and KV cache storage. This is the cost of having the model available. It reconciles with your infrastructure bill and answers the question, “What is this model costing us?”"
- **Our assessment**: Buy this as the accounting definition the guide should adopt. The load-bearing word is "available": allocation cost is the cost of *readiness*, which is why it includes idle VRAM and shared components that usage cost excludes. Because it reconciles to the bill, it is the correct basis for chargeback/showback — a usage-based number cannot be summed to the invoice.

### Claim 5: Usage-based cost per model includes only active-inference infrastructure cost and credits KV-cache hits; the gap between usage and allocation cost is the cost of keeping the model warm and ready
- **Evidence**: The paired definition and the sentence naming what the gap represents, plus the workload-dependent interpretation of that gap.
- **Confidence**: emerging (definitional model; the "gap" interpretation is the authors' framing)
- **Quote**: "The gap between the two figures represents the cost of keeping the model warm and ready. Depending on the workload, that gap may reflect a deliberate latency tradeoff, an opportunity to improve utilization, or both."
- **Our assessment**: This is the cleanest statement of why two metrics exist. The gap is not waste by definition — it can be a purchased latency guarantee — so the guide should frame it as a *decision variable* to inspect, not an alert that always means "right-size." That distinction is what keeps the advice from becoming "always consolidate," which would be wrong for latency-critical low-volume models.

### Claim 6: Usage-based cost per million tokens is stable regardless of load, while allocation-based cost per million tokens varies with utilization — and the allocation figure is the relevant one for build-vs-buy
- **Evidence**: The two paragraphs defining each per-million-token metric and naming the decision each supports.
- **Confidence**: emerging (the math follows from the definitions; the recommendation is the authors')
- **Quote**: "Usage-based cost per million tokens is stable regardless of how busy the model is. It reflects the compute cost of active inference and is useful for comparing models and hardware configurations or for benchmarking active-inference costs against external API prices."
- **Quote**: "Allocation-based cost per million tokens varies with utilization. A model serving light traffic will have a higher allocation-based cost per token because fixed hosting costs—GPU reservation, model loading, and infrastructure components—are spread across fewer tokens. This is the relevant metric for build-vs-buy decisions."
- **Our assessment**: The stability property is the transferable insight: usage-based cost is a *hardware/model efficiency* measure, allocation-based cost is a *deployment economics* measure. A team that benchmarks hardware on usage-based cost and then makes a procurement decision on it has switched questions mid-analysis. The guide should state which question each metric answers before presenting either.

### Claim 7: Utilization can be derived directly as usage-based cost per million tokens divided by allocation-based cost per million tokens, without a separate utilization metric
- **Evidence**: The explicit formula and worked example ($1.00 ÷ $4.00 = 25%).
- **Confidence**: settled (arithmetic identity given the two cost definitions)
- **Quote**: "The relationship between the two directly expresses GPU utilization without needing a separate metric:"
- **Our assessment**: Buy the identity, with one caveat: it is *cost-weighted* utilization, not SM occupancy. It answers "what fraction of the hosting cost produced billable tokens," which is the economically relevant denominator — and is more useful for FinOps than `nvidia-smi` utilization, which can read high while serving little useful output. Do not conflate the two in the guide; name it "cost utilization" or "allocation utilization."

### Claim 8: The build-vs-buy trap is comparing usage-based self-host cost to an API price; at 25% utilization a $1.00/Mtok usage cost is really $4.00/Mtok allocation cost, so a $2.00/Mtok API is cheaper, and self-hosting becomes competitive only above ~50% utilization
- **Evidence**: A worked dollar example and the explicit conclusion; the ~50% crossover is stated as an approximation, not derived from a dataset.
- **Confidence**: emerging (the arithmetic is sound and illustrative; the 50% threshold is a rule of thumb, not a measured break-even across hardware/prices)
- **Quote**: "If your model’s usage-based cost is $1.00 per million tokens and the SaaS API charges $2.00, self-hosted appears cheaper. But usage-based cost captures only active compute; it excludes GPU reservation, idle time, and infrastructure overhead. At 25% utilization, the actual self-hosting cost is $4.00 per million tokens, not $1.00."
- **Quote**: "Self-hosting becomes competitive above ~50% utilization."
- **Our assessment**: This is the highest-value decision rule in the source and should be lifted nearly verbatim. The ~50% crossover depends on the ratio of API price to usage cost and on which shared costs are included, so present it as a *worked example that must be recomputed with your own numbers*, not a universal threshold. The guide should require the comparison to name the utilization assumption explicitly; an unqualified "self-hosting is cheaper" claim is the trap this source exists to expose.

### Claim 9: Raising utilization through smarter routing, model sharing, or traffic consolidation lowers allocation-based cost per token and can make self-hosting economical
- **Evidence**: The optimization-target paragraph immediately after the trap.
- **Confidence**: emerging (follows from the allocation-cost definition; no measured savings)
- **Quote**: "This framing also gives you an optimization target: increasing utilization through smarter routing, model sharing, or traffic consolidation reduces the allocation-based cost per token and can make self-hosting economical."
- **Our assessment**: Buy the direction, and note the operational tension the post does not resolve: traffic consolidation and model sharing improve cost utilization but can worsen isolation, blast radius, and latency SLOs. In the guide this belongs alongside the routing-as-cost-decision material, with the trade-off stated — consolidation is a capacity lever, not a free win.

### Claim 10: OpenCost 1.121.0 publishes `llm_total_hourly_cost` (hourly cost per model) and `llm_cost_per_million_tokens` (blended, with input/output cost labels) to Prometheus and the OpenCost REST API, labeled by `model_name`, `model_version`, `namespace`, `cost_basis`, and `workload_type`
- **Evidence**: The metric table, the label sentence, and the statement that they are exposed via Prometheus and the REST API.
- **Confidence**: settled (shipped feature statement); the *values* depend on the deployment's OpenCost pricing inputs, which the post does not cover
- **Quote**: "The result is a new set of inference cost metrics published to Prometheus and available via OpenCost’s REST API:"
- **Quote**: "All metrics include labels for `model_name`, `model_version`, `namespace`, `cost_basis`(usage vs. allocation), and `workload_type` (currently always “inference”)."
- **Our assessment**: The label set is the reusable design: `cost_basis` as a *label* rather than two metric names means a single query can compare usage and allocation cost per model, and `namespace` is the chargeback join key. `workload_type` being currently always "inference" is a placeholder, not a useful dimension yet — do not build dashboards that assume it varies. The guide should require `cost_basis` to be surfaced explicitly so nobody compares a usage figure to an allocation figure by accident.

### Claim 11: Input and output token costs are reported separately because they map to prefill and decode, which is essential for accurate attribution in disaggregated serving; the per-token metrics also account for KV-cache-hit savings on input processing
- **Evidence**: The explicit rationale paragraph tying token classes to serving phases and to disaggregated deployments.
- **Confidence**: settled (prefill/decode mapping is architectural; the KV-cache accounting is a stated feature of the shipped metrics)
- **Quote**: "Input and output token costs (including reasoning tokens) are reported separately because they reflect different compute workloads. Input tokens trigger the prefill phase, while output tokens drive the decode phase. In disaggregated serving deployments—where prefill and decode run on separate hardware—this distinction is essential for accurate cost attribution. The per-token metrics also account for the effect of KV cache hits on input-token processing costs."
- **Our assessment**: This is the most technically substantive claim and it connects the cost layer to the corpus's goodput/prefill-decode note. A blended per-token price hides the fact that prefill and decode have different hardware economics; a single blended number is fine for a rough comparison but not for tuning a disaggregated deployment. The KV-cache credit is the cost counterpart of the caching behavior already documented elsewhere: cache hits are not just latency wins, they are input-token cost reductions, and a cost model that ignores them overstates prefill spend.

### Claim 12: A complete model cost includes llm-d components beyond the GPU — EPP scheduler, gateway proxy, tiered KV cache (up to 18 TB), and the Workload Variant Autoscaler — with shared components attributed via OpenCost `SharedLabels` and counted only in allocation-based cost
- **Evidence**: The component list, the 18 TB figure, the `SharedLabels` mechanism description, and the explicit inclusion/exclusion rule.
- **Confidence**: emerging (component list and mechanism are concrete; the 18 TB figure is an example, not a measured deployment)
- **Quote**: "In tiered-cache deployments, this can reach 18 TB of persistent storage. The integration treats it as an allocation cost because KV cache capacity is sized at deployment time rather than in proportion to request volume."
- **Quote**: "The SharedLabels approach keeps llm-d and OpenCost decoupled: llm-d components are labeled at deployment time, and OpenCost’s shared-cost distribution logic handles attribution without requiring OpenCost to understand llm-d’s internal architecture. These shared costs are included in allocation-based costs but excluded from usage-based costs."
- **Our assessment**: The `SharedLabels` pattern is the reusable engineering idea: attribute shared infrastructure by deployment-time labels and let the cost engine distribute, rather than teaching the cost engine each project's topology. That generalizes to any inference stack with a scheduler, gateway, and cache tier. The 18 TB figure should be read as "cache capacity can dominate the storage bill," not as a benchmark; and the allocation-only rule is correct — cache is sized for readiness, so charging it to active tokens would make usage cost vary with deployment size.

### Claim 13: The four combinations of allocation and usage cost form a 2×2 diagnostic that maps each quadrant to an action — utilization problem, wrong model, well-sized, or model/hardware fit
- **Evidence**: The explicit four-row matrix with a diagnosis for each quadrant.
- **Confidence**: emerging (a useful decision heuristic; no measured validation of the recommended actions)
- **Quote**: "The four combinations of allocation-based and usage-based costs each tell a distinct story:"
- **Our assessment**: Adopt this as the runbook-shaped artifact. It is more actionable than either metric alone because it separates "expensive to host" from "expensive to run," which have different remedies (sharing/consolidation vs quantization/hardware fit). Caveat: the quadrants are relative, so the guide must say "high/low against what baseline" — a raw dollar threshold is meaningless across clusters. The matrix is a triage starting point, not a verdict.

### Claim 14: The feature shipped in OpenCost 1.121.0 after a PoC on a 109-GPU cluster with 30 models, and vLLM users who do not run llm-d also benefit because the token counters come from vLLM
- **Evidence**: The "Where things stand" section, the PoC sentence, the release call-out, and the vLLM note near the top.
- **Confidence**: emerging (release status is settled; "validated" is the authors' own claim with no published method or data)
- **Quote**: "A proof-of-concept was implemented and tested on a cluster with 109 GPUs and 30 deployed AI models, and the generated metrics were validated."
- **Quote**: "Note: vLLM users who do not use llm-d can also benefit from these capabilities, since the core metrics used to calculate model and per-token costs come from vLLM."
- **Our assessment**: Record the release status and the vLLM portability, but grade the validation as self-reported. A 109-GPU/30-model PoC is a serious scale for a first implementation, yet the post publishes no error bars, no comparison to a ground-truth bill, and no method for "validated." Treat the metrics as available and plausible, not as audited. The vLLM note matters for scope: the note is not llm-d-only, and the guide should not imply that adopting llm-d is a prerequisite for token-cost attribution.

### Claim 15: The metrics support FinOps workflows — chargeback/showback by namespace and team label, underutilized-model detection, and a future smart router that factors per-token cost into routing alongside latency and throughput
- **Evidence**: The closing use-case paragraph; the smart router is described as something llm-d "is developing," not a shipped capability.
- **Confidence**: emerging for chargeback/showback (follows from the labels); anecdotal for the smart-router use (future work)
- **Quote**: "A finance team running a chargeback program can query costs by namespace and team label to generate showback reports for billing periods. A FinOps team can identify underutilized models and quantify the savings from right-sizing or decommissioning."
- **Our assessment**: The chargeback use is the immediate, defensible one: `namespace` plus allocation-based cost reconciles to the bill, which is exactly what a showback report needs. The smart-router idea is forward-looking and should be flagged as such; routing on per-token cost also creates a feedback loop (routing changes utilization, which changes allocation cost per token), which the post does not discuss and the guide should not present as solved.

## Concrete Artifacts

**Utilization identity and worked example (verbatim from source):**
```
Utilization = usage-based cost per million tokens / allocation-based cost per million tokens

Example:
  Usage-based:       $1.00 / million tokens  (compute only)
  Allocation-based:  $4.00 / million tokens  (full hosting cost)
  Utilization:       25%
```

**Build-vs-buy worked example (verbatim from source):**
```
Self-hosted model at 25% utilization:
  Usage-based cost per million tokens:      $1.00  (compute only — misleading)
  Allocation-based cost per million tokens: $4.00  (real cost — use this)
  External API price per million tokens:    $2.00

Conclusion: The external API is cheaper at the current utilization.
Self-hosting becomes competitive above ~50% utilization.
```

**Inference cost metrics (verbatim cell text from the source's table; the page
renders it as an HTML table, reproduced here in Markdown):**

| Metric | What it measures |
|---|---|
| `llm_total_hourly_cost` | Hourly cost per model |
| `llm_cost_per_million_tokens` | Blended cost per million tokens. Includes labels breaking out input and output costs per million tokens |

**2×2 cost diagnostic (verbatim cell text from the source's table; the page
renders it as an HTML table, reproduced here in Markdown):**

| Allocation cost | Usage cost per million tokens | Diagnosis |
|---|---|---|
| High | Low | Costly to keep available but efficient during inference—utilization is the problem. Consider model sharing or traffic consolidation. |
| High | High | Expensive to host and expensive to run. Evaluate whether this model is the right choice for the workload. |
| Low | Low | Likely a well-sized deployment. The model fits its traffic profile. |
| Low | High | Cheap to host, but inference itself is costly. Evaluate model size, quantization, and hardware fit. |

**Metric sources named in the post (verbatim):** `vllm:prompt_tokens_total`,
`vllm:generation_tokens_total`, GPU costs from OpenCost's existing allocation
engine, and processing-time metrics that support separate input/output cost
calculations.

## Cross-References

- **Extends**: `source-notes/blog-cncf-gpu-autoscaling-keda-external-scaler.md` — that note's **Claim 1** establishes that the default autoscaling path is blind to the GPU, and **Claim 9** makes the KEDA `activationThreshold` the cost knob that decides whether idle capacity is released. This source supplies the *measurement* that note lacks: it distinguishes "costly to keep available" from "costly to run" (**Claims 4–6** here) and gives a 2×2 diagnostic for deciding whether to consolidate or right-size (**Claim 13**). Together they close the loop from "idle GPUs are invisible" to "here is the cost basis and the action." That note's **Claim 11** (`maxReplicaCount` as a cost guard) is the replica-level analogue of allocation cost here.

- **Extends**: `source-notes/blog-cncf-goodput-more-than-throughput-llm-serving.md` — that note's **Claim 1** defines goodput as requests/sec meeting both TTFT and TPOT, and **Claim 4** explains that TTFT comes from prefill while TPOT comes from the shared decode step. This source adds the cost dimension: input/output token costs are reported separately *because* they map to prefill/decode (**Claim 11** here), and the allocation/usage split is the economic counterpart of goodput's "completed work that meets the target" framing. A serving team optimizing goodput and a FinOps team optimizing cost per token are looking at the same prefill/decode structure from two sides; cross-link them rather than re-extracting the mechanism here.

- **Extends**: `source-notes/blog-cncf-running-self-hosted-llm-kubernetes-vllm.md` — that note's **Claim 10** frames self-hosting as a cost-predictability option and **Claim 4** shows scale-to-zero preserving cached weights, which is precisely the warm-idle trade-off this source prices (**Claim 3** here). This source supplies the missing decision rule: self-hosting's apparent cost advantage depends on utilization, and the correct comparison is allocation-based cost vs the API price (**Claims 6, 8**). The two notes together answer "should we self-host?" with "at what utilization?" instead of a slogan.

- **Corroborates**: `source-notes/failure-cncf-kubeflow-cilium-60-idle-gpus.md` — that note's **Claim 3** shows the same root cause surfacing as a cost symptom only on the cloud bill, and **Claim 4** treats GPU utilization as the observable signal ("In our lab, GPU utilization went from around 40% to around 85% the moment the group was co-located."). This source agrees that idle accelerator capacity is the silent cost, and goes further: it attributes that cost to a model/namespace and splits it into allocation vs usage (**Claims 4–6, 10** here). The failure note explains *why* GPUs go idle; this note explains how to price the idleness.

- **Extends**: `source-notes/docs-litellm-cost-map-and-response-cost.md` — that note's **Claim 1** documents a per-call `response_cost` at the gateway/SDK layer, and **Claim 5** documents `input_cost_per_token` / `output_cost_per_token` in the model price map. This source is a different layer: *infrastructure* allocation on the cluster, not the provider's price list. The two are complementary, not conflicting — gateway cost answers "what did this call cost at the listed price," allocation cost answers "what did hosting this model cost us." The guide should keep the layers distinct and use the gateway figure for per-request attribution and the OpenCost figure for build-vs-buy/chargeback.

- **Extends**: `source-notes/docs-litellm-a2a-cost-tracking.md` **Claim 3** and `source-notes/docs-litellm-mcp-cost-tracking.md` **Claim 7** — both notes establish that gateway-configured per-query costs are operator-declared *prices*, not measurements of upstream consumption. This source is the measurement layer those notes lack: it derives cost from GPU allocation and vLLM token counters (**Claims 10–12** here) rather than a declared dollar figure. The contrast is the guide-relevant point: declared price is fine for chargeback, measured allocation is required for build-vs-buy.

- **Corroborates**: `source-notes/docs-google-sre-eliminating-toil.md` — that note's **Claim 5** lists "Cost Engineering/Capacity Planning" as one of six toil categories. This source is a concrete tool for converting that category from manual purchase-order/Reserved-Instance guesswork into a measured allocation-vs-usage signal (**Claims 4–8** here). It supports the toil note's argument that measurement must precede optimization, applied to AI infrastructure cost.

- **Extends**: `source-notes/blog-cncf-kepler-rearchitected-power-accuracy.md` — that note's **Claim 10** states GPU power monitoring in Kepler is experimental and explicitly seeking validation, and **Claim 11** describes the power-attribution pipeline. This source is adjacent but narrower: it attributes *dollar* cost from GPU allocation and token counters, not energy from power meters. The two should be cross-linked so the guide does not conflate cost accounting with energy accounting; the validation discipline in the Kepler note (compare against an independent meter) is exactly what the OpenCost PoC's "validated" claim does not publish.

- **Contradicts**: None. The apparent tension with `blog-cncf-running-self-hosted-llm-kubernetes-vllm.md` **Claim 10** ("self-hosting is cheaper for cost predictability at high volume") is a conditioning variable, not a disagreement: this source agrees self-hosting can be cheaper, and adds the utilization condition (~50%) under which that is true. Verified against `CONTRADICTIONS.md` (no `C-NNN` entries on inference/GPU cost) and open `contradiction`-labeled issues (none on this topic). No contradiction issue filed.

- **Novel**: First source note in the corpus on OpenCost, Kubernetes inference cost attribution, or GPU allocation economics. Specifically new: (1) the usage-vs-allocation two-cost model; (2) the cost-derived utilization identity; (3) the build-vs-buy trap and ~50% crossover rule; (4) the warm-but-idle failure mode with a cost basis; (5) the `llm_total_hourly_cost` / `llm_cost_per_million_tokens` metric and label surface; (6) input/output cost splitting tied to prefill/decode and KV-cache credits; (7) llm-d component cost via `SharedLabels`; (8) the 2×2 allocation×usage diagnostic.

## Guide Impact

- **Chapter 05 (Cost, capacity, and fallback patterns, `guide/05-llm-ops-reliability.md:970`)**: Add a subsection "Inference cost attribution: usage-based vs allocation-based." State the two definitions and the utilization identity [Claims 4–7], then the build-vs-buy rule: compare allocation-based cost at the measured utilization against the API price, never usage-based cost [Claim 8]. Include the warm-but-idle failure mode and the ~95% example as an illustration, not a benchmark [Claim 3]. Present the 2×2 matrix as a triage table with an explicit "relative to what baseline" caveat [Claim 13]. Pair it with the existing routing-as-cost-decision material [Claim 9; `guide/05-llm-ops-reliability.md:1028`].

- **Chapter 05 (Routing decisions are cost decisions, `guide/05-llm-ops-reliability.md:1028`)**: Add that routing, model sharing, and traffic consolidation are *utilization* levers that lower allocation cost per token [Claim 9], and that the gateway-level cost figure and the infrastructure allocation figure are different layers — use the former for per-request attribution and the latter for build-vs-buy/chargeback [Claim 10; cross-ref `docs-litellm-cost-map-and-response-cost.md` Claim 1]. Flag the future smart-router idea as unshipped and note the routing↔utilization feedback loop [Claim 15].

- **Chapter 02 (Observability → SLI measurement design, `guide/02-observability.md:227`)**: Add the inference cost metric surface: `llm_total_hourly_cost`, `llm_cost_per_million_tokens`, labels `model_name` / `model_version` / `namespace` / `cost_basis` / `workload_type` [Claim 10]. Require `cost_basis` to be explicit in dashboards so usage and allocation figures are never compared by accident. Add the input/output split and KV-cache credit as the cost counterpart of prefill/decode [Claim 11], and the `SharedLabels` pattern for shared gateway/scheduler/cache cost [Claim 12]. Note that `workload_type` is currently always "inference" and is not yet a useful dimension.

- **Chapter 00 (Feasibility study before scale, `guide/00-principles.md:73`)**: Add a build-vs-buy decision rule: before scaling a self-hosted inference deployment, compute allocation-based cost per million tokens at the expected utilization and compare it to the API price [Claims 6, 8]. The feasibility question "can we do this at scale?" now has a cost form: "at what utilization does self-hosting beat the API?" [Claim 7]. Mark the ~50% crossover as an example to recompute, not a universal threshold [Claim 8].

- **Chapter 04 (Oncall and toil → cost-anomaly runbook)**: Use the 2×2 matrix as the first triage step when an AI bill spikes: high allocation/low usage points to a utilization problem (consolidate/share), high allocation/high usage to model choice, low allocation/high usage to model size/quantization/hardware fit, low/low to a well-sized deployment [Claim 13]. Pair with the Kubeflow idle-GPU failure note for the "why did utilization drop" branch [cross-ref `failure-cncf-kubeflow-cilium-60-idle-gpus.md` Claims 3–4].

## Extraction Notes

- Read the full article (single page). Links to OpenCost, llm-d, and the CNCF project pages were not deep-read; the note's claims are scoped to what this post states, and those links are background rather than evidence. No paywall; fully readable.
- Quotes were copied character-for-character from the rendered page, including the curly apostrophes/quotes, the unspaced em dash in "costs—they see," and the spaced em dash in "hardware—this distinction." Where the source used Markdown bold inside a sentence (`**Allocation-based cost per model**`, `** This feature is available in OpenCost 1.121.0!**`), I quoted only the contiguous plain-text fragment so the quoted string matches the page's text rather than its markup. No quote splices non-adjacent sentences.
- The metrics table and the 2×2 matrix render as HTML tables on the page; I reproduced their cell text exactly in Markdown tables and noted the formatting conversion. The source table has a third column for the metric table in the raw HTML ("Metric / What it measures"), reproduced as shown.
- `confidence_overall: emerging` — the two-cost model, the utilization identity, and the label/metric surface are concrete and shipped in OpenCost 1.121.0, but the only evidence is the authors' own PoC ("validated" with no published method, data, or ground-truth reconciliation), the dollar figures are illustrative, the ~50% crossover is a rule of thumb, and several operational features (UI integration, idle-GPU detection, optimization-savings estimation) are explicitly future work. Do not promote the build-vs-buy threshold or the 95% idle figure to settled.
- `miner-related-notes.md` candidates (10), each cited or explicitly dismissed per MINER.md §4:
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed; retail/gaming SLO granularity, no inference cost or GPU attribution.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — dismissed; imperative vs declarative change workflows, unrelated.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — dismissed; multi-agent security platform deployment, no cost accounting.
  - `docs-google-sre-on-call.md` — dismissed; on-call pager load and alerting, unrelated.
  - `docs-litellm-anthropic-advisor-tool.md` — dismissed; within-request advisor model composition, no infrastructure cost attribution.
  - `docs-litellm-batches-api.md` — dismissed; batch rate-limiting surface, different layer and topic.
  - `docs-litellm-creating-adapters.md` — dismissed; format-translation adapters, unrelated.
  - `docs-google-sre-eliminating-toil.md` — **cited** (Corroborates; Claim 5 names Cost Engineering/Capacity Planning as a toil category).
  - `docs-google-sre-reliable-product-launches.md` — dismissed; launch coordination/checklists, unrelated.
  - `docs-google-sre-prodcast-03-01.md` — dismissed; SRE methodology/organizational influence, unrelated.
- Additional notes found by searching `source-notes/` (beyond the candidates): `blog-cncf-gpu-autoscaling-keda-external-scaler.md`, `blog-cncf-goodput-more-than-throughput-llm-serving.md`, `blog-cncf-running-self-hosted-llm-kubernetes-vllm.md`, `failure-cncf-kubeflow-cilium-60-idle-gpus.md`, `docs-litellm-cost-map-and-response-cost.md`, `docs-litellm-a2a-cost-tracking.md`, `docs-litellm-mcp-cost-tracking.md`, `blog-cncf-kepler-rearchitected-power-accuracy.md`.
- Cross-reference claim numbers were re-read and verified against each cited note before writing (MINER.md §4b). No contradiction found; no contradiction issue filed. The candidates file `miner-related-notes.md` was read but not committed.
