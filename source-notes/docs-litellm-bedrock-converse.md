---
source_url: https://docs.litellm.ai/docs/bedrock_converse
source_type: docs
title: "/converse — LiteLLM AI Gateway Documentation (Bedrock native Converse passthrough)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; the referenced model `us.anthropic.claude-sonnet-5` places it in the current 2026 lifecycle)
date_extracted: 2026-09-22
last_checked: 2026-09-22
status: current
confidence_overall: emerging
issue: "#1416"
---

# /converse — LiteLLM Bedrock native Converse passthrough (LiteLLM Docs)

> LiteLLM exposes Bedrock's native `/converse` endpoint as a pass-through
> route — `POST /bedrock/model/<model_name>/converse` (with `/converse-stream`
> for streaming) — where the `model_name` path segment is the alias from
> `config.yaml`, resolved by the proxy to the configured Bedrock model ID and
> region. The page documents a four-row support matrix (Cost Tracking,
> Logging, Streaming, Load Balancing all ✅) with **no caching or
> system-message statement**, a multi-region load-balancing pattern (duplicate
> `model_name` with different `aws_region_name`), and a boto3 SDK interception
> recipe (point `endpoint_url` at the proxy with dummy AWS credentials and a
> LiteLLM virtual key as `AWS_BEARER_TOKEN_BEDROCK`).

## Source Context

