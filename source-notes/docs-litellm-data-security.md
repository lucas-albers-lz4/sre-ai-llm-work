---
source_url: https://docs.litellm.ai/docs/data_security
source_type: docs
title: "Data Privacy and Security | liteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-18)
date_extracted: 2026-10-18
last_checked: 2026-10-18
status: current
confidence_overall: emerging
issue: "#1651"
---

# Data Privacy and Security (LiteLLM Docs)

> LiteLLM's vendor trust page pairs three checkable self-host commitments
> (no telemetry/no data on LiteLLM servers, a 24-hour JWT session-cookie
> contract, and grype image scanning in CI) with an AI-spam-aware
> vulnerability-disclosure policy (video PoC required, reports without one
> closed without review) — while staying silent on encryption, key
> management, log redaction, and retention, surfaces the vendor's own
> linked pages (shared responsibility, encryption FAQ) assign to the
> operator.

## Source Context

- **Type**: docs (vendor compliance / trust-center page, LiteLLM Enterprise
  section of `docs.litellm.ai`).
- **Author credibility**: LiteLLM (BerriAI) first-party vendor documentation,
  signed off in the Legal/Compliance FAQ section by Krish Amit Dholakia. It is
  authoritative for *what the vendor asserts about its own product* — every
  claim here is an unvalidated vendor assurance (at best `[emerging]`), not
  practitioner-verified evidence. The page carries specific, falsifiable
  process claims (cookie lifetime, scan tooling, disclosure channel), which is
  why it survives triage as extraction-worthy rather than pure procurement
  prose.
- **Scope**: Self-hosted privacy/telemetry stance, Admin UI cookie policy,
  vulnerability-reporting process, container image scanning status, and
  procurement-compliance FAQ (SOC 2, ISMS, audit logs, legal entity). Does
  **not** cover encryption in transit or at rest, key management, secrets
  storage/rotation, prompt/response log redaction, PII scrubbing, retention
  windows, backups, or multi-tenant isolation — those topics are linked out
  (encryption FAQ, shared responsibility, `security.md`) or absent entirely.
  Per the Prospector's triage on #1651, the omissions themselves are part of
  the extraction target: for a self-hosted gateway they become the
  operator-owned surface.

## Extracted Claims

### Claim 1: When you self-host, the vendor asserts no data or telemetry reaches LiteLLM servers — as a commitment, not a documented mechanism
- **Evidence**: Two bolded bullet assertions in the "Self-hosted Instances
  LiteLLM" section of the data-security page; the same two lines are repeated
  verbatim in the canonical in-repo `security.md` (sub-page followed). There
  is no config key, opt-out flag, or code path shown on either page backing
  the claim.
- **Confidence**: emerging (vendor assertion; consistent across two vendor
  documents but with no inspectable mechanism)
- **Quote**: "No data or telemetry is stored on LiteLLM Servers when you self-host"
- **Quote**: "We run no telemetry when you self-host LiteLLM"
- **Our assessment**: A dated, citable vendor commitment an operator can hold
  the vendor to, but not a verifiable control. The self-hoster's job is to
  verify it against the actual deployment (egress monitoring of the proxy
  container is the obvious check). We buy the claim as a *commitment*; we do
  not treat it as evidence that a given deployment is egress-clean. Worth
  pinning precisely because the corpus documents LiteLLM security defects that
  make "trust the vendor's quiet-network claim" a weak posture
  (`failure-litellm-security-hardening-april-2026.md`).

### Claim 2: Self-hosted deployments collect no personal data and transmit none to LiteLLM servers — all data "remains entirely within your own infrastructure"
- **Evidence**: Stated in the "Collection of Personal Data" section, scoped
  explicitly "For Self-hosted LiteLLM Users".
- **Confidence**: emerging (vendor assertion)
- **Quote**: "No personal data is collected or transmitted to LiteLLM servers when you self-host our software."
- **Quote**: "Any data generated or processed remains entirely within your own infrastructure."
- **Our assessment**: The privacy half of Claim 1. Note the tension the page
  does not resolve: "remains entirely within your own infrastructure" is true
  of *storage* only in the sense that LiteLLM the vendor never sees it — the
  operator's own observability sinks (spend logs, OTEL backends) absolutely
  do see request-derived data, and the vendor's own encryption FAQ admits
  those stores are plaintext (Claim 9) and its own incident report shows
  credentials leaking into them
  (`failure-litellm-guardrail-logging-secret-exposure.md`). "Your
  infrastructure" is not automatically safe infrastructure.

