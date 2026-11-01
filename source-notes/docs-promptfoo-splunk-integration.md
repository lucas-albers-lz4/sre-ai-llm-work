---
source_url: https://www.promptfoo.dev/docs/integrations/splunk
source_type: docs
title: "Promptfoo × Splunk HEC — The Red-Team-to-SIEM Recipe and Its Silent Failure Modes"
author: "Promptfoo (vendor documentation; page last updated by renovate[bot])"
date_published: 2026-11-01
date_extracted: 2026-11-01
last_checked: 2026-11-01
status: current
confidence_overall: emerging
issue: "#1934"
---

# Promptfoo × Splunk HEC

> The vendor's end-to-end recipe for promoting failed red-team findings into a
> Splunk SIEM — a scheduled batch job that runs a scan, exports the latest eval
> to JSON, transforms failures with an **unpinned personal-gist script**, and
> POSTs each finding to HEC under `sourcetype=promptfoo:redteam` — together with
> the two tradeoffs the recipe does not reconcile: `PROMPTFOO_PASS_RATE_THRESHOLD=0`
> deliberately stops the CI job from gating on findings, and the OSS export
> carries no severity, so the page's `severity IN ("high","critical")` alert
> depends on a mapping the page never defines.

## Source Context

- **Type**: docs (vendor integration page, promptfoo × Splunk). The page sits
  under "Integrations" and is not Enterprise-gated; it explicitly claims to work
  "with Splunk Cloud Platform and Splunk Enterprise without a Promptfoo-specific
  Splunk app."
- **Author credibility**: Promptfoo, maintainer of the eval/red-team harness,
  documenting its own export command and a community-contributed transformer.
  Authoritative for the *vendor*-owned surfaces (`promptfoo redteam run`,
  `promptfoo export eval`, `PROMPTFOO_PASS_RATE_THRESHOLD`,
  `PROMPTFOO_STRIP_*`, the HEC endpoint shape). **Not** authoritative for the
  transformer: the page points at a public gist under a personal account
  (`ianw-oai`), so the mapping code is third-party, not vendor specification.
  The page is machine-maintained (footer: "Last updated on **Nov 1, 2026** by
  **renovate\[bot\]**"); it contains no eval run, no captured HEC response, no
  failure trace, and no measurement of any kind.
- **Scope**: Covers prerequisites (HEC token, HEC endpoint forms), exporting the
  latest eval, running the transformer, a complete GitHub Actions workflow, two
  example SPL queries, the Enterprise webhook alternative, and three security
  notes. Does **not** cover retry/backoff, dead-letter handling, delivery
  confirmation, deduplication/idempotency, ordering, event schema/versioning,
  severity mapping for the OSS path, token rotation, index retention, or any
  measurement of delivery behavior.
- **Relationship to sibling pages**: this is the **push-to-SIEM** counterpart to
  `source-notes/docs-promptfoo-enterprise-webhooks.md` (the Enterprise webhook
  event model, which documents the same delivery-guarantee absences) and the
  outbound counterpart to `source-notes/docs-promptfoo-langfuse-integration.md`
  (Langfuse as an inbound trace/prompt backend). The red-team finding object
  itself is owned by `source-notes/docs-promptfoo-enterprise-findings-reports.md`.

## Extracted Claims

### Claim 1: The integration's scope is deliberately failure-only — it ingests "failed Promptfoo red team results" into a SIEM, so successful probes never become SIEM events
- **Evidence**: The page's opening sentence states the purpose and the two
  supported Splunk deployment forms; the Overview then lists the four stages,
  ending at "Search, alert, or dashboard on those events in Splunk."
- **Confidence**: settled (documented scope)
- **Quote**: "Use Splunk's HTTP Event Collector (HEC) to ingest failed Promptfoo red team results as SIEM events. This works with Splunk Cloud Platform and Splunk Enterprise without a Promptfoo-specific Splunk app."
- **Our assessment**: Buy it, and read the consequence: the SIEM stream is a
  *finding* feed, not a *coverage* feed. A successful adversarial probe — the
  evidence that a defense held — produces no event, and neither does a scan that
  ran clean, a scan that was skipped, nor a scan that errored before producing
  results. That is a reasonable SIEM design (you alert on failures, not
  successes), but it means the SIEM cannot answer "how much red-team coverage
  did we run this week?" from this stream alone. The page never says the export
  is filtered to failures at the source; the filtering happens in the
  transformer (Claim 5), so the export artifact still contains everything. For
  the guide: a findings-to-SIEM pipeline is an alerting input, not an
  audit-of-coverage input.

### Claim 2: The documented pipeline is a four-stage batch job coupled by a local JSON file and the mutable `latest` pointer, not an event-driven integration
- **Evidence**: The Overview enumerates the four stages, and the Export section
  gives two commands — scan, then `export eval latest` — plus an alternative for
  a known eval ID.
- **Confidence**: settled (documented command sequence)
- **Quote**: "Run a Promptfoo red team scan." / "Export the latest eval to JSON." / "Transform failed red team results into Splunk HEC events." / "If you already have a specific eval ID, export that instead of `latest`:"
- **Our assessment**: Buy the sequence, and flag the coupling. In the documented
  GitHub Actions workflow the whole sequence runs in one job, so `latest`
  normally resolves to the eval the job just produced. But `latest` is a
  *mutable pointer*, not a binding: if the scan step is skipped, if two evals
  share a workspace, or if the export is run out-of-band, `latest` can select a
  different eval than intended, and the page's own alternative (an explicit eval
  ID) is not used in the workflow. There is also no schema/version handshake
  between the exported JSON and the transformer; the transformer treats the file
  as an unversioned contract (Claim 5). The guide rule: in CI, bind the export
  to the eval ID the scan produced (or assert the exported `evalId`), rather
  than relying on `latest`.

