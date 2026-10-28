---
source_url: https://docs.litellm.ai/docs/mcp_control
source_type: docs
title: "MCP Control — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-10-27
last_checked: 2026-10-28
status: current
confidence_overall: emerging
issue: "#1918"
---

# MCP Control (LiteLLM Docs)

> LiteLLM's MCP permission model composes across six entity levels with asymmetric intersection (org is a ceiling, others intersect most-restrictively), has a fail-open default ("no level has a list = open by default"), provides a team-ceiling opt-in via `require_key_mcp_access_defined`, explicit deny via `no-mcp-servers`, per-entity tool controls plus server-level parameter whitelists, tool-list pinning to close tool poisoning, per-server and per-entity rate limits, and dashboard visibility controls.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP Control" page under "Agent & MCP Gateway").
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation. Authoritative for the exposed surface (hierarchy, fields, flags, API behavior), but documents capability not measured reliability; claims stay at "the gateway documents this surface".
- **Confidence policy**: all 13 claims are graded `emerging` uniformly. The page states most behavior explicitly (e.g., Claim 2's open-by-default and Claim 5's `no-mcp-servers` override), so the grade is not a doubt that the page says what it says; it reflects first-party capability documentation with no measured reliability evidence and no independent verification of the documented behavior, on a page that can change between releases.
- **Scope**: Covers MCP permission management by keys/teams/orgs/users/agents/internal users, inheritance vs intersection vs ceiling semantics, `require_key_mcp_access_defined`, `no-mcp-servers` sentinel, per-entity server/tool controls, server-level `allowed_params` parameter whitelists, tool pinning, access groups, public MCPs (`allow_all_keys`), per-server rate limiting (entity and global), dashboard view modes, and MCP registry publishing. Does not deep-dive OAuth/ID-JAG/OBO transport details beyond what is referenced.

## Extracted Claims

### Claim 1: Permissions compose across six levels with asymmetric intersection — org is a ceiling, all others intersect (most-restrictive wins)
- **Evidence**: Permission hierarchy table listing Key, Team, End user, Agent, Internal user, Organization with composition rules and the note about org as ceiling.
- **Confidence**: emerging
- **Quote**: "Permissions can be set at six distinct levels. When more than one level applies to a request, LiteLLM **intersects** the lists (most-restrictive wins), except for the organization level, which acts as a **ceiling**."
- **Our assessment**: This is the core composition rule. Critically, org does not participate in intersection like others — it only caps the final set. The ordering/which identity headers apply is specified elsewhere, but the asymmetry is central and easy to misread.

### Claim 2: Default is open if no level defines a list
- **Evidence**: Hierarchy section.
- **Confidence**: emerging
- **Quote**: "If no level has a list, the request can access **every** MCP server (open by default)."
- **Our assessment**: Concrete fail-open default. With teams often acting as defaults in practice, this is a high-value security/reliability note that matches the "fail-open by default" pattern seen elsewhere in LiteLLM auth.

### Claim 3: A key bound to an agent gets the agent's list intersected on every request; granting the server to the key alone is insufficient
- **Evidence**: Hierarchy section describing agent binding via `agent_id` at key generation and `x-litellm-agent-id` requests.
- **Confidence**: emerging
- **Quote**: "A key bound to an agent (`agent_id` passed to `/key/generate`) gets the same treatment as a request carrying `x-litellm-agent-id`: the agent's list is intersected with the key's on every request the key makes. Granting a server to the key alone is not enough; the agent must also hold the grant (via the Admin UI agent edit form or `PATCH /v1/agents/{agent_id}`), otherwise requests scoped to that server are denied with an error naming the agent."
- **Our assessment**: This is a strong "defense in depth" rule and also a common misconfiguration. The error names the agent, which is good for runbooks.

### Claim 4: `require_key_mcp_access_defined: true` flips empty-key-list from "inherit team" to "grant nothing" (team becomes ceiling)
- **Evidence**: `general_settings.require_key_mcp_access_defined` section.
- **Confidence**: emerging
- **Quote**: "By default a key with an empty or absent `mcp_servers` list inherits its team's list, so the team is effectively a default that every key falls back to. Set `require_key_mcp_access_defined: true` under `general_settings` to flip that relationship: the team becomes a ceiling rather than a default, and a key with an empty list is granted no MCP servers unless it grants some explicitly (either directly in `object_permission.mcp_servers` or via an [access group](#grouping-mcps-access-groups))."
- **Our assessment**: Documents the migration cliff explicitly: flipping it on before keys carry grants drops MCP access. The page states this is "the recommended posture" but not default yet and points to a deprecation discussion — any guide advice must phrase it as currently non-default.