### Claim 3: Admin UI session cookies are a bounded, checkable contract — JWT, auth/session-only, no third-party cookies, expiring on browser close, logout, or 24 hours
- **Evidence**: Seven-bullet cookie policy under "Cookies Information,
  Security, and Privacy", all scoped "For Self-hosted LiteLLM Users". These
  are the most directly falsifiable assertions on the page (an operator can
  inspect the cookie in a browser and watch the expiry).
- **Confidence**: emerging (documented vendor behavior; directly checkable,
  not independently verified here)
- **Quote**: "Session cookies expire when you close your browser, logout or after 24 hours."
- **Quote**: "The only cookies used are essential for maintaining user authentication and session management for the app UI."
- **Quote**: "The cookie is stored as JWT and is not accessible to any other part of the system."
- **Quote**: "LiteLLM does not use any third-party cookies."
- **Our assessment**: The most operational content on the page. The 24-hour
  hard ceiling on Admin UI sessions is a concrete session-hygiene number a
  hardening checklist can cite; "not accessible to any other part of the
  system" is the vendor-side counterpart to the operator-side lesson from
  `failure-litellm-security-hardening-april-2026.md` (a JWT-shaped artifact
  crossing an unintended boundary — the OIDC cache — was exactly the CVE
  class). The cookie-as-JWT claim is checkable and worth spot-checking at
  upgrade time.

### Claim 4: The canonical vulnerability-disclosure policy lives in-repo (`security.md`); GitHub Security Advisories is the preferred channel, with email as a slower fallback
- **Evidence**: "Security Vulnerability Reporting Guidelines" section; both
  the preferred channel and the fallback are linked/identified on-page.
  `security.md` (sub-page followed) confirms and expands the policy.
- **Confidence**: emerging (documented process; stable across both documents)
- **Quote**: "The preferred channel for reporting a vulnerability is to file a private vulnerability report through GitHub Security Advisories."
- **Quote**: "If you cannot use GitHub, emailing support@berri.ai with the same details works in a pinch, though may be triaged more slowly."
- **Our assessment**: Standard, well-structured disclosure routing. The
  interesting governance detail is that the *canonical* policy is versioned
  in the repo the software ships from, not on the marketing site — the docs
  page defers to it. Operators running forks should read the in-repo policy
  rather than the trust page.

### Claim 5: All vulnerability reports must include a video/screen recording demonstrating the full exploit, explicitly framed as a defense against low-quality AI-generated reports — and `security.md` enforces it by closing video-less reports without review
- **Evidence**: The data-security page states the requirement and its
  rationale in one sentence; the canonical `security.md` (sub-page followed)
  elevates it to a warning banner, restates it as "required for every
  report", gives the AI-spam rationale, and describes the enforcement
  (closed without review; reopened if a video is added).
- **Confidence**: emerging (vendor policy assertion, not a measured outcome —
  we have no data on report volumes or junk-report rates)
