---
source_url: https://docs.litellm.ai/docs/mcp_oauth
source_type: docs
title: "MCP OAuth — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-10-29
last_checked: 2026-10-29
status: current
confidence_overall: emerging
issue: "#1932"
---

# MCP OAuth (LiteLLM Docs)

> LiteLLM's MCP Gateway defines five outbound OAuth patterns discriminated by
> `auth_type` / `oauth2_flow` (interactive PKCE, M2M client credentials, OBO
> token exchange, transparent passthrough, delegated upstream OAuth), and
> validates browser-supplied `redirect_uri` values against a public origin
> resolved as `PROXY_BASE_URL` → trusted `X-Forwarded-*` (only when
> `use_x_forwarded_for` is true **and** the peer is inside
> `mcp_trusted_proxy_ranges`) → `request.base_url` — with an ingress origin
> mismatch surfacing as the non-obvious `400 {"detail":"invalid_request"}` on
> the MCP page's Connect button.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway,
  "MCP OAuth" page under MCP Gateway → Authentication).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented surface (flow names, config fields, env vars,
  validation rules, error shapes), but documents capability, not measured
  reliability. No production metrics, incident writeups, or independent
  verification on the page. Claims stay at "the gateway documents this surface."
- **Scope**: Covers the OAuth 2.0 patterns LiteLLM supports for MCP servers:
  the five-pattern taxonomy, interactive PKCE discovery/registration/token
  exchange, static-client callback URLs and redirect-URI validation, reverse
  proxy/ingress public-origin resolution, gateway dynamic client registration,
  M2M `client_credentials` token caching, `upstream_token_header` for
  two-credential deployments, `token_validation` / `token_storage_ttl_seconds`,
  and masked `x-mcp-debug-*` diagnostic headers. The passthrough and delegated
  modes are only summarized here and documented in the sibling "MCP OAuth
  Passthrough" page; OBO/ID-JAG have their own pages. Does not cover MCP
  permission/ACL composition (see `docs-litellm-mcp-control.md`) or AWS SigV4
  (see `docs-litellm-mcp-aws-sigv4.md`).

## Extracted Claims

### Claim 1: LiteLLM has five MCP outbound OAuth patterns — interactive PKCE and M2M are both `auth_type: oauth2` discriminated by `oauth2_flow`, while OBO, transparent passthrough, and delegated upstream OAuth are their own `auth_type` values — and `oauth2_flow` is mandatory at startup for every `auth_type: oauth2` server
- **Evidence**: The opening taxonomy table and the "How It Works" / Config
  Reference sections. The taxonomy table names each flow, its `oauth2_flow` or
  `auth_type` selector, use case, and how it works. The `oauth2_flow` Config
  Reference row states the startup failure.
- **Confidence**: emerging (documented vendor surface; no independent
  verification)
- **Quote**: "Every `auth_type: oauth2` server in `config.yaml` must declare its flow via `oauth2_flow`; the passthrough modes are their own `auth_type` values"
- **Quote**: "LiteLLM admission plus a separate forwarded upstream bearer, keeps spend and rate limits."
- **Quote**: "Forwards the client's `Authorization` verbatim, no LiteLLM admission."
- **Quote**: "Required for every `auth_type: oauth2` server in `config.yaml`; the proxy refuses to start if it is missing or invalid."
- **Our assessment**: This is the security-critical taxonomy. The
  `true_passthrough` vs `oauth_delegate` distinction is the one operators must
  get right: both forward an upstream token, but `true_passthrough` performs no
  LiteLLM admission and therefore cannot preserve gateway spend/rate accounting,
  whereas `oauth_delegate` admits the caller first and then forwards a separate
  upstream bearer. The fail-fast on missing `oauth2_flow` is the shipped
  realization of the July stability post's declared-auth fix (see
  Cross-References) and is a good operational property: a misconfigured
  `auth_type: oauth2` server refuses to start rather than silently picking a
  flow.

### Claim 2: Interactive-flow tokens are stored per user under the calling key's `user_id`, not per key or per server
- **Evidence**: Stated immediately after the taxonomy table, with a pointer to
  the per-user credentials page for service-account interaction.
- **Confidence**: emerging
- **Quote**: "Per-user tokens from the interactive flow are stored under the calling key's `user_id`."
- **Our assessment**: This is the key data-model fact for multi-tenant
  deployments: the token cache identity is the end user, not the virtual key.
  It explains why a service-account key used by many humans (or by an agent on
  their behalf) collapses them onto one principal's token — the reason the page
  points readers at the service-account/per-user credentials page. The page does
  not itself resolve the service-account semantics; that is deferred.