- **Type**: docs (official vendor endpoint reference — LiteLLM AI Gateway,
  `/converse`, one page under "Supported Endpoints" in the docs nav; plus its
  "More Info" link, the deeper [`/docs/pass_through/bedrock`](https://docs.litellm.ai/docs/pass_through/bedrock)
  "Bedrock (boto3) SDK" page, followed as the substantive sub-page per the
  extraction rubric).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented surface* — the route, the config contract,
  the support matrix, the boto3 interception pattern. The pages carry no
  measured data (no latency, no throughput, no rate-limit interaction, no
  cache-hit measurement), so every claim stays at "the vendor documents this,"
  never "this holds at scale."
- **Scope**: The native Converse pass-through: route shape, config contract,
  support matrix, multi-region load balancing, and the client-SDK interception
  (boto3 / LangChain AWS). The primary page is thin (~2 screens); the
  pass-through sub-page adds the `/invoke` family, the direct-passthrough mode
  for non-model endpoints, and the client-auth swap. Does **not** cover: Claude
  Code migration guidance, prompt-cache behavior, guardrails/knowledge-base
  configuration, or the unified `/v1/messages` translation surface (that is a
  different path, see Cross-References).
- **Roadmap note**: both pages are undated living docs; the config examples
  use `bedrock/us.anthropic.claude-sonnet-5`, placing them in the current
  (2026) model lifecycle, not pre-Dec-2025.
- **Sibling**: issue #1417 (`docs bedrock_invoke`) is the companion page for
  the `/invoke` route; triaged separately and not mined here.

## Extracted Claims

### Claim 1: The native Converse passthrough is routed as `POST /bedrock/model/<model_name>/converse`, with `/converse-stream` as the streaming variant — the path segment is the `model_name` alias from `config.yaml`, resolved by the proxy to the real Bedrock model ID and region
- **Evidence**: The Quick Start's curl uses
  `http://0.0.0.0:4000/bedrock/model/my-bedrock-model/converse` against a
  config registering `model_name: my-bedrock-model`; the Streaming section
  uses the same base with `/converse-stream`. The pass-through sub-page's
  "Supported Bedrock Endpoints with config.yaml" table lists exactly four
  model routes (`/model/{model_name}/converse`, `/converse-stream`,
  `/invoke`, `/invoke-with-response-stream`) hanging off the
  `.../bedrock` base, and states the resolution rule.
- **Confidence**: settled (explicitly documented route shape, cross-confirmed
  on two first-party pages)
- **Quote**: "The proxy automatically resolves the `model_name` to the actual Bedrock model ID and region configured in your `config.yaml`."
- **Our assessment**: Resolves the triage's route-shape question: the
  `/bedrock/model/` double segment is not a one-off — both pages use it
  consistently for every model-backed Bedrock route (the pass-through base is
  always `{proxy}/bedrock`, and model routes always hang off
  `/bedrock/model/{model_name}/...`). The `model_name` is a proxy-local alias,
  not a provider model ID, so the URL exposes no region or model — the mapping
  to `bedrock/<model-id>` + `aws_region_name` lives in config.

### Claim 2: A model must be registered with `custom_llm_provider: bedrock`, `model: bedrock/<model-id>`, `aws_region_name`, and AWS credentials in `config.yaml` before the `/converse` route will serve it
- **Evidence**: The Quick Start's `config.yaml` block registers
  `model_name: my-bedrock-model` with
  `model: bedrock/us.anthropic.claude-sonnet-5`,
  `aws_region_name: us-west-2`,
  `aws_access_key_id` / `aws_secret_access_key` read from the environment, and
  `custom_llm_provider: bedrock`.
- **Confidence**: settled (documented config contract)
- **Quote**: (see Concrete Artifacts — Config contract, verbatim YAML)
- **Our assessment**: Same config genre as the corpus's other Bedrock notes
  (`blog-litellm-claude-opus-4-8-day-0` registers
  `model: bedrock/anthropic.claude-opus-4-8` with `aws_region_name`), and it is
  the shape that keeps real AWS credentials on the proxy side only. Note the
  bare-ID model (`us.anthropic.claude-sonnet-5`) here vs the Opus 4.8 note's
  bare `anthropic.claude-opus-4-8` — consistent with that note's Claim 6 that
  not every Anthropic-on-Bedrock model requires an inference-profile prefix;
  the operator must check per model, not assume one invocation pattern.

### Claim 3: The page's support matrix claims Cost Tracking ✅, Logging ✅, Streaming ✅ via `/converse-stream`, and Load Balancing ✅ on the `/converse` route — a vendor surface claim with no caching caveat and no measured backing
- **Evidence**: The four-row Feature/Supported table at the top of the primary
  page. The pass-through sub-page qualifies Cost Tracking with "For `/invoke`
  and `/converse` endpoints" and Load Balancing with "You can load balance
  `/invoke`, `/converse` routes across multiple deployments".
- **Confidence**: emerging (documented vendor claim; no measurements, and the
  "✅ = surface support, not per-provider parity" caveat from the corpus's
  other matrix notes applies)
- **Quote**: "For `/invoke` and `/converse` endpoints"
- **Our assessment**: Treat all four ✅ rows as surface support claims (the
  same reading the corpus applies to the `/v1/messages` and
  `/audio/transcriptions` matrices), not independently exercised behavior. Two
  absences matter more than the ✅: the matrix has **no 5xx/failure, guardrail,
  or prompt-cache row at all**, and the page nowhere addresses the cache-loss
  hazard the corpus documents for Converse-routed Claude Code
  (`failure-litellm-bedrock-invoke-prompt-cache.md` Claim 12). That the
  all-green matrix carries no caching statement is vendor-docs incompleteness
  (a gap), not a contradiction.

### Claim 4: End-user Tracking is documented ❌ on the Bedrock passthrough, alongside Cost Tracking ✅ — attribution at the endpoint level is incomplete even though spend tracking is claimed
- **Evidence**: The pass-through sub-page's feature matrix: Cost Tracking ✅
  "For `/invoke` and `/converse` endpoints"; End-user Tracking ❌ with a link
  ("Tell us if you need this"); Load Balancing ✅; Streaming ✅.
- **Confidence**: settled (explicit matrix row)
- **Quote**: "Tell us if you need this"
- **Our assessment**: Cost and end-user attribution are documented as
  independent rows here, and they diverge: spend on the route is tracked, but
  per-end-user attribution is not. For Ch02-style cost dashboards this means a
  `/converse` passthrough can answer "total spend" but not "spend by user"
  without an external correlation layer — a real boundary on the route's
  accounting surface.

### Claim 5: Existing boto3 Bedrock clients move behind the proxy with an `endpoint_url` change only — `endpoint_url='http://0.0.0.0:4000/bedrock'`, a kept `region_name`, dummy AWS credentials, and the LiteLLM virtual key set as `AWS_BEARER_TOKEN_BEDROCK`
- **Evidence**: The "Using boto3 SDK" Python block sets
  `os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'`,
  `os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'`,
  `os.environ['AWS_BEARER_TOKEN_BEDROCK'] = "sk-<your-litellm-api-key>"`, then
  builds `boto3.client(service_name='bedrock-runtime', region_name='us-west-2',
  endpoint_url='http://0.0.0.0:4000/bedrock')` and calls
  `bedrock_runtime.converse(modelId='my-bedrock-model', ...)`. The sub-page
  states everything after the `/bedrock` base is a provider-specific route.
- **Confidence**: settled (documented code recipe, cross-confirmed on both
  pages)
- **Quote**: "Anything after `http://0.0.0.0:4000/bedrock` is treated as a provider-specific route, and handled accordingly."
- **Our assessment**: This is the reusable pattern the triage flagged: an
  existing Bedrock SDK caller migrates behind the gateway by changing
  `endpoint_url` (and the auth env) only — application code is otherwise
  untouched. The page states **no limitation** for this interception (e.g., it
  does not say whether non-`converse` boto3 operations like `invoke_model` work
  on the same base, though the sub-page's LangChain/boto3 examples do use
  `invoke_model` and `converse` on it, and the direct-passthrough mode claims
  ALL Bedrock endpoints). The `modelId` in the client call is the proxy alias,
  not the provider model ID.

### Claim 6: Client authentication on the passthrough replaces AWS SigV4 with a bearer token — `AWS4-HMAC-SHA256` credentials are swapped for `Bearer <LITELLM_VIRTUAL_KEY>`, so the LiteLLM virtual key stands in for IAM at the client boundary while the proxy holds the real AWS credentials
- **Evidence**: The sub-page's "Key Changes" table maps the SDK's SigV4 auth
  to a bearer token: the AWS endpoint host is replaced by
  `LITELLM_PROXY_BASE_URL/bedrock` and AWS signature auth is replaced by
  `Bearer anything` (preferably `Bearer LITELLM_VIRTUAL_KEY` when virtual keys
  are enabled). The Virtual-Keys section confirms the operator can avoid giving
  developers raw AWS keys.
- **Confidence**: settled (documented auth swap)
- **Quote**: "`Bearer anything` (use `Bearer LITELLM_VIRTUAL_KEY` if Virtual Keys are setup on proxy)"
- **Our assessment**: This is the credential-handling shape the triage
  flagged for Ch06: the client presents the LiteLLM virtual key as a bearer
  token (`AWS_BEARER_TOKEN_BEDROCK`), and its AWS keys are dummies — real AWS
  credentials never leave the proxy. It's the SDK-interception dual of the
  gateway's normal role, and it means the operator's IAM blast radius is the
  proxy, not the fleet of clients. Per-user/tenant identity still travels via
  the virtual key (see Claim 4's End-user Tracking ❌).

### Claim 7: Multi-region load balancing for `/converse` is achieved by registering multiple deployments with the same `model_name` but different `aws_region_name`; the proxy distributes automatically
- **Evidence**: The "Load Balancing" section shows two deployments both named
  `my-bedrock-model` (`aws_region_name: us-west-2` / `aws_region_name: us-east-1`)
  and states the proxy distributes automatically. The sub-page affirms this
  works across all four model routes ("This works for all Bedrock endpoints:
  `/invoke`, `/invoke-with-response-stream`, `/converse`, and
  `/converse-stream`").
- **Confidence**: settled (documented config + explicit distribution claim)
- **Quote**: "The proxy automatically distributes requests across both regions."
- **Our assessment**: Region load balancing here is *proxy-side*, driven by
  duplicate aliases — same mechanism LiteLLM uses for routing generally, but
  for Bedrock it doubles as a regional-failure split. It connects to the
  corpus's regional-pricing material: since Bedrock `us.`/`eu.` inference
  profiles carry a ~10% premium over `global.`
  ([`blog-litellm-claude-fable-5-day-0`], and choosing regions is a cost
  decision, load balancing across regions is also a cost lever. One open
  question the page does not answer: whether a client session stays
  region-pinned or can silently migrate regions (and thus cache affinity)
  between turns under this scheme.

### Claim 8: The `/converse` model routes are one half of a two-mode Bedrock passthrough surface — config.yaml-backed model endpoints vs a direct passthrough claiming ALL Bedrock endpoints (guardrails, knowledge bases, agents) — with boto3 and LangChain AWS SDK both supported
- **Evidence**: The sub-page's Overview distinguishes "config.yaml (Recommended
  for model endpoints)" (for `/converse`, `/converse-stream`, `/invoke`,
  `/invoke-with-response-stream`) from "Direct passthrough (For non-model
  endpoints)" (guardrails, knowledge bases, agents) via
  `curl "http://0.0.0.0:4000/bedrock/guardrail/..."`, and states "Supports
  **ALL** Bedrock Endpoints (including streaming)". The LangChain section
  documents `ChatBedrockConverse(model_id=..., endpoint_url=...,
  region_name=..., aws_access_key_id=API_KEY, aws_secret_access_key="bedrock")`
  — note the access key carries the *bearer* key and the secret can be any
  non-empty value.
- **Confidence**: settled (documented surface) for the endpoint split; the
  "ALL endpoints" claim is a vendor assertion, not exercised here
- **Quote**: "Supports **ALL** Bedrock Endpoints (including streaming)."
- **Our assessment**: An operator migrating Bedrock traffic should pick the
  mode by endpoint class: model inference via a config-registered `model_name`
  (gets routing/LB/cost-tracking), non-model Bedrock services (guardrails,
  knowledge bases, agents) via the direct passthrough. The LangChain access-key
  quirk (`aws_access_key_id=API_KEY` carrying the bearer key, `aws_secret_access_key`
  as any non-empty string) is the same dummy-credentials shape as Claim 5 in a
  different SDK — the pattern generalizes across both Python clients.

### Claim 9: Cost tracking on the Converse passthrough is documented as supported with no statement about cache-dependent traffic — whether spend accounting is trustworthy when Claude Code loses its cached prefix on Converse is unanswered by this page
- **Evidence**: The matrix's Cost Tracking ✅ row (primary page) and "For
  `/invoke` and `/converse` endpoints" (sub-page), against the failure-note's
  Claim 12 (Converse must still hoist mid-conversation system messages, so
  Claude Code sessions on Converse lose cached prefix per mid-conversation
  system message, and the vendor's own guidance is to route Claude Code through
  `bedrock/invoke/<model>` instead) and the spend-logging rationale in
  `blog-litellm-july-stability-update` Claim 5 (JSON responses buffer so spend
  logging can inspect the body).
- **Confidence**: emerging (the support claim is documented; the cache-cost
  interaction is the Miner's synthesis of two vendor sources that do not state
  the link)
- **Quote**: (no direct quote — the page's silence on caching is the relevant
  fact; see the cited notes for the cache-loss claims)
- **Our assessment**: This is the triage's core tension and it stays a *gap*,
  not a contradiction. The docs here advertise Cost Tracking ✅ on the
  passthrough while the failure-note says Converse-routed Claude Code still
  loses its cached prefix on every mid-conversation system message — spend
  accounting for that traffic reflects cache-miss pricing. Whether the
  passthrough shares the Converse translation path the failure note describes
  is **not verifiable from these pages**, so we do not assert the link; we
  record that the docs give the operator no way to tell, and that the corpus's
  cache-loss caveat should travel with the cost-tracking claim wherever the
  guide cites it.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/bedrock_converse
(the primary page) and https://docs.litellm.ai/docs/pass_through/bedrock (the
followed sub-page).

