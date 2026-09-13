---
source_url: https://docs.litellm.ai/docs/a2a
source_type: docs
title: "Agent Gateway (A2A Protocol) - Overview — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-13)
date_extracted: 2026-09-13
last_checked: 2026-09-13
status: current
confidence_overall: emerging
issue: "#1302"
---

# Agent Gateway (A2A Protocol) - Overview (LiteLLM Docs)

> The operational contract for invoking (not just routing to) agents through an
> LLM gateway: LiteLLM's Agent Gateway registers A2A-protocol agents across six
> runtimes, normalizes the wire format, and governs them with per-agent
> authorization and trace-ID enforcement — but trace grouping, per-agent spend
> attribution, and identity propagation only work if the *agent server forwards
> gateway-set headers back* on its own LLM calls, and most JSON-RPC methods
> bypass the gateway's client path entirely.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living
  page under the "Agent & MCP Gateway" nav section, sibling to the A2A Agent
  Card / Invoking / Authentication Headers / Cost Tracking / Permission
  Management / Iteration Budgets pages).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Claims about the surface LiteLLM exposes (headers, endpoints, error codes,
  config keys, registration behavior) are authoritative for that surface, but
  the page documents *capability*, not demonstrated reliability: no measured
  overhead, no failure-mode writeups, no production experience report. Per the
  Prospector's scope rule, everything in this note stays at "the gateway
  exposes this surface," never "this works at scale."
- **Scope**: Covers registering agents (Admin UI, `POST /v1/agents`, `config.yaml`
  `agents:` key), protocol versioning (0.3 vs 1.0 wire formats and the unpinned
  inference matrix), trace/spend header propagation across the agent hop, the
  A2A JSON-RPC API surface, authentication + per-agent authorization, trace-ID
  enforcement, and the agent registry with semantic search. Sibling pages
  already under the same A2A nav section (Agent Card, Invoking, Authentication
  Headers, Cost Tracking, Permissions, Iteration Budgets) are being filed from
  the same crawl batch; this note extracts only what the overview page itself
  asserts and does not duplicate the sub-pages.

## Extracted Claims

### Claim 1: LiteLLM's Agent Gateway registers and invokes A2A-protocol agents through the gateway with logging, load balancing, streaming, and iteration budgets, across A2A, Vertex AI Agent Engine, LangGraph, Azure AI Foundry, Bedrock AgentCore, and Pydantic AI
- **Evidence**: The page's feature table lists the six supported agent providers
  and four supported features (Logging, Load Balancing, Streaming, Iteration
  Budgets); the intro states the gateway "tracks request/response logs in
  LiteLLM Logs" and manages "which Teams, Keys can access which Agents." The
  body then walks registration per provider.
- **Confidence**: emerging (vendor capability surface; no production metrics or
  failure analysis on the page)
- **Quote**: "LiteLLM follows the A2A (Agent-to-Agent) Protocol for invoking agents."
- **Our assessment**: This is the concrete, shipping implementation surface the
  control-plane vision post described as an open gap — a gateway that *invokes*
  (not just lists) agents across multiple runtimes through one protocol. But it
  is the same vendor (`blog-litellm-agents-are-the-new-llms.md` is LiteLLM's own
  vision post) and it is capability, not demonstrated reliability, so it narrows
  rather than refutes the guide's "unsolved" framing — see Cross-References.

### Claim 2: Trace grouping and per-agent spend attribution are a forwarding obligation, not a gateway guarantee — when LiteLLM invokes an A2A agent it sets `X-LiteLLM-Trace-Id` and `X-LiteLLM-Agent-Id`, but grouping and attribution only materialize if the agent server forwards those headers on its own calls back to LiteLLM
- **Evidence**: The "Forwarding LiteLLM Context Headers" section defines the two
  headers (trace grouping; agent spend tracking), then states the forwarding
  requirement explicitly and provides four client-side implementations
  (OpenAI SDK `default_headers`, LangChain `default_headers`, LiteLLM
  `extra_headers`, httpx) alongside a `get_litellm_headers(request)` helper that
  filters `x-litellm-*` from the incoming A2A request.
- **Confidence**: emerging (documented contract; the failure mode — silent loss
  of trace grouping and agent-level cost attribution when the server does not
  forward — follows from the imperative but is not demonstrated on the page)
