---
source_url: https://docs.litellm.ai/blog/realtime_webrtc_http_endpoints
source_type: blog-post
title: "Realtime WebRTC HTTP Endpoints"
author: "Sameer Kankute (SWE, LLM Translation), Krrish Dholakia (CEO), Ishaan Jaffer (CTO)"
date_published: 2026-03-12
date_extracted: 2026-07-29
last_checked: 2026-07-29
status: current
confidence_overall: emerging
issue: "#646"
---

# Realtime WebRTC HTTP Endpoints

> LiteLLM's vendor documentation for routing OpenAI-compatible WebRTC realtime audio API traffic through its proxy, describing the ephemeral token flow, SDP exchange via HTTP endpoints, and proxy configuration required to expose the browser-facing Realtime API surface — with no operational patterns, failure analysis, or performance benchmarks beyond the documented flow.

## Source Context

- **Type**: blog-post (vendor documentation page hosted on the LiteLLM docs blog)
- **Author credibility**: High for *what the LiteLLM proxy supports* — all three authors are LiteLLM team members (Sameer Kankute, SWE focused on LLM translation; Krrish Dholakia, CEO; Ishaan Jaffer, CTO). The content is official product documentation describing how to use a specific, shipped feature. Credibility for the documented flow is high; there are no independent benchmarks, operational experience reports, or failure analyses.
- **Scope**: Covers (1) proxy configuration for realtime models (`model_info: mode: realtime`), (2) the ephemeral token generation flow (`POST /v1/realtime/client_secrets`), (3) WebRTC SDP exchange routed through HTTP (`POST /v1/realtime/calls` with `application/sdp`), (4) client-side JavaScript code example covering all three steps, (5) Azure OpenAI backend support, (6) FAQ with five common issues. Does NOT cover: rate limiting for WebRTC connections, cost tracking for realtime sessions, key management for ephemeral connections, performance benchmarks vs direct OpenAI WebRTC, failure modes beyond 401 token expiry and no-audio, or comparative analysis with other proxy approaches.

## Extracted Claims

### Claim 1: LiteLLM proxy provides a `/v1/realtime/client_secrets` endpoint that generates encrypted, short-lived ephemeral tokens encoding the target model for routing, enabling browser/mobile clients to connect to the Realtime API via WebRTC without exposing a raw provider API key to the client
- **Evidence**: The page describes the "ephemeral token flow" architecture diagram and provides a client-side code example calling `POST /v1/realtime/client_secrets` with a LiteLLM API key and `{ model }` in the body, returning a `client_secret.value` encrypted token. The FAQ explicitly states the token encodes routing state including the target model.
- **Confidence**: settled (documented API behavior of a shipped LiteLLM proxy feature)
- **Quote**: "1. Get token - POST /v1/realtime/client_secrets with LiteLLM API key and { model }."
- **Our assessment**: This is the central architectural pattern of the source: the proxy acts as an auth intermediary that obtains a real token from the upstream provider (OpenAI/Azure), wraps it in an encrypted envelope, and returns it to the client. The client never holds the raw provider API key — only an ephemeral, model-scoped encrypted credential. This is a distinct pattern from standard chat/completions where the client passes its API key on every request. The claim is well-documented with a code example and two architecture diagrams; it reflects shipped proxy behavior. Confidence is settled as factual documentation.

### Claim 2: WebRTC SDP exchange is proxied through a standard HTTP POST endpoint (`/v1/realtime/calls`) using `application/sdp` content type, with the encrypted ephemeral token as the Bearer auth credential — not the user's raw API key
- **Evidence**: The "WebRTC handshake" step description and full JavaScript code example show the SDP offer being sent as plaintext body with `Content-Type: application/sdp` and `Authorization: Bearer <encrypted_token>`. The FAQ explicitly distinguishes this credential from the raw API key.
- **Confidence**: settled (documented API behavior)
- **Quote**: "2. WebRTC handshake - Create RTCPeerConnection, add mic track, create data channel oai-events, send SDP offer to POST /v1/realtime/calls with Authorization: Bearer <encrypted_token> and Content-Type: application/sdp."
- **Our assessment**: This is an architectural pattern worth noting: a non-HTTP protocol (WebRTC SDP) is tunneled through HTTP at the proxy layer. The proxy receives the SDP offer as HTTP body, handles the upstream negotiation with OpenAI/Azure via WebRTC internally, and returns the SDP answer as the HTTP response. This lets browser/mobile clients use standard fetch() without a WebRTC stack at the application layer. The security model (encrypted token, not raw API key) prevents the provider key from ever reaching the client device. This is the implicit operational pattern the Prospector flagged for extraction.

