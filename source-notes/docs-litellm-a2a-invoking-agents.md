---
source_url: https://docs.litellm.ai/docs/a2a_invoking_agents
source_type: docs
title: "Invoking A2A Agents — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-16)
date_extracted: 2026-09-16
last_checked: 2026-09-16
status: current
confidence_overall: emerging
issue: "#1330"
---

# Invoking A2A Agents (LiteLLM Docs)

> The same registered A2A agent is reachable through **two client-facing
> invocation paths**: native A2A JSON-RPC via the a2a-sdk (`>= 1.1.0, < 2.0`)
> and an OpenAI-compatible `POST /v1/chat/completions` bridge selected by an
> `a2a/` model prefix (`model: "a2a/my-agent"`) — the OpenAI bridge collapses a
> task-shaped agent into a single `chat.completions` round-trip (task state,
> artifacts, and context management structurally unavailable), and the page is
> silent on whether that bridge inherits the gateway's logging, spend, and
> guardrail controls.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living
  page under the "Agent & MCP Gateway > A2A Agent Gateway" nav section, sibling
  to the A2A Agent Gateway overview, Agent Card, Authentication Headers, Cost
  Tracking, Permission Management, and Iteration Budgets pages).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Claims about the invocation surfaces LiteLLM exposes (endpoints, code shapes,
  protocol-version guidance) are authoritative for the *documented surface*,
  but the page demonstrates capability only — no measured overhead, no
  failure-mode writeups, no production experience report. Per the Prospector's
  bounding, every claim in this note stays at "the gateway exposes this
  invocation path," never "this works at scale."
- **Scope**: A client-perspective "how to invoke" guide covering (1) the A2A
  Python SDK 1.x path (card discovery → `ClientFactory` → `send_message`),
  (2) the `/chat/completions` OpenAI-SDK path via the `a2a/` model prefix,
  (3) task polling via `tasks/get`, and (4) a brief protocol-version pinning
  note. It does **not** cover headers/credentials (sibling auth pages), agent
  registration, permission resolution (sibling #1317), or the enterprise footer
  (marketing — excluded per bounding).

## Extracted Claims

### Claim 1: A2A agents registered with LiteLLM are invocable through the OpenAI-compatible `POST /v1/chat/completions` surface by prefixing the agent name with `a2a/` — `model: "a2a/my-agent"` — from Python, TypeScript, and cURL clients, streaming and non-streaming
- **Evidence**: The "/chat/completions API (OpenAI SDK)" section ships three
  language examples (Python, TypeScript, cURL), each passing
  `model: "a2a/my-agent"`; the "Model Prefix" section states the rule
  explicitly. Verbatim examples preserved in Concrete Artifacts.
- **Confidence**: emerging (vendor capability surface; no reliability claims)
- **Quote**: "You can also invoke A2A agents using the familiar OpenAI SDK by using the `a2a/` model prefix."
- **Our assessment**: This is the genuinely new invocation surface for this
  corpus: the gateway's JSON-RPC endpoint table (overview note #1302, Concrete
  Artifacts → Primary endpoint) does not list any `a2a/`-prefixed OpenAI
  completion path, and no existing source note documents it. Operationally it
  means *any* OpenAI-SDK tooling can call an agent without an A2A client — but
  that same drop-in-ness is what makes the instrumentation question (Claim 3)
  matter.

### Claim 2: The OpenAI bridge collapses a task-shaped agent into a single `chat.completions` round-trip whose only result surface is `choices[0].message.content` — task state, artifacts, and context management are structurally unavailable on that path
- **Evidence**: Every OpenAI example reads the result only via
  `response.choices[0].message.content` (or `chunk.choices[0].delta.content`
  streaming); the page's own "Key Differences" table reserves "Access to task
  states and artifacts" and "Context management" for the A2A SDK path while the
  OpenAI path is framed as "Drop-in replacement for OpenAI calls."
