---
source_url: https://langfuse.com/docs/compatibility
source_type: docs
title: "Versions & Compatibility — Langfuse"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.; page contributors include Max Deichmann, Marc Klingen)
date_published: n.d. (living documentation; page footer © 2022–2026)
date_extracted: 2026-07-23
last_checked: 2026-07-23
status: current
confidence_overall: settled
issue: "#436"
---

# Versions & Compatibility — Langfuse

> A reference documentation page documenting the version-compatibility relationships between Langfuse server versions (v3, v4), SDK majors (Python v1–v4, JS/TS v1–v5), API endpoints, and deployment models (Cloud, self-hosted OSS v2/v3/v4). Includes the version lifecycle policy, the feature availability matrix comparing Cloud v3 vs v4 and self-hosted v2/v3/v4, deprecation timelines, concrete version constraints per SDK, and the real-time vs delayed OTel data visibility distinction. Essential reading for SREs planning Langfuse upgrades, SDK migrations, or v4 cutover.

## Source Context

- **Type**: documentation (vendor product compatibility reference)
- **Author credibility**: Langfuse is a production LLM-observability platform; this page documents the shipped version-compatibility constraints across its server, SDKs, and APIs. All claims about compatibility, deprecation status, and version requirements are authoritative (settled). The self-hosted sub-page lists two contributors (Max Deichmann, Marc Klingen). First-party documentation maintained alongside the shipped code and release cycle.
- **Scope**: Covers (1) version lifecycle stages and policy, (2) Cloud vs self-hosted deployment differences, (3) GA version table, (4) feature availability matrix for Cloud v3 (deprecated) vs v4 (GA) across Python SDK, JS/TS SDK, OpenTelemetry, REST API, exports/integrations, and evaluations, (5) expanded compat detail sections for each SDK/API combination, (6) the self-hosted feature matrix for OSS v2 (EOL), v3 (deprecated), v4 (GA), (7) deprecated read API replacement mapping, (8) legacy export source deprecation timeline, (9) FAQs covering Cloud and self-hosted upgrade scenarios. Does NOT cover: SDK setup, evaluation methodology, prompt management, datasets, MCP server, or metrics (each has dedicated pages).
- **Sub-pages followed** (per MINER.md §1): The self-hosted versioning and compatibility page at `/self-hosting/upgrade/versioning` was read in full — it contains an expanded feature availability matrix for OSS v2/v3/v4 and the semantic versioning scope policy. The Python v3-to-v4 and JS/TS v4-to-v5 upgrade path pages were noted but not followed — they document specific code migration steps (method renames, config changes) rather than compatibility constraints, and the Prospector triage scope asked for the compatibility matrix.

## Extracted Claims

### Claim 1: The Langfuse compatibility rule is that each server major version aims to support the current and the previous SDK major version of each language
- **Evidence**: Both the main compatibility page and the self-hosted versioning page state this as the explicit compatibility policy. The self-hosted page adds: "We try extremely hard to uphold this rule, but the v4 transition is an exception: it ends support for older SDK majors on a published schedule."
- **Confidence**: settled
- **Quote**: "Each Langfuse server major version aims to support the current and the previous SDK major version of each language."
- **Our assessment**: This is the foundational version-pinning claim of the page. It gives SREs a simple rule for planning upgrades: if you run server v4, SDKs from v4 and v3 are supported; v2 and below are out of support. The self-hosted page confirms the v4 transition is an explicit exception to this rule — it ends support for older SDK majors on a published schedule, which is a harder break than the normal policy would imply. The guide should cite this as the baseline version coupling constraint for self-hosted Langfuse deployments.

