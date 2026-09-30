---
source_url: https://docs.litellm.ai/docs/completion/knowledgebase
source_type: docs
title: "Using Vector Stores (Knowledge Bases) | liteLLM"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page footer reads "Copyright © 2026 liteLLM")
date_extracted: 2026-09-30
last_checked: 2026-09-30
status: current
confidence_overall: emerging
issue: "#1508"
---

# Using Vector Stores (Knowledge Bases) — gateway-side retrieval augmentation (LiteLLM Docs)

> The corpus's only record of **retrieval augmentation performed inside the
> gateway**: when a request names a vector store that exists in
> `vector_store_registry`, LiteLLM silently adds a provider-side `retrieve`
> call, rewrites the message array to insert a second `user` turn prefixed
> `Context:`, and returns the citations out-of-band in a non-standard field —
> on streaming, **only on the final chunk gated on `finish_reason == "stop"`**.
> The page documents two incompatible wire shapes for the same parameter and
> never reconciles them (filed as contradiction **#1517**), and it is silent on
> every failure mode: per the shipped hook, a search error **fails open** — the
> request proceeds un-grounded with the failure recorded in a second
> undocumented `provider_specific_fields` key — and pre-call **guardrails run
> over each retrieved chunk**, so a knowledge-base document can fail the user's
> request.

## Source Context

- **Type**: docs (LiteLLM first-party documentation, "Guides > Retrieval &
  Knowledge", the only child page of that guide section; verified HTTP 200 on
  2026-09-30). Living/undated — the page carries no publication or revision
  date, only a `Copyright © 2026 liteLLM` footer.
- **Author credibility**: BerriAI / LiteLLM, the gateway vendor. Authoritative
  for the *surface* it defines: the `VectorStoreRegistry` schema, the
  `config.yaml` block, the response field paths, the provider support matrix,
  the control-plane endpoint. It is **capability documentation only** — there
  is no measured latency added by the retrieval hop, no hit-rate, no token or
  cost impact, no failure writeup, and no versioning of the behaviour against
  any LiteLLM release. Every claim below therefore stays at "the vendor
  documents this", never "this holds at scale".
- **Scope**: Covers the full gateway-side retrieval surface: SDK + proxy
  quickstart, `config.yaml` and UI registry setup, the documented
  request-transformation mechanic, the citation response contract (non-streaming
  and streaming), the "always on for a model" default, `GET /vector_store/list`,
  the UI Logs view, and the provider matrix. It does **not** cover chunking,
  embedding strategy, index refresh, ranking beyond the single `score` float,
  retrieval quality, or multi-tenant isolation of retrieved content.
- **Claims marked `[code-verified]`**: for the six claims where the page's
  contract is either silent or under-specified in a way that matters
  operationally, the claim was checked against LiteLLM `main` on 2026-09-30
  (latest release at that moment: `v1.104.0-rc.2`, published 2026-09-30) —
  principally `litellm/integrations/vector_store_integrations/vector_store_pre_call_hook.py`
  and `litellm/vector_stores/vector_store_registry.py`. These are **not**
  vendor-documented claims and are attributed as such in each claim's Evidence
  field. This follows the precedent set by `docs-litellm-message-sanitization.md`
  (issue #1509).

## Extracted Claims

### Claim 1: Retrieval is triggered by *registry membership*, not by an opt-in flag — any requested vector-store ID that is found in the `vector_store_registry` causes LiteLLM to run the retrieval, and the registry is the only place a store can be declared

- **Evidence**: The "How It Works" trigger sentence, plus the fact that every one
  of the page's six worked request examples keys on the same registered ID
  (`T37J8R4WTM`), which can only come from the `vector_store_registry` block in
  `config.yaml` or the UI "Create Vector Store" form.
- **Confidence**: settled (documented trigger condition and a closed config surface)
- **Quote**: "If your request includes a `vector_store_ids` parameter where any of the vector store ids are found in the `vector_store_registry`, LiteLLM will automatically use the vector store for the request."
- **Our assessment**: We buy the trigger as documented. What the page does
  **not** say is what happens when a requested ID is *not* in the registry — and
  this is the whole reliability question, because the answer determines whether a
  grounding bug is a 5xx or a silent no-op. `[code-verified]` the shipped hook
  returns the original messages unchanged when no registered store matches
  (`_augment_messages` returns `None` and `async_get_chat_completion_prompt`
  short-circuits), so the answer is: **silently nothing happens**. No error, no
  warning on the request, no field in the response. The guide should treat
  "unregistered vector-store ID" as a silent-failure class on par with an
  unmatched fallback target.

### Claim 2: The retrieval query is the **last message only** — and the page's only worked transformation is a single-message request, so it cannot show what happens to earlier turns

- **Evidence**: The three-bullet "How It Works" list, and the "Example
  Transformation" section, whose "Original Request to LiteLLM" payload contains
  exactly one message.
- **Confidence**: settled
- **Quote**: "Uses your last message as the query to retrieve relevant information from the Knowledge Base"
- **Our assessment**: This is the multi-turn trap, and the page's example hides
  it rather than showing it. The gateway is documented as deriving the entire
  retrieval query from one message — the user must restate the retrieval
  intent in the final turn, since a follow-up like "yes, make it shorter" carries
  no searchable content and the earlier substantive question is invisible to the
  retriever. There is no documented `search_query` override. `[code-verified]`
  the shipped `_extract_query_from_messages` returns `messages[-1]` and returns
  `None` when that message is not dict-shaped, has no `content`, or carries no
  `type: "text"` content item — and a `None` query aborts retrieval entirely with
  only a debug line. The concrete consequence: **a chat turn whose last message
  is a tool result, an assistant continuation, or a non-text block gets no
  retrieval and no error.** For any tool-using agent loop proxied through this
  gateway, that is most turns.

### Claim 3: The gateway rewrites the message array — retrieved text is injected as an *additional `user` turn* prefixed `Context:`, so context and cost accounting shift at the gateway, not at the client

- **Evidence**: The page's three-step "Example Transformation", including the
  exact outbound provider call and the exact augmented request body (both
  reproduced under Concrete Artifacts).
- **Confidence**: settled (for the single-store, single-message case the page actually shows)
- **Quote**: "Adds the retrieved context to your conversation"
- **Our assessment**: We buy the mechanic — this is real, wire-level evidence
  and it is the page's most valuable content. Two refinements the page's example
  is too small to show, both `[code-verified]` against the shipped hook:
  (a) the context turn is **inserted immediately before the final message**,
  not appended after it — `_messages_with_context` returns
  `[..., *messages[:-1], *context_messages, *messages[-1:]]`, so on a multi-turn
  conversation the `Context:` turn lands *inside* the history, between the prior
  exchange and the question being asked; and (b) there is **one `Context:` turn
  per vector store**, each independently prefixed (`CONTENT_PREFIX_STRING =
  "Context:\n\n"`), with each result's text joined by blank lines — so N
  registered stores matching one request produce N user turns. Note also that
  the page captions step 3 "Final Request to LiteLLM" when the payload shown is
  the request going *to the model*; a small mislabel, but it invites reading the
  transformation as round-tripping through LiteLLM rather than out to Anthropic.
  Neither the injection point nor the per-store fan-out is documented, and both
  change how a client should expect its own message array to look in provider
  logs.

### Claim 4: Citations are out-of-band in a non-standard field, and on the streaming path they exist only on the final chunk gated on `finish_reason == "stop"`

- **Evidence**: The "Key Concept" statement, the streaming example payload, and
  both streaming SDK snippets, each of which branches on `finish_reason == "stop"`
  to read the field. The `Search Result Fields` table gives the inner schema
  (`search_query`, `data[]`, `score`, `content`, `filename`, `file_id`,
  `attributes`).
- **Confidence**: settled
- **Quote**: "Search results are always in: `response.choices[0].message.provider_specific_fields["search_results"]`"
- **Our assessment**: The non-standard field is the lesser problem and the
  `finish_reason` gate is the real one. A stream that terminates any other way —
  client disconnect, gateway or provider timeout, `max_tokens` truncation giving
  `finish_reason == "length"` — carries **neither the citations nor any marker
  that retrieval ran**. Retrieval that succeeded and retrieval that never
  happened are byte-identical from the collector's point of view, and the
  degradation window is exactly the window where the answer is most likely to be
  wrong. `[code-verified]` this is structural, not incidental: the streaming path
  is a *deployment* hook
  (`async_post_call_streaming_deployment_hook`) whose own docstring is "Add search
  results to the final streaming chunk", so there is no mechanism by which an
  intermediate chunk could carry them. The page's own streaming snippets encode
  the trap for the reader — the Python one prints the model text on every chunk
  and the citations once, after the stream is already over. The guide should
  require that any attribution or citation metric be computed from a
  final-chunk-aware collector, and should state that citation absence is
  ambiguous rather than evidence of non-retrieval.

### Claim 5: "Always on for a model" makes retrieval **unconditional for every request routed to that model alias**, with no per-request signal

- **Evidence**: The `config.yaml` block under that heading, which puts
  `vector_store_ids` inside a `model_list` entry's `litellm_params`, plus the
  page's own prose describing the effect.
- **Confidence**: settled (config surface and stated effect); the operational
  consequence is our assessment
- **Quote**: "This means that any request to the claude-3-5-sonnet-with-vector-store model will always use the vector store with the id `T37J8R4WTM` defined in the `vector_store_registry`."
- **Our assessment**: This is the blast-radius pattern and the page gives no way
  to bound it. Because the switch is scoped to a *model alias* rather than to a
  request, the blast radius of the alias is the blast radius of the grounding:
  any caller, any key, any team, any workload that resolves to
  `claude-3-5-sonnet-with-vector-store` is grounded whether or not it asked to
  be. The page is silent on what happens when that alias is a fallback target
  or a routing destination — and in this gateway those are ordinary
  configuration, not exotic. The failure mode is therefore the one
  `guide/05-llm-ops-reliability.md` §"Silent model fallback breaks attribution"
  already names, arriving from a different direction: a fallback *onto* the
  vector-store alias injects enterprise content into a request that was not
  written for it, and a fallback *off* it silently removes grounding from a
  request that depended on it. Neither is visible in the response's `model`
  field. A guide rule should require that any alias carrying `vector_store_ids`
  be excluded from fallback chains and from cross-tier routing pools, or that
  retrieval state be asserted (not assumed) from the response.

### Claim 6: A per-store search error fails **open** by default — the request proceeds with that store's context missing, and the failure is recorded in a second, undocumented `provider_specific_fields` key

- **Evidence**: `[code-verified]` — the shipped hook's
  `_DEFAULT_FAILURE_MODE: Final[VectorStoreSearchFailureMode] = "annotate"`, its
  `_search_one` exception handler, and its two `provider_fields[...]`
  assignments.
- **Confidence**: emerging (read from `main`, not from any release note or docs page; not verified at a pinned tag)
- **Quote**: (no direct quote; the page documents no failure behaviour — see paraphrase in Our assessment)
- **Our assessment**: This is the most operationally important thing on the page
  and the page says nothing about it. `[code-verified]` the search call is
  wrapped in a `try/except Exception` that logs
  `"Vector store search failed for vector_store_id=%s, continuing without its context"`
  at *warning* and returns a `SearchFailed`; in the default `annotate` mode the
  request then goes to the model with **less grounding than intended and no
  error**, and the failure is attached out-of-band under
  `vector_store_search_failures` in `provider_specific_fields` — a key absent
  from the page's `Search Result Fields` table. Setting
  `litellm.vector_store_search_failure_mode = "error"` converts the same
  condition into a raised `VectorStoreSearchError`. So the operator has a real
  fail-closed switch, undocumented, and the default is the one that produces
  confidently-wrong answers. Two operational consequences the guide should carry:
  alert on `vector_store_search_failures` *before* alerting on retrieval
  quality, and treat retrieval degradation as its own failure domain rather than
  folding it into model errors. This claim is the main reason this note is not
  rated `settled` — it rests on reading `main`, and the default could change
  without notice.

### Claim 7: Pre-call guardrails run over each retrieved context chunk, and a block fails the request — so knowledge-base content is an input to the guardrail, and a document can fail a chat

- **Evidence**: `[code-verified]` — the hook's module docstring and its
  `_scanned_context_messages` / `_scan_through` methods.
- **Confidence**: emerging (code-only, `main`)
- **Quote**: (no direct quote; the page does not mention guardrails anywhere)
- **Our assessment**: The page describes retrieval as a transparent
  context-injection step and never mentions that the gateway's own guardrail
  layer processes the retrieved text. `[code-verified]` it does, and in two
  ways that matter. First, the guardrail receives the **client's original
  request body** — `_scan_request` reads `proxy_server_request.body` out of the
  non-default params — so a guardrail's decisions on a retrieval-augmented
  request are being made against the unaugmented payload, which is the payload
  the user never sent and cannot see. Second, the retrieved context is scanned
  and the scanned output *replaces* it (`_messages_with_context` is called on
  `scanned_context`, not on the raw context), so masking/redaction applied by a
  guardrail silently changes the facts the model is grounded on, with nothing in
  the response recording it. And a guardrail that *blocks* raises rather than
  annotates: a document sitting in an enterprise knowledge base can fail the
  user's chat, months after it was indexed, on a trigger the user never
  authored. This is the sharpest new instance of the corpus's "a guardrail in the
  request path is an availability dependency" theme, because here the
  guardrail's input set is partly machine-generated and outside the caller's
  control.

### Claim 8: The client-declared `file_search` tool is **consumed by the gateway** — a recognised one is removed from `tools` before the provider call, and recognition is all-or-nothing

- **Evidence**: `[code-verified]` — `get_and_pop_recognised_vector_store_tools`
  in `litellm/vector_stores/vector_store_registry.py`, the function the
  retrieval path (`pop_vector_stores_to_run_with_db_fallback`) calls.
- **Confidence**: emerging (code-only, `main`)
- **Quote**: (no direct quote; the page presents `file_search` as a tool the client sends and never says whether the model receives it)
- **Our assessment**: Two things worth writing down. First, the tool does not
  reach the model: `[code-verified]` recognised entries are removed from the
  `tools` list via `remove_items_at_indices` before the request goes upstream,
  and the top-level parameter is likewise `pop`ped out of the params. So the
  `file_search` tool in the request is a *gateway* directive wearing a provider
  tool's clothes — a client cannot use it to make a native provider-side file
  search, and a reader of the page would reasonably assume it could. This is the
  same shape as the advisor-tool finding in
  `docs-litellm-anthropic-advisor-tool.md` (Claim 7: the client's view of what
  the model was offered does not survive the gateway). Second, recognition is
  `if all(...)` over the ID list, so **one unrecognised ID in a multi-store
  `tools` entry disables retrieval for all of them, the entry is not popped, and
  it is forwarded to the provider instead** — the request succeeds, the model
  receives a `file_search` tool for a store that LiteLLM never queried, and no
  citations appear. The top-level parameter does not have this all-or-nothing
  property: it is resolved one ID at a time, in memory and then against the
  database. The two documented-but-unreconciled shapes therefore also have
  different partial-failure semantics, which is the substance of contradiction
  **#1517**.

### Claim 9: The provider matrix carries two explicit capability gaps and one BETA — Azure Vector Stores "cannot be directly queried", RAGFlow Datasets are "dataset management only", MongoDB Vector Search is BETA

- **Evidence**: The "Supported Vector Stores" list, with the parenthetical
  qualifications the page attaches inline.
- **Confidence**: settled (as a vendor support statement)
- **Quote**: "(Dataset management only, search not supported)"
- **Our assessment**: The gaps are the useful half of a support matrix, and this
  one is unusually honest about them: a RAGFlow "vector store" that cannot be
  searched is a registry entry with no retrieval behind it — register it and
  requests appear grounded-shaped but return nothing. Azure Vector Stores'
  qualifier is the sharpest: the store exists in LiteLLM's registry and in this
  support list, but is reachable only through Assistants messages, so a
  `/v1/chat/completions` request naming it cannot retrieve. Both read as
  "listed as supported, not usable on this endpoint". The MongoDB entry being
  explicitly BETA matters for a capacity conversation: a knowledge-base tier
  built on it inherits a stability caveat the other rows do not carry.

### Claim 10: PG Vector requires a **separately deployed connector** whose embedding configuration points back at the LiteLLM proxy itself — a circular dependency in the retrieval path

- **Evidence**: The "PG Vector" section's `.env` block, reproduced verbatim
  below.
- **Confidence**: settled (for the documented env contract); the cycle is our reading of those values
- **Quote**: "LiteLLM provides a server that exposes OpenAI-compatible `vector_store` endpoints for PG Vector. The LiteLLM Proxy server connects to your deployed service and uses it as a vector store when querying."
- **Our assessment**: This is the only part of the page with real deploy shape,
  and it is where the operational dependency lives. The connector is a second
  process to run, secure, version, and monitor, with its own `SERVER_API_KEY` —
  and note that in the page's own example the connector's `SERVER_API_KEY` and
  the embedding `EMBEDDING__API_KEY` are **the same literal value**, one LiteLLM
  API key serving both as the connector's inbound credential and as the proxy's
  credential for outbound embedding calls. `EMBEDDING__BASE_URL="http://localhost:4000"`
  completes the picture: the connector's embedding traffic is routed back
  through the proxy that depends on it. An embedding-request storm or a proxy
  degradation therefore degrades *indexing and querying* simultaneously, and the
  cycle is invisible if you read only the "PG Vector" UI steps — the page lists
  the connector as a deployment prerequisite and never mentions that its
  embeddings re-enter the proxy. Also operationally relevant: `DB_FIELDS__*`
  makes the Postgres schema a named contract (six columns, `EMBEDDING__DIMENSIONS`
  pinned to 1536 for `text-embedding-ada-002`), so a silent embedding-model
  change on the proxy side is a dimensionality break discovered as query
  failures, not as a config error.

### Claim 11: The registry is a control-plane object with its own list endpoint, credential reference, pagination fields, and a log view of the retrieval query

- **Evidence**: The "Listing available vector stores" section (request + response
  payloads) and the "Logging Vector Store Usage" section.
- **Confidence**: settled
- **Quote**: "After completing a request with a vector store, navigate to the `Logs` page on LiteLLM. Here you should be able to see the query sent to the vector store and corresponding response with scores."
- **Our assessment**: `GET /vector_store/list` is an authenticated
  enumeration of every knowledge base the proxy can reach, each entry carrying
  `litellm_credential_name` — so it is both an inventory endpoint and a map of
  which credential touches which corpus, worth treating as sensitive in an
  inventory-diff context. The response is paginated
  (`total_count` / `current_page` / `total_pages`), which matters for
  scripted reconciliation against the config. The Logs page is the page's *only*
  stated observability surface for retrieval, and it is a UI, not an export, not
  a metric, and not an OTel span — the query that was actually issued and the
  scores that came back are visible to a human in a browser and to nothing else.
  That is a real gap against the corpus's span model (Claim 12, and
  `guide/02-observability.md` §"The seven-kind span taxonomy", which already
  has a `Retrieval` kind). One inconsistency to note while reading: the page
  gives two different UI paths for the same object — "Experimental > Vector
  Stores" in the registry section, "Tools > Vector Stores" in every
  provider-specific guide.

### Claim 12: The page documents two incompatible wire shapes for `vector_store_ids` — `tools`-wrapped `file_search` in all six worked examples, top-level parameter in the trigger sentence, the worked transformation, and the API Reference table — and never reconciles them

- **Evidence**: Six code blocks use the `tools` form; the "How It Works"
  trigger and step 1, the "Original Request to LiteLLM" payload, and the API
  Reference parameter table use or describe the top-level form. `[code-verified]`
  both are read by the shipped registry resolver, which collects the top-level
  param and the tool-embedded IDs and dedupes them.
- **Confidence**: settled (that the page is inconsistent); see contradiction #1517 for the resolution
- **Quote**: "Pass tools with vector_store_ids to the completion request. Where `vector_store_ids` is a list of vector store ids you initialized in litellm.vector_store_registry"
- **Our assessment**: Filed as contradiction **#1517** rather than resolved
  here. Both shapes work in the shipped code, so this is a documentation gap
  rather than a broken feature — but the page's *only* wire-level evidence of
  the request transformation is the top-level form, while every copy-pasteable
  example is the `tools` form, and per Claim 8 the two shapes do not degrade
  identically on a partial registry match. The guide should not derive a
  canonical client shape from this page alone until that issue is resolved.

## Concrete Artifacts

### The request transformation, as the page publishes it (page, "How It Works → Example Transformation")

Step 1 — what the client sends:

```json
{
    "model": "anthropic/claude-sonnet-5",
    "messages": [
        {"role": "user", "content": "What is litellm?"}
    ],
    "vector_store_ids": ["YOUR_KNOWLEDGE_BASE_ID"]
}
```

Step 2 — what the gateway sends to the provider, to the endpoint the page names:

```
https://bedrock-agent-runtime.{aws_region}.amazonaws.com/knowledgebases/YOUR_KNOWLEDGE_BASE_ID/retrieve
```

```json
{
    "retrievalQuery": {
        "text": "What is litellm?"
    }
}
```

Step 3 — what the gateway sends to the model (page caption: "Final Request to LiteLLM"):

```json
{
    "model": "anthropic/claude-sonnet-5",
    "messages": [
        {"role": "user", "content": "What is litellm?"},
        {"role": "user", "content": "Context: \n\nLiteLLM is an open-source SDK to simplify LLM API calls across providers (OpenAI, Claude, etc). It provides a standardized interface with robust error handling, streaming, and observability tools."}
    ]
}
```

Note that step 3's payload carries **no `tools` key**, and the model is
`anthropic/claude-sonnet-5` while the store is a Bedrock knowledge base — the
retrieval provider and the generation provider are independent, and the page's
own examples pair a Bedrock store with a first-party Anthropic model. Also note
that the `Context:` turn is captioned as going "to LiteLLM"; it is the outbound
request to the model.

### Proxy `config.yaml` — registry declaration (page, "1. Configure your vector_store_registry")

```yaml
vector_store_registry:
  - vector_store_name: "bedrock-litellm-website-knowledgebase"
    litellm_params:
      vector_store_id: "T37J8R4WTM"                            # Required: Unique ID
      custom_llm_provider: "bedrock"                           # Required: Provider
      vector_store_description: "Bedrock vector store for the Litellm website knowledgebase"
      vector_store_metadata:
        source: "https://www.litellm.com/docs"
```

The page states that block "accepts all the same parameters as the
`LiteLLM_ManagedVectorStore` constructor in the Python SDK", whose required
fields are `vector_store_id` and `custom_llm_provider`, with
`vector_store_name`, `vector_store_description`, `vector_store_metadata`, and
`litellm_credential_name` optional.

### "Always on for a model" (page, verbatim block)

```yaml
model_list:
  - model_name: claude-3-5-sonnet-with-vector-store
    litellm_params:
      model: anthropic/claude-sonnet-5
      vector_store_ids: ["T37J8R4WTM"]

vector_store_registry:
  - vector_store_name: "bedrock-litellm-website-knowledgebase"
    litellm_params:
      vector_store_id: "T37J8R4WTM"
      custom_llm_provider: "bedrock"
      vector_store_description: "Bedrock vector store for the Litellm website knowledgebase"
      vector_store_metadata:
        source: "https://www.litellm.com/docs"
```

The alias is named `claude-3-5-sonnet-with-vector-store` and points at
`anthropic/claude-sonnet-5` — the page's copy-paste block carries a stale name,
which is a small but real hazard for anyone copying an alias into a routing
table or a dashboard filter.

### Non-streaming response with citations (page, "Non-Streaming Example")

```json
{
  "id": "chatcmpl-abc123",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "LiteLLM is a platform...",
      "provider_specific_fields": {
        "search_results": [{
          "search_query": "What is litellm?",
          "data": [{
            "score": 0.95,
            "content": [{"text": "...", "type": "text"}],
            "filename": "litellm-docs.md",
            "file_id": "doc-123"
          }]
        }]
      }
    },
    "finish_reason": "stop"
  }]
}
```

### Streaming: citations on the final chunk only (page, "Streaming Example")

```json
{
  "id": "chatcmpl-abc123",
  "choices": [{
    "index": 0,
    "delta": {
      "provider_specific_fields": {
        "search_results": [{
          "search_query": "What is litellm?",
          "data": [{
            "score": 0.95,
            "content": [{"text": "...", "type": "text"}],
            "filename": "litellm-docs.md",
            "file_id": "doc-123"
          }]
        }]
      }
    },
    "finish_reason": "stop"
  }]
}
```

The page's own Python consumer shows the gate the collector has to implement
(python):

```python
for chunk in stream:
    # Stream content
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    # Get citations in final chunk
    if chunk.choices[0].finish_reason == "stop":
        search_results = getattr(chunk.choices[0].delta, 'provider_specific_fields', {}).get('search_results', [])
```

Note the asymmetry this makes unavoidable in a collector: `delta.content` is
read every chunk, `search_results` only on the terminal one. There is no chunk
that carries "retrieval ran but produced nothing".

### `GET /vector_store/list` (page, "Listing available vector stores")

```bash
curl -X GET "http://localhost:4000/vector_store/list" \
  -H "Authorization: Bearer $LITELLM_API_KEY"
```

```json
{
  "object": "list",
  "data": [
    {
      "vector_store_id": "T37J8R4WTM",
      "custom_llm_provider": "bedrock",
      "vector_store_name": "bedrock-litellm-website-knowledgebase",
      "vector_store_description": "Bedrock vector store for the Litellm website knowledgebase",
      "vector_store_metadata": {
        "source": "https://www.litellm.com/docs"
      },
      "created_at": "2023-05-03T18:21:36.462Z",
      "updated_at": "2023-05-03T18:21:36.462Z",
      "litellm_credential_name": "bedrock_credentials"
    }
  ],
  "total_count": 1,
  "current_page": 1,
  "total_pages": 1
}
```

The `created_at` / `updated_at` values are the page's own (identical timestamps
on a store the page just created, and a 2023 date on a 2026-dated knowledge
base) — treat them as illustrative, not as an audit trail.