### Claim 3: Realtime models require `model_info: mode: realtime` in the proxy `config.yaml`, establishing a distinct model category for WebRTC realtime traffic separate from standard chat/completions, embedding, or image generation models
- **Evidence**: The Proxy Setup section provides the exact YAML configuration snippet with `model_info: mode: realtime`. Azure setup is also described.
- **Confidence**: settled (documented configuration syntax)
- **Quote**: (see Concrete Artifacts for the verbatim YAML config)
- **Our assessment**: The `mode: realtime` flag creates a routing distinction within the proxy's model registry. Models without this flag should not receive WebRTC traffic, and realtime WebRTC requests must target models flagged with this mode. This is significant for proxy operations: operators must explicitly declare which models support realtime, and the config structure defines a new model category alongside existing categories (chat, completion, embedding, image, etc.). The YAML snippet is the authoritative reference for this configuration pattern.

### Claim 4: WebRTC realtime tokens are intentionally short-lived and require a fresh token obtained immediately before the WebRTC offer is created to avoid 401 token-expired errors
- **Evidence**: The FAQ directly addresses this as a known operational concern with a clear recommended practice.
- **Confidence**: settled (explicitly documented by the vendor)
- **Quote**: "Q: What do I do if I get a 401 Token expired error? A: Tokens are short-lived. Get a fresh token right before creating the WebRTC offer."
- **Our assessment**: This is a concrete operational constraint for realtime proxy usage. Unlike standard chat API keys (long-lived, often stored as environment variables), WebRTC tokens must be fetched fresh on each connection attempt and must be used immediately. This token lifecycle pattern is an implicit operational requirement for any service or automation that connects to the Realtime API through the LiteLLM proxy: the token acquisition step cannot be pre-computed or cached meaningfully.

### Claim 5: The encrypted ephemeral token from `client_secrets` encodes all routing information including the target model, so the model parameter does not need to be passed separately in the SDP call request
- **Evidence**: The FAQ entry explicitly states this as a design property of the token-based routing model.
- **Confidence**: settled (explicitly documented by the vendor)
- **Quote**: "Q: Should I pass the model parameter when making the call? A: No, the encrypted token already encodes all routing information including model."
- **Our assessment**: This is a design choice that simplifies the client's responsibility: the token is a self-contained routing envelope. The client only needs to hold the token; the proxy extracts routing state from it during the SDP exchange. This eliminates a class of client-side configuration errors (model mismatch between token request and call request). From an operational standpoint, this means token management is the single point of configuration for WebRTC routing — lose the token's model binding, and the entire routing is wrong. The pattern is architecturally similar to JWT-based routing but uses LiteLLM's own encrypted token format.

### Claim 6: LiteLLM supports Azure OpenAI as a backend for WebRTC realtime connections, with the same proxy config pattern plus explicit `api_version`, `api_base`, and deployment configuration
- **Evidence**: The Proxy Setup section mentions Azure as an alternative backend, and the FAQ addresses Azure-specific `api-version` errors with a resolution.
- **Confidence**: settled (documented Azure-specific configuration)
- **Quote**: "Azure: use model: azure/gpt-4o-realtime-preview, api_key, api_base."
- **Quote**: "Q: How do I resolve Azure api-version errors? A: Set the correct api_version in litellm_params (or via the AZURE_API_VERSION environment variable), along with the right api_base and deployment values."
- **Our assessment**: Azure OpenAI support for WebRTC realtime means the proxy's realtime routing works across at least two provider backends. The Azure-specific configuration notes (explicit `api_version`, `api_base`) are consistent with Azure's general API surface, which requires more explicit URL construction than OpenAI's standard endpoint. The `AZURE_API_VERSION` env var alternative is a useful operational detail for containerized deployments where config is injected via environment rather than file.

## Concrete Artifacts

### Proxy configuration (verbatim from the page's YAML code block)

```yaml
model_list:
  - model_name: gpt-4o-realtime
    litellm_params:
      model: openai/gpt-4o-realtime-preview-2024-12-17
      api_key: os.environ/OPENAI_API_KEY
    model_info:
      mode: realtime
```

Attribution: https://docs.litellm.ai/blog/realtime_webrtc_http_endpoints, "Proxy Setup" section.

### Start command (verbatim from the page's bash code block)

```
litellm --config /path/to/config.yaml
```

Attribution: https://docs.litellm.ai/blog/realtime_webrtc_http_endpoints, "Proxy Setup" section.

### Full client-side JavaScript code example (verbatim from the page's code block)

