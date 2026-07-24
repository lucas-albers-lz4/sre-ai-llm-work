---
source_url: https://docs.litellm.ai/blog/host-header-auth-bypass
source_type: failure-report
platform: blog
title: "Fixed in 1.84.0+ - Version Update: Authentication Bypass via Host Header Injection (GHSA-4xpc-pv4p-pm3w)"
author: "Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM), Yuneng Jiang (Senior SWE @ LiteLLM)"
date_published: 2026-06-01
date_extracted: 2026-07-24
last_checked: 2026-07-24
status: current
confidence_overall: settled
issue: "#460"
---

# Failure Report: LiteLLM Host Header Authentication Bypass (CVE-2026-49468 / GHSA-4xpc-pv4p-pm3w)

> A crafted `Host` header could make LiteLLM Proxy's auth gate evaluate a different route from the one FastAPI actually dispatched, enabling unauthenticated access to protected management routes under three specific deployment conditions. Fixed in v1.84.0 by deriving the request route from the ASGI scope path instead of the `Host`-reconstructed URL. Linked to the upstream Starlette framework vulnerability CVE-2026-48710 (BadHost).

## Source Context

- **Type**: failure-report (security vulnerability disclosure via vendor blog post)
- **Platform**: Vendor blog post on `docs.litellm.ai/blog` (Docusaurus), co-published with GitHub Security Advisory GHSA-4xpc-pv4p-pm3w (CVE-2026-49468). The upstream framework vulnerability in Starlette (CVE-2026-48710, "BadHost") is also referenced as the root mechanism enabling the attack.
- **Author credibility**: High — authored by Krrish Dholakia (CEO), Ishaan Jaffer (CTO), and Yuneng Jiang (Senior SWE) of LiteLLM/BerriAI. The blog follows LiteLLM's standard disclosure format with clear root-cause description, version ranges, fix and backport information, action items, and mitigations. Discovery was by external security researchers (Le The Thang / KCSC and Kim Ngoc Chung / One Mount Group) through coordinated disclosure.
- **Scope**: A single authentication bypass vulnerability (CWE-290) specific to the LiteLLM Proxy's route-resolution mechanism. The blog post covers the vulnerability mechanism, three-condition impact model, fix (primary + follow-up hardening), version ranges, and stopgap mitigations. It does not cover other security topics or general LiteLLM architecture beyond the auth route-resolution path.

## What Was Attempted

- **Goal**: N/A — this is a proactive security disclosure published by the vendor. The vulnerability is a design flaw in how the LiteLLM Proxy resolved routes for authentication: the auth layer derived the effective route from `request.url.path`, which Starlette reconstructs from the `Host` header, enabling a mismatch between auth-evaluated and dispatched routes.
- **Tool/approach**: LiteLLM Proxy (pip package `litellm`), versions prior to v1.84.0. The auth layer used `litellm/proxy/auth/auth_utils.py::get_request_route()` to determine which route a request targeted, and Starlette's `request.url.path` was the input — a value reconstructed from the client-supplied `Host` header.
- **Setup**: LLM gateway proxy deployment meeting three conditions: running the proxy server (not just the Python SDK), version earlier than v1.84.0, and proxy listener reachable by untrusted clients.

## What Went Wrong

- **Symptoms**: A crafted `Host` header could cause the proxy's authentication gate to evaluate a different route from the one FastAPI actually dispatched, granting potential unauthenticated access to protected management routes. No LiteLLM Cloud customers were affected.
- **Severity**: Critical — CVSS 9.5 (GHSA v4.0) / CVSS 9.8 (NIST v3.1). Remote, unauthenticated, low-complexity. However, exploitation required three specific conditions and upstream Host-validating infrastructure (CDN/WAF, reverse proxy) blocks the bypass in most deployments. CISA ADP rated exploitation as "none" as of June 2026 but "automatable with total technical impact."
- **Reproducibility**: Deterministic — any crafted `Host` header sent to an affected proxy listener with no upstream Host validation could trigger the route/auth desync.

### Vulnerability Detail A: Host-header route-resolution gap causes auth bypass
- **Evidence**: Blog post describes the exact mechanism and code location.
- **Quote**: "The proxy's auth layer derived the effective route from `request.url.path` in `litellm/proxy/auth/auth_utils.py::get_request_route()`, which Starlette reconstructs from the `Host` header. A crafted `Host` header could therefore make the auth gate evaluate a different route from the one FastAPI actually dispatched, causing a protected management route to be treated as public."
- **Confidence**: settled.

