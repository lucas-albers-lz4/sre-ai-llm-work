---
source_url: https://www.cncf.io/blog/2026/06/30/kepler-re-architected-improved-power-accuracy-and-a-community-call-to-action
source_type: blog-post
title: "Kepler, re-architected: Improved power accuracy and a community call to action!"
author: Niki Manoledaki (Grafana Labs), Sunyanan Choochotkaew (IBM)
date_published: 2026-06-30
date_extracted: 2026-10-17
last_checked: 2026-10-17
status: current
confidence_overall: emerging
issue: "#1636"
---

# Kepler, re-architected: Improved power accuracy and a community call to action!

> A maintainer account of rewriting the Kepler power-attribution exporter: dropping eBPF for read-only `/proc`+`/sys` to remove CAP_BPF/CAP_SYSADMIN, renaming the exported Prometheus series, discovering hardware power-meter topology at runtime, and validating the new design against IPMI BMC ground truth with a pre-stated expected ratio.

## Source Context

- **Type**: blog-post (CNCF Ambassador Post — open-source project write-up, no vendor pitch)
- **Author credibility**: Niki Manoledaki (Grafana Labs) and Sunyanan Choochotkaew (IBM) are CNCF Ambassadors and Kepler maintainers; the post credits four additional Kepler contributors. Experiments are attributed to named maintainers (Laura Llinares at CERN, Vimal Kumar at Red Hat) with linked Grafana dashboard JSON in the Kepler repo. This is a first-party re-architecture narrative — the accuracy claims are self-reported by the team that did the rewrite, with methodology and dashboards shown but raw measurement data not published in the post.
- **Scope**: Covers the Kepler rewrite (architecture change, metric rename, runtime topology discovery) and two accuracy experiments (old-vs-new vs IPMI; stress-ng attribution gap). Does NOT cover SLOs, incidents, or on-call practice; the AI/LLM angle is adjacent (IEA energy-growth citation, experimental GPU power-monitoring flag). Roughly half the post is a community call-to-action (GPU testers, VM model retraining, data-accuracy volunteers) — mined here only where it states product limitations or feature status, not for recruitment content.

## Extracted Claims

### Claim 1: The old eBPF architecture required CAP_BPF and CAP_SYSADMIN — named as a production adoption blocker — and the rewrite replaced it with read-only `/proc` and `/sys` access deployable via a single Helm chart
- **Evidence**: Stated rationale section naming the privilege requirement as "a blocker for many production environments"; the re-architecture description of the replacement signal source and deployment path.
- **Confidence**: emerging (maintainer assertion; the capability requirement itself is architectural fact, the "blocker for many" magnitude is unsourced)
- **Quote**: "First, it required CAP_BPF and CAP_SYSADMIN privileges, which is a blocker for many production environments."
- **Quote**: "To prioritize ease of adoption and accuracy improvement, we are shifting away from eBPF and going back to basics. Our re-architected solution leverages read-only access to standard /proc and /sys. Because these are universally available on Linux systems, they require significantly lower privileges and minimal setup."
- **Our assessment**: We buy this as a concrete adoption-barrier data point: privileged kernel instrumentation can be technically correct and still undeployable in locked-down production environments (restricted PSA, security review, change-approval friction on privileged DaemonSets). The transferable rule for the guide is to weigh the deployment-permission burden of an instrumentation choice as a first-class selection criterion, not an afterthought. Note the scoping: Kepler dropped eBPF for *fine-grained utilization capture*; eBPF remains a sound choice for coarser security telemetry elsewhere in the corpus.

