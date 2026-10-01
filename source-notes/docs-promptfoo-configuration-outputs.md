---
source_url: https://www.promptfoo.dev/docs/configuration/outputs/
source_type: docs
title: "Promptfoo Configuration: Output Formats — Results Export and Analysis"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-01
date_extracted: 2026-10-01
last_checked: 2026-10-01
status: current
confidence_overall: emerging
issue: "#1528"
---

# Promptfoo Configuration: Output Formats

> The vendor reference for how an LLM eval's results leave the harness — and
> therefore what a CI gate is allowed to see: JUnit XML as the deliberately
> minimised CI-bridge format (one `testsuite` per prompt/provider pair, one
> `testcase` per result, `failure` for assertion failures vs `error` for
> provider/runtime faults) that omits config, prompts, variables, raw outputs,
> assertion reasons, and provider error payloads "so CI test-report viewers stay
> compact and do not become a second full export surface" — while every other
> documented format except CSV embeds the eval `config` under a sanitizer the
> vendor itself calls "best-effort (not comprehensive)."

## Source Context

- **Type**: docs (vendor product documentation — promptfoo configuration
  reference, "Configuration > Output Formats" page)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of the tool's own export surface — authoritative for
  promptfoo product behavior, but vendor-positioned: the page reports no
  measured file sizes, artifact-retention figures, or redaction test results, and
  the "intentionally stays compact" framing is a stated design rationale with no
  independent validation. The format shapes and the CLI flag surface are
  directly checkable against an installed CLI.
- **Scope**: Covers the seven documented export formats and a `Use when:` for
  each, `outputPath` in config vs repeated `--output` flags, which fields land in
  which format, the JSONL streaming-reader pattern, artifact-hygiene
  `.gitignore` guidance, the JSON/CSV post-hoc analysis snippets, and the
  sharing surface. Does NOT cover the assertion types themselves (other notes),
  the eval-result cache (covered by `docs-promptfoo-configuration-caching.md`),
  or red-team report generation. Three linked sub-pages were read for the claims
  that depend on them — see Extraction Notes.
- **Last updated**: Oct 1, 2026 by renovate[bot]; page is otherwise undated.
- **Issue provenance**: auto-filed from the `promptfoo-docs` site-crawl seed
  (`https://www.promptfoo.dev/docs/getting-started/`); no human deep-read
  preceded this extraction.

## Extracted Claims

### Claim 1: JUnit XML is promptfoo's documented CI-gating format — emitted with `promptfoo eval --output results.junit.xml` and aimed at CI systems that already consume JUnit-style test reports, naming GitLab, Azure Pipelines, Bitbucket Pipelines, and Jenkins
- **Evidence**: The "JUnit XML Format" section's `Use when:` line, and the
  Quick Start block's fifth line.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Use when: Publishing eval results into CI systems that already understand JUnit-style test reports, such as GitLab, Azure Pipelines, Bitbucket Pipelines, Jenkins, and other test-report viewers."
- **Our assessment**: Buy it. This is the mechanism by which an LLM eval becomes a
  first-class CI check rather than a side artifact someone has to remember to open
  — and the named-consumer list is the operative part: the payoff is
  interoperability with test-report viewers an organisation already has
  provisioned and staffed, not a bespoke dashboard. For the guide this is the
  concrete answer to "how does an eval gate a pipeline": emit a format the
  existing CI already understands. No existing corpus note covers JUnit
  emission (`grep -ril junit source-notes/ guide/` returns zero hits), so this is
  net-new.

### Claim 2: The JUnit structural contract is one `<testsuite>` per prompt/provider pair and one `<testcase>` per eval result — so grouping and per-case coverage are explicit design requirements, not incidental
- **Evidence**: The "JUnit XML intentionally stays compact" bullet list, plus the
  worked XML sample whose `<testsuite name="[openai:gpt-4.1] prompt 1">` carries
  `tests="2" failures="1" errors="0"` and two `<testcase>` children.
- **Confidence**: settled (documented product behavior; the shape is checkable
  against the published sample)
- **Quote**: "one `testsuite` per prompt/provider pair so CI groups related cases together" / "one `testcase` per eval result so every promptfoo test appears in CI"
- **Our assessment**: Buy it, and the second half is the load-bearing clause.
  "Every promptfoo test appears in CI" is a coverage guarantee, not a formatting
  note: the failure mode this rules out is the eval harness silently reporting a
  subset of its cases to CI, which would turn a partially-executed gate into a
  green one. The prompt/provider-pair grouping is the other half of the contract
  — it is what makes per-model and per-prompt regressions legible in a CI
  dashboard instead of collapsing into one undifferentiated pass/fail count.

### Claim 3: `failure` is reserved for failed assertions and `error` for provider/runtime errors, explicitly so CI can tell incorrect model behavior apart from an execution fault
- **Evidence**: The third bullet of the "JUnit XML intentionally stays compact"
  list.
- **Confidence**: settled as a documented distinction; **emerging** as a
  reliability guarantee, because the page states the intent but does not
  demonstrate that downstream viewers preserve the distinction
- **Quote**: "`failure` for failed assertions and `error` for provider/runtime errors so CI can distinguish incorrect behavior from execution problems"
- **Our assessment**: Buy the distinction; treat the reliability claim as
  unverified. The taxonomy is real and first-class — the aggregate counters are
  separate (`<testsuites tests="2" failures="1" errors="0" ...>`), and the same
  failure/error split is independently load-bearing elsewhere in the product
  (Claim 8). But the page makes no claim about whether GitLab/Azure/Jenkins
  render `<error>` distinctly from `<failure>` in their UIs, and many generic
  JUnit viewers collapse both to "failed". A guide should therefore assert the
  format-level distinction (settled) and treat "your CI dashboard will show the
  responder which of the two it is" as something to verify against the specific
  viewer rather than assume. This is the eval-harness analogue of the
  skip-vs-clean distinction the corpus already carries for security scanners.