- **Quote**: "To enable these features, your A2A server must forward these headers to any LLM calls it makes back to LiteLLM."
- **Our assessment**: This is the highest-value extraction on the page: a
  "looks fine, fails silently" observability contract at a trust boundary. The
  gateway sets the correlation/spend ids on the way in; nothing guarantees they
  continue on the way out. An operator who wires the A2A gateway and does not
  audit the agent server for header forwarding gets no agent-level trace
  grouping and no per-agent cost attribution — with no error. It is the agent-hop
  counterpart of the manual session-correlation rule already in the corpus
  (Helicone `Helicone-Session-Id`, OTel conversation id) and the per-model cost
  attribution blind spot (the model-cost-map incident). See Cross-References.

### Claim 3: The caller's virtual key and end-user ID are not propagated to the backend agent / sub-agents — identity re-propagation is a manual, explicit obligation via `extra_headers` or the `x-a2a-{agent_name_or_id}-{header}` convention
- **Evidence**: The "Sub-agent identity propagation" paragraph states that
  LiteLLM forwards the trace/agent headers to the backend agent but that the
  caller's virtual key and end-user ID are deliberately not forwarded, pointing
  to the convention-based header forwarding mechanism on the sibling auth-headers
  page.
- **Confidence**: emerging (documented behavior; the auth-headers page confirms
  the `x-a2a-{agent_name_or_id}-{header}` convention and that static headers
  win over client-forwarded ones)
- **Quote**: "The caller's **virtual key** and **end-user ID** are not automatically forwarded. If the downstream agent needs the user's identity, propagate it explicitly via `extra_headers` or the `x-a2a-{agent_name_or_id}-{header}` convention."
- **Our assessment**: Security/audit consequence: end-user attribution silently
  degrades across an agent hop unless the client or an intermediate layer
  deliberately threads it. The `x-a2a-{agent_name_or_id}-{header}` convention is
  a per-agent namespace, which limits cross-agent header leakage, and admin
  `static_headers` always win over client-controlled values — but identity
  continuity remains wholly manual.

### Claim 4: Protocol-version pinning is a footgun — the proxied agent card defaults to 1.0 when `protocolVersion` is unset, but legacy `message/send` callers without an `a2a-version` header receive 0.3-shaped responses, so card and responses can disagree; only "0.3" and "1.0" are accepted (HTTP 400 at registration), and the unpinned served version is inferred from client signals
- **Evidence**: The "Pinning a version" and "When `protocolVersion` is not
  pinned" sections: only `"0.3"` and `"1.0"` accepted, other values rejected
  HTTP 400 at registration; when unpinned, `SendMessage`/`SendStreamingMessage`
  method or `a2a-version: 1.x` header → 1.0, otherwise (e.g. `message/send` with
  no header) → 0.3; plus the "Always pin `protocolVersion`" callout.
- **Confidence**: emerging (documented vendor behavior; the card/default
  mismatch is stated explicitly)
- **Quote**: "The proxied agent card defaults to `1.0` when unset, but legacy `message/send` callers without an `a2a-version` header receive **0.3**-shaped responses. Pin `protocolVersion` explicitly so your card and responses always match."
- **Quote**: "Only `"0.3"` and `"1.0"` are accepted; other values return HTTP 400 at registration."
- **Our assessment**: A concrete version-negotiation hazard unique to gateways
  that proxy agent protocols: two artifacts (the served card and the served
  responses) can disagree depending on the client's signals. The 0.3 vs 1.0 wire
  shapes differ structurally (kind-discriminated objects vs protobuf JSON
  envelopes), so a card/client that assumes one shape can silently misinterpret
  the other. Cheap to avoid (pin it), silent when you don't — a good deploy-time
  checklist item.

