---
source_url: https://docs.litellm.ai/docs/container_files
source_type: docs
title: "Container Files API | liteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page footer reads "© 2026 LiteLLM")
date_extracted: 2026-10-08
last_checked: 2026-10-08
status: current
confidence_overall: settled
issue: "#1622"
---

# Container Files API — the file-artifact surface of vendor-hosted code-interpreter containers (LiteLLM Docs)

> The gateway's five-route CRUD surface for files inside OpenAI/Azure
> code-interpreter containers — the artifacts (charts, CSVs, images) that
> interpreter runs drop under `/mnt/data/` as an implicit side effect. Two
> things carry operational weight beyond the route table: the container ID
> returned by a routed create **encodes the deployment**, so file calls route
> themselves back to that deployment (deployment-bound state in a
> multi-deployment gateway), and the page documents **only `DELETE` as a
> removal path** — no retention policy, no GC, no error codes, no rate limits —
> for artifacts that often contain customer data.

## Source Context

- **Type**: docs (LiteLLM first-party API reference under "Supported Endpoints >
  /containers/files"; verified HTTP 200 on 2026-10-08). Living/undated — no
  publication or revision date, only a "© 2026 LiteLLM" footer.
- **Author credibility**: BerriAI / LiteLLM, the gateway vendor. Authoritative
  for the surface it defines: route paths, SDK helper names, parameter bounds,
  response-object shapes, provider matrix. It is **capability reference only** —
  no measurements, no failure modes, no error catalogue, no versioning of the
  behaviour against any LiteLLM release. The two feature-table flags (Cost
  Tracking, Logging) are asserted with zero substantiation on the page.
- **Scope**: Covers (1) the five `/v1/containers/{container_id}/files` routes,
  (2) the LiteLLM SDK helpers and the OpenAI-SDK/curl proxy forms for each,
  (3) parameter tables including the pagination bound, (4) three response
  objects, (5) the two-provider support matrix and the Azure routing note.
  Does NOT cover: retention/GC, cleanup on container expiry, error codes, rate
  limits, retry semantics, per-file access control, or any cost/logging detail
  behind the feature-table checkmarks. Per §1 the page was followed into two
  substantive linked pages: the Containers API (`/docs/containers`, container
  lifecycle + the deployment-encoding statement) and the Code Interpreter guide
  (`/docs/guides/code_interpreter`, how `container_id` reaches the client).

## Extracted Claims

### Claim 1: The gateway fronts a five-route file CRUD surface scoped per container — upload, list, metadata, content download, and delete under `/v1/containers/{container_id}/files`
- **Evidence**: The page's "Endpoints" table (five rows, methods POST/GET/GET/
  GET/DELETE) and matching proxy curl examples for every route.
- **Confidence**: settled
- **Quote**: (no direct quote; route table reproduced verbatim in Concrete
  Artifacts — see the Endpoints table below)
- **Our assessment**: This is the whole surface, and it is deliberately narrow:
  file operations are keyed on `container_id` + `file_id` only, with no
  container-level operations on this page (create/list/delete container live on
  the sibling Containers page). For an operator the significance is that the
  gateway exposes *provider-side* container storage as an OpenAI-compatible
  API — the artifacts are not gateway-local bytes, they are proxied through to
  OpenAI/Azure.

### Claim 2: Container files are created implicitly as code-interpreter output, not by operator upload — the artifact channel starts empty and fills as a side effect of model runs
- **Evidence**: The page's opening sentence under the H1.
- **Confidence**: settled
- **Quote**: "Manage files within Code Interpreter containers. Files are created automatically when code interpreter generates outputs (charts, CSVs, images, etc)."
- **Our assessment**: The data-governance framing falls out of this sentence:
  the files in scope are *model-generated*, frequently derived from whatever
  customer data the prompt carried, and they appear in provider-side storage
  without any operator action. "Created automatically" plus "delete only via
  explicit DELETE" (Claim 7) is the accumulation pattern the guide should
  record: nothing in the documented flow removes them.

### Claim 3: The upload route exists because `/chat/completions` and `/responses` restrict container input files to PDF — this route is the documented path for CSV, Excel, and Python scripts
- **Evidence**: The Upload Container File SDK section's rationale sentence,
  plus the "Supported file formats" list (CSV, Excel, Python scripts, JSON,
  Markdown, text, "And more...").
