---
source_url: https://www.cncf.io/blog/2026/06/12/securing-ci-cd-for-an-open-source-project-locking-down-dependencies
source_type: blog-post
title: "Securing CI/CD for an open source project: Locking down dependencies"
author: "André Martins (Cilium maintainer and Software Engineer, Isovalent at Cisco) and Feroz Salam (Cilium Security Team and Security Engineer, Isovalent at Cisco)"
date_published: 2026-06-12
date_extracted: 2026-10-19
last_checked: 2026-10-19
status: current
confidence_overall: emerging
issue: "#1793"
---

# Securing CI/CD for an open source project: Locking down dependencies

> Cilium's first-party account of its dependency-intake layer: full 40-char
> SHA pinning of every `uses:` action and `@sha256` digest pinning of CI
> container images — with the honest admission that transitive action
> dependencies remain a blind spot until GitHub's workflow-level
> `dependencies:` lock ships — plus a Renovate configuration that treats
> automated updates as a trust boundary (`minimumReleaseAge: "5 days"`
> cooldown, trusted-namespace auto-merge allowlist, an auto-approve workflow
> that verifies `github.triggering_actor` against bot impersonation) and Go
> module vendoring that moves the trust decision from build time to review
> time. This is the dependency-intake companion to the series' part 3
> (credentials/signing), and the concrete implementation of the "pinned-SHA
> + cooldown" remediation the corpus currently carries only as a rule from
> the LiteLLM March 2026 incident.

## Source Context

- **Type**: blog-post (CNCF Member Post — the second post in a three-part
  series on how the Cilium project hardens its own CI/CD pipeline. Part 1
  covered access control, part 3 covered credentials and verification).
- **Author credibility**: High for a first-party engineering account. Authors
  are André Martins (Cilium maintainer, Software Engineer at Isovalent/Cisco)
  and Feroz Salam (Cilium Security Team, Security Engineer at Isovalent/Cisco)
  — the same authors as the already-extracted part 3 note. The post describes
  the project's actual configuration (Renovate config, auto-approve workflow
  conditions, vendoring CI) and links directly to the files in Cilium's public
  repository, but the claim set is a self-report and is not independently
  verified.
- **Scope**: Covers the dependency layer: GitHub Actions SHA/digest pinning,
  the transitive-dependency blind spot and GitHub's announced fix, Renovate
  as an update mechanism with a trust boundary (cooldown, allowlist
  auto-merge, bot-identity verification), Go module vendoring with drift
  checks, the fork-vs-pin escalation tradeoff, typosquatting evidence, and
  static-analysis enforcement of workflow hygiene including GitHub Actions
  expression injection. Does NOT cover access control (part 1) or
  credentials/signing (part 3, already extracted), Cilium-specific release
  process detail, or any AI/LLM content — this is a general Go CNCF project's
  CI/CD dependency hardening, and no reliability metrics, latency numbers,
  or incident data are present. Quantitative content is limited to config
  values (5-day cooldown) and the `utfave` typosquat example.
- **Prospector framing**: Triage routed this as `triaged:text`, novelty
  medium, priority medium, relevant to Ch06 (Security and Trust — "Pin
  everything; verify releases", "A SHA pin says what you have; an attestation
  says who built it", "Three CI/CD anti-patterns"), secondarily Ch05
  ("CI/CD supply-chain isolation"). The intended value is the transferable
  dependency-hygiene practice for LLM infrastructure, not AI-native content.

## Extracted Claims

### Claim 1: Action pinning and dependency pinning compose — "A pinned workflow that fetches a compromised dependency is still a compromised workflow"
- **Evidence**: Stated as the threat-model framing for the whole dependency
  layer, positioned as the follow-on question after access control.
- **Confidence**: settled (a position statement, but one the corpus's
  incident evidence directly supports)
- **Quote**: "Once you control who triggers builds, the next question is what
  code those builds pull in. A pinned workflow that fetches a compromised
  dependency is still a compromised workflow."
- **Our assessment**: Buy it, and this is the missing linking statement for
  the guide's current pinning material. The guide's "Pin everything" rule
  (`guide/06-security-and-trust.md:636`) treats action pinning and package
  pinning as separate controls; this sentence states that they compose —
  pinning the workflow does not immunize it against a compromised thing the
  workflow pulls at runtime. It is also the direct generalization of the
  LiteLLM incident's root cause (a pinned-everything pipeline defeated by one
  unpinned scanner dependency).

