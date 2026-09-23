---
source_url: https://www.promptfoo.dev/docs/code-scanning/vscode-extension
source_type: docs
title: "Promptfoo Code Scanning — VS Code Extension"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-23
date_extracted: 2026-09-23
last_checked: 2026-09-23
status: current
confidence_overall: emerging
issue: "#1418"
---

# Promptfoo Code Scanning — VS Code Extension

> The IDE-side surface of Promptfoo's LLM-security code scanner. The net-new
> contributions are narrow but quotable: an unqualified vendor retention claim
> ("not stored after analysis completes") for Ch06 data governance, an egress
> surface that lives on the developer's workstation rather than the CI runner,
> and a same-named `diffsOnly` knob that defaults to the **opposite** value
> (`true`) of the CLI's (`false`, #1264 Claim 5) — so identical-looking config
> means different scan coverage depending on which surface runs it.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Code Scanning VS Code Extension page)
- **Author credibility**: Promptfoo, the commercial LLM-security scanner vendor
  (now part of OpenAI per the site banner). First-party product documentation.
  The settings table and distribution path are documented product surface
  (verbatim, directly checkable from the page); scan behavior and the retention
  claim are vendor-positioned and, unlike the CLI (#1264), cannot be verified
  against an installed artifact because the extension ships only as a
  sales-gated `.vsix`.
- **Scope**: Covers the extension's feature list, install path (Enterprise-gated),
  manual/automatic scanning commands, `settings.json` surface with defaults,
  supported languages, severity display, and a one-paragraph Privacy statement.
  Does NOT cover the scanner's code-analysis methodology (far-tracing,
  call-graph — see `blog-promptfoo-building-security-scanner-llm-apps.md`),
  the CLI surface (#1264), or the GitHub Action CI wiring / SARIF publishing /
  supply-chain hardening (#1265).
- **Vendor caveat**: The extension is Enterprise-only and obtained via
  "Contact us" for a `.vsix` file. There is no marketplace listing, no published
  version, and no changelog. Every config key and behavior claim is therefore
  documented-but-unverifiable for anyone outside Promptfoo's customer list.
  Treat all runtime/behavior claims as vendor-reported; `confidence_overall` is
  `emerging` at best, consistent with the sibling notes (#1264, #1265).

## Extracted Claims

### Claim 1: The extension's scan-on-save loop is on by default, runs from the developer's workstation, and ships the file being edited to Promptfoo's SaaS API at every save — an egress surface distinct from the CI-runner egress already in the corpus
- **Evidence**: The settings table documents `promptfoo.scanOnSave` default
  `true` ("Auto-scan files on save") and `promptfoo.apiHost` default
  `https://api.promptfoo.app`; Usage states "Files are scanned when you save.";
  Supported Languages lists nine language families scanned by default, so the
  loop is active for any of them unless disabled. The Privacy section confirms
  code is sent to Promptfoo's servers.
- **Confidence**: emerging (documented defaults, but vendor-reported behavior on
  an enterprise-gated, unverifiable artifact)
- **Quote**: "Files are scanned when you save."
- **Our assessment**: Buy the documented surface. This is the first corpus
  evidence of code-scanning egress happening on an engineer's workstation
  rather than inside a CI runner: the existing notes frame egress as a CI
  problem (scans leave the runner — #1264 Claim 2, #1265 vendor caveat), and
  neither records an editor-side surface at all. Whether "source code leaves the
  endpoint on save" is a materially distinct governance concern from "source
  code leaves the CI runner" is the question for Ch06; the default-on posture
  (`scanOnSave: true`) means opting out is the active decision.

### Claim 2: Promptfoo's privacy statement asserts code sent for analysis "is not stored after analysis completes," but the page provides no mechanism, retention-window detail, audit trail, or contractual hook behind it — an unqualified vendor assertion, not a verifiable control
- **Evidence**: The Privacy section is a single sentence followed by the
  on-prem redirect. No link to a trust-center document, deletion mechanism, or
  retention policy appears on the page; the only alternative offered is
  Enterprise On-Prem.
- **Confidence**: anecdotal (vendor assertion; no independent verification
  possible given enterprise-gated distribution)
- **Quote**: "Code is sent to Promptfoo's servers for analysis and is not stored after analysis completes."
- **Our assessment**: Record it as vendor-claimed, not settled. The sentence is
  the quotable one for Ch06 §Data governance, but nothing on the page shows how
  "not stored" is enforced or audited, and neither sibling note (#1264, #1265)
  records any retention claim for the same backend. This is a softer statement
  than an audited control, and the triage explicitly asks that it be marked as
  such rather than promoted.

### Claim 3: The extension defaults `diffsOnly` to `true` while the CLI's `--diffs-only` defaults to `false` — the same-named knob means opposite scan coverage depending on which surface runs it
- **Evidence**: This page's settings table: `promptfoo.diffsOnly` — "Only
  analyze code diffs" — default `true`. The CLI page (docs-promptfoo-code-scan-cli.md,
  #1264 Claim 5): `--diffs-only` — "Scan only PR diffs, don't explore full
  repo" — default `false`, with the config-file comment "default: false =
  explore full repo".
- **Confidence**: settled for the documented default values on each page
  (verbatim, directly checkable); the behavioral consequence is vendor-positioned
- **Quote**: "Only analyze code diffs"
- **Our assessment**: The single most citable item on the page. A reader who
  configures the CLI for PR-diff-only (`diffsOnly: true`) and assumes the IDE
  matches gets the narrower-of-two interpretations, and a team that assumes
  "same scanner, same coverage everywhere" will be wrong in one direction or the
  other: the extension by default scans a narrower scope on the workstation
  (diffs only) while the CLI's default explores the full repo. Within-family
  divergence, not a corpus contradiction — both defaults are simultaneously true
  vendor documentation.

### Claim 4: The IDE defaults are more aggressive on when to scan (on-save, debounced 1500ms) and more conservative on scope (diffs only) than the CLI defaults, positioning the extension as a pre-CI, developer-loop complement rather than a gate
- **Evidence**: Settings defaults `promptfoo.scanOnSave` `true`,
  `promptfoo.scanOnSaveDebounceMs` `1500`, `promptfoo.diffsOnly` `true`,
  plus the page framing "before they reach your CI pipeline or production" and
  the manual command surface (Scan Current File / Scan Selection / Scan Git
  Changes / Clear All Scan Results / Show Output).
- **Confidence**: emerging (documented defaults; editor-ergonomics claims not
  independently verifiable)
- **Quote**: "Real-time scanning: Automatically scans files on save"
- **Our assessment**: The debounce is the concrete knob that prevents a scan
  storm while typing, and it is the IDE-side analogue of the CLI's runtime
  budget (#1264 Claim 3, 3–10 min typical). Worth citing as the shift-left
  complement to the PR gate, but the triage notes there is nothing here for the
  CI-gating material — the page explicitly positions this surface as pre-CI.
  Do not stretch this claim into a CI pattern.

### Claim 5: The extension is enterprise-gated end to end — contact-sales `.vsix`, installed via "Install from VSIX", no marketplace listing, no version, no changelog — so nothing on this page is reproducible or independently verifiable
- **Evidence**: The Enterprise Feature banner and Getting Started steps 1–2
  ("Contact us to get the extension package (`.vsix` file)"; "Install in VS
  Code: Extensions → ⋯ → Install from VSIX"). No marketplace URL, version
  number, or changelog appears anywhere on the page.
- **Confidence**: settled (the distribution path is stated plainly on the page)
- **Quote**: "The VS Code extension is available for Promptfoo Enterprise customers."
- **Our assessment**: This is the verifiability ceiling for the whole note.
  Unlike the CLI (installed via npm, `--help` checkable) or the GitHub Action
  (public repo, `gh attestation verify` — #1265 Claim 2), no guide reader can
  obtain this artifact without a vendor conversation. Every config key stays
  documented-but-unverified, which is why the confidence stays at
  `emerging` overall.

## Concrete Artifacts

### Settings table (verbatim rows from Configuration section)

| Setting | Description | Default |
|---------|-------------|---------|
| `promptfoo.apiHost` | Promptfoo API host URL | `https://api.promptfoo.app` |
| `promptfoo.minimumSeverity` | Minimum severity to display | `low` |
| `promptfoo.scanOnSave` | Auto-scan files on save | `true` |
| `promptfoo.scanOnSaveDebounceMs` | Debounce delay for auto-scan | `1500` |
| `promptfoo.diffsOnly` | Only analyze code diffs | `true` |
| `promptfoo.showCodeLens` | Show inline CodeLens annotations | `true` |
| `promptfoo.enabledLanguages` | Languages to scan | See below |

Source: promptfoo docs, "Configuration" section. Verbatim.

### Example settings.json (verbatim from Configuration section)

```
{  "promptfoo.minimumSeverity": "medium",  "promptfoo.scanOnSave": true,  "promptfoo.scanOnSaveDebounceMs": 2000,  "promptfoo.showCodeLens": true}
```

### Command Palette commands (verbatim from Usage section)

```
Promptfoo: Scan Current File — Scan the active file
Promptfoo: Scan Selection — Scan selected code
Promptfoo: Scan Git Changes — Scan all changed files in your branch
Promptfoo: Clear All Scan Results — Clear all diagnostics
Promptfoo: Show Output — Show the extension's output channel
```

### Supported languages (verbatim from Supported Languages section)

"By default, the extension scans: JavaScript / TypeScript (including JSX/TSX),
Python, Go, Java, Rust, Ruby, PHP, C#, C/C++... An empty array enables scanning
for all languages."

### Privacy statement (verbatim from Privacy section)

"Code is sent to Promptfoo's servers for analysis and is not stored after
analysis completes. For organizations that need to run scans on their own
infrastructure, the extension works with Promptfoo Enterprise On-Prem."

## Cross-References

- **Corroborates**:
  - `docs-promptfoo-code-scan-cli.md` **Claim 2** (scanner is SaaS-dependent;
    `--api-host` default `https://api.promptfoo.app`) — the extension's
    `promptfoo.apiHost` default is the IDE-side restatement of the same
    SaaS-by-default backend.
  - `docs-promptfoo-code-scan-github-action.md` vendor caveat (scans run
    against `https://api.promptfoo.app`; on-prem execution is Enterprise-only) —
    this page's Privacy section repeats the same on-prem escape hatch
    ("the extension works with Promptfoo Enterprise On-Prem").
- **Contradicts**: None. The extension's `diffsOnly: true` default is not a
  contradiction with #1264's `--diffs-only: false` — both are simultaneous,
  documented product defaults for two surfaces of the same product; no existing
  note claims either is universal. No contradiction issue filed.
- **Extends**:
  - `docs-promptfoo-code-scan-cli.md` **Claim 5** (`--diffs-only` default
    `false` = full-repo exploration) — this page documents the opposite default
    for the same knob on the IDE surface (Claim 3); together they establish the
    "same knob, different default per surface" divergence pattern.
  - `docs-promptfoo-code-scan-cli.md` **Claim 3** (PR scan runtime envelope,
    3–10 min typical) — the IDE's scan-on-save debounce (`scanOnSaveDebounceMs`,
    1500 ms) is the editor-side analogue of that runtime budget (Claim 4).
  - `blog-promptfoo-building-security-scanner-llm-apps.md` — the far-tracing
    methodology note (#292) now has a third deployment surface in the corpus:
    blog methodology (#292), CLI (#1264), GitHub Action (#1265), and now the
    IDE extension. The extension is a UI over the same scanner; no methodology
    is re-mined here per the sibling notes' coordination.
- **Novel**:
  1. **A vendor retention claim** — the first statement in the corpus that
     Promptfoo "is not stored after analysis completes"; neither #1264 nor
     #1265 records any retention claim for the same backend.
  2. **Workstation egress as a distinct surface** — code leaves the
     developer's machine via default-on scan-on-save, distinct from the
     CI-runner egress the existing notes document.
  3. **The `diffsOnly` default-divergence pattern** — same-named knob with
     opposite defaults (`true` here vs `false` in #1264) across two surfaces of
     one product.
  4. **Scan-on-save + debounce as a dev-loop cost control** — the concrete
     knob for avoiding a scan storm while typing.

## Guide Impact

- **Chapter 06 (Security and Trust)**, section "Data governance for AI
  workloads" (`guide/06-security-and-trust.md:509`): Add the vendor retention
  claim alongside the existing SaaS/data-egress material — "not stored after
  analysis completes" is vendor-asserted with no verifiable mechanism on this
  page, and the corpus should cite it as asserted, not settled. Also note the
  workstation-egress distinction: with `scanOnSave: true` default, source code
  leaves the endpoint on every save from an engineer's laptop, not just from a
  CI runner (Claims 1–2).
- **Chapter 06**, section "Gating on LLM security scans"
  (`guide/06-security-and-trust.md:768-781`, which already cites
  docs-promptfoo-code-scan-cli Claims 3/5/6): Add a caveat that the `--diffs-only`
  tradeoff cited there is surface-specific — the extension's `diffsOnly`
  defaults to `true` (Claim 3), so "PR-diff-only vs full-repo" depends on which
  surface runs the scan. A team reading the CLI config and assuming the IDE
  behaves identically is wrong in the default case.
- **Chapter 03 (Runbooks and Agents)**: The scan-on-save/debounce loop (Claim 4)
  is an editor-ergonomics, pre-CI surface; recommend not treating it as a CI
  gate. At most it belongs in agent-workstation setup notes as a shift-left
  complement.

## Extraction Notes

- Source read in full: https://www.promptfoo.dev/docs/code-scanning/vscode-extension
  (fetched via direct HTTP, rendered markdown). Single self-contained docs page;
  "Last updated on Sep 23, 2026" by renovate[bot]. No sub-pages followed — the
  only outbound content links are the code-scanning Overview / GitHub Action /
  CLI pages (all already mined or covered here) and the Enterprise On-Prem docs.
- Followed the Prospector triage guidance: extract net-new only, keep the note
  short (4–5 claims), and do NOT re-derive the severity taxonomy (#1264 Claim 6),
  the scanning premise (#1264 Claim 1), the SARIF/GHA publishing path (#1265),
  or the far-tracing methodology (#292).
- Cross-reference candidates file (`miner-related-notes.md`) read per MINER.md
  §4 before writing Cross-References. All 10 listed candidates dismissed as
  non-overlapping: `blog-pagerduty-sre-agent-triage.md` (AI incident triage),
  `docs-langfuse-mcp-server.md` (docs MCP server), `docs-google-sre-reliable-product-launches.md`
  (launch process), `docs-litellm-batches-api.md` (batch rate limiting),
  `blog-promptfoo-red-team-claude.md` (runtime model red-teaming), `docs-promptfoo-classifier-grading.md`
  (classifier grading), `docs-promptfoo-javascript-assertions.md` (JS assertions),
  `docs-google-sre-prodcast-04-05-furino-slos.md` (SLO construction),
  `blog-promptfoo-owasp-red-teaming.md` (runtime attack simulation; same
  thematic security-testing arena but no evidential overlap with the IDE
  settings surface — consistent with the #1265 dismissal), and
  `blog-incidentio-ai-sre-incident-run.md` (incident runs). The substantive
  cross-references (`docs-promptfoo-code-scan-cli.md`, `docs-promptfoo-code-scan-github-action.md`,
  `blog-promptfoo-building-security-scanner-llm-apps.md`) were found by
  searching `source-notes/`. Each cited claim was re-read and its number
  verified per MINER.md §4b before citation.
- All quoted passages and table rows were copied character-for-character from
  the fetched source; the settings table, example `settings.json`, command list,
  and Privacy paragraph were lifted verbatim rather than reconstructed.
- Vendor caveat reflected in confidence grading: the page is vendor docs, the
  artifact is enterprise-gated (`.vsix` via contact-sales, no version), so no
  behavior is independently verifiable. `confidence_overall` is `emerging`,
  matching the sibling notes; individual documented-default claims are graded
  `settled` only for the verbatim surface, with the retention claim explicitly
  `anecdotal`.