### Support matrix (primary page, from "Feature", verbatim)

| Feature | Supported |
|---------|-----------|
| Cost Tracking | ✅ |
| Logging | ✅ |
| Streaming | ✅ via `/converse-stream` |
| Load Balancing | ✅ |

### Feature matrix (sub-page, from "Feature → Supported → Notes", verbatim)

| Feature | Supported | Notes |
|---------|-----------|-------|
| Cost Tracking | ✅ | For `/invoke` and `/converse` endpoints |
| Load Balancing | ✅ | You can load balance `/invoke`, `/converse` routes across multiple deployments |
| End-user Tracking | ❌ | Tell us if you need this |
| Streaming | ✅ | Just replace `https://bedrock-runtime.{aws_region_name}.amazonaws.com` with `LITELLM_PROXY_BASE_URL/bedrock` 🚀 |

### Config contract (primary page, "1. Setup config.yaml", verbatim)

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

### Call /converse (primary page, "3. Call /converse endpoint", verbatim)

```
curl -X POST 'http://0.0.0.0:4000/bedrock/model/my-bedrock-model/converse' \
-H "Authorization: Bearer $LITELLM_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
    "messages": [
        {
            "role": "user",
            "content": [{"text": "Hello, how are you?"}]
        }
    ],
    "inferenceConfig": {
        "temperature": 0.5,
        "maxTokens": 100
    }}'
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
response = bedrock_runtime.converse(
    modelId='my-bedrock-model',  # Your model_name from config.yaml
    messages=[
        {
            "role": "user",
            "content": [{"text": "Hello, how are you?"}]
        }
    ],
    inferenceConfig={
        "temperature": 0.5,
        "maxTokens": 100
    })
```

