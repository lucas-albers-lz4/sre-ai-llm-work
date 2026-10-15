---
source_url: https://docs.litellm.ai/docs/files_endpoints
source_type: docs
title: "Provider Files Endpoints — LiteLLM AI Gateway Documentation (provider-level /files passthrough)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page front-matter `last_updated: 2026-10-14`)
date_extracted: 2026-10-15
last_checked: 2026-10-15
status: current
confidence_overall: settled
issue: "#1722"
---

# Provider Files Endpoints (LiteLLM Docs)

> The gateway's provider-level `/files` passthrough — five OpenAI-format file
> operations (upload / list / retrieve / delete / content) staged in the
> provider's own storage for Assistants, Fine-tuning, and Batch API — with a
> documented credential-config migration (`files_settings` block → `model_list`)
> that the batches note explicitly scoped out, and one cost-attribution trap:
> Anthropic file bytes are **free to upload and priced as input tokens to use**.

## Source Context

- **Type**: docs (first-party vendor API reference — LiteLLM AI Gateway, living
  Docusaurus page under "Supported Endpoints > /files > Provider Files
  Endpoints"; fetched HTTP 200 on 2026-10-15, no paywall, no truncation; the
  page also exposes a markdown form at `/docs/files_endpoints.md`).
- **Author credibility**: LiteLLM (BerriAI), the gateway vendor. Authoritative
  for the *surface* it defines — the five operations, the SDK helper names, the
  legacy `files_settings` config schema, the encoded-ID routing example, the
  Bedrock S3-URI retrieval shape, the five-provider list, and Anthropic's
  documented purpose/cost caveat. It is **capability reference only**: no
  measurements, no benchmarks, no failure modes, no error catalogue, no
  versioning against any LiteLLM release. Every claim below is either a
  documented first-party contract or an absence verified against the full page.
- **Scope**: Covers (1) the five `/files` operations in proxy and SDK form,
  (2) multi-account routing via `model_list` + base64-encoded IDs, (3) the
  `model`-parameter transport options, (4) the `files_settings` → `model_list`
  migration, (5) the Bedrock S3-URI content-retrieval variant, (6) the provider
  list, and (7) the Anthropic purpose/cost note. Does **not** cover the batch
  input-file validation or batch rate-limit accounting (those live on the
  sibling `/docs/batches` page, already mined — see Cross-References), the
  container-scoped file surface (`/docs/container_files`, already mined), the
  managed-files beta, or any per-provider sub-page.

## Extracted Claims

