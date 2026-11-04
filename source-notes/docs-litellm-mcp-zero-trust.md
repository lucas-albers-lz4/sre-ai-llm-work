---
source_url: https://docs.litellm.ai/docs/mcp_zero_trust
source_type: docs
title: "MCP Zero Trust Auth (JWT Signer) — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page last_updated 2026-11-03)
date_extracted: 2026-11-04
last_checked: 2026-11-04
status: current
confidence_overall: emerging
issue: "#2015"
---

# MCP Zero Trust Auth (JWT Signer) — LiteLLM Docs

> LiteLLM's `mcp_jwt_signer` guardrail signs every outbound MCP tool call with a short-lived RS256 JWT so the MCP server can cryptographically verify the request traversed LiteLLM, and this page documents the full operational surface: key lifecycle, identity threading, claim gating and mutation order, scope generation, the Bedrock AgentCore dual-token case, and two fail-silent behaviors (OpenAPI-backed servers skip injection; debug headers leak claim metadata).

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, MCP Gateway → Authentication → "MCP Zero Trust Auth (JWT Signer)")
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation. Authoritative for the config surface LiteLLM exposes and its documented defaults, but it is capability documentation, not measured reliability or incident data. Claims stay at "the gateway documents this behavior."
- **Scope**: Covers the outbound call-attestation layer for MCP — `MCPJWTSigner` / `guardrail: mcp_jwt_signer`, key management, OIDC/JWKS discovery, IdP identity threading, required/optional claim gating, claim mutation, scope generation, AgentCore dual-token injection, debug headers, and stated limitations. Does **not** cover inbound/upstream OAuth flows (separate pages), the general guardrail framework, or measured latency/availability.

## Extracted Claims

### Claim 1: MCP servers have no built-in proof that a request traversed LiteLLM; `MCPJWTSigner` closes that gap by signing every outbound tool call with a short-lived RS256 JWT that the server verifies against LiteLLM's public key
- **Evidence**: The page opens with the threat model and the mechanism; requests not routed through LiteLLM have no valid signature and are rejected.
- **Confidence**: emerging
- **Quote**: "MCP servers have no built-in way to verify that a request actually came through LiteLLM. Without this guardrail, any client that can reach your MCP server directly can call tools, bypassing your access controls entirely."
- **Our assessment**: This is the concrete enforcement mechanism behind the "zero trust" name: it turns gateway presence from an assumption into a signature check at the backend. It is attestation of *path*, not authorization of *intent* — the server still needs its own claim/scope policy, which the rest of the page supplies.

### Claim 2: The signer is configured as a `pre_mcp_call` guardrail with `default_on: true`, and its basic defaults are `audience: "mcp"`, `ttl_seconds: 300`, and an `issuer` that defaults to the request base URL
- **Evidence**: The "Basic setup" `config.yaml` example annotates each default inline.
- **Confidence**: emerging
- **Quote**: "issuer: \"https://my-litellm.example.com\"  # defaults to request base URL"
- **Our assessment**: `default_on: true` matters because MCP sub-calls do not inherit a parent request's guardrail selection (established in `docs-litellm-mcp-guardrails.md`). The 300s TTL bounds replay/leak windows but is still long enough that a captured JWT is usable for several minutes.

### Claim 3: The signing keypair is in-memory by default and rotates on every restart unless `MCP_JWT_SIGNING_KEY` is set (env var or `file://` path); FastMCP's `JWTVerifier` copes via JWKS key-ID matching
- **Evidence**: The "Bring your own signing key" callout plus the "Limitations" bullet; the FastMCP example notes automatic JWKS re-fetch.
- **Confidence**: emerging
- **Quote**: "The keypair is **in-memory by default** and rotated on each restart unless `MCP_JWT_SIGNING_KEY` is set. FastMCP's `JWTVerifier` handles key rotation transparently via JWKS key ID matching."
- **Our assessment**: This is the main reliability trap. Key rotation is safe only for verifiers that honor `kid`; a server that pins or caches a public key instead of re-fetching JWKS breaks at each proxy restart. The docs put the burden on the verifier, not on LiteLLM, so an operator must both pin `MCP_JWT_SIGNING_KEY` and confirm the backend verifier uses `kid`.

