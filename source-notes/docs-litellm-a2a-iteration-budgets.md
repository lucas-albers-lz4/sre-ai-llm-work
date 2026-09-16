---
source_url: https://docs.litellm.ai/docs/a2a_iteration_budgets
source_type: docs
title: "Agent Iteration Budgets — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-16)
date_extracted: 2026-09-16
last_checked: 2026-09-16
status: current
confidence_overall: emerging
issue: "#1331"
---

# Agent Iteration Budgets (LiteLLM Docs)

> LiteLLM's A2A gateway offers two per-session agent-loop cost controls —
> `max_iterations` (hard cap on LLM calls per session) and
> `max_budget_per_session` (dollar cap per session) — both **fail open**
> unless `require_trace_id_on_calls_by_agent` is enabled, both are
> TTL-windowed (rolling 1-hour caps, not lifetime session guarantees), both
> surface over-cap responses as **HTTP 429** with `type: budget_exceeded`
> (the same status class as ordinary rate limiting), and the page
> **contradicts itself** on whether the caps are stored on the agent's
> `litellm_params` (applied across all keys) or in the virtual key's
> metadata (filed as contradiction #1338).

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living
  page under "Agent & MCP Gateway > A2A Agent Gateway", sibling to the A2A
  Agent Gateway / Agent Card / Invoking / Authentication Headers / Cost
  Tracking / Permission Management pages).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* the gateway exposes (config keys, header
  names, env vars, error codes, storage-model statements), but documents
  capability only — no measured enforcement, no latency/throughput numbers, no
  failure writeups, no production experience report. Per the Prospector's
  bounding rule, every claim in this note stays at "the gateway documents this
  control," never "this holds at scale."