### Claim 3: The page recommends `PROMPTFOO_PASS_RATE_THRESHOLD=0` in CI specifically so the scan step does not fail the pipeline on findings — which means the pipeline's exit code stops being a security gate
- **Evidence**: The Export section states the override and the reason
  ("continue to the Splunk upload even when the scan finds failed tests"), and
  the GitHub Actions workflow sets it in the scan step's `env`.
- **Confidence**: settled (the override and its stated purpose are verbatim; the
  gate consequence is our derivation)
- **Quote**: "In CI, set `PROMPTFOO_PASS_RATE_THRESHOLD=0` on the scan step if you want the pipeline to continue to the Splunk upload even when the scan finds failed tests."
- **Our assessment**: This is the page's most important operational tension.
  A red-team job whose job is *shipping findings to the SIEM* cannot abort on
  findings, so the recipe intentionally disables the usual promptfoo CI gate. A
  threshold of `0` means even a scan in which every test failed exits
  successfully, and the workflow's green check then means "the upload step ran",
  not "the scan was clean." That is defensible for a data-pump job, but it is
  unsafe if the same job is also treated as a deploy gate: the security signal
  has moved entirely to the SIEM/SPL side (Claim 7), and the CI job no longer
  carries it. The guide should say this explicitly: **when you set the pass-rate
  threshold to zero to keep an upload alive, you have converted the red-team job
  from a gate into a data pump — run a separate gating job (threshold > 0) if
  you also need the build to block, and alert on the SIEM side for the pump.**
  The page presents the override as a convenience and never states this
  consequence.

### Claim 4: The transformer is fetched at job time from an unpinned, unversioned personal GitHub gist via `curl -L`, and the workflow also installs promptfoo globally without a version pin — a supply-chain hazard inside a security pipeline
- **Evidence**: The "Send findings to Splunk HEC" section links the
  `promptfoo-to-splunk.mjs` gist, and the GitHub Actions example's "Download
  Splunk transformer" step fetches
  `https://gist.githubusercontent.com/ianw-oai/418470829f7feff8e52a24ad6d028402/raw/promptfoo-to-splunk.mjs`
  with `curl -L`. The same workflow runs `npm install -g promptfoo` with no
  version.
- **Confidence**: settled (the URL, `curl` invocation, and unpinned `npm install`
  are verbatim in the workflow)
- **Quote**: "Use the public `promptfoo-to-splunk.mjs` transformer gist." / "run: npm install -g promptfoo"
- **Our assessment**: Do not buy this part of the recipe for a production
  security pipeline. The `/raw/` gist URL is a moving target — it serves the
  latest revision of a file controlled by a personal account, with no commit
  SHA, checksum, release tag, or package version — and it executes in a step
  that holds `SPLUNK_HEC_TOKEN` in its environment and can read the exported
  red-team results. A silent change to the gist is a code-execution path with
  the HEC write token and the exported findings in scope. The same workflow also
  installs `promptfoo` from npm with no pin, so the scanner binary itself floats.
  This is especially pointed because the page gets adjacent supply-chain advice
  right: it says to "fix certificate trust rather than disabling TLS
  verification in CI" and to store HEC/provider credentials as CI secrets. The
  guide rule: **pin or vendor the transformer (commit SHA + checksum, or copy it
  into the repo and review it), and pin the scanner version; a URL fetched at
  runtime is not a dependency you control.** Contrast with the corpus's
  `docs-promptfoo-code-scan-github-action.md`, whose Claim 8 records the
  vendor's own SHA-pinning convention for the scanner Action.

### Claim 5: The documented event contract is a field mapping plus `source: promptfoo` / `sourcetype: promptfoo:redteam`, but the field *names* used by the SPL queries are defined only by the unpinned gist, not by the vendor page
- **Evidence**: The prose describes the mapping ("plugin ID, strategy ID, score,
  attack prompt, target output, and share URL") and names the `source` and
  `sourcetype`; the two SPL examples then query `plugin_id`, `strategy_id`,
  `provider`, `severity`, `score`, `attack_prompt`, `failure_reason`,
  `shareable_url`, and `eval_id`. The page never publishes the per-finding JSON
  event body or a schema version (it does publish the Enterprise webhook
  envelope — Claim 10); the gist's `toFinding()` defines those keys (Concrete
  Artifacts → observed third-party transformer).
- **Confidence**: settled (mapping prose, `source`/`sourcetype`, and SPL field
  names are verbatim; the "only the gist defines the keys" observation is
  confirmed by reading the fetched gist on 2026-11-01)
