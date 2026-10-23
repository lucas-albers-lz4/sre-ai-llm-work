---
source_url: https://www.promptfoo.dev/docs/integrations/circle-ci/
source_type: docs
title: "Promptfoo CircleCI Integration — Eval-Only Gate, Prompt-Path Trigger, and an Implicit Exit-Code Contract"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-23
date_extracted: 2026-10-23
last_checked: 2026-10-23
status: current
confidence_overall: emerging
issue: "#1844"
---

# Promptfoo CircleCI Integration — Eval-Only Gate, Prompt-Path Trigger, and an Implicit Exit-Code Contract

> A short vendor recipe for running promptfoo evals in CircleCI that is useful
> less for what it prescribes than for what it leaves implicit: the workflow
> fires only when `prompts/**/*` changes (not when the eval config or app code
> changes), the gate depends on promptfoo's undocumented-here exit code rather
> than the custom `jq` check shown, and the artifact/cache steps are skipped on
> exactly the failing runs a responder would want to inspect.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo "Setting up
  Promptfoo with CircleCI" page, `/docs/integrations/circle-ci`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own CircleCI recipe, so authoritative about
  the configuration it ships, but vendor-positioned and unvalidated: the page
  reports no run, no timing, no cost, and no measured gate outcome. The page
  footer reads "Last updated on **Oct 23, 2026** by **renovate\[bot\]**", i.e.
  it is machine-maintained, and no original publication date is given.
- **Scope**: Covers one eval job in CircleCI — a `.circleci/config.yml` that
  installs promptfoo, restores a cache, runs `promptfoo eval`, saves the cache,
  and stores `output.json` as an artifact — plus an optional `jq` failure check,
  a parallel-evaluation snippet, and a short troubleshooting list. It does
  **not** cover red-team scans, `code-scans`, JUnit output, exit-code semantics,
  pass-rate thresholds, fork-PR trust boundaries, or version pinning.
