---
source_url: https://www.cncf.io/blog/2026/06/26/securing-ci-cd-for-an-open-source-project-part-3-credentials-verification-and-whats-next
source_type: blog-post
title: "Securing CI/CD for an open source project, part 3: Credentials, verification, and what's next"
author: "André Martins (Cilium maintainer and Software Engineer, Isovalent at Cisco) and Feroz Salam (Cilium Security Team and Security Engineer, Isovalent at Cisco)"
date_published: 2026-06-26
date_extracted: 2026-10-11
last_checked: 2026-10-11
status: current
confidence_overall: emerging
issue: "#1676"
---

# Securing CI/CD for an open source project, part 3: Credentials, verification, and what's next

> Cilium's first-party account of its release-pipeline credential isolation:
> two separately scoped registry credential sets behind distinct protected
> GitHub environments (CI creds reach only `quay.io/cilium/*-ci`; production
> creds sit behind a maintainer-approved `release` environment), keyless-OIDC
> Cosign signing with SBOM attestation, `persist-credentials: false` on every
> checkout, and a candid list of the gaps still open — most usefully that
> `provenance: false` on every build means consumers can verify *who* signed but
> not *how* it was built. This is the positive-implementation counterpart to the
> LiteLLM March 2026 supply-chain incident already in the corpus.

## Source Context

- **Type**: blog-post (CNCF Member Post — the third and final part of a
  three-part series on how the Cilium project hardens its own CI/CD pipeline.
  Part 1 covered access control, Part 2 covered dependency hardening).
- **Author credibility**: High for a first-party engineering account. Authors
  are André Martins (Cilium maintainer, Software Engineer at Isovalent/Cisco)
  and Feroz Salam (Cilium Security Team, Security Engineer at Isovalent/Cisco).
  The post describes the project's actual configuration and names its own
  weaknesses. The concrete mechanisms (protected environments,
  `persist-credentials`, the `.github/actions/cosign/action.yaml` composite
  action, the 68 `@main` refs) are checkable in Cilium's public repository, but
  the claim set is a self-report and is not independently verified.
- **Scope**: Covers credential protection (minimal `GITHUB_TOKEN` defaults, two
  protected-environment credential sets, `persist-credentials: false`), signing
  and attesting (keyless-OIDC Cosign, SPDX SBOM attestation, release
  environments), the project security team's operational role, additional
  layers (tag immutability, DCO sign-off, third-party audits), an audited gap
  list, and a mapping of GitHub's 2026 Actions security roadmap. Does NOT cover
  the release process specifics (Helm chart OCI artifacts, DCO bot internals,
  ADA Logics audit findings) or any AI/LLM content — this is a general CI/CD
  supply-chain post for a Go CNCF project, and no reliability metrics, latency
  numbers, or incident data are present.
- **Prospector framing**: Triage (three concurrent runs) routed this as
  `triaged:text`, novelty medium, relevant to Ch06 (security and trust —
  supply-chain security for LLM infrastructure), secondarily Ch00 (principles)
  and Ch05 (release engineering). The intended value is the transferable
  credential-isolation and signing patterns, not Cilium-specific release detail.

## Extracted Claims

### Claim 1: Two separately scoped registry credential sets behind distinct protected GitHub environments limit blast radius — CI creds can push only to `quay.io/cilium/*-ci`, while production creds sit behind a `release` environment requiring explicit maintainer approval
- **Evidence**: The post names the two credential sets, the registry scopes, and
  the approval requirement for the production set.
