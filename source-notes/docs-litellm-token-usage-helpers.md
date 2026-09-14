---
source_url: https://docs.litellm.ai/token_usage
source_type: docs
title: "Token Usage helpers (token_counter / cost_per_token / completion_cost) — liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-09-14)
date_extracted: 2026-09-14
last_checked: 2026-09-14
status: current
confidence_overall: emerging
issue: "#1300"
---

# Token Usage helpers (liteLLM Docs)

> LiteLLM's `token_usage` docs page documents three public client-side helper
> functions — `token_counter`, `cost_per_token`, `completion_cost` — that
> compute token counts and USD spend **entirely locally**: a tokenizer (with
> tiktoken as the fallback) plus the bundled `model_cost` map, with no
> provider-side reconciliation. The ops-relevant consequence: any spend figure
> an operator logs through these helpers is only as trustworthy as the installed
> package's `model_cost` map — the same map whose staleness caused the silent
> `cost=0` fallback in the 2026-02-10 model-cost-map incident.

## Source Context

- **Type**: docs (single-page LiteLLM SDK helper-function reference, part of the
  `litellm-docs` site-crawl scope via spend/accounting)
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  The description of what these three functions do is authoritative for the
  LiteLLM SDK surface, but is vendor documentation of a library behavior — not
  independently exercised here against any provider.
- **Scope**: Three helper definitions plus three `gpt-3.5-turbo` hello-world
  snippets (Example Usage). The page contains nothing on routing, rate limits,
  fallbacks, deployment, or proxy-side spend tracking. Low-substance page.
- **Extraction note**: Per the Prospector's scoped key question (#1300), this
  note extracts only the client-side cost/usage helper contract and its
  dependency on the bundled `model_cost` map. The hello-world snippets carry no
  ops content and were deliberately skipped; the `model_cost` map staleness
  incident itself was **not** re-extracted (covered by
  `failure-litellm-model-cost-map-silent-fallback.md`).

## Extracted Claims

### Claim 1: LiteLLM exposes three public client-side helpers (`token_counter`, `cost_per_token`, `completion_cost`) that compute token counts and USD cost from local inputs only — a tokenizer and the bundled `model_cost` map — with no provider-side reconciliation
- **Evidence**: The page's intro sentence enumerates the three functions; each
  bullet describes a purely local computation (tokenizer count, map lookup for
  USD, composition of the two). Nothing on the page references provider-reported
  billing, provider API responses, or wire usage data.
- **Confidence**: settled (documented first-party API contract, deterministic
  library behavior)
- **Quote**: "However, we also expose 3 public helper functions to calculate token usage across providers:"
- **Our assessment**: This is the page's one structural fact worth keeping for
  the guide: LiteLLM's documented cost/usage *estimation* surface is a local
  computation, not a claim about what a provider bills. Operators who log
  `completion_cost` output are logging an estimate whose inputs are a tokenizer
  and a bundled price table.

### Claim 2: `token_counter` counts tokens locally using the model's tokenizer, falling back to tiktoken when no model-specific tokenizer is available — so locally computed counts can diverge from provider-reported `usage`
- **Evidence**: The `token_counter` bullet states the model-specific-tokenizer-
  first behavior and names tiktoken as the default fallback.
- **Confidence**: settled (documented API contract; deterministic function
  behavior)
- **Quote**: "This returns the number of tokens for a given input - it uses the tokenizer based on the model, and defaults to tiktoken if no model-specific tokenizer is available."
- **Our assessment**: The fallback detail is the extractable nuance. Once a
  model has no dedicated tokenizer, `token_counter` is a tiktoken-based
  estimate; providers commonly count tokens with their own tokenization, so the
  estimate can diverge from provider-reported totals. Any quota, rate-limit, or
  cost math derived from locally counted tokens inherits that divergence — worth
  stating as a caveat wherever the guide recommends estimating usage locally.

### Claim 3: `cost_per_token` computes USD for prompt (input) and completion (output) tokens entirely from LiteLLM's bundled `model_cost` map — living in `__init__.py` and mirrored as the `model_prices_and_context_window.json` community resource — with no provider-side billing input
- **Evidence**: The `cost_per_token` bullet names the `model_cost` map and its
  two locations (in-package `__init__.py` and the GitHub-hosted
  `model_prices_and_context_window.json`).
