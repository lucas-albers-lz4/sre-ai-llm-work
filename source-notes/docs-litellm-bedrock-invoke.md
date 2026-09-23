---
source_url: https://docs.litellm.ai/docs/bedrock_invoke
source_type: docs
title: "/invoke — LiteLLM AI Gateway Documentation (Bedrock native Invoke passthrough)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; the referenced model `us.anthropic.claude-sonnet-5` places it in the current 2026 lifecycle)
date_extracted: 2026-09-23
last_checked: 2026-09-23
status: current
confidence_overall: emerging
issue: "#1417"
---

# /invoke — LiteLLM Bedrock native Invoke passthrough (LiteLLM Docs)

> LiteLLM exposes Bedrock's native `/invoke` endpoint as a pass-through route —
> `POST /bedrock/model/<model_name>/invoke` (with `/invoke-with-response-stream`
> for streaming) — where the client speaks the native Bedrock
> Invoke/Anthropic Messages wire format directly at the proxy
> (`anthropic_version: "bedrock-2023-05-31"`) and the `model_name` path segment
> is the alias from `config.yaml`, resolved by the proxy to the configured
> Bedrock model ID and region. The page documents a four-row support matrix
> (Cost Tracking, Logging, Streaming, Load Balancing all ✅) with **no caching
> or system-message statement**, a multi-region load-balancing pattern
> (duplicate `model_name` with different `aws_region_name`)
> ("The proxy automatically distributes requests across both regions."), and a
> boto3 drop-in migration recipe (point `endpoint_url` at the proxy with dummy
> AWS credentials and the LiteLLM virtual key set as
> `AWS_BEARER_TOKEN_BEDROCK`).

## Source Context

- **Type**: docs (official vendor endpoint reference — LiteLLM AI Gateway,
  `/invoke`, one page under "Supported Endpoints" in the docs nav; plus its
  "More Info" link, the deeper [`/docs/pass_through/bedrock`](https://docs.litellm.ai/docs/pass_through/bedrock)
  "Bedrock (boto3) SDK" page, followed as the substantive sub-page per the
  extraction rubric).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented surface* — the route, the config contract,
  the support matrix, the boto3 interception pattern. The pages carry no
  measured data (no latency, no throughput, no rate-limit interaction, no
  cache-hit measurement), so every claim stays at "the vendor documents this,"
  never "this holds at scale."
- **Scope**: The native Bedrock Invoke pass-through: route shape, config
  contract, support matrix, multi-region load balancing, and the boto3
  interception (`invoke_model` against the proxy). The primary page is thin
  (a quick-start, ~1.5 KB of extractable text); the pass-through sub-page adds
  the two-mode surface split (config.yaml model endpoints vs direct passthrough
  for non-model endpoints), the client-auth swap, and the virtual-keys
  credential pattern. Does **not** cover: prompt-cache behavior or
  system-message handling (no statement anywhere on either page), Claude Code
  migration guidance, guardrails/knowledge-base/agent configuration (deferred
  to the direct-passthrough mode, not detailed here), or the unified
  `/v1/messages` translation surface (a different path, see Cross-References).
- **Roadmap note**: both pages are undated living docs; the config examples use
  `bedrock/us.anthropic.claude-sonnet-5`, placing them in the current (2026)
  model lifecycle.
- **Sibling**: issue #1416 (`docs bedrock_converse`) mines the companion page
  for the `/converse` route family from the same `/bedrock/model/{model_name}`/
  base; this note covers the `/invoke` half of that family and cross-cites it.

## Extracted Claims

### Claim 1: The native Invoke passthrough is routed as `POST /bedrock/model/<model_name>/invoke`, with `/invoke-with-response-stream` as the streaming variant — the path segment is the `model_name` alias from `config.yaml`, resolved by the proxy to the real Bedrock model ID and region, and the request body is the native Bedrock Invoke/Anthropic Messages wire format (`anthropic_version: "bedrock-2023-05-31"`)
- **Evidence**: The Quick Start's curl uses
  `http://0.0.0.0:4000/bedrock/model/my-bedrock-model/invoke` with
  `"anthropic_version": "bedrock-2023-05-31"` in the body; the Streaming
  section uses the same base with `/invoke-with-response-stream`. The
  pass-through sub-page's "Supported Bedrock Endpoints with config.yaml" table
  lists `/model/{model_name}/invoke` ("Legacy Invoke API") and
  `/model/{model_name}/invoke-with-response-stream` ("Legacy Streaming")
  hanging off the `.../bedrock` base, and states the resolution rule; its
  Overview describes the whole surface as native-format, no-translation
  passthrough.
- **Confidence**: settled (explicitly documented route shape, cross-confirmed
  on two first-party pages)
- **Quote**: "The proxy automatically resolves the `model_name` to the actual Bedrock model ID and region configured in your `config.yaml`."
- **Our assessment**: Confirms the triage's route-shape question: the `/invoke`
  routes hang off the same `/bedrock/model/{model_name}` double segment as the
  `/converse` family ([`docs-litellm-bedrock-converse`] Claim 1) — one
  consistent route scheme for every model-backed Bedrock passthrough. The wire
  format is what distinguishes Invoke from Converse here: the client sends the
  Anthropic Messages request body with the Bedrock `anthropic_version` field,
  i.e. the proxy is not translating an OpenAI-compatible format — it forwards a
  provider-native body (the sub-page bills the surface as "native format (no
  translation)").

### Claim 2: A model must be registered with `custom_llm_provider: bedrock`, `model: bedrock/<model-id>`, `aws_region_name`, and AWS credentials read from the environment in `config.yaml` before the `/invoke` route will serve it
- **Evidence**: The Quick Start's `config.yaml` block registers
  `model_name: my-bedrock-model` with `model: bedrock/us.anthropic.claude-sonnet-5`,
  `aws_region_name: us-west-2`,
  `aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID` /
  `aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY`, and
  `custom_llm_provider: bedrock`.
- **Confidence**: settled (documented config contract)
- **Quote**: (see Concrete Artifacts — config.yaml, verbatim)
- **Our assessment**: The same config genre as the sibling `/converse` note and
  the corpus's other Bedrock notes (`blog-litellm-claude-opus-4-8-day-0`
  registers `model: bedrock/anthropic.claude-opus-4-8` with `aws_region_name`).
  Real AWS credentials live on the proxy side only — the client never presents
  them (see Claim 5). The `bedrock/us.`-prefixed model string matches the
  current regional-profile convention the corpus already tracks; the operator
  must still check per model whether an inference-profile prefix is required
  (consistent with `docs-litellm-anthropic-unified-structured-output` Claim 5's
  model-string split and `blog-litellm-claude-opus-4-8-day-0` Claim 6).

