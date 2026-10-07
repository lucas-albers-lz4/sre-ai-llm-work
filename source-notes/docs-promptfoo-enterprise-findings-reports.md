---
source_url: https://www.promptfoo.dev/docs/enterprise/findings
source_type: docs
title: "Promptfoo Enterprise: Findings and Reports — Finding Disposition, the Export/Interop Matrix, and the Read-Only Findings Surface"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-07
date_extracted: 2026-10-07
last_checked: 2026-10-07
status: current
confidence_overall: emerging
issue: "#1610"
---

# Promptfoo Enterprise: Findings and Reports

> The vendor's specification of what happens to a red-team finding after a scan
> finishes: a three-value human disposition state machine (`Marked as Fixed` /
> `False Positive` / `Ignore`) with manual severity re-rating and comments, a
> four-format vulnerability export matrix whose novel member is a **Colang v1/v2
> → NVIDIA NeMo Guardrails** export that turns findings into runtime guardrails,
> a six-format eval export matrix whose novel members are Burp Suite payloads,
> DPO JSON, Human Eval Test YAML and a **failed-test-only config**, and a
> **read-only** programmatic surface (`GET /api/v1/results`, `promptfoo share`)
> — with no CI gating, no retention window, and no quantitative claim anywhere
> on the page.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Enterprise
  "Enterprise > Findings and Reports" page). The page opens with the gate
  "This feature requires Promptfoo Enterprise." Page footer: "Last updated on
  Oct 7, 2026 by mldangelo-oai" (the date and author are rendered in bold).
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own Enterprise application, so authoritative
  *as a specification* — the status values, export format names, filter keys,
  and endpoint path below are the vendor's own contract and are string-checkable
  by anyone with an Enterprise tenant. It is **not** measurement: the page
  publishes no metric, threshold, volume, latency, retention, or cost figure,
  and the feature is Enterprise-gated so none of it is verifiable in the
  open-source repository (see Extraction Notes).
- **Scope**: Covers how grading is scoped (application context at target
  creation), the dashboard and Vulnerabilities review surface, the vulnerability
  export matrix, point-in-time Reports and the evals drill-in, the eval export
  matrix, eval filtering/sorting, and the ways findings leave the platform
  (exports, PDF, API, `promptfoo share`). Does **not** cover CI gating or
  build-blocking, severity-level vocabulary, finding status transition rules or
  SLAs, who is attributed when a status/severity changes, retention, access
  control on findings, alerting, or any measurement of scan behavior.
- **Relationship to sibling pages**: this is the corpus's second coverage of a
  Promptfoo Enterprise surface, after
  `source-notes/docs-promptfoo-enterprise-audit-logging.md` (same Enterprise doc
  tree, same first-party-spec framing). No note exists for the findings /
  reports surface itself.

## Extracted Claims

### Claim 1: Red-team grading is stated to key on *application context supplied when creating a target* — the only statement on the page of what grading actually depends on, and the input is bound to the target object rather than to the scan
- **Evidence**: The "How Grading Works" section is three sentences: a definition
  of grading, the dependency statement, and a routing note saying where results
  are compiled. There is no other mention of grading
  inputs, target context, or versioning anywhere on the page, and no statement
  that the context is snapshotted per report.
- **Confidence**: settled as a statement of the documented dependency (the
  sentence is on the page); the reproducibility consequence below is our
  derivation, not a documented behavior
- **Quote**: "Grading is the process of evaluating the success of a red team attack. Promptfoo grades results based on the application context that is provided when creating a target."
- **Our assessment**: Buy the dependency, and treat it as a *pinning* question
  the page does not answer. Two consequences. (1) **The grading input lives on
  the target, not the scan** — so two reports of the same target at different
  times are only comparable if that application context did not change in
  between, and the page documents no versioning, no per-report snapshot, and no
  context hash that would let a reviewer establish it. "The grade moved" and
  "the target's declared context moved" are indistinguishable from this page
  alone, which is the same shape as the corpus's Ch05 rule that a green eval is
  not evidence until you can name what it measured. (2) The phrasing is notable
  for what it does *not* say: grading is not stated to key on the plugin
  configuration, the model version, or the probe set — only on application
  context. We do not read that as an exclusion (the page gives grading three
  sentences total, not a grading spec); we record it as *the only documented
  grading input*. Guide-safe formulation: **the documented grading context is
  target-creation-time application context, and its versioning is undocumented —
  so a finding's grade is not demonstrably reproducible from this page.**

### Claim 2: Vulnerability disposition is a closed three-value status set — "Marked as Fixed", "False Positive", "Ignore" — plus manual severity re-rating and free-text comments, all human-in-the-loop, with no documented transition rules, auto-closure, SLA, or actor attribution
- **Evidence**: The "Viewing Vulnerabilities" section states the status set and
  the two editable annotations verbatim. The page publishes no state diagram, no
  allowed-transition list, no default status, no reopening path, no clock, and
  no field recording who made the change.
- **Confidence**: settled (the status set and the two edit capabilities are
  stated verbatim; the absences are absences, recorded as such)
