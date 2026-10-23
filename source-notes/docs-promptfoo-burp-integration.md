---
source_url: https://www.promptfoo.dev/docs/integrations/burp
source_type: docs
title: "Finding LLM Jailbreaks with Burp Suite — the `.burp` Payload Contract and the Intruder Handoff"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-23
date_extracted: 2026-10-23
last_checked: 2026-10-23
status: current
confidence_overall: emerging
issue: "#1842"
---

# Finding LLM Jailbreaks with Burp Suite

> The only promptfoo page that specifies the `.burp` payload artifact and the
> Burp Intruder handoff: two export paths (web UI and `promptfoo redteam
> generate -o payloads.burp --burp-escape-json`), a `.burp` file that is both
> JSON-escaped and URL-encoded, a consumer-side URL-decoding step that silently
> corrupts payloads if missed, and a **manual, one-way** handoff — promptfoo
> produces probes, Burp executes them, and no result travels back.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Integrations > Burp
  Suite" page).
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own CLI flag and export format, so the
  command and the two encoding statements are authoritative *as a product
  contract*. It is not measurement and not a compatibility statement: the page
  publishes no `.burp` schema, no Burp version, no encoding specification, no
  worked request/response, and no metric. The page footer reads "Last updated on
  **Oct 23, 2026** by **renovate\[bot\]**" — that is the only date on the page,
  used here as `date_published`.
- **Scope**: Covers the purpose of the integration, prerequisites, the web-UI
  export path, the CLI generation command, the `--burp-escape-json` flag, the
  Intruder import procedure, the URL-decoding requirement, and one example
  `promptfooconfig.yaml` redteam block. Does **not** cover the `.burp` file
  schema, the exact encoding rules (percent-encoding set, line-ending handling),
  Burp edition/version differences, how to choose Sniper vs Pitchfork, how to
  mark JSON injection points, session/auth handling, how to judge whether a
  jailbreak succeeded, any results-import path, or CI integration.
- **Relationship to sibling pages**: this URL was named as an uncovered crawl
  candidate at the end of
  `source-notes/docs-promptfoo-enterprise-findings-reports.md` (its Claim 6 and
  Novel section record "Download Burp Suite Payloads" as one of six eval export
  formats and explicitly state that no note covers `docs/integrations/burp`).
  This note is that extraction. It is also the first corpus note to describe the
  artifact contract rather than the export-menu label.

## Extracted Claims

### Claim 1: The integration's deliverable is a *Burp Intruder configuration* — promptfoo generates application-level jailbreak probes, Burp replays them against the LLM endpoint, and the page frames the output as a test setup rather than a result

- **Evidence**: The page's opening two sentences state the integration and the
  end state; the "Overview" section restates it as three capabilities
  (generate → export → use as payloads). There is no section on reading results.
- **Confidence**: settled (stated verbatim; scope of the page)
- **Quote**: "This guide shows how to integrate Promptfoo's application-level jailbreak creation with Burp Suite's Intruder feature for security testing of LLM-powered applications." / "The end result is a Burp Suite Intruder configuration that can be used to test for LLM jailbreak vulnerabilities."
- **Our assessment**: Buy the framing, and it is the most important thing to get
  right in the guide: **the integration produces a test harness, not a test
  verdict.** Promptfoo's red-team generation is the probe factory; Burp is the
  executor; the page ends at "can be used to test". That is a different contract
  from promptfoo's own eval loop, where the harness grades each probe and emits
  a pass/fail. Here the grading is whatever a human reading Burp responses does.
  The guide should therefore not describe this as "promptfoo red-teaming in
  Burp" as if the results were attributable to promptfoo — the finding is
  produced on the Burp side and does not exist as a promptfoo finding.

### Claim 2: There are two documented export paths — a web-UI download and a CLI generation command — and they have different generation semantics: the UI exports "all unique test inputs from your evaluation", while the CLI *generates* a fresh red-team set

- **Evidence**: "Option 1: Using the Web UI" describes opening an existing
  evaluation's results and choosing Evaluation Actions → Download → Advanced
  Options → "Download Burp Suite Payloads". "Option 2: Using the Command Line"
  gives `promptfoo redteam generate -o payloads.burp --burp-escape-json`.
