---
source_url: https://docs.litellm.ai/docs/mcp_troubleshoot
source_type: docs
title: "MCP Troubleshooting Guide — LiteLLM Documentation (symptom-to-fix runbook for an MCP gateway)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; .md metadata last_updated 2026-11-01)
date_extracted: 2026-11-03
last_checked: 2026-11-03
status: current
confidence_overall: emerging
issue: "#2001"
---

# MCP Troubleshooting Guide (LiteLLM Docs)

> LiteLLM documents a two-hop MCP gateway topology (`Client -> LiteLLM Proxy ->
> MCP Server`) and a symptom-to-fix runbook whose central operational rule is
> that the HTTP status line localizes the fault: 401/403/404/405/406 are raised
> by LiteLLM before the upstream call, while a `200` carrying
> `"status": "unreachable"` or an empty tool list means the upstream hop failed
> — an unreachable MCP server is **not** a gateway 502, so status-keyed health
> checks and error-rate SLOs can miss a fully broken server.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP
  Troubleshooting Guide" page under "MCP Gateway → Troubleshooting & FAQ").
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented routes, status/body shapes, header names,
  log lines, and config keys; the page states its failure responses were
  captured against a live proxy. It publishes no independent reproduction,
  production metrics, or third-party verification, so the claims below stay at
  "the vendor documents and demonstrates this behavior" and are graded
  `emerging` per the Prospector's guidance.
- **Scope**: Covers the five-minute triage procedure, a 15-row symptom matrix
  keyed by HTTP status and layer, the endpoint/session model (aggregate `/mcp`
  vs named `/<alias>/mcp`), verified 401/403/404/405/406 responses, OAuth
  discovery/DCR/`redirect_uri` failures, network/TLS/timeout failure classes,
  empty tool lists and tool-name prefixing, silent `/v1/responses` and
  `/v1/chat/completions` MCP-tool degradation, `x-mcp-debug-*` headers,
  connectivity checks (MCP Inspector, curl, UI Playground), log examples, and
  the support-bundle checklist. Does **not** cover MCP permission composition
  (see `docs-litellm-mcp-control.md`), the OAuth flow taxonomy
  (`docs-litellm-mcp-oauth.md`), guardrail scanning
  (`docs-litellm-mcp-guardrails.md`), or deployment topology
  (`docs-litellm-mcp-deployment.md`).
- **Artifacts followed**: The live markdown endpoint
  (`https://docs.litellm.ai/docs/mcp_troubleshoot.md`) was fetched and read in
  full (HTTP 200, no paywall, 22,982 bytes). The linked pages
  (`mcp_config_reference`, `mcp_oauth`, `mcp_control`) were used only to verify
  that overlapping material is already covered by existing notes; they were not
  re-extracted here.

## Extracted Claims

### Claim 1: The HTTP status line localizes the fault — 401/403/404/405/406 are produced by LiteLLM before the upstream call, while a `200` reporting `"status": "unreachable"` or an empty tool list means the upstream MCP hop failed
- **Evidence**: The "Five-Minute Triage" Step 2 and the "Likely layer" column of
  the symptom matrix, which repeats the partition per row.
- **Confidence**: emerging (vendor-documented diagnostic rule, demonstrated on a
  live proxy; not independently verified)
- **Quote**: "The status tells you the layer: 401/403/404/405/406 come from LiteLLM before the upstream call (Client -> LiteLLM), while a `200` whose body reports `"status": "unreachable"` or an empty tool list means LiteLLM answered but the upstream hop failed (LiteLLM -> MCP Server)"
- **Our assessment**: This is the page's load-bearing idea and the transferable
  pattern: status class is a *hop selector*, not merely a severity signal. The
  clean split (client/gateway errors before the call, upstream failures after)
  gives an operator a decision procedure instead of a guess. The caveat is that
  it is LiteLLM's own partition of its own routes; the general lesson — map
  status/body to topology before debugging — transfers, but the exact row
  assignments are vendor-specific.

### Claim 2: An unreachable upstream surfaces as HTTP 200 with an empty tool list and per-server status, not as a gateway 502/503
- **Evidence**: The "Network, TLS, and timeouts" response capture plus the
  corresponding matrix row; the page says the broken-server responses were
  deliberately induced.