- **Confidence**: settled (documented API contract)
- **Quote**: "This returns the cost (in USD) for prompt (input) and completion (output) tokens. It utilizes our model_cost map which can be found in __init__.py and also as a community resource."
- **Our assessment**: This is the claim the triage asked the Miner to confirm:
  the USD output of `cost_per_token` is derived **entirely** from the bundled
  `model_cost` map (the page's "community resource" is a link to
  `model_prices_and_context_window.json` on the LiteLLM repo). There is no
  provider-billing reconciliation. The accuracy of the returned figure is a
  function of the installed package's map version — which is precisely the map
  whose staleness produced silent `cost=0` in the model-cost-map incident.

### Claim 4: `completion_cost` returns the overall per-call USD figure by composing `token_counter` and `cost_per_token` — meaning it re-tokenizes the prompt and completion locally and prices them from the map, rather than reading provider-reported usage
- **Evidence**: The `completion_cost` bullet explicitly states the composition.
- **Confidence**: settled (documented API contract)
- **Quote**: "This returns the overall cost (in USD) for a given LLM API Call. It combines token_counter and cost_per_token to return the cost for that query (counting both cost of input and output)."
- **Our assessment**: The composition is the mechanism that ties the previous
  two claims together into a single number. Because it re-uses `token_counter`,
  a stale/absent map entry does not cause an error — it silently yields a zero
  or wrong USD figure. The page's own `completion_cost` example is also
  malformed: it ends `completion_cost(model="gpt-3.5-turbo", prompt=prompt,
  completion=completion))` with a stray closing paren.

### Claim 5: The page's default claim — "By default LiteLLM returns token usage in all completion requests" — is about what the *response payload* carries; the companion streaming page makes usage in streamed responses an opt-in (`stream_options={"include_usage": True}`)
- **Evidence**: This page's opening sentence states the default; the LiteLLM
  `/stream` page ("Streaming Token Usage" section) documents that a streaming
  completion reports usage only when `stream_options={"include_usage": True}` is
  set.
- **Confidence**: emerging (the default statement is verbatim on this page and
  the opt-in requirement is verbatim on the streaming page; the reconciliation —
  "the payload default holds for non-streamed traffic" — is the Miner's
  synthesis)
- **Quote**: "By default LiteLLM returns token usage in all completion requests"
- **Our assessment**: Read precisely, the default sentence is about the `usage`
  field on the response, so it governs any component that meters spend **from
  response payloads** — a logger or callback reading `response.usage`, a
  proxy-side spend tracker. For streamed traffic that path needs
  `stream_options={"include_usage": True}`; without it there is no usage field
  to read. It is *not* a statement about the local helpers, whose inputs are
  text and token counts (Claims 2-4), not the wire `usage` field.
  **On the triage key question — is local computation a substitute for
  `stream_options={"include_usage": True}`, or only an SDK convenience? — this
  page is silent.** A string search for `stream` over the fetched page returns
  zero hits: the page never mentions streaming, `stream_options`, or
  `include_usage`, so it neither claims nor denies substitution. What the note
  can support is the distinction, not the substitution: the payload-metering
  path and the local-estimator path are independent. Our inference (from the
  documented signatures, *not* a source claim) is that the helpers can price a
  streamed call from text the caller accumulates out of SSE deltas, because
  `completion_cost` takes `prompt`/`completion` strings and `token_counter`
  takes `messages` — so `include_usage` is a precondition for reading usage off
  a streamed *response*, not for pricing locally. Do not carry that inference
  into the guide as if LiteLLM asserted it. This is a conditioning variable
  (streaming vs. non-streaming; payload-reader vs. local estimator), not a
  material contradiction, so per MINER.md §4a no contradiction issue was filed;
  the streaming note's Claim 1 covers the wire side.

## Concrete Artifacts