### Supported Bedrock model routes (sub-page, "Supported Bedrock Endpoints with config.yaml", verbatim)

| Endpoint | Description | Example |
|---|---|---|
| `/model/{model_name}/converse` | Converse API | `http://0.0.0.0:4000/bedrock/model/my-claude-model/converse` |
| `/model/{model_name}/converse-stream` | Streaming Converse | `http://0.0.0.0:4000/bedrock/model/my-claude-model/converse-stream` |
| `/model/{model_name}/invoke` | Legacy Invoke API | `http://0.0.0.0:4000/bedrock/model/my-claude-model/invoke` |
| `/model/{model_name}/invoke-with-response-stream` | Legacy Streaming | `http://0.0.0.0:4000/bedrock/model/my-claude-model/invoke-with-response-stream` |

### Client auth swap (sub-page, "Key Changes", verbatim)

| Original Endpoint | Replace With |
|---|---|
| `https://bedrock-runtime.{aws_region_name}.amazonaws.com` | `http://0.0.0.0:4000/bedrock` (LITELLM_PROXY_BASE_URL="http://0.0.0.0:4000") |
| `AWS4-HMAC-SHA256..` | `Bearer anything` (use `Bearer LITELLM_VIRTUAL_KEY` if Virtual Keys are setup on proxy) |

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path addressed):

