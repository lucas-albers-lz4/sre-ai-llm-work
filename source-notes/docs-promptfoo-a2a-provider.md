---
source_url: https://www.promptfoo.dev/docs/providers/a2a
source_type: docs
title: "Promptfoo A2A Provider — Task-Shaped Agent Evaluation, the HTTP+JSON-Only Binding, and the 5-Minute Polling Stall"
author: "Promptfoo (vendor documentation; page footer last updated 2026-11-07 by Naveen Chatlapalli)"
date_published: 2026-11-07
date_extracted: 2026-11-07
last_checked: 2026-11-07
status: current
confidence_overall: emerging
issue: "#1961"
---

# Promptfoo A2A Provider

> Promptfoo's first-party page for driving an Agent2Agent (A2A) agent as an
> eval/red-team provider: the provider sends each test prompt as an A2A message
> and extracts only a final text result, supports **only** the HTTP+JSON REST
> binding (JSON-RPC, gRPC, and push-notification webhooks are unsupported), and
> ships a send-and-poll path whose defaults — 1000 ms interval, 300000 ms
> timeout — turn a stuck agent into a five-minute stall per prompt while
> documenting no poll-attempt or task-state history in the result metadata
> unless `transformResponse` promotes it.

## Source Context

- **Type**: docs (vendor provider reference page —
  `https://www.promptfoo.dev/docs/providers/a2a`, in the Providers nav section;
  footer "Last updated on **Nov 7, 2026** by **Naveen Chatlapalli**").
- **Author credibility**: Promptfoo, the LLM eval/red-team vendor, documenting
  its own shipped `a2a` provider. The configuration option table, default
  values, endpoint paths, auth schemes, output-extraction order, and error list
  are checkable against the tool, so the mechanics claims are authoritative.
  The page reports **no** run metrics, no latency data beyond the configured
  defaults, no failure writeup, and no production experience report; every
  efficacy-adjacent statement is vendor assertion. The security implications in
  `Our assessment` are the Miner's inference from the documented surface.