### Claim 4: JUnit XML is deliberately lossy — it omits eval config, prompts, variables, raw model outputs, assertion reasons, and provider error payloads, and carries "concise failure/error summaries only", on the stated rationale that CI viewers must not become a second full export surface
- **Evidence**: The "Structured Output Fields" warning's closing paragraph, the
  fourth compactness bullet, and the published sample whose `<failure
  message="Assertion failed">` body is the three-line summary
  `Score: 0` / `Reason: Assertion failed` / `Failed assertions: - contains`.
- **Confidence**: settled (documented design behavior, vendor-stated rationale)
- **Quote**: "JUnit XML omits the eval config, prompts, variables, raw model outputs, assertion reasons, and provider error payloads by design so CI test-report viewers stay compact and do not become a second full export surface." / "concise failure/error summaries only; use JSON, HTML, or Promptfoo XML when you need assertion reasons, provider errors, prompts, variables, raw model outputs, or full config"
- **Our assessment**: Buy this as a design statement, and it is the most
  transferable idea on the page. The vendor explicitly treats "how much data
  lands in a widely-readable, widely-retained CI artifact" as an
  artifact-exposure-control decision, and solves it by subtraction at the format
  boundary rather than by trusting downstream retention. Note the cost, which
  the page also states: a CI-gated assertion failure arrives **without its
  reason**. Anyone debugging a red CI check must go back to the JSON/HTML export
  or the web viewer — so the lossy format is a gating surface, not an
  investigation surface, and a pipeline that only publishes the JUnit file has
  an unexplainable gate. The two must be emitted together. This is the
  one-place in the corpus where the blast-radius tradeoff is stated by the tool
  vendor as a first-class design goal.

### Claim 5: The other documented formats are full exports — `json`, `yaml`, `yml`, `txt`, `html`, and Promptfoo XML all include the eval `config`, with sensitive fields redacted "on a best-effort basis (not comprehensive)" and non-sensitive `config.env` values possibly still present
- **Evidence**: The `warning` admonition in the "Structured Output Fields"
  section, quoted verbatim below.
- **Confidence**: settled (documented product behavior, vendor-flagged as a
  security matter)
- **Quote**: "`json`, `yaml`, `yml`, `txt`, `html`, and Promptfoo XML outputs include the eval `config`. Sensitive fields are redacted using Promptfoo's sanitizer rules on a best-effort basis (not comprehensive). Non-sensitive `config.env` values may still appear in exports."
- **Our assessment**: Buy it, and it is the highest-value Ch06 item on the page.
  Two things matter operationally. First, the sanitizer's own vendor describes
  it as incomplete — so "redacted" is not a control you can rely on, and any
  pipeline that publishes these files to CI artifacts, a shared viewer, or SCM
  inherits an artifact-hygiene surface where prompt text, variables, and raw
  model outputs all travel with them (the same files carry `outputs` as "Raw LLM
  responses" per the field table). Second, the qualifier "Non-sensitive" is the
  vendor's classification, not a guarantee the tool enforces: what counts as
  non-sensitive is exactly the judgement a team gets wrong when it routes real
  customer data through `config.env` or prompt variables. The honest reading is
  that, on the page's own disclosure, only JUnit XML (Claim 4) and CSV are not
  named as config-carrying — and CSV's field list is prefaced "Columns include:",
  so that is an absence of a warning, not a positive guarantee. Every full export
  should be treated as potentially containing production data. This claim
  underwrites contradiction issue #1534 (see Cross-References).

### Claim 6: Promptfoo's share and record-export paths carry an explicit "do not put secrets in shareable inputs" rule, and `promptfoo export eval` redacts config secrets while still warning that exports contain user data
- **Evidence**: Read from the linked **Sharing** page (`/docs/usage/sharing/`)
  opening paragraph and its "trusted configs" tip, and from the **Command line**
  page's `promptfoo export eval` section — both quoted verbatim below. These
  are *not* claims from the Output Formats page itself.
- **Confidence**: settled (documented product behavior; two independent pages
  agree)
- **Quote** (Sharing page): "Sharing uploads the eval/report snapshot needed to view the result. This can include prompts, vars, outputs, traces, metadata, provider configuration fields, media/blob references, scan artifacts, and derived artifacts. Do not put secrets in prompts, datasets, provider config fields, metadata, or other shareable inputs unless that field is documented as redacted." / "Config-supplied sharing endpoints are trusted. Only accept or run configs with `sharing.apiBaseUrl` / `sharing.appBaseUrl` from sources you trust, because sharing sends the eval snapshot to the configured endpoint."
- **Quote** (Command line page, `promptfoo export eval`): "Exports always redact config secrets before writing." and "Eval exports can still contain user data in prompts, outputs, variables, traces, and opt-in media. Inspect an export before sharing it."
- **Our assessment**: Buy it — this is the strongest single piece of
  corroboration that the leakage surface in Claim 5 is real and known to the
  vendor rather than an inference. Three separate surfaces (file export, cloud
  share, record export) each carry an explicit secrets warning, and the
  "unless that field is documented as redacted" phrasing is notable: it does not
  promise redaction, it enumerates which fields are documented as redacted. The
  self-hosted `sharing.apiBaseUrl` tip adds a distinct failure mode worth
  carrying: eval snapshots are exfiltrated to whatever endpoint a config file
  names, so a `promptfooconfig.yaml` is itself a data-egress control and must be
  treated as trusted input (this is the same class of concern as the corpus's
  existing "config file as attack surface" material). Note the asymmetry worth
  flagging for the guide: `promptfoo export eval` says it "always redact[s] config
  secrets," whereas the Output Formats page calls redaction "best-effort (not
  comprehensive)" — these are different code paths (record export vs `--output`
  format writer) rather than a documented conflict, so this note records both
  wordings rather than picking one.

