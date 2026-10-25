---
source_url: https://docs.litellm.ai/docs/fine_tuning
source_type: docs
title: /fine_tuning — LiteLLM AI Gateway Documentation
author: LiteLLM
date_published: unknown
date_extracted: 2026-10-25
last_checked: 2026-10-25
status: current
confidence_overall: emerging
issue: "#1723"
---

# /fine_tuning — LiteLLM AI Gateway Documentation

> LiteLLM exposes OpenAI-compatible fine-tuning/file operations for select providers behind the proxy, gated behind Enterprise, configured via `finetune_settings` and `files_settings`, with fine-tuning cost tracking marked partial.

## Source Context

- **Type**: docs (vendor API reference)
- **Author credibility**: Official LiteLLM documentation
- **Scope**: Covers config keys (`finetune_settings`, `files_settings`), creating files for fine-tuning, creating/cancelling/listing fine-tuning jobs, supported providers (OpenAI, Azure OpenAI, Vertex AI), and feature matrix including cost tracking/logging. Does not cover routing/retries/rate limits/error catalogue/measurements.

## Extracted Claims

### Claim 1: Fine-tuning is an Enterprise-gated feature with a partial cost-tracking row
- **Evidence**: Feature table on the page marks "Cost Tracking" as "Not yet" with note "Let us know if you need this" and links to GitHub issue. "Logging" is marked ✅.
- **Confidence**: settled
- **Quote**: "Feature\n\nSupported\n\nNotes\n\nSupported Providers\n\nOpenAI, Azure OpenAI, Vertex AI\n\n-\n\n#### See an exhaustive list of supported models and providers at [models.litellm.ai](https://models.litellm.ai/)\n\n| Cost Tracking | Not yet | [Let us know if you need this](https://github.com/BerriAI/litellm/issues) | | Logging | ✅ | Works across all logging integrations |"
- **Our assessment**: This is the load-bearing finding per triage - billable surface (training jobs/files) whose spend the gateway does not fully attribute; contrast against cost-map spend patterns.

### Claim 2: Provider dispatch uses per-request `custom-llm-provider` header against explicit config blocks
- **Evidence**: Examples show passing `extra_headers={"custom-llm-provider": "azure"}` (Python) and `-H "custom-llm-provider: azure"` (curl). Config shows `finetune_settings` and `files_settings` as top-level blocks listing providers with their credentials/params.
- **Confidence**: settled
- **Quote**: "client = AsyncOpenAI(api_key=\"sk-<your-litellm-api-key>\", base_url=\"http://0.0.0.0:4000\") # base_url is your litellm proxy url\nfile_name = \"openai_batch_completions.jsonl\"\nresponse = await client.files.create(\n    extra_headers={\"custom-llm-provider\": \"azure\"}, # tell litellm proxy which provider to use\n    file=open(file_name, \"rb\"),\n    purpose=\"fine-tune\",\n)"
- **Our assessment**: Dispatch is header-driven against explicit config blocks (not inferred from model alone in this surface) - a separate dispatch path from normal model routing.

### Claim 3: Fine-tuning configuration uses dedicated `finetune_settings` and `files_settings` blocks
- **Evidence**: Page states "Add `finetune_settings` and `files_settings` to your litellm config.yaml to use the fine-tuning endpoints." Example shows provider entries with `custom_llm_provider`, credentials (env/file paths), and api params.
- **Confidence**: settled
- **Quote**: "Add `finetune_settings` and `files_settings` to your litellm config.yaml to use the fine-tuning endpoints.\n\n## Example config.yaml for `finetune_settings` and `files_settings`[​](#example-configyaml-for-finetune_settings-and-files_settings \"Direct link to example-configyaml-for-finetune_settings-and-files_settings\")\n\n```\nmodel_list:  - model_name: gpt-6.1-sol    litellm_params:      model: openai/fake      api_key: fake-key      api_base: https://exampleopenaiendpoint-production.up.railway.app/# For /fine_tuning/jobs endpointsfinetune_settings:  - custom_llm_provider: azure    api_base: https://exampleopenaiendpoint-production.up.railway.app    api_key: os.environ/AZURE_API_KEY    api_version: \"2023-03-15-preview\"  - custom_llm_provider: openai    api_key: os.environ/OPENAI_API_KEY  - custom_llm_provider: \"vertex_ai\"    vertex_project: \"adroit-crow-413218\"    vertex_location: \"us-central1\"    vertex_credentials: \"/Users/ishaanjaffer/Downloads/adroit-crow-413218-a956eef1a2a8.json\"# for /files endpointsfiles_settings:  - custom_llm_provider: azure    api_base: https://exampleopenaiendpoint-production.up.railway.app    api_key: fake-key    api_version: \"2023-03-15-preview\"  - custom_llm_provider: openai    api_key: os.environ/OPENAI_API_KEY\n```"
- **Our assessment**: Separate config surface from `model_list`; credentials can come from env vars or local files (Vertex). This is config-drift boundary relevant to credential handling.

