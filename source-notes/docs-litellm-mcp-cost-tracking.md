---
source_url: https://docs.litellm.ai/docs/mcp_cost
source_type: docs
title: "MCP Cost Tracking — LiteLLM AI Gateway Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; front-matter last_updated 2026-10-29)
date_extracted: 2026-10-29
last_checked: 2026-10-29
status: current
confidence_overall: emerging
issue: "#1919"
---

# MCP Cost Tracking (LiteLLM Docs)

> LiteLLM exposes a **third cost-attribution axis** — MCP *tool* calls — with
> exactly two documented pricing paths: a static, operator-declared price in
> `config.yaml` (`mcp_server_cost_info.default_cost_per_query` plus a per-tool
> override map), or a custom `async_post_mcp_tool_call_hook` that sets
> `response_obj.hidden_params.response_cost`. The hook's value is real: it is
> copied into `model_call_details["response_cost"]`, appears in the standard
> logging payload, and lands in the same `LiteLLM_SpendLogs` table as
> completion spend under `call_type = 'call_mcp_tool'`. But both paths price a
> **declared charge**, not a measured upstream cost, and an unpriced tool call
> silently logs `0.0` with no error and no page-documented warning.

## Source Context

- **Type**: docs — official LiteLLM (BerriAI) vendor documentation, living
  Docusaurus page under "MCP Gateway → Features". The page's own markdown
  endpoint (`/docs/mcp_cost.md`) reports `last_updated: "2026-10-29"` and two
  related pages (`/docs/proxy/tool_policies`, `/docs/mcp_guardrail`).
- **Author credibility**: First-party product documentation. Authoritative for
  the documented configuration surface and the hook signature; it publishes no
  measured overhead, no failure-mode statement, and no version pin. Behavior
  claims below were therefore checked against the LiteLLM source (see
  Extraction Notes) rather than treated as guaranteed by the page.
- **Scope**: Two cost methods for MCP tool calls — config-based fixed pricing
  and a custom post-call hook — plus a registration snippet and a three-step
  "what the hook will do" list. It does **not** cover: spend-log schema or
  attribution target, per-key/team budgets, reconciliation with upstream
  provider cost, token-based MCP pricing, or failure behavior when a tool is
  missing from the price map. Those gaps are where this note does its
  verification work.
- **Page size**: Very thin — roughly one screen of prose plus four code
  blocks. The page is a pointer to a surface, not a reference; most operational
  conclusions here come from pairing it with the implementation.

## Extracted Claims

### Claim 1: LiteLLM documents exactly two ways to cost MCP tool calls — config-based fixed costs per tool/server, or a custom post-MCP hook for "dynamic" cost logic — and documents no measured/usage-based path
- **Evidence**: The opening table names the two methods, their "when to use",
  and their effect. No third row, no token/usage pricing, no provider-invoice
  import.
- **Confidence**: settled (the page explicitly enumerates the surface; the
  absence of a measured path is a verified full-page absence)
- **Quote**: "LiteLLM provides two ways to track costs for MCP tool calls:"
- **Our assessment**: This is the load-bearing scope statement. The word
  "dynamic" in the hook row is easy to over-read: the hook lets an operator run
  arbitrary Python, but it still produces a number the operator chose or
  computed. Nothing on the page ties either path to measured upstream spend,
  token usage, or tool execution time. That makes MCP a third cost axis
  alongside completion-token cost and A2A agent cost, with the same
  declared-vs-measured distinction the corpus already records for A2A
  (see Cross-References → `docs-litellm-a2a-cost-tracking.md` Claim 3).

### Claim 2: The config path places prices at `mcp_servers.<name>.mcp_info.mcp_server_cost_info`, with `default_cost_per_query` for the whole server and a `tool_name_to_cost_per_query` map for per-tool overrides
- **Evidence**: The page's `config.yaml` block shows both fields nested under
  `mcp_info.mcp_server_cost_info` on two servers, with inline comments
  distinguishing the default from the per-tool override. The implementation
  reads the same nested key from the server's `mcp_info` and types it as
  `MCPServerCostInfo` (`litellm/types/mcp.py`).
