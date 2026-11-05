---
source_url: https://docs.litellm.ai/docs/mcp_rest_api
source_type: docs
title: "MCP REST API — LiteLLM Documentation (direct HTTP tool-invocation contract)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; .md metadata last_updated 2026-11-03)
date_extracted: 2026-11-05
last_checked: 2026-11-05
status: current
confidence_overall: emerging
issue: "#1957"
---

# MCP REST API (LiteLLM Docs)

> LiteLLM documents a three-endpoint REST surface (`GET /v1/mcp/server`,
> `GET /mcp-rest/tools/list`, `POST /mcp-rest/tools/call`) that invokes MCP tools
> directly over HTTP, separately from the JSON-RPC transport at `/mcp`; the page
> supplies the tool-name grammar (prefix + separator, optional 3-character short
> prefix), `server_id` resolution (UUID / server_name / alias), and a concrete
> HTTP error taxonomy whose most operationally notable entry is `arguments: null`
> surfacing as **500**, not a 4xx.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP REST
  API" page under "MCP Gateway → Features → Essential").
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the routes, request fields, env vars, and error bodies it
  publishes. It is a short capability/reference page: no measured reliability,
  latency, adoption, or incident data. Claims below stay at "the gateway
  documents this contract" and are graded `emerging` per the Prospector.
- **Scope**: Covers only the direct HTTP invocation surface — the three routes,
  inbound auth forms, tool-name resolution/prefixed vs. unprefixed calls,
  `server_id` resolution, the call request body, and a "what does not work"
  error list. It does **not** cover LLM-driven MCP use (`/v1/responses`, Cursor,
  OpenAI SDK), OAuth/SigV4 outbound auth, permissions composition, guardrails,
  rate limits, or deployment topology; those are linked to other pages and
  covered by existing source notes.
- **Artifacts followed**: The live markdown endpoint
  (`https://docs.litellm.ai/docs/mcp_rest_api.md`) was fetched and read in full
  (HTTP 200, no paywall, 290 lines). Linked pages (`mcp_usage`,
  `mcp_config_reference`, `mcp_troubleshoot`) were used only to verify
  overlapping material is already covered; they were not re-extracted.

## Extracted Claims

### Claim 1: The direct-invocation surface is exactly three REST endpoints and is deliberately separate from the JSON-RPC MCP transport at `/mcp` and `/{server_name}/mcp`
- **Evidence**: The Endpoints table lists `GET /v1/mcp/server`, `GET
  /mcp-rest/tools/list`, and `POST /mcp-rest/tools/call`; the following sentence
  marks the separation from the Claude Desktop/Cursor transport and points to
  the configuration reference for the endpoint decision matrix. The page's own
  opener scopes it to "when you already know which tool to run."
- **Confidence**: emerging (documented vendor route contract; no measured use)
- **Quote**: "These routes are separate from the JSON-RPC MCP transport at `/mcp` or `/{server_name}/mcp` used by Claude Desktop and Cursor."
- **Quote**: "Use this when you already know which tool to run. For LLM-driven tool use, see [Using your MCP](./mcp_usage.md)."
- **Our assessment**: The split is the page's framing claim: the REST surface is
  an operator/programmatic path, not the agent-facing MCP protocol path. That
  matters for runbooks because the same tool can be reached two ways with
  different naming, auth-parsing, and error semantics (see Cross-References to
  `docs-litellm-mcp-troubleshoot.md` Claim 7). The three-endpoint set is small
  enough to treat as a closed contract, but it is vendor-declared, not a spec.

### Claim 2: Every REST request authenticates with a LiteLLM API key, shown in two accepted forms — `Authorization: Bearer` and `x-litellm-api-key`
- **Evidence**: The page's Auth block gives both header forms; the "Works:
  `x-litellm-api-key` header" example repeats the second form on a tool call.
- **Confidence**: emerging (documented examples; the page does not enumerate the
  full accepted header set)
