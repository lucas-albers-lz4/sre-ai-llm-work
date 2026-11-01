---
source_url: https://www.cncf.io/blog/2026/08/03/cortex-completes-ostif-security-audit
source_type: blog-post
title: "Cortex Security Audit Results — multi-tenant isolation and cluster operations (Quarkslab / OSTIF)"
author: "Daniel Blando (Cortex maintainer); audit by Quarkslab, coordinated by OSTIF"
date_published: 2026-08-03
date_extracted: 2026-11-01
last_checked: 2026-11-01
status: current
confidence_overall: emerging
issue: "#1929"
---

# Cortex Security Audit Results — multi-tenant isolation and cluster operations

> An OSTIF-coordinated, Quarkslab-performed audit of Cortex's multi-tenant
> Prometheus storage layer found seven vulnerabilities (six Medium, one Low, none
> Critical/High) and produced the corpus's first concrete **tenant-boundary**
> finding: an authenticated tenant could override the org ID inside a PushStream
> gRPC payload and write across tenants, because the tenant identifier was trusted
> from the request rather than bound to the authenticated caller (V01). The
> remaining findings are credential exposure on a diagnostic endpoint and
> unbounded resource allocation on the ingest/gossip paths.

## Source Context

- **Type**: blog-post. The submitted URL is a short CNCF/OSTIF completion
  announcement. The substantive payload is one hop away and was followed per
  `agents/MINER.md` §1 (up to five substantive linked pages):
  - Primary: `https://cortexmetrics.io/blog/2026/07/07/cortex-security-audit-results/`
    — the maintainers' results post with the full V01–V07 table, per-finding fix
    PRs, the fixed release, and operator actions.
  - Auditor: `https://blog.quarkslab.com/cortex-security-audit.html` — Quarkslab's
    own summary, independent corroboration of the finding set and severities.
  - The full OSTIF/Quarkslab PDF report was **not** fetched; per-finding technical
    detail beyond the two posts is therefore not claimed here.
- **Author credibility**: The results post is by a Cortex maintainer (Daniel
  Blando) reporting an audit performed independently by Quarkslab and coordinated
  by OSTIF with CNCF funding. The vulnerability facts are checkable against fix
  PRs and the v1.21.1 release; the narrative is first-party.
- **Scope**: Cortex is a horizontally scalable, multi-tenant, long-term storage
  backend for Prometheus/OpenTelemetry. The audit scoped itself to *tenant
  boundary integrity and cluster operations* — confidentiality, integrity, and
  availability of those functions — plus the ingestion path, query path, and
  configuration/secrets exposure. It does NOT cover LLM workloads, agent
  gateways, or prompt/trace payloads; the transfer to this guide is the
  shared-telemetry-store tenant boundary, not any model-specific claim.
- **Prospector framing**: `triaged:text`, novelty medium, priority medium,
  relevant to Ch06 (Security & Trust) and Ch02 (Observability). Instructions were
  explicit: attribute no claim to the CNCF announcement beyond audit-program
  facts, and extract findings from the results post / Quarkslab write-up.

## Extracted Claims

### Claim 1: Cortex is a horizontally scalable, multi-tenant long-term storage backend for Prometheus, and multi-tenancy is enforced in the application layer by the `X-Scope-OrgID` header on every read and write path
- **Evidence**: Stated in the results post's introduction as the reason the audit
  was commissioned; the header is named as the mechanism scoping access to
  series, rules, and alertmanager configurations.
- **Confidence**: settled (project architecture, stated first-party).
- **Quote**: "Cortex is a horizontally scalable, multi-tenant, long-term storage backend for Prometheus. Multi-tenancy is enforced at the application layer via the `X-Scope-OrgID` header — every read and write path uses this tenant identifier to scope access to time-series data, rules, and alertmanager configurations. The integrity of this boundary is a critical security property."
- **Our assessment**: Buy it, and note the architectural shape: tenancy is not a
  database-level feature here, it is a header the application must honor on every
  path. That makes "did every code path propagate the tenant ID correctly?" the
  central security question — which is exactly what V01 (Claim 5) answers badly.
  Any platform storing per-tenant LLM telemetry in a shared backend inherits this
  shape.

