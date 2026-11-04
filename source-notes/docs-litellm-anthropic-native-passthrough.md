---
source_url: https://docs.litellm.ai/docs/anthropic_unified/native_passthrough
source_type: docs
title: "Native /v1/messages Passthrough for OpenAI-Compatible Providers — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-11-04)
date_extracted: 2026-11-04
last_checked: 2026-11-04
status: current
confidence_overall: emerging
issue: "#2031"
---

# Native `/v1/messages` Passthrough for OpenAI-Compatible Providers (LiteLLM Docs)

> A per-deployment `model_info.supported_endpoints` opt-in (v1.92.0+) flips
> LiteLLM's `/v1/messages` route from translate-to-target-API into native
> Anthropic-body forwarding — and, by default, silently reduces every
> `cache_control` marker to `{"type": "ephemeral"}`, stripping a Claude Code
> client's `ttl: "1h"` down to the short default cache tier unless
> `cache_control_ttl: true` is set. The ops content is a config-gated behavior
> cliff with no documented metric, log line, or error for the downgrade.

## Source Context

- **Type**: docs (single child page of the LiteLLM `/v1/messages` reference,
  `/docs/anthropic_unified/native_passthrough`, auto-discovered from the
  `litellm-docs` site-crawl seed).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented config surface and forwarding contract
  (`model_info` field names, header precedence, URL join rule, provider split).
  It is vendor documentation of a translation/forwarding layer: the page reports
  no measured cache hit rate, latency, cost delta, or failure narrative, and no
  independent validation exists.
- **Scope**: The `/v1/messages` half of the `model_info.supported_endpoints`
  opt-in: how to enable native passthrough, what the gateway rewrites
  (`cache_control`), the forwarded header contract, URL normalization, the
  provider split table, and the response usage shape. It does **not** cover the
  `/v1/responses` opt-in (separate linked page), `/v1/chat/completions` routing,
  rate limits, spend accounting, or any observability surface for the
  `cache_control` reduction.