- **Confidence**: settled
- **Quote**: "This is useful when `/chat/completions` or `/responses` sends files to the container but the input file type is limited to PDF. This endpoint lets you work with other file types like CSV, Excel, Python scripts, etc."
- **Our assessment**: A concrete endpoint-design constraint: the chat and
  responses request paths cannot stage arbitrary input files into the
  container, so any pipeline that needs the interpreter to read a CSV has to
  make a separate authenticated upload call first, hold the returned
  `container_id`, and sequence the two calls. That is an extra round trip and
  an extra credential surface for what is conceptually one workflow — worth
  naming in any runbook that stages data for interpreter runs.

### Claim 4: Provider support is exactly `openai` and `azure` — the vendor-hosted path, with no file-management counterpart for operator-controlled sandboxes
- **Evidence**: The "Supported Providers" matrix (two rows) and the
  "Supported Providers" line in the feature table.
- **Confidence**: settled
- **Quote**: (no direct quote; two-row support matrix — `OpenAI` "✅ Supported",
  `Azure OpenAI` "✅ Supported" — reproduced in Concrete Artifacts)
- **Our assessment**: The scoping caveat that matters most for Ch06. This API
  manages files in *OpenAI's and Azure's* containers; the gateway's own
  sandbox-interception path (E2B/OpenSandbox, per
  `blog-litellm-swap-openai-code-interpreter.md`) has no file-artifact surface
  documented here at all. So a deployment that follows the guide's rule to
  route code execution through operator-controlled sandboxes does **not** get a
  built-in artifact-handling story from this page — the two features sit on
  disjoint provider sets, and a reader skimming "Cost Tracking ✅ Logging ✅"
  could easily assume broader parity than exists.

### Claim 5: A container created through the proxy against a specific deployment returns an ID whose file calls route back to that deployment — the container ID carries deployment affinity
- **Evidence**: The Azure section's closing sentence, corroborated verbatim by
  the sibling Containers page's `model_list` credential note.
- **Confidence**: settled (both pages state it directly; no implementation
  detail is given on either page)
- **Quote**: "A container created on the proxy with an Azure deployment's `model` returns an ID that routes its file calls to that deployment"
- **Our assessment**: This is the one genuinely operational claim on the page,
  and the Prospector's key question resolves as **real routing constraint, not
  cosmetic ID-embedding** — the sibling Containers page confirms it in routing
  terms: "Retrieve, delete, and container file calls need no `model`: the ID a
  routed create returns encodes the deployment, so they route on their own"
  (`/docs/containers`, `model_list` credentials section). Consequences for a
  multi-deployment gateway: (a) container state is deployment-bound, so a
  container created against deployment A cannot be load-balanced onto
  deployment B — file calls silently follow the ID; (b) with Azure, that
  affinity extends to a *tenant/resource endpoint* (`api_base`), so file bytes
  traverse to whichever Azure resource minted the container regardless of which
  proxy replica serves the request; (c) deleting or draining the deployment a
  container is bound to orphans its files with no documented migration or
  error. Nothing on either page documents what happens on the mismatch — the
  affinity is asserted as working, never as failing.

### Claim 6: List pagination is a bounded cursor contract — `limit` 1–100 defaulting to 20, with `after` and `order`
- **Evidence**: The List Files parameter table row for `limit`.
- **Confidence**: settled
- **Quote**: "Items to return (1-100, default: 20)"
- **Our assessment**: The only numeric bound anywhere on the page, and it
  matters because containers accumulate interpreter output unbounded (Claim 2)
  while list returns 20 by default — a script that reads `files.data` once
  silently sees the first page only, despite the response envelope carrying
  `has_more` (Claim 7). The bound is ordinary, but the combination of
  default-20 + no documented lifecycle is what turns "list my artifacts" into a
  pagination bug waiting to happen.

### Claim 7: The only documented removal path is explicit `DELETE`; no retention policy, cleanup/GC, error codes, rate limits, or retry semantics appear anywhere on the page
- **Evidence**: Exhaustive reading of the page — the endpoints table, parameter
  tables, response objects, and provider section contain no retention, TTL,
  lifecycle, error, or rate-limit content. The one lifecycle control on the
  *linked* Containers page is container-level `expires_after` (`anchor`,
  `minutes`), which the Files page never mentions and never says deletes
  contained files.