### Claim 2: The eBPF signal source was the majority of user-reported issues — error-prone at fine granularity and missing short-lived terminated processes, under-reporting energy footprints — and added a steep maintenance learning curve
- **Evidence**: Maintainer characterization of user-reported issue distribution and failure mode; no counts or issue-tracker links given.
- **Confidence**: anecdotal (first-party, unquantified)
- **Quote**: "Previously, Kepler relied on eBPF to capture utilization signals, which accounted for the majority of user-reported issues. At the same time, it caused missing short-live, terminated processes, leading to inaccurate, under-reported energy footprints."
- **Quote**: "Secondly, eBPF proved to be error-prone when it comes to tracking fine-grained, kernel-level processes at this level of accuracy. Data inaccuracy at this level creates a bottleneck for the power estimation models that we need to train in order to deploy Kepler on virtual machines (VMs)."
- **Quote**: "Beyond the elevated privileges and accuracy issues, the eBPF integration made the learning curve steeper. It added complex abstractions that made it difficult to extend and maintain the codebase."
- **Our assessment**: The interesting operational claim is the coupling between measurement fidelity and downstream model training: garbage utilization signals poison the power-estimation models needed for VM deployment, so an instrumentation-accuracy problem becomes a roadmap blocker. The "majority of user-reported issues" figure is unquantified maintainer recollection; treat as directional, not measured. (Note "short-live" is a typo in the source, preserved in the quote.)

### Claim 3: The rewrite renamed the exported Prometheus series — old `*_package_*` names moved behind an `old_` prefix — so the metric surface change is a breaking change for every dashboard, recording rule, and alert bound to the old names
- **Evidence**: The post's old-vs-new metric table (node-level and container-level), the experiment setup bullet defining `kepler-old` as "publishing metrics with an old_ prefix," and a linked old-vs-new Grafana dashboard JSON in the Kepler repo.
- **Confidence**: settled (the rename itself is documented and checkable; the consumer-breakage consequence is our inference, not spelled out in the post)
- **Quote**: "kepler-old: the previous version, publishing metrics with an old_ prefix."
- **Quote**: "The newer Kepler versions expose power both as a watts gauge (kepler_node_cpu_watts) and as joules counters (kepler_node_cpu_joules_total and kepler_container_cpu_joules_total)."
- **Our assessment**: This is the cleanest concrete example in the corpus of "a telemetry schema change is a breaking change for consumers, not just producers." The post shows the rename and the side-by-side validation but never warns operators that dashboards and alerts bound to `kepler_node_package_joules_total` / `kepler_container_package_joules_total` go dark on upgrade — the silent-dark-dashboard risk is ours to record. The `old_`-prefix coexistence during the experiment is itself the mitigation pattern worth generalizing: dual-publish old and new series during a transition window so consumers can migrate before the old names die.

### Claim 4: The old API exposed only joules counters requiring PromQL `rate()` to derive watts, and the old counters produced multi-kW spikes exceeding IPMI ground truth; the new version adds a native watts gauge that eliminates those spikes
- **Evidence**: The experiment-1 result paragraph and dashboard; the post states PromQL `rate()` was used in the comparison panels "so that all series share the same unit."
- **Confidence**: emerging (experiment described with dashboard images; no raw time series published)
- **Quote**: "In the Grafana dashboard panels shown below, PromQL is used to derive watts from the old joules counters using PromQL's rate() so that all series share the same unit."
- **Quote**: "The new Kepler node_cpu_watts metric tracks IPMI patterns closely and eliminates the multi-kW spikes seen with the old node_pkg_joules and full_node_joules counters that exceed the IPMI ground truth values."
- **Our assessment**: Two hygiene lessons. First, a counter-only API pushes every consumer to write the same `rate()` derivation, multiplying the places a unit mistake can live; exporting the gauge natively collapses that. Second, the failure signature — derived power readings spiking to physically impossible multi-kW values above whole-node ground truth — is exactly what an independent-meter check catches and a dashboard eyeball does not. The specific spike mechanism is not diagnosed in the post.