### PG Vector connector `.env` (page, "PG Vector")

```
DATABASE_URL="postgresql://neondb_owner:xxxx"
SERVER_API_KEY="sk-<your-litellm-api-key>"
HOST="0.0.0.0"
PORT=8001
EMBEDDING__MODEL="text-embedding-ada-002"
EMBEDDING__BASE_URL="http://localhost:4000"
EMBEDDING__API_KEY="sk-<your-litellm-api-key>"
EMBEDDING__DIMENSIONS=1536
DB_FIELDS__ID_FIELD="id"
DB_FIELDS__CONTENT_FIELD="content"
DB_FIELDS__METADATA_FIELD="metadata"
DB_FIELDS__EMBEDDING_FIELD="embedding"
DB_FIELDS__VECTOR_STORE_ID_FIELD="vector_store_id"
DB_FIELDS__CREATED_AT_FIELD="created_at"
```

### Implementation verification (Miner, not the page)

Source: `litellm/integrations/vector_store_integrations/vector_store_pre_call_hook.py`
and `litellm/vector_stores/vector_store_registry.py` at `main`, retrieved
2026-09-30 (latest release `v1.104.0-rc.2`, published 2026-09-30). Snippets are
verbatim from those two files with elisions marked `...`; no line numbers are
given, because they drift against `main`.

