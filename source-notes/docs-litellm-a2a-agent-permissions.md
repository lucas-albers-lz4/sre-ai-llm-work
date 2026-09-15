---
source_url: https://docs.litellm.ai/docs/a2a_agent_permissions
source_type: docs
title: "Agent Permission Management — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-14)
date_extracted: 2026-09-15
last_checked: 2026-09-15
status: current
confidence_overall: emerging
issue: "#1317"
---

# Agent Permission Management (LiteLLM Docs)

> Per-agent authorization in LiteLLM's A2A gateway is a two-level
> (Key → Team) intersection with a fail-open default when neither level
> sets restrictions, and agent access groups — tag-based ACLs that scale
> better than per-agent enumeration — can only be managed through the
> dashboard UI, not the API, placing agent ACLs outside declarative
> config / IaC control.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living
  page under the "Agent & MCP Gateway > A2A Agent Gateway" nav section).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the surface LiteLLM exposes (field names, resolution rules,
  curl shapes, error codes), but documents *capability*, not demonstrated
  reliability: no measured overhead, no failure-mode writeups, no production
  experience report.
- **Scope**: Covers per-agent permission resolution semantics (the "How It
  Works" table), setting permissions on keys and teams via UI/API, agent access
  groups (dashboard-only tagging + group grant), and the visibility filtering on
  `GET /v1/agents`. Does not cover trace-ID enforcement (overview page Claim 7),
  agent registration (overview page Claims 1/5), or the protocol-version
  negotiation matrix (overview page Claim 4).

## Extracted Claims

### Claim 1: A2A agent permission resolution is two-level (Key, Team) with a fail-open default — when neither the key nor the team sets agent restrictions, the key can access all agents
- **Evidence**: The "How It Works" resolution table's first row: key `None`, team
  `None` → "Key can **all** agents." The page states this explicitly in the
  table's Notes column.
- **Confidence**: emerging (documented vendor behavior; no security audit or
  measured default)
- **Quote**: "Key can access **all** agents" (Notes column, first row of the
  resolution table)
- **Our assessment**: A real security-relevant default. An operator who never
  configures agent permissions has granted every key access to every agent. This
  is the "least-privilege by exception, not by default" pattern — worth calling
  out in Ch06 as a deployment checklist item: if you enable the A2A gateway,
  set agent permissions on every key/team, or the default is full access.

### Claim 2: When both a key and a team set agent permissions, the intersection applies — most restrictive wins
- **Evidence**: The resolution table's fourth row: key `["agent-1", "agent-2"]`,
  team `["agent-1", "agent-3"]` → key can access `agent-1` only, with the note
  "Intersection of both lists (most restrictive wins)."
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "Intersection of both lists (most restrictive wins)"
- **Our assessment**: Standard RBAC intersection model, sensible for least-
  privilege. Confirms the overview note's Claim 7 summary (key/team intersection
  → 403) and adds the concrete semantics: it is a set intersection, not a union
  or override. Worth citing alongside the overview Claim 7 rather than
  restating it.

### Claim 3: When a key has both a direct `agents` list and `agent_access_groups`, the union of those is computed first, then the team-level intersection is applied
- **Evidence**: The resolution table's last row shows the mixed case; the Agent
  Access Groups section states: "When a key has **both** a direct `agents` list
  and `agent_access_groups`, the union is computed (any agent reached by either
  path is allowed), and then the team-level intersection is applied as described
  below."
- **Confidence**: emerging (documented order of operations)
- **Quote**: "When a key has **both** a direct `agents` list and
  `agent_access_groups`, the union is computed (any agent reached by either
  path is allowed), and then the team-level intersection is applied"