- **Quote**: "LiteLLM API key on every request:"
- **Our assessment**: These are two demonstrated accepted forms, not an
  exhaustive allowlist. `docs-litellm-gateway-auth-reference.md` Claim 1 states
  the MCP REST/management routes accept the full vendor auth-alias set
  (`API-Key`, `x-api-key`, `x-goog-api-key`, `Ocp-Apim-Subscription-Key`, and
  `x-litellm-tags`), while the MCP ASGI routes do not. This page showing only
  Bearer / `x-litellm-api-key` is a scope difference in the examples, not a
  contradiction — an operator should read this page's two forms as the minimum,
  and the auth reference as the broader route-family contract.

### Claim 3: Tool names follow one of two patterns — a globally prefixed name, or an unprefixed name paired with `server_id`
- **Evidence**: The Tool naming table: "Prefixed" for a global tool list or a
  self-contained tool id (`places_api-getPlaces`), "Unprefixed + `server_id`" for
  a per-server tool list (`server_id: places_api`, `name: getPlaces`).
- **Confidence**: emerging (documented request grammar)
- **Quote**: "LiteLLM registers tools from multiple MCP servers. Tool names in requests follow one of two patterns:"
- **Our assessment**: The two forms are not interchangeable in every context:
  the prefixed form is self-describing and works without `server_id`, while the
  unprefixed form depends on `server_id` to disambiguate. This is the source of
  a large share of the page's downstream error cases (wrong separator, missing
  `server_id`, tool/server mismatch).

### Claim 4: The prefix grammar is `{server_prefix}{separator}{upstream_tool_name}`, with `-` as the default separator
- **Evidence**: The "Prefix format" line and the two bullets that follow it.
- **Confidence**: emerging (documented grammar/default)
- **Quote**: "**Prefix format:** `{server_prefix}{separator}{upstream_tool_name}`"
- **Quote**: "Default **separator** is `-` (hyphen)."
- **Our assessment**: The default is a hyphen, not the underscore many MCP
  server names themselves contain (`places_api`, `order_status_mcp`). That
  collision is why the page's "wrong separator" failure section exists: copying
  the server's own naming convention into the tool id produces a name the
  gateway cannot resolve. This is config-grammar knowledge a runbook should
  state explicitly rather than leave to trial and error.

### Claim 5: Both prefix knobs are proxy-level configuration — `MCP_TOOL_PREFIX_SEPARATOR` overrides the separator, and `LITELLM_USE_SHORT_MCP_TOOL_PREFIX=true` replaces the server-name prefix with a 3-character id
- **Evidence**: The two bullets under "Prefix format" and the separate "What
  does not work → Wrong separator" fix sentence that points at
  `MCP_TOOL_PREFIX_SEPARATOR`.
- **Confidence**: emerging (documented env vars)
- **Quote**: "Override with env var `MCP_TOOL_PREFIX_SEPARATOR` on the proxy."
- **Quote**: "With `LITELLM_USE_SHORT_MCP_TOOL_PREFIX=true`, the prefix is a 3-character id instead of the server name (same `{prefix}{separator}{tool}` shape)."
- **Our assessment**: These are deployment-wide namespace switches, not
  per-request fields. Flipping either changes the public tool id for every
  caller — a client that hardcodes a prefixed name breaks, while clients using
  unprefixed name + `server_id` are insulated. The page does not describe a
  compatibility window or dual-name serving, so the guide should treat these as
  breaking config changes.

### Claim 6: The proxy forwards the **unprefixed** upstream tool name, so a name that validates at the gateway is not necessarily the name the upstream server receives
- **Evidence**: The sentence immediately after the prefix bullets.
- **Confidence**: emerging (documented forwarding behavior)
- **Quote**: "The proxy calls the **upstream** MCP server with the unprefixed tool name (e.g. `getPlaces`), not the full prefixed string."
- **Our assessment**: This is the highest-value detail for debugging upstream
  MCP servers: seeing `places_api-getPlaces` in a request log does not mean the
  upstream saw that string. It also bounds what `MCP_TOOL_PREFIX_SEPARATOR` and
  the short-prefix flag can affect — they change the gateway-side namespace,
  not the upstream call. An operator should not blame the upstream for a name
  that the gateway itself mangled before forwarding.

