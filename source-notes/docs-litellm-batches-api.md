---
source_url: https://docs.litellm.ai/docs/batches
source_type: docs
title: "/batches — LiteLLM AI Gateway Documentation (Batches / Files)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-22)
date_extracted: 2026-09-22
last_checked: 2026-09-22
status: current
confidence_overall: settled
issue: "#1415"
---

# /batches (LiteLLM Docs)

> LiteLLM's `/docs/batches` page documents a batch workload-governance surface
> with a fundamental shape mismatch: the gateway charges an entire multi-hour
> batch **at submission time, to a single per-minute TPM/RPM window**, on limits
> computed from a pre-read of the JSONL input file — and then publishes the
> enforcement gaps (counters never reconciled with the provider; unreadable
> files submitted **unmetered**; zero-cost ≠ zero-work in Enterprise-only cost
> tracking) that a platform team must plan around if it governs batch LLM work
> through this gateway.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living
  Docusaurus page under "Supported Endpoints > /batches", the single canonical
  page for the `/v1/files` + `/v1/batches` surface; sibling sub-pages
  `[BETA] LiteLLM Managed Files with Batches`, `Unmanaged Vertex AI Batches`,
  per-provider batch pages, and "Batch API Guardrails" are linked but out of
  scope per the Prospector's bounding).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* LiteLLM exposes (which endpoint charges which
  limit, the `batch_enqueued_token_limit` contract, the validation gates, the
  cost-tracking license gate, the ID-encoding routing scheme). Per the
  Prospector's bounding rule, this note records documented **product behavior
  and schema/contract claims as `settled`** — the page carries no benchmarks or
  effectiveness claims, and none are inferred here.
- **Scope**: Covers supported providers; batch rate limiting (submission-time
  charging, per-record counts, enqueued-token allowances, skip/dead knobs, the
  operational-behavior enforcement-gap table); input-file validation
  (`max_batch_file_size_mb` 413 gate, always-on content validation, provider
  caps table); Enterprise-gated batch cost tracking; and multi-account
  model-based routing via base64-encoded IDs. Does **not** cover the batch
  quick-start CRUD as a learning object (endpoint examples are generic
  OpenAI-compatible calls), the managed-files beta, per-provider batch
  sub-pages, or guardrail *configuration* (the page only states that proxy
  guardrails run against batch input at upload — placed here as a
  security-relevant claim, with the dedicated "Batch API Guardrails" page not
  absorbed).

## Extracted Claims

### Claim 1: Batch TPM/RPM limits are charged when the client calls `POST /v1/batches`, not when the input file is uploaded — LiteLLM downloads the referenced JSONL, evaluates the complete file against every applicable limit, and returns 429 before forwarding anything to the provider
- **Evidence**: The "How Rate Limiting for Batches API Works" section's
  opening sentence plus the four-step numbered list (upload consumes nothing →
  batch creation downloads and evaluates the file → atomic check of the whole
  file → 429 and no provider submission on overage).
- **Confidence**: settled (documented API-contract behavior with an explicit
  step list)
- **Quote**: "Batch rate limits are enforced when the client calls `POST /v1/batches`, not when the input file is uploaded." / "LiteLLM atomically checks the complete file against every applicable limit." / "If any limit would be exceeded, LiteLLM returns `429` and does not submit the batch to the provider. Otherwise, it records the usage and creates the provider batch."
- **Our assessment**: The core timing fact for governance: a gateway that
  meters at *upload* time enforces something completely different from this
  documented behavior. The entire batch — which may represent hours of provider
  work — stands or falls on the submission-time pre-read, and the upload path
  itself is metering-free. Note the "records the usage" wording: the
  submission-time charge is LiteLLM's own counter, not a provider confirmation
  (see Claim 6 — those counters are never reconciled).

### Claim 2: What LiteLLM counts per JSONL record is a closed contract — RPM = one request per record; TPM/ITPM = input tokens from `body.messages` / `body.prompt` / `body.input`; OTPM = an output-token reservation per record honoring `max_tokens` / `max_completion_tokens` / `max_output_tokens` and `n` / `best_of`; embedding records reserve no output tokens; untokenizable records fall back to a serialized-size estimate
- **Evidence**: The "What LiteLLM counts" table's per-limit rows: RPM, TPM,
  Project ITPM, Project OTPM, plus the following note on tokenization failure.
- **Confidence**: settled (documented counting contract; deterministic
  per-record rules)