- `source-notes/docs-litellm-audio-transcription.md` — **cited** (Extends, see
  below): the shared endpoint feature-matrix genre and the "✅ = surface
  support" reading apply to this page's four-row matrix.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch input-file
  TPM/RPM limiting and enqueued-token reservations; a different endpoint and a
  different rate-limit surface, no Bedrock passthrough content.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: routing-flavor
  collapse, LLM classifier, session affinity; no native per-provider passthrough
  surface.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session cost/iteration caps; unrelated to Bedrock route surfaces.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum and write-permission governance; unrelated.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: A2A agent-card
  per-field ✅/❌ matrix; a different passthrough genre with no Bedrock content.
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **cited**
  (Extends, see below): the reverse case — the native passthrough is the
  no-translation path, contrasted with that note's translation-hazard catalogue.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: A2A
  flat/token per-agent cost ledger; unrelated.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP
  coding-agent intake; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  observability integration (provider vs `success_callback` paths); no Bedrock
  native-endpoint content.

Additional cross-references found by searching `source-notes/` (the triage's
overlap list plus Bedrock/thematic neighbors):
`failure-litellm-bedrock-invoke-prompt-cache.md`,
`blog-litellm-july-stability-update.md`,
`docs-litellm-anthropic-unified.md`,
`blog-litellm-claude-opus-4-8-day-0.md` (all cited below).