- **Confidence**: settled (that the documentation is silent — an absence claim,
  verified against the full page text)
- **Quote**: (no direct quote; the page documents no retention policy — see
  paraphrase in Our assessment)
- **Our assessment**: Recorded as an explicit open question, per the
  Prospector's instruction not to invent a policy. The operational picture:
  artifacts containing customer data accumulate under `/mnt/data/` (Claim 2),
  the sole removal is an operator-issued DELETE (the delete route returns
  `{"deleted": true}` with no documented partial-failure semantics), and the
  only hint of any expiry anywhere in the feature area is the *container's*
  `expires_after` on the sibling page — which this page neither references nor
  explains. Whether container expiry purges files, whether files outlive
  expired containers, and what a DELETE against a provider-side container that
  has already expired returns are all unanswerable from the documentation. For
  a data-perimeter feature this is the gap worth putting in front of the
  Assayer: the guide can state the absence, not the behavior.

### Claim 8: The feature table asserts Cost Tracking ✅ and Logging ✅ with no substantiation anywhere on the page
- **Evidence**: The feature table's two checkmark rows; no cost, spend, log, or
  callback detail appears in any section, example, or parameter table.
- **Confidence**: settled (that the flags are asserted; the underlying
  capability is unverified)
- **Quote**: (no direct quote; feature-table cells "Cost Tracking ✅" and
  "Logging ✅" — see Concrete Artifacts)
- **Our assessment**: Extracted precisely so it is *not* treated as settled,
  per the Prospector. This is the same vendor support-matrix pattern other
  LiteLLM endpoint pages carry: a checkmark with no per-provider breakdown, no
  log field list, no cost attribution example. Do not let Ch02 cite this page
  for a cost or logging claim — there is nothing here to cite beyond the glyph.

### Claim 9: Every artifact object carries its container-relative path and a `source` marker identifying code-interpreter provenance
- **Evidence**: The `ContainerFileObject` response example.
- **Confidence**: settled
- **Quote**: (no direct quote; JSON reproduced verbatim in Concrete Artifacts)
- **Our assessment**: Two fields are worth more than their listing suggests.
  `path: "/mnt/data/chart.png"` fixes the in-container location convention —
  the same mount the interpreter's own code writes to, so operator uploads and
  model outputs land in one namespace with no separation. `source:
  "code_interpreter"` is a provenance tag distinguishing interpreter-produced
  files from operator uploads; an audit or egress-control workflow can filter
  on it, though the page documents no such workflow. Neither field appears in
  any other corpus note — this is the first record of the gateway surfacing
  in-container artifact provenance.

## Concrete Artifacts

All artifacts are extracted verbatim from the source page (whitespace
reconstructed from the rendered tables/code blocks; no words added or removed).

### Endpoints table (page, "Endpoints")

| Endpoint | Method | Description |
|---|---|---|
| `/v1/containers/{container_id}/files` | POST | Upload file to container |
| `/v1/containers/{container_id}/files` | GET | List files in container |
| `/v1/containers/{container_id}/files/{file_id}` | GET | Get file metadata |
| `/v1/containers/{container_id}/files/{file_id}/content` | GET | Download file content |
| `/v1/containers/{container_id}/files/{file_id}` | DELETE | Delete file |

### Feature table (page, top)

| Feature | Supported |
|---|---|
| Cost Tracking | ✅ |
| Logging | ✅ |
| Supported Providers | `openai`, `azure` |

### ContainerFileObject (page, "Response Objects")

```json
{
  "id": "cfile_456...",
  "object": "container.file",
  "container_id": "cntr_123...",
  "bytes": 12345,
  "created_at": 1234567890,
  "filename": "chart.png",
  "path": "/mnt/data/chart.png",
  "source": "code_interpreter"
}
```

### ContainerFileListResponse and DeleteContainerFileResponse (page, "Response Objects")

```json
{
  "object": "list",
  "data": [...],
  "first_id": "cfile_456...",
  "last_id": "cfile_789...",
  "has_more": false
}
```

```json
{
  "id": "cfile_456...",
  "object": "container.file.deleted",
  "deleted": true
}
```

### Upload via proxy, curl (page, "Upload File" tab)

```bash
curl "http://localhost:4000/v1/containers/cntr_123.../files" \
    -H "Authorization: Bearer $LITELLM_API_KEY" \
    -F file="@data.csv"
```

