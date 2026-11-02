---
source_url: https://docs.litellm.ai/docs/mcp_obo_auth
source_type: docs
title: "MCP OBO Auth — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-11-02
last_checked: 2026-11-02
status: current
confidence_overall: emerging
issue: "#1945"
---

# MCP OBO Auth (LiteLLM Docs)

> LiteLLM's `oauth2_token_exchange` OBO mode exchanges a caller's inbound bearer
> for a scoped MCP-server token using either RFC 8693 (`rfc8693` default) or
> Microsoft Entra's RFC 7523 `jwt-bearer` dialect (`entra_obo`), caches the
> result per `(subject token, MCP server ID)` until expiry, and fails closed with
> a `401` challenge rather than ever forwarding an unexchanged request.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP OBO
  Auth" page under MCP Gateway → Authentication).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented surface (config field requirements, wire
  request shapes, cache-key semantics, error behavior), but documents capability,
  not measured reliability. No production metrics, incident writeups, or
  independent verification on the page. Claims stay at "the gateway documents
  this surface."
- **Scope**: Covers OAuth 2.0 On-Behalf-Of for MCP servers: the exchange flow,
  the `oauth2_token_exchange` config fields, the RFC 8693 request shape, the
  Microsoft Entra `entra_obo` profile (RFC 7523 `jwt-bearer`), inbound header
  splitting, `upstream_token_header` for two-credential deployments, cross-origin
  redirect behavior, per-user exchange caching, the no-subject-token fail-closed
  path, the separate M2M entry requirement, and a troubleshooting table. It does
  not re-document interactive PKCE/M2M mechanics (see
  `docs-litellm-mcp-oauth.md`) or the passthrough modes (see
  `docs-litellm-mcp-oauth-passthrough.md`).

## Extracted Claims

### Claim 1: OBO exchanges the caller's incoming bearer at the identity provider and forwards only the exchanged, MCP-scoped token to the MCP server
- **Evidence**: The "How It Works" five-step list names the caller token, the
  RFC 8693 `subject_token` role, the exchange call, the forwarding step, and the
  cache.
- **Confidence**: emerging (documented vendor surface; no measured behavior)
- **Quote**: "OAuth 2.0 On-Behalf-Of (OBO) auth lets LiteLLM exchange a user's incoming bearer token for a scoped token that is valid for a specific MCP server."
- **Quote**: "LiteLLM forwards only the exchanged scoped token to the MCP server."
- **Our assessment**: This is the core delegation property: the MCP server never
  receives the user's raw inbound token, and the gateway is an active token
  authority rather than a relay. That is a materially different trust posture
  from `true_passthrough`/`oauth_delegate`, where the caller's token is forwarded
  verbatim. The guide should present OBO as the "mint a scoped token" option in
  the MCP auth mode matrix, not as a variant of passthrough.

### Claim 2: `auth_type: oauth2_token_exchange` requires only `token_exchange_endpoint`, `client_id`, and `client_secret`; `audience` is recommended and `scopes`, `subject_token_type`, `upstream_token_header`, and `token_exchange_profile` are optional
- **Evidence**: The Config Fields table marks exactly three fields "Yes" and
  `audience` "Recommended", with the rest "Optional" and per-field descriptions.
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "Must be `oauth2_token_exchange`."
- **Quote**: "The identity provider endpoint that accepts RFC 8693 token exchange requests."
- **Quote**: "Resource identifier for the MCP server. LiteLLM sends this as the token exchange `audience`."
- **Quote**: "Scopes LiteLLM requests for the exchanged token. LiteLLM joins the list into the OAuth `scope` parameter."
- **Quote**: "RFC 8693 subject token type. Defaults to `urn:ietf:params:oauth:token-type:access_token`."
- **Our assessment**: The required set is smaller than an operator might expect —
  no token URL/authorization URL, because the exchange endpoint is the only IdP
  interaction. The recommended `audience` is the audience-scoping control; the
  page treats it as optional at the schema level but security-relevant in
  practice, and omitting it is the most likely way to end up with a broadly
  scoped exchanged token. `token_exchange_profile` is the dialect switch that
  Claim 4 expands.