- **Confidence**: settled (documented schema, confirmed by the code path)
- **Quote**: "Configure fixed costs for MCP servers directly in your config.yaml:"
- **Our assessment**: This is a materially better IaC story than the A2A cost
  panel, which the corpus records as Admin-UI-only
  (`docs-litellm-a2a-cost-tracking.md` Claim 7): MCP prices are reviewable
  YAML, so they can live in the same change process as the server registration.
  The schema is per *server*, not per *tool definition* — a tool rename or a
  server-alias change can orphan the price without touching the cost block
  (see Claim 6).

### Claim 3: Precedence is per-tool override → server default → `0.0`; the page only implies it through comments, while the implementation and unit tests state it explicitly
- **Evidence**: The implementation checks membership in
  `tool_name_to_cost_per_query` first, then falls back to
  `default_cost_per_query`, then returns `0.0`. Unit tests assert
  `0.05` (tool-specific) beats `0.01` (default), and that a missing tool with a
  default yields the default. The page's comments say "Default cost for all
  tools in this server" and "Custom cost for specific tools" but never state
  which wins.
- **Confidence**: settled (code + tests; the page's implication is consistent)
- **Quote**: (no direct quote; the page states no precedence sentence — see
  paraphrase in Our assessment)
- **Our assessment**: The precedence is the sane one, and the unit tests make
  it safe to rely on at the tested version. The documentation gap matters
  because an operator reading only the page could reasonably ask whether the
  default also applies on top of the per-tool price. It does not: one price per
  call, per-tool first. Record the tested version when you depend on this;
  the guide has no LiteLLM version pin, and this note verified `main`, not a
  released tag.

### Claim 4: The custom hook is a `CustomLogger` subclass implementing `async_post_mcp_tool_call_hook`, registered under `litellm_settings.callbacks`, that sets `response_obj.hidden_params.response_cost` and returns the response object
- **Evidence**: The page gives the full class, the assignment line, and the
  registration YAML. The implementation's callback loop passes each
  `CustomLogger` an `MCPPostCallResponseObject` and reads the returned object's
  `hidden_params`.
- **Confidence**: settled (documented contract, confirmed by implementation and
  a unit test)
- **Quote**: "response_obj.hidden_params.response_cost = custom_cost"
- **Our assessment**: The Prospector flagged this shape as possibly an
  unreviewed sketch because response objects elsewhere expose a private
  `_hidden_params`. Here the public field is real: `MCPPostCallResponseObject`
  declares `hidden_params: HiddenParams`, and `HiddenParams` declares
  `response_cost: float | None`. The implementation writes
  `response.hidden_params.response_cost` into
  `model_call_details["response_cost"]`, and a unit test asserts a hook-set
  `1.42` reaches the standard logging payload. So this is not a contradiction
  with the code — the page's core contract holds at current `main`.

### Claim 5: A hook-set cost takes precedence over the configured price, and because the check is `is not None`, a hook that sets `0.0` silently disables the configured per-tool price
- **Evidence**: `MCPCostCalculator.calculate_mcp_tool_call_cost` returns
  `model_call_details["response_cost"]` immediately when it is not `None`,
  before reading `mcp_server_cost_info`. `0.0` is not `None`, so it short-
  circuits the config path.
- **Confidence**: settled (direct code read; the zero path is not covered by
  the page or by the cost-calculator unit tests)
- **Quote**: (no direct quote; the page documents no override or zero-value
  semantics — see paraphrase in Our assessment)
- **Our assessment**: This is the sharpest operational footgun on the surface.
  A hook intended to mean "this call is free" (or a buggy calculation that
  produces `0.0`) overrides a correctly configured per-tool price, and the
  spend row will say zero. There is no warning, no clamp, and no page
  documentation of the interaction. If both paths are configured, treat the
  hook as the authoritative price for every successful call it touches, and
  test the zero case deliberately.

### Claim 6: When neither a hook cost nor a matching config price exists, the MCP cost calculator returns `0.0` — the call succeeds and logs zero spend with no error, and the page documents no warning
- **Evidence**: The calculator's final statement returns `cost_per_query`,
  initialized to `0.0`; unit tests assert `0.0` for empty metadata, an empty
  `mcp_server_cost_info`, and a `None` logging object. The calculator has no
  logging branch of its own. The page's only assurance is the table phrase
  "Automatically tracks costs based on configuration".
- **Confidence**: settled for the code behavior; the page is silent on the
  zero default
- **Quote**: "Automatically tracks costs based on configuration"
- **Our assessment**: "Tracks" here means "writes a spend row", not "detects
  that the price is missing". A renamed tool, a renamed server alias, or a
  server whose `mcp_info` lost its cost block drops the price to zero with no
  request-path error and no page-documented signal. That is the same
  silent-zero class as the model-cost-map incident
  (`failure-litellm-model-cost-map-silent-fallback.md`, Symptom 2: cost
  tracking silently returned `cost=0`), now on the MCP tool path. The guide
  should not let "cost tracking is enabled" stand in for "this tool has a
  price that matches its current name".

### Claim 7: Config-based MCP pricing is an operator-declared per-query price, not a measurement of upstream tool cost — no documented linkage to token usage, provider invoice, or execution duration
- **Evidence**: Every config value is a fixed dollar amount
  (`default_cost_per_query: 0.01`, `send_email: 0.05`,
  `default_cost_per_query: 1.50`); the implementation returns that static value
  per call and reads no usage, duration, or upstream-cost field. The page never
  claims the figure is derived.
- **Confidence**: emerging (vendor-documented configuration semantics; the
  "declared, not measured" framing is our synthesis of the page and code, not a
  vendor claim)
- **Quote**: "Simple cost tracking with fixed costs per tool/server"
- **Our assessment**: This is the same gap the A2A note found for per-agent
  cost: a "Cost Per Query" field in an accounting context implies measurement,
  but a fixed per-query number is a pricing declaration. It is legitimate for
  chargeback and showback — the caller can be billed a known amount — but it is
  not a cost-accuracy instrument. The number drifts from reality as upstream
  provider prices, tool latency, or tool fan-out change, and neither the page
  nor the code documents a reconciliation. The custom hook can compute
  something better, but only from inputs the operator supplies; it does not
  make the gateway measure the upstream.

### Claim 8: A custom cost hook that raises is swallowed by the logging path — the request still succeeds and the cost silently falls back to config or zero
- **Evidence**: The callback loop wraps each hook call in `try/except
  Exception`, logs the exception through `verbose_logger.exception`, and
  continues with `hook_content = None`. The MCP call returns normally.
- **Confidence**: settled (direct code read)
- **Quote**: (no direct quote; the page documents no failure behavior — see
  paraphrase in Our assessment)
- **Our assessment**: Non-blocking logging is the right availability trade-off,
  but it makes cost fidelity a best-effort property. A syntax error, a missing
  attribute, or a provider timeout inside the hook produces a successful tool
  call with the wrong (or zero) price, visible only in proxy logs. This is a
  Ch02 monitoring problem: the absence of errors on the request path says
  nothing about whether the cost hook ran.

### Claim 9: MCP tool-call spend lands in the same `LiteLLM_SpendLogs` table as completion spend, discriminated by `call_type` (`call_mcp_tool` / `list_mcp_tools`), and session aggregation exposes `mcp_tool_call_spend = SUM(spend)`
- **Evidence**: The spend-management queries define
  `_MCP_CALL_TYPES_SQL = "('call_mcp_tool', 'list_mcp_tools')"` and compute
  `mcp_tool_call_spend` by summing `spend` filtered to those call types from
  `"LiteLLM_SpendLogs"`. The standard logging test asserts the hook-set cost
  reaches the payload's `response_cost`.
- **Confidence**: settled (code + unit test)
- **Quote**: (no direct quote; the page says only "Track costs in LiteLLM's
  logging system" — see paraphrase in Our assessment)
- **Our assessment**: This answers the Prospector's question directly: the
  hook's return value is not overwritten downstream. It becomes
  `model_call_details["response_cost"]`, survives into the standard logging
  payload, and is written to the same spend table as completion cost. The
  practical consequence is good: one spend ledger can carry both token cost and
  tool cost, and a `call_type` filter separates them. The caveat is that
  `list_mcp_tools` is included in the MCP spend aggregate even though only
  `call_mcp_tool` goes through the MCP cost calculator, so an operator summing
  the aggregate is summing tool-call charges plus any listing-call charges
  recorded on that path.

### Claim 10: The page's hook sample is illustrative rather than executable as a cost recipe — `custom_cost = 42.00` is a literal placeholder, and the sample reads `kwargs.get("name")` / `kwargs.get("server_name")` without documenting that the built-in calculator keys the tool off `mcp_tool_call_metadata["name"]`
- **Evidence**: The sample assigns `custom_cost = 42.00` and reads the two flat
  kwargs keys. The implementation passes `kwargs=logging_obj.model_call_details`
  to the hook and sets the tool identity under
  `model_call_details["mcp_tool_call_metadata"]["name"]`; the built-in
  calculator reads `mcp_tool_call_metadata.get("name", "")`. The page never
  documents the metadata layout.
- **Confidence**: settled as a documentation finding (page + implementation
  both read this session); whether a flat `name` key is also present in
  `model_call_details` is not documented on the page and is not asserted here
- **Quote**: "Extract tool information from kwargs"
- **Our assessment**: The sample is a shape demo, not a working pricing recipe.
  The `42.00` placeholder is obvious; the metadata path is the subtler trap,
  because a custom hook that copies the sample may key its logic off a field
  the built-in path does not use for cost lookup. The robust pattern is to
  read the nested `mcp_tool_call_metadata` (and its `namespaced_tool_name`) and
  to log the key you matched, so a rename shows up as a mismatch instead of a
  silent zero. This is a doc-quality finding, not a contradiction with the
  code — the page's cost assignment contract (Claim 4) is correct.

## Concrete Artifacts

### Config-based pricing (verbatim from `https://docs.litellm.ai/docs/mcp_cost.md`)

```yaml
mcp_servers:
  zapier_server:
    url: "https://actions.zapier.com/mcp/sk-xxxxx/sse"
    mcp_info:
      mcp_server_cost_info:
        # Default cost for all tools in this server
        default_cost_per_query: 0.01
        # Custom cost for specific tools
        tool_name_to_cost_per_query:
          send_email: 0.05
          create_document: 0.03
          
  expensive_api_server:
    url: "https://api.expensive-service.com/mcp"
    mcp_info:
      mcp_server_cost_info:
        default_cost_per_query: 1.50
```

### Custom post-MCP hook (verbatim from the page, including the placeholder)

```python
from typing import Optional
from litellm.integrations.custom_logger import CustomLogger
from litellm.types.mcp import MCPPostCallResponseObject

class CustomMCPCostTracker(CustomLogger):
    """
    Custom handler for MCP cost tracking and response modification
    """
    
    async def async_post_mcp_tool_call_hook(
        self, 
        kwargs, 
        response_obj: MCPPostCallResponseObject, 
        start_time, 
        end_time
    ) -> Optional[MCPPostCallResponseObject]:
        """
        Called after each MCP tool call. 
        Modify costs and response before returning to user.
        """
        
        # Extract tool information from kwargs
        tool_name = kwargs.get("name", "")
        server_name = kwargs.get("server_name", "")
        
        # Calculate custom cost based on your logic
        custom_cost = 42.00
        
        # Set the response cost
        response_obj.hidden_params.response_cost = custom_cost
        
  
      
        return response_obj
    

# Create instance for LiteLLM to use
custom_mcp_cost_tracker = CustomMCPCostTracker()
```

### Registration (verbatim from the page)

```yaml
litellm_settings:
  callbacks:
    - custom_mcp_hook.custom_mcp_cost_tracker
```

### What the hook is documented to do (verbatim from the page)

```
1. Calculate costs based on your custom logic
2. Modify the response if needed
3. Track costs in LiteLLM's logging system
```

### Code verification: cost precedence and the silent-zero default

Attributed to `BerriAI/litellm` `main` at commit `e93e01ca4b66b8a675da0af25193b50e6bb65a91`
(fetched 2026-10-29), file `litellm/proxy/mcp_server/cost_calculator.py`:

```python
        #########################################################
        # Get the response cost from logging object model_call_details
        # This is set when a user modifies the response in a post_mcp_tool_call_hook
        #########################################################
        response_cost: Final = litellm_logging_obj.model_call_details.get("response_cost", None)
        if response_cost is not None:
            return response_cost

        #########################################################
        # User defined cost per query
        #########################################################
        default_cost_per_query: Final = mcp_server_cost_info.get("default_cost_per_query", None)
        tool_name_to_cost_per_query: Final = mcp_server_cost_info.get("tool_name_to_cost_per_query", {}) or {}
        tool_name: Final = mcp_tool_call_metadata.get("name", "")

        #########################################################
        # 1. If tool_name is in tool_name_to_cost_per_query, use the cost per query
        # 2. If tool_name is not in tool_name_to_cost_per_query, use the default cost per query
        # 3. Default to 0.0 if no cost per query is found
        #########################################################
        cost_per_query: float = 0.0
        if tool_name in tool_name_to_cost_per_query:
            cost_per_query = tool_name_to_cost_per_query[tool_name]
        elif default_cost_per_query is not None:
            cost_per_query = default_cost_per_query
        return cost_per_query
```

### Code verification: the hook value reaches `model_call_details`

Attributed to the same commit, file
`litellm/litellm_core_utils/litellm_logging.py`:

```python
    def _parse_post_mcp_call_hook_response(
        self, response: MCPPostCallResponseObject | None
    ) -> "Sequence[TextContent | ImageContent | EmbeddedResource] | None":
        """
        Parse the response from the post_mcp_tool_call_hook

        1. Unpack the mcp_tool_call_response
        2. save the updated response_cost to the model_call_details
        """
        if response is None:
            return None
        self.model_call_details["response_cost"] = response.hidden_params.response_cost
        return response.mcp_tool_call_response
```

### Code verification: `hidden_params` is public on the MCP post-call object

Attributed to the same commit, files `litellm/types/mcp.py` and
`litellm/types/llms/base.py`:

```python
class MCPPostCallResponseObject(LiteLLMBaseModel):
    """
    Pydantic object used for MCP post_call_hook response
    """

    mcp_tool_call_response: list[MCPTextContent | MCPImageContent | MCPEmbeddedResource]
    hidden_params: HiddenParams
```

```python
class HiddenParams(OpenAIObject):
    original_response: str | object | None = None
    model_id: str | None = None  # used in Router for individual deployments
    api_base: str | None = None  # returns api base used for making completion call
    _response_ms: float | None = None
    response_cost: float | None = None
```

### Code verification: MCP spend shares the completion spend table

Attributed to the same commit, file
`litellm/proxy/spend_tracking/spend_management_endpoints.py`:

```python
_MCP_CALL_TYPES_SQL: Final = "('call_mcp_tool', 'list_mcp_tools')"
```

```python
                           COALESCE(SUM(spend) FILTER (
                               WHERE call_type IN {_MCP_CALL_TYPES_SQL}
                           ), 0)::double precision AS mcp_tool_call_spend,
```

### Code verification: a hook-set cost reaches the standard logging payload

Attributed to the same commit, file
`tests/unit/proxy/mcp_server/test_mcp_logging.py`:

```python
class MCPLoggerHook(TestMCPLogger):
    async def async_post_mcp_tool_call_hook(
        self, kwargs, response_obj: MCPPostCallResponseObject, start_time, end_time
    ) -> MCPPostCallResponseObject | None:
        print("post mcp tool call response_obj", response_obj)
        # update the MCPPostCallResponseObject with the response_cost
        response_obj.hidden_params.response_cost = 1.42
        return response_obj
```

```python
            assert logged_standard_logging_payload["response_cost"] == 1.42
```

## Cross-References

**Candidates from `miner-related-notes.md`** (read before Cross-References per
MINER.md §4; all ten pre-computed candidates are cited or dismissed below).
The lexical retrieval returned generic LiteLLM docs neighbors; the notes that
actually matter (`docs-litellm-a2a-cost-tracking.md`,
`docs-litellm-cost-map-and-response-cost.md`,
`failure-litellm-model-cost-map-silent-fallback.md`, and the MCP control/
guardrail notes) were found by searching `source-notes/` directly, which
MINER.md §4 permits.

- `source-notes/docs-litellm-batches-api.md` — **Dismissed**. Batch JSONL
  rate limiting and `batch_enqueued_token_limit`; no MCP tool cost surface.
- `source-notes/docs-litellm-completion-web-search.md` — **Dismissed**. The
  provider web-search support matrix mentions cost tracking, but for
  provider-native search on completion endpoints, not MCP tool calls.
- `source-notes/docs-litellm-evals-api.md` — **Dismissed**. Managed
  Evaluations API and grader model calls; unrelated to MCP pricing.
- `source-notes/docs-litellm-generate-content.md` — **Dismissed**. Gemini
  native `generateContent` passthrough; no MCP or spend surface.
- `source-notes/docs-litellm-completion-input-params.md` — **Dismissed**.
  Request-parameter gate; no MCP cost or spend content.
- `source-notes/docs-litellm-files-endpoints.md` — **Dismissed**. Provider
  `/files` passthrough; unrelated.
- `source-notes/docs-litellm-bedrock-invoke.md` — **Dismissed**. Bedrock
  native Invoke routing and bearer-token swap; unrelated.
- `source-notes/docs-litellm-enterprise.md` — **Dismissed**. Licensing and
  enterprise features; no MCP cost configuration.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **Dismissed**. A2A
  per-session iteration/budget caps; adjacent as a cost-control surface but a
  different protocol and enforcement mechanism. The A2A *cost* note is cited
  separately below.
- `source-notes/docs-litellm-audio-transcription.md` — **Dismissed**.
  Transcription fallbacks and `mock_testing_fallbacks`; unrelated.

**Primary cross-references** (all verified against the cited note before
writing, per MINER.md §4b):

- **Corroborates**:
  - `source-notes/docs-litellm-a2a-cost-tracking.md` **Claim 3** — the A2A
    note's load-bearing finding is that a configured per-query cost is a
    gateway-declared synthetic charge with no documented linkage to the agent's
    measured token usage or upstream model cost. This page is the same pattern
    on a different object: a per-tool/per-server declared price with no
    measured linkage (Claim 7 here). The two notes together establish that
    LiteLLM's agent-gateway cost accounting is consistently *declared* on both
    the A2A and MCP axes, while the model path is map-derived. They do not
    contradict: different objects, same design trade-off.
  - `source-notes/docs-litellm-mcp-guardrails.md` **Claim 2** — the guardrail
    page documents a `post_mcp_call` phase that runs after the MCP server
    returns, on the tool result, before the model sees it. This page's
    `async_post_mcp_tool_call_hook` is the same post-call stage on the logging
    callback path (not the guardrail path). Both confirm that MCP gives
    operators a post-execution hook point; they are different hook families
    (`post_mcp_call` guardrails vs. `async_post_mcp_tool_call_hook` logging
    callbacks), so do not treat them as interchangeable.
- **Contradicts**: None filed. Three candidate tensions were checked per
  MINER §4a; none is a claim-level opposition:
  1. *Hook contract vs. code* — the Prospector's caveat suggested
     `hidden_params` might be a private structure. The implementation shows a
     public `hidden_params: HiddenParams` field on `MCPPostCallResponseObject`,
     a `response_cost` field on `HiddenParams`, and a test that the hook value
     reaches the logging payload. No contradiction; the page's contract is
     correct at `main`.
  2. *Declared MCP price vs. Ch05's cost-attribution rule* — the guide's
     `guide/05-llm-ops-reliability.md:1028` rule ("Routing decisions are cost
     decisions — attribute the cause") concerns model-routing attribution. A
     declared per-tool charge is still attributable — it lands in the spend
     table against the calling key and `call_type` (Claim 9) — so it adds a
     third axis rather than opposing the rule. No contradiction filed.
  3. *MCP config-based pricing vs. A2A UI-only pricing* — the A2A note records
     its cost panel as UI-only (Claim 7); MCP pricing is `config.yaml`-native.
     That is a feature difference between two protocols, not a disagreement
     about the same mechanism. No contradiction filed.
- **Extends**:
  - `source-notes/docs-litellm-cost-map-and-response-cost.md` **Claim 1** —
    that note documents the SDK's per-call `response_cost` handle on
    `response._hidden_params["response_cost"]`. This page extends the same
    concept to MCP tool calls, but with a *public* `hidden_params` on the
    post-call object and a separate `MCPCostCalculator`, so the MCP cost is not
    derived from the completion cost map at all. The two notes together show
    that `response_cost` is a shared *field name*, not a shared calculation
    path.
  - `source-notes/failure-litellm-model-cost-map-silent-fallback.md`
    **Symptom 2** and **Symptom 3** (cost tracking silently returned `cost=0`;
    the cost map is not in the request path) plus **Lesson 2** and
    **Lesson 3** (warn on fallback; probe out-of-band functions). MCP's
    unpriced-tool default is the same silent-zero failure class on a different
    subsystem: a successful tool call with `spend = 0.0` and no request-path
    error. The incident note's remediation vocabulary (warning on fallback,
    synthetic probes) applies directly.
  - `source-notes/docs-litellm-mcp-control.md` **Claim 11** — that note
    documents per-server rate limits (`mcp_rpm_limit`, server `rpm`) as a
    per-server control axis. This page adds a second per-server control —
    price — in the same `mcp_servers` registration block. Access, rate, and
    price are now three per-server governance knobs an operator must keep in
    sync with the server alias and tool names.
- **Novel**: First source note in the corpus covering LiteLLM's MCP cost
  surface at all: `mcp_server_cost_info`, `default_cost_per_query`,
  `tool_name_to_cost_per_query`, `async_post_mcp_tool_call_hook`, and the
  `call_mcp_tool` spend rows. The corpus's prior cost content is model-path
  (cost map, `response_cost`, streaming usage), A2A-path (per-agent declared
  price), or client-side (Claude Code budgets); no note covered per-tool MCP
  pricing or the MCP spend `call_type` discriminator.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — cost, capacity, fallback)**: Add MCP
  tool calls as a **third cost-attribution axis** next to completion tokens and
  A2A agents, citing this source. Teach: (a) prices are declared in
  `config.yaml` under `mcp_info.mcp_server_cost_info`, per-tool first then
  server default then zero (Claim 3); (b) the custom hook overrides config and
  a `0.0` hook value disables the configured price (Claim 5); (c) an unpriced
  tool call logs zero silently, so "cost tracking is on" is not evidence that a
  tool is priced (Claim 6); (d) both paths are declared charges, not measured
  upstream cost, so add the same chargeback-accuracy check the A2A note
  recommends — re-verify declared prices against actual upstream spend when
  tool mix or provider pricing changes (Claim 7).
- **Chapter 02 (Observability — per-tool cost as a metric)**: Add MCP
  `call_type` as a spend-log dimension (`call_mcp_tool`, `list_mcp_tools`) and
  `mcp_tool_call_spend` as a session metric, citing Claim 9. Add an alert or
  synthetic probe for "configured MCP price exists but observed spend is zero"
  and for hook exceptions, because a failed cost hook is swallowed and leaves a
  successful call with wrong spend (Claim 8). This is the MCP analogue of the
  out-of-band cost probe the model-cost-map incident note's Lesson 3 requires.
- **Chapter 03 (Runbooks and Agents)**: Add a pre-rollout MCP cost check:
  call one known tool through the proxy, assert the spend row is non-zero and
  equals the configured per-tool price; if a custom hook is registered, assert
  the hook's value overrides config and test the `0.0` case deliberately; after
  any server-alias or tool rename, re-check that the price still matches
  (Claim 6). Keep the price block in the same reviewed change as the
  `mcp_servers` registration.

## Extraction Notes

- Primary source read in full from the live markdown endpoint
  (`https://docs.litellm.ai/docs/mcp_cost.md`, HTTP 200, no paywall). Front
  matter reports `last_updated: "2026-10-29"`. All page quotes and code blocks
  are byte-exact from that endpoint.
- Followed the two related links from the page (`/docs/proxy/tool_policies`,
  `/docs/mcp_guardrail`) and the MCP gateway's configuration and troubleshooting
  pages (`/docs/mcp_config_reference`, `/docs/mcp_troubleshoot`) to check for
  cost-attribution details. They document routing, auth, transport, and
  troubleshooting; none adds MCP cost semantics. The guardrail page is cited
  for the post-call timing distinction (Cross-References).
- **Code verification**: because the page is thin and the Prospector asked
  whether the hook's value actually lands in the request log/spend table, the
  claims were checked against `BerriAI/litellm` `main` at commit
  `e93e01ca4b66b8a675da0af25193b50e6bb65a91` (2026-10-29):
  `litellm/proxy/mcp_server/cost_calculator.py`,
  `litellm/litellm_core_utils/litellm_logging.py`,
  `litellm/proxy/mcp_server/operations.py`, `litellm/types/mcp.py`,
  `litellm/types/llms/base.py`,
  `litellm/proxy/spend_tracking/spend_management_endpoints.py`, and
  `tests/unit/proxy/mcp_server/test_mcp_cost_calculator.py` /
  `test_mcp_logging.py`. The guide has no LiteLLM version pin, so these are
  `main`-HEAD findings; a pinned release could differ.
- The Prospector's caveat about `hidden_params` being private was checked
  directly: on `MCPPostCallResponseObject` it is a public field, and
  `HiddenParams.response_cost` is a declared field. No contradiction issue was
  filed. The page's sample is still a sketch (`custom_cost = 42.00`, flat
  `kwargs.get("name")`), recorded as Claim 10 rather than as a contradiction.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  listed candidate paths are cited or dismissed above. Every cited claim number
  was re-read in the cited note before writing: A2A cost Claim 3, guardrail
  Claim 2, cost-map/`response_cost` Claim 1, MCP control Claim 11. The
  failure-report note is cited by section name (Symptom 2/3, Lesson 2/3)
  because it uses symptom/lesson headings, not `### Claim N`.
- `confidence_overall` is `emerging`: the page's surface claims are settled,
  and the behavior claims are confirmed in current source and unit tests, but
  the page publishes no measured data or failure writeups, the code check is
  against `main` rather than a pinned release, and the declared-vs-measured
  framing is our synthesis. `date_published` is unknown (living vendor docs);
  `date_extracted` and `last_checked` are both 2026-10-29 (UTC).