- **Quote**: "Please note that in order to combat low-quality AI spam, all vulnerability reports require a video or screen recording of you demonstrating the full exploit."
- **Quote**: "Reports that do not include a video demonstrating the exploit will be closed without review." (security.md, Reproduction Video Requirement)
- **Quote**: "AI tools have made it easy to produce plausible-sounding vulnerability reports that do not reproduce in practice, and triaging them takes time away from real issues." (security.md, Reproduction Video Requirement)
- **Our assessment**: The single most AI-relevant governance pattern on the
  page and the highest-value extraction for Ch06: an LLM-adjacent vendor has
  adapted its intake channel to the *volume economics of LLM-generated
  submissions* — raising the cost of a report (produce a working exploit
  video) to filter machine-generated noise. The design is sound in principle
  (proof-of-work at the intake boundary) and the enforcement is explicit
  (close-without-review), but it has a known failure mode worth stating:
  it also filters low-bandwidth human reporters who can demonstrate an
  exploit in text. `security.md` softens this ("If you add a video to a
  closed report, we will reopen and triage it"). This is a directly
  copyable pattern for any open-source LLM-infrastructure project drowning
  in AI-written advisories.

### Claim 6: LiteLLM runs `grype` security scans on all built Docker images in CI, reported as "0 High/Critical" — a dependency-scan status for image contents, not an application-security claim
- **Evidence**: "Vulnerability Scanning" section names the tool, the scope
  ("all built Docker images"), links the CircleCI check by line anchor, and
  states current status.
- **Confidence**: emerging (vendor scan-status statement; the CI check is
  linkable but the "0 High/Critical" figure is a point-in-time vendor claim)
- **Quote**: "LiteLLM runs grype security scans on all built Docker images."
- **Quote**: "Current Status: ✅ Passing. 0 High/Critical severity vulnerabilities found."
- **Our assessment**: Concrete, falsifiable supply-chain scanning posture —
  the scan scope is OS packages/dependencies inside the built images, so it
  says nothing about application-layer flaws. This matters for how the guide
  uses the line: the "0 High/Critical" status **must not** be presented as
  softening or contradicting the app-layer CVEs in
  `failure-litellm-security-hardening-april-2026.md` (OIDC cache collision,
  config-update privilege escalation, password-hash exposure — none of which
  a container dependency scan would catch), nor the PyPI release-path
  compromise in `failure-litellm-supply-chain-incident-march-2026.md`
  (compromised *release credentials* exfiltrate; an image-content scan of
  build output is upstream-adjacent, not a defense against that attack).
  Scan-scope discipline is the guide-worthy lesson: "vendor reports zero
  criticals in images" and "vendor disclosed three proxy CVEs" are both
  true simultaneously because they measure different things.

### Claim 7: Compliance posture — SOC 2 Type II via the Trust Center, CodeQL plus an ISMS, audit logs covering auth/create/update events, incident-response policy "available upon request", legal entity Berrie AI Incorporated
- **Evidence**: Legal/Compliance FAQ section: signed Q&A entries naming the
  Trust Center for the SOC 2 report, CodeQL + ISMS, the audit-logs doc link
  for event coverage, and the IR-policy-on-request answer; vendor information
  block names the legal entity and security-incident contact.
- **Confidence**: emerging (procurement assurance; the SOC 2 report itself
  sits behind the Trust Center login and was not examined)
- **Quote**: "SOC 2 Type II. Our current report is available through the LiteLLM Trust Center."
- **Quote**: "Yes - CodeQL and an ISMS covering multiple security domains."
- **Quote**: "Yes - we have audit logs"
- **Quote**: "Legal Entity Name: Berrie AI Incorporated"
- **Quote**: "Yes, Incident Response Policy available upon request."
- **Our assessment**: Questionnaire-answer material, useful to the corpus as
  a dated vendor-attestation snapshot rather than as engineering evidence.
  Two details are worth keeping: audit-log event coverage is only
  auth/create/update (no read/access events — adjacent to the same
  audit-coverage gap the corpus already flagged for promptfoo in
  contradiction issue #1597, a different vendor), and the IR policy is
  request-gated rather than published, which limits what an operator can
  review before procurement.

### Claim 8: SSO/SAML, audit logs, spend tracking, multi-team management, and guardrails are Enterprise-tier features
- **Evidence**: The page footer's Enterprise banner and the Enterprise nav
  sidebar; the audit-logs link in Claim 7 targets the multiple-admins doc
  under the Enterprise section.
- **Confidence**: emerging (vendor product-tier statement)
- **Quote**: "SSO/SAML, audit logs, spend tracking, multi-team management, and guardrails, built for production."
- **Our assessment**: A trust-relevant gating fact, not just pricing: an OSS
  self-hoster gets no SSO/SAML and no audit logs out of the box, so
  authentication-strength and change-audit controls for a self-hosted
  deployment are operator-assembled (external IdP in front, DB-level
  auditing, or an Enterprise license). Ch06's self-host hardening guidance
  should say so explicitly rather than assuming the gateway provides them.

### Claim 9: The data-security page is silent on encryption, key management, log redaction, and retention — and the vendor's own linked pages confirm those surfaces are partially plaintext and operator-owned
- **Evidence**: Negative-space reading of the page (no encryption content in
  body; "encryption" appears only as a sidebar link), plus two followed
  sub-pages: the encryption FAQ (linked from the same Enterprise sidebar)
  and the shared-responsibility page (linked as "Next" from this page).
  The FAQ answers what this page omits — including the parts that are
  *not* secure by default.
- **Confidence**: emerging (documented vendor positions across three vendor
  pages; the omissions are verifiable by reading, the FAQ answers are vendor
  self-report)
- **Quote**: "Partially. Only specific sensitive data is encrypted at rest." (encryption FAQ, Data at Rest Encryption)
- **Quote**: "Spend Logs - Request/response data in LiteLLM_SpendLogs" listed under "NOT Encrypted" (encryption FAQ)
- **Quote**: "Cached prompts and completions are NOT encrypted." (encryption FAQ)
- **Quote**: "we own the behavior of the product as documented on this site, and you own the environment it runs in + any code you add to it." (shared responsibility)
- **Our assessment**: The Prospector's key extraction target, now with the
  gap filled by the vendor's own adjacent pages, which makes the rule
  sharper than "the page is silent": the vendor *does* document the missing
  topics — just not here — and what it documents is that at-rest encryption
  covers credentials/config secrets only (NaCl SecretBox keyed by
  `LITELLM_SALT_KEY`), while spend logs, audit logs, org data, and all cache
  backends are plaintext, and the environment plus any injected code are
  the operator's problem. The self-hoster's rule this supports: a vendor
  trust page's silence is not safety; follow the linked pages, and treat
  every store the vendor leaves plaintext (spend logs, caches) as an
  operator-owned redaction/access-control surface. The guardrail-logging
  incident (`failure-litellm-guardrail-logging-secret-exposure.md`,
  Concrete Artifacts → Exposure surfaces) is the empirical proof: plaintext
  spend logs and OTEL traces did carry `Authorization` headers until
  v1.82.3.

### Claim 10: The bug bounty is severity-tiered with only P0/P1 eligible, and misconfiguration-dependent attacks (e.g. no `master_key` set) are explicitly out of scope
- **Evidence**: `security.md` (sub-page followed): three named vulnerability
  categories (P0 supply chain, P1 unauthenticated proxy access, P2
  authenticated malicious actions), the bounty table with P2 marked N/A, and
  a "Known Non-Issues" section.
- **Confidence**: emerging (vendor program terms; corroborated in spirit by
  the corpus's existing note on the same program's launch —
  `failure-litellm-security-hardening-april-2026.md`, Concrete Artifacts →
  Bug bounty program, which records the same $1,500–$3,000 / $500–$1,500
  tiers)
- **Quote**: "Note that currently only P0/P1 reports are eligible for a bounty, though submissions for P2 bugs are still encouraged"
- **Quote**: "Attacks that require a misconfiguration on setup (e.g not setting a master_key on the proxy configuration), are explicitly not in scope and are not considered vulnerable."
- **Our assessment**: The P0 category ("Supply Chain Attacks… compromise our CI/CD pipeline") exists *because of* the March 2026 PyPI incident the corpus already documents (`failure-litellm-supply-chain-compromise-march-2026.md`,
  `failure-litellm-supply-chain-incident-march-2026.md`) — the taxonomy is
  post-incident governance made concrete. The misconfiguration carve-out is
  the operator-relevant clause: "secure by default" stops at `master_key`,
  so an unkeyed proxy is a deployment bug the vendor will not pay for and
  will not treat as a vulnerability. That belongs in Ch06's self-host
  checklist as a vendor-scoped boundary of the "secure defaults" claim.

## Concrete Artifacts

All artifacts verbatim; primary-source artifacts from
https://docs.litellm.ai/docs/data_security, sub-page artifacts attributed
explicitly.

### Self-host / telemetry and personal-data assertions (data_security page, verbatim)

```
No data or telemetry is stored on LiteLLM Servers when you self-host
Telemetry: We run no telemetry when you self-host LiteLLM

No personal data is collected or transmitted to LiteLLM servers when you
self-host our software.
Any data generated or processed remains entirely within your own
infrastructure.
```

### Cookie policy (data_security page, verbatim)

```
- Cookie data remains within your own infrastructure.
- LiteLLM uses minimal cookies, solely for the purpose of allowing Proxy
  users to access the LiteLLM Admin UI.
- These cookies are stored in your web browser after you log in.
- We do not use cookies for advertising, tracking, or any purpose beyond
  maintaining your login session.
- The only cookies used are essential for maintaining user authentication
  and session management for the app UI.
- Session cookies expire when you close your browser, logout or after 24
  hours.
- LiteLLM does not use any third-party cookies.
- The Admin UI accesses the cookie to authenticate your login session.
- The cookie is stored as JWT and is not accessible to any other part of
  the system.
```

### Vulnerability scanning (data_security page, verbatim)

```
- LiteLLM runs grype security scans on all built Docker images.
    - See grype litellm check on ci/cd
      (https://github.com/BerriAI/litellm/blob/main/.circleci/config.yml#L1099).
    - Current Status: ✅ Passing. 0 High/Critical severity vulnerabilities
      found.
```

### Reproduction video requirement (security.md — canonical policy in
BerriAI/litellm, verbatim)

```
> [!WARNING]
> Reports that do not include a video demonstrating the exploit will be
> closed without review. See Reproduction Video Requirement below.

### Reproduction Video Requirement

A video demonstrating the exploit is required for every report. AI tools
have made it easy to produce plausible-sounding vulnerability reports that
do not reproduce in practice, and triaging them takes time away from real
issues. Reports submitted without a working reproduction video will be
closed without review. If you add a video to a closed report, we will
reopen and triage it.
```

### Bug bounty tiers and vulnerability categories (security.md, verbatim)

```
P0: Supply Chain Attacks
Attacks that compromise our CI/CD pipeline, allowing a malicious actor to
point our PyPI package or Docker images (GHCR or Docker Hub) to vulnerable
or tampered artifacts.

P1: Unauthenticated Proxy Access
Application-level attacks where an unauthenticated user is able to gain
access to protected data on a LiteLLM proxy instance that should be
protected (e.g api keys).

P2: Authenticated Malicious Actions
Application-level attacks where an authenticated user is able to perform
actions beyond their intended permissions, such as privilege escalation or
unauthorized data access.

| Severity | Bounty Range         | Example                          |
|----------|----------------------|----------------------------------|
| Critical | $1,500 - $3,000      | P0 supply chain compromise       |
| High     | $500 - $1,500        | P1 unauthenticated proxy access  |
| Medium   | N/A                  | P2 authenticated privilege escalation |
| Low      | N/A                  | Minor information disclosure, low-impact misconfigurations |

### Known Non-Issues

- Attacks that require a misconfiguration on setup (e.g not setting a
  `master_key` on the proxy configuration), are **explicitly not in scope**
  and are not considered vulnerable.
```

### At-rest encryption scope (encryption FAQ —
/docs/proxy/security_encryption_faq, verbatim)

