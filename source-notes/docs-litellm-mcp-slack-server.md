---
source_url: https://docs.litellm.ai/docs/mcp_servers/slack
source_type: docs
title: "Slack MCP server — LiteLLM Documentation (hosted remote MCP through the gateway: upstream app provisioning, per-user identity without DCR, and the per-app toggle fail-silent)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-11-08
last_checked: 2026-11-08
status: current
confidence_overall: emerging
issue: "#1983"
---

# Slack MCP server (LiteLLM Docs)

> LiteLLM's integration page for exposing Slack's vendor-hosted remote MCP
> server through the MCP Gateway: Slack has no dynamic client registration, so
> the operator must create a Slack app and supply explicit client credentials
> while identity stays per-user; the upstream `/mcp` endpoint sits behind a
> per-app toggle and a reinstall-to-apply-scopes rule that both fail silently
> *outside* the gateway's visibility, so "OAuth worked but the tool list is
> empty or 403" is often an upstream-provisioning fault, not a LiteLLM
> permission fault.

## Source Context

- **Type**: docs (official first-party LiteLLM vendor documentation — "Slack MCP
  server", under MCP Gateway → MCP Servers, at
  `https://docs.litellm.ai/docs/mcp_servers/slack`).
- **Author credibility**: LiteLLM (BerriAI) documenting its own gateway against
  Slack's hosted MCP server. Authoritative for the exposed config surface
  (fields, endpoint URLs, auth mode, UI/tab names, scopes, tool-name prefixing)
  and for how LiteLLM interprets the upstream's identity. It reports no
  production metrics, no incident writeup, and no independent verification. The
  page documents capability, not measured behavior; every claim is graded
  `emerging`.
- **Scope**: Covers why to use Slack's hosted MCP server, Slack's OAuth app
  requirements (redirect URL, user-token scopes, the per-app MCP toggle,
  reinstall), gateway registration (UI and `config.yaml`), connecting from
  Claude Desktop / Cursor / Claude Code, the runtime-published tool catalog, the
  scope→capability mapping, `object_permission` / `mcp_rpm_limit`, the
  `x-litellm-api-key` vs `Authorization` split, and the stacked upstream rate
  limits. It restates gateway mechanics documented in depth elsewhere (OAuth
  flows, access control, tool naming, debug headers); this note extracts only
  the upstream-integration delta and treats the rest as corroboration.
- **Sub-pages followed**: none (only the canonical page was fetched). The page
  defers its mechanics to the sibling MCP OAuth, MCP Control, MCP REST API (tool
  naming), and MCP Troubleshooting pages; the corresponding notes in this corpus
  are cross-referenced below rather than re-mined.

## Extracted Claims

### Claim 1: Slack's hosted MCP endpoint sits behind a per-app toggle; when it is off, OAuth still succeeds and the tool list comes back empty or 403, which mimics a gateway permission failure
- **Evidence**: The warning callout under "Step 2: Enable MCP (Agents & AI
  Apps)", which states the failure output explicitly.
- **Confidence**: emerging (explicit first-party behavioral statement; no
  observed incident)
- **Quote**: "If you leave it off, OAuth still succeeds and the tool list comes back empty or 403, which reads like a LiteLLM permissions problem when it is not."
- **Our assessment**: This is the highest-value material on the page: a
  fail-silent *upstream* provisioning fault that lands where gateway operators
  look first. `docs-litellm-mcp-troubleshoot.md` Claim 1 already partitions the
  symptom space by status line — 401/403/404/405/406 come from LiteLLM before
  the upstream call, while an empty tool list means the upstream hop failed —
  but it has no category for "the upstream answered, but the upstream's own app
  configuration disabled the endpoint." The guide's runbook should therefore
  check the Slack app toggle *before* touching `allowed_tools`,
  `object_permission`, or `mcp_tool_permissions`, because a gateway-side
  misconfiguration cannot produce "OAuth succeeded, zero tools" against a
  correctly configured upstream.

### Claim 2: Adding user-token scopes does not take effect until the app is installed or reinstalled to the workspace
- **Evidence**: The final numbered step of "Step 2: Enable MCP (Agents & AI
  Apps)", immediately after enabling the toggle.