### Vulnerability Detail B: The upstream root cause is a Starlette framework vulnerability (CVE-2026-48710)
- **Evidence**: The blog post links to CVE-2026-48710, which NVD confirms is a Starlette vulnerability where "a malformed header could make `request.url.path` differ from the path that was actually requested." The LiteLLM advisory (GHSA-4xpc-pv4p-pm3w, CVE-2026-49468) is the downstream instance of this framework flaw.
- **Confidence**: settled.
- **Our assessment**: This is a case study in supply-chain vulnerability propagation — a framework-level flaw (Starlette's Host-header reconstruction) becomes exploitable in a downstream application (LiteLLM) because the application uses the framework's reconstructed URL for security-critical decisions (auth route resolution). The LiteLLM-specific CVE is properly scoped to the application's usage pattern.

### Vulnerability Detail C: Three-condition impact model limits exploitability
- **Evidence**: Blog post enumerates the conditions explicitly.
- **Quote**: "You are potentially affected only if **all** of the following are true: You run the **LiteLLM proxy server** (not just the Python SDK). You are on a version **earlier than `v1.84.0`**. The proxy listener is reachable by untrusted clients."
- **Confidence**: settled.

### Vulnerability Detail D: Upstream Host-validating infrastructure blocks the bypass in most real-world deployments
- **Evidence**: Blog post and GHSA both describe how CDNs, WAFs, and reverse proxies mitigate the vector.
- **Quote**: "You are **not** remotely open to potential bypass if the proxy listener is not reachable by untrusted clients — for example, it is bound to a private network or sits behind a gateway that requires its own authentication."
- **Confidence**: settled.

### Vulnerability Detail E: Python SDK not affected; only the proxy server
- **Evidence**: Blog post scoping statement.
- **Quote**: "The LiteLLM Python SDK is not affected; only the proxy server is in limited scope."
- **Confidence**: settled.

### Vulnerability Detail F: No LiteLLM Cloud customers were affected
- **Evidence**: Blog post explicitly states this.
- **Quote**: "No LiteLLM Cloud customers were affected. The update was deployed across all LiteLLM Cloud environments - backported to the release lines in use - ahead of this publication."
- **Confidence**: settled.

### Vulnerability Detail G: Three CVSS assessments from different sources
- **Evidence**: NVD and GHSA publish differing scores.
- **Quote (NIST CVSS 3.1)**: "9.8 – AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H — CRITICAL"
- **Quote (GHSA CVSS 4.0)**: "9.5 – CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H — CRITICAL"
- **Quote (Red Hat ADP CVSS 3.1)**: "8.1 – AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H — HIGH"
- **Confidence**: settled.
- **Our assessment**: The score variation (9.8 vs 9.5 vs 8.1) reflects differing assumptions about the Attack Complexity / Attack Requirements. NIST's 9.8 assumes no special conditions (Attack Complexity: Low), GHSA's 9.5 adds Attack Requirements: Present (reflecting the three-condition deployment criteria), and Red Hat's 8.1 uses Attack Complexity: High (reflecting the need for upstream infrastructure bypass). This is a useful real-world example of how CVSS scoring assumptions affect severity ratings — the LiteLLM blog's own framing (three conditions, no Cloud impact) aligns most closely with the GHSA's 9.5 score.

### Vulnerability Detail H: CWE classification — Authentication Bypass by Spoofing (CWE-290)
- **Evidence**: GHSA advisory classifies the weakness.
- **Confidence**: settled.

## Root Cause

- **Author's diagnosis**: The vulnerability is a route-resolution design flaw. `get_request_route()` in `litellm/proxy/auth/auth_utils.py` derived the effective route from `request.url.path`. Starlette reconstructs `request.url.path` from the HTTP `Host` header (per its URL construction logic), which is a client-supplied value. A crafted `Host` header could therefore make the auth gate evaluate a different route from the one FastAPI dispatched, because FastAPI uses its own routing (based on the ASGI scope path) that does not depend on the `Host` header for dispatch decisions.
- **Our assessment**: Agree. The root cause is a semantic gap between two path-resolution mechanisms: (1) Starlette's `request.url.path` (reconstructed from the client-supplied `Host` header per RFC 7230) and (2) FastAPI's ASGI dispatch path (from the server-side `scope["path"]`). The auth layer used path (1) while the dispatch layer used path (2). This is a classic confused-deputy pattern where the wrong path source is used for a security decision. The fix — switching to the ASGI scope path — is architecturally correct because the scope path is set by the ASGI server (e.g., uvicorn) and is not influenced by the `Host` header.
- **Category**: genuine-bug (LiteLLM code defect), but with an important framework-level dimension: the vulnerability relies on Starlette's `request.url.path` reconstruction behavior, which is itself a framework design property that was independently identified as a vulnerability (CVE-2026-48710).

### Root-cause detail A: The specific code location
- **Evidence**: Blog post names the file and function.
- **Quote**: "litellm/proxy/auth/auth_utils.py::get_request_route()"
- **Confidence**: settled.

### Root-cause detail B: Starlette's `request.url.path` reconstruction behavior
- **Evidence**: CVE-2026-48710 confirms that Starlette's `request.url` reconstruction from the `Host` header is the framework-level enabler.
- **Quote (from NVD for CVE-2026-48710)**: "a malformed header could make `request.url.path` differ from the path that was actually requested."
- **Confidence**: settled.

### Root-cause detail C: Fix — derive route from ASGI scope path
- **Evidence**: Blog post describes the fix.
- **Quote**: "The primary update in `v1.84.0` addressed the reported potential for bypass by deriving the request route from the ASGI scope path rather than the `Host`-reconstructed URL."
- **Confidence**: settled.

### Root-cause detail D: Follow-up hardening — audited all route derivations
- **Evidence**: Blog post describes the broader audit.
- **Quote**: "As additional follow-up, we audited every other location in the proxy that derived a route from the request URL and moved them onto the same hardened resolution."
- **Confidence**: settled.

### Root-cause detail E: The gap between scoping of the two CVEs
- **Evidence**: CVE-2026-48710 (Starlette BadHost) is a Medium-severity framework-level vulnerability (CVSS 6.5) about `request.url.path` potentially differing from the requested path. CVE-2026-49468 (LiteLLM) is a Critical downstream instance (CVSS 9.5/9.8) where this framework behavior enables auth bypass.
- **Our assessment**: The LiteLLM advisory correctly links to the upstream Starlette CVE as context. The blog post's `CVE:` reference points to the Starlette CVE (CVE-2026-48710), not the LiteLLM-specific CVE (CVE-2026-49468 from the GHSA). Both are relevant: CVE-2026-48710 is the framework precondition, CVE-2026-49468 is the LiteLLM exploitation instance. This is a notable example of CVE dependency chains in the LLM infrastructure supply chain.

## Recovery Path

- **What they switched to**: Derive the request route from the ASGI scope path instead of `request.url.path`. Primary fix in v1.84.0; follow-up path-handling hardening (auditing all other route-derivation locations) backported across maintained release lines.
- **Action**: Upgrade to v1.84.0 or later (latest release recommended, which includes backported hardening).
- **Workaround**: Place the proxy behind an upstream component that validates or normalizes the `Host` header before forwarding — a CDN or WAF (e.g. Cloudflare), a reverse proxy with explicit `server_name` allowlists (nginx, Caddy, Traefik), a cloud load balancer with host-based routing rules, or restrict network access to the proxy listener. **However** "a reverse proxy that forwards the client `Host` unchanged (e.g. nginx `proxy_set_header Host $host;`) may not comprehensively protect your use from this potential."
- **Credential rotation**: If the proxy was reachable from an untrusted network on an affected version, rotate any API keys created during the exposure window and review management audit logs.
- **Unresolved**: None stated; status is Resolved with fix released and backported across maintained release lines.

### Fix detail A: Version ranges and backport releases
- **Evidence**: Blog post enumerates the fixed versions.
- **Quote**: "The update addressing this Host-header authentication bypass in the LiteLLM proxy shipped in `v1.84.0`, with follow-up path-handling hardening completed and backported across the maintained release lines in `v1.84.3`, `v1.85.2`, `v1.86.2`, and `v1.83.10-stable.patch.3`."
- **Confidence**: settled.

### Fix detail B: The fix is architectural, not a configuration change
- **Evidence**: Blog post states no configuration change is required.
- **Quote**: "Action: upgrade to `v1.84.0` or later. No configuration change is required."
- **Confidence**: settled.

### Fix detail C: Principle — gateway auth must derive routes from server-side dispatch path, not client-supplied headers
- **Evidence**: The fix pattern (ASGI scope path vs Host-reconstructed URL) demonstrates this principle.
- **Quote**: "deriving the request route from the ASGI scope path rather than the `Host`-reconstructed URL"
- **Confidence**: settled.

### Mitigation detail: Edge filtering is a stopgap, not a substitute for upgrading
- **Evidence**: Blog post explicitly warns that infrastructure-level Host validation may not fully mitigate.
- **Quote**: "Treat upgrading as the elimination of any potential for bypass and edge filtering only as a stopgap."
- **Confidence**: settled.

## Concrete Artifacts

**CVE and Advisory references (verbatim from source):**
```
CVE: https://www.cve.org/CVERecord?id=CVE-2026-48710  (Starlette BadHost — framework-level precondition)
GHSA: https://github.com/BerriAI/litellm/security/advisories/GHSA-4xpc-pv4p-pm3w  (LiteLLM-specific advisory, CVE-2026-49468)
```

**Version ranges (verbatim from source):**
```
Addressed in: v1.84.0
Recommended: the latest release; follow-up path-handling hardening was
backported in v1.84.3, v1.85.2, and v1.86.2
Affected: versions earlier than v1.84.0
```

**Three conditions for potential impact (verbatim from source):**
```
You are potentially affected only if all of the following are true:
- You run the LiteLLM proxy server (not just the Python SDK).
- You are on a version earlier than v1.84.0.
- The proxy listener is reachable by untrusted clients.
```

**CVSS scores (from NVD and GHSA, verbatim):**
```
NIST CVSS 3.1: 9.8 – AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H – CRITICAL
GHSA CVSS 4.0: 9.5 – CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H – CRITICAL
Red Hat ADP CVSS 3.1: 8.1 – AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H – HIGH
```

**Action items (verbatim from source):**
```
1. Upgrade to v1.84.0 or later. Upgrading to the latest release is
   recommended, which includes the follow-up hardening backported in
   v1.84.3, v1.85.2, and v1.86.2.
2. If your proxy was reachable from an untrusted network on an affected
   version, rotate any API keys created during the exposure window and
   review your management audit logs for unexpected key, user, or settings
   changes.
```

**Mitigations (verbatim from source):**
```
If you cannot upgrade immediately, to better mitigate the potential for
bypass, we recommend placing the proxy behind an upstream component that
validates or normalizes the Host header before forwarding:
- a CDN or WAF (e.g. Cloudflare),
- a reverse proxy with explicit server_name allowlists (nginx, Caddy, Traefik),
- a cloud load balancer with host-based routing rules,
or otherwise restrict network access to the proxy listener.
```

## Cross-References

- **Corroborates**: None directly — this is the first source note in the corpus covering a Host-header injection or route-resolution authentication bypass in an LLM gateway.

- **Contradicts**: None. No existing source note claims that deriving auth routes from `request.url.path` is safe, or that Host-header validation is unnecessary for LLM gateways.

- **Extends / thematically adjacent**:
  - `failure-litellm-proxy-sql-injection-cve-2026-42208.md` — Same vendor (LiteLLM), different failure class (SQL injection through API key verification). Both are CVE-level security vulnerabilities in LiteLLM Proxy's authentication layer, establishing a pattern of recurring auth/security vulnerabilities in LLM proxy/gateway components. The SQL injection note covers input-sanitization failure in database queries; this note covers route-resolution failure in auth path evaluation. Together they establish the principle that the authentication/authorization path in LLM gateways is a recurring source of critical vulnerabilities.
  - `failure-litellm-wildcard-model-access-desync.md` — Same vendor (LiteLLM), different failure class (stale in-memory state in access control resolution). That note covers a config-reload desync affecting wildcard access rules; this note covers a Host-header injection affecting route-based auth evaluation. Both involve the auth/access-control layer of the same proxy, but through completely different mechanisms.
  - `failure-litellm-guardrail-logging-secret-exposure.md` — Same vendor (LiteLLM), different failure class (credential leak through observability path). This is the fourth distinct LiteLLM failure pattern in the corpus, establishing that LiteLLM Proxy has a pattern of recurring security vulnerabilities across multiple attack surfaces (SQL injection, stale state, observability leaks, Host-header injection).
  - `docs-google-sre-prodcast-04-01-security-sre-intersection.md` — Discusses security–SRE intersection at a principles level. The concept of "security controls must use the same path the request takes" (rather than a reconstituted path) aligns with this failure's lesson about auth route evaluation.
  - `blog-litellm-fastapi-middleware-performance.md` — Discusses FastAPI middleware behavior in LiteLLM; the FastAPI/Starlette stack is the same framework context in which the Host-header reconstruction occurs.

- **Novel**: This is the first source note in the corpus covering:
  1. **Host-header injection / route-resolution auth bypass** in an LLM gateway — a distinct attack class from SQL injection, stale state, or credential leaks.
  2. **The specific mechanism**: Starlette's `request.url.path` reconstructed from the `Host` header, creating a desync between auth-evaluated and dispatched routes.
  3. **The fix pattern**: deriving auth routes from the ASGI scope path instead of the Host-reconstructed URL — an architectural principle for gateway security.
  4. **Framework-level CVE dependency chain**: CVE-2026-48710 (Starlette BadHost, medium severity) enabling CVE-2026-49468 (LiteLLM auth bypass, critical severity) — demonstrating how a framework vulnerability becomes far more severe when a downstream application uses the framework's behavior for security decisions.
  5. **The "edge filtering is a stopgap" principle**: explicit vendor warning that upstream Host normalization (CDN/WAF/reverse proxy) may not comprehensively protect against bypass, with the specific example of nginx `proxy_set_header Host $host;` forwarding the client `Host` unchanged.

## Guide Impact

- **Chapter 04 (Security / LLM Gateway) or Chapter 06 (Security and Trust)**: Add a specific security requirement: "LLM gateway proxies MUST derive the route being accessed for authentication from the server-side dispatch path (e.g., ASGI `scope["path"]`), NOT from any client-supplied header (including `Host`, `X-Forwarded-*`, or `Forwarded`)." Include this failure (GHSA-4xpc-pv4p-pm3w, CVE-2026-49468) as a real-world case study showing how `request.url.path` (reconstructed from the `Host` header by Starlette) creates a desync between auth-evaluated and dispatched routes.

- **Chapter 04 or Chapter 06**: Add a design principle: "Gateway auth route resolution must be derived from the same path that the routing/dispatch layer uses. Any reconstitution of the URL from HTTP headers for security decisions introduces a confused-deputy risk." Reference both CVE-2026-48710 (Starlette framework precondition) and CVE-2026-49468 (LiteLLM exploitation).

- **Chapter 06 (Security and Trust)**: Add the "three-condition impact model" as a diagnostic framework for assessing exposure to similar auth-bypass vulnerabilities in LLM gateways: (1) what component is running, (2) what version, (3) can untrusted clients reach the listener. Reference this note's impact conditions.

- **Chapter 06 (Security and Trust)**: Add a mitigation-grading note: "Upstream Host-validating infrastructure (CDN, WAF, reverse proxy with `server_name` allowlists) reduces exposure to Host-header injection but is not a substitute for fixing the application-level route-resolution gap. Specifically, a reverse proxy that forwards the client `Host` header unchanged (e.g., nginx `proxy_set_header Host $host;`) may not block this bypass class at all." Reference the vendor's explicit warning that "edge filtering only as a stopgap."

- **Chapter 01 (Incident Response) / Ch04 (Oncall)**: Add this vulnerability chain as a case study for supply-chain CVE dependency tracking: a Medium-severity framework CVE (Starlette BadHost, CVSS 6.5) becomes a Critical-severity downstream CVE (LiteLLM auth bypass, CVSS 9.5/9.8). Teams operating LLM infrastructure should monitor framework-level CVEs for their gateway components, not just application-level advisories.

## Extraction Notes

- Source read in full: LiteLLM blog post (2026-06-01), GHSA-4xpc-pv4p-pm3w advisory, and NVD records for both CVE-2026-49468 and CVE-2026-48710. All text extracted from rendered HTML or advisory pages; all quoted passages copied character-for-character from the source.
- The upstream CVE connection is significant: the blog post links to CVE-2026-48710 (Starlette BadHost), not the LiteLLM-specific CVE-2026-49468 from the GHSA. Both are captured in this note because the LiteLLM vulnerability is downstream of the Starlette framework vulnerability — a meaningful supply-chain dependency.
- No sub-pages from the blog post were followed beyond the linked GHSA advisory and the CVE/NVD records for both CVEs. The adjacent blog posts listed in the sidebar are unrelated (model release announcements, other incident reports, product updates).
- No contradiction issue filed: verified against all existing source notes (three LiteLLM failure notes + all others). This vulnerability class (Host-header injection / route-resolution auth bypass) is genuinely uncovered in the corpus. The existing LiteLLM failure notes cover different CVE/incident classes (SQL injection, stale state, credential leaks) — orthogonal failure surfaces in the same vendor's proxy, not contradictions.
- The blog post is a concise disclosure (~2 KB of extractable content) but sufficient for a failure-report source note when combined with the GHSA advisory and CVE/NVD information. No code snippets or configuration examples are present in the blog post itself.
