---
source_url: https://www.cncf.io/blog/2026/06/29/otel-and-mesh-derived-metrics-a-2026-reference
source_type: blog-post
title: "OTel and mesh-derived metrics: A 2026 reference"
author: Mesut Oezdil (DevOps Engineer, Adfinis — written on behalf of Buoyant)
date_published: 2026-06-29
date_extracted: 2026-10-10
last_checked: 2026-10-10
status: current
confidence_overall: emerging
issue: "#1661"
---

# OTel and mesh-derived metrics: A 2026 reference

> A hands-on lab write-up showing how to bridge Linkerd service-mesh
> (east-west L7) metrics into an existing OpenTelemetry Collector pipeline
> with zero application changes — contributing a "who to trust for what" split
> between mesh metrics and OTel app metrics, a gRPC-trailer alerting blind
> spot, and measured cardinality economics showing that family-level metric
> filtering does not reduce label cardinality inside a retained family.

## Source Context

- **Type**: blog-post (CNCF Community Post, engineer-authored, vendor-adjacent
  but with a working Collector config, measured series counts, and a linked
  upstream bug report)
- **Author credibility**: Mesut Oezdil is a DevOps Engineer at Adfinis GmbH
  writing for CNCF *on behalf of Buoyant* (Linkerd's commercial steward). He is
  a practitioner reporting from a reproducible lab, not an official Linkerd
  maintainer; the config is also maintained in his public `myOTel` reference
  stack. The environment: single-node K3s v1.34.6, Linkerd edge-26.5.5,
  OTel Collector contrib 0.118.0, VictoriaMetrics + Grafana, with the OTel
  "Astronomy Shop" demo as the meshed workload. The claim that Linkerd "no
  longer publishes stable release artifacts" and the Buoyant Enterprise
  framing are vendor-adjacent and recorded as sourced claims, not guide facts.
- **Scope**: Covers what mesh-derived metrics add beyond app-layer OTel
  (service topology + mTLS identity), the overlap/non-overlap between the two
  signal layers and a decision rule for trusting each, a full Collector
  pipeline for scraping mesh metrics, two filtering mechanisms with measured
  outcomes, and a documented Collector config-parse failure. Does NOT cover:
  AI/LLM workloads (the post explicitly stays out of that), per-route proxy
  metrics (`outbound_http_route_*` are deliberately excluded as future work),
  north-south ingress, or the VictoriaLogs log pipeline. Series counts are
  lab-scale (30 pods) and should be read as illustrative of cardinality
  mechanics, not production benchmarks.

## Extracted Claims

### Claim 1: A meshed workload gets golden metrics for every inbound and outbound request with zero code changes — no instrumentation, SDK calls, or image rebuild
- **Evidence**: Linkerd injects a sidecar proxy into each pod; the proxy
  intercepts all inbound/outbound traffic and exposes a Prometheus endpoint on
  port 4191. Injection is one namespace annotation (`linkerd.io/inject=enabled`)
  plus a rollout, after which pods go from `1/1` to `2/2` Ready. The post shows
  the proxy answering on 4191 where nothing listened before injection.
- **Confidence**: settled (reproducible lab mechanics with shown commands/output)
- **Quote**: "Linkerd's proxy provides those metrics. Once a workload is meshed, the proxy immediately emits golden metrics for every inbound and outbound request. No need for instrumentation, SDK calls, or image rebuild."
- **Our assessment**: This is the piece's headline and its most transferable
  property: the network layer emits golden signals without any app cooperation.
  For the guide it is the counterpoint to the app-layer OTel GenAI
  instrumentation the corpus already covers (Honeycomb note) — mesh metrics
  require no SDK or span annotations at all. The `no rebuild` claim is
  conditional on the sidecar-injection model (Linkerd), not universal across
  meshes.

### Claim 2: OTel cannot see network-layer east-west traffic unless both ends are explicitly instrumented — the mesh layer fills the service-topology gap
- **Evidence**: The post contrasts what OTel covers (what the application knows
  about itself: HTTP counts, DB durations, business counters like
  `app_cart_add_item_latency_seconds`) with what the network knows, and states
  the OTel blind spot directly.
- **Confidence**: settled
- **Quote**: "All of this lives at the application layer. OTel instruments your code, but it can't see traffic that flows between services at the network level unless you explicitly instrument both ends."
- **Our assessment**: A crisp statement of the boundary: trace propagation
  requires both caller and callee to cooperate, so service-to-service traffic
  is invisible to OTel unless every endpoint is instrumented. The mesh proxy,
  intercepting L7 traffic regardless of app behavior, is authoritative on the
  actual connection. This supports the guide's "instrument the whole
  execution graph" rule by identifying the residual blind spot that no
  app-level SDK can close.

### Claim 3: The `client_id` label is the mTLS identity of the caller — cryptographic proof of who is talking to whom that no application-level metric can produce
- **Evidence**: Raw proxy counter output shows
  `client_id="otel-demo.otel-demo.serviceaccount.identity.linkerd.cluster.local"`
  on a `request_total` series; the post states this is the mTLS identity.
- **Confidence**: settled
- **Quote**: "The `client_id` label is the mTLS identity of the caller. That's something no application-level metric gives you: cryptographic proof of who is talking to whom on every request counter."
- **Our assessment**: mTLS-derived caller identity is a genuinely new dimension
  for the observability corpus: it is not something the app reports about
  itself, so it cannot be spoofed by app bugs and requires no instrumentation.
  Note the cardinality consequence — a per-identity label like `client_id`
  multiplies series on every retained histogram (see Claim 8) — which is
  exactly the cost the linsun cardinality rule exists to control.

### Claim 4: Linkerd's golden metrics (success rate, request rate, latency) are computed from two families — `response_total` and `response_latency_ms` — plus TCP-level gauges/counters
- **Evidence**: The post lists the families available with Linkerd 2.19+
  (`response_total`, `response_latency_ms`, `tcp_open_connections`,
  `tcp_read_bytes_total`, `tcp_write_bytes_total`), states which two feed the
  golden signals, and notes the proxy also exposes per-route families
  (`outbound_http_route_*`) that the pipeline deliberately drops because they
  bring different units and "another layer of cardinality."
- **Confidence**: settled
- **Quote**: "The first 2 are where Linkerd's golden metrics come from: success rate, request rate, and latency are all computed from them."
- **Our assessment**: Useful for the guide as the concrete map from raw mesh
  metrics to golden signals. The deliberate exclusion of per-route families is
  itself a scoping decision worth recording: the author treats per-route
  cardinality as "future work rather than a headline," i.e., an incremental
  series-cost decision the operator must make consciously.

### Claim 5: Request rate, latency, and errors appear in both layers but are measured differently — the decision rule is mesh for mTLS identity and east-west success rate, OTel app metrics for business semantics, traces for root cause
- **Evidence**: Worked comparison: `response_total{layer="mesh"}` (proxy,
  carries `client_id`, `classification`, `grpc_status`) vs
  `app_frontend_requests_total` (app instrumentation); `response_latency_ms_bucket`
  (proxy, headers-to-stream-complete timing) vs `app_cart_add_item_latency_seconds_bucket`
  (cart service's own instrumentation). A Grafana panel plots mesh p99 per pod
  against app p99 for `cart.add_item`. The post then gives the trust rule as a
  three-bullet list.
- **Confidence**: emerging (the measurements-won't-match observation is settled;
  the trust split is the author's recommended design rule)
- **Quote**: "The mesh and app measurements won't be identical. The proxy measures network-level timing; the application measures its own internal processing. The gap between them can surface network overhead, queuing, or slow middleware."
- **Our assessment**: This is the source's single most durable contribution: a
  boundary rule for running both signal layers without constant low-level
  mismatches. The mesh series carry `grpc_status` and mTLS identity the app
  series cannot; the app series carry business dimensions the proxy cannot see
  ("Only your code knows that a request was a 'checkout' for a 'platinum'
  customer"). The guide should present this as a self-documenting division of
  labor with the conditioning caveat that the two numbers will differ by design.

### Claim 6: HTTP-status-only alerting silently misses gRPC failures because gRPC status travels in the response trailers — a series can carry `status_code="200"` plus `classification="failure"` and `grpc_status="14"`
- **Evidence**: Raw proxy output shows
  `response_total{direction="outbound", status_code="200", dst_service="ad",
  classification="failure", grpc_status="14", ...} 6` — HTTP reports success
  while the gRPC status is UNAVAILABLE. A Jaeger trace of the same operation
  resolves it (`error=true`, `grpc.error_message` "14 UNAVAILABLE").
- **Confidence**: settled (protocol fact plus a demonstrated series)
- **Quote**: "In gRPC, the status code travels in the response trailers, separately from the HTTP status line, so if you only alert on HTTP status codes, this failure is invisible. The proxy reads that status and classifies the response as a failure anyway."
- **Our assessment**: Directly actionable for the guide's alerting design: for
  gRPC services, HTTP-based success/failure classification is insufficient, and
  the mesh layer's `classification`/`grpc_status` labels are a free
  out-of-band failure signal. This transfers to LLM ops because gRPC is common
  in LLM serving infrastructure. Assayer note: the post cannot see this failure
  "and the mesh knows the call failed and how many times, but it doesn't know
  why" — a deliberate boundary (see Claim 7).

### Claim 7: The mesh knows a call failed and how many times, but not why — distributed traces supply the root cause
- **Evidence**: The Jaeger trace shows the exact failing span (`oteldemo.AdService/GetAds`), the error message "`14 UNAVAILABLE`", and both addresses; the post states the trace "shows the exact span that failed, the exact error message, and the client and server addresses involved."
- **Confidence**: settled (demonstrated with a labeled trace screenshot)
- **Quote**: "The trace shows the exact span that failed, the exact error message, and the client and server addresses involved. The mesh flags the issue while the trace shows you the root cause."
- **Our assessment**: This is the same SLO-must-drill-down doctrine the
  observability-spectrum note argues (Claim 9): a trending failure signal
  (here the mesh's `classification=failure` counters) is only the pointer; the
  actual bisect needs trace data. It corroborates that the guide's rule —
  "every user-facing SLO must reference a trace that lets you bisect" — holds
  for infrastructure-layer golden signals too, and justifies keeping both
  layers.

### Claim 8: Filtering by metric family shortens the name list but does nothing to label cardinality inside a retained family — "a histogram you keep is a histogram you pay for"
- **Evidence**: Measured in the lab: one stored `response_latency_ms_bucket`
  series carries 35 labels (proxy-emitted plus k8sattributes/resource
  enrichment: `direction, tls, client_id, authz_kind, route_name, srv_name,
  le`, and more). Across the 30 meshed pods in the scrape,
  `response_latency_ms_bucket` alone produced 5,642 series and the whole
  `job="linkerd-mesh"` scrape totaled 9,280 series *after* filtering. Without
  filtering the proxy exposes 163 distinct metric families.
- **Confidence**: settled (measured counts, explicitly post-filter)
- **Quote**: "Both numbers are post-filter, and that's the point: filtering by metric family shortens the name list, but it does nothing to the label cardinality inside a family you keep. A histogram you keep is a histogram you pay for."
- **Our assessment**: The strongest cost argument in the piece and the direct
  quantitative evidence for the corpus's cardinality rule (linsun Claim 11):
  per-series cost is labels × buckets × pods, and keeping a family means paying
  for every allowed label combination. The 5,642 / 9,280 / 163 figures are
  lab-scale but the *mechanism* is universal. Guide rule: before retaining a
  metric family, estimate retained series as (distinct label-value
  combinations) × (histogram buckets) × (instances) — family filtering alone is
  not a cardinality control.

### Claim 9: Filtering mechanism choice changes what reaches the backend — an anchored `metric_relabel_configs` keep regex admits 15 metric names while an unanchored OTTL `IsMatch` filter admits 11, because the two anchor differently and only OTTL drops synthetic scrape series
- **Evidence**: Tested on contrib 0.118.0. With the keep rule
  (`response_total|response_latency_ms.*|tcp_.*`) and no OTTL filter, 15 names
  flowed in: 9 matching proxy names plus 6 the keep rule never sees — the
  scrape's synthetic series (`up`, `scrape_duration_seconds`,
  `scrape_samples_scraped`, `scrape_samples_post_metric_relabeling`,
  `scrape_series_added`), which relabeling does not apply to, and the
  exporter-generated `target_info`. The OTTL filter lands at 11 names (163
  families in, 11 out). The gap comes from anchoring plus the synthetic series.
- **Confidence**: settled (reproducible comparison with counted results on a
  pinned Collector version)
- **Quote**: "The relabel regex is fully anchored, so `response_latency_ms.*` doesn't admit `control_response_latency_ms_*;` OTTL's IsMatch is unanchored, so those 3 control-plane names leak through it. In the other direction, tcp\_.\* in the keep rule admits every TCP family the proxy exposes, `tcp_open_total` and `tcp_close_total` included, while the OTTL list names its 3 TCP metrics explicitly. And only the OTTL filter drops the synthetic scrape series."
- **Our assessment**: A concrete, reproducible trap: anchorage semantics differ
  between the receiver's relabel regex (fully anchored) and OTTL `IsMatch`
  (unanchored), so apparently equivalent keep lists admit different metric
  sets. The `control_response_latency_ms_*` leakage is Linkerd control-plane
  traffic the operator did not intend to ship. The guide should record this as
  a config-level decision: pick the filtering mechanism knowingly, verify what
  it actually admits at runtime, and remember the scrape's synthetic series
  flow unless OTTL (or equivalent) drops them.

### Claim 10 (mini failure report): The `$1:4191` relabel replacement collides with the Collector's `$`-based env-var expansion on some versions — startup-rejected on contrib 0.104.0 via the `confmap.unifyEnvVarExpansion` gate, still broken (even escaped `$$1`/`$$2`) at 0.112.0, fixed by 0.118.0 — pin your image tag
- **Evidence**: The author hit the rejection on contrib 0.104.0 with the
  workaround `--feature-gates=-confmap.unifyEnvVarExpansion`; the same failure
  is reported upstream
  (open-telemetry/opentelemetry-collector-contrib issue #36160) on 0.112.0,
  rejecting even an escaped `$$1:$$2` replacement; contrib 0.118.0 accepts the
  config.
- **Confidence**: settled (first-person reproduction plus linked upstream issue)
- **Quote**: "I hit it on contrib 0.104.0 in an earlier run, where the `confmap.unifyEnvVarExpansion` feature gate was the cause `(workaround then: --feature-gates=-confmap.unifyEnvVarExpansion)`."
- **Quote**: "Contrib 0.118.0, the version this lab pins, accepts the config. Pin your image tag."
- **Our assessment**: A genuine "pin your image tag" lesson with version-
  specific evidence: `$` is overloaded in Collector config (regex replacement
  vs env-var expansion), so a `$1:4191` relabel rule is ambiguous to the
  config-unification machinery and can reject startup without any scraping
  error. For the guide this is a failure-report pattern worth recording in
  Ch02's pipeline section: treat "it parsed yesterday" as false when the
  Collector image tag moves, and gate config changes on the pinned Collector
  version.

### Claim 11: The reference integration pattern is a dedicated `prometheus/mesh` receiver pipeline — pod discovery of `linkerd-proxy` containers, OTTL filter to 5 families, `layer=mesh` resource insertion, k8sattributes enrichment — delivering to any Prometheus-compatible backend with mesh and app metrics kept as separate Grafana datasources
- **Evidence**: Full Collector YAML provided (see Concrete Artifacts). Mesh
  metrics land in VictoriaMetrics while the OTel Demo's app metrics stay in its
  bundled Prometheus; Grafana reads both as separate datasources, wired as a
  mixed-datasource panel where query A pulls `response_latency_ms_bucket{layer="mesh"}`
  and query B pulls `app_cart_add_item_latency_seconds_bucket`.
- **Confidence**: settled (working config, downloadable dashboard, also
  maintained in the public `myOTel` reference stack)
- **Quote**: "When import-testing, both datasource inputs are prometheus-type and easy to point at the same source by accident. Map the mesh input to VictoriaMetrics and the app input to your Prometheus."
- **Our assessment**: The config is the reusable artifact; the one added gotcha
  is the import-time datasource mis-wiring, where the two largely identical
  prometheus-type inputs can silently collapse both queries onto one backend.
  The guide can cite this as a worked mesh-integration recipe that requires one
  Collector config change and a namespace annotation on top of an existing OTel
  deployment.

### Claim 12 (vendor-adjacent, sourced claim only): As of this writing, Linkerd open source no longer publishes stable release artifacts — edge releases are the production-ready line, and Buoyant Enterprise for Linkerd (BEL) is the supported enterprise distribution
- **Evidence**: Stated in a version note before the commands, with a link to
  linkerd.io/releases; the lab runs edge-26.5.5.
- **Confidence**: anecdotal (single vendor-affiliated blog statement; not
  independently verified here)
- **Quote**: "as of this writing, the Linkerd open source project no longer publishes stable release artifacts; edge releases are the production-ready line (see linkerd.io/releases), and Buoyant Enterprise for Linkerd (BEL) is the supported enterprise distribution."
- **Our assessment**: Record as a sourced claim, not guide fact. It is the
  clearest vendor-adjacent statement in the piece and the one the Assayer flagged
  for caution: a Buoyant-affiliated author's framing of the project's release
  model should not be absorbed into the guide without independent confirmation.

## Concrete Artifacts

### Artifact 1: Collector pipeline for mesh metrics (verbatim from the post; the full file is downloadable alongside the post)

```
receivers:
  prometheus/mesh:
    config:
      scrape_configs:
        - job_name: linkerd-mesh
          scrape_interval: 30s
          kubernetes_sd_configs:
            - role: pod
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_container_name]
              action: keep
              regex: linkerd-proxy
            - source_labels: [__meta_kubernetes_pod_ip]
              action: replace
              target_label: __address__
              regex: (.+)
              replacement: $1:4191

processors:
  filter/mesh:
    error_mode: ignore
    metrics:
      metric:
        - 'not(name == "response_total" or IsMatch(name, "response_latency_ms.*") or name == "tcp_open_connections" or name == "tcp_read_bytes_total" or name == "tcp_write_bytes_total")'

  resource/mesh:
    attributes:
      - key: layer
        value: mesh
        action: insert

service:
  pipelines:
    metrics/mesh:
      receivers: [prometheus/mesh]
      processors: [memory_limiter, filter/mesh, resource/mesh, resourcedetection, k8sattributes, batch]
      exporters: [prometheusremotewrite]
```

### Artifact 2: The receiver-side `metric_relabel_configs` alternative (verbatim from the post)

```
metric_relabel_configs:
  - source_labels: [__name__]
    action: keep
    regex: "response_total|response_latency_ms.*|tcp_.*"
```

### Artifact 3: Unmeshed vs meshed probe (verbatim excerpts)

No listener before injection:

```
kubectl exec -n otel-demo ad-74784f8f59-4nmwp -- wget -qO- http://localhost:4191/metrics 2>&1
```

Counter output after meshing (labels trimmed for readability in the source):

```
# HELP request_total Total count of HTTP requests.
request_total{direction="inbound", target_addr="10.42.0.217:8080", tls="true",

client_id="otel-demo.otel-demo.serviceaccount.identity.linkerd.cluster.local", ...} 20
```

### Artifact 4: The gRPC-trailer failure series (verbatim from the post, labels trimmed for readability)

```
response_total{direction="outbound", status_code="200", dst_service="ad",
  classification="failure", grpc_status="14", ...} 6
```

The resolving Jaeger span tag: `error=true`, `grpc.error_message`
`"14 UNAVAILABLE: client 10.42.0.216:52176: server: 10.42.0.217:4143."`

### Artifact 5: Cardinality accounting (measured in the lab, post-filter unless noted)

| Item | Count |
|------|-------|
| Labels on one stored `response_latency_ms_bucket` series | 35 |
| Pods in the `job="linkerd-mesh"` scrape | 30 |
| Series from `response_latency_ms_bucket` alone (post-filter) | 5,642 |
| Total series for the whole scrape (post-filter) | 9,280 |
| Distinct metric families the proxy exposes (unfiltered) | 163 |
| Metric names reaching backend via anchored relabel keep (no OTTL) | 15 |
| Metric names reaching backend via OTTL filter/mesh | 11 |

11-name breakdown (per post): 5 families export as 7 names (each histogram
splits into `_bucket, _count, _sum`), 3 more leak from
`control_response_latency_ms_*`, and the last is the exporter-generated
`target_info`.

### Artifact 6: The env-var expansion trap (version → behavior)

| Collector contrib version | Behavior with `replacement: $1:4191` |
|---------------------------|---------------------------------------|
| 0.104.0 | Config rejected at startup (`confmap.unifyEnvVarExpansion` gate); workaround `--feature-gates=-confmap.unifyEnvVarExpansion` |
| 0.112.0 | Still rejected, even with escaped `$$1:$$2` replacement (upstream open-telemetry/opentelemetry-collector-contrib#36160) |
| 0.118.0 | Accepted |

## Cross-References

- **Corroborates**:
  - `source-notes/docs-google-sre-prodcast-03-04-observability-spectrum.md`
    **Claim 9** — the SLO-signal-must-drill-down principle. This source's Claim
    7 ("The mesh flags the issue while the trace shows you the root cause") is
    the same doctrine applied to infrastructure golden signals: a trending
    failure counter is only the pointer; bisecting the cause needs trace data.
  - `source-notes/blog-linsun-pod-deployment-unit-ai-agent.md` **Claim 11** —
    its cardinality rule ("high-cardinality actor identity ... stays off
    metrics entirely and lives on logs and traces instead") is the corpus's
    standing answer to the exact problem this source quantifies: Claim 8 here
    measures the series cost (35 labels, 5,642 series from one family across 30
    pods) of carrying identity-like labels on retained histograms. This source
    keeps `client_id` on mesh metrics and *shows the price*; it evidences the
    rule rather than opposing it. Same claim heading, both directions — see
    Contradicts for the tension note.
  - `source-notes/docs-google-sre-prodcast-03-09-profiling-data.md` **Claim 4** —
    the "discarding ~90% of data still covers ~90% of cost" framing is the
    profiling-data analog of this source's "keep what you pay for" cardinality
    arithmetic: high-cardinality telemetry must be actively curated for cost.
    Scope differs (per-cohort profiling modeling vs metrics series count), so the
    link is thematic, not a same-mechanism agreement.
- **Contradicts**: None that meets the MINER.md §4a bar (checked open
  `contradiction`-labeled issues — none concern this topic). Two **tensions**
  recorded rather than filed:
  - The mesh post ships high-cardinality identity (`client_id`) on metric
    series — the linsun cardinality rule's explicit anti-pattern. Not an
    opposition: the two are the same coin. The mesh layer makes a deliberate
    exception (mTLS identity is the layer's whole point) and pays the series
    cost this source candidly measures. Guide treatment: state both — prefer
    the linsun rule for app/agent metrics, and treat mesh-provided identity
    labels as a known-cost exception whose series math must be checked before
    retention.
  - `docs-google-sre-prodcast-03-04-observability-spectrum.md` **Claim 4**
    frames pre-aggregated metrics as only answering anticipated questions,
    while this source advocates deriving golden success-rate/latency alerts
    from mesh counters. Complementary, not opposed: the mesh metrics are the
    "anticipated questions" layer (awareness that something failed and how
    often), and the source itself defers root cause to traces (Claim 7) — the
    spectrum note's point exactly. Different questions, same division of labor.
- **Extends**:
  - `source-notes/blog-cncf-operating-opentelemetry-at-scale-opamp.md` — same
    CNCF seed and OTel-Collector domain; that note is the *control plane*
    (OpAMP agent/fleet config), this note is the *data plane* (a Collector
    pipeline with measured cardinality economics). The series-cost math here
    quantifies what a fleet operator must govern there.
  - `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md` — same
    OTel-Collector-in-a-single-node-K8s idiom and same network-layer
    complement to app-layer OTel; that note adds egress spans as an audit plane,
    this note adds mesh metrics as a golden-signal layer. Shared collector-config
    idiom, different concern.
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` —
    the layer below the app. Honeycomb instruments agent internals with GenAI
    semconv (Claim 4: auto-instrumentation covers the LLM layer only, agent
    attributes are hand-authored); this source adds the *infra* layer beneath,
    where golden signals come with zero app cooperation. Together they describe
    three layers of one AI-ops stack: network/mesh, app/instrumentation, and the
    collector pipeline connecting both to a backend.
- **Novel**:
  - **Service-mesh-derived metrics as an OTel signal source** — no existing
    note covers mesh metrics, `layer=mesh` tagging, or the "who to trust for
    what" split (mesh → mTLS identity + east-west success rate; app metrics →
    business semantics; traces → root cause).
  - **The gRPC-trailer alerting blind spot** — `status_code="200"` +
    `classification="failure"` + `grpc_status="14"`: HTTP-status-only alerting
    misses gRPC failures because gRPC status rides in response trailers. New to
    the corpus and directly transferable to LLM ops (gRPC-heavy serving).
  - **Family-filtering ≠ cardinality control** — the measured claim that
    deleting metric families does nothing to label cardinality inside a
    retained family, plus the anchor-difference comparison (relabel keep: 15
    names vs OTTL `IsMatch`: 11 names).
  - **The `$1:4191`-vs-env-var-expansion Collector trap** — a config-parse
    failure with version-gated evidence (0.104.0 broken → 0.112.0 still broken
    → 0.118.0 fixed), i.e. a "pin the Collector image tag" lesson.

## Guide Impact

- **Chapter 01 (Incident Response)**: Add the gRPC-trailer alerting rule from
  Claim 6: alert on the mesh's `classification`/`grpc_status` labels for
  east-west traffic rather than HTTP status alone, because gRPC status travels
  in response trailers and HTTP-success + gRPC-failure is a real series shape.
  This is the concrete example the chapter's alerting-design guidance lacks.
- **Chapter 02 (Observability)**: Add a subsection on the signal layer below
  the app — mesh-derived metrics within an OTel pipeline (Claims 1, 4, 11):
  golden metrics with zero instrumentation, the "trust mesh for mTLS identity
  and east-west success rate, OTel app metrics for business semantics, traces
  for root cause" decision rule (Claim 5), and the two cardinality rules from
  Claim 8 (family filtering does not curb label cardinality; estimate retained
  series as label-combinations × buckets × instances before keeping a
  histogram). Wire Claim 7 into the existing SLO-drill-down section: mesh
  failure counters are pointers; traces are the bisect every SLO needs.
  Include the Claim 10 "pin your Collector image tag" failure-report note in
  the pipeline section.
- **Chapter 05 (LLM Ops Reliability)**: The cardinality economics (Claim 8) and
  the gRPC alerting blind spot (Claim 6) transfer directly to LLM pipelines,
  where gRPC is common and metric cost scales with model/service count. Frame
  the note as the infra-layer telemetry substrate beneath LLM app
  instrumentation rather than an LLM-specific pattern.

## Extraction Notes

- **Source was read in full** via WebFetch; it is a single page with no
  sub-pages. The post ships a working Collector config and downloadable Grafana
  dashboard JSON; per the triage, the config is also maintained in the public
  `myOTel` reference stack (linked in the post) which the guide should prefer
  as the authoritative artifact. I did not follow the upstream
  open-telemetry/opentelemetry-collector-contrib#36160 issue beyond recording
  its number and version claims as reported in the post.
- **Quotes**: All `Quote` fields were copied character-for-character from the
  fetched page, including embedded code spans (`client_id`,
  `response_latency_ms.*`, `confmap.unifyEnvVarExpansion`,
  `--feature-gates=-confmap.unifyEnvVarExpansion`) and the escaped `tcp\_.\*`
  in the Claim 9 quote exactly as rendered. One source rendering artifact was
  deliberately avoided: the post's phrase around the relabel replacement
  renders ambiguously ("`the replacement:` $1:4191 relabel rule"), so Claim 10
  quotes only the contiguous fragments that carry the version-specific evidence
  rather than that ambiguous clause. Claim 12's quote retains the source's
  parenthetical "(see linkerd.io/releases)" verbatim.
- **Candidate list disposition** (`miner-related-notes.md`, read first): the 10
  candidates were each considered. Cited from the list:
  `docs-google-sre-prodcast-03-09-profiling-data.md` (Claim 4, thematic
  cardinality-must-be-curated corroboration) and
  `docs-google-sre-prodcast-03-04-observability-spectrum.md` (found by corpus
  search, not on the list — Claims 4 and 9). Explicitly dismissed as not
  materially overlapping: `docs-google-sre-prodcast-03-07-retail-gaming.md`,
  `docs-google-sre-slo-engineering-case-studies.md`,
  `docs-google-sre-eliminating-toil.md`,
  `docs-google-sre-prodcast-03-13-imperative-declarative.md`,
  `docs-google-sre-reliable-product-launches.md`, `docs-google-sre-on-call.md`,
  `docs-google-sre-team-lifecycles.md`, `docs-google-sre-prodcast-03-01.md`, and
  `docs-litellm-anthropic-advisor-tool.md` — no candidate carries mesh metrics,
  Prometheus/OTel Collector pipeline config, metrics cardinality economics, or
  gRPC alerting content, so no honest corroboration/contradiction exists. Cited
  from outside the candidate list (corpus search):
  `blog-linsun-pod-deployment-unit-ai-agent.md` (Claim 11, cardinality rule),
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`, and the two
  sibling CNCF notes.
- **Confidence**: `confidence_overall: emerging`. The lab mechanics, series
  counts, and the gRPC-trailer protocol fact are independently checkable
  (several stated settled at claim level), but the environment is a single-node
  lab and the author is vendor-affiliated (Buoyant), so the transferable
  numbers and the "who to trust" guidance stay at emerging until corroborated
  at production scale. Consistent with the two sibling CNCF notes.
- **No contradiction issue was filed.** Per MINER.md §4a, the two recorded
  tensions (client_id vs the linsun cardinality rule; meshes-as-metrics vs the
  spectrum note's metrics-critic framing) are conditioning/context differences,
  not oppositions that would force different guide advice; the open
  contradiction issue list contains nothing about this topic.
- **Vendor-adjacency caveat**: written "on behalf of Buoyant," the post's
  release-line claim (Claim 12) and enterprise framing are recorded as sourced
  claims; the independently reproducible config and measurements are the parts
  the guide should lean on.