- **Confidence**: emerging (explicit first-party instruction; the failure
  symptom is our inference from the surrounding text)
- **Quote**: "Install or reinstall the app to the workspace so the new scopes take effect."
- **Our assessment**: A second upstream-side fail-silent in the same class as
  Claim 1. The page frames reinstall as the step that makes added scopes
  effective, which means a scope edit in the Slack app settings is not live
  until the app is reinstalled — the gateway sees the old consent even though
  the operator "already added `chat:write`." The diagnostic implication: when a
  specific tool fails authorization (or is absent) after a scope change, verify
  the install step before auditing the gateway. This is a provisioning state the
  gateway cannot observe, so it belongs in the runbook as an upstream check, not
  a gateway control.

### Claim 3: Explicit client credentials do not imply machine-to-machine identity — Slack requires an operator-created app with `client_id`/`client_secret` (no dynamic client registration) yet stays per-user because `oauth2_flow: authorization_code` selects the interactive flow; `m2m-client-credentials` is the debug-header signal of a shared-identity config
- **Evidence**: The Authentication section, the info callout before Step 1, the
  Step 3 `config.yaml` (client credentials + `oauth2_flow: authorization_code`),
  the "Key features" per-user bullet, and the closing debug-header sentence.
- **Confidence**: emerging (explicit documented behavior; no measured
  attribution audit)
- **Quote**: "Slack does not support dynamic client registration, so you create a Slack app and give LiteLLM its client credentials."
- **Quote**: "Slack only permits MCP on internal apps and directory-published apps, so an app built in your own workspace qualifies."
- **Quote**: "Per-user auth, so every tool call runs as the signed-in person and only sees what they can already see in Slack"
- **Quote**: "`m2m-client-credentials` means a `token_url` is set and every caller shares one identity."
- **Our assessment**: This is the sharpest finding on the page and it refines a
  rule the corpus stated too broadly. `docs-litellm-mcp-linear-server.md` Claim 5
  presents *any* of `client_id`/`client_secret`/`token_url` as switching the
  server to a shared M2M identity. Slack is a counterexample to the
  `client_id`/`client_secret` clauses: it cannot use DCR, so client credentials
  are mandatory, and per-user identity survives because
  `oauth2_flow: authorization_code` selects the interactive flow. The
  operationally correct discriminator is the **flow**, not the presence of a
  token endpoint: `oauth2_flow: client_credentials` (no interactive flow) ⇒
  shared M2M identity; static client credentials with
  `oauth2_flow: authorization_code` ⇒ per-user, whether or not a `token_url` is
  configured. A `token_url` is normal for an authorization-code flow that
  exchanges its own code — `docs-litellm-mcp-oauth.md`'s "Static OAuth client
  config.yaml" artifact shows exactly that: a per-user `authorization_code`
  server with `client_id`, `client_secret`, and `token_url` all set. The page's
  `m2m-client-credentials` debug-header sentence ("a `token_url` is set") is
  therefore a confirming signal of a shared-identity config, not a logical
  discriminator to invert; the header name itself names the grant. This is filed
  as contradiction **#2079** (recommended verdict: accepted-B / scope
  refinement) rather than resolved unilaterally here. The app-visibility
  constraint (internal or directory-published only) is also a provisioning
  boundary: an app that is neither cannot expose `/mcp` at all.

### Claim 4: Tool surface is scope-driven, not endpoint-driven — the same Slack server gives a read-only or a full read/write surface depending on the user-token scopes granted at consent
- **Evidence**: The "Key features" first bullet and the "OAuth scopes by
  capability" table.
- **Confidence**: emerging (documented design and mapping)
- **Quote**: "Tool surface depends on the OAuth scopes you grant, so a read-only rollout and a full read/write rollout use the same server with different consent"
- **Our assessment**: This is the clearest counterpoint to the
  endpoint-narrowing pattern in `docs-litellm-mcp-linear-server.md` Claim 2,
  where Linear offers a dedicated `/mcp/readonly` endpoint and the guide's
  ordering is endpoint > consent-scope > deny list. Slack has no read-only
  endpoint, so consent scopes are the *primary* least-privilege mechanism, not
  the second choice. That matters as a general rule: whether least privilege can
  be an endpoint swap or must be a consent-scope grant is an upstream property,
  not a gateway feature. The page also notes tools are published at runtime
  through `tools/list` and that the live MCP Tools tab is the source of truth,
  corroborating the runtime-mutable-catalog warning in
  `docs-litellm-mcp-linear-server.md` Claim 4.