### Claim 7: `server_id` accepts a UUID, `server_name`, or alias interchangeably, and `GET /v1/mcp/server` is the discovery call that returns those identifiers
- **Evidence**: The "List MCP servers" section, the server_id field table, and
  the "One server" note.
- **Confidence**: emerging (documented resolution rules)
- **Quote**: "`server_id` accepts UUID, `server_name`, or alias."
- **Quote**: "Use `server_id` or `server_name` from the response in later calls. Both work as `server_id` in `/mcp-rest/*`."
- **Our assessment**: Three interchangeable identifiers for one field make
  copy-paste errors easy: a value that looks like a server name may be an alias,
  and an id from a customer example may be a placeholder (Claim 13). The
  authoritative discovery path is `GET /v1/mcp/server`, not a support thread or
  the config file alone. This is a runbook step, not just a field description.

### Claim 8: `GET /mcp-rest/tools/list` serves all servers or one server; the single-server listing is "recommended for discovery" and returns **unprefixed** upstream names
- **Evidence**: The two subsections under "List tools"; the all-servers example
  notes `mcp_info.server_name` identifies the owning server, and the one-server
  section is explicitly labelled "recommended for discovery."
- **Confidence**: emerging (documented listing behavior)
- **Quote**: "Returns **unprefixed** upstream names (e.g. `getPlaces`, `ping`)."
- **Our assessment**: Discovery output and invocation input are not the same
  shapes: the list can return an unprefixed name that is only callable with a
  `server_id` (or after prefixing). A client that reads the list and passes the
  name back verbatim to `/mcp-rest/tools/call` without `server_id` can hit the
  400 or mismatch paths. The page telling operators to prefer the per-server
  listing is also a hint that the all-servers view carries cross-server
  ambiguity.

### Claim 9: The call body requires `server_id` and `name`; `arguments` is recommended and defaults to `{}` when omitted, but `null` is explicitly forbidden
- **Evidence**: The Request body table: `server_id` Yes/string, `name` Yes/string,
  `arguments` Recommended/object with the "use `{}` when none… Do not pass
  `null`." description.
- **Confidence**: emerging (documented request contract)
- **Quote**: "Tool parameters; use `{}` when none. If omitted, the proxy treats it as `{}`. Do not pass `null`."
- **Our assessment**: The defaulting rule (`omitted` → `{}`) means an empty
  `arguments` field is unnecessary; only the `null` shape is invalid. This is a
  narrow but concrete contract that a client library or a runbook can enforce
  before sending the request, avoiding the 500 in Claim 10.

### Claim 10: `arguments: null` returns HTTP **500**, turning a client-side request-shape error into a server-side one
- **Evidence**: The "`arguments: null`" failure section shows the request and the
  inline captured status comment; the fix is `{}` or omit.
- **Confidence**: emerging (vendor-documented status; no independent repro)
- **Quote**: "# 500 — arguments must be a JSON object, not null"
- **Quote**: "**Fix:** use `\"arguments\": {}` or omit the field entirely."
- **Our assessment**: This is the single most operationally important claim on
  the page. A 5xx SLO or error-budget alert keyed on HTTP status will absorb bad
  direct REST callers as gateway failures, and an operator following the status
  code will look at the gateway/upstream rather than the caller. The correct
  answer is either client-side validation (coerce/omit `null`) or SLO
  classification that separates this body-contract case from genuine gateway
  faults. The page documents the behavior but not whether it is intentional;
  treat it as a current contract, not a desired one.

### Claim 11: Missing `server_id` is `400 missing_parameter`; a tool that belongs to a different server than `server_id` is `403 tool_server_mismatch` with a structured `detail.error` body
- **Evidence**: The two corresponding "What does not work" sections and the
  verbatim JSON response for the mismatch case.
- **Confidence**: emerging (vendor-documented statuses and body)
- **Quote**: "# 400 missing_parameter"
- **Quote**:
```json
{
  "detail": {
    "error": "tool_server_mismatch",
    "message": "Tool 'places_api-getPlaces' belongs to MCP server 'places_api' but request specified server_id for 'order_status_mcp'."
  }
}
```
- **Our assessment**: These are gateway-local validation failures — the upstream
  tool never runs, so debugging the MCP server is wasted work. The mismatch body
  is unusually helpful: it names both the tool's real server and the requested
  one, which is enough for a client to self-correct. A runbook can key on
  `detail.error` rather than parsing the human message.