- **Confidence**: settled (first-party description of the project's own config)
- **Quote**: "We keep two distinct sets of registry credentials behind separate GitHub protected environments:"
- **Quote**: "CI credentials can push to our development image registry (`quay.io/cilium/*-ci`) and are available to CI builds. Even if a CI workflow is compromised somehow, these credentials cannot push to production image tags."
- **Quote**: "Production credentials sit behind the `release` environment, which requires an explicit maintainer approval before a workflow run can touch them. No fork, no feature branch, and no CI build can reach those secrets. Only tag-triggered release builds that a maintainer has approved can."
- **Our assessment**: Buy it. This is the concrete positive form of the
  "isolated per-stage credentials" remedy the corpus currently carries only as a
  rule (from the LiteLLM incident). The key design move is environmental scoping:
  the production secret is not merely guarded by policy — it is scoped to a
  protected environment that a CI-initiated workflow cannot enter without a
  human approval. Directly transferable to LLM infra release pipelines.

### Claim 2: The stated worst case of a CI compromise is that the attacker can publish a malicious `-ci` image but cannot publish a production release — because "the credentials simply aren't on the runner"
- **Evidence**: Stated explicitly as the blast-radius argument, with both
  production registries named.
- **Confidence**: settled (first-party description of the intended property)
- **Quote**: "Worst-case, in a CI compromise, the attacker can publish a malicious -ci image. They cannot publish to `quay.io/cilium/cilium:v1.x.x` or `docker.io/cilium/cilium:v1.x.x`. The credentials simply aren’t on the runner."
- **Our assessment**: Buy it. "The credentials simply aren't on the runner" is
  the sharpest formulation of the principle in the corpus: make the secret
  *absent from the compromised host* rather than trying to guard its use. It
  matches the corpus's architecture-over-policy theme (cf. the NGINX network
  boundary note) and is the direct counter-pattern to the LiteLLM incident's
  shared-CircleCI-environment factor.

### Claim 3: `GITHUB_TOKEN` defaults to minimal read permissions on contents and packages, and workflows needing more must opt in explicitly
- **Evidence**: Stated as a deliberate default with the rationale.
- **Confidence**: settled
- **Quote**: "By default our `GITHUB_TOKENs` are scoped to minimal read permissions on contents and packages. Workflows that need anything more have to opt in explicitly, so a workflow that forgets to declare permissions doesn’t end up with broad org-wide write access."
- **Our assessment**: Buy it. Least-privilege-by-default (fail-closed on
  forgotten `permissions:` blocks) is a small, checkable, copyable control.
  It is the workflow-permission half of the credential-isolation story; the
  registry-credential environments are the other half.

### Claim 4: Every `actions/checkout` call sets `persist-credentials: false`, so the token never lands in the runner's git config where a later step could grab it
- **Evidence**: Stated as a project-wide convention.
- **Confidence**: settled
- **Quote**: "Every actions/checkout call also sets persist-credentials: false, so the `GITHUB_TOKEN` never ends up in the runner’s git config where a later step could grab it."
- **Our assessment**: Buy it. This is a concrete mitigation for the
  intra-job credential-persistence class of attack (the promptfoo note documents
  the analogous environment-state persistence via `$GITHUB_PATH`/`$GITHUB_ENV`/`$HOME`).
  `persist-credentials: false` removes one specific persistence channel (the git
  credential file) but not the environment-state channels promptfoo describes —
  the two controls are complementary, not substitutes.

### Claim 5: Every released container image is signed with Sigstore Cosign using keyless OIDC — there are no long-lived signing keys to steal
- **Evidence**: Names the released images and the signing mode.
- **Confidence**: settled
- **Quote**: "Every container image we release (cilium, operator-*, hubble-relay, clustermesh-apiserver) is signed with Sigstore Cosign using keyless OIDC. There are no long-lived signing keys for anyone to steal."
- **Our assessment**: Buy it. Keyless OIDC signing is the ephemeral-credential
  form for release integrity: the signing identity is derived from the workflow's
  short-lived OIDC token, so there is no static key an attacker can exfiltrate
  and reuse. This extends the corpus's Litellm Cosign material (which used a
  pinned-commit public key) with the keyless variant.

### Claim 6: A reusable composite action pins its dependencies by full SHA, generates an SPDX SBOM, then signs and attests the image
- **Evidence**: The post shows the composite action verbatim (see Concrete
  Artifacts); it pins `sigstore/cosign-installer` and `anchore/sbom-action` by
  commit SHA and runs `cosign sign -y` plus `cosign attest -y --type spdxjson`.
