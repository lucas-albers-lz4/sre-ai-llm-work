---
source_url: https://docs.litellm.ai/docs/mcp_openapi
source_type: docs
title: "MCP from OpenAPI Specs — LiteLLM Documentation (gateway-side OpenAPI/Swagger ingestion)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; front-matter last_updated 2026-10-31)
date_extracted: 2026-11-02
last_checked: 2026-11-02
status: current
confidence_overall: emerging
issue: "#1946"
---

# MCP from OpenAPI Specs (LiteLLM Docs)

> LiteLLM can turn any OpenAPI 3.0.x/3.1.x or Swagger 2.0 spec into an MCP
> server at gateway registration time — each `operationId` becomes a tool — and
> it guards an `http(s)` `spec_path` fetch with SSRF protection that is on by
> default and allowlisted by the **hostname from the URL**, with the controls
> placed under `litellm_settings` rather than `general_settings`.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP
  from OpenAPI Specs" under "MCP Gateway → MCP Servers"). The page's markdown
  endpoint (`/docs/mcp_openapi.md`) reports `last_updated: "2026-10-31"`.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented config keys, defaults, supported spec
  versions, tool-naming behavior, and SSRF controls; it publishes no
  measurements, incident reports, or independent verification. Claims stay at
  "the gateway documents this behavior" and are graded `emerging`.
- **Scope**: Covers adding an OpenAPI/Swagger-backed MCP server via
  `config.yaml` or the UI, the `mcp_servers` parameter surface (`url`,
  `spec_path`, auth fields, tool filters), supported spec versions and
  `operationId` naming, the SSRF guard on URL-based `spec_path` fetches
  (`user_url_validation` / `user_url_allowed_hosts`), and tool name/description
  overrides via UI or API. It does **not** define the execution semantics of
  each derived tool (how paths/methods/bodies map beyond `operationId`), the
  auth transport flows behind each `auth_type`, the MCP permission model, or
  general outbound MCP egress behavior.
- **Page read**: The live `.md` endpoint was read in full. Linked client
  snippets (FastMCP, Cursor, OpenAI Responses) were read but deliberately not
  extracted as gateway behavior; the linked `mcp_guardrail` discovery section
  was consulted only to frame the override-scan claim against the existing
  guardrail note.

## Extracted Claims

### Claim 1: The gateway itself converts an OpenAPI/Swagger spec into an MCP server, requiring no custom MCP server code
- **Evidence**: The page's opening sentence and the UI/API registration paths that load spec operations as tools.
- **Confidence**: emerging (documented capability; no conversion-fidelity test or edge-case matrix)
- **Quote**: "LiteLLM can convert any OpenAPI/Swagger spec into an MCP server, with no custom MCP server code required."
- **Our assessment**: This moves OpenAPI ingestion into the gateway control plane: the spec becomes an executable tool catalog at registration, not a client-side adapter. That is useful operationally but makes the spec an executable supply-chain input, which is why the SSRF guard (Claims 4–6) and the tool-description scan (Claim 8) matter. "Any spec" is vendor marketing language; the supported-version list in Claim 3 is the actual boundary.

### Claim 2: A spec-backed MCP server is configured with a base `url` plus `spec_path`; authentication and per-server tool allow/deny lists are optional fields
- **Evidence**: The `config.yaml` example and the "Configuration parameters" table.
- **Confidence**: emerging (explicit config surface; no validation rules for mismatched base URL/spec)
- **Quote**: "Path or URL to your OpenAPI spec (JSON or YAML)"
- **Our assessment**: The split between `url` (base API URL) and `spec_path` (local path or URL to the spec) is the key config shape: the spec can be local, or it can be a second remote fetch — the latter triggers the SSRF path in Claims 4–6. `auth_type` accepts `none`, `api_key`, `bearer_token`, `basic`, `authorization`, or `oauth2`, with `auth_value` required when auth is set; the page documents the enum but not the per-type transport behavior. `allowed_tools` / `disallowed_tools` are registration-level filters that bind every caller, distinct from per-entity MCP tool permissions.

