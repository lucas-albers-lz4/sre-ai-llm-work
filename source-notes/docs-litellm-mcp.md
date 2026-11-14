---
source_url: https://docs.litellm.ai/docs/mcp
source_type: docs
title: "MCP Gateway (LiteLLM Documentation)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-26)
date_extracted: 2026-10-27
last_checked: 2026-10-27
status: current
confidence_overall: emerging
issue: "#1901"
---

# MCP Gateway (LiteLLM Docs)

> Operational contract for LiteLLM's MCP Gateway: transport defaults and safe defaults, identity stability via `server_id`, config-vs-database collision behavior, SEP-986 tool name namespacing and migration risk, scoped credential forwarding with precedence rules (including silent failure cases), and end-user attribution — with stdio gated by an environment-only flag and many "silent" failure modes that need runbook attention.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway). Living page; no publication date.
- **Author credibility**: First-party product docs. Claims about the exposed surface (flags, headers, precedence, collisions) are authoritative for that surface; behavior is documented as capability/contract, not demonstrated reliability or production metrics.
- **Scope**: Covers adding MCP servers (HTTP/SSE/stdio) via UI/config, auth types, OAuth/AWS SigV4/static headers, `server_id` stability, transport defaults, tool namespacing (SEP-986), header-based credential forwarding (`x-mcp-{server_alias}-{header}` vs `x-mcp-{access_group}-{header}`), end-user attribution via `x-litellm-end-user-id`, aliases, and troubleshooting pointers. This note focuses on operational failure modes and constraints called out by triage; it does not duplicate detailed auth enum tables already covered elsewhere where not necessary.

## Extracted Claims

### Claim 1: stdio transport is disabled by default and gated by an environment-only flag
- **Evidence**: "stdio MCP servers are disabled unless the proxy is started with `LITELLM_ENABLE_MCP_STDIO=true` in its environment. While it is off, the stdio transport is greyed out in the UI, creating or updating a stdio server returns an error, and existing stdio servers stay listed but never start: their tools are left out of tool listings, direct tool calls return `403`, and their health check reports them as unhealthy. The flag is read from the proxy's process environment only. Setting it under `environment_variables` in config.yaml or in the database has no effect."
- **Confidence**: settled
- **Quote**: "stdio MCP servers are disabled unless the proxy is started with `LITELLM_ENABLE_MCP_STDIO=true` in its environment. While it is off, the stdio transport is greyed out in the UI, creating or updating a stdio server returns an error, and existing stdio servers stay listed but never start: their tools are left out of tool listings, direct tool calls return `403`, and their health check reports them as unhealthy. The flag is read from the proxy's process environment only. Setting it under `environment_variables` in config.yaml or in the database has no effect."
- **Our assessment**: Safe-default posture. The failure mode is particularly dangerous because servers appear listed (not removed), tools silently disappear from listings, direct calls return 403, and health checks report unhealthy — easy to misread as permission/auth issues rather than a disabled transport. Upgrade procedure matters: add `LITELLM_ENABLE_MCP_STDIO=true` to the proxy process environment and restart; until then the proxy logs a warning naming each stdio server it will not start.

### Claim 2: `server_id` is derived from name+connection settings unless pinned; changing them breaks permissions
- **Evidence**: "`server_id` is Optional stable id for the server. LiteLLM derives a config server's id from its name and connection settings. If you change those settings, the id changes and existing key or team permissions stop matching. Set `server_id` to keep the same id when the server changes. If the server already has permissions, use its current id from `GET /v1/mcp/server` or the Admin UI, then set that exact value as `server_id`."
- **Confidence**: settled
- **Quote**: "LiteLLM derives a config server's id from its name and connection settings. If you change those settings, the id changes and existing key or team permissions stop matching. Set `server_id` to keep the same id when the server changes. If the server already has permissions, use its current id from `GET /v1/mcp/server` or the Admin UI, then set that exact value as `server_id`."
- **Our assessment**: Pre-change checklist item: pin identity before mutating config, or permissions silently detach. `server_id` must be non-empty. Servers added through UI or `/v1/mcp/server` already have stable ids.

### Claim 3: Config-vs-database id/name/alias collisions have non-obvious resolution behavior
- **Evidence**: "`server_id` must be a non-empty string. Config entries cannot reuse an id or another entry's name or alias. Clashes with a database-backed server only log a warning: if the id matches, the database server wins and the config one is unreachable, and if it matches that server's name or alias, permissions naming it reach the config server instead."
- **Confidence**: settled
- **Quote**: "`server_id` must be a non-empty string. Config entries cannot reuse an id or another entry's name or alias. Clashes with a database-backed server only log a warning: if the id matches, the database server wins and the config one is unreachable, and if it matches that server's name or alias, permissions naming it reach the config server instead."
- **Our assessment**: Collisions are logged, not fatal — a startup-validation gap. Two directions of confusion: id collision makes config server unreachable (DB wins), name/alias collision routes permissions to the config server (opposite effect). Operators need to be aware of which entity "wins" depending on the kind of clash.