### Claim 12: A `404 server_not_found` (unknown name/UUID) and a `403 access_denied` (server exists but the key cannot access it) are deliberately distinguishable on the same endpoint
- **Evidence**: The "Invalid or unknown server_id" section gives the 404 case and
  the following comment block gives the 403 case.
- **Confidence**: emerging (vendor-documented status pair)
- **Quote**: "# 404 server_not_found (unknown name/uuid)"
- **Quote**: "# 403 access_denied (server exists but key cannot access it)"
- **Our assessment**: The pair separates "typo/wrong identifier" from "real
  server, key lacks access" — a useful triage distinction that many APIs blur
  into a single 404 for enumeration resistance. The tradeoff is that the
  distinct 403 confirms server existence to a caller who is already
  authenticated; the page does not discuss whether that is intended. Either way
  the operator should not treat 404 as automatically a permissions problem.

### Claim 13: Using the wrong separator (`_` instead of `-`) yields tool-not-found or wrong routing, and placeholder ids from customer examples (`serverid1`, `serverid2`) are not valid unless those servers were actually created
- **Evidence**: The "Wrong separator" section (default is `-`, not `_`) and the
  "Placeholder server ids from customer examples" section.
- **Confidence**: emerging (documented failure modes)
- **Quote**: "# Tool not found or wrong routing"
- **Quote**: "Strings like `\"serverid1\"` / `\"serverid2\"` are not valid unless you created servers with those exact ids."
- **Our assessment**: Both are copy-paste traps rather than platform faults. The
  wrong-separator case is made worse by real server names containing `_`
  (e.g. `places_api`), so the "obvious" concatenation is the broken one. The
  placeholder warning is a useful corpus-level lesson: examples pasted from
  support threads can look like a contract while being fictional identifiers.
  Always resolve via `GET /v1/mcp/server` (Claim 7).

### Claim 14: Optional JSON-RPC fields (`jsonrpc`, `method`, `id`) are ignored by the REST handler, so clients may include them for compatibility but they do not change REST behavior
- **Evidence**: The Request body section's note after the field table.
- **Confidence**: emerging (documented handler behavior)
- **Quote**: "Optional JSON-RPC fields (`jsonrpc`, `method`, `id`) are ignored by the REST handler; you may include them for client compatibility."
- **Our assessment**: The REST route is not a JSON-RPC endpoint with a different
  path — it is a distinct handler that tolerates JSON-RPC-shaped bodies. This
  makes it easier to point an existing MCP client at `/mcp-rest/tools/call`, but
  it also means fields that would be meaningful in JSON-RPC (`id`, `method`)
  provide no routing or correlation semantics here. Do not assume `/mcp`
  behavior carries over.

## Concrete Artifacts

All artifacts are verbatim from
`https://docs.litellm.ai/docs/mcp_rest_api.md` unless explicitly marked as a
derived summary.

### Endpoint surface (from the Endpoints table)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/v1/mcp/server` | List MCP servers (get `server_id` / `server_name`) |
| `GET` | `/mcp-rest/tools/list` | List tools (all servers, or one server) |
| `POST` | `/mcp-rest/tools/call` | Execute a tool |

Attribution: "MCP REST API", Endpoints section.

### Authentication headers (from the Auth block)

```bash
-H "Authorization: Bearer $LITELLM_API_KEY"
# or
-H "x-litellm-api-key: sk-<your-litellm-api-key>"
```

Attribution: "MCP REST API", Auth block.

### Tool-name grammar (from the Tool naming section)

```text
Prefix format: {server_prefix}{separator}{upstream_tool_name}
Default separator: - (hyphen)
Override: MCP_TOOL_PREFIX_SEPARATOR (proxy env var)
Short prefix: LITELLM_USE_SHORT_MCP_TOOL_PREFIX=true → 3-character id prefix
```

