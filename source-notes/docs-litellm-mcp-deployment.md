---
source_url: https://docs.litellm.ai/docs/mcp_deployment
source_type: docs
title: "MCP Deployment Guide — LiteLLM Documentation (gateway topology and public-internet exposure)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; front-matter last_updated 2026-10-29)
date_extracted: 2026-10-30
last_checked: 2026-10-30
status: current
confidence_overall: emerging
issue: "#1920"
---

# MCP Deployment Guide (LiteLLM Docs)

> LiteLLM documents two ways to deploy its LLM + MCP + A2A control plane — a
> single recommended gateway (Option A) or a split LLM gateway / MCP gateway
> (Option B, which keeps provider API keys off the internet-facing process) —
> and the exposure controls that decide whether that control plane is safe:
> `available_on_public_internet` defaults to **true**, `mcp_internal_ip_ranges`
> defines what counts as "internal," the same public-internet filter is applied
> at every MCP access point (including the registry and OAuth discovery), and
> disabling an MCP capability is a gateway-wide pruning switch rather than a
> per-caller permission.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP
  Deployment Guide" page under "MCP Gateway → Deployment"). The page's own
  markdown endpoint (`/docs/mcp_deployment.md`) reports
  `last_updated: "2026-10-29"`.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented deployment shapes, config keys, and
  default values; it publishes no production metrics, incident writeups, or
  independent verification. Claims below stay at "the gateway documents this
  behavior" and are graded `emerging` per the Prospector's guidance.
- **Scope**: Covers the single-gateway vs split-deployment topology choice, the
  shared catalog endpoints for LLMs/MCP servers/agents, the open-port problem,
  outbound MCP egress, the `available_on_public_internet` /
  `mcp_internal_ip_ranges` filter, `mcp_disabled_capabilities`, and the opt-in
  MCP registry. It does **not** cover the full MCP permission hierarchy (see
  `docs-litellm-mcp-control.md`), OAuth/SigV4 transport auth (see the MCP OAuth
  notes), rate limits, or cost tracking.
- **Pages read**: The deployment page was read in full, and the linked
  `docs/mcp_public_internet` page (the "Public Internet Filter" reference) was
  read in full because it defines the filter's mechanism and defaults. The
  linked MCP Control, Zero Trust, and Guardrails pages were **not** re-read in
  full here; their surfaces are already covered by existing source notes and
  are cited as cross-references only.

## Extracted Claims

### Claim 1: LiteLLM positions itself as one control plane for three resource types — LLMs, MCP servers, and A2A agents — sharing auth, rate limiting, and usage accounting
- **Evidence**: The opening "core idea" section and its resource-registration
  table (`model_list`, `mcp_servers`, A2A routes).
- **Confidence**: emerging (documented product positioning; no measured
  consolidation benefit)
- **Quote**: "All three share the same auth (LiteLLM API key), rate limiting, and usage dashboard, giving you a central catalog without separate registries."
- **Our assessment**: This is the deployment premise the rest of the page
  reasons from. It is also the source of the coupling risk: the same process
  that holds provider API keys is the process that serves MCP tool calls when
  Option A is used. The page treats the shared catalog as a feature; for Ch06
  the shared process boundary is what makes the topology decision matter.

### Claim 2: Option A — the recommended topology — runs `/v1/chat/completions`, `/mcp`, and `/a2a` in one LiteLLM instance with one config and one key set
- **Evidence**: The "Option A: Single gateway (recommended)" heading, its
  topology diagram, and the follow-on prose.
- **Confidence**: emerging (documented recommendation)
- **Quote**: "One LiteLLM instance handles LLM routing, MCP tool calls, and A2A agent invocations."
- **Quote**: "One service, one config, one set of API keys."
- **Our assessment**: "Recommended" is a vendor convenience recommendation, not
  a risk assessment. The page immediately qualifies it with the public-internet
  filter and later the open-port problem, so the guide should not repeat
  "single gateway" as an unconditional default without the exposure caveats in
  Claims 4–7.

### Claim 3: Option B splits LLM routing and MCP serving into separate LiteLLM deployments so LLM provider credentials are not reachable through the internet-facing MCP process
- **Evidence**: The "Option B: Separate LLM gateway and MCP gateway" heading, its
  diagram (LLM gateway "no public port"; MCP gateway "port 443 / public"), and
  the security rationale paragraph.
- **Confidence**: emerging (documented topology and rationale; no compromise
  test or measured blast radius)
