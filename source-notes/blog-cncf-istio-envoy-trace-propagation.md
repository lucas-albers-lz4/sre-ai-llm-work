---
source_url: https://www.cncf.io/blog/2026/08/11/a-practical-guide-to-solving-when-zerozerotwo-in-mesh-observability
source_type: blog-post
title: "A practical guide to solving when zero+zero=two in mesh observability"
author: Israel Blancas (Software Engineer, Coralogix), Jose Gomez-Selles (Product Lead, VictoriaMetrics)
date_published: 2026-08-11
date_extracted: 2026-11-05
last_checked: 2026-11-05
status: current
confidence_overall: emerging
issue: "#2042"
---

# A practical guide to solving when zero+zero=two in mesh observability

> A worked OpenTelemetry Demo case study showing that adding Istio/Envoy to an
> already-instrumented workload silently forks one request into two unrelated
> trace trees, and that the fix requires both an Envoy-side switch to the
> Zipkin/B3 tracer via the Collector's `:9411` receiver and an app-side
> `OTEL_PROPAGATORS` addition of `b3multi` — establishing the Collector as a
> format-normalization layer rather than merely an exporter target.

## Source Context

- **Type**: blog-post (CNCF Member Post, practitioner-authored, vendor-adjacent)
- **Author credibility**: Israel Blancas is a Software Engineer at Coralogix;
  Jose Gomez-Selles is a Product Lead at VictoriaMetrics. Both are practitioners
  in the observability vendor ecosystem, but the post sells no specific product
  feature — the fix uses only upstream Istio, Envoy, and OpenTelemetry Collector
  configuration. The environment is explicitly the OpenTelemetry Demo on Istio
  with Jaeger and the Collector, not the authors' production estate.
- **Scope**: Covers why Istio/Envoy tracing fragments traces for an already-OTel-
  instrumented application, the exact propagation mismatch, the two-sided fix
  (mesh-side Zipkin/B3 tracer + app-side B3 emission), the measured before/after
  span counts, and the general role of the Collector as a multi-format
  convergence point. Does NOT cover: production validation, Envoy/Istio version
  pins, sampling or tail-sampling interaction with the fix, B3 single-header
  (`b3`) versus multi-header (`b3multi`) trade-offs, or non-Istio meshes
  (Linkerd, Cilium) beyond the general Collector argument.
- **Maturity note**: The mechanics are demonstrated end-to-end in a reproducible
  demo, but the post gives no Envoy/Istio version and the authors themselves
  describe the Envoy OTel tracer behavior as something that can change upstream.
  Read the mechanism as settled-for-demo and the workaround as version-sensitive.

## Extracted Claims

### Claim 1: A service mesh plus Kiali gives request-rate, latency, error-rate, and topology visibility with no application changes, but it still cannot explain why one specific request failed — that gap needs tracing
- **Evidence**: The intro lists what arrives once sidecars are injected (request
  volume, latency and error rate per workload, Kiali topology, proxy access
  logs) and then states the gap between "the network looks unhealthy" and a
  concrete failed user request. The authors frame tracing as what closes it.
- **Confidence**: settled (mesh capability and the observability boundary are
  both well established)
- **Quote**: "You install the mesh, point Prometheus at it, and suddenly you have request rate, latency, error rate, and a fairly good picture of service-to-service traffic."
- **Quote**: "But there is still a gap between “the network looks unhealthy” and “this exact user request failed because checkout called product-catalog twice and retried after a timeout”. That gap is usually closed by tracing."
- **Our assessment**: This is the motivating split the corpus already uses for
  metrics versus traces: the mesh layer tells you *that* something is wrong and
  *where* on the topology, while a trace tells you *which request* and *which
  hop*. It is a useful concrete example for the guide's "every SLO needs a
  drill-down target" rule, not a novel claim on its own.