- **Our assessment**: The order of operations matters: union (key's direct list ∪
  key's access groups) → then intersect with team's effective set. An operator
  who adds an agent to a key's direct list and also grants the group containing
  that agent gets no extra access — the union is idempotent — but if the team
  excludes the agent, the team intersection wins. This is the concrete mechanism
  underneath the overview's Claim 7 "key/team permission intersection" and is
  the first time the two-step (union then intersection) order is stated
  explicitly.

### Claim 4: Agent access groups let you tag agents with logical labels in the dashboard, then grant the group to a key or team — new agents tagged into the group automatically become reachable
- **Evidence**: The "Agent Access Groups" section: "Tag agents with logical
  labels in the dashboard, then grant the **group** to a key or team. Adding a
  new agent to the group automatically makes it available to every key/team that
  holds the group."
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "Adding a new agent to the group automatically makes it available
  to every key/team that holds the group."
- **Our assessment**: A scalability pattern for large agent catalogs — avoids
  per-agent enumeration on every key/team. But it has a governance shadow: the
  tagging step is dashboard-only (see Claim 5), so adding an agent to a group
  is a UI mutation that is not visible in config, not diffable in code review,
  and not reproducible from a declarative spec. The "automatically makes it
  available" behavior is a membership-mutation side effect that widens access
  silently.

### Claim 5: Tagging an agent with access groups is a dashboard-only operation — `POST /v1/agents` does not expose `agent_access_groups` as a top-level field; tags persist via the underlying DB column
- **Evidence**: The callout box under "Tag the agent with one or more groups":
  "Tagging an agent with access groups is currently a dashboard-only operation.
  The `POST /v1/agents` body schema does not expose `agent_access_groups` as a
  top-level field; the group tags persist via the underlying DB column and are
  consumed during permission resolution."
- **Confidence**: emerging (documented vendor limitation)
- **Quote**: "The `POST /v1/agents` body schema does not expose
  `agent_access_groups` as a top-level field; the group tags persist via the
  underlying DB column"
- **Our assessment**: The highest-value extraction on the page. This is the
  "looks governed, isn't reproducible from config" edge — agent ACL state lives
  in the DB, is only settable via the dashboard UI, and is invisible to config
  files, `config.yaml`, and any IaC / GitOps review path. Same config-vs-DB
  precedence seam as the overview's Claim 5 (config-defined agent names losing
  to same-named DB records), but here it is a field that simply does not exist
  in the API surface at all. Operationally: you cannot express your agent ACL
  policy in code, you cannot diff it in a PR, and you cannot audit it from
  config — it is shadow config in the console.

### Claim 6: `GET /v1/agents` only returns agents the key/team can access, and `POST /a2a/{agent_id}` returns HTTP 403 Forbidden if access is denied
- **Evidence**: The "Overview" section: "When permissions are configured:
  `GET /v1/agents` only returns agents the key/team can access;
  `POST /a2a/{agent_id}` (Invoking an agent) returns `403 Forbidden` if access
  is denied." The key creation + test examples demonstrate both the allowed path
  (succeeds) and the blocked path (403 response body shown).