- **Quote**: "LLM API keys stay behind the firewall. A compromise of the MCP gateway does not expose them. Use this when external MCP access is needed but LLM credentials must stay fully private."
- **Our assessment**: This is the highest-value security pattern on the page: a
  network boundary that separates the credential-holding data plane from the
  externally reachable tool surface. It is a *credential-blast-radius*
  argument, not a claim that either gateway is individually secure — the MCP
  gateway is still the exposed process.

### Claim 4: Exposing LiteLLM's port for MCP clients also makes `/v1/chat/completions` reachable externally; the page lists separate deployments, a network-layer firewall rule, and short-lived scoped keys as mitigations
- **Evidence**: The "Security considerations → The open-port problem" section
  and its three-item mitigation list.
- **Confidence**: emerging (documented behavior and vendor mitigations)
- **Quote**: "If you expose LiteLLM's port to the internet (for Claude Desktop / ChatGPT), `/v1/chat/completions` is also reachable externally. LLM credentials stay protected by key auth, but be deliberate about this."
- **Our assessment**: This is the concrete failure mode behind the "one
  gateway" default: MCP exposure is not port-scoped in the way an operator
  might assume — opening `/mcp` to the internet opens the sibling LLM API on
  the same listener. Key auth still gates the LLM route, but the reachable
  credential-consuming surface expands. This belongs in a Ch06 deployment
  checklist and in a Ch05 runbook review at ingress changes, not just in prose.

### Claim 5: Registering an external MCP URL makes the gateway issue outbound requests on every tool call; for air-gapped networks the page says to register only in-perimeter servers and set `available_on_public_internet: false` on each
- **Evidence**: The "MCP servers can reach the public internet" section and its
  air-gapped guidance.
- **Confidence**: emerging (documented egress behavior and vendor guidance)
- **Quote**: "When you register an external MCP URL (e.g. `https://mcp.exa.ai/mcp`), LiteLLM makes outbound requests to it on every tool call."
- **Quote**: "For air-gapped networks: only register MCP servers inside your perimeter and set `available_on_public_internet: false` on each of them."
- **Our assessment**: The direction of traffic matters for firewall policy:
  MCP registration is not only an inbound exposure decision, it is also an
  egress grant. An air-gapped deployment therefore needs both an inbound filter
  (`false`) and a network policy that refuses external MCP URLs — the config
  flag alone does not stop an operator from registering one.

### Claim 6: `available_on_public_internet` defaults to `true`, so an MCP server is visible to external callers unless the operator explicitly sets it to `false`
- **Evidence**: The air-gapped paragraph's default statement and the Option A
  sample config's inline comment for `web_search`.
- **Confidence**: emerging (explicit documented default)
- **Quote**: "The default is `true`, so a server is visible to external callers unless you explicitly set it to `false`."
- **Our assessment**: This is the load-bearing default for Ch06. An operator who
  registers an internal MCP server and does not think about this field gets an
  externally discoverable server. It is a visibility filter, not an
  authentication control (corroborated by
  `docs-litellm-mcp-oauth-passthrough.md` Claim 6), so "private" here means
  hidden from non-private-CIDR callers, not "requires a credential."

### Claim 7: The public-internet filter classifies the caller's IP (optionally from `X-Forwarded-For`) against `mcp_internal_ip_ranges`; internal callers see every server, external callers see only `available_on_public_internet: true` servers, and the filter is applied at every MCP access point
- **Evidence**: The linked Public Internet Filter page's "How It Works" section,
  its filtering bullets, and the statement about access points.
- **Confidence**: emerging (documented filter semantics)
- **Quote**: "This filtering is applied at every MCP access point: the MCP registry, tool listing, tool calling, dynamic server routes, and OAuth discovery endpoints."
- **Our assessment**: "Every MCP access point" is what makes the flag a real
  boundary rather than a listing-time convenience: a hidden server must not be
  callable by direct route, and the OAuth discovery path must not advertise it.
  The `X-Forwarded-For` dependency is also the weak point — the filter is only
  as trustworthy as the proxy chain that sets that header, so a deployment
  behind an untrusted hop can misclassify callers.

### Claim 8: `mcp_internal_ip_ranges` overrides the default private ranges; when empty, LiteLLM uses `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, and `127.0.0.0/8`
- **Evidence**: The linked Public Internet Filter page's "Custom Private IP
  Ranges" section, plus the deployment page's sample `general_settings` block
  that adds the VPN/Tailscale `100.64.0.0/10` range.
