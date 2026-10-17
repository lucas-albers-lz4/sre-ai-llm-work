---
source_url: https://docs.litellm.ai/docs/contributing/adding_openai_compatible_providers
source_type: docs
title: "Adding OpenAI-Compatible Providers | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-10-17)
date_extracted: 2026-10-17
last_checked: 2026-10-17
status: current
confidence_overall: emerging
issue: "#1639"
---

# Adding OpenAI-Compatible Providers (LiteLLM Docs)

> A JSON entry in `litellm/llms/openai_like/providers.json` registers an OpenAI-compatible backend with the gateway — and the same entry can declare a silent wire-payload rewrite (`param_mappings`), value clamps (`constraints`), an env-var base-URL override (`api_base_env`), and endpoint enablement (`supported_endpoints`), making the registry the deterministic place to look when a vendor's params come back renamed or capped.

## Source Context

- **Type**: docs (LiteLLM vendor documentation, `/docs/contributing/adding_openai_compatible_providers` — the "Add OpenAI-Compatible Provider (JSON)" page under Providers → Add a Provider).
- **Author credibility**: LiteLLM (first-party product docs). Authoritative for the documented config surface; no independent validation, metrics, or failure evidence on the page.
- **Scope**: The declarative provider-registration schema (required/optional fields, worked JSON examples, Responses API opt-in semantics) and the documented boundary where the no-Python path ends (auth flows, complex transforms). Does **not** cover routing policy, rate limits, spend, deployment, or the contributor PR/merge workflow — per Prospector triage, those sections were deliberately not mined.

## Extracted Claims

### Claim 1: An OpenAI-compatible provider can be registered entirely via a single JSON file — `litellm/llms/openai_like/providers.json` — with only `base_url` and `api_key_env` required
- **Evidence**: Quick Start section (three-step procedure) and Required Fields list.
- **Confidence**: settled (explicit vendor statement).
- **Quote**: "For simple OpenAI-compatible providers (like Hyperbolic, Nscale, etc.), you can add support by editing a single JSON file."
- **Our assessment**: This is the mechanism-level answer to "how does a self-hosted vLLM / internal gateway / non-conforming vendor get into LiteLLM's shared OpenAI-like forwarding path in the first place." The failure note `failure-litellm-vllm-embeddings-encoding-format.md` documents what can go wrong *inside* that shared path; this page documents the declared entry point into it. Two fields are enough for a fully-conformant backend; everything else is opt-in divergence handling.

### Claim 2: `param_mappings` declares a silent wire-parameter rename — the worked example maps OpenAI's `max_completion_tokens` to the provider's `max_tokens`
- **Evidence**: "Provider with Parameter Mapping" example (full JSON snippet) and the Optional Fields description.
- **Confidence**: settled (explicit, with worked example).
- **Quote**: "`param_mappings` - Map OpenAI parameter names to provider-specific names"
- **Our assessment**: This is the ops-relevant core of the page (per Prospector triage): a JSON-registered provider's outbound payload can be rewritten *by the gateway itself*, by static declared config — a third source of silent parameter mutation, distinct from provider-SDK default injection and from the model's own supported-param set. An operator who sees `max_tokens` on the wire where the client sent `max_completion_tokens` now has a deterministic place to look. The rename happens without any Python and without any per-call kwarg, so it is invisible in client code.

### Claim 3: `constraints` clamps parameter values to declared min/max bounds — the worked example constrains temperature to 0.0–1.0
- **Evidence**: "Provider with Constraints" example (full JSON snippet) and the Optional Fields description.
- **Confidence**: settled (explicit, with worked example).
- **Quote**: "`constraints` - Parameter value constraints (min/max)"
- **Our assessment**: The second declared-rewrite surface: beyond renaming, the gateway can *clamp* values before forwarding. A client sending `temperature: 1.5` to a backend registered with `temperature_max: 1.0` gets a silently altered request. Combined with Claim 2, the `providers.json` entry is a per-provider request-transformation policy expressed as data — which is exactly the "document per-backend constraints" rule Ch05 already states, now with a named mechanism.

