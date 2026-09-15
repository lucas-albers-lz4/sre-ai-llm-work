---
source_url: https://docs.litellm.ai/docs/a2a_agent_card
source_type: docs
title: "A2A Agent Card — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-15)
date_extracted: 2026-09-15
last_checked: 2026-09-15
status: current
confidence_overall: emerging
issue: "#1315"
---

# A2A Agent Card (LiteLLM Docs)

> The gateway serves a **curated, reduced** agent card — the per-field A2A v1.0
> §4.4 support matrix shows exactly which fields silently vanish (signatures,
> per-skill `securityRequirements`, `pushNotifications`, all of `AgentExtension`),
> skill selection via `metadata.skillId` is forwarded to the upstream agent
> **unenforced**, the curated card drifts from the upstream agent until a manual
> re-sync, and a client cannot verify the authenticity of what the proxy serves.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living page
  under the "Agent & MCP Gateway" nav section). Sibling issue #1316
  (`docs/a2a_agent_headers`) and #1317 (`docs/a2a_agent_permissions`) are filed
  from the same crawl batch; this note stays on the agent-card page and does not
  preempt them.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Claims about the field-support matrix, the served-card paths, and the routing
  rules are authoritative for the *documented surface*, but the page demonstrates
  capability only — no measured overhead, no failure writeups, no production
  experience report. Per the Prospector's bounding rule, everything in this note
  stays at "the gateway exposes / does not expose this surface," never "this
  works at scale."
