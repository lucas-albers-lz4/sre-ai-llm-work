---
source_url: https://docs.litellm.ai/blog/guardrail-logging-secret-exposure-incident
source_type: failure-report
platform: blog
title: "Incident Report: Guardrail logging exposed secret headers in spend logs and traces"
author: "LiteLLM Team (BerriAI)"
date_published: 2026-03-18
date_extracted: 2026-07-23
last_checked: 2026-07-23
status: current
confidence_overall: settled
issue: "#438"
---

# Failure Report: LiteLLM guardrail logging path exposed `Authorization` headers in spend logs and OpenTelemetry traces

> An incomplete sanitization gap in LiteLLM's guardrail logging path allowed `secret_fields.raw_headers` (including plaintext `Authorization` API key headers) to propagate to spend logs and OpenTelemetry traces when a custom guardrail returned the full request/data dictionary. This is a distinct failure class: the observability/logging integration itself became a credential leak vector.

## Source Context

- **Platform**: Vendor engineering incident blog published on `docs.litellm.ai/blog`, by the LiteLLM Core Team (BerriAI).
- **Author credibility**: High — vendor-authored incident report with clear root cause, impact conditions, and remediation guidance. LiteLLM is a widely-used open-source LLM gateway/proxy. The report follows the same incident-report format as LiteLLM's other postmortems (wildcard desync, SQL injection CVE).
- **Community response**: None captured on-page (single-vendor self-posted incident report). No comments or community discussion visible on the blog page.

## What Was Attempted

- **Goal**: Provide guardrail response observability by logging custom guardrail outcomes to spend logs (UI) and OpenTelemetry traces, so operators could monitor guardrail behavior alongside LLM calls.
- **Tool/approach**: LiteLLM Proxy with custom guardrails. Guardrail responses were logged through the standard guardrail logging path that feeds spend logs (rendered in the admin UI) and OpenTelemetry span attributes.
- **Setup**: LiteLLM proxy deployment with custom guardrails enabled and guardrail logging active; spend logs and/or OpenTelemetry tracing configured.

## What Went Wrong

- **Symptoms**: When a custom guardrail returned the full LiteLLM request/data dictionary, the guardrail response logged by LiteLLM could include `secret_fields.raw_headers`, containing plaintext `Authorization` headers with API keys or other credentials. This information propagated to:
  - **Spend logs in the LiteLLM UI**: "visible to admins with access to spend-log data"
  - **OpenTelemetry traces**: "guardrail_response could be written as a span attribute on guardrail spans" — "visible to anyone with access to the relevant telemetry backend"
  - **Other downstream observability backends**: any integration consuming guardrail metadata could receive the leaked values
- **Severity**: High — credential exposure to anyone with access to spend logs or telemetry backends, but bounded by three required conditions (see Impact). "LLM calls, proxy routing, and provider execution were not blocked by this bug."
- **Reproducibility**: Deterministic — any custom guardrail that returned the full request/data dict would trigger the exposure through the guardrail logging path.

### Symptom A: Spend logs in the LiteLLM UI exposed request headers
- **Evidence**: Blog post states the propagation path explicitly.
- **Quote**: "guardrail metadata could be included in spend-log payloads rendered in the admin UI"
- **Confidence**: settled.

### Symptom B: OpenTelemetry traces carried secret headers as span attributes
- **Evidence**: Blog post describes the OTEL propagation path.
- **Quote**: "guardrail_response could be written as a span attribute on guardrail spans"
- **Confidence**: settled.

### Symptom C: Only logging/telemetry paths were affected, not request processing
- **Evidence**: Blog post explicitly scopes the impact.
- **Quote**: "LLM calls, proxy routing, and provider execution were not blocked by this bug."
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: "The root cause was incomplete sanitization in the guardrail logging path." When building the payload sent to spend logs and traces, LiteLLM prepared guardrail responses for logging but "did not strip internal request data (such as headers) from them." If a guardrail returned a response containing that data, "it was passed through to the logging and observability systems unchanged."
- **Our assessment**: Agree. The root cause is a sanitization gap at the output boundary of a data pipeline — the guardrail logging path is an internal integration point that failed to apply the same sanitization that other output paths do. The key architectural lesson is that guardrail logging is itself an output path (it writes data to spend logs and OTEL traces) and must be treated with the same security posture as any other API response: strip internal fields (headers, raw request data) before emission. This is a class of vulnerability that manifests when an observability integration is added as a secondary concern rather than designed with the same data-minimization principles as the primary code path.
- **Category**: genuine-bug (LiteLLM code defect), but broadly representative of the "observability path as leak vector" anti-pattern.