### Claim 3: The default `rfc8693` exchange is a form-encoded POST with `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`, the caller bearer as `subject_token`, plus `subject_token_type`, `client_id`, `client_secret`, `audience`, and space-joined `scope`
- **Evidence**: The "Token Exchange Request" section gives the full form-encoded
  request and states it is sent once per uncached `(subject token, MCP server)`
  pair.
- **Confidence**: emerging (documented wire format)
- **Quote**: "For each uncached subject token and MCP server pair, LiteLLM sends a form-encoded request like this to `token_exchange_endpoint`:"
- **Quote**: "Your identity provider should return an access token:"
- **Our assessment**: This is the concrete implementation detail the overview page
  omits. It is directly usable for IdP-side allowlisting/debugging: the request
  is indistinguishable from a standard RFC 8693 token-exchange call, with the
  client credentials embedded in the form body (not HTTP Basic). Operators can
  reproduce it with `curl` to separate a LiteLLM bug from an IdP policy
  rejection.

### Claim 4: `token_exchange_profile: entra_obo` switches to RFC 7523 `jwt-bearer` — the caller token rides as `assertion`, `requested_token_use=on_behalf_of` turns it into delegation, and `audience`/`subject_token_type` are silently unused
- **Evidence**: The "Microsoft Entra ID (Azure AD)" section states Entra does
  not implement RFC 8693, gives the jwt-bearer request shape, and explicitly
  names the two fields that become inert.
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "Its On-Behalf-Of flow uses the RFC 7523 `jwt-bearer` grant instead: the caller's token rides as `assertion` rather than `subject_token`, there's no `audience` parameter, and a Microsoft-only `requested_token_use=on_behalf_of` extension is what turns the grant into a delegation rather than a plain jwt-bearer exchange."
- **Quote**: "`audience` and `subject_token_type` are unused with `entra_obo`: Entra has no audience parameter (the target resource goes in `scope` instead), and the jwt-bearer grant doesn't examine subject token type."
- **Our assessment**: This is the highest-value operational gotcha on the page:
  the same `auth_type` accepts two incompatible wire dialects, and the profile
  switch silently discards config fields that were meaningful in the default
  profile. An operator who copies an RFC 8693 config to Entra and only adds
  `token_exchange_profile` will find `audience` ignored and the target resource
  must instead appear as `<app-id-uri>/.default` in `scopes`. This is a concrete
  "declare the dialect" case, consistent with the corpus's declared-auth theme.

### Claim 5: Under Entra OBO the caller's token must be issued for LiteLLM's app registration as its `aud`; a harness authenticated to another app must first request a token for LiteLLM's scope
- **Evidence**: The note callout immediately after the Entra config example.
- **Confidence**: emerging (documented vendor requirement)
- **Quote**: "The caller's token must be issued for LiteLLM's app registration, not some other Entra app. If your harness authenticates against a different app registration, have it request a token for this app's scope first, then send that token to LiteLLM."
- **Our assessment**: This is an identity-plane constraint, not a LiteLLM
  setting: the exchange fails if the incoming token's audience is another Entra
  app. It is the Entra analogue of the passthrough page's "don't widen `aud`"
  rule — except here the correct move is to obtain a correctly scoped inbound
  token, not to relax the exchange. Runbooks should check the inbound token's
  `aud` before blaming the exchange endpoint.

### Claim 6: Inbound requests must carry the user token in `Authorization` while the LiteLLM key moves to `x-litellm-api-key` — the same split applies to Responses API MCP tool `headers`
- **Evidence**: The "Calling an OBO MCP Server" section gives a direct MCP
  `curl` example and a Responses API example with both headers inside
  `tools[].headers`, plus a tip for single-header clients.
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "For direct MCP calls, keep the LiteLLM key in `x-litellm-api-key` and leave `Authorization` for the user token:"
- **Quote**: "If the MCP client can only send one `Authorization` header, use `x-litellm-api-key` for the LiteLLM key and reserve `Authorization` for the user's token. LiteLLM needs the user token as the OBO `subject_token`."
- **Our assessment**: The header assignment is a hard requirement, not a style
  preference: putting the LiteLLM key in `Authorization` leaves no
  `subject_token`, which Claim 10 turns into a 401. The Responses API form shows
  this is per-tool header configuration, so an operator must remember it on the
  nested `tools[].headers` object rather than the outer request. Compare the
  passthrough page's leak-defense rule: there a lone `Authorization` is treated
  as admission and withheld; here `Authorization` is the user token and
  `x-litellm-api-key` is admission.