### Claim 4: Transport defaults differ between config.yaml and Management API
- **Evidence**: "Transport: Defaults to `http` in `config.yaml`. Management API request models default to `sse`; set it explicitly when adding or updating a server. See transport defaults."
- **Confidence**: settled
- **Quote**: "Transport: Defaults to `http` in `config.yaml`. Management API request models default to `sse`; set it explicitly when adding or updating a server."
- **Our assessment**: Easy source of confusion when mixing declarative config and API/UI-driven changes. Must set transport explicitly in API calls to avoid unexpected default.

### Claim 5: Tool namespacing enforces SEP-986 for new servers with migration risk for legacy names
- **Evidence**: "LiteLLM namespaces multiple MCP servers by prefixing each tool name with its MCP server name, so newly created servers now must use names that comply with SEP-986; noncompliant names cannot be added anymore. Existing servers that still violate SEP-986 only emit warnings today, but future MCP-side rollouts may block those names entirely, so we recommend updating any legacy server names proactively before MCP enforcement makes them unusable. If `LITELLM_USE_SHORT_MCP_TOOL_PREFIX` is enabled, changing the id also changes the server's tool prefix."
- **Confidence**: settled
- **Quote**: "LiteLLM namespaces multiple MCP servers by prefixing each tool name with its MCP server name, so newly created servers now must use names that comply with SEP-986; noncompliant names cannot be added anymore. Existing servers that still violate SEP-986 only emit warnings today, but future MCP-side rollouts may block those names entirely, so we recommend updating any legacy server names proactively before MCP enforcement makes them unusable. If `LITELLM_USE_SHORT_MCP_TOOL_PREFIX` is enabled, changing the id also changes the server's tool prefix."
- **Our assessment**: Renaming a server changes tool names that prompts/clients reference. With short prefix tied to `server_id`, identity changes have cascading effects on tool namespaces. Migration risk is real for legacy non-compliant names.

### Claim 6: Per-request credential routing has strict precedence rules with silent failure cases
- **Evidence**: "When the servers in an access group share one credential, pass `x-mcp-{access_group}-{header_name}` once instead of repeating it per server. LiteLLM uses it as the default for every server whose `access_groups` includes that group. A server-specific `x-mcp-{server_alias}-{header_name}` header overrides it for that server, servers outside the group never receive it, and if a server is in several groups that carry different credentials none of them is forwarded. Server aliases and access group names share the `x-mcp-` header namespace, so a server whose alias equals a group name keeps receiving `x-mcp-{alias}-*` as its own credential; avoid naming a server after an access group it does not belong to."
- **Confidence**: settled
- **Quote**: "When the servers in an access group share one credential, pass `x-mcp-{access_group}-{header_name}` once instead of repeating it per server. LiteLLM uses it as the default for every server whose `access_groups` includes that group. A server-specific `x-mcp-{server_alias}-{header_name}` header overrides it for that server, servers outside the group never receive it, and if a server is in several groups that carry different credentials none of them is forwarded. Server aliases and access group names share the `x-mcp-` header namespace, so a server whose alias equals a group name keeps receiving `x-mcp-{alias}-*` as its own credential; avoid naming a server after an access group it does not belong to."
- **Our assessment**: Critical runbook detail — when a server belongs to multiple groups with different credentials, **none are forwarded** (silent auth failure). Server-specific always wins over group-level. Namespace collision between alias and group name is a footgun.

### Claim 7: End-user attribution via `x-litellm-end-user-id` for object permissions, customer budgets, and per-customer spend
- **Evidence**: Mentioned in the page context under "Control MCP Access for End Users" / general usage patterns (the page describes using `x-litellm-end-user-id` for object permissions, customer budgets, per-customer spend attribution).
- **Confidence**: emerging
- **Quote**: "(as described in the page) Use `x-litellm-end-user-id` for object permissions, customer budgets, and per-customer spend attribution."
- **Our assessment**: Gateway-level multi-tenant control surface for attributing usage/costs and enforcing object permissions per end user.

## Concrete Artifacts

**stdio disabled-by-default behavior (verbatim):**
```
stdio MCP servers are disabled unless the proxy is started with LITELLM_ENABLE_MCP_STDIO=true in its environment. While it is off, the stdio transport is greyed out in the UI, creating or updating a stdio server returns an error, and existing stdio servers stay listed but never start: their tools are left out of tool listings, direct tool calls return 403, and their health check reports them as unhealthy. The flag is read from the proxy's process environment only. Setting it under environment_variables in config.yaml or in the database has no effect.
```

**server_id collision rules (verbatim):**
```
server_id must be a non-empty string. Config entries cannot reuse an id or another entry's name or alias. Clashes with a database-backed server only log a warning: if the id matches, the database server wins and the config one is unreachable, and if it matches that server's name or alias, permissions naming it reach the config server instead.
```

