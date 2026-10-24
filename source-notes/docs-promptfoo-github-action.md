---
source_url: https://www.promptfoo.dev/docs/integrations/github-action
source_type: docs
title: "Promptfoo GitHub Actions Integration — Before/After Report, Prompt-Path-Only Trigger, and a Red-Team Snippet That Masks Run Failure"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-23
date_extracted: 2026-10-24
last_checked: 2026-10-24
status: current
confidence_overall: emerging
issue: "#1857"
---

# Promptfoo GitHub Actions Integration — Before/After Report, Prompt-Path-Only Trigger, and a Red-Team Snippet That Masks Run Failure

> The vendor recipe for `promptfoo/promptfoo-action@v1` is a PR *reporting*
> integration, not a documented pass/fail gate: it triggers only on
> `prompts/**`, posts a before/after viewer link, and never states an exit
> code or threshold. Its red-team example deliberately swallows the CLI's
> exit status with `|| true` and substitutes a file-existence check, so a
> failed scan and a clean scan are indistinguishable at the gate.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "Testing Prompts
  with GitHub Actions", `/docs/integrations/github-action`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own GitHub Action, so authoritative about
  the YAML and parameter table it ships, but vendor-positioned and
  unvalidated: the page reports no measured run, timing, cost, gate outcome,
  or cache hit rate. The footer reads "Last updated on **Oct 23, 2026** by
  **promptfoobot\[bot\]**", i.e. the page is machine-maintained, and no
  original publication date is given.
- **Scope**: Covers one PR-triggered eval workflow built on
  `promptfoo/promptfoo-action@v1` (with `actions/setup-node` and
  `actions/cache`), a supported-parameter table, a short "How It Works"
  section, and a red-team example that bypasses the action in favour of
  `npx promptfoo@latest redteam run`. It does **not** document exit codes,
  pass-rate thresholds, JUnit output, fork-PR trust boundaries, artifact
  persistence, or cache invalidation. The linked action repository is not
  described on this page.
