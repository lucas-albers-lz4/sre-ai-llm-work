---
source_url: https://docs.litellm.ai/docs/a2a_cost_tracking
source_type: docs
title: "A2A Agent Cost Tracking — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-15)
date_extracted: 2026-09-15
last_checked: 2026-09-15
status: current
confidence_overall: emerging
issue: "#1329"
---

# A2A Agent Cost Tracking (LiteLLM Docs)

> LiteLLM's A2A agent gateway exposes a **second, orthogonal cost-attribution
> axis**: an operator-declared, Admin-UI-configured per-agent price — flat
> "Cost Per Query" or "Input/Output Cost Per Token" — that lands in the gateway
> request log and is attributed to the **calling API key** (a per-team / per-project
> chargeback surface rolled up in a dedicated Agent Usage dashboard), with no
> documented linkage to the measured upstream model-cost path or to the
> `X-LiteLLM-Agent-Id` header-forwarding requirement the overview page describes.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living page
  under the "Agent & MCP Gateway > A2A Agent Gateway" nav section, sibling to the
  A2A Agent Gateway / Agent Card / Invoking / Authentication Headers / Permission
  Management / Iteration Budgets pages). Archived screenshot walkthrough dated
  2025-12-13 in the image URLs; page current as of 2026-09-15.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* LiteLLM exposes (field names, UI tab paths,
  attribution target, dashboard dimensions), but documents capability only — no
  measured overhead, no failure writeups, no production experience report. Per
  the Prospector's bounding rule, every claim in this note stays at "the gateway
  exposes this surface," never "this works at scale."
- **Scope**: Covers the per-agent cost configuration panel (three price fields),
  the attribution target (calling API key), the Logs cost column, the Agent Usage
  dashboard, and the Playground verification path on the `/v1/a2a/message/send`
  endpoint. Does **not** cover the measured model-path cost map, budget/rate-limit
  enforcement, or the header-forwarding spend contract — the page links "A2A
  Agent Gateway" and "Spend Tracking" as Related pages that this note does not
  absorb, per the Prospector's bounding.

## Extracted Claims