### Upload via LiteLLM SDK — the PDF-limit rationale and supported formats (page, "Upload Container File")

```python
from litellm import upload_container_file

# Upload a CSV file
file = upload_container_file(
    container_id="cntr_123...",
    file=("data.csv", open("data.csv", "rb").read(), "text/csv"),
    custom_llm_provider="openai")

print(f"Uploaded: {file.id}")
print(f"Path: {file.path}")
```

Supported file formats as listed: CSV (`.csv`), Excel (`.xlsx`), Python scripts
(`.py`), JSON (`.json`), Markdown (`.md`), text files (`.txt`), "And more...".
Note that every SDK helper takes `custom_llm_provider` as an explicit argument —
the provider is a client-side routing input on the SDK path, while on the proxy
path it rides in a `custom-llm-provider` header or (per Claim 5) is inferred
from the container ID.

### Azure / provider section (page, "Supported Providers") — verbatim

> For Azure, pass `custom_llm_provider="azure"` with `api_base` and `api_key`
> in the SDK, or send `custom-llm-provider: azure` to the proxy. A container
> created on the proxy with an Azure deployment's `model` returns an ID that
> routes its file calls to that deployment

### Corroborating routing statement — sibling page `/docs/containers` (linked from this page, fetched 2026-10-08)

> The OpenAI key can also live in `model_list` instead of the environment. Pass
> that deployment's `model` in the create body or as a `model` query param on
> list, and the proxy calls OpenAI with the deployment's `api_key` and
> `api_base`. Retrieve, delete, and container file calls need no `model`: the
> ID a routed create returns encodes the deployment, so they route on their own

### Artifact retrieval workflow — linked Code Interpreter guide (`/docs/guides/code_interpreter`, fetched 2026-10-08)

```python
# 1. Run code interpreter
response = client.responses.create(
    model="openai/gpt-5.6-terra",
    tools=[{"type": "code_interpreter"}],
    input="Create a scatter plot and save as PNG")
# 2. Get container_id from response
container_id = response.output[0].container_id
# 3. List files
files = client.containers.files.list(container_id=container_id)
```

The guide shows `container_id` arriving on `response.output[0]` — i.e. the
affinity-bearing ID (Claim 5) is handed to the client by the completion itself,
which is why file calls can proceed with no `model` parameter.

## Cross-References

All citations below were verified by re-reading the cited note and locating the
`### Claim:` heading in document order, per `agents/MINER.md` §4b. Every
candidate path in `miner-related-notes.md` is either cited or explicitly
dismissed in Extraction Notes.