### Claim 7: `upstream_token_header` lets the exchanged token ride on a custom header while `static_headers` carries a separate shared credential, so two credentials coexist on one upstream request
- **Evidence**: "Sending the exchanged token on a different header" describes the
  gateway-behind-gateway case, gives a config with `upstream_token_header:
  "esb-oauth"` plus `static_headers.Authorization`, and shows the resulting
  request.
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "Set `upstream_token_header` to name the header the exchanged token should use. Anything under `static_headers` is then left alone, so a shared credential still reaches the server behind the gateway."
- **Quote**: "Each upstream request then carries both, with the exchanged token scoped to the calling user:"
- **Our assessment**: This solves the same header-collision problem the MCP OAuth
  overview records for the other flows, but here the per-user token is
  LiteLLM-minted rather than caller-forwarded. The example's split — per-user
  exchanged token on `esb-oauth`, shared bearer on `Authorization` — is a useful
  reference for outer-gateway deployments that own `Authorization`.

### Claim 8: A cross-origin upstream redirect drops the custom `upstream_token_header` rather than forwarding it, so a redirecting upstream loses the credential on the second hop
- **Evidence**: The paragraph immediately after the two-credential example.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "If a redirect from the upstream crosses origin, the custom header is dropped rather than forwarded, the same way HTTP clients drop `Authorization`. An upstream that legitimately redirects across origins will not see the credential on the second hop."
- **Our assessment**: A concrete, low-visibility failure mode: the first hop
  succeeds and the redirect target returns an auth error, which reads like a
  server bug. The page frames it as expected HTTP-client behavior, so the fix is
  to avoid cross-origin redirects in the upstream route, not to escalate to
  LiteLLM. Worth a runbook line because the symptom is one hop removed from the
  cause.

### Claim 9: Exchanged tokens are cached per `(subject token, MCP server ID)` until expiry, giving per-user isolation and reuse across requests
- **Evidence**: The "Caching Behavior" section lists the two cache-key
  components, explains the per-user consequence, and defines the TTL.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "This means two different users get separate exchanged tokens, while repeated calls from the same user to the same MCP server reuse the cached token until it expires."
- **Quote**: "The cache TTL is based on `expires_in` minus LiteLLM's OAuth expiry buffer. If `expires_in` is missing or invalid, LiteLLM uses the default OAuth token cache TTL."
- **Our assessment**: The cache key is a security-relevant isolation boundary:
  keying on the subject token rather than `user_id` means a caller cannot reuse
  another user's exchanged token, and a rotated subject token correctly forces a
  new exchange. It also answers the common cost/latency objection — short-lived
  user tokens do not imply an IdP round trip per request, provided the IdP
  actually returns `expires_in`.

### Claim 10: A request to an `oauth2_token_exchange` server with no user bearer is rejected with `401` and a `WWW-Authenticate` challenge, with no `client_credentials` fallback and no forwarding without an exchanged token
- **Evidence**: The "Requests Without a Subject Token" section gives the exact
  status, challenge header, and error description, then states the two negative
  guarantees.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "There is no fallback to OAuth `client_credentials` and the request is never forwarded to the MCP server without an exchanged token."
- **Quote**: "Missing or invalid subject token; authenticate with the IdP and retry"
- **Our assessment**: This is the fail-closed guarantee that distinguishes OBO
  from a convenience wrapper. Operationally, the 401 is the expected
  discriminator: if an MCP client calls without a user bearer, this is correct
  behavior, and the `resource_metadata` URL tells the client where to
  authenticate. It should be in the runbook as "expected until the caller sends a
  user token," not as an outage symptom.