### Claim 5: Hardcoded hardware-topology assumptions attributed energy to a non-existent ground truth; the rewrite discovers the host's power-meter structure at runtime
- **Evidence**: The power-metrics paragraph contrasting the old hardcoded RAPL composition (core, DRAM, other) with actual hardware variety, and the runtime-discovery replacement.
- **Confidence**: emerging (mechanism stated; no measurement of mis-attribution magnitude)
- **Quote**: "For the power metrics, previously, Kepler assumed a hardcoded power structure (e.g., RAPL is composed of core, DRAM, and other). However, we found that actual hardware topologies vary significantly, meaning the old design was attributing data to a non-existent ground truth."
- **Quote**: "The re-architected Kepler dynamically discovers the host's power meter structure at runtime."
- **Our assessment**: The phrase "attributing data to a non-existent ground truth" is the post's sharpest line: the system was self-consistent against a model of the hardware that did not match the hardware. This generalizes beyond power telemetry — any exporter that encodes assumptions about underlying topology (NUMA layout, device presence, cloud-instance shapes) instead of discovering it will mis-attribute on the fleet subset where the assumption fails, and the error will be invisible in aggregate dashboards.

### Claim 6: Validation methodology — compare derived telemetry against a physically independent meter with the expected ratio stated up front, and use the independent meter as a load-shape reference under controlled increasing load
- **Evidence**: Experiment 1 (Laura Llinares, CERN): old and new Kepler deployed simultaneously on the same bare-metal node against IPMI BMC readings, with the expected Kepler/IPMI ratio and the defect criterion (spiking above ground truth) defined before the comparison.
- **Confidence**: emerging (methodology is sound and fully described; single node, self-reported)
- **Quote**: "IPMI is the full-node power draw from the BMC. It includes DRAM, fans, NICs, and PSU losses on top of CPU, so Kepler values are expected to be 40-70% of IPMI."
- **Quote**: "Since IPMI measures the whole node and Kepler measures only the CPU, we use IPMI as a load shape reference. IPMI is displayed as a background reference in the overlay panels. When a stress workload ramps up, IPMI and both Kepler versions should all rise together. A Kepler estimator that rises and falls in sync with IPMI is correctly tracking load."
- **Our assessment**: This is the transferable core of the post for the guide: validate a derived/attributed signal by (a) choosing an independent physical meter, (b) pre-stating the expected ratio and *why* it is not 1:1 (scope difference — CPU-only vs whole node), (c) ramping controlled load and checking co-movement rather than absolute plausibility. "Does the dashboard look plausible" is the failure mode this replaces. The same shape applies to LLM token-cost attribution (derived cost vs provider invoice) and GPU-utilization attribution (exporter reading vs in-band device counters).

### Claim 7: A progressive `stress-ng` experiment reported a process-power-attribution gap of essentially 0 W — node active energy minus process-distributed energy differing by only a few milliwatts
- **Evidence**: Experiment 2 (Vimal Kumar, Red Hat): progressive stress-ng workload; Grafana panels for core and package energy; delta graphs described.
- **Confidence**: emerging (quantified claim, self-reported; no raw data or pass/fail threshold published)
- **Quote**: "The second test, led by Vimal Kumar (Red Hat), shows the negligible attribution gap when comparing Node power with power derived through the process attribution model, which validates the accuracy of Kepler's new design. The system testing uses a progressive stress-ng workload. The resulting Grafana dashboard panels for core and package energy show a Process Power Attribution Gap of essentially 0 Watts."
- **Quote**: "Furthermore, the detailed delta graphs indicate that the difference between the total node active energy and the energy distributed to individual processes is minimal, fluctuating by only a few milliwatts."
- **Our assessment**: Conservation-style validation — the sum of attributed parts should equal the independently measured whole within a stated tolerance — is a stronger check than per-series plausibility, and it is cheap to run anywhere a whole-workload counter exists. The blog does not state the tolerance band or publish the series, so the "essentially 0 W" number is directional. Worth noting the scope caveat: this validates *active* CPU attribution only (see Claim 8).