```
#### NOT Encrypted:

1.  **Spend Logs** - Request/response data in `LiteLLM_SpendLogs`
2.  **Audit Logs** - Change history in `LiteLLM_AuditLog`
3.  **User/Team/Organization Data** - Metadata and configuration
4.  **Cached Prompts and Completions** - Cache data is stored in plaintext

Algorithm: NaCl SecretBox (XSalsa20-Poly1305 AEAD)

**Never change this key** - encrypted data becomes unrecoverable
```

### Shared-responsibility split (shared responsibility page —
/docs/shared_responsibility, verbatim excerpt)

```
In a nutshell, we own the behavior of the product as documented on this
site, and you own the environment it runs in + any code you add to it.

| Area                                                             | Owner    |
|------------------------------------------------------------------|----------|
| Security patches and the official Docker image and Helm chart    | LiteLLM  |
| Uptime of your instance and the infrastructure under it          | You      |
| Custom callbacks, custom guardrails, custom auth, and other code |
| you inject                                                       | You      |
```

## Cross-References

- **Corroborates**:
  - `failure-litellm-security-hardening-april-2026.md` (Concrete Artifacts →
    Bug bounty program) — that note records the bug bounty tiers
    ($1,500–$3,000 Critical/P0, $500–$1,500 High/P1) announced with the April
    2026 disclosures; `security.md` (followed here) confirms the same tiers
    as the standing program terms and adds the P0/P1/P2 category taxonomy and
    the P2-ineligible rule, which that note did not cover. This page's
    disclosure-channel claims (Claim 4) describe the intake path those
    disclosures arrived through.
  - `failure-litellm-supply-chain-incident-march-2026.md` (Extracted Claims →
    Claim 14) — the pinned-SHA/cooldown/zizmor CI hardening that note
    documents is the release-pipeline counterpart to this page's grype
    image-scan claim (Claim 6): both are supply-chain scanning/hygiene
    practices in the same CircleCI estate, at different stages (dependency
    pinning of the pipeline vs. scanning of built image contents).