### Claim 5: Declarative agents defined in `config.yaml` have different behavior from DB agents — they require both `agent_name` and `agent_card_params` or are silently skipped at startup, are not stored in the database (so not editable/deletable in the Admin UI), survive the periodic DB reload, and lose name collisions to a same-named DB record; pre-`v1.95.0` they are read via `agent_list` and are dropped entirely on DB-attached gateways
- **Evidence**: The "Define agents in config.yaml" subsection + version note.
  States both fields required ("entries missing either one are skipped at
  startup"), config agents show up in the UI/`GET /v1/agents`, survive the
  periodic reload, are not DB-stored, a UI-created agent with the same name wins
  and the config entry is dropped (reclaims the name after the DB record is
  deleted), and the `agents` key is read correctly only after `v1.95.0`
  (earlier: `agent_list`, and config-defined agents are dropped on
  DB-attached gateways).
- **Confidence**: emerging (documented vendor behavior with an explicit version
  cutoff)
- **Quote**: "The `agents` key is read correctly starting in the next release (after `v1.95.0`). On earlier versions, use `agent_list`, and note that config-defined agents are dropped on gateways that have a database attached."
- **Our assessment**: The "declarative config on a read-only ConfigMap" pattern
  with sharp edges. Three silent-failure characteristics: entries missing a
  field are skipped at startup (no error), config entries silently lose name
  collisions to DB records (canonical source is ambiguous — config says one
  thing, runtime resolves the DB record), and the field name itself changed
  (`agent_list` → `agents`) so a config written against an older version is
  silently misread. Operationally: verify config-defined agents after upgrade
  and treat config and DB as two sources of truth with rigid precedence, not a
  merged view.

### Claim 6: Only `message/send` and `message/stream` traverse the gateway's A2A client path (logging, guardrails, spend) — all other JSON-RPC methods (`tasks/get`, `tasks/list`, `tasks/cancel`, push-notification config, `agent/getAuthenticatedExtendedCard`) are forwarded to the upstream agent URL unchanged, so task and monitoring APIs bypass gateway controls
- **Evidence**: The "Routing:" note under "Supported JSON-RPC methods" and the
  sibling agent-card page's per-method table (task methods "forwarded to
  upstream"; `message/send`/`message/stream` through the A2A SDK/streaming
  handler). The overview also notes task APIs require the upstream URL; task
  method `params` are forwarded as-is.
- **Confidence**: emerging (documented routing rule)
- **Quote**: "**Routing:** `message/send` and `message/stream` go through LiteLLM's A2A client (logging, guardrails, spend). All other methods are forwarded to the upstream URL in `agent_card_params.url`."
- **Our assessment**: A real governance gap in the "govern" verb: the methods
  that observe and control long-running agent work (`tasks/get`, `tasks/list`,
  `tasks/cancel`, push-notification config) bypass the gateway's logging,
  guardrails, and spend tracking entirely. An operator who assumes "the gateway
  governs everything an agent does" will find no log entries, no pre-call
  guardrails, and no cost rows for task-polling and cancellation traffic.
  Consequences for guide design: model the gateway's control surface per-method,
  not per-agent.