### Claim 8: Known fidelity trade-off — after the rewrite, Kepler attributes only active CPU usage per workload, dropping idle power, which the authors call an oversimplification they intend to restore
- **Evidence**: Explicit limitation in the call-to-action list (item 4, "Improve Idle Power Attribution").
- **Confidence**: settled (author-stated limitation)
- **Quote**: "After the rewrite, Kepler only attributes active CPU usage per workload. However, this oversimplifies power estimation. While this was added to avoid confusion between idle and dynamic states, it should be added back and expressed better."
- **Our assessment**: A useful worked example of an observability re-architecture trading one blind spot for another — the old design missed short-lived terminated processes (Claim 2); the new one misses idle draw — with the trade stated openly rather than implied. For the guide: when an instrumentation swap changes what is *invisible*, publish the new blind spot alongside the migration notes; consumers who sized capacity on total draw will silently read low.

### Claim 9: The rewrite added integration and unit tests to 90% coverage, framed as necessary to validate the trustworthiness of the exported metrics
- **Evidence**: Closing validation paragraph.
- **Confidence**: settled (verifiable in the repo; coverage number is a claim about the project at publication time)
- **Quote**: "Last but not least, we added extensive integration and unit tests to reach 90% testing coverage. This improves the long-term maintainability and trust in results. This is key to validate the accuracy of the power metrics that Kepler exports."
- **Our assessment**: Minor but aligned with the post's theme: when the product *is* a derived number, test coverage is part of the accuracy argument, not just maintainability hygiene. The post ties tests and external ground-truth comparison as complementary trust mechanisms rather than substitutes.

### Claim 10: GPU power monitoring exists only behind an experimental flag, positioned as crucial for AI/accelerator-heavy workloads, with end-user validation explicitly sought against physical meters
- **Evidence**: Call-to-action item 1 with a link to the GPU power-monitoring design doc in the Kepler repo.
- **Confidence**: settled (feature status); the "crucial" framing is author judgment
- **Quote**: "We have an experimental flag for GPU power monitoring, which is crucial now for AI and accelerator-heavy workloads. We need end users running AI/ML workloads to test and validate Kepler's GPU power monitoring feature."
- **Our assessment**: For an LLM-serving fleet this is the only AI-adjacent item with operational substance, and its status is *experimental and unvalidated* — not something to build GPU power cost attribution on today. The methodology transfer (Claim 6/7) is the durable value: when GPU-attribution telemetry does mature, validate it against in-band device counters or external meters the same way the CPU design was validated. The IEA citation (data-center electricity projected to ~945 TWh by 2030) is context, not evidence for any operational claim.

### Claim 11: Kepler's pipeline is hardware power meters → Linux-process attribution → Pod association → Prometheus metrics; there is no easy built-in Kubernetes method to allocate power per workload
- **Evidence**: Opening problem-statement paragraphs defining the gap and the pipeline.
- **Confidence**: settled (product definition; the "no easy built-in method" gap is consistent with the absence of any power signal in core Kubernetes)
- **Quote**: "In Kubernetes clusters, there is no easy built-in method to allocate power per workload. Kepler solves this: it reads from hardware power meters, attributes this power consumption to Linux processes, associates that to Pods running in your Kubernetes cluster, and exports Prometheus metrics."
- **Our assessment**: Establishes Kepler as the attribution layer in the same Prometheus/Grafana stack an LLM-serving SRE already runs — the relevance hook for the guide is operational adjacency and the attribution-validation discipline, not energy management as a practice area.

## Concrete Artifacts

### Old → new metric name mapping (from the experiment-1 table, verbatim)

| Metric | Version |
|---|---|
| `kepler_node_package_joules_total` | old |
| `kepler_node_cpu_watts` | new |
| `kepler_container_package_joules_total` | old |
| `kepler_container_cpu_joules_total` | new |

The post also states: "Both counters increment with energy consumed by the CPU Package RAPL domain at node level." During the experiment the old version published under an `old_` prefix; the old counters were additionally derivable as watts via PromQL `rate()`.

### Experiment setup (Experiment 1, from the post's bullets, verbatim)

```
- kepler-old: the previous version, publishing metrics with an old_ prefix.
- kepler-new: the re-architected version, publishing clean metrics without prefix.
- Intelligent Power Management Interface (IPMI): hardware BMC power meter readings.
```

### Linked dashboard sources (in-article links to the Kepler repo)

