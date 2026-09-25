---
source_url: https://docs.litellm.ai/docs/completion/anthropic_advisor_tool
source_type: docs
title: "Advisor Tool — LiteLLM Documentation (Anthropic advisor tool via the gateway)"
author: "LiteLLM (BerriAI) — official vendor documentation; upstream Anthropic API docs linked from the page"
date_published: unknown (living vendor docs; current as of 2026-09-25)
date_extracted: 2026-09-25
last_checked: 2026-09-25
status: current
confidence_overall: emerging
issue: "#1456"
---

# Advisor Tool (LiteLLM Docs)

> LiteLLM proxies Anthropic's beta **advisor tool** — a within-request
> executor↔advisor composition where a cheap executor model consults a bigger
> advisor mid-generation — and for every non-Anthropic provider it *runs the
> orchestration loop itself* (`AdvisorOrchestrationHandler`). The operational
> content is not the pattern (it is vendor marketing); it is the four contracts
> the gateway does not surface at the top level: **advisor tokens are absent
> from top-level `usage`** (they appear only in `usage.iterations[]` with
> `type: "advisor_message"`), the **stream pauses** for a non-streaming
> sub-inference, **`max_uses` has a different failure encoding on the gateway
> than upstream Anthropic** (filed as contradiction #1461), and the gateway
> **rewrites conversation history** to keep Anthropic-only block types away
> from non-Anthropic providers.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, a
  focused topic page under "Guides > Tool Calling", sitting between "Code
  Interpreter Sandbox Interception" and "Message Sanitization for Tool Calling
  for anthropic models").
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* the gateway exposes (tool-definition fields,
  `usage` shape, the named `AdvisorOrchestrationHandler` /
  `AdvisorMaxIterationsError` identifiers, the provider matrix, the system-prompt
  blocks). It documents **capability only**: no measured latency, no cost
  figures beyond the token counts in one example, no failure writeup, no
  production experience report. Per the Prospector's bounding rule, every claim
  below stays at "the gateway documents this," never "this holds in production."
- **Scope**: Covers the pattern, the provider support matrix, LiteLLM's native
  orchestration loop for non-Anthropic providers, the response structure, the
  `usage`/`iterations` cost split, the `max_uses` and `caching` knobs, the
  recommended system-prompt blocks, and the Chat Completions / Messages API /
  AI-Gateway call shapes. Does **not** cover the Anthropic beta header's
  interaction with other betas, advisor-side rate-limit accounting, or the
  `pause_turn` resumption path (see Extraction Notes).
- **Linked upstream page also read (per MINER §1, sub-page follow-up)**: the
  page's "Additional Resources" links
  `https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool`
  ("Anthropic Advisor Tool Documentation"), which is the normative spec for the
  same `advisor_20260301` tool. It was read in full. Every quote in this note
  taken from it is **explicitly attributed inline** to that URL and to
  `platform.claude.com`; every other quote is verbatim from the LiteLLM page
  (`docs.litellm.ai`, the note's `source_url`). Two contradictions against
  upstream were found and filed (#1461, #1462).

## Extracted Claims

### Claim 1: The advisor tool is a *within-request* model composition — a fast, low-cost executor consults a higher-intelligence advisor mid-generation, and the advisor reads the full conversation to produce a 400–700-token plan or course correction before the executor continues
- **Evidence**: The page's opening two paragraphs, plus a "Response Structure"
  section showing the advisor's text arriving as a `server_tool_use` /
  `advisor_tool_result` block pair inside the assistant's own content.
- **Confidence**: emerging (documented vendor pattern; the pattern exists and
  the block shape is concrete, but nothing on the page measures it)
- **Quote**: "The advisor tool lets a fast, lower-cost executor model (Sonnet or Haiku) consult a high-intelligence advisor model (Opus 4.6) mid-generation. The advisor reads the full conversation and produces a plan or course correction, typically 400–700 text tokens, and the executor continues with the task."
- **Our assessment**: The pattern boundary is the guide-relevant part, and it is
  genuinely *not* the same lever as the routing material the corpus already
  holds. `docs-litellm-adaptive-router.md` Claim 2 and
  `blog-litellm-auto-router-v2.md` Claim 1 are both **per-request
  classification**: pick one model for the whole request. This is a second model
  invoked *inside* a single request, with the cheaper model authoring the bulk
  of the output. The guide's model-selection section currently teaches only the
  first axis; this is a second, orthogonal cost/quality dial, and an operator
  can combine them (a router picks the executor, the advisor tool supplies the
  planning pass). Explicitly **not** carried forward from this page: the
  marketing sentence "You get close to advisor-solo quality while the bulk of
  token generation happens at executor-model rates." That is a vendor assertion
  with **no eval, no baseline, and no measurement on the page** — the Prospector
  explicitly flagged it as not-to-be-imported. The linked Anthropic page points
  at a separate cost/intelligence optimization doc for measured results; this
  page does not, and the "close to advisor-solo" framing should be treated as
  `[emerging]` marketing, not a settled quality claim.

### Claim 2: Advisor spend is split out of the top-level `usage` object — advisor calls are a separate sub-inference billed at the advisor model's rates, top-level `usage` reflects **executor tokens only**, and advisor tokens are reachable only via `usage.iterations[]` entries carrying `type: "advisor_message"`
- **Evidence**: The "Cost Control" section's opening sentence, its worked
  `usage` example, and the sentence immediately after it. The example's
  `advisor_message` entry reports `input_tokens: 823, output_tokens: 1612` —
  roughly **3.4x the executor's total** input tokens and **3x** its output
  tokens in the same request.
- **Confidence**: emerging (explicit documented payload shape with a numeric
  worked example; the *rate* used is the advisor model's, so the hidden spend
  is the expensive spend)
- **Quote**: "Advisor calls run as a separate sub-inference billed at the advisor model's rates. Usage is reported in `usage.iterations[]`:" / "Top-level `usage` reflects executor tokens only. Advisor tokens appear in `iterations` entries with `type: \"advisor_message\"` and are billed at Opus rates."
- **Our assessment**: This is the single highest-value claim on the page for
  Ch02/Ch05, and it is a *silent* accounting gap — the response is a 200, the
  `usage` object is present and looks complete, and the expensive half of the
  work is one array level down. Any spend dashboard, per-request cost
  calculator, or budget alert that reads `usage.input_tokens` /
  `usage.output_tokens` **under-reports this feature by the advisor's share**,
  and the advisor's share is billed at Opus rates. Two extra properties the page
  does not state but the linked upstream page does, which sharpen the trap:
  upstream says the top-level `max_tokens` "applies to executor output only. It
  does not bound advisor sub-inference tokens", so a request with
  `max_tokens=4096` can consume unbounded advisor output; and
  "Priority Tier applies to each model independently. A Priority Tier commitment
  on the executor model does not extend to the advisor" (quoted from
  `platform.claude.com`, the linked Anthropic page) — so a capacity/commitment
  assumption carried over from the executor model is wrong for the sub-inference.
  Nothing in the corpus covered a top-level metric that systematically
  under-reports the expensive path.

### Claim 3: The page's own `usage` example is arithmetically inconsistent with the summing rule the upstream spec states — it reports top-level `input_tokens: 412` while its own two `message` iterations sum to 1760
- **Evidence**: The page's "Usage with advisor sub-inference" example (see
  Concrete Artifacts) vs the `## Usage and billing` section of the linked
  Anthropic page. The two examples share **byte-identical iteration values**
  (`412/89`, `823/1612` on `claude-opus-5`, `1348/442`); upstream's top-level
  `input_tokens` is `1760` and it also carries `cache_read_input_tokens: 412`,
  while this page's is `412` with the cache fields removed.
- **Confidence**: settled for the arithmetic (412 + 1348 = 1760 ≠ 412);
  "copied from upstream and edited" is the Miner's inference from the identical
  iteration triples, not a statement either page makes
- **Quote**: (LiteLLM page, the example) `"input_tokens": 412` /
  `"output_tokens": 531` — versus, from `platform.claude.com`,
  "Every top-level `usage` field is the sum of that field across all executor iterations, including `input_tokens`, `output_tokens`, and `cache_read_input_tokens`." and its own `"input_tokens": 1760`
- **Our assessment**: Recorded as a **documentation defect with a live
  consequence**, not as a product bug. The page's `output_tokens: 531` *does*
  satisfy the summing rule (89 + 442 = 531) while its `input_tokens` does not
  (412 + 1348 = 1760) — so the example is half-right in a way that suggests a
  hand-edit rather than a deliberate illustration. The operational read for
  Ch02: **do not build a cost calculator by copying this example.** It is the
  corpus's second instance of a documented payload being quoted with a field
  that contradicts the rule stated for it (cf. `docs-litellm-token-usage-helpers.md`
  Claim 4, where a malformed example coexists with a correct API contract).

### Claim 4: Streaming contains a non-streaming hop — the advisor sub-inference does not stream, the executor's stream pauses while it runs, and the full advisor result then arrives in a single event before executor output resumes
- **Evidence**: The "Streaming behavior" callout under the Chat Completions
  streaming example, quoted below. The linked Anthropic page adds the wire-level
  detail this page omits (where the pause begins, what — if anything — arrives
  during it, and when usage lands).
- **Confidence**: emerging (explicit documented behavior; no latency figures
  anywhere on either page)
- **Quote**: (LiteLLM page) "The advisor sub-inference does not stream. The executor's stream pauses while the advisor runs, then the full advisor result arrives in a single event. Executor output resumes streaming afterward."
- **Our assessment**: Operationally this is an **inter-token-latency alert
  false-positive generator**. On an otherwise healthy stream, one advisor call
  produces a silent gap whose length is the full sub-inference duration —
  plausibly seconds. A client cannot distinguish that from a hung upstream, so
  (a) client-side and proxy-side stream-idle timeouts must be budgeted above
  worst-case advisor duration, and (b) an ITL/inter-token-gap SLO needs an
  explicit advisor-call carve-out or it will page. The linked Anthropic page
  (quoted inline from `platform.claude.com`) supplies the two facts needed to
  act on it: the pause "begins when that block closes (`content_block_stop`)" and
  "the stream is quiet except for standard SSE `ping` keepalives emitted roughly
  every 30 seconds. Short advisor calls might show no pings." — i.e. a gateway
  or client that treats *any* silence as a dead stream will drop a 25-second
  advisor call, and one that only tolerates 30s of silence may kill a
  legitimately longer one. Note also that the page's own orchestration loop
  "Wraps the final response in an SSE stream if you requested `stream=True`"
  (Claim 5) — for non-Anthropic providers the stream is *synthesized* by
  LiteLLM, and the page **never says whether that synthesized stream reproduces
  the pause at all**. Left as a documented gap, not asserted either way.

### Claim 5: For every non-Anthropic provider, LiteLLM runs the advisor loop itself via a named internal component, `AdvisorOrchestrationHandler`, and enumerates five things it does on the operator's behalf
- **Evidence**: The "How it works (LiteLLM native orchestration)" section —
  one prose paragraph naming the handler, then an explicit "What LiteLLM does
  for you" bullet list of five items (reproduced verbatim in Concrete Artifacts).
- **Confidence**: settled for the documented mechanism (a named component plus
  an enumerated contract); emerging for the behavior it produces
- **Quote**: "When a request arrives with an `advisor_20260301` tool and a non-Anthropic provider, `AdvisorOrchestrationHandler` intercepts it. It translates the advisor tool into a regular function tool the provider understands, then runs an orchestration loop:"
- **Our assessment**: This is the guide's "what the proxy does on your behalf"
  material made concrete and inspectable — the same class of gateway-owned
  agentic loop the corpus already records for the OpenAI code-interpreter swap
  (`blog-litellm-swap-openai-code-interpreter.md` Claim 3: intercept → execute →
  feed back → tear down, response shape preserved). Two operational consequences
  of the *advisor* version: (1) the advisor loop is a **second, invisible
  provider call** inside one client request, so provider-side rate limits,
  credentials, and spend all see traffic the client's own request count does not
  (the linked Anthropic page adds: "Advisor rate limits draw from the same
  per-model bucket as direct calls to the advisor model. A rate limit on the
  advisor appears as `too_many_requests` inside the tool result. A rate limit on
  the executor fails the whole request with HTTP 429." — quoted from
  `platform.claude.com`; the LiteLLM page says nothing about rate limits at
  all). (2) The `stream=True` SSE re-wrap means on this path the client's
  stream is gateway-generated, which is a second reason the pause semantics in
  Claim 4 are worth confirming empirically rather than assuming.

### Claim 6: The provider matrix splits the feature into "Anthropic = native server-side" and "everything else = LiteLLM orchestration loop", and both API surfaces are ✅ for every listed provider
- **Evidence**: The "Supported Providers" table, reproduced verbatim in
  Concrete Artifacts.
- **Confidence**: settled for the documented matrix; the ✅ rows are
  surface-support claims, not per-provider parity
- **Quote**: (table Notes column) "Native — runs server-side" (Anthropic API) and "LiteLLM orchestration loop" (OpenAI / Azure OpenAI, Amazon Bedrock, Google Vertex AI, Groq / Mistral / others)
- **Our assessment**: Apply the corpus's standing reading of a LiteLLM support
  matrix — **✅ = surface support, not per-provider parity** — exactly as
  `docs-litellm-anthropic-unified.md` Claim 2, `docs-litellm-bedrock-invoke.md`
  Claim 3, and `docs-litellm-audio-transcription.md` Claim 5 each record for
  their own tables. A sharper question the matrix raises and does not answer:
  the LiteLLM table lists **Amazon Bedrock** and **Google Vertex AI** as
  supported, while the linked Anthropic page states (quoted from
  `platform.claude.com`) "The advisor tool is available in beta on the Claude API
  and on Claude Platform on AWS. It is not currently available on Amazon
  Bedrock, Google Cloud, or Microsoft Foundry." These are reconcilable — in
  LiteLLM's case Bedrock/Vertex are the **executor** provider while the advisor
  sub-inference would still go to Anthropic — but **the LiteLLM page never says
  where the advisor sub-inference is sent.** Recorded as an open question, not a
  contradiction: an operator cannot determine from this page whether enabling
  the advisor on a Vertex executor route adds Anthropic API egress (and
  therefore Anthropic credentials, region, and data-residency implications) to
  a workload that looks Vertex-only from the outside. That is a
  data-governance question, not a latency one, and it deserves an explicit
  answer before this feature is enabled on a non-Anthropic executor.

### Claim 7: On the non-Anthropic orchestration path the client receives a clean response with no advisor blocks at all, so the advisor's contribution is not observable by the client
- **Evidence**: The inline comment on the "Advisor Tool with OpenAI executor"
  example, which uses `model="openai/gpt-5.6-luna"` with
  `custom_llm_provider="openai"`, plus the `print(response["content"][0]["text"])`
  line that indexes the response as if no advisor blocks existed.
- **Confidence**: emerging (documented via a code comment and response access
  pattern rather than a prose guarantee — a single code comment is thin support
  for a load-bearing observability claim)
- **Quote**: "# Final response is clean — no advisor tool_use blocks"
- **Our assessment**: This is the observability half of Claims 1 and 2 and it
  cuts the other way from the rest of the page. On the **native Anthropic**
  path the client sees `server_tool_use` + `advisor_tool_result` blocks and can
  at least *count* advisor calls from the response body; on the **LiteLLM
  orchestration** path the documented example says the client gets no such
  blocks. Combined with Claim 2's token split, that means an operator who
  enables the advisor on an OpenAI/Gemini/Groq executor may be left with **no
  client-side evidence that the advisor ever ran** — the only signal is the
  `advisor_message` entry in `usage.iterations[]`, which the page itself warns
  is absent from the top-level totals. Caveat recorded honestly: this rests on a
  code comment, and the page elsewhere claims LiteLLM "handles this
  automatically through `provider_specific_fields`" for round-tripping advisor
  blocks — so the surface is genuinely ambiguous. Treat as a **must-verify
  before rollout** item, not a settled contract.

### Claim 8: `max_uses` is enforced as a hard cap, exceeding it raises `AdvisorMaxIterationsError`, `max_uses=0` disables the advisor entirely, and on reaching the cap the executor continues without further advice
- **Evidence**: The fifth bullet of the "What LiteLLM does for you" list, plus
  the second "Cost Control" tip. Both quotes below are verbatim from the page.
- **Confidence**: emerging (documented vendor behavior with a named error
  identifier; the *consequences* of the error on the response are not stated)
- **Quote**: "Enforces `max_uses` as a hard cap; `AdvisorMaxIterationsError` is raised if exceeded, and `max_uses=0` disables the advisor entirely" / "Use `max_uses` to cap advisor calls per request. Once reached, the executor continues without further advice."
- **Our assessment**: The `AdvisorMaxIterationsError` identifier is a
  grep-able, alertable name — good. But the page is **internally ambiguous
  about whether that error is raised or handled**, because the same page's
  second tip says that on reaching the cap "the executor continues without
  further advice" (i.e. a degraded success). Those two statements can only both
  be true if the error is raised-and-caught inside the orchestration loop, which
  the page never says. The upstream spec is unambiguous on the same field and
  is the *opposite* encoding: per `platform.claude.com`, further advisor calls
  "return an `advisor_tool_result_error` with `error_code: \"max_uses_exceeded\"`
  and the executor continues without further advice… The request itself does
  not fail." **Filed as contradiction #1461** (MINER §4a) — no verdict picked
  here. The guide-relevant rule either way: `max_uses` bounds advisor calls
  **per request**, and a "cap reached" condition is a *degraded* outcome that
  must be counted and alerted on explicitly, because on at least one of the two
  documented encodings it arrives as a **200**.
  `docs-litellm-a2a-iteration-budgets.md` Claim 3/Claim 5 records a *third*
  encoding for the same conceptual control in the same product (over-cap → HTTP
  429 `budget_exceeded`, which collides with rate limiting) — three failure
  shapes for "the loop ran out of budget" is itself worth a Ch03/Ch05 note.

### Claim 9: The gateway mutates conversation history in both directions — it strips Anthropic-only `advisor_tool_result` / `server_tool_use` blocks from re-sent history so non-Anthropic providers never see them, and it auto-strips `advisor_tool_result` blocks on follow-up turns when the advisor tool is absent from the current request in order to prevent an Anthropic 400
- **Evidence**: The third bullet of the "What LiteLLM does for you" list and
  the "Auto-strip on follow-up turns" callout under the multi-turn example.
  Both are verbatim below. These are the only two history-mutation rules stated
  on the page.
- **Confidence**: settled for the documented rules (explicit, imperative vendor
  statements about a mechanism); emerging for what it does to a client's
  round-trip contract
- **Quote**: "Strips any `advisor_tool_result` / `server_tool_use` blocks from message history on re-send so non-Anthropic providers never see Anthropic-specific types" / "LiteLLM automatically strips `advisor_tool_result` blocks from message history when the advisor tool is not present in the current request. This prevents the Anthropic 400 error that would otherwise occur."
- **Our assessment**: Two different rules doing two different jobs, and the
  guide should not conflate them. The **first** is a provider-compatibility
  rewrite on the non-Anthropic path: the gateway is editing the *conversation
  transcript* (not just the request parameters) so that Anthropic-native block
  types never reach a provider that would reject them. The **second** is a
  shape-repair rule that fires on *all* paths, including native Anthropic,
  whenever a client drops the tool from `tools` while history still contains
  advisor result blocks — it is the gateway pre-empting a documented 400.
  The second rule's existence is itself a Ch05 finding: the guide's existing
  §Provider parity rule (guide/05-llm-ops-reliability.md:352) is scoped to
  **parameters** — "Present-but-null and omitted are not equivalent across
  'OpenAI-compatible' backends". This page is a second, independent instance of
  the same class where the carrier is **content blocks in conversation
  history**, which the existing rule does not name. See Guide Impact.
  Two open questions the page leaves unanswered, recorded not asserted: (a) if
  the client manages history itself, what exactly does LiteLLM strip and does
  the strip apply to *inbound* stored history or only to the outbound re-send;
  (b) the page's own multi-turn example does not exercise the strip rule at all
  (it reuses the same `tools` array on the follow-up turn — see Concrete
  Artifacts), so the rule has no worked example on the page.

### Claim 10: The beta gate is `anthropic-beta: advisor-tool-2026-03-01`, and LiteLLM adds it automatically whenever it detects the advisor tool in the `tools` array
- **Evidence**: The page's "Beta" callout directly under the title, and the
  Anthropic-SDK-via-proxy example which additionally shows the caller passing
  `betas=["advisor-tool-2026-03-01"]` explicitly.
- **Confidence**: settled (explicit header name plus explicit auto-injection
  rule)
- **Quote**: "The advisor tool is in beta. Include `anthropic-beta: advisor-tool-2026-03-01` in your requests; LiteLLM adds this automatically when it detects the advisor tool in your `tools` array."
- **Our assessment**: The auto-injection rule is a governance fact, not a
  convenience: **any** request reaching a LiteLLM proxy that carries an
  `advisor_20260301` entry in `tools` is silently promoted onto an Anthropic
  beta feature, whether or not the client intended to opt in. On a shared
  multi-tenant gateway that means (a) a beta feature can be enabled by a
  client's request body rather than by operator config, and (b) the
  beta-admission surface is a body field, so a gateway allowlist that only
  constrains model names will not catch it. Note the tension with Claim 6: the
  page's Messages-API-via-proxy example has the *caller* send the beta header
  through an OpenAI-compatible Anthropic SDK call, so on that path the header is
  client-supplied — i.e. the "LiteLLM adds this automatically" rule and the
  "client passes `betas=[...]`" example are two different admission paths for
  the same feature, and the page does not say which one wins when both are
  present. The feature is a **beta** (both vendors say so), which is why every
  claim in this note is capped at `emerging`.

### Claim 11: Caching on the advisor tool definition has a stated break-even threshold — enable it only when you expect 3+ advisor calls per conversation, because below that it costs more than it saves
- **Evidence**: The first "Cost Control" tip, and the inline comment in the
  "With Optional Parameters" example, which carries the same threshold:
  `"caching": {"type": "ephemeral", "ttl": "5m"},  # enable for 3+ calls per conversation`.
  The linked Anthropic page states the same threshold with the mechanism
  spelled out (quoted inline below).
- **Confidence**: emerging (documented threshold with a mechanism; no
  cost arithmetic published on either page)
- **Quote**: "Enable `caching` on the tool definition only when you expect 3+ advisor calls per conversation; it costs more than it saves below that threshold."
- **Our assessment**: A rare published break-even point for a per-call cache
  knob, and the mechanism (quoted from `platform.claude.com`) explains why it is
  a *conversation-length* threshold rather than a request-length one: "The
  advisor's prompt on the Nth call is the (N-1)th call's prompt with one more
  segment appended, so the prefix is stable across calls." Because the advisor
  reads the executor's **full transcript**, the cache only pays once the
  transcript is long enough for the read savings to beat the write. The
  threshold interacts directly with Claim 14: `max_uses` is per-request and the
  conversation cap is client-side, so the 3-call threshold is a statement about
  the *conversation*, not the request. Two caching hazards documented upstream
  but **absent from this page** (quoted from `platform.claude.com`): "Set
  `caching` once and leave it for the whole conversation. Toggling it off and on
  mid-conversation causes cache misses", and a `clear_thinking` warning that
  advisor-side caching silently degrades under context editing. The page's
  `caching` shape also differs from every other cache knob in the corpus —
  per `platform.claude.com` it "is not a breakpoint marker. It is an on/off
  switch" — which matters because the corpus's caching notes
  (`docs-litellm-caching-all-caches.md` Claim 4/Claim 9) treat cache controls as
  per-call markers and layered TTLs.

### Claim 12: LiteLLM's documented model pairing is Opus-advisor-only over a three-row table, and the page contradicts itself on the advisor's model ID — "Opus 4.6" in the intro, `claude-opus-5` in Model Compatibility
- **Evidence**: The intro sentence, the "Model Compatibility" prose sentence,
  and the three-row compatibility table, all quoted below. Upstream's rule and
  table are quoted inline from `platform.claude.com` for comparison.
- **Confidence**: emerging (documented table plus a verified same-page
  inconsistency; the *correct* pairing set is not determinable from these pages)
- **Quote**: "The advisor is an Opus model (`claude-opus-5`), and the executor can be Opus 4.6 or later, Sonnet 4.6 or later, or Haiku 4.5." (contrast with the intro's "consult a high-intelligence advisor model (Opus 4.6)")
- **Our assessment**: **Filed as contradiction #1462**; no verdict picked. Three
  separate problems, all checkable on the page: (1) the intro names a different
  advisor model than the Model Compatibility section, and per
  `platform.claude.com` the choice is not cosmetic — "With `claude-opus-5` as
  the advisor… the block's `content` field is an `advisor_redacted_result`
  variant (encrypted; the executor reads it server-side, but your client does
  not)", whereas a Claude Opus 4.8 advisor returns readable plaintext; (2) the
  page's "Opus model" rule is narrower than upstream's, which per
  `platform.claude.com` is a capability floor — "The advisor must be Claude
  Sonnet 4.6 or a more capable model, and it must be at least as capable as the
  executor" — admitting Sonnet 4.6/5, Fable 5/5.1 and Mythos 5/5.1 as advisors at
  materially different cost; (3) the table is a **subset of the page's own
  prose**: the prose permits "Opus 4.6 or later, Sonnet 4.6 or later, or Haiku
  4.5" as executors, the table lists only `claude-haiku-4-5-20251001`,
  `claude-sonnet-5`, and `claude-opus-5`. Also worth recording as a
  documentation gap rather than an error: the table's executor ID
  (`claude-haiku-4-5-20251001`) is a dated form while upstream writes
  `claude-haiku-4-5` throughout.

### Claim 13: The page ships three recommended system-prompt blocks, including an optional instruction the vendor reports cutting advisor output length by 35–45%
- **Evidence**: The "Recommended System Prompt" section — a timing block
  (prepend), an advice-weight block (add after timing), and a cost-reduction
  line (add before the timing block), all reproduced verbatim in Concrete
  Artifacts.
- **Confidence**: emerging (verbatim prompt text; the 35–45% figure is a
  vendor-reported number with **no method, n, benchmark, or baseline** on the
  page)
- **Quote**: "To reduce advisor output length by 35–45% without losing quality, add:"
- **Our assessment**: The prompt content is operationally useful and specific
  (it encodes a real control loop: consult *before* committing to an
  interpretation, again *before* declaring done, and treat advice as weighty
  but not infallible). The 35–45% number should be cited as **[emerging,
  vendor-reported, unverified]** and never as a planning input. Note that the
  *harder* control is not on this page: upstream's `max_tokens` on the tool
  definition is "a hard ceiling rather than a soft request" (quoted from
  `platform.claude.com`, which also reports "this reduced mean advisor output by
  roughly 7x compared with leaving the cap unset, with near-zero truncation"
  on n=40 per configuration) — the LiteLLM page **never documents
  `max_tokens` on the advisor tool definition at all**, even though it documents
  `max_uses` and `caching` from the same parameter family. That omission is a
  gap a reader will hit immediately when trying to bound cost.

### Claim 14: There is no conversation-level cap — the gateway's documented remedy is for the client to count advisor calls and remove the advisor tool from `tools` when it reaches its limit
- **Evidence**: The third "Cost Control" tip, verbatim below.
- **Confidence**: settled (explicit, imperative vendor instruction); the
  failure mode of getting the client-side count wrong is the Miner's reading
- **Quote**: "For conversation-level caps, count advisor calls client-side. When you reach your limit, remove the advisor tool from `tools`."
- **Our assessment**: The control is **not enforceable at the gateway** and the
  page says so plainly. Combined with Claim 8, the full cost-control surface
  is: per-request advisor-call cap (`max_uses`, gateway-enforced, ambiguous
  error encoding), per-conversation advisor-call cap (**client-enforced**), and
  per-call advisor-output cap (`max_tokens` on the tool definition, **not
  documented on this page**). Any guide claim that this feature is
  gateway-governable is wrong on the conversation axis. The client-side counting
  is also the one place where a client needs to *see* advisor calls — and per
  Claim 7 the client may have no block-level evidence on the non-Anthropic
  path, so "count client-side" may mean "count from `usage.iterations[]`," which
  is the same deep-array read that Claim 2's cost trap already requires.

### Claim 15: The AI-Gateway surface requires no gateway-side advisor configuration — the advisor model is supplied per request by the client through the proxy, and the only proxy config is the ordinary executor model alias
- **Evidence**: The `config.yaml` snippet (identical for both the OpenAI-SDK and
  Anthropic-SDK gateway examples) and the two client examples, which both pass
  the advisor definition in the request `tools` array.
- **Confidence**: settled (documented config surface; both gateway examples
  reproduced in Concrete Artifacts)
- **Quote**: (config.yaml, verbatim) `model_list:\n  - model_name: claude-sonnet\n    litellm_params:\n      model: anthropic/claude-sonnet-5\n      api_key: os.environ/ANTHROPIC_API_KEY`
- **Our assessment**: Operationally important and slightly counter-intuitive:
  **the advisor model is not a gateway policy object.** There is no
  `advisor_model` key, no allowlist, and no per-key restriction on which
  advisor a client may name — any client that can call the route can name
  `claude-opus-5` in its tool definition and incur Opus-rate sub-inference spend
  against the key's budget. That is a **spend-governance gap**, and it lands
  directly on top of Claim 2's accounting gap: the client selects the expensive
  model *and* the top-level `usage` does not show what it cost. Combined, a
  key's budget can be consumed by advisor sub-inference that the key's own
  usage log under-reports. Nothing in the page documents a gateway-side way to
  constrain this. Contrast the corpus's existing gateway cost controls
  (`blog-litellm-save-claude-code-costs.md` Claim 1 budget windows; Claim 2
  budget fallback chains) — those bound spend at the key; the advisor tool
  introduces a spend dimension those controls were not designed to observe
  through the top-level usage fields.

## Concrete Artifacts

All artifacts verbatim from the fetched pages. Blocks marked
**[platform.claude.com]** are from the Anthropic page linked in the LiteLLM
page's "Additional Resources"
(`https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool`),
read per MINER §1; all other blocks are from the note's `source_url`.

### Provider matrix (LiteLLM page, "Supported Providers", verbatim)

```
Provider

Chat Completions API

Messages API

Notes

Anthropic API            ✅   ✅   Native — runs server-side
OpenAI / Azure OpenAI    ✅   ✅   LiteLLM orchestration loop
Amazon Bedrock           ✅   ✅   LiteLLM orchestration loop
Google Vertex AI         ✅   ✅   LiteLLM orchestration loop
Groq / Mistral / others  ✅   ✅   LiteLLM orchestration loop
```

(Rendered as a five-column table on the page; flattened here per row.)

### The five-step orchestration contract (LiteLLM page, "What LiteLLM does for you", verbatim)

```
-   Strips `advisor_20260301` from the outgoing request, so the provider only sees a standard function tool named `advisor`
-   When the executor calls it, intercepts before the result reaches you, runs the advisor sub-call, and injects the advice
-   Strips any `advisor_tool_result` / `server_tool_use` blocks from message history on re-send so non-Anthropic providers never see Anthropic-specific types
-   Wraps the final response in an SSE stream if you requested `stream=True`
-   Enforces `max_uses` as a hard cap; `AdvisorMaxIterationsError` is raised if exceeded, and `max_uses=0` disables the advisor entirely
```

### Model compatibility table (LiteLLM page, verbatim — all three rows)

```
Executor                    Advisor
claude-haiku-4-5-20251001   claude-opus-5
claude-sonnet-5             claude-opus-5
claude-opus-5               claude-opus-5
```

### The cost-split `usage` example (LiteLLM page, "Usage with advisor sub-inference", verbatim)

```json
{
  "usage": {
    "input_tokens": 412,
    "output_tokens": 531,
    "iterations": [
      {
        "type": "message",
        "input_tokens": 412,
        "output_tokens": 89
      },
      {
        "type": "advisor_message",
        "model": "claude-opus-5",
        "input_tokens": 823,
        "output_tokens": 1612
      },
      {
        "type": "message",
        "input_tokens": 1348,
        "output_tokens": 442
      }
    ]
  }
}
```

Compare **[platform.claude.com]**'s "Usage and billing" example, whose iteration
values are identical but whose top-level `input_tokens` is `1760` (and which
also carries `cache_read_input_tokens: 412`) — see Claim 3.

### Advisor `max_uses` failure contract ([platform.claude.com], "Tool parameters" table row, verbatim)

> Maximum number of advisor calls allowed in a single request. Once the executor reaches this cap, further advisor calls return an `advisor_tool_result_error` with `error_code: "max_uses_exceeded"` and the executor continues without further advice. This is a per-request cap, not a per-conversation cap.

and the error-code table ([platform.claude.com], verbatim):

```
max_uses_exceeded       The request reached the `max_uses` cap set on the tool definition. Further advisor calls in the same request return this error.
too_many_requests       The advisor sub-inference was rate-limited.
overloaded              The advisor sub-inference hit capacity limits.
prompt_too_long         The transcript exceeded the advisor model's context window.
execution_time_exceeded The advisor sub-inference timed out.
model_not_found         The configured advisor model is not available.
unavailable             Any other advisor failure.
```

None of these seven error codes appears on the LiteLLM page; LiteLLM names
exactly one error, `AdvisorMaxIterationsError`, and describes no others.

### Tool definition with `max_uses` + `caching` (LiteLLM page, "With Optional Parameters", verbatim — whitespace normalized)

```python
import litellm

response = litellm.completion(
    model="anthropic/claude-sonnet-5",
    messages=[
        {"role": "user", "content": "Build a REST API with authentication in Python."}
    ],
    tools=[
        {
            "type": "advisor_20260301",
            "name": "advisor",
            "model": "claude-opus-5",
            "max_uses": 3,                             # cap advisor calls per request
            "caching": {"type": "ephemeral", "ttl": "5m"},  # enable for 3+ calls per conversation
        }
    ],
    max_tokens=4096,
)
```

### Response with advisor blocks (LiteLLM page, "Response with advisor blocks", verbatim)

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Let me consult the advisor on this."
    },
    {
      "type": "server_tool_use",
      "id": "srvtoolu_abc123",
      "name": "advisor",
      "input": {}
    },
    {
      "type": "advisor_tool_result",
      "tool_use_id": "srvtoolu_abc123",
      "content": {
        "type": "advisor_result",
        "text": "Use a channel-based coordination pattern. The tricky part is draining in-flight work during shutdown: close the input channel first, then wait on a WaitGroup..."
      }
    },
    {
      "type": "text",
      "text": "Here's the implementation using a channel-based coordination pattern..."
    }
  ]
}
```

### Multi-turn example (LiteLLM page, verbatim — whitespace normalized)

```python
import litellm