### Claim 3: The page's support matrix claims Cost Tracking ✅, Logging ✅, Streaming ✅ via `/invoke-with-response-stream`, and Load Balancing ✅ on the `/invoke` route — a vendor surface claim with no per-provider parity and no caching caveat
- **Evidence**: The four-row Feature/Supported table at the top of the page. The
  pass-through sub-page qualifies Cost Tracking with "For `/invoke` and
  `/converse` endpoints" and Load Balancing with "You can load balance `/invoke`,
  `/converse` routes across multiple deployments", and marks End-user Tracking ❌
  ("Tell us if you need this").
- **Confidence**: emerging (documented vendor claim; no measurements, and the
  "✅ = surface support, not per-provider parity" caveat the corpus applies to
  every endpoint matrix holds here)
- **Quote**: "For `/invoke` and `/converse` endpoints"
- **Our assessment**: Treat all four ✅ rows as surface-support claims (the same
  reading the corpus applies to the `/v1/messages`, `/audio/transcriptions`, and
  `/converse` matrices), not independently exercised behavior. Two absences
  matter more than the ✅: the matrix has **no guardrail, 5xx/failure, or
  prompt-cache row at all**, and the sub-page's End-user Tracking ❌ means spend
  is trackable on the route but not attributable per end user — the same
  attribution boundary the sibling `/converse` note records (its Claim 4).

### Claim 4: Existing boto3 Bedrock clients move to the `/invoke` passthrough with an `endpoint_url` change only — dummy AWS credentials, `AWS_BEARER_TOKEN_BEDROCK` set to the LiteLLM proxy API key, and the same `invoke_model(modelId=...)` call with `modelId` = the LiteLLM `model_name` alias
- **Evidence**: The "Using boto3 SDK" Python block sets
  `os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'`,
  `os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'`,
  `os.environ['AWS_BEARER_TOKEN_BEDROCK'] = "sk-<your-litellm-api-key>"`, then
  builds `boto3.client(service_name='bedrock-runtime', region_name='us-west-2',
  endpoint_url='http://0.0.0.0:4000/bedrock')` and calls
  `bedrock_runtime.invoke_model(modelId='my-bedrock-model', ..., body=...)`
  with `"anthropic_version": "bedrock-2023-05-31"` in the body, reading
  `response['body']` for `content[0]['text']`.