- **Quote**: "RPM: One request for each JSONL record." / "TPM: Input tokens found in each record's `body.messages`, `body.prompt`, or `body.input`." / "An output-token reservation for each record, grouped by `body.model`. LiteLLM uses `max_tokens`, `max_completion_tokens`, or `max_output_tokens` when present and accounts for `n` or `best_of`. Embedding records reserve no output tokens. If no output cap is present, LiteLLM uses the v3 limiter's built-in estimate, bounded by the smallest applicable OTPM limit." / "If LiteLLM cannot tokenize an individual record, it uses a conservative estimate based on the serialized record size. A malformed JSONL line still counts as one request."
- **Our assessment**: The "Project OTPM" row is the sharpest operational detail:
  an *output reservation* (from `max_tokens`-family caps) is charged for each
  record, so a JSONL whose per-record `max_tokens` is generous charges far more
  OTPM at submission than the provider will actually consume — predictable
  over-reservation, not a ledger. And because `n`/`best_of` are honored, the
  reservation still under-counts if a record omits the cap fields and the v3
  estimate applies. These are estimates by design (see Claim 6).

### Claim 3: Per-minute TPM/RPM windows fit batch work poorly — the whole input file is charged to a single minute at submission — and the documented remedy is `batch_enqueued_token_limit`, an outstanding-work allowance in key/team metadata that reserves estimated tokens, refunds on observed terminal state, bypasses the per-minute windows entirely, and expires reservations after 8 days if a terminal state is never observed
- **Evidence**: The "Enqueued-token limits" section: the mismatch statement,
  the key-metadata curl example, the admin-only 403 rule, the
  reserve/reject/refund/not-charged step list, the both-must-fit rule, and the
  two-details-to-plan-around note.
- **Confidence**: settled (documented contract incl. the 403 rule and the 8-day
  expiry; the "fits batches poorly" framing is the page's own)
- **Quote**: "Per-minute windows fit batches poorly: a batch runs for hours, but its whole input file is charged to a single minute at submission." / "Only a proxy admin can set or change `batch_enqueued_token_limit`. Key and team requests from other roles that try to write it are rejected with a `403`." / "When the client creates a batch, LiteLLM reserves the file's estimated tokens (the input tokens plus each record's output cap) against the allowance." / "If the batch does not fit, LiteLLM returns `429` naming the enqueued token limit and does not submit the batch to the provider." / "When LiteLLM serves a response showing the batch in a terminal state (completed, failed, expired, or cancelled), it refunds the reservation." / "Batch submissions are not charged to the per-minute TPM and RPM windows, so a batch whose record count exceeds the key's RPM is accepted when it fits the allowance." / "Reservations for batches whose terminal state LiteLLM never observes (for example, a batch only ever polled directly against the provider) expire after 8 days."
- **Our assessment**: This is the batch-shaped governance pattern (an
  outstanding-work allowance) versus the request-shaped RPM/TPM window, and the
  page's own framing endorses measuring batch governance in reserved tokens, not
  per-minute throughput. Three operational consequences worth encoding: (a) the
  allowance is *silently* high-authority — a batch fitting both the key's and
  team's allowances skips the per-minute counters entirely (real-time traffic
  still consumes them as before); (b) only the proxy admin can write it — a
  403-classified configuration gate for non-admin key/team writes (ties to
  Ch06); (c) the refund and the 8-day expiry both depend on LiteLLM *observing*
  a terminal state through its own retrieve/cancel, so a client that polls the
  provider directly leaves the reservation out there to rot (the missed-refund
  leak is a concrete failure mode).

### Claim 4: `LITELLM_TPM_TOKEN_RESERVATION_ENABLED` does **not** control batch rate limiting — it only governs pre-request reservation for real-time requests; `POST /v1/batches` always uses the batch input-file limiter unless a batch-specific skip setting is enabled
- **Evidence**: The `important` callout box immediately after the "What LiteLLM
  counts" table.