- **Relationship to sibling pages**: This is the corpus's second non-GitHub CI
  integration for promptfoo, after
  `source-notes/docs-promptfoo-aws-codecommit-codebuild.md` (#1825), and it is
  much narrower: the AWS page covers both evals and code scanning, while this
  page covers evals only. The hardening contrast is with
  `source-notes/docs-promptfoo-code-scan-github-action.md` (#1265).

## Extracted Claims

### Claim 1: The CircleCI integration is eval-only — the page never mentions red-team scanning or `code-scans`, so it does not describe a security gate
- **Evidence**: The opening sentence frames the page as LLM evaluation; the
  single configuration runs `promptfoo eval`; the sections cover caching,
  artifacts, a `jq` failure check, and parallelism. There is no `redteam`,
  `code-scans`, SARIF, or scan-comment content anywhere on the page.
- **Confidence**: settled (the section inventory in Source Context covers the whole page, and none of those sections mentions red-team scanning or `code-scans`)
- **Quote**: "This guide shows how to integrate promptfoo's LLM evaluation into your CircleCI pipeline. This allows you to automatically test your prompts and models whenever changes are made to your repository."
- **Our assessment**: Buy the scope statement, and treat the omission as the
  first guide-relevant fact. The corpus's GitHub-Action note is about a
  *security scanner* gate (`docs-promptfoo-code-scan-github-action.md`), and the
  CodeCommit note covers both eval and code-scan paths. A reader who sees
  "promptfoo + CircleCI" could reasonably assume parity; this page gives only
  the eval path. For Ch06, the actionable point is that a CircleCI security
  gate has to be assembled by hand from the CLI/API surface, not copied from
  this integration page.

### Claim 2: The recipe installs promptfoo globally, unpinned, into a floating `cimg/node:lts` image — the same supply-chain posture the corpus flagged in the CodeCommit recipe and the opposite of the hardened GitHub Action
- **Evidence**: The `docker:` image line and the install step's command line
  in the basic configuration.
- **Confidence**: settled (directly readable configuration)
- **Quote**: "`- image: cimg/node:lts`"
- **Quote**: "`command: npm install -g promptfoo`"
- **Our assessment**: Buy it, with the same caveat the CodeCommit note records:
  this is a vendor recipe, not a hardened distribution path. `cimg/node:lts`
  floats with the Node LTS line, and `npm install -g promptfoo` resolves
  whatever `latest` is at run time with lifecycle scripts enabled. Compare the
  GitHub Action, which installs "an exact, release-pinned version of the
  `promptfoo` CLI with npm lifecycle scripts disabled (`--ignore-scripts`)" and
  publishes a signed build-provenance attestation
  (`docs-promptfoo-code-scan-github-action.md` Claim 2), and the CodeCommit
  note's Claim 13, which calls the unpinned non-Action path the supply-chain
  opposite of the Action. The guide already tells readers to pin LLM
  infrastructure dependencies and CI dependencies
  (`guide/06-security-and-trust.md:636`, `:726`); this page is another concrete
  instance of a vendor recipe that violates that rule.

### Claim 3: The basic configuration runs `promptfoo eval` with `--share` unconditionally, so every CI eval publishes a shareable result URL in addition to storing the artifact
- **Evidence**: The eval command includes both `--share` and `-o output.json`;
  the "Storing Results" section explains that the flag creates a web URL.
- **Confidence**: settled (documented flag behavior)
- **Quote**: "`command: promptfoo eval -c promptfooconfig.yaml --prompts prompts/**/*.json --share -o output.json`"
- **Quote**: "The --share flag creates a shareable web URL for results"
- **Our assessment**: Buy the behavior, and treat the default as a data-egress
  decision the page does not discuss. The corpus's outputs note records the
  vendor's own warning that sharing "can include prompts, vars, outputs,
  traces, metadata, provider configuration fields, media/blob references, scan
  artifacts, and derived artifacts" and that secrets must not be placed in
  shareable inputs (`docs-promptfoo-configuration-outputs.md` Claim 6). A CI
  pipeline that shares on every run publishes that snapshot to a URL on each
  green and red build, before anyone has reviewed it. The guide should require
  an explicit opt-in (and a data-classification check) for `--share` in CI,
  rather than copying the vendor's default.

### Claim 4: The workflow's only path filter is `prompts/**/*`, so changes to `promptfooconfig.yaml`, assertions/tests, provider configuration, or application code do not trigger the eval job
- **Evidence**: The `workflows.evaluate.jobs.evaluate_prompts.filters.paths`
  block contains exactly one glob, `prompts/**/*`. The eval command also
  overrides the prompt set with `--prompts prompts/**/*.json`.
- **Confidence**: settled (directly readable configuration)
- **Quote**: "`- prompts/**/*`"
- **Our assessment**: Buy it, and this is the page's most consequential gate
  gap. A promptfoo eval's behavior is a function of the prompt files *and* the
  config (providers, assertions, test cases, thresholds) *and* the application
  under test. Filtering on prompt files alone means a pull request that changes
  only `promptfooconfig.yaml` — for example, loosening an assertion or swapping
  a model — skips evaluation entirely. The gate is therefore bypassable by
  editing the gate's own definition, which is the same class of failure as a
  test suite that only runs when test files change. The guide's CI-gating
  guidance should name the full change surface, not just the prompts.

### Claim 5: The CircleCI cache key's `checksum "prompts/**/*"` component is inert — CircleCI's `checksum` helper hashes a single file path, not a glob — so the effective key degenerates to the branch plus the global fallback and fingerprints neither the prompts nor the eval configuration
- **Evidence**: The `restore_cache.keys` and `save_cache.key` both use
  `promptfoo-cache-v1-{{ .Branch }}-{{ checksum "prompts/**/*" }}`, with
  fallbacks to the branch alone and to the global `promptfoo-cache-v1-` prefix.
  CircleCI's configuration reference defines the helper as "A base64 encoded
  SHA256 hash of the given filename's contents", with the file "referenced as
  an absolute or relative path from the current working directory" — a single
  file, with no glob support — and every example passes one lockfile. There is
  no file literally named `prompts/**/*`, so the helper never hashes the prompt
  files. The caching section nevertheless says the cache "Is keyed by branch
  and content hash".
- **Confidence**: settled for the key contents and for the helper's single-file
  contract (CircleCI's own reference); emerging for the exact runtime result of
  passing a glob — an unresolved/empty component and an interpolation error are
  both plausible, and the page documents neither
- **Quote**: "`- promptfoo-cache-v1-{{ .Branch }}-{{ checksum "prompts/**/*" }}`"
- **Quote**: "Is keyed by branch and content hash"
- **Our assessment**: Buy the narrow key, and read the checksum component as
  broken rather than merely narrow: this is a glob passed where CircleCI
  expects a file path, so the "content hash" the page advertises never tracks
  prompt edits. Because the key is immutably written once and CircleCI then
  reuses it, the effective key is branch-scoped, with the branch-only and
  global `promptfoo-cache-v1-` fallbacks behind it letting a new branch restore
  another branch's cache directory. Nothing in the CircleCI key covers the eval
  definition (assertions/tests), provider configuration, or application code.
  promptfoo's *inner* cache partly compensates — it is keyed by provider
  identifier, prompt/request content, provider configuration, and context
  variables (`docs-promptfoo-configuration-caching.md` Claim 2), so a
  provider/model change inside `promptfooconfig.yaml` should miss the inner
  cache even when CircleCI restores the directory. That inner keying does not
  rescue the CircleCI-key design: the safe reading is that the CircleCI key is
  a *directory-selection* policy with a dead fingerprint component, not an
  eval-configuration fingerprint. A team that edits the RAG app but not the
  prompt files can still replay cached model responses against the old
  behavior — assuming the job runs at all, which per Claim 4 it will not.

### Claim 6: The page's own custom failure check is unreachable in the default CircleCI flow when it would be true — `promptfoo eval` exits non-zero on a failed test, and CircleCI skips subsequent steps
- **Evidence**: The custom step is a `run` step that follows the eval step and
  reads `output.json` with `jq`. It has no `when: always`. promptfoo's documented
  default is exit code `100` on at least one failed test case
  (`docs-promptfoo-configuration-outputs.md` Claim 10), and CircleCI's default
  is to halt the job on a failed step.
- **Confidence**: settled for the code order and promptfoo's exit-code contract;
  emerging for the CircleCI default (external, not stated on this page)
- **Quote**: "`if jq -e '.results.stats.failures > 0' output.json; then`"
- **Quote**: "Any test failures will cause the CircleCI job to fail"
- **Our assessment**: Buy the mechanism, and read the custom check as decorative
  rather than load-bearing. If the eval has a failing assertion, promptfoo
  exits `100`, CircleCI stops the job, and the "Check evaluation results" step
  never runs. If the eval exits `0`, the check runs but its condition is false.
  The gate that actually fires is promptfoo's implicit exit code, not the
  vendor's `jq` snippet. This is a different failure mode from the CodeCommit
  page's custom gate, which *replaces* `--fail-on-error` and fails open
  (`docs-promptfoo-aws-codecommit-codebuild.md` Claims 4–6); here the default
  exit code still fails closed, but the extra check gives a false sense that
  the JSON is being consulted. A team that sets
  `PROMPTFOO_FAILED_TEST_EXIT_CODE=0` to keep the job alive would make the
  check meaningful — but then it ignores `errors`, only counting `failures`.

### Claim 7: The page asserts that test failures fail the job but never documents the exit-code mechanism, the failure code, or the environment-variable overrides that can change or disable it
- **Evidence**: The "Example Output" bullet is the only statement of the
  failure contract; there is no mention of exit code `100`, exit code `1`,
  `PROMPTFOO_FAILED_TEST_EXIT_CODE`, or `PROMPTFOO_PASS_RATE_THRESHOLD`
  anywhere on the page.
- **Confidence**: settled (page text and absence)
- **Quote**: "Any test failures will cause the CircleCI job to fail"
- **Our assessment**: Buy the statement, flag the omission. promptfoo's actual
  contract is three independent failure modes — a per-test failure, an
  aggregate pass-rate threshold, and any other error — and the failure exit code
  can itself be overridden (`docs-promptfoo-configuration-outputs.md` Claim 10).
  A reader of this page cannot tell whether the job failed because an assertion
  failed, because the pass rate was below a threshold, or because the provider
  errored; nor can they tell that an ambient env var can turn the gate green.
  The guide's Ch05 gate checklist should require the exit-code contract to be
  written down next to the CI config, not inferred from a success bullet.

### Claim 8: `store_artifacts` and `save_cache` run after the eval step, so a failing eval skips both — the JSON artifact is unavailable on exactly the runs that need debugging
- **Evidence**: In the configuration, `promptfoo eval` precedes `save_cache` and
  `store_artifacts`; neither step has `when: always`. CircleCI's default
  stop-on-failure behavior therefore skips them when the eval exits non-zero.
- **Confidence**: emerging (artifact order is settled; the skip behavior relies
  on CircleCI's documented default rather than this page)
- **Quote**: "`path: output.json`"
- **Quote**: "Results are saved to output.json"
- **Our assessment**: Buy it as an operational trap. The page says CircleCI
  makes results "available in the Artifacts tab", which is true for green runs.
  On a red run — the run a responder or on-call engineer actually wants — the
  eval step's non-zero exit stops the job before `store_artifacts`, so
  `output.json` is not uploaded. The fix is a `when: always` on the artifact
  step (and arguably on `save_cache`). This is the CI equivalent of a gate that
  discards its evidence; the guide should pair every gate with
  always-persisted failure artifacts.

### Claim 9: The recipe uses raw `output.json` as both the artifact and the gate input, not JUnit XML — even though JUnit is promptfoo's documented CI-gating format
- **Evidence**: The only output flag is `-o output.json`; the custom check
  parses `.results.stats.failures` with `jq`; no `junit.xml`, `--output`, or
  JUnit mention appears. The outputs note documents JUnit XML as the format
  aimed at CI viewers and deliberately lossy (`docs-promptfoo-configuration-outputs.md`
  Claims 1–4).
- **Confidence**: settled (directly readable configuration; the JUnit
  documentation is from the sibling note)
- **Quote**: "`command: promptfoo eval -c promptfooconfig.yaml --prompts prompts/**/*.json --share -o output.json`"
- **Quote**: "Results are saved to output.json"
- **Our assessment**: Buy it. Raw JSON is a full export that embeds the eval
  `config` under best-effort redaction
  (`docs-promptfoo-configuration-outputs.md` Claim 5), and it is being both
  shared (`--share`, Claim 3) and archived as a CI artifact. JUnit would give
  CircleCI a native pass/fail view with config, prompts, variables, raw
  outputs, assertion reasons, and provider error payloads deliberately omitted.
  The custom `jq` check also depends on `.results.stats.failures`, a field the
  outputs note describes as an opaque stub that the vendor's own snippet
  consumes without documenting (`docs-promptfoo-aws-codecommit-codebuild.md`
  Claim 5). For a CI recipe, the safer default is JUnit for the gate and a
  separate, access-controlled full export for debugging.

### Claim 10: The basic recipe does set an explicit `PROMPTFOO_CACHE_PATH`, matching promptfoo's documented CI guidance for external frameworks
- **Evidence**: The eval step's `environment` block sets
  `PROMPTFOO_CACHE_PATH: ~/.promptfoo/cache`, and the save/restore paths point
  at the same directory. The caching note records the vendor's CI
  recommendation to set `PROMPTFOO_CACHE_TYPE=disk` and an explicit
  `PROMPTFOO_CACHE_PATH`.
- **Confidence**: settled (configuration + sibling documentation)
- **Quote**: "`PROMPTFOO_CACHE_PATH: ~/.promptfoo/cache`"
- **Our assessment**: Buy it as the page's best practice. Making the cache path
  explicit is preferable to letting a runner default create an implicit cache,
  and it is what makes the `save_cache`/`restore_cache` pair coherent. The
  caveat is that the *placement* is explicit while the *invalidation policy* is
  not (Claim 5): the page never sets `PROMPTFOO_CACHE_TTL`, never disables the
  cache for a cold gate, and never explains what a stale hit means for a red or
  green build. Explicit path, implicit freshness.

### Claim 11: The "Parallel Evaluation" example is not a runnable CircleCI job — it omits checkout, install, cache, artifacts, and output flags, and passes the split file list unquoted
- **Evidence**: The advanced snippet defines `jobs.evaluate_prompts` with
  `parallelism: 3` and a single `run` step; it has no `checkout`, no
  `npm install -g promptfoo`, no `store_artifacts`, no `--share`, and no
  `-o output.json`. The split command substitutes an unquoted `$prompts` into
  `--prompts`.
- **Confidence**: settled for the omissions (directly readable); emerging for
  the word-splitting consequence
- **Quote**: "`prompts=$(find prompts -name "*.json" | circleci tests split)`"
- **Quote**: "`promptfoo eval -c promptfooconfig.yaml --prompts $prompts`"
- **Our assessment**: Buy it as a documentation defect. The snippet is presented
  under "Advanced Configuration" as a job replacement
  (`jobs: evaluate_prompts:`), but a fresh CircleCI container has neither the
  repository nor the CLI, so the job as written cannot run. Even if a reader
  merges it into the basic job, it drops the persistence and share steps, so a
  parallel run produces no artifact and no shareable URL. The unquoted
  `$prompts` also relies on word splitting to turn a newline-separated list
  into separate CLI arguments; filenames with spaces would break it. Treat this
  snippet as pseudocode, not a copy-paste recipe.

### Claim 12: The troubleshooting section addresses cache plumbing, credential typos, and timeouts, but not the gate's own failure modes — assertion failure vs provider error, empty results, or stale cache
- **Evidence**: The three troubleshooting entries are "Cache not working",
  "API key errors", and "Evaluation timeout"; the remedies are cache key/path/
  permissions, env-var spelling/permissions, and `no_output_timeout` plus test
  splitting.
- **Confidence**: settled (page text)
- **Quote**: "Adjust the no_output_timeout setting in your job"
- **Quote**: "Consider splitting tests into smaller batches"
- **Our assessment**: Buy the list as plumbing help, not gate diagnosis. The
  corpus already distinguishes assertion failures from provider/runtime errors
  as a first-class product concept (`docs-promptfoo-configuration-outputs.md`
  Claim 3) and documents the CLI filters/retry behavior that separate them
  (same note, Claim 9). A CircleCI user whose eval fails for a provider reason
  will see a red job and, per this page, be told to check API keys or raise the
  timeout — not to distinguish an errored run from a failed assertion. That is
  the same gap as Claim 7, from the operator's side.

## Concrete Artifacts

### Basic `.circleci/config.yml` (verbatim from "1. Create CircleCI Configuration")

```yaml
version: 2.1

jobs:
  evaluate_prompts:
    docker:
      - image: cimg/node:lts
    steps:
      - checkout

      - restore_cache:
          keys:
            - promptfoo-cache-v1-{{ .Branch }}-{{ checksum "prompts/**/*" }}
            - promptfoo-cache-v1-{{ .Branch }}
            - promptfoo-cache-v1-

      - run:
          name: Install promptfoo
          command: npm install -g promptfoo

      - run:
          name: Run prompt evaluation
          command: promptfoo eval -c promptfooconfig.yaml --prompts prompts/**/*.json --share -o output.json
          environment:
            OPENAI_API_KEY: ${OPENAI_API_KEY}
            PROMPTFOO_CACHE_PATH: ~/.promptfoo/cache

      - save_cache:
          key: promptfoo-cache-v1-{{ .Branch }}-{{ checksum "prompts/**/*" }}
          paths:
            - ~/.promptfoo/cache

      - store_artifacts:
          path: output.json
          destination: evaluation-results

workflows:
  version: 2
  evaluate:
    jobs:
      - evaluate_prompts:
          filters:
            paths:
              - prompts/**/*
```

### Custom failure step (verbatim from "Adding Custom Test Steps")

```yaml
- run:
    name: Check evaluation results
    command: |
      if jq -e '.results.stats.failures > 0' output.json; then
        echo "Evaluation had failures"
        exit 1
      fi
```

### Parallel evaluation snippet (verbatim from "Parallel Evaluation")

```yaml
jobs:
  evaluate_prompts:
    parallelism: 3
    steps:
      - run:
          name: Split tests
          command: |
            prompts=$(find prompts -name "*.json" | circleci tests split)
            promptfoo eval -c promptfooconfig.yaml --prompts $prompts
```

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-configuration-outputs.md` Claim 10 — the exit-code contract
    (exit `100` on a failed case or below-threshold pass rate, exit `1` on
    other errors, overridable via `PROMPTFOO_FAILED_TEST_EXIT_CODE`) is what
    makes Claim 6's custom check unreachable and Claim 7's statement true but
    under-specified.
  - `docs-promptfoo-configuration-caching.md` Claims 1, 2, and 9 — the cache is
    on by default at `~/.promptfoo/cache`, keyed by a provider-scoped composite
    including request content and provider configuration, and controlled by
    `PROMPTFOO_CACHE_*`; this refines Claim 5's reading of the CircleCI key.
  - `docs-promptfoo-aws-codecommit-codebuild.md` Claim 13 — unpinned
    `npm install -g promptfoo` is the non-Action supply-chain posture, matching
    Claim 2 here; its Claims 4–6 describe a different custom-gate failure mode
    (fails open), not the same one.
  - `docs-promptfoo-configuration-outputs.md` Claim 6 — the vendor's own
    "do not put secrets in shareable inputs" warning corroborates the exposure
    concern in Claim 3.
  - `docs-promptfoo-configuration-outputs.md` Claims 1–4 — JUnit XML is the
    documented CI-gating format and deliberately lossy, supporting Claim 9's
    recommendation.
- **Contradicts**: None found. The CircleCI page and the CodeCommit page
  prescribe different gates (implicit exit code here vs. a custom `jq`/`bc`
  threshold there), but they are different vendor recipes for different
  platforms, not opposing claims about the same behavior. No contradiction
  issue filed.
- **Extends**:
  - `docs-promptfoo-aws-codecommit-codebuild.md` — adds a second non-GitHub CI
    platform, and a narrower one (evals only).
  - `docs-promptfoo-configuration-outputs.md` — extends the CI-gating/artifact
    discussion into CircleCI's path filters and cache keys.
  - `docs-promptfoo-code-scan-github-action.md` — supplies the hardened-install
    counterexample for Claim 2.
- **Novel**: First CircleCI-specific source note in the corpus. The
  prompt-path-only trigger (Claim 4), the branch/global cache fallback keys
  (Claim 5), the unreachable custom check (Claim 6), and the
  skipped-on-failure artifact step (Claim 8) are all new to the corpus.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add a CI-gate checklist item requiring
  the eval job to trigger on the full gate surface — prompt files, eval config
  (`promptfooconfig.yaml`), assertions/tests, provider config, and application
  code — not just `prompts/**/*` (Claim 4). Add a second item requiring the
  failure contract to be explicit (exit code, threshold, overrides) and failure
  artifacts to be persisted with `when: always` (Claims 6–8). The existing
  "a gate that cannot fail is not a gate" rule
  (`guide/05-llm-ops-reliability.md:655`) should be paired with "a gate that
  never runs on the change is not a gate."
- **Chapter 06 (Security and Trust)**: Use this page as a concrete
  counterexample when repeating the pinning rule
  (`guide/06-security-and-trust.md:636`, `:726`): the vendor's CircleCI recipe
  installs `promptfoo` unpinned on a floating Node image (Claim 2). Add
  `--share` and raw `output.json` artifacts to the data-egress inventory
  (Claims 3, 9), with the rule that sharing is opt-in and artifacts are
  access-controlled because the JSON export carries eval config.
- **Chapter 02 / eval methodology**: When distinguishing assertion failures
  from execution errors, cite this page as an example of a CI recipe that
  conflates them operationally — the failure bullet and troubleshooting list
  never name the distinction (Claims 7, 12), even though promptfoo models it
  (`docs-promptfoo-configuration-outputs.md` Claims 3, 9).

## Extraction Notes

- The source is a short vendor page (roughly 500 words plus three code blocks).
  I read the entire page, extracted all three code blocks from the rendered HTML
  to preserve exact line breaks, and did not follow sub-pages: the only
  substantive outbound link is the configuration reference, whose relevant
  behavior is already covered by the corpus notes cited above
  (`docs-promptfoo-configuration-outputs.md`,
  `docs-promptfoo-configuration-caching.md`).
- Page metadata: footer "Last updated on Oct 23, 2026 by renovate\[bot\]"; no
  original publication date. `date_published` in the frontmatter is therefore
  the last-updated date, matching the convention in sibling notes.
- Claims 6 and 8 rely on CircleCI's documented default of stopping a job when
  a step fails; that behavior is not stated on the source page, so those
  consequences are marked emerging rather than settled.
- Claim 5's reading of `{{ checksum }}` comes from CircleCI's own
  configuration reference (`circleci.com/docs/configuration-reference`, the
  "String interpolation" section), not from the promptfoo page, which never
  describes the helper. Verified 2026-10-23: the helper hashes one named file
  and is given an absolute or relative path; no glob support is documented.
- Related-candidates file (`miner-related-notes.md`) reviewed. Dismissed:
  - `docs-promptfoo-enterprise-findings-reports.md` — Enterprise findings UI,
    no CI or CircleCI content.
  - `docs-litellm-evals-api.md` — LiteLLM evals API, different product and
    surface.
  - `docs-litellm-batches-api.md` — LiteLLM batch rate limiting, unrelated.
  - `blog-pagerduty-sre-agent-triage.md` — AI incident triage, not CI eval
    gating.
  - `docs-promptfoo-pi-scorer.md` — a specific model-graded scorer, not CI.
  - `docs-langfuse-mcp-server.md` — docs MCP server, unrelated.
  - `docs-google-sre-eliminating-toil.md` — toil taxonomy; no CI gate or
    CircleCI material.
  - `docs-google-sre-reliable-product-launches.md` — launch process, not CI
    eval configuration.
  - `docs-google-sre-team-lifecycles.md` — SRE team formation, unrelated.
  - `docs-promptfoo-deterministic-metrics.md` — deterministic assertion types,
    not CI integration.
- No guide files, registry files, or eval notes were modified. This note is
  intended as a real source-note PR, not a miner-eval artifact.