```python
# vector_store_pre_call_hook.py — the documented query rule and its abort case
    def _extract_query_from_messages(self, messages: Sequence[AllMessageValues]) -> str | None:
        """
        Extract the query from the last user message.

        Args:
            messages: List of messages

        Returns:
            The extracted query string or None if not found
        """
        if not messages or len(messages) == 0:
            return None

        last_message: Final = messages[-1]
        if not isinstance(last_message, dict) or "content" not in last_message:
            return None

        content: Final = last_message["content"]

        if isinstance(content, str):
            return content
        elif isinstance(content, list) and len(content) > 0:
            # Handle list of content items, extract text from first text item
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                    return item["text"]

        return None
```

```python
# vector_store_pre_call_hook.py — injection point, prefix, fail-open default, hidden failure field
    CONTENT_PREFIX_STRING = "Context:\n\n"

    def _messages_with_context(
        self,
        messages: Sequence[AllMessageValues],
        context_messages: Sequence[AllMessageValues],
    ) -> list[AllMessageValues]:
        if not context_messages:
            return list(messages)
        return [*messages[:-1], *context_messages, *messages[-1:]]

SEARCH_FAILURES_FIELD: Final = "vector_store_search_failures"
_DEFAULT_FAILURE_MODE: Final[VectorStoreSearchFailureMode] = "annotate"
```