tools = [
    {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": "claude-opus-5",
    }
]

messages = [
    {"role": "user", "content": "Build a concurrent worker pool in Go with graceful shutdown."}
]

response = litellm.completion(
    model="anthropic/claude-sonnet-5",
    messages=messages,
    tools=tools,
    max_tokens=4096,
)

# Append the full response (includes server_tool_use + advisor_tool_result blocks)
messages.append({"role": "assistant", "content": response.choices[0].message.content})

# Continue the conversation — keep the same tools array
messages.append({"role": "user", "content": "Now add a max-in-flight limit of 10."})

response2 = litellm.completion(
    model="anthropic/claude-sonnet-5",
    messages=messages,
    tools=tools,
    max_tokens=4096,
)
```

**Discrepancy, recorded not resolved**: the comment says the appended value
"includes server_tool_use + advisor_tool_result blocks", but the value appended
is `response.choices[0].message.content` — a Chat Completions content value,
not the block array the "Response with advisor blocks" artifact above
documents (which is a Messages-API-shaped `content` array). The example also
re-uses the *same* `tools` array on the follow-up turn, so it never exercises
the auto-strip rule in Claim 9. Flagged as a documentation gap; the page's only
stated round-trip guarantee is "LiteLLM handles this automatically through
`provider_specific_fields`."

### Non-Anthropic provider example (LiteLLM page, "Advisor Tool with OpenAI executor", verbatim)

```python
import asyncio
import litellm

