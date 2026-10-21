---
source_url: https://www.cncf.io/blog/2026/06/04/securing-ci-cd-for-an-open-source-project-controlling-who-runs-what
source_type: blog-post
title: "Securing CI/CD for an open source project: Controlling who runs what"
author: "André Martins (Cilium maintainer and Software Engineer, Isovalent at Cisco) and Feroz Salam (Cilium Security Team and Security Engineer, Isovalent at Cisco)"
date_published: 2026-06-04
date_extracted: 2026-10-21
last_checked: 2026-10-21
status: current
confidence_overall: emerging
issue: "#1821"
---

# Securing CI/CD for an open source project: Controlling who runs what

> Part 1 of Cilium's three-part CI/CD hardening series, covering the layer the
> other two parts do not: **access control** — who may trigger a build and
> what code that build is allowed to execute. It contributes three controls the
> corpus does not otherwise carry: a bot-mediated **trigger allow-list** bound
> to an enumerated team (untrusted commenters cannot spend CI minutes or fire
> cloud conformance suites), the **two-phase checkout** that separates trusted
> from untrusted code in a `pull_request_target` job with five explicitly
> stated preconditions, and **CODEOWNERS as the CI review gate**. Its most
> transferable artifact is the negative space: a *documented* set of conditions
> under which a pattern that security scanners flag as a vulnerability is
> actually safe — a false positive with a receipt.

## Source Context

- **Type**: blog-post (CNCF Member Post — the **first** of a three-part series
  on how the Cilium project hardens its own CI/CD pipeline. Parts 2
  (dependency hardening) and 3 (credentials, signing, gaps) are already in the
  corpus as separate notes).
- **Author credibility**: High for a first-party engineering account. Authors
  are André Martins (Cilium maintainer, Software Engineer at Isovalent/Cisco)
  and Feroz Salam (Cilium Security Team, Security Engineer at Isovalent/Cisco)
  — the same authors as the two sibling notes already in the corpus. The post
  names the project's actual configuration files and links to Cilium's public
  repository, but the claim set is a self-report and is not independently
  verified. The authors also volunteer that the pattern they describe draws
  recurring security reports, which is a signal of candor rather than of
  marketing.
- **Scope**: Covers the access-control layer only: (1) trigger control via the
  in-house Ariane bot, including the hand-maintained workflow allow-list;
  (2) separating trusted from untrusted code in `pull_request_target` jobs via
  a two-phase checkout, with the enumerated preconditions and the bounded
  blast radius; (3) CODEOWNERS as the review gate for the pipeline itself.
  It also carries the series framing, a threat-context opening, and a one-row
  summary of the residual gaps (detailed in the part 3 note). Does **not**
  cover dependency pinning, Renovate, Go module vendoring, static analysis of
  workflows, credential isolation, signing, or release verification — those
  are parts 2 and 3, already mined — and contains no AI/LLM content, no
  reliability metrics, and no incident data. This is a general CI/CD
  supply-chain post for a Go CNCF project.
- **Prospector framing**: Triage (three concurrent runs) routed this as
  `triaged:text`, novelty medium–high, `priority:high`, relevant to Ch06
  (Security and Trust) and secondarily Ch03 (CI-gated agent-triggered
  workflows) and Ch05 (release engineering). The triage flagged the content
  as "general CI/CD supply-chain hardening, not LLM-ops specific" and asked
  for the **transferable control**, not Cilium release detail.

## Extracted Claims

### Claim 1: The access-control layer is the *first* question in any CI supply-chain story — who can trigger a build, and what code does that build execute — because many CI compromises begin by tricking the system into running attacker-controlled code with elevated privileges
- **Evidence**: Explicit framing sentence opening the "Controlling who runs
  what" section; the whole post is organized as the answer to that question.
- **Confidence**: settled (a position statement, but one the corpus's own
  incident evidence directly supports)
- **Quote**: "The first question in any CI supply chain story is: who can
  trigger a build, and what code does it execute? Plenty of CI
  compromises start right here, by tricking the system into running
  attacker-controlled code with elevated privileges."
- **Our assessment**: Buy it. The corpus's LiteLLM incident note starts at the
  *dependency* layer (an unpinned scanner dependency was compromised) and the
  part 3 note starts at the *credential* layer. Neither asks the upstream
  question — whether the trigger was ever legitimate. This sentence is the
  framing that places trigger control upstream of both, and it is the missing
  first line of the guide's supply-chain section, which currently opens with
  pinning (Ch06, "Pin everything; verify releases",
  `guide/06-security-and-trust.md:636`) and only later reaches
  untrusted-code execution.

### Claim 2: Trigger control is a separate trust boundary from dependency pinning — Cilium's in-house Ariane bot dispatches CI workflows from PR comments, gated on the commenter being in the `organization-members` team, resolving inter-workflow dependencies and dispatching via `workflow_dispatch`
- **Evidence**: The bot's mechanism is described in prose and corroborated by
  the linked `cilium/ariane` repository README (see Concrete Artifacts): a
  GitHub App that watches PR comments for trigger phrases and runs workflows
  via `workflow_dispatch`.
- **Confidence**: settled (first-party description of the project's own
  tooling; the linked repository confirms the mechanism)
- **Quote**: "Ariane is a GitHub bot we wrote in-house to dispatch CI workflows
  from PR comments. When a maintainer types /test or /ci-eks on a
  pull request, Ariane checks that the commenter belongs to the
  organization-members team, figures out which workflows to fire
  (including dependencies, like tests that need a fresh image build
  first), and dispatches them via workflow_dispatch."
- **Quote** (from the linked `cilium/ariane` README, not the blog post):
  "A GitHub App watches comments on pull requests for specific trigger phrases,
  and manually runs workflows using `workflow_dispatch` events. If configured
  only allowed team members can trigger the tests."
- **Our assessment**: Buy it, and this is the corpus's first concrete
  implementation of trigger control as a distinct trust boundary. The key
  design move is that the *trigger phrase* is not a capability — it is a
  **request** that a policy-checking intermediary decides whether to honor.
  GitHub's own `workflow_dispatch` has no notion of *who asked*; Ariane adds
  one. The dependency-resolution detail (a test that needs a fresh image build
  triggers the build first) is what makes the pattern usable in practice
  rather than theoretical. Note the mechanism requires the GitHub App to hold
  `Actions: Read and write` plus organization `Members: Read-only` — the
  permission to *read membership* is the entire basis of the gate, so a
  project adopting this pattern must grant its bot org-membership read
  access, which is itself a small but real privilege to hand to a bot.

