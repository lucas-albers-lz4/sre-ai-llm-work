---
source_url: https://docs.litellm.ai/docs/mcp_tool_search
source_type: docs
title: "MCP Tool Search — LiteLLM Documentation (four virtual tools, keyword vs semantic ranking, and the embedding-dependency failure modes)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-11-08
last_checked: 2026-11-08
status: current
confidence_overall: settled
issue: "#1984"
---

# MCP Tool Search (LiteLLM Docs)

> LiteLLM's operational contract for collapsing a key's whole MCP catalog into
> four virtual tools: it replaces `tools/list` with a fixed dispatch surface,
> switches between token-substring and embedding ranking, and — in semantic
> mode — turns a failed `/embeddings` call or one oversized tool into a hard
> search outage rather than degrading to keyword ranking.

## Source Context

- **Type**: docs (official first-party LiteLLM/BerriAI vendor documentation,
  "MCP Tool Search", under MCP Gateway → Features, at
  `https://docs.litellm.ai/docs/mcp_tool_search`).
- **Author credibility**: LiteLLM documents its own proxy/MCP gateway. This is
  authoritative for the exposed config surface, defaults, version gates, and
  the access-control path it names (`_get_allowed_mcp_servers`,
  `filter_server_ids_by_ip`, `execute_mcp_tool`). It is vendor narrative for
  claims like "does not widen the access surface", which this note checks
  against the permission model rather than accepting outright.
- **Scope**: the per-key `mcp_tool_search_enabled` opt-in, the four virtual
  tools (`mcp_tool_search`, `mcp_tool_call`, `agent_search`, `skill_search`),
  keyword vs semantic ranking, the `litellm_settings.mcp_tool_search` block,
  the separate `/mcp/proxy` schema-discovery endpoint, runtime settings
  propagation, version prerequisites, and the page's comparison against the
  `/v1/responses` semantic filter. It does not document the underlying
  `object_permission` composition rules (that is `/docs/mcp_control`), spend-log
  plumbing (that is `/docs/mcp_cost`), or the A2A/skills registry internals.

## Extracted Claims

### Claim 1: With `mcp_tool_search_enabled` on a key, both `/mcp/` and `/mcp-rest/tools/list` return exactly four virtual tools regardless of catalog size; keys without the flag keep full-catalog behavior and are rejected if they call the virtual names
- **Evidence**: The "How it works" section names the four tools and both
  endpoints; the step-2 curl shows the exact four-name output; the paragraph
  after the Python SDK example states the unchanged path for keys without the
  flag. This is the rollback/blast-radius boundary.
- **Confidence**: settled
- **Quote**: "When `mcp_tool_search_enabled: true` is set on a key's `object_permission`, both the streamable-http endpoint (`/mcp/`) and the REST surface (`/mcp-rest/tools/list`) return exactly four tools regardless of how many MCP servers the key can reach:"
- **Our assessment**: This is the core contract and the thing to write into a
  runbook: enabling the flag is not an additive feature, it replaces the
  discovery surface for that key. The rollback path is per key (clear the flag),
  not per proxy, so a single key can be reverted without changing other
  tenants. The four-tool claim is version-gated (Claim 14): on old builds only
  the first two exist. The page later says "the two virtual tool names are
  rejected with a `forbidden` error" for keys without the flag — a stale
  "two" leftover from the original two-tool design, not a statement that
  `agent_search`/`skill_search` are exempt (see Extraction Notes).

### Claim 2: Keyword ranking is the default and has no embedding dependency; it scores tools by substring token overlap on name + description, so literal synonyms that share no token are missed
- **Evidence**: The "Ranking" subsection gives the exact algorithm — lowercase,
  whitespace split, substring count over lowercased name and description,
  zero-score tools dropped, ties keep catalog order, first `top_k` returned.
  The page's own `"FX"` vs `"foreign exchange"` example shows the recall gap.
- **Confidence**: settled
- **Quote**: "The proxy lowercases the query, splits it on whitespace, and scores each tool by how many query tokens appear as a substring of its lowercased name and description."
- **Our assessment**: This is the low-dependency default: no vector store, no
  embedding provider, no cold start. The cost is recall — the guide should not
  describe keyword mode as "semantic-lite". The substring rule also means short
  tokens can match inside unrelated words, so ranking quality depends heavily on
  tool naming discipline. The same `name + "\n" + description` text is used in
  semantic mode, so description quality is the only lever in both modes.