### Root-cause detail: Propagation chain
The blog post describes a clear propagation chain:
1. A custom guardrail returns the full request/data dict (or another object containing `secret_fields`)
2. "LiteLLM logged that guardrail response through the standard guardrail logging path"
3. Guardrail metadata appears in spend-log payloads rendered in the admin UI
4. "guardrail_response could be written as a span attribute on guardrail spans" in OpenTelemetry
5. Any integration consuming guardrail metadata receives the leaked values

The report notes that "LiteLLM keeps internal request data (including request headers) for use during the call. That data is not meant to be written to logs or telemetry." The guardrail logging path was the bridge that inadvertently carried this internal data across the boundary.

- **Confidence**: settled.

### Root-cause detail: What was missing (sanitization)
- **Evidence**: Blog post describes the gap and the fix direction.
- **Quote**: "Before the fix, the guardrail logging path did not strip that data before sending it to those systems."
- **Confidence**: settled.

### Root-cause detail: The three impact conditions (all required)
- **Evidence**: Blog post enumerates the conditions explicitly.
- **Quote**: "This issue required all of the following: A custom guardrail returned the full LiteLLM request/data dictionary, or another response object containing secret_fields. LiteLLM logged that guardrail response through the standard guardrail logging path. An operator, admin, or telemetry consumer had access to the resulting logs or traces."
- **Confidence**: settled.

### Root-cause detail: Credential exposure scope
- **Evidence**: Blog post scoping statement.
- **Quote**: "This was a logging and telemetry exposure bug. It did not let callers bypass auth, access other tenants directly, or change model behavior, but it could expose plaintext credentials to people with access to those observability systems."
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: Upgrade to **LiteLLM 1.82.3+** which strips internal request data from guardrail responses before writing to spend logs and OTEL traces.
- **Workaround**: No explicit workaround given beyond upgrading. However, removing custom guardrails that return the full request/data dict would break the propagation chain at condition 1.
- **Unresolved**: None stated; status is Resolved.

### Remediation guidance (verbatim from source)
- "Upgrade to LiteLLM 1.82.3+"
- "If you operated custom guardrails that return the full request/data dict, review whether spend logs or telemetry traces were retained during the affected period"
- "Rotate any credentials that may have appeared in Authorization or other forwarded request headers in those systems"
- "Apply least-privilege access controls to spend-log views and telemetry backends that may contain request-derived metadata"

## Concrete Artifacts

**Incident metadata (verbatim from source):**
```
Date: March 18, 2026
Duration: Unknown
Severity: High
Status: Resolved
```

**Impact conditions (verbatim from source):**
```
This issue required all of the following:
1. A custom guardrail returned the full LiteLLM request/data dictionary,
   or another response object containing secret_fields.
2. LiteLLM logged that guardrail response through the standard guardrail
   logging path.
3. An operator, admin, or telemetry consumer had access to the resulting
   logs or traces.
```

**Exposure surfaces (verbatim from source):**
```
Where leaked data could appear:
- Spend logs / UI responses: guardrail metadata could be included in
  spend-log payloads rendered in the admin UI.
- OpenTelemetry traces: guardrail_response could be written as a span
  attribute on guardrail spans.
- Other downstream observability backends: any integration consuming
  the same guardrail metadata could receive the leaked values.
```

## Extracted Lessons

### Lesson 1: Observability/logging integrations are data-exposure surfaces and must apply the same sanitization as any other output path
- **Evidence**: The guardrail logging path passed internal request data (headers) to spend logs and OTEL traces without stripping sensitive fields. The report states the root cause as "incomplete sanitization in the guardrail logging path."
- **Quote**: "When building the payload that gets sent to spend logs and traces, LiteLLM prepared guardrail responses for logging but did not strip internal request data (such as headers) from them."
- **Confidence**: settled.
- **Actionable as**: Treat every observability/logging integration that receives application-internal data as an output boundary requiring the same sanitization as external API responses. Apply data-minimization (strip headers, raw request bodies, internal fields) before writing to telemetry backends, spend logs, or any observability pipeline. This is especially critical for LLM gateways where the request path carries credentials (API keys in `Authorization` headers).