```javascript
// 1. Token
const r = await fetch("http://proxy:4000/v1/realtime/client_secrets", {
  method: "POST",
  headers: { "Authorization": "Bearer sk-litellm-key", "Content-Type": "application/json" },
  body: JSON.stringify({ model: "gpt-4o-realtime" }),
});
const { client_secret } = await r.json();
const token = client_secret.value;

// 2. WebRTC
const pc = new RTCPeerConnection();
const audio = document.createElement("audio");
audio.autoplay = true;
pc.ontrack = (e) => (audio.srcObject = e.streams[0]);
const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
pc.addTrack(ms.getTracks()[0]);
const dc = pc.createDataChannel("oai-events");
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);
const sdpRes = await fetch("http://proxy:4000/v1/realtime/calls", {
  method: "POST",
  headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/sdp" },
  body: offer.sdp,
});
await pc.setRemoteDescription({ type: "answer", sdp: await sdpRes.text() });

// 3. Events
dc.send(JSON.stringify({ type: "session.update", session: { instructions: "..." } }));
```

Attribution: https://docs.litellm.ai/blog/realtime_webrtc_http_endpoints, "Client Usage" section, "Full code example" collapsible block.

### FAQ entries (verbatim from the page)

```
Q: What do I do if I get a 401 Token expired error?
A: Tokens are short-lived. Get a fresh token right before creating the WebRTC offer.

Q: Which key should I use for /v1/realtime/calls?
A: Use the encrypted token from client_secrets, not your raw API key.

Q: Should I pass the model parameter when making the call?
A: No, the encrypted token already encodes all routing information including model.

Q: How do I resolve Azure api-version errors?
A: Set the correct api_version in litellm_params (or via the AZURE_API_VERSION
   environment variable), along with the right api_base and deployment values.

Q: What if I get no audio?
A: Make sure you grant microphone permission, ensure pc.ontrack assigns the audio
   element with autoplay enabled, check your network/firewall for WebRTC traffic,
   and inspect the browser console for ICE or SDP errors.
```

Attribution: https://docs.litellm.ai/blog/realtime_webrtc_http_endpoints, "FAQ" section.

## Cross-References

- **Corroborates**:
  - `blog-litellm-june-townhall-updates.md` — that note's Claim 1 enumerates "14 fixes" under "Streaming / Realtime APIs" as a bug-fix category in the June townhall. The fixes *followed* this March documentation: LiteLLM shipped the WebRTC HTTP endpoint feature (this source, March 12) and then fixed 14 streaming/realtime bugs in June (that source, June 26). The two notes together show the product cycle: feature ship → bug-fix iteration.
  - `blog-litellm-may-townhall-updates.md` Claim 10 — that note's performance tracking framework includes TTFT and TPM for streaming, which are indirectly applicable to realtime WebRTC audio streams (the proxy must handle realtime audio packets, not just HTTP response bodies). While the May note's streaming metrics target `/chat/completions` specifically, the broader "performance tracking" framework is relevant to any realtime proxy route.

- **Contradicts**: None. No existing source note describes WebRTC routing through an LLM proxy, so there is nothing to contradict. No source note claims that WebRTC realtime traffic cannot be proxied through an existing HTTP gateway, or that such proxying requires different architectural patterns — this source simply documents that it is possible and how.

- **Extends**:
  - `blog-litellm-fastapi-middleware-performance.md` — that source describes LiteLLM proxy's FastAPI middleware optimization for standard HTTP request handling (chat/completions via BaseHTTPMiddleware → pure ASGI). This source extends the proxy's capability scope to include non-HTTP protocol routing (WebRTC SDP exchange tunneled through HTTP). Together they show the proxy handles two different transport modalities: standard HTTP request/response for chat, and WebRTC-over-HTTP for realtime audio.
  - `blog-litellm-june-townhall-updates.md` Claim 3 — the Rust migration benchmarks (150x lower overhead, 15x throughput, 11x lighter memory) are for the non-realtime request path. This source documents the feature set the Rust gateway will need to eventually support for realtime WebRTC traffic as the migration proceeds to full server coverage by December.

- **Novel**: The first source note in the corpus to introduce:
  - WebRTC realtime audio traffic proxied through an LLM gateway (no existing note covers any form of realtime media routing through an AI proxy).
  - The ephemeral token pattern for WebRTC auth (`/v1/realtime/client_secrets`) as distinct from standard API key auth for chat/completions.
  - The SDP-over-HTTP tunneling pattern (`/v1/realtime/calls` with `application/sdp` content type) — a non-HTTP protocol (WebRTC) tunneled through an HTTP proxy endpoint.
  - The `model_info: mode: realtime` configuration flag as a distinct model category in the proxy's model registry.
  - The encrypted token as a combined auth + routing envelope, eliminating the need for separate model parameter in nested API calls.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — proxy/gateway patterns)**: Add the WebRTC-over-HTTP proxy pattern as an advanced gateway routing capability beyond standard chat completions. Specific additions:
  - The ephemeral token flow (`/v1/realtime/client_secrets`) as a pattern for auth delegation to browser/mobile clients where the raw provider API key must not be exposed on the client device (Claims 1, 5). This extends Chapter 05's existing auth/routing coverage with a realtime-specific credential pattern.
  - The `model_info: mode: realtime` configuration flag as a model category system in proxy model registries (Claim 3) — operators managing multiple model categories (chat, completion, embedding, realtime) need to understand this routing distinction.
  - The short-lived token lifecycle constraint (Claim 4) as an operational requirement: automation that connects to the Realtime API cannot cache tokens and must implement fresh-token-on-every-connection logic.