### Claim 3: The set of triggerable workflows is enumerated **by hand** in `.github/ariane-config.yaml` — an explicit allow-list, not a wildcard — with per-trigger workflow lists and a `depends-on` graph
- **Evidence**: The config file is quoted verbatim in the post (see Concrete
  Artifacts); the linked repository's `example/ariane-config.yaml` confirms
  the schema.
- **Confidence**: settled (config shown verbatim; checkable in the public
  repository)
- **Quote**: "The interesting bit is the allow-list. Only verified org members
  can trigger workflows, and the set of workflows that can be
  triggered is enumerated by hand in the config:"
- **Quote** (from the post's TL;DR table):
  "Only verified org members can fire CI workflows from PR comments, against an
  explicit allow-list of workflows."
- **Our assessment**: Buy it. Two properties matter and neither is automatic:
  (a) the *team* gate (who may ask) and (b) the *workflow* allow-list (what
  may be asked for). A bot that lets any org member trigger *any* workflow is
  still a wide door — the allow-list is what makes the gate a *scope*
  statement rather than an identity statement. *Enumerated by hand* also means
  the allow-list is a reviewable artifact: adding a workflow to it is a visible
  diff in a config file, not a silent behavior change in code.

### Claim 4: An unauthorized trigger from a random external commenter is ignored — the gate bounds both CI spend and the attacker's ability to fire expensive cloud-provider conformance suites
- **Evidence**: Stated directly, with the two concrete harms named.
- **Confidence**: settled
- **Quote**: "A random external commenter typing /test in a PR is ignored. They
  can’t kick off our expensive cloud-provider conformance suites or
  burn through our CI minutes."
- **Our assessment**: Buy it. This is the corpus's first statement of the
  *cost* side of trigger control, and it is the half that generalizes least
  obviously to LLM-ops: a self-hosted LLM pipeline whose CI dispatches
  GPU-backed eval jobs on comment text has the same exposure, and the
  expensive-suite analogy ("conformance suites") maps directly onto
  *GPU hours*. It also reframes who the adversary is: not a supply-chain
  attacker who has already compromised a dependency, but an ordinary
  *commenter* — a much lower bar than a supply-chain compromise, and therefore
  a control worth more per unit of effort.

### Claim 5: The two-phase checkout separates trusted from untrusted code *inside one privileged job* — the base branch is checked out first so composite actions, scripts and signing logic come from reviewed code, and only then is the PR head checked out, used purely as Docker build context and never executed as a script
- **Evidence**: The workflow YAML is quoted verbatim in the post (see Concrete
  Artifacts); the prose states the ordering and the purpose of each checkout.
- **Confidence**: settled (config shown verbatim)
- **Quote**: "The first checkout grabs the base branch (code that’s already
  been reviewed and merged) so we can load our composite actions,
  scripts, and the Cosign signing logic from a known-good source.
  Only after that does the workflow check out the PR head, and that
  checkout is used purely as build context for docker build.
  Nothing from the PR branch is ever executed as a script."
