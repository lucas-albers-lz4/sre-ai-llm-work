---
source_url: https://www.cncf.io/blog/2026/06/22/telemetry-that-matters-designing-sustainable-high-impact-observability-pipelines/
source_type: blog-post
title: "Telemetry that matters: Designing sustainable, high-impact observability pipelines"
author: Diana Todea (VictoriaMetrics, DevRel Engineer; Cloud Native Days Romania organizer), Laura Luttmer (Principal Product Manager, Bindplane/Dynatrace), Antonio Jimenez Martinez (Tech Lead Software Engineer, Cisco ThousandEyes)
date_published: 2026-06-22
date_extracted: 2026-10-14
last_checked: 2026-10-14
status: current
confidence_overall: emerging
issue: "#1718"
---
# Telemetry that matters: Designing sustainable, high-impact observability pipelines

> A CNCF Community Post recapping an Observability Summit North America panel discussion on sustainable, high-impact observability pipelines. The panel emphasizes moving from "instrument everything" to intentional telemetry selection, with concrete pipeline-side reduction techniques and a reframing of observability for agentic/LLM workloads.

## Source Context

- **Type**: blog-post (CNCF Community Post, written recap of a panel at Observability Summit NA in Minneapolis)
- **Authors**: Diana Todea (DevOps Engineer/DevRel, VictoriaMetrics; Cloud Native Days Romania community organizer), Laura Luttmer (Principal Product Manager, Bindplane/Dynatrace), Antonio Jimenez Martinez (Tech Lead Software Engineer, Cisco ThousandEyes)
- **Venue**: Observability Summit North America 2026, Minneapolis — [panel "Telemetry that Matters"](https://observabilitysummitna26.sched.com/event/2HJVN/panel-telemetry-that-matters-diana-todea-victoriametrics-antonio-jimenez-martinez-cisco-thousandeyes-laura-luttmer-dynatrace)
- **Evidence quality**: Panel recap. No code examples, no collector YAML configs, no benchmarks, no before/after measurements, and no incident reports are included. There is exactly one quantitative claim ("around 50% of collected metrics are never queried or acted upon") which is attributed to an external Medium article by Dotan Horovits, not measured by the authors. All other claims are practitioner commentary, design principles, and named patterns. As such, confidence for extracted claims is capped at **emerging**.
- **Scope**: Covers the over-collection problem, observability mesh/cross-signal correlation, zero-code vs manual instrumentation trade-offs, five collector-side telemetry reduction techniques, and the shift to agentic/LLM observability (from "is it fast?" to "does it produce cost-effective, reliable, correct outcomes?").
- **Not covered**: Production cost data, specific SLO values, failure postmortems, or concrete implementation details.

## Key Takeaways

- The default "instrument everything and filter later" approach leads to wasted telemetry — "around 50% of collected metrics are never queried or acted upon" (secondhand, attributed to external source)
- Optimize in the data pipeline (Day 2), not in application code — changes don't require redeploying services
- For agentic/LLM systems, errors are often qualitative (response quality/decision quality), not deterministic technical failures; the LLM itself is rarely the sole/root cause
- Start with zero-code/auto-instrumentation to establish a baseline, then layer manual instrumentation only where business logic context is required
- Apply pipeline-side controls: smart/tail-based sampling, high-cardinality management/masking, cardinality limiters, log deduplication, and centralized infrastructure enrichment

## Extracted Claims

### Claim 1: Unchecked telemetry collection wastes resources and creates cognitive load
- **Evidence**: Panel commentary on the "instrument everything and filter it out later" baseline and its consequences (storage bloat, engineering overhead, alert noise, cognitive load during incidents). Also introduces "green observability" as an environmental concern.
- **Confidence**: emerging
- **Quote**: "industry experience routinely shows that [**around 50% of**](https://horovits.medium.com/expensive-metrics-why-your-monitoring-data-and-bill-get-out-of-hand-) **collected metrics are never queried or acted upon**. This unchecked data collection does more than just bloat storage bills; it introduces steep engineering overhead, increases alert noise, and heightens cognitive load during active incidents."
- **Our assessment**: The 50% figure is not measured by the authors — it's attributed to a third-party Medium article. The post acknowledges it's "industry experience routinely shows" the figure, but explicitly links to Horovits' post as the source. For guide purposes, this is an attributed assertion, not a validated metric; it should be treated cautiously. The broader point (excess telemetry creates overhead/noise) is reasonable even if the precise percentage is contestable.

### Claim 2: Green observability matters — telemetry waste has energy/carbon cost
- **Evidence**: Panel framing linking observability volume to environmental impact.
- **Confidence**: emerging
- **Quote**: "A critical but frequently overlooked angle of this issue is **green observability**. Every metric stored, indexed, and processed consumes real compute resources, disk storage, and energy. Reducing telemetry waste isn’t just an infrastructure cost optimization strategy, it directly minimizes the carbon and environmental footprint of our cloud-native platforms."
- **Our assessment**: This is a framing claim, not backed by measurements in the post. It's a reasonable extension of "reduce waste to reduce cost" but the environmental impact claim is asserted without supporting data. Still, it's a coherent principle that aligns with sustainability concerns in cloud-native.

### Claim 3: Observability must be treated as a day-zero design requirement
- **Evidence**: Recommendation that teams intentionally define system health and required signals before shipping.
- **Confidence**: emerging
- **Quote**: "To build sustainable and highly reliable infrastructure, observability must be treated as a day-zero system design requirement. Teams need to intentionally define what a healthy system looks like and map out exactly which signals are needed to detect structural drift before pushing code to production."
- **Our assessment**: Corroborates general SRE/observability best practices (defining SLIs/SLOs and key signals early). Not novel in principle, but reinforces intentional instrumentation over ad-hoc collection. Useful framing alongside the pipeline optimizations.

### Claim 4: During incidents, cross-signal correlation (observability mesh) reduces context-switching
- **Evidence**: Description of how metrics, traces, logs, and profiles connect; using RED metrics to isolate service before digging deeper.
- **Confidence**: emerging
- **Quote**: "Rather than treating these elements as isolated diagnostic categories, the community is shifting toward an [**observability mesh**](https://medium.com/@dianatodea/observability-is-a-mesh-not-a-braid-c3ac3ca9a305). In this interconnected web, metrics point directly to traces, traces embed relevant logs, and logs tie back into resource profiles. During an active incident, this cross-signal connection drastically reduces context-switching friction."
- **Our assessment**: The "observability mesh" terminology is introduced here (with an external link). This is a conceptual framing about signal interconnection. It overlaps with existing ideas about correlated telemetry; the key value is emphasizing cross-linking to reduce friction during incidents. No implementation specifics.

### Claim 5: Auto-instrumentation is fast but cannot see internal business logic; manual gives control but risks stalling
- **Evidence**: Trade-off table comparing zero-code/auto-instrumentation (e.g., OTel eBPF/OBI) vs manual. Specific failure modes listed for each.
- **Confidence**: emerging
- **Quote**: "Many teams attempt to launch fully manual frameworks from day one, but often stall out and lose executive backing due to slow progress and runaway costs. A practical route is to **start with zero-code auto-instrumentation first** to instantly establish a telemetry baseline, then look at the data flowing through your pipelines and fine-tune it by progressively layering in manual instrumentation where deep context is needed."
- **Our assessment**: This matches guidance seen in `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (Claim 4 in that note: "Auto-instrumentation covers LLM-layer spans, but agent-layer attributes must be hand-authored") and general OTel guidance. The "stall out and lose executive backing" is anecdotal practitioner commentary. The recommended sequencing (auto-first baseline, then layer manual) is actionable.

### Claim 6: Optimize in the pipeline (Day 2) to avoid app redeploys
- **Evidence**: Panel recommendation to move optimization to collection pipelines for agility.
- **Confidence**: emerging
- **Quote**: "Once telemetry collection is widely deployed, optimization should happen directly within your data pipelines. This allows platform teams to adapt quickly to data explosions without forcing application teams to constantly rewrite and redeploy code."
- **Our assessment**: This is a strong platform engineering principle (separate collection/config control from app code). It aligns with OpAMP-style fleet control (`blog-cncf-operating-opentelemetry-at-scale-opamp.md` carries "pipeline-side control beats per-service burden" idea) and with mesh-derived metrics work (`blog-cncf-otel-mesh-derived-metrics.md`). The "never in application code" phrasing for Day 2 optimizations is emphatic but directionally correct.

### Claim 7: Smart/tail-based sampling preserves anomalies while dropping boring traffic
- **Evidence**: Named technique as first pipeline optimization.
- **Confidence**: emerging
- **Quote**: "Move away from pure random sampling, which can accidentally drop critical error signals. Implement tail-based or pattern-based sampling to ensure you drop boring, successful requests while capturing 100% of anomalies or failures."
- **Our assessment**: This is a standard OTel Collector sampling principle (head-based vs tail-based). The claim that random sampling can drop critical error signals is accurate in general; tail-based sampling aims to make sampling decisions after seeing the full trace (including errors). This is conceptual guidance, not implementation detail.

### Claim 8: High-cardinality management — mask unique IDs, drop attributes, truncate IPs
- **Evidence**: Named technique with concrete examples of what to avoid and how to fix.
- **Confidence**: emerging
- **Quote**: "Avoid attaching highly unique attributes like user_id or request_id directly to system metrics, which can instantly trigger a dimensional explosion that breaks backend query engines. Instead, use transform processors to mask unique IDs (e.g., transforming specific URL parameters into a generic $ placeholder), drop unneeded attributes, or truncate fine-grained IPs into broader subnets."
- **Our assessment**: This directly intersects with `blog-cncf-otel-mesh-derived-metrics.md` (Claim 5 in that note discusses cardinality economics and filtering). The mesh note provides measured evidence (family-level filtering doesn't reduce label cardinality inside retained family) while this post gives the policy approach (mask/drop/truncate). They are complementary: this gives operational guidance, the mesh note gives the measured constraint. The guidance here is sound at the conceptual level.

### Claim 9: Cardinality limiters skip attributes past a uniqueness threshold
- **Evidence**: Named pipeline processor pattern.
- **Confidence**: emerging
- **Quote**: "Implement pipeline processors that actively monitor incoming attribute values. If a specific label passes a configured uniqueness threshold, the pipeline automatically skips that attribute to prevent metric performance degradation."
- **Our assessment**: This is a concrete control mechanism. Many OTel Collector distributions offer cardinality limiters (e.g., `metrics_cardinality_limit` processor behavior or third-party processors). The post describes the intent clearly; no config shown.

### Claim 10: Log deduplication collapses identical lines in a window with iteration count
- **Evidence**: Named technique for log volume control.
- **Confidence**: emerging
- **Quote**: "Use processors that identify identical log lines emitted within a small time window, collapsing them into a single record accompanied by an accurate iteration count."
- **Our assessment**: Reasonable for repetitive log spam (e.g., repeated connection errors, health check noise). This is a common log pipeline optimization. No implementation specifics.

### Claim 11: Centralized infrastructure enrichment avoids per-service overhead
- **Evidence**: Move common metadata injection to pipeline rather than per-agent/per-service.
- **Confidence**: emerging
- **Quote**: "Minimize individual agent overhead by decoupling per-service metadata collection. Instead, standardize your semantic conventions and inject common infrastructure or container orchestrator labels once centrally within the collection pipeline."
- **Our assessment**: This aligns with the "Day 2 in pipeline" principle (Claim 6). It also complements OpAMP fleet management ideas (centralized control/config) and mesh-derived metrics where enrichment happens at collection time. The guidance is sound.

### Claim 12: Agentic/LLM systems require shifting from "is it fast?" to "is it producing cost-effective, reliable, correct outcomes?"
- **Evidence**: Core reframing for AI workloads — probabilistic vs deterministic, qualitative errors vs technical errors, success based on response quality.
- **Confidence**: emerging
- **Quote**: "Traditional microservices operate on deterministic logic, we look for deterministic  success criteria, explicit network errors, and reproducible failure states. AI systems break these assumptions. They operate in probabilistic environments where the exact same prompt can yield wildly different results, errors are frequently qualitative rather than technical, and “success” is based on the quality of the response. Consequently, our definition of telemetry must adapt. While standard latency and error rates still matter, observability must expand to look closely at semantic prompt/response patterns and evaluate **decision quality** rather than just system uptime."
- **Our assessment**: This is the strongest novel angle relative to existing corpus. It overlaps with `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (Claims 1,3,5,8 cover LLM rarely root cause, full execution graph, tool failures, prompt/response capture) and `docs-datadog-llm-observability.md`. The unique contribution here is the explicit "decision quality as observability object" framing and the question shift. The trace path enumerated is also useful: "from user prompt to LLM model, down to iterative tool and agents calls, onto legacy backend microservices, and back up to a final evaluation loop."

### Claim 13: Retroactive/centralized sampling is an emerging standard to watch
- **Evidence**: Forward-looking item — decide centrally, pull granular traces on demand.
- **Confidence**: emerging
- **Quote**: "Keep an eye on incoming paradigms like **retroactive sampling**, which allows systems to make a centralized sampling decision first and then pull back the deep, granular trace telemetry on demand."
- **Our assessment**: Flagged as unadopted/emerging. The post gives no concrete mechanism or adoption status beyond calling it an "emerging architectural standard to watch." Treat as a standards-watch item, not a recommendation. No evidence presented.

### Claim 14: Audit heuristic — "if this data stream stopped flowing tomorrow, what would we actually lose?"
- **Evidence**: Practical litmus test for telemetry value.
- **Confidence**: emerging
- **Quote**: "Regularly audit your architecture by asking one healthy question: *“If this specific data stream stopped flowing tomorrow, what would we actually lose?”*"
- **Our assessment**: This is a simple, actionable heuristic that operationalizes the "telemetry that matters" principle. It forces teams to justify retention/query value rather than collecting by default. No supporting data, but it's a useful mental model.

## Cross-References

**Corroborates:**
- `blog-cncf-otel-mesh-derived-metrics.md` (issue #1661) — shares concern with telemetry volume/cost and cardinality economics; that note provides measured evidence (family-level filtering doesn't reduce label cardinality inside retained family) while this one provides policy controls (mask/drop/truncate, limiters). Complementary, not duplicative.
- `blog-cncf-operating-opentelemetry-at-scale-opamp.md` (issue #1571) — shares "pipeline-side control beats per-service burden" principle and fleet-scale management framing; OpAMP is about control plane, this is about data plane volume reduction. Complementary.
- `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (issue #2) — overlaps on agentic observability: LLM rarely root cause, need to trace full execution graph, auto-instrumentation baseline + manual layering for business context, capturing prompt/response with PII care. The key difference: this post adds "decision quality" as the framing question and enumerates pipeline reduction techniques; Honeycomb focuses on instrumentation patterns and Agent Timeline.

**Extends:**
- Guide Ch02 (Observability) — the "Scripting the observability data plane" section (per triage) currently lacks coverage of cardinality control, sampling strategies (tail-based), log deduplication, and volume/cost control at collection layer. The five named techniques are a concrete extension to that material.
- Guide Ch05 (LLM Ops Reliability) — agentic reframing to "decision quality" and tracing full prompt→model→tool/agent→legacy→eval loop extends existing agent observability content with selection/evaluation framing.

**Contradicts:** None identified.

**Novel (relative to our corpus):**
- The explicit five-technique taxonomy (smart/tail-based sampling, high-cardinality mgmt/masking, cardinality limiters, log deduplication, centralized enrichment) presented as a concrete Day-2 checklist.
- "Decision quality" as the observability object for probabilistic agent workflows (distinct from latency/error rates).
- "Retroactive sampling" flagged as emerging standard (decide centrally, pull granular traces on demand).
- "Green observability" framing linking telemetry waste to energy/carbon footprint.

## Extraction Notes

- **Evidence caveat recorded**: This is a panel recap with no code, configs, benchmarks, or measurements by authors. The sole numeric claim (50% of metrics never queried) is secondhand from external Medium link — marked as attributed, not validated. Confidence capped at `emerging` throughout.
- **Vendor context**: Authors represent VictoriaMetrics, Bindplane/Dynatrace, Cisco ThousandEyes — all commercial observability vendors. Content is tool-neutral (references OTel/OTLP/eBPF), but commercial stake exists. Recorded in author metadata.
- **No contradiction issues filed**: Claims don't materially oppose existing source notes; overlaps are corroborative/complementary.
- **Related-notes candidates**: Reviewed candidates from `miner-related-notes.md` (docs-google-sre-prodcast-03-07-retail-gaming.md, docs-google-sre-slo-engineering-case-studies.md, docs-google-sre-eliminating-toil.md, docs-google-sre-on-call.md, prodcast-03-06 incident response, prodcast-03-09 profiling, prodcast-04-05 furino SLOs, prodcast-03-11 embracing complexity, prodcast-01-05 client-transparent migrations). None of these cover collector-side telemetry volume reduction, cardinality control techniques, or agentic "decision quality" framing. Explicitly dismiss all candidates as non-overlapping for the core claims extracted here.

## Concrete Artifacts Extracted

None (source contains no code blocks, config snippets, terminal transcripts, metrics tables with raw numbers beyond the attributed 50% figure, workflow diagrams, or error messages). All techniques are described conceptually.