### Claim 3: Supported specs are exactly OpenAPI 3.0.x, 3.1.x, and Swagger 2.0; each operation's `operationId` becomes the tool name and must be unique
- **Evidence**: The bold "Supported spec versions" sentence immediately after the parameter table.
- **Confidence**: emerging (explicit documented supported set and naming rule)
- **Quote**: "**Supported spec versions:** OpenAPI 3.0.x, 3.1.x, Swagger 2.0. Each operation's `operationId` becomes the tool name, so make sure they're unique."
- **Our assessment**: The version set is precise and includes Swagger 2.0, so "OpenAPI 3 only" would be wrong. The `operationId` dependency is a practical gate: a spec with missing or duplicate `operationId` values cannot produce a clean one-tool-per-operation catalog. The page says to "make sure they're unique" but does not document how a collision is resolved (overwrite, first-wins, or load error) — treat spec linting as a pre-registration check rather than something the gateway is guaranteed to catch.

### Claim 4: When `spec_path` is an `http(s)` URL, the proxy fetches it with SSRF protection on by default and rejects the request if any resolved address is not globally routable
- **Evidence**: The "Internal spec URLs (SSRF)" opening paragraph.
- **Confidence**: emerging (explicit documented default and rejection behavior; no bypass testing or code reference)
- **Quote**: "When `spec_path` is an `http://` or `https://` URL, the LiteLLM proxy fetches it with **SSRF protection** enabled by default: the hostname is resolved and the request is **rejected** if any resolved address is not globally routable (e.g. `10.x`, `192.168.x`, `127.0.0.1`), unless you allowlist the **hostname from the URL** (not the resolved IP)."
- **Our assessment**: This is the page's highest-value security claim, and its scope is narrow: it applies to the **spec fetch** when `spec_path` is a URL, not to every outbound request the gateway makes (cf. `docs-litellm-mcp-deployment.md` Claim 5 on per-tool-call MCP egress). "Any resolved address" is the safer form — a multi-A-record hostname with one private answer is rejected rather than accepted on the first public answer. The allowlist exception is keyed on the configured hostname, not the resolved IP, so it is an operator trust decision about that name, not a post-DNS IP check.

### Claim 5: The SSRF allowlist is expressed as URL-hostname entries, including port-pinned forms, with separate examples for private-DNS and loopback spec URLs
- **Evidence**: The "Typical cases" bullets under the SSRF section.
- **Confidence**: emerging (explicit documented allowlist matching forms)
- **Quote**: "- Spec URL uses `https://api.example.com/...` but DNS inside your network returns a private IP. Add `api.example.com` to the allowlist (or `api.example.com:443` if you pin the port).
- Spec URL is `http://127.0.0.1:8080/openapi.json`. Add `127.0.0.1` or `127.0.0.1:8080`."
- **Our assessment**: This settles the port question at the documentation level: both a bare host and a `host:port` form are accepted, and the example pairs the port only when the operator pins it. It does not state whether an allowlisted host bypasses DNS resolution entirely or is resolved and then exempted from the routability check; the page's wording ("unless you allowlist the hostname") suggests the allowlist is the exception to rejection, not a separate resolve-free path. Operators should read it as "this hostname is trusted even if it resolves privately," not as "this hostname is never resolved."

### Claim 6: The SSRF controls live under `litellm_settings`, not `general_settings`; validation defaults to `true`, and disabling it is a trust decision
- **Evidence**: The explicit placement sentence, the `config.yaml` sample, and the inline default/disable comment.
- **Confidence**: emerging (explicit documented placement and default)
- **Quote**: "Configure under **`litellm_settings`** in your proxy `config.yaml` (this is **not** read from `general_settings`):"
- **Our assessment**: This is a classic silent-no-op footgun: an operator who places `user_url_validation` or `user_url_allowed_hosts` under `general_settings` gets no error and no effect from the documented perspective. The page names the correct block explicitly, which is exactly the kind of placement detail a runbook should encode. `user_url_validation: true` is the default; setting it false is documented only for fully trusted URL sources, so it should be treated as a deliberate exception with a compensating network control.