### Claim 4: LiteLLM publishes OIDC discovery so MCP servers can locate the JWKS without manual configuration — `/.well-known/openid-configuration` advertises `jwks_uri`, and `/.well-known/jwks.json` serves the RSA keys
- **Evidence**: The discovery contract is shown as two GET endpoints with response shapes.
- **Confidence**: emerging
- **Quote**: "LiteLLM publishes OIDC discovery so MCP servers find the key without any manual configuration:"
- **Our assessment**: Standard OIDC discovery is a genuine operational win: verifier config is just the LiteLLM origin plus issuer/audience, and key rotation is handled by re-fetch. The `iss` value still must match what the verifier expects, so the `issuer` config is not cosmetic.

### Claim 5: By default the outbound `sub` is LiteLLM's internal `user_id`; "verify+re-sign" validates the incoming IdP token and rebuilds the outbound JWT from real identity claims via `access_token_discovery_uri`, `verify_issuer`, `verify_audience`, and an ordered `end_user_claim_sources` list
- **Evidence**: The "Thread IdP identity into MCP JWTs" section, including the Microsoft Entra discovery example and the first-non-empty-wins comment.
- **Confidence**: emerging
- **Quote**: "With verify+re-sign, LiteLLM validates the incoming IdP token first, then builds the outbound JWT using the real identity claims from that token."
- **Our assessment**: Without this, the MCP server sees a LiteLLM-internal ID rather than a corporate identity, which defeats per-user authorization at the backend. The ordered fallback (`token:sub` → `token:email` → `litellm:user_id`) is explicit and auditable, but the last fallback silently degrades to an internal ID if the IdP token lacks the earlier claims.

### Claim 6: Opaque incoming tokens are supported by adding an RFC 7662 `token_introspection_endpoint`; LiteLLM POSTs the token there and uses the returned claims
- **Evidence**: The "If the incoming token is opaque" note in the identity section.
- **Confidence**: emerging
- **Quote**: "If the incoming token is **opaque** rather than a JWT (some IdPs issue these), add an introspection endpoint. LiteLLM will POST the token to it (RFC 7662) and use the returned claims:"
- **Our assessment**: Important for IdPs that issue reference tokens. It adds a per-request network dependency on the IdP's introspection endpoint, which is an availability and latency consideration the page does not discuss.

### Claim 7: With no identity configured, the default `sub` chain degrades to a shared literal — `user_id` → API-key hash → `"litellm-proxy"` — and `act.sub` is `team_id` → `org_id` → `"litellm-proxy"`
- **Evidence**: The "JWT claims reference" table rows for `sub` and `act.sub`.
- **Confidence**: emerging
- **Quote**: "Resolved via `end_user_claim_sources` (default: `user_id` → api-key hash → `\"litellm-proxy\"`)"
- **Our assessment**: The final fallback is a single shared subject, so backends that authorize on `sub` would treat all such callers identically. This is the concrete reason to configure identity sources before relying on per-user policy downstream.

### Claim 8: `required_claims` is a fail-closed gate that returns HTTP 403 before the MCP server sees the request, while `optional_claims` forwards claims only when present
- **Evidence**: The "Block callers missing required attributes" section plus the verbatim 403 error body.
- **Confidence**: emerging
- **Quote**: "`required_claims` rejects with `403` if the incoming token is missing any listed claim. `optional_claims` forwards claims that are useful but not mandatory."
- **Our assessment**: This is the positive contrast to the fail-open items elsewhere on the page: enforcement happens at the gateway and the tool never runs. The error body names the missing claim, which is useful operationally but also confirms claim names to the caller.