### Claim 2: The audit was a Quarkslab whitebox engagement coordinated by OSTIF, run against a maintainer-agreed threat model, and scoped to the security health of the tenant boundary and cluster operations
- **Evidence**: Engagement details on the results post (auditor, coordinator,
  assessed commit `b4f5cfc37d83719040de7ca997ec125304a6b766`, methodology) and the
  CNCF announcement's description of the process.
- **Confidence**: settled (engagement facts, corroborated across two sources).
- **Quote**: "The auditors operated from a threat model agreed upon with the maintainers prior to the engagement."
- **Quote**: "In early spring of 2026, two auditors from Quarkslab reviewed the overall security posture of Cortex using whitebox code review methods."
- **Quote**: "The focus of this work was around the security health of the tenant boundary and cluster operations. That means interrogating the confidentiality, integrity, and availability of those two functions."
- **Our assessment**: Buy it. The methodology detail matters for how much weight
  to give the result: threat-model-first, then whitebox review plus static
  analysis and dynamic testing, is the same shape as the Inspektor Gadget audit
  (`blog-cncf-inspektor-gadget-security-audit`, Claim 3). The scope is unusually
  well-matched to the security property — the audit was *about* tenant isolation,
  not a general code review that happened to touch it.

### Claim 3: The scope named five attack surfaces, with tenant-boundary integrity first: cross-tenant read/write/delete of series, rules, or alertmanager state, and missing or bypassable `X-Scope-OrgID` propagation
- **Evidence**: The results post's enumerated scope list, including the
  parenthetical questions the auditors asked of each surface.
- **Confidence**: settled (stated scope).
- **Quote**: "**Tenant boundary integrity** — Can a tenant read, write, or delete another tenant’s series, rules, or alertmanager state? Are there code paths where `X-Scope-OrgID` propagation is missing or bypassable?"
- **Quote**: "**Cluster operations** — Can an internal component (ingester, compactor, store-gateway) be induced into serving cross-tenant data? Are gossip/memberlist communications authenticated and integrity-checked?"
- **Quote**: "**Configuration and secrets exposure** — Runtime config endpoints, debug endpoints."
- **Our assessment**: This is the reusable audit checklist for any shared
  telemetry store: (1) can a tenant name another tenant in a request and have it
  honored; (2) can an *internal* component be induced to serve cross-tenant data,
  i.e. the boundary must hold against compromised insiders, not just external
  callers; (3) are diagnostic endpoints an unauthenticated data source. The
  second question is the one most platform teams skip.

### Claim 4: The audit found seven vulnerabilities — six Medium and one Low, none Critical or High
- **Evidence**: Stated identically in the results post, the Quarkslab write-up,
  and the CNCF announcement; the results post gives the per-finding table.
- **Confidence**: settled (three-source agreement on count and severity profile).
- **Quote**: "7 vulnerabilities identified — 6 Medium, 1 Low. No Critical or High severity issues."
- **Quote**: "The table below summarizes the findings of the audit. A total of 7 vulnerabilities were identified: 6 of medium severity and 1 of low severity."
- **Our assessment**: Buy the calibration point, and read it the same way as the
  Inspektor Gadget result: an independent audit with no Critical/High findings is
  a positive signal about the codebase, not evidence that nothing was wrong. Note
  the severity/impact asymmetry — V01 is rated Medium risk but **High impact**
  (Claim 5), so "no High findings" does not mean "no high-impact failure modes."

### Claim 5: V01 is a tenant-impersonation flaw: an authenticated tenant could send a crafted PushStream gRPC stream with an overridden org ID and write across tenants — the payload-supplied tenant ID was trusted instead of bound to the authenticated caller
- **Evidence**: The findings table (risk Medium, impact "High (cross-tenant
  write)", attack vector "Authenticated tenant sending crafted gRPC stream with
  overridden org ID") and the fix description (reject on `TenantID` divergence
  plus HMAC-SHA256 stream auth, PR #7475).
