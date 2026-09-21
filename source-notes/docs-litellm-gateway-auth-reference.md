---
source_url: https://docs.litellm.ai/docs/auth_overview
source_type: docs
title: "Gateway Auth Reference — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-21)
date_extracted: 2026-09-21
last_checked: 2026-09-21
status: current
confidence_overall: emerging
issue: "#1402"
---

# Gateway Auth Reference (LiteLLM Docs)

> LiteLLM's MCP Gateway and A2A Agent Gateway share most authentication
> primitives but diverge in security-relevant ways: MCP ASGI routes bypass the
> standard FastAPI auth dependency (ignoring vendor auth aliases and
> `x-litellm-tags` that their REST siblings honor), MCP declares outbound auth
> via a first-class nine-value `auth_type` enum while A2A has no such field and
> *infers* its mode from which `litellm_params` fields are set, and a zero-trust
> `mcp_jwt_signer` guardrail exists for MCP only.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "Gateway
  Auth Reference", a living side-by-side reference page under "Agent & MCP
  Gateway" in the nav, dedicated to the auth surfaces of the MCP Gateway and
  the A2A Agent Gateway).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* LiteLLM exposes (header names, `auth_type`
  values, parse rules, resolution depth, error codes), but documents
  *capability*, not demonstrated reliability — no measured overhead, no failure
  writeups, no production experience report. Every claim in this note stays at
  "the gateway documents this surface," never "this holds at scale."
- **Scope**: Covers the side-by-side auth surface of the two gateway surfaces:
  inbound caller auth headers, outbound (gateway→backend) auth mode, per-user
  header passthrough, RBAC/access-group resolution depth, trace-ID propagation
  and enforcement, guardrails on the gateway path, and a copy-paste cheatsheet.
  It is a cross-reference page; the dedicated per-surface pages (MCP Overview,
  MCP OAuth/OBO/ID-JAG/AWS SigV4, MCP Zero Trust, A2A Agent Gateway,
  A2A Agent Permissions) are linked but not deep-dived — the collapse/divergence
  table itself is the extraction target. Does not cover the full MCP
  registration or model-path auth (virtual keys, teams, budgets) outside what
  the divergence tables state.

## Extracted Claims

### Claim 1: The MCP ASGI routes (`/mcp`, `/{name}/mcp`, `/toolset/{name}/mcp`, `/sse`) bypass the standard FastAPI auth dependency and do not parse the vendor-specific auth aliases (`API-Key`, `x-api-key`, `x-goog-api-key`, `Ocp-Apim-Subscription-Key`) or `x-litellm-tags` — while the MCP REST/management routes (`/v1/mcp/...`, `/mcp-rest/...`) and all A2A routes accept the full header set
- **Evidence**: The §1 divergence statement plus the inbound-header table, whose
  "MCP ASGI" column marks the vendor aliases and `x-litellm-tags` as not parsed
  (—) while "MCP REST + A2A" marks them accepted (✓).
- **Confidence**: emerging (documented vendor behavior; no security audit or
  measured consequence on the page)
- **Quote**: "the MCP **ASGI** routes (the streamable MCP endpoints at `/mcp`, `/{name}/mcp`, `/toolset/{name}/mcp`, `/sse`) bypass the standard FastAPI auth dependency and do not parse the vendor-specific auth aliases (`API-Key`, `x-api-key`, `x-goog-api-key`, `Ocp-Apim-Subscription-Key`) or `x-litellm-tags`. The MCP **REST/management** routes (`/v1/mcp/...`, `/mcp-rest/...`) and **all** A2A routes accept the full header set."
- **Our assessment**: The highest-value claim on the page for Ch06. An operator
  who configures a vendor auth alias on a key (e.g. an API Gateway/camel-case
  `API-Key` because the calling client is an Azure APIM tier) will find it
  silently ignored on `/mcp` but honored on `/mcp-rest` — the credential form is
  route-dependent without any error. This is the same "auth layer and dispatch
  layer disagree about the same request" family as the Host-header auth bypass
  (`failure-litellm-host-header-auth-bypass.md`), but the mechanism differs:
  there the desync was between auth-evaluated and dispatched *routes*; here it
  is a per-route-family *header-parsing* divergence that is documented as
  current, intentional behavior, not a fixed vulnerability.

