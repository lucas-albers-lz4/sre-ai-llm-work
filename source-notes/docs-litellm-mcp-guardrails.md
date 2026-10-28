---
source_url: https://docs.litellm.ai/docs/mcp_guardrail
source_type: docs
title: "MCP Guardrails — LiteLLM Documentation (MCP tool-call and tool-description scanning)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; .md metadata last_updated 2026-10-28)
date_extracted: 2026-10-28
last_checked: 2026-10-28
status: current
confidence_overall: emerging
issue: "#1931"
---

# MCP Guardrails (LiteLLM Docs)

> LiteLLM documents three MCP-specific guardrail phases (`pre_mcp_call`,
> `during_mcp_call`, `post_mcp_call`), response-side scanning of MCP tool
> results, and a discovery-time `pre_mcp_call` scan of tool descriptions and
> input-schema descriptions that hides poisoned tools from `tools/list` and
> refuses them on `tools/call` — with important operational caveats: MCP
> sub-calls do not inherit the parent request's guardrail selection, a blocked
> tool result can arrive under HTTP 200, and an unsupported guardrail mode is
> logged and skipped while the proxy keeps starting.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP
  Guardrails" page under "MCP Gateway → Features").
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the exposed configuration keys, hook names, block/mask
  semantics, alert names, and version notes. The page documents capability, not
  measured efficacy: it gives no false-positive rates, latency figures, or
  independent verification that a given provider detects poisoned descriptions
  reliably. Claims here stay at "the gateway documents this behavior".
- **Scope**: Covers MCP guardrail modes, Presidio `pre_mcp_call` and PANW
  `post_mcp_call` configuration examples, response-side `CallToolResult`
  scanning, custom `apply_guardrail` hooks, block/mask error behavior on `/mcp`
  and `/v1/responses`, discovery-time scanning of `tools/list` descriptions and
  input schemas, the `mcp_tool_description_blocked` alert, call-time definition
  retrieval, interaction with pinned tool lists, and the supported provider
  list. Does **not** cover the full MCP permission hierarchy, per-server rate
  limits, OAuth/SigV4 transport auth, or generic guardrail-provider contracts;
  those are covered by other LiteLLM pages.
- **Artifacts followed**: The live `.md` page
  (`https://docs.litellm.ai/docs/mcp_guardrail.md`) was read in full. The
  linked `mcp_control` page was read to verify the pinning interaction and the
  existing source note's claims; `mcp_config_reference` was read to verify that
  guardrails run inside the MCP gateway/Responses execution path. `mcp_cost`
  and `mcp_tool_search` were not followed because they do not affect the
  guardrail contract extracted here.

## Extracted Claims

### Claim 1: LiteLLM positions guardrails as an in-path MCP control that can run before, during, or after an MCP call, covering both tool inputs and tool results
- **Evidence**: The opening paragraph and the "Supported MCP Guardrail Modes" list.
- **Confidence**: settled (documented purpose and mode surface)
- **Quote**: "LiteLLM supports applying guardrails to MCP tool calls to ensure security and compliance. You can configure guardrails to run before, during, or after MCP calls to validate tool inputs and tool results and block or mask sensitive information."
- **Our assessment**: This is the page's core scope statement: the guardrail is not limited to model prompt/response text, but sits on the MCP tool path itself. For an SRE/LLM-ops guide this is the boundary between "model safety" and "tool-execution safety" — tool arguments and returned tool content are separate trust boundaries.

### Claim 2: The three MCP modes have distinct timing, and `post_mcp_call` deliberately runs on the tool result before the model sees it
- **Evidence**: The mode bullet list; `post_mcp_call` is defined as running after the MCP server returns and before the model receives the result.
- **Confidence**: settled (explicit mode definition)
- **Quote**: "`post_mcp_call`: Run **after** the MCP server returns, on the **tool result**, before the model sees it. Use this mode to block or mask PII, prompt injections, or other unsafe content coming back from a tool"
- **Our assessment**: The placement is the security-relevant part. A tool result is untrusted content entering model context; scanning it after the tool executes but before the model consumes it addresses indirect prompt injection/PII from upstream tools, not just risky user input. `pre_mcp_call` is input-side validation; `during_mcp_call` is described only as "real-time monitoring and intervention", without the concrete intervention contract given for pre/post.

