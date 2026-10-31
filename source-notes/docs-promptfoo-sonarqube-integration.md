---
source_url: https://www.promptfoo.dev/docs/integrations/sonarqube
source_type: docs
title: "Integrate Promptfoo with SonarQube"
author: "Promptfoo"
date_published:
date_extracted: "2026-10-31"
last_checked: "2026-10-31"
status: current
confidence_overall: emerging
issue: "#1923"
---

# Integrate Promptfoo with SonarQube

> A vendor how-to for turning Promptfoo red-team findings into SonarQube generic-import issues, with a GitHub Actions/Jenkins recipe whose concrete blocking mechanism is a SonarQube Quality Gate — not the eval step itself.

## Source Context

- **Type**: docs (vendor product documentation; "Last updated on Oct 31, 2026 by renovate[bot]")
- **Author credibility**: Promptfoo (maintainer of the scanner) — authoritative for the flags and recipe shape, but this is a specification of an Enterprise-gated feature, not evidence that any team runs it or that the gate catches anything. No metrics, volumes, time-to-triage, or false-positive data are published.
- **Scope**: Covers the `sonarqube` output format, SonarQube Generic Issue Import via `sonar.externalIssuesReportPaths`, basic and advanced GitHub Actions workflows, a Jenkins pipeline, and optional custom-rule/Quality-Gate configuration. It does not document the `pf-sonar.json` schema, the finding-to-rule/severity mapping, zero-finding vs. skipped-scan behavior, or efficacy of the resulting gate.

## Extracted Claims

### Claim 1: The integration is positioned as making red-team findings participate in Quality Gates and block pipelines by importing them as ordinary SonarQube issues, using Generic Issue Import with no custom plugin
- **Evidence**: The page's opening promise plus the Overview bullet list. The page names the mechanism explicitly as "Generic Issue Import" and says no custom plugins are required; the four claimed benefits are issue visibility, gate enforcement, a familiar UI, and CI/CD portability.
- **Confidence**: emerging (vendor specification; no worked gate-failure example, no published measurements)
- **Quote**: 'This guide demonstrates how to integrate Promptfoo's scanning results into SonarQube, allowing red team findings to appear in your normal "Issues" view, participate in Quality Gates, and block pipelines when they breach security policies.'
- **Our assessment**: Buy the integration shape — this is a traditional-security-tool handoff, not another bespoke dashboard, so findings land where developers already triage code issues. Do **not** buy "block pipelines" from this sentence alone: the blocking mechanism is downstream (SonarQube Quality Gate), and the basic recipe in Claim 6 never checks the gate. The page conflates "issues imported" with "pipeline blocked."

### Claim 2: The documented artifact handoff is exactly `promptfoo eval --output pf-sonar.json --output-format sonarqube`, consumed by `sonar-scanner -Dsonar.externalIssuesReportPaths=pf-sonar.json`
- **Evidence**: The Basic CI/CD Integration workflow's "Run Promptfoo scan" and "SonarQube Scan" steps. The same two-command handoff is repeated in the Jenkins and advanced recipes.
- **Confidence**: settled as a documented product contract (flags and consumer flag are explicit); the report *contents* are undocumented
- **Quote**: '-Dsonar.externalIssuesReportPaths=pf-sonar.json'
- **Our assessment**: Buy the contract. The `sonarqube` formatter is a first-class output format, and `sonar.externalIssuesReportPaths` is SonarQube's documented generic-import consumer, so the bridge is a real one. But this note cannot confirm what the formatter emits — rule IDs, severities, file/line locations, and whether costs or prompts are included are all absent from the page. Treat the flag pair as stable and the payload as unverified.

### Claim 3: The page never documents the `pf-sonar.json` schema or the finding-to-rule/severity mapping; the only severity shown is a hard-coded `CRITICAL` in an optional custom-rule example
- **Evidence**: The "Create Custom Rules (optional)" snippet creates one rule with `custom_key=PF-Prompt-Injection`, `severity=CRITICAL`, and `type=VULNERABILITY`; there is no mapping table, sample report, or statement that promptfoo's own severity values are translated. The Overview instead relies on generic-import defaults it does not describe.
- **Confidence**: settled (documented absence across the page)
- **Quote**: "# Example API call to create a custom rule"
- **Our assessment**: This is the largest missing bridge. A gate is only as good as its rule/severity mapping: if every finding arrives as the same rule and the same `CRITICAL` severity, the Quality Gate cannot distinguish a prompt-injection bypass from a low-value finding. Calling custom rules "optional" while showing only one hard-coded rule reinforces that the mapping is manual and underspecified, not automatic.

