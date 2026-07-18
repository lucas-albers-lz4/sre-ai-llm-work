---
source_url: https://langfuse.com/docs/metrics/overview
source_type: docs
title: "Metrics — Langfuse"
author: "Langfuse (Langfuse GmbH / Finto Technologies Inc.)"
date_published: n.d. (living documentation; current as of 2026-07-18)
date_extracted: 2026-07-18
last_checked: 2026-07-18
status: current
confidence_overall: emerging
issue: "#284"
---

# Metrics — Langfuse

> A vendor-documentation reference for Langfuse's operational metrics layer —
> cost, latency, and volume tracking by dimension (user, session, geography,
> feature, model, prompt version), the Custom Dashboards widget-based query
> interface, and the Metrics API v1/v2 for programmatic access. Fills a gap
> the existing Langfuse corpus doesn't address: cost-attribution by dimension
> and volume-as-a-metric alongside the quality/scores model already captured
> in #195.

## Source Context

- **Type**: documentation (vendor product docs — Langfuse metrics subsystem)
- **Author credibility**: Langfuse is a widely-used open-source LLM observability
  platform. The page is first-party documentation describing the product's metrics
  tracking, dashboards, and API surface. Claims about what the product exposes are
  authoritative for the tool's intended capabilities but are vendor-authored and
  not independently benchmarked.