### Lesson 2: The guardrail-observability path has a built-in tension — making guardrails observable also makes any data they return observable, including data they should not have returned
- **Evidence**: The propagation chain shows that the guardrail's return value was written directly to spend logs and OTEL traces without intermediate sanitization. If the guardrail returned the full request dict (which contains `secret_fields`), that data flowed unchanged into observability.
- **Quote**: "If a guardrail returned the full request payload instead of a minimal result, that internal request data could be included in what was logged."
- **Confidence**: emerging.
- **Actionable as**: When designing guardrail interfaces for LLM gateways, enforce a strict return-type contract: guardrails should return minimal structured results (pass/fail + risk score) rather than the full request/data dictionary. The gateway should validate the guardrail response shape before passing it to the logging path, rejecting oversized responses that could contain internal data.

### Lesson 3: Least-privilege access to observability backends is a security control, not just a cost/compliance measure — telemetry backends that receive guardrail metadata may contain sensitive request data
- **Evidence**: The report recommends "apply least-privilege access controls to spend-log views and telemetry backends that may contain request-derived metadata" as part of its remediation guidance.
- **Quote**: "Apply least-privilege access controls to spend-log views and telemetry backends that may contain request-derived metadata."
- **Confidence**: emerging.
- **Actionable as**: Treat OTEL telemetry backends and spend-log UIs as sensitive-data stores when they receive guardrail metadata, response headers, or any request-derived data. Apply access controls consistent with the sensitivity of the LLM gateway's API keys and credentials. This recommendation from the LiteLLM vendor confirms the principle that observability pipelines should be in-scope for security audits.

### Lesson 4: Credential rotation is the safety net when an observability leak is discovered — but it depends on knowing which credentials were exposed
- **Evidence**: The report recommends rotating "any credentials that may have appeared in Authorization or other forwarded request headers in those systems." This implies the operator must be able to determine which API keys might have been exposed, which depends on correlating spend log / OTEL trace retention periods with the set of credentials used during that window.
- **Quote**: "Rotate any credentials that may have appeared in Authorization or other forwarded request headers in those systems."
- **Confidence**: settled.
- **Actionable as**: Build the capability to determine which API keys or credentials might have transited a compromised observability path. For LLM gateways using per-user or per-team API keys, the blast radius assessment requires cross-referencing the exposure window with the provisioning timeline of each active credential. Automate this correlation rather than relying on manual log review.

## Cross-References

- **Corroborates failures in**:
  - `failure-litellm-proxy-sql-injection-cve-2026-42208.md` — Same vendor (LiteLLM), different failure class. That note covers SQL injection through the API key verification path (CWE-89). This note covers logging-path credential exposure. Both involve LiteLLM Proxy's handling of sensitive authentication data (API keys), making LiteLLM Proxy a recurring security concern in the corpus for credential handling. The credential exposure through observability paths is orthogonal to the injection vulnerability.
  - `failure-litellm-wildcard-model-access-desync.md` — Same vendor (LiteLLM), different failure class. That note covers stale in-memory state in access-control resolution after config reload. This note covers sanitization gaps in the logging path. Both involve data-flow gaps in LiteLLM's internal architecture rather than infrastructure-level issues. Together they establish LiteLLM Proxy as having a pattern of subtle data-flow bugs at integration boundaries (config reload → access resolver; guardrail output → logging path).

- **Contradicts / thematically adjacent**:
  - `docs-langfuse-security-and-guardrails.md` — This Langfuse note discusses guardrail observability/tracing from the perspective of how to instrument guardrails with `@observe()` and make them visible in traces (a positive design pattern). The LiteLLM failure note shows that the same observability path can become a leakage vector if guardrail responses are not sanitized before emission. There is no direct contradiction — the Langfuse note does not claim guardrail logging is automatically safe, and the LiteLLM note does not argue against guardrail observability. Rather, the LiteLLM failure is a caveat that must be applied to the Langfuse pattern: guardrail observability needs sanitization at the logging boundary. **No contradiction issue filed** — these are complementary views (how to observe guardrails vs. what can go wrong), not opposing claims.
  - `docs-datadog-llm-observability.md` — This Datadog note describes an LLM observability product taxonomy (span kinds, traces, evaluations). The LiteLLM failure demonstrates a concrete risk of observability instrumentation: the same instrumentation that provides visibility into LLM gateway behavior can also expose sensitive fields if the instrumentation boundary is not sanitized. No direct contradiction — the Datadog note describes product capabilities; the LiteLLM note provides a failure case that informs how those capabilities should be deployed (with sanitization and access controls).