### Claim 5: `no-mcp-servers` is an explicit deny that overrides team inheritance and additive access-group grants
- **Evidence**: `no-mcp-servers` section.
- **Confidence**: emerging
- **Quote**: "To explicitly deny a key every MCP server, put the sentinel `no-mcp-servers` in its `mcp_servers` list. This mirrors the `no-default-models` sentinel used for model access. Unlike an empty list, which inherits the team's servers, `no-mcp-servers` overrides team inheritance and any additive access-group grants, so the key resolves to zero MCP servers no matter what its team allows."
- **Our assessment**: Clear distinction from empty list. Important for break-glass/deny cases.

### Claim 6: Internal user entitlements act as a narrowing ceiling across all other levels
- **Evidence**: "Entitling a person rather than a credential" section.
- **Confidence**: emerging
- **Quote**: "The grant lives on the internal user's `object_permission` and uses the same fields as everywhere else, `mcp_servers`, `mcp_access_groups` and `mcp_tool_permissions`. It resolves as a ceiling on both axes: the servers the person reaches are intersected with what their key, team, agent and organization allow, and so are the tools they may run on each of those servers. Someone entitled to a server their key does not grant still cannot reach it. In resolution order the key and team come first, then the end user, then the agent, then the internal user, then the organization ceiling"
- **Our assessment**: Person-centric entitlement that only narrows. The quote above is contiguous; the following details are a paraphrase from later paragraphs of the same section ("Entitling a person rather than a credential"), not part of that quote: `GET /v2/user/info` returns the linked `object_permission` (verbatim: "Read the grant back with `GET /v2/user/info`, which now returns the linked `object_permission`"); the refusal is surfaced inside the MCP result (verbatim: "The refusal arrives inside the MCP result with `isError: true`"), so a client that hardcodes a tool name is still refused. An admin role is not a waiver once the human carries an entitlement: "the admin role widens what the credential reaches, and leaves the scope attached to the person in place." Only a proxy admin can set the entitlement.

### Claim 7: Tool-level control is per-entity via `mcp_tool_permissions` intersected the same way as server lists
- **Evidence**: Per-entity tool-level permissions section and examples (key/team/agent/internal user).
- **Confidence**: emerging
- **Quote**: "The same intersection model applies to the per-server tool-level dict `mcp_tool_permissions` (see [Per-entity Tool-Level Permissions](#per-entity-tool-level-permissions) below)."
- **Our assessment**: Server ACLs alone are insufficient; tool lists are also intersected across levels, and `mcp_tool_permissions` is explicitly distinct from server-registration-level `allowed_tools`/`disallowed_tools` (which bind every caller). Parameter-level filtering is a *separate, server-level* control (`allowed_params`), extracted as Claim 8 — the page documents no per-entity parameter layer.

### Claim 8: Parameter-level filtering is server-registration-level via `allowed_params` (per-tool whitelist, 403 otherwise)
- **Evidence**: "Allow/Disallow MCP Tool Parameters" section — `allowed_params` config example, the five "How It Works" rules, an allowed-vs-rejected request example, and the error response.
- **Confidence**: emerging
- **Quote**: "`allowed_params` is a dictionary that maps tool names to lists of allowed parameter names. When configured, only the specified parameters will be accepted for that tool - any other parameters will be rejected with a 403 error."
- **Our assessment**: This is a server-wide control (applies to every caller of the server), not a per-entity one — the per-entity layer stops at tool names (Claim 7). The page documents no per-entity parameter control and does not mention a `mcp_tool_parameters` field. It is a whitelist: tools with no `allowed_params` entry stay unrestricted, and a tool whose upstream signature gains a parameter later needs a config update or those calls start failing with `403`. Tool names may be specified with or without the server prefix (`"getpetbyid"` and `"my_api_mcp-findpetsbystatus"` both work). It composes with `allowed_tools`/`disallowed_tools` on the same server.

### Claim 9: Pinning freezes tool list/description/input schema and closes tool poisoning; snapshot taken after discovery guardrail scan
- **Evidence**: "Pin a Server's Tool List" section.
- **Confidence**: emerging
- **Quote**: "`allowed_tools` trusts whatever the upstream says each tool does. Pinning freezes the tool list, the descriptions, and the input schemas too: the gateway serves only the pinned tools with their pinned descriptions and schemas, refuses calls to any other name, and alerts when the upstream drifts from the pin. That closes tool poisoning (OWASP LLM01): a server that quietly rewrites a description to carry instructions for the model, or adds a tool your clients never approved, changes nothing your clients see"
- **Our assessment**: Strong control: snapshot taken after discovery guardrail scan (blocked descriptions never pinned, masked ones pinned masked). Pin requires admin + database. `pinned_tools` can be set in `config.yaml`. Unpin returns to live upstream catalog.

