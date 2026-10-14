---
source_url: https://www.cncf.io/blog/2026/06/23/building-jaegers-clickhouse-backend-8-6x-compression-on-10-million-spans
source_type: blog-post
title: "Building Jaeger’s ClickHouse backend: 8.6× compression on 10 million spans"
author: Mahad Zaryab (CNCF Jaeger Project Maintainer, Software Engineer at Meta)
date_published: 2026-06-23
date_extracted: 2026-10-14
last_checked: 2026-10-14
status: current
confidence_overall: emerging
issue: "#1700"
---

# Building Jaeger’s ClickHouse backend: 8.6× compression on 10 million spans

> A columnar ClickHouse backend for Jaeger v2 (alpha in v2.18.0) trades primary-key sort order between trace retrieval and multi-dimensional search, achieves 8.6× compression on spans, and uses skip indexes/materialized views to mitigate that trade-off while modeling typed OTel attributes.

## Source Context

- **Type**: blog-post (CNCF maintainer engineering deep-dive)
- **Author credibility**: Mahad Zaryab, Jaeger project maintainer at Meta (not a ClickHouse employee). Post references Jaeger ADR 008 and BENCHMARKING.md, giving concrete provenance.
- **Scope**: Jaeger v2.18.0 ClickHouse storage backend design — schema, primary key trade-offs, attribute modeling, materialized views, benchmark results on a single-node dataset. Does not cover production outage data, dollar-costs, or large-scale operational experience.
- **Maturity note**: ClickHouse backend is explicitly alpha in Jaeger v2.18.0; benchmark figures are presented as context-dependent (single-node, 10M spans / 1M traces).

## Extracted Claims

### Claim 1: Columnar storage suits telemetry workloads due to repetitive values and OLAP design
- **Evidence**: Tracing produces repetitive service/operation names, tag keys, status codes across spans; ClickHouse as OLAP DB supports high-throughput ingest, aggressive compression, fast analytical queries.
- **Confidence**: settled
- **Quote**: "Trace data is repetitive by nature—the same service names, operation names, status codes, and tags appear over and over. A columnar layout thrives on that repetition."
- **Our assessment**: This is a general columnar rationale; the durable value in this source is the concrete schema/trade-offs and measured results, not this framing alone.

### Claim 2: Primary key sort order forces asymmetric trade-off between trace retrieval and filtered search
- **Evidence**: Sort by `trace_id` → GetTrace is contiguous/sequential (fast retrieval) but service/operation filters cannot use primary key index (slow search). Sort by `(service_name, name, start_time)` → search becomes primary-key lookups but trace retrieval is slower. Mitigations recover lost retrieval speed.
- **Confidence**: emerging
- **Quote**: "Trace retrieval was about 27 ms, but a search query took about 880 ms. Re-sorting by (service_name , name , start_time ) pushed trace retrieval to around 100 ms (slower, but still well under interactive thresholds) while bringing multi-filter search down to about 140 ms."
- **Our assessment**: The numbers quantify the asymmetry clearly; they are from the benchmark in this evaluation context and should not be generalized as universal.

### Claim 3: Two mitigations partially recover trace retrieval under search-optimized sort order
- **Evidence**: To offset slower trace retrieval when sorted by `(service_name, name, start_time)`, the design uses (a) a `bloom_filter` skip index on `trace_id` to prove granules cannot contain a given ID without reading them, and (b) a `trace_id_timestamps` materialized view that provides time bounds so GetTrace/GetTraces can prune partitions and granules.
- **Confidence**: emerging
- **Quote**: "A bloom_filter skip index on trace_id, which lets the engine prove a granule can’t contain a given ID without reading it. A trace_id_timestamps materialized view that tells the search path each matching trace’s time bounds, so the follow-up GetTraces call can prune partitions and granules."
- **Our assessment**: These are reusable trace-store design mitigations independent of product marketing.

### Claim 4: Typed attributes require per-primitive Nested columns and metadata mapping
- **Evidence**: OTel v2 uses typed attributes (Bool/Int64/Float64/String and complex types). Schema stores a ClickHouse `Nested` column per primitive type, repeated at five levels (span, event, link, resource, scope). An `attribute_metadata` table populated by materialized views resolves which (type, level, key) combinations exist so filters can target correct columns.
- **Confidence**: emerging
- **Quote**: "The schema leverages ClickHouse’s Nested column per primitive type, repeated at the span, event, link, resource, and scope level... we maintain a dedicated attribute_metadata table, populated by materialized views off the spans table. This allows the reader to look up the filter key at query time and only query the columns for the types and levels that were observed."
- **Our assessment**: Highlights ambiguity in attribute filtering (same key name appearing as different types/levels) — a concrete operational constraint.

### Claim 5: Attribute-only searches cannot fully leverage the primary index
- **Evidence**: Primary index is optimized around top-level structural fields (`service_name`, `name`/operation, `start_time`). Attribute-only searches risk heavy column scans; best practice is to combine attribute filters with structural fields to limit scanned data.
- **Confidence**: emerging
- **Quote**: "Attribute-only searches are inherently more expensive because they cannot fully leverage ClickHouse’s primary index. The table’s index is optimized around top-level structural fields—specifically service , operation , and time . For optimal query performance and to prevent heavy column scans, users should always combine attribute filters with these fields to limit the data ClickHouse has to scan."
- **Our assessment**: Actionable operational guidance for query shape in trace backends.