```python
# vector_store_pre_call_hook.py — a failed search does not fail the request
        except Exception as search_error:
            verbose_logger.warning(
                "Vector store search failed for vector_store_id=%s, continuing without its context: %s",
                vector_store_id,
                search_error,
            )
            return SearchFailed(
                failure=VectorStoreSearchFailure(
                    vector_store_id=vector_store_id,
                    custom_llm_provider=custom_llm_provider,
                    error=str(search_error),
                )
            )
```

```python
# vector_store_registry.py — both wire shapes are read, and deduped
    def get_vector_store_ids_to_run(self, non_default_params: dict, tools: list[dict] | None = None) -> list[str]:
        """
        Returns the vector store ids to run

        vector_store_ids can be provided in two ways:
        """
        vector_store_ids: list[str] = []

        # 1. check if vector_store_ids is provided in the non_default_params
        vector_store_ids_param: Final = non_default_params.get("vector_store_ids")
        if isinstance(vector_store_ids_param, list):
            vector_store_ids.extend(vector_store_ids_param)

        # 2. check if vector_store_ids is provided as a tool in the request
        vector_store_ids = self._get_vector_store_ids_from_tool_calls(tools=tools, vector_store_ids=vector_store_ids)

        return list(dict.fromkeys(vector_store_ids))
```