### Claim 7: JSONL is the documented answer to both very large evaluations and a JSON export that fails with memory errors — one self-contained JSON object per line, streamed rather than parsed whole
- **Evidence**: The "JSONL Format" section's `Use when:` line and the
  "Performance Tips" list.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Use when: Working with very large evaluations or when JSON export fails with memory errors." / "1.  **Use JSONL for large datasets** - avoids memory issues"
- **Our assessment**: Buy it. This is a capacity fact stated plainly by the
  vendor: the natural format (one big JSON document, `results.outputs` and all)
  has a memory ceiling, and the documented escape hatch is a line-delimited
  format the same CLI writes. The operational consequence is that **format choice
  is a function of eval size**, not just of consumer preference — a team that
  picks JSON because it is convenient can hit an OOM mid-eval and lose the run,
  and the fix is not "bigger runner" but "different format plus a streaming
  reader." For the guide this pairs with the repo-scale conditioning pattern the
  corpus already uses elsewhere: the same harness config needs a different output
  format at different eval sizes.

### Claim 8: `gradingResult` and `componentResults` are both optional on a JSONL row — the page's own worked example includes `"gradingResult":null`, and the documented reader uses `row.gradingResult?.componentResults ?? []` to tolerate both the null case and rows with no nested sub-results
- **Evidence**: The two-row JSONL sample (row `testIdx:1` ends `"gradingResult":null`),
  the paragraph that follows it, the streaming-reader snippet, and the sentence
  that explains the operator.
- **Confidence**: settled (documented schema behavior; checkable against the
  published sample)
- **Quote**: "Both `gradingResult` and `componentResults` may be absent on error rows or rows without assertions." / "`?.` and `?? []` together cover the `gradingResult: null` case shown above and rows where a single top-level assertion produced no nested `componentResults`."
- **Our assessment**: Buy it, and this is the most concrete footgun on the page
  for anyone building reporting on top of promptfoo exports. The page's own
  example data contains the trap: a consumer that writes
  `row.gradingResult.componentResults.map(...)` crashes on the second row of the
  documented sample. Two distinct causes produce the absence — an **error row**
  (the provider call failed, so there is nothing to grade) and a **row with no
  assertions at all** — and a consumer that conflates them will report an
  infrastructure fault as a grading failure, or drop the row entirely and
  silently shrink its denominator. The `?? []` fallback additionally loses the
  distinction between "no assertions" and "assertions that produced no
  sub-results," so the report needs the row-level `success`/`error` signal to
  avoid turning missing evidence into a clean line item. This is a small
  documented example that encodes a large class of eval-reporting bug.

### Claim 9: The assertion-failure/error split is a first-class product concept beyond JUnit — CLI filters separate them, a dedicated subcommand retries only errors, and both timeout knobs convert timeout into the error state
- **Evidence**: The **Configuration Reference** page's `evaluateOptions.timeoutMs`
  and `evaluateOptions.maxEvalTimeMs` rows and its `filterErrorsOnly` /
  `filterFailing` / `filterFailingOnly` rows, plus the **Command line** page's
  `--filter-failing-only` option and the `promptfoo retry <evalId>` /
  `promptfoo eval --retry-errors` entries. Read from those two sub-pages, not
  from the Output Formats page.
- **Confidence**: settled (documented product behavior, three separate surfaces)
- **Quote** (Command line page, the `--filter-failing-only` row of the `promptfoo eval` options table): "Filter tests that had assertion failures in a previous eval, excluding errors"
- **Quote** (Configuration Reference): "Timeout in milliseconds for each individual test case/provider API call. When reached, that specific test is marked as an error. Default is 0 (no timeout)." and "Maximum total runtime in milliseconds for the entire evaluation process. When reached, all remaining tests are marked as errors and the evaluation ends. Default is 0 (no limit)."
- **Our assessment**: Buy it — this materially strengthens Claim 3 from "one
  output format happens to use two element names" to "the harness maintains a
  persistent failed-vs-errored distinction that three independent surfaces expose."
  It matters for two reasons. (a) A CI gate that only counts total failures
  cannot separate a model-quality regression from an infrastructure flake, and
  the vendor's own tooling is built around making that separation possible —
  including `promptfoo retry`, which re-runs *only* ERROR results in place while
  preserving the originals if the retry fails, i.e. retry-the-flakes without
  re-paying for the assertions that already failed. (b) `maxEvalTimeMs` is a
  quiet footgun in the other direction: a global eval timeout converts *every
  remaining test* into an error, so a CI runner that is merely slow can turn a
  partially-graded suite into a wall of errors — and per Claim 8 those rows carry
  `gradingResult: null`, so the reports built on top of them show infrastructure
  failures, not quality failures. The pair (timeout → error state) and
  (error state → null gradingResult → parser crash) is a chain worth stating
  explicitly in the guide.

### Claim 10: CI gating is exit-code based and the exit code carries three independent failure modes — a per-test failure, an aggregate pass-rate threshold (`PROMPTFOO_PASS_RATE_THRESHOLD`), and any other error (exit 1) — and the failure exit code is itself overridable via `PROMPTFOO_FAILED_TEST_EXIT_CODE`
- **Evidence**: The **Command line** page's `promptfoo eval` closing paragraph and
  the `PROMPTFOO_FAILED_TEST_EXIT_CODE` / `PROMPTFOO_PASS_RATE_THRESHOLD` rows in
  its environment-variable table. Read from that sub-page, not from the Output
  Formats page.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `eval` command will return exit code `100` when there is at least 1 test case failure or when the pass rate is below the threshold set by `PROMPTFOO_PASS_RATE_THRESHOLD`. It will return exit code `1` for any other error. The exit code for failed tests can be overridden with environment variable `PROMPTFOO_FAILED_TEST_EXIT_CODE`."