**Credential forwarding precedence (verbatim):**
```
A server-specific x-mcp-{server_alias}-{header_name} header overrides it for that server, servers outside the group never receive it, and if a server is in several groups that carry different credentials none of them is forwarded. Server aliases and access group names share the x-mcp- header namespace, so a server whose alias equals a group name keeps receiving x-mcp-{alias}-* as its own credential; avoid naming a server after an access group it does not belong to.
```

**SEP-986 / namespacing (verbatim):**
```
LiteLLM namespaces multiple MCP servers by prefixing each tool name with its MCP server name, so newly created servers now must use names that comply with SEP-986; noncompliant names cannot be added anymore. Existing servers that still violate SEP-986 only emit warnings today, but future MCP-side rollouts may block those names entirely, so we recommend updating any legacy server names proactively before MCP enforcement makes them unusable. If LITELLM_USE_SHORT_MCP_TOOL_PREFIX is enabled, changing the id also changes the server's tool prefix.
```

## Cross-References

- **Corroborates**:
  - `failure-litellm-mcp-stdio-command-injection.md` (#595) — CVE-2026-30623 / stdio transport surface. This docs page is the current contractual behavior (stdio off by default, env-gated) that the CVE remediation context builds on; complementary, not duplicate.
  - `docs-litellm-gateway-auth-reference.md` (#1402) — MCP auth surface (`auth_type` enum, patterns). This page adds operational details (stdio gating, identity stability, collisions, credential routing precedence) not covered there.
  - `docs-litellm-a2a-agent-gateway.md` (#1302) / `docs-litellm-a2a-agent-permissions.md` (#1400+) — adjacent Agent Gateway with similar identity/naming/permission concerns; useful for contrast.
  - `blog-litellm-may-townhall-updates.md` Claim 6 (MCP OAuth token vaulting at the proxy) — related auth path.

- **Contradicts**: none identified.

- **Extends**:
  - `failure-litellm-mcp-stdio-command-injection.md` — extends the stdio surface with the "listed but non-functional" operational failure mode and env-only gating details.

- **Novel** (to our corpus):
  - Env-only gating of stdio (`LITELLM_ENABLE_MCP_STDIO`) with specific failure symptoms (greyed UI, errors on create/update, servers listed but tools disappear, 403 on direct calls, unhealthy health checks; warning on upgrade).
  - `server_id` derivation/stability rules and the exact collision resolution matrix (id collision → DB wins/config unreachable; name/alias collision → permissions route to config server).
  - Transport defaults differing between `config.yaml` (http) and Management API (sse).
  - SEP-986 enforcement posture (new servers must comply, legacy warn now, may block later) and coupling of `LITELLM_USE_SHORT_MCP_TOOL_PREFIX` to `server_id`.
  - Per-request credential routing precedence with group/server-specific rules and the silent failure when a server belongs to multiple groups with different credentials; namespace collision between alias and group name.
  - End-user attribution via `x-litellm-end-user-id` for permissions/budgets/spend.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add runbook entries for MCP Gateway operations — (1) stdio enablement checklist (set `LITELLM_ENABLE_MCP_STDIO=true` in proxy process env, restart, watch logs for warnings; expect "server listed but non-functional" if missed), (2) pre-change checklist for MCP servers (pin `server_id` before renaming/URL/transport changes; verify current id via `GET /v1/mcp/server`), (3) collision troubleshooting (check logs for warnings on id/name/alias clashes; know which side wins), (4) transport defaults (explicitly set transport in API/config as appropriate), (5) credential routing debugging (check precedence when using group+server headers; note silent "none forwarded" case for multi-group with different creds).
- **Chapter 06 (Security and Trust)**: Add guardrails — enforce least privilege on MCP server creation (relevant to CVE-2026-30623 posture), be careful with header namespace collisions (`x-mcp-{alias}-*` vs group names), audit end-user attribution usage, and treat legacy SEP-986 non-compliant names as migration debt before enforcement.
- **Chapter 03 (Runbooks and Agents)**: Add MCP Gateway troubleshooting notes (symptoms: tools missing while server listed + 403s + unhealthy → check stdio flag; permissions lost after change → check `server_id` stability).

## Extraction Notes

- Source read in full via WebFetch on canonical URL (`https://docs.litellm.ai/docs/mcp`, HTTP 200, no paywall). Living vendor docs, current as of 2026-10-26.
- Focused extraction on operational failure modes and constraints per triage targets; did not re-extract full auth enum tables already covered in `docs-litellm-gateway-auth-reference.md`.
- Cross-referenced against related notes (CVE failure note on stdio, gateway auth reference, A2A notes). All claims verified against the live page content.
- Confidence `emerging` (vendor capability/contract; no measured behavior/failure case studies on the page).
- No contradiction issue filed; claims are consistent with existing corpus.
