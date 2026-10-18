---
source_url: https://docs.litellm.ai/docs/guides/security_settings
source_type: docs
title: "SSL, HTTP Proxy Security Settings | LiteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-18)
date_extracted: 2026-10-18
last_checked: 2026-10-18
status: current
confidence_overall: emerging
issue: "#1784"
---

# SSL, HTTP Proxy Security Settings (LiteLLM Docs)

> LiteLLM documents operational TLS and egress proxy controls for gateway operators: CA bundle configuration, verification toggles, client certificates, ECDH curve tuning (including disabling PQC for performance), proxy env var semantics across aiohttp/httpx transports, and per-service/guardrail SSL overrides. The page is a reference surface; claims are vendor assertions requiring verification against deployed LiteLLM versions.

## Source Context

- **Type**: docs (vendor reference documentation, LiteLLM guides under `docs.litellm.ai`).
- **Canonical URL**: `https://docs.litellm.ai/docs/guides/security_settings` (the originally submitted `guides/security_network` is a redirect stub returning a meta-refresh to this canonical page).
- **Author credibility**: LiteLLM (BerriAI) first-party vendor documentation. Authoritative for *what the vendor asserts*; every operational claim below is treated as `[emerging]` until verified against the actual LiteLLM code/version in use.
- **Scope**: TLS verification (custom CA, disable verification, lower security level), mTLS/client cert auth, ECDH curve configuration and fallback behavior, HTTP proxy resolution (`HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`) across transports, distinction between `DISABLE_AIOHTTP_TRUST_ENV` and `AIOHTTP_TRUST_ENV`, and per-service SSL verification overrides (SDK per-call, per-guardrail in config). Does not cover data retention/redaction or end-to-end encryption guarantees beyond transport verification.
- **Note on redirect**: Issue #1784 submitted `security_network` as the source URL; the triage explicitly directs mining the canonical redirected URL. This note records the canonical URL as `source_url`.

## Extracted Claims

### Claim 1: Custom CA bundle can be configured via `SSL_CERT_FILE` env var or by passing a string to `ssl_verify` (SDK/proxy)
- **Evidence**: Docs show setting a custom CA bundle path using `SSL_CERT_FILE` environment variable or passing a string to `ssl_verify`. Examples given for SDK (`litellm.ssl_verify="client.pem"`), PROXY (`litellm_settings.ssl_verify: "client.pem"`), and Environment Variables (`export SSL_CERT_FILE="client.pem"`).
- **Confidence**: emerging (vendor docs claim)
- **Quote**: "You can set a custom CA bundle file path using the `SSL_CERT_FILE` environmental variable or passing a string to the the ssl_verify setting."
- **Our assessment**: Concrete, actionable config surface. The note about precedence ("Be aware that environmental variables take precedence over the settings in the SDK.") appears early on the page, setting up the precedence chain elaborated later.

### Claim 2: SSL verification can be disabled via `ssl_verify=False` or `SSL_VERIFY="False"` (explicit footgun)
- **Evidence**: Explicit example disabling verification in SDK, PROXY, and env vars.
- **Confidence**: emerging
- **Quote**: "Disable SSL verification" (section heading) with SDK example `litellm.ssl_verify = False`, proxy `ssl_verify: false`, env `export SSL_VERIFY="False"`.
- **Our assessment**: Documents the disabling knob explicitly. For Ch06, this is a footgun that must be called out as weakening transport verification; operator must understand blast radius (all calls using that scope unless overridden). No built-in warning text beyond showing the option.

### Claim 3: OpenSSL security level can be lowered via `ssl_security_level` / `SSL_SECURITY_LEVEL` (footgun)
- **Evidence**: Section 3 shows setting `ssl_security_level="DEFAULT@SECLEVEL=1"` in SDK, PROXY, and env vars.
- **Confidence**: emerging
- **Quote**: "The `ssl_security_level` allows setting a lower security level for SSL connections."
- **Our assessment**: Documents lowering security level as a supported option. Needs to be flagged as a weakening posture in hardening guidance.

### Claim 4: Client certificate authentication (mTLS) via `ssl_certificate` / `SSL_CERTIFICATE`
- **Evidence**: Section 4 documents client-side certificate auth to server via `ssl_certificate` attribute or `SSL_CERTIFICATE` env var, with examples for SDK, PROXY, env.
- **Confidence**: emerging
- **Quote**: "The `SSL_CERTIFICATE` environmental variable or `ssl_certificate` attribute allows setting a client side certificate to authenticate the client to the server."
- **Our assessment**: Supports mutual TLS topologies where gateway/client cert is required.