The page contains no configuration, metrics, failure detail, or procedures —
only the three helper definitions (extracted as Claims 1-4) and three
`gpt-3.5-turbo` hello-world snippets. Per the triage bounding (#1300), the
snippets carry no ops content and were **not** extracted. The one observable
artifact worth recording is that the page's `completion_cost` example is
malformed, ending `completion_cost(model="gpt-3.5-turbo", prompt=prompt, completion=completion))` with a stray closing paren.

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every path
listed in the candidates file is addressed):

- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Dismissed**:
  agent capability spectrum, write-permission guardrails, pre-on-caller
  pattern; no token/usage/cost-accounting content.
- `source-notes/blog-litellm-auto-router-v2.md` — **Dismissed**: router/scoring
  collapse and debuggability rationale; no cost-helper or usage-accounting
  content.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **Dismissed** (and
  checked for redundancy per triage): that note covers proxy-level spend
  *governance* levers (budget windows, budget fallback chains, prompt-cache
  injection, Headroom, MCP tool search, auto routing) that presuppose spend
  accounting but document none of the client-side helpers here (`token_counter`
  / `cost_per_token` / `completion_cost`) and no map dependency. No overlap with
  this page's helper API; no duplication.
- `source-notes/docs-langfuse-mcp-server.md` — **Dismissed**: Langfuse docs MCP
  server topic; unrelated.
- `source-notes/docs-litellm-helicone-integration.md` — **Dismissed**: Helicone
  telemetry *shipping* paths (provider-in-path vs `success_callback` logging);
  no content on the client-side cost-estimation helpers or the `model_cost` map
  dependency that this page documents.
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **Dismissed**:
  pipeline data-freshness/correctness SLOs; unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **Dismissed**: toil
  characterization and reduction measurement; unrelated.
- `source-notes/docs-datadog-llm-observability.md` — **Cited** (Corroborates,
  see below).
- `source-notes/docs-langfuse-security-and-guardrails.md` — **Dismissed**:
  guardrail scanner stacks and latency drivers; no usage/cost-accounting
  content.
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **Dismissed**:
  embedding-based semantic-cache backends; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/docs-datadog-llm-observability.md` **Claim 3** (span/trace
    structure — the `input_tokens`/`output_tokens`-as-metrics detail appears in
    that claim's *Evidence* line, not its title) and **Claim 5** (out-of-the-box
    dashboards monitor cost/latency/usage trends). The Datadog note establishes
    token counts → cost as a first-class observability dimension; this page
    supplies the LiteLLM-side estimator that turns token counts into a USD
    figure on that dashboard. Same token/usage-as-telemetry theme; no conflict.
- **Contradicts**: None. The nearest candidate — this page's "returns token
  usage in all completion requests" default vs. `docs-litellm-streaming-token-usage.md`
  Claim 1's streaming opt-in requirement — is a conditioning variable
  (streaming vs. non-streaming context), not a material contradiction that would
  split guide advice, so per MINER.md §4a no contradiction issue was filed. Both
  sides are LiteLLM's own docs describing different transport contexts.
- **Extends**:
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md` — **primary
    overlap**. That note (Root Cause, Lesson 2) documents the failure mode: a
    stale/absent `model_cost` map entry silently yields `cost=0` / "This model
    isn't mapped yet" with no error, because the map is out of the request path.
    This page adds the read-side public API that failure poisons: `cost_per_token`
    and `completion_cost` (Claims 3-4) consume that same bundled map directly and
    return USD derived entirely from it, so a stale map means these helpers
    silently return zero or wrong USD. Together the two notes bound the chain: the
    incident explains how the map can go stale; this page explains where the
    number an operator logs actually comes from.
  - `source-notes/docs-litellm-streaming-token-usage.md` — that note (Claim 1)
    documents the wire precondition for *streamed* responses
    (`stream_options={"include_usage": True}`); this page covers the client-side
    conversion of token counts into dollars for the non-streaming path (and
    presupposes those counts exist — see Claim 5). Together they bound the
    accounting path: tokens must arrive (streaming note) before they can be
    priced (this page).