- **Confidence**: settled (named finding, mechanism, impact, and merged fix).
- **Quote**: "Authenticated tenant sending crafted gRPC stream with overridden org ID"
- **Quote**: "Reject `PushStream` requests where per-message `TenantID` diverges from authenticated caller; add HMAC-SHA256 stream auth via `-distributor.sign-write-requests-keys`"
- **Quote**: "**Audit PushStream gRPC access.** If you expose the distributor gRPC port to tenants directly (not behind an auth gateway), V01 was exploitable prior to the fix."
- **Our assessment**: This is the source's highest-value claim and the reason the
  note is worth filing. The failure is not a missing check in the abstract — it
  is a **confused-deputy** design: authentication proves *who* the caller is, but
  the tenant scope is taken from a field the caller controls, so an authenticated
  tenant can act as another. The generalizable rule is: derive the tenant
  identifier from the authenticated principal, and reject any request where a
  payload-supplied tenant/org ID disagrees. That rule applies directly to a
  shared LLM-observability backend keyed by tenant/org ID for prompt, token, and
  spend attribution, and to any gateway that accepts an org header
  (`docs-litellm-enterprise`, Claim 6). Note the exploitability precondition the
  operator action names: exposing the distributor gRPC port directly to tenants.
  The fix is defense in depth — reject divergence *and* sign the stream.