### Claim 11: OBO and M2M cannot share one server entry — machine access needs a second entry with `auth_type: oauth2` and an explicit `oauth2_flow: client_credentials`, which the proxy requires at startup
- **Evidence**: The final paragraph of "Requests Without a Subject Token" states
  the separate-entry requirement and the startup refusal.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "If you also need machine-to-machine access to the same MCP server, register a separate server entry with `auth_type: oauth2` and `client_id`, `client_secret`, and `token_url` configured. Set `oauth2_flow: client_credentials` on that entry; the proxy refuses to start an `oauth2` server without an explicit `oauth2_flow`."
- **Our assessment**: This is the same "declare, don't infer" property recorded
  in the MCP OAuth overview, applied to the OBO/M2M boundary: the two credential
  models are distinct `auth_type` entries, not one entry that picks a mode by
  request. An operator who expects a single server entry to serve both humans
  and service accounts will get a fail-closed 401 on the machine path. The
  startup refusal for a missing `oauth2_flow` is a second fail-fast check worth
  citing.

### Claim 12: The troubleshooting table maps four symptoms to specific causes — LiteLLM key in `Authorization`, a 400 from the exchange endpoint, a missing upstream `Authorization`, and an exchange per request
- **Evidence**: The "Troubleshooting" table's four rows, each naming a symptom
  and a check.