- **Quote**: "You can modify the status of the finding as either \"Marked as Fixed\", \"False Positive\", or \"Ignore\". You can also add comments to the finding to provide additional context about the vulnerability, as well as change the severity level of the vulnerability based on your company's risk assessment."
- **Our assessment**: Buy the state machine, and read it as the vendor handing
  the human half of triage to a person rather than to a policy — which is the
  right default for red-team findings (a "False Positive" call needs domain
  judgement) and the wrong thing to cite as an *operational* loop. Four things
  are missing that an SRE would ask for first: (a) **no `Reopened`/`Regressed`
  state**, so a "Marked as Fixed" finding that reappears on the next scan has no
  documented disposition other than being filed again; (b) **no transition
  rules** — nothing says a finding starts open, whether "Ignore" suppresses it
  from future scans or only from the view, or whether severity can be raised as
  well as lowered; (c) **no SLA or aging** — no "days open", no escalation, no
  link from a stale finding to anything; (d) **no actor attribution** on the
  change, which composes directly with `docs-promptfoo-enterprise-audit-logging.md`
  (its Concrete Artifacts → "No audit sink" section records webhook events
  `issue.status_changed`, `issue.severity_changed`, `issue.comment_added` —
  exactly these three edits, delivered externally, but no audit-log event for
  them). So the disposition *is* externally visible in real time via webhooks,
  yet the page itself documents no who/when on the record. The phrase "based on
  your company's risk assessment" also matters: severity is explicitly
  *org-relative*, which means severity is not comparable across two tenants and
  the guide must not treat a vendor severity number as an absolute.

### Claim 3: The finding detail view is a per-finding evidence bundle — exploit strategies, probe records, per-scan instances, and remediation recommendations — i.e. triage input is per-finding evidence, not an aggregate score
- **Evidence**: The second paragraph of "Viewing Vulnerabilities" enumerates
  four detail elements.
- **Confidence**: settled (enumerated on the page)
- **Quote**: "Selecting a vulnerability will open a finding that shows you the details of the vulnerability, including details about the types of strategies that were used to exploit the vulnerability, records of the probes that were used, the instances when the vulnerability was identified during scans, and remediation recommendations."
- **Our assessment**: Buy it, and note the one design property worth carrying to
  the guide: the vendor chose to attach the *probes* and the *strategies* to the
  finding, not just a severity label. That makes a disposition call reviewable
  against the actual adversarial input rather than against a summary — which is
  the same argument Ch06 already makes for testing the action path rather than
  only the text output. The phrase "the instances when the vulnerability was
  identified during scans" also implies a finding is *not* a single-scan object:
  one finding aggregates its occurrences across scans, which is what makes a
  persistent "Marked as Fixed" status meaningful across runs and is the
  unstated reason a `Reopened` state would matter (Claim 2). Caveat: the page
  documents no volume bound — how many probes or instances a finding carries,
  and whether they are sampled, is undocumented.

### Claim 4: The vulnerability export matrix is exactly four formats — CSV, SARIF, Colang v1, Colang v2 — and while SARIF is named for GitHub Security, SonarQube and "other DevOps platforms", the page documents no upload step, no CI job, and no build-blocking behavior
- **Evidence**: "Exporting Vulnerabilities" is a four-bullet list, each bullet a
  format with a one-sentence purpose. The words *CI*, *pipeline*, *gate*, *block*,
  *upload*, and *workflow* do not appear anywhere on the page; the SARIF bullet
  stops at "for integration with".