- **Contradicts**: None filed. The one candidate tension the Prospector
  flagged — "0 High/Critical severity vulnerabilities found" (Claim 6) vs.
  the app-layer CVEs in `failure-litellm-security-hardening-april-2026.md` —
  is a **scan-scope difference, not a claim opposition**: grype scans OS
  packages/dependencies inside built Docker images; none of CVE-2026-35030,
  CVE-2026-35029, or GHSA-69x8-hrgq-fjj8 is a container-dependency
  vulnerability, and the PyPI release-path compromise
  (`failure-litellm-supply-chain-incident-march-2026.md`) exfiltrated
  release *credentials* rather than shipping a vulnerable image layer. Both
  statements are simultaneously true; per MINER §4a ("claims differ only in
  context… that's not a contradiction") and the Prospector's explicit
  guidance, no contradiction issue is filed. The scan-scope framing rule is
  carried into Guide Impact instead.

- **Extends**:
  - `failure-litellm-security-hardening-april-2026.md` — this page is the
    vendor's *assurance* counterpart to that note's CVE disclosures (its
    Source Context scopes the page as covering three vulnerabilities and
    nothing else). This note adds the process framing the disclosures
    assumed (disclosure channel, video requirement, scan posture) and the
    omission inventory that note could not see. Pairs as: what went wrong
    (April disclosures) vs. what the trust page promises (this page).
  - `failure-litellm-guardrail-logging-secret-exposure.md` (Concrete
    Artifacts → Exposure surfaces; Extracted Lessons → Lesson 1) — that
    note's incident is the empirical counterexample to this page's silence
    on log redaction (Claim 2/Claim 9): plaintext `Authorization` headers
    reached spend logs and OTEL traces, which the encryption FAQ confirms
    are unencrypted stores. The two notes together justify the "vendor page
    silent on log redaction → operator owns it, and here's proof it leaks"
    rule.
  - `docs-litellm-gateway-auth-reference.md` — that note covers the MCP/A2A
    gateway auth *surface*; this page adds the two adjacent facts it did not
    carry: the Admin UI session-cookie contract (24h JWT, Claim 3) and the
    audit-log event coverage (auth/create/update only, Claim 7). Same
    vendor, complementary slices of the auth/audit surface.
  - `failure-litellm-supply-chain-compromise-march-2026.md` — the initial
    supply-chain disclosure whose aftermath (P0 category, bounty program,
    CI hardening) shows up as this page's scanning and disclosure process.
    Claim 10's P0 taxonomy is governance shaped by that incident.

- **Novel**: First source note in the corpus covering:
  1. **Video-PoC-required vulnerability disclosure as an anti-AI-spam
     control** — an intake policy adapted to LLM-generated junk reports,
     with explicit close-without-review enforcement. No other note in the
     corpus documents AI-volume-driven changes to a security-governance
     process.
  2. **The dated, verbatim self-host "no telemetry / no data" vendor
     commitment** — previously unrecorded; now citable as a vendor
     assertion with the mechanism-gap caveat attached.
  3. **The 24-hour JWT Admin UI session-cookie contract** — concrete
     session-hygiene numbers (24h ceiling, browser-close expiry, no
     third-party cookies) for the gateway UI.
  4. **The encryption-at-rest scope map** (NaCl SecretBox over
     credentials/config only; spend logs, audit logs, org data, and caches
     plaintext) and the **shared-responsibility ownership table** — from the
     vendor's own adjacent pages, filling this page's omission inventory
     with vendor-attested answers.
  5. **The P0/P1/P2 vulnerability-category taxonomy** and the
     misconfiguration-out-of-scope clause as published program terms.

## Guide Impact

- **Chapter 06 (Security & Trust) — data governance / compliance as
  engineering**: Add a "vendor trust-page reading rule": *silence is not
  safety; omissions are operator-owned inventory*. Use this page as the
  worked example — enumerate what it does not say (encryption, key
  management, log redaction, retention, backups, multi-tenant isolation),
  then follow the vendor's own links to see the answer (encryption FAQ:
  spend logs/caches plaintext; shared responsibility: environment +
  injected code are yours). Cite Claims 1–3 and 9.