- **Our assessment**: Buy it, and flag the third clause. Two independent and
  easily-conflated facts live in one sentence: exit `100` fires both for "at
  least one test failed" and for "no test failed but aggregate pass rate is
  below a threshold" — so a suite can be all-green per-case and still fail the
  gate, which is a legitimate design (a quality floor over many samples) but
  means `100` does not localise. Worse, and this is the operational teeth:
  `PROMPTFOO_FAILED_TEST_EXIT_CODE` can be set to make a failing eval exit `0`.
  A gate whose pass/fail is one environment variable away from green is not a
  gate. Combined with the corpus's existing finding that the eval cache is
  enabled by default (`docs-promptfoo-configuration-caching.md` Claim 9), the
  honest statement is that a promptfoo CI gate's greenness is a function of four
  ambient settings — `PROMPTFOO_CACHE_ENABLED`, `PROMPTFOO_PASS_RATE_THRESHOLD`,
  `PROMPTFOO_FAILED_TEST_EXIT_CODE`, and the provider credentials selecting the
  grader — none of which are visible in the JUnit artifact the gate produces.

### Claim 11: `txt` and `yml` are accepted output formats and are named as config-carrying, but neither has an "Available Formats" section — the format inventory is nine-wide in the CLI and seven-wide on the page
- **Evidence**: The CLI flag description and the Configuration Reference's
  `commandLineOptions.output` row both enumerate nine extensions; the page's
  "Available Formats" section documents seven; and the redaction warning
  (Claim 5) names `txt` and `yml` among the config-carrying formats.
- **Confidence**: settled (both enumerations are explicit on the pages)
- **Quote**: "Path(s) to output file (csv, txt, json, jsonl, yaml, yml, html, xml, junit.xml)"
- **Our assessment**: Buy it as a small but real coverage gap, with a security
  consequence. A reader who trusts the page's seven-section inventory to decide
  what is safe to publish can conclude `txt` is not an output format at all —
  when in fact `txt` *is* accepted, and the page's own redaction warning names
  it as one of the formats that carries the eval `config`. The undocumented
  formats are precisely the ones with no "Use when:" guidance to steer a reader
  away from them. The guide should enumerate the format→consumer→exposure table
  from the CLI's nine-extension list rather than from the page's section list,
  and treat `txt` as a full export until proven otherwise.

### Claim 12: The vendor's own artifact-hygiene recipe is to gitignore the full exports and keep only the CSV summary — which happens to be the other non-config-carrying format
- **Evidence**: The "3. Version Control Considerations" `.gitignore` block and
  the "Organize Output Files" tree.
- **Confidence**: settled as documented advice; **emerging** as a consistent
  policy (the page never links the two together explicitly — see Our assessment)
- **Quote** (from the `.gitignore` block, the retention comment): "# But keep summary reports!"
- **Our assessment**: Buy the advice and note the alignment the page does not
  spell out. The recipe excludes `html` and `json` from version control and
  retains `summary-*.csv` — and per Claim 5 CSV is one of only two documented
  formats not named as embedding the eval `config`. So the vendor's default
  hygiene advice and its exposure disclosure happen to agree on the same
  allow/deny split. Two caveats for the guide: the `.gitignore` guidance covers
  SCM only and says nothing about CI build artifacts, which is where the
  `--output` files usually land; and "But keep summary reports!" invites
  committing an artifact produced by the very run that Claim 8 says may carry
  `gradingResult: null` error rows, so a committed summary can encode
  infrastructure faults as if they were quality results. The page's
  `sharing.includeRawOutputs: false` knob is the documented mitigation for
  artifact size but, per the Sharing page (Claim 6), is not a redaction control.

## Concrete Artifacts

### JUnit XML shape (verbatim from the "JUnit XML Format" section)

```xml
<testsuites tests="2" failures="1" errors="0" time="0.840">
  <testsuite name="[openai:gpt-4.1] prompt 1" tests="2" failures="1" errors="0" time="0.840">
    <testcase name="test 1: greets the customer" classname="[openai:gpt-4.1] prompt 1" time="0.420" />
    <testcase name="test 2: refuses refunds outside policy" classname="[openai:gpt-4.1] prompt 1" time="0.420">
      <failure message="Assertion failed">Score: 0Reason: Assertion failedFailed assertions:- contains</failure>
    </testcase>
  </testsuite>
</testsuites>
```

Note the `<failure>` body: it is the three-line summary, with the assertion *type*
(`contains`) but not its *value*, and no config, prompt, or variable.

### The compactness contract (verbatim bullet list, "JUnit XML Format" section)

```
JUnit XML intentionally stays compact:

-   one `testsuite` per prompt/provider pair so CI groups related cases together
-   one `testcase` per eval result so every promptfoo test appears in CI
-   `failure` for failed assertions and `error` for provider/runtime errors so CI can distinguish incorrect behavior from execution problems
-   concise failure/error summaries only; use JSON, HTML, or Promptfoo XML when you need assertion reasons, provider errors, prompts, variables, raw model outputs, or full config
```

### Two-row JSONL sample (verbatim, "JSONL Format" section) — note `gradingResult` is null on the second row

```json
{"testIdx":0,"promptIdx":0,"success":true,"score":1.0,"response":{"output":"Response 1"},"gradingResult":{"pass":true,"score":1.0,"reason":"All assertions passed","componentResults":[{"pass":true,"score":1.0,"reason":"Expected output to contain \"hello\"","assertion":{"type":"contains","value":"hello"}}]}}
{"testIdx":1,"promptIdx":0,"success":false,"score":0.0,"response":{"output":"Response 2"},"gradingResult":null}
```

### Streaming reader for assertion-level detail (verbatim, "JSONL Format" section)