### Claim 6: V02 is a stored XSS: malicious metric label values were rendered into Alertmanager and Store Gateway status pages, fixed by switching `text/template` to `html/template`
- **Evidence**: Findings table (Medium risk, Marginal impact, attack vector
  "Malicious metric label values rendered in UI contexts") and the fix row
  (PR #7512).
- **Confidence**: settled (named finding, rendering path, merged fix).
- **Quote**: "Malicious metric label values rendered in UI contexts"
- **Quote**: "Replace `text/template` with `html/template` in Alertmanager and Store Gateway status pages"
- **Our assessment**: Buy it, and record the class rather than the specific
  template package: **telemetry is attacker-influenced input to every UI that
  renders it**. Label values, log lines, trace attributes, and prompt text are all
  tenant-controlled strings, so any status page, dashboard, or alert view that
  renders them without contextual escaping is an injection surface. This is the
  same "output is untrusted input" discipline the corpus applies to model output
  and terminal renderers (`blog-cncf-inspektor-gadget-security-audit`, Claim 6).

### Claim 7: V03 is credential leakage: the `/config` endpoint exposed Swift, etcd, Redis, and HTTP basic-auth credentials in plaintext
- **Evidence**: Findings table (Medium risk, Marginal impact, "`/config` endpoint
  exposing storage credentials in plaintext") and the fix row (mask credentials,
  PR #7473).
- **Confidence**: settled (named finding, credential classes, merged fix).
- **Quote**: "`/config` endpoint exposing storage credentials in plaintext"
- **Quote**: "Mask Swift, etcd, Redis, and HTTP basic-auth credentials on `/config` endpoint"
- **Quote**: "**Review your `/config` endpoint exposure.** If you expose Cortex’s HTTP API without authentication, V03 may have been exploitable in your environment."
- **Our assessment**: Buy it. The transferable point is that **diagnostic and
  config endpoints are a credential-exposure surface**, and their risk is
  conditional on deployment topology — behind an authenticated gateway the same
  endpoint is far less dangerous. The operator action is the right framing:
  inventory which diagnostic endpoints are reachable without authentication.
  For an LLM platform, the analogous endpoints are gateway config/admin APIs that
  can echo provider keys, DB URLs, or webhook secrets.

### Claim 8: V04 is unbound gzip decompression — a crafted compressed payload caused excessive memory allocation on the distributor — fixed by capping the decompressed body size
- **Evidence**: Findings table (Medium risk, Marginal DoS impact, "Crafted
  compressed payload causing excessive memory allocation on distributor") and the
  fix row (cap via `-distributor.otlp-max-recv-msg-size` in `ParseProtoReader` and
  the OTLP path, PR #7515).
- **Confidence**: settled (named finding, mechanism, merged fix).
- **Quote**: "Crafted compressed payload causing excessive memory allocation on distributor"
- **Quote**: "Cap decompressed body via `-distributor.otlp-max-recv-msg-size` in `ParseProtoReader` and OTLP path"
- **Our assessment**: Buy it. Compression is an amplification primitive: a small
  request becomes a large allocation, so the size limit must be applied to the
  **decompressed** bytes, not the wire size. Any telemetry ingest endpoint that
  accepts compressed bodies (OTLP/HTTP is the common case) needs an explicit
  decompressed-size cap.

### Claim 9: V05 is uncontrolled memory allocation via a protobuf histogram with an extreme bucket count, fixed by adding a `WrappedHistogram` with a configurable 16 KB default size limit
- **Evidence**: Findings table (Medium risk, Marginal DoS impact, "Malformed
  histogram sample with extreme bucket count") and the fix row (PR #7570).
- **Confidence**: settled (named finding, mechanism, merged fix and default).
- **Quote**: "Malformed histogram sample with extreme bucket count"
- **Quote**: "Add `WrappedHistogram` with configurable size limit (`-validation.max-native-histogram-size-bytes`, default 16 KB)"
- **Our assessment**: Buy it. A schema-valid but pathological sample can allocate
  arbitrarily: "valid protobuf" is not "bounded memory." The fix pattern — a
  wrapper type that enforces a size limit with a conservative default — is the
  right place to put the bound, because per-component checks are what the
  auditors separately recommended centralizing (Claim 13).

### Claim 10: V06 is an unbounded read on gossip connections — an oversized gossip packet caused an unbounded memory read in memberlist — fixed with packet read timeout, max packet size, and max concurrent connections
- **Evidence**: Findings table (Medium risk, Marginal DoS impact, "Oversized
  gossip packet causing unbounded memory read in memberlist") and the fix row
  (PR #7518).
- **Confidence**: settled (named finding, mechanism, merged fix).
- **Quote**: "Oversized gossip packet causing unbounded memory read in memberlist"
- **Quote**: "Add `-memberlist.packet-read-timeout`, `-memberlist.max-packet-size`, `-memberlist.max-concurrent-connections`"
- **Our assessment**: Buy it. This is the network-transport half of the same
  resource-exhaustion class as V04/V05: an unauthenticated peer can make a node
  allocate or block by sending a packet the receiver did not bound. The three
  knobs are a checklist — read deadline, size cap, concurrency cap — that any
  gossip/mesh listener should expose.

### Claim 11: V07 is a missing gossip integrity check — unauthenticated gossip messages were accepted without HMAC validation — fixed by dropping incoming TCP transport packets when digest verification fails
- **Evidence**: Findings table (Low risk, Negligible impact, "Unauthenticated
  gossip messages accepted without HMAC validation") and the fix row (PR #7474).
- **Confidence**: settled (named finding, mechanism, merged fix).
- **Quote**: "Unauthenticated gossip messages accepted without HMAC validation"
- **Quote**: "Drop incoming TCP transport packets when digest verification fails"
- **Our assessment**: Buy it, but weight it as Low and pair it with Claim 12's
  secure-default recommendation. The important structural point is that the code
  had an integrity mechanism and did not enforce it on this path — a check that
  exists but is not mandatory is not a control. The fix moves from "verify if
  configured" to "drop on failure."

### Claim 12: All seven findings have verified fixes merged and shipped in Cortex v1.21.1 (released 2026-06-04), and the operator action is to upgrade to v1.21.1 or later
- **Evidence**: Fix-status section naming the release and linking it; Quarkslab
  independently states all findings are resolved; the CNCF announcement repeats
  the update guidance.
- **Confidence**: settled (version-scoped remediation with a named release).
- **Quote**: "All 7 findings have verified fixes merged to `master` and shipped in [**Cortex v1.21.1**](https://github.com/cortexproject/cortex/releases/tag/v1.21.1) (released 2026-06-04)."
- **Quote**: "**Upgrade to [v1.21.1](https://github.com/cortexproject/cortex/releases/tag/v1.21.1) or later to include all security fixes.**"
- **Quote**: "All findings have since been resolved, using either the fixes the auditors recommended or alternative mitigations with equivalent effect."
- **Our assessment**: Buy it. This is the version-scoped-remediation pattern the
  guide already prefers (`blog-cncf-inspektor-gadget-security-audit`, Claim 14):
  name the exact minimum fixed version so fleet state is checkable, rather than
  "update to latest." The Quarkslab wording adds a useful nuance — fixes may be
  *equivalent mitigations*, not necessarily the auditors' literal recommendation,
  so "verified fixed" is the property to track, not "implemented as suggested."

### Claim 13: The auditors' overall assessment was a "solid engineering foundation," with three forward-looking recommendations: tighten insecure defaults, centralize input validation at ingestion boundaries, and establish a dependency update cadence for indirect transitive dependencies
- **Evidence**: Quoted conclusion from the report plus the results post's
  recommendation list; Quarkslab's own conclusion repeats the same themes.
- **Confidence**: settled for the quoted assessment; emerging for the
  recommendations' effect (process guidance, not measured outcomes).
- **Quote**: "Cortex benefits from a solid engineering foundation. The project shows good code quality, extensive test coverage, and strong observability features, all of which contribute to its maintainability and resilience."
- **Quote**: "Tightening default configurations (e.g., enabling gossip encryption by default)"
- **Quote**: "Centralizing input validation at ingestion boundaries rather than relying on per-component checks"
- **Quote**: "Establishing a dependency update cadence for indirect transitive dependencies"
- **Our assessment**: Buy the first two; the third is corroboration of existing
  guide material. "Centralizing input validation at ingestion boundaries" is the
  architectural lesson behind V04–V06: the same size/format bounds were missing in
  several components because each component owned its own validation. One
  ingestion-boundary validation layer is easier to reason about and harder to
  bypass. "Tighten defaults" is the guide's secure-default rule stated by an
  auditor: encryption available but off is not a secure default.

### Claim 14: The operator guidance is deployment-conditional — update, review `/config` exposure, enable memberlist encryption if gossip crosses untrusted networks, and audit direct PushStream gRPC access
- **Evidence**: The results post's numbered "Operator Action Required" list.
- **Confidence**: settled (author-stated guidance tied to specific findings).
- **Quote**: "**Consider enabling memberlist encryption** (`-memberlist.encryption-enabled=true`) if your gossip traffic traverses untrusted networks. V07 makes this particularly relevant."
- **Our assessment**: Buy it. The guidance is notable for being conditioned on
  topology rather than universal: V03 is only dangerous if the HTTP API is
  unauthenticated, V01 only if the distributor gRPC port is exposed to tenants
  directly, V07 only if gossip crosses an untrusted network. That is the right
  shape for security advice — state the precondition, not just the patch level —
  and it is a useful template for the guide's own remediation sections.

## Concrete Artifacts

### Finding table (from the results post — risk / impact / attack vector)

```
ID   Title                                              Risk    Impact                  Attack Vector
V01  Tenant impersonation via PushStream gRPC            Medium  High (cross-tenant write)  Authenticated tenant sending crafted gRPC stream with overridden org ID
V02  Stored XSS                                         Medium  Marginal                Malicious metric label values rendered in UI contexts
V03  Sensitive information leakage                      Medium  Marginal                /config endpoint exposing storage credentials in plaintext
V04  Unbound Gzip decompression                         Medium  Marginal (DoS)          Crafted compressed payload causing excessive memory allocation on distributor
V05  Uncontrolled memory allocation via protobuf histogram  Medium  Marginal (DoS)      Malformed histogram sample with extreme bucket count
V06  Unbounded read on gossip connections               Medium  Marginal (DoS)          Oversized gossip packet causing unbounded memory read in memberlist
V07  Gossip packet integrity check not enforced         Low     Negligible              Unauthenticated gossip messages accepted without HMAC validation
```

The table is reproduced from the results post; the post presents it as an HTML
table, so this block is a faithful tabulation of its cell text, not a byte-exact
copy of the page source.

### Fix table (from the results post — finding / fix / PR)

```
V01  Reject PushStream requests where per-message TenantID diverges from authenticated
     caller; add HMAC-SHA256 stream auth via -distributor.sign-write-requests-keys   #7475
V02  Replace text/template with html/template in Alertmanager and Store Gateway
     status pages                                                                   #7512
V03  Mask Swift, etcd, Redis, and HTTP basic-auth credentials on /config endpoint    #7473
V04  Cap decompressed body via -distributor.otlp-max-recv-msg-size in ParseProtoReader
     and OTLP path                                                                  #7515
V05  Add WrappedHistogram with configurable size limit
     (-validation.max-native-histogram-size-bytes, default 16 KB)                   #7570
V06  Add -memberlist.packet-read-timeout, -memberlist.max-packet-size,
     -memberlist.max-concurrent-connections                                         #7518
V07  Drop incoming TCP transport packets when digest verification fails             #7474
```

### Operator action list (verbatim from the results post)

```
1.  Update to the v1.21.1 or later release. All fixes are included.
2.  Review your /config endpoint exposure. If you expose Cortex's HTTP API without
    authentication, V03 may have been exploitable in your environment.
3.  Consider enabling memberlist encryption (-memberlist.encryption-enabled=true) if
    your gossip traffic traverses untrusted networks. V07 makes this particularly
    relevant.
4.  Audit PushStream gRPC access. If you expose the distributor gRPC port to tenants
    directly (not behind an auth gateway), V01 was exploitable prior to the fix.
```

(Link markup removed; wording and ordering preserved. The page uses a curly
apostrophe in "Cortex’s", rendered here as a straight apostrophe.)

### Scope list (verbatim headings from the results post)

```
1. Tenant boundary integrity — Can a tenant read, write, or delete another tenant's
   series, rules, or alertmanager state? Are there code paths where X-Scope-OrgID
   propagation is missing or bypassable?
2. Cluster operations — Can an internal component (ingester, compactor, store-gateway)
   be induced into serving cross-tenant data? Are gossip/memberlist communications
   authenticated and integrity-checked?
3. Ingestion path — Remote write, PushStream gRPC, distributor validation, ingester
   replication.
4. Query path — Query frontend, querier, store-gateway block loading and filtering.
5. Configuration and secrets exposure — Runtime config endpoints, debug endpoints.
```

## Cross-References

**Candidates from `miner-related-notes.md` (all ten listed paths evaluated; two
cited, eight dismissed):**

- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**:
  retail/gaming SLO granularity and platform migration; no shared-storage,
  tenancy, or audit content.
- `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` —
  **cited** (Extends): **Claim 2** (verified) describes per-agent mTLS identities
  via cert-manager plus CiliumNetworkPolicy restricting which agent identity may
  reach which MCP server. That is the *identity-derived scope* pattern this source
  finds missing in V01: there, the tenant scope came from a payload field rather
  than the authenticated principal. The two notes are complementary — one shows
  identity-scoped reachability between workloads, the other shows what happens
  when a scope field is not bound to identity at the storage boundary.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
  **dismissed**: imperative vs declarative change workflows; no tenancy or audit
  material.
- `source-notes/blog-cncf-inspektor-gadget-security-audit.md` — **cited**
  (Corroborates / Extends): **Claim 4** (verified) is the audit-calibration
  pattern — an independent audit with no Critical/High findings concluding the
  project is "adequately mature"; this source's Claim 4 is the same shape.
  **Claim 14** (verified) is version-scoped remediation to the named fixed
  release; this source's Claim 12 is the same pattern (v1.21.1). The delta is the
  tenant-isolation failure class (Claim 5), which that note does not cover — its
  findings are kernel-tracing/build/rendering issues, not cross-tenant writes.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch rate-limit
  accounting; no tenant-isolation or audit content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  definition/measurement; unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch coordination checklists; unrelated.
- `source-notes/docs-google-sre-on-call.md` — **dismissed**: pager load and
  alerting hygiene; no shared-storage or tenancy claims.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **dismissed**:
  within-request model composition; unrelated.
- `source-notes/docs-litellm-completion-function-call.md` — **dismissed**:
  function-calling capability predicates; unrelated.

**Additional cross-references found by searching `source-notes/`:**

- **Corroborates**:
  - `source-notes/docs-litellm-enterprise.md` **Claim 6** (verified) — the
    gateway-side tenant model: "Governance includes multi-tenant
    orgs/teams/projects/keys, project management with budgets/owners/rate
    limits/model allowlists/isolated spend..." This source adds the
    *storage-backend* half of the same boundary. The V01 rule (derive tenant from
    the authenticated principal) is the enforcement counterpart to the gateway's
    org/team/key model: a gateway that scopes spend by org is only as trustworthy
    as the backend's willingness to reject a mismatched org ID.
  - `source-notes/blog-cncf-securing-cicd-locking-down-dependencies.md` **Claim 1**
    (verified) — "A pinned workflow that fetches a compromised dependency is still
    a compromised workflow." The audit's recommendation to establish a dependency
    update cadence for **indirect transitive** dependencies (Claim 13) is the same
    composition concern: direct pins do not cover what those pins pull in.
- **Extends**:
  - `source-notes/docs-cncf-iam-whitepaper-reference-patterns.md` **Claim 4**
    (verified) — dual-subject authorization, where workload identity is carried in
    the SPIFFE SVID and user identity/authorization context in the OAuth access
    token, and the decision uses both. V01 is a concrete failure of that
    discipline at a storage boundary: the authenticated identity was checked, but
    a second, caller-supplied tenant identity overrode it. **Claim 7** (verified)
    supplies the adjacent audit rule — log every request with a unique identifier
    and the applied authorization decision — which is how a cross-tenant write
    would be detected after the fact.
  - `source-notes/docs-litellm-data-security.md` **Claim 9** (verified) — the
    data-security page is silent on encryption, key management, log redaction, and
    retention, and "the vendor's own linked pages confirm those surfaces are
    partially plaintext and operator-owned." V03 (Claim 7 here) is a concrete
    instance of the credential-exposure half of that gap in a different product.
- **Contrast** (not corroboration or contradiction):
  - `source-notes/blog-cncf-telemetry-that-matters-observability-pipelines.md`
    **Claim 7** (verified) — tail/pattern-based sampling should "drop boring,
    successful requests while capturing 100% of anomalies or failures." That note
    treats volume as a cost/quality lever the operator controls; this source
    treats unbounded ingest input (V04–V06) as an availability attack the operator
    must cap. Same pipeline, opposite direction of control.
  - `source-notes/blog-cncf-jaeger-clickhouse-backend.md` — the corpus's other
    long-term telemetry storage backend note; performance/schema oriented
    (Claims 1–8), with no tenant-boundary or credential-exposure material. Cited
    as a contrast only: a storage backend can be well-understood for throughput
    and still have its isolation properties unexamined.
- **Contradicts**: **none.** No existing source note claims that a
  caller-supplied tenant identifier is safe to trust, or that diagnostic
  endpoints are not a credential surface, or that unbounded ingest is acceptable.
  The apparent tension with `blog-cncf-cloud-native-agentic-ai-security-platform`
  (identity-scoped mTLS) is complementary, not opposing — that note is about
  workload-to-workload reachability, this one about tenant-scoped data access.
  `CONTRADICTIONS.md` and open `contradiction`-labeled issues were checked; no
  entry covers shared-telemetry-store tenant isolation. No contradiction issue
  filed.
- **Novel** (new to the corpus):
  - **Application-layer tenant isolation in shared telemetry storage** as a
    security property, with the header-propagation audit question ("are there
    code paths where `X-Scope-OrgID` propagation is missing or bypassable?").
  - **Tenant impersonation via a payload-supplied org ID** (V01) — the
    confused-deputy failure where authentication succeeds but scope is
    caller-controlled. The corpus had gateway-side tenancy models
    (`docs-litellm-enterprise`) but no note on enforcing tenancy at the storage
    boundary.
  - **Diagnostic `/config` endpoints as a plaintext-credential surface** (V03),
    with the topology-conditional exploitability framing.
  - **Ingest-path resource-exhaustion taxonomy**: decompression amplification
    (V04), schema-valid-but-pathological sample size (V05), and unbounded gossip
    packet read (V06), plus the "centralize validation at the ingestion boundary"
    recommendation.
  - **Gossip integrity as a must-enforce check** rather than an optional feature
    (V07), paired with encryption-by-default as a secure-default recommendation.

## Guide Impact

- **Chapter 06 (Security & Trust)** — add a **tenant-boundary enforcement** rule
  near the gateway-defaults material (`guide/06-security-and-trust.md:316`):
  1. State the V01 rule (Claim 5): *never trust a tenant/org identifier supplied
     in the request payload; derive it from the authenticated principal and reject
     any request where the two disagree.* Signing the stream is defense in depth,
     not a substitute for the binding. Apply it to any shared store keyed by
     tenant for prompt/token metrics and spend attribution, and to gateways that
     accept org/team headers.
  2. Add **diagnostic endpoints as a credential surface** (Claim 7): inventory
     config/debug/admin endpoints, require authentication on them, and mask
     storage/basic-auth credentials in what they return.
  3. Add the **secure-default + version-scoped remediation** pair (Claims 12–13):
     name the exact minimum fixed version, and treat "encryption available but
     off by default" as a misconfiguration rather than a supported mode.
  4. Note the **centralize-validation-at-ingestion** recommendation (Claim 13) as
     the architectural alternative to per-component checks.
- **Chapter 02 (Observability)** — extend the platform/tenant section
  (`guide/02-observability.md:349`), which currently covers shared SLO dashboards
  but not the store's isolation:
  1. Add the security half of the platform/tenant boundary: a shared telemetry
     backend holding many tenants' traces/metrics must enforce tenant isolation at
     every read and write path, and the enforcement must hold against internal
     components too (Claim 3's second question).
  2. Add the **ingest-bound resource caps** (Claims 8–10): cap decompressed body
     size, sample/histogram size, and gossip packet size/concurrency. Treat these
     as availability controls on the observability pipeline, not just tuning
     knobs.
  3. Cite Claim 1's architecture note when explaining why header-based tenancy is
     fragile: the boundary is only as strong as the least-careful code path that
     propagates the header.
- **Chapter 06 / Ch02 cross-link** — use Claim 4 to calibrate audit language:
  report the severity profile and the auditors' conclusion together, and do not
  equate "no Critical/High findings" with "no high-impact failure modes" (V01 is
  Medium risk / High impact).

## Extraction Notes

- **Pages read**: the submitted CNCF announcement (audit-program facts only:
  OSTIF/Quarkslab/CNCF, threat-model-led whitebox methodology, scope = tenant
  boundary + cluster operations, 6 Medium / 1 Low); the Cortex results post
  (primary payload — full V01–V07 table, fix PRs, v1.21.1, operator actions,
  auditor recommendations); and the Quarkslab write-up (independent corroboration
  of the finding set, severities, and conclusion). The full OSTIF/Quarkslab PDF
  report was **not** fetched, so this note makes no per-finding technical claims
  beyond what the two public posts state (no CVSS vectors, no exploit detail, no
  code-level root cause beyond the fix descriptions).
- **Attribution discipline**: per the Prospector's mining instruction, no finding
  claim is attributed to the CNCF announcement. Claims 5–11 and the finding/fix
  tables are from the results post; Claim 2's process quote and the
  severity-profile corroboration are from the Quarkslab post and/or the
  announcement where explicitly quoted. Claim 1 (architecture/header) is from the
  results post introduction.
- **Quote fidelity**: quotes were copied from the fetched pages. Where the
  results post's HTML table was flattened into the Concrete Artifacts code
  blocks, the block is labeled as a faithful tabulation rather than a byte-exact
  page copy, and link markup was stripped from the operator-action block (noted
  inline). Curly apostrophes in the page were preserved in claim quotes
  ("tenant’s", "Cortex’s"); the operator-action artifact block renders one as a
  straight apostrophe and says so. No non-adjacent sentences were spliced into a
  single quoted passage.
- **`miner-related-notes.md` disposition**: all ten candidate paths evaluated —
  two cited (`blog-cncf-cloud-native-agentic-ai-security-platform`,
  `blog-cncf-inspektor-gadget-security-audit`), eight explicitly dismissed (see
  Cross-References). Additional cross-refs (`docs-litellm-enterprise`,
  `blog-cncf-securing-cicd-locking-down-dependencies`,
  `docs-cncf-iam-whitepaper-reference-patterns`, `docs-litellm-data-security`,
  `blog-cncf-telemetry-that-matters-observability-pipelines`,
  `blog-cncf-jaeger-clickhouse-backend`) were found by searching `source-notes/`.
  Every cited `Claim N` was re-read and verified against the named note per
  MINER.md §4b.
- **No contradiction issue filed**: the identity-scoped-reachability note is
  complementary, not opposing (see Cross-References → Contradicts). No `guide/`
  edits, no `registry/*` edits — registry indexes are rebuilt after merge from
  this note's frontmatter and claim headings.
- `date_extracted` / `last_checked` set to 2026-11-01 UTC (pages fetched and
  quote-verified on that date). `confidence_overall: emerging` — the audit facts
  (findings, severities, fixes, release) are concrete and settled, but the
  guide-relevant transfer (tenant-boundary rule for an LLM telemetry backend,
  ingest resource caps) is an extrapolation from a single non-LLM project's
  audit.
