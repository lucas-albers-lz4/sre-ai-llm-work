---
source_url: https://docs.litellm.ai/docs/completion/prefix
source_type: docs
title: "Pre-fix Assistant Messages | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-10-06)
date_extracted: 2026-10-06
last_checked: 2026-10-06
status: current
confidence_overall: emerging
issue: "#1542"
---

# Pre-fix Assistant Messages (LiteLLM Docs)

> The reference page for LiteLLM's assistant-prefill feature: a **message-level**
> `prefix: true` flag (not a completion parameter) that makes the model continue
> a pre-filled assistant turn, published as a three-name provider list
> (Deepseek, Mistral, Anthropic) and gated by a capability field whose name —
> `supports_assistant_prefill` — differs from the wire key the client sends.
> Its main ops value is the **capability-introspection pair**
> (`litellm.get_model_info(model=...)` and `GET /v1/model/info`): the corpus's
> second independent pre-flight support probe, applied to a flag whose
> mismatch behavior (prefill routed onto a non-supporting model via fallback)
> the page never documents.

## Source Context

- **Type**: docs (single-page LiteLLM vendor reference at
  `/docs/completion/prefix` — verified HTTP 200 this session, matching
  `source_url`). Page title: "Pre-fix Assistant Messages". Site breadcrumb per
  the page's own nav: "Guides → Prompts & Context → Pre-fix Assistant
  Messages". Nav siblings in the same section: `message_trimming`,
  `predict_outputs`, `prompt_compression`, `prompt_caching`,
  `prompt_formatting` — all already mined as separate notes (see Cross-
  References); none was followed as a sub-page.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented* feature surface: it gives the wire shape,
  two runnable quickstarts (SDK + proxy curl), one sample response, and two
  executable capability probes. No independent validation, no metrics, no
  latency/cost data, no error-behavior section, and the page is undated.