### Claim 3: Semantic ranking is selected by pointing `litellm_settings.mcp_tool_search.embedding_model` at a `model_list` entry, and adds cosine-similarity scoring, `similarity_threshold`, and a per-result `score` field
- **Evidence**: The "Semantic" paragraph and the field table define
  `embedding_model`, `top_k`, `similarity_threshold`, and `core_tools`, with
  defaults `null`, `5`, `0.0`, and `[]`. The config example shows the
  `model_list` entry plus the `mcp_tool_search` block.
- **Confidence**: settled
- **Quote**: "**Semantic (`embedding_model` set).** Point `embedding_model` at a `model_name` from your `model_list` and the proxy ranks by meaning instead."
- **Our assessment**: Semantic mode turns a gateway feature into a dependency on
  an embedding deployment; the page is explicit that `embedding_model` is a
  `model_name`, not a provider model id, so the embedding model must be routable
  through the same proxy. `similarity_threshold` defaults to `0.0`, which the
  page notes only drops negative scores — so the default is effectively "return
  top_k no matter how weak", and a threshold tuned for precision is an explicit
  operator choice. This matches the semantic-filter defaults split captured in
  `docs-litellm-mcp-semantic-filter.md` Claim 3.

### Claim 4: Semantic search fails closed on embedding errors — an embedding failure returns `isError: true` (`embedding the search query failed`) and does **not** fall back to keyword ranking
- **Evidence**: The "Semantic" paragraph states the error behavior explicitly;
  the page has no documented degradation path.
- **Confidence**: settled
- **Quote**: "If the embedding call fails, the search returns an error result (`isError: true`, text starting `embedding the search query failed`) instead of falling back to keyword ranking."
- **Our assessment**: This is the highest-value availability claim on the page.
  Configuring `embedding_model` replaces a zero-dependency default with a hard
  runtime dependency: an embedding-provider outage or misconfiguration takes
  tool discovery down for every semantic-mode key, and the proxy does not
  degrade to the mode that still works. For an SRE guide, treat keyword mode as
  the availability floor and semantic mode as the quality upgrade with an
  explicit failure policy. The error text is the runbook grep string.

### Claim 5: On builds before PR #43554 (v1.107.0-dev.2), one tool whose embedded text exceeds the model's input limit breaks **every** semantic search; newer builds drop that tool and skip re-embedding it for an hour
- **Evidence**: The paragraph after the field table gives the 8192-token
  OpenAI `text-embedding-3-*` limit, both version behaviors, and the
  `disallowed_tools`/unset workarounds.
- **Confidence**: settled
- **Quote**: "On builds that include [PR #43554](https://github.com/BerriAI/litellm/pull/43554) (v1.107.0-dev.2 and later) that tool is left out of semantic results, the rest of the catalog is still ranked, and the proxy skips re-embedding it for an hour. On earlier builds one oversized tool makes every semantic search fail with the embedding provider's input-too-long error."
- **Our assessment**: This is a fleet-wide single-point-of-failure caused by one
  upstream tool description. The failure is especially confusing because the
  error surfaces on searches for *other* tools, so incident response can chase
  the wrong server. The documented workaround (`disallowed_tools` on the
  offending server) depends on identifying the oversized tool; if the provider
  error does not name it, the operator has to bisect the catalog. Note that
  `disallowed_tools` is itself drift-prone (see Cross-References), so the
  workaround is a stopgap, not a durable control.

### Claim 6: Config validation is fail-open at boot — an invalid `mcp_tool_search` block (e.g. `top_k: 0`) lets the proxy start but fails every search, and `embedding_model` with an empty `model_list` also makes every search error
- **Evidence**: Two explicit sentences in the "Ranking"/settings prose and the
  `embedding_model` row in the field table.
