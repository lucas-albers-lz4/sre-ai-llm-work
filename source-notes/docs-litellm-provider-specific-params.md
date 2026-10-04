---
source_url: https://docs.litellm.ai/docs/completion/provider_specific_params
source_type: docs
title: "Provider-specific Params | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-10-04)
date_extracted: 2026-10-04
last_checked: 2026-10-04
status: current
confidence_overall: emerging
issue: "#1572"
---

# Provider-specific Params (LiteLLM Docs)

> LiteLLM treats any non-OpenAI param as a provider-specific param and passes it to the provider in the request body as a kwarg. The page documents a per-call pass-through, a per-provider config-class approach, and a small set of concrete metadata knobs used for cost attribution/labeling.

## Source Context

- **Type**: docs (LiteLLM gateway documentation, `/docs/completion/provider_specific_params`).
- **Author credibility**: LiteLLM (first-party product docs). Authoritative for documented knob surface; no independent validation or metrics.
- **Scope**: (1) General rule: non-OpenAI params pass through to provider as kwargs; (2) two ways to pass provider-specific params (per-call kwarg, or via provider-specific config variable like `litellm.OpenAIConfig()`); (3) concrete examples showing max-tokens set via both methods across many providers; (4) explicit HuggingFace caveat (config defaults not read); (5) Proxy usage (config + request examples); (6) Provider-Specific Metadata Parameters table (Bedrock `requestMetadata`, Gemini/Vertex `labels`, Anthropic `metadata`).

## Extracted Claims

### Claim 1: General pass-through rule — any non-OpenAI param is treated as provider-specific and passed to the provider in the request body as a kwarg
- **Evidence**: Opening sentence of the page body states the rule and links to the reserved params list in `litellm/main.py`.
- **Confidence**: settled (explicit vendor statement).
- **Quote**: "Providers might offer params not supported by OpenAI (e.g. top_k). LiteLLM treats any non-openai param, as a provider-specific param, and passes it to the provider in the request body, as a kwarg. [**See Reserved Params**](https://github.com/BerriAI/litellm/blob/aa2fd29e48245f360e771a8810a69376464b195e/litellm/main.py#L700)"
- **Our assessment**: This is the complement of the support-gate in `docs-litellm-drop-params.md` (Claim 2/3): parameters LiteLLM doesn't classify as OpenAI params are assumed provider-specific and passed through. The linked reserved params list is the source of truth for exceptions, but that file isn't fetched here.

### Claim 2: Two ways to pass provider-specific params — per-call kwarg, or via provider-specific config variable (e.g. `litellm.OpenAIConfig(...)`)
- **Evidence**: Numbered list immediately after the rule.
- **Confidence**: settled (explicit).
- **Quote**: "You can pass those in 2 ways:\n\n- via completion(): We'll pass the non-openai param, straight to the provider as part of the request body.\n  - e.g. `completion(model=\"claude-sonnet-5\", top_k=3)`\n- via provider-specific config variable (e.g. `litellm.OpenAIConfig()`)."
- **Our assessment**: The config-class form sets defaults that apply to subsequent calls using that provider context; per-call overrides are passed as kwargs. This is the mechanism behind provider-specific naming divergence shown in examples.

### Claim 3: Provider-specific config class naming and param-name divergence across providers (max_tokens vs num_predict vs max_new_tokens vs maxOutputTokens)
- **Evidence**: SDK Usage tabs show for each provider how to set max tokens via completion() and via config, with explicit config class names and param names.
- **Confidence**: settled (concrete examples on the page).
- **Quote**: "Ollama: `litellm.OllamaChatConfig(num_predict=200)`"; "Replicate: `litellm.ReplicateConfig(max_new_tokens=200)`"; "Petals: `litellm.PetalsConfig(max_new_tokens=10)`"; "AI21: `litellm.AI21Config(maxOutputTokens=10)`"; "Anthropic: `litellm.AnthropicConfig(max_tokens=200)`"; "TogetherAI: `litellm.TogetherAIConfig(max_tokens=200)`"; "Cohere: `litellm.CohereChatConfig(max_tokens=200)`"; "Azure OpenAI/OpenAI: `max_tokens` via config where shown."
- **Our assessment**: The "max tokens" concept maps to different wire names per provider (OpenAI-family `max_tokens`, Ollama `num_predict`, Replicate/Petals `max_new_tokens`, AI21 `maxOutputTokens`). The config class encapsulates provider-specific mapping. This is a concrete source of naming divergence and a potential "silently not applied" failure mode if the wrong param name is used or if config defaults are ignored (Claim 4).