- **Confidence**: emerging (captured vendor response; no independent repro)
- **Quote**: "An unreachable upstream does not surface as a gateway 502. The named endpoint returns 200 with an empty tool list and a per-server status:"
- **Quote**: "Every response below was captured against a live proxy with the quickstart config and a `deepwiki` server, plus deliberately broken servers for the network and TLS rows"
- **Our assessment**: Highest-value claim for Ch02/Ch05. Any health check or SLO
  that treats non-2xx as the only failure signal will report a completely
  unreachable MCP server as healthy. The correct probe must inspect the JSON-RPC
  result: `_meta["litellm.ai/server_outcomes"]` status and a non-empty `tools`
  array. This is a concrete instance of "the transport succeeded but the work
  failed," and it is invisible to status-code telemetry.

### Claim 3: The aggregate `POST /mcp` absorbs per-server failures and can hide a broken server behind healthy ones, so triage must target the named `POST /<alias>/mcp`
- **Evidence**: "Endpoints and Sessions" and the aggregate empty-tools capture
  showing one `ok` server alongside one `unreachable` server.
- **Confidence**: emerging (documented endpoint semantics; captured response)
- **Quote**: "`POST /mcp` lists tools from every server your key can access, with each tool prefixed by its server alias (`deepwiki-ask_question`) and a per-server `litellm.ai/server_outcomes` report in `_meta`. `POST /<alias>/mcp` scopes the call to one server and is the right target for triage, because an aggregate response can hide one failing server behind other healthy ones"
- **Our assessment**: This is a partial-failure masking behavior built into the
  convenience endpoint. It is defensible as availability engineering (one dead
  server does not take down the whole tool list), but it means an aggregate
  health probe is not a per-server health probe. The named endpoint plus the
  `server_outcomes` map is the minimum viable per-server probe.

### Claim 4: The two 404 bodies have different owners — an alias/config 404 names the missing server, while a plain `{"detail":"Not Found"}` is a URL/path problem
- **Evidence**: "404: server or route", which shows both captured bodies and the
  one-line interpretation.
- **Confidence**: emerging (captured responses)
- **Quote**: "The two bodies look similar but mean different things: the first is a config/alias problem, the second is a URL problem"
- **Our assessment**: A small but high-precision triage detail. Both are 404s,
  so status alone routes them to the same bucket; only the body distinguishes a
  `mcp_servers` alias mismatch (gateway config owner) from a missing `/mcp`
  suffix (client URL owner). This is exactly the kind of disambiguation a runbook
  needs to prevent bouncing the ticket between teams.

### Claim 5: The MCP endpoints speak streamable HTTP — `Accept: application/json, text/event-stream` is mandatory (406 otherwise), POST is required for JSON-RPC (405 otherwise), and `tools/list` works without an `initialize` handshake
- **Evidence**: "Endpoints and Sessions", plus the captured 405/406 responses
  under "405 and 406: transport or endpoint mismatch".
- **Confidence**: emerging (documented transport contract; captured responses)
- **Quote**: "The endpoints speak MCP streamable HTTP. Responses arrive as `text/event-stream` frames even for single JSON-RPC calls, which is why the `Accept` header must allow both content types. Plain `tools/list` and `tools/call` requests work without a prior `initialize` handshake, so curl triage needs no session setup."
- **Quote**: "Not Acceptable: Client must accept both application/json and text/event-stream"
- **Quote**: "Both indicate the client's transport configuration, not the upstream server."
- **Our assessment**: The transport contract explains a class of failures that
  look like server faults but are client configuration: 405/406 are produced by
  the gateway's transport negotiation. The session-free `tools/list` is what
  makes a one-line curl a legitimate triage tool rather than a partial MCP
  client, and it is why the diagnostic in Claim 10 is reliable.

### Claim 6: A wrong `server_label` in `/v1/responses` or `/v1/chat/completions` returns 200 and silently answers without tools
- **Evidence**: "Responses and Chat Completions failures"; the page contrasts a
  working request (which emits `mcp_tools_fetched` / `tool_execution_results`
  items) with the wrong-label case.
- **Confidence**: emerging (documented behavior; no independent repro)
- **Quote**: "If `server_label` does not match any configured alias, the request still returns 200 but those items are absent and the model answers without tools; that silent degradation is the symptom to look for."
- **Our assessment**: This is the most dangerous failure mode on the page: no
  error, a plausible model answer, and no tool use. It converts a configuration
  typo into a quality regression that only an output-shape assertion can catch.
  SRE monitoring must assert the presence of `mcp_tools_fetched` /
  `tool_execution_results` for routes that are supposed to use MCP, not just
  request success or latency.