- **Confidence**: settled (both paths are stated verbatim; the semantic
  difference is our reading of "from your evaluation" vs `redteam generate`)
- **Quote**: "This will generate a `.burp` file containing all unique test inputs from your evaluation, with proper JSON escaping and URL encoding." / "promptfoo redteam generate -o payloads.burp --burp-escape-json"
- **Our assessment**: Buy both paths and flag the difference rather than
  collapsing them. The UI path is an **export of evidence already collected** —
  de-duplicated ("all unique test inputs"), so the payload set is bounded by the
  eval that ran. The CLI path is a **new generation run**, so its payload set is
  defined by the config and `numTests`, not by prior results. For the guide that
  distinction matters twice: (a) an export of an old eval is a replay of the
  probe set that produced those findings, which is the right artifact for
  reproducing a known bypass but the wrong one for discovering a new one; (b) the
  UI wording "unique" implies de-duplication that the CLI path does not promise,
  so the same notional run can yield different payload counts depending on which
  door you use. The page does not state whether the UI download applies the CLI
  flag's escaping by default — it only says "proper JSON escaping and URL
  encoding", with no flag named — so we treat the CLI invocation as the
  documented, reproducible path and the UI as the convenience path.

### Claim 3: The `.burp` file is URL-encoded specifically to support multi-line payloads, so the Burp consumer must enable URL-decoding in Payload processing or the target receives an encoded — not the intended — probe

- **Evidence**: Step 4 of "Import into Burp Intruder" states the requirement and
  its reason in one sentence, immediately after the payload-load step. Nothing
  else on the page describes the encoding.
- **Confidence**: settled as the documented requirement; **emerging** as a
  reliability property, because the page gives no encoding specification and no
  example of what a decoded vs undecoded payload looks like
- **Quote**: "Under \"Payload processing\", enable URL-decoding (promptfoo's .burp output is URL-encoded to support multi-line payloads)"
- **Our assessment**: Buy it as *the* operational footgun on the page. A
  multi-line jailbreak prompt cannot survive as a raw line in a line-oriented
  payload file, so the encoding is load-bearing rather than cosmetic; but the
  cost is that the decode step becomes a mandatory, easy-to-miss part of the
  contract. Three failure modes follow, and the page warns about none of them
  explicitly: (a) **missing decode** — Burp sends `%0A`-style text, the request
  is syntactically valid, the model receives a mangled prompt, and the run
  produces a false negative that looks like a clean result; (b) **double
  decode** — a second payload-processing rule or a proxy that decodes again
  changes the payload before it reaches the target; (c) **decode ordering** —
  because the artifact is also JSON-escaped (Claim 4), the decode must happen
  once, in the right layer, or the JSON string and the URL encoding fight each
  other. The honest guide rule is: treat the `.burp` file as an encoded artifact
  and verify one known payload's decoded form in Burp before trusting a run. The
  page does not even name the encoding (percent-encoding vs form encoding), so
  the verification step is the only reliable check.

### Claim 4: `--burp-escape-json` is required when payloads are injected into JSON request bodies — it escapes special characters so the payload does not break JSON syntax

- **Evidence**: A "tip" admonition directly under the CLI command, plus the flag
  in the command itself.
- **Confidence**: settled (documented flag semantics)
- **Quote**: "The `--burp-escape-json` flag is important when your payloads will be inserted into JSON requests. It ensures that special characters are properly escaped to maintain valid JSON syntax."
- **Our assessment**: Buy the flag and read it as a *precondition*, not an
  optimization. The failure it prevents is not a security finding but a
  **transport failure**: a quote or backslash in a jailbreak prompt terminates
  the JSON string, the endpoint returns a 4xx (or the app rejects the body), and
  the Intruder run records a non-200 that has nothing to do with model
  susceptibility. If an operator counts that as "the jailbreak failed", the
  result is a false clean. Note the asymmetry the page leaves implicit: the flag
  is documented only for JSON bodies. It gives no guidance for form-encoded,
  multipart, XML, or plain-text endpoints, where the same special characters
  fail differently and where JSON-escaping would itself be wrong. The guide
  should pair the flag with the body type: **escape for the body you are
  attacking, and verify that the request parses before interpreting the
  response.** This also composes with Claim 3 — JSON escaping and URL encoding
  are two layers applied to the same payload, and only the URL layer has a
  documented consumer-side decode step.