### Claim 9: Claim mutation runs in a fixed order — `add_claims` → `set_claims` → `remove_claims` — where `set_claims` overrides `add_claims` and `remove_claims` beats both
- **Evidence**: The "Add custom metadata to every JWT" config example and the explicit ordering sentence.
- **Confidence**: emerging
- **Quote**: "Operations run in order: `add_claims` → `set_claims` → `remove_claims`. `set_claims` always wins over `add_claims`; `remove_claims` beats both."
- **Our assessment**: Non-obvious precedence. An operator who puts the same key in both `add_claims` and `set_claims` may expect the add to be skipped but not that `set` silently overrides an incoming token claim. The page also documents `remove_claims: nbf` for validators that reject `nbf`, which is a practical interop fix.

### Claim 10: Scope generation is least-privilege per request by default (`mcp:tools/call` plus `mcp:tools/{name}:call`, or `mcp:tools/list` for listing), and `allowed_scopes` replaces generation entirely
- **Evidence**: The "Control which scopes go into the JWT" section.
- **Confidence**: emerging
- **Quote**: "If your MCP server does its own scope enforcement and needs a specific format, set `allowed_scopes` to replace auto-generation entirely:"
- **Our assessment**: `allowed_scopes` is all-or-nothing: the page's own example includes `mcp:admin`, and "Every JWT carries exactly those scopes regardless of which tool is being called." That is a blast-radius footgun — one broad scope applies to every call, including read-only tools.

### Claim 11: AWS Bedrock AgentCore Gateway needs two JWTs with different audiences and TTLs — a resource token in `Authorization` (`aud=mcp-resource`, 300s) and a channel token in `x-mcp-channel-token` (`aud=bedrock-agentcore-gateway`, 60s) — both signed by the same LiteLLM key
- **Evidence**: The AgentCore section's config (`audience`, `ttl_seconds`, `channel_token_audience`, `channel_token_ttl`) and its two-header list.
- **Confidence**: emerging
- **Quote**: "Bedrock AgentCore Gateway uses two separate JWTs: one to authenticate the transport connection and another to authorize tool calls. They need different `aud` values and TTLs, so a single JWT won't work for both."
- **Our assessment**: Concrete and actionable: a single-JWT configuration cannot satisfy both layers. The shorter channel TTL (60s) is sensible for the transport hop. This is the JWT-signer complement to `docs-litellm-mcp-aws-sigv4.md`, which covers SigV4-authenticated AgentCore connections.

### Claim 12: `debug_headers: true` adds an `x-litellm-mcp-debug` response header echoing `kid`, `sub`, `iss`, `exp`, and `scope`, and the page says to disable it in production because it leaks claim metadata
- **Evidence**: The "Debug JWT rejections" section and its sample response header.
- **Confidence**: emerging
- **Quote**: "Check that `kid` matches what the MCP server fetched from JWKS, `iss`/`aud` match your server's expected values, and `exp` hasn't passed. Disable in production, since the header leaks claim metadata."
- **Our assessment**: A real production hazard: the header exposes subject identity and scope to any response consumer. It is useful for a bounded 401 triage window, but should be treated as a temporary diagnostic switch with an explicit off step in the runbook.

### Claim 13: OpenAPI-backed MCP servers configured via `spec_path` do not support JWT injection — LiteLLM logs a warning and skips the header, so the request still reaches the backend unsigned
- **Evidence**: The "Limitations" section, first bullet.
- **Confidence**: emerging
- **Quote**: "**OpenAPI-backed MCP servers** (`spec_path` set) do not support JWT injection. LiteLLM logs a warning and skips the header. Use SSE/HTTP transport servers to get full JWT injection."
- **Our assessment**: This is a fail-open surface, and it is the most important operational caveat on the page. A server that enforces JWT verification will reject such calls; a server that merely accepts the header if present will accept them unsigned. The warning is the only signal, so it belongs in deployment checks rather than in prose only.

## Concrete Artifacts