### Claim 2: Installing Istio sidecars on an already-OTel-instrumented app does not simply add spans — it fragments traces, producing two versions of the same service and two unrelated trace trees for one request
- **Evidence**: The OpenTelemetry Demo shows complete end-to-end traces before
  Istio. After sidecar injection and Envoy tracing, Jaeger shows `checkout` from
  the app SDK and `checkout.otel-demo` from the Envoy sidecar; the post shows the
  before/after Jaeger screenshots.
- **Confidence**: settled (demonstrated in the stated demo environment)
- **Quote**: "In Jaeger, you start seeing two versions of the same service:"
- **Quote**: "The first comes from the OpenTelemetry SDK inside the application. The second comes from the Envoy sidecar. At first glance, this looks promising. More spans should mean more visibility."
- **Quote**: "In practice,  what you have is two unrelated trace trees for the same request."
- **Our assessment**: This is the central failure mode and the one the guide
  currently lacks. "Two versions of the same service" is the tell: the mesh is
  emitting spans under a different resource identity because it never joined the
  app's trace. The double space in the third quote is reproduced from the source
  as fetched. The claim is strong because the demo is reproducible, but it is a
  demo, not a production census — see Claim 11.

### Claim 3: The root cause is context propagation: Envoy's built-in OTel tracer starts a new root span per request and never reads the incoming W3C `traceparent`, while the app SDK keeps forwarding its own `traceparent` independently
- **Evidence**: The authors state the behavior directly and contrast it with the
  app's SDK propagation using standard W3C Trace Context headers. The same
  mechanism is restated in the final section.
- **Confidence**: settled for the demo configuration; version-sensitive as a
  statement about Envoy generally (see Claim 10)
- **Quote**: "Envoy’s built-in OTel tracer starts a brand-new root span for every request. It never reads the incoming W3C `traceparent` header. The OTel SDK inside each service continues forwarding its own `traceparent` independently, so the two trace streams never converge."
- **Our assessment**: This is the most valuable technical finding in the post.
  It explains the "zero+zero=two" title: both components are instrumented
  correctly, yet the boundary between them drops continuity. For LLM ops this is
  the same class of silent failure as an agent gateway that sets correlation
  headers the downstream service never forwards. The guide should record the
  general rule — verify propagation at every infrastructure boundary, not just
  inside the app — and treat the specific Envoy behavior as versioned.

### Claim 4: Enabling the `otel-tracing` extension provider is not sufficient; switching Envoy to its Zipkin tracer, pointed at the Collector's Zipkin receiver on `:9411`, is what makes Envoy extract B3 context and create child spans under the existing trace
- **Evidence**: The post calls this "the most surprising bit," shows the
  `extensionProviders` configuration that only exports Envoy spans, then adds a
  `defaultConfig.tracing.zipkin.address` pointing at the Collector's `:9411`
  receiver. The authors explain that the Collector can converge multiple
  receivers into one pipeline.