### Claim 4: `api_base_env` names an environment variable that overrides the entry's `base_url` — a built-in per-environment base-URL swap without editing the JSON
- **Evidence**: Optional Fields list (one-line description).
- **Confidence**: settled (explicit).
- **Quote**: "`api_base_env` - Environment variable to override `base_url`"
- **Our assessment**: Small field, real ops surface: the same registry entry can point at different endpoints per environment (staging gateway, per-region internal proxy) purely by setting an env var, and the actual base URL can live in a secret-injection channel rather than in a committed JSON file. This pairs with the existing Ch05 material on per-environment base-URL swapping (`api_base` in `model_list` entries) — this is the registration-side equivalent.

### Claim 5: `base_class` selects the inheritance base — `"openai_gpt"` (documented default) or `"openai_like"`
- **Evidence**: Optional Fields list.
- **Confidence**: settled (explicit, though the page gives no criteria for choosing between the two).
- **Quote**: "`base_class` - Use `\"openai_gpt\"` (default) or `\"openai_like\"`"
- **Our assessment**: The choice is documented as a two-value switch with `openai_gpt` as default, but the page never explains the behavioral difference — an operator hitting an unexpected transformation has no docs-level answer here. We record the field and default only; per Prospector triage, `base_class` inheritance mechanics were out of extraction scope.

### Claim 6: `supported_endpoints` defaults to `[]` when omitted, but chat completions is always enabled for JSON providers regardless; `/v1/responses` requires explicit declaration
- **Evidence**: Responses API Support section, including the opt-in example and the default-semantics sentence.
- **Confidence**: settled (explicit).
- **Quote**: "If `supported_endpoints` is omitted, it defaults to `[]`. Chat completions is always enabled for JSON providers regardless of this field."
- **Our assessment**: The default is misleading on its face — `[]` reads as "no endpoints," but chat completions is unconditionally on. The practical rule: a JSON-registered provider always serves `/v1/chat/completions`; any *other* endpoint (`/v1/responses`) is opt-in only. Operators auditing "which endpoints will this proxy actually serve for this vendor" must apply this two-part rule, not the field's literal default. The page further states the Responses path inherits OpenAI's request/response handling wholesale: "The provider inherits all request/response handling from OpenAI's Responses API, so streaming, tools, and every standard parameter work without extra code."

### Claim 7: The documented boundary of the no-Python path — custom authentication flows (OAuth, JWT) and complex request/response transformations require a Python config class instead
- **Evidence**: "When to Use Python Instead" section (bulleted list of four triggers).
- **Confidence**: settled (explicit list).
- **Quote**: "Use a Python config class if you need:"
- **Our assessment**: The JSON registry covers rename, clamp, base-URL override, and endpoint opt-in — and stops there. Anything involving a non-header auth handshake (OAuth, JWT) or a transform more complex than rename/clamp forces a Python subclass. That boundary is the honest scope statement for the declarative surface: it absorbs *parameter-name and range divergence*, not *protocol divergence*. (Per Prospector triage, the Python escape-hatch file paths and class-inheritance mechanics are contributor-process material and were not extracted.)

## Concrete Artifacts

**Minimal registration (verbatim from source, "Basic Configuration"):**
```json
{
  "your_provider": {
    "base_url": "https://api.yourprovider.com/v1",
    "api_key_env": "YOUR_PROVIDER_API_KEY"
  }
}
```

**Fully-compatible provider (verbatim, "Simple Provider (Fully Compatible)"):**
```json
{
  "hyperbolic": {
    "base_url": "https://api.hyperbolic.xyz/v1",
    "api_key_env": "HYPERBOLIC_API_KEY"
  }
}
```

**Parameter rename (verbatim, "Provider with Parameter Mapping"):**
```json
{
  "publicai": {
    "base_url": "https://api.publicai.co/v1",
    "api_key_env": "PUBLICAI_API_KEY",
    "param_mappings": {
      "max_completion_tokens": "max_tokens"
    }
  }
}
```