- **Confidence**: settled
- **Quote**: "An invalid `mcp_tool_search` block (for example `top_k: 0`) does not stop the proxy from starting. Each search returns the validation error as an error result until the block is fixed."
- **Our assessment**: This is a classic "boots green, fails closed at request
  time" configuration risk. Readiness checks that only probe the proxy process
  will pass while tool search is 100% broken. The guide should recommend a
  synthetic `mcp_tool_search` probe, not just a health endpoint, when semantic
  mode is enabled. It also means a bad config rollout is not caught by startup
  validation — it is caught by callers.

### Claim 7: `core_tools` pins named tools to the front of every search without a score, does not consume `top_k`, and never grants access to a tool the caller cannot already reach
- **Evidence**: The `core_tools` field row plus the "hybrid mode" paragraph,
  including the omission rule and the empty-query behavior.
- **Confidence**: settled
- **Quote**: "A core tool the caller's key, team, or server permissions do not allow is omitted, so listing a tool here never grants access to it."
- **Our assessment**: This is a useful hybrid: keep a handful of high-frequency
  tools always visible while ranking the long tail. The security property is the
  important one — `core_tools` is a ranking preference, not an ACL grant. It
  inherits the existing permission intersection unchanged. Operationally, an
  empty query returns only the core list, which gives a cheap way to verify the
  pin set without depending on ranking quality.

### Claim 8: `top_k` is a narrowing-only cap — the call argument and the proxy setting take the smaller value — and core tools do not count against it
- **Evidence**: The `top_k` field row states the "smaller of the two wins" rule
  and excludes core tools from the count.
- **Confidence**: settled
- **Quote**: "Most ranked tools one search returns. The `top_k` argument on the `mcp_tool_search` call can narrow this but not widen it, since the smaller of the two wins. Core tools do not count against it."
- **Our assessment**: This prevents a caller from overriding an operator's
  catalog/response-size policy upward, which is the right default for cost and
  context control. It also means raising the proxy `top_k` does not by itself
  give callers more results if their client hardcodes a lower value — a common
  source of "the setting didn't take effect" confusion.

### Claim 9: Tool-search embeddings are cached in memory per process (up to 5000 vectors, LRU-evicted), each semantic search bills an `/embeddings` call to the calling key, and the cache is therefore per-pod rather than shared
- **Evidence**: The "Semantic" paragraph states the per-model, per-process
  cache, the 5000-vector cap, LRU eviction, and that the embedding call passes
  the same rate-limit/budget/guardrail hooks as `/embeddings`, is billed to the
  calling key, and appears in spend logs.
- **Confidence**: settled
- **Quote**: "Tool vectors are cached in memory per embedding model (up to 5000 vectors per process, least recently searched evicted first), so repeat searches over an unchanged catalog only embed the query."
- **Our assessment**: The "per process" wording is the operational catch: on an
  N-pod deployment there are N independent caches, so each pod pays the
  first-search embedding cost for the same catalog and cache warmth is uneven
  behind a load balancer. The cost model is also unusual — search is a
  billable embedding call attributed to the caller, not a free index lookup — so
  budget and rate-limit design must include tool discovery. The cache only
  avoids re-embedding *tools*; it never avoids the per-query embedding call.

### Claim 10: Tool-search settings can be changed at runtime via the Admin UI or `GET`/`PATCH` settings endpoints, are stored in the database, and propagate to every pod within about 10 seconds without a restart
- **Evidence**: The paragraph immediately before the `/mcp/proxy` section names
  both endpoints, the proxy-admin restriction, DB storage, and the ~10s
  fleet propagation.
- **Confidence**: settled
- **Quote**: "Values saved this way are stored in the database and picked up by every pod within about 10 seconds, with no restart."
- **Our assessment**: For runbooks this is a live, fleet-wide change surface: a
  bad `embedding_model` or `top_k` update propagates to all pods in seconds,
  with no deploy gate and no restart (and, per Claim 6, no boot-time validation).
  The compensating control is the `PATCH` audit trail and admin-only restriction,
  not a staged rollout. This is a strong argument for treating tool-search
  config as production-change-managed even though it is "just settings".