- **Confidence**: emerging (documented vendor troubleshooting surface)
- **Quote**: "Move the LiteLLM key to `x-litellm-api-key` and use `Authorization` for the user token."
- **Quote**: "Confirm `audience`, `scopes`, `client_id`, and `subject_token_type` match your identity provider configuration."
- **Quote**: "Confirm the identity provider returns `expires_in`, and that the same user token and MCP server are being reused."
- **Our assessment**: The table is the on-call layer: it converts the page's
  guarantees into four checks, and each aligns with a claim above (header split,
  dialect/config mismatch, missing subject token, cache behavior). The 400 row is
  the one that catches the Entra/profile mismatch in practice, because the
  exchange endpoint rejects a malformed or policy-disallowed grant before LiteLLM
  can surface a more specific error.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(https://docs.litellm.ai/docs/mcp_obo_auth).

### Default RFC 8693 OBO config (from "Configure an MCP Server for OBO")

```yaml
mcp_servers:
  internal_tools:
    url: "https://mcp.example.com/mcp"
    transport: "http"
    auth_type: oauth2_token_exchange
    # OAuth 2.0 Token Exchange endpoint on your identity provider
    token_exchange_endpoint: "https://idp.example.com/oauth2/token"
    # Token exchange client registered with your identity provider
    client_id: "<idp-client-id>"
    client_secret: "<idp-client-secret>"
    # Optional but recommended: restrict the exchanged token to this MCP server
    audience: "api://internal-tools-mcp"
    scopes:
      - "mcp.tools.read"
      - "mcp.tools.execute"
    # Optional. Defaults to access_token.
    subject_token_type: "urn:ietf:params:oauth:token-type:access_token"
```

### Two-credential upstream config (from "Sending the exchanged token on a different header")

```yaml
mcp_servers:
  my_mcp_server:
    url: "https://gateway.example.com/mcp"
    auth_type: oauth2_token_exchange
    token_exchange_endpoint: "https://idp.example.com/token"
    client_id: os.environ/MCP_CLIENT_ID
    client_secret: os.environ/MCP_CLIENT_SECRET
    audience: "api://esb"
    upstream_token_header: "esb-oauth"
    static_headers:
      Authorization: "Bearer os.environ/UPSTREAM_MCP_TOKEN"
```

Resulting upstream headers (from the same section):

```
esb-oauth: Bearer <token exchanged for this user>
Authorization: Bearer <the shared token you configured>
```

### RFC 8693 token exchange request (from "Token Exchange Request")

```
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded
grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&subject_token=<caller-bearer-token>
&subject_token_type=urn:ietf:params:oauth:token-type:access_token
&client_id=<idp-client-id>
&client_secret=<idp-client-secret>
&audience=api://internal-tools-mcp
&scope=mcp.tools.read mcp.tools.execute
```

Expected IdP response (from the same section):

```json
{
  "access_token": "scoped-token-for-mcp-server",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Entra OBO config (from "Microsoft Entra ID (Azure AD)")

```yaml
mcp_servers:
  internal_tools:
    url: "https://mcp.example.com/mcp"
    transport: "http"
    auth_type: oauth2_token_exchange
    token_exchange_profile: entra_obo
    # Your Entra tenant's v2.0 token endpoint
    token_exchange_endpoint: "https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token"
    # App registration LiteLLM uses to call the token endpoint. The caller's
    # token must have been issued with this client_id as its `aud`.
    client_id: "<entra-app-client-id>"
    client_secret: "<entra-app-client-secret>"
    # Entra has no audience parameter, so the target resource goes in scope
    # as <app-id-uri>/.default
    scopes:
      - "api://internal-tools-mcp/.default"
```

### Entra jwt-bearer exchange request (from "Microsoft Entra ID (Azure AD)")

```
POST /<tenant-id>/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded
grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
&assertion=<caller-bearer-token>
&scope=api://internal-tools-mcp/.default
&requested_token_use=on_behalf_of
&client_id=<entra-app-client-id>
&client_secret=<entra-app-client-secret>
```

### Direct MCP OBO call (from "Calling an OBO MCP Server")

```bash
curl -X POST "https://litellm.example.com/internal_tools/mcp" \
  -H "Content-Type: application/json" \
  -H "x-litellm-api-key: Bearer <litellm-api-key>" \
  -H "Authorization: Bearer <user-token>" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Responses API MCP tool headers (from "Calling an OBO MCP Server")

```json
{
  "model": "gpt-6.1-sol",
  "input": "List the available internal tools",
  "tools": [
    {
      "type": "mcp",
      "server_label": "internal_tools",
      "server_url": "https://litellm.example.com/internal_tools/mcp",
      "require_approval": "never",
      "headers": {
        "x-litellm-api-key": "Bearer <litellm-api-key>",
        "Authorization": "Bearer <user-token>"
      }
    }
  ]
}
```

### Missing-subject-token challenge (from "Requests Without a Subject Token")

```
401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="/.well-known/oauth-protected-resource/mcp/<server_name>", error="invalid_token", error_description="Missing or invalid subject token; authenticate with the IdP and retry"
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch input-file
  rate limiting and enqueued-token accounting; no OAuth or token-exchange content.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**:
  provider-native web-search support matrix; no auth surface.
- `source-notes/docs-litellm-mcp-deployment.md` — **dismissed**: MCP gateway
  topology and public-internet exposure options; orthogonal to per-request OBO
  token exchange.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: Evaluations API
  CRUD/grader contract; no MCP or credential content.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` request-field passthrough; unrelated to token exchange.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock-native
  `/invoke` route where a LiteLLM virtual key rides in an AWS-shaped auth slot;
  a client→gateway auth substitution, not an inbound-token exchange at an IdP.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: Enterprise license
  tiers/features; no OBO mechanics.
- `source-notes/docs-litellm-mcp-aws-sigv4.md` — **cited**: the sibling MCP
  outbound-auth mode (`auth_type: aws_sigv4`, Claim 1). Same `auth_type` slot,
  different answer to "who holds the upstream credential"; this page supplies the
  OBO member's mechanics.
- `source-notes/docs-litellm-mcp-oauth.md` — **cited** (Extends; see below).
- `source-notes/docs-litellm-mcp-oauth-passthrough.md` — **cited**
  (Corroborates; see below).

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-oauth-passthrough.md` **Claim 4** — its
    mode-selection rule says, in its own words, "The practical test: if you would
    have to ask your IdP to widen a token's audience so the upstream accepts it,
    stop and use token exchange." This page supplies the mechanics behind that
    recommendation: the caller token is exchanged at the IdP for an
    MCP-server-scoped token (Claim 1), with `audience` sent on the RFC 8693 path
    (Claim 3) and the target resource expressed as `<app-id-uri>/.default` under
    Entra (Claim 4). The two notes agree: token exchange is the alternative to
    widening `aud`, not a passthrough variant.
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 3** — the
    "declare, don't infer" design fix. This page's `token_exchange_profile`
    switch (Claim 4) and the separate `auth_type: oauth2` + explicit
    `oauth2_flow` M2M entry (Claim 11) are the same declared-mode pattern extended
    to the wire dialect and to the human/machine split; the proxy refusing to
    start without `oauth2_flow` matches the July note's fail-closed
    exhaustive-match property.
  - `source-notes/blog-litellm-may-townhall-updates.md` **Claim 6** — the May
    townhall announced on-behalf-of MCP OAuth with tokens vaulted at the proxy
    and transparent refresh. This page is the shipped config-level detail for
    that announcement. One nuance: the May post says the client "never sees a
    401"; this page documents a `401` when the inbound request carries no user
    bearer (Claim 10). That is a different condition — the May statement is
    about the upstream exchange/refresh path, while this 401 is a missing-subject-
    token admission error — so the two are mode/condition-scoped, not in
    conflict.
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 2** — that
    note establishes `oauth2_token_exchange` as one member of the nine-value
    `auth_type` enum and labels it "RFC 8693 On-Behalf-Of (OBO) — exchange the
    caller's bearer token for a scoped MCP token." This page confirms that
    taxonomy entry and adds the field-level config, the Entra dialect, the cache
    key, and the fail-closed path. It also shows the reference's one-line
    "RFC 8693" label is incomplete for Entra deployments (Claim 4).

- **Contradicts**: No contradiction issue filed. The apparent tensions are
  conditioning variables, not claim-level opposition: (a) the May townhall's
  "client never sees a 401" versus this page's missing-subject-token 401
  (different condition, above); (b) the MCP OAuth overview's interactive PKCE
  flow returning tokens to the client versus this page's exchanged-token flow —
  different `auth_type`s. `CONTRADICTIONS.md` has no entry and no open
  `contradiction`-labeled issue covers OBO auth.

- **Extends**:
  - `source-notes/docs-litellm-mcp-oauth.md` — its Source Context explicitly
    scopes OBO to its own page, and its Claim 1 names `oauth2_token_exchange`
    only at the taxonomy level, while Claim 13 covers `upstream_token_header`
    for M2M. This page is the deferred OBO deep-dive: the RFC 8693 request shape,
    the Entra profile, inbound header split, per-user exchange cache, and
    no-subject-token fail-closed path. The `upstream_token_header` claim here
    (Claim 7) is the OBO-specific two-credential form; it agrees with the
    overview's Claim 13 rather than restating it.
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 2** — see
    Corroborates; the field-level surface is the extension.
  - `source-notes/docs-litellm-mcp-aws-sigv4.md` **Claim 1** — the sibling
    `auth_type` mode. `aws_sigv4` signs each upstream request with the gateway's
    own AWS credential chain, while `oauth2_token_exchange` mints a per-user
    scoped token at the IdP. Same config slot, opposite credential-ownership
    answer; useful as a contrast pair for Ch06.

- **Novel**: Entirely new to the corpus (grep-verified before writing): the
  full `oauth2_token_exchange` config surface and required/optional split; the
  concrete RFC 8693 form-encoded request shape; the Microsoft Entra `entra_obo`
  RFC 7523 `jwt-bearer` dialect (the corpus had no Entra/Azure AD, RFC 7523, or
  `requested_token_use=on_behalf_of` coverage); the `<app-id-uri>/.default`
  scope convention and the silent non-use of `audience`/`subject_token_type`;
  the Entra inbound-token `aud` constraint; the `x-litellm-api-key` +
  `Authorization` inbound split for OBO (including Responses API tool headers);
  the cross-origin redirect header drop for OBO; the `(subject token, MCP server
  ID)` exchange-cache key and TTL; the missing-subject-token 401 challenge with
  no `client_credentials` fallback; and the separate M2M entry requirement.

## Guide Impact

- **Chapter 06 (Security and Trust)** — "Gateway credential routing: declare,
  don't infer": Add `oauth2_token_exchange` as the third credential-ownership
  pattern alongside passthrough (caller-held) and `aws_sigv4`
  (gateway-held/static): OBO is gateway-minted, per-user, MCP-scoped (Claim 1),
  with the raw inbound token never forwarded. Make the Entra dialect split
  explicit — `token_exchange_profile: entra_obo` is RFC 7523 `jwt-bearer`, not
  RFC 8693, `audience`/`subject_token_type` are silently unused, and the target
  resource moves into `scope` as `<app-id-uri>/.default` (Claim 4) — because a
  copy-pasted RFC 8693 config against Entra is a plausible production mistake.
  Add the inbound-token `aud` constraint (Claim 5) and the fail-closed
  missing-subject-token behavior (Claim 10) as positive security properties:
  OBO never downgrades to `client_credentials` and never forwards an unexchanged
  request.

- **Chapter 05 (LLM Ops Reliability)** — MCP gateway auth configuration: Add the
  required-vs-optional `oauth2_token_exchange` field split, including the
  recommendation to set `audience` even though the schema marks it optional
  (Claim 2). Document the exchange cache as `(subject token, MCP server ID)`
  keyed, TTL = `expires_in` minus buffer, so operators neither assume a
  per-request IdP round trip nor assume cross-user reuse (Claim 9). Add the
  separate M2M entry requirement and `oauth2_flow` startup fail-fast (Claim 11),
  and the two-credential `upstream_token_header` + `static_headers` pattern for
  gateway-behind-gateway deployments (Claim 7).

- **Chapter 03 (Runbooks and Agents)** — MCP auth incident triage: Add the OBO
  runbook entries: (a) a 401 with `error="invalid_token"` and
  `error_description="Missing or invalid subject token..."` is expected until
  the caller sends a user bearer, not an outage (Claim 10); (b) check that the
  LiteLLM key is in `x-litellm-api-key` and the user token in `Authorization`
  (Claim 6); (c) a 400 from the exchange endpoint means `audience`, `scopes`,
  `client_id`, or `subject_token_type` do not match the IdP, and under
  `entra_obo` `audience` is ignored entirely (Claims 4, 12); (d) an IdP call on
  every request points at a missing/invalid `expires_in` or a changing subject
  token (Claim 9); (e) a cross-origin upstream redirect drops the custom token
  header on the second hop (Claim 8).

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/mcp_obo_auth`, HTTP 200, no paywall), a living
  Docusaurus page. All `Quote` fields are contiguous verbatim strings from the
  fetched page; no quote was spliced across non-adjacent sentences. The one
  challenge-header quote is a single contiguous fragment from the
  `WWW-Authenticate` value. Markdown formatting and table pipes were avoided
  inside quotes.