### Claim 7: Tool names and descriptions default to the spec's `operationId` and description fields; UI overrides can rename/rewrite them, and a blank field keeps the spec's original
- **Evidence**: The "Step 2: Optionally Override Tool Names and Descriptions" intro and the UI bullet list.
- **Confidence**: emerging (explicit documented default and override behavior)
- **Quote**: "By default, tool names and descriptions come from the `operationId` and description fields in your spec. You can rename or rewrite them so MCP clients see something cleaner, without touching the upstream spec."
- **Our assessment**: Overrides decouple the client-visible catalog from the upstream spec without forking it, which is useful for cleanup but creates a second catalog to govern. The "leave blank to keep the original" rule means an override map is partial by design; absence is not deletion. For security review, the displayed name/description is not necessarily the upstream spec text, so trust decisions must account for both sources.

### Claim 8: Operator-written description overrides go through the same discovery guardrail scan as the spec's own text, so a guardrail can mask or hide an override too
- **Evidence**: The **Description** bullet in the UI override section, which links to the `mcp_guardrail` discovery-scan section.
- **Confidence**: emerging (explicit documented scan coverage; no example of a blocked override)
- **Quote**: "**Description** — overrides the description MCP clients see. It goes through the same [discovery guardrail scan](./mcp_guardrail#scanning-tool-descriptions-on-discovery) as the spec's text, so a guardrail can mask or hide it too"
- **Our assessment**: This extends `docs-litellm-mcp-guardrails.md` Claim 7 (discovery-time scan of tool descriptions and input-schema descriptions) to override text: the scan is not limited to upstream-supplied spec text. Operationally, an operator can write a clean description and still have the tool hidden or masked because the guardrail flags it, which makes guardrail logs the place to debug an unexpectedly missing or altered tool. It also means the override is not a way to bypass description scanning.

### Claim 9: The name/description override maps are keyed on the original `operationId`, not the prefixed exposed tool name; LiteLLM strips the server prefix before lookup
- **Evidence**: The explicit key-semantics paragraph and the `petstore_mcp` / `getPetById` example.
- **Confidence**: emerging (explicit documented key contract)
- **Quote**: "The map key is the **original `operationId`** from the spec, not the prefixed tool name. LiteLLM strips the server prefix before doing the lookup."
- **Our assessment**: This is the page's clearest config footgun. Tools are exposed as `<server>-<operationId>` (the page's example is `petstore_mcp-getPetById`), but the override key is the bare `getPetById`. An operator who copies the exposed name into the map will not match the lookup; the page does not document an error for a non-matching key, so the likely result is a silently unapplied override with the spec's name/description still served. Runbooks should validate override keys against the spec's `operationId` set, not against the gateway's advertised tool names.

### Claim 10: The UI registration path fetches the spec and loads all endpoints as tools; the API path supports create and update with the override maps
- **Evidence**: The "Or from the UI" sentence, the "From the API" create/update examples, and the before/after tool listing.
- **Confidence**: emerging (explicit documented UI/API surface)
- **Quote**: "Or from the UI: go to **MCP Servers → Add New MCP Server**, fill in the URL and spec path, and LiteLLM will fetch the spec and load all endpoints as tools."
- **Our assessment**: The UI is not merely a viewer — it performs the ingestion/fetch, so the SSRF path and the "load all endpoints" behavior apply there too. The API examples use `/v1/mcp/server` with `tool_name_to_display_name` and `tool_name_to_description`; the before/after block shows the exposed names changing from `petstore_mcp-getPetById` to `Get Pet`, confirming that overrides change the caller-visible tool name, not just the description. This is convenient but means a spec refresh plus override drift can change the client catalog without a code change.

## Concrete Artifacts