### Claim 10: Public MCPs via `allow_all_keys` make a server available to every LiteLLM API key without per-key restrictions
- **Evidence**: "Public MCP Servers (allow_all_keys)" section.
- **Confidence**: emerging
- **Quote**: "Mark specific servers as available to every LiteLLM API key when you don't need per-key restrictions."
- **Our assessment**: Convenience feature; still subject to other controls as configured.

### Claim 11: Per-server rate limits exist at entity level (`mcp_rpm_limit` on key/team/user) and global level (server `rpm`), with specific counting rules
- **Evidence**: Rate limiting sections.
- **Confidence**: emerging
- **Quote**: "Cap how many requests a key or team can make to a specific MCP server per minute with `mcp_rpm_limit`. This is a `Dict[str, int]` keyed by MCP server name... Every MCP operation sent to that server counts: `tools/call`, `tools/list`, `prompts/list`, `prompts/get`, `resources/list`, `resources/templates/list` and `resources/read`, plus the REST tool listing at `/mcp-rest/tools/list`. Once the limit is exceeded within the window, further requests to that server are rejected until the window rolls over."
- **Our assessment**: Detailed counting rules (pagination pages count per server, discovery charges each server once, rejections before limiter not counted, internal listings not counted). Server-wide `rpm` applies in addition and is shared across instances if Redis used. Key/team limits have precedence rules; legacy multi-instance flag disables enforcement.

### Claim 12: Dashboard visibility controlled by `general_settings.user_mcp_management_mode` (restricted default vs view_all)
- **Evidence**: Dashboard View Modes section.
- **Confidence**: emerging
- **Quote**: "Proxy admins can also control what non-admins see inside the MCP dashboard via `general_settings.user_mcp_management_mode`:" — with the two modes as separate verbatim list items: "`restricted` *(default)* – users only see servers that their team explicitly has access to." and "`view_all` – every dashboard user can see the full MCP server list."
- **Our assessment**: Discoverability vs privilege separation; execution privileges still enforced.

### Claim 13: MCP registry can be published at `/v1/mcp/registry.json` when `enable_mcp_registry: true` (advertises URLs only; permissions still enforced)
- **Evidence**: Publish MCP Registry section.
- **Confidence**: emerging
- **Quote**: "If you want other systems... to automatically discover the MCP servers hosted on LiteLLM, you can expose a Model Context Protocol Registry endpoint... LiteLLM will serve the registry at `GET /v1/mcp/registry.json`. Each entry points to either `/mcp` (built-in server) or `/{mcp_server_name}/mcp` for your custom servers... The registry only advertises server URLs. Actual access control is still enforced by LiteLLM when the client connects to `/mcp` or `/{server}/mcp`, so publishing the registry does not bypass per-key permissions."
- **Our assessment**: Discovery mechanism only; authZ still applies.

## Concrete Artifacts

### Permission hierarchy (from docs)
```text
Key → Team → End user → Agent → Internal user → Organization
Intersect all except Organization acts as ceiling. If no level has a list → open by default.
```

### Require key to define access
```yaml
general_settings:
  require_key_mcp_access_defined: true
```

### Deny all MCP servers
```bash
curl -X POST "http://localhost:4000/key/generate" \
  -H "Authorization: Bearer sk-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "object_permission": {
      "mcp_servers": ["no-mcp-servers"]
    }
  }'
```

### Parameter whitelist per tool (`allowed_params`, from docs)
```yaml
mcp_servers:
  deepwiki_mcp:
    url: https://mcp.deepwiki.com/mcp
    transport: "http"
    auth_type: "none"
    allowed_params:
      # Tool name: list of allowed parameters
      read_wiki_contents: ["status"]

  my_api_mcp:
    url: "https://my-api-server.com"
    auth_type: "api_key"
    auth_value: "my-key"
    allowed_params:
      # Using unprefixed tool name
      getpetbyid: ["status"]
      # Using prefixed tool name (both formats work)
      my_api_mcp-findpetsbystatus: ["status", "limit"]
      # Another tool with multiple allowed params
      create_issue: ["title", "body", "labels"]
```

Rejection response for a disallowed parameter:
```json
{
  "error": "Parameters ['limit'] are not allowed for tool read_wiki_contents. Allowed parameters: ['status']. Contact proxy admin to allow these parameters."
}
```

### Internal user entitlement example
```bash
curl -X POST "http://localhost:4000/user/update" \
  -H "Authorization: Bearer sk-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "object_permission": {
      "mcp_servers": ["github_mcp"],
      "mcp_tool_permissions": {"github_mcp": ["list_issues"]}
    }
  }'
```

