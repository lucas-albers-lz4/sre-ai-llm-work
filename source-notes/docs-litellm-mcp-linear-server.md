---
source_url: https://docs.litellm.ai/docs/mcp_servers/linear
source_type: docs
title: "Linear MCP server — LiteLLM Documentation (hosted remote MCP through the gateway: read-only endpoint, identity attribution, and fail-silent deny-list drift)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-11-07
last_checked: 2026-11-07
status: current
confidence_overall: emerging
issue: "#1969"
---

# Linear MCP server (LiteLLM Docs)

> LiteLLM's integration page for exposing Linear's vendor-hosted remote MCP
> server through the MCP Gateway: it documents a dedicated read-only endpoint as
> the default reads-only grant, the identity fork between per-user OAuth (leave
> `client_id`/`client_secret`/`token_url` unset) and a shared machine identity
> (client credentials or an API key), the workspace-binding limitation of an
> authorized session, and a server-level `disallowed_tools` entry that "fails
> silently and leaves that tool callable" once the upstream tool name changes.

## Source Context

- **Type**: docs (official first-party LiteLLM vendor documentation — "Linear
  MCP server", under MCP Gateway → MCP Servers, at
  `https://docs.litellm.ai/docs/mcp_servers/linear`).
- **Author credibility**: LiteLLM (BerriAI) documenting its own gateway against
  Linear's hosted MCP server. Authoritative for the exposed config surface
  (fields, endpoint URLs, auth modes, UI/tab names, tool-name prefixing) and for
  how the gateway treats a hosted upstream. It reports no production metrics, no
  incident writeup, and no independent verification. The page documents
  capability, not measured behavior; every claim is graded `emerging`.
- **Scope**: Covers why to use Linear's hosted MCP server, its two endpoints
  (`/mcp` and `/mcp/readonly`) plus the deprecated `/sse` fallback, OAuth 2.1
  per-user vs API-key shared identity, gateway registration (UI and `config.yaml`),
  the `PROXY_BASE_URL` ingress requirement, connecting from Claude Desktop /
  Cursor / Claude Code, the runtime-published tool catalog, and the read-only vs
  deny-list trade-off. It restates gateway mechanics that are documented in
  depth elsewhere (OAuth flow, `object_permission`, `mcp_rpm_limit`); this note
  extracts only the integration-specific delta and treats the rest as
  corroboration.
- **Sub-pages followed**: none. The page defers its mechanics to the sibling
  MCP OAuth, MCP Control, Tool naming, and troubleshooting pages, all of which
  already have source notes in the corpus and are cited below rather than
  re-mined.

## Extracted Claims

### Claim 1: Linear hosts the MCP server centrally over Streamable HTTP, and the gateway adds centralized auth, per-key/team access control, per-tool-call cost tracking, and one audit trail
- **Evidence**: The page intro ("Linear hosts and manages the server centrally…")
  and the "Key features" bullets. The gateway-side additions are stated as the
  reason to front the hosted server rather than connect directly.
- **Confidence**: emerging (vendor capability documentation; no measured
  consolidation benefit)
- **Quote**: "Linear hosts and manages the server centrally, so there is nothing to deploy or run yourself."
- **Quote**: "LiteLLM adds centralized auth, access control by key and team, cost tracking per tool call, and one audit trail across every MCP server you expose."
- **Our assessment**: This is the integration shape the Prospector asked about:
  a vendor-hosted remote MCP server registered as an upstream in the gateway.
  The value is not transport (Linear runs it) but the gateway observation
  position — spend/audit/permission resolve at LiteLLM while the upstream owns
  the tools. That is the same "gateway as control plane" premise as
  `docs-litellm-mcp-deployment.md` Claim 1, applied to a single hosted server.

### Claim 2: The dedicated read-only endpoint `https://mcp.linear.app/mcp/readonly` is the cleanest way to grant reads only and the default choice; the weaker alternatives are declining the write scope at consent or excluding write tools in config
- **Evidence**: The "Key features" bullet ("A dedicated read-only endpoint…"),
  the Endpoint block listing both URLs, and the "Reads without writes" section's
  explicit ordering.