**Minimal `mcp_jwt_signer` guardrail config (verbatim from "Basic setup"):**

```yaml
mcp_servers:
  - server_name: weather
    url: http://localhost:8000/mcp
    transport: http

guardrails:
  - guardrail_name: mcp-jwt-signer
    litellm_params:
      guardrail: mcp_jwt_signer
      mode: pre_mcp_call
      default_on: true
      issuer: "https://my-litellm.example.com"  # defaults to request base URL
      audience: "mcp"                            # default: "mcp"
      ttl_seconds: 300                           # default: 300
```

**Production signing key (verbatim):**

```bash
export MCP_JWT_SIGNING_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
# or point to a file
export MCP_JWT_SIGNING_KEY="file:///secrets/mcp-signing-key.pem"
```

**Server-side verification with FastMCP (verbatim from the page):**

```python
from fastmcp import FastMCP, Context
from fastmcp.server.auth.providers.jwt import JWTVerifier

auth = JWTVerifier(
    jwks_uri="https://my-litellm.example.com/.well-known/jwks.json",
    issuer="https://my-litellm.example.com",
    audience="mcp",
    algorithm="RS256",
)

mcp = FastMCP("weather-server", auth=auth)

@mcp.tool()
async def get_weather(city: str, ctx: Context) -> str:
    caller = ctx.client_id  # JWT `sub` — the verified user identity
    return f"Weather in {city}: sunny, 72°F (requested by {caller})"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**OIDC discovery contract (verbatim):**

```
GET /.well-known/openid-configuration  →  { "jwks_uri": "https://<litellm>/.well-known/jwks.json" }
GET /.well-known/jwks.json             →  { "keys": [{ "kty": "RSA", "alg": "RS256", ... }] }
```

**Required/optional claim gating (verbatim config excerpt):**

```yaml
      # Service accounts without `employee_id` are blocked before the tool runs
      required_claims:
        - "sub"
        - "employee_id"

      # Forward these into the outbound JWT when present — skipped silently if absent
      optional_claims:
        - "groups"
        - "department"
```

**Fail-closed 403 response body (verbatim):**

```text
HTTP 403
{ "error": "MCPJWTSigner: incoming token is missing required claims: ['employee_id']. Configure the IdP to include these claims." }
```

**AgentCore dual-token config (verbatim excerpt):**

```yaml
      audience: "mcp-resource"   # for the MCP resource layer
      ttl_seconds: 300

      # Second JWT for the transport channel — same sub/act/scope, different aud + TTL
      channel_token_audience: "bedrock-agentcore-gateway"
      channel_token_ttl: 60      # transport tokens should be short-lived
```

**Injected headers (verbatim):**

```
Authorization: Bearer <resource-token> — audience mcp-resource, TTL 300s
x-mcp-channel-token: Bearer <channel-token> — audience bedrock-agentcore-gateway, TTL 60s
```

**Debug response header (verbatim):**

```
x-litellm-mcp-debug: v=1; kid=a3f1b2c4d5e6f708; sub=alice@corp.com; iss=https://my-litellm.example.com; exp=1712345678; scope=mcp:tools/call mcp:tools/get_weather:call
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path addressed):