**Primary cross-references (verified per MINER §4b — claims re-read in the
cited notes before writing):**

- **Corroborates**:
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 6**
    — "Converse requires all system content in a top-level field; LiteLLM has
    hoisted it there since December 2024 (#7037)." This page's native-Converse
    route is exactly that Converse surface, now exposed as a first-class
    passthrough; the failure note's Converse/Invoke system-message split is the
    backdrop for why this route exists as a documented endpoint. (Verified:
    Claim 6 quote matches.)
  - `source-notes/docs-litellm-audio-transcription.md` **Claims 5–6** — the
    recurring "Feature/Supported/Notes" endpoint matrix genre. This page's
    four-row table (with its own scoping note "via `/converse-stream`") is
    another instance; consistently with that note's assessment, the ✅ rows are
    surface support, not per-provider parity, and the genuinely limiting facts
    live in the notes column and the absences. (Verified: Claims 5-6 content.)
- **Contrasts** (same genre, different shape — not a contradiction, so no issue
  filed):
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 2** — `/v1/messages`
    asserts Cost Tracking/Logging/Streaming/Fallbacks/Loadbalancing/Guardrails
    all ✅ on the *translated* unified surface; this Converse passthrough page
    asserts a thinner four-row matrix on the *native, untranslated* Bedrock
    wire format, with cost tracking qualified on the sub-page ("For `/invoke`
    and `/converse` endpoints") and End-user Tracking ❌. The two pages document
    different route families, so the matrix differences are a contrast, not a
    contradiction. (Verified: Claim 2 row list.)
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 5** — "JSON
    responses still buffer by design, so spend logging and guardrails can
    inspect the body." This passthrough page's Cost Tracking ✅ is only as good
    as that buffer: spend accounting needs body inspection, and the converse
    docs give no detail on how usage is measured (billed tokens vs buffered
    body) on the passthrough. Complementary rather than opposing — the
    stability note supplies the mechanism the passthrough docs omit. (Verified:
    Claim 5 quote.)
- **Contradicts**: None. No existing source note claims the Converse passthrough
  is cache-safe, carries no system-message constraints, or supports End-user
  Tracking. The tension with `failure-litellm-bedrock-invoke-prompt-cache.md`
  Claim 12 (Converse-routed Claude Code loses cached prefix per mid-conversation
  system message) is a vendor-docs *gap* — this page's all-green matrix simply
  omits a caching statement and the failure note's Converse claims do not
  address the passthrough route — not an opposing claim, per the Prospector's
  explicit "do not file a contradiction" instruction. Verified against the open
  `contradiction`-labeled issues (#1408/#1352/#1338/#1322/#1307/#1150) and
  `CONTRADICTIONS.md` (no related `C-NNN` entries). No contradiction issue filed.
- **Extends**:
  - `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md` — this page
    is the operator-facing counterpart to that incident: the failure note
    documents how LiteLLM's Converse vs Invoke translation affected Claude Code
    caching and pointed operators to `bedrock/invoke/<model>`; this note
    documents the native `/converse` passthrough surface the Converse side of
    that split runs on, plus the cache-cost caveat that must travel with it
    (Claim 9 here). The failure note's Claim 12 vendor guidance ("route it
    through the Invoke path") remains the operative caching rule; nothing here
    changes it.
  - `source-notes/docs-litellm-messages-to-responses-mapping.md` — the mirror
    case. That note catalogues silent drops, cache-affinity losses, and
    bucket-quantization on the `/v1/messages`→Responses *translation* path,
    and its Claim 3 notes Bedrock does not receive the derived `prompt_cache_key`.
    This page documents the native Bedrock-format passthrough where no such
    translation happens — a gateway operator who wants Bedrock's native contract
    intact (including Converse-native params, caching semantics left to the
    provider) has this route; one who wants Anthropic-format fan-out faces the
    translation hazards. Together they delimit when to use which route.
    (Verified: Claim 3's provider list includes Bedrock.)
  - `source-notes/blog-litellm-claude-opus-4-8-day-0.md` — the Bedrock config
    shape (`model: bedrock/<model-id>`, `aws_region_name`, env AWS creds) and
    its Claim 6 (bare model ID on Bedrock, no inference-profile prefix for Opus
    4.8) are exactly the genre this page's config contract instantiates; the
    two notes jointly form the corpus's Bedrock config-shape precedent. Notably,
    this page's `us.anthropic.claude-sonnet-5` carries a `us.` prefix while the
    Opus 4.8 note's model is bare — consistent with that note's "check each
    model individually" rule. (Verified: Claim 6 head + Concrete Artifacts
    Bedrock config.)
- **Novel**: First source note covering LiteLLM's native Bedrock `/converse`
  passthrough endpoint surface — nothing in `source-notes/` mentions
  `bedrock_converse`, `/bedrock/model/`, or `AWS_BEARER_TOKEN_BEDROCK` (the
  failure note discusses `bedrock_converse` the provider path, not this
  endpoint). Specifically new: the `/converse` + `/converse-stream` route
  surface and the `/bedrock/model/{model_name}/` resolution rule (Claim 1-2);
  the four-row matrix with End-user Tracking ❌ on the sub-page (Claims 3-4);
  the boto3 interception recipe and SigV4→bearer auth swap (Claims 5-6); and
  the documented cost-tracking-without-caching-caveat gap for cache-dependent
  traffic (Claim 9).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — pass-through route surface
  (`guide/05-llm-ops-reliability.md:1124-1146`)**: Add the Bedrock native
  passthrough as a concrete instance of the pass-through genre the chapter
  already rules on (memory/stream boundary at :1124-1146). Specific additions:
  (1) a documented route family
  `{proxy}/bedrock/model/{model_name}/converse`(+`/converse-stream`,
  `/invoke`, `/invoke-with-response-stream`) where the path segment is a
  proxy-local alias resolved to model+region in config [Claim 1-2]; (2) region
  load balancing via duplicate `model_name` with different `aws_region_name`,
  which doubles as a cost lever given regional inference-profile pricing
  [Claim 7]; (3) the cache-cost caveat — cost tracking is claimed ✅ on the
  passthrough (Claim 3/9), and per the existing JSON-buffer-for-spend-logging
  rule (:1130-1132) that spend line is only as good as body inspection; where
  the corpus documents Converse losing Claude Code's cached prefix
  (`failure-litellm-bedrock-invoke-prompt-cache` Claim 12), the guide should
  state that Cost Tracking ✅ on `/converse` is not a cache-safe-or-accurate
  promise for that traffic.
- **Chapter 06 (Security and Trust) — credential shape at the proxy boundary**:
  Add the `AWS_BEARER_TOKEN_BEDROCK` / dummy-AWS-credentials interception shape
  as the pass-through form of "clients hold virtual keys, the proxy holds real
  credentials" (Claims 5-6): existing SDK clients keep their code, swap
  `endpoint_url` to the proxy, and present the LiteLLM virtual key as a bearer
  token while AWS SigV4 is replaced — so the IAM blast radius collapses to the
  proxy and per-tenant identity rides the virtual key (with End-user Tracking
  documented ❌, per Claim 4).
- **Chapter 02 (Observability) — passthrough spend accounting**: Note the
  documented split on this passthrough — Cost Tracking ✅ but End-user
  Tracking ❌ (Claim 4) — so cost dashboards can answer total/"per-key" spend
  but not per-end-user attribution without an external layer; and carry the
  Claim 9 caveat (cost on cache-dependent Converse traffic lacks a caching
  qualifier) as a monitor-read-your-bill sanity check, pairing with the
  failure-note's "cache-read tokens are the only early signal" lesson.
- **Chapter 05 — routing/Bedrock model enablement**: Reinforce the existing
  per-model rule (guide/05-llm-ops-reliability.md:304-325) with this config:
  the `model` field strings differ across Bedrock models (`us.`-prefixed vs
  bare, Claim 2 here vs `blog-litellm-claude-opus-4-8-day-0` Claim 6) — the
  inference-profile/prefix question is model-specific and must be checked per
  model when registering a `/converse`-served alias.

## Extraction Notes

- Source read in full: the primary page (https://docs.litellm.ai/docs/bedrock_converse,
  HTTP 200, no paywall, ~2 screens) plus its one substantive linked page, the
  "Full Bedrock Passthrough Docs" sub-page (https://docs.litellm.ai/docs/pass_through/bedrock,
  HTTP 200), followed per the extraction rubric. Both fetched as markdown; all
  quotes and code artifacts copied character-for-character from the rendered
  page text. No further sub-pages followed (the AWS API-reference links and the
  virtual-keys section are cited as identifiers/context only).
- Triage honored: extraction leads with the route shape (Claim 1-2), the
  support matrix as a vendor claim with the verified "For `/invoke` and
  `/converse` endpoints" qualifier (Claim 3), the boto3 interception pattern
  and its absent limitation (Claim 5-6), multi-region load balancing (Claim 7),
  and the cost-tracking-vs-cache tension (Claim 4, 9). The page is thin but
  concrete; per the Prospector's "do not inflate it," no failure metrics,
  limits, or performance claims were invented or inferred from silence.
- **Contradiction scan (MINER §4a)**: no contradiction issue filed. The only
  candidate tension — this page's all-green matrix vs
  `failure-litellm-bedrock-invoke-prompt-cache.md` Claim 12's Converse cache
  loss — is a vendor-docs gap (the page simply omits caching), not an opposing
  claim, per the Prospector's explicit instruction. Verified against
  CONTRADICTIONS.md (no matching `C-NNN`) and all open `contradiction`-labeled
  issues (#1408/#1352/#1338/#1322/#1307/#1150 — none touch this surface).
- **Left unverified, not asserted**: whether the `/converse` passthrough shares
  the Converse translation/hoisting path the failure note describes (Claim 9
  records the gap without asserting the link); whether the read-model
  "resolves the `model_name`" applies to `/invoke` too (the sub-page's
  Supported-Endpoints table says yes for all four routes — claimed there as
  documented); and whether a session stays region-pinned under multi-region LB
  (recorded as an open question in Claim 7).
- **Cross-ref verification (§4b)**: re-read before citing —
  `failure-litellm-bedrock-invoke-prompt-cache.md` Claims 6 & 12,
  `blog-litellm-july-stability-update.md` Claim 5,
  `docs-litellm-anthropic-unified.md` Claim 2,
  `docs-litellm-messages-to-responses-mapping.md` Claim 3,
  `docs-litellm-audio-transcription.md` Claims 5-6, and
  `blog-litellm-claude-opus-4-8-day-0.md` Claim 6 — all verified in full text;
  no claim numbers invented; every `Claim N` citation resolves to a real
  numbered claim.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes
  (#1390, #1401, #1382): the extractable facts (route shape, config contract,
  auth swap, LB mechanism) are settled first-party documentation cross-
  confirmed on two pages, but the page carries no measured data and the
  high-value synthesis (the cache-cost gap, End-user ❌ attribution boundary,
  SDK-path generalization) is the Miner's reading of that documented surface.
- `date_published` unknown (undated living docs); `date_extracted` and
  `last_checked` both 2026-09-22 (UTC).
- Live trial #571 (OpenCode Action, Zen free `big-pickle` backend) — production-
  shaped drain. The triage's sibling #1417 (`docs bedrock_invoke`) is separate
  and not mined here.