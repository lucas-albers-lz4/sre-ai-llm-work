---
source_url: https://docs.litellm.ai/docs/completion/prompt_formatting
source_type: docs
title: "Prompt Formatting | liteLLM"
author: "LiteLLM (vendor docs)"
date_published: unknown (living vendor docs; current as of 2026-10-06)
date_extracted: 2026-10-06
last_checked: 2026-10-06
status: current
confidence_overall: emerging
issue: "#1558"
---

# Prompt Formatting (LiteLLM Docs)

> LiteLLM's prompt-formatting layer translates OpenAI ChatCompletions `messages` into provider-native prompts, with an optional registered custom template that only applies to a narrow class of "raw text prompt" providers and silently does nothing for several chat-endpoint providers.

## Source Context

- **Type**: docs (single-page LiteLLM SDK reference at `/docs/completion/prompt_formatting`). Page breadcrumb: "Guides → Prompts & Context → Prompt Formatting". Verified accessible HTTP 200 (current snapshot extracted 2026-10-06).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation. Authoritative for the *documented* behavior of the SDK/proxy prompt-translation layer, but no independent validation, metrics, or revision history present on the page.
- **Scope**: Covers (1) stored/bundled prompt templates and their applicability rules, (2) registering a custom template via `litellm.register_prompt_template()`, (3) the exact API shape for registered templates (`initial_prompt_value`, `roles{...}.pre_message/post_message`, `final_prompt_value`), (4) the provider applicability set (raw-prompt vs chat-endpoint), (5) a provider→formatting reference table with links to source code. Does **not** cover: the runtime effect of `add_function_to_prompt` (documented elsewhere in the corpus), the generic prompt management API (`/prompt_management`), parameter semantics of the `completion()` call (that belongs to `/completion/input`), or response normalization.
- **Redundancy / what this page owns**: The sibling page `docs-litellm-completion-input-params.md` (#1495) explicitly defers CUSTOM PROMPT TEMPLATE detail to this page ("CUSTOM PROMPT TEMPLATE (See prompt formatting for more info)"), listing the template parameter names (`initial_prompt_value`, `roles`, `final_prompt_value`, `bos_token`, `eos_token`, `hf_model_name`) in its litellm-specific params block. This page owns the **registration API contract**, the **applicability/no-op conditions**, and the **provider routing rule** that determines whether LiteLLM applies any template at all.

## Extracted Claims

### Claim 1: Prompt templates (stored or registered) apply only to providers that take a single raw text prompt — the narrow set is `ollama/`, `petals/`, `replicate/`, `sagemaker/`, `predibase/`; registered templates have no effect on `huggingface/` and `together_ai/` chat models
- **Evidence**: Explicit applicability sentence at the top of the page, and the subsequent clarification about OpenAI-compatible chat endpoints.
- **Confidence**: settled (explicit, unqualified vendor statement on the page)
- **Quote**: "Prompt templates only apply to providers that take a single raw text prompt, such as `ollama/`, `petals/`, `replicate/`, `sagemaker/`, and `predibase/`. `huggingface/` and `together_ai/` call the providers' OpenAI-compatible chat completions APIs, so LiteLLM sends your `messages` as-is and the provider applies the model's own chat template. Neither the stored templates below nor templates registered with `register_prompt_template` are used for them"
- **Our assessment**: This is the page's most operationally important claim: **custom templates registered with `register_prompt_template()` are a silent no-op for `huggingface/` and `together_ai/`**. An operator who registers a template for those models will see no effect and no error signal — a classic config-footgun. The "raw text prompt" boundary is precisely enumerated.

### Claim 2: For `sagemaker/`, the template selection depends on `hf_model_name` (to pick the correct base-model chat template); for other raw-prompt providers LiteLLM supports Hugging Face chat templates and falls back to the Hub-registered chat template
- **Evidence**: The second paragraph describing template resolution behavior.
- **Confidence**: settled (explicit vendor statement)
- **Quote**: "On `sagemaker/`, pass `hf_model_name` to pick the template for your endpoint's base model. For popular models, the templates are saved as part of the package"
- **Our assessment**: The omission of `hf_model_name` on SageMaker can select the wrong template with no error; combined with Claim 1's silence, this is a correctness footgun for raw-prompt deployments.

### Claim 3: `register_prompt_template()` is keyed by `model` name **without** the provider prefix; the template schema supports `initial_prompt_value`, `roles` with per-role `pre_message`/`post_message`, and `final_prompt_value` (all optional as documented)
- **Evidence**: The Python example shows `litellm.register_prompt_template(model="llama2", ...)` and the roles structure with `system`, `user`, `assistant` each having `pre_message`/`post_message`. Comments mark optional fields.
- **Confidence**: settled (code example + prose)
- **Quote**: "`litellm.register_prompt_template(\n    model=\"llama2\",\n    initial_prompt_value=\"You are a good assistant\", # [OPTIONAL]\n    roles={\n        \"system\": {\n            \"pre_message\": \"[INST] <<SYS>>\\n\", # [OPTIONAL]\n            \"post_message\": \"\\n<</SYS>>\\n [/INST]\\n\" # [OPTIONAL]\n        },\n        \"user\": { \n            \"pre_message\": \"[INST] \", # [OPTIONAL]\n            \"post_message\": \" [/INST]\" # [OPTIONAL]\n        }, \n        \"assistant\": {\n            \"pre_message\": \"\\n\", # [OPTIONAL]\n            \"post_message\": \"\\n\" # [OPTIONAL]\n        }\n    },\n    final_prompt_value=\"Now answer as best you can:\" # [OPTIONAL]\n)`"
- **Our assessment**: The keying by model name (no provider prefix) means a registered template for `"llama2"` will apply when using `ollama/llama2` (a raw-prompt path) but will **not** apply when using `together_ai/llama2` or `huggingface/...` chat paths — the provider-prefix omission combined with Claim 1 is the mechanism. The documented contract is precisely as shown.

### Claim 4: The registration API is supported only for raw-prompt providers; the example uses `ollama/llama2` (not `ollama_chat/`) to make the template take effect
- **Evidence**: Text immediately following the code block.
- **Confidence**: settled
- **Quote**: "This is supported for raw-prompt providers such as Ollama (`ollama/`, not `ollama_chat/`), Petals, Replicate, SageMaker, and Predibase. It has no effect on `huggingface/` or `together_ai/` chat models"
- **Our assessment**: Explicitly warns against the `ollama_chat/` prefix (chat endpoint variant), reinforcing the raw-prompt vs chat split. The provider prefix is the discriminant for whether templates apply.

### Claim 5: The page lists bundled/stored templates and links to the implementation; the "All Providers" table maps provider names to model patterns and to source code paths in the LiteLLM repo
- **Evidence**: A table of stored templates (Mistral-7B-Instruct-v0.1, Llama-2-7b-chat, falcon-7b-instruct, mpt-7b-chat, CodeLlama-34b-Instruct-hf, WizardCoder, Phind-CodeLlama) and a second table ("All Providers") with columns Provider, Model Name, Code linking to specific files in the repo (e.g. `litellm/llms/anthropic.py`, `litellm/llms/replicate.py`, `litellm/llms/huggingface_restapi.py`, `litellm/llms/together_ai.py`, `litellm/llms/petals.py`, etc.). Also links to `litellm_core_utils/prompt_templates/factory.py`.
- **Confidence**: settled (reference data from the vendor page)
- **Quote**: (representative) "Here's the code for how we format all providers..." with table entries including Anthropic (claude-instant-1, claude-instant-1.2, claude-2) linking to anthropic.py, TogetherAI (all model names starting with `together_ai/`) linking to together_ai.py, Petals (all model names starting with `petals/`) linking to petals.py, NLP Cloud (all model names starting with `palm/`) linking to nlp_cloud.py.
- **Our assessment**: The bundled templates are legacy chat model families (LLaMA 2 chat, Mistral v0.1, Falcon, MPT, CodeLlama, WizardCoder, Phind) — consistent with the page covering both legacy raw-prompt paths and the general formatting machinery. The NLP Cloud row in the "All Providers" table says "all model names starting with `palm/`" (copy-paste artifact noted by triage) — the table is a reference to implementation mapping, not a correctness claim we need to second-guess; we record it as part of the documented surface.

## Concrete Artifacts

```python
# Register a custom prompt template (keyed by model name, no provider prefix)
# Only takes effect for raw-prompt providers (ollama/, not ollama_chat/; petals/; replicate/; sagemaker/; predibase/)
# No effect on huggingface/ or together_ai/ chat models
import litellm
from litellm import completion

litellm.register_prompt_template(
    model="llama2",
    initial_prompt_value="You are a good assistant",  # [OPTIONAL]
    roles={
        "system": {
            "pre_message": "[INST] <<SYS>>\n",  # [OPTIONAL]
            "post_message": "\n<</SYS>>\n [/INST]\n"  # [OPTIONAL]
        },
        "user": {
            "pre_message": "[INST] ",  # [OPTIONAL]
            "post_message": " [/INST]"  # [OPTIONAL]
        },
        "assistant": {
            "pre_message": "\n",  # [OPTIONAL]
            "post_message": "\n"  # [OPTIONAL]
        }
    },
    final_prompt_value="Now answer as best you can:"  # [OPTIONAL]
)

messages = [{"role": "user", "content": "Hey, how's it going?"}]
response = completion(
    model="ollama/llama2",
    messages=messages,
    api_base="http://localhost:11434"
)
print(response['choices'][0]['message']['content'])
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-completion-input-params.md` (#1495) — lists CUSTOM PROMPT TEMPLATE params (`initial_prompt_value`, `roles`, `final_prompt_value`, `bos_token`, `eos_token`, `hf_model_name`) and defers detail to this page. Confirms `hf_model_name` is SageMaker-specific.
  - `source-notes/docs-litellm-completion-prefix.md` — references prompt formatting machinery; no direct duplication of the no-op conditions.
- **Contradicts**: None identified on this page. (Open contradiction #1550 concerns `add_function_to_prompt` scope; that does not appear on this page.)
- **Extends**: None required. This page fills the detail deferred by #1495 rather than extending a specific mined claim.
- **Novel**: The explicit enumeration that `register_prompt_template()` is a **silent no-op for `huggingface/` and `together_ai/` chat models** is the concrete, extractable config-footgun not previously stated as a standalone claim in the existing notes. Also the `ollama_chat/` exclusion is explicit.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add a short "Prompt template registration caveats" subsection covering (a) templates only apply to raw-prompt providers (`ollama/`, `petals/`, `replicate/`, `sagemaker/`, `predibase/`); (b) registering templates has **no effect and no error** for `huggingface/` and `together_ai/` (chat endpoints) — operators should not expect behavior change; (c) on `sagemaker/`, set `hf_model_name` to select the correct base template; (d) for Ollama use `ollama/` (not `ollama_chat/`) if relying on custom templates. This is a silent-failure trap similar in shape to other "silently dropped/ignored params" already called out in Ch05.
- **Chapter 02 (Observability)**: Note that template registration produces no observability signal on no-op paths (no warning/error) — relevant when debugging "why didn't my custom template change outputs?".

## Extraction Notes

- Deep-read of a short, self-contained docs page (17 lines of substantive text plus code block and two tables). Followed no sub-pages (none linked as required follow-ups).
- No paywall, source fully readable. No contradiction found with existing notes; no new contradiction filed (the only open contradiction #1550 is about `add_function_to_prompt`, absent here).
- Cross-referenced #1495 to avoid duplicating its param list; this note only extracts the registration contract and no-op conditions.
- Did not commit `miner-related-notes.md`.