**Value constraints (verbatim, "Provider with Constraints"):**
```json
{
  "custom_provider": {
    "base_url": "https://api.custom.com/v1",
    "api_key_env": "CUSTOM_API_KEY",
    "constraints": {
      "temperature_max": 1.0,
      "temperature_min": 0.0
    }
  }
}
```

**Responses API opt-in (verbatim, "Responses API Support"):**
```json
{
  "your_provider": {
    "base_url": "https://api.yourprovider.com/v1",
    "api_key_env": "YOUR_PROVIDER_API_KEY",
    "supported_endpoints": ["/v1/chat/completions", "/v1/responses"]
  }
}
```

**Full field list (verbatim, Required Fields + Optional Fields):**
```
Required:
- `base_url` - API endpoint (e.g., `https://api.provider.com/v1`)
- `api_key_env` - Environment variable name for API key (e.g., `PROVIDER_API_KEY`)

Optional:
- `api_base_env` - Environment variable to override `base_url`
- `base_class` - Use `"openai_gpt"` (default) or `"openai_like"`
- `param_mappings` - Map OpenAI parameter names to provider-specific names
- `constraints` - Parameter value constraints (min/max)
- `special_handling` - Special behaviors like content format conversion
```

## Cross-References

**Candidates from `miner-related-notes.md` (cited/dismissed):**
- `source-notes/docs-litellm-completion-input-params.md` — **Cited** (Extends): its Claim 3 documents the supported-params gate's scope — any parameter LiteLLM does not classify as an OpenAI param is assumed provider-specific and passed through. The `providers.json` registry is a *prior*, declared layer on top of that gate: `param_mappings` and `constraints` rewrite OpenAI-classified params *before* the per-provider pass-through logic ever sees them.
- `source-notes/docs-litellm-creating-adapters.md` — **Cited** (Corroborates): its Claim 1 describes adapters as a bidirectional format-translation layer around LiteLLM's OpenAI-format internals; this page is the upstream sibling — the declarative registration surface that decides which OpenAI-like translation path a backend rides in the first place. Both are "format divergence is absorbed by a named, registered translation layer," at different pipeline stages (registration vs per-call adaptation).
- `source-notes/docs-litellm-generate-content.md` — **Cited** (Corroborates, weakly): its Claims 2–3 document a declared passthrough/override surface on the request side (native fields forwarded verbatim; `extra_body` wins on conflict). Same theme — the gateway's mutation behavior is governed by declared config, not inference — but a different mechanism and route.
- `source-notes/docs-litellm-batches-api.md` — **Dismissed**: batch TPM/RPM limiting and enqueued-token reservation; unrelated to provider registration.
- `source-notes/docs-litellm-completion-web-search.md` — **Dismissed**: provider-native web-search feature matrix; unrelated to the registration schema.
- `source-notes/docs-litellm-files-endpoints.md` — **Dismissed**: provider-level `/files` passthrough and encoded file/batch IDs; unrelated.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**: audio-transcription fallbacks and `model_info: mode` routing; unrelated to `providers.json`.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**: Bedrock native Invoke passthrough and bearer-token auth swap; a different passthrough surface, not the OpenAI-like registry.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **Dismissed**: within-request advisor-tool composition and usage accounting; unrelated.
- `source-notes/blog-litellm-auto-router-v2.md` — **Dismissed**: routing-strategy collapse (complexity/semantic/adaptive); routing policy, not provider registration.

**Additional cross-references (Prospector-flagged; verified per §4b):**
- **Extends** `source-notes/docs-litellm-provider-specific-params.md` — same theme (param-name divergence across providers) via a **different mechanism**: that note's Claim 2 documents the two runtime ways to pass provider-specific params (per-call kwarg, or a provider config *class* like `litellm.OllamaChatConfig(num_predict=200)`), and Claim 3 catalogs the wire-name divergence (`num_predict` / `max_new_tokens` / `maxOutputTokens`). This page adds the third, static mechanism: a JSON registry entry that renames and clamps params for every request to that provider, no Python and no per-call kwarg. Complementary, not duplicate — request-side vs registration-side.
- **Extends** `source-notes/failure-litellm-vllm-embeddings-encoding-format.md` — same shared `openai_like` forwarding boundary. That failure (its Claim 1) was an *accidental* mutation through the shared path (explicit-`None` injection breaking vLLM's strict validation), cured by filter-to-omit (Claim 4). This page documents the *intentional, declared* rewrite surface on the same boundary: `param_mappings` and `constraints` are the config-half where a renamed or clamped param on a vendor is explained by lookup rather than debugging. No contradiction — different halves of one mechanism.
- **Contradicts**: None. Verified against the notes above and `guide/05-llm-ops-reliability.md` §§"Provider parity in the shared forwarding path" / "Per-backend constraints are conditioning variables" — the guide states the rules (filter-to-omit; document per-backend constraints) without naming the `providers.json` mechanism; this source supplies the mechanism, it does not oppose the rules. No contradiction issue filed.
- **Novel**: First corpus coverage of (1) `litellm/llms/openai_like/providers.json` as the named place-to-look for gateway-side silent param renames/clamps on OpenAI-compatible backends; (2) the full registration field schema (`base_url`, `api_key_env`, `api_base_env`, `base_class`, `param_mappings`, `constraints`, `special_handling`, `supported_endpoints`); (3) the `supported_endpoints` default trap (`[]` on omission, chat completions always on, `/v1/responses` opt-in only); (4) `api_base_env` as the registration-side per-environment base-URL override.

## Guide Impact

- **Chapter 05 — "Provider parity in the shared forwarding path"**: Name `litellm/llms/openai_like/providers.json` as the place-to-look mechanism. The section currently states the *rule* (treat present-but-null vs omitted as a compat surface; filter-to-omit) citing the vLLM-embeddings failure note; add the counterpart: a provider's wire payload can also be *deliberately* rewritten by declared registry config (`param_mappings`, `constraints`), so an unexplained renamed-or-capped param on a vendor should be checked against the registry entry before suspecting a bug.
- **Chapter 05 — "Per-backend constraints are conditioning variables"**: The section's "document per-backend constraints" advice now has a named home: `constraints` (`temperature_max` / `temperature_min`) is the declarative form of exactly that, enforced gateway-side on every request. Recommend showing the `constraints` JSON snippet as the worked example.
- **Chapter 05 — gateway/backends (new short subsection or paragraph)**: Capture the endpoint-enablement rule — JSON providers always serve chat completions; `supported_endpoints` defaults to `[]` and non-chat endpoints (`/v1/responses`) are opt-in only — and the `api_base_env` base-URL override knob as the registration-side equivalent of per-environment `api_base` swapping. Also record the documented no-Python boundary (OAuth/JWT and complex transforms force a Python config class), so operators know the declarative path's honest limits.

## Extraction Notes

- Source fetched in full via WebFetch (markdown render of the Docusaurus page, 2026-10-17); no paywall, no truncation. The page is short by design (a schema reference); no substantive sub-pages were followed — nav siblings under Contributing/Providers are distinct pages filed or triaged separately (#1637, #1638 are sibling crawl findings, not sub-pages of this one).
- Per Prospector triage, contributor-process content (PR/merge workflow, Testing one-liner, `base_class` inheritance mechanics, Python escape-hatch file paths) was deliberately **not** mined; Claim 7 records only the trigger list for needing Python, not the implementation.
- All quotes copied character-for-character from the rendered page. `special_handling` is listed in the schema but the page gives no example of it; no claim beyond its one-line description was made.
- Cross-reference candidates from `miner-related-notes.md` all cited or dismissed above; the two Prospector-flagged notes (`docs-litellm-provider-specific-params.md`, `failure-litellm-vllm-embeddings-encoding-format.md`) were re-read and their cited claims (Claim 2/3 and Claim 1/4 respectively) verified in place per §4b.
- `confidence_overall: emerging` — first-party vendor docs with concrete schema and examples, but no independent validation, no operational evidence, and several fields (`special_handling`, `base_class` choice criteria) documented only as one-liners. Matches the convention in the sibling note `docs-litellm-provider-specific-params.md`.