### Claim 5: ECDH curve tuning to disable PQC for performance; invalid curve falls back with warning
- **Evidence**: Section 5 documents `ssl_ecdh_curve` / `SSL_ECDH_CURVE` to configure ECDH curve. Explicit use case: OpenSSL 3.x enabling PQC by default can slow TLS handshakes; setting to `X25519` disables PQC and can improve performance. Lists common curves (`X25519`, `prime256v1`, `secp384r1`, `secp521r1`). Notes: if invalid or unsupported, LiteLLM logs warning and continues with default curves.
- **Confidence**: emerging (performance claim is vendor-stated; "significantly improve connection performance" is qualitative)
- **Quote**: "Setting the ECDH curve to `X25519` disables PQC and can significantly improve connection performance."
- **Quote**: "If an invalid curve name is provided or if your Python/OpenSSL version doesn't support this feature, LiteLLM will log a warning and continue with default curves."
- **Our assessment**: Novel operational lever (ECDH curve selection to trade PQC off for handshake latency). The graceful degradation (warning + fallback, not fail-closed) is a concrete behavior detail worth capturing. Treat performance claim as anecdotal until measured in operator context.

### Claim 6: Proxy env vars are honored on both aiohttp and httpx transports; no extra flag needed
- **Evidence**: Section 6 states LiteLLM resolves `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` from the environment for every LLM request on both the default aiohttp transport and httpx transport (`DISABLE_AIOHTTP_TRANSPORT=True`), with or without `force_ipv4`. Examples show setting `HTTPS_PROXY` and `NO_PROXY` for SDK/PROXY contexts via env.
- **Confidence**: emerging
- **Quote**: "LiteLLM resolves `HTTP_PROXY`, `HTTPS_PROXY` and `NO_PROXY` from the environment for every LLM request on both the default aiohttp transport and the httpx transport (`DISABLE_AIOHTTP_TRANSPORT=True`), with or without `force_ipv4`. No extra flag is needed; set the variables before the proxy or SDK starts:"
- **Our assessment**: Documents transport parity for proxy resolution — a useful operational detail for debugging egress routing. Confirms env-vars as the primary interface.

### Claim 7: `DISABLE_AIOHTTP_TRUST_ENV` and `AIOHTTP_TRUST_ENV` control trust_env behavior and are unrelated to proxy selection
- **Evidence**: Section 6 clarifies distinction: `DISABLE_AIOHTTP_TRUST_ENV=True` (or `litellm.disable_aiohttp_trust_env=True`) makes aiohttp transport ignore proxy vars. `AIOHTTP_TRUST_ENV` (or `litellm.aiohttp_trust_env`) is unrelated to proxy selection — it passes `trust_env=True` to the aiohttp session so aiohttp also reads `~/.netrc` and `SSL_CERT_FILE`/`SSL_CERT_DIR`.
- **Confidence**: emerging
- **Quote**: "Set `DISABLE_AIOHTTP_TRUST_ENV=True` (or `litellm.disable_aiohttp_trust_env = True`) to make the aiohttp transport ignore these variables. `AIOHTTP_TRUST_ENV` (or `litellm.aiohttp_trust_env`) is unrelated to proxy selection: it passes `trust_env=True` to the aiohttp session so aiohttp itself also reads `~/.netrc` and `SSL_CERT_FILE` / `SSL_CERT_DIR`."
- **Our assessment**: Explicitly calls out a common point of confusion ("unrelated to proxy selection"). The docs are precise here; this is high-value for operators troubleshooting auth (netrc) and CA discovery in aiohttp sessions.

### Claim 8: Per-service SSL verification overrides are supported (Bedrock per-call; guardrails per-config)
- **Evidence**: Section 7 documents overriding SSL verification per service. For Bedrock SDK: pass `ssl_verify` directly in `completion()` call (can be path or `False`). For AIM guardrail (proxy): set `ssl_verify` in guardrails config under `litellm_params` (path). For Cato Networks guardrail (proxy): same pattern with `guardrail: cato_networks` and `ssl_verify` path.
- **Confidence**: emerging
- **Quote**: "LiteLLM allows you to override SSL verification settings for specific services or provider calls. This is useful when different services (e.g., an internal guardrail vs. a public LLM provider) require different CA certificates."
- **Quote**: "You can pass `ssl_verify` directly in the `completion` call." (Bedrock example showing `ssl_verify="path/to/bedrock_cert.pem"` or `False`)
- **Our assessment**: Supports multi-tenant/heterogeneous egress topologies (different CAs for internal guardrails vs external providers). The blast radius of weakening verification can be scoped narrowly — but also introduces risk of inconsistent posture if misconfigured.

### Claim 9: SSL verification resolution priority is explicitly documented (parameter → env → global → system)
- **Evidence**: Section 7 "Priority Logic" states the exact order:
  1. Explicit Parameter (passed in `completion()` or guardrail config)
  2. Environment Variable (`SSL_VERIFY`)
  3. Global Setting (`litellm.ssl_verify`)
  4. System Standard (`SSL_CERT_FILE`)
- **Confidence**: emerging
- **Quote**: "LiteLLM resolves `ssl_verify` using the following priority: 1. **Explicit Parameter**: Passed in `completion()` or guardrail config. 2. **Environment Variable**: `SSL_VERIFY` environment variable. 3. **Global Setting**: `litellm.ssl_verify` setting. 4. **System Standard**: `SSL_CERT_FILE` environment variable."
- **Our assessment**: The key operational rule for debugging "why is my custom CA ignored?" incidents. This is a concrete, testable ordering claim; operators can verify it by experimentation. The page's early note about env precedence aligns with this chain.

