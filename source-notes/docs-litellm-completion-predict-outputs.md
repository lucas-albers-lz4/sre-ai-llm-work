---
source_url: https://docs.litellm.ai/docs/completion/predict_outputs
source_type: docs
title: "Predicted Outputs | liteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-06)
date_extracted: 2026-10-06
last_checked: 2026-10-06
status: current
confidence_overall: emerging
issue: "#1541"
---

# Predicted Outputs (`prediction=`) — LiteLLM Docs

> The corpus's first record of a **latency lever that can raise cost**: LiteLLM
> documents `prediction={"type": "content", "content": <string>}` as an
> OpenAI-only, `v1.51.4`+ passthrough with a single unquantified performance
> claim ("reduce your latency significantly") and **no observability surface at
> all** — no `usage` field, response field, header, log line or metric, even
> though the upstream API it links to returns exactly the two fields
> (`accepted_prediction_tokens` / `rejected_prediction_tokens`) that prove
> whether the optimization fired and price the tokens it wasted. The same
> upstream page documents a hard mutual-exclusion list (eight request params
> including `max_completion_tokens` and `tools` are unsupported alongside it),
> classifies it as an **inference-speed** optimization rather than a
> token-reduction one, and warns that rejected prediction tokens are still
> billed. The immediately-preceding nav page documents the *other* mechanism for
> the same problem — assistant prefill — on a **disjoint, non-overlapping**
> provider set, with a capability probe and no cross-reference in either
> direction.

## Source Context

- **Type**: docs (single-page LiteLLM SDK/proxy reference at
  `/docs/completion/predict_outputs` — verified HTTP 200 this session, matching
  `source_url`). Site breadcrumb per the page's own nav: "Guides → Prompts &
  Context → Predicted Outputs". Nav siblings: `Pre-fix Assistant Messages`
  (Previous) and `Prompt Compression (compress())` (Next); the wider "Prompts &
  Context" set also holds `Trimming Input Messages` and `Prompt Caching`. The
  page has no publish or update date in its HTML.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation,
  describing a feature it forwards rather than implements. Authoritative for the
  *documented* wire shape and the two hard operating boundaries (provider,
  version). The vendor has **no incentive to document the feature's limits** on
  a page whose purpose is adoption, which is exactly the gap this note records.
- **Scope**: One request parameter, end to end: the property table (description,
  supported providers, upstream link, minimum LiteLLM version), the Python SDK
  sample, and the three-step proxy path (`config.yaml` → `litellm --config` →
  stock `openai` client). Does **NOT** cover: the feature's actual behavior
  contract, its cost accounting, its interaction with any other request
  parameter, its interaction with routing/fallback, or any observability
  surface. The page is genuinely thin — verified by full read: one 4-row property
  table, one prose sentence, one two-tab usage section, and three numbered steps.
- **Upstream material mined in parallel**: because the page's own property table
  carries a single outbound link to
  `https://platform.openai.com/docs/guides/latency-optimization#use-predicted-outputs`
  and delegates the feature's substance to it, that target was read in full
  this session, plus the canonical feature guide it links to
  (`https://developers.openai.com/api/docs/guides/predicted-outputs`). Claims 4,
  5, 6 and 10 are sourced from those **OpenAI** pages and are labeled as such in
  every `Quote` field; they are attributed context, not LiteLLM documentation.
  The gap between what the LiteLLM page carries and what its own outbound link
  carries is itself the finding (Claims 6, 9).