- **Confidence**: emerging (documented recommendation)
- **Quote**: "The read-only endpoint is the cleanest way to grant reads only, and the one to reach for by default. On the standard endpoint you can get the same result by declining the write scope at consent time, or by excluding the write tools in config."
- **Our assessment**: This is the highest-value security pattern on the page: a
  capability-narrowing *endpoint* beats a gateway-side deny list because the
  write tools never exist in the exposed surface at all. The explicit ordering —
  endpoint > consent-scope > `disallowed_tools` — is the guide-worthy rule.
  Note the qualification: the alternatives are "the same result" only if the
  exclusion list stays correct, which Claim 3 shows it may not.

### Claim 3: A server-level `disallowed_tools` entry that no longer matches a real tool fails silently and leaves that tool callable
- **Evidence**: The "Reads without writes" config example, preceded by the
  warning to "Confirm the names against your live tool list first" and the
  fail-silent statement. The page pairs it directly with the runtime-mutable
  catalog in Claim 4.
- **Confidence**: emerging (explicit first-party behavioral statement; not an
  observed incident)
- **Quote**: "Confirm the names against your live tool list first, because a `disallowed_tools` entry that no longer matches a real tool fails silently and leaves that tool callable:"
- **Our assessment**: This is the page's most important operational claim and
  the one that materially extends `docs-litellm-mcp-control.md` Claim 7 (which
  establishes that server-registration-level `allowed_tools`/`disallowed_tools`
  exist and bind every caller, but says nothing about stale entries). It is a
  fail-open deny list: a renamed upstream tool silently becomes callable again.
  Contrast with tool *pinning*, which the control page's Claim 9 says "alerts
  when the upstream drifts from the pin" — a stale deny entry has no such
  signal. The practical rule for the guide: do not treat a deny list as a
  read-only grant on a runtime-mutable upstream; prefer the read-only endpoint
  (Claim 2) and pin the tool list where possible.

### Claim 4: Linear publishes tool definitions at runtime through `tools/list`, so tool names and fields can change without notice; the live MCP Tools tab, not the docs table, is the source of truth
- **Evidence**: The "info" callout above the "Tools provided" table: it states
  the runtime publication and points at the gateway UI's MCP Tools tab as the
  authoritative live list, with a test-call affordance. The docs table is shown
  as illustrative.
- **Confidence**: emerging (explicit first-party statement; the operational
  consequence is our inference)
- **Quote**: "Linear publishes its tool definitions at runtime through `tools/list`, so names and fields can change without notice."
- **Our assessment**: This turns the docs table into a non-contract. Combined
  with Claim 3, the failure is quiet: an allow/deny entry compiled against
  today's names can be wrong after any upstream change, and nothing in the
  gateway records that the name disappeared. For Ch05, the live `tools/list`
  (via the MCP Tools tab or an API `tools/list`) should be the pre-rollout check
  and the drift baseline, not the prose table. This is the same "discovery is
  not negotiation" caution the corpus applies to Agent Cards
  (`docs-promptfoo-a2a-provider.md` Claim 3), applied to a hosted MCP tool
  catalog.

### Claim 5: Leaving `client_id`, `client_secret`, and `token_url` unset preserves per-user OAuth identity via Linear's dynamic client registration; setting them silently switches every caller to one machine-to-machine identity
- **Evidence**: The "Leave the client credentials out" callout inside the
  gateway-connect section, and the OAuth registration snippet that omits all
  three fields. The Authentication section separately states Linear supports
  RFC 7591 dynamic client registration.
- **Confidence**: emerging (explicit documented behavior; no measured
  attribution audit)
- **Quote**: "Do not set `client_id`, `client_secret`, or `token_url` on the OAuth server. Those switch it to a machine-to-machine identity shared by every caller, so issues get filed by one service account instead of the person who asked. Linear's dynamic registration makes them unnecessary."
- **Our assessment**: This is the identity-attribution decision the Prospector
  asked for, stated concretely. The failure is silent in the audit trail: the
  gateway still works, but every write is attributed to one service account. It
  corroborates `docs-litellm-mcp-oauth.md` Claim 2 (per-user interactive tokens
  are stored under the calling key's `user_id`) and its Claim 15 diagnostic
  (`m2m-client-credentials` means client credentials are set and every caller
  shares one identity). The guide rule: for anything user-facing or anything
  that writes, omit the client credentials and let DCR carry per-user identity.

### Claim 6: The API-key/bearer path is an explicit shared identity — every caller is attributed to the key's owner — so it should be reserved for read-only context sources and unattended backend agents
- **Evidence**: The Authentication "Alternative" bullet and the "config.yaml (API
  key)" snippet, which pairs a Linear personal API key with the read-only
  endpoint. The "Security > Security & access > Personal API keys" steps tell the
  operator to grant only the Read permission.