### Claim 6: Measured compression and throughput on single-node benchmark
- **Evidence**: 10M spans / 1M traces, single-node. Sustained >50k spans/sec ingest, 8.6× compression on spans table, span data reduced from ~6 GiB to ~722 MiB on disk. Trace retrieval ~100 ms, most searches <50 ms, complex filtered queries ~140 ms under the chosen schema.
- **Confidence**: anecdotal
- **Quote**: "The backend sustained more than 50k spans/sec during ingestion, achieved an 8.6× compression ratio on the spans table, and reduced span data by nearly 6 GiB to roughly 722 MiB on disk... Trace retrieval averaged around 100 ms, while most search queries stayed under 50 ms. More complex filtered queries completed in about 140 ms."
- **Our assessment**: Lab/benchmark figures; explicitly context-dependent. Should be treated as indicative, not production generalization.

### Claim 7: Materialized views support auxiliary lookups (services, operations, trace time ranges)
- **Evidence**: Materialized views transform inserts and populate optimized target tables to answer queries not well-served by spans-table sort order (e.g. list of known service names/operations, trace ID timestamp ranges for GetTraces).
- **Confidence**: emerging
- **Quote**: "Rather than answering these with expensive table scans, we use materialized views to precompute the data... This approach is used to speed up queries for service names, operations, and trace ID timestamp ranges."
- **Our assessment**: Standard ClickHouse pattern; its application to trace-store retrieval paths is the interesting detail.

### Claim 8: Maturity caveat — alpha feature in Jaeger v2.18.0
- **Evidence**: Feature is marked alpha at release; full methodology/config/query details in BENCHMARKING.md and design in ADR 008.
- **Confidence**: settled
- **Quote**: "ClickHouse support is available in alpha as a storage backend starting with Jaeger v2.18.0."
- **Our assessment**: Important caveat to prevent overgeneralizing production readiness.

## Concrete Artifacts

```
Primary key trade-off (measured):
- trace_id-sorted schema: trace retrieval ~27 ms; search query ~880 ms
- (service_name, name, start_time)-sorted schema (chosen): trace retrieval ~100 ms; multi-filter search ~140 ms

Mitigations for chosen sort order:
- bloom_filter skip index on trace_id
- trace_id_timestamps materialized view for pruning partitions/granules

Attribute schema:
- Nested columns per primitive type (Bool/Int64/Float64/String) repeated at five levels: span, event, link, resource, scope
- attribute_metadata table populated by materialized views to resolve (type, level, key)

Benchmark (single-node, 10M spans / 1M traces):
- >50k spans/sec ingest
- 8.6× compression on spans table; ~6 GiB → ~722 MiB on disk
- Trace retrieval ~100 ms; most searches <50 ms; complex filtered queries ~140 ms

Maturity: ClickHouse backend alpha in Jaeger v2.18.0; design in ADR 008; methodology in BENCHMARKING.md
```

## Cross-References

- **Corroborates**: None found in existing source-notes corpus (no note covers Jaeger ClickHouse backend, columnar span-store schema, or these specific trade-offs).
- **Contradicts**: None identified.
- **Extends**: None identified (closest notes mention Jaeger only as a sink, e.g. `source-notes/blog-cncf-otel-mesh-derived-metrics.md`, `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md`).
- **Novel**: Primary key sort-order trade-off with concrete asymmetry numbers; combined use of bloom_filter skip index on trace_id + trace_id_timestamps materialized view to recover trace retrieval under search-optimized ordering; five-level typed-attribute storage via per-primitive Nested columns with attribute_metadata mapping for filter resolution; specific single-node benchmark figures (8.6× compression, 50k spans/sec, 6 GiB→722 MiB) for Jaeger ClickHouse backend (alpha).

## Guide Impact

- **Chapter 02 (Observability)**: Add a subsection on trace-storage backend trade-offs covering primary key ordering in columnar trace stores — explicitly state the asymmetry (trace retrieval vs multi-dimensional search), when to prefer search-optimized ordering, and the mitigation set (skip index on trace_id + pruning via trace time-bounds MV). Treat these as design patterns, not product claims.
- **Chapter 02 (Observability)**: Document attribute filtering performance constraint — attribute-only searches cannot leverage the top-level structural index; always co-filter with service/operation/time. Include typed-attribute storage complexity (five levels × per-primitive types) as an operational note.
- **Chapter 02 (Observability)**: Add a short note on retention/cost levers referencing compression (e.g. ~8.6×) and ingest rates as indicative lab results, with maturity caveat (alpha), dataset scope (10M spans/1M traces, single-node), and provenance (maintainer writeup with ADR 008/BENCHMARKING.md). Do not generalize to production dollars.

## Extraction Notes

- Deep-read of CNCF blog post (text extracted). Key figures and exact phrases captured verbatim where appropriate. Post links to Jaeger ADR 008 and BENCHMARKING.md as upstream artifacts; the prose is clear about alpha status and context-dependence.
- Reviewed `miner-related-notes.md` candidates: most unrelated (SRE prodcast topics, launch coordination, etc.). No candidates overlap with trace storage/ClickHouse/Jaeger backend; all others dismissed.
- Verified no existing source note duplicates this URL/topic. Author Mahad Zaryab (Jaeger maintainer, Meta); after 2025-12-01 cutoff but relevant as new implementation detail. Benchmark is single-node lab result — recorded as anecdotal/emerging confidence where appropriate.