- **Confidence**: emerging (demo-verified, counter-intuitive, and dependent on
  the Zipkin tracer's B3 extraction behavior)
- **Quote**: "This was the most surprising bit. One would think that enabling OpenTelemetry with the `otel-tracing` provider would be the ultimate zero-instrumentation solution (see Telemetry resource)."
- **Quote**: "After that, the actual fix, from a user perspective, is to switch Envoy to its Zipkin tracer instead. Envoy’s Zipkin tracer does extract B3 trace context from incoming requests and creates child spans under the existing trace."
- **Quote**: "By just pointing it at the OTel Collector’s Zipkin receiver (port 9411) spans will still end up together."
- **Our assessment**: The counter-intuition is the point: choosing a *different*
  tracer on the mesh side is what makes the OpenTelemetry ecosystem converge.
  The guide should present this as a specific, conditional recipe for
  Istio/Envoy, not a universal "use Zipkin" recommendation. The Collector's
  ability to accept Zipkin and OTLP in one pipeline is what keeps the backend
  choice open.

### Claim 5: The app side must also emit B3 in addition to W3C `tracecontext` and `baggage`; the mesh-side tracer change alone does not join the traces
- **Evidence**: The demo values set `OTEL_PROPAGATORS` to
  `"tracecontext,baggage,b3multi"`, which the authors say keeps W3C propagation
  while also emitting B3 headers Envoy can consume.
- **Confidence**: settled (concrete demo configuration, both halves required)
- **Quote**: "The other half of the fix is propagation on the application side."
- **Quote**: "In practice, this configures automatically instrumented applications to keep propagating the standard W3C headers, while also emitting B3 headers that Envoy can use to continue the same trace instead of creating a new one."
- **Our assessment**: This is the actionable app-side half of the contract. It
  also carries an important implication for "zero-code instrumentation": the
  demo's auto-instrumentation is still correct, but its default propagator list
  is insufficient for this mesh. Zero-code does not mean zero-configuration at
  system boundaries. The `b3multi` choice (multi-header B3) is specific to what
  Envoy's Zipkin tracer extracts and should be stated as such.

### Claim 6: The Collector must be treated as the convergence and normalization point where OTLP app telemetry and Zipkin/B3 mesh telemetry meet — not merely as an exporter target
- **Evidence**: The authors define the two pieces of the fix (Collector
  integration and propagation agreement) and later say the Collector receives
  multiple formats, normalizes them into the OpenTelemetry model, and exports to
  one backend. The demo already sends app OTLP to the Collector; only a Zipkin
  receiver is added for Envoy.
- **Confidence**: emerging (design principle demonstrated in the demo, not
  measured at scale)
- **Quote**: "The first is the Collector. Instead of treating the Collector as just another exporter target, treat it as the place where the mesh and the applications meet."
- **Quote**: "The OpenTelemetry Collector is perfect for that: it receives telemetry in multiple formats, normalizes everything into the OpenTelemetry model, and exports it to a single backend."
- **Our assessment**: This reframing is the durable architectural lesson. It
  explains why the fix does not require Envoy to speak OTLP natively and why the
  backend stays unchanged. The guide should state the rule generally: any
  component boundary with a format mismatch should be normalized in the
  Collector, not patched by changing every producer.

### Claim 7: In the demo, the fix consolidates a request from trace clusters of ~14 or 2 spans into 51–75 spans in a single trace
- **Evidence**: Before/after Jaeger screenshots plus the stated span-count
  comparison for the `checkout` service.
- **Confidence**: settled for the stated demo; not a production benchmark
- **Quote**: "In our example, instead of having clusters of ~14 or 2 spans we can see that the checkout service now has between 51 and 75 spans together:"
- **Our assessment**: The number is useful as evidence that the traces actually
  merged rather than merely appearing adjacent in the UI, and it makes the
  before/after concrete. It is not a cost or latency claim, and the guide should
  not generalize the absolute counts — only the direction: correct propagation
  turns several small orphaned traces into one larger, causally connected trace.

### Claim 8: The application trace and the mesh trace are both useful and neither is sufficient — app spans carry business logic, RPCs, and database spans; mesh spans carry proxy hops, network latency, and retries
- **Evidence**: The post enumerates what each trace half contains after
  describing the split, then states that both are useful and neither is enough.
- **Confidence**: settled (conceptual decomposition backed by the demonstrated
  traces)
- **Quote**: "the application trace, with business logic, RPCs, and database spans"
- **Quote**: "the mesh trace, with proxy hops, network latency, and retries"
- **Quote**: "Both are useful. Neither is enough on its own."
- **Our assessment**: This is the trace analogue of the corpus's mesh-versus-app
  metrics trust split: the network layer has timing and retry detail the app
  cannot see, while the app has semantic detail the proxy cannot see. The guide
  should present unified traces as the mechanism that lets one request carry
  both, rather than treating the two views as competing sources of truth.

### Claim 9: Format mismatch between independently correct components silently breaks trace continuity; a normalization layer is the general fix, and the pattern extends beyond tracing to semantic-convention drift, sampling, cardinality, span metrics, and redaction
- **Evidence**: The final section argues that app, Collector, and backend can all
  be "correct" while traces are still broken because one dependency is not
  configured exactly as the others expect. The authors then list Collector
  responsibilities beyond tracing.
- **Confidence**: emerging (well-argued from the demo, but the extension beyond
  tracing is asserted rather than demonstrated)
- **Quote**: "Applications can be instrumented correctly. The Collector can be running correctly. Jaeger can be receiving data correctly. And the traces can still be broken because one dependency is not configured exactly like the others need it."
- **Quote**: "This pattern extends well beyond tracing. The Collector can handle semantic convention changes, sampling, cardinality control, span metrics generation, information redaction, and export to multiple backends simultaneously."
- **Our assessment**: This is the generalizable lesson and the reason the note
  belongs in the guide rather than only in an Istio runbook. "Correct components,
  broken system" is the defining failure mode of composed observability
  pipelines. The list of other Collector responsibilities is a useful roadmap,
  but only the trace-propagation instance is evidenced here.

### Claim 10: The Envoy OTel tracer behavior is version-sensitive and upstream change "takes time"; the post supplies no Envoy/Istio version pin, so the workaround is a versioned observation rather than an invariant
- **Evidence**: The authors link an Envoy upstream issue comment and explicitly
  say changes take time. Neither the Istio version nor the Envoy version used in
  the demo is stated in the post.
- **Confidence**: emerging (upstream issue linked, but no version matrix or
  reproduction against a named release)
- **Quote**: "In our case, Envoy’s built-in OTel tracer starts a brand-new root span for every request rather than reading the incoming `traceparent`, and changes to that behavior take time (as in every project!)."
- **Our assessment**: The missing version pin is a real gap, not a reason to
  discard the claim. The guide should phrase it as "as of the versions used in
  this 2026 demo" and tell readers to re-check the upstream issue before
  applying the Zipkin-tracer workaround, because a future Envoy release could
  remove the need for the mesh-side half.

### Claim 11: The evidence is demo-scale, not production-validated — the repro is the OpenTelemetry Demo on Istio, with before/after span counts but no production environment, latency, throughput, or cost measurement
- **Evidence**: The post repeatedly says "in the demo" and "in our example" and
  never presents a production deployment, a version matrix, or an operational
  cost measurement. The five screenshots are from Jaeger in the demo.
- **Confidence**: settled (about the source's own scope)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This bounds how the guide should cite the source. The
  propagation mechanism and the two-sided configuration are reproducible and
  worth recording now; the measured span counts and the claim that this is "what
  production systems need" are demo illustrations. The guide should mark the
  recommendation as validated-in-demo and require a production check of trace
  continuity after the change.

## Concrete Artifacts

### Artifact 1: Envoy span export via the Istio `otel-tracing` extension provider (verbatim from the post)

```
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    extensionProviders:
      - name: otel-tracing
        opentelemetry:
          service: otel-collector.otel-demo.svc.cluster.local
          port: 4317
```

The post presents this as necessary but **not sufficient** — it makes Envoy
export spans, yet Envoy still starts a new root span.

### Artifact 2: The mesh-side fix — switch Envoy to the Zipkin tracer (verbatim from the post)

```
enableTracing: true
    defaultConfig:
      tracing:
        zipkin:
          address: otel-collector.otel-demo.svc.cluster.local:9411
```

The fragment is reproduced exactly as rendered in the post, including the
leading `enableTracing: true` line and the indentation of `defaultConfig`; it is
described as an addition to the same `meshConfig`.

### Artifact 3: The app-side fix — add `b3multi` while keeping W3C propagation (verbatim from the post)

```
default:
  envOverrides:
    - name: OTEL_PROPAGATORS
      value: "tracecontext,baggage,b3multi"
```

### Artifact 4: Before/after span counts (as stated in the post)

| State | Spans per request for `checkout` |
|-------|-----------------------------------|
| Before the fix | clusters of ~14 or 2 spans |
| After the fix | between 51 and 75 spans in one trace |

## Cross-References

- **Corroborates**:
  - `source-notes/blog-cncf-otel-mesh-derived-metrics.md` **Claim 2** — that
    note's rule that OTel "can't see traffic that flows between services at the
    network level unless you explicitly instrument both ends" is the metrics-era
    statement of this source's trace-continuity problem. Both sources conclude
    that the mesh and the app must cooperate at the boundary; this one shows the
    header-level mechanism and the exact failure when they do not.
  - `source-notes/blog-cncf-otel-mesh-derived-metrics.md` **Claim 5** — its
    mesh-versus-app trust split (mesh for mTLS identity and east-west success
    rate, app metrics for business semantics, traces for root cause) matches
    this source's Claim 8: app spans carry business logic, proxy spans carry
    network hops and retries, and the unified trace is what makes both usable.
  - `source-notes/blog-cncf-telemetry-that-matters-observability-pipelines.md`
    **Claim 4** — the "observability mesh" argument that metrics point to
    traces and traces embed logs presupposes exactly the trace continuity this
    source is trying to restore; fragmented traces break the cross-signal
    correlation that note treats as the incident-response payoff.
  - `source-notes/blog-cncf-jaeger-ai-agent-tracing-opentelemetry.md` **Claim 2**
    — Jaeger v2 ingests OTLP natively through the OpenTelemetry Collector. This
    source exercises that same collector-based path and adds the multi-format
    (OTLP + Zipkin) receiver requirement the Jaeger note does not discuss.
- **Contradicts**: None. Checked the open `contradiction`-labeled issues; none
  concerns Istio/Envoy, trace propagation, B3, or Zipkin receivers. The
  version-sensitivity caveat in Claim 10 is a gap, not an opposition to another
  note.
- **Extends**:
  - `source-notes/blog-cncf-otel-mesh-derived-metrics.md` — that note covers
    mesh-derived **metrics** in a Linkerd lab; this note covers mesh-derived
    **traces** in an Istio lab. Read together they complete the mesh-signal
    story: metrics need reciprocal app instrumentation to cross the boundary,
    and traces additionally need propagation-format agreement. Same
    Collector-as-integration-point conclusion, different signal.
  - `source-notes/blog-cncf-jaeger-ai-agent-tracing-opentelemetry.md` — Jaeger is
    the backend that visualizes the split, and that note establishes the
    collector-based v2 architecture. This note supplies the upstream producer-
    side prerequisite: for Jaeger to show one trace, Envoy and the app must
    agree on propagation before the spans ever reach it.
  - `source-notes/blog-cncf-operating-opentelemetry-at-scale-opamp.md` — that
    note is the collector-fleet control plane (remote config and health); this
    note is the data-plane consequence of a collector receiving two wire
    formats. A fleet operator using OpAMP would still need this per-pipeline
    receiver and processor configuration.
  - `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md` — that
    note makes the proxy emit an audited span per agent egress request; this
    note shows the boundary condition that determines whether those proxy spans
    join the app trace or become a second orphaned tree. Same "proxy as telemetry
    producer" idiom, different failure mode.
- **Novel**:
  - **Mesh↔app trace-context propagation breakage** — the first corpus note on
    the mechanism by which a correctly instrumented app plus a correctly
    configured Istio mesh produce two trace trees for one request.
  - **The Zipkin-tracer-via-Collector workaround** — Envoy's OTel tracer is the
    problem, not the solution; the mesh-side assembles B3 and the app-side emits
    it, with the Collector's `:9411` Zipkin receiver as the convergence point.
  - **The two-sided propagation contract** — `OTEL_PROPAGATORS` must retain
    `tracecontext,baggage` while adding `b3multi`; either half alone is
    insufficient.
  - **Measured before/after span consolidation** (~14 or 2 → 51–75 spans) as
    concrete evidence that the fix rejoins the trees rather than merely
    enabling more export.
  - **Collector as format-normalizer, not exporter target** — the generalizable
    "correct components, broken system" rule for composed observability.

## Guide Impact

- **Chapter 02 (Observability)**: The "One trace per request" section currently
  describes the single-request trace model only for application/agent spans.
  Add a subsection on **trace continuity across infrastructure hops**: when a
  mesh, gateway, or proxy is inserted, both sides must agree on propagation
  format, or one request silently becomes two trees (Claims 2–3). Use this
  source's two-sided Istio/Envoy recipe as the concrete example (Claims 4–5,
  Artifacts 1–3), and phrase it as an Istio/Envoy-specific, version-sensitive
  workaround (Claim 10) rather than a universal "switch to Zipkin" rule. Pair
  it with the existing "Correlation survives an agent hop only if the hop
  re-sends it" rule: both are the same boundary-propagation failure, one at the
  agent/gateway hop and one at the mesh/sidecar hop.
- **Chapter 02 — Collector/pipeline guidance**: Add the rule that the Collector
  is the normalization layer for multi-format telemetry — OTLP from apps plus
  Zipkin/B3 from Envoy into one pipeline (Claim 6) — and generalize it beyond
  tracing to semantic-convention drift, sampling, cardinality, span-metrics, and
  redaction (Claim 9). Mark the demo-scale evidence boundary (Claim 11) and
  require a post-change check that a known request produces one trace ID across
  the whole path.
- **Chapter 05 (LLM Ops Reliability)**: Use the silent-failure framing (Claim 3,
  Claim 9) for LLM serving stacks that sit behind meshes or gateways: a request
  can succeed while its telemetry is split, so trace-continuity verification
  belongs in the deployment checklist alongside latency and error checks. Keep
  the evidence at demo strength and do not present the specific span counts as
  production expectations.

## Extraction Notes

- **Source was read in full** via WebFetch; it is a single page with no
  substantive sub-pages. The linked upstream Envoy issue
  (`envoyproxy/envoy#30052`) and the OpenTelemetry propagator docs were not
  fetched beyond what the post states; the note deliberately records only the
  post's characterization, not independent verification of current Envoy
  behavior.
- **Quotes**: All `Quote` fields were copied character-for-character from the
  fetched page, including curly apostrophes/quotes and the double space in the
  "In practice,  what you have" fragment. Where the source uses bold or italic
  emphasis (`does extract B3`, `exactly`, `all processed in the same telemetry
  pipeline`) the quote reproduces the words without the markdown emphasis
  markers; no non-adjacent sentences were spliced into a single quote.
- **Candidate list disposition** (`miner-related-notes.md`, read first): all 10
  listed candidates were considered and explicitly dismissed — none carries
  trace-context propagation, B3/Zipkin, Istio/Envoy tracing, or mesh-trace
  content:
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — SLO/gaming operations,
    no tracing-propagation overlap.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — agent security
    platform and policy-as-code; its mesh-free mTLS design is unrelated to trace
    propagation.
  - `docs-promptfoo-model-audit.md` — model scanning CLI, unrelated.
  - `docs-google-sre-reliable-product-launches.md` — launch coordination,
    unrelated.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — change-workflow
    paradigms, not telemetry propagation.
  - `docs-google-sre-prodcast-03-01.md` — general SRE influence/feedback loops,
    no trace-continuity content.
  - `docs-google-sre-prodcast-03-09-profiling-data.md` — profiling as a signal
    type, no mesh or propagation content.
  - `docs-litellm-anthropic-advisor-tool.md` — model-composition billing and
    streaming, unrelated.
  - `docs-litellm-completion-function-call.md` — capability predicates and tool
    injection, unrelated.
  - `docs-litellm-batches-api.md` — batch rate limiting, unrelated.
  Additional cross-references were found by searching `source-notes/` directly
  (the four Corroborates/Extends notes above), as the candidate retrieval did
  not surface the mesh/OTel siblings.
- **Confidence**: `confidence_overall: emerging`. Claim-level mechanics are
  settled-for-demo (reproducible configuration plus before/after traces), but
  the source is a vendor-adjacent single-demo write-up with no Envoy/Istio
  version pin and no production validation; the transferable recommendation is
  therefore emerging until corroborated in a production mesh.
- **No contradiction issue filed.** Per MINER.md §4a, the only tension is
  between the demo-verified workaround and the possibility of future Envoy
  change (Claim 10) — a versioning gap, not two opposing claims. The open
  `contradiction` issue list contains nothing about mesh tracing or propagation.