### Claim 1: The page documents the provider-level `/files` surface as five OpenAI-format operations — upload, list, retrieve, delete, and content — available both through the proxy and through LiteLLM SDK async helpers
- **Evidence**: The opening sentence ("call the provider's `/files` endpoints
  directly, in the OpenAI format"), the Quick Start five-bullet list, the
  "LiteLLM PROXY Server" tab's five worked client calls, and the SDK tab's five
  `afile*` helpers.
- **Confidence**: settled
- **Quote**: "Use this to call the provider's `/files` endpoints directly, in the OpenAI format."
- **Our assessment**: This is the endpoint surface the batches note and the
  container-files note each explicitly did **not** cover: a generic
  OpenAI-shape passthrough to the provider's native file API, distinct from
  batch-input files (`docs-litellm-batches-api.md`, scope) and from
  container-scoped artifacts (`docs-litellm-container-files-api.md`). The five
  operations are the OpenAI `/v1/files` set; the page presents the Quick Start
  as a bare five-bullet list (the executable examples live under the proxy and
  SDK tabs), so the contract is "the provider's endpoints, proxied", not a
  gateway-defined file model.

### Claim 2: Files are a shared dependency of three distinct features — Assistants, Fine-tuning, and Batch API — so one upload surface governs workloads with very different lifecycles
- **Evidence**: The page's opening sentence under the H1.
- **Confidence**: settled
- **Quote**: "Files are used to upload documents that can be used with features like Assistants, Fine-tuning, and Batch API."
- **Our assessment**: The `purpose` parameter is what discriminates the
  workloads (the examples use `"user_data"`, `"fine-tune"`, and `"batch"`), but
  this page documents no `purpose`→feature contract of its own — the batch-only
  validation lives on the batches page (that note's Claim 7). Governance
  consequence: a retention or egress policy scoped to "batch files" misses the
  Assistant and fine-tuning uploads that flow through the same endpoint, and all
  three land in provider-side storage.

### Claim 3: Multi-account routing works without a database because the returned file/batch ID embeds the model name — the encoded ID is base64 of `litellm:<id>;model,<name>`, and later retrieve/delete/content/batch calls route off the ID alone
- **Evidence**: The "Multi-Account Support (Multiple OpenAI Keys)" section's
  five-step "How It Works" list and the "How Encoded IDs Work" section (decode →
  extract model → look up credentials → route; original provider ID preserved
  internally), with the worked example ID
  `file-bGl0ZWxsbTpmaWxlLWFiYzEyMzttb2RlbCxncHQtNG8taWZvb2Q` decoding to
  `litellm:file-abc123;model,gpt-4o-ifood`.
- **Confidence**: settled for the mechanism; the page states **no** precedence
  among the three `model`-transport surfaces (see Claim 4)
- **Quote**: "Use different OpenAI API keys for files and batches by specifying a `model` parameter that references entries in your `model_list`." and "The encoded ID is base64-encoded and looks like: `file-bGl0ZWxsbTpmaWxlLWFiYzEyMzttb2RlbCxncHQtNG8taWZvb2Q`"
- **Our assessment**: This is the **same routing scheme** already documented in
  `docs-litellm-batches-api.md` Claim 10 (base64 of `litellm:<id>;model,<name>`,
  IDs "remember" their account, stateless/no-DB) — the Prospector's bounding
  says not to re-extract it, and this note does not. What this page adds is the
  *file-side* worked example (`file-…` → `litellm:file-abc123;model,gpt-4o-ifood`)
  and the fact that the routing example is presented inside the `/files`
  reference itself rather than only on the batches page.

### Claim 4: The `model` parameter can be passed three ways — request body (`extra_body`), query parameter (`?model=`), or header (`x-litellm-model`) — and is only needed on the call that creates the object
- **Evidence**: The "Parameter Options" section's prose line and three bullets;
  the worked example passes `model` once on create and then reuses the returned
  ID with no model.
- **Confidence**: settled
- **Quote**: "You can pass the `model` parameter via:" / "**Request body**: `extra_body={\"model\": \"gpt-4o-litellm\"}`" / "**Query parameter**: `?model=gpt-4o-litellm`" / "**Header**: `x-litellm-model: gpt-4o-litellm`"
- **Our assessment**: Corroborates the three-transport parameter pattern the
  containers note records for provider selection
  (`docs-litellm-containers-api.md`, Claim 6). The transport name here is
  `x-litellm-model`, distinct from the legacy `custom-llm-provider` header — so
  a gateway that strips or sets `x-litellm-model` at the edge silently chooses
  the account, same class of edge-injection hazard the containers note flags for
  its provider header. The page states no priority order among body/query/header
  (unlike the containers note); none is asserted here.

### Claim 5: The legacy `files_settings` config is a separate per-provider credential block (`custom_llm_provider`, `api_base`, `api_key`, `api_version`) that required a `custom-llm-provider` header on every call, and the page recommends migrating to `model_list` entries instead
- **Evidence**: The "Migration from files_settings" section — "Old approach
  (still works)" config + per-call-header client code, then "New approach
  (recommended)" `model_list` config + create-once/use-ID client code — plus the
  "for /files endpoints" `config.yaml` block showing the Azure entry with
  `api_version: "2023-03-15-preview"`.
- **Confidence**: settled
- **Quote**: "**Old approach (still works):**" / "**New approach (recommended):**" / "# Had to specify provider on every call" / "# Specify model once on create"
- **Our assessment**: This is a config-layer claim no existing note carries.
  `files_settings` is a **distinct config surface from `model_list`** — entries
  are keyed by `custom_llm_provider` and carry `api_base` / `api_key` /
  `api_version`, not a `model_name` alias — so the `/files` credential store is
  not the model router. Migration is explicitly *not* deprecation ("still
  works"): two live credential paths can coexist, which is exactly the kind of
  "declare the credential once" ambiguity the guide's Ch06 rule targets
  (`guide/06-security-and-trust.md:603`). The old path's documented UX tax — a
  `custom-llm-provider` header on *every* call — is what the model_list form
  removes by moving routing into the returned ID.

### Claim 6: Bedrock content retrieval is routed by an S3 URI rather than an opaque file ID — `afile_content(file_id="s3://bucket/path.jsonl", custom_llm_provider="bedrock", aws_region_name="us-west-2")`, returning `content.text`
- **Evidence**: The SDK tab's "Get File Content (Bedrock)" example and its inline
  comment.
- **Confidence**: settled
- **Quote**: "# For Bedrock batch output files stored in S3" / "    file_id=\"s3://bucket-name/path/to/file.jsonl\",  # S3 URI or unified file ID" / "    aws_region_name=\"us-west-2\""
- **Our assessment**: Operationally distinct from the plain file-ID form: the
  `file_id` slot accepts a **customer-owned S3 location** and the call is
  region-scoped by an explicit `aws_region_name`, with output read from
  `content.text`. The comment "S3 URI or unified file ID" is the only signal the
  two forms are interchangeable. The page documents no behavior when the URI's
  bucket region disagrees with `aws_region_name`, and no access-control story
  for a bucket the gateway can read — for a security chapter, this is where the
  gateway's file surface reaches directly into operator AWS storage.

### Claim 7: Provider coverage is exactly five — OpenAI, Azure OpenAI, Vertex AI, Bedrock, Anthropic — presented as a bare link list with no per-provider operation matrix and no per-provider caveat other than the Anthropic note
- **Evidence**: The "**Supported Providers**" section (five provider headings,
  each a link to that provider's page) and the absence of any table or
  capability grid anywhere on the page.
- **Confidence**: settled (that the list is bare and unqualified)
- **Quote**: (no direct quote; the five-item provider list — see Concrete Artifacts)
- **Our assessment**: Recorded as a routing-eligible list, **not** a
  feature-parity claim. Unlike the web-search/web-fetch pages' support matrices,
  this page never says which of the five operations each provider supports, nor
  whether cost tracking/logging/streaming apply. A reader could reasonably
  assume the five operations are uniform across all five providers; the page
  does not establish it.

### Claim 8: Anthropic's Files API is documented as semantically different from OpenAI's — upload once and reference by `file_id` across Messages rather than re-uploading — with the cost rule that Files API operations are free but file content used in Messages requests is priced as input tokens
- **Evidence**: The `:::` note block under the Anthropic provider link.
- **Confidence**: settled (stated first-party; no measurement needed — it is a
  billing/behavior statement)
- **Quote**: "Anthropic Files API has a different purpose than OpenAI's. Rather than serving Batches or Fine-tuning, it lets you upload a file once and reference it by `file_id` in multiple messages, avoiding re-uploads. File API operations are free; file content used in Messages requests is priced as input tokens."
- **Our assessment**: The corpus's **only concrete file-cost attribution
  statement** and the page's highest-value operational claim. It is a
  cost-attribution trap for Ch02: counting Files API calls (or bytes uploaded)
  understates spend entirely, because the cost lands on the *Messages* call that
  consumes the file, not on the Files operation that staged it — a file can be
  free to upload and expensive to use. Scope caveat: the page states this for
  **Anthropic only**; it gives no cost statement for the other four providers.
  No existing note carries this rule (verified — see Cross-References).

### Claim 9: A second documented purpose of the surface is feature staging only — the SDK helpers are async-only and named `acreate_file` / `afile_list` / `afile_retrieve` / `afile_delete` / `afile_content`, each taking `custom_llm_provider` explicitly, with `afile_list(limit=…)` as the only pagination hint
- **Evidence**: The SDK tab's five code blocks and the `afile_list` example's
  `limit=10` argument.
- **Confidence**: settled
- **Quote**: "files = await litellm.afile_list(" / "    limit=10" / "    custom_llm_provider=\"openai\","
- **Our assessment**: The SDK path requires `custom_llm_provider` on **every**
  call — the same observation the container-files note makes about its helpers —
  while on the proxy path the credential is carried by the config/ID. `limit=10`
  is the only numeric bound on the page, and it is an example argument, not a
  documented range/default (contrast the containers/container-files notes, whose
  list contracts document `1–100, default 20`). No retry, timeout, or
  partial-failure semantics are documented for any helper.

### Claim 10: The worked proxy example passes `model` through `extra_body` for `client.files.list` but through `extra_query` for `client.batches.list`, with no explanation of the difference
- **Evidence**: The "Usage Example" Python block — the two list calls and their
  trailing comments.
- **Confidence**: settled (that the page shows two different transports without
  reconciling them)
- **Quote**: "files = client.files.list(" / "    extra_body={\"model\": \"gpt-4o-free\"}  # List free files" / "batches = client.batches.list(" / "    extra_query={\"model\": \"gpt-4o-litellm\"}  # List litellm batches"
- **Our assessment**: A small but real documentation inconsistency on the same
  page: two `list` calls, two different homes for `model`, unexplained. It does
  not oppose any existing note's claim (the containers note documents its own
  `extra_query`-for-list rule), so it is recorded as a page-level inconsistency,
  not a corpus contradiction — no contradiction issue filed.

### Claim 11: The page documents no error/status-code catalogue, no rate limits or quotas, no retry/timeout semantics, no file-size caps, no retention/lifecycle policy, no storage-backend description, and no metrics/logging/tracing hooks; its only deeper surface is a Swagger reference link
- **Evidence**: Exhaustive read of the page — the only outbound pointers are the
  five provider links, the `related` links to `/docs/bedrock_converse` and the
  managed-files beta, and the Swagger line; no section, table, or example
  carries enforcement, lifecycle, or observability content.
- **Confidence**: settled (absence verified against the full page text)
- **Quote**: (no direct quote; the page's only deeper reference is its closing line "[Swagger API Reference](https://docs.litellm.ai/api-reference/#/files)" — see paraphrase in Our assessment)
- **Our assessment**: Recorded as an explicit absence per the Prospector so the
  guide infers no enforcement or lifecycle for this surface. The contrast with
  the sibling pages is the point: the batches page documents size caps +
  validation + rate-limit accounting, the container-files page documents a
  pagination bound and a DELETE-only removal story; this page attaches **none**
  of that to the provider `/files` surface. Whatever governs these files
  (retention, quotas, storage) is undocumented here.

## Concrete Artifacts

All artifacts verbatim from the source page
(`https://docs.litellm.ai/docs/files_endpoints`, fetched 2026-10-15).

### `files_settings` config block (from "LiteLLM PROXY Server" → "1. Setup config.yaml")

```yaml
# for /files endpoints
files_settings:
  - custom_llm_provider: azure
    api_base: https://exampleopenaiendpoint-production.up.railway.app
    api_key: fake-key
    api_version: "2023-03-15-preview"
  - custom_llm_provider: openai
    api_key: os.environ/OPENAI_API_KEY
```

### `model_list` multi-account setup (from "Multi-Account Support" → "Setup")

```yaml
model_list:
  # litellm OpenAI Account
  - model_name: "gpt-4o-litellm"
    litellm_params:
      model: openai/gpt-5.6-terra
      api_key: os.environ/OPENAI_LITELLM_API_KEY

  # Free OpenAI Account
  - model_name: "gpt-4o-free"
    litellm_params:
      model: openai/gpt-5.6-terra
      api_key: os.environ/OPENAI_FREE_API_KEY
```

### Encoded-ID example (from "How Encoded IDs Work")

```text
The encoded ID is base64-encoded and looks like: file-bGl0ZWxsbTpmaWxlLWFiYzEyMzttb2RlbCxncHQtNG8taWZvb2Q
```

Decodes to `litellm:file-abc123;model,gpt-4o-ifood` (LiteLLM's own comment in the
Usage Example names the encoded ID `file-bGl0ZWxsbTpmaWxlLWFiYzEyMzttb2RlbCxncHQtNG8taWZvb2Q`).

### SDK helper set (from the "SDK" tab)

```python
# Upload a File
file_obj = await litellm.acreate_file(
    file=open("mydata.jsonl", "rb"),
    purpose="fine-tune",
    custom_llm_provider="openai",
)

# List Files
files = await litellm.afile_list(
    custom_llm_provider="openai",
    limit=10
)

# Retrieve File Information
file = await litellm.afile_retrieve(
    file_id="file-abc123",
    custom_llm_provider="openai"
)

# Delete File
response = await litellm.afile_delete(
    file_id="file-abc123",
    custom_llm_provider="openai"
)

# Get File Content
content = await litellm.afile_content(
    file_id="file-abc123",
    custom_llm_provider="openai"
)
```

### Bedrock content retrieval by S3 URI (from the "SDK" tab)

```python
# For Bedrock batch output files stored in S3
content = await litellm.afile_content(
    file_id="s3://bucket-name/path/to/file.jsonl",  # S3 URI or unified file ID
    custom_llm_provider="bedrock",
    aws_region_name="us-west-2"
)
print("file content=", content.text)
```

### Proxy upload example and the `purpose` values in use (from the "LiteLLM PROXY Server" tab and Usage Example)

```python
client.files.create(
    file=wav_data,
    purpose="user_data",
    extra_headers={"custom-llm-provider": "openai"}
)
```

`purpose` values appearing on the page: `"user_data"` (proxy upload),
`"fine-tune"` (SDK upload), `"batch"` (multi-account Usage Example).

### Provider list (from "**Supported Providers**")

```text
OpenAI | Azure OpenAI | Vertex AI | Bedrock | Anthropic
```

### Anthropic note (from the provider section, verbatim)

> Anthropic Files API has a different purpose than OpenAI's. Rather than serving
> Batches or Fine-tuning, it lets you upload a file once and reference it by
> `file_id` in multiple messages, avoiding re-uploads. File API operations are
> free; file content used in Messages requests is priced as input tokens.

## Cross-References

All citations below were verified by re-reading the cited note and locating the
`### Claim:` heading in document order, per `agents/MINER.md` §4b. Every
candidate path in `miner-related-notes.md` is cited or explicitly dismissed.

- **Corroborates**:
  - `source-notes/docs-litellm-batches-api.md` **Claim 10** — the strong
    overlap the Prospector flagged. That claim already documents the base64
    `litellm:<id>;model,<name>` encoding, the preserved `file-…`/`batch_…`
    prefixes, the three-tier priority (encoded ID > `model` parameter >
    `custom_llm_provider` fallback), and the "IDs remember which account created
    them" property. This page restates the *same mechanism* and is deliberately
    **not** re-extracted as a new claim (Claim 3 here is a corroboration with
    the file-side worked example). This page does not state the three-tier
    priority — that stays sourced to the batches note.
  - `source-notes/docs-litellm-containers-api.md` **Claim 6** (provider
    selection is a documented multi-transport override: header, then query,
    then body). This page's Claim 4 documents the same three transports for the
    `model` parameter on `/files`; together they establish that LiteLLM's
    OpenAI-shape endpoints accept routing inputs in body, query, and header.
  - `source-notes/docs-litellm-knowledgebase-vector-stores.md` **Claim 8** (the
    client's `file_search` tool is consumed by the gateway; "provider file
    objects are fronted by gateway routes"). This page is the provider-level
    instance of that shape: the client talks only to the proxy's `/files`
    routes while the bytes live in OpenAI/Azure/Vertex/Bedrock/Anthropic
    storage, and the gateway holds the provider credential.

- **Contradicts**: None. The apparent tension with
  `docs-litellm-container-files-api.md` — this page documents model-embedded
  file IDs while that note documents *deployment-encoded* container IDs
  (its Claim 5) — is not a contradiction: the two are **different surfaces**
  (provider-level `/files` objects vs. files inside code-interpreter
  containers), and the Prospector explicitly frames them as two unrelated
  identity-encoding mechanisms to be kept separate. The files-vs-container-files
  distinction is a conditioning variable (route + object lifecycle), not opposed
  claims. No contradiction issue filed; verified against `CONTRADICTIONS.md` and
  the open `contradiction`-labeled issues.

- **Extends**:
  - `source-notes/docs-litellm-batches-api.md` **Claim 7** (batch input-file
    validation: `POST /v1/files` with `purpose="batch"` gets the `.jsonl` /
    JSON-object / `custom_id` checks). The batches page covers only the
    `purpose="batch"` slice of `POST /v1/files`; this page supplies the general
    `/files` CRUD surface (`user_data`, `fine-tune`, and the other four
    operations) that the batches note's scope leaves out.
  - `source-notes/docs-litellm-container-files-api.md` **Claim 7** (the only
    documented removal for container artifacts is explicit DELETE; no retention
    policy, GC, or error codes). This page is a **second** file surface in the
    corpus with the same documentation gap (Claim 11 here): provider-level
    files are documented with no retention, quota, or lifecycle either. Two
    file-bearing gateway surfaces, one shared absence.
  - `source-notes/docs-litellm-containers-api.md` **Claim 7** (`model_list`
    credentials: create names the deployment in the body, list in the query,
    because list is a GET). This page's Claim 10 shows the same
    build-the-deployment-input-into-the-right-place pattern for `/files`
    (`extra_body` on `files.list`, `extra_query` on `batches.list`), with no
    reconciliation — an extension of the corpus's "which verb takes the routing
    input where" concern.
  - `source-notes/docs-litellm-a2a-cost-tracking.md` **Claim 8** (no
    reconciliation between the two A2A cost mechanisms). Read to check the
    Anthropic file-cost rule against it as the Prospector instructed: the A2A
    note covers per-agent synthetic charges, not provider file billing, and
    states no file-cost rule — so the Anthropic statement (Claim 8 here) is
    novel, not a repeat. Cited only to record that the cross-check was done.

- **Novel**: First source note in the corpus covering:
  - The **provider-level `/files` passthrough surface** itself — the five
    OpenAI-format operations in proxy and SDK form (Claim 1), distinct from both
    the batch-input-file and container-files surfaces.
  - The **`files_settings` credential config block and its `model_list`
    migration path** (Claim 5) — `custom_llm_provider`/`api_base`/`api_key`/
    `api_version` vs. `model_name`-keyed `model_list` entries.
  - The **Anthropic file-cost rule** — Files API operations are free, file
    content in Messages is priced as input tokens (Claim 8) — the corpus's only
    file-cost attribution statement.
  - The **Bedrock S3-URI content-retrieval form** (`file_id="s3://…"` +
    `aws_region_name`, returning `content.text`, Claim 6).
  - The **three-way `model`-transport for `/files`** (`extra_body` / `?model=` /
    `x-litellm-model`, Claim 4) and the documented absences (Claim 11).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — gateway surface area, config):** Add the
  provider-level `/files` surface as a distinct file path alongside the batch
  and container-files paths the guide already tracks. Two specifics: (1) the
  credential-config migration — teach `files_settings` (per-`custom_llm_provider`
  `api_base`/`api_key`/`api_version`) as the legacy `/files` credential store
  and `model_list` as the recommended replacement, noting the old path is *still
  live* and requires a `custom-llm-provider` header per call (Claim 5), so a
  rollout can leave two credential paths active; (2) the SDK helpers are
  async-only and need `custom_llm_provider` per call (Claim 9), and the page
  documents **no** timeouts, retries, or rate limits for this surface (Claim 11)
  — do not assume gateway quota enforcement covers file operations.
- **Chapter 06 (Security and Trust — data governance / gateway credential
  routing):** Two items. (a) Files staged through `/files` are *operator-
  uploaded* bytes sitting in provider-side storage for Assistants, fine-tuning,
  and batch (Claim 2), with no documented retention or lifecycle (Claim 11) —
  the operator-uploaded counterpart to the container-files note's model-generated
  artifacts. (b) Bedrock content retrieval reads by **customer S3 URI** with a
  caller-specified `aws_region_name` (Claim 6) — the gateway's file surface
  reaches into operator AWS storage, which belongs next to the Ch06
  "gateway credential routing: declare, don't infer" rule
  (`guide/06-security-and-trust.md:603`): the `files_settings` → `model_list`
  migration (Claim 5) is exactly a "declare the credential once" pattern.
- **Chapter 02 (Observability — cost attribution):** Add the Anthropic
  file-cost rule (Claim 8): Files API operations are free, but file content used
  in Messages requests is priced as input tokens — so per-operation file metrics
  (upload/list/retrieve counts or bytes) **understate** spend, and the cost
  appears on the Message call that consumes the file. Scope it to Anthropic; the
  page gives no cost statement for the other four providers. This pairs with the
  corpus's existing "gateway counters are not a ledger" material from the
  batches note.

## Extraction Notes

- Source read in full on 2026-10-15 via WebFetch on the canonical URL (HTTP 200)
  **and** the page's own markdown form (`/docs/files_endpoints.md`), which is the
  authoritative text for the code blocks here; the two agree. No paywall, no
  truncation.
- Triage bounding honored (#1722, `triaged:text`, `priority:medium`). The
  Prospector's instruction **not to re-extract the routing scheme** is followed:
  Claim 3 records it as corroboration of `docs-litellm-batches-api.md` Claim 10
  (with the file-side worked example) rather than as a new mechanism, and the
  three-tier priority order is left sourced to the batches note because this
  page does not state it.
- All `Quote` fields and Concrete Artifacts are verbatim contiguous fragments
  from the page (markdown form), copied character-for-character; no splicing
  across non-adjacent sentences. Where a claim rests on the Miner's synthesis
  (e.g. the cost-attribution-trap framing in Claim 8, the absence-claim framing
  in Claim 11) it is labeled as such and placed outside `Quote`.
- `confidence_overall` is `settled`, matching the sibling LiteLLM endpoint notes
  (`docs-litellm-batches-api.md`, `docs-litellm-container-files-api.md`): every
  numbered claim is a documented first-party product/schema contract or an
  absence verified against the full page text. The page carries no benchmarks or
  effectiveness claims, and none are inferred.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or explicitly dismissed:
  - `docs-litellm-batches-api.md` — **cited** (Corroborates Claim 10; Extends
    Claim 7).
  - `docs-litellm-completion-web-search.md` — **dismissed**: web-search support
    matrix and per-provider search backends; no file-endpoint content.
  - `docs-litellm-creating-adapters.md` — **dismissed**: format-translation
    adapters; no file surface.
  - `docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock `/invoke`
    passthrough route; different endpoint family (though two Bedrock notes now
    both touch `aws_region_name`, the surfaces do not overlap).
  - `docs-litellm-audio-transcription.md` — **dismissed**: transcription
    fallbacks and `mode:` routing; unrelated.
  - `docs-litellm-completion-input-params.md` — **dismissed**: supported-param
    gate and defaults; no file parameters.
  - `docs-litellm-completion-web-fetch.md` — **dismissed**: Anthropic
    web-fetch tool params; unrelated surface.
  - `docs-litellm-a2a-iteration-budgets.md` — **dismissed**: per-session A2A
    iteration/budget caps; different subsystem.
  - `docs-litellm-bedrock-converse.md` — **dismissed**: Bedrock `/converse`
    passthrough; different endpoint family.
  - `docs-google-sre-eliminating-toil.md` — **dismissed**: toil
    characterization; unrelated to this API surface.
- Additional cross-references found by searching `source-notes/`:
  `docs-litellm-container-files-api.md` (Corroborates/Extends — Claims 5 and 7),
  `docs-litellm-containers-api.md` (Corroborates Claim 6; Extends Claim 7),
  `docs-litellm-knowledgebase-vector-stores.md` (Corroborates Claim 8),
  `docs-litellm-a2a-cost-tracking.md` (read to check the Anthropic cost rule;
  not overlapping), and `docs-litellm-completion-batching.md` (its Scope
  explicitly excludes the `/v1/files` + `/v1/batches` surface — this note fills
  the file side of that exclusion).
- No contradiction issue filed. The only candidate tension (files IDs vs.
  container IDs) is a different-surface conditioning variable, not an opposed
  claim; the `files_settings`-vs-`model_list` choice is the page's own
  recommendation, not a disagreement between sources. Verified against
  `CONTRADICTIONS.md` and open `contradiction`-labeled issues.
- `date_published` is unknown (living Docusaurus page; the markdown form carries
  `last_updated: 2026-10-14`). `date_extracted` and `last_checked` are both
  2026-10-15 (UTC).