- **Quote** (from the post's TL;DR table):
  "Trusted code (composite actions, scripts, signing logic) is loaded from the
  base branch; the PR head is only used as Docker build context, never
  executed as a script."
- **Our assessment**: Buy it. The elegant move is that the *trusted* tree is
  what the job executes and the *untrusted* tree is what the job consumes as
  inert data. The PR branch is present on disk (it has to be — it is the
  build input) but is never a source of executable code. This is a materially
  different design from the corpus's current guidance, which says to put
  untrusted code in a *different job*; see the near-miss analysis under
  Cross-References → Contradicts for why these are complementary rather than
  conflicting. The `ref: ${{ steps.tag.outputs.sha }}` detail (the second
  checkout pins an explicitly computed SHA rather than a branch name) also
  matters: the untrusted checkout is not *whatever the PR head is right now*.

### Claim 6: The safety of this usually-unsafe pattern rests on **five explicitly enumerated preconditions**, and the post states them as a list rather than implying them
- **Evidence**: The five-bullet list in the "Separating trusted and untrusted
  code in CI" section, quoted verbatim in Concrete Artifacts.
- **Confidence**: settled (the preconditions are stated as design invariants;
  whether each actually holds is a self-report)
- **Quote**: "We get security reports about this pattern fairly regularly.
  Automated scanners and well-meaning researchers see
  “pull_request_target plus a second checkout” and flag it as a
  vulnerability. In the general case they’re right too. In ours,
  the workflow is intentionally designed so the pattern is safe:"
- **Our assessment**: Buy it — this is the highest-value artifact in the post.
  The value is not the pattern; it is the **enumeration**. A security pattern
  that is safe only under stated invariants is only reviewable if the
  invariants are written down, and writing them down turns a scanner
  finding into a checklist a reviewer can run. This is the same
  architecture-over-policy theme the corpus already carries (the network
  boundary note's "a property of the architecture, not a policy we hope the
  application respects"), applied to CI job structure. The two halves of the
  framing also matter: the authors concede the scanners' general case is
  right, which is what makes their specific carve-out credible rather than
  defensive.

### Claim 7: Precondition 1 — no `run:` step executes anything from the untrusted checkout; every shell block after the second checkout is written inline in the workflow YAML
- **Evidence**: First bullet of the enumerated list.
- **Confidence**: settled (stated invariant; the inline-shell-block detail is
  the mechanism that makes it checkable)
- **Quote**: "No run: steps execute scripts from the untrusted checkout. Every
  shell block after the second checkout is written inline in the
  workflow YAML (disk usage checks, file copies, digest output).
  Nothing is sourced from the PR branch."
- **Our assessment**: Buy it. The inline-shell-block detail is the part that
  makes the invariant *auditable*: if a step's body is inline in the workflow
  file, then it came from the trusted base-branch checkout of the workflow
  file itself, not from the PR tree — a reviewer can see the whole body at
  review time without tracing file loads. This is a checkable property of the
  YAML, not a promise in prose.

### Claim 8: Precondition 2 — no composite actions are loaded from the untrusted checkout; every composite action comes from the trusted base-branch checkout or the saved `../cilium-base-branch/` directory
- **Evidence**: Second bullet of the enumerated list; the post also names the
  three composite actions in scope (`set-runtime-image`, `cosign`,
  `set-env-variables`) and states the in-flight plan to move them to a
  dedicated repository.
- **Confidence**: settled
- **Quote**: "No composite actions are loaded from the untrusted checkout
  either. All composite actions (set-runtime-image, cosign,
  set-env-variables) come from the trusted base-branch checkout or
  from the saved ../cilium-base-branch/ directory. We’re also
  working on moving these composite actions into a dedicated
  repository so we don’t have to check out source to run them at
  all."
- **Our assessment**: Buy it. Composite actions are the step most often
  forgotten in a `pull_request_target` threat model, because the reviewer
  reads `uses:` lines and assumes they resolve to trusted upstream code — but
  a *local* composite action (`uses: ./.github/actions/foo`) resolves against
  the checked-out tree, so the second checkout silently changes what
  `uses: ./...` means. The `../cilium-base-branch/` detail is the concrete
  workaround: the trusted tree is preserved at a separate path so local
  composite actions keep resolving to trusted code. The stated next step
  (a dedicated composite-actions repo) removes the need for a source checkout
  to run them at all, which is the same *don't check out code to get a tool*
  move the part 2 note describes for pinning.

### Claim 9: Precondition 3 — Docker BuildKit *does* execute the untrusted Dockerfile, and that is accepted because BuildKit runs isolated from the job: no Actions environment variables, no repo secrets, no access to the runner's Docker credential store, and no secrets in the build args
- **Evidence**: Third bullet of the enumerated list; the post states the
  residual risk explicitly rather than denying that untrusted code runs.
- **Confidence**: settled (a stated boundary of the builder's isolation; the
  isolation claim itself is a first-party assertion about BuildKit)
- **Quote**: "Docker BuildKit does execute the untrusted Dockerfile, and that’s
  the whole point of building a CI image from a PR. BuildKit runs
  in isolation: no GitHub Actions environment variables, no repo
  secrets, no access to the runner’s Docker credential store. The
  build args we pass contain no secrets, just the runtime image
  reference and the operator variant name."
- **Our assessment**: Buy it, with the caveat that "BuildKit runs in isolation"
  is the load-bearing assertion and is not demonstrated here — it is a
  property of the builder's sandbox, not a property of the workflow. The
  honest form of the claim is therefore *narrower* than *untrusted code never
  runs*: untrusted code runs in a context that has been deliberately emptied
  of everything worth stealing. The clause that the build args contain no
  secrets matters because build args are a classic leak channel — they are
  visible in the image's history — and the authors are explicit that the only
  two are the runtime image reference and the operator variant name.

### Claim 10: Precondition 4 — untrusted data flows into **exactly one** trusted action, `set-runtime-image`, which enforces the `quay.io/cilium/` prefix and strips newlines to block a `GITHUB_ENV` injection
- **Evidence**: Fourth bullet of the enumerated list; the mechanism is named
  with its two validation behaviors and its security purpose.
- **Confidence**: settled (named mechanism with named defenses)
- **Quote**: "Untrusted data flows into exactly one trusted action. The
  runtime-image*.txt file from the PR is fed into the trusted
  set-runtime-image action, which checks the image reference starts
  with quay.io/cilium/ and strips newlines so an attacker can’t
  smuggle in a GITHUB_ENV injection. There’s no way to repoint the
  build to anything outside the Cilium namespace."
- **Our assessment**: Buy it — this is the sharpest single-sentence control in
  the post. Two independent defenses on one value: an **allow-list prefix**
  (the build cannot be repointed to another namespace, so a compromised PR
  cannot substitute someone else's base image) and a **newline strip** (which
  is what actually stops `GITHUB_ENV` injection — the value reaches the
  environment file, and a newline terminates the assignment and starts a new
  one). The corpus already carries the `GITHUB_ENV` injection channel from a
  different angle — the part 2 note documents expression injection into
  `run:` blocks, and the part 3 note notes `persist-credentials: false` as
  removing one credential-persistence channel — but this is the first corpus
  claim that treats *newline stripping at a validation choke point* as a
  named control. The "exactly one" phrasing is the real lesson: the number
  of places untrusted data can enter the trusted path is the quantity to
  minimize, and one is a reviewable number.

### Claim 11: Precondition 5 — only CI credentials are in scope: the Docker login uses `QUAY_USERNAME_CI` / `QUAY_PASSWORD_CI`, which can push only to the `-ci` development registry, and production credentials are not on the runner at all
- **Evidence**: Fifth bullet of the enumerated list.
- **Confidence**: settled
- **Quote**: "Only CI credentials are in scope. The Docker login uses
  QUAY_USERNAME_CI / QUAY_PASSWORD_CI, which can only push to the
  -ci development registry. Production credentials aren’t on the
  runner at all."
- **Our assessment**: Buy it, and note that this is the one precondition that
  is **not** established by this post but imported from part 3 — the
  credential scoping is part 3's material (see Cross-References → Extends).
  Worth flagging because a reader copying the two-phase pattern in isolation
  would get preconditions 1–4 without 5, and precondition 5 is what bounds
  the blast radius. The five conditions are not independent; they compose.

### Claim 12: The blast radius of the whole pattern is bounded to the development registry — the stated worst case of a compromised PR build is a malicious CI image, and the pattern is described as intentional rather than as an oversight
- **Evidence**: Stated as the closing argument of the section, with the
  report-handling stance included.
- **Confidence**: settled (first-party statement of the intended property)
- **Quote**: "The worst-case outcome of a compromised PR build is a malicious
  CI image landing in the development registry, which is the same
  blast radius any CI system that builds contributor code carries.
  We do appreciate every report and read each one carefully, but
  this pattern is intentional."
- **Our assessment**: Buy it. Two things are worth carrying. First, the
  bounding claim itself: the worst case is a *bad artifact in a non-production
  namespace*, which is the same shape as the part 3 note's "the credentials
  simply aren't on the runner" — the secret is absent, so there is nothing to
  steal. Second, the "this pattern is intentional" framing is a genuinely
  useful piece of operational craft for
  the guide: a documented, preconditioned exception that still expects
  incoming findings and answers them, rather than either silently ignoring
  them or removing the control.

### Claim 13: CODEOWNERS is used as the review gate for the pipeline itself — everything under `.github/` is owned by a security-focused CI team plus a CI-structure team, and the `auto-approve.yaml` workflow is owned by maintainers
- **Evidence**: The CODEOWNERS excerpt is quoted verbatim in the post (see
  Concrete Artifacts), with the two owning teams named and annotated.
- **Confidence**: settled (config shown verbatim)
- **Quote**: "For CI configuration that means anything under .github/ is owned
  by @cilium/github-sec (our security-focused CI team) plus
  @cilium/ci-structure, and the auto-approve.yaml workflow is owned
  by @cilium/cilium-maintainers:"
- **Quote**: "Nobody can change the CI pipeline without an explicit review from
  the team responsible for keeping it safe."
- **Quote** (from the post's TL;DR table):
  "Anything under .github/ requires review from the security-focused CI team,
  and auto-approve.yaml requires a maintainer."
- **Our assessment**: Buy it. CODEOWNERS on the pipeline directory is the
  control that makes every *other* control in this note enforceable — the
  allow-list, the two-phase checkout and the single validating action are all
  files under `.github/`, so without this gate they are ordinary PR-editable
  content. The stricter ownership of `auto-approve.yaml` specifically (a
  maintainer team rather than the CI team) is the right calibration: the
  workflow that grants automatic approval is the one whose compromise would
  bypass every other control. Note the corpus already carries CODEOWNERS
  twice — the part 2 note applies it to `vendor/` and the LiteLLM incident
  notes apply it to dependency directories — but **CODEOWNERS on `.github/`
  as the CI-review gate is a distinct use** and is new.

### Claim 14: The series is explicitly layered — this post is the
access-control layer — and the post frames that layer with a year of
open-source supply-chain compromise, Cilium's own unusually large blast
radius, and an explicit statement that the patterns are not
Cilium-specific
- **Evidence**: The series preamble (this is the first post of a
  three-part series, with the TL;DR table organized "by which layer of the
  pipeline each control lives at"), plus the four named incidents in the
  opening paragraph (Axios on npm, LiteLLM's PyPI package, typosquatted
  Trivy forks, and the 2020 SolarWinds breach), the authors' own
  blast-radius statement, and their explicit transferability claim.
- **Confidence**: settled for the series structure and the named
  incidents; the SolarWinds scale figure is the source's own
  characterization of the historical breach
- **Quote**: "This is the first post in a three-part series. This post covers
  access control: who can trigger builds and what code CI is
  allowed to execute. Part 2 will cover dependency hardening, and
  Part 3 credential isolation, release verification, and the gaps
  we’re still closing."
- **Quote**: "If you don’t have time to read the whole series, here’s what
  Cilium does to harden its supply chain today, organized by which
  layer of the pipeline each control lives at:"
- **Quote**: "The last twelve months have been rough on the open source supply
  chain."
- **Quote**: "Typosquatted forks of Trivy were published to catch people who
  fat-finger go install. And the canonical example, the 2020
  SolarWinds breach, is still the cautionary tale we keep coming
  back to: attackers got into the build system and pushed malware
  through normal Orion updates to roughly 18,000 organizations,
  including U.S. federal agencies, NATO, and Microsoft. The malware
  sat dormant for months. The breach went undetected for the better
  part of a year."
- **Quote**: "Cilium runs in the kernel-level networking path of millions of
  Kubernetes pods. If our supply chain were compromised, the blast
  radius would not be small."
- **Quote**: "Most of what follows isn’t Cilium-specific: any open source
  project running CI/CD on GitHub Actions can apply these patterns.
  We’ve also called out where we still fall short, in case any of
  it makes a useful starting point for someone else."
- **Our assessment**: Buy the framing, with one caveat. The layer
  decomposition is the useful part: *intake* (what code enters), *execution*
  (what runs and what code CI may run), *output* (what ships and with what
  credentials). A guide that teaches only one layer teaches an incomplete
  control set. This note fills the *execution/trigger* layer, which parts 2
  and 3 left open. The SolarWinds detail is the most useful number in the
  source — "roughly 18,000 organizations" and "undetected for the better
  part of a year" — because it is the only figure here that shows the
  *detection lag* cost, which is the cost the corpus's incident notes keep
  implying but never quantifying. The caveat: SolarWinds was a build-system
  intrusion that produced *signed* updates, so it illustrates why release
  verification (parts 2/3) matters rather than why trigger control does;
  do not let the guide use it as evidence for a control it does not
  illustrate. The authors' own transferability claim is corroborated by the
  fact that the concrete artifacts are plain GitHub Actions YAML with no
  Cilium-specific machinery.

### Claim 15: The residual gaps in this layer are stated in the same table as the controls — no SLSA provenance, no PR-time dependency review, no `govulncheck` in CI, and internal `@main` references that still need to move to a dedicated composite-actions repo
- **Evidence**: The "Where we still fall short" row of the TL;DR table; the
  full gap list (with the 68 `@main` count, the expired
  `SECURITY-INSIGHTS.yml`, and the missing `go mod verify`) is in the part 3
  note and is deliberately not re-extracted here.
- **Confidence**: settled (first-party admission; details covered in the
  part 3 note)
- **Quote**: "No SLSA provenance yet, no PR-time dependency review, no
  govulncheck in CI, and a handful of internal @main references
  that need to move to a dedicated composite-actions repo."
- **Our assessment**: Buy it, but cite it to the part 3 note for the detail.
  The one genuinely new item in this row is the *reason* the `@main`
  references matter here rather than in part 2: the composite actions that
  carry the security-critical logic (per Claim 8) are themselves the ones
  still referenced by mutable branch refs — so the one control that must not
  be mutable is, in part, mutable. That connection is not made anywhere else
  in the corpus and is worth carrying forward.

## Concrete Artifacts

### Ariane trigger allow-list config (verbatim from the post)

```
.github/ariane-config.yaml
```

```
allowed-teams:
  - organization-members

triggers:
  /test\s*:
    workflows:
      - conformance-aws-cni.yaml
      - conformance-clustermesh.yaml
      - conformance-eks.yaml
    # ...and so on
    depends-on:
      - /build-images-dependency
  /ci-aks:
    workflows:
      - conformance-aks.yaml
    depends-on:
      - /build-images-dependency
```

### Two-phase checkout in the image-build workflow (verbatim from the post)

```
.github/workflows/build-images-ci.yaml
```

```
- name: Checkout base or default branch (trusted)
  uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
  with:
    ref: ${{ github.base_ref || github.event.repository.default_branch }}
    persist-credentials: false

# ...trusted setup steps run here, including loading composite actions...

# Warning: since this is a privileged workflow, subsequent workflow job
# steps must take care not to execute untrusted code.
- name: Checkout pull request branch (NOT TRUSTED)
  uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
  with:
    persist-credentials: false
    ref: ${{ steps.tag.outputs.sha }}
```

### The five stated preconditions for the pattern's safety (verbatim from the post)

```
- No run: steps execute scripts from the untrusted checkout. Every shell
block after the second checkout is written inline in the workflow YAML (disk
usage checks, file copies, digest output). Nothing is sourced from the PR
  branch.
- No composite actions are loaded from the untrusted checkout either. All
composite actions (set-runtime-image, cosign, set-env-variables) come from
the trusted base-branch checkout or from the saved ../cilium-base-branch/
directory. We’re also working on moving these composite actions into a
dedicated repository so we don’t have to check out source to run them at
  all.
- Docker BuildKit does execute the untrusted Dockerfile, and that’s the
whole point of building a CI image from a PR. BuildKit runs in isolation: no
GitHub Actions environment variables, no repo secrets, no access to the
runner’s Docker credential store. The build args we pass contain no secrets,
just the runtime image reference and the operator variant name.
- Untrusted data flows into exactly one trusted action. The
runtime-image*.txt file from the PR is fed into the trusted
set-runtime-image action, which checks the image reference starts with
quay.io/cilium/ and strips newlines so an attacker can’t smuggle in a
GITHUB_ENV injection. There’s no way to repoint the build to anything
outside the Cilium namespace.
- Only CI credentials are in scope. The Docker login uses QUAY_USERNAME_CI /
QUAY_PASSWORD_CI, which can only push to the -ci development registry.
Production credentials aren’t on the runner at all.```

### CODEOWNERS as the CI review gate (verbatim from the post)

```
/.github/                          @cilium/github-sec @cilium/ci-structure
/.github/ariane-config.yaml        @cilium/github-sec @cilium/ci-structure
/.github/renovate.json5            @cilium/github-sec @cilium/ci-structure
/.github/workflows/                @cilium/github-sec @cilium/ci-structure
/.github/workflows/auto-approve.yaml  @cilium/cilium-maintainers
```

### The post's TL;DR table rows for this layer (verbatim cell text)

- Layer "Who triggers builds" → control "Trigger control via Ariane": "Only
  verified org members can fire CI workflows from PR comments, against an
  explicit allow-list of workflows."
- Layer "What code CI executes" → control "Two-phase checkouts for
  pull_request_target": "Trusted code (composite actions, scripts, signing
  logic) is loaded from the base branch; the PR head is only used as Docker
  build context, never executed as a script."
- Layer "Who reviews CI changes" → control "CODEOWNERS gates": "Anything under
  .github/ requires review from the security-focused CI team, and
  auto-approve.yaml requires a maintainer."
- Layer "Where we still fall short" → control "Gaps we're still closing": "No
  SLSA provenance yet, no PR-time dependency review, no govulncheck in CI, and
  a handful of internal @main references that need to move to a dedicated
  composite-actions repo."

(The remaining table rows — SHA pinning, vendoring, static analysis,
credential isolation, signed releases — are parts 2 and 3 material and are
covered by the sibling notes, not re-extracted here.)

### Ariane repository — linked from the source, read for verification

Attribution: `https://github.com/cilium/ariane` (linked from the post) and
`https://raw.githubusercontent.com/cilium/ariane/main/example/ariane-config.yaml`.
These are the bot's own repository, not the blog post; they are quoted here as
supporting artifacts for Claims 2 and 3.

The README states that the app holds the following permissions — note that
org-level `Members: Read-only` is what makes the team gate implementable:

```
Set up permissions & events for the GitHub App:
- Repository permissions:
  - Actions: Read and write
  - Administration: Read-only
  - Checks: Read and write
  - Commit statuses: Read and write
  - Contents: Read-only
  - Issues: Read-only
  - Merge queues: Read-only
  - Pull requests: Read and write
- Organization permissions:
  - Members: Read-only
```

The merge-queue handler is a separate, and separately interesting, trust
decision — the bot can satisfy a required check on its own:

```
Merge Group

A GitHub App watches `merge_group` events. When a PR is added to the merge
queue the app gets all the required checks for the target branch, and marks
the status of the required check as completed with success if its check source
is configured as `any source`.
```

The workflow-run handler is scoped to the project's own bots by name shape — a
bot-impersonation control on the same axis as the part 2 note's
`github.triggering_actor` check:

```
**Note**: This handler only processes PRs created by bot users with username
prefix matching the repository organization name and suffix `[bot]` (e.g., for
organization `isovalent`: `isovalent-renovate[bot]`,
`isovalent-release[bot]`).
```

The example config shows the fuller schema the blog's excerpt implies —
per-workflow path filters, a staged-trigger map, and a bounded rerun policy:

```
allowed-teams:
  - organization-members

triggers:
  /test:
    workflows:
      - foo.yaml
      - bar.yaml
  /test-something-else:
    workflows:
      - baz.yaml
  /default: #special trigger that runs when new PR is opened
    workflows:
      - this-will-run-on-every-open-pr.yaml
  /dependent-on-default:
    workflows:
      - dependent.yaml
    depends-on:
      - /default
workflows:
  foo.yaml:
    paths-ignore-regex: (bar|baz)/
  bar.yaml:
    paths-regex: test
    paths-ignore-regex: baz # every `baz` file will be ignored even if it matches `test`

feedback:
  verbose: true
  reactions: true
  workflows-report: true
  report-all-workflows: true

stages-config:
  label: auto-cicd
  stages:
    - workflows:
        - image-build-releases-ci.yaml
        - tests-smoke.yaml
      command: /test

rerun:
  max-retries: 3
  workflows:
    - conformance-e2e.yaml
    - integration-test.yaml
  exclude-workflows:
    - flaky-test.yaml```

## Cross-References

- **Corroborates**:
  - `blog-cncf-securing-cicd-credentials-verification.md` **Claim 2** (the
    stated worst case of a CI compromise is a malicious `-ci` image that cannot
    publish a production release, because "the credentials simply aren't on
    the runner") — this note's Claim 12 is the *same bounding claim stated
    from the execution side*: the worst case of a compromised PR build is a
    malicious image in the development registry. Two posts, two layers, one
    property: the production secret is absent from the compromised host.
  - `blog-cncf-securing-cicd-credentials-verification.md` **Claim 1** (two
    separately scoped registry credential sets behind distinct protected
    environments) — this note's Claim 11 (precondition 5, CI credentials
    only) is the in-job expression of that same split; the two posts meet at
    the `-ci` tag boundary.
  - `blog-cncf-securing-cicd-credentials-verification.md` **Claim 4** (every
    `actions/checkout` call sets `persist-credentials: false`, so the token
    never lands in the runner's git config) — visible directly in this post's
    two-phase checkout artifact, where both checkouts carry
    `persist-credentials: false`. Same convention, independently visible.
  - `blog-cncf-securing-cicd-credentials-verification.md` **Claim 15** (the
    series' defense-in-depth framing: "access controls so only trusted people
    can trigger builds, pinned digests so a compromised tag can't reach us,
    least-privilege permissions … credential isolation … and signatures so
    users can verify what they're running") — this note is the **first clause
    of that sentence** ("access controls so only trusted people can trigger
    builds"), which the part 3 note states as a thesis but never substantiates.
  - `blog-cncf-securing-cicd-locking-down-dependencies.md` **Claim 1** ("Once
    you control who triggers builds, the next question is what code those
    builds pull in. A pinned workflow that fetches a compromised dependency is
    still a compromised workflow.") — this note's Claim 1 and Claim 2 are the
    *once you control who triggers builds* half. The two sibling notes now
    form the complete chain: trigger control (this note) → intake control
    (part 2) → output/credential control (part 3).
  - `blog-cncf-securing-cicd-locking-down-dependencies.md` **Claim 12** (GitHub
    Actions expression injection is a distinct vulnerability class: `${{ }}` is
    pre-bash text substitution, so untrusted input flowing into a `run:` block
    executes as shell; the fix is env-var indirection) — this note's Claim 10
    is the *same class of injection* reached through a different channel
    (a newline in a file value reaching `GITHUB_ENV` rather than an
    expression reaching bash). Both notes agree that the mitigation is a
    validating boundary between untrusted data and the execution environment.
  - `docs-promptfoo-code-scan-github-action.md` **Claim 1** (intra-job
    environment-state persistence — a PR-controlled step can persist
    `$GITHUB_PATH`, `$GITHUB_ENV`, or `$HOME` writes that later steps inherit)
    — this note's Claim 10 is the upstream fix for one of those exact
    channels (`GITHUB_ENV`), and Claim 7 (no `run:` step executes PR-tree
    code) is the structural fix for the whole family. The two notes
    independently arrive at "keep untrusted data out of the job's execution
    context".
  - `docs-promptfoo-code-scan-github-action.md` **Claim 8** (pin third-party
    actions to full commit SHAs; a tag is mutable) — visible in this post's
    workflow artifact, where both `actions/checkout` references are pinned to
    the same 40-character SHA with the version kept as a comment.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 3** (root
    cause — a compromised Trivy security-scanner dependency in the CI/CD
    pipeline) — this post names the same tool from the attacker's side:
    "Typosquatted forks of Trivy were published to catch people who fat-finger
    go install" (Claim 14). Same tool, same year, one as the exploited
    dependency and one as the typosquatted impostor.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 5**
    (contributing factor — static long-lived release credentials available as
    environment variables, so a compromised step could reach them directly) —
    this note's Claims 11–12 are the prevention of exactly that: the
    credential that is reachable on the runner can only write to a
    non-production namespace.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 11**
    (remediation — the pipeline broken into four semantic concepts, each run
    in isolated environments) — this note's Claim 5 is the same
    isolation-by-construction idea applied at *code* granularity rather than
    stage granularity: the trusted tree and the untrusted tree coexist in one
    job because only one of them is executable.
- **Contradicts**: None. No existing source note claims that shared CI
  environments, static release credentials, mutable refs, or unscoped automerge
  are safe, and none opposes trigger control, two-phase checkout, or
  CODEOWNERS gating. `CONTRADICTIONS.md` contains no open entries and no
  existing `C-NNN` covers this territory. One near-miss was checked and
  rejected as a contradiction:
  - `docs-promptfoo-code-scan-github-action.md` **Claim 1** prescribes "keep
    the scan in a job that only checks out and scans the PR; run untrusted
    build steps in a separate job", and the guide currently states "Treat the
    job, not the stage, as the isolation boundary for untrusted code"
    (`guide/06-security-and-trust.md:741-743`). Read strictly, Cilium's
    two-phase pattern keeps the untrusted Dockerfile and the CI credentials
    in the *same* job, which the guide's rule would forbid. This is **not** a
    contradiction — it is a conditioning variable. The two designs differ in
    *whether untrusted code executes inside the Actions job at all*: the
    promptfoo design moves it to another job, Cilium's design ensures the
    untrusted tree is never executable by the job and confines the only
    execution to BuildKit, which is deliberately emptied of env vars, secrets,
    and credential store. Both satisfy the guide's underlying principle (a
    step holding a credential must not share a context with PR-controlled
    code); they differ in the mechanism, not in the claim. The guide should
    carry both, and should state that the job boundary is the *default* and
    the two-phase pattern is the exception that requires the five enumerated
    preconditions to hold. No contradiction issue filed.
  - A second near-miss: `blog-cncf-securing-cicd-credentials-verification.md`
    **Claim 14** lists GitHub's roadmap as including "org-level rulesets
    banning `pull_request_target`", while this post describes Cilium using
    `pull_request_target` with mitigating controls. Rejected as a
    contradiction: part 3's statement is about a *planned platform
    capability* (a ruleset a project may adopt), not a claim that current
    usage is safe or unsafe, and this post's statement is about current
    practice with stated compensating controls. Different propositions about
    different things; no shared claim is opposed.
- **Extends**:
  - `blog-cncf-securing-cicd-locking-down-dependencies.md` and
    `blog-cncf-securing-cicd-credentials-verification.md` — same series,
    parts 2 and 3 (already extracted as issues #1793 and #1676). This note
    is the series' **missing first layer**: part 2 controls what code enters
    the build, part 3 controls what the build can touch on the way out, and
    neither controls *who may start the build at all* or *which code the
    build is allowed to execute*. Overlapping material deliberately not
    re-extracted: the 68 internal `@main` refs, the GitHub 2026 roadmap
    items, the credential-environment mechanics and the signing pipeline are
    cited here rather than duplicated (Claims 11, 12, 15).
  - `blog-cncf-network-boundary-ai-agents-nginx-otel.md` **Claim 1** (the
    boundary must be a property of the architecture — "That makes the
    boundary a property of the architecture, not a policy we hope the
    application respects") — same thesis, different domain. That note
    enforces agent egress at the network layer; this note enforces code
    separation at the CI-job layer (trusted tree executes, untrusted tree is
    inert data). Worth cross-linking as two applications of one design
    principle, and as a caution: in both cases the architecture, not a
    policy document, is what an attacker cannot talk their way past.
  - `failure-litellm-supply-chain-compromise-march-2026.md` **Lesson 4**
    (impact scoping must be deployment-path-aware) — this note's Claim 12 is
    the same idea applied to *registry namespaces* rather than installation
    paths: the compromised build has one path it can write to, and it is not
    the path users pull from. **Lesson 1** (release integrity is distinct from
    repo integrity) — this note adds the *execution* boundary that the
    incident lacked: a poisoned release can also be produced by a build that
    was correctly triggered but executed the wrong code.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` **Claim 5**
    (declarative systems decompose into small modules with bounded blast
    radius; one growing imperative script eventually half-deploys your whole
    infrastructure) — adjacent rather than overlapping, cited for the
    cross-domain shape: a hand-enumerated allow-list and a named owning team
    are the declarative-style decomposition of *who may run what*, applied to
    a CI trigger surface instead of a change-management surface.
- **Novel**: First source note in the corpus covering:
  1. **Trigger control as a distinct trust boundary** — an in-house bot that
     checks team membership and a hand-enumerated workflow allow-list before
     dispatching, so a trigger phrase is a *request*, not a capability
     (Claims 2, 3, 4).
  2. **The two-phase checkout** — trusted base-branch checkout first, PR head
     second and only as build context, with the PR tree never executable by
     the job (Claim 5).
  3. **A security pattern published with its safety preconditions enumerated**
     — five invariants, each stated as a checkable property of the workflow
     YAML, plus the honest admission that scanners flag the pattern and are
     right in the general case (Claims 6–11).
  4. **The single-choke-point validating action** — `set-runtime-image` as the
     only place untrusted data enters the trusted path, enforcing an
     allow-listed image prefix and stripping newlines to block `GITHUB_ENV`
     injection (Claim 10).
  5. **A documented, intentional, preconditioned security exception** with an
     explicit report-handling stance — "We do appreciate every report and read
     each one carefully, but this pattern is intentional" (Claim 12).
  6. **CODEOWNERS on `.github/` as the CI-change review gate**, with the
     auto-approve workflow separately owned by maintainers (Claim 13).
  7. **A CI bot that can itself satisfy a required check** in the merge queue
     (Ariane's `merge_group` handler) and a bot-impersonation control on the
     workflow-run handler (Concrete Artifacts).

## Guide Impact

- **Chapter 06 (Security and Trust)**, "Supply-chain security for LLM
  infrastructure" (`guide/06-security-and-trust.md:634`): Add a new
  subsection immediately after "Three CI/CD anti-patterns that enabled a
  supply-chain compromise" (`guide/06-security-and-trust.md:691`) and before
  "Job-level isolation is not step-level isolation"
  (`guide/06-security-and-trust.md:729`), titled something like
  **Access control: who may trigger the build, and what code it may run**.
  Three specific additions:
  1. Open the section with the framing sentence — "The first question in any
     CI supply chain story is: who can trigger a build, and what code does it
     execute?" — because the section currently starts downstream at pinning
     and never asks whether the trigger was legitimate (cite Claim 1).
  2. Add the **trigger allow-list** pattern as a fourth remediation
     component alongside the existing "isolated per-stage CI/CD environments,
     ephemeral credentials, and pinned-SHA + cooldown + automated scanning"
     list at `guide/06-security-and-trust.md:709-714`: a bot (or a wrapper)
     that checks the requester's membership in an enumerated team and fires
     only workflows named in a hand-maintained allow-list, so an untrusted
     commenter cannot spend CI minutes or trigger expensive suites (cite
     Claims 2, 3, 4). For an LLM-ops reader the concrete harm to name is
     GPU-hours, not just CI minutes.
  3. Add the **two-phase checkout** with its five enumerated preconditions as
     the worked example of how to make a `pull_request_target` job safe, and
     — importantly — state that it is safe *only* when all five hold
     (cite Claims 5–11). Recommend the guide present the five preconditions
      as a review checklist in the same style as the existing "Treat the job,
      not the stage, as the isolation boundary" rule, and add the
      `set-runtime-image` choke point (allow-listed prefix
     + newline stripping against `GITHUB_ENV` injection) as the corpus's first
     concrete statement of that injection channel (cite Claim 10).
- **Chapter 06**, "Three CI/CD anti-patterns" section: Extend the
  remediation paragraph at `guide/06-security-and-trust.md:709-714` with a
  fourth item — *unrestricted trigger surface* — and note that the LiteLLM
  incident note's Claim 4 (shared environment across stages) has a
  same-job analogue: untrusted code sharing a job with a credential-bearing
  step (cite Claims 4, 5).
- **Chapter 06**, "Job-level isolation is not step-level isolation"
  (`guide/06-security-and-trust.md:729-743`): Add the two-phase checkout as
  the **second** structural option alongside "put untrusted build steps in a
  separate job", and be explicit that the job boundary is the default while
  the two-phase pattern is an exception that requires the five preconditions
  to hold (cite Claims 5–11). Also add the operational rule this source
  demonstrates: a `pull_request_target` + second-checkout finding from a
  scanner is a *true* positive unless the preconditions hold — document the
  preconditions in-repo so the next report can be answered with a checklist
  rather than a rewrite (cite Claims 6, 12).
- **Chapter 06**, new trust-layer material: Add **CODEOWNERS on the CI
  directory** as the control that makes the pipeline's other controls
  enforceable, and recommend the stricter-owner pattern (the auto-approve
  workflow owned by maintainers rather than by the CI team) (cite Claim 13).
  This is a distinct use from the corpus's existing CODEOWNERS-on-`vendor/`
  material and is worth its own paragraph.
- **Chapter 05 (LLM Ops Reliability)**, "CI/CD supply-chain isolation"
  (`guide/05-llm-ops-reliability.md:1359`): The section currently cites only
  LiteLLM's CI/CD v2 goals (limit per-stage package access, reduce sensitive
  env vars, avoid compromised packages, reduce release-tampering risk). Add
  this source as the **access-control** half of stage isolation: trigger
  allow-list, two-phase checkout, and CODEOWNERS gating of the pipeline
  directory (cite Claims 2, 3, 5, 13). Pair with the existing blast-radius
  rule: the guide's "Isolate CI/CD stages by blast radius" is currently
  stage-granular; this source shows the same principle applied to *which code
  a stage may execute*.
- **Chapter 03 (or wherever the corpus's agent-triggered CI is discussed)**:
  Flag the direct applicability — a repo whose CI dispatches on issue labels
  or PR comments (as this corpus's own `workflow_dispatch` Miner/Assayer
  drains do) has the same trigger surface, and the Ariane pattern is the
  reference implementation (cite Claims 2, 4).
- **Chapter 00 (Principles)**: The "bounded blast radius" formulation — the
  worst case is a bad artifact in a non-production namespace, not a
  compromised release path — is a clean blast-radius-reduction example to
  pair with the part 3 note's "the credentials simply aren't on the runner"
  (cite Claims 11, 12).

## Extraction Notes

- Source read in full: the CNCF Member Post page (published 2026-06-04,
  ~11 KB of extractable body text). This is **part 1** of a three-part series;
  parts 2 and 3 are already mined as separate notes and were deliberately
  not re-extracted (see Cross-References → Extends).
- One linked sub-page was followed for verification: the `cilium/ariane`
  repository linked from the post, including its
  `example/ariane-config.yaml`. It confirmed the trigger mechanism (a GitHub
  App watching PR comments and dispatching via `workflow_dispatch`, gated on
  allowed teams), the required org-level `Members: Read-only` permission, the
  merge-group handler that can mark a required check successful, and the
  bot-identity scoping of the workflow-run handler. Artifacts from it are
  quoted with explicit attribution so the Assayer does not mistake them for
  blog-post text.
- The canonical Cilium-hosted version of this post
  (`https://cilium.io/blog/2026/05/06/securing-cicd-open-source-lessons-from-cilium/`,
  which the TL;DR table's anchors point at) was fetched but did not render
  server-side content — the fetch returned only the page title — so **no text
  was extracted from it** and no quote in this note comes from it. No
  material was lost: the CNCF page carries the full part 1 body (threat
  context, TL;DR table, Ariane, two-phase checkout with all five
  preconditions, CODEOWNERS), and the TL;DR table's rows for parts 2 and 3
  are cited to the sibling notes instead.
- Third-party links in the source (the Axios npm compromise write-up, the
  LiteLLM PyPI hijack write-up, the Trivy typosquatting write-up, the
  SolarWinds reference, and the GitHub Security Lab `pull_request_target`
  write-up) were **not** fetched. The claims about those incidents in this
  note are attributed to what the post itself says about them; the
  LiteLLM-hijack item is cross-referenced to the corpus's own
  first-party incident notes rather than to the third-party write-up.
- `date_published` set to 2026-06-04 (page dateline). `date_extracted` and
  `last_checked` set to 2026-10-21 UTC.
- `confidence_overall` set to `emerging`: the post is a first-party
  self-report of the project's own configuration, consistent with the posture
  of the two sibling notes. The individual claims are concrete and checkable
  (config shown verbatim, named teams, named actions, linked public
  repository), but they are not independently verified, and two load-bearing
  assertions — "BuildKit runs in isolation" and the actual enforcement of the
  Ariane team gate — are the authors' own characterizations rather than
  demonstrated facts. The pattern is also explicitly a set of *design
  invariants*: the post asserts the invariants hold; it does not show a test
  that they hold.
- The `miner-related-notes.md` candidates list was read per MINER.md §4. Of
  the 10 listed candidates, one is cited and nine are explicitly dismissed as
  non-overlapping:
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SRE
    SLOs, real-timeyness, user-facing cost of failure; no CI/CD access
    control. Dismissed.
  - `blog-cncf-securing-cicd-credentials-verification.md` — **cited**
    (Corroborates Claims 1, 2, 4, 15; Extends). Same series, part 3; already
    in the corpus as issue #1676. Claims re-read and verified per §4b.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative
    vs declarative change workflows; no trigger-control or CI access-control
    content. Dismissed as a candidate, but a single adjacent claim (Claim 5,
    bounded blast radius via decomposition) is cited under Extends because
    the shape genuinely carries over. Claims re-read and verified per §4b.
  - `docs-google-sre-reliable-product-launches.md` — launch-coordination
    process (checklists, launch gates); no CI/CD supply-chain content.
    Dismissed.
  - `docs-litellm-anthropic-advisor-tool.md` — a model-composition feature
    (advisor token accounting, streaming hops); unrelated. Dismissed.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO framework
    components and error budgets; unrelated. Dismissed.
  - `docs-promptfoo-enterprise-audit-logging.md` — audit-log event taxonomy
    and record schema for an enterprise eval platform; no CI trigger or
    pipeline-review content. Dismissed.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — multi-agent
    security platform on Kubernetes (per-agent Deployments, inter-agent
    mTLS, OPA/Kyverno policy-as-code, Isolation Forest anomaly gating); no
    CI/CD pipeline-control content, despite the security subject matter.
    Dismissed.
  - `blog-litellm-valkey-semantic-caching.md` — semantic caching backends
    for a gateway; unrelated. Dismissed.
  - `docs-google-sre-eliminating-toil.md` — toil taxonomy and automation
    framing; no supply-chain content. Dismissed.
  The remaining useful cross-references (the part 2 sibling note, the two
  LiteLLM supply-chain failure notes, the promptfoo code-scan note, and the
  NGINX network-boundary note) were identified from the Prospector triage and
  from searching `source-notes/`; each cited claim was re-read and verified
  per §4b before citation.
- Per the triage's caveat, Cilium-specific release-process detail was not
  extracted as LLM-ops guidance, and the no-AI/LLM-content caveat was
  followed: only the transferable controls (trigger allow-list, two-phase
  checkout with preconditions, CODEOWNERS gating, bounded blast radius) are
  carried.
- No contradiction issue filed: checked the two sibling notes, the two
  LiteLLM supply-chain failure notes, the promptfoo code-scan note, and
  `CONTRADICTIONS.md` (which has no open entries). Two near-misses were
  identified and explicitly rejected as contradictions (the job-isolation
  design difference and the `pull_request_target` roadmap item) — both are
  analyzed under Cross-References → Contradicts.