### Claim 4: HuggingFace route does not read provider config defaults — config-class has no effect; pass params per-call
- **Evidence**: HuggingFace tab shows a note in text after the code block.
- **Confidence**: settled (explicit caveat).
- **Quote**: "The Huggingface route does not read provider config defaults, so `litellm.HuggingFaceChatConfig(max_tokens=...)` has no effect on the request. Pass `max_tokens` on each `completion()` call instead"
- **Our assessment**: This is a documented silent-ignore failure mode: setting provider config defaults does not guarantee they are applied for HuggingFace route. Operators must not assume config-class defaults take effect across all providers.

### Claim 5: Provider-specific metadata parameters for cost attribution/labeling (Bedrock requestMetadata, Gemini/Vertex labels, Anthropic metadata)
- **Evidence**: "Provider-Specific Metadata Parameters" section with table and code examples.
- **Confidence**: settled (explicit).
- **Quote**: "**AWS Bedrock**: `requestMetadata` → Cost attribution, logging; **Gemini/Vertex AI**: `labels` → Resource labeling; **Anthropic**: `metadata` → User identification"
- **Concrete examples**:
```python
response = litellm.completion(
    model="bedrock/us.anthropic.claude-sonnet-5",
    messages=[{"role": "user", "content": "Hello!"}],
    requestMetadata={"cost_center": "engineering"})
```
```python
response = litellm.completion(
    model="vertex_ai/gemini-3.8-flash",
    messages=[{"role": "user", "content": "Hello!"}],
    labels={"environment": "production"})
```
```python
response = litellm.completion(
    model="anthropic/claude-sonnet-5",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={"user_id": "user123"})
```
- **Our assessment**: These are operational knobs for attribution/labeling. `requestMetadata` is specific to AWS Bedrock; Gemini/Vertex uses `labels` (different semantics/names); Anthropic uses `metadata`. This is the page’s main ops-relevant content (as noted in triage). No existing note in corpus records `requestMetadata` usage pattern; existing notes touch cost attribution generally but not these specific vendor field names.

### Claim 6: Proxy usage supports provider-specific params via config (litellm_params) and via request body
- **Evidence**: Proxy Usage section shows config example with `adapter_base` under `litellm_params` and curl example passing provider-specific param in request.
- **Confidence**: settled.
- **Quote**: Config: `adapter_base: <my-special_base> # 👈 PROVIDER-SPECIFIC PARAM`; Request: `"adapater_id": "my-special-adapter-id"` (note: example shows `adapater_id` as written).
- **Our assessment**: Provider-specific params can be set at proxy deployment level (litellm_params) or passed in per-request body. The example typo `adapater_id` appears as written in the page text — we quote verbatim as published.

### Claim 7: Non-OpenAI params bypass the OpenAI-param gate and are forwarded as kwargs (complementary to drop_params)
- **Evidence**: Claim 1 + cross-reference to `docs-litellm-drop-params.md` Claim 3 context (the gate’s scope is OpenAI-param recognition).
- **Confidence**: emerging (inferred from stated rule).
- **Quote**: (implicit from Claim 1)
- **Our assessment**: This is consistent with existing corpus notes: `docs-litellm-completion-input-params.md` Claim 3 states "any parameter it does not classify as an OpenAI param is assumed provider-specific and passed into the request body as a kwarg". This page states the same rule explicitly.

## Concrete Artifacts

### General rule (verbatim)
> "Providers might offer params not supported by OpenAI (e.g. top_k). LiteLLM treats any non-openai param, as a provider-specific param, and passes it to the provider in the request body, as a kwarg. [**See Reserved Params**](https://github.com/BerriAI/litellm/blob/aa2fd29e48245f360e771a8810a69376464b195e/litellm/main.py#L700)"

### Two ways (verbatim)
> "You can pass those in 2 ways:\n\n- via completion(): We'll pass the non-openai param, straight to the provider as part of the request body.\n  - e.g. `completion(model=\"claude-sonnet-5\", top_k=3)`\n- via provider-specific config variable (e.g. `litellm.OpenAIConfig()`)."

### HuggingFace caveat (verbatim)
> "The Huggingface route does not read provider config defaults, so `litellm.HuggingFaceChatConfig(max_tokens=...)` has no effect on the request. Pass `max_tokens` on each `completion()` call instead"

### Metadata params table (verbatim)
> Provider | Parameter | Use Case
> --- | --- | ---
> **AWS Bedrock** | `requestMetadata` | Cost attribution, logging
> **Gemini/Vertex AI** | `labels` | Resource labeling
> **Anthropic** | `metadata` | User identification

