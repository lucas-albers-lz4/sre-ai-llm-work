---
source_url: https://www.promptfoo.dev/docs/integrations/jenkins
source_type: docs
title: "Setting up Promptfoo with Jenkins"
author: "Promptfoo"
date_published:
date_extracted: "2026-10-24"
last_checked: "2026-10-24"
status: current
confidence_overall: emerging
issue: "#1873"
---

# Setting up Promptfoo with Jenkins

> A vendor how-to for running Promptfoo evals in Jenkins, showing a two-tier gate (fail on exception, mark UNSTABLE on assertion failures), unconditional `--share`, and unpinned global install with filesystem caching.

## Source Context

- **Type**: docs (vendor documentation, machine-maintained by promptfoobot[bot]; "Last updated on Oct 23, 2026")
- **Author credibility**: Promptfoo (maintainer of the tool) — authoritative for the recipe itself; no timing, cost, or measured gate-outcome data provided
- **Scope**: Covers basic Jenkinsfile (install, eval, process results, archive artifacts) and an advanced variant (timeouts, timestamps, SCM polling, changeset trigger, HTML report publishing, email on failure, workspace cleanup). No red-team, code-scans, SARIF, JUnit output, thresholding, fork-PR trust, or version pinning are discussed.

## Extracted Claims

### Claim 1: The basic pipeline fails only on a thrown exception; assertion failures are downgraded to UNSTABLE
- **Evidence**: Jenkinsfile code — `Evaluate Prompts` stage wraps `promptfoo eval` in `try/catch` and on exception sets `currentBuild.result = 'FAILURE'` and calls `error(...)`; `Process Results` reads `output.json`, echoes successes/failures, and if `output.results.stats.failures > 0` sets `currentBuild.result = 'UNSTABLE'` (no `error()` call).
- **Confidence**: settled
- **Quote**: "stage('Evaluate Prompts') { steps { script { try { sh 'promptfoo eval -c promptfooconfig.yaml --prompts prompts/**/*.json --share -o output.json' } catch (Exception e) { currentBuild.result = 'FAILURE' error(\"Prompt evaluation failed: ${e.message}\") } } } } } stage('Process Results') { steps { script { def output = readJSON file: 'output.json' echo \"Evaluation Results:\" echo \"Successes: ${output.results.stats.successes}\" echo \"Failures: ${output.results.stats.failures}\" if (output.shareableUrl) { echo \"View detailed results at: ${output.shareableUrl}\" } if (output.results.stats.failures > 0) { currentBuild.result = 'UNSTABLE' } } } }"
- **Our assessment**: This is a concrete gate-semantics split. In Jenkins, `UNSTABLE` does not fail the build by default and downstream jobs may still proceed; blocking depends on branch protection/job configuration. The page never states that failing assertions block merges — it only downgrades to unstable. This is distinct from exit-code-only gating described elsewhere.

### Claim 2: The eval command unconditionally uploads results via `--share`
- **Evidence**: Both basic and advanced Jenkinsfiles pass `promptfoo eval ... --share -o output.json` with no flag to disable sharing; `Process Results` echoes `output.shareableUrl` when present.
- **Confidence**: settled
- **Quote**: "sh 'promptfoo eval -c promptfooconfig.yaml --prompts prompts/**/*.json --share -o output.json'"
- **Our assessment**: `--share` is baked into the vendor recipe. The page provides no discussion of what prompts/responses/variables are uploaded, access control for the shareable URL, or opt-out for internal data — a data-egress decision that needs to be weighed against org policy.

### Claim 3: Provider credentials are bound via Jenkins `credentials()` as plain environment variables
- **Evidence**: `environment { OPENAI_API_KEY = credentials('openai-api-key') ... }` binds a Secret-text credential to an env var for the pipeline; setup instructs adding a secret credential with ID `openai-api-key`.
- **Confidence**: settled
- **Quote**: "environment { OPENAI_API_KEY = credentials('openai-api-key') PROMPTFOO_CACHE_PATH = '~/.promptfoo/cache' }"
- **Our assessment**: Uses Jenkins credential binding (better than hardcoding), but the key is exposed as a plain env var to all steps and there is no guidance to mask it in shell output, restrict it to a single step, or avoid logging `output.json` contents that might include sensitive data.

