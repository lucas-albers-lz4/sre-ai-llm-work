---
source_url: https://www.promptfoo.dev/docs/configuration/telemetry
source_type: docs
title: "Promptfoo Configuration: Telemetry — Default-On Usage Egress, the Metadata Payload, and the Two Env-Var Opt-Outs"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-09
date_extracted: 2026-10-09
last_checked: 2026-10-09
status: current
confidence_overall: emerging
issue: "#1561"
---

# Promptfoo Configuration: Telemetry

> The vendor's own account of the CLI's default-on usage telemetry: an event
> fires on every command run (`init`/`eval`/`view`) and on every assertion use
> (recording the assertion *type*, e.g. `is-json`/`similar`/`llm-rubric`), the
> payload carries package version plus a CI flag (and, when account details are
> in the local config, user ID / email / cloud login status / auth method), the
> vendor names five exclusions (no prompts, model outputs, test cases, provider
> API keys, or full config files) — and the only documented opt-out is the
> environment variable `PROMPTFOO_DISABLE_TELEMETRY=1`, with a *separate*
> update-check egress path switched off by `PROMPTFOO_DISABLE_UPDATE=1`. The
> page discloses no endpoint, transport, retention window, or deletion path.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo configuration
  reference, "Evals > Runtime > Telemetry" page; the third page in the Runtime
  family after `/docs/configuration/caching/` and
  `/docs/configuration/rate-limits/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  This is the vendor's first-party description of its *own* client-side data
  collection, so it is authoritative for what the product is documented to
  collect and for the exact opt-out env vars — but it is a self-report, not an
  audited data-flow disclosure: the page names **no endpoint, host, transport,
  retention window, deletion mechanism, or schema**, and there is no
  independent verification of the exclusion list. Every behavioral claim is
  directly checkable against an installed CLI (`dbg`/network inspection), but
  the page itself publishes no evidence.
- **Scope**: Covers promptfoo CLI usage telemetry (event triggers, payload
  fields, documented exclusions, and the disable env var) and the separate
  NPM update-check egress path. Does NOT cover: the eval-result cache
  (`docs-promptfoo-configuration-caching.md`, #1275), the rate-limit/retry
  control plane (`docs-promptfoo-configuration-rate-limits.md`, #1545), the
  red-team/Enterprise control-plane audit trail
  (`docs-promptfoo-enterprise-audit-logging.md`), the code-scanning SaaS
  egress (`docs-promptfoo-code-scan-cli.md` #1264,
  `docs-promptfoo-code-scan-vscode-extension.md`), or self-hosted/on-prem
  telemetry behavior.
- **Last updated**: Oct 9, 2026 by `mldangelo-oai` (Docusaurus page footer).
  The Prospector triage saw the page dated Oct 2, 2026, so it was edited
  within the week before extraction — a reminder that a live vendor page can
  move under a source note, which is why `last_checked` is set to the
  extraction date.
- **Thin but concrete**: the page is roughly one screen of prose. It is
  retained as a source because the default-on egress posture and the exact
  opt-out variables are concrete, checkable, and previously uncovered by the
  corpus (zero `telemetry` / `PROMPTFOO_DISABLE_TELEMETRY` hits across the 49
  existing promptfoo notes); the note's value is a CI-hardening fact, not a
  pattern.

## Extracted Claims

### Claim 1: promptfoo CLI usage telemetry is **opt-out (on by default)** and collects usage data with no action required by the operator
- **Evidence**: The page's opening sentence states the default posture and the
  vendor's stated purpose; no opt-in, first-run prompt, or config key is
  documented.
- **Confidence**: settled (documented default behavior; directly checkable by
  watching network traffic from a fresh `promptfoo eval`)
- **Quote**: "promptfoo collects basic usage telemetry by default. This
  telemetry helps us decide how to spend time on development."
- **Our assessment**: Buy it, and treat it as the load-bearing fact of the
  page. The harness is explicitly designed to run unattended in CI and from
  developer laptops, so "default on" means an outbound connection happens
  without a deliberate decision and without appearing in the YAML a reviewer
  reads. This is the same default-on posture the corpus already documents for
  the eval-result cache (`docs-promptfoo-configuration-caching.md` Claim 1)
  and the code-scan loop (`docs-promptfoo-code-scan-vscode-extension.md`
  Claim 1) — three independent promptfoo surfaces that phone home or persist
  by default, none of which is visible in the eval config. The vendor's stated
  purpose ("decide how to spend time on development") also frames the data as
  product telemetry, not operational telemetry the customer gets back.

### Claim 2: An event fires on **every command run** (`init`, `eval`, `view`) and on **every assertion use**, and the assertion-use event includes the assertion *type* (e.g. `is-json`, `similar`, `llm-rubric`)
- **Evidence**: The "An event is recorded when:" bullet list names both
  triggers and the parenthetical examples of assertion types.
- **Confidence**: settled (documented event triggers)
- **Quote**: "A command is run (e.g. `init`, `eval`, `view`)" and "An
  assertion is used (along with the type of assertion, e.g. `is-json`,
  `similar`, `llm-rubric`)"
- **Our assessment**: Buy it. The command trigger is unsurprising for a usage
  metric, but the assertion-type dimension is the higher-signal part for a
  security/privacy reading: what leaves the machine is a signal about *how the
  team builds evals* — which grader families dominate (deterministic vs
  model-graded vs string-similarity) — which is methodology metadata even
  though it is not test content. Combined with Claim 1, an `eval` invocation
  in CI emits both a run event and one event per assertion type used, so
  assertion-heavy suites generate the most telemetry. The page does not state
  whether the assertion events are batched, one-per-instance, or
  one-per-type; that granularity is undocumented.

### Claim 3: The payload includes **package version** and a **CI flag**, and when account information is present in the local promptfoo config, *hosted* telemetry additionally includes promptfoo **user ID, email address, cloud login status, and authentication method**
- **Evidence**: The single-sentence payload paragraph naming the base fields
  and the conditional identity fields.
- **Confidence**: settled (documented payload fields)
- **Quote**: "Telemetry events include package version and whether the command
  is running in CI. When account information is present in the local promptfoo
  config, hosted telemetry also includes the promptfoo user ID, email address,
  cloud login status, and authentication method."
- **Our assessment**: Buy the field list, and note two operational
  consequences. First, the **CI flag** is the vendor's own segmentation of
  "automated pipeline" versus "human on a laptop" — an eval harness that
  reports whether it is running under CI is, by construction, designed to run
  in CI. Second, the identity enrichment is **conditional**: user ID, email,
  login status, and auth method are added only "when account information is
  present in the local promptfoo config," which ties telemetry at rest to
  whether credentials have been configured on that runner — and, because
  `{{ env.* }}` is resolved into the config at load time
  (`docs-promptfoo-configuration-guide.md` Claim 7), a config that interpolates
  a login from the environment can make that condition true in CI. The word
  "hosted" also implies the identity fields are gated on the hosted-service
  path; see Claim 7 for the ambiguity it creates.

### Claim 4: The vendor documents five exclusions — telemetry does **not** include prompts, model outputs, test cases, provider API keys, or full configuration files
- **Evidence**: The one-sentence exclusion list immediately after the payload
  paragraph.
- **Confidence**: settled as the vendor's *stated* payload boundary; anecdotal
  as a verifiable control (no schema, enforcement mechanism, or independent
  audit is cited)
- **Quote**: "Telemetry does not include prompts, model outputs, test cases,
  provider API keys, or full configuration files."
- **Our assessment**: This is the vendor's data-minimization claim and it is
  the reassuring half of the page — but read it precisely. It is an
  *assertion* about intended payload contents, not a control: no schema, no
  client-side redaction description, and no external attestation appears on
  the page (contrast the code-scan privacy statement, which the corpus already
  flags as an unqualified vendor assertion — `docs-promptfoo-code-scan-vscode-extension.md`
  Claim 2). The exclusions also leave a seam: "full configuration files" are
  excluded, but telemetry is *demonstrably* derived from config (the account
  fields in Claim 3 come from the local config), so the guarantee is
  "not the whole file," not "nothing from the file." For the guide the honest
  form is: the vendor says the payload excludes eval content, and the guide
  should not upgrade that to "the harness is safe to run on sensitive data"
  without an endpoint/retention control this page does not provide.

### Claim 5: The **only** documented opt-out is the environment variable `PROMPTFOO_DISABLE_TELEMETRY=1` — no YAML/config key is presented
- **Evidence**: The "To disable telemetry, set the following environment
  variable:" instruction and its single code block.
- **Confidence**: settled (documented control surface)
- **Quote**: "To disable telemetry, set the following environment variable:"
- **Our assessment**: Buy it, and this is the concrete hardening item. The
  control is **environment-only**: a team cannot switch telemetry off from the
  config it commits to the repo, so the decision must be re-applied on every
  CI runner image, every job step, and every developer machine. That is the
  opposite of the declarative-config pattern the rest of the tool uses — and it
  is consistent with `docs-promptfoo-configuration-guide.md`, whose config-key
  surface does not include telemetry. The practical rule for the guide: for a
  team that treats an eval harness as part of a hardened CI supply chain, this
  env var belongs in the runner's baseline environment (or container image),
  not in the eval YAML, because the YAML cannot carry it.

### Claim 6: The NPM update check is a **separate egress path** with its own switch, `PROMPTFOO_DISABLE_UPDATE=1` — so both variables must be set to fully silence the CLI's default network traffic
- **Evidence**: The "Updates" section describes the registry check and its
  banner, then gives the second disable variable.
- **Confidence**: settled (documented second egress path and its control)
- **Quote**: "The CLI checks NPM's package registry for updates. If there is a
  newer version available, it will display a banner to the user." and "To
  disable, set:"
- **Our assessment**: Buy it, and treat the two-switch structure as the
  operational gotcha. A team that reads the top of the page, sets
  `PROMPTFOO_DISABLE_TELEMETRY=1`, and stops has silenced the usage telemetry
  but **not** the package-registry lookup — the CLI still reaches out to NPM.
  In an air-gapped or egress-allowlisted environment this second path is the
  one that fails or must be permitted, and it is a different host (the public
  NPM registry) from whatever receives telemetry. The corpus's `PROMPTFOO_*`
  env-var convention (cache: `PROMPTFOO_CACHE_ENABLED`; rate limits:
  `PROMPTFOO_RETRY_5XX`) is the same toggle style, but this page is the first
  to document *two* independent off switches for two default-on behaviors, so
  the guide should present them as a pair and not as one "disable networking"
  flag.

### Claim 7: The account-identity fields are gated on "**hosted** telemetry," implying a local/offline emission path whose payload is not separately documented
- **Evidence**: The qualifier in the Claim 3 sentence — identity fields apply
  to "hosted telemetry" specifically, while the base fields (package version,
  CI flag) are unconditional.
- **Confidence**: emerging (the wording supports the inference but the page
  never names a non-hosted endpoint or says what a fully local install emits)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: Do not over-read, but flag it. The sentence contrasts
  unconditional base fields with conditional "hosted telemetry" identity
  fields, which reads as: telemetry is emitted from the CLI regardless, and the
  hosted service *additionally* enriches it with account identity when
  credentials are present. If that reading is right, then the opt-out variable
  must suppress the whole path (it is the only switch), and the page simply
  does not tell an operator what leaves a machine that has never logged in.
  The guide should record this as an open question rather than resolve it: the
  page answers "what is collected when account info is present," not "what is
  collected in a clean, credential-less install."

### Claim 8: The page documents no destination, transport, retention window, deletion path, CI auto-disable, air-gapped/proxy guidance, or org-level opt-out — the reassurance is a payload-content statement, not an egress-control statement
- **Evidence**: Full read of the page (it is one screen). Every operational
  detail on this list is simply absent; the page offers only the payload
  description, the exclusions, and the two disable variables.
- **Confidence**: settled as a claim about the *documentation* (verifiable by
  reading the entire page); the underlying unstated behavior is unknown rather
  than proven absent
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the negative-space finding that makes the note
  useful and it should be stated as *undocumented*, not *disabled*. A team
  asked to approve promptfoo in a sensitive CI environment needs to know where
  the data goes and how long it is kept to write a data-flow review or a
  deletion request; this page supplies neither the hostname to allow-list nor
  a retention term. That is the same shape as the code-scan privacy assertion
  (`docs-promptfoo-code-scan-vscode-extension.md` Claim 2: "not stored after
  analysis completes" with no mechanism) and the audit-logging gap
  (`docs-promptfoo-enterprise-audit-logging.md`: retrieval documented,
  retention not). The guide's actionable form: the only lever this page gives
  an operator is the all-or-nothing env-var opt-out (Claims 5–6), so the
  defensible posture for a restricted runner is to set both variables and
  treat the endpoint/retention questions as unanswered rather than assumed
  harmless.

## Concrete Artifacts

### Event triggers (verbatim from the page's "An event is recorded when:" list)

```
- A command is run (e.g. `init`, `eval`, `view`)
- An assertion is used (along with the type of assertion, e.g. `is-json`, `similar`, `llm-rubric`)
```

### Payload fields and documented exclusions (verbatim, two adjacent paragraphs)

```
Telemetry events include package version and whether the command is running in CI. When account information is present in the local promptfoo config, hosted telemetry also includes the promptfoo user ID, email address, cloud login status, and authentication method.