async def main():
    # executor: openai/gpt-5.6-luna  |  advisor: claude-opus-5
    # LiteLLM runs the orchestration loop automatically
    response = await litellm.anthropic.messages.acreate(
        model="openai/gpt-5.6-luna",
        messages=[
            {"role": "user", "content": "Implement a Python LRU cache with O(1) get and put."}
        ],
        tools=[
            {
                "type": "advisor_20260301",
                "name": "advisor",
                "model": "claude-opus-5",
                "max_uses": 3,
            }
        ],
        max_tokens=1024,
        custom_llm_provider="openai",
    )
    # Final response is clean — no advisor tool_use blocks
    print(response["content"][0]["text"])

asyncio.run(main())
```

Note this example calls the **Anthropic Messages** surface
(`litellm.anthropic.messages.acreate`) with an **OpenAI** executor, then
subscripts the result as `response["content"][0]["text"]` (dict access) while
every other example on the page treats the return value as an object with
attribute access. Recorded as a page inconsistency.

### Gateway config + client request (LiteLLM page, "AI Gateway Usage", verbatim)

```yaml
model_list:
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-5
      api_key: os.environ/ANTHROPIC_API_KEY
```

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-litellm-proxy-key",
    base_url="http://0.0.0.0:4000/v1"
)

response = client.chat.completions.create(
    model="claude-sonnet",
    messages=[
        {"role": "user", "content": "Implement a distributed rate limiter in Python."}
    ],
    tools=[
        {
            "type": "advisor_20260301",
            "name": "advisor",
            "model": "claude-opus-5",
        }
    ],
    max_tokens=4096,
)
```