- **Scope**: The A2A provider's contract — setup and supported bindings, Agent
  Card discovery, the full configuration option table, auth (bearer/basic/API
  key/OAuth), request modes (`auto`/`send`/`stream`), custom messages,
  `transformResponse`, output-extraction priority, red-team usage, error
  handling, and limitations. It does **not** document A2A gateway-side
  registration/authorization (LiteLLM's side; covered by sibling notes), task
  budget/cost controls, or any per-poll observability surface.
- **Sub-pages followed** (per MINER.md §1): none. The page is self-contained;
  its outbound links are the A2A specification, the A2A definitions page, the
  MCP provider, the HTTP provider, and the red-team guide — none adds
  substantive detail about this provider's contract, and the A2A/red-team
  siblings already have notes in the corpus (cited below).

## Extracted Claims

### Claim 1: The `a2a` provider treats an A2A agent as a promptfoo provider — each test prompt becomes an A2A message, and the eval consumes the final extracted text rather than the task lifecycle
- **Evidence**: The page intro states the purpose and the three-step flow
  (send message → wait for response/task completion → extract final text). The
  Output Extraction section then defines what "final text" means.
- **Confidence**: settled (shipped provider behavior)
- **Quote**: "The `a2a` provider allows you to use agents that implement the Agent2Agent protocol directly as providers in promptfoo." and "Promptfoo sends each test prompt as an A2A message, waits for the agent to respond or complete a task, and extracts the final text from the A2A response."
- **Our assessment**: This is the load-bearing inversion for Ch05: promptfoo
  normally evaluates an LLM endpoint, but here the *unit under test* is an
  entire task-shaped agent behind a protocol. That is a better fit than a
  chat-completions wrapper (which LiteLLM's bridge uses and which structurally
  loses task state — see `docs-litellm-a2a-invoking-agents.md` Claim 2), but the
  eval still only *scores* the extracted text by default. The task lifecycle is
  available to assertions only insofar as `transformResponse` promotes it
  (Claim 12).

### Claim 2: Only the A2A HTTP+JSON REST binding is supported — JSON-RPC, gRPC, and push-notification webhooks are explicitly unsupported, so an agent that advertises only those bindings is silently unreachable through this provider
- **Evidence**: The Setup section enumerates the four supported endpoints and
  then makes three explicit non-support statements; the Limitations section
  repeats two of them.
- **Confidence**: settled (explicit vendor non-support statement)
- **Quote**: "JSON-RPC, gRPC, and push-notification webhooks are not supported in this provider yet."
- **Our assessment**: This answers the Prospector's key question (a). A2A's
  canonical wire binding is JSON-RPC, and LiteLLM's gateway is built around
  JSON-RPC forwarding (`docs-litellm-a2a-agent-card.md` Claim 7). An agent that
  publishes a JSON-RPC-only card in its `supportedInterfaces` will not be
  selectable by promptfoo even though a LiteLLM gateway in front of it could
  route JSON-RPC just fine. The failure is not a loud protocol error at
  discovery time for a bare `url`; the provider simply has no transport for it.
  Treat "which A2A binding does the agent actually expose" as a provider
  selection gate, not a runtime detail.

### Claim 3: Agent Card discovery selects the first supported interface with `protocolBinding: HTTP+JSON` and inherits its URL, tenant, protocol version, and streaming capability unless the config overrides them
- **Evidence**: The Agent Card Discovery section states the selection rule and
  the inherited fields; the config table documents `tenant` and
  `protocolVersion` as overridable.
- **Confidence**: settled (documented selection behavior)
- **Quote**: "When an Agent Card is configured, promptfoo selects the first supported interface with `protocolBinding: HTTP+JSON` and uses its URL, tenant, protocol version, and streaming capability unless you explicitly override them in `config`."
- **Our assessment**: "First supported interface" is an ordering rule the page
  does not qualify: if an agent card lists multiple `HTTP+JSON` interfaces, the
  winner is whichever appears first, and `protocolVersion` defaults to `1.0`
  independently of what the card advertised (Claim 6 table). This is the
  client-side mirror of the gateway-side protocol-pinning footgun in
  `docs-litellm-a2a-agent-gateway.md` Claim 4: discovery is not negotiation, and
  the page gives the operator no preview of which interface was chosen. For
  Ch05, log/assert the resolved endpoint and version rather than assuming the
  card's first-listed or latest interface won.

### Claim 4: Agent Card metadata is injected into red-team generation context — the target agent's own self-description (name, description, capabilities, skills) becomes input to the attack generator
- **Evidence**: The intro's "add advertised skills to red team generation
  context" sentence, restated and expanded in the Red Team Testing section, plus
  the explicit analogy to MCP-discovered tools.
- **Confidence**: emerging (documented behavior; the trust implication is the
  Miner's inference)
- **Quote**: "During red team generation, promptfoo also extracts useful Agent Card metadata such as the agent name, description, capabilities, and skills. This gives the attack generator more target-specific context, similar to how the MCP provider uses discovered tools."
- **Our assessment**: Answers the Prospector's key question (e) and is the
  highest-value security finding on the page. An Agent Card is attacker-
  influenced input in the untrusted-agent case: an agent (or a compromised
  well-known endpoint) can write skill descriptions intended to steer the
  generator — toward verbose/expensive probes, away from the skills that are
  actually vulnerable, or into prompt-injection text carried straight into the
  attack-generation prompt. The page frames this only as a quality improvement
  ("more target-specific context"), not as an injection surface. Ch06 should
  treat a remote Agent Card as data, not instructions, when it feeds a
  generator — the same rule the corpus applies to any externally supplied
  context that reaches an LLM prompt.

### Claim 5: `mode: auto` chooses streaming only when the Agent Card advertises streaming support; with only a bare `url` it falls back to `message:send` because there is no capability metadata
- **Evidence**: The Auto Mode subsection and its explicit fallback sentence;
  the config table's `mode` default of `auto`.
- **Confidence**: settled (documented selection behavior)
- **Quote**: "If you configure only `url` and no Agent Card, `auto` uses `message:send` because promptfoo has no capability metadata to indicate that streaming is supported."
- **Our assessment**: Answers the Prospector's key question (b). The default
  silently picks the weaker transport: without a card, streaming is never
  attempted, so latency/partial-output behavior differs between two configs
  that look equivalent. This is a conditioning variable worth recording in the
  eval config: "streaming tested" is only true when `mode: stream` is explicit
  or a card advertises streaming — a bare-`url` `auto` run tells you nothing
  about the agent's stream path.

### Claim 6: The send-and-poll path defaults to polling every 1000 ms with a 300000 ms timeout, and a non-terminal task is polled until completion, failure, cancellation, rejection, or an input/auth requirement
- **Evidence**: The Configuration Options table (`polling.enabled` true,
  `polling.intervalMs` 1000, `polling.timeoutMs` 300000) and the Send and Poll
  subsection's termination sentence and example config.
- **Confidence**: settled (documented defaults and behavior)
- **Quote**: "If the response returns a non-terminal task, promptfoo polls `GET /tasks/{id}` until the task completes, fails, is canceled, is rejected, or requires more input/authentication."
- **Our assessment**: This is the Prospector's central question. Yes — a stuck
  agent turns one eval case into a five-minute stall per prompt by default: the
  300000 ms cap at a 1000 ms interval allows up to ~300 polls before the
  provider errors out (Claim 13). In a suite of N prompts that hit the timeout,
  wall-clock grows as N × 5 min with no parallelism implied by the page. The
  default is not wrong for a synchronous eval harness, but it must be sized
  against the suite and the agent's real p95 task duration; a lower
  `polling.timeoutMs` is the only documented dial.

### Claim 7: Poll attempts and intermediate task states are not documented as result metadata — the only documented way to surface task id/state/mode into eval output is `transformResponse`
- **Evidence**: The Output Extraction section defines a five-step final-text
  priority and says structured data "remains available through `raw`,
  `metadata.a2a`, and `transformResponse`"; the Structured output example
  explicitly promotes `taskId`, `state`, and `eventCount` via a transform. The
  page documents no poll counter, attempt log, or state history field.
- **Confidence**: emerging (the absence is an argument from silence; the
  transform escape hatch is documented)
- **Quote**: "Text parts are joined with newlines. Structured data remains available through `raw`, `metadata.a2a`, and `transformResponse`."
- **Our assessment**: Answers the second half of the Prospector's central
  question. Poll *attempts* vanish: a 5-minute stall and a 1-second completion
  produce the same shape of result unless the operator writes a transform. The
  task *state* is recoverable (`raw`, `metadata.a2a`, or a `transformResponse`
  that reads `json.task?.status?.state`), but the number of polls and the
  sequence of non-terminal states are not a documented field. For Ch02, "the
  eval failed" cannot distinguish your agent was slow from promptfoo polled the
  wrong task/endpoint without a transform; instrument the transform or accept
  the blind spot.

### Claim 8: OAuth discovery from the A2A server URL requires the token endpoint to share the server's origin and rejects redirects, so an agent fronted by a separate IdP is only configurable by setting `tokenUrl` explicitly
- **Evidence**: The OAuth 2.0 subsection's discovery rule and its remedy; the
  example sets `tokenUrl` to a different origin.
- **Confidence**: settled (documented discovery constraint)
- **Quote**: "If `tokenUrl` is omitted, promptfoo tries OAuth authorization-server metadata discovery from the A2A server URL. A discovered token endpoint must share that URL's origin, and redirects are rejected; set `tokenUrl` for an identity provider on another origin."
- **Our assessment**: Answers the Prospector's key question (c). This is a
  silent-ish failure mode: the A2A URL and the IdP are commonly on different
  origins (the page's own example is `agent.example.com` vs
  `auth.example.com`), so the "just works" discovery path fails exactly where
  real deployments are split. It is not silent if the provider errors, but the
  page documents no specific error text — the operator's runbook should set
  `tokenUrl` explicitly whenever the IdP is not same-origin, and should not rely
  on discovery following a redirect to an identity host.

### Claim 9: When a bare `headers.Authorization` and `auth` both produce an `Authorization` header, `auth` wins — an ordering rule that can mask a hand-set header
- **Evidence**: The Authentication section's closing precedence sentence; the
  `headers` config field is documented as sent to both card and operation
  requests.
- **Confidence**: settled (documented precedence)
- **Quote**: "If both `headers.Authorization` and `auth` produce an `Authorization` header, the `auth` header wins."
- **Our assessment**: Answers the Prospector's key question (d). This is the
  kind of precedence rule that produces a confusing auth failure: an operator
  sets a custom `headers.Authorization` (say, an upstream token), configures
  `auth` for something else, and the custom header is silently overridden. It
  also means a misconfigured `auth` block cannot be "patched" from `headers`.
  Ch06's "declare, don't infer" credential-routing rule applies: pick one
  channel for the `Authorization` header and assert what was actually sent.

### Claim 10: `auth` applies to both Agent Card discovery requests and A2A operation requests, so the credential is presented to the well-known card endpoint as well as the operation endpoint
- **Evidence**: The Authentication section's opening sentence; the config
  table describes `headers` as sent to both endpoints too.
- **Confidence**: settled (documented behavior)
- **Quote**: "Use `auth` for common authentication schemes. Promptfoo applies it to both Agent Card discovery requests and A2A operation requests."
- **Our assessment**: Important for least-privilege review: an API key or OAuth
  token configured for operations is also sent to `/.well-known/agent-card.json`.
  If the card endpoint is served by a different trust domain or a CDN, that is a
  credential-exposure path the operator may not expect. Record the card URL's
  host as part of the credential's blast radius during review.

### Claim 11: Streaming is consumed into a single final `ProviderResponse`; stream events include `message`, `task`, `statusUpdate`, and `artifactUpdate`, but token-by-token UI streaming is not exposed
- **Evidence**: The Streaming subsection and the Limitations bullet; the config
  table lists `mode: stream`.
- **Confidence**: settled (documented behavior)
- **Quote**: "Use `mode: stream` to call `POST /message:stream` and consume Server-Sent Events (SSE). Promptfoo returns one final `ProviderResponse` when the stream closes or a terminal task state is reached." and "Streaming is consumed into a single final `ProviderResponse`; token-by-token UI streaming is not exposed"
- **Our assessment**: The stream path gives lower time-to-first-byte for the
  underlying call but not a streaming *eval* surface: assertions still see one
  final response. The page names the event types but does not document whether
  `statusUpdate` events are preserved for assertions; per Claim 7 they are only
  recoverable through `transformResponse`/`raw`. Do not read "supports streaming"
  as "the eval sees partial progress."

### Claim 12: `transformResponse` is the documented escape hatch for reshaping A2A results — it receives `(json, text, context)` and may return a primitive (sets `output`) or a full `ProviderResponse` carrying `metadata`, `guardrails`, or `sessionId`
- **Evidence**: The Response Transforms section (three arguments, return-shape
  rule), the structured-output example promoting task id/state/event count, and
  the config table's `transformResponse` type (`string | Function`).
- **Confidence**: settled (documented transform contract)
- **Quote**: "Return a primitive value to set `output`, or return a full `ProviderResponse` object when you need fields such as `metadata`, `guardrails`, or `sessionId`."
- **Our assessment**: This is the only documented observability lever on the
  agent path. It is consequential: a transform can promote `json.task?.id`,
  `json.task?.status?.state`, event counts, and `context.mode` into
  `metadata` — i.e., the eval author decides what is auditable. It can also set
  `guardrails` and `sessionId`, which means the transform is not purely
  presentational; it influences downstream control flow. For Ch02/Ch05, treat
  the transform as eval code under review, not a formatting nicety.

### Claim 13: The provider returns provider errors for non-2xx responses, invalid JSON, malformed SSE, failed/canceled/rejected tasks, tasks requiring input/auth, and polling timeout — but the timeout is the only documented client-side cancellation bound
- **Evidence**: The Error Handling section's six bullets; the Limitations
  section's streaming and binding bullets.
- **Confidence**: settled (documented error classes)
- **Quote**: "The A2A provider returns provider errors for common failure cases:" and "Polling exceeds `polling.timeoutMs`"
- **Our assessment**: A timeout surfaces as a generic provider error, not a
  categorized "agent too slow" signal; combined with Claim 7, the eval result
  does not tell you how many polls ran or which state the task was in. The page
  documents no per-request cancellation/abort knob beyond `polling.timeoutMs`
  and the generic `timeoutMs` HTTP timeout, and no retry/circuit-breaker story.
  Treat "agent eval failed" as requiring a transform or external trace to
  classify.

### Claim 14: By default the provider sends a `ROLE_USER` message with one text part containing the prompt, adds a stable `messageId`, and maps `sessionId` to the A2A `contextId` when available
- **Evidence**: The Custom Messages section's default-shape sentence and the
  Nunjucks/session sentence.
- **Confidence**: settled (documented default request shape)
- **Quote**: "By default, promptfoo sends a `ROLE_USER` message with a single text part containing `{{prompt}}`." and "It also adds a stable `messageId` and uses `sessionId` as the A2A `contextId` when available."
- **Our assessment**: The default request is single-turn text. Multi-turn or
  structured A2A conversations require a custom `message` template; the page
  documents no automatic conversation-state management across test cases, and
  `sessionId` reuse is the only documented continuity hook. Relevant to Ch05's
  multi-turn eval caveat (`guide/05-llm-ops-reliability.md:610`): if the harness
  does not carry context, a multi-turn eval is really a sequence of independent
  prompts unless the message template encodes history.

## Concrete Artifacts

### Configuration option table (source: "Configuration Options", verbatim values)

```
Option                  Type                        Default       Description
url                     string                      -             Base URL for the A2A HTTP+JSON interface
agentCardUrl            string                      -             URL of the Agent Card used for endpoint and capability discovery
auth                    object                      -             Bearer, basic, API key, or OAuth authentication configuration
headers                 Record<string, string>      {}            Headers sent to the Agent Card endpoint and A2A operation requests
mode                    auto | send | stream        auto          Whether to call message:send, message:stream, or choose automatically
tenant                  string                      -             Tenant override. Defaults to the selected Agent Card interface tenant
protocolVersion         string                      1.0           Value for the A2A-Version header
polling.enabled         boolean                     true          Poll non-terminal tasks returned by message:send
polling.intervalMs      number                      1000          Delay between GET /tasks/{id} polls
polling.timeoutMs       number                      300000        Maximum time to wait for task completion
message                 object                      -             Custom A2A message template
configuration           object                      -             A2A message configuration sent with each request
metadata                object                      -             JSON metadata sent with each message request
transformResponse       string | Function           -             JavaScript transform for reshaping the final provider response
timeoutMs               number                      -             Per-request HTTP timeout. Defaults to promptfoo's provider request timeout.
```

### Basic configuration (source: "Basic Configuration", verbatim)

```yaml
providers:
  - id: a2a:https://agent.example.com/a2a/v1
    config:
      auth:
        type: bearer
        token: '{{ env.A2A_API_KEY }}'
```

"The `a2a:<url>` shorthand sets `config.url`. Promptfoo appends the operation paths, such as `/message:send`, `/message:stream`, and `/tasks/{id}`, to this base URL."

### Agent Card discovery config (source: "Agent Card Discovery", verbatim)

```yaml
providers:
  - id: a2a
    config:
      agentCardUrl: https://agent.example.com/.well-known/agent-card.json
      auth:
        type: bearer
        token: '{{ env.A2A_API_KEY }}'
      mode: auto
```

### Send-and-poll config with the documented defaults (source: "Send and Poll", verbatim)

```yaml
providers:
  - id: a2a:https://agent.example.com/a2a/v1
    config:
      mode: send
      polling:
        enabled: true
        intervalMs: 1000
        timeoutMs: 300000
```

### Streaming config (source: "Streaming", verbatim)

```yaml
providers:
  - id: a2a:https://agent.example.com/a2a/v1
    config:
      mode: stream
```

### OAuth with an out-of-origin IdP (source: "OAuth 2.0", verbatim)

```yaml
providers:
  - id: a2a:https://agent.example.com/a2a/v1
    config:
      auth:
        type: oauth
        grantType: client_credentials
        tokenUrl: https://auth.example.com/oauth/token
        clientId: '{{ env.A2A_CLIENT_ID }}'
        clientSecret: '{{ env.A2A_CLIENT_SECRET }}'
        scopes:
          - a2a.send
```

### Custom message + metadata (source: "Custom Messages", verbatim)

```yaml
providers:
  - id: a2a:https://agent.example.com/a2a/v1
    config:
      message:
        role: ROLE_USER
        parts:
          - text: '{{prompt}}'
      configuration:
        returnImmediately: false
      metadata:
        metadata_field: '{{metadata_field_value}}'
```

### Transform that promotes task metadata (source: "Structured output", verbatim)

```yaml
providers:
  - id: a2a:https://agent.example.com/a2a/v1
    config:
      transformResponse: |
        {
          output: text,
          metadata: {
            taskId: json.task?.id,
            state: json.task?.status?.state,
            eventCount: json.events?.length ?? 0
          }
        }
```

The transform's three arguments (source: "Response Transforms", verbatim):

```
json:    The normalized A2A result { message, task, events, raw }
text:    Promptfoo's default extracted output
context: A2A metadata { message, task, events, raw, mode }
```

### Output extraction priority (source: "Output Extraction", verbatim order)

```
1. Direct A2A message text parts
2. Completed task artifact text parts
3. Task status message text
4. Task history text
5. Raw JSON fallback
```

### Red-team A2A config (source: "Red Team Testing with A2A", verbatim)

```yaml
description: A2A travel agent red team
providers:
  - id: a2a
    config:
      agentCardUrl: https://travel-agent.example.com/.well-known/agent-card.json
      auth:
        type: bearer
        token: '{{ env.A2A_API_KEY }}'
redteam:
  purpose: |
    The system is a travel booking agent that helps users search for flights,
    compare itineraries, and manage reservations.
  plugins:
    - pii
    - bola
    - bfla
    - excessive-agency
  strategies:
    - basic
```

### Error-handling list (source: "Error Handling", verbatim bullets)

```
- Agent Card or operation requests return non-2xx HTTP responses
- Responses are not valid JSON
- Streaming responses contain malformed SSE frames
- Tasks reach TASK_STATE_FAILED, TASK_STATE_CANCELED, or TASK_STATE_REJECTED
- Tasks require additional input or authentication
- Polling exceeds polling.timeoutMs
```

### Limitations list (source: "Limitations", verbatim bullets)

```
- Only the A2A HTTP+JSON REST binding is supported
- JSON-RPC and gRPC bindings are not supported yet
- Push-notification webhooks are not supported because promptfoo evals require a synchronous result
- Streaming is consumed into a single final ProviderResponse; token-by-token UI streaming is not exposed
- Agent Card discovery selects the first HTTP+JSON supported interface
```

## Cross-References

**Candidates from `miner-related-notes.md`** (read first; every listed path is
cited or explicitly dismissed):

- `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — **dismissed**:
  Python `openai-agents` SDK tracing/OTLP bridge; no A2A provider, Agent Card,
  or task-polling surface.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  accounting; no A2A or eval-provider content.
- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **dismissed**:
  finding disposition and export matrices; no A2A provider or polling.
- `source-notes/docs-promptfoo-pi-scorer.md` — **dismissed**: a single
  model-graded scorer's mechanics; no provider transport or task surface.
- `source-notes/docs-promptfoo-evaluate-coding-agents.md` — **cited** (Extends:
  agent-as-system eval framing and final-text output, see below).
- `source-notes/docs-promptfoo-enterprise-guardrails.md` — **dismissed**:
  runtime guardrail HTTP endpoint; no A2A provider.
- `source-notes/docs-litellm-evals-api.md` — **dismissed**: stored-completions
  evals API; no A2A or external agent provider.
- `source-notes/docs-promptfoo-multimodal-red-team.md` — **dismissed**:
  media-channel red-team strategies; no A2A provider or Agent Card context.
- `source-notes/docs-promptfoo-portkey-integration.md` — **cited** (Extends:
  provider auth credential placement, see below).
- `source-notes/blog-pagerduty-sre-agent-triage.md` — **dismissed**: incident
  triage agent workflow; no eval provider or A2A transport.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-litellm-a2a-invoking-agents.md` **Claim 8** ("Task-shaped
    agents require client-side polling — an agent that returns a `submitted` task
    from `message/send` expects the client to poll `tasks/get`") — promptfoo
    automates exactly that client-side poll loop, with the 1000 ms/300000 ms
    defaults in this note's Claim 6. The two notes agree that task-shaped A2A is
    a poll-based contract; promptfoo hides the loop, LiteLLM exposes it.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 6** ("Only
    `message/send` and `message/stream` traverse the gateway's A2A client path …
    all other JSON-RPC methods … are forwarded to the upstream agent URL
    unchanged") — promptfoo's provider likewise builds its surface around
    `message:send`/`message:stream` plus task polling. The two sides agree on
    which operations are first-class.
- **Contradicts**: none filed. The nearest surface is a *conditioning variable*,
  not a contradiction: this page supports only HTTP+JSON while LiteLLM's gateway
  is JSON-RPC-centric (`docs-litellm-a2a-agent-card.md` Claim 7, method table).
  Those are two different clients of the same protocol, each choosing a
  different binding — that is a deployment constraint to plan around, not a
  claim conflict. Checked `CONTRADICTIONS.md` (no entries) and open
  `contradiction`-labeled issues before writing; no contradiction issue filed.
  Note that this page's `/.well-known/agent-card.json` card path independently
  matches one side of the existing path-naming contradiction #1322 (LiteLLM
  page stakes); mention only — do not reopen or pick a verdict.
- **Extends**:
  - `source-notes/docs-litellm-a2a-agent-card.md` **Claim 1** (the gateway
    serves a curated, reduced agent card) and **Claim 5** (`metadata.skillId`
    is forwarded, not enforced) — that note covers the *gateway-side* curation
    and trust of the card. This page is the *client-side consumer*: it trusts the
    card's advertised skills enough to inject them into red-team generation
    (Claim 4) and selects the first HTTP+JSON interface (Claim 3). Read together:
    the card a promptfoo eval consumes may be LiteLLM-curated rather than the
    upstream original, so "the agent's self-description" is already one
    transformation removed from the source.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` **Claim 6** (both
    iteration and budget counters are TTL-windowed, not lifetime) — the
    timeout/budget theme on the gateway side. This page contributes the
    *client-side* bound (`polling.timeoutMs`, Claim 6) and documents no
    token/spend budget at all; the two notes together show that neither side of
    the A2A path gives a lifetime cost guarantee.
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` **Claim 1** ("An
    agent eval tests a *system with emergent behavior*, not a function") and
    **Claim 9** ("An agent's output *is* its final text response, not the files
    it changed") — the same vendor's methodology note establishes that agent
    evals are system evals and that text output is not the whole story. This
    page is the concrete A2A instantiation: final text extraction (Claim 1) plus
    a `transformResponse` escape hatch (Claim 12) are how the "whole story" is
    either surfaced or lost.
  - `source-notes/docs-promptfoo-portkey-integration.md` **Claim 3** ("A Portkey
    request can carry two credentials in two different places") — provider-side
    credential placement. This page adds the A2A provider's own precedence rule
    (`auth` beats `headers.Authorization`, Claim 9) and the card-endpoint scope
    of `auth` (Claim 10); together they argue for treating provider auth config
    as a declared routing decision, not an inferred one.
  - `source-notes/docs-promptfoo-mcp-server.md` **"Available Tools"** (the
    eval/red-team tool catalog) — the corpus's other promptfoo agent-protocol
    surface, but the opposite direction: that page exposes promptfoo's eval
    tools *to* an agent over MCP, while this page consumes an A2A agent *as* an
    eval provider. The page's own "similar to how the MCP provider uses
    discovered tools" analogy refers to the MCP *provider* page, which is not
    yet a corpus note; cite this sibling only for the direction contrast, not
    for the analogy.
- **Novel** (first appearances in the corpus):
  1. An A2A **eval-client** provider (as opposed to the LiteLLM gateway side):
     promptfoo drives an agent as a provider and scores its extracted text.
  2. The HTTP+JSON-only binding constraint and the explicit JSON-RPC/gRPC/
     webhook non-support, including its reachability consequence (Claim 2).
  3. The concrete send-and-poll defaults (1000 ms / 300000 ms) and the
     five-minute-stall-per-prompt failure surface (Claim 6).
  4. Agent Card metadata as red-team generation input — the untrusted
     self-description → attack-generator path (Claim 4).
  5. The auth-precedence rule (`auth` over `headers.Authorization`) and the
     fact that `auth` is sent to the card endpoint too (Claims 9-10).
  6. `transformResponse` as the only documented way to make task id/state/mode
     auditable in eval output (Claims 7, 12).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — "Evaluation must stay separate from side
  effects", `guide/05-llm-ops-reliability.md:254`)**: Add A2A-provider evals as
  a case where the eval *transport* is an external agent: the provider sends
  real messages to the target, so an eval run is live traffic against the agent.
  For the timeout question, document the defaults (Claim 6) and require an
  explicit `polling.timeoutMs` sized to the suite — a stuck agent otherwise
  stalls a gate for five minutes per prompt, and the stall is indistinguishable
  from a fast failure without a transform (Claim 7).
- **Chapter 05 ("Multi-turn evals serialize, and their failures do not
  localise", `guide/05-llm-ops-reliability.md:610`)**: Add that the A2A provider
  defaults to one single-turn text message per test case (Claim 14) and
  documents no automatic context carry-over; multi-turn A2A evals need a custom
  `message` template plus `sessionId`→`contextId` continuity. Otherwise a
  "multi-turn" suite is independent prompts that cannot localize a failure to a
  turn.
- **Chapter 05 ("A gate that cannot fail is not a gate",
  `guide/05-llm-ops-reliability.md:655`)**: Add the observability gap as a gate
  design rule: with the A2A provider, a failed case does not by itself tell you
  whether the agent failed, the task was canceled/rejected, or polling timed out
  (Claim 13), and poll attempts are not in the result (Claim 7). Require a
  `transformResponse` (or external trace) that promotes `task.id`,
  `task.status.state`, `events.length`, and `context.mode` into response
  metadata before trusting the gate's failure classification.
- **Chapter 06 (Security and Trust — "Red-teaming as a CI gate",
  `guide/06-security-and-trust.md:120`)**: Add the Agent Card → attack-generator
  path (Claim 4): when red-teaming an A2A target, the provider reads the target's
  own name/description/capabilities/skills into generation context, so a
  compromised or adversarial card can steer probe selection. Recommend fetching
  and reviewing the card as untrusted data (snapshot it, diff it between runs),
  and not treating advertised skills as a complete coverage list.
- **Chapter 06 ("An agent gateway's default is full access",
  `guide/06-security-and-trust.md:316`)**: Add the client-side auth notes: an
  A2A provider sends its configured credential to `/.well-known/agent-card.json`
  as well as operation endpoints (Claim 10), and `auth` overrides a hand-set
  `headers.Authorization` (Claim 9). Include "which hosts receive the token"
  and "which channel wins" in the credential review; set `tokenUrl` explicitly
  for out-of-origin IdPs instead of relying on discovery (Claim 8).
- **Chapter 06 ("Pin everything; verify releases",
  `guide/06-security-and-trust.md:636`)**: Add that agent eval configs are
  executable contracts too: `transformResponse` can be inline JavaScript, a
  function, or a `file://` reference (Concrete Artifacts → Response Transforms)
  and can set `guardrails`/`sessionId` (Claim 12). Treat an A2A eval config and
  any referenced transform file as reviewable code, and pin the provider version
  the eval runs under.
- **Chapter 03 (Runbooks and Agents — "The emerging agent control plane",
  `guide/03-runbooks-and-agents.md:332`)**: Add the provider-selection gate from
  Claim 2: registering/invoking an agent is not enough; the eval client must
  speak a binding the agent actually exposes. HTTP+JSON-only support means a
  JSON-RPC-only agent is invisible to this provider, so "the agent passed evals"
  is a statement about one binding, not the agent's whole interface.

## Extraction Notes

- Source read in full via WebFetch of the canonical URL
  (`https://www.promptfoo.dev/docs/providers/a2a`, HTTP 200, no paywall) on
  2026-11-07; page footer "Last updated on **Nov 7, 2026** by **Naveen
  Chatlapalli**". All configuration examples, the option table, the output
  extraction order, the error list, and the limitations list were captured
  verbatim. No sub-pages followed: the outbound links (A2A spec, A2A
  definitions, MCP provider, HTTP provider, red-team guide) do not document this
  provider's contract, and the sibling corpus notes already cover the protocol
  and red-team surfaces.
- Quotes were checked character-for-character against the fetched rendered page
  before writing. YAML blocks arrived as collapsed single lines after HTML
  extraction; line breaks/indentation were restored at YAML boundary only, with
  no wording changes (same convention as the sibling promptfoo notes). The
  option table preserves the page's exact names, types, defaults, and
  descriptions; alignment spaces are formatting only.
- **Arguments from silence are labeled as such**: Claim 7 (poll attempts not
  surfaced) rests on the page never documenting a poll counter/attempt log, not
  on a statement that it cannot exist; it is graded `emerging` for that reason.
  We did not assert that the provider cannot expose polling details, only that
  the page documents no field for them and the only documented escape hatch is
  `transformResponse`. The failure-surface reading in Claim 6 (five-minute
  stall) is arithmetic from the documented defaults, not an observed run.
- **Candidate disposition** (from `miner-related-notes.md`, read before writing
  Cross-References; every listed path is cited or dismissed by name above):
  cited `docs-promptfoo-evaluate-coding-agents.md` and
  `docs-promptfoo-portkey-integration.md`; dismissed the other eight
  (`docs-promptfoo-evaluate-openai-agents-python.md`,
  `docs-litellm-batches-api.md`,
  `docs-promptfoo-enterprise-findings-reports.md`,
  `docs-promptfoo-pi-scorer.md`,
  `docs-promptfoo-enterprise-guardrails.md`,
  `docs-litellm-evals-api.md`,
  `docs-promptfoo-multimodal-red-team.md`,
  `blog-pagerduty-sre-agent-triage.md`).
- Additional cross-refs beyond the candidate list found by searching
  `source-notes/`: `docs-litellm-a2a-agent-card.md`,
  `docs-litellm-a2a-invoking-agents.md`, `docs-litellm-a2a-agent-gateway.md`,
  `docs-litellm-a2a-iteration-budgets.md`, and `docs-promptfoo-mcp-server.md`.
  Every cited `Claim N` was re-read and verified against the cited note per
  MINER.md §4b before writing (agent-card Claims 1/5/7, invoking-agents Claim 8,
  agent-gateway Claim 6, iteration-budgets Claim 6, coding-agents Claims 1/9,
  portkey Claim 3, mcp-server "Available Tools" section by name because the tool
  catalog is not a numbered claim).
- No contradiction issue filed: checked `CONTRADICTIONS.md` (no entries) and
  open `contradiction`-labeled issues. The HTTP+JSON vs JSON-RPC difference is a
  client-binding conditioning variable, not a same-topic claim conflict. The
  page's `/.well-known/agent-card.json` path is noted against the existing
  #1322 ambiguity without reopening it or picking a verdict.
- `confidence_overall: emerging` — the mechanics (defaults, endpoint set, auth
  schemes, precedence, extraction order, error/limitation lists) are settled and
  checkable; the security and observability claims that matter most
  (card-metadata injection, poll-attempt invisibility, transform-as-control)
  are inferences from the documented surface and from what the page omits, and
  the page reports no measured run data.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited —
  both are derived indexes rebuilt after merge.