### Claim 3: The proxy mediates every interactive PKCE step — resource discovery, authorization-server discovery, RFC 7591 dynamic client registration, authorization, token exchange, and MCP invocation — so the MCP client never talks to the upstream authorization server directly
- **Evidence**: The "Participants" and "Flow Steps" lists under Interactive
  OAuth (PKCE): six numbered steps, each naming which `.well-known` endpoint or
  proxy route handles it.
- **Confidence**: emerging
- **Quote**: "**LiteLLM Proxy** -- Mediates all OAuth discovery, registration, token exchange, and MCP traffic while protecting stored credentials."
- **Quote**: "The client fetches MCP resource metadata from LiteLLM's `.well-known/oauth-protected-resource` endpoint to understand scopes and capabilities."
- **Quote**: "The client retrieves the OAuth server metadata (token endpoint, authorization endpoint, supported PKCE methods) through LiteLLM's `.well-known/oauth-authorization-server` endpoint."
- **Quote**: "The client registers through LiteLLM, which forwards the request to the authorization server (RFC 7591)."
- **Quote**: "LiteLLM exchanges them with the authorization server and returns the issued access/refresh tokens."
- **Our assessment**: The gateway is a full OAuth intermediary, not just a proxy
  that adds a header. That has two consequences worth teaching: (1) the
  client's `.well-known` calls terminate at LiteLLM, so the gateway must
  synthesize or forward metadata correctly (the `per_server_oauth_discovery`
  escape hatch exists for upstreams that publish none); (2) interactive token
  exchange returns tokens to the client, which is a different trust boundary
  from the May townhall's OBO mode (tokens vaulted, never returned) — see
  Cross-References. Not a contradiction, a mode difference.

### Claim 4: Static-client authorization uses two distinct callbacks — the proxy's `<proxy origin>/callback` registered with the upstream IdP, and the MCP client's own callback supplied as `redirect_uri` to `/{mcp_server_name}/authorize` (loopback callbacks need not be registered with the IdP)
- **Evidence**: "Redirect URLs for static OAuth clients" callback table and the
  concrete proxy/desktop example.
- **Confidence**: emerging
- **Quote**: "The client supplies this URL as `redirect_uri` to `/{mcp_server_name}/authorize`."
- **Quote**: "For example, a proxy at `https://llm.example.com` uses `https://llm.example.com/callback` as its IdP callback. A desktop client's local callback, such as `http://localhost:33418/callback`, is supplied to LiteLLM and does not need to be registered with the upstream IdP."
- **Our assessment**: The two-hop callback structure is the thing operators
  most often get wrong when the IdP reports a redirect mismatch: the IdP must
  only know the proxy's `/callback`, while the client's localhost/desktop
  callback is validated by LiteLLM. The `PROXY_BASE_URL` value determines the
  first URL exactly, which is why the ingress section follows immediately.

### Claim 5: For MCP OAuth endpoints, LiteLLM resolves its public origin in a fixed order — `PROXY_BASE_URL` verbatim, then `X-Forwarded-Proto/Host/Port` only when `use_x_forwarded_for` is true **and** the peer IP is inside `mcp_trusted_proxy_ranges`, then `request.base_url` — and enabling `use_x_forwarded_for` without the trust range makes the headers untrusted
- **Evidence**: "Origin resolution order" enumerated list plus the explicit
  warning about the double condition and the `general_settings` config example.
- **Confidence**: emerging
- **Quote**: "For MCP OAuth endpoints, LiteLLM resolves the proxy's public origin in this order:"
- **Quote**: "If `use_x_forwarded_for` is enabled without `mcp_trusted_proxy_ranges`, the headers are not trusted (there is no way to distinguish a trusted reverse proxy from a direct attacker)."
- **Quote**: "When `PROXY_BASE_URL` is set, LiteLLM uses it directly and skips the `X-Forwarded-*` trust path described below."
- **Our assessment**: This is the precise condition the Prospector asked for:
  the `X-Forwarded-*` path is silently ignored unless **both** flags are
  satisfied. A common deployment sets `use_x_forwarded_for: true` for other
  proxy features but forgets `mcp_trusted_proxy_ranges`; MCP OAuth then falls
  through to the pod-internal `request.base_url` and the same-origin check fails.
  The peer-IP allowlist is the security-relevant difference from a naive
  `X-Forwarded-*` trust model — it is the same "don't trust client-controlled
  origin headers" principle as the Host-header CVE, implemented as an explicit
  trust boundary (see Cross-References).