### Claim 1: LiteLLM's A2A gateway supports custom per-agent cost tracking in two modes — a flat cost charged for each agent request, and a variable cost based on input/output token usage
- **Evidence**: The page's intro defines the two configurable modes as a bulleted
  list and frames them as a way to "track and attribute costs for agent usage
  across your organization." The rest of the page operationalizes exactly these
  two modes (the cost table's three fields).
- **Confidence**: emerging (documented vendor capability surface; no
  implementation detail and no reliability claims on the page)
- **Quote**: "LiteLLM supports adding custom cost tracking for A2A agents. You can configure:"
- **Our assessment**: This is the flat-vs-token cost surface the Prospector
  flagged as a concrete spend-accounting surface rather than marketing. It is a
  per-agent accounting construct layered on the gateway request path, distinct
  from the per-model cost map the model path uses — we do not buy that it
  replaces the measured cost path; it complements it (see Claims 3 and 8).

### Claim 2: The per-agent "Cost Configuration" panel exposes two-and-three price fields — Cost Per Query ($), Input Cost Per Token ($), Output Cost Per Token ($) — with page guidance that a flat cost per query is simplest and token-based pricing is for when agent cost varies significantly with input/output length
- **Evidence**: The "Cost Configuration Options" table lists the three fields
  with descriptions, and the closing guidance sentence states the
  when-to-use-each rule.
- **Confidence**: emerging (documented field table + vendor guidance; no
  measured data behind the recommendation)
- **Quote**: "For most use cases, a flat cost per query is simplest. Use token-based pricing if your agent costs vary significantly based on input/output length."
- **Our assessment**: The page's own heuristic — token-based pricing only where
  agent cost varies significantly with length — matches the classic
  chargeback-model decision (flat avoids metering complexity; per-token aligns
  price to use). Operationally the interesting part is that token-based agent
  pricing must obtain input/output token counts *somewhere*; the page does not say
  which usage path feeds those counts (see Extends → `docs-litellm-streaming-token-usage.md`).

### Claim 3: The flat per-query cost is a gateway-declared synthetic charge — the operator enters a dollar figure in the UI and "each request to this agent" bills at that rate, with no documented linkage to the agent's measured token usage or upstream model cost
- **Evidence**: The "Set Cost Per Query" step states the flat amount directly;
  the cost table defines Cost Per Query ($) as a "Fixed cost charged for each
  agent request." No sentence on the page ties the configured figure to measured
  spend.
- **Confidence**: emerging (vendor-documented configuration semantics; the
  "synthetic charge, not a measured rollup" reading is the Miner's synthesis of
  the page's own wording — the page never claims the number is derived from
  anything)
- **Quote**: "Enter the cost per query amount (in dollars). For example, entering `0.05` means each request to this agent will be charged $0.05."
- **Our assessment**: This is the precise distinction the Prospector warned is
  easy to blur: a field labeled "Cost" in an accounting context implies
  *measurement*, but "$0.05 per request" is an operator-declared *price*, not a
  measured spend. For chargeback purposes that is fine; for cost *accuracy*
  purposes it is a pricing declaration that can silently drift from the agent's
  real consumption as token usage or model mix changes — and the page documents
  no reconciliation between the declared figure and observed model cost (see
  Extends → `failure-litellm-model-cost-map-silent-fallback.md`).

### Claim 4: Configured agent cost lands in the gateway request log (Logs cost column) and is attributed to the API key that made the request — the chargeback axis is per-team / per-project (the caller pays), not attribution to the agent's own backend spend
- **Evidence**: The "Viewing Cost in Logs" section states both the log placement
  and the attribution target.
- **Confidence**: emerging (documented vendor behavior; the per-key vs
  per-agent-backend distinction is the Miner's framing from the page's wording)
- **Quote**: "This cost is now attributed to the API key that made the request, so you can track spend per team or project."
- **Our assessment**: The attribution target matters for guide design: the
  configured cost is charged to whoever *mounted the request through the gateway*
  (the calling key), not to the agent's own upstream LLM spend. So the Agent
  Usage "total spend per agent" is really "aggregate declared charges across the
  requesters who hit this agent" — a chargeback rollup, not a measurement of the
  agent's model consumption. The two readings are easy to conflate; the guide
  should be explicit about which axis it is teaching (see Guide Impact → Ch05).

### Claim 5: A dedicated Agent Usage dashboard in the Admin UI provides agent-level spend analytics separate from the model-level spend views — total spend per agent, daily spend trends, model usage breakdown, and activity metrics (requests, tokens, success rates), filterable by agent ID
- **Evidence**: The "View Spend in Usage Page" section gives the tab path
  (`PROXY_BASE_URL/ui/?login=success&page=new_usage` → Agent Usage), the four
  analytics dimensions, and the agent filter dropdown; the model-usage breakdown
  dimension shows agent-to-model linkage.
- **Confidence**: emerging (documented dashboard surface; no metrics behind it)
- **Quote**: "Go to the Usage page in the Admin UI (`PROXY_BASE_URL/ui/?login=success&page=new_usage`) and click on the **Agent Usage** tab."
- **Our assessment**: The dashboard is the observability surface this page
  actually adds: agent-traffic spend analytics (total/daily/model breakdown)
  alongside activity metrics (requests, tokens, success rates) that the model
  "spend" views do not organize by agent. Note the "Model usage breakdown"
  dimension implies the dashboard can see which model an agent's requests used —
  but the configured cost is still the operator price, so the dashboard rolls up
  declared charges, with whatever linkage the page does not explain.

### Claim 6: The documented verification path bills through the A2A *message* path, not task methods — the Playground tests cost by selecting the `/v1/a2a/message/send` Endpoint Type for the agent, and the agent request is "logged with the cost you configured"
- **Evidence**: The "Testing Cost Tracking" section steps through the Playground
  Endpoint Type dropdown (`/v1/a2a/message/send`) and states the logged-cost
  outcome.
- **Confidence**: emerging (documented vendor procedure)
- **Quote**: "By default, the Playground uses the chat completions endpoint. To test your agent, click \"Endpoint Type\" and select `/v1/a2a/message/send` from the dropdown."
- **Our assessment**: The page's own verification path exercises `message/send` —
  exactly the method the gateway overview note and the agent-card method table
  put on the gateway's A2A client path ("logging, guardrails, spend"). The page
  never claims task methods (`tasks/get`, `tasks/list`, `tasks/cancel`,
  `tasks/pushNotificationConfig/*`) are billed, and they do not appear in the
  walkthrough. Per the Prospector's request, the "flat cost per agent request"
  scope tension is resolved here as a conditioning scope: the unqualified "each
  request" language should be read as *each request through the gateway's billable
  A2A path* (message/send / message/stream), consistent with the method-level
  routing table in the agent-card note — this is marked as a needs-cross-check
  relationship, not filed as a contradiction (see Cross-References).

### Claim 7: The cost configuration surface is Admin-UI-only — the page documents the three price fields exclusively through the UI "Cost Configuration" panel and never shows a config.yaml / API form, so the per-agent price is not liftable into declarative config or IaC from this page
- **Evidence**: The entire page is a UI click-through (Agents → + Add New Agent →
  Cost Configuration → Create Agent); no YAML, JSON, or API snippet appears
  anywhere. The "Quick Start" step 3 names the UI panel explicitly.
- **Confidence**: emerging (absence on this page — verified by full-page read;
  the page's Related links point to the A2A Gateway and Spend Tracking pages,
  which the Prospector instructed not to absorb, so a config form may exist
  elsewhere in the docs)
- **Quote**: "Scroll down and click on \"Cost Configuration\" to expand the cost settings panel. This is where you define how much to charge for agent usage."
- **Our assessment**: Operationally this is the IaC gap: the three cost fields
  have no documented declarative form on this page, so standing up agents with
  prices via config campaign (`config.yaml` `agents:` — see the gateway note's
  Claim 5) cannot carry the cost fields from this page. The gate-driven
  "when did we last re-check the declared per-query cost" question implies a
  human in the dashboard, not a reviewed file.

### Claim 8: The page gives no reconciliation between the configured cost and the overview page's header-forwarding spend-attribution contract — it neither mentions `X-LiteLLM-Agent-Id` nor states that configured costs bypass the forwarding requirement, so per-agent cost accounting in LiteLLM's docs is split across two unconnected mechanisms
- **Evidence**: Absence across the full page: the only attribution sentence names
  the calling API key; there is no header, forwarding, or agent-ID language. The
  overview page (`docs-litellm-a2a-agent-gateway.md` Claim 2) describes a
  different mechanism: per-agent spend attribution via `X-LiteLLM-Agent-Id` that
  materializes only if the agent server forwards the header.
- **Confidence**: emerging (the page's non-statement is a verified absence; the
  "two mechanisms" reading is the Miner's synthesis of the two pages)
- **Quote**: (no direct quote — absence claim based on full-page read; see Our assessment)
- **Our assessment**: These are best read as **two orthogonal cost axes**, not as
  a disagreement. Axis A (overview page Claim 2): *measured* spend — the agent
  server's own LLM calls back to LiteLLM are attributed to an agent only if it
  re-forwards `X-LiteLLM-Agent-Id`. Axis B (this page): *declared* charge — the
  gateway charges a configured price per billable A2A request and attributes it to
  the requesting key, needing no header forwarding because nothing is measured.
  They target different objects (agent vs calling key) and neither page asserts
  the other's mechanism is absent or replaced. Because the cost page asserts
  neither that forwarding is required nor that configured costs bypass it, this
  is not a claim-level opposition — no §4a contradiction filed (consistent with
  the Prospector's instruction). The gap is that the docs never connect A and B
  (e.g., whether both land in the same cost column for the same request, or how a
  "Model usage breakdown" reconciles declared vs measured price).

## Concrete Artifacts

All artifacts verbatim from the fetched page.

### Cost configuration fields (from "Cost Configuration Options" table)

| Field | Description |
|---|---|
| **Cost Per Query ($)** | Fixed cost charged for each agent request |
| **Input Cost Per Token ($)** | Cost per input token processed |
| **Output Cost Per Token ($)** | Cost per output token generated |

### Flat-vs-token guidance (verbatim)

> "For most use cases, a flat cost per query is simplest. Use token-based pricing if your agent costs vary significantly based on input/output length."

### Cost attribution (from "Viewing Cost in Logs", verbatim)

> "Find your agent request in the list. You'll see the cost column showing the amount you configured. This cost is now attributed to the API key that made the request, so you can track spend per team or project."

### Agent Usage dashboard (from "View Spend in Usage Page", verbatim)

Tab path: "Go to the Usage page in the Admin UI (`PROXY_BASE_URL/ui/?login=success&page=new_usage`) and click on the **Agent Usage** tab."

Analytics dimensions:

```
Total spend per agent:     View aggregated spend across all agents
Daily spend trends:        See how agent spend changes over time
Model usage breakdown:     Understand which models each agent uses
Activity metrics:          Track requests, tokens, and success rates per agent
```

Filter: select "one or more agent IDs from the dropdown" to view "filtered analytics, spend logs, and activity metrics".

### Playground verification path (from "Testing Cost Tracking", verbatim)

> "By default, the Playground uses the chat completions endpoint. To test your agent, click "Endpoint Type" and select `/v1/a2a/message/send` from the dropdown."

### Cost Configuration panel (from "Quick Start", verbatim)

> "This is where you define how much to charge for agent usage." — UI panel expanded under "Agents → + Add New Agent → Cost Configuration".

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-a2a-agent-card.md` — **cited** (Corroborates,
  Extends — see below).
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors and debuggability rationale (semantic/complexity/adaptive
  scorer); no agent-cost or chargeback content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization and measurement; no spending/chargeback surface.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guardrails, pre-on-caller; no cost-accounting
  content.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  model-path guardrail scanner stacks and latency drivers; no per-agent cost
  surface.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **dismissed** (per
  triage): budget windows / fallback chains / caching for *client-side* Claude
  Code spend control; different subject from gateway-configured per-agent
  chargeback.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP /
  coding-agent integration; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: the
  manual session-correlation parallel was already drawn by the A2A gateway note
  (its Claim 2); this page is about a configured cost, not trace/session
  correlation.
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **dismissed**:
  pipeline freshness/correctness SLOs; unrelated.
- `source-notes/docs-google-sre-on-call.md` — **dismissed**: on-call shift /
  pager-load practices; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 6** (only
    `message/send` and `message/stream` traverse the gateway's A2A client —
    logging, guardrails, spend — all other methods forwarded upstream). This
    page's own verification path tests cost on `/v1/a2a/message/send` (Claim 6
    here), consistent with cost attaching on the message path rather than on
    task methods. The gateway note's Ch05 cross-route ("per-agent spend
    attribution as a second cost-attribution axis") is realized by this page.
  - `source-notes/docs-litellm-a2a-agent-card.md` — its Concrete Artifacts →
    Supported A2A methods table rows `message/send` ("Routed through LiteLLM A2A
    SDK (asend_message) — logging, guardrails, cost tracking") and
    `message/stream` ("Routed through LiteLLM streaming handler — NDJSON/SSE
    response"), with every task/push-notification method "JSON-RPC forwarded to
    upstream". Confirms the cost-tracking surface attaches only to the message
    path this page's test exercises.
- **Contradicts**: None filed. Two candidate tensions were analyzed per MINER
  §4a and the Prospector's guidance; neither rises to claim-level opposition, so
  no contradiction issue was filed:
  1. *Configured-cost vs forwarding obligation*: the gateway note's Claim 2
     (`X-LiteLLM-Agent-Id` per-agent spend requires the agent server to forward
     the header) targets *measured* spend attributed to an agent; this page's
     configured cost is *declared* and attributed to the calling key. Different
     objects, different mechanisms, and this page asserts neither that
     forwarding is required nor that configured costs bypass it — so both can be
     true simultaneously. Marked as "extends / needs cross-check" (Claim 8
     here), not a contradiction.
  2. *Scope of "each agent request"*: the cost page's "each request to this
     agent will be charged $0.05" is unqualified, while the gateway note (Claim
     6) and agent-card method table place cost on `message/send`/`message/stream`
     only. The cost page never asserts task methods are billed and its own test
     path is `message/send`, so the correct reading is a conditioning scope (per
     billable A2A request through the gateway's cardinal path), not a
     disagreement. No contradiction issue filed; verified open contradiction
     issues (#1150, #1307, #1322) do not cover this surface.
- **Extends**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 2** — this page adds
    the second, orthogonal cost axis the gateway note's Ch05 entry anticipated:
    a gateway-declared per-request charge that needs no header forwarding,
    attributed to the calling key, surfaced in a per-agent dashboard.
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — that note
    documents silent loss of *per-model measured* cost rows. This page introduces
    a *configured* price the operator types in, which is immune to cost-map
    staleness but exposed to its own drift mode: the declared per-query figure
    quietly diverging from real consumption, with no documented reconciliation
    (Claim 3 here). Both are "cost accounting diverges from reality without an
    error signal" failure classes on the same vendor's gateway.
  - `source-notes/docs-litellm-streaming-token-usage.md` — token-based agent
    pricing (Claim 2 here) consumes input/output token quantities that this page
    does not source; if that usage rides the model-path accounting the streaming
    note documents (`stream_options={"include_usage": True}` or silent-zero),
    per-token agent pricing inherits the same silent-zero exposure for streamed
    agent traffic. Cross-reference only — the cost page says nothing about the
    usage source.
  - `source-notes/docs-litellm-a2a-agent-permissions.md` — sibling from the same
    crawl batch: permissions define *who may call* an agent (key/team
    intersection, fail-open default); this page defines *what the caller is
    charged*. Together they bound the per-agent governance surface (access +
    price) an operator must configure in the dashboard.
- **Novel**: First source note in the corpus covering LiteLLM's *configured
  per-agent cost surface*: the three-field Cost Configuration panel, the
  attributed-to-calling-key chargeback model, the Agent Usage dashboard
  dimensions, and the UI-only config status. The corpus's prior cost content is
  per-model (cost map, streaming usage) or client-side (Claude Code budgets);
  nothing covered an operator-declared per-agent price, and no note covered the
  Agent Usage dashboard as an agent-traffic observability surface.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — cost/capacity)**: Recommend the chapter
  teach **two distinct cost-attribution axes** for agent traffic through a
  gateway, per this page + the gateway note (Claim 2) + the model-cost-map
  incident note: (a) *measured* spend — upstream model cost attributed per model
  and, when forwarded, per agent via `X-LiteLLM-Agent-Id`; (b) *declared*
  charge — an operator-entered flat/token price charged per billable A2A request
  and attributed to the calling key (per team/project). Add a **chargeback-
  accuracy obligation**: a declared per-query cost is a pricing statement that
  can silently drift from real consumption as token usage or model mix changes;
  the docs document no reconciliation, so the runbook check becomes "when did we
  last re-check the declared per-query cost against the agent's actual spend?"
- **Chapter 02 (Observability)**: Add the Agent Usage dashboard as an
  agent-traffic spend-analytics surface (total/daily/model-breakdown/activity
  metrics, filterable by agent ID) distinct from the model-level spend views,
  and note the attribution subtlety: the dashboard rolls up *declared charges*
  attributed to the calling key, not the agent's own backend spend — teach the
  guide's cost-attribution guidance to be explicit about which axis is being
  reported.
- **Chapter 03 (Runbooks and Agents)**: Note the config surface is UI-only on
  this page — the three cost fields have no documented config.yaml / API form, so
  per-agent pricing cannot be lifted into `config.yaml` `agents:` registration or
  IaC from these docs; price-setting stays a dashboard action. Pair with the
  gateway note's Claim 5 (declarative config agents) as the declarative/UI
  boundary for agent registration vs pricing.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/a2a_cost_tracking`, HTTP 200, no paywall). The
  page is a thin Admin-UI click-through plus three short reference sections; no
  substantive outbound links needed for verification beyond the sibling A2A notes
  already in the corpus. All `Quote` fields are character-for-character from the
  fetched page prose; the cost table, dashboard dimensions, and guidance sentence
  are preserved verbatim in Concrete Artifacts. Claims 3 and 8 encode the
  Prospector's two reconciliation questions, each marked as the Miner's synthesis
  where the page itself is silent.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  listed candidate paths are cited or dismissed above. Primary cross-reference
  verification (MINER §4b) re-read the cited claims/artifacts in
  `docs-litellm-a2a-agent-gateway.md` (Claims 2 & 6), the
  `docs-litellm-a2a-agent-card.md` method table (Concrete Artifacts →
  "Supported A2A methods"), `failure-litellm-model-cost-map-silent-fallback.md`
  (Lessons + context), and `docs-litellm-streaming-token-usage.md` (Claims 1-2),
  and confirmed the content matches what they are cited for. No claim numbers
  were invented.
- No contradiction issue filed. The two candidate tensions (configured-vs-
  forwarded cost; the unqualified "each request" scope) were verified against the
  relevant sibling notes before deciding: both resolve to orthogonal mechanisms
  or conditioning scopes, neither page asserts the opposing position, and
  verified open contradiction issues (#1150, #1307, #1322) plus CONTRADICTIONS.md
  (no A2A-cost entries) confirm no duplicate exists — see the Contradicts section
  for the resolution logic.
- The config surface is deliberately recorded as **UI-only on this page** per
  triage item 5. The Prospector's "Related" bounding was honored: A2A Agent
  Gateway and Spend Tracking were not absorbed; the note cross-references rather
  than re-extracts the gateway content.
- `confidence_overall` is `emerging`, matching the sibling A2A notes: everything
  here is documented vendor *capability* surface with concrete field names, tab
  paths, and attribution wording, but no measured overhead, no failure modes, and
  no production experience are demonstrated. `date_published` is unknown (living
  Docusaurus page); `date_extracted` and `last_checked` are both 2026-09-15.