- **Confidence**: settled (config shown verbatim)
- **Quote**: "A reusable composite action handles the signing pipeline:"
- **Our assessment**: Buy it. Pinning the signing toolchain itself by SHA is the
  recursive application of the "pin everything" rule — the supply-chain
  hardening must cover the tools that implement supply-chain hardening. The
  SPDX-SBOM-then-attest sequence is the copyable release-signing workflow.

### Claim 7: Release builds run inside protected environments (`release`, `release-tool`, `release-helm`) and cannot be triggered from a fork or a feature branch
- **Evidence**: Stated with the environment names.
- **Confidence**: settled
- **Quote**: "Release builds also run inside protected environments (`release, release-tool, release-helm`) so production registry credentials are gated behind environment protection rules. You can’t trigger a release build from a fork or a feature branch."
- **Our assessment**: Buy it. This is the enforcement half of Claim 1: the
  environment protection rules are what make the two-credential-set design hold.
  It also matches the corpus's fork-PR default-deny pattern (promptfoo note),
  applied to releases rather than scans.

### Claim 8: Audited gap — no SLSA provenance: every `docker/build-push-action` sets `provenance: false`, so consumers can verify *who* signed an image but not *how* it was built
- **Evidence**: Stated as the first, largest admitted gap in their own audit
  against OpenSSF Scorecard / SLSA / StepSecurity.
- **Confidence**: settled (first-party admission of a concrete config value)
- **Quote**: "Every `docker/build-push-action` call sets `provenance: false`. We sign images with Cosign, but we don’t generate SLSA build provenance attestations. Consumers can verify *who* signed an image, but not *how* it was built."
- **Our assessment**: Buy it, and this is the highest-value nugget in the post.
  It sharpens the corpus's existing "a SHA pin says what you have; an attestation
  says who built it" rule with two new facts: (1) signing is not provenance —
  Cosign signing and SLSA build provenance answer different questions; and (2)
  `provenance: false` is the *default* of the most common build action, so the
  gap is silent unless explicitly looked for. A first-party example of a mature
  pipeline that signs but does not attest.

### Claim 9: Audited gap — no dependency review at PR time; they rely on Renovate's `vulnerabilityAlerts`, which is reactive
- **Evidence**: Stated as a gap with the proposed fix.
- **Confidence**: settled
- **Quote**: "We rely on Renovate’s `vulnerabilityAlerts` to flag known-vulnerable dependencies, but that’s reactive."
- **Our assessment**: Buy it. Reactive vulnerability alerting only fires after an
  advisory exists; PR-time dependency review catches malicious or vulnerable
  *new* dependencies before they merge. The distinction (pre-merge gate vs
  post-advisory alert) is a useful addition to the corpus's dependency-hygiene
  material.

### Claim 10: Audited gap — 68 internal `@main` references to a mutable branch ref in composite actions, inconsistent with the project's own SHA-pinning policy
- **Evidence**: Concrete count plus the specific action path.
- **Confidence**: settled
- **Quote**: "68 internal @main references. A bunch of conformance and scale-test workflows reference `cilium/cilium/.github/actions/set-commit-status@main`, which is a mutable branch ref. It’s lower risk than a third-party tag, but inconsistent with our SHA-pinning policy."
- **Our assessment**: Buy it. The transferable lesson is that a pinning policy
  has an internal-consistency failure mode: first-party refs feel safer than
  third-party tags, so they escape the policy and accumulate. 68 is the only
  quantitative figure in the source, and it makes the point crisply.

### Claim 11: Audited gap — no `govulncheck` in CI (vulnerable-package presence is not vulnerable-function reachability), no OpenSSF Scorecard workflow, an expired `SECURITY-INSIGHTS.yml` (January 2025), and no `go mod verify`
- **Evidence**: Stated as smaller items in the same audit.
- **Confidence**: settled
- **Quote**: "No `govulncheck` in CI. We fuzz and we lint, but we don’t yet run Go’s official vulnerability scanner, which checks whether our code actually calls vulnerable functions rather than just whether a vulnerable package shows up in go.sum."
- **Quote**: "Our `SECURITY-INSIGHTS.yml` expired in January 2025 and hasn’t been updated. (We actually noticed this while writing this post.)"
- **Our assessment**: Buy it. The `govulncheck` distinction is the analytically
  interesting one: dependency scanning answers "is a vulnerable package
  present?", reachability analysis answers "does our code call the vulnerable
  function?" — presence is the conservative over-approximation. The expired
  `SECURITY-INSIGHTS.yml` is a reminder that security metadata is itself a
  maintenance artifact that silently goes stale.