- **Redundancy**: `docs-litellm-drop-params.md` (#1480) and
  `docs-litellm-completion-input-params.md` (#1495) own the parameter-support
  gate and the `completion()` request surface. Per the Prospector's explicit
  instruction ("do not re-derive the feature overview; capture only the param
  shape and the multi-provider behavior question"), those mechanisms are **not**
  re-derived here — this note cites them for the routing answer and adds only
  what is specific to `prediction`.

## Extracted Claims

### Claim 1: The feature is gated on **two independent conditions** — a single supported provider (`openai`) and a single minimum version (`v1.51.4`) — stated as a 4-row property table with no upper bound and no changelog link
- **Evidence**: The page's entire property table, in this order: `Description`,
  `Supported providers` = `openai`, `Link to OpenAI doc on Predicted Outputs`,
  `Supported from LiteLLM Version` = `v1.51.4`. The two gate values are the only
  non-prose cells in the page.
- **Confidence**: settled (explicit vendor statement of both boundaries,
  unqualified)
- **Quote**: "Supported providers" / "openai" / "Supported from LiteLLM Version" / "v1.51.4"
- **Our assessment**: The provider restriction is a **support-boundary fact**, and
  the version floor is a **fleet-compatibility fact** — the corpus had neither
  for this param before. The version floor is the operationally sharper half and
  the page does nothing with it: `v1.51.4` is stated as a bare floor with no
  upper bound, no release-note link, and no "changed since" note, so an operator
  on an older LiteLLM cannot determine from this page whether `prediction` is
  unknown, silently ignored, or an error — and per the gate mechanics in
  `docs-litellm-completion-input-params.md` Claim 3, a parameter LiteLLM does not
  classify as an OpenAI param is *assumed provider-specific and passed into the
  request body as a kwarg*, so on a pre-`v1.51.4` build the most likely outcome
  is neither of those three. The practical rule: pin the gateway version before
  adopting this param, and treat the version floor as a fleet-wide precondition
  rather than a per-deployment one.

### Claim 2: The wire shape is a bare `prediction={"type": "content", "content": <string>}` object on the request body, identical in the LiteLLM SDK sample and in the stock-`openai`-SDK-to-proxy sample — the LiteLLM layer adds no LiteLLM-specific key, envelope, or `extra_body` wrapper
- **Evidence**: Two code samples. The first is LiteLLM-native
  (`litellm.completion(...)`); the second reaches the proxy through an
  **unmodified `openai` client** pointed at `LITELLM_PROXY_BASE`. Both carry the
  identical `prediction={"type": "content", "content": code},` line. The
  `config.yaml` sample in between contains exactly three keys
  (`model_name`, `model`, `api_key`) and no `litellm_params` entry for the
  feature.
- **Confidence**: settled (two complete, runnable samples with no variation
  between them)
- **Quote**: (no prose quote — the claim is about the shape of two code blocks;
  both are reproduced verbatim in Concrete Artifacts)
- **Our assessment**: Two things worth carrying forward. (1) **The proxy
  contract is body-native OpenAI**: a stock OpenAI SDK call reaches the gateway's
  feature with no `extra_body`, no LiteLLM-only key. That is the opposite of the
  escape-hatch pattern the corpus records for params the gateway does *not*
  recognize — compare `docs-litellm-drop-params.md`'s proxy example, where
  force-passing requires `extra_body={"allowed_openai_params": [...]}`. The
  distinction is a reliable tell: **body-native means LiteLLM recognizes the
  param and gates it; `extra_body` means LiteLLM does not and forwards it
  blind.** (2) There is **nothing to configure** — no `litellm_params` key, no
  `model_info` capability flag, no opt-in. Contrast `docs-litellm-a2a-iteration-budgets.md`
  Claim 9 and `docs-litellm-audio-transcription.md` Claim 4, where the feature is
  unreachable until it is registered in `config.yaml`. Predicted outputs is
  entirely request-scoped, which means its blast radius is exactly the set of
  callers that opt in — and, per Claim 7, entirely the set of callers that do
  *not*, with no config to inspect.

### Claim 3: The page's only quantitative performance claim is "you can reduce your latency significantly" — no number, no baseline, no benchmark, no deployment detail — and the OpenAI guide it links to repeats the same unquantified wording
- **Evidence**: One clause inside the single `Description` cell of the property
  table. That sentence is the *entire* performance claim on the page; there is
  no metrics section, no table, no measurement.
- **Confidence**: anecdotal (unsourced vendor assertion — no figure, no
  methodology, no comparison, on either the LiteLLM page or the upstream page it
  points to)
- **Quote**: "Use this when most of the output of the LLM is known ahead of time. For instance, if you are asking the model to rewrite some text or code with only minor changes, you can reduce your latency significantly by using Predicted Outputs, passing in the existing content as your prediction."
- **Our assessment**: We buy the *direction* and do not buy it as evidence for
  any target. This is the same class of assertion the corpus already grades
  `anecdotal` twice — `docs-litellm-completion-input-params.md` Claim 1 on
  provider-uniform streaming usage, and Claim 9 there on the "for every provider"
  clause — so it is consistent with house practice to grade it down rather than
  accept a vendor's adverb. The comparison that makes the gap concrete: the
  OpenAI latency guide this page links to **does** quantify its *other* levers
  ("cutting 50% of your output tokens may cut ~50% of your latency"; "cutting
  50% of your prompt may only result in a 1–5% latency improvement") and pointedly
  does **not** quantify predicted outputs. So the "significantly" is not a
  summary of a withheld number; upstream has no number either. Guide rule that
  follows: **do not cite this page as evidence for a latency target.** If a team
  needs a figure, the figure has to come from their own A/B on their own
  workload, and — per Claim 5 — the accept/reject ratio has to be recorded in
  the same experiment, because a prediction that is mostly rejected buys latency
  the page never promised and cost the upstream page explicitly warns about.

### Claim 4 (upstream, OpenAI docs — not the LiteLLM page): Predicted outputs is classified by its own vendor as an **inference-speed** optimization, not an output-reduction one — it sits under "Process tokens faster", the section that defines its subject as tokens-per-second
- **Evidence**: In the OpenAI latency-optimization guide the LiteLLM page links to,
  the "Process tokens faster" section defines its subject ("**Inference speed**
  is probably the first thing that comes to mind when addressing latency … This
  refers to the actual **rate at which the LLM processes tokens**") and is the
  section that introduces predicted outputs. It appears nowhere in the sibling
  "Generate fewer tokens" section, which is the one that carries the token-cut
  heuristics.
- **Confidence**: settled as a documented **taxonomy placement** (the upstream
  vendor's own framing, read directly from the linked page)
- **Quote** (from `https://platform.openai.com/docs/guides/latency-optimization`): "Inference speed is probably the first thing that comes to mind when addressing latency" / "This refers to the actual **rate at which the LLM processes tokens**, and is often measured in TPM (tokens per minute) or TPS (tokens per second)."
- **Quote** (same page, the section's own first line): "Process tokens faster"
- **Our assessment**: This is the most useful thing the source contributes and it
  is invisible from the LiteLLM page, which presents the feature as a flat
  latency win with no mechanism. The placement carries a hard operational
  consequence: **predicted outputs changes time-per-token, not token count.**
  Therefore (a) a workload model that predicts latency from output tokens — the
  model the corpus's own cost/latency material implies — will show **no** change
  and an operator may conclude the lever did nothing; and (b) since rejected
  prediction tokens are still billed (Claim 5), token count can go **up**. The
  right instrument is time-to-first-token and inter-token latency on a matched
  A/B, not a token-budget projection. Note also that the LiteLLM page's linked
  anchor (`#use-predicted-outputs`) does not resolve to a section of that name
  (Claim 9), so an operator following the vendor's own pointer lands on
  "Process tokens faster" by accident rather than by design — which is the only
  reason this taxonomy placement is discoverable at all.

### Claim 5 (upstream, OpenAI docs — not the LiteLLM page): Predicted outputs can **increase** cost — rejected prediction tokens are billed at completion rates — and the only signal for either the win or the waste is a pair of `usage` sub-detail fields
- **Evidence**: Two worked `usage` objects on the OpenAI feature guide, with
  `"accepted_prediction_tokens": 14, "rejected_prediction_tokens": 2` in the
  first and `"accepted_prediction_tokens": 60, "rejected_prediction_tokens": 0`
  in the second, plus an explicit prose warning immediately after the first
  object. The guide's Limitations section repeats the billing rule and names
  `rejected_prediction_tokens` as the field to read.
- **Confidence**: settled (explicit vendor warning plus two numeric worked
  examples, one of which shows the nonzero-rejection case)
- **Quote** (from `https://developers.openai.com/api/docs/guides/predicted-outputs`): "Note that any rejected tokens are still billed like other completion tokens generated by the API, so Predicted Outputs can introduce higher costs for your requests."
- **Quote** (same page): "When providing a prediction, any tokens provided that are not part of the final completion are still charged at completion token rates. See the [`rejected_prediction_tokens` property of the `usage` object](https://developers.openai.com/api/docs/api-reference/resources/chat#chat/object-usage) to see how many tokens are not used in the final response."
- **Our assessment**: This is the corpus's first **latency-versus-cost tradeoff**
  on a documented request parameter, and it reframes the whole page. The feature
  is not free: the mechanism is "reuse the tokens the caller already predicted",
  and every token the model *declines* to reuse is charged anyway. A request
  whose prediction is stale — the normal case when the caller predicts from a
  pre-edit snapshot and the model legitimately diverges — pays for the
  prediction twice over, once as rejected completion tokens and once as the real
  output. The detection rule is therefore not optional: **`rejected_prediction_tokens`
  is the SLI for this feature**, `accepted_prediction_tokens` the denominator, and
  a deploy without an accept-ratio dashboard has adopted a lever whose two
  failure modes (no latency win, higher bill) are both invisible. It also
  composes with the corpus's existing `usage`-accounting findings in a way worth
  stating once: `docs-litellm-completion-prompt-caching.md` Claim 4 records that
  `prompt_tokens` is *not* net of cache and so over-bills cached traffic at full
  input price — the same class of error, opposite direction, and both are
  "headline token counters do not mean what the arithmetic assumes". And per
  `docs-litellm-completion-output.md` Claim 12, the gateway declares its `usage`
  object provider-invariant on an assertion-only footing, while the fields that
  carry this signal live in `completion_tokens_details`, **one level below the
  four-key contract** that note's Claim 1 says the page documents. Neither of
  those LiteLLM notes mentions `completion_tokens_details` at all.

### Claim 6 (upstream, OpenAI docs — not the LiteLLM page): The parameter is **mutually exclusive with eight other request parameters**, including `max_completion_tokens` and `tools`, which are documented as *not supported at all* in this combination — a constraint the LiteLLM page states nowhere
- **Evidence**: The OpenAI feature guide's "Limitations" section: a model-support
  line, the billing line, and an eight-item list of unsupported API parameters.
  Two items are unconditional ("not supported"): `max_completion_tokens` and
  `logprobs`, plus `tools` ("Function calling is not currently supported");
  three are value-conditional (`n` > 1, `presence_penalty` > 0,
  `frequency_penalty` > 0); two are modality restrictions (`audio`,
  `modalities`).
- **Confidence**: settled (explicit vendor limitation list, unconditional items
  quoted verbatim)
- **Quote** (from `https://developers.openai.com/api/docs/guides/predicted-outputs`): "The following [API parameters](https://developers.openai.com/api/docs/api-reference/resources/chat) are not supported when using Predicted Outputs:" / "`n`: values higher than 1 are not supported" / "`logprobs`: not supported" / "`presence_penalty`: values greater than 0 are not supported" / "`frequency_penalty`: values greater than 0 are not supported" / "`audio`: Predicted Outputs are not compatible with [audio inputs and outputs](https://developers.openai.com/api/docs/guides/audio)" / "`modalities`: Only `text` modalities are supported" / "`max_completion_tokens`: not supported" / "`tools`: Function calling is not currently supported with Predicted Outputs"
- **Our assessment**: This is the highest-value item in the whole extraction for
  Ch05, and it is a **cross-document hazard the gateway's own reference page
  cannot see**. `docs-litellm-completion-input-params.md` lists
  `max_completion_tokens` and `logprobs` / `top_logprobs` as ordinary optional
  fields in its **Concrete Artifacts → `completion()` signature** block (no
  numbered claim in that note covers them), with **no** combination caveats, and
  its **Claim 12** documents `tools[].type: "mcp"` on the same surface — and the
  LiteLLM gateway will accept that combination and forward it. The caller who
  audited their request against LiteLLM's parameter reference has therefore been
  given false clearance. Three
  concrete failure shapes follow, each grounded in a corpus item:
  (a) **`max_completion_tokens` is the corpus's headline output cap.** Many of
  the corpus's own budget mechanisms are expressed in terms of an output-token
  bound, including the A2A per-session spend cap
  (`docs-litellm-a2a-iteration-budgets.md` Claims 1 and 4, where an
  over-budget call reaches the provider before being rejected on the *next*
  call). A caller who pairs this feature with an explicit output cap loses the
  cap's meaning on this path.
  (b) **`logprobs` is the natural confidence signal**, and it is unconditionally
  unsupported here — so a team that adds logprob-based quality scoring to a
  workload cannot adopt the latency lever, and vice versa. The two are mutually
  exclusive choices, not composable options.
  (c) **`tools` exclusion collides with the corpus's agent surfaces.**
  `docs-litellm-completion-input-params.md` Claim 12 records that
  `tools[].type` may be `"mcp"`, so ordinary `/chat/completions` traffic can
  invoke registered MCP servers; `docs-litellm-drop-params.md` Claim 6 documents
  stripping `input_examples` from tool definitions for Claude Code on Bedrock;
  and `docs-google-sre-prodcast-04-09-ai-agents.md` Claim 3 is the corpus's
  canonical guardrail for world-mutating agent actions. **Any tool-using
  workload — the entire class the rest of the corpus is about — cannot use this
  feature at all.** The page's own example is consistent with that (a
  single-turn code rewrite, no tools), which is the only signal on the page that
  a scope limit exists.

### Claim 7: The multi-provider question the page does not answer — whether a `prediction` survives a route to a non-OpenAI deployment — resolves against the gate's *default* polarity, and the other polarity is a fleet-wide silent no-op; `prediction` is inside the gate's namespace, so the input-params page's kwarg fallback does not apply
- **Evidence**: Two documented statements from other LiteLLM reference pages plus
  a source-code spot check on `main` this session. (i) `prediction` is named in
  `OpenAIChatConfig.get_supported_openai_params`'s `base_params` list in
  `litellm/llms/openai/chat/gpt_transformation.py`, and it is an explicit keyword
  parameter (`prediction=None,`) in `get_optional_params(...)` in
  `litellm/utils.py` — i.e. LiteLLM classifies it as a known OpenAI param and
  routes it through the optional-params machinery, not the
  pass-through-as-kwarg fallback. (ii) `docs-litellm-drop-params.md` Claim 1
  documents the resulting polarity for any param in that namespace whose
  provider+model does not list it: raise by default, silent drop under
  `drop_params`. The LiteLLM page itself says only the restriction.
- **Confidence**: emerging (documentation-derived plus a source-code spot check
  on a moving `main`; line numbers are version-sensitive, and the page under
  extraction states nothing about routing behavior)
- **Quote**: "Supported providers" / "openai"
- **Our assessment**: This is the answer to the triage question, and both of its
  poles are bad in different ways. **Default (raise):** a request that carries a
  `prediction` and lands on any non-OpenAI deployment fails at the gateway with
  an `UnsupportedParamsError`-class error rather than degrading — which is
  *better* than silence, but turns a pure latency optimization into a hard
  availability dependency on the routing decision, and interacts badly with
  `fallbacks` / `context_window_fallback_dict`
  (`docs-litellm-completion-input-params.md` Claims 4 and 13): a primary OpenAI
  deployment that falls back to a non-OpenAI one converts a working call into a
  raised error, and the page documents no interaction. **`drop_params` set
  (silent):** the parameter is dropped, the caller gets a **correct answer with
  none of the latency benefit**, and per `docs-litellm-drop-params.md` Claim 9
  the page documents no log line, metric, response field or header for a drop —
  so this is undetectable. That coupling is the finding worth stating: **an
  operator who enables `drop_params` for an unrelated reason has silently
  disabled this latency lever on every non-OpenAI deployment the proxy serves,
  with no config diff to show for it and no signal to detect it.** Two
  honest limits on this claim: the page states none of this, and whether LiteLLM
  instead *forwards* `prediction` to providers whose transformation ignores it
  is **not determined by the documentation** — a single request against a
  non-OpenAI route is the cheap experiment that would settle it, and the
  `x-litellm-response-cost` / `response_ms` surfaces in
  `docs-litellm-completion-output.md` Claims 7 and 12 would give the two
  measurements needed (did it error, and did the latency change).

### Claim 8: The page documents **no observability surface for the feature** — no `usage` field, no response field, no header, no log line, no metric, no troubleshooting section — even though the upstream API returns the two fields that would tell an operator whether the optimization fired
- **Evidence**: Verified by full-page read against the page's complete section
  inventory: one `Description` sentence; one property table (4 rows); one
  "Using Predicted Outputs" heading with two tabs (LiteLLM Python SDK / LiteLLM
  Proxy Server); one intro sentence; three numbered steps. The page contains no
  `usage` example, no response body, no metrics, and no error text. Its two
  concrete artifacts are requests — the samples `print(completion)` and nothing
  else.
- **Confidence**: settled as an **absence claim** (the page is short and fully
  read; the omission is checkable by re-reading it). It is an absence in
  *documentation*, not a claim that LiteLLM emits nothing.
- **Quote**: (no direct quote — the page contains no sentence about logging,
  metrics, response fields, or headers; the section inventory is in Evidence and
  the two code samples are reproduced verbatim in Concrete Artifacts)
- **Our assessment**: This is the corpus's recurring LiteLLM failure shape, and
  the corpus already names it: `docs-litellm-drop-params.md` Claim 9 (no signal
  for a param drop), `docs-litellm-completion-batching.md` Claim 3 (winner-only
  `usage`, the N−1 cancelled calls leave nothing), and
  `docs-litellm-anthropic-advisor-tool.md` Claim 7 (the advisor's contribution is
  not observable by the client on the non-Anthropic path). Predicted outputs is
  the **fourth instance and the most consequential**, because the missing fields
  are not diagnostics — they are *billing* fields. An operator can enable this
  on a fleet, watch cost-per-request rise and TTFT fail to move, and have **no
  documented way to tell "the prediction is being rejected" from "the
  deployment is slow"**. Per `docs-litellm-completion-output.md` Claim 1, the
  gateway's own documented response contract is four top-level keys
  (`choices`, `created`, `model`, `usage`) and does not document
  `completion_tokens_details` where both signal fields live — so even a team
  that reads the upstream docs will not find the fields named anywhere in the
  LiteLLM reference. The guide-shaped rule: **a latency lever is not adoptable
  until the field that proves it fired is on a dashboard**, and for this
  parameter that field has to be hunted out of the upstream API reference
  rather than the gateway's.

### Claim 9: The page's one outbound link — the vendor's own pointer to the authoritative document for the feature's limits — points at a **dead fragment**, so the reader who follows it misses the billing caveat and the entire incompatibility list
- **Evidence**: The `Link to OpenAI doc on Predicted Outputs` row of the property
  table carries anchor text "Predicted Outputs ↗" and href
  `https://platform.openai.com/docs/guides/latency-optimization#use-predicted-outputs`.
  Fetched this session, the target page's headings are "Seven principles",
  "Process tokens faster", "Generate fewer tokens", "Use fewer input tokens",
  "Make fewer requests", "Parallelize", "Make your users wait less", "Don't
  default to an LLM", and "Example" — **no `use-predicted-outputs` anchor
  exists**, and the feature's real limitations live on a *different* page
  (`/docs/guides/predicted-outputs`), which the target page links to only from a
  general "Predicted outputs" hyperlink in its first paragraph.
- **Confidence**: settled (directly re-checkable: the href is in the page's own
  HTML and the fragment is absent from the fetched target)
- **Quote**: "Predicted Outputs ↗"
- **Our assessment**: A stale anchor in the vendor's only hand-off to the
  authoritative source. It matters more than a cosmetic docs bug here because the
  missed content is exactly what the page itself needed to carry (Claims 5, 6):
  a reader who clicks through lands on the section that gives no numbers for
  predicted outputs, with the billing warning and the eight-parameter
  incompatibility list one more hop away on a page the LiteLLM docs never name.
  The page's "Supported from LiteLLM Version `v1.51.4`" framing — the one thing
  that makes a reader believe the page is the complete contract — is reinforced
  by that dead end. Also record the host migration for citation hygiene: the
  href uses the legacy `platform.openai.com` host and `/docs/guides/` path while
  OpenAI's current docs live at `developers.openai.com/api/docs/guides/`; the
  legacy URL still redirects, so the link resolves but the fragment does not.

### Claim 10: Every published example — LiteLLM's two and OpenAI's seven — sends the **same content twice in one request**: once as a user message, once as the prediction — and neither the LiteLLM page nor the upstream guide states how that duplicate is counted
- **Evidence**: LiteLLM's SDK sample and its proxy sample each pass
  `{"role": "user", "content": code}` in `messages` **and**
  `prediction={"type": "content", "content": code}` with the identical `code`
  value. Upstream's guide repeats the pattern in its JavaScript, Python, Go,
  Java, C#, Ruby and `curl` samples. The upstream worked `usage` objects are
  given without any field explaining the prediction's own token cost.
- **Confidence**: settled that the **published pattern duplicates the content**
  (verifiable in every sample, on both pages); **emerging / undetermined** for
  the token-accounting consequence, which neither page states
- **Quote** (from `https://developers.openai.com/api/docs/guides/predicted-outputs`): "In addition to the refactored code, an abridged model response without the `choices` field contains usage data like this:"
- **Our assessment**: A small but genuinely surprising cost-of-entry that no
  prose anywhere flags. The operator reading the LiteLLM page sees a
  `prediction` field added to a request they already send and concludes the
  delta is one extra field; the published shape actually *doubles the payload*
  for the predicted content, and the caller is expected to construct the
  prediction from content they already hold. We deliberately do **not** assert
  the accounting outcome — the two upstream `usage` objects (`prompt_tokens: 59`
  for a ~10-line file, `prompt_tokens: 203` for a ~30-line file) are not
  accompanied by a breakdown, and arithmetic on them would be invention. The
  honest statement is: **the input-side cost of this feature is unstated on both
  pages**, and it belongs in the same measurement plan as the accept-ratio
  dashboard (Claim 5). What *is* settled and worth a guide line: the pattern is
  "put the known output in `messages` for context **and** in `prediction` for
  reuse", which is the mirror image of the `prefix` mechanism in Claim 11 — there
  the known output is the *last* assistant turn, here it is a separate top-level
  object.

### Claim 11: The immediately-preceding nav page documents the *other* mechanism for the same problem — assistant-message prefill — on a **disjoint provider set with zero overlap**, and each page documents a capability probe the other does not have
- **Evidence**: `/docs/completion/prefix` (fetched in full this session) declares
  its own supported-provider list and documents a capability probe. This page
  declares `openai` only and documents no probe. Neither page links to or
  mentions the other; the nav lists them as consecutive siblings under "Prompts &
  Context".
- **Confidence**: settled (both provider lists and the probe are explicit vendor
  statements, read directly from both pages)
- **Quote** (from `https://docs.litellm.ai/docs/completion/prefix`): "Supported by:" / "Deepseek" / "Mistral" / "Anthropic"
- **Quote** (same page): "Call `litellm.get_model_info` to check if a model/provider supports `prefix`." / "Call the `/model/info` endpoint to get a list of models + their supported params."
- **Our assessment**: The corpus's sharpest **conditioning-variable** example in
  this neighborhood, and a textbook illustration of why "which vendors do I run"
  is an SRE question rather than a preference. An operator searching the LiteLLM
  docs for "make generation faster when the output is mostly known" lands on two
  adjacent pages offering two different mechanisms — and the sets **partition**:
  `prefix` covers Deepseek, Mistral and Anthropic; `prediction` covers OpenAI.
  There is no deployment on which both work, and no page says so. Two concrete
  consequences. (1) The **selection is a routing decision, not a config choice**,
  and it must be made per model family, so a mixed-vendor fleet has to decide per
  deployment which mechanism its traffic gets — and the mechanism changes the
  request shape (`"prefix": true` on the final assistant message versus a
  top-level `prediction` object), so it is a client-side change too.
  (2) The two pages are **asymmetric in kind, not just in coverage**: the prefill
  page tells you how to *ask* whether a model supports it
  (`get_model_info(...)["supports_assistant_prefill"]`, `/v1/model/info`), while
  the predicted-outputs page gives you a bare provider name and no probe at all.
  That asymmetry is exactly the difference between a support boundary an operator
  can audit pre-deployment and one they discover in production — and it is the
  same gap as `docs-litellm-drop-params.md` Claim 2's finding that provider
  capability tables are the wrong audit instrument, here with no executable
  alternative offered either. Note for the Smith: the prefill page is **not**
  covered by this note (its own issue is filed separately); it is cited here as
  contrast evidence only, with claims kept to what both pages state directly.

## Concrete Artifacts

All artifacts verbatim from
`https://docs.litellm.ai/docs/completion/predict_outputs` (line structure
preserved from the rendered code blocks; the `config.yaml` sample's trailing
space after `os.environ/OPENAI_API_KEY` is as published). Line breaks inside the
SDK sample are the rendered code block's own.

### Property table (verbatim, all four rows, in published order)

| Property | Details |
| --- | --- |
| Description | Use this when most of the output of the LLM is known ahead of time. For instance, if you are asking the model to rewrite some text or code with only minor changes, you can reduce your latency significantly by using Predicted Outputs, passing in the existing content as your prediction. |
| Supported providers | `openai` |
| Link to OpenAI doc on Predicted Outputs | [Predicted Outputs ↗](https://platform.openai.com/docs/guides/latency-optimization#use-predicted-outputs) |
| Supported from LiteLLM Version | `v1.51.4` |

The href in row three is reproduced from the page's own HTML. It is the dead
fragment documented in Claim 9.

### LiteLLM Python SDK (verbatim)

```python
import litellm
os.environ["OPENAI_API_KEY"] = "your-api-key"
code = """
/// <summary>
/// Represents a user with a first name, last name, and username.
/// </summary>
public class User
{
    /// <summary>
    /// Gets or sets the user's first name.
    /// </summary>
    public string FirstName { get; set; }

    /// <summary>
    /// Gets or sets the user's last name.
    /// </summary>
    public string LastName { get; set; }

    /// <summary>
    /// Gets or sets the user's username.
    /// </summary>
    public string Username { get; set; }
}
"""

completion = litellm.completion(
    model="gpt-5.6-luna",
    messages=[
        {
            "role": "user",
            "content": "Replace the Username property with an Email property. Respond only with code, and with no markdown formatting.",
        },
        {"role": "user", "content": code},
    ],
    prediction={"type": "content", "content": code},
)

print(completion)
```

Introducing sentence, verbatim: "In this example we want to refactor a piece of
C# code, and convert the Username property to Email instead:" — the page's only
prose about the example, and the only indication that this is a
single-turn-rewrite workload with no tools (see Claim 6).

### LiteLLM Proxy Server — step 1, `config.yaml` (verbatim)

```yaml
model_list:
  - model_name: gpt-5.6-luna # OpenAI gpt-5.6-luna
    litellm_params:
      model: openai/gpt-5.6-luna
      api_key: os.environ/OPENAI_API_KEY 
```

Three keys, no feature-specific `litellm_params` entry, no `model_info`
capability flag — the basis for Claim 2's "nothing to configure" and the reason
there is no `config.yaml` state to audit for this feature.

### LiteLLM Proxy Server — step 2, run the proxy (verbatim)

```
litellm --config config.yaml
```

### LiteLLM Proxy Server — step 3, test with the stock OpenAI SDK (verbatim)

```python
from openai import OpenAI

client = OpenAI(
    api_key="LITELLM_PROXY_KEY", # sk-<your-litellm-api-key>
    base_url="LITELLM_PROXY_BASE" # http://0.0.0.0:4000
)

completion = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[
        {
            "role": "user",
            "content": "Replace the Username property with an Email property. Respond only with code, and with no markdown formatting.",
        },
        {"role": "user", "content": code},
    ],
    prediction={"type": "content", "content": code},
)

print(completion)
```

Note that `code` is referenced in this proxy sample without being defined in it —
the sample assumes the variable from the SDK sample above it. Both samples end
at `print(completion)`; the page publishes **no** response body, no `usage`
object, and no latency figure for either (Claim 8).

### Upstream usage objects (verbatim, from
`https://developers.openai.com/api/docs/guides/predicted-outputs`) — the signal
fields the LiteLLM page never mentions

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1786652188,
  "model": "gpt-4.1-2025-04-14",
  "usage": {
    "prompt_tokens": 59,
    "completion_tokens": 24,
    "total_tokens": 83,
    "prompt_tokens_details": { "cached_tokens": 0, "audio_tokens": 0 },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 14,
      "rejected_prediction_tokens": 2
    }
  },
  "system_fingerprint": "fp_6ddb4f7408"
}
```

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1731014771,
  "model": "gpt-4o-2024-08-06",
  "usage": {
    "prompt_tokens": 203,
    "completion_tokens": 159,
    "total_tokens": 362,
    "prompt_tokens_details": { "cached_tokens": 0, "audio_tokens": 0 },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 60,
      "rejected_prediction_tokens": 0
    }
  },
  "system_fingerprint": "fp_9ee9e968ea"
}
```

The first object is the nonzero-rejection case (14 accepted, 2 rejected); the
second is the clean case (60 accepted, 0 rejected) from the page's
"position of predicted text in response" section, where the prediction appears
both before and after newly generated content. Upstream's own captions, verbatim:
"Note both the `accepted_prediction_tokens` and `rejected_prediction_tokens` in
the `usage` object. In this example, 14 tokens from the prediction were used to
speed up the response, while 2 were rejected." and "This time, there were no
rejected prediction tokens, because the entire content of the file we predicted
was used in the final response."

### Upstream incompatibility list (verbatim, from the same OpenAI page's
"Limitations" section)

> The following [API
> parameters](https://developers.openai.com/api/docs/api-reference/resources/chat)
> are not supported when using Predicted Outputs:
>
> - `n`: values higher than 1 are not supported
> - `logprobs`: not supported
> - `presence_penalty`: values greater than 0 are not supported
> - `frequency_penalty`: values greater than 0 are not supported
> - `audio`: Predicted Outputs are not compatible with [audio inputs and
>   outputs](https://developers.openai.com/api/docs/guides/audio)
> - `modalities`: Only `text` modalities are supported
> - `max_completion_tokens`: not supported
> - `tools`: Function calling is not currently supported with Predicted Outputs

### Sibling page `/docs/completion/prefix` — the disjoint provider set and its
capability probe (verbatim)

> Supported by:
>
> - Deepseek
> - Mistral
> - Anthropic

```python
from litellm import get_model_info
params = get_model_info(model="deepseek/deepseek-chat")
assert params["supports_assistant_prefill"] is True
```

Quoted only as contrast evidence for Claim 11. The prefill page is **not** the
subject of this note and is not mined here.

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path is cited or
dismissed below):

- `source-notes/docs-litellm-completion-input-params.md` — **Cited (Extends /
  Contrasts, the load-bearing cross-reference)**: **Claim 3** is the mechanism
  that makes the routing question answerable — a param LiteLLM does not
  recognize is *assumed provider-specific and passed in as a kwarg*, so the
  question of whether `prediction` is gated or forwarded blind reduces to
  whether LiteLLM recognizes it (Claim 7). **Claim 1** supplies the
  gate-exemption boundary that makes "is it in the matrix" an unreliable
  pre-flight test. **Claim 8**'s vendor disclaimer of its own support matrix is
  the general form of the gap this page leaves open (its provider cell is a bare
  `openai` with no probe). That note's **Concrete Artifacts → `completion()`
  signature** block lists `max_completion_tokens` and `logprobs` /
  `top_logprobs` as ordinary optional fields with no combination caveats — the
  direct opposite of Claim 6's incompatibility list, and the reason that
  combination is a live hazard (no numbered claim in that note covers these
  fields; **Claim 12** there is the unrelated `tools[].type: "mcp"` finding,
  cited below for `tools`). **Claim 11** documents
  `input_cost_per_token` / `output_cost_per_token` as caller-supplied per-call
  price overrides, which is the ledger this feature's rejected-token billing
  (Claim 5) would land in.
- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch
  input-file rate limiting, per-record token charging, and
  `batch_enqueued_token_limit`. This page is a single request parameter with no
  batch accounting. Adjacency noted once: both notes are about *where tokens are
  charged*, but on disjoint surfaces (per-file submission vs. per-request
  `usage` sub-details).
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed** as a
  cross-reference, with one adjacency worth recording: its Claim 5 records that
  client auth on that route swaps AWS SigV4 for a bearer token, i.e. a client
  whose SDK contract is fixed to one provider. This page's Claim 6 finding is
  the mirror case from the other direction — a parameter whose *contract* is
  fixed to one provider (OpenAI) even when the SDK is a stock `openai` client.
  Both are "the client's provider assumption is load-bearing"; no claim overlap.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**:
  audio-transcription endpoint config, `mode: audio_transcription` registration,
  and mock-testing fallbacks. One conditional note: its Claim 5 records a
  Guardrails qualification "Applies to output transcribed text", and Claim 6's
  list makes `audio` **incompatible** with this feature — so the audio surface is
  doubly out of scope for predicted outputs. No claim is cited.
- `source-notes/docs-litellm-mock-requests.md` — **Cited (Extends)**: that
  note's **Claim 2** is the corpus's precedent that a documented stub response
  whose token fields are all `null` breaks anything asserting on cost or tokens.
  Claim 8 here is the same hazard in the opposite direction and on the real
  path: the real response *does* carry the two signal fields, but the LiteLLM
  reference that should name them documents a four-key `usage` contract instead
  (`docs-litellm-completion-output.md` Claim 1), so an operator building a test
  double from the LiteLLM docs alone would stub out the only two fields that
  prove the feature fired. **Claim 5** of that note (`stream=True` delivers
  `delta` fragments rather than one shot) is adjacent to the upstream streaming
  note in Claim 4's assessment — the upstream page says latency gains are
  "greater" with streaming, which only compounds a per-chunk attribution
  problem — but the streaming surface is not documented here, so no claim is
  cited from it.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Cited (Extends /
  Contrast)**: that note's **Claim 1** documents the A2A gateway's dollar cap
  (`max_budget_per_session`) and its **Claim 4** the asymmetric timing — an
  over-budget call reaches the provider and is only rejected on the next call.
  This page's Claim 5 supplies the *other* end of spend control: a request-level
  parameter that can **raise** billed tokens while lowering latency, with no cap
  and no in-band rejection. The two compose into the shape the guide needs: the
  A2A cap is the only documented per-session spend ceiling in the corpus, and
  this feature is a way to spend more inside a single call that the cap cannot
  see. Its **Claim 5** (a cost cap surfaces as HTTP 429 with
  `"type": "budget_exceeded"`) is the contrast case: this feature's cost
  increase surfaces as **nothing at all**.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **Cited
  (Corroborates)**: **Claim 3** — "The default guardrail is to deny agents any
  world-mutating action and require explicit human permission before any
  write". This page's Claim 6 establishes that the feature is **unavailable to
  any tool-using agent workload** (function calling not supported), which is the
  corpus's one documented *mechanical* enforcement of that guardrail's spirit
  rather than a policy statement. Recorded as a constraint the guide can cite,
  not as evidence that the guardrail is satisfied — the two are independent.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Cited (Extends)**:
  that note's **Claim 2** is the corpus's precedent for sub-inference tokens
  living in `usage` *sub-detail* arrays (`usage.iterations[]` with
  `type: "advisor_message"`) rather than the headline counters — the same
  structural fact that makes Claim 5's `completion_tokens_details` fields
  easy to miss. Its **Claim 7** is the closest analogue to Claim 8: on the
  non-Anthropic path the client "receives a clean response with no advisor
  blocks at all, so the advisor's contribution is not observable by the client".
  Read together, the corpus now has two documented features whose entire effect
  is invisible at the request surface, in opposite directions — one consumes
  hidden work, the other should be saving time you cannot confirm it saved. That
  pair is worth a single guide rule rather than two separate anecdotes.
- `source-notes/blog-litellm-auto-router-v2.md` — **Cited (Extends)**:
  **Claim 3** — "predictable beats clever for debuggability", and **Claim 8**'s
  greppable `cause=` decision line per request. This page's Claims 2 and 8 are
  the same philosophy unmet: a request-scoped optimization with no capability
  flag, no config state, and no documented observability field, so "why was this
  request slow / expensive" has no attributable cause in the way that note's
  decision log provides. **Claim 9** of that note records that alias-level
  `litellm_params` (naming `drop_params` as the worked example) used to vanish
  on routed requests — which is the same fleet-wide-config-coupling hazard as
  this note's Claim 7, one layer down.
- `source-notes/docs-litellm-completion-batching.md` — **Cited (Extends /
  Contrast)**: **Claim 2** is the corpus's other latency-only optimization
  ("Use this to reduce latency", won by whoever responds first) and **Claim 3**
  its cost of admission — the N−1 cancelled calls leave no field, header or
  array. Read against Claim 4 here (predicted outputs is an *inference-speed*
  optimization) the corpus now has **two** latency levers with the same blind
  spot in opposite shapes: batching hides the losers of a race, predicted
  outputs hides the rejected tokens of a prediction. **Claim 4** of that note
  ("publishes *no* billing semantics for the cancelled calls") is the direct
  precedent for treating this page's silence on cost as a documentation gap
  rather than a promise of no cost. A third pairing for the Smith: that note's
  **Claim 5** records the hedge set expressed in the `model` *data field*
  rather than as config — the same "the wire is where LiteLLM puts routing
  intent" pattern as this page's body-native `prediction` (Claim 2).

**Additional cross-references found by searching `source-notes/` and `guide/`**
(the candidates file was not exhaustive):

- **Corroborates**:
  - `source-notes/docs-litellm-drop-params.md` **Claim 1** — "By default,
    LiteLLM raises an exception if you send a parameter to a model that doesn't
    support it" / "`drop_params=True` … will drop the unsupported parameter
    instead of raising an exception." This note's Claim 7 inherits this polarity
    for `prediction` and is deliberately graded `emerging` and labeled as
    Miner derivation, not as a statement on the page. **Claim 9** of that note
    (no documented signal for a drop) is the load-bearing half of Claim 8's
    assessment: a `drop_params`-enabled fleet loses this lever silently.
  - `source-notes/docs-litellm-completion-prompt-caching.md` **Claim 4** —
    "`prompt_tokens`: These are all prompt tokens including cache-miss and
    cache-hit input tokens." Same class of accounting hazard as Claim 5, in the
    opposite direction (over-billing vs. under-reporting), and both resolve the
    same way: read the `*_details` sub-objects, never the headline counters.
  - `source-notes/docs-litellm-completion-output.md` **Claim 1** (four-key
    response contract `choices` / `created` / `model` / `usage`, with
    `id`, `object`, `system_fingerprint` and `tool_calls` undocumented) and
    **Claim 12** (the `usage` object declared provider-invariant on an
    assertion-only footing). Both are why `completion_tokens_details` — where
    the accept/reject signal lives — is absent from the gateway's own documented
    contract. Its **Claim 7** (`response.response_ms`, a per-call latency float
    exposed directly on the response object, "documented only by a single
    `print` and its printed value") is the nearest thing the corpus has to an
    instrument for measuring this feature's effect, and it is equally
    undocumented-in-practice.
  - `source-notes/docs-litellm-completion-message-trimming.md` **Claim 11** —
    the corpus's only published benchmark for a prompt-side optimization
    (n=5 on SWE-bench Lite at `trigger=10k`, reporting 77.7% token and 72.0%
    cost reduction alongside a real tool-loop quality tradeoff). It is the
    reference standard for what "adopt an optimization with evidence" looks
    like, and it is the bar this feature's evidence (Claim 3) does not meet.
    Useful for the Smith: the report-shape precedent exists in the corpus.
- **Contradicts**: **None filed, and no self-contradiction in the source.** Two
  candidate conflicts were examined and both fail the MINER §4a bar, for
  different reasons, and both are recorded here so the Assayer does not have to
  re-derive them.
  (a) **`max_completion_tokens`**: `docs-litellm-completion-input-params.md`
  lists it as an ordinary optional field (in its **Concrete Artifacts →
  `completion()` signature** block; no numbered claim covers it, and no caveats)
  while OpenAI's Limitations list says it is "not supported" *when using
  Predicted Outputs*. This is a **conditioning variable, not a conflict** — §4a
  "when NOT to file: Claims differ only in context." Both claims are true; they
  are about a two-parameter combination, and neither source claims the other is
  wrong. The operational hazard is real (a caller audited against LiteLLM's
  reference has false clearance) and is carried by Claim 6 and Guide Impact,
  which is the right instrument for it. Filing a contradiction would assert a
  disagreement that does not exist.
  (b) **latency framing vs. cost**: the LiteLLM page presents the feature purely
  as a latency win while the upstream page it links to warns it "can introduce
  higher costs". The LiteLLM page makes **no cost claim at all**, so there are
  not two opposing claims — there is one claim and one omission. §4a "when NOT
  to file: One side is so weakly supported it doesn't rise to a real claim" does
  not apply (upstream's side is strongly supported); the omission simply is not a
  contradiction, and §4a's own remedy for an omission is to record it in the
  source note, which Claim 5 does. Verified before deciding: all 18 open
  `contradiction`-labeled issues (#1150, #1307, #1322, #1338, #1352, #1408,
  #1461, #1462, #1486, #1514, #1517, #1534, #1548, #1550, #1562, #1565, #1591,
  #1593, #1597 — routing, A2A, `thinking.summary`, advisor tool, promptfoo,
  cost-map provenance, prompt-cache minimums) cover none of this surface, and
  `CONTRADICTIONS.md` has no `C-NNN` entries.
- **Extends**:
  - `source-notes/docs-litellm-drop-params.md` **Claim 9** — that note's
    most consequential claim is an *absence* (no documented signal for a drop),
    and **Claim 2** its finding that the support matrix is keyed on provider
    **and** model with an executable probe as the only reliable audit. This note
    adds the mirror-image absence (Claim 8: no documented signal for the feature
    *firing*) and the mirror-image audit gap (Claim 1: a bare provider name with
    no probe, where the sibling prefill page *does* ship one — Claim 11).
    Together the pair gives the guide a symmetric statement: **LiteLLM's
    documentation is asymmetric in observability — it is better at telling you
    when it refuses to do something than when it quietly did or did not do
    something for you.**
  - `source-notes/docs-litellm-completion-input-params.md` **Claim 12** and
    **Claim 3** — the world-mutating-MCP surface on `/chat/completions` and the
    gate's outer boundary. Claim 6 above makes the first one *unreachable* for
    this feature (`tools` unsupported), which is a constraint rather than an
    extension, but the pair is worth citing together in the guide: the request
    surface that can invoke MCP servers is also the request surface where this
    latency lever is unavailable.
  - `guide/05-llm-ops-reliability.md` **L322-325** (per-backend constraints are
    conditioning variables) and **L327-341** (parameter migration hazards) —
    cited as the target sections in Guide Impact rather than as claims; see
    below.
- **Novel**: First corpus coverage of **predicted outputs / the `prediction=`
  request parameter** — re-verified this session: zero hits for "predicted
  output", `prediction=`, `accepted_prediction_tokens`,
  `rejected_prediction_tokens`, or "reduce your latency" across
  `source-notes/` and `guide/`. Specifically new: the OpenAI-only + `v1.51.4`
  double gate; the body-native wire shape and the "no config state" property;
  the first **latency-versus-cost tradeoff** on a documented request parameter
  (rejected prediction tokens billed as completion tokens); the corpus's first
  **inference-speed vs. token-reduction** distinction for a latency lever; the
  eight-parameter mutual-exclusion list, including that this feature is
  unavailable to every tool-using workload; the `prefix` / `prediction`
  provider-set partition with zero overlap and the probe/no-probe asymmetry
  between those two sibling pages; the duplicated-payload shape of every
  published example; the dead `#use-predicted-outputs` anchor on the page's only
  outbound link; and the fourth instance of the corpus's recurring "LiteLLM
  documents no observable signal" pattern — the first one where the missing
  fields are billing fields.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability), "Per-backend constraints are conditioning
  variables" (~L304-325)**: The chapter's Rule currently uses Anthropic effort
  caps (`max` vs `xhigh`) as its worked example of a backend constraint that
  changes behavior on failover. Add a second worked example that is a pure
  *vendor partition*, not a value translation: LiteLLM documents **two**
  mechanisms for "the output is mostly known" — assistant-message prefill
  (`"prefix": true`, supported by **Deepseek / Mistral / Anthropic**) and
  predicted outputs (`prediction=`, supported by **OpenAI** only) — on adjacent
  nav pages under "Prompts & Context", with **zero provider overlap** and no
  cross-reference in either direction [Claim 11] [settled]. Consequence for the
  section: for this class of optimization the conditioning variable *is* the
  vendor list, so the enablement decision must be made per model family and
  cannot be deferred to a fallback chain. Add the operational asymmetry as the
  section's audit rule: the prefill page documents a capability probe
  (`get_model_info(...)["supports_assistant_prefill"]`, `/v1/model/info`) and the
  predicted-outputs page documents **only a bare provider name**, so on the
  predicted-outputs path there is no pre-deployment check to run
  [Claims 1, 11] [settled].
- **Chapter 05, "Parameter migration hazards" (~L327-341)**: The chapter's Rule
  — "audit existing request parameters against the model's supported set before
  routing production traffic. Parameters valid on earlier models may be silently
  ignored or explicitly rejected" — audits params **individually**. This source
  shows the audit it needs is **combinatorial**: `max_completion_tokens`,
  `logprobs` and `tools` are each documented by the gateway's own parameter
  reference as ordinary optional fields (**Concrete Artifacts → `completion()`
  signature** block of `docs-litellm-completion-input-params.md` for
  `max_completion_tokens` and `logprobs` / `top_logprobs`; that note's
  **Claim 12** for `tools[].type: "mcp"`), and each is *individually* valid, yet
  the upstream feature's Limitations list makes all
  three unavailable **in combination with** `prediction`
  (`tools`: "Function calling is not currently supported"; `max_completion_tokens`:
  "not supported"; `logprobs`: "not supported") [Claim 6] [settled]. Add the
  rule: **an audit that checks params one at a time can pass and still produce an
  unsupported combination** — parameter validity is a property of the *set*, not
  of each member. Three concrete pairings worth naming in the chapter, because
  each collides with material the chapter already carries: (i) `tools` exclusion
  makes this lever unavailable to every tool-using workload, including the
  MCP-capable `/chat/completions` surface from
  `docs-litellm-completion-input-params.md` Claim 12; (ii) `logprobs` exclusion
  collides with confidence-scoring evals; (iii) `max_completion_tokens` exclusion
  collides with output-token-bounded spend caps such as the A2A
  `max_budget_per_session` (`docs-litellm-a2a-iteration-budgets.md` Claims 1, 4).
- **Chapter 05, "Parameter migration hazards" — the config-coupling corollary**:
  add the routing answer the page leaves open, since it is now derivable
  [Claim 7] [emerging]. `prediction` sits inside LiteLLM's recognized-OpenAI-param
  set, so the kwarg pass-through fallback does not apply; a request carrying it
  that lands on a non-OpenAI deployment therefore meets the gate's documented
  default, which is a **raise** — and the fleet-wide `drop_params` switch
  converts that into a **silent no-op** with a correct answer at full latency and
  no documented signal (`docs-litellm-drop-params.md` Claims 1, 9). Rule for the
  chapter: **an operator who enables `drop_params` for an unrelated reason has
  silently disabled this lever on every non-OpenAI deployment the proxy serves,
  with no `config.yaml` diff and no detection field.** Flag the confidence
  honestly in the chapter text — the page states none of this, and the derivation
  combines two other LiteLLM reference pages with a source-code spot check on
  `main`. The cheap experiment that would settle it (one request with a
  `prediction` against a non-OpenAI route) is noted as an open follow-up, not
  as a result.
- **Chapter 05 / new material on latency levers — "adopt a latency lever only
  with the field that proves it fired"**: two rules, both from this source. (1)
  **Latency is not token count for this lever.** OpenAI's own latency guide files
  predicted outputs under inference speed (tokens/second), not under output-token
  reduction [Claim 4] [settled]; a workload model that predicts latency from
  output tokens will show no change, and token count can rise. Measure TTFT and
  inter-token latency on a matched A/B. (2) **The accept/reject ratio is the SLI,
  and it lives in `usage.completion_tokens_details`** as
  `accepted_prediction_tokens` / `rejected_prediction_tokens`
  [Claim 5] [settled]; rejected tokens are billed at completion rates, so this
  is simultaneously the correctness signal and the cost signal. Note for the
  Smith the corpus context: the gateway's own response reference documents a
  **four-key** `usage` contract and never names `completion_tokens_details`
  (`docs-litellm-completion-output.md` Claim 1), so an operator must source this
  field from the upstream API reference, not from LiteLLM's docs. This is the
  fourth instance of the corpus's "no documented observable signal" pattern
  (`docs-litellm-drop-params.md` Claim 9,
  `docs-litellm-completion-batching.md` Claim 3,
  `docs-litellm-anthropic-advisor-tool.md` Claim 7) and the first where the
  missing fields are **billing** fields — worth stating as one rule covering all
  four, with this one as the sharpest instance.
- **Chapter 05, "Cost, capacity, and fallback patterns" (~L970+)**: add the
  inverse of the section's cost-control theme. The section's mechanisms
  (`docs-litellm-a2a-iteration-budgets.md` Claims 1, 4, 5) all *cap* spend and
  signal the cap — 429 with `"type": "budget_exceeded"`. This feature *raises*
  billed tokens on a path with **no cap and no in-band signal**: a stale
  prediction is billed as rejected completion tokens and the caller still gets a
  200 [Claim 5] [settled]. Add it as the counterexample that makes the section's
  implicit premise explicit — **not every cost effect on the request path is a
  budget you can configure.**
- **Chapter 05, latency-SLI material**: if a latency-lever subsection is added
  later, record that **"reduce your latency significantly" is not citable as
  evidence for a target** [Claim 3] [anecdotal]. The source's only performance
  claim is one adverb, and the upstream guide it links to declines to quantify
  predicted outputs while *quantifying its other levers* — so the number is not
  withheld upstream, it does not exist. The corpus's bar for adoptable evidence is
  already set by `docs-litellm-completion-message-trimming.md` Claim 11 (n=5,
  SWE-bench Lite, with the quality tradeoff reported alongside the reduction);
  this feature is nowhere near it, and the correct guide stance is "measure it
  yourself, and record the accept ratio while you do."
- **Chapter 02 (Observability)**: add this source as the worked example for the
  chapter's "if you cannot observe the effect, you have not adopted the change"
  rule [Claims 5, 8] [settled]. The feature is request-scoped with no config
  state (nothing to grep in `config.yaml`), no documented response field, and no
  documented metric — the only two numbers that exist are returned by the
  upstream API and are named by neither the gateway's response reference nor its
  parameter reference. Contrast the sibling prefill page, which at least ships a
  capability probe (Claim 11): the observability bar for "can this model do it"
  is met; the bar for "did it do it" is not.

## Extraction Notes

- Source read in full via WebFetch (markdown) **and** re-fetched with `curl` to
  recover exact code-block line structure, since the markdown pass flattens
  newlines inside fenced blocks. Canonical URL
  `https://docs.litellm.ai/docs/completion/predict_outputs`, HTTP 200, no
  paywall, no auth, no JS-gated content. Complete section inventory, all of it
  extracted: the 4-row property table, the "Using Predicted Outputs" heading with
  its two tabs, the one intro sentence, and the three numbered proxy steps. The
  page has no publish or update date in its HTML (unlike
  `docs-litellm-completion-message-trimming.md`, whose frontmatter carried one).
- **Sub-pages followed: two**, both from the page's own outbound links.
  (1) `https://docs.litellm.ai/docs/completion/prefix` — the Previous nav sibling,
  read in full because it solves the same problem by a different mechanism and
  the provider-set contrast (Claim 11) is the note's most transferable finding.
  It is cited as contrast evidence only; its claims are **not** mined here and it
  has its own issue. (2) The OpenAI latency-optimization guide and the OpenAI
  feature guide the page links to — the page delegates the feature's substance to
  them, and Claims 4, 5, 6 and 10 exist only because they were read. The
  `/docs/completion/prompt_compression` Next sibling was **not** followed
  (already covered by `docs-litellm-completion-message-trimming.md` Claims 6-11,
  which mine `compress()`).
- **Source-code spot check performed and disclosed.** To answer the triage
  question about non-OpenAI routing (Claim 7), two upstream files were fetched
  from `https://raw.githubusercontent.com/BerriAI/litellm/main/` this session:
  `litellm/llms/openai/chat/gpt_transformation.py` (where `"prediction"` appears
  in `OpenAIChatConfig.get_supported_openai_params`'s `base_params` list) and
  `litellm/utils.py` (where `prediction=None,` is a keyword parameter of
  `get_optional_params`). This is a **GitHub source check, not documentation**,
  it is on a moving `main` branch (line numbers are version-sensitive), and it is
  the reason Claim 7 is graded `emerging` and labeled as Miner derivation rather
  than `settled`. **No `Quote` field in this note is taken from either file** —
  every quote is from a fetched documentation page, per MINER §2a. Nothing else in
  this note is asserted from source code.
- **Quote discipline**: every `Quote` is a character-for-character contiguous
  fragment from a fetched page. Where a quote comes from an OpenAI page rather
  than the LiteLLM page, the `Quote**` field opens with
  `(from <url>)` and the attribution is repeated in `Evidence`. No quote splices
  non-adjacent sentences; the multi-item Limitations list in Claim 6 is a list of
  contiguous list items reproduced one per line, not a merged sentence. Claims 2,
  8 and 9 carry explicit `Quote: (no direct quote …)` markers because their
  evidence is a code-block shape, a documented absence, and an href
  respectively — each of which is reproduced verbatim in Concrete Artifacts
  instead. Interpretation lives in `Our assessment`, per MINER §2a item 4.
- **Tension examined, no contradiction filed** (MINER §4a when-NOT-to-file), in
  two parts, both detailed in Cross-References. (i) The `max_completion_tokens`
  and `logprobs` incompatibility list versus the gateway's own parameter
  reference documenting them as ordinary fields: a **combination** constraint,
  i.e. a conditioning variable, not a disagreement between two claims — both are
  true. (ii) The LiteLLM page's latency-only framing versus upstream's
  "higher costs" warning: the LiteLLM page makes **no cost claim**, so this is
  an omission rather than a conflict, and §4a's remedy for an omission is to
  record it in the source note (Claim 5), which is what this note does. Checked
  all 18 open `contradiction`-labeled issues and `CONTRADICTIONS.md` (no
  `C-NNN` entries) before deciding; none covers predicted outputs, prefill, or
  this parameter surface.
- **Open sub-questions recorded, not resolved** (the page does not answer them,
  and they were deliberately not filled in by inference):
  (1) whether LiteLLM *forwards* `prediction` to providers whose transformation
  ignores it, rather than raising or dropping it per the gate — settled only by
  one live request against a non-OpenAI route; (2) whether the prediction's
  content is counted in `prompt_tokens` (Claim 10 — the two upstream `usage`
  objects carry no breakdown, and arithmetic on them would be invention);
  (3) whether the feature composes with `fallbacks` /
  `context_window_fallback_dict` on a mixed-provider chain
  (`docs-litellm-completion-input-params.md` Claims 4, 13); (4) whether LiteLLM
  surfaces `accepted_prediction_tokens` / `rejected_prediction_tokens` in its
  `usage` object at all, given that neither its response reference nor its
  parameter reference names `completion_tokens_details`.
- **Thinness assessment, honestly stated.** The Prospector predicted this page
  would yield little more than a one-line capability note plus the parity
  question, and warned that padding to reach a claim count would be a failure.
  That judgment was correct about the **LiteLLM page**: it contains one
  parameter, one property table, three request samples, and no response, no
  metrics, and no error text. It was too pessimistic about the **source** as a
  unit, because the page delegates the feature's substance to the OpenAI
  documents it links to, and those carry the cost accounting, the
  incompatibility list, and the inference-speed framing that make the feature
  assessable at all. Claims 4, 5, 6 and 10 are sourced from those upstream pages
  and labeled accordingly; the remaining seven claims are from the LiteLLM page.
  No claim was padded: every one of the eleven rests on a specific artifact, an
  explicit vendor statement, or a verified absence.
- **Cross-reference verification (MINER §4b)**: every `Claim N` cited from another
  source note was re-read and matched against the cited content —
  `docs-litellm-completion-input-params.md` Claims 1, 3, 8, 11, 12;
  `docs-litellm-drop-params.md` Claims 1, 2, 6, 9;
  `docs-litellm-completion-prompt-caching.md` Claim 4;
  `docs-litellm-completion-output.md` Claims 1, 7, 12;
  `docs-litellm-completion-message-trimming.md` Claims 6-11 (scope check) and
  Claim 11 (benchmark comparison); `docs-litellm-completion-batching.md` Claims
  2, 3, 4, 5; `docs-litellm-a2a-iteration-budgets.md` Claims 1, 4, 5;
  `docs-litellm-anthropic-advisor-tool.md` Claims 2, 7;
  `docs-litellm-audio-transcription.md` Claims 4, 5, 6 (scope check);
  `docs-litellm-mock-requests.md` Claims 2, 5; `blog-litellm-auto-router-v2.md`
  Claims 3, 8, 9; `docs-google-sre-prodcast-04-09-ai-agents.md` Claim 3;
  `docs-litellm-bedrock-invoke.md` Claim 5 (adjacency only);
  `docs-litellm-batches-api.md` (dismissed). Two quotations of *other* notes'
  prose appear in this note (`docs-litellm-completion-prompt-caching.md` Claim 4's
  `prompt_tokens` glossary line and `docs-litellm-drop-params.md` Claim 1's
  polarity sentences); both were copied verbatim from those notes, not
  reconstructed. Where material lives in a cited note's Concrete Artifacts rather
  than a numbered claim, it is cited by section topic rather than by claim number.
- `guide/05-llm-ops-reliability.md` was read at ~L304-384 to confirm the section
  headings and line ranges cited in Guide Impact, and its full heading list was
  enumerated to confirm that the chapter has **no** existing latency-lever or
  latency-SLI section — which is why the two new latency rules above are offered
  as new material rather than as edits to an existing subsection.
- `miner-related-notes.md` was read before Cross-References was written; all ten
  listed candidates are cited or dismissed above. **This file was not modified
  and is not part of the commit.**
- `registry/sources.json` and `registry/claims-index.json` were **not** edited —
  both are derived indexes rebuilt post-merge by `scripts/build_registry.py` /
  `scripts/build_claims_index.py`.