- **Confidence**: emerging (documented recommendation)
- **Quote**: "A Linear API key sent as a bearer token. This is a single shared identity rather than per-user, so reserve it for read-only context sources and unattended backend agents."
- **Quote**: "Every caller shares this identity, so tool calls are attributed to the key's owner rather than the end user. Prefer OAuth for anything user-facing or anything that writes."
- **Our assessment**: The page is unusually explicit that this is a deliberate
  opt-in to shared identity, not a fallback that "just works." The pairing of
  the API key with `/mcp/readonly` is the safe configuration: shared identity
  plus a capability-narrowed endpoint, so the blast radius is "reads as the key
  owner," not "writes as the key owner." This is the operational answer for an
  unattended backend agent that cannot complete a browser sign-in.

### Claim 7: `oauth2_flow: authorization_code` is required for the interactive per-user flow; the proxy refuses to start on an `auth_type: oauth2` server that omits it
- **Evidence**: The sentence immediately after the OAuth `config.yaml` snippet,
  plus the requirement that storing MCP servers needs `store_model_in_db: true`.
- **Confidence**: emerging (explicit documented startup behavior)
- **Quote**: "`oauth2_flow: authorization_code` selects the interactive per-user flow and is required; the proxy refuses to start on an `auth_type: oauth2` server that omits it."
- **Our assessment**: Corroborates `docs-litellm-mcp-oauth.md` Claim 1 ("Every
  `auth_type: oauth2` server in `config.yaml` must declare its flow via
  `oauth2_flow`") and is a good fail-fast property: a misconfigured server
  refuses startup rather than silently choosing a flow. The `store_model_in_db`
  prerequisite is easy to miss and produces an empty/registration failure rather
  than an auth failure, so it belongs in the same runbook step.

### Claim 8: An authorized session is bound to one Linear workspace; reconnecting alone does not switch it, so a second workspace needs a separate MCP server entry
- **Evidence**: The closing paragraph of the gateway-connect section, after the
  key-placement/debug callout.
- **Confidence**: emerging (explicit documented limitation)
- **Quote**: "An authorized session is bound to one Linear workspace, and reconnecting alone does not switch it, so a user who needs a second workspace has to register it as a separate MCP server entry."
- **Our assessment**: A concrete multi-tenant gotcha with no equivalent in the
  existing MCP notes. It means workspace is part of the server's identity, not a
  per-request parameter: a single `linear_mcp` registration cannot serve users
  in two workspaces. The workaround (one server entry per workspace) multiplied
  by per-user OAuth is a config-management and audit-attribution concern for
  Ch05/Ch06 — two entries mean two `object_permission` grants and two entries in
  the tool-prefix namespace.

### Claim 9: Interactive OAuth needs the `Authorization` header free for the upstream token — the LiteLLM key must ride in `x-litellm-api-key` or the OAuth flow never runs and the LiteLLM key is forwarded to Linear
- **Evidence**: The "Put the LiteLLM key in `x-litellm-api-key`" callout, the
  client connection examples (which use that header), and the debug signal
  guidance pointing at `x-litellm-mcp-debug`.
- **Confidence**: emerging (explicit documented behavior)
- **Quote**: "Interactive OAuth needs the `Authorization` header free for the upstream token. If a client sends the LiteLLM API key as `Authorization: Bearer sk-...`, the OAuth flow never runs and LiteLLM forwards your LiteLLM key to Linear, which rejects it."
- **Quote**: "To diagnose, add `x-litellm-mcp-debug: true` and read the response headers: `SAME_AS_LITELLM_KEY` confirms this case, and `m2m-client-credentials` means client credentials are set and every caller shares one identity."
- **Our assessment**: Corroborates `docs-litellm-mcp-oauth.md` Claim 15 and
  `docs-litellm-mcp-oauth-passthrough.md` Claim 9 (the gateway keeps the
  admission credential and the upstream bearer in different headers; a lone
  `Authorization` is treated as admission). The failure is not a generic 401: it
  is the LiteLLM key being sent to a third party, which is a credential-exposure
  event. The debug signal is the discriminator and belongs in the runbook before
  any credential rotation.

### Claim 10: When LiteLLM runs behind a TLS-terminating ingress, `PROXY_BASE_URL` must be the user-visible origin or the OAuth callback validation fails with `400 Bad Request` / `{"detail":"invalid_request"}`
- **Evidence**: "Step 2: Set the proxy's public origin" and its example.
- **Confidence**: emerging (explicit documented failure signature)
- **Quote**: "If LiteLLM runs behind a TLS-terminating ingress, set `PROXY_BASE_URL` to the origin users see in their address bar so the OAuth callback validates"
- **Our assessment**: Corroborates `docs-litellm-mcp-oauth.md` Claim 6 (the
  ingress origin mismatch surfaces as the non-obvious top-level `invalid_request`)
  and its Claim 5 (origin resolution order). This page is the per-integration
  instance of that failure: a hosted upstream's first Connect click is where the
  misconfiguration shows up. No new mechanism; useful as the concrete runbook
  symptom.

### Claim 11: LiteLLM prefixes tool names with the server name, so `create_issue` is exposed to models as `linear_mcp-create_issue`
- **Evidence**: The "Tools provided" closing paragraph and its link to the Tool
  naming reference. The `disallowed_tools` example uses unprefixed names, while
  the control page notes both prefixed and unprefixed forms are accepted.
- **Confidence**: emerging (explicit documented behavior)
- **Quote**: "LiteLLM prefixes tool names with the server name, so `create_issue` is exposed to models as `linear_mcp-create_issue`"
- **Our assessment**: The prefix is the namespace that makes multi-server
  allow/deny lists unambiguous, but it also means the model-visible name differs
  from the upstream name (different from the promptfoo naming style). The
  `disallowed_tools` example on this page uses unprefixed names; per
  `docs-litellm-mcp-control.md` Claim 8 both forms work for `allowed_params`, so
  the safest rule is to confirm the accepted form against the live list rather
  than assume one. This is a small but real source of "the deny list didn't
  match" bugs (Claim 3).

### Claim 12: Upstream writes are confined to issues, projects, and comments; documents, cycles, teams, statuses, and labels are read-only at the upstream, so the read-only problem is about the write-capable subset
- **Evidence**: The sentence immediately after the "Tools provided" table.
- **Confidence**: emerging (explicit first-party statement)
- **Quote**: "Writes are limited to issues, projects, and comments; documents, cycles, teams, statuses, and labels are read-only."
- **Our assessment**: Clarifies the blast radius of the endpoint choice: even on
  `/mcp`, only a subset of tools writes. But "only a subset" still includes
  `create_issue`, `update_issue`, `create_project`, `update_project`, and
  `create_comment` — enough to file/alter tickets and comment. The read-only
  endpoint is therefore about removing the five write tools, not about a broad
  upstream restriction.

### Claim 13: Linear's `/sse` endpoint survives only as a deprecated fallback for clients without Streamable HTTP, so a provider-hosted server can move its transport out from under the gateway
- **Evidence**: The "Key features" bullet and the Endpoint section's deprecation
  sentence recommending `/mcp` for new setups.
- **Confidence**: emerging (explicit deprecation statement)
- **Quote**: "Linear also exposes `https://mcp.linear.app/sse` as a deprecated fallback for clients without Streamable HTTP support. Use the `/mcp` endpoint for new setups."
- **Our assessment**: This is a dependency-risk fact with no equivalent in the
  existing MCP notes: because the upstream is vendor-hosted, its transport
  lifecycle is not under the operator's control. A client or gateway that depends
  on `/sse` is on a path the provider has already deprecated. For Ch05, record
  the transport (`http` Streamable HTTP) and the upstream endpoint in the
  registration inventory so a provider deprecation is a detectable change, not a
  surprise outage.

### Claim 14: Per-key/per-team grants and per-server rate limits apply to this hosted server through `object_permission` and `mcp_rpm_limit`, with no new semantics
- **Evidence**: The closing "Restrict who can use it" callout, which delegates to
  "MCP Permission Management" for both controls.
- **Confidence**: emerging (documented application of existing gateway controls)
- **Quote**: "Grant the server per key or per team with `object_permission`, and cap call volume per server with `mcp_rpm_limit`"
- **Our assessment**: This is corroboration of
  `docs-litellm-mcp-control.md` Claims 1–13, not a new mechanism: a hosted
  remote MCP server is just another `mcp_servers` entry for the permission model.
  Worth stating in the guide so operators do not assume a vendor-hosted upstream
  needs a separate authorization story — it needs the same grants, and the
  read-only endpoint (Claim 2) is an additional narrowing layer on top.

## Concrete Artifacts

All artifacts are from the fetched page
(https://docs.litellm.ai/docs/mcp_servers/linear). YAML blocks were collapsed to
single lines by HTML extraction; line breaks/indentation were restored at YAML
boundaries only, with no wording changes.

### Endpoints (source: "Endpoint")

```text
https://mcp.linear.app/mcp            # remote MCP server (use for new setups)
https://mcp.linear.app/mcp/readonly   # read-only
https://mcp.linear.app/sse            # deprecated fallback (no Streamable HTTP)
```

### OAuth 2.1 per-user registration (source: "Step 1: Register the server in LiteLLM → config.yaml")

```yaml
mcp_servers:
  linear_mcp:
    url: "https://mcp.linear.app/mcp"
    transport: "http"
    description: "Linear issues, projects, and cycles"
    auth_type: oauth2
    oauth2_flow: authorization_code
```

### Shared-identity API key + read-only endpoint (source: "Step 1 → config.yaml (API key)")

```yaml
mcp_servers:
  linear_readonly:
    url: "https://mcp.linear.app/mcp/readonly"
    transport: "http"
    description: "Linear, read-only"
    auth_type: bearer_token
    auth_value: os.environ/LINEAR_API_KEY
```

### Read-only via deny list on the standard endpoint (source: "Reads without writes")

```yaml
mcp_servers:
  linear_mcp:
    url: "https://mcp.linear.app/mcp"
    transport: "http"
    auth_type: oauth2
    oauth2_flow: authorization_code
    disallowed_tools: ["create_issue", "update_issue", "create_project", "update_project", "create_comment"]
```

### Ingress origin (source: "Step 2: Set the proxy's public origin")

```bash
PROXY_BASE_URL=https://llm.example.com
```

### Agent connection — Claude Desktop / Cursor (source: "Step 3: Connect from an agent")

```json
{
  "mcpServers": {
    "linear": {
      "url": "http://localhost:4000/linear_mcp/mcp",
      "headers": {
        "x-litellm-api-key": "Bearer sk-<your-litellm-api-key>"
      }
    }
  }
}
```

### Agent connection — Claude Code (source: "Step 3: Connect from an agent")

```bash
claude mcp add --transport http linear http://localhost:4000/linear_mcp/mcp \
  --header "x-litellm-api-key: Bearer $LITELLM_API_KEY"
```

### Tool catalog (source: "Tools provided", transcribed from the table)

```text
Area              Tools
Issues            get_issue, list_issues, create_issue, update_issue, list_my_issues
Issue metadata    list_issue_statuses, get_issue_status, list_issue_labels
Projects          list_projects, get_project, create_project, update_project
Comments          list_comments, create_comment
Documents         get_document, list_documents
Cycles            list_cycles
Teams             list_teams
```

The page caveats this table: "Linear publishes its tool definitions at runtime
through `tools/list`, so names and fields can change without notice."

## Cross-References

**Candidates from `miner-related-notes.md`** (read first; every listed path is
cited or explicitly dismissed):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  accounting at `POST /v1/batches`; no MCP server, auth-identity, or tool-ACL
  content.
- `source-notes/docs-litellm-mcp-deployment.md` — **cited** (Extends; see below):
  gateway topology and the egress grant of registering an external MCP URL; this
  page is a concrete vendor-hosted upstream.
- `source-notes/docs-litellm-mcp-zero-trust.md` — **cited** (adjacent; see below):
  outbound JWT call attestation. Different layer from this page's per-user vs
  shared identity choice, but the same per-user attribution goal.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**:
  provider-native web-search support matrix; unrelated.
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**:
  completion parameter support gate; unrelated to MCP auth or ACLs.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: Evaluations API
  stored-completion grading; unrelated.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` passthrough fields; unrelated.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: Enterprise license
  tiers/features; no MCP integration or auth mechanics.
- `source-notes/docs-litellm-mcp-aws-sigv4.md` — **dismissed**: a different
  outbound `auth_type` (SigV4 for AgentCore); no hosted Linear server, read-only
  endpoint, or deny-list content.
- `source-notes/docs-litellm-files-endpoints.md` — **dismissed**: provider
  `/files` passthrough; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 1** — establishes that every
    `auth_type: oauth2` server must declare `oauth2_flow` or the proxy refuses to
    start; this page's Claim 7 is the same rule applied to `linear_mcp`.
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 2** — per-user interactive
    tokens are stored under the calling key's `user_id`; that is the data-model
    reason this page's Claim 5 says omitting client credentials preserves per-user
    identity.
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 6** — the ingress origin
    mismatch produces `400 Bad Request` with `{"detail":"invalid_request"}`; this
    page's Claim 10 is the per-integration instance of that signature.
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 15** — `SAME_AS_LITELLM_KEY`
    means the LiteLLM key is being forwarded upstream and
    `m2m-client-credentials` means every caller shares one identity; this page's
    Claim 9 repeats both diagnostics for the Linear connect path.
  - `source-notes/docs-litellm-mcp-oauth-passthrough.md` **Claim 9** — a lone
    `Authorization` credential is treated as the admission credential and never
    forwarded upstream; combined with this page's Claim 9, the two-header rule
    (`x-litellm-api-key` + upstream token) is the same two-trust-domain design.
  - `source-notes/docs-litellm-mcp-control.md` **Claim 7** — server-registration
    `allowed_tools`/`disallowed_tools` bind every caller; this page adds the
    fail-silent stale-entry behavior (Claim 3).
- **Contradicts**: None filed. There is a *control-choice* contrast, not a claim
  conflict: this page's `disallowed_tools` deny list fails silently when a name
  goes stale (Claim 3), while the control page's tool *pinning* "alerts when the
  upstream drifts from the pin" (`docs-litellm-mcp-control.md` Claim 9). These
  are two different mechanisms with different failure modes, and the page itself
  recommends the endpoint/consent path over the deny list, so no contradiction
  issue was filed per MINER §4a. Checked `CONTRADICTIONS.md` (no entries) and open
  `contradiction`-labeled issues (none about MCP deny-list drift) before writing.
- **Extends**:
  - `source-notes/docs-litellm-mcp-control.md` **Claim 7** — that note documents
    that server-level ACLs exist and bind every caller but says nothing about
    stale entries; this page supplies the fail-silent semantics and the explicit
    endpoint > consent-scope > deny-list ordering (Claims 2–3).
  - `source-notes/docs-litellm-mcp-control.md` **Claim 9** — the pinning path is
    the drift-detecting alternative to the deny list; this page is the concrete
    "why a deny list is not enough on a runtime-mutable upstream" case (Claims 3–4).
    Cite by claim number for the contrast only; the verdict stays with the guide.
  - `source-notes/docs-litellm-mcp-deployment.md` **Claim 5** — registering an
    external MCP URL makes the gateway issue outbound requests on every tool call;
    this page is a concrete vendor-hosted upstream (`mcp.linear.app`) whose
    transport (Streamable HTTP, with deprecated `/sse`) is controlled by the
    provider (Claim 13).
- **Novel** (first appearances in the corpus):
  1. A per-server integration page for a vendor-hosted remote MCP server, rather
     than a gateway-mechanics page.
  2. The `/mcp` vs `/mcp/readonly` *endpoint* as a capability-narrowing primitive,
     with the explicit ordering endpoint > consent-scope > deny list.
  3. Fail-silent stale `disallowed_tools` entries on a runtime-mutable upstream
     (the deny-list-that-stops-denying failure mode).
  4. The client-credentials identity fork: unset preserves per-user OAuth via DCR;
     set collapses every caller to one M2M identity, silently changing audit
     attribution.
  5. Workspace binding of an authorized session (one workspace per MCP server
     entry; reconnecting does not switch it).
  6. Deprecated `/sse` as a provider-side transport dependency risk.

## Guide Impact

- **Chapter 06 (Security and Trust — "Gateway credential routing: declare, don't
  infer", `guide/06-security-and-trust.md:603`)**: Add the identity-attribution
  rule from Claims 5–6: for a per-user hosted MCP server, *omit*
  `client_id`/`client_secret`/`token_url` so dynamic registration preserves the
  caller's identity; setting them (or using an API key) is an explicit opt-in to
  one shared service identity and must be reserved for read-only/unattended use.
  State the audit consequence — "issues get filed by one service account instead
  of the person who asked" — because the failure is invisible in normal operation.
- **Chapter 06 (Security and Trust — least privilege / MCP tool controls,
  `guide/06-security-and-trust.md:285`)**: Add the endpoint-over-deny-list rule
  from Claims 2–4: prefer the upstream's dedicated read-only endpoint over a
  gateway `disallowed_tools` list; if a deny list is used, confirm names against
  the live `tools/list` and pin the tool list, because a stale entry "fails
  silently and leaves that tool callable." This is the concrete fail-open case
  for server-level ACLs and should be paired with the pinning alert control in
  `docs-litellm-mcp-control.md` Claim 9.
- **Chapter 06 ("An agent gateway's default is full access",
  `guide/06-security-and-trust.md:316`)**: Add that per-key/per-team
  `object_permission` and `mcp_rpm_limit` are the same controls for a hosted
  remote MCP server (Claim 14), and that the read-only endpoint is the default
  posture for context-only grants. A vendor-hosted server needs the same grants as
  an in-house one; the gateway is the single authorization point.
- **Chapter 05 (LLM Ops Reliability)**: Add the vendor-hosted-upstream dependency
  checklist from Claims 1, 4, and 13: record the upstream URL/transport
  (`http`/Streamable HTTP) in the registration inventory, treat the live
  `tools/list` (not the docs table) as the source of truth for tool names before
  rollout, and track the deprecated `/sse` fallback as a provider-side change
  that can break clients. Add the `store_model_in_db: true` prerequisite and the
  `oauth2_flow` startup fail-fast (Claim 7) to the registration runbook.
- **Chapter 03 (Runbooks and Agents)**: Add the "agent write-back" workflow the
  page names — read the ticket, act, comment progress — with the read-only
  endpoint as the default context grant and a write-capable entry only where the
  agent must file/update issues (Claim 12). Add the two operational gotchas:
  `x-litellm-api-key` vs `Authorization` (Claim 9, with the
  `SAME_AS_LITELLM_KEY` debug signal) and one-workspace-per-server-entry
  (Claim 8), which determines how many `linear_mcp` entries a multi-workspace
  deployment needs.

## Extraction Notes

- Source read in full via WebFetch of the canonical URL
  (`https://docs.litellm.ai/docs/mcp_servers/linear`, HTTP 200, no paywall) on
  2026-11-07. All `Quote` fields are contiguous verbatim strings from the fetched
  page; no quote was spliced across non-adjacent sentences. The tool-catalog
  table was transcribed row-by-row; YAML blocks were line-broken for readability
  only.
- This page intentionally restates gateway mechanics already covered in the
  corpus. Per the Prospector's bounded scope, the OAuth-flow mechanics, the
  `400 invalid_request` ingress error, the `x-litellm-api-key` /
  `SAME_AS_LITELLM_KEY` leak, and the "leave client credentials out" rule are
  extracted only as the per-integration instance and cited as corroboration
  against `docs-litellm-mcp-oauth.md` (Claims 1, 2, 6, 15) and
  `docs-litellm-mcp-oauth-passthrough.md` (Claim 9) rather than re-mined at
  length. The novel delta is the read-only endpoint ordering, the fail-silent
  stale deny-list entry, the runtime-mutable tool catalog, and workspace binding.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Additional cross-references
  (`docs-litellm-mcp-oauth.md`, `docs-litellm-mcp-oauth-passthrough.md`,
  `docs-litellm-mcp-control.md`) came from the Prospector triage and a
  `source-notes/` search. Every cited `Claim N` was re-read in its note per MINER
  §4b before writing; claim numbers and quoted fragments were confirmed.
- **Contradiction decision (no issue filed).** The only near-tension is the
  fail-silent `disallowed_tools` drift here versus the drift-alerting tool
  pinning in `docs-litellm-mcp-control.md` Claim 9. They are different controls
  with different failure modes, not opposing claims about the same behavior; the
  page itself recommends the endpoint/consent path over the deny list. Per MINER
  §4a's "when NOT to file" this is a mechanism contrast, not a claim conflict.
  `CONTRADICTIONS.md` has no entries and no open `contradiction` issue covers MCP
  deny-list drift.
- The page is a living vendor document with no measured reliability, incident
  data, or independent verification, so every claim is `emerging` and
  `confidence_overall` is `emerging`. The fail-silent deny-list and
  runtime-mutable-catalog statements are explicit first-party statements; the
  operational risk framing in `Our assessment` is the Miner's inference.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited — both
  are derived indexes rebuilt after merge.
