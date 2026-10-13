---
source_url: https://www.cncf.io/blog/2026/07/20/why-goodput-matters-more-than-throughput-for-llm-serving
source_type: blog-post
title: "Why goodput matters more than throughput for LLM serving"
author: "Graziano Casto (Akamas)"
date_published: 2026-07-20
date_extracted: 2026-10-13
last_checked: 2026-10-13
status: current
confidence_overall: emerging
issue: "#1702"
---

# Why goodput matters more than throughput for LLM serving

> A CNCF Member Post (vendor-authored by Akamas) that reframes LLM inference
> capacity around **goodput** — completed requests/sec that also meet both
> TTFT *and* TPOT latency targets — and demonstrates the mechanistic trap
> behind the framing: a tuning objective that constrains only TTFT
> (`avg TTFT ≤ 1.5 s`) let one vLLM config deliver ~50% more combined token
> throughput at ~10x worse p95 TPOT, because TTFT is bounded by prefill while
> TPOT is set by the decode step that every in-flight request shares.

## Source Context

- **Type**: blog-post (CNCF Member Post; CNCF highlights Kubernetes and
  Prometheus). Author is a practitioner at **Akamas**, a vendor of automated
  Kubernetes/configuration tuning — so the closing recommendation ("an
  automated, data-driven search") is product-aligned even though the harness,
  knobs, and measured latencies read as hands-on.
- **Author credibility**: Graziano Casto, Akamas. The study is reproducible in
  principle — public harness at `github.com/graz-dev/vllm-benchmark`, named
  tools (vLLM, GuideLLM load generator, Prometheus, Grafana, NVIDIA DCGM
  exporter), explicit knob values, and measured TTFT/TPOT/throughput — but it
  is self-reported, single-GPU, synthetic-load, and never independently
  replicated. The vendor incentive is real and recorded below; the mechanistic
  finding (one-sided latency constraints hide regressions on the unconstrained
  dimension) does not depend on the vendor's product.
- **Scope**: One `Qwen2.5-7B` on a single NVIDIA A10G (24 GB) in EKS, served by
  vLLM, driven by GuideLLM, observed via Prometheus/Grafana + DCGM. Three
  vLLM knobs varied (`gpu_memory_utilization`, `max_num_batched_tokens`,
  `max_num_seqs`) across three workload shapes (chatbot, reasoning, agentic)
  and two load modes (rate sweep vs saturation/throughput run). Does **not**
  cover autoscaling, multi-node serving, cost, or production-scale GPU
  hardware — the author states the GPU is deliberately cheap and the absolute
  numbers are modest by design.

## Extracted Claims

### Claim 1: Goodput — completed requests per second that *also* meet latency targets — is the capacity number that captures the user's experience; raw throughput counts requests a late response already failed
- **Evidence**: The article's central definition, plus the restaurant-kitchen analogy it uses to distinguish the two.
- **Confidence**: emerging (the construct is well known in queuing/serving literature — the author links DistServe — and the argument is sound; the specific framing is the author's)
- **Quote**: "The definition is refreshingly plain: it is the number of completed requests per second that also meet your latency targets."
- **Quote**: "A request that finishes but blows past either target is a plate that left the kitchen cold. It still counts toward throughput but it does not count toward goodput."
- **Our assessment**: Buy the construct and promote it to the guide's serving-capacity material. It is the serving-layer instance of the corpus's existing principle that "your users, not your monitoring, decide your reliability" (`docs-google-sre-reaching-beyond-walls`, Claim 2): a throughput figure counts requests the user already gave up on. The two target dimensions are named explicitly in the same passage (Claim 2).

### Claim 2: For LLM serving the two latency targets goodput must satisfy are TTFT (wait before anything appears) and TPOT (pace of the streaming answer) — and throughput alone "can keep rising while your service quietly gets worse"
- **Evidence**: The definition passage names TTFT and TPOT; the opening paragraph states the throughput-alone failure independent of the numbers.
- **Confidence**: emerging (conceptual, but consistent with streaming-service reality; the dichotomy is not itself measured)
- **Quote**: "For LLM serving those targets are usually time to first token (TTFT), the wait before anything appears on screen, and time per output token (TPOT), the pace at which the rest of the answer streams out."
- **Quote**: "this number, on its own, can keep rising while your service quietly gets worse."
- **Our assessment**: This is the definitional core. TTFT and TPOT are **two distinct SLIs**, not one "latency" — a serving team that targets a single latency number has already chosen which half of the user experience to ignore. Directly extends the corpus's two-SLI framing (Claim 4 of `docs-google-sre-prodcast-04-05-furino-slos`: "did we give the users what they want?" and "did it happen fast enough?") by showing that "fast enough" for a streaming LLM is itself two-dimensional.

### Claim 3: In the chatbot study, constraining only `avg TTFT ≤ 1.5 s` produced ~50% more combined token throughput at ~10x worse p95 TPOT — the unconstrained target absorbed the entire cost
- **Evidence**: The chatbot study objective ("maximize combined token throughput, `prefill_token_throughput + decode_token_throughput`, under one constraint: average TTFT had to stay at or below 1.5 seconds"), the Exp 1 vs Exp 20 results (TTFT 1395 ms vs 1403 ms; prefill 1925 vs 2934 tok/s; decode 478 vs 690 tok/s; p95 TPOT ~50 ms vs ~494 ms), and the explicit sentence naming where the bill landed.
- **Confidence**: emerging (single-GPU, synthetic-load, self-reported; the *shape* is the transferable claim, not the absolute numbers)
- **Quote**: "Exp 20 wins that squeeze by a wide margin, with about 50 percent more combined throughput than Exp 1."
- **Quote**: "That extra throughput is not free, and the bill shows up somewhere I did not constrain. Exp 1's p95 TPOT sits at about 50 milliseconds. Exp 20's sits at about 494 milliseconds, nearly ten times higher."
- **Our assessment**: This is the load-bearing experiment and the Prospector's primary target. The two configs sit at nearly identical TTFT (just under the ceiling), so a single-constraint search has no reason to prefer Exp 1 — yet Exp 20 is ~10x worse on the metric nobody constrained. Treat the causal direction as well-supported and the magnitudes as indicative: a single A10G is not production-representative, but the trade-off shape is hardware-agnostic (see Claim 7's author caveat).

### Claim 4: The two latencies move in opposite directions because they come from different stages — TTFT from prefill, TPOT from the decode step where vLLM advances every active request one token at a time, so packing more throughput per step lengthens every request's inter-token gap
- **Evidence**: The mechanism paragraph tying each metric to a serving stage and explaining the batch-step economics; reinforced by the author's "one course to every table each round" analogy.
- **Confidence**: settled (this is vLLM's continuous-batching decode behavior; the mechanism is architectural, not an empirical claim)
- **Quote**: "TTFT comes out of the prefill stage, where the model reads your prompt, and bounding it directly is what keeps both configs near the same 1.4 second mark. Every token after that comes from the decode stage, where vLLM advances all the active requests at once, one token to each per step. Pushing more combined throughput means packing more work into each of those steps, and a fuller step takes longer to run, so every request gets its next token a little later."
- **Our assessment**: The mechanism is the guide-worthy content: because decode is a *shared* step across all in-flight requests, per-step throughput and per-request inter-token latency are coupled by construction. That is why a one-sided TTFT objective silently degrades TPOT — the search spends a budget on prefill scheduling while the decode loop pays for it. Grade the *interpretation* settled, the specific config values emerging.

### Claim 5: Two configs can tie on requests/sec while differing sharply on p95 TPOT — the agentic study's two best configs ran 6.20 vs 6.11 req/s yet differed by ~220 ms on p95 TPOT (682 vs 902 ms)
- **Evidence**: The agentic study paragraph stating the near-tie on req/s and the p95 TPOT gap.
- **Confidence**: emerging (saturation run, self-reported; a single pair of configs, not a distribution)
- **Quote**: "In the agentic study, the two best configs I found were nearly tied on requests per second, 6.20 against 6.11, yet their p95 TPOT differed by about 220 milliseconds, 682 against 902."
- **Our assessment**: The cleanest counter-example to "pick the fastest config." Throughput is a *lossy* summary: it cannot distinguish two configs whose user-visible stream pace differs by more than 30%. This is the empirical case for goodput as the selection criterion, and for per-workload TPOT SLIs.

### Claim 6: Changing the binding latency target moves the winning config — tightening the inter-token target on the reasoning workload pushed the winner to a different configuration entirely
- **Evidence**: The reasoning study paragraph (answers ~4,000 tokens, TPOT-bound) and the explicit statement that a tighter inter-token target changed the winner.
- **Confidence**: emerging (single workload, self-reported; the author does not publish the winning config names)
- **Quote**: "In the reasoning study, where each answer runs to about 4,000 tokens, the config with the best raw throughput was not the one you would want once you cared about latency: asking the same search to respect a tighter inter-token target pushed the winner to a different configuration entirely."
- **Quote**: "a throughput number with nothing else attached does not tell you which configuration to run."
- **Our assessment**: Buy the generalized conclusion. The optimal serving config is a function of the *objective*, so a config tuned against one SLO is not portable to another. This is the tuning-level analogue of the corpus's "per-backend constraints are conditioning variables" rule in Ch05, and it argues against a single "best config" in any capacity doc.

### Claim 7: The author deliberately chose a cheap single A10G and states the study's value is the *shape* of the throughput-vs-latency trade-off, not the absolute ceiling
- **Evidence**: The setup paragraph (Qwen2.5-7B, vLLM, one A10G 24 GB, EKS, GuideLLM, Prometheus/Grafana, DCGM) and the explicit caveat paragraph.
- **Confidence**: emerging (author's own scoping statement; the number set is nonetheless real and measured)
- **Quote**: "A single A10G is not the GPU you would pick for a production-grade LLM service, so the absolute numbers here will look modest next to an H100 cluster."
- **Quote**: "The point of this post is not the ceiling, it is the shape of the trade-off between throughput and latency, and that shape holds regardless of how big the GPU is."
- **Our assessment**: Carry this caveat verbatim into the guide. The single-GPU, synthetic-load, vendor-adjacent setup means the *numbers* are indicative only; the *mechanism* (Claims 3, 4) is what transfers. The public harness (`github.com/graz-dev/vllm-benchmark`) is the reproducibility hook, though it was not independently rerun for this note.

### Claim 8: Load mode matters — a **rate sweep** reads latencies while the server still keeps up, while a **saturation/throughput run** fires requests as fast as the server accepts them and cannot by itself expose SLO violations
- **Evidence**: The two-mode description of GuideLLM usage and the statement that the reasoning/agentic saturation runs carry "no TTFT constraint at all."
- **Confidence**: settled (methodological distinction; a saturated system's latency is definitionally not the compliant-latency regime)
- **Quote**: "A rate sweep ramps the request rate up gradually and lets me read latencies while the server still keeps up, so the numbers reflect real serving and not a backlog. A throughput run does the opposite, firing requests as fast as the server will take them to find the ceiling, which pushes it into saturation."
- **Quote**: "Reasoning and agentic ran a different experiment on purpose. I kept the same goal, maximizing combined prefill and decode throughput, but with no TTFT constraint at all, and I drove load with a throughput run instead of a sweep, sending requests as fast as the server would take them to find the ceiling."
- **Our assessment**: A reusable load-test-design rule that complements the corpus's existing closed-loop caveat. `docs-litellm-benchmarks` Claim 9 warns that a closed-loop client measures its own queueing; this adds that a *saturation* run measures the server's ceiling, not its SLO compliance — only a rate sweep (or an explicit SLO-constrained run) can show whether requests met their latency targets. The author correctly tags the reasoning/agentic latency figures as unconstrained, so they must not be read as SLO-compliant evidence.

### Claim 9: A live streaming metric jitters, so a config should be scored from a run of consecutive *settled* samples — the author uses eight consecutive data points after prefill throughput settles, not any single sample
- **Evidence**: The explicit windowing rule stated in the chatbot-study setup and explained with the jitter rationale.
- **Confidence**: settled (a sound, general measurement-design rule; the specific N=8 is the author's choice)
- **Quote**: "I also added a windowing rule, scoring each config from a stretch of eight consecutive data points where prefill throughput had settled down rather than from any single sample."
- **Quote**: "Requiring eight steady points in a row is an easy way to score the system's real running rate instead of a blip."
- **Our assessment**: The jitter-suppression rule is directly applicable to the guide's measurement methodology (Ch05's "metrics without a unit are noise"). It also corroborates the existing corpus claim that *variance* is a first-class reliability property (`docs-google-sre-prodcast-01-04-rethinking-slos` Claim 16: a lower-variance service with the same mean is perceived as more reliable). The exact N=8 is anecdotal, but "score a settled window, not a peak" should be stated as a rule.

### Claim 10: The workload shape decides which latency target binds — chatbot (~485/121 tokens) hangs on tight TTFT, reasoning (~400/4000) on TPOT with TTFT loose, agentic (~512/128) on per-call TTFT that accumulates
- **Evidence**: The article's workload table mapping each traffic shape to prompt/output token counts and the SLO it hangs on.
- **Confidence**: emerging (illustrative categories, not measured distributions; token counts are the author's synthetic profiles)
- **Quote**: "I ran the same setup against three kinds of traffic because the shape of the traffic decides which latency target actually bites."
- **Our assessment**: Adopt the "a latency target without a workload shape is unbound" generalization. The three shapes (short-in/short-out chat, short-in/long-out reasoning, many-chained-short-call agentic) are a useful taxonomy for the guide's LLM-serving SLO section. Treat the exact token counts as illustrative.

### Claim 11: The best config is not stable — traffic, prompts, and models all change over time, so the tuning search has to re-run; and the tuning space contains sharp cliffs (a nearby config in the reasoning runs "failed outright")
- **Evidence**: The third lesson and the "small cliffs" sentence in the second lesson.
- **Confidence**: emerging (author's practical observation; no drift-rate measurements)
- **Quote**: "Third, none of this stays put. Traffic, prompts, and models all change over time, and the best config moves with them so the search has to run again, not once."
- **Quote**: "In my reasoning runs, two settings that looked almost the same ended up far apart and one nearby setting failed outright."
- **Our assessment**: Reframes serving-knob tuning as a *recurring operational process*, not a one-time setting — the process-management analogue of the corpus's "a canary is a process, not a traffic fraction." The "sharp cliffs / nearby config failed outright" observation is anecdotal but operationally important: hand tuning stops at the first config that looks good and may sit one step from a discontinuity.

### Claim 12 (vendor-aligned): The reliable way through the tuning space is "an automated, data-driven search that tries many configs against your real targets"
- **Evidence**: The second lesson's recommendation; the article does not benchmark any automated search against manual tuning.
- **Confidence**: anecdotal (recommendation stated, not tested; the author works for Akamas, whose product is automated configuration tuning)
- **Quote**: "The reliable way through it is an automated, data-driven search that tries many configs against your real targets rather than a few hand-picked guesses."
- **Our assessment**: Do not lift as a demonstrated finding. The premise (hand tuning stops early in a cliffy space) is plausible and partly supported by Claim 11, but the conclusion funnels into the vendor's product category. Record it as the author's vendor-aligned recommendation; the transferable part is "tune against your real targets, not raw throughput," which is really Claim 10/13.

### Claim 13: The same trade-off lives in the layers held fixed (GPU settings, runtime, scheduling), and the largest gains come from tuning the whole stack together because the layers interact
- **Evidence**: The "fourth point" paragraph, explicitly flagged by the author as not directly tested.
- **Confidence**: anecdotal (author explicitly says the study did not test it)
- **Quote**: "There is a fourth point worth making even though my study did not test it directly. I changed only three serving knobs and the gap was already this wide."
- **Quote**: "The same trade-off lives in the layers I held fixed too, in the GPU settings, the runtime, and the scheduling, and the largest gains tend to come from tuning the whole stack together rather than one layer at a time since the layers interact."
- **Our assessment**: Keep as a hypothesis, not a finding — the author flags it as untested. It does align with the guide's whole-system-champion principle (Ch00: "Complexity is an externality"), so it is worth a one-line cross-link, but it should not be graded as evidence.

### Claim 14: The concrete deliverable is a reproducible public harness — Qwen2.5-7B + vLLM + GuideLLM + Prometheus/Grafana + DCGM on EKS, with Kubernetes manifests — and the practical instruction to set TTFT/TPOT targets first, then maximize throughput subject to them
- **Evidence**: The setup paragraph, the "one honest note before the numbers," and the closing "practical move" paragraph pointing at `github.com/graz-dev/vllm-benchmark`.
- **Confidence**: emerging (the harness is public; the note did not clone or rerun it)
- **Quote**: "Set your TTFT and TPOT targets first, then look for the config that gives you the most throughput while still meeting them instead of chasing throughput on its own. You will often ship a smaller requests-per-second number and a clearly better service, the trade your users would make every time."
- **Our assessment**: This is the actionable statement of the whole source — define the SLO first, then *maximize subject to it* (goodput), rather than maximize throughput and hope latency stays acceptable. The harness is the reproducibility hook; a Repo Scout pass on `github.com/graz-dev/vllm-benchmark` may be worth filing separately.

## Concrete Artifacts

### Workload shapes and the latency target each one binds (verbatim table)

```
Workload    Prompt / Output (tokens)   What the SLO hangs on
Chatbot     ~485 / 121                 tight TTFT, medium TPOT
Reasoning   ~400 / 4000                TPOT, with TTFT loose
Agentic     ~512 / 128                 per-call TTFT that adds up
```

Attribution: https://www.cncf.io/blog/2026/07/20/why-goodput-matters-more-than-throughput-for-llm-serving, "What the studies show."

### Chatbot main-example configs (verbatim table)

```
Config   gpu_memory_utilization   max_num_batched_tokens   max_num_seqs   TTFT avg   Prefill tput   Decode tput
Exp 1    0.89                      4160                     212            1395 ms    1925 tok/s     478 tok/s
Exp 20   0.87                      2150                     271            1403 ms    2934 tok/s     690 tok/s
```

Attribution: same page, same section. Exp 1 p95 TPOT ≈ 50 ms; Exp 20 p95 TPOT ≈ 494 ms (stated in the following paragraph, not in the table).

### Observation and load-mode description (verbatim)

```
A rate sweep ramps the request rate up gradually and lets me read latencies
while the server still keeps up, so the numbers reflect real serving and not
a backlog. A throughput run does the opposite, firing requests as fast as the
server will take them to find the ceiling, which pushes it into saturation.
```

Attribution: same page, "The setup, and how I drove load."

### Toolchain and reproduction pointer (verbatim)

```
Everything here runs on parts you probably already have. I served Qwen2.5-7B
with vLLM on a single NVIDIA A10G with 24 GB of memory inside an EKS cluster,
drove load with GuideLLM, and watched the system through Prometheus and Grafana
with GPU level metrics coming from NVIDIA's DCGM exporter.
```

Harness: `https://github.com/graz-dev/vllm-benchmark` (public; not cloned or rerun for this note).

## Cross-References

- **Corroborates**:
  - `docs-google-sre-reaching-beyond-walls` — **Claim 2** ("Your users, not your monitoring, decide your reliability — the only reliability measure that matters is the user's experienced reliability"). Goodput (Claim 1 here) is the serving-layer operationalization of that principle: throughput counts requests that already failed the user's latency expectation, so it is precisely a provider-side metric standing in for a user-experienced one. Strong thematic corroboration.
  - `docs-google-sre-prodcast-04-05-furino-slos` — **Claim 4** ("There are really only two SLIs — 'did we give the users what they want?' and 'did it happen fast enough?' — making availability and latency the entry-level SLOs"). This source extends the "fast enough" SLI into two distinct streaming dimensions (TTFT and TPOT, Claim 2 here) and supplies the failure mode when only one is constrained (Claim 3). Corroborates the two-SLI framing; adds the streaming decomposition.
  - `docs-google-sre-slo-engineering-case-studies` — **Claim 10** ("THD's latency SLOs required percentiles over arithmetic averages"). This source's use of **p95** TPOT (not average) to expose the Exp 1 vs Exp 20 divergence (Claim 3) is an independent, workload-specific instance of the same percentile-over-average rule.
  - `docs-google-sre-prodcast-01-04-rethinking-slos` — **Claim 16** (reliability as a stationary distribution; "variance is a core property that should be taken 'more seriously'; a lower-variance service with the same mean is perceived as more reliable"). The settle-window scoring rule (Claim 9 here) is a concrete measurement procedure for exactly that variance concern.

- **Contradicts**: None. No existing note claims goodput, TTFT/TPOT trade-offs, or vLLM serving-knob tuning. The apparent tension with raw-throughput capacity sources is scope-conditioned, not a disagreement: `docs-litellm-benchmarks` measures *gateway* capacity with a mock model, while this measures *inference-server* capacity — different layers, and the page itself flags that its saturation numbers are unconstrained. Verified against `CONTRADICTIONS.md` (no open `C-NNN` entries) and open `contradiction`-labeled issues (none on LLM serving latency/SLO). No contradiction issue filed.

- **Extends**:
  - `docs-litellm-benchmarks` — **Claim 9** ("Closed-loop load tests measure the client's queueing, not the gateway … the same deployment, at the same RPS, reports roughly 8x the latency purely because the client queued 8x as much work into it"). This source adds the complementary **rate-sweep vs saturation-run** distinction (Claim 8 here): the LiteLLM note says a closed-loop client distorts *reported latency*; this note says a saturation-only run measures the *ceiling* and cannot show SLO compliance. Together they define the load modes that are and are not valid for capacity claims. (This note's Claim 8 and the LiteLLM note's Claim 5 also share the client-vs-server vantage-point discipline.)
  - `blog-cncf-running-self-hosted-llm-kubernetes-vllm` — **Claim 2** ("`--gpu-memory-utilization` governs how aggressively vLLM reserves memory … its 92% default caused startup failures … setting it to `0.80` provided enough headroom"). Same CNCF blog, same vLLM engine, and the same `gpu_memory_utilization` knob — but a different operational use: that note tunes it for *startup headroom* on a CPU-only lab, this note varies it (0.89 vs 0.87) as one of three *throughput/latency* tuning knobs. Cross-link them; do not re-extract the flag's meaning here.
  - `docs-google-sre-handling-overload` — **Claim 10** ("a great source of load that you can shed cheaply is requests that are exceeding their response deadlines") and **Claim 4** ("Autoscaling should trigger before load shedding kicks in"). The saturation-run finding (Claim 8 here) and the goodput definition (Claim 1) supply the serving-side *reason* to shed/cancel a request whose TPOT has blown its target — the request is already a goodput loss despite consuming GPU. Related axis: overload management for inference, not corroboration of the load-shedding mechanics.

- **Novel**: First source note in the corpus to introduce:
  1. **Goodput as an LLM-serving SLI** — completed requests/sec meeting *both* TTFT and TPOT targets. No existing note (269 checked) mentions goodput, TTFT, or TPOT.
  2. **The TTFT-vs-TPOT trade-off mechanism** — a one-sided prefill/latency constraint silently degrading the shared decode step (Claims 3, 4).
  3. **Rate-sweep vs saturation-run** as distinct (and non-interchangeable) capacity-load modes (Claim 8).
  4. **Workload-shape-dependent binding latency targets** — chatbot/reasoning/agentic each hang on a different dimension (Claim 10).
  5. **Settled-window scoring** (eight consecutive settled points) as the jitter-suppression rule for serving benchmarks (Claim 9).
  6. **vLLM serving-knob tuning** (`gpu_memory_utilization`, `max_num_batched_tokens`, `max_num_seqs`) as the inference-server capacity surface (Claim 14).

## Guide Impact

- **Chapter 05 (Evaluation and measurement methodology → "Metrics without a unit are noise", guide/05-llm-ops-reliability.md:388)**: Add goodput as the unit for serving capacity. State the rule verbatim from this source: a throughput number with no co-stated latency SLO is not a reliability signal [source: blog-cncf-goodput-more-than-throughput-llm-serving, Claim 1, Claim 10]. Add the settled-window scoring rule — score a config from a run of consecutive settled samples, not a single peak — as the second concrete instance alongside the existing ASR unit rule [Claim 9].

- **Chapter 05 (SLO programs for LLM services, guide/05-llm-ops-reliability.md:785)**: Add a "what goodput means for a streaming LLM service" subsection: the SLI is requests/sec that meet *both* TTFT and TPOT targets, because a single-sided latency objective hides regressions on the unconstrained dimension [Claim 2, Claim 3, Claim 4]. Add the mechanism in one paragraph (TTFT = prefill; TPOT = shared decode step) so the failure mode is legible, and state that changing the binding target changes the optimal config [Claim 6].

- **Chapter 05 (Cost, capacity, and fallback patterns → capacity, guide/05-llm-ops-reliability.md:970)**: Add self-hosted inference-server tuning to the capacity material: the three vLLM knobs that trade throughput against latency (`gpu_memory_utilization`, `max_num_batched_tokens`, `max_num_seqs`) [Claim 14]; treat the tuned config as a **recurring process, not a one-time setting**, because traffic/prompts/models drift and the space has cliffs [Claim 11]. Carry the source's own scope caveat [Claim 7] and mark the automated-search recommendation as vendor-aligned [Claim 12].

- **Chapter 02 (SLI measurement design, guide/02-observability.md:227)**: Add that streaming-LLM latency is **two** SLIs (TTFT and TPOT), each measured as a percentile, and that which one binds depends on workload shape [Claim 2, Claim 9, Claim 10]. This is a direct extension of the existing "THD: percentiles, not averages" rule [source: docs-google-sre-slo-engineering-case-studies, Claim 10].

- **Chapter 00 (Your users, not your monitoring, decide your reliability, guide/00-principles.md:41)**: Add one line: for LLM serving, the user-experienced capacity metric is **goodput**, not throughput — a request that finished after its latency target is a failure the throughput number counts as a success [Claim 1].

## Extraction Notes

- Deep-read of the full CNCF Member Post (single page). No paywall; fully readable. All quotes copied character-for-character from the rendered page. The page's raw-metric figures are images (`image-13.png`, `image-15.png`, `image-16.png`) and were not extractable as text; the numeric results reproduced here are the ones stated in the article's prose and tables.
- The page's markdown renders `gpu_memory_utilization` and `max_num_seqs` inside slightly garbled inline-code spans; the artifact tables reproduce the *values* character-for-character and the knob names as the article's own prose spells them. No substantive content was altered.
- **Vendor caveat carried explicitly**: the author works for Akamas (automated configuration tuning) and the closing recommendation is to adopt "an automated, data-driven search" — the product category the author sells. Claims 12 and 13 are graded `anecdotal` and flagged; the mechanistic claims (3, 4) are graded on their own architectural merit and the author's stated single-GPU/synthetic-load scope (Claim 7).
- `confidence_overall: emerging` — the mechanism and the measurement rules are sound and transferable, but every number is self-reported, single-A10G, synthetic-load, never independently replicated, and the source is vendor-adjacent. No claim was promoted to `settled` except the architectural decode/prefill mechanism (Claim 4) and the load-mode/measurement-design rules (Claims 8, 9), which do not depend on the numbers.
- **miner-related-notes.md candidates (10) evaluated**:
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — **cited** (Corroborates, Claim 4: two-SLI framing).
  - `docs-google-sre-slo-engineering-case-studies.md` — **cited** (Corroborates, Claim 10: percentiles over averages).
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — SLOs in retail/gaming; no inference-serving or latency-dimension content.
  - `docs-google-sre-eliminating-toil.md` — toil definition/measurement; unrelated.
  - `docs-litellm-batches-api.md` — LiteLLM batch rate-limiting surface; unrelated to inference-server tuning.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative vs declarative config; unrelated.
  - `docs-google-sre-reliable-product-launches.md` — launch checklists; unrelated.
  - `docs-google-sre-on-call.md` — on-call/page-load; unrelated.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — incident-response tooling; unrelated.
  - `docs-google-sre-prodcast-03-09-profiling-data.md` — profiling/observability data types; adjacent observability theme but no inference-serving, goodput, or latency-target content.
- **Cross-reference verification (§4b)**: every cited claim was re-read in its source note and its number confirmed before writing — `docs-google-sre-reaching-beyond-walls` Claim 2; `docs-google-sre-prodcast-04-05-furino-slos` Claim 4; `docs-google-sre-slo-engineering-case-studies` Claim 10; `docs-google-sre-prodcast-01-04-rethinking-slos` Claim 16; `docs-litellm-benchmarks` Claim 5, Claim 9; `blog-cncf-running-self-hosted-llm-kubernetes-vllm` Claim 2; `docs-google-sre-handling-overload` Claim 4, Claim 10. No fabricated claim numbers or quotes. The two cited-by-inspection notes (`docs-google-sre-handling-overload`, `docs-litellm-benchmarks`) are the Prospector-flagged overlaps; the rest were found by searching `source-notes/` directly.
- No contradiction issue filed (see **Contradicts**). The candidates file `miner-related-notes.md` was read but not committed.
