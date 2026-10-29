---
source_url: https://docs.litellm.ai/docs/mcp_oauth_passthrough
source_type: docs
title: "MCP OAuth Passthrough — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-10-29
last_checked: 2026-10-29
status: current
confidence_overall: emerging
issue: "#1933"
---

# MCP OAuth Passthrough (LiteLLM Docs)

> LiteLLM defines two declared MCP auth modes that forward a caller's upstream
> OAuth bearer instead of minting one — `true_passthrough` (no gateway
> admission, no spend/rate-limit/audit) and `oauth_delegate` (gateway admission
> plus a separate forwarded bearer) — with a leak-defense rule that never
> forwards the admission credential, a confused-deputy-safe audience rule
> (relay the upstream's own 401; use token exchange instead of widening `aud`),
> and a fail-closed transparent path that fires only when every target in scope
> is `true_passthrough`.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP OAuth
  Passthrough" page under MCP Gateway → Authentication).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the exposed surface (mode names, header rules, config fields,
  fail-closed conditions, migration notes), but documents capability, not
  measured reliability. No production metrics, incident writeups, or independent
  verification on the page. Claims stay at "the gateway documents this surface."
- **Scope**: Covers client-forwarded OAuth for MCP servers whose own issuer
  authenticates the client: the `true_passthrough` / `oauth_delegate` split, the
  audience/token-exchange decision table, `true_passthrough` fail-closed
  conditions, multi-server aggregate header bindings and `Authorization`
  withholding, the admin-UI browser-only tool preview, intentional limits
  (no per-server re-auth signal on the aggregate, DPoP/mTLS, revocation), the
  orthogonal `dcr_bridge` flag, and the deprecated `delegate_auth_to_upstream`
  flag. Does not deep-dive gateway-issued OAuth (see
  `docs-litellm-mcp-oauth.md`), the MCP permission model (see
  `docs-litellm-mcp-control.md`), or AWS SigV4 (see
  `docs-litellm-mcp-aws-sigv4.md`).

## Extracted Claims