### Claim 6: On an ingressed deployment whose origin resolves to the internal pod address, the MCP page's Connect button fails with `400 Bad Request` and `{"detail":"invalid_request"}`, and the proxy logs the rejected value as `MCP OAuth: rejecting redirect_uri '<value>'` at warning level
- **Evidence**: "Reverse proxy and ingress configuration" intro plus "Identify
  the MCP client's callback URL" and the "Troubleshoot callback errors" section.
- **Confidence**: emerging
- **Quote**: "If the proxy resolves to its internal address (`http://<pod-ip>:4000`) the same-origin check fails and the **Connect** button on the MCP server page returns `400 Bad Request` with `{"detail":"invalid_request"}`."
- **Quote**: "The proxy also logs the rejected value as `MCP OAuth: rejecting redirect_uri '<value>'` at warning level."
- **Our assessment**: This is the concrete operational failure mode: a generic
  400 with `invalid_request` on the MCP page is not an OAuth-flow bug and not a
  client bug — it is almost always an origin-resolution mismatch. The warning
  log is the only place the actual rejected value appears; `detail.redirect_uri`
  appears on origin-mismatch responses. This belongs in a runbook exactly as
  stated.

### Claim 7: Redirect-URI validation differs by callback class — loopback accepts any port and path, trusted origins must be HTTPS with wildcard subdomains excluding the apex, and fragments, embedded credentials, backslashes in the host, and query strings on native schemes are rejected
- **Evidence**: The "Redirect URI validation" rules table and the
  `MCP_TRUSTED_REDIRECT_ORIGINS` / `MCP_TRUSTED_NATIVE_REDIRECT_URIS` prose.
- **Confidence**: emerging
- **Quote**: "Uses HTTP or HTTPS with `localhost`, an address in `127.0.0.0/8`, or `::1`. Any port and path are accepted."
- **Quote**: "A wildcard such as `*.tools.example.com` matches subdomains, including `a.tools.example.com`, but excludes `tools.example.com` itself."
- **Quote**: "Callback URLs must include a host and must not contain a fragment (`#...`), embedded credentials (`user:pass@host`), or a backslash in the host. Custom URI schemes require a trusted native callback entry. Native callback URIs must not contain a query string."
- **Quote**: "Include the callback path; `myclient://auth/callback` and `myclient://auth/callback/` are distinct entries."
- **Our assessment**: The wildcard-excludes-apex rule is a classic allowlist
  footgun: `*.tools.example.com` does not authorize `tools.example.com`, so an
  operator who lists a wildcard and then uses the apex gets a 400. The native
  scheme exact-match including trailing slash is similarly brittle. Loopback
  being accepted on any port is what makes desktop MCP clients work out of the
  box, but it is also the broadest exemption — worth pairing with the threat
  model in Claim 8 in the guide.

### Claim 8: The same-origin check exists to stop an admin-phishing flow that bounces an upstream authorization code through an attacker-controlled host, and LiteLLM deliberately prefers an operator-declared `PROXY_BASE_URL` over inferring the origin from headers because the check itself is not relaxed
- **Evidence**: "Why the same-origin check exists" section, including the
  attacker scenario and the `PROXY_BASE_URL` design rationale.
- **Confidence**: emerging
- **Quote**: "The check exists to stop an attacker from phishing a logged-in admin into a link that bounces an authorization code, for an upstream OAuth-protected MCP server such as GitHub or Slack, through an attacker-controlled host."
- **Quote**: "Same-origin (plus an explicit ops allowlist) is the threat-model-safe equivalent of the loopback-only rule used for native MCP clients."
- **Quote**: "`PROXY_BASE_URL` is the right escape hatch for ingressed deployments because the operator is declaring the proxy's true public origin out of band, rather than asking the proxy to infer it from headers an attacker might be able to set. The check itself is not relaxed."
- **Our assessment**: The page states the threat model explicitly, which is rare
  and valuable. The recommendation to use `PROXY_BASE_URL` is not just
  convenience — it removes origin inference from attacker-influenced inputs.
  This is directly transferable to any gateway that must compare a
  browser-supplied redirect target against its own identity.

### Claim 9: The aggregate `/mcp` endpoint uses gateway-level dynamic client registration with one to four `redirect_uris` (max 256 characters each), and `/authorize` requires an exact match to a registered value or returns a top-level `invalid_request`
- **Evidence**: "Gateway Dynamic Client Registration" section with limits,
  exact-match rule, and the unregistered error JSON.