### Claim 5: Slack applies per-tool rate limits matching the equivalent Web API method's tier, and those limits stack on top of LiteLLM's `mcp_rpm_limit`
- **Evidence**: The closing sentence of the "OAuth scopes by capability"
  section.
- **Confidence**: emerging (explicit first-party statement)
- **Quote**: "Rate limits are applied per tool, matching the tier of the equivalent Web API method, and stack on top of anything you configure in LiteLLM."
- **Our assessment**: A minor but operationally important capacity fact:
  configuring `mcp_rpm_limit` does not raise the effective ceiling, because the
  upstream's per-tool tier still applies underneath. It qualifies
  `docs-litellm-mcp-control.md` Claim 11 (gateway-side per-server/entity rate
  limiting): the gateway limit is an *additional* ceiling, not the binding one.
  For capacity planning, the effective rate is `min(gateway limit, upstream
  per-tool tier)`, and the upstream tier is not configurable from LiteLLM.

## Concrete Artifacts

All artifacts are from the fetched page
(https://docs.litellm.ai/docs/mcp_servers/slack). YAML/JSON blocks were
collapsed to single lines by HTML extraction; line breaks/indentation were
restored at YAML/JSON boundaries only, with no wording changes.

### Remote MCP endpoint (source: "Endpoint")

```text
https://mcp.slack.com/mcp
```

### Gateway registration — config.yaml (source: "Step 3: Register the server in LiteLLM")

```yaml
mcp_servers:
  slack_mcp:
    url: "https://mcp.slack.com/mcp"
    transport: "http"
    description: "Slack workspace search, channels, and messaging"
    auth_type: oauth2
    oauth2_flow: authorization_code
    client_id: os.environ/SLACK_OAUTH_CLIENT_ID
    client_secret: os.environ/SLACK_OAUTH_CLIENT_SECRET
```

The page adds: "`oauth2_flow: authorization_code` selects the interactive
per-user flow and is required; the proxy refuses to start on an `auth_type:
oauth2` server that omits it." and "Storing MCP servers also needs
`store_model_in_db: true`, covered in Prerequisites."

### Gateway registration — UI fields (source: "Step 3 → LiteLLM UI")

```text
Server Name            slack_mcp
Transport              HTTP
Server URL             https://mcp.slack.com/mcp
Authentication         OAuth
OAuth flow type        Interactive (PKCE)
Client ID / Secret     From Step 1
```

### Agent connection — Claude Desktop / Cursor (source: "Step 4: Connect from an agent")

```json
{
  "mcpServers": {
    "slack": {
      "url": "http://localhost:4000/slack_mcp/mcp",
      "headers": {
        "x-litellm-api-key": "Bearer sk-<your-litellm-api-key>"
      }
    }
  }
}
```

### Agent connection — Claude Code (source: "Step 4: Connect from an agent")

```bash
claude mcp add --transport http slack http://localhost:4000/slack_mcp/mcp \
  --header "x-litellm-api-key: Bearer $LITELLM_API_KEY"
```

### Tool catalog (source: "Tools provided", transcribed from the table)

```text
Area       Tools
Search     search_public, search_public_and_private, search_channels, search_users
Read       read_channel, read_thread, read_user_profile
Messaging  send_message, send_message_draft, schedule_message
Canvases   create_canvas, read_canvas, update_canvas
```

The page caveats: "Slack publishes its tool definitions at runtime through
`tools/list`, so names and fields can change without notice." Canvas tools
require a paid Slack plan, and tool names are prefixed (`slack_mcp-search_public`).

### OAuth scopes by capability (source: "Tools provided → OAuth scopes by capability")

```text
Capability                    User token scopes (examples)
Search messages and files     search:read
Read public channels          channels:read, channels:history
Read private channels         groups:read, groups:history
Read direct messages          im:history
Post messages                 chat:write
Resolve user profiles         users:read
Read files                    files:read
```

The page adds: "Slack documents the full list in OAuth scopes. Rate limits are
applied per tool, matching the tier of the equivalent Web API method, and stack
on top of anything you configure in LiteLLM."

## Cross-References

**Candidates from `miner-related-notes.md`** (read first; every listed path is
cited or explicitly dismissed):

- `source-notes/docs-litellm-mcp-linear-server.md` — **cited**: the direct
  sibling integration. Claim 2's dedicated `/mcp/readonly` endpoint is the
  endpoint-narrowing alternative Slack does not offer (Claim 4 here); Claim 5's
  "do not set client credentials" rule is the one this page refines (Claim 3
  here) and is Side A of contradiction #2079; Claim 4's runtime-published tool
  catalog is corroborated by this page.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  accounting at `POST /v1/batches`; no MCP server, OAuth, or app-provisioning
  content.
- `source-notes/docs-litellm-mcp-deployment.md` — **cited** (Extends): Claim 5
  establishes that registering an external MCP URL makes the gateway issue
  outbound requests on every tool call; `https://mcp.slack.com/mcp` is another
  concrete vendor-hosted upstream, and its provisioning state (Claims 1–3 here)
  is outside the gateway's control.
- `source-notes/docs-litellm-mcp-zero-trust.md` — **cited** (Adjacent): Claim 5
  (outbound JWT `sub` defaults to the internal `user_id` unless verify+re-sign
  rebuilds it) and Claim 7 (with no identity configured the `sub` degrades to
  the shared literal `"litellm-proxy"`) cover what the MCP *server* is told
  about the caller. This page's Claim 3 covers which *upstream credential* acts
  against Slack. Both must be checked to claim end-to-end per-user attribution;
  neither substitutes for the other.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: Enterprise license
  tiers/features; no MCP integration, OAuth, or Slack content.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**:
  provider-native web-search support matrix; unrelated.
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**:
  completion parameter support gate; unrelated to MCP auth or provisioning.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: Evaluations API
  stored-completion grading; unrelated.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` passthrough fields; unrelated.
- `source-notes/docs-litellm-mcp-aws-sigv4.md` — **dismissed**: a different MCP
  outbound `auth_type` (SigV4 for AgentCore); no OAuth identity, upstream app
  provisioning, or scope content. (It is a hosted-upstream precedent, but the
  auth mechanism does not intersect this page.)

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 1** — every
    `auth_type: oauth2` server must declare `oauth2_flow` or the proxy refuses
    to start; this page's Concrete Artifacts repeats that requirement for
    `slack_mcp`.
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 2** — interactive-flow
    tokens are stored per user under the calling key's `user_id`; that is the
    data-model reason this page's Claim 3 can keep per-user identity even with
    static client credentials.
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 15** — `SAME_AS_LITELLM_KEY`
    and `m2m-client-credentials` diagnostics; this page restates both. Its
    `m2m-client-credentials` sentence ("a `token_url` is set") is the confirming
    signal for shared identity in Claim 3 / #2079, but is not a discriminator on
    its own: an `authorization_code` flow can also use a `token_url` (see that
    note's "Static OAuth client config.yaml" artifact).
  - `source-notes/docs-litellm-mcp-troubleshoot.md` **Claim 1** — the status
    line localizes the fault and an empty tool list means the upstream hop
    failed; this page's Claim 1 supplies a concrete upstream cause (the Slack app
    toggle) for the empty-list branch.
  - `source-notes/docs-litellm-mcp-troubleshoot.md` **Claim 9** and
    `docs-litellm-mcp-oauth-passthrough.md` **Claim 9** — the masked
    `x-litellm-mcp-debug` headers and the two-header rule (`x-litellm-api-key`
    admission, `Authorization` reserved for the upstream token) are the same
    mechanics this page restates when it says to put the LiteLLM key in
    `x-litellm-api-key`.
  - `source-notes/docs-litellm-mcp-control.md` **Claim 11** — `mcp_rpm_limit`
    caps gateway-side calls per key/team/server; this page's Claim 5 adds that
    the upstream's per-tool tier stacks underneath, so the gateway limit is not
    the effective ceiling.
  - `source-notes/docs-litellm-mcp-linear-server.md` **Claim 4** — tools are
    published at runtime via `tools/list` and the live MCP Tools tab is the
    source of truth; this page states the same for Slack.
- **Contradicts**: `source-notes/docs-litellm-mcp-linear-server.md` **Claim 5** —
  its quote "Do not set `client_id`, `client_secret`, or `token_url` on the OAuth
  server. Those switch it to a machine-to-machine identity shared by every
  caller" over-groups the three fields: Slack requires
  `client_id`/`client_secret` (no DCR) and yet stays per-user because
  `oauth2_flow: authorization_code` selects the interactive flow.
  `source-notes/docs-litellm-mcp-oauth.md` **Claim 15** is *ambiguous* on the
  same question, not a clean contradiction: its quote lists all three fields
  together ("The server has `client_id`/`client_secret`/`token_url` configured")
  without stating the flow, so it does not establish whether a `token_url`
  under `authorization_code` collapses identity (that note's static-client
  artifact shows it does not). Filed as contradiction issue **#2079**
  (recommended verdict: accepted-B / scope refinement). Do not pick a verdict
  here.
- **Extends**:
  - `source-notes/docs-litellm-mcp-deployment.md` **Claim 5** — a vendor-hosted
    upstream is a dependency outside the operator's control; this page adds a
    provisioning-state dependency (upstream app toggle + reinstall) that is
    invisible to the gateway (Claims 1–2).
  - `source-notes/docs-litellm-mcp-linear-server.md` **Claim 2** — the
    endpoint > consent-scope > deny-list ordering is upstream-dependent:
    Slack has no read-only endpoint, so scope consent is the primary control
    (Claim 4 here).
  - `source-notes/docs-litellm-mcp-control.md` **Claim 11** — gateway rate
    limits are additive to upstream tiers (Claim 5 here).
- **Novel** (first appearances in the corpus):
  1. An upstream per-app toggle that fails silently outside the gateway's
     visibility: OAuth succeeds, tool list empty or 403 (Claim 1).
  2. A reinstall-to-apply-scopes rule: added user-token scopes are inert until
     the app is installed/reinstalled (Claim 2).
  3. A static-client-credentials counterexample showing that the auth flow, not
     the client credentials or a token endpoint, decides identity:
     `oauth2_flow: authorization_code` keeps per-user identity even when
     `client_id`/`client_secret` are mandatory (Claim 3).
  4. An upstream with no read-only endpoint, so consent scopes are the primary
     least-privilege control (Claim 4).
  5. Upstream per-tool rate tiers stacking under `mcp_rpm_limit` (Claim 5).
  6. The Slack app-visibility constraint (internal or directory-published only)
     as part of MCP enablement (Claim 3).

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Add an ordered diagnostic for "OAuth
  visibly succeeded but the tool list is empty or a tool call returns 403"
  (Claims 1–2). Order: (1) confirm the upstream app's MCP toggle is enabled —
  Slack's *Agents & AI Apps → Model Context Protocol* — because a disabled
  toggle produces exactly this symptom and is not a LiteLLM permission error;
  (2) confirm the app was reinstalled after the last scope change; (3) only then
  inspect gateway `allowed_tools` / `disallowed_tools` /
  `object_permission` / `mcp_tool_permissions`. This inserts an upstream-owned
  check *before* the gateway checks that
  `docs-litellm-mcp-troubleshoot.md` Claim 1's status-line partition currently
  sends operators toward.
- **Chapter 06 (Security and Trust — credential routing / per-user identity)**:
  Correct the M2M rule to the **flow** discriminator from Claim 3 (and
  contradiction #2079): `oauth2_flow: client_credentials` (no interactive flow)
  collapses every caller to one shared machine-to-machine identity, whereas
  static client credentials under `oauth2_flow: authorization_code` stay
  per-user whether or not a `token_url` is set. Add the counterexample
  explicitly, because the current "remove the client credentials" advice would
  break Slack (and any upstream without DCR). Keep the audit-attribution
  warning, but scope it to client-credentials-flow / shared-identity configs;
  do not treat a `token_url` alone as evidence of M2M, since authorization-code
  upstreams routinely exchange their own code at a token endpoint.
- **Chapter 06 (Security and Trust — least privilege / upstream privilege
  boundary)**: Add that whether least privilege is an endpoint swap or a
  consent-scope grant is an *upstream* property (Claim 4). Slack offers no
  read-only endpoint, so scope selection at consent is the primary control and
  the gateway's `allowed_tools` is a secondary narrowing layer; contrast with
  Linear's `/mcp/readonly` (Claim 2 there). State the privilege boundary
  explicitly: for a hosted upstream, the tool surface and per-tool rate tiers
  are upstream-owned (Claims 4–5), so the gateway governs *who calls* and
  *which tools it exposes*, not *what the upstream will allow*.
- **Chapter 05 (LLM Ops Reliability)**: Add the effective-rate formula for
  hosted MCP upstreams — `min(gateway mcp_rpm_limit, upstream per-tool tier)` —
  and note that Slack's per-tool limits are not configurable from LiteLLM
  (Claim 5). Add the upstream provisioning state (app toggle, install/reinstall)
  to the vendor-hosted-upstream registration inventory alongside the endpoint
  URL and transport, so a provider-side change is a detectable change rather
  than a surprise "OAuth works but no tools" page.

## Extraction Notes

- Source read in full via WebFetch of the canonical URL
  (`https://docs.litellm.ai/docs/mcp_servers/slack`, HTTP 200, no paywall) on
  2026-11-08. All `Quote` fields are contiguous verbatim strings from the
  fetched page; no quote was spliced across non-adjacent sentences. Markdown
  link syntax and bold markers were avoided inside quotes by quoting only the
  contiguous plain-text fragment that carries the meaning. The tool catalog and
  scope table were transcribed row-by-row; YAML/JSON blocks were line-broken for
  readability only.
- The page intentionally restates gateway mechanics already covered in the
  corpus. Per the Prospector's bounded scope, the OAuth-flow taxonomy, the
  ingress `400 invalid_request` signature, per-key/team `object_permission`, and
  the `x-litellm-api-key` / `SAME_AS_LITELLM_KEY` leak are extracted only where
  this page adds an upstream-specific detail, and are otherwise cited as
  corroboration rather than re-mined.
- Linked sibling pages (Slack's own MCP server overview, `/docs/mcp_oauth`,
  `/docs/mcp_control`, `/docs/mcp_rest_api#tool-naming`, `/docs/mcp_troubleshoot`)
  were not deep-dived; their corpus notes are cited instead. The Slack upstream
  page was not fetched, so this note does not assert upstream behavior beyond
  what LiteLLM's page states.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Every cited `Claim N` in another
  note was re-read per MINER §4b before writing: `docs-litellm-mcp-oauth.md`
  Claims 1, 2, 15; `docs-litellm-mcp-linear-server.md` Claims 2, 4, 5;
  `docs-litellm-mcp-control.md` Claim 11; `docs-litellm-mcp-troubleshoot.md`
  Claims 1, 9; `docs-litellm-mcp-oauth-passthrough.md` Claim 9;
  `docs-litellm-mcp-deployment.md` Claim 5; `docs-litellm-mcp-zero-trust.md`
  Claims 5, 7. Claim numbers and quoted fragments were confirmed against those
  notes.
- **Contradiction filed**: the Claim 3 flow-based discriminator opposes
  `docs-litellm-mcp-linear-server.md` Claim 5's rule that setting `client_id`,
  `client_secret`, or `token_url` switches the server to a shared M2M identity;
  `docs-litellm-mcp-oauth.md` Claim 15 discusses the same three fields together
  but is ambiguous about the flow, so it is not a clean contradiction. Per MINER
  §4a this was filed as contradiction issue **#2079** before opening this PR
  (checked `CONTRADICTIONS.md` and open `contradiction` issues first; neither
  covered it). This note records both sides and does not assign a verdict.
- The page is a living vendor document with no measured reliability, incident
  data, or independent verification, so every claim is `emerging` and
  `confidence_overall` is `emerging`. The operational framing in `Our
  assessment` (especially the runbook ordering) is the Miner's inference from
  the page's explicit statements.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited — both
  are derived indexes rebuilt after merge. `date_published` is unknown (living
  vendor docs); `date_extracted` and `last_checked` are both 2026-11-08.