### Claim 2: Langfuse v4 breaks backwards compatibility with older SDKs in a way that previous major versions did not
- **Evidence**: The main compatibility page states this explicitly, linking to the Langfuse v4 page for details. The self-hosted page repeats the exception language.
- **Confidence**: settled
- **Quote**: "v4 breaks backwards compatibility with older SDKs; see the Langfuse v4 page for all information."
- **Our assessment**: This is the single most operationally significant claim on the page. Previous Langfuse major versions maintained backward compatibility within the "current + previous SDK major" rule. v4 is an explicit break from that pattern. From the self-hosted matrix, OSS v4 marks Python SDK v2 and JS/TS SDK v3/v2 as "Unsupported" (v3 had them as "Full"). This means any team still running Python SDK ≤ v2 or JS/TS SDK ≤ v3 must upgrade their SDKs before or during the v4 migration — it is not optional. The guide should highlight this as a hard constraint for the v4 migration path.

### Claim 3: Langfuse components move through four lifecycle stages — Preview, GA, Deprecated, and End of Life — with specific operational meanings for each
- **Evidence**: A lifecycle stages table on the main compatibility page defines all four stages with standard meanings. Deprecated means "still works but is superseded; removal is noted in the matrix below." End of life means "unsupported, no security patches."
- **Confidence**: settled
- **Quote**: "Every Langfuse component (server, SDKs, and APIs) moves through these lifecycle stages:" and "Deprecated — Still works but is superseded; removal is noted in the matrix below. Migrate to the replacement." and "End of life — Unsupported, no security patches."
- **Our assessment**: The lifecycle stage definitions are standard for a mature platform but worth documenting because the guide's Ch04 (Tooling) section will reference these terms when describing Langfuse upgrade planning. Note the specific Langfuse convention: "Preview" means "production-ready, but interfaces or API design may still change" — so Previews are deployable but not API-stable. The guide should recommend against building integrations on Preview-stage APIs and should schedule migration work during the Deprecated window.

### Claim 4: On Langfuse Cloud, server versions are managed automatically — only SDK version and API endpoints matter; self-hosted server minimums do not apply
- **Evidence**: The Deployment section of the main compatibility page states this explicitly. Both the Cloud and self-hosted pages explain the deployment model difference: Cloud deploys continuously and runs ahead of self-hosted releases.
- **Confidence**: settled
- **Quote**: "Always runs the latest Langfuse version; server versions are managed for you. Only your SDK version and the API endpoints you call matter; the self-hosted server minimums on this page do not apply. Breaking removals happen on published dates."
- **Our assessment**: This is a critical distinction for the guide's deployment guidance. Cloud users have a significantly simpler upgrade path — they only need to manage SDK versions and migrate away from deprecated endpoints before cutover dates. The "breaking removals happen on published dates" clause means Cloud users get a deprecation window before forced removal. By contrast, self-hosted users control their upgrade timing but must manage server-upgrade risk (Claim 5). The self-hosted page adds that "new capabilities are battle-tested on Langfuse Cloud before they ship in a self-hosted release" — meaning self-hosted users always lag behind Cloud in feature availability.

