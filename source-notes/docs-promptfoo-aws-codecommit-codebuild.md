---
source_url: https://www.promptfoo.dev/docs/integrations/aws-codecommit
source_type: docs
title: "Promptfoo AWS CodeCommit Integration — CodeBuild Evals, the Hand-Rolled CodeCommit PR Comment, and a Custom Pass-Rate Gate That Cannot Fail"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-22
date_extracted: 2026-10-22
last_checked: 2026-10-22
status: current
confidence_overall: emerging
issue: "#1825"
---

# Promptfoo AWS CodeCommit Integration — CodeBuild Evals, the Hand-Rolled CodeCommit PR Comment, and a Custom Pass-Rate Gate That Cannot Fail

> The first non-GitHub CI platform in the corpus for a promptfoo eval/code-scan
> gate, and a negative case for the GitHub-native path: the vendor states
> outright that CodeCommit pull requests are not a first-class code-scan target,
> so the page prescribes a hand-rolled `get-pull-request` → `code-scans run` →
> `post-comment-for-pull-request` pipeline. Its two most reusable findings are
> (a) the vendor-prescribed custom pass-rate gate, which we reproduced going
> **green on an all-error run** because its denominator is zero and `bc` fails
> open, and (b) the gap in the supply-chain posture between the hardened
> GitHub Action (`promptfoo@<pinned>`, `--ignore-scripts`, provenance
> attestation) and the unpinned `npm install -g promptfoo` this page installs.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "AWS CodeCommit
  Integration" page, `/docs/integrations/aws-codecommit`)
- **Author credibility**: Promptfoo, the commercial LLM-security/eval vendor.
  First-party documentation of its own CI integration, so authoritative about
  the product's *documented* interface (buildspec shape, env-var names, IAM
  actions, CLI flags) but vendor-positioned and unvalidated as to outcomes.
  The page carries no original publication date; the site footer shows
  "Last updated on **Oct 22, 2026** by **dependabot\[bot\]**" — i.e. the
  content is machine-updated, not hand-authored prose.