- **Confidence**: emerging
- **Quote**: "The aggregate `/mcp` endpoint uses gateway-level registration through `POST /register`, `GET /authorize`, and `POST /token`. Each registration accepts one to four `redirect_uris`, with a maximum of 256 characters per URI."
- **Quote**: "For this flow, the `redirect_uri` supplied to `/authorize` must exactly match a registered value. An unregistered value returns `HTTP 400` with the following top-level JSON fields:"
- **Our assessment**: The exact-match requirement is stricter than the per-server
  validation rules: gateway DCR stores a per-client allowlist, so a
  previously-valid loopback URL with a different port is rejected unless it was
  one of the registered values. The 1–4 / 256-character limits are quotas an
  operator should know before debugging why a client's registration fails.

### Claim 10: Per-server static registration returns placeholder credentials — `client_id` equal to the server name, `client_secret` equal to `dummy` — and stores no client-specific callback allowlist, so authorization falls back to the per-server validation rules
- **Evidence**: "For static clients" paragraph plus the Gateway DCR section's
  contrast statement and the verification example showing the placeholder
  response.
- **Confidence**: emerging
- **Quote**: "For static clients, LiteLLM handles `POST /{mcp_server_name}/register` locally. It returns the MCP server name as `client_id`, `dummy` as `client_secret`, and the client's submitted `redirect_uris`. LiteLLM uses the configured upstream credentials for authorization and token exchange."
- **Quote**: "Per-server static registration returns placeholder credentials and does not store a client-specific callback allowlist. Its authorization endpoint applies the per-server validation rules described above."
- **Our assessment**: The placeholder credentials are safe only because the
  proxy substitutes the real upstream credentials; a reader who assumes the
  returned `client_secret` is meaningful could misdiagnose. The absence of a
  stored callback allowlist is the important security nuance: per-server
  validation is origin/loopback/native-based, not per-registration, so it is
  broader than the aggregate `/mcp` DCR path.

### Claim 11: `per_server_oauth_discovery: true` makes LiteLLM publish discovery documents for an upstream that publishes none, but is accepted only with `auth_type: oauth2`, `oauth2_flow: authorization_code`, and no `delegate_auth_to_upstream`
- **Evidence**: The paragraph after the static-client config example, naming
  Microsoft Graph behind `ms-365-mcp-server` as the motivating case, plus the
  acceptance constraint.
- **Confidence**: emerging
- **Quote**: "add `per_server_oauth_discovery: true` so LiteLLM publishes the discovery documents for `/{mcp_server_name}/mcp` itself, with its own `/{mcp_server_name}/authorize` and `/{mcp_server_name}/token` endpoints fronting the provider URLs above."
- **Quote**: "It is accepted only with `auth_type: oauth2`, `oauth2_flow: authorization_code`, and no `delegate_auth_to_upstream`."
- **Our assessment**: This is the escape hatch for providers that do not publish
  OAuth metadata, and the constraint is narrow by design: it only applies to the
  interactive code flow with proxy-managed upstream credentials. It is mutually
  exclusive with delegation because delegated mode is supposed to let the
  upstream own authorization; synthesizing discovery there would blur that
  boundary.

### Claim 12: M2M auth uses the `client_credentials` grant with proxy-managed token fetch/cache/refresh, caching in memory for `expires_in - 60s`
- **Evidence**: "Machine-to-Machine (M2M) Auth" intro, "How It Works" four
  steps, and the config.yaml example.
- **Confidence**: emerging
- **Quote**: "LiteLLM automatically fetches, caches, and refreshes OAuth2 tokens using the `client_credentials` grant. No manual token management required."
- **Quote**: "The access token is cached in-memory with TTL = `expires_in - 60s`"
- **Quote**: "When the token expires, LiteLLM fetches a new one automatically."
- **Our assessment**: The 60-second safety margin is a sensible skew to avoid
  using a token that expires in flight. Because the cache is in-memory, each
  proxy worker fetches its own token; the page does not claim a shared cache, so
  operators should not assume one token fetch per upstream per deployment. The
  "no manual token management" claim is the vendor's capability statement, not a
  reliability guarantee under provider outages.

### Claim 13: `upstream_token_header` lets two credentials coexist on one request by moving the LiteLLM-minted token to a named header while leaving `static_headers` untouched, and an invalid header name fails startup / is rejected with 400 by the management API
- **Evidence**: "Sending the token on a different header" section with the
  two-credential example and the validation statement.