- **Scope**: The `prefix` assistant-prefill flag only: wire shape, supported
  provider list, SDK and proxy quickstarts, one expected response, and the
  "Check Model Support" introspection section. Does NOT cover: what happens
  when the flag reaches a model that does not support it (Claim 5), streaming
  interaction, per-provider caveats, a LiteLLM version gate (the sibling
  predicted-outputs page carries a "Supported from LiteLLM Version" row; this
  page carries none), the supported-params gate surface
  (`docs-litellm-drop-params.md`, #1480 — not re-derived here), or prompt
  caching (a different mechanism entirely; see Cross-References).
- **Redundancy**: `docs-litellm-completion-predict-outputs.md` (#1541) Claim 11
  already mined this page **as contrast evidence** — provider list and probe
  quoted there, with an explicit note that "the prefill page is **not**
  covered by this note (its own issue is filed separately)". This note is
  that separately-filed extraction. `docs-litellm-completion-message-trimming.md`
  (#1510) recorded this page as deliberately-unmapped ("noted here only so the
  next Miner knows it is unmapped"). Nothing else in the corpus covers it
  (re-verified: no other note matches `completion/prefix`).

## Extracted Claims

### Claim 1: Assistant prefill is a per-message flag — `"prefix": true` on an assistant message object — not a top-level `completion()` parameter
- **Evidence**: The page's opening wire-shape snippet, plus both quickstarts:
  the SDK example passes `prefix` **inside** the message dict
  (`{"role": "assistant", "content": "Argentina", "prefix": True}`) and the
  `completion()` call itself carries no `prefix` kwarg; the proxy curl example
  reproduces the same shape inside `messages[]`.
- **Confidence**: settled (explicit code on both documented paths; the shape
  is directly re-checkable against the page)
- **Quote**: `"prefix": true # 👈 KEY CHANGE`
- **Our assessment**: The placement is the load-bearing detail and it puts
  this flag **outside** the parameter family the corpus has mined so far:
  `docs-litellm-completion-input-params.md` documents the `completion()`
  *input-param* surface and its supported-params gate, and
  `docs-litellm-drop-params.md` documents the gate keyed on top-level OpenAI
  params — but a field nested inside a message object is not a top-level
  param, so neither page's machinery is documented as applying to it. Whether
  `drop_params` ever touches an in-message `prefix` field is **not stated
  anywhere** and is recorded as an open question (Claim 5), not inferred.
  Operationally, the message-level placement also means the flag travels with
  the conversation: any middleware that serializes/normalizes `messages[]`
  (trimming, mapping, caching wrappers) can silently drop or preserve it, and
  the page documents no signal either way — the same absent-signal shape
  `docs-litellm-drop-params.md` Claim 9 records for the param gate.

### Claim 2: Support is published as a three-name provider list — Deepseek, Mistral, Anthropic — at provider granularity, with no model-level table, no version gate, and only one model ever instantiated on the page
- **Evidence**: The "Supported by:" list directly under the page title; the
  only model string the page ever uses is `deepseek/deepseek-chat` (both
  quickstarts and the probe example). Unlike the sibling predicted-outputs
  page, there is no "Supported providers" property table, no per-model
  breakdown, and no "Supported from LiteLLM Version" row.
- **Confidence**: settled for the **list as published** (read directly from
  the page); the list's *completeness* and model-level reliability are
  explicitly **not** established here (see assessment)
- **Quote**: "Supported by:" / "Deepseek" / "Mistral" / "Anthropic"
- **Our assessment**: This is the page's biggest footgun, and the corpus
  already contains the counterexample. The list reads as a provider-level
  guarantee, but `blog-litellm-claude-fable-5-day-0.md` Claim 4 documents
  that Anthropic's own current flagship — Fable 5 — does **not** support
  assistant message prefill ("fixed thinking budgets, temperature, top_p, and
  assistant message prefill are not supported by the model"), and
  `guide/05-llm-ops-reliability.md` ~L327-330 already carries that as a
  migration hazard. So "Anthropic" on this list is true only at *some*
  model   granularity, and the page gives no table to resolve which. Per MINER
  §4a this is a **conditioning variable** (provider list vs a model-level
  exception), not a contradiction — both statements are true at different
  granularity — so no contradiction issue is filed; the pairing is recorded
  under Cross-References. The guide-relevant rule is the one the params
  matrix pages already established — `docs-litellm-drop-params.md` Claim 2
  ("LiteLLM maps all supported openai params by provider + model") and the
  support-matrix caption quoted in `docs-litellm-completion-input-params.md`
  ("Support is model dependent within a provider … so call the function for
  the exact model you use"): **a provider name is not an audit
  instrument**. The single instantiated model (`deepseek/deepseek-chat`) is
  also the page's entire empirical base — Anthropic and Mistral support are
  asserted by the list alone, with no worked example.

### Claim 3: The capability gate has a distinct name from the wire key — `supports_assistant_prefill` (what you check) vs `prefix` (what you send) — exposed via `litellm.get_model_info(model=...)`
- **Evidence**: The "Check Model Support" section's intro sentence plus its
  SDK code block, where the asserted key is spelled out. The flag name appears
  nowhere in the wire-shape snippet or either quickstart.
- **Confidence**: settled (explicit vendor statement plus runnable assert)
- **Quote**: "Call `litellm.get_model_info` to check if a model/provider supports `prefix`."
- **Our assessment**: Two things worth recording. (1) **The name mismatch is
  a real ops trap**: an operator grepping `config.yaml` or a dashboard for
  `prefix` will not find the capability field, and one grepping
  `supports_assistant_prefill` will not find the wire key — a support audit
  must know both names and that they differ. This is the same
  check-name ≠ send-name split the corpus recorded for
  `max_retries`/`num_retries` in `docs-litellm-completion-input-params.md`
  Claim 2, here on a capability surface instead of a knob surface. (2) The
  probe's **semantics are inherited, not stated on this page**:
  `docs-litellm-completion-function-call.md` Claims 1-3 establish how this
  model-record lookup family behaves — a fail-closed inventory of *declared*
  capability read from LiteLLM's remotely-updatable model cost map (Claim 2:
  "an unknown model, a missing key, or *any* exception all resolve to
  `False`"; Claim 3: the matrix is "a field in a **remote JSON artifact
  served from `main`**"). The prefix page documents neither property, but
  `get_model_info(model=...)` is the same helper that note's Claim 3
  dissects, so a `supports_assistant_prefill` answer should be read the same
  way: declared, not measured, and refreshable under a running gateway. One
  sharp difference in failure mode, flagged as Miner inference from the two
  artifacts: the prefix page's example uses **bracket indexing**
  (`params["supports_assistant_prefill"]`), which raises `KeyError` when the
  key is absent from the record, whereas the `supports_*` predicates return
  `False`. The published probe pattern therefore crashes on an undeclared
  model rather than failing closed — arguably the louder, but also the
  unhandled, of the two. The page does not discuss this; we do not assert the
  runtime behavior, only the shape of the example.

### Claim 4: The proxy exposes the same capability inventory at `GET /v1/model/info` — models plus supported params — the routing-time introspection route for gateway operators
- **Evidence**: The "Check Model Support" section's proxy half: one prose
  sentence plus a curl example against the local proxy with a bearer key.
- **Confidence**: settled (explicit vendor statement of endpoint and
  payload content)
- **Quote**: "Call the `/model/info` endpoint to get a list of models + their supported params."
- **Our assessment**: This is the second distinct introspection surface in
  the corpus for pre-flight capability checks — the first is
  `litellm.get_supported_openai_params(...)` on the params gate
  (`docs-litellm-drop-params.md` Claim 2, `docs-litellm-completion-input-params.md`
  Claim 8). Together they give an operator two *different* questions to ask
  before routing: "which params does this deployment accept?" and "does it
  carry this specific capability flag?" — and only the second answers the
  prefill question. The page does not say (a) whether `supports_assistant_prefill`
  is actually present in the `/v1/model/info` response for every model, (b)
  whether the gateway consults it when admitting a request, or (c) whether
  fallback/Router machinery consults it when moving one — (c) is the gap in
  Claim 5. It also does not say whether the SDK probe and the HTTP route read
  the same underlying record (the corpus's cost-map finding in
  `docs-litellm-completion-function-call.md` Claim 3 suggests they do, but
  neither page states it). The guide-relevant pattern is the *pair*: check
  the flag in-process at config time with `get_model_info`, and expose the
  same field via `/model/info` for auditing a live fleet.

### Claim 5: The page documents no behavior for the mismatch case — a `prefix: true` request routed or fallback-shifted onto a non-supporting model is an undocumented gap (with no error, drop, or fallback statement anywhere)
- **Evidence**: Verified by full-page read. The page has exactly five prose
  units beyond headings: the "Supported by:" list, the two quickstart
  sentences (implicit), "Expected Response", the `get_model_info` intro
  sentence, and the `/model/info` sentence. None addresses unsupported-target
  behavior, error classes, `drop_params` interaction, streaming, latency,
  per-provider caveats, or fallback. The section inventory is reproduced in
  Concrete Artifacts.
- **Confidence**: settled as a **documentation absence** (the page is short
  and was read end-to-end; the omission is re-checkable); it is *not* a claim
  about runtime behavior — what the gateway actually does is unknown from
  this source, which is precisely the finding the Prospector asked to record
- **Quote**: (no direct quote; the page contains no sentence describing
  mismatch behavior — see the section inventory and paraphrase in Our
  assessment)
- **Our assessment**: Record the gap, do not fill it. The question matters
  because the two mechanisms that *move requests between models* are both
  documented elsewhere and neither is wired to this flag in the docs:
  (1) `docs-litellm-completion-input-params.md` Claim 13 documents SDK
  `fallbacks` as "calls each entry once, in order" across a model list with
  no capability re-check mentioned — so a prefill-bearing request whose
  primary fails will be attempted against fallback targets that may lack
  `supports_assistant_prefill`, and the page before us says nothing about
  what then happens (reject loudly like the default param gate? silently
  strip the flag like `drop_params`'s silent branch? forward it and let the
  provider error?). (2) The gateway-side admission question is equally open:
  nothing states whether the proxy validates `prefix` against
  `supports_assistant_prefill` at `/v1/chat/completions` or passes the field
  through. The honest synthesis for the guide is a **pre-flight rule**: the
  probe (Claims 3-4) must be evaluated against *every* model a request can
  reach — primary **and** each fallback target — because post-routing
  behavior on an unsupported target is undocumented. Also absent and noted
  for completeness: streaming interaction (`prefix` + `stream=True`), any
  latency/quality claim the feature would presumably motivate, and a version
  gate telling operators when the flag started existing.

### Claim 6: The expected response demonstrates prefill semantics concretely — the model *continues* the pre-filled assistant turn with a leading space — and the sample payload's `created` epoch is ~2 years stale
- **Evidence**: The "Expected Response" JSON block: the answer to
  "Who won the world cup in 2022?" prefixed by the canned assistant turn
  `"Argentina"` comes back as a continuation, and the `created` value
  1723323084 resolves to 2024-08-10T20:51:24Z.
- **Confidence**: settled for the response shape (verbatim artifact); the
  staleness observation is a directly checkable unit conversion
- **Quote**: `"content": " won the FIFA World Cup in 2022."`
- **Our assessment**: The leading space in the content is the whole feature
  in one character: the model is not answering the user's question, it is
  completing the assistant message the caller pre-filled — so downstream
  consumers must expect continuation output (leading whitespace, no question
  re-anchoring) rather than a self-contained answer. Anything that asserts on
  response content (eval harnesses, stop-sequence logic, JSON parsers) sees a
  different output class on prefill routes. The sample also quietly confirms
  the feature composes with an ordinary `usage` object (`prompt_tokens: 16`,
  `completion_tokens: 12`) — no special billing surface is documented. The
  staleness half: `created: 1723323084` = **2024-08-10**, ~2 years before
  this extraction, so the page's flagship example has not been refreshed —
  the same documentation-liveness finding `docs-litellm-mock-requests.md`
  Claim 4 records for a sibling page's sample (epoch 2023-09-11). Two pages,
  same pattern: vendor sample payloads age silently with no stated "as of"
  field, so they are evidence of *shape*, never of *current* behavior.

### Claim 7: The identical message shape is shown on both documented paths — SDK `completion()` and proxy `POST /v1/chat/completions` — but with a single shared "Expected Response" and no statement that the gateway validates the flag
- **Evidence**: The Quick Start section's SDK and PROXY tabs carry the same
  user/assistant message array (only the wrapping differs); the "Expected
  Response" block sits after the tab group, presented once for both. The
  proxy curl targets `http://0.0.0.0:4000/v1/chat/completions` with a
  `Bearer $LITELLM_KEY`.
- **Confidence**: emerging (the request shapes are explicit; that the sample
  response represents the *proxy* path specifically is the page's layout
  implication, not a labelled attribution, and no gateway-side validation
  behavior is documented)
- **Quote**: `curl http://0.0.0.0:4000/v1/chat/completions \` (line 1 of the
  proxy quickstart, verbatim)
- **Our assessment**: The proxy example is what makes this page
  ops-relevant rather than SDK-only: it shows a message-level flag accepted
  on the shared ingress endpoint every fleet client uses. But "accepted" is
  all it shows — the page never says whether the proxy *checks*
  `supports_assistant_prefill` before forwarding (the admission half of
  Claim 5's gap). Given `docs-litellm-drop-params.md` established that the
  param gate's default is a loud raise precisely because the vendor chose to
  validate, the silence here on a message-level field is noticeable: an
  operator cannot infer either "validated" or "forwarded blindly" from this
  page. Stated as an open sub-question, per the Prospector's instruction to
  record rather than resolve.

## Concrete Artifacts

All artifacts verbatim from https://docs.litellm.ai/docs/completion/prefix
(line structure recovered from the raw HTML, whose code lines are delimited
by `<br>` tokens — the flattened markdown render collapses them).

### Page-level wire shape (verbatim, section intro)

```json
{
  "role": "assistant", 
  "content": "..", 
  ...,
  "prefix": true # 👈 KEY CHANGE
}
```

### Quick Start — SDK (verbatim)

```python
from litellm import completion
import os 

os.environ["DEEPSEEK_API_KEY"] = ""

response = completion(
  model="deepseek/deepseek-chat",
  messages=[
    {"role": "user", "content": "Who won the world cup in 2022?"},
    {"role": "assistant", "content": "Argentina", "prefix": True}
  ]
)
print(response.choices[0].message.content)
```

### Quick Start — PROXY (verbatim)

```bash
curl http://0.0.0.0:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -d '{
    "model": "deepseek/deepseek-chat",
    "messages": [
      {
        "role": "user",
        "content": "Who won the world cup in 2022?"
      },
      {
        "role": "assistant", 
        "content": "Argentina", "prefix": true
      }
    ]
}'
```

### Expected Response (verbatim)

```json
{
    "id": "3b66124d79a708e10c603496b363574c",
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": " won the FIFA World Cup in 2022.",
                "role": "assistant",
                "tool_calls": null,
                "function_call": null
            }
        }
    ],
    "created": 1723323084,
    "model": "deepseek/deepseek-chat",
    "object": "chat.completion",
    "system_fingerprint": "fp_7e0991cad4",
    "usage": {
        "completion_tokens": 12,
        "prompt_tokens": 16,
        "total_tokens": 28,
    },
    "service_tier": null
}
```

Note the trailing comma after `"total_tokens": 28,` — reproduced as published;
the block is illustrative JSON, not parseable JSON.

### Check Model Support — SDK probe (verbatim)

```python
from litellm import get_model_info

params = get_model_info(model="deepseek/deepseek-chat")

assert params["supports_assistant_prefill"] is True
```

### Check Model Support — PROXY route (verbatim)

```bash
curl -X GET 'http://0.0.0.0:4000/v1/model/info' \
-H 'Authorization: Bearer $LITELLM_KEY' \
```

### Section inventory (for Claim 5's absence finding)

The page, in order: H1 "Pre-fix Assistant Messages" → "Supported by:" list
(Deepseek / Mistral / Anthropic) → wire-shape block → H2 "Quick Start"
(SDK | PROXY tabs) → "Expected Response" block → H2 "Check Model Support"
(`get_model_info` sentence → SDK | PROXY tabs → `/model/info` sentence →
curl block) → page footer. No other content sections exist.

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path cited or
dismissed):

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch input-file
  rate limiting and per-record token accounting; no message-shape or
  capability-gate overlap with assistant prefill.
- `source-notes/docs-litellm-completion-input-params.md` — **Cited
  (Extends / boundary)**: its scope owns the `completion()` **input-param**
  surface, and this page sits just outside it — `prefix` is an in-message
  field, not a completion kwarg (Claim 1). **Claim 13** of that note
  (SDK `fallbacks` = "calls each entry once, in order", no capability
  re-check) is the mechanism that makes this page's Claim 5 gap dangerous:
  fallbacks move requests across models while the prefill flag rides along
  unchecked. Its gate claims (1, 3, 8) are **not** re-derived here.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: native Bedrock
  Invoke passthrough route; no overlap with the message-level `prefix` flag.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  audio-transcription endpoint registration and mock-fallback testing; no
  prefill or capability-probe overlap.
- `source-notes/docs-litellm-mock-requests.md` — **Cited (Extends, one narrow
  pattern)**: its **Claim 4** finds the sibling mock page's sample `created`
  epoch stale by ~3 years with no stated liveness field; this note's Claim 6
  records the same documentation-staleness pattern here (~2 years). Cited as
  a recurring corpus pattern about vendor sample payloads, not as agreement
  about any prefill claim — that note's `mock_response` surface is otherwise
  unrelated.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**: A2A
  per-session iteration/budget caps; unrelated surface.
- `source-notes/docs-litellm-bedrock-converse.md` — **Dismissed**: Bedrock
  Converse passthrough route; no overlap.
- `source-notes/docs-litellm-helicone-integration.md` — **Dismissed**:
  Helicone telemetry integration paths; unrelated.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Dismissed**:
  agent capability spectrum and write-guardrail defaults; no claim overlap
  with a message-shape feature page.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Dismissed**:
  within-request advisor sub-inference and its `usage.iterations[]`
  accounting; a different request-shape extension with no shared claim.

**Additional cross-references found by searching `source-notes/` and `guide/`**
(the candidates file was not exhaustive):

- **Corroborates**:
  - `source-notes/docs-litellm-completion-predict-outputs.md` **Claim 11** —
    that note independently read this page and corroborates Claims 2-4: the
    three-name provider list quoted verbatim there ("Supported by:" /
    "Deepseek" / "Mistral" / "Anthropic"), the probe pair
    (`get_model_info(...)["supports_assistant_prefill"]`, `/v1/model/info`),
    and the finding that the two sibling mechanisms' provider sets are
    **disjoint** (`prefix` = Deepseek/Mistral/Anthropic, `prediction` =
    OpenAI) with "no deployment on which both work, and no page says so."
    This note supplies the dedicated extraction that note explicitly deferred
    ("the prefill page is **not** covered by this note … its own issue is
    filed separately"). Its finding that the prefill page is the sibling that
    *ships a probe* is corroborated here (Claims 3-4); no conflict.
  - `source-notes/blog-litellm-claude-fable-5-day-0.md` **Claim 4** — "Fable 5
    decides how deeply to think on its own. You steer it per request with
    reasoning_effort or output_config.effort; fixed thinking budgets,
    temperature, top_p, and assistant message prefill are not supported by
    the model." Read against this page's "Supported by: … Anthropic" (Claim
    2), the pair is a **conditioning variable, not a contradiction**: the
    provider list is coarse, the model constraint is fine-grained, and both
    are vendor statements that can hold simultaneously. No contradiction
    issue filed (MINER §4a when-NOT-to-file); recorded here because the
    pairing is exactly why the probe (Claims 3-4) must be run per model.
- **Contradicts**: **None filed.** Checked before deciding: no open
  `contradiction`-labeled issue and no `C-NNN` entry in `CONTRADICTIONS.md`
  covers prefill, `prefix`, or `supports_assistant_prefill`; the Fable 5
  pairing above is the only candidate and fails the §4a test (different
  granularity / conditioning variable, not opposing claims). The source
  also does not disagree with itself — it makes one set of statements and
  omits the rest (Claim 5 is an absence, not a conflict).
- **Extends**:
  - `source-notes/docs-litellm-completion-function-call.md` **Claims 1-3** —
    the corpus's dissection of the `get_model_info` / `supports_*` lookup
    family: independent keys on one model record (Claim 1), fail-closed
    declared-capability semantics where "an unknown model, a missing key, or
    *any* exception all resolve to `False`" (Claim 2), and the matrix being
    "a field in a **remote JSON artifact served from `main`**" (Claim 3).
    This page adds a *new key* on that same record
    (`supports_assistant_prefill`) without restating any of those semantics —
    so those claims qualify how this page's probe should be read (Claim 3's
    assessment), while this note adds the flag-name mismatch and the
    bracket-index failure shape that note does not cover.
  - `source-notes/docs-litellm-drop-params.md` **Claim 2** — the params
    support matrix "is keyed on provider *and* model (not provider)" and
    provider capability tables are the wrong audit instrument. This page is
    the same lesson reaching a *second* surface: a three-name provider list
    (Claim 2) plus an executable per-model probe (Claims 3-4) for a flag
    that lives in the message body rather than the param namespace. That
    note's introspection call answers "which params?"; this page's answers
    "which capability?" — complementary probes, same rule: never audit from
    the provider name.
  - `source-notes/docs-litellm-completion-message-trimming.md` — its
    **Extraction Notes → "Pages deliberately not mined"** bullet recorded this
    page as unmapped ("`/docs/completion/prefix` was read in full during
    navigation and does document a `prefix: true` assistant-prefill flag
    (Deepseek, Mistral, Anthropic); noted here only so the next Miner knows
    it is unmapped"). This note closes that recorded gap; no claims from that
    note are re-derived.
  - `source-notes/docs-litellm-anthropic-unified.md` **Claim 1** —
    `/v1/messages` is "a unified Anthropic-messages-format endpoint across
    all LiteLLM-supported providers". Adjacent open question (recorded, not
    resolved): Anthropic-wire requests arriving on that route may carry
    native prefill semantics, yet the route fans out to non-Anthropic
    providers where this page's list does not promise support — whether the
    `/v1/messages` translation preserves, validates, or drops a prefill turn
    is documented on neither page.
  - `guide/05-llm-ops-reliability.md` ~L327-330 — the chapter's "Parameter
    migration hazards" section currently mentions assistant prefill **only
    as unsupported** on Fable 5. This page is the positive counterpart (the
    feature exists; here is its shape, its provider list, and its probe) —
    see Guide Impact.
- **Novel**: First dedicated corpus coverage of the assistant-prefill
  surface: the message-level `prefix: true` wire shape (Claim 1); the
  check-name/send-name split (`supports_assistant_prefill` vs `prefix`,
  Claim 3); the documented three-name provider list and its missing
  model-level granularity, with the Fable 5 counterexample pairing
  (Claim 2); the `GET /v1/model/info` pre-flight route as a *second*
  introspection surface distinct from the params gate (Claim 4); and the
  documented-behavior gap for mismatched routing/fallback (Claim 5) — none of
  which appears in `source-notes/` or `guide/` (re-verified this session:
  `supports_assistant_prefill` had zero corpus hits outside the
  contrast-evidence quotes in the predicted-outputs note).
- **Explicitly not conflated** (per the Prospector's warning): prompt caching
  (`source-notes/docs-litellm-completion-prompt-caching.md`,
  `source-notes/failure-litellm-bedrock-invoke-prompt-cache.md`, the
  `docs-litellm-caching-*` notes) is token-prefix reuse driven by
  `cache_control` markers and per-model minimums — a different mechanism from
  assistant prefill, which is a *generation-continuation* trick driven by an
  in-message boolean. The shared word "prefix" is the only thing they share;
  no caching note is cited as corroboration for any claim here.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Parameter migration hazards"
  (guide/05-llm-ops-reliability.md ~L327-341)**: The section currently cites
  assistant prefill only in the *negative* — Fable 5 does not support it
  [source: blog-litellm-claude-fable-5-day-0, Claim 4]. Add the positive
  counterpart and the audit rule this source provides: LiteLLM documents
  assistant prefill as `"prefix": true` on the final assistant message, lists
  Deepseek / Mistral / Anthropic as supporters [Claim 1, Claim 2] [settled],
  and exposes a per-model capability probe — `get_model_info(model=...)["supports_assistant_prefill"]`
  in-process and `GET /v1/model/info` over the proxy [Claims 3-4] [settled].
  The rule the chapter gains: **audit prefill-bearing traffic with the
  capability flag per model, never with the provider list** — the list's
  "Anthropic" entry coexists with Fable 5's documented lack of support, so a
  provider-name check admits requests a specific model will reject
  [Claim 2 + blog-litellm-claude-fable-5-day-0 Claim 4] [conditioning
  variable, not a contradiction]. Also record the flag-name footgun: the wire
  key (`prefix`) and the check key (`supports_assistant_prefill`) differ, so
  config greps and alert rules must know both [Claim 3].
- **Chapter 05, silent-fallback / attribution rules (~L973-985)**: Add a
  pre-flight coverage rule: because SDK `fallbacks` attempt each entry in
  order with no documented capability re-check
  [docs-litellm-completion-input-params, Claim 13] and this page documents
  **no** behavior for a prefill request reaching a non-supporting model —
  no error, no strip, no signal [Claim 5] [settled-as-documented-absence] —
  the capability probe must be evaluated against every fallback target, not
  just the primary model, before prefill traffic is enabled. The mismatch
  outcome stays recorded as an open vendor-documentation gap; the guide must
  not state an outcome the source does not document.
- **Chapter 03 (Runbooks and agents), marginal**: agent prompt templates that
  rely on prefill for continuation-style output should assert
  `supports_assistant_prefill` at config time (the Claim 3 probe pattern) and
  expect continuation output with leading whitespace in responses
  [Claim 6] [settled for the documented sample] — an eval harness comparing
  prefill and non-prefill responses sees different output classes.

## Extraction Notes

- Source read in full via direct HTTP fetch of the rendered Docusaurus page
  (raw HTML → article extraction). The markdown render collapses code-block
  line structure, so all six code blocks were re-extracted from the raw HTML
  with `<br>` tokens restored as newlines — the artifacts in Concrete
  Artifacts are character-for-character, including the published trailing
  comma in the response JSON and the trailing backslash in the `/model/info`
  curl. No paywall, no auth, no truncation; page verified HTTP 200 at
  `source_url`.
- **No sub-pages followed** (MINER §1 allows up to 5): every outbound link on
  the page is either site navigation or a nav sibling already mined as its
  own note (`message_trimming` #1510, `predict_outputs` #1541, plus
  `prompt_caching` #1556, `function_call` #1481, `model_alias`,
  `mock_requests`, `drop_params` #1480, `input` #1495). Following them would
  duplicate existing notes; the two whose claims genuinely qualify this one
  (predicted-outputs, function-call) are cited as cross-references instead.
- **Quote fidelity**: every `Quote` field was located on the fetched page and
  copied character-for-character. Code-line quotes (`"prefix": true # 👈 KEY
  CHANGE`, the curl line, the response `content` value) are verbatim
  fragments of the page's own fenced blocks; prose quotes are contiguous
  single sentences (the "Supported by:" quote concatenates the heading and
  its three adjacent list items, exactly as the sibling
  `docs-litellm-completion-predict-outputs.md` Claim 11 quotes them — each
  fragment independently verified against this fetch). No splicing across
  non-adjacent sentences. Interpreted consequences live in `Our assessment`.
- **Claim 5 is a verified absence**, scoped to this page's section inventory
  (reproduced in Concrete Artifacts), not a claim about gateway runtime —
  consistent with how `docs-litellm-drop-params.md` Claim 9 grades its own
  absent-signal finding. Claim 7's proxy-response attribution is graded
  `emerging` for the same honesty reason: the layout implies it, the page
  does not label it.
- **Cross-reference verification (MINER §4b)**: re-read each cited note and
  confirmed the numbered claims match the cited content —
  `docs-litellm-completion-predict-outputs.md` Claim 11 (prefill provider
  list + probe, quoted from this page, with the "filed separately" note);
  `blog-litellm-claude-fable-5-day-0.md` Claim 4 (Fable 5 prefill
  unsupported); `docs-litellm-drop-params.md` Claim 2 (provider+model
  keying); `docs-litellm-completion-input-params.md` Claim 13 (fallback
  attempt-list semantics); `docs-litellm-completion-function-call.md`
  Claims 1-3 (capability-predicate record lookups, fail-closed semantics,
  cost-map data source); `docs-litellm-anthropic-unified.md` Claim 1
  (`/v1/messages` fan-out). The `message-trimming` citation is by section
  name ("Extraction Notes → Pages deliberately not mined"), not by claim
  number, per §4b.
- **Contradiction check performed** (§4a): the only opposition surfaced —
  "Anthropic supports prefill" vs Fable 5's documented lack of it — is a
  conditioning-variable pair at different granularity, so no contradiction
  issue was filed; no existing contradiction issue or `C-NNN` entry covers
  this surface. Confidence held at `emerging` per the Prospector's explicit
  instruction: thin page, documented surface only, no independent validation,
  no error-behavior documentation.