### Recommended system-prompt blocks (LiteLLM page, verbatim)

Timing guidance (prepend to system prompt):

```
You have access to an `advisor` tool backed by a stronger reviewer model. It takes NO parameters — when you call advisor(), your entire conversation history is automatically forwarded. They see the task, every tool call you've made, every result you've seen.

Call advisor BEFORE substantive work — before writing, before committing to an interpretation, before building on an assumption. If the task requires orientation first (finding files, fetching a source, seeing what's there), do that, then call advisor. Orientation is not substantive work. Writing, editing, and declaring an answer are.

Also call advisor:
- When you believe the task is complete. BEFORE this call, make your deliverable durable: write the file, save the result, commit the change.
- When stuck — errors recurring, approach not converging, results that don't fit.
- When considering a change of approach.

On tasks longer than a few steps, call advisor at least once before committing to an approach and once before declaring done. On short reactive tasks where the next action is dictated by tool output you just read, you don't need to keep calling.
```

Advice weight guidance (add after timing block):

```
Give the advice serious weight. If you follow a step and it fails empirically, or you have primary-source evidence that contradicts a specific claim, adapt. A passing self-test is not evidence the advice is wrong.

If you've already retrieved data pointing one way and the advisor points another: don't silently switch. Surface the conflict in one more advisor call — "I found X, you suggest Y, which constraint breaks the tie?"
```