- **Quote**: "It reads `redteam-results.json`, filters failed red team assertions, maps Promptfoo fields like plugin ID, strategy ID, score, attack prompt, target output, and share URL into a Splunk HEC event, then sends each finding with `source: promptfoo` and `sourcetype: promptfoo:redteam`." / "Splunk's HEC event format supports top-level metadata such as `time`, `host`, `source`, `sourcetype`, and `index`."
- **Our assessment**: Buy the mapping as the conceptual contract, but note the
  documentation seam: the vendor documents the *idea* of the mapping and the SPL
  uses concrete snake_case field names that only the third-party gist supplies.
  The practical consequence is that the query contract is not owned by the
  vendor: a gist revision can rename `attack_prompt` or change the severity
  default and silently break every saved SPL alert, with no version to detect
  the change. The only stable key the vendor actually promises is the
  `sourcetype` (`promptfoo:redteam`), which is therefore the right thing to
  build indexes/searches around. The top-level `time`, `host`, `source`,
  `sourcetype`, and `index` metadata are a documented HEC shape; the event body
  is not.

### Claim 6: The SIEM becomes a store of offensive payloads and potentially application data; the page's access-control story is index/token scoping plus two opt-in strip flags, with no documented redaction of the attack prompt itself
- **Evidence**: The Security notes section makes three statements: treat results
  as sensitive because attack prompts and target outputs can contain harmful
  content or application data; restrict the Splunk index and HEC token to the
  teams that need access; and use `PROMPTFOO_STRIP_RESPONSE_OUTPUT=true` or
  `PROMPTFOO_STRIP_TEST_VARS=true` to reduce what leaves CI. The transformer
  sends `attack_prompt`, `target_output`, and `shareable_url` (observed gist).
- **Confidence**: settled (all three statements are verbatim; the payload fields
  are confirmed from the fetched gist)
- **Quote**: "Treat exported red team results as sensitive. Attack prompts and target outputs can contain harmful content or application data." / "Restrict the Splunk index and HEC token to the teams that need access." / "Use `PROMPTFOO_STRIP_RESPONSE_OUTPUT=true` or `PROMPTFOO_STRIP_TEST_VARS=true` if you need to reduce what leaves the CI environment."
- **Our assessment**: Buy the warning and read it as an egress decision, which is
  the same shape as the corpus's guardrail-egress rule. The SIEM event can carry
  the adversarial prompt that elicited a failure, the target's raw output, and a
  share link — i.e. the most sensitive payload in the whole eval pipeline is
  being copied into a security index with broader read access than the CI
  workspace. The only documented controls are (a) scope the HEC token/index, so
  the write credential cannot reach unrelated indexes, and (b) opt into response
  or variable stripping. There is no documented redaction of the attack prompt
  itself, no default for the strip flags, and no statement of what exactly they
  remove; the share URL is an additional egress path if promptfoo sharing is
  enabled. Guide rule: **treat a findings SIEM as a sensitive data store —
  scope the write token, decide explicitly whether attack prompts and target
  outputs are allowed to persist there, and do not assume `PROMPTFOO_STRIP_*`
  makes the event safe without reading what it strips.**

### Claim 7: The OSS path carries only pass/fail and score; severity is an operator mapping the page never defines, so the page's own `severity IN ("high","critical")` alert can be inert on open-source findings
- **Evidence**: The "Search in Splunk" section states the edition asymmetry and
  tells the reader to "Tune severity mapping to your internal policy"; the
  example alert filters on `severity IN ("high", "critical")`; the page never
  gives a mapping table or default. The observed gist fills severity from
  `metadata.severity` and otherwise defaults to `medium` via
  `PROMPTFOO_SPLUNK_DEFAULT_SEVERITY || 'medium'`.
- **Confidence**: settled as a description of the page's documented gap
  (full-text read plus the fetched gist); the *behavior* of any particular
  promptfoo version's metadata is not independently measured here
- **Quote**: "Tune severity mapping to your internal policy. The open-source eval export contains per-result pass/fail and score fields; Promptfoo Enterprise findings include vulnerability status and severity that are better suited for long-lived SIEM case management." / "severity IN (\"high\", \"critical\")"
- **Our assessment**: This is the subtlest trap on the page, and it is worth
  recording explicitly because the page presents the alert as ready-to-use. On
  the OSS path the export has no documented severity field, so the alert only
  fires if (a) the finding metadata already carries a severity value or (b) the
  operator supplies a default/mapping — and the observed gist's default is
  `medium`, which is *below* the alert's threshold. In other words, the
  documented high/critical alert can silently never fire for OSS findings that
  lack metadata severity: the pipeline is healthy, events are in the index, and
  the "high-priority" alert is quiet. Enterprise findings are the path that
  carries real severity/status, which is consistent with
  `docs-promptfoo-enterprise-findings-reports.md` Claim 11 (no severity
  vocabulary on the OSS findings page) and Claim 2 (severity is org-relative).
  Guide rule: **when a SIEM alert keys on a field the export does not carry, the
  missing field is either defaulted below the alert threshold or absent — either
  way the alert is not testing what its name says.** Define and test the
  severity mapping end-to-end before trusting the alert.

### Claim 8: The documented HEC path has no retry, backoff, dead-letter, delivery confirmation, or idempotency key — and the fetched transformer aborts the remaining findings on the first non-OK POST
- **Evidence**: Full-page read: *retry*, *backoff*, *dead-letter*, *delivery
  guarantee*, *ordering*, *timeout*, *deduplicate*, and *idempotency* do not
  appear; the only failure behavior is the transformer's own error. The fetched
  gist's `sendFinding` throws on `!response.ok`, and the send loop
  (`for (const result of failedResults) { await sendFinding(...) }`) has no
  catch, so one failed POST stops every subsequent finding.
