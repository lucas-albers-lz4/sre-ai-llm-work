---
source_url: https://docs.litellm.ai/blog/headroom-integration
source_type: blog-post
title: "LiteLLM × Headroom: Use 60-95% fewer tokens with Claude Code"
author: "Krrish Dholakia (CEO, LiteLLM) and Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-06-30
date_extracted: 2026-07-23
last_checked: 2026-07-23
status: current
confidence_overall: emerging
issue: "#439"
---

# LiteLLM × Headroom: Use 60-95% fewer tokens with Claude Code

> A vendor partnership announcement describing how Headroom — a prompt-compression
> sidecar — integrates with the LiteLLM proxy as a `pre_call` guardrail, claiming
> 60-95% token reduction for Claude Code and other LLM clients. The post documents
> a sidecar guardrail architecture pattern (fail-open reliability, transparent
> dual-format support, per-key/per-request/global config) that is the corpus's first
> coverage of prompt compression as a guarded middleware pattern. Evidence is thin
> (vendor claims without independent benchmarks) but the architectural pattern is
> novel for the corpus.

## Source Context

- **Type**: blog-post (vendor partnership announcement), tagged `partnership`,
  `guardrails`, `context`, `headroom`, `claude-code`.
- **Author credibility**: Co-authored by LiteLLM's CEO (Krrish Dholakia) and CTO
  (Ishaan Jaffer). Claims about how the integration works are authoritative for
  LiteLLM product behavior; the token-reduction claims (60-95%) are vendor marketing
  with no independent benchmarks or methodology disclosed. The post is primarily a
  partnership announcement between LiteLLM and Headroom Labs.
- **Scope**: Covers (1) the sidecar guardrail architecture pattern, (2) fail-open
  reliability design, (3) dual-format API support (OpenAI + Anthropic), (4) the
  admin-to-developer key handoff pattern for Claude Code teams, (5) config granularity
  (per-key, per-request, global), (6) verification via response headers. Does NOT
  cover: compression algorithms, benchmark methodology, latency impact measurements,
  pricing, or detailed configuration beyond the quick-start pattern. The companion
  setup guide at `/docs/proxy/headroom` was also read for concrete artifacts (config
  YAML, curl commands, environment variables). The GitHub discussion thread (linked
  in the post) was read for user-reported issues.

## Extracted Claims

### Claim 1: Headroom runs as a sidecar guardrail on the LiteLLM proxy, invoked via the pre_call hook — clients and LLM providers never interact with it directly
- **Evidence**: The post states the architecture explicitly. The request flow is:
  Client → LiteLLM gateway → Headroom compression (`pre_call`) → compressed payload →
  upstream LLM. The docs page confirms "Only `pre_call` is meaningful; the guardrail is
  a no-op on responses."
- **Confidence**: settled (stated architectural fact about the LiteLLM product)
- **Quote**: "Headroom runs as a sidecar to LiteLLM." and "Clients and the LLM provider
  never talk to Headroom directly."
- **Our assessment**: The architectural claims are settled — they describe how the
  LiteLLM product works. The sidecar design is the key pattern: the guardrail lives
  outside the gateway process but is called in-band during request processing. This
  is the corpus's first coverage of a sidecar guardrail deployed at the gateway level
  (as opposed to in-process middleware or client-side libraries). The pattern is
  generally applicable to any LLM gateway that supports pre/post-call hooks.

### Claim 2: The sidecar architecture provides fail-open reliability — if Headroom goes down, LLM calls are unaffected
- **Evidence**: Listed as the second of two bullet points in the "How is it deployed?"
  section of the blog post.
- **Confidence**: emerging (stated claim without failure-mode evidence or
  testing methodology)