### Claim 2: MCP outbound auth is declared per server via a first-class `auth_type` field with nine values — static header modes, `oauth2` (PKCE vs M2M `client_credentials`, discriminated by `oauth2_flow`), `oauth2_token_exchange` (RFC 8693 OBO), `oauth2_id_jag`, and `aws_sigv4` — which determines the outbound `Authorization` header or per-request SigV4 signature
- **Evidence**: The "MCP: `auth_type` enum" section: the intro sentence, the
  "Nine values" statement, the mechanism table, and the sentence tying the enum
  to the outbound header/signature.
- **Confidence**: emerging (documented vendor surface; no measured behavior)
- **Quote**: "The MCP server's outbound `Authorization` header (or per-request SigV4 signature) is determined by `auth_type`." / "Nine values."
- **Our assessment**: This is the *shipping materialization* of the July
  stability post's "declare, don't infer" fix
  (`blog-litellm-july-stability-update.md` Claim 3): MCP auth is now an explicit
  typed enum, with the OBO/ID-JAG/SigV4 variants expanding well beyond the
  OAuth/static header modes the corpus knew. `auth_type`, `oauth2_token_exchange`,
  `oauth2_id_jag`, and `aws_sigv4` appear nowhere else in `source-notes/` —
  entirely new MCP-surface material.

### Claim 3: A2A has no `auth_type` field at all — the outbound auth mode is inferred from which `litellm_params` fields are present: Bearer/JWT when `api_key` is set, SigV4 (AgentCore only) when it is unset, provider-native auth for non-Bedrock providers
- **Evidence**: The "A2A: auth mode inferred from `litellm_params`" section and
  its mode table (When it fires / Send to backend) and the sentence naming the
  Dual JWT-vs-SigV4 mode as AgentCore-specific.
- **Confidence**: emerging (documented vendor behavior — a claim about *documented
  product behavior*, i.e. whether the surfaces differ; the guide poses a scope
  question addressed in Cross-References)
- **Quote**: "**A2A has no `auth_type` field at all**; the outbound auth mode is inferred from what's present in `litellm_params`." / "The dual JWT-vs-SigV4 mode is specific to AgentCore. Other A2A providers (Vertex, LangGraph, Azure Foundry) use the provider's own credential conventions."
- **Our assessment**: The counterpart to Claim 2, and the reliability-relevant
  asymmetry: MCP gets explicit declared mode selection, A2A still selects by
  field *presence* (`api_key` set vs unset) — exactly the "which fields are set"
  pattern the July postmortem condemned for MCP. Note the claim is about
  *A2A's* current documented surface, not about whether this is safe; it is the
  tinder for the Ch06 scope question (see Cross-References and Guide Impact).

### Claim 4: A zero-trust add-on exists for MCP only — the `mcp_jwt_signer` guardrail (`mode: pre_mcp_call`) signs every outbound tool call with a short-lived RS256 JWT and publishes a JWKS endpoint; it composes with any `auth_type` and has no A2A equivalent
- **Evidence**: The "Zero-trust add-on (MCP only)" section and the §6 guardrail
  table's row marking zero-trust JWT signing as "— (not applicable to A2A
  today)".
- **Confidence**: emerging (documented vendor surface; no failure reports)
- **Quote**: "It signs every outbound tool call with a short-lived RS256 JWT and publishes a JWKS endpoint the MCP server can verify against. This is a guardrail (`guardrail: mcp_jwt_signer`, `mode: pre_mcp_call`) rather than an `auth_type`, and it composes with any `auth_type`."
- **Our assessment**: A rare in-corpus example of a gateway→backend zero-trust
  layer: the MCP server can *cryptographically verify* a call came through
  LiteLLM (as opposed to any client that can reach it with a valid token).
  Extracted only for the MCP-only zero-trust angle — the general guardrail
  mechanics are already covered by
  `docs-litellm-generic-guardrail-api.md` (a different, webhook-based guardrail
  framework). `mcp_jwt_signer` appears nowhere else in `source-notes/`.