### Claim 5: The documented CLI surface is exactly `promptfoo redteam generate -o payloads.burp --burp-escape-json`, with the `.burp` extension selecting the output format — the page shows no other flag, config key, or format selector

- **Evidence**: The single command block in "Option 2", and its repetition under
  "Example Configuration". No `--format burp`, config key, or schema reference
  appears anywhere on the page.
- **Confidence**: settled as what the page documents; **emerging** as a stable
  interface, because format-by-extension and `.burp` schema/version stability
  are not stated
- **Quote**: "promptfoo redteam generate -o payloads.burp --burp-escape-json" / "This will create a file with payloads ready for use in Burp Intruder."
- **Our assessment**: Buy the invocation; do **not** infer more contract than it
  states. Two gaps matter for a runbook. First, reproducibility: the page shows
  a config *fragment* under `redteam:` with no `targets:` block, so the example
  cannot be run end-to-end from this page alone — a reader must already know
  promptfoo red-team target configuration. Second, artifact stability: because
  the format is selected by the file extension and the page publishes no schema
  or version, a pinned pipeline cannot tell from the artifact whether a future
  promptfoo release changed the encoding. The mitigation is operational, not
  documentary: pin the promptfoo version, hash the generated `.burp` file, and
  re-verify the decode step (Claim 3) whenever it changes. The guide should
  treat the `.burp` file as an opaque, version-sensitive build artifact rather
  than a stable interchange standard.

### Claim 6: The Intruder import is a six-step manual procedure — intercept a request, send to Intruder, choose Sniper or Pitchfork, mark injection points, load the `.burp` file in Payloads, and enable URL-decoding

- **Evidence**: The numbered "Import into Burp Intruder" list; each step is one
  sentence. The page's only guidance on attack type is the parenthetical
  "usually".
- **Confidence**: settled as the documented procedure; **emerging** as
  operational guidance, because the page does not map attack type to injection
  count or payload-set shape
- **Quote**: "Set attack type (usually \"Sniper\" or \"Pitchfork\")" / "Mark the injection points where you want to test the payloads" / "Click \"Load\" and select your `payloads.burp` file"
- **Our assessment**: Buy the steps and note what the procedure assumes.
  (a) **One request, one endpoint, one session** — the operator intercepts a
  single live request, so the setup is inherently a manual, authenticated,
  point-in-time exercise rather than a repeatable pipeline. (b) **The attack-type
  choice is underspecified**: Sniper iterates one payload set across each marked
  position; Pitchfork pairs multiple payload sets position-by-position. The page
  loads exactly one payload file and mentions Pitchfork anyway, so a reader who
  chooses Pitchfork has to know from Burp's own docs that it needs a matching
  payload set per position — a gap that can produce a half-empty or misaligned
  run. (c) **Marking JSON injection points is not described**: for the JSON-body
  case the flag in Claim 4 is designed for, the operator has to place markers
  inside a JSON string without breaking it — exactly the step where a
  hand-edited request can invalidate the body. The page documents the button
  sequence but not the judgment calls, which is why this handoff belongs in a
  runbook with a worked example, not in a one-screen integration note.

### Claim 7: The example red-team config uses the `harmful` plugin with three jailbreak strategies — `jailbreak`, `jailbreak:composite`, and `jailbreak-templates` — and the same command then exports the generated probes

- **Evidence**: The "Example Configuration" YAML block and the command that
  follows it. The block is a `redteam:` fragment (no `targets:`), and the page
  says the result is "payloads ready for use in Burp Intruder".