Attribution: "MCP REST API", Tool naming section (bullets condensed, values
verbatim).

### Call request body (from the Request body table)

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `server_id` | Yes | string | UUID, `server_name`, or alias |
| `name` | Yes | string | Prefixed or unprefixed tool name |
| `arguments` | Recommended | object | Tool parameters; use `{}` when none. If omitted, the proxy treats it as `{}`. Do not pass `null`. |

Attribution: "MCP REST API", §3 Call a tool → Request body.

### Working call examples (from the page)

Prefixed name + server UUID:

```bash
curl -s -X POST http://localhost:4000/mcp-rest/tools/call \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "17a4490465f74d3696caf12b30220166",
    "name": "places_api-getPlaces",
    "arguments": {}
  }' | jq .
```

Unprefixed name + server name:

```bash
curl -s -X POST http://localhost:4000/mcp-rest/tools/call \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "places_api",
    "name": "getPlaces",
    "arguments": { "query": "coffee" }
  }' | jq .
```

Attribution: "MCP REST API", §3.

### Failure matrix (from "What does not work")

| Condition | Documented status | Documented signal |
|-----------|-------------------|-------------------|
| `server_id` missing | `400` | `missing_parameter` |
| `arguments: null` | `500` | "arguments must be a JSON object, not null" |
| wrong separator (`_` instead of `-`) | not stated | "Tool not found or wrong routing" |
| tool belongs to another server | `403` | `tool_server_mismatch` with `detail.error` |
| unknown name/UUID | `404` | `server_not_found` |
| server exists, key lacks access | `403` | `access_denied` |
| placeholder ids (`serverid1`) | not stated | invalid unless created |