- Sibling pages linked from this one (MCP OAuth overview, MCP OAuth Passthrough,
  MCP ID-JAG, MCP per-user credentials, Gateway Auth Reference) were not
  re-fetched for this note; their relevant claims were verified in the existing
  source notes cited above, per MINER §4b.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Additional cross-references
  (`docs-litellm-gateway-auth-reference.md` Claim 2,
  `blog-litellm-may-townhall-updates.md` Claim 6,
  `blog-litellm-july-stability-update.md` Claim 3) came from the Prospector
  triage and `source-notes/` search. Claim numbers and quoted fragments in the
  cited notes were re-read and confirmed before writing (MINER §4b); no claim
  numbers were invented.
- **Contradiction decision (no issue filed).** The May-townhall statement
  ("The client never sees a 401") and this page's missing-subject-token 401 are
  about different conditions — transparent upstream refresh versus an inbound
  request with no user bearer — and the page itself frames the latter as
  expected admission behavior. Per MINER §4a's "conditioning variable" exception,
  no contradiction issue was filed.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes:
  first-party capability documentation with concrete field/wire/cache detail but
  no measured reliability, incident evidence, or independent verification. The
  page accurately states the documented guarantees; the grade is about
  vendor-doc provenance, not doubt that the page says what it says.
- `date_published` is unknown (living vendor docs); `date_extracted` and
  `last_checked` are both 2026-11-02 (UTC).