- **Quote**: "Reliability: If Headroom goes down, your LLM calls are unaffected."
- **Our assessment**: This is a significant reliability claim — the guardrail is not
  in the critical path for availability, only for optimization. The fail-open design
  means a Headroom outage results in uncompressed (but functional) LLM calls rather
  than a gateway failure. We rate this emerging rather than settled because the post
  provides no testing methodology, failure-injection results, or timeout configuration
  details to back the claim. For the guide, this is the most important architectural
  takeaway: a sidecar guardrail with fail-open behavior is the recommended deployment
  model for non-critical guardrails (optimization, enrichment) vs. in-line middleware
  for critical guardrails (auth, rate limiting).

### Claim 3: Supports both OpenAI /v1/chat/completions and Anthropic /v1/messages formats, enabling transparent Claude Code compression with no client-side changes
- **Evidence**: Explicitly stated in the post and confirmed in the docs page. The
  three-step Claude Code rollout flow demonstrates the pattern: admin registers Headroom,
  admin issues per-developer keys with guardrail bound, developer points Claude Code at
  the proxy via `ANTHROPIC_BASE_URL`.
- **Confidence**: settled (product feature, verifiable from the docs)
- **Quote**: "Compression works on both /v1/chat/completions and /v1/messages (Anthropic
  format)," and "No client-side change, no code diff."
- **Our assessment**: The `/v1/messages` format support is what makes Claude Code
  integration seamless — the developer does not need to switch API formats. The three-step
  admin→developer handoff is a concrete rollout pattern the guide should document for
  any team deploying proxy-level compression for Claude Code users. The GitHub discussion
  confirms maintainer intent to add `/v1/responses` support for Codex as well, showing
  the format-agnostic design is a deliberate pattern.

### Claim 4: Claims 60-95% token reduction — vendor-marketed claim with no independent benchmarks or methodology disclosed
- **Evidence**: The post title states "Use 60-95% fewer tokens" but provides no test
  methodology, benchmark suite, dataset, or independent verification. No per-use-case
  breakdown of when 60%, 95%, or any intermediate reduction applies.
- **Confidence**: anecdotal (unsupported vendor claim)
- **Quote**: (the title itself makes the claim; no additional evidence paragraph exists
  in the source to quote) — "LiteLLM × Headroom: Use 60-95% fewer tokens with Claude Code"