- **Confidence**: emerging (explicit documented defaults and override)
- **Quote**: "By default, LiteLLM treats RFC 1918 private ranges as internal."
- **Quote**: "When empty, the standard private ranges are used (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`)."
- **Our assessment**: The default set omits `100.64.0.0/10` (CGNAT / Tailscale),
  which is why the deployment page explicitly adds it in the sample config. An
  operator whose internal callers arrive over Tailscale and who leaves the
  setting empty will classify those callers as external and hide internal
  servers from them — a reliability surprise, not just a security one.

### Claim 9: The IP filter is not an auth control — an internal MCP server with `delegate_auth_to_upstream: true` and interactive `oauth2` PKCE still permits anonymous callers to use the upstream OAuth `/authorize` path without a LiteLLM session
- **Evidence**: The warning box at the top of the linked Public Internet Filter
  page, which points to the OAuth passthrough page for mitigations.
- **Confidence**: emerging (documented interaction; no measured exploitation)
- **Quote**: "If an MCP server is `available_on_public_internet: false` (internal for IP-based discovery) and has `delegate_auth_to_upstream: true` with `auth_type: oauth2` (interactive PKCE, not M2M), anonymous callers can still use the upstream OAuth `/authorize` path without a LiteLLM session."
- **Our assessment**: This is the sharpest caveat in the linked material and the
  one most likely to invalidate a naive reading of Claim 6. `false` hides the
  server from IP-based discovery; it does not close every OAuth path. The guide
  should pair the flag with an explicit statement that it is visibility, not
  admission, and should route operators to the passthrough note's
  `oauth_delegate` guidance when the gateway must stay in the auth path.

### Claim 10: `mcp_disabled_capabilities` prunes prompts/resources gateway-wide — disabled capabilities disappear from `initialize` / `server/discover`, list calls return empty without contacting upstream, get/read calls return JSON-RPC `METHOD_NOT_FOUND`, and tools are unaffected
- **Evidence**: The "Disable prompts or resources" section, including its
  config example and the Admin UI location.
- **Confidence**: emerging (explicit documented behavior)
- **Quote**: "A disabled capability is left out of the `initialize` and `server/discover` responses, its list calls (`prompts/list`, `resources/list`, `resources/templates/list`) return an empty list without contacting any MCP server, and its get/read calls (`prompts/get`, `resources/read`) return the JSON-RPC `METHOD_NOT_FOUND` error. Tools are not affected."
- **Our assessment**: A useful least-privilege default for tool-only MCP
  servers: the pruning happens before upstream fan-out, so it also reduces the
  gateway's discovery load. It is gateway-wide, not per-caller, so it is a
  deployment-shape decision rather than a substitute for the permission model
  in `docs-litellm-mcp-control.md`.

### Claim 11: MCP server names may not contain hyphens — the proxy rejects keys such as `internal-db` at startup
- **Evidence**: The note immediately after the Option A config sample.
- **Confidence**: emerging (explicit documented startup behavior)
- **Quote**: "Server names may not contain a hyphen; the proxy rejects `mcp_servers` keys like `internal-db` at startup. Use underscores instead."
- **Our assessment**: A concrete deployment footgun with a clear runbook check:
  validate `mcp_servers` keys before rollout, because the failure is a startup
  rejection rather than a request-time error. Names in the existing corpus use
  underscores (for example `internal_db`), which matches the documented rule.

### Claim 12: The MCP registry is opt-in via `enable_mcp_registry: true` and exposes a discovery endpoint for Claude Desktop / Cursor — and the public-internet filter applies to the registry as one of the MCP access points
- **Evidence**: The "Central catalog → MCP registry (opt-in)" config sample, and
  the linked Public Internet Filter page's list of filtered access points.
- **Confidence**: emerging (explicit documented opt-in and filter coverage)
- **Quote**: "MCP registry (opt-in): expose a discovery endpoint for Claude Desktop / Cursor:"
- **Quote**: "This filtering is applied at every MCP access point: the MCP registry, tool listing, tool calling, dynamic server routes, and OAuth discovery endpoints."
- **Our assessment**: Extends `docs-litellm-mcp-control.md` Claim 13, which
  documents the registry's `/v1/mcp/registry.json` path and its
  advertise-only/auth-still-enforced semantics. This page adds the visibility
  dimension: the registry is opt-in, but once enabled it is filtered by caller
  IP like the tool endpoints.