### Claim 11: `default_key_generate_params.object_permission` merges into `/key/generate` requests that omit the field; a partial `object_permission` keeps its explicit fields and only fills unset ones, and the merge runs after caller-scope validation
- **Evidence**: The "Enable as a default for every new key" section, its
  `config.yaml` example, and the paragraph explaining merge order.
- **Confidence**: settled
- **Quote**: "The default is merged **after** the caller-scope validation runs, so it never turns an ordinary non-admin personal-key request into a 403."
- **Our assessment**: This is a safe-default mechanism worth recommending for
  fleets that want tool search on by default: the admin default cannot
  retroactively escalate a request's scope, and an explicit partial
  `object_permission` is respected. The distinction between "omitted" and
  "partial" is subtle but matters — a caller that sets only `mcp_servers` still
  inherits the default `mcp_tool_search_enabled`, so the default is closer to an
  opt-out than an opt-in once configured.

### Claim 12: `/mcp/proxy` is a separate always-available streamable-http surface exposing three meta-tools (`search_tools`, `get_tool_schema`, `call_tool`), keyed by opaque 32-character `tool_id`s, independent of `mcp_tool_search_enabled`, and tools-only
- **Evidence**: The `/mcp/proxy` section defines the three tools, the opaque
  hash, the stability and authorization behavior, schema validation before
  dispatch, and the tools-only limitation.
- **Confidence**: settled
- **Quote**: "`/mcp/proxy` is a separate streamable-http MCP endpoint for clients that should discover tools and fetch schemas one at a time instead of loading the full catalog. Unlike the virtual tools above, it does not depend on `mcp_tool_search_enabled`."
- **Our assessment**: This is a distinct surface, not another name for the
  four-tool mode, and its independence from the flag means an operator cannot
  "turn it off" with the same switch. The `tool_id` is an opaque hash, not a
  capability token — the page says it only resolves for keys that can reach the
  tool — so it should not be logged as an access grant or reused across keys.
  Schema validation before dispatch is a real protection for clients that would
  otherwise send malformed arguments straight upstream. Prompts/resources
  returning `METHOD_NOT_FOUND` means this endpoint is not a general MCP proxy.

### Claim 13: The page asserts tool search does not widen the access surface, and the documented dispatch path supports it — search walks the filtered catalog and calls re-run allowed-server resolution, IP filtering, and `execute_mcp_tool`
- **Evidence**: The "Access control" section names the same filtered catalog as
  `tools/list`, then `_get_allowed_mcp_servers`, `filter_server_ids_by_ip`, and
  `execute_mcp_tool` for calls; the 403 example confirms the out-of-scope
  rejection is the same guard as direct calls.
- **Confidence**: emerging (vendor assertion with a named code path, but no
  independent test or audit)
- **Quote**: "Tool search does not widen the access surface. `mcp_tool_search` walks the same filtered catalog the normal `tools/list` handler uses, so a tool the key cannot reach is invisible to search."
- **Our assessment**: The claim is consistent with the six-level permission
  intersection in `docs-litellm-mcp-control.md` Claim 1 and the tool-level
  `mcp_tool_permissions` model in Claim 7. The important nuance for the guide is
  "discovery equals authorization" only because dispatch re-checks; search
  itself is not an authorization step. That means a compromised or buggy
  `mcp_tool_search` response cannot by itself grant a call, but the page is still
  a vendor self-assessment — the guide should cite the named guard path and
  recommend an authorization test, not repeat "does not widen" as settled fact.

### Claim 14: Version floors: tool search since v1.92.0; semantic ranking, `similarity_threshold`, `core_tools`, and `/mcp/proxy` since v1.102.0
- **Evidence**: The "Prerequisites" section states both gates and the
  `model_list` requirement, and says no extra Python dependency is needed.
- **Confidence**: settled
- **Quote**: "Tool search works Since v1.92.0. Semantic ranking, `similarity_threshold`, `core_tools`, and `/mcp/proxy` work Since v1.102.0."
- **Our assessment**: The version floor is not optional context because the
  oversized-tool failure mode (Claim 5) is itself build-dependent
  (v1.107.0-dev.2). Any guide advice pairing semantic ranking with an oversized
  catalog must state all three versions, or a reader on an older build will hit
  a fleet-wide search outage the page says is fixed "later".