### Claim 4: Installation is unpinned global npm install with self-managed filesystem cache
- **Evidence**: `Setup` stage runs `sh 'npm install -g promptfoo'` (no version pin). Cache configured via `PROMPTFOO_CACHE_PATH = '~/.promptfoo/cache'`, with instructions to `mkdir -p ~/.promptfoo/cache` and `chown -R jenkins:jenkins ~/.promptfoo/cache`.
- **Confidence**: settled
- **Quote**: "stage('Setup') { steps { sh 'npm install -g promptfoo' } }"
- **Our assessment**: Reproducibility and supply-chain posture mirror other non-Action CI recipes in the corpus (CircleCI, CodeCommit) — floating install on an unpinned agent base image. Tilde expansion in `~/.promptfoo/cache` may not be honored by all shells/agents.

### Claim 5: The advanced pipeline narrows trigger scope and adds reporting/notifications
- **Evidence**: Advanced config adds `timeout(time: 1, unit: 'HOURS')`, `timestamps()`, `triggers { pollSCM('H/15 * * * *') }`, `when { changeset 'prompts/**' }` on the eval stage, writes an HTML report and publishes it with `publishHTML`, emails on failure via `emailext`, and does `cleanWs()` in post.
- **Confidence**: settled
- **Quote**: "triggers { pollSCM('H/15 * * * *') } ... stage('Evaluate Prompts') { when { changeset 'prompts/**' } ... } ... publishHTML([... reportName: 'Prompt Evaluation Report' ...]) ... post { failure { emailext (...) } always { cleanWs() } }"
- **Our assessment**: Triggering only on `prompts/**` changes means changes to `promptfooconfig.yaml`, assertions, providers, or app code do not run evals — a common coverage gap. HTML report is published as an ad-hoc artifact alongside `output.json`.

### Claim 6: No JUnit/SARIF/security-gate artifacts or exit-code threshold configuration are documented
- **Evidence**: Pipeline archives only `output.json` (and HTML in advanced variant). No `--output junit.xml`, no SARIF, no `code-scans`, no `PROMPTFOO_PASS_RATE_THRESHOLD`, no failure-exit-code override shown.
- **Confidence**: settled
- **Quote**: "archiveArtifacts artifacts: 'output.json', fingerprint: true" (basic); "archiveArtifacts artifacts: 'output.json,evaluation-report.html', fingerprint: true" (advanced)
- **Our assessment**: This is an eval-only recipe with no security-gate integration — consistent with other non-GitHub-Action Promptfoo CI recipes and contrasts with the hardened Action examples in the corpus.

## Concrete Artifacts