- **Known issue**: None. This is a vendor-disclosed and fixed bug (v1.82.3+). No known CVE or GHSA is associated with this incident (unlike the SQL injection CVE-2026-42208 which had GHSA-r75f-5x8p-qvmc).

- **Novel**: This is the first source note in the corpus covering:
  1. **Observability path as a credential leak vector** — the concept that an LLM gateway's own logging and telemetry integration can expose sensitive data. The existing Datadog and Langfuse observability notes describe how to instrument LLM systems for observability but do not address the security implications of those instrumentation paths.
  2. **Guardrail output sanitization** as a distinct security boundary — guardrail responses must be treated as untrusted data for logging purposes, because they may carry internal request state.
  3. **Credential exposure through OpenTelemetry span attributes** — the specific mechanism by which `secret_fields.raw_headers` (including `Authorization` headers) becomes an OTEL span attribute. This is a concrete example of the "telemetry data sensitivity" concern that the Datadog and Langfuse observability notes do not address.
  4. The **three-condition impact model** (custom guardrail returning full dict + guardrail logging enabled + access to logs/traces) as a diagnostic framework for assessing exposure risk.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Add a subsection on **observability as an exposure surface** — the insight that logging, telemetry, and spend-tracking integrations are themselves output paths that carry the same risk of credential exposure as API responses. Reference the three-condition impact model as a diagnostic framework. Include the specific anti-pattern: "guardrail responses carrying internal request state (including `secret_fields.raw_headers` with plaintext `Authorization` headers) were written directly to spend logs and OTEL span attributes without sanitization until v1.82.3."

- **Chapter 05 (LLM Ops Reliability — monitoring/observability)**: Add a design requirement for LLM proxy observability pipelines: "All observability integrations (spend logs, OTEL traces, custom backends) MUST sanitize internal request fields (headers, `secret_fields`, raw request data) before emitting data to telemetry sinks." Reference the LiteLLM v1.82.3+ fix as the remediation pattern. Add the recommendation to treat telemetry backends as sensitive-data stores when they may receive request-derived metadata, requiring least-privilege access controls.

- **Chapter 02 (Observability) or Ch04 (Security / LLM Gateway)**: Add the guardrail response as a security boundary in the data-flow diagram for LLM gateway request processing: guardrail output → sanitization gate → logging/telemetry. The un-sanitized path is the failure mode documented here. Show the propagation chain (guardrail → guardrail_response → spend_logs / OTEL span attributes) as the data flow that must be broken by a sanitization step.

- **Chapter 01 (Incident Response)**: Add this incident as a case study for the "observability-path leak" failure class — distinct from injection vulnerabilities and config-reload bugs. The remediation pattern (upgrade + rotate credentials + apply least-privilege access) and the three-condition impact assessment model are useful as a template for incident response documentation.

## Extraction Notes

- Source fetched 2026-07-23 via direct HTTP (Docusaurus blog page). Full article content extracted from rendered HTML. No paywall, no truncation.
- The source is a single-page incident report (~3 KB of extractable content). It is concise but contains all elements needed for a failure-report source note: clear root cause, propagation chain, impact conditions, and remediation guidance. No code snippets, config examples, or session logs are present — the remediation advice is prose-only (upgrade to 1.82.3+, rotate credentials, apply access controls).
- No sub-pages were linked from the incident report, so none were followed. The adjacent blog posts (Security Update: Suspected Supply Chain Incident; Day 0 Support: GPT-5.4-mini and GPT-5.4-nano) are unrelated.
- No contradiction issue filed: the note's claims do not oppose any existing source note. The closest overlap is `docs-langfuse-security-and-guardrails.md` which covers guardrail observability from a positive-design perspective — the LiteLLM failure is a caveat that applies to that pattern, not a contradiction of it. Both can coexist in the guide (instrument guardrails; sanitize before logging).