- **Confidence**: settled as a description of what this page and the fetched
  gist document (full-text read of both); the product-level absence is recorded
  as undocumented, not nonexistent
- **Quote**: "You can run the export and Splunk upload manually, but most teams put this in CI/CD so SIEM data stays current." / "(no direct quote for retry/backoff/dead-letter; see paraphrase in Our assessment)"
- **Our assessment**: Do not buy this as a reliable delivery path. The vendor
  commits to a *recipe* for producing POSTs; it commits to nothing about what
  happens when a POST fails. The observed transformer is fire-and-forget with a
  fail-fast loop: if HEC rejects or is unreachable at finding N, findings
  N..end are never sent, the job fails, and there is no queue to replay them on
  the next run unless the next run re-exports the same eval (which the `latest`
  pointer does not guarantee — Claim 2). There is no idempotency key, so the
  natural recovery (re-run the job) can duplicate the findings that did land.
  This is the same documented-absence pattern as
  `docs-promptfoo-enterprise-webhooks.md` Claim 7, but here it is arguably
  worse: the operator owns the code and still ships no durability. Guide rule:
  **a SIEM push is best-effort until it has retry/backoff, a dead-letter path,
  and an idempotency key; otherwise reconcile from the exported eval and alert
  on the absence of expected events.** The corpus's Langfuse contrast
  (`docs-langfuse-alerts.md` Claim 8: a five-failure circuit breaker) shows what
  a documented delivery contract looks like.

### Claim 9: Freshness is bounded by a daily cron (`0 8 * * *`) plus manual dispatch — there is no event-driven trigger from the scan, so a finding can sit outside the SIEM for up to a day
- **Evidence**: The GitHub Actions example's `on:` block has `workflow_dispatch`
  and one schedule entry, `- cron: '0 8 * * *'`; the page's justification is
  "so SIEM data stays current".
- **Confidence**: settled (the trigger block is verbatim)
- **Quote**: "- cron: '0 8 * * *'"
- **Our assessment**: Buy the schedule and state its bound. A daily batch is a
  defensible cost choice, but "current" here means "at most ~24 hours stale",
  and the page does not discuss the detection-latency implication: a critical
  finding from a 09:00 scan does not reach the SIEM until the next 08:00 run.
  Worse, a missing upload is indistinguishable in the SIEM from "no findings" —
  the only failure signal is the GitHub Actions run itself. The guide should pair
  this with a completion/missing-event alert: trigger on scan completion (or use
  a shorter cadence for high-severity targets), and alert when the expected
  daily event volume for a `sourcetype` drops to zero, so a broken cron is not
  read as a clean day. This is the SIEM-side analogue of the corpus's
  completion-signal rule for scanners.

### Claim 10: The Enterprise alternative is a pointer to the webhook integration, not a delivery contract — it inherits the webhook page's documented absence of retry, ordering, and delivery guarantees
- **Evidence**: The "Enterprise webhooks" section says to configure
  `issue.created` / `issue.updated` and forward payloads to HEC, names the
  payload fields, and shows a HEC envelope with
  `sourcetype: promptfoo:redteam:issue`; it does not restate any delivery
  behavior. The linked webhooks page (already in the corpus) documents no
  retry/ordering/delivery guarantee.
- **Confidence**: settled for the pointer and the envelope (verbatim);
  the inherited delivery absence is verified against
  `docs-promptfoo-enterprise-webhooks.md` Claim 7
- **Quote**: "For continuous synchronization from Promptfoo Enterprise, configure webhooks for `issue.created` and `issue.updated`, then forward those webhook payloads to Splunk HEC. Webhook payloads include issue ID, plugin ID, status, severity, target ID, provider ID, and change information."
- **Our assessment**: Buy the pointer, and do not treat "continuous
  synchronization" as a guarantee — it is the same content-completeness framing
  the webhooks note already flagged (its Claim 8). This page adds two concrete
  facts: the Enterprise path uses a *different* `sourcetype`
  (`promptfoo:redteam:issue`, not `promptfoo:redteam`), and its event is a
  finding-issue payload rather than a per-test result. Everything about
  delivery reliability lives on the webhooks page and should be cited there, not
  re-derived here. The guide should route readers to the webhooks note for the
  reliability discussion and cite this page only for the HEC-forwarding shape.

### Claim 11: The page is vendor documentation with no measurement, no observed HEC delivery, and a machine-maintained footer — a recipe, not practitioner validation or a failure report
- **Evidence**: Full-page read: the only numbers are the cron schedule, example
  ports/URLs, and a Node 24 version; there is no metric, latency, volume,
  retention, cost, or captured response. Footer: "Last updated on **Nov 1,
  2026** by **renovate\[bot\]**". The page links no sub-pages that supply
  evidence.
- **Confidence**: settled as a description of the page (full-text read)
- **Quote**: "Last updated on **Nov 1, 2026** by **renovate\[bot\]**"
- **Our assessment**: This is the calibration claim that governs how every other
  claim may be cited. Treat the command names, env vars, HEC endpoint forms,
  `source`/`sourcetype`, and the SPL examples as `settled` (vendor-owned,
  string-checkable), and treat the *behavior* of the pipeline — delivery,
  retries, severity mapping, freshness, secret handling — as undocumented. The
  triage's caution is right: the transformer is referenced only as a gist and
  must be recorded as observed third-party code, not as vendor spec. Hence
  `confidence_overall: emerging`.