### Claim 12: Additional release-integrity layers — tag immutability, DCO sign-off enforcement, and third-party audits plus a published threat model
- **Evidence**: Stated as supporting controls.
- **Confidence**: settled
- **Quote**: "Tag immutability. Once a GitHub release is published, the tags and assets attached to it can’t be modified. The setting lives in the repository’s *Settings → Releases* page."
- **Our assessment**: Buy it. Tag immutability is a one-setting control that
  removes a whole class of "the artifact changed after review" attacks, and it
  is the precondition that makes tag-based verification trustworthy at all.
  Included here as a concrete, low-cost control rather than for Cilium-specific
  process detail.

### Claim 13: Within a single environment, secrets are still scoped broadly — any workflow running in that environment can access them — so a new workflow added to the environment inherits the credentials
- **Evidence**: Stated as the residual gap the GitHub scoped-secrets roadmap
  item would close.
- **Confidence**: settled
- **Quote**: "CI vs. production credential isolation is one of our strongest controls, but within a given environment, secrets are still scoped pretty broadly: any workflow running in that environment can access them."
- **Quote**: "A release credential could be restricted not just to the `release` environment but to the specific `release.yaml` workflow file, so a new workflow added to that environment (by accident or by an attacker) wouldn’t inherit the credentials."
- **Our assessment**: Buy it. The honest framing that environment isolation is
  not the same as workflow isolation is important — the credential boundary is
  only as tight as the environment's membership, and membership can grow by
  accident or attack. Scoped secrets (bind credential to workflow path/branch)
  is the proposed tightening.

### Claim 14: GitHub's 2026 Actions security roadmap would add workflow-level dependency locking (direct and transitive, hash-verified before execution), org-level rulesets banning `pull_request_target`, scoped secrets, and a native L7 egress firewall outside the runner VM
- **Evidence**: Stated as an explicit mapping of the roadmap to their controls.
- **Confidence**: emerging (forward-looking platform roadmap, public preview
  estimates only)
- **Quote**: "GitHub’s planned dependencies: section in workflow YAML would lock all direct *and transitive* `dependencies` by commit SHA, with hash verification before execution starts. That closes the gap."
- **Quote**: "It runs outside the runner VM at L7, so it’s immutable even if an attacker gets root inside the runner."
- **Our assessment**: Buy the direction. The egress-firewall detail is the same
  architecture-not-policy principle: enforcement outside the thing being
  defended (outside the runner VM) cannot be disabled by compromising the
  runner. Timeline is soft ("Public preview is expected in 6 to 9 months"), so
  this is `emerging` and should not be cited as available capability.

### Claim 15: The closing thesis — supply-chain security is the practice of repeatedly asking "what if this thing I trust gets compromised?" and adding a layer that limits the blast radius
- **Evidence**: Stated as the framing for the whole series.
- **Confidence**: settled (a position statement, not an empirical claim)
- **Quote**: "Supply chain security is mostly the practice of repeatedly asking “what if this thing I trust gets compromised?” and adding a layer that limits the blast radius when it does."
- **Quote**: "We’ve tried to build defense in depth: access controls so only trusted people can trigger builds, pinned digests so a compromised tag can’t reach us, least-privilege permissions so a rogue action can’t exfiltrate secrets, credential isolation so CI can never touch production, and signatures so users can verify what they’re running."
- **Our assessment**: Buy it as a concise framing for Ch06. The enumeration in
  the second quote is effectively a checklist of release-pipeline defense
  layers, each of which maps to a concrete claim in this note.

## Concrete Artifacts

All artifacts verbatim from
https://www.cncf.io/blog/2026/06/26/securing-ci-cd-for-an-open-source-project-part-3-credentials-verification-and-whats-next.

### Cosign signing composite action (verbatim)

```
.github/actions/cosign/action.yaml
```