- **Confidence**: emerging (documented API shape; the structural narrowing is
  the Miner's reading of that shape)
- **Quote**: "Access to task states and artifacts"
- **Quote**: "Works with existing OpenAI tooling"
- **Our assessment**: The reliability-relevant narrowing. An agent whose
  `message/send` returns a non-terminal `submitted` / `working` task (the
  polling pattern of Claim 8) has no place to put that state on the OpenAI path
  — the client gets a single content message, so task lifecycle, artifact
  retrieval, and context management are not expressible. Task-shaped agents
  must be invoked over the A2A SDK path; the `a2a/` bridge fits
  single-round-trip agents only. Guide runbooks should pick the invocation
  surface by task shape, not by client familiarity.

### Claim 3: The page documents no gateway-control semantics for the `a2a/` chat-completions bridge — it is silent on whether bridge calls are logged, spend-attributed, or guardrailed, and documents no error/timeout or non-terminal-state mapping for the path
- **Evidence**: Documented absence, not measurement: the page's only content on
  this path is the flat non-streaming/streaming examples, the "Key Differences"
  table, and the Model Prefix sentence. There is no statement about telemetry,
  spend, guardrails, virtual-key governance, per-agent permission checks, or
  what happens on timeout / on a `submitted` task result.
- **Confidence**: emerging (documented absence — treated as a gap, per triage)
- **Quote**: (no direct quote; the page has no sentence addressing gateway
  controls on this path — see Our assessment)
- **Our assessment**: Flagged as a gap rather than inferred to a resolution. The
  two plausibly-contradictory readings are (a) the bridge rides the ordinary
  `/v1/chat/completions` pipeline and inherits standard chat telemetry/spend/
  guardrails, or (b) it is a separate alias with different (possibly bypass)
  instrumentation — including the message-parameter-stripping oddity where
  pins for the version a client might expect to see are inferred client-side
  (overview note Claim 4). The page gives no basis to choose. A naive reader
  would assume governance parity between the two paths; that assumption is
  unverified, so the guide should treat the `a2a/` path's instrumentation as an
  open verification check, not a documented behavior.

### Claim 4: a2a-sdk 1.x is a breaking *client* change — `A2AClient` + dict `MessageSendParams` are replaced by `ClientFactory` + protobuf `Message`/`Part` types, and `send_message` becomes an async generator of stream events, with a matching client floor of `a2a-sdk>=1.1.0,<2.0`
- **Evidence**: The "Migration from a2a-sdk 0.3.x" callout states the migration
  contract explicitly; the install command pins
  `"a2a-sdk>=1.1.0,<2.0"`.
- **Confidence**: emerging (documented vendor migration contract)
- **Quote**: "a2a-sdk 1.x replaces `A2AClient` + dict `MessageSendParams` with `ClientFactory`, protobuf `Message` / `Part` types, and `send_message` as an async generator of stream events."
- **Our assessment**: This is the caller-side half of the overview note's
  server-side floor ("LiteLLM proxy A2A routes require **a2a-sdk >= 1.1.0**",
  #1302 Concrete Artifacts). The migration is not a drop-in: the object model
  changes (dict → protobuf), the entry point changes (`A2AClient` →
  `ClientFactory(config).create(agent_card)`), and the call shape changes
  (coroutine → `async for` over an async generator). An upgrade cannot be done
  gateway-side alone — client and gateway must move to compatible SDK lines
  together, which is upgrade-runbook material for Ch03/Ch05.

### Claim 5: The same `send_message` API serves streaming and non-streaming — selected by `ClientConfig(streaming=...)`, with clients declaring `supported_protocol_bindings: [JSONRPC, HTTP_JSON]` and discovering the card via `A2ACardResolver` at `{base}/a2a/{agent_id}`
- **Evidence**: The non-streaming example sets `streaming=False` and the
  streaming example sets `streaming=True` on otherwise identical
  `ClientConfig(...)` blocks; both pass
  `supported_protocol_bindings=[TransportProtocol.JSONRPC, TransportProtocol.HTTP_JSON]`.
- **Confidence**: emerging (documented API shape)
- **Quote**: "In a2a-sdk 1.x, set `streaming=True` on `ClientConfig` and iterate `send_message`. The same API handles streaming and non-streaming:"
- **Our assessment**: Streaming is a client-config toggle, not a distinct method
  — the example flow is identical (resolve card → create client → async-iterate
  `send_message`) in both modes. The `supported_protocol_bindings` field is
  present in every example, so it is effectively a required declaration for 1.x
  clients. Note that these are protobuf-structured events the client must
  decode via `event.ListFields()` — a client migrating from an HTTP-JSON
  (`kind`-discriminated, 0.3-style) response parser must change its event
  handling, not just its imports.

### Claim 6: The page restates the protocol-version pinning advice from the client side — pin `protocolVersion: "1.0"` on the agent so responses match the a2a-sdk 1.x wire format, or `"0.3"` for legacy callers
- **Evidence**: The sentence directly under the install command.
- **Confidence**: emerging (restatement of a documented rule; cross-referenced,
  not re-derived)
- **Quote**: "Pin `protocolVersion: \"1.0\"` on the agent (recommended) so responses match the 1.x SDK. For legacy `0.3` wire format, pin `\"0.3\"` instead."
- **Our assessment**: Contributes no new mechanism beyond the overview note's
  Claim 4 (unpinned inference footgun, only `0.3`/`1.0` accepted) and the
  agent-card note's Claim 10 (per-agent bidirectional conversion). What it adds
  is the client-side consequence stated as advice: a 1.x SDK client depends on
  the agent being pinned to `1.0`, otherwise it can receive `0.3`-shaped
  responses (the overview's headerless-legacy inference path). Pin-on-agent is
  the mitigation; nothing here extends the mechanism.

### Claim 7: The two invocation paths address the agent by different-looking identifiers — the OpenAI path uses the registered agent *name* (`a2a/my-agent`) while the SDK path uses the `{agent_id}` path segment — but both resolve the same registry entry, since `{agent_id}` accepts the UUID or the registered name
- **Evidence**: The Model Prefix sentence says to prefix "your agent name"; the
  non-streaming SDK example resolves `agent_id` from `GET /v1/agents`, while
  the streaming SDK example sets `LITELLM_AGENT_NAME = "ij-local"` (an agent
  *name*) and still builds `base_url = f"{LITELLM_BASE_URL}/a2a/{LITELLM_AGENT_NAME}"`.
- **Confidence**: emerging (both spellings demonstrated on the page; the
  same-key interpretation is confirmed by the overview note's endpoint table)
- **Quote**: "When using the OpenAI SDK, always prefix your agent name with `a2a/` (e.g., `a2a/my-agent`) to route requests to the A2A agent instead of an LLM provider."
- **Our assessment**: Not a real divergence — the overview note's endpoint
  table already states "{agent_id} may be the agent UUID or the registered
  agent name" (#1302 Concrete Artifacts), and this page's own streaming example
  passes a name in the `{agent_id}` slot. The `a2a/` prefix is the *name* keyed
  spelling of the same registry key. Residual misconfiguration risk is modest
  and concrete: the `a2a/` model string must exactly match the registered agent
  name, and the SDK path must match whichever id form was registered.

### Claim 8: Task-shaped agents require client-side polling — an agent that returns a `submitted` task from `message/send` expects the client to poll `tasks/get` against the same `{base}/a2a/{agent_id}` JSON-RPC URL, which LiteLLM forwards upstream
- **Evidence**: The "Task APIs" section states the polling expectation and
  shows the `tasks_get.sh` example; the forwarding sentence names the
  forwarded method set.
- **Confidence**: emerging (restatement; the forwarding rule is already
  extracted in the overview note Claim 6)
- **Quote**: "Agents that return a `submitted` task from `message/send` expect clients to poll with `tasks/get`. Call the same LiteLLM base URL with JSON-RPC:"
- **Our assessment**: Per triage bounding, this is a restatement of the
  overview's Claim 6 routing split — do not re-extract the forwarding. What the
  page confirms from the client side is the polling *pattern* implied by that
  claim: the client polls through the gateway against the same `/a2a/{agent_id}`
  base URL, i.e. task-polling traffic traverses the gateway but (per Claim 6's
  routing rule) bypasses its client-path logging/guardrails/spend. The
  `tasks/get` example call shape is preserved in Concrete Artifacts only where
  it differs from the agent-card note's two-step curl (placeholder
  `TASK_ID_FROM_SEND_RESPONSE` confirmed).

### Claim 9: Client-side card discovery on the SDK path resolves the agent card from the proxy — the 1.x examples call `A2ACardResolver(base_url="{base}/a2a/{agent_id}")` and build the client from the resolved card via `ClientFactory`, exercising the SDK's default well-known card path against the proxy's `/a2a/{agent_id}` base
- **Evidence**: Both SDK examples perform
  `resolver = A2ACardResolver(httpx_client=http_client, base_url=base_url)`,
  `agent_card = await resolver.get_agent_card()`, then
  `ClientFactory(config).create(agent_card)`. Agent listing for key access uses
  `GET /v1/agents`.
- **Confidence**: emerging (documented call shape)
- **Quote**: "resolver = A2ACardResolver(httpx_client=http_client, base_url=base_url)"
- **Our assessment**: Two cross-references ride on this claim. (1) Corroborates
  the permissions note's Claim 6 — `GET /v1/agents` only returns agents the
  key can access: the page's SDK walkthrough step 1 labels that call "Query
  `/v1/agents` to see which agents your key can access." (2) A data point for
  open contradiction **#1322** (served-card path naming: `/.well-known/agent.json`
  proxy-served vs `/.well-known/agent-card.json` upstream standard path): this
  page is a concrete client that resolves the card through the *SDK default
  well-known path* against the proxy's `/a2a/{agent_id}` base — i.e. it
  exercises one of the two contested paths. Recorded as evidence for the issue,
  not adjudicated here.

## Concrete Artifacts

### Install pin (from "A2A SDK", verbatim)

```bash
pip install "a2a-sdk>=1.1.0,<2.0" httpx
```

### OpenAI non-streaming invocation (from `openai_non_streaming.py`, verbatim)

```python
import openai

client = openai.OpenAI(
    api_key="sk-<your-litellm-api-key>",  # Your LiteLLM Virtual Key
    base_url="http://localhost:4000"  # Your LiteLLM proxy URL
)

response = client.chat.completions.create(
    model="a2a/my-agent",  # Use a2a/ prefix with your agent name
    messages=[
        {"role": "user", "content": "Hello, what can you do?"}
    ]
)

print(response.choices[0].message.content)
```

### OpenAI streaming invocation (from `curl_streaming.sh`, verbatim)

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "a2a/my-agent",
    "messages": [
      {"role": "user", "content": "Tell me a long story"}
    ],
    "stream": true
  }'
```

### a2a-sdk 1.x client construction with streaming toggle (from `invoke_a2a_agent_streaming.py`, verbatim — non-streaming variant identical except `streaming=False`)

```python
base_url = f"{LITELLM_BASE_URL}/a2a/{LITELLM_AGENT_NAME}"
headers = {"Authorization": f"Bearer {LITELLM_VIRTUAL_KEY}"}

async with httpx.AsyncClient(headers=headers, timeout=60.0) as http_client:
    resolver = A2ACardResolver(httpx_client=http_client, base_url=base_url)
    agent_card = await resolver.get_agent_card()

    config = ClientConfig(
        httpx_client=http_client,
        streaming=True,
        supported_protocol_bindings=[
            TransportProtocol.JSONRPC,
            TransportProtocol.HTTP_JSON,
        ],
    )
    client = ClientFactory(config).create(agent_card)
```

### Task-polling call (from `tasks_get.sh`, verbatim)

```bash
curl -X POST "http://localhost:4000/a2a/${AGENT_ID}" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-2",
    "method": "tasks/get",
    "params": {"id": "TASK_ID_FROM_SEND_RESPONSE"}
  }'
