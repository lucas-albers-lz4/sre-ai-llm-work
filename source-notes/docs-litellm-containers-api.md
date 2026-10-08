---
source_url: https://docs.litellm.ai/docs/containers
source_type: docs
title: "/containers — LiteLLM AI Gateway Documentation (code-interpreter container sessions)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page footer reads "© 2026 LiteLLM")
date_extracted: 2026-10-08
last_checked: 2026-10-08
status: current
confidence_overall: settled
issue: "#1623"
---

# /containers — container session lifecycle (LiteLLM Docs)

> The gateway's four-call CRUD surface for *vendor-hosted* code-interpreter
> container sessions — the native path that the guide's sandbox-interception
> rule bypasses. Two things carry operational weight: `expires_after{anchor,
> minutes}` is the **only** retention bound the page exposes over uploaded
> `file_ids` (create-time, per-request, no update path), and the container ID
> returned by a routed create **encodes the deployment**, so retrieve/delete
> self-route — container state is pinned, not load-balanced, in a page whose
> own feature table claims Load Balancing ✅. What the page never says is what
> happens on expiry: no status enum, no error codes, no retries, no GC.

## Source Context

- **Type**: docs (LiteLLM first-party API reference under "Supported Endpoints >
  /containers"; verified HTTP 200 on 2026-10-08). Living/undated — no
  publication or revision date, only a "© 2026 LiteLLM" footer.
- **Author credibility**: BerriAI / LiteLLM, the gateway vendor. Authoritative
  for the surface it defines: route paths, SDK helper names, parameter bounds,
  response-object shapes, provider matrix, routing precedence. It is
  **capability reference only** — no measurements, no failure modes, no error
  catalogue, no version pin. The six-row feature table (Cost Tracking, Logging,
  Load Balancing, Proxy Server Support, Spend Management, Supported Providers)
  is asserted with zero substantiation in the body.
- **Scope**: Covers (1) the two `/v1/containers` routes and their four
  operations, (2) the LiteLLM SDK, curl, and OpenAI-client forms of each,
  (3) create/list parameter tables including `expires_after` and the pagination
  bound, (4) three response objects, (5) provider selection precedence and the
  `model_list` credential path, (6) the two-provider support matrix and the
  Azure wire shape. Does NOT cover: expiry behavior, status values, retention
  or GC of the container and its `file_ids`, error codes, rate limits, retries,
  timeouts, concurrency, multi-replica behavior, or any configuration example
  behind the feature-table checkmarks. **Scope caveat (Prospector)**: despite
  the `/containers` slug this is *not* Docker/OCI content — the only
  "deployment" on the page is a single local `litellm` process on
  `http://0.0.0.0:4000`; no image, scaling, health-check, resource-limit, or
  metric content exists here, and none is extracted.

## Extracted Claims

### Claim 1: The gateway fronts a two-route, four-operation container lifecycle — create and list on `/v1/containers`, retrieve and delete on `/v1/containers/{container_id}`
- **Evidence**: The proxy section's endpoint list, a curl example for each of
  the four operations, the OpenAI-client equivalents (`client.containers.create`
  / `.list` / `.retrieve` / `.delete`), and the eight sync/async SDK helpers
  (`create_container` / `acreate_container`, `list_containers` /
  `alist_containers`, `retrieve_container` / `aretrieve_container`,
  `delete_container` / `adelete_container`).
- **Confidence**: settled
- **Quote**: "LiteLLM provides OpenAI API compatible container endpoints for managing code interpreter sessions:" / "- `/v1/containers` - Create and list containers" / "- `/v1/containers/{container_id}` - Retrieve and delete containers"
- **Our assessment**: The whole lifecycle is four calls, and every operation is
  documented in three transport forms (SDK, curl against the proxy, OpenAI SDK
  against the proxy), which is what makes this an OpenAI-compatible surface
  rather than a LiteLLM extension. The operational significance is what is
  *absent* from the set: there is no update/PATCH route anywhere on the page,
  so a container's name, `expires_after`, and `file_ids` are fixed at create
  (see Claim 3), and the only removal path is an operator-issued DELETE (Claim
  11).

### Claim 2: `expires_after{anchor, minutes}` is the only documented retention control — create-time, per-request, and every worked example anchors on `last_active_at` with 20 minutes
- **Evidence**: The Create Container parameter table (three rows:
  `expires_after`, `expires_after.anchor`, `expires_after.minutes`, all
  `Required: No`), and all six create examples on the page (SDK sync, SDK async,
  curl, OpenAI client, complete workflow, both with the same object).
- **Confidence**: settled for the documented field semantics; the idle-vs-
  lifetime reading in the assessment is our inference from the two field names,
  explicitly flagged as such
- **Quote**: "Container expiration settings" / "Anchor point for expiration (e.g., \"last_active_at\")" / "Minutes until expiration from anchor"
- **Our assessment**: The TTL is measured *from an anchor*, and the only anchor
  value the page ever shows is `last_active_at` — so on the documented example
  the knob behaves as an **idle timeout** (expiry = last activity + 20 min),
  not an absolute lifetime cap. That distinction matters for the Ch06
  data-retention angle: a container that keeps being used keeps pushing its
  expiry forward, so `expires_after` bounds *idle* accumulation, not total
  session age. The page never enumerates the allowed `anchor` values, never
  states whether activity recomputes `expires_at`, and documents no
  absolute-lifetime option — so an operator who wants "this session dies 24h
  after creation no matter what" has no documented way to express it. Recorded
  as our reading of the field pair, not as vendor-stated behavior.

### Claim 3: Expiry is fixed at create — no update route, no documented default TTL, and no documented way to extend or re-bind a live container's expiration
- **Evidence**: Exhaustive reading — the endpoint list exposes only
  create/list/retrieve/delete; the parameter tables mark `expires_after`
  optional with no default; no `PUT`/`PATCH` example, no "update container"
  section, and no global `general_settings` TTL appear anywhere on the page.
- **Confidence**: settled (absence claim, verified against the full page text)
- **Quote**: (no direct quote; the page documents no update path — see
  paraphrase in Our assessment)
- **Our assessment**: TTL is a per-request create-time decision with exactly
  two subsequent levers: read `expires_at` (retrieve) or destroy the container
  (delete). A long-running workflow that needs to keep a session alive has no
  documented "touch" operation — the only renewal primitive implied is create
  again with fresh `file_ids`. Combined with Claim 2's missing absolute cap,
  the retention story is: bound it once, at creation, or clean up manually
  afterwards.

### Claim 4: The response objects expose `created_at`, `last_active_at`, `expires_at`, and `status` — but the page documents no status values and no expiry behavior at all
- **Evidence**: The `ContainerObject` example (`status: "active"`, plus both
  timestamps) and the `ContainerListResponse` (`status: "active"`). A full-text
  scan of the page returns **zero** occurrences of `error`, `retry`,
  `timeout`, or `429`; `status` appears only inside example prints and the two
  JSON objects; `rate limit` appears only inside the Spend Management
  feature-table cell.
- **Confidence**: settled for the field presence and for the documentation
  silence; the underlying runtime behavior is unverifiable from this source
- **Quote**: (no direct quote; the fields are reproduced verbatim in Concrete
  Artifacts — the page states no status enum and no expiry semantics)
- **Our assessment**: This is the answer to the Prospector's cleanup question,
  and the answer is a *gap*, not a behavior. The three timestamps are exactly
  what a reaper needs to act (list → read `expires_at` → delete), so the data
  for operational cleanup is present — but the page says nothing about what
  happens when a container crosses `expires_at`: whether `status` changes,
  whether retrieve then fails and with what code, and above all whether the
  container's `file_ids` are purged or orphaned. Per the Prospector's
  instruction, none of that is inferred here. The guide can state the absence;
  it must not state a policy.

### Claim 5: Retrieve, delete, and container-file calls need no `model` because the ID a routed create returns encodes the deployment — container state is deployment-bound
- **Evidence**: The `model_list` credentials paragraph under "LiteLLM Proxy
  Usage"; independently quoted by the sibling `docs-litellm-container-files-api.md`
  note (Claim 5) from this same page.
- **Confidence**: settled (both pages state it directly; no implementation
  detail is given on either page)
- **Quote**: "Retrieve, delete, and container file calls need no `model`: the ID a routed create returns encodes the deployment, so they route on their own"
- **Our assessment**: A non-obvious routing semantic with three consequences
  for a multi-deployment gateway: (a) container state is pinned to the
  deployment that minted it — it cannot be load-balanced onto a sibling
  deployment on retrieve/delete; (b) the "no `model` needed" convenience is
  *the same fact* as that pin, so a deployment that is drained or deleted
  orphans its containers with no documented error or migration path; (c) the
  same gateway already ships this pattern for batches/files as base64-encoded
  IDs (`docs-litellm-batches-api.md` Claim 10) — routing state carried inside
  an opaque client-held identifier is now a recurring LiteLLM design, and any
  tooling that logs, truncates, or round-trips IDs is carrying routing intent.
  The one place this page's Load Balancing ✅ row cannot be true at face value
  is here (see Claim 10).

### Claim 6: Provider selection for container calls follows a documented four-tier precedence — header, then query param, then request body, then default `openai`
- **Evidence**: The "Custom Provider Specification" section — one prose
  sentence plus a four-item ordered list, with one curl example per tier.
- **Confidence**: settled
- **Quote**: "You can specify the custom LLM provider in multiple ways (priority order):" / "Header: `-H \"custom-llm-provider: openai\"`" / "Query param: `?custom_llm_provider=openai`" / "Request body: `{\"custom_llm_provider\": \"openai\", ...}`" / "Defaults to \"openai\" if not specified"
- **Our assessment**: A per-request provider override on an authenticated
  endpoint, with an explicit order. Two operational notes: (1) the header wins
  over body and query, so a gateway or client that injects
  `custom-llm-provider` at the edge silently overrides what the application
  thought it chose — worth knowing when debugging "why did this container
  create hit the other provider"; (2) the default is `openai`, so an
  unconfigured create against a proxy whose `OPENAI_API_KEY` is unset fails at
  the provider, not at validation. This is the routing knob the Prospector
  flagged for per-team key scoping: an Azure-bound team's traffic can be
  steered per request without touching `config.yaml`.

### Claim 7: With `model_list` credentials, create names the deployment in the body (`model`) and list names it in the query — because list is a GET
- **Evidence**: The `model_list` credentials paragraph, the two `model`-taking
  curl examples, and the OpenAI-client list example's lead-in sentence.
- **Confidence**: settled
- **Quote**: "The OpenAI key can also live in `model_list` instead of the environment. Pass that deployment's `model` in the create body or as a `model` query param on list, and the proxy calls OpenAI with the deployment's `api_key` and `api_base`." / "With `model_list` credentials, name the deployment in `extra_query`, since list is a GET:"
- **Our assessment**: The GET-vs-body asymmetry is a small config trap: the
  same "which deployment" input has two different homes depending on the
  verb, and the OpenAI SDK needs `extra_body` for one and `extra_query` for
  the other — a mismatch produces a request that silently falls back to the
  environment-key path rather than an error (the page documents no failure for
  omitting `model`). What the page does *not* say is what happens when `model`
  is omitted and multiple deployments share a `model_name`: no load-balancing
  statement appears for container creates, despite the feature table's claim
  (Claim 10). Left open, not inferred.

### Claim 8: List pagination is a bounded cursor contract — `limit` 1–100 defaulting to 20, `order` asc/desc defaulting to `desc`, cursor `after`, with `has_more` in the envelope
- **Evidence**: The List Container parameter table (three rows) and the
  `ContainerListResponse` example (`first_id` / `last_id` / `has_more`).
- **Confidence**: settled
- **Quote**: "Number of items to return (1-100, default: 20)" / "Sort order: \"asc\" or \"desc\" (default: \"desc\")" / "Cursor for pagination"
- **Our assessment**: Operational, not trivia: the only way to discover
  orphaned or expiring sessions is `list`, and a script that reads `data` once
  sees the first 20 by default despite `has_more` being in the response. Any
  cleanup job over container sessions must paginate with `after`, and the
  `desc` default means the newest containers are the ones you see first — the
  oldest (most likely stale) ones are the ones a naive script misses.

### Claim 9: Provider support is exactly `openai` and `azure`, and the Azure path is a distinct wire shape — `{api_base}/openai/v1/containers` carrying the `api-key` header
- **Evidence**: The "Supported Providers" matrix (two rows) and the Azure
  section's prose, SDK example, and proxy instructions.
- **Confidence**: settled
- **Quote**: "Requests go to `{api_base}/openai/v1/containers` with the `api-key` header" / "For Azure OpenAI, pass the resource endpoint as `api_base` and the key as `api_key`, or set `AZURE_API_BASE` and `AZURE_API_KEY`" / "On the proxy, send `-H \"custom-llm-provider: azure\"` to use the `AZURE_API_BASE` and `AZURE_API_KEY` environment variables, or pass the `model` of an `azure/` deployment in `model_list` to use that deployment's `api_base` and `api_key`"
- **Our assessment**: The scoping caveat that matters for Ch06: this API
  manages sessions in *OpenAI's and Azure's* infrastructure. The gateway's own
  sandbox-interception path (`blog-litellm-swap-openai-code-interpreter.md`)
  has no counterpart documented here — a deployment that follows the guide's
  rule to execute model code in operator-controlled sandboxes gets no
  container-session lifecycle from this page at all, and a reader skimming the
  five ✅ rows could easily assume broader parity than exists. The Azure form
  also sharpens Claim 5's affinity: with Azure, the encoded deployment carries
  a specific resource endpoint (`api_base`), so container state is bound not
  just to a config entry but to a tenant/resource.

### Claim 10: The feature table asserts five ✅ capabilities — including Load Balancing and Spend Management — with no configuration example, no evidence, and one row that sits in tension with the deployment-encoded-ID rule on the same page
- **Evidence**: The page-top feature table (six rows); a full-text scan finds
  no cost, spend, log, callback, or load-balancing configuration anywhere in
  the body — `rate limit` occurs exactly once, inside the Spend Management
  cell itself.
- **Confidence**: settled that the flags are asserted; the underlying
  capabilities are unverified
- **Quote**: "Load Balancing" / "✅" / "Spend Management" / "✅ Budget tracking and rate limiting" / "Proxy Server Support" / "✅ Full proxy integration with virtual keys"
- **Our assessment**: Extracted precisely so it is *not* treated as settled,
  per the Prospector. Three parts. (1) **Spend Management / Cost Tracking /
  Logging**: bare checkmarks with no key/team scoping example and no statement
  that container creates consume the same budgets as `/v1/chat/completions`
  calls — do not let Ch05 cite this page for spend or rate-limit enforcement;
  there is nothing to cite beyond the glyph. (2) **Proxy Server Support with
  virtual keys**: plausible and structurally consistent with the rest of the
  gateway (every curl example carries `Authorization: Bearer $LITELLM_API_KEY`),
  but still unconfigured on the page. (3) **Load Balancing ✅ vs Claim 5**:
  the same page says container IDs encode their deployment so retrieve/delete
  "route on their own" — i.e. pinned. Evaluated under MINER.md §4a for
  filing: **no contradiction issue filed**, on two grounds — the load-balancing
  side is a bare table cell with no claim strong enough to oppose a concrete
  routing statement ("one side is so weakly supported it doesn't rise to a real
  claim"), and the two are reconcilable as a conditioning variable (create/list
  *could* spread across deployments while retrieve/delete remain pinned; the
  page simply never says). The tension is recorded here for the Assayer and
  Smith rather than resolved.

### Claim 11: Cleanup ownership is entirely the operator's — the page documents no GC, no orphan handling, no session-count bound, and no error/retry/timeout semantics; the only removal is an explicit DELETE
- **Evidence**: Exhaustive read — zero occurrences of `error`, `retry`,
  `timeout`, `429` anywhere on the page; the only `rate limit` string is a
  feature-table cell; the delete curl example and `DeleteContainerResult`
  (`"deleted": true`) are the sole removal affordances; no max-container,
  sweeper, or retention setting appears in any parameter or config block.
- **Confidence**: settled (absence claim, verified against the full page text)
- **Quote**: (no direct quote; the page documents no GC or failure semantics —
  see paraphrase in Our assessment)
- **Our assessment**: The operational contract for container sessions is
  "create it, page through them, delete them yourself." Nothing in the
  documented flow removes a session: expiry is documented only as a field
  (`expires_at`) and a create-time input, with no statement that expiry frees
  the container or its `file_ids` (Claim 4), and there is no sweeper. Pair
  with the sibling Files page's matching finding — artifacts are removable
  only by explicit DELETE — and the two pages together describe a
  vendor-side store that fills itself from model runs and never empties
  itself. For Ch05 this is the same "who cleans up: you" shape as
  `docs-litellm-container-files-api.md` Claim 7, one level up: sessions, not
  just files.

## Concrete Artifacts

All artifacts are extracted verbatim from the source page's rendered HTML
(code blocks' line breaks preserved; no words added or removed).

### Feature table (page, top)

| Feature | Supported |
|---|---|
| Cost Tracking | ✅ |
| Logging | ✅ (Full request/response logging) |
| Load Balancing | ✅ |
| Proxy Server Support | ✅ Full proxy integration with virtual keys |
| Spend Management | ✅ Budget tracking and rate limiting |
| Supported Providers | `openai`, `azure` |

### Proxy endpoint list and setup (page, "LiteLLM Proxy Usage")

> LiteLLM provides OpenAI API compatible container endpoints for managing code
> interpreter sessions:
>
> - `/v1/containers` - Create and list containers
> - `/v1/containers/{container_id}` - Retrieve and delete containers

```
$ export OPENAI_API_KEY="sk-..."

$ litellm

# RUNNING on http://0.0.0.0:4000
```

`model_list` credential form (verbatim):

```yaml
model_list:
  - model_name: gpt-5.6
    litellm_params:
      model: openai/gpt-5.6
      api_key: os.environ/OPENAI_API_KEY_TEAM_A
```

```
$ litellm --config config.yaml
```

### Provider precedence (page, "Custom Provider Specification")

> You can specify the custom LLM provider in multiple ways (priority order):
>
> 1. Header: `-H "custom-llm-provider: openai"`
> 2. Query param: `?custom_llm_provider=openai`
> 3. Request body: `{"custom_llm_provider": "openai", ...}`
> 4. Defaults to "openai" if not specified

### Create a Container — default provider, with `expires_after` (page, "Create a Container")

```bash
# Default provider (openai)
curl -X POST "http://localhost:4000/v1/containers" \
    -H "Authorization: Bearer $LITELLM_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "My Container",
        "expires_after": {
            "anchor": "last_active_at",
            "minutes": 20
        }
    }'
```

### Create with `model_list` credentials / List / Retrieve / Delete (page, proxy section)

```bash
# With model_list credentials: name the deployment
curl -X POST "http://localhost:4000/v1/containers" \
    -H "Authorization: Bearer $LITELLM_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "My Container",
        "model": "gpt-5.6"
    }'
```

```bash
# With model_list credentials: name the deployment
curl "http://localhost:4000/v1/containers?model=gpt-5.6&limit=20&order=desc" \
    -H "Authorization: Bearer $LITELLM_API_KEY"
```

```bash
curl "http://localhost:4000/v1/containers/cntr_123..." \
    -H "Authorization: Bearer $LITELLM_API_KEY"
```

```bash
curl -X DELETE "http://localhost:4000/v1/containers/cntr_123..." \
    -H "Authorization: Bearer $LITELLM_API_KEY"
```

### Create Container parameters (page, parameter table, verbatim rows)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Name of the container |
| `expires_after` | object | No | Container expiration settings |
| `expires_after.anchor` | string | No | Anchor point for expiration (e.g., "last_active_at") |
| `expires_after.minutes` | integer | No | Minutes until expiration from anchor |
| `file_ids` | array | No | List of file IDs to include in the container |
| `custom_llm_provider` | string | No | LLM provider to use (default: "openai") |

### List Container parameters (page, parameter table, verbatim rows)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `after` | string | No | Cursor for pagination |
| `limit` | integer | No | Number of items to return (1-100, default: 20) |
| `order` | string | No | Sort order: "asc" or "desc" (default: "desc") |
| `custom_llm_provider` | string | No | LLM provider to use (default: "openai") |

Retrieve/Delete parameter table adds exactly one row beyond
`custom_llm_provider`: `container_id` (string, Yes) — "ID of the container to
retrieve/delete".

### Response objects (page, "Response Objects")

```json
{
  "id": "cntr_123...",
  "object": "container",
  "created_at": 1234567890,
  "name": "My Container",
  "status": "active",
  "last_active_at": 1234567890,
  "expires_at": 1234569090,
  "file_ids": []
}
```

```json
{
  "object": "list",
  "data": [
    {
      "id": "cntr_123...",
      "object": "container",
      "created_at": 1234567890,
      "name": "My Container",
      "status": "active"
    }
  ],
  "first_id": "cntr_123...",
  "last_id": "cntr_456...",
  "has_more": false
}
```

```json
{
  "id": "cntr_123...",
  "object": "container.deleted",
  "deleted": true
}
```

### Supported Providers (page, "Supported Providers", verbatim table)

| Provider | Support Status | Notes |
|---|---|---|
| OpenAI | ✅ Supported | Full support for all container operations |
| Azure OpenAI | ✅ Supported | Set `custom_llm_provider="azure"`. Requests go to `{api_base}/openai/v1/containers` with the `api-key` header |

Azure SDK create (verbatim):

```python
container = litellm.create_container(
    name="My Code Interpreter Container",
    custom_llm_provider="azure",
    api_base="https://<your-resource>.openai.azure.com",
    api_key=os.environ["AZURE_API_KEY"],
)
```

## Cross-References

All citations below were verified by re-reading the cited note and locating
the `### Claim:` heading in document order, per `agents/MINER.md` §4b. Every
candidate path in `miner-related-notes.md` is either cited or explicitly
dismissed in Extraction Notes.

- **Corroborates**:
  - `docs-litellm-container-files-api.md` **Claim 5** (deployment-affinity
    container IDs — file calls self-route to the creating deployment). This
    page is the *source* of that note's corroborating quote; it states the rule
    in routing terms first: "Retrieve, delete, and container file calls need no
    `model`: the ID a routed create returns encodes the deployment, so they
    route on their own". **Claim 7** (only documented removal is explicit
    DELETE; no retention/GC/error/rate-limit documentation) — this page
    supplies the one lifecycle control that note says the Files page never
    mentions: `expires_after{anchor, minutes}`, plus the matching session-level
    silence here (Claims 4, 11). **Claim 8** (feature-table checkmarks asserted
    with no substantiation) — same pattern one table over, five rows deep
    (Claim 10 here).
  - `docs-litellm-batches-api.md` **Claim 10** (routing state embedded in
    gateway-minted opaque IDs — `base64("litellm:<id>;model,<name>")`, with
    documented priority: encoded ID > model parameter > `custom_llm_provider`
    fallback). Claim 5 here is the container-lineage twin of that mechanism:
    two LiteLLM endpoint families where an ID silently pins which provider
    account/deployment subsequent calls go to. The batch note records the
    cross-account hazard; this note records the deployment-pin hazard.
  - `docs-litellm-bedrock-invoke.md` **Claim 3** (support matrix claims Cost
    Tracking ✅, Logging ✅, Streaming ✅, Load Balancing ✅ "with no
    per-provider parity and no caching caveat") — the identical bare-checkmark
    genre, now on a third endpoint family. Its **Claim 6** is the useful
    contrast: *that* page at least shows the load-balancing config (two
    deployments, same `model_name`, different `aws_region_name`) while still
    leaving strategy/failure semantics undocumented; this page shows no
    configuration for its Load Balancing ✅ at all (Claim 10).
  - `docs-litellm-audio-transcription.md` **Claim 5** (support matrix of ✅
    rows on a non-`/chat/completions` endpoint) and **Claim 6** (the matrix is
    a recurring per-endpoint contract across the LiteLLM docs, not a one-off) —
    `/containers` is another instance of that genre, which is exactly why the
    rows are recorded as assertions rather than evidence.
  - `docs-litellm-completion-web-search.md` **Claim 15** ("The page documents
    no rate limits, fallbacks, retries, caching, timeouts, auth, or error
    semantics for the search path") — the same documented-silence posture this
    page forces on us (Claims 4, 11): an endpoint reference whose operational
    behavior section simply does not exist, recorded as a negative finding
    rather than filled in from inference.

- **Contradicts**: None filed. Verified against `CONTRADICTIONS.md` (no entry
  touching containers or session lifecycle), the open `contradiction`-labeled
  issues (none cover this surface), and all existing source notes. The one
  internal tension — the Load Balancing ✅ row vs. the deployment-encoded-ID
  rule (Claim 10 vs Claim 5) — was evaluated under MINER.md §4a and **not**
  filed: the checkmark side is a bare table cell too weakly supported to rise
  to a real claim, and the two statements are reconcilable as a conditioning
  variable (create/list may spread across deployments while retrieve/delete are
  pinned; the page never says which). No verdict is picked here.

- **Extends**:
  - `blog-litellm-swap-openai-code-interpreter.md` — extends that note's
    "before" picture with the concrete **native lifecycle** it bypasses: four
    CRUD routes, the TTL field, the routing precedence, and the provider matrix.
    That note's **Claim 1** describes why the OpenAI-hosted container is a
    perimeter problem; this page is the API for operating those containers
    directly when interception is *not* enabled — including the retention lever
    (`expires_after`) that decides how long uploaded `file_ids` sit vendor-side.
    The two notes now bound the feature area from both sides (rerouting vs.
    native sessions), matching the sibling Files note's framing.
  - `docs-litellm-container-files-api.md` — the lifecycle half of that note's
    feature area: it documents file CRUD *inside* a container; this page
    documents creating, enumerating, reading, and destroying the container
    itself, and owns the `expires_after` control its Claim 7 flags as the only
    expiry hint anywhere in the feature area. Per that note's Extraction Notes,
    the overlap is deliberately confined to the shared routing statement, which
    it left to this issue.
  - `docs-litellm-a2a-iteration-budgets.md` **Claim 1** (per-session
    `max_iterations` / `max_budget_per_session` caps, keyed on a session
    identifier) — the contrast worth naming for Ch05: LiteLLM's A2A *sessions*
    get documented, configurable cost controls, while container *sessions* get
    a "Spend Management ✅ Budget tracking and rate limiting" cell and nothing
    else (Claim 10). Same word, very different operational contract.

- **Novel**: First source note in the corpus covering:
  - The **container session lifecycle** itself — `/v1/containers`
    create/list/retrieve/delete, the eight sync/async SDK helpers, and the
    three response
    objects (no other note extracts `create_container`, `list_containers`, or
    `delete_container` as claims; the Files note explicitly left container
    lifecycle to this issue).
  - **`expires_after{anchor, minutes}`** as the only documented retention
    bound over vendor-held session files, its create-time-only scope, the
    `last_active_at` idle-timeout reading, and the absence of an
    absolute-lifetime option (Claims 2, 3).
  - The **documented expiry/failure gap** (Claims 4, 11): timestamps and a
    `status` field exist, but no status enum, no expiry behavior, no error
    codes, no retries, no GC anywhere on the page.
  - **Provider-precedence and `model`-placement rules for container calls**
    (Claims 6, 7) — the per-request routing surface for this endpoint family,
    including the GET-vs-body asymmetry between list and create.

## Guide Impact

- **Chapter 06 (Security and Trust) — §"Gateway-level code-execution
  interception"**: The chapter's existing rule — "Model-generated code must not
  execute on opaque vendor-hosted containers" — is the *reason* this API is the
  "before" state; cite this note as the concrete native surface interception
  bypasses (Extends: `blog-litellm-swap-openai-code-interpreter.md` Claims 1,
  2, 7). Add the retention consequence for deployments that *do* enable vendor
  containers: `expires_after` (create-time, anchor example `last_active_at`) is
  the only documented bound over session-held `file_ids` (Claims 2–3), the page
  never says what expiry does to those files (Claim 4), and the only removal
  path is explicit DELETE (Claim 11) — so artifact/session cleanup must be an
  explicit operational job. Pair with `docs-litellm-container-files-api.md`
  Claim 7 for the file half of the same gap. Note the provider scope (Claim 9):
  `openai`/`azure` only, no operator-sandbox counterpart.

- **Chapter 05 (LLM Ops Reliability)**: Add **container sessions as an
  operational resource**: (a) **deployment-bound state** — a routed create
  returns an ID that encodes the deployment, so retrieve/delete self-route and
  cannot be freely load-balanced; treat containers as pinned to the creating
  deployment (drain/expire before removing it), and expect Azure affinity to
  reach a specific resource endpoint (Claims 5, 9). (b) **Bounded
  enumeration** — cleanup scripts must paginate: `limit` 1–100 defaults to 20,
  `order` defaults to `desc`, cursor `after`, `has_more` in the envelope
  (Claim 8). (c) **Documented silence as a caveat** — no error codes, no
  retries, no timeouts, no expiry behavior, no GC (Claims 4, 11); state the
  absence rather than inferring behavior. (d) **Provider precedence** for
  per-request provider steering: header > query > body > default `openai`, and
  the `model`-in-body-vs-query rule for `model_list` credentials (Claims 6, 7).

- **Chapter 02 / Ch05 observability**: **Do not import** the feature-table
  flags (Claim 10). Cost Tracking, Logging, Load Balancing, and Spend
  Management are unsubstantiated checkmarks on this page — specifically, there
  is no evidence that container creates consume virtual-key budgets or emit
  logs the way `/v1/chat/completions` does, and the Load Balancing row is in
  unresolved tension with the deployment-pin rule on the same page. Flagged
  explicitly so the ✅s are not picked up downstream as evidence, consistent
  with `docs-litellm-container-files-api.md` Claim 8.

- **Explicitly do not import**: any statement about what happens when a
  container expires (status change, file purge, error on retrieve), any
  absolute-lifetime or default-TTL policy, and any Docker/OCI deployment claim
  — the page contains none of these.

## Extraction Notes

- Source read in full on 2026-10-08 via direct HTTP fetch (Docusaurus page,
  HTTP 200, no paywall, no truncation). All quoted passages were located in
  the rendered HTML and copied character-for-character; code blocks were
  extracted with line breaks preserved from the `<pre>` elements, tables from
  their `<td>` cells. Per §1, linked pages were checked for substance: the two
  outbound links are the sibling Container Files API (`/docs/container_files`,
  already mined as issue #1622) and the Code Interpreter guide
  (`/docs/guides/code_interpreter`, already followed and cited by that note) —
  neither carried additional container-lifecycle content not quoted here, so
  no further pages were pursued.
- **Scope honored**: despite the `/containers` slug, no deployment/OCI
  content exists on the page (single local `litellm` process on port 4000);
  nothing about Docker, images, scaling, health checks, or resource limits is
  extracted.
- **Sibling issue #1622** (`docs container_files`) is already merged as
  `docs-litellm-container-files-api.md`. That note deliberately left container
  lifecycle (deployment-encoding statement, `expires_after`) unclaimed for this
  issue; the overlap here is limited to that shared routing statement (Claim
  5), which both notes quote verbatim from this page.
- **Contradiction evaluation (§4a)**: the Load Balancing ✅ row vs the
  deployment-encoded-ID statement was assessed and **not** filed (reasoning in
  Claim 10 and Cross-References → Contradicts). Verified against
  `CONTRADICTIONS.md` (no container entries), open `contradiction`-labeled
  issues (none cover this surface), and all corpus notes. No opposing claim in
  any existing note: the swap note's interception path and this native path are
  disjoint feature areas, not opposed claims.
- `confidence_overall: settled` — every numbered claim is descriptive of a
  first-party API contract (routes, parameters, precedence, object shapes) or
  an absence verified against the full page text. The unverified items (the
  five feature-table checkmarks, the idle-timeout reading of
  `last_active_at`) are quarantined in Claims 2 and 10 as asserted/inferred
  rather than relied on.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are either cited above or explicitly dismissed here:
  - `docs-litellm-batches-api.md` — cited (Corroborates, Claim 10 of that
    note: ID-encoded routing state).
  - `docs-litellm-completion-web-search.md` — cited (Corroborates, Claim 15:
    documented operational silence).
  - `docs-litellm-bedrock-invoke.md` — cited (Corroborates, Claims 3 and 6:
    bare-checkmark support matrix vs a configured load-balancing example).
  - `docs-litellm-audio-transcription.md` — cited (Corroborates, Claims 5–6:
    per-endpoint support-matrix genre).
  - `docs-litellm-completion-input-params.md` — param gating/defaults on the
    completion path; no container parameter overlap (its **Claim 5**
    prose-vs-code default disagreement is a docs-quality pattern this note
    does not reproduce — no code/default conflict was found on this page).
    Dismissed.
  - `docs-litellm-completion-web-fetch.md` — Anthropic web-fetch tool
    parameters; different feature entirely. Dismissed.
  - `docs-litellm-a2a-iteration-budgets.md` — cited (Extends, Claim 1:
    session-scoped cost controls as the contrast to a Spend Management
    checkmark).
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — its sandbox/write-guardrail
    claims (Claims 2–3) are the principle behind the guide's interception rule,
    already cited there via the swap note; this page documents container CRUD,
    not code execution or writes, so it does not engage those claims
    directly. Dismissed as a cross-ref for *this* note (relevant to Ch06 via
    `blog-litellm-swap-openai-code-interpreter.md` instead).
  - `docs-litellm-anthropic-advisor-tool.md` — advisor sub-inference usage
    accounting; no shared claim. Dismissed.
  - `blog-litellm-auto-router-v2.md` — model-selection routing (complexity/
    semantic/adaptive); this note covers per-request *provider* selection for a
    non-chat endpoint. Different routing layer. Dismissed.
- Triage-flagged notes addressed: `blog-litellm-swap-openai-code-interpreter.md`
  (cited — Extends; native "before" surface, not a re-derivation of the
  interception mechanism), `docs-litellm-container-files-api.md` (cited —
  Corroborates + Extends; lifecycle side of its feature area),
  `docs-litellm-completion-function-call.md` (verification posture — that
  note's **Claim 14** established the corpus rule that LiteLLM doc code blocks
  are illustrative, not transcribed; accordingly this note verifies quotes
  against the live page only and makes no claim about shipped behavior behind
  the documented surface).
- No code/implementation verification was performed for this note (no claim
  asserts what LiteLLM's code does — only what this page documents), so no
  version-pinned source read was needed.