- **Confidence**: settled (documented code recipe, cross-confirmed on the
  primary page and the sub-page's load-balanced boto3 variant)
- **Quote**: "# Set dummy AWS credentials (required by boto3, but not used by LiteLLM proxy)" / "os.environ['AWS_BEARER_TOKEN_BEDROCK'] = \"sk-<your-litellm-api-key>\"  # your litellm proxy api key" / "modelId='my-bedrock-model',  # Your model_name from config.yaml"
- **Our assessment**: This is the migration path the triage flagged for Ch06: an
  existing `invoke_model` code path survives unchanged except for
  `endpoint_url` (plus the auth env). The `modelId` the client sends is the
  proxy-local alias, not the provider model ID — the client has no idea which
  region or Bedrock model ID will execute it (that resolution is proxy-side).
  The page states **no limitation** for this interception; the sub-page
  confirms boto3 works in the load-balanced case too.

### Claim 5: Client authentication on the Bedrock passthrough replaces AWS SigV4 with a bearer token — the client's `AWS4-HMAC-SHA256` signature is swapped for `Bearer <LITELLM_VIRTUAL_KEY>`, so the LiteLLM virtual key travels in a Bedrock-shaped auth slot while the proxy holds the real AWS credentials
- **Evidence**: The sub-page's "Key Changes" table maps the SDK's SigV4 auth to
  a bearer token: the AWS endpoint host is replaced by
  `LITELLM_PROXY_BASE_URL/bedrock` and "`AWS4-HMAC-SHA256..`" is replaced by
  "`Bearer anything` (use `Bearer LITELLM_VIRTUAL_KEY` if Virtual Keys are setup on proxy)". The
  Virtual-Keys section confirms the operator can avoid giving developers raw
  AWS keys.
- **Confidence**: settled (documented auth swap)
- **Quote**: "`AWS4-HMAC-SHA256..`" / "`Bearer anything` (use `Bearer LITELLM_VIRTUAL_KEY` if Virtual Keys are setup on proxy)"
- **Our assessment**: The credential-substitution detail the triage asked to
  verify: what the boto3 client sets as `AWS_BEARER_TOKEN_BEDROCK` is not an
  AWS credential at all — it is the LiteLLM gateway key, presented in a
  Bedrock-shaped auth slot so the SDK keeps working. Real AWS keys never leave
  the proxy (they live in its environment). This is the pass-through dual of the
  gateway's normal credential model and is consistent with the corpus's gateway
  auth picture: the auth-reference note's MCP `aws_sigv4` mode is the *mirror*
  (there the *gateway* signs per-request SigV4 to a backend; here the
  client-facing SigV4 is replaced by a bearer key). The two must not be
  conflated — different sides of the gateway boundary.

### Claim 6: Multi-region load balancing for `/invoke` is achieved by registering multiple deployments with the same `model_name` but different `aws_region_name` (us-west-2 / us-east-1); the proxy distributes automatically — with the routing strategy, health-check semantics, and regional-failure behavior left undocumented
- **Evidence**: The "Load Balancing" section shows two deployments both named
  `my-bedrock-model` (`aws_region_name: us-west-2` / `aws_region_name: us-east-1`)
  and states "The proxy automatically distributes requests across both regions."
  The sub-page affirms this works across all four model routes ("This works for
  all Bedrock endpoints: `/invoke`, `/invoke-with-response-stream`, `/converse`,
  and `/converse-stream`"). Neither page states a routing strategy, cooldown,
  health-check, or what happens when one region fails.
- **Confidence**: settled for the documented config pattern; the behavior claims
  (strategy, failure semantics) are documented absences
- **Quote**: "The proxy automatically distributes requests across both regions."
- **Our assessment**: Per the Prospector's explicit Miner guidance, the
  "automatic" distribution is recorded **only** as the documented claim — the
  page does **not** document the routing strategy, health-check / cooldown
  semantics, or regional-failure behavior, so no failover property is inferred
  here. The pattern doubles as a cost lever given Bedrock `us.`/`eu.`
  inference-profile pricing (mirroring the sibling `/converse` note's Claim 7),
  and one open question applies: whether a session stays region-pinned or can
  silently migrate regions (and thus prompt-cache affinity) between turns —
  unanswered by either page.

### Claim 7: The credential-handling consequence is that developers never see raw AWS keys — the Virtual-Keys pattern covers the Bedrock passthrough, so per-tenant/developer identity rides the LiteLLM virtual key and the IAM blast radius collapses to the proxy
- **Evidence**: The sub-page's "Advanced - Use with Virtual Keys" section
  describes generating a virtual key and using it in place of AWS credentials
  on the `/bedrock/...` route.
- **Confidence**: emerging (documented pattern; no security analysis on either
  page)
- **Quote**: "Use this, to avoid giving developers the raw AWS Keys, but still letting them use AWS Bedrock endpoints."
- **Our assessment**: Consistent with the gateway's general virtual-key model
  and with the sibling `/converse` note's Ch06 reading: the operator's IAM
  footprint concentrates on the proxy, and each developer's identity is the
  virtual key. The `AWS_BEARER_TOKEN_BEDROCK` slot is the transport. Attribution
  granularity is still proxy-key-level on this route — the sub-page's End-user
  Tracking ❌ (Claim 3) means "spend by end user" needs an external correlation
  layer.

### Claim 8: The page is silent on prompt caching and system-message handling — no statement, no caching row, no system-message caveat anywhere on the primary page or the sub-page — so the operator cannot tell from these docs whether the `/invoke` passthrough is cache-safe for Claude Code-shaped traffic, and the docs give no way to verify the interaction with the translated Invoke path's prompt-cache regression
- **Evidence**: The primary page's sections are Quick Start, Streaming, Load
  Balancing, Using boto3 SDK, More Info — nothing on caching. The sub-page's
  feature matrix has no caching or system-message row. I searched both pages in
  full; the only adjacent statement is the sub-page's Overview billing the
  passthrough as "native format (no translation)".
- **Confidence**: emerging (the absence is documented; no cache behavior is
  asserted either direction)
- **Quote**: "Pass-through endpoints for Bedrock - call provider-specific endpoint, in native format (no translation)."
- **Our assessment**: This is the triage's key question and it stays an open
  *gap*, not a finding: `[failure-litellm-bedrock-invoke-prompt-cache]`
  documented a prompt-cache regression on the translated Bedrock **Invoke**
  path (`bedrock/invoke/<model>` model-string routing) and its guidance was to
  route Claude Code through Invoke. This page documents a **different** surface
  — an HTTP passthrough route speaking the native Invoke wire format — and the
  two must not be conflated. Whether this passthrough shares the translation
  logic (and thus the cache hazards, mitigated or not) is **not verifiable
  from these pages**; "no translation" is itself a vendor claim about the
  wire format, not a statement about cache-contract handling. Per MINER §2a we
  do not infer safety: the gap is recorded so the Assayer/Smith can carry the
  failure note's cache caveat alongside any citation of this route.

### Claim 9: The cost-tracking claim on the passthrough is only as good as gateway body inspection — the vendor separately documents that JSON responses are deliberately buffered for spend logging, but this page gives no usage-measurement detail (billed tokens vs body-derived usage) for the `/invoke` route
- **Evidence**: The sub-page's Cost Tracking ✅ row ("For `/invoke` and
  `/converse` endpoints") against the vendor stability post's mechanism
  statement that JSON responses "still buffer by design" so spend logging and
  guardrails can inspect the body.
- **Confidence**: emerging (the Cost Tracking ✅ is documented; the mechanism
  link is the combination of two vendor sources that do not cross-reference)
- **Quote**: "JSON responses still buffer by design, so spend logging and guardrails can inspect the body." — from `blog-litellm-july-stability-update` Claim 5 (the stability post, not this page)
- **Our assessment**: Cost Tracking ✅ on the passthrough is a *surface* claim:
  the mechanism the corpus can document is the JSON-body buffering the July
  stability post describes. This page does not state what is counted (billed
  tokens, buffered-body tokens, usage fields from the response), so an operator
  adopting the route for spend accounting gets no measurement contract here.
  Combined with Claim 8's cache silence, the cost line for cache-dependent
  traffic on this route carries the corpus's standing "read your bill and your
  cache-hit rate" caution.

### Claim 10: The `/invoke` route family is the config.yaml half of a two-mode Bedrock passthrough surface — model endpoints via config-registered `model_name` vs a "direct passthrough" claiming ALL Bedrock endpoints for non-model services (guardrails, knowledge bases, agents) — and the primary page's "More Info" points to that second mode
- **Evidence**: The primary page's "More Info" section links
  `/docs/pass_through/bedrock` for "complete documentation including Guardrails,
  Knowledge Bases, and Agents". The sub-page's Overview distinguishes
  "config.yaml (Recommended for model endpoints)" (used for `/converse`,
  `/converse-stream`, `/invoke`, `/invoke-with-response-stream`) from "Direct
  passthrough (For non-model endpoints)" (guardrails, knowledge bases, agents)
  and states the direct mode "Supports **ALL** Bedrock Endpoints (including
  streaming)".
- **Confidence**: settled for the mode split (explicit on the sub-page); the
  "ALL endpoints" sentence is a vendor assertion, not exercised here
- **Quote**: "Supports **ALL** Bedrock Endpoints (including streaming)."
- **Our assessment**: An operator migrating Bedrock traffic picks the mode by
  endpoint class: model inference through a config-registered `model_name`
  (gets routing/load balancing/cost tracking per Claims 3 and 6), non-model
  Bedrock services through the direct passthrough. This page's ownership is the
  former; the `/invoke` route inherits the config.yaml-mode benefits (routing,
  LB, cost) precisely because it is a model endpoint.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/bedrock_invoke
(the primary page) and https://docs.litellm.ai/docs/pass_through/bedrock (the
followed sub-page).

### Feature table (primary page, verbatim)

| Feature | Supported |
|---------|-----------|
| Cost Tracking | ✅ |
| Logging | ✅ |
| Streaming | ✅ via `/invoke-with-response-stream` |
| Load Balancing | ✅ |

### config.yaml (primary page, "1. Setup config.yaml", verbatim)

```yaml
model_list:
  - model_name: my-bedrock-model
    litellm_params:
      model: bedrock/us.anthropic.claude-sonnet-5
      aws_region_name: us-west-2
      aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID  # reads from environment
      aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
      custom_llm_provider: bedrock
```

### Call /invoke (primary page, "3. Call /invoke endpoint", verbatim)

```
curl -X POST 'http://0.0.0.0:4000/bedrock/model/my-bedrock-model/invoke' \
-H "Authorization: Bearer $LITELLM_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ],
    "anthropic_version": "bedrock-2023-05-31"
}'
```

### Streaming (primary page, "Streaming", verbatim)

```
curl -X POST 'http://0.0.0.0:4000/bedrock/model/my-bedrock-model/invoke-with-response-stream' \
-H "Authorization: Bearer $LITELLM_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Tell me a short story"
        }
    ],
    "anthropic_version": "bedrock-2023-05-31"
}'
```

### Multi-region load balancing (primary page, "Load Balancing", verbatim)

```yaml
model_list:
  # Deployment 1 - us-west-2
  - model_name: my-bedrock-model
    litellm_params:
      model: bedrock/us.anthropic.claude-sonnet-5
      aws_region_name: us-west-2
      aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
      aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
      custom_llm_provider: bedrock
    # Deployment 2 - us-east-1
  - model_name: my-bedrock-model
    litellm_params:
      model: bedrock/us.anthropic.claude-sonnet-5
      aws_region_name: us-east-1
      aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
      aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
      custom_llm_provider: bedrock
```

### boto3 interception (primary page, "Using boto3 SDK", verbatim)

```
import boto3
import json
import os
# Set dummy AWS credentials (required by boto3, but not used by LiteLLM proxy)
os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
os.environ['AWS_BEARER_TOKEN_BEDROCK'] = "sk-<your-litellm-api-key>"  # your litellm proxy api key
# Point boto3 to the LiteLLM proxy
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2',
    endpoint_url='http://0.0.0.0:4000/bedrock')
response = bedrock_runtime.invoke_model(
    modelId='my-bedrock-model',  # Your model_name from config.yaml
    contentType='application/json',
    accept='application/json',
    body=json.dumps({
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "Hello"}],
        "anthropic_version": "bedrock-2023-05-31"
    }))
response_body = json.loads(response['body'].read())
print(response_body['content'][0]['text'])
```

### Feature matrix, sub-page ("Feature → Supported → Notes", verbatim)

| Feature | Supported | Notes |
|---------|-----------|-------|
| Cost Tracking | ✅ | For `/invoke` and `/converse` endpoints |
| Load Balancing | ✅ | You can load balance `/invoke`, `/converse` routes across multiple deployments |
| End-user Tracking | ❌ | Tell us if you need this |
| Streaming | ✅ | Just replace `https://bedrock-runtime.{aws_region_name}.amazonaws.com` with `LITELLM_PROXY_BASE_URL/bedrock` 🚀 |

### Supported Bedrock model routes, sub-page ("Supported Bedrock Endpoints with config.yaml", verbatim)

| Endpoint | Description | Example |
|---|---|---|
| `/model/{model_name}/converse` | Converse API | `http://0.0.0.0:4000/bedrock/model/my-claude-model/converse` |
| `/model/{model_name}/converse-stream` | Streaming Converse | `http://0.0.0.0:4000/bedrock/model/my-claude-model/converse-stream` |
| `/model/{model_name}/invoke` | Legacy Invoke API | `http://0.0.0.0:4000/bedrock/model/my-claude-model/invoke` |
| `/model/{model_name}/invoke-with-response-stream` | Legacy Streaming | `http://0.0.0.0:4000/bedrock/model/my-claude-model/invoke-with-response-stream` |

### Client auth swap, sub-page ("Key Changes", verbatim)

| Original Endpoint | Replace With |
|---|---|
| `https://bedrock-runtime.{aws_region_name}.amazonaws.com` | `http://0.0.0.0:4000/bedrock` (LITELLM_PROXY_BASE_URL="http://0.0.0.0:4000") |
| `AWS4-HMAC-SHA256..` | `Bearer anything` (use `Bearer LITELLM_VIRTUAL_KEY` if Virtual Keys are setup on proxy) |

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path addressed):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch input-file
  TPM/RPM limiting and enqueued-token accounting (its Claims 1-5, 8); a
  different endpoint class, no Bedrock passthrough content.
