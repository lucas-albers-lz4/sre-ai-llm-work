---
source_url: https://docs.litellm.ai/docs/completion/model_alias
source_type: docs
title: "Model Alias | liteLLM (SDK client-side `litellm.model_alias_map`)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page frontmatter last_updated 2026-10-03)
date_extracted: 2026-10-05
last_checked: 2026-10-05
status: current
confidence_overall: emerging
issue: "#1524"
---

# Model Alias (LiteLLM SDK docs)

> The only LiteLLM "alias" mechanism in this corpus that is neither a proxy
> `config.yaml` route nor a provider capability mapping: a **module-level dict
> on the `litellm` package object** (`litellm.model_alias_map`) that renames
> the `model` argument of the client's own `completion()` call before the
> request is dispatched. Its stated purpose is cosmetic — displaying
> `GPT-5.6` to an end user while calling `gpt-5.6-luna` — and the page's
> principal finding for an SRE is that it is **documented as a pure display
> rename with no stated observability at all**: nothing on the page says which
> name reaches spend records, response metadata, logging, or cache keys, and
> nothing says what happens to an unmapped name. This is the **third**
> substitution authority in `guide/05-llm-ops-reliability.md`'s
> "Silent model fallback breaks attribution" (after provider-side silent
> fallback and the prompt store's `prompt_template_model`) and the **first**
> one that runs *outside* the gateway, where proxy logging cannot see it.

## Source Context

- **Type**: docs (single-page LiteLLM Python SDK reference). Site breadcrumb
  per the page's own JSON-LD: "Guides → Compatibility & Extensibility → Model
  Alias". Nav position in its section: third of five, between `drop_params`
  (Previous) and `/docs/guides/finetuned_models` (Next). Frontmatter
  `last_updated: "2026-10-03"`; frontmatter `related:` lists exactly
  `/docs/completion/drop_params` and `/docs/guides/finetuned_models`.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation —
  the vendor's own account of its own SDK surface. Authoritative for the
  *documented surface* (the attribute name, the dict shape, the two worked
  aliases, the runnable-code defects below). Not authoritative for *behavior*:
  the page carries no stated resolution order, no error mode, no precedence
  rule, no metrics, no test output, no issue links, and no operational
  experience report. It is a 2-sentence, 3-code-block page.
- **Scope — what the page covers**: the `litellm.model_alias_map` attribute, a
  schema line for its expected format, and two usage snippets (a fragment and
  a "Complete Code" block).
- **Scope — what the page does NOT cover** (all verified by full read, see
  Claims 5 and 6): unmapped-name behavior; chaining / precedence inside the
  map; interaction with the proxy's `model_name` alias or `model_list`;
  which SDK entry points honor the map (only `completion()` is ever
  demonstrated); logging, callbacks, spend/cost attribution, `response.model`,
  cache keys, fallbacks, rate limits, retries; thread-safety, per-tenant or
  per-request scoping, and whether mutating the map mid-flight is safe. The
  page contains no gateway, proxy, deployment, or version content of any kind.
- **Provenance**: machine-filed by `scripts/scan-sites.py` from the
  `litellm-docs` site-crawl seed; evaluated by the Prospector as
  `priority:low` / `novelty:low` "thin-source caveat". That grading held up on
  read, and this note is scoped accordingly: it mines the alias surface and the
  *documented gap*, not LiteLLM aliasing in general.

## Extracted Claims

### Claim 1: `litellm.model_alias_map` is a plain dict assigned as an attribute on the `litellm` module object, and the page's "expected format" block is a schema description rather than a runnable or configurable surface
- **Evidence**: The "expected format" section is a single fenced Python block
  whose only content is the assignment plus an inline comment; there is no
  `config.yaml`, no environment variable, and no proxy key anywhere on the page.
- **Confidence**: settled
- **Quote**: "# a dictionary containing a mapping of the alias string to the actual litellm model name string"
- **Our assessment**: We buy this, and the operational consequence is the
  point: the documented configuration unit is **process-global mutable state in
  the client**, not per-deployment config. The schema form (`"model_alias":
  "litellm_model_name"`) is a shape declaration — it is not a value an operator
  would ever paste in, and executing it verbatim would resolve
  `completion(model="model_alias")` to a model literally named
  `litellm_model_name`. Read as "the map is alias→backend-name, one level
  deep"; do not read it as a config sample.

### Claim 2: The rename happens client-side, before dispatch — `completion(model="GPT-5.6", ...)` reaches `gpt-5.6-luna`
- **Evidence**: The "Complete Code" block's inline comment annotating the call
  site.
- **Confidence**: settled
- **Quote**: `# call "gpt-5.6-luna"`
- **Our assessment**: The page asserts the *result* (the alias reaches
  `gpt-5.6-luna`) and not the *ordering* — it never states whether resolution
  precedes or follows provider detection, credential lookup, or
  supported-params gating. One ordering fact is nonetheless forced by the
  page's own second example (Claim 3): a model name carrying a `replicate/`
  provider prefix cannot be routed by any layer that reads the name *before*
  the map is applied. So "resolve, then select provider" is the only reading
  consistent with the documented examples, but it is an inference from the
  examples, not a statement. Recorded as OQ-1 in Extraction Notes rather than
  asserted.

### Claim 3: A single alias map is not provider-scoped — the two documented entries resolve to two different backends in two different providers
- **Evidence**: The "Relevant Code" and "Complete Code" snippets, which map
  `"GPT-5.6"` to an OpenAI-side name and `"llama2"` to a `replicate/…` model in
  the *same* dict, and then call both through the same `completion` symbol.
- **Confidence**: settled
- **Quote**: `response = completion("llama2", messages)`
- **Our assessment**: We buy this and it is the page's most load-bearing
  operational fact: alias resolution is a **cross-provider redirector**, so a
  one-character edit to a map entry can move production traffic between
  vendors with no gateway config change, no redeploy, and (per Claim 6) no
  documented signal. Note also that the alias is passed **positionally** in this
  example (`completion("llama2", messages)`) rather than as `model=`, so the
  page demonstrates the alias in both supported call forms.

### Claim 4: The page's own second alias is an immutable content-hash-pinned model ID, so the vendor's worked example is a version pin rather than a floating tag
- **Evidence**: The 64-hex-character Replicate version digest inside the
  documented alias value, present verbatim in both snippets.
- **Confidence**: emerging
- **Quote**: `"llama2": "replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca12251a30609463dcfd4cd76703f22e96cdf"`
- **Our assessment**: Worth recording as an *observation about the example*,
  not as a claim about LiteLLM behavior: the value is pinned to a content
  digest, so the one non-OpenAI example in the docs is version-exact. The
  ops-relevant consequence is about **repointing**: when an operator later
  edits an alias to a different backend, the page documents no field, header,
  or record that preserves which alias was in force for a historical call, and
  no way to answer "what did `llama2` mean on Tuesday" from the alias alone.
  The vendor documents no deprecation or alias-history surface. Graded
  `emerging` because it is a reading of a sample value, not a stated contract.

### Claim 5: The page never states what happens to a name that is absent from the map, and never states precedence between the map and any other alias layer
- **Evidence**: Full-page read. The page has exactly two prose sentences, three
  headings (`expected format`, `usage` → `Relevant Code` / `Complete Code`), and
  no section on errors, fallbacks, precedence, or configuration scope. There is
  no `try`/`except`, no "if not found", no mention of the proxy's `model_name`
  alias or `model_list`, and no mention of chaining (an alias whose value is
  itself a key in the map).
- **Confidence**: settled (as a statement about the page; it was verified by
  reading the entire page, not inferred)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: We do not buy any inference about behavior — the page is
  silent, and this note deliberately records that as silence rather than as a
  defect. The SRE-relevant consequence is bounded and real: with no documented
  unmapped-name contract, a typo or a map that failed to load (e.g. an
  import-order mistake) degrades to whatever the *underlying* client does with
  an unknown model name, and nothing on this page would tell an operator which
  name that is. This is exactly the "silent rewrite, no telemetry" shape that
  `guide/05` already flags for the other two substitution authorities.

### Claim 6: The page documents no observability whatsoever — nothing about logging, callbacks, spend, response metadata, cache keys, or concurrency, despite its own stated purpose being a name split between display and call
- **Evidence**: Full-page read. The word "log", "callback", "cost", "spend",
  "trace", "cache", "fallback", "rate limit", "retry", "thread", and "tenant"
  do not appear anywhere in the page body; the only environment variables shown
  are two API keys set directly into `os.environ`.
- **Confidence**: settled (as a statement about the page)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the finding that earns the note its place in the
  corpus. The page's own motivating sentence establishes that two names are in
  play for one request — one shown to the end user, one passed to the backend —
  and then documents nothing about which of the two any downstream system sees.
  For an SRE the three questions the triage raised (cost/spend attribution,
  callback and logging payloads, cache keys) all resolve to "unstated", and the
  honest reading is that an operator cannot rely on the alias appearing in any
  of them *or* on it being absent, because the page never says. Paired with
  Claim 1's process-global storage, that yields the caution worth carrying into
  the guide: **an alias layer that exists to make a name prettier is
  undocumented with respect to every place a name is used for money or
  debugging** — and unlike the gateway-side aliases in this corpus, it runs in
  the client process, outside the proxy's logging path entirely.

### Claim 7: The "Complete Code" block is not runnable as written — it assigns `os.environ[...]` while the only two import lines in the block are `import litellm` and `from litellm import completion`
- **Evidence**: The block's full import header is two lines; `os.environ` is
  used four lines later with no `import os` anywhere in the block. Executed
  top-to-bottom, the snippet raises `NameError: name 'os' is not defined` at the
  first environment assignment, i.e. before either `completion()` call.
- **Confidence**: settled
- **Quote**: `os.environ["REPLICATE_API_KEY"] = "cohere key"`
- **Our assessment**: We buy this as a documentation defect, not as a
  behavioral claim — the fix is one import line, and nothing suggests the
  mechanism is broken. It is recorded because a reader who copies this block
  (the only complete example on the page) gets an error before reaching the one
  behavior the page exists to demonstrate, which is a plausible reason readers
  reach for the proxy-side alias config instead.

### Claim 8: The only complete example on the page carries a placeholder value from a different vendor — `"cohere key"` assigned as the Replicate credential
- **Evidence**: The `REPLICATE_API_KEY` assignment in the "Complete Code"
  block, quoted above; the sibling `OPENAI_API_KEY` line is correctly
  `"openai key"`.
- **Confidence**: settled
- **Quote**: `os.environ["OPENAI_API_KEY"] = "openai key"`
- **Our assessment**: A copy-paste residue from a Cohere example. Trivial in
  itself, but it is the same class of artifact defect this corpus already
  records for other LiteLLM pages (`docs-litellm-mock-requests.md` Claim 8,
  `docs-litellm-drop-params.md` Claim 10): the vendor's illustrative code is
  not linted or executed, so "the example looks trustworthy" is a weaker signal
  than it appears. Two independent defects in one 20-line block (Claim 7 and
  this one) is a small but real sample of that.

### Claim 9: The "Relevant Code" snippet is a fragment rather than a runnable module, and it is the block the page presents first
- **Evidence**: The block begins at `model_alias_map = {` with no `import
  litellm` and no enclosing function or module context, and references
  `litellm.model_alias_map` bare.
- **Confidence**: settled
- **Quote**: `litellm.model_alias_map = model_alias_map`
- **Our assessment**: It depends on the "Complete Code" block for its imports
  and its `messages` payload, which is stated nowhere — a reader who copies
  "Relevant Code" first (it appears first in the `usage` section) gets a
  `NameError` on `litellm`. Same category as Claim 7, lower severity. The
  ordering is worth noting for the guide: the page shows the fragment before
  the whole.

### Claim 10: This page is SDK-client-only — the entire documented surface is one module attribute plus `completion()`, with no gateway or proxy content
- **Evidence**: All three code blocks import from `litellm` and call
  `completion()` directly; the breadcrumb places it under "Compatibility &
  Extensibility" in the SDK docs tree (`/docs/completion/*`), not the AI
  Gateway tree (`/docs/proxy/*`); no `model_list`, `config.yaml`, virtual key,
  or `/v1/chat/completions` appears.
- **Confidence**: settled
- **Quote**: "The model name you show an end-user might be different from the one you pass to LiteLLM - e.g. Displaying `GPT-5.6` while calling `gpt-5.6-luna` on the backend."
- **Our assessment**: This is the layer-boundary claim the whole note is built
  on, and it is load-bearing for every cross-reference below: "alias" in
  LiteLLM means at least three different things (this client-side map, the
  proxy's per-deployment `model_name`, and auto-router alias `litellm_params`),
  and nothing on this page may be cited as proxy routing behavior. It is also
  what makes this mechanism operationally distinct rather than a third
  restatement: a map assigned in the client process cannot appear in proxy logs,
  cannot be reloaded by `POST /reload/model_cost_map`, and is not visible to
  gateway-side spend attribution at all.

### Claim 11: The page carries a first-party freshness date that the rendered page hides, and its frontmatter `summary` is a broken interpolation of its own first sentence
- **Evidence**: Frontmatter `last_updated: "2026-10-03"` (not rendered anywhere
  on the page body) and `summary: "…while calling {} on the backend."`, where
  the body's `gpt-5.6-luna` has been replaced by an empty format field; the
  page's `<meta property="og:description">` carries the same `{}` rendering.
- **Confidence**: emerging
- **Quote**: `summary: "The model name you show an end-user might be different from the one you pass to LiteLLM - e.g. Displaying GPT-5.6 while calling {} on the backend."`
- **Our assessment**: Low guide relevance, recorded for provenance rather than
  operations. Two things follow. First, the page is **current** — updated two
  days before extraction — so nothing here can be dismissed as stale docs.
  Second, the docs build string-formats its summary, and the failure mode is
  a token silently replaced by `{}` rather than an error; that is a small,
  concrete instance of the corpus's recurring "a transformation in the path
  quietly changes a name" theme, sourced from the vendor's own publishing
  pipeline rather than from its runtime.

## Concrete Artifacts

Verbatim from the page's raw markdown endpoint
`https://docs.litellm.ai/docs/completion/model_alias.md` (front matter included
in this dump; not shown on the rendered page).

**Front matter (verbatim):**
```yaml
---
title: "Model Alias"
url: "/docs/completion/model_alias"
canonical_url: "https://docs.litellm.ai/docs/completion/model_alias"
type: "docs"
last_updated: "2026-10-03"
summary: "The model name you show an end-user might be different from the one you pass to LiteLLM - e.g. Displaying GPT-5.6 while calling {} on the backend."
related:
  - "/docs/completion/drop_params"
  - "/docs/guides/finetuned_models"
---
```

**"expected format" block (verbatim — a schema shape, not a value to paste):**
```python
litellm.model_alias_map = {
    # a dictionary containing a mapping of the alias string to the actual litellm model name string
    "model_alias": "litellm_model_name"
}
```

**"Relevant Code" block (verbatim — a fragment; `import litellm` is absent and
`messages` is never defined in this block; Claims 9 and 10):**
```python
model_alias_map = {
    "GPT-5.6": "gpt-5.6-luna",
    "llama2": "replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca12251a30609463dcfd4cd76703f22e96cdf"
}

litellm.model_alias_map = model_alias_map
```

**"Complete Code" block (verbatim — raises `NameError: name 'os' is not
defined` at the fourth code line, before either `completion()` call; Claims 7
and 8):**
```python
import litellm 
from litellm import completion 

## set ENV variables
os.environ["OPENAI_API_KEY"] = "openai key"
os.environ["REPLICATE_API_KEY"] = "cohere key"

## set model alias map
model_alias_map = {
    "GPT-5.6": "gpt-5.6-luna",
    "llama2": "replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca12251a30609463dcfd4cd76703f22e96cdf"
}

litellm.model_alias_map = model_alias_map

messages = [{ "content": "Hello, how are you?","role": "user"}]

# call "gpt-5.6-luna"
response = completion(model="GPT-5.6", messages=messages)

# call replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca1...
response = completion("llama2", messages)
```

**Page inventory (complete, for absence verification):** 1 `<h1>`, 2 prose
sentences, 3 headings (`expected format`, `usage`, `Relevant Code`,
`Complete Code`), 3 fenced Python blocks, a `## Related pages` footer listing
`Drop Unsupported Params` and `Calling Finetuned Models`. No tables, no
admonitions, no examples of output or response objects.

## Cross-References

Layer note applied to every entry: this page is the **SDK client-side** alias
map. Every other note below documents a **gateway/proxy** alias or an alias
effect on the gateway path. They are cited for contrast and for shared failure
class, never as corroboration of routing behavior.

- **Corroborates**: none, and that is the finding. No existing source note
  asserts anything about `litellm.model_alias_map` — a `grep` for
  `model_alias_map` and `completion/model_alias` across `source-notes/`
  returns only `docs-litellm-drop-params.md`, which cites the URL as an
  unmined nav sibling in three places (lines 41, 763, and 810). The nearest
  thing to corroboration is shared *shape*, not shared content: this page's
  "a name you display is not the name you call" is the same class of
  mismatch as `docs-litellm-messages-to-responses-mapping.md` **Claim 9**
  (`response.model` falls back to `"unknown-model"` when missing) and
  `docs-litellm-mock-requests.md` **Claim 2** (LiteLLM synthesizes
  `"model": "MockResponse"` and nulls all three `usage` token fields). Both
  confirm that LiteLLM controls what the `model` field contains on at least one
  path, which is why "which name surfaces here?" is a legitimate question to
  ask of this page — and why its silence is the notable part.

- **Contradicts**: no contradiction filed (MINER.md §4a "when NOT to file").
  Four candidates were examined and all four are **layer/scope differences or
  shared failure classes, not opposing claims**:
  - `failure-litellm-bedrock-invoke-prompt-cache.md` **Claim 7** (verified,
    line 179) — alias-based capability detection failing silently because
    "an alias like `bedrock-claude` has no version substring". The triage
    suggested checking this for inconsistency. It is not one: that claim is
    about a **client detecting model capabilities from a name it was given**
    (Claude Code inferring a feature set from a string), whereas this page
    documents LiteLLM rewriting the name *before* the client-provider boundary.
    Both agree that a name can stop carrying version identity; neither asserts
    the other's mechanism. Recorded here because the two claims compose into a
    single hazard the corpus does not yet state: an alias chain
    (`bedrock-claude` → `anthropic.claude-…-v2`) removes the version substring
    at both ends.
  - `blog-litellm-auto-router-v2.md` **Claim 9** (verified, line 74) —
    `litellm_params` on an auto-router alias silently dropped pre-v1.94.x.
    Proxy-side alias; different layer, different failure (dropped params, not
    rewritten name).
  - `docs-litellm-knowledgebase-vector-stores.md` **Claim 5** (verified,
    line 155) — retrieval is "always on for a model", i.e. unconditional for
    every request routed to that **proxy** alias. Cited so the Smith does not
    conflate the two senses of "alias"; it is the strongest existing statement
    in the corpus about an alias carrying behavior, and it is a gateway
    `model_name`.
  - `docs-litellm-bedrock-invoke.md` **Claim 1** and
    `docs-litellm-bedrock-converse.md` **Claim 1** (both verified) — the path
    segment of the passthrough is the `config.yaml` `model_name` alias,
    resolved by the proxy. The clearest available contrast to this page: there,
    the alias is a **route** that the gateway resolves and logs; here it is a
    rename the client performs before the gateway is ever contacted.

- **Extends**:
  - `source-notes/docs-litellm-drop-params.md` — **closes a named deferral,
    without resolving its sub-question.** Its Extraction Notes record this
    page's URL as an unmined nav sibling (lines 41, 763) and defer to "a future
    `/provider_specific_params` / `model_alias` source" (line 810). This note
    is that source, so the URL deferral is now discharged. The recorded open
    sub-question — whether `stop_sequences` / `top_k` on the
    `/v1/messages`→Responses path raise or silently drop, and whether
    `drop_params` changes that — is **not** answered here and stays open: this
    page mentions no parameters and no drop gate, and `/docs/completion/drop_params`
    appears only as a frontmatter `related:` entry and a "Related pages" footer
    link. Per the triage's instruction, no link is forced.
  - `failure-litellm-wildcard-model-access-desync.md` **Lesson 2** (verified)
    — "Prefer passing freshly-fetched data explicitly rather than relying on a
    module-level global as the iteration target", whose fix removed what
    `guide/05` calls the module-global ambiguity in `add_known_models()`. That
    is a **contrast, not corroboration**: LiteLLM hardened one module global
    because a stale reference caused 401s for three hours, and this page
    documents a *second* module global — `litellm.model_alias_map` — as the
    documented, supported way to configure model identity, with no reload path,
    no audit trail, and no per-caller scoping documented. The vendor treats
    module-global model state as a defect class in one place and as a feature
    in another.
  - `docs-litellm-batches-api.md` **Claim 5** (verified) — provider is taken
    "from the configured route, not client-supplied `custom_llm_provider`".
    The one existing corpus statement about *which* string LiteLLM uses to pick
    a provider, and it is deliberately not the client's string. Combined with
    Claim 3 here (an alias whose value carries a `replicate/` prefix), the
    corpus can now say that LiteLLM's provider determination is route- and
    config-driven in at least two places — which sharpens OQ-1 without
    answering it.
  - `docs-litellm-completion-batching.md` **Claim 5** (verified) — SDK-mode
    hedging puts the whole hedge set *inside the `model` data field*, as a
    comma-separated string, "not as a route, alias, or config key". Strong
    support for treating the SDK `model` argument as a **parsed, overloaded
    field** rather than an opaque name; an alias map that rewrites it is
    operating on a field that already carries a second syntax.
  - `docs-litellm-completion-message-trimming.md` **Claim 1** (verified) —
    `trim_messages()` as the corpus's existing example of a client-side,
    in-process, pre-call SDK helper with a one-line documented contract. This
    page is the same deployment shape (in the client process, before the
    gateway) with an even thinner contract, and its documented-gap analysis is
    the methodology precedent for Claims 5 and 6.

- **Novel**: First corpus coverage of `litellm.model_alias_map` — zero prior
  notes mention the attribute, and the page's URL appears in the corpus only as
  an unmined nav sibling in `docs-litellm-drop-params.md`. New to the corpus:
  that LiteLLM ships a **client-process** alias mechanism alongside the
  gateway's `model_name` alias, so "the alias" is a three-way ambiguous term;
  that this one is a **cross-provider redirector** in a single dict (Claim 3);
  the complete list of documented-and-undocumented surface (Claims 5 and 6);
  the artifact defects in all three code blocks (Claims 7, 8, 9); and the
  frontmatter `last_updated` / broken-`{}`-summary observation (Claim 11).

- **`miner-related-notes.md` candidate dispositions** (all ten read and
  resolved per MINER.md §4; none was cited without verification):
  1. `docs-litellm-batches-api.md` — **cited** (Claim 5) under Extends.
  2. `docs-litellm-bedrock-invoke.md` — **cited** (Claim 1) under Contradicts,
     as the proxy-route contrast.
  3. `docs-litellm-completion-input-params.md` — **dismissed**. It is the
     sibling `completion()` reference and documents the supported-params gate;
     this page documents no parameters at all, so it neither corroborates nor
     contradicts. Its own claims add nothing to the alias question.
  4. `docs-litellm-audio-transcription.md` — **dismissed**. Per-endpoint
     `model_info: mode` registration and a feature matrix; no client-side name
     rewriting.
  5. `docs-litellm-anthropic-advisor-tool.md` — **dismissed**. Within-request
     model composition and its `usage` split; the only adjacency is that spend
     is attributed per sub-inference, which is a gateway concern this page does
     not touch.
  6. `blog-litellm-auto-router-v2.md` — **cited** (Claim 9) under Contradicts.
  7. `docs-litellm-mock-requests.md` — **cited** (Claim 2) under Corroborates
     (LiteLLM-authored `model` field content).
  8. `docs-litellm-bedrock-converse.md` — **cited** (Claim 1) alongside
     `docs-litellm-bedrock-invoke.md` Claim 1; same proxy-path-alias pattern,
     cited as the pair that establishes the contrast.
  9. `docs-litellm-completion-batching.md` — **cited** (Claim 5) under
     Extends (overloaded `model` field).
  10. `docs-litellm-completion-message-trimming.md` — **cited** (Claim 1)
      under Extends (client-side helper precedent).

## Guide Impact

Verified before writing: `grep -rn "model_alias_map" guide/` returns **zero**
matches, and `grep -niE "model alias" guide/02-observability.md` returns zero
as well. `guide/05-llm-ops-reliability.md` mentions "model alias" exactly twice
(lines 301 and 319), both inside the model-enablement and per-backend-constraint
sections, and both in the *gateway* sense. `guide/02-observability.md` contains
no occurrence of "model name", "model identity", or `response.model` at all.
So this is net-new chapter material, not a correction.

- **Chapter 05 — extend "Silent model fallback breaks attribution"
  (line 972) with a third substitution authority, and mark the layer.** That
  section currently enumerates two: provider-side silent fallback (Fable 5 →
  Opus 4.8) and the prompt store's `prompt_template_model`, whose rule is
  "surface the `model` field from the response metadata — do not infer it from
  the request". `model_alias_map` belongs in the same list and differs in a way
  the guide should state: it runs **in the client process, before the gateway
  is contacted**, so the response-`model` check that section relies on is
  checking a name the gateway never saw. Claims 1, 3, 6, 10. Concretely: when
  auditing a fleet, ask not only "which model served this request" but "which
  string did the client ask for, and did anything rename it on the way out".
- **Chapter 05 — qualify the "Reload success ≠ model reachability" rule
  (line 300).** The existing rule reads "validate with an end-to-end request
  against the new model alias on each backend". This source adds the caveat that
  the string used for that validation may itself be rewritten client-side by a
  map the operator does not control from the gateway, and that nothing
  documents what an unmapped name does (Claims 5, 6). Suggested wording: an
  end-to-end validation is only meaningful once you know the name you typed is
  the name that was dispatched — with a client-side alias map, that is a second
  check, and it is not in the reload path.
- **Chapter 05 — add a "cross-provider redirector" caution to the cost
  attribution section (line 1028).** One dict edit can move traffic between
  vendors with no config change and no documented signal, and the page's own
  example demonstrates exactly that shape (one alias to an OpenAI-side name,
  one to a `replicate/` model). Claims 3, 4. This is the same class of lever
  the section already flags for the router and the prompt store, with a weaker
  evidence trail.
- **Chapter 05 — add the module-global hazard to the existing
  module-global-ambiguity material (lines 294–298).** The guide already
  records LiteLLM hardening `add_known_models()` to stop depending on a
  module-level reference. `model_alias_map` is a supported module-level global
  for model identity in the same codebase, with no documented reload, audit, or
  per-caller scoping. Claims 1, 6. Framed as a caution, not a defect: the page
  documents no defect.
- **Chapter 02 — nothing recommended.** Triage suggested Ch02 (Observability);
  on verification there is no section here to correct and no new mechanism to
  add. The observability content this source carries is an **absence**
  (Claim 6), which is a caution for Ch05's attribution rules rather than a
  Ch02 pattern — a reader cannot instrument a layer the vendor documents
  nothing about. Recommend Ch02 be left alone.
- **No `guide/` edit is proposed by this note.** Per repo rules this is Smith
  work; the impact above is advisory input only.

## Extraction Notes

- **Source read in full, from the raw markdown endpoint.** The page was read
  three ways: `markdown` and `html` WebFetch renders of
  `https://docs.litellm.ai/docs/completion/model_alias`, then the raw
  `…/model_alias.md` endpoint. The raw endpoint was necessary, not optional:
  the rendered HTML collapses newlines inside fenced blocks, which would have
  made every code-block quote inexact, and the `.md` form is the only place the
  frontmatter (`last_updated`, `summary`, `related:`) is exposed. HTTP 200, no
  paywall, no auth, no interactive elements. Nothing was skipped: the page is
  the four sections inventoried in Concrete Artifacts.
- **No sub-pages followed, deliberately.** The only outbound references are
  `drop_params` (Previous, and mined as `docs-litellm-drop-params.md`, #1480)
  and `/docs/guides/finetuned_models` (Next). Neither can bear on the alias
  questions this page raises — `drop_params` is about parameter validation,
  not naming, and the finetuned-models page was not read. No claim in this note
  is asserted from any page other than `source_url`.
- **Absences were verified, not inferred** (Claims 5, 6). The page is short
  enough that the full inventory fits in four bullets; the absence claims rest
  on that inventory, not on an impression.
- **Thin-source handling.** This is the `priority:low` / "thin-source caveat"
  case the triage named. The response was to mine the surface and the documented
  gap rather than inflate the note: 11 claims, of which 4 are artifact-level
  observations that *are* checkable against the page (Claims 7–9, 11) and 2 are
  verified absences. No padding, no proxy-aliasing re-extraction, and no claim
  about behavior the page does not state.
- **Quote fidelity.** Every `Quote` field is a character-for-character
  contiguous fragment of the raw `.md` body or its frontmatter, or a verbatim
  code-block line. Nothing is spliced across non-adjacent sentences. Claims 5
  and 6 carry `(no direct quote; see paraphrase in Our assessment)` because
  their evidence is an absence. The inner double quotes in
  `# call "gpt-5.6-luna"` are the source's own.
- **Open questions this source cannot answer** (recorded, not guessed, per the
  triage's instruction):
  - **OQ-1** — ordering of alias resolution relative to provider detection,
    credential lookup, and the supported-params gate. The examples force
    "resolve first" (Claim 3) but the page never states it, and this is exactly
    where `docs-litellm-batches-api.md` **Claim 5** shows the corpus that
    LiteLLM elsewhere ignores client-supplied provider strings.
  - **OQ-2** — what happens when `model` is not a key in the map: raise,
    pass-through to the provider, or provider error. Undocumented (Claim 5).
  - **OQ-3** — whether a mapped value that is itself a key in the map resolves
    once or chains. Undocumented.
  - **OQ-4** — precedence between `litellm.model_alias_map` and a proxy
    `model_name` alias when a client sits behind a gateway that also has the
    alias configured. Undocumented, and the most likely real-world
    misconfiguration.
  - **OQ-5** — which name appears in callbacks, logging, spend records,
    `response.model`, and cache keys. Undocumented (Claim 6); answering it
    needs LiteLLM source or a black-box experiment, neither of which is in
    scope for a docs note.
  - **OQ-6** — whether the map is honored by entry points other than
    `completion()` (`embedding()`, `aembedding()`, image, audio, or a
    `Router`/`ProviderManager` path). Only `completion()` is demonstrated.
  - **OQ-7** — whether mutating `model_alias_map` after import is safe under
    concurrency, and whether a multi-tenant service in one process can vary an
    alias per caller. The storage is process-global (Claim 1) and the page is
    silent.
- **Cross-reference verification (MINER.md §4b), including one corrected
  claim number.** Every cited claim was re-read in the cited note and matched
  to its numbered heading: `docs-litellm-messages-to-responses-mapping.md`
  Claim 9, `docs-litellm-mock-requests.md` Claims 2 and 8,
  `blog-litellm-auto-router-v2.md` Claim 9,
  `docs-litellm-knowledgebase-vector-stores.md` Claim 5,
  `docs-litellm-bedrock-invoke.md` Claim 1, `docs-litellm-bedrock-converse.md`
  Claim 1, `docs-litellm-batches-api.md` Claim 5,
  `docs-litellm-completion-batching.md` Claim 5,
  `docs-litellm-completion-message-trimming.md` Claim 1,
  `docs-litellm-drop-params.md` Claim 10. Note that the triage comment pointed
  at `failure-litellm-bedrock-invoke-prompt-cache.md` **claim 6** for the
  alias-capability-gating point; on re-read that is **Claim 7** (Claim 6 is the
  Converse/Invoke system-message contract), so the citation above uses Claim 7
  — re-read, not approximated, per §4b. `docs-litellm-drop-params.md` is cited
  by line number and by section name (Extraction Notes) because the deferral it
  records is not a numbered claim, and
  `failure-litellm-wildcard-model-access-desync.md` by Lesson heading, because
  failure-report notes in this corpus use `Lesson N` rather than `### Claim`
  numbering. `failure-litellm-model-cost-map-silent-fallback.md` was read and
  not cited: its `cost=0`-on-cost-map-miss failure is a gateway cost-map
  lookup, and this page documents nothing about cost, so a link would have been
  thematic rather than evidentiary.
- **`confidence_overall: emerging`.** The documented surface (attribute name,
  dict shape, both worked aliases, the code-block defects) is `settled` at the
  individual-claim level and was verified against the raw source. The note is
  `emerging` overall because: every claim is first-party vendor documentation
  with no independent validation and no operational experience report; the page
  is a living, undated-as-published doc; the two highest-value claims (5 and 6)
  are claims about *missing* documentation, which a second reader can only
  confirm by re-reading the same page; and Claim 4 is a reading of a sample
  value rather than a stated contract. Consistent with how other single-page
  LiteLLM docs notes in this corpus are graded (#1480, #1510).
- `date_published` unknown (living vendor docs; frontmatter `last_updated:
  "2026-10-03"`, i.e. two days before extraction — current past the
  Dec-2025 freshness bar, and the page's own example references
  `gpt-5.6-luna`); `date_extracted` and `last_checked` both 2026-10-05 (UTC).
- Live trial #571 (OpenCode GitHub Action, Zen free chat-completions,
  `opencode/big-pickle`) — production-shaped drain. `miner-related-notes.md`
  was read first and every one of its ten candidates is cited or dismissed above;
  the file was not committed (it is gitignored).