### Claim 7: Calling an unprefixed or wrong tool name returns HTTP 200 and fails inside the tool result with `isError: true`
- **Evidence**: "Empty tool lists and tool naming", with the captured result
  body.
- **Confidence**: emerging (captured response)
- **Quote**: "Calling an unprefixed or wrong name fails inside the tool result, not at the HTTP layer"
- **Our assessment**: Same "200 is not success" theme as Claim 6, one level
  down: tools are namespaced by server alias (`deepwiki-ask_question`), and the
  failure is a protocol-level tool error. A log pipeline that records only HTTP
  status treats this as a healthy call; tool-level error rate must be derived
  from the result body.

### Claim 8: The diagnostic curl must be run unfiltered against the named endpoint, preserving status line, headers, and body
- **Evidence**: "Five-Minute Triage" Step 1 and its diagnostic command, which
  includes `-D -` and `x-litellm-mcp-debug: true`.
- **Confidence**: emerging (documented procedure)
- **Quote**: "Do not pipe it through `grep`, you will throw away the part that identifies the layer"
- **Our assessment**: This is a direct anti-pattern warning for on-call habits:
  grepping for a known string destroys the headers that reveal the layer. The
  runbook should ship the exact unfiltered command and treat the full
  status+headers+body capture as the unit of evidence.

### Claim 9: `x-litellm-mcp-debug: true` returns masked `x-mcp-debug-*` headers that confirm the layer and outbound auth resolution, and are safe to attach to a support bundle
- **Evidence**: "Debug Headers", including the five-header capture, the
  enumeration of `auth-resolution` values, and the Claude Code config example.