### Tool pinning (API)
```bash
curl -s -X POST http://localhost:4000/v1/mcp/server/$SERVER_ID/pin \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

### Per-server/global rate limits (examples)
```yaml
mcp_servers:
  github:
    url: "https://api.githubcopilot.com/mcp"
    rpm: 300
```
```bash
curl -X POST "http://localhost:4000/key/generate" \
  -H "Authorization: Bearer sk-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "mcp_rpm_limit": {"github": 100, "slack": 200},
    "object_permission": {"mcp_servers": ["github", "slack"]}
  }'
```

### Dashboard view mode
```yaml
general_settings:
  user_mcp_management_mode: view_all  # or restricted (default)
```

### MCP registry
```yaml
general_settings:
  enable_mcp_registry: true
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-gateway-auth-reference.md` — Confirms MCP permission model is deeper than A2A (six levels vs two); notes internal user resolution exists on MCP side. Also aligns with route-dependent auth behavior noted elsewhere.
  - `source-notes/docs-litellm-a2a-agent-permissions.md` — Shares intersection semantics for agent/group permissions; this page extends MCP hierarchy to include internal users and documents the full six-level composition with org-as-ceiling. A2A remains narrower per gateway-auth-reference.
  - `source-notes/blog-litellm-july-stability-update.md` — Reinforces shift toward explicit/declarative control (aligns with "declare don't infer" theme); `require_key_mcp_access_defined` is the MCP-layer counterpart to fail-open defaults.
- **Contradicts**: None obvious.
- **Extends**:
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md` — This page provides the access-control half (per-entity server/tool controls, server-level parameter whitelists, pinning) that complements stdio command injection concerns; together they form a fuller MCP threat model (creation/injection vs access control).
  - `source-notes/docs-litellm-security-settings.md`, `source-notes/docs-litellm-data-security.md` — General security posture; this page adds concrete MCP-specific ACLs, pinning (tool poisoning mitigation), and rate limiting.
- **Novel**:
  - Six-level MCP permission hierarchy with org-as-ceiling (explicitly documented asymmetry)
  - `require_key_mcp_access_defined` migration-cliff behavior and non-default recommended posture
  - `no-mcp-servers` sentinel semantics (overrides inheritance + access groups)
  - Internal user entitlements as narrowing ceiling with admin-role caveat
  - Tool pinning with post-guardrail-scan snapshot and drift alerting (OWASP LLM01 mitigation)
  - Per-entity and global MCP rate limits with detailed counting rules
  - MCP registry publishing (discovery only)
  - Server-level `allowed_params` parameter whitelists (per tool, all callers) — distinct from `allowed_tools`/`disallowed_tools` and from per-entity `mcp_tool_permissions`; no per-entity parameter layer is documented

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — gateway config, defaults)**: Add explicit note that MCP access is open by default if no permission level defines a list; document the recommended migration to `require_key_mcp_access_defined: true` (team becomes ceiling) with the migration cliff warning. Include `no-mcp-servers` as explicit deny.
- **Chapter 06 (Security and Trust — MCP tool poisoning, least privilege)**: Add six-level permission model with org-as-ceiling and intersection rules; document internal user entitlements as person-centric narrowing control; call out tool pinning as mitigation for tool poisoning (snapshot after discovery guardrail scan, alerts on drift) distinct from `allowed_tools`/`disallowed_tools`; document server-level `allowed_params` parameter whitelists (per tool, applied to every caller) and state that the page documents no per-entity parameter control; note public MCPs (`allow_all_keys`) and registry discoverability vs enforced authZ.
- **Chapter 03 (Architecture/Components — gateway controls)**: Document per-server/per-entity MCP rate limiting with counting semantics and Redis/shared behavior; dashboard visibility modes.

## Extraction Notes

- Read deeply from the live docs page (full content retrieved). Followed all major sections: hierarchy, inheritance flag, sentinel, tool controls, pinning, public MCPs, tool-parameter controls (`allowed_params`), access groups, per-entity permissions, internal users, rate limiting (entity + global), dashboard modes, registry.
- All quotes were re-verified character-for-character against the raw page source (`.md` endpoint) on 2026-10-28. Where a quote spans non-adjacent text it is marked with `...`; Claim 6's assessment details that fall outside its quote are explicitly labeled as paraphrase from later paragraphs of the same section.
- Parameter control on this page is **server-registration-level** `allowed_params` only. The source does not mention any `mcp_tool_parameters` field or any per-entity parameter layer; the per-entity layer stops at tool names (`mcp_tool_permissions`).
- No contradictions surfaced vs existing notes; this page is largely additive to MCP access control surface.
- Internal user entitlements and pinning details are particularly important and appear to be newer surface relative to existing notes.
