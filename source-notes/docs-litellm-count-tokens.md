---
source_url: https://docs.litellm.ai/docs/count_tokens
source_type: docs
title: "Token Counting (count_tokens) — liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-10-09)
date_extracted: 2026-10-09
last_checked: 2026-10-09
status: current
confidence_overall: emerging
issue: "#1650"
---

# Token Counting (liteLLM Docs)

> LiteLLM's `/docs/count_tokens` page is the SDK/proxy home of pre-flight token
> counting. Its ops-relevant delta over the sibling `/docs/anthropic_count_tokens`
> note (#1381, which followed this page as a linked reference) is the
> **observability + silent-degradation contract** around the count: the
> `TokenCountResponse` object carries a `tokenizer_type` discriminator
> (`openai_api` / `anthropic_api` / `bedrock_api` / `bedrock_mantle_api` /
> `local_tokenizer`) that records *which* counting backend actually answered, and
> the Bedrock Claude fallback chain (`bedrock-runtime` 400 → `bedrock-mantle`,
> requiring the IAM action `bedrock-mantle:CountTokens`) means a **missing IAM
> permission turns a provider-exact count into a local tiktoken estimate with no
> caller-visible error** — the count "succeeds" with a wrong-provenance number,
> and both failures appear only in the proxy log.

## Source Context

- **Type**: docs (single-page LiteLLM SDK/proxy token-counting reference, part of
  the `litellm-docs` site-crawl seed via the LLM-gateway scope)
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the SDK response object, the `tokenizer_type` enum, the
  Bedrock fallback mechanics, and the `litellm_params` overrides it names. It is
  vendor documentation of a gateway behavior — the count-degradation path is not
  independently exercised here against a live Bedrock deployment.
- **Scope**: The `litellm.acount_tokens()` SDK response contract, the fallback
  behavior, the Bedrock Claude (mantle) fallback chain and its IAM/bearer
  prerequisites, the `/v1/responses/input_tokens` OpenAI-format proxy endpoint,
  and a two-model proxy `config.yaml`. Does **not** cover: rate limits, caching,
  pricing, or any failure writeup beyond the mantle 400/403 path.
- **Relationship to `docs-litellm-anthropic-count-tokens.md` (#1381)**: that
  note is bound to the sibling page `/docs/anthropic_count_tokens` and, per its
  own Source Context, followed *this* page as the "Previous" nav link, taking the
  local-tiktoken fallback, the proxy concurrency env vars
  (`TOKEN_COUNTER_MAX_CONCURRENT_COUNTS` / `TOKEN_COUNTER_MAX_EXACT_CHARS`), and
  the OpenAI-format endpoint from it. This note is the primary extraction of the
  `/docs/count_tokens` page and is scoped to the material #1381 did **not**
  capture: the `TokenCountResponse` / `tokenizer_type` contract and the Bedrock
  mantle fallback chain. The fallback env vars and the six-row provider routing
  table are deliberately **not** re-extracted (cross-linked to #1381 Claims 7 and
  2). No contradiction issue was indicated by triage or found on re-read (see
  Cross-References → Contradicts).

## Extracted Claims

### Claim 1: `litellm.acount_tokens()` returns a `TokenCountResponse` whose `tokenizer_type` field records which counting backend actually answered — `openai_api`, `anthropic_api`, `bedrock_api`, `bedrock_mantle_api`, or `local_tokenizer`
- **Evidence**: The "Response Format" section prints the returned object and its
  inline comment enumerates the five allowed `tokenizer_type` values; the two
  "Basic Usage" examples assert the expected value per provider (`# "openai_api"`
  for the OpenAI call, `# "anthropic_api"` for the Anthropic call).
- **Confidence**: settled (documented first-party SDK response contract)
- **Quote**: `# "openai_api", "anthropic_api", "bedrock_api", "bedrock_mantle_api", "local_tokenizer"`
- **Our assessment**: This is the single most consequential field on the page for
  operations, and it is the delta #1381 does not have: the counting path is
  **self-describing**. A caller that reads only `total_tokens` cannot tell a
  provider-exact count from a local tiktoken estimate; a caller that reads
  `tokenizer_type` can. Any pre-flight context-budget gate built on this endpoint
  can therefore assert the provenance of the number it is about to trust, rather
  than assuming "pre-flight count == provider-authoritative count."

### Claim 2: The count response signals counting failures **in-band** — `error` ("True if counting failed") and `error_message`, returned alongside `total_tokens`, `request_model`, `model_used`, and `original_response`, rather than raised as an exception
- **Evidence**: The "Response Format" object lists the six fields plus the two
  error fields; the inline comments define `error` and `error_message`.
- **Confidence**: settled (documented response contract)
- **Quote**: "`error=False,               # True if counting failed`" / "`error_message=None,        # Error details if failed`"
- **Our assessment**: Combined with Claim 1, a caller must check **two**
  independent signals: `error` (the count failed outright) and `tokenizer_type`
  (the count succeeded but via a fallback backend). A counting-dependent gate
  that only handles a raised exception, or only checks `error`, will treat a
  `local_tokenizer` response as a normal provider count. The `original_response`
  field is the raw provider payload, which is where an operator would confirm the
  upstream shape when reconciling a suspicious number.

### Claim 3: On Bedrock, counting is a two-hop chain — `bedrock-runtime`'s CountTokens API 400-rejects a named set of Claude models ("Claude Opus 4.8, 5 and 5.5 when this was written"), and LiteLLM re-sends the same body to `bedrock-mantle` signed with the deployment's AWS credentials, reporting `tokenizer_type: "bedrock_mantle_api"`; models `bedrock-runtime` accepts stay `tokenizer_type: "bedrock_api"`
- **Evidence**: The "Bedrock Claude models" section states the rejection set, the
  host, the signing, and the resulting `tokenizer_type`; it also states the
  negative case for models that do not need the hop.
- **Confidence**: settled (documented vendor fallback mechanism; the named
  model set is explicitly time-stamped "when this was written")
- **Quote**: "The bedrock-runtime CountTokens API rejects some Claude models with a 400 (Claude Opus 4.8, 5 and 5.5 when this was written). For a Claude model it rejects, LiteLLM sends the same body to bedrock-mantle (https://bedrock-mantle.<region>.api.aws/anthropic/v1/messages/count_tokens), signed with the deployment's AWS credentials, and reports tokenizer_type: "bedrock_mantle_api"."
- **Our assessment**: This is the mechanism the provider routing table only
  gestures at — the "Bedrock (Claude)" row now reads "AWS Bedrock CountTokens API,
  then bedrock-mantle for a Claude model it rejects." An operator reading the
  `tokenizer_type` sees three Bedrock outcomes with different trust levels:
  `bedrock_api` (runtime counted it), `bedrock_mantle_api` (runtime rejected it,
  Mantle counted it), and `local_tokenizer` (neither counted it — see Claims 4-6).
  The named model set is snapshot-bound and will drift as AWS adds coverage.

### Claim 4: The Bedrock mantle hop has an IAM precondition with a **silent** failure mode — the credentials need `bedrock-mantle:CountTokens` next to `bedrock:CountTokens`; without it Mantle answers 403 and the count falls back to the local tokenizer, with both errors visible only in the proxy log
- **Evidence**: The "Bedrock Claude models" section states the required IAM
  action pair, the 403 consequence, the fallback, and where the errors surface.
- **Confidence**: settled (documented permission contract and documented
  degradation consequence)
- **Quote**: "The credentials need the IAM action `bedrock-mantle:CountTokens` next to `bedrock:CountTokens`. Without it Mantle answers 403 and the count falls back to the local tokenizer, with both errors in the proxy log."
- **Our assessment**: This is the strongest new ops item and the answer to the
  triage's key question. The degradation is triggered by an **IAM policy**, not a
  config change and not an outage: a deployment that can count most Claude models
  exactly will, for the rejected models, silently answer with a local tiktoken
  estimate because one IAM action is missing. The caller gets
  `total_tokens` with `tokenizer_type: "local_tokenizer"` and no exception; the
  `400` from bedrock-runtime and the `403` from Mantle exist only in the proxy
  log. A pre-flight gate that reads `total_tokens` before sending the request
  will therefore size the context window against an estimate without ever
  surfacing that its "authoritative" count degraded. This extends #1381 Claim 7's
  trigger list (unsupported provider / missing API key) with a third,
  permission-shaped trigger.

### Claim 5: `BEDROCK_MANTLE_API_BASE` is the only override that redirects the Mantle call — the deployment's `api_base` and `aws_bedrock_runtime_endpoint` apply to `bedrock-runtime` only — so a VPC/private-endpoint deployment that sets those two and not `BEDROCK_MANTLE_API_BASE` loses exact counting for the rejected models, and `AWS_BEARER_TOKEN_BEDROCK` rides to Mantle as the bearer token under the same policy
- **Evidence**: The "Bedrock Claude models" section names the override, scopes the
  two runtime-only settings, and states the bearer-token forwarding.
- **Confidence**: settled (documented override scoping) / the VPC-deployment
  consequence is the Miner's reading of the scoping
- **Quote**: "Set `BEDROCK_MANTLE_API_BASE` to send the Mantle call to another host, for example a VPC endpoint. The deployment's `api_base` and `aws_bedrock_runtime_endpoint` apply to bedrock-runtime only."
- **Our assessment**: The scoping split is the second silent-degradation lever.
  In a locked-down Bedrock deployment the operator follows the conventional
  guidance — set `api_base` and `aws_bedrock_runtime_endpoint` for the private
  endpoint — and reasonably expects the counting path to inherit it. It does not:
  the Mantle hop needs its own `BEDROCK_MANTLE_API_BASE`, and without it the
  rejected-model count degrades exactly as in Claim 4. Because
  `AWS_BEARER_TOKEN_BEDROCK` is forwarded to Mantle, the same IAM policy governs
  the bearer-token path, so a key configured for `bedrock:CountTokens` alone
  still trips the 403.

### Claim 6: Local fallback is the default terminal state for Bedrock counting — a Claude model Mantle does not serve in the region, and any non-Claude model, keeps the local fallback
- **Evidence**: The closing sentence of the "Bedrock Claude models" section.
- **Confidence**: settled (documented fallback boundary)
- **Quote**: "A Claude model Mantle does not serve in the region, and any non-Claude model, keeps the local fallback"
- **Our assessment**: Together with Claims 3-5 this defines the full Bedrock
  counting decision tree and makes `local_tokenizer` the expected, not
  exceptional, outcome for models outside the runtime+Mantle coverage. It is a
  conditioning variable for a gate author: the returned `total_tokens` is only
  provider-authoritative for the subset of models that one of the two AWS
  counting APIs serves in the configured region.

### Claim 7: The proxy exposes a distinct OpenAI-format pre-flight counting endpoint, `POST /v1/responses/input_tokens`, returning `{"object": "response.input_tokens", "input_tokens": N}` — a different wire shape from the Anthropic-format `/v1/messages/count_tokens`
- **Evidence**: The "Proxy Usage → OpenAI Format" section and its curl/httpx
  examples; the "Overview" feature table lists both proxy endpoints.
- **Confidence**: settled (documented endpoint contract)
- **Quote**: "`{"object": "response.input_tokens", "input_tokens": 13}`"
- **Our assessment**: Recorded briefly per triage — #1381 already captured the
  endpoint surface. The only added nuance here is that the OpenAI-format response
  carries an `object` envelope (`response.input_tokens`) in addition to the
  integer, unlike the bare `{"input_tokens": N}` Anthropic shape; a client that
  parses only `input_tokens` is portable across both, one that asserts the full
  envelope is not. Neither proxy endpoint is documented here as returning the
  `tokenizer_type` discriminator that the SDK object carries, so an HttpOnly
  caller may not get the provenance observable of Claim 1 — worth verifying.

### Claim 8: `tokenizer_type` (and the `error` flag) is the monitoring signal that makes silent count-degradation detectable — a proxy log/metric keyed on it distinguishes `local_tokenizer` answers from provider-exact ones that look identical in `total_tokens`
- **Evidence**: The page documents `tokenizer_type` as a returned field (Claim 1)
  and the degradation path as silent except for proxy-log errors (Claim 4). The
  monitoring use is the Miner's synthesis of those two documented facts.
- **Confidence**: emerging (synthesis across the documented response contract and
  the documented silent-fallback behavior; not a page claim and not exercised
  against a live deployment)
- **Quote**: (no direct quote; the synthesis is stated in Our assessment)
- **Our assessment**: This is the guide-actionable conclusion of the note. The
  page gives an operator the exact observable needed to answer "did my count
  degrade?" but never says to watch it. A monitoring query over the counting
  path's `tokenizer_type` distribution — alerting when `local_tokenizer` appears
  for a model that should be counted by `bedrock_api` / `bedrock_mantle_api` —
  turns the silent IAM/quota-induced fallback into a visible signal. Absent that,
  the only evidence is the two errors buried in the proxy log.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/count_tokens (fetched
2026-10-09, HTTP 200, no paywall), unless noted.

### `TokenCountResponse` shape (from "SDK Usage → Response Format", verbatim)

```python
litellm.acount_tokens() returns a TokenCountResponse:

TokenCountResponse(
    total_tokens=15,           # Token count
    request_model="openai/gpt-5.6-terra",  # Model requested
    model_used="gpt-5.6-terra",      # Model used for counting
    tokenizer_type="openai_api",    # "openai_api", "anthropic_api", "bedrock_api", "bedrock_mantle_api", "local_tokenizer"
    original_response={"input_tokens": 15},  # Raw API response
    error=False,               # True if counting failed
    error_message=None,        # Error details if failed
)
```

### Bedrock Claude models (from the "Bedrock Claude models" section, verbatim prose)

> The bedrock-runtime CountTokens API rejects some Claude models with a 400
> (Claude Opus 4.8, 5 and 5.5 when this was written). For a Claude model it
> rejects, LiteLLM sends the same body to bedrock-mantle
> (`https://bedrock-mantle.<region>.api.aws/anthropic/v1/messages/count_tokens`),
> signed with the deployment's AWS credentials, and reports `tokenizer_type:
> "bedrock_mantle_api"`. A model bedrock-runtime counts never reaches Mantle and
> keeps `tokenizer_type: "bedrock_api"`
>
> The credentials need the IAM action `bedrock-mantle:CountTokens` next to
> `bedrock:CountTokens`. Without it Mantle answers 403 and the count falls back
> to the local tokenizer, with both errors in the proxy log. A Bedrock API key
> (`AWS_BEARER_TOKEN_BEDROCK`) is sent to Mantle as the bearer token, so the same
> policy applies to it
>
> Set `BEDROCK_MANTLE_API_BASE` to send the Mantle call to another host, for
> example a VPC endpoint. The deployment's `api_base` and
> `aws_bedrock_runtime_endpoint` apply to bedrock-runtime only. A Claude model
> Mantle does not serve in the region, and any non-Claude model, keeps the local
> fallback

### OpenAI-format proxy endpoint (from "Proxy Usage → OpenAI Format", verbatim)

```
curl -X POST "http://localhost:4000/v1/responses/input_tokens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -d '{
    "model": "gpt-5.6-terra",
    "input": "Hello, how are you?"
  }'
```

Response:

```
{"object": "response.input_tokens", "input_tokens": 13}
```

### Provider routing table — Bedrock row (from "Supported Providers", verbatim cell)

| Provider | Token Counting API | Format |
|---|---|---|
| Bedrock (Claude) | AWS Bedrock CountTokens API, then bedrock-mantle for a Claude model it rejects (see Bedrock Claude models) | Anthropic Messages |

### Proxy configuration (from "Proxy Configuration", verbatim)

```yaml
model_list:
  - model_name: gpt-5.6-terra
    litellm_params:
      model: openai/gpt-5.6-terra
      api_key: os.environ/OPENAI_API_KEY
  - model_name: claude-sonnet-5
    litellm_params:
      model: anthropic/claude-sonnet-5
      api_key: os.environ/ANTHROPIC_API_KEY
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch input-file
  TPM/RPM limiting and enqueued-token reservations; a rate-limit surface with no
  counting-endpoint or tokenizer-provenance content.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  transcription-endpoint support matrix; no token-counting contract.
- `source-notes/docs-litellm-completion-web-search.md` — **Dismissed**:
  provider-native web search across chat/responses; unrelated to counting.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: the Bedrock
  native `/invoke` completions passthrough (SigV4→Bearer auth swap); the
  CountTokens/Mantle path is a *separate* AWS API, so the shared "Bedrock"
  vocabulary does not imply a shared mechanism.
- `source-notes/docs-litellm-completion-web-fetch.md` — **Dismissed**: Anthropic
  `web_fetch` server tool; no counting content.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Dismissed**:
  within-request advisor composition and its split `usage`; unrelated.
- `source-notes/docs-litellm-completion-input-params.md` — **Dismissed**:
  supported-params gate / hard-coded exemptions; no counting-endpoint content.
- `source-notes/docs-litellm-mock-requests.md` — **Dismissed**: `mock_response`
  stub below the provider layer (null usage fields); unrelated.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  session iteration/budget caps keyed on trace ids; a different pre-spend
  gateway control with no counting-path mechanism in common.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **Dismissed**: per-agent
  flat/token cost ledger; a cost-attribution surface that presupposes token
  counts but documents no counting endpoint or degradation path.

**Additional cross-references found by searching `source-notes/`:**

- `source-notes/docs-litellm-anthropic-count-tokens.md` — **Cited** (primary
  Extends; see below).
- `source-notes/docs-litellm-claude-code-compatibility.md` — **Cited** (Extends;
  see below).
- `source-notes/docs-litellm-token-usage-helpers.md` — **Cited** (Corroborates;
  see below).
- `source-notes/docs-litellm-streaming-token-usage.md` — **Cited**
  (Corroborates; see below).
- `source-notes/docs-litellm-completion-message-trimming.md` — **Cited**
  (Corroborates; see below).

**Primary cross-references (verified per MINER §4b — every numbered claim was
re-read in the cited note before writing):**

- **Extends**:
  - `source-notes/docs-litellm-anthropic-count-tokens.md` (#1381) — **primary
    overlap; this note is framed as a correction/extension to it.** #1381
    **Claim 7** documents that provider routing is not total and falls back to
    local tiktoken for unsupported providers / missing keys; this page adds the
    *observable* of that fallback (`tokenizer_type`, Claim 1 here) and a third
    trigger (a missing `bedrock-mantle:CountTokens` IAM action, Claims 4-5 here).
    #1381 **Claim 2**'s routing table lists the Bedrock row as the plain "AWS
    Bedrock CountTokens API"; this page's table (Claim 3 here) adds the
    "then bedrock-mantle for a Claude model it rejects" hop. #1381 **Claim 6**
    frames the endpoint as a free pre-flight context-budget gate; this note adds
    that a gate can now verify the *provenance* of the count it gates on
    (Claims 1, 8 here). Same page family, two evidence slices — the Assayer
    should reconcile rather than treat them as independent claims.
  - `source-notes/docs-litellm-claude-code-compatibility.md` **Claim 6** — the
    compatibility matrix's `count_tokens endpoint` parity row shows the
    `bedrock_mantle` column entirely `—` (no test ran). This page supplies the
    *mechanism* behind that untested route: the bedrock-runtime 400 → Mantle hop
    and its IAM precondition (Claims 3-5 here). The matrix explains which
    providers were exercised; this page explains the fallback mechanics of the
    one column that was not. (Verified: Claim 6 read in full.)
- **Corroborates**:
  - `source-notes/docs-litellm-token-usage-helpers.md` **Claim 2** — local
    `token_counter` "can diverge from provider-reported totals." The
    `local_tokenizer` value in Claim 1 here is exactly that local surface
    observed as a *fallback outcome*: this page shows which runtime conditions
    (missing key, unsupported provider, Bedrock IAM gap/region gap) route a count
    onto it. (Verified: Claim 2 read in full.)
  - `source-notes/docs-litellm-streaming-token-usage.md` **Claim 1** — the
    post-hoc response-usage surface is usage-blind by default. This page is the
    **pre-flight** leg of the same three-way estimate / pre-flight / post-hoc
    split #1381 identified; both notes turn on a client/gateway decision (opt-in
    flag there, IAM/bearer policy here) that silently changes what the number
    means. (Verified: Claim 1 read in full.)
  - `source-notes/docs-litellm-completion-message-trimming.md` — that note's
    cross-references cite #1381 Claim 7 for "provider routing for token counting
    is not total and falls back to local tiktoken counting." This page names the
    concrete Bedrock trigger for that fallback (the Mantle 403), giving the
    trim-budget consequence (trim fires early/late against a local estimate) a
    specific, deploy-reproducible cause. (Verified: the cited cross-reference
    passage read in full.)
- **Contradicts**: None filed (MINER §4a). The nearest candidate tension — this
  page's source is the same page #1381 extracted fallback/env-var material from,
  so a reader might expect disagreement — is not a contradiction: the two notes
  address different slices (wire/auth/routing there; response-provenance and the
  Bedrock chain here) and this note deliberately does **not** re-extract the
  env-var bounds. Verified against the open `contradiction`-labeled issues
  (#1633, #1597, #1593, #1591, #1565, #1562, #1550, #1548, #1534, #1517, #1514,
  #1486, #1462, #1461, #1408, #1352, #1338, #1322, #1307, #1150) and
  `CONTRADICTIONS.md` (no `C-NNN` entries): none touch the count_tokens surface.
  No contradiction issue filed.
- **Novel**: First corpus coverage of the **count-response provenance contract
  and the Bedrock mantle fallback chain.** Re-checked this session: a string
  search for `tokenizer_type`, `TokenCountResponse`, `bedrock-mantle`, and
  `BEDROCK_MANTLE_API_BASE` returns zero hits across `source-notes/` and `guide/`.
  Specifically new: (1) the five-value `tokenizer_type` enum as the "which
  counter answered" observable (Claim 1); (2) in-band `error`/`error_message`
  signaling (Claim 2); (3) the bedrock-runtime 400 → Mantle hop and its
  `bedrock_mantle_api` result (Claim 3); (4) the `bedrock-mantle:CountTokens` IAM
  precondition and the 403 → silent-local-fallback failure mode (Claim 4);
  (5) the `BEDROCK_MANTLE_API_BASE`-only override scoping (Claim 5); and (6) the
  monitoring synthesis that makes the degradation detectable (Claim 8).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Streamed traffic is usage-blind by
  default" (`guide/05-llm-ops-reliability.md:1209-1242`)**: that section already
  teaches the streaming opt-in path and the local-estimator path. Add the
  **pre-flight counting path** with its provenance caveat: `litellm.acount_tokens()`
  returns a `TokenCountResponse` whose `tokenizer_type` says whether the number
  was provider-exact (`openai_api` / `anthropic_api` / `bedrock_api` /
  `bedrock_mantle_api`) or a local estimate (`local_tokenizer`) [Claim 1]
  [settled]. Recommend the section's rule gain a third metering path and its
  detection: (a) a count is only provider-authoritative when `tokenizer_type` is
  a provider value, and on Bedrock that requires `bedrock-mantle:CountTokens`
  IAM plus (for private endpoints) `BEDROCK_MANTLE_API_BASE` — missing either
  degrades the count silently [Claims 4, 5] [settled]; (b) monitor the
  `tokenizer_type` distribution on the counting path so an unexpected
  `local_tokenizer` for a model that should be provider-counted becomes an alert
  rather than a proxy-log-only error [Claim 8] [emerging].
- **Chapter 05 (Model enablement / config verification, alongside the
  `vertex_count_tokens_location` guidance from #1381 Claim 3)**: add the Bedrock
  equivalent — a gateway serving the Claude models bedrock-runtime 400-rejects
  must carry `bedrock-mantle:CountTokens` next to `bedrock:CountTokens`
  [Claim 4] [settled], and a VPC/private-endpoint deployment must also set
  `BEDROCK_MANTLE_API_BASE` because `api_base` / `aws_bedrock_runtime_endpoint`
  apply to bedrock-runtime only [Claim 5] [settled]. Recommend verifying the
  count's `tokenizer_type` post-deploy for each Bedrock model rather than
  assuming inference success implies exact counting — an inference smoke test
  passes while counting silently estimates.
- **Chapter 02 (Observability)**: where the chapter treats token counts as a
  metric source (per `docs-datadog-llm-observability` and the sibling LiteLLM
  notes), keep the **pre-flight** count distinct from the post-hoc response
  usage and attach its `tokenizer_type` provenance as a label. A count that
  degraded to `local_tokenizer` is indistinguishable from a provider-exact count
  by value alone, so the provenance field — not the number — is what makes the
  metric trustworthy [Claims 1, 4, 8] [emerging].

## Extraction Notes

- Source read in full via WebFetch (markdown) plus a raw HTML fetch of
  `https://docs.litellm.ai/docs/count_tokens` (HTTP 200, no paywall) to confirm
  the exact prose of the Bedrock section and the `TokenCountResponse` field
  comments; both passes agree. No sub-pages followed: the page's only substantive
  outbound link is the sibling `/docs/anthropic_count_tokens`, which is already
  the separate source note #1381 (`docs-litellm-anthropic-count-tokens.md`) and is
  cross-linked, not re-mined.
- Triage bounding honored: the fallback env vars
  (`TOKEN_COUNTER_MAX_CONCURRENT_COUNTS` / `TOKEN_COUNTER_MAX_EXACT_CHARS`), the
  six-row provider auto-routing table, and the generic local-tiktoken fallback
  are **not** re-extracted — #1381 Claims 7 and 2 already cover them, and they
  are cross-linked. The note is scoped to the `TokenCountResponse` /
  `tokenizer_type` contract and the Bedrock mantle chain, per the triage's
  "extract only the delta" instruction, and is explicitly framed as an
  extension/correction to #1381.
- All `Quote` fields are character-for-character contiguous fragments from the
  fetched page prose or code comments (re-verified against the raw HTML this
  session); no splicing across non-adjacent sentences. The two-sentence
  Claim 3 and Claim 4 quotes are adjacent sentences copied in order. Table cells
  are quoted as single cells. Claim 8 has no source quote because it is the
  Miner's synthesis; the cue is given in `Our assessment`.
- Cross-reference verification (MINER §4b) re-read the cited claims before
  writing: `docs-litellm-anthropic-count-tokens.md` (Claims 2, 6, 7),
  `docs-litellm-claude-code-compatibility.md` (Claim 6),
  `docs-litellm-token-usage-helpers.md` (Claim 2),
  `docs-litellm-streaming-token-usage.md` (Claim 1), and the cited passage in
  `docs-litellm-completion-message-trimming.md`. All numbered claims verified in
  full text; no claim numbers invented.
- No contradiction issue filed (MINER §4a): the #1381 relationship resolves as
  complementary slices of the same page (see Cross-References → Contradicts).
  Verified the open `contradiction`-labeled issues and `CONTRADICTIONS.md` (no
  `C-NNN` entries) cover none of this surface.
- `confidence_overall` set to `emerging`: the response contract, the
  `tokenizer_type` enum, the Bedrock fallback description, and the override
  scoping (Claims 1-7) are settled first-party documentation of the LiteLLM
  surface, but the note's ops value is the silent-degradation and monitoring
  synthesis (Claims 4, 8), none of it exercised against a live Bedrock
  deployment. Consistent with the sibling LiteLLM docs notes (#1381, #1300,
  #1286, #1444).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain for issue #1650. `miner-related-notes.md` was read for
  candidates and left uncommitted.