- **Redundancy**: `docs-litellm-anthropic-unified.md` (#1382) is the parent
  `/v1/messages` page and documents the unified/translated surface;
  `docs-litellm-messages-to-responses-mapping.md` (#1390) documents the
  translation this opt-in bypasses. This page is the **opt-out from
  translation** and is non-duplicate. `docs-litellm-adding-openai-compatible-providers.md`
  (#1639) covers `supported_endpoints` at the provider-registry JSON level, not
  this deployment-level `model_info` field.

## Extracted Claims

### Claim 1: Adding `/v1/messages` to a deployment's `model_info.supported_endpoints` opts that deployment into native Anthropic passthrough (v1.92.0+), and the `/v1/messages` and `/v1/responses` opt-ins are independent flags

- **Evidence**: The page opens by scoping itself to the `/v1/messages` half of the opt-in, states the two opt-ins are independent, and gives the exact `model_list` YAML. The version floor "Since v1.92.0" follows the opt-in paragraph.
- **Confidence**: settled (explicit vendor config contract with a worked example)
- **Quote**: "The two opt-ins are independent: list both when the server serves both" / "you can opt a deployment into forwarding the Anthropic payload untranslated" / "Add `/v1/messages` to `model_info.supported_endpoints` on the deployment:"
- **Our assessment**: This is the deployment-level switch the guide needs to name. It is not a global gateway mode and not a provider-registry setting: it is a per-deployment `model_info` field. A fleet can therefore contain two deployments of the same provider where one translates and one forwards natively — which is exactly the kind of per-route behavior divergence Ch05's "Provider parity in the shared forwarding path" section warns about, now at deployment granularity.

### Claim 2: Without the opt-in, LiteLLM translates `/v1/messages` into the target provider's API — `openai/` through the Responses API, everything else through `/v1/chat/completions` — and the translation drops `cache_control`, maps `thinking`, and approximates or loses other Anthropic-only details

- **Evidence**: The intro paragraph states the translation routing split and enumerates what translation cannot preserve.
- **Confidence**: settled (explicit vendor statement; the parameter-level consequences are separately documented in the linked mapping page)
- **Quote**: "`openai/` deployments go through the OpenAI Responses API" / "everything else goes through `/v1/chat/completions`" / "That translation only keeps what the target API can express: `cache_control` blocks are dropped, `thinking` is mapped to the provider's own reasoning parameter, and other Anthropic-only request details are approximated or lost"
- **Our assessment**: The default is lossy, not transparent. `cache_control` is dropped outright on the translated path, while the passthrough path preserves it in reduced form (Claim 3). So the cache behavior an operator gets depends on the opt-in state *and* on the provider class — a two-axis matrix, not a single "caching works" fact.

### Claim 3: By default, **every** `cache_control` in the forwarded body is reduced to `{"type": "ephemeral"}` — at the request level and inside system blocks, tools, message content blocks, and `tool_result` content — stripping Anthropic-only extensions such as `ttl`

- **Evidence**: A dedicated section states the reduction and enumerates the exact locations, with the motivating case (Claude Code sends `{"type": "ephemeral", "ttl": "1h"}` on every prompt block when 1h caching is on) and the strict-upstream rejection message (`cache_control.ttl: 1h is not supported`).
- **Confidence**: settled (explicit vendor statement of default behavior; the page gives the full location list)
- **Quote**: "So by default every `cache_control` in the forwarded body is reduced to `{"type": "ephemeral"}`, at the request level and in system blocks, tools, message content blocks, and `tool_result` content." / "clients like Claude Code send `{"type": "ephemeral", "ttl": "1h"}` on every prompt block whenever 1h prompt caching is on" / "Application data such as `tool_use.input` and tool `input_schema` is never touched"
- **Our assessment**: The highest-value claim on the page. This is a **silent 1h → short-default cache-tier downgrade** on the passthrough path: the request still succeeds and the completion is correct, but the cache write is now the cheaper, shorter-lived tier. For an agent session whose economics depend on a 1h prefix cache, the result is more cache rewrites, higher cost, and worse latency — with no error. The "application data never touched" sentence bounds the blast radius: the reduction is confined to `cache_control` markers, not tool payloads.

### Claim 4: `cache_control_ttl: true` in `model_info` preserves `ttl` on the passthrough path, but only when the upstream honors it; providers with built-in Anthropic Messages support keep forwarding `cache_control` as sent regardless

- **Evidence**: The restore snippet places `cache_control_ttl: true` alongside `supported_endpoints` in the same `model_info` block, and a following sentence scopes the behavior by provider class.
- **Confidence**: settled (explicit config field with worked example + explicit provider-class carve-out)
- **Quote**: "When the upstream honors `ttl`, keep it with `cache_control_ttl: true` in `model_info`:" / "Deployments of providers with built-in Anthropic Messages support (`anthropic/`, `bedrock/`, `vertex_ai/`, and others) keep forwarding `cache_control` as sent"
- **Our assessment**: The opt-in is **two config keys, not one** — `supported_endpoints` turns on passthrough and `cache_control_ttl` preserves the TTL. Enabling only the first gives an operator native forwarding with a downgraded cache tier. The conditional "when the upstream honors `ttl`" also means the safe setting depends on the backend's Messages-API fidelity, not just on LiteLLM: setting it against a strict implementation reintroduces the `cache_control.ttl: 1h is not supported` rejection the reduction exists to avoid.

### Claim 5: The URL join rule strips a trailing `/v1` from `api_base` before appending `/v1/messages`, so `/v1`-suffixed and bare host bases resolve to the same endpoint

- **Evidence**: The opt-in paragraph states the strip rule and gives both concrete forms resolving to the same URL.
- **Confidence**: settled (explicit, with two worked examples)
- **Quote**: "A trailing `/v1` on `api_base` is stripped first, so `https://inference.example.com/v1` and `https://inference.example.com` both resolve to `https://inference.example.com/v1/messages`."
- **Our assessment**: Small but operationally useful: a base-URL change between `/v1` and non-`/v1` form is not a routing change on this path. It also means an operator cannot use the trailing `/v1` to target a non-standard path; the gateway always reconstructs `/v1/messages`.

### Claim 6: On the forwarded request, LiteLLM adds `Authorization: Bearer <api_key>` **unless the caller already supplied `Authorization` or `x-api-key`**, defaults `anthropic-version` to `2023-06-01`, and forwards `anthropic-beta` from both the caller and the gateway

- **Evidence**: The opt-in paragraph states the header precedence, version default, and beta-header forwarding in one sentence.
- **Confidence**: settled (explicit vendor contract)
- **Quote**: "LiteLLM sends `Authorization: Bearer <api_key>` unless the request already carries an `Authorization` or `x-api-key` header, defaults `anthropic-version` to `2023-06-01`, and forwards `anthropic-beta` headers, both the ones the caller sent and the ones LiteLLM adds for features like context management."
- **Our assessment**: The security-relevant rule is the **caller-wins precedence**: a client-supplied `Authorization` or `x-api-key` suppresses the gateway's configured key for the upstream hop. An operator who assumes the gateway always injects its own credential can be wrong for exactly the clients that set the header themselves. Pair this with the gateway's normal virtual-key auth: the caller still authenticates to LiteLLM, but the credential forwarded to the backend can be the caller's, not the deployment's. The `anthropic-beta` merge is the plumbing that lets gateway-added features (e.g. context management) reach an upstream that only accepts them via beta header.

### Claim 7: The opt-in only changes behavior for providers LiteLLM would otherwise translate (`openai/`, `custom_openai/`, and other OpenAI-compatible providers); `anthropic/`, `bedrock/`, `vertex_ai/`, and similar providers already forward natively and ignore the flag

- **Evidence**: The closing paragraphs state the opt-in's applicability, the native-provider carve-out twice, and a two-row table mapping `openai/<model>` and `custom_openai/<model>` to "Native passthrough" vs "Translated via the Responses API" / "Translated via `/v1/chat/completions`".
- **Confidence**: settled (explicit + table)
- **Quote**: "The opt-in only matters for providers LiteLLM would otherwise translate, such as `openai/` and `custom_openai/` deployments." / "Providers with built-in Anthropic Messages support (`anthropic/`, `bedrock/`, `vertex_ai/`, and others) already forward natively and ignore it"
- **Our assessment**: This is the provider-class axis that prevents over-reading the feature. Turning on `supported_endpoints` for an `anthropic/` deployment is a no-op; the same field on an `openai/` deployment is a behavioral switch. An audit should therefore check the opt-in only on translation-class deployments — and should not assume that adding it anywhere changes anything.

### Claim 8: On the native path the response comes back in the provider's own Anthropic shape, including its own `usage` fields `cache_creation_input_tokens` and `cache_read_input_tokens`

- **Evidence**: The sentence immediately after the test `curl` example states the response shape and names the two cache usage fields.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "The response comes back in the provider's native Anthropic shape, including its own `usage` fields such as `cache_creation_input_tokens` and `cache_read_input_tokens`"
- **Our assessment**: This is the observability hook for Claim 3: on the passthrough path an operator can at least read native cache write/read counters to prove what tier engaged. But the page does not say these fields are normalized or exposed identically on the translated path, so a cache-hit dashboard built on them is route-dependent. It also means the cache signal is *post-hoc* — after the downgraded write has already happened — not a pre-flight warning.

### Claim 9: The page documents **no metric, log line, error, or warning** for the default `cache_control` reduction — whether the downgrade is observable at runtime is an open question

- **Evidence**: The `cache_control` section states the reduction and the restore flag but names no telemetry; the opt-in section names no warning on enablement. This is an absence across the page, not a quoted admission.
- **Confidence**: emerging (absence-of-documentation claim; the page may omit telemetry that exists in code)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The triage asked specifically whether the downgrade is observable anywhere. The page does not answer: it neither documents a warning on opt-in nor a log/metric for a stripped `ttl`. We therefore record a **documented absence of an observability contract**, not a verified silence. The operational consequence stands either way — an operator cannot rely on this page to learn that a 1h cache became ephemeral; they must inspect native `cache_creation_input_tokens` / `cache_read_input_tokens` (Claim 8) or compare cost/latency after enabling passthrough.

### Claim 10: `/v1/chat/completions` calls to the same deployment are unaffected by the opt-in either way, and streaming/response parsing on the passthrough path work as they do for a native Anthropic deployment

- **Evidence**: The sentence after the opt-in description states the no-op for chat completions and the streaming/parsing parity.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "Without the opt-in the deployment behaves as before and the request is translated. `/v1/chat/completions` calls to the same deployment are not affected either way" / "Streaming and response parsing work the same way they do for a native Anthropic deployment"
- **Our assessment**: The opt-in is route-scoped, not deployment-scoped in the broad sense. That narrows the blast radius of enabling it — chat-completions traffic is untouched — but it also means a deployment can have two different fidelity contracts at once, one per endpoint, which is easy to miss in a deployment-level config review.

## Concrete Artifacts

**Deployment opt-in (verbatim from source, "Opt in with `supported_endpoints`"):**
```yaml
model_list:
  - model_name: my-open-model
    litellm_params:
      model: openai/some-open-model
      api_base: https://inference.example.com/v1
      api_key: os.environ/EXAMPLE_API_KEY
    model_info:
      supported_endpoints: ["/v1/chat/completions", "/v1/messages"]
```

**Preserving `ttl` (verbatim, "`cache_control` is reduced to its portable core"):**
```yaml
model_list:
  - model_name: my-open-model
    litellm_params:
      model: openai/some-open-model
      api_base: https://inference.example.com/v1
      api_key: os.environ/EXAMPLE_API_KEY
    model_info:
      supported_endpoints: ["/v1/chat/completions", "/v1/messages"]
      cache_control_ttl: true
```

**Test request (verbatim from source):**
```bash
curl http://0.0.0.0:4000/v1/messages \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "content-type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "my-open-model",
    "max_tokens": 64,
    "system": [{"type": "text", "text": "You are concise", "cache_control": {"type": "ephemeral"}}],
    "messages": [{"role": "user", "content": "Say hi in three words"}]
  }'
```

**Provider split (verbatim table rows from source):**

| Deployment `model` | `/v1/messages` with the opt-in | `/v1/messages` without it |
|---|---|---|
| `openai/<model>` | Native passthrough | Translated via the Responses API |
| `custom_openai/<model>` and other OpenAI-compatible providers without built-in Anthropic Messages support | Native passthrough | Translated via `/v1/chat/completions` |

## Cross-References

- **Corroborates**: `docs-litellm-completion-prompt-caching.md` Claim 1 — the
  "silently skipped with no error" thesis; this page adds a second,
  gateway-side way to get a success-shaped cache miss (a `ttl` stripped rather
  than a prompt below minimum). Claim 6 of that note documents the 5 min / 1
  hour TTL options this page's `cache_control_ttl` gate is choosing between.
- **Extends**: `docs-litellm-anthropic-unified.md` Claim 1 (the `/v1/messages`
  unified endpoint and its cross-provider fan-out) and Claim 9 (the response
  `usage` cache fields); this page documents the per-deployment opt-out from
  the translation that overview describes.
- **Extends**: `docs-litellm-messages-to-responses-mapping.md` Claim 1 — the
  translated `openai/` path silently drops `stop_sequences` and `top_k`; this
  page is the opt-in that bypasses that translation entirely.
- **Extends**: `docs-litellm-claude-code-context-management.md` Claim 1 — the
  routing split between native pass-through and in-gateway polyfill; the
  gateway-added `anthropic-beta` header this page forwards is the mechanism by
  which features like context management reach the upstream.
- **Distinguishes (not a duplicate)**: `docs-litellm-adding-openai-compatible-providers.md`
  Claim 6 — `supported_endpoints` at the `openai_like/providers.json` registry
  level defaults to `[]` and gates `/v1/responses`; this page's field is
  `model_info.supported_endpoints` on a deployment and gates `/v1/messages`.
  Same field name, different config layer.
- **Extends**: `docs-litellm-generate-content.md` Claim 1 — the sibling
  "native passthrough vs gateway translation" pattern on the Google
  `generateContent` route; that page documents native-field forwarding, this
  one documents the Anthropic-body equivalent.
- **Extends**: `docs-litellm-gateway-auth-reference.md` Claim 1 — `x-api-key`
  is a recognized vendor auth alias on the gateway surface; this page adds the
  outbound precedence rule (caller `Authorization`/`x-api-key` suppresses the
  gateway's bearer token) for forwarded `/v1/messages` requests. Different
  surface (inbound MCP vs outbound Messages), so cite the header family only.
- **Contradicts**: None found. `docs-litellm-anthropic-unified.md` and
  `docs-litellm-completion-prompt-caching.md` do not claim that `cache_control`
  or `ttl` is preserved verbatim on the translated path, so the default
  reduction here is new coverage rather than a contradiction. No contradiction
  issue filed.
- **Novel**: First corpus coverage of `cache_control_ttl`, the deployment-level
  `model_info.supported_endpoints` passthrough opt-in, the forward-auth
  precedence rule, and the native-path `usage` fields.

## Guide Impact

- **Chapter 05 — "Provider parity in the shared forwarding path" (~L343)**:
  add that LiteLLM's `/v1/messages` fidelity is **per-deployment**, not
  per-provider: `model_info.supported_endpoints` flips a translation-class
  deployment (`openai/`, `custom_openai/`) from lossy translation into native
  forwarding, while native providers ignore it. A parity check must include the
  opt-in state, not just the provider name.
- **Chapter 05 — prompt-cache / session-affinity material (~L1056)**: add the
  config-gated cache-tier cliff: passthrough defaults to reducing every
  `cache_control` to `{"type": "ephemeral"}`, so a Claude Code 1h prefix cache
  becomes the short default tier unless `cache_control_ttl: true` is set — a
  cost/latency regression with no documented error. Recommend verifying native
  `cache_creation_input_tokens` / `cache_read_input_tokens` after enabling
  passthrough.
- **Chapter 06 — header/egress boundary (~L550)**: add the forwarded-auth
  precedence rule. The gateway sends `Authorization: Bearer <api_key>` only
  when the caller has not supplied `Authorization` or `x-api-key`, so a client
  that sets either header controls the credential the backend sees. Treat
  caller-supplied auth headers on `/v1/messages` as a credential-routing
  decision, not an implementation detail; `anthropic-beta` is merged from both
  caller and gateway.
- **Chapter 02 — usage/token accounting**: note that on the native passthrough
  path the `usage` object is the provider's Anthropic shape
  (`cache_creation_input_tokens`, `cache_read_input_tokens`), and that cache
  accounting is therefore route-dependent. A cache-hit dashboard must know
  which route produced the response.

## Extraction Notes

- Read the full page plus the linked parent `/v1/messages` and
  `/v1/responses` references only at the level needed to scope this page; the
  `/v1/responses` child page was not mined (out of scope, separate issue).
- **Candidate-list reconciliation** (`miner-related-notes.md`, all 10 paths):
  1. `docs-litellm-completion-web-search.md` — dismissed; web-search support
     matrix, no passthrough/cache overlap.
  2. `docs-litellm-batches-api.md` — dismissed; batch rate limiting, unrelated.
  3. `docs-litellm-generate-content.md` — **cited** (Extends) as the sibling
     native-passthrough pattern on a different route.
  4. `docs-litellm-bedrock-invoke.md` — dismissed; Bedrock `/invoke` route and
     SigV4→bearer swap, not the `/v1/messages` opt-in.
  5. `docs-litellm-files-endpoints.md` — dismissed; provider `/files` surface.
  6. `docs-litellm-interactions.md` — dismissed; Interactions endpoint bridge.
  7. `docs-litellm-evals-api.md` — dismissed; Evaluations API surface.
  8. `docs-litellm-completion-web-fetch.md` — dismissed; Anthropic web-fetch
     tool, unrelated to forwarding.
  9. `docs-litellm-enterprise.md` — dismissed; licensing/SSO/audit tiers.
  10. `docs-litellm-anthropic-advisor-tool.md` — dismissed; advisor-tool
      usage split, different feature (though also a `usage`-accounting note).
- Contradiction scan: checked `docs-litellm-anthropic-unified.md`,
  `docs-litellm-completion-prompt-caching.md`, and
  `docs-litellm-messages-to-responses-mapping.md` per the triage. None asserts
  that `cache_control`/`ttl` is preserved on the translated path, so no
  contradiction issue was filed.
- The "silent downgrade" is recorded as a **documented absence of an
  observability contract** (Claim 9), not as a verified absence of telemetry in
  code — the page does not say whether a warning or metric exists.