### Claim 15: Tool search and the semantic filter are different layers: tool search is an MCP-layer per-key opt-in that hands discovery to the LLM, while the semantic filter rewrites tool lists on `/v1/responses` and `/v1/chat/completions`; they coexist but tool search keys still expose only the four virtual tools
- **Evidence**: The final "When to use tool search vs. semantic filter" section
  contrasts the layers and states the coexistence behavior.
- **Confidence**: settled
- **Quote**: "They can coexist; a key with tool search on will only expose the four virtual tools even when semantic filtering is enabled upstream."
- **Our assessment**: This is the positioning claim the guide needs so the two
  features are not presented as interchangeable fixes for "tool catalog
  blowout". The practical consequence is compositional: enabling the semantic
  filter upstream does not restore a full tool list to a tool-search key, so
  operators should pick the layer that matches the client (MCP-native agents vs
  chat-completions callers) and test the combination rather than assume they
  stack.

## Concrete Artifacts

### Key generation enabling tool search (verbatim from "Quick start")
```bash
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "object_permission": {
      "mcp_tool_search_enabled": true,
      "mcp_servers": ["github", "slack"]
    }
  }'
```

### `tools/list` collapse (verbatim from step 2)
```text
$ curl -s http://localhost:4000/mcp-rest/tools/list \
    -H "Authorization: Bearer $KEY" | jq '[.tools[].name]'
["mcp_tool_search", "mcp_tool_call", "agent_search", "skill_search"]
```

### Search then call (verbatim from steps 3–4)
```text
$ curl -s -X POST http://localhost:4000/mcp-rest/tools/call \
    -H "Authorization: Bearer $KEY" \
    -d '{"name":"mcp_tool_search","arguments":{"query":"add numbers"}}' \
  | jq -r '.content[0].text | fromjson | [.[].name]'
["math-add", "math-multiply"]
```

```text
$ curl -s -X POST http://localhost:4000/mcp-rest/tools/call \
    -H "Authorization: Bearer $KEY" \
    -d '{"name":"mcp_tool_call","arguments":{"tool_name":"math-add","arguments":{"a":3,"b":4}}}' \
  | jq '{result: .content[0].text, isError}'
{
  "result": "7",
  "isError": false
}
```

### Default-for-all-new-keys config (verbatim from "Enable as a default for every new key")
```yaml
litellm_settings:
  default_key_generate_params:
    object_permission:
      mcp_tool_search_enabled: true
      mcp_servers: ["github", "slack"]
```

### Semantic ranking config (verbatim from "Ranking")
```yaml
model_list:
  - model_name: text-embedding-3-small
    litellm_params:
      model: openai/text-embedding-3-small
      api_key: os.environ/OPENAI_API_KEY
litellm_settings:
  mcp_tool_search:
    embedding_model: text-embedding-3-small  # unset = keyword ranking
    top_k: 5
    similarity_threshold: 0.2
    core_tools:
      - treasury-get_rates
```

### Settings field table (verbatim rows)
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `embedding_model` | string | `null` | A `model_name` from `model_list` used to rank tools by meaning. Unset keeps keyword ranking. Setting it on a proxy with no `model_list` makes every search return an error. |
| `top_k` | integer, 1 to 100 | `5` | Most ranked tools one search returns. The `top_k` argument on the `mcp_tool_search` call can narrow this but not widen it, since the smaller of the two wins. Core tools do not count against it. |
| `similarity_threshold` | float, 0.0 to 1.0 | `0.0` | Lowest cosine similarity a tool needs to appear in semantic results. The default `0.0` only drops tools with a negative similarity. Ignored in keyword mode. |
| `core_tools` | list of strings | `[]` | Tool names, in the `server-tool` form that `tools/list` shows, returned first on every search without a score. |

### `/mcp/proxy` meta-tools (verbatim table)
| Tool | Arguments | Returns |
|------|-----------|---------|
| `search_tools` | `query` | Up to 5 matching tools as `{tool_id, name, description}`, plus `score` in semantic mode. No input schemas. |
| `get_tool_schema` | `tool_id` | The tool's `tool_id`, `name`, `description`, `inputSchema`, and `outputSchema` when the upstream server declares one. |
| `call_tool` | `tool_id`, `arguments` | The upstream tool result, after `arguments` is validated against the tool's `inputSchema`. |