### Claim 7: Per-agent authorization is a separate check after virtual-key authentication — key/team permission intersection → HTTP 403; optional per-agent trace-ID enforcement rejects requests missing trace or session IDs with HTTP 400 (inbound and outbound variants)
- **Evidence**: The "Per-agent permission check" section ("After the virtual key
  is authenticated, LiteLLM checks whether the calling key (and its team) is
  allowed to invoke the requested agent. If not, the response is HTTP 403") and
  the "Trace ID enforcement" section — `require_trace_id_on_calls_to_agent: true`
  in `litellm_params` rejects requests missing `x-litellm-trace-id` (or
  `x-litellm-session-id`) with HTTP 400; the outbound mirror
  `require_trace_id_on_calls_by_agent` controls calls made by a key owned by an
  agent.
- **Confidence**: emerging (documented, with a concrete registration curl)
- **Quote**: "After the virtual key is authenticated, LiteLLM checks whether the calling key (and its team) is allowed to invoke the requested agent. If not, the response is HTTP 403."
- **Our assessment**: The two levers that make the gateway's governance
  concrete rather than aspirational: per-agent/per-key/team access scoping and a
  mandatory-trace-ID knob for cross-system audit threading. The key/team scope
  intersection is the same authorization model as the LLM proxy (virtual keys +
  teams), now applied per *agent*. Worth checking whether iteration budgets and
  admin-defined static credentials (headers-page sibling) compose with the
  per-key limits — the page does not show interactions.

### Claim 8: The agent registry supports semantic search over `GET /v1/agents?query=` — cosine-similarity ranking subject to configuration and visibility constraints: requires `agent_search_embedding_model` else HTTP 400 `agent_search_not_configured`; embedding failure → HTTP 503 `agent_search_unavailable`; results always scoped to the key's visible agents; `top_k` defaults to 5 and caps at 100; embeddings are computed once per process and reused until the agent card changes
- **Evidence**: "Search the registry" section: config example wiring
  `litellm_settings.agent_search_embedding_model`, a ranked curl response with
  `search_score`, and the error/behavior sentences.
- **Confidence**: emerging (documented with explicit error codes and a config
  requirement)
- **Quote**: "Without `agent_search_embedding_model` a `query` returns `400 agent_search_not_configured`; if the embedding call fails, the request returns `503 agent_search_unavailable`."
- **Quote**: "Ranking only ever covers agents the key is allowed to see, so a key restricted to two agents gets those two back whatever the query."
- **Our assessment**: Two operational facts: (a) semantic search is a *new
  configurable dependency* — if you enable registry search you inherit an
  embedding provider, and misconfiguring it produces two distinct, documented
  failure codes (400 not-configured vs 503 embedding unavailable); (b) search
  correctness is bounded by the key's visibility scope, so "top_k ranked agents"
  is really "top_k among what this key may already see" — the API widens no
  access. `top_k` default 5 / cap 100 and process-lifetime embedding caching are
  concrete tuning inputs.

### Claim 9: Agent-call authentication accepts the virtual key via `Authorization: Bearer` or `x-litellm-api-key`, with the latter preferred when the inbound `Authorization` header may carry a token destined for the backend agent; backend-agent credentials can be static, client-forwarded, or convention-based, and static headers always win on conflicts
- **Evidence**: The "Authentication" section names both headers and the
  preference rule; the sibling Authentication Headers page details the three
  backend-credential methods and the merge precedence ("static headers always
  win"), plus per-agent header isolation (headers for agent A are never sent to
  agent B).
- **Confidence**: emerging (documented; the auth-headers sibling page confirms
  the three methods and precedence)
- **Quote**: "`x-litellm-api-key` is preferred when the inbound `Authorization` header may carry a token destined for the backend agent"
- **Our assessment**: The `Authorization`-vs-`x-litellm-api-key` split matters
  operationally: if you use `Authorization` for both the gateway and the backend
  agent you create a header ambiguity the docs resolve by telling you to use
  `x-litellm-api-key` for the gateway. The static-headers-win rule means
  admin-controlled backend credentials cannot be overridden by clients — a
  sensible security property, but it also means the admin credential path is a
  place to store secrets, and the sibling page warns to treat `static_headers`
  as credentials (avoid long-lived tokens in the API/database).

## Concrete Artifacts

### Supported agent providers (from the feature table, verbatim)

```
Supported Agent Providers: A2A, Vertex AI Agent Engine, LangGraph,
Azure AI Foundry, Bedrock AgentCore, Pydantic AI
Features: Logging ✅, Load Balancing ✅, Streaming ✅, Iteration Budgets ✅
```

### Declarative agent registration in config.yaml (from "Define agents in config.yaml", verbatim)

```yaml
agents:
  - agent_name: my-agent
    agent_card_params:
      name: "My Agent"
      url: "http://localhost:10001"
      protocolVersion: "1.0"  # or "0.3"
```

Verify with: `curl -s http://localhost:4000/v1/agents -H "Authorization: Bearer $LITELLM_MASTER_KEY"`

### Header extraction + forwarding helper (from "Forwarding LiteLLM Context Headers", verbatim)

```python
def get_litellm_headers(request) -> dict:
    """Extract X-LiteLLM-* headers from incoming A2A request."""
    all_headers = request.call_context.state.get('headers', {})
    return {
        k: v for k, v in all_headers.items()
        if k.lower().startswith('x-litellm-')
    }
```

Forwarded on the agent's own LLM calls via `default_headers` (OpenAI SDK) or
`extra_headers` (LiteLLM SDK / httpx):

```python
from openai import OpenAI
headers = get_litellm_headers(request)
client = OpenAI(
    api_key="sk-your-litellm-key",
    base_url="http://localhost:4000",
    default_headers=headers,  # Forward headers
)
response = client.chat.completions.create(
    model="gpt-5.6-terra",
    messages=[{"role": "user", "content": "Hello"}]
)
```

The two headers, from the page's table (verbatim):

```
Header: X-LiteLLM-Trace-Id      Purpose: Links all LLM calls to the same execution flow
Header: X-LiteLLM-Agent-Id      Purpose: Attributes spend to the correct agent
```

### Protocol-version inference when `protocolVersion` is not pinned (from "When `protocolVersion` is not pinned", verbatim)

```
Client signal                                           Served version
JSON-RPC method SendMessage or SendStreamingMessage    -> 1.0
Request header a2a-version: 1.x                        -> 1.0
Otherwise (e.g. message/send with no header)           -> 0.3
```

Wire-shape table (verbatim): 0.3 = "Objects discriminated by `kind` (`message`,
`task`, `status-update`, …)"; 1.0 = "Protobuf JSON envelopes (`message`, `task`,
`statusUpdate`, `artifactUpdate`)".