### Claim 4: Workflow is files upload then create/cancel/list fine-tuning jobs
- **Evidence**: Sections cover creating file for fine-tuning (upload to `/v1/files` with purpose fine-tune), creating job (requires `model`, `training_file`, optional hyperparams/suffix/validation_file/integrations/seed), cancelling job, listing jobs. All via OpenAI SDK style or curl with `custom-llm-provider` header.
- **Confidence**: settled
- **Quote**: "## Create File for fine-tuning[​](#create-file-for-fine-tuning \"Direct link to Create File for fine-tuning\")\n\n-   OpenAI Python SDK\n-   curl\n\n```\nclient = AsyncOpenAI(api_key=\"sk-<your-litellm-api-key>\", base_url=\"http://0.0.0.0:4000\") # base_url is your litellm proxy urlfile_name = \"openai_batch_completions.jsonl\"response = await client.files.create(    extra_headers={\"custom-llm-provider\": \"azure\"}, # tell litellm proxy which provider to use    file=open(file_name, \"rb\"),    purpose=\"fine-tune\",\n)```\n\n## Create fine-tuning job[​](#create-fine-tuning-job \"Direct link to Create fine-tuning job\")\n\n-   Azure OpenAI\n\n-   OpenAI Python SDK\n-   curl\n\n```\nft_job = await client.fine_tuning.jobs.create(    model=\"gpt-4.1-2025-04-14\",                   # Azure OpenAI model you want to fine-tune    training_file=\"file-abc123\",                 # file_id from create file response    extra_headers={\"custom-llm-provider\": \"azure\"}, # tell litellm proxy which provider to use)\n```"
- **Our assessment**: Uses top-level `/v1/files` and `/v1/fine_tuning/jobs` endpoints; training data uploaded as JSONL.

### Claim 5: Hyperparameters and options are passed through as documented
- **Evidence**: Request body documents `model`, `custom_llm_provider` (required), `training_file` (required), `hyperparameters` (batch_size, learning_rate_multiplier, n_epochs), `suffix`, `validation_file`, `integrations`, `seed`. Example shows full payload.
- **Confidence**: settled
- **Quote**: "-   `hyperparameters`\n    \n    **Type:** object  \n    **Required:** No  \n    The hyperparameters used for the fine-tuning job.\n    \n    > #### Supported `hyperparameters`[​](#supported-hyperparameters \"Direct link to supported-hyperparameters\")\n    > \n    > #### batch_size[​](#batch_size \"Direct link to batch_size\")\n    \n    **Type:** string or integer  \n    **Required:** No  \n    Number of examples in each batch...\n    > #### learning_rate_multiplier[​](#learning_rate_multiplier \"Direct link to learning_rate_multiplier\")\n    \n    **Type:** string or number  \n    **Required:** No  \n    Scaling factor for the learning rate...\n    > #### n_epochs[​](#n_epochs \"Direct link to n_epochs\")\n    \n    **Type:** string or integer  \n    **Required:** No  \n    The number of epochs to train the model for..."
- **Our assessment**: Standard OpenAI-style params passed through; provider support varies as noted.

## Concrete Artifacts