### Claim 5: Per-user header passthrough conventions look symmetric but parse differently — MCP's `x-mcp-{server_alias}-{header}` is matched against the server's `alias` then `server_name` (case-insensitive), while A2A's `x-a2a-{agent_name_or_id}-{header}` is matched against the agent's UUID and human-readable name (both tried)
- **Evidence**: The §3 table with both surfaces' prefix, format, parse rule,
  match target, and concrete examples (`x-mcp-github-authorization` →
  server `github`, header `Authorization`; `x-a2a-my-agent-x-api-key` →
  agent `my-agent`, header `x-api-key`).
- **Confidence**: emerging (documented parse rules)
- **Quote**: "Both surfaces let clients forward credentials destined for a specific backend server/agent without admin pre-configuration. The conventions look symmetric but parse differently, so be precise when copy-pasting."
- **Quote**: "`x-mcp-github-authorization: Bearer ghp_...` → server `github`, header `Authorization`" / "`x-a2a-my-agent-x-api-key: secret` → agent `my-agent`, header `x-api-key`"
- **Our assessment**: The copy-paste hazard the Prospector flagged: the two
  conventions collide lexically (`x-mcp-github-authorization` vs
  `x-a2a-github-authorization`) but resolve by different identity axes. A2A is
  the looser match (UUID *and* human name both tried) — a human-readable name
  collision could route a user passthrough header to the wrong agent; MCP's
  alias-then-server_name ordering is a documented precedence.

### Claim 6: On passthrough conflicts the admin wins — `static_headers` are always sent and "win over user passthrough on key conflicts", while `extra_headers` is an admin allowlist of client header names forwarded verbatim
- **Evidence**: The §3 "admin-controlled alternatives" table (symmetric across
  both surfaces) with the `static_headers` and `extra_headers` notes.