### Claim 1: Two `auth_type` values differ on exactly one axis — whether LiteLLM still authenticates the caller at its own edge
- **Evidence**: The opening mode table and the sentence that introduces it. The
  table contrasts `true_passthrough` ("LiteLLM admission: None; anonymous at the
  LiteLLM layer") with `oauth_delegate` ("Required (LiteLLM key / SSO / JWT)"),
  and contrasts "Not recorded" versus "Recorded, keyed on the admission
  identity" for spend/rate limits/audit.
- **Confidence**: emerging (documented vendor surface; no measured behavior)
- **Quote**: "Two `auth_type` values cover this. They differ in one thing: whether LiteLLM still authenticates the caller at its own edge."
- **Our assessment**: This is the cleanest statement in the corpus that a
  declared, typed auth mode can still be *deliberately unauthenticated at the
  gateway*. It does not weaken the "declare, don't infer" rule — both are
  declared modes — but it creates a boundary case: fail-closed here means
  "resolve the mode, then apply that mode's admission posture," not "every mode
  must authenticate." Guide wording that equates declared auth with gateway
  admission would misstate this page.

### Claim 2: Both modes forward the token verbatim — no decoding, no audience or scope check, no exchange
- **Evidence**: The paragraph after the mode table, plus the discovery sentence
  preceding it ("Both modes return the upstream's protected-resource metadata
  verbatim during discovery").
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "Both forward the token exactly as the caller sent it. LiteLLM does not decode it, does not check its audience or scopes, and does not exchange it; the upstream MCP server is the only party that validates it."
- **Our assessment**: This is the core contract and the source of every
  intentional limit later on the page (audience, DPoP/mTLS, revocation). The
  gateway becomes a relay, not a token authority. Operators who expect the
  gateway to normalize scopes or re-mint for the upstream will be surprised by an
  upstream 401 that LiteLLM cannot explain or fix.

### Claim 3: An audience-locked token rejected by the upstream is the correct confused-deputy-safe outcome, not a LiteLLM bug
- **Evidence**: The "Audience-locked tokens" section explains that an OAuth
  access token carries an `aud`, that a well-behaved upstream rejects a token
  minted for another resource, and that the rejection is relayed as the
  upstream's own 401.
- **Confidence**: emerging (documented vendor behavior and stated security
  position)
- **Quote**: "This is the correct confused-deputy-safe outcome: the gateway did not launder a token minted for one resource into access to another, and it is not a LiteLLM bug to file."
- **Our assessment**: A strong, quotable anti-pattern rule: do not "fix" an
  upstream audience rejection by disabling audience checks or widening the token.
  The refusal is the security property. The phrasing also gives an on-call
  runbook discriminator — an upstream 401 on a passthrough route is expected
  behavior until proven otherwise.

### Claim 4: Mode selection is keyed on who minted the token, with an explicit test that forbids widening `aud`
- **Evidence**: The decision table in "Audience-locked tokens" (token minted for
  the upstream → passthrough/delegate; minted for another resource and IdP
  supports RFC 8693 or Entra OBO → `oauth2_token_exchange`; identity-only
  credential → neither mode) and the practical-test paragraph.
- **Confidence**: emerging (documented vendor rule)
- **Quote**: "The practical test: if you would have to ask your IdP to widen a token's audience so the upstream accepts it, stop and use token exchange."
- **Our assessment**: This is the most transferable decision rule on the page.
  It converts an ambiguous IAM negotiation ("can we just add the MCP server to
  the token's audience?") into a hard stop. It also explains when the
  passthrough modes are the *wrong* answer, which a note focused only on their
  mechanics would miss.

### Claim 5: `true_passthrough` is the entire configuration — `url` plus `auth_type`, with no client credentials or token endpoints
- **Evidence**: The `true_passthrough` Setup section and its single config
  snippet.
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "That is the entire configuration. No client credentials or token endpoints, because LiteLLM never participates in the token exchange."
- **Our assessment**: The setup's minimalism is the operational signal: if a
  `true_passthrough` block contains `client_id`, `client_secret`, or token
  endpoints, the operator has likely copied a gateway-issued OAuth config by
  mistake. This is a cheap config-lint check for a runbook.

### Claim 6: `true_passthrough` makes the MCP route unauthenticated ingress and disables spend, per-key rate limits, and `user_id`-keyed guardrails
- **Evidence**: The "Security Trade-offs" bullet list under `true_passthrough`;
  the page separately notes that `available_on_public_internet: false` does not
  add authentication.
- **Confidence**: emerging (documented vendor consequences)
- **Quote**: "The MCP route becomes an unauthenticated ingress at the LiteLLM layer."
- **Quote**: "Spend tracking, per-key rate limits, and any guardrail depending on `user_api_key_auth.user_id` do not run."
- **Quote**: "`available_on_public_internet: false` adds no authentication here; it mainly controls IP-based discovery"
- **Our assessment**: This is the "what does the operator lose" answer the
  Prospector asked for. The `available_on_public_internet: false` caveat is the
  easiest misread on the page: a private-network flag is not an auth control.
  Pair it with Claim 12 (audit must come from the upstream) and Claim 13 (no
  per-server re-auth signal) for the full observability loss.

### Claim 7: The transparent path fails closed on resolution — it fires only when every target in scope is `true_passthrough`
- **Evidence**: The "Fail-Closed Behavior" list under `true_passthrough`.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "The transparent path fires only when every target resolves to `true_passthrough`. It falls back to normal LiteLLM admission when:"
- **Our assessment**: The single most operationally important sentence on the
  page. It also tempers the earlier "unauthenticated ingress" claim: mixed
  fleets, multi-server aggregates with any non-passthrough member, and
  unresolvable targets all revert to normal admission. The fail-closed axis is
  the *resolution of the mode*, not the presence of a credential. A runbook
  should state both halves together, or it will overstate the exposure.

### Claim 8: `oauth_delegate` keeps admission in `x-litellm-api-key` and forwards only the separate upstream bearer
- **Evidence**: The `oauth_delegate` "How It Works" steps and Security
  Trade-offs. The upstream bearer rides in `Authorization`, or in
  `x-mcp-<alias>-authorization` for aggregate requests.
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "The caller admits with a LiteLLM credential in `x-litellm-api-key`."
- **Quote**: "LiteLLM validates admission, then forwards only the upstream bearer, never the admission credential."
- **Our assessment**: This is the mode that preserves the gateway's
  observation position: spend, rate limits, audit, and per-key/team tool
  permissions all resolve against the admission identity while the upstream
  still owns tool-level authorization. It is the recommended pattern when the
  operator wants both gateway gating and upstream-owned tokens.

### Claim 9: A lone `Authorization` credential is treated as the admission credential and never forwarded upstream — the leak defense
- **Evidence**: The "Keep the two credentials in separate headers" callout
  inside the `oauth_delegate` section.
- **Confidence**: emerging (documented vendor rule)
- **Quote**: "If a caller sends a single credential in `Authorization` with no `x-litellm-api-key`, LiteLLM treats it as the admission credential (virtual key, IdP JWT, or SSO session token) and never forwards it upstream. That is the leak defense keeping a LiteLLM or IdP token from reaching a third-party MCP server."
- **Our assessment**: The highest-value security rule on the page. It defines
  two trust domains and a deterministic header assignment, so a LiteLLM virtual
  key or IdP JWT cannot be replayed to a third-party MCP server by accident. The
  cost is a client-shape requirement: callers must send two headers, and a
  single-header client will silently lose the upstream token rather than leak
  the admission one — the right failure direction.

### Claim 10: Aggregate requests can carry only one `Authorization`, so per-server headers bind a token to one server and request-wide `Authorization` is withheld during listing fan-out
- **Evidence**: The "Multi-server aggregate requests" section: the RFC 9700
  cross-resource replay rationale, the per-server header rule, the withholding
  rule for `tools/list` and prompt/resource listings, and the explicit
  consequence for tool visibility.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "If two of those upstreams both forward the caller's token, sending that one header to both would replay a single bearer across unrelated resources (the cross-resource replay RFC 9700 warns about)."
- **Quote**: "The request-wide `Authorization` is withheld from a client-forwarded server during a listing fan-out (`tools/list`, and the prompt and resource listings) whenever another server in the same scope would also consume it."
- **Quote**: "In practice this is why a single bearer that is valid for several upstreams can execute tools through the aggregate endpoint yet not appear in the aggregate `tools/list`: the tool call names one server, the listing does not."
- **Our assessment**: A concrete, testable failure mode: tools execute but do
  not list. It will read as a tool-discovery bug to anyone who has not internalized
  the withholding rule. The documented fix — send the token per server — is
  also a config-review item for aggregate `/mcp` deployments.

### Claim 11: Per-server passthrough headers normalize the alias (`[a-z0-9_]`) and forward the value verbatim, scheme included
- **Evidence**: The alias-normalization paragraph in "Multi-server aggregate
  requests" and the worked `Jira Cloud` example.
- **Confidence**: emerging (documented parse rule)
- **Quote**: "The alias is lowercased and any character outside `a-z0-9_` becomes `_`, so a server aliased `Jira Cloud` is addressed as `x-mcp-jira_cloud-authorization`. The value is forwarded verbatim, so include the scheme (`Bearer <token>`)."
- **Our assessment**: A copy-paste hazard: an operator who writes
  `x-mcp-Jira Cloud-authorization` or omits `Bearer ` gets a silently ignored
  header. This complements the gateway auth reference's parse rule (alias then
  `server_name`, case-insensitive) with the exact normalization algorithm.

### Claim 12: The admin-UI "Authorize & Fetch Tools" flow keeps the token in the browser session only
- **Evidence**: The "Previewing tools in the Admin UI" section.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "It runs the upstream OAuth flow in the admin's browser and keeps the resulting token in that browser session only, forwarding it per server for the tool preview and for configuring `allowed_tools`. The token is not written to the server row, to the per-user credential store, or to any cache; closing the tab discards it."
- **Our assessment**: A good example of scoping a privileged token to the
  shortest useful lifetime. The page also distinguishes optional OAuth Client
  ID/Secret (saved as declared server config for IdPs without DCR) from the
  browser-only token — a distinction an operator could easily blur.

### Claim 13: Three forwarding limits are intentional — no per-server re-auth signal on the aggregate, no DPoP/mTLS relay, no connect-time revocation detection
- **Evidence**: The "Intentional limits" section, which frames them as
  consequences of forwarding verbatim rather than defects.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "A single-server route relays the upstream's `401` and `WWW-Authenticate` truthfully, but the aggregate absorbs one server's auth failure into an empty listing for that server so the remaining servers still list."
- **Quote**: "Sender-constrained tokens (DPoP, RFC 9449, or mTLS-bound tokens, RFC 8705) cannot be relayed."
- **Quote**: "Revoked tokens are not detected at connect time. LiteLLM keeps no state about a forwarded token and does not introspect it, so a token revoked at the issuer is forwarded and rejected by the upstream on the request that uses it."
- **Our assessment**: These are the runbook caveats. The aggregate's absorption
  of a 401 into an empty listing is the same "deny but hide" pattern seen on the
  MCP permission side, and it makes the single-server route the diagnostic path.
  DPoP/mTLS rejection is architectural, not a bug to escalate; revocation
  detection belongs to the upstream.

### Claim 14: `dcr_bridge` is valid only on the two passthrough modes, and the `oauth_delegate` bridge requires a working browser sign-in
- **Evidence**: The "Gateway-hosted sign-in (DCR bridge)" section: validity
  rule, the two prerequisites, and the note that a missing gateway sign-in is
  the usual stall cause.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "Valid only on `true_passthrough` and `oauth_delegate`; rejected on any other `auth_type` at create, update, and config load."
- **Quote**: "The gateway needs a working browser sign-in (SSO or username/password). Without one there is no identity to bind and the authorize step cannot proceed. A missing gateway sign-in is the usual reason an `oauth_delegate` bridge connection stalls at the login page."
- **Our assessment**: The DCR bridge is the compatibility escape hatch for
  OAuth-only clients (OpenCode, Claude Code, Cursor, Claude Desktop) that cannot
  send two credentials. The `oauth_delegate` + bridge path is also
  identity-bearing: it seals a gateway identity plus upstream token into a
  gateway-bound credential, which is how spend/audit resolve for clients that
  cannot present a LiteLLM key inline. The first-run failure mode is concrete
  and testable.

### Claim 15: The legacy `delegate_auth_to_upstream` flag is deprecated and no longer bypasses admission
- **Evidence**: The "Delegate Auth to Upstream (PKCE Passthrough)" deprecation
  callout and its migration guidance.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "It no longer bypasses LiteLLM admission: on current versions LiteLLM still requires its own API key, SSO, or JWT on every request that carries a bearer, and the proxy logs a deprecation warning when a server is loaded with `auth_type: oauth2` and `delegate_auth_to_upstream: true`."
- **Our assessment**: Important upgrade/migration note: an old config that
  relied on the flag to avoid gateway auth now behaves like `oauth_delegate` once
  a bearer is present, and only the credential-free discovery step remains
  anonymous. The documented migration target is `auth_type: oauth_delegate` or
  `true_passthrough`. Anyone auditing "who can reach this MCP server" needs to
  re-check servers that still carry the flag.

## Concrete Artifacts

All artifacts verbatim from the fetched page.

### `true_passthrough` minimal config (from "`true_passthrough` → Setup")

```yaml
mcp_servers:
  notion_passthrough:
    url: "https://mcp.notion.com/mcp"
    auth_type: true_passthrough
```

### `true_passthrough` with the only tool restriction available without caller identity (from "Config Reference")

```yaml
mcp_servers:
  notion_passthrough:
    url: "https://mcp.notion.com/mcp"
    auth_type: true_passthrough
    allowed_tools:
      - search
      - fetch
```

### `oauth_delegate` config (from "`oauth_delegate` → Setup")

```yaml
mcp_servers:
  notion_delegate:
    url: "https://mcp.notion.com/mcp"
    auth_type: oauth_delegate
```

### Aggregate `tools/list` with per-server tokens (from "Multi-server aggregate requests")

```bash
curl -X POST "https://litellm.example.com/mcp" \
  -H "Content-Type: application/json" \
  -H "x-litellm-api-key: Bearer $LITELLM_API_KEY" \
  -H "x-mcp-servers: jira,confluence" \
  -H "x-mcp-jira-authorization: Bearer <token-for-jira>" \
  -H "x-mcp-confluence-authorization: Bearer <token-for-confluence>" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### `dcr_bridge` with `true_passthrough` (from "Gateway-hosted sign-in (DCR bridge)")

```yaml
mcp_servers:
  miro:
    url: "https://mcp.miro.com/"
    transport: http
    auth_type: true_passthrough
    dcr_bridge: true
```

### `dcr_bridge` with `oauth_delegate` (from "Gateway-hosted sign-in (DCR bridge)")

```yaml
mcp_servers:
  miro:
    url: "https://mcp.miro.com/"
    transport: http
    auth_type: oauth_delegate
    dcr_bridge: true
```

### Deprecated `delegate_auth_to_upstream` config (from "Delegate Auth to Upstream (PKCE Passthrough)")

```yaml
mcp_servers:
  notion_mcp:
    url: "https://mcp.notion.com/mcp"
    auth_type: oauth2
    oauth2_flow: authorization_code
    delegate_auth_to_upstream: true
```

### Mode table (from the page header, transcribed row-by-row)

```text
Mode               LiteLLM admission                          Credential forwarded upstream                          Spend / rate limits / audit
true_passthrough   None; anonymous at the LiteLLM layer        The client's Authorization, verbatim                    Not recorded
oauth_delegate     Required (LiteLLM key / SSO / JWT)          A distinct upstream bearer the caller sends alongside  Recorded, keyed on the admission identity
                                                               admission
```

Attribution: "MCP OAuth Passthrough", mode table, https://docs.litellm.ai/docs/mcp_oauth_passthrough.

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch input-file
  rate limiting and enqueued-token accounting; no MCP auth, header-forwarding,
  or OAuth content.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` request-field passthrough; "passthrough" there means request
  body fields, not credential forwarding.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**:
  provider-native web-search support matrix and search-model routing; no auth
  surface.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: Evaluations API
  stored-completion grading; no MCP or credential content.
- `source-notes/docs-litellm-files-endpoints.md` — **dismissed**: provider
  `/files` proxy and file-ID routing; no MCP OAuth.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock-native
  `/invoke` route where a LiteLLM virtual key rides in a Bedrock-shaped auth slot
  instead of SigV4; a client→gateway auth substitution, not a caller-token
  passthrough to an upstream MCP issuer.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: licensing, SSO/SCIM,
  and enterprise feature tiers; no MCP passthrough mechanics.
- `source-notes/docs-litellm-mcp-oauth.md` — **cited** (Extends; see below).
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**: the
  supported-parameter gate and provider param matrix; no relation to MCP auth.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**:
  per-session agent-loop iteration/budget caps keyed on `x-litellm-trace-id`;
  cost controls, not credential forwarding.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 1** — its five-pattern
    taxonomy already names `true_passthrough` and `oauth_delegate`, and its
    Source Context → Scope section states that the passthrough and delegated
    modes are only summarized there and documented in this sibling page. This
    page is the detailed source that summary defers to; the two agree on the
    admission split and on the upstream-bearer forwarding.
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 3** — the
    "declare, don't infer" fix. `true_passthrough` and `oauth_delegate` are
    exactly the requested *declared, typed* modes, matching the July post's
    "Each mode has its own fully typed config, so there is no guessing from
    which fields are set and no precedence order." The nuance this page adds is
    that fail-closed applies to *mode resolution* (Claim 7), not to requiring a
    credential on every mode (Claim 1). Consistent with the July post's Claim 1:
    ambiguity resolves to "stop," while an explicit `true_passthrough` is not
    ambiguous.
- **Extends**:
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 2** — that
    page enumerates the `auth_type` enum and says "Nine values," but the
    enumeration does **not** include `true_passthrough` or `oauth_delegate`.
    This page documents both as first-class `auth_type` values, plus their
    config and admission behavior. The delta matters for the guide: the
    reference page's "nine values" should not be presented as the exhaustive
    enum. See Extraction Notes for why this is recorded as a currency/scope gap
    rather than a filed contradiction.
  - `source-notes/docs-litellm-mcp-control.md` **Claim 7** — the per-entity
    `mcp_tool_permissions` model (intersected across key/team/agent/internal
    user). This page states the boundary directly: under `true_passthrough`
    there is no caller identity, so "there are no per-key or per-team tool
    permissions, so this list is the only tool restriction and it applies to
    every caller identically" (Config Reference → `allowed_tools`). Under
    `oauth_delegate` the permission model applies "on top of whatever the
    upstream enforces." The two notes compose: one documents the ACL model, the
    other documents when its subject (an admission identity) does not exist.
  - `source-notes/docs-litellm-mcp-aws-sigv4.md` **Claim 1** and **Claim 3** —
    the sibling outbound-auth mode. `aws_sigv4` has the gateway sign each
    request using its own boto3 credential chain, while the passthrough modes
    forward the caller's bearer and mint nothing. Same config slot
    (`auth_type`), opposite answer to "who holds the upstream credential" —
    useful as a contrast example in Ch06.
- **Contradicts**: No contradiction issue filed. Reasons in Extraction Notes.
  The only candidate is the `auth_type`-enum completeness gap versus
  `docs-litellm-gateway-auth-reference.md` Claim 2; it is a version/scope
  difference between two living vendor pages, not two opposing claims about how
  the gateway behaves, and the practical remedy is a Guide Impact wording fix.
- **Novel**: `true_passthrough` and `oauth_delegate` as named `auth_type`
  values; the leak-defense rule that a lone `Authorization` credential is
  admission and is never forwarded; the audience/confused-deputy rule and the
  RFC 8693/OBO decision table; the fail-closed transparent-path gate; aggregate
  `Authorization` withholding and `x-mcp-{alias}-authorization` binding
  (including alias normalization); the admin-UI browser-only tool-preview token
  handling; the three intentional limits; `dcr_bridge` prerequisites and
  identity binding; and the `delegate_auth_to_upstream` deprecation/migration
  path.

## Guide Impact

- **Chapter 06 (Security and Trust)** — §"Gateway credential routing: declare,
  don't infer": Add the passthrough boundary case. The existing `[settled]` rule
  ("a declared auth mode per MCP server … Ambiguity must resolve to 'stop'") is
  about *selection*, not admission. As shipped, a declared mode can be
  `true_passthrough`, which is deliberately anonymous at the gateway (Claim 1,
  Claim 6). Word the rule as "declared and fail-closed on resolution — the
  selected mode determines admission posture; it does not imply admission,"
  citing Claim 7 for the resolution gate. Add the leak-defense rule (Claim 9) as
  a concrete two-trust-domain control, and the audience rule (Claim 3/Claim 4):
  an upstream 401 on a passthrough route is the correct confused-deputy-safe
  outcome, not a defect; widening `aud` is the anti-pattern that should push to
  `oauth2_token_exchange`. Also correct the `auth_type` teaching so it does not
  present the nine-value enumeration from
  `docs-litellm-gateway-auth-reference.md` as exhaustive — these two modes are
  additional values.
- **Chapter 05 (LLM Ops Reliability)** — gateway ingress and accounting:
  Document the telemetry loss of `true_passthrough` as a design decision, not a
  defect: spend tracking, per-key rate limits, and any guardrail keyed on
  `user_api_key_auth.user_id` do not run (Claim 6); per-user audit must come from
  upstream logs; `allowed_tools` is the only tool restriction because there is no
  caller identity (Claim 6 + `docs-litellm-mcp-control.md` Claim 7);
  `available_on_public_internet: false` adds no authentication. Contrast with
  `oauth_delegate`, which keeps spend/limits/audit keyed on the admission
  identity (Claim 8). Recommend `oauth_delegate` when the gateway must remain in
  the observation path.
- **Chapter 03 (Runbooks and Agents)** — MCP auth incident triage: Add a
  passthrough runbook with (a) the two-header client shape and the leak-defense
  behavior for a lone `Authorization` (Claim 9); (b) aggregate `tools/list`
  withholding as the explanation for "tools execute but do not list" (Claim 10);
  (c) use the single-server route or per-server header to surface a per-upstream
  401, since the aggregate absorbs it into an empty listing (Claim 13);
  (d) `dcr_bridge` + `oauth_delegate` stalls at the login page when gateway
  browser SSO is missing (Claim 14); (e) audit configs still carrying the
  deprecated `delegate_auth_to_upstream` (Claim 15).
- **Chapter 02 (Observability)** — attribution gaps: Note that under
  `true_passthrough` the gateway cannot attribute a tool call to a user
  (Claim 6), and on the aggregate there is no per-server "needs
  re-authentication" signal (Claim 13). Both are expected gaps to source from
  upstream logs/alerts, not gaps the gateway can close by configuration.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/mcp_oauth_passthrough`, HTTP 200, no paywall),
  including the mode table, both mode sections, the aggregate section, the
  admin-UI section, intentional limits, the DCR-bridge section, and the
  deprecated-flag section. All `Quote` fields are contiguous verbatim fragments
  from the fetched page; no quotes were spliced across non-adjacent sentences.
  Concrete artifacts are character-for-character from the page with attribution
  (the mode table is transcribed row-by-row rather than as raw HTML).
- Linked sibling pages (`docs/mcp_oauth`, `docs/mcp_control`,
  `docs/mcp_aws_sigv4`, `docs/mcp_public_internet`) were not re-fetched for this
  note — their relevant claims were verified in the existing source notes cited
  above, per MINER §4b.
- **Contradiction decision (no issue filed).** The only tension is with
  `docs-litellm-gateway-auth-reference.md` Claim 2 ("Nine values" with an
  enumeration that omits `true_passthrough` / `oauth_delegate`). This page
  documents two more `auth_type` values. That is a currency/completeness gap
  between two living vendor pages (the reference page is dated 2026-09-21; this
  page is current 2026-10-29), not a disagreement about behavior, and the two
  claims do not lead to different operational advice — both say "the outbound
  auth mode is a declared `auth_type` field." Per MINER §4a's "when NOT to
  file" (context/version difference, not claim-level opposition), no
  contradiction issue is filed; the remedy is the Guide Impact note to stop
  presenting the nine-value list as exhaustive. `CONTRADICTIONS.md` is empty and
  no open `contradiction`-labeled issue covers MCP passthrough auth.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Additional cross-references
  (`docs-litellm-gateway-auth-reference.md`, `docs-litellm-mcp-control.md`,
  `docs-litellm-mcp-aws-sigv4.md`, `blog-litellm-july-stability-update.md`)
  came from the Prospector triage and `source-notes/` search. Claim numbers and
  quoted fragments in the cited notes were re-read and confirmed before writing
  (MINER §4b): `docs-litellm-mcp-oauth.md` Claim 1 and Scope,
  `docs-litellm-gateway-auth-reference.md` Claim 2,
  `docs-litellm-mcp-control.md` Claim 7,
  `docs-litellm-mcp-aws-sigv4.md` Claims 1/3,
  `blog-litellm-july-stability-update.md` Claim 3. No claim numbers invented.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes:
  first-party capability documentation with concrete header/config semantics,
  but no measured reliability, incident evidence, or independent verification.
  The page states the security positions explicitly, so the grade reflects "the
  vendor documents this surface," not doubt that the page says what it says.
- `available_on_public_internet: false` is extracted only as the page states it
  (no authentication added; mainly IP-based discovery) and is not generalized to
  other LiteLLM flags.
- `date_published` is unknown (living Docusaurus page); `date_extracted` and
  `last_checked` are both 2026-10-29.