### Out-of-scope call rejection (verbatim from "Access control")
```text
$ curl -s -X POST http://localhost:4000/mcp-rest/tools/call \
    -H "Authorization: Bearer $KEY" \
    -d '{"name":"mcp_tool_call","arguments":{"tool_name":"secret-server-delete_all","arguments":{}}}'
{"detail":"User not allowed to call this tool. Allowed MCP servers: [math]"}
```

### Prerequisites (verbatim)
```text
Tool search works Since v1.92.0. Semantic ranking, `similarity_threshold`, `core_tools`, and `/mcp/proxy` work Since v1.102.0. Semantic ranking, `similarity_threshold` and `core_tools` also need an embedding model in `model_list`. None of it needs an extra Python dependency.
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-control.md` Claim 1 (permission composition
    across six levels, most-restrictive-wins/org-as-ceiling) and Claim 7 (tool
    level `mcp_tool_permissions` intersected the same way) — the access-control
    path in Claim 13 above is a reused instance of that model, not a new
    permission layer.
  - `source-notes/blog-litellm-save-claude-code-costs.md` Claim 5 — the blog's
    "no embedding dependency" and "access surface does not widen" statements are
    the keyword-mode/two-tool version of Claims 2 and 13 here.
- **Contradicts**: none filed. The page's "does not widen the access surface"
  claim and the semantic-filter note's disputed fail-open claim are about
  different features (tool search fails closed on embedding errors; the filter
  page's fail-open statement is already contradicted in
  `docs-litellm-mcp-semantic-filter.md` Claim 7). No new contradiction issue is
  warranted.