- `source-notes/docs-litellm-audio-transcription.md` — **cited** (Corroborates,
  see below): the recurring "Feature/Supported/Notes" endpoint matrix genre and
  the "✅ = surface support" reading its Claims 5-6 establish.
- `source-notes/blog-litellm-auto-router-v2.md` — **cited** (Extends, see
  below): only Claim 7 — `session_affinity` pins a session's model to preserve
  provider-side prompt caches, the router-level context for this note's
  region-pinning open question (Claim 6). The rest of the note (routing-flavor
  collapse, LLM classifier) is not relevant.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session cost/iteration caps; unrelated to Bedrock route surfaces.
- `source-notes/docs-litellm-bedrock-converse.md` — **cited** (primary, see
  below): the sibling `/converse` route note mined for #1416 — same route
  family, same matrix genre, same boto3/auth/LB patterns.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum and write-permission governance; unrelated.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: A2A agent-card
  per-field ✅/❌ matrix; a different passthrough genre, no Bedrock content.
- `source-notes/docs-litellm-apply-guardrail-endpoint.md` — **dismissed**: the
  out-of-band `/guardrails/apply_guardrail` surface; its Bedrock rows are
  Bedrock *guardrail* wiring, not the model `/invoke` route (different surface).
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **cited**
  (Extends, see below): the reverse case — the native passthrough is the
  no-translation path, contrasted with that note's translation-hazard catalogue;
  its Extraction Notes explicitly scope out `native_passthrough` as the
  Prospector-deferred sibling.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: A2A
  flat/token per-agent cost ledger; unrelated.

