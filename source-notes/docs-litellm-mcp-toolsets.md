---
source_url: https://docs.litellm.ai/docs/mcp_toolsets
source_type: docs
title: "MCP Toolsets — LiteLLM Documentation (named cross-server tool selections: stale saved tools, server-side routing, and the management API)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-11-08
last_checked: 2026-11-08
status: current
confidence_overall: emerging
issue: "#1985"
---

# MCP Toolsets (LiteLLM Docs)

> LiteLLM's implementation page for MCP Toolsets — a persisted, named selection
> of specific tools drawn from one or more MCP servers: it documents the
> tool-surface-narrowing rationale, that saved tools "remain selected even when
> they are unavailable" (labeled, not pruned), that the toolset name is resolved
> server-side as an MCP selector rather than a network URL, and a small
> management API (`GET`/`POST /v1/mcp/toolset`, `DELETE /v1/mcp/toolset/<id>`)
> that makes tool grants deployable as code. It leaves the permission-model
> binding ("the same way you assign MCP servers today") unspecified.

## Source Context

- **Type**: docs (official first-party LiteLLM vendor documentation — "MCP
  Toolsets", under MCP Gateway → MCP Servers, at
  `https://docs.litellm.ai/docs/mcp_toolsets`).
- **Author credibility**: LiteLLM (BerriAI) documenting its own gateway feature.
  Authoritative for the exposed surface (toolset concept, editor behavior,
  management endpoints, selector string) and for how its own UI treats an
  unavailable saved tool. It reports no production metrics, no incident writeup,
  and no independent verification. The page documents capability, not measured
  behavior; every claim is graded `emerging`, including the explicit
  stale-retention statement, per the Prospector's caveat.
- **Scope**: Covers the toolset definition and rationale, the create/edit UI
  (search, bulk select, hidden selections), the "saved tools remain selected"
  staleness behavior, use in the Playground, use via the Responses / Chat
  Completions `tools` list, and the list/create/delete management API. It does
  **not** cover: how toolsets attach to keys/teams at the field level, whether a
  stale tool is shown to the model or errors at call time, name-collision
  precedence, update semantics beyond the UI, or any measured reliability.