- **Relationship to sibling pages**: This is the GitHub Actions counterpart
  to `source-notes/docs-promptfoo-circleci-integration.md` (#1844), which
  covers the same eval-on-prompt-change pattern for CircleCI. It is a
  different product surface from
  `source-notes/docs-promptfoo-code-scan-github-action.md` (#1265), which
  covers the *code-scanning* action and its supply-chain hardening; this
  page covers the *eval/report* action.

## Extracted Claims

### Claim 1: The integration's stated job is a before-vs-after comparison posted as a PR comment — a report, not a documented pass/fail gate
- **Evidence**: The opening describes running "a before vs. after evaluation
  of edited prompts"; the outcome is a PR comment whose link opens the web
  viewer for interactive exploration. Neither the page nor the workflow
  config mentions a threshold, a required check, or a non-zero exit that
  would fail the PR.
- **Confidence**: settled for what the page documents; emerging for the
  action's actual exit-code behavior, which the page never states
- **Quote**: "This guide describes how to automatically run a before vs. after evaluation of edited prompts using the promptfoo GitHub Action."
- **Quote**: "On every pull request that modifies a prompt, the action will automatically run a full comparison"
- **Our assessment**: Buy the framing, and treat it as the page's most
  consequential omission. A comment-plus-viewer-link integration is a review
  aid: a human has to open the link and decide. Wiring it into a required
  status check without an explicit threshold converts "the action completed"
  into "the eval passed", which is the "gate that cannot fail" failure class
  the guide already names (`guide/05-llm-ops-reliability.md:655`). The
  sibling CircleCI note found the same gap and relied on promptfoo's
  undocumented-here exit code (`docs-promptfoo-circleci-integration.md`
  Claims 6–7); this page does not even show the CLI, because the action hides
  it. For Ch05 the actionable rule is: pair the action with an explicit
  threshold/exit-code contract, or label the job informational.

### Claim 2: The workflow trigger is path-filtered to `prompts/**` only, so edits to `promptfooconfig.yaml`, assertions/tests, provider config, or application code do not run the evaluation
- **Evidence**: The `on.pull_request.paths` block contains exactly one glob,
  `prompts/**`. The action input then narrows the evaluated files further to
  `prompts/**/*.json` and reads config from
  `prompts/promptfooconfig.yaml`.
- **Confidence**: settled (directly readable configuration)
- **Quote**: "Here's an example action that watches a PR for modifications. If any file in the `prompts/` directory is modified, we automatically run the eval and post a link to the results using the `promptfoo/promptfoo-action@v1`."
- **Our assessment**: Buy it, and it is the same bypass the CircleCI note
  documents (`docs-promptfoo-circleci-integration.md` Claim 4). An eval's
  behavior is a function of the prompts *and* the config (providers,
  assertions, test cases, thresholds) *and* the system under test. A PR that
  only loosens an assertion in `promptfooconfig.yaml`, swaps a provider, or
  changes RAG retrieval plumbing exercises none of the prompt files and
  skips the eval entirely. The gate is editable by the change it is supposed
  to gate. The guide's CI-gating checklist should require the trigger surface
  to enumerate every input to the eval, not just the prompt directory.

### Claim 3: The action contract is three required inputs (`github-token`, `prompts`, `config`), two optional inputs (`openai-api-key`, `cache-path`), and `pull-requests: write` for the comment
- **Evidence**: The parameter table marks `github-token`, `prompts`, and
  `config` as required and `openai-api-key` and `cache-path` as optional; the
  workflow's `permissions` block sets `pull-requests: write` with the inline
  comment "This permission is used to post comments on Pull Requests".
- **Confidence**: settled (documented parameter table and workflow config)
- **Quote**: "The GitHub token. Used to authenticate requests to the GitHub API."
- **Quote**: "The glob patterns for the prompt files. These patterns are used to find the prompt files that the action should evaluate."
- **Quote**: "The path to the configuration file. This file contains settings for the action."
- **Our assessment**: Buy the contract as written, and note what it implies:
  the action needs a write-scoped `GITHUB_TOKEN` because its output channel is
  a PR comment. That makes the comment surface part of the gate's trust
  boundary (Claim 12). The table also omits the most important gate
  parameters a CI owner would look for — threshold, fail-on-error, JUnit
  output — consistent with Claim 11.

### Claim 4: The action imposes a hard Node.js runner floor of `>=22.22.0`, with Node.js 24 LTS recommended, and the recipe pins `setup-node` by commit SHA
- **Evidence**: The paragraph introducing the workflow states the requirement;
  the workflow uses
  `actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6` with
  `node-version: '24'`.
- **Confidence**: settled (stated requirement and directly readable config)
- **Quote**: "The action requires Node.js `>=22.22.0` on the runner; Node.js 24 LTS is recommended"
- **Our assessment**: Buy the floor as a compatibility constraint, but flag
  that the page documents no failure mode. A self-hosted runner or a pinned
  container below the floor is not told what happens — install failure,
  runtime error, or silent misbehavior — and the `node-version: '24'` example
  means the recipe silently moves with Node 24's minor releases unless the
  runner image is pinned. The guide's CI-gating checklist should require
  runtime-version floors to be enforced by the workflow, not just stated in
  prose.

### Claim 5: Caching is presented as an optional cost lever, keyed only on the runner OS and a static `promptfoo-v1` suffix — no config, model, prompt, or lockfile fingerprint
- **Evidence**: The `actions/cache@v4` step caches `~/.cache/promptfoo` with
  `key: ${{ runner.os }}-promptfoo-v1` and `restore-keys` prefix
  `${{ runner.os }}-promptfoo-`. The inline comment calls the step optional
  and says it saves money and time; "How It Works" repeats that the cache
  stores LLM requests and outputs "to save cost".
- **Confidence**: settled for the key shape (directly readable config);
  emerging for the operational consequence, since the page reports no
  measurements and no invalidation policy
- **Quote**: "This cache is optional, but you'll save money and time by setting it up!"
- **Quote**: "We use caching to speed up subsequent runs. The cache stores LLM requests and outputs, which can be reused in future runs to save cost."
- **Our assessment**: Buy the cost intent, and read the key as a correctness
  hazard. Because the key has no prompt/config/model component, the cache
  directory is restored across prompt edits — the very change the workflow
  fires on. promptfoo's *inner* cache key is provider-scoped and includes
  request content and provider configuration
  (`docs-promptfoo-configuration-caching.md` Claim 2), so a changed prompt
  should miss the inner cache even when the GitHub cache hits; but the outer
  key also carries a 14-day TTL'd directory
  (`docs-promptfoo-configuration-caching.md` Claim 4) with no
  `PROMPTFOO_CACHE_TTL` or `--no-cache` guidance. The page's "save cost" claim
  is unquantified, and the guide should require a cache key that fingerprints
  the eval definition and model/version when the cache is used for a
  correctness-bearing gate.

### Claim 6: The recipe's cache path is `~/.cache/promptfoo`, which differs from promptfoo's documented default `~/.promptfoo/cache`; coherence depends on the `cache-path` input, which the page never explains
- **Evidence**: The `actions/cache` `path`, the workflow's
  `cache-path: ~/.cache/promptfoo`, and the configuration section's statement
  that "The action uses `PROMPTFOO_CONFIG_DIR` and `PROMPTFOO_CACHE_PATH` to
  record state on the filesystem." The sibling caching reference documents
  the default as `~/.promptfoo/cache`.
- **Confidence**: emerging (the path difference is settled; the action's
  internal wiring from `cache-path` to `PROMPTFOO_CACHE_PATH` is implied but
  not stated)
- **Quote**: "Set environment variables: The action uses `PROMPTFOO_CONFIG_DIR` and `PROMPTFOO_CACHE_PATH` to record state on the filesystem."
- **Quote**: "The path to the cache. This is where the action stores temporary data."
- **Our assessment**: Buy the discrepancy and treat it as a copy-paste trap.
  The workflow caches `~/.cache/promptfoo`; the documented promptfoo default
  is `~/.promptfoo/cache`
  (`docs-promptfoo-configuration-caching.md` Claim 9). The recipe closes the
  gap by passing `cache-path`, but the page never says that this input sets
  `PROMPTFOO_CACHE_PATH` — a reader who removes the optional `cache-path`
  while keeping the `actions/cache` step may cache an empty directory and
  quietly lose the savings the step advertises. The page also never sets
  `PROMPTFOO_CONFIG_DIR` in the workflow despite naming it here.

### Claim 7: Pinning is inconsistent — `setup-node` is pinned to a commit SHA, while `promptfoo/promptfoo-action@v1` and `actions/cache@v4` float on mutable tags
- **Evidence**: `actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6`
  is SHA-pinned; `actions/cache@v4` and `promptfoo/promptfoo-action@v1` are
  tag references. The secret `OPENAI_API_KEY` is passed into the action as
  `openai-api-key`.
- **Confidence**: settled (directly readable config)
- **Quote**: "uses: promptfoo/promptfoo-action@v1"
- **Our assessment**: Buy it, and contrast it with the corpus's hardened
  scanner action. `docs-promptfoo-code-scan-github-action.md` Claim 2 records
  that the code-scan action installs an exact release-pinned CLI with
  `--ignore-scripts` and publishes a signed provenance attestation, and its
  Claim 8 records that the documented workflow pins third-party actions to
  full commit SHAs. This page's eval action is referenced by major tag `v1`,
  and `actions/cache` by `v4`, so both resolve to whatever the upstream tag
  points at on the run — the supply-chain posture the guide's rule at
  `guide/06-security-and-trust.md:726` rejects. The guide should apply the
  same SHA-pinning rule to the eval action, not only the scanner action.

### Claim 8: The red-team example bypasses the action entirely — it runs `npx promptfoo@latest`, names the config and target by UUID, uses `-j 5`, and writes `output.json`
- **Evidence**: The "For red teaming" section replaces the action with a
  `run` step invoking `npx promptfoo@latest redteam run` with
  `-c 9d32de26-…`, `-t 213c2235-…`, `-j 5`, and `-o output.json`.
- **Confidence**: settled (directly readable command)
- **Quote**: "For red teaming integrations, we recommend embedding more detailed reporting in your workflow."
- **Our assessment**: Buy it, and note the two operational facts the page
  does not explain. First, the vendor's own recommendation for red teaming is
  *not* the action, so the eval and security paths have different contracts
  and different failure semantics. Second, the command resolves
  `promptfoo@latest` at run time — unpinned, lifecycle scripts enabled, the
  same posture the CircleCI and CodeCommit notes flag
  (`docs-promptfoo-circleci-integration.md` Claim 2,
  `docs-promptfoo-aws-codecommit-codebuild.md` Claim 13) and the opposite of
  the scanner action's pinned install. The UUID arguments also imply a hosted
  config/target rather than a checked-in config file, which matters for
  reviewability: the thing under test is resolved from an opaque identifier,
  not visible in the PR diff.

### Claim 9: The red-team step swallows the CLI exit status with `|| true` and substitutes a file-existence check, so a failed or partial scan is only distinguishable as "output.json missing"
- **Evidence**: The step ends the `redteam run` invocation with `|| true`,
  then runs `test -f output.json || { echo 'output.json not found'; exit 1; }`.
  No step inspects the scan result, finding count, or exit code.
- **Confidence**: settled for the shell semantics; emerging for promptfoo's
  actual redteam exit codes, which the page does not document
- **Quote**: "test -f output.json || { echo 'output.json not found'; exit 1; }"
- **Our assessment**: Buy the masking, and this is the page's clearest
  failure-mode defect. `|| true` makes the step succeed regardless of what
  `redteam run` did; the compensating check only fires when the output file
  is absent. A scan that crashes after creating a partial file, a scan that
  is rate-limited into an empty result set, and a successful scan that found
  critical vulnerabilities all produce an `output.json` and a green step. The
  vendor's intent — keep the job alive long enough to publish duration and a
  summary (Claim 10) — is reasonable, but the compensating gate needs to be
  an exit-code/finding check, not a file check. The guide should call out
  `|| true` before a file-existence check as an anti-pattern: it downgrades
  "the security tool failed" to "the artifact is missing", which is the same
  class of fail-open the CodeCommit note reproduced
  (`docs-promptfoo-aws-codecommit-codebuild.md` Claims 4–6).

### Claim 10: The red-team step captures wall-clock duration into `$GITHUB_ENV` and a separate Node step builds the PR summary, so the keep-alive is sequencing, not evidence collection
- **Evidence**: The first step computes `start`/`end` with `date +%s`, writes
  `DURATION_SECONDS=$((end-start))` to `$GITHUB_ENV`, then runs the file
  check. The next step runs
  `node .github/scripts/redteam-summary.js --input output.json --out comment.md --print`.
- **Confidence**: settled (directly readable workflow)
- **Quote**: "echo \"DURATION_SECONDS=$((end-start))\" >> $GITHUB_ENV"
- **Our assessment**: Buy the mechanics. The `|| true` exists so the duration
  write runs even when the scan fails, and the summary step consumes
  `output.json` whether or not the scan was successful — which is exactly why
  Claim 9 matters: the summary can render a failed run as if it were a
  completed report. Passing a numeric duration through `$GITHUB_ENV` is safe,
  but the pattern is a reminder that `$GITHUB_ENV` is job-scoped shared state;
  the scanner note's intra-job persistence concern
  (`docs-promptfoo-code-scan-github-action.md` Claim 1) applies to any
  PR-controlled step writing it.

### Claim 11: The page documents no exit-code, pass-rate threshold, JUnit output, or required-check guidance — the only stated failures are the job failing on a missing `output.json` or on the action's internal behavior
- **Evidence**: The parameter table, "How It Works", and red-team section
  contain no mention of exit codes, `PROMPTFOO_PASS_RATE_THRESHOLD`,
  `PROMPTFOO_FAILED_TEST_EXIT_CODE`, JUnit, or required status checks. The
  only explicit failure is the red-team `test -f`. The "How It Works" section
  describes results being "automatically posted to the pull request".
- **Confidence**: settled (page text and absence)
- **Quote**: "This is where the magic happens. We run the evaluation, passing in the configuration file and the prompts we want to evaluate. The results of this step are automatically posted to the pull request."
- **Our assessment**: Buy the omission, and connect it to the documented CLI
  contract. promptfoo's actual CI gate is exit-code based, with three
  independent failure modes and an overridable failure code
  (`docs-promptfoo-configuration-outputs.md` Claim 10), and JUnit is the
  documented CI-viewer format (`docs-promptfoo-configuration-outputs.md`
  Claims 1–4). None of that is surfaced by this integration page. A reader
  who treats the example as a complete gate cannot tell whether a red PR
  comment means "assertion failed", "provider errored", or "the action posted
  something". The guide's Ch05 checklist should require the gate's failure
  contract to be written next to the workflow, not inferred from the action's
  marketing surface.

### Claim 12: The recipe is an `on: pull_request` workflow that passes a write-scoped token and PR-controlled prompt content into a third-party action, with no fork-PR or data-egress discussion
- **Evidence**: The workflow uses `on: pull_request` (not
  `pull_request_target`), requests `pull-requests: write`, and passes
  `${{ secrets.GITHUB_TOKEN }}` and `${{ secrets.OPENAI_API_KEY }}` to
  `promptfoo/promptfoo-action@v1`. The evaluated prompt files come from the
  PR checkout. The page never mentions forks, untrusted contributors, or what
  prompt content leaves the runner.
- **Confidence**: emerging (the workflow shape is settled; the fork-token
  downgrade and provider data-egress consequences are our reading of GitHub
  and promptfoo behavior)
- **Quote**: "# This permission is used to post comments on Pull Requests"
- **Our assessment**: Buy the omission as a Ch06 gap. Using `pull_request`
  rather than `pull_request_target` is the safer choice for running
  PR-controlled code, and GitHub normally downgrades a fork PR's
  `GITHUB_TOKEN` to read-only — which means the comment step fails on forks
  rather than gaining write access. But the page neither states that nor
  addresses the inverse risk: the action sends PR-supplied prompt text to a
  third-party API with the repository's provider key. That is a data-egress
  path on every untrusted PR. The guide's fork-PR trust-boundary discussion
  (`guide/06-security-and-trust.md:729`) should use this recipe as the
  concrete case: write token + third-party action + PR content + provider
  key, all in one job.

### Claim 13: The page's caching tip offers two install paths — add `promptfoo` as a dependency and cache npm, or `npx promptfoo@latest` with workflow files as the cache key — without recommending a pinned version
- **Evidence**: The tip shows `npm install --save-dev promptfoo` with
  `actions/setup-node` `cache: 'npm'`, and separately `npx promptfoo@latest`
  with `cache-dependency-path: '**/.github/workflows/*.yml'`. The gloss is
  "cache promptfoo instead of downloading it every run".
- **Confidence**: settled (directly readable snippets)
- **Quote**: "To speed up builds, you can cache promptfoo instead of downloading it every run:"
- **Quote**: "With package.json: Add promptfoo as a dependency, then use setup-node with caching:"
- **Our assessment**: Buy the performance intent, and note the two paths
  differ in reproducibility: `npm install --save-dev` plus a committed lockfile
  is the only one that gives a version-stable CLI, while `@latest` keyed on
  the workflow file gets a cache hit but still resolves a new version whenever
  the key rolls. The page presents them as equivalent cost optimizations; for
  a security or regression gate they are not. This is the same supply-chain
  choice the CodeCommit and CircleCI notes flag.

## Concrete Artifacts

### Eval workflow (verbatim from "Using the GitHub Action"; line breaks restored from the rendered code block)

```yaml
name: 'Prompt Evaluation'
on:
  pull_request:
    paths:
      - 'prompts/**'

jobs:
  evaluate:
    runs-on: ubuntu-latest

    permissions:
      # This permission is used to post comments on Pull Requests
      pull-requests: write

    steps:
      - name: Set up Node.js
        uses: actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6
        with:
          node-version: '24'

      # This cache is optional, but you'll save money and time by setting it up!
      - name: Set up promptfoo cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/promptfoo
          key: ${{ runner.os }}-promptfoo-v1
          restore-keys: |
            ${{ runner.os }}-promptfoo-

      # This step will actually run the before/after evaluation
      - name: Run promptfoo evaluation
        uses: promptfoo/promptfoo-action@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          prompts: 'prompts/**/*.json'
          config: 'prompts/promptfooconfig.yaml'
          cache-path: ~/.cache/promptfoo
```

### Supported parameters (verbatim from "Configuration")

| Parameter | Description | Required |
|---|---|---|
| `github-token` | The GitHub token. Used to authenticate requests to the GitHub API. | Yes |
| `prompts` | The glob patterns for the prompt files. These patterns are used to find the prompt files that the action should evaluate. | Yes |
| `config` | The path to the configuration file. This file contains settings for the action. | Yes |
| `openai-api-key` | The API key for OpenAI. Used to authenticate requests to the OpenAI API. | No |
| `cache-path` | The path to the cache. This is where the action stores temporary data. | No |

### Red-team steps (verbatim from "For red teaming"; line breaks restored)

```yaml
- name: Run Promptfoo redteam
  run: |
    start=$(date +%s)
    npx promptfoo@latest redteam run \
      -c 9d32de26-7926-44f1-af13-bd06cb86f691 \
      -t 213c2235-865c-4aa4-90cc-a002256e0a94 \
      -j 5 \
      -o output.json || true
    end=$(date +%s)
    echo "DURATION_SECONDS=$((end-start))" >> $GITHUB_ENV
    test -f output.json || { echo 'output.json not found'; exit 1; }

- name: Build redteam summary (JS)
  run: |
    node .github/scripts/redteam-summary.js --input output.json --out comment.md --print
```

### Caching tip — with `package.json` (verbatim from "For red teaming → Tip")

```yaml
steps:
  - uses: actions/checkout@v5
  - uses: actions/setup-node@v4
    with:
      node-version: '24'
      cache: 'npm'
  - run: npm ci
  - name: Run Promptfoo redteam
    run: npx promptfoo redteam run -c config.yaml -o output.json
```

### Caching tip — without `package.json` (verbatim from "For red teaming → Tip")

```yaml
steps:
  - uses: actions/checkout@v5
  - uses: actions/setup-node@v4
    with:
      node-version: '24'
      cache: 'npm'
      cache-dependency-path: '**/.github/workflows/*.yml'
  - name: Run Promptfoo redteam
    run: npx promptfoo@latest redteam run -c config.yaml -o output.json
```

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-circleci-integration.md` Claim 4 — the CircleCI recipe's
    only path filter is `prompts/**/*`, so config and app changes skip the
    eval. Claim 2 here is the same gate-bypass on GitHub Actions, reached
    independently.
  - `docs-promptfoo-circleci-integration.md` Claims 6–7 — that page's custom
    `jq` check is unreachable and its only failure contract is promptfoo's
    implicit exit code; this page documents no exit-code or threshold
    contract at all, so the same implicit gate is even less visible here.
  - `docs-promptfoo-configuration-caching.md` Claim 2 — the inner cache key is
    a provider-scoped composite including request content and provider
    configuration; that is what limits the blast radius of this page's static
    outer cache key (Claim 5).
  - `docs-promptfoo-configuration-caching.md` Claim 4 — cached responses are
    invalidated only by TTL (default 14 days) or manual clearing; the workflow
    here sets neither `PROMPTFOO_CACHE_TTL` nor a cold-cache flag.
  - `docs-promptfoo-configuration-caching.md` Claim 9 — the documented default
    cache path is `~/.promptfoo/cache` (overridable via
    `PROMPTFOO_CACHE_PATH`), which is the basis for the path discrepancy in
    Claim 6.
  - `docs-promptfoo-configuration-outputs.md` Claim 10 — CI gating is
    exit-code based with three independent failure modes and an overridable
    failure code; the source page documents none of that (Claim 11).
  - `docs-promptfoo-code-scan-github-action.md` Claim 2 and Claim 8 — the
    scanner action is exact-release-pinned with `--ignore-scripts`, provenance
    attestations, and full-SHA action pinning; this page's `@v1` and
    `actions/cache@v4` are the contrast (Claim 7).
  - `docs-promptfoo-aws-codecommit-codebuild.md` Claim 13 — the CodeCommit
    recipe installs promptfoo unpinned with lifecycle scripts enabled, the
    same posture as `npx promptfoo@latest` here (Claim 8).
- **Contradicts**: None found. The cache-path difference between this page
  (`~/.cache/promptfoo`) and the caching reference's default
  (`~/.promptfoo/cache`) is not a contradiction: the action exposes a
  `cache-path` input, so the recipe is configuring a non-default location,
  not asserting a different default. No contradiction issue filed.
- **Extends**:
  - `docs-promptfoo-circleci-integration.md` — supplies the GitHub Actions
    counterpart to the CircleCI eval gate, adding the action-input contract,
    the static `actions/cache` key, and the red-team `|| true` pattern.
  - `docs-promptfoo-code-scan-github-action.md` — extends the corpus's
    GitHub-Action coverage from the *scanner* action (hardened, SHA-pinned,
    fork-PR default-deny) to the *eval/report* action, which shares none of
    those properties.
  - `docs-promptfoo-configuration-caching.md` — shows how the eval cache is
    wired in a specific CI recipe: outer `actions/cache` key plus an explicitly
    placed cache directory, with no invalidation contract.
  - `docs-promptfoo-configuration-outputs.md` — extends the exit-code/JUnit
    discussion to a vendor integration page that omits both.
- **Novel**: This is the first corpus note on
  `/docs/integrations/github-action`. Specifically new:
  1. The eval action is documented as a before/after *report* posted as a PR
     comment, not as a pass/fail gate (Claim 1).
  2. The red-team `|| true` + `test -f output.json` pattern, which reduces a
     failed or partial security scan to a missing-artifact error (Claims 9–10).
  3. The `actions/cache` key `${{ runner.os }}-promptfoo-v1` with no
     config/model/prompt fingerprint (Claim 5), and the `~/.cache/promptfoo`
     vs `~/.promptfoo/cache` path mismatch (Claim 6).
  4. The action contract's required/optional inputs and the write-scoped
     comment permission in an `on: pull_request` job (Claims 3, 12).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add a GitHub Actions eval-gate
  checklist item requiring the trigger to cover the full gate surface —
  `prompts/**`, `promptfooconfig.yaml`, assertions/tests, provider config, and
  application code — not just `prompts/**` (Claim 2). Add a second item
  requiring an explicit failure contract: if the job is built on
  `promptfoo/promptfoo-action@v1`, it posts a report by default, so a
  threshold/exit-code check must be added or the job must be labeled
  informational (Claims 1, 11). This directly extends the existing "A gate
  that cannot fail is not a gate" section
  (`guide/05-llm-ops-reliability.md:655`) from config-level pass conditions to
  CI-level pass conditions. For caching, require the cache key to fingerprint
  the eval definition and model/version, and set `PROMPTFOO_CACHE_TTL` or
  `--no-cache` when the gate is correctness-bearing (Claims 5–6;
  `docs-promptfoo-configuration-caching.md` Claims 4, 9).
- **Chapter 06 (Security and Trust)**: Use this page as the eval-action
  counterexample to the scanner action's hardening: `promptfoo-action@v1` and
  `actions/cache@v4` are mutable tags while `setup-node` is SHA-pinned, and
  the red-team path runs `npx promptfoo@latest` (Claim 7–8). Apply the rule at
  `guide/06-security-and-trust.md:726` to eval actions, not only scanners.
  Add the red-team `|| true` + file-existence check as a concrete fail-open
  anti-pattern: it collapses "security scan failed" into "artifact missing"
  and never distinguishes a clean scan from a vulnerable one (Claim 9). For
  the fork-PR trust boundary (`guide/06-security-and-trust.md:729`), document
  the combined exposure in this recipe: write-scoped token + third-party
  action + PR-controlled prompt content sent to a provider API with the repo's
  key (Claim 12).
- **Chapter 02 / eval methodology**: When documenting the red-team run
  contract, note that the vendor's own GitHub Actions recommendation for red
  teaming bypasses the action entirely (Claim 8), so the eval and red-team
  paths have separate failure semantics. Cite this page as the example where
  a security run's exit status is discarded before the artifact check
  (Claim 9), in contrast to promptfoo's documented exit-code contract
  (`docs-promptfoo-configuration-outputs.md` Claim 10).

## Extraction Notes

- The source is a short vendor page (roughly 700 words plus code blocks). I
  read the entire rendered page via direct HTTP fetch
  (https://www.promptfoo.dev/docs/integrations/github-action), including the
  "Using the GitHub Action", "Configuration", "How It Works", and "For red
  teaming" sections and the caching tip. I did not follow sub-pages: the
  outbound links are the promptfoo-action repository, the web viewer, the
  getting-started/config docs, and a `redteam-summary.js` gist; the action
  repository's actual exit-code behavior is not described on this page and was
  not verified, so Claim 1's action-level exit status is marked emerging rather
  than settled.
- Page metadata: footer "Last updated on Oct 23, 2026 by
  promptfoobot\[bot\]"; no original publication date. `date_published` in the
  frontmatter therefore uses the last-updated date, matching the convention in
  sibling notes. `date_extracted` / `last_checked` are 2026-10-24 (UTC).
- Quotes were copied from the rendered page character-for-character. Code
  blocks arrive from HTML extraction as single reflowed lines; I restored line
  breaks at YAML/statement boundaries only, with no wording changes, and
  labeled the artifacts accordingly.
- `confidence_overall` is `emerging`: the YAML, parameter table, and shell
  snippets are settled (directly readable), but this is first-party vendor
  documentation with no measured run, cost, cache-hit, or gate outcome, and
  the action's internal exit-code/threshold behavior is not documented here.
  The fork-PR and data-egress readings (Claim 12) rely on GitHub behavior not
  stated on the page and are marked emerging.
- Related-candidates file (`miner-related-notes.md`) reviewed before writing
  Cross-References. Cited: `docs-promptfoo-circleci-integration.md` (direct
  sibling). Explicitly dismissed:
  - `docs-promptfoo-enterprise-findings-reports.md` — Enterprise findings
    UI/export matrix; no GitHub Actions eval wiring.
  - `docs-promptfoo-enterprise-guardrails.md` — runtime guardrail endpoint,
    not CI eval gating.
  - `docs-promptfoo-llm-rubric.md` — model-graded assertion configuration,
    not a CI integration.
  - `docs-google-sre-reliable-product-launches.md` — launch checklist process,
    not CI eval configuration.
  - `docs-promptfoo-enterprise-audit-logging.md` — control-plane audit events,
    unrelated to CI.
  - `docs-promptfoo-evaluate-openai-agents-python.md` — Python provider bridge
    for OpenAI Agents, not GitHub Actions.
  - `blog-incidentio-ai-sre-incident-run.md` — AI SRE incident response, not
    CI eval gating.
  - `docs-litellm-evals-api.md` — LiteLLM's OpenAI Evals API, different
    product and surface.
  - `docs-litellm-batches-api.md` — LiteLLM batch rate limiting, unrelated.
- Additional cross-references beyond the candidate list
  (`docs-promptfoo-code-scan-github-action.md`,
  `docs-promptfoo-configuration-caching.md`,
  `docs-promptfoo-aws-codecommit-codebuild.md`,
  `docs-promptfoo-configuration-outputs.md`) were found by searching
  `source-notes/` and each cited claim number was re-read and verified per
  MINER.md §4b before citation. No contradiction issue was filed. No guide
  files, registry files, or eval notes were modified; this is a real
  source-note PR, not a miner-eval artifact.