- **Confidence**: emerging (documented headers and masking; extends the OAuth
  page's Claim 15)
- **Quote**: "Add `x-litellm-mcp-debug: true` to any MCP request to get masked diagnostic response headers"
- **Quote**: "`x-mcp-debug-auth-resolution` tells you how LiteLLM resolved outbound auth: `oauth2-passthrough`, `m2m-client-credentials`, `per-request-header`, `static-token`, or `no-auth`."
- **Quote**: "Values are masked, so the headers are safe to include in a support bundle"
- **Our assessment**: The masking is the operationally important property: it
  gives a shareable evidence artifact without exposing credentials. The
  `auth-resolution` enum is also a compact state machine for "which credential
  did the gateway actually send upstream," which is otherwise invisible from the
  client side. This is the proxy-MCP analogue of the SDK-only debugging surface
  in `docs-litellm-local-debugging.md` (which documents no proxy debug control).

### Claim 10: An ingress origin mismatch on the MCP OAuth Connect flow returns `400 {"detail":"invalid_request"}`, diagnosed via the `.well-known` issuer and fixed in order by `PROXY_BASE_URL` → trusted `X-Forwarded-*` plus `mcp_trusted_proxy_ranges` → ingress correction
- **Evidence**: The "MCP OAuth: Connect returns `{"detail":"invalid_request"}`"
  subsection (symptom, cause, diagnostic, three ordered fixes).
- **Confidence**: emerging (documented cause and fix order; already corroborated
  in depth by `docs-litellm-mcp-oauth.md`)
- **Quote**: "Behind a TLS-terminating ingress (Kubernetes, ALB, nginx, Cloudflare, etc.) the proxy resolves to its internal address (`http://<pod-ip>:4000`) by default, so the same-origin check rejects"
- **Quote**: "`use_x_forwarded_for` alone is not enough. Without `mcp_trusted_proxy_ranges`, the proxy refuses to honor `X-Forwarded-*` because it cannot tell a trusted reverse proxy from a direct attacker."
- **Quote**: "Operator declares the proxy's true public origin out of band, no header trust required"
- **Our assessment**: This is a symptom-index restatement of material already
  mined in `docs-litellm-mcp-oauth.md` (Claims 5–6), not new mechanics. Its added
  value is the diagnostic entry point: check the published `issuer` against the
  browser origin before touching the OAuth flow. We do not re-grade the
  mechanism here; see the OAuth note.

### Claim 11: HTTP 401/403/404 rows are distinguished by body and ownership — 403 means the credential authenticated but lacks MCP permission, and a 401 body's key-naming behavior changed in v1.107.0
- **Evidence**: "401 and 403: authentication", including the version note and
  the 403 interpretation.
- **Confidence**: emerging (documented version-dependent response behavior)
- **Quote**: "A 403 means the key authenticated but lacks MCP permissions for that server"
- **Quote**: "Starting in v1.107.0, the body no longer names the rejected key"
- **Quote**: "An expired key returns its own `Expired Key` message."
- **Our assessment**: The 403/401 split matters because it routes the fix to
  two different owners: credential rotation vs permission grant (the permission
  model is in `docs-litellm-mcp-control.md`). The version-dependent 401 body is
  a reminder that runbook string-matches on error text are brittle across
  upgrades; a runbook keyed on the literal "Invalid proxy server token passed"
  will silently stop matching after v1.107.0.

### Claim 12: The support bundle is a fixed nine-item evidence checklist with an explicit "never share" credential list
- **Evidence**: "Support Bundle" numbered list and the closing "Never share"
  paragraph.
- **Confidence**: emerging (documented escalation procedure)
- **Quote**: "A complete bundle replaces the discovery call where support reconstructs your setup"
- **Quote**: "Never share: raw LiteLLM virtual keys or the master key, upstream API keys or static tokens from `mcp_servers` auth config, OAuth client secrets, unmasked `Authorization` header values, or `.env` contents."
- **Our assessment**: This is an incident-response artifact, not just docs. The
  nine items (version, redacted config subset, masked request, raw status/headers/
  body, debug headers, proxy logs, MCP-server logs, topology+TLS termination,
  timezone timestamps) are exactly the correlation set needed to attribute a
  cross-hop failure. The "never share" list is the safe-paste boundary; it pairs
  with the masked debug headers from Claim 9 so the operator never has to choose
  between evidence and credential hygiene.

## Concrete Artifacts

All artifacts are verbatim from the fetched page
(https://docs.litellm.ai/docs/mcp_troubleshoot, `.md` endpoint, `last_updated:
"2026-11-01"`).

### Diagnostic curl (from "Five-Minute Triage", Step 1)

```bash
curl -sS -D - -X POST http://localhost:4000/deepwiki/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "x-litellm-api-key: Bearer $LITELLM_API_KEY" \
  -H "x-litellm-mcp-debug: true" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Healthy control response (from "Five-Minute Triage")

```text
HTTP/1.1 200 OK
content-type: text/event-stream

event: message
data: {"jsonrpc":"2.0","id":1,"result":{"_meta":{"litellm.ai/server_outcomes":{"deepwiki":{"status":"ok","tool_count":3}}},"tools":[{"name":"deepwiki-ask_question",...}]}}
```

### Unreachable upstream — HTTP 200, not 502 (from "Network, TLS, and timeouts")

```text
HTTP/1.1 200 OK
event: message
data: {"jsonrpc":"2.0","id":1,"result":{"_meta":{"litellm.ai/server_outcomes":{"brokenserver":{"status":"unreachable"}}},"tools":[]}}
```

### Network vs TLS failure classes in the proxy log (from "Network, TLS, and timeouts")

```text
09:00:34 - LiteLLM:WARNING: mcp_server_manager.py - Error listing tools from brokenserver: All connection attempts failed
httpx.ConnectError: All connection attempts failed
```

```text
09:01:40 - LiteLLM:WARNING: mcp_server_manager.py - Error listing tools from tlsbroken: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1000)
```

### Aggregate `/mcp` masks one broken server (from "Empty tool lists and tool naming")

```text
data: {"jsonrpc":"2.0","id":1,"result":{"_meta":{"litellm.ai/server_outcomes":{"deepwiki":{"status":"ok","tool_count":3},"brokenserver":{"status":"unreachable"}}},"tools":[{"name":"deepwiki-ask_question",...}]}}
```

### Two 404s, two owners (from "404: server or route")

```text
HTTP/1.1 404 Not Found
{"detail":"MCP server, toolset, or access group 'nosuchserver' not found"}
```

```text
HTTP/1.1 404 Not Found
{"detail":"Not Found"}
```

### 405 and 406 (from "405 and 406: transport or endpoint mismatch")

```text
HTTP/1.1 405 Method Not Allowed
allow: GET, POST, DELETE
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Method Not Allowed"}}
```

```text
HTTP/1.1 406 Not Acceptable
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept both application/json and text/event-stream"}}
```

### Unknown tool name fails inside a 200 (from "Empty tool lists and tool naming")

```text
HTTP/1.1 200 OK
data: {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"Error: Tool 'nonexistent_tool' not found"}],"isError":true}}
```

### Debug headers (from "Debug Headers")

```text
x-mcp-debug-inbound-auth: x-litellm-api-key=Bearer****1234
x-mcp-debug-oauth2-token: (none)
x-mcp-debug-auth-resolution: no-auth
x-mcp-debug-outbound-url: https://mcp.deepwiki.com/mcp
x-mcp-debug-server-auth-type: (none)
```

### Claude Code MCP config with debug header (from "Debug Headers")

```bash
claude mcp add --transport http my_server http://localhost:4000/deepwiki/mcp \
  --header "x-litellm-api-key: Bearer sk-..." \
  --header "x-litellm-mcp-debug: true"
```

### Ingress trusted-forwarder config (from "MCP OAuth: Connect returns invalid_request")

```yaml
general_settings:
  use_x_forwarded_for: true
  mcp_trusted_proxy_ranges:
    - "10.0.0.0/8"      # your ingress / load-balancer CIDR(s)
```

### Support bundle checklist (from "Support Bundle", abridged to item labels)

```text
1. LiteLLM version: curl /health/readiness output or image tag.
2. Config subset: mcp_servers block + MCP/forwarding general_settings, secrets removed.
3. The exact failing request: full curl command with the key masked.
4. HTTP status line, response headers, and body (-D - output, unfiltered).
5. x-mcp-debug-* headers from a run with x-litellm-mcp-debug: true.
6. LiteLLM proxy logs covering the failing request (--detailed_debug if possible).
7. MCP-server logs for the same time window.
8. Topology: client/LiteLLM/ingress/MCP-server placement and TLS termination.
9. Timestamps with timezone for each captured request.
```

## Cross-References

Candidate paths from `miner-related-notes.md` (all ten addressed):

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-deployment.md` — Claim 2 documents the same
    single-gateway topology (`/v1/chat/completions`, `/mcp`, `/a2a` in one
    instance) that the troubleshoot page assumes, and Claim 7 documents the
    public-internet filter being applied at every MCP access point (including
    auth/discovery), which is why a hidden/broken server can still produce a
    confusing client symptom. This note supplies the failure signature for those
    topology choices.
  - `source-notes/docs-litellm-mcp-control.md` — Claim 5 (`no-mcp-servers`
    explicit deny) and Claim 1 (permission composition) explain the 403 row in
    this page's matrix. The troubleshoot page describes the symptom; the control
    note explains the grant model that produces it.
  - `source-notes/docs-litellm-mcp-guardrails.md` — Claim 5 independently
    establishes the same "HTTP 200 is not success" theme: a blocked tool result
    can arrive as an MCP tool error under HTTP 200. Together with this page's
    Claims 2, 6, and 7, that is a repeated corpus pattern rather than a one-off.
- **Extends**:
  - `source-notes/docs-litellm-mcp-oauth.md` — Claims 5 and 6 already cover the
    ingress origin resolution chain and the `400 {"detail":"invalid_request"}`
    symptom in depth; Claim 15 covers `x-litellm-mcp-debug` and
    `SAME_AS_LITELLM_KEY`. This page adds the operator-facing symptom→fix row
    and the `.well-known` issuer check, not new OAuth mechanics (see Claim 10).
  - `source-notes/docs-litellm-local-debugging.md` — Claim 6 scopes that page to
    SDK-level debug handles and notes it documents **no** proxy debug control.
    This page supplies the proxy-MCP debug surface (`x-litellm-mcp-debug`) that
    the local-debugging note explicitly leaves out, so the two are complementary
    surfaces rather than duplicates.
  - `source-notes/docs-litellm-mcp-cost-tracking.md` — its "Extraction Notes"
    record this troubleshooting page as unread adjacent material; this note
    closes that gap. No cost semantics are added (the troubleshoot page is about
    attribution, not spend).
- **Contradicts**: none found. No contradiction issue was filed. Where this page
  overlaps `docs-litellm-mcp-oauth.md`, it restates the same fix order rather
  than opposing it.
- **Novel**: the symptom→layer→fix matrix itself, the explicit "unreachable is
  not a 502" anti-pattern, the aggregate-vs-named endpoint masking behavior, the
  silent `/v1/responses` `server_label` degradation, the two-404 disambiguation,
  and the support-bundle/credential-hygiene checklist. The corpus had
  configuration semantics and permission mechanics for LiteLLM MCP, but not a
  diagnostic runbook.
- **Dismissed candidates** (lexically related, topically unrelated):
  - `source-notes/docs-litellm-batches-api.md` — batch input-file rate limiting;
    no MCP gateway or transport-layer content.
  - `source-notes/docs-litellm-completion-web-search.md` — provider-native web
    search; not MCP transport or gateway triage.
  - `source-notes/docs-litellm-evals-api.md` — Evaluations API state; no overlap.
  - `source-notes/docs-litellm-generate-content.md` — Google `generateContent`
    passthrough; no overlap.
  - `source-notes/docs-litellm-enterprise.md` — licensing/tiering; no overlap.
  - `source-notes/docs-litellm-completion-input-params.md` — completion param
    gate; no overlap.
  - `source-notes/docs-litellm-files-endpoints.md` — provider `/files`
    passthrough; no overlap.
  - `source-notes/docs-litellm-bedrock-invoke.md` — Bedrock native Invoke
    passthrough; no overlap.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` — A2A per-session
    budgets; different protocol and failure class.

## Guide Impact

- **Chapter 02 (Observability)**: Add an MCP-gateway SLI caveat. HTTP status is
  not a sufficient health signal on this route: an unreachable upstream returns
  `200` with an empty `tools` array (Claim 2), a wrong `server_label` returns
  `200` with no MCP output items (Claim 6), and an unprefixed tool name returns
  `200` with `isError: true` (Claim 7). Recommend a pass signal derived from
  `_meta["litellm.ai/server_outcomes"].<alias>.status == "ok"` and a non-empty
  tool list, and a tool-error rate derived from result bodies, not status codes.
- **Chapter 03 (Runbooks and Agents)**: Add an "MCP gateway triage" runbook
  section with the layer-attribution matrix (Claim 1), the unfiltered named-
  endpoint diagnostic (Claims 3, 8), and the `x-mcp-debug-*` confirmation step
  (Claim 9). The guide currently discusses the MCP permission model but has no
  symptom-to-fix procedure for the gateway itself.
- **Chapter 05 (LLM Ops Reliability)**: Add "silent upstream failure" as a
  reliability failure class alongside silent model fallback: a dependency can be
  fully down while the gateway reports success, so health checks must probe the
  dependency-specific payload. Include the aggregate-endpoint masking behavior
  (Claim 3) as a reason per-server probes are required for per-server SLOs, and
  the network-vs-TLS log signatures (Claim 12 artifacts) for fast classification.
- **Chapter 06 (Security and Trust)**: Add the support-bundle credential-hygiene
  checklist (Claim 12) and the masked-debug-header pattern (Claim 9) as the
  approved way to share gateway evidence. Reinforce the OAuth origin precedence
  (`PROXY_BASE_URL` → trusted-`X-Forwarded-*`-with-range → ingress) with a pointer
  to `docs-litellm-mcp-oauth.md` for the full mechanism; do not duplicate it.

## Extraction Notes

- Primary source read in full from the live markdown endpoint
  (`https://docs.litellm.ai/docs/mcp_troubleshoot.md`, HTTP 200, no paywall,
  22,982 bytes). Front matter reports `last_updated: "2026-11-01"`. All quoted
  passages and code blocks are byte-exact from that endpoint; where the rendered
  page wraps code blocks the `.md` source was used.
- `miner-related-notes.md` was read before writing Cross-References. All ten
  listed candidates are cited or explicitly dismissed above. Additional
  cross-references (`mcp-oauth`, `mcp-control`, `mcp-guardrails`,
  `local-debugging`, `mcp-cost-tracking`) were found by searching `source-notes/`
  and correspond to the Prospector's overlap list. Every cited claim number was
  re-read in the cited note before writing (OAuth Claims 5, 6, 15; control
  Claims 1, 5; guardrails Claim 5; deployment Claims 2, 7; local-debugging
  Claim 6; cost-tracking cited by its "Extraction Notes" section, not a claim
  number).
- The Prospector supplied three triage comments with substantially the same
  reading; this note follows the third (most complete) list and does not treat
  the repetition as independent corroboration.
- No contradiction found: the overlapping OAuth rows restate the same origin
  precedence, and the "200 can mean failure" observations in the guardrails note
  are complementary, not opposing. No contradiction issue filed.
- `confidence_overall` is `emerging`: the page's response captures are concrete
  and internally consistent, but they are first-party vendor evidence for one
  product with no independent reproduction, and the diagnostic rule is
  LiteLLM-specific even though the hop-attribution pattern generalizes.
  `date_published` is unknown (living vendor docs); `date_extracted` and
  `last_checked` are both 2026-11-03 (UTC).