Attribution: "MCP REST API", "What does not work" sections (table assembled from
the page's inline status comments; not verbatim table text).

## Cross-References

**Candidates from `miner-related-notes.md`** (all ten addressed; verified per
MINER §4b where cited):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch rate-limit
  accounting (`POST /v1/batches`, JSONL token charging); no MCP REST routes or
  tool-invocation contract.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**:
  provider-native web-search surface across chat/responses; unrelated to MCP
  tool invocation.
- `source-notes/docs-litellm-mcp-zero-trust.md` — **cited** (adjacent MCP
  surface; see Extends). Its subject is outbound JWT signing on every MCP tool
  call, not the REST invocation contract. No shared claim to corroborate; cited
  as the complementary gateway→upstream control on the same MCP path.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: managed Evaluations
  API and label-classifier grading; no MCP REST content.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: licensing and
  enterprise feature tiers; unrelated.
- `source-notes/docs-litellm-mcp-deployment.md` — **cited** (Extends): that note
  documents the deployment topology / public-internet exposure of the MCP
  gateway; this page adds the `/mcp-rest/*` surface that such a deployment also
  exposes and must authorize. No claim-level overlap beyond the same gateway.
- `source-notes/docs-litellm-files-endpoints.md` — **dismissed**: provider
  `/files` passthrough; unrelated.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` passthrough; unrelated.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock-native
  `/invoke` passthrough; unrelated.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  session cost/iteration caps; no MCP REST contract.

**Primary cross-references** (all claim numbers re-read before citing):

- **Corroborates**:
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 1** — that
    note establishes the route-family auth split: MCP ASGI routes bypass the
    standard FastAPI auth dependency and do not parse vendor auth aliases,
    while MCP REST/management routes (`/v1/mcp/...`, `/mcp-rest/...`) and all
    A2A routes accept the full header set. This page's REST examples (Claim 2)
    are consistent with the REST half; the page simply demonstrates two of the
    accepted forms. Scope difference in examples, not a contradiction.
  - `source-notes/docs-litellm-mcp-control.md` **Claim 11** — documents that
    `mcp_rpm_limit` counts every MCP operation sent to a server, explicitly
    including "the REST tool listing at `/mcp-rest/tools/list`". This page
    defines that endpoint (Claim 8), so the two notes describe the same route
    from the rate-limit and request-contract sides.
  - `source-notes/docs-litellm-mcp-guardrails.md` **Claim 7** — the discovery
    guardrail scan explicitly covers `GET /mcp-rest/tools/list` (alongside
    `/mcp` and `/{server_name}/mcp`). This page documents that listing endpoint
    and its unprefixed output (Claim 8); together they show the REST listing is
    a first-class discovery path with its own guardrail coverage.
- **Contradicts**: None filed. The one candidate tension is
  `docs-litellm-mcp-troubleshoot.md` **Claim 7**, which says calling an
  unprefixed/wrong tool name returns HTTP 200 and fails inside the tool result
  with `isError: true`. That claim is scoped to the `/mcp` named endpoint; this
  page says the wrong separator on `/mcp-rest/tools/call` yields "Tool not
  found or wrong routing" and does not state the HTTP status. Different
  transports, and this page leaves the REST status unstated — a scope gap, not
  claim-level opposition. Recorded under Extends, not a contradiction.
- **Extends**:
  - `source-notes/docs-litellm-mcp-troubleshoot.md` — that note's status-line
    fault localization (`Claim 1`) and "200 is not success" tool-error behavior
    (`Claim 7`) cover the JSON-RPC `/mcp` transport. This page supplies the
    sibling REST-surface error taxonomy (Claims 10-13) needed before an operator
    jumps to the upstream-server runbook. The REST table and the `/mcp`
    status/gap analysis are complementary views of the same gateway.
  - `source-notes/docs-litellm-mcp-aws-sigv4.md` — its Concrete Artifacts →
    "Tool usage" section calls `/mcp-rest/tools/list` and `/mcp-rest/tools/call`
    with `server_id` + prefixed `name` + `arguments`; this page is the contract
    those examples assume, so the SigV4 note's usage example is now
    specification-backed.
  - `source-notes/docs-litellm-mcp-deployment.md` — Extends the deployment
    topology with the direct REST surface: an internet-facing MCP gateway
    exposes `/mcp-rest/*` as well as `/mcp`, so the exposure analysis applies to
    both, and the REST routes accept the full LiteLLM API key (Claim 2).
  - `source-notes/docs-litellm-mcp-zero-trust.md` — the zero-trust guardrail
    signs outbound MCP tool calls; a REST-initiated call still traverses the
    same outbound path, so the REST contract is the front door to the path that
    note hardens. No claim-level corroboration is asserted (the zero-trust note
    does not mention `/mcp-rest`).
- **Novel**: The REST API contract itself is new to the corpus. Earlier notes
  mention `/mcp-rest/...` in passing (auth-header split in
  `docs-litellm-gateway-auth-reference.md`, `mcp_rpm_limit` counting in
  `docs-litellm-mcp-control.md`, discovery scan in
  `docs-litellm-mcp-guardrails.md`, `/mcp-rest/test/*` gating in
  `failure-litellm-mcp-stdio-command-injection.md`), but none extracts: the
  three-endpoint set, the `{server_prefix}{separator}{upstream_tool_name}`
  grammar and its two env-var knobs, the UUID/server_name/alias resolution
  rule, the `arguments` default-vs-null distinction, or the REST error taxonomy
  (`400 missing_parameter`, `500` on `arguments: null`, `403
  tool_server_mismatch`, `404 server_not_found` vs `403 access_denied`).

## Guide Impact

- **Chapter 03 (Runbooks and Agents)** — §"Structured tool contracts over
  free-form interfaces" and §"The pre-on-caller triage pattern": Add a
  gateway-localization step for direct MCP REST calls. Before debugging the
  upstream MCP server, the on-caller should check, in order: (1) `server_id`
  resolved from `GET /v1/mcp/server` (Claim 7), (2) tool name grammar —
  prefixed with `-`, or unprefixed plus `server_id` (Claims 3-6, 13), and
  (3) `arguments` is an object or omitted (Claim 9). The documented
  `400/403/404` bodies (Claims 11-12) are gateway-local refusals, so escalating
  to the MCP-server owner is premature until they are ruled out. Cite this note
  as the REST-surface companion to `mcp_troubleshoot`'s `/mcp` triage.

- **Chapter 05 (LLM Ops Reliability)** — §"SLO programs for LLM services":
  Add the `arguments: null` → **500** caveat (Claim 10). A status-only 5xx SLO
  over `/mcp-rest/tools/call` counts a malformed direct caller as a gateway
  failure, inflating the error budget and pointing responders at the wrong hop.
  Either validate/coerce `arguments` at the client or edge, or classify this
  body-contract case separately from genuine gateway/upstream 5xx. Also add
  tool-namespace changes (`MCP_TOOL_PREFIX_SEPARATOR`,
  `LITELLM_USE_SHORT_MCP_TOOL_PREFIX`) to the config-change watch list
  (Claim 5): flipping either silently changes every prefixed tool id.

- **Chapter 06 (Security and Trust)** — §"Gateway credential routing: declare,
  don't infer" / MCP auth surface: Record that the `/mcp-rest/*` family accepts
  a LiteLLM API key as `Authorization: Bearer` or `x-litellm-api-key` (Claim 2),
  and cross-reference `docs-litellm-gateway-auth-reference.md` Claim 1 for the
  broader route-family header split — do not assume header-form parity between
  `/mcp` and `/mcp-rest`. Add the `404 server_not_found` vs `403 access_denied`
  distinction (Claim 12) to the access-denial triage section: a 404 is an
  identifier problem, not necessarily a permission problem, and the distinct
  403 confirms server existence to an authenticated caller.

- **Chapter 06 (Security and Trust)** — MCP tool-name trust boundary: Use
  Claim 6 (proxy forwards the unprefixed upstream name) together with Claim 5
  (deployment-wide prefix/separator knobs) to make explicit that the
  gateway-side tool identity is a configurable alias, not the upstream tool
  name. Any allowlist, pin, or audit keyed on a tool name must state which layer
  it applies to; a name valid at the gateway is not evidence of what the
  upstream server received.

## Extraction Notes

- Primary source read in full from the live markdown endpoint
  (`https://docs.litellm.ai/docs/mcp_rest_api.md`, HTTP 200, no paywall, 290
  lines). The HTML page was also fetched; all `Quote` fields and Concrete
  Artifacts are character-for-character from the markdown source. Multi-quote
  claims use ` / `-separated quoted fragments; no non-adjacent sentences were
  spliced into a single quoted passage, and the assembled failure matrix is
  explicitly labelled as derived rather than quoted.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or explicitly dismissed above. Primary
  cross-references were verified by re-reading the cited notes:
  `docs-litellm-gateway-auth-reference.md` (Claim 1),
  `docs-litellm-mcp-control.md` (Claim 11),
  `docs-litellm-mcp-guardrails.md` (Claim 7),
  `docs-litellm-mcp-troubleshoot.md` (Claims 1, 7),
  `docs-litellm-mcp-aws-sigv4.md` (Concrete Artifacts → Tool usage), and
  `docs-litellm-mcp-deployment.md` (source context/topology). Claim numbers and
  quotes confirmed against the cited notes; none invented.
- No contradiction issue filed (MINER §4a). The only apparent tension —
  `mcp_troubleshoot` Claim 7's HTTP-200/`isError` behavior for wrong tool names
  vs. this page's unstated REST status for a wrong separator — is a
  transport-scope difference, and this page never asserts a REST status for
  that case. The auth-form difference vs. `gateway-auth-reference` Claim 1 is
  likewise a scope difference (demonstrated examples vs. exhaustive route-family
  table). Checked `CONTRADICTIONS.md` and open `contradiction`-labeled issues:
  no existing entry covers the MCP REST contract.
- `confidence_overall` is `emerging`, matching sibling LiteLLM docs notes: the
  page is first-party capability documentation with concrete routes, fields,
  env vars, and captured-looking status comments, but no measured reliability,
  independent reproduction, or production experience. Claim 10 (the
  `arguments: null` → 500) is the most checkable operational claim and should
  stay `emerging` until reproduced against a live proxy.
- `date_published` is unknown (living Docusaurus page); the markdown
  front-matter reports `last_updated: "2026-11-03"`. `date_extracted` and
  `last_checked` are both 2026-11-05.