```jenkinsfile
pipeline {
    agent any
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
        PROMPTFOO_CACHE_PATH = '~/.promptfoo/cache'
    }
    stages {
        stage('Setup') {
            steps {
                sh 'npm install -g promptfoo'
            }
        }
        stage('Evaluate Prompts') {
            steps {
                script {
                    try {
                        sh 'promptfoo eval -c promptfooconfig.yaml --prompts prompts/**/*.json --share -o output.json'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Prompt evaluation failed: ${e.message}")
                    }
                }
            }
        }
        stage('Process Results') {
            steps {
                script {
                    def output = readJSON file: 'output.json'
                    echo "Evaluation Results:"
                    echo "Successes: ${output.results.stats.successes}"
                    echo "Failures: ${output.results.stats.failures}"
                    if (output.shareableUrl) {
                        echo "View detailed results at: ${output.shareableUrl}"
                    }
                    if (output.results.stats.failures > 0) {
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'output.json', fingerprint: true
        }
    }
}
```
*(Source: https://www.promptfoo.dev/docs/integrations/jenkins — basic Jenkinsfile as shown)*

```text
npm install -g promptfoo
promptfoo eval -c promptfooconfig.yaml --prompts prompts/**/*.json --share -o output.json
PROMPTFOO_CACHE_PATH = '~/.promptfoo/cache'
OPENAI_API_KEY = credentials('openai-api-key')
```
*(Key commands/env from the page)*

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-circleci-integration.md` Claim 1 — eval-only (no red-team/code-scans). Claim 2 — unpinned global `npm install -g promptfoo`. Claim 3 — unconditional `--share`. Claim 4 — narrow path filters (`prompts/**`). Claim 6/7 — exit-code/gate semantics leave room for custom handling; here the page makes the split explicit (exception → FAILURE, assertion failures → UNSTABLE).
  - `docs-promptfoo-aws-codecommit-codebuild.md` Claim 13 — unpinned global install posture on non-Action CI.
  - `docs-promptfoo-configuration-outputs.md` Claim 1 — JUnit/XML are documented CI-gating formats for systems like Jenkins, but this recipe does not use them (uses raw `output.json` + ad-hoc HTML). Claim 6 — share/export carries "do not put secrets in shareable inputs" warning; `--share` is used unconditionally here with no discussion.
  - `docs-promptfoo-configuration-caching.md` — `PROMPTFOO_CACHE_PATH` guidance matches using an external cache path in CI.

- **Contradicts**: None found. Different platforms show different gate mechanics (CircleCI relies more on exit codes/step flow; Jenkins recipe explicitly splits exception vs assertion failure). Not opposing the same claim.

- **Extends**:
  - `docs-promptfoo-circleci-integration.md` — adds a third non-GitHub CI platform (Jenkins) and makes the "report vs gate" distinction explicit via Jenkins' FAILURE vs UNSTABLE states.
  - `docs-promptfoo-github-action.md` / `docs-promptfoo-aws-codecommit-codebuild.md` — reinforces the pattern of vendor recipes baking in `--share` and unpinned installs on non-hardened CI paths.

- **Novel**:
  - **Jenkins-specific gate semantics**: explicit two-tier handling (caught exception → `FAILURE` + `error()`; assertion failures read from `output.json` → `UNSTABLE` only). The page states neither that UNSTABLE blocks merges nor the branch-protection implications.
  - **`--share` in a Jenkins recipe with shareable URL surfaced in console and HTML report** — concrete egress surface (logged to console, linked in published HTML). Combined with no egress discussion.
  - **Credentials via Jenkins `credentials()` Secret-text binding** as the documented pattern (with no per-step scoping/masking guidance).
  - **Filesystem cache setup instructions** (`mkdir` + `chown` on `~/.promptfoo/cache`) and reliance on tilde expansion.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — eval gating in delivery pipelines)**: Add Jenkins as a third distinct CI example. Call out the FAILURE-vs-UNSTABLE split as a "report vs. gate" case (yellow != red by default) and note that merge blocking depends on branch protection. Contrast with CircleCI exit-code behavior.
- **Chapter 06 (Security and Trust — CI egress/credentials)**: Treat unconditional `--share` in CI as a data-egress decision (prompts/outputs uploaded to Promptfoo's hosted viewer; URL logged/linked). Note credential binding via `credentials()` but lack of step-scoping/masking guidance and unpinned global install as supply-chain considerations.
- **Chapter 02 (Observability — artifact surface)**: Note raw `output.json` archiving (no JUnit) and optional HTML report publication; surface `shareableUrl` as an external artifact.

## Extraction Notes

- Read the full page (basic and advanced Jenkinsfiles, prerequisites, credentials, caching, troubleshooting). Page is vendor-authored, machine-maintained (promptfoobot[bot], updated Oct 23 2026), no measured timing/cost/gate outcomes.
- Cross-references verified against cited notes: checked claim numbers/contents in `docs-promptfoo-circleci-integration.md`, `docs-promptfoo-aws-codecommit-codebuild.md`, `docs-promptfoo-configuration-outputs.md`, `docs-promptfoo-configuration-caching.md`. No contradictions found; split is a difference in how gates are expressed across platforms.
- Related-notes candidates from `miner-related-notes.md` were reviewed: none directly overlapped the Jenkins-specific gate semantics/egress; dismissed as not directly applicable (enterprise findings/reports, litellm evals/batches, pagerduty triage, pi scorer, langfuse mcp, SRE toil) — no citations added.