### Trace-ID enforcement registration (from "Trace ID enforcement", verbatim)

```
curl -X POST http://localhost:4000/v1/agents \
  -H "Authorization: Bearer sk-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "audit-critical-agent",
    "agent_card_params": { ... },
    "litellm_params": {
      "require_trace_id_on_calls_to_agent": true
    }
  }'
```

Outbound mirror: `require_trace_id_on_calls_by_agent` on the same
`litellm_params` block.

### Registry search wiring (from "Search the registry", verbatim)

```yaml
model_list:
  - model_name: text-embedding-3-small
    litellm_params:
      model: openai/text-embedding-3-small
      api_key: os.environ/OPENAI_API_KEY
litellm_settings:
  agent_search_embedding_model: text-embedding-3-small
```

Ranked call: `curl -s "http://localhost:4000/v1/agents?query=translate+a+pdf+document&top_k=3"` —
each result is the normal agent object plus `search_score` ("cosine similarity,
higher is better"). `top_k` defaults to 5 and caps at 100. Also surfaced to MCP
clients as an `agent_search(query, top_k)` virtual tool when `mcp_tool_search_enabled:
true` on the key's `object_permission`.

### Primary endpoint (from the API Reference table, verbatim)

```
POST /a2a/{agent_id}        JSON-RPC 2.0   Primary — all A2A methods
POST /a2a/{agent_id}/message/send                       Alias for message/send only
POST /v1/a2a/{agent_id}/message/send                    Alias for message/send only
GET  /a2a/{agent_id}/.well-known/agent.json             Agent card (proxy URL in url field)
GET  /a2a/{agent_id}/.well-known/agent-card.json        Agent card (standard path)
```

`{agent_id}` may be the agent UUID or the registered agent name. Methods:
`message/send`, `message/stream`, `tasks/get|list|cancel|resubscribe`,
`tasks/pushNotificationConfig/set|get|list|delete`,
`agent/getAuthenticatedExtendedCard`. Requires `a2a-sdk >= 1.1.0` on the proxy
("LiteLLM proxy A2A routes require **a2a-sdk >= 1.1.0**").

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guards, pre-on-caller, golden-label eval for SRE
  agents; no agent-gateway / A2A / wire-format content.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors and debuggability; not agent invocation.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP /
  coding-agent integration topic; unrelated to agent-gateway governance.
- `source-notes/docs-litellm-helicone-integration.md` — **cited** (Corroborates,
  Claim 2 below).
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization; unrelated to agent proxy surfaces.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  model/LLM guardrail scanner stacks; no per-agent authorization or proxy
  surfaces.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **dismissed**: budget
  windows/caching on the model path. Its MCP Tool Search virtual-tool pattern
  (`mcp_tool_search`/`mcp_tool_call`) is structurally parallel to this page's
  `agent_search` MCP virtual tool, but the mechanism differs (token-overlap
  ranking for tools vs cosine-similarity ranking for agents) and the topics
  (cost control vs agent registry) do not overlap.
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **dismissed**:
  embedding-based response-cache backends; unrelated to agent search/ranking.
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **dismissed**:
  pipeline freshness/correctness SLOs; unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch coordination/checklists; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-helicone-integration.md` **Claim 2** (Helicone
    session correlation is a manual per-request application-context layer —
    `Helicone-Session-Id`/`Helicone-Session-Path` set by the caller on every
    request, "nothing auto-propagates them"). The A2A page's `X-LiteLLM-Trace-Id`
    forwarding obligation (this note Claim 2) is the same rule at the *agent-hop*
    boundary: the gateway hands you a correlation id but the continuity depends
    on code you control re-sending it. Same "application context is manual"
    principle, concrete in a second vendor surface.
  - `source-notes/blog-pagerduty-production-ai-agent-gaps.md` **Claim 4** ("The
    article notes this intensifies in multi-agent systems as protocols like
    DNS-AID and A2A make integration easier"). The LiteLLM page is the gateway
    implementation of that enabler — and the page's routing split (this note
    Claim 6) is exactly the kind of compounding-integration surface that makes
    low-return paths like `tasks/*` silently bypass governance.
- **Contradicts**: None filed as a contradiction issue. The one surface-level
  tension is the guide's current "the cross-runtime agent API layer is explicitly
  unsolved" framing (guide `03-runbooks-and-agents.md` §"The emerging agent
  control plane" and `05-llm-ops-reliability.md` §"The gateway is shifting from
  routing model calls to governing agent sessions", both citing
  `source-notes/blog-litellm-agents-are-the-new-llms.md` Claim 8 "one API across
  agent runtimes … open gap"). This page documents a shipping gateway that maps
  onto the four control-plane verbs (register via UI/API/config; invoke via
  A2A JSON-RPC with version normalization; observe via per-agent logs; govern via
  per-agent auth → 403 and trace-ID enforcement → 400) across six runtimes. That
  is a real *narrowing* of the "unsolved" claim, not a refutation: it is the same
  vendor (LiteLLM's own vision post), it covers only the A2A-protocol family
  (non-A2A runtimes and the full lifecycle/scheduling/memory scope remain open),
  and the page demonstrates capability, not reliability at scale. Per MINER §4a
  this is a vendor-consistency / temporal nuance, not a claim-level opposition
  between two live positions — no contradiction issue filed.
- **Extends**:
  - `source-notes/blog-litellm-agents-are-the-new-llms.md` — that vision post's
    Claims 3 (a registry is insufficient; "The harder problem is invocation"),
    4 (four verbs: register/invoke/observe/govern), and 9 (LAP "register, invoke,
    observe, and govern agents across multiple runtimes") are given a concrete,
    shipping instantiation here — but in the mainline LiteLLM proxy A2A gateway,
    not LAP, so the Control-Plane thesis gains implementation evidence while its
    "open gap" framing (Claim 8) is narrowed (see Contradicts).
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — that note
    documents silent loss of *per-model* cost tracking via a stale cost map. This
    page adds a second, orthogonal cost-attribution axis: *per-agent* spend
    attribution via `X-LiteLLM-Agent-Id`, which also fails silently unless the
    backend agent forwards the header. Both are "cost attribution degrades
    without an error" failure classes in the same vendor's gateway.
  - `source-notes/docs-litellm-streaming-token-usage.md` — model-path streaming
    usage accounting (opt-in `include_usage`, final-chunk semantics). The A2A
    page's `message/stream` is the agent-path streaming counterpart (NDJSON/SSE),
    and both pages document that stepping off the happy path silently yields
    absent accounting data on the *model* path and absent grouping/attribution on
    the *agent* path.
- **Novel**: First source note in the corpus to cover LiteLLM's A2A / agent-gateway
  surface: agent registration paths (UI / API / `config.yaml` `agents:` key with
  the drop/collision semantics), agent cards and wire-format normalization (0.3
  vs 1.0 and the unpinned inference matrix), the `X-LiteLLM-Trace-Id` /
  `X-LiteLLM-Agent-Id` cross-hop forwarding contract, per-agent authorization
  (403) and trace-ID enforcement (400), the `message/*`-vs-everything-else
  routing split, and registry semantic search error codes
  (`agent_search_not_configured` 400 / `agent_search_unavailable` 503). The
  multi-runtime agent invocation list (A2A, Vertex, LangGraph, Azure AI Foundry,
  Bedrock AgentCore, Pydantic AI) is also new to the corpus.

## Guide Impact

- **Chapter 03 (Runbooks and Agents)** — §"The emerging agent control plane":
  This page is the strongest concrete counter-signal to the chapter's current
  "the cross-runtime agent API layer is explicitly unsolved … plan for
  fragmentation, not turnkey unification" rule (citing
  `blog-litellm-agents-are-the-new-llms` Claim 8). Recommend rebalancing that
  rule: within the A2A-protocol family, a shipping gateway now maps all four
  control-plane verbs (register / invoke / observe / govern) with concrete
  semantics — but with three sharp edges the chapter should name: (1) pin
  `protocolVersion` or card and responses can disagree (Claim 4); (2) config
  `agents:` entries silently skip/drop on version and DB collisions (Claim 5);
  (3) `tasks/*` and push-notification methods bypass the gateway's client path
  (Claim 6). Add the routing-split as an example of per-method gateway controls.

- **Chapter 02 (Observability)** — cross-hop trace continuity: Add the
  `X-LiteLLM-Trace-Id` / `X-LiteLLM-Agent-Id` forwarding obligation (Claim 2) as
  a concrete instance of the "application context is manual" rule and of
  "observability silently degrades across a trust boundary": when an agent hop
  (gateway → agent server → agent's own LLM calls) is in the path, trace grouping
  and attribution depend on the agent server re-forwarding gateway-set headers —
  audit each agent for header forwarding or lose agent-level grouping and cost
  attribution with no error signal. Cite alongside the Helicone manual-session
  rule.

- **Chapter 05 (LLM Ops Reliability)** — cost/capacity: Add *per-agent* spend
  attribution as a second cost-attribution axis beside the per-model cost map
  (`failure-litellm-model-cost-map-silent-fallback`): the gateway sets
  `X-LiteLLM-Agent-Id`, but per-agent cost rows only exist if the backend agent
  forwards it. Also add the governance-gap check: because most JSON-RPC methods
  (task polling, push-notification config) are forwarded unchanged, gateway
  logging/spend rows will miss agent-task traffic — verify per-method.

- **Chapter 06 (Security and Trust)** — per-agent authorization surface: Add
  key/team-permission intersection → HTTP 403 and the optional
  `require_trace_id_on_calls_to_agent` / `require_trace_id_on_calls_by_agent`
  enforcement → HTTP 400 (Claim 7) as concrete levers for per-agent access scoping
  and audit-thread enforcement; note that end-user identity is deliberately not
  propagated across the hop unless threaded manually (Claim 3). 

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/a2a`, HTTP 200, no paywall). Two substantive
  linked sub-pages were followed per MINER §1 to verify the overview's claims:
  `docs/a2a_agent_headers` (backend-credential methods, merge precedence,
  per-agent isolation — used for Claims 3 and 9) and `docs/a2a_agent_card`
  (per-method routing table, task-method forwarding — used for Claims 4 and 6).
  All `Quote` fields are character-for-character from the fetched overview page;
  code-block artifacts preserve the page's call shapes.
- Triage bounding honored (#1302, `priority:medium`): the extraction prioritizes
  the two "looks fine, fails silently" contracts the Prospector flagged —
  trace/spend identity propagation (Claim 2, Claim 3) and declarative
  config-vs-DB precedence (Claim 5) — plus the protocol-version footgun (Claim
  4), the routing split (Claim 6), and the error-code/auth surface (Claims 7-9).
  The endpoint/method tables are preserved as concrete artifacts that the guide
  can cite rather than reproduce (per Prospector guidance).
- Confidence is `emerging`: the page documents vendor *capability* with explicit
  config keys, headers, and error codes, but demonstrates no measured overhead,
  no failure modes, and no production experience — this note never asserts
  reliability. The `blog-litellm-agents-are-the-new-llms.md` vision post remains
  the guide's directional source; this page is the implementation surface under
  its Claims 3/4/9.
- No contradiction issue filed. The narrowing relationship with the guide's
  "explicitly unsolved" rule (and `blog-litellm-agents-are-the-new-llms.md` Claim
  8) is a same-vendor consistency data point and a temporal/capability nuance,
  not a live claim-level opposition — see the Contradicts section. Verified
  `CONTRADICTIONS.md` (no entries) and open `contradiction`-labeled issues
  (#1150 routing flavors, #1307 promptfoo trace assertions) — neither covers A2A
  or agent-gateway surfaces; a duplicate contradiction is not already filed.
- `date_published` is unknown (living Docusaurus docs page); `date_extracted`
  and `last_checked` are both 2026-09-13. The page references `v1.95.0` as the
  cutoff for the `agents` config key, so the content is post-2026-09.
- Sibling A2A pages (Agent Card, Invoking, Authentication Headers, Cost
  Tracking, Permissions, Iteration Budgets) are being filed from the same crawl
  batch; this note does not preempt them — any overlap flagged here is only what
  the overview page itself states.