### Claim 13: `available_on_public_internet` and the unauthenticated MCP Hub (`GET /public/mcp_hub`) are separate mechanisms — `available_on_public_internet` defaults to `true`, while the hub's strict whitelist is on by default and advertises only servers explicitly listed in `public_mcp_servers`
- **Evidence**: The linked Public Internet Filter page's "Public Internet vs MCP
  Hub Visibility" comparison table and its default-mode explanation.
- **Confidence**: emerging (explicit documented distinction)
- **Quote**: "`available_on_public_internet` and the MCP Hub (`GET /public/mcp_hub`) are two separate mechanisms that are easy to confuse:"
- **Quote**: "Hub strict whitelist is on by default — only servers explicitly listed in `public_mcp_servers` are advertised"
- **Our assessment**: Important default-ordering nuance: a server can be visible
  to external callers at the tool endpoints (default `true`) without being
  advertised on the unauthenticated hub. The guide should not conflate
  "publicly visible to MCP clients" with "listed on the public hub"; the hub is
  the stronger exposure and has the safer default.

## Concrete Artifacts

### Option A single-gateway config (verbatim from `docs/mcp_deployment`)

```yaml
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  store_model_in_db: true
  mcp_internal_ip_ranges:
    - "10.0.0.0/8"
    - "172.16.0.0/12"
    - "192.168.0.0/16"
    - "100.64.0.0/10"   # VPN/Tailscale range

model_list:
  - model_name: gpt-6.1-sol
    litellm_params:
      model: openai/gpt-6.1-sol
      api_key: os.environ/OPENAI_API_KEY

mcp_servers:
  internal_db:
    url: http://db-mcp.internal:8000/mcp
    transport: http
    available_on_public_internet: false  # internal callers only

  web_search:
    url: https://mcp.exa.ai/mcp
    transport: http
    available_on_public_internet: true   # visible to ChatGPT / Claude Desktop (the default)
```

### Option B split-deployment topology (verbatim from `docs/mcp_deployment`)

```text
Internal AI clients             External AI clients
        │                       (ChatGPT, Claude Desktop)
        │                               │
        ▼                               ▼
┌────────────────────┐     ┌────────────────────────┐
│  LLM Gateway       │     │  MCP Gateway           │
│  (no public port)  │     │  (port 443 / public)   │
│  /v1/chat/...      │     │  /mcp                  │
└────────┬───────────┘     └──────────┬─────────────┘
         │                            │
    LLM providers              MCP servers
    (OpenAI, Bedrock, …)       (internal + public)
```

### Open-port mitigations (verbatim from `docs/mcp_deployment`)

```text
1. Separate deployments (Option B): the LLM gateway never gets a public port
2. Firewall — block /v1/chat/completions from public IPs at the network layer
3. Short-lived scoped keys — limit blast radius if a key leaks
```

### Disable prompts/resources (verbatim from `docs/mcp_deployment`)

```yaml
general_settings:
  mcp_disabled_capabilities: ["prompts", "resources"]  # either value alone is fine
```

### Opt-in MCP registry (verbatim from `docs/mcp_deployment`)

```yaml
general_settings:
  enable_mcp_registry: true
```

### Custom private IP ranges (verbatim from `docs/mcp_public_internet`)

```yaml
general_settings:
  mcp_internal_ip_ranges:
    - "10.0.0.0/8"
    - "172.16.0.0/12"
    - "192.168.0.0/16"
    - "100.64.0.0/10"    # Add your VPN/Tailscale range
```

## Cross-References