- **Confidence**: emerging (documented vendor behavior)
- **Quote**: "`GET /v1/agents` only returns agents the key/team can access"
- **Quote**: "`POST /a2a/{agent_id}` (Invoking an agent) returns `403
  Forbidden` if access is denied"
- **Our assessment**: The visibility filtering on `GET /v1/agents` is consistent
  with the overview note's Claim 8 (search-scoped to the key's visible agents).
  The 403 on `POST /a2a/{agent_id}` confirms the overview's Claim 7 (key/team
  permission intersection → 403). Both are implementation details of the same
  authorization layer, now made concrete with response bodies and curl examples.

### Claim 7: MCP's permission hierarchy extends to End-user / Agent / Org additionally — A2A agent permissions are a narrower model today
- **Evidence**: The "How It Works" section preamble: "MCP's permission hierarchy
  extends to End-user / Agent / Org additionally; agent permissions are a
  narrower model today."
- **Confidence**: emerging (documented scope boundary)
- **Quote**: "MCP's permission hierarchy extends to End-user / Agent / Org
  additionally; agent permissions are a narrower model today."
- **Our assessment**: An explicit statement that A2A agent governance is less
  developed than MCP's. Useful for the guide's framing: the "emerging agent
  control plane" (Ch03) is not one model — the permission depth differs across
  protocols, and A2A's two-level model (Key, Team) is narrower than MCP's four-
  level model (End-user, Agent, Org, plus Key/Team). An operator choosing
  between A2A and MCP gateway surfaces should know this gap.

### Claim 8: The `agent_access_groups` field is valid on both a key's and a team's `object_permission` — groups resolve to concrete agent IDs at permission time
- **Evidence**: The Agent Access Groups section: "The same `agent_access_groups`
  field is also valid on a team's `object_permission`." The resolution table's
  fifth row shows the team-less case (groups resolve directly); the sixth row
  shows groups + team intersection.
- **Confidence**: emerging (documented field availability)
- **Quote**: "The same `agent_access_groups` field is also valid on a team's
  `object_permission`."
- **Our assessment**: Confirms the symmetry between key and team for group
  grants. The resolution semantics are: groups → concrete agent IDs → then
  intersection with team. The indirection layer (group → IDs at resolution
  time) means the effective permission set can change without any key/team
  mutation — just by re-tagging agents in the dashboard.

## Concrete Artifacts

### Key with direct agent permissions (from "Create a key with agent permissions", verbatim)

```json
{
  "object_permission": {
    "agents": ["agent-123"]
  }
}
```

### Team with agent permissions (from "Create team with agent permissions", verbatim)

```json
{
  "team_alias": "support-team",
  "object_permission": {
    "agents": ["agent-123"]
  }
}
```

### Key with access group grants (from "Key with access to two agent groups", verbatim)

```json
{
  "object_permission": {
    "agent_access_groups": ["clinical-tools", "research-tools"]
  }
}
```

### 403 Forbidden response (from the blocked-agent test example, verbatim)

```json
{
  "error": {
    "message": "Access denied to agent: agent-456",
    "code": 403
  }
}
```

### Permission resolution table (from "How It Works", verbatim)

```
Key Permissions                         | Team Permissions        | Result                                        | Notes
----------------------------------------|-------------------------|-----------------------------------------------|--------------------------------------
None                                    | None                    | Key can access ALL agents                     | Open access by default
["agent-1", "agent-2"]                  | None                    | Key can access agent-1 and agent-2            | Key uses its own permissions
None                                    | ["agent-1", "agent-3"]  | Key can access agent-1 and agent-3            | Key inherits team's permissions
["agent-1", "agent-2"]                  | ["agent-1", "agent-3"]  | Key can access agent-1 only                   | Intersection of both lists (most restrictive wins)
agent_access_groups: ["clinical"]       | None                    | Key can access every agent tagged clinical    | Access groups resolved to concrete agent IDs
agent_access_groups: ["clinical"]       | agents: ["agent-1"]     | Intersection of (every agent tagged clinical) and ["agent-1"] | Mixing direct and group grants is supported
```

## Cross-References

**Candidates from `miner-related-notes.md`** (cited or dismissed; every listed
path is addressed):

- `source-notes/docs-litellm-a2a-agent-card.md` — **dismissed**: agent-card
  serving (field matrix, signatures dropped, per-skill security scoping) and
  skill-selection forwarding; no permission resolution or access-group content.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP /
  coding-agent integration topic; unrelated to agent-gateway governance.
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  agent spectrum, read/write guards, pre-on-caller, golden-label eval for SRE
  agents; no agent-gateway / A2A / permission content.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors and debuggability; not agent permission resolution.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**: Helicone
  telemetry integration, session correlation headers; no per-agent authorization
  or access-group content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization; unrelated to agent proxy surfaces.
- `source-notes/docs-langfuse-security-and-guardrails.md` — **dismissed**:
  model/LLM guardrail scanner stacks; no per-agent authorization or proxy
  surfaces.
- `source-notes/blog-litellm-save-claude-code-costs.md` — **dismissed**: budget
  windows, caching, MCP Tool Search on the model path; unrelated to agent
  permission resolution.
- `source-notes/blog-litellm-valkey-semantic-caching.md` — **dismissed**:
  embedding-based response-cache backends; unrelated to agent permissions.
- `source-notes/docs-promptfoo-classifier-grading.md` — **dismissed**:
  classifier-based output grading; unrelated to agent-gateway surfaces.

**Primary cross-references:**

- **Extends**:
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 7** (overview note:
    "After the virtual key is authenticated, LiteLLM checks whether the calling
    key (and its team) is allowed to invoke the requested agent. If not, the
    response is HTTP 403"). This page provides the resolution *rules* underneath
    that summary: the full matrix (key-only, team-only-inherits, intersection,
    groups, mixed), the fail-open default, and the union-then-intersection order
    of operations. Do not re-extract the 403 fact — cite the overview Claim 7
    and add the resolution semantics as the delta.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 5** (overview note:
    config-defined agents vs DB agents with name-collision and version-cutoff
    semantics). The access-group dashboard-only constraint (this note Claim 5) is
    the same config-vs-DB precedence seam applied to a different field —
    agent ACL tags exist only in the DB and are invisible to config.yaml, just
    as agent names lose collisions to DB records.
  - `source-notes/docs-litellm-a2a-agent-gateway.md` **Claim 8** (overview note:
    `GET /v1/agents?query=` semantic search scoped to the key's visible agents).
    This page's `GET /v1/agents` visibility filtering (Claim 6) is the same
    constraint stated without the search dimension — both confirm that the agent
    list returned to the caller is bounded by the permission layer.
- **Novel**: First source note in the corpus to cover A2A agent permission
  *resolution semantics*: the fail-open default (unconfigured = full access),
  the union-then-intersection order of operations, the `agent_access_groups`
  field (tag-based ACLs with group-to-ID resolution at permission time), the
  dashboard-only tagging constraint (no API field, DB-column persistence), and
  the explicit scope boundary vs MCP's deeper permission hierarchy.

## Guide Impact

- **Chapter 06 (Security and Trust)** — §"Function-calling authorization":
  Add the fail-open default (Claim 1) as a deployment checklist item: when
  enabling the A2A gateway, set agent permissions on every key/team or the
  default grants full access. Add the resolution table (Claims 2-3) as the
  concrete authorization model, and the dashboard-only access-group constraint
  (Claim 5) as a "governed but not reproducible from config" caveat — agent
  ACLs cannot be expressed in IaC, so they fall outside GitOps review and
  are shadow config in the console. The access-group membership-mutation side
  effect (Claim 4) should be noted: adding a tag to an agent silently widens
  who can reach it.

- **Chapter 03 (Runbooks and Agents)** — §"The emerging agent control plane":
  Add the MCP-vs-A2A scope boundary (Claim 7) to the governance framing:
  A2A's two-level permission model (Key, Team) is narrower than MCP's four-
  level model (End-user, Agent, Org), so the "agent control plane" is not
  one model — permission depth differs across protocols.

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/a2a_agent_permissions`, HTTP 200, no paywall).
  The page is thin (~70 lines of substantive content) — a topic page focused
  on the permission resolution mechanism. All `Quote` fields are character-for-
  character from the fetched page.
- Cross-reference candidates from `miner-related-notes.md` were all reviewed.
  The only relevant overlap is `docs-litellm-a2a-agent-gateway.md` (the
  overview note from #1302); all other candidates are unrelated to agent
  permission resolution and were dismissed. The overview note's Claims 5, 7,
  and 8 were verified by re-reading the cited source note before writing
  cross-references (MINER §4b).
- Confidence is `emerging`: the page documents vendor *capability* with field
  names, resolution rules, and curl examples, but demonstrates no measured
  behavior, no failure modes, and no production experience. The page is thin
  by design (focused topic page); the value is concentrated in the fail-open
  default, the resolution semantics, and the dashboard-only constraint.
- No contradiction issue filed. This page's claims are consistent with the
  overview note's Claims 5, 7, and 8 — it extends them with resolution rules,
  not opposes them. `CONTRADICTIONS.md` and open `contradiction`-labeled
  issues were checked; no existing contradiction covers A2A agent permissions.
- `date_published` is unknown (living Docusaurus docs page); `date_extracted`
  and `last_checked` are both 2026-09-15.