### Claim 2: Every `uses:` action is pinned to a full 40-character commit SHA (tag kept as a comment) and CI container images are pinned by `@sha256:` digest
- **Evidence**: Concrete config example shown verbatim; the post names the
  affected third-party actions (`docker/build-push-action`,
  `sigstore/cosign-installer`, `golangci/golangci-lint-action`, "and dozens
  more").
- **Confidence**: settled (config shown verbatim, checkable in the public
  repository)
- **Quote**: "The single highest-leverage thing any project can do here is
  stop trusting mutable tags."
- **Quote**: "If somebody compromises the v6 tag on actions/checkout and
  force-pushes malicious code, our workflows won't pull it. They're pinned to
  a specific commit."
- **Quote**: "We pin container images used directly in workflow steps the
  same way, by `@sha256:` digest, so even the tools we run inside CI are
  content-addressed."
- **Our assessment**: Buy it. The SHA-pin half is already corpus-settled
  (promptfoo note Claim 8, LiteLLM incident Claim 14); the addition here is
  (a) the first-party scale claim ("dozens more") from a mature CNCF project
  and (b) explicit *image digest* pinning for in-workflow containers — the
  corpus's existing pinning material covers actions and packages but not the
  container-image-in-workflow channel.

### Claim 3: Pinning's honest blind spot — a pinned action that references another action by tag resolves that nested dependency at runtime, invisible to the pinner; GitHub's workflow-level `dependencies:` lock (direct + transitive, `go.mod`/`go.sum`-style) is the announced fix but is not yet available
- **Evidence**: Stated as the explicit limit of the pinning control, with the
  forward-looking platform fix named and linked (GitHub's 2026 Actions
  security roadmap).
- **Confidence**: settled for the blind-spot statement (a mechanical property
  of Actions resolution); emerging for the `dependencies:` lock (announced
  roadmap feature, not shipped)
- **Quote**: "Pinning has one annoying blind spot, which is transitive
  dependencies. When we pin actions/checkout@de0fac2e… we know exactly which
  code runs for that action. But if actions/checkout itself references
  another action by tag (`uses: some-org/some-helper@v1`), that resolution
  happens at runtime and is invisible to us. An attacker who pops the nested
  dependency can still reach our pipeline."
- **Quote**: "We'll adopt it as soon as it ships."
- **Our assessment**: Buy it. This is the honest caveat the guide's "pin
  everything" rule currently lacks: a SHA pin covers the pinned artifact and
  nothing it pulls by tag at runtime. The guide should state the limit
  explicitly and mark the `dependencies:` lockfile as `emerging` — the same
  roadmap item appears in the part 3 note (Claim 14 there) and should be
  cited once, from either note, not treated as new capability.

### Claim 4: Renovate maintains the pins mechanically — `helpers: pinGitHubActionDigests` preset plus global `pinDigests: true`, running as a self-hosted bot on a dedicated GitHub App (not a personal access token), with `vulnerabilityAlerts` on
- **Evidence**: Configuration described with links to Cilium's actual
  `renovate.json5` and `renovate.yaml` workflow files in the public repo.
- **Confidence**: settled (first-party description of the project's own
  config, linked to source files)
- **Quote**: "Maintaining SHA pins by hand would be miserable, so we don't.
  Our Renovate configuration extends the `helpers: pinGitHubActionDigests`
  preset and sets `pinDigests: true` globally."
- **Quote**: "We stay current without ever falling back to a mutable ref."
- **Quote**: "Renovate runs as a self-hosted bot on an hourly schedule, using
  a dedicated GitHub App with fine-grained permissions instead of a personal
  access token. `vulnerabilityAlerts` is on, so known CVEs in the dependency
  tree turn into PRs straight away."
- **Our assessment**: Buy it. The subtle point is that SHA pinning without an
  automated update mechanism decays into either staleness (unpatched pinned
  versions) or policy erosion (people fall back to tags); Renovate is what
  makes full-SHA pinning operationally sustainable at dozens-of-actions scale.
  The GitHub-App-instead-of-PAT choice is itself a credential-hygiene control
  (a PAT is a human identity with org-wide reach; a GitHub App installation
  token is scoped and expirable) — consistent with the corpus's
  ephemeral-credential theme.

### Claim 5: A 5-day release-age cooldown (`minimumReleaseAge: "5 days"`) delays adoption of brand-new releases — the window in which a compromised package typically gets noticed and yanked
- **Evidence**: Renovate config shown verbatim with a comment stating the
  intent; linked to the Cilium PR that introduced it; explicit threat-model
  rationale.
- **Confidence**: settled (config shown verbatim; the rationale is a
  reasoned security heuristic, not measured data)
- **Quote**: "We recently added a Renovate cooldown so we don't pick up
  brand-new releases the moment they appear. Given the current pace of supply
  chain attacks, those few days are usually the window in which a compromised
  package gets noticed and yanked:"
- **Our assessment**: Buy it, and this is the highest-value copyable nugget
  in the post for the corpus. The LiteLLM incident note's Claim 14 recommends
  "add an upgrade cooldown period" as remediation but gives no mechanism or
  duration; this post supplies both — the concrete Renovate key
  (`minimumReleaseAge: "5 days"`, applied to major/minor/patch) and the
  rationale that maps the cooldown onto the compromise-detection window. The
  5-day figure is a judgment call, not a derived constant; teams with faster
  advisory pipelines can justify shorter, but the *existence* of a cooldown
  is the control.

### Claim 6: Automated updates are scoped by a trust boundary — an allowlist of trusted publisher namespaces (`actions/`, `docker/`, `cilium/`, `k8s.io/`, `sigs.k8s.io/`, `golang.org/x/`, etc.) auto-merges after CI; everything else requires human review
- **Evidence**: Renovate config shown verbatim with the allowlist and
  `automerge: true` / `groupName: "auto-merge-trusted-deps"` settings.
- **Confidence**: settled (config shown verbatim)
- **Quote**: "Updates from this allow-list auto-merge after CI passes.
  Everything else needs a human review."
- **Our assessment**: Buy it. This is the corpus's first concrete
  implementation of "where does the human trust boundary sit in automated
  dependency updates": not "automerge everything green" and not "human-review
  everything" (which doesn't scale and quietly rots), but a publisher-scoped
  allowlist where the trust decision is made once, per namespace, in a
  reviewable config file. The scoping is by *publisher* (`actions/`,
  `k8s.io/`) rather than by package, which is the right granularity: you are
  trusting an org's release process, not individual artifact histories.

### Claim 7: The auto-approve workflow verifies not just the PR author but `github.triggering_actor` — defending against a human triggering actions while impersonating the bot
- **Evidence**: Conditional shown verbatim from Cilium's auto-approve
  workflow, with the threat it defends against stated explicitly.
- **Confidence**: settled (config shown verbatim; the spoofing threat is a
  real GitHub Actions identity property)
- **Quote**: "it verifies that the PR was created by cilium-renovate[bot]
  and that the review request was actually triggered by the bot itself, not
  by a human pretending to be it"
- **Quote**: "If those conditions don't hold, no `auto-approval` happens."
- **Our assessment**: Buy it. `pull_request.user.login` records who authored
  the PR; `github.triggering_actor` records who actually set the event in
  motion — they can diverge, and an auto-approve rule that checks only the
  author can be satisfied by a human-created PR that merely *looks* like it
  came from the bot's ecosystem. Checking both is a two-factor identity gate
  on a fully-automated merge path, and it is the kind of detail that separates
  a real trust boundary from a decorative one. Directly transferable to any
  repo running LLM-agent CI with auto-merge (a live concern for this corpus's
  own automation).

### Claim 8: Go module vendoring relocates the trust decision — builds never contact external module proxies, CI verifies `go.mod`/`go.sum`/`vendor/` drift, and "it moves the trust decision from build time, where it's invisible, to review time, where a human can see the diff"
- **Evidence**: Stated as the project's practice, with the drift-check
  workflow linked and a license-check command named.
- **Confidence**: settled (first-party description of the project's own
  config)
- **Quote**: "All Go dependencies are vendored and committed to the repo."
- **Quote**: "Builds are reproducible and don't talk to external module
  proxies at build time, so a tampered module on a proxy never reaches us."
- **Quote**: "That's why we vendor: it moves the trust decision from build
  time, where it's invisible, to review time, where a human can see the
  diff."
- **Our assessment**: Buy it, and the framing sentence is the transferable
  core. Vendoring is not primarily a reproducibility or availability control
  here — it is a *visibility* control: dependency content becomes a reviewable
  diff in the same PR as the code that consumes it. The transfer to LLM
  infra is direct: Python `requirements.txt`/lockfiles with hash-checked
  wheels and npm lockfiles are the same move (dependency content in the
  review surface), and the pattern pairs with the corpus's existing
  unpinned-install exposure material (LiteLLM compromise Lesson 4). The
  build-time network silence ("don't talk to external module proxies") is
  the same architecture-over-policy shape as the part 3 note's "the
  credentials simply aren't on the runner."

### Claim 9: Vendoring's honest limitation — a typosquatted import shows up as a `vendor/` diff only if a reviewer notices the unfamiliar path; it does not catch the typo at introduction. CODEOWNERS gating on `vendor/` is what held up "so far"
- **Evidence**: Stated limitation plus concrete typosquat evidence from
  third-party research (Michael Henriksen's survey found a fork of
  `urfave/cli` registered as `utfave` that exfiltrated hostname/OS/arch).
- **Confidence**: settled for the mechanics and the example; the "held up
  well so far" efficacy claim is anecdotal (first-party, no incident count)
- **Quote**: "It doesn't catch the typo at the moment it's introduced (it
  relies on a reviewer noticing the unfamiliar path in the PR), but combined
  with CODEOWNERS gating it has held up well so far."