Telemetry does not include prompts, model outputs, test cases, provider API keys, or full configuration files.
```

### Telemetry opt-out (verbatim from the page)

```
PROMPTFOO_DISABLE_TELEMETRY=1
```

### Update-check egress and its opt-out (verbatim from the "Updates" section)

```
The CLI checks NPM's package registry for updates. If there is a newer version available, it will display a banner to the user.

To disable, set:

PROMPTFOO_DISABLE_UPDATE=1
```

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/telemetry
— "Telemetry" and "Updates" sections. Copied character-for-character from the
rendered page.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-code-scan-cli.md` **Claim 2** ("A bare CLI
    scan runs against the Promptfoo-hosted API and requires Promptfoo account
    authentication — the scanner is SaaS-dependent, not standalone") and
    `source-notes/docs-promptfoo-code-scan-vscode-extension.md` **Claim 1**
    ("The extension's scan-on-save loop is on by default ... ships the file
    being edited to Promptfoo's SaaS API at every save — an egress surface
    distinct from the CI-runner egress already in the corpus") — together these
    are the corpus's existing "promptfoo egresses by default" material. This
    telemetry page adds a third, *content-lighter* egress surface (metadata,
    not the scanned file/prompt) and, crucially, the first one attached to the
    plain `eval`/`view` command rather than to the code scanner. The guide's
    Ch06 egress story should list all three. (Verified: #1264 Claim 2 and the
    code-scan-vscode note's Claim 1.)
  - `source-notes/failure-litellm-guardrail-logging-secret-exposure.md`
    (root-cause section: "guardrail logging is itself an output path ... and
    must be treated with the same security posture as any other API response";
    "guardrail_response could be written as a span attribute on guardrail
    spans" — "visible to anyone with access to the relevant telemetry
    backend") — that failure note establishes that an observability/telemetry
    channel is an egress surface that can carry more than intended. This page
    is the same architectural point from the vendor-design side: an eval
    harness's usage telemetry is an output path, so its documented exclusions
    (Claim 4) deserve the same "verify the boundary" scrutiny that incident
    demands. (Verified: the named failure note's Root Cause section.)

- **Contradicts**: None identified, and no contradiction issue filed. Verified
  against `CONTRADICTIONS.md` and the corpus. Nothing on this page opposes an
  existing note: the exclusions (Claim 4) and the code-scan egress claims are
  complementary (different data classes on different features), not competing,
  and the default-on posture agrees with the caching note's account of
  promptfoo defaults. The closest "tension" is thematic — the vendor asserts
  payload minimization while disclosing no retention/endpoint — but that is an
  absence of documentation, not an opposing claim, so per MINER.md §4a it is
  recorded here rather than filed.

- **Extends**:
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 7**
    (`{{ env.X }}` is "resolved at config load time (not runtime)," and the
    vendor warns that secrets copied into `config.env` "may appear in exported
    results") — the config guide owns promptfoo's env-var/secret handling and
    its config-key surface, which notably does **not** contain a telemetry key.
    This note's env-var-only opt-out (Claim 5) is the runtime-side counterpart:
    the same tool that resolves env vars at load time also controls its own
    egress only through env vars, so a committed config can neither carry the
    secret safely nor switch off telemetry. Read together they define the
    config's *non*-coverage of both secret declaration and egress control.
    (Verified: #1513 Claim 7.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 9** (the
    env-var control surface `PROMPTFOO_CACHE_ENABLED` / `_TYPE` / `_PATH` /
    `_TTL`, with `PROMPTFOO_CACHE_ENABLED` default `true`) — the caching note
    documents the sibling Runtime page's default-on, env-var-toggled behavior.
    This note is the same design pattern applied to network egress: a
    default-on capability whose only control is a `PROMPTFOO_*` env var, set
    outside the eval config. (Verified: #1275 Claim 9.)
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 2**
    (administrative actions are logged, while "Evaluation runs, prompt
    testing, and other data plane operations are tracked separately" — with no
    named destination) — this telemetry page is a *candidate* for what "data
    plane operations are tracked separately" points at, but the audit-logging
    note's own point is that the target is unnamed, and this page names no
    destination either. Cite it as a research lead, not a resolution: the
    corpus now has both halves of the sentence — a control-plane audit trail
    and a data-plane usage signal — and neither documents retention or a
    retrievable endpoint. (Verified: the audit-logging note's Claim 2.)
  - `source-notes/docs-promptfoo-pi-scorer.md` **Claim 2** ("`pi` requires a
    separately-issued third-party credential ... unlike `llm-rubric`, it does
    not run on your existing providers") and **Claim 9** ("The graded payload
    is the eval's own input/output pair — the page names the fields
    `llm_input` and `llm_output`") — the `pi` grader is a *content-level*
    egress path (the eval's input/output go to a third party), whereas this
    page's telemetry is a *metadata-level* egress path from the CLI itself.
    Extending the corpus's egress inventory with the distinction matters: the
    hardening lever differs (choose/avoid the `pi` grader vs.
    `PROMPTFOO_DISABLE_TELEMETRY=1`), and a team can be compliant on one while
    leaking on the other. (Verified: the pi-scorer note's Claims 2 and 9.)

- **Novel**: New to the corpus (verified by grep: zero hits for `telemetry` or
  `PROMPTFOO_DISABLE_TELEMETRY` across the 49 pre-existing promptfoo notes and
  `guide/`). Specifically new:
  1. **The default-on CLI usage-telemetry posture** for the eval harness
     (Claim 1) and its event triggers (Claim 2) — the first corpus statement
     that the *base* `promptfoo eval`/`view` command egresses, independent of
     the code scanner.
  2. **The assertion-type dimension** of the event payload (Claim 2) — a
     methodology-metadata field not previously documented for any promptfoo
     surface.
  3. **The documented exclusions list** (Claim 4) as the vendor's
     data-minimization boundary — and its status as an unverified assertion.
  4. **The two-switch opt-out** — `PROMPTFOO_DISABLE_TELEMETRY=1` for usage
     events (Claim 5) plus the *separate* `PROMPTFOO_DISABLE_UPDATE=1` for the
     NPM update check (Claim 6), the latter being the first corpus mention of
     the CLI's registry lookup at all.
  5. **The documented-gap set** — no endpoint, transport, retention, deletion,
     CI auto-disable, proxy/air-gap guidance, or org-level opt-out (Claim 8).

## Guide Impact

- **Chapter 06 (Security and Trust)** — CI supply-chain / eval-container
  hardening: add a concrete default-on egress item for LLM eval harnesses.
  This source gives the exact hardening recipe: set **both**
  `PROMPTFOO_DISABLE_TELEMETRY=1` and `PROMPTFOO_DISABLE_UPDATE=1` on CI
  runners and eval containers (Claims 5–6), because the usage telemetry and
  the NPM update check are two independent egress paths and silencing one
  leaves the other. State explicitly that the switch is **environment-only**
  (Claim 5) — it cannot be committed in the eval YAML — so it belongs in the
  runner baseline or image, and that the payload includes package version, a
  CI flag, and (when credentials are configured on the runner) user ID/email/
  auth method (Claim 3). Pair it with the existing promptfoo egress notes so
  the guide presents one consolidated "what this harness sends by default"
  list: the code scanner (CLI **and** VS Code, #1264 / code-scan-vscode note),
  the `pi` grader (pi-scorer note), and now CLI usage telemetry.
- **Chapter 06** — *"A vendor privacy assertion is not a control"* pattern:
  add this page as a second instance. The vendor states five exclusions
  (Claim 4) but discloses no endpoint, retention window, or deletion path
  (Claim 8) and offers only an all-or-nothing env-var opt-out. The guide's
  rule: treat a payload-content reassurance as a claim to verify, and where
  egress cannot be scoped, use the off switch rather than assuming the
  exclusions cover the sensitivity of the workload. Cite alongside the
  code-scan privacy-assertion note (Claim 2) and the audit-logging
  retention gap.
- **Chapter 05 (LLM Ops Reliability)** — Ops/observability boundary: one line
  to note that this "telemetry" is *vendor-facing usage analytics*, not the
  operator's own observability. It is not the audit trail
  (`docs-promptfoo-enterprise-audit-logging.md`: eval/data-plane operations
  are "tracked separately" with no named destination) and it does not return
  useful telemetry to the customer. Keep the guide's "telemetry" vocabulary
  distinct from "the vendor's product analytics" so a reader does not mistake
  the env-var opt-out for disabling operational logging.

## Extraction Notes

- Source read in full via direct HTTP fetch of the rendered Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/telemetry). It is a very short
  page — one screen of prose, two code blocks, one bullet list — so this note
  is deliberately claim-light and lead-heavy rather than padded. Quotes were
  verified character-for-character against the fetched content, including the
  backticked identifiers (`init`/`eval`/`view`, `is-json`/`similar`/`llm-rubric`)
  and the two env-var blocks. No sub-pages were followed: the page links only
  to its Runtime siblings (`Caching`, `Rate Limits`), which are already mined
  (#1275, #1545) and add no telemetry surface.
- `date_published` uses the page footer's "Last updated on **Oct 9, 2026** by
  **mldangelo-oai**". The issue body and the Prospector triage comments
  (2026-10-02) reference the page as dated Oct 2, 2026, so the page was edited
  within the week before extraction; `last_checked` is set to the extraction
  date (2026-10-09).
- **Cross-reference candidate handling** (`miner-related-notes.md` read before
  writing Cross-References, per MINER.md §4; candidates are suggestions only,
  each cited or dismissed by name):
  - `docs-promptfoo-enterprise-findings-reports.md` — findings/reports and the
    export-disposition surface; no telemetry or CLI-egress content. **Dismissed.**
  - `docs-promptfoo-pi-scorer.md` — **cited** (Extends): the `pi` grader is a
    content-level third-party egress path; cited Claims 2 and 9 were re-read
    and number-verified.
  - `docs-google-sre-team-lifecycles.md` — SRE team organization; unrelated.
    **Dismissed.**
  - `blog-promptfoo-owasp-red-teaming.md` — red-team methodology and CI/CD
    placement; same vendor and CI theme but no telemetry/egress surface.
    **Dismissed.**
  - `docs-promptfoo-enterprise-audit-logging.md` — **cited** (Extends): the
    only-adjacent promptfoo control-plane/audit note; cited Claim 2 re-read and
    number-verified. The relationship is "the audit note says data-plane
    operations are tracked separately with no named destination; this page
    names no destination either," recorded as a lead, not a resolution.
  - `docs-litellm-batches-api.md` — LiteLLM batch API; unrelated vendor and
    topic. **Dismissed.**
  - `blog-pagerduty-sre-agent-triage.md` — AI incident triage; unrelated.
    **Dismissed.**
  - `docs-promptfoo-classifier-grading.md` — classifier assert type; no
    telemetry content. **Dismissed.**
  - `docs-promptfoo-javascript-assertions.md` — JS assertion mechanics; no
    telemetry content. **Dismissed.**
  - `docs-promptfoo-llm-rubric.md` — model-graded rubric mechanics; no
    telemetry content. **Dismissed.**
  - Additional cross-references found by searching `source-notes/` (per the
    Prospector's "none directly overlap" note and MINER.md §4): the
    `docs-promptfoo-configuration-guide.md` (Claim 7),
    `docs-promptfoo-configuration-caching.md` (Claim 9),
    `docs-promptfoo-code-scan-cli.md` (Claim 2),
    `docs-promptfoo-code-scan-vscode-extension.md` (Claim 1), and
    `failure-litellm-guardrail-logging-secret-exposure.md` (Root Cause
    section). Each cited claim/section was re-read and verified per MINER.md
    §4b before citation.
- **Contradiction handling**: no contradiction issue filed. Checked
  `CONTRADICTIONS.md` and the corpus; the page raises no opposing claim. The
  vendor's exclusion assertion vs. its undocumented retention/endpoint is an
  absence of documentation, not a contradiction with another source, so per
  MINER.md §4a it is captured as a research lead in Cross-References/Claim 8
  rather than filed.
- `confidence_overall` is `emerging`, not `settled`: the individual
  documented facts (default-on, triggers, payload fields, exclusions, the two
  env vars) are settled-for-product-behavior and directly checkable against an
  installed CLI, but the page is a thin, self-reported vendor page with **no**
  measured evidence, no endpoint/retention detail, and no independent
  validation — and the exclusions are an unverified assertion rather than a
  control. Consistent with the sibling Runtime notes (#1275, #1545) and the
  code-scan notes, which also land at `emerging`.