- **Confidence**: emerging
- **Quote**: "Set `upstream_token_header` to name the header the resolved token should use. Anything you configure under `static_headers` is then left alone, so a second credential reaches the server behind the gateway untouched."
- **Quote**: "The value must be a valid HTTP header name; the proxy refuses to start on a malformed one, and the management API rejects it with a 400."
- **Quote**: "In the UI the same setting is the **Token Header** field in the OAuth section of the MCP server form, and it applies to the interactive flow and the token-exchange modes as well as M2M."
- **Our assessment**: This solves the gateway-behind-gateway credential
  collision: the outer API gateway reads its own header while the inner MCP
  server still receives a bearer on `Authorization`. The startup/API validation
  is a good fail-fast property; the setting is broader than M2M, which matters
  for interactive and token-exchange deployments too.

### Claim 14: `token_validation` asserts key-value rules against the post-exchange token response (e.g. a tenant claim) and `token_storage_ttl_seconds` overrides the per-user token-cache TTL
- **Evidence**: The two Config Reference rows immediately after `scopes`.
- **Confidence**: emerging
- **Quote**: "Dict of key-value rules checked against the OAuth token response after the `/token` exchange. Any rule mismatch fails the exchange with `token_validation_failed`. Useful for asserting a tenant claim like `{"team.enterprise_id": "T12345"}`."
- **Quote**: "Override the TTL for the per-user token cache (interactive flow). If unset, LiteLLM uses `expires_in - buffer` from the token response."
- **Our assessment**: `token_validation` is a post-exchange authorization gate,
  not a pre-exchange request filter — it lets the gateway reject a token that is
  cryptographically valid but belongs to the wrong tenant. That is high-value for
  Ch06 multi-tenant isolation. The TTL override is for shortening (or extending)
  per-user token lifetime independent of the IdP's `expires_in`.

### Claim 15: `x-litellm-mcp-debug: true` returns masked `x-mcp-debug-*` response headers, and `SAME_AS_LITELLM_KEY` on `x-mcp-debug-oauth2-token` is the signature that the LiteLLM API key is being forwarded upstream instead of an OAuth token
- **Evidence**: "Debugging OAuth" section, the response-header table, and the
  two worked examples ("healthy OAuth2 passthrough" and "LiteLLM key leaking").