- **Quote**: "Swapping that callback for a reverse shell would have been a
  one-line change."
- **Our assessment**: Buy the limitation — it is the same failure mode as the
  part 3 note's `provenance: false` gap: the control exists but its efficacy
  rests on human attention at review time, which is exactly where static
  analysis (this post's Claim 12) is recruited as the backstop. The `utfave`
  example is a concrete, memorable artifact for the guide's typosquatting
  material. Also worth carrying: Go's import paths include the source org,
  which the post says "kills off the Dependency Confusion attack class
  entirely" — a language-ecosystem conditioning variable the guide should
  state when generalizing to Python/npm (where dependency confusion remains
  live).

### Claim 10: The fork-vs-pin decision, stated as a calibrated tradeoff — Cilium deliberately does not fork third-party actions (maintenance burden, stale-fork risk, doubled Renovate chain), and names the escalation criterion: "If a major action provider got repeatedly compromised, forking the high-risk ones is a reasonable escalation"
- **Evidence**: Three named cost arguments (maintenance burden, missed
  upstream improvements, Renovate chain complexity) plus the explicit
  condition that would flip the decision.
- **Confidence**: settled (a reasoned position with named conditions, not an
  empirical claim)
- **Quote**: "SHA pinning gives us the immutability guarantee that actually
  matters: a specific commit is a specific commit, regardless of which org
  hosts it."
- **Quote**: "If a major action provider got repeatedly compromised, forking
  the high-risk ones is a reasonable escalation, but we haven't been pushed
  to that point."
- **Our assessment**: Buy it. This is useful as a calibrated "when to
  escalate" rule rather than an absolutist one — the corpus's pinning advice
  currently stops at "pin to SHA" without addressing the next rung
  (fork-and-pin) or when to climb it. The stale-fork argument is the
  strongest: a fork accumulates its own unpatched vulnerabilities, converting
  a supply-chain risk into a patch-lag risk. The companion Go-dependency
  argument — "A little copying is better than a little dependency" — plus
  the deliberate tree-shrinking practice (periodic third-party library audits,
  replacing small-utility dependencies with inlined code, an explicit
  hand-managed disabled-dependency list) extends the same reasoning into the
  package layer: "Every dependency you remove is one that can never be
  compromised and reviewing future dependency changes gets easier."

### Claim 11: Workflow-hygiene policy is enforced by static analysis, not reviewer memory — CodeQL's `actions/missing-workflow-permissions` rule fails any modified workflow lacking explicit `permissions:`, and actionlint enforces conventions including no floating `ubuntu-latest` runner (pinned to `ubuntu-24.04`) and names on every job and step
- **Evidence**: Both tools and specific rules named; the runner pin version
  given; enforcement mode stated (fails the workflow, runs on every push
  and PR).
- **Confidence**: settled (tool configuration, checkable)
- **Quote**: "We don't rely on memory for this, though. CodeQL runs on every
  push and PR with the actions/missing-workflow-permissions rule turned on,
  and the workflow fails any modified workflow file that doesn't set
  permissions explicitly."
- **Quote**: "The same lint pipeline also enforces project conventions:
  every job and step has a name, no job uses the floating ubuntu-latest
  runner tag (we pin to ubuntu-24.04), and there's no trailing whitespace in
  workflow files."
- **Our assessment**: Buy it. The architecture-over-policy theme again: the
  least-privilege `permissions:` convention (already in the part 3 note,
  Claim 3) is only as good as its enforcement, and here enforcement is a
  failing CI check rather than a style guide. `ubuntu-latest` floating is a
  mutable-ref anti-pattern of exactly the class SHA-pinning addresses, applied
  to the runner image itself — a channel the corpus has not yet named.

### Claim 12: GitHub Actions expression injection is a distinct vulnerability class — `${{ }}` is pre-bash text substitution, so untrusted input (PR title, branch name) flowing into a `run:` block executes as shell; the fix is env-var indirection, and both actionlint and CodeQL flag the pattern
- **Evidence**: The attack mechanics stated precisely; the fix stated
  precisely; the authors disclose that the GitHub security team reported
  instances in their own workflows and they "fixed every instance."
- **Confidence**: settled (mechanical behavior of the platform, confirmed by
  a third-party security-team report and subsequent fixes)
- **Quote**: "The ${{ }} syntax in workflow YAML is a text substitution that
  happens before bash sees the line at all. If an attacker controls the value
  being substituted (a PR title, a branch name), they can inject arbitrary
  shell commands via ;, $(…), or backticks. Bash has no idea where the value
  came from."
- **Quote**: "It's a subtle bug that's easy to introduce and hard to spot in
  review, which is exactly why static analysis matters: both actionlint and
  CodeQL flag ${{ }} usage in run: blocks where untrusted input flows in."
- **Our assessment**: Buy it in full. This is the single most transferable
  vulnerability class in the post for this corpus specifically: any repo
  running LLM-agent CI (including this one) writes workflows that interpolate
  issue titles, branch names, and model outputs — all attacker-influenced in
  the general case — and the failure is silent-by-default because the
  substitution happens before bash. The env-var indirection fix is small and
  copyable. Recommend the guide carry it as a named anti-pattern alongside
  the existing "Three CI/CD anti-patterns."

## Concrete Artifacts

All artifacts verbatim from
https://www.cncf.io/blog/2026/06/12/securing-ci-cd-for-an-open-source-project-locking-down-dependencies.

### SHA-pinned action reference (verbatim)

```
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
```

### Renovate cooldown + trusted-namespace auto-merge config (verbatim from the post's `.github/renovate.json5` excerpt)

```
{
  // Dependency cooldown: skip versions published less than 5 days ago
  "matchUpdateTypes": ["major", "minor", "patch"],
  "minimumReleaseAge": "5 days"
},
{
  "matchPackageNames": [
    "actions/{/,}**",                  // GitHub's official actions
    "docker/{/,}**",                   // Official Docker actions
    "cilium/{/,}**",                   // Our own ecosystem
    "k8s.io/{/,}**",                   // Kubernetes official
    "sigs.k8s.io/{/,}**",              // Kubernetes SIGs
    "golang.org/x/{/,}**",             // Go experimental
    "github.com/golang/{/,}**",        // Go official org
    "github.com/prometheus/{/,}**",
    "github.com/hashicorp/{/,}**",
    "go.etcd.io/etcd/{/,}**",
    // ...trimmed
  ],
  "automerge": true,
  "automergeType": "pr",
  "groupName": "auto-merge-trusted-deps",
  "reviewers": ["ciliumbot"]
}
```

### Auto-approve bot-identity check (verbatim from the post's excerpt of Cilium's auto-approve workflow)

```
if: ${{
  github.event.pull_request.user.login == 'cilium-renovate[bot]' &&
  (github.triggering_actor == 'cilium-renovate[bot]' ||
  github.triggering_actor == 'auto-committer[bot]')
  }}
```

### Fork-vs-pin cost bullets (verbatim, condensed from "Would forking actions into our own org be even safer?")

```
- Maintenance burden. We use dozens of third-party actions. Keeping forks in
  sync with upstream security patches becomes a part-time job, and a stale
  fork with unpatched vulnerabilities is itself a security problem.
- Missed improvements. Upstream actions regularly fix bugs and ship security
  features. Forks add friction to picking those up.
- Renovate complexity. Our update pipeline would have to track upstream
  releases, open PRs against each fork, and then update the consuming
  workflows. The chain doubles in length.
```

### Expression-injection fix (condensed from the post's prose; the env-var indirection pattern)

```
# The fix pattern described in the post:
# 1. Assign the untrusted ${{ }} value to an env var at the step level.
# 2. Reference it in the run: block as a quoted shell variable ("$MY_VAR"),
#    so bash treats it as a single variable regardless of contents.
```

## Cross-References

- **Corroborates**:
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 3**
    (root cause — an unpinned Trivy security-scanner dependency ran in CI
    with environment access and exfiltrated release credentials) — this
    post's opening framing (Claim 1: "A pinned workflow that fetches a
    compromised dependency is still a compromised workflow") is exactly the
    general principle that incident instantiates: one unpinned dependency
    defeated an otherwise-functional pipeline. The incident is the evidence;
    this post is the mature-project rule derived from that class of evidence.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 14**
    (remediation — "pin to verified SHAs, add an upgrade cooldown period,
    and add zizmor") — this post supplies the concrete *implementation* of
    the cooldown half that Claim 14 names but does not specify: the Renovate
    `minimumReleaseAge: "5 days"` key with the detection-window rationale
    (this note's Claim 5). The incident note's cooldown is the rule; this
    post's config is the mechanism. Also corroborates the pinned-SHA half
    (this note's Claim 2) and the automated-scanning half (this note's
    Claim 11, static analysis as the unpinned-dep/policy-enforcement guard —
    Cilium uses CodeQL+actionlint where LiteLLM adopted zizmor; same class,
    different toolchain).
  - `docs-promptfoo-code-scan-github-action.md` **Claim 8** ("Tags such as
    `v0` are convenient but mutable; a commit SHA is the only immutable
    reference") — same full-SHA pinning convention, independently adopted by
    a second project. This post extends it with `@sha256` digest pinning for
    in-workflow container images and the explicit transitive-pin blind spot
    (Claims 2, 3), which the promptfoo note does not cover.
  - `blog-cncf-securing-cicd-credentials-verification.md` **Claim 3**
    (minimal-default `GITHUB_TOKEN` permissions with explicit opt-in) —
    this post's Claim 11 enforcement layer (CodeQL
    `actions/missing-workflow-permissions` failing modified workflows that
    lack `permissions:`) is the static-analysis backstop for the convention
    that note describes as policy. Same series, same project; different
    enforcement mechanism for the same rule.
- **Contradicts**: None. No existing source note claims that mutable tags,
  unpinned dependencies, unpinned runners, or un-scoped automerge are safe,
  and none opposes release-age cooldowns or identity-checked auto-approval.
  One near-miss checked and rejected as a contradiction:
  `blog-cncf-securing-cicd-credentials-verification.md` **Claim 9** calls
  reliance on Renovate's `vulnerabilityAlerts` "reactive" (a named gap),
  while this post lists `vulnerabilityAlerts` as a control — but this post
  does not claim it is *sufficient*; it sits alongside the cooldown and the
  allowlist boundary, which are the pre-advisory controls that note's gap
  analysis implies. Complementary layers in one architecture, not opposing
  claims. No contradiction issue filed.
- **Extends**:
  - `blog-cncf-securing-cicd-credentials-verification.md` — same series,
    part 3 (credentials/signing layer; already extracted as issue #1676).
    This note is the dependency-intake counterpart: part 3 answers "who can
    touch the credentials that sign and ship"; this note answers "what code
    is allowed to enter the build at all." Per the series architecture:
    part 2 controls intake, part 3 controls output. Overlapping material
    deliberately not re-extracted here — the 68 internal `@main` refs and
    the GitHub 2026 roadmap `dependencies:` lock item appear in both posts
    and are covered once, in the part 3 note's Claims 10 and 14; this note
    cites them (Claim 3) rather than duplicating them as new findings.
  - `failure-litellm-supply-chain-compromise-march-2026.md` **Lesson 4**
    (impact scoping — pinned installs safe, unpinned pip installs including
    transitive deps via AI agent frameworks/MCP servers were the exposed
    population) — vendoring with drift checks (this note's Claim 8) is the
    stronger sibling control on the same axis: where Lesson 4 says pinning
    determined who was safe, this post shows a project that removed the
    build-time dependency-resolution step from the trust path entirely.
    The Go-vs-Python conditioning (Go import paths kill dependency
    confusion; Python/npm remain exposed) is a caveat the guide must carry
    when transferring this to LLM-infra package management (Claim 9).
  - `docs-litellm-data-security.md` — its supply-chain scanning posture
    (grype image scanning in CI) is the scanning-layer cousin of this post's
    static-analysis enforcement (Claim 11); noted as thematic adjacency
    only, not cited by claim number for this extraction.
- **Novel**: First source note in the corpus covering:
  1. The **composition statement** for pinning controls — action pinning and
     dependency pinning are one threat model, not two (Claim 1).
  2. The **transitive action-dependency blind spot**: a SHA pin does not
     cover nested actions resolved by tag at runtime, and GitHub's
     workflow-level `dependencies:` lock is the announced (emerging) fix
     (Claim 3).
  3. **`minimumReleaseAge` release-age cooldown** as the concrete Renovate
     implementation of the cooldown remedy the corpus currently carries only
     as a named rule from the LiteLLM remediation list (Claim 5).
  4. **Renovate as a trust boundary**: trusted-publisher allowlist auto-merge
     vs human review for everything else — the corpus's first concrete
     "where does the human boundary sit in automated updates" implementation
     (Claim 6).
  5. **`github.triggering_actor` verification** as a bot-impersonation
     control on automated merge paths (Claim 7).
  6. **Vendoring as trust relocation** — build-time invisibility to
     review-time visibility — with the honest reviewer-attention limitation
     and CODEOWNERS backstop (Claims 8, 9).
  7. **Fork-vs-pin escalation criteria** as a calibrated rule rather than an
     absolutist one (Claim 10).
  8. **GitHub Actions expression injection** as a named vulnerability class
     with the env-var indirection fix — a live exposure class for any repo
     running LLM-agent CI (Claim 12).
  9. **`ubuntu-latest` (floating runner image)** named as a mutable-ref
     anti-pattern of the same class as unpinned action tags (Claim 11).

## Guide Impact

- **Chapter 06 (Security and Trust)**, "Pin everything; verify releases"
  (`guide/06-security-and-trust.md:636`): Add the composition statement as
  the framing sentence — pinning actions and pinning packages are one threat
  model ("A pinned workflow that fetches a compromised dependency is still a
  compromised workflow", cite Claim 1). Add full-SHA `uses:` pinning plus
  `@sha256` digest pinning of in-workflow container images (cite Claim 2),
  and add the explicit caveat that transitive action dependencies resolve at
  runtime and are *not* covered by direct pinning until GitHub's
  `dependencies:` lock ships (cite Claim 3, mark the lock `emerging`).
  Extend the section's remediation list with the release-age cooldown
  mechanism: the guide currently names "pinned-SHA + cooldown + automated
  scanning" at `guide/06-security-and-trust.md:712` citing the LiteLLM
  incident's Claim 14, but gives no implementation — add Renovate
  `minimumReleaseAge: "5 days"` with the detection-window rationale (cite
  Claim 5).
- **Chapter 06**, "Three CI/CD anti-patterns" section
  (`guide/06-security-and-trust.md:691`): The remediation paragraph names
  isolated environments, ephemeral credentials, and pinned-SHA + cooldown +
  scanning. Add the trust-boundary auto-merge pattern as the fourth
  remediation component: trusted-publisher allowlist auto-merges after CI,
  everything else requires human review, and the auto-approve path verifies
  both PR author and `github.triggering_actor` (cite Claims 6, 7) —
  directly relevant to any repo (including this corpus's own workflows) that
  runs automated merge or auto-approve paths.
- **Chapter 06**, anti-pattern list extension: Add **GitHub Actions
  expression injection** as a named anti-pattern with the env-var indirection
  fix (cite Claim 12). This is currently absent from the guide and is a
  concrete, non-obvious vulnerability class for LLM-agent CI repos, where
  issue titles, branch names, and agent output routinely flow into workflow
  `run:` blocks. Pair with the static-analysis enforcement note (CodeQL
  `actions/missing-workflow-permissions`, actionlint; no floating
  `ubuntu-latest`) as the architecture-over-policy backstop (cite Claim 11).
- **Chapter 06**, fork-vs-pin guidance: Add the calibrated escalation rule —
  SHA pinning is the default; forking is justified only when a major provider
  is repeatedly compromised, because stale forks carry their own unpatched-
  vulnerability risk (cite Claim 10). Optionally carry the Go proverb
  framing ("A little copying is better than a little dependency") and
  deliberate tree-shrinking as the package-layer analogue.
- **Chapter 05 (LLM Ops Reliability)**, "CI/CD supply-chain isolation"
  (`guide/05-llm-ops-reliability.md:1359`): The section currently cites only
  LiteLLM's CI/CD v2 goals. Add vendoring / lockfile-with-drift-check as the
  dependency-intake half of stage isolation: committed dependency trees that
  CI verifies for drift remove build-time dependency resolution from the
  trust path — transferable to Python (hash-locked wheels) and npm lockfiles
  (cite Claim 8), with the Go-vs-Python dependency-confusion caveat (cite
  Claim 9).

## Extraction Notes

- Source read in full: the CNCF Member Post page (published 2026-06-12,
  ~16 KB of extractable body text). No sub-pages were followed beyond what
  was needed for attribution: Part 1 and Part 3 of the series are linked but
  not extracted (Part 3 is already in the corpus; Part 1's access-control
  material is out of this note's triaged scope), and the linked
  cilium/cilium config files, Renovate PR, GitHub roadmap post, and
  third-party research pages are referenced by the source but not fetched.
  All quoted passages were copied character-for-character from the fetched
  page text; markdown emphasis markers were treated as formatting noise and
  omitted from quotes per MINER.md §2a.
- `date_published` set to 2026-06-12 (page dateline). `date_extracted` and
  `last_checked` set to 2026-10-19 UTC.
- `confidence_overall` set to `emerging`: the post is a first-party self-report
  of the project's own configuration, consistent with the series sibling
  note's posture. Specific claims are concrete and checkable (configs shown
  verbatim, linked to public repo files), but they are not independently
  verified; one claim component (GitHub's workflow-level `dependencies:`
  lock, Claim 3) is explicitly forward-looking platform roadmap. The
  operational-efficacy claims ("held up well so far", the cooldown's
  detection-window rationale) are reasoned heuristics, not measured data.
- The `miner-related-notes.md` candidates list was read per MINER.md §4. Of
  the 10 listed candidates, one is cited and nine are explicitly dismissed as
  non-overlapping:
  - `blog-cncf-securing-cicd-credentials-verification.md` — **cited**
    (Extends; Corroborates via Claim 3). Same series, part 3; already in the
    corpus as issue #1676. Claims re-read and verified per §4b.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SRE
    SLOs; unrelated to CI/CD dependency hardening. Dismissed.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — agent
    platform security on Kubernetes (mTLS, policy-as-code); no CI/CD
    dependency-intake content. Dismissed.
  - `docs-google-sre-reliable-product-launches.md` — launch coordination
    process; no supply-chain dependency content. Dismissed.
  - `docs-google-sre-slo-engineering-case-studies.md` — SLO case studies;
    unrelated. Dismissed.
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — sociotechnical
    complexity; unrelated. Dismissed.
  - `docs-google-sre-eliminating-toil.md` — toil taxonomy; unrelated.
    Dismissed.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative
    vs declarative change workflows; no supply-chain content. Dismissed.
  - `docs-google-sre-on-call.md` — on-call pager load; unrelated. Dismissed.
  - `docs-google-sre-prodcast-03-01.md` — SRE influence methodology;
    unrelated. Dismissed.
  The remaining useful cross-references (the two LiteLLM supply-chain notes,
  the promptfoo code-scan note) were identified via the Prospector triage
  and `source-notes/` search; each cited claim was re-read and verified per
  §4b before citation.
- Per the triage's "What this is NOT": Cilium-specific release-process detail
  was not extracted; the no-AI/LLM-content caveat was followed (transferable
  practice only); the GitHub `dependencies:` lock and roadmap items are
  marked `emerging`, not available capability. Overlapping material with the
  part 3 note (68 internal `@main` refs, roadmap items) is cited to the part
  3 note rather than re-extracted.
- No contradiction issue filed: verified against the overlapping notes
  (part 3, both LiteLLM supply-chain notes, promptfoo code-scan). All
  overlapping sources agree with this one or are complementary layers of one
  architecture (see Cross-References → Contradicts for the Claim 9
  near-miss analysis). Checked `CONTRADICTIONS.md` context via the part 3
  note's own extraction notes; no existing `C-NNN` entry covers this
  territory.