Cost reduction (optional, add before timing block):

```
The advisor should respond in under 100 words and use enumerated steps, not explanations.
```

### Streaming wire behavior ([platform.claude.com], "Streaming", verbatim — the detail the LiteLLM page omits)

> The advisor sub-inference does not stream. The executor's stream pauses while the advisor runs; then the full result arrives in a single event.
>
> The `server_tool_use` block with `name: "advisor"` signals that an advisor call is starting. The pause begins when that block closes (`content_block_stop`). During the pause, the stream is quiet except for standard SSE `ping` keepalives emitted roughly every 30 seconds. Short advisor calls might show no pings.
>
> When the advisor finishes, the `advisor_tool_result` arrives fully formed in a single `content_block_start` event (no deltas). Executor output then resumes streaming.
>
> A `message_delta` event follows with the updated `usage.iterations` array reflecting the advisor's token counts.

### Advisor-output cap table ([platform.claude.com], "Capping advisor output", verbatim — the knob the LiteLLM page never documents)

```
max_tokens   Mean advisor output tokens   Calls truncated
unset        ~4,200 to 5,900               n/a
2048         ~630 to 840                   ~0%
1024         ~370 to 480                   ~10%
```

with the page's own framing: "In Anthropic's testing on a hard reasoning
benchmark (n = 40 per configuration), this reduced mean advisor output by roughly
7x compared with leaving the cap unset, with near-zero truncation and no
detectable quality degradation."

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch-file
  rate-limit accounting (`POST /v1/batches` charging the whole JSONL to one
  minute, `batch_enqueued_token_limit`). Unrelated surface; the advisor's
  per-sub-inference accounting is a different mechanism and is not covered by
  any of that note's claims.