Additional cross-references found by searching `source-notes/` (the triage's
overlap list plus Bedrock/thematic neighbors):
`failure-litellm-bedrock-invoke-prompt-cache.md`,
`docs-litellm-anthropic-unified.md`,
`docs-litellm-streaming-token-usage.md`,
`docs-litellm-gateway-auth-reference.md`,
`docs-litellm-anthropic-unified-structured-output.md`,
`blog-litellm-july-stability-update.md` (all cited below).

**Primary cross-references (verified per MINER §4b — claims re-read in the
cited notes before writing):**

- **Corroborates**:
  - `source-notes/docs-litellm-bedrock-converse.md` **Claims 1, 3, 5, 7** — the
    sibling page documents the identical route scheme
    (`/bedrock/model/{model_name}/...`, proxy-resolved alias), the identical
    four-row matrix (its Claim 3, with the same "End-user Tracking ❌" boundary
    on the sub-page, its Claim 4), the same boto3 interception recipe with
    `AWS_BEARER_TOKEN_BEDROCK` + dummy creds (its Claim 5), and the same
    multi-region LB-by-duplicated-`model_name` pattern (its Claim 7). Two
    first-party pages asserting the same surface is the strongest corroboration
    available in the corpus. (Verified: Claims 1/3/4/5/7 content match.)
  - `source-notes/docs-litellm-audio-transcription.md` **Claims 5-6** — the
    recurring "Feature/Supported/Notes" endpoint matrix genre, including the
    non-chat support matrix and the standing "surface support, not per-provider
    parity" reading. This page's four-row table (with its own
    "via `/invoke-with-response-stream`" scoping note) is another instance.
    (Verified: Claims 5-6 content.)
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 4** — the
    memory fix applied to the `/bedrock/*` pass-through routes, confirming the
    route family is a first-class, vendor-maintained surface; and **Claim 5**
    (JSON buffering for spend logging/guardrails) as the mechanism behind this
    note's Cost Tracking ✅ (used in Claim 9). (Verified: both claims read in
    full.)