- **Scope**: Covers (1) running `promptfoo eval` in AWS CodeBuild against a
  CodeCommit repo — secret injection, artifact persistence, cache reuse, and
  `--fail-on-error` as the gate; (2) a *custom pass-rate quality gate* built
  from `jq` + `bc` over the eval JSON; (3) running `promptfoo code-scans run`
  against CodeCommit pull requests and posting a summary comment back with the
  AWS CLI; (4) the least-privilege IAM policies; (5) a four-entry
  troubleshooting list. Does NOT cover the scanner's detection methodology
  (see `blog-promptfoo-building-security-scanner-llm-apps.md`, #292), the
  CLI flag/schema surface (see `docs-promptfoo-code-scan-cli.md`, #1264), the
  GitHub Action's trust model and SARIF publishing (see
  `docs-promptfoo-code-scan-github-action.md`, #1265), or the eval cache's
  semantics (see `docs-promptfoo-configuration-caching.md`).
- **Vendor caveat**: Everything here is a vendor recipe, not an
  independently-operated pipeline. The page documents *what a team can wire*;
  it does not document that anyone has run it, and — as Claim 4 shows — the
  headline quality-gate recipe is decorative in its most important failure
  mode. Treat the artifacts as checkable configuration and the recipes as
  unreviewed samples.

## Extracted Claims

### Claim 1: The vendor states that CodeCommit pull requests are not a first-class target for `promptfoo code-scans run`, so the hosted-Action path has to be re-implemented by hand
- **Evidence**: The opening paragraph of the "Run promptfoo code scans on
  CodeCommit pull requests" section, followed by the two-step workaround
  (pass PR context into CodeBuild → add a scan buildspec).
- **Confidence**: settled (vendor-stated product limitation)
- **Quote**: "Promptfoo's hosted GitHub Action posts inline review comments on GitHub pull requests, but CodeCommit pull requests are not a first-class target in `promptfoo code-scans run` today."
- **Quote**: "For CodeCommit, run the scanner in CodeBuild, save JSON output, and post a summary comment back to the pull request with the AWS CLI."
- **Our assessment**: Buy it — this is the vendor naming its own gap, which
  makes it citable rather than inferred. The operational shape matters for
  the guide: a security gate's reach is bounded by *which CI platforms the
  vendor supports*, and a team on CodeCommit inherits the whole integration
  cost. The corpus previously held only the GitHub-native realization
  (`docs-promptfoo-code-scan-github-action.md`), which reads as if the Action
  *is* the CI gate; this page is the counterexample. Note what the workaround
  does **not** carry over: the Action's fork-PR default-deny control (the
  GitHub-Action note's Claim 4) has no analogue here — the page documents no
  trust boundary for untrusted contributors at all, so on this path the
  untrusted-PR question is simply unanswered.

### Claim 2: The DIY path degrades to one general PR comment capped at 20 findings, and the page states why inline review is not used
- **Evidence**: The buildspec's jq renderer slices `.comments[:20]`; the prose
  after the buildspec names the cap and the reason.
- **Confidence**: settled (documented behavior)
- **Quote**: "This posts one general pull request comment with the scan summary and up to 20 findings. `PostCommentForPullRequest` also supports file-level locations, but promptfoo's scanner output is currently tuned for GitHub review semantics, so a summary comment is the simplest integration path for CodeCommit."
- **Our assessment**: Buy it, and treat the 20-finding slice as a *silent*
  truncation: findings 21+ never reach the reviewer, and nothing in the
  comment says so — the JSON artifact holds the full set, but the artifact is
  not what the reviewer reads. The vendor's stated reason ("tuned for GitHub
  review semantics") is the real lesson: a scanner's output shape is coupled
  to one platform's review API, so porting the *gate* to another platform
  means porting the *presentation* too, by hand. The guide's Ch06 currently
  describes the gate only in GitHub terms; the porting cost is the missing
  half.

### Claim 3: The vendor's own summary-comment renderer maps an empty `comments` array to "No findings" without checking `success` or `skipReason` — the skip-vs-clean footgun, instantiated by the vendor
- **Evidence**: The jq program in `buildspec-code-scan.yml` tests
  `(.comments | length) == 0` and emits "- No findings"; it never reads
  `.success` or `.skipReason`, both of which are documented fields of the
  scanner's JSON response.
- **Confidence**: settled (the artifact is directly checkable against the
  documented response schema)
- **Quote** (jq fragment, verbatim from the buildspec): `if (.comments | length) == 0 then` / `"- No findings"`
- **Our assessment**: Buy it, and this is the page's most reusable negative
  result. The corpus already documents the schema fact that a skipped scan
  and a clean scan both produce an empty `comments` array
  (`docs-promptfoo-code-scan-cli.md` Claim 9: "`skipReason` … `comments` will
  be empty"), and that an unguarded consumer therefore reads a skip as a clean
  result (`docs-promptfoo-code-scan-github-action.md` Claim 5, the
  conditional-SARIF-upload rule). This page adds the third instance, and it
  is the sharpest one: a **vendor-authored consumer** that violates the rule
  the vendor's other pages document. A team copying this buildspec gets a PR
  comment saying "No findings" for a scan that never ran. Note this is an
  *instance* of the documented footgun, not a contradiction of it — see the
  Cross-References section.

### Claim 4: The vendor-prescribed custom pass-rate gate goes **green** when the eval produced no graded results — reproduced, not inferred
- **Evidence**: The "Add a quality gate" snippet computes
  `successes / (successes + failures) * 100` with `jq`, prints it, and compares
  it to a hard-coded 95 with `bc -l` inside a bash arithmetic `(( ... ))`.
  We reproduced the snippet locally with jq 1.7 and bc 1.07 against
  `{"results":{"stats":{"successes":0,"failures":0,"errors":3}}}` (full
  transcript in Concrete Artifacts).
- **Confidence**: settled (we executed the vendor's snippet and observed the
  outcome; the mechanism is a documented property of `jq`, `bc`, and bash
  arithmetic rather than a guess about promptfoo's internals)
- **Quote**: "If you want a custom pass-rate threshold instead of `--fail-on-error`, write the JSON output and check the stats in a second command:"
- **Quote** (the gate line, verbatim): `PASS_RATE=$(jq '.results.stats.successes / (.results.stats.successes + .results.stats.failures) * 100' promptfoo-results.json)`
- **Our assessment**: Buy it hard — this is a direct, vendor-shipped instance
  of the corpus's "A gate that cannot fail is not a gate" rule
  (`guide/05-llm-ops-reliability.md:655`). The failure chain is: with zero
  successes and zero failures the denominator is zero, so `jq` **errors** (its
  own message, reproduced in Concrete Artifacts: `number (0) and number (0)
  cannot be divided because the divisor is zero`, exit 5) and writes nothing
  to stdout; `PASS_RATE` is therefore empty; `bc -l` is then handed `" < 95"`,
  prints `(standard_in) 1: syntax error` to stderr,
  outputs nothing, and **exits 0**; `$( )` is empty, so bash's `(( ))`
  evaluates to 0 and the `if` never fires; the script exits 0 and the build is
  green with the log line `Pass rate: %`. Two independent fail-opens stack
  here: `bc` reports a syntax error but returns success, and bash treats an
  empty arithmetic expansion as zero. (Versions of `jq` that emit `null`
  instead of erroring land in the same non-numeric path — `bc` cannot parse
  `null` either.) Two further notes for the guide: the vendor's own
  `PROMPTFOO_PASS_RATE_THRESHOLD` already implements a native pass-rate
  threshold (`docs-promptfoo-configuration-outputs.md` Claim 10) and this
  page does not use it; and the "Custom CI gating format" the vendor
  documents as the CI-gating format is JUnit XML, not raw JSON
  (same note, Claim 1) — the hand-rolled `jq` path exists because the
  artifact is JSON, not because the gate needed JSON.

### Claim 5: The gate's denominator counts only successes and failures — rows that are neither are invisible to it
- **Evidence**: The jq expression's two terms; no other field is consulted.
- **Confidence**: settled (directly readable from the snippet)
- **Quote**: `'.results.stats.successes / (.results.stats.successes + .results.stats.failures) * 100'`
- **Our assessment**: Buy it. promptfoo separates assertion failures from
  execution errors as a first-class distinction — "`failure` for failed
  assertions and `error` for provider/runtime errors so CI can distinguish
  incorrect behavior from execution problems"
  (`docs-promptfoo-configuration-outputs.md` Claim 3) — and this gate throws
  that distinction away: an error row contributes to neither numerator nor
  denominator. A run where every case errored (provider outage, bad API key,
  rate limit) is arithmetically identical to a run that graded nothing, which
  is precisely the zero-denominator case Claim 4 shows going green. Note also
  that `.results.stats` is documented only as an opaque stub — the Output
  Formats page's JSON structure shows `"results": { …, "stats": { … } }` with
  the sub-fields elided — so `successes` and `failures` are consumed by the
  vendor's own snippet without being documented by name.

### Claim 6: The custom-gate variant *replaces* the per-case gate rather than adding to it — `--fail-on-error` is dropped
- **Evidence**: The eval command in the "Add a quality gate" buildspec is
  `promptfoo eval -c promptfooconfig.yaml --share -o promptfoo-results.json`,
  with no `--fail-on-error`, whereas the first buildspec's eval command
  includes `--fail-on-error`.
- **Confidence**: settled (directly readable from the two artifacts)
- **Quote**: "If you want a custom pass-rate threshold instead of `--fail-on-error`, write the JSON output and check the stats in a second command:"
- **Our assessment**: Buy it, and read the word "instead" literally. The
  custom gate is a *substitution*, so the per-case assertion gate is gone: a
  suite with 100 cases and 5 failures sits at exactly 95% and passes, while
  the same suite under `--fail-on-error` fails on the first failing case. The
  page frames this as an alternative threshold mechanism ("If you want a
  custom pass-rate threshold"), which is accurate, but a team switching from
  the first buildspec to the second silently loosens the gate from failing
  the build on any assertion failure to passing up to 5% of cases — and, per
  Claim 4, to permitting every case to fail whenever nothing was graded at
  all. The two gates should be composed, not swapped.

### Claim 7: CodeBuild's native secret-injection mechanism is `env.parameter-store`, and the page attributes leaked secrets to using plain environment variables instead
- **Evidence**: The first buildspec's `env:` block maps an SSM parameter path
  to an environment variable; the troubleshooting entry "Secrets appear in
  logs" states the preference explicitly.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Prefer Parameter Store or Secrets Manager mappings in `buildspec.yml` instead of plain environment variables for provider API keys."
- **Our assessment**: Buy it, with one honest caveat. The benefit is
  real and matches the corpus's credential-handling pattern: the credential
  value never appears in the repository, and the *read* is governed by IAM
  rather than by possession of a build-time literal — the same
  design of scoping credentials so that a CI compromise cannot reach
  production
  the CNCF note documents as its primary control
  (`blog-cncf-securing-cicd-credentials-verification.md` Claim 1: two
  separately scoped credential sets behind distinct protected environments).
  The caveat: a `parameter-store` mapping still materializes the value as an
  environment variable for **every command in the build**, so Parameter Store
  is not a substitute for per-step credential scoping — the blast-radius
  boundary is the IAM policy, and the injection mechanism only keeps the
  secret out of the repo and out of the buildspec. The page does not mention
  this limit; it presents the mapping as the fix for a log-leak symptom.

### Claim 8: Least-privilege IAM is two additive statements — `ssm:GetParameters` on a `parameter/promptfoo/*` prefix for eval builds, and two CodeCommit actions scoped to a single repository ARN for PR comments
- **Evidence**: The two JSON policy blocks in the "IAM permissions" section,
  introduced by the prose below.
- **Confidence**: settled (directly checkable policy documents)
- **Quote**: "The CodeBuild service role needs access to your repository, your secret store, and any CodeCommit pull request APIs you use."
- **Quote**: "For pull request scan comments, add CodeCommit permissions:"
- **Our assessment**: Buy it. The scoping is genuinely tight: the
  CodeCommit actions are pinned to one `arn:aws:codecommit:REGION:ACCOUNT_ID:REPOSITORY_NAME`,
  so a compromised CodeBuild role can comment on one repository and not
  read or comment on another. The `parameter/promptfoo/*` prefix is a
  *namespace convention*, not a narrow resource — it grants read on every
  parameter under that prefix, so the prefix is the real boundary and a
  convention like `/promptfoo/<repo>/<secret>` is what makes it meaningful.
  Two gaps to flag for the guide: (i) the page's prose says the role "needs
  access to your repository" but **neither sample policy grants repository
  read** — the clone permission must come from somewhere else (e.g. the AWS
  managed CodeBuild service-role policy), so a team assembling the policy
  from the samples alone gets a build that cannot clone; and (ii) the
  eval-only policy is a complete standalone document, so an eval build that
  also wants the scan path needs the second block *added*, not swapped.

### Claim 9: `code-scans run` needs a Promptfoo API key on every non-GitHub-Action path — there is no keyless option here
- **Evidence**: The buildspec's `parameter-store` mapping for
  `PROMPTFOO_API_KEY`, the Prerequisites list, and the first troubleshooting
  entry.
- **Confidence**: settled (documented product behavior)
- **Quote**: "`promptfoo code-scans run` requires a Promptfoo API key outside of the GitHub Action flow. Store `PROMPTFOO_API_KEY` in Parameter Store or Secrets Manager and expose it to CodeBuild."
- **Quote**: "A Promptfoo API key if you want to run `promptfoo code-scans run`"
- **Our assessment**: Buy it. It corroborates the CLI note's auth-precedence
  chain (`docs-promptfoo-code-scan-cli.md` Claim 7: `--api-key` →
  `PROMPTFOO_API_KEY` → `promptfoo auth login` → GitHub OIDC "when used in the
  Promptfoo GitHub Action") from the platform side: OIDC is an
  Action-only affordance, so the *CI platform* determines the credential's
  trust model. On GitHub the scanner can run keyless via the GitHub App path
  (`docs-promptfoo-code-scan-github-action.md` Claim 6); on CodeBuild the
  team is left with a long-lived API key it must store, rotate, and scope
  itself. That is a credential-hygiene delta the guide should name when it
  recommends CI-gated scanning.

### Claim 10: Both `--base` and `--compare` must be overridden, and the destination branch must be fetched first — the CLI's defaults are wrong for every CodeCommit PR
- **Evidence**: The buildspec's `git fetch origin "${DESTINATION_BRANCH}:${DESTINATION_BRANCH}"`
  followed by `--base "$DESTINATION_BRANCH"` and
  `--compare "$CODEBUILD_RESOLVED_SOURCE_VERSION"`; the "Pass pull request
  context" section's env-var semantics; and the second troubleshooting entry.
- **Confidence**: settled (documented behavior)
- **Quote**: "CodeBuild exposes source metadata in environment variables including `CODEBUILD_SOURCE_REPO_URL`, `CODEBUILD_SOURCE_VERSION`, and `CODEBUILD_RESOLVED_SOURCE_VERSION`. For CodeCommit sources, `CODEBUILD_SOURCE_VERSION` is the commit ID or branch name and `CODEBUILD_RESOLVED_SOURCE_VERSION` is the commit ID after `DOWNLOAD_SOURCE`."
- **Quote**: "Fetch the destination branch before running `promptfoo code-scans run`, then pass `--base` explicitly. For CodeCommit pull requests, you can read the destination branch from `aws codecommit get-pull-request`."
- **Our assessment**: Buy it. The CLI's documented default for `--base` is
  "Auto-detects either main or master" and the default for `--compare` is
  `HEAD`
  (`docs-promptfoo-code-scan-cli.md` Claim 4) — neither is usable here: a
  CodeBuild checkout is not a local branch, and `HEAD` in a detached CI
  checkout is not the PR head. The page's pairing of the two flags with two
  *different* ref kinds is the subtle part: `--base` receives a **branch
  name** (which must exist locally, hence the `git fetch`) while `--compare`
  receives a **commit SHA** (`CODEBUILD_RESOLVED_SOURCE_VERSION`). The
  troubleshooting entry is the useful symptom-to-cause map: "the scan
  compares against the wrong branch" is not a scanner bug but a missing
  fetch plus an unset `--base`. Worth adding to Ch06's diff-scoped-scanner
  paragraph, which currently describes only the CLI defaults.

### Claim 11: The eval cache is deliberately placed *and* persisted across builds — so a green build can be entirely memoised from an earlier build's provider responses
- **Evidence**: The first buildspec's `env.variables.PROMPTFOO_CACHE_PATH:
  .promptfoo/cache` plus the `cache.paths` block, and the "What this does"
  bullet.
- **Confidence**: settled (documented product behavior; the cache contract
  itself is established in `docs-promptfoo-configuration-caching.md`)
- **Quote**: "Caches promptfoo responses between builds"
- **Our assessment**: Buy it, and read the cross-build consequence carefully.
  This is the vendor's own CI recommendation — an explicit
  `PROMPTFOO_CACHE_PATH` rather than the `~/.promptfoo/cache` default
  (`docs-promptfoo-configuration-caching.md` Claim 9), which is the same
  guidance that note records for test-framework users (its Claim 10). What
  CodeBuild's `cache.paths` adds over a local runner is **cross-build
  persistence**: the cache outlives the build, so a build can pass on
  responses recorded weeks earlier, within the documented 14-day TTL, where a
  provider may have silently changed (that note's Claim 4). Because errors
  and empty responses are never cached (that note's Claim 5), the failure
  asymmetry inverts here: the successful majority is free and the failing
  tail re-hits the provider on every build. The buildspec sets neither
  `PROMPTFOO_CACHE_ENABLED=false` nor `--no-cache`, so a team adopting it
  unchanged gets a gate whose greenness is a function of an ambient cache.

### Claim 12: The build artifacts *are* the report surface — and the JSON file the gate parses is also the only machine-readable record of the run
- **Evidence**: The `artifacts:` blocks in both buildspecs and the "What this
  does" bullet list.
- **Confidence**: settled (directly checkable configuration)
- **Quote**: "Saves JSON and HTML reports as build artifacts"
- **Quote**: "Fails the CodeBuild build if any assertions fail"
- **Our assessment**: Buy it, and connect it to the corpus's
  report-artifact-as-observability-surface material. Three properties are
  worth naming for the guide: (a) the HTML report is a *human* artifact with
  no retention policy stated anywhere on the page — CodeBuild's default
  artifact retention applies, and the page never mentions it; (b) the JSON
  file is simultaneously the gate's input, the audit trail, and the only
  machine-readable record — the gate's input is also its audit trail, so a
  corrupted or truncated artifact is both a wrong verdict and no evidence; (c) the eval command includes `--share`, which uploads the eval
  snapshot to Promptfoo Cloud — an egress decision that the page presents as
  a default and that the vendor's own sharing docs warn about
  (`docs-promptfoo-configuration-outputs.md` Claim 6: "Do not put secrets in
  prompts, datasets, provider config fields, metadata, or other shareable
  inputs").

### Claim 13: The non-Action CI path installs the scanner **unpinned**, with npm lifecycle scripts enabled, and installs `jq` unpinned at build time — the supply-chain posture is the opposite of the hardened GitHub Action
- **Evidence**: The install phase of both buildspecs.
- **Confidence**: settled (directly readable configuration; the contrast is
  with the Action's documented install, quoted below)
- **Quote**: "A [CodeBuild Ubuntu image that supports Node.js 24](https://docs.aws.amazon.com/codebuild/latest/userguide/available-runtimes.html): Ubuntu 22.04 standard 7.0 or Ubuntu 24.04 standard 8.0"
- **Our assessment**: Buy it — and it is the most consequential claim for
  Ch06, because it is the same product and the same CLI installed two
  different ways. The GitHub Action installs "an exact, release-pinned
  version of the `promptfoo` CLI with npm lifecycle scripts disabled
  (`--ignore-scripts`)" and publishes "a signed build-provenance attestation
  for the exact artifact bytes"
  (`docs-promptfoo-code-scan-github-action.md` Claim 2, with the hardening
  scoped to post-v0.1.8 releases per its Claim 3). This page installs
  `npm install -g promptfoo` — floating `latest`, lifecycle scripts enabled,
  no attestation — and installs `jq` from apt at build time with no version
  constraint. The guide's rule is explicit that this is an exposure:
  "Pin all LLM infrastructure dependencies to verified versions"
  (`guide/06-security-and-trust.md:636`) and "Pin every CI dependency to
  verified SHAs — including security scanners" (`guide/06-security-and-trust.md:726`).
  A team that copies the vendor's AWS recipe verbatim is shipping a
  security scanner whose install is unpinned, in a pipeline whose whole
  purpose is to gate on security findings. The one thing this path *does*
  pin is the runtime (`runtime-versions: nodejs: 24`, plus the documented
  Ubuntu image floor), which is a useful nuance: the platform pins the
  runtime and floats the application. Note this is a **gap in the vendor's
  own guidance**, not a contradiction between two corpus claims — see the
  Cross-References section for why no contradiction issue was filed.

## Concrete Artifacts

### Eval buildspec (verbatim from "Run promptfoo eval in CodeBuild")

```yaml title="buildspec.yml"
version: 0.2

env:
  parameter-store:
    OPENAI_API_KEY: /promptfoo/openai-api-key
  variables:
    PROMPTFOO_CACHE_PATH: .promptfoo/cache

phases:
  install:
    runtime-versions:
      nodejs: 24
    commands:
      - npm install -g promptfoo
  build:
    commands:
      - |
        promptfoo eval \
          -c promptfooconfig.yaml \
          --share \
          --fail-on-error \
          -o promptfoo-results.json \
          -o promptfoo-report.html

artifacts:
  files:
    - promptfoo-results.json
    - promptfoo-report.html

cache:
  paths:
    - '.promptfoo/cache/**/*'
```
Source: promptfoo docs, "Run promptfoo eval in CodeBuild" section. Verbatim.

Vendor's own summary of what it does (verbatim bullets):

```
- Loads `OPENAI_API_KEY` from Parameter Store
- Runs the eval suite defined in `promptfooconfig.yaml`
- Fails the CodeBuild build if any assertions fail
- Saves JSON and HTML reports as build artifacts
- Caches promptfoo responses between builds
```

### Custom quality gate (verbatim from "Add a quality gate")

```yaml
phases:
  install:
    runtime-versions:
      nodejs: 24
    commands:
      - npm install -g promptfoo
  build:
    commands:
      - promptfoo eval -c promptfooconfig.yaml --share -o promptfoo-results.json
      - |
        PASS_RATE=$(jq '.results.stats.successes / (.results.stats.successes + .results.stats.failures) * 100' promptfoo-results.json)
        echo "Pass rate: ${PASS_RATE}%"
        if (( $(echo "${PASS_RATE} < 95" | bc -l) )); then
          echo "Quality gate failed: ${PASS_RATE}% < 95%"
          exit 1
        fi
```
Source: promptfoo docs, "Add a quality gate" section. Verbatim. Note: this
fragment omits the `artifacts:` and `cache:` blocks of the full buildspec
above, and drops `--fail-on-error` from the eval command.

### Our reproduction of the gate's zero-denominator path (NOT a source quote)

Environment: `jq-1.7`, `bc 1.07.1`, bash (default, no `set -e`), GNU/Linux.

```bash
$ printf '%s' '{"results":{"stats":{"successes":0,"failures":0,"errors":3}}}' > r.json

$ jq -n '0/(0+0)'
jq: error (at <unknown>): number (0) and number (0) cannot be divided because the divisor is zero
$ echo $?
5

$ PASS_RATE=$(jq '.results.stats.successes / (.results.stats.successes + .results.stats.failures) * 100' r.json)
jq: error (at r.json:0): number (0) and number (0) cannot be divided because the divisor is zero
$ echo "PASS_RATE=[$PASS_RATE]"
PASS_RATE=[]

$ echo " < 95" | bc -l
(standard_in) 1: syntax error
$ echo $?
0

$ if (( $(echo "" | bc -l) )); then echo FIRED; else echo "DID NOT FIRE"; fi
DID NOT FIRE
```

Running the vendor's block verbatim against that file:

```console
$ bash gate.sh
jq: error (at r.json:0): number (0) and number (0) cannot be divided because the divisor is zero
Pass rate: %
(standard_in) 1: syntax error
(standard_in) 1: syntax error
$ echo $?
0
```
Observation: the gate prints a malformed pass rate, `bc` reports a syntax
error on stderr while exiting 0, the `if` never fires, and the script exits
**0** — a green build for a run that graded nothing. (Caveat recorded in the
claim: a CodeBuild phase may abort on a failed command depending on the
shell's error handling; the snippet itself does not check the `jq` exit
status, so under default bash semantics the block exits 0.)

### PR-scan buildspec (verbatim from "2. Add a pull request scan buildspec")

```yaml title="buildspec-code-scan.yml"
version: 0.2

env:
  parameter-store:
    PROMPTFOO_API_KEY: /promptfoo/api-key

phases:
  install:
    runtime-versions:
      nodejs: 24
    commands:
      - npm install -g promptfoo
      - apt-get update && apt-get install -y jq
  build:
    commands:
      - |
        if [ -z "$CODECOMMIT_PULL_REQUEST_ID" ]; then
          echo "CODECOMMIT_PULL_REQUEST_ID is required for pull request scans"
          exit 1
        fi

        PR_JSON=$(aws codecommit get-pull-request \
          --pull-request-id "$CODECOMMIT_PULL_REQUEST_ID")

        REPOSITORY_NAME=$(echo "$PR_JSON" | jq -r '.pullRequest.pullRequestTargets[0].repositoryName')
        DESTINATION_REF=$(echo "$PR_JSON" | jq -r '.pullRequest.pullRequestTargets[0].destinationReference')
        SOURCE_COMMIT=$(echo "$PR_JSON" | jq -r '.pullRequest.pullRequestTargets[0].sourceCommit')
        DESTINATION_COMMIT=$(echo "$PR_JSON" | jq -r '.pullRequest.pullRequestTargets[0].destinationCommit')
        DESTINATION_BRANCH="${DESTINATION_REF#refs/heads/}"

        git fetch origin "${DESTINATION_BRANCH}:${DESTINATION_BRANCH}"

        promptfoo code-scans run . \
          --base "$DESTINATION_BRANCH" \
          --compare "$CODEBUILD_RESOLVED_SOURCE_VERSION" \
          --json \
          > promptfoo-code-scan.json

        COMMENT_BODY=$(jq -r '
          def sev(c): if c.severity then "\(.severity | ascii_upcase): " else "" end;
          [
            "## Promptfoo Code Scan",
            "",
            (.review // "Scan complete."),
            "",
            "### Findings",
            (
              if (.comments | length) == 0 then
                "- No findings"
              else
                (.comments[:20] | map(
                  "- " + sev(.) +
                  (if .file then "`\(.file)\(if .line then ":\(.line)" else "" end)` - " else "" end) +
                  .finding
                ) | .[])
              end
            ),
            "",
            "[View code scanning docs](https://www.promptfoo.dev/docs/code-scanning/cli/)"
          ] | join("\n")
        ' promptfoo-code-scan.json)

        aws codecommit post-comment-for-pull-request \
          --pull-request-id "$CODECOMMIT_PULL_REQUEST_ID" \
          --repository-name "$REPOSITORY_NAME" \
          --before-commit-id "$DESTINATION_COMMIT" \
          --after-commit-id "$SOURCE_COMMIT" \
          --content "$COMMENT_BODY"

artifacts:
  files:
    - promptfoo-code-scan.json
```
Source: promptfoo docs, "2. Add a pull request scan buildspec" section.
Verbatim.

### IAM policies (verbatim from "IAM permissions")

Eval-only build:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ssm:GetParameters"],
      "Resource": "arn:aws:ssm:REGION:ACCOUNT_ID:parameter/promptfoo/*"
    }
  ]
}
```

PR scan comments (additive):

```json
{
  "Effect": "Allow",
  "Action": ["codecommit:GetPullRequest", "codecommit:PostCommentForPullRequest"],
  "Resource": "arn:aws:codecommit:REGION:ACCOUNT_ID:REPOSITORY_NAME"
}
```

### Troubleshooting entries (verbatim headings + bodies)

```
### `promptfoo code-scans run` fails with an auth error

`promptfoo code-scans run` requires a Promptfoo API key outside of the GitHub Action flow. Store `PROMPTFOO_API_KEY` in Parameter Store or Secrets Manager and expose it to CodeBuild.

### The scan compares against the wrong branch

Fetch the destination branch before running `promptfoo code-scans run`, then pass `--base` explicitly. For CodeCommit pull requests, you can read the destination branch from `aws codecommit get-pull-request`.

### No pull request comment appears

Confirm `CODECOMMIT_PULL_REQUEST_ID` is present in the build environment, and verify the CodeBuild service role can call `codecommit:GetPullRequest` and `codecommit:PostCommentForPullRequest`.

### Secrets appear in logs

Prefer Parameter Store or Secrets Manager mappings in `buildspec.yml` instead of plain environment variables for provider API keys.
```

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-code-scan-cli.md` **Claim 7** (auth precedence:
    `--api-key` → `PROMPTFOO_API_KEY` → `promptfoo auth login` → GitHub OIDC,
    whose entry the note records as applying only inside the Promptfoo
    GitHub Action) — this page's troubleshooting
    entry ("requires a Promptfoo API key outside of the GitHub Action flow",
    Claim 9) is the platform-side statement of the same chain: OIDC is an
    Action-only affordance.
  - `docs-promptfoo-code-scan-cli.md` **Claim 4** (`--base` "Auto-detects
    either main or master", `--compare` default `HEAD`) — this page's
    explicit `--base "$DESTINATION_BRANCH"` /
    `--compare "$CODEBUILD_RESOLVED_SOURCE_VERSION"` (Claim 10) is the
    non-interactive proof that neither default holds in a CI checkout.
  - `docs-promptfoo-configuration-outputs.md` **Claim 3** ("`failure` for
    failed assertions and `error` for provider/runtime errors so CI can
    distinguish incorrect behavior from execution problems") — this page's
    custom gate counts only successes and failures (Claim 5), i.e. it
    discards exactly the distinction the vendor documents elsewhere as the
    reason CI needs the split.
  - `docs-promptfoo-configuration-outputs.md` **Claim 10** (CI gating is
    exit-code based, with `PROMPTFOO_PASS_RATE_THRESHOLD` as the native
    aggregate pass-rate threshold and `PROMPTFOO_FAILED_TEST_EXIT_CODE` as
    an overridable failure code) — the native mechanism this page's custom
    `jq`/`bc` gate re-implements by hand (Claims 4, 6).
  - `docs-promptfoo-configuration-caching.md` **Claim 9** (`PROMPTFOO_CACHE_PATH`
    default `~/.promptfoo/cache`) and **Claim 10** (the vendor's own CI
    guidance to set `PROMPTFOO_CACHE_TYPE=disk` with an explicit
    `PROMPTFOO_CACHE_PATH`) — this page's buildspec sets
    `PROMPTFOO_CACHE_PATH: .promptfoo/cache` (Claim 11), the same
    deliberate-placement decision, now with cross-build persistence.
  - `blog-cncf-securing-cicd-credentials-verification.md` **Claim 1** (two
    separately scoped registry credential sets behind distinct protected
    GitHub environments, so a CI compromise "cannot push to production
    image tags") — the AWS-native realization of that principle: Parameter
    Store injection plus an IAM policy whose `codecommit:*` Resource is a
    single repository ARN and whose `ssm:GetParameters` Resource is a
    `parameter/promptfoo/*` prefix (Claims 7, 8). The corpus's CNCF case is
    GitHub-environments; this is IAM-ARN scoping.
  - `failure-litellm-supply-chain-incident-march-2026.md` **Claim 14**
    ("Avoid compromised packages — pin to verified SHAs, add an upgrade
    cooldown period, and add zizmor to catch unpinned deps and credential
    leakage") — the rule this page's `npm install -g promptfoo` and
    `apt-get install -y jq` violate (Claim 13), inside the vendor's own
    recommended CI recipe.
- **Contradicts**: None identified, and no contradiction issue was filed.
  Two candidate conflicts were examined and rejected under MINER.md §4a:
  1. *The skip-vs-clean footgun (Claim 3).* The CLI note's Claim 9 states
     the schema fact (`skipReason` set → `comments` empty); this page's
     renderer ignores it. That is a consumer *violating* a documented
     distinction, not two source claims opposing each other — the guide
     advice is identical either way ("check `success`/`skipReason` before
     treating empty comments as a pass"). Recorded as a concrete instance
     for Ch06's existing rule, not as a contradiction.
  2. *The unpinned install (Claim 13).* The GitHub-Action note's Claims 2
     and 3 are scoped to *the Action's* installer; no note in the corpus
     claims the CLI's own install is pinned. The opposing position here is
     a guide rule (`guide/06-security-and-trust.md:636`, `:726`), not a
     corpus source claim, so it does not meet §4a's filing bar — it is
     carried as a Guide Impact recommendation instead. Also checked the
     open `contradiction`-labeled issues and `CONTRADICTIONS.md`: no
     existing entry covers CI-gate implementation or scanner-install pinning.
  Everything else in this note is either a new platform realization or a
  documented-behavior restatement of an existing claim.
- **Extends**:
  - `docs-promptfoo-code-scan-github-action.md` (**#1265**) — the sibling
    CI surface, and this page is its negative case. The Action posts inline
    review comments and publishes SARIF to GitHub Code Scanning; the
    CodeCommit path posts one summary comment capped at 20 findings and
    keeps the JSON as a build artifact (Claims 1, 2, 12). The Action's
    fork-PR default-deny (its Claim 4) and conditional SARIF upload (its
    Claim 5) have no counterpart in the vendor's own DIY buildspec, which
    renders an empty `comments` array as "No findings" (Claim 3).
  - `docs-promptfoo-code-scan-github-action.md` **Claim 2** (exact,
    release-pinned CLI install with `--ignore-scripts` plus a signed
    provenance attestation) and **Claim 3** (hardening scoped to post-v0.1.8
    releases) — this page's non-Action install (Claim 13) is the same
    product's CLI installed without either control, and the note's
    post-v0.1.8 boundary is the version the buildspec's floating
    `npm install -g promptfoo` cannot guarantee.
  - `docs-promptfoo-code-scan-cli.md` **Claim 9** (a skipped scan leaves
    `comments` empty, so "empty is ambiguous") — this page's jq renderer is
    the first corpus artifact that consumes that JSON without the
    `skipReason` check (Claim 3).
  - `docs-promptfoo-code-scan-cli.md` **Claim 2** (scans run against
    Promptfoo's hosted API, so code leaves the environment) — the AWS path
    keeps that property and adds `--share` on the eval side, uploading the
    eval snapshot to the vendor's cloud (Claim 12).
  - `docs-promptfoo-configuration-caching.md` **Claim 4** (14-day TTL,
    TTL-or-manual invalidation only) and **Claim 5** (errors and empty
    responses are never cached) — this page's CodeBuild `cache.paths`
    block turns those into a cross-build green-build hazard (Claim 11).
  - `docs-promptfoo-configuration-outputs.md` **Claim 1** (JUnit XML is the
    documented CI-gating format) — this page's gate parses raw JSON instead,
    which is what forces the hand-rolled arithmetic (Claim 4).
  - `docs-promptfoo-configuration-outputs.md` **Claim 6** (the "do not put
    secrets in shareable inputs" rule) — this page's buildspec uses
    `--share` unconditionally (Claim 12).
- **Novel**:
  1. **A vendor-stated, first-class CI-platform gap** for a security gate:
     "CodeCommit pull requests are not a first-class target in `promptfoo
     code-scans run` today" (Claim 1) — with the full hand-rolled
     replacement pipeline as a runnable artifact.
  2. **A reproduced, vendor-shipped decorative gate** — the custom
     pass-rate recipe goes green on a zero-denominator (all-error) run
     because `jq` errors, `bc` fails open with exit 0, and bash treats an
     empty arithmetic expansion as zero (Claim 4). First corpus instance of
     a *shell-implemented* gate that cannot fail.
  3. **The AWS-native CI realization of credential scoping** — Parameter
     Store injection plus `ssm:GetParameters` on a `parameter/promptfoo/*`
     prefix and `codecommit:GetPullRequest` /
     `codecommit:PostCommentForPullRequest` scoped to one repository ARN
     (Claims 7, 8). First CodeBuild/CodeCommit surface in the corpus.
  4. **The supply-chain posture delta inside one vendor's docs** — a
     hardened, pinned, attested Action install alongside an unpinned
     `npm install -g promptfoo` in the sibling integration page (Claim 13).
  5. **The CodeCommit PR-comment renderer** — a concrete, copyable
     `jq`→`aws codecommit post-comment-for-pull-request` integration with a
     hard 20-finding cap and no inline review (Claims 2, 3).
  6. **Cross-build eval-cache persistence** via CodeBuild `cache.paths`
     combined with an explicit `PROMPTFOO_CACHE_PATH` (Claim 11) — the
     eval cache as a *build-level* artifact rather than a runner-local one.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**, section "A gate that cannot fail is
  not a gate" (`guide/05-llm-ops-reliability.md:655`): this page supplies
  the CI-gate *instance* of the rule that section currently states only in
  terms of assertion config. **Recommendation**: add the vendor's own custom
  pass-rate gate as the worked counterexample for a gate implemented in shell
  over an eval artifact — the zero-denominator path (Claim 4) is a
  "cannot fail" gate that is invisible in the config, because the defect is
  in the *gate implementation*, not in a threshold default. The two rules
  the Smith should state together: (a) a gate must fail when its denominator
  is zero and when its input is missing or non-numeric (the vendor's snippet
  passes both), and (b) prefer the vendor's native
  `PROMPTFOO_PASS_RATE_THRESHOLD`
  (`docs-promptfoo-configuration-outputs.md` Claim 10) over hand-rolled
  arithmetic, and compose the aggregate gate with `--fail-on-error` rather
  than swapping one for the other (Claim 6). Also worth adding to the same
  section: a gate that consumes an artifact must treat "artifact missing or
  malformed" as a failure, and the corpus already knows error rows are a
  separate class from failures (same note, Claim 3) — the vendor's gate
  drops that class on the floor (Claim 5).
- **Chapter 06 (Security and Trust)**, section "Gating on LLM security scans"
  (`guide/06-security-and-trust.md:768`): the section currently describes
  the gate in GitHub terms only. **Recommendation**: (a) add the
  platform-contingent framing — the gate's reach is bounded by which CI
  platforms the vendor supports, and on CodeCommit the vendor's own recipe
  is a hand-rolled pipeline (Claim 1); (b) extend the existing rule "Gate on
  the scan's completion signal, never on its findings count" with this
  page's instance — a vendor-authored renderer that prints "- No findings"
  for a skipped scan because it tests `(.comments | length) == 0` and never
  reads `success`/`skipReason` (Claim 3), which is the third corpus
  instance of that footgun and the first one shipped as a copyable recipe;
  (c) add the CI-side base/compare requirements — in a CI checkout neither
  the CLI's `--base` auto-detection nor its `--compare HEAD` default is
  usable, and the destination branch must be fetched explicitly (Claim 10);
  (d) note the reviewer's-eye difference — the DIY path posts one summary
  comment capped at 20 findings with no inline file-level review, so the
  gate's *presentation* degrades with the platform (Claim 2).
- **Chapter 06**, section "Pin everything; verify releases"
  (`guide/06-security-and-trust.md:636`) and the rule at
  `guide/06-security-and-trust.md:726` ("Pin every CI dependency to verified
  SHAs — including security scanners"): **Recommendation**: extend the rule
  to the case where the *vendor's own documentation* recommends an unpinned
  install. Concretely: the GitHub Action installs a release-pinned
  `promptfoo` with `--ignore-scripts` and publishes a signed provenance
  attestation, while the sibling AWS integration page installs
  `npm install -g promptfoo` (floating `latest`, lifecycle scripts enabled)
  and `apt-get install -y jq` (Claim 13). A team on a non-GitHub CI platform
  must pin the version and add the `--ignore-scripts` hardening themselves;
  the guide should say so explicitly rather than let the vendor's recipe
  set the default. The page's one pinned element — `runtime-versions: nodejs: 24`
  with a documented Ubuntu image floor — is a useful illustration of the
  gap: the platform pins the runtime and floats the application.
- **Chapter 06**, supply-chain / credential-handling material: add the
  AWS-native instance of scoped CI credentials — Parameter Store or Secrets
  Manager mapping in the buildspec plus IAM policies whose `codecommit:*`
  Resource is a single repository ARN and whose `ssm:GetParameters` Resource
  is a `parameter/promptfoo/*` prefix (Claims 7, 8), corroborating the CNCF
  note's scoped-credentials principle in a second platform. Two caveats the
  Smith should carry: the parameter prefix, not the injection mechanism, is
  the real boundary (a `parameter-store` mapping still exposes the value to
  every command in the build), and neither sample IAM policy grants the
  repository-read permission the prose assumes — a team assembling the
  policy from the samples alone gets a build that cannot clone.
- **Chapter 02 (Observability)**, report-artifact material: this page makes
  the artifact boundary concrete for a CI-gated eval — the JSON and HTML
  reports are CodeBuild artifacts, and the JSON file the gate parses is
  simultaneously the gate's input, the audit trail, and the only
  machine-readable record of the run (Claim 12). **Recommendation**: state
  that a gate whose input artifact is also its evidence must therefore treat
  a missing, truncated, or malformed artifact as a failure, and note the
  `--share` egress the buildspec enables by default (same note, Claim 6 on
  the vendor's own secrets warning for shared inputs).
- **Chapter 05**, cache/reproducibility material (around
  `guide/05-llm-ops-reliability.md:570-608`): add the cross-build form of the
  caching hazard — CodeBuild's `cache.paths` persists the eval cache across
  builds, so a green build can be entirely replayed from responses recorded
  up to 14 days earlier, while errors are never cached and the failing tail
  re-hits the provider every run (Claim 11, extending
  `docs-promptfoo-configuration-caching.md` Claims 4, 5, 9, 10). The
  buildspec sets neither `PROMPTFOO_CACHE_ENABLED=false` nor `--no-cache`.
- **Chapter 03 (Runbooks and Agents)**: the scanner's JSON is consumed here
  by a hand-written renderer rather than a hosted bot, which is the same
  "agent-ready artifact" seam the corpus records for `aiAgentPrompt`
  (`docs-promptfoo-code-scan-cli.md` Claim 10) — on CodeCommit that
  machine-consumable field is dropped by the summary renderer, which prints
  only `finding`, `file`, `line`, and `severity`.

## Extraction Notes

- Source read in full: https://www.promptfoo.dev/docs/integrations/aws-codecommit
  (fetched as rendered markdown and cross-checked against the upstream
  Markdown source at
  `https://raw.githubusercontent.com/promptfoo/promptfoo/main/site/docs/integrations/aws-codecommit.md`
  so that the YAML blocks, the jq program, and the IAM JSON could be copied
  character-for-character rather than reconstructed from a lossy HTML
  render). Single self-contained page; its "See Also" links (CI/CD
  Integration, CLI Command, Sharing and Collaboration) point at surfaces
  already mined in this corpus — `docs-promptfoo-code-scan-cli.md` (#1264)
  for the CLI, `docs-promptfoo-configuration-outputs.md` for output formats
  and sharing — so no sub-page was followed, per the sibling notes'
  division of labour.
- The page carries no original publication date; the site footer shows
  "Last updated on **Oct 22, 2026** by **dependabot\[bot\]**", so
  `date_published` is recorded as the last-updated date and the
  machine-update provenance is noted here.
- Claim 4 is a **reproduction**, not a source claim: the vendor snippet was
  executed locally (jq 1.7, bc 1.07.1, bash without `set -e`) against a
  results file with `successes: 0, failures: 0`. The transcript is in
  Concrete Artifacts. The mechanism is version-sensitive in one place — jq
  versions that emit `null` instead of erroring on a zero divisor still
  produce a non-numeric `PASS_RATE` that `bc` cannot parse — but the
  fail-open outcome is the same. The claim is stated as a property of the
  *snippet*, and the page's own CodeBuild shell behaviour (whether a failed
  command aborts the phase) is flagged as an unknown we did not verify.
- The JSON field path `.results.stats.successes` / `.results.stats.failures`
  is consumed by the vendor's snippet but is not enumerated on the Output
  Formats page: that page's JSON structure shows `"results": { …, "stats": {
  … } }` with the `stats` sub-fields elided. The path's existence in the
  artifact was not independently verified against a real `promptfoo eval`
  run, so Claims 4 and 5 are stated about the snippet's arithmetic and its
  documented schema, not about a verified artifact shape.
- Cross-reference candidates file (`miner-related-notes.md`) read per
  MINER.md §4 before writing Cross-References. All 10 listed candidates were
  explicitly dismissed as non-overlapping: `docs-promptfoo-enterprise-findings-reports.md`
  (Enterprise finding disposition and the export/interop matrix),
  `docs-promptfoo-enterprise-guardrails.md` (runtime enforcement contract),
  `docs-litellm-batches-api.md` (LiteLLM batch rate limiting),
  `blog-pagerduty-sre-agent-triage.md` (AI incident triage),
  `docs-langfuse-mcp-server.md` (documentation MCP server),
  `docs-google-sre-reliable-product-launches.md` (launch-process checklists
  — thematic adjacency to gating, no evidential overlap),
  `docs-promptfoo-evaluate-coding-agents.md` (agent-eval capability tiers
  and workspace isolation), `blog-promptfoo-owasp-red-teaming.md` (runtime
  attack simulation rather than static code scanning — same dismissal
  reasoning as the sibling #1264/#1265 notes),
  `docs-promptfoo-enterprise-audit-logging.md` (control-plane audit trail),
  and `docs-promptfoo-evaluate-openai-agents-python.md` (the tracing/OTLP
  bridge). The real cross-references were discovered by searching
  `source-notes/` for the code-scan, cache, outputs, and credential notes
  named by the Prospector triage. Every cited `Claim N` was re-read and its
  number verified against the cited note before use, per MINER.md §4b.
- Sibling issues #1826 (`azure-pipelines`) and #1827 (`bitbucket-pipelines`)
  are the same integration family and were still untriaged at extraction
  time. Per the Prospector's guidance, this note extracts the AWS-specific
  delta (CodeBuild buildspec, Parameter Store injection, least-privilege
  IAM, the CodeCommit PR-comment workaround, and the unpinned-install
  posture) rather than re-deriving the generic "eval as a CI gate" pattern
  that those pages will also contain.
- No contradiction issue was filed; the two candidate conflicts and the
  reasons for rejecting them are recorded under Cross-References →
  Contradicts, per MINER.md §4a. Checked open `contradiction`-labeled issues
  and `CONTRADICTIONS.md`: no existing entry covers CI-gate implementation
  or scanner-install pinning.
- Vendor caveat: everything here is Promptfoo's own recipe for its own
  product. The configuration artifacts (buildspecs, IAM JSON, jq program) are
  directly checkable and are the citable content; the outcomes the recipes
  are supposed to produce (a build that fails on a failing assertion, a PR
  comment that reflects the scan) are vendor-intended, and Claim 4 shows
  one of them not holding. `confidence_overall` is `emerging`, consistent
  with the sibling #1264 and #1265 notes.