- Old-vs-new accuracy overlay dashboard:
  `https://github.com/sustainable-computing-io/kepler/blob/f6e275fee21e785c6034d86043e1bbd27604ca09/compose/dev/grafana/dashboards/dev/old-vs-new-accuracy.json`
- Attribution-gap dashboard (Experiment 2):
  `https://github.com/sustainable-computing-io/kepler/blob/main/compose/dev/grafana/dashboards/dev/dashboard.json`

### Deployment surface

Kepler installs via Helm chart or the Kepler Operator; the post points to the Kepler GitHub quick-start and the power-attribution design docs at `https://sustainable-computing.io/kepler/usage/power-attribution/`. No code snippets or config files appear in the post itself.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-completion-prompt-caching.md` **Claim 12** (verified) — same validation principle in a different substrate: LiteLLM's `completion_cost()` / `x-litellm-response-cost` are "map-derived estimates, so the provider invoice remains the only ground truth." This note's IPMI-vs-Kepler methodology (Claim 6) is the physical-meter instance of that rule: derived attribution gets reconciled against an independent measurement, not trusted because it renders.
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 7** (verified) — corroborates the silent-consumer-breakage family of Claim 3: a typo'd derived-metric name "resolves to `0` rather than erroring," and "the eval still completes, the gate still reports, and the arithmetic is just wrong." Metric-name bindings — whether a Prometheus series rename or a derivedMetrics reference — fail silently by default on both sides of this corpus.
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — **Cited by section name** (per MINER.md §4b rule 4; this note's headings are `Symptom`/`Root Cause`/`Lesson`, not `### Claim N`): **Symptom 2** ("Cost tracking silently returned `cost=0`") and the root cause (silent fallback to a stale local map) corroborate the Claim 3/4 theme that derived-metric pipelines degrade without any failure signal — here the derived quantity zeroed out, there the consuming dashboards go dark.
  - `source-notes/docs-google-sre-canarying-releases.md` **Claim 17** (verified) — adjacent consumer-dependence claim: "whole-service aggregates hide a small canary" and metric aggregation intervals must match evaluation windows. Complements Claim 3: the metric surface's *names and granularity* jointly determine what consumers can detect; Kepler's rename kills the binding, aggregation kills the resolution.
  - `source-notes/blog-cncf-otel-mesh-derived-metrics.md` **Claim 6** (verified) — same silent-miss family: alerting on HTTP status alone "silently misses gRPC failures" because the status travels in trailers. Different mechanism (wrong label vs renamed series), same operator lesson — verify the signal your consumer actually binds to reaches the backend.