- **Confidence**: emerging
- **Quote**: "Add the `x-litellm-mcp-debug: true` header to your MCP client request."
- **Quote**: "The response includes these headers (all sensitive values are masked):"
- **Quote**: "The OAuth2 token (masked). Shows `SAME_AS_LITELLM_KEY` if the LiteLLM key is leaking."
- **Quote**: "The `Authorization` header carries the LiteLLM API key instead of an OAuth2 token. The OAuth2 flow never ran because the client already had an `Authorization` header set."
- **Quote**: "The server has `client_id`/`client_secret`/`token_url` configured so LiteLLM is fetching a machine-to-machine token instead of using the per-user OAuth2 token. To use per-user tokens, remove the client credentials from the server config."
- **Our assessment**: This is the single most useful runbook addition: a
  remote-hosted proxy's logs may be unavailable, and `SAME_AS_LITELLM_KEY`
  distinguishes a credential-plumbing bug from a flow bug. The cause — a static
  `Authorization` header in the client config blocking OAuth discovery — is a
  concrete misconfiguration, not a gateway defect. The M2M-vs-user-token symptom
  (`x-mcp-debug-auth-resolution: m2m-client-credentials`) is the second
  high-value diagnostic.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(https://docs.litellm.ai/docs/mcp_oauth).

### Interactive PKCE config.yaml (from "Interactive OAuth (PKCE) → Setup")

```yaml
mcp_servers:
  github_mcp:
    url: "https://api.githubcopilot.com/mcp"
    auth_type: oauth2
    oauth2_flow: authorization_code
    client_id: os.environ/GITHUB_OAUTH_CLIENT_ID
    client_secret: os.environ/GITHUB_OAUTH_CLIENT_SECRET
```

### Static OAuth client config.yaml (from "Redirect URLs for static OAuth clients")

```yaml
mcp_servers:
  jira_mcp:
    url: https://mcp.example.com/mcp
    auth_type: oauth2
    oauth2_flow: authorization_code
    client_id: os.environ/JIRA_OAUTH_CLIENT_ID
    client_secret: os.environ/JIRA_OAUTH_CLIENT_SECRET
    authorization_url: https://idp.example.com/oauth2/authorize
    token_url: https://idp.example.com/oauth2/token
    scopes:
      - read:jira-work
```

Attribution: "Redirect URLs for static OAuth clients → Configure the upstream
OAuth application".

### Trusted redirect origins env vars (from "Identify the MCP client's callback URL")

```bash
# Trusted HTTPS client hosts, with optional ports or wildcard subdomains.
export MCP_TRUSTED_REDIRECT_ORIGINS='app.example.com,*.tools.example.com'
# Trusted native client callback URIs.
export MCP_TRUSTED_NATIVE_REDIRECT_URIS='myclient://auth/callback'
```

### Origin mismatch response (selected fields, from "Troubleshoot callback errors")

```json
{
  "detail": {
    "error": "invalid_request",
    "error_description": "redirect_uri origin (https://app.example.com) does not match the proxy origin. host/port: redirect_uri 'app.example.com' does not match the proxy origin",
    "redirect_uri": "https://app.example.com/oauth/callback"
  }
}
```

### Ingress X-Forwarded trust config (from "Origin resolution order")

```yaml
general_settings:
  use_x_forwarded_for: true
  mcp_trusted_proxy_ranges:
    - "10.0.0.0/8"      # your ingress / load-balancer CIDR(s)
```

### Static registration response (from "Verify the configuration")

```json
{"client_id":"jira_mcp","client_secret":"dummy","redirect_uris":["http://localhost:33418/callback"]}
```

### M2M config.yaml (from "Machine-to-Machine (M2M) Auth → Config.yaml Setup")

```yaml
mcp_servers:
  my_mcp_server:
    url: "https://my-mcp-server.com/mcp"
    auth_type: oauth2
    oauth2_flow: client_credentials
    client_id: os.environ/MCP_CLIENT_ID
    client_secret: os.environ/MCP_CLIENT_SECRET
    token_url: "https://auth.example.com/oauth/token"
    scopes: ["mcp:read", "mcp:write"]  # optional
```

### Two-credential gateway config (from "Sending the token on a different header")

```yaml
mcp_servers:
  my_mcp_server:
    url: "https://my-mcp-server.com/mcp"
    auth_type: oauth2
    oauth2_flow: client_credentials
    client_id: os.environ/MCP_CLIENT_ID
    client_secret: os.environ/MCP_CLIENT_SECRET
    token_url: "https://auth.example.com/oauth/token"
    upstream_token_header: "esb-oauth"
    static_headers:
      Authorization: "Bearer os.environ/UPSTREAM_MCP_TOKEN"
```

The page then describes the resulting request headers (verbatim):

```
esb-oauth: Bearer <the token LiteLLM minted>
Authorization: Bearer <the token you configured>
```

### Debug response headers — leaking-key example (from "Reading the Debug Response Headers")

```
x-mcp-debug-inbound-auth: authorization=Bearer****1234
x-mcp-debug-oauth2-token: Bearer****1234 (SAME_AS_LITELLM_KEY - likely misconfigured)
x-mcp-debug-auth-resolution: oauth2-passthrough
x-mcp-debug-outbound-url: https://mcp.atlassian.com/v1/mcp
x-mcp-debug-server-auth-type: oauth2
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  accounting at `POST /v1/batches`; no OAuth flow or redirect-URI content.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**: provider
  web-search support matrix; unrelated to MCP OAuth.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: Evaluations API
  CRUD/grader contract; no auth-flow content.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` passthrough fields; no OAuth.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: Enterprise license
  tiers/features; no MCP OAuth mechanics.
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**:
  completion parameter support gate; unrelated to auth.
- `source-notes/docs-litellm-files-endpoints.md` — **dismissed**: provider
  `/files` passthrough; no OAuth.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock Invoke
  passthrough with bearer-in-AWS-auth-slot; a different auth surface (client→LiteLLM
  passthrough), not MCP OAuth flows.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session iteration/budget controls; no OAuth flow.
- `source-notes/docs-litellm-mcp-aws-sigv4.md` — **cited**: the sibling MCP
  outbound auth mode (`auth_type: aws_sigv4`, Claim 1); this page covers the
  OAuth modes and does not overlap SigV4 signing.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 2** — that
    note establishes that MCP outbound auth is a first-class `auth_type` enum
    and that `oauth2` is PKCE-or-M2M discriminated by `oauth2_flow`, while
    leaving the dedicated OAuth flow pages un-deep-dived. This page is that
    deep-dive: it adds the per-flow mechanics, the `oauth2_token_exchange`
    OBO mode, and the two separate passthrough `auth_type` values
    (`true_passthrough`, `oauth_delegate`) with their admission/accounting
    difference (Claim 1 here).
  - `source-notes/blog-litellm-may-townhall-updates.md` **Claim 6** — the May
    townhall announced on-behalf-of MCP OAuth with tokens vaulted at the proxy,
    never returned to the client, with transparent refresh. This page is the
    shipped config-level detail: OBO is `auth_type: oauth2_token_exchange`, and
    `oauth_delegate` keeps a separate forwarded upstream bearer while preserving
    spend/rate limits (Claim 1). The May wording applies to the OBO/delegated
    modes; this page's interactive PKCE flow returns tokens to the client
    (Claim 3), so the two are mode-scoped, not in conflict.
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 3** — the July
    fix replaced inference-from-fields with a declared, typed auth mode and an
    exhaustive match. This page's requirement that every `auth_type: oauth2`
    server declare `oauth2_flow` and refuse startup if missing/invalid (Claim 1)
    is the same declared-auth design at the MCP OAuth layer. One nuance stated
    on this page: legacy database rows created before the field existed still
    fall back to inference at request time; config entries are never inferred.
    That is consistent with the July note's config-scoped claim, not a
    contradiction.
  - `source-notes/docs-litellm-mcp-aws-sigv4.md` **Claim 1** — confirms that MCP
    outbound auth has multiple autonomous modes selected by `auth_type`; this
    page supplies the OAuth half and does not restate SigV4 signing.

- **Contradicts**: No contradiction issue filed. The only apparent tension is
  between the May townhall's "OAuth tokens are vaulted at the proxy — never
  returned to the client" (Claim 6 there) and this page's interactive PKCE step
  "returns the issued access/refresh tokens" to the client (Claim 3 here). These
  describe different modes: the May statement is about on-behalf-of/delegated
  OAuth, while this page's interactive flow is explicitly user-facing consent
  with per-user token storage (Claim 2). Same product, different `auth_type`;
  this is a conditioning variable, not a claim-level opposition, so no
  contradiction issue was filed per MINER §4a.

- **Extends / thematically adjacent**:
  - `source-notes/docs-litellm-mcp-control.md` — its Source Context explicitly
    says it does not deep-dive OAuth transport details. This page is the
    complementary OAuth half; permission composition (six-level intersection,
    tool pinning, rate limits) remains in that note and is not restated here.
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md` — orthogonal
    MCP security surface: stdio `command` input validation vs outbound OAuth
    credential handling. No claim conflict; both are part of the MCP threat
    model.
  - `source-notes/failure-litellm-host-header-auth-bypass.md` — same
    "don't let a client-controlled header decide a security-sensitive origin"
    principle. That note's Root Cause / Fix detail C is about auth route
    resolution from the `Host`-reconstructed URL vs the ASGI scope path; this
    page's Claim 5 is about OAuth origin resolution, where LiteLLM makes
    `PROXY_BASE_URL` authoritative and gates `X-Forwarded-*` on both
    `use_x_forwarded_for` and a peer-IP trust range. The hardened analogue, not
    a contradiction. Cite by section name, not a numbered claim (that note uses
    Vulnerability/Root-cause detail sections rather than `### Claim N`).

- **Novel**: Entirely new to the corpus (grep-verified before writing): the
  full MCP OAuth pattern taxonomy including `true_passthrough` and
  `oauth_delegate`; per-user token storage under the calling key's `user_id`;
  the six-step interactive PKCE mediation flow; static-client two-callback
  design; the `PROXY_BASE_URL` → trusted `X-Forwarded-*` → `request.base_url`
  origin-resolution order with its double trust condition; the ingress
  `400 invalid_request` failure signature and warning log; redirect-URI
  validation rules (loopback any port/path, wildcard-excludes-apex, native
  exact-match, fragment/credential/backslash rejection); the admin-phishing
  threat model; aggregate-`/mcp` gateway DCR limits and exact-match requirement;
  per-server static registration placeholder credentials and missing callback
  allowlist; `per_server_oauth_discovery`; M2M in-memory TTL caching;
  `upstream_token_header`; `token_validation` / `token_storage_ttl_seconds`; and
  the masked `x-mcp-debug-*` diagnostics.

## Guide Impact

- **Chapter 06 (Security and Trust)** — MCP OAuth delegation: Add the five-mode
  taxonomy with "who holds the token" stated per mode, and make the
  `true_passthrough` vs `oauth_delegate` distinction explicit: `true_passthrough`
  forwards the client's `Authorization` verbatim with no LiteLLM admission, so
  gateway spend/rate accounting is bypassed; `oauth_delegate` admits the caller
  and forwards a separate upstream bearer while preserving spend/rate limits
  (Claim 1). Add the redirect-URI threat model (admin phishing via
  attacker-controlled host, Claim 8) and the validation rules (Claim 7),
  including the wildcard-excludes-apex and native-trailing-slash footguns. Add
  `token_validation` as a post-exchange tenant-claim gate (Claim 14), and warn
  that per-server static registration returns `client_id` = server name /
  `client_secret` = `dummy` and stores no client callback allowlist (Claim 10).

- **Chapter 05 (LLM Ops Reliability)** — Gateway behind TLS-terminating
  ingress: Add the public-origin resolution order and the exact trust condition
  for `X-Forwarded-*` (`use_x_forwarded_for` **and** peer in
  `mcp_trusted_proxy_ranges`), with `PROXY_BASE_URL` as the recommended out-of-band
  declaration (Claim 5). Note that a missing trust range silently falls back to
  the pod-internal `request.base_url`, and that `PROXY_BASE_URL` must be a full
  origin with no path or trailing slash. Add the `oauth2_flow` startup
  fail-fast (Claim 1) and the M2M in-memory cache with `expires_in - 60s` TTL
  (Claim 12), noting the cache is not documented as shared across workers.

- **Chapter 03 (Runbooks and Agents)** — MCP OAuth troubleshooting: Add the
  Connect-button failure signature (`400`, `detail.error=invalid_request`,
  warning log `MCP OAuth: rejecting redirect_uri '<value>'`) and the
  `detail.redirect_uri` field as the first diagnostic for origin mismatches
  (Claim 6). Add the `x-litellm-mcp-debug: true` masked diagnostics and the
  `SAME_AS_LITELLM_KEY` / `m2m-client-credentials` signals, with their known
  causes — a static `Authorization` header blocking OAuth discovery, or
  leftover `client_id`/`client_secret`/`token_url` forcing M2M (Claim 15). Add
  `per_server_oauth_discovery` as the fix when the upstream publishes no
  metadata (Claim 11).

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/mcp_oauth`, HTTP 200, no paywall), a living
  Docusaurus page. All `Quote` fields are contiguous verbatim strings from the
  fetched page; no quote was spliced across non-adjacent sentences. Markdown
  link syntax and bold markers were avoided inside quotes by quoting only the
  contiguous plain-text fragment that carries the meaning. Concrete artifacts
  are character-for-character from the page with attribution.
- Linked sibling pages (MCP OAuth Passthrough, MCP OBO Auth, MCP ID-JAG, MCP
  Per-User and Per-Key Credentials, MCP troubleshooting) were not deep-dived.
  This page explicitly defers the passthrough/delegated and OBO mechanics to
  them; the extraction stays on the material this page states, per its own
  scope statement.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Primary cross-reference
  verification (MINER §4b) re-read the cited claims in
  `docs-litellm-gateway-auth-reference.md` (Claim 2),
  `blog-litellm-may-townhall-updates.md` (Claim 6),
  `blog-litellm-july-stability-update.md` (Claim 3), and
  `docs-litellm-mcp-aws-sigv4.md` (Claim 1) before writing them; claim numbers
  and quoted passages were confirmed against those notes. The
  `failure-litellm-host-header-auth-bypass.md` reference is cited by section
  name because that note uses Vulnerability/Root-cause detail headings rather
  than numbered `### Claim N` headings.
- **Contradiction decision (no issue filed).** The May-townhall OBO statement
  ("tokens are vaulted at the proxy — never returned to the client") and this
  page's interactive PKCE step ("returns the issued access/refresh tokens") are
  different OAuth modes on the same product, not opposing claims. This is a
  conditioning variable per MINER §4a's "when NOT to file" guidance. No other
  existing note makes a claim about MCP OAuth origin resolution, redirect-URI
  validation, or these `auth_type` modes; no contradiction issue was needed.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes:
  first-party capability documentation with concrete config/env/validation
  detail but no measured reliability, no failure writeups, and no independent
  verification. The page can change between releases.
- `date_published` is unknown (living vendor docs); `date_extracted` and
  `last_checked` are both 2026-10-29.