All artifacts are verbatim from the fetched page
(https://docs.litellm.ai/docs/mcp_openapi.md).

### Registering spec-backed MCP servers (`config.yaml`)

```yaml
mcp_servers:
  petstore_mcp:
    url: "https://petstore.swagger.io/v2"
    spec_path: "/path/to/openapi.json"
    auth_type: "none"

  my_api_mcp:
    url: "http://0.0.0.0:8090"
    spec_path: "/path/to/openapi.json"
    auth_type: "api_key"
    auth_value: "your-api-key-here"

  secured_api_mcp:
    url: "https://api.example.com"
    spec_path: "/path/to/openapi.json"
    auth_type: "bearer_token"
    auth_value: "your-bearer-token"
```

### Configuration parameter table (from the source)

```text
| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | Base URL of your API |
| `spec_path` | Yes | Path or URL to your OpenAPI spec (JSON or YAML) |
| `auth_type` | No | `none`, `api_key`, `bearer_token`, `basic`, `authorization`, `oauth2` |
| `auth_value` | No | Auth value (required if `auth_type` is set) |
| `description` | No | Optional description |
| `allowed_tools` | No | Allowlist of specific tools |
| `disallowed_tools` | No | Blocklist of specific tools |
```

### SSRF controls under `litellm_settings`

```yaml
litellm_settings:
  user_url_validation: true # default; set false only if you fully trust URL sources
  user_url_allowed_hosts:
    - "api.example.com"
    - "127.0.0.1"
    - "127.0.0.1:8080"
```

### Create server with tool name overrides (API)

```bash
curl -X POST http://localhost:4000/v1/mcp/server \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "petstore_mcp",
    "url": "https://petstore.swagger.io/v2",
    "spec_path": "/path/to/openapi.json",
    "tool_name_to_display_name": {
      "getPetById": "Get Pet",
      "findPetsByStatus": "List Available Pets"
    },
    "tool_name_to_description": {
      "getPetById": "Look up a pet by its ID",
      "findPetsByStatus": "Returns all pets matching a given status (available, pending, sold)"
    }
  }'
```

### Update overrides on an existing server (API)

```bash
curl -X PUT http://localhost:4000/v1/mcp/server \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "<server-id>",
    "tool_name_to_display_name": {
      "getPetById": "Get Pet"
    },
    "tool_name_to_description": {
      "getPetById": "Look up a pet by its ID"
    }
  }'
```

### Before and after overrides

```text
# Without overrides
Tool: "petstore_mcp-getPetById"
Description: "Returns a single pet"

Tool: "petstore_mcp-findPetsByStatus"
Description: "Finds Pets by status"

# After overrides
Tool: "Get Pet"
Description: "Look up a pet by its ID"

Tool: "List Available Pets"
Description: "Returns all pets matching a given status (available, pending, sold)"
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-control.md` Claim 8 — both notes treat
    tool-parameter restriction as a server-registration-level control applying
    to every caller (`allowed_params` there; `allowed_tools` /
    `disallowed_tools` here). They describe different fields but the same
    "registration-time filter binds all callers, distinct from per-entity
    permissions" shape.
- **Contradicts**: None. No existing note claims that URL-based `spec_path`
  fetches are unguarded, that the allowlist matches resolved IPs, or that
  OpenAPI ingestion is client-side. No contradiction issue filed.
- **Extends**:
  - `source-notes/docs-litellm-mcp-guardrails.md` Claim 7 — that note
    documents the discovery-time `pre_mcp_call` scan of a tool's description
    and every `description` in its input schema. This page adds that
    operator-written description overrides pass through the same scan, so the
    override path is not a scan bypass (Claim 8 here).
  - `source-notes/docs-litellm-mcp-control.md` Claim 7 — that note
    distinguishes per-entity `mcp_tool_permissions` from
    registration-level `allowed_tools`/`disallowed_tools`; this page supplies
    the OpenAPI spec-ingestion context in which those registration-level
    filters are attached to a derived server (Claim 2 here).
  - `source-notes/docs-litellm-mcp-deployment.md` Claim 5 — that note covers
    outbound MCP egress on every tool call and air-gapped guidance to register
    only in-perimeter servers. This page adds a *registration-time* fetch guard
    for `spec_path` URLs, which is a different egress moment and a different
    control (`user_url_validation` / `user_url_allowed_hosts`). It does not
    generalize to per-tool-call egress.
- **Novel**:
  - OpenAPI 3.0.x/3.1.x/Swagger 2.0 → MCP server conversion as a gateway
    capability, with each `operationId` becoming a tool.
  - The `user_url_validation` / `user_url_allowed_hosts` SSRF controls for
    `spec_path` URL fetches, including the hostname-from-URL (not resolved-IP)
    allowlist semantics and port-pinned entries.
  - The explicit `litellm_settings` (not `general_settings`) placement of those
    controls.
  - The `tool_name_to_display_name` / `tool_name_to_description` override maps
    being keyed on the original `operationId` while the exposed tool name is
    server-prefixed.
  - Operator-written description overrides going through the discovery
    guardrail scan.

## Guide Impact

- **Chapter 06 (Security and Trust) — operator-supplied URL fetching**: Add the
  spec-ingestion SSRF contract: when `spec_path` is an `http(s)` URL the
  gateway resolves and rejects non-globally-routable answers by default, and
  the allowlist matches the URL hostname (with optional port), not the resolved
  IP. Pair it with the placement warning: `user_url_validation` and
  `user_url_allowed_hosts` belong under `litellm_settings`, and putting them
  under `general_settings` is a silent no-op. Scope the advice explicitly to
  the spec fetch; do not present it as gateway-wide outbound protection.
- **Chapter 06 (Security and Trust) — tool-catalog trust**: Add spec ingestion
  as an executable supply-chain input: lint `operationId` uniqueness before
  registration, treat `allowed_tools`/`disallowed_tools` as all-caller filters,
  and account for operator-written description overrides being scanned just
  like upstream text (so guardrails can hide an operator tool too).
- **Chapter 05 (LLM Ops Reliability) — gateway configuration**: Add the
  OpenAPI→MCP registration surface to the gateway config inventory, including
  the `operationId`-vs-prefixed-name override key footgun: use the bare
  `operationId` (`getPetById`) even though the tool is advertised as
  `petstore_mcp-getPetById`, or the override will not apply. Include the
  supported spec-version set and a pre-registration spec lint check.

## Extraction Notes

- Primary source read in full from the live Docusaurus `.md` endpoint
  (`https://docs.litellm.ai/docs/mcp_openapi.md`), which exposes the page text
  without navigation chrome. Front-matter metadata reports
  `last_updated: "2026-10-31"`; `date_published` is not stated on the page.
- The page is thin (about two procedural sections plus client snippets). Claims
  are concentrated on spec ingestion, the SSRF paragraph, and override-key
  semantics; I did not manufacture extra claims from the generic FastMCP,
  Cursor, or OpenAI Responses examples, per the triage guidance.
- All quotes were checked against the `.md` source. Claim 5's quote is a
  contiguous two-bullet block with the markdown list markers preserved; Claim
  8's quote includes the inline documentation link exactly as it appears in the
  source rather than paraphrasing around it.
- Candidate handling from `miner-related-notes.md`:
  - `source-notes/docs-litellm-batches-api.md` — dismissed; batch rate limits,
    unrelated to MCP spec ingestion.
  - `source-notes/docs-litellm-completion-web-search.md` — dismissed;
    provider-native web search surface, no MCP/OpenAPI ingestion.
  - `source-notes/docs-litellm-mcp-deployment.md` — cited under Extends
    (outbound MCP egress vs registration-time spec fetch).
  - `source-notes/docs-litellm-evals-api.md` — dismissed; managed Evaluations
    API, unrelated.
  - `source-notes/docs-litellm-generate-content.md` — dismissed; Gemini native
    `generateContent` passthrough, unrelated.
  - `source-notes/docs-litellm-enterprise.md` — dismissed; enterprise
    licensing/features, unrelated.
  - `source-notes/docs-litellm-completion-input-params.md` — dismissed;
    supported-parameter gate for completions, unrelated.
  - `source-notes/docs-litellm-files-endpoints.md` — dismissed; provider
    `/files` passthrough, unrelated.
  - `source-notes/docs-litellm-bedrock-invoke.md` — dismissed; Bedrock native
    Invoke passthrough, unrelated.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` — dismissed; A2A
    session cost/iteration limits, unrelated.
- No contradiction issue filed: this page is additive to the MCP guardrail and
  deployment notes and does not oppose any existing claim.
- `confidence_overall: emerging` reflects first-party capability documentation
  with no measurements, no failure reports, and a living page that can change
  between releases — not doubt that the page states these contracts.