- **Chapter 03 (Runbooks and Agents — realtime agent interaction)**: Add the WebRTC-to-proxy-to-provider architecture (Claim 2) as a reference pattern for agents that interact with users via realtime audio. The SDP exchange tunneled through HTTP means agent backend services can use standard HTTP client libraries (not WebRTC stacks) to manage realtime connections by handling the SDP negotiation at the proxy layer. The three-step client flow (token → SDP → events) documented in the full code example serves as a client integration template.

## Extraction Notes

- Source read in full. Docusaurus blog post at `https://docs.litellm.ai/blog/realtime_webrtc_http_endpoints`, published March 12, 2026, by Sameer Kankute, Krrish Dholakia, and Ishaan Jaffer. The page was fetched via direct HTTP (curl) and the raw HTML was parsed for verbatim text; all quoted passages were copied character-for-character from the rendered HTML text. The interactive "Try it live" tester section (embedded CSS/JS component for live WebRTC testing in the browser) was noted but its dynamic content could not be extracted as static text — the page's code example in the collapsible "Full code example" block provides the same content in static form.
- The page is self-contained. No substantive sub-pages needed following — the page links to two image files (WebRTC flow diagram, ephemeral token flow diagram) at `/assets/images/webrtc_flow-*.png` and `/assets/images/ephemeral_token-*.png`, which are architecture diagrams described adequately by the surrounding prose. The sidebar links to adjacent blog posts (newer "New Video Characters, Edit and Extension API support", older "Day 0 Support: GPT-5.4") are unrelated content. The enterprise callout (sidebar box promoting SSO/SAML, audit logs, spend tracking) is marketing copy.
- `confidence_overall` set to `emerging` (not `settled`): all claims describe factual, documented API behavior of a shipped LiteLLM proxy feature, so individual claims warrant `settled` at the level of "this is how the documented API works." However, the source as a whole is vendor documentation without independent verification, operational experience reports, performance benchmarks, failure analyses, or comparative patterns. The `emerging` rating reflects that these are documented API endpoints without evidence of production usage patterns or reliability characteristics. The sibling LiteLLM notes in the corpus use the same `emerging` rating for similar vendor documentation.
- The `miner-related-notes.md` candidates list was read per §4. All 10 listed candidates were evaluated:
  - `docs-langfuse-mcp-server.md` — dismissed; Langfuse MCP server documentation is unrelated to LiteLLM WebRTC realtime proxy patterns (different tool, different protocol, different domain).
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — dismissed; AI agent definition spectrum and SRE practices are unrelated to proxy WebRTC routing.
  - `docs-langfuse-security-and-guardrails.md` — dismissed; Langfuse security/guardrail patterns are unrelated to WebRTC proxy configuration.
  - `docs-google-sre-reliable-product-launches.md` — dismissed; SRE launch management is unrelated to LLM proxy feature documentation.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — dismissed; SLO framework is unrelated to proxy realtime routing.
  - `blog-litellm-observatory.md` — dismissed; load testing for release validation is unrelated to WebRTC proxy endpoints.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed; retail/gaming SRE is unrelated.
  - `blog-litellm-april-townhall-updates.md` — dismissed; CI/CD supply-chain patterns and Prisma migration failures are unrelated to WebRTC realtime proxy routing.
  - `blog-incidentio-ai-sre-incident-run.md` — dismissed; AI SRE incident management is unrelated.
  - `blog-litellm-claude-fable-5-day-0.md` — dismissed; Day 0 model support is unrelated to WebRTC proxy patterns.
  Additional cross-references were found by searching `source-notes/` for "realtime" and "WebRTC" and by reading the LiteLLM townhall notes suggested in the Prospector's triage (`blog-litellm-june-townhall-updates.md`, `blog-litellm-fastapi-middleware-performance.md`, `blog-litellm-may-townhall-updates.md`, `blog-litellm-april-townhall-updates.md`). The only overlapping note mentioning "realtime" is `blog-litellm-june-townhall-updates.md`, cited under Corroborates.
- No contradiction issue filed: verified against all existing source notes. No existing note describes WebRTC proxy routing, so there is nothing to contradict. The proxy middleware performance note (`blog-litellm-fastapi-middleware-performance.md`) covers HTTP middleware optimization for a different protocol layer (ASGI middleware for chat/completions), not WebRTC proxying. The LiteLLM townhall notes use "realtime" only in the context of streaming API bug-fix categories, not WebRTC routing — different scope, compatible findings.
