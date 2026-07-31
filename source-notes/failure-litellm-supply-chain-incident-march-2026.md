---
source_url: https://docs.litellm.ai/blog/security-townhall-updates
source_type: failure-report
title: "Security Townhall Updates"
author: "Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-03-27
date_extracted: 2026-07-31
last_checked: 2026-07-31
status: current
confidence_overall: settled
issue: "#686"
---

# Failure Report: LiteLLM PyPI supply-chain incident (v1.82.7/v1.82.8, 2026-03-24)

> The primary vendor incident report for the March 24, 2026 LiteLLM supply-chain
> compromise — a compromised, unpinned Trivy dependency in the shared CircleCI
> release pipeline exfiltrated static PyPI/GHCR/Docker release credentials and
> published two poisoned versions to PyPI (~40-minute exposure). This source is
> the incident half (timeline, root cause, containment, Cosign release-signing
> roadmap) that the April townhall note reports as the delivered CI/CD v2 response.

## Source Context

- **Type**: failure-report (vendor incident post-mortem / townhall retrospective,
  written version of the March 2026 security town hall). Tagged `security`,
  `incident-report`.
- **Platform**: Vendor blog post on `docs.litellm.ai/blog` (Docusaurus).
- **Author credibility**: High for facts about LiteLLM's own incident — authored
  by Krrish Dholakia (CEO) and Ishaan Jaffer (CTO) of BerriAI/LiteLLM, published
  as the written version of a live town hall. Self-reported, but the incident
  facts are independently corroborated in the corpus: the sibling April townhall
  note (`blog-litellm-april-townhall-updates.md`) treats this incident as the
  driver of CI/CD v2, and the post cites external parties (Google's Mandiant,
  Veria Labs whitehat review, PyPI quarantine) that verify the timeline.