### Claim 3: `post_mcp_call` scans every text content block and every string value in `structuredContent`; block rejects the tool call, mask rewrites text in place, and an unrewritable masking hit becomes a block
- **Evidence**: The "Scanning MCP tool results" paragraph.
- **Confidence**: settled (explicit documented behavior)
- **Quote**: "A `post_mcp_call` guardrail receives the `CallToolResult` the MCP server returned. Every text content block and every string value inside `structuredContent` is scanned as response-side output. A block verdict rejects the tool call; a mask verdict rewrites the matching text in place. A masking hit on a `structuredContent` key or a non-string value cannot be rewritten and is treated as a block."
- **Our assessment**: This is a precise response-side contract. The safe default is notable: when the guardrail cannot rewrite a hit (a key or non-string value), it blocks rather than passing the unscanned/unsanitized value through. The limitation is equally important — the page says *string values* are scanned, so structured/non-string payload shapes are not described as content-scanned; operators should not assume arbitrary JSON tool output is semantically inspected.

### Claim 4: MCP sub-calls do not inherit the parent request's `guardrails` selection; `default_on: true` is the documented way to make the guardrail apply
- **Evidence**: The paragraph immediately after the `post_mcp_call` example.
- **Confidence**: settled (explicit configuration requirement)
- **Quote**: "MCP sub-calls do not inherit the parent request's `guardrails` selection, so set `default_on: true` on the guardrail."
- **Our assessment**: A high-value configuration footgun. A caller can explicitly select a guardrail on the parent chat/Responses request and still have MCP sub-calls bypass that selection unless the guardrail is `default_on`. The page states the remedy but does not explain whether a non-`default_on` guardrail is skipped entirely or only when the sub-call has no explicit selection; operators should treat `default_on: true` as required for MCP coverage.

### Claim 5: On `/mcp`, a blocked tool result is an MCP tool error that can arrive with HTTP 200; on `/v1/responses` the model receives a tool error and may continue, and the overall Responses request is not made HTTP 400 by the block
- **Evidence**: The block/error behavior paragraph under "Scanning MCP tool results".
- **Confidence**: settled (explicit documented status/error semantics)
- **Quote**: "On `/mcp`, a blocked result is returned as an MCP tool error (`result.isError: true`), which can arrive with HTTP 200. For `/v1/responses` MCP auto-execution, the model receives a tool error instead of the blocked content and can continue generating a response. A guardrail block does not by itself make the overall Responses request return HTTP 400."
- **Our assessment**: This is the operational weak point for monitoring. A 200 response does not prove the tool result was clean, and a blocked tool call is not necessarily a failed user request. Dashboards keyed only on HTTP status will miss MCP guardrail blocks; observability must inspect MCP result errors, guardrail logs, or the description-blocked alert. On `/v1/responses`, the model may recover by continuing after the tool error, so "request completed" also does not mean "no unsafe tool result was blocked".

### Claim 6: An unsupported guardrail mode logs an initialization error and skips that guardrail while the proxy continues to start
- **Evidence**: The custom-guardrail paragraph.
- **Confidence**: settled (explicit documented startup behavior)
- **Quote**: "An unsupported mode causes initialization to log an error and skip that guardrail while the proxy continues starting. Check the startup logs to confirm registration."
- **Our assessment**: Availability-first startup, but a security-control availability failure: a typo in `mode` can leave the proxy healthy-looking while the intended guardrail is not registered. This is not request-level fail-open, but it is silent non-enforcement unless startup logs are monitored. Registration should be a deployment/runbook check, not assumed from a successful proxy boot.