- **Confidence**: settled as the documented example
- **Quote**: "This will create a file with payloads ready for use in Burp Intruder."
- **Our assessment**: Buy the example as a minimal multi-strategy generator —
  `jailbreak` and `jailbreak:composite` are iterative/compound transformations,
  and `jailbreak-templates` applies template wrappers, so the exported payload
  set is not a plain list of harmful prompts but a set of transformed variants.
  That matters for interpreting a Burp run: a bypass on a composite strategy is
  evidence about the *transformation pipeline*, not about the raw policy
  question, and the `.burp` artifact carries the transformed payload without the
  strategy label that produced it (the page documents no metadata in the file).
  The example is also narrower than "red-team everything": `harmful` is one
  plugin family, and the config declares no target, no `numTests`, and no
  policy-specific plugin — so the guide should present it as a starting
  fragment, not a complete suite. It corroborates the strategy list in
  `blog-promptfoo-owasp-red-teaming.md` Claim 12 (which uses the same three
  jailbreak strategies alongside `best-of-n` and `jailbreak:likert`), and it
  extends that note by showing the strategies feeding a DAST export rather than
  a promptfoo-native grade.

### Claim 8: The handoff is one-way — promptfoo produces payloads, Burp executes them, and the page documents no way to import Burp results, attach a verdict, or return a finding to promptfoo

- **Evidence**: The page's scope ends at the Intruder import and the example
  command. Its Overview lists three capabilities, the last of which is "Use the
  test cases as payloads in Burp Suite for security testing". There is no
  results, reporting, or import section, and no promptfoo command is shown after
  the export.
- **Confidence**: settled as a statement of what this page documents; the
  product-level absence of an import path is **not** established by one page
- **Quote**: "Generate adversarial test cases using Promptfoo's red teaming capabilities" / "Export these test cases in a format compatible with Burp Intruder" / "Use the test cases as payloads in Burp Suite for security testing"
- **Our assessment**: Buy it, and treat it as the boundary the guide must state.
  The artifact that crosses the boundary is a **payload list**, not a test
  definition: no expected outcome, no grader, no strategy provenance, no
  finding ID travels with it. So the verdict is produced entirely in Burp and
  recorded entirely in Burp — meaning (a) there is **no completion signal** on
  the promptfoo side that the probes were ever run, and (b) a re-run cannot be
  reconciled with the export that seeded it unless the operator hashes and keeps
  the `.burp` file (Claim 5). This is the same skip-vs-clean discipline the guide
  already applies to security-scanner output
  (`docs-promptfoo-code-scan-cli.md` Claim 9), moved one tool downstream: an
  absent Burp result and a clean Burp run are indistinguishable unless the
  operator records the run. It also qualifies the "first LLM-probe → conventional
  DAST bridge" label in
  `docs-promptfoo-enterprise-findings-reports.md` Claim 6 — the bridge is real,
  but it is a **one-way export plus a human-driven execution**, not an
  instrumented loop.

### Claim 9: The page publishes no `.burp` schema, no encoding specification, no Burp version or edition compatibility data, no worked transcript, and no metric — the prerequisites are only a Burp edition and a global promptfoo install

- **Evidence**: Full-page read: the page is roughly one screen of prose, one
  command block, one YAML block, and two screenshots. The prerequisites are two
  bullets. There is no table, no schema, no version number, and no measured
  claim of any kind.
- **Confidence**: settled as a description of the page's contents; the
  surrounding product behavior is unverified
- **Quote**: "Burp Suite Community Edition or Professional Edition" / "Promptfoo installed (`npm install -g promptfoo`)"
- **Our assessment**: Record this as the calibration claim that bounds every
  other claim above. The page is authoritative for *the flag names and the two
  encoding requirements* because those are checkable strings, but it is not
  evidence that a given `.burp` file works against a given Burp/endpoint
  combination — it names both editions without stating whether either is
  tested, and the screenshots are the only worked example. `confidence_overall`
  is therefore `emerging`: the artifact contract is vendor-stated, while the
  operational behavior behind it is undocumented and unmeasured. The guide
  should cite the flag and decode requirements (Claims 3–4) as vendor contract,
  and cite the one-way handoff (Claim 8) as a page-scope observation, not as a
  claim that no import API exists anywhere in the product.

## Concrete Artifacts