### Claim 4: Quality Gate enforcement is documented as three conditions — built-in `Security Rating`, built-in `Security Hotspots Reviewed`, and a *custom* `"Issues from promptfoo > 0"` condition — but no procedure or API is given for creating that custom condition
- **Evidence**: The "Configure Quality Gate" bullet list names the three conditions. The page's only API example creates a *rule* via `/api/rules/create`; it never shows the Quality Gate condition API, a condition key, or a prerequisite that enables custom conditions on the stated SonarQube editions.
- **Confidence**: emerging (instructions are UI-level and incomplete; edition support is unstated)
- **Quote**: 'Add custom condition: "Issues from promptfoo > 0" (for critical findings)'
- **Our assessment**: Partially buy it. `Security Rating` and hotspot review are ordinary SonarQube gate conditions, but the promptfoo-specific condition is the one that makes this integration distinctive, and it is the one left as a UI exercise. The page's prerequisites say "Community Edition or higher" while custom rules/conditions are commonly edition- or plugin-dependent; the note cannot resolve that from the source. For the guide, the safe reading is: the generic import is portable, but the *custom blocking condition* needs edition-specific verification before relying on it.

### Claim 5: The page carries a product-tier mismatch — promptfoo side is Enterprise-gated, while the SonarQube prerequisite says Community Edition or higher and the prerequisites omit Promptfoo Enterprise
- **Evidence**: An info banner states the feature is Enterprise-only, immediately above Prerequisites that list SonarQube server edition, scanner, Node.js, and a promptfoo config — with no promptfoo edition/tier item.
- **Confidence**: settled (both statements are explicit on the same page)
- **Quote**: "This feature is available in Promptfoo Enterprise."
- **Our assessment**: Flag this for the guide. The mismatch is not fatal, but it makes the recipe non-reproducible for an open-source promptfoo user and undercuts the "works with any CI/CD system" portability claim: a key half of the integration is a paid-tier capability. Extract the recipe as a vendor specification of mechanics, not as an open-source-supported path.