### Metadata code examples (verbatim)
```python
import litellm
response = litellm.completion(
    model="bedrock/us.anthropic.claude-sonnet-5",
    messages=[{"role": "user", "content": "Hello!"}],
    requestMetadata={"cost_center": "engineering"})
```
```python
import litellm
response = litellm.completion(
    model="vertex_ai/gemini-3.8-flash",
    messages=[{"role": "user", "content": "Hello!"}],
    labels={"environment": "production"})
```
```python
import litellm
response = litellm.completion(
    model="anthropic/claude-sonnet-5",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={"user_id": "user123"})
```

### Proxy config example (verbatim)
```yaml
model_list:
    - model_name: llama-3-8b-instruct
      litellm_params:
        model: predibase/llama-3-8b-instruct
        api_key: os.environ/PREDIBASE_API_KEY
        tenant_id: os.environ/PREDIBASE_TENANT_ID
        max_tokens: 256
        adapter_base: <my-special_base> # 👈 PROVIDER-SPECIFIC PARAM
```

### Proxy request example (verbatim, includes typo as published)
```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H "Authorization: Bearer $LITELLM_API_KEY" \
-d '{
  "model": "llama-3-8b-instruct",
  "messages": [
    {
      "role": "user",
      "content": "What'\''s the weather like in Boston today?"
    }
  ],
  "adapater_id": "my-special-adapter-id"}'
```

## Cross-References

**Candidates from `miner-related-notes.md` (cited/dismissed):**
- `source-notes/docs-litellm-completion-input-params.md` — **Cited** (Corroborates): Claim 3 there states non-OpenAI params are assumed provider-specific and passed as kwargs; matches Claim 1 here. Also documents the support gate scope.
- `source-notes/docs-litellm-drop-params.md` — **Cited** (Complementary/Corroborates): Documents the gate (default raise vs drop_params) and `additional_drop_params`/`allowed_openai_params`. This page is the pass-through complement (what happens when params are *not* dropped).
- Others from candidates list (batches, audio, a2a, bedrock-invoke, auth, etc.) — **Dismissed** as unrelated to provider-specific param naming/pass-through/metadata.

**Additional cross-references (searched `source-notes/`):**
- **Corroborates**: `source-notes/blog-litellm-gemini-3-flash-day-0.md` notes provider-specific thinking/param conversion (Claim 6); `docs-litellm-anthropic-advisor-tool.md` mentions provider-specific behavior; but no existing note captures the exact metadata field names (`requestMetadata`, `labels`, `metadata`) or the HuggingFace config-defaults caveat in this explicit form.
- **Novel**: First corpus coverage of the explicit metadata mapping table (`requestMetadata` on Bedrock, `labels` on Vertex/Gemini, `metadata` on Anthropic) as a concrete ops-attribution pattern; first explicit documentation of HuggingFaceChatConfig having no effect (silent-ignore). Also documents provider-specific config class names and param-name divergence (num_predict/max_new_tokens/maxOutputTokens) in one place.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add note on provider-specific param naming divergence (OpenAI `max_tokens` vs Ollama `num_predict`, Replicate/Petals `max_new_tokens`, AI21 `maxOutputTokens`). Include the HuggingFace caveat as a documented silent-ignore case: config-class defaults don't apply to all providers (HuggingFace route ignores them). Pair with drop_params behavior (from docs-litellm-drop-params.md).
- **Chapter 02 (Observability)**: Add cost-attribution metadata guidance — use `requestMetadata` (Bedrock) for cost_center/logging, `labels` (Vertex/Gemini) for resource labeling, `metadata` (Anthropic) for user identification. These are vendor-specific fields that propagate for attribution; operators should be explicit about which field to set per provider.
- **Chapter 03 (Runbooks)**: When migrating across providers, don't assume param names match; check provider-specific config class and wire names. For HuggingFace, always pass params per-call.

## Extraction Notes

- Source fetched via WebFetch (markdown). Page is living vendor docs; examples include current model names like `gpt-5.6-luna`, `claude-sonnet-5`, `vertex_ai/gemini-3.8-flash`. No sub-pages followed (nav siblings filed separately). Linked reserved params file in litellm/main.py not fetched.
- Quotes are verbatim contiguous fragments. The proxy request example contains `adapater_id` as written on page (typo) — quoted verbatim per rule.
- Cross-references verified: `docs-litellm-completion-input-params.md` Claim 3 matches pass-through rule; `docs-litellm-drop-params.md` is complementary (gate). No contradiction found.
- Confidence `emerging`: vendor docs, no independent validation; metadata fields and caveat are explicit but operational impact depends on runtime behavior.