- **Confidence**: settled (explicit document-level callout)
- **Quote**: "`LITELLM_TPM_TOKEN_RESERVATION_ENABLED` does not control batch rate limiting. That variable controls pre-request reservation for real-time requests such as chat completions. `POST /v1/batches` always uses the batch input-file limiter described here unless one of the batch-specific skip settings below is enabled."
- **Our assessment**: A misconfiguration trap the docs pre-empt explicitly: an
  operator who believes the TPM-reservation toggle governs batch submissions is
  wrong, and batch traffic is governed by a separate limiter on a separate code
  path. The "batch input-file limiter" is also where the pre-read cost shows up
  (see Claim 7's "skipping the input-file pre-read").

### Claim 5: Two skip settings take precedence and disable enqueued-token accounting entirely — `disable_batch_input_file_rate_limiting` and `skip_batch_input_file_rate_limiting_for_providers` (provider taken from the configured route, not client-supplied `custom_llm_provider`) — while `skip_batch_input_file_rate_limiting_for_models` is a retained no-op (startup warning) and a request-metadata `skip_batch_input_file_rate_limiting` flag is ignored
- **Evidence**: The "Skipping the input-file pre-read" section's config block,
  the provider-source sentence, the "not supported" bullet list, and the
  model-allowlist exception sentence.
- **Confidence**: settled (documented config semantics; the no-op/ignored status
  is stated explicitly)
- **Quote**: "`disable_batch_input_file_rate_limiting` and `skip_batch_input_file_rate_limiting_for_providers` take precedence. When they apply, LiteLLM performs no enqueued-token accounting." / "The provider-specific option uses the provider configured on the selected route. It does not use a `custom_llm_provider` value supplied by the client." / "`skip_batch_input_file_rate_limiting_for_models` is retained for compatibility but has no effect. LiteLLM logs a warning at startup when it is configured." / "A `skip_batch_input_file_rate_limiting` flag in request metadata is ignored." / "For API keys with a model allowlist, LiteLLM must still read the file to validate each `body.model` value. In this case, the settings above skip the TPM and RPM counter update, but not the file download or model validation."
- **Our assessment**: Two recurring LiteLLM-doc patterns in one section. First,
  "config that looks like it works but doesn't": a `_for_models` knob retained
  for compatibility with zero effect (logged at startup) and a request-metadata
  flag that is silently ignored — an operator who sets them believes batch
  submissions skip the pre-read and gets the opposite. Second, a security
  override: the skip settings never bypass the model-allowlist file read, so
  per-record `body.model` validation still forces the download even when
  rate-limit charging is disabled.

### Claim 6: The gateway's batch accounting silently under-counts in documented cases — batch TPM/RPM counters are never reconciled against the provider's final usage, and a batch whose input file cannot be downloaded or evaluated is submitted **unmetered** (with a logged error the docs say to monitor if strict enforcement is required)
- **Evidence**: The "Operational behavior" table's four rows (Behavior /
  Operational impact), quoted here per row.