- **Chapter 06 — AI-era vulnerability intake**: Add the video-PoC disclosure
  pattern (Claim 5) as a governance pattern with its tradeoff: raising
  report cost to filter AI-generated junk works but filters text-only human
  reporters; `security.md`'s reopen-on-video-added clause is the mitigation.
  Relevant to any project maintaining an LLM-adjacent OSS gateway.
- **Chapter 06 — scan-scope discipline**: Add the explicit rule that
  "vendor reports 0 High/Critical in Docker images" (grype, Claim 6) and
  "vendor disclosed app-layer CVEs" are not in conflict; container
  dependency scans do not measure application security. Cite Claim 6 with
  `failure-litellm-security-hardening-april-2026.md` and
  `failure-litellm-supply-chain-incident-march-2026.md` as the two sides.
- **Chapter 05 (LLM Ops Reliability) / Ch06 self-host checklist**: Add the
  checkable items this page uniquely provides — 24h Admin UI session-cookie
  ceiling (Claim 3), egress verification of the "no telemetry" claim
  (Claim 1), and the fact that SSO/SAML and audit logs are Enterprise-tier
  (Claim 8), so OSS self-hosters must supply their own IdP and change
  auditing. The `master_key` misconfiguration carve-out (Claim 10) bounds
  the "secure by default" claim and belongs in the same checklist.