- **Scope**: This page documents which A2A agent card fields LiteLLM supports
  (per-spec-object ✅/❌ matrix), the five-step fetch→curate→serve flow, per-agent
  protocol-version conversion, the supported JSON-RPC method surface (including
  PascalCase SDK aliases), completion-bridge narrowing, and skill routing. It
  does **not** cover headers/credentials (sibling #1316) or permission management
  (sibling #1317). The per-method routing table and the 0.3/1.0 wire-shape table
  were already extracted by `docs-litellm-a2a-agent-gateway.md` (#1302,
  Claims 4 and 6) — this note cross-references them instead of re-extracting per
  the Prospector's bounding.

## Extracted Claims

### Claim 1: The gateway serves a curated, reduced agent card — LiteLLM's support for A2A v1.0 §4.4 agent-card objects is a per-field ✅/❌ matrix, not a passthrough
- **Evidence**: The "Agent card support" section publishes a ✅/❌ table per spec
  object (§4.4.1 AgentCard through §4.4.7 AgentCardSignature); the section intro
  defines the symbols. Unsupported within §4.4.1–4.4.7: `signatures`,
  `capabilities.pushNotifications`, `capabilities.extensions`,
  `capabilities.extendedAgentCard`, all of `AgentExtension`, `AgentSkill.securityRequirements`,
  `AgentInterface.tenant`, and the entire `AgentCardSignature` object. Intro
  sentence frames the served card as a deliberate artifact.
- **Confidence**: emerging (vendor capability surface with an explicit
  field-level matrix; no reliability claims)
- **Quote**: "A ✅ means the field is present in the agent card LiteLLM serves to clients; a ❌ means the field is not."
- **Our assessment**: This is the ops-relevant claim: a client discovering
  capabilities through the proxy is reading a *reduced* contract that silently
  omits fields the upstream agent may actually advertise. Any tooling that
  consumes the proxied card as ground truth inherits the gaps below. The full
  matrix is preserved verbatim in Concrete Artifacts.

### Claim 2: The served card carries no signatures — `AgentCard.signatures` and the entire `AgentCardSignature` (§4.4.7) object are dropped, so a client cannot verify agent-card authenticity or provenance through the gateway
- **Evidence**: §4.4.1 row `signatures` ❌; §4.4.7 table has all three fields
  (`protected`, `signature`, `header`) ❌.
- **Confidence**: emerging (field matrix; the security implication is the Miner's
  inference, not a statement on the page)
- **Quote**: (no direct quote — see §4.4.1 `signatures` row and §4.4.7 field-support
  matrix in Concrete Artifacts)
- **Our assessment**: At the gateway, the card is a LiteLLM-authored artifact (it
  is fetched then curated by a human in the UI), and with the signature fields
  dropped there is nothing a client can verify against the upstream agent.
  "Verify the agent card" checks therefore have to run on a path that bypasses
  the proxy, or against the upstream agent directly. This is Claim 9's Serviciul
  gap in the overview note made concrete at the field level — see Contradicts/Extends.

### Claim 3: Per-skill security scoping is dropped — `AgentSkill.securityRequirements` (§4.4.5) is ❌ while every other skill field (`id`, `name`, `description`, `tags`, `examples`, `inputModes`, `outputModes`) is ✅, so per-skill security requirements are invisible to clients even though the skill itself is exposed
- **Evidence**: §4.4.5 field-support table.
- **Confidence**: emerging (field matrix)
- **Quote**: (no direct quote — see §4.4.5 field-support matrix in Concrete Artifacts)
- **Our assessment**: A client trying to make skill-level authorization or
  scoping decisions from the served card cannot see what each skill requires.
  The card advertises skills (roster) without their security context — a
  mismatch that matters in Ch06 terms (see Guide Impact).

### Claim 4: `capabilities.pushNotifications` is dropped (§4.4.3 ❌) while every push-notification RPC method is routed to upstream — capability advertisement and the routed method surface disagree
- **Evidence**: §4.4.3 matrix lists `pushNotifications` ❌ (and `extensions` ❌,
  `extendedAgentCard` ❌, `streaming` ✅); the Supported A2A Methods table lists
  `tasks/pushNotificationConfig/set|get|list|delete` all ✅ "JSON-RPC forwarded to
  upstream". No reconciling statement on the page.
- **Confidence**: emerging (matrix vs method table; the disagreement itself is
  the finding, not the Miner's inference)
- **Quote**: (no direct quote — compare the §4.4.3 `pushNotifications` ❌ row with
  the `tasks/pushNotificationConfig/*` rows in Concrete Artifacts)
- **Our assessment**: A capability-based client that sees `pushNotifications` ❌
  and disables async notification workflows would be wrong about the *routed
  surface* — the methods still reach upstream and work if the upstream agent
  supports them. Nothing on the page reconciles discovery and method surface, so
  feature detection via the proxy card can silently mismatch what the endpoint
  accepts. Borderline §4a case (within-source tension rather than two live
  positions) — surfaced here rather than filed as a contradiction issue.

### Claim 5: Skill selection is forwarded, not enforced — clients pick a skill via `params.message.metadata.skillId` and LiteLLM forwards the entire message envelope unchanged, leaving routing and any skill-level authorization to the upstream agent
- **Evidence**: "Skill routing" section with the `skillId` JSON-RPC example;
  the explicit pass-through sentence.
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "LiteLLM forwards the entire message envelope, including metadata, to the upstream agent unchanged. The upstream agent is responsible for reading `skillId` and routing internally."
- **Our assessment**: The card's skill roster is **advisory, not an access-control
  boundary**: hiding a skill from the curated card (Claim 6 flow) does not stop a
  client from naming it in `metadata.skillId` — there is no gateway-side
  validation that the requested `skillId` exists in the served card, and no
  gateway-side skill authorization. Contrast the overview note's Claim 7
  (per-agent key/team permission → HTTP 403): authorization granularity here is
  **agent**, not skill. "Look like a control, aren't one" pattern worth naming in
  the guide.

### Claim 6: The curated card drifts from the upstream agent — re-sync is a manual, selective UI action, so new upstream skills/capabilities stay invisible until a human re-syncs, and locally curated edits persist against upstream changes
- **Evidence**: "How A2A on LiteLLM works" flow (fetch upstream card → review in
  UI → choose skills/fields → serve) plus the "Editing the agent card" section
  describing the "Re-sync from upstream" button.
- **Confidence**: emerging (documented vendor flow; drift follows from the manual
  step but is not demonstrated)
- **Quote**: "You can edit supported fields from the agent detail page in the LiteLLM UI. Use the **Re-sync from upstream** button to pick up new skills or capabilities the upstream agent has added since registration; it shows a diff and lets you accept changes selectively."
- **Our assessment**: The served card is a fork of the upstream card with no
  described automated freshness check. New upstream skills/capabilities are
  invisible to clients until someone clicks re-sync, and locally curated edits
  survive against upstream changes. Operationally that is a config-drift problem
  (Ch05/Ch03): the runbook question "does my gateway card still match the agent
  it fronts?" has no automated answer on this page.

### Claim 7: Task and push-notification methods require a real upstream A2A JSON-RPC server — LiteLLM forwards the request body unchanged (aside from auth headers) to `agent_card_params.url`, and `agent/getAuthenticatedExtendedCard`'s `result.url` is rewritten to the proxy
- **Evidence**: "Requirements" bullet 1 and the method table's
  `agent/getAuthenticatedExtendedCard` row ("JSON-RPC forwarded to upstream;
  `result.url` rewritten to the proxy").
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "**Task and push-notification methods** require `agent_card_params.url` pointing at a real A2A JSON-RPC server. LiteLLM forwards the request body unchanged (aside from auth headers)."
- **Our assessment**: Extends the overview note's Claim 6 (non-`message/*` methods
  forwarded upstream) with the forwarding details: the body passes through
  untouched except auth header handling, and the extended-card method's `url`
  comes back proxy-rewritten so clients calling back through the gateway stay on
  the proxy. Verbose agreement with the overview note's routing split, sharpened
  with the concrete error case in Claim 8.

### Claim 8: Completion-bridge-only agents have a narrower capability surface — LangGraph / Bedrock AgentCore agents with `custom_llm_provider` and no `url` support `message/send` and `message/stream` only; task APIs return an error when no upstream URL is configured
- **Evidence**: "Requirements" bullet 2 (explicit agent classes and the error
  condition).
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "**Completion-bridge-only agents** (for example LangGraph/Bedrock AgentCore with `custom_llm_provider` and no `url`) support `message/send` and `message/stream` only. Task APIs return an error if no upstream URL is configured."
- **Our assessment**: Adds the no-`url` error case the overview note's Claim 6
  established a bypass for but did not state as an error. Config-shape
  distinction: a gateway agent with a bridge provider and no `url` cannot
  participate in task-based or notification-based workflows at all — worth a
  registration-time check, since the documented failure is a runtime error, not a
  go/no-go gate.

### Claim 9: `message/send` and `message/stream` may strip LiteLLM-specific keys from `params` (e.g. `guardrails`), while task-method `params` are forwarded as-is so A2A fields like `id` are preserved
- **Evidence**: "Requirements" bullet 3.
- **Confidence**: emerging (documented vendor behavior; the page says "may strip",
  naming `guardrails` as an example, with no exhaustive list)
- **Quote**: "**`message/send` / `message/stream` only:** LiteLLM may strip LiteLLM-specific keys from `params` (for example `guardrails`). Task method `params` are forwarded as-is so A2A fields like `id` are preserved."
- **Our assessment**: A param-handling asymmetry across the two surface classes:
  a per-call control threaded through `message/*` params (e.g., a guardrail
  selector a client expects the gateway to honor) can be silently absent on the
  upstream call, while task methods carry everything through. The "may strip" is
  non-deterministic language — operators cannot enumerate which keys disappear.
  Relevant to Ch05 (config is what you can observe upstream).

### Claim 10: Protocol conversion is per-agent and bidirectional — LiteLLM converts upstream agent responses to the `protocolVersion` pinned on each agent, clients always see the chosen version, `"1.0"` is the default on new cards, and unsupported versions are rejected with HTTP 400
- **Evidence**: "Protocol versioning" section (conversion sentence, the
  1.0/0.3 wire-shape table, default-on-new-cards note, HTTP 400 rejection), plus
  the page's cross-link to `/docs/a2a` for "client negotiation when
  `protocolVersion` is not pinned".
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "LiteLLM converts upstream agent responses to the `protocolVersion` pinned on each agent. Clients always see the version you choose, regardless of what the upstream agent speaks natively."
- **Quote**: "Unsupported values are rejected with HTTP 400."
- **Our assessment**: Confirms the overview note's Claim 4 pinning story from the
  card side and adds *per-agent, bidirectional* conversion — the served
  responses are rendered into the pinned version whatever the upstream speaks.
  That softens (does not eliminate) the overview's unpinned-negotiation footgun:
  the hazard lives specifically in the *unpinned* default (`1.0` card vs
  0.3-shaped `message/send` responses for headerless legacy callers) — pinning on
  the card removes the disagreement. The two pages must be read together; this
  note deliberately restates nothing about unpinned negotiation.

### Claim 11: LiteLLM accepts PascalCase SDK aliases for every A2A method — the wire methods are all reachable through the aliases (`SendMessage`→`message/send`, `GetTask`→`tasks/get`, `SubscribeToTask`→`tasks/resubscribe`, `GetExtendedAgentCard`→`agent/getAuthenticatedExtendedCard`, etc.)
- **Evidence**: "PascalCase aliases (SDK)" table (12 rows) and the intro sentence
  to "Supported A2A methods".
- **Confidence**: emerging (documented vendor surface; page states nothing about
  whether alias handling differs on gateway controls)
- **Quote**: "LiteLLM also accepts the PascalCase aliases from the A2A SDK (for example `GetTask` → `tasks/get`)."
- **Our assessment**: Relevant to any per-method gateway control (logging,
  guardrails, cost — most of which only attach to `message/*` anyway): a control
  keyed on the camelCase wire name could be bypassed by the PascalCase alias
  *if* alias handling ever diverges. The page gives no such divergence — this
  stays an emerging breadth observation, not a finding of a bypass.

## Concrete Artifacts

### Field-support matrix (from "Agent card support", verbatim — A2A v1.0 §4.4)

AgentCard (§4.4.1):

```
Field                      Supported
protocolVersion            ✅
name                       ✅
description                ✅
supportedInterfaces        ✅
provider                   ✅
version                    ✅
documentationUrl           ✅
capabilities               ✅
securitySchemes            ✅
securityRequirements       ✅
defaultInputModes          ✅
defaultOutputModes         ✅
skills                     ✅
signatures                 ❌
iconUrl                    ✅
```

AgentProvider (§4.4.2):

```
Field                      Supported
url                        ✅
organization               ✅
```

AgentCapabilities (§4.4.3):

```
Field                      Supported
streaming                  ✅
pushNotifications          ❌
extensions                 ❌
extendedAgentCard          ❌
```

AgentExtension (§4.4.4): all fields ❌ — `uri`, `description`, `required`, `params`.

AgentSkill (§4.4.5):

```
Field                      Supported
id                         ✅
name                       ✅
description                ✅
tags                       ✅
examples                   ✅
inputModes                 ✅
outputModes                ✅
securityRequirements       ❌
```

AgentInterface (§4.4.6):

```
Field                      Supported
url                        ✅
protocolBinding            ✅
tenant                     ❌
protocolVersion            ✅
```

AgentCardSignature (§4.4.7): all fields ❌ — `protected`, `signature`, `header`.

### Fetch → curate → serve flow (from "How A2A on LiteLLM works", verbatim)

```
1. You provide a base URL (and, for some providers, an assistant identifier).
2. LiteLLM fetches the upstream agent card from the agent's `/.well-known/agent-card.json`
   (or the provider-specific equivalent).
3. You review the parsed card in the LiteLLM UI, choose which skills and fields to
   expose, and pick a Protocol Version (`1.0` or `0.3`) for clients.
4. LiteLLM saves the curated card and serves it at:
   GET /a2a/{agent_id}/.well-known/agent.json
5. Clients invoke the agent at:
   POST /a2a/{agent_id}
   using A2A JSON-RPC 2.0 (see Supported A2A methods below).
```

### Protocol-version serving table (from "Protocol versioning", verbatim)

```
protocolVersion                 Served to clients
"1.0" (default on new cards)    Protobuf JSON envelopes — result.message,
                                stream statusUpdate / artifactUpdate
"0.3"                           Legacy kind-discriminated JSON — result.kind == "message"
```

### Supported A2A methods (from "Supported A2A methods", verbatim — condensed)

```
Method                              Handle
message/send                        Routed through LiteLLM A2A SDK (asend_message) — logging, guardrails, cost tracking
message/stream                      Routed through LiteLLM streaming handler — NDJSON/SSE response
tasks/get                           JSON-RPC forwarded to the agent's agent_card_params.url
tasks/list                          JSON-RPC forwarded to upstream
tasks/cancel                        JSON-RPC forwarded to upstream
tasks/resubscribe                   JSON-RPC forwarded to upstream (streaming/SSE)
tasks/pushNotificationConfig/set    JSON-RPC forwarded to upstream
tasks/pushNotificationConfig/get    JSON-RPC forwarded to upstream
tasks/pushNotificationConfig/list   JSON-RPC forwarded to upstream
tasks/pushNotificationConfig/delete JSON-RPC forwarded to upstream
agent/getAuthenticatedExtendedCard  JSON-RPC forwarded to upstream; result.url rewritten to the proxy
```

### PascalCase SDK aliases (from "PascalCase aliases (SDK)", verbatim)

```
SendMessage                     -> message/send
SendStreamingMessage            -> message/stream
GetTask                         -> tasks/get
ListTasks                       -> tasks/list
CancelTask                      -> tasks/cancel
SubscribeToTask                 -> tasks/resubscribe
CreateTaskPushNotificationConfig -> tasks/pushNotificationConfig/set
GetTaskPushNotificationConfig   -> tasks/pushNotificationConfig/get
ListTaskPushNotificationConfigs -> tasks/pushNotificationConfig/list
DeleteTaskPushNotificationConfig -> tasks/pushNotificationConfig/delete
GetExtendedAgentCard            -> agent/getAuthenticatedExtendedCard
```

### Two-step task flow curl example (from "Example: two-step task flow", verbatim, 0.3 wire format)

```bash
curl -X POST "http://localhost:4000/a2a/my-agent" \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "r1",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "messageId": "m1",
        "parts": [{"kind": "text", "text": "Hello"}]
      }
    }
  }'
```

Then poll with `method: "tasks/get"`, `params: {"id": "<task-id-from-step-1>"}`.

### Skill-selection envelope (from "Skill routing", verbatim)

```json
{
  "jsonrpc": "2.0",
  "id": "req-1",
  "method": "message/send",
  "params": {
    "message": {
      "messageId": "msg-001",
      "role": "user",
      "parts": [{"kind": "text", "text": "..."}],
      "metadata": {"skillId": "triage_ticket"}
    }
  }
}
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guardrails, pre-on-caller; no agent-card /
  proxy-gateway surface.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP
  coding-agent integration; unrelated to agent-card surfaces.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors; not agent invocation or cards.
- `source-notes/docs-litellm-a2a-agent-gateway.md` — **cited** (Corroborates,
  Contradicts, Extends — see below). The primary reference note.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: its
  manual-session-correlation parallel was already drawn by the overview note; no
  agent-card content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization; unrelated.
- `source-notes/docs-datadog-llm-observability.md` — **dismissed**: trace/span
  model for LLM apps; no agent-card or capability-advertisement content.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  model-path guardrail scanner stacks; no card-field or proxy capability surface.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **dismissed**: budget
  windows/caching + MCP Tool Search; cost-control topic, not agent-card surfaces.
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **dismissed**:
  embedding-based response caching; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 4** (the proxied
    card defaults to `1.0` when `protocolVersion` is unset; only `0.3`/`1.0`
    accepted, else HTTP 400) — this page states `"1.0" (default on new cards)`
    and "Unsupported values are rejected with HTTP 400" (this note Claim 10).
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 6** (`message/send`
    and `message/stream` go through LiteLLM's A2A client; all other methods
    forwarded to `agent_card_params.url`) — this page's method table (this note
    Claim 7) matches row-for-row, adding the `result.url` proxy rewrite for
    `agent/getAuthenticatedExtendedCard`.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 2** (gateway sets a
    contract; enforcement lives in code the operator does not control) — this
    note's skill-routing finding (Claim 5) is the same class of gap for skill
    selection: the card is advisory, the upstream agent routes.
- **Contradicts**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` — **served-card path naming**.
    The overview note's API-reference artifact lists
    `GET /a2a/{agent_id}/.well-known/agent.json` **and**
    `GET /a2a/{agent_id}/.well-known/agent-card.json` ("standard path") as
    proxy-served card paths. This page instead locates `/.well-known/agent-card.json`
    at the **upstream agent** ("LiteLLM fetches the upstream agent card from the
    agent's `/.well-known/agent-card.json`") and names
    `GET /a2a/{agent_id}/.well-known/agent.json` as the only proxy-served path.
    Filed as **contradiction issue #1322** per MINER §4a (same-vendor docs, two
    pages, non-obvious which path is authoritative on the proxy; likely
    legacy-vs-v1.0 naming during spec migration — no verdict picked here). Any
    client-discovery guidance in the guide should state both paths until the
    contradiction resolves.
- **Extends**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 7** (per-agent
    authorization: key/team permission intersection → HTTP 403) — this page adds
    the granularity gap (Claims 3, 5): authorization is at **agent** level, not
    per-skill, and the served card carries no per-skill security requirements.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 4** — the per-agent
    bidirectional protocol conversion on this page (Claim 10) narrows the
    unpinned footgun to explicitly-unpinned configurations; the two pages must be
    read together.
  - `source-notes/blog-litellm-agents-are-the-new-llms.md` — the "control plane"
    register/invoke/observe/govern thesis: this page is the register/govern
    artifact concrete — a card is curated and served centrally, but skill
    selection is not enforced, so "expose only these skills" is a documentation
    act, not a control. Same corpus convention as the overview note (vendor
    vision post vs shipping surface).
  - `source-notes/docs-litellm-streaming-token-usage.md` — model-path streaming
    accounting vs this page's agent-path streaming surface (`message/stream`
    "Routed through LiteLLM streaming handler — NDJSON/SSE response"); an
    agent-path counterpart, though this page documents no accounting behavior on
    the stream.
- **Novel**: First source note in the corpus with the per-field A2A v1.0 §4.4
  support matrix for a gateway-served agent card, including the signature
  (`AgentCardSignature` wholly unsupported), per-skill
  `securityRequirements`, capability-advertisement-vs-routed-method mismatch
  (`pushNotifications`), the fetch→curate→serve flow with the manual "Re-sync
  from upstream" drift model, the `metadata.skillId` pass-through, the
  completion-bridge no-`url` error case, the `message/*` param-stripping
  asymmetry, and the PascalCase alias surface. Nothing about agent-card field
  fidelity existed in the corpus before the overview note.

## Guide Impact

- **Chapter 06 (Security and Trust)** — proxy-fronted card authenticity: Add the
  `signatures` / `AgentCardSignature` gap (Claim 2) and the per-skill
  `securityRequirements` gap (Claim 3): a card served through the LiteLLM A2A
  gateway is unsigned and unverifiable against the upstream agent, and per-skill
  security context is dropped even where skills are exposed. Any "verify the
  agent card" guidance must either verify against the upstream agent directly or
  treat the proxy card as advisory. Also state the path ambiguity from
  contradiction #1322 (both `/.well-known/agent.json` and
  `/.well-known/agent-card.json`) so Ch06 checks target the right URL.
- **Chapter 03 (Runbooks and Agents)** — §"The emerging agent control plane":
  Add the skill-routing finding (Claim 5) and the curated-card drift model
  (Claim 6) as the "governed-agent artifact" example: the curated card's skill
  roster is visibility, not access control — `metadata.skillId` is forwarded
  unvalidated, so hiding a skill does not prevent a client from naming it, and
  authorization granularity is per-agent (overview Claim 7), not per-skill. Pair
  with the overview note's routing split already filed. Add the completion-bridge
  narrowing (Claim 8): LangGraph/Bedrock AgentCore agents without a `url` are
  message-only and error on task APIs — a registration-time check, not a runtime
  surprise.
- **Chapter 02 (Observability)** — notification/streaming surface: `message/stream`
  is the agent-path streaming handler (NDJSON/SSE) and `capabilities.pushNotifications`
  is ❌ while the pushNotificationConfig methods are forwarded (Claim 4) — an
  agent whose work is async/notification-driven has no advertised
  notification path on the proxied card, so async completion signals are not
  discoverable by clients through the gateway. Note the capability-vs-method
  mismatch for feature detection.
- **Chapter 05 (LLM Ops Reliability)** — config-management: Add card/upstream
  drift as a config-drift obligation (Claim 6): the served card is a manually
  re-synced fork with no automated freshness check — the operative runbook check
  is "does my gateway card still match the agent it fronts?" Add the
  `message/*` param-stripping asymmetry (Claim 9) as a second silent
  configuration-loss surface beside the overview note's forwarding obligations.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/a2a_agent_card`, HTTP 200, no paywall), with
  the running text and all seven field tables, the method table, the alias table,
  the fetch→curate→serve flow, and the two curl/JSON examples captured verbatim.
  No substantive linked sub-pages needed for verification beyond the overview
  note already in the corpus (`docs-litellm-a2a-agent-gateway.md`, which followed
  this same page for its Claims 4 and 6).
- Prospector bounding (both #1315 triage comments) honored: the per-method
  routing table and the 0.3/1.0 wire-shape table are **cross-referenced** to the
  overview note's Claims 4 and 6 rather than re-extracted; this note's novelty is
  the field matrix, skill routing, curation/drift, completion-bridge narrowing,
  param-stripping asymmetry, PascalCase aliases, and the no-`url` error case.
  Sibling pages (#1316 headers, #1317 permissions) not preempted.
- A contradiction issue was filed BEFORE this PR per MINER §4a — **#1322**,
  served-card path naming (this page's fetch/serve split vs the overview note's
  API-table "standard path"). No verdict picked in this note. A second,
  within-source tension (pushNotifications capability ❌ vs pushNotificationConfig
  methods forwarded) is surfaced as Claim 4 without a contradiction issue (no
  two live positions). Verified no duplicate filings: open contradiction issues
  are #1150 (LiteLLM routing flavors) and #1307 (promptfoo trace assertions);
  CONTRADICTIONS.md has no A2A entries.
- Confidence is `emerging` throughout: field-matrix and routing claims are
  documented vendor *capability* surface, and the security/drift implications in
  `Our assessment` are the Miner's inference from that surface, flagged as such.
  `date_published` is unknown (living Docusaurus page); `date_extracted` and
  `last_checked` are both 2026-09-15.