## Concrete Artifacts

```yaml
# Proxy config example: per-guardrail ssl_verify override
guardrails:
  - guardrail_name: aim-protected-app
    litellm_params:
      guardrail: aim
      ssl_verify: "/path/to/aim_cert.pem"
```

```yaml
# Proxy global ssl_verify
litellm_settings:
  ssl_verify: "client.pem"
```

```python
# SDK: disable verification
import litellm
litellm.ssl_verify = False
```

```python
# SDK: per-call override (Bedrock)
response = litellm.completion(
    model="bedrock/us.anthropic.claude-sonnet-5",
    messages=[{"role": "user", "content": "hi"}],
    ssl_verify="path/to/bedrock_cert.pem"  # or False
)
```

```bash
# Proxy env vars
export HTTPS_PROXY='http://username:password@proxy_uri:port'
export NO_PROXY='localhost,127.0.0.1'
export SSL_CERT_FILE="client.pem"
export SSL_VERIFY="False"
export SSL_SECURITY_LEVEL="DEFAULT@SECLEVEL=1"
export SSL_CERTIFICATE="/path/to/certificate.pem"
export SSL_ECDH_CURVE="X25519"
```

## Cross-References

- **Corroborates**: `source-notes/docs-litellm-data-security.md` — same vendor docs site/trust posture. The data-security page focuses on privacy/telemetry and cookie policy; this page is the transport/proxy configuration counterpart. Both treat vendor assertions as `[emerging]` and emphasize operator responsibility boundaries.
- **Contradicts**: none identified (complementary reference documentation)
- **Extends**: `source-notes/docs-litellm-data-security.md` — adds concrete TLS/egress knobs the earlier data-security page explicitly omits (encryption in transit configuration surface). Also relates to `source-notes/docs-litellm-completion-http-handler-config.md` (HTTP handler/transport tuning) though that note focuses on different transport behaviors; no direct TLS/proxy overlap.
- **Novel**: This is the first captured source note covering LiteLLM's SSL verification precedence, per-service/guardrail `ssl_verify` overrides, ECDH curve configuration (`ssl_ecdh_curve` / `X25519`) with documented fallback behavior, and the explicit distinction between `DISABLE_AIOHTTP_TRUST_ENV` vs `AIOHTTP_TRUST_ENV` (and that the latter is unrelated to proxy selection). No existing claim in the corpus matches `ssl_verify`, `SSL_CERT_FILE`, `SSL_CERTIFICATE`, `SSL_ECDH_CURVE`, `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`, or the trust-env distinction.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Add operator guidance on egress boundary controls for LLM gateways. Specifically document the `ssl_verify` precedence order (explicit param → SSL_VERIFY → global → SSL_CERT_FILE) as the canonical troubleshooting rule. Call out footguns (`ssl_verify=False`, `ssl_security_level="DEFAULT@SECLEVEL=1"`) as weakening postures requiring justification and blast radius containment. Document per-service/guardrail `ssl_verify` overrides as a pattern for heterogeneous CA requirements while warning against inconsistent verification posture.
- **Chapter 06 (Security and Trust)**: Capture the `DISABLE_AIOHTTP_TRUST_ENV` vs `AIOHTTP_TRUST_ENV` distinction (proxy selection independence) as a common misconfiguration gotcha for aiohttp-based deployments reading `.netrc`/system certs.
- **Chapter 05 (LLM Ops Reliability)**: Add TLS handshake tuning guidance referencing `ssl_ecdh_curve="X25519"` to disable PQC in OpenSSL 3.x where latency-sensitive; note the documented behavior (warning + fallback on invalid/unsupported curve) and that performance claims need validation in the specific environment.

## Extraction Notes

- **Redirect handling**: The submitted URL `guides/security_network` returned a 355-byte HTML meta-refresh redirecting to `guides/security_settings`. The canonical target was mined as `source_url` per triage instructions. No content extracted from the stub.
- **Source depth**: Read the entire canonical page including all sections (1-7), code blocks, and explanatory text. Followed the triage's specific extractables list.
- **Confidence rationale**: This is vendor reference documentation with concrete, falsifiable configuration keys and behaviors (precedence order, fallback behavior, transport parity). However it is unvalidated by code inspection in this extraction; confidence remains `emerging`. Claims are quoted verbatim where possible from the rendered docs content captured.
- **Cross-reference check**: Searched existing `source-notes/` for SSL/TLS/proxy terms (ssl_verify, SSL_CERT_FILE, SSL_CERTIFICATE, SSL_ECDH_CURVE, HTTP_PROXY, HTTPS_PROXY, NO_PROXY, DISABLE_AIOHTTP_TRUST_ENV, AIOHTTP_TRUST_ENV) — no existing notes cover this surface. The adjacent `docs-litellm-data-security.md` is complementary (privacy/telemetry) and already cited.