- **Our assessment**: This is the weakest part of the source. The range is extremely wide
  (60-95% = 35 percentage points of variance) with no conditioning variables explaining
  when users should expect which end of the range. Without methodology, dataset, or
  independent reproduction, this claim is not actionable for the guide. The Smith should
  treat this as a directional signal ("prompt compression can substantially reduce token
  usage") rather than a citeable benchmark. A separate source note based on independent
  benchmarking would be valuable.

### Claim 5: LiteLLM provides a retrieve_headroom tool so the model can recover the full original context when compression loses fidelity
- **Evidence**: Stated in the post's third paragraph: "If the model needs the full
  context, LiteLLM will also pass a 'retrieve_headroom' tool to the model so it can
  retrieve the complete context from Headroom." The docs page confirms Headroom returns
  compressed content with retrieval identifiers embedded as placeholders.
- **Confidence**: emerging (described at the integration level, not the mechanism level)
- **Quote**: "If the model needs the full context, LiteLLM will also pass a
  'retrieve_headroom' tool to the model so it can retrieve the complete context from
  Headroom."
- **Our assessment**: This is a clever pattern that addresses the key concern with lossy
  compression: the model can retrieve the original when needed (e.g., when a code snippet
  was compressed too aggressively and the model needs exact characters). The GitHub
  discussion reveals this tool is NOT automatically exposed to all clients — one user
  reported it was not available in OpenCode, suggesting the tool injection depends on
  the client's tool-use capabilities. The guide should note this as an advanced pattern
  with client-dependent availability.

### Claim 6: Configurable per key, per request, or globally via default_on: true, with verification via the x-litellm-applied-guardrails response header
- **Evidence**: The post states "Turn it on per key, per request, or globally via
  default_on: true." The docs page provides concrete examples for each mode. The
  response header is documented on the page.
- **Confidence**: settled (documented product feature)
- **Quote**: "Turn it on per key, per request, or globally via default_on: true."
  — and — "an `x-litellm-applied-guardrails: headroom-compression` header so the
  caller can confirm compression actually ran."
- **Our assessment**: This is standard LiteLLM guardrail config — the same granularity
  model used for other guardrails (content moderation, PII detection). The per-key
  pattern is the recommended production approach for Claude Code: admin creates a key
  with the guardrail bound, distributes to developers, and can audit adoption via
  response headers. The per-request opt-in via `guardrails` array (or `litellm_metadata`
  for Anthropic format) provides flexibility for development/testing.

### Claim 7: The admin-to-developer virtual key handoff pattern enables teams to roll out compression transparently — admin binds the guardrail to a key, developer uses ANTHROPIC_BASE_URL with no code changes
- **Evidence**: The docs page provides a concrete three-step process: (1) admin registers
  Headroom in config.yaml, (2) admin issues per-developer keys with the guardrail bound
  via `/key/generate`, (3) developer sets `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN`
  environment variables. Developers can bypass compression per-request via
  `x-headroom-bypass: true` header.
- **Confidence**: settled (documented, reproducible workflow)
- **Quote**: "a platform admin wants to cut input token spend for a team that drives
  heavy traffic through Claude Code" — and — "they can set the `x-headroom-bypass:
  true` header on that call."
- **Our assessment**: This is the most reusable production pattern in the source. The
  key insight is separation of concerns: the admin controls which requests get compressed
  (via key binding), the developer gets compression for free, and individual developers
  can bypass per-request via a header. This pattern is generalizable beyond Headroom to
  any gateway-level guardrail that needs selective enforcement across teams.

### Claim 8: Headroom protects two message types by default — user/system messages are NOT compressed without HEADROOM_COMPRESS_USER_MESSAGES=1, and messages with Anthropic cache_control markers are NEVER compressed
- **Evidence**: Documented on the Headroom setup guide page in a "Why
  requests_compressed Can Be 0" section. The cache_control protection preserves
  prompt-cache byte matching. The user message protection note states: "Most Claude
  Code traffic is `user` role, so a default deployment compresses none of it."
- **Confidence**: settled (documented product behavior)
- **Quote**: "protects two message types by default" — and — "with an Anthropic
  `cache_control` marker."
- **Our assessment**: This is a critical operational detail. A team deploying Headroom
  without setting `HEADROOM_COMPRESS_USER_MESSAGES=1` would see zero compression on
  Claude Code traffic where most messages are `user` role. The `cache_control` protection
  means prompt caching and compression are compatible — Headroom preserves cached
  prefixes. The guide should document both defaults clearly to prevent misconfiguration.

### Claim 9: The GitHub discussion reveals user-reported issues — the headroom guardrail requires v1.92.x (ValueError on earlier versions) and the retrieve_headroom tool is not exposed to all clients
- **Evidence**: The GitHub discussion documents: (a) `ValueError: Unsupported guardrail:
  headroom` error on LiteLLM v1.90.2 and initial v1.92.0-dev.1 installations, (b) user
  qschweitzer reported the error "disappeared" after switching to Docker Compose, (c)
  user D0wn10ad reported `retrieve_headroom` not being exposed in OpenCode — the model
  responded "I can't call headroom_retrieve in this session because that tool is not
  exposed to me."
- **Confidence**: settled (user reports are verifiable in the public discussion thread)
- **Quote**: (from the GitHub discussion) "ValueError: Unsupported guardrail: headroom"
  — and — "I can't call headroom_retrieve in this session because that tool is not
  exposed to me."
- **Our assessment**: The version gate (v1.92.x required) is a concrete operational
  constraint not highlighted in the blog post itself. The Docker Compose resolution
  suggests a dependency or configuration issue in the raw Python package path. The
  `retrieve_headroom` tool availability issue is a significant limitation: the
  full-context retrieval pattern only works in clients that support tool injection
  from the proxy. The guide should note these as known constraints.

## Concrete Artifacts

### Configuration YAML (verbatim from the Headroom setup guide)

```yaml
guardrails:
  - guardrail_name: headroom-compression
    litellm_params:
      guardrail: headroom
      mode: pre_call
      api_base: https://your-headroom-service
#     api_key: os.environ/HEADROOM_API_KEY  [OPTIONAL]
#     default_on: true [OPTIONAL]
```

Source: https://docs.litellm.ai/docs/proxy/headroom — "Quick Start" section.
The `model_list` section is omitted for brevity; the guardrail section is the
relevant configuration artifact.

### Per-developer key generation (verbatim curl from the Headroom setup guide)

```bash
curl -X POST 'http://0.0.0.0:4000/key/generate' \
  -H 'Authorization: Bearer sk-1234' \
  -H 'Content-Type: application/json' \
  -d '{
        "key_alias": "claude-code-alice",
        "guardrails": ["headroom-compression"],
        "models": ["claude-sonnet-4"],
        "metadata": {"team": "claude-code-rollout"}
      }'
```

Source: https://docs.litellm.ai/docs/proxy/headroom — "Claude Code" section.

### Headroom Dockerfile (verbatim from the Headroom setup guide)

```dockerfile
FROM python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir "headroom-ai[proxy]==0.27.0" \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
EXPOSE 8787
ENV HEADROOM_TELEMETRY=off
CMD ["headroom", "proxy", "--host", "0.0.0.0", "--port", "8787"]
```

Source: https://docs.litellm.ai/docs/proxy/headroom — "Deploy Headroom" section.

### Configuration reference table (reconstructed from the Headroom setup guide)

| Param | Type | Description |
|---|---|---|
| `guardrail` | str | Must be `headroom`. |
| `mode` | str | Use `pre_call`. No-op on responses. |
| `api_base` | str | Base URL of the headroom service. Falls back to `HEADROOM_API_BASE` env var. Required. |
| `api_key` | str | Bearer token for headroom service. Falls back to `HEADROOM_API_KEY`. Optional. |
| `model` | str | Model forwarded to `/v1/compress`. Defaults to the request's `model` field. |
| `default_on` | bool | Run guardrail on every request. Defaults to `false`. |

Source: https://docs.litellm.ai/docs/proxy/headroom — Configuration Reference section.

### User-reported errors from GitHub discussion (verbatim)

```
ValueError: Unsupported guardrail: headroom
```
— Reported by tnndclub on LiteLLM v1.90.2 and qschweitzer on initial v1.92.0-dev.1 install.

```
I can't call headroom_retrieve in this session because that tool is not exposed to me.
```
— Reported by D0wn10ad; the `retrieve_headroom` tool was not available in OpenCode.

Source: https://github.com/BerriAI/litellm/discussions/31816 — comments by tnndclub
(Jul 1), qschweitzer (Jul 2), and D0wn10ad (Jul 14).

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-production-ai-agent-gaps.md` **Claim 14** — Guardrails require
    defense-in-depth with synchronous and asynchronous checks. The Headroom `pre_call`
    sidecar pattern is a concrete implementation of a *synchronous* guardrail (checked
    before the LLM call), with the fail-open design providing the reliability tradeoff
    that Claim 14's sync/async classification calls for: synchronous for optimization
    (safe to fail open), async for security (must not be bypassed).

- **Extends**:
  - `blog-litellm-fastapi-middleware-performance.md` — That note covers LiteLLM proxy
    *middleware* architecture (ASGI middleware replacement for performance). This note
    covers LiteLLM proxy *guardrail* architecture (sidecar pattern for prompt compression).
    Together they bracket the two extensibility mechanisms of the LiteLLM proxy: middleware
    hooks for proxy-internal processing, and guardrail hooks (`pre_call`/`post_call`) for
    external service integration. The guide should treat these as complementary —
    middleware for in-process concerns, guardrails for sidecar services.
  - `docs-langfuse-security-and-guardrails.md` **Claim 1** — Two-pronged architecture
    (runtime guardrails + post-hoc observability). The Headroom integration is a runtime
    guardrail at the gateway level (before the LLM call), while Langfuse operates at the
    application level (traced `@observe()` decorators around the guardrail call). Both
    are guardrail implementations at different stack layers: Headroom at the
    proxy/reverse-proxy layer, Langfuse at the application/SDK layer. The guide should
    distinguish these layers.
  - `docs-google-sre-prodcast-05-06-ai-safety.md` **Claim 5** — Multi-layered defense
    architecture (system instructions → filters → LLM-classifier → ART). The Headroom
    sidecar operates at the gateway/proxy layer, conceptually between "system instructions"
    and "filters" — it modifies the input before the model sees it. This introduces a
    prompt optimization/compression layer not explicitly covered by the Prodcast's model.

- **Novel**: First source note in the corpus to introduce:
  - **Prompt compression as a guardrail pattern** deployed at the gateway/proxy level
    (as opposed to client-side compression libraries).
  - The **sidecar guardrail architecture** with fail-open reliability — a guardrail
    that lives outside the gateway process, is called in-band during request processing,
    and can fail without affecting availability. This is a distinct deployment model
    from the in-process middleware guardrails covered in
    `docs-langfuse-security-and-guardrails.md`.
  - The **admin-to-developer key handoff pattern** for guardrail rollout — admin binds
    the guardrail to a virtual key, developer consumes transparently via environment
    variables, with per-request bypass via header.
  - The **dual-format support pattern** (OpenAI + Anthropic) as a first-class design
    consideration for proxy-level tooling — enabling transparent adoption by Claude Code
    without API format migration.
  - The **retrieve_headroom full-context retrieval tool** pattern — a mechanism for
    the model to recover original content after lossy compression, injected as a tool
    by the proxy.
  - **Content protection defaults** for prompt compression — Headroom's dual protection
    (user messages require opt-in, cache_control markers are never compressed) is a
    specific operational detail any compression-at-the-proxy deployment must consider.
  - Real-world **user-reported integration issues** from the GitHub discussion,
    providing the corpus's first practitioner evidence for a prompt compression tool
    (version gate, tool exposure limitations).

- **Contradicts**: None identified. The fail-open design (Claim 2) does not oppose the
  sync/async guardrail classification in `blog-pagerduty-production-ai-agent-gaps.md`
  Claim 14 — it represents a deliberate *design choice* for non-critical guardrails
  (optimization) rather than a different claim about guardrail architecture. No
  contradiction issue filed.

## Guide Impact

- **Chapter 04 (Guardrails / Proxy Patterns)**: Add the **sidecar guardrail architecture**
  pattern as a distinct deployment model. Specific additions:
  - The `pre_call` hook mechanism for guardrails that run before the LLM call — as a
    generic pattern supported by LiteLLM and applicable to any proxy that supports
    pre/post-call hooks. Differentiate from in-process middleware (covered by
    `blog-litellm-fastapi-middleware-performance.md`) and application-layer guardrails
    (covered by `docs-langfuse-security-and-guardrails.md`).
  - The **fail-open design consideration**: non-critical guardrails (compression,
    enrichment) should fail open; critical guardrails (auth, rate limiting, content
    filtering) should fail closed. The Headroom sidecar exemplifies this tradeoff.
  - The **admin-to-developer key handoff pattern** as a recommended rollout strategy:
    admin attaches guardrails to virtual keys, developers consume transparently via
    environment variables, with per-request bypass headers for exceptions.
  - The **config granularity model** (per-key, per-request, global `default_on: true`)
    as a generic pattern for proxy-level feature flags.
  - The **verification pattern** (`x-litellm-applied-guardrails` response header) as
    recommended practice for confirming guardrail execution — analogous to the traced
    `@observe()` decorators from `docs-langfuse-security-and-guardrails.md` but at the
    HTTP-header level rather than the SDK level.

- **Chapter 05 (LLM Ops Reliability — cost optimization)**: Add prompt compression as
  a **cost optimization pattern** distinct from prompt caching, model selection, and
  batching. Specific additions:
  - The **sidecar compression deployment model** as a zero-client-change optimization:
    the LLM ops team deploys Headroom as a sidecar, configures which teams/keys get
    compression, and all traffic through those keys is automatically compressed.
  - The **token-reduction claim** (60-95%) with a strong caveat: this is a vendor claim
    without independent benchmarking. Cite the range as a directional indicator, not a
    validated figure. Reference this note's Claim 4 (Our assessment) for the caveat.
  - The **dual default behavior** warning: Headroom does NOT compress `user`/`system`
    messages by default (needs `HEADROOM_COMPRESS_USER_MESSAGES=1`). Teams deploying
    Headroom should verify their traffic roles and set this env var if needed. The
    `cache_control` protection is a positive feature (caching and compression are
    compatible), but the guide should explain why this matters.

- **Chapter 06 (Deployment Architecture — sidecar pattern)**: Add the **compression
  sidecar** as a reference pattern for gateway-adjacent services. Specific additions:
  - The **sidecar service model**: Headroom runs as a separate container/pod, called
    by LiteLLM during the `pre_call` hook, outside the gateway process. The compression
    service can be scaled, deployed, and updated independently of the gateway.
  - The **fail-open vs fail-closed axis** as a deployment decision: the compression
    sidecar demonstrates a fail-open service (safe to degrade). Contrast with patching
    sidecars or auth services that must fail closed.
  - The **dual-format support** requirement for sidecar services: if a sidecar supports
    both OpenAI and Anthropic formats, clients on either API format can use it without
    migration. This is a design consideration for any proxy-level middleware.
  - The **Dockerfile** from the setup guide (see Concrete Artifacts) as a starting
    template for teams building or deploying compression sidecars.

## Extraction Notes

- Primary source: blog post at https://docs.litellm.ai/blog/headroom-integration,
  published June 30, 2026. The companion setup guide at
  https://docs.litellm.ai/docs/proxy/headroom was read end-to-end for configuration
  details, code examples, and operational caveats (user message and cache_control
  protection defaults). The GitHub discussion at
  https://github.com/BerriAI/litellm/discussions/31816 was read for user-reported
  issues and maintainer responses.
- The blog post is thin — it is approximately 300 words with no code examples, metrics
  methodology, or independent evidence. Most of the concrete artifacts and operational
  detail came from the setup guide (docs page) and the GitHub discussion. Without these
  companion sources, this source would yield only 3-4 claims. The Prospector's `low`
  novelty assessment is accurate: the architectural pattern (sidecar guardrail with
  fail-open) is the primary value, not the token-reduction claim.
- `confidence_overall` is `emerging` following the precedent of other LiteLLM blog notes
  (e.g., `blog-litellm-fastapi-middleware-performance.md` uses `emerging`). The
  architectural and config claims (Claims 1, 3, 6, 7, 8) are settled LiteLLM product
  behavior. The token-reduction claim (Claim 4) is anecdotal vendor marketing. The
  reliability claim (Claim 2) is stated but unsupported. The user-reported issues
  (Claim 9) are settled evidence from the public discussion.
- Quotes marked as direct in this note were extracted from the rendered page text via
  WebFetch. The WebFetch tool enforces a 125-character single-quote limit, so multi-part
  quotes separated by "— and —" are adjacent fragments from the same page section. The
  Assayer should spot-check key quotes against
  https://docs.litellm.ai/blog/headroom-integration for character-for-character accuracy.
- No contradiction issue filed: verified against all existing source notes. No existing
  note covers prompt compression, the sidecar guardrail pattern, the Headroom integration,
  or any claim that this source opposes. The fail-open design (Claim 2) is a design choice
  for non-critical guardrails, not a contradiction with the sync/async classification in
  `blog-pagerduty-production-ai-agent-gaps.md`.