```yaml
# Example config.yaml for finetune_settings and files_settings
model_list:
  - model_name: gpt-6.1-sol
    litellm_params:
      model: openai/fake
      api_key: fake-key
      api_base: https://exampleopenaiendpoint-production.up.railway.app
# For /fine_tuning/jobs endpoints
finetune_settings:
  - custom_llm_provider: azure
    api_base: https://exampleopenaiendpoint-production.up.railway.app
    api_key: os.environ/AZURE_API_KEY
    api_version: "2023-03-15-preview"
  - custom_llm_provider: openai
    api_key: os.environ/OPENAI_API_KEY
  - custom_llm_provider: "vertex_ai"
    vertex_project: "adroit-crow-413218"
    vertex_location: "us-central1"
    vertex_credentials: "/Users/ishaanjaffer/Downloads/adroit-crow-413218-a956eef1a2a8.json"
# for /files endpoints
files_settings:
  - custom_llm_provider: azure
    api_base: https://exampleopenaiendpoint-production.up.railway.app
    api_key: fake-key
    api_version: "2023-03-15-preview"
  - custom_llm_provider: openai
    api_key: os.environ/OPENAI_API_KEY
```

```python
# Create fine-tuning job (Azure OpenAI)
ft_job = await client.fine_tuning.jobs.create(
    model="gpt-4.1-2025-04-14",                   # Azure OpenAI model you want to fine-tune
    training_file="file-abc123",                 # file_id from create file response
    extra_headers={"custom-llm-provider": "azure"}, # tell litellm proxy which provider to use
)
```

```bash
# Create file for fine-tuning
curl http://localhost:4000/v1/files \
    -H "Authorization: Bearer $LITELLM_API_KEY" \
    -H "custom-llm-provider: azure" \
    -F purpose="batch" \
    -F file="@mydata.jsonl"
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-files-endpoints.md` (Claim 2: Files shared dependency across Assistants/Fine-tuning/Batch; Claim 5 describes legacy `files_settings` and migration to `model_list`) — fine-tuning uses top-level `/v1/files` upload path; files surface is shared dependency.
  - `source-notes/docs-litellm-batches-api.md` (Claims re batch limits/skip settings) — both use file upload patterns; page shows purpose `batch` in curl example for files upload in this doc context.
- **Contradicts**: (none found)
- **Extends**:
  - `source-notes/docs-litellm-container-files-api.md`, `source-notes/docs-litellm-containers-api.md` — different file/artifact surfaces (`/containers/files` vs top-level `/v1/files` for fine-tuning); reconcile that these are distinct stores/surfaces.
- **Novel**:
  - `finetune_settings` config block and fine-tuning specific dispatch surface not covered in existing notes.
  - Feature table explicitly marks **Cost Tracking as "Not yet"** for fine-tuning (vendor-acknowledged gap) — spend attribution hole for billable training jobs.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — cost accounting/model enablement)**: Record fine-tuning as a billable surface with **partial/no cost tracking** in the gateway today; clarify whether `model_list` cost entries apply to fine-tune jobs or if spend is invisible to spend/SLO pipeline. Treat as known blind spot until cost tracking is implemented.
- **Chapter 06 (Security and Trust — credential routing/config drift)**: Document `finetune_settings`/`files_settings` as separate declare-don't-infer config blocks with header-driven provider selection (`custom-llm-provider`); note credentials can come from env vars or local file paths (Vertex) and Enterprise gating.
- **Chapter 02 (Observability — spend telemetry as SLI input)**: Note cost tracking gap for fine-tuning jobs as a telemetry gap affecting spend SLIs.

## Extraction Notes

- Read the full page including config example, file creation, job creation/cancel/list, and feature table. No sub-pages followed (page is self-contained reference). Thin reference with no error catalogue/rate limits/retries/measurements; load-bearing finding is the cost-tracking partial/gap.
- Cross-referenced against candidate list in `miner-related-notes.md` (batches-api, files-endpoints, etc.) and existing litellm notes; no existing note covers `finetune_settings`/fine-tuning cost-tracking gap.