```

### Key Differences (from the "Key Differences" table, verbatim)

```
Method          Use Case                              Advantages
A2A SDK         Native A2A protocol integration       • Full A2A protocol support
                                                     • Access to task states and artifacts
                                                     • Context management
OpenAI SDK      Familiar OpenAI-style interface       • Drop-in replacement for OpenAI calls
                                                     • Easier migration from LLM to agent workflows
                                                     • Works with existing OpenAI tooling
```

Model Prefix (verbatim): "When using the OpenAI SDK, always prefix your agent name with `a2a/` (e.g., `a2a/my-agent`) to route requests to the A2A agent instead of an LLM provider."

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guardrails, pre-on-caller; no A2A / gateway
  invocation-surface content.
- `source-notes/docs-litellm-a2a-agent-card.md` — **cited** (Corroborates,
  Contradicts-data-point — see below).
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP /
  coding-agent integration; unrelated to agent invocation surfaces.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors; not agent invocation.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  telemetry integration and manual session correlation; no content on the `a2a/`
  bridge's instrumentation (the channel-space parallel to Claim 3 was already
  drawn by the overview note).
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization; unrelated.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  model/LLM guardrail scanner stacks; no A2A invocation or proxy surfaces.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **dismissed**: budget
  windows / caching / MCP Tool Search on the model path; no agent invocation
  content (the MCP Tool Search parallel was already dismissed by the overview
  note for the same reason).
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **dismissed**:
  embedding-based response caching; unrelated.
- `source-notes/docs-litellm-a2a-agent-gateway.md` — **cited** (Corroborates,
  Contradicts-data-point, Extends — see below). The primary reference note.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 4** (protocol
    versioning footgun: only `"0.3"` and `"1.0"` accepted, unpinned responses
    inferred from client signals) — this page's pin-on-the-agent advice
    (this note Claim 6) is the client-facing equivalent, adding only the
    "1.x SDK clients expect `1.0`-pinned agents" consequence.
  - `source-notes/docs-litellm-a2a-agent-card.md` **Claim 10** (per-agent
    bidirectional protocol conversion; clients always see the pinned version)
    — again corroborated, not extended, by the invoking page's pin advice.
  - `source-notes/docs-litellm-a2a-agent-permissions.md` **Claim 6** (`GET
    /v1/agents` only returns agents the key/team can access; 403 on
    `POST /a2a/{agent_id}`) — this page's SDK walkthrough lists agents
    precisely as "which agents your key can access".
- **Contradicts**: No new contradiction issue filed. The page provides one
  **data point** for open contradiction **#1322** (served-card path naming —
  `/.well-known/agent.json` proxy-served vs `/.well-known/agent-card.json`
  upstream standard path, filed against the conflicting statements in the
  overview note #1302 and the agent-card note #1315): the two SDK examples
  resolve the card through `A2ACardResolver` against the proxy's
  `/a2a/{agent_id}` base, i.e. the SDK's default well-known path is exercised
  against the proxy in official vendor examples. Evidence for the existing
  issue; no verdict picked. The `a2a/` bridge is a third surface (chat
  completions, not JSON-RPC) that is orthogonal to the path-name dispute, and
  the overview's Claim 6 routing split (only `message/send`/`message/stream`
  through the client path) is not opposed by this page — it simply does not
  cover the `a2a/` bridge either. Verified `CONTRADICTIONS.md` (no A2A entries)
  and open contradiction issues (#1150 routing flavors, #1307 promptfoo trace
  assertions, #1322 served-card path) — no duplicate for this page's content.
- **Extends**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 6** (only
    `message/send` and `message/stream` traverse the gateway's A2A client path;
    all other JSON-RPC methods forwarded upstream) — this page adds a
    second client-facing invocation path the overview does not enumerate: the
    OpenAI-compatible `a2a/` bridge. Because the overview's routing rule is
    stated over JSON-RPC methods only, the bridge's relationship to the client
    path is *unresolved by either page* (this note Claim 3) — a gap the guide
    should surface rather than resolve.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` Concrete Artifacts →
    "Primary endpoint" (server-side floor: "LiteLLM proxy A2A routes require
    **a2a-sdk >= 1.1.0**") — this page provides the matching *client* floor
    (`a2a-sdk>=1.1.0,<2.0`) and the breaking 0.3.x → 1.x client migration
    contract (this note Claim 4), so the version constraint is a two-sided
    lock-step obligation.
  - `source-notes/docs-litellm-a2a-agent-card.md` Concrete Artifacts →
    "Two-step task flow curl example" — this page's `tasks_get.sh` confirms the
    client-side polling pattern (`submitted` → poll `tasks/get`, same base
    URL), per triage bounding as a restatement only.
  - `source-notes/blog-litellm-agents-are-the-new-llms.md` (qualitative, via
    the overview note's Extends) — the "invoke" control-plane verb gains a
    second concrete surface here; no claim-number citation made because the
    relationship is via the overview note.
- **Novel**: The `a2a/` model-prefix OpenAI-compatible invocation bridge is
  entirely new to the corpus — no existing note mentions a chat-completions
  path into an agent. Also new: the client-side a2a-sdk 1.x migration contract
  (`A2AClient`+dict → `ClientFactory`+protobuf, `send_message` as async
  generator, `supported_protocol_bindings` requirement) and the structural
  narrowing (task state / artifacts / context management unavailable on the
  OpenAI path, this note Claim 2).

## Guide Impact

- **Chapter 03 (Runbooks and Agents)** — add a dual-invocation-path runbook
  rule: a registered LiteLLM A2A agent is reachable via native JSON-RPC
  (`POST /a2a/{agent_id}`, a2a-sdk) **and** via `model: "a2a/<agent_name>"`
  on `POST /v1/chat/completions`. Choose the surface by task shape: the
  `a2a/` bridge fits single-round-trip, content-style agents; anything that
  returns `submitted`/`working` tasks (or needs artifacts/context) must use
  the SDK path, since the OpenAI bridge collapses to one
  `choices[0].message.content` result with no task-state surface (Claims 1-2,
  8). Add the client-SDK upgrade floor (`a2a-sdk>=1.1.0,<2.0`) and the
  0.3.x→1.x breaking client migration to any A2A upgrade runbook — client and
  gateway must move in lock-step (Claim 4).
- **Chapter 05 (LLM Ops Reliability)** — add an open verification check, not a
  documented behavior: the vendor docs do not state whether `a2a/`
  chat-completions calls are logged, spend-attributed, and guardrailed like
  gateway `message/send` traffic, or routed through a less-instrumented alias
  (the overview's Claim 6 bypass pattern does not cover this surface). A naive
  "both paths are governed identically" assumption is unsupported — verify
  per-path instrumentation and spend rows before relying on the bridge
  (Claim 3). Also note the identifier rule (name vs id, Claim 7) as a
  misconfiguration source (exact-name match required for the `a2a/` prefix).
- **Chapter 02 (Observability)** — the `a2a/` chat-completions bridge's
  observability status is undocumented (no logging/spend/trace statement on
  the page) — record the check "is the `a2a/` path visible in gateway
  logs/spend/traces?" alongside the overview note's cross-hop header
  forwarding obligation (#1302 Claim 2) as a second A2A-path observability
  uncertainty (Claim 3).

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/a2a_invoking_agents`, HTTP 200, no paywall)
  **and** via raw HTML fetch (`curl`) so the ten prism code blocks and all
  running-text quotes were captured character-for-character (the webfetch's
  markdown render flattened code-block line breaks; the raw-HTML extraction
  restored them). Every `Quote` in this note is a contiguous verbatim string
  from the fetched page/article text; code artifacts preserve the page's exact
  call shapes.
- Triage bounding honored (#1330, three triage comments, `triaged:text`,
  `priority:medium`). Primary extraction is the `a2a/` chat-completions bridge
  (Claims 1-3 — the one genuinely novel surface). Secondary is the client-side
  SDK migration contract (Claims 4-5). Tertiary is the pin-the-agent advice as
  a footnote re-citing overview Claim 4 / agent-card Claim 10 (Claim 6, no
  mechanism re-derived). The "Reuse warning" was honored: the Task APIs section
  (Claim 8) and the `/a2a/{agent_id}` method surface are restatements of the
  overview's Claim 6 and the agent-card note — captured as a client-side
  polling confirmation and artifacts only, with the method-forwarding rule
  explicitly cross-referenced, not re-extracted. The auth angle (403 behavior)
  is not re-extracted — the permissions note already cites this page's
  "Invoking an agent" text.
- Gaps flagged rather than inferred, per the Prospector's key question: the
  page is **silent** on (a) whether the `a2a/` bridge inherits gateway
  logging/spend/guardrails or a bypass, (b) how a `submitted`/`working`
  non-terminal task maps onto a `chat.completions` response, and (c) any
  error/timeout semantics for the bridge. Claim 3 records this as a documented
  absence with the two unresolved readings; no verdict selected.
- The identifier question (name vs id) was answered from the page's own
  examples plus the overview note's "{agent_id} may be the agent UUID or the
  registered agent name" (Claim 7) — two spellings of one registry key, not a
  divergence.
- No contradiction issue filed: no new two-live-positions opposition. The
  page contributes one client-side evidence data point to open contradiction
  #1322 (the SDK `A2ACardResolver` examples resolve the card via the SDK
  default well-known path against the proxy) without adjudicating it; the
  overview's Claim 6 routing split is not opposed. Verified
  `CONTRADICTIONS.md` and open `contradiction`-labeled issues (#1150, #1307,
  #1322) before concluding — no duplicate.
- Confidence is `emerging` throughout: the page documents vendor *capability*
  surfaces (endpoints, code shapes, migration contract) with no measured
  overhead, no failure writeup, and no production experience report. The
  reliability-relevant claims (structural narrowing, Claim 2; instrumentation
  gap, Claim 3) are flagged in `Our assessment` as the Miner's reading of the
  documented surface, not as source assertions.
- `date_published` is unknown (living Docusaurus docs page); `date_extracted`
  and `last_checked` are both 2026-09-16. Sibling open issues from the same
  crawl batch (#1329 cost tracking, #1331 iteration budgets) are separate pages
  and were not preempted.