- `source-notes/docs-litellm-bedrock-invoke.md` — **cited** (Corroborates,
  Claim 6's matrix reading). Its **Claim 3** — "The page's support matrix claims
  Cost Tracking ✅, Logging ✅, Streaming ✅ via `/invoke-with-response-stream`,
  and Load Balancing ✅ on the `/invoke` route — a vendor surface claim with no
  per-provider parity and no caching caveat" — is the exact same epistemic
  object as this page's provider matrix, on the same product, and its
  assessment ("Treat all four ✅ rows as surface-support claims… not
  independently exercised behavior") is the reading applied in Claim 6.
- `source-notes/blog-litellm-auto-router-v2.md` — **cited** (Extends /
  contrast, Claim 1). **Claim 1** ("Auto Router v2 collapses complexity,
  semantic, and adaptive routing into a single `auto_router/complexity_router`
  config, shipping in v1.94.x") and **Claim 3** ("The operational rationale is
  'predictable beats clever for debuggability' — a fixed, versioned
  capability→model mapping is what makes 'why did this response cost 4x today'
  answerable after the fact") together describe the corpus's *request-level*
  routing axis. This page adds a second, *intra-request* axis. Claim 3's
  debuggability criterion is also what Claim 2 undermines: if the advisor
  sub-inference is invisible in top-level `usage`, "why did this response cost
  4x today" is harder to answer here than for a routed request.
- `source-notes/docs-litellm-audio-transcription.md` — **cited** (Corroborates,
  Claim 6's matrix reading). **Claim 5** ("The support matrix documents Cost
  Tracking, Logging, End-user Tracking, Fallbacks, and Loadbalancing as ✅ on this
  non-chat endpoint, and qualifies the lone Guardrails row as 'Applies to output
  transcribed text (non-streaming only)'") — again a LiteLLM ✅ matrix where the
  only honest reading is surface support, and where the one scoping note is the
  operationally load-bearing cell. Same caution applies to this page's matrix,
  whose Notes column does disclose the native-vs-orchestrated split (so this
  page's matrix is *better* than either of those).
- `source-notes/docs-litellm-messages-to-responses-mapping.md` — **cited**
  (Corroborates, Claim 9; the corpus's nearest neighbour). **Claim 1** ("On the
  `/v1/messages` → OpenAI/Azure path, `stop_sequences` and `top_k` are silently
  dropped — a caller setting them gets a 200 with no error and no telemetry that
  the constraint was ignored") is the same hazard class on the same
  Anthropic↔OpenAI boundary with a different carrier: here the rewritten thing
  is *conversation history content blocks*, there it is *request parameters*.
  Also **Claim 7** ("`tools` and `tool_choice` are type-remapped, not passed
  through") is the corpus's existing instance of gateway-side tool *type*
  rewriting, which is precisely what `advisor_20260301` → plain function tool
  named `advisor` is (Claim 5). And **Claim 5** (`thinking.budget_tokens`
  quantized into a four-rung `reasoning.effort` ladder, "inferred thinking depth
  is lossy after translation") is a third instance of "the top-level field is a
  lossy summary of what actually happened."
- `source-notes/blog-litellm-save-claude-code-costs.md` — **cited**
  (Corroborates / tension, Claim 15). **Claim 1** (budget windows with stacked
  durations capping virtual-key spend) and **Claim 3** (auto-injected
  `cache_control` markers enabling Claude's prompt cache without client-side
  changes) are the corpus's two gateway-side spend levers. This page's advisor
  tool introduces a spend dimension those levers were not built to see: the
  client names the advisor model per request (Claim 15, no gateway-side
  allowlist) and the cost lands outside top-level `usage` (Claim 2). A budget
  window is only as good as its metering input.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited** (Extends,
  Claims 8 and 14). That note's **Claim 1** (`max_iterations` + `max_budget_per_session`
  as the A2A gateway's two per-session loop cost controls) and **Claim 3** (over-cap
  → "a 429 Too Many Requests") plus **Claim 5** (429 with
  `type: budget_exceeded`, colliding with rate limiting) establish the corpus's
  existing treatment of loop-budget exhaustion. This page supplies a *third*
  and *fourth* encoding for the same conceptual condition: a named Python
  exception (`AdvisorMaxIterationsError`) and an in-band
  `advisor_tool_result_error` / `max_uses_exceeded` block that arrives on a 200
  (#1461). It also exposes the same gateway-vs-client enforcement asymmetry that
  note recorded from the other direction: here the *conversation*-level cap is
  explicitly client-side (Claim 14) while that note's session-level caps are
  gateway-enforced (and fail open). Together the two notes give Ch05 a
  complete picture of "who is allowed to cap an agent loop" across LiteLLM's
  surfaces.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP
  server for coding agents (`https://langfuse.com/docs/mcp`, transport config,
  Cursor/Windsurf per-client config). Unrelated to the advisor tool; the lexical
  overlap was "tools" and "agent".
- `source-notes/docs-litellm-gateway-auth-reference.md` — **dismissed**: MCP /
  A2A inbound and outbound auth headers and zero-trust JWT signing. The advisor
  page's auth surface is nil beyond the ordinary proxy key, so there is nothing
  to corroborate or contradict here.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  Langfuse guardrail libraries and PII anonymization pipelines. Unrelated.

Additional cross-references found by searching `source-notes/`:

- `source-notes/blog-litellm-swap-openai-code-interpreter.md` — **cited**
  (Corroborates, Claim 5). **Claim 2** ("LiteLLM intercepts the
  `code_interpreter` tool call and re-executes it in a sandbox the operator
  controls, leaving the client request unchanged"), **Claim 3** (the
  intercept → execute → feed-back → tear-down loop with a preserved response
  shape), and **Claim 5** ("On the Chat Completions path the native
  `code_interpreter` tool is rewritten before it reaches OpenAI into a
  `litellm_code_execution` function tool, and each sandbox result is appended as
  a `role: tool` message until the model returns a final answer") are the
  corpus's existing record of a gateway-owned agentic loop. The advisor tool is
  the same architectural pattern with three material differences: the gateway
  makes a *second billable model call* (the code-interpreter swap makes a
  *sandbox* call), the loop bound is a model-call cap rather than
  `max_agentic_loops`, and the loop's output is a **second model's advice**
  rather than a tool result. Worth a Ch05 pairing.
- `source-notes/docs-litellm-anthropic-unified.md` — **cited** (Corroborates,
  Claim 6's matrix reading; and Claim 9's translation family). **Claim 2** ("The
  feature matrix claims Cost Tracking, Logging, End-user Tracking, Streaming,
  Fallbacks, Loadbalancing, and Guardrails are all ✅ on `all supported models` —
  with no per-backend granularity in the table"), whose assessment ("Operators
  should treat the ✅ flags as surface support, not per-provider parity") is the
  corpus's standing caveat applied in Claim 6. Its **Claim 8** (the response is
  Anthropic-format, `content` blocks of type `text`/`tool_use`/`thinking`) and
  **Claim 9** (the `usage` object exposes cache-token accounting) are the same
  wire surface where the advisor's Anthropic-only block types
  (`server_tool_use`, `advisor_tool_result`) have to survive or be stripped —
  i.e. the stripping problem in Claim 9 lands on the route this note describes.
- `source-notes/docs-litellm-claude-code-compatibility.md` — **cited**
  (Corroborates, Claim 6's matrix reading). **Claim 3** ("Cell semantics are
  four-state, not pass/fail — ✅ all three model tiers pass, ❌ at least one tier
  failed…, — no test ran for this combination, n/a not applicable") is the
  corpus's most disciplined matrix-reading guidance; this page's provider table
  uses only ✅ and prose Notes, so it carries none of the four-state discipline
  and should be read strictly more conservatively than that note's matrix.
- `source-notes/docs-litellm-caching-all-caches.md` — **cited** (Extends,
  Claim 11). **Claim 4** (four per-call cache-controls on the `cache={...}`
  kwarg providing runtime bypass and expiry control) and **Claim 9** (three
  distinct TTL knobs with no documented precedence) describe the corpus's
  response-cache model. The advisor's `caching` object is a *different kind of
  thing* — per `platform.claude.com` it "is not a breakpoint marker. It is an
  on/off switch. The server determines where cache boundaries go" — and it
  caches the advisor's *own quoted transcript*, a cache population the client
  never authors and cannot inspect. So the corpus has no existing note covering
  a cache whose key the client cannot see; that is new.
- `source-notes/docs-litellm-token-usage-helpers.md` — **cited** (Corroborates,
  Claim 2 and Claim 3). **Claim 3** ("`cost_per_token` computes USD for prompt
  (input) and completion (output) tokens entirely from LiteLLM's bundled
  `model_cost` map … with no provider-side billing input") and **Claim 4**
  ("`completion_cost` returns the overall per-call USD figure by composing
  `token_counter` and `cost_per_token`") are the corpus's client-side cost
  calculation path. Those helpers take *the* `input_tokens`/`output_tokens` as
  given — and per Claim 2 those fields are executor-only, so `completion_cost`
  on an advisor request returns a *systematically understated* USD figure with
  no error. That is a direct, actionable interaction: the corpus already
  documents the helper; this note documents the input it silently gets wrong.
  Also its **Claim 5** (usage in the response payload is a default, but
  streaming usage is opt-in via `stream_options`) compounds with Claim 4: on a
  streamed advisor request, the operator needs `include_usage` *and* must read
  `iterations[]`.
- `source-notes/docs-litellm-streaming-token-usage.md` — **cited**
  (Corroborates, Claim 4's assessment). **Claim 1** ("A streaming completion
  does not report token usage unless the client opts in with
  `stream_options={\"include_usage\": True}`") is the existing corpus record of
  streamed-traffic accounting gaps. This page adds a *second* independent
  requirement on the same path: pass `include_usage` **and** parse
  `usage.iterations[]` for the advisor share (and per
  `platform.claude.com`, that array is delivered in a trailing `message_delta`
  event, which is a *third* thing to get right).
- `source-notes/docs-litellm-adaptive-router.md` — **cited** (Extends /
  contrast, Claim 1). **Claim 2** ("The router balances quality against cost
  per request type using a multi-armed-bandit-style mechanism") is the corpus's
  per-request-type cost/quality mechanism. Its **Claim 6** (the router
  classifies every request into one of 7 types) and **Claim 3** (Postgres
  required for learned state) mark it as a *decision* made before generation.
  The advisor tool is a second model chosen *during* generation; the two are
  composable and a guide that teaches only one leaves an obvious gap.
- **Corroborates**: the two `docs-litellm-anthropic-unified` /
  `docs-litellm-bedrock-invoke` / `docs-litellm-audio-transcription` /
  `docs-litellm-claude-code-compatibility` support-matrix claims (the ✅ =
  surface-support caveat, Claim 6); `docs-litellm-messages-to-responses-mapping`
  Claims 1, 5, 7 (lossy gateway translation on the Anthropic↔OpenAI boundary,
  Claims 2 and 9);
  `blog-litellm-swap-openai-code-interpreter` Claims 2, 3, 5 (gateway-owned
  agentic loop, Claim 5); `blog-litellm-save-claude-code-costs` Claims 1, 3
  (gateway spend levers whose metering input this feature undermines, Claim 15);
  `docs-litellm-token-usage-helpers` Claims 3, 4 (the cost helper that gets
  the wrong input, Claim 2).
- **Contradicts**:
  - **#1461** (filed before this PR per MINER §4a): the `max_uses` failure
    encoding. This page: "Enforces `max_uses` as a hard cap;
    `AdvisorMaxIterationsError` is raised if exceeded". Linked Anthropic page
    (quoted in Claim 8): further advisor calls "return an
    `advisor_tool_result_error` with `error_code: \"max_uses_exceeded\"`…
    The request itself does not fail." Same field, same beta program, opposite
    failure channel. No verdict picked (Claim 8).
  - **#1462** (filed before this PR per MINER §4a): advisor-model pairing. This
    page's intro says the advisor is "Opus 4.6" while its "Model Compatibility"
    section says "`claude-opus-5`", its table is a three-row subset of its own
    prose, and its "The advisor is an Opus model" rule is narrower than
    upstream's capability floor ("The advisor must be Claude Sonnet 4.6 or a more
    capable model, and it must be at least as capable as the executor"). No
    verdict picked (Claim 12).
  - No claim-level opposition with any existing **source note**. The nearest
    candidates are structural *analogues* rather than disagreements:
    `docs-litellm-a2a-iteration-budgets` Claim 3/5 encodes over-cap as HTTP 429
    (a third encoding, not a competing claim about this feature), and
    `docs-litellm-caching-all-caches` Claim 9 documents *response*-cache TTL
    precedence, which the advisor's server-side `caching` switch does not
    contradict so much as bypass.
- **Extends**: `blog-litellm-auto-router-v2` (Claim 1 adds the intra-request
  axis to a corpus that only has the per-request axis; Claim 3's
  "answerable after the fact" debuggability test is the standard this feature
  currently fails on cost); `docs-litellm-adaptive-router` (same: a
  cost/quality lever chosen before vs during generation);
  `docs-litellm-a2a-iteration-budgets` (a third and fourth loop-cap failure
  encoding, plus the gateway-enforced vs client-enforced cap split);
  `docs-litellm-caching-all-caches` (first corpus note of a cache the client
  cannot author or inspect); `docs-litellm-messages-to-responses-mapping`
  (first note of *conversation-history* rewriting as the translation carrier).
- **Novel**: The first corpus note on **within-request** (intra-request) model
  composition as a distinct cost/quality axis. The first note on a **top-level
  response metric that systematically under-reports the expensive path**
  (`usage` excludes advisor tokens entirely). The first note on a
  **non-streaming sub-inference inside a stream** and the inter-token-gap
  alerting consequence. The first note on a gateway **stripping Anthropic-only
  content-block types out of conversation history** to keep non-Anthropic
  providers from 400-ing. The first note on a **client-supplied, un-allowlisted
  second model** as a spend-governance gap on a shared gateway. The first note
  with a **vendor-published cache break-even threshold for a per-call knob**
  (3+ calls per conversation). And the first note where the **same vendor page
  contradicts both itself and its upstream spec** on two separate points
  (#1461, #1462).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — §Provider parity in the shared
  forwarding path (guide/05-llm-ops-reliability.md:343)**: the existing rule is
  scoped to *parameters*: "Present-but-null and omitted are not equivalent
  across 'OpenAI-compatible' backends — how a parameter's absence is expressed
  is a compatibility surface, not an implementation detail." This page supplies
  an independent instance of the same class where the carrier is **conversation
  history**, and the mechanism is a *strip*, not an *omit*: LiteLLM removes
  `advisor_tool_result` / `server_tool_use` blocks from re-sent history
  specifically so non-Anthropic providers never see Anthropic-specific types,
  and separately auto-strips advisor result blocks when the tool is absent from
  the current request "to prevent the Anthropic 400 error that would otherwise
  occur" (Claim 9). **Recommend adding a companion rule** rather than editing
  the existing one: *a gateway that rewrites conversation history is a second
  compatibility surface — audit what it strips, and never assume the transcript
  you sent is the transcript the provider received.* Also record the
  inversion: the guide's rule warns against forwarding a falsy parameter; this
  feature is a case where the gateway must **withhold** an entire block type, and
  the operator loses the ability to see the transformation after the fact.
- **Chapter 05 — model-selection / cost-and-capacity section**: add the second
  axis. The chapter's routing material (ComplexityRouter / Auto Router v2 /
  Adaptive Router — `blog-litellm-auto-router-v2.md` Claim 1,
  `docs-litellm-adaptive-router.md` Claim 2) teaches *classify-then-route*.
  Add *escalate-mid-generation*: a cheap executor consults a bigger advisor
  inside the request, and the trade is a small second sub-inference for planning
  quality. Per the Prospector's bounding, state it as an **emerging, vendor-
  documented pattern with no published evals** — explicitly do **not** import
  "You get close to advisor-solo quality" as established (Claim 1). Add the
  enforcement asymmetry as a table: per-request cap is gateway-side
  (`max_uses`), per-conversation cap is **client-side only** ("count advisor
  calls client-side… remove the advisor tool from `tools`", Claim 14), and the
  per-call output cap (`max_tokens` on the tool definition) is **not documented
  on this page at all** (Claim 13).
- **Chapter 05 — gateway-orchestration material**: add the advisor loop as a
  named, inspectable case study of the gateway running the agentic loop itself
  (`AdvisorOrchestrationHandler`), pairing with the existing code-interpreter
  swap note (`blog-litellm-swap-openai-code-interpreter.md` Claims 2, 3, 5).
  The distinguishing operational point: this loop makes a **second billable
  model call** inside one client request, so provider rate limits, credentials,
  and capacity plans must account for roughly double the upstream calls the
  client's own request count implies — and per `platform.claude.com` the
  advisor "draws from the same per-model bucket as direct calls to the advisor
  model."
- **Chapter 02 (Observability) — cost/usage attribution**: this is the
  worked example the chapter's "the top-level metric hides the expensive path"
  argument needs. Concrete material: top-level `usage` is **executor-only**;
  advisor tokens live only in `usage.iterations[]` with `type: "advisor_message"`
  and are billed at Opus rates; the page's own example shows the advisor entry
  at `823` in / `1612` out against a top-level `412` / `531` (Claim 2); and the
  example is arithmetically wrong against the summing rule upstream states, so
  it must not be used as a template (Claim 3). Add the two derived rules: (1) a
  per-request cost calculator that reads `usage.input_tokens`/`output_tokens`
  **under-reports this feature by the advisor share**, and `completion_cost`
  (`docs-litellm-token-usage-helpers.md` Claims 3, 4) inherits that error with
  no signal; (2) on a streamed request the operator needs **both**
  `stream_options={"include_usage": True}` (`docs-litellm-streaming-token-usage.md`
  Claim 1) **and** an `iterations[]` parse. Add the alert-shape note: on the
  orchestration path the client may see **no** advisor blocks at all
  ("Final response is clean — no advisor tool_use blocks", Claim 7), so
  "`advisor_message` appeared in `iterations[]`" is the only available
  evidence-of-advisor-ran signal.
- **Chapter 02 — latency/stream alerting**: add the non-streaming-sub-inference
  carve-out. "The advisor sub-inference does not stream. The executor's stream
  pauses while the advisor runs, then the full advisor result arrives in a
  single event" (Claim 4) means a healthy stream can go silent for the duration
  of an Opus sub-inference; per `platform.claude.com` the only traffic during
  the pause is "standard SSE `ping` keepalives emitted roughly every 30 seconds.
  Short advisor calls might show no pings." Recommend: (a) client/proxy
  stream-idle timeouts budgeted above worst-case advisor duration; (b) an
  explicit advisor-call exemption in any inter-token-gap SLO, or it will page on
  correct behavior; (c) audit the gateway's SSE re-wrap, since the
  orchestration path synthesizes the stream and the page does not say whether
  the pause survives it.
- **Chapter 03 (Runbooks and Agents)**: the loop-cap signal is
  **not vendor-neutral**, and the guide should say so rather than teach a single
  encoding. The corpus now has four documented shapes for "the loop ran out of
  budget": HTTP 429 `type: budget_exceeded` (`docs-litellm-a2a-iteration-budgets.md`
  Claims 3, 5), a named `AdvisorMaxIterationsError` exception, an in-band
  `advisor_tool_result_error` / `max_uses_exceeded` block on a **200** (with
  upstream's seven `error_code` values the gateway page does not document at
  all), and a client-side counter. Runbook implication: "cap reached" is a
  **degraded success** in at least one documented encoding, so an agent that
  looks healthy may be running unadvised. Pair with the beta-gate governance
  point (Claim 10): the feature is enabled on a shared gateway by a **request
  body field**, not by operator config, so beta-admission cannot be enforced by
  a model-name allowlist.
- **Ch05 §spend governance (new caveat on existing content)**: the advisor
  model is named **per request by the client** with no gateway-side allowlist
  or `advisor_model` key in the documented `config.yaml` (Claim 15). Existing
  gateway spend levers — budget windows, budget fallback chains
  (`blog-litellm-save-claude-code-costs.md` Claims 1, 2) — bound spend at the
  key, but their metering input is the top-level `usage`, which by Claim 2
  excludes the advisor. Recommend a note: *a gateway spend control is only as
  accurate as the usage fields it meters, and a feature that bills a hidden
  sub-inference defeats both the control and the dashboard.*

## Extraction Notes

- Primary source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/completion/anthropic_advisor_tool`, HTTP 200,
  no paywall, no login). The page is a focused topic page; all running-text
  quotes are contiguous verbatim strings from the fetched page. Two table
  blocks (provider matrix, model compatibility) are reproduced with rows
  flattened for readability — the row *contents* are verbatim and the row count
  is the page's row count.
- **Linked page followed (MINER §1)**: the page's "Additional Resources" links
  `https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool`,
  which is the normative spec for the same `advisor_20260301` tool and is the
  page's own primary reference. Read in full. Every quote from it in this note
  is attributed inline to `platform.claude.com` and is confined to: Claims 2,
  3, 4, 5, 6, 7, 8, 11, 12, 13 and the three `[platform.claude.com]`-labeled
  Concrete Artifacts. This is what surfaced contradictions #1461 and #1462, and
  it is also the source of the wire-level streaming detail, the seven
  `error_code` values, the `max_tokens` output-cap table, the `clear_thinking`
  caching warning, the rate-limit-bucket statement, and the
  `advisor_redacted_result` observability caveat. It is cited as a *comparison
  layer*, not as this note's `source_url`; a reader wanting only LiteLLM's own
  claims can ignore every `[platform.claude.com]`-marked passage and still have
  a complete LiteLLM picture.
- Prospector triage bounding honored (issue #1456, `triaged:text`,
  `priority:high`, chapters Ch05/Ch02/Ch03). All three triage comments
  independently converged on the same four contracts (cost split, streaming
  pause, `max_uses`/error, history-mutation + beta header), and each is covered
  (Claims 2, 4, 8, 9, 10). The Prospector's flagged internal inconsistency —
  prose "an Opus model (`claude-opus-5`)" vs intro "Opus 4.6" — is recorded in
  Claim 12 and filed as **#1462**; **no side was picked**, per instruction.
- **Two contradictions filed before this PR, per MINER §4a**: **#1461**
  (`max_uses` failure encoding: `AdvisorMaxIterationsError` vs in-band
  `advisor_tool_result_error` / `max_uses_exceeded`, where the request "does not
  fail") and **#1462** (advisor-model pairing: intro "Opus 4.6" vs Model
  Compatibility `claude-opus-5`, Opus-only rule vs upstream's "Sonnet 4.6 or a
  more capable model" capability floor, and a table that is a subset of the
  page's own prose). Both quotes are recorded in Claims 8 and 12; neither note
  picks a verdict. Neither duplicates an existing open `contradiction`-labeled
  issue (checked: #1150, #1307, #1322, #1338, #1352, #1408) or an existing
  `C-NNN` entry.
- `miner-related-notes.md` was read **before** writing Cross-References; all ten
  candidate paths are cited or dismissed above. Cross-reference verification
  (MINER §4b) re-read the cited claims in
  `docs-litellm-messages-to-responses-mapping.md` (Claims 1, 5, 7),
  `blog-litellm-swap-openai-code-interpreter.md` (Claims 2, 3, 5),
  `docs-litellm-token-usage-helpers.md` (Claims 3, 4, 5),
  `docs-litellm-anthropic-unified.md` (Claims 2, 8, 9),
  `docs-litellm-claude-code-compatibility.md` (Claim 3),
  `docs-litellm-bedrock-invoke.md` (Claim 3), `docs-litellm-audio-transcription.md`
  (Claim 5), `blog-litellm-save-claude-code-costs.md` (Claims 1, 3),
  `blog-litellm-auto-router-v2.md` (Claims 1, 3),
  `docs-litellm-a2a-iteration-budgets.md` (Claims 1, 3, 5),
  `docs-litellm-caching-all-caches.md` (Claims 4, 9),
  `docs-litellm-streaming-token-usage.md` (Claim 1), and
  `docs-litellm-adaptive-router.md` (Claims 2, 3, 6) — content confirmed
  against what each is cited for. No claim numbers invented; non-claim material
  is cited by section name.
- **Discrepancies recorded but deliberately NOT filed as contradictions**
  (MINER §4a "when NOT to file" — each is a documentation defect or a
  documented gap, not a pair of claims that would yield different guide advice):
  (a) the `usage` example's `input_tokens: 412` vs upstream's `1760` (Claim 3 —
  arithmetic, resolvable by a human in one minute; upstream is the spec);
  (b) the multi-turn example's comment claiming advisor blocks are included in
  an appended Chat Completions `message.content` string, and its re-use of the
  same `tools` array so the auto-strip rule is never exercised (Claim 9);
  (c) the OpenAI-executor example calling the Anthropic Messages surface and
  then subscripting the result as a dict while every other example uses
  attribute access (Claim 7); (d) the table's dated executor ID
  `claude-haiku-4-5-20251001` vs upstream's `claude-haiku-4-5` (Claim 12);
  (e) LiteLLM's provider matrix listing Bedrock/Vertex ✅ while upstream says
  the advisor tool "is not currently available on Amazon Bedrock, Google Cloud,
  or Microsoft Foundry" — reconcilable if Bedrock/Vertex are the *executor*
  and the advisor sub-inference still goes to Anthropic, but the page never says
  where the sub-inference is sent, so it is recorded as an open question
  (Claim 6), not a conflict.
- **Open questions deliberately left open (not asserted)**: (1) where the
  advisor sub-inference is routed when the executor is Bedrock/Vertex/Groq
  (Claim 6 — data-residency and credential implications); (2) whether the
  `advisor_20260301` → plain-`advisor`-function-tool rewrite changes the
  executor's tool-selection behavior versus the native path, i.e. whether the
  orchestration loop is semantically faithful (Claim 5); (3) whether the
  gateway-synthesized SSE stream on the orchestration path reproduces the
  documented stream pause (Claim 4); (4) whether the client can observe
  advisor calls at all on the non-Anthropic path (Claim 7 — single code comment
  as evidence); (5) whether advisor sub-inference tokens count toward
  LiteLLM's own spend logs, virtual-key budgets, or rate limits — **the page
  never says**, and that was the Prospector's first question; it is recorded
  here as unstated rather than guessed.
- Vendor-docs caveat carried throughout: every claim is bounded to "the gateway
  documents this" / "the page documents this knob." No measured latency, no
  published cost arithmetic, no production experience, and no eval for the
  "close to advisor-solo quality" claim appear on the page. The 35–45% advisor-
  output reduction (Claim 13) and the 3+ call caching threshold (Claim 11) are
  vendor-reported numbers with no published method and must not be used as
  planning inputs. `confidence_overall: emerging` for exactly this reason —
  matching the sibling LiteLLM notes' treatment of documented capability
  surfaces. `date_published` is unknown (living Docusaurus page; beta header
  dated 2026-03-01); `date_extracted` and `last_checked` are both 2026-09-25.