### CLI generation (verbatim, "Option 2: Using the Command Line")

```bash
promptfoo redteam generate -o payloads.burp --burp-escape-json
```

*(Attribution: promptfoo docs "Integrations > Burp Suite > Option 2: Using the
Command Line".)*

### Example `promptfooconfig.yaml` redteam block (verbatim content, "Example Configuration")

The page renders this block as a single line after HTML extraction; line breaks
are restored at YAML structure boundaries only — no tokens added or removed.

```yaml
redteam:
  plugins:
    - harmful
  strategies:
    - jailbreak
    - jailbreak:composite
    - jailbreak-templates
```

*(Attribution: promptfoo docs "Integrations > Burp Suite > Example
Configuration". The block is a fragment: the page shows no `targets:` key, so
the config is not runnable as shown — see Claim 5.)*

### The `.burp` artifact contract (verbatim statements)

> This will generate a `.burp` file containing all unique test inputs from your
> evaluation, with proper JSON escaping and URL encoding.

> The `--burp-escape-json` flag is important when your payloads will be inserted
> into JSON requests. It ensures that special characters are properly escaped to
> maintain valid JSON syntax.

> Under "Payload processing", enable URL-decoding (promptfoo's .burp output is
> URL-encoded to support multi-line payloads)

Contract as stated: **unique** test inputs (UI path), **JSON-escaped** when
`--burp-escape-json` is set, **URL-encoded** in all cases to preserve multi-line
payloads, and **requires a consumer-side URL-decode** before the payload reaches
the target.

*(Attribution: promptfoo docs "Integrations > Burp Suite", "Option 1", the CLI
tip, and the Intruder import step 4. The page does not name the encoding scheme
or publish a file schema — see Claims 3 and 9.)*

### Burp Intruder import procedure (verbatim steps, "Import into Burp Intruder")

1. "In Burp Suite, intercept a request to your LLM-powered endpoint"
2. "Right-click and select \"Send to Intruder\""
3. "In the Intruder tab: Set attack type (usually \"Sniper\" or \"Pitchfork\")"
4. "Mark the injection points where you want to test the payloads"
5. "Go to the \"Payloads\" tab"
6. "Click \"Load\" and select your `payloads.burp` file"
7. "Under \"Payload processing\", enable URL-decoding (promptfoo's .burp output is URL-encoded to support multi-line payloads)"

*(Attribution: promptfoo docs "Integrations > Burp Suite > Import into Burp
Intruder". Steps 3–7 are the page's nested bullets, flattened to one level
here; wording is unaltered.)*

### Web UI export path (verbatim, "Option 1: Using the Web UI")

> Click the "Evaluation Actions" > "Download" menu in the top right

> Under "Advanced Options", click "Download Burp Suite Payloads"

*(Attribution: promptfoo docs "Integrations > Burp Suite > Option 1: Using the
Web UI". Note this page does not carry the "requires Promptfoo Enterprise" gate
that the sibling Enterprise findings page places on its Burp download — see
Extraction Notes.)*

## Cross-References

- **Corroborates**:
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 12** ("The
    foundation model itself should be baseline red-teamed before
    application-layer testing, using multiple jailbreak strategies") — its
    config example enumerates `jailbreak`, `jailbreak:composite`,
    `jailbreak-templates`, `jailbreak:likert`, and `best-of-n`, which contains
    exactly the three jailbreak strategies this page's example uses (Claim 7).
    The two pages independently establish the same strategy vocabulary for
    promptfoo red-team generation; this page adds the DAST export target, that
    note supplies the baseline-testing rationale. (Verified by re-reading the
    note's Claim 12 heading, its YAML artifact, and its surrounding assessment.)
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` **Claim 6**
    ("The eval-level export matrix is six formats, four of which are specialized
    interchange artifacts — Burp Suite payloads, DPO JSON, Human Eval Test YAML,
    and a failed-test-only config") — that claim records "Download Burp Suite
    Payloads" as an export menu entry and calls the Burp path "the corpus's
    first LLM-probe → conventional-DAST bridge". This page corroborates the
    existence of that export (its Option 1 is the same UI download) and supplies
    the command-line path and artifact contract the other note explicitly did
    not cover. (Verified: Claim 6 heading, its verbatim quotes, and the note's
    Novel item 3 re-read.)

- **Contradicts**: None, and this was checked rather than assumed.
  - The nearest tension is a **cross-page documentation gap, not a
    contradiction**: this page presents "Download Burp Suite Payloads" in the web
    UI with no licence gate, while
    `docs-promptfoo-enterprise-findings-reports.md` Claim 6/Claim 11 places the
    same eval-export surface behind "This feature requires Promptfoo
    Enterprise." Both statements can be true of different builds/plans, and
    neither page says the other is wrong; per MINER §4a this is a gap in one of
    the two pages, not two claims about one fact. No contradiction issue was
    filed.
  - No existing note claims a `.burp` schema, an encoding specification, a
    results-import path, or a Burp-side grader, so Claims 3, 5, and 8 have
    nothing to oppose. Checked `CONTRADICTIONS.md` (no `C-NNN` entries) and all
    open `contradiction`-labeled issues: none covers Burp, `.burp`, Intruder, or
    this integration.

- **Extends**:
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` **Claim 6** and
    its **Novel** item 3 — that note stops at the export-list label and records
    that no note covers `docs/integrations/burp`. This note is that extraction:
    it adds the CLI invocation, the `--burp-escape-json` contract, the
    URL-encoding/decode requirement, and the Intruder procedure. It also
    **qualifies** the "bridge" label: the bridge is a one-way payload export
    plus manual execution (Claim 8), not an instrumented handoff. (Verified:
    Claim 6 heading/quote and Novel item 3 re-read.)
  - `source-notes/docs-promptfoo-configuration-outputs.md` **Claim 6**
    ("Promptfoo's share and record-export paths carry an explicit "do not put
    secrets in shareable inputs" rule, and `promptfoo export eval` redacts
    config secrets while still warning that exports contain user data") — the
    `.burp` file is yet another egress path, and an unusually sensitive one: it
    contains adversarial probe text, and the UI path exports the test inputs of
    an evaluation — which can include customer-derived content if that eval's
    tests do. This page documents no
    redaction for the `.burp` artifact and no secrets warning, so the
    configuration-outputs rule applies by extension: **treat the payload file as
    an unredacted export and apply the same minimization review as any other
    eval artifact.** (Verified: Claim 6 heading and both verbatim quotes
    re-read.)
  - `source-notes/docs-promptfoo-code-scan-cli.md` **Claim 9** ("`skipReason` is
    set when a scan is intentionally skipped (e.g. fork PR awaiting maintainer
    approval), in which case `comments` is empty — an empty result is not a clean
    result") — that claim establishes the skip-vs-clean rule on the scanner's
    own output. This page extends the rule to a **handoff boundary**: promptfoo
    emits no completion signal for the Burp run (Claim 8), so a missing Burp
    result and a clean Burp run are indistinguishable unless the operator
    records the run and keeps the payload file. The guide's existing completion-
    signal Rule should therefore cover not just artifacts a tool produces but
    artifacts it hands to another tool. (Verified: Claim 9 heading and quote
    re-read.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** ("Pre-
    deployment red teaming must be integrated into CI/CD pipelines and run on a
    recurring schedule because LLM application changes have nondeterministic
    consequences") — that note states the CI requirement; this page documents a
    handoff that is inherently **outside** CI (manual interception of a live
    request, manual attack-type choice, no result import). Read together they
    locate the gap precisely: the requirement is real, and the DAST bridge is
    an *escalation path for a confirmed or suspected bypass*, not a substitute
    for the recurring automated suite. (Verified: Claim 4 heading and quote
    re-read.)

- **Novel**: Net-new to the corpus, verified by searching `source-notes/` and
  `guide/`:
  1. **The `.burp` artifact contract** — unique inputs (UI path), JSON escaping
     via `--burp-escape-json`, and URL encoding "to support multi-line payloads"
     (Claims 2–4). The only prior mention of Burp anywhere in the corpus is the
     export-menu label in
     `docs-promptfoo-enterprise-findings-reports.md`, which records none of this.
  2. **The consumer-side URL-decode requirement and its silent-corruption
     failure mode** (Claim 3) — no prior corpus note describes a security-tool
     handoff where the receiver must decode the payload or measure the wrong
     thing.
  3. **The `promptfoo redteam generate -o <file>.burp` invocation and the
     format-by-extension assumption** (Claim 5).
  4. **The Intruder import procedure and its attack-type/injection-point gaps**
     (Claim 6).
  5. **The one-way export semantics** (Claim 8) — the corpus's first concrete
     instance of a red-team → DAST handoff with no result path back.

## Guide Impact

- **Chapter 06 §"Red-teaming as a CI gate" (`guide/06-security-and-trust.md:120`)** —
  add the Burp handoff as an explicit **manual escalation path, not a CI gate**.
  The section currently says to run red-team tests before each deployment and
  track a CI/CD security scorecard; this source shows the one documented bridge
  from promptfoo probes to a conventional DAST tool requires intercepting a live
  request, choosing Sniper/Pitchfork by hand, and reading Burp responses
  (Claims 1, 6, 8). Proposed wording: *exporting red-team probes to a DAST tool
  is a handoff, not an automated gate — the verdict is produced in the DAST tool
  and never returns to the generator, so record the run and the payload file
  hash alongside it.* Support with Claims 2, 6, and 8.
- **Chapter 06 §"Gating on LLM security scans" (`guide/06-security-and-trust.md:768`,
  Rule at lines 821–823)** — extend the completion-signal Rule from *produced*
  artifacts to *handed-off* artifacts. The existing Rule covers the code
  scanner's `skipReason` and `sarif-path`
  [source: docs-promptfoo-code-scan-cli, Claim 9; docs-promptfoo-code-scan-github-action, Claim 5].
  Add: a `.burp` export carries no completion or result signal, and promptfoo
  documents no import of Burp findings (Claim 8), so **a DAST run gate must read
  its completion from Burp and pin the payload file it consumed** — otherwise a
  run that never happened is indistinguishable from a run that found nothing.
  Cite `docs-promptfoo-code-scan-cli.md` Claim 9 for the general rule.
- **Chapter 06 — data governance / artifact egress** — add `.burp` to the
  enumerated egress paths. The file carries adversarial probe text, and for
  `harmful`/`pii` plugins that text can contain customer-derived or PII content;
  this page documents no redaction and no secrets warning (Claim 9). Rule:
  *every export menu is an egress path, including the payload handoff to a
  security tool; review it like any other eval artifact.* Cite
  `docs-promptfoo-configuration-outputs.md` Claim 6 for the vendor's own
  "do not put secrets in shareable inputs" rule and the best-effort sanitizer
  caveat.
- **Chapter 05 §"Evaluation and measurement methodology"** — when the guide
  enumerates eval artifact/export contracts, record the `.burp` encoding
  contract so a consumer does not double-decode or interpret a transport
  failure as a clean result: URL-encoded to preserve multi-line payloads, with a
  mandatory decode step; JSON-escaped only when `--burp-escape-json` is set
  (Claims 3–4). The transferable rule is larger than Burp: **when a harness
  hands payloads to another tool, the encoding and completion contracts live at
  the boundary and must be verified with one known payload before the run is
  trusted.**
- **Do not** cite this page as evidence that promptfoo grades or reports Burp
  results, that a `.burp` file is a stable interchange schema, or that the
  integration is CI-automatable. Claims 5, 8, and 9 are the boundaries.

## Extraction Notes

- Source read in full via direct fetch of the rendered page
  (https://www.promptfoo.dev/docs/integrations/burp) on 2026-10-23. The page is
  short — a title, five `h2` sections (Overview, Prerequisites, Configuration
  Steps with two options and an import subsection, Example Configuration), one
  command block, one YAML block, two screenshots — so a full read is a complete
  read rather than a skim. Every `Quote` above is a character-for-character copy
  of a contiguous passage from that fetch; passages are quoted separately rather
  than spliced, and the two bullets in Claim 9 are separate contiguous
  fragments.
- **No sub-pages were followed.** The page's only outbound links are navigation,
  the screenshot assets, and product/marketing links; there is no linked
  specification of the `.burp` format or of Burp Intruder. Burp's own docs are
  external to this source and were not treated as evidence for any claim.
- **Candidate handling** (`miner-related-notes.md`, 10 lexical candidates, read
  before writing Cross-References; file not committed). Cited from the list:
  **1** — `docs-promptfoo-enterprise-findings-reports.md` (Corroborates,
  Extends). The other nine candidates are explicitly dismissed, one line each:
  - `docs-litellm-evals-api.md` — LiteLLM's server-side Evaluations API; no
    export format, DAST tool, or payload handoff.
  - `docs-litellm-batches-api.md` — batch request accounting/rate limits; the
    shared "payload" word denotes an API request body there, not an adversarial
    probe.
  - `blog-pagerduty-sre-agent-triage.md` — AI *incident* triage by an SRE agent;
    no relationship to red-team probe generation or Burp.
  - `docs-promptfoo-pi-scorer.md` — a model-graded scorer's configuration and
    determinism claims; adjacent only in being a promptfoo docs page, and makes
    no claim about export or security testing.
  - `docs-langfuse-mcp-server.md` — docs-MCP transport plumbing; unrelated.
  - `docs-google-sre-eliminating-toil.md` — toil taxonomy and the 50%
    operational-work cap; unrelated.
  - `docs-google-sre-reliable-product-launches.md` — launch coordination;
    unrelated.
  - `docs-google-sre-team-lifecycles.md` — SRE org design; unrelated.
  - `docs-promptfoo-deterministic-metrics.md` — assertion-type inventory; its
    "deterministic means no model judge" line is about graders, not about
    payload encoding or DAST handoff.
- **Additional cross-references found by searching `source-notes/` directly (not
  in the candidate list)**: `docs-promptfoo-configuration-outputs.md` Claim 6
  (Extends), `blog-promptfoo-owasp-red-teaming.md` Claims 4 and 12
  (Corroborates, Extends), and `docs-promptfoo-code-scan-cli.md` Claim 9
  (Extends). Each was verified by re-reading its heading and quote per MINER
  §4b. No other note was
  found that covers Burp, Intruder, `.burp`, or `--burp-escape-json`
  (`grep -riE 'burp|intruder|burp-escape-json' source-notes/ guide/` returns
  only the export-list mentions in
  `docs-promptfoo-enterprise-findings-reports.md` and this note).
- **Cross-references verified before writing** (MINER §4b): every `Claim N`
  cited from another note was located by re-reading that note's `### Claim:`
  heading and confirming content — `docs-promptfoo-enterprise-findings-reports`
  Claim 6, `docs-promptfoo-configuration-outputs` Claim 6,
  `docs-promptfoo-code-scan-cli` Claim 9,
  `blog-promptfoo-owasp-red-teaming` Claims 4 and 12. No quote was reconstructed
  from memory; the two short passages quoted from cited notes are copied from
  those notes.
- **Contradiction filing decision**: none filed. The only contradiction-shaped
  observation — the Enterprise-gate discrepancy between this page's UI export
  and the Enterprise findings page — is a cross-page documentation gap, not two
  opposing claims about one fact, and no guide advice changes based on which page
  is right (either way the user's plan decides access). Checked
  `CONTRADICTIONS.md` and all open `contradiction`-labeled issues; none covers
  this surface.
- **`confidence_overall: emerging` rather than `settled`**: the flag names and
  the two encoding statements are settled vendor contract, but the page
  publishes no `.burp` schema, no encoding specification, no Burp
  version/edition compatibility evidence, no worked transcript, and no measured
  behavior. The operational claims (silent corruption on a missed decode, false
  cleans from JSON breakage, no completion signal on the Burp side) are our
  analysis of the documented contract, marked as such in the Claims.
- `registry/sources.json` and `registry/claims-index.json` were **not** touched;
  both are derived indexes rebuilt by `registry-rebuild.yml` after merge.
  `miner-related-notes.md` was read but is not committed.