```
- name: Install Cosign
  uses: sigstore/cosign-installer@cad07c2e89fa2edd6e2d7bab4c1aa38e53f76003 # v4.1.1

- name: Generate SBOM
  uses: anchore/sbom-action@e22c389904149dbc22b58101806040fa8d37a610 # v0.24.0
  with:
    artifact-name: sbom_${{ inputs.sbom_name }}.spdx.json
    output-file: ./sbom_${{ inputs.sbom_name }}.spdx.json
    image: ${{ inputs.image_tag }}

- name: Sign Container Image
  shell: bash
  run: cosign sign -y "${{ inputs.image }}"

- name: Attach SBOM Attestation
  shell: bash
  run: |
    cosign attest -y \
      --predicate "./sbom_${{ inputs.sbom_name }}.spdx.json" \
      --type spdxjson \
      "${{ inputs.image }}"
```

### Registry credential scoping (verbatim, condensed from the "Protecting credentials" section)

```
- CI credentials can push to our development image registry (quay.io/cilium/*-ci)
  and are available to CI builds.
- Production credentials sit behind the release environment, which requires an
  explicit maintainer approval before a workflow run can touch them.
Worst-case, in a CI compromise, the attacker can publish a malicious -ci image.
They cannot publish to quay.io/cilium/cilium:v1.x.x or docker.io/cilium/cilium:v1.x.x.
The credentials simply aren't on the runner.
```

### Audited gap list (verbatim, condensed from "What we're still working on")

```
- No SLSA provenance. Every docker/build-push-action call sets provenance: false.
- No dependency review at PR time. We rely on Renovate's vulnerabilityAlerts ...
  but that's reactive.
- No govulncheck in CI. ... checks whether our code actually calls vulnerable
  functions rather than just whether a vulnerable package shows up in go.sum.
- 68 internal @main references.
- No OpenSSF Scorecard workflow for continuous supply chain health monitoring.
- Our SECURITY-INSIGHTS.yml expired in January 2025 and hasn't been updated.
- No go mod verify step to validate vendor directory integrity against go.sum
  checksums.
```

## Cross-References