- **Confidence**: settled (each row is a documented operational consequence; the
  "counter is an estimate, not a ledger" synthesis is the Miner's framing of the
  table's own wording)
- **Quote**: "Batch TPM and RPM counters are not reconciled against the provider's final usage. Final cost tracking is separate." / "LiteLLM logs the error and submits the batch without charging it to TPM or RPM. Monitor these errors if your deployment requires strict rate-limit enforcement." / "LiteLLM submits the batch without downloading it for rate-limit accounting." / "LiteLLM reads the file and validates every `body.model` before submission."
- **Our assessment**: The strongest single claim on the page and the core
  answer to the Prospector's key question ("what is actually metered, at which
  point, and what does it silently not meter?"). Charging is estimate-based,
  one-shot, and unreconciled: the only counter the gateway maintains is its own
  submission-time computation, and it degrades to *no charging at all* exactly
  when the input file is problematic — a silent quota-enforcement hole. The
  fourth row is the flip side: an allowlist key forces the file read that the
  skip knobs would otherwise avoid, so "skipped" never equals "unread" for
  allowlist keys. This is the "counters are not an audit trail" evidence Ch02
  needs (see Guide Impact).

### Claim 7: Batch input files pass a pre-forward validation gate — `max_batch_file_size_mb` under `general_settings` rejects oversized `purpose="batch"` uploads with HTTP 413 before provider forwarding (separate from `max_request_size_mb`), and always-on content validation requires a case-insensitive `.jsonl`, ≥1 non-blank line, every non-blank line a valid JSON object carrying `custom_id` / `method` / `url` / `body`, rejected with OpenAI-format HTTP 400 errors and 1-based line numbers
- **Evidence**: The "Batch Input File Validation" section's two sub-sections:
  the `max_batch_file_size_mb` config + 413 error body, the content-validation
  rules + reject format, and the "runs on every routing path" note.
- **Confidence**: settled (explicit validation contract with error bodies)
- **Quote**: "When a client uploads a file to `POST /v1/files` with `purpose="batch"`, LiteLLM checks the file locally and rejects invalid files before anything is forwarded to the provider." / "The filename must end in `.jsonl`, matched case-insensitively. The file must contain at least one non-blank line. Every non-blank line must be valid JSON. Every line must be a JSON object. Every object must contain the `custom_id`, `method`, `url`, and `body` keys" / "The `message` includes the 1-based line number where relevant. Line numbers count every line in the file, including blank lines" / "`max_batch_file_size_mb` applies only to batch input file uploads. It is separate from `max_request_size_mb`, which applies to every proxy route"
- **Our assessment**: A real pre-forward admission gate, which is notable given
  Claim 6's unmetered-submission hole — validation is strict while *charging* is
  soft. Two details operators will trip on: the 413 is *not* a rate-limit signal
  (it is the size gate, "not forwarded to the provider"), and line numbers count
  blank lines (a wrapper that strips blank lines before upload gets *different*
  error line numbers than the file it uploaded). Pinpointing a malformed record
  therefore requires the client and the gateway to agree on what a "line" is.

### Claim 8: Provider batch caps differ by an order of magnitude, and the page instructs operators to set `max_batch_file_size_mb` at or below the smallest limit of the providers they route to — OpenAI 200 MB / 50k requests, Azure OpenAI 200 MB / 100k per file (1 GB with BYO blob storage), Vertex 1 GB / 200k per job (Cloud Storage input), Bedrock 1 GB per file with a ~5 GB total-job cap
- **Evidence**: The "Provider batch limits" table plus its closing guidance
  sentence.
- **Confidence**: settled (numeric vendor limits as published on the page;
  independent verification against provider docs is out of scope for this
  extraction)
- **Quote**: "Each provider enforces its own limits on batch input files. Use them to pick a value for `max_batch_file_size_mb`" / "Set `max_batch_file_size_mb` at or below the smallest limit of the providers you route batch traffic to" / "Azure OpenAI raises its file cap to 1 GB with bring-your-own Blob Storage. The Vertex AI cap applies to Cloud Storage input. Amazon Bedrock also caps total job size, at 5 GB for most models."
- **Our assessment**: This converts the validation knob into a
  multi-tenant-routing decision: the cap that protects the gateway must be the
  *intersection* of the caps of every provider a key can route to, since the
  enqueued-token path routes per model/account (Claim 10). A cap picked against
  one provider silently fails on another — and the docs' own guidance makes
  smallest-limit selection the responsibility of whoever sets the config.

### Claim 9: Automated batch cost tracking is Enterprise-only and recorded separately from submission — LiteLLM monitors the provider job, aggregates successful output records, excludes failed records (an all-failed batch records zero usage and zero cost), records the aggregate as an `aretrieve_batch` spend entry attributed to the creating user/key/team/tags, and never adjusts the TPM/RPM counters reserved at submission
- **Evidence**: The "How Cost Tracking for Batches API Works" section — the
  Enterprise badge, the five numbered steps, the failed-record exclusion
  sentence, and the counters-unchanged sentence.
- **Confidence**: settled (documented feature gating and accounting contract)
- **Quote**: "Automated batch cost tracking requires a LiteLLM Enterprise license." / "Failed output records are excluded from the aggregate. If the batch has no output file because every record failed, LiteLLM records zero usage and zero cost." / "The initial submission and the completed aggregate are recorded separately. The completed aggregate is emitted through standard spend tracking as an `aretrieve_batch` record, so it is available to the Admin UI and configured logging callbacks." / "Batch cost tracking does not change the TPM or RPM counters reserved at submission."
- **Our assessment**: Two governance implications. First, *spend visibility is
  licensed*: in an OSS deployment batch spend is invisible through this
  mechanism until the Enterprise license is added — a concrete monitoring gap
  for cost-conscious teams (Ch02). Second, *"zero cost" does not imply "no
  work"*: an all-failed batch is recorded with zero usage and zero cost, exactly
  the inverse of the silent-fallback `cost=0` signature from the model-cost-map
  incident — batch records must be corner-cased in any spend report. And the
  separation of the aggregate ('completed aggregate' at terminal state) from the
  submission-time counters means neither number can substitute for the other.

### Claim 10: Batch and file operations route across multiple provider accounts through model info embedded in base64-encoded IDs — `file-…` / `batch_…` prefixes preserved, `base64("litellm:<id>;model,<name>")` — with documented priority: encoded ID (highest) > model parameter via header/query/body > `custom_llm_provider` environment fallback
- **Evidence**: The "Multi-Account / Model-Based Routing" section — the
  priority-order list, the encoding walkthrough, the encoded-ID example
  responses, and the per-endpoint routing table.
- **Confidence**: settled for the mechanism and the three-tier priority order;
  the page does **not** state a precedence among header vs query vs body, and no
  precedence is asserted here
- **Quote**: "**1. Encoded Batch/File ID** (highest) - Model info embedded in the ID / **2. Model Parameter** - Via header (`x-litellm-model`), query param, or request body / **3. Custom Provider** (fallback) - Uses environment variables" / "LiteLLM encodes model information into file and batch IDs using base64:" / "File and batch IDs \"remember\" which account created them" / "Automatic routing for retrieve, cancel, and file content operations"
- **Our assessment**: The ops angle is that routing state is carried *inside an
  opaque client-held identifier*: once a file is uploaded with an `x-litellm-model`
  header, the returned ID silently pins the account for every subsequent
  retrieve/cancel/content call, so copy-paste or truncation of IDs is a latent
  cross-account hazard, and observability tooling that logs IDs carries routing
  intent in what looks like a random string. The page's silence on header-vs-
  query-vs-body precedence is respected here — the Miner asserts only the
  documented three-tier order.

### Claim 11: Guardrails configured on the proxy run against the records **inside** the batch input file at upload time, not at execution time — a security-relevant placement that interacts with the always-on file validation
- **Evidence**: The page's feature table row ("Guardrails configured on your
  proxy are applied to the records inside a batch input file when it is
  uploaded") and its link to "Batch API Guardrails"; the validation section's
  "runs on every `/v1/files` routing path" note.
- **Confidence**: settled (documented feature placement; the security
  interpretation is the Miner's framing)
- **Quote**: "Guardrails configured on your proxy are applied to the records inside a batch input file when it is uploaded. See [Batch API Guardrails](/docs/proxy/guardrails/batch_guardrails)"
- **Our assessment**: Guardrail enforcement at *upload* means the security
  checkpoint happens before any provider work — but only against the file's raw
  request records, and on a path that also performs size/content validation
  (Claim 7). The dedicated guardrails page is linked but not absorbed per the
  Prospector's bounding; this note records the placement so Ch06 can model
  "upload-time validation + guardrails" as the batch admission surface.

## Concrete Artifacts

All artifacts verbatim from the fetched page (`https://docs.litellm.ai/docs/batches`).

### Quick-start batch creation shape (from "Quick Start", LiteLLM PROXY tab)

```bash
curl http://localhost:4000/v1/files \
    -H "Authorization: Bearer $LITELLM_API_KEY" \
    -F purpose="batch" \
    -F file="@mydata.jsonl"

curl http://localhost:4000/v1/batches \
        -H "Authorization: Bearer $LITELLM_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "input_file_id": "file-abc123",
            "endpoint": "/v1/chat/completions",
            "completion_window": "24h"
    }'
```

### `max_batch_file_size_mb` config (from "Limit the batch input file size")

```yaml
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  max_batch_file_size_mb: 10
```

### 413 rejection body (from the same section, verbatim)

```json
{
  "error": {
    "message": "Batch input file is 12.0 MB, which exceeds the configured max_batch_file_size_mb of 10 MB. The file was not forwarded to the provider.",
    "type": "invalid_request_error",
    "param": "file",
    "code": "413"
  }
}
```

### Enqueued-token allowance (from "Enqueued-token limits")

```bash
curl -X POST 'http://localhost:4000/key/generate' \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"metadata": {"batch_enqueued_token_limit": 100000}}'
```

`batch_enqueued_token_limit` also works in team metadata.

### Skip settings (from "Skipping the input-file pre-read")

```yaml
general_settings:
  # Apply to all batch submissions
  disable_batch_input_file_rate_limiting: true
  # Or apply only to batches routed to selected providers
  skip_batch_input_file_rate_limiting_for_providers:
    - bedrock
```

### Operational-behavior table (from "Operational behavior", verbatim)

```
Behavior                                                          Operational impact
Accounting is based on the submitted file                         Batch TPM and RPM counters are not reconciled against the provider's final usage. Final cost tracking is separate.
The complete file cannot be downloaded or evaluated               LiteLLM logs the error and submits the batch without charging it to TPM or RPM. Monitor these errors if your deployment requires strict rate-limit enforcement.
No applicable rate limit is configured                            LiteLLM submits the batch without downloading it for rate-limit accounting.
The API key has a model allowlist                                 LiteLLM reads the file and validates every `body.model` before submission.
```

### Cost-tracking steps (from "How Cost Tracking for Batches API Works", condensed verbatim)

```
1. Downloads the provider's output file.
2. Reads each successful output record.
3. Aggregates prompt, completion, and total token usage across those records.
4. Calculates each record's cost using the deployment's configured batch pricing.
5. Records the combined usage and cost against the user, key, team, and request tags that created the batch.
```

### Provider batch limits table (from "Provider batch limits", verbatim)

| Provider | Max input file size | Max requests |
|---|---|---|
| OpenAI | 200 MB | 50,000 per batch |
| Azure OpenAI | 200 MB | 100,000 per file |
| Vertex AI | 1 GB | 200,000 per job |
| Amazon Bedrock | 1 GB per file | See AWS Service Quotas |

Azure OpenAI raises its file cap to 1 GB with bring-your-own Blob Storage. The
Vertex AI cap applies to Cloud Storage input. Amazon Bedrock also caps total job
size, at 5 GB for most models.

### ID encoding (from "How ID Encoding Works", verbatim)

```
Original:  file-abc123
Encoded:   file-bGl0ZWxsbTpmaWxlLWFiYzEyMzttb2RlbCxncHQtNG8tdGVzdA
           └─┬─┘ └──────────────────┬──────────────────────┘
          prefix      base64(litellm:file-abc123;model,gpt-4o-test)
Original:  batch_xyz789
Encoded:   batch_bGl0ZWxsbTpiYXRjaF94eXo3ODk7bW9kZWwsZ3B0LTRvLXRlc3Q
           └──┬──┘ └──────────────────┬──────────────────────┘
           prefix       base64(litellm:batch_xyz789;model,gpt-4o-test)
```

The encoding: preserves OpenAI-compatible prefixes (`file-`, `batch_`), is
transparent to clients, enables automatic routing without additional parameters,
and works across all batch and file endpoints.

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited**
  (Corroborates, Extends — see below).
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **cited** (Extends — see
  below).
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guardrails, pre-on-caller patterns; no
  gateway-rate-limit or batch-accounting content.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: Auto Router v2
  scoring/mode collapse; no batch or quota-accounting content.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP /
  coding-agent integration; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  telemetry shipping paths; no batch or rate-limit-accounting content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization/measurement; unrelated to batch quota accounting.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  Langfuse scanner stacks and latency drivers; different guardrail vendor/surface
  from the LiteLLM batch-upload guardrail placement (Claim 11 here).
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: served agent-card
  field matrix; no batch or rate-limit surface.
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **dismissed**:
  `/messages`→`/responses` parameter mapping; different gateway surface. (It
  shares the corpus-wide "silently-degraded config/param" family resemblance,
  not a claim-level bond.)

**Additional cross-references found by searching `source-notes/`:**
(Prospector-named overlaps verified — see dismissals below.)

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` **Claim 5** (over-cap
    responses are HTTP 429 with `"type": "budget_exceeded"` — a *cost* cap
    surfaces as the same status class as ordinary rate limiting). The batches
    page complements this from the batch side: an enqueued-token allowance
    overage is also a 429 at submission (Claim 3 here), so "429" carries at
    least three distinct LiteLLM meanings documented in the corpus
    (rate-limited, budget-exceeded on the agent path, enqueued-token-over)
    that callers can only disambiguate by error type / message — a single
    corpus-wide warning the guide already gives for the A2A path.
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 6** (on
    passthrough conflicts "the admin wins" — `static_headers` always sent,
    `extra_headers` an admin allowlist). Converges on the same
    admin-authority principle this page documents for batch metadata: only a
    proxy admin can write `batch_enqueued_token_limit` (other roles 403), and
    the global `general_settings` skip knobs outrank the (ignored) request-level
    flag — configuration authority is consistently admin-only across both
    surfaces.
- **Contradicts**: None. No existing source note makes a claim about batch
  rate-limit or cost accounting that this page opposes (string search for
  `batch_enqueued|/v1/batches|batch rate` returns zero hits across every
  candidate, Prospector-named, and litellm-family note in `source-notes/`). The
  candidate tensions were analyzed per MINER §4a and resolved as
  non-contradictions: (a) "the file is charged at submission" vs
  "guardrails/validation happen at upload" — different surfaces (rate limits at
  `POST /v1/batches`; validation/guardrails at `POST /v1/files`), stated as such
  on the page, no opposition; (b) "counters are not reconciled" vs the A2A
  budget note's accumulated-spend semantics — different metering domains
  (batch-estimate vs per-call session counter), no claim conflict. Verified open
  contradiction issues (#1150, #1307, #1322, #1338, #1352, #1408) and
  `CONTRADICTIONS.md` (no entries matching batch/429 beyond the iteration-budget
  entry) confirm no duplicate exists. No contradiction issue filed.
- **Extends**:
  - `source-notes/docs-litellm-a2a-cost-tracking.md` — that note maps two
    cost-attribution axes (measured vs declared) with **no documented
    reconciliation** (its Claim 3: flat per-query charge with no linkage to
    measured usage; Claim 8: no reconciliation between the two axes). This page
    adds a third, batch-specific axis where the docs are *explicit* about the
    gap: batch TPM/RPM counters are "not reconciled against the provider's final
    usage" and the Enterprise cost aggregate is an `aretrieve_batch` record
    separate from submission. Together they give Ch05 a coherent "LiteLLM cost
    surfaces are reconciliations-by-hand, not ledgers" family.
  - `source-notes/docs-litellm-streaming-token-usage.md` — that note (Claim 1)
    establishes that streaming usage is usage-blind by default unless the client
    opts in. The batches page is the second metering-surface precondition in the
    corpus: batch TPM/RPM are charged from a *pre-read estimate* of the input
    file, not from provider-reported usage. Both notes bound "what a gateway
    counter actually promises": streaming tokens exist only if `include_usage`;
    batch tokens are a submission-time estimate never reconciled. Distinct
    surfaces, no shared claims, no contradiction (matching the Prospector).
  - `source-notes/docs-litellm-token-usage-helpers.md` — that note (Claims 1-4)
    shows the client-side estimators derive entirely from the bundled
    `model_cost` map with no provider-side reconciliation. The batches page is
    gateway-side confirmation of the same architecture: batch cost tracking
    aggregates provider token usage but only with an Enterprise license, and the
    non-Enterprise path keeps batch spend invisible — a spend-visibility gap
    that belongs next to the local-estimator caveats (Ch05).
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — that
    incident note (Extracted Lessons → Lesson 2) teaches that silent
    cost-accounting failures prevent operators from connecting symptoms to
    causes. The batches page adds a second, documented-by-design instance of the
    same class: an all-failed batch records zero usage and zero cost **without
    error** (so "zero cost for a batch" must never be read as "no work was
    attempted"), and an undownloadable input file submits a batch that is never
    charged with only a logged error to warn the operator. Both are
    "cost/usage accounting diverges from reality with a weak or absent signal"
    failure classes on LiteLLM's own accounting surfaces.
  - `source-notes/docs-litellm-adaptive-router.md` — the routing surface that
    note covers is real-time request routing (7 request types, quality/cost
    bandits). The batches page extends the route-resolution surface with
    batch/file multi-account routing via base64-encoded IDs (Claim 10 here) —
    a different routing mechanism (ID-embedded intent vs learned per-type
    scoring) on the same gateway, relevant to RAG/agent teams that split batch
    jobs across provider accounts.
  - `source-notes/docs-litellm-gateway-auth-reference.md` — see Corroborates.
- **Novel**: First source note in the corpus covering the LiteLLM Batch API's
  quota and cost-accounting semantics: submission-time charging with atomic
  whole-file limit checks and 429-before-forwarding; the per-record counting
  contract (RPM/TPM/ITPM/OTPM incl. `n`/`best_of` and the v3-estimate fallback);
  `batch_enqueued_token_limit` as the outstanding-work-allowance pattern with
  its 8-day unobserved-terminal-state leak; the explicit unmetered-submission
  enforcement gaps; the Enterprise-only cost tracking with the "zero cost ≠ no
  work" corner case; and the base64-ID multi-account routing scheme. The guide's
  existing "batch" coverage (Ch02 batch-pipeline freshness SLOs; Ch05 batch
  evals / large-result downloads) is a different sense of the word and does not
  touch gateway batch-quota accounting.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — rate limits, cost, capacity)**:
  (1) Add the submission-time batch charging model as a distinct gateway
  rate-limit shape: the whole input file is charged to a single per-minute
  window at `POST /v1/batches`, so per-minute TPM/RPM limits structurally fit
  batch work badly — the page's own remedy, `batch_enqueued_token_limit`, is
  the batch-shaped alternative (an outstanding-work allowance). Recommend the
  chapter teach both shapes and when to combine them. (2) Extend the existing
  "over-cap shares a status code with rate limiting" guidance
  (guide/05-llm-ops-reliability.md:1167, sourced from
  `docs-litellm-a2a-iteration-budgets`): batch admission adds a third 429
  meaning (enqueued-token overage), so batch clients must branch on error type,
  not status. (3) Add the enforcement-gap caveats to any "gateway enforces batch
  quotas" guidance: counters are submission-time estimates never reconciled
  with provider usage, and a batch submitted with an undownloadable input file
  is never charged — alert on the logged error if strict enforcement is
  expected (Claim 6). (4) In the cost section, pair the model-cost-map and
  token-accounting notes with the batch corner case: Enterprise-gated batch
  spend means OSS deployments have no automated batch cost records, and a fully
  failed batch records zero usage and zero cost (Claim 9).
- **Chapter 02 (Observability)**: Teach that gateway batch counters are an
  estimate, not an audit trail — batch TPM/RPM are computed from the input file
  at submission and never reconciled with the provider (Claim 6); final batch
  cost only appears via the Enterprise `aretrieve_batch` aggregate, recorded
  separately from submission (Claim 9). Add the "zero cost ≠ zero work" rule for
  batch spend dashboards, and recommend monitoring the logged
  un-readable-file/unmetered-submission errors that the docs themselves flag
  for strict-enforcement deployments.
- **Chapter 06 (Security and Trust)**: Add two items from this page: (a) the
  admin-only metadata gate — `batch_enqueued_token_limit` writes from non-admin
  key/team roles are rejected with 403, so batch allowance is a proxy-admin
  configuration authority (Claim 3); (b) the model-allowlist override — skip
  settings that disable batch rate-limit accounting never skip the file
  download when a key has a model allowlist, because every `body.model` must
  still be validated per record (Claim 5), and guardrails run against the batch
  input file at upload time (Claim 11).
- **Chapter 04 (Runbooks / batch job toil)**: Reference the pre-forward
  validation gates as the batch-admission contract: `max_batch_file_size_mb`
  (413, "not forwarded to the provider", separate from `max_request_size_mb`)
  and the always-on content validation (400 with `param` and 1-based line
  numbers counting blank lines), plus the provider-caps table as the input to
  choosing the cap (Claims 7-8). File generators must remember line numbers
  count blank lines (Claim 7 assessment).

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/batches`, HTTP 200, no paywall, no truncation).
  The page is a substantial reference (~5 KB of body text): Quick Start (4 tabs,
  CRUD examples), Multi-Account / Model-Based Routing (priority order, encoding
  walkthrough, endpoint routing table), Supported providers, Batch Input File
  Validation (size cap + content rules + provider caps), How Rate Limiting for
  Batches API Works (counting contract, enqueued-token limits, operational
  behavior, skip settings), and How Cost Tracking for Batches API Works. The
  linked per-provider batch pages, the managed-files beta, and the "Batch API
  Guardrails" page were **not** absorbed, per the Prospector's bounding; the
  guardrails placement is recorded as a claim (Claim 11) without re-extracting
  that page.
- Triage bounding honored (#1415, `triaged:text`, `priority:high`). Extraction
  followed the Prospector's numbered items: submission-time charging (Claim 1),
  per-record counting contract (Claim 2), batch-shaped allowance + 8-day leak
  (Claim 3), the `LITELLM_TPM_TOKEN_RESERVATION_ENABLED` misconfiguration trap
  (Claim 4), skip/dead knobs incl. the no-op `_for_models` (Claim 5), the
  enforcement-gaps table (Claim 6), the validation contract + provider caps
  (Claims 7-8), Enterprise-gated cost tracking (Claim 9), ID-encoded
  multi-account routing (Claim 10), and upload-time guardrails (Claim 11). The
  generic quick-start CRUD was deliberately not mined as a learning object.
- All `Quote` fields and Concrete Artifacts are verbatim contiguous fragments
  from the fetched page, copied character-for-character; no splicing across
  non-adjacent sentences. Where a claim rests on the Miner's synthesis (e.g.
  "counter is an estimate, not a ledger" in Claim 6; the 429 disambiguation
  reading in Corroborates) it is labeled as such and placed outside `Quote`.
- `confidence_overall` is `settled`, following the Prospector's explicit
  novelty caveat: every claim here is documented **product behavior / schema
  contract** (which requests charge which limits, when 429/403/413/400 return,
  the 8-day expiry, the provider-cap table) — deterministic, stated
  first-party, with no benchmarks and no effectiveness claims on the page.
  Sibling LiteLLM notes use `emerging` where their value is synthesis over a
  capability surface; this page's value is the contract itself. The routing
  precedence is bounded per triage: the page does not state a header-vs-query-vs-
  body precedence, and none is asserted (Claim 10).
- `miner-related-notes.md` was read before writing Cross-References; all ten
  listed candidate paths are cited or dismissed above. Primary
  cross-reference verification (MINER §4b) re-read the cited claims/artifacts:
  `docs-litellm-a2a-iteration-budgets.md` (Claim 5, 429 `budget_exceeded`),
  `docs-litellm-a2a-cost-tracking.md` (Claims 3 & 8, declared-vs-measured +
  no-reconciliation), `docs-litellm-streaming-token-usage.md` (Claim 1,
  usage opt-in), `docs-litellm-token-usage-helpers.md` (Claims 1-4, local
  estimators), `failure-litellm-model-cost-map-silent-fallback.md` (Extracted
  Lessons → Lesson 2), `docs-litellm-gateway-auth-reference.md` (Claim 6, admin
  wins), and `docs-litellm-adaptive-router.md` (topic-level, real-time routing
  surface). No claim numbers invented. String search
  `batch_enqueued|/v1/batches|batch rate` across all candidate + litellm-family
  notes returns zero hits, confirming the triage's duplicate check and the
  Novel finding.
- No contradiction issue filed. The two candidate tensions (submission-time
  charging vs upload-time validation/guardrails; unreconciled batch counters vs
  A2A accumulated-spend counters) were analyzed per MINER §4a — both resolve to
  distinct surfaces or distinct metering domains that the page itself
  distinguishes, neither existing note asserts the opposing position, and
  verified open `contradiction`-labeled issues (#1150, #1307, #1322, #1338,
  #1352, #1408) plus CONTRADICTIONS.md confirm no duplicate exists. See the
  Contradicts section for the resolution logic.
- `date_published` is unknown (living Docusaurus page); `date_extracted` and
  `last_checked` are both 2026-09-22 (UTC).