### Claim 6: The Basic GitHub Actions recipe has no Quality Gate check step — it runs the scan and stops — so on its own it cannot block a pipeline despite the page's opening promise
- **Evidence**: The basic workflow's last step is "SonarQube Scan" invoking `sonar-scanner`; there is no `waitForQualityGate`, no quality-gate action, and no `abortPipeline` equivalent. The advanced workflow and Jenkins recipe add those mechanisms separately.
- **Confidence**: settled (absence in the complete basic workflow)
- **Quote**: '      - name: SonarQube Scan'
- **Our assessment**: Do not copy the basic recipe and claim you have a gate. Importing issues is necessary but not sufficient; the build fails only if a later step checks the gate (or SonarQube's server-side PR decoration does it out-of-band). This is an internal docs omission rather than a competing technical claim, so it does not warrant a contradiction issue, but it is exactly the "a gate that cannot fail is not a gate" failure mode Ch05 names.

### Claim 7: The advanced GitHub Actions recipe does add a Quality Gate check, via `SonarSource/sonarqube-quality-gate-action@master` with a five-minute timeout
- **Evidence**: The "Check Quality Gate" step uses the SonarSource quality-gate action and sets `timeout-minutes: 5`; the preceding scan step passes pull-request keys/branches so the gate can evaluate the PR.
- **Confidence**: settled (concrete workflow step)
- **Quote**: '        uses: SonarSource/sonarqube-quality-gate-action@master'
- **Our assessment**: Buy the mechanism, but note the supply-chain posture: `@master` is a floating ref for both the scan and gate actions, unlike the SHA-pinned pattern documented elsewhere in the promptfoo corpus. The timeout is sensible; the missing piece is that the gate action has no documented relationship to promptfoo's own eval exit status — it reads SonarQube's gate, which may be green even when the eval run failed (Claim 8).

### Claim 8: The advanced recipe swallows eval failure — `EVAL_FAILED=true` is written to `$GITHUB_OUTPUT` but never read, and the report is regenerated under `if: always()` — so a failed or incomplete eval can still yield a fresh `pf-sonar.json`
- **Evidence**: The eval command ends with `--share || echo "EVAL_FAILED=true" >> $GITHUB_OUTPUT`; no later step references `EVAL_FAILED` or the `redteam` step outcome. The "Generate multiple report formats" step runs under `if: always()` and re-runs `promptfoo eval` with `--no-cache` to produce the SonarQube file.
- **Confidence**: settled (the output is never consumed; the always() step is explicit)
- **Quote**: '          --share || echo "EVAL_FAILED=true" >> $GITHUB_OUTPUT'
- **Our assessment**: This repeats the skipped-vs-clean ambiguity the guide already warns about for SARIF. Here it is worse: the failed run's exit status is discarded, and the SonarQube report is produced by a *new* eval under `always()`, so the imported findings may not correspond to the run that was supposed to gate. There is no `skipReason`, completion marker, or "scan failed" artifact documented for this path.

### Claim 9: "Generate multiple report formats" does not convert one result set — it re-runs the entire eval three times (JSON, SonarQube, HTML), so the gated artifact and the imported report can diverge
- **Evidence**: The step invokes `promptfoo eval` separately for `pf-results.json` (json), `pf-sonar.json` (sonarqube), and `pf-results.html` (html), each with `--no-cache`.
- **Confidence**: settled (three full eval invocations are shown)
- **Quote**: '          # Generate SonarQube format'
- **Our assessment**: Do not copy this as a report-generation pattern. Re-running a red-team eval is non-deterministic (models, sampling, time), triples cost/latency, and breaks the audit link between the artifact a human reviews and the artifact the gate imports. The correct shape is one eval producing multiple output files, or an explicit conversion path if promptfoo supports it — neither is shown here.

### Claim 10: Jenkins gets the most explicit blocking mechanism — `waitForQualityGate abortPipeline: true` with a one-hour timeout — confirming that blocking is a gate step, not an eval side effect
- **Evidence**: The Jenkinsfile's "Quality Gate" stage wraps `waitForQualityGate abortPipeline: true` in `timeout(time: 1, unit: 'HOURS')`, after a `withSonarQubeEnv('SonarQube')` scan that passes `sonar.externalIssuesReportPaths=pf-sonar.json`.
- **Confidence**: settled (concrete Jenkinsfile)
- **Quote**: "                    waitForQualityGate abortPipeline: true"
- **Our assessment**: Buy it. This is the clearest statement on the page of how a pipeline is actually blocked; the GitHub examples leave that implicit or delegate it to a separate action. It also strengthens the cross-CI reading: the portable part is the `sonar-scanner` handoff; the gate check is CI-specific.

### Claim 11: The custom-rule API example hard-codes one rule (`PF-Prompt-Injection`, `CRITICAL`, `VULNERABILITY`) and does not show how promptfoo findings are assigned to it or to any other rule
- **Evidence**: The curl block passes `custom_key=PF-Prompt-Injection`, `name=Prompt Injection Vulnerability`, `severity=CRITICAL`, and `type=VULNERABILITY`; nothing maps eval finding categories (jailbreak, PII, harmful content, etc.) to distinct rules. The rules step is labelled "(optional)".
- **Confidence**: settled (only one example rule is shown)
- **Quote**: 'custom_key=PF-Prompt-Injection'
- **Our assessment**: Treat this as an illustration, not a mapping contract. One hard-coded `CRITICAL` rule collapses all promptfoo risk categories into a single severity, which makes the Quality Gate coarse and likely noisy; it also gives no path for adjusting severity per finding. The guide should not present this snippet as sufficient configuration.

### Claim 12: The "works with any CI/CD system" claim is demonstrated only with GitHub Actions and Jenkins, and the portable surface is just the two-command Handoff; everything about enforcement is SonarQube-side
- **Evidence**: The Overview bullet asserts broad CI/CD support. The page's concrete recipes are GitHub Actions (basic and advanced) and Jenkins; no GitLab/Azure/Bitbucket example is provided, despite sibling integration pages existing for some of those systems.
- **Confidence**: emerging (asserted portability; two examples only)
- **Quote**: "Works with any CI/CD system that supports SonarQube"
- **Our assessment**: Mostly buy the portability, narrowly. Any CI that can run Node/npm and `sonar-scanner` can produce and import the file; the gate evaluation is a SonarQube server feature, so portability is really "SonarQube portability," not proof that each CI's blocking semantics behave the same. The Jenkins example (`abortPipeline`) and GitHub example (quality-gate action) already differ in wiring.

### Claim 13: The page publishes no efficacy, volume, latency, or false-positive data, and no sample `pf-sonar.json`, so it specifies wiring but cannot substantiate that the gate catches anything
- **Evidence**: The page is a how-to with prerequisites, workflows, and configuration bullets; it contains no measured scan duration, finding counts, gate outcomes, or example report. The only "verification" is a PR-comment script that reports test pass/fail counts from `pf-results.json`.
- **Confidence**: settled (absence across the page)
- **Quote**: "Issues have been imported to SonarQube for tracking."
- **Our assessment**: Buy the wiring, withhold judgment on effectiveness. This is the same evidentiary class as the sibling promptfoo integration notes: first-party specification with no independent run. For the guide, cite it for the handoff mechanics and the tier caveat, not for "this catches vulnerabilities in CI."

## Concrete Artifacts

### Basic GitHub Actions workflow (complete, from "1. Basic CI/CD Integration")

```yaml
name: SonarQube Analysis with Promptfoo
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
jobs:
  analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Shallow clones should be disabled for better analysis
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'
      - name: Install Promptfoo
        run: npm install -g promptfoo
      - name: Run Promptfoo scan
        run: |
          promptfoo eval \
            --config promptfooconfig.yaml \
            --output pf-sonar.json \
            --output-format sonarqube
      - name: SonarQube Scan
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        run: |
          sonar-scanner \
            -Dsonar.projectKey=${{ github.event.repository.name }} \
            -Dsonar.sources=. \
            -Dsonar.externalIssuesReportPaths=pf-sonar.json
```

### Advanced GitHub Actions workflow (eval, report generation, scan, gate — excerpt)

```yaml
      - name: Run red team evaluation
        id: redteam
        env:
          PROMPTFOO_CACHE_PATH: ~/.cache/promptfoo
        run: |
          # Run with failure threshold
          promptfoo eval \
            --config promptfooconfig.yaml \
            --output pf-results.json \
            --output-format json \
            --max-concurrency 5 \
            --share || echo "EVAL_FAILED=true" >> $GITHUB_OUTPUT
      - name: Generate multiple report formats
        if: always()
        run: |
          # Generate SonarQube format
          promptfoo eval \
            --config promptfooconfig.yaml \
            --output pf-sonar.json \
            --output-format sonarqube \
            --no-cache
          # Also generate HTML report for artifacts
          promptfoo eval \
            --config promptfooconfig.yaml \
            --output pf-results.html \
            --output-format html \
            --no-cache
      - name: SonarQube Scan
        if: always()
        uses: SonarSource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        with:
          args: >
            -Dsonar.projectKey=${{ github.event.repository.name }}
            -Dsonar.externalIssuesReportPaths=pf-sonar.json
            -Dsonar.pullrequest.key=${{ github.event.pull_request.number }}
            -Dsonar.pullrequest.branch=${{ github.head_ref }}
            -Dsonar.pullrequest.base=${{ github.base_ref }}
      - name: Check Quality Gate
        uses: SonarSource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Custom rule creation (from "3. Configure SonarQube")

```bash
# Example API call to create a custom rule
curl -u admin:$SONAR_PASSWORD -X POST \
  "$SONAR_HOST/api/rules/create" \
  -d "custom_key=PF-Prompt-Injection" \
  -d "name=Prompt Injection Vulnerability" \
  -d "markdown_description=Potential prompt injection vulnerability detected" \
  -d "severity=CRITICAL" \
  -d "type=VULNERABILITY"
```

### Quality Gate configuration (verbatim bullets)

```text
Navigate to Quality Gates in SonarQube
Add condition: "Security Rating is worse than A"
Add condition: "Security Hotspots Reviewed is less than 100%"
Add custom condition: "Issues from promptfoo > 0" (for critical findings)
```

### Jenkins pipeline (complete, from "4. Jenkins Integration")

```groovy
pipeline {
    agent any
    environment {
        SONAR_TOKEN = credentials('sonar-token')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Run Promptfoo') {
            steps {
                sh '''
                    npm install -g promptfoo
                    promptfoo eval \
                        --config promptfooconfig.yaml \
                        --output pf-sonar.json \
                        --output-format sonarqube
                '''
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=${JOB_NAME} \
                            -Dsonar.sources=. \
                            -Dsonar.externalIssuesReportPaths=pf-sonar.json
                    '''
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '*.json,*.html', fingerprint: true
        }
    }
}
```

## Cross-References

- **Corroborates**: `source-notes/docs-promptfoo-enterprise-findings-reports.md` Claim 4 — that note records that the findings page's SARIF export names SonarQube but documents "no upload step, no CI job, and no build-blocking behavior." This page supplies the missing CI-side bridge for the *direct* `sonarqube` output format (not the SARIF export), including an import flag and gate conditions. Also corroborates the skipped-vs-clean rule in `source-notes/docs-promptfoo-code-scan-cli.md` Claim 9 and `source-notes/docs-promptfoo-code-scan-github-action.md` Claim 5: this page has no completion signal at all, so the same ambiguity applies and is arguably worse because failed evals are swallowed.
- **Contradicts**: None material. The basic workflow's missing gate step contradicts the page's own opening claim in spirit, but the advanced GitHub and Jenkins recipes supply the blocking step, so this is an incomplete example rather than an opposing technical claim. No contradiction issue filed.
- **Extends**: `source-notes/docs-promptfoo-jenkins-integration.md` Claim 6 — that note says the Jenkins integration documents "No JUnit/SARIF/security-gate artifacts or exit-code threshold configuration." This page documents a Jenkins security-gate variant (`sonar-scanner` + `waitForQualityGate abortPipeline: true` + `sonar.externalIssuesReportPaths`), so it extends that note rather than refuting it (different integration page). Also extends `source-notes/docs-promptfoo-configuration-outputs.md` Claim 1: JUnit is documented there as the CI-gating format; this page adds `sonarqube` as another output consumer with a different gate model.
- **Novel**: The `sonarqube` output format, the `sonar.externalIssuesReportPaths` generic-import handoff, SonarQube Quality Gate condition vocabulary for promptfoo findings, and the `waitForQualityGate abortPipeline` blocking shape are all new to the corpus. The SARIF export path already covered in `docs-promptfoo-enterprise-findings-reports.md` Claim 4 is a distinct mechanism and is not conflated here.

## Guide Impact

- **Chapter 06 — §"Gating on LLM security scans"**: Add a second consumer path alongside the code-scan SARIF example: red-team eval findings can be imported into SonarQube via `--output-format sonarqube` and `sonar.externalIssuesReportPaths`, but the gate must be the SonarQube Quality Gate check (`waitForQualityGate abortPipeline: true` in Jenkins; `sonarqube-quality-gate-action` in GitHub Actions). Cite this note; do not imply the import step itself blocks.
- **Chapter 06 — §"Red-teaming as a CI gate"**: Add the traditional-tool handoff as a concrete pattern, with the caveat that the promptfoo side is Enterprise-gated and the page publishes no efficacy data. Note the product-tier mismatch explicitly so readers do not plan an OSS-only deployment around this recipe.
- **Chapter 05 — §"A gate that cannot fail is not a gate"**: Use the advanced workflow's `--share || echo "EVAL_FAILED=true" >> $GITHUB_OUTPUT` as a named anti-pattern: writing a failure flag that nothing reads, then regenerating the gating artifact under `if: always()` with a fresh eval. Recommend one eval run producing all formats and an explicit failure/completion signal that the gate consumes.
- **Chapter 05 — evaluation methodology**: Add the point that report generation should not re-run the eval; separate generation from execution so the artifact a human reviews matches the artifact the gate imports. This page's three separate `promptfoo eval` invocations are a concrete counterexample.

## Extraction Notes

- Read the full page, including all four code recipes. No sub-pages were followed: the next-step link points at generic red-team documentation, and the page is self-contained for this integration.
- The page is current per its footer ("Last updated on Oct 31, 2026 by renovate[bot]"), but that is bot maintenance, not a human freshness review.
- Candidate dismissal from `miner-related-notes.md`: cited `docs-promptfoo-enterprise-findings-reports.md`; dismissed `docs-litellm-evals-api.md`, `docs-litellm-batches-api.md`, `blog-pagerduty-sre-agent-triage.md`, `docs-promptfoo-pi-scorer.md`, `docs-langfuse-mcp-server.md`, `docs-google-sre-eliminating-toil.md`, `docs-google-sre-reliable-product-launches.md`, `docs-google-sre-team-lifecycles.md`, and `docs-promptfoo-deterministic-metrics.md` as not bearing on the SonarQube handoff (different products, eval-scoring internals, or unrelated SRE chapters).
- The raw HTML renders code tokens with line-number spans that strip newlines; code blocks above were reconstructed from the page's rendered text with indentation preserved. Prose quotes were copied from the page source verbatim.
- The page says "Configure Quality Gate" but gives no API for custom conditions; I did not import outside knowledge of SonarQube edition feature matrices into the claims, beyond flagging that the page leaves the question unresolved.
- Do not merge the `miner-eval` / eval-note variants; this is a live-trial source note.