- **Scope**: Covers (1) the three metric dimensions (quality, cost & latency,
  volume), (2) the four slicing dimensions (trace name, user, tags, release/
  version), (3) Custom Dashboards (widgets, layouts, curated dashboards, JSON
  import/export), (4) Metrics API v2 (endpoint, views, dimensions, metrics,
  constraints, migration from v1), (5) the legacy Metrics API v1 endpoint. Does
  NOT cover: evaluation methodology (see #195), SDK setup (see #302), the Langfuse
  glossary or data model (see #255), pricing, or self-hosting ops.
- **Sub-pages followed**: Two linked pages were read end-to-end to satisfy the
  triage's requirement for concrete API and dashboard reference:
  - **Custom Dashboards** (`/docs/metrics/features/custom-dashboards`) for the
    widget model, query engine, curated dashboards, and JSON portability format.
  - **Metrics API** (`/docs/metrics/features/metrics-api`) for the v2 API
    endpoint specification, views, dimensions/metrics tables, constraints
    (high-cardinality grouping restrictions, row limits), v1→v2 migration
    guidance, and legacy Daily Metrics API.

## Extracted Claims

### Claim 1: Langfuse tracks three categories of metrics — Quality, Cost & Latency, and Volume — with distinct measurement approaches for each
- **Evidence**: The "Metrics & Dimensions" section on the overview page enumerates
  all three categories with definitions for each.
- **Confidence**: settled
- **Quote**: "Quality is measured through user feedback, model-based scoring,
  human-in-the-loop scored samples or custom scores via SDKs/API." / "Cost and
  Latency are accurately measured and broken down by user, session, geography,
  feature, model and prompt version." / "Volume — based on the ingested traces and
  tokens used."
- **Our assessment**: This three-category model (quality / cost & latency / volume)
  is the page's primary structure. Quality measurement via scores is already covered
  in depth by #195 (Claims 2–4, evaluation methods and Score data model). Cost &
  latency and Volume are **new** to the corpus — no existing source note tracks
  Langfuse's cost-by-dimension attribution or volume-as-a-metric. The dimension
  breakdown (user, session, geography, feature, model, prompt version) for cost &
  latency is the most actionable claim on the page.

### Claim 2: Langfuse supports four slicing dimensions for operational metrics — trace name (feature/use-case), user (userId), tags (cross-cutting filters), and release/version (change tracking)
- **Evidence**: The "Dimensions" subsection on the overview page lists all four
  with their intended use.
- **Confidence**: settled
- **Quote**: "Trace name — differentiate between different use cases, features,
  etc. by adding a name field to your traces." / "User — track usage and cost by
  user. Just add a userId to your traces." / "Tags — filter different use cases,
  features, etc. by adding tags to your traces." / "Release and version numbers —
  track how changes to the LLM application affected your metrics."
- **Our assessment**: These four dimensions are the Cartesian axes for slicing any
  metric. Trace name maps to "application/feature," user maps to "tenant/customer,"
  tags are ad-hoc cross-cutting labels, and release/version correlates metrics with
  deploys. This is a concrete dimension model an SRE can adopt for dashboard
  design. The dimensions map onto the Metrics API's dimension fields (see Claims 5
  and 6 for the API-level dimension lists, which are more granular). No existing
  source note documents a dimension-slicing model for observability metrics.

### Claim 3: Custom Dashboards provide a widget-based analytics interface with a flexible query engine supporting multi-level aggregations across traces, observations, users, sessions, and scores
- **Evidence**: The Custom Dashboards sub-page "Key Capabilities" section and the
  "Flexible Query Engine" bullet.
- **Confidence**: settled
- **Quote**: "Create powerful, customizable dashboards to visualize, monitor, and
  share insights from your LLM application data with flexible metrics, rich
  filtering, and dynamic layouts." / "A flexible, self-service analytics solution
  built on a powerful query engine that supports multi-level aggregations."
- **Our assessment**: Custom Dashboards is the primary UI for ad-hoc metric
  exploration in Langfuse. The widget model (data source, metric, dimension,
  filter, chart type) is a standard analytics-dashboard pattern. The "multi-level
  aggregations" capability — aggregating at trace, user, or session level — is the
  key differentiator from a simple time-series view: it lets an SRE ask "what is
  the cost per user across all traces this week" rather than just "what is the
  average trace cost." The page also documents a widget-example architecture: each
  widget has a Data Source (traces, observations, or evaluation scores), Metrics
  (count, latency, cost, scores, etc.), Dimensions (group by user, model, time,
  trace name, etc.), Filters, and Chart Type.

### Claim 4: Langfuse provides three pre-built curated dashboards — Latency, Cost, and Usage — that are editable and duplicable as a starting point for custom monitoring
- **Evidence**: The Custom Dashboards sub-page "Leverage Curated Dashboards"
  section.
- **Confidence**: settled
- **Quote**: "Langfuse Curated Dashboards: Pre-built dashboards focused on Latency,
  Cost, and Langfuse usage" / "Langfuse-managed dashboards and widgets keep all of
  their edit controls (drag, resize, delete, add, and edit)."
- **Our assessment**: The curated dashboards provide a ready-made starting point.
  The page notes that the first edit creates a project-local copy, leaving the
  original untouched — this is a careful design that prevents accidental
  overwrites. The three focus areas (latency, cost, usage) mirror the three metric
  categories from the overview page. The project Home page also functions as a
  dashboard with a "Set as default" that applies to everyone in the project
  (requiring confirmation), making it a shared team monitoring surface.

### Claim 5: Metrics API v2 (GET /api/public/v2/metrics) provides programmatic access to observation-level, numeric-score, and categorical-score views with significant performance improvements over v1
- **Evidence**: The Metrics API sub-page "Metrics API v2" section and the endpoint
  description.
- **Confidence**: settled
- **Quote**: "The v2 API provides significant performance improvements through an
  optimized data architecture built on a new events table schema that minimizes
  database work per query."
- **Our assessment**: The v2 API is the recommended path for all new integrations.
  It offers three views (`observations`, `scores-numeric`, `scores-categorical`)
  with a richer set of dimensions and metrics than v1. The "traces" view was
  deliberately removed in v2 — the `observations` view is both faster and more
  powerful, and trace-level aggregations can be achieved via trace-level dimensions
  within the observations view (e.g., `traceName`, `traceRelease`, `traceVersion`).
  This is a concrete API reference for the guide's Ch05 monitoring chapter.

### Claim 6: Metrics API v2 enforces two important constraints — high-cardinality dimensions (id, traceId, userId, sessionId) cannot be used for grouping (only for filtering), and row limit is max 1,000 rows per query (default 100)
- **Evidence**: The Metrics API v2 page explicitly states both constraints.
- **Confidence**: settled
- **Quote**: "Dimensions like id, traceId, userId, and sessionId cannot be used
  for grouping in the v2 Metrics API" / "Grouping by these high cardinality
  fields is extremely expensive and rarely useful in practice" / "The v2 API
  enforces a default config.row_limit of 100 rows per query to ensure consistent
  performance. You can specify a custom config.row_limit up to a maximum of 1,000
  rows."
- **Our assessment**: These constraints are important operational details for
  anyone building an automated reporting pipeline on top of the Metrics API. The
  high-cardinality restriction means that per-user or per-trace aggregations
  require client-side grouping after fetching from the Observations API v2 rather
  than the Metrics API. The 1,000-row maximum means pagination or time-chunked
  queries are needed for large-scale analytics. The page explicitly recommends
  using the Observations API v2 when row-level span/generation/event data is
  needed instead of aggregate metrics.

### Claim 7: The v2 Observations view supports a rich set of grouping dimensions — traceName, environment, type, name, providedModelName, promptName, promptVersion, userId, sessionId, traceRelease, traceVersion, scoreName — and metrics including count, latency, totalTokens, totalCost, timeToFirstToken, and countScores
- **Evidence**: The Metrics API v2 page "Available Views" table and the subsequent
  "Observation Dimensions" and "Observation Metrics" tables (documented under the
  v1 data model but carried forward with the same fields in v2).
- **Confidence**: settled
- **Quote**: "Query observation-level data with optional trace-level aggregations"
  (for the `observations` view description).
- **Our assessment**: The dimension/metric matrix for observations is the most
  concrete reference material on the page. The `totalCost` metric is Langfuse's
  cost-attribution mechanism — it accounts costs per observation based on the
  associated model definition's token-to-cost mapping. The `timeToFirstToken`
  metric is a generation-specific latency signal not present in many observability
  tools. The dimension set (promptName, promptVersion, providedModelName, etc.)
  directly supports the slicing model described in Claim 2. Aggregation functions
  include sum, avg, count, max, min, p50, p75, p90, p95, p99.

### Claim 8: The legacy Metrics API v1 (GET /api/public/metrics) still supports a traces view with trace-level dimensions (name, tags, userId, sessionId, release, version, environment) and metrics (count, observationsCount, scoresCount, latency, totalTokens, totalCost), but is less performant and not recommended for new usage
- **Evidence**: The Metrics API sub-page "Legacy Metrics API v1" section with the
  full traces-view dimension and metric tables and the explicit deprecation
  guidance.
- **Confidence**: settled
- **Quote**: "The v1 API remains available, but is not recommended as the default
  for new aggregate data extraction workflows because it's less performant at
  scale."
- **Our assessment**: The v1 trace-level view is still useful for backwards
  compatibility and for existing dashboards that depend on trace-level aggregates.
  The trace-level dimensions (name, tags, userId, sessionId, release, version,
  environment) and metrics (count, observationsCount, scoresCount, latency,
  totalTokens, totalCost) are a superset of what was described in Claim 2 and
  include additional query-time filters (`observationName`, `scoreName`). The page
  provides explicit migration steps: replace the endpoint URL, replace `view:
  "traces"` with `view: "observations"`, use trace-level dimensions, adjust
  metrics from trace-level to observation-level calculations, and set explicit
  `config.row_limit`.

### Claim 9: Dashboards and widgets are portable across Langfuse projects and instances via a versioned JSON export/import format — widgets carry a `$langfuseWidget` marker and inlined dashboard references
- **Evidence**: The Custom Dashboards sub-page "Managing and Sharing Widgets"
  section.
- **Confidence**: settled
- **Quote**: "A widget carries {'$langfuseWidget': true, 'version': 1}, and a
  dashboard carries a matching $langfuseDashboard envelope with each referenced
  widget's config inlined, so it travels without database IDs."
- **Our assessment**: The JSON portability format is a notable engineering detail —
  it means dashboards are version-controlled artifacts, not database-bound UIs.
  The "copy widget to clipboard / paste onto any dashboard" pattern (multiplatform
  paste with Cmd/Ctrl+V) and the drag-a-JSON-file-to-import workflow are both
  documented. The Download JSON and import-via-drag operations make it possible to
  version-control dashboard configurations in Git alongside code. This is directly
  relevant to Ch05's monitoring infrastructure guidance.

### Claim 10: Data from older SDKs (Python < v4.0.0, JS/TS < v5.0.0) or OTEL exporters without the `x-langfuse-ingestion-version: 4` header can be delayed by up to 10 minutes on v2 endpoints
- **Evidence**: The Metrics API v2 page "Data Availability" note.
- **Confidence**: settled
- **Quote**: "Data from older SDKs (langfuse-python < 4.0.0, langfuse-js < 5.0.0)
  or direct OpenTelemetry exporters that don't send x-langfuse-ingestion-version: 4
  can be delayed by up to 10 minutes on v2 endpoints."
- **Our assessment**: This is a critical operational detail. The v2 API's
  performance improvements depend on the new events-table schema, which requires
  the v4 ingestion header. Teams using older SDKs or custom OTEL exporters will
  see stale data on v2 endpoints. The page recommends upgrading to Python SDK
  v4.7.0+ or JS/TS SDK v5.4.0+, or setting the header on the OTEL span exporter,
  for real-time data. Relevant to Ch05 for any monitoring/alerting pipeline built
  on the Metrics API.

### Claim 11: The Daily Metrics API (GET /api/public/metrics/daily) is a legacy endpoint for aggregated daily cost and usage timeseries, filterable by traceName, userId, and tags, but is no longer listed in the public API reference
- **Evidence**: The Metrics API sub-page "Daily Metrics API" section.
- **Confidence**: settled
- **Quote**: "This endpoint is no longer listed in the public API reference. It
  remains available for backward compatibility, but for new use cases please use
  the Metrics API v2 above."
- **Our assessment**: The Daily Metrics API is an older endpoint that returns a
  daily timeseries of cost, trace/observation counts, and model breakdowns. It
  is documented primarily for migration reference — new work should use v2. The
  example response shows the data shape: per-day cost, counts, and a per-model
  usage sub-array with input/output token breakdowns. This is the least important
  claim on the page; recorded for completeness since it is documented in the same
  source.

## Concrete Artifacts

### Metrics API v2 — query example (bash curl from the Metrics API page)
```bash
curl \
  -H "Authorization: Basic <BASIC AUTH HEADER>" \
  -G \
  --data-urlencode 'query={
    "view": "observations",
    "metrics": [{"measure": "totalCost", "aggregation": "sum"}],
    "dimensions": [{"field": "providedModelName"}],
    "filters": [],
    "fromTimestamp": "2025-12-01T00:00:00Z",
    "toTimestamp": "2025-12-16T00:00:00Z",
    "orderBy": [{"field": "sum_totalCost", "direction": "desc"}],
    "config": {"row_limit": 1000}
  }' \
  https://cloud.langfuse.com/api/public/v2/metrics
```
Source: langfuse.com/docs/metrics/features/metrics-api (Metrics API v2 section, curl
code block verbatim).

### v2 Query object structure (from the Metrics API page)
```
Field          | Type   | Required | Description
---------------+--------+----------+---------------------------------------------------
view           | string | Yes      | "observations", "scores-numeric", "scores-categorical"
dimensions     | array  | No       | Array of dimension objects to group by
metrics        | array  | Yes      | Array of metric objects to calculate
filters        | array  | No       | Array of filter objects to narrow results
timeDimension  | object | No       | Configuration for time-based analysis (granularity: hour/day/week/month/auto)
fromTimestamp  | string | Yes      | ISO timestamp for the start of the query period
toTimestamp    | string | Yes      | ISO timestamp for the end of the query period
orderBy        | array  | No       | Specification for result ordering
config         | object | No       | Configuration (e.g., row_limit)
```
Source: langfuse.com/docs/metrics/features/metrics-api (Legacy Metrics API v1 section,
query object structure table — pattern carried forward into v2).

### v2 Observations dimensions (from the Metrics API page)
```
Dimension          | Type     | Description
-------------------+----------+---------------------------------------------------
traceName          | string   | Name of the parent trace
environment        | string   | Environment (e.g., production, staging)
type               | string   | Observation type
name               | string   | Observation name
level              | string   | Log level
version            | string   | Version
providedModelName  | string   | Model name
promptName         | string   | Prompt name
promptVersion      | string   | Prompt version
userId             | string   | User ID from parent trace
sessionId          | string   | Session ID from parent trace
traceRelease       | string   | Release from parent trace
traceVersion       | string   | Version from parent trace
scoreName          | string   | Related score name
```
Source: langfuse.com/docs/metrics/features/metrics-api (Observation Dimensions table
from Legacy v1 section, valid for v2 observations view).

### v2 Observations metrics (from the Metrics API page)
```
Metric            | Description
------------------+---------------------------------------------------
count             | Count of observations
latency           | Observation duration in milliseconds
totalTokens       | Total tokens used
totalCost         | Total cost
timeToFirstToken  | Time to first token in milliseconds
countScores       | Count of related scores
```
Aggregation types: sum, avg, count, max, min, p50, p75, p90, p95, p99.
Source: langfuse.com/docs/metrics/features/metrics-api (Observation Metrics table
from Legacy v1 section, valid for v2 observations view).

### Legacy Daily Metrics API response example (verbatim)
```json
{
  "data": [
    {
      "date": "2024-02-18",
      "countTraces": 1500,
      "countObservations": 3000,
      "totalCost": 102.19,
      "usage": [
        {
          "model": "llama2",
          "inputUsage": 1200,
          "outputUsage": 1300,
          "totalUsage": 2500,
          "countTraces": 1000,
          "countObservations": 2000,
          "totalCost": 50.19
        },
        {
          "model": "gpt-4",
          "inputUsage": 500,
          "outputUsage": 550,
          "totalUsage": 1050,
          "countTraces": 500,
          "countObservations": 1000,
          "totalCost": 52.0
        }
      ]
    }
  ]
}
```
Source: langfuse.com/docs/metrics/features/metrics-api (Daily Metrics API section,
response example verbatim). Truncated to one day and response fields for brevity;
the full response includes a `meta` block with page/limit/totalItems/totalPages.

### v1 → v2 migration steps (verbatim from Metrics API page)
1. "Replace GET /api/public/metrics with GET /api/public/v2/metrics."
2. "Replace view: 'traces' with view: 'observations' and use trace-level
   dimensions such as traceName, traceRelease, or traceVersion where supported.
   userId and sessionId remain available as filters, but cannot be used for
   grouping in v2."
3. "Review the metrics array when migrating trace-view queries. In v2's
   observations view, measures like count, latency, totalCost, and totalTokens
   are calculated over observation rows. Use the Observations API v2 and group
   by traceId client-side when you need trace-level counts or trace durations."
4. "Set config.row_limit explicitly when migrating queries that should return
   more than the default 100 rows."
5. "Use Observations API v2 instead if you need row-level spans, generations,
   or events."
Source: langfuse.com/docs/metrics/features/metrics-api (Legacy Metrics API v1 section,
migration guidance — verbatim).

### Widget/Dashboard JSON portable format specification (verbatim from Custom Dashboards page)
> "A widget carries {'$langfuseWidget': true, 'version': 1}, and a dashboard
> carries a matching $langfuseDashboard envelope with each referenced widget's
> config inlined, so it travels without database IDs."
Source: langfuse.com/docs/metrics/features/custom-dashboards (Managing and Sharing
Widgets section, verbatim).

## Cross-References

- **Corroborates**:
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 2** (Scores are
    Langfuse's universal data object for evaluation results) and **Claim 3** (Score
    data model with four types). The Metrics overview page states that "Quality is
    measured through user feedback, model-based scoring, human-in-the-loop scored
    samples or custom scores via SDKs/API" — the same measurement methods #195
    documents at depth. The scores-numeric and scores-categorical views in Metrics
    API v2 (this note, Claim 5) are the API-level instantiation of #195's Score
    data model. No contradiction.
  - `docs-langfuse-glossary.md` (#255) **Claim 1** (Session ⊃ Trace ⊃ Observation
    hierarchy). The Metrics API dimension set (traceName, userId, sessionId,
    traceRelease, traceVersion — this note, Claims 6–7 and Concrete Artifacts)
    operates within the same containment hierarchy. The glossary mentions "Custom
    Dashboards" and "Metrics API" as glossary terms; this note provides the
    substantive mechanism behind those entries.
  - `docs-langfuse-sdk-overview.md` (#302) **Claim 7** (singleton client pattern
    and credential setup). SDK instrumentation is the prerequisite for any data to
    exist in the Metrics API — this note's API reference assumes data is already
    flowing through the SDK (#302). The SDK version requirements for v2 real-time
    data (Claim 10 here) directly link to SDK versions documented in #302.

- **Extends**:
  - `docs-langfuse-glossary.md` (#255). The glossary lists "Custom Dashboards" and
    "Metrics API" as terms with one-line definitions. This note extends those
    definitions with the full query interface, widget model, curated dashboards,
    JSON portability format, and the Metrics API v2/v1 endpoint specification
    including all dimension/metric tables.
  - `docs-langfuse-evaluation-core-concepts.md` (#195). That note covers quality
    metrics (scores) in depth. This note adds the operational metrics — cost &
    latency (broken down by seven dimensions) and volume (traces and tokens) —
    that complete the quality/cost/latency/volume triangle. The Metrics API's
    `scores-numeric` and `scores-categorical` views (this note, Claim 5) are the
    API surface for querying the Score data model #195 defines.
  - `docs-datadog-llm-observability.md` (#91) **Claim 5** (out-of-the-box
    operational dashboards for cost, latency, performance, and usage). Langfuse's
    curated dashboards (Latency, Cost, Usage — this note, Claim 4) fill the same
    role. The Custom Dashboards widget model (Claim 3) goes further by offering
    a self-service query engine, whereas Datadog's offering is described as
    out-of-the-box dashboards. Both vendors expose cost as a first-class
    operational metric alongside latency. Directionally aligned.

- **Novel** (first appearances in the corpus):
  - **Cost-attribution by dimension** — cost broken down by user, session,
    geography, feature, model, and prompt version (Claim 1). No existing source
    note tracks this dimension model.
  - **Volume as a first-class metric** — defined as "ingested traces and tokens
    used" (Claim 1). No existing note defines volume this way.
  - **The four-slicing-dimension model** (trace name, user, tags, release/version)
    for metric breakdown (Claim 2).
  - **Custom Dashboards widget model** — the data source → metric → dimension →
    filter → chart type architecture, multi-level aggregations, and curated
    dashboards (Claims 3–4).
  - **JSON dashboard portability** — versioned JSON format with `$langfuseWidget`
    / `$langfuseDashboard` markers for Git-versioned dashboard configs (Claim 9).
  - **Metrics API v2 specification** — the full endpoint, views, dimension/metric
    tables, aggregation types (p50/p75/p90/p95/p99, sum, avg, count, max, min),
    constraints (high-cardinality grouping restrictions, row limits), and v1→v2
    migration steps (Claims 5–8, Concrete Artifacts).
  - **SDK version → API latency coupling** — the 10-minute delay on v2 endpoints
    for data from older SDKs without the `x-langfuse-ingestion-version: 4`
    ingestion header (Claim 10).

- **Contradicts**: None. All overlapping sources (the Langfuse evaluation note #195,
  glossary #255, and SDK overview #302) are complementary and consistent. The
  Metrics API v2 removes the `traces` view that v1 offered (Claim 8), but this is
  a version change within the same product, not a contradiction — the migration
  guidance is documented. No contradiction issue filed.

## Guide Impact

- **Chapter 02 (Observability)**: This source provides the cost/latency/volume
  operational-metrics side of observability, complementing the quality/eval side
  already covered by #195. Specific additions:
  1. **Cost-attribution by dimension** (Claim 1) — add the dimension model
     (user, session, geography, feature, model, prompt version) as the recommended
     way to instrument cost tracking in LLM applications. This is directly relevant
     to Ch02's observability pillar and to any SRE needing cost breakdown across
     tenants, models, or features.
  2. **The four slicing dimensions** (Claim 2) — add trace name, user, tags, and
     release/version as the canonical axes for metric breakdown. This is the
     practical dimension model for dashboard design.
  3. **Volume tracking** (Claim 1) — add trace/ingestion volume as a base metric
     alongside cost and latency, useful for capacity planning and usage monitoring.
  4. **Custom Dashboards** (Claims 3–4) — reference as the recommended UI for
     ad-hoc metric exploration. The curated Latency/Cost/Usage dashboards are
     ready-made starting points. The JSON portability format (Claim 9) is worth
     noting for version-controlled dashboard-as-code practices.

- **Chapter 05 (LLM Ops Reliability — monitoring and alerting)**: This is the
  highest-impact chapter. The Metrics API v2 specification (Claims 5–8) provides
  the concrete query interface for building automated monitoring, reporting, and
  alerting pipelines:
  1. **Metrics API v2 as the alerting backend** (Claim 5) — use the `observations`
     view with `totalCost`, `latency`, `totalTokens`, and `timeToFirstToken`
     metrics in automated monitoring. The aggregation types (p50/p75/p90/p95/p99)
     are directly usable for SLO-based alerting on latency percentiles.
  2. **High-cardinality constraint awareness** (Claim 6) — note that per-user
     grouping is not possible via the Metrics API; client-side grouping via the
     Observations API is required. Document this in the monitoring pipeline design
     so teams don't design around a capability the API doesn't have.
  3. **Row-limit planning** (Claim 6) — the 1,000-row max means pagination or
     time-chunked queries are needed for large-scale analytics. Document the
     `config.row_limit` parameter and the default of 100 rows.
  4. **SDK latency coupling** (Claim 10) — add a note that the Metrics API v2
     requires SDK v4.7.0+ (Python) / v5.4.0+ (JS/TS) or the `x-langfuse-ingestion-
     version: 4` header for real-time data; older SDKs incur a 10-minute delay.
  5. **v1→v2 migration** (Claims 7–8, Concrete Artifacts migration steps) — if
     the guide references the Metrics API at all, point to v2 and document the key
     migration differences (no traces view, observation-level measures, explicit
     row_limit, high-cardinality grouping restrictions).
  6. **Daily cost reporting** (Claim 11) — the legacy Daily Metrics endpoint is
     documented as a reference for existing integrations; new work should use v2.

- **Chapter 04 (Tooling — Langfuse as an integration)**: Reference the Custom
  Dashboards widget model (Claim 3) and the Metrics API v2 endpoint (Claims 5–6)
  as the two interfaces for Langfuse integration — UI for human analysts, API for
  automated pipelines. The JSON dashboard portability (Claim 9) enables
  dashboard-as-code practices.

## Extraction Notes

- Source fetched 2026-07-18 via WebFetch (three pages: the overview page plus the
  Custom Dashboards and Metrics API sub-pages). All three render server-side and
  were fully readable. Quotes are copied character-for-character from the extracted
  prose.
- The Metrics API page documents both v2 (current, recommended) and v1 (legacy)
  endpoints. Both are extracted because the v1 documentation is the most complete
  source for the dimension/metric tables (the v2 page references the API reference
  for full parameter lists but includes the same dimension/metric sets). The v1→v2
  migration guidance is extracted as a verbatim artifact.
- The Custom Dashboards page also references an embedded YouTube demo video
  (z6g9xmciaBE, "Custom Dashboard Demo") which was noted but not watched —
  the page text suffices for extraction.
- `confidence_overall` is set to **emerging** (not settled) because while the API
  surface, endpoint specifications, and dimension tables are factual vendor
  documentation, the *operational usefulness* of the cost-attribution model and
  the dashboard patterns for production SRE teams is untested in this source —
  that would require practitioner validation (PagerDuty, etc.) or at least a
  real-world deployment report. The confidence is higher than the evaluation note
  (#195 rated emerging for the same reason) because the API tables and constraint
  documentation are factual reference material; the pattern-level claims (Claims 1,
  2, 3, 4) are still emerging.
- No part of the source was paywalled; all pages are publicly accessible.
- No contradiction with existing source notes was found. The removal of the
  `traces` view in v2 is a version change within the same product, not a
  contradiction with any external source. No contradiction issue filed.