```js
import fs from 'node:fs';
import readline from 'node:readline';

const rl = readline.createInterface({
  input: fs.createReadStream('results.jsonl', { encoding: 'utf8' }),
  crlfDelay: Infinity,
});

for await (const line of rl) {
  if (!line.trim()) {
    continue;
  }
  const row = JSON.parse(line);
  for (const component of row.gradingResult?.componentResults ?? []) {
    console.log({
      type: component.assertion?.type,
      pass: component.pass,
      score: component.score,
      reason: component.reason,
    });
  }
}
```

Two independent null-guards are required and neither is optional: `?.` for
`gradingResult: null`, and `?? []` for a present `gradingResult` with no
`componentResults`. Note also that this reader silently yields zero lines for a
failed/error row — the null-tolerance that prevents a crash also means an
all-error file produces an empty, non-alarming report.

### Config-carrying formats — the redaction warning (verbatim, "Structured Output Fields")

```
warning

`json`, `yaml`, `yml`, `txt`, `html`, and Promptfoo XML outputs include the eval
`config`. Sensitive fields are redacted using Promptfoo's sanitizer rules on a
best-effort basis (not comprehensive). Non-sensitive `config.env` values may
still appear in exports.
```

### Output path and multi-format emission (verbatim, "Configuration Options")

```yaml
# promptfooconfig.yaml
# Specify default output file
outputPath: evaluations/latest_results.html
prompts:
  - '...'
tests:
  - '...'
```

```bash
# Command line
promptfoo eval --output results.html --output results.json

# Or use shell commands
promptfoo eval --output results.json && \
promptfoo eval --output results.csv
```

`--output` is repeatable, so the lossy CI format and the full export can be
emitted in one invocation. The shell form shown re-runs the eval (a second paid
run) rather than emitting both formats from one.

### Artifact hygiene: directory layout, filenames, and `.gitignore` (verbatim, "Best Practices")

```
project/
├── promptfooconfig.yaml
└── evaluations/
    ├── 2024-01-15-baseline.html
    ├── 2024-01-16-improved.html
    └── comparison.json
```

```bash
# Include date and experiment name
promptfoo eval --output "results/$(date +%Y%m%d)-gpt4-temperature-test.html"
```

```
# .gitignore
# Exclude large output files
evaluations/*.html
evaluations/*.json
# But keep summary reports!
evaluations/summary-*.csv
```

### Output-path default for large evals (verbatim, "Troubleshooting > Large Output Files")

```yaml
# Limit output size
outputPath: results.json
sharing:
  # Exclude raw outputs from file
  includeRawOutputs: false
```

### CI gate exit codes and format list (verbatim, Command line page — `promptfoo eval`)

```
-o, --output <paths...>            Path(s) to output file (csv, txt, json, jsonl, yaml, yml, html, xml, junit.xml)
--filter-failing <path or id>      Filter tests that failed in a previous eval (by file path or eval ID)
--filter-failing-only <path or id> Filter tests that had assertion failures in a previous eval, excluding errors
--filter-errors-only <path or id>  Filter tests that resulted in errors in a previous eval
--no-cache                         Do not read or write results to disk cache
--retry-errors                     Retry all ERROR results from the latest eval
```