### Claim 7: A `pre_mcp_call` guardrail also runs on tool discovery: it sees each tool's description plus every description inside its input schema before the gateway serves `tools/list`
- **Evidence**: The "Scanning Tool Descriptions on Discovery" section and its endpoint coverage sentence.
- **Confidence**: settled (explicit documented scan scope)
- **Quote**: "A `pre_mcp_call` guardrail also runs on every tool an upstream server returns from `tools/list`, before the gateway serves the listing. What the guardrail sees on that pass is the tool's description plus every `description` inside its input schema. At call time, guardrails receive the arguments and the tool definition served to that caller. The scan covers `tools/list` over `/mcp` and `/{server_name}/mcp`, `GET /mcp-rest/tools/list`, and the discovery a `/v1/responses` or `/v1/chat/completions` request runs with `server_url: "litellm_proxy"`"
- **Our assessment**: This is the page's most distinctive control: guardrails are applied to tool *metadata*, not just arguments/results. The scan covers direct MCP listing, the REST listing endpoint, and LLM-driven discovery through the Responses/Chat Completions MCP path. The scope is descriptions and input-schema descriptions; other tool metadata (for example annotations or output schemas) is not named on this page, so the claim should not be generalized to "all tool metadata is scanned".

### Claim 8: A blocked tool is omitted from the listing and refused on `tools/call` even if the client already knows its name; a masked description is listed masked; the gateway emits a self-clearing `mcp_tool_description_blocked` alert
- **Evidence**: The three bullets under "Scanning Tool Descriptions on Discovery" and the follow-on log example.
- **Confidence**: settled (explicit documented enforcement and alert behavior)
- **Quote**: "- A tool whose description or input schema the guardrail blocks is left out of the listing and refused on `tools/call`, even when the client already knows its name
- A tool whose description the guardrail masks is listed with the masked text
- The gateway logs a warning and sends an `mcp_tool_description_blocked` [alert](./proxy/alerting#all-possible-alert-types) naming the hidden tools, once per distinct set of hidden tools per server; the alert clears on its own once the upstream serves a clean catalog again"
- **Our assessment**: The call-time refusal is what closes the obvious bypass (hiding a tool from `tools/list` is insufficient if a client can still call a known name). The alert lifecycle is operationally useful but deliberately deduplicated: it fires once per distinct hidden-tool set per server and self-clears only when the upstream serves a clean catalog, so it is a state alert rather than a per-call event. "Once per distinct set" also means an unchanged poisoned catalog does not keep re-alerting.

### Claim 9: When a call lacks a tool definition from the caller's listing, LiteLLM retrieves the definition with that caller's upstream credentials and applies the discovery guardrail before execution, covering clients that never listed tools and calls handled by another proxy worker
- **Evidence**: The paragraph after the blocked-tool log example.
- **Confidence**: settled (explicit documented fallback path)
- **Quote**: "When a call has no tool definition from the caller's listing, LiteLLM retrieves the definition using that caller's upstream credentials and applies the discovery guardrail before execution. This also covers clients that never called `tools/list` and calls handled by another proxy worker. A blocked tool or a definition that cannot be retrieved is refused before the upstream tool runs. Masked descriptions and pinned definitions retain the text served to the caller."
- **Our assessment**: This closes two realistic bypasses: a client that skips discovery and calls a tool name directly, and a call landing on a proxy worker that did not serve the original listing. The failure direction is safe — an unrecoverable definition is refused before the upstream tool runs — but the behavior depends on the caller's upstream credentials being sufficient to fetch the definition.

### Claim 10: Pinning a server's tool list does not replace guardrails; guardrails still scan pinned text, and the call-enforcement behavior requires a version containing a specific fix
- **Evidence**: The pinning paragraph in the discovery section, including the versioned fix link.
- **Confidence**: settled (explicit documented interaction and version gate)
- **Quote**: "To restrict calls to an admin-approved set of tools, [pin the server's tool list](./mcp_control#pin-a-servers-tool-list). Guardrails still scan the pinned text. This behavior requires a version containing [the call enforcement fix](https://github.com/BerriAI/litellm/pull/48669)."
- **Our assessment**: Pinning and guardrails are complementary controls: pinning freezes the approved catalog, while the discovery guardrail scans the text the proxy is about to serve. The version gate matters because the page attaches the call-enforcement behavior to a specific fix; an older deployment may document/behave differently. This extends `docs-litellm-mcp-control.md` Claim 9's pinning claim with the scan interaction and version dependency.

### Claim 11: Custom guardrails get a distinct discovery hook (`call_type: list_mcp_tools`) with `mcp_tool_description` / `mcp_input_schema` request data, and `apply_guardrail` receives description texts ahead of argument texts; raising blocks, rewriting masks
- **Evidence**: The final "Custom guardrails" paragraph in the discovery section.
- **Confidence**: settled (explicit documented hook contract)
- **Quote**: "Custom guardrails: on a discovery scan the hook's `call_type` is `list_mcp_tools` instead of `call_mcp_tool`, `mcp_tool_description` and `mcp_input_schema` are set in the request data, and a guardrail built on `apply_guardrail` receives the description and the schema descriptions as extra `texts` entries ahead of the argument texts. Raising blocks the tool; returning rewritten texts masks it"
- **Our assessment**: Custom guardrail authors must branch on `call_type`; treating every invocation as `call_mcp_tool` will mis-handle discovery. The `texts` ordering is another contract hazard: tool/schema descriptions arrive *ahead of* argument texts, so a guardrail that assumes `texts[0]` is the user's argument can apply the wrong policy to metadata. Raising is the block signal and rewritten text is the mask signal, matching the block/mask model rather than a separate verdict enum.

### Claim 12: The page claims MCP guardrails work with all LiteLLM-supported guardrail providers, enumerating Presidio, Bedrock, Lakera, Aporia, Noma, PANW Prisma AIRS, and custom implementations, with PANW requiring a version containing a named integration fix
- **Evidence**: The "Supported Guardrail Providers" list and the PANW version note earlier on the page.
- **Confidence**: emerging (provider breadth is a vendor compatibility claim; no per-provider MCP behavior matrix or efficacy data)
- **Quote**: "MCP guardrails work with all LiteLLM-supported guardrail providers:

- **Presidio**: PII detection and masking
- **Bedrock**: AWS Bedrock guardrails
- **Lakera**: Content moderation
- **Aporia**: Custom guardrails
- **Noma**: Noma Security
- **PANW Prisma AIRS**: Prisma AIRS guardrails
- **Custom**: Your own guardrail implementations"
- **Our assessment**: The list establishes intended provider coverage but not behavioral parity. Only PANW gets an explicit version caveat ("PANW support requires a LiteLLM version containing the integration fix"); the page does not state whether each provider supports all three MCP modes, response-side rewriting, or description scanning equivalently. Treat the list as a compatibility claim to test per provider, not as evidence that any provider detects prompt injection or PII with acceptable accuracy.

## Concrete Artifacts

All artifacts are verbatim from the fetched page
(https://docs.litellm.ai/docs/mcp_guardrail.md).

### Presidio `pre_mcp_call` configuration (`config.yaml`)

```yaml
guardrails:
  - guardrail_name: "mcp-input-validation"
    litellm_params:
      guardrail: presidio  # or other supported guardrails
      mode: "pre_mcp_call" # or during_mcp_call
      pii_entities_config:
        CREDIT_CARD: "BLOCK"  # Will block requests containing credit card numbers
        EMAIL_ADDRESS: "MASK"  # Will mask email addresses
        PHONE_NUMBER: "MASK"   # Will mask phone numbers
      default_on: true
```

### PANW Prisma AIRS `post_mcp_call` configuration (`config.yaml`)

```yaml
guardrails:
  - guardrail_name: "mcp-output-scan"
    litellm_params:
      guardrail: panw_prisma_airs  # or presidio, or any guardrail that implements apply_guardrail
      mode: "post_mcp_call"
      api_key: os.environ/PANW_PRISMA_AIRS_API_KEY
      profile_name: os.environ/PANW_PRISMA_AIRS_PROFILE_NAME
      mask_response_content: true
      default_on: true
```

### Discovery-time prompt-injection filter (`config.yaml`)

```yaml
mcp_servers:
  notes:
    url: http://notes.internal/mcp
    transport: http

guardrails:
  - guardrail_name: mcp-injection-filter
    litellm_params:
      guardrail: litellm_content_filter
      mode: pre_mcp_call
      default_on: true
      categories:
        - category: prompt_injection_jailbreak
          enabled: true
          action: BLOCK
          severity_threshold: low
```

### Listing tools over the MCP REST surface

```bash
curl -s http://localhost:4000/mcp-rest/tools/list \
  -H "Authorization: Bearer $LITELLM_API_KEY"
```

### Log example for a poisoned tool hidden from `tools/list`

```text
MCP server `notes`: 1 tool description(s) blocked by a guardrail and hidden from tools/list
- `get_note`: Content blocked: prompt_injection_jailbreak conditional match 'enable + no restrictions' detected (severity: high)
```

### Pre-MCP-call test request (chat completions with explicit guardrail selection)

```bash
curl http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -d '{
    "model": "gpt-6-luna",
    "messages": [
      {"role": "user", "content": "My credit card is 4111-1111-1111-1111 and my email is john@example.com"}
    ],
    "guardrails": ["mcp-input-validation"]
  }'
```

The page describes the outcome as: credit card blocked (request rejected);
email masked (for example, replaced with `<EMAIL_ADDRESS>`).

### MCP tool call through the OpenAI SDK with guardrails selected

```python
import openai

client = openai.OpenAI(
    api_key="your-api-key",
    base_url="http://localhost:4000"
)

# This request will trigger MCP guardrails
response = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[
        {"role": "user", "content": "Send an email to 555-123-4567 with my SSN 123-45-6789"}
    ],
    tools=[{"type": "mcp", "server_label": "litellm", "server_url": "litellm_proxy"}],
    extra_body={"guardrails": ["mcp-input-validation"]},
)
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-generic-guardrail-api.md` Claim 3 — both
    contracts model a guardrail as a gate plus optional body rewrite rather
    than a pure pass/fail flag. The generic API uses the
    `BLOCKED`/`NONE`/`GUARDRAIL_INTERVENED` verdicts; this MCP page uses
    "block verdict rejects the tool call" and "mask verdict rewrites the
    matching text in place" for `CallToolResult` content. Same control shape at
    a different layer (MCP tool traffic vs. the proxy→guardrail webhook).
- **Contradicts**: None. No existing source note claims that MCP tool results
  are automatically safe, that parent-request guardrail selection propagates to
  MCP sub-calls, or that an HTTP 200 proves a tool result was not blocked. No
  contradiction issue filed.
- **Extends**:
  - `source-notes/docs-litellm-mcp-control.md` Claim 9 — that note documents
    that pinning freezes the tool list/descriptions/schemas, closes tool
    poisoning, and takes the snapshot after the discovery guardrail scan. This
    page supplies the scan semantics: it runs on `tools/list` over `/mcp`,
    `/{server_name}/mcp`, `/mcp-rest/tools/list`, and LLM-driven discovery; it
    hides blocked tools and refuses known-name calls; and it still scans pinned
    text (Claim 10 here).
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md` — the failure
    note covers creation-time MCP stdio command injection ("What Was Attempted"
    and "Root Cause" sections); this page covers the runtime tool-path controls
    (argument scanning, result scanning, and discovery-time description
    scanning). Together they cover creation, invocation, and returned-content
    surfaces of the MCP threat model.
- **Novel**:
  - MCP-specific `pre_mcp_call` / `during_mcp_call` / `post_mcp_call` phases,
    including response-side scanning before the model sees a tool result.
  - Discovery-time scanning of tool descriptions and input-schema descriptions,
    with blocked tools hidden from the listing and refused on `tools/call`.
  - The `mcp_tool_description_blocked` alert and its once-per-distinct-set,
    self-clearing lifecycle.
  - Call-time definition retrieval for clients that never called `tools/list`
    and for calls handled by another proxy worker.
  - Block-as-MCP-tool-error semantics (`result.isError: true`, possibly HTTP
    200) and the fact that a block does not make the overall Responses request
    return HTTP 400.
  - The `default_on` requirement because MCP sub-calls do not inherit the
    parent request's guardrail selection.
  - The custom-guardrail discovery hook contract (`list_mcp_tools`,
    `mcp_tool_description`, `mcp_input_schema`, description texts ahead of
    argument texts).

## Guide Impact

- **Chapter 06 (Security and Trust) — MCP tool trust boundaries**: Add a
  concrete control pattern: scan tool arguments with `pre_mcp_call`, scan
  returned tool content with `post_mcp_call` before it reaches the model, and
  scan tool descriptions/input-schema descriptions at discovery. State that
  scanning arguments alone leaves indirect injection and PII in tool results
  uncovered, and that a guardrail must be `default_on: true` to apply to MCP
  sub-calls.
- **Chapter 06 (Security and Trust) — tool poisoning**: Extend the existing
  tool-pinning advice with the discovery-scan behavior: a blocked tool is
  omitted from `tools/list` and refused on `tools/call` even when the client
  knows the name, and a masked description is served masked. Position pinning
  (approved catalog) and discovery guardrails (content scan) as complementary,
  not substitutes.
- **Chapter 05 (LLM Ops Reliability) — guardrail enforcement monitoring**: Add
  the HTTP-200/tool-error caveat. A successful `/mcp` or `/v1/responses` status
  does not prove no block occurred; monitor MCP `result.isError`, guardrail
  logs, and the `mcp_tool_description_blocked` alert. Also add startup-log
  verification that every configured MCP guardrail registered, because an
  unsupported `mode` logs an error and skips the guardrail while the proxy
  continues starting.
- **Chapter 03 (Runbooks and Agents) — MCP guardrail runbook**: Add a
  pre-deployment check that exercises each mode (`pre`, `post`, discovery
  listing) and a response step for `mcp_tool_description_blocked`: identify the
  hidden tool, inspect the upstream description/schema, decide whether to pin,
  and re-enable only after the upstream catalog is clean.

## Extraction Notes

- Primary source read in full from the live Docusaurus `.md` endpoint
  (`https://docs.litellm.ai/docs/mcp_guardrail.md`), which exposes the page text
  without navigation chrome. Front-matter metadata reports
  `last_updated: "2026-10-28"`; `date_published` is not stated on the page.
- Followed the linked `mcp_control` page and `mcp_config_reference` page to
  verify the pinning interaction and the MCP execution paths. `mcp_cost` and
  `mcp_tool_search` were not needed for this extraction.
- All quotes were checked against the `.md` source. Multi-line quotes (Claim 8
  and Claim 12) are contiguous bullet-list block quotes from the source; the
  markdown link targets inside quoted text are preserved verbatim.
- Candidate dismissal from `miner-related-notes.md`: all ten lexical candidates
  were reviewed and are unrelated to MCP tool-call guardrails —
  `docs-litellm-batches-api.md` (batch API rate limits),
  `docs-litellm-generate-content.md` (Gemini native safetySettings
  passthrough), `docs-litellm-enterprise.md` (enterprise licensing/features),
  `docs-litellm-completion-web-search.md` (provider web-search surface),
  `docs-litellm-evals-api.md` (managed Evaluations API),
  `docs-litellm-audio-transcription.md` (audio endpoint guardrail row, not MCP),
  `docs-litellm-completion-input-params.md` (supported-parameter gate),
  `docs-litellm-files-endpoints.md` (provider files passthrough),
  `docs-litellm-bedrock-invoke.md` (Bedrock native invoke passthrough), and
  `docs-litellm-a2a-iteration-budgets.md` (A2A session cost/iteration limits).
  Cross-references were instead found by searching existing MCP and guardrail
  notes and verified against their numbered claims where applicable.
- No contradiction issue filed: this page is additive to the existing MCP
  access-control/pinning note and the MCP stdio failure note; it does not
  oppose any existing claim.
- The page is first-party capability documentation with no measurements. The
  `confidence_overall: emerging` reflects documented-but-unmeasured behavior
  and a living vendor doc that can change between releases, not doubt that the
  page states these contracts.