- **Corroborates**:
  - `blog-litellm-swap-openai-code-interpreter.md` **Claim 1** ("The OpenAI
    Responses and Chat Completions APIs let you declare a `code_interpreter`
    tool and the model runs Python inside an OpenAI-hosted container. That
    container is opaque, billed by OpenAI, and the code (often customer data)
    leaves your perimeter."). That note establishes *why* vendor-hosted
    interpreter containers are a perimeter problem; this page is the concrete
    inventory of what accumulates inside one — `path: "/mnt/data/chart.png"`
    artifacts with `source: "code_interpreter"` (Claim 9), created
    automatically (Claim 2) and removable only by explicit DELETE (Claim 7).
    Together they make the data-governance case: opaque vendor storage that
    fills itself and never empties itself.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` **Claim 2** (capabilities
    split into read vs. world-modifying write, "you must know exactly what you
    hand the agent because when/how a capability gets called is hard to
    predict") and **Claim 3** (writes run in a sandbox). This page is the
    artifact half of that sandbox principle: the guide can cite Claim 3 for
    *where* code runs and this page for *what it leaves behind* — the write
    guardrail is incomplete if the sandbox's output store has no documented
    lifecycle (Claim 7).
  - `docs-litellm-knowledgebase-vector-stores.md` **Claim 8** (the client's
    `file_search` tool is consumed by the gateway; provider file objects are
    fronted by gateway routes). This page is the second instance of that shape
    in the corpus: provider-side file objects (`cfile_*`, `file_id`) exposed
    through OpenAI-compatible gateway routes, with the gateway holding the
    provider credential and the client never touching OpenAI's file API
    directly. Same fronting pattern, different subsystem (container artifacts
    vs. retrieval corpora).

- **Contradicts**: None. Verified against `CONTRADICTIONS.md` (no entry touching
  container files), the open `contradiction`-labeled issues (none cover this
  surface), and all existing source notes. The apparent tension with
  `blog-litellm-swap-openai-code-interpreter.md` — that note reroutes execution
  *off* OpenAI's container while this page manages files *inside* it — is a
  conditioning variable (Claim 4's provider scope: `openai`/`azure` only), not
  an opposed claim: the two describe disjoint paths through the same feature
  area, and the interception path simply has no file surface here. No
  contradiction issue filed.

- **Extends**:
  - `blog-litellm-swap-openai-code-interpreter.md` — extends that note's
    sandbox/container context with the **file-management surface** of the
    vendor-hosted path it does not cover: five routes, the object shape, the
    pagination bound, and the deployment-affinity behavior (Claim 5). Two
    notes now bound the feature area from both sides — execution rerouting
    (swap) and artifact handling (this page) — and the gap between them
    (operator sandboxes have no documented file API) is stated in Claim 4.
  - `docs-litellm-batches-api.md` — adjacent only in that both pages document a
    *file-bearing* LiteLLM endpoint family with a bounded list contract. No
    claim-level overlap: per that note's **Claim 1**, batch input files are
    client-uploaded JSONL charged against rate limits at submission; container
    files are model-generated artifacts with no rate-limit story at all
    (Claim 7 here). The corpus's nearest "files behind the gateway" surface;
    nothing more.

- **Novel**: First source note in the corpus covering:
  - The **container-file CRUD surface** itself — five routes under
    `/v1/containers/{container_id}/files`, the SDK helpers, and the three
    response objects (no existing note mentions `container_files`,
    `cfile_`, or `/mnt/data/`).
  - **Deployment-affinity container IDs** (Claim 5) — a container ID that
    encodes its creating deployment and self-routes file calls, i.e.
    deployment-bound state a load balancer cannot distribute. Nothing else in
    the corpus records this class of routing constraint on a gateway artifact
    path.
  - The **PDF-only input limitation** on `/chat/completions` and `/responses`
    container staging and the upload route as the documented workaround
    (Claim 3).
  - The **documented lifecycle gap** (Claim 7): explicit-DELETE-only removal
    for automatically-created, often customer-derived artifacts, with no
    retention/GC/error/rate-limit documentation anywhere on the page.

## Guide Impact

- **Chapter 06 (Security and Trust / data governance for AI workloads)**: Add a
  subsection on **interpreter artifact retention**. The rule this source
  supports: when code-interpreter containers are enabled through the gateway,
  know that files are created automatically from model runs (Claim 2), live at
  provider side under `/mnt/data/` with operator uploads in the same namespace
  (Claim 9), and the *only* documented removal is an explicit per-file DELETE
  (Claim 7) — so artifact cleanup must be an explicit operational job (list →
  paginate → delete), because nothing in the documented flow does it for you.
  State the absence plainly: no retention policy, no GC, no error codes are
  documented. Also record the provider scope (Claim 4): this artifact-handling
  story exists only for the vendor-hosted (`openai`/`azure`) path, so the
  chapter's "route code execution through operator-controlled sandboxes" rule
  does **not** come with a built-in file-management counterpart — an operator
  sandbox needs its own artifact inventory and purge story.

- **Chapter 05 (LLM Ops Reliability — gateway surface area)**: Add
  **deployment-bound container state** as a routing/load-balancing constraint.
  A container ID minted by a routed create self-routes its file calls (and per
  the sibling Containers page, retrieve/delete too) to the creating deployment
  — so container-backed workflows cannot be freely load-balanced across a
  deployment pool, and with Azure the affinity reaches a specific resource
  endpoint (Claim 5). Recommend: treat containers as pinned to the deployment
  that created them (drain/expire before removing that deployment), and do not
  assume a container created on one replica is usable via another. Also carry
  the **list pagination contract** (Claim 6): `limit` defaults to 20 with
  `has_more` in the envelope — artifact-inventory scripts must paginate.

- **Chapter 02 (Observability)**: **Do not import** the page's Cost Tracking ✅
  and Logging ✅ flags (Claim 8). They are unsubstantiated checkmarks; if cost
  or log behavior for this endpoint family matters, it needs a source that
  actually documents field-level detail. Noted explicitly so the flags are not
  picked up downstream as evidence.

- **Explicitly do not import**: any inference about what happens to files when
  a container expires (Claim 7's open question), and any reliability claim —
  the page states no error codes, no rate limits, no retry semantics.

## Extraction Notes

- Source read in full on 2026-10-08 via direct HTTP fetch (Docusaurus page,
  HTTP 200, no paywall, no truncation). Per §1, two substantive linked pages
  were followed: `/docs/containers` (container lifecycle, `expires_after`,
  and the deployment-encoding routing statement used in Claim 5) and
  `/docs/guides/code_interpreter` (how `container_id` reaches the client on
  `response.output[0]`, and the gateway file-retrieval workflow). Both are
  cited in Concrete Artifacts; no other linked page carried operational
  content.
- **Sibling issue #1623** (`docs containers`) covers the *container lifecycle*
  page, which was read here only for the two statements quoted above
  (deployment encoding, `expires_after`). If that issue is mined
  independently, the overlap is exactly those two artifacts — noted, not
  duplicated: no container-lifecycle claim is extracted as a numbered claim in
  this note.
- The Prospector's key question is answered in Claim 5: the Azure
  deployment-affinity sentence is a **real routing constraint** (file calls
  self-route to the creating deployment), not merely ID-embedding cosmetics —
  corroborated by the sibling page's "the ID a routed create returns encodes
  the deployment, so they route on their own". Whether it *fails* usefully on
  mismatch is undocumented; that sub-question stays open inside Claim 5.
- The apparent conflict with the swap/interception pattern was evaluated for
  §4a and dismissed as a conditioning variable, not a contradiction: the
  container-files surface is scoped to `openai`/`azure` (Claim 4), while the
  intercepted path executes in E2B/OpenSandbox where this API does not apply.
  Both statements can be true simultaneously and would not lead to different
  guide advice. No contradiction issue filed; verified against
  `CONTRADICTIONS.md` and open `contradiction` issues.
- `confidence_overall: settled` — every numbered claim is descriptive of a
  first-party API contract (routes, bounds, object shapes, support matrix) or
  an absence verified against the full page text. The unverified items (the
  two feature-table checkmarks, expiry behavior) are quarantined in Claims 7
  and 8 as gaps rather than relied on. Unlike the knowledge-base note, no
  claim here rests on reading `main`.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are either cited above or explicitly dismissed here:
  - `docs-litellm-batches-api.md` — cited under Extends (nearest
    file-bearing endpoint family; no claim overlap).
  - `docs-litellm-completion-web-search.md` — provider support matrix for web
    search; different feature, no shared claim. Dismissed.
  - `docs-litellm-bedrock-invoke.md` — Bedrock passthrough route and its
    support matrix; different endpoint family. Dismissed.
  - `docs-litellm-audio-transcription.md` — transcription fallbacks and
    `mode:` routing; unrelated. Dismissed.
  - `docs-litellm-completion-input-params.md` — param gating and defaults;
    no container-file parameter overlap. Dismissed.
  - `docs-litellm-completion-web-fetch.md` — Anthropic web-fetch tool params;
    unrelated. Dismissed.
  - `docs-litellm-a2a-iteration-budgets.md` — per-session A2A caps; different
    subsystem. Dismissed.
  - `docs-google-sre-eliminating-toil.md` — toil taxonomy; unrelated to this
    API surface. Dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — cited under Corroborates
    (Claims 2 and 3: write side-effects and sandboxed writes).
  - `docs-litellm-anthropic-advisor-tool.md` — advisor sub-inference usage
    accounting; no shared claim. Dismissed.
- Triage-flagged notes addressed: `blog-litellm-swap-openai-code-interpreter.md`
  (cited — Corroborates + Extends, not restated), `docs-litellm-knowledgebase-vector-stores.md`
  (cited — Corroborates Claim 8), `docs-litellm-a2a-cost-tracking.md` and
  `docs-litellm-cost-map-and-response-cost.md` (the Cost Tracking flag was
  examined and deliberately not extracted as a claim — see Claim 8; the
  cost-map note was not engaged because there is no cost assertion here to
  check against it).
- The page's feature table also differs from the sibling Containers page
  (which adds Load Balancing, Proxy Server Support, and Spend Management rows
  not present here) — recorded as an observation only; it changes no claim.