## Concrete Artifacts

All page artifacts are verbatim from the rendered page
(https://www.promptfoo.dev/docs/integrations/splunk, fetched 2026-11-01). The
fetched renderer collapsed some fenced code blocks onto one line; the blocks
below are reproduced with normal line breaks and no wording changes.

### Prerequisites — HEC endpoints (verbatim, "Prerequisites")

- Splunk Cloud Platform: `https://http-inputs-<stack>.splunkcloud.com/services/collector/event`
- Splunk Enterprise: `https://<splunk-host>:8088/services/collector/event`

> "Use the `/services/collector/event` endpoint for JSON events. Splunk's HEC event format supports top-level metadata such as `time`, `host`, `source`, `sourcetype`, and `index`."

### Export red team results (verbatim, "Export red team results")

```bash
promptfoo redteam run -c promptfooconfig.yaml --no-cache
promptfoo export eval latest -o redteam-results.json
```

> "If you already have a specific eval ID, export that instead of `latest`:"

```bash
promptfoo export eval <eval-id> -o redteam-results.json
```

> "In CI, set `PROMPTFOO_PASS_RATE_THRESHOLD=0` on the scan step if you want the pipeline to continue to the Splunk upload even when the scan finds failed tests."

### Transformer invocation (verbatim, "Send findings to Splunk HEC")

```bash
export SPLUNK_HEC_URL="https://http-inputs-<stack>.splunkcloud.com/services/collector/event"
export SPLUNK_HEC_TOKEN="<hec-token>"
export SPLUNK_INDEX="security"
# Run the transformer on the exported red team results and send findings to Splunk HEC.
node promptfoo-to-splunk.mjs redteam-results.json
```

> "For Splunk Enterprise with a self-signed certificate, fix certificate trust rather than disabling TLS verification in CI."

### GitHub Actions workflow (verbatim, ".github/workflows/redteam-splunk.yml")

```yaml
name: Promptfoo Red Team to Splunk
on:
  workflow_dispatch:
  schedule:
    - cron: '0 8 * * *'
jobs:
  redteam:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
      - name: Install promptfoo
        run: npm install -g promptfoo
      - name: Run red team scan
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PROMPTFOO_PASS_RATE_THRESHOLD: '0'
        run: promptfoo redteam run -c promptfooconfig.yaml --no-cache
      - name: Export latest eval
        run: promptfoo export eval latest -o redteam-results.json
      - name: Download Splunk transformer
        run: |
          curl -L \
            https://gist.githubusercontent.com/ianw-oai/418470829f7feff8e52a24ad6d028402/raw/promptfoo-to-splunk.mjs \
            -o promptfoo-to-splunk.mjs
      - name: Send findings to Splunk
        env:
          SPLUNK_HEC_URL: ${{ secrets.SPLUNK_HEC_URL }}
          SPLUNK_HEC_TOKEN: ${{ secrets.SPLUNK_HEC_TOKEN }}
          SPLUNK_INDEX: security
        run: node promptfoo-to-splunk.mjs redteam-results.json
```

> "Store `SPLUNK_HEC_URL`, `SPLUNK_HEC_TOKEN`, and LLM provider API keys as CI secrets."

### SPL queries (verbatim, "Search in Splunk")

```spl
index=security sourcetype="promptfoo:redteam"
| stats count as findings values(strategy_id) as strategies by plugin_id provider severity
| sort - findings
```

```spl
index=security sourcetype="promptfoo:redteam" severity IN ("high", "critical")
| table _time eval_id provider plugin_id strategy_id score attack_prompt failure_reason shareable_url
```

### Enterprise webhook → HEC envelope (verbatim, "Enterprise webhooks")

```json
{
  "source": "promptfoo",
  "sourcetype": "promptfoo:redteam:issue",
  "event": {
    "event_type": "promptfoo_redteam_issue",
    "issue": "<Promptfoo webhook issue payload>"
  }
}
```

### Security notes (verbatim)

- "Treat exported red team results as sensitive. Attack prompts and target outputs can contain harmful content or application data."
- "Restrict the Splunk index and HEC token to the teams that need access."
- "Use `PROMPTFOO_STRIP_RESPONSE_OUTPUT=true` or `PROMPTFOO_STRIP_TEST_VARS=true` if you need to reduce what leaves the CI environment."

### Observed third-party transformer (gist) — selected excerpts

**Attribution and caveat:** the following is verbatim from the gist the page
links, fetched 2026-11-01:
`https://gist.githubusercontent.com/ianw-oai/418470829f7feff8e52a24ad6d028402/raw/promptfoo-to-splunk.mjs`.
It is **third-party code, not vendor specification**, and the `/raw/` URL is a
moving target — a later revision may differ. Ellipses (`...`) mark omitted
sections; no wording inside an excerpt was changed.

```js
const defaultSeverity = process.env.PROMPTFOO_SPLUNK_DEFAULT_SEVERITY || 'medium';
...
const failedResults = results.filter(
  (result) => result.success === false && result.failureReason !== 2,
);
...
    severity: metadata.severity || defaultSeverity,
...
  const body = {
    time: Date.now() / 1000,
    host: os.hostname(),
    source: 'promptfoo',
    sourcetype: 'promptfoo:redteam',
    ...(index ? { index } : {}),
    event: finding,
  };

  const response = await fetch(hecUrl, {
    method: 'POST',
    headers: {
      Authorization: `Splunk ${hecToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Splunk HEC request failed: ${response.status} ${await response.text()}`);
  }
}

for (const result of failedResults) {
  await sendFinding(toFinding(result));
}
```

Observed, not vendor-documented: the finding body carries
`event_type: 'promptfoo_redteam_finding'`, `eval_id`, `prompt_idx`, `test_idx`,
`provider`, `plugin_id`, `strategy_id`, `severity`, `score`, `success`,
`failure_reason`, `attack_prompt`, `target_output`, and `shareable_url`; the
filter excludes results whose `failureReason` equals `2` (the constant is not
explained in the page or the gist); and one failed POST throws out of the send
loop.

## Cross-References

**Candidates from `miner-related-notes.md`** (read before writing this section;
every listed path is cited or dismissed by name):

- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **cited**
  (Corroborates + Extends — see below).
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: LiteLLM's
  server-side Evaluations API; no findings egress or SIEM content.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  accounting; no event-delivery or SIEM surface.
- `source-notes/blog-pagerduty-sre-agent-triage.md` — **dismissed**: AI incident
  triage by an SRE Agent; no claim about red-team findings or SIEM ingestion.
- `source-notes/docs-promptfoo-pi-scorer.md` — **dismissed**: model-graded
  scorer configuration; no egress surface.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs MCP transport,
  unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  taxonomy; the recurring cron job is toil-shaped but the note makes no claim
  about security-finding egress.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch coordination, unrelated.
- `source-notes/docs-google-sre-team-lifecycles.md` — **dismissed**: SRE org
  lifecycle, unrelated.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — **dismissed**:
  assertion-type inventory; no event-delivery or SIEM content.

Additional cross-references found by searching `source-notes/` (not in the
candidate list): `docs-promptfoo-enterprise-webhooks.md`,
`docs-promptfoo-enterprise-audit-logging.md`,
`docs-promptfoo-langfuse-integration.md`, `docs-langfuse-alerts.md`, and
`docs-promptfoo-code-scan-github-action.md` — all cited below.

**Primary cross-references (verified per MINER §4b — every cited claim was
re-read in its source note before writing):**

- **Corroborates**:
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` **Claim 2**
    ("Vulnerability disposition is a closed three-value status set ... plus
    manual severity re-rating and free-text comments ... with no documented
    transition rules, auto-closure, SLA, or actor attribution") and **Claim 11**
    ("no severity-level vocabulary", with "severity level" used without
    enumerating values). This page's "Tune severity mapping to your
    internal policy" is the concrete consequence: the OSS export has pass/fail +
    score, not the Enterprise finding's severity, so the SPL alert's
    `severity IN ("high","critical")` keys on a field the OSS path does not
    provide (Claim 7 here). Both notes agree that severity is an
    operator/Enterprise concern, not an OSS export fact. (Verified: Claim 2 and
    Claim 11 headings and quotes re-read.)
  - `source-notes/docs-promptfoo-enterprise-webhooks.md` **Claim 7** ("The page
    documents no delivery contract whatsoever — no retry, no backoff, no
    ordering guarantee, no timeout, no dead-letter queue, and no delivery log")
    and **Claim 8** ("The SIEM recipe asserts the stream \"makes it easy to keep
    your SIEM system synchronized\" while the page documents no delivery
    guarantee — a payload-completeness claim is presented as if it were a
    synchronization guarantee"). This page's HEC path has the same absence and
    the same "so SIEM data stays current" framing (Claim 8 here); the two notes
    independently document the same vendor pattern on the webhook and HEC
    egresses. (Verified: Claim 7 and Claim 8 headings and quotes re-read.)

- **Extends**:
  - `source-notes/docs-promptfoo-enterprise-webhooks.md` **Claim 1** (the
    Enterprise webhook surface is five red-team `issue.*` events, not run/eval
    telemetry) — this page supplies the Enterprise SIEM-forwarding *envelope*
    for those events (`sourcetype: promptfoo:redteam:issue`, event_type
    `promptfoo_redteam_issue`, Claim 10) that the webhooks note did not include.
    It does **not** re-derive delivery reliability; it points at that note.
    (Verified: Claim 1 heading and event list re-read.)
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` **Claim 10**
    ("The documented programmatic surface for findings is read-only — search via
    `GET /api/v1/results` and shareable URLs via `promptfoo share` — with no
    documented write API ...") — this page shows the *other* way findings leave
    the platform: an outbound push, not a read API. Read together, the corpus
    now holds the two egress postures for the same finding object: pull
    (`GET /api/v1/results`, read-only) and push (HEC, failure-only). The push
    path is the one that can feed a SIEM, and it inherits the reliability gap
    above. (Verified: Claim 10 heading and quotes re-read.)
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 2** ("The
    coverage boundary is drawn explicitly ... administrative actions are logged,
    while \"Evaluation runs, prompt testing, and other data plane operations are
    tracked separately\" — with no named destination") — this page is a concrete,
    named destination for one slice of the data plane: failed red-team findings
    go to a SIEM under `sourcetype=promptfoo:redteam`. It does not make the
    audit log cover those operations, but it fills in part of the "tracked
    separately" gap the audit note could only describe as unnamed. The plane
    distinction remains: audit = control plane, this stream = finding plane.
    (Verified: Claim 2 heading and quotes re-read.)
  - `source-notes/docs-promptfoo-langfuse-integration.md` — the **contrast** that
    makes this page's egress posture clear. Langfuse is wired *into* the eval as
    an inbound prompt/trace source (its Claims 1–7: SDK dependency, server floor,
    trace retrieval), whereas Splunk is an *outbound* sink for findings (Claims
    1, 5, 6 here). Repo triage called this the "other observability-vendor
    integration"; the useful axis is direction of data flow (in vs out) and
    failure ownership (trace fetch failure vs HEC delivery failure), not the
    vendor. (Verified: the note's scope and Claims 1–7 were read.)
  - `source-notes/docs-langfuse-alerts.md` **Claim 8** ("After 5 consecutive
    delivery failures, Langfuse automatically disables the automation's trigger")
    and **Claim 9** (the webhook delivers a *versioned*, HMAC-signed JSON
    payload) — the counterexample this page lacks. Langfuse documents a delivery
    circuit breaker and a versioned payload; this page documents neither, so a
    reader can see exactly what "no documented delivery contract" costs: no
    retry/disable behavior and no schema version to detect a transformer change
    (Claim 8 here). (Verified: Claim 8 and Claim 9 headings and quotes re-read.)
  - `source-notes/docs-promptfoo-code-scan-github-action.md` **Claim 5** ("SARIF
    output is only published when a scan actually completes") and **Claim 8**
    ("Tags such as `v0` are convenient but mutable; a commit SHA is the only
    immutable reference") — the corpus already carries the two controls this
    page omits: a completion signal that distinguishes skipped from clean, and
    SHA pinning for CI dependencies. The Splunk recipe has neither (no
    upload-completion signal, unpinned gist/npm install). The guide's existing
    completion-signal and SHA-pinning rules therefore apply here by extension,
    not as new discoveries. (Verified: Claim 5 and Claim 8 headings and quotes
    re-read.)

- **Contradicts**: **None filed, and this was checked rather than assumed.**
  - The OSS-vs-Enterprise severity asymmetry (Claim 7) is a conditioning
    variable, not a contradiction: the OSS export has pass/fail + score, and the
    Enterprise finding carries status/severity. Both can be true at once, and
    the page states both. No source note claims otherwise.
  - The `PROMPTFOO_PASS_RATE_THRESHOLD=0` recommendation (Claim 3) does not
    contradict the corpus's "gate on the scan's completion signal" rule
    (`guide/06-security-and-trust.md:821`): it is an explicitly scoped tradeoff
    for a data-pump job, and this note records the missing consequence rather
    than opposing the recipe. It is a *different job purpose*, not a different
    verdict on gating.
  - No contradiction issue was filed. Checked `CONTRADICTIONS.md` and the open
    `contradiction`-labeled issues: none cover promptfoo/Splunk/SIEM egress.

- **Novel**: The following are net-new to the corpus:
  1. **The HEC finding pipeline as a documented end-to-end recipe** (Claims 1,
     2, 5, 9) — scan → `export eval latest` → gist transform → HEC POST, with
     `sourcetype=promptfoo:redteam` and a daily cron.
  2. **`PROMPTFOO_PASS_RATE_THRESHOLD=0` as an intentional gate-disable for
     SIEM upload** (Claim 3) — the corpus's first concrete instance of a
     security pipeline whose green check intentionally stops meaning "no
     findings."
  3. **The unpinned personal-gist transformer as a supply-chain hazard** (Claim
     4) — runtime-fetched `/raw/` gist code executing with the HEC write token
     and access to the exported findings.
  4. **The OSS severity-mapping gap** (Claim 7) — the page's `severity IN
     ("high","critical")` alert against an export that carries no severity, plus
     the observed gist default of `medium`.
  5. **The HEC egress-access story** (Claim 6) — attack prompts/target
     outputs/application data into a SIEM, index/token scoping as the only
     access control, and two opt-in strip flags with no documented redaction.
  6. **The Enterprise SIEM envelope** (Claim 10) — `sourcetype:
     promptfoo:redteam:issue` and `event_type: promptfoo_redteam_issue`, which
     the existing webhooks note did not record.

## Guide Impact

- **Chapter 06 §"Red-teaming as a CI gate" (`guide/06-security-and-trust.md:120`)
  — add the data-pump vs gate distinction.** The section currently says to run
  red-team tests before each deployment and track results as a security
  scorecard. Add: when the job's purpose is to ship findings to a SIEM, the
  documented recipe sets `PROMPTFOO_PASS_RATE_THRESHOLD=0` so the upload still
  runs on failed tests (Claim 3). That intentionally removes the CI gate: a green
  run means "the upload ran", not "the scan was clean." Proposed rule text: *a
  red-team pipeline that feeds a SIEM is a data pump, not a gate; if you also
  need the build to block, run a separate gating job with a non-zero pass-rate
  threshold and let the SIEM-side alert own detection.*
- **Chapter 06 §"A guardrail is an egress boundary — configure what crosses it"
  (`guide/06-security-and-trust.md:547`) — extend the egress rule to
  findings-to-SIEM.** The section currently reviews guardrail payloads and header
  allowlists. Add the red-team finding egress: attack prompts, target outputs,
  and a share URL can cross into a SIEM index (Claim 6), the page's only
  documented controls are index/token scoping and `PROMPTFOO_STRIP_*`, and the
  attack prompt itself has no documented redaction. Proposed rule text: *treat a
  findings SIEM as a sensitive data store: scope the HEC write token to one
  index, decide explicitly whether offensive prompts and target outputs may
  persist there, and verify what the strip flags actually remove.*
- **Chapter 06 §"Pin every CI dependency to verified SHAs — including security
  scanners" (`guide/06-security-and-trust.md:726`) — add the runtime-fetched
  transformer case.** The existing rule covers Action and scanner pinning. Add
  that this vendor recipe fetches `promptfoo-to-splunk.mjs` from a personal
  gist's `/raw/` URL at job time and installs promptfoo globally with no version
  (Claim 4), so the transformer is a secret-bearing, mutable dependency. Proposed
  addition: *vendor or pin the transformer (commit SHA + checksum) and pin the
  scanner version; a script fetched from a moving URL is not a pinned
  dependency.* Cite `docs-promptfoo-code-scan-github-action.md` Claim 8 for the
  SHA-pinning convention.
- **Chapter 05 (LLM Ops Reliability — eval harness / CI gating) — add
  "detection signal vs pipeline exit code" and "push is best-effort".** The
  chapter already distinguishes a scan that completed from one that did not
  (the completion-signal material). Extend it with the SIEM path: the documented
  HEC push has no retry/backoff/dead-letter/idempotency (Claim 8), the cron
  bounds freshness to ~24h (Claim 9), and the transformer aborts remaining
  findings on the first failed POST. Recommended additions: bind the export to
  the scan's eval ID rather than `latest` (Claim 2); add retry/backoff plus a
  dead-letter path and an idempotency key; alert when the expected daily event
  volume for `sourcetype=promptfoo:redteam` is zero, so a broken cron is not
  read as a clean day.
- **Chapter 02 (Observability) — add the eval-to-SIEM boundary as an
  observability hand-off.** State that promoting findings into a SIEM changes
  the consumer: the SIEM's readers are security responders, the event schema is
  the integration contract, and the OSS export's fields (pass/fail + score) are
  not the same as the Enterprise finding's (status/severity) (Claims 5, 7, 10).
  Cite the `sourcetype` as the stable key and the gist as an unpinned,
  non-vendor mapping. Do not present the recipe as a complete telemetry
  pipeline: it carries failures only (Claim 1) and has no delivery guarantee
  (Claim 8).
- **Do not** cite this page as evidence of reliable SIEM delivery, retry,
  ordering, deduplication, or a complete OSS severity mapping. It documents a
  recipe (Claim 11) whose delivery and severity semantics are left to the
  operator.

## Extraction Notes

- Source read in full via direct fetch of the rendered page
  (https://www.promptfoo.dev/docs/integrations/splunk, HTTP 200, no paywall,
  fetched 2026-11-01). Every `Quote` above is character-for-character from the
  rendered text; code/JSON/SPL artifacts are reproduced verbatim with line
  breaks normalized where the renderer collapsed fenced blocks (noted in the
  relevant sections).
- **Third-party gist read separately.** Per the Prospector's caution, I fetched
  the linked transformer to confirm what the page's SPL queries actually depend
  on, and recorded it in Concrete Artifacts as *observed third-party code*, not
  vendor specification. The gist is unpinned, so the excerpts are dated
  2026-11-01 and may not match a later revision. No claim here treats the gist's
  behavior as documented product behavior.
- **No metrics were manufactured.** The page contains no measurement of volume,
  latency, retention, cost, or delivery. `confidence_overall: emerging` reflects
  vendor documentation plus one mutable third-party artifact; the command/env/
  endpoint facts are `settled` as a specification, while the operational
  behavior behind them is unverified.
- **Linked pages followed**: none beyond the gist and the already-extracted
  Enterprise webhooks page. The page is self-contained and defers only to the
  webhooks page; the reliability discussion there is cited rather than
  re-derived.
- **Contradiction filing decision (MINER §4a)**: none filed. The
  OSS/Enterprise severity asymmetry is a conditioning variable, and the
  threshold-0 gate override is a scoped tradeoff, not an opposing verdict.
  Checked `CONTRADICTIONS.md` and open `contradiction`-labeled issues — no
  existing entry covers promptfoo Splunk/HEC/SIEM egress.
- **Candidate handling** (`miner-related-notes.md`, 10 lexical candidates):
  cited **1** — `docs-promptfoo-enterprise-findings-reports.md` (Corroborates,
  Extends). The other nine dismissed, one line each in Cross-References. Five
  additional cross-references were found by searching `source-notes/`
  (`enterprise-webhooks`, `enterprise-audit-logging`, `langfuse-integration`,
  `langfuse-alerts`, `code-scan-github-action`) and are cited above.
- **Cross-references verified before writing** (MINER §4b): every `Claim N`
  cited from another note was located by re-reading that note's `### Claim:`
  headings and confirming content — `enterprise-findings-reports` Claims 2, 10,
  11; `enterprise-webhooks` Claims 1, 7, 8; `enterprise-audit-logging` Claim 2;
  `docs-promptfoo-langfuse-integration` (scope + Claims 1–7); `docs-langfuse-alerts`
  Claims 8, 9; `docs-promptfoo-code-scan-github-action` Claims 5, 8. No quote
  was reconstructed from memory.
- `registry/sources.json` and `registry/claims-index.json` were **not** touched;
  both are derived indexes rebuilt by `registry-rebuild.yml` after merge.
  `miner-related-notes.md` was read but is not committed.