- **Extends**:
  - `source-notes/blog-litellm-save-claude-code-costs.md` Claim 4 — the blog's
    "two virtual tools" (`mcp_tool_search`, `mcp_tool_call`) is superseded by
    this page's four-tool contract. The blog remains the token-cost motivation;
    this note is the current accuracy source.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` Claim 8 and its Concrete
    Artifacts "Registry search wiring" — `agent_search` surfaced as an MCP
    virtual tool when `mcp_tool_search_enabled: true` is the same feature from
    the A2A side; this note adds the catalog-collapse and ranking semantics.
  - `source-notes/docs-litellm-mcp-cost-tracking.md` Claim 9 — the spend-log
    `LiteLLM_SpendLogs`/`call_type` plumbing is where the billed `/embeddings`
    calls from Claim 9 above land.
  - `source-notes/docs-litellm-mcp-semantic-filter.md` Claim 2 and Claim 4 — the
    filter is the other layer in Claim 15: global vs per-key, `/v1/responses`
    and `/v1/chat/completions` vs `/mcp/`, fail-open (disputed) vs fail-closed.
  - `source-notes/docs-litellm-mcp-rest-api.md` Claim 8 — `/mcp-rest/tools/list`
    is the REST listing this page replaces with four virtual tools for flagged
    keys.
  - `source-notes/docs-litellm-mcp-deployment.md` Claim 2 — the recommended
    single-instance topology is the multi-pod context in which Claim 9's
    per-process cache is not shared.
  - `source-notes/docs-litellm-mcp-linear-server.md` Claim 3 — the documented
    oversized-tool workaround uses server-level `disallowed_tools`, whose
    fail-silent drift on renamed upstream tools is captured there; the workaround
    can silently stop protecting once the tool name changes.
- **Novel**: the four-virtual-tool catalog-collapse contract as its own subject;
  the embedding-failure availability cliff in semantic mode; the
  one-oversized-tool fleet-wide failure and its version gate; `core_tools` and
  `top_k` narrowing-only semantics; per-process vector caching and per-query
  embedding billing; runtime fleet-wide settings propagation; and the
  `/mcp/proxy` opaque-`tool_id` schema-discovery surface.

## Guide Impact

- **Ch05 (LLM Ops Reliability)**: add a runbook subsection for
  `litellm_settings.mcp_tool_search`. State the failure chain: semantic mode
  depends on `/embeddings`; an embedding failure returns `isError: true` with
  `embedding the search query failed` and does not degrade to keyword ranking
  (Claim 4); invalid config boots green and fails per search (Claim 6); one
  oversized tool breaks all semantic searches before v1.107.0-dev.2 (Claim 5).
  Recommend keyword mode as the availability floor, a synthetic tool-search
  probe instead of a process health check, and pinning the version floor from
  Claim 14 before enabling semantic ranking.
- **Ch05/Ch06 (cost and change control)**: note that each semantic search bills
  an `/embeddings` call to the calling key, passes rate-limit/budget/guardrail
  hooks, and that tool vectors are cached per process (Claim 9) — so fleet cost
  and cache warmth scale with pod count, and canary rollouts do not share caches.
  Document that `PATCH /update/mcp_tool_search_settings` is a live fleet-wide
  change within ~10s with no restart (Claim 10), so it needs the same change
  control as a deploy.
- **Ch06 (Security and Trust)**: present tool search as inheriting the existing
  permission model, not extending it. Cite `docs-litellm-mcp-control.md` Claim 1
  and Claim 7 plus the dispatch path in Claim 13. Add two cautions: `core_tools`
  listing never grants access (Claim 7), and `/mcp/proxy` `tool_id`s are opaque
  hashes, not capability tokens, and the endpoint is independent of
  `mcp_tool_search_enabled` (Claim 12) — so disabling the per-key flag does not
  remove that surface. Recommend an authorization test rather than repeating the
  vendor's "does not widen" claim as fact.
- **Ch03 (Runbooks and Agents)**: when an agent framework speaks MCP end to end,
  document the four-tool catalog collapse (Claim 1) and `core_tools` pinning
  (Claim 7) as the supported pattern; keep the `/v1/responses` semantic filter as
  a separate layer for chat-completions callers (Claim 15) instead of presenting
  the two as interchangeable.

## Extraction Notes

- Read the full page plus its in-page sections (Quick start, default-key
  merging, How it works/Ranking, `/mcp/proxy`, Prerequisites, Access control,
  tool search vs semantic filter). Did not follow external sub-pages; the
  related `/docs/a2a`, `/docs/skills`, `/docs/mcp_control`, `/docs/mcp_semantic_filter`,
  and PR #43554 links were used only to place the claims already stated on this
  page.
- The page has one internal wording inconsistency: after documenting four
  virtual tools, it says "the two virtual tool names are rejected with a
  `forbidden` error" for keys without the flag. I read this as a stale "two"
  from the original design (the two original tools are `mcp_tool_search` and
  `mcp_tool_call`), not as a fifth behavior. It does not change the guide
  advice and is not a contradiction issue because there is no conflicting
  operational recommendation.
- `date_published` is unknown; this is living vendor documentation. The
  version floors in Claim 14 are the effective date anchors.
- Related-notes candidates reviewed and dispositioned:
  - `docs-litellm-mcp-linear-server.md` — cited (Extends; `disallowed_tools`
    workaround drift).
  - `docs-litellm-mcp-deployment.md` — cited (Extends; multi-pod context for
    per-process cache).
  - `docs-litellm-completion-web-search.md` — dismissed: provider-native web
    search on completions, no MCP tool-catalog overlap.
  - `docs-litellm-batches-api.md` — dismissed: batch submission/rate-limit
    accounting, unrelated to tool search.
  - `docs-litellm-mcp-zero-trust.md` — dismissed: outbound JWT signing for MCP
    calls, orthogonal to catalog discovery.
  - `docs-litellm-evals-api.md` — dismissed: Evaluations API surface, unrelated.
  - `docs-litellm-generate-content.md` — dismissed: Google-native generation
    passthrough, unrelated.
  - `docs-litellm-completion-web-fetch.md` — dismissed: Anthropic web-fetch
    tool, unrelated.
  - `docs-litellm-enterprise.md` — dismissed: licensing/SSO/audit tier, no
    tool-search detail beyond admin roles already covered by Claim 10.
  - `docs-langfuse-mcp-server.md` — dismissed: a specific docs MCP server, not
    the gateway's tool-search feature.
- No contradiction issue filed (see Cross-References).