- **Contrasts** (same genre, different shape — not a contradiction, so no issue
  filed):
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 2** — `/v1/messages`
    asserts Cost Tracking/Logging/End-user Tracking/Streaming/Fallbacks/
    Loadbalancing/Guardrails all ✅ on the *translated* unified surface; this
    `/invoke` passthrough page asserts a thinner four-row matrix on the *native,
    untranslated* Bedrock wire format (Cost Tracking qualified on the sub-page
    to "For `/invoke` and `/converse` endpoints", End-user Tracking ❌). Two
    route families (translated unified vs native passthrough), so the matrix
    differences are a contrast, not an opposition. (Verified: Claim 2's row
    list.)
  - `source-notes/docs-litellm-streaming-token-usage.md` — that note documents
    the OpenAI-compatible SSE `stream_options={"include_usage": True}` usage
    contract on `/v1/chat/completions`; this page's `/invoke-with-response-stream`
    is a native-format Bedrock streaming surface whose usage accounting is not
    documented at all. Complementary rather than opposing: one documents an
    opt-in usage chunk on the OpenAI wire, the other is a provider-native stream
    with no usage statement — the streaming-usage gap (Claim 8's sibling)
    remains. (Verified: the streaming note's Claim 1 scope.)
  - `source-notes/docs-litellm-anthropic-unified-structured-output.md` **Claim 5**
    — the `bedrock/invoke/<model>` **model-string** indirection vs the
    `bedrock/<model>` provider path. That note already owns the model-string
    split; this page documents the **HTTP passthrough route family** (`/bedrock/
    model/{model_name}/invoke`), a different layer. Per the Prospector's
    explicit instruction, the model-string split is **not re-extracted** here.
    (Verified: Claim 5's verbatim config values.)
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 2** — the MCP
    outbound `aws_sigv4` auth_type signs every outbound call with SigV4 using a
    gateway-side credential chain. That is the mirror of this page's Claim 5:
    on the Bedrock passthrough the *client-facing* SigV4 is replaced by a bearer
    key; on MCP the *gateway* performs SigV4 signing. Both are "where does SigV4
    live at the gateway boundary" — different sides, no conflict. (Verified:
    Claim 2's `aws_sigv4` row.)
- **Contradicts**: None. No existing source note claims the `/invoke` passthrough
  is cache-safe, carries no system-message constraints, supports End-user
  Tracking, or documents regional failover semantics. The tension with
  `failure-litellm-bedrock-invoke-prompt-cache.md` (Claim 8 here vs the failure
  note's Claims 1-2, 12) is a vendor-docs *gap* — this page's all-green matrix
  simply omits caching and the failure note's Invoke-path claims concern the
  translated model-string route, not this passthrough — not an opposing claim,
  per the Prospector's explicit "do not conflate the surfaces" instruction.
  Verified against the open `contradiction`-labeled issues (#1408/#1352/#1338/
  #1322/#1307/#1150) and `CONTRADICTIONS.md` (no matching `C-NNN` entries). No
  contradiction issue filed.
- **Extends**:
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` — the
    incident whose reputation this route carries. The failure note documents the
    translated Bedrock **Invoke** path (`bedrock/invoke/<model>` model-string
    routing), the prompt-cache regression it caused (Claims 1-2), and the
    Converse/Invoke system-message split (Claim 6) with the standing guidance to
    route Claude Code via `bedrock/invoke/<model>` (Claim 12). This note
    documents the *native-format HTTP passthrough* `/invoke` route as a
    **different surface** and records the caching gap (Claim 8) instead of
    asserting safety; the failure note's route-Claude-Code-via-Invoke guidance
    is not changed by anything here. (Verified: Claims 1-2, 6, 12 read in full.)
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 5** — supplies
    the spend-logging mechanism the passthrough's Cost Tracking ✅ presupposes
    (Claim 9 here).
  - `source-notes/blog-litellm-auto-router-v2.md` **Claim 7** — `session_affinity`
    pinning a session's model to preserve provider-side prompt caches is the
    general router mechanism behind this note's region-pinning open question
    (Claim 6): if the multi-region Bedrock passthrough does not pin regions, a
    session could migrate regions (and cache affinity) between turns.
    (Verified: Claim 7 read in full.)
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — the mirror
    case. That note catalogues silent drops and cache-affinity losses on the
    `/v1/messages`→Responses *translation* path, and its Extraction Notes
    explicitly scope out `native_passthrough` as a Prospector-deferred sibling.
    This page documents a native no-translation passthrough where those
    translation hazards do not apply by construction — but where the operator
    gets the provider's contract untouched, including whatever caching
    semantics the provider implements (unverifiable here, Claim 8). Together
    they delimit when to use a translated vs a native passthrough route.
    (Verified: Claim 1 and the Extraction Notes scope-out paragraph.)
- **Novel**: First source note covering the `/invoke` **HTTP passthrough route
  surface** on its own — the sibling `/converse` note (#1416) already captured
  the route *names* in its sub-page table ("Legacy Invoke API"), but the
  `/invoke`-specific surface is new here: the request body contract
  (`anthropic_version: "bedrock-2023-05-31"` at the proxy), the
  `/invoke-with-response-stream` variant, the feature matrix on the `/invoke`
  page itself, and the boto3 `invoke_model` migration recipe. Also new: the
  explicit record that the passthrough docs give **no caching statement** for
  the exact route family whose translated sibling suffered the corpus's
  highest-profile prompt-cache incident (Claim 8), and the SigV4→bearer auth
  swap stated for the invoke route (Claim 5). The `docs-litellm-bedrock-converse`
  note's own Extraction Notes predicted this note for the `/invoke` page and
  identified it as a separate, non-duplicate sibling.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — pass-through route surface
  (`guide/05-llm-ops-reliability.md:1124-1146`)**: Add the Bedrock `/invoke`
  passthrough as the second concrete instance of the pass-through genre the
  chapter already rules on (:1124-1146), alongside the sibling `/converse`.
  Specific additions: (1) the route family
  `{proxy}/bedrock/model/{model_name}/invoke`(+`/invoke-with-response-stream`)
  where the client speaks the native Bedrock Invoke wire format and the path
  segment is a proxy-local alias resolved to model+region in config
  [Claims 1-2]; (2) multi-region load balancing via duplicate `model_name` with
  different `aws_region_name`, claimed automatic but **explicitly gapped** — no
  routing strategy, health-check/cooldown, or regional-failure semantics are
  documented, so the chapter must not present this as a failover mechanism
  [Claim 6]; (3) cost tracking on the passthrough is a surface support claim
  whose mechanism is the JSON-body buffering for spend logging (Claim 3, 9), and
  the cache-cost caveat from the Invoke-path incident should travel with any
  citation of this route.
- **Chapter 05 — routing / Bedrock model enablement
  (`guide/05-llm-ops-reliability.md:304-325`)**: The regional load-balancing
  pattern joins the existing regional-pricing material (:309-325): Bedrock
  `us.`/`eu.` inference profiles carry a ~10% premium, so spreading deployments
  across regions is a cost decision as well as a distribution mechanism
  [Claim 6]. Record the region-pinning open question (does a session stay
  region-pinned, preserving prompt-cache affinity?) next to the chapter's
  existing session-affinity/cache-preservation guidance, citing
  `blog-litellm-auto-router-v2` Claim 7 as the router-level mechanism that would
  be needed for cache-preserving regional distribution on this route.
- **Chapter 05 — Claude Code on Bedrock (cache guidance)**: The chapter should
  keep the failure note's guidance ("route Claude Code via
  `bedrock/invoke/<model>`") for the translated path, and add an explicit note
  that the **native-format HTTP passthrough** `/invoke` route is a different
  surface whose cache-safety is **unverified by vendor documentation** (silent
  on prompt caching and system-message handling) [Claim 8]. Do not let a reader
  conflate "route via Invoke" with "use `/bedrock/model/<model>/invoke`".
- **Chapter 06 (Security and Trust) — credential substitution at the proxy
  boundary**: In the gateway credential material (the "declare, don't infer"
  section scope at `guide/06-security-and-trust.md:603-632` is MCP-specific;
  this is the Bedrock passthrough's separate credential shape), add the pattern:
  existing boto3 clients swap `endpoint_url` to the proxy, set dummy AWS
  credentials, and present the **LiteLLM virtual key as
  `AWS_BEARER_TOKEN_BEDROCK`** while AWS SigV4 is replaced by `Bearer <key>` —
  so the IAM blast radius collapses to the proxy and per-tenant identity rides
  the virtual key [Claims 4-5, 7]. Note per the sub-page matrix that End-user
  Tracking is ❌ on this route (Claim 3), and cross-reference the MCP
  `aws_sigv4` outbound mode (`docs-litellm-gateway-auth-reference` Claim 2) so
  the gateway's two SigV4 roles are not conflated.
- **Chapter 02 (Observability) — passthrough spend accounting**: Add the
  documented split on this route — Cost Tracking ✅ but End-user Tracking ❌
  (Claim 3) — so cost dashboards can answer total/per-key spend but not
  per-end-user attribution without an external layer; carry the Claim 9 note
  (no usage-measurement detail for the passthrough; the vendor mechanism is
  JSON-body buffering, per `blog-litellm-july-stability-update` Claim 5); and
  pair with the failure note's "cache-read tokens and spend are the only early
  signals" lesson for any cache-dependent traffic routed here (Claim 8).

## Extraction Notes

- Source read in full: the primary page (https://docs.litellm.ai/docs/bedrock_invoke,
  HTTP 200, no paywall, ~1.5 KB of body text) plus its one substantive linked
  page, the "Full Bedrock Passthrough Docs" sub-page
  (https://docs.litellm.ai/docs/pass_through/bedrock, HTTP 200), followed per
  the extraction rubric per the Prospector's "follow it only if needed to
  resolve a claim" instruction (it was needed for Claims 3, 5, 7, 9-10). No
  further sub-pages followed (the AWS API-reference and virtual-keys links are
  cited as identifiers/context only). All quotes and code artifacts copied
  character-for-character from the rendered page text; YAML blocks were
  reconstructed with standard line breaks from the rendered text.
- Triage honored: extraction leads with the route shape (Claims 1-2), the
  support matrix as a vendor claim with the verified "For `/invoke` and
  `/converse` endpoints" qualifier and the End-user ❌ boundary (Claim 3), the
  boto3 drop-in and its absent limitation (Claims 4-5), multi-region load
  balancing recorded as documented-with-gaps, not inferred failover (Claim 6),
  and the caching question recorded as an explicit gap rather than a safety
  finding (Claims 8), per the Prospector's explicit Miner guidance.
- **Contradiction scan (MINER §4a)**: no contradiction issue filed. The only
  candidate tension — this page's all-green matrix vs
  `failure-litellm-bedrock-invoke-prompt-cache.md` Claims 1-2/12 — is a
  vendor-docs gap (two different /invoke surfaces; the passthrough page simply
  omits caching), not an opposing claim, per the Prospector's explicit
  instruction. Verified against CONTRADICTIONS.md (no matching `C-NNN`) and all
  open `contradiction`-labeled issues (#1408/#1352/#1338/#1322/#1307/#1150 —
  none touch this surface).
- **Left unverified, not asserted**: whether the `/invoke` HTTP passthrough
  shares the translated Invoke path's translation/hoisting logic and thus its
  prompt-cache hazards (Claim 8 records the gap without asserting the link; the
  sub-page's "native format (no translation)" is a wire-format claim, not a
  cache-contract statement); the routing strategy / health-check / regional-
  failure behavior behind "automatically distributes" (Claim 6); whether a
  session stays region-pinned under multi-region LB (open question in Claim 6);
  and what a passthrough retry/fallback would do (undocumented).
- **Cross-ref verification (§4b)**: re-read before citing —
  `docs-litellm-bedrock-converse.md` (Claims 1, 3, 4, 5, 7),
  `failure-litellm-bedrock-invoke-prompt-cache.md` (Claims 1-2, 6, 12),
  `docs-litellm-anthropic-unified.md` (Claim 2),
  `docs-litellm-anthropic-unified-structured-output.md` (Claim 5),
  `docs-litellm-streaming-token-usage.md` (Claim 1),
  `docs-litellm-gateway-auth-reference.md` (Claim 2),
  `docs-litellm-messages-to-responses-mapping.md` (Claim 1 + Extraction Notes
  scope-out), `blog-litellm-july-stability-update.md` (Claims 4-5),
  `blog-litellm-auto-router-v2.md` (Claim 7), and
  `docs-litellm-audio-transcription.md` (Claims 5-6) — all verified in full
  text; no claim numbers invented; every `Claim N` citation resolves to a real
  numbered claim.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes
  (#1382, #1390, #1391, #1416): the extractable facts (route shape, config
  contract, boto3 recipe, auth swap, LB pattern) are settled first-party
  documentation cross-confirmed on two pages, but the page carries no measured
  data and the high-value synthesis (the caching gap, the End-user ❌
  attribution boundary, the cost-tracking mechanism) is the Miner's reading of
  that documented surface.
- `date_published` unknown (undated living docs); `date_extracted` and
  `last_checked` both 2026-09-23 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) —
  production-shaped drain for issue #1417.