- `source-notes/docs-litellm-mcp-deployment.md` — **cited** (Extends; see below).
- `source-notes/docs-litellm-mcp-aws-sigv4.md` — **cited** (Extends; see below).
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch input-file rate limiting and enqueued-token accounting; no MCP auth or JWT surface.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**: provider-native web search support matrix; unrelated to gateway auth.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: Evaluations API state and grader prompts; unrelated.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native `generateContent` passthrough; unrelated.
- `source-notes/docs-litellm-enterprise.md` — **dismissed**: enterprise licensing/SSO/audit-log tiers; no MCP zero-trust signing content.
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**: supported-params gate and retry/timeout defaults; unrelated.
- `source-notes/docs-litellm-files-endpoints.md` — **dismissed**: provider `/files` passthrough; unrelated.
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock native Invoke passthrough routing/auth; no MCP JWT signing.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 4** — the auth-reference note records the same mechanism at summary level: "It signs every outbound tool call with a short-lived RS256 JWT and publishes a JWKS endpoint the MCP server can verify against. This is a guardrail (`guardrail: mcp_jwt_signer`, `mode: pre_mcp_call`) rather than an `auth_type`, and it composes with any `auth_type`." This page confirms and expands that description (Claims 1–4 here). The auth-reference note explicitly declines to mine the framework; this note fills that gap.
  - `source-notes/docs-litellm-mcp-guardrails.md` **Claim 1** and **Claim 2** — both sources place this control in the `pre_mcp_call` phase; the guardrails note covers PII/description scanning under the same phase, while this page covers outbound signing. Same phase, different control.
