---
source_url: https://docs.litellm.ai/docs/adding_provider/generic_guardrail_api
source_type: docs
title: "[BETA] Generic Guardrail API — Integrate Without a PR (LiteLLM Docs)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; BETA as of 2026-09-17)
date_extracted: 2026-09-17
last_checked: 2026-09-17
status: current
confidence_overall: emerging
issue: "#1359"
---

# [BETA] Generic Guardrail API (LiteLLM Docs)

> LiteLLM's Generic Guardrail API is a PR-less integration contract for
> third-party guardrail providers — a `POST /beta/litellm_basic_guardrail_api`
> webhook with a three-verdict response (`BLOCKED` / `NONE` /
> `GUARDRAIL_INTERVENED`) — whose operationally load-bearing part is the
> error-handling section: a two-knob fail-open/fail-closed spectrum
> (`unreachable_fallback` narrow, `fail_on_error` broad, both defaulting to
> closed), critical-level logging of every fail-open bypass so a silently
> suspended security control stays alertable and auditable, a request-breaking
> 500-on-contract-mismatch failure mode on `/v1/responses`, an allowlist-based
> header egress protocol, and the first concrete gateway-side mechanism for
> tool-call authorization in the corpus.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, BETA
  page under "Guardrails > Contributing to Guardrails" in the docs nav).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented surface* — config keys, endpoint list,
  request/response schema, default values, the documented error-handling
  semantics. The page is explicitly BETA ("We're actively improving it based on
  feedback") and carries no measured data: no latency, throughput, or
  false-positive figures anywhere, and the one worked vendor example (Pillar
  Security) is a config shape, not validated efficacy. Everything here stays at
  "the gateway documents this contract," never "this holds at scale."
- **Scope**: Inbound-side request/response contract for the generic guardrail
  webhook. Covers the endpoint list, the verdict and rewrite contract, the
  `tools` / `tool_calls` / `structured_messages` parameters, the
  `request_data` / `request_headers` payload minimization, the
  `unreachable_fallback` / `fail_on_error` error-handling spectrum, static vs
  dynamic headers, config for `guardrail: generic_guardrail_api`, the Pillar
  Security example, client-side usage, and the reference implementation. Does
  **not** cover other guardrail mechanisms (content filters, load balancing,
  other provider integrations), or anything outside this contract.
- **Artifacts followed**: The linked reference implementation
  (`mock_bedrock_guardrail_server.py` in the LiteLLM GitHub cookbook) is named
  as the only runnable artifact; the FastAPI example on-page is illustrative.
  The page is self-contained; no external sub-pages were needed.

## Extracted Claims

### Claim 1: LiteLLM offers a PR-less guardrail integration contract — a provider implements `POST /beta/litellm_basic_guardrail_api` and attaches it under `litellm_settings.guardrails` with `guardrail: generic_guardrail_api`, avoiding PR review/merge and provider-specific code in LiteLLM's codebase
- **Evidence**: The "The Problem" list (making a PR, waiting for review/merge,
  maintaining provider-specific code, updating the integration for API changes)
  versus "The Solution" paragraph and the config block under "LiteLLM
  Configuration".
- **Confidence**: settled (documented contract mechanics)
- **Quote**: "The **Generic Guardrail API** lets you integrate with LiteLLM **instantly** by implementing a simple API endpoint. No PR required."
- **Our assessment**: This is the boundary contract for the corpus's first
  guardrail-as-deployed-component coverage: the guardrail runs *outside* the
  proxy as a network dependency of it. Everything else on this page is the
  consequence of that architectural fact — because the guardrail is a separate
  service, its unreachability and malformed responses become gateway
  availability events, not just security events (Claims 8-9).

### Claim 2: The generic guardrail API intercepts an explicitly enumerated surface of the model path — `/v1/chat/completions`, `/v1/completions`, `/v1/responses`, `/v1/images/generations`, `/v1/audio/transcriptions`, `/v1/audio/speech`, `/v1/messages`, `/v1/rerank`, plus pass-through endpoints — so one guardrail config spans chat, image, audio, and rerank traffic
- **Evidence**: The "Supported Endpoints" bullet list (the page's own answer to
  what one generic guardrail config covers).
- **Confidence**: settled (explicit documented list)
- **Quote**: "- `/v1/chat/completions` - OpenAI Chat Completions" (contiguous list: "- `/v1/messages` - Anthropic Messages" / "- `/v1/rerank` - Cohere Rerank" / "- Pass-through endpoints")
- **Our assessment**: Usable as a coverage map: a guardrail operator's blast
  radius is one config across chat, completion, responses, image, audio, and
  rerank classes. The carve-outs (Claim 5: tool forwarding only on
  chat/responses/messages) mean the *interception* is broad but the
  *enforcement surface* is narrower — see Claim 5 and the Universal-Support
  tension recorded there.

### Claim 3: The webhook returns one of three verdicts — `BLOCKED` (LiteLLM raises an error and blocks the request), `NONE` (request proceeds unchanged), or `GUARDRAIL_INTERVENED` (request proceeds with modified texts/images) — so a guardrail decision is a body substitute, not just a pass/fail flag
- **Evidence**: The response-format schema (`action`, `blocked_reason`, optional
  `texts`/`images`/`structured_messages`) and the "Actions:" block.
- **Confidence**: settled (documented contract)
- **Quote**: "`BLOCKED` - LiteLLM raises error and blocks request" / "`NONE` - Request proceeds unchanged" / "`GUARDRAIL_INTERVENED` - Request proceeds with modified texts/images (provide `texts` and/or `images` fields)"
- **Our assessment**: The three-action model makes the guardrail a body
  transformer as well as a gate — the same hook both blocks and rewrites. That
  is a larger contract surface than a simple allow/deny flag and explains why
  the rewrite-contract failure mode exists (Claim 4): a guardrail that can edit
  traffic can also corrupt it, and LiteLLM chooses to fail the request rather
  than pass it through unrewritten. The `blocked_reason` (required when
  `action=BLOCKED`) is also the only failure detail the caller gets — it must
  be assumed to contain whatever the third-party guardrail decides to echo.

### Claim 4: The rewrite contract is strict — on `/v1/responses` a `texts` array that counts one entry per message does not match what LiteLLM extracted, so the request is rejected with a 500 naming the guardrail rather than sent unrewritten; per-message rewrites instead go through `structured_messages`, one row per received row in order, where an echoed-unchanged row counts as unchanged, an all-unchanged response makes LiteLLM apply `texts`, and a length-mismatched array replaces the conversation as a whole
- **Evidence**: The "Rewriting per message" paragraph and the "Returning
  rewritten messages" section, both under the response-format contract, plus
  the longer `structured_messages` availability note.
- **Confidence**: settled (explicit documented behavior with a named error
  surface and two distinct rewrite paths)
- **Quote**: "On `/v1/responses` a `texts` array that counts one entry per message does not match what LiteLLM extracted, so the request is rejected with a 500 naming the guardrail rather than sent unrewritten"
- **Quote**: "A returned array whose length differs from the one you received replaces the conversation as a whole"
- **Our assessment**: A request-breaking failure mode introduced by a
  third-party service, surfacing to the user as a gateway 500 that only names
  the guardrail — and the received request was never scanned (fail-closed by
  contract, but not by content review). In Ch05 terms this is an availability
  dependency exactly like a flaky upstream: the guardrail is a network service
  in the request path, so its response should be monitored like any upstream
  (error rate by endpoint), and the `texts`-vs-`structured_messages` sidedness
  contract is what a pre-deployment conformance test must lock (echo-through vs
  length-change each have defined, different semantics — a mismatch silently
  re-scopes the conversation or errors the request).

### Claim 5: Tool-aware guardrails are the concrete gateway-side enforcement surface for function-calling authorization — `tools` (definitions/schemas) and `tool_calls` (invocations with arguments) are both forwarded, on request and response scans, with documented use cases for per-user/team tool permission policies, argument validation/redaction, and dangerous-parameter blocking; but tool forwarding is limited to `/v1/chat/completions`, `/v1/responses`, and `/v1/messages`, so tool-level enforcement is *not* universal despite the page's "Universal Support" key-benefit claim
- **Evidence**: The `tools Parameter` and `tool_calls Parameter` sections
  (formats, availability, use-case lists), the "Key Benefits" item 2
  ("Universal Support - Works across ALL LiteLLM endpoints"), and the
  supported-endpoints carve-outs on both parameters.
- **Confidence**: emerging (documented surface; the Universal-Support tension is
  the Miner's reading of two statements on the page)
- **Quote**: "**`tools`** = Tool definitions/schemas (what tools are *available*)" / "**`tool_calls`** = Tool invocations/executions (what tools are *being called* with what arguments)"
- **Quote**: "Enforce tool permission policies (e.g., only allow certain users/teams to access specific tools)" / "Block tool calls with dangerous parameters"
- **Quote**: "**Supported endpoints:** The `tools` parameter is supported on: `/v1/chat/completions`, `/v1/responses`, and `/v1/messages`. Other endpoints do not have tool support."
- **Our assessment**: This is the mechanism behind the guide's
  `### Function-calling authorization` section (Ch06), which currently names
  `rbac`/`bfla`/`bola` probes and tool-permission model checks but no runtime
  enforcement point: a guardrail with `tool_calls` visibility can block
  path-traversal arguments, apply per-team tool policies, redact PII from
  arguments, and log invocations outside the model call. The within-source
  tension — headline "**Universal Support** - Works across ALL LiteLLM
  endpoints" versus the three-endpoint tool carve-out ("Other endpoints do not
  have tool support") — is exactly the class the triage flagged: interception
  is advertised as universal while tool-level enforcement is explicitly not.
  Surfaced here rather than filed as a contradiction issue (within-source
  product-doc tension, mirroring the agent-card note's `pushNotifications`
  precedent); the Assayer should weigh it.

### Claim 6: The outbound payload is data-minimized at the boundary — `request_data` carries only identity attributes of the calling virtual key (hash, alias, user id/email, team id/alias, end-user id, org id) plus `litellm_version`, `input_type`, `litellm_call_id`, and `litellm_trace_id`, and `request_headers` is allowlist-only: listed header names show their value, all other headers render as the literal `[present]`
- **Evidence**: The Request Format schema and its inline comments for
  `request_data`, `request_headers`, `litellm_call_id` / `litellm_trace_id`.
- **Confidence**: settled (documented schema and comment text)
- **Quote**: "optional: inbound request headers (allowlist). Allowed headers show their value; all others show \"[present]\" to indicate the header existed."
- **Quote**: "\"user_api_key_hash\": \"hash of the litellm virtual key used\"" / "\"user_api_key_team_id\": \"team id associated with the litellm virtual key used\"" / "\"user_api_key_end_user_id\": \"end user id associated with the litellm virtual key used\""
- **Our assessment**: The guardrail receives identity attributes sufficient for
  per-user / per-team / per-org policy decisions without the gateway handing
  over full request headers. This is a vendor-documented minimization pattern
  at *exactly* the boundary where the corpus already records a leak
  (`failure-litellm-guardrail-logging-secret-exposure.md`): the input side
  ships a redacted view (`[present]`), which is the design mirror of that
  failure note's sanitize-before-emission lesson. The `litellm_call_id` /
  `litellm_trace_id` pair is also what makes every fail-open bypass traceable
  back to a call (Claim 9).

### Claim 7: Header egress from proxy to guardrail is allowlist-only and split into static vs dynamic — `headers` is a fixed key/value map sent with every request to the guardrail, while `extra_headers` is a list of client-request header names whose values are forwarded (plus a small default allowlist such as `x-litellm-*`); everything else is sent as `[present]`
- **Evidence**: The "Static and dynamic headers" section with both config
  examples and the forwarding rule, plus the page's note that this mirrors the
  MCP static/extra header behavior.
- **Confidence**: settled (documented config surface)
- **Quote**: "**Static headers** (`headers`): A key/value map sent with **every** request to your guardrail. Use this for fixed values (e.g. API keys, `X-Service-Name`)."
- **Quote**: "**Dynamic headers** (`extra_headers`): A list of **header names** that are forwarded from the **client request** to your guardrail. Only headers in this list (plus a small default allowlist such as `x-litellm-*`) have their values sent; others are sent as `[present]`."
- **Our assessment**: An explicit egress-minimization design decision: the
  proxy forwards *names* by default and values only by opt-in. The default
  `x-litellm-*` allowlist is the leaked-surface control — anything the union of
  operator config and that allowlist lets through is sent to a third-party
  guardrail service. This is the counterpart control to the guardrail-logging
  leak already in the corpus: it limits what the guardrail can see (egress),
  whereas the failure note is about what LiteLLM logs (its own ingestion side).

### Claim 8: Fail behavior sits on a two-knob spectrum, both defaults closed — `unreachable_fallback` (default `fail_closed`) reacts *only* to endpoint unreachability (network errors, timeouts, HTTP 502/503/504 from an upstream proxy/load balancer), while `fail_on_error` (default `true`) is the broader control governing *any* guardrail error: non-2xx, malformed/unparseable body, network failure, or internal serialization/validation error
- **Evidence**: The "Error handling: `unreachable_fallback` and `fail_on_error`"
  section, the two-setting table, and the `config.yaml` inline comments.
- **Confidence**: settled (explicit default values and scoping)
- **Quote**: "`unreachable_fallback` (default `fail_closed`) only reacts to the guardrail endpoint being **unreachable**: network errors, timeouts, or an HTTP 502/503/504 from an upstream proxy/load balancer. Set it to `fail_open` to let requests proceed in just those cases."
- **Quote**: "`fail_on_error` (default `true`) is the broader control. It governs **any** guardrail error, not only unreachability."
- **Our assessment**: The two knobs compose (unreachability is a subset of
  "any error"), and their defaults are both fail-closed. The operator lever
  that matters in practice is `fail_on_error` — it is the one that decides
  whether a guardrail outage blocks traffic. Note the important nuance the
  docs state explicitly: only a *valid parsed response* can act, so even under
  `fail_on_error: false`, a parsed `BLOCKED` still blocks (Claim 9).

### Claim 9: `fail_on_error: false` is a complete bypass, not graceful degradation — any guardrail error downgrades to a critical-level log line and the request proceeds as if the guardrail were not configured; on the response path fail-open returns the already-generated model output while fail-closed turns a successful generation into an error; and every fail-open bypass is logged at critical level (`Generic Guardrail API error (fail-open) ...`) with the call id and trace id "so you can alert on it and audit how often it happens"
- **Evidence**: The `fail_on_error` table, the danger callout, and the closing
  sentence of the "Error handling" section.
- **Confidence**: settled (documented behavior with the vendor's own warning)
- **Quote**: "**Fail open (complete).** Any guardrail error is downgraded to a critical-level log line and the request proceeds as if the guardrail were not configured"
- **Quote**: "The default is fail closed precisely because a guardrail is usually a security control. Every fail-open bypass is logged at critical level (`Generic Guardrail API error (fail-open) ...`) with the call id and trace id, so you can alert on it and audit how often it happens."
- **Quote**: "on the response path, a fail-open returns the already-generated model output, while fail-closed turns a successful generation into an error."
- **Our assessment**: The highest-value operational claim on the page. The
  detection hook for "my security control silently stopped enforcing" is a *log
  level and a message string*, not an HTTP status or a metric LiteLLM emits —
  the node from the corpus's other fail-open flavor
  (`docs-promptfoo-guardrails-assertions.md`), which is decided by a
  different signal (an *omitted* field) at a different layer (eval-time). There
  is no metric in the docs; the only countable signal is how often the critical
  log line appears. And the response-path asymmetry is a real availability
  cost of the fail-closed default: fail-open lets a generated (possibly unsafe)
  output out, fail-closed turns an already-successful generation into an error.
  An operator must choose, per guardrail, which failure it would rather burn.

### Claim 10: The vendor's own guidance anchors the fail-open/fail-closed choice in security-vs-availability tradeoffs — fail open only when "availability and operational constraints are stronger than your security constraints," and keep the default when the guardrail is "a hard security boundary"
- **Evidence**: The danger callout paragraph.
- **Confidence**: settled (explicit vendor guidance)
- **Quote**: "Enable it only if you have understood and accepted that tradeoff: choose it when your availability and operational constraints are stronger than your security constraints. If the guardrail is a hard security boundary, leave it at the default `true` (fail closed)."
- **Our assessment**: Naming the tradeoff is the actionable part: the vendor
  doesn't recommend one side, it requires the operator to classify the
  guardrail (security boundary vs. commodity check) before choosing a default.
  For the guide this belongs next to Ch05's config-change three-property test
  (config changes must be gradual, rollable, and auto-stop on loss of operator
  control) — `fail_on_error` is exactly a config knob that, flipped, silently
  disables a security control, and it cannot be validated by a canary of
  *successful* requests (a canary that never trips the guardrail won't observe
  the bypass).

### Claim 11: The contract is version-sensitive by the vendor's own framing — the page is an explicitly BETA API under active iteration, and the one worked vendor example (Pillar Security) is a config shape (modes `[pre_call, post_call]`, `default_on: true`, provider-specific params like `plr_mask`) with no efficacy or latency data on the page
- **Evidence**: The "Questions?" closing note, and the "Example: Pillar
  Security" config block with its pointer to separate Pillar Security docs.
- **Confidence**: emerging (beta status explicit; the config is a supported
  shape, its security value unmeasured here)
- **Quote**: "This is a **beta API**. We're actively improving it based on feedback."
- **Our assessment**: Two bounds on what this note supports: (1) contract
  details (endpoint list, defaults, error semantics) are current-as-of the
  2026-09-17 fetch and may drift while BETA — treat the note's claims as
  version-sensitive; (2) the Pillar Security block demonstrates the *config
  surface* (a two-mode `pre_call`+`post_call` guardrail with
  vendor-specific `additional_provider_specific_params`) but the page records
  no measurement of what any guardrail buys — no false-positive rate, no
  latency, no cost of fail-open. Recorded as a config shape, not efficacy.

## Concrete Artifacts

All artifacts verbatim from the fetched page (https://docs.litellm.ai/docs/adding_provider/generic_guardrail_api).

### Request format (from "API Contract → Request Format", verbatim code block)

```json
{
  "texts": ["extracted text from the request"],  // array of text strings
  "images": ["base64_encoded_image_data"],  // optional array of images
  "tools": [  // tool calls sent to the LLM (in the OpenAI Chat Completions spec)
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          }
        }
      }
    }
  ],
  "tool_calls": [  // tool calls received from the LLM (in the OpenAI Chat Completions spec)
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"San Francisco\"}"
      }
    }
  ],
  "structured_messages": [  // optional, full messages in OpenAI format (for chat endpoints)
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "request_data": {
    "user_api_key_hash": "hash of the litellm virtual key used",
    "user_api_key_alias": "alias of the litellm virtual key used",
    "user_api_key_user_id": "user id associated with the litellm virtual key used",
    "user_api_key_user_email": "user email associated with the litellm virtual key used",
    "user_api_key_team_id": "team id associated with the litellm virtual key used",
    "user_api_key_team_alias": "team alias associated with the litellm virtual key used",
    "user_api_key_end_user_id": "end user id associated with the litellm virtual key used",
    "user_api_key_org_id": "org id associated with the litellm virtual key used"
  },
  "request_headers": {  // optional: inbound request headers (allowlist). Allowed headers show their value; all others show "[present]" to indicate the header existed.
    "User-Agent": "OpenAI/Python 2.17.0",
    "Content-Type": "application/json",
    "X-Request-Id": "[present]"
  },
  "litellm_version": "1.x.y",  // optional: LiteLLM library version running this proxy
  "input_type": "request",  // "request" or "response"
  "litellm_call_id": "unique_call_id",  // the call id of the individual LLM call
  "litellm_trace_id": "trace_id",  // the trace id of the LLM call - useful if there are multiple LLM calls for the same conversation
  "additional_provider_specific_params": {
    // your custom params from config
  }
}
```

### Response format (from "API Contract → Response Format", verbatim code block)

```json
{
  "action": "BLOCKED" | "NONE" | "GUARDRAIL_INTERVENED",
  "blocked_reason": "why content was blocked",  // required if action=BLOCKED
  "texts": ["modified text"],  // optional array of modified text strings
  "images": ["modified_base64_image"],  // optional array of modified images
  "structured_messages": [{"role": "user", "content": "modified message"}]  // optional array of rewritten chat messages
}
```

### LiteLLM configuration (from "LiteLLM Configuration", verbatim)

```yaml
litellm_settings:
  guardrails:
    - guardrail_name: "my-guardrail"
      litellm_params:
        guardrail: generic_guardrail_api
        mode: pre_call  # or post_call, during_call
        api_base: https://your-guardrail-api.com
        api_key: os.environ/YOUR_GUARDRAIL_API_KEY  # optional
        unreachable_fallback: fail_closed  # default: fail_closed. Set to fail_open to proceed if the guardrail endpoint is unreachable (network errors, or HTTP 502/503/504 from an upstream proxy/LB).
        fail_on_error: true  # default: true (fail closed). Set to false to proceed on ANY guardrail error. See "Error handling" below before changing this.
        additional_provider_specific_params:
          # your custom parameters
          threshold: 0.8
          language: "en"
```

### Error-handling matrix (from "Error handling" table, verbatim)

```
fail_on_error
true  (default)   Fail closed. Any error blocks the request: a non-2xx response,
                  a malformed or unparseable body, a network failure, or an
                  internal serialization/validation error. This preserves
                  LiteLLM's existing behavior
false             Fail open (complete). Any guardrail error is downgraded to a
                  critical-level log line and the request proceeds as if the
                  guardrail were not configured
```

### Static and dynamic headers (from "Static and dynamic headers", verbatim config blocks)

```yaml
litellm_params:
  guardrail: generic_guardrail_api
  api_base: https://your-guardrail-api.com
  headers:
    X-Service-Name: "my-app"
    X-API-Key: "secret"
```

```yaml
litellm_params:
  guardrail: generic_guardrail_api
  api_base: https://your-guardrail-api.com
  extra_headers:
    - x-request-id
    - x-correlation-id
    - x-custom-auth
```

### Pillar Security vendor example (from "Example: Pillar Security", verbatim config block)

```yaml
guardrails:
  - guardrail_name: "pillar-security"
    litellm_params:
      guardrail: generic_guardrail_api
      mode: [pre_call, post_call]
      api_base: https://api.pillar.security/api/v1/integrations/litellm
      api_key: os.environ/PILLAR_API_KEY
      default_on: true
      additional_provider_specific_params:
        plr_mask: true      # Enable automatic masking of sensitive data
        plr_evidence: true  # Include detection evidence in response
        plr_scanners: true  # Include scanner details in response
```

### Client-side usage (from "Usage", verbatim)

```python
response = client.chat.completions.create(
    model="gpt-5.6-terra",
    messages=[{"role": "user", "content": "hello"}],
    guardrails=["my-guardrail"])
```

Or with dynamic parameters: `guardrails=[{"my-guardrail": {"extra_body": {"custom_threshold": 0.9}}}]`.

### Reference implementation

The page links `mock_bedrock_guardrail_server.py` in the LiteLLM cookbook
(https://github.com/BerriAI/litellm/blob/main/cookbook/mock_guardrail_server/mock_bedrock_guardrail_server.py)
as "a complete reference implementation"; the FastAPI example on-page is
illustrative (a `GuardrailRequest`/`GuardrailResponse` pair implementing
`POST /beta/litellm_basic_guardrail_api`).

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-langfuse-security-and-guardrails.md` — **cited**
  (Corroborates, Extends — see below). Guardrail-observability side.
- `source-notes/docs-litellm-a2a-agent-card.md` — **cited** (Extends — the
  A2A-path guardrail-attachment carve-out, see below).
- `source-notes/blog-litellm-save-claude-code-costs.md` — **cited**
  (Extends — guardrail as a non-security `pre_call` sidecar, see below).
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session cost/iteration caps; no guardrail mechanism or enforcement
  content.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors and debuggability rationale; no guardrail contract.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP
  coding-agent intake; unrelated to guardrail enforcement.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  observability/telemetry integration; no guardrail contract.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: per-agent
  declared-charge accounting on the A2A path; no guardrail contract.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization/measurement; unrelated.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum and "guardrail" only in the read/write-governance sense
  (deny world-mutating actions); no gateway guardrail contract.

Additional cross-references found by searching `source-notes/` (triage overlap
list plus ad-hoc search): `failure-litellm-guardrail-logging-secret-exposure.md`,
`docs-promptfoo-guardrails-assertions.md`, `docs-litellm-a2a-agent-gateway.md`
(all cited below); `docs-litellm-a2a-invoking-agents.md` and
`docs-litellm-streaming-token-usage.md` were checked and carry no guardrail
mechanism content beyond what the agent-gateway / agent-card notes already
record.

**Primary cross-references (verified per MINER §4b — claims re-read in the
cited notes before writing):**

- **Corroborates**:
  - `source-notes/docs-langfuse-security-and-guardrails.md` **Claim 1**
    (security architecture is two-pronged: runtime blocking guardrails +
    post-hoc observability) — this page supplies the *gateway-side* runtime
    enforcement contract for the half that note implements with `llm_guard`
    at the app layer, and its critical-level fail-open log is the concrete
    "observable security control" that note's tracing argument assumes.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 6** (only
    `message/send` and `message/stream` traverse the gateway's A2A client
    path with logging, guardrails, spend) — same documented "a guardrail
    attaches to a bounded surface" genre: that note bounds guardrail coverage
    on the A2A JSON-RPC path; this page bounds it on the `/v1/*` model path.
    Both stay at "the gateway documents where the control attaches." (Verified:
    Claim 6 heading + routing quote.)
- **Contradicts**:
  - No existing source-note claim opposes the fail-open/fail-closed semantics
    extracted here. The nearest cross-surface relation — the A2A notes attach
    guardrails only to `message/*` methods while this page's model path is
    broad — is a surface difference (A2A JSON-RPC vs `/v1/*` model endpoints),
    not an opposing claim. The within-source tension ("Universal Support"
    headline vs the three-endpoint `tools`/`tool_calls` carve-out, Claim 5)
    is surfaced in-notes following the `a2a-agent-card` `pushNotifications`
    precedent rather than filed as a contradiction issue. Verified: open
    contradiction issues #1150 / #1307 / #1322 / #1338 / #1352 and
    CONTRADICTIONS.md hold nothing covering the generic guardrail API. No
    contradiction issue filed.
- **Extends**:
  - `source-notes/docs-langfuse-security-and-guardrails.md` — that note's
    guardrail work is app-layer scanner *observability* (trace-instrumented
    checks, score validation); this page adds the gateway-side *enforcement*
    contract and its availability failure modes (fail-closed = traffic outage,
    fail-open = silent bypass + critical-level log), the half the trace /
    monitoring view assumes away.
  - `source-notes/failure-litellm-guardrail-logging-secret-exposure.md` —
    that failure note's **Lesson 2** asks for a strict guardrail return
    contract (minimal structured results, not full request dicts); this page
    is the vendor's published, versioned version of that contract, and its
    header-delivery model (allowlist + `[present]` redaction, Claims 6-7
    here) is the design mirror of that incident's unsanitized output path.
    Claim 6 flags this as an explicit cross-reference.
  - `source-notes/docs-promptfoo-guardrails-assertions.md` — the *other*
    fail-open flavor in the corpus: there a guardrails gate fails open when
    the response omits the `guardrails` field (eval-time verdict reader,
    Claim 3); here LiteLLM's request-time guardrail fails open only when the
    operator sets `fail_on_error: false`, and every bypass is logged at
    critical. Together the two give the guide both silent-bypass mechanisms:
    one from a *missing signal*, one from a *configured bypass*.
  - `source-notes/docs-litellm-a2a-agent-card.md` **Claim 9** (A2A
    `message/send` / `message/stream` may strip `guardrails` from message
    `params`) — the A2A-path control-threading caveat; for any A2A traffic,
    this page's model-path contract is not the controlling document, so the
    two must be read together to avoid asserting an A2A guardrail that the
    gateway does not carry.
  - `source-notes/blog-litellm-save-claude-code-costs.md` (via
    `blog-litellm-headroom-integration.md`) — Headroom runs as a `pre_call`
    guardrail used purely for cost optimization, a *non-security* guardrail
    with a documented fail-open design. Contrast case for Claim 10's
    classify-before-choosing guidance: the same hook and config shape serve
    security and non-security guards, and fail-open is defensible for the
    latter in ways it is not for the former.
- **Novel**: First source note in the corpus covering a **guardrail as a
  deployed enforcement component with its own availability failure mode**:
  the two-knob `unreachable_fallback` / `fail_on_error` spectrum with their
  defaults; the critical-level fail-open bypass log (call id + trace id) as
  the alertable signal; the fail-closed-defaults-kill-traffic availability
  cost plus its response-path asymmetry (fail-open returns the generation,
  fail-closed errors a successful generation); the 500-on-`/v1/responses`
  contract-mismatch failure mode; the `texts` vs `structured_messages` rewrite
  sidedness; the virtual-key-identity `request_data` and `[present]` header
  egress minimization; and the `tools` / `tool_calls` gateway-side
  function-calling enforcement surface with its three-endpoint carve-out. The
  corpus previously treated guardrails at three other layers — app-layer
  scanner observability (Langfuse), eval-time verdict reading (promptfoo), and
  an opaque control attached to A2A `message/*` (the A2A notes) — none covered
  the request-time enforcement contract or its failure semantics.

## Guide Impact

- **Chapter 06 (Security and Trust) — "Function-calling authorization"
  (`guide/06-security-and-trust.md:243`)**: Attach the enforcement mechanism the
  section currently lacks. Today it names `rbac`/`bfla`/`bola` red-team probes
  and a tool-permission checklist but no runtime control; add a gateway-side
  guardrail using `tools` + `tool_calls` (Claim 5) as the mechanism that blocks
  dangerous arguments (path traversal), enforces per-user/team tool policies,
  and logs invocations — with two honesty caveats from this page: the carve-out
  (tool forwarding only on `/v1/chat/completions`, `/v1/responses`,
  `/v1/messages`), and the fact that a 404-grade silent non-enforcement exists
  wherever "Universal Support" is read literally. Pair with `## Data
  governance for AI workloads` (`guide/06-security-and-trust.md:352`): the
  `[present]`-redacted egress and the `request_data` identity allowlist
  (Claims 6-7) are a vendor-documented minimization pattern for what a
  third-party guardrail may see, and should be cited as the input-side mirror
  of the guardrail-logging secret-exposure failure.
- **Chapter 05 (LLM Ops Reliability) — "Cost, capacity, and fallback patterns"
  and "Canary and config-change release" (`guide/05-llm-ops-reliability.md:143`
  and `:153`)**: Add the guardrail-as-availability-dependency frame. The
  fail-closed default turns any guardrail outage into a traffic outage; the
  fail-open flip (`fail_on_error: false`) is a config-change hazard that
  silently disables a security control and cannot be caught by a canary of
  successful requests (Claim 10). The `/v1/responses` 500-on-contract-mismatch
  (Claim 4) is a request-breaking failure mode introduced by a third-party
  service and must be monitored per endpoint like any upstream, with a
  pre-deployment conformance test for the `texts`-vs-`structured_messages`
  sidedness. Run the guardrail response-error rate through the chapter's SLO
  machinery: a security-control dependency has its own error budget.
- **Chapter 02 (Observability)**: Add the critical-level fail-open log line
  (`Generic Guardrail API error (fail-open) ...`, carrying call id + trace id)
  as the *only* documented signal that a security control silently stopped
  enforcing (Claim 9) — a log-level-count alert (rate of that string per
  guardrail) rather than a metric, because LiteLLM emits no independent metric
  for bypasses. Note the response-path asymmetry as an availability signal:
  fail-closed on the response hook turns a successful generation into an error,
  which should itself be alertable. The `litellm_call_id` / `litellm_trace_id`
  pair in `request_data` (Claim 6) is what links a bypass log to its call.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (https://docs.litellm.ai/docs/adding_provider/generic_guardrail_api, HTTP
  200, no paywall), then quotes and code blocks verified against that fetch.
  All `Quote` fields are contiguous verbatim strings from the page prose;
  code blocks in Concrete Artifacts are copied from the page's own fenced
  blocks (including inline comments) character-for-character. The page is
  self-contained; no sub-pages were needed (the linked `mock_bedrock_guardrail_server.py`
  reference implementation and the on-page FastAPI example are both
  illustrative-only and recorded as such). The page is explicitly BETA — treat
  all contract details as current-as-of 2026-09-17.
- Prospector triage (three concurrent runs, reconciled to the `priority:high`
  assessment) honored: extraction centers on the fail-open/fail-closed
  spectrum (Claims 8-10), the observable-bypass signal (Claim 9), the
  `/v1/responses` 500 contract (Claim 4), the tool-authorization surface
  (Claim 5), and the data-minimization/`[present]`-egress protocol
  (Claims 6-7), per its numbered items. The reconciliation comment's carve-out
  finding ("Universal Support" vs three-endpoint tool forwarding) is recorded
  as Claim 5's within-source tension.
- **Contradiction scan (MINER §4a)**: no contradiction issue filed. The
  within-source "Universal Support" vs `tools`-carve-out tension is a
  product-doc capability-advertisement mismatch, surfaced in-notes per the
  `a2a-agent-card` `pushNotifications` precedent (that note explicitly decided
  the same genre "rather than filed as a contradiction issue"); no *two live
  positions* exist. Verified against CONTRADICTIONS.md (no matching `C-NNN`
  entries) and all open `contradiction`-labeled issues
  (#1150/#1307/#1322/#1338/#1352 — none touch this page or the generic
  guardrail API). No opposing claim exists in any source note.
- **Cross-ref verification (§4b)**: before citing, re-read
  `docs-langfuse-security-and-guardrails.md` Claim 1,
  `docs-litellm-a2a-agent-gateway.md` Claim 6 (heading + routing quote),
  `docs-litellm-a2a-agent-card.md` Claim 9 (A2A `guardrails` param stripping),
  `failure-litellm-guardrail-logging-secret-exposure.md` Lesson 2,
  `docs-promptfoo-guardrails-assertions.md` Claims 3 and 12 (the config-shape
  overlaps in `blog-litellm-save-claude-code-costs.md` were confirmed from its
  Concrete Artifacts and Claim 9/Headroom pointer). No claim numbers invented;
  every `Claim N` citation resolves to a real numbered claim in the cited note.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes:
  the claims are documented vendor *contract* with explicit defaults, response
  codes, and log strings (settled-as-documented), but the page is BETA, offers
  no measured enforcement/latency/false-positive data, and the operational
  consequences in `Our assessment` (outage blast radius, alerting gaps) are the
  Miner's synthesis from that documented surface, not measurements.