- **Corroborates**:
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 4** (shared
    CI/CD environment across stages increased blast radius) — Cilium's two
    separately scoped credential sets behind distinct protected environments
    (this note's Claim 1) are the positive-side implementation of the isolation
    remedy that LiteLLM adopted after the incident. Same principle, one party
    proactive and one reactive.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 5** (static
    long-lived release credentials in env vars let a compromised step reach them
    directly) — Cilium's environment-gated production credentials plus
    keyless-OIDC signing (this note's Claims 1, 5) remove the static,
    always-present credential that was LiteLLM's second contributing factor.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 11** (isolated
    per-stage CI/CD environments: unit / integration / security-scan / release)
    — Cilium's CI-vs-production credential split is the same stage-isolation
    idea realized through GitHub protected environments rather than separate
    runners.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 12**
    (ephemeral credentials: PyPI Trusted Publisher, GHCR token auth) — keyless
    OIDC (this note's Claim 5) is the same ephemeral-credential class applied to
    signing identity.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 13** (Cosign
    signing shipped, verified against a pinned-commit public key) — this note
    documents the keyless-OIDC variant and the SBOM-attestation step; both are
    release-tampering countermeasures. The two together give the corpus both
    Cosign verification modes (pinned key and keyless OIDC).
  - `docs-promptfoo-code-scan-github-action.md` **Claim 2** (a signed
    build-provenance attestation binds exact bytes to the release workflow,
    strictly stronger than SHA pinning alone — "a SHA pin tells you what you
    have; the attestation tells you who built it and how") — this note's
    Claim 8 is the first-party confirmation that **signing is not provenance**:
    Cilium signs every image yet sets `provenance: false`, so its consumers can
    verify *who* signed but not *how* it was built. The promptfoo note supplies
    the positive control (`gh attestation verify`); this note supplies the
    concrete gap that makes the distinction operationally important.
  - `docs-promptfoo-code-scan-github-action.md` **Claim 8** (pin third-party
    actions to full commit SHAs; a tag is mutable) — Cilium's composite action
    pins `sigstore/cosign-installer` and `anchore/sbom-action` by SHA (Claim 6)
    but admits 68 internal `@main` refs (Claim 10); the pair shows both the
    convention and its internal-consistency failure mode.
- **Contradicts**: None. No existing source note claims that shared CI
  environments, static release credentials, or mutable refs are safe, and none
  opposes credential isolation or artifact signing. This source is confirming
  sibling evidence for Ch06, not a disagreement. No contradiction issue filed.
- **Extends**:
  - `blog-cncf-network-boundary-ai-agents-nginx-otel.md` **Claim 1** (the
    boundary must be a property of the architecture enforced regardless of
    application policy — "there is no second path") — same architecture-over-policy
    thesis in a different domain. That note enforces agent egress at the network
    layer; this note enforces credential absence at the runner/environment layer
    ("the credentials simply aren't on the runner"). Worth cross-linking as two
    applications of one design principle.
  - `failure-litellm-supply-chain-compromise-march-2026.md` **Lesson 4**
    (impact scoping by deployment path; pinned/source installs safe, unpinned
    pip exposed) and **Lesson 1** (release integrity is distinct from repo
    integrity) — this note extends the release-integrity half with the
    *positive* mechanism: separate protected environments and keyless signing,
    rather than the incident's post-hoc rotation and safe-version audit.
  - `failure-litellm-security-hardening-april-2026.md` — named in the Prospector
    triage as the CI/CD v2 follow-through for the same supply-chain wave. This
    note adds an independent, proactive project's implementation of the same
    control classes. (That note is a failure-report structured by
    "Vulnerability" sections, not numbered Claims, so it is cited by section /
    note name rather than a claim number.)
  - `docs-google-sre-canarying-releases.md` — adjacent release-pipeline safety
    material named in the triage; different mechanism (staged rollout and
    error-budget evaluation, not supply-chain integrity). Complementary, not
    overlapping: canarying limits the impact of a *bad change*, credential
    isolation limits the impact of a *compromised build*. Cited as adjacent
    only.
- **Novel**: First source note in the corpus covering:
  1. The **positive, first-party implementation** of release-pipeline credential
     isolation (two scoped credential sets behind distinct protected GitHub
     environments with maintainer approval), as opposed to an incident-driven
     remediation.
  2. **`persist-credentials: false`** as a concrete, project-wide control against
     credential persistence in git config.
  3. **Keyless-OIDC Cosign signing with SPDX SBOM attestation** via a pinned
     composite action — the keyless variant of the corpus's existing
     pinned-key Cosign material.
  4. The explicit **signing-vs-provenance distinction** and the `provenance:
     false` **default trap** on `docker/build-push-action`.
  5. A first-party **audited gap list** as a planning artifact (SLSA provenance,
     PR-time dependency review, `govulncheck`, 68 internal `@main` refs, expired
     `SECURITY-INSIGHTS.yml`, no `go mod verify`).
  6. A **mapping of GitHub's 2026 Actions security roadmap** (workflow-level
     dependency locking, org-level rulesets, scoped secrets, native L7 egress
     firewall, Actions Data Stream) onto current controls.

## Guide Impact

- **Chapter 06 (Security and Trust)**, "Three CI/CD anti-patterns" /
  "Pin everything; verify releases" sections: Add the positive
  credential-isolation pattern as the concrete remedy for the existing
  anti-pattern list. Specific additions:
  1. Two credential sets behind distinct protected environments; the production
     set gated by an explicit maintainer approval; the worst case is a
     non-production image, because "the credentials simply aren't on the
     runner" (cite Claim 1, Claim 2).
  2. `persist-credentials: false` on every checkout and minimal-default
     `GITHUB_TOKEN` permissions (cite Claim 3, Claim 4) as checkable, low-cost
     controls.
  3. Keyless-OIDC Cosign signing with SBOM attestation as the ephemeral-credential
     form of release signing (cite Claim 5, Claim 6).
- **Chapter 06**, "A SHA pin says what you have; an attestation says who built
  it": Add the sharpening from this source — **signing is not provenance**, and
  `provenance: false` is the default of the most common build action, so a
  mature, Cosign-signing pipeline can still leave consumers unable to verify
  *how* an image was built (cite Claim 8). Recommend the guide state the
  Cosign-signature vs SLSA-provenance distinction explicitly and warn that the
  gap is silent by default.
- **Chapter 06**, supply-chain metadata hygiene: Add the `govulncheck`
  presence-vs-reachability distinction and the stale-`SECURITY-INSIGHTS.yml`
  example as reasons to treat security metadata as a maintained artifact
  (cite Claim 11).
- **Chapter 05 (LLM Ops Reliability)**, "CI/CD supply-chain isolation" section
  (`guide/05-llm-ops-reliability.md:1359`): The section currently cites only
  LiteLLM's CI/CD v2 goals. Add this source as the concrete, positive
  implementation of "isolate CI/CD stages by blast radius": environment-scoped
  credentials, release-environment approval, and keyless signing (cite
  Claim 1, Claim 5, Claim 7).
- **Chapter 00 (Principles)**: The closing thesis and the "the credentials
  simply aren't on the runner" formulation are a clean statement of
  blast-radius reduction / defense in depth; usable as a Ch00 principle example
  (cite Claim 2, Claim 15).

## Extraction Notes

- Source read in full: the CNCF Member Post page (published 2026-06-26,
  ~14 KB of extractable body text). No sub-pages were followed beyond what was
  needed for attribution: Part 1 and Part 2 of the series are linked but were
  not fetched (the triage scoped this to part 3's credential/signing material),
  and the linked GitHub docs/roadmap pages are referenced by the source but not
  extracted. All quoted passages were copied character-for-character from the
  fetched page text.
- `date_published` set to 2026-06-26 (page dateline). `date_extracted` and
  `last_checked` set to 2026-10-11 UTC.
- `confidence_overall` set to `emerging`: the post is a first-party self-report
  of the project's own configuration. Many specific claims are concrete and
  checkable (config shown verbatim, named environments and actions), but they
  are not independently verified, and the roadmap half (Claim 14) is explicitly
  forward-looking with only a "6 to 9 months" public-preview estimate. The
  overall posture is therefore emerging rather than settled.
- The `miner-related-notes.md` candidates list was read per MINER.md §4. All 10
  listed candidates were evaluated and each is explicitly dismissed as
  non-overlapping:
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SRE SLOs;
    unrelated to CI/CD credential isolation. Dismissed.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative vs
    declarative change workflows; no supply-chain or credential content.
    Dismissed.
  - `docs-google-sre-on-call.md` — on-call pager load; unrelated. Dismissed.
  - `docs-google-sre-slo-engineering-case-studies.md` — SLO case studies;
    unrelated. Dismissed.
  - `docs-google-sre-eliminating-toil.md` — toil taxonomy; unrelated. Dismissed.
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` — batch-job
    reliability; unrelated. Dismissed.
  - `docs-google-sre-team-lifecycles.md` — SRE team adoption; unrelated.
    Dismissed.
  - `docs-litellm-anthropic-advisor-tool.md` — a model-composition feature;
    unrelated. Dismissed.
  - `docs-litellm-completion-function-call.md` — function-calling capability
    predicates; unrelated. Dismissed.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO framework; unrelated.
    Dismissed.
  The useful cross-references (the LiteLLM supply-chain notes, the promptfoo
  code-scan note, the CNCF network-boundary note, the security-hardening note)
  were discovered by searching `source-notes/` per the Prospector's triage
  guidance; each cited claim was re-read and verified per §4b before citation.
- The Prospector's caveat was followed: this is a general CI/CD supply-chain
  post for a Go CNCF project with no AI/LLM angle. Cilium-specific release
  process detail (Helm chart OCI artifacts, DCO bot internals, ADA Logics audit
  findings) was not extracted as LLM-ops guidance; only the transferable
  credential-isolation and signing patterns are carried.
- No contradiction issue filed: verified against the overlapping notes and
  `CONTRADICTIONS.md`. All overlapping sources agree with this one (they are
  either the incident this post is the positive counterpart to, or
  complementary controls); none opposes credential isolation or artifact
  signing.