```python
# vector_store_registry.py — all-or-nothing recognition, and the tool is popped
            # Check if all vector_store_ids are recognized in the registry
            recognised = all(
                any(vs.get("vector_store_id") == vs_id for vs in self.vector_stores) for vs_id in tool_vector_store_ids
            )

            if recognised:
                tools_to_remove.append(i)
                ...
        # Remove recognized tools from the original list
        remove_items_at_indices(items=tools, indices=tools_to_remove)
```

```python
# vector_store_registry.py — config.yaml-declared stores skip the DB existence check
            # Verify vector store still exists in database (if we have DB access)
            # This ensures deleted vector stores are removed from cache
            if vector_store is not None and prisma_client is not None and not vector_store.get("is_config", False):
```

Consequence, stated as read from the code rather than as a verified claim: a
store declared in `config.yaml` carries `is_config`, skips the database
existence check, and therefore is **not** removed from the in-memory registry
when it is deleted through the UI — so deleting a vector store in one place and
declaring it in `config.yaml` in another does not disable it. This was not
re-tested against a pinned tag.

## Cross-References

All citations below were verified by re-reading the cited note and counting
claims in document order, per `agents/MINER.md` §4b. Every candidate path in
`miner-related-notes.md` is either cited or explicitly dismissed below.

- **Corroborates**:
  - `docs-litellm-anthropic-advisor-tool.md` — **Claim 7** ("On the
    non-Anthropic orchestration path the client receives a clean response with no
    advisor blocks at all, so the advisor's contribution is not observable by
    the client") and **Claim 2** (sub-inference spend split out of top-level
    `usage`). This source is the same gateway with the same shape of problem one
    layer down: a gateway-injected sub-call whose effect on the request and whose
    cost are both visible only out-of-band. Extends that pattern to retrieval,
    where the injection is not merely unobservable but *rewrites the message
    array* (Claims 3, 8).
  - `docs-litellm-message-sanitization.md` (issue #1509, sibling page from the
    same crawl seed) — **Claim 8** ("The only documented signal that any of this
    happened is three `verbose_logger.debug` lines ... nothing appears in the
    response and no metric is named") and **Claim 1** (`modify_params=True` as
    the single global switch gating content mutations). The knowledge-base page
    is a *fourth* gateway message-mutation path with the same signature and no
    switch at all.
  - `docs-litellm-completion-input-params.md` — **Claim 3** ("The gate's scope
    is bounded by LiteLLM's own OpenAI-param recognition — any parameter it does
    not classify as an OpenAI param is assumed provider-specific and passed into
    the request body as a kwarg"). That is the mechanism which makes the two
    documented `vector_store_ids` shapes (Claim 12) behave differently: the
    `tools`-wrapped form is inside a recognised OpenAI param, the top-level form
    is not. **Claim 6** ("a `stop` list longer than 4 sequences is silently
    truncated ... a request-mutating behavior with no warning emitted") is the
    same silent-mutation class as the `Context:` injection.
- **Extends**:
  - `docs-litellm-completion-input-params.md` — **Claim 4**
    (`context_window_fallback_dict` fires only on a context-window error, where
    `fallbacks` fires on any call failure) and **Claim 13** (SDK-level
    `fallbacks` has no time budget, no loop, no cooldown; success carries
    `x-litellm-attempted-fallbacks`). Claim 5 here is a *third* substitution
    axis the same notes do not cover: retrieval state is scoped to a model
    alias, so a fallback chain's grounding is a function of which alias served
    the request — and grounding, unlike the responding model, leaves no trace in
    the response `model` field that Ch05 §"Silent model fallback breaks
    attribution" currently tells readers to check.
  - `blog-litellm-auto-router-v2.md` — **Claim 3** ("predictable beats clever for
    debuggability") and **Claim 1** (complexity/semantic/adaptive routing
    collapsed into one `auto_router/complexity_router`). Claim 5's hazard is the
    interaction: an alias carrying `vector_store_ids` inside a routed tier pool
    means the retrieval contract is a function of a routing decision the page
    never mentions. Under that note's own debuggability rationale, a
    vector-store-scoped alias is exactly the kind of config that makes "why was
    this answer grounded this time" unanswerable after the fact.
  - `docs-litellm-caching-all-caches.md` — **Claim 5** (the docs' own cache-key
    example composes `model + messages + temperature + log_bias`, with no
    user/tenant identity). Retrieval changes what `messages` contains at the
    gateway, and this note establishes that the cache key is derived from
    `messages`; the interaction between gateway-side context injection and
    response-cache keys is unaddressed by both pages.
  - `docs-litellm-bedrock-invoke.md` — **Claim 10** ("The `/invoke` route family
    is the config.yaml half of a two-mode Bedrock passthrough surface — model
    endpoints via config-registered `model_name` vs a 'direct passthrough'
    claiming ALL Bedrock endpoints for non-model services (guardrails,
    knowledge bases, agents)") and `docs-litellm-bedrock-converse.md` —
    **Claim 8** (the same two-mode statement). Both notes record that
    knowledge-base access existed on this gateway as an *undocumented-passthrough*
    surface and explicitly deferred it; this page is that deferred surface, and
    it shows the KB path is a first-class registry feature rather than a
    passthrough. No claim-level overlap — nothing here contradicts them.
  - `docs-litellm-a2a-cost-tracking.md` — **Claim 4** ("Configured agent cost
    lands in the gateway request log ... attributed to the API key that made the
    request"). This page adds the retrieval hop to the same log without adding
    it to any documented cost field; retrieved content's token cost lands in the
    request's `usage`, charged to the caller's key.
- **Novel**: The corpus has **no** record of gateway-side retrieval
  augmentation before this note — no claim in `registry/claims-index.json`
  mentions `vector_store_registry`, `vector_store_ids`, `vector_store_search_failures`,
  or `/vector_store/list`. Specifically new: (1) the registry-membership trigger
  (Claim 1); (2) last-message-only query derivation and its silent abort on a
  non-user final turn (Claim 2); (3) the `Context:` user-turn rewrite on the wire
  (Claim 3); (4) the out-of-band citation contract and its final-chunk-only
  streaming gate (Claim 4); (5) the model-alias "always on" default (Claim 5);
  (6) fail-open search behaviour and the hidden
  `vector_store_search_failures` channel (Claim 6); (7) guardrails scanning
  retrieved content (Claim 7); (8) the `file_search` tool being consumed by the
  gateway with all-or-nothing registry recognition (Claim 8); (9) the PG Vector
  connector's embedding path looping back through the proxy (Claim 10).
- **Dismissed candidates** (`miner-related-notes.md` suggestions that do not
  bear on this source):
  - `source-notes/docs-litellm-batches-api.md` — batch rate-limit accounting
    (`/v1/batches`); retrieval is not a batch path and the page says nothing
    about batches.
  - `source-notes/docs-litellm-audio-transcription.md` — transcription fallback
    and `mode: audio_transcription` routing; unrelated endpoint and no overlap
    beyond both being LiteLLM docs pages.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` — per-session A2A caps
    keyed on `x-litellm-trace-id`; a different subsystem. Adjacent only in that
    both are gateway-side limits keyed on something other than the request body.
  - `source-notes/docs-litellm-a2a-agent-card.md` — A2A card field-dropping
    matrix; no shared claim with retrieval.
  - `source-notes/docs-litellm-a2a-cost-tracking.md` — cited above under
    Extends; no claim-level corroboration beyond the shared log/cost surface.
- **Corroborates (internally inconsistent — filed)**: **contradiction #1517**,
  this source against itself on the `vector_store_ids` wire shape (Claim 12).

## Guide Impact

- **Chapter 05, §"Parameter migration hazards"**: add a subsection for
  *gateway-side message augmentation*. This source supplies the second
  documented instance (with `docs-litellm-message-sanitization.md`) of a gateway
  that changes what the model receives while the client sees an ordinary
  response. The concrete rule this source supports: audit gateway config for
  *request-mutating* features the way you audit model upgrades for unsupported
  parameters, because the blast radius is keyed on the model alias
  (`vector_store_ids` in `litellm_params`, Claim 5) and not on anything the
  caller sets. Also extend the existing audit checklist with the specific
  failure the page cannot answer: what a request does when the feature's
  preconditions are unmet (Claim 1 — silently nothing).
- **Chapter 05, §"Silent model fallback breaks attribution"**: the existing rule
  is "surface the `model` field from the response metadata — do not infer it from
  the request". This source shows a case the `model` field *cannot* cover: with
  an alias carrying `vector_store_ids`, a fallback onto or off that alias
  changes grounding without changing what the `model` check reports. Recommend a
  second, independent assertion: a request that is *expected* to be grounded must
  be verified grounded from `provider_specific_fields["search_results"]`, and
  grounding state must not be inferred from the model name or from the client's
  own request. Cross-reference the existing prompt-management substitution
  material already in that section — this is a third substitution authority on
  the same request path, and none of the three is visible in `model`.
- **Chapter 05, new subsection under §"Cost, capacity, and fallback patterns"**:
  a fail-open-by-default rule. This source's Claim 6 is the sharpest statement
  in the corpus of a retrieval dependency that degrades rather than fails: alert
  on the degradation signal (`vector_store_search_failures`) before alerting on
  answer quality, and know the knob that converts degradation into failure
  (`litellm.vector_store_search_failure_mode = "error"`, undocumented on the
  page) before you need it. This complements the existing §"Agent-loop cost caps
  fail open and expire" material — same class of finding, different subsystem.
- **Chapter 05, §"A guardrail in the request path is an availability
  dependency"**: extend with the *generated-input* case. Retrieved content is
  machine-fed into the guardrail layer (Claim 7), so the guardrail's input set
  is not what any human authored and not what any user can see; a document
  indexed months ago can block a chat, and guardrail masking silently changes
  the facts the model is grounded on. Recommend the existing section's rule be
  stated with "and the input to the guardrail may include content the caller
  never sent" rather than only the availability framing.
- **Chapter 02, §"The seven-kind span taxonomy"**: the taxonomy already has a
  `Retrieval` kind marked "Cannot be root" — this source is the concrete case
  that fills it from the *provider* side. The gateway performs the retrieval hop
  itself and its only stated visibility surface is a UI Logs page (Claim 11), no
  span and no metric. Recommend adding that a gateway-executed retrieval does
  not produce a client-side `Retrieval` span unless the gateway exports one, so
  a tracing setup that assumes client-side span capture will show a grounding
  change as an unexplained prompt-length difference. Cross-reference
  `docs-litellm-claude-code-context-management.md`'s treatment of injected
  context if the Smith wants the two unified.
- **Chapter 02, §"The observability model for LLM applications"**: add the
  citation-collection rule from Claim 4 — attribution data on streaming traffic
  exists only on the chunk whose `finish_reason == "stop"`, so citation
  collection must be final-chunk-aware and citation *absence* must be reported
  as ambiguous (retrieval-not-run vs stream-cut-short) rather than as a
  negative.
- **Chapter 06**: `GET /vector_store/list` (Claim 11) enumerates every
  reachable knowledge base together with `litellm_credential_name`, which is a
  credential-to-corpus map worth classifying; and retrieved content lands in the
  gateway's request logs (Claim 11, plus the page's own Logs-page statement),
  which is a data-governance surface for enterprise corpora. Neither is
  currently in the chapter.
- **Explicitly do not import**: the page's framing ("more accurate and
  contextually relevant responses"), and any reliability or performance claim.
  There is no measured latency, cost, or hit-rate anywhere on the page, so
  nothing here supports a statement about what gateway-side retrieval costs or
  how well it works.

## Extraction Notes

- Read in full on 2026-09-30 (HTTP 200, `docs.litellm.ai`, Docusaurus). Per
  §1 the page was followed into its two substantive linked sub-pages: the PG
  Vector connector repo (`github.com/BerriAI/litellm-pgvector`, deployment and
  configuration guide — read for the `.env` contract, which the page itself
  reproduces) and the parent guide index (`/docs/guides/retrieval_knowledge`),
  which contains no additional claims beyond this page. Provider-specific
  walkthroughs (Bedrock KB, Vertex AI RAG Engine, OpenAI Vector Stores) were
  read and deliberately **not** extracted beyond the support matrix: they are
  product UI click-through with no operational claim.
- The extraction is deliberately split into *page claims* (Claims 1–5, 9–12)
  and *page-silent, code-verified* claims (Claims 6–8, and the two halves of
  Claim 12). The code claims are attributed per-claim and are the reason
  `confidence_overall` is `emerging` rather than `settled`: they were read from
  `main` on 2026-09-30, not pinned to `v1.104.0-rc.2`, and could drift. An
  Assayer or human should re-pin before treating Claim 6 (the fail-open
  default) as settled — it is the highest-value claim in the note and the least
  vendor-documented.
- Contradiction **#1517** was filed before this PR (per §4a) rather than
  resolved here. Verdict deliberately not picked in this note. Worth noting for
  the resolver: the shipped code reads *both* documented shapes, so the issue is
  a documentation gap, not a broken feature — but the two shapes do not degrade
  identically (Claim 8), which is why it was filed rather than dismissed as a
  stylistic difference.
- Two same-page inconsistencies were noticed and are recorded here rather than
  filed separately, as neither would change guide advice on its own: the two
  different UI nav paths for the same object ("Experimental > Vector Stores" vs
  "Tools > Vector Stores", Claim 11), and the "Final Request to LiteLLM"
  caption on a payload that is the outbound model request (Claim 3). One
  same-page code/comment mismatch is also visible in the vendor's own source and
  is noted only as an observation, unverified and unfiled: in
  `pop_vector_stores_to_run_with_db_fallback` the comment reads "Tool params
  take precedence over existing params" while the code
  (`tool_params_dict.update(existing_params)`) gives the registry's own params
  precedence.
- Deliberately not extracted, per the Prospector's instruction: the marketing
  framing, and the provider-by-provider UI click-through steps. Also not
  extracted: the `litellm.com/docs` vs `docs.litellm.ai` URL inconsistency that
  appears in the `vector_store_metadata` examples, which is a copy-paste artifact
  with no operational content.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are either cited above or explicitly dismissed. No
  corroboration was inferred from a candidate that does not support it.