```
The `eval` command will return exit code `100` when there is at least 1 test case
failure or when the pass rate is below the threshold set by
`PROMPTFOO_PASS_RATE_THRESHOLD`. It will return exit code `1` for any other error.
The exit code for failed tests can be overridden with environment variable
`PROMPTFOO_FAILED_TEST_EXIT_CODE`.
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/outputs/
for the sections as noted, plus https://www.promptfoo.dev/docs/usage/command-line/
for the last two blocks (explicitly attributed in-line). Code blocks arrive as
single lines after HTML extraction; line breaks were restored at comment and
statement boundaries only — no wording changed. The last two blocks additionally
render two-column option tables as aligned lines (option, then its description
verbatim); the descriptions are unaltered.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-code-scan-cli.md` **Claim 9** ("`skipReason` is
    set when a scan is intentionally skipped (e.g. fork PR awaiting maintainer
    approval), in which case `comments` is empty — an empty result is not a clean
    result") and `source-notes/docs-promptfoo-code-scan-github-action.md`
    **Claim 5** ("SARIF output is only published when a scan actually completes —
    an intentionally skipped scan does not publish a clean Code Scanning result").
    Both verified by re-reading the cited notes. The JUnit `failure`/`error`
    split (Claim 3) is the same discipline applied on the eval-result side: a
    harness that can distinguish "the check ran and the system is wrong" from
    "the check could not run" is the shared property, and the corpus previously
    carried it only for the *security scanner* output path. The two families now
    agree on the rule, which is what makes it a guide-level principle rather than
    a vendor quirk. (Both notes are also already cited into
    `guide/06-security-and-trust.md` §"Gating on LLM security scans", which
    states the rule as "Gate on the scan's completion signal, never on its
    findings count.")
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 7** ("`{{ env.X }}`
    is resolved at **config load time, not runtime**, can therefore control file
    paths and API keys, and the vendor explicitly warns that putting secrets in
    `config.env` 'resolves the secret into the eval config object and may appear in
    exported results'"). Verified by re-reading the note. This page's redaction
    warning (Claim 5) is the *downstream half* of the same warning: even with the
    sanitizer applied, "`config.env` values may still appear in exports." Together
    they close the loop from materializing a secret into the config object to that
    secret's appearance in a file.
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** ("Pre-deployment
    red teaming must be integrated into CI/CD pipelines and run on a recurring
    schedule because LLM application changes have nondeterministic consequences").
    Verified by re-reading the note. That note established *that* LLM checks belong
    in CI; this page documents the wire format that makes it a check rather than a
    report, and is the mechanism the OWASP recommendation was missing.

- **Contradicts** (existing filed contradiction, not filed again):
  - Issue **#1534** (open, `contradiction` label) — "promptfoo config.env secret
    handling: configuration/guide warns against `{{ env.X }}` API-key templates (may
    leak into exported results) vs modular-configs' 'Environment-Specific
    Configurations' example is exactly that pattern (`env:
    file://configs/env-prod.yaml`)". This page's Claim 5 is **evidence on Side A
    of #1534**: it is the outputs surface where the leaked value lands, from the
    vendor's own redaction warning. Side B is `source-notes/docs-promptfoo-modular-configs.md`
    **Claim 4** ("`env:` is loadable from a file (`env: file://configs/env-prod.yaml`)
    and its entries are templated from the process environment
    (`OPENAI_API_KEY: '{{ env.OPENAI_API_KEY_PROD }}'`) — the documented
    per-environment credential indirection"). Both cited notes re-read and
    verified. **No new contradiction issue was filed** per MINER.md §4a: the
    `config.env` leakage conflict is already filed, and this page's contribution
    is corroboration rather than a second, opposing claim. The one genuinely new
    wrinkle for #1534 is that this page qualifies the exposure as "Non-sensitive
    `config.env` values may still appear" — a narrower wording than
    configuration/guide's "may appear in exported results" for secrets, and the
    narrowing is the vendor's own classification rather than an enforced
    guarantee. That nuance strengthens Side A rather than splitting the sides, so
    it belongs as a comment on #1534, not as a new issue.
  - No other contradiction identified. Verified against `CONTRADICTIONS.md` (no
    `C-NNN` entries appended) and all open `contradiction`-labeled issues. The
    two live tensions found are **not** contradictions: (a) `promptfoo export
    eval` says it "always redact[s] config secrets" while this page calls the
    sanitizer "best-effort (not comprehensive)" — different code paths (record
    export vs `--output` format writer), no guidance conflict for a reader;
    recorded in Claim 6 rather than adjudicated. (b) `txt`/`yml` appear in the
    CLI's extension list and in this page's redaction warning but have no
    "Available Formats" section — an omission in one page, not two sources
    disagreeing; recorded as Claim 11.

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-caching.md` — the sibling runtime
    page (#1275). This page's output surface is the other half of that note's
    argument: the cache decides *whether* the gate ran against live model
    behavior, and this page documents *what the gate's verdict looks like*
    downstream. The two compose into a single statement the guide can make —
    a green JUnit report is evidence only if the run was uncached *and* the exit
    code was not overridden (Claim 10) *and* the viewer preserved the
    failure/error distinction (Claim 3). Nothing in the JUnit artifact itself
    records any of those three conditions.
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 10**
    ("`GradingResult` supports nested `componentResults` that render as an
    assertion-details table in the Eval view modal, plus `namedScores` in the
    worked example — nested sub-results are inspectable rather than opaque").
    Verified by re-reading the note. That note establishes that `componentResults`
    is the assertion-level detail structure; this page establishes that it is
    **optional** on an exported row (Claim 8). The two together mean the same
    field is guaranteed in the UI and absent-by-contract in the file — so a
    report built on exports must treat the UI as the authoritative rendering and
    the export as the lossy one.
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 9** ("Already-captured
    LLM outputs can be scored offline via `promptfoo eval --assertions
    asserts.yaml --model-outputs outputs.json` — a post-hoc replay path for
    running a gate over production traffic that was recorded, not generated at
    eval time"). Verified by re-reading the note. That is a way to *produce* eval
    verdicts from captured traffic; this page is a way to *serialize and gate*
    them. The provenance hook that note flags (`tags` per output) is exactly what
    has to survive into the artifact — and per Claim 4 the JUnit format drops
    config and variables, so provenance must be carried in the file name or the
    suite/test naming convention, not in the report body.
  - `source-notes/blog-pagerduty-sre-agent-triage.md` **Claim 1** ("LLM-as-a-judge
    eval alerts redefine the triage signal — 'something might be broken' changes
    what a responder is supposed to do at 2 a.m. versus a traditional broken-service
    alert"). Verified by re-reading the note. This page supplies the missing
    mechanical half: the `failure`/`error` split and `--filter-errors-only` /
    `promptfoo retry` are how the "something might be broken" signal is sorted
    into the two queues that note says a responder has to distinguish — model
    quality vs execution fault — before it reaches a human.
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` — adjacent eval
    methodology (that note's Claims 1, 3, 12 are all about a metric lacking a
    stable unit). This page is the serialization counterpart: it documents the
    `version: 3` field on the JSON export, which is the format-level version
    marker a consumer should check before trusting field names — the export-side
    version discipline that note argues for on the metric side. Not cited by claim
    number because the specific claims were not needed here.

- **Novel**: This is the first corpus source on **how eval results are
  serialized and consumed by a CI gate** — `grep -ril junit source-notes/ guide/`
  returns zero hits before this note, and `outputPath` likewise. Specifically new:
  1. **JUnit XML as the CI-gating bridge**, including the concrete consumer list
     (GitLab / Azure Pipelines / Bitbucket Pipelines / Jenkins) and the structural
     contract of one `testsuite` per prompt/provider pair and one `testcase` per
     result (Claims 1–2).
  2. **The failure-vs-error split as an exported, consumer-visible signal**
     (Claim 3), plus the evidence that it is product-wide rather than
     format-local — three CLI filters, a dedicated `promptfoo retry` subcommand,
     and both timeout knobs all read the same distinction (Claim 9).
  3. **A vendor-stated artifact-exposure-control design** — CI reports are
     deliberately not full exports, justified so they "do not become a second
     full export surface" (Claim 4). The guide has no other citation for the
     general principle that a widely-retained CI artifact should be minimised at
     the format boundary.
  4. **The full-export leakage surface and its explicitly incomplete sanitizer**
     (Claim 5), corroborated across three vendor surfaces including the Share
     path's "do not put secrets in ... shareable inputs" rule (Claim 6). Ch06 has
     no other source on credential exposure through eval tooling.
  5. **Export-format failure modes as an ops concern**: JSONL as the documented
     answer to a JSON-export OOM (Claim 7), the `gradingResult: null` /
     missing-`componentResults` parser footgun visible in the page's own sample
     data (Claim 8), and the exit-code contract including the
     `PROMPTFOO_FAILED_TEST_EXIT_CODE` override (Claim 10).
  6. **`outputPath` in `promptfooconfig.yaml` vs repeated `--output` flags**, and
     the fact that `--output` is repeatable so a lossy gate artifact and a full
     export can be produced in one run (Concrete Artifacts).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — add a new section on how an eval gates a
  pipeline, immediately after "Staging-gated main with live API testing"**: that
  section currently says CI must gate on "live LLM API testing" but never says how
  the result reaches CI. Add: emit JUnit XML via `promptfoo eval --output
  results.junit.xml` and publish it to the existing test-report surface rather
  than building a bespoke dashboard (Claim 1); rely on the one-`testsuite`-per-
  prompt/provider-pair grouping so a per-model regression is legible, and treat
  "every promptfoo test appears in CI" as a coverage guarantee worth stating
  (Claim 2). Cite this note as the source.
- **Chapter 05 — extend the existing "A green eval is not evidence until you can
  name what it measured" section** (`guide/05-llm-ops-reliability.md` line ~567,
  which currently rests on `docs-promptfoo-configuration-caching` alone). Add
  the second and third ways a green gate is unearned: the exit code is `100` both
  for a per-test failure *and* for an aggregate pass rate below
  `PROMPTFOO_PASS_RATE_THRESHOLD`, and `PROMPTFOO_FAILED_TEST_EXIT_CODE` can
  override it to `0` (Claim 10). Net rule to state: a promptfoo gate's greenness
  is a function of at least four ambient settings — `PROMPTFOO_CACHE_ENABLED`,
  `PROMPTFOO_PASS_RATE_THRESHOLD`, `PROMPTFOO_FAILED_TEST_EXIT_CODE`, and the
  provider credentials that select the grader — and **none of them is visible in
  the JUnit artifact**, so the artifact alone is not evidence of what ran.
- **Chapter 05 — add the failure-vs-error distinction to the flaky-gate
  discussion**: document that `failure` is a model-quality verdict and `error` an
  execution fault, that the split is product-wide (`--filter-failing-only` is
  documented as "excluding errors", `promptfoo retry` re-runs only ERROR results
  in place), and that a global `maxEvalTimeMs` converts *every remaining test*
  into an error so a slow runner manufactures errors (Claims 3, 9). Add the
  caveat honestly: the format carries the distinction; whether a given CI viewer
  preserves it is unverified and must be checked per viewer.
- **Chapter 06 (Security and Trust) — add a subsection under "Data governance
  for AI workloads" or "Red-teaming as a CI gate"**: full exports are not safe to
  publish. `json`, `yaml`, `yml`, `txt`, `html`, and Promptfoo XML all embed the
  eval `config` under a sanitizer the vendor calls "best-effort (not
  comprehensive)", with `config.env` values possibly still present, and the same
  files carry raw model outputs and prompt variables (Claim 5). Cross-reference
  contradiction #1534 for the `{{ env.X }}` materialization side. Rule to state:
  the CI gate artifact should be JUnit XML precisely because it is the one format
  the vendor built to be a summary rather than a second full export surface
  (Claim 4), and every fuller export is a data-egress decision that must be
  reviewed like any other.
- **Chapter 06 — add the share/export trust boundary**: `promptfoo share` uploads
  a snapshot that can include prompts, vars, outputs, traces, metadata, provider
  config fields and media references, with the rule "Do not put secrets in
  prompts, datasets, provider config fields, metadata, or other shareable inputs
  unless that field is documented as redacted", and a `promptfooconfig.yaml` that
  sets `sharing.apiBaseUrl` redirects that whole snapshot to whatever host it
  names (Claim 6). Rule to state: treat an eval config that sets sharing
  endpoints as trusted input, at the same trust level as a deploy script.
- **Chapter 03 (Runbooks and Agents) — CI pipeline runbook, artifact handling**:
  add the `.gitignore` recipe (exclude `evaluations/*.html` and
  `evaluations/*.json`, keep `evaluations/summary-*.csv`) plus the caveat that it
  covers SCM only and not CI build artifacts (Claim 12), and the JSONL parsing
  rule for report builders: tolerate `gradingResult === null` and missing
  `componentResults` on both error rows and assertion-free rows, and never infer
  "no failures" from an empty `componentResults` (Claim 8).

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/outputs/). Per MINER.md §1, three
  linked sub-pages were also read because claims depend on them, and each is
  attributed in-line rather than blended into the primary source:
  1. **Configuration Reference** (`/docs/configuration/reference/`) — for
     `evaluateOptions.timeoutMs` / `maxEvalTimeMs` (Claim 9), the
     `commandLineOptions.output` extension list (Claim 11), and the
     `filterErrorsOnly` / `filterFailing` / `filterFailingOnly` rows (Claim 9).
  2. **Command line** (`/docs/usage/command-line/`) — for the exit-code contract
     and `PROMPTFOO_FAILED_TEST_EXIT_CODE` / `PROMPTFOO_PASS_RATE_THRESHOLD`
     (Claim 10), the `-o, --output` extension list (Claim 11), the
     `--filter-failing-only` wording (Claim 9), `promptfoo retry` / `--retry-errors`
     (Claim 9), and `promptfoo export eval`'s redaction warning (Claim 6).
  3. **Sharing** (`/docs/usage/sharing/`) — for the share-surface secrets rule and
     the trusted-config-endpoints tip (Claim 6). This page is *not* linked from
     the Output Formats page's "Related Documentation" block; it was reached
     because the Output Formats page's `sharing.includeRawOutputs` remediation
     points at that surface, and it is where the vendor states the secrets rule
     most explicitly.
  Not followed: `/docs/category/integrations/` (a category index, no eval-output
  content), and the per-format analysis snippets on the page itself were read but
  carry no ops claim (per the Prospector's caveat against writing notes for the
  HTML/CSV/YAML inventory sections — they get one line each in Concrete
  Artifacts only).
- The issue was auto-filed from the `promptfoo-docs` site-crawl seed and was
  triaged three times by the Prospector, all three agreeing on `triaged:text`,
  `medium` priority, Ch05 primary / Ch06 secondary, and on the extractable set
  (JUnit CI bridge, export failure modes, redaction caveat). All four of the
  Prospector's named extraction targets are covered: JUnit XML and its
  failure/error split (Claims 1–4), JSONL as the memory-safe path with the
  streaming reader and null-`gradingResult` nuance (Claims 7–8), redaction and
  `config.env` leakage across three surfaces (Claims 5–6), and format selection
  plus `outputPath` / repeated `--output` (Claim 11 + Concrete Artifacts).
- `confidence_overall` is `emerging`: this is vendor product documentation, so
  the format shapes, field lists, CLI flags, and exit codes are authoritative and
  individually settled — but there are **no measured artifact sizes, no
  redaction test results, no CI-viewer compatibility evidence, and no independent
  validation** of the "stays compact" rationale. Two claims are explicitly marked
  emerging-within-the-note for that reason: Claim 3 (the viewer-preservation half
  of the failure/error guarantee) and Claim 12 (the page never links its
  `.gitignore` advice to its own redaction disclosure; the alignment is our
  reading).
- **Candidate review** (from `miner-related-notes.md`, read before Cross-References
  per MINER.md §4; the file was not committed). Each of the 10 candidates was
  cited or dismissed by name:
  1. `docs-promptfoo-pi-scorer.md` — **dismissed**. Sibling
     `configuration/expected-outputs/` page about a model-graded scorer
     (`WITHPI_API_KEY`, threshold `0.5`); no export, serialization, or CI-gating
     content. Its only tangential overlap is the external-credential theme, which
     belongs to Claim 5's `config.env` story and is better carried by #1534.
  2. `docs-google-sre-team-lifecycles.md` — **dismissed**. Google SRE org
     design (hiring, team topology, SLOs-with-consequences); unrelated to eval
     output formats.
  3. `blog-promptfoo-owasp-red-teaming.md` — **cited** (Corroborates,
     **Claim 4**, verified): the note that says LLM red teaming belongs in CI/CD,
     which this page supplies the wire format for.
  4. `docs-litellm-batches-api.md` — **dismissed**. Both sources use JSONL, but
     that note is about batch-API request accounting and rate limiting on the
     *request* side; this page's JSONL is the *result* side. The shared surface
     ("JSONL") is a serialization choice, not a claim overlap — reading them
     together would conflate what a JSONL line means in each.
  5. `blog-pagerduty-sre-agent-triage.md` — **cited** (Extends, **Claim 1**,
     verified): the triage-signal note whose "something might be broken"
     distinction this page's `failure`/`error` split mechanises.
  6. `docs-promptfoo-classifier-grading.md` — **dismissed**. Grader
     implementation detail (`apiEndpoint`, gated HF repos, threshold
     recalibration); no serialization or CI-gate content.
  7. `docs-promptfoo-javascript-assertions.md` — **cited** (Extends, **Claim 10**,
     verified): establishes `componentResults` as the assertion-detail structure
     that this page shows to be optional on an exported row.
  8. `docs-promptfoo-llm-rubric.md` — **dismissed**. Audio-grading contract and
     judge-model selection; unrelated to how results are written out. Its
     `renderedGradingPrompt` observability caveat has no bearing on export
     fidelity.
  9. `docs-langfuse-mcp-server.md` — **dismissed**. Different vendor, docs-MCP
     plumbing; nothing about eval results or CI.
  10. `docs-google-sre-eliminating-toil.md` — **dismissed**. Toil taxonomy and
     the 50% operational-work cap; the CI-gate theme is shared with the corpus but
     that note makes no claim about eval artifacts.
  Additional cross-references found by searching `source-notes/` directly (not in
  the candidate list), each verified per MINER.md §4b by re-reading the cited
  note and confirming the claim number:
  `docs-promptfoo-code-scan-cli.md` Claim 9, `docs-promptfoo-code-scan-github-action.md`
  Claim 5 (Corroborates); `docs-promptfoo-configuration-guide.md` Claim 7 and
  `docs-promptfoo-modular-configs.md` Claim 4 (Corroborates / contradiction #1534
  sides); `docs-promptfoo-assertions-metrics.md` Claim 9 (Extends);
  `docs-promptfoo-configuration-caching.md` (Extends, by note-level scope
  description rather than claim number); `blog-promptfoo-asr-not-portable-metric.md`
  (Extends, note-level only — no specific claim cited, so no claim number is
  claimed for it).
- Verification discipline for quotes: every quoted passage was taken from the
  rendered page text fetched in this session and copied without tightening,
  reordering, or splicing non-adjacent sentences. Claims that combine more than
  one passage quote each passage separately rather than joining them into a
  single string. Code blocks in the source arrive as single lines after HTML
  extraction; line breaks were restored at comment and statement boundaries only.
  Where a claim's meaning is our synthesis across several source sentences
  (notably Claim 10's "one environment variable away from green" and Claim 12's
  allow/deny alignment), the synthesis is in **Our assessment** and the
  `Quote` field carries only the source's own contiguous words.
- No contradiction issue filed. Rationale in Cross-References: the one genuine
  `config.env` leakage conflict is already filed as #1534, and this page's
  contribution is corroboration of Side A; the other two live tensions are
  single-page omissions or distinct code paths, neither of which meets MINER.md
  §4a's "when to file" bar.