- **Confidence**: settled (the four-item list is exhaustive on the page; the
  CI-absence is an absence, stated per this corpus's convention)
- **Quote**: "Export as SARIF: Export vulnerabilities in SARIF format (Static Analysis Results Interchange Format) for integration with security tools like GitHub Security, SonarQube, and other DevOps platforms. SARIF is an industry-standard format for representing static analysis results."
- **Our assessment**: Buy the matrix; do **not** treat the SARIF bullet as new —
  the Prospector correctly scoped it as already owned
  (`docs-promptfoo-code-scan-cli.md` Claim 11 owns the CLI `--format sarif`
  surface, `docs-promptfoo-code-scan-github-action.md` Claim 5 owns the
  conditional-upload rule, and `guide/06-security-and-trust.md` §"Gating on LLM
  security scans" already carries the zero-finding gating warning). What *is*
  new here is the pairing: this is the **red-team findings** SARIF path, distinct
  from the code-scanner SARIF path the corpus already covers, and it has no
  documented equivalent of the `sarif-path` completion signal — so on this path
  the skipped-vs-clean ambiguity the guide warns about is unresolved. The larger
  point for the guide: the vendor's own story ends at "export ... for
  integration with", i.e. **the vendor documents the bridge and not the
  crossing**. Every gating decision on this data is the consumer's, which is
  exactly where the guide's existing completion-signal Rule belongs.

### Claim 5: Colang v1 and Colang v2 exports convert red-team findings directly into NVIDIA NeMo Guardrails guardrails — a findings-to-runtime-defense loop that is net-new to this corpus
- **Evidence**: Two dedicated bullets in "Exporting Vulnerabilities", each
  naming the Colang version and the NeMo Guardrails integration, with the v1
  bullet stating the purpose as implementing "defensive guardrails based on the
  vulnerabilities discovered during red team testing".
- **Confidence**: settled as a documented export capability (enumerated vendor
  contract); the round-trip quality of the generated guardrails is undocumented
  and unmeasured
- **Quote**: "Export as Colang v1: Export vulnerabilities as Colang 1.0 guardrails for integration with NVIDIA NeMo Guardrails. This format allows you to implement defensive guardrails based on the vulnerabilities discovered during red team testing."
- **Our assessment**: Buy the capability — it is the single most interesting
  thing on the page, and the reason this source is worth a note despite being a
  dashboard reference. Red-team findings and runtime guardrails are normally two
  disconnected artifacts: the scanner says "this probe got through", and
  separately someone writes a Colang rule. This export makes the finding itself
  the source of the rule, which closes the loop the guide has described only in
  prose. Three honest caveats before the guide cites it. (1) **The page
  documents no quality bar**: no statement of what a generated guardrail looks
  like, whether it is allow/deny/snippet form, how a "False Positive" finding
  affects the export, or whether export granularity is per-finding or
  per-scan. (2) **It is an export, not a deployment**: shipping Colang into a
  NeMo Guardrails runtime is the consumer's job, with all the review a new
  deny-rule deserves — a guardrail that blocks legitimate traffic is an
  availability incident, per Ch05's "A guardrail in the request path is an
  availability dependency". (3) There is **no reverse path documented**: nothing
  says a NeMo-guarded rejection feeds back into promptfoo findings. Treat this as
  a one-way bridge, and pair it with `docs-promptfoo-guardrails-assertions.md`
  Claim 1 — that note establishes the `guardrails` assertion is a *verdict
  reader*, not a runner; this claim is the corpus's first documented way to
  *produce* a real guardrail from eval evidence.

### Claim 6: The eval-level export matrix is six formats, four of which are specialized interchange artifacts — Burp Suite payloads, DPO JSON, Human Eval Test YAML, and a failed-test-only config
- **Evidence**: The eval export list under "Viewing Reports" is six bullets:
  CSV, JSON, Burp Suite Payloads, DPO JSON, Human Eval Test YAML, and the failed
  test config. This is a different list from the vulnerability export matrix
  (Claim 4) and is attached to individual eval results, not to findings.
- **Confidence**: settled (six-item list is exhaustive on the page); the
  *purpose* sentence of the Human Eval bullet is the page's weakest and is
  treated as such below
- **Quote**: "Download Burp Suite Payloads: Download the adversarial probes as payloads that can be imported into Burp Suite." / "Download DPO JSON: Download the eval results as a DPO JSON file." / "Download Human Eval Test YAML: Evaluate the eval results for performance in code-related tasks."
- **Our assessment**: Buy the list; grade the four specialized members
  differently. **Burp Suite payloads** is the operationally meaningful one: it
  takes promptfoo's adversarial probes and hands them to a traditional DAST
  toolchain, which is the cleanest documented bridge in the corpus from LLM
  red-teaming into conventional AppSec tooling — a probe that succeeded against
  the model becomes a payload replayed against the app. **DPO JSON** turns eval
  results into preference-pair training data, i.e. a remediation path that is
  model-weight-level rather than config-level; the page states no format detail,
  so we record the capability only. **Human Eval Test YAML** is the one to be
  careful with: the bullet's own description ("Evaluate the eval results for
  performance in code-related tasks") describes an action, not a format, and no
  schema is given — we read it as exporting results in a form consumable by
  code-generation benchmarks, but that reading is ours, not the vendor's, and the
  guide should not restate it as fact. **CSV/JSON** are the plain paths and are
  already covered generically by `docs-promptfoo-configuration-outputs.md`.

### Claim 7: The "failed test config" is a re-run artifact — a configuration file containing only the failed tests — so the documented remediation loop is *shrink the suite to the failures, fix, re-run* rather than *re-run everything*
- **Evidence**: The last bullet of the eval export list states the artifact and
  its purpose in one sentence.
- **Confidence**: settled (stated verbatim); the shape of the emitted file
  (whether it preserves providers, plugins, vars, and assertions, and whether
  pass-rate thresholds reset) is undocumented
- **Quote**: "Download the failed test config: Download a configuration file containing only the failed tests to focus on fixing just the tests that need attention."
- **Our assessment**: Buy it, and rate it higher than its position on the list
  suggests. This is the only artifact on the page that is a *workflow primitive*
  rather than an export format: it operationalizes a triage pattern the guide
  already recommends in prose — iterate on the failures rather than re-running
  the whole suite — and
  it does so with a file the user can commit, diff, and re-run. It also has a
  sharp edge the page does not mention: **a suite of only failing tests cannot
  report a regression in anything that used to pass**, so the failed-test config
  is a *debugging* artifact, never a *gate*. If a team wires it into CI as the
  suite, the gate becomes structurally incapable of failing on new breakage.
  The guide should state both halves together: use it to focus remediation, and
  never substitute it for the full suite in a gating context. Second-order note:
  because the artifact is generated from eval results, it inherits whatever
  secrets/PII the results carry — see `docs-promptfoo-configuration-outputs.md`
  Claim 5 (full exports carry `config`, redaction is "best-effort (not
  comprehensive)") and Claim 6 (the vendor's own "do not put secrets in
  shareable inputs" rule). The page makes no redaction claim for this artifact,
  so treat it as an unredacted export until proven otherwise.

### Claim 8: Reports are point-in-time PDFs per scan that summarize the most successful exploit strategies and most critical vulnerabilities, with a "View Logs" deep link into the evals section — reporting is a scan artifact, not a live view
- **Evidence**: The opening two sentences of the "Viewing Reports" section
  (what a Report is and what it is for) plus the Sharing section's PDF bullet.
- **Confidence**: settled (both statements are on the page)
- **Quote**: "Reports are point-in-time scans of your target that are generated when you run a scan. These reports can be used to review the findings from a specific scan." / "Download Vulnerability Reports: Download point-in-time vulnerability reports for each scan in the \"Reports\" section. These reports are exported as a PDF."
- **Our assessment**: Buy it, and note the two properties that matter for the
  guide. (a) **Reports are per-scan and immutable** — generated at scan time,
  exported as PDF — so a Report is a durable evidentiary artifact (good for the
  compliance-adjacent audience Ch06 addresses) but it is a *snapshot*: a finding
  dispositioned afterwards (Claim 2) will not be reflected in a previously
  generated PDF, so Report and Vulnerabilities view can legitimately disagree
  and the guide should say which one is authoritative for a given question
  (point-in-time posture vs current disposition). (b) The "View Logs" deep link
  is the documented join key between an aggregate Report and the underlying eval
  evidence, which is the chain a reviewer walks: report → scan → eval → probe →
  response → grading reason. The page documents no equivalent link in the other
  direction (finding → report), and no report scheduling, retention, or access
  control.

### Claim 9: The evals review surface supports a per-eval pass/failure flip, comments, report view and clipboard copy, filter/sort across eight keys, and a CSV download — the finest-grained human override on the platform is at the individual test-case level
- **Evidence**: The status/comment/report/copy sentence that ends the
  drill-in part of "Viewing Reports", plus the full "Filtering and Sorting
  Findings" paragraph with its eight enumerated keys.
- **Confidence**: settled (enumerated on the page)
- **Quote**: "You can modify the status of the finding as either a pass or failure, provide comments on the finding, view the vulnerability report associated with the eval result, and copy the eval result to your clipboard." / "The \"Evals\" section will display all of the evaluations and let you filter and sort through them based on the eval ID, date the scan was created, author, description, plugin, strategy, pass rate, or number of tests. You can then download the evals as a CSV file."
- **Our assessment**: Buy it, and extract the structural observation: promptfoo
  exposes **two independent human overrides at two different grains** — finding
  disposition (Claim 2, severity + status) and eval-result pass/failure (this
  claim) — and the page documents no reconciliation between them. A test case
  flipped to `pass` while its vulnerability stays undispositioned (or the
  reverse) is a state the page neither prevents nor flags. That is not
  necessarily wrong —
  the two objects answer different questions (did this probe succeed against
  the target vs is this a real vulnerability) — but it means **any derived
  metric ("pass rate", "open findings") is computed over data a human can edit
  at two levels**, and the guide's Ch05 discipline (name what a green number
  measured) should say so explicitly for this platform. The `author` sort key is
  also worth noting as a small positive: it implies eval results carry an author
  field, which is the attribution the audit log lacks (per the audit-logging
  note's Claim 3) — but the page documents no schema for it.

### Claim 10: The documented programmatic surface for findings is read-only — search via `GET /api/v1/results` and shareable URLs via `promptfoo share` — with no documented write API for status, severity, or comments, so the disposition state machine is UI-only
- **Evidence**: "Filtering and Sorting Findings" links search to the API
  reference's `GET /api/v1/results`; the Sharing section's final bullet names
  `promptfoo share`. No `POST`/`PATCH`/`PUT` endpoint appears anywhere on the
  page, and no section describes automating a status or severity change.
- **Confidence**: settled as a description of what this page documents; the
  write-API absence is an absence on *this* page — the linked API Reference is
  client-rendered and returns no retrievable body (verified 2026-10-07, same
  observation the audit-logging note recorded), so "undocumented" is the honest
  word, not "nonexistent"
- **Quote**: "You can also search for findings using Promptfoo's API." / "Share via URL: Generate shareable URLs for your evaluation results using the `promptfoo share` command. Learn more about sharing options."
- **Our assessment**: Buy the two named paths, and read the composition as the
  page's main operational limitation. **The read path is machine-accessible and
  the write path is not.** So a team can poll findings out of the platform and
  can share a URL into it, but cannot automate "if severity >= high and age > 7
  days then escalate" — the escalation lives in a human's browser tab unless it
  is reimplemented outside the product against the read API. Combined with
  Claim 2 (no SLA, no aging) and the webhook surface recorded in the
  audit-logging note (status/severity/comment *changes* are push-notified), the
  workable architecture is: **read via `GET /api/v1/results`, react via
  webhook, actuate outside promptfoo, and write the disposition back by hand** —
  a human-in-the-loop round trip the vendor has documented every read for and no
  write for. That is the sentence the guide should carry. Also flag the URL
  path itself: an API-reference deep link (`#tag/default/GET/api/v1/results`)
  whose target renders client-side cannot be cited as a contract, per the
  audit-logging note's Claim 9 rule ("a reference you cannot fetch cannot be
  cited").

### Claim 11: The page contains no CI gating, no severity-level vocabulary, no retention window, and no quantitative claim of any kind — it is a specification of a review surface, not of an operational loop
- **Evidence**: Full-page read: no occurrence of *CI*, *pipeline*, *gate*,
  *block*, *alert*, *SLA*, *retention*, or any number expressed as a measurement.
  Severity appears only as "severity level" with no enumerated values (the
  corpus's only promptfoo severity vocabulary is the code-scanner config
  `low|medium|high|critical`, on a different surface —
  `docs-promptfoo-code-scan-cli.md`, Concrete Artifacts → the
  `.promptfoo-code-scan.yaml` excerpt; its Claim 6 owns the `minSeverity` knob
  but does not enumerate the levels, so it is cited here by section name per
  MINER §4b). The page opens with the Enterprise gate.
- **Confidence**: settled as a description of what the page does and does not
  say (full-text read); the *product-level* absence of these features is not
  established by their absence from one page
- **Quote**: "This feature requires Promptfoo Enterprise."
- **Our assessment**: This is the calibration claim that governs how every
  other claim above may be cited, and it mirrors what the audit-logging note
  concluded about its sibling page: **the documented surface is the auditable
  surface.** Record three explicit non-claims so the Assayer and Smith see them.
  (1) **No CI gating** — the page never says a finding blocks a build; the only
  gate on the page is the licence requirement in its first line. The
  finding → gate path exists only as exports (Claims 4, 6). (2) **No
  quantitative claim** — no retention window, no scan volume, no latency, no
  cost, no finding counts; nothing here may be turned into a metric. (3) **No
  severity vocabulary** — "severity level" is used as a filter key and an editable
  field without ever enumerating the levels, so a cross-tenant severity
  comparison is unsupported (this compounds Claim 2's "based on your company's
  risk assessment"). Because the feature is Enterprise-gated, none of this is
  code-verifiable in the open-source repository, which is why
  `confidence_overall` is `emerging`: the enumerated facts are a *specification*
  we trust because it is the vendor's contract, and the operational behavior
  behind it is unverified.

## Concrete Artifacts

### Grading scope (verbatim, "How Grading Works")

> Grading is the process of evaluating the success of a red team attack.
> Promptfoo grades results based on the application context that is provided
> when creating a target. These results are subsequently compiled in the
> dashboard, vulnerabilities view, reports, and evaluations sections.

*(Attribution: promptfoo docs "Enterprise > Findings and Reports > How Grading
Works".)*

### Vulnerability review surface (verbatim, "Viewing Vulnerabilities")

> The "Vulnerabilities" section displays a list of all the vulnerabilities that
> have been found. You can filter based on the target, severity level, status of
> finding, risk category, or type of vulnerability.

> You can modify the status of the finding as either "Marked as Fixed", "False
> Positive", or "Ignore". You can also add comments to the finding to provide
> additional context about the vulnerability, as well as change the severity
> level of the vulnerability based on your company's risk assessment.

Filter keys as enumerated: **target**, **severity level**, **status of
finding**, **risk category**, **type of vulnerability**.
Disposition states as enumerated: **Marked as Fixed**, **False Positive**,
**Ignore**.

*(Attribution: promptfoo docs "Enterprise > Findings and Reports > Viewing
Vulnerabilities".)*

### Vulnerability export matrix (verbatim, "Exporting Vulnerabilities")

- **Export as CSV**: Export vulnerability data as a CSV file with details about each finding, severity, and remediation recommendations.
- **Export as SARIF**: Export vulnerabilities in [SARIF format](https://sarifweb.azurewebsites.net/) (Static Analysis Results Interchange Format) for integration with security tools like GitHub Security, SonarQube, and other DevOps platforms. SARIF is an industry-standard format for representing static analysis results.
- **Export as Colang v1**: Export vulnerabilities as Colang 1.0 guardrails for integration with [NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails). This format allows you to implement defensive guardrails based on the vulnerabilities discovered during red team testing.
- **Export as Colang v2**: Export vulnerabilities as Colang 2.x guardrails, supporting the latest Colang format for NeMo Guardrails.

*(Attribution: promptfoo docs "Enterprise > Findings and Reports > Exporting
Vulnerabilities"; link targets shown as the page links them.)*

### Eval export matrix (verbatim, "Viewing Reports")

- **Export to CSV**: Export the eval results as a CSV file.
- **Export to JSON**: Export the eval results as a JSON file.
- **Download Burp Suite Payloads**: Download the adversarial probes as payloads that can be imported into Burp Suite.
- **Download DPO JSON**: Download the eval results as a DPO JSON file.
- **Download Human Eval Test YAML**: Evaluate the eval results for performance in code-related tasks.
- **Download the failed test config**: Download a configuration file containing only the failed tests to focus on fixing just the tests that need attention.

*(Attribution: promptfoo docs "Enterprise > Findings and Reports > Viewing
Reports". Note the sixth bullet is described as an action, not a format — see
Claim 6.)*

### Sharing surface (verbatim, "Sharing Findings")

- **Export Vulnerabilities**: Export vulnerability data as CSV, SARIF, or Colang format from the "Vulnerabilities" section. See Exporting Vulnerabilities above for format details.
- **Export Eval Results**: Export eval results as CSV or JSON from the "Evals" section.
- **Download Vulnerability Reports**: Download point-in-time vulnerability reports for each scan in the "Reports" section. These reports are exported as a PDF.
- **Use the Promptfoo API**: Use the Promptfoo API to export findings, reports, and eval results.
- **Share via URL**: Generate shareable URLs for your evaluation results using the `promptfoo share` command. Learn more about sharing options.

*(Attribution: promptfoo docs "Enterprise > Findings and Reports > Sharing
Findings". The API bullet links to
`/docs/api-reference/`; the "search for findings" link on the same page targets
`/docs/api-reference/#tag/default/GET/api/v1/results`.)*

### Evals review surface (verbatim, "Viewing Reports" and "Filtering and Sorting Findings")

> You can modify the status of the finding as either a pass or failure, provide
> comments on the finding, view the vulnerability report associated with the
> eval result, and copy the eval result to your clipboard.

> The "Evals" section will display all of the evaluations and let you filter and
> sort through them based on the eval ID, date the scan was created, author,
> description, plugin, strategy, pass rate, or number of tests. You can then
> download the evals as a CSV file.

Filter/sort keys as enumerated: **eval ID**, **date the scan was created**,
**author**, **description**, **plugin**, **strategy**, **pass rate**, **number
of tests**.

*(Attribution: promptfoo docs "Enterprise > Findings and Reports > Viewing
Reports" and "> Filtering and Sorting Findings".)*

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **Concrete
    Artifacts → "No audit sink" section**, which records the Enterprise webhook
    event list as "`issue.created`, `issue.updated`, `issue.status_changed`,
    `issue.severity_changed`, `issue.comment_added` — five red-team finding
    events, no audit-log event". Those three mutable events map one-to-one onto
    the three edits this page documents (status change, severity re-rating,
    comment added — Claim 2), so the two pages independently establish the same
    object: **the red-team finding record, mutated by a human through the UI and
    pushed externally by webhook, but absent from the audit-log taxonomy.** The
    notes also share the same first-party-spec framing: that note's Source
    Context → "Author credibility" records that the page is authoritative *as a
    specification* while publishing no volume, latency, retention or cost figure,
    which is the identical caveat this note applies to Claim 11. (Verified by
    re-reading the cited section's heading, the five-event list, and that note's
    Author credibility paragraph.)
  - `source-notes/docs-promptfoo-code-scan-cli.md` **Claim 11** ("`--format
    sarif` emits location-backed findings that GitHub Code Scanning can
    display — the reuse route for the existing security toolchain") and
    `source-notes/blog-promptfoo-open-sourcing-modelaudit.md` **Claim 12**
    ("ModelAudit supports SARIF output, SBOM generation, secret scanning, and
    license detection — capabilities absent from all other open-source model
    scanners") — SARIF is a capability promptfoo carries on every scanning
    surface it ships, and this page adds the third instance (red-team
    vulnerabilities) to the two the corpus already holds (code scanner, model
    scanner). Corroborates the *format choice*, not the export mechanics; the
    red-team SARIF path remains undocumented as to completion signal (Claim 4).
    (Verified: both claim headings and quotes re-read.)

- **Contradicts**: None, and this was checked rather than assumed.
  - The nearest candidate — `guide/06-security-and-trust.md` §"Gating on LLM
    security scans" (the completion-signal Rule, lines 821–823) — is **not**
    contradicted: that Rule governs the code-scanner's `sarif-path` upload step,
    and this page documents no upload step at all (Claim 4). An undocumented
    step cannot oppose a documented rule; the correct treatment is *extension*,
    which is recorded under Guide Impact.
  - No existing note claims a findings→guardrail export, a findings disposition
    state machine, or a read-only findings API, so there is nothing for Claims
    2, 5, or 10 to oppose.
  - Two absences that looked contradiction-shaped were deliberately **not**
    filed as contradictions, following the precedent in
    `docs-promptfoo-enterprise-audit-logging.md` Extraction Notes (cross-page
    documentation gaps are not contradictions): (a) this page's UI-editable
    severity/status against that note's finding that no audit action covers
    them — a *gap* between two features, not two claims about one fact; (b) the
    page's "based on your company's risk assessment" severity against the
    code-scanner's enumerated `low|medium|high|critical` — different surfaces
    with different vocabularies, an ambiguity rather than an opposition. No
    `C-NNN` entry applies and **no verdict is picked in this note.**

- **Extends**:
  - `source-notes/docs-promptfoo-code-scan-github-action.md` **Claim 5** ("SARIF
    output is only published when a scan actually completes — an intentionally
    skipped scan does not publish a clean Code Scanning result") — that claim is
    the reason the guide's completion-signal Rule exists; this source extends
    the Rule's *scope* to a second SARIF-producing path (red-team vulnerability
    export, Claim 4) on which no completion signal is documented. The Rule
    should be stated as applying to **every** producer of a security artifact,
    not to the code scanner alone. (Verified: claim heading and quote re-read.)
  - `source-notes/docs-promptfoo-configuration-outputs.md` **Claim 6**
    ("Promptfoo's share and record-export paths carry an explicit "do not put
    secrets in shareable inputs" rule, and `promptfoo export eval` redacts
    config secrets while still warning that exports contain user data") —
    this page names two
    of that claim's three surfaces as its own sharing methods (`promptfoo share`
    and the CSV/JSON eval export) without repeating the secrets warning, so the
    warning composes: **every export on this page inherits it**, including the
    failed-test config (Claim 7), which is an eval-result-derived config file
    and therefore the highest-risk of the six. (Verified: claim heading and its
    two verbatim quotes re-read.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** ("Pre-deployment
    red teaming must be integrated into CI/CD pipelines and run on a recurring
    schedule because LLM application changes have nondeterministic consequences")
    — that note states the *requirement*; this source shows the vendor's own
    surface stops one step short of it. Promptfoo provides the export formats
    (Claims 4, 6) and explicitly does not provide the pipeline (Claim 11), so
    the requirement in that claim must be satisfied by the consumer. Read
    together they are the cleanest statement in the corpus of **where a vendor's
    security story ends and the operator's begins.** (Verified: claim heading
    and quote re-read.)
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 2** ("The
    coverage boundary is drawn explicitly and in control-plane vocabulary:
    administrative actions are logged, while "Evaluation runs, prompt testing,
    and other data plane operations are tracked separately" — with no named
    destination"). This page is one of the things "tracked separately" points
    at, and it confirms the pattern from the other side: findings live in their
    own review surface with their own read API (`GET /api/v1/results`, Claim 10)
    and their own webhook events, none of which appear in the audit taxonomy.
    That note's own assessment of the sentence — that the deferral names no
    product, page, or API — is exactly what this source resolves in one
    direction while leaving the audit side unresolved. The rule generalizes:
    **an eval platform's audit trail and its findings trail are different data
    sets, and neither substitutes for the other.** (Verified: Claim 2 heading,
    its two verbatim quotes, and the surrounding assessment re-read.)

- **Novel**: The following are net-new to the corpus. Verified 2026-10-07:
  `grep -riE 'colang|burp|dpo json|human eval|failed test config|marked as fixed'`
  over `source-notes/` and `guide/` — excluding this note, **zero** hits.
  (`registry/site-crawl-state.json` contains one unrelated
  `docs/integrations/burp` URL as a crawl candidate; no note covers it.)
  1. **Colang v1/v2 → NVIDIA NeMo Guardrails export of red-team findings**
     (Claim 5) — the corpus's first documented path from an eval/red-team finding
     to an enforceable runtime guardrail. Zero prior `Colang` matches in
     `source-notes/`, `guide/`, or `registry/`.
  2. **The failed-test-only config artifact** (Claim 7) — plus its gating hazard,
     which no note has recorded: a suite of only-failing tests cannot detect
     regressions in previously passing tests.
  3. **Burp Suite payload export, DPO JSON, Human Eval Test YAML** (Claim 6) —
     three interchange surfaces with no prior coverage; the Burp path is the
     corpus's first LLM-probe → conventional-DAST bridge.
  4. **The three-value finding disposition state machine with manual severity
     re-rating** (Claim 2) — no existing note documents a red-team finding
     status vocabulary, and the paired webhook events give the corpus its first
     complete picture of a finding's mutation surface.
  5. **Grading keyed on application context supplied at target creation**
     (Claim 1) — the corpus's first statement of *what* promptfoo red-team
     grading depends on, and the first instance of a grading input bound to a
     target object rather than to a run.
  6. **A read-only findings API with a human-only write path** (Claim 10) — the
     first documented instance on this platform of a review workflow whose reads
     are automatable and whose writes are not.

## Guide Impact

- **Chapter 06 §"Red-teaming as a CI gate" (`guide/06-security-and-trust.md:120`)
  — state where the vendor's story stops.** The section's Rule currently says to
  run red-team tests before each deployment and track a CI/CD security scorecard,
  citing `blog-promptfoo-ai-orchestrated-cyberattacks` for the *tests*. This
  source supplies the missing link and its absence: promptfoo's own findings
  surface ends at export (Claims 4, 6, 11), so the crossing from finding to gate
  is entirely the operator's. Proposed addition: *a red-team platform's
  documented loop usually ends at "export"; check that your pipeline names the
  step that consumes the export, because no vendor page in our corpus documents
  build-blocking on red-team findings.* Support it with Claim 11 (no `CI`,
  `pipeline`, `gate`, or `block` on the page) and with
  `blog-promptfoo-owasp-red-teaming.md` Claim 4 (the requirement, stated
  independently).
- **Chapter 06 §"Gating on LLM security scans" (`guide/06-security-and-trust.md:768`)
  — generalize the completion-signal Rule to every security-artifact producer.**
  The Rule at lines 821–823 is currently anchored to the code Action's
  `sarif-path` [source: `docs-promptfoo-code-scan-github-action`, Claim 5]. Add
  the second instance: promptfoo Enterprise's **red-team** vulnerability export
  also emits SARIF, and that path documents no completion or skip signal at all
  (Claim 4) — so a consumer of *that* file has no way to distinguish
  "scan ran, zero findings" from "export was empty". Proposed wording: *the
  completion-signal requirement applies to every producer of a security artifact
  — code scan, model scan, red-team export — and a producer with no signal must
  be treated as indistinguishable from a skip.*
- **Chapter 06 §"A guardrail gate reads a signal — it does not run a guardrail"
  (`guide/06-security-and-trust.md:387`) — add the one documented route to
  *produce* a guardrail.** That section establishes the read/execute distinction;
  `docs-promptfoo-guardrails-assertions.md` Claim 1 establishes that promptfoo's
  assertion reads rather than runs. This source is the first evidence for the
  other direction: **export red-team findings as Colang v1/v2 and deploy them as
  NVIDIA NeMo Guardrails guardrails** (Claim 5). Add it as the worked example of
  closing the loop, with the three caveats from Claim 5 attached: the page
  documents no generated-guardrail quality bar, no deployment step, and no
  reverse path — and per Ch05's guardrail-availability Rule, a generated
  deny-rule enters the request path and must be canaried like any other.
- **Chapter 06 §"A guardrail is an egress boundary — configure what crosses it"
  (`guide/06-security-and-trust.md:547`) — extend the egress rule to the export
  matrix.** Six eval export formats plus four vulnerability export formats leave
  the platform (Claims 4, 6, 7), and only two of the eval formats are described
  by the vendor as carrying anything sensitive; the page makes no redaction
  claim for any of them. Rule to add: *every "download as" menu is an egress
  path — enumerate the export formats a product offers and apply the same
  minimization review to each as to an API response*, citing
  `docs-promptfoo-configuration-outputs.md` Claim 5 ("best-effort (not
  comprehensive)") for why vendor redaction cannot be assumed.
- **Chapter 05 §"Evaluation and measurement methodology" — a grading input
  declared at target creation is a pinning question.** Add a line under the
  existing "A green eval is not evidence until you can name what it measured"
  material: promptfoo documents that red-team grading keys on "the application
  context that is provided when creating a target" (Claim 1) with no documented
  versioning or per-report snapshot, so **two reports of one target are only
  comparable if that context is known to be unchanged** — and since the platform
  also allows humans to flip pass/failure per eval and re-rate severity per
  finding (Claims 2, 9), any derived number ("pass rate", "open findings") is
  computed over human-editable data at two grains. The guide rule: *name the
  grading input, pin it, and say who may edit the result.*
- **Do not** cite this page as evidence that promptfoo provides a findings
  *workflow* (SLA, aging, auto-closure, escalation, attribution) or a CI gate.
  It documents a review surface and an export surface; Claims 2, 10, and 11 are
  the boundaries, and the Enterprise gate means none of it is verifiable in the
  open-source repository.

## Extraction Notes

- Source read in full via direct fetch of the rendered page
  (https://www.promptfoo.dev/docs/enterprise/findings) and, for quote
  verification, a second fetch of the raw HTML whose `<article>` body was
  text-extracted locally — every `Quote` above is character-for-character from
  that extraction. The page is short (eight `h2` sections plus the page title,
  no code blocks, no tables, no metrics), and both readings confirm the
  Prospector's assessment that
  this is a reference page rather than an engineering page: the only
  command-like strings on it are the `promptfoo share` command and the API path
  `GET /api/v1/results`.
- **No metrics were manufactured.** The page contains no number of any kind
  except version identifiers (`Colang 1.0`, `Colang 2.x`) and the page-update
  date. `confidence_overall: emerging` rather than `settled` for the same reason
  the audit-logging note made that choice: the enumerated facts are a
  specification string-checkable by an Enterprise tenant, while the behavior
  behind them is unverified and unverifiable from the open-source repository.
- **Open-source verifiability checked.** The page is gated ("This feature
  requires Promptfoo Enterprise") and nothing on it is a config file, schema, or
  CLI flag that could be checked against `promptfoo/promptfoo`. I did not run a
  repository code search this time: the audit-logging note (same Enterprise doc
  tree, extracted 2026-10-05) already recorded that its feature returns a single
  markdown hit and that the Enterprise surfaces are doc-only, and nothing on
  *this* page is an implementation claim.
- **Linked pages**: 1 of the 5-permitted budget used. The API Reference link
  (`/docs/api-reference/`, and the deep link
  `#tag/default/GET/api/v1/results`) was fetched on 2026-10-07: HTTP 200,
  18,434 bytes, **zero** occurrences of `results` and no rendered operation tags
  — a client-rendered spec with no retrievable body, confirming by independent
  re-observation what `docs-promptfoo-enterprise-audit-logging.md` Claim 9
  recorded for its own endpoint. Claim 10 is therefore bounded to "what this
  page documents". The Sharing page (`/docs/usage/sharing/`) was **not**
  re-fetched: `docs-promptfoo-configuration-outputs.md` Claim 6 already quotes it
  verbatim and is cited for the secrets rule instead of duplicating it.
- **Candidate handling** (`miner-related-notes.md`, 10 lexical candidates).
  Cited: **2** — `docs-promptfoo-enterprise-audit-logging.md` (Corroborates,
  Extends) and `blog-promptfoo-owasp-red-teaming.md` (Extends). The other eight
  explicitly dismissed, one line each:
  `docs-litellm-batches-api.md` — LiteLLM batch rate-limit admission semantics,
  no findings, export, or triage content;
  `blog-pagerduty-sre-agent-triage.md` — AI *incident* triage by an SRE Agent;
  the shared word "triage" denotes alert routing there and red-team finding
  disposition here, and the two make no claim about the same object;
  `docs-promptfoo-pi-scorer.md` — a model-graded grader's configuration; adjacent
  only in that both concern *grading*, but its Claim 3 (a vendor determinism
  assertion published without evidence) is the calibration precedent this note
  uses for how to treat the unevidenced capability statements in Claims 5 and 6;
  `docs-langfuse-mcp-server.md` — docs-MCP transport, unrelated;
  `docs-google-sre-eliminating-toil.md` — the toil taxonomy, unrelated;
  `docs-google-sre-reliable-product-launches.md` — launch coordination,
  unrelated;
  `docs-google-sre-team-lifecycles.md` — SRE org design, unrelated;
  `docs-promptfoo-deterministic-metrics.md` — assertion-type inventory; its
  "deterministic means no model judge" line is about assertion families, not
  about red-team grading context (Claim 1), so no citation is warranted.
- **Prospector pointer reconciliation (MINER §4b).** The Prospector's superseding
  triage named `docs-promptfoo-configuration-outputs.md` **Claim 5** as owning
  the SARIF export/publishing path alongside `docs-promptfoo-code-scan-cli.md`
  **Claim 11**. Re-reading both: **Claim 11 is confirmed** (heading and quote
  match the SARIF-export claim exactly). `docs-promptfoo-configuration-outputs.md`
  **Claim 5 is not** — that claim is "The other documented formats are full
  exports — `json`, `yaml`, `yml`, `txt`, `html`, and Promptfoo XML all include
  the eval `config` ...", about config-carrying output formats, and SARIF does
  not appear in any of its claims; the only SARIF mention in that file is inside
  its **Cross-References** section, where it cites
  `docs-promptfoo-code-scan-github-action.md` Claim 5. So the citations written
  above are to `code-scan-cli` Claim 11 and `code-scan-github-action` Claim 5 —
  the two claims that actually own the SARIF material — and the
  `configuration-outputs` Claim 5 pointer is recorded here as resolved rather
  than followed. Its Claim 6 *is* cited (Extends), for the sharing/secrets rule.
- **Cross-references verified before writing** (MINER §4b): every `Claim N`
  cited from another note was located by re-reading that note's `### Claim:`
  headings and confirming content — `code-scan-cli` Claim 11,
  `code-scan-github-action` Claim 5, `configuration-outputs` Claims 5 and 6,
  `guardrails-assertions` Claim 1, `owasp-red-teaming` Claim 4,
  `enterprise-audit-logging` Claim 2 and its Concrete Artifacts section,
  `open-sourcing-modelaudit` Claim 12. The audit-logging webhook list is cited
  **by section name** (Concrete Artifacts → "No audit sink"), not by a claim
  number, because it lives in that note's artifacts section. No quote was
  reconstructed from memory.
- **Contradiction filing decision**: none filed; the two contradiction-shaped
  observations were assessed and declined under MINER §4a with reasons recorded
  in Cross-References → Contradicts. Checked against `CONTRADICTIONS.md` and the
  `contradiction`-labeled issues: no existing entry covers promptfoo findings
  triage or exports.
- `registry/sources.json` and `registry/claims-index.json` were **not** touched;
  both are derived indexes rebuilt by `registry-rebuild.yml` after merge.
  `miner-related-notes.md` was read but is not committed.