- **Contradicts**: None. The auth-reference note's "composes with any `auth_type`" is about the outbound-auth axis; this page's `spec_path` limitation is about the server transport/registration axis (OpenAPI-backed servers skip injection). Different axes, not opposing claims, so no contradiction issue was filed.
- **Extends**:
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 4** — one-line existence statement → full operational surface (key lifecycle, identity threading, claim gating/mutation, scopes, AgentCore, debug, limitations).
  - `source-notes/docs-litellm-mcp-deployment.md` — deployment topology and public-internet exposure controls; this page is the post-exposure attestation that a call actually came through the gateway. That note's Extraction Notes state it did not re-read `mcp_zero_trust` in full; this note closes that acknowledged gap.
  - `source-notes/docs-litellm-mcp-aws-sigv4.md` **Claim 1** — SigV4 signing for AgentCore connections (`aws_sigv4` outbound auth, per-request signing via `MCPSigV4Auth`; the config fields are Claim 2); this page adds the JWT-signer dual-token pattern for the same AgentCore target, a different layer of the same integration.
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md` — the CVE note documents MCP-surface RCE on the proxy host; this page is the complementary "prove the call traversed the gateway" control, not a defense against that creation-time injection. Cited as MCP blast-radius context only.
- **Adjacent / not conflated**:
  - `source-notes/docs-litellm-mcp-oauth.md` **Claim 1** (five MCP *outbound OAuth* patterns), `docs-litellm-mcp-obo-auth.md` **Claim 1** (OBO exchange), and `docs-litellm-mcp-oauth-passthrough.md` **Claim 1** (passthrough vs delegate admission) cover inbound/upstream credential flows. This page is outbound call attestation and is distinct; it composes with those `auth_type` flows rather than replacing them.
  - `source-notes/docs-litellm-generic-guardrail-api.md` — the webhook-based generic guardrail framework. Different framework; the `mcp_jwt_signer` is a built-in MCP guardrail, not a webhook provider. Not conflated.
  - `source-notes/docs-cncf-iam-whitepaper-reference-patterns.md` **Claim 10** and **Claim 13** — adjacent, not conflated, but a necessary security contrast. Claim 10's assessment names this same signer as "the corpus's only concrete gateway→verdict contract" and characterizes it as "a signed JWT, not a decision request" — i.e. the signer is a call-attestation artifact, not a PEP→PDP decision request. The CNCF note also carries, in its "Additional cross-references" section under the `docs-litellm-gateway-auth-reference.md` Claim 4 bullet, the distinction this note should preserve: the signer is "the corpus's only concrete gateway→backend cryptographic-identity surface," yet "a bearer JWT is verifiable but not sender-constrained." Claim 13 is the normative source of that constraint ("Access tokens and refresh tokens MUST be bound to external OAuth clients using DPoP or OAuth 2.0 Mutual-TLS to prevent unauthorized or illegitimate parties from using leaked or stolen tokens."), and Claims 8/12 add the SVID-based mutual authentication the paper mandates. So the `mcp_jwt_signer` proves the call traversed LiteLLM (Claim 1 here) but does not bind the token to the holder: a stolen JWT is replayable for up to `ttl_seconds` (Claim 2). That reinforces this note's Claim 1 framing ("attestation of *path*, not authorization of *intent*") rather than contradicting it — different security layer, not opposing claims.
- **Novel**: `end_user_claim_sources` and the `sub`/`act.sub` fallback chains; `required_claims` / `optional_claims` and the 403 body; `add_claims` → `set_claims` → `remove_claims` precedence; `allowed_scopes` replacing per-request least-privilege scopes; the AgentCore dual-token (`channel_token_audience` / `channel_token_ttl`, `x-mcp-channel-token`); `debug_headers` claim-metadata leak; and the `spec_path` fail-open limitation. A grep of `source-notes/` finds `mcp_jwt_signer` in `docs-litellm-gateway-auth-reference.md` (Claim 4 summary plus its cross-reference notes) and in `docs-cncf-iam-whitepaper-reference-patterns.md` (Claim 10's assessment and its Additional cross-references), but no earlier note documents the guardrail's operational surface — that is what this note adds.

## Guide Impact

- **Chapter 06 (Security and Trust) — MCP zero-trust attestation**: Add a subsection that states the threat model in Claim 1 and the control in Claim 2, then publishes the operating rules: pin `MCP_JWT_SIGNING_KEY` for production (Claim 3), rely on OIDC/JWKS discovery (Claim 4), and configure `end_user_claim_sources` so the backend sees a real identity rather than `"litellm-proxy"` (Claims 5, 7). Present `required_claims` as the fail-closed gate (Claim 8) and contrast it explicitly with the `spec_path` fail-open skip (Claim 13): do not let a server that merely accepts an optional JWT be described as "zero trust enforced." Also bound the claim: a signed bearer JWT attests path but is not sender-constrained, where the CNCF IAM whitepaper's Advanced pattern mandates sender-constrained tokens (DPoP or OAuth 2.0 Mutual-TLS) and mTLS/SVID (`docs-cncf-iam-whitepaper-reference-patterns.md` Claims 13, 8, 12) — state both layers so Chapter 06 does not present JWT signing as proof-of-possession.
- **Chapter 06 — least-privilege scope warning**: Document that default scopes are per-request least-privilege, but `allowed_scopes` replaces generation for every call; including `mcp:admin` grants it on read-only tools too (Claim 10). Add `debug_headers: false` as a production hardening item (Claim 12).
- **Chapter 05 (LLM Ops Reliability) — key lifecycle and restart runbook**: Add a pre-deployment and post-restart check: confirm `MCP_JWT_SIGNING_KEY` is set, confirm the backend verifier re-fetches JWKS by `kid`, and alert on signature failures clustered around proxy restarts (Claim 3). Add a startup-log check for the `spec_path` "JWT injection skipped" warning (Claim 13).
- **Chapter 03 (Runbooks and Agents) — 401 triage**: Add a bounded diagnostic procedure using `debug_headers: true` to compare `kid`/`iss`/`aud`/`exp`, with an explicit step to disable the header afterward (Claim 12). For AgentCore, verify both `Authorization` and `x-mcp-channel-token` are present with their separate audiences/TTLs (Claim 11).

## Extraction Notes

- Read the full live page via its markdown endpoint (`/docs/mcp_zero_trust.md`), including the claims-reference table and Limitations section. No substantive sub-pages were needed; the linked Related pages (`mcp_guardrail`, `mcp_oauth`, `mcp_aws_sigv4`) are already represented in the corpus and are cited rather than re-read.
- Quotes are verbatim contiguous fragments from the source markdown endpoint. Config/code blocks are copied as published; no reconstruction.
- All `miner-related-notes.md` candidates are addressed above (two cited, eight dismissed). Primary citations were checked against the cited notes' numbered claims before writing (§4b).
- The source is vendor capability documentation with no measured reliability or incident data, so `confidence_overall` is `emerging`. The two limitations are explicit first-party statements, not our inference.