- **Contradicts**: None identified. No existing note covers power/energy attribution, and no claim here opposes an established corpus claim. (The corpus's eBPF usage elsewhere is a scoping contrast, not a conflict — see Extends.)
- **Extends**:
  - `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` — the corpus's other eBPF data point: Falco-with-eBPF for syscall-level security interception is presented as working well. This note scopes why Kepler left eBPF (fine-grained utilization accuracy + privilege burden, Claim 1/2), not eBPF in general — together the two sources argue for matching the instrumentation mechanism to the signal's granularity and trust requirements.
  - `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md` and `source-notes/blog-cncf-4-body-problem-sre-context.md` — same publisher (CNCF blog) and, for the former, the same Prometheus/Grafana operational stack, but zero shared claims; noted so the Assayer sees they were checked, not skipped.
- **Novel**:
  - First note in the corpus on power/energy telemetry and on metric-surface renames as a consumer-breaking change with the `old_`-prefix dual-publish mitigation (Claim 3).
  - The pre-stated-expected-ratio validation methodology against a physically independent meter under a controlled load ramp (Claim 6) and the conservation-style attribution-gap check (Claim 7) — no prior note documents either pattern.
  - The least-privilege instrumentation trade (dropping CAP_BPF/CAP_SYSADMIN for read-only `/proc`+`/sys`) as an adoption-enabler case study (Claim 1), and the runtime-discovery-vs-hardcoded-topology rule (Claim 5).

## Guide Impact

- **Chapter 02 (Observability)** — three additions:
  1. Treat exported-series renames as breaking API changes: inventory dashboards, recording rules, and alerts bound to old names before an exporter upgrade; dual-publish old and new series (Kepler's `old_`-prefix pattern) through a migration window. Cite this note's Claim 3 mapping table as the worked example.
  2. Add a "validate derived metrics against independent ground truth" rule: pre-state the expected ratio and why it is not 1:1, ramp controlled load, check co-movement and conservation (Claim 6/7), instead of eyeballing dashboard plausibility. Cross-link the LiteLLM invoice-as-ground-truth note (prompt-caching Claim 12) as the cost-attribution instance.
  3. Add instrumentation-source selection criteria including deployment-permission burden: privileged kernel instrumentation (CAP_BPF/CAP_SYSADMIN, privileged DaemonSets) can be correct yet undeployable; prefer universally-available read-only sources where accuracy permits (Claim 1/2).
- **Chapter 06 (Security & Trust)**: Add the Kepler privilege-reduction as a case study where capability sprawl was eliminated without losing the needed signal — supports least-privilege guidance with a concrete rollback story (eBPF → `/proc`+`/sys`).
- **Chapter 05 (LLM Ops Reliability)** — tangential, GPU/attribution angle only: when GPU or energy cost attribution is used for LLM fleet capacity/cost decisions, its validation discipline is the invoice/physical-meter reconciliation pattern (Claims 6/7, 10); Kepler's GPU monitoring is explicitly experimental and should not be relied on. Do not add an energy-monitoring section to the guide.

## Extraction Notes

- Deep-read the full article (fetched 2026-10-17). All quotes copied character-for-character from the rendered page; the source's typo "short-live" (for short-lived, Claim 2) is preserved; curly apostrophes in "Kepler's", "host's", "rate()", "PromQL's" match the source. The call-to-action half was skipped per Prospector guidance except where it states limitations or feature status (Claims 8, 10).
- **miner-related-notes.md candidates — all 10 reviewed and dismissed** (none share claims with this source; all are lexical matches on generic SRE terms): `docs-google-sre-prodcast-03-07-retail-gaming.md` (SLO granularity, unrelated); `blog-cncf-cloud-native-agentic-ai-security-platform.md` — **the single exception, promoted to a real Extends citation** (eBPF scoping contrast, above); `docs-litellm-completion-function-call.md` (capability predicates, unrelated); `docs-google-sre-prodcast-03-11-embracing-complexity.md` (complexity theory, unrelated); `docs-google-sre-prodcast-03-13-imperative-declarative.md` (change workflows, unrelated); `docs-google-sre-on-call.md` (pager load, unrelated); `docs-google-sre-prodcast-03-06-incident-response-tooling.md` (IR tooling, unrelated); `docs-google-sre-team-lifecycles.md` (team formation, unrelated); `docs-google-sre-prodcast-03-01.md` (team rename — different sense of "renamed", unrelated); `docs-litellm-anthropic-advisor-tool.md` (advisor composition, unrelated).
- Prospector's two noted neighbors checked: `blog-cncf-4-body-problem-sre-context.md` (AI-ops context-availability argument — no shared claims) and `blog-cncf-network-boundary-ai-agents-nginx-otel.md` (agent egress boundary — same stack, no shared claims). Cited under Extends as checked-and-disjoint.
- Issue #1555 (Kepler CNCF project landing page) was a different URL rejected at pre-screen as a tool homepage — not a duplicate of this article; no note exists for it.
- No contradiction with existing notes or within the source; the old-vs-new fidelity trade (misses short-lived processes → misses idle power, Claim 8) is an author-flagged sequencing of known limitations, not an internal disagreement. No contradiction issue filed.
- Evidence ceiling: the post's quantitative claims (multi-kW spike elimination, ~0 W gap, few-milliwatt deltas, 40-70% ratio) rest on dashboard images and prose — linked dashboard JSON exists in the Kepler repo, but raw measurement series are not published. Confidence graded `emerging` overall for that reason.