- **Corroborates**:
  - `docs-litellm-mcp-oauth-passthrough.md` Claim 6 — agrees that
    `available_on_public_internet: false` adds no authentication and mainly
    controls IP-based discovery. This source adds the positive mechanism (the
    filter's caller-IP classification and its access-point coverage) while the
    passthrough note supplies the auth-path caveat.
  - `docs-litellm-mcp-control.md` Claim 2 — both pages document permissive MCP
    defaults (permissions "open by default" there; external visibility
    `true` by default here). Different control layers, same fail-open posture.
- **Contradicts**: None found. The linked Public Internet Filter page's config
  reference carries a comment that reads like "internal only (default)" next to
  `false`, but the same page's comparison table explicitly says the default is
  `True`; the deployment page also says `true`. I read that as an ambiguous
  inline comment, not a substantive contradiction, so I did not file a
  contradiction issue.
- **Extends**:
  - `docs-litellm-mcp-control.md` Claim 13 — that note documents the MCP
    registry path and its advertise-only/permissions-still-enforced semantics;
    this source adds the registry's opt-in switch and its coverage by the
    public-internet filter.
  - `docs-litellm-gateway-auth-reference.md` — that note covers the *auth*
    surface (headers, `auth_type`, zero-trust JWT); this source adds the
    *network-topology* dimension the auth page does not cover.
  - `failure-litellm-mcp-stdio-command-injection.md` — the CVE note documents
    an MCP-surface RCE on the proxy host; Option B is the related
    blast-radius-separation pattern for that class of compromise, although the
    failure transport (stdio) and attack path are different. Cite as context,
    not as evidence that Option B prevents that CVE.
- **Novel**: No existing source note documents the deployment topology choice
  (Option A vs B), the open-port problem, `mcp_internal_ip_ranges`,
  `mcp_disabled_capabilities`, the `available_on_public_internet: true`
  default, or the hyphen restriction on `mcp_servers` keys. A grep of
  `source-notes/` found `available_on_public_internet` only as the passthrough
  caveat; the rest of this surface is new to the corpus.

## Guide Impact

- **Chapter 06 (Security and Trust)** — add a deployment-topology subsection
  near "Gateway credential routing" or the MCP/governance material: state that
  a single gateway co-locates provider credentials and the MCP tool surface
  (Claim 2), and that operators who need external MCP access (Claude Desktop /
  ChatGPT) should either split the LLM and MCP gateways (Option B, Claim 3) or
  explicitly firewall the LLM route and scope keys (Claim 4). Document
  `available_on_public_internet` as **visible by default** (Claim 6), define
  "internal" via `mcp_internal_ip_ranges` including `100.64.0.0/10` for
  VPN/Tailscale (Claim 8), and warn that the flag is visibility, not
  authentication — especially with `delegate_auth_to_upstream` + interactive
  OAuth (Claim 9). Include `mcp_disabled_capabilities` as capability
  minimization for tool-only servers (Claim 10).
- **Chapter 05 (LLM Ops Reliability)** — add deployment review items to the
  gateway/runbook material: choose Option A vs B based on where LLM credentials
  may live, re-check ingress whenever `/mcp` is exposed (Claim 4), validate
  `mcp_servers` keys for hyphens before rollout because the proxy rejects them
  at startup (Claim 11), and treat external MCP URLs as an egress grant, not
  just a config entry (Claim 5). The public-internet filter's dependence on
  `X-Forwarded-For` (Claim 7) should be an ingress/proxy-chain check.
- **Chapter 02/03 (Observability / Runbooks)** — if the guide documents the
  MCP registry, distinguish registry visibility from hub advertisement
  (Claims 12–13) so an operator does not assume "not on the hub" means "not
  externally visible."

## Extraction Notes

- Read the deployment page in full and the linked `docs/mcp_public_internet`
  page in full. Did not re-read `mcp_control`, `mcp_zero_trust`, or
  `mcp_guardrail`; their surfaces are already covered by existing notes and are
  cited only as cross-references.
- All quotes were copied from the source markdown endpoints
  (`/docs/mcp_deployment.md`, `/docs/mcp_public_internet.md`). Where the source
  uses bold emphasis around inline code, the quote carries the same sentence
  with markdown emphasis markers removed; code spans are preserved.
- Candidate-list dispositions (all verified as not the same surface):
  - `docs-litellm-batches-api.md` — batch API rate limiting, unrelated.
  - `docs-litellm-completion-web-search.md` — provider web-search feature,
    unrelated.
  - `docs-litellm-evals-api.md` — Evaluations API, unrelated.
  - `docs-litellm-generate-content.md` — Google `generateContent`
    passthrough, unrelated.
  - `docs-litellm-enterprise.md` — licensing/feature gating only, no topology
    or exposure content.
  - `docs-litellm-completion-input-params.md` — parameter gate, unrelated.
  - `docs-litellm-creating-adapters.md` — format adapters, unrelated.
  - `docs-litellm-files-endpoints.md` — provider `/files` passthrough,
    unrelated.
  - `docs-litellm-bedrock-invoke.md` — Bedrock native invoke passthrough,
    unrelated.
  - `docs-litellm-a2a-iteration-budgets.md` — A2A per-session budgets,
    unrelated to deployment topology or MCP exposure.
- The source is vendor documentation with no production metrics or incident
  evidence, so every claim is graded `emerging`; `confidence_overall` is
  `emerging` for the same reason.
- The page is a living document; the linked public-internet page's inline
  config comment about the default is ambiguous relative to its own comparison
  table. I flagged the ambiguity in Cross-References rather than filing a
  contradiction issue because the default is stated unambiguously as `true` in
  the deployment page and in the linked page's table.