- **Scope**: Covers the two per-session controls, the two trace-id enforcement
  flags, the documented iteration/budget counter mechanics, the 429
  `budget_exceeded` response contract, the TTL env vars, and the page's
  internal storage-model contradiction. Does **not** cover per-agent cost
  *tracking* (sibling #1329), permissions (sibling #1317), the OpenAI `a2a/`
  invocation bridge (sibling #1330), or the general A2A gateway surface
  (overview note #1302).

## Extracted Claims

### Claim 1: LiteLLM's A2A gateway exposes two per-session agent-loop cost controls — `max_iterations` (hard cap on LLM calls per session) and `max_budget_per_session` (dollar cap per session, keyed on `x-litellm-trace-id`) — and both require a `session_id` to track calls within a session
- **Evidence**: The Overview paragraph introduces "two controls" as the answer
  to "unbounded LLM calls, causing unexpected costs," the control table defines
  the pair, and the closing sentence states the session requirement.
- **Confidence**: emerging (documented vendor capability surface; no measured
  enforcement)
- **Quote**: "Control runaway costs from agentic loops with per-session iteration and budget caps." / "Hard cap on the number of LLM calls per session" / "Dollar cap per session (identified by `x-litellm-trace-id`)" / "Both controls require a `session_id` (sent via `x-litellm-trace-id` header or `metadata.session_id`) to track calls within a session."
- **Our assessment**: This is the concrete "stop the agent from succeeding
  repeatedly and expensively" control the Prospector flagged Ch05/Ch03 as
  missing (the guide's error-budget content covers SLO sense and anti-toil
  automation, not per-session loop/cost caps). The fidelity note: this is a
  *documented* gateway control, not evidence the cap holds under load — nothing
  on the page measures enforcement overhead or counter accounting at scale.

### Claim 2: Session tracking is enabled by two independent trace-id flags in the agent's `litellm_params` — `require_trace_id_on_calls_to_agent` (inbound: callers must include `x-litellm-trace-id`, 400 if missing) and `require_trace_id_on_calls_by_agent` (outbound: all LLM/MCP calls made by the agent via its virtual key must carry the trace id, 400 if missing) — and the outbound flag is what actually enables `max_iterations` / `max_budget_per_session` tracking
- **Evidence**: The "Trace-ID Enforcement" table defines both flags and the
  second flag's description names the iteration/budget tracking dependency.
- **Confidence**: emerging (documented vendor behavior, with explicit 400
  responses)
- **Quote**: "Requires callers invoking this agent to include `x-litellm-trace-id`. Use when the agent should only be called as a sub-agent with a trace context. Returns **400** if missing." / "Requires all LLM/MCP calls made **by** this agent (via its virtual key) to include `x-litellm-trace-id`. This is what enables `max_iterations` and `max_budget_per_session` tracking. Returns **400** if missing."
- **Our assessment**: The dependency chain is the highest-value fact on the
  page: the caps *silently do nothing* unless the outbound flag is set. And the
  outbound flag is only meaningful if the agent's own downstream LLM/MCP calls
  actually carry the trace id — which the overview note (#1302 Claims 2) shows
  is a *forwarding obligation on the agent server*, so the budget control's
  effectiveness ultimately depends on the agent honoring gateway-set headers.
  The inbound flag (`to_agent`, 400 for callers missing a trace context) is the
  "only call this as a sub-agent" governance knob, orthogonal to the budget.

### Claim 3: The iteration control is a per-call counter — when `max_iterations` is set in agent `litellm_params`, each LLM call for a session increments a counter, and a request that pushes the counter over the cap receives a 429 Too Many Requests
- **Evidence**: The "Max Iterations" section's three bullets, stated
  conditional on `max_iterations` being set in agent `litellm_params`.
- **Confidence**: emerging (documented counter mechanics)
- **Quote**: "Each LLM call for a session increments a counter" / "When the counter exceeds `max_iterations`, the request receives a **429 Too Many Requests**"
- **Our assessment**: An *increment on call* / *reject when over* semantics —
  the 25th-and-beyond call in the page's example is rejected, i.e. the cap is
  on calls *made*, not a concurrent-loop limiter (nothing here bounds
  parallelism or in-flight calls; it is a lifetime-of-session counter windowed
  by the TTL of Claim 6).

### Claim 4: The budget control has asymmetric timing — spend is accumulated *after* each successful LLM call and checked *before* each call, so a single over-budget call reaches the provider and the excess is only rejected on the next call
- **Evidence**: The "Max Budget Per Session" bullets state the
  accumulate-after / check-before ordering explicitly.
- **Confidence**: emerging (documented check/accumulate ordering; the
  one-call-overrun implication is the Miner's reading of that ordering)
- **Quote**: "After each successful LLM call, the response cost is accumulated for the session" / "Before each call, the accumulated spend is checked against the budget" / "When spend exceeds the budget, the request receives a **429 Too Many Requests**"
- **Our assessment**: The ordering means the budget is a *soft* ceiling by one
  call: because the check runs before each call against spend accumulated only
  after successful calls, a call that crosses the line completes (and its cost
  is spent) and the 429 lands on the *next* call in the session. Operators
  should read `max_budget_per_session` as "rejects once cumulative spend has
  exceeded the cap," not "stops spend at the cap." Whether partial/streamed
  failures still accumulate is unspecified.

### Claim 5: Over-cap responses are HTTP 429 with `"type": "budget_exceeded"` and a message that embeds the session id, current spend, and the configured cap — a *cost* cap surfaces as the same status class as ordinary rate limiting and cannot be distinguished by status code alone
- **Evidence**: The JSON error body shown after "After 25 calls or $5 spent
  within this session, subsequent requests will receive:", plus the page's
  framing of the same as "a **429 Too Many Requests**".
- **Confidence**: emerging (explicit documented response body)
- **Quote**: "Session budget exceeded for session session-abc-123. Current spend: $5.0032, max_budget_per_session: $5.00." (the `message` field of the documented example error body)
- **Our assessment**: The 429 collision is the operational trap the Prospector
  flagged: callers that treat 429 as transient retryable backoff will retry a
  budget-exhausted session that will keep failing for the life of the session
  (until the TTL resets the counter — see Claim 6, which means a blind retry
  loop can burn budget only if the session_id changes on each attempt, or wait
  out the TTL to get a fresh budget). Callers must key off the `error.type ===
  "budget_exceeded"` discriminant, not the status code. The message also leaks
  current spend vs cap (`$5.0032` vs `$5.00`) — an operational fingerprint an
  on-call can grep, but also incidental information disclosure of spend amounts
  to anyone who can trigger the error.

### Claim 6: Both counters are TTL-windowed, not lifetime — iteration counters and session-spend counters expire after 1 hour by default (`LITELLM_MAX_ITERATIONS_TTL` and `LITELLM_MAX_BUDGET_PER_SESSION_TTL`, default `3600`), so a "$5 per session" cap is really a "$5 per rolling hour" cap and a long-running session silently gets its counters reset and budget replenished
- **Evidence**: The "Max Iterations" and "Max Budget Per Session" bullets plus
  the Environment Variables table (default `3600` / "1 hour" for both).
- **Confidence**: emerging (documented env-var behavior; the rolling-window
  consequence is the Miner's framing of documented defaults)
- **Quote**: "Counters expire after 1 hour by default (configurable via `LITELLM_MAX_ITERATIONS_TTL` env var)" / "Session spend counters expire after 1 hour by default (configurable via `LITELLM_MAX_BUDGET_PER_SESSION_TTL` env var)"
- **Our assessment**: The most operationally important bound on the guarantee.
  The control's name says "per session," but the counters are time-boxed:
  an agent loop still running after 1 hour has its iteration counter and
  accumulated spend reset, so a genuinely long workload gets a fresh budget
  each hour — the cap degrades exactly on the long-running workloads it was
  bought to bound. This matches the "TTL windowed, not lifetime" reading the
  Prospector requested. Runbooks should treat the two env vars as the knob that
  turns "per-session" into "per-rolling-window."

### Claim 7: Session identity is entirely caller-supplied via `x-litellm-trace-id` or `metadata.session_id`, and the page does not document any validation that the trace id is bound to the calling key or the agent — the cap is bypassable by varying the session identifier if callers control the header
- **Evidence**: The "Session Tracking" section lists exactly two caller-supplied
  mechanisms; no sentence anywhere on the page describes validating, binding,
  or minting session ids.
- **Confidence**: emerging (documented identity surface; the absence of
  validation is a verified absence, flagged per triage — the page is silent on
  whether the trace id is validated or bound)
- **Quote**: "Callers identify their session by including a `session_id` in one of these ways:" (followed by the `x-litellm-trace-id` header and `metadata.session_id` bullets)
- **Our assessment**: Recorded as an *open question the page does not answer*,
  not an assertion of exploitability: the docs show clients free to choose
  `x-litellm-trace-id: session-abc-123` (or any string) and never state how
  (or whether) LiteLLM authenticates that identity against the calling key or
  agent. If session ids are unvalidated, a caller can dodge the cap simply by
  varying the header per attempt; if they are validated server-side, the doc
  should say so. Neither is asserted here.

### Claim 8: The page contradicts itself on where the budget controls are stored — the "Configuring via UI" section says they live in the virtual key's metadata, while the "Configuring via API" section says they live on the agent's `litellm_params` (not on individual keys, applying across all keys) — determining whether the cap is per-agent or per-key
- **Evidence**: The two storage-model sentences, both on the same page in
  code-adjacent context, plus the API example bodies (caps nested in the
  agent's `litellm_params` on `POST /v1/agents`) and the UI step flow
  ("Proceed to create a new key for the agent" as a separate step).
- **Confidence**: emerging (two directly contradictory documented statements)
- **Quote**: "The trace-id flags are stored on the agent's `litellm_params`. Budget controls (`max_iterations`, `max_budget_per_session`) are stored in the virtual key's metadata." / "Budget controls are set on the agent's `litellm_params` (not on individual keys), so they apply across all keys for the agent"
- **Our assessment**: Filed as **contradiction issue #1338** per MINER §4a
  (same-source disagreement — a source disagreeing with itself). The two models
  have different blast radii: agent-`litellm_params` storage makes the cap
  apply across every key that calls the agent (per-agent), while virtual-key
  metadata storage makes it per-key (bypassable or independently exhausted via
  additional keys). No verdict picked here — the resolver must decide. Note the
  API path's example is self-consistent with per-agent storage (budget set at
  agent creation, key minted afterward in a separate `/key/generate` call), and
  the "How It Works" sections both read the caps from "agent `litellm_params`" —
  so the API/How-It-Works sections cohere and the UI section is the outlier.

### Claim 9: The controls are configured through the same `litellm_params` block as the trace-id flags via `POST /v1/agents`, with `max_iterations` and `max_budget_per_session` set alongside `require_trace_id_on_calls_by_agent` — the page's documented configurable form is agent-creation-time, not per-call
- **Evidence**: The "Configuring via API" curl example bodies show the exact
  nesting; the UI steps set the same values in Agent Settings → Tracing.
- **Confidence**: emerging (documented configuration surface with explicit
  example bodies)
- **Quote**: the API example setting `"max_iterations": 25`, `"max_budget_per_session": 5.00` inside `litellm_params` (see Concrete Artifacts)
- **Our assessment**: Configuration is agent-scoped at creation time on the
  documented API path — there is no per-call or per-session budget override
  surface on this page (config lives with the agent definition, and how it
  composes with per-key/per-team LLM-proxy limits from the rest of LiteLLM is
  the open composition question the overview note left at #1302 Claim 7: "the
  page does not show interactions"). The page also never states whether the
  budget applies to the `a2a/` chat-completions bridge (sibling #1330) — a
  second open composition gap.

## Concrete Artifacts

All artifacts verbatim from the fetched page.

### Control table (from "Overview", verbatim)

```
Control                       Description
Max Iterations                Hard cap on the number of LLM calls per session
Max Budget Per Session        Dollar cap per session (identified by x-litellm-trace-id)
```

### API agent creation with both controls (from "Configuring via API", verbatim — budget + iteration caps nested in `litellm_params`)

```bash
curl -X POST 'http://localhost:4000/v1/agents' \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_name": "my-research-agent",
    "agent_card_params": {
      "name": "my-research-agent",
      "description": "A research agent with budget controls",
      "url": "http://my-agent:8080",
      "version": "1.0.0"
    },
    "litellm_params": {
      "require_trace_id_on_calls_by_agent": true,
      "max_iterations": 25,
      "max_budget_per_session": 5.00
    }
  }'
```

### Session-tracking call (from "Making Calls with Session Tracking", verbatim)

```bash
curl -X POST 'http://localhost:4000/chat/completions' \
  -H 'Authorization: Bearer sk-agent-key-xxx' \
  -H 'x-litellm-trace-id: session-abc-123' \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gpt-5.6-terra",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

Session identity alternatives (verbatim): `x-litellm-trace-id: my-session-123`
(header) or `{"metadata": {"session_id": "my-session-123"}}` (metadata).

### Over-cap response (from "Example → Making Calls with Session Tracking", verbatim)

> "After 25 calls or $5 spent within this session, subsequent requests will receive:"

```json
{
  "error": {
    "message": "Session budget exceeded for session session-abc-123. Current spend: $5.0032, max_budget_per_session: $5.00.",
    "type": "budget_exceeded",
    "code": 429
  }
}
```

### Environment variables (from "Environment Variables" table, verbatim)

```
Variable                             Default         Description
LITELLM_MAX_ITERATIONS_TTL            3600 (1 hour)   TTL in seconds for session iteration counters
LITELLM_MAX_BUDGET_PER_SESSION_TTL    3600 (1 hour)   TTL in seconds for session budget counters
```

### UI configuration steps (from "Configuring via UI" and "Example → Via UI", condensed verbatim)

```
1. Navigate to the Agents tab and click Add Agent
2. In the Agent Settings step, expand the Tracing section
3. Toggle "Require x-litellm-trace-id on calls BY this agent" to enable session tracking
4. Set Max Iterations to cap the number of LLM calls per session
5. Set Max Budget Per Session ($) to cap spend per session
6. Proceed to create a new key for the agent
7. Click Create Agent
```

UI storage model note (verbatim): "The trace-id flags are stored on the agent's
`litellm_params`. Budget controls (`max_iterations`, `max_budget_per_session`)
are stored in the virtual key's metadata." — versus the API section's "Budget
controls are set on the agent's `litellm_params` (not on individual keys), so
they apply across all keys for the agent" (see Claim 8 / contradiction #1338).

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-a2a-agent-gateway.md` — **cited** (Corroborates,
  Contradicts-data-point, Extends — see below). Primary reference note.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **cited** (Corroborates,
  Extends — see below).
- `source-notes/docs-litellm-a2a-agent-card.md` — **cited** (Corroborates one
  surfaced interaction — see below), otherwise its served-card field matrix /
  skill-routing content is **dismissed** as unrelated to budget caps.
- `source-notes/docs-litellm-a2a-invoking-agents.md` — **cited** (Corroborates
  — the "docs are silent on gateway controls" gap, see below).
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors and debuggability rationale; no agent session budget content.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP /
  coding-agent integration; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **cited** (Corroborates
  the manual/caller-supplied session-correlation principle — see below).
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **dismissed**:
  pipeline freshness/correctness SLOs; unrelated to session budget caps.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization/measurement; unrelated.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guardrails, pre-on-caller; no per-session budget
  or gateway cap content.

Additional cross-references found by searching `source-notes/`:

- `source-notes/docs-litellm-a2a-agent-permissions.md` — **cited**
  (Corroborates the fail-open-default structural parallel — see below).

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 7** (per-agent
    trace-ID enforcement via `require_trace_id_on_calls_to_agent` /
    `require_trace_id_on_calls_by_agent`, HTTP 400 if missing). This page is the
    dedicated sub-page for the budget half of that enforcement surface: it gives
    the same two flags with the same 400 semantics, and states the dependency
    (outbound flag "enables `max_iterations` and `max_budget_per_session`
    tracking") the overview note identified without detail.
  - `source-notes/docs-litellm-helicone-integration.md` **Claim 2** (Helicone
    session correlation is caller-supplied per-request context —
    `Helicone-Session-Id` / `Helicone-Session-Path` set by the app, "nothing
    auto-propagates them"). This page's session identity is the same shape and
    the same manual obligation: the session is whatever string the caller puts
    in `x-litellm-trace-id` / `metadata.session_id`, and enforcement
    (Claim 7 here) depends on that caller-supplied value reaching the gateway —
    with the extra wrinkle that the budget *also* depends on the agent's own
    downstream calls carrying the trace id back (depends on the overview's
    forwarding obligation, #1302 Claim 2).
  - `source-notes/docs-litellm-a2a-agent-permissions.md` **Claim 1** (per-agent
    permission resolution is fail-open by default — unconfigured key/team can
    access all agents). Same governance shape as this page's budget controls:
    unconfigured = no limit (no iteration cap, no budget cap, no inbound/outbound
    trace enforcement). Both pages document a control that silently does nothing
    in its default state.
  - `source-notes/docs-litellm-a2a-agent-card.md` Concrete Artifacts →
    "Supported A2A methods" (message/send and message/stream routed through the
    gateway's A2A client with "logging, guardrails, cost tracking"). This page's
    per-session budget is charged against the agent's *LLM/MCP calls* (the
    outbound trace-id flag covers "all LLM/MCP calls made by this agent via its
    virtual key"), i.e. a different accounting object than the per-query agent
    cost tracked on the message path — the two cost axes must not be conflated.
- **Contradicts**:
  - Filing **#1338** (filed before this PR per MINER §4a): this page's
    "Configuring via UI" section ("Budget controls ... are stored in the virtual
    key's metadata") vs its own "Configuring via API" section ("Budget controls
    are set on the agent's `litellm_params` (not on individual keys)"). Same
    vendor, same page, mutually exclusive storage models with different blast
    radii (per-key vs per-agent). This note records both quotes and picks no
    verdict (Claim 8). Related open contradiction **#1322** (A2A served-card
    path naming, overview vs agent-card notes) is the same class of vendor-doc
    self-inconsistency already being tracked for this page family.
  - No claim-level opposition with any existing *source note*: the cost-tracking
    note (#1329) Chargeback model and this page's budget cap are orthogonal axes
    (declared charge attributed to calling key vs enforced spend cap per
    session-tagged agent calls); neither note asserts the other is absent. The
    overview note's claim that iteration budgets are one of the four gateway
    features (#1302 Claim 1) is detailed, not opposed, here.
- **Extends**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` — answers part of the
    overview note's open question (Claim 7 assessment: "Worth checking whether
    iteration budgets and admin-defined static credentials compose with the
    per-key limits — the page does not show interactions") for the
    iteration-budget half: per the API section, budgets are set on the agent's
    `litellm_params` and "apply across all keys for the agent" (this note
    Claim 8) — but the contradiction (UI section, virtual-key metadata) and the
    untouched per-key/per-team LLM-proxy-limit composition mean the overview's
    question is only *partially* answered; the composition with per-key limits
    remains open. Also extends #1302 Claim 2 (the forwarding obligation) with
    the dependency chain: budget enforcement only has teeth if the agent sends
    its own calls back with the trace id, and that forwarding is not
    guaranteed.
  - `source-notes/docs-litellm-a2a-cost-tracking.md` — adds a third cost
    surface to the two axes that note already mapped (measured per-agent spend
    via `X-LiteLLM-Agent-Id`, declared per-query charge): an *enforced per
    session-tagged spend cap* with accumulate-after/check-before mechanics and a
    429 `budget_exceeded` contract. The two notes together give Ch05 a
    complete-ish cost surface for agent traffic: attribution axes + a cap.
  - `source-notes/docs-litellm-a2a-invoking-agents.md` **Claim 3** (the docs are
    silent on whether the `a2a/` chat-completions bridge is logged,
    spend-attributed, or guardrailed) — the iteration-budget page is *also*
    silent on whether `a2a/` bridge calls count toward `max_iterations` /
    `max_budget_per_session`, and on whether non-`message/*` A2A method traffic
    (task polling etc.) triggers the caps. Same "documented absence" class; the
    guide should treat the budget's interaction surface as partially
    unverified, not fully documented.
- **Novel**: First source note in the corpus covering *per-session* agent-loop
  cost/iteration caps at a gateway: the `max_iterations` /
  `max_budget_per_session` control pair, the fail-open dependency on
  `require_trace_id_on_calls_by_agent`, the 429 `budget_exceeded` response
  contract with its rate-limit-status collision, the TTL-windowed counter
  semantics (`LITELLM_MAX_*_TTL`, rolling-1-hour not lifetime), the
  caller-supplied session identity, and the accumulate-after/check-before budget
  mechanics. The corpus's prior cost content is attribution/measurement-focused
  (per-model cost map, per-agent declared charge, streaming usage) — nothing
  covered *enforcement* of a per-session ceiling.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — cost, capacity, fallback patterns)**:
  Add per-session cost/iteration caps for agentic execution as a distinct
  failure mode the chapter does not yet cover (the chapter's error-budget
  content is SLO/canary/anti-toil; it does not cover "the agent is not failing,
  it is succeeding repeatedly and expensively"). Concrete mechanics to teach
  from this page: (1) the cap is **fail-open** unless the outbound trace-id
  flag is set (Claim 2); (2) budget is checked *before* each call and
  accumulated *after* successful ones, so it rejects one call late, not the
  crossing call (Claim 4); (3) over-cap errors are **HTTP 429 with
  `type: budget_exceeded`** — callers must key off the error type, not the
  status code, because retry-on-429 on a budget-exhausted session keeps failing
  for the session lifetime (Claim 5); (4) the cap is **TTL-windowed** — `$5 per
  session` is `$5 per rolling hour`, and a session longer than the TTL silently
  gets a fresh budget (Claim 6). Add a runbook check: "is the budget stored
  per-agent or per-key?" — the docs contradict themselves (Claim 8 → #1338),
  so the blast radius is ambiguous until resolved.

- **Chapter 03 (Runbooks and Agents)** — §"Automation-safety baseline for
  agents" / "The emerging agent control plane": Add the gateway-side agent-loop
  guard as the control-plane "govern" verb made concrete — an iteration cap and
  a dollar cap enforced at the gateway rather than inside the agent. But pair
  it with the dependency caveat: enforcement silently depends on
  `require_trace_id_on_calls_by_agent` *and* on the agent server forwarding the
  trace id on its own downstream calls (ties to #1302 Claim 2's forwarding
  obligation), so "gateway enforces the budget" is really "gateway enforces the
  budget only if the agent cooperates on trace propagation." Add the
  caller-controlled session identity caveat (Claim 7): a client that can mint
  its own `x-litellm-trace-id` can present a fresh session and a fresh budget
  unless the gateway validates the id — flagged as an open question the docs do
  not answer.

- **Chapter 02 (Observability)** — cost/usage signals: Add the 429
  `budget_exceeded` response as a grep-able signal (message leaks current spend
  vs cap, e.g. `Current spend: $5.0032, max_budget_per_session: $5.00`) and as
  a *non-transient* 429 distinct from rate-limit backoff — an alert split by
  `error.type` rather than status class. Note the counters' TTL (1-hour window)
  so spend dashboards interpret "budget reset" events correctly for long
  sessions (Claim 6).

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/a2a_iteration_budgets`, HTTP 200, no paywall),
  then re-fetched as raw HTML to verify all `Quote` fields and both code blocks
  character-for-character. The page is a focused topic page (~120 lines of
  substantive content); all running-text quotes are contiguous verbatim strings
  from the fetched page prose. The one table row quoted across cells
  ("Configuring via API") is preserved as the page renders it.
- Prospector triage bounding honored (#1331, `triaged:text`,
  `priority:medium`). Extraction priority followed the Prospector's numbered
  items: the two controls + storage/semantics (Claims 1, 8, 9), the enforcement
  response contract incl. the 429/rate-limit collision (Claims 4, 5), the TTL
  expiry failure mode (Claim 6), caller-controlled session identity as an open
  question the page does not answer (Claim 7), and the internal doc
  contradiction (Claim 8 → **#1338**). The vendor-docs caveat is carried: every
  claim stays at "the gateway documents this control," TTL behavior and
  fail-open default are documented facts, and nothing here asserts the caps
  hold at scale or that counter expiry is observable.
- **Contradiction filed before this PR, per MINER §4a**: #1338 — the page's
  UI section (budget controls stored in the virtual key's metadata) vs its API
  section (budget controls on the agent's `litellm_params`, across all keys).
  Both quotes recorded in Claim 8; no verdict picked. A sibling contradiction
  (#1322, served-card path naming) is the same class of vendor-doc
  self-inconsistency and is cross-referenced, not duplicated.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Primary cross-reference
  verification (MINER §4b) re-read the cited claims/artifacts in
  `docs-litellm-a2a-agent-gateway.md` (Claims 1, 2, 7), `docs-litellm-a2a-cost-tracking.md`
  (Claims 1-8), `docs-litellm-a2a-agent-card.md` (Concrete Artifacts →
  "Supported A2A methods"), `docs-litellm-a2a-invoking-agents.md` (Claim 3),
  `docs-litellm-a2a-agent-permissions.md` (Claim 1), and
  `docs-litellm-helicone-integration.md` (Claim 2) — content confirmed against
  what they are cited for. No claim numbers invented.
- Open questions deliberately left open (not asserted): (a) whether the trace-id
  session identity is validated/bound to the caller (Claim 7); (b) whether the
  budget applies to the `a2a/` chat-completions bridge and to non-`message/*`
  A2A methods (links to #1330 Claim 3's silent-bridge finding); (c) the
  composition of these caps with per-key/per-team LLM-proxy limits from the
  overview note (#1302 Claim 7, partially answered per Claim 8 here).
- `confidence_overall` is `emerging`, matching the sibling A2A notes
  (#1302/#1315/#1317/#1329/#1330): documented vendor *capability* surface with
  concrete config keys, env vars, and error codes, but no measured enforcement,
  no failure writeups, and no production experience. `date_published` is unknown
  (living Docusaurus page); `date_extracted` and `last_checked` are both
  2026-09-16.