- **Novel**: First corpus coverage of the `token_counter` / `cost_per_token` /
  `completion_cost` public helper API (string search for these names returns
  zero hits in `source-notes/` and `guide/`, re-verified this session), and of
  the central fact that LiteLLM's documented cost helpers are **local-computation
  estimators** over the bundled `model_cost` map with no provider-side
  reconciliation — distinct from proxy-side spend tracking and from the
  wire-level usage contract already covered.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — "Model enablement and the cost-map reload
  pattern")**: The guide already documents the remote cost map and the
  `POST /reload/model_cost_map` reload path
  (guide/05-llm-ops-reliability.md, end of the cost-map-reload section). Add the
  read-side contract this page establishes: portable USD spend figures an
  operator logs via `completion_cost`/`cost_per_token` are local estimate outputs
  bounded by the running package's `model_cost` map version, with **no
  provider-side reconciliation** — so on a stale map these helpers silently
  return zero or wrong USD (per
  `failure-litellm-model-cost-map-silent-fallback`). Recommend attributing logged
  spend to "local estimator output (function of bundled pricing map)" and
  reconciling periodically against provider billing, rather than treating
  `completion_cost` output as a billed figure.

- **Chapter 02 (Observability)**: Where token counts → cost appear on dashboards
  (per `docs-datadog-llm-observability`, Claim 3's evidence line and Claim 5),
  keep the two metering paths distinct rather than collapsing them into one
  sentence. (i) **Payload metering** — a logger, callback, or proxy-side spend
  tracker that reads the `usage` field off the response — sees token counts on
  non-streamed calls by default, but on streamed traffic only if the client
  opts in with `stream_options={"include_usage": True}` (per
  `docs-litellm-streaming-token-usage`, Claim 1). (ii) **Local estimation** —
  `token_counter`/`cost_per_token`/`completion_cost` over prompt and completion
  text (Claims 2-4) — is not gated by that flag; it prices from text the caller
  holds and reads the bundled `model_cost` map. Recommend the guide state the
  streaming caveat against path (i) only: "streamed traffic must opt in or there
  is nothing to price" is true of a payload reader and false of the local
  helpers.

## Extraction Notes

- Source read in full via direct HTTP fetch (HTTP 200; the page is ~1.6 KB of
  body text — three helper definitions plus three example snippets). No
  sub-pages followed; the page links only to the readthedocs output page and the
  community `model_prices_and_context_window.json` resource, neither of which
  adds ops content beyond what is quoted here.
- All `Quote` fields are verbatim contiguous fragments from the fetched page
  prose, copied character-for-character from the rendered HTML (re-verified via
  raw HTML fetch this session); no splicing across non-adjacent sentences. Claims
  1-4 quote the page's own bullets; Claim 5 quotes the page's opening sentence.
- Triage key question answered explicitly in Claim 5: whether the page presents
  local computation as a *substitute* for
  `stream_options={"include_usage": True}` or only as an SDK convenience. The
  page is **silent** — a string search for `stream` over the fetched page
  returns zero hits (no mention of streaming, `stream_options`, or
  `include_usage`). The note states the distinction it does support
  (payload-reader vs. local-estimator metering) and labels the substitution
  reading as our inference, explicitly not as a source claim.
- Triage bounding honored (`priority:low`): the `gpt-3.5-turbo` hello-world
  snippets were skipped (no ops content, per triage). The `model_cost` map
  staleness incident was not re-extracted — it is already covered by
  `failure-litellm-model-cost-map-silent-fallback.md`; this page only adds the
  public helper API above it.
- `confidence_overall` set to `emerging`: the helper contracts (Claims 1-4) are
  settled first-party API documentation, but the ops value of this note is the
  analytic link between the helper API and the cost-map failure mode, and the
  cross-page "usage by default" caveat (Claim 5) is a synthesis across two
  vendor pages — none of it independently exercised against a live provider.
- No contradiction issue filed: the one potential tension (default usage-return
  vs. streaming opt-in) resolves as a conditioning variable (transport context)
  per MINER.md §4a; `CONTRADICTIONS.md` has no entries and no open
  `contradiction`-labeled issues to extend.
- String search `token_counter|cost_per_token|completion_cost` returns zero hits
  in `source-notes/` and `guide/` (re-verified this session), confirming the
  triage's duplicate check.