### Claim 5: Self-hosted Langfuse deployments have a tighter version-coupling model — SDK majors require minimum server versions, breaking removals only happen in major server releases, and Cloud runs ahead of self-hosted releases
- **Evidence**: The Deployment section on both pages. The self-hosted page has an expanded "Compatibility between Langfuse Server and SDKs" section. The self-hosted feature matrix documents per-SDK minimum server versions (Python SDK v4 ≥ 3.63.0, JS/TS SDK v5 ≥ 3.63.0).
- **Confidence**: settled
- **Quote**: "You choose when to upgrade the server. New capabilities are battle-tested on Langfuse Cloud before they ship in a self-hosted release, so Cloud can run ahead of the latest self-hosted version. SDK majors require the minimum server versions in the self-hosted compatibility matrix; breaking removals only happen in major server releases."
- **Our assessment**: The most important operational detail here is the minimum server version per SDK — the self-hosted matrix shows Python SDK v4 and JS/TS SDK v5 both require OSS ≥ 3.63.0. This is a lower bar than the SDK overview note (#302, Claim 11) which documented Python SDK v3 ≥ 3.125.0 and TypeScript SDK v4 ≥ 3.95.0 — those were for older SDK majors. The current SDK majors have a gentler requirement. The guide should reference both sets: v3/v4 SDKs need higher server versions, while v4/v5 SDKs need ≥ 3.63.0.

### Claim 6: On Langfuse Cloud v4, Python SDK v3 and JS/TS SDK v4 continue to work but with a 10-minute data delay in OTel tracing — only Python SDK v4 ≥ 4.7.0 and JS/TS SDK v5 ≥ 5.4.0 get real-time data
- **Evidence**: Multiple sections on the main page — the feature availability matrix "Deprecated" rows, the CompatDetail sections for Python SDK v3, JS/TS SDK v4, and the OpenTelemetry CompatDetail — all document the same delay pattern. The FAQ "My data takes minutes to show up in the UI, why?" confirms it.
- **Confidence**: settled
- **Quote**: "Supported (data delayed up to 10 min; Python SDK v4 ≥ 4.7.0 for real time)" and "Supported (data delayed up to 10 min; JS/TS SDK v5 ≥ 5.4.0 for real time)"
- **Our assessment**: This is a critical operational constraint for SRE debugging workflows. If a team upgrades to Cloud v4 but continues running Python SDK v3 or JS/TS SDK v4 (which are still in the "current + previous" compatibility window), tracing data will be delayed by up to 10 minutes. This makes real-time debugging during incidents unreliable without a matching SDK upgrade. The guide should recommend upgrading SDKs to the GA minor versions listed (≥ 4.7.0 Python, ≥ 5.4.0 JS/TS) before or immediately after the v4 cutover.

### Claim 7: The `x-langfuse-ingestion-version: 4` header is required on non-SDK OTel span exporters for real-time data on Langfuse v4; without it, data can be delayed up to 10 minutes
- **Evidence**: The OpenTelemetry CompatDetail section on both the main and self-hosted pages documents this header requirement. Langfuse SDKs qualify automatically.
- **Confidence**: settled
- **Quote**: "On Langfuse v4, send the x-langfuse-ingestion-version: 4 header on your span exporter to see data in real time; without it, data can be delayed by up to 10 minutes. (Langfuse SDKs qualify for real time automatically.)"
- **Our assessment**: This header requirement is an important implementation detail for any team using custom OTel instrumentation or non-SDK OTel exporters (e.g., OpenTelemetry Collector, OpenTelemetry Lambda Layers, community OTel SDKs). Without this header, even properly instrumented custom exporters will experience the 10-minute delay. The guide should document this header as a required configuration step for any non-SDK OTel ingestion pipeline targeting Langfuse.

### Claim 8: Self-hosted Langfuse deployments can bypass the `x-langfuse-ingestion-version` header requirement by setting `LANGFUSE_MIGRATION_V4_NATIVE_OTEL_BEHAVIOUR=direct`
- **Evidence**: Both the main compatibility page and the self-hosted page document this environment variable in the OpenTelemetry CompatDetail section and the OpenTelemetry feature availability matrix row.
- **Confidence**: settled
- **Quote**: "self-hosted deployments can set LANGFUSE_MIGRATION_V4_NATIVE_OTEL_BEHAVIOUR=direct to make all OTLP ingestion real time without the header."
- **Our assessment**: The `LANGFUSE_MIGRATION_V4_NATIVE_OTEL_BEHAVIOUR=direct` flag is a self-hosted escape hatch. It bypasses the header check entirely, making all OTLP ingestion real time without requiring per-exporter header configuration. This is useful for teams running many OTel exporters that cannot easily add custom headers. The flag name contains "MIGRATION" suggesting it is a temporary compatibility mechanism that may be removed in a future release — the guide should note this and recommend the header approach for long-term setups.

### Claim 9: The legacy batch ingestion API and its endpoints (POST `/api/public/ingestion`, `/traces`, `/spans`, `/generations`, `/events`) are deprecated and not supported on the v4 data model — on Cloud they work until the v4 cutover; on self-hosted v4 they are rejected
- **Evidence**: The Legacy Ingestion API CompatDetail section on both pages documents this. The feature availability matrix shows ingestion as "Full" on Cloud v3 and "Deprecated" on Cloud v4, "Full" on OSS v3 and "Unsupported" on OSS v4.
- **Confidence**: settled
- **Quote**: "Trace, span, and generation events via the legacy batch ingestion API are not supported on the v4 data model: on Langfuse Cloud they keep working until the v4 cutover (date will follow), on self-hosted Langfuse v4 they are rejected."
- **Our assessment**: This is the most impactful deprecation on the page for teams using older SDKs. Python SDK v2 and JS/TS SDK v3 (and older) send traces via the legacy batch ingestion API. On self-hosted OSS v4, these SDKs simply stop working for tracing — there is no grace period. The FAQ explicitly warns: "Python SDK v2 and JS/TS SDK v3 (and older) send traces via the legacy batch ingestion API, which is removed on Langfuse Cloud at the v4 cutover." The guide should flag this as a hard dependency: teams on older SDKs must upgrade before deploying server v4.

### Claim 10: The deprecated read APIs (7 REST endpoints) have explicit replacement mappings — Observations API v2, Scores API v3, Metrics API v2, and Experiments API — organized in a per-endpoint migration table
- **Evidence**: A full replacement mapping table on both pages lists each deprecated GET endpoint and its v4 replacement.
- **Confidence**: settled
- **Quote**: A full table reproduced in Concrete Artifacts.
- **Our assessment**: This is a concrete migration reference. The deprecated read APIs include `/api/public/traces`, `/api/public/observations`, `/api/public/sessions`, `/api/public/scores`, `/api/public/metrics`, `/api/public/datasets/{name}/runs`, and `/api/public/dataset-run-items`. Their replacements all converge on the new Observations API v2, Scores API v3, Metrics API v2, or Experiments API. The guide should reference this table for any code or automation that queries the Langfuse API directly.

### Claim 11: Observations API v2 and Metrics API v2 are GA, require Langfuse v4, and are the default resources in Python SDK v4 and JS/TS SDK v5; on OSS v3 the defaults fail and users must use `api.legacy.*` resources instead
- **Evidence**: The Observations API v2 & Metrics API v2 CompatDetail on both pages documents this behavior.
- **Confidence**: settled
- **Quote**: "Via SDK: these are the default resources in Python SDK v4 (api.observations, api.metrics) and JS/TS SDK v5 (api.observations, api.metrics). On OSS v3, the defaults fail; use api.legacy.observations_v1 / api.legacy.metrics_v1 (Python) or api.legacy.observationsV1 / api.legacy.metricsV1 (JS/TS)."
- **Our assessment**: This is a critical gotcha for self-hosted v3 users who upgrade their SDK to v4/v5 before upgrading their server to v4. The SDK defaults will call v2 API endpoints that don't exist on server v3, causing API failures. The self-hosted FAQ confirms this: "The default api.observations and api.metrics resources call v2 endpoints that require Langfuse v4; use the api.legacy.* resources until you upgrade your server to v4." The guide should document this as a staged migration pattern: upgrade SDK first with `api.legacy.*` fallback, then upgrade server, then switch to default resources.

### Claim 12: Trace-level evaluators are deprecated and not supported on the v4 data model; on Cloud they keep running until the v4 cutover — the replacement is observation-level evaluators
- **Evidence**: Both the feature availability matrix ("Full" on v3, "Deprecated" on v4) and the Trace-level Evaluators CompatDetail section document this. The self-hosted matrix shows trace-level evaluators as "Full" on OSS v3 and "Deprecated" on OSS v4.
- **Confidence**: settled
- **Quote**: "Trace-level evaluators are not supported on the v4 data model; on Langfuse Cloud they keep running until the v4 cutover (date will follow)."
- **Our assessment**: Teams using trace-level evaluators (LLM-as-a-judge or code evaluators attached at the trace level) must migrate them to observation-level evaluators before the v4 cutover. This aligns with the data model shift in v4 (observations-first, traces as a container). The glossary note (#255) and evaluation note (#195) both discuss observation-level evaluation but don't flag the trace-level deprecation — this page is the source for that constraint. The guide's evaluation chapter should recommend observation-level evaluators as the default and reference this deprecation as the reason.

### Claim 13: Legacy export source (traces and observations) is replaced by the enriched observations source on the v4 data model, with specific cutoff dates: projects created on or after 2026-05-20 cannot select legacy sources, new legacy export integrations cannot be created since 2026-06-22, and remaining legacy exports switch automatically at the Cloud v4 cutover
- **Evidence**: The Legacy Export Source CompatDetail on both pages documents this timeline with specific dates. The feature availability matrix shows "Traces & observations" on Cloud v3 and "Enriched observations" on Cloud v4.
- **Confidence**: settled
- **Quote**: "On Langfuse Cloud, projects created on or after 2026-05-20 cannot select legacy sources, new legacy export integrations cannot be created since 2026-06-22, and remaining legacy exports are switched to the enriched source automatically at the Cloud v4 cutover (date will follow)."
- **Our assessment**: This is the most time-sensitive claim on the page — it contains actual deadlines. The 2026-05-20 and 2026-06-22 dates have already passed as of extraction (2026-07-23). Any team still running legacy export integrations should have already migrated; if they haven't, they are on borrowed time until the automatic switch at the v4 cutover. The guide should cite these dates as a concrete example of Langfuse's deprecation timeline.

### Claim 14: Self-hosted OSS v3 supports Python SDK v4 and JS/TS SDK v5 as long as the server is ≥ 3.63.0, but observations and metrics v2 endpoints fail — the `api.legacy.*` workaround is required until the server is upgraded to v4
- **Evidence**: The self-hosted feature matrix shows Python SDK v4 and JS/TS SDK v5 as "≥ 3.63.0" on OSS v3. The FAQ on the main page confirms this scenario. The self-hosted Observations API v2 CompatDetail documents the `api.legacy.*` workaround.
- **Confidence**: settled
- **Quote**: "Tracing, prompt management, datasets, and scores work fully (server ≥ 3.63.0). The default api.observations and api.metrics resources call v2 endpoints that require Langfuse v4; use the api.legacy.* resources until you upgrade your server to v4."
- **Our assessment**: This confirms a supported mixed-version state: self-hosted v3 with current SDK majors is a valid interim configuration. The minimum server version (≥ 3.63.0) is achievable for any team running a mid-to-late v3 release. The `api.legacy.*` workaround is well-documented. This is the guide's recommended staging path for v4 migration: upgrade SDKs first (with legacy API fallback), then upgrade the server.

## Concrete Artifacts

### Deprecated read APIs — replacement mapping (both pages)
Source: langfuse.com/docs/compatibility and langfuse.com/self-hosting/upgrade/versioning — CompatDetail section "Deprecated read APIs."

```
Deprecated GET endpoints                              | Replacement
-------------------------------------------------------|-----------------------------------------------
/api/public/observations, /api/public/observations/{id}  | Observations API v2
/api/public/traces, /api/public/traces/{id}               | Observations API v2, filtered by traceId
/api/public/sessions, /api/public/sessions/{id}          | Observations API v2, filtered by sessionId
/api/public/scores, /api/public/v2/scores (+ /{id})      | Scores API v3
/api/public/metrics, /api/public/metrics/daily            | Metrics API v2
/api/public/datasets/{name}/runs (+ /{runName})           | Experiments API
/api/public/dataset-run-items                             | Experiment Items API
```

### GA versions table (main page)
Source: langfuse.com/docs/compatibility — "GA versions" section.

```
Component     | GA version | Package / repo         | Notes
--------------|------------|------------------------|---------------------------------------------------
Server        | v4         | langfuse/langfuse      | Observations-first data model; v3 continues to receive security patches
Python SDK    | v4         | langfuse               | OpenTelemetry-based since v3. Requires Python 3.9+.
JS/TS SDK     | v5         | @langfuse/*            | OpenTelemetry-based since v4. Requires Node.js 20+.
Other languages| n/a       | OpenTelemetry          | Any OTel SDK to the Langfuse OTel endpoint
```

### Self-hosted feature availability matrix — SDK-to-server minimum versions (self-hosted page)
Source: langfuse.com/self-hosting/upgrade/versioning — "Feature availability matrix" section.

```
Client             | OSS v2 (EOL) | OSS v3 (Deprecated) | OSS v4 (GA) | Status
-------------------|--------------|---------------------|-------------|--------
Python SDK v4      | Unsupported  | ≥ 3.63.0           | Full        | GA
Python SDK v3      | Unsupported  | ≥ 3.63.0           | Deprecated  | Deprecated
Python SDK v2      | Full         | Full                | Unsupported | Deprecated
Python SDK v1      | Full         | Unsupported         | Unsupported | End of life
JS/TS SDK v5       | Unsupported  | ≥ 3.63.0           | Full        | GA
JS/TS SDK v4       | Unsupported  | ≥ 3.63.0           | Deprecated  | Deprecated
JS/TS SDK v3 / v2  | Full         | Full                | Unsupported | Deprecated
JS/TS SDK v1       | Full         | Unsupported         | Unsupported | End of life
OpenTelemetry      | Unsupported  | ≥ 3.22.0           | Full        | GA
Legacy ingestion   | Full         | Full                | Unsupported | Deprecated
Observation v2     | Unsupported  | Unsupported         | Full        | GA
Deprecated read    | Full         | Full                | Unsupported | Deprecated
Trace evaluators   | Full         | Full                | Deprecated  | Deprecated
```

### Key version pinning rules — self-hosted minimum server versions per SDK (self-hosted page)
Source: langfuse.com/self-hosting/upgrade/versioning — SDK detail rows.

```
Python SDK v4 → OSS ≥ 3.63.0
Python SDK v3 → OSS ≥ 3.63.0
JS/TS SDK v5  → OSS ≥ 3.63.0
JS/TS SDK v4  → OSS ≥ 3.63.0
OpenTelemetry OTLP → OSS ≥ 3.22.0
Observation-level evaluators → OSS ≥ 3.153.0
```

### Legacy export source deprecation timeline (main page)
Source: langfuse.com/docs/compatibility — Legacy Export Source CompatDetail.

```
- Projects created on or after 2026-05-20: cannot select legacy sources
- New legacy export integrations created since 2026-06-22: blocked
- Remaining legacy exports: switched automatically at the Cloud v4 cutover
```

## Cross-References

- **Corroborates**:
  - `docs-langfuse-sdk-overview.md` (#302) **Claim 11** (Self-hosted minimum server version requirements for Python SDK v3 ≥ 3.125.0 and TypeScript SDK v4 ≥ 3.95.0). This note documents a broader set of version constraints (including Python SDK v4 ≥ 3.63.0, JS/TS SDK v5 ≥ 3.63.0). The SDK overview's older-SDK version numbers are higher (v3 needs ≥ 3.125.0) than the current-SDK numbers (v4 needs ≥ 3.63.0) — this is not a contradiction, just different SDK generations having different server requirements. Both are settled, factual vendor documentation.
  - `docs-langfuse-roadmap.md` (#320) **Claim 5** (Platform reliability priorities include finishing the v4 rollout). This note documents the v4 cutover mechanics and feature changes in concrete, shipped detail that the roadmap only references directionally.
  - `docs-langfuse-glossary.md` (#255) **Claim 7** ("Langfuse is built on OpenTelemetry"). The v4 data model's OTel-native ingestion (Claim 6–8 in this note) confirms OTel remains the ingestion foundation; the legacy batch API deprecation (Claim 9) reinforces that OTel is the only forward-ingestion path.
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 4** (Observation-level evaluators are the recommended default). This note's Claim 12 (trace-level evaluators deprecated) provides the deprecation rationale for the eval-note's recommendation — trace-level evaluators are not supported on the v4 data model.
  - `docs-datadog-llm-observability.md` (#91) **Claim 3** (SDK upgrades can cause breaking changes). The Langfuse v4 compatibility matrix provides a concrete case study of this pattern: SDK-server version coupling, deprecation windows, and cutover dates.

- **Contradicts**: None. All claims are factual vendor documentation about shipped compatibility constraints. The SDK overview note (#302) has different minimum server versions for different SDK generations (older SDKs need higher server versions), which is a conditioning variable, not a contradiction. No contradiction issue filed.

- **Extends**:
  - `docs-langfuse-sdk-overview.md` (#302). The SDK overview documents SDK setup and three SDK-minimum server versions. This compatibility note extends that with the full cross-product version matrix (Cloud v3/v4, OSS v2/v3/v4, all SDK majors, ingestion paths, read APIs, exports, evaluators), the lifecycle policy, and the v4 transition timeline. Together they form the complete picture for upgrade planning: one note for SDK usage, this note for version constraint management.
  - `docs-langfuse-roadmap.md` (#320). The roadmap documents the v4 rollout as a future priority. This compatibility note documents the shipped result: which features are available on v4, which are deprecated, and what the cutover timeline looks like. The roadmap says "finish the v4 rollout" — this note is the feature matrix of the finished rollout.
  - `docs-langfuse-evaluation-core-concepts.md` (#195). The eval note recommends observation-level evaluators but doesn't explain why trace-level evaluators should be avoided. This note provides the deprecation rationale (Claim 12): trace-level evaluators are not supported on the v4 data model.
  - `docs-langfuse-glossary.md` (#255). The glossary defines the trace/observation model. This note documents which SDK/API versions support which parts of that model in production.

- **Novel** (not present in the corpus before this note):
  - The **compatibility rule** (Claim 1) — the explicit "current + previous SDK major" policy. No prior note documents this version-coupling contract.
  - The **v4 backwards compatibility break** (Claim 2) — explicit vendor confirmation that v4 deviates from the normal compatibility policy.
  - The **lifecycle stage definitions** (Claim 3) — Preview/GA/Deprecated/EOL with Langfuse-specific meanings.
  - The **Cloud vs self-hosted deployment model distinction** (Claims 4–5) — the different upgrade-risk profiles are not documented in any prior note.
  - The **10-minute OTel data delay** (Claim 6) — the real-time vs delayed data visibility constraint for non-GA SDK versions. An operational constraint absent from all prior notes.
  - The **`x-langfuse-ingestion-version: 4` header requirement** (Claim 7) — the specific mechanism for real-time OTel ingestion.
  - The **`LANGFUSE_MIGRATION_V4_NATIVE_OTEL_BEHAVIOUR=direct` self-hosted bypass** (Claim 8).
  - The **legacy batch ingestion API deprecation** (Claim 9) — the full deprecation scope and its hard stop on self-hosted v4.
  - The **deprecated read APIs replacement mapping** (Claim 10, full table in Concrete Artifacts) — 7 deprecated endpoints with exact replacements.
  - The **Observations/Metrics v2 gotcha** (Claim 11) — `api.legacy.*` fallback required on v3. An important migration footgun.
  - The **trace-level evaluator deprecation** (Claim 12) — the specific data-model conflict that makes trace-level evaluators unsupported on v4.
  - The **legacy export source deprecation timeline** (Claim 13) — with concrete dates (2026-05-20, 2026-06-22).
  - The **self-hosted mixed-version staging path** (Claim 14) — OSS v3 + current SDK majors is a supported interim configuration.

## Guide Impact

- **Chapter 02 (Observability / Instrumentation)**: Add four specific updates:
  1. **SDK version requirements for real-time data** — The guide should state that Python SDK ≥ 4.7.0 and JS/TS SDK ≥ 5.4.0 are required for real-time OTel tracing on Langfuse v4 (Claim 6). This updates the instrumentation guidance from #302 which covers SDK setup but not the real-time constraint.
  2. **OTel exporter header requirement** — For custom OTel instrumentation (non-SDK), document the `x-langfuse-ingestion-version: 4` header as a required configuration (Claim 7). The self-hosted `LANGFUSE_MIGRATION_V4_NATIVE_OTEL_BEHAVIOUR=direct` bypass should be noted as a temporary workaround (Claim 8).
  3. **Legacy ingestion API deprecation** — Any instrumentation guidance referencing `POST /api/public/ingestion` or the older per-resource endpoints (`/traces`, `/spans`, `/generations`, `/events`) should be updated to use OTel ingestion (Claim 9).
  4. **On self-hosted v3, use `api.legacy.*`** — For teams running self-hosted v3 with SDK v4/v5, document the `api.legacy.observations_v1` / `api.legacy.observationsV1` fallback pattern (Claim 11, Claim 14).

- **Chapter 04 (Tooling — Platform Engineering)**: This is the highest-value chapter target. Add:
  1. **Version lifecycle policy** — Document the compatibility rule (Claim 1) and lifecycle stages (Claim 3) as the framework for Langfuse version planning.
  2. **Cloud vs self-hosted upgrade calculus** — Document the different upgrade-risk profiles: Cloud teams only manage SDK versions and endpoint deprecations (Claim 4); self-hosted teams manage server upgrades with minimum version constraints per SDK (Claim 5). Include the explicit minimum server versions per SDK from the Concrete Artifacts table.
  3. **v4 migration planning** — Reference the self-hosted staging path (Claim 14): upgrade SDKs first (with `api.legacy.*` fallback), then upgrade the server. Note the v4 backwards compatibility break (Claim 2) means this is a harder cut than prior major upgrades.
  4. **Deprecated read API migration** — Reference the replacement mapping table (Claim 10, Concrete Artifacts) for any code or automation that calls the deprecated endpoints.
  5. **Export source migration** — Note the legacy export deprecation timeline (Claim 13) with the specific cutoff dates already in effect.

- **Chapter 05 (LLM Ops Reliability — Evaluation)**: Add one update:
  1. **Trace-level evaluator deprecation** — Note that trace-level evaluators are deprecated and unsupported on v4 (Claim 12). The evaluation chapter should recommend observation-level evaluators as the default and cite this deprecation as the reason to migrate existing trace-level eval configs.

- **Chapter 06 (Managing the AI Stack — Deployment/Access)**: Add one reference:
  1. **Self-hosted version coupling** — Reference the self-hosted minimum version matrix (Concrete Artifacts) for teams planning self-hosted Langfuse upgrades. The key takeaway: current SDK majors (Python v4, JS/TS v5) require OSS ≥ 3.63.0, older SDK majors require higher versions or are unsupported on v4.

## Extraction Notes

- Source fetched 2026-07-23. The main page (`/docs/compatibility`) and the self-hosted sub-page (`/self-hosting/upgrade/versioning`) were both fetched via `curl` and HTML text extraction (scripts and styles stripped). All quotes are character-for-character from the rendered prose.
- The main page's feature availability matrix is rendered via a `<MatrixTable>` React component with filter buttons (All, Python SDK, JS/TS SDK, OpenTelemetry, REST API, Exports & integrations, Evaluations). The extracted text covers all filter views in a combined form. The CompatDetail expandable sections were programmatically collapsible-only in the static HTML — the text content within them was extracted from the page markup, not from clicking/interacting.
- The self-hosted versioning page was followed per MINER.md §1 (substantive sub-page with its own expanded feature availability matrix and semantic versioning policy). No other linked pages were followed — the upgrade-path pages document code migration steps (method renames, config changes) rather than compatibility constraints, and are outside the Prospector's extraction scope.
- Both pages are living documentation with no stated publication date. The `date_extracted` and `last_checked` are both set to 2026-07-23. The deprecation dates in Claim 13 (2026-05-20, 2026-06-22) are embedded in the page content and may shift; the v4 cutover date is specified as "date will follow" throughout.
- `confidence_overall` is **settled** because the claims are factual vendor documentation about shipped (or explicitly deprecated) compatibility constraints, API endpoint statuses, and version requirements. Unlike the roadmap note (#320), none of these claims are aspirational — they describe the current state of Langfuse's version compatibility as defined by the vendor.
- No contradiction with existing notes was identified (see Contradicts section). No contradiction issue was filed.