## Extraction Notes

- Primary source read in full via WebFetch of
  `https://docs.litellm.ai/docs/data_security` (HTTP 200, no paywall, thin
  ~1.5 KB body). Three linked substantive pages followed per MINER §1
  (budget: up to 5): the canonical in-repo `security.md`
  (BerriAI/litellm, raw fetch), `/docs/shared_responsibility` (the page's
  "Next" link), and `/docs/proxy/security_encryption_faq` (Enterprise
  sidebar link the Prospector flagged as where "encryption" content
  actually lives). The audit-logs target
  (`/docs/proxy/multiple_admins#1-switch-on-audit-logs`) was not fetched —
  the event-coverage claim is extractable from this page's own Q&A and the
  note carries enough substance without it.
- All `Quote` fields and Concrete Artifacts were copied character-for-
  character from the fetched rendered text of the respective pages;
  sub-page quotes carry explicit `(security.md, …)` / `(encryption FAQ …)`
  / `(shared responsibility …)` attributions. No quotes were spliced
  across non-adjacent sentences.
- `miner-related-notes.md` was read before writing Cross-References (per
  MINER §4). All ten listed candidates were evaluated and **dismissed** —
  none has security/compliance/privacy content overlapping this vendor
  trust page: `docs-litellm-batches-api.md`, `docs-litellm-completion-web-search.md`,
  `docs-litellm-generate-content.md`, `docs-litellm-completion-input-params.md`,
  `docs-litellm-files-endpoints.md`, `docs-litellm-bedrock-invoke.md`,
  `docs-litellm-audio-transcription.md`, `docs-litellm-creating-adapters.md`,
  `docs-litellm-completion-web-fetch.md` (all LiteLLM API-surface feature
  docs — no data-governance or security-process content), and
  `docs-google-sre-prodcast-04-09-ai-agents.md` (agent definitions/guardrail
  philosophy — not LiteLLM vendor security). Cross-references above were
  instead sourced from the overlapping notes named in the Prospector's
  triage on #1651 and verified against those notes' actual section
  structure per MINER §4b (failure notes cited by section name — e.g.
  "Concrete Artifacts → Exposure surfaces" — not by invented claim
  numbers; those notes do not number their claims in `### Claim N` form).
- No contradiction issue filed: the grype-vs-CVEs tension is a scan-scope
  difference (reasoning in Cross-References → Contradicts); open
  `contradiction`-labeled issues and existing `C-NNN` entries were checked
  and none covers LiteLLM trust-page material.
- `confidence_overall` is `emerging`: every positive claim on this page is
  an unvalidated vendor assurance (per Prospector instruction, the
  assurance framing is never upgraded to practitioner-validated evidence);
  the claims are kept because they are specific, falsifiable, and several
  are independently checkable (cookie expiry, scan CI link, disclosure
  channel). The failure-report cross-refs supply the practitioner
  grounding this page lacks.
- `date_published` is unknown (living Docusaurus vendor page; no date
  shown). `date_extracted` and `last_checked` are both 2026-10-18.