- **Sub-pages followed**: one — the linked
  [MCP Configuration Reference](https://docs.litellm.ai/docs/mcp_config_reference)
  (`#endpoint-matrix`), fetched because the toolsets page opens by deferring
  "direct-client URLs and LLM tool selectors" to it. It supplies the
  `/toolset/{toolset_name}/mcp` direct-client route, the "selectors are not
  network URLs" rule, the shared 404 lookup across server/toolset/access-group,
  and the `require_approval: "never"` semantics. Claims 10–11 and part of Claim
  9 are attributed to that sub-page explicitly.

## Extracted Claims

### Claim 1: A toolset is a named collection of specific tools drawn from one or more MCP servers; the vendor's rationale is a smaller tool surface (6 tools instead of 13+) for fewer tokens, faster responses, and less hallucination
- **Evidence**: The definition paragraph, the worked diagram caption, and the
  three "Why this matters" bullets.
- **Confidence**: emerging (vendor design rationale; no measurements of the
  token/latency/hallucination benefit)
- **Quote**: "A **Toolset** is a named collection of specific tools drawn from one or more MCP servers. Instead of giving an agent access to every tool on every server, you pick exactly which tools it needs, from whichever servers they live on, and bundle them under a single name."
- **Quote**: "Instead of 13+ tools across two servers, the agent gets 6: the ones it actually needs."
- **Quote**: "Smaller tool lists → fewer tokens, faster responses, less hallucination"
- **Our assessment**: The narrowing argument is stated as a vendor assertion, not
  a measurement. The mechanism (fewer tool schemas in context) is plausible and
  consistent with the corpus's tool-surface caution, but the page gives no
  before/after token counts, latency data, or hallucination metric — so the
  benefits are `emerging`, not `settled`. The 6-vs-13 example is illustrative
  (CircleCI + DeepWiki). This page is the implementation surface of the May
  townhall announcement (`blog-litellm-may-townhall-updates.md` Claim 5), which
  described "a single flat list" with name-scoped collisions; here the selection
  is concrete: explicit `{server_id, tool_name}` pairs (Claim 5) whose visible
  result is exactly the selected tools (Claim 2).

### Claim 2: The toolset is the model-visible tool surface — the model "will only see the tools you included in it", with access to "exactly the tools in your toolset and nothing else"
- **Evidence**: The Playground section's two closing statements, plus the API
  section that passes the toolset as an MCP `tools` entry.
- **Confidence**: emerging (explicit first-party statement about the selected
  surface; no test of the degraded/unavailable case)
- **Quote**: "The model will only see the tools you included in it."
- **Quote**: "The model now has access to exactly the tools in your toolset and nothing else."
- **Our assessment**: This is the enforcement claim that makes a toolset a
  governance primitive rather than a UI convenience: the model is offered the
  selected set, not the union of every server's catalog. The important limit is
  scope: "exactly ... nothing else" describes the *configured* selection. The
  page does not say what the model sees when a saved tool is unavailable
  (Claim 3) — whether it is offered and fails, omitted, or still callable. The
  guide should not convert "exactly the tools" into a fail-closed guarantee for
  the degraded state.

### Claim 3: Saved tools remain selected when they are unavailable; the editor labels them `server not found`, `server unreachable`, or `tool not found`, and those labels do not remove them — explicit removal is required
- **Evidence**: The "Edit a toolset" paragraph and its screenshot caption,
  immediately after the edit/save instructions.
- **Confidence**: emerging (explicit documented behavior; the operational
  consequence is not measured)
- **Quote**: "Saved tools remain selected even when they are unavailable."
- **Quote**: "The selected-tools panel labels them **server not found** when the server no longer exists, **server unreachable** when its tools cannot load, or **tool not found** when the server responds without that tool. These labels do not remove the tools from the saved selection."
- **Quote**: "Remove an entry explicitly if it no longer belongs in the toolset."
- **Our assessment**: The highest-value operational claim on the page. A named
  grant can keep referencing tools that no longer exist, and the gateway surfaces
  the drift only as a label in the editor. The three labels are also a useful
  diagnostic taxonomy: *not found* (server unregistered/renamed), *unreachable*
  (transport/upstream failure), and *tool not found* (server answered but the
  tool name is gone). This is the toolset analogue of the fail-silent stale
  `disallowed_tools` entry in `docs-litellm-mcp-linear-server.md` Claim 3, with a
  key difference: a stale deny entry leaves a *forbidden* tool callable, while a
  stale toolset entry leaves a *selected* tool pointing at a missing target. The
  page does not resolve which failure the agent experiences, so the guide must
  treat this as drift that is retained, not as a fail-closed control. Unlike tool
  pinning (`docs-litellm-mcp-control.md` Claim 9), there is no documented alert
  when the upstream drifts from the toolset selection.

### Claim 4: A toolset is addressed by name through `server_url: "litellm_proxy/mcp/<toolset-name>"` in the model's `tools` list; LiteLLM resolves it server-side, so no public URL is needed
- **Evidence**: The "Use a toolset via API" intro sentence and the three
  equivalent example blocks (Responses, Chat Completions, REST).
- **Confidence**: emerging (documented request shape)
- **Quote**: "Pass the toolset's route as the `server_url` in your tools list. LiteLLM resolves it server-side, so no public URL is needed."
- **Our assessment**: The toolset name is the routing key, and the `server_url`
  value is a selector sent to the proxy, not a URL the client fetches. The linked
  config reference makes the rule explicit: "These selectors are not network
  URLs" (Claim 11). The client still needs a gateway credential on the LLM
  request; per-server upstream credentials are handled separately. This is also
  the semantics behind the `/toolset/{name}/mcp` row in the gateway auth
  reference (`docs-litellm-gateway-auth-reference.md` Claim 1). Two gaps the page
  does not answer: collision precedence when a toolset and a server share a name,
  and whether a typo'd toolset name degrades silently like a wrong `server_label`
  (`docs-litellm-mcp-troubleshoot.md` Claim 6).

### Claim 5: Toolsets are manageable over REST as list/create/delete: `GET /v1/mcp/toolset`, `POST /v1/mcp/toolset` with `toolset_name`, `description`, and `tools[] {server_id, tool_name}`, and `DELETE /v1/mcp/toolset/{toolset_id}`
- **Evidence**: The "Manage toolsets via API" code block (three curl commands and
  the create body).
- **Confidence**: emerging (documented endpoint/body surface; no update,
  conflict, or idempotency semantics shown)
- **Quote**: (no direct quote; see Concrete Artifacts → Management API)
- **Our assessment**: This is the machine-readable surface the May townhall
  announcement lacked, and it is what makes a toolset deployable as code rather
  than dashboard-only. Read literally, the surface is incomplete for GitOps: no
  update verb is documented (edit is described only through the UI), no
  idempotency/conflict behavior is stated, and `toolset_id` (delete) is distinct
  from `toolset_name` (routing key). A rename therefore appears to be a
  delete+create with a new id — inferred, not stated. The create body identifies
  each tool by `server_id` + `tool_name`, which strongly implies the stored
  selection is by upstream identity, but the page does not say whether
  `tool_name` here is the prefixed or unprefixed form documented in
  `docs-litellm-mcp-rest-api.md` Claims 3–5. The corpus's toolset-collision
  guarantee from `blog-litellm-may-townhall-updates.md` Claim 5 ("name-scoped")
  is not restated here; this page disambiguates by `server_id` at config time
  instead.

### Claim 6: Toolsets are assignable to keys and teams "the same way you assign MCP servers today", but the page never states whether that is a distinct toolset field or the existing `mcp_servers` grant list
- **Evidence**: The third "Why this matters" bullet. There is no permission
  section on the page, and the create body contains no grant/entitlement fields.
- **Confidence**: emerging (one-line assertion; mechanism unspecified)
- **Quote**: "Assign to keys and teams the same way you assign MCP servers today"
- **Our assessment**: This is the most important gap in the page and a direct
  conflation risk. The corpus documents a six-level permission model over
  `mcp_servers` and `mcp_tool_permissions`
  (`docs-litellm-mcp-control.md` Claim 1, Claim 7), but nothing there names a
  toolset grant. The page also does not say whether granting a toolset implies
  access to its member servers, or whether the member servers must be granted
  separately. Operators must not infer either direction; verify the actual field
  against the live API/dashboard. For the guide, "which tools are in the grant"
  (the toolset) and "may access the server" (the permission model) must stay
  distinct, which is exactly the distinction the Prospector flagged.

### Claim 7: Search/selection state is not the same as the saved selection — hidden tools stay selected, and "Clear all" removes the entire selection including hidden tools
- **Evidence**: The "Review the selection" step (step 6).
- **Confidence**: emerging (explicit UI behavior)
- **Quote**: "**Your Toolset** lists every selected tool, including tools hidden by the current search. Changing or clearing the search keeps those selections. Click a selected tool to remove it, or **Clear all** to remove the entire selection, including hidden tools."
- **Our assessment**: A review hazard for large cross-server toolsets: the
  visible screen can omit tools that are still in the grant. This is editor
  behavior, not API behavior — the management API (Claim 5) takes an explicit
  list — so the safe review path is to read the saved toolset, not to trust what
  the search view shows. It belongs in the Ch06 "what you approve is what you
  grant" discussion rather than in the request-time enforcement layer.

### Claim 8: Bulk-selection actions apply only to tools that have loaded, so a partial server load silently changes what "Select all matching" and a server checkbox select
- **Evidence**: The paragraph after the search instructions (step 5).
- **Confidence**: emerging (explicit UI behavior; the consequence is our
  inference)
- **Quote**: "These actions apply to tools that have loaded, so wait for the loading indicator to finish to include every server."
- **Our assessment**: The same click yields a different grant depending on load
  timing. The page's only mitigation is a human instruction to wait. For
  automation, this argues for the management API (Claim 5) with an explicit tool
  list rather than bulk UI selection, and for verifying the saved selection after
  edits (Claim 7). It is a small but real "the UI state is not the config state"
  failure class.

### Claim 9: The toolsets page's API examples set `require_approval: "never"`; the linked config reference states that this "enables execution of model-selected tools"
- **Evidence**: All three example payloads on the toolsets page (`tools` entry
  with `"require_approval": "never"`), plus the endpoint matrix on the linked MCP
  Configuration Reference.
- **Confidence**: emerging (documented flag semantics; the page does not
  recommend or discuss approval policy)
- **Quote**: 'Responses / Chat Completions output; require_approval: "never" enables execution of model-selected tools'
- **Our assessment**: `require_approval` is a separate control from the toolset
  selection. The toolsets page presents `"never"` in every copy-paste example,
  including a toolset containing `run_pipeline` — a write-capable tool. The page
  does not state the default or recommend `"never"`, so this is not evidence that
  auto-approval is the default; it is a copy-paste hazard. The guide should say
  the toolset grant and the approval policy are independent and that the
  documented example opts out of per-call approval. (Attribution: quote and
  semantics are from the linked MCP Configuration Reference; the example values
  are from the toolsets page.)

### Claim 10: Direct MCP clients reach a toolset at `/toolset/{toolset_name}/mcp` over streamable-HTTP JSON-RPC, authenticated with `x-litellm-api-key`, and see exactly the tools in that toolset
- **Evidence**: The endpoint matrix on the linked MCP Configuration Reference
  (`/toolset/{toolset_name}/mcp` row: purpose, auth header, permission scope,
  response scope).
- **Confidence**: emerging (documented vendor route; no measured behavior)
- **Quote**: "A direct MCP client should see exactly the tools in a toolset"
- **Quote**: "The named toolset"
- **Our assessment**: This makes the toolset a first-class MCP surface, not only
  an LLM-side selector: a direct MCP client can be pointed at
  `/toolset/<name>/mcp` with a LiteLLM key and gets the same narrowed catalog.
  This corroborates the `/toolset/{name}/mcp` row already recorded in
  `docs-litellm-gateway-auth-reference.md` Claim 1, and it is the route whose
  semantics that note said this page supplies. Note the auth consequence from
  that note: this route is an MCP ASGI route, so it does not parse the vendor
  auth aliases or `x-litellm-tags` — use `x-litellm-api-key` (or the standard
  `Authorization` form the matrix shows).

### Claim 11: `litellm_proxy/mcp/<name>` selectors are literal sentinels, never network URLs, and a 404 on `/{server_name}/mcp` means the server name, toolset, or access group does not exist — so toolsets share the server-name lookup namespace
- **Evidence**: The "Selectors" prose and expected-result paragraph on the
  linked MCP Configuration Reference, plus the endpoint matrix rows for
  `/{server_name}/mcp` and `server_url: "litellm_proxy"`.
- **Confidence**: emerging (documented selector/lookup behavior; precedence not
  stated)
- **Quote**: "For a server or toolset, use litellm_proxy/mcp/<name>. These selectors are not network URLs."
- **Quote**: "A 404 on /{server_name}/mcp means the server name, toolset, or access group does not exist"
- **Our assessment**: The shared lookup is genuinely useful (one name space for
  servers, toolsets, and access groups in a direct-client path) but it is also a
  collision surface the pages do not resolve: if a server alias and a toolset
  share a name, which one wins on `/<name>/mcp`? And is the explicit
  `/toolset/<name>/mcp` route an unambiguous escape hatch? The config reference
  says `/{server_name}/mcp` grants only "The named server(s), toolset, or access
  group", so a caller may be reaching a toolset without using the toolset route.
  The guide should treat toolset names as part of the MCP name namespace and
  require a uniqueness check before rollout.

## Concrete Artifacts

All artifacts are from the fetched pages. On the toolsets page the code blocks
and list markers were collapsed by HTML extraction; line breaks, indentation, and
list markers were restored at structural boundaries only, with no wording
changes. Quotes and selector prose are character-for-character.

### Toolset concept and rationale (source: "How it works")

```text
Agent sees exactly 6 tools, nothing more.

Instead of 13+ tools across two servers, the agent gets 6: the ones it actually needs.

Why this matters:
- Smaller tool lists → fewer tokens, faster responses, less hallucination
- Combine tools from GitHub + Linear + CircleCI into one named grant
- Assign to keys and teams the same way you assign MCP servers today
```

### Responses API example (source: "Use a toolset via API → Responses API")

```python
import openai

client = openai.OpenAI(
    api_key="your-litellm-key",
    base_url="http://your-proxy/v1",
)

response = client.responses.create(
    model="gpt-6.1-sol",
    input="What CI/CD tools do you have?",
    tools=[
        {
            "type": "mcp",
            "server_label": "devtooling-prod",
            "server_url": "litellm_proxy/mcp/devtooling-prod",
            "require_approval": "never",
        }
    ],
)

print(response.output_text)
```

The Chat Completions example uses the identical `tools` entry and
`require_approval: "never"`; the REST example sends the same JSON to
`/v1/responses`.

### Management API (source: "Manage toolsets via API")

```bash
# List all toolsets
curl http://your-proxy/v1/mcp/toolset \
  -H "Authorization: Bearer your-litellm-key"

# Create a toolset
curl -X POST http://your-proxy/v1/mcp/toolset \
  -H "Authorization: Bearer your-litellm-key" \
  -H "Content-Type: application/json" \
  -d '{
    "toolset_name": "devtooling-prod",
    "description": "CircleCI + DeepWiki tools for the dev team",
    "tools": [
      {"server_id": "<circleci-server-id>", "tool_name": "get_build_failure_logs"},
      {"server_id": "<circleci-server-id>", "tool_name": "run_pipeline"},
      {"server_id": "<deepwiki-server-id>", "tool_name": "read_wiki_structure"}
    ]
  }'

# Delete a toolset
curl -X DELETE http://your-proxy/v1/mcp/toolset/<toolset_id> \
  -H "Authorization: Bearer your-litellm-key"
```

### Direct-client toolset route (source: linked MCP Configuration Reference → endpoint matrix)

```text
/toolset/{toolset_name}/mcp        MCP JSON-RPC (streamable HTTP)
  A direct MCP client should see exactly the tools in a toolset
  x-litellm-api-key: Bearer sk-...
  The named toolset
  Same JSON-RPC responses, scoped to the toolset
```

### Selector semantics (source: linked MCP Configuration Reference)

```text
Use litellm_proxy inside requests sent to LiteLLM's LLM API. The accepted aggregate form
litellm_proxy/mcp has the same purpose; standardize new examples on litellm_proxy. For a
server or toolset, use litellm_proxy/mcp/<name>. These selectors are not network URLs.
```

### Shared 404 lookup (source: linked MCP Configuration Reference)

```text
A 401 means the gateway credential is wrong; a 404 on /{server_name}/mcp means the
server name, toolset, or access group does not exist
```

## Cross-References

**Candidates from `miner-related-notes.md`** (read first; every listed path is
cited or explicitly dismissed):

- `source-notes/docs-litellm-mcp-linear-server.md` — **cited** (Extends; see
  Claim 3 contrast: stale `disallowed_tools` entry vs stale saved toolset entry).
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  accounting at `POST /v1/batches`; no tool-selection, MCP-route, or grant
  content.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**:
  provider-native web-search support matrix; unrelated to MCP tool selection.
- `source-notes/docs-litellm-mcp-deployment.md` — **cited** (adjacent; see
  Claim 11 naming namespace below, citing its Claim 11 hyphen rule).
- `source-notes/docs-litellm-mcp-zero-trust.md` — **dismissed**: outbound
  gateway→MCP JWT attestation; a different layer (how the upstream verifies the
  caller), not which tools are selected.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: stored-completion
  evaluation/grading API; unrelated.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` passthrough; unrelated.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: Enterprise license
  tiers/features; no toolset or MCP selection mechanics.
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**:
  completion parameter support gate; unrelated.
- `source-notes/docs-litellm-files-endpoints.md` — **dismissed**: provider
  `/files` passthrough; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 1** — records
    `/toolset/{name}/mcp` as an MCP ASGI route that bypasses the standard FastAPI
    auth dependency and ignores vendor auth aliases and `x-litellm-tags`. This
    note supplies the semantics of that route (Claim 10 here: exact toolset
    catalog, `x-litellm-api-key`) and the management routes (`/v1/mcp/toolset`,
    Claim 5 here) that the auth note says accept the full header set. Cite the
    auth consequence together: the toolset ASGI route is authenticated but its
    header parsing is narrower than the management API.
  - `source-notes/docs-litellm-mcp-troubleshoot.md` **Claim 4** and its
    **Concrete Artifacts → "Two 404s, two owners"** section — the captured alias
    404 body is `{"detail":"MCP server, toolset, or access group 'nosuchserver'
    not found"}`, independently confirming that "toolset" is part of the same
    lookup as servers and access groups (Claim 11 here). Cited by section name
    because the toolset wording lives in the artifact, not the numbered claim
    quote.
  - `source-notes/blog-litellm-may-townhall-updates.md` **Claim 5** — the May
    townhall announced toolsets as "a single flat list" with name-scoped
    collision safety; this page is consistent with that announcement and supplies
    the implementation detail (explicit `{server_id, tool_name}` selection,
    persisted staleness, management API). No disagreement.
- **Extends**:
  - `source-notes/blog-litellm-may-townhall-updates.md` **Claim 5** — announcement
    → implementation surface. The townhall note is conceptual only; this note adds
    the lifecycle (stale saved tools, explicit removal), the routing key
    (`litellm_proxy/mcp/<name>` and `/toolset/<name>/mcp`), and the REST
    management surface.
  - `source-notes/docs-litellm-mcp-control.md` **Claim 7** — establishes that
    server-registration `allowed_tools`/`disallowed_tools` bind every caller and
    that per-entity `mcp_tool_permissions` is a separate tool-name layer. A
    toolset is a third tool-selection primitive (a named, persisted selection
    spanning servers) that the control page does not document. Keep the three
    distinct in the guide: server ACLs (bind all callers), per-entity tool
    permissions (intersected per caller), toolset (a named selectable surface).
  - `source-notes/docs-litellm-mcp-control.md` **Claim 9** — tool pinning freezes
    descriptions/schemas and "alerts when the upstream drifts from the pin". This
    page documents the opposite operational property for toolsets: stale saved
    tools are retained and labeled, with no documented alert. They are
    complementary controls, not substitutes — pin for drift detection, toolset
    for surface selection, and verify both after upstream changes.
  - `source-notes/docs-litellm-mcp-rest-api.md` **Claims 3–5** — the model-visible
    tool-name grammar is a server prefix plus separator (`{server_prefix}
    {separator}{upstream_tool_name}`, default `-`), while the toolset management
    body selects by `server_id` + `tool_name`. The page does not state whether
    `tool_name` is the prefixed or unprefixed form; per that note's Claim 8, the
    single-server listing returns **unprefixed** upstream names. Flag as an
    unresolved config-format question before writing a toolset by API.
  - `source-notes/docs-litellm-mcp-deployment.md` **Claim 11** — MCP server names
    may not contain hyphens (the proxy rejects `mcp_servers` keys like
    `internal-db` at startup). Because toolset names resolve through the same
    `/{server_name}/mcp` lookup (Claim 11 here), operators should assume the same
    name hygiene applies; the toolsets and config-reference pages do not state
    whether the hyphen rule covers toolset names. Flag the gap rather than
    generalise.
  - `source-notes/docs-litellm-mcp-linear-server.md` **Claim 3** — a stale
    `disallowed_tools` entry "fails silently and leaves that tool callable" on a
    runtime-mutable upstream. This note's Claim 3 is the selected-tool analogue:
    a stale toolset entry is retained and only labeled. Together they argue that
    name-based MCP grants (allow, deny, or select) drift when the upstream
    catalog changes, and none of them is self-healing.
  - `source-notes/docs-litellm-mcp-troubleshoot.md` **Claim 6** — a wrong
    `server_label` in `/v1/responses` or `/v1/chat/completions` returns HTTP 200
    and silently answers without tools. Since a toolset is selected by name in
    the same request path (Claim 4 here), the same silent-degradation risk
    applies to a mistyped toolset name; assert tool-use items, not just HTTP
    success.
- **Contradicts**: No contradiction issue filed. The only near-tension is
  mechanism contrast, not claim opposition: toolsets retain stale selections with
  no alert (Claim 3 here) while tool pinning alerts on drift
  (`docs-litellm-mcp-control.md` Claim 9). They are different controls with
  different failure modes, and the toolsets page never claims drift detection.
  Also checked `CONTRADICTIONS.md` (no entries) and open `contradiction`-labeled
  issues — the two LiteLLM MCP-related ones are #2039 (semantic tool-filter
  fail-open vs fail-closed) and #2079 (OAuth identity discriminator), neither of
  which covers toolsets.
- **Novel** (first appearances in the corpus):
  1. A persisted, named cross-server tool **selection** as a first-class grant
     object (beyond the May townhall's conceptual announcement).
  2. The stale-saved-tool lifecycle: retained references labeled `server not
     found` / `server unreachable` / `tool not found`, with explicit removal
     required and no documented alert.
  3. The toolset management API (`GET`/`POST /v1/mcp/toolset`, `DELETE
     /v1/mcp/toolset/<id>`) with `{server_id, tool_name}` selection.
  4. Server-side name resolution of a toolset selector
     (`litellm_proxy/mcp/<name>`), and the direct-client
     `/toolset/{toolset_name}/mcp` route.
  5. The shared server/toolset/access-group name lookup and its unresolved
     collision precedence.
  6. The UI selection semantics (hidden selections persist; bulk actions apply
     only to loaded tools).
  7. The permission-model gap: "assign ... the same way you assign MCP servers"
     with no documented toolset grant field.

## Guide Impact

- **Chapter 06 — "Skills ship a tool allowlist at authoring time"
  (`guide/06-security-and-trust.md:63`)**: Add the toolset as the gateway-side
  counterpart to a skill's authoring-time allowlist (Claim 1). State the
  drift caveat from Claim 3: the allowlist is persisted, not re-derived, so a
  server rename or unregister leaves stale entries labeled but still selected.
  Pair it with pinning (`docs-litellm-mcp-control.md` Claim 9) for drift
  detection, because the page documents no alert for a stale toolset.
- **Chapter 06 — "Function-calling authorization"
  (`guide/06-security-and-trust.md:265`)**: Add that a function/tool grant can
  outlive its target (Claim 3). The page labels `server not found` /
  `server unreachable` / `tool not found` and requires explicit removal; the
  guide should say to include toolset references in the post-change
  verification, and must not assume the gateway fails closed — the page is silent
  on whether the agent sees a stale tool or errors at call time.
- **Chapter 06 — "An agent gateway's default is full access"
  (`guide/06-security-and-trust.md:316`)**: Add the toolset as the narrowing
  primitive (Claims 1–2) and flag the grant-binding gap (Claim 6): "assign to
  keys and teams the same way you assign MCP servers today" is not a field-level
  contract, so the guide should tell operators to verify whether a toolset is a
  distinct grant or piggybacks on `mcp_servers`, and to keep "may access the
  server" separate from "which tools are in the grant."
- **Chapter 03 — "Structured tool contracts over free-form interfaces"
  (`guide/03-runbooks-and-agents.md:159`)**: Add the management-API pattern
  (Claim 5): provision a toolset from an explicit `{server_id, tool_name}` list
  rather than via bulk UI selection (Claim 8), and read back the saved selection
  (Claim 7) because the visible search state can hide selected tools. This is
  the concrete "tool contracts as code" implementation for MCP tool surfaces.
- **Chapter 03 — "The emerging agent control plane"
  (`guide/03-runbooks-and-agents.md:332`)**: Add "select the tool surface" as a
  control-plane verb alongside register/authorize: a toolset is a named,
  cross-server selection that can be attached to keys and teams and reached
  either through the LLM tool list or a direct `/toolset/<name>/mcp` route
  (Claims 4, 10).
- **Chapter 05 — "Config changes need their own three-property test"
  (`guide/05-llm-ops-reliability.md:197`)**: Add a toolset verification step to
  MCP config changes: after unregistering or renaming a server, check every
  toolset that referenced it (Claim 3), and check the `/<name>/mcp` 404 lookup
  because toolset names share the server/access-group namespace (Claim 11). Note
  the unresolved update/idempotency semantics of the management API (Claim 5)
  as a GitOps precondition to verify before treating toolsets as declarative
  config.

## Extraction Notes

- Source read in full via HTTP fetch of the canonical page
  (`https://docs.litellm.ai/docs/mcp_toolsets`, HTTP 200, no paywall) on
  2026-11-08. All `Quote` fields were verified character-for-character against
  the rendered page text with a custom HTML text extractor; no quote was spliced
  from non-adjacent sentences. Bold markers (`**...**`) inside two quotes are
  preserved from the source rendering, matching the convention of sibling
  LiteLLM doc notes.
- One linked sub-page was followed, per MINER §1: the MCP Configuration
  Reference (`https://docs.litellm.ai/docs/mcp_config_reference`), because the
  toolsets page explicitly defers direct-client URLs and LLM tool selectors to
  it. Claims 10–11 and the approval-semantics part of Claim 9 are attributed to
  that sub-page in the claim text; everything else is from the toolsets page.
  Other linked pages (MCP Control, MCP OAuth, troubleshooting) were not re-mined
  because the corpus already has notes for them; they are cross-referenced
  instead.
- The toolsets page's code blocks and list markers were collapsed by the site's
  HTML output. Line breaks, indentation, and list markers were restored at
  structural boundaries only; wording, field names, and values are unchanged.
  This is noted above the artifacts.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or explicitly dismissed above. Additional
  cross-references (`blog-litellm-may-townhall-updates.md`,
  `docs-litellm-mcp-control.md`, `docs-litellm-gateway-auth-reference.md`,
  `docs-litellm-mcp-rest-api.md`, `docs-litellm-mcp-troubleshoot.md`) came from
  the Prospector triage, the source page's own links, and a `source-notes/`
  search. Every cited `Claim N` was re-read in its note per MINER §4b before
  writing; claim numbers and quoted fragments were confirmed. Where material
  lived in a non-claim artifact (troubleshoot's captured 404 body), it is cited
  by section name, not a fictional claim number.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM MCP docs
  notes. The page states some behavior explicitly — most importantly the
  stale-retention rule (Claim 3) and the exact-surface rule (Claim 2) — but it
  is first-party capability documentation with no measured consequence, no
  incident data, and no independent verification, and the Prospector explicitly
  capped the staleness claim at `emerging`.
- No contradiction issue filed: the one near-tension (toolset staleness vs
  pinning drift alerts) is a mechanism contrast, not a claim conflict, per MINER
  §4a's "when NOT to file" criterion. `CONTRADICTIONS.md` has no entries and no
  open contradiction issue covers toolsets.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited —
  both are derived indexes rebuilt after merge.