- **Confidence**: emerging (documented precedence rule)
- **Quote**: "Always sent. **Wins over user passthrough** on key conflicts."
- **Quote**: "Admin-allowlist of client header names to forward verbatim."
- **Our assessment**: A concrete, checkable precedence rule: admin-configured
  backend credentials silently override any client-supplied header of the same
  name. Symmetric with the A2A overview note's "static headers always win"
  (#1302 Claim 9); this page confirms the same rule on the MCP side and states
  the conflict-resolution semantics explicitly.

### Claim 7: Authorization resolution depth is asymmetric — MCP resolves `object_permission` across six levels (Key, Team, End user, Agent, Internal user, Org) while A2A resolves across two (Key, Team), with end-user, internal-user, and org levels "not resolved today" for A2A
- **Evidence**: The §4 level table pairing MCP and A2A fields per level, with the
  A2A column marking End user, Internal user, and Org as "— not resolved today"
  and Agent as "— not applicable (the agent is the target)".
- **Confidence**: emerging (documented vendor scope boundary)
- **Quote**: "Both surfaces use the `object_permission` model with intersection-style resolution, but at different depths today. MCP resolves across six levels; A2A across two."
- **Quote**: "Same (the human the request authenticated as); intersected with the running result, so it can only narrow" / "— not resolved today" (Internal user row — MCP field vs A2A field)
- **Our assessment**: Confirms the depth asymmetry already asserted by
  `docs-litellm-a2a-agent-permissions.md` Claim 7 (MCP extends to
  End-user/Agent/Org; A2A is narrower), and adds a level that note's enumeration
  did not name: MCP also resolves **Internal user** (the authenticated human),
  described as an intersection that "can only narrow" — an explicit
  narrowing-only property worth teaching. Not re-extracted as new per triage;
  cited as corroboration with the internal-user detail as the delta.

### Claim 8: Reject behavior differs by surface — MCP hides denied servers/tools (`list_tools` filters out hidden servers; `call_tool` returns an error), while A2A filters `GET /v1/agents` and returns HTTP 403 from `POST /a2a/{agent_id}`
- **Evidence**: The §4 concern table's "Reject behaviour" row.
- **Confidence**: emerging (documented vendor behavior; the 403 confirms
  #1302 Claim 7's per-agent authorization consequence)
- **Quote**: "`list_tools` filters out hidden servers; `call_tool` returns error" / "`GET /v1/agents` filters; `POST /a2a/{agent_id}` returns HTTP **403**"
- **Our assessment**: The divergence is in the *observability* of rejection too:
  on MCP the denial is a filtered list or a call-time error, on A2A a list
  filter plus an explicit 403 on invoke. Both are "deny, but the visibility of
  what exists differs" — an operator probing a gateway expecting explicit 403s
  learns nothing about hidden MCP servers, which is arguably a feature
  (enumeration resistance) but worth noting for debugging.

### Claim 9: Trace-ID enforcement has two opposite directions with the same HTTP 400 contract — `require_trace_id_on_calls_to_agent` rejects inbound `/a2a/{agent_id}` calls missing the trace id, and `require_trace_id_on_calls_by_agent` requires trace IDs on outbound calls made by a key owned by the agent
- **Evidence**: The §5 "A2A-specific extras" table with both flags, their scope
  (per-agent `litellm_params`), and their behavior.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "Reject inbound `/a2a/{agent_id}` calls missing `x-litellm-trace-id` (or `x-litellm-session-id` fallback) with **HTTP 400**." / "Reverse direction — when a key **owned by** that agent makes outbound calls, require a trace ID on those."
- **Our assessment**: Corroborates the same two-flag surface already extracted in
  `docs-litellm-a2a-iteration-budgets.md` Claim 2 and
  `docs-litellm-a2a-agent-gateway.md` Claim 7, and adds the explicit
  cross-reference framing: the outbound flag is what actually enables the
  per-session budget counters (iteration budgets note), so this page's summary
  row and the budget note's dependency chain are two views of one control
  surface.

### Claim 10: Sub-agent identity is not propagated — on a downstream dispatch LiteLLM forwards `X-LiteLLM-Trace-Id` and `X-LiteLLM-Agent-Id` but "the original virtual key and end-user identity are not auto-forwarded", requiring manual threading via `extra_headers` or the `x-a2a-{agent_name_or_id}-{header}` convention
- **Evidence**: The §5 "Sub-agent identity propagation" paragraph.
- **Confidence**: emerging (documented behavior; already asserted by #1302 Claim 3
  — extracted here as corroboration/consolidation, per triage "extract only what
  the overview page did not assert")
- **Quote**: "The original virtual key and end-user identity are **not** auto-forwarded. Use `extra_headers` or the `x-a2a-{agent_name_or_id}-{header}` convention to thread identity explicitly."
- **Our assessment**: Same manual-threading obligation as the A2A overview note
  (#1302 Claim 3) — this page states it in the auth-reference framing, tying it
  to the passthrough conventions of Claim 5. End-user attribution silently
  degrades across the agent hop unless the client threads it; relevant to
  Ch02/Ch05 spend attribution and per-end-user budgets.

### Claim 11: Gateway-path guardrails differ by surface — MCP has `pre_mcp_call`/`during_mcp_call` modes plus the zero-trust signer, while A2A has no dedicated guardrail modes and relies on standard chat-completion guardrails applied to the agent's underlying LLM calls
- **Evidence**: The §6 concern table (Pre-call input guardrails, During-call
  intervention, Zero-trust JWT signing rows).
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "Standard chat-completion guardrails apply to the underlying LLM calls the agent makes"
- **Quote**: "— (not applicable to A2A today)" (Zero-trust JWT signing, A2A column)
- **Our assessment**: The MCP surface gets request-phase guardrail hooks at the
  gateway path boundary (`pre_mcp_call`, `during_mcp_call`); A2A's guardrails
  are only the model-call guardrails on the agent's own LLM traffic. An operator
  expecting A2A invoke-time guardrail interception like MCP's will not find it —
  a second MCP/A2A "the surfaces parse the same job differently" asymmetry.

### Claim 12: MCP-only headers — `x-mcp-servers` scopes a request to specific MCP servers (comma-separated) and `x-litellm-mcp-debug: true` returns masked diagnostic response headers (`x-mcp-debug-*`); neither has an A2A counterpart
- **Evidence**: The §1 inbound-header table rows for `x-litellm-mcp-debug` and
  `x-mcp-servers` (both marked MCP ASGI ✓, MCP REST + A2A —).
- **Confidence**: emerging (documented vendor surface)
- **Quote**: "Scope a request to specific MCP servers (comma-separated)." / "Returns masked diagnostic response headers (`x-mcp-debug-*`)."
- **Our assessment**: `x-mcp-servers` is the MCP-side request-targeting knob the
  triage flagged: a caller can pin a request to one server in a multi-server
  deployment without auth changes. `x-litellm-mcp-debug` notes it *masks*
  diagnostic values — potentially a head-start for debuging MCP routing without
  leaking credentials in response headers.

## Concrete Artifacts

All artifacts verbatim from the fetched page.

### Gateway surface table (from the page header, verbatim)

```
Surface                              Endpoints
MCP Gateway                          /mcp, /{server}/mcp, /toolset/{name}/mcp, /sse, /v1/mcp/..., /mcp-rest/...
A2A Agent Gateway                    /a2a/{agent_id}, /a2a/{agent_id}/message/send, /v1/agents/...
```

Attribution: "Gateway Auth Reference", surface table, https://docs.litellm.ai/docs/auth_overview.

### MCP `auth_type` enum (from "MCP: `auth_type` enum", verbatim)

```
auth_type                           Mechanism
none                                No auth header added
api_key / bearer_token / basic      Static header, sent verbatim per call
  / authorization / token
oauth2                              PKCE (interactive) or M2M client_credentials. Discriminated by oauth2_flow.
oauth2_token_exchange               RFC 8693 On-Behalf-Of (OBO) — exchange the caller's bearer token for a scoped MCP token
oauth2_id_jag                       Identity Assertion Authorization Grant: two-leg exchange of the user's identity token (inbound or captured at SSO login) for an MCP access token
aws_sigv4                           Per-request SigV4 signature using a dedicated MCP-side credential chain
```

Attribution: "Gateway Auth Reference", §2 → MCP `auth_type` enum table.

### A2A mode-inference table (from "A2A: auth mode inferred from `litellm_params`", verbatim)

```
Mode                            When it fires                                                        Send to backend
Bearer / JWT                    litellm_params.api_key is set                                        Authorization: Bearer <api_key>
SigV4 (AgentCore only)          litellm_params.api_key is unset                                     Per-request SigV4 via the full AWS credential chain
Provider-native                 litellm_params.custom_llm_provider matches a non-Bedrock provider   The provider's normal auth path
                                (Vertex AI Agent Engine, LangGraph, Azure AI Foundry, Pydantic AI)
```

Attribution: "Gateway Auth Reference", §2 → A2A mode table.

### Header cheatsheet (from §7 "Cheatsheet", verbatim)

```
# Always (LiteLLM-side auth and identification)
x-litellm-api-key: Bearer sk-...
# or
Authorization: Bearer sk-...
x-litellm-end-user-id: user-42
x-litellm-trace-id: 8f4a-2b1c-d3e5-...
# MCP — server scoping / per-user passthrough
x-mcp-servers: github,zapier
x-mcp-github-authorization: Bearer ghp_<user-token>     # user passthrough to github_mcp
x-litellm-mcp-debug: true                                # diagnostic response headers
# A2A — per-user passthrough
x-a2a-my-agent-authorization: Bearer <user-token>        # caller's token to my-agent
x-a2a-my-agent-x-api-key: <user-key>                     # additional per-agent header
```

Attribution: "Gateway Auth Reference", §7 cheatsheet.

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited**
  (Corroborates Claim 9's two-direction trace-ID enforcement; see below).
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: per-agent
  spend tracking/chargeback model; no auth-header or auth-mode content, and the
  auth reference page carries no cost-tracking section.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guards, pre-on-caller; no gateway auth surface.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors and debuggability ethos; no gateway auth content.
- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: served
  agent-card field matrix and skill-scoping drop; no auth-header content.
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **dismissed**:
  embedding-based response caching; unrelated to gateway auth.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP for
  coding-agent integration; no LiteLLM gateway auth surface.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  telemetry integration and session-correlation headers; no gateway auth
  surface.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization/measurement; unrelated.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  LLM-level guardrail scanner stacks (PII, prompt-injection, toxicity) — a
  different layer from the LiteLLM gateway-path guardrail *modes* and the
  `mcp_jwt_signer` signing guardrail this page documents; the scanner
  mechanics are unrelated to the MCP/A2A divergence.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/blog-litellm-july-stability-update.md` **Claim 3** (the July
    MCP fix: "Each mode has its own fully typed config, so there is no guessing
    from which fields are set and no precedence order" — the declared-auth
    resolver). This page's `auth_type` enum (Claim 2 here) is the shipped
    surface that fix built: MCP now declares exactly one typed auth mode per
    server. The July post is MCP-scoped, and this page confirms the declared
    mode landed on MCP — the two sources agree; the July fix and this page's
    MCP enum are the same design described at different altitudes.
  - `source-notes/docs-litellm-a2a-agent-permissions.md` **Claim 7** (MCP's
    permission hierarchy "extends to End-user / Agent / Org additionally; agent
    permissions are a narrower model today"). This page's §4 depth table (Claim
    7 here) independently confirms the asymmetry with the same multi-level vs
    two-level shape, and names an additional MCP level the permissions note did
    not enumerate — **Internal user** ("Same (the human the request
    authenticated as); intersected with the running result, so it can only
    narrow"). Cited as corroboration with the internal-user level as the delta,
    not re-extracted as new, per triage.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 3** (sub-agent
    identity is deliberately not auto-forwarded, must be threaded via
    `extra_headers` or `x-a2a-{agent_name_or_id}-{header}`). This page's Claim
    10 is the same obligation restated in the auth-reference framing; verbatim
    paraphrase level is nearly identical, so it is recorded here as a
    consolidation, not a new finding.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` **Claim 2** (the two
    trace-id enforcement flags with their 400 contract, and the dependency that
    the outbound flag enables budget tracking). This page's Claim 9 gives the
    same two flags and directions in table form; the iteration-budget note adds
    the dependency chain (budgets only enforced via the outbound flag), which
    this page does not repeat.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 9** and **Claim 7**
    (`x-litellm-api-key` preferred over `Authorization` when the inbound
    `Authorization` carries a backend-bound token; per-agent authorization → 403).
    This page restates the `x-litellm-api-key` preference and the A2A 403 reject
    path, and adds the MCP side (Claim 1: `x-litellm-api-key` and
    `Authorization` are parsed on MCP ASGI; the vendor aliases are not).
- **Contradicts**: No contradiction issue filed. Full reasoning in Extraction
  Notes. The Prospector's key question — does A2A's inferred auth mode
  contradict the guide's `[settled]` "declare, don't infer" rule — was examined
  against `guide/06-security-and-trust.md` §"Gateway credential routing:
  declare, don't infer": the guide's rule is already scoped to MCP ("a declared
  auth mode per MCP server", prose about "An MCP gateway"), and the rule's cited
  source (`blog-litellm-july-stability-update.md` Claims 1-3) is MCP-scoped
  ("The MCP Gateway previously inferred…"). This page's Claim 3 does not oppose
  either: MCP declares (consistent), A2A infers (a *different surface* the guide
  rule never addressed). No existing source note claims A2A declares its auth.
  This is a per-surface scope boundary the guide should make explicit, not a
  live claim-level opposition — recorded under Guide Impact; `CONTRADICTIONS.md`
  (no entries) and open `contradiction`-labeled issues (#1150, #1307, #1322,
  #1338, #1352) cover none of this material.
- **Extends / thematically adjacent**:
  - `source-notes/failure-litellm-host-header-auth-bypass.md` — same
    "auth layer and dispatch layer disagree about a request" family. That note
    documents a fixed CVE (GHSA-4xpc-pv4p-pm3w) where FastAPI dispatched a
    different route than the auth gate evaluated (route-resolution desync).
    This page documents a *current, intentional* divergence where a route
    family (MCP ASGI) silently accepts a narrower header set than its REST
    siblings and A2A (header-set divergence). Different mechanism, same
    operational class for Ch06/Ch04: audit that every way to reach a surface
    parses every credential form you rely on. Prospector guidance: related
    context, not a contradiction — agreed.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` — the auth reference
    generalizes that overview note's A2A-specific auth claims (Claims 3, 7, 9)
    into a two-surface side-by-side and adds the MCP half, which the overview
    note could not see.
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md` — prior MCP
    security surface in the corpus is input validation (CVE-2026-30623). This
    page's MCP material covers *auth surface* instead (header parsing, outbound
    mode declaration, zero-trust signing) — orthogonal MCP attack/control
    surfaces from the same vendor.
- **Novel**: Entirely new to the corpus (grep-verified per triage): the MCP
  Gateway auth *surface* as a whole — `auth_type` (nine values incl. `oauth2`,
  `oauth2_token_exchange` RFC 8693 OBO, `oauth2_id_jag`, `aws_sigv4`),
  the MCP-ASGI-bypasses-FastAPI-auth-dependency divergence, `mcp_jwt_signer`
  zero-trust guardrail (RS256 + JWKS), the `x-mcp-{server_alias}-{header}`
  passthrough parse rule with alias-then-server_name matching, `x-mcp-servers`
  request scoping, `x-litellm-mcp-debug`, the six-level MCP RBAC depth with the
  Internal-user level, and the explicit side-by-side MCP-vs-A2A asymmetry
  table. The A2A half (inferred auth mode from `litellm_params` presence) is
  also new: no prior note described how the A2A outbound mode is selected.

## Guide Impact

- **Chapter 06 (Security and Trust)** — §"Gateway credential routing: declare,
  don't infer": Add a **per-surface scope qualifier** to the rule. As shipped
  (this page, current as of 2026-09-21), the declared-mode design is MCP-only:
  MCP has the typed `auth_type` enum (Claim 2), while A2A still selects its
  outbound auth mode by field *presence* — `api_key` set → Bearer/JWT, unset →
  SigV4 on AgentCore (Claim 3) — the exact "which fields are set" inference
  pattern the July postmortem condemned
  (`blog-litellm-july-stability-update.md` Claim 1/3). The guide rule already
  says "per MCP server", so this is a title/scope clarification, not a rule
  flip: "divide, don't infer" did not land product-wide. Also add the Ch06
  security-footgun from Claim 1: MCP ASGI routes ignore vendor auth aliases and
  `x-litellm-tags`, so a credential form that authenticates on `/mcp-rest` and
  A2A is silently ignored on `/mcp` — a deployment checklist item ("verify your
  auth header set against every route family you expose") in the same
  auth-layer-vs-dispatch-layer family as
  `failure-litellm-host-header-auth-bypass.md`. And the zero-trust add-on
  (Claim 4): a gateway→backend JWKS-signed outbound call is the MCP-only
  mechanism for proving a request transited LiteLLM; A2A has no equivalent.

- **Chapter 05 (LLM Ops Reliability)** — agent/gateway invariants: Add the
  MCP/A2A per-surface asymmetry as a design-decision watch item: explicit
  declared config (MCP `auth_type`) vs implicit inferred selection (A2A
  `litellm_params` presence) is a config-model divergence with
  upgrade/hardening implications — a declared enum is enumerable and type-
  checkable; an inferred mode is only discoverable by reading what fields are
  set. Note the overhead-hidden failure mode: `x-litellm-tags` (spend-labeling
  and tag-based routing) is not parsed on MCP ASGI, so MCP streamable-route
  spend tagging silently diverges from MCP REST/A2A (Claim 1).

- **Chapter 02 (Observability)** — trace/identity propagation: Consolidate the
  two-direction trace-ID enforcement surface (`require_trace_id_on_calls_to_agent`
  inbound → 400, `require_trace_id_on_calls_by_agent` outbound → 400, Claim 9)
  with `docs-litellm-a2a-iteration-budgets.md` Claim 2's dependency chain — the
  outbound flag is what enables per-session budget tracking. Sub-agent identity
  non-propagation (Claim 10) already lands in Ch02 via
  `docs-litellm-a2a-agent-gateway.md` Claim 3; cite this page as the
  consolidation.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/auth_overview`, HTTP 200, no paywall), a
  ~250-line living Docusaurus page. All `Quote` fields are contiguous verbatim
  strings from the fetched page; no quotes were spliced across non-adjacent
  sentences. Concrete artifacts (surface table, `auth_type` enum, A2A mode
  table, cheatsheet) are character-for-character from the page with attribution.
  Linked sub-pages (MCP Overview, MCP OAuth/OBO/ID-JAG/SigV4, MCP Zero Trust)
  were not deep-dived — this page is a cross-reference surface itself and the
  linked pages are outside the source's own text, per the Prospector's "extract
  the asymmetries, not the header tables" instruction.
- **Contradiction decision (no issue filed).** The Prospector's key question
  (comment 3) — whether A2A's inferred auth mode contradicts the guide's
  `[settled]` "declare, don't infer" rule — was tested against the actual guide
  text and the rule's cited source. `guide/06-security-and-trust.md` §603-632 is
  already MCP-scoped ("An MCP gateway that infers…", Rule: "a declared auth mode
  per MCP server"), and `blog-litellm-july-stability-update.md` Claims 1-3 are
  MCP-scoped ("The MCP Gateway previously inferred…"). This page's A2A claim
  (inferred mode from field presence) does not oppose either: MCP declaring is
  confirmed (consistent), and A2A inference is a *different surface* the rule
  never addressed. No existing source note claims A2A declares its auth mode.
  Per MINER §4a's "when NOT to file" (context/scope differs; not a claim-level
  opposition) no contradiction issue is filed; the correction is a Guide Impact
  scope qualifier, not a contradiction verdict. Verified no pre-existing
  contradiction covers MCP/A2A auth (CONTRADICTIONS.md empty; open
  contradiction issues #1150, #1307, #1322, #1338, #1352 unrelated).
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Primary cross-reference
  verification (MINER §4b) re-read the cited claims in
  `docs-litellm-a2a-agent-permissions.md` (Claim 7),
  `docs-litellm-a2a-agent-gateway.md` (Claims 3, 7, 9),
  `docs-litellm-a2a-iteration-budgets.md` (Claim 2),
  `blog-litellm-july-stability-update.md` (Claims 1-3), and
  `failure-litellm-host-header-auth-bypass.md` before writing them — quotes and
  claim numbers confirmed against the cited notes. No claim numbers invented.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs notes:
  this is vendor capability documentation with concrete header names, enum
  values, and parse rules, but no measured overhead, no failure reports, and no
  production experience. The one `settled`-grade observation (that the two
  surfaces *differ*) is captured inside Claim 3's framing without promoting the
  whole note — per Prospector, "a claim about documented product behavior".
- Binary-data notes: the page's §1 header table and §4/§6 tables are preserved
  as claims with the divergent cells quoted; the full header tables are not
  duplicated (they are vendor reference material) — the asymmetries are.
- `date_published` is unknown (living Docusaurus page); `date_extracted` and
  `last_checked` are both 2026-09-21.