- **Scope**: Covers (1) what happened — the timeline with exact exposure-window
  numbers; (2) how it happened — three contributing factors; (3) what they've
  already done — containment; (4) the prevention roadmap — 4 guiding principles,
  isolated per-stage CI/CD environments, ephemeral credentials, Cosign release
  auditing, avoid-compromised-packages (zizmor); (5) FAQ (lateral movement,
  older-package impact). Does NOT cover: the earlier short initial disclosure
  ("Security Update: Suspected Supply Chain Incident", tracked in sibling issue
  #687), the full CI/CD v2 delivery (April townhall), or the separate
  vulnerability disclosures (April 3 security-hardening post).

### Failure-Report Profile

- **What was attempted**: LiteLLM's normal release process — build, security-scan,
  and publish LLM-gateway releases to PyPI and GHCR through a shared CircleCI
  pipeline using static release credentials stored in environment variables.
- **What went wrong**: Two poisoned versions (v1.82.7, v1.82.8) pushed to PyPI on
  2026-03-24 at 10:39 UTC, live ~40 minutes before PyPI quarantine, deleted by
  16:00 UTC. Attackers obtained release credentials via a compromised Trivy
  dependency in the security-scan step.
- **Root cause (author's diagnosis)**: Unpinned Trivy dependency in the security
  scanning component ran a compromised package during the scan; because all
  CircleCI steps shared one environment holding static long-lived PyPI/GHCR/Docker
  release credentials, the compromised package exfiltrated them.
- **What they switched to**: Rotated/revoked all affected secrets and maintainer
  accounts; removed ~6,000 open branches + auto-deletion policy; pinned GitHub
  Actions; paused releases; and began a prevention roadmap (isolated per-stage CI
  environments, ephemeral credentials, Cosign signing, zizmor).
- **Our take**: A real, self-inflicted CI supply-chain compromise — the failures
  (shared env, static long-lived release creds, unpinned build tool) are all
  classic, preventable anti-patterns, and the remediation is textbook
  supply-chain hardening. The incident facts read as settled; the roadmap items
  are later reported delivered by the April/May/June townhall notes.

## Extracted Claims

### Claim 1: Incident timeline — v1.82.7/v1.82.8 pushed to PyPI at 10:39 UTC on 2026-03-24, live ~40 minutes before PyPI quarantine, and deleted by 16:00 UTC the same day
- **Evidence**: Explicit timeline with exact times; the ~40-minute exposure window
  and 16:00 UTC deletion are concrete, citable numbers.
- **Confidence**: settled
- **Quote**: "On March 24, 2026 at 10:39 UTC, LiteLLM v1.82.7 was pushed to PyPI. Version v1.82.8 was published soon after. Those packages were live for about 40 minutes before being quarantined by PyPI. By 16:00 UTC, the LiteLLM team had worked with PyPI to delete the affected packages."
- **Our assessment**: Retrospective vendor report with concrete numbers; the
  exposure-window metric (~40 min from push to quarantine) is the key citable
  quantity. Consistent with the sibling initial-disclosure post and the April
  townhall, which both treat this as the incident. We buy it — a short window,
  plausibly caught by PyPI's own malicious-upload detection.

### Claim 2: The incident is classified as a supply-chain incident limited to the two poisoned releases — no malicious code was pushed to main
- **Evidence**: Stated classification plus a separate containment statement that
  main was clean.
- **Confidence**: settled
- **Quote**: "At this point, our understanding is that this was a supply-chain incident affecting those two published versions."
- **Quote**: "We also confirmed that no malicious code was pushed to main."
- **Our assessment**: The classification bounds the incident to the release path,
  not the codebase. The "no malicious code on main" claim is the key reassurance
  for downstream users deciding whether older releases are safe — and it is
  independently reviewed (see Claim 9).

### Claim 3: Root cause — a compromised Trivy security-scanner dependency in the CI/CD pipeline (the unpinned-Trivy contributing factor)
- **Evidence**: Stated root cause; the compromised package ran during the
  security-scan step, had access to environment variables, and let attackers
  obtain release credentials.
- **Confidence**: settled
- **Quote**: "Our understanding is that the issue came from the compromised Trivy security scanner dependency in our CI/CD pipeline."
- **Quote**: "In our security scanning component, we had an unpinned Trivy dependency. Our present understanding is that a compromised Trivy package ran during the scan, had access to environment variables, and enabled attackers to obtain those credentials."
- **Quote**: "a compromised package in CI had access to secrets it should not have had, and those secrets were then used in the release path."
- **Our assessment**: A textbook CI supply-chain compromise: an unpinned build
  dependency pulled a malicious version, ran in the scan step with broad
  environment access, and exfiltrated credentials. Notable irony — the compromised
  tool was the *security scanner*, the very component meant to catch this class of
  issue. The entry vector (unpinned Trivy) maps directly onto the
  pinned-SHA/cooldown remediation in Claim 14.

### Claim 4: Contributing factor 1 — all CircleCI steps shared a common environment, increasing blast radius
- **Evidence**: Explicitly listed as the first of three major contributing
  factors.
- **Confidence**: settled
- **Quote**: "At the time, everything was running on CircleCI, and all steps shared a common environment. That increased blast radius: if one component was compromised, it could potentially access credentials or context intended for other parts of the pipeline."
- **Our assessment**: The classic "no isolation between pipeline stages"
  anti-pattern. One compromised step inherited the whole pipeline's access
  context. This is the direct driver of the isolated-environments remediation
  (Claim 11).

### Claim 5: Contributing factor 2 — static long-lived release credentials (PyPI, GHCR, Docker) stored as environment variables
- **Evidence**: Explicitly listed as the second contributing factor, naming the
  three credential stores.
- **Confidence**: settled
- **Quote**: "Release credentials, including credentials for PyPI, GHCR, and Docker publishing, were available as static secrets in the environment. That meant a compromised step could access long-lived release credentials."
- **Our assessment**: Static, long-lived, env-var-scoped release credentials are
  the second half of the attack chain — the compromised step could reach them
  directly with no further work. This is exactly the risk that ephemeral
  credentials (Trusted Publisher, GHCR token auth — Claim 12) are designed to
  remove.

### Claim 6: Containment — all impacted or adjacent secrets deleted/rotated, and LiteLLM maintainer accounts rotated out of caution
- **Evidence**: Stated action taken in the first 3 days.
- **Confidence**: settled
- **Quote**: "We deleted or rotated all impacted or adjacent secret keys, including PyPI, GitHub, Docker, and related credentials. Out of an abundance of caution, we've also rotated LiteLLM maintainer accounts."
- **Our assessment**: Standard-but-thorough secret rotation; rotating maintainer
  accounts goes beyond the leaked release secrets and acknowledges the compromised
  step may have touched context beyond the credential stores. Good
  blast-radius-first practice.

### Claim 7: Containment — branch attack surface reduced (~6,000 open branches removed, auto-deletion policy for branches merged into main)
- **Evidence**: Stated action.
- **Confidence**: settled
- **Quote**: "We removed roughly 6,000 open branches and added an auto-deletion policy for branches merged into main. This reduces the surface area for branch-based abuse."
- **Our assessment**: An unusual but concrete supply-chain containment step —
  stale open branches are a common CI-trigger and credential-holder surface (many
  CI systems run jobs against branch pushes). The auto-deletion *policy* (not just
  a one-time cleanup) is the durable part; 6,000 open branches is a striking
  number for a repo this active.

### Claim 8: Containment — all GitHub Actions pinned, CircleCI pinning in progress, and new releases paused
- **Evidence**: Stated actions.
- **Confidence**: settled
- **Quote**: "We've pinned all Github Actions, and are working on pinning all CircleCI dependencies as well."
- **Quote**: "We've paused new releases until we've confirmed codebase security and put stronger release controls in place."
- **Our assessment**: Pinning (to verified SHAs) directly addresses the unpinned
  dependency root cause; pausing releases is the "stop the bleeding" response that
  gives forensics time. Both are directly traceable to the incident's root cause.

### Claim 9: Verification evidence — Mandiant forensics, last 20 releases contain no indicators of compromise, no unauthenticated attack on the proxy, independent Veria Labs review
- **Evidence**: Stated verification results attributed to Google's Mandiant and
  Veria Labs.
- **Confidence**: settled
- **Quote**: "We are working with Google's Mandiant cybersecurity team to confirm the source of the attack and verify the security of the codebase."
- **Quote**: "We have also confirmed that the last 20 LiteLLM releases contain no indicators of compromise, and that no unauthenticated attacks can be made against LiteLLM Proxy based on our current investigation."
- **Quote**: "Our current findings show no indicators of compromise in the last 20 versions of LiteLLM. This was manually verified by our team and independently reviewed by Veria Labs."
- **Our assessment**: This is the scope-of-impact bound that lets downstream users
  evaluate their exposure: the incident was contained to two releases, and 20 prior
  releases were reviewed. The independent parties (Mandiant forensics, Veria Labs
  whitehat review) raise credibility above a bare vendor assertion, though a
  "no IoC in last 20 releases" check is only as strong as the detection coverage
  applied to them.

### Claim 10: Prevention roadmap — four guiding principles for the new CI/CD pipeline (limit package access, reduce sensitive env vars, avoid compromised packages, prevent release tampering)
- **Evidence**: Stated as the four guiding principles for the new pipeline; these
  are the same four goals the April townhall reports delivered as CI/CD v2.
- **Confidence**: settled
- **Quote**: "Limit what each package can access / Reduce the number of sensitive environment variables / Avoid compromised packages / Prevent release tampering"
- **Our assessment**: This is the origin of the four-goal CI/CD v2 framework that
  `blog-litellm-april-townhall-updates.md` (Claim 1) reports as delivered. Each
  principle maps to a contributing factor: limit package access + reduce sensitive
  env vars → factors 1–2; avoid compromised packages → factor 3; prevent release
  tampering → the Cosign work (Claim 13).

### Claim 11: Isolated CI/CD environments — the pipeline is broken into 4 semantic concepts (unit tests, integration tests, security scans, release publishing), each run in isolation
- **Evidence**: Stated plan with the four named stages and the rationale.
- **Confidence**: emerging
- **Quote**: "We are breaking our CI/CD into 4 semantic concepts: Unit tests / Integration tests / Security scans / Release publishing / And will be running each of these in isolated environments."
- **Quote**: "This will limit the damage that any single compromised component can cause."
- **Our assessment**: Direct blast-radius containment for the factor-1 shared
  environment. The four-stage split is concrete and copyable — a sensible default
  taxonomy for any LLM-gateway or proxy release pipeline. Forward-looking at
  publication; the April townhall note reports it begun, so emerging at the
  claim level.

### Claim 12: Ephemeral credentials — moving to PyPI Trusted Publisher and GHCR token-based authentication, with both migrations already begun
- **Evidence**: Stated plan plus two linked migration PRs ("already begun").
- **Confidence**: emerging
- **Quote**: "We plan to move to ephemeral credentials for PyPI (Trusted Publisher) and GHCR (Token-based authentication) releases. This will reduce the risk of credentials being leaked or compromised."
- **Our assessment**: Directly addresses the static-credential contributing
  factor. Trusted Publisher and GHCR token-based auth are the standard
  ephemeral-credential mechanisms for OSS releases — a best-practice migration,
  not a novel mechanism. The "already begun with PRs" detail signals the
  migration was real, not aspirational.

### Claim 13: Release auditing — Cosign signing shipped in PR #24683; all GHCR Docker images signed from v1.83.0-nightly with a pinned-commit key
- **Evidence**: Shipped PR number and starting version stated; two concrete
  `cosign verify` command variants provided (see Concrete Artifacts).
- **Confidence**: settled
- **Quote**: "Our goal is to allow users to independently verify that a release came from us and prevent silent modifications of releases after they are published."
- **Quote**: "We believe that Cosign is a good fit for this, and have shipped it in PR #24683."
- **Quote**: "Starting from v1.83.0-nightly, all LiteLLM Docker images published to GHCR are signed with cosign. Every release is signed with the same key that was introduced in commit 0112e53."
- **Our assessment**: This is the release-tampering countermeasure (guiding
  principle 4), and it is the most copyable artifact in the source. The
  pinned-commit-key verification mode (verify against the `cosign.pub` at an
  immutable commit hash, not a mutable tag) is the strongest practice — it does
  not trust a tag that could itself be mutated. Reported as shipped, so settled.

### Claim 14: Avoid compromised packages — pin to verified SHAs, add an upgrade cooldown period, and add zizmor to catch unpinned deps and credential leakage
- **Evidence**: Stated practices; zizmor added via a linked commit.
- **Confidence**: settled (zizmor added; pinned-SHA policy is a stated intent)
- **Quote**: "Move to pinned, verified SHAs for packages and actions used in CI/CD, avoiding latest wherever possible."
- **Quote**: "Add a cooldown period before upgrading to a new version of a package - allows more time to investigate and verify the new version."
- **Quote**: "We've added zizmor to help us catch issues such as unpinned dependencies and credential leakage."
- **Our assessment**: The pinned-SHA + cooldown combination is the direct fix for
  the unpinned-Trivy factor. zizmor (a GitHub Actions security scanner) is the
  automated guard against both unpinned dependencies and credential leakage — this
  is the origin of the zizmor toolchain that the May/June townhall notes report
  running on every PR.

### Claim 15: FAQ — no lateral movement into the corporate environment; the incident was isolated to the CI/CD pipeline and the release path for v1.82.7 and v1.82.8
- **Evidence**: FAQ response to a direct question.
- **Confidence**: settled
- **Quote**: "No. Our investigation to date, conducted in coordination with external security experts, has found no evidence of lateral movement into our internal corporate systems. The incident was isolated to the CI/CD pipeline and the release path for specific versions (v1.82.7 and v1.82.8)."
- **Our assessment**: The blast-radius bound (CI/CD pipeline + two releases only)
  is important for downstream users deciding whether to trust the codebase and
  other releases. The coordination with external security experts is cited, which
  strengthens the claim relative to a bare assertion.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/blog/security-townhall-updates.

### Incident timeline (verbatim)

```
On March 24, 2026 at 10:39 UTC, LiteLLM v1.82.7 was pushed to PyPI. Version
v1.82.8 was published soon after. Those packages were live for about 40 minutes
before being quarantined by PyPI. By 16:00 UTC, the LiteLLM team had worked with
PyPI to delete the affected packages.
```

### Three contributing factors (verbatim summary)

```
In summary: a compromised package in CI had access to secrets it should not have
had, and those secrets were then used in the release path.
```

```
1. Shared CI/CD environment — at the time, everything was running on CircleCI,
   and all steps shared a common environment.
2. Static credentials in environment variables — release credentials, including
   PyPI, GHCR, and Docker publishing, were available as static secrets in the
   environment.
3. Unpinned Trivy dependency — in our security scanning component, we had an
   unpinned Trivy dependency.
```

### Cosign release verification commands (verbatim)

Verify using the pinned commit hash (recommended) — a commit hash is
cryptographically immutable, so this is the strongest way to ensure you are using
the original signing key:

```
cosign verify \
--key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub \
ghcr.io/berriai/litellm:<release-tag>
```

Verify using a release tag (convenience) — tags are protected in this repository
and resolve to the same key:

```
cosign verify \
--key https://raw.githubusercontent.com/BerriAI/litellm/<release-tag>/cosign.pub \
ghcr.io/berriai/litellm:<release-tag>
```

Replace `<release-tag>` with the version you are deploying (e.g. `v1.83.0-stable`).
Expected output:

```
The following checks were performed on each of these signatures:
- The cosign claims were validated
- The signatures were verified against the specified public key
```

### Four guiding principles for the new CI/CD pipeline (verbatim)

```
Limit what each package can access
Reduce the number of sensitive environment variables
Avoid compromised packages
Prevent release tampering
```

### Four isolated CI/CD environment concepts (verbatim)

```
Unit tests
Integration tests
Security scans
Release publishing
```

### Avoid-compromised-packages practices (verbatim)

```
Move to pinned, verified SHAs for packages and actions used in CI/CD, avoiding
latest wherever possible.
Add a cooldown period before upgrading to a new version of a package - allows
more time to investigate and verify the new version.
We've added zizmor to help us catch issues such as unpinned dependencies and
credential leakage.
```

## Cross-References

- **Corroborates**:
  - `blog-litellm-april-townhall-updates.md` **Claim 1** (CI/CD v2 is organized
    around four supply-chain/isolation goals) — this source's four guiding
    principles are the *origin* of those goals; the wording is near-identical
    ("Limit what each package can access / Reduce the number of sensitive
    environment variables / Avoid compromised packages / Prevent release
    tampering" here vs. "Reduce the risk of release tampering" in the April note).
  - `blog-litellm-april-townhall-updates.md` **Claim 2** (isolated environments
    per CI/CD stage) — corroborates; this source names the concrete four-stage
    split (unit / integration / security-scan / release) that the April note
    reports as begun.
  - `blog-litellm-april-townhall-updates.md` **Claim 3** (independent verification
    of release artifacts) — corroborates the release-auditing goal that this
    source's Cosign work (Claim 13) delivers.
  - `blog-litellm-may-townhall-updates.md` **Claim 4** (every PR requires a Veria
    AI + zizmor + semgrep scan) — the zizmor adoption this source announces is the
    seed of that required-check toolchain.
  - `blog-litellm-june-townhall-updates.md` **Claim 8** (Veria scan required on
    every PR) — same toolchain origin; the June note reports it as a standing
    required check.
- **Contradicts**: None. No contradiction issue filed. All overlapping notes
  (April/May/June townhalls) report *follow-through* on this incident's roadmap
  (CI/CD v2 delivery, zizmor/Veria PR scanning), so they extend rather than oppose
  it. Verified per §4b: no existing note claims shared CI environments or static
  release credentials are safe, or that the incident didn't happen.
- **Extends**:
  - `failure-litellm-security-hardening-april-2026.md` — that note explicitly
    scopes the supply-chain incident *out* ("Does not cover the supply chain
    incident that prompted the audit"); this note supplies the incident facts
    that note excludes. Together they complete LiteLLM's April 2026 security
    picture: the April 3 post is the vulnerability disclosures that followed the
    audit, this note is the incident that prompted it.
  - `blog-litellm-april-townhall-updates.md` — this note (Mar 27) is the incident
    half; the April townhall (Apr 10) is the response/delivery half. Before/after
    pair: roadmap → delivered CI/CD v2.
  - `blog-litellm-may-townhall-updates.md` / `blog-litellm-june-townhall-updates.md`
    — post-incident security tooling follow-through (Veria + zizmor + semgrep as a
    required PR check, bug bounty).
  - `failure-litellm-guardrail-logging-secret-exposure.md` — that note lists the
    "Suspected Supply Chain Incident" post in its sidebar but does not cover its
    content; this note provides the detailed incident facts behind that
    sibling disclosure.
- **Novel**: First source note in the corpus to mine the incident itself. New to
  the corpus:
  - The concrete incident timeline and exposure-window numbers (10:39 UTC push,
    ~40-min live window, 16:00 UTC deletion).
  - The three contributing factors as a named anti-pattern set (shared CI
    environment, static long-lived release creds in env vars, unpinned scan
    dependency).
  - The containment actions specific to this incident (deleting ~6,000 open
    branches + auto-deletion policy, maintainer-account rotation).
  - The **Cosign release-signing workflow with pinned-commit-key verification** —
    the first copyable `cosign verify` commands in the corpus, including the
    expected-output text.
  - The ephemeral-credentials migration (PyPI Trusted Publisher + GHCR token-based
    auth) and the cooldown-before-upgrade policy.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Add a supply-chain / release-pipeline
  hardening subsection. Ch06 currently has no coverage of release-supply-chain
  risk (no "supply" or "release signing" content; the security content is threat
  landscape, red-teaming CI gates, compliance, data governance). Add:
  - The three contributing-factor anti-patterns as a "don't do this" list for LLM
    gateway operators: shared CI/CD environment across stages, static long-lived
    release credentials in env vars, unpinned security-scan dependencies.
  - The four remediation patterns from the roadmap: isolated per-stage CI/CD
    environments, ephemeral credentials (PyPI Trusted Publisher, GHCR token-based
    auth), release signing with Cosign using a pinned-commit key, and
    pinned-SHA + cooldown + zizmor dependency hygiene.
  - The copyable `cosign verify` commands (pinned-commit and release-tag modes)
    as the reference workflow for verifying a gateway release image against an
    immutable signing key.
- **Chapter 01 (Incident Response)**: Ch01 is currently a stub with no sourced
  claims. This is a strong candidate for its first sourced content: the incident
  report structure as a supply-chain postmortem template — quantified exposure
  window, named contributing factors, containment sequence (secret rotation,
  branch-surface reduction, release pause), and independent forensics (Mandiant,
  Veria Labs). The "no malicious code on main" + "last 20 releases clean"
  verification is a reusable pattern for scoping downstream-user impact in any
  supply-chain incident report.
- **Chapter 05 (LLM Ops Reliability)**: Add release verification as an operator
  practice — how a user verifies a LiteLLM (or any proxy) Docker image against the
  pinned signing key, and the ephemeral-credential migration as release-engineering
  practice for the release pipeline.

## Extraction Notes

- Source read in full. Single self-contained Docusaurus blog post (published
  2026-03-27 by Krrish Dholakia, CEO, and Ishaan Jaffer, CTO; ~13.5 KB of
  extracted text). No sub-pages followed: the "Slides available here" link is
  external (slide deck, not needed per the triage note), and the linked GitHub PRs
  (Cosign PR #24683, PyPI Trusted Publisher PR, GHCR token-auth PR, zizmor commit)
  are referenced for attribution but their content was not fetched.
- All quoted passages were copied character-for-character from the rendered page
  text. The page is a Next.js render; HTML-to-text extraction introduced line
  breaks where the source uses inline links/code (e.g., "compromised Trivy security
  scanner", "Limit what each package can access", "cosign verify" blocks). Every
  quoted sentence was re-verified as a contiguous string against the
  whitespace-normalized page text before inclusion.
- `confidence_overall` set to `settled`: the bulk of the note is retrospective,
  concrete incident fact (timeline, contributing factors, containment,
  verification) that is independently corroborated in the corpus (April townhall
  treats the incident as the CI/CD v2 driver; May/June notes report the security
  toolchain follow-through). The roadmap claims (isolated envs, ephemeral creds)
  were forward-looking at publication and are flagged `emerging` at the claim
  level, but the April note reports them begun/delivered, so the overall posture
  is settled rather than emerging.
- The `miner-related-notes.md` candidates list was read per §4. All 10 candidates
  evaluated:
  - `blog-litellm-may-townhall-updates.md` — cited under Corroborates (zizmor
    toolchain origin).
  - `blog-litellm-april-townhall-updates.md` — cited extensively under
    Corroborates and Extends (the delivered CI/CD v2 response to this incident).
  - `blog-litellm-june-townhall-updates.md` — cited under Corroborates (Veria
    scan as required PR check).
  - `docs-langfuse-security-and-guardrails.md` — not cited; Langfuse guardrail
    architecture is unrelated to the LiteLLM supply-chain incident. Dismissed.
  - `docs-langfuse-mcp-server.md` — not cited; MCP server docs unrelated.
    Dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — not cited; agent-definition
    spectrum unrelated. Dismissed.
  - `blog-litellm-save-claude-code-costs.md` — not cited; Claude Code cost
    optimization unrelated. Dismissed.
  - `docs-google-sre-reliable-product-launches.md` — not cited; launch engineering
    unrelated. Dismissed.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — not cited; SLO framework
    unrelated. Dismissed.
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` — not cited;
    client-transparent migrations unrelated. Dismissed.
  Additional cross-references (`failure-litellm-security-hardening-april-2026.md`,
  `failure-litellm-guardrail-logging-secret-exposure.md`) were discovered by
  reading the overlapping notes named in the Prospector's triage.
- No contradiction issue filed: verified against all existing source notes. No
  existing note makes a claim opposed by this source — the April/May/June notes
  report delivery of this incident's roadmap, and the security-hardening note
  explicitly scopes the incident out. The relationship is incident